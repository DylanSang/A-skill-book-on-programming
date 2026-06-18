#!/usr/bin/env python3
"""Assemble multi-role findings into a single markdown summary."""

from __future__ import annotations

import argparse
from pathlib import Path


SECTION_TITLES = (
    "## 目标",
    "## 已确认事实",
    "## 分析与判断",
    "## 风险与待确认",
    "## 建议动作 / 交付物",
)


def collect_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {title: [] for title in SECTION_TITLES}
    current: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if line in SECTION_TITLES:
            current = line
            continue
        if current and line:
            sections[current].append(line)

    return sections


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", help="Role markdown files to assemble")
    parser.add_argument("--output", required=True, help="Output markdown path")
    args = parser.parse_args()

    merged: dict[str, list[str]] = {title: [] for title in SECTION_TITLES}
    sources: list[str] = []

    for input_path in args.inputs:
        path = Path(input_path)
        text = path.read_text(encoding="utf-8")
        sources.append(path.name)
        sections = collect_sections(text)
        for title in SECTION_TITLES:
            for line in sections[title]:
                entry = f"- [{path.stem}] {line}"
                if entry not in merged[title]:
                    merged[title].append(entry)

    lines: list[str] = [
        "# 角色输出汇总",
        "",
        "## 来源",
        *[f"- {name}" for name in sources],
        "",
    ]

    for title in SECTION_TITLES:
        lines.append(title)
        if merged[title]:
            lines.extend(merged[title])
        else:
            lines.append("- 无")
        lines.append("")

    Path(args.output).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote assembled role output to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

