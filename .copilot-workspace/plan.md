# Plan — Reverse Pomodoro Timer CLI

## Overview

Build a Python CLI tool implementing the reverse Pomodoro technique. The tool lives in a new subdirectory `reverse-pomodoro/` inside the repo, structured as a `uv`-managed Python package (Python 3.10+). No external dependencies — stdlib only (`argparse`, `json`, `time`, `datetime`, `signal`, `sys`).

## Project Structure

```
reverse-pomodoro/
├── pyproject.toml          # Package metadata, uv-managed, entry point
├── src/
│   └── reverse_pomodoro/
│       ├── __init__.py
│       ├── __main__.py     # Entry point (python -m reverse_pomodoro)
│       ├── cli.py          # Argument parsing
│       ├── timer.py        # Countdown display + bell logic
│       ├── session.py      # Session management (progression, run loop)
│       └── log.py          # JSON log read/write + stats
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_timer.py
│   ├── test_session.py
│   └── test_log.py
└── GUIDE.md
```

## Architecture

### cli.py — Argument Parsing
- Uses `argparse` to define CLI flags:
  - `-w / --work`: starting work duration in minutes (default: 5)
  - `-m / --max`: max work duration in minutes (default: 50)
  - `-i / --increment`: growth increment in minutes (default: 5)
  - `-b / --break-duration`: break duration in minutes (default: 5)
  - `--stats`: show today's stats and exit
  - `--reset`: reset progression and exit
  - `--log-file`: path to log file (default: `./reverse-pomodoro.json`)
- Returns a namespace; `main()` function dispatches to stats/reset/run.

### timer.py — Countdown Display
- `countdown(duration_seconds: int, label: str) -> bool`:
  - Displays live countdown using `\r` carriage return (no curses).
  - Format: `🍅 Work [25:00] ███████░░░ 70%` with a simple progress bar.
  - Returns `True` if completed, `False` if interrupted.
  - Rings system bell (`\a`) on completion.
- Uses `time.sleep(1)` for ticks — acceptable for a CLI timer.

### session.py — Session Management
- `run_sessions(config)`: main loop
  - Calculates current work duration from log history (count completed work sessions × increment + initial, capped at max).
  - Alternates work → break → work → break...
  - On Ctrl+C (SIGINT): save partial session (with actual elapsed time) and exit gracefully.
  - Each completed session is appended to the log before starting the next.

### log.py — JSON Log + Stats
- Log file format: JSON array of objects:
  ```json
  [
    {
      "timestamp": "2026-03-03T14:30:00",
      "type": "work",
      "planned_duration": 300,
      "actual_duration": 300,
      "completed": true
    }
  ]
  ```
- `load_log(path) -> list[dict]`: Read log, return empty list if missing.
- `append_entry(path, entry)`: Append one entry atomically.
- `get_today_stats(path) -> dict`: Filter today's entries, compute total focus time, session count, current progression level.
- `reset_progression(path)`: Write a special reset marker entry so progression restarts.

### __main__.py — Entry Point
```python
from reverse_pomodoro.cli import main
main()
```

### pyproject.toml
- `uv`-managed, stdlib only, no dependencies.
- `[project.scripts]` entry: `reverse-pomodoro = "reverse_pomodoro.cli:main"`
- Python requires `>=3.10`

### GUIDE.md
- Explains the reverse Pomodoro concept and its benefits for procrastination/ADHD.
- Installation: `uv sync` then `uv run reverse-pomodoro` (or `pip install -e .`).
- Full CLI flag examples with expected output.
- Tips section (start when motivation is lowest, pair with task lists, don't skip breaks).

## Key Design Decisions

1. **No external dependencies** — keeps it lightweight, `uv` manages the venv only.
2. **Log file default is CWD** (`./reverse-pomodoro.json`), overridable via `--log-file`.
3. **Progression is derived from log history** — no separate state file. Count completed work sessions since last reset marker.
4. **Ctrl+C handling**: register SIGINT handler that sets a flag; timer loop checks it, saves partial session, exits cleanly.
5. **Reset** writes a `{"type": "reset", ...}` marker entry — progression count starts from entries after the latest reset marker.
6. **Tests** use pytest, mock `time.sleep` and stdin/stdout for timer tests.
