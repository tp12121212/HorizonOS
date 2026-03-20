# Horizon OS Architecture Baseline

## 1. Scope and feasibility guardrails

Horizon OS is feasible as an enterprise Linux operating system with a custom web-rendered shell, but several Microsoft-adjacent capabilities must be constrained to documented realities:

- **Unsupported assumption rejected:** full Entra Join semantics on Linux. Horizon OS supports **Entra device registration** plus tenant-aware token brokerage, not Windows-style join.
- **Unsupported assumption rejected:** native Intune management without additional work. Horizon OS must implement **OMA-DM v1.2 / SyncML**, **MS-MDE2-compatible enrollment flows where documented**, and custom CSP surfaces.
- **Unsupported assumption rejected:** native Windows app compatibility. Win32, COM/DCOM, .NET Framework desktop applications, and Windows kernel workloads are delivered only through **Azure Virtual Desktop** or **Windows 365 HTML5**.
- **Unsupported assumption rejected:** Chromium alone can serve as the OS. Chromium is an embedded runtime inside a real Linux OS with a hardened kernel, systemd, wlroots compositor, and native daemons.

## 2. Trusted computing base and trust boundaries

| Component | Trust level | Notes |
| --- | --- | --- |
| UEFI firmware + Secure Boot chain | TRUSTED | Root for boot validation; failures route to recovery. |
| shim, bootloader, UKI, initramfs | TRUSTED | Signed artifacts only; no unverified fallback. |
| Linux kernel + LSM + dm-verity stack | TRUSTED | LTS kernel, pinned version, measured boot. |
| `horizon-compositor` | TRUSTED | Owns input/output arbitration, session lock, capture gating. |
| `horizon-shell-host` | TRUSTED | Chromium embedder and policy enforcer for shell runtime. |
| `horizon-systemext` | TRUSTED | Sole native bridge from web shell to system daemons. |
| `horizon-policy` | TRUSTED | Authoritative effective-policy resolver. |
| `horizon-crypto` | TRUSTED | Sole steady-state TPM broker. |
| `horizon-identity` | TRUSTED by shell; CONDITIONALLY TRUSTED elsewhere | Device registration and token brokerage. |
| `horizon-storage` | CONDITIONALLY TRUSTED | Brokers file access and sync lifecycle. |
| PWAs / web shell code | UNTRUSTED | All requests validated, authorized, rate-limited, audited. |
| Remote servers, IdP responses, MDM payloads | UNTRUSTED | Signature/schema/protocol validation mandatory before use. |

## 3. MVP platform baseline

### 3.1 Base OS

- **Build system:** Yocto Project for production images.
- **Prototype allowance:** Alpine-derived bootstrap is acceptable only as a temporary developer path and must not become the production artifact model.
- **Architectures:** x86-64 is MVP shipping target; ARM64 build graph is designed but deferred.
- **Init:** systemd required.
- **Filesystem model:**
  - `/` read-only squashfs protected by dm-verity
  - `/var` writable, LUKS2-encrypted, TPM-sealed
  - `/home` writable, LUKS2-encrypted, TPM-sealed
  - `/etc` overlay sourced from `/var/etc`
  - `/run`, `/tmp` tmpfs

### 3.2 Boot and recovery

1. UEFI validates signed shim.
2. shim validates signed bootloader.
3. bootloader validates signed UKI.
4. UKI embeds kernel, initramfs, cmdline, `os-release`, and dm-verity metadata.
5. initramfs establishes dm-verity for the active rootfs.
6. TPM PCR policy gates LUKS unseal for `/var` and `/home`.
7. systemd starts only after security prerequisites are verified.

**Recovery requirements:**
- independently verified recovery partition
- reinstall from signed network source or signed local media
- OS-only reinstall preserving `/var` and `/home`
- factory wipe
- audited enterprise debug mode using a signed, time-limited token

### 3.3 Update model

- A/B partitions: `OS-A`, `OS-B`
- Full-image OTA only in MVP
- Standby image signature and dm-verity tree verified before boot target switch
- Health check commits update after successful boot
- Automatic rollback on boot or health failure
- Rings: Dev, Beta, Stable, Enterprise-LTS

## 4. Runtime architecture

### 4.1 Display and session stack

- `horizon-compositor` is a minimal compositor built on wlroots.
- Required protocols include output management, tablet input, IME, session lock, screencopy, cursor shape, and fractional scaling.
- Screen capture requires both user approval and policy approval.
- Remote input/control is deferred to enterprise debug sessions with signed admin authorization and auditing.

### 4.2 Shell host and web shell

- `horizon-shell-host` is a native Chromium embedder (CEF or Chromium Content API behind an abstraction layer).
- `horizon-shell-server` serves the shell over randomized loopback HTTPS using an embedder-trusted local certificate.
- External URLs open in separate browser contexts rather than inside privileged shell surfaces.
- Chromium version is pinned to the OS build in MVP and updated only through OS OTA.

### 4.3 Native service plane

Primary IPC is D-Bus with strict policies and explicit versioning. Core daemons:

- `horizon-identity`
- `horizon-policy`
- `horizon-mdm-agent`
- `horizon-kerberos`
- `horizon-crypto`
- `horizon-network`
- `horizon-update`
- `horizon-storage`
- `horizon-print`
- `horizon-systemext`

## 5. Identity and enterprise management

### 5.1 Identity model

MVP identity is a hybrid of:
- Entra device registration and OAuth/OIDC-based SSO token brokerage
- AD integration through SSSD, MIT Kerberos, and `realmd`

This is **not** Windows domain join or Windows Entra Join. AD GPO support is limited to SSSD-supported access-control use cases and cannot replace Horizon policy.

### 5.2 Enrollment model

1. Device boots to provisioning mode.
2. Enrollment is initiated from the local provisioning/recovery UI.
3. User or admin provides QR code or enrollment token.
4. `horizon-mdm-agent` performs MDM enrollment exchange.
5. `horizon-identity` completes device registration.
6. `horizon-mdm-agent` establishes OMA-DM session.
7. Signed policy bundle is validated by `horizon-policy`.
8. Device reboots into enrolled state.

### 5.3 Policy model

Horizon policy is a custom signed, deterministic policy system inspired by CSP and ADMX concepts, but implemented as:
- versioned JSON Schema templates
- signed policy bundles
- explicit precedence and conflict rules
- auditable effective-policy materialization

Policy precedence order:
1. local emergency TPM-sealed policy
2. cloud-delivered MDM policy
3. AD access-control subset
4. tenant baseline embedded in image

## 6. Microsoft workload delivery matrix

| Workload | MVP delivery | Offline | Limitations |
| --- | --- | --- | --- |
| Word / Excel / PowerPoint | Separate PWAs | Only if web app supports it | Add-ins and advanced desktop scenarios may require AVD. |
| Outlook | Outlook Web PWA | Limited to web capabilities | PST-heavy workflows and COM add-ins require AVD. |
| Teams | Teams web PWA | Limited | WebRTC only; non-web features require AVD. |
| OneDrive | Web PWA + managed OSS sync helper | Partial | No Files On-Demand in MVP. |
| Edge | Native Edge for Linux | N/A | Secondary browser, policy-managed. |
| PowerShell 7+ | Native package | Local/offline possible | Windows-only modules unsupported locally. |
| Remote Windows apps | AVD / Windows 365 HTML5 | No | Requires network and tenant-side service availability. |

## 7. Explicit phase boundaries

### Phase 1 / MVP
- x86-64 only
- verified boot
- hardened base image
- shell host + web shell
- core daemons
- Entra registration + SSO
- Intune-compatible OMA-DM subset
- JSON Schema policy engine
- M365 PWAs
- Edge for Linux
- PowerShell 7+
- A/B full-image OTA

### Phase 2
- ARM64 shipping support
- delta OTA
- richer policy categories including advanced DLP controls
- first-party Graph-based OneDrive/SharePoint sync engine
- Samba/Kerberos on-prem share integration
- handwriting recognition
- Horizon-native management portal

### Phase 3
- phone SKU
- phone-specific shell adaptations
- broader Graph object integration and portal maturity

