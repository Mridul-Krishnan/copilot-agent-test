# Plan — sysmon (Iteration 2 — Revision)

## Context
Iteration 1 delivered a working TUI app. The Reviewer found 5 critical issues and 4 warnings. This revision focuses on fixing those issues without restructuring the working code.

## Issues to Address (from review.md)

### CRITICAL Fixes
1. **Null guard in collector.collect()** — `psutil.disk_io_counters()` and `psutil.net_io_counters()` can return `None` (VMs, containers). Lines 57-64 and 67-74 of `collector.py` will crash with `AttributeError`. Guard with `if disk is not None` / `if net is not None`, return 0 rates when counters unavailable.

2. **Replace bare `except Exception: pass`** in widget watchers (widgets.py lines 60-67, 69-74, 122-127, 129-134). Import `NoMatches` from `textual.css.query` and catch only that specific exception. This prevents silent swallowing of real bugs.

3. **Add `_human_bytes()` unit tests** — the helper (widgets.py:137-143) has zero coverage. Test: 0 bytes, exact 1024 boundary, MB range, GB range, TB range, negative input.

4. **Add isolated `IOMetricPanel` tests** — current tests only check DOM presence. Add tests verifying label rendering with `_human_bytes` output and sparkline data updates.

5. **Add theme toggle test** — press `t` via pilot and verify the stylesheet source actually changed.

### WARNING Fixes
6. **Add collector edge-case tests** — verify `cpu_total` ∈ [0, 100], `swap_percent` ≥ 0, I/O rates ≥ 0 (guards against counter rollover producing negatives).

7. **Clamp I/O rates to ≥ 0** in `collector.collect()` — use `max(0.0, rate)` to handle counter rollover.

8. **Fix Python version mismatch** — requirements.md says >=3.10, pyproject.toml says >=3.11. Align to >=3.10 in pyproject.toml (per original requirement).

### Deferred (non-blocking)
- Widget code duplication (MetricPanel/IOMetricPanel) — noted as WARNING, not a correctness bug. Defer to future iteration.
- Thread safety on collector globals — Textual's `set_interval` runs on the main thread; no multi-thread risk in current usage. Add a comment noting this assumption.

## Files Modified

| File | Changes |
|------|---------|
| `sysmon/src/sysmon/collector.py` | Null guards for disk/net counters, clamp rates ≥ 0, thread-safety comment |
| `sysmon/src/sysmon/widgets.py` | Replace `except Exception` with `except NoMatches` |
| `sysmon/tests/test_collector.py` | Add edge-case tests (cpu range, swap, non-negative rates) |
| `sysmon/tests/test_widgets.py` | Add `_human_bytes` tests, `IOMetricPanel` tests, theme toggle test |
| `sysmon/pyproject.toml` | Change `requires-python` to `>=3.10` |
| `sysmon/.copilot-workspace/requirements.md` | No change needed (already says >=3.10) |

## Tasks (see tasks.md for checklist)
