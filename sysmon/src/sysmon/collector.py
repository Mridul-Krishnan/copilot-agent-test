"""System stats collector — wraps psutil into a clean dataclass."""

from __future__ import annotations

import platform
import socket
import time
from dataclasses import dataclass, field

import psutil


@dataclass
class SystemSnapshot:
    """Point-in-time snapshot of system metrics."""

    cpu_percent: list[float] = field(default_factory=list)
    cpu_total: float = 0.0
    ram_percent: float = 0.0
    ram_used_gb: float = 0.0
    ram_total_gb: float = 0.0
    swap_percent: float = 0.0
    disk_read_bytes_sec: float = 0.0
    disk_write_bytes_sec: float = 0.0
    net_sent_bytes_sec: float = 0.0
    net_recv_bytes_sec: float = 0.0
    hostname: str = ""
    os_name: str = ""
    uptime_seconds: float = 0.0


# Module-level state for computing I/O deltas.
# NOTE: assumes single-threaded usage (Textual's set_interval runs on the main thread).
_prev_disk: psutil._common.sdiskio | None = None
_prev_net: psutil._common.snetio | None = None
_prev_time: float | None = None


def collect() -> SystemSnapshot:
    """Sample current system stats and return a snapshot.

    I/O rates are computed as deltas from the previous call.  The first call
    will report 0 for all rate-based metrics.
    """
    global _prev_disk, _prev_net, _prev_time

    now = time.monotonic()

    # CPU
    cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
    cpu_total = psutil.cpu_percent(interval=None)

    # Memory
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    # Disk I/O — disk_io_counters() can return None in VMs/containers
    disk = psutil.disk_io_counters()
    disk_read_rate = 0.0
    disk_write_rate = 0.0
    if disk is not None and _prev_disk is not None and _prev_time is not None:
        dt = now - _prev_time
        if dt > 0:
            disk_read_rate = max(0.0, (disk.read_bytes - _prev_disk.read_bytes) / dt)
            disk_write_rate = max(0.0, (disk.write_bytes - _prev_disk.write_bytes) / dt)

    # Network I/O — net_io_counters() can return None in some environments
    net = psutil.net_io_counters()
    net_sent_rate = 0.0
    net_recv_rate = 0.0
    if net is not None and _prev_net is not None and _prev_time is not None:
        dt = now - _prev_time
        if dt > 0:
            net_sent_rate = max(0.0, (net.bytes_sent - _prev_net.bytes_sent) / dt)
            net_recv_rate = max(0.0, (net.bytes_recv - _prev_net.bytes_recv) / dt)

    # Update previous state (may be None — that's fine)
    _prev_disk = disk
    _prev_net = net
    _prev_time = now

    return SystemSnapshot(
        cpu_percent=cpu_percent,
        cpu_total=cpu_total,
        ram_percent=mem.percent,
        ram_used_gb=mem.used / (1024**3),
        ram_total_gb=mem.total / (1024**3),
        swap_percent=swap.percent,
        disk_read_bytes_sec=disk_read_rate,
        disk_write_bytes_sec=disk_write_rate,
        net_sent_bytes_sec=net_sent_rate,
        net_recv_bytes_sec=net_recv_rate,
        hostname=socket.gethostname(),
        os_name=platform.system(),
        uptime_seconds=time.time() - psutil.boot_time(),
    )


def reset() -> None:
    """Reset module-level state (useful for tests)."""
    global _prev_disk, _prev_net, _prev_time
    _prev_disk = None
    _prev_net = None
    _prev_time = None


def collect_processes(n: int = 25) -> list[dict]:
    """Return the top-n processes by CPU usage.

    Each entry is a dict with keys: pid, name, cpu_percent, mem_percent, status.
    Permission and disappearing-process errors are silently skipped.
    """
    procs: list[dict] = []
    attrs = ["pid", "name", "cpu_percent", "memory_percent", "status"]
    for proc in psutil.process_iter(attrs):
        try:
            info = proc.info  # type: ignore[attr-defined]
            procs.append(
                {
                    "pid": info["pid"],
                    "name": info["name"] or "",
                    "cpu_percent": info["cpu_percent"] or 0.0,
                    "mem_percent": info["memory_percent"] or 0.0,
                    "status": info["status"] or "",
                }
            )
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
    procs.sort(key=lambda p: p["cpu_percent"], reverse=True)
    return procs[:n]
