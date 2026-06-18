# Domain Routing

## 默认模式

若没有明显嵌入式关键词，默认使用 `通用模式`。

## 嵌入式模式关键词

命中以下任一关键词，优先进入 `嵌入式模式`：

`RV1126` `MCU` `MPU` `STM32` `MQTT` `BSP` `驱动` `嵌入式` `鸿蒙` `OpenHarmony` `RTOS` `Linux 内核` `交叉编译` `工具链` `烧录` `固件` `OTA` `NPU` `RKNN` `UART` `I2C` `SPI` `GPIO` `DTS` `U-Boot` `Buildroot`

## 嵌入式子领域映射

- 出现 `DTS` `GPIO` `I2C` `SPI` `UART` `probe` `compatible` -> `驱动/BSP`
- 出现 `systemd` `daemon` `守护进程` `bridge` `MQTT broker` -> `系统服务`
- 出现 `RKNN` `NPU` `推理` `模型部署` -> `AI 应用`
- 出现 `测试` `回归` `验收` `量产` -> `测试/交付`

## 通用模式建议领域

按关键词选择更贴近的领域：

- `代码` `审阅` `重构` -> 软件工程
- `分析` `调研` `比较` -> 研究分析
- `写作` `文案` `邮件` -> 专业写作
- `翻译` -> 双语语言服务
- `产品` `需求` `PRD` -> 产品管理
- `调试` `排障` -> 工程诊断

