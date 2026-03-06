"""Tkinter GUI for the sleep timer."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import font as tkfont
from typing import Callable, Optional

from sleeptimer.timer import CountdownTimer


class SleepTimerApp(tk.Tk):
    """Main application window."""

    def __init__(
        self,
        action_sleep: Callable[[], None],
        action_lock: Callable[[], None],
    ) -> None:
        super().__init__()

        self._action_sleep = action_sleep
        self._action_lock = action_lock
        self._use_sleep: bool = False  # False → Lock (default), True → Sleep

        self.title("Sleep Timer")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")

        self._timer = CountdownTimer(minutes=20, on_expire=self._on_expire)

        self._build_ui()
        self._bind_keys()
        self._timer.start()  # auto-start countdown on launch

        # Hide window → tray instead of destroy
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Start polling loop
        self._tick()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}

        # ── Display ────────────────────────────────────────────────────
        display_font = tkfont.Font(family="Courier", size=96, weight="bold")
        self._display_var = tk.StringVar(value=self._timer.display)
        self._display_label = tk.Label(
            self,
            textvariable=self._display_var,
            font=display_font,
            bg="#1e1e2e",
            fg="#cdd6f4",
        )
        self._display_label.pack(**pad)

        # ── Action toggle ──────────────────────────────────────────────
        self._action_btn = tk.Button(
            self,
            text="🔒  Lock",
            font=("Segoe UI", 14),
            width=14,
            bg="#313244",
            fg="#fab387",
            activebackground="#45475a",
            relief=tk.FLAT,
            command=self._toggle_action,
        )
        self._action_btn.pack(**pad)

        # ── Control buttons ────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg="#1e1e2e")
        btn_frame.pack(**pad)

        btn_cfg = dict(font=("Segoe UI", 12), width=8, bg="#313244", fg="#cdd6f4",
                       activebackground="#45475a", relief=tk.FLAT)

        self._pause_btn = tk.Button(btn_frame, text="▶ Start", command=self._toggle_pause, **btn_cfg)
        self._pause_btn.grid(row=0, column=0, padx=4, pady=4)

        tk.Button(btn_frame, text="+ 1 min", command=self._add_minute, **btn_cfg).grid(
            row=0, column=1, padx=4, pady=4
        )
        tk.Button(btn_frame, text="− 1 min", command=self._sub_minute, **btn_cfg).grid(
            row=0, column=2, padx=4, pady=4
        )
        tk.Button(btn_frame, text="↺ Reset", command=self._reset, **btn_cfg).grid(
            row=0, column=3, padx=4, pady=4
        )

    def _bind_keys(self) -> None:
        self.bind("<Up>", lambda _e: self._add_minute())
        self.bind("<plus>", lambda _e: self._add_minute())
        self.bind("<KP_Add>", lambda _e: self._add_minute())
        self.bind("<Down>", lambda _e: self._sub_minute())
        self.bind("<minus>", lambda _e: self._sub_minute())
        self.bind("<KP_Subtract>", lambda _e: self._sub_minute())
        self.bind("<r>", lambda _e: self._reset())
        self.bind("<R>", lambda _e: self._reset())
        self.bind("<space>", lambda _e: self._toggle_pause())

    # ------------------------------------------------------------------
    # Periodic tick
    # ------------------------------------------------------------------

    def _tick(self) -> None:
        self._timer.tick()
        self._refresh_display()
        try:
            self.after(1000, self._tick)
        except tk.TclError:
            return

    def _refresh_display(self) -> None:
        self._display_var.set(self._timer.display)
        if self._timer.is_running:
            self._pause_btn.configure(text="⏸ Pause")
            self._display_label.configure(fg="#cdd6f4")
        elif self._timer.is_expired:
            self._pause_btn.configure(text="▶ Start")
            self._display_label.configure(fg="#f38ba8")
        else:
            self._pause_btn.configure(text="▶ Start")
            self._display_label.configure(fg="#a6e3a1")

    # ------------------------------------------------------------------
    # Button / key handlers
    # ------------------------------------------------------------------

    def _toggle_pause(self) -> None:
        self._timer.toggle()
        self._refresh_display()

    def _add_minute(self) -> None:
        self._timer.add_minutes(1)
        self._refresh_display()

    def _sub_minute(self) -> None:
        self._timer.add_minutes(-1)
        self._refresh_display()

    def _reset(self) -> None:
        self._timer.reset(minutes=20)
        self._refresh_display()

    def _toggle_action(self) -> None:
        self._use_sleep = not self._use_sleep
        if self._use_sleep:
            self._action_btn.configure(text="⏾  Sleep", fg="#89dceb")
        else:
            self._action_btn.configure(text="🔒  Lock", fg="#fab387")

    # ------------------------------------------------------------------
    # Expiry / close
    # ------------------------------------------------------------------

    def _on_expire(self) -> None:
        """Called by the timer when countdown reaches zero."""
        def run() -> None:
            try:
                if self._use_sleep:
                    self._action_sleep()
                else:
                    self._action_lock()
            except Exception as exc:  # noqa: BLE001
                # Schedule UI update back on the Tk thread
                self.after(0, lambda: self._display_var.set("ERR"))
                print(f"[sleeptimer] Action failed: {exc}")

        threading.Thread(target=run, daemon=True).start()

    def _on_close(self) -> None:
        """Hide window (minimize to tray) instead of destroying it."""
        self.withdraw()
