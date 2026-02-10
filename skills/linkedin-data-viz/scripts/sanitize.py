#!/usr/bin/env python3
"""
sanitize.py - Data anonymization for publishing LinkedIn visualizations.

Replaces real names, companies, and message content with plausible fakes
while preserving all metrics, dates, cluster sizes, and structural
patterns. Uses Faker if available, falls back to built-in name/company
lists.

Uses only Python 3.9+ stdlib for core functionality.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import logging
import random
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Try to import Faker, fall back gracefully
# ---------------------------------------------------------------------------

try:
    from faker import Faker

    _faker = Faker()
    _HAS_FAKER = True
    logger.debug("Faker available, using it for name generation.")
except ImportError:
    _HAS_FAKER = False
    logger.debug("Faker not installed, using built-in name lists.")

# ---------------------------------------------------------------------------
# Built-in fallback name and company lists
# ---------------------------------------------------------------------------

FAKE_FIRST_NAMES_F: list[str] = [
    "Aria", "Nova", "Luna", "Sage", "Iris", "Wren", "Lyra",
    "Cleo", "Maren", "Thea", "Daphne", "Selene", "Freya", "Zara",
    "Nadia", "Vera", "Camille", "Elara", "Rowan", "Sable",
    "Astrid", "Briar", "Celeste", "Dahlia", "Esme", "Flora",
    "Gemma", "Haven", "Ivy", "Jade", "Kaia", "Lila", "Mila",
    "Nora", "Opal", "Petra", "Quinn", "Ren", "Stella", "Tessa",
    "Uma", "Viola", "Winter", "Xena", "Yara", "Zola",
]

FAKE_FIRST_NAMES_M: list[str] = [
    "Kai", "Leo", "Atlas", "Orion", "Felix", "Jasper", "Ezra",
    "Milo", "Silas", "Ronan", "Axel", "Dante", "Ellis", "Forrest",
    "Griffin", "Hugo", "Ivan", "Jude", "Knox", "Leander",
    "Magnus", "Nash", "Oscar", "Pax", "Remy", "Sterling", "Tobias",
    "Viggo", "Wells", "Xander", "York", "Zane", "Arlo", "Beck",
    "Cade", "Drake", "Emmett", "Flynn", "Grant", "Heath",
    "Idris", "Jett", "Kieran", "Lachlan", "Marco", "Nico",
]

FAKE_LAST_NAMES: list[str] = [
    "Ashford", "Blackwell", "Calloway", "Devereaux", "Eastwood",
    "Fairchild", "Gallagher", "Hartwell", "Irvine", "Jameson",
    "Keating", "Lancaster", "Mercer", "Northwood", "Oconnell",
    "Prescott", "Quinlan", "Redmond", "Sinclair", "Thorne",
    "Underwood", "Voss", "Whitfield", "Ximenez", "Yardley", "Zhao",
    "Aldridge", "Brennan", "Carver", "Drake", "Everett", "Frost",
    "Gray", "Holmes", "Ingram", "Jensen", "Klein", "Lockwood",
    "Monroe", "Nolan", "Palmer", "Reed", "Stone", "Turner",
    "Vaughn", "Walsh",
]

FAKE_COMPANIES: dict[str, list[str]] = {
    "dtc": [
        "Lumina Beauty", "Woven Home", "Cedarstone Goods",
        "Velvet & Vine", "Solstice Skincare", "Harbor + Thread",
        "Crestline Organics", "Wildbloom Botanicals", "Dusk & Co",
        "Ember & Oak", "Radiant Earth", "Moonstone Provisions",
        "Petal & Post", "Sunridge Essentials", "Verdant Living",
    ],
    "tech": [
        "NexaFlow", "Prism Labs", "Vertex Systems", "Arcane Data",
        "Helix Cloud", "Quantum Leap AI", "Cobalt Logic",
        "Meridian Software", "Stratos Computing", "Vanguard Tech",
        "Zephyr Dynamics", "Pinnacle Digital", "Forge Analytics",
        "Skyward Platforms", "Atlas Intelligence",
    ],
    "martech": [
        "SignalStack", "Engagify", "RetainIQ", "FlowMetrics",
        "Pulse Analytics", "Beacon CRM", "Orbit Engage",
        "TriggerPath", "Audience Labs", "Segment Pro",
        "Lifecycle AI", "Conversion Cloud", "Reach Engine",
        "Attribution Works", "DataBridge",
    ],
    "agency": [
        "Kindling Creative", "Northstar Agency", "Bright Path Media",
        "Summit Strategy", "Redline Digital", "Clear Signal Group",
        "Horizon Partners", "Catalyst Collective", "Spark & Frame",
        "Mosaic Agency", "Craft & Commerce", "Blueprint Studio",
    ],
    "recruiting": [
        "TalentForge", "Apex Recruiting", "Keystone Search",
        "Bridgepoint Talent", "Summit Staffing", "Compass Careers",
        "Elevate Recruiting", "Pathfinder HR", "PeakSearch",
        "Catalyst Talent Group",
    ],
    "finance": [
        "Ironwood Capital", "Bluewater Ventures", "Crestview Partners",
        "Granite Equity", "Lighthouse Fund", "Sequoia Ridge VC",
        "Sterling Growth", "Timberline Investments", "Apex Fund",
        "Foundry Capital",
    ],
    "luxury": [
        "Maison Lumiere", "Ateliers du Monde", "Prestige Collective",
        "Noir & Blanc", "Gilded Path", "Opulent & Co",
    ],
    "media": [
        "Chronicle Media", "Narrative Labs", "Wavelength Publishing",
        "Aperture Content", "Storyforge", "Current Media Group",
    ],
    "other": [
        "Greenfield Corp", "Ridgeline Industries", "Cornerstone Group",
        "Ironside Partners", "Bridgewater Associates", "Clearview Global",
        "Aspen Holdings", "Pinnacle Group", "Summit Enterprises",
        "Vantage Works", "Nexus Corp", "Horizon Global",
    ],
}

# ---------------------------------------------------------------------------
# Fake email domains
# ---------------------------------------------------------------------------

FAKE_DOMAINS: list[str] = [
    "protonmail.com", "fastmail.com", "tutanota.com", "hey.com",
    "outlook.com", "icloud.com", "pm.me",
]

# ---------------------------------------------------------------------------
# Fake message templates
# ---------------------------------------------------------------------------

FAKE_MESSAGES_GENUINE: list[str] = [
    "Great to connect! Would love to chat about your work in the space.",
    "Thanks for reaching out. Happy to discuss further next week.",
    "Really enjoyed your recent post. Let me know if you want to collaborate.",
    "Following up on our conversation at the conference last month.",
    "Appreciate the introduction. Looking forward to connecting.",
    "Would you be open to a quick call? I think there could be some synergy.",
    "Thanks for the recommendation! Excited about the opportunity.",
    "Just saw your company announcement. Congratulations on the milestone!",
    "Been meaning to reach out. Your perspective on this would be valuable.",
    "Let me know when you have time for that coffee chat.",
]

FAKE_MESSAGES_NOISE: list[str] = [
    "I noticed your profile and thought you might be interested in...",
    "We're hiring for a role that seems like a perfect fit for you.",
    "I'd love to connect and share an exciting opportunity.",
    "Hope this finds you well. I came across your profile and...",
    "Limited time offer: exclusive access to our platform.",
    "Are you open to exploring new opportunities?",
    "I help professionals like you achieve their career goals.",
    "Quick question: are you satisfied with your current CRM?",
    "Book a free consultation to learn how we can help.",
    "Just following up on my previous message about the opportunity.",
]

# ---------------------------------------------------------------------------
# Gender heuristic (very simplified, for name mapping only)
# ---------------------------------------------------------------------------

# Common feminine name endings for a rough heuristic
_FEMININE_ENDINGS = ("a", "e", "i", "y", "ah", "ie", "na", "la", "ne")


def _guess_gender(first_name: str) -> str:
    """Very rough heuristic to guess M/F for name mapping.

    This is used solely to preserve approximate gender distribution
    when replacing names. Not intended for any other purpose.
    """
    if not first_name:
        return random.choice(["M", "F"])
    name_lower = first_name.strip().lower()
    if any(name_lower.endswith(end) for end in _FEMININE_ENDINGS):
        return "F"
    return "M"


# ---------------------------------------------------------------------------
# Name mapping
# ---------------------------------------------------------------------------


def _get_fake_first_name(gender: str) -> str:
    """Get a fake first name, using Faker if available."""
    if _HAS_FAKER:
        return _faker.first_name_female() if gender == "F" else _faker.first_name_male()
    pool = FAKE_FIRST_NAMES_F if gender == "F" else FAKE_FIRST_NAMES_M
    return random.choice(pool)


def _get_fake_last_name() -> str:
    """Get a fake last name, using Faker if available."""
    if _HAS_FAKER:
        return _faker.last_name()
    return random.choice(FAKE_LAST_NAMES)


def build_name_map(
    connections: list[dict[str, Any]],
) -> dict[str, dict[str, str]]:
    """Create a 1:1 real-to-fake name mapping preserving gender distribution.

    Args:
        connections: List of connection dicts with first_name, last_name.

    Returns:
        Dict mapping ``"FirstName LastName"`` to
        ``{"first_name": "FakeFN", "last_name": "FakeLN", "full": "FakeFN FakeLN"}``.
    """
    # Seed for reproducibility within a session
    rng = random.Random(42)

    name_map: dict[str, dict[str, str]] = {}
    used_names: set[str] = set()

    # Shuffle the fallback pools to avoid repetition
    f_pool = list(FAKE_FIRST_NAMES_F)
    m_pool = list(FAKE_FIRST_NAMES_M)
    l_pool = list(FAKE_LAST_NAMES)
    rng.shuffle(f_pool)
    rng.shuffle(m_pool)
    rng.shuffle(l_pool)

    f_idx, m_idx, l_idx = 0, 0, 0

    for conn in connections:
        first = (conn.get("first_name") or "").strip()
        last = (conn.get("last_name") or "").strip()
        real_full = f"{first} {last}".strip()

        if not real_full or real_full in name_map:
            continue

        gender = _guess_gender(first)

        # Generate unique fake name
        for _ in range(50):  # safety limit
            if _HAS_FAKER:
                fake_first = _get_fake_first_name(gender)
                fake_last = _get_fake_last_name()
            else:
                if gender == "F":
                    fake_first = f_pool[f_idx % len(f_pool)]
                    f_idx += 1
                else:
                    fake_first = m_pool[m_idx % len(m_pool)]
                    m_idx += 1
                fake_last = l_pool[l_idx % len(l_pool)]
                l_idx += 1

            fake_full = f"{fake_first} {fake_last}"
            if fake_full not in used_names:
                used_names.add(fake_full)
                name_map[real_full] = {
                    "first_name": fake_first,
                    "last_name": fake_last,
                    "full": fake_full,
                }
                break

    logger.info("Built name map for %d unique names.", len(name_map))
    return name_map


# ---------------------------------------------------------------------------
# Company sanitization
# ---------------------------------------------------------------------------

# Industry keyword matching (same as analyze.py for consistency)
_COMPANY_INDUSTRY_KEYWORDS: dict[str, list[str]] = {
    "dtc": [
        "beauty", "skin", "cosmetic", "fashion", "apparel", "clothing",
        "home", "food", "beverage", "wellness", "jewelry", "lifestyle",
        "retail", "brand", "dtc", "d2c", "ecommerce",
    ],
    "tech": [
        "tech", "technology", "ai", "cloud", "cyber", "fintech",
        "computing", "digital", "software", "platform",
    ],
    "martech": [
        "klaviyo", "braze", "shopify", "attentive", "yotpo",
        "analytics", "data", "automation", "crm", "martech", "saas",
    ],
    "agency": [
        "agency", "consulting", "service", "studio", "creative",
    ],
    "recruiting": [
        "recruiting", "staffing", "talent", "hiring", "workforce",
    ],
    "finance": [
        "venture", "capital", "investment", "fund", "finance",
    ],
    "luxury": ["luxury", "premium", "prestige", "designer"],
    "media": ["media", "publish", "news", "content", "entertainment"],
}


def _classify_company(name: str) -> str:
    """Classify a company name into an industry bucket."""
    lower = name.lower()
    for industry, keywords in _COMPANY_INDUSTRY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return industry
    return "other"


def sanitize_companies(
    data: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str]]:
    """Replace real company names with tier-matched fake companies.

    Args:
        data: Full parsed data dict (modified in-place on a deep copy).

    Returns:
        Tuple of (sanitized data, company_map dict).
    """
    data = copy.deepcopy(data)

    # Collect all real company names
    all_companies: set[str] = set()
    for conn in data.get("connections", []):
        if conn.get("company"):
            all_companies.add(conn["company"].strip())
    for follow in data.get("company_follows", []):
        if follow.get("company"):
            all_companies.add(follow["company"].strip())

    # Build company map
    company_map: dict[str, str] = {}
    used_fakes: set[str] = set()
    industry_indices: dict[str, int] = {}

    for real_name in sorted(all_companies):
        industry = _classify_company(real_name)
        pool = FAKE_COMPANIES.get(industry, FAKE_COMPANIES["other"])
        idx = industry_indices.get(industry, 0)

        # Find unused fake name
        fake_name = None
        for offset in range(len(pool)):
            candidate = pool[(idx + offset) % len(pool)]
            if candidate not in used_fakes:
                fake_name = candidate
                industry_indices[industry] = (idx + offset + 1) % len(pool)
                break

        if fake_name is None:
            # Exhausted pool; generate a variant
            base = pool[idx % len(pool)]
            fake_name = f"{base} ({len(used_fakes)})"
            industry_indices[industry] = idx + 1

        used_fakes.add(fake_name)
        company_map[real_name] = fake_name

    # Apply to connections
    for conn in data.get("connections", []):
        if conn.get("company"):
            conn["company"] = company_map.get(
                conn["company"].strip(), conn["company"]
            )

    # Apply to company follows
    for follow in data.get("company_follows", []):
        if follow.get("company"):
            follow["company"] = company_map.get(
                follow["company"].strip(), follow["company"]
            )

    logger.info("Sanitized %d company names.", len(company_map))
    return data, company_map


# ---------------------------------------------------------------------------
# Message sanitization
# ---------------------------------------------------------------------------


def sanitize_messages(
    messages: list[dict[str, Any]],
    name_map: dict[str, dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    """Replace message content with category-appropriate templates.

    Preserves message structure (dates, conversation IDs) but replaces
    sender names and content with fake equivalents.

    Args:
        messages: List of message dicts.
        name_map: Optional name mapping for sender replacement.

    Returns:
        Sanitized message list.
    """
    messages = copy.deepcopy(messages)
    rng = random.Random(99)

    for msg in messages:
        # Replace sender
        if name_map and msg.get("sender"):
            sender = msg["sender"].strip()
            if sender in name_map:
                msg["sender"] = name_map[sender]["full"]
            else:
                # Hash-based consistent replacement
                msg["sender"] = _hash_to_name(sender)

        # Replace content with template
        content = (msg.get("content") or "").lower()
        from analyze import _is_spam
        if _is_spam(content):
            msg["content"] = rng.choice(FAKE_MESSAGES_NOISE)
        else:
            msg["content"] = rng.choice(FAKE_MESSAGES_GENUINE)

        # Replace subject
        if msg.get("subject"):
            msg["subject"] = "Re: Connection"

    return messages


def _hash_to_name(real_name: str) -> str:
    """Deterministically map a name to a fake name via hashing."""
    h = int(hashlib.md5(real_name.encode()).hexdigest(), 16)
    first_pool = FAKE_FIRST_NAMES_F + FAKE_FIRST_NAMES_M
    first = first_pool[h % len(first_pool)]
    last = FAKE_LAST_NAMES[(h >> 8) % len(FAKE_LAST_NAMES)]
    return f"{first} {last}"


# ---------------------------------------------------------------------------
# Full sanitization pipeline
# ---------------------------------------------------------------------------


def sanitize_all(
    parsed_data: dict[str, Any],
) -> dict[str, Any]:
    """Full sanitization pipeline.

    Preserves all metrics, dates, cluster sizes, and structural patterns
    while replacing identifying information.

    Args:
        parsed_data: Full parsed LinkedIn data dict.

    Returns:
        Fully sanitized copy of the data.
    """
    data = copy.deepcopy(parsed_data)

    # 1. Build name map from connections
    name_map = build_name_map(data.get("connections", []))

    # 2. Sanitize connection names
    for conn in data.get("connections", []):
        real_full = (
            f"{conn.get('first_name', '')} {conn.get('last_name', '')}"
        ).strip()
        if real_full in name_map:
            fake = name_map[real_full]
            conn["first_name"] = fake["first_name"]
            conn["last_name"] = fake["last_name"]

        # Sanitize email
        if conn.get("email_address"):
            fake_first = conn["first_name"].lower()
            fake_last = conn["last_name"].lower()
            domain = random.choice(FAKE_DOMAINS)
            conn["email_address"] = f"{fake_first}.{fake_last}@{domain}"

    # 3. Sanitize companies
    data, company_map = sanitize_companies(data)

    # 4. Sanitize messages
    data["messages"] = sanitize_messages(
        data.get("messages", []), name_map
    )

    # 5. Sanitize invitations
    for inv in data.get("invitations", []):
        if inv.get("from_name") and inv["from_name"] in name_map:
            inv["from_name"] = name_map[inv["from_name"]]["full"]
        elif inv.get("from_name"):
            inv["from_name"] = _hash_to_name(inv["from_name"])

        if inv.get("to_name") and inv["to_name"] in name_map:
            inv["to_name"] = name_map[inv["to_name"]]["full"]
        elif inv.get("to_name"):
            inv["to_name"] = _hash_to_name(inv["to_name"])

        if inv.get("message"):
            inv["message"] = random.choice(FAKE_MESSAGES_GENUINE)

    # 6. Sanitize ad targeting (keep structure, generalise values)
    # Ad targeting categories are already generic enough; leave as-is

    # 7. Sanitize inferences (keep structure)
    # Inferences are LinkedIn's own categories; no PII

    logger.info(
        "Sanitization complete. %d names mapped, %d companies mapped.",
        len(name_map),
        len(company_map),
    )

    return data


# ---------------------------------------------------------------------------
# Demo generation
# ---------------------------------------------------------------------------


def generate_sanitized_demo(
    sanitized_data: dict[str, Any],
    template_dir: Path,
    output_path: Path,
    theme_css_path: Path | None = None,
) -> Path | None:
    """Generate a demo HTML file with embedded fake data.

    Uses generate_viz to produce a dashboard from sanitized data.

    Args:
        sanitized_data: Fully sanitized data dict.
        template_dir: Directory containing HTML templates.
        output_path: Output directory for the demo.
        theme_css_path: Optional CSS theme file.

    Returns:
        Path to generated demo dashboard, or None on failure.
    """
    from generate_viz import generate_all as gen_all
    from analyze import analyze_all

    try:
        # Run analysis on sanitized data
        analysis = analyze_all(sanitized_data)

        # Generate HTML
        results = gen_all(template_dir, analysis, output_path, theme_css_path)
        dashboard = results.get("dashboard")
        if dashboard:
            logger.info("Generated sanitized demo at %s", dashboard)
        return dashboard
    except Exception as exc:
        logger.error("Failed to generate sanitized demo: %s", exc)
        return None


# ---------------------------------------------------------------------------
# JSON serialization helper
# ---------------------------------------------------------------------------


class _DateEncoder(json.JSONEncoder):
    """JSON encoder that serialises datetime objects to ISO format."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sanitize LinkedIn data for safe publishing."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help=(
            "Path to parsed JSON file (output of parse_export.py) "
            "or folder of CSV exports."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output directory for sanitized data and demo HTML.",
    )
    parser.add_argument(
        "--templates",
        type=Path,
        default=None,
        help="Path to HTML template directory (for demo generation).",
    )
    parser.add_argument(
        "--theme",
        type=Path,
        default=None,
        help="Path to CSS theme file.",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output sanitized JSON only (skip HTML demo generation).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible sanitization (default: 42).",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging."
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    random.seed(args.seed)

    # Load input data
    input_path = Path(args.input)
    if input_path.is_dir():
        # Treat as CSV export folder
        from parse_export import parse_all
        parsed_data = parse_all(input_path)
    elif input_path.suffix == ".json":
        raw = input_path.read_text(encoding="utf-8")
        parsed_data = json.loads(raw)
    else:
        logger.error(
            "Input must be a JSON file or a directory of CSV exports."
        )
        sys.exit(1)

    # Sanitize
    sanitized = sanitize_all(parsed_data)

    # Write sanitized JSON
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "sanitized-data.json"
    json_str = json.dumps(
        sanitized, cls=_DateEncoder, indent=2, ensure_ascii=False
    )
    json_path.write_text(json_str, encoding="utf-8")
    logger.info("Wrote sanitized data to %s", json_path)
    print(f"Sanitized JSON: {json_path}")

    # Generate demo HTML if templates provided
    if not args.json_only and args.templates:
        demo_path = generate_sanitized_demo(
            sanitized, args.templates, output_dir / "demo", args.theme
        )
        if demo_path:
            print(f"Demo dashboard: {demo_path}")
    elif not args.json_only and not args.templates:
        logger.info(
            "Skipping HTML demo (no --templates provided). "
            "Use --json-only to suppress this message."
        )


if __name__ == "__main__":
    main()
