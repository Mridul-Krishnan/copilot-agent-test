# Requirements

## Reverse Pomodoro Timer CLI (Python)

Build a CLI tool in Python that implements the **reverse Pomodoro technique** — starts with short work sessions and gradually increases duration as momentum builds.

### Core Features

1. **Configurable parameters via CLI args:**
   - `--work` / `-w`: starting work duration (default 5 min)
   - `--max` / `-m`: maximum work duration (default 50 min)
   - `--increment` / `-i`: growth increment per session (default 5 min)
   - `--break` / `-b`: break duration (default 5 min)

2. **Progressive work sessions:** Each completed work session increases the next by the increment, capped at max.

3. **Live countdown display** in the terminal (updates in-place).

4. **System bell (`\a`)** when a session ends.

5. **Session logging** to `reverse-pomodoro.json`:
   - Timestamp, session type (work/break), planned duration (seconds)

6. **`--stats` flag:** Show today's sessions, total focus time, and current session progression.

7. **`--reset` flag:** Restart progression from the initial short duration (clears progression state in log).

### Documentation

8. **GUIDE.md** covering:
   - What the reverse Pomodoro technique is and why it helps with procrastination/ADHD
   - Installation and usage instructions
   - Examples of all CLI flags
   - Tips for getting the most out of it
