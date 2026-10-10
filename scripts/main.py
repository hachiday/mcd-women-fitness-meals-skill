#!/usr/bin/env python3
"""麦练营养官 · 命令行入口。

用法：
    # 需要先设置 MCD_MCP_TOKEN 环境变量
    python scripts/main.py --weight 55 --training-day
    python scripts/main.py --weight 55 --rest-day --html out/card.html --top 10
    python scripts/main.py --demo          # 无 Token 时用内置快照跑通

选项：
    --weight KG      体重（公斤）。可选；提供后蛋白目标更精确。
    --rest-day       标记为休息日（默认为训练日）
    --training-day   标记为训练日（默认）
    --html PATH      额外输出单文件 HTML 配餐卡
    --top N          钠效率榜条目数（默认 8）
    --demo           离线演示模式，使用内置营养快照
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_card import DISCLAIMER, render_card, render_quick_reference  # noqa: E402
from nutrition import Item, Plan, Profile, build_plan, classify, rank  # noqa: E402

SNAPSHOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nutrition_snapshot.json")


def load_items(use_demo: bool) -> list[Item]:
    """加载营养数据。离线模式读内置快照，否则实时调用 MCP。"""
    if use_demo:
        with open(SNAPSHOT, encoding="utf-8") as f:
            records = json.load(f)
        return [Item.from_record(r) for r in records]

    from mcd_client import MCPClient, MissingTokenError  # 延迟导入，避免离线模式报错

    try:
        client = MCPClient()
    except MissingTokenError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        print("\n提示：可加 --demo 用内置快照先看效果。", file=sys.stderr)
        raise SystemExit(1)
    return [Item.from_record(r) for r in client.list_nutrition_foods()]


def main() -> None:
    ap = argparse.ArgumentParser(
        description="麦练营养官 · 面向力量训练女性的麦当劳蛋白/钠双锚点配餐助手",
    )
    ap.add_argument("--weight", type=float, default=None, help="体重（公斤），可选")
    ap.add_argument("--training-day", action="store_true", help="训练日（默认）")
    ap.add_argument("--rest-day", action="store_true", help="休息日")
    ap.add_argument("--html", default=None, help="输出 HTML 配餐卡路径")
    ap.add_argument("--top", type=int, default=8, help="钠效率榜条目数")
    ap.add_argument("--demo", action="store_true", help="离线演示模式")
    args = ap.parse_args()

    items = load_items(args.demo)
    profile = Profile(
        body_weight=args.weight,
        training_day=not args.rest_day,
    )

    try:
        plan = build_plan(items, profile)
    except ValueError as exc:
        print(f"✗ 生成配餐失败: {exc}", file=sys.stderr)
        raise SystemExit(1)

    top_items = rank(items, limit=max(args.top, 1))

    source = "内置快照（离线演示）" if args.demo else "麦当劳官方 MCP 实时数据"
    print(f"\n麦练营养官 · 麦练配餐建议")
    print(f"数据来源：{source}｜共 {len(items)} 条营养记录\n")

    text = render_quick_reference(plan, top_items)
    print(text)

    if args.html:
        out_dir = os.path.dirname(os.path.abspath(args.html))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(render_card(plan, top_items))
        print(f"\n✓ 配餐卡已生成: {os.path.abspath(args.html)}")

    print(f"\n{'=' * 60}")
    print(f"免责：{DISCLAIMER}")


if __name__ == "__main__":
    main()
