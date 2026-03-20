# Horizon OS MVP Plan

## Milestone ordering

1. **Security root and base image**
   - Yocto image definition
   - Secure Boot chain
   - UKI generation
   - dm-verity rootfs
   - TPM-sealed LUKS2 for `/var` and `/home`
   - recovery partition
   - A/B partition layout

2. **Display, shell host, and bridge**
   - wlroots-based compositor
   - Chromium embedder abstraction
   - shell loopback HTTPS server
   - `horizon-systemext` bridge with schema validation and audit logging

3. **Core daemons and contracts**
   - `horizon-policy`
   - `horizon-crypto`
   - `horizon-update`
   - `horizon-network`
   - `horizon-identity`
   - D-Bus and bridge contract freeze for v1

4. **Enterprise enrollment and compliance**
   - provisioning UI
   - OMA-DM enrollment subset
   - Entra registration flow
   - signed policy bundle ingestion
   - compliance reporting

5. **Microsoft productivity integrations**
   - PWA install catalog
   - Edge for Linux packaging
   - Teams/Outlook/Office/OneDrive launch flows
   - PowerShell 7+ packaging
   - AVD / Windows 365 HTML5 surfacing

6. **Release engineering and hardening**
   - artifact signing pipeline
   - update ring promotion
   - reproducible image verification
   - test matrices on reference hardware

## Epic list

### Epic 1 — Verified platform root
Deliver the secure, measured, rollback-capable base image.

### Epic 2 — Trusted session runtime
Deliver compositor, shell host, local shell serving, and hardened browser embedding.

### Epic 3 — Native control plane
Deliver Rust daemons with stable D-Bus contracts and system extension mediation.

### Epic 4 — Enterprise device lifecycle
Deliver enrollment, policy application, compliance, wipe/lock/reboot, and audit.

### Epic 5 — Productivity surface
Deliver M365 PWAs, Edge, PowerShell, OneDrive integration strategy, and remote Windows app entry points.

## Explicit deferments

1. **ARM64 shipping images** — deferred to Phase 2 because MVP must reduce hardware validation breadth while preserving architecture-neutral interfaces.
2. **Delta OTA** — deferred to Phase 2 because full-image OTA is simpler to validate alongside dm-verity and rollback.
3. **First-party Graph sync engine** — deferred to Phase 2 because MVP can use a managed OSS sync helper behind `horizon-storage`.
4. **Advanced DLP and per-file encryption** — deferred to Phase 2 because secure baseline and device management are higher priority than deep content controls.
5. **Phone SKU** — deferred to Phase 3 because telephony, mobile power policy, and UI adaptation materially expand system scope.
