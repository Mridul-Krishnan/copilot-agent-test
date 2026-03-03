"""Tests for timer.py — countdown display."""

from unittest.mock import patch

from reverse_pomodoro import timer


def test_countdown_completes():
    timer.interrupted = False
    with patch("reverse_pomodoro.timer.time.sleep"):
        result = timer.countdown(3, "Test")
    assert result is True


def test_countdown_interrupted():
    timer.interrupted = False

    call_count = 0

    def fake_sleep(n):
        nonlocal call_count
        call_count += 1
        if call_count >= 2:
            timer.interrupted = True

    with patch("reverse_pomodoro.timer.time.sleep", side_effect=fake_sleep):
        result = timer.countdown(10, "Test")
    assert result is False
    timer.interrupted = False
