"""营养引擎 —— 蛋白 / 钠双锚点评分与配餐生成。

核心指标（见 docs/adr/0001）：
    钠效率 = 钠(mg) ÷ 蛋白质(g)     越低越优
    蛋白密度 = 蛋白质(g) ÷ 热量 × 100  越高越优

本模块只做「算」和「排」，不负责渲染与 I/O，便于测试。

⚠️ 免责：本模块输出仅供参考，不构成医疗或营养建议。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = [
    "Item",
    "Profile",
    "sodium_efficiency",
    "protein_density",
    "classify",
    "rank",
    "build_plan",
    "PROTEIN_G_LOW",
    "PROTEIN_G_HIGH",
    "SODIUM_REFERENCE_DAILY",
    "SODIUM_REFERENCE_MEAL",
]

# --- 口径常量 -------------------------------------------------------------

#: 蛋白目标区间（每公斤体重）。增肌期通行区间，见 CONTEXT.md
PROTEIN_G_LOW = 1.6
PROTEIN_G_HIGH = 2.2

#: 每日钠参考上限（WHO 推荐上限）
SODIUM_REFERENCE_DAILY = 2000
#: 单餐钠参考线
SODIUM_REFERENCE_MEAL = 700

#: 参与钠效率排序的蛋白下限（g）。低于此值时钠效率分母趋近 0，指标失去意义。
PROTEIN_FLOOR_FOR_RANKING = 5

#: 主食候选的热量上限（kcal）。
#: 增肌场景需要热量，但对单餐而言 700 kcal 以上会挤占后续正餐的额度。
#: 注意：安格斯厚牛堡等高蛋白单品虽在钠效率榜上排名优秀，却因热量过高被排除，
#: 否则会得出"单餐吃 987 kcal"的荒谬结论。
MAIN_MAX_KCAL = 700

#: 主食候选的蛋白下限（g），对应 _POST_WORKOUT_MIN_PROTEIN。
MAIN_MIN_PROTEIN = 14

#: 饮品 / 佐餐关键字。用于把饮品从主食榜单中分离，避免"冰牛奶大杯"
#: 与"猪柳麦满分"这类主食在同维度混排。
_BEVERAGE_KEYWORDS = (
    "可乐", "雪碧", "红茶", "绿茶", "咖啡", "牛奶", "豆浆", "果汁", "纯悦",
    "新地", "麦旋风", "派", "冰淇淋", "拉明顿", "雪冰", "奶铁", "奶绿",
    "玛奇朵", "阿芙佳朵", "怡泉", "鲜橙", "奶昔", "美式", "拿铁",
    "卡布奇诺", "摩卡", "浓缩", "鲜萃",
)

#: 训练后 / 加餐场景候选（低卡高蛋白）
_POST_WORKOUT_MAX_KCAL = 350
_POST_WORKOUT_MIN_PROTEIN = 14


@dataclass(frozen=True)
class Item:
    """一个餐品的营养条目（不可变）。"""

    name: str
    kcal: int
    protein: int
    fat: int
    carbohydrate: int
    sodium: int
    calcium: int = 0

    @classmethod
    def from_record(cls, rec: dict[str, Any]) -> "Item":
        return cls(
            name=str(rec.get("productName", "")).strip(),
            kcal=int(rec.get("energyKcal") or 0),
            protein=int(rec.get("protein") or 0),
            fat=int(rec.get("fat") or 0),
            carbohydrate=int(rec.get("carbohydrate") or 0),
            sodium=int(rec.get("sodium") or 0),
            calcium=int(rec.get("calcium") or 0),
        )

    @property
    def is_beverage(self) -> bool:
        return any(k in self.name for k in _BEVERAGE_KEYWORDS)

    def sodium_efficiency(self) -> float | None:
        """每克蛋白对应的钠毫克数。低者优。无有效值时返回 None。"""
        if self.protein <= 0:
            return None
        return self.sodium / self.protein

    def protein_density(self) -> float:
        """每 100 千卡的蛋白质克数。高者优。"""
        if self.kcal <= 0:
            return 0.0
        return self.protein / self.kcal * 100


@dataclass
class Profile:
    """用户画像。体重与训练类型均为可选输入。"""

    body_weight: float | None = None
    training_day: bool = True

    def protein_target(self) -> tuple[int, int] | None:
        """返回每日蛋白目标区间（克）。未提供体重时返回 None。"""
        if not self.body_weight or self.body_weight <= 0:
            return None
        return (
            round(self.body_weight * PROTEIN_G_LOW),
            round(self.body_weight * PROTEIN_G_HIGH),
        )

    def per_meal_target(self) -> int | None:
        """按三餐均分给出单餐蛋白参考值（克）。"""
        target = self.protein_target()
        if not target:
            return None
        low, high = target
        return round((low + high) / 2 / 3)


# --- 指标 -----------------------------------------------------------------


def sodium_efficiency(item: Item) -> float | None:
    """钠效率：钠(mg) / 蛋白质(g)。越低越优。"""
    return item.sodium_efficiency()


def protein_density(item: Item) -> float:
    """蛋白密度：蛋白质(g) / 热量(kcal) × 100。越高越优。"""
    return item.protein_density()


def classify(item: Item) -> str:
    """将餐品归入语义分组。"""
    if item.is_beverage:
        return "饮品"
    if item.kcal <= _POST_WORKOUT_MAX_KCAL and item.protein >= _POST_WORKOUT_MIN_PROTEIN:
        return "加餐"
    return "主食"


def _eligible(item: Item) -> bool:
    """是否参与钠效率排序：需有足够蛋白作为分母。"""
    return item.protein >= PROTEIN_FLOOR_FOR_RANKING


# --- 排序 -----------------------------------------------------------------


def rank(
    items: list[Item],
    limit: int | None = None,
    group: str | None = None,
) -> list[Item]:
    """按钠效率升序排列。数值相同者按蛋白密度降序。

    Args:
        items: 候选餐品。
        limit: 返回数量上限，None 表示全部。
        group: 仅返回该分组（"主食" / "饮品" / "加餐"），None 表示全部。

    Returns:
        排序后的 Item 列表（不含蛋白不足的条目）。
    """
    pool = [i for i in items if _eligible(i)]
    if group:
        pool = [i for i in pool if classify(i) == group]
    pool.sort(key=lambda i: (i.sodium_efficiency() or 1e9, -i.protein_density()))
    return pool[:limit] if limit else pool


def find_counterpart(items: list[Item], target: Item) -> Item | None:
    """找一个蛋白含量接近、但钠效率明显更优的对照单品。

    用途：生成"同样吃 X 克蛋白，钠能省 Y 倍"这类可传播论断。

    由于 build_plan 已选出「主食候选池」中钠效率最优的单品，主食往往
    已无更优对照。此时本函数会放宽为**全表**搜索（含饮品），
    因为高蛋白主食搭配低钠饮品才是本项目倡导的真实用法。

    Args:
        items: 全量候选。
        target: 参照单品（通常是用户原本会点的、钠效率偏高的）。

    Returns:
        找到的对照单品；无合适对照时返回 None。
    """
    base = target.sodium_efficiency()
    if base is None or base <= 0:
        return None

    for cand in rank(items):
        if cand.name == target.name:
            continue
        # 蛋白差距控制在 ±4g 内，才算"同等蛋白"
        if abs(cand.protein - target.protein) > 4:
            continue
        ce = cand.sodium_efficiency() or 1e9
        # 要求钠效率至少好 1.5 倍，避免"优化"幅度微乎其微
        if base / ce >= 1.5:
            return cand
    return None


def find_sodium_anchor(items: list[Item]) -> Item | None:
    """找出「低钠蛋白锚点」单品。

    这是本项目最具传播力的发现：某些饮品（尤其冰牛奶系列）能以
    极低的钠提供可观蛋白质，与普通主食搭配可大幅拉低整单的钠效率。

    筛选条件：蛋白 ≥ 8g、钠效率 ≤ 15 mg/g，且热量不高于 350 kcal。
    """
    anchors = [
        i
        for i in rank(items)
        if i.protein >= 8
        and (i.sodium_efficiency() or 1e9) <= 15
        and i.kcal <= 350
    ]
    # 优先选蛋白量高的锚点：同样低钠，蛋白越多越有替换价值
    anchors.sort(key=lambda i: (-i.protein, i.sodium_efficiency()))
    return anchors[0] if anchors else None


# --- 配餐生成 -------------------------------------------------------------


@dataclass
class Plan:
    """一份配餐方案。"""

    profile: Profile
    main: Item
    drink: Item | None
    day_note: str
    target_text: str
    counterpart: Item | None = None
    baseline: Item | None = None
    baseline_ratio: float = 0.0
    baseline_saved: int = 0
    totals: dict[str, int] = field(default_factory=dict)


def build_plan(items: list[Item], profile: Profile) -> Plan:
    """生成核心配餐方案。

    规则：
      1. 主食 —— 在「蛋白 ≥14g 且热量 ≤700 kcal」的候选中，取钠效率最低者
      2. 饮品 —— 蛋白 ≥5g 的饮品中，钠效率最低者（可为空）
      3. 组合对照 —— 用「高蛋白主食 + 低钠蛋白锚点」的组合，对比
         「同等蛋白量的常见高钠单品」，量化可省的钠

    热量上限是必要约束：高蛋白厚牛堡类单品钠效率虽好，但单份接近 1000 kcal，
    作为单餐推荐并不合理。
    """
    candidates = [
        i
        for i in rank(items)
        if not i.is_beverage
        and i.protein >= MAIN_MIN_PROTEIN
        and i.kcal <= MAIN_MAX_KCAL
    ]
    if not candidates:
        # 放宽蛋白下限，但仍守住热量上限
        candidates = [i for i in rank(items) if not i.is_beverage and i.kcal <= MAIN_MAX_KCAL]
    if not candidates:
        candidates = rank(items)
    if not candidates:
        raise ValueError("营养数据中无可用条目（全部蛋白含量低于 5g）")

    main = candidates[0]

    drinks = rank(items, group="饮品")
    drink = drinks[0] if drinks else None

    counterpart = find_counterpart(items, main)

    # ---- 组合对照：同等蛋白下的钠对比 ----
    # 组合 = 主食 + 低钠蛋白锚点；基线 = 与组合蛋白量最接近的高钠单品
    anchor = find_sodium_anchor(items)
    baseline: Item | None = None
    baseline_ratio = 0.0
    baseline_saved = 0

    if anchor:
        combo_protein = main.protein + anchor.protein
        combo_sodium = main.sodium + anchor.sodium
        combo_eff = combo_sodium / combo_protein if combo_protein else 0

        # 在「非饮品」中找一个蛋白量接近 combo 的单品作为基线
        pool = [
            i
            for i in rank(items)
            if not i.is_beverage and i.name not in {main.name, anchor.name}
        ]
        best_gap = None
        for cand in pool:
            gap = abs(cand.protein - combo_protein)
            if best_gap is None or gap < best_gap:
                best_gap = gap
                baseline = cand
        # 蛋白差距超过 8g 时对比就不成立了
        if baseline and best_gap is not None and best_gap <= 8:
            b_eff = baseline.sodium_efficiency() or 0
            if b_eff > 0 and combo_eff > 0:
                baseline_ratio = b_eff / combo_eff
                baseline_saved = baseline.sodium - combo_sodium

    kcal = main.kcal + (drink.kcal if drink else 0)
    protein = main.protein + (drink.protein if drink else 0)
    fat = main.fat + (drink.fat if drink else 0)
    carb = main.carbohydrate + (drink.carbohydrate if drink else 0)
    sodium = main.sodium + (drink.sodium if drink else 0)

    per_meal = profile.per_meal_target()
    day_word = "训练日" if profile.training_day else "休息日"
    if per_meal and protein >= per_meal:
        target_text = f"本单合计 {protein} g 蛋白，已达单餐参考值 {per_meal} g"
    elif profile.body_weight:
        lo, hi = profile.protein_target() or (0, 0)
        target_text = (
            f"本单 {protein} g 蛋白；你的每日区间为 {lo}~{hi} g，{day_word}建议分三餐补足"
        )
    else:
        target_text = f"本单合计 {protein} g 蛋白"

    day_note = (
        "训练日：碳水需求较高，可另加薯条等主食补足能量"
        if profile.training_day
        else "休息日：碳水需求下调，建议以蛋白与蔬菜为主，减少主食"
    )

    return Plan(
        profile=profile,
        main=main,
        drink=drink,
        day_note=day_note,
        target_text=target_text,
        counterpart=counterpart,
        baseline=baseline,
        baseline_ratio=baseline_ratio,
        baseline_saved=baseline_saved,
        totals={"kcal": kcal, "protein": protein, "fat": fat, "carb": carb, "sodium": sodium},
    )
