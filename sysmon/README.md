# sysmon

A terminal-based system monitor built with [Textual](https://textual.textualize.io/) and [psutil](https://github.com/giampaolo/psutil).

Displays live CPU, RAM, swap, disk I/O, and network I/O stats with progress bars and sparkline history graphs, refreshing every second.

## Screenshot

*(placeholder — run `sysmon` to see it live)*

## Install & Run

```bash
# From the sysmon/ directory:
uv sync
uv run sysmon
```

## Key Bindings

| Key | Action        |
|-----|---------------|
| `q` | Quit          |
| `t` | Toggle theme  |

## Architecture

```
src/sysmon/
├── app.py        # Main Textual app, layout, key bindings, timer
├── collector.py  # psutil wrapper — SystemSnapshot dataclass + collect()
├── widgets.py    # MetricPanel (bar + sparkline), IOMetricPanel (sparkline)
└── theme.py      # Dark/light CSS theme strings
```

- **Collector** gathers system stats into a `SystemSnapshot` dataclass each tick.
- **MetricPanel** displays a percentage metric with a progress bar and sparkline.
- **IOMetricPanel** displays a rate-based metric (bytes/sec) with a sparkline.
- The app maintains 60-second `deque` histories for each metric's sparkline.
