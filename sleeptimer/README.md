# sleeptimer

A cross-platform desktop countdown timer that **sleeps** or **logs out** your machine when the time runs out. Defaults to 20 minutes. Built with Python + Tkinter and lives in your system tray.

---

## Installation

Requires [uv](https://github.com/astral-sh/uv).

```bash
git clone <repo-url>
cd sleeptimer
uv sync
```

## Running

```bash
uv run sleeptimer
```

---

## Key Bindings

| Key | Action |
|-----|--------|
| `Up` / `+` | +1 minute |
| `Down` / `-` | −1 minute |
| `r` / `R` | Reset to 20 minutes |
| `Space` | Pause / Resume |

---

## Buttons

| Button | Action |
|--------|--------|
| ▶ Start / ⏸ Pause | Toggle countdown |
| + 1 min | Add one minute |
| − 1 min | Subtract one minute |
| ↺ Reset | Reset to 20 minutes |
| ⏾ Sleep / ⏏ Logout | Toggle the expiry action |

---

## System Tray

Closing the window **minimises to tray** rather than quitting. Right-click the tray icon for:

- **Show** — bring the window back
- **Quit** — exit the application

---

## Platform Notes

### Windows
Sleep and logout use `rundll32` / `shutdown /l` — no extra dependencies.

### macOS
Sleep uses `pmset sleepnow`; logout uses AppleScript via `osascript`.

### Linux
Sleep uses `systemctl suspend`; logout uses `loginctl terminate-session self`.

The system tray on Linux requires either **AppIndicator** (GTK) or **Xlib**:

```bash
# Debian / Ubuntu
sudo apt install python3-gi gir1.2-appindicator3-0.1

# or install python-xlib (already a dependency via pystray)
```

If tray support is unavailable, the app will still run — close the window via the OS task-bar instead.

---

## Platform Actions

| Platform | Sleep command | Logout command |
|----------|--------------|----------------|
| Windows  | `rundll32 powrprof.dll,SetSuspendState 0,1,0` | `shutdown /l` |
| macOS    | `pmset sleepnow` | AppleScript log out |
| Linux    | `systemctl suspend` | `loginctl terminate-session self` |
