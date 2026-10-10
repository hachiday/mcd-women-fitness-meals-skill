"""配餐卡生成 —— 输出可保存、可截图分享的单文件 HTML 与纯文本速查表。

设计约束：
  * 单文件，零外部依赖（无 CDN、无外链字体、无 JS），保证离线可开
  * 麦当劳红黄配色，但不模仿商标图形，不含官方标识
  * 底部固定免责声明（赛事合规要求）

⚠️ 免责声明不得移除。
"""

from __future__ import annotations

import html
from typing import Any

from nutrition import (
    SODIUM_REFERENCE_DAILY,
    SODIUM_REFERENCE_MEAL,
    Item,
    Plan,
    classify,
    rank,
)

__all__ = ["render_card", "render_quick_reference", "render_top_table"]

DISCLAIMER = (
    "本项目为麦当劳程序员创意开发大赛参赛作品，由参赛者独立开发，"
    "非麦当劳官方产品。项目输出仅供参考，不构成医疗、营养或其他专业建议；"
    "餐品信息、价格及供应状态以麦当劳官方渠道的实时结果为准。"
)

# 麦当劳品牌色（用于视觉呼应，不构成商标使用）
MCD_RED = "#DA291C"
MCD_YELLOW = "#FFC72C"
INK = "#2C2C2A"
MUTED = "#5F5E5A"


def _e(text: Any) -> str:
    return html.escape(str(text))


def _item_card(item: Item, role: str) -> str:
    eff = item.sodium_efficiency() or 0
    density = item.protein_density()
    return f"""      <div class="item">
        <div class="item-role">{_e(role)}</div>
        <div class="item-name">{_e(item.name)}</div>
        <div class="macros">
          <span><b>{item.kcal}</b> kcal</span>
          <span><b>{item.protein}</b> g 蛋白</span>
          <span class="hi"><b>{item.sodium}</b> mg 钠</span>
        </div>
        <div class="metrics">
          <span>钠效率 <b>{eff:.1f}</b> mg/g 蛋白</span>
          <span>蛋白密度 <b>{density:.1f}</b> g/100kcal</span>
        </div>
      </div>"""


def render_card(plan: Plan, top_items: list[Item] | None = None) -> str:
    """生成配餐卡 HTML。

    Args:
        plan: 配餐方案。
        top_items: 钠效率榜单条目，None 表示不渲染榜单区。

    Returns:
        完整 HTML 文档字符串。
    """
    t = plan.totals
    eff = (plan.main.sodium_efficiency() or 0)
    density = plan.main.protein_density()

    # ---- 组合对比论断：同等蛋白，钠差多少 ----
    counter_html = ""
    if plan.counterpart:
        c = plan.counterpart
        base_eff = eff
        c_eff = c.sodium_efficiency() or 0
        times = base_eff / c_eff if c_eff else 0
        counter_html = f"""
    <section class="counter">
      <h2>同样一份蛋白，钠可以差 {times:.1f} 倍</h2>
      <div class="cmp">
        <div class="cmp-col cmp-hi">
          <div class="cmp-tag">高钠选择</div>
          <div class="cmp-name">{_e(plan.main.name)}</div>
          <div class="cmp-num">{plan.main.protein} g 蛋白 · {plan.main.sodium} mg 钠</div>
          <div class="cmp-eff">{base_eff:.1f} mg/g</div>
        </div>
        <div class="cmp-vs">vs</div>
        <div class="cmp-col cmp-lo">
          <div class="cmp-tag">低钠替代</div>
          <div class="cmp-name">{_e(c.name)}</div>
          <div class="cmp-num">{c.protein} g 蛋白 · {c.sodium} mg 钠</div>
          <div class="cmp-eff">{c_eff:.1f} mg/g</div>
        </div>
      </div>
      <p class="cmp-note">蛋白量接近，但钠效率相差 {times:.1f} 倍。数据来自麦当劳官方营养表。</p>
    </section>"""

    # ---- 组合方案 vs 常见高钠单品 ----
    combo_html = ""
    if plan.baseline and plan.baseline_ratio >= 1.5:
        b = plan.baseline
        combo_p = plan.main.protein + (plan.drink.protein if plan.drink else 0)
        combo_na = plan.main.sodium + (plan.drink.sodium if plan.drink else 0)
        combo_eff = combo_na / combo_p if combo_p else 0
        b_eff = b.sodium_efficiency() or 0
        saved = plan.baseline_saved
        combo_html = f"""
    <section class="combo">
      <h2>同样 {b.protein} g 蛋白，本方案少摄入 {saved} mg 钠</h2>
      <div class="cmp">
        <div class="cmp-col cmp-hi">
          <div class="cmp-tag">常见高钠单品</div>
          <div class="cmp-name">{_e(b.name)}</div>
          <div class="cmp-num">{b.protein} g 蛋白 · {b.sodium} mg 钠</div>
          <div class="cmp-eff">{b_eff:.1f} mg/g</div>
        </div>
        <div class="cmp-vs">vs</div>
        <div class="cmp-col cmp-lo">
          <div class="cmp-tag">本方案组合</div>
          <div class="cmp-name">{_e(plan.main.name)}{' + ' + _e(plan.drink.name) if plan.drink else ''}</div>
          <div class="cmp-num">{combo_p} g 蛋白 · {combo_na} mg 钠</div>
          <div class="cmp-eff">{combo_eff:.1f} mg/g</div>
        </div>
      </div>
      <p class="cmp-note">蛋白量相差不超过 8 g，钠效率却相差 {plan.baseline_ratio:.1f} 倍。
        单次即可少摄入 {saved} mg 钠 —— 相当于日常食盐的 {saved / 2000 * 5:.1f} g。</p>
    </section>"""

    # ---- 榜单 ----
    top_html = ""
    if top_items:
        rows = []
        for idx, it in enumerate(top_items[:8], start=1):
            e_ = it.sodium_efficiency() or 0
            grp = classify(it)
            rows.append(
                f"""        <tr>
          <td class="rk">{idx}</td>
          <td class="nm">{_e(it.name)}</td>
          <td class="tg grp-{grp}">{_e(grp)}</td>
          <td class="num">{it.kcal}</td>
          <td class="num">{it.protein}</td>
          <td class="num">{it.sodium}</td>
          <td class="num strong">{e_:.1f}</td>
        </tr>"""
            )
        top_html = f"""
    <section class="rank-sec">
      <h2>官方菜单钠效率榜（越低越优）</h2>
      <table>
        <thead>
          <tr><th>#</th><th>餐品</th><th>类型</th><th>kcal</th><th>蛋白 g</th><th>钠 mg</th><th>mg/g</th></tr>
        </thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </section>"""

    drink_html = _item_card(plan.drink, "饮品补蛋白") if plan.drink else ""

    # ---- 首屏标题所需的派生变量 ----
    if plan.baseline and plan.baseline_ratio >= 1.5:
        headline_ratio = plan.baseline_ratio
        headline_protein = plan.baseline.protein
        headline_word = f"{headline_protein} 克"
    elif plan.counterpart:
        base_eff = eff
        c_eff = plan.counterpart.sodium_efficiency() or 0
        headline_ratio = base_eff / c_eff if c_eff else 0.0
        headline_protein = plan.main.protein
        headline_word = f"{headline_protein} 克"
    else:
        headline_ratio = 0.0
        headline_protein = plan.totals["protein"]
        headline_word = f"{headline_protein} 克蛋白"

    day_label = "训练日配餐建议" if plan.profile.training_day else "休息日配餐建议"

    # 首屏标题：明确对比口径，避免与"全表极差"混淆
    if plan.baseline and plan.baseline_ratio >= 1.5:
        headline_line1 = f"{plan.baseline.protein} 克蛋白"
        headline_line2 = f"本方案少摄入 {plan.baseline_saved} mg 钠"
    elif plan.counterpart:
        base_eff = eff
        c_eff = plan.counterpart.sodium_efficiency() or 0
        headline_line1 = f"{plan.main.protein} 克蛋白"
        headline_line2 = f"钠效率可以差 {base_eff / c_eff:.1f} 倍" if c_eff else "钠效率可以大幅优化"
    else:
        headline_line1 = f"{plan.totals['protein']} 克蛋白"
        headline_line2 = "按钠效率优选"

    headline_sub = (
        "同为"
        f"{plan.baseline.protein} g 蛋白的两份搭配，钠效率相差 {plan.baseline_ratio:.1f} 倍"
        if plan.baseline and plan.baseline_ratio >= 1.5
        else "依据钠效率 = 钠(mg) ÷ 蛋白(g) 优选"
    )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>麦练营养官 · 配餐卡</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
    background: {MCD_YELLOW}; color: {INK};
    padding: 20px; line-height: 1.6;
  }}
  .sheet {{
    max-width: 720px; margin: 0 auto; background: #fff;
    border-radius: 20px; overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,.10);
  }}
  .head {{ background: {MCD_RED}; color: #fff; padding: 26px 28px 22px; }}
  .head .eyebrow {{
    font-size: 12px; letter-spacing: .18em; opacity: .9;
    text-transform: uppercase; margin-bottom: 6px;
  }}
  .head h1 {{ font-size: 25px; font-weight: 700; line-height: 1.3; }}
  .head .sub {{ font-size: 13px; opacity: .94; margin-top: 8px; }}
  .head .sub2 {{ font-size: 12px; opacity: .80; margin-top: 4px; }}
  .badge {{
    display: inline-block; margin-top: 12px; padding: 5px 12px;
    background: {MCD_YELLOW}; color: {INK};
    border-radius: 999px; font-size: 12px; font-weight: 700;
  }}
  .body {{ padding: 24px 28px 28px; }}
  section {{ margin-bottom: 26px; }}
  h2 {{
    font-size: 15px; font-weight: 700; margin-bottom: 12px;
    padding-left: 10px; border-left: 4px solid {MCD_RED};
  }}
  .item {{
    border: 1px solid #E8E6E0; border-radius: 14px;
    padding: 16px 18px; margin-bottom: 12px; background: #FAFAF8;
  }}
  .item-role {{
    font-size: 11px; color: {MUTED}; letter-spacing: .1em;
    margin-bottom: 5px; font-weight: 700;
  }}
  .item-name {{ font-size: 18px; font-weight: 700; margin-bottom: 10px; line-height: 1.35; }}
  .macros, .metrics {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .macros span, .metrics span {{
    font-size: 12px; background: #fff; border: 1px solid #E8E6E0;
    padding: 5px 10px; border-radius: 8px; color: {MUTED};
  }}
  .macros b {{ color: {INK}; font-size: 14px; }}
  .macros .hi b {{ color: {MCD_RED}; }}
  .metrics span {{ background: transparent; border: none; padding: 2px 0; }}
  .metrics b {{ color: {MCD_RED}; }}
  .totals {{
    display: grid; grid-template-columns: repeat(5, 1fr);
    gap: 8px; margin-top: 4px;
  }}
  .tot {{
    background: #FAFAF8; border: 1px solid #E8E6E0;
    border-radius: 12px; padding: 12px 6px; text-align: center;
  }}
  .tot .v {{ font-size: 20px; font-weight: 700; display: block; line-height: 1.2; }}
  .tot .l {{ font-size: 11px; color: {MUTED}; display: block; margin-top: 3px; }}
  .tot .u {{ font-size: 10px; color: #999; }}
  .cmp {{ display: grid; grid-template-columns: 1fr auto 1fr; gap: 10px; align-items: center; }}
  .cmp-col {{ border-radius: 14px; padding: 14px; }}
  .cmp-hi {{ background: #FCEBEB; border: 1px solid #F09595; }}
  .cmp-lo {{ background: #EAF3DE; border: 1px solid #97C459; }}
  .cmp-tag {{ font-size: 11px; font-weight: 700; margin-bottom: 5px; }}
  .cmp-hi .cmp-tag {{ color: #A32D2D; }}
  .cmp-lo .cmp-tag {{ color: #3B6D11; }}
  .cmp-name {{ font-size: 15px; font-weight: 700; line-height: 1.3; margin-bottom: 6px; }}
  .cmp-num {{ font-size: 12px; color: {MUTED}; }}
  .cmp-eff {{ font-size: 22px; font-weight: 700; margin-top: 6px; }}
  .cmp-hi .cmp-eff {{ color: #A32D2D; }}
  .cmp-lo .cmp-eff {{ color: #3B6D11; }}
  .cmp-vs {{ font-size: 13px; font-weight: 700; color: {MUTED}; }}
  .cmp-note {{ font-size: 12px; color: {MUTED}; margin-top: 10px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  th, td {{ padding: 8px 6px; text-align: left; border-bottom: 1px solid #EFEDE7; }}
  th {{ font-size: 11px; color: {MUTED}; font-weight: 700; }}
  td.rk {{ width: 24px; color: {MUTED}; }}
  td.nm {{ font-weight: 600; }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  td.strong {{ color: {MCD_RED}; font-weight: 700; }}
  .grp-主食, .grp-加餐, .grp-饮品 {{
    font-size: 10px; padding: 2px 6px; border-radius: 6px;
  }}
  .grp-主食 {{ background: #FAEEDA; color: #854F0B; }}
  .grp-加餐 {{ background: #E1F5EE; color: #0F6E56; }}
  .grp-饮品 {{ background: #E6F1FB; color: #185FA5; }}
  .note {{
    font-size: 13px; background: #FAFAF8; border-left: 4px solid {MCD_YELLOW};
    padding: 12px 14px; border-radius: 0 10px 10px 0;
  }}
  .ref {{ font-size: 12px; color: {MUTED}; margin-top: 10px; }}
  footer {{
    background: #FAFAF8; border-top: 1px solid #EFEDE7;
    padding: 16px 28px 20px; font-size: 11px; color: #8A8985; line-height: 1.7;
  }}
</style>
</head>
<body>
<div class="sheet">
  <div class="head">
    <div class="eyebrow">McDonald'&#39;s China MCP · Nutrition Skill</div>
    <h1>同样吃{_e(headline_line1)}，<br>{_e(headline_line2)}</h1>
    <div class="sub">{_e(headline_sub)}</div>
    <div class="sub2">面向力量训练 / 增肌期女性的麦当劳配餐建议</div>
    <div class="badge">{day_label}</div>
  </div>

  <div class="body">
    <section>
      <h2>今日推荐</h2>
{_item_card(plan.main, "主食")}
{drink_html}
    </section>

    <section>
      <h2>本单合计</h2>
      <div class="totals">
        <div class="tot"><span class="v">{t['kcal']}</span><span class="l">kcal</span><span class="u">能量</span></div>
        <div class="tot"><span class="v">{t['protein']}</span><span class="l">g</span><span class="u">蛋白质</span></div>
        <div class="tot"><span class="v">{t['fat']}</span><span class="l">g</span><span class="u">脂肪</span></div>
        <div class="tot"><span class="v">{t['carb']}</span><span class="l">g</span><span class="u">碳水</span></div>
        <div class="tot"><span class="v">{t['sodium']}</span><span class="l">mg</span><span class="u">钠</span></div>
      </div>
      <p class="ref">参考线：每日钠 &lt; {SODIUM_REFERENCE_DAILY} mg，单餐 &lt; {SODIUM_REFERENCE_MEAL} mg</p>
    </section>

    <section>
      <h2>{_e(plan.target_text)}</h2>
      <div class="note">{_e(plan.day_note)}</div>
    </section>
{counter_html}
{combo_html}
{top_html}
  </div>

  <footer>{_e(DISCLAIMER)}</footer>
</div>
</body>
</html>"""


def render_top_table(items: list[Item], limit: int = 8) -> list[Item]:
    """取钠效率榜前 N 条（供 HTML 渲染）。"""
    return rank(items, limit=limit)


def render_quick_reference(plan: Plan, top_items: list[Item]) -> str:
    """生成纯文本速查表，复制即可粘贴到任意聊天工具。"""
    t = plan.totals
    ratio = 0.0
    counter_line = ""
    if plan.counterpart:
        base = plan.main.sodium_efficiency() or 0
        alt = plan.counterpart.sodium_efficiency() or 0
        ratio = base / alt if alt else 0
        counter_line = (
            f"\n【同样一份蛋白，钠差 {ratio:.1f} 倍】\n"
            f"  高钠：{plan.main.name}｜{plan.main.protein}g 蛋白｜{plan.main.sodium}mg 钠｜{base:.1f} mg/g\n"
            f"  低钠：{plan.counterpart.name}｜{plan.counterpart.protein}g 蛋白｜{plan.counterpart.sodium}mg 钠｜{alt:.1f} mg/g"
        )

    lines = [
        "麦练营养官 · 配餐速查表",
        "=" * 34,
        "",
        "【今日推荐】",
        f"  主食：{plan.main.name}",
        f"        {plan.main.kcal} kcal｜蛋白 {plan.main.protein}g｜钠 {plan.main.sodium}mg"
        f"｜钠效率 {plan.main.sodium_efficiency():.1f} mg/g",
    ]
    if plan.drink:
        lines += [
            f"  饮品：{plan.drink.name}",
            f"        {plan.drink.kcal} kcal｜蛋白 {plan.drink.protein}g｜钠 {plan.drink.sodium}mg"
            f"｜钠效率 {plan.drink.sodium_efficiency():.1f} mg/g",
        ]

    lines += [
        "",
        "【本单合计】",
        f"  {t['kcal']} kcal｜蛋白 {t['protein']}g｜脂肪 {t['fat']}g｜碳水 {t['carb']}g｜钠 {t['sodium']}mg",
        f"  参考线：每日钠 < {SODIUM_REFERENCE_DAILY} mg，单餐 < {SODIUM_REFERENCE_MEAL} mg",
        "",
        f"【{plan.target_text}】",
        f"【{plan.day_note}】",
    ]

    if counter_line:
        lines.append(counter_line)

    if plan.baseline and plan.baseline_ratio >= 1.5:
        b = plan.baseline
        combo_p = plan.main.protein + (plan.drink.protein if plan.drink else 0)
        combo_na = plan.main.sodium + (plan.drink.sodium if plan.drink else 0)
        combo_eff = combo_na / combo_p if combo_p else 0
        b_eff = b.sodium_efficiency() or 0
        lines += [
            "",
            f"【同样 {b.protein} g 蛋白，本方案少摄入 {plan.baseline_saved} mg 钠】",
            f"  常见高钠：{b.name}｜{b.protein}g 蛋白｜{b.sodium}mg 钠｜{b_eff:.1f} mg/g",
            f"  本方案组合：{plan.main.name}{' + ' + plan.drink.name if plan.drink else ''}"
            f"｜{combo_p}g 蛋白｜{combo_na}mg 钠｜{combo_eff:.1f} mg/g",
            f"  钠效率相差 {plan.baseline_ratio:.1f} 倍，"
            f"单次少摄入约 {plan.baseline_saved / 2000 * 5:.1f} g 食盐",
        ]

    if top_items:
        lines += ["", "【钠效率榜 · 越低越优】"]
        for idx, it in enumerate(top_items[:8], start=1):
            grp = classify(it)
            lines.append(
                f"  {idx:>2}. [{grp}] {it.name}"
                f"\n      {it.kcal}kcal｜蛋白{it.protein}g｜钠{it.sodium}mg｜钠效率 {it.sodium_efficiency():.1f} mg/g"
            )

    lines += [
        "",
        "-" * 34,
        "数据来源：麦当劳官方 MCP list-nutrition-foods（160 条官方营养表）",
        "钠效率 = 钠(mg) ÷ 蛋白(g)，越低越优",
        DISCLAIMER,
    ]
    return "\n".join(lines)
