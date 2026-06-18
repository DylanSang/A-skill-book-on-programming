---
name: expert-prompt-generator
description: 根据用户需求生成精简、专家级、可复用的 AI prompt，并以追加方式写入当前工作目录的 describe_prompt.md。支持嵌入式与通用模式路由、角色设计、提示词优化、describe_prompt.md 维护，以及把模糊请求收敛为结构化高质量 prompt。Use when the user asks 生成 prompt、写 prompt、设计角色、专家提示词、prompt engineering、提示词优化、给我一个 prompt，or mentions describe_prompt.md / discribe_prompt.md.
---

# Expert Prompt Generator

Use this repository-local wrapper to expose the optimized canonical workflow while keeping the entrypoint lightweight.

1. Read `.claude/expert-prompt-generator/AGENTS.md` in full before generating or appending any prompt output.
2. Treat `.claude/expert-prompt-generator/AGENTS.md` as the canonical workflow and preserve its success criteria, four-line prompt contract, append behavior, and file naming rules.
3. Read `.claude/expert-prompt-generator/references/official-design-principles.md` before changing the prompt structure.
4. Read `.claude/expert-prompt-generator/references/domain-routing.md` when classifying the request into embedded or general mode.
5. Read `.claude/expert-prompt-generator/references/prompt-quality-rubric.md` before finalizing output.
6. Keep model routing off unless the user explicitly asks to route different functions to different models; if enabled, follow `.claude/embedded_ai_roles/references/model-routing-policy.md`.
7. Write output to the current workspace root exactly as the canonical workflow specifies, especially `describe_prompt.md`.
8. Validate output with `.claude/expert-prompt-generator/scripts/validate_prompt_output.py` when practical, or apply the same checks manually if the script cannot be run.
