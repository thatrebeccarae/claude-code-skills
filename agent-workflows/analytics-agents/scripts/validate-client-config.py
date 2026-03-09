#!/usr/bin/env python3
"""Validate a client config JSON file against the schema."""

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
        print(f"Usage: {sys.argv[0]} <config.json>")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    schema_path = Path(__file__).parent.parent / "schemas" / "client-config.schema.json"

    if not config_path.exists():
        print(f"ERROR: File not found: {config_path}")
        sys.exit(1)

    with open(schema_path) as f:
        schema = json.load(f)

    with open(config_path) as f:
        config = json.load(f)

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(config), key=lambda e: list(e.path))

    if not errors:
        print(f"VALID: {config_path.name}")
        sys.exit(0)

    print(f"INVALID: {config_path.name} ({len(errors)} error(s))")
    for error in errors:
        path = ".".join(str(p) for p in error.path) or "(root)"
        print(f"  - {path}: {error.message}")
    sys.exit(1)


if __name__ == "__main__":
    main()
