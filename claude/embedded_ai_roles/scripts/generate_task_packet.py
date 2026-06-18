#!/usr/bin/env python3
"""Generate a reusable task packet for embedded planning and debug workflows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from model_routing_core import resolve_model_routing
from task_routing_core import (
    ROLE_FOCUS,
    ROLE_LABELS,
    SCENARIO_PLAYBOOK_SECTION,
    detect_mode,
    detect_scenario,
    get_mode_signals,
    get_scenario_signals,
    select_roles,
)


PACKET_SCHEMA_VERSION = 1
PLAYBOOK_PATH = ".claude/embedded_ai_roles/references/task-playbooks.md"
ROLE_DIR = Path(".claude/embedded_ai_roles/embedded_ai_roles")

PLAN_HEADINGS = [
    "# 方案：[功能名称]",
    "## 目标与范围",
    "## 现状与证据",
    "## 实现方案",
    "## 接口与影响面",
    "## 风险与待确认",
    "## 验收标准",
]

TODO_HEADINGS = [
    "# Todo：[功能名称]",
    "## 里程碑",
    "## 任务列表",
    "## 验收与回归",
    "## 风险跟踪",
]

DEBUG_REQUIRED_KEYS = [
    "feature",
    "created_at",
    "mode",
    "requirement",
    "evidence",
    "decisions",
    "debug_log",
    "status",
]

COMMON_INITIAL_CHECKS = [
    "确认当前工作目录、仓库状态和已有未提交修改",
    "确认是否已有 topStruct.md、方案.md、Todo.md、debug.json",
    "优先读取成功标准、证据门禁和对应 playbook",
]

SCENARIO_INITIAL_CHECKS = {
    "new_feature_planning": [
        "判断是新工程还是已有工程",
        "盘点现有模块、接口、构建方式与可复用能力",
        "明确当前版本的目标、非目标和验收口径",
    ],
    "compile_or_link_failure": [
        "保留完整编译输出和失败命令",
        "确认问题属于代码、脚本、工具链还是环境",
        "检查相关源文件、头文件、链接库是否纳入构建",
    ],
    "dts_or_driver_not_effective": [
        "确认板级版本、DTS 来源与当前内核树位置",
        "核对 binding、compatible 与 parse 链路",
        "收集 dmesg、sysfs 或 debugfs 运行时证据",
    ],
    "runtime_service_instability": [
        "明确复现条件、触发路径与日志时间窗",
        "核对服务配置、启动链与依赖状态",
        "区分系统、应用、驱动或环境问题",
    ],
    "release_blocker": [
        "盘点阻塞项并区分发布阻断与可后移项",
        "核对交付物、测试结论和版本状态",
        "明确负责人与最后闭环动作",
    ],
    "general_embedded_task": [
        "先把任务拆成 planning、implementation 或 debug",
        "补充最小证据，再决定后续角色与产物",
    ],
}

SCENARIO_EVIDENCE_TARGETS = {
    "new_feature_planning": [
        "现有模块与调用链",
        "现有配置入口与部署方式",
        "与目标功能相关的历史日志、接口和问题记录",
    ],
    "compile_or_link_failure": [
        "完整编译输出",
        "CMakeLists.txt / Makefile / toolchain 文件",
        "缺失符号、头文件和链接库来源",
    ],
    "dts_or_driver_not_effective": [
        "DTS / DTSI / binding 文档",
        "of_device_id、属性解析函数和 Kconfig / Makefile 链路",
        "运行时日志、节点或寄存器侧证据",
    ],
    "runtime_service_instability": [
        "复现步骤和日志",
        "配置文件、启动脚本与依赖状态",
        "资源占用、watchdog 和错误路径证据",
    ],
    "release_blocker": [
        "当前通过 / 未通过的门禁",
        "测试报告、回归结果和已知风险",
        "版本、交付物和回滚准备状态",
    ],
    "general_embedded_task": [
        "与当前任务最直接相关的源码、配置、脚本和日志",
        "任何会影响结论的版本、接口和运行环境事实",
    ],
}

COMMON_ACCEPTANCE_CHECKS = [
    "结论必须区分已确认事实与待确认项",
    "产物必须可直接交接给下一位角色继续推进",
    "所有关键判断都应附带证据来源或明确标记为 pending",
]

SCENARIO_ACCEPTANCE_CHECKS = {
    "new_feature_planning": [
        "方案.md 包含明确目标、影响面、风险和量化验收标准",
        "Todo.md 中每项任务都有产物或验证方式",
        "debug.json 记录关键决策与后续补证据动作",
    ],
    "compile_or_link_failure": [
        "至少覆盖一个上游和一个下游文件的检查",
        "修复后重跑构建或说明未验证原因",
        "debug.json.debug_log 记录根因、修复和结果",
    ],
    "dts_or_driver_not_effective": [
        "同时检查 DTS、binding、parse 与运行时证据",
        "给出最小验证路径而不是停留在理论判断",
        "明确哪些属性已确认、哪些仍待板级验证",
    ],
    "runtime_service_instability": [
        "包含复现条件、修复验证和回归方案",
        "区分根因、诱因和暂未确认因素",
        "避免只看崩溃点而忽略上下游影响",
    ],
    "release_blocker": [
        "阻塞项必须有负责人、下一步和风险等级",
        "明确区分阻断发布与可后移问题",
        "交付证据、测试证据和回滚准备状态可追踪",
    ],
    "general_embedded_task": [
        "任务被收敛到明确模式和最小角色集合",
        "至少给出一组可执行的下一步动作",
    ],
}

HANDOFF_FIELDS = [
    "目标与范围",
    "关键证据",
    "当前判断",
    "待确认与阻塞",
    "建议下一步",
]


def build_role_entries(role_ids: list[str]) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for role_id in role_ids:
        entries.append(
            {
                "id": role_id,
                "file": str(ROLE_DIR / ROLE_LABELS[role_id]),
                "focus": ROLE_FOCUS[role_id],
            }
        )
    return entries


def build_task_packet(
    task: str,
    *,
    enable_model_routing: bool = False,
    routing_config_path: str | None = None,
) -> dict[str, object]:
    mode = detect_mode(task)
    scenario = detect_scenario(task, mode=mode)
    role_ids = select_roles(task, scenario=scenario, mode=mode)
    model_routing = resolve_model_routing(
        task=task,
        mode=mode,
        scenario=scenario,
        skill="embedded-feature-planner",
        enable_model_routing=enable_model_routing,
        routing_config_path=routing_config_path,
    )

    return {
        "schema_version": PACKET_SCHEMA_VERSION,
        "task": task,
        "mode": mode,
        "scenario": scenario,
        "model_routing": model_routing,
        "playbook": PLAYBOOK_PATH,
        "playbook_section": SCENARIO_PLAYBOOK_SECTION[scenario],
        "roles": build_role_entries(role_ids),
        "artifacts": {
            "task_packet": "required",
            "topStruct": "conditional",
            "plan": "required",
            "todo": "required",
            "debug": "required",
        },
        "artifact_templates": {
            "plan_headings": PLAN_HEADINGS,
            "todo_headings": TODO_HEADINGS,
            "debug_required_keys": DEBUG_REQUIRED_KEYS,
        },
        "initial_checks": COMMON_INITIAL_CHECKS + SCENARIO_INITIAL_CHECKS[scenario],
        "evidence_targets": SCENARIO_EVIDENCE_TARGETS[scenario],
        "acceptance_checks": COMMON_ACCEPTANCE_CHECKS + SCENARIO_ACCEPTANCE_CHECKS[scenario],
        "handoff_fields": HANDOFF_FIELDS,
        "routing_signals": {
            "mode": get_mode_signals(task),
            "scenario": get_scenario_signals(task, mode=mode),
        },
        "notes": [
            "先生成任务包，再据此决定读取哪些角色文件与规则文件。",
            "如果证据不足，优先在 debug.json 和记为 pending，而不是把猜测写成事实。",
        ],
    }


def print_markdown(packet: dict[str, object]) -> None:
    print("# Task Packet")
    print(f"- schema_version: {packet['schema_version']}")
    print(f"- mode: {packet['mode']}")
    print(f"- scenario: {packet['scenario']}")
    print(f"- playbook: {packet['playbook']}")
    print(f"- playbook_section: {packet['playbook_section']}")
    print(f"- model_routing_enabled: {packet['model_routing']['enabled']}")
    print("- roles:")
    for role in packet["roles"]:
        print(f"  - {role['id']}: {role['focus']}")
    print("- initial_checks:")
    for item in packet["initial_checks"]:
        print(f"  - {item}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout")
    parser.add_argument("--output", help="Optional JSON output path")
    parser.add_argument("--enable-model-routing", action="store_true", help="Explicitly enable model routing")
    parser.add_argument("--routing-config", help="JSON config path for model routing")
    args = parser.parse_args()

    packet = build_task_packet(
        args.task,
        enable_model_routing=args.enable_model_routing,
        routing_config_path=args.routing_config,
    )

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json or args.output:
        print(json.dumps(packet, ensure_ascii=False, indent=2))
    else:
        print_markdown(packet)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
