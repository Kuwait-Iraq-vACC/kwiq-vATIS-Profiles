"""
Bumps the "serial" field in any changed .json file.

Reads a newline-separated list of changed file paths (relative to repo root)
and, for each one that:
  - still exists (i.e. wasn't deleted)
  - ends in .json
  - parses as a JSON object containing an integer "serial" key
increments that "serial" value by 1 and rewrites the file in place,
preserving key order and using 2-space indentation.

Files without a top-level "serial" key are left untouched.

Uses only the Python standard library - no external dependencies required.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SERIAL_KEY = "updateSerial"


def load_changed_files(list_path: str) -> list[Path]:
    path = Path(list_path)
    if not path.exists():
        return []

    lines = path.read_text(encoding="utf-8").splitlines()
    return [Path(line.strip()) for line in lines if line.strip()]


def next_serial(old_serial: int, today: str) -> int:
    """
    vATIS-style serial format: YYYYMMDDNN (date + 2-digit sequence number).
    Same day as the existing serial -> increment NN.
    Different day (or unparsable) -> reset to today + 01.
    """
    old_str = str(old_serial)
    if len(old_str) == 10:
        old_date, old_seq = old_str[:8], old_str[8:]
        if old_date == today:
            return int(today + f"{int(old_seq) + 1:02d}")
    return int(today + "01")


def bump_serial(file_path: Path, today: str) -> bool:
    """Returns True if the file was modified."""
    if not file_path.exists() or file_path.suffix.lower() != ".json":
        return False

    try:
        text = file_path.read_text(encoding="utf-8")
        data = json.loads(text)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"  skip {file_path}: not valid JSON ({exc})")
        return False

    if not isinstance(data, dict) or SERIAL_KEY not in data:
        print(f"  skip {file_path}: no top-level '{SERIAL_KEY}' key")
        return False

    if not isinstance(data[SERIAL_KEY], int):
        print(f"  skip {file_path}: '{SERIAL_KEY}' is not an integer")
        return False

    old_serial = data[SERIAL_KEY]
    data[SERIAL_KEY] = next_serial(old_serial, today)

    file_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"  updated {file_path}: {SERIAL_KEY} {old_serial} -> {data[SERIAL_KEY]}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--changed-files-list",
        required=True,
        help="Path to a text file listing changed files, one per line.",
    )
    args = parser.parse_args()

    changed_files = load_changed_files(args.changed_files_list)
    json_files = [f for f in changed_files if f.suffix.lower() == ".json"]

    if not json_files:
        print("No changed .json files to process.")
        return 0

    today = datetime.now(timezone.utc).strftime("%Y%m%d")

    print(f"Processing {len(json_files)} changed JSON file(s):")
    any_updated = False
    for file_path in json_files:
        if bump_serial(file_path, today):
            any_updated = True

    if not any_updated:
        print("No files needed a serial bump.")

    return 0


if __name__ == "__main__":
    sys.exit(main())