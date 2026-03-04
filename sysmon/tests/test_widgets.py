"""Smoke tests for sysmon widgets and app."""

import pytest

from sysmon.app import SysmonApp
from sysmon.widgets import IOMetricPanel, MetricPanel, _human_bytes


class TestAppSmoke:
    def test_app_instantiation(self) -> None:
        app = SysmonApp()
        assert app is not None

    @pytest.mark.asyncio
    async def test_app_mounts(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            assert app.query("MetricPanel")
            assert app.query("IOMetricPanel")

    @pytest.mark.asyncio
    async def test_quit_binding(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            await pilot.press("q")
            assert app._exit


class TestHumanBytes:
    def test_zero(self) -> None:
        assert _human_bytes(0) == "0.0 B"

    def test_sub_kb(self) -> None:
        assert _human_bytes(512) == "512.0 B"

    def test_exact_kb(self) -> None:
        assert _human_bytes(1024) == "1.0 KB"

    def test_exact_mb(self) -> None:
        assert _human_bytes(1024**2) == "1.0 MB"

    def test_exact_gb(self) -> None:
        assert _human_bytes(1024**3) == "1.0 GB"

    def test_exact_tb(self) -> None:
        assert _human_bytes(1024**4) == "1.0 TB"

    def test_negative(self) -> None:
        # Should not crash; negative values are handled via abs() in the loop
        result = _human_bytes(-500)
        assert "B" in result


class TestIOMetricPanel:
    @pytest.mark.asyncio
    async def test_io_panel_renders_label(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#disk-r", IOMetricPanel)
            assert panel is not None
            # Default value is 0 → label should contain "0.0 B/s"
            assert "0.0 B" in panel._format_label()

    @pytest.mark.asyncio
    async def test_io_panel_value_updates_label(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#disk-r", IOMetricPanel)
            panel.value = 2048.0
            assert "2.0 KB" in panel._format_label()

    @pytest.mark.asyncio
    async def test_io_panel_history_updates_sparkline(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#disk-r", IOMetricPanel)
            panel.history = [1.0, 2.0, 3.0]
            from textual.widgets import Sparkline
            spark = panel.query_one("#spark", Sparkline)
            assert spark.data == [1.0, 2.0, 3.0]


class TestThemeToggle:
    @pytest.mark.asyncio
    async def test_theme_toggle(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            assert app._dark_mode is True
            assert app.theme == "textual-dark"
            await pilot.press("t")
            assert app._dark_mode is False
            assert app.theme == "textual-light"
