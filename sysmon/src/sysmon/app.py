"""Main Textual app for sysmon."""

from __future__ import annotations

import datetime
from collections import deque

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.timer import Timer
from textual.widgets import Label

from sysmon.collector import collect, collect_processes
from sysmon.theme import SYSMON_CSS
from sysmon.widgets import CpuPanel, IOMetricPanel, MetricPanel, ProcessTable

HISTORY_LEN = 60
_SPINNER = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
POLL_INTERVALS = [0.25, 0.5, 1.0, 2.0, 5.0]


class SysmonApp(App):
    """Live system monitor TUI."""

    CSS = SYSMON_CSS

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("t", "toggle_theme", "Toggle theme"),
        Binding("p", "toggle_processes", "Processes"),
        Binding("+", "speed_up", "Faster"),
        Binding("=", "speed_up", "Faster"),
        Binding("-", "slow_down", "Slower"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._dark_mode = True
        self._show_processes: bool = False
        self._spinner_idx: int = 0
        self._poll_idx: int = 2
        self._timer: Timer | None = None
        # 60-second history deques
        self._cpu_hist: deque[float] = deque(maxlen=HISTORY_LEN)
        self._ram_hist: deque[float] = deque(maxlen=HISTORY_LEN)
        self._swap_hist: deque[float] = deque(maxlen=HISTORY_LEN)
        self._disk_r_hist: deque[float] = deque(maxlen=HISTORY_LEN)
        self._disk_w_hist: deque[float] = deque(maxlen=HISTORY_LEN)
        self._net_s_hist: deque[float] = deque(maxlen=HISTORY_LEN)
        self._net_r_hist: deque[float] = deque(maxlen=HISTORY_LEN)

    def compose(self) -> ComposeResult:
        yield Label("sysmon", id="header-bar")
        with Container(classes="panels-grid", id="main-view"):
            yield CpuPanel("CPU", "%", id="cpu")
            yield MetricPanel("RAM", "%", id="ram")
            yield MetricPanel("Swap", "%", id="swap")
            yield IOMetricPanel("Disk Read", id="disk-r")
            yield IOMetricPanel("Disk Write", id="disk-w")
            yield IOMetricPanel("Net Send", id="net-s")
            yield IOMetricPanel("Net Recv", id="net-r")
        yield ProcessTable(id="proc-view")
        yield Label("q Quit  t Theme  p Processes  +/- Speed", id="footer-bar")

    def on_mount(self) -> None:
        # Initial collection to prime psutil counters
        collect()
        self._timer = self.set_interval(POLL_INTERVALS[self._poll_idx], self._refresh_stats)
        self._update_footer()

    def _refresh_stats(self) -> None:
        snap = collect()

        # Header with host info, live clock, and spinner
        uptime = str(datetime.timedelta(seconds=int(snap.uptime_seconds)))
        now = datetime.datetime.now().strftime("%H:%M:%S")
        spinner = _SPINNER[self._spinner_idx % len(_SPINNER)]
        self._spinner_idx += 1
        header = self.query_one("#header-bar", Label)
        header.update(
            f"  {spinner} sysmon │ {snap.hostname} │ {snap.os_name} │ up {uptime} │ {now}"
        )

        # CPU
        self._cpu_hist.append(snap.cpu_total)
        cpu = self.query_one("#cpu", CpuPanel)
        cpu.value = snap.cpu_total
        cpu.history = list(self._cpu_hist)
        cpu.cores = snap.cpu_percent

        # RAM
        self._ram_hist.append(snap.ram_percent)
        ram = self.query_one("#ram", MetricPanel)
        ram.label_text = f"RAM ({snap.ram_used_gb:.1f}/{snap.ram_total_gb:.1f} GB)"
        ram.value = snap.ram_percent
        ram.history = list(self._ram_hist)

        # Swap
        self._swap_hist.append(snap.swap_percent)
        swap = self.query_one("#swap", MetricPanel)
        swap.value = snap.swap_percent
        swap.history = list(self._swap_hist)

        # Disk I/O
        self._disk_r_hist.append(snap.disk_read_bytes_sec)
        dr = self.query_one("#disk-r", IOMetricPanel)
        dr.value = snap.disk_read_bytes_sec
        dr.history = list(self._disk_r_hist)

        self._disk_w_hist.append(snap.disk_write_bytes_sec)
        dw = self.query_one("#disk-w", IOMetricPanel)
        dw.value = snap.disk_write_bytes_sec
        dw.history = list(self._disk_w_hist)

        # Network I/O
        self._net_s_hist.append(snap.net_sent_bytes_sec)
        ns = self.query_one("#net-s", IOMetricPanel)
        ns.value = snap.net_sent_bytes_sec
        ns.history = list(self._net_s_hist)

        self._net_r_hist.append(snap.net_recv_bytes_sec)
        nr = self.query_one("#net-r", IOMetricPanel)
        nr.value = snap.net_recv_bytes_sec
        nr.history = list(self._net_r_hist)

        # Process table (only refresh when visible)
        if self._show_processes:
            rows = collect_processes()
            self.query_one("#proc-view", ProcessTable).refresh_processes(rows)
        self._update_footer()

    def _update_footer(self) -> None:
        rate = POLL_INTERVALS[self._poll_idx]
        rate_str = f"{rate:g}s"
        footer = self.query_one("#footer-bar", Label)
        footer.update(f"q Quit  t Theme  p Processes  +/- Speed [{rate_str}]")

    def action_speed_up(self) -> None:
        if self._poll_idx > 0:
            self._poll_idx -= 1
            self._restart_timer()

    def action_slow_down(self) -> None:
        if self._poll_idx < len(POLL_INTERVALS) - 1:
            self._poll_idx += 1
            self._restart_timer()

    def _restart_timer(self) -> None:
        if self._timer is not None:
            self._timer.stop()
        self._timer = self.set_interval(POLL_INTERVALS[self._poll_idx], self._refresh_stats)
        self._update_footer()

    def action_toggle_processes(self) -> None:
        self._show_processes = not self._show_processes
        self.query_one("#main-view").display = not self._show_processes
        self.query_one("#proc-view").display = self._show_processes

    def action_toggle_theme(self) -> None:
        self._dark_mode = not self._dark_mode
        self.theme = "textual-dark" if self._dark_mode else "textual-light"


def main() -> None:
    """Entry point for the sysmon CLI."""
    app = SysmonApp()
    app.run()


if __name__ == "__main__":
    main()
