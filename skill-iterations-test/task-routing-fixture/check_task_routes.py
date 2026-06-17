#!/usr/bin/env python3
"""Validate task routing fixtures against route_task.py."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


FIXTURE_PATH = Path("skill-iterations-test/task-routing-fixture/expected-routes.json")


def build_utf8_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def main() -> int:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    for name, expected in fixture.items():
        result = subprocess.run(
            [sys.executable, ".claude/embedded_ai_roles/scripts/route_task.py", "--task", expected["task"], "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=build_utf8_env(),
            check=True,
        )
        actual = json.loads(result.stdout)
        for key in ("mode", "scenario"):
            if actual[key] != expected[key]:
                errors.append(
                    f"{name}: expected {key}={expected[key]!r}, got {actual[key]!r}"
                )
        if "playbook_section" not in actual:
            errors.append(f"{name}: route output missing playbook_section")
        if "routing_signals" not in actual:
            errors.append(f"{name}: route output missing routing_signals")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Task routing fixture passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
