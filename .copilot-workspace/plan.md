# Plan — Reverse Pomodoro GUI Improvements (Revision 2)

## Problem
Three improvements requested to `gui.py`:
1. **Next keys always work** — N / ↵ / Space should advance to the next session even mid-session.
2. **No minimise-to-taskbar** — Instead of `showMinimized()`, shrink window to default size.
3. **Larger default size** — 420×580 to fit the break mini-game.
4. **Full-reset key** — `Shift+R` resets `_completed` to 0 and restarts from Work #1.

## Status After Iteration 1
Most logic was implemented correctly. Two issues remain from the Reviewer:

### Issue A — Syntax error in `gui.py` line 227 (CRITICAL)
The Implementer merged two lines into one:
```
self.resize(420, 580)(self) -> None:
```
This should be two separate things:
- `self.resize(420, 580)` — last line of `_shrink_to_default`
- `def _update_display(self) -> None:` — declaration of the next method (currently missing entirely)

The body of `_update_display` (lines 228–232) is present but the method has no `def` declaration, so Python sees it as unreachable code inside `_shrink_to_default`, causing a `SyntaxError`.

**Fix:** Replace line 227 with:
```python
        self.resize(420, 580)

    def _update_display(self) -> None:
```

### Issue B — Test `test_key_n_no_advance_when_disabled` conflicts with new spec
The old test asserts that pressing N when `_btn_next` is disabled does NOT advance. The new spec (and the already-implemented `keyPressEvent`) removes this guard — N always advances. The test must be updated to assert the new intended behaviour: N advances even when button is disabled.

**Fix:** Rename the test to `test_key_n_advances_even_when_disabled` and change the final assertion from `assert app._session_type == "work"` to `assert app._session_type == "break"` (plus stop the tick timer after advancing).

## Files Changed
- `src/reverse_pomodoro/gui.py` — fix line 227 only
- `tests/test_gui.py` — update `test_key_n_no_advance_when_disabled`

