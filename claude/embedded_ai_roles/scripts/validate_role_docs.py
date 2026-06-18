#!/usr/bin/env python3
"""Validate embedded AI role docs for richer structure and anti-drift rules."""

from __future__ import annotations

import argparse
from pathlib import Path


ROLE_DIR = Path(".claude/embedded_ai_roles/embedded_ai_roles")
ROLE_FILES = sorted(ROLE_DIR.glob("*.md"))

REQUIRED_HEADINGS = (
    "# Role:",
    "## 职责",
    "## 输入",
    "## 输出",
    "## 协作关系",
)

REQUIRED_ROLE_SIGNALS = (
    "## 证据清单",
    "## 何时升级",
    "## 交付关注点",
    "## 常见失误",
)

DISCOURAGED_LITERALS = (
    "Linux 5.10",
    "localhost:1883",
    "arm-linux-gnueabihf-gcc 9.4",
    "arm-none-eabi-gcc 10.3",
)


def validate_role_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"{path.name}: missing heading {heading}")

    for signal in REQUIRED_ROLE_SIGNALS:
        if signal not in text:
            errors.append(f"{path.name}: missing role completeness section {signal}")

    for literal in DISCOURAGED_LITERALS:
        if literal in text:
            errors.append(f"{path.name}: contains project-like hardcoded literal `{literal}`")

    if "## 已确认事实" not in text:
        errors.append(f"{path.name}: missing section ## 已确认事实")
    if "## 风险与待确认" not in text:
        errors.append(f"{path.name}: missing section ## 风险与待确认")
    if "## 建议动作 / 交付物" not in text:
        errors.append(f"{path.name}: missing section ## 建议动作 / 交付物")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.parse_args()

    errors: list[str] = []
    for role_file in ROLE_FILES:
        errors.extend(validate_role_file(role_file))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Role docs validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
