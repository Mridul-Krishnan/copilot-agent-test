# Tasks — sysmon (Iteration 2 — Revision)

> Iteration 1 tasks are all ✅ complete. Below are revision tasks from the review.

## Task R1: Fix Collector Null Guards
- [x] Guard `psutil.disk_io_counters()` — if it returns `None`, skip disk rate calculation, set rates to 0, and set `_prev_disk = None`
- [x] Guard `psutil.net_io_counters()` — same pattern for network
- [x] Clamp all computed I/O rates to `max(0.0, rate)` to handle counter rollover
- [x] Add comment noting the module-level state assumes single-threaded usage (Textual's main thread)
- **File:** `sysmon/src/sysmon/collector.py`
- **Acceptance:** ✅ `collect()` guards against None counters and clamps rates

## Task R2: Fix Widget Exception Handling
- [x] Import `NoMatches` from `textual.css.query`
- [x] In `MetricPanel.watch_value`: replace `except Exception: pass` with `except NoMatches: pass`
- [x] In `MetricPanel.watch_history`: same fix
- [x] In `IOMetricPanel.watch_value`: same fix
- [x] In `IOMetricPanel.watch_history`: same fix
- **File:** `sysmon/src/sysmon/widgets.py`
- **Acceptance:** ✅ Only `NoMatches` is caught; other exceptions propagate normally

## Task R3: Add `_human_bytes()` Tests
- [x] Test `_human_bytes(0)` → `"0.0 B"`
- [x] Test `_human_bytes(1024)` → `"1.0 KB"`
- [x] Test `_human_bytes(1048576)` → `"1.0 MB"` (1024²)
- [x] Test `_human_bytes(1073741824)` → `"1.0 GB"` (1024³)
- [x] Test `_human_bytes(1099511627776)` → `"1.0 TB"` (1024⁴)
- [x] Test `_human_bytes(-500)` → handles negative input without crash
- [x] Test `_human_bytes(512)` → `"512.0 B"`
- **File:** `sysmon/tests/test_widgets.py`
- **Acceptance:** ✅ All 7 `_human_bytes` tests pass

## Task R4: Add IOMetricPanel Isolated Tests
- [x] Test that `IOMetricPanel` renders with a label containing `_human_bytes` formatted output
- [x] Test that setting `.value` updates the label
- [x] Test that setting `.history` updates the sparkline data
- **File:** `sysmon/tests/test_widgets.py`
- **Acceptance:** ✅ All 3 IOMetricPanel tests pass

## Task R5: Add Theme Toggle Test
- [x] Use `app.run_test()` pilot to press `t`
- [x] Assert the app's `_dark_mode` attribute flipped
- [x] Assert `app.theme` changed from `"textual-dark"` to `"textual-light"`
- **File:** `sysmon/tests/test_widgets.py`
- **Acceptance:** ✅ Theme toggle test passes

## Task R6: Add Collector Edge-Case Tests
- [x] Test `cpu_total` is in range [0, 100]
- [x] Test `swap_percent` ≥ 0
- [x] Test that after two calls, all I/O rates are ≥ 0 (non-negative)
- **File:** `sysmon/tests/test_collector.py`
- **Acceptance:** ✅ All 3 edge-case tests pass

## Task R7: Fix Python Version in pyproject.toml
- [x] Change `requires-python = ">=3.11"` to `requires-python = ">=3.10"` in `sysmon/pyproject.toml`
- **File:** `sysmon/pyproject.toml`
- **Acceptance:** ✅ `requires-python` matches requirements.md

## Task R8: Run Full Test Suite
- [x] Run `uv run pytest -v` and confirm all tests pass (old + new)
- **Acceptance:** ✅ 23/23 tests pass
