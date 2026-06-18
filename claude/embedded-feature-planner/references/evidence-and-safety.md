# Evidence And Safety

## 证据优先级

当信息冲突时，按以下优先级决策：

1. 用户明确约束
2. 当前仓库源码、配置、绑定文档、构建脚本
3. 当前板卡日志或用户提供的实测现象
4. 芯片、内核、SDK 官方文档
5. 角色文件中的通用经验
6. 模型记忆

不要让低优先级信息覆盖高优先级事实。

## 版本与接口门禁

在写入 `方案.md`、`Todo.md`、代码建议或修复结论前，凡涉及以下内容都必须先核实：

- Linux / U-Boot / Buildroot / SDK / toolchain 版本
- 芯片型号、板型、DTS、defconfig
- DTS 属性与 compatible
- Kconfig 符号、Makefile 链路
- proc/sysfs/debugfs 节点
- 函数/API 名称
- 构建命令、脚本参数、分区名、镜像名
- MQTT topic 和 JSON 字段

如果仓库中找不到证据，写成：

- `待确认`
- `需实现`
- `自定义扩展`

不要写成“当前已支持”。

## Git 约束

1. 新工程第一次进入时，先检查是否存在 `.git`。
2. 若不存在，先 `git init`，再维护 `.gitignore`。
3. 不要回滚用户已有修改。
4. 每一轮规划、实现、调试后都检查工作区状态，确保改动可解释。

## debug.json 约束

`debug.json` 是事实源，而不是日志堆放区。

### `debug_log` 最小条目格式

```json
{
  "timestamp": "...",
  "module": "...",
  "issue": "...",
  "fix": "...",
  "result": "pass|fail|pending"
}
```

### 强制规则

- 只能追加合法 JSON 条目
- 不能在 JSON 尾部粘贴终端文本
- 如果证据不完整，`result` 必须是 `pending`

## 修复类任务的全局闭环

当任务是 bug 修复或报错处理时，至少覆盖：

1. 符号链路：声明 -> 定义 -> 调用
2. 构建链路：源文件、链接库、编译选项
3. 脚本链路：bootstrap、环境、自检门禁
4. 配置链路：config、默认值、环境变量
5. 文档链路：方案、Todo、debug 记录

