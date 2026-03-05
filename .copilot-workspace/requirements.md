# Requirements

## Feature: GUI Pop-out Window for Reverse Pomodoro

Convert the reverse-pomodoro CLI app into a draggable pop-out GUI window while preserving all existing CLI functionality (--stats, --reset, etc.).

### Must Have
- Floating, draggable GUI window showing the timer (session label, countdown MM:SS, progress bar)
- On timer completion: window blinks (flashing background), rises to top, gains focus, maximizes so the user notices
- GUI is the default mode when running `uv run reverse-pomodoro` without --stats/--reset
- All existing flags (-w, -m, -i, -b, --stats, --reset, --log-file) still work

### Nice to Have
- `--cli` flag to fall back to the original terminal output mode
- Session type label (Work / Break) clearly visible in the window

