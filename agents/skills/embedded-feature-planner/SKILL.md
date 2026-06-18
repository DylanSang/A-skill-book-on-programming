---
name: embedded-feature-planner
description: 嵌入式需求规划与工程修复工作流。用于新功能规划、已有工程功能接入、topStruct 结构梳理、方案/Todo/debug.json 生成，以及 bug 修复、编译失败、运行异常等场景下的证据化分析与闭环执行。Use when the user asks for 新功能规划、方案设计、Todo 拆解、topStruct 分析、嵌入式工程结构梳理，or asks to 修复bug、排查报错、解决编译失败、链接失败、无法运行 in an embedded project.
---

# Embedded Feature Planner

Use this repository-local wrapper to expose the optimized canonical workflow while keeping the entrypoint small and stable.

1. Read `.claude/embedded-feature-planner/AGENTS.md` in full before planning, implementing, generating project documents, or proposing a bug-fix path.
2. Treat `.claude/embedded-feature-planner/AGENTS.md` as the canonical workflow and follow its success criteria, sequencing, uncertainty policy, and forbidden actions.
3. Read `.claude/embedded-feature-planner/references/official-design-principles.md` and `.claude/embedded-feature-planner/references/evidence-and-safety.md` before producing conclusions that depend on repository facts.
4. Read `.claude/embedded-feature-planner/references/workflow-and-outputs.md` when generating or updating `topStruct.md`, `方案.md`, `Todo.md`, or `debug.json`.
5. When the canonical workflow references role prompts, load only the necessary files from `.claude/embedded_ai_roles/embedded_ai_roles/`.
6. When the canonical workflow references rule files, load the needed files from `.claude/embedded_ai_roles/rules/` and preserve safety-first priority.
7. Keep generated artifacts in the current workspace root exactly as the canonical workflow specifies.
8. Before proposing versions, DTS properties, Kconfig symbols, APIs, script arguments, MQTT fields, or proc/sysfs/debugfs nodes, enforce the evidence-first gate: verify support in the current repository or mark the item as `pending`, `custom`, or `to-be-implemented`.
9. Prefer generating `.claude/embedded_ai_roles/scripts/generate_task_packet.py` output before reading many role files, then follow the packet's role list and playbook section.
10. Keep model routing off unless the user explicitly asks to enable different models for different functions; if enabled, follow `.claude/embedded_ai_roles/references/model-routing-policy.md`.
11. When validation is needed, use `.claude/embedded-feature-planner/scripts/validate_planning_artifacts.py`, `.claude/embedded_ai_roles/scripts/validate_task_packet.py`, `.claude/embedded_ai_roles/scripts/validate_model_routing_config.py`, or apply the same checks manually if the scripts cannot be run.
