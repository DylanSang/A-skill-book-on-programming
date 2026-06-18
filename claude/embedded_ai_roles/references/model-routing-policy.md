# Model Routing Policy

这个文件定义 skill 体系中的模型路由规则。目标不是默认把任务拆给多个模型，而是在用户明确要求时，才安全、可追踪地启用。

## 默认状态

- 模型路由默认 `disabled`
- 只有在以下任一条件满足时，才允许启用：
  - 用户明确要求“启用模型路由”
  - 用户明确要求“不同功能使用不同模型”
  - 调用脚本时显式传入 `--enable-model-routing`

如果没有这些显式信号，就保持关闭，不做隐式模型选择。

## 设计原则

1. 默认关闭优先于默认智能
   - 避免在没有明确授权时引入成本、延迟或行为分叉。

2. 先按功能路由，再按模型落位
   - 先定义“哪个功能需要什么能力”，再决定“用哪个模型”。

3. 路由配置优先于硬编码
   - 不把具体模型 ID 写死在主流程文档里。
   - 优先通过 JSON 配置文件指定。

4. 路由结果必须可追踪
   - 一旦启用，`task-packet.json` 或路由结果中必须记录：
     - 是否启用
     - 由谁显式启用
     - 使用了哪个配置文件
     - 每个功能落到哪个模型

5. 关闭状态也要显式记录
   - `disabled` 不是“缺省省略”，而是要在结构化结果中明确表示。

## 推荐功能槽位

以下功能槽位适合做模型分工：

- `task_routing`
- `planning`
- `implementation`
- `debug`
- `role_synthesis`
- `artifact_review`
- `prompt_generation`

## 推荐启用方式

### Embedded Feature Planner

```bash
python .claude/embedded_ai_roles/scripts/generate_task_packet.py --task "<用户任务描述>" --enable-model-routing --routing-config "<配置文件路径>" --output task-packet.json
```

### Expert Prompt Generator

```bash
python .claude/embedded_ai_roles/scripts/resolve_model_routing.py --skill expert-prompt-generator --task "<用户需求>" --enable-model-routing --routing-config "<配置文件路径>" --json
```

## 配置文件要求

推荐基于：

- `.claude/embedded_ai_roles/assets/model-routing-template.json`

配置文件应满足：

- `default_enabled` 必须为 `false`
- `activation` 必须为 `explicit_opt_in_required`
- 至少定义一个 `functions` 路由表
- 如需覆盖场景，可使用 `scenario_overrides`

## 禁止事项

- 不要在没有明确提示时自动启用
- 不要把“推荐模型层级”伪装成“已选择具体模型”
- 不要把模型路由结果写成不可追踪的自然语言描述
- 不要把主流程绑定到单一厂商的临时模型命名
