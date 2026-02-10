#!/usr/bin/env python3
"""
analyze.py - Data analysis modules for LinkedIn export data.

Takes parsed data dicts from parse_export.py and produces structured
analysis results: network clustering, relationship scoring, invitation
trends, message classification, career strata mapping, and aggregate stats.

Uses only Python 3.9+ stdlib.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Role-clustering keyword sets
# ---------------------------------------------------------------------------

FOUNDER_KEYWORDS: list[str] = [
    "founder", "co-founder", "cofounder", "ceo", "chief executive",
    "owner", "principal", "managing partner", "entrepreneur",
]
TECH_KEYWORDS: list[str] = [
    "engineer", "developer", "software", "swe", "devops", "sre",
    "architect", "cto", "tech lead", "data scientist", "ml ", "machine learning",
    "full stack", "fullstack", "frontend", "backend", "platform",
    "infrastructure", "security engineer",
]
SALES_KEYWORDS: list[str] = [
    "sales", "account executive", "business development", "bdr", "sdr",
    "revenue", "partnerships", "ae ", "account manager",
]
MARKETING_KEYWORDS: list[str] = [
    "marketing", "brand", "content", "growth", "demand gen", "cmo",
    "communications", "social media", "digital marketing", "email marketing",
    "lifecycle", "crm", "retention", "acquisition", "performance marketing",
    "product marketing", "pmm",
]
PRODUCT_KEYWORDS: list[str] = [
    "product manager", "product lead", "product director", "vp product",
    "head of product", "cpo", "product design", "ux", "ui/ux",
]
DESIGN_KEYWORDS: list[str] = [
    "designer", "design lead", "creative director", "art director",
    "visual design", "graphic design", "ux design", "ui design",
]
RECRUITING_KEYWORDS: list[str] = [
    "recruiter", "talent", "recruiting", "people ops", "hr ",
    "human resources", "head of people", "vp people",
]
CONSULTING_KEYWORDS: list[str] = [
    "consultant", "advisor", "advisory", "freelance", "independent",
    "strategist", "strategy",
]
EXECUTIVE_KEYWORDS: list[str] = [
    "vp ", "vice president", "svp", "evp", "director", "head of",
    "chief", "c-suite", "coo", "cfo", "cro", "cmo",
]
OPERATIONS_KEYWORDS: list[str] = [
    "operations", "ops ", "supply chain", "logistics", "fulfillment",
    "procurement", "project manager", "program manager",
]

_CLUSTER_DEFINITIONS: list[tuple[str, list[str]]] = [
    ("Founders & CEOs", FOUNDER_KEYWORDS),
    ("Tech & Engineering", TECH_KEYWORDS),
    ("Sales & BD", SALES_KEYWORDS),
    ("Marketing & Growth", MARKETING_KEYWORDS),
    ("Product", PRODUCT_KEYWORDS),
    ("Design & Creative", DESIGN_KEYWORDS),
    ("Recruiting & HR", RECRUITING_KEYWORDS),
    ("Consulting & Strategy", CONSULTING_KEYWORDS),
    ("Executive Leadership", EXECUTIVE_KEYWORDS),
    ("Operations", OPERATIONS_KEYWORDS),
]

# ---------------------------------------------------------------------------
# Company industry classification keywords
# ---------------------------------------------------------------------------

INDUSTRY_KEYWORDS: dict[str, list[str]] = {
    "DTC / E-commerce": [
        "beauty", "skin", "cosmetic", "fashion", "apparel", "clothing",
        "home", "decor", "food", "beverage", "wellness", "supplement",
        "jewelry", "accessories", "lifestyle", "retail", "shop", "store",
        "brand", "direct", "dtc", "d2c", "ecommerce", "e-commerce",
        "consumer", "subscription box",
    ],
    "Martech / SaaS": [
        "klaviyo", "braze", "shopify", "attentive", "yotpo", "gorgias",
        "iterable", "sailthru", "segment", "amplitude", "mixpanel",
        "hubspot", "marketo", "salesforce", "platform", "saas", "software",
        "analytics", "data", "automation", "crm", "martech", "adtech",
    ],
    "Tech": [
        "tech", "technology", "ai ", "artificial intelligence",
        "machine learning", "cloud", "cyber", "fintech", "biotech",
        "healthtech", "edtech", "proptech", "crypto", "blockchain",
        "computing", "digital",
    ],
    "Recruiting / Staffing": [
        "recruiting", "staffing", "talent", "hiring", "recruitment",
        "headhunt", "career", "job", "workforce",
    ],
    "Luxury / Premium": [
        "luxury", "premium", "high-end", "designer", "couture",
        "prestige", "artisan", "bespoke",
    ],
    "Media / Publishing": [
        "media", "publish", "news", "content", "editorial",
        "journalism", "entertainment", "podcast", "video",
    ],
    "Agency / Services": [
        "agency", "consulting", "consultancy", "service", "studio",
        "creative agency", "digital agency", "marketing agency",
    ],
    "Finance / VC": [
        "venture", "capital", "investment", "fund", "finance", "banking",
        "private equity", "pe ", "vc ", "angel",
    ],
}

# ---------------------------------------------------------------------------
# Spam / noise heuristics for message classification
# ---------------------------------------------------------------------------

SPAM_INDICATORS: list[str] = [
    "i noticed your profile",
    "i came across your profile",
    "i saw your profile",
    "limited time",
    "exclusive opportunity",
    "are you open to",
    "we're hiring",
    "we are hiring",
    "job opportunity",
    "perfect fit",
    "reaching out because",
    "thought you'd be interested",
    "hope this finds you well",
    "i'd love to connect",
    "open to exploring",
    "exciting opportunity",
    "top talent",
    "passive candidate",
    "impressive background",
    "quick question",
    "just following up",
    "checking in",
    "i help companies",
    "i help professionals",
    "revenue growth",
    "book a call",
    "schedule a chat",
    "free consultation",
    "free trial",
    "demo",
    "webinar",
    "download our",
    "unsubscribe",
    "opt out",
]


# ---------------------------------------------------------------------------
# 1. cluster_network
# ---------------------------------------------------------------------------


def cluster_network(
    connections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Group connections by position keywords into role clusters.

    Returns a list of cluster dicts, each with:
        - name: cluster label
        - count: number of connections in cluster
        - top_companies: most common companies (up to 10)
        - connections: list of connection dicts in this cluster
    """
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unmatched: list[dict[str, Any]] = []

    for conn in connections:
        position = (conn.get("position") or "").lower()
        matched = False
        for cluster_name, keywords in _CLUSTER_DEFINITIONS:
            if any(kw in position for kw in keywords):
                clusters[cluster_name].append(conn)
                matched = True
                break  # First match wins
        if not matched:
            unmatched.append(conn)

    if unmatched:
        clusters["Other / Unclassified"] = unmatched

    results: list[dict[str, Any]] = []
    for name, conns in sorted(clusters.items(), key=lambda x: -len(x[1])):
        companies = Counter(
            c.get("company", "") for c in conns if c.get("company")
        )
        results.append({
            "name": name,
            "count": len(conns),
            "top_companies": [co for co, _ in companies.most_common(10)],
            "connections": conns,
        })
    return results


# ---------------------------------------------------------------------------
# 2. categorize_companies
# ---------------------------------------------------------------------------


def categorize_companies(
    follows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Classify company follows into industry buckets.

    Returns list of category dicts with name, count, companies list.
    """
    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unmatched: list[dict[str, Any]] = []

    for follow in follows:
        company = (follow.get("company") or "").lower()
        matched = False
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            if any(kw in company for kw in keywords):
                buckets[industry].append(follow)
                matched = True
                break
        if not matched:
            unmatched.append(follow)

    if unmatched:
        buckets["Other"] = unmatched

    results: list[dict[str, Any]] = []
    for name, items in sorted(buckets.items(), key=lambda x: -len(x[1])):
        results.append({
            "name": name,
            "count": len(items),
            "companies": [item.get("company", "") for item in items],
        })
    return results


# ---------------------------------------------------------------------------
# 3. score_messages (relationship tiers)
# ---------------------------------------------------------------------------

_TIER_THRESHOLDS: list[tuple[str, int]] = [
    ("Active", 30),
    ("Some Contact", 90),
    ("Going Stale", 180),
    ("Dormant", 365),
    # Anything beyond 365 → Deep Sleep
]


def score_messages(
    connections: list[dict[str, Any]],
    messages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Cross-reference connections with messages to assign relationship tiers.

    Tiers:
        - Active: messaged in last 30 days
        - Some Contact: messaged in last 90 days
        - Going Stale: messaged in last 180 days
        - Dormant: messaged in last 365 days
        - Deep Sleep: last message over 1 year ago
        - Never Messaged: no messages found

    Returns enriched connection dicts with ``tier`` and ``last_message_date``.
    """
    now = datetime.now()

    # Build a lookup: lowercase full name → most recent message date
    name_to_last_msg: dict[str, datetime] = {}
    for msg in messages:
        sender = (msg.get("sender") or "").strip().lower()
        msg_date = msg.get("date")
        if not sender or not msg_date:
            continue
        if isinstance(msg_date, str):
            # Attempt re-parse if still a string
            from parse_export import parse_date
            msg_date = parse_date(msg_date)
        if msg_date and (
            sender not in name_to_last_msg
            or msg_date > name_to_last_msg[sender]
        ):
            name_to_last_msg[sender] = msg_date

    enriched: list[dict[str, Any]] = []
    for conn in connections:
        full_name = (
            f"{conn.get('first_name', '')} {conn.get('last_name', '')}"
        ).strip().lower()

        last_msg = name_to_last_msg.get(full_name)
        tier = "Never Messaged"

        if last_msg:
            days_ago = (now - last_msg).days
            tier = "Deep Sleep"  # default for > 365
            for tier_name, threshold in _TIER_THRESHOLDS:
                if days_ago <= threshold:
                    tier = tier_name
                    break

        enriched.append({
            **conn,
            "tier": tier,
            "last_message_date": last_msg,
        })
    return enriched


# ---------------------------------------------------------------------------
# 4. analyze_invitations
# ---------------------------------------------------------------------------


def analyze_invitations(
    invitations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Compute inbound vs outbound invitations by month.

    Returns a list of monthly breakdown dicts sorted chronologically:
        [{"month": "2024-01", "inbound": 12, "outbound": 5}, ...]
    """
    monthly: dict[str, dict[str, int]] = defaultdict(
        lambda: {"inbound": 0, "outbound": 0}
    )

    for inv in invitations:
        dt = inv.get("date")
        if not dt:
            continue
        if isinstance(dt, str):
            from parse_export import parse_date
            dt = parse_date(dt)
        if not dt:
            continue
        month_key = dt.strftime("%Y-%m")
        direction = inv.get("direction", "outbound")
        if direction in ("inbound", "outbound"):
            monthly[month_key][direction] += 1

    results: list[dict[str, Any]] = []
    for month_key in sorted(monthly.keys()):
        results.append({
            "month": month_key,
            "inbound": monthly[month_key]["inbound"],
            "outbound": monthly[month_key]["outbound"],
        })
    return results


# ---------------------------------------------------------------------------
# 5. classify_inbox
# ---------------------------------------------------------------------------


def _is_spam(content: str) -> bool:
    """Heuristic spam detection based on keyword indicators."""
    lower = content.lower()
    matches = sum(1 for ind in SPAM_INDICATORS if ind in lower)
    # If 2+ spam indicators or very short generic message, classify as noise
    return matches >= 2 or (matches >= 1 and len(content) < 100)


def classify_inbox(
    messages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Classify messages as genuine vs noise by half-year period.

    Returns period breakdown:
        [{"period": "2024-H1", "genuine": 45, "noise": 120, "total": 165}, ...]
    """
    periods: dict[str, dict[str, int]] = defaultdict(
        lambda: {"genuine": 0, "noise": 0}
    )

    for msg in messages:
        dt = msg.get("date")
        if not dt:
            continue
        if isinstance(dt, str):
            from parse_export import parse_date
            dt = parse_date(dt)
        if not dt:
            continue
        half = "H1" if dt.month <= 6 else "H2"
        period_key = f"{dt.year}-{half}"
        content = msg.get("content") or msg.get("subject") or ""
        if _is_spam(content):
            periods[period_key]["noise"] += 1
        else:
            periods[period_key]["genuine"] += 1

    results: list[dict[str, Any]] = []
    for period_key in sorted(periods.keys()):
        data = periods[period_key]
        results.append({
            "period": period_key,
            "genuine": data["genuine"],
            "noise": data["noise"],
            "total": data["genuine"] + data["noise"],
        })
    return results


# ---------------------------------------------------------------------------
# 6. build_career_strata
# ---------------------------------------------------------------------------

# Default career phases if no positions are provided
_DEFAULT_PHASES: list[dict[str, Any]] = [
    {"label": "Early Career", "start_year": 2010, "end_year": 2014},
    {"label": "Growth Phase", "start_year": 2015, "end_year": 2018},
    {"label": "Senior Phase", "start_year": 2019, "end_year": 2022},
    {"label": "Current Phase", "start_year": 2023, "end_year": 2030},
]


def build_career_strata(
    connections: list[dict[str, Any]],
    positions: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Group connections by connected-on date, mapped to career phases.

    If ``positions`` is provided, derive phase boundaries from position
    start dates. Otherwise, fall back to default 4-year phase buckets.

    Returns list of strata dicts:
        [{"label": "Phase Name", "start_year": 2019, "end_year": 2022,
          "count": 45, "top_companies": [...], "top_roles": [...]}, ...]
    """
    phases = _DEFAULT_PHASES
    if positions:
        # Build phases from position history
        sorted_pos = sorted(
            [p for p in positions if p.get("start_date")],
            key=lambda p: p["start_date"],
        )
        if sorted_pos:
            phases = []
            for i, pos in enumerate(sorted_pos):
                start_dt = pos["start_date"]
                if isinstance(start_dt, str):
                    from parse_export import parse_date
                    start_dt = parse_date(start_dt)
                if not start_dt:
                    continue
                end_year = (
                    sorted_pos[i + 1]["start_date"].year - 1
                    if i + 1 < len(sorted_pos) and sorted_pos[i + 1].get("start_date")
                    else 2030
                )
                phases.append({
                    "label": pos.get("title", f"Phase {i+1}"),
                    "start_year": start_dt.year,
                    "end_year": end_year,
                })

    # Bucket connections into phases
    strata: list[dict[str, Any]] = []
    for phase in phases:
        bucket: list[dict[str, Any]] = []
        for conn in connections:
            dt = conn.get("connected_on")
            if not dt:
                continue
            if isinstance(dt, str):
                from parse_export import parse_date
                dt = parse_date(dt)
            if not dt:
                continue
            if phase["start_year"] <= dt.year <= phase["end_year"]:
                bucket.append(conn)

        companies = Counter(
            c.get("company", "") for c in bucket if c.get("company")
        )
        roles = Counter(
            c.get("position", "") for c in bucket if c.get("position")
        )
        strata.append({
            "label": phase["label"],
            "start_year": phase["start_year"],
            "end_year": phase["end_year"],
            "count": len(bucket),
            "top_companies": [co for co, _ in companies.most_common(10)],
            "top_roles": [r for r, _ in roles.most_common(10)],
        })
    return strata


# ---------------------------------------------------------------------------
# 7. identify_high_value_messages
# ---------------------------------------------------------------------------


def identify_high_value_messages(
    messages: list[dict[str, Any]],
    connections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Find unanswered messages ranked by potential value.

    Scoring heuristics:
        - Sender is in connections: +2
        - Sender has a "senior" position: +3
        - Message contains actionable language: +2
        - Message is not spam: +2
        - Recency bonus (within 90 days): +1

    Returns scored message list, sorted descending by score.
    """
    # Build connection lookup
    conn_lookup: dict[str, dict[str, Any]] = {}
    for c in connections:
        name = f"{c.get('first_name', '')} {c.get('last_name', '')}".strip().lower()
        if name:
            conn_lookup[name] = c

    # Group messages by conversation to find unanswered ones
    # An "unanswered" message is the last message in a conversation not sent by the user
    conversations: dict[str | None, list[dict[str, Any]]] = defaultdict(list)
    for msg in messages:
        conversations[msg.get("conversation_id")].append(msg)

    now = datetime.now()
    actionable_keywords = [
        "meet", "coffee", "call", "chat", "discuss", "collaborate",
        "advice", "introduce", "referral", "recommend", "opportunity",
        "project", "role", "position", "offer", "proposal",
    ]
    senior_keywords = [
        "vp", "vice president", "director", "head of", "chief",
        "founder", "ceo", "cto", "cmo", "coo", "partner", "principal",
        "svp", "evp",
    ]

    scored: list[dict[str, Any]] = []

    for conv_id, conv_msgs in conversations.items():
        # Sort by date
        dated = [m for m in conv_msgs if m.get("date")]
        if not dated:
            continue
        dated.sort(
            key=lambda m: m["date"] if isinstance(m["date"], datetime) else datetime.min
        )
        last_msg = dated[-1]
        content = (last_msg.get("content") or "").lower()
        sender = (last_msg.get("sender") or "").lower()

        score = 0

        # Connection bonus
        conn = conn_lookup.get(sender)
        if conn:
            score += 2
            position = (conn.get("position") or "").lower()
            if any(kw in position for kw in senior_keywords):
                score += 3

        # Not spam
        if not _is_spam(content):
            score += 2
        else:
            score -= 3  # Penalise spam heavily

        # Actionable language
        if any(kw in content for kw in actionable_keywords):
            score += 2

        # Recency
        msg_date = last_msg.get("date")
        if isinstance(msg_date, datetime) and (now - msg_date).days <= 90:
            score += 1

        scored.append({
            **last_msg,
            "score": score,
            "is_connection": conn is not None,
            "sender_position": conn.get("position", "") if conn else "",
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


# ---------------------------------------------------------------------------
# 8. generate_summary_stats
# ---------------------------------------------------------------------------


def generate_summary_stats(all_data: dict[str, Any]) -> dict[str, Any]:
    """Compute aggregate stats for the hero / summary section.

    Returns a flat dict of key metrics.
    """
    connections = all_data.get("connections", [])
    messages = all_data.get("messages", [])
    invitations = all_data.get("invitations", [])
    follows = all_data.get("company_follows", [])
    inferences = all_data.get("inferences", [])
    ad_targeting = all_data.get("ad_targeting", {})

    # Connection date range
    connected_dates = [
        c["connected_on"]
        for c in connections
        if c.get("connected_on") and isinstance(c["connected_on"], datetime)
    ]
    earliest = min(connected_dates) if connected_dates else None
    latest = max(connected_dates) if connected_dates else None

    # Unique companies
    unique_companies = set(
        c.get("company", "").strip()
        for c in connections
        if c.get("company", "").strip()
    )

    # Message stats
    unique_conversations = set(
        m.get("conversation_id")
        for m in messages
        if m.get("conversation_id")
    )
    orphan_messages = sum(
        1 for m in messages if not m.get("conversation_id")
    )

    # Invitations
    inbound_invites = sum(
        1 for i in invitations if i.get("direction") == "inbound"
    )
    outbound_invites = sum(
        1 for i in invitations if i.get("direction") == "outbound"
    )

    # Ad targeting counts
    ad_interests = len(ad_targeting.get("interests", []))
    ad_skills = len(ad_targeting.get("skills", []))

    return {
        "total_connections": len(connections),
        "total_messages": len(messages),
        "total_conversations": len(unique_conversations),
        "orphan_messages": orphan_messages,
        "total_invitations": len(invitations),
        "inbound_invitations": inbound_invites,
        "outbound_invitations": outbound_invites,
        "total_company_follows": len(follows),
        "total_inferences": len(inferences),
        "unique_companies": len(unique_companies),
        "ad_interests": ad_interests,
        "ad_skills": ad_skills,
        "earliest_connection": earliest.isoformat() if earliest else None,
        "latest_connection": latest.isoformat() if latest else None,
        "network_span_years": (
            round((latest - earliest).days / 365.25, 1)
            if earliest and latest
            else None
        ),
    }


# ---------------------------------------------------------------------------
# Master analysis
# ---------------------------------------------------------------------------


def analyze_all(parsed_data: dict[str, Any]) -> dict[str, Any]:
    """Run all analysis modules on parsed LinkedIn data.

    Returns a dict containing results from every analysis function.
    """
    connections = parsed_data.get("connections", [])
    messages = parsed_data.get("messages", [])
    invitations = parsed_data.get("invitations", [])
    follows = parsed_data.get("company_follows", [])

    results: dict[str, Any] = {
        "summary_stats": generate_summary_stats(parsed_data),
        "network_clusters": cluster_network(connections),
        "company_categories": categorize_companies(follows),
        "relationship_tiers": _summarise_tiers(
            score_messages(connections, messages)
        ),
        "invitation_trends": analyze_invitations(invitations),
        "inbox_classification": classify_inbox(messages),
        "career_strata": build_career_strata(connections),
        "high_value_messages": identify_high_value_messages(
            messages, connections
        )[:25],  # Top 25 only
    }
    return results


def _summarise_tiers(
    enriched: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarise tier distribution from enriched connections."""
    tier_counts: dict[str, int] = Counter(
        c.get("tier", "Unknown") for c in enriched
    )
    return {
        "distribution": dict(
            sorted(tier_counts.items(), key=lambda x: -x[1])
        ),
        "total": len(enriched),
        "connections": enriched,
    }


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
        description="Analyze parsed LinkedIn export data."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to parsed JSON file (output of parse_export.py).",
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

    raw = args.input.read_text(encoding="utf-8")
    parsed_data = json.loads(raw)

    # Re-parse date strings back to datetime objects
    _rehydrate_dates(parsed_data)

    results = analyze_all(parsed_data)

    json_str = json.dumps(results, cls=_DateEncoder, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(json_str, encoding="utf-8")
        logger.info("Wrote analysis to %s", args.output)
    else:
        print(json_str)


def _rehydrate_dates(data: dict[str, Any]) -> None:
    """Convert ISO date strings back to datetime objects in-place."""
    date_fields = {"connected_on", "followed_on", "date", "last_message_date"}
    for key, value in data.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for field in date_fields:
                        if field in item and isinstance(item[field], str):
                            try:
                                item[field] = datetime.fromisoformat(
                                    item[field]
                                )
                            except (ValueError, TypeError):
                                pass


if __name__ == "__main__":
    main()
