# Workflow And Outputs

## 工程分类

### 新工程

满足以下任一条件，可视为新工程：

- 目录为空
- 只有少量非源码文件
- 没有 `.c` / `.cpp` / `.h` / `CMakeLists.txt` / `Makefile` / 工程脚本

### 已有工程

存在源码、构建文件、配置文件或项目脚本时，视为已有工程。

## topStruct.md 生成规则

只在以下条件同时满足时生成：

1. 当前是已有工程
2. 用户要做新功能接入、复杂调试或架构梳理
3. 根目录还没有 `topStruct.md`

生成内容至少包含：

- 模块划分
- 模块关系
- 关键调用链
- 关键接口输入/输出
- 硬件与存储结构

## 输出契约

### `task-packet.json`

这是规划或调试启动前的中间任务包，用来把“如何开工”先结构化下来。推荐由：

```bash
python .claude/embedded_ai_roles/scripts/generate_task_packet.py --task "<用户任务描述>" --output task-packet.json
```

最低包含：

- `schema_version`
- `task`
- `mode`
- `scenario`
- `model_routing`
- `playbook`
- `playbook_section`
- `roles`
- `initial_checks`
- `evidence_targets`
- `acceptance_checks`
- `handoff_fields`

要求：

- `roles` 至少包含角色 id、角色文件路径和关注点
- `model_routing.enabled` 默认必须为 `false`，除非用户明确要求启用
- `initial_checks` 必须能指导“先做什么”
- `acceptance_checks` 必须能指导“做到什么算收口”
- `handoff_fields` 必须能指导多角色之间如何交接

`task-packet.json` 是中间契约，不替代 `方案.md`、`Todo.md`、`debug.json`。

### `方案.md`

最低结构：

```markdown
# 方案：[功能名称]

## 目标与范围
## 现状与证据
## 实现方案
## 接口与影响面
## 风险与待确认
## 验收标准
```

要求：

- `现状与证据` 中至少列出关键证据文件或日志来源
- `风险与待确认` 中必须列出 `pending` 项
- `验收标准` 尽量量化

### `Todo.md`

最低结构：

```markdown
# Todo：[功能名称]

## 里程碑
## 任务列表
## 验收与回归
## 风险跟踪
```

要求：

- `任务列表` 中的每个任务都要有产物、完成定义或验证方式
- 修复类任务要包含回归动作

### `debug.json`

最低结构：

```json
{
  "feature": "[功能名称]",
  "created_at": "[ISO 时间]",
  "mode": "planning|implementation|debug",
  "requirement": {
    "input": "[用户原始需求]",
    "clarifications": []
  },
  "evidence": [],
  "decisions": [],
  "debug_log": [],
  "status": "planning|implementation|blocked|done"
}
```

要求：

- `evidence` 保存确认事实与缺口
- `decisions` 保存关键技术取舍
- `debug_log` 保存本轮问题、修复与验证结果

## 推荐执行顺序

1. 判断工程类型
2. 生成或更新 `task-packet.json`
3. 判断是 `planning` / `implementation` / `debug`
4. 如需结构梳理，先补 `topStruct.md`
5. 再生成或更新 `方案.md`
6. 再生成或更新 `Todo.md`
7. 同步维护 `debug.json`
8. 最后运行校验脚本
