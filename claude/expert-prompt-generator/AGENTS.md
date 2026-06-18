---
name: expert-prompt-generator
description: 根据用户需求生成精简、专家级、可复用的 AI prompt，并追加写入当前工作目录的 describe_prompt.md。适用于 prompt 生成、角色设计、提示词优化、describe_prompt.md 维护，以及把模糊请求收敛为结构化高质量 prompt 的场景。
---

# Expert Prompt Generator

用这个工作流把用户的自然语言需求压缩成高质量 prompt，并把结果持续沉淀到 workspace 根目录的 `describe_prompt.md`。

## 成功标准

生成的 prompt 必须同时满足：

1. 角色明确，不使用泛化身份，例如“你是一个 AI 助手”。
2. 任务、约束、输出结构齐全，默认控制在 4 行内。
3. 对需求做必要收敛，但不擅自添加强假设或虚构背景。
4. 追加记录格式稳定，可长期维护，不破坏已有 `describe_prompt.md`。
5. 最终内容通过本地校验脚本；如果无法运行脚本，则按同样规则手工检查。

## 先读哪些文件

1. 始终先读 `references/official-design-principles.md`。
2. 识别领域和子领域时，读 `references/domain-routing.md`。
3. 生成前后做质量核查时，读 `references/prompt-quality-rubric.md`。
4. 只有当用户明确要求“不同功能使用不同模型”或“启用模型路由”时，才读取 `.claude/embedded_ai_roles/references/model-routing-policy.md`。

## 执行顺序

### 1. 解析需求

先提炼四个槽位：

- `领域`
- `任务`
- `关键约束`
- `输出形式`

默认少问问题；只有当需求几乎没有信息量时，最多反问 1 个聚焦问题。

### 2. 路由模式

按 `references/domain-routing.md` 判断：

- `嵌入式模式`
- `通用模式`

如果命中了嵌入式关键词，再继续判断更细子领域，例如 BSP、驱动、系统服务、AI 应用、测试。

模型路由默认关闭。若用户明确启用，才允许使用：

```bash
python .claude/embedded_ai_roles/scripts/resolve_model_routing.py --skill expert-prompt-generator --task "<用户需求>" --enable-model-routing --routing-config ".claude/embedded_ai_roles/assets/model-routing-template.json" --json
```

### 3. 组装四行 prompt

默认使用固定四行骨架：

1. 角色与背景
2. 任务
3. 约束
4. 输出

如果用户约束极少，也不要删掉这四个槽位，改用简洁默认值补齐。

### 4. 维护 describe_prompt.md

写入规则：

- 目标文件固定为 workspace 根目录的 `describe_prompt.md`
- 若文件不存在，先写文件头
- 若文件已存在，只允许追加，不允许覆盖整份文件
- 若发现 `discribe_prompt.md`，不要静默迁移；说明风险后仍默认写正确拼写的文件

每次追加一节，格式固定为：

````markdown
## [YYYY-MM-DD HH:mm] - [一句话主题]

**原始需求**：
> [用户原话]

**模式**：通用 | 嵌入式

**生成 Prompt**：
```
[四行 prompt]
```

---
````

文件头仅首次创建时写入：

```markdown
# Prompt 库

> 由 expert-prompt-generator 自动追加维护。
```

### 5. 做最终校验

优先运行：

```bash
python .claude/expert-prompt-generator/scripts/validate_prompt_output.py --describe-file describe_prompt.md
```

如果暂时不方便运行脚本，手工检查：

- 是否只有 1 个角色行、1 个任务行、1 个约束行、1 个输出行
- 是否没有泛化角色
- 是否没有超过 4 行
- `describe_prompt.md` 是否为追加而非覆盖

## 不确定时怎么做

1. 需求过短时，最多追问 1 个核心问题。
2. 其余信息用保守默认值补齐，例如输出默认 `Markdown`。
3. 如果用户想要“详细版”，再在四行 prompt 之外补充扩展要求；默认先交付精简版。

## 禁止事项

不要做以下事情：

- 直接输出“你是一个 AI 助手”
- 把提示词扩成冗长说明文
- 静默覆盖 `describe_prompt.md`
- 因为需求模糊就停止推进
- 虚构技术栈、版本或行业背景
