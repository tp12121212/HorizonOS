#!/usr/bin/env python3
"""Deterministic validation of Horizon OS documentation and generated artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from horizonos import generate_build_artifacts

SCHEMA_DIR = ROOT / "schemas"
DBUS_DIR = ROOT / "dbus"
ARTIFACTS_DIR = ROOT / "artifacts"


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


def validate_generated_artifacts() -> list[str]:
    errors: list[str] = []
    expected = generate_build_artifacts()
    targets = {
        ARTIFACTS_DIR / "image" / "horizonos-mvp-manifest.json": expected.image_manifest,
        ARTIFACTS_DIR / "policy" / "default-policy-bundle.json": expected.default_policy_bundle,
        ARTIFACTS_DIR / "runtime" / "systemext-metadata.json": expected.systemext_metadata,
    }
    for path, expected_payload in targets.items():
        if not path.exists():
            errors.append(f"Generated artifact missing: {path.relative_to(ROOT)}")
            continue
        try:
            actual_payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - simple validation helper
            errors.append(f"Generated artifact is invalid JSON for {path.relative_to(ROOT)}: {exc}")
            continue
        if actual_payload != expected_payload:
            errors.append(f"Generated artifact is out of date: {path.relative_to(ROOT)}")
    return errors


def main() -> int:
    errors = [
        *validate_json_files(),
        *validate_dbus_files(),
        *validate_generated_artifacts(),
    ]
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Validated JSON schemas, D-Bus XML artifacts, and generated HorizonOS build artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
