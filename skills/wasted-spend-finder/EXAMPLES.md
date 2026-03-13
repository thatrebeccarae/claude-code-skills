# Wasted Spend Finder — Examples

## Example 1: Google Ads Search Term Audit

**Prompt:**
> Analyze our Google Ads search terms for the last 60 days. Our average CPA is $45. Find wasted spend and generate a negative keyword list.

**Expected output:**
- Waste threshold: $90 (2x CPA for branded), $135 (3x CPA for non-brand)
- Findings: 127 search terms flagged, $8,400 total waste (12% of spend)
- Breakdown by theme:
  - Competitor terms: 23 terms, $2,100 wasted
  - Informational intent: 41 terms, $2,800 wasted
  - Job/career: 18 terms, $1,200 wasted
  - Geographic irrelevance: 12 terms, $900 wasted
  - Free/cheap intent: 33 terms, $1,400 wasted
- CSV output: `negative-keywords.csv` with match types per theme
- Estimated monthly savings: $4,200
- False positive check: 3 terms flagged for review (high-ticket consideration window)

---

## Example 2: Meta Placement Audit

**Prompt:**
> Check our Meta Ads placements for waste. We're spending $30K/month across Feed, Stories, Reels, and Audience Network. Average CPA is $22.

**Expected output:**
- Audience Network analysis: 18% of spend, 2% of conversions
  - 14 app placements with zero conversions, $3,200 wasted
  - Recommendation: exclude Audience Network for conversion campaigns
- Stories placement: $0.38 CPA vs. Feed $0.52 — efficient, keep
- Reels: high impressions, low clicks — brand awareness value, not waste
- Feed: 3 ad sets with frequency >5 and zero conversions, creative fatigue
- CSV output: `placement-exclusions.csv` and `audience-exclusions.csv`
- Estimated savings: $3,200/month from Audience Network exclusion alone

---

## Example 3: Cross-Platform Quarterly Cleanup

**Prompt:**
> Run a full wasted spend analysis across Google Ads and Meta for Q4. We spent $120K total. Generate all exclusion lists and estimate total recoverable budget.

**Expected output:**
- **Google Ads ($75K spent):**
  - Search term waste: $6,800 (9.1%)
  - Placement waste (Display): $3,200 (4.3%)
  - YouTube waste: $1,100 (1.5%)
  - Total Google waste: $11,100 (14.8%)

- **Meta Ads ($45K spent):**
  - Audience Network waste: $4,500 (10%)
  - Creative fatigue: $2,800 (6.2%)
  - Audience segment waste: $1,900 (4.2%)
  - Total Meta waste: $9,200 (20.4%)

- **Combined:** $20,300 wasted (16.9% of total spend)
- **Projected annual savings:** ~$81,200 if cleaned monthly
- 4 CSV exclusion files generated
- Priority actions: (1) Exclude Audience Network, (2) Add negative keyword themes, (3) Refresh fatigued creative, (4) Consolidate low-volume ad sets
