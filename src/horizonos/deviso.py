from __future__ import annotations

import gzip
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KERNEL_PATH = Path('/boot/vmlinuz')
DEFAULT_SOURCE_DATE_EPOCH = '1704067200'
DEFAULT_ISO_BASENAME = 'horizonos-dev-x86_64'
REQUIRED_TOOLS = (
    'busybox',
    'cpio',
    'grub-mkrescue',
    'gzip',
    'xorriso',
)


@dataclass(frozen=True)
class DevIsoBuildRequest:
    output_path: Path
    kernel_path: Path = DEFAULT_KERNEL_PATH
    volume_id: str = 'HORIZONOS_DEV'
    source_date_epoch: str = DEFAULT_SOURCE_DATE_EPOCH
    menu_label: str = 'HorizonOS Developer ISO'
    root_label: str = 'horizonos-dev'


@dataclass(frozen=True)
class DevIsoBuildResult:
    iso_path: Path
    kernel_path: Path
    initrd_path: Path
    grub_config_path: Path
    volume_id: str


class DevIsoBuildError(RuntimeError):
    pass


INIT_SCRIPT = """#!/bin/sh
export PATH=/bin
mount -t devtmpfs devtmpfs /dev 2>/dev/null || true
mount -t proc proc /proc
mount -t sysfs sysfs /sys
printf '%s\n' 'HORIZONOS_BOOT_OK'
printf '%s\n' 'HorizonOS developer environment is running from initramfs.'
printf '%s\n' 'Type exit to trigger a controlled poweroff.'
/bin/sh
poweroff -f
"""


def _require_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise DevIsoBuildError(
            f"Required tool '{name}' is not installed. Install it and rerun the build."
        )


def _run(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    completed = subprocess.run(command, cwd=cwd, env=env, check=False, text=True, capture_output=True)
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or 'command failed without output'
        raise DevIsoBuildError(f"Command failed ({' '.join(command)}): {message}")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8', newline='\n')


def _set_tree_timestamps(root: Path, epoch_seconds: int) -> None:
    for path in sorted([root, *root.rglob('*')]):
        os.utime(path, (epoch_seconds, epoch_seconds), follow_symlinks=False)


def _copy_busybox(initrd_root: Path) -> None:
    busybox_path = Path(shutil.which('busybox') or '')
    if not busybox_path.exists():
        raise DevIsoBuildError('busybox was not found after tool validation.')
    target = initrd_root / 'bin' / 'busybox'
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(busybox_path, target)
    for applet in ('echo', 'mount', 'poweroff', 'sh'):
        link_path = initrd_root / 'bin' / applet
        if link_path.exists() or link_path.is_symlink():
            link_path.unlink()
        link_path.symlink_to('busybox')


def _build_initrd(initrd_root: Path, output_path: Path, source_date_epoch: str) -> None:
    _copy_busybox(initrd_root)
    for directory in ('dev', 'proc', 'sys'):
        (initrd_root / directory).mkdir(parents=True, exist_ok=True)
    init_path = initrd_root / 'init'
    _write_text(init_path, INIT_SCRIPT)
    init_path.chmod(0o755)

    file_list = sorted(path.relative_to(initrd_root).as_posix() for path in initrd_root.rglob('*'))
    manifest = ''.join(f'{item}\n' for item in ['.', *file_list])
    cpio = subprocess.Popen(
        ['cpio', '--create', '--format=newc'],
        cwd=initrd_root,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, 'LC_ALL': 'C', 'SOURCE_DATE_EPOCH': source_date_epoch},
    )
    stdout, stderr = cpio.communicate(manifest.encode('utf-8'))
    if cpio.returncode != 0:
        raise DevIsoBuildError(f"cpio failed while creating the initrd: {stderr.decode('utf-8', errors='replace').strip()}")

    with gzip.GzipFile(filename='', mode='wb', fileobj=output_path.open('wb'), mtime=0) as handle:
        handle.write(stdout)


def _write_grub_config(path: Path, request: DevIsoBuildRequest) -> None:
    content = f"""set timeout=0
set default=0
serial --speed=115200
terminal_input console serial
terminal_output console serial
menuentry '{request.menu_label}' {{
    linux /boot/vmlinuz console=ttyS0,115200 printk.time=0 quiet root=/dev/ram0 rootfstype=ramfs horizonos.root_label={request.root_label}
    initrd /boot/initrd.img
}}
"""
    _write_text(path, content)


def build_developer_iso(request: DevIsoBuildRequest) -> DevIsoBuildResult:
    for tool in REQUIRED_TOOLS:
        _require_tool(tool)
    if not request.kernel_path.exists():
        raise DevIsoBuildError(
            f'Kernel image not found at {request.kernel_path}. Install a Linux kernel package or provide --kernel-path.'
        )

    request.output_path.parent.mkdir(parents=True, exist_ok=True)
    epoch = int(request.source_date_epoch)
    env = {**os.environ, 'LC_ALL': 'C', 'SOURCE_DATE_EPOCH': request.source_date_epoch}

    with TemporaryDirectory(prefix='horizonos-deviso-') as temp_dir:
        temp_root = Path(temp_dir)
        iso_root = temp_root / 'iso-root'
        boot_root = iso_root / 'boot'
        boot_root.mkdir(parents=True, exist_ok=True)
        initrd_root = temp_root / 'initrd-root'
        grub_config_path = boot_root / 'grub' / 'grub.cfg'
        initrd_path = boot_root / 'initrd.img'
        kernel_output = boot_root / 'vmlinuz'

        shutil.copy2(request.kernel_path, kernel_output)
        _build_initrd(initrd_root, initrd_path, request.source_date_epoch)
        _write_grub_config(grub_config_path, request)
        _set_tree_timestamps(temp_root, epoch)

        _run(
            ['grub-mkrescue', '-o', str(request.output_path), '-volid', request.volume_id, str(iso_root)],
            env=env,
        )
        os.utime(request.output_path, (epoch, epoch))

        return DevIsoBuildResult(
            iso_path=request.output_path,
            kernel_path=kernel_output,
            initrd_path=initrd_path,
            grub_config_path=grub_config_path,
            volume_id=request.volume_id,
        )


__all__ = [
    'DEFAULT_ISO_BASENAME',
    'DEFAULT_SOURCE_DATE_EPOCH',
    'DevIsoBuildError',
    'DevIsoBuildRequest',
    'DevIsoBuildResult',
    'build_developer_iso',
]
