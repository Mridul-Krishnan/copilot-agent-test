"""Tkinter GUI for Reverse Pomodoro — drives the session loop via root.after()."""

import tkinter as tk
from datetime import datetime

from reverse_pomodoro.log import (
    append_entry,
    count_completed_work_sessions,
    load_log,
)

_BLINK_COLORS = ["orange", "white"]
_BLINK_COUNT = 16  # 8 pairs × 2 = 16 half-second flashes


class PomodoroApp:
    def __init__(self, args) -> None:
        self.args = args
        self.root = tk.Tk()
        self.root.title("Reverse Pomodoro")
        self.root.resizable(True, True)

        # Draggable window: small floating size
        self.root.geometry("360x200")

        self._log = load_log(args.log_file)
        self._completed = count_completed_work_sessions(self._log)
        self._session_start: float | None = None
        self._tick_job = None
        self._partial_entry: dict | None = None  # for on-destroy save

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.root.configure(bg="white")

        self._label_session = tk.Label(
            self.root, text="", font=("Helvetica", 14, "bold"),
            bg="white", fg="#333"
        )
        self._label_session.pack(pady=(18, 4))

        self._label_time = tk.Label(
            self.root, text="00:00", font=("Helvetica", 42, "bold"),
            bg="white", fg="#111"
        )
        self._label_time.pack()

        # Progress bar (Canvas)
        self._canvas = tk.Canvas(self.root, height=14, bg="#e0e0e0", highlightthickness=0)
        self._canvas.pack(fill=tk.X, padx=24, pady=10)
        self._bar = self._canvas.create_rectangle(0, 0, 0, 14, fill="#ff6b35", outline="")

        self._btn_next = tk.Button(
            self.root, text="▶ Next", font=("Helvetica", 13),
            command=self._advance, state=tk.DISABLED,
            bg="#ff6b35", fg="white", relief=tk.FLAT, padx=14, pady=6,
        )
        self._btn_next.pack(pady=4)

    # ------------------------------------------------------------------
    # Session logic
    # ------------------------------------------------------------------

    def _calc_work_secs(self) -> int:
        mins = min(
            self.args.work + self._completed * self.args.increment,
            self.args.max_duration,
        )
        return mins * 60

    def _start_work(self) -> None:
        self.root.configure(bg="white")
        self._label_session.configure(bg="white")
        self._label_time.configure(bg="white")
        self._btn_next.configure(state=tk.DISABLED)

        self._total_secs = self._calc_work_secs()
        work_mins = self._total_secs // 60
        self._label_session.configure(
            text=f"🍅 Work #{self._completed + 1} — {work_mins}m"
        )
        self._session_type = "work"
        self._session_start = _now()
        self._partial_entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "type": "work",
            "planned_duration": self._total_secs,
        }
        self._tick(self._total_secs)

    def _start_break(self) -> None:
        self.root.configure(bg="white")
        self._label_session.configure(bg="white")
        self._label_time.configure(bg="white")
        self._btn_next.configure(state=tk.DISABLED)

        self._total_secs = self.args.break_duration * 60
        self._label_session.configure(text=f"☕ Break — {self.args.break_duration}m")
        self._session_type = "break"
        self._session_start = _now()
        self._partial_entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "type": "break",
            "planned_duration": self._total_secs,
        }
        self._tick(self._total_secs)

    def _tick(self, remaining: int) -> None:
        # Update countdown label
        mins, secs = divmod(remaining, 60)
        self._label_time.configure(text=f"{mins:02d}:{secs:02d}")

        # Update progress bar
        self.root.update_idletasks()
        width = self._canvas.winfo_width()
        if width > 1 and self._total_secs > 0:
            filled = int(width * (self._total_secs - remaining) / self._total_secs)
            self._canvas.coords(self._bar, 0, 0, filled, 14)

        if remaining == 0:
            self._on_complete()
        else:
            self._tick_job = self.root.after(1000, self._tick, remaining - 1)

    def _on_complete(self) -> None:
        elapsed = int(_now() - self._session_start) if self._session_start else self._total_secs
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "type": self._session_type,
            "planned_duration": self._total_secs,
            "actual_duration": elapsed,
            "completed": True,
        }
        append_entry(self.args.log_file, entry)
        self._partial_entry = None  # already saved

        if self._session_type == "work":
            self._completed += 1

        # Grab attention
        try:
            self.root.state("normal")
            self.root.attributes("-zoomed", True)
        except tk.TclError:
            pass
        self.root.lift()
        self.root.focus_force()
        self.root.attributes("-topmost", True)

        self._blink(_BLINK_COUNT, _BLINK_COLORS)

    def _blink(self, count: int, colors: list[str]) -> None:
        if count == 0:
            self._show_next_button()
            return
        color = colors[count % 2]
        self.root.configure(bg=color)
        self._label_session.configure(bg=color)
        self._label_time.configure(bg=color)
        self.root.after(500, self._blink, count - 1, colors)

    def _show_next_button(self) -> None:
        self.root.configure(bg="white")
        self._label_session.configure(bg="white")
        self._label_time.configure(bg="white")
        self._btn_next.configure(state=tk.NORMAL)
        self.root.attributes("-topmost", False)

    def _advance(self) -> None:
        """Called when user clicks ▶ Next."""
        if self._session_type == "work":
            self._start_break()
        else:
            self._start_work()

    # ------------------------------------------------------------------
    # Window close — save partial entry if mid-session
    # ------------------------------------------------------------------

    def _on_close(self) -> None:
        if self._tick_job is not None:
            self.root.after_cancel(self._tick_job)
        if self._partial_entry is not None and self._session_start is not None:
            elapsed = int(_now() - self._session_start)
            entry = {**self._partial_entry, "actual_duration": elapsed, "completed": False}
            append_entry(self.args.log_file, entry)
        self.root.destroy()

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        self._start_work()
        self.root.mainloop()


def _now() -> float:
    import time
    return time.time()
