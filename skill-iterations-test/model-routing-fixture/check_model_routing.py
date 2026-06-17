#!/usr/bin/env python3
"""Validate explicit model routing behavior for default-off and opt-in flows."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


FIXTURE_PATH = Path("skill-iterations-test/model-routing-fixture/expected-routing-states.json")
CONFIG_PATH = ".claude/embedded_ai_roles/assets/model-routing-template.json"
INVALID_CONFIG_PATH = "skill-iterations-test/model-routing-fixture/invalid-model-routing-config.json"


def build_utf8_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_json(command: list[str]) -> dict[str, object]:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=build_utf8_env(),
        check=True,
    )
    return json.loads(result.stdout)


def main() -> int:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    errors: list[str] = []

    disabled = run_json(
        [
            sys.executable,
            ".claude/embedded_ai_roles/scripts/resolve_model_routing.py",
            "--skill",
            fixture["default_disabled"]["skill"],
            "--task",
            fixture["default_disabled"]["task"],
            "--json",
        ]
    )
    if disabled["enabled"] is not fixture["default_disabled"]["enabled"]:
        errors.append("default_disabled: expected routing to remain disabled")
    if disabled["source"] != fixture["default_disabled"]["source"]:
        errors.append(
            f"default_disabled: expected source={fixture['default_disabled']['source']!r}, got {disabled['source']!r}"
        )

    embedded_enabled = run_json(
        [
            sys.executable,
            ".claude/embedded_ai_roles/scripts/resolve_model_routing.py",
            "--skill",
            fixture["explicit_enabled_embedded"]["skill"],
            "--task",
            fixture["explicit_enabled_embedded"]["task"],
            "--enable-model-routing",
            "--routing-config",
            CONFIG_PATH,
            "--json",
        ]
    )
    if embedded_enabled["enabled"] is not fixture["explicit_enabled_embedded"]["enabled"]:
        errors.append("explicit_enabled_embedded: expected routing to be enabled")
    embedded_functions = [item["function"] for item in embedded_enabled["effective_functions"]]
    for function_name in fixture["explicit_enabled_embedded"]["required_functions"]:
        if function_name not in embedded_functions:
            errors.append(f"explicit_enabled_embedded: missing function route {function_name!r}")

    prompt_enabled = run_json(
        [
            sys.executable,
            ".claude/embedded_ai_roles/scripts/resolve_model_routing.py",
            "--skill",
            fixture["explicit_enabled_prompt"]["skill"],
            "--task",
            fixture["explicit_enabled_prompt"]["task"],
            "--enable-model-routing",
            "--routing-config",
            CONFIG_PATH,
            "--json",
        ]
    )
    if prompt_enabled["enabled"] is not fixture["explicit_enabled_prompt"]["enabled"]:
        errors.append("explicit_enabled_prompt: expected routing to be enabled")
    prompt_functions = [item["function"] for item in prompt_enabled["effective_functions"]]
    for function_name in fixture["explicit_enabled_prompt"]["required_functions"]:
        if function_name not in prompt_functions:
            errors.append(f"explicit_enabled_prompt: missing function route {function_name!r}")

    invalid = subprocess.run(
        [
            sys.executable,
            ".claude/embedded_ai_roles/scripts/validate_model_routing_config.py",
            "--config",
            INVALID_CONFIG_PATH,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=build_utf8_env(),
        check=False,
    )
    if invalid.returncode == 0:
        errors.append("invalid_config: expected validate_model_routing_config.py to fail")

    task_packet = run_json(
        [
            sys.executable,
            ".claude/embedded_ai_roles/scripts/generate_task_packet.py",
            "--task",
            fixture["default_disabled"]["task"],
            "--json",
        ]
    )
    if task_packet["model_routing"]["enabled"]:
        errors.append("task_packet default_disabled: expected task packet model routing to stay disabled")

    task_packet_enabled = run_json(
        [
            sys.executable,
            ".claude/embedded_ai_roles/scripts/generate_task_packet.py",
            "--task",
            fixture["explicit_enabled_embedded"]["task"],
            "--enable-model-routing",
            "--routing-config",
            CONFIG_PATH,
            "--json",
        ]
    )
    if not task_packet_enabled["model_routing"]["enabled"]:
        errors.append("task_packet explicit_enabled: expected task packet model routing to be enabled")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Model routing fixture passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
