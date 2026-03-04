## Review — Iteration 2

### Verdict: PASS

### Issues Found
None.

### Tests Run
- `TestCollector` (9 existing tests): PASS — no regressions
- `TestCollectProcesses.test_returns_list_of_dicts`: PASS
- `TestCollectProcesses.test_sorted_by_cpu_descending`: PASS
- `TestCollectProcesses.test_respects_n_limit`: PASS
- `TestCollectProcesses.test_access_denied_skipped`: PASS
- `TestCollectProcesses.test_no_such_process_skipped`: PASS
- `TestCollectProcesses.test_zombie_process_skipped`: PASS
- `TestProcessTable.test_refresh_empty_list`: PASS
- `TestProcessTable.test_refresh_valid_row`: PASS
- `TestProcessToggle.test_p_binding_toggles_views`: PASS — full two-press cycle verified
- `TestMetricPanelThresholds.test_ok_class`: PASS — boundary values 59.9 and 1.0
- `TestMetricPanelThresholds.test_warn_class`: PASS — boundary values 60.0 and 84.9
- `TestMetricPanelThresholds.test_crit_class`: PASS — boundary values 85.1 and 100.0
- `TestHumanBytes` (7 tests): PASS — no regressions
- `TestAppSmoke` (3 tests): PASS — no regressions
- `TestIOMetricPanel` (3 tests): PASS — no regressions
- `TestThemeToggle` (1 test): PASS — no regressions

### Summary of fixes verified
- `theme.py`: CSS selector corrected to `MetricPanel ProgressBar.ok Bar` (and `warn`, `crit`) — class is applied to `ProgressBar` in Python, inner `Bar` correctly styled via ancestor selector.
- `collector.py`: `psutil.ZombieProcess` added to except clause; all three error types now covered.
- `test_collector.py`: Full `TestCollectProcesses` suite added — shape, sort, n-limit, and all three psutil exceptions mocked and verified.
- `test_widgets.py`: `TestProcessTable`, `TestProcessToggle`, and `TestMetricPanelThresholds` added with boundary values at every threshold (59.9/60.0/84.9/85.1/100.0).

---

# Review — Iteration 1

### Verdict: FAIL

---

### Issues Found

- **[CRITICAL] CSS selector mismatch — progress bar colour coding is broken**  
  In `widgets.py`, `watch_value` adds `ok/warn/crit` classes to the **`ProgressBar`** widget:
  ```python
  bar = self.query_one("#bar", ProgressBar)
  bar.add_class("ok")
  ```
  But `theme.py` targets **`Bar.ok`** (Textual's inner sub-widget of ProgressBar):
  ```css
  MetricPanel ProgressBar Bar.ok { color: $success; }
  ```
  These selectors never match — the `ok/warn/crit` class lives on `ProgressBar`, but the CSS rule looks for it on the inner `Bar` child. The colour-coding feature is silently broken at runtime. The fix is to change the CSS to `MetricPanel ProgressBar.ok Bar { color: $success; }` (and similarly for `warn`/`crit`), OR add the class to the inner `Bar` widget instead.

- **[CRITICAL] No tests for `collect_processes()`**  
  The plan's Task 3 acceptance criteria explicitly requires: "Function returns a list of dicts with expected keys; no crash on permission errors." Zero tests exist for this function. At minimum: a basic return-shape test, a test that the output is sorted descending by `cpu_percent`, and a test that permission errors don't propagate.

- **[CRITICAL] No tests for `ProcessTable` widget**  
  The new `ProcessTable` widget (Task 2) has no tests. `refresh_processes()` with a well-formed list, an empty list, and a row with None/missing fields should all be covered.

- **[CRITICAL] No tests for `action_toggle_processes()` / `p` binding**  
  Task 4 acceptance criteria: "Pressing `p` switches to process table; pressing `p` again returns to dashboard." No async test exercises the `p` key. `_show_processes` state, `#main-view` visibility, and `#proc-view` visibility must be verified.

- **[WARNING] `psutil.ZombieProcess` not caught in `collect_processes()`**  
  On Linux, iterating zombie processes can raise `psutil.ZombieProcess` (a subclass of `NoSuchProcess` in some psutil versions, but raised independently in others). The except clause `(psutil.AccessDenied, psutil.NoSuchProcess)` may not cover it. Should add `psutil.ZombieProcess` explicitly or catch the base `psutil.Error`.

- **[WARNING] No test for ProgressBar CSS class state**  
  The threshold logic (< 60 = ok, 60–85 = warn, > 85 = crit) has no unit test. A widget-level async test should assert the correct CSS class is present on the bar after `watch_value` fires for representative values (e.g. 0, 59.9, 60, 85, 85.1, 100).

---

### Feedback for Planner

1. **Fix CSS selectors** in `theme.py`: change  
   `MetricPanel ProgressBar Bar.ok` → `MetricPanel ProgressBar.ok Bar`  
   (and likewise for `warn` and `crit`) to match where the Python code actually sets the class.

2. **Add tests to `test_collector.py`** for `collect_processes()`:  
   - Returns a list of dicts with keys `pid, name, cpu_percent, mem_percent, status`.  
   - List is sorted by `cpu_percent` descending.  
   - Respects `n` limit.  
   - Does not raise when psutil raises `AccessDenied` or `NoSuchProcess` (mock).

3. **Add tests to `test_widgets.py`** for `ProcessTable`:  
   - `refresh_processes([])` clears the table without error.  
   - `refresh_processes([{...valid row...}])` adds a row.

4. **Add async test** for the `p` binding in `test_widgets.py`:  
   - Before press: `#main-view` visible, `#proc-view` hidden, `_show_processes == False`.  
   - After one press: inverse.  
   - After second press: back to original.

5. **Add `psutil.ZombieProcess`** to the except clause in `collect_processes()`.

---

### Tests Run

- Existing tests (`test_collector.py`, `test_widgets.py`): reviewed for coverage — existing tests PASS (no regressions from code inspection), but new functionality is entirely untested.

