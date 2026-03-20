# Horizon System Bridge v1 Contract

## Scope

`HorizonSystemBridge` is the only supported privileged API surface exposed to shell web code. All request payloads are untrusted until validated by `horizon-systemext`.

## Versioning rules

- Semantic major version in namespace: `v1`
- Additive request/response fields are minor-compatible
- Field removals or behavior changes require `v2`
- Every request and response includes `schema_version`

## Security invariants

- schema validation before dispatch
- caller/session authorization check
- effective-policy evaluation before action
- audit event emission for accepted and denied calls
- per-method rate limiting
- explicit allowlist of destination daemons

## Namespaces

### `identity`
- `status()`
- `signIn(interactive_allowed: boolean)`
- `signOut(account_id: string)`
- `accounts()`

### `policy`
- `activePolicy()`
- `complianceState()`

### `network`
- `status()`
- `availableNetworks()`
- `connect(network_id: string, credential_ref?: string)`
- `disconnectVpn(vpn_id: string)`

### `update`
- `state()`
- `scheduleReboot(window_id?: string, deadline_epoch_ms?: integer)`

### `storage`
- `requestFileAccessToken(purpose: string, scope: string)`
- `volumes()`
- `syncStatus(provider: string)`

### `system`
- `deviceInfo()`
- `battery()`
- `setBrightness(percent: integer)`
- `setVolume(percent: integer)`

### `apps`
- `installedPwas()`
- `installPwa(manifest_url: string)`
- `uninstallPwa(app_id: string)`

### `notifications`
- `list()`
- `dismiss(notification_id: string)`

### `print`
- `printers()`
- `submit(job_ref: string)`

## Non-goals

- direct shell access to TPM
- direct shell access to NetworkManager D-Bus
- arbitrary D-Bus tunneling
- unrestricted file-system read/write
