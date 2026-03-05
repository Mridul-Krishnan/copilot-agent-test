# Tasks

## Iteration 1 — GUI Pop-out Window

### T1 — Create `src/reverse_pomodoro/gui.py`
**Description:** Build a `PomodoroApp` tkinter class that drives the full work→break session loop using `root.after()` scheduling. No threads needed.

**Acceptance criteria:**
- Window opens, shows session label + large MM:SS countdown + filled progress bar
- Timer ticks every second, updating the display
- On completion: window maximizes, lifts to top, gains focus, blinks (8 × 500 ms, orange ↔ white)
- After blink: shows a "▶ Next" button to advance to the next session
- Closing the window mid-session saves a partial log entry
- All session data is logged to the JSON log file (same format as CLI mode)

**Affected files:** `src/reverse_pomodoro/gui.py` (new)

**Status:** [x]

---

### T2 — Modify `src/reverse_pomodoro/cli.py`
**Description:** Add a `--cli` flag. Without it, `main()` calls `PomodoroApp(args).run()`. With `--cli`, calls the existing `run_sessions(args)` as before.

**Acceptance criteria:**
- `uv run reverse-pomodoro` opens the GUI window
- `uv run reverse-pomodoro --cli` runs in the terminal exactly as before
- `--stats` and `--reset` still work (exit before any GUI/CLI session loop)

**Affected files:** `src/reverse_pomodoro/cli.py`

**Status:** [x]

---

### T3 — Update `GUIDE.md`
**Description:** Add a section explaining the GUI mode, the `--cli` fallback, and the `python3-tk` system dependency note for Linux users.

**Acceptance criteria:**
- GUI mode documented with example command
- `--cli` flag listed in the All CLI Flags table
- Note about `sudo apt install python3-tk` (or equivalent) for users who lack tkinter

**Affected files:** `reverse-pomodoro/GUIDE.md`

**Status:** [x]

---

### T4 — Smoke-test the GUI
**Description:** Run the app, confirm the window appears, timer counts down visually, and completion triggers blink + maximize + focus.

**Acceptance criteria:**
- Window launches without errors
- Countdown progresses correctly
- Completion alert is clearly visible (blink + maximize)
- Existing tests (`uv run pytest`) still pass

**Affected files:** none (verification only)

**Status:** [x] — 18 tests passed
