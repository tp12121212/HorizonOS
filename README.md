# Horizon OS

Horizon OS is a web-centric, enterprise-grade operating system for Microsoft 365–centric organizations.
It is a real Linux OS with a hardened kernel, verified boot, a web-rendered shell, native Rust daemons,
and a pinned Chromium runtime.

## MVP principles

- Verified boot, signed artifacts, and A/B updates are mandatory.
- Entra device registration is supported; Windows-style Entra Join is not.
- Intune compatibility requires Horizon OS to implement OMA-DM v1.2 / SyncML enrollment and CSP support.
- Win32, COM/DCOM, .NET Framework desktop, and kernel-mode Windows workloads are remote only via Azure Virtual Desktop or Windows 365 HTML5.
- Chromium is pinned to the OS release and updated through the verified OS update pipeline in MVP.

## Repository layout

- `docs/architecture.md` — end-to-end MVP architecture, trust boundaries, boot chain, and phased roadmap.
- `docs/repository-structure.md` — proposed source tree and ownership boundaries.
- `docs/mvp-plan.md` — milestone sequencing, epics, and explicit deferments.
- `docs/adr/` — architecture decision records.
- `docs/contracts/` — versioned interface contracts for native services and shell bridge APIs.
- `schemas/policy/` — deterministic JSON Schema documents for Horizon policy bundles and templates.
- `dbus/` — versioned D-Bus introspection XML for daemon interfaces.
- `tools/` — deterministic validation helpers and build-artifact generators.
- `src/horizonos/` — deterministic Python helpers that materialize HorizonOS build artifacts from repo contracts.
- `artifacts/` — generated image, policy, and runtime metadata outputs checked for reproducibility.

## MVP scope

1. Hardened x86-64 Linux base with systemd, dm-verity, TPM 2.0 sealing, UEFI Secure Boot, and A/B OTA.
2. wlroots-based compositor, Chromium embedder, and local shell server.
3. Native daemons for identity, policy, MDM, crypto, networking, updates, storage, print, and shell bridge.
4. Microsoft 365 PWAs, Edge for Linux, PowerShell 7+, and remote Windows apps through AVD / Windows 365 HTML5.
5. Intune-compatible OMA-DM subset, JSON Schema policy engine, and compliance reporting.

## Explicit limitations

- No Wine, Proton, Android runtime, or native Win32 compatibility layer.
- No full Windows Group Policy support; Horizon OS uses signed JSON Schema–driven policy.
- No phone SKU in MVP.
- No delta OTA in MVP.
- No first-party Graph-based OneDrive sync in MVP.

## Validation

Use the repository helpers to generate deterministic build artifacts and validate that schemas, D-Bus contracts, and generated outputs remain in sync.

```bash
python3 tools/build_horizonos.py
python3 tools/validate_artifacts.py
```
