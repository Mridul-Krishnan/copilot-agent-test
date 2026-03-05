"""Headless unit tests for PySide6 GUI logic.

Run with: QT_QPA_PLATFORM=offscreen uv run pytest tests/test_gui.py
The session-scoped fixture sets the env var automatically.
"""

import json
import os
import sys
import time
import types
from unittest.mock import MagicMock

import pytest


@pytest.fixture(scope="session", autouse=True)
def offscreen_qt():
    """Force Qt to use the offscreen platform — no display required."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    yield app


def _make_args(**overrides):
    defaults = dict(
        work=5,
        max_duration=25,
        increment=5,
        break_duration=5,
        log_file="/tmp/test_pomodoro_gui.json",
    )
    defaults.update(overrides)
    return types.SimpleNamespace(**defaults)


@pytest.fixture(autouse=True)
def clean_log():
    path = "/tmp/test_pomodoro_gui.json"
    yield
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def app(qapp):
    from reverse_pomodoro.gui import PomodoroApp
    a = PomodoroApp(_make_args())
    yield a
    a._tick_timer.stop()
    a._blink_timer.stop()
    a._partial_entry = None  # prevent log write on destroy


# ------------------------------------------------------------------
# T4-1: _calc_work_secs progression and cap
# ------------------------------------------------------------------

def test_calc_work_secs_initial(app):
    assert app._calc_work_secs() == 5 * 60


def test_calc_work_secs_progression(app):
    app._completed = 2
    assert app._calc_work_secs() == (5 + 2 * 5) * 60  # 15 min


def test_calc_work_secs_cap(app):
    app._completed = 100  # would be way over max
    assert app._calc_work_secs() == 25 * 60  # capped at max_duration=25


# ------------------------------------------------------------------
# T4-2: closeEvent saves partial entry
# ------------------------------------------------------------------

def test_on_close_saves_partial_entry(qapp, tmp_path):
    from reverse_pomodoro.gui import PomodoroApp

    log_file = str(tmp_path / "log.json")
    a = PomodoroApp(_make_args(log_file=log_file))
    a._partial_entry = {
        "timestamp": "2024-01-01T10:00:00",
        "type": "work",
        "planned_duration": 300,
    }
    a._session_start = time.time() - 60  # 60 s in

    mock_event = MagicMock()
    a.closeEvent(mock_event)

    mock_event.accept.assert_called_once()

    with open(log_file) as f:
        entries = json.load(f)
    assert len(entries) == 1
    assert entries[0]["completed"] is False
    assert entries[0]["type"] == "work"
    assert entries[0]["actual_duration"] >= 60


# ------------------------------------------------------------------
# T4-3: _on_complete logs entry and clears _partial_entry
# ------------------------------------------------------------------

def test_on_complete_logs_entry(qapp, tmp_path):
    import time
    from reverse_pomodoro.gui import PomodoroApp

    log_file = str(tmp_path / "log.json")
    a = PomodoroApp(_make_args(log_file=log_file))
    a._tick_timer.stop()
    a._blink_timer.stop()

    a._session_type = "work"
    a._total_secs = 300
    a._session_start = time.time() - 300
    a._partial_entry = {
        "timestamp": "2024-01-01T10:00:00",
        "type": "work",
        "planned_duration": 300,
    }
    prev_completed = a._completed

    a._on_complete()
    a._blink_timer.stop()  # stop the blink that _on_complete started

    with open(log_file) as f:
        entries = json.load(f)

    assert len(entries) == 1
    assert entries[0]["completed"] is True
    assert entries[0]["type"] == "work"
    assert a._partial_entry is None
    assert a._completed == prev_completed + 1


# ------------------------------------------------------------------
# T4-4: _advance routing
# ------------------------------------------------------------------

def test_advance_work_to_break(qapp, tmp_path):
    from reverse_pomodoro.gui import PomodoroApp

    log_file = str(tmp_path / "log.json")
    a = PomodoroApp(_make_args(log_file=log_file))
    a._tick_timer.stop()

    a._session_type = "work"
    a._advance()
    a._tick_timer.stop()

    assert a._session_type == "break"


def test_advance_break_to_work(qapp, tmp_path):
    from reverse_pomodoro.gui import PomodoroApp

    log_file = str(tmp_path / "log.json")
    a = PomodoroApp(_make_args(log_file=log_file))
    a._tick_timer.stop()

    a._session_type = "break"
    a._advance()
    a._tick_timer.stop()

    assert a._session_type == "work"


# ------------------------------------------------------------------
# Keyboard shortcuts
# ------------------------------------------------------------------

def test_key_plus_increments_remaining(app):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtCore import QEvent

    app._tick_timer.start()
    app._remaining = 300
    evt = QKeyEvent(QEvent.KeyPress, Qt.Key_Plus, Qt.NoModifier)
    app.keyPressEvent(evt)
    app._tick_timer.stop()
    assert app._remaining == 360


def test_key_minus_decrements_remaining(app):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtCore import QEvent

    app._tick_timer.start()
    app._remaining = 300
    evt = QKeyEvent(QEvent.KeyPress, Qt.Key_Minus, Qt.NoModifier)
    app.keyPressEvent(evt)
    app._tick_timer.stop()
    assert app._remaining == 240


def test_key_minus_floor(app):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtCore import QEvent

    app._tick_timer.start()
    app._remaining = 30
    evt = QKeyEvent(QEvent.KeyPress, Qt.Key_Minus, Qt.NoModifier)
    app.keyPressEvent(evt)
    app._tick_timer.stop()
    assert app._remaining == 1


def test_key_plus_inactive_timer_no_change(app):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtCore import QEvent

    app._tick_timer.stop()
    app._remaining = 300
    evt = QKeyEvent(QEvent.KeyPress, Qt.Key_Plus, Qt.NoModifier)
    app.keyPressEvent(evt)
    assert app._remaining == 300


def test_key_r_resets_session(qapp, tmp_path):
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QKeyEvent
    from reverse_pomodoro.gui import PomodoroApp

    log_file = str(tmp_path / "log.json")
    a = PomodoroApp(_make_args(log_file=log_file))
    a._tick_timer.start()
    a._remaining = 10

    evt = QKeyEvent(QEvent.KeyPress, Qt.Key_R, Qt.NoModifier)
    a.keyPressEvent(evt)

    assert a._tick_timer.isActive()
    a._tick_timer.stop()


def test_key_n_advances_when_enabled(qapp, tmp_path):
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QKeyEvent
    from reverse_pomodoro.gui import PomodoroApp

    log_file = str(tmp_path / "log.json")
    a = PomodoroApp(_make_args(log_file=log_file))
    a._tick_timer.stop()
    a._session_type = "work"
    a._btn_next.setEnabled(True)

    evt = QKeyEvent(QEvent.KeyPress, Qt.Key_N, Qt.NoModifier)
    a.keyPressEvent(evt)
    a._tick_timer.stop()

    assert a._session_type == "break"


def test_key_n_advances_even_when_disabled(app):
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QKeyEvent

    app._session_type = "work"
    app._btn_next.setEnabled(False)

    evt = QKeyEvent(QEvent.KeyPress, Qt.Key_N, Qt.NoModifier)
    app.keyPressEvent(evt)
    app._tick_timer.stop()

    assert app._session_type == "break"


def test_key_left_forwarded_during_break(app):
    from unittest.mock import MagicMock
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QKeyEvent

    app._session_type = "break"
    app._minigame.move_left = MagicMock()

    evt = QKeyEvent(QEvent.KeyPress, Qt.Key_Left, Qt.NoModifier)
    app.keyPressEvent(evt)

    app._minigame.move_left.assert_called_once()


def test_key_right_forwarded_during_break(app):
    from unittest.mock import MagicMock
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QKeyEvent

    app._session_type = "break"
    app._minigame.move_right = MagicMock()

    evt = QKeyEvent(QEvent.KeyPress, Qt.Key_Right, Qt.NoModifier)
    app.keyPressEvent(evt)

    app._minigame.move_right.assert_called_once()


def test_key_left_not_forwarded_during_work(app):
    from unittest.mock import MagicMock
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QKeyEvent

    app._session_type = "work"
    app._minigame.move_left = MagicMock()

    evt = QKeyEvent(QEvent.KeyPress, Qt.Key_Left, Qt.NoModifier)
    app.keyPressEvent(evt)

    app._minigame.move_left.assert_not_called()


# ------------------------------------------------------------------
# _reset_session
# ------------------------------------------------------------------

def test_reset_session_logs_partial(qapp, tmp_path):
    import time
    from reverse_pomodoro.gui import PomodoroApp

    log_file = str(tmp_path / "log.json")
    a = PomodoroApp(_make_args(log_file=log_file))
    a._session_type = "work"
    a._session_start = time.time() - 30
    a._partial_entry = {
        "timestamp": "2024-01-01T10:00:00",
        "type": "work",
        "planned_duration": 300,
    }

    a._reset_session()
    a._tick_timer.stop()

    import json
    with open(log_file) as f:
        entries = json.load(f)
    assert any(e["completed"] is False for e in entries)


def test_reset_session_restarts_timer(qapp, tmp_path):
    from reverse_pomodoro.gui import PomodoroApp

    log_file = str(tmp_path / "log.json")
    a = PomodoroApp(_make_args(log_file=log_file))
    a._tick_timer.stop()
    a._session_type = "work"
    a._partial_entry = None

    a._reset_session()

    assert a._tick_timer.isActive()
    a._tick_timer.stop()


# ------------------------------------------------------------------
# Auto-minimize
# ------------------------------------------------------------------

def test_auto_minimize_work(qapp, tmp_path):
    from unittest.mock import patch
    from reverse_pomodoro.gui import PomodoroApp

    log_file = str(tmp_path / "log.json")
    a = PomodoroApp(_make_args(log_file=log_file))

    with patch("reverse_pomodoro.gui.QTimer.singleShot") as mock_shot:
        a._start_work()
        a._tick_timer.stop()
        calls = [c for c in mock_shot.call_args_list if c.args[0] == 100]
        assert len(calls) >= 1


def test_auto_minimize_break(qapp, tmp_path):
    from unittest.mock import patch
    from reverse_pomodoro.gui import PomodoroApp

    log_file = str(tmp_path / "log.json")
    a = PomodoroApp(_make_args(log_file=log_file))

    with patch("reverse_pomodoro.gui.QTimer.singleShot") as mock_shot:
        a._start_break()
        a._tick_timer.stop()
        a._minigame.stop()
        calls = [c for c in mock_shot.call_args_list if c.args[0] == 100]
        assert len(calls) >= 1


# ------------------------------------------------------------------
# Mini-game visibility
# ------------------------------------------------------------------

def test_minigame_hidden_during_work(app):
    app._start_work()
    app._tick_timer.stop()
    assert not app._minigame.isVisible()


def test_minigame_visible_during_break(app):
    app.show()
    app._start_break()
    app._tick_timer.stop()
    app._minigame.stop()
    assert app._minigame.isVisible()
    app.hide()


# ------------------------------------------------------------------
# Hints label
# ------------------------------------------------------------------

def test_hints_label_work(app):
    app._start_work()
    app._tick_timer.stop()
    text = app._label_hints.text()
    assert "[+/-]" in text
    assert "[R]" in text


def test_hints_label_break(app):
    app._start_break()
    app._tick_timer.stop()
    app._minigame.stop()
    text = app._label_hints.text()
    assert "[←/→]" in text
