"""Tests for session.py — progression logic."""

from unittest.mock import patch
from types import SimpleNamespace

from reverse_pomodoro.session import _calc_work_duration


def test_calc_work_duration_initial():
    assert _calc_work_duration(0, 5, 5, 50) == 5


def test_calc_work_duration_progression():
    assert _calc_work_duration(3, 5, 5, 50) == 20


def test_calc_work_duration_capped():
    assert _calc_work_duration(100, 5, 5, 50) == 50


def test_run_sessions_one_cycle():
    """Run one work+break cycle then interrupt."""
    from reverse_pomodoro import timer, session
    from reverse_pomodoro.session import run_sessions

    call_count = 0
    original_countdown = timer.countdown

    def fake_countdown(duration, label):
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            # After work completes, interrupt during break
            timer.interrupted = True
            return False
        return True

    args = SimpleNamespace(
        work=1, max_duration=10, increment=1, break_duration=1,
        log_file="/tmp/test-session-run.json",
    )

    import os
    if os.path.exists(args.log_file):
        os.remove(args.log_file)

    with patch.object(timer, "countdown", side_effect=fake_countdown):
        with patch("reverse_pomodoro.session.time.time", return_value=0):
            run_sessions(args)

    # Verify log was written
    from reverse_pomodoro.log import load_log
    log = load_log(args.log_file)
    assert len(log) >= 1
    assert log[0]["type"] == "work"

    os.remove(args.log_file)
