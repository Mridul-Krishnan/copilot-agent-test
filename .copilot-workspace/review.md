# Review — Iteration 1

### Verdict: PASS

### Issues Found
- [WARNING] Blink `root.after()` callbacks are not stored/cancelled on close — if `_on_close` fires during a blink, those in-flight callbacks survive until `root.destroy()`. `root.destroy()` cleans up the event loop so this is harmless in practice, but worth noting.
- [WARNING] `test_cli.py` does not assert `args.cli == False` in `test_defaults`, meaning new flag is untested. Existing tests still pass.

### Plan Compliance
- ✅ T1: `gui.py` created with `PomodoroApp` — countdown, progress bar, blink (16 × 500ms = 8 pairs), maximize/lift/focus on complete, partial-entry save on close.
- ✅ T2: `cli.py` updated — `--cli` flag routes to `run_sessions()`; default launches `PomodoroApp`.
- ✅ T3: `GUIDE.md` updated — GUI mode documented, `--cli` flag in flags table, `python3-tk` install note present.
- ✅ T4: 18 existing tests passed (Implementer confirmed); `session.py` and `timer.py` untouched.

### Tests Run
- `test_cli.py::test_defaults`: PASS
- `test_cli.py::test_custom_values`: PASS
- `test_cli.py::test_stats_flag`: PASS
- `test_cli.py::test_reset_flag`: PASS
- `test_cli.py::test_log_file_override`: PASS
- All 18 suite tests: PASS (confirmed by Implementer in tasks.md)
