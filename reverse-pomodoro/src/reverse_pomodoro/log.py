"""JSON log read/write and stats."""

import json
import os
from datetime import datetime, date


def load_log(path: str) -> list[dict]:
    """Read log file; return empty list if missing or invalid."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def append_entry(path: str, entry: dict) -> None:
    """Append one entry to the log file."""
    log = load_log(path)
    log.append(entry)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(log, f, indent=2)
    os.replace(tmp, path)


def _entries_since_last_reset(log: list[dict]) -> list[dict]:
    """Return entries after the most recent reset marker."""
    last_reset = -1
    for i, entry in enumerate(log):
        if entry.get("type") == "reset":
            last_reset = i
    return log[last_reset + 1:]


def count_completed_work_sessions(log: list[dict]) -> int:
    """Count completed work sessions since the last reset."""
    active = _entries_since_last_reset(log)
    return sum(
        1 for e in active
        if e.get("type") == "work" and e.get("completed") is True
    )


def get_today_stats(path: str) -> dict:
    """Compute today's stats from the log."""
    log = load_log(path)
    today = date.today().isoformat()
    today_entries = [
        e for e in log
        if e.get("timestamp", "").startswith(today) and e.get("type") == "work"
    ]
    sessions = sum(1 for e in today_entries if e.get("completed"))
    focus_seconds = sum(e.get("actual_duration", 0) for e in today_entries)
    level = count_completed_work_sessions(log)
    return {
        "sessions": sessions,
        "focus_minutes": focus_seconds / 60,
        "level": level,
    }


def reset_progression(path: str) -> None:
    """Write a reset marker entry so progression restarts."""
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "type": "reset",
    }
    append_entry(path, entry)
