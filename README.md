# Project-Ready AI Workflow Pack

把 `.claude` 和 `.agents` 直接放进你的工程目录，让 `Claude Code`、`Codex`、`Cursor` 不再“自由发挥”，而是按一套可路由、可校验、可交接的稳定工作流真正干活。

这不是一堆提示词模板。
这是一套已经被拆成 canonical workflow、role system、task packet、validation chain 的项目内 AI 工作流骨架。

## 为什么这套东西会让人上头

- 不靠运气问 AI，而是先走主流程，再出产物
- 不默认全量加载角色，而是先选最少必要角色
- 不让模型路由偷偷生效，而是默认关闭、显式启用
- 不只会“给建议”，还能产出 `task-packet.json`、`方案.md`、`Todo.md`、`debug.json`、`describe_prompt.md`
- 不只写文档，还自带校验器、fixture 和状态索引

如果你也受够了：

- AI 一会儿像架构师，一会儿像瞎猜机器
- 每个会话都要重新解释项目规范
- 做了半天没有中间契约，也没有交接材料
- prompt 很长，但没有稳定结果

这套仓库就是为这些问题准备的。

## 你会得到什么

仓库核心分成三层：

- `.claude`
  - 真正的 canonical workflow、references、rules、scripts、模板
- `.agents`
  - skill wrapper 与 UI metadata，让工具更容易触发正确入口
- `skill-iterations-test`
  - fixture、验证样例、状态索引、阶段性报告

当前已经稳定的两个核心能力：

1. `embedded-feature-planner`
   用于嵌入式规划、工程接入、Bug 修复、编译失败、运行异常排查
2. `expert-prompt-generator`
   用于高质量 prompt 生成、角色设计、提示词优化、`describe_prompt.md` 维护

## 它和普通 prompt 仓库的区别

普通 prompt 仓库通常只有：

- 一些长提示词
- 一些角色模板
- 一些“建议”

这套仓库已经进化成更像工作流引擎的结构：

- 有 canonical 主流程
- 有按需加载的 references
- 有最少必要角色路由
- 有 task packet 中间契约
- 有默认关闭的模型路由
- 有 wrapper 漂移校验
- 有最近一次产物摘要索引

一句话说，它已经不是“让 AI 看起来更聪明”，而是“让 AI 更像一个能交付结果的项目成员”。

## 最推荐的用法

把下面这些内容直接放进你的真实工程根目录：

```text
your-project/
├── .claude/
├── .agents/
├── CLAUDE.md
├── src/ 或你的业务代码
└── 其他工程目录
```

想保留完整导航和验证样例时，再加上：

```text
优化报告.md
skill-iterations-test/
```

然后进入工程目录，直接开始用。

## 真正的入口顺序

放进工程后，优先级是这样的：

1. `CLAUDE.md`
2. `.claude/embedded-feature-planner/AGENTS.md`
3. `.claude/expert-prompt-generator/AGENTS.md`
4. `.claude/.../references/*`
5. `.claude/.../scripts/*`
6. `.agents/skills/*/SKILL.md`

核心原则只有一句：

`.claude` 是执行真源，`.agents` 是轻量触发器。

## 三种工具怎么直接开工

### Claude Code

```text
请先遵循项目根目录的 CLAUDE.md。
然后阅读 .claude/embedded-feature-planner/AGENTS.md。
按 embedded-feature-planner 工作流处理当前工程任务。
默认关闭模型路由，除非我明确要求启用。
如果是复杂嵌入式任务，先生成 task-packet.json，再继续输出正式产物。
```

### Codex

```text
Use $embedded-feature-planner for this project task.
First follow the repository CLAUDE.md and then read .claude/embedded-feature-planner/AGENTS.md.
Keep model routing disabled unless I explicitly enable it.
Generate task-packet.json first, then continue with the project artifacts.
```

### Cursor

```text
先遵循项目根目录 CLAUDE.md。
再阅读 .claude/embedded-feature-planner/AGENTS.md。
按该工作流处理当前工程任务。
默认关闭模型路由。
先生成 task-packet.json，再执行后续步骤。
```

Prompt 任务也同理，把入口换成：

- `.claude/expert-prompt-generator/AGENTS.md`
- 输出追加到 `describe_prompt.md`

## 最能打的几个能力

### 1. 任务先路由，再执行

先用脚本判断这是：

- `planning`
- `implementation`
- `debug`

再把任务路由到具体场景，例如：

- 新功能规划
- 编译失败 / 链接失败
- DTS / 驱动不生效
- 运行时异常 / 服务不稳定
- 发布阻塞 / 交付前收口

### 2. 先生成 task packet，再让角色接棒

`task-packet.json` 不是装饰文件，它是这套体系的中间契约。

它会明确：

- mode
- scenario
- playbook section
- roles
- evidence targets
- acceptance checks
- handoff fields

这让多角色协作、调试闭环、文档交接都开始变得可靠。

### 3. 模型路由默认关闭

很多项目一上来就搞“不同功能用不同模型”，最后变成复杂度爆炸。

这套体系默认反着来：

- 默认 `disabled`
- 只有用户明确要求时才启用
- 启用后必须结构化记录
- 错误配置不会偷偷生效

所以它更适合实际项目，而不是 demo。

### 4. 不只生成内容，还会自检

仓库内已经带了验证链：

- `validate_skill_wrappers.py`
- `validate_task_packet.py`
- `validate_model_routing_config.py`
- `validate_planning_artifacts.py`
- `validate_prompt_output.py`
- `validate_role_docs.py`
- `validate_rule_docs.py`
- `validate_reference_links.py`
- `validate_playbooks.py`

它不是“写完就算”，而是“写完还要过检查”。

## 常用命令

### 看任务应该怎么走

```bash
python .claude/embedded_ai_roles/scripts/route_task.py --task "<任务描述>" --json
```

### 看最少必要角色

```bash
python .claude/embedded_ai_roles/scripts/select_roles.py --task "<任务描述>"
```

### 生成开工任务包

```bash
python .claude/embedded_ai_roles/scripts/generate_task_packet.py --task "<任务描述>" --output task-packet.json
```

### 校验任务包

```bash
python .claude/embedded_ai_roles/scripts/validate_task_packet.py --packet task-packet.json
```

### 校验模型路由配置

```bash
python .claude/embedded_ai_roles/scripts/validate_model_routing_config.py --config ".claude/embedded_ai_roles/assets/model-routing-template.json"
```

### 看当前状态快照

```bash
python .claude/embedded_ai_roles/scripts/generate_current_state_index.py --check skill-iterations-test/current-state-index.md
```

## 当前状态

已经稳定：

- canonical 主流程
- references 按需加载
- 最少必要角色路由
- task packet 生成与校验
- prompt 四行契约
- 默认关闭的模型路由
- wrapper 漂移校验
- 最近一次产物摘要索引

仍是占位：

- 模型路由模板中的 `model_id`
- 真实 Git 工程中的完整演练
- 多次真实任务的连续历史索引

## 从哪里开始看

如果你想快速理解全貌，按这个顺序：

1. [使用说明.md](/E:/AI/skill%20V3/%E4%BD%BF%E7%94%A8%E8%AF%B4%E6%98%8E.md:1)
2. [使用示例.md](/E:/AI/skill%20V3/%E4%BD%BF%E7%94%A8%E7%A4%BA%E4%BE%8B.md:1)
3. [优化报告.md](/E:/AI/skill%20V3/%E4%BC%98%E5%8C%96%E6%8A%A5%E5%91%8A.md:1)
4. [CLAUDE.md](/E:/AI/skill%20V3/CLAUDE.md:1)
5. [current-state-index.md](/E:/AI/skill%20V3/skill-iterations-test/current-state-index.md:1)

## 最后一句

如果你想要的不是“一个会聊天的 AI”，而是“一个进了工程目录就知道先读什么、先产什么、怎么校验、怎么交接的 AI 工作流底座”，这套仓库就是现成答案。
