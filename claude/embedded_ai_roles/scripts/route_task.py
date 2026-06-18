#!/usr/bin/env python3
"""Route an embedded task into planner mode, scenario, roles, and playbook."""

from __future__ import annotations

import argparse
import json

from task_routing_core import (
    SCENARIO_PLAYBOOK_SECTION,
    detect_mode,
    detect_scenario,
    get_mode_signals,
    get_scenario_signals,
    select_roles,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    args = parser.parse_args()

    mode = detect_mode(args.task)
    scenario = detect_scenario(args.task, mode=mode)
    roles = select_roles(args.task, scenario=scenario, mode=mode)
    playbook = ".claude/embedded_ai_roles/references/task-playbooks.md"

    packet = {
        "mode": mode,
        "scenario": scenario,
        "playbook": playbook,
        "playbook_section": SCENARIO_PLAYBOOK_SECTION[scenario],
        "roles": roles,
        "routing_signals": {
            "mode": get_mode_signals(args.task),
            "scenario": get_scenario_signals(args.task, mode=mode),
        },
    }

    if args.json:
        print(json.dumps(packet, ensure_ascii=False, indent=2))
        return 0

    print("# Task Route")
    print(f"- mode: {mode}")
    print(f"- scenario: {scenario}")
    print(f"- playbook: {playbook}")
    print(f"- playbook_section: {SCENARIO_PLAYBOOK_SECTION[scenario]}")
    print("- roles:")
    for role in roles:
        print(f"  - {role}")
    print("- routing_signals:")
    print(f"  - mode: {packet['routing_signals']['mode']}")
    print(f"  - scenario: {packet['routing_signals']['scenario']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
