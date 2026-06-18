#!/usr/bin/env python3
"""Shared routing helpers for embedded task classification and role selection."""

from __future__ import annotations

from collections import OrderedDict


ROLE_LABELS = OrderedDict(
    [
        ("product_manager", "01_product_manager.md"),
        ("system_architect", "02_system_architect.md"),
        ("hardware_engineer", "03_hardware_engineer.md"),
        ("bsp_engineer", "04_bsp_engineer.md"),
        ("driver_engineer", "05_driver_engineer.md"),
        ("system_engineer", "06_system_engineer.md"),
        ("application_engineer", "07_application_engineer.md"),
        ("test_engineer", "08_test_engineer.md"),
        ("devops_engineer", "09_devops_engineer.md"),
        ("project_manager", "10_project_manager.md"),
    ]
)

ROLE_FOCUS = {
    "product_manager": "收敛目标、范围、优先级与验收标准",
    "system_architect": "定义模块边界、接口约束与关键技术取舍",
    "hardware_engineer": "确认板级约束、电气条件与接口现实",
    "bsp_engineer": "确认 SDK、内核、板级配置与底层集成链路",
    "driver_engineer": "确认设备匹配、属性解析与驱动行为",
    "system_engineer": "确认系统服务、配置、运行链路与跨模块联动",
    "application_engineer": "确认应用逻辑、协议处理与异常路径",
    "test_engineer": "定义验证入口、阻断条件与回归范围",
    "devops_engineer": "确认构建、打包、部署与可追溯门禁",
    "project_manager": "管理里程碑、依赖、阻塞与交付节奏",
}

MODE_KEYWORDS = {
    "debug": (
        "修复",
        "报错",
        "失败",
        "异常",
        "bug",
        "排查",
        "不生效",
        "崩溃",
        "超时",
        "阻塞",
        "卡死",
    ),
    "implementation": ("实现", "开发", "编码", "落地", "接入", "改造", "新增"),
}

SCENARIO_RULES = OrderedDict(
    [
        (
            "new_feature_planning",
            {
                "keywords": (
                    "新功能",
                    "新增",
                    "接入",
                    "实现",
                    "落地",
                    "需求",
                    "规划",
                    "方案",
                    "todo",
                    "roadmap",
                    "feature",
                    "能力扩展",
                    "版本规划",
                ),
                "priority": {"planning": 0, "implementation": 2, "debug": 4},
            },
        ),
        (
            "compile_or_link_failure",
            {
                "keywords": (
                    "编译",
                    "链接",
                    "cmake",
                    "makefile",
                    "toolchain",
                    "undefined reference",
                    "compiler",
                    "build error",
                ),
                "priority": {"planning": 2, "implementation": 1, "debug": 0},
            },
        ),
        (
            "dts_or_driver_not_effective",
            {
                "keywords": (
                    "dts",
                    "dtsi",
                    "device tree",
                    "驱动",
                    "probe",
                    "compatible",
                    "kconfig",
                    "sysfs",
                    "debugfs",
                    "of_property",
                    "不生效",
                ),
                "priority": {"planning": 3, "implementation": 3, "debug": 1},
            },
        ),
        (
            "runtime_service_instability",
            {
                "keywords": (
                    "崩溃",
                    "超时",
                    "服务",
                    "异常",
                    "死锁",
                    "watchdog",
                    "运行时",
                    "重启",
                    "hang",
                    "卡死",
                    "daemon",
                ),
                "priority": {"planning": 4, "implementation": 4, "debug": 2},
            },
        ),
        (
            "release_blocker",
            {
                "keywords": (
                    "发布",
                    "交付",
                    "验收",
                    "回归",
                    "收口",
                    "门禁",
                    "blocker",
                    "release",
                    "阻塞",
                ),
                "priority": {"planning": 1, "implementation": 0, "debug": 3},
            },
        ),
    ]
)

SCENARIO_PLAYBOOK_SECTION = {
    "new_feature_planning": "## 1. 新功能规划",
    "compile_or_link_failure": "## 2. 编译失败 / 链接失败",
    "dts_or_driver_not_effective": "## 3. DTS / 驱动不生效",
    "runtime_service_instability": "## 4. 运行时异常 / 服务不稳定",
    "release_blocker": "## 5. 发布阻塞 / 交付前收口",
    "general_embedded_task": "## 1. 新功能规划",
}


def normalize(task: str) -> str:
    return task.lower()


def ordered_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def matched_keywords(text: str, keywords: tuple[str, ...]) -> list[str]:
    return [keyword for keyword in keywords if keyword.lower() in text]


def get_mode_signals(task: str) -> dict[str, list[str]]:
    text = normalize(task)
    return {mode: matched_keywords(text, keywords) for mode, keywords in MODE_KEYWORDS.items()}


def detect_mode(task: str) -> str:
    signals = get_mode_signals(task)
    if signals["debug"]:
        return "debug"
    if signals["implementation"]:
        return "implementation"
    return "planning"


def rank_scenarios(task: str, mode: str | None = None) -> list[dict[str, object]]:
    current_mode = mode or detect_mode(task)
    text = normalize(task)
    ranked: list[dict[str, object]] = []

    for scenario, rule in SCENARIO_RULES.items():
        signals = matched_keywords(text, rule["keywords"])
        if not signals:
            continue
        ranked.append(
            {
                "scenario": scenario,
                "signals": signals,
                "score": len(signals),
                "priority": rule["priority"][current_mode],
            }
        )

    ranked.sort(key=lambda item: (-int(item["score"]), int(item["priority"])))
    return ranked


def detect_scenario(task: str, mode: str | None = None) -> str:
    ranked = rank_scenarios(task, mode=mode)
    if ranked:
        return str(ranked[0]["scenario"])
    return "general_embedded_task"


def get_scenario_signals(task: str, mode: str | None = None) -> list[str]:
    ranked = rank_scenarios(task, mode=mode)
    if ranked:
        return list(ranked[0]["signals"])
    return []


def select_roles(task: str, scenario: str | None = None, mode: str | None = None) -> list[str]:
    current_mode = mode or detect_mode(task)
    current_scenario = scenario or detect_scenario(task, mode=current_mode)
    text = normalize(task)

    if current_scenario == "new_feature_planning":
        roles = ["product_manager", "system_architect", "test_engineer", "project_manager"]
    elif current_scenario == "compile_or_link_failure":
        roles = ["system_engineer", "application_engineer", "devops_engineer", "test_engineer"]
    elif current_scenario == "dts_or_driver_not_effective":
        roles = ["hardware_engineer", "bsp_engineer", "driver_engineer", "test_engineer"]
    elif current_scenario == "runtime_service_instability":
        roles = ["system_engineer", "application_engineer", "test_engineer", "devops_engineer"]
    elif current_scenario == "release_blocker":
        roles = ["project_manager", "test_engineer", "devops_engineer", "system_architect"]
    else:
        roles = ["system_architect", "test_engineer", "project_manager"]

    if any(key in text for key in ("硬件", "原理图", "pcb", "gpio", "供电", "时序", "电平")):
        roles.append("hardware_engineer")

    if any(
        key in text
        for key in ("dts", "dtsi", "device tree", "驱动", "内核", "probe", "compatible", "kconfig", "bsp")
    ):
        roles.extend(["bsp_engineer", "driver_engineer", "system_engineer"])

    if any(
        key in text
        for key in ("编译", "链接", "cmake", "makefile", "toolchain", "部署", "ci", "构建", "发布")
    ):
        roles.extend(["devops_engineer", "test_engineer"])

    if any(
        key in text
        for key in ("服务", "daemon", "mqtt", "systemd", "运行时", "崩溃", "异常", "桥接")
    ):
        roles.extend(["system_engineer", "application_engineer"])

    if any(key in text for key in ("ai", "模型", "推理", "业务逻辑", "云端", "app", "协议", "算法")):
        roles.append("application_engineer")

    if current_mode == "planning" and "product_manager" not in roles:
        roles.insert(0, "product_manager")

    if current_mode == "implementation":
        roles.append("system_engineer")
        if current_scenario in {"new_feature_planning", "runtime_service_instability"}:
            roles.append("application_engineer")

    if current_scenario == "release_blocker":
        roles.append("project_manager")

    return ordered_unique(roles)
