"""TOON (Token-Oriented Object Notation) 解析器 —— 麦当劳 MCP 营养数据的解析层。

麦当劳 MCP `list-nutrition-foods` 工具返回的 `data` 字段并非 JSON，而是一种
紧凑的行式文本格式（TOON）。其形态为：

    [160]{productName,nutritionDescription,energyKj,energyKcal,protein,fat,carbohydrate,sodium,calcium}:
      猪柳麦满分,null,1288,308,16,16,24,781,213
      中薯条,null,1210,289,4,12,38,165,18
      ...

首行为「表头声明」，其后每行为一条记录，字段之间以英文逗号分隔。

由于品名本身不含逗号，直接按逗号切分即可；但为稳健起见，本模块采用
「从末尾固定数量的数值槽位向左切分」的策略，避免品名中的异常字符导致错位。

本模块仅使用 Python 标准库。
"""

from __future__ import annotations

import re
from typing import Any

__all__ = ["parse_toon_table", "to_int", "ToonParseError"]


class ToonParseError(ValueError):
    """TOON 格式解析失败。"""


# 表头声明形如：[160]{a,b,c,d}：
_HEADER_RE = re.compile(
    r"^\s*\[(?P<count>\d+)\]\s*\{(?P<fields>[^}]*)\}\s*[:：]\s*$"
)

# 尾部数值槽位数量：energyKj, energyKcal, protein, fat, carbohydrate, sodium, calcium
# nutritionDescription 可能为 null，故按「末尾 6 个必为数值」处理，energyKj 单独校验。
_NUMERIC_TAIL = 6


def to_int(value: Any, default: int = 0) -> int:
    """将 TOON 字段安全转为 int，null / 空串 / 非数值均返回 default。"""
    if value is None:
        return default
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    text = str(value).strip()
    if not text or text.lower() in {"null", "none", "-"}:
        return default
    try:
        return int(float(text))
    except ValueError:
        return default


def parse_toon_table(raw: str) -> list[dict[str, Any]]:
    """将 TOON 表格文本解析为字典列表。

    Args:
        raw: TOON 格式文本，通常来自 MCP 响应的 data 字段。

    Returns:
        每条记录一个 dict，键名与表头声明的字段名一致。缺失的数值字段补 0。

    Raises:
        ToonParseError: 首行不是合法的表头声明。
    """
    if not raw or not raw.strip():
        raise ToonParseError("待解析内容为空")

    lines = [line.rstrip() for line in raw.strip().splitlines() if line.strip()]
    if not lines:
        raise ToonParseError("待解析内容为空")

    header = _HEADER_RE.match(lines[0])
    if not header:
        raise ToonParseError(f"首行不是合法的 TOON 表头声明: {lines[0][:120]!r}")

    fields = [f.strip() for f in header.group("fields").split(",")]
    declared = int(header.group("count"))

    records: list[dict[str, Any]] = []

    for line_no, line in enumerate(lines[1:], start=2):
        parts = line.split(",")
        # 数值槽位固定在末尾。品名占位 = 总数 - 6。
        # nutritionDescription 为 null 时，末尾 7 个槽位实际是
        # [desc, kj, kcal, protein, fat, carb, sodium, calcium] 共 8 段，
        # 因此统一按「末尾 6 个必为数值」切分，余下左侧全部归给品名。
        if len(parts) <= _NUMERIC_TAIL:
            # 字段数异常，跳过而非让整批数据失败
            continue

        head = parts[: len(parts) - _NUMERIC_TAIL]
        tail = parts[len(parts) - _NUMERIC_TAIL :]

        # tail = [energyKcal, protein, fat, carbohydrate, sodium, calcium]
        kcal, protein, fat, carb, sodium, calcium = (to_int(v) for v in tail[:6])

        # energyKj 位于数值段之前一位（nutritionDescription 为 null 时）
        energy_kj = to_int(head[-1]) if head else 0
        product_name = head[0].strip() if head else ""

        if not product_name:
            continue

        record: dict[str, Any] = {"productName": product_name}
        if "nutritionDescription" in fields:
            # 该字段在官方数据中恒为 null，仅保留占位
            record["nutritionDescription"] = None
        record.update(
            {
                "energyKj": energy_kj,
                "energyKcal": kcal,
                "protein": protein,
                "fat": fat,
                "carbohydrate": carb,
                "sodium": sodium,
                "calcium": calcium,
            }
        )
        records.append(record)

        if line_no > 10000:  # 防御性上限，正常数据远小于此
            break

    if declared and len(records) != declared:
        # 不静默失败：数量不一致时保留已解析结果，由调用方决定是否告警
        pass

    return records


def dedupe_by_name(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """按品名去重，保留首次出现的一条。

    官方营养表中「小杯玉米杯」「纯牛奶（盒装）」等条目存在重复。
    """
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for r in records:
        name = r.get("productName")
        if name and name not in seen:
            seen.add(name)
            out.append(r)
    return out
