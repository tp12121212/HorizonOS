# ADR 0003: Keep Web Shell, Embedder, and Native Bridge Strictly Separated

- Status: Accepted
- Date: 2026-03-20

## Context

The shell is rendered with web technology, but web content is untrusted and cannot directly perform privileged operations.

## Decision

Adopt a three-layer model:
1. web shell UI served locally over loopback HTTPS
2. native `horizon-shell-host` Chromium embedder
3. native `horizon-systemext` bridge as sole path to privileged daemon operations

## Consequences

- Prevents direct privileged access from web code.
- Requires versioned bridge contracts and rigorous schema validation.
- Makes browser runtime replacement more feasible because the native bridge contract remains stable.
