"""Unit tests for the collector module."""

import time

from sysmon.collector import SystemSnapshot, collect, reset


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
