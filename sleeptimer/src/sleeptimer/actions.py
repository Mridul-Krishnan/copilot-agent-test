"""Platform-specific sleep and lock actions."""

from __future__ import annotations

import subprocess
import sys


def sleep_machine() -> None:
    """Put the machine to sleep using the appropriate OS command."""
    if sys.platform == "win32":
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
    elif sys.platform == "darwin":
        subprocess.run(["pmset", "sleepnow"], check=True)
    elif sys.platform.startswith("linux"):
        subprocess.run(["systemctl", "suspend"], check=True)
    else:
        raise NotImplementedError(f"sleep_machine() is not supported on platform: {sys.platform!r}")


def lock_machine() -> None:
    """Lock the screen using the appropriate OS command."""
    if sys.platform == "win32":
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
    elif sys.platform == "darwin":
        try:
            subprocess.run(
                ["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession",
                 "-suspend"],
                check=True,
            )
        except FileNotFoundError:
            raise RuntimeError("lock_machine(): CGSession not found on this macOS installation")
    elif sys.platform.startswith("linux"):
        for cmd in (
            ["loginctl", "lock-session"],
            ["xdg-screensaver", "lock"],
            ["gnome-screensaver-command", "-l"],
        ):
            try:
                subprocess.run(cmd, check=True)
                return
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        raise RuntimeError("lock_machine(): no supported lock command found on this Linux system")
    else:
        raise NotImplementedError(f"lock_machine() is not supported on platform: {sys.platform!r}")
