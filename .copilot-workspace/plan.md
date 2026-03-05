# Plan: GUI Pop-out for Reverse Pomodoro

## Problem
The app only runs in the terminal. The user wants a draggable GUI window that pops up, shows the countdown, and grabs their attention (blinks + maximizes + focuses) when a session ends.

## Approach
Use **tkinter** (Python stdlib — no new dependencies) to build a `PomodoroApp` GUI class that drives the session loop via `root.after()` (no extra threads needed). The existing CLI path (`session.py`, `timer.py`) is left **untouched**. A `--cli` flag restores the old behaviour.

## Architecture

```
cli.py          ← adds --cli flag; routes to gui.py or session.py
gui.py          ← NEW: tkinter PomodoroApp class
session.py      ← unchanged (CLI mode)
timer.py        ← unchanged (CLI mode)
log.py          ← unchanged (shared by both modes)
```

## GUI Design
- Small, always-on-top-ish floating window (~360×180 px), freely draggable
- Session label: "🍅 Work #N — Xm" or "☕ Break — Xm"
- Countdown in large text: MM:SS
- Filled progress bar (Canvas rectangle)
- On completion:
  1. Restore & maximize the window (`root.state('normal')` → `root.attributes('-zoomed', True)` on Linux)
  2. `root.lift()` + `root.focus_force()` + `root.attributes('-topmost', True)`
  3. Blink loop: alternate window background + label bg between orange and white 8 times (500 ms each) using `root.after()`
  4. After blink, show "Continue?" prompt — user clicks button to proceed to next session

## Files to Create/Modify

| File | Action | What changes |
|------|--------|--------------|
| `src/reverse_pomodoro/gui.py` | CREATE | `PomodoroApp` tkinter class with full session loop |
| `src/reverse_pomodoro/cli.py` | MODIFY | Add `--cli` flag; default launches `PomodoroApp` |
| `pyproject.toml` | MODIFY | No new deps needed (tkinter is stdlib) |
| `GUIDE.md` | MODIFY | Document the GUI mode and `--cli` flag |

## Key Implementation Details

### `gui.py` — `PomodoroApp`
- `__init__`: build window, init state variables, call `_start_work()`
- `_start_work()`: compute duration, update label, schedule `_tick()`
- `_tick(remaining)`: update countdown + bar; if remaining==0 call `_on_complete()`; else `root.after(1000, _tick, remaining-1)`
- `_on_complete(session_type)`: log entry, blink, maximize, show "Next" button
- `_start_break()` / `_next_cycle()`: transition between sessions

### Blink Mechanism
```python
def _blink(self, count, colors):
    if count == 0:
        self._show_next_button()
        return
    color = colors[count % 2]
    self.root.configure(bg=color)
    self.root.after(500, self._blink, count - 1, colors)
```

### Attention Grab on Complete
```python
self.root.attributes('-zoomed', True)   # Linux maximize
self.root.lift()
self.root.focus_force()
self.root.attributes('-topmost', True)
```

## Considerations
- `tkinter` may require `python3-tk` system package on some Linux distros; the Implementer should note this in GUIDE.md
- Interrupt/Ctrl+C: bind `<Destroy>` or `WM_DELETE_WINDOW` to save a partial log entry
- Keep `--cli` working exactly as before (no changes to session.py / timer.py)
