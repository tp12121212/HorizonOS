# Proposed Repository Structure

This structure keeps kernel/base, compositor, embedder, daemons, contracts, schemas, and policy assets separated so trust boundaries stay explicit.

```text
.
├── README.md
├── dbus/
│   ├── org.horizon.Identity1.xml
│   ├── org.horizon.Policy1.xml
│   ├── org.horizon.SystemExt1.xml
│   └── org.horizon.Update1.xml
├── docs/
│   ├── architecture.md
│   ├── mvp-plan.md
│   ├── repository-structure.md
│   ├── contracts/
│   │   └── horizon-system-bridge-v1.md
│   └── adr/
│       ├── 0001-yocto-production-baseline.md
│       ├── 0002-verified-boot-and-ab-updates.md
│       └── 0003-shell-embedder-and-bridge-boundary.md
├── schemas/
│   └── policy/
│       ├── policy-bundle-v1.schema.json
│       └── templates/
│           ├── app-policy-v1.schema.json
│           ├── network-policy-v1.schema.json
│           └── update-policy-v1.schema.json
└── tools/
    └── validate_artifacts.py
```

## Ownership boundaries

- `dbus/`: stable introspection documents consumed by daemon implementations and integration tests.
- `docs/contracts/`: human-readable API contracts and versioning rules for shell/native interfaces.
- `schemas/policy/`: signed policy schema source of truth.
- `tools/`: deterministic validation helpers only; no hidden network calls or timestamps.

## Implementation guidance

- Native daemons should live under `services/` in future code work, one service per directory.
- Shell host and Chromium integration should live under `runtime/` and remain isolated from shell web code under `shell/`.
- Yocto layers should live under `build/yocto/` once image work begins.
- Provisioning and recovery UI assets should stay separate from daily shell code because they run under different operational constraints.
