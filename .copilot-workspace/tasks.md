# Tasks — Reverse Pomodoro Timer CLI

## Iteration 1

### Task 1: Project scaffold
- **Description:** Create `reverse-pomodoro/` directory with `pyproject.toml`, `src/reverse_pomodoro/__init__.py`, `src/reverse_pomodoro/__main__.py`, and empty `tests/__init__.py`.
- **Files:** `reverse-pomodoro/pyproject.toml`, `src/reverse_pomodoro/__init__.py`, `src/reverse_pomodoro/__main__.py`, `tests/__init__.py`
- **Acceptance:** `uv sync` succeeds in the project directory. `uv run python -m reverse_pomodoro --help` shows usage.
- [x] Done

### Task 2: CLI argument parsing (cli.py)
- **Description:** Implement `cli.py` with argparse: `-w`, `-m`, `-i`, `-b`, `--stats`, `--reset`, `--log-file` flags. `main()` function dispatches to appropriate handler.
- **Files:** `src/reverse_pomodoro/cli.py`
- **Acceptance:** `--help` shows all flags with defaults. Invalid args produce clear errors.
- [x] Done

### Task 3: Log module (log.py)
- **Description:** Implement `load_log()`, `append_entry()`, `get_today_stats()`, `reset_progression()`. Log format as specified in plan.
- **Files:** `src/reverse_pomodoro/log.py`
- **Acceptance:** Can write and read entries. Stats correctly compute today's focus time. Reset marker works.
- [x] Done

### Task 4: Timer display (timer.py)
- **Description:** Implement `countdown()` with live terminal display using `\r`, progress bar, and system bell on completion. Returns completion status.
- **Files:** `src/reverse_pomodoro/timer.py`
- **Acceptance:** Countdown displays and updates in-place. Bell rings on finish. Returns `False` if interrupted.
- [x] Done

### Task 5: Session manager (session.py)
- **Description:** Implement `run_sessions()` — calculates progression from log, runs work/break loop, handles Ctrl+C gracefully with partial session save.
- **Files:** `src/reverse_pomodoro/session.py`
- **Acceptance:** Sessions alternate work→break. Duration grows each cycle. Ctrl+C saves partial and exits.
- [x] Done

### Task 6: Wire up main + entry point
- **Description:** Connect `cli.py` main → session/stats/reset dispatch. Update `__main__.py`. Verify `uv run reverse-pomodoro` works end-to-end.
- **Files:** `src/reverse_pomodoro/__main__.py`, `src/reverse_pomodoro/cli.py`
- **Acceptance:** Full flow works: `uv run reverse-pomodoro` starts timer; `--stats` and `--reset` work.
- [x] Done

### Task 7: Tests
- **Description:** Write pytest tests for log.py (read/write/stats/reset), cli.py (arg parsing), timer.py (mocked countdown), session.py (mocked progression logic).
- **Files:** `tests/test_cli.py`, `tests/test_log.py`, `tests/test_timer.py`, `tests/test_session.py`
- **Acceptance:** All tests pass with `uv run pytest`.
- [x] Done

### Task 8: GUIDE.md
- **Description:** Write GUIDE.md explaining the technique, installation, CLI usage examples, and tips.
- **Files:** `reverse-pomodoro/GUIDE.md`
- **Acceptance:** Covers all required sections. CLI examples match actual flags.
- [x] Done
