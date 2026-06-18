#!/usr/bin/env python3
"""Validate generated task packets against fixture expectations."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


FIXTURE_PATH = Path("skill-iterations-test/task-packet-fixture/expected-task-packets.json")


def build_utf8_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def main() -> int:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    for name, expected in fixture.items():
        result = subprocess.run(
            [sys.executable, ".claude/embedded_ai_roles/scripts/generate_task_packet.py", "--task", expected["task"], "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=build_utf8_env(),
            check=True,
        )
        packet = json.loads(result.stdout)

        if packet["mode"] != expected["mode"]:
            errors.append(f"{name}: expected mode={expected['mode']!r}, got {packet['mode']!r}")
        if packet["scenario"] != expected["scenario"]:
            errors.append(f"{name}: expected scenario={expected['scenario']!r}, got {packet['scenario']!r}")
        if packet["model_routing"]["enabled"] != expected["model_routing_enabled"]:
            errors.append(
                f"{name}: expected model_routing.enabled={expected['model_routing_enabled']!r}, "
                f"got {packet['model_routing']['enabled']!r}"
            )

        role_ids = [role["id"] for role in packet["roles"]]
        for required_role in expected["required_roles"]:
            if required_role not in role_ids:
                errors.append(f"{name}: missing required role {required_role!r}")

        validation = subprocess.run(
            [sys.executable, ".claude/embedded_ai_roles/scripts/validate_task_packet.py", "--task", expected["task"]],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=build_utf8_env(),
            check=False,
        )
        if validation.returncode != 0:
            errors.append(f"{name}: validate_task_packet.py failed with output: {validation.stdout}{validation.stderr}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Task packet fixture passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
