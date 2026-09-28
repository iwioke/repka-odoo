import argparse
import subprocess
import sys
from pathlib import Path

from engine import SCENARIOS


ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Каталог Repka AI Automations (DEMO)")
    parser.add_argument("scenario", nargs="?", choices=SCENARIOS)
    parser.add_argument("--list", action="store_true", help="Список сценариев")
    args = parser.parse_args()
    if args.scenario:
        return subprocess.call([sys.executable, str(ROOT / args.scenario / "run.py")])
    for index, (slug, title) in enumerate(SCENARIOS.items(), 1):
        print(f"{index}. {title} ({slug}; DEMO, deterministic rules)")
    if args.list or not sys.stdin.isatty():
        return 0
    choice = input("Номер сценария (Enter — выход): ").strip()
    if not choice:
        return 0
    if not choice.isdecimal() or not 1 <= int(choice) <= len(SCENARIOS):
        parser.error("Выберите номер из списка")
    slug = list(SCENARIOS)[int(choice) - 1]
    return subprocess.call([sys.executable, str(ROOT / slug / "run.py")])


if __name__ == "__main__":
    raise SystemExit(main())
