"""Entry point — wires GUI, tray icon, and platform actions."""

from __future__ import annotations

import sys

if sys.platform.startswith("linux"):
    import ctypes
    import ctypes.util
    # Load libxcb-cursor so PySide6/Qt xcb plugin can find it in WSL
    _libxcb_cursor = ctypes.util.find_library("xcb-cursor")
    if _libxcb_cursor:
        ctypes.CDLL(_libxcb_cursor)

import threading

import pystray
from PIL import Image, ImageDraw

from sleeptimer import actions
from sleeptimer.gui import SleepTimerApp


def _make_tray_icon(size: int = 64) -> Image.Image:
    """Generate a simple filled-circle tray icon at runtime (no asset files)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 4
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill="#89dceb",
        outline="#cdd6f4",
        width=3,
    )
    return img


def main() -> None:
    app = SleepTimerApp(
        action_sleep=actions.sleep_machine,
        action_lock=actions.lock_machine,
    )

    icon: pystray.Icon | None = None

    def show(_icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        app.after(0, app.deiconify)

    def quit_app(_icon: pystray.Icon, _item: pystray.MenuItem) -> None:
        app.after(0, app.destroy)
        _icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem("Show", show, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_app),
    )

    icon = pystray.Icon(
        name="sleeptimer",
        icon=_make_tray_icon(),
        title="Sleep Timer",
        menu=menu,
    )

    tray_thread = threading.Thread(target=icon.run, daemon=True)
    tray_thread.start()

    app.mainloop()

    # Ensure tray icon stops when the window is destroyed
    if icon is not None:
        icon.stop()


if __name__ == "__main__":
    main()
