#!/usr/bin/env python3
"""Generate deterministic HorizonOS implementation artifacts from repository contracts."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from horizonos import write_build_artifacts


def main() -> int:
    written = write_build_artifacts(ROOT / "artifacts")
    for path in written:
        print(path.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
