from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas" / "policy"
DBUS_DIR = ROOT / "dbus"
CONTRACT_PATH = ROOT / "docs" / "contracts" / "horizon-system-bridge-v1.md"
YOCTO_LOCAL_CONF_SAMPLE = ROOT / "build" / "yocto" / "conf" / "local.conf.sample"


BOOT_CHAIN = (
    "uefi-secure-boot",
    "signed-shim",
    "signed-bootloader",
    "signed-uki",
    "dm-verity-rootfs",
    "tpm-sealed-luks2-var",
    "tpm-sealed-luks2-home",
)

CORE_DAEMONS = (
    "horizon-crypto",
    "horizon-identity",
    "horizon-mdm-agent",
    "horizon-network",
    "horizon-policy",
    "horizon-print",
    "horizon-storage",
    "horizon-systemext",
    "horizon-update",
)

PWA_CATALOG = (
    "https://outlook.office.com/mail/",
    "https://teams.microsoft.com/",
    "https://www.microsoft365.com/launch/word",
    "https://www.microsoft365.com/launch/excel",
    "https://www.microsoft365.com/launch/powerpoint",
    "https://www.office.com/launch/onedrive",
)

UPDATE_CHANNELS = (
    {
        "name": "Dev",
        "promotion_from": None,
        "audience": "engineering-validation",
        "auto_reboot_window_required": False,
        "policy_template": "update-policy-v1",
        "signing_profile": "dev-ed25519",
        "rollout": {"mode": "manual-approval", "max_parallel_devices": 50},
    },
    {
        "name": "Beta",
        "promotion_from": "Dev",
        "audience": "pre-production-pilot",
        "auto_reboot_window_required": True,
        "policy_template": "update-policy-v1",
        "signing_profile": "beta-ed25519",
        "rollout": {"mode": "staged-percentage", "percentage": 10},
    },
    {
        "name": "Stable",
        "promotion_from": "Beta",
        "audience": "broad-production",
        "auto_reboot_window_required": True,
        "policy_template": "update-policy-v1",
        "signing_profile": "stable-ed25519",
        "rollout": {"mode": "staged-percentage", "percentage": 25},
    },
    {
        "name": "Enterprise-LTS",
        "promotion_from": "Stable",
        "audience": "regulated-production",
        "auto_reboot_window_required": True,
        "policy_template": "update-policy-v1",
        "signing_profile": "enterprise-lts-ed25519",
        "rollout": {"mode": "manual-approval", "max_parallel_devices": 10},
    },
)

RELEASE_VALIDATIONS = (
    "yocto-build-reproducibility",
    "uki-signature-verification",
    "dm-verity-root-hash-verification",
    "ab-slot-health-check",
    "policy-bundle-schema-validation",
    "systemext-contract-drift-check",
)


@dataclass(frozen=True)
class BuildArtifacts:
    image_manifest: dict[str, Any]
    default_policy_bundle: dict[str, Any]
    systemext_metadata: dict[str, Any]
    release_manifest: dict[str, Any]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_yocto_local_conf() -> list[str]:
    with YOCTO_LOCAL_CONF_SAMPLE.open("r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip() and not line.lstrip().startswith("#")]


def _parse_dbus_interfaces() -> list[dict[str, Any]]:
    interfaces: list[dict[str, Any]] = []
    for path in sorted(DBUS_DIR.glob("*.xml")):
        tree = ElementTree.parse(path)
        for interface in tree.findall(".//interface"):
            methods: list[dict[str, Any]] = []
            signals: list[dict[str, Any]] = []
            for method in sorted(interface.findall("method"), key=lambda node: node.attrib["name"]):
                methods.append(
                    {
                        "name": method.attrib["name"],
                        "in_args": [
                            arg.attrib["name"]
                            for arg in method.findall("arg")
                            if arg.attrib.get("direction") == "in"
                        ],
                        "out_args": [
                            arg.attrib["name"]
                            for arg in method.findall("arg")
                            if arg.attrib.get("direction") == "out"
                        ],
                    }
                )
            for signal in sorted(interface.findall("signal"), key=lambda node: node.attrib["name"]):
                signals.append(
                    {
                        "name": signal.attrib["name"],
                        "args": [arg.attrib["name"] for arg in signal.findall("arg")],
                    }
                )
            interfaces.append(
                {
                    "interface": interface.attrib["name"],
                    "methods": methods,
                    "signals": signals,
                    "source": path.relative_to(ROOT).as_posix(),
                }
            )
    return sorted(interfaces, key=lambda item: item["interface"])


def _parse_bridge_namespaces() -> dict[str, list[str]]:
    namespaces: dict[str, list[str]] = {}
    current: str | None = None
    with CONTRACT_PATH.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line.startswith("### `") and line.endswith("`"):
                current = line.split("`", 2)[1]
                namespaces[current] = []
                continue
            if current and line.startswith("- `") and line.endswith("`"):
                namespaces[current].append(line.split("`", 2)[1])
    return {name: sorted(values) for name, values in sorted(namespaces.items())}


def _build_image_manifest() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "product": "HorizonOS",
        "release_channel": "MVP",
        "build_system": "yocto",
        "architectures": ["x86-64"],
        "boot_chain": list(BOOT_CHAIN),
        "filesystem_layout": {
            "/": "read-only squashfs with dm-verity",
            "/etc": "overlay from /var/etc",
            "/home": "luks2 encrypted and tpm sealed",
            "/run": "tmpfs",
            "/tmp": "tmpfs",
            "/var": "luks2 encrypted and tpm sealed",
        },
        "partition_layout": [
            "efi-system",
            "recovery",
            "os-a",
            "os-b",
            "var",
            "home",
        ],
        "core_daemons": list(CORE_DAEMONS),
        "m365_catalog": list(PWA_CATALOG),
        "dbus_interfaces": _parse_dbus_interfaces(),
        "bridge_contract": {
            "path": CONTRACT_PATH.relative_to(ROOT).as_posix(),
            "namespaces": _parse_bridge_namespaces(),
        },
    }


def _build_default_policy_bundle() -> dict[str, Any]:
    templates = {
        "app-policy-v1": _load_json(SCHEMA_DIR / "templates" / "app-policy-v1.schema.json"),
        "network-policy-v1": _load_json(SCHEMA_DIR / "templates" / "network-policy-v1.schema.json"),
        "update-policy-v1": _load_json(SCHEMA_DIR / "templates" / "update-policy-v1.schema.json"),
    }
    policies = [
        {
            "policy_id": "apps.m365-defaults",
            "scope": "device",
            "template": "app-policy-v1",
            "value": {
                "allowed_install_sources": [
                    "enterprise_catalog",
                    "managed_pwa",
                    "oci_signed",
                ],
                "auto_install_pwas": list(PWA_CATALOG),
                "schema_version": templates["app-policy-v1"]["properties"]["schema_version"]["const"],
            },
        },
        {
            "policy_id": "network.enterprise-baseline",
            "scope": "device",
            "template": "network-policy-v1",
            "value": {
                "allow_user_vpn_disconnect": False,
                "allowed_wifi_ssids": ["HorizonCorp", "HorizonCorp-Guest"],
                "schema_version": templates["network-policy-v1"]["properties"]["schema_version"]["const"],
            },
        },
        {
            "policy_id": "updates.enterprise-lts",
            "scope": "device",
            "template": "update-policy-v1",
            "value": {
                "allow_deferral": False,
                "ring": "Enterprise-LTS",
                "schema_version": templates["update-policy-v1"]["properties"]["schema_version"]["const"],
            },
        },
    ]
    return {
        "bundle_id": "horizonos.mvp.baseline",
        "generated_by": "tools/build_horizonos.py",
        "policies": policies,
        "schema_version": "1.0.0",
        "signature": {
            "algorithm": "placeholder-ed25519",
            "key_id": "tenant-key-placeholder",
            "signature_b64": "REPLACE_WITH_REAL_SIGNATURE",
        },
        "tenant_id": "TENANT_ID_PLACEHOLDER",
    }


def _build_systemext_metadata() -> dict[str, Any]:
    bridge_namespaces = _parse_bridge_namespaces()
    allowlisted_daemons = sorted(
        {namespace for namespace in bridge_namespaces if namespace not in {"apps", "notifications", "system"}}
        | {"print"}
    )
    return {
        "schema_version": "1.0.0",
        "bridge_name": "HorizonSystemBridge",
        "contract_path": CONTRACT_PATH.relative_to(ROOT).as_posix(),
        "dbus_interface": "org.horizon.SystemExt1",
        "allowlisted_daemons": allowlisted_daemons,
        "methods": [
            {
                "namespace": namespace,
                "operations": operations,
            }
            for namespace, operations in bridge_namespaces.items()
        ],
        "security_invariants": [
            "schema validation before dispatch",
            "caller/session authorization check",
            "effective-policy evaluation before action",
            "audit event emission for accepted and denied calls",
            "per-method rate limiting",
        ],
    }


def _build_release_manifest() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "product": "HorizonOS",
        "build_system": {
            "name": "yocto",
            "local_conf_sample": YOCTO_LOCAL_CONF_SAMPLE.relative_to(ROOT).as_posix(),
            "pinned_settings": _load_yocto_local_conf(),
        },
        "image_model": {
            "architecture": "x86-64",
            "format": "full-image-ota",
            "slot_strategy": ["os-a", "os-b"],
            "recovery_partition": True,
            "verified_boot": list(BOOT_CHAIN),
        },
        "release_channels": list(UPDATE_CHANNELS),
        "required_validations": list(RELEASE_VALIDATIONS),
        "publish_requirements": {
            "artifact_extensions": [".otaimg", ".uki", ".verity", ".manifest.json"],
            "immutable_metadata_fields": [
                "build_system.name",
                "image_model.slot_strategy",
                "release_channels[*].name",
                "schema_version",
            ],
            "signing": {
                "bundle_manifest": "required",
                "uki": "required",
                "ota_payload": "required",
            },
        },
    }


def generate_build_artifacts() -> BuildArtifacts:
    return BuildArtifacts(
        image_manifest=_build_image_manifest(),
        default_policy_bundle=_build_default_policy_bundle(),
        systemext_metadata=_build_systemext_metadata(),
        release_manifest=_build_release_manifest(),
    )


def write_build_artifacts(output_dir: Path) -> list[Path]:
    artifacts = generate_build_artifacts()
    output_dir.mkdir(parents=True, exist_ok=True)
    targets = {
        output_dir / "image" / "horizonos-mvp-manifest.json": artifacts.image_manifest,
        output_dir / "policy" / "default-policy-bundle.json": artifacts.default_policy_bundle,
        output_dir / "runtime" / "systemext-metadata.json": artifacts.systemext_metadata,
        output_dir / "release" / "release-manifest.json": artifacts.release_manifest,
    }
    written: list[Path] = []
    for path, payload in targets.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(path)
    return written


__all__ = ["BuildArtifacts", "generate_build_artifacts", "write_build_artifacts"]
