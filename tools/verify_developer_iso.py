#!/usr/bin/env python3
"""Boot a HorizonOS developer ISO under QEMU and assert the initramfs banner appears."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

BOOT_SENTINEL = 'HORIZONOS_BOOT_OK'
ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('iso_path', type=Path, help='ISO file to boot and verify.')
    parser.add_argument('--timeout-seconds', type=int, default=60, help='QEMU timeout.')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.iso_path.exists():
        print(f'ISO not found: {args.iso_path}', file=sys.stderr)
        return 1
    if shutil.which('qemu-system-x86_64') is None:
        print("Required tool 'qemu-system-x86_64' is not installed.", file=sys.stderr)
        return 1

    ovmf_path = Path('/usr/share/ovmf/OVMF.fd')
    if not ovmf_path.exists():
        print(f'UEFI firmware not found: {ovmf_path}', file=sys.stderr)
        return 1

    command = [
        'timeout',
        str(args.timeout_seconds),
        'qemu-system-x86_64',
        '-m',
        '1024',
        '-cdrom',
        str(args.iso_path),
        '-nographic',
        '-serial',
        'stdio',
        '-monitor',
        'none',
        '-no-reboot',
        '-bios',
        str(ovmf_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    output = completed.stdout + completed.stderr
    if BOOT_SENTINEL not in output:
        print(output, end='', file=sys.stderr)
        print('Boot sentinel was not observed in serial output.', file=sys.stderr)
        return 1
    print(BOOT_SENTINEL)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
