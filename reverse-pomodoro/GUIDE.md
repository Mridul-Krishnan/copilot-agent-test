# Reverse Pomodoro Timer — GUIDE

## What Is the Reverse Pomodoro Technique?

The classic Pomodoro technique asks you to work for 25 minutes right away. That's great if you're already motivated — but terrible when you're procrastinating, overwhelmed, or dealing with ADHD.

The **reverse Pomodoro** flips the script: **start with a tiny commitment** (5 minutes), then gradually increase. Each time you complete a session, the next one grows a little longer. By the time you're doing 25- or 50-minute sessions, you've already built momentum and focus.

This works because:
- **Starting is the hardest part.** 5 minutes feels effortless.
- **Momentum compounds.** Once you're in flow, longer sessions feel natural.
- **It removes the "all-or-nothing" trap.** Even one 5-minute session is progress.

## Linux Prerequisites

The GUI requires several system X11/xcb libraries (needed by PySide6's Qt xcb platform plugin). This is especially relevant on **WSL** or minimal Linux installs that don't have a full desktop environment.

Install all required libraries in one command:

```bash
sudo apt install -y libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
  libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
  libxcb-shape0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0
```

If you'd rather not install GUI dependencies, use CLI mode instead:

```bash
uv run reverse-pomodoro --cli
```

## Installation

```bash
# Using uv (recommended)
cd reverse-pomodoro/
uv sync
uv run reverse-pomodoro

# Or install with pip
pip install -e reverse-pomodoro/
reverse-pomodoro
```

## Usage

### Start a session (defaults — GUI mode)

```bash
uv run reverse-pomodoro
```

Opens a small floating GUI window. Starts at 5 min work, grows by 5 min each cycle, capped at 50 min. Breaks are 5 min. When a session ends the window maximizes, grabs focus, and blinks to get your attention. Click **▶ Next** to continue.

> **Linux/Wayland users:** If `activateWindow` doesn't bring the window to focus, you can force
> the xcb platform — but first ensure `libxcb-cursor0` is installed (see [Linux Prerequisites](#linux-prerequisites)):
> ```bash
> QT_QPA_PLATFORM=xcb uv run reverse-pomodoro
> ```

### Run in terminal (CLI mode)

```bash
uv run reverse-pomodoro --cli
```

Falls back to the original terminal countdown — no window needed.

### Customize durations

```bash
# Start at 3 min, grow by 3, max 30, with 2-min breaks
uv run reverse-pomodoro -w 3 -i 3 -m 30 -b 2
```

### Check today's stats

```bash
uv run reverse-pomodoro --stats
```

Output:
```
📊 Today's Stats
  Sessions completed: 4
  Total focus time:   50.0 min
  Current level:      4
```

### Reset progression

```bash
uv run reverse-pomodoro --reset
```

Resets your progression level so the next work session starts from the initial duration again.

### Custom log file

```bash
uv run reverse-pomodoro --log-file ~/my-pomodoro.json
```

## All CLI Flags

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--work` | `-w` | 5 | Starting work duration (minutes) |
| `--max` | `-m` | 50 | Maximum work duration (minutes) |
| `--increment` | `-i` | 5 | Growth per completed session (minutes) |
| `--break-duration` | `-b` | 5 | Break duration (minutes) |
| `--stats` | | | Show today's stats and exit |
| `--reset` | | | Reset progression and exit |
| `--cli` | | | Run in terminal instead of GUI |
| `--log-file` | | `./reverse-pomodoro.json` | Path to session log |

## Keyboard Shortcuts

The GUI supports the following keyboard shortcuts while the timer window is focused:

| Key | Action |
|-----|--------|
| `+` / `=` | Add 1 minute to the current session's remaining time |
| `-` | Subtract 1 minute from the current session's remaining time (minimum 1 second) |
| `R` | Reset the current session — restart from the full planned duration |
| `N` / `Enter` / `Space` | Advance to the next session (same as clicking **▶ Next**) |
| `←` / `→` | Move your player left/right in the Dodge mini-game (break sessions only) |

### Break Mini-Game — Dodge!

During break countdowns, a small **Dodge!** mini-game appears inside the timer window:

- A grid of 9 × 10 cells is displayed.
- Your player (`▲`) starts in the middle of the bottom row.
- Obstacles (`■`) spawn at the top and fall one row every ~400 ms.
- Use `←` / `→` to dodge them.
- Your **score** is the number of obstacles you successfully avoid.
- On collision the round ends and auto-restarts after 2 seconds.
- The mini-game hides automatically when a work session starts.

## Tips

1. **Start when motivation is lowest.** That's exactly when this technique shines — you only need to commit to 5 minutes.
2. **Pair with a task list.** Before starting, write down what you'll work on. Even "open the file and read it" counts.
3. **Don't skip breaks.** They're not optional — they prevent burnout and keep the technique sustainable.
4. **Use `--stats` for motivation.** Seeing accumulated focus time is a powerful motivator.
5. **Ctrl+C is OK.** If you must stop, the timer saves your partial session so it still counts toward your stats.
