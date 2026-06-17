# Current State Index

## Canonical Entrypoints

- `.claude/embedded-feature-planner/AGENTS.md`
- `.claude/expert-prompt-generator/AGENTS.md`

## Core Routing Scripts

- `.claude/embedded_ai_roles/scripts/route_task.py`
- `.claude/embedded_ai_roles/scripts/select_roles.py`
- `.claude/embedded_ai_roles/scripts/generate_task_packet.py`
- `.claude/embedded_ai_roles/scripts/resolve_model_routing.py`

## Validation Scripts

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

## Summary Reports

- `优化报告.md`
- `skill-iterations-test/skill-iteration-report.md`
- `skill-iterations-test/claude-roles-iteration-report.md`

## Current Model Routing Status

- Default state: `disabled`
- Explicit opt-in required: `true`
- Config template: `.claude/embedded_ai_roles/assets/model-routing-template.json`
