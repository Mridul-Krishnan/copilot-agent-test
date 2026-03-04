"""Custom widgets for sysmon."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import DataTable, Label, ProgressBar, Sparkline


class MetricPanel(Widget):
    """A panel showing a metric label, progress bar, and sparkline history."""

    DEFAULT_CSS = """
    MetricPanel {
        height: auto;
        padding: 0 1;
        margin: 0 0 1 0;
    }
    MetricPanel .metric-label {
        text-style: bold;
        margin-bottom: 0;
    }
    MetricPanel ProgressBar {
        margin: 0 0;
    }
    MetricPanel Sparkline {
        height: 2;
        margin: 0 0;
    }
    """

    value: reactive[float] = reactive(0.0)
    history: reactive[list[float]] = reactive(list, always_update=True)
    label_text: reactive[str] = reactive("")
    unit: reactive[str] = reactive("%")

    def __init__(
        self,
        label: str = "",
        unit: str = "%",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.label_text = label
        self.unit = unit
        self.history = []

    def compose(self) -> ComposeResult:
        yield Label(self._format_label(), classes="metric-label", id="lbl")
        yield ProgressBar(total=100, show_eta=False, show_percentage=False, id="bar")
        yield Sparkline(self.history, id="spark")

    def _format_label(self) -> str:
        return f"{self.label_text}: {self.value:.1f}{self.unit}"

    def watch_value(self, new_value: float) -> None:
        try:
            lbl = self.query_one("#lbl", Label)
            lbl.update(self._format_label())
            bar = self.query_one("#bar", ProgressBar)
            bar.animate("progress", max(0, min(new_value, 100)), duration=0.4, easing="out_cubic")
            # Colour-code the bar and panel border based on thresholds
            bar.remove_class("ok", "warn", "crit")
            self.remove_class("ok", "warn", "crit")
            if new_value < 60:
                bar.add_class("ok")
                self.add_class("ok")
                lbl.remove_class("crit-label")
            elif new_value < 85:
                bar.add_class("warn")
                self.add_class("warn")
                lbl.remove_class("crit-label")
            else:
                bar.add_class("crit")
                self.add_class("crit")
                lbl.add_class("crit-label")
        except NoMatches:
            pass

    def watch_history(self, new_history: list[float]) -> None:
        try:
            spark = self.query_one("#spark", Sparkline)
            spark.data = new_history
        except NoMatches:
            pass


_BLOCK_CHARS = " ▁▂▃▄▅▆▇█"


class CpuPanel(MetricPanel):
    """CPU MetricPanel extended with a per-core mini-bar row."""

    cores: reactive[list[float]] = reactive(list, always_update=True)

    def compose(self) -> ComposeResult:
        yield from super().compose()
        yield Label("", classes="core-bar", id="core-bar")

    def watch_cores(self, new_cores: list[float]) -> None:
        try:
            bar_lbl = self.query_one("#core-bar", Label)
            chars = "".join(
                _BLOCK_CHARS[min(8, int(v / 100 * 8))] for v in new_cores
            )
            bar_lbl.update(chars)
        except NoMatches:
            pass


class IOMetricPanel(Widget):
    """A panel for I/O rates (no progress bar — just label + sparkline)."""

    DEFAULT_CSS = """
    IOMetricPanel {
        height: auto;
        padding: 0 1;
        margin: 0 0 1 0;
    }
    IOMetricPanel .metric-label {
        text-style: bold;
        margin-bottom: 0;
    }
    IOMetricPanel Sparkline {
        height: 2;
        margin: 0 0;
    }
    """

    value: reactive[float] = reactive(0.0)
    history: reactive[list[float]] = reactive(list, always_update=True)
    label_text: reactive[str] = reactive("")
    unit: reactive[str] = reactive("B/s")

    def __init__(
        self,
        label: str = "",
        unit: str = "B/s",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.label_text = label
        self.unit = unit
        self.history = []

    def compose(self) -> ComposeResult:
        yield Label(self._format_label(), classes="metric-label", id="lbl")
        yield Sparkline(self.history, id="spark")

    def _format_label(self) -> str:
        return f"{self.label_text}: {_human_bytes(self.value)}/s"

    def watch_value(self, new_value: float) -> None:
        try:
            lbl = self.query_one("#lbl", Label)
            lbl.update(self._format_label())
        except NoMatches:
            pass

    def watch_history(self, new_history: list[float]) -> None:
        try:
            spark = self.query_one("#spark", Sparkline)
            spark.data = new_history
        except NoMatches:
            pass


def _human_bytes(n: float) -> str:
    """Format bytes as a human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


class ProcessTable(Widget):
    """A widget displaying a live process list table."""

    DEFAULT_CSS = """
    ProcessTable {
        height: 1fr;
    }
    ProcessTable DataTable {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        table: DataTable = DataTable(id="proc-table")
        table.add_columns("PID", "Name", "CPU %", "MEM %", "Status")
        yield table

    def refresh_processes(self, rows: list[dict]) -> None:
        try:
            table = self.query_one("#proc-table", DataTable)
            table.clear()
            for proc in rows:
                table.add_row(
                    str(proc["pid"]),
                    proc["name"],
                    f"{proc['cpu_percent']:.1f}",
                    f"{proc['mem_percent']:.1f}",
                    proc["status"],
                )
        except NoMatches:
            pass
