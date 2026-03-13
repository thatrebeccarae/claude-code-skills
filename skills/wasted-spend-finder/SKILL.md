---
name: wasted-spend-finder
description: "Systematic analysis of Google Ads and Meta advertising spend to identify wasted budget. Produces actionable exclusion lists with thematic categorization and statistical validation. Use when onboarding new accounts, performing monthly hygiene, or preparing for budget optimization."
license: MIT
origin: custom
author: Rebecca Rae Barton
author_url: https://github.com/thatrebeccarae
metadata:
  version: 1.0.0
  category: paid-media
  domain: optimization
  updated: 2026-03-13
---

# Wasted Spend Finder

Identify and categorize wasted ad spend across Google Ads and Meta platforms. Produces uploadable exclusion lists with thematic categorization.

## Core Capabilities

### Google Ads Waste Detection

1. **Search Term Waste** — zero-conversion terms above spend threshold
2. **Placement Waste** — Display Network sites/apps and YouTube channels with no conversions
3. **Keyword-Level Waste** — low conversion rate keywords relative to spend

### Meta Ads Waste Detection

1. **Placement Waste** — Audience Network apps, low-quality inventory
2. **Audience Segment Waste** — lookalike/interest targeting with poor performance
3. **Creative Waste** — high frequency + zero conversions, creative fatigue

## Waste Thresholds

### Spend Threshold Formula

```
Waste threshold = Average CPA x Multiplier

Multiplier by campaign type:
- Search (branded): 2x CPA
- Search (non-brand): 3x CPA
- Display: 3x CPA
- Meta (all): 2.5x CPA
```

A search term, placement, or audience segment is flagged as waste when:
- Spend exceeds the threshold AND
- Conversions = 0 AND
- Minimum click threshold is met

### Minimum Click Thresholds

| Campaign Type | Min Clicks Before Flagging |
|---------------|---------------------------|
| Search (branded) | 50 |
| Search (non-brand) | 25 |
| Display / GDN | 15 |
| YouTube | 20 |
| Meta Feed | 20 |
| Meta Stories | 15 |
| Meta Audience Network | 10 |

### Conversion Rate Minimums

Flag keywords/placements performing below these floors:

| Campaign Type | Min Conversion Rate |
|---------------|-------------------|
| Search (branded) | 8% |
| Search (non-brand) | 1.5% |
| Display | 0.3% |
| YouTube | 0.2% |
| Meta Feed | 0.5% |
| Meta Stories | 0.3% |

## Negative Keyword Categorization

Classify wasted search terms into themes for organized exclusion:

| Theme | Pattern | Match Type |
|-------|---------|------------|
| Competitor terms | Brand names, product names | Exact / Phrase |
| Informational intent | how to, what is, tutorial, guide, definition | Phrase |
| Wrong product/service | Related but non-target products | Phrase / Exact |
| Geographic irrelevance | Wrong cities, states, countries | Exact |
| Job/career searches | jobs, salary, hiring, career, resume | Phrase |
| Free/cheap intent | free, cheap, discount, coupon, deal | Phrase |
| Irrelevant modifiers | DIY, homemade, kids, old, used | Phrase |

## Placement Exclusion Categories

### Google Display Network
- Low-quality apps (game apps, utility apps, kids apps)
- Parked domains and MFA (made-for-advertising) sites
- Irrelevant content categories

### YouTube
- Music videos and lyrics channels
- Kids and animation content
- Gaming content (unless relevant)
- Clickbait and low-quality channels

### Meta Audience Network
- Game apps
- Utility and calculator apps
- Foreign language apps
- Apps with under 100 reviews

## Workflow

### 1. Data Collection

Pull data for the analysis period (typically 30-90 days):

**Google Ads:**
- Search terms report
- Placement report (Display + YouTube)
- Keyword performance report
- Campaign/ad group settings for CPA benchmarks

**Meta Ads:**
- Placement breakdown report
- Audience breakdown report
- Ad-level report with frequency data

### 2. Apply Thresholds

Calculate waste threshold per campaign using the formula above. Flag items exceeding thresholds.

### 3. Categorize

Assign each flagged item to a theme category. Group for batch exclusion.

### 4. Generate Exclusion Lists

Output CSV files ready for upload:
- `negative-keywords.csv` — with match type and campaign/ad group scope
- `placement-exclusions.csv` — with reason and spend wasted
- `audience-exclusions.csv` — with segment details and waste amount

### 5. Validate

- Cross-check that exclusions do not remove converting terms
- Verify match types will not over-exclude
- Estimate savings from the proposed exclusions

## Safety Rules

1. **Analysis only.** Never make live account changes without human review.
2. **Projections are estimates.** Label all savings projections clearly.
3. **Check for false positives.** Some high-spend zero-conversion terms may be in a consideration window.
4. **Consider attribution.** View-through and assisted conversions may justify some "wasted" spend.
5. **Preserve data.** Export current state before applying any exclusions.

For GAQL query patterns and CSV formats, see [REFERENCE.md](REFERENCE.md).
