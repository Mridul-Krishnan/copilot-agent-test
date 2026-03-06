"""Unit tests for SleepTimerApp GUI (headless, no display required)."""

from __future__ import annotations

import tkinter as tk
from unittest.mock import MagicMock, patch


def test_autostart():
    """SleepTimerApp.__init__ must call timer.start() automatically."""

    mock_timer_instance = MagicMock()

    with (
        patch.object(tk.Tk, "__init__", return_value=None),
        patch.object(tk.Tk, "title"),
        patch.object(tk.Tk, "configure"),
        patch.object(tk.Tk, "resizable"),
        patch.object(tk.Tk, "protocol"),
        patch.object(tk.Tk, "after"),
        patch.object(tk.Tk, "bind"),
        patch("sleeptimer.gui.tkfont.Font"),
        patch("sleeptimer.gui.tk.StringVar"),
        patch("sleeptimer.gui.tk.Label"),
        patch("sleeptimer.gui.tk.Button"),
        patch("sleeptimer.gui.tk.Frame"),
        patch("sleeptimer.gui.CountdownTimer", return_value=mock_timer_instance),
    ):
        from sleeptimer.gui import SleepTimerApp

        app = SleepTimerApp(
            action_sleep=MagicMock(),
            action_lock=MagicMock(),
        )

    mock_timer_instance.start.assert_called_once()
