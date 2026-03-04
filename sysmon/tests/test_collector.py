"""Unit tests for the collector module."""

import time
from unittest.mock import MagicMock, PropertyMock, patch

import psutil
import pytest

from sysmon.collector import SystemSnapshot, collect, collect_processes, reset


class TestCollector:
    def setup_method(self) -> None:
        reset()

    def test_collect_returns_snapshot(self) -> None:
        snap = collect()
        assert isinstance(snap, SystemSnapshot)

    def test_cpu_percent_populated(self) -> None:
        snap = collect()
        assert len(snap.cpu_percent) > 0
        assert all(isinstance(v, float) for v in snap.cpu_percent)

    def test_ram_total_positive(self) -> None:
        snap = collect()
        assert snap.ram_total_gb > 0

    def test_hostname_and_os(self) -> None:
        snap = collect()
        assert len(snap.hostname) > 0
        assert len(snap.os_name) > 0

    def test_uptime_positive(self) -> None:
        snap = collect()
        assert snap.uptime_seconds > 0

    def test_io_rates_after_two_calls(self) -> None:
        collect()  # first call primes the counters
        time.sleep(0.1)
        snap = collect()
        # I/O rates should be numeric (may be 0 if no activity, but not None)
        assert isinstance(snap.disk_read_bytes_sec, float)
        assert isinstance(snap.disk_write_bytes_sec, float)
        assert isinstance(snap.net_sent_bytes_sec, float)
        assert isinstance(snap.net_recv_bytes_sec, float)

    def test_cpu_total_in_range(self) -> None:
        snap = collect()
        assert 0 <= snap.cpu_total <= 100

    def test_swap_percent_non_negative(self) -> None:
        snap = collect()
        assert snap.swap_percent >= 0

    def test_io_rates_non_negative(self) -> None:
        collect()
        time.sleep(0.1)
        snap = collect()
        assert snap.disk_read_bytes_sec >= 0
        assert snap.disk_write_bytes_sec >= 0
        assert snap.net_sent_bytes_sec >= 0
        assert snap.net_recv_bytes_sec >= 0


class TestCollectProcesses:
    def _make_proc(self, pid: int, name: str, cpu: float, mem: float, status: str = "running") -> MagicMock:
        proc = MagicMock()
        proc.info = {"pid": pid, "name": name, "cpu_percent": cpu, "memory_percent": mem, "status": status}
        return proc

    def test_returns_list_of_dicts(self) -> None:
        result = collect_processes()
        assert isinstance(result, list)
        for item in result:
            assert "pid" in item
            assert "name" in item
            assert "cpu_percent" in item
            assert "mem_percent" in item
            assert "status" in item

    def test_sorted_by_cpu_descending(self) -> None:
        p1 = self._make_proc(1, "low", 5.0, 1.0)
        p2 = self._make_proc(2, "high", 80.0, 2.0)
        with patch("psutil.process_iter", return_value=[p1, p2]):
            result = collect_processes()
        assert result[0]["cpu_percent"] == 80.0
        assert result[1]["cpu_percent"] == 5.0

    def test_respects_n_limit(self) -> None:
        procs = [self._make_proc(i, f"p{i}", float(i), 0.1) for i in range(30)]
        with patch("psutil.process_iter", return_value=procs):
            result = collect_processes(n=5)
        assert len(result) <= 5

    def test_access_denied_skipped(self) -> None:
        proc = MagicMock()
        type(proc).info = PropertyMock(side_effect=psutil.AccessDenied(pid=99))
        with patch("psutil.process_iter", return_value=[proc]):
            result = collect_processes()
        assert result == []

    def test_no_such_process_skipped(self) -> None:
        proc = MagicMock()
        type(proc).info = PropertyMock(side_effect=psutil.NoSuchProcess(pid=99))
        with patch("psutil.process_iter", return_value=[proc]):
            result = collect_processes()
        assert result == []

    def test_zombie_process_skipped(self) -> None:
        proc = MagicMock()
        type(proc).info = PropertyMock(side_effect=psutil.ZombieProcess(pid=99))
        with patch("psutil.process_iter", return_value=[proc]):
            result = collect_processes()
        assert result == []
