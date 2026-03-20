#!/usr/bin/env python3
"""Deterministic validation of Horizon OS documentation artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
DBUS_DIR = ROOT / "dbus"


def validate_json_files() -> list[str]:
    errors: list[str] = []
    for path in sorted(SCHEMA_DIR.rglob("*.json")):
        try:
            with path.open("r", encoding="utf-8") as handle:
                json.load(handle)
        except Exception as exc:  # pragma: no cover - simple validation helper
            errors.append(f"JSON parse failed for {path.relative_to(ROOT)}: {exc}")
    return errors


def validate_dbus_files() -> list[str]:
    errors: list[str] = []
    for path in sorted(DBUS_DIR.glob("*.xml")):
        try:
            ElementTree.parse(path)
        except Exception as exc:  # pragma: no cover - simple validation helper
            errors.append(f"XML parse failed for {path.relative_to(ROOT)}: {exc}")
    return errors


def main() -> int:
    errors = [*validate_json_files(), *validate_dbus_files()]
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Validated JSON schemas and D-Bus XML artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
