# Plan — sysmon UI Enhancements + Process List View (Iteration 2)

## Problem

The current sysmon UI is functional but visually flat. Panels have no borders, all
sparklines are the same colour, progress bars are unstyled, and there is no way to
inspect individual processes. The user wants:

1. A more animated, visually engaging dashboard (colours, styled panels, richer header/footer).
2. A new **`p`** key that toggles a live process-list table view (similar to how `t` toggles the theme).

---

## Approach

### 1 — Richer CSS & Styling (`theme.py`)

- Add rounded `border` to every panel (card-style look).
- Style the header with a left-side coloured accent and the app name in bold/brighter colour.
- Give the footer a more descriptive key-binding bar (show all three bindings).
- Colour-code `ProgressBar` fill: green → yellow → red as value rises (via CSS classes
  `--ok`, `--warn`, `--crit` toggled in `watch_value`).
- Per-metric sparkline colours: distinct `color` rules for `#cpu`, `#ram`, `#swap`,
  `#disk-r`, `#disk-w`, `#net-s`, `#net-r` sparklines.
- Larger sparkline height (3 rows) for more visual drama.

### 2 — Widget Enhancements (`widgets.py`)

- **`MetricPanel`**: In `watch_value`, dynamically add/remove CSS classes (`ok`, `warn`,
  `crit`) on the ProgressBar so CSS can colour it.  Thresholds: < 60 % = ok, 60–85 % = warn,
  > 85 % = crit.
- **`IOMetricPanel`**: No structural change — just benefits from new CSS colours.
- **New `ProcessTable` widget**: A `Widget` wrapping Textual's `DataTable`.
  Columns: `PID`, `Name`, `CPU %`, `MEM %`, `Status`.  
  Exposed method `refresh_processes(rows)` to update rows every tick.

### 3 — Process Collector (`collector.py`)

- Add a `collect_processes(n=25)` helper that returns a list of dicts
  `{pid, name, cpu_percent, mem_percent, status}` sorted by `cpu_percent` descending,
  using `psutil.process_iter(['pid','name','cpu_percent','memory_percent','status'])`.

### 4 — App wiring (`app.py`)

- Add `Binding("p", "toggle_processes", "Processes")`.
- Track `_show_processes: bool = False`.
- `compose()`: yield both `Container(classes="panels-grid", id="main-view")` and
  `ProcessTable(id="proc-view")`.  Initially hide `proc-view` via CSS `display: none`.
- `action_toggle_processes()`: flip `_show_processes`, show/hide each view using
  `widget.display = True/False`.
- In `_refresh_stats()`, if `_show_processes` is True, also call
  `collect_processes()` and call `proc_table.refresh_processes(rows)`.
- Update footer label to include `p Processes`.

---

## Files Changed

| File | Nature of change |
|---|---|
| `src/sysmon/theme.py` | Rich CSS: borders, sparkline colours, bar colour classes, header/footer style |
| `src/sysmon/widgets.py` | Dynamic CSS classes on ProgressBar; new `ProcessTable` widget |
| `src/sysmon/collector.py` | New `collect_processes()` helper |
| `src/sysmon/app.py` | `p` binding, view toggle logic, process refresh, footer update |

---

## Notes / Constraints

- Textual's `DataTable` does not support in-place cell updates efficiently for many rows;
  use `clear()` + `add_rows()` each tick (acceptable for ≤ 25 rows at 1 Hz).
- `psutil.process_iter` with `cpu_percent` returns instantaneous values (non-blocking);
  first call may show 0 % for all processes — that is acceptable and matches htop behaviour.
- Keep the `t` theme toggle working as-is; CSS colour classes must work in both dark and
  light themes (use `$` token-based colours where possible).

---

## Iteration 2 — Fixes from Reviewer

### Fix A — CSS selector mismatch (`theme.py`)

The class `ok/warn/crit` is added to the **`ProgressBar`** widget in `widgets.py`, but
`theme.py` targets `MetricPanel ProgressBar Bar.ok` (the inner `Bar` sub-widget).
Fix: change to `MetricPanel ProgressBar.ok Bar` (and likewise for `warn`/`crit`).

### Fix B — `psutil.ZombieProcess` not caught (`collector.py`)

The except clause in `collect_processes()` catches `(psutil.AccessDenied, psutil.NoSuchProcess)`.
On Linux, zombie processes can raise `psutil.ZombieProcess` independently.
Fix: add `psutil.ZombieProcess` to the except tuple.

### Fix C — Tests for `collect_processes()` (`test_collector.py`)

Add a `TestCollectProcesses` class with:
- `test_returns_list_of_dicts` — real call returns a list of dicts with keys `pid, name, cpu_percent, mem_percent, status`.
- `test_sorted_by_cpu_descending` — mock two procs; assert order.
- `test_respects_n_limit` — mock >n procs; assert `len(result) <= n`.
- `test_access_denied_skipped` — mock proc that raises `AccessDenied`; assert not in result.
- `test_no_such_process_skipped` — mock proc that raises `NoSuchProcess`; assert not in result.
- `test_zombie_process_skipped` — mock proc that raises `ZombieProcess`; assert not in result.

### Fix D — Tests for `ProcessTable` widget (`test_widgets.py`)

Add a `TestProcessTable` class with:
- `test_refresh_empty_list` — mount `ProcessTable`, call `refresh_processes([])`, assert no crash and table has 0 rows.
- `test_refresh_valid_row` — call `refresh_processes([{valid row}])`, assert table has 1 row.

### Fix E — Async test for `p` binding / `action_toggle_processes()` (`test_widgets.py`)

Add a `TestProcessToggle` class with:
- `test_p_binding_toggles_views` — before press: `#main-view` visible, `#proc-view` hidden, `_show_processes == False`; after one `p` press: inverse; after second `p` press: back to original.

### Fix F — Test for ProgressBar CSS class thresholds (`test_widgets.py`)

Add a `TestMetricPanelThresholds` class with:
- `test_ok_class` — set `value = 0` (and 59.9), assert `ProgressBar` has class `ok`, not `warn`/`crit`.
- `test_warn_class` — set `value = 60` (and 85), assert class `warn`.
- `test_crit_class` — set `value = 85.1` (and 100), assert class `crit`.

---

## Files Changed (Iteration 2)

| File | Nature of change |
|---|---|
| `src/sysmon/theme.py` | Fix CSS selectors: `ProgressBar Bar.ok` → `ProgressBar.ok Bar` (and warn/crit) |
| `src/sysmon/collector.py` | Add `psutil.ZombieProcess` to except clause in `collect_processes()` |
| `tests/test_collector.py` | Add `TestCollectProcesses` class with 6 tests |
| `tests/test_widgets.py` | Add `TestProcessTable`, `TestProcessToggle`, `TestMetricPanelThresholds` classes |

