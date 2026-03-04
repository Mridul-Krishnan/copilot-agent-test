# Requirements

## Project: sysmon

A **Terminal UI (TUI) system monitor** that displays live system stats with animated visuals.

### Core Requirements
- **Metrics displayed:** CPU usage (per-core + total), RAM usage, swap, disk I/O, network I/O (up/down)
- **Visuals:** Progress bars for current values + sparkline mini-graphs showing last ~60s of history
- **Refresh rate:** 1 second
- **Animated:** Smooth transitions / live-updating gauges and sparklines

### Technical Decisions
- **Language:** Python (>=3.10)
- **Package manager:** uv
- **TUI framework:** Textual (with Rich rendering)
- **Data collection:** psutil (cross-platform)
- **Build system:** hatchling (consistent with existing project conventions)
- **Project location:** `sysmon/` directory at repo root (self-contained)

### Nice-to-haves
- Keyboard shortcuts: `q` to quit, `t` to toggle theme (dark/light)
- Header showing hostname, OS, uptime
- Responsive layout that adapts to terminal size
