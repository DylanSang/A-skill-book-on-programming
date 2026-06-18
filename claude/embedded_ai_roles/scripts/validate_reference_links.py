#!/usr/bin/env python3
"""Validate that key .claude markdown files reference existing local assets."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CHECK_FILES = [
    Path(".claude/embedded-feature-planner/AGENTS.md"),
    Path(".claude/embedded_ai_roles/references/role-routing-and-selection.md"),
    Path(".claude/embedded_ai_roles/references/task-playbooks.md"),
]

PATH_PATTERN = re.compile(r"`(\.claude/[^`]+)`")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.parse_args()

    errors: list[str] = []

    for check_file in CHECK_FILES:
        text = check_file.read_text(encoding="utf-8")
        for match in PATH_PATTERN.findall(text):
            target = Path(match)
            if not target.exists():
                errors.append(f"{check_file.name}: missing referenced path {match}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Reference link validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
