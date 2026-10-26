"""
Validates every vATIS profile in the repository.

Checks that each profile:
  - parses as JSON and has a name, updateUrl, updateSerial and stations
  - has an updateUrl pointing at its own path on main
  - has an updateSerial in YYYYMMDDNN format
  - has unique station, preset and static-definition ids/ordinals
  - only uses known [VARIABLES] in preset templates
  - has balanced parentheses in online/weather conditions

Exits non-zero if any error is found. Uses only the Python standard library.
"""

import json
import re
import sys
from pathlib import Path

REPO = "Kuwait-Iraq-vACC/kwiq-vATIS-Profiles"
URL_PREFIX = f"https://raw.githubusercontent.com/{REPO}/refs/heads/main/"

KNOWN_VARIABLES = {
    "FACILITY", "ATIS_CODE", "ATIS_LETTER", "LETTER", "ID", "WX", "FULL_WX_STRING", "METAR",
    "OBS_TIME", "OBSTIME", "TIME", "WIND", "SURFACE_WIND", "RVR", "VIS", "PREVAILING_VISIBILITY",
    "PRESENT_WX", "PRESENT_WEATHER", "CLOUDS", "TEMP", "DEW", "PRESSURE", "QNH", "TREND",
    "RECENT_WX", "WS", "RWY_COND", "RUNWAY_CONDITION", "RMK_WIND", "AUTO", "ARPT_COND", "ARRDEP",
    "NOTAMS", "TL", "CLOSING",
}
VARIABLE_RE = re.compile(r"\[([A-Z_]+)(?::VOX)?\]")
DYNAMIC_VARIABLE_RE = re.compile(r"\[(PRESSURE_[A-Z0-9]{4}|QFE\|-?\d+)(?::VOX)?\]")
SERIAL_RE = re.compile(r"^\d{8}\d{2}$")


def check_unique(errors, where, items, key):
    seen = set()
    for item in items:
        value = item.get(key)
        if value in seen:
            errors.append(f"{where}: duplicate {key} {value!r}")
        seen.add(value)


def check_condition(errors, where, text):
    depth = 0
    for char in text:
        depth += char == "("
        depth -= char == ")"
        if depth < 0:
            break
    if depth != 0:
        errors.append(f"{where}: unbalanced parentheses in condition {text!r}")


def validate_station(errors, profile, station):
    where = f"{profile}:{station.get('identifier', '?')}"

    check_unique(errors, f"{where} presets", station.get("presets", []), "id")
    check_unique(errors, f"{where} presets", station.get("presets", []), "ordinal")
    check_unique(errors, f"{where} presets", station.get("presets", []), "name")

    for preset in station.get("presets", []):
        template = preset.get("template") or ""
        stripped = DYNAMIC_VARIABLE_RE.sub("", template)
        for variable in VARIABLE_RE.findall(stripped):
            if variable not in KNOWN_VARIABLES:
                errors.append(f"{where} preset {preset.get('name')!r}: unknown variable [{variable}]")

    for kind in ("airportConditionDefinitions", "notamDefinitions"):
        definitions = station.get(kind, [])
        check_unique(errors, f"{where} {kind}", definitions, "ordinal")
        for definition in definitions:
            for key in ("onlineCondition", "weatherCondition"):
                if definition.get(key):
                    check_condition(errors, f"{where} {kind} {definition.get('text')!r}", definition[key])

    names = [c.get("variableName") for c in station.get("contractions", [])]
    for name in {n for n in names if names.count(n) > 1}:
        errors.append(f"{where}: duplicate contraction {name!r}")

    for pattern in station.get("patterns", []):
        try:
            re.compile(pattern.get("pattern", ""))
        except re.error as exc:
            errors.append(f"{where}: invalid pattern {pattern.get('pattern')!r} ({exc})")


def validate_profile(path: Path) -> list[str]:
    errors = []
    rel = path.as_posix()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"{rel}: not valid JSON ({exc})"]

    for key in ("name", "updateUrl", "updateSerial", "stations"):
        if key not in data:
            errors.append(f"{rel}: missing top-level '{key}'")

    if data.get("updateUrl") and data["updateUrl"] != URL_PREFIX + rel:
        errors.append(f"{rel}: updateUrl should be {URL_PREFIX + rel}")

    if "updateSerial" in data and not SERIAL_RE.match(str(data["updateSerial"])):
        errors.append(f"{rel}: updateSerial {data['updateSerial']} is not YYYYMMDDNN")

    stations = data.get("stations", [])
    check_unique(errors, rel, stations, "id")
    check_unique(errors, rel, stations, "identifier")
    for station in stations:
        validate_station(errors, rel, station)

    return errors


def main() -> int:
    profiles = sorted(p for p in Path(".").glob("*/*.json") if not p.parts[0].startswith("."))
    if not profiles:
        print("No profiles found.")
        return 1

    errors = []
    for profile in profiles:
        profile_errors = validate_profile(profile)
        status = "FAIL" if profile_errors else "ok"
        print(f"  {status:4} {profile.as_posix()}")
        errors.extend(profile_errors)

    if errors:
        print(f"\n{len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"\nAll {len(profiles)} profile(s) valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
