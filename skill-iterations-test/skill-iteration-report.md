# Skill Iteration Report

## 背景

当前 workspace 中真正可执行的 skill 行为主要由以下 canonical 文件决定：

- `.claude/embedded-feature-planner/AGENTS.md`
- `.claude/expert-prompt-generator/AGENTS.md`

`.agents/skills/*/SKILL.md` 目前是轻量 wrapper，但在当前环境中这些目录是只读，因此本轮迭代优先落在 canonical 工作流上。

## 三轮迭代结果

### 第 1 轮：收紧入口与输出契约

- 重写两份 canonical `AGENTS.md`
- 把“成功标准、读文件顺序、执行顺序、禁止事项”前置
- 明确区分：
  - 规划
  - 实现
  - 调试
- 给出稳定输出契约，而不是只描述大方向

### 第 2 轮：补验证与不确定性策略

- 为 `embedded-feature-planner` 新增：
  - `references/evidence-and-safety.md`
  - `references/workflow-and-outputs.md`
  - `scripts/validate_planning_artifacts.py`
- 为 `expert-prompt-generator` 新增：
  - `references/domain-routing.md`
  - `references/prompt-quality-rubric.md`
  - `scripts/validate_prompt_output.py`
- 增加“when unsure”策略和 `pending` 机制

### 第 3 轮：降上下文耦合并验证可执行性

- 把大段规则拆到 `references/`，减少主文件上下文膨胀
- 明确角色文件和规则文件按需读取，而非默认全量加载
- 用样例 fixture 验证校验脚本：
  - `skill-iterations-test/embedded-feature-planner-fixture`
  - `skill-iterations-test/expert-prompt-generator-fixture`

### 第 4 轮：同步 wrapper 入口与修复校验器兼容性

- 更新 `.agents/skills/*/SKILL.md`，让 wrapper 的触发范围、导航说明和 canonical 行为一致
- 更新 `.agents/skills/*/agents/openai.yaml`
  - `short_description`
  - `default_prompt`
- 修复 `C:/Users/maitekai/.codex/skills/.system/skill-creator/scripts/quick_validate.py`
  - 从系统默认编码读取改为显式 `UTF-8`
  - 避免 Windows 环境下中文/Unicode skill 出现假失败

## 外部经验映射

本轮主要吸收了以下公开最佳实践方向：

- OpenAI：
  - 指令前置
  - 输出格式明确
  - 结构化输出与校验
- Anthropic：
  - 先定义 success criteria
  - context engineering，减少无关上下文
- Google：
  - prompt 需要测试与迭代
  - 路由、评估、收敛要明确
- Microsoft：
  - 要具体
  - 要写清楚 when unsure 的策略

## 当前残留差异

本轮开始时 `.agents/skills` 一度表现为只读，但后续已完成实际同步，因此 wrapper 与 canonical 的主要差异已经消除。

当前残留风险主要变成：

1. 如果未来再次大改 `.claude/.../AGENTS.md`，需要同步检查 wrapper 描述是否仍然一致
2. 若继续扩充 references/scripts，最好把新增入口导航也同步回 wrapper

## 本轮验证

- `python .claude/embedded-feature-planner/scripts/validate_planning_artifacts.py --workspace skill-iterations-test/embedded-feature-planner-fixture`
  - 通过
- `python .claude/expert-prompt-generator/scripts/validate_prompt_output.py --describe-file skill-iterations-test/expert-prompt-generator-fixture/describe_prompt.md`
  - 通过
- `python -m py_compile ...`
  - 通过
- `python C:/Users/maitekai/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/embedded-feature-planner`
  - 通过
- `python C:/Users/maitekai/.codex/skills/.system/skill-creator/scripts/quick_validate.py .agents/skills/expert-prompt-generator`
  - 通过
- `quick_validate.py` 只读语法解析
  - 通过

## 后续联动

随着 `.claude/embedded_ai_roles` 的继续迭代，`embedded-feature-planner` 现已额外接入：

- `role-examples.md`
- `validate_rule_docs.py`
- `assemble_role_output.py`
- `task-playbooks.md`
- `role-review-checklist.md`

这让 skill 入口除了能规划和校验产物，也能更稳定地组织多角色输出。

## 持续增强

当前 `.claude` 体系又进一步接入了：

- `select_roles.py`
- `validate_reference_links.py`
- `route_task.py`
- `validate_playbooks.py`

这意味着 planner 现在不仅能“引用”多角色体系，还能：

- 先自动建议最少必要角色集
- 自动检查关键引用是否断链
- 自动输出任务路由包
- 自动验证 playbook 结构与场景覆盖

## 新一轮迭代：任务包中间层与可靠性补丁

这轮继续优化把“能路由任务”升级成“能生成开工任务包”，并补齐了 Windows 下中文 JSON fixture 的稳定性问题。

### 新增能力

- 新增 `.claude/embedded_ai_roles/scripts/task_routing_core.py`
  - 把 `mode`、`scenario`、`roles` 的判断抽成共享核心
  - 避免 `select_roles.py`、`route_task.py`、后续自动化各自漂移
- 新增 `.claude/embedded_ai_roles/scripts/generate_task_packet.py`
  - 生成 `task-packet.json`
  - 输出：
    - `mode`
    - `scenario`
    - `playbook_section`
    - `roles`
    - `initial_checks`
    - `evidence_targets`
    - `acceptance_checks`
    - `handoff_fields`
- 新增 `.claude/embedded_ai_roles/scripts/validate_task_packet.py`
  - 校验任务包结构、角色路径、本地 playbook 路径和产物模板契约

### 主流程接入

- `embedded-feature-planner/AGENTS.md` 现已明确：
  1. 先生成 `task-packet`
  2. 再按任务包读取最少必要角色
  3. 再执行对应 playbook
  4. 最后输出 `方案.md`、`Todo.md`、`debug.json`
- `workflow-and-outputs.md` 新增 `task-packet.json` 契约
- wrapper `SKILL.md` 与 `agents/openai.yaml` 已同步强调“先生成任务包”

### 角色与参考补强

- `role-output-contracts.md`
  - 新增 `task-packet.json` 作为中间交付物
  - 新增多角色交接最低字段
- `role-review-checklist.md`
  - 新增“是否可回填 task-packet 交接字段”的检查项
- `role-examples.md`
  - 新增交接好例子 / 坏例子
- 重点补强角色：
  - `01_product_manager.md`
  - `02_system_architect.md`
  - `08_test_engineer.md`
  - `09_devops_engineer.md`
  - `10_project_manager.md`
  - 明确它们如何回填 `task-packet.json`，减少角色之间交接断层

### 可靠性修复

- 修复 `skill-iterations-test/task-routing-fixture/check_task_routes.py`
- 修复 `skill-iterations-test/task-packet-fixture/check_task_packets.py`
  - 统一对子进程设置 `PYTHONIOENCODING=utf-8`
  - 解决 Windows 下中文 JSON fixture 在 `subprocess.run(..., encoding="utf-8")` 场景中偶发解码失败的问题

### 外部经验映射增强

本轮继续把头部厂商公开经验落成工程规则，而不只停留在报告描述：

- OpenAI / Microsoft：
  - 明确输出契约
  - 明确 when unsure 策略
- Anthropic：
  - success criteria 前置
  - 主文件短、细节按需加载
- Google：
  - 先路由、再执行、再验证
  - 用 fixture 和校验器维持迭代稳定性

### 本轮验证

- `python -m py_compile ...`
  - 通过
- `python .claude/embedded_ai_roles/scripts/validate_role_docs.py`
  - 通过
- `python .claude/embedded_ai_roles/scripts/validate_rule_docs.py`
  - 通过
- `python .claude/embedded_ai_roles/scripts/validate_reference_links.py`
  - 通过
- `python .claude/embedded_ai_roles/scripts/validate_playbooks.py`
  - 通过
- `python .claude/embedded_ai_roles/scripts/validate_task_packet.py --task "处理发布前回归不过和交付物不齐的问题"`
  - 通过
- `python skill-iterations-test/task-routing-fixture/check_task_routes.py`
  - 通过
- `python skill-iterations-test/task-packet-fixture/check_task_packets.py`
  - 通过
- `python .claude/embedded-feature-planner/scripts/validate_planning_artifacts.py --workspace skill-iterations-test/embedded-feature-planner-fixture`
  - 通过
- `python .claude/expert-prompt-generator/scripts/validate_prompt_output.py --describe-file skill-iterations-test/expert-prompt-generator-fixture/describe_prompt.md`
  - 通过

## 新一轮迭代：默认关闭的模型路由

这轮继续优化新增了“模型路由”能力，但严格保持默认关闭，只有在用户明确要求时才启用。

### 设计目标

- 支持“不同功能使用不同模型”
- 默认不启用，不做隐式模型选择
- 启用后必须结构化记录、可校验、可追踪

### 新增内容

- 新增参考：
  - `.claude/embedded_ai_roles/references/model-routing-policy.md`
- 新增配置模板：
  - `.claude/embedded_ai_roles/assets/model-routing-template.json`
- 新增脚本：
  - `.claude/embedded_ai_roles/scripts/model_routing_core.py`
  - `.claude/embedded_ai_roles/scripts/resolve_model_routing.py`
  - `.claude/embedded_ai_roles/scripts/validate_model_routing_config.py`

### 主流程接入

- `generate_task_packet.py`
  - 新增 `model_routing` 字段
- `validate_task_packet.py`
  - 新增对 `model_routing` 的结构校验
- `embedded-feature-planner/AGENTS.md`
  - 明确只有在用户显式要求时才允许 `--enable-model-routing`
- `expert-prompt-generator/AGENTS.md`
  - 同步接入默认关闭的模型路由说明

### 行为约束

- 默认调用：
  - `model_routing.enabled = false`
  - `source = default_off`
- 显式启用：
  - 需要 `--enable-model-routing`
  - 可配合 `--routing-config`
- 无效配置：
  - 不报喜不报忧地启用
  - 保持关闭并返回结构化警告

### 新增 fixture

- `skill-iterations-test/model-routing-fixture/expected-routing-states.json`
- `skill-iterations-test/model-routing-fixture/invalid-model-routing-config.json`
- `skill-iterations-test/model-routing-fixture/check_model_routing.py`

覆盖场景：

1. 默认关闭
2. 嵌入式任务显式启用
3. prompt 生成任务显式启用
4. 无效配置应失败

### 本轮验证

- `python -m py_compile ...`
  - 通过
- `python .claude/embedded_ai_roles/scripts/validate_model_routing_config.py --config .claude/embedded_ai_roles/assets/model-routing-template.json`
  - 通过
- `python .claude/embedded_ai_roles/scripts/resolve_model_routing.py --skill embedded-feature-planner --task "..." --json`
  - 默认关闭，符合预期
- `python .claude/embedded_ai_roles/scripts/resolve_model_routing.py --skill embedded-feature-planner --task "..." --enable-model-routing --routing-config .claude/embedded_ai_roles/assets/model-routing-template.json --json`
  - 显式启用，符合预期
- `python skill-iterations-test/model-routing-fixture/check_model_routing.py`
  - 通过
- `python skill-iterations-test/task-packet-fixture/check_task_packets.py`
  - 通过

## 新一轮迭代：总览报告与状态索引

这轮继续优化主要解决“信息已经很多，但新接手的人上手仍然慢”的问题。

### 新增内容

- 新增仓库根目录总览：
  - `优化报告.md`
- 新增轻量索引：
  - `skill-iterations-test/current-state-index.md`

### 新增价值

- 把长对话和多轮迭代结果压缩成一份可快速阅读的总览
- 给出 canonical 入口、核心脚本、fixture、验证器和下一步建议
- 后续继续优化时，先看 `优化报告.md` 就能快速进入状态
