"""Tests for cli.py — argument parsing."""

import sys
import pytest
from unittest.mock import patch

from reverse_pomodoro.cli import build_parser, _ensure_qt_platform


def test_defaults():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.work == 5
    assert args.max_duration == 50
    assert args.increment == 5
    assert args.break_duration == 5
    assert args.stats is False
    assert args.reset is False
    assert args.log_file == "./reverse-pomodoro.json"
    assert args.cli is False


def test_custom_values():
    parser = build_parser()
    args = parser.parse_args(["-w", "10", "-m", "60", "-i", "10", "-b", "3"])
    assert args.work == 10
    assert args.max_duration == 60
    assert args.increment == 10
    assert args.break_duration == 3


def test_stats_flag():
    parser = build_parser()
    args = parser.parse_args(["--stats"])
    assert args.stats is True


def test_reset_flag():
    parser = build_parser()
    args = parser.parse_args(["--reset"])
    assert args.reset is True


def test_log_file_override():
    parser = build_parser()
    args = parser.parse_args(["--log-file", "/tmp/my-log.json"])
    assert args.log_file == "/tmp/my-log.json"


def test_ensure_qt_platform_non_linux(monkeypatch):
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)
    # Should return immediately without checking xcb-cursor or exiting
    _ensure_qt_platform()  # must not raise


def test_ensure_qt_platform_already_set(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setenv("QT_QPA_PLATFORM", "xcb")
    # Should be a no-op
    _ensure_qt_platform()  # must not raise


def test_ensure_qt_platform_xcb_cursor_found(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    with patch("ctypes.util.find_library", return_value="libxcb-cursor.so"):
        _ensure_qt_platform()  # must not raise


def test_ensure_qt_platform_wayland_fallback(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)
    monkeypatch.setenv("WAYLAND_DISPLAY", ":0")
    with patch("ctypes.util.find_library", return_value=None):
        _ensure_qt_platform()
    import os
    assert os.environ.get("QT_QPA_PLATFORM") == "wayland"


def test_ensure_qt_platform_no_platform(monkeypatch, capsys):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("QT_QPA_PLATFORM", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    with patch("ctypes.util.find_library", return_value=None):
        with pytest.raises(SystemExit) as exc_info:
            _ensure_qt_platform()
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "libxcb-cursor0" in captured.out
    assert "sudo apt install libxcb-cursor0" in captured.out
