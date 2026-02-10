#!/usr/bin/env python3
"""
generate_viz.py - Template-to-output HTML generator for LinkedIn data visualizations.

Reads HTML templates, injects JSON data and theme CSS, and generates
individual visualization pages plus a unified dashboard. Templates use
``{{DATA}}`` and ``{{THEME_CSS}}`` placeholders.

Uses only Python 3.9+ stdlib.
"""
from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Template definitions
# ---------------------------------------------------------------------------

# Maps output filename → template filename for the 9 individual viz pages
INDIVIDUAL_TEMPLATES: dict[str, str] = {
    "network-clusters.html": "network-clusters.html",
    "company-categories.html": "company-categories.html",
    "relationship-tiers.html": "relationship-tiers.html",
    "invitation-trends.html": "invitation-trends.html",
    "inbox-classification.html": "inbox-classification.html",
    "career-strata.html": "career-strata.html",
    "high-value-messages.html": "high-value-messages.html",
    "ad-targeting.html": "ad-targeting.html",
    "summary-stats.html": "summary-stats.html",
}

DASHBOARD_TEMPLATE: str = "dashboard.html"


# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def load_template(template_path: Path) -> str:
    """Read an HTML template file and return its contents as a string.

    Args:
        template_path: Path to the HTML template file.

    Returns:
        Template HTML as a string.

    Raises:
        FileNotFoundError: If the template file does not exist.
    """
    template_path = Path(template_path)
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def inject_data(
    template_html: str,
    data_dict: dict[str, Any],
    theme_css: str = "",
) -> str:
    """Replace template placeholders with actual data and theme CSS.

    Placeholders:
        - ``{{DATA}}`` is replaced with ``JSON.dumps(data_dict)``
        - ``{{THEME_CSS}}`` is replaced with the CSS file contents
        - ``{{GENERATED_AT}}`` is replaced with the current ISO timestamp

    Args:
        template_html: Raw HTML template string with placeholders.
        data_dict: Data to inject as JSON.
        theme_css: CSS string to inject for theming.

    Returns:
        Populated HTML string ready to write to disk.
    """
    json_str = json.dumps(data_dict, cls=_DateEncoder, ensure_ascii=False)
    generated_at = datetime.now().isoformat(timespec="seconds")

    result = template_html
    result = result.replace("{{DATA}}", json_str)
    result = result.replace("{{THEME_CSS}}", theme_css)
    result = result.replace("{{GENERATED_AT}}", generated_at)
    return result


def generate_individual(
    template_dir: Path,
    data: dict[str, Any],
    output_dir: Path,
    theme_css_path: Path | None = None,
) -> list[Path]:
    """Generate all 9 individual HTML visualization files.

    Each template receives the full data dict so it can pull the keys
    it needs. Templates are expected at ``template_dir/<template_name>``.

    Args:
        template_dir: Directory containing HTML template files.
        data: Full analysis data dict.
        output_dir: Directory to write generated HTML files.
        theme_css_path: Optional path to a CSS theme file.

    Returns:
        List of paths to generated HTML files.
    """
    template_dir = Path(template_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    theme_css = ""
    if theme_css_path and Path(theme_css_path).exists():
        theme_css = Path(theme_css_path).read_text(encoding="utf-8")

    generated: list[Path] = []

    for output_name, template_name in INDIVIDUAL_TEMPLATES.items():
        template_path = template_dir / template_name
        if not template_path.exists():
            logger.warning(
                "Template not found, skipping: %s", template_path
            )
            continue

        try:
            template_html = load_template(template_path)
            populated = inject_data(template_html, data, theme_css)
            output_path = output_dir / output_name
            output_path.write_text(populated, encoding="utf-8")
            generated.append(output_path)
            logger.info("Generated: %s", output_path)
        except Exception as exc:
            logger.error(
                "Failed to generate %s: %s", output_name, exc
            )

    return generated


def generate_dashboard(
    template_dir: Path,
    data: dict[str, Any],
    output_dir: Path,
    theme_css_path: Path | None = None,
) -> Path | None:
    """Generate the unified dashboard HTML file.

    The dashboard template receives the full data dict and is expected
    to embed or link to all individual visualizations.

    Args:
        template_dir: Directory containing HTML template files.
        data: Full analysis data dict.
        output_dir: Directory to write the dashboard HTML file.
        theme_css_path: Optional path to a CSS theme file.

    Returns:
        Path to the generated dashboard file, or None on failure.
    """
    template_dir = Path(template_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    template_path = template_dir / DASHBOARD_TEMPLATE
    if not template_path.exists():
        logger.error("Dashboard template not found: %s", template_path)
        return None

    theme_css = ""
    if theme_css_path and Path(theme_css_path).exists():
        theme_css = Path(theme_css_path).read_text(encoding="utf-8")

    try:
        template_html = load_template(template_path)
        populated = inject_data(template_html, data, theme_css)
        output_path = output_dir / "dashboard.html"
        output_path.write_text(populated, encoding="utf-8")
        logger.info("Generated dashboard: %s", output_path)
        return output_path
    except Exception as exc:
        logger.error("Failed to generate dashboard: %s", exc)
        return None


def generate_all(
    template_dir: Path,
    data: dict[str, Any],
    output_dir: Path,
    theme_css_path: Path | None = None,
) -> dict[str, Any]:
    """Generate all visualization HTML files (individual + dashboard).

    Also copies any static assets (images, fonts) from the template
    directory's ``assets/`` subfolder to the output directory.

    Args:
        template_dir: Directory containing HTML template files.
        data: Full analysis data dict.
        output_dir: Directory to write all generated files.
        theme_css_path: Optional path to a CSS theme file.

    Returns:
        Dict with keys ``individual`` (list of paths) and
        ``dashboard`` (path or None).
    """
    template_dir = Path(template_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy static assets if they exist
    assets_src = template_dir / "assets"
    if assets_src.is_dir():
        assets_dst = output_dir / "assets"
        if assets_dst.exists():
            shutil.rmtree(assets_dst)
        shutil.copytree(assets_src, assets_dst)
        logger.info("Copied assets to %s", assets_dst)

    individual = generate_individual(
        template_dir, data, output_dir, theme_css_path
    )
    dashboard = generate_dashboard(
        template_dir, data, output_dir, theme_css_path
    )

    return {
        "individual": individual,
        "dashboard": dashboard,
    }


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
        description=(
            "Generate HTML visualizations from LinkedIn analysis data."
        )
    )
    parser.add_argument(
        "--templates",
        type=Path,
        required=True,
        help="Path to directory containing HTML template files.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        required=True,
        help="Path to JSON data file (output of analyze.py).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output directory for generated HTML files.",
    )
    parser.add_argument(
        "--theme",
        type=Path,
        default=None,
        help="Path to CSS theme file (e.g. carrier-dark.css).",
    )
    parser.add_argument(
        "--dashboard-only",
        action="store_true",
        help="Generate only the dashboard (skip individual pages).",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging."
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # Load data
    if not args.data.exists():
        logger.error("Data file not found: %s", args.data)
        sys.exit(1)

    raw = args.data.read_text(encoding="utf-8")
    data = json.loads(raw)
    logger.info(
        "Loaded data with %d top-level keys: %s",
        len(data),
        ", ".join(data.keys()),
    )

    if args.dashboard_only:
        result = generate_dashboard(
            args.templates, data, args.output, args.theme
        )
        if result:
            print(f"Dashboard generated: {result}")
        else:
            sys.exit(1)
    else:
        results = generate_all(
            args.templates, data, args.output, args.theme
        )
        individual = results.get("individual", [])
        dashboard = results.get("dashboard")
        print(f"Generated {len(individual)} individual pages")
        if dashboard:
            print(f"Dashboard: {dashboard}")


if __name__ == "__main__":
    main()
