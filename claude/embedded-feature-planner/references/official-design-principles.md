# Official Design Principles

这个参考文件把头部 AI 厂商的公开 guidance 提炼成适合 skill/agent 工作流的规则。

## 核心原则

1. 先定义成功标准，再写长指令
   - Anthropic 官方 prompting overview 强调先从 success criteria 出发，而不是盲目加 prompt 细节。
   - 在本 skill 中体现为：先定义“证据充分、输出可交接、修复有闭环”，再执行具体步骤。

2. 指令前置，结构清晰，边界明确
   - OpenAI 官方建议把指令放在前面，并明确分隔上下文与任务。
   - Microsoft 官方强调要具体、限制操作空间。
   - 在本 skill 中体现为：AGENTS 主文件先给成功标准、读文件顺序、执行顺序和禁止事项。

3. 输出契约必须显式
   - OpenAI 和 Microsoft 都强调输出格式要写清楚。
   - OpenAI 还建议在结构化输出场景使用 schema、校验和必要重试。
   - 在本 skill 中体现为：`方案.md`、`Todo.md`、`debug.json` 都有固定章节和字段，并配套校验脚本。

4. 不确定时要有明确策略
   - Microsoft system message design guidance 明确建议加入 “when unsure” policy。
   - 在本 skill 中体现为：证据不足时标 `pending`，最多问 1 个关键问题，其余用假设块推进。

5. 提示需要测试、度量和迭代
   - Google 官方 prompt design strategies 和 prompt iteration guidance 都强调严格测试与迭代。
   - 在本 skill 中体现为：产物落地后必须运行校验脚本或手工按同等标准验收。

6. 主文件要短，细节按需加载
   - Anthropic 的 context engineering 思路强调上下文是有限资源。
   - 在本 skill 中体现为：把大段规则拆到 `references/`，主 AGENTS 只保留决策骨架。

7. 先路由，再执行，再校验
   - Google 和 OpenAI 的公开方法都强调在复杂任务里先拆清类别、目标和评估，再让主体流程执行。
   - 在本 skill 中体现为：先生成 `task-packet.json`，再读取最少必要角色与 playbook，最后产出正式文档并校验。

8. 高成本能力默认关闭，显式启用
   - 头部厂商公开 guidance 一致强调：额外能力、额外成本、额外风险都应在边界清楚时才启用。
   - 在本 skill 中体现为：模型路由默认 `disabled`，只有用户明确要求时才启用并写入结构化结果。

## 对本 skill 的直接要求

- 主 AGENTS 只保留执行骨架、门禁和路由。
- 细节模板、字段说明和检查表放到 `references/`。
- 角色文件和规则文件按需读取，不默认全量加载。
- 每次输出都要显式区分：
  - 已确认
  - 待确认
  - 需实现
