# HorizonOS Yocto Build Scaffold

This directory is the production build root for HorizonOS image work.

## MVP targets

- deterministic x86-64 image assembly
- signed UKI generation
- dm-verity root filesystem generation
- A/B partition image composition
- release-channel specific artifact publication

## Initial contents

- `conf/local.conf.sample` provides a deterministic baseline for developer image generation.
- `../../artifacts/release/release-manifest.json` captures publish-time channel ordering, validation gates, and signing requirements derived from the repository contracts.
- future Yocto layers should live under this directory and remain the only source of release artifacts.
