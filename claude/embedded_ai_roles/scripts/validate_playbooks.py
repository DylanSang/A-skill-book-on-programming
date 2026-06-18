#!/usr/bin/env python3
"""Validate task playbooks for expected scenario structure."""

from __future__ import annotations

import argparse
from pathlib import Path


PLAYBOOK_PATH = Path(".claude/embedded_ai_roles/references/task-playbooks.md")
REQUIRED_SECTIONS = (
    "## 1. 新功能规划",
    "## 2. 编译失败 / 链接失败",
    "## 3. DTS / 驱动不生效",
    "## 4. 运行时异常 / 服务不稳定",
    "## 5. 发布阻塞 / 交付前收口",
)
REQUIRED_SUBSECTIONS = (
    "### 适用场景",
    "### 优先加载角色",
    "### 最小步骤",
    "### 必查证据",
    "### 常见误判",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.parse_args()

    text = PLAYBOOK_PATH.read_text(encoding="utf-8")
    errors: list[str] = []

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"Missing playbook section: {section}")

    for subsection in REQUIRED_SUBSECTIONS:
        if text.count(subsection) < 5:
            errors.append(f"Expected at least 5 occurrences of subsection: {subsection}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Playbook validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

