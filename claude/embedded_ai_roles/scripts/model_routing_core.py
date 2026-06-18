#!/usr/bin/env python3
"""Shared helpers for explicit, default-off model routing."""

from __future__ import annotations

import json
from pathlib import Path


ROUTING_SCHEMA_VERSION = 1
DEFAULT_ACTIVATION = "explicit_opt_in_required"
PLACEHOLDER_PREFIX = "replace-with-"
MODEL_ROUTING_TEMPLATE_PATH = Path(".claude/embedded_ai_roles/assets/model-routing-template.json")

SKILL_FUNCTIONS = {
    "embedded-feature-planner": {
        "planning": ["task_routing", "planning", "role_synthesis", "artifact_review"],
        "implementation": ["task_routing", "implementation", "role_synthesis", "artifact_review"],
        "debug": ["task_routing", "debug", "role_synthesis", "artifact_review"],
    },
    "expert-prompt-generator": {
        "planning": ["task_routing", "prompt_generation", "artifact_review"],
        "implementation": ["task_routing", "prompt_generation", "artifact_review"],
        "debug": ["task_routing", "prompt_generation", "artifact_review"],
    },
}

FUNCTION_DESCRIPTIONS = {
    "task_routing": "快速任务分类、关键信号提取和最少必要角色建议。",
    "planning": "方案设计、任务拆解、架构取舍和长链分析。",
    "implementation": "代码实现、工程接入、重构与落地修改。",
    "debug": "根因定位、跨层问题分析、修复路径和验证闭环。",
    "role_synthesis": "多角色结论汇总、冲突收敛和交接压缩。",
    "artifact_review": "方案、Todo、debug 记录和交付物的结构审阅与风险检查。",
    "prompt_generation": "高质量 prompt、角色提示词和约束压缩生成。",
}


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_route_entry(entry: object, label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(entry, dict):
        return [f"{label} must be an object"]

    for key in ("model_id", "reason", "when_to_use"):
        value = entry.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}.{key} must be a non-empty string")

    return errors


def validate_routing_config(config: dict[str, object]) -> list[str]:
    errors: list[str] = []

    if config.get("schema_version") != ROUTING_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {ROUTING_SCHEMA_VERSION}, got {config.get('schema_version')!r}"
        )

    if config.get("default_enabled") is not False:
        errors.append("default_enabled must be false to keep model routing default-off")

    if config.get("activation") != DEFAULT_ACTIVATION:
        errors.append(f"activation must be {DEFAULT_ACTIVATION!r}")

    functions = config.get("functions")
    if not isinstance(functions, dict) or not functions:
        errors.append("functions must be a non-empty object")
    else:
        for function_name, entry in functions.items():
            if function_name not in FUNCTION_DESCRIPTIONS:
                errors.append(f"functions contains unsupported slot: {function_name}")
                continue
            errors.extend(validate_route_entry(entry, f"functions.{function_name}"))

    overrides = config.get("scenario_overrides")
    if overrides is not None:
        if not isinstance(overrides, dict):
            errors.append("scenario_overrides must be an object when provided")
        else:
            for scenario_name, mapping in overrides.items():
                if not isinstance(mapping, dict) or not mapping:
                    errors.append(f"scenario_overrides.{scenario_name} must be a non-empty object")
                    continue
                for function_name, entry in mapping.items():
                    if function_name not in FUNCTION_DESCRIPTIONS:
                        errors.append(
                            f"scenario_overrides.{scenario_name} contains unsupported slot: {function_name}"
                        )
                        continue
                    errors.extend(
                        validate_route_entry(entry, f"scenario_overrides.{scenario_name}.{function_name}")
                    )

    return errors


def load_routing_config(config_path: str | None) -> tuple[dict[str, object], str | None]:
    path = Path(config_path) if config_path else MODEL_ROUTING_TEMPLATE_PATH
    return load_json(path), str(path)


def required_functions(skill: str, mode: str) -> list[str]:
    skill_map = SKILL_FUNCTIONS.get(skill, SKILL_FUNCTIONS["embedded-feature-planner"])
    return skill_map.get(mode, skill_map["planning"])


def make_disabled_routing(skill: str, config_path: str | None = None) -> dict[str, object]:
    return {
        "enabled": False,
        "activation": DEFAULT_ACTIVATION,
        "requested": {
            "skill": skill,
            "config_path": config_path,
        },
        "source": "default_off",
        "inactive_reason": "模型路由默认关闭，只有显式启用后才会生效。",
        "effective_functions": [],
        "warnings": [],
    }


def resolve_model_routing(
    *,
    task: str,
    mode: str,
    scenario: str,
    skill: str,
    enable_model_routing: bool,
    routing_config_path: str | None,
) -> dict[str, object]:
    if not enable_model_routing:
        return make_disabled_routing(skill, routing_config_path)

    config, effective_path = load_routing_config(routing_config_path)
    errors = validate_routing_config(config)
    if errors:
        return {
            "enabled": False,
            "activation": DEFAULT_ACTIVATION,
            "requested": {
                "skill": skill,
                "config_path": routing_config_path,
            },
            "source": "invalid_config",
            "inactive_reason": "模型路由已显式请求，但配置无效，因此保持关闭。",
            "effective_functions": [],
            "warnings": errors,
        }

    functions = config["functions"]
    overrides = config.get("scenario_overrides", {})
    routes: list[dict[str, str]] = []
    warnings: list[str] = []

    for function_name in required_functions(skill, mode):
        source_label = f"functions.{function_name}"
        selected = functions[function_name]

        if isinstance(overrides, dict):
            scenario_override = overrides.get(scenario)
            if isinstance(scenario_override, dict) and function_name in scenario_override:
                selected = scenario_override[function_name]
                source_label = f"scenario_overrides.{scenario}.{function_name}"

        model_id = str(selected["model_id"])
        if model_id.startswith(PLACEHOLDER_PREFIX):
            warnings.append(f"{source_label} still uses placeholder model_id: {model_id}")

        routes.append(
            {
                "function": function_name,
                "model_id": model_id,
                "reason": str(selected["reason"]),
                "when_to_use": str(selected["when_to_use"]),
                "source": source_label,
            }
        )

    return {
        "enabled": True,
        "activation": DEFAULT_ACTIVATION,
        "requested": {
            "skill": skill,
            "config_path": routing_config_path,
        },
        "source": effective_path,
        "inactive_reason": None,
        "effective_functions": routes,
        "warnings": warnings,
        "config_summary": {
            "schema_version": config["schema_version"],
            "profile_name": config.get("profile_name", "unnamed-profile"),
            "task": task,
            "mode": mode,
            "scenario": scenario,
        },
    }
