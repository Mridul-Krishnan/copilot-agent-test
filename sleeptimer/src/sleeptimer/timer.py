"""Countdown timer state machine — pure Python, no Tkinter dependency."""

from __future__ import annotations

from typing import Callable, Optional

DEFAULT_MINUTES = 20


class CountdownTimer:
    """Countdown timer with start/pause/reset/tick semantics.

    Call :meth:`tick` externally once per second (e.g. from Tkinter's
    ``after()`` loop).  When the counter reaches zero :attr:`on_expire` is
    called exactly once.
    """

    def __init__(
        self,
        minutes: int = DEFAULT_MINUTES,
        on_expire: Optional[Callable[[], None]] = None,
    ) -> None:
        self._total_seconds: int = minutes * 60
        self._remaining: int = self._total_seconds
        self._running: bool = False
        self._expired: bool = False
        self.on_expire: Optional[Callable[[], None]] = on_expire

    # ------------------------------------------------------------------
    # Control methods
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start (or resume) the countdown."""
        if not self._expired:
            self._running = True

    def pause(self) -> None:
        """Pause the countdown."""
        self._running = False

    def toggle(self) -> None:
        """Toggle between running and paused."""
        if self._running:
            self.pause()
        else:
            self.start()

    def reset(self, minutes: int = DEFAULT_MINUTES) -> None:
        """Reset to *minutes* and stop the timer."""
        self._total_seconds = minutes * 60
        self._remaining = self._total_seconds
        self._running = False
        self._expired = False

    def add_minutes(self, n: int) -> None:
        """Add *n* minutes (may be negative).  Clamps to 0."""
        self._remaining = max(0, self._remaining + n * 60)
        # If the timer had expired and we add time, allow it to run again.
        if self._remaining > 0:
            self._expired = False

    # ------------------------------------------------------------------
    # Tick — called externally once per second
    # ------------------------------------------------------------------

    def tick(self) -> None:
        """Decrement by one second if running; fire expiry callback at 0."""
        if not self._running or self._expired:
            return
        if self._remaining > 0:
            self._remaining -= 1
        if self._remaining == 0:
            self._running = False
            self._expired = True
            if self.on_expire is not None:
                self.on_expire()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def display(self) -> str:
        """Return remaining time as an ``MM:SS`` string."""
        minutes, seconds = divmod(self._remaining, 60)
        return f"{minutes:02d}:{seconds:02d}"

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_expired(self) -> bool:
        return self._expired

    @property
    def remaining(self) -> int:
        return self._remaining
