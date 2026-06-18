#!/usr/bin/env python3
"""Select the minimal suggested role set for an embedded task description."""

from __future__ import annotations

import argparse
from task_routing_core import ROLE_LABELS, detect_mode, detect_scenario, select_roles


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Task description")
    args = parser.parse_args()

    mode = detect_mode(args.task)
    scenario = detect_scenario(args.task, mode=mode)
    roles = select_roles(args.task, scenario=scenario, mode=mode)

    print("# Suggested Roles")
    print(f"- mode: {mode}")
    print(f"- scenario: {scenario}")
    for role in roles:
        print(f"- {role}: {ROLE_LABELS[role]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
