#!/usr/bin/env python3
"""Generate or check a deterministic repository state index."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]

CANONICAL_ENTRYPOINTS = (
    ".claude/embedded-feature-planner/AGENTS.md",
    ".claude/expert-prompt-generator/AGENTS.md",
)

SKILL_WRAPPERS = (
    ".agents/skills/embedded-feature-planner/SKILL.md",
    ".agents/skills/expert-prompt-generator/SKILL.md",
)

CORE_ROUTING_SCRIPTS = (
    ".claude/embedded_ai_roles/scripts/route_task.py",
    ".claude/embedded_ai_roles/scripts/select_roles.py",
    ".claude/embedded_ai_roles/scripts/generate_task_packet.py",
    ".claude/embedded_ai_roles/scripts/resolve_model_routing.py",
    ".claude/embedded_ai_roles/scripts/generate_current_state_index.py",
)

VALIDATION_SCRIPTS = (
    ".claude/embedded_ai_roles/scripts/validate_skill_wrappers.py",
    ".claude/embedded_ai_roles/scripts/validate_role_docs.py",
    ".claude/embedded_ai_roles/scripts/validate_rule_docs.py",
    ".claude/embedded_ai_roles/scripts/validate_reference_links.py",
    ".claude/embedded_ai_roles/scripts/validate_playbooks.py",
    ".claude/embedded_ai_roles/scripts/validate_task_packet.py",
    ".claude/embedded_ai_roles/scripts/validate_model_routing_config.py",
    ".claude/embedded-feature-planner/scripts/validate_planning_artifacts.py",
    ".claude/expert-prompt-generator/scripts/validate_prompt_output.py",
)

FIXTURE_DIRS = (
    "skill-iterations-test/task-routing-fixture",
    "skill-iterations-test/task-packet-fixture",
    "skill-iterations-test/model-routing-fixture",
    "skill-iterations-test/embedded-feature-planner-fixture",
    "skill-iterations-test/expert-prompt-generator-fixture",
    "skill-iterations-test/role-output-fixture",
    "skill-iterations-test/role-selection-fixture",
)

SUMMARY_REPORTS = (
    "优化报告.md",
    "skill-iterations-test/skill-iteration-report.md",
    "skill-iterations-test/claude-roles-iteration-report.md",
)

MODEL_ROUTING_CONFIG = ".claude/embedded_ai_roles/assets/model-routing-template.json"
WORKSPACE_ARTIFACTS = (
    "task-packet.json",
    "方案.md",
    "Todo.md",
    "debug.json",
    "describe_prompt.md",
    "role-summary.md",
)
PLANNING_FIXTURE_DIR = "skill-iterations-test/embedded-feature-planner-fixture"
PROMPT_FIXTURE_FILE = "skill-iterations-test/expert-prompt-generator-fixture/describe_prompt.md"
TASK_PACKET_FIXTURE_FILE = "skill-iterations-test/task-packet-fixture/expected-task-packets.json"
ROLE_SUMMARY_FIXTURE_FILE = "skill-iterations-test/role-output-fixture/role-summary.md"

CAPABILITY_RULES = (
    (
        "Canonical workflows for embedded planning and prompt generation",
        (
            ".claude/embedded-feature-planner/AGENTS.md",
            ".claude/expert-prompt-generator/AGENTS.md",
        ),
    ),
    (
        "Task routing, minimal-role selection, and task-packet generation",
        (
            ".claude/embedded_ai_roles/scripts/route_task.py",
            ".claude/embedded_ai_roles/scripts/select_roles.py",
            ".claude/embedded_ai_roles/scripts/generate_task_packet.py",
        ),
    ),
    (
        "Default-off model routing with explicit opt-in",
        (
            ".claude/embedded_ai_roles/references/model-routing-policy.md",
            ".claude/embedded_ai_roles/scripts/resolve_model_routing.py",
            ".claude/embedded_ai_roles/scripts/validate_model_routing_config.py",
        ),
    ),
    (
        "Structured validation for roles, rules, references, playbooks, planning artifacts, and prompts",
        (
            ".claude/embedded_ai_roles/scripts/validate_skill_wrappers.py",
            ".claude/embedded_ai_roles/scripts/validate_role_docs.py",
            ".claude/embedded_ai_roles/scripts/validate_rule_docs.py",
            ".claude/embedded_ai_roles/scripts/validate_reference_links.py",
            ".claude/embedded_ai_roles/scripts/validate_playbooks.py",
            ".claude/embedded-feature-planner/scripts/validate_planning_artifacts.py",
            ".claude/expert-prompt-generator/scripts/validate_prompt_output.py",
        ),
    ),
    (
        "Deterministic repository state snapshots for handoff, drift detection, and recent artifact summaries",
        (".claude/embedded_ai_roles/scripts/generate_current_state_index.py",),
    ),
)


@dataclass(frozen=True)
class ValidationCommand:
    name: str
    command: tuple[str, ...]


VALIDATION_COMMANDS = (
    ValidationCommand(
        "validate_skill_wrappers",
        (sys.executable, ".claude/embedded_ai_roles/scripts/validate_skill_wrappers.py"),
    ),
    ValidationCommand(
        "validate_role_docs",
        (sys.executable, ".claude/embedded_ai_roles/scripts/validate_role_docs.py"),
    ),
    ValidationCommand(
        "validate_rule_docs",
        (sys.executable, ".claude/embedded_ai_roles/scripts/validate_rule_docs.py"),
    ),
    ValidationCommand(
        "validate_reference_links",
        (sys.executable, ".claude/embedded_ai_roles/scripts/validate_reference_links.py"),
    ),
    ValidationCommand(
        "validate_playbooks",
        (sys.executable, ".claude/embedded_ai_roles/scripts/validate_playbooks.py"),
    ),
    ValidationCommand(
        "validate_task_packet",
        (
            sys.executable,
            ".claude/embedded_ai_roles/scripts/validate_task_packet.py",
            "--task",
            "处理发布前回归不过和交付物不齐的问题",
        ),
    ),
    ValidationCommand(
        "validate_model_routing_config",
        (
            sys.executable,
            ".claude/embedded_ai_roles/scripts/validate_model_routing_config.py",
            "--config",
            MODEL_ROUTING_CONFIG,
        ),
    ),
    ValidationCommand(
        "validate_planning_artifacts",
        (
            sys.executable,
            ".claude/embedded-feature-planner/scripts/validate_planning_artifacts.py",
            "--workspace",
            "skill-iterations-test/embedded-feature-planner-fixture",
        ),
    ),
    ValidationCommand(
        "validate_prompt_output",
        (
            sys.executable,
            ".claude/expert-prompt-generator/scripts/validate_prompt_output.py",
            "--describe-file",
            "skill-iterations-test/expert-prompt-generator-fixture/describe_prompt.md",
        ),
    ),
    ValidationCommand(
        "task_routing_fixture",
        (sys.executable, "skill-iterations-test/task-routing-fixture/check_task_routes.py"),
    ),
    ValidationCommand(
        "task_packet_fixture",
        (sys.executable, "skill-iterations-test/task-packet-fixture/check_task_packets.py"),
    ),
    ValidationCommand(
        "model_routing_fixture",
        (sys.executable, "skill-iterations-test/model-routing-fixture/check_model_routing.py"),
    ),
)


def repo_path(relative_path: str) -> Path:
    return REPO_ROOT / relative_path


def output_path(raw_path: str) -> Path:
    path = Path(raw_path)
    return path if path.is_absolute() else REPO_ROOT / path


def existing_paths(paths: tuple[str, ...]) -> list[str]:
    return [path for path in paths if repo_path(path).exists()]


def add_path_section(lines: list[str], title: str, paths: tuple[str, ...]) -> None:
    lines.extend([f"## {title}", ""])
    for path in existing_paths(paths):
        lines.append(f"- `{path}`")
    lines.append("")


def build_utf8_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def run_validation(command: ValidationCommand) -> str:
    result = subprocess.run(
        command.command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=build_utf8_env(),
        check=False,
    )
    return "passed" if result.returncode == 0 else "failed"


def load_model_routing_status() -> tuple[str, str, str]:
    config_path = repo_path(MODEL_ROUTING_CONFIG)
    if not config_path.exists():
        return ("unknown", "unknown", MODEL_ROUTING_CONFIG)

    data = json.loads(config_path.read_text(encoding="utf-8"))
    default_enabled = "enabled" if data.get("default_enabled") else "disabled"
    explicit_opt_in = "true" if data.get("activation") == "explicit_opt_in_required" else "false"
    return (default_enabled, explicit_opt_in, MODEL_ROUTING_CONFIG)


def read_json_if_exists(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_text_if_exists(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def extract_first_meaningful_line(block: str) -> str | None:
    for raw_line in block.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        return line.lstrip("- ").strip()
    return None


def extract_section_summary(text: str, heading: str) -> str | None:
    pattern = re.compile(rf"{re.escape(heading)}\n(.*?)(?:\n## |\Z)", re.DOTALL)
    match = pattern.search(text)
    if not match:
        return None
    return extract_first_meaningful_line(match.group(1))


def add_workspace_artifact_presence(lines: list[str]) -> None:
    lines.extend(["## Workspace Artifact Presence", ""])
    for relative_path in WORKSPACE_ARTIFACTS:
        status = "present" if repo_path(relative_path).exists() else "missing"
        lines.append(f"- `{relative_path}`: `{status}`")
    lines.append("")


def build_planning_snapshot() -> list[str]:
    workspace_debug = repo_path("debug.json")
    fixture_debug = repo_path(f"{PLANNING_FIXTURE_DIR}/debug.json")

    debug_path = workspace_debug if workspace_debug.exists() else fixture_debug
    source_label = "workspace root" if workspace_debug.exists() else "fixture fallback"
    artifact_root = debug_path.parent
    debug_data = read_json_if_exists(debug_path)
    plan_text = read_text_if_exists(artifact_root / "方案.md")
    todo_text = read_text_if_exists(artifact_root / "Todo.md")

    if debug_data is None:
        return [
            "### Planning Artifact",
            "",
            "- Source: `unavailable`",
            "- Reason: `No debug.json or fixture fallback found.`",
            "",
        ]

    feature = debug_data.get("feature", "unknown")
    mode = debug_data.get("mode", "unknown")
    status = debug_data.get("status", "unknown")
    created_at = debug_data.get("created_at", "unknown")

    evidence_hint = None
    evidence = debug_data.get("evidence")
    if isinstance(evidence, list) and evidence:
        first = evidence[0]
        if isinstance(first, dict):
            evidence_hint = first.get("path") or first.get("type")

    latest_debug_result = None
    latest_debug_log = debug_data.get("debug_log")
    if isinstance(latest_debug_log, list) and latest_debug_log:
        last = latest_debug_log[-1]
        if isinstance(last, dict):
            latest_debug_result = " / ".join(
                str(last.get(key, "unknown")) for key in ("module", "issue", "result")
            )

    next_task = extract_section_summary(todo_text, "## 任务列表") if todo_text else None
    objective = extract_section_summary(plan_text, "## 目标与范围") if plan_text else None

    lines = [
        "### Planning Artifact",
        "",
        f"- Source: `{source_label}`",
        f"- Artifact root: `{artifact_root.relative_to(REPO_ROOT).as_posix()}`",
        f"- Feature: `{feature}`",
        f"- Mode / status: `{mode}` / `{status}`",
        f"- Created at: `{created_at}`",
    ]
    if objective:
        lines.append(f"- Objective: `{objective}`")
    if next_task:
        lines.append(f"- Next task hint: `{next_task}`")
    if evidence_hint:
        lines.append(f"- Evidence hint: `{evidence_hint}`")
    if latest_debug_result:
        lines.append(f"- Latest debug log: `{latest_debug_result}`")
    lines.append("")
    return lines


def extract_latest_prompt_snapshot(text: str) -> dict[str, str] | None:
    heading_pattern = re.compile(r"^## \[(?P<timestamp>[^\]]+)\] - (?P<title>.+)$", re.MULTILINE)
    matches = list(heading_pattern.finditer(text))
    if not matches:
        return None

    latest = matches[-1]
    block = text[latest.start() :]
    mode_match = re.search(r"\*\*模式\*\*：\s*(.+)", block)
    prompt_match = re.search(r"\*\*生成 Prompt\*\*：\s*```(?:\r?\n)(.*?)(?:\r?\n)```", block, re.DOTALL)
    prompt_first_line = None
    if prompt_match:
        prompt_first_line = extract_first_meaningful_line(prompt_match.group(1))

    snapshot = {
        "timestamp": latest.group("timestamp").strip(),
        "title": latest.group("title").strip(),
    }
    if mode_match:
        snapshot["mode"] = mode_match.group(1).strip()
    if prompt_first_line:
        snapshot["role_line"] = prompt_first_line
    return snapshot


def build_prompt_snapshot() -> list[str]:
    workspace_prompt = repo_path("describe_prompt.md")
    prompt_path = workspace_prompt if workspace_prompt.exists() else repo_path(PROMPT_FIXTURE_FILE)
    source_label = "workspace root" if workspace_prompt.exists() else "fixture fallback"
    text = read_text_if_exists(prompt_path)
    snapshot = extract_latest_prompt_snapshot(text) if text else None

    if snapshot is None:
        return [
            "### Prompt Artifact",
            "",
            "- Source: `unavailable`",
            "- Reason: `No describe_prompt.md or fixture fallback found.`",
            "",
        ]

    lines = [
        "### Prompt Artifact",
        "",
        f"- Source: `{source_label}`",
        f"- Artifact path: `{prompt_path.relative_to(REPO_ROOT).as_posix()}`",
        f"- Topic: `{snapshot.get('title', 'unknown')}`",
        f"- Mode: `{snapshot.get('mode', 'unknown')}`",
        f"- Timestamp: `{snapshot.get('timestamp', 'unknown')}`",
    ]
    if snapshot.get("role_line"):
        lines.append(f"- Role line: `{snapshot['role_line']}`")
    lines.append("")
    return lines


def build_task_packet_snapshot() -> list[str]:
    workspace_packet = repo_path("task-packet.json")
    packet_data = read_json_if_exists(workspace_packet)

    if packet_data is not None:
        source_label = "workspace root"
        packet_path = workspace_packet.relative_to(REPO_ROOT).as_posix()
    else:
        source_label = "fixture fallback"
        fixture_data = read_json_if_exists(repo_path(TASK_PACKET_FIXTURE_FILE))
        if not isinstance(fixture_data, dict) or not fixture_data:
            return [
                "### Task Packet Artifact",
                "",
                "- Source: `unavailable`",
                "- Reason: `No task-packet.json or fixture fallback found.`",
                "",
            ]
        _, packet_data = list(fixture_data.items())[-1]
        packet_path = TASK_PACKET_FIXTURE_FILE

    roles = packet_data.get("roles") if isinstance(packet_data, dict) else None
    role_summary = None
    if isinstance(roles, list) and roles:
        role_names: list[str] = []
        for role in roles:
            if isinstance(role, dict) and "id" in role:
                role_names.append(str(role["id"]))
        if role_names:
            role_summary = ", ".join(role_names)
    elif isinstance(packet_data, dict):
        required_roles = packet_data.get("required_roles")
        if isinstance(required_roles, list) and required_roles:
            role_summary = ", ".join(str(role) for role in required_roles)

    model_routing = "unknown"
    if isinstance(packet_data, dict):
        routing = packet_data.get("model_routing")
        if isinstance(routing, dict) and "enabled" in routing:
            model_routing = "enabled" if routing.get("enabled") else "disabled"
        elif "model_routing_enabled" in packet_data:
            model_routing = "enabled" if packet_data.get("model_routing_enabled") else "disabled"

    lines = [
        "### Task Packet Artifact",
        "",
        f"- Source: `{source_label}`",
        f"- Artifact path: `{packet_path}`",
        f"- Task: `{packet_data.get('task', 'unknown')}`",
        f"- Mode / scenario: `{packet_data.get('mode', 'unknown')}` / `{packet_data.get('scenario', 'unknown')}`",
        f"- Model routing: `{model_routing}`",
    ]
    if isinstance(packet_data, dict) and packet_data.get("playbook_section"):
        lines.append(f"- Playbook section: `{packet_data['playbook_section']}`")
    if role_summary:
        lines.append(f"- Roles: `{role_summary}`")
    lines.append("")
    return lines


def build_role_summary_snapshot() -> list[str]:
    workspace_summary = repo_path("role-summary.md")
    summary_path = workspace_summary if workspace_summary.exists() else repo_path(ROLE_SUMMARY_FIXTURE_FILE)
    source_label = "workspace root" if workspace_summary.exists() else "fixture fallback"
    text = read_text_if_exists(summary_path)

    if text is None:
        return [
            "### Role Summary Artifact",
            "",
            "- Source: `unavailable`",
            "- Reason: `No role-summary.md or fixture fallback found.`",
            "",
        ]

    goal = extract_section_summary(text, "## 目标")
    risk = extract_section_summary(text, "## 风险与待确认")

    lines = [
        "### Role Summary Artifact",
        "",
        f"- Source: `{source_label}`",
        f"- Artifact path: `{summary_path.relative_to(REPO_ROOT).as_posix()}`",
    ]
    if goal:
        lines.append(f"- Goal hint: `{goal}`")
    if risk:
        lines.append(f"- Risk hint: `{risk}`")
    lines.append("")
    return lines


def add_recent_artifact_snapshot(lines: list[str]) -> None:
    lines.extend(["## Recent Artifact Snapshot", ""])
    lines.extend(build_planning_snapshot())
    lines.extend(build_prompt_snapshot())
    lines.extend(build_task_packet_snapshot())
    lines.extend(build_role_summary_snapshot())


def render_index(run_validations: bool) -> str:
    lines: list[str] = ["# Current State Index", ""]

    lines.extend(["## Capability Summary", ""])
    for capability, required_paths in CAPABILITY_RULES:
        if all(repo_path(path).exists() for path in required_paths):
            lines.append(f"- {capability}")
    lines.append("")

    add_path_section(lines, "Canonical Entrypoints", CANONICAL_ENTRYPOINTS)
    add_path_section(lines, "Skill Wrappers", SKILL_WRAPPERS)
    add_path_section(lines, "Core Routing Scripts", CORE_ROUTING_SCRIPTS)
    add_path_section(lines, "Validation Scripts", VALIDATION_SCRIPTS)
    add_path_section(lines, "Fixtures", FIXTURE_DIRS)
    add_path_section(lines, "Summary Reports", SUMMARY_REPORTS)
    add_workspace_artifact_presence(lines)
    add_recent_artifact_snapshot(lines)

    if run_validations:
        lines.extend(["## Validation Snapshot", ""])
        for command in VALIDATION_COMMANDS:
            status = run_validation(command)
            lines.append(f"- `{command.name}`: `{status}`")
        lines.append("")

    default_state, explicit_opt_in, config_template = load_model_routing_status()
    lines.extend(
        [
            "## Current Model Routing Status",
            "",
            f"- Default state: `{default_state}`",
            f"- Explicit opt-in required: `{explicit_opt_in}`",
            f"- Config template: `{config_template}`",
            "",
        ]
    )

    return "\n".join(lines)


def check_output(target_path: Path, expected_text: str) -> int:
    if not target_path.exists():
        print(f"ERROR: Missing file: {target_path}")
        return 1

    actual_text = target_path.read_text(encoding="utf-8")
    if actual_text == expected_text:
        print("Current state index is up to date.")
        return 0

    diff = difflib.unified_diff(
        actual_text.splitlines(),
        expected_text.splitlines(),
        fromfile=str(target_path),
        tofile="generated",
        lineterm="",
    )
    for line in diff:
        print(line)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Write the generated index to a markdown file")
    parser.add_argument("--check", help="Compare a markdown file with the generated index")
    parser.add_argument(
        "--skip-validations",
        action="store_true",
        help="Render the index without running validation commands",
    )
    args = parser.parse_args()

    if args.output and args.check:
        parser.error("--output and --check are mutually exclusive")

    generated = render_index(run_validations=not args.skip_validations)

    if args.check:
        return check_output(output_path(args.check), generated)

    if args.output:
        target_path = output_path(args.output)
        target_path.write_text(generated, encoding="utf-8")
        print(f"Wrote current state index to {target_path}")
        return 0

    print(generated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
