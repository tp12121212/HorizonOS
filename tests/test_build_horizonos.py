from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from horizonos import generate_build_artifacts, write_build_artifacts


def _canonical_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_generate_build_artifacts_is_deterministic(tmp_path: Path) -> None:
    first = write_build_artifacts(tmp_path / "first")
    second = write_build_artifacts(tmp_path / "second")

    assert [path.name for path in first] == [path.name for path in second]
    for left, right in zip(first, second, strict=True):
        assert json.loads(left.read_text(encoding="utf-8")) == json.loads(right.read_text(encoding="utf-8"))
        assert _canonical_digest(left) == _canonical_digest(right)


def test_bridge_metadata_and_policy_bundle_shape() -> None:
    artifacts = generate_build_artifacts()

    assert artifacts.image_manifest["build_system"] == "yocto"
    assert artifacts.image_manifest["architectures"] == ["x86-64"]
    assert artifacts.default_policy_bundle["schema_version"] == "1.0.0"
    assert artifacts.default_policy_bundle["tenant_id"] == "TENANT_ID_PLACEHOLDER"
    assert artifacts.systemext_metadata["dbus_interface"] == "org.horizon.SystemExt1"
    assert "policy" in [item["namespace"] for item in artifacts.systemext_metadata["methods"]]
    assert artifacts.release_manifest["build_system"]["name"] == "yocto"
    assert [channel["name"] for channel in artifacts.release_manifest["release_channels"]] == [
        "Dev",
        "Beta",
        "Stable",
        "Enterprise-LTS",
    ]
    assert "yocto-build-reproducibility" in artifacts.release_manifest["required_validations"]


def test_cli_rebuilds_repository_artifacts() -> None:
    subprocess.run([sys.executable, "tools/build_horizonos.py"], cwd=ROOT, check=True)

    for path in (
        ROOT / "artifacts" / "image" / "horizonos-mvp-manifest.json",
        ROOT / "artifacts" / "policy" / "default-policy-bundle.json",
        ROOT / "artifacts" / "runtime" / "systemext-metadata.json",
        ROOT / "artifacts" / "release" / "release-manifest.json",
    ):
        assert path.exists(), path
        assert path.read_text(encoding="utf-8").endswith("\n")
