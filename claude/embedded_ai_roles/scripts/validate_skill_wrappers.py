#!/usr/bin/env python3
"""Validate repository-local skill wrappers against canonical workflow adapters."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class WrapperSpec:
    skill_name: str
    display_name: str
    wrapper_path: str
    openai_yaml_path: str
    canonical_path: str
    required_wrapper_signals: tuple[str, ...]
    required_description_signals: tuple[str, ...]
    required_short_description_signals: tuple[str, ...]
    required_default_prompt_signals: tuple[str, ...]


SPECS = (
    WrapperSpec(
        skill_name="embedded-feature-planner",
        display_name="Embedded Feature Planner",
        wrapper_path=".agents/skills/embedded-feature-planner/SKILL.md",
        openai_yaml_path=".agents/skills/embedded-feature-planner/agents/openai.yaml",
        canonical_path=".claude/embedded-feature-planner/AGENTS.md",
        required_wrapper_signals=(
            ".claude/embedded-feature-planner/AGENTS.md",
            ".claude/embedded-feature-planner/references/official-design-principles.md",
            ".claude/embedded-feature-planner/references/evidence-and-safety.md",
            ".claude/embedded-feature-planner/references/workflow-and-outputs.md",
            ".claude/embedded_ai_roles/scripts/generate_task_packet.py",
            ".claude/embedded_ai_roles/references/model-routing-policy.md",
            ".claude/embedded-feature-planner/scripts/validate_planning_artifacts.py",
            ".claude/embedded_ai_roles/scripts/validate_task_packet.py",
            ".claude/embedded_ai_roles/scripts/validate_model_routing_config.py",
            "canonical workflow",
            "repository-local wrapper",
        ),
        required_description_signals=(
            "方案/Todo/debug.json",
            "修复bug",
            "embedded project",
        ),
        required_short_description_signals=(
            "嵌入式",
            "任务包",
        ),
        required_default_prompt_signals=(
            "Use $embedded-feature-planner",
            "model routing disabled",
            "task packet",
            "evidence",
            "planning and debug artifacts",
        ),
    ),
    WrapperSpec(
        skill_name="expert-prompt-generator",
        display_name="Expert Prompt Generator",
        wrapper_path=".agents/skills/expert-prompt-generator/SKILL.md",
        openai_yaml_path=".agents/skills/expert-prompt-generator/agents/openai.yaml",
        canonical_path=".claude/expert-prompt-generator/AGENTS.md",
        required_wrapper_signals=(
            ".claude/expert-prompt-generator/AGENTS.md",
            ".claude/expert-prompt-generator/references/official-design-principles.md",
            ".claude/expert-prompt-generator/references/domain-routing.md",
            ".claude/expert-prompt-generator/references/prompt-quality-rubric.md",
            ".claude/embedded_ai_roles/references/model-routing-policy.md",
            ".claude/expert-prompt-generator/scripts/validate_prompt_output.py",
            "describe_prompt.md",
            "canonical workflow",
            "repository-local wrapper",
        ),
        required_description_signals=(
            "describe_prompt.md",
            "prompt",
            "提示词优化",
        ),
        required_short_description_signals=(
            "Prompt",
            "沉淀",
        ),
        required_default_prompt_signals=(
            "Use $expert-prompt-generator",
            "concise",
            "expert-grade prompt",
            "append",
            "describe_prompt.md",
        ),
    ),
)


REPO_PATH_PATTERN = re.compile(r"`((?:\.claude|\.agents)/[^`]+)`")


def repo_path(relative_path: str) -> Path:
    return REPO_ROOT / relative_path


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---"):
        return (None, text)

    lines = text.splitlines()
    if len(lines) < 3:
        return (None, text)

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        return (None, text)

    frontmatter = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :])
    return (frontmatter, body)


def parse_simple_yaml_block(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        values[key.strip()] = strip_quotes(raw_value.strip())
    return values


def extract_yaml_scalar(text: str, key: str) -> str | None:
    pattern = re.compile(rf"(?m)^\s*{re.escape(key)}:\s*(.+?)\s*$")
    match = pattern.search(text)
    if not match:
        return None
    return strip_quotes(match.group(1))


def validate_wrapper_markdown(spec: WrapperSpec) -> list[str]:
    path = repo_path(spec.wrapper_path)
    errors: list[str] = []

    if not path.exists():
        return [f"{spec.skill_name}: missing wrapper file {spec.wrapper_path}"]

    text = path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(text)

    if frontmatter is None:
        errors.append(f"{spec.skill_name}: wrapper is missing YAML frontmatter")
        return errors

    parsed = parse_simple_yaml_block(frontmatter)
    if parsed.get("name") != spec.skill_name:
        errors.append(
            f"{spec.skill_name}: wrapper frontmatter name must be {spec.skill_name!r}, got {parsed.get('name')!r}"
        )

    description = parsed.get("description", "")
    if not description:
        errors.append(f"{spec.skill_name}: wrapper frontmatter description is required")
    else:
        for signal in spec.required_description_signals:
            if signal not in description:
                errors.append(f"{spec.skill_name}: wrapper description missing signal `{signal}`")

    for signal in spec.required_wrapper_signals:
        if signal not in body:
            errors.append(f"{spec.skill_name}: wrapper body missing signal `{signal}`")

    if spec.canonical_path not in body:
        errors.append(f"{spec.skill_name}: wrapper must point to canonical file {spec.canonical_path}")

    for relative_path in REPO_PATH_PATTERN.findall(body):
        if not repo_path(relative_path).exists():
            errors.append(f"{spec.skill_name}: wrapper references missing repo path `{relative_path}`")

    return errors


def validate_openai_yaml(spec: WrapperSpec) -> list[str]:
    path = repo_path(spec.openai_yaml_path)
    errors: list[str] = []

    if not path.exists():
        return [f"{spec.skill_name}: missing UI metadata file {spec.openai_yaml_path}"]

    text = path.read_text(encoding="utf-8")
    display_name = extract_yaml_scalar(text, "display_name")
    short_description = extract_yaml_scalar(text, "short_description")
    default_prompt = extract_yaml_scalar(text, "default_prompt")
    allow_implicit = extract_yaml_scalar(text, "allow_implicit_invocation")

    if display_name != spec.display_name:
        errors.append(
            f"{spec.skill_name}: display_name must be {spec.display_name!r}, got {display_name!r}"
        )

    if not short_description:
        errors.append(f"{spec.skill_name}: short_description is required")
    else:
        for signal in spec.required_short_description_signals:
            if signal not in short_description:
                errors.append(f"{spec.skill_name}: short_description missing signal `{signal}`")

    if not default_prompt:
        errors.append(f"{spec.skill_name}: default_prompt is required")
    else:
        for signal in spec.required_default_prompt_signals:
            if signal not in default_prompt:
                errors.append(f"{spec.skill_name}: default_prompt missing signal `{signal}`")

    if allow_implicit != "true":
        errors.append(f"{spec.skill_name}: allow_implicit_invocation must be true")

    return errors


def validate_canonical_path(spec: WrapperSpec) -> list[str]:
    if repo_path(spec.canonical_path).exists():
        return []
    return [f"{spec.skill_name}: canonical file does not exist: {spec.canonical_path}"]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Workspace root")
    parser.parse_args()

    errors: list[str] = []
    for spec in SPECS:
        errors.extend(validate_canonical_path(spec))
        errors.extend(validate_wrapper_markdown(spec))
        errors.extend(validate_openai_yaml(spec))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Skill wrapper validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
