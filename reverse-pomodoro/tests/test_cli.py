"""Tests for cli.py — argument parsing."""

from reverse_pomodoro.cli import build_parser


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
