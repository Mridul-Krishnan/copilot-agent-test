"""CLI argument parsing and main dispatch."""

import argparse
import sys

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
    return parser


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

    run_sessions(args)
