"""Tests for log.py — JSON log read/write and stats."""

import json
import os
from datetime import date, datetime

from reverse_pomodoro.log import (
    append_entry,
    count_completed_work_sessions,
    get_today_stats,
    load_log,
    reset_progression,
)


def test_load_log_missing_file(tmp_path):
    assert load_log(str(tmp_path / "nope.json")) == []


def test_load_log_invalid_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("not json")
    assert load_log(str(p)) == []


def test_append_and_load(tmp_path):
    p = str(tmp_path / "log.json")
    append_entry(p, {"type": "work", "completed": True})
    append_entry(p, {"type": "break", "completed": True})
    log = load_log(p)
    assert len(log) == 2
    assert log[0]["type"] == "work"
    assert log[1]["type"] == "break"


def test_count_completed_work_sessions():
    log = [
        {"type": "work", "completed": True},
        {"type": "break", "completed": True},
        {"type": "work", "completed": True},
        {"type": "work", "completed": False},
    ]
    assert count_completed_work_sessions(log) == 2


def test_count_after_reset():
    log = [
        {"type": "work", "completed": True},
        {"type": "reset"},
        {"type": "work", "completed": True},
    ]
    assert count_completed_work_sessions(log) == 1


def test_get_today_stats(tmp_path):
    p = str(tmp_path / "log.json")
    today = date.today().isoformat()
    entries = [
        {
            "timestamp": f"{today}T10:00:00",
            "type": "work",
            "actual_duration": 300,
            "completed": True,
        },
        {
            "timestamp": f"{today}T10:10:00",
            "type": "work",
            "actual_duration": 600,
            "completed": True,
        },
        {
            "timestamp": "2020-01-01T10:00:00",
            "type": "work",
            "actual_duration": 999,
            "completed": True,
        },
    ]
    with open(p, "w") as f:
        json.dump(entries, f)

    stats = get_today_stats(p)
    assert stats["sessions"] == 2
    assert stats["focus_minutes"] == 15.0
    assert stats["level"] == 3  # all 3 completed work entries count


def test_reset_progression(tmp_path):
    p = str(tmp_path / "log.json")
    append_entry(p, {"type": "work", "completed": True})
    reset_progression(p)
    log = load_log(p)
    assert log[-1]["type"] == "reset"
    assert count_completed_work_sessions(log) == 0
