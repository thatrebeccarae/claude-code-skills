#!/usr/bin/env python3
"""Validate a GA4 event spec JSON file against the schema."""

import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <event-spec.json>")
        sys.exit(1)

    spec_path = Path(sys.argv[1])
    schema_path = Path(__file__).parent.parent / "schemas" / "event-spec.schema.json"

    if not spec_path.exists():
        print(f"ERROR: File not found: {spec_path}")
        sys.exit(1)

    with open(schema_path) as f:
        schema = json.load(f)

    with open(spec_path) as f:
        spec = json.load(f)

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(spec), key=lambda e: list(e.path))

    if not errors:
        groups = len(spec.get("event_groups", []))
        events = sum(len(g.get("events", [])) for g in spec.get("event_groups", []))
        print(f"VALID: {spec_path.name} ({groups} groups, {events} events)")
        sys.exit(0)

    print(f"INVALID: {spec_path.name} ({len(errors)} error(s))")
    for error in errors:
        path = ".".join(str(p) for p in error.path) or "(root)"
        print(f"  - {path}: {error.message}")
    sys.exit(1)


if __name__ == "__main__":
    main()
