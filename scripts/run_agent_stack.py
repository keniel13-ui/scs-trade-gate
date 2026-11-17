from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _required_env(names: list[str]) -> list[str]:
    return [name for name in names if not os.environ.get(name, "").strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the client Telegram chat plus Discord monitor from one terminal.")
    parser.add_argument("--no-discord", action="store_true", help="Run Telegram chat only.")
    args = parser.parse_args()

    required = ["SCS_TELEGRAM_BOT_TOKEN"]
    if not args.no_discord:
        required.extend(["SCS_DISCORD_BOT_TOKEN", "SCS_DISCORD_CHANNEL_IDS", "SCS_TELEGRAM_CHAT_ID"])
    missing = _required_env(required)
    if missing:
        print("Missing required environment variables:", ", ".join(missing), file=sys.stderr)
        print("Set them, then rerun this script.", file=sys.stderr)
        return 2

    commands = [
        [sys.executable, "scripts/telegram_bot.py"],
    ]
    if not args.no_discord:
        commands.append([sys.executable, "scripts/discord_monitor.py"])

    processes: list[subprocess.Popen] = []
    try:
        for command in commands:
            processes.append(subprocess.Popen(command, cwd=ROOT))
        print("the client agent stack is running. Press Ctrl+C here to stop all processes.")
        for process in processes:
            process.wait()
    except KeyboardInterrupt:
        print("\nStopping the client agent stack...")
    finally:
        for process in processes:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.terminate()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

