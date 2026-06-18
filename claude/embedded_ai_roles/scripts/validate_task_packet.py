#!/usr/bin/env python3
"""Validate generated task packets for completeness and local-path integrity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from generate_task_packet import (
    DEBUG_REQUIRED_KEYS,
    HANDOFF_FIELDS,
    PACKET_SCHEMA_VERSION,
    PLAN_HEADINGS,
    TODO_HEADINGS,
    build_task_packet,
)


REQUIRED_PACKET_KEYS = (
    "schema_version",
    "task",
    "mode",
    "scenario",
    "model_routing",
    "playbook",
    "playbook_section",
    "roles",
    "artifacts",
    "artifact_templates",
    "initial_checks",
    "evidence_targets",
    "acceptance_checks",
    "handoff_fields",
    "routing_signals",
    "notes",
)


def validate_packet(packet: dict[str, object]) -> list[str]:
    errors: list[str] = []

    for key in REQUIRED_PACKET_KEYS:
        if key not in packet:
            errors.append(f"task-packet missing key: {key}")

    if packet.get("schema_version") != PACKET_SCHEMA_VERSION:
        errors.append(
            f"task-packet schema_version must be {PACKET_SCHEMA_VERSION}, got {packet.get('schema_version')!r}"
        )

    if packet.get("mode") not in {"planning", "implementation", "debug"}:
        errors.append(f"task-packet mode is invalid: {packet.get('mode')!r}")

    model_routing = packet.get("model_routing")
    if not isinstance(model_routing, dict):
        errors.append("task-packet model_routing must be an object")
    else:
        if model_routing.get("activation") != "explicit_opt_in_required":
            errors.append("task-packet model_routing.activation must be explicit_opt_in_required")
        if not isinstance(model_routing.get("enabled"), bool):
            errors.append("task-packet model_routing.enabled must be a boolean")
        if "effective_functions" not in model_routing or not isinstance(
            model_routing.get("effective_functions"), list
        ):
            errors.append("task-packet model_routing.effective_functions must be a list")
        if not model_routing.get("enabled") and model_routing.get("source") != "default_off":
            if model_routing.get("source") != "invalid_config":
                errors.append("disabled model routing should come from default_off or invalid_config")
        if model_routing.get("enabled"):
            routes = model_routing.get("effective_functions", [])
            if not routes:
                errors.append("enabled model routing must provide at least one effective function route")
            else:
                for index, route in enumerate(routes, start=1):
                    if not isinstance(route, dict):
                        errors.append(f"task-packet model_routing.effective_functions[{index}] must be an object")
                        continue
                    for key in ("function", "model_id", "reason", "when_to_use", "source"):
                        if key not in route:
                            errors.append(
                                f"task-packet model_routing.effective_functions[{index}] missing key: {key}"
                            )

    playbook = packet.get("playbook")
    if isinstance(playbook, str):
        if not Path(playbook).exists():
            errors.append(f"task-packet playbook path does not exist: {playbook}")
    else:
        errors.append("task-packet playbook must be a string path")

    roles = packet.get("roles")
    if not isinstance(roles, list) or not roles:
        errors.append("task-packet roles must be a non-empty list")
    else:
        for index, role in enumerate(roles, start=1):
            if not isinstance(role, dict):
                errors.append(f"task-packet roles[{index}] must be an object")
                continue
            for key in ("id", "file", "focus"):
                if key not in role:
                    errors.append(f"task-packet roles[{index}] missing key: {key}")
            role_file = role.get("file")
            if isinstance(role_file, str) and not Path(role_file).exists():
                errors.append(f"task-packet roles[{index}] file does not exist: {role_file}")

    artifacts = packet.get("artifacts")
    if not isinstance(artifacts, dict):
        errors.append("task-packet artifacts must be an object")
    else:
        for key in ("task_packet", "topStruct", "plan", "todo", "debug"):
            if key not in artifacts:
                errors.append(f"task-packet artifacts missing key: {key}")

    templates = packet.get("artifact_templates")
    if not isinstance(templates, dict):
        errors.append("task-packet artifact_templates must be an object")
    else:
        if templates.get("plan_headings") != PLAN_HEADINGS:
            errors.append("task-packet plan_headings do not match expected contract")
        if templates.get("todo_headings") != TODO_HEADINGS:
            errors.append("task-packet todo_headings do not match expected contract")
        if templates.get("debug_required_keys") != DEBUG_REQUIRED_KEYS:
            errors.append("task-packet debug_required_keys do not match expected contract")

    for key in ("initial_checks", "evidence_targets", "acceptance_checks", "notes"):
        value = packet.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f"task-packet {key} must be a non-empty list")

    if packet.get("handoff_fields") != HANDOFF_FIELDS:
        errors.append("task-packet handoff_fields do not match expected contract")

    routing_signals = packet.get("routing_signals")
    if not isinstance(routing_signals, dict):
        errors.append("task-packet routing_signals must be an object")
    else:
        if "mode" not in routing_signals or "scenario" not in routing_signals:
            errors.append("task-packet routing_signals must contain mode and scenario")

    return errors


def load_packet_from_path(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", help="Path to an existing task packet JSON file")
    parser.add_argument("--task", help="Generate an in-memory task packet from task text and validate it")
    parser.add_argument("--enable-model-routing", action="store_true", help="Enable model routing for --task")
    parser.add_argument("--routing-config", help="Routing config path for --task")
    args = parser.parse_args()

    if bool(args.packet) == bool(args.task):
        parser.error("Exactly one of --packet or --task is required.")

    packet = (
        build_task_packet(
            args.task,
            enable_model_routing=args.enable_model_routing,
            routing_config_path=args.routing_config,
        )
        if args.task
        else load_packet_from_path(Path(args.packet))
    )
    errors = validate_packet(packet)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Task packet validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
