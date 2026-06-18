#!/usr/bin/env python3
"""Validate a model routing config file."""

from __future__ import annotations

import argparse
from pathlib import Path

from model_routing_core import load_json, validate_routing_config


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to model routing JSON config")
    args = parser.parse_args()

    config = load_json(Path(args.config))
    errors = validate_routing_config(config)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Model routing config validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
