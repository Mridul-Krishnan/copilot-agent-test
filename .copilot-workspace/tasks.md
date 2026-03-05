# Tasks — Revision 2

## Task 1 — Larger default window size [x]
**File:** `src/reverse_pomodoro/gui.py`
**Change:** `self.resize(420, 280)` → `self.resize(420, 580)` in `__init__`
**Acceptance:** Window opens at 420×580, large enough to display the mini-game.

## Task 2 — Shrink instead of minimise [x]
**File:** `src/reverse_pomodoro/gui.py`
**Change:**
- Add `_shrink_to_default()`: calls `self.showNormal()` then `self.resize(420, 580)`.
- Replace both `QTimer.singleShot(100, self.showMinimized)` calls (in `_start_work` and `_start_break`) with `QTimer.singleShot(100, self._shrink_to_default)`.
**Acceptance:** Starting a session keeps the window on screen at 420×580 instead of minimising to taskbar.

## Task 3 — N / ↵ / Space work at any time [x]
**File:** `src/reverse_pomodoro/gui.py`
**Change:**
- Remove `if self._btn_next.isEnabled():` guard in `keyPressEvent`.
- In `_advance()`: add guard to stop timers and save partial entry as `completed=False` when called mid-session.
**Acceptance:** Pressing N/↵/Space skips the current session at any point.

## Task 4 — Full-reset key (Shift+R) [x]
**File:** `src/reverse_pomodoro/gui.py`
**Change:**
- Add `_full_reset()`: saves partial entry, stops timers, sets `self._completed = 0`, calls `_start_work()`.
- In `keyPressEvent` for `Qt.Key_R`: branch on `Qt.ShiftModifier` → `_full_reset()` vs `_reset_session()`.
- Update hints text in `_build_ui`, `_start_work`, `_start_break` to include `[Shift+R] full reset`.
**Acceptance:** Pressing Shift+R at any time resets back to Work #1.

## Task 5 — Fix syntax error in `_shrink_to_default` / `_update_display` (CRITICAL) [x]
**File:** `src/reverse_pomodoro/gui.py`
**Change:** Line 227 currently reads:
```
        self.resize(420, 580)(self) -> None:
```
Replace with two correct lines:
```
        self.resize(420, 580)

    def _update_display(self) -> None:
```
so that `_shrink_to_default` ends cleanly and `_update_display` is restored as its own method declaration.
**Acceptance:** `python -c "import reverse_pomodoro.gui"` succeeds; all tests pass.

## Task 6 — Update test for new N-key behaviour [x]
**File:** `tests/test_gui.py`
**Change:** Rename `test_key_n_no_advance_when_disabled` → `test_key_n_advances_even_when_disabled`. Change the final assertion from `app._session_type == "work"` to `app._session_type == "break"`, and add `app._tick_timer.stop()` after the key press.
**Acceptance:** `test_key_n_advances_even_when_disabled` passes; all other tests pass.

**File:** `src/reverse_pomodoro/gui.py`
**Change:** `self.resize(420, 280)` → `self.resize(420, 580)` in `__init__`
**Acceptance:** Window opens at 420×580, large enough to display the mini-game.

## Task 2 — Shrink instead of minimise [x]
**File:** `src/reverse_pomodoro/gui.py`
**Change:**
- Add `_shrink_to_default()`: calls `self.showNormal()` then `self.resize(420, 580)`.
- Replace both `QTimer.singleShot(100, self.showMinimized)` calls (in `_start_work` and `_start_break`) with `QTimer.singleShot(100, self._shrink_to_default)`.
**Acceptance:** Starting a session keeps the window on screen at 420×580 instead of minimising to taskbar.

## Task 3 — N / ↵ / Space work at any time [x]
**File:** `src/reverse_pomodoro/gui.py`
**Change:**
- Remove `if self._btn_next.isEnabled():` guard in `keyPressEvent`.
- In `_advance()`: add guard to stop timers and save partial entry as `completed=False` when called mid-session.
**Acceptance:** Pressing N/↵/Space skips the current session at any point.

## Task 4 — Full-reset key (Shift+R) [x]
**File:** `src/reverse_pomodoro/gui.py`
**Change:**
- Add `_full_reset()`: saves partial entry, stops timers, sets `self._completed = 0`, calls `_start_work()`.
- In `keyPressEvent` for `Qt.Key_R`: branch on `Qt.ShiftModifier` → `_full_reset()` vs `_reset_session()`.
- Update hints text in `_build_ui`, `_start_work`, `_start_break` to include `[Shift+R] full reset`.
**Acceptance:** Pressing Shift+R at any time resets back to Work #1.

