#!/usr/bin/env python3
"""Validate embedded AI role rule docs for drift, metadata, and usefulness."""

from __future__ import annotations

import argparse
from pathlib import Path


RULE_DIR = Path(".claude/embedded_ai_roles/rules")
RULE_FILES = sorted(RULE_DIR.glob("*.mdc"))

REQUIRED_FRONTMATTER_KEYS = ("description:", "alwaysApply:")
REQUIRED_RULE_SIGNALS = (
    "## ",
)
DISCOURAGED_LITERALS = (
    "Linux 5.10",
    "localhost:1883",
    "arm-linux-gnueabihf-gcc 9.4",
    "arm-none-eabi-gcc 10.3",
    "git commit -m",
    "adb push build/qe_<module> /userdata/app/",
)


def validate_rule(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if not text.startswith("---"):
        errors.append(f"{path.name}: missing frontmatter start")

    for key in REQUIRED_FRONTMATTER_KEYS:
        if key not in text:
            errors.append(f"{path.name}: missing frontmatter key {key}")

    if not any(signal in text for signal in REQUIRED_RULE_SIGNALS):
        errors.append(f"{path.name}: missing structured sections")

    for literal in DISCOURAGED_LITERALS:
        if literal in text:
            errors.append(f"{path.name}: contains discouraged literal `{literal}`")

    if "当前工程" not in text and "当前仓库" not in text:
        errors.append(f"{path.name}: should mention current-project/current-repo verification mindset")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.parse_args()

    errors: list[str] = []
    for rule_file in RULE_FILES:
        errors.extend(validate_rule(rule_file))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Rule docs validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
