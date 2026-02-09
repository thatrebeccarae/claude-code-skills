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
  OK Welcome Series — live
  OK Abandoned Cart — live
  OK Browse Abandonment — live
  OK Post-Purchase — live
  XX Winback — MISSING (HIGH priority)
  OK Sunset/Re-engagement — live
  XX Review Request — MISSING (MEDIUM priority)
  OK Replenishment — draft
  XX Birthday/Anniversary — MISSING (LOW priority)
  OK VIP/Loyalty — live

Active: 6 | Draft: 2 | Inactive: 1

=== SEGMENT HEALTH ===
Total Segments: 14 | Lists: 6
Engagement Tiers: OK Active (0-30d), OK Warm (31-90d), XX At-Risk, OK Lapsed
RFM Segments: XX Not found
Predictive Segments: XX Not found
Suppression Segment: OK Present

=== CAMPAIGN METRICS (Last 30 Days) ===
Campaigns Sent: 8 | Total Recipients: 124,500

Metric           Value    Benchmark    Rating
Open Rate        22.4%    20-25%       OK Good
Click Rate       1.8%     2-3%         !! Warning
Unsubscribe      0.28%    <0.3%        OK Good
Spam Complaints  0.03%    <0.05%       OK Good

=== REVENUE ATTRIBUTION ===
Total Email Revenue: $52,400
Flow Revenue: $21,500 (41.0%) — OK Good
Campaign Revenue: $30,900 (59.0%)

Top Flows by Revenue:
1. Abandoned Cart — $8,750
2. Welcome Series — $4,600
3. Post-Purchase — $4,200
4. Browse Abandonment — $2,350
5. VIP/Loyalty — $1,600
```

## Example 2: Flow Gap Analysis

**User Request**: "What flows am I missing and which should I build first?"

**Script Command**:
```bash
python scripts/analyze.py --analysis-type flow-audit
```

**Sample Output** (abbreviated — see SKILL.md Essential Flows Checklist for full pattern):
```
Coverage Score: 6/10
Missing: Winback (CRITICAL), Sunset (HIGH), Replenishment (MEDIUM), Birthday (LOW)
```

## Example 3: Segment Health Check

**User Request**: "Are my segments set up correctly?"

**Script Command**:
```bash
python scripts/analyze.py --analysis-type segment-health
```

Focus on: engagement tier completeness, RFM presence, suppression segment, mutual exclusivity.

## Example 4: Campaign Performance Comparison

**User Request**: "How are my recent campaigns performing?"

**Script Command**:
```bash
python scripts/analyze.py --analysis-type campaign-comparison --days 30
```

Compare: open rate, click rate, CTOR, unsub rate, spam rate, RPR against benchmarks. Flag underperformers.

## Example 5: Deliverability Diagnostic

**User Request**: "My open rates are dropping — deliverability problem?"

**Script Command**:
```bash
python scripts/analyze.py --analysis-type deliverability
```

Check: bounce rate (<2%), spam complaints (<0.05%), delivery rate (>98%), SPF/DKIM/DMARC auth.

## Example 6: Revenue Attribution

**User Request**: "What % of revenue comes from flows vs campaigns?"

**Script Command**:
```bash
python scripts/analyze.py --analysis-type revenue-attribution
```

Benchmark: flow revenue should be 30-50% of total. Below 20% = major flow gap.

---

## Example 7: Per-Flow Configuration Audit

**User Request**: "Do a deep audit of my abandoned cart flow configuration"

This is a Phase 2 (Configuration Audit) analysis — goes beyond flow existence to examine how the flow is built.

**Sample Output Analysis**:
```
=== FLOW CONFIGURATION AUDIT: Abandoned Cart ===

Trigger: Segment Entry — "Added to Cart - Active"
  Type: Segment-based (not direct metric trigger)
  Risk: MEDIUM — If API stops syncing cart data to profiles,
        segment stops updating and flow stops triggering.
  Recommendation: Consider direct metric trigger on "Started Checkout"
                  or "Added to Cart" event for resilience.

Messages: 1 email
  Email 1: "Complete Your Order" — Sends immediately on segment entry
  Issue: Single email only. Best practice is 2-3 emails.

Smart Send: ON (16-hour window)
  Issue: Smart Send should be OFF for abandoned cart.
         Cart recovery is time-sensitive — delays reduce conversion.
  Impact: Estimated 10-20% of recipients delayed past optimal window.

Exclusion Filters:
  - "Has Placed Order at least 1 time in the last 4 hours" — OK
  - Missing: No exclusion for profiles already in Welcome Series
  Issue: New subscribers could receive Welcome Email 1 AND Cart Email 1
         on the same day, creating a jarring experience.

Flow Duration: 0 days (single immediate email)
  Benchmark: 2-3 days with 3 touchpoints
  Issue: Missing follow-up emails means ~60% of recoverable carts are lost.

Timing Analysis:
  Email 1 at 0h — OK (immediate is correct for first touch)
  No Email 2 at 24h — MISSING (urgency reminder)
  No Email 3 at 48-72h — MISSING (last chance + incentive)

A/B Testing: None active
  Recommendation: Test subject line first (urgency vs benefit),
                  then CTA placement, then incentive.

=== THREE-TIER RECOMMENDATION ===

Finding: Abandoned Cart flow has 1 email (should be 3), Smart Send ON
(should be OFF), and no exclusion for Welcome Series overlap. Single
email captures only ~40% of recoverable revenue.

Recommendation: Expand to 3-email series with Smart Send OFF, add
Welcome Series exclusion filter, implement sequential A/B testing
program starting with subject lines.

Implementation Spec: Build steps include detailed trigger configuration,
content briefs per email, timing, conditional splits, and testing plan.
See the implementation spec section for full details.
```

## Example 8: Event Schema Audit

**User Request**: "Audit our event tracking — are we capturing everything we need?"

This is a Phase 3 (Data Structure Audit) analysis using the MCP metrics endpoint.

**Sample Output Analysis**:
```
=== EVENT SCHEMA AUDIT ===

Total Metrics: 50 across 4 sources

Source Breakdown:
  API (Custom Integration): 10 metrics
    Placed Order (AbC12d)         — Active, revenue-tracked
    Started Checkout (XyZ78e)     — Active, used in flows
    Viewed Product (Mn34Pq)       — Active, NOT used in any flow
    Added to Cart (Rs56Tu)        — Active, NOT used in any flow
    Order Completed (Jk90Wx)      — Active, used in post-purchase flow
    Cancelled Order               — Active, NOT used
    Refunded Order                — Active, NOT used
    Cart Viewed                   — Active, NOT used
    Account Created               — Active, used in welcome flow
    Subscription Started          — Active, NOT used

  Klaviyo Internal: 24 metrics
    Received Email, Opened Email, Clicked Email, Bounced Email,
    Marked Email as Spam, Unsubscribed, Subscribed to List, etc.
    Status: All normal — auto-tracked by Klaviyo

  Klaviyo Forms: 14 metrics
    submitted_back_in_stock_form (Fg45Hj) — Active, potential flow trigger
    Various form submissions — Active

  Meta Ads: 1 metric
    Ads Audience Synced — Active

Issues Identified:

1. UNUSED HIGH-VALUE EVENTS (HIGH)
   Viewed Product — Tracked but not used in any flow.
   Impact: Missing Browse Abandonment flow ($15K-$30K/year potential).
   Action: Build Browse Abandonment flow (see implementation spec).

   Added to Cart — Tracked but not used in any flow.
   Impact: Could supplement Started Checkout for cart recovery.
   Action: Evaluate as backup trigger for Abandoned Cart flow.

2. POTENTIAL DUPLICATE: Cart Viewed vs Added to Cart (MEDIUM)
   Both track cart-related activity. Need to verify if they capture
   different user actions or are redundant.
   Action: Check event properties and volumes. If duplicate, deprecate one.

3. UNUSED EVENTS (LOW)
   Cancelled Order, Refunded Order — Tracked but not used.
   Opportunity: Use Cancelled Order to suppress from post-purchase flows.
   Use Refunded Order to trigger save-the-sale re-engagement.

4. MISSING STANDARD EVENT: Fulfilled Order (MEDIUM)
   Not detected via API source. May be tracked under different name
   ("Order Completed" Jk90Wx may serve this purpose).
   Action: Verify Order Completed includes fulfillment/shipping data.
   If not, add Fulfilled Order event for review request flow timing.

Event Property Accessibility:
  Placed Order Items[] — Nested (templates only, not segments/splits)
  Placed Order $value — Top-level (full access)
  Placed Order Categories — Top-level array (segmentable via "contains")
  Profile company_type — Top-level string (full access)
  Profile industry — Top-level array (segmentable via "contains")
```

## Example 9: Three-Tier Recommendation Format

**Example of the standard recommendation format used in Phase 4 output:**

```
=== FINDING ===
Welcome flow bounce rate is 8.7% (435 bounces out of 5,000 recipients).
Industry benchmark is <2%. This is 4x above acceptable levels.
Root cause: The trigger segment ("New Subscribers - 14 Day") includes
profiles up to 14 days old, many of which have stale/invalid emails from
abandoned registrations.

=== RECOMMENDATION (Client-Facing) ===
Fix the Welcome flow bounce rate by tightening the trigger window and adding
email verification. This protects your sender reputation, which underpins
$750K in annual campaign revenue. Without action, deliverability will degrade
over the next 3-6 months, reducing inbox placement across all sends.

Priority: P1 (Critical)
Timeline: 1-2 weeks
Expected Impact: Protects $1M+ annual email revenue

=== IMPLEMENTATION SPEC (Internal SOW) ===

Prerequisites:
- Access to API/backend for email verification integration
- Klaviyo admin access for segment and flow modifications

Step 1: Tighten trigger segment window from 14 days to 3 days
  - Edit segment "New Subscribers - 14 Day"
  - Change condition: "created in the last 3 days" (was 14)
  - Rationale: 90%+ of valid signups engage within 3 days

Step 2: Integrate email verification at registration
  - Add ZeroBounce/NeverBounce API call on account creation
  - Set profile property: email_verified = true/false
  - Add segment condition: email_verified = true

Step 3: Suppress existing hard-bounced profiles
  - Create segment: "Hard Bounced - Never Purchased"
  - Suppress via profile suppression bulk job
  - Estimated: 500-1,000 profiles

Step 4: Monitor
  - Track bounce rate weekly for 30 days
  - Target: <1% within 2 weeks of implementation

Testing Plan:
  - No A/B test needed (this is a fix, not an optimization)
  - Monitor: bounce rate, delivery rate, welcome flow conversion rate
  - Success: bounce rate <2% sustained for 30 days

Dependencies: None (this is the first action in the roadmap)
```

---

## Common Analysis Patterns

### Audit Cadence
- **Monthly**: Campaign metrics review, segment health check
- **Quarterly**: Full account audit, flow optimization
- **Semi-annual**: Deliverability deep-dive, integration review
- **Annual**: Strategy review, benchmark comparison

### Flow Optimization Sequence
1. Check revenue per recipient
2. Compare open/click rates to benchmarks
3. Review timing between messages
4. Check for split test opportunities
5. Verify flow filters are current

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

### Request Implementation Specs
Instead of: "What should I improve?"
Ask: "Give me a three-tier recommendation with an implementation SOW for fixing my click rates"

### Compare Periods
Instead of: "How are campaigns doing?"
Ask: "How do this month's campaign metrics compare to last month?"
