"""PySide6 GUI for Reverse Pomodoro — dark-mode, reliable focus/blink."""

import sys
import time
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from reverse_pomodoro.minigame import DodgeGame

from reverse_pomodoro.log import (
    append_entry,
    count_completed_work_sessions,
    load_log,
)

_BG = "#12121f"
_WORK_ACCENT = "#ff6b35"
_BREAK_ACCENT = "#00b4d8"
_TEXT = "#e0e0e0"
_BLINK_STEPS = 16  # 8 pairs × 2


_BASE_STYLESHEET = """
QMainWindow, QWidget#central {{
    background-color: {bg};
}}
QLabel#session {{
    color: {text};
    font-size: 15pt;
    font-weight: bold;
}}
QLabel#countdown {{
    color: {text};
    font-size: 54pt;
    font-weight: bold;
}}
QProgressBar {{
    background-color: #2a2a3d;
    border: none;
    border-radius: 5px;
    height: 14px;
}}
QProgressBar::chunk {{
    background-color: {accent};
    border-radius: 5px;
}}
QPushButton#next_btn {{
    background-color: {accent};
    color: #ffffff;
    font-size: 13pt;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 8px 24px;
}}
QPushButton#next_btn:hover {{
    background-color: {accent_hover};
}}
QLabel#hints {{
    color: #888888;
    font-size: 9pt;
    font-style: italic;
}}
"""


def _make_stylesheet(bg: str, accent: str) -> str:
    # darken accent slightly for hover
    return _BASE_STYLESHEET.format(
        bg=bg, text=_TEXT, accent=accent, accent_hover=accent
    )


class PomodoroApp(QMainWindow):
    def __init__(self, args) -> None:
        # Ensure a QApplication exists
        self._app = QApplication.instance() or QApplication(sys.argv)

        super().__init__()
        self.args = args

        self._log = load_log(args.log_file)
        self._completed = count_completed_work_sessions(self._log)
        self._session_start: float | None = None
        self._total_secs: int = 0
        self._session_type: str = "work"
        self._partial_entry: dict | None = None

        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(1000)
        self._tick_timer.timeout.connect(self._on_tick)
        self._remaining: int = 0

        self._blink_timer = QTimer(self)
        self._blink_timer.setInterval(500)
        self._blink_timer.timeout.connect(self._on_blink)
        self._blink_count: int = 0
        self._blink_accent: str = _WORK_ACCENT

        self._build_ui()
        self.setWindowTitle("Reverse Pomodoro")
        self.resize(420, 580)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(10)

        self._label_session = QLabel("")
        self._label_session.setObjectName("session")
        layout.addWidget(self._label_session)

        self._label_time = QLabel("00:00")
        self._label_time.setObjectName("countdown")
        layout.addWidget(self._label_time)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        layout.addWidget(self._progress)

        self._minigame = DodgeGame()
        self._minigame.hide()
        layout.addWidget(self._minigame)

        self._btn_next = QPushButton("▶ Next")
        self._btn_next.setObjectName("next_btn")
        self._btn_next.setEnabled(False)
        self._btn_next.hide()
        self._btn_next.clicked.connect(self._advance)
        layout.addWidget(self._btn_next)

        self._label_hints = QLabel("[+/-] time  [R] reset  [Shift+R] full reset  [N/↵] next")
        self._label_hints.setObjectName("hints")
        layout.addWidget(self._label_hints)

        self._set_accent(_WORK_ACCENT)

    def _set_accent(self, accent: str) -> None:
        self.setStyleSheet(_make_stylesheet(_BG, accent))

    def _set_bg(self, bg: str) -> None:
        accent = self._blink_accent
        self.setStyleSheet(_make_stylesheet(bg, accent))

    # ------------------------------------------------------------------
    # Session logic
    # ------------------------------------------------------------------

    def _calc_work_secs(self) -> int:
        mins = min(
            self.args.work + self._completed * self.args.increment,
            self.args.max_duration,
        )
        return mins * 60

    def _start_work(self) -> None:
        self._blink_accent = _WORK_ACCENT
        self._set_accent(_WORK_ACCENT)
        self._btn_next.hide()
        self._btn_next.setEnabled(False)

        self._minigame.stop()
        self._minigame.hide()
        self._label_hints.setText("[+/-] time  [R] reset  [Shift+R] full reset  [N/↵] next")

        self._total_secs = self._calc_work_secs()
        work_mins = self._total_secs // 60
        self._label_session.setText(f"🍅 Work #{self._completed + 1} — {work_mins}m")
        self._session_type = "work"
        self._session_start = time.time()
        self._partial_entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "type": "work",
            "planned_duration": self._total_secs,
        }
        self._remaining = self._total_secs
        self._update_display()
        self._tick_timer.start()
        QTimer.singleShot(100, self._shrink_to_default)

    def _start_break(self) -> None:
        self._blink_accent = _BREAK_ACCENT
        self._set_accent(_BREAK_ACCENT)
        self._btn_next.hide()
        self._btn_next.setEnabled(False)

        self._minigame.show()
        self._minigame.start()
        self._label_hints.setText("[←/→] dodge  [+/-] time  [R] reset  [Shift+R] full reset  [N/↵] next")

        self._total_secs = self.args.break_duration * 60
        self._label_session.setText(f"☕ Break — {self.args.break_duration}m")
        self._session_type = "break"
        self._session_start = time.time()
        self._partial_entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "type": "break",
            "planned_duration": self._total_secs,
        }
        self._remaining = self._total_secs
        self._update_display()
        self._tick_timer.start()
        QTimer.singleShot(100, self._shrink_to_default)

    def _shrink_to_default(self) -> None:
        self.showNormal()
        self.resize(420, 580)

    def _update_display(self) -> None:
        mins, secs = divmod(self._remaining, 60)
        self._label_time.setText(f"{mins:02d}:{secs:02d}")
        if self._total_secs > 0:
            pct = int(100 * (self._total_secs - self._remaining) / self._total_secs)
            self._progress.setValue(pct)

    def _on_tick(self) -> None:
        if self._remaining > 0:
            self._remaining -= 1
            self._update_display()
        if self._remaining == 0:
            self._tick_timer.stop()
            self._on_complete()

    def _on_complete(self) -> None:
        elapsed = int(time.time() - self._session_start) if self._session_start else self._total_secs
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "type": self._session_type,
            "planned_duration": self._total_secs,
            "actual_duration": elapsed,
            "completed": True,
        }
        append_entry(self.args.log_file, entry)
        self._partial_entry = None

        if self._session_type == "work":
            self._completed += 1

        # Hide mini-game when break ends
        if self._session_type == "break":
            self._minigame.stop()
            self._minigame.hide()

        # Grab attention — reliable on X11/Wayland/macOS/Windows
        self.showNormal()
        self.showMaximized()
        self.raise_()
        self.activateWindow()
        QApplication.alert(self, 0)

        # Start blink
        self._blink_count = _BLINK_STEPS
        self._blink_timer.start()

    def _on_blink(self) -> None:
        if self._blink_count == 0:
            self._blink_timer.stop()
            self._set_accent(self._blink_accent)
            self._btn_next.show()
            self._btn_next.setEnabled(True)
            return
        if self._blink_count % 2 == 0:
            self._set_bg(self._blink_accent)
        else:
            self._set_bg(_BG)
        self._blink_count -= 1

    def _advance(self) -> None:
        """Called when user clicks ▶ Next or presses N/↵/Space."""
        # If called mid-session, save partial entry and stop timers
        if self._tick_timer.isActive():
            self._tick_timer.stop()
            if self._partial_entry is not None and self._session_start is not None:
                elapsed = int(time.time() - self._session_start)
                entry = {**self._partial_entry, "actual_duration": elapsed, "completed": False}
                append_entry(self.args.log_file, entry)
                self._partial_entry = None
        self._blink_timer.stop()
        if self._session_type == "work":
            self._start_break()
        else:
            self._start_work()

    def _reset_session(self) -> None:
        """Restart current session from full planned duration."""
        if self._partial_entry is not None and self._session_start is not None:
            elapsed = int(time.time() - self._session_start)
            entry = {**self._partial_entry, "actual_duration": elapsed, "completed": False}
            append_entry(self.args.log_file, entry)
            self._partial_entry = None
        self._blink_timer.stop()
        self._tick_timer.stop()
        if self._session_type == "work":
            self._start_work()
        else:
            self._start_break()

    def _full_reset(self) -> None:
        """Save partial entry as incomplete, reset counter, restart from Work #1."""
        if self._partial_entry is not None and self._session_start is not None:
            elapsed = int(time.time() - self._session_start)
            entry = {**self._partial_entry, "actual_duration": elapsed, "completed": False}
            append_entry(self.args.log_file, entry)
            self._partial_entry = None
        self._tick_timer.stop()
        self._blink_timer.stop()
        self._completed = 0
        self._start_work()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        key = event.key()
        if key in (Qt.Key_Plus, Qt.Key_Equal):
            if self._tick_timer.isActive():
                self._remaining = min(self._remaining + 60, 3600)
                self._update_display()
        elif key == Qt.Key_Minus:
            if self._tick_timer.isActive():
                self._remaining = max(self._remaining - 60, 1)
                self._update_display()
        elif key == Qt.Key_R:
            if event.modifiers() & Qt.ShiftModifier:
                self._full_reset()
            else:
                self._reset_session()
        elif key in (Qt.Key_N, Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self._advance()
        elif key == Qt.Key_Left:
            if self._session_type == "break":
                self._minigame.move_left()
        elif key == Qt.Key_Right:
            if self._session_type == "break":
                self._minigame.move_right()
        else:
            super().keyPressEvent(event)

    # ------------------------------------------------------------------
    # Window close — save partial entry if mid-session
    # ------------------------------------------------------------------

    def closeEvent(self, event) -> None:  # noqa: N802
        self._tick_timer.stop()
        self._blink_timer.stop()
        if self._partial_entry is not None and self._session_start is not None:
            elapsed = int(time.time() - self._session_start)
            entry = {**self._partial_entry, "actual_duration": elapsed, "completed": False}
            append_entry(self.args.log_file, entry)
            self._partial_entry = None
        event.accept()

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        self.show()
        self._start_work()
        sys.exit(self._app.exec())
