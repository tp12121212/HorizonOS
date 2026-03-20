#!/usr/bin/env python3
"""Build a deterministic HorizonOS developer ISO image."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from horizonos.deviso import (  # noqa: E402
    DEFAULT_ISO_BASENAME,
    DevIsoBuildError,
    DevIsoBuildRequest,
    build_developer_iso,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--output',
        default=ROOT / 'artifacts' / 'iso' / f'{DEFAULT_ISO_BASENAME}.iso',
        type=Path,
        help='Output ISO path.',
    )
    parser.add_argument(
        '--kernel-path',
        default=Path('/boot/vmlinuz'),
        type=Path,
        help='Kernel image used for the live developer environment.',
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    request = DevIsoBuildRequest(output_path=args.output, kernel_path=args.kernel_path)
    try:
        result = build_developer_iso(request)
    except DevIsoBuildError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    try:
        output = result.iso_path.relative_to(ROOT).as_posix()
    except ValueError:
        output = str(result.iso_path)
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
