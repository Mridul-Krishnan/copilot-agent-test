"""Session management — progression, run loop, Ctrl+C handling."""

import signal
import sys
import time
from datetime import datetime

from reverse_pomodoro import timer
from reverse_pomodoro.log import append_entry, count_completed_work_sessions, load_log


def _sigint_handler(signum, frame):
    """Set the interrupted flag so the timer exits cleanly."""
    timer.interrupted = True


def _calc_work_duration(completed: int, initial: int, increment: int, maximum: int) -> int:
    """Calculate current work duration in minutes based on progression."""
    return min(initial + completed * increment, maximum)


def run_sessions(args) -> None:
    """Main session loop: work → break → work → break..."""
    original_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, _sigint_handler)

    log = load_log(args.log_file)
    completed = count_completed_work_sessions(log)

    try:
        while True:
            # --- Work session ---
            work_mins = _calc_work_duration(
                completed, args.work, args.increment, args.max_duration
            )
            work_secs = work_mins * 60
            print(f"\n⏱️  Work session #{completed + 1} — {work_mins} min")
            start = time.time()
            finished = timer.countdown(work_secs, f"Work {work_mins}m")
            elapsed = int(time.time() - start)

            entry = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "type": "work",
                "planned_duration": work_secs,
                "actual_duration": elapsed,
                "completed": finished,
            }
            append_entry(args.log_file, entry)

            if not finished:
                print(f"\n⏹️  Session interrupted. {elapsed}s saved.")
                break

            completed += 1

            # --- Break ---
            break_secs = args.break_duration * 60
            print(f"\n☕ Break — {args.break_duration} min")
            start = time.time()
            finished = timer.countdown(break_secs, f"Break {args.break_duration}m")
            elapsed = int(time.time() - start)

            entry = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "type": "break",
                "planned_duration": break_secs,
                "actual_duration": elapsed,
                "completed": finished,
            }
            append_entry(args.log_file, entry)

            if not finished:
                print(f"\n⏹️  Break interrupted. Exiting.")
                break

    finally:
        signal.signal(signal.SIGINT, original_handler)
