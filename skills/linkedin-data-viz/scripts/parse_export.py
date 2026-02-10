#!/usr/bin/env python3
"""
parse_export.py - LinkedIn CSV export ingestion with quirk handling.

Parses LinkedIn data export CSVs into structured Python dicts. Handles
known quirks: junk header lines in Connections.csv, semicolons inside
Ad_Targeting cells, null conversation IDs in messages, and mixed date
formats across files.

Uses only Python 3.9+ stdlib (csv, json, datetime, pathlib, re).
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Date parsing
# ---------------------------------------------------------------------------

# Pattern: "12 Jan 2024"
_RE_DMY = re.compile(r"^\d{1,2}\s+\w{3}\s+\d{4}$")
# Pattern: "2024-01-12 08:30:45 UTC" or "2024-01-12 08:30:45"
_RE_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}")


def parse_date(raw: str | None) -> datetime | None:
    """Detect and parse LinkedIn's two common date formats.

    Handles:
        - ``DD Mon YYYY`` (e.g. "12 Jan 2024")
        - ``YYYY-MM-DD HH:MM:SS UTC`` or just ``YYYY-MM-DD``

    Returns None on failure and logs a warning.
    """
    if not raw or not raw.strip():
        return None
    raw = raw.strip()
    try:
        if _RE_DMY.match(raw):
            return datetime.strptime(raw, "%d %b %Y")
        if _RE_ISO.match(raw):
            # Strip trailing " UTC" if present
            cleaned = raw.replace(" UTC", "").strip()
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(cleaned, fmt)
                except ValueError:
                    continue
    except Exception as exc:
        logger.warning("Date parse failed for %r: %s", raw, exc)
    logger.warning("Unrecognised date format: %r", raw)
    return None


def _safe_strip(value: str | None) -> str:
    """Strip whitespace, return empty string for None."""
    return value.strip() if value else ""


# ---------------------------------------------------------------------------
# Individual parsers
# ---------------------------------------------------------------------------


def parse_connections(path: Path) -> list[dict[str, Any]]:
    """Parse Connections.csv.

    LinkedIn exports prepend 3 junk header lines (notes / blank) before the
    real CSV header row. We skip lines 0-2 and start the DictReader at line 3.
    """
    path = Path(path)
    if not path.exists():
        logger.warning("Connections file not found: %s", path)
        return []

    results: list[dict[str, Any]] = []
    try:
        text = path.read_text(encoding="utf-8-sig")
        lines = text.splitlines(keepends=True)
        # Skip the first 3 junk lines
        csv_text = "".join(lines[3:]) if len(lines) > 3 else "".join(lines)
        reader = csv.DictReader(StringIO(csv_text))
        for row in reader:
            try:
                results.append({
                    "first_name": _safe_strip(row.get("First Name")),
                    "last_name": _safe_strip(row.get("Last Name")),
                    "company": _safe_strip(row.get("Company")),
                    "position": _safe_strip(row.get("Position")),
                    "connected_on": parse_date(row.get("Connected On")),
                    "email_address": _safe_strip(row.get("Email Address")),
                })
            except Exception as exc:
                logger.warning("Skipping malformed connection row: %s", exc)
    except Exception as exc:
        logger.error("Failed to parse connections: %s", exc)
    return results


def parse_messages(path: Path) -> list[dict[str, Any]]:
    """Parse messages.csv.

    CONVERSATION ID may be null. We preserve the raw value so downstream
    code can group by non-null IDs and isolate orphans.
    """
    path = Path(path)
    if not path.exists():
        logger.warning("Messages file not found: %s", path)
        return []

    results: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                try:
                    conv_id = _safe_strip(row.get("CONVERSATION ID", ""))
                    results.append({
                        "conversation_id": conv_id if conv_id else None,
                        "sender": _safe_strip(
                            row.get("FROM")
                            or row.get("SENDER PROFILE URL")
                            or row.get("Sender")
                            or ""
                        ),
                        "date": parse_date(
                            row.get("DATE") or row.get("Date") or ""
                        ),
                        "subject": _safe_strip(
                            row.get("SUBJECT") or row.get("Subject") or ""
                        ),
                        "content": _safe_strip(
                            row.get("CONTENT") or row.get("Content") or ""
                        ),
                    })
                except Exception as exc:
                    logger.warning("Skipping malformed message row: %s", exc)
    except Exception as exc:
        logger.error("Failed to parse messages: %s", exc)
    return results


def parse_invitations(path: Path) -> list[dict[str, Any]]:
    """Parse Invitations.csv.

    Direction is inferred from ``Direction`` column or from presence of
    ``From``/``To`` fields.
    """
    path = Path(path)
    if not path.exists():
        logger.warning("Invitations file not found: %s", path)
        return []

    results: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                try:
                    direction_raw = _safe_strip(
                        row.get("Direction", "")
                    ).lower()
                    if "incoming" in direction_raw or "inbound" in direction_raw:
                        direction = "inbound"
                    elif "outgoing" in direction_raw or "outbound" in direction_raw:
                        direction = "outbound"
                    else:
                        # Heuristic: if "From" is populated, likely inbound
                        from_name = _safe_strip(row.get("From", ""))
                        direction = "inbound" if from_name else "outbound"

                    results.append({
                        "from_name": _safe_strip(
                            row.get("From") or row.get("From Name") or ""
                        ),
                        "to_name": _safe_strip(
                            row.get("To") or row.get("To Name") or ""
                        ),
                        "date": parse_date(
                            row.get("Sent At") or row.get("Date") or ""
                        ),
                        "direction": direction,
                        "message": _safe_strip(
                            row.get("Message") or row.get("message") or ""
                        ),
                    })
                except Exception as exc:
                    logger.warning("Skipping malformed invitation row: %s", exc)
    except Exception as exc:
        logger.error("Failed to parse invitations: %s", exc)
    return results


def parse_company_follows(path: Path) -> list[dict[str, Any]]:
    """Parse Company Follows.csv (or Company_Follows.csv)."""
    path = Path(path)
    if not path.exists():
        logger.warning("Company follows file not found: %s", path)
        return []

    results: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                try:
                    results.append({
                        "company": _safe_strip(
                            row.get("Organization")
                            or row.get("Company")
                            or row.get("Organization Name")
                            or ""
                        ),
                        "followed_on": parse_date(
                            row.get("Followed On")
                            or row.get("Date")
                            or ""
                        ),
                    })
                except Exception as exc:
                    logger.warning(
                        "Skipping malformed company follow row: %s", exc
                    )
    except Exception as exc:
        logger.error("Failed to parse company follows: %s", exc)
    return results


def parse_inferences(path: Path) -> list[dict[str, Any]]:
    """Parse Inferences_about_you.csv (LinkedIn's ad inferences)."""
    path = Path(path)
    if not path.exists():
        logger.warning("Inferences file not found: %s", path)
        return []

    results: list[dict[str, Any]] = []
    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                try:
                    results.append({
                        "category": _safe_strip(
                            row.get("Category") or row.get("Type") or ""
                        ),
                        "inference": _safe_strip(
                            row.get("Inference")
                            or row.get("Description")
                            or row.get("Type Description")
                            or ""
                        ),
                        "description": _safe_strip(
                            row.get("Description") or ""
                        ),
                    })
                except Exception as exc:
                    logger.warning(
                        "Skipping malformed inference row: %s", exc
                    )
    except Exception as exc:
        logger.error("Failed to parse inferences: %s", exc)
    return results


def parse_ad_targeting(path: Path) -> dict[str, list[str]]:
    """Parse Ad_Targeting.csv.

    This file typically has a single row with semicolons inside cells
    representing multiple values. We split each cell on ``;`` to get lists.
    """
    path = Path(path)
    if not path.exists():
        logger.warning("Ad targeting file not found: %s", path)
        return {}

    result: dict[str, list[str]] = {}
    try:
        with open(path, encoding="utf-8-sig", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                for key, value in row.items():
                    if not key:
                        continue
                    clean_key = _normalise_ad_key(key.strip())
                    if value and value.strip():
                        items = [
                            item.strip()
                            for item in value.split(";")
                            if item.strip()
                        ]
                        result[clean_key] = items
                    else:
                        result[clean_key] = []
                # Typically only one row; break after first
                break
    except Exception as exc:
        logger.error("Failed to parse ad targeting: %s", exc)
    return result


def _normalise_ad_key(raw_key: str) -> str:
    """Convert ad-targeting column names to snake_case dict keys.

    Examples:
        "Member Interests" → "interests"
        "Job Titles" → "job_titles"
        "Member Traits" → "member_traits"
        "Skills" → "skills"
    """
    key = raw_key.lower().strip()
    key = key.replace("member ", "")
    key = re.sub(r"[^a-z0-9]+", "_", key).strip("_")
    return key


# ---------------------------------------------------------------------------
# File discovery helpers
# ---------------------------------------------------------------------------

_FILE_MAP: dict[str, list[str]] = {
    "connections": ["Connections.csv", "connections.csv"],
    "messages": ["messages.csv", "Messages.csv"],
    "invitations": [
        "Invitations.csv",
        "invitations.csv",
        "Sent Invitations.csv",
    ],
    "company_follows": [
        "Company Follows.csv",
        "Company_Follows.csv",
        "company_follows.csv",
    ],
    "inferences": [
        "Inferences_about_you.csv",
        "Inferences.csv",
        "inferences.csv",
    ],
    "ad_targeting": [
        "Ad_Targeting.csv",
        "Ad Targeting.csv",
        "ad_targeting.csv",
    ],
}


def _find_file(folder: Path, candidates: list[str]) -> Path | None:
    """Return the first existing file from a list of candidate names."""
    for name in candidates:
        candidate = folder / name
        if candidate.exists():
            return candidate
    return None


# ---------------------------------------------------------------------------
# Master parser
# ---------------------------------------------------------------------------


def parse_all(folder_path: str | Path) -> dict[str, Any]:
    """Parse all known LinkedIn CSV exports from a folder.

    Returns a dict keyed by data type (connections, messages, etc.)
    containing the parsed results from each individual parser.
    """
    folder = Path(folder_path)
    if not folder.is_dir():
        logger.error("Export folder does not exist: %s", folder)
        return {}

    data: dict[str, Any] = {}

    # Connections
    p = _find_file(folder, _FILE_MAP["connections"])
    data["connections"] = parse_connections(p) if p else []

    # Messages
    p = _find_file(folder, _FILE_MAP["messages"])
    data["messages"] = parse_messages(p) if p else []

    # Invitations
    p = _find_file(folder, _FILE_MAP["invitations"])
    data["invitations"] = parse_invitations(p) if p else []

    # Company Follows
    p = _find_file(folder, _FILE_MAP["company_follows"])
    data["company_follows"] = parse_company_follows(p) if p else []

    # Inferences
    p = _find_file(folder, _FILE_MAP["inferences"])
    data["inferences"] = parse_inferences(p) if p else []

    # Ad Targeting
    p = _find_file(folder, _FILE_MAP["ad_targeting"])
    data["ad_targeting"] = parse_ad_targeting(p) if p else {}

    counts = {k: len(v) if isinstance(v, list) else len(v.keys()) for k, v in data.items()}
    logger.info("Parsed LinkedIn export: %s", counts)
    return data


# ---------------------------------------------------------------------------
# JSON serialization helper
# ---------------------------------------------------------------------------


class _DateEncoder(json.JSONEncoder):
    """JSON encoder that serialises datetime objects to ISO format."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse LinkedIn CSV exports into structured JSON."
    )
    parser.add_argument(
        "folder",
        type=Path,
        help="Path to the folder containing LinkedIn CSV exports.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output JSON file path. Defaults to stdout.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging."
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    data = parse_all(args.folder)

    json_str = json.dumps(data, cls=_DateEncoder, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(json_str, encoding="utf-8")
        logger.info("Wrote parsed data to %s", args.output)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
