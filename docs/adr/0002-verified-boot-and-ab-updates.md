# ADR 0002: Enforce Verified Boot and A/B Updates from MVP

- Status: Accepted
- Date: 2026-03-20

## Context

The product brief requires verified boot from day one, no silent fallback to unverified state, and rollback-capable system updates.

## Decision

Ship MVP with:
- Secure Boot
- signed shim / bootloader / UKI chain
- dm-verity root filesystem
- recovery partition with independent verification
- A/B full-image OTA

## Consequences

- Update implementation is operationally heavier than package-based mutation of a live rootfs.
- Security posture is materially stronger and easier to reason about.
- Delta OTA is deferred until the A/B image pipeline is stable.
