"""Countdown display with progress bar."""

import sys
import time


# Flag set by session.py's SIGINT handler
interrupted = False


def countdown(duration_seconds: int, label: str) -> bool:
    """Display a live countdown. Returns True if completed, False if interrupted."""
    global interrupted

    total = duration_seconds
    for remaining in range(duration_seconds, 0, -1):
        if interrupted:
            return False

        mins, secs = divmod(remaining, 60)
        pct = (total - remaining) / total
        bar_len = 20
        filled = int(bar_len * pct)
        bar = "█" * filled + "░" * (bar_len - filled)

        sys.stdout.write(f"\r🍅 {label} [{mins:02d}:{secs:02d}] {bar} {pct * 100:.0f}%  ")
        sys.stdout.flush()

        time.sleep(1)

        if interrupted:
            return False

    # Completed
    bar = "█" * 20
    sys.stdout.write(f"\r🍅 {label} [00:00] {bar} 100%  \n")
    sys.stdout.flush()
    sys.stdout.write("\a")  # system bell
    sys.stdout.flush()
    return True
