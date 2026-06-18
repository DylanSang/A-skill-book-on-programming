---
name: embedded-feature-planner
description: 嵌入式需求规划与工程修复工作流。用于新功能规划、已有工程功能接入、结构梳理、方案/Todo/debug.json 生成，以及 bug 修复时的证据化分析与闭环执行。Use when the user asks for 新功能规划、方案设计、Todo 拆解、topStruct 分析、嵌入式工程结构梳理，or asks to 修复bug/排查报错/解决编译与运行问题 in an embedded project.
---

# Embedded Feature Planner

用这个工作流在当前 workspace 中完成嵌入式需求规划、工程分析和修复闭环。默认输出写到当前工作目录根目录，而不是 skill 目录。

## 成功标准

在开始写方案、Todo、代码建议或修复结论前，先确保以下目标成立：

1. 所有版本、接口、DTS、Kconfig、脚本参数和路径都基于当前仓库或用户提供证据，不凭记忆补全。
2. 结论区分 `已确认` 与 `待确认`，证据不足时明确标记 `pending`，不要把猜测写成事实。
3. 输出的 `方案.md`、`Todo.md`、`debug.json` 可直接交接、可追踪、可继续迭代。
4. 涉及实现或修复时，必须形成“定位 -> 修改 -> 验证 -> 记录”的闭环，而不是只给建议。
5. 最终产物通过本地校验脚本；如果无法运行脚本，按同样检查项手工核对。

## 先读哪些文件

按需加载，避免一次把所有大文件都塞进上下文。

1. 始终先读 `references/official-design-principles.md`，理解本 skill 的设计原则。
2. 始终再读 `references/evidence-and-safety.md`，执行证据门禁、Git 约束和不确定性策略。
3. 遇到规划、结构分析、topStruct、方案/Todo/debug.json 生成时，读 `references/workflow-and-outputs.md`。
4. 处理任何嵌入式多角色协作任务前，优先读取以下共享参考，而不是直接全量加载 10 个角色文件：
   - `.claude/embedded_ai_roles/references/shared-foundation.md`
   - `.claude/embedded_ai_roles/references/role-output-contracts.md`
   - `.claude/embedded_ai_roles/references/role-routing-and-selection.md`
   - `.claude/embedded_ai_roles/references/role-examples.md`
   - `.claude/embedded_ai_roles/references/role-review-checklist.md`
   - `.claude/embedded_ai_roles/references/task-playbooks.md`
   - `.claude/embedded_ai_roles/references/model-routing-policy.md`
5. 涉及代码、构建、调试、交付时，再按场景读取：
   - `.claude/embedded_ai_roles/rules/rv1126-safety-guard.mdc`
   - `.claude/embedded_ai_roles/rules/rv1126-debug-workflow.mdc`
   - `.claude/embedded_ai_roles/rules/rv1126-code-generation.mdc`
   - `.claude/embedded_ai_roles/rules/rv1126-compilation.mdc`
   - `.claude/embedded_ai_roles/rules/rv1126-module-handover.mdc`
6. 只有在确实需要某个角色视角时，才读取对应角色文件：
   - 产品/范围不清 -> `01_product_manager.md`
   - 架构和模块边界 -> `02_system_architect.md`
   - 硬件约束 -> `03_hardware_engineer.md`
   - BSP/驱动/内核链路 -> `04_bsp_engineer.md` / `05_driver_engineer.md`
   - 系统集成与工程化 -> `06_system_engineer.md` / `09_devops_engineer.md`
   - 应用逻辑 -> `07_application_engineer.md`
   - 测试、风险、回归 -> `08_test_engineer.md`
   - 里程碑、交付、优先级 -> `10_project_manager.md`

## 执行顺序

### 1. 识别任务模式

先把当前请求归类成以下之一：

- `planning`: 新功能规划、方案设计、Todo 拆解、topStruct 梳理
- `implementation`: 在已有规划基础上开始实现
- `debug`: 修复 bug、编译失败、运行异常、接口不通

如果用户同时提到“新功能 + 报错”，先做 `debug` 消除阻塞，再补齐 `planning` 产物。

识别完模式后，优先从 `.claude/embedded_ai_roles/references/task-playbooks.md` 读取对应场景的最小步骤、证据清单和常见误判。

如果用户明确要求“不同功能使用不同模型”或“启用模型路由”，再读取 `.claude/embedded_ai_roles/references/model-routing-policy.md`，否则保持模型路由关闭。

需要先得到稳定的开工任务包时，优先运行：

```bash
python .claude/embedded_ai_roles/scripts/generate_task_packet.py --task "<用户任务描述>" --json
python .claude/embedded_ai_roles/scripts/validate_task_packet.py --task "<用户任务描述>"
```

只有在用户明确启用模型路由时，才允许这样运行：

```bash
python .claude/embedded_ai_roles/scripts/generate_task_packet.py --task "<用户任务描述>" --enable-model-routing --routing-config ".claude/embedded_ai_roles/assets/model-routing-template.json" --output task-packet.json
python .claude/embedded_ai_roles/scripts/validate_model_routing_config.py --config ".claude/embedded_ai_roles/assets/model-routing-template.json"
```

需要快速建议角色集合或只看路由结果时，可再运行：

```bash
python .claude/embedded_ai_roles/scripts/select_roles.py --task "<用户任务描述>"
python .claude/embedded_ai_roles/scripts/route_task.py --task "<用户任务描述>" --json
```

默认顺序是：

1. 先生成 `task-packet`
2. 再按 `task-packet.roles` 读取最少必要角色
3. 如显式启用了模型路由，再按 `task-packet.model_routing` 选择功能对应模型
4. 再按 `task-packet.playbook_section` 执行对应 playbook
5. 最后写 `方案.md`、`Todo.md`、`debug.json`

### 2. 检查工程与版本管理状态

先确认：

- 当前工作目录是否为空、新工程还是已有工程
- 是否存在 `.git`
- 是否已有 `topStruct.md`
- 是否已有 `方案.md`、`Todo.md`、`debug.json`

如果不是 Git repository，初始化版本管理并补 `.gitignore`。如果已有用户未提交改动，继续工作但不要覆盖或回滚。

### 3. 采证后再分析

只要要写到以下内容，就必须先采证：

- 内核、SDK、芯片、板型、工具链版本
- DTS 属性、compatible、Kconfig、Makefile、脚本参数
- proc/sysfs/debugfs 节点
- MQTT topic、JSON 字段、分区名、镜像名

采证来源优先级见 `references/evidence-and-safety.md`。如果本地仓库没有证据，写成 `待确认` 或 `需实现`。

### 4. 选择最少必要角色视角

不要机械读取全部 10 个角色文件。优先按照 `.claude/embedded_ai_roles/references/role-routing-and-selection.md` 选择最少必要集合。常见模式如下：

- 纯规划最少集：产品、架构、测试、项目管理
- 涉及硬件接口：加硬件工程师
- 涉及内核/BSP/驱动：加 BSP、驱动、系统工程师
- 涉及构建/部署：加 DevOps
- 涉及应用协议或 AI 业务：加应用工程师

### 5. 生成或更新产物

默认在 workspace 根目录维护以下文件：

- `topStruct.md`
  - 仅在已有工程且缺少结构梳理时生成
- `方案.md`
- `Todo.md`
- `debug.json`

具体格式、字段和最低验收见 `references/workflow-and-outputs.md`。

如果一次任务需要汇总多个角色视角，优先使用：

```bash
python .claude/embedded_ai_roles/scripts/assemble_role_output.py <role-output-1.md> <role-output-2.md> --output role-summary.md
```

如果任务还没有稳定开工材料，可先把任务包落到 workspace 根目录：

```bash
python .claude/embedded_ai_roles/scripts/generate_task_packet.py --task "<用户任务描述>" --output task-packet.json
```

`task-packet.json` 不是最终交付物，但它是主流程的中间契约，至少应包含：

- 模式
- 场景
- 模型路由状态
- playbook 章节
- 最少必要角色集合
- 初始检查项
- 证据目标
- 验收检查项
- 交接字段

### 6. 修复类任务必须闭环

当用户意图包含 `修复bug`、`解决问题`、`处理报错`、`编译失败`、`链接失败`、`无法运行` 时，自动进入彻底修复模式：

1. 执行全局链路排查，而不是只盯单一报错点。
2. 至少检查一个上游和一个下游文件。
3. 同步检查构建脚本、配置文件、bootstrap 脚本和 debug 记录。
4. 修改后重跑验证，再把根因和修复写入 `debug.json.debug_log`。

### 7. 做最终校验

优先运行：

```bash
python .claude/embedded-feature-planner/scripts/validate_planning_artifacts.py --workspace .
python .claude/embedded_ai_roles/scripts/validate_role_docs.py
python .claude/embedded_ai_roles/scripts/validate_rule_docs.py
python .claude/embedded_ai_roles/scripts/validate_reference_links.py
python .claude/embedded_ai_roles/scripts/validate_playbooks.py
python .claude/embedded_ai_roles/scripts/validate_task_packet.py --packet task-packet.json
python .claude/embedded_ai_roles/scripts/validate_model_routing_config.py --config ".claude/embedded_ai_roles/assets/model-routing-template.json"
```

如果环境里没有可用 Python，则按脚本同等规则手工检查：

- `方案.md` 是否包含必需章节
- `Todo.md` 是否包含里程碑、任务、回归与风险
- `debug.json` 是否是合法 JSON，且字段完整
- `task-packet.json` 是否包含角色、playbook、模型路由状态、初始检查项和验收检查项
- 所有 `pending` 项是否有补证据动作

## 不确定时怎么做

遵守以下策略：

1. 缺少核心业务目标时，最多提 1 个聚焦问题；其余用清晰假设继续推进。
2. 缺少仓库证据时，不补脑，直接标记 `pending`。
3. 两种方案都可行但影响差异明显时，先给对比，再推荐一个默认方案。
4. 如果规则文件与当前实现策略冲突，先对齐实现逻辑，再调整门禁，不要让门禁误拦截。
5. 如果用户没有明确要求启用模型路由，保持 `disabled`，不要擅自挑选不同模型。

## 禁止事项

不要做以下事情：

- 凭记忆编造版本、接口、节点、参数、构建命令
- 把“建议新增”写成“当前已支持”
- 只生成文档，不落调试闭环
- 只修当前报错，不检查构建链、配置链、脚本链和记录链
- 把终端日志直接粘在 `debug.json` 外部导致 JSON 失效
