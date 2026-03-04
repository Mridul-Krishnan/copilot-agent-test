"""Smoke tests for sysmon widgets and app."""

import re
import pytest

from sysmon.app import SysmonApp, _SPINNER, POLL_INTERVALS
from sysmon.widgets import CpuPanel, IOMetricPanel, MetricPanel, ProcessTable, _human_bytes, _BLOCK_CHARS


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


class TestProcessTable:
    @pytest.mark.asyncio
    async def test_refresh_empty_list(self) -> None:
        from textual.widgets import DataTable
        app = SysmonApp()
        async with app.run_test() as pilot:
            table = app.query_one("#proc-view", ProcessTable)
            table.refresh_processes([])
            dt = table.query_one("#proc-table", DataTable)
            assert dt.row_count == 0

    @pytest.mark.asyncio
    async def test_refresh_valid_row(self) -> None:
        from textual.widgets import DataTable
        app = SysmonApp()
        async with app.run_test() as pilot:
            table = app.query_one("#proc-view", ProcessTable)
            table.refresh_processes([
                {"pid": 1, "name": "init", "cpu_percent": 0.1, "mem_percent": 0.5, "status": "running"}
            ])
            dt = table.query_one("#proc-table", DataTable)
            assert dt.row_count == 1


class TestProcessToggle:
    @pytest.mark.asyncio
    async def test_p_binding_toggles_views(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            main_view = app.query_one("#main-view")
            proc_view = app.query_one("#proc-view")
            # Initial state
            assert main_view.display is True
            assert proc_view.display is False
            assert app._show_processes is False
            # After first press
            await pilot.press("p")
            assert main_view.display is False
            assert proc_view.display is True
            assert app._show_processes is True
            # After second press — back to original
            await pilot.press("p")
            assert main_view.display is True
            assert proc_view.display is False
            assert app._show_processes is False


class TestMetricPanelThresholds:
    @pytest.mark.asyncio
    async def test_ok_class(self) -> None:
        from textual.widgets import ProgressBar
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", MetricPanel)
            bar = panel.query_one("#bar", ProgressBar)

            panel.value = 59.9
            await pilot.pause()
            assert bar.has_class("ok")
            assert not bar.has_class("warn")
            assert not bar.has_class("crit")

            # Also check near-zero value (change from 59.9 so watcher fires)
            panel.value = 1.0
            await pilot.pause()
            assert bar.has_class("ok")

    @pytest.mark.asyncio
    async def test_warn_class(self) -> None:
        from textual.widgets import ProgressBar
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", MetricPanel)
            bar = panel.query_one("#bar", ProgressBar)

            panel.value = 60.0
            await pilot.pause()
            assert bar.has_class("warn")
            assert not bar.has_class("ok")
            assert not bar.has_class("crit")

            panel.value = 84.9
            await pilot.pause()
            assert bar.has_class("warn")

    @pytest.mark.asyncio
    async def test_crit_class(self) -> None:
        from textual.widgets import ProgressBar
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", MetricPanel)
            bar = panel.query_one("#bar", ProgressBar)

            panel.value = 85.1
            await pilot.pause()
            assert bar.has_class("crit")
            assert not bar.has_class("ok")
            assert not bar.has_class("warn")

            panel.value = 100.0
            await pilot.pause()
            assert bar.has_class("crit")


class TestMetricPanelThresholdsPanelClass:
    @pytest.mark.asyncio
    async def test_ok_panel_class(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", MetricPanel)
            panel.value = 59.9
            await pilot.pause()
            assert panel.has_class("ok")
            assert not panel.has_class("warn")
            assert not panel.has_class("crit")

    @pytest.mark.asyncio
    async def test_warn_panel_class(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", MetricPanel)
            panel.value = 60.0
            await pilot.pause()
            assert panel.has_class("warn")
            assert not panel.has_class("ok")
            assert not panel.has_class("crit")

    @pytest.mark.asyncio
    async def test_crit_panel_class(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", MetricPanel)
            panel.value = 85.1
            await pilot.pause()
            assert panel.has_class("crit")
            assert not panel.has_class("ok")
            assert not panel.has_class("warn")


class TestCritLabel:
    @pytest.mark.asyncio
    async def test_crit_label_added(self) -> None:
        from textual.widgets import Label
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", MetricPanel)
            lbl = panel.query_one("#lbl", Label)
            panel.value = 85.1
            await pilot.pause()
            assert lbl.has_class("crit-label")

    @pytest.mark.asyncio
    async def test_crit_label_removed_warn(self) -> None:
        from textual.widgets import Label
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", MetricPanel)
            lbl = panel.query_one("#lbl", Label)
            panel.value = 85.1
            await pilot.pause()
            panel.value = 60.0
            await pilot.pause()
            assert not lbl.has_class("crit-label")

    @pytest.mark.asyncio
    async def test_crit_label_removed_ok(self) -> None:
        from textual.widgets import Label
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", MetricPanel)
            lbl = panel.query_one("#lbl", Label)
            panel.value = 85.1
            await pilot.pause()
            panel.value = 10.0
            await pilot.pause()
            assert not lbl.has_class("crit-label")


class TestCpuPanel:
    @pytest.mark.asyncio
    async def test_cpu_panel_mounts(self) -> None:
        from textual.widgets import Label
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", CpuPanel)
            assert panel is not None
            lbl = panel.query_one("#core-bar", Label)
            assert lbl is not None

    @pytest.mark.asyncio
    async def test_watch_cores_normal(self) -> None:
        from textual.widgets import Label
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", CpuPanel)
            panel.cores = [0.0, 25.0, 50.0, 75.0, 100.0]
            await pilot.pause()
            lbl = panel.query_one("#core-bar", Label)
            expected = "".join(
                _BLOCK_CHARS[min(8, int(v / 100 * 8))]
                for v in [0.0, 25.0, 50.0, 75.0, 100.0]
            )
            assert str(lbl.render()) == expected

    @pytest.mark.asyncio
    async def test_watch_cores_empty(self) -> None:
        from textual.widgets import Label
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", CpuPanel)
            panel.cores = []
            await pilot.pause()
            lbl = panel.query_one("#core-bar", Label)
            assert str(lbl.render()) == ""

    @pytest.mark.asyncio
    async def test_watch_cores_over_100(self) -> None:
        from textual.widgets import Label
        app = SysmonApp()
        async with app.run_test() as pilot:
            panel = app.query_one("#cpu", CpuPanel)
            panel.cores = [200.0]
            await pilot.pause()
            lbl = panel.query_one("#core-bar", Label)
            assert str(lbl.render()) == "█"


class TestSpinnerAndClock:
    @pytest.mark.asyncio
    async def test_spinner_in_header(self) -> None:
        from textual.widgets import Label
        app = SysmonApp()
        async with app.run_test() as pilot:
            app._refresh_stats()
            header = app.query_one("#header-bar", Label)
            text = str(header.render())
            assert any(ch in text for ch in _SPINNER)

    @pytest.mark.asyncio
    async def test_spinner_wraps(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            app._spinner_idx = len(_SPINNER) - 1
            app._refresh_stats()
            assert app._spinner_idx == len(_SPINNER)

    @pytest.mark.asyncio
    async def test_clock_in_header(self) -> None:
        from textual.widgets import Label
        app = SysmonApp()
        async with app.run_test() as pilot:
            app._refresh_stats()
            header = app.query_one("#header-bar", Label)
            text = str(header.render())
            assert re.search(r"\d{2}:\d{2}:\d{2}", text)


class TestPollingRate:
    @pytest.mark.asyncio
    async def test_speed_up_decrements_index(self) -> None:
        from textual.widgets import Label
        app = SysmonApp()
        async with app.run_test() as pilot:
            await pilot.press("+")
            assert app._poll_idx == 1
            footer = app.query_one("#footer-bar", Label)
            assert "[0.5s]" in str(footer.render())

    @pytest.mark.asyncio
    async def test_slow_down_increments_index(self) -> None:
        from textual.widgets import Label
        app = SysmonApp()
        async with app.run_test() as pilot:
            await pilot.press("-")
            assert app._poll_idx == 3
            footer = app.query_one("#footer-bar", Label)
            assert "[2s]" in str(footer.render())

    @pytest.mark.asyncio
    async def test_speed_up_clamped_at_min(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            for _ in range(10):
                await pilot.press("+")
            assert app._poll_idx == 0
            app._timer.stop()  # prevent fast 0.25s timer firing during teardown

    @pytest.mark.asyncio
    async def test_slow_down_clamped_at_max(self) -> None:
        app = SysmonApp()
        async with app.run_test() as pilot:
            for _ in range(10):
                await pilot.press("-")
            assert app._poll_idx == 4

    @pytest.mark.asyncio
    async def test_update_footer_content(self) -> None:
        from textual.widgets import Label
        expected = ["[0.25s]", "[0.5s]", "[1s]", "[2s]", "[5s]"]
        app = SysmonApp()
        async with app.run_test() as pilot:
            for idx, label in enumerate(expected):
                app._poll_idx = idx
                app._update_footer()
                footer = app.query_one("#footer-bar", Label)
                assert label in str(footer.render()), f"Expected {label} at index {idx}"

    @pytest.mark.asyncio
    async def test_on_mount_footer_shows_rate(self) -> None:
        from textual.widgets import Label
        app = SysmonApp()
        async with app.run_test() as pilot:
            footer = app.query_one("#footer-bar", Label)
            assert "[1s]" in str(footer.render())
