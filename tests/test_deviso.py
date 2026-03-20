from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src'
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from horizonos.deviso import (  # noqa: E402
    DEFAULT_SOURCE_DATE_EPOCH,
    DevIsoBuildRequest,
    _write_grub_config,
    build_developer_iso,
)


REQUIRED_ISO_TOOLS = ('busybox', 'cpio', 'grub-mkrescue', 'qemu-system-x86_64', 'xorriso')


def test_grub_config_is_deterministic(tmp_path: Path) -> None:
    config_path = tmp_path / 'grub.cfg'
    request = DevIsoBuildRequest(output_path=tmp_path / 'artifact.iso')

    _write_grub_config(config_path, request)

    assert config_path.read_text(encoding='utf-8') == (
        "set timeout=0\n"
        "set default=0\n"
        "serial --speed=115200\n"
        "terminal_input console serial\n"
        "terminal_output console serial\n"
        "menuentry 'HorizonOS Developer ISO' {\n"
        "    linux /boot/vmlinuz console=ttyS0,115200 printk.time=0 quiet root=/dev/ram0 rootfstype=ramfs horizonos.root_label=horizonos-dev\n"
        "    initrd /boot/initrd.img\n"
        "}\n"
    )


@pytest.mark.skipif(any(shutil.which(tool) is None for tool in REQUIRED_ISO_TOOLS), reason='iso build tools unavailable')
def test_build_developer_iso_builds_successfully(tmp_path: Path) -> None:
    first_request = DevIsoBuildRequest(output_path=tmp_path / 'first.iso')
    second_request = DevIsoBuildRequest(output_path=tmp_path / 'second.iso')

    first = build_developer_iso(first_request)
    second = build_developer_iso(second_request)

    assert first.iso_path.exists()
    assert second.iso_path.exists()
    assert first_request.source_date_epoch == DEFAULT_SOURCE_DATE_EPOCH
    assert first.iso_path.stat().st_size > 0
    assert second.iso_path.stat().st_size > 0


@pytest.mark.skipif(any(shutil.which(tool) is None for tool in REQUIRED_ISO_TOOLS), reason='iso build tools unavailable')
def test_cli_build_and_verify_iso(tmp_path: Path) -> None:
    iso_path = tmp_path / 'horizonos-dev.iso'

    subprocess.run([sys.executable, 'tools/build_developer_iso.py', '--output', str(iso_path)], cwd=ROOT, check=True)
    completed = subprocess.run(
        [sys.executable, 'tools/verify_developer_iso.py', str(iso_path), '--timeout-seconds', '40'],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert 'HORIZONOS_BOOT_OK' in completed.stdout
    assert iso_path.exists()
    assert iso_path.stat().st_size > 0
