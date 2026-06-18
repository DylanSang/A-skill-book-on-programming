# Official Design Principles

这个 skill 的设计吸收了公开官方 guidance 中最稳定、最可迁移的部分。

## 核心原则

1. 先明确目标，再写 prompt
   - Anthropic 官方材料强调 success criteria 优先。
   - 这里体现为：先确定角色、任务、约束、输出，再组装文字。

2. 把要求写具体，限制歧义空间
   - OpenAI 和 Microsoft 都强调要具体、描述清楚输出格式和边界。
   - 这里体现为：强制四行结构，不允许角色和输出要求缺失。

3. 结构化优于散文化
   - OpenAI Structured Outputs guidance 强调 schema、校验与必要重试。
   - 这里体现为：把 prompt 与 `describe_prompt.md` 追加格式视为固定契约，并提供校验脚本。

4. 需要“when unsure”策略
   - Microsoft 的 system message design guidance 建议显式说明模型在信息不足时该怎么做。
   - 这里体现为：需求很短时最多问 1 个问题，否则用保守默认值补齐。

5. 设计需要持续测试和迭代
   - Google 官方 prompt design strategies 与 iteration guidance 都强调测试、评估、迭代。
   - 这里体现为：每次生成后都验证四行结构与 Markdown 追加格式。

6. 先收敛任务槽位，再生成正文
   - OpenAI、Anthropic 和 Microsoft 的公开 guidance 都强调：角色、任务、约束、输出要先明确，再开始写 prompt。
   - 这里体现为：先提炼四个槽位，再按固定结构组装，而不是先写长提示词再回头删改。

## 对本 skill 的直接要求

- 主 AGENTS 简短，只保留流程骨架与禁止事项。
- 路由逻辑、质量 rubric 和示例格式放在 references 中按需读取。
- Prompt 尽量短，但信息槽位不能缺。
- 如果后续新增模板，也优先做成可校验契约，而不是放任自由文本增长。
