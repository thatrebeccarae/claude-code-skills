---
name: html-report-builder
description: "Create polished HTML technical reports and multi-page documents for consulting deliverables. Features a professional design system with dark cover pages, warm cream content pages, Switzer + Cartograph CF typography, and a curated component library (KPI cards, data tables, callout boxes, recommendation cards, priority banners). Outputs standalone HTML that prints cleanly to PDF."
license: MIT
origin: custom
author: Rebecca Rae Barton
author_url: https://github.com/thatrebeccarae
metadata:
  version: 1.0.0
  category: reporting
  domain: consulting
  updated: 2026-03-13
---

# HTML Report Builder

Polished consulting reports as standalone HTML. Print to PDF via browser.

## When to Use

- Audit reports, performance analyses, strategy documents
- Any multi-section document that needs professional formatting
- When the deliverable is a report (not slides — use pro-deck-builder for decks)

## Quick Reference

| Task | Approach |
|------|----------|
| Create report from scratch | Read [REFERENCE.md](REFERENCE.md) for CSS + HTML patterns |
| Add a new component | Compose from existing components in REFERENCE.md |
| Export to PDF | Open in browser → Print → Save as PDF (Cmd+P) |
| Update design tokens | Edit CSS custom properties in `:root` block |

## Before You Start

Ask the user:

1. **What type of report?** Audit, strategy, performance review, case study?
2. **How many sections?** Helps plan the document structure.
3. **What data do they have?** Raw numbers, API exports, spreadsheets?
4. **Where should the file be saved?** Get an explicit path.

## Design System

### Color Tokens

```css
:root {
  /* Dark mode (cover page only) */
  --bg-deep: #141414;
  --bg-surface: #1E1E1E;
  --bg-elevated: #282828;
  --text-bright: #f0f3f6;
  --text-secondary-dark: #9ca3af;

  /* Light mode (content pages — the default) */
  --bg-light: #FAF7F2;
  --bg-light-surface: #F2EDE6;
  --text-primary: #0f0e0e;
  --text-secondary: #57606a;
  --text-muted: #8b949e;

  /* Brand accent */
  --accent: #3D7A5C;
  --accent-light: #6AB88A;

  /* Semantic */
  --green: #2e8b57;
  --red: #c0392b;
  --amber: #D97706;
}
```

### Color Rules

- Light mode (`#FAF7F2` warm cream) is default for all content pages. NOT white.
- Dark mode (`#141414`) only for: cover page.
- Accent green (`#3D7A5C`) used sparingly: key metrics, accent callouts.
- Semantic colors (green/amber/red) only for status indicators, never decoration.

### Typography

| Role | Font | Weight | Size |
|------|------|--------|------|
| Report title | Switzer | Light (300) | 48-64px |
| Section heading | Switzer | Regular (400) | 28-32px |
| Subsection heading | Switzer | Medium (500) | 20-22px |
| Body text | Switzer | Regular (400) | 16-17px |
| KPI number | Cartograph CF | Bold (700) | 36-48px |
| Data label | Cartograph CF | Regular (400) | 13px |
| Table data | Cartograph CF | Regular (400) | 14px |

**Critical rules:**
1. **Headlines use Light (300), NOT Bold.** Light at large sizes = confident, premium.
2. **Cartograph CF for ALL numeric/data content.** KPIs, table numbers, labels.
3. **Negative tracking on headlines.** -0.03em to -0.04em.
4. **Positive tracking on ALL CAPS labels.** +0.08em to +0.1em.

**Font loading:**
- Switzer: free from Fontshare CDN
- Cartograph CF: commercial, loaded via `local()`. Fallback: `'JetBrains Mono', 'Consolas', monospace`

## Document Structure

```
Cover Page (dark) → Table of Contents → Executive Summary → Findings (3-6 sections) → Recommendations → Appendix
```

## Component Library

| Component | Use |
|-----------|-----|
| KPI Card | Big number + label + detail |
| Data Table | Styled table with mono numbers, severity colors |
| Callout Box | Highlighted insight or bottom-line statement |
| Recommendation Card | Numbered action with impact + effort badges |
| Priority Banner | Critical/warning/info alert bar |
| Section Divider | Visual break between major sections |
| Bullet List | Styled list with custom markers |
| Numbered List | Ordered list with accent-colored numbers |

## Narrative Rules

1. **Lead with the number.** Metric-first, explanation second.
2. **One insight per section.** If a section makes two points, split it.
3. **Benchmark everything.** Never show a metric without context.
4. **Color = meaning.** Green/amber/red only for performance indicators.
5. **No white backgrounds.** Always warm cream `#FAF7F2`.
6. **No bold headlines.** Switzer Light (300) for report title and hero headings.

## PDF Export

Open the HTML file in Chrome/Safari → Cmd+P → Save as PDF. Set margins to "None" and enable "Background graphics."

For complete CSS framework and HTML patterns, see [REFERENCE.md](REFERENCE.md).
