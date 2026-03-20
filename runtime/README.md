# HorizonOS Runtime

Runtime components own the trusted local session stack.

- `horizon-compositor` will host the wlroots session runtime.
- `horizon-shell-host` will host the Chromium embedder.
- shell web assets remain isolated from native bridge code.
