"""CLI argument parsing and main dispatch."""

import argparse
import ctypes
import ctypes.util
import sys

# Ensure system libxcb-cursor is loaded before Qt initializes (needed in WSL/PySide6)
_libxcb_cursor = ctypes.util.find_library("xcb-cursor")
if _libxcb_cursor:
    ctypes.CDLL(_libxcb_cursor)

from reverse_pomodoro.log import get_today_stats, reset_progression
from reverse_pomodoro.session import run_sessions


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reverse-pomodoro",
        description="Reverse Pomodoro Timer — start small, build momentum.",
    )
    parser.add_argument(
        "-w", "--work",
        type=int, default=5,
        help="starting work duration in minutes (default: 5)",
    )
    parser.add_argument(
        "-m", "--max",
        type=int, default=50,
        dest="max_duration",
        help="max work duration in minutes (default: 50)",
    )
    parser.add_argument(
        "-i", "--increment",
        type=int, default=5,
        help="growth increment in minutes (default: 5)",
    )
    parser.add_argument(
        "-b", "--break-duration",
        type=int, default=5,
        help="break duration in minutes (default: 5)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="show today's stats and exit",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="reset progression and exit",
    )
    parser.add_argument(
        "--log-file",
        type=str, default="./reverse-pomodoro.json",
        help="path to log file (default: ./reverse-pomodoro.json)",
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="run in terminal (no GUI window)",
    )
    return parser


def _ensure_qt_platform() -> None:
    """Set QT_QPA_PLATFORM if xcb-cursor is missing, or exit with helpful message."""
    import os
    if sys.platform != "linux":
        return  # xcb/xcb-cursor is Linux-only; other platforms handle Qt natively
    if "QT_QPA_PLATFORM" in os.environ:
        return  # already set by user
    if ctypes.util.find_library("xcb-cursor"):
        return  # xcb will work fine
    # xcb-cursor missing — try wayland
    if os.environ.get("WAYLAND_DISPLAY"):
        os.environ["QT_QPA_PLATFORM"] = "wayland"
        return
    # No viable GUI platform
    print("Error: libxcb-cursor0 is required for the GUI but is not installed.")
    print("  Fix: sudo apt install libxcb-cursor0")
    print("  Or run in terminal mode: uv run reverse-pomodoro --cli")
    sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.stats:
        stats = get_today_stats(args.log_file)
        print(f"📊 Today's Stats")
        print(f"  Sessions completed: {stats['sessions']}")
        print(f"  Total focus time:   {stats['focus_minutes']:.1f} min")
        print(f"  Current level:      {stats['level']}")
        sys.exit(0)

    if args.reset:
        reset_progression(args.log_file)
        print("🔄 Progression reset. Next session starts from the beginning.")
        sys.exit(0)

    if args.cli:
        run_sessions(args)
    else:
        _ensure_qt_platform()
        from reverse_pomodoro.gui import PomodoroApp
        PomodoroApp(args).run()
