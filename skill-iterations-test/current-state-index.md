# Current State Index

## Capability Summary

- Canonical workflows for embedded planning and prompt generation
- Task routing, minimal-role selection, and task-packet generation
- Default-off model routing with explicit opt-in
- Structured validation for roles, rules, references, playbooks, planning artifacts, and prompts
- Deterministic repository state snapshots for handoff, drift detection, and recent artifact summaries

## Canonical Entrypoints

- `.claude/embedded-feature-planner/AGENTS.md`
- `.claude/expert-prompt-generator/AGENTS.md`

## Skill Wrappers

- `.agents/skills/embedded-feature-planner/SKILL.md`
- `.agents/skills/expert-prompt-generator/SKILL.md`

## Core Routing Scripts

- `.claude/embedded_ai_roles/scripts/route_task.py`
- `.claude/embedded_ai_roles/scripts/select_roles.py`
- `.claude/embedded_ai_roles/scripts/generate_task_packet.py`
- `.claude/embedded_ai_roles/scripts/resolve_model_routing.py`
- `.claude/embedded_ai_roles/scripts/generate_current_state_index.py`

## Validation Scripts

- `.claude/embedded_ai_roles/scripts/validate_skill_wrappers.py`
- `.claude/embedded_ai_roles/scripts/validate_role_docs.py`
- `.claude/embedded_ai_roles/scripts/validate_rule_docs.py`
- `.claude/embedded_ai_roles/scripts/validate_reference_links.py`
- `.claude/embedded_ai_roles/scripts/validate_playbooks.py`
- `.claude/embedded_ai_roles/scripts/validate_task_packet.py`
- `.claude/embedded_ai_roles/scripts/validate_model_routing_config.py`
- `.claude/embedded-feature-planner/scripts/validate_planning_artifacts.py`
- `.claude/expert-prompt-generator/scripts/validate_prompt_output.py`

## Fixtures

- `skill-iterations-test/task-routing-fixture`
- `skill-iterations-test/task-packet-fixture`
- `skill-iterations-test/model-routing-fixture`
- `skill-iterations-test/embedded-feature-planner-fixture`
- `skill-iterations-test/expert-prompt-generator-fixture`
- `skill-iterations-test/role-output-fixture`
- `skill-iterations-test/role-selection-fixture`

## Summary Reports

- `优化报告.md`
- `skill-iterations-test/skill-iteration-report.md`
- `skill-iterations-test/claude-roles-iteration-report.md`

## Workspace Artifact Presence

- `task-packet.json`: `missing`
- `方案.md`: `missing`
- `Todo.md`: `missing`
- `debug.json`: `missing`
- `describe_prompt.md`: `missing`
- `role-summary.md`: `missing`

## Recent Artifact Snapshot

### Planning Artifact

- Source: `fixture fallback`
- Artifact root: `skill-iterations-test/embedded-feature-planner-fixture`
- Feature: `示例功能`
- Mode / status: `planning` / `planning`
- Created at: `2026-06-15T17:40:00+08:00`
- Objective: `验证规划产物校验脚本是否按预期工作。`
- Next task hint: `[ ] 运行规划校验脚本并确认通过`
- Evidence hint: `skill-iterations-test/embedded-feature-planner-fixture`
- Latest debug log: `validation / Need a minimal fixture for validator verification. / pass`

### Prompt Artifact

- Source: `fixture fallback`
- Artifact path: `skill-iterations-test/expert-prompt-generator-fixture/describe_prompt.md`
- Topic: `Python 安全审查`
- Mode: `通用`
- Timestamp: `2026-06-15 17:40`
- Role line: `你是 Python 应用安全与代码审计领域的资深专家，具备多年安全审查与 CWE 分析经验。`

### Task Packet Artifact

- Source: `fixture fallback`
- Artifact path: `skill-iterations-test/task-packet-fixture/expected-task-packets.json`
- Task: `处理发布前回归不过和交付物不齐的问题`
- Mode / scenario: `planning` / `release_blocker`
- Model routing: `disabled`
- Roles: `project_manager, test_engineer, devops_engineer, system_architect, product_manager`

### Role Summary Artifact

- Source: `fixture fallback`
- Artifact path: `skill-iterations-test/role-output-fixture/role-summary.md`
- Goal hint: `[product_manager_output] 明确当前版本是否需要新增 OTA 容错功能。`
- Risk hint: `[product_manager_output] - 尚未确认当前分区和回滚逻辑是否真实存在。`

## Validation Snapshot

- `validate_skill_wrappers`: `passed`
- `validate_role_docs`: `passed`
- `validate_rule_docs`: `passed`
- `validate_reference_links`: `passed`
- `validate_playbooks`: `passed`
- `validate_task_packet`: `passed`
- `validate_model_routing_config`: `passed`
- `validate_planning_artifacts`: `passed`
- `validate_prompt_output`: `passed`
- `task_routing_fixture`: `passed`
- `task_packet_fixture`: `passed`
- `model_routing_fixture`: `passed`

## Current Model Routing Status

- Default state: `disabled`
- Explicit opt-in required: `true`
- Config template: `.claude/embedded_ai_roles/assets/model-routing-template.json`
