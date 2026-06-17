# Claude Roles Iteration Report

## 范围

本轮针对 `.claude` 目录进行了 5 轮自动迭代，覆盖：

- `.claude/embedded-feature-planner/AGENTS.md`
- `.claude/embedded_ai_roles/embedded_ai_roles/*.md`
- `.claude/embedded_ai_roles/rules/*.mdc`
- `.claude/embedded_ai_roles/references/*`
- `.claude/embedded_ai_roles/scripts/validate_role_docs.py`

同时处理了 `.claude` 下文件可读可写的持续迭代前提。

## 第 1 轮：权限与共享基础设施

- 规范化 `.claude` 目录的只读属性
- 新建共享参考目录和脚本目录
- 新增：
  - `references/shared-foundation.md`
  - `references/role-output-contracts.md`
  - `references/role-routing-and-selection.md`
  - `scripts/validate_role_docs.py`

目标：

- 让角色共享规则不再分散复制
- 让多角色工作流先走共享参考，再按需加载角色

## 第 2 轮：流程入口对齐

- 更新 `.claude/embedded-feature-planner/AGENTS.md`
- 显式要求优先读取共享参考文件
- 明确“最少必要角色集”原则
- 把角色文档校验器纳入最终校验步骤

目标：

- 降低上下文噪声
- 减少默认全量加载 10 个角色造成的幻觉和漂移

## 第 3 轮：角色瘦身与收敛

重写了全部 10 个角色文件，使其从“强模板 + 强平台假设”转为“共享规则 + 差异化职责”：

- `01_product_manager.md`
- `02_system_architect.md`
- `03_hardware_engineer.md`
- `04_bsp_engineer.md`
- `05_driver_engineer.md`
- `06_system_engineer.md`
- `07_application_engineer.md`
- `08_test_engineer.md`
- `09_devops_engineer.md`
- `10_project_manager.md`

主要变化：

- 删除大段项目固定值、版本号、topic、工具链号的硬编码
- 每个角色统一采用：
  - 目标
  - 已确认事实
  - 分析与判断
  - 风险与待确认
  - 建议动作 / 交付物
- 明确每个角色：
  - 证据清单
  - 何时升级
  - 交付关注点
  - 常见失误

## 第 4 轮：规则文件去模板化

重写了以下规则文件：

- `rv1126-code-generation.mdc`
- `rv1126-compilation.mdc`
- `rv1126-debug-workflow.mdc`
- `rv1126-module-handover.mdc`

保留了安全禁区文件：

- `rv1126-safety-guard.mdc`

主要变化：

- 从“理想项目模板”改为“当前仓库友好型规则”
- 不再硬性要求：
  - 默认 adb
  - 默认 patch/commit
  - 默认 README
  - 默认固定模块目录结构
  - 默认固定编译器版本和内核版本
- 改为：
  - 先确认仓库事实
  - 先走最小闭环
  - 再决定生成方式和交付形态

## 第 5 轮：查漏补缺与验证

角色丰富化重点补了三类信息：

1. `证据清单`
2. `何时升级`
3. `交付关注点`

验证结果：

- `python .claude/embedded_ai_roles/scripts/validate_role_docs.py`
  - 通过
- `python -m py_compile ...`
  - 通过
- 角色文件平台硬编码扫描
  - 未发现 `Linux 5.10`、`localhost:1883`、固定工具链版本等残留

## 本轮实际改善

### 可靠性

- 角色不再把示例平台事实当成默认真值
- 流程先走证据门禁，再产出结论
- 规则文件不再和当前项目现实脱节

### 科学性

- 共享规则和角色输出契约被显式化
- 角色选择改为“最少必要集合”
- 各角色都有升级条件和证据要求

### 可维护性

- 公共约束集中在 `references/`
- 角色正文更短、更聚焦
- 后续改规则不必同时修改 10 个角色正文

## 后续建议

如果继续迭代，最有价值的下一步是：

1. 为每个角色补一个 `good example / bad example` 参考文件
2. 为 `embedded-feature-planner` 增加“角色输出汇总器”脚本
3. 把 `rules/` 中剩余的安全规则也做一次字段级验证器

## 继续迭代结果

本次继续迭代已经把上面的前三项全部落地：

- 新增 `references/role-examples.md`
- 新增 `scripts/assemble_role_output.py`
- 新增 `scripts/validate_rule_docs.py`
- 更新 `embedded-feature-planner/AGENTS.md`，把新参考和新校验器接入主流程

### 新增验证结果

- `python .claude/embedded_ai_roles/scripts/validate_rule_docs.py`
  - 通过
- `python .claude/embedded_ai_roles/scripts/assemble_role_output.py ...`
  - 通过
- 生成示例输出：
  - `skill-iterations-test/role-output-fixture/role-summary.md`

### 这轮新增价值

- 角色不只“会说要求”，现在还有好坏示例可对照
- 多角色分析不再需要手工拼接，可以脚本化汇总
- 规则文件也具备了基础漂移检查能力

## 进一步优化结果

本轮继续优化又补了两类关键能力：

### 1. 任务级 playbook

新增：

- `references/task-playbooks.md`
- `references/role-review-checklist.md`

覆盖了 5 类高频任务：

1. 新功能规划
2. 编译失败 / 链接失败
3. DTS / 驱动不生效
4. 运行时异常 / 服务不稳定
5. 发布阻塞 / 交付前收口

价值：

- 不再只依赖通用原则
- 面对真实任务时能直接套用稳定分解模板

### 2. 更严格的校验器

升级了：

- `validate_role_docs.py`
- `validate_rule_docs.py`

新增校验重点：

- 角色文件必须包含：
  - `证据清单`
  - `何时升级`
  - `交付关注点`
  - `常见失误`
  - `已确认事实`
  - `风险与待确认`
  - `建议动作 / 交付物`
- 规则文件必须体现“当前工程 / 当前仓库验证” mindset

### 3. 主流程接入

`embedded-feature-planner/AGENTS.md` 已接入：

- `task-playbooks.md`
- `role-review-checklist.md`

并明确要求按任务模式读取对应 playbook。

### 本轮验证

- `python .claude/embedded_ai_roles/scripts/validate_role_docs.py`
  - 通过
- `python .claude/embedded_ai_roles/scripts/validate_rule_docs.py`
  - 通过
- `python -m py_compile ...`
  - 通过

## 自动化增强结果

本轮继续优化把“人工判断”再收进了一层脚本：

### 新增脚本

- `scripts/select_roles.py`
- `scripts/validate_reference_links.py`

### 新增能力

1. 自动建议最少必要角色集合
   - 支持按任务描述自动路由
   - 已用 DTS / 编译失败 / 回归 / 发布检查混合任务做 fixture 验证

2. 校验 references / planner 中的本地路径引用是否断链
   - 防止后续继续迭代时 references 存在但主流程忘记更新

3. 主流程接入
   - `embedded-feature-planner/AGENTS.md` 已接入 `select_roles.py`
   - 最终校验步骤已接入 `validate_reference_links.py`

### 本轮验证

- `python .claude/embedded_ai_roles/scripts/select_roles.py --task "..."`
  - 通过
- `python .claude/embedded_ai_roles/scripts/validate_reference_links.py`
  - 通过
- 角色选择 fixture
  - 通过

### 新增价值

- 主流程现在不仅“知道怎么选角色”，而且“可以先自动给出角色建议”
- references、rules、planner 之间的断链风险降低
- `.claude` 体系开始具备更强的自解释、自校验和自路由能力

## 任务级自动化结果

本轮继续优化把 playbook 进一步做成了可测试的任务路由层。

### 新增脚本

- `scripts/route_task.py`
- `scripts/validate_playbooks.py`
- `skill-iterations-test/task-routing-fixture/check_task_routes.py`

### 新增 fixture

- `skill-iterations-test/task-routing-fixture/expected-routes.json`

覆盖场景：

1. 新功能规划
2. 编译 / 链接失败
3. DTS / 驱动不生效
4. 运行时异常 / 服务不稳定
5. 发布阻塞

### 新增能力

1. 从任务描述自动输出：
   - `mode`
   - `scenario`
   - `playbook`
   - `roles`
2. 校验 `task-playbooks.md` 是否维持完整结构
3. 用 fixture 批量验证路由结果是否符合预期

### 主流程接入

`embedded-feature-planner/AGENTS.md` 已接入：

- `route_task.py`
- `validate_playbooks.py`

### 本轮验证

- `python .claude/embedded_ai_roles/scripts/validate_playbooks.py`
  - 通过
- `python skill-iterations-test/task-routing-fixture/check_task_routes.py`
  - 通过
- `python .claude/embedded_ai_roles/scripts/route_task.py --task "..."`
  - 通过
- `python -m py_compile ...`
  - 通过

### 新增价值

- `.claude` 体系从“能给角色建议”进一步升级到“能输出任务路由包”
- playbook 不再只是静态说明，而是可被 fixture 验证
- 后续新增场景时，可以直接扩展 fixture 集而不是只改文档

## 继续优化结果：任务包层与交接补强

本轮继续迭代把“任务路由包”再往前推进成“任务执行包”，并进一步补强角色交接与 Windows 环境稳定性。

### 1. 新增共享路由核心

新增：

- `scripts/task_routing_core.py`

价值：

- `select_roles.py`
- `route_task.py`
- `generate_task_packet.py`

现在共享同一套路由逻辑，减少未来继续迭代时三处漂移。

### 2. 新增任务包生成与校验

新增：

- `scripts/generate_task_packet.py`
- `scripts/validate_task_packet.py`

任务包内容包括：

- `mode`
- `scenario`
- `playbook_section`
- `roles`
- `initial_checks`
- `evidence_targets`
- `acceptance_checks`
- `handoff_fields`

价值：

- 不再只有“这是哪个场景”的静态判断
- 现在还能直接给出“应该先做什么、看什么证据、交给谁、做到什么算过”

### 3. 主流程接入

更新：

- `.claude/embedded-feature-planner/AGENTS.md`
- `.claude/embedded-feature-planner/references/workflow-and-outputs.md`

新主流程顺序变成：

1. 先生成 `task-packet.json`
2. 按任务包读取最少必要角色
3. 按任务包中的 playbook section 执行
4. 最后产出 `方案.md`、`Todo.md`、`debug.json`

### 4. 角色查漏补缺

继续补强了以下角色：

- `01_product_manager.md`
- `02_system_architect.md`
- `08_test_engineer.md`
- `09_devops_engineer.md`
- `10_project_manager.md`

补强重点：

1. 角色如何回填 `task-packet.json`
2. 角色如何说明“谁接下一棒”
3. 角色如何把分析输出转成交接字段而不是散文

同时更新：

- `references/role-output-contracts.md`
- `references/role-review-checklist.md`
- `references/role-examples.md`

新增：

- 交接最低字段
- 交接好例子 / 坏例子
- 回填 `task-packet` 的复核项

### 5. 环境可靠性修复

修复：

- `skill-iterations-test/task-routing-fixture/check_task_routes.py`
- `skill-iterations-test/task-packet-fixture/check_task_packets.py`

问题：

- Windows 下中文 JSON 通过 `subprocess.run(..., encoding="utf-8")` 抓取时偶发解码失败

修复方式：

- 统一对子进程设置 `PYTHONIOENCODING=utf-8`

价值：

- fixture 结果不再受控制台默认编码波动影响
- 让“多角色 / 多脚本 / 中文任务”的验证更稳定

### 6. 新增 fixture

新增：

- `skill-iterations-test/task-packet-fixture/expected-task-packets.json`
- `skill-iterations-test/task-packet-fixture/check_task_packets.py`

覆盖场景：

1. 新功能规划
2. 编译 / 链接失败
3. DTS / 驱动不生效
4. 运行时异常 / 服务不稳定
5. 发布阻塞

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
- `python .claude/embedded_ai_roles/scripts/validate_task_packet.py --task "..."`
  - 通过
- `python skill-iterations-test/task-routing-fixture/check_task_routes.py`
  - 通过
- `python skill-iterations-test/task-packet-fixture/check_task_packets.py`
  - 通过

## 继续优化结果：显式启用的模型路由

本轮继续迭代把路由体系再向前推了一层，新增“模型路由”能力，但坚持默认关闭。

### 1. 新增模型路由策略与模板

新增：

- `references/model-routing-policy.md`
- `assets/model-routing-template.json`

核心约束：

1. 默认 `disabled`
2. 只有用户明确要求时才启用
3. 启用后必须记录：
   - 是否启用
   - 配置来源
   - 功能到模型的映射

### 2. 新增模型路由脚本

新增：

- `scripts/model_routing_core.py`
- `scripts/resolve_model_routing.py`
- `scripts/validate_model_routing_config.py`

价值：

- 把模型路由从文档建议变成可执行、可校验、可测试的能力
- 避免主流程直接硬编码具体模型名

### 3. 主流程接入

更新：

- `scripts/generate_task_packet.py`
- `scripts/validate_task_packet.py`
- `.claude/embedded-feature-planner/AGENTS.md`
- `.claude/expert-prompt-generator/AGENTS.md`

具体变化：

1. `task-packet.json` 新增 `model_routing`
2. 默认任务包中模型路由为关闭态
3. 只有显式 `--enable-model-routing` 才返回有效功能路由

### 4. 默认关闭的可靠性保障

这轮最重要的不是“能启用”，而是“不会误启用”。

新增保障包括：

- 配置文件必须 `default_enabled = false`
- `activation` 必须为 `explicit_opt_in_required`
- 无效配置不会偷偷启用，只会返回关闭态和警告
- fixture 明确覆盖默认关闭场景

### 5. 新增 fixture

新增：

- `skill-iterations-test/model-routing-fixture/expected-routing-states.json`
- `skill-iterations-test/model-routing-fixture/invalid-model-routing-config.json`
- `skill-iterations-test/model-routing-fixture/check_model_routing.py`

覆盖：

1. 默认关闭
2. planner 显式启用
3. prompt generator 显式启用
4. 非法配置验证失败

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

## 继续优化结果：总览报告与状态索引

本轮继续优化新增了两份面向“后续接手与继续迭代”的导航文件：

- 根目录：`优化报告.md`
- 测试目录：`current-state-index.md`

作用：

1. 把当前 `.claude` 体系已经具备的能力压缩成一份总览
2. 明确 canonical 入口、关键 references、脚本、fixture 和下一步建议
3. 避免后续继续迭代时重新从对话历史里恢复上下文
