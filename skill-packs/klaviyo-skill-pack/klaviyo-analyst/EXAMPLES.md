# Klaviyo Analyst Examples

Practical examples of common Klaviyo marketing analysis tasks and optimization patterns.

## Example 1: Full Account Health Audit

**User Request**: "Audit my Klaviyo account and tell me what needs fixing"

**Analysis Steps**:
1. Inventory all flows and compare against essential checklist
2. Assess segment structure and engagement tiers
3. Review campaign metrics against benchmarks
4. Check deliverability health
5. Analyze revenue attribution (flows vs campaigns)

**Script Command**:
```bash
python scripts/analyze.py --analysis-type full-audit --output audit.json
```

**Sample Output Analysis**:
```
Klaviyo Account Health Audit

=== FLOW AUDIT ===
Coverage: 7/10 essential flows

Essential Flows Checklist:
  ✓ Welcome Series — live
  ✓ Abandoned Cart — live
  ✓ Browse Abandonment — live
  ✓ Post-Purchase — live
  ✗ Winback — MISSING (HIGH priority)
  ✓ Sunset/Re-engagement — live
  ✗ Review Request — MISSING (MEDIUM priority)
  ✓ Replenishment — draft
  ✗ Birthday/Anniversary — MISSING (LOW priority)
  ✓ VIP/Loyalty — live

Active: 6 | Draft: 2 | Inactive: 1

=== SEGMENT HEALTH ===
Total Segments: 14 | Lists: 6
Engagement Tiers: ✓ Active (0-30d), ✓ Warm (31-90d), ✗ At-Risk, ✓ Lapsed
RFM Segments: ✗ Not found
Predictive Segments: ✗ Not found
Suppression Segment: ✓ Present

=== CAMPAIGN METRICS (Last 30 Days) ===
Campaigns Sent: 8 | Total Recipients: 124,500

Metric           Value    Benchmark    Rating
Open Rate        22.4%    20-25%       ✓ Good
Click Rate       1.8%     2-3%         ⚠ Warning
Unsubscribe      0.28%    <0.3%        ✓ Good
Spam Complaints  0.03%    <0.05%       ✓ Good

=== DELIVERABILITY ===
Delivery Rate: 97.8%
Bounce Rate: 2.2% — ✓ Good
Complaint Rate: 0.03% — ✓ Good
Authentication: Verify SPF, DKIM, DMARC records

=== REVENUE ATTRIBUTION ===
Total Email Revenue: $48,230
Flow Revenue: $19,780 (41.0%) — ✓ Good
Campaign Revenue: $28,450 (59.0%)

Top Flows by Revenue:
1. Abandoned Cart — $8,240
2. Welcome Series — $4,120
3. Post-Purchase — $3,890
4. Browse Abandonment — $2,130
5. VIP/Loyalty — $1,400

Recommendations:
1. HIGH: Create Winback flow — Expected: 5-8% of total email revenue
2. HIGH: Improve click rates (1.8% vs 2% benchmark) — Optimize CTAs
3. MEDIUM: Create Review Request flow — Indirect revenue via social proof
4. MEDIUM: Implement RFM segmentation — 15-25% lift in targeting
5. MEDIUM: Enable predictive segments (CLV, churn risk)
6. LOW: Create Birthday/Anniversary flow — 2-5% incremental revenue
```

## Example 2: Flow Gap Analysis

**User Request**: "What flows am I missing and which should I build first?"

**Analysis Steps**:
1. Fetch all flows from the account
2. Compare against the 10-flow essential checklist
3. Identify gaps and prioritize by revenue impact
4. Provide implementation recommendations

**Script Command**:
```bash
python scripts/analyze.py --analysis-type flow-audit
```

**Sample Output Analysis**:
```
Flow Gap Analysis

Essential Flows Checklist:
  ✓ Welcome Series — live (trigger: List Subscribe)
  ✓ Abandoned Cart — live (trigger: Started Checkout)
  ✓ Browse Abandonment — live (trigger: Viewed Product)
  ✓ Post-Purchase — live (trigger: Placed Order)
  ✗ Winback — MISSING (trigger: Time Since Last Purchase)
  ✗ Sunset/Re-engagement — MISSING (trigger: Engagement Date)
  ✓ Review Request — live (trigger: Fulfilled Order)
  ✗ Replenishment — MISSING (trigger: Predicted Next Order)
  ✗ Birthday/Anniversary — MISSING (trigger: Date Property)
  ✓ VIP/Loyalty — live (trigger: Segment Entry)

Coverage Score: 6/10

All Flows (12 total):
  live (8): Welcome Series, Abandoned Cart, Browse Abandonment,
            Post-Purchase, Review Request, VIP/Loyalty,
            Price Drop Alert, Back in Stock
  draft (2): Cross-Sell, Holiday Promo
  inactive (2): Old Welcome v1, Test Flow

Recommendations:
1. CRITICAL: Create Winback flow
   Trigger: 60-90 days since last purchase
   Structure: 3 emails (miss you → incentive → last chance)
   Expected Impact: 5-8% of total email revenue

2. HIGH: Create Sunset/Re-engagement flow
   Trigger: No email engagement in 90-180 days
   Structure: 2 emails (re-engage → suppress if no action)
   Expected Impact: Protect deliverability, reduce list costs

3. MEDIUM: Create Replenishment flow
   Trigger: Predicted next order date (or fixed interval)
   Structure: 1-2 emails before expected reorder
   Expected Impact: 5-10% of total email revenue

4. LOW: Create Birthday/Anniversary flow
   Trigger: Date property (requires birthday collection)
   Structure: 1 email with offer on/near birthday
   Expected Impact: 2-5% incremental revenue
```

## Example 3: Segment Health Check

**User Request**: "Are my segments set up correctly? What am I missing?"

**Analysis Steps**:
1. Fetch all segments and lists
2. Categorize by engagement tier
3. Check for RFM and predictive segments
4. Verify suppression segment exists

**Script Command**:
```bash
python scripts/analyze.py --analysis-type segment-health
```

**Sample Output Analysis**:
```
Segment Health Check

Summary:
  Total Segments: 18 | Total Lists: 8
  Engagement Tiers: ⚠ Partial
  RFM Segments: ✗ Not found
  Predictive Segments: ✗ Not found
  Suppression Segment: ✓ Present

Engagement Tiers:
  Active (0-30d):    ✓ 2 segments — "Engaged 30d Email", "Active SMS"
  Warm (31-90d):     ✓ 1 segment  — "Warm 31-90d"
  At-Risk (91-180d): ✗ MISSING
  Lapsed (180d+):    ✓ 1 segment  — "Lapsed 180d+"
  Suppression:       ✓ 1 segment  — "Never Engaged - Suppress"

Other Segments (13):
  "All Subscribers", "VIP Customers", "Repeat Buyers",
  "First-Time Buyers", "High AOV", "Discount Shoppers",
  "Email Only", "SMS Subscribers", "Product: Shoes",
  "Product: Accessories", "Geo: US", "Geo: International",
  "Holiday Buyers 2025"

Lists (8):
  "Newsletter Signup", "Footer Popup", "Exit Intent",
  "Checkout Opt-in", "SMS Opt-in", "Partner Import",
  "Event Attendees", "Manual Import"

Recommendations:
1. HIGH: Create "At-Risk" segment (91-180 days since engagement)
   Why: Gap in engagement funnel between "Warm" and "Lapsed"
   Impact: 20-30% better targeting for re-engagement flows

2. MEDIUM: Implement RFM segmentation
   Create segments based on: Recency × Frequency × Monetary value
   Suggested: Champions, Loyal, Promising, At-Risk, Lost
   Impact: 15-25% lift in campaign revenue

3. MEDIUM: Enable predictive segments
   Use Klaviyo AI: Predicted CLV, Churn Risk, Next Order Date
   Impact: 10-20% better targeting for winback and VIP flows

4. LOW: Consolidate overlapping segments
   Review "Repeat Buyers" vs "Loyal" potential overlap
   Impact: Cleaner segmentation, easier campaign planning
```

## Example 4: Campaign Performance Comparison

**User Request**: "How are my recent campaigns performing? Are we hitting benchmarks?"

**Analysis Steps**:
1. Fetch recent campaigns and their reports
2. Calculate aggregate metrics (open rate, click rate, etc.)
3. Compare each metric against industry benchmarks
4. Identify underperforming areas

**Script Command**:
```bash
python scripts/analyze.py --analysis-type campaign-comparison --days 30
```

**Sample Output Analysis**:
```
Campaign Performance (Last 30 Days)

Campaigns Analyzed: 12 | Total Recipients: 186,400

Aggregate Metrics vs Benchmarks:
  Metric              Value    Good     Great    Rating
  ─────────────────────────────────────────────────────
  Open Rate           24.2%    20-25%   30%+     ✓ Good
  Click Rate          3.1%     2-3%     4%+      ✓ Good
  Unsubscribe Rate    0.35%    <0.3%    <0.1%    ⚠ Warning
  Spam Complaint Rate 0.04%    <0.05%   <0.02%   ✓ Good
  Revenue/Recipient   $0.42    —        —        —

Top Performing Campaigns:
  Campaign                   Opens   Clicks  Revenue   RPR
  ──────────────────────────────────────────────────────────
  Valentine's Day Sale        31.2%   4.8%   $8,420   $0.68
  New Arrivals Feb            26.8%   3.5%   $4,210   $0.38
  VIP Early Access            28.4%   5.2%   $6,890   $1.24
  Weekly Newsletter #6        22.1%   2.8%   $1,240   $0.12

Underperforming Campaigns:
  Campaign                   Opens   Clicks  Unsub    Issue
  ──────────────────────────────────────────────────────────
  Flash Sale Reminder         18.2%   1.2%   0.52%   ❌ Low opens + high unsubs
  Re-engagement Blast         15.8%   0.9%   0.68%   ❌ Sent to cold list
  Product Update              19.4%   1.5%   0.41%   ⚠ Below benchmark

Recommendations:
1. HIGH: Reduce unsubscribe rate (0.35% vs <0.3% benchmark)
   - Review send frequency — consider reducing to 2-3x/week
   - Improve segmentation to match content to interests
   - Add preference center for frequency control
   Expected Impact: 50% reduction in unsubscribes

2. HIGH: Stop sending to cold/unengaged segments
   - "Re-engagement Blast" and "Flash Sale Reminder" hurt deliverability
   - Use sunset flow instead of mass re-engagement campaigns
   Expected Impact: Protect sender reputation

3. MEDIUM: Scale VIP-style targeted campaigns
   - VIP Early Access: best RPR ($1.24) and engagement
   - Create more exclusive, segmented sends
   Expected Impact: 20-30% higher campaign revenue
```

## Example 5: Deliverability Diagnostic

**User Request**: "My open rates are dropping — is there a deliverability problem?"

**Analysis Steps**:
1. Analyze bounce and complaint rates from recent sends
2. Check against ISP safety thresholds
3. Review authentication setup checklist
4. Identify root causes and fixes

**Script Command**:
```bash
python scripts/analyze.py --analysis-type deliverability
```

**Sample Output Analysis**:
```
Deliverability Diagnostic

Sending Summary (Recent Campaigns):
  Campaigns Checked: 15
  Total Sent: 242,800
  Total Delivered: 234,520
  Delivery Rate: 96.6%

Deliverability Metrics:
  Metric              Value    Threshold    Status
  ──────────────────────────────────────────────────
  Bounce Rate         3.4%     <2% good     ⚠ Elevated
  Spam Complaint Rate 0.08%    <0.05% good  ⚠ Elevated
  Delivery Rate       96.6%    >98% good    ⚠ Below target

Issues Identified:
  ⚠ HIGH: Elevated bounce rate (3.4%)
    Detail: Bounce rate 3.4% above 2% benchmark
    Impact: Sender reputation degradation over time
    Root Causes:
    - Stale email addresses in list
    - Insufficient list hygiene (no sunset flow or list cleaning)
    - Possible purchased/scraped email addresses in imports

  ⚠ HIGH: Elevated spam complaint rate (0.08%)
    Detail: Complaint rate 0.08% above 0.05% benchmark
    Impact: Gradual inbox placement decline
    Root Causes:
    - Sending to unengaged subscribers
    - Content not matching subscriber expectations
    - Send frequency too high for some segments

Authentication Checklist:
  SPF:   Verify include:_spf.klaviyo.com in DNS      → Check DNS records
  DKIM:  Verify CNAME records from Klaviyo Settings   → Check DNS records
  DMARC: Verify DMARC policy (p=quarantine or reject) → Check DNS records

Recommendations:
1. HIGH: Implement list cleaning
   - Remove hard bounces immediately (Klaviyo does this automatically)
   - Create sunset flow: suppress contacts unengaged 120+ days
   - Run email verification on imported lists before sending
   Expected Impact: Reduce bounces by 60-80%

2. HIGH: Review sending frequency and segmentation
   - Segment by engagement: send more to active, less to at-risk
   - Add preference center for frequency control
   - Exclude 90+ day unengaged from promotional campaigns
   Expected Impact: Reduce complaints by 50-70%

3. MEDIUM: Verify DNS authentication records
   - Run SPF, DKIM, DMARC checks on your sending domain
   - Set DMARC to p=quarantine (minimum) or p=reject
   - Consider dedicated sending domain for high-volume
   Expected Impact: Improved inbox placement across all ISPs

4. MEDIUM: IP warming (if on dedicated IP)
   - Follow warming schedule: 500/day → double every 2 days
   - Send to most engaged contacts first during warm-up
   - Monitor daily during warm-up period
   Expected Impact: Establish strong sender reputation
```

## Example 6: Revenue Attribution

**User Request**: "What percentage of our email revenue comes from flows vs campaigns?"

**Analysis Steps**:
1. Fetch revenue data from all flows
2. Fetch revenue data from recent campaigns
3. Calculate the flow vs campaign revenue split
4. Identify top revenue drivers and gaps

**Script Command**:
```bash
python scripts/analyze.py --analysis-type revenue-attribution
```

**Sample Output Analysis**:
```
Revenue Attribution Analysis

Total Email Revenue: $68,420

Revenue Split:
  Flow Revenue:     $28,940 (42.3%) — ✓ Good (benchmark: 30-50%)
  Campaign Revenue: $39,480 (57.7%)

Top Flows by Revenue:
  Flow                    Revenue    % of Flow Rev    Status
  ───────────────────────────────────────────────────────────
  Abandoned Cart          $11,240    38.8%            live
  Welcome Series          $6,420     22.2%            live
  Post-Purchase           $4,890     16.9%            live
  Browse Abandonment      $3,210     11.1%            live
  VIP/Loyalty             $1,840     6.4%             live
  Replenishment           $1,340     4.6%             live

Top Campaigns by Revenue:
  Campaign                Revenue    Recipients    RPR
  ─────────────────────────────────────────────────────
  Valentine's Day Sale    $12,840    12,400       $1.04
  VIP Early Access        $8,920     5,560        $1.60
  New Arrivals Feb        $6,240     11,200       $0.56
  Weekly Newsletter #5    $4,120     18,600       $0.22
  Flash Sale              $3,890     15,400       $0.25

Benchmark Comparison:
  Flow Revenue %: 42.3% — ✓ Good (industry benchmark: 30-50%)
  Revenue-generating flows: 6 — ✓ Healthy flow portfolio
  Top flow contribution: Abandoned Cart at 38.8% of flow revenue

Recommendations:
1. MEDIUM: Add Winback flow to increase flow revenue share
   Currently missing from flow portfolio
   Expected Impact: +5-8% of total email revenue

2. MEDIUM: Optimize Welcome Series
   Currently 22.2% of flow revenue — room to grow
   Actions: Add product recommendations, extend to 5 emails
   Expected Impact: +20-30% Welcome Series revenue

3. LOW: Diversify campaign revenue
   VIP Early Access has best RPR ($1.60) — scale this format
   Reduce reliance on broad promotional blasts
   Expected Impact: Higher campaign ROI
```

## Common Analysis Patterns

### Audit Cadence Template
```python
# Monthly: Campaign metrics review, segment health check
# Quarterly: Full account audit, flow optimization
# Semi-annual: Deliverability deep-dive, integration review
# Annual: Strategy review, benchmark comparison
```

### Benchmark Comparison Template
```python
# Pull current metrics → Compare to BENCHMARKS dict
# Flag metrics below "good" threshold
# Identify trends (improving, stable, declining)
# Prioritize fixes by revenue impact
```

### Flow Optimization Template
```python
# For each active flow:
#   1. Check revenue per recipient
#   2. Compare open/click rates to benchmarks
#   3. Review timing between messages
#   4. Check for split test opportunities
#   5. Verify flow filters are current
```

### Segment Strategy Template
```python
# Build engagement ladder: Active → Warm → At-Risk → Lapsed → Suppressed
# Layer with: Purchase behavior (RFM), Predictive (CLV, churn)
# Create suppression segments for: unengaged, bounced, complained
# Review segment overlap quarterly
```

## Pro Tips

### Ask Better Questions
Instead of: "Show me my Klaviyo data"
Ask: "What are the top 3 revenue opportunities in my Klaviyo account?"

### Request Actionable Insights
Instead of: "What's my open rate?"
Ask: "Are my email metrics hitting industry benchmarks, and what should I fix first?"

### Focus on Revenue Impact
Instead of: "List all my flows"
Ask: "Which flows are missing and how much revenue am I leaving on the table?"

### Request Prioritization
Instead of: "What should I improve?"
Ask: "Give me a prioritized action plan for the next 30 days"

### Compare Periods
Instead of: "How are campaigns doing?"
Ask: "How do this month's campaign metrics compare to last month?"
