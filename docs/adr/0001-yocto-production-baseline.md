# ADR 0001: Use Yocto Project as the Production Image Baseline

- Status: Accepted
- Date: 2026-03-20

## Context

Horizon OS requires a deterministic, signed, appliance-style Linux image with explicit control over kernel configuration, package composition, boot artifacts, and reproducibility.

## Decision

Use Yocto Project as the production build and image generation system.

## Consequences

- Supports deterministic image assembly and long-lived appliance maintenance.
- Requires up-front investment in layers, recipes, and CI pipelines.
- Developer-friendly distro bootstraps may still exist, but they are not release artifacts.
