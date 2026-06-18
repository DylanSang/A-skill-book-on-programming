#!/usr/bin/env python3
"""Resolve explicit model routing for a skill and task."""

from __future__ import annotations

import argparse
import json

from task_routing_core import detect_mode, detect_scenario
from model_routing_core import resolve_model_routing


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument(
        "--skill",
        default="embedded-feature-planner",
        choices=("embedded-feature-planner", "expert-prompt-generator"),
        help="Skill name to resolve routing for",
    )
    parser.add_argument("--mode", help="Optional precomputed mode")
    parser.add_argument("--scenario", help="Optional precomputed scenario")
    parser.add_argument("--enable-model-routing", action="store_true", help="Explicitly enable model routing")
    parser.add_argument("--routing-config", help="JSON config path for explicit model routing")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    args = parser.parse_args()

    mode = args.mode or detect_mode(args.task)
    scenario = args.scenario or detect_scenario(args.task, mode=mode)
    routing = resolve_model_routing(
        task=args.task,
        mode=mode,
        scenario=scenario,
        skill=args.skill,
        enable_model_routing=args.enable_model_routing,
        routing_config_path=args.routing_config,
    )

    if args.json:
        print(json.dumps(routing, ensure_ascii=False, indent=2))
        return 0

    print("# Model Routing")
    print(f"- enabled: {routing['enabled']}")
    print(f"- activation: {routing['activation']}")
    print(f"- source: {routing['source']}")
    if routing["inactive_reason"]:
        print(f"- inactive_reason: {routing['inactive_reason']}")
    print("- effective_functions:")
    for item in routing["effective_functions"]:
        print(f"  - {item['function']}: {item['model_id']}")
    if routing["warnings"]:
        print("- warnings:")
        for warning in routing["warnings"]:
            print(f"  - {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
