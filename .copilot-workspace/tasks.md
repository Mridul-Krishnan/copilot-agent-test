# Tasks — sysmon UI Enhancement + Process List

## Task 1 — Richer CSS in `theme.py`
**File:** `src/sysmon/theme.py`  
**Status:** [x] (done in iteration 1)

---

## Task 2 — Dynamic bar colouring in `widgets.py`
**File:** `src/sysmon/widgets.py`  
**Status:** [x] (done in iteration 1)

---

## Task 3 — `collect_processes()` in `collector.py`
**File:** `src/sysmon/collector.py`  
**Status:** [x] (done in iteration 1)

---

## Task 4 — App wiring in `app.py`
**File:** `src/sysmon/app.py`  
**Status:** [x] (done in iteration 1)

---

## Task 5 — Fix CSS selector mismatch in `theme.py`
**File:** `src/sysmon/theme.py`  
**Changes:**
- Change `MetricPanel ProgressBar Bar.ok` → `MetricPanel ProgressBar.ok Bar`
- Change `MetricPanel ProgressBar Bar.warn` → `MetricPanel ProgressBar.warn Bar`
- Change `MetricPanel ProgressBar Bar.crit` → `MetricPanel ProgressBar.crit Bar`

**Acceptance:** CSS selectors match where Python code actually sets the class (on `ProgressBar`, not inner `Bar`).

**Status:** [x]

---

## Task 6 — Add `psutil.ZombieProcess` to except clause in `collector.py`
**File:** `src/sysmon/collector.py`  
**Changes:**
- Update except tuple in `collect_processes()` from `(psutil.AccessDenied, psutil.NoSuchProcess)` to `(psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess)`.

**Acceptance:** Zombie processes on Linux do not cause an unhandled exception.

**Status:** [x]

---

## Task 7 — Tests for `collect_processes()` in `test_collector.py`
**File:** `tests/test_collector.py`  
**Changes:**
- Add `TestCollectProcesses` class with:
  - `test_returns_list_of_dicts` — real call; assert list of dicts with keys `pid, name, cpu_percent, mem_percent, status`.
  - `test_sorted_by_cpu_descending` — mock two procs; assert descending order.
  - `test_respects_n_limit` — mock >n procs; assert `len(result) <= n`.
  - `test_access_denied_skipped` — mock proc raising `AccessDenied`; assert skipped.
  - `test_no_such_process_skipped` — mock proc raising `NoSuchProcess`; assert skipped.
  - `test_zombie_process_skipped` — mock proc raising `ZombieProcess`; assert skipped.

**Acceptance:** All 6 tests pass; no live psutil calls in mocked tests.

**Status:** [x]

---

## Task 8 — Tests for `ProcessTable` widget in `test_widgets.py`
**File:** `tests/test_widgets.py`  
**Changes:**
- Add `TestProcessTable` class:
  - `test_refresh_empty_list` — mount `ProcessTable`, call `refresh_processes([])`, assert 0 rows and no crash.
  - `test_refresh_valid_row` — call `refresh_processes([{valid row}])`, assert 1 row.

**Acceptance:** Both tests pass; `ProcessTable` renders without error in both cases.

**Status:** [x]

---

## Task 9 — Async test for `p` key binding in `test_widgets.py`
**File:** `tests/test_widgets.py`  
**Changes:**
- Add `TestProcessToggle` class:
  - `test_p_binding_toggles_views` — verify initial state (`#main-view` visible, `#proc-view` hidden, `_show_processes == False`); press `p`; assert inverse; press `p` again; assert back to original.

**Acceptance:** Test passes; `#main-view` and `#proc-view` visibility are correctly toggled.

**Status:** [x]

---

## Task 10 — Tests for ProgressBar CSS class thresholds in `test_widgets.py`
**File:** `tests/test_widgets.py`  
**Changes:**
- Add `TestMetricPanelThresholds` class:
  - `test_ok_class` — value 0 and 59.9 → `ProgressBar` has class `ok`.
  - `test_warn_class` — value 60 and 85 → class `warn`.
  - `test_crit_class` — value 85.1 and 100 → class `crit`.

**Acceptance:** All threshold tests pass; correct CSS class is present after `watch_value` fires.

**Status:** [x]

