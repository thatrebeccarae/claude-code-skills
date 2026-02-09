---
name: klaviyo-analyst
description: Klaviyo marketing operations and analyst expertise. Audit flows, segments, campaigns, deliverability, and revenue attribution. Use when the user asks about Klaviyo marketing strategy, email/SMS automation, customer segmentation, flow optimization, or lifecycle marketing. For API integration, SDK, webhook, or developer questions, see the klaviyo-developer skill.
---

# Klaviyo Marketing Analyst

Expert-level guidance for Klaviyo email and SMS marketing from the **marketing operations and analyst perspective** — auditing, building, and optimizing flows, segments, campaigns, and integrations.

> For API integration, SDK usage, event tracking implementation, webhooks, and developer patterns, see the **klaviyo-developer** skill.

## Core Capabilities

### Flow Auditing & Optimization
- Audit existing flows against best practices (welcome series, abandoned cart, post-purchase, winback, browse abandonment, sunset)
- Identify revenue leakage from missing or underperforming flows
- Recommend split tests, timing adjustments, and conditional logic improvements
- Review flow filters and trigger conditions for accuracy

### Segmentation Strategy
- Build RFM-based segments (Recency, Frequency, Monetary)
- Design engagement tiers: Active (0-30d), Warm (31-90d), At-Risk (91-180d), Lapsed (180d+)
- Create predictive segments using Klaviyo's predictive analytics (CLV, churn risk, next order date)
- Suppress unengaged contacts to protect deliverability

### Campaign Strategy
- Plan campaign calendars balancing promotional and value content
- A/B testing frameworks for subject lines, send times, content blocks
- Dynamic content personalization using profile properties and catalog data
- SMS campaign compliance (TCPA, quiet hours, opt-in requirements)

### Deliverability Management
- Monitor and diagnose deliverability issues (bounce rates, spam complaints, inbox placement)
- Warm-up strategies for new sending domains/IPs
- Authentication setup: SPF, DKIM, DMARC
- List hygiene practices and sunset flow design

### Revenue Attribution & Reporting
- Interpret Klaviyo's attribution model (click-based, 5-day email / 24-hour SMS default windows)
- Build custom dashboards for flow revenue, campaign ROI, list growth
- Benchmark KPIs against industry standards

### Event Schema Auditing
- Inventory all tracked metrics by source (built-in integration, custom API, Klaviyo-internal, forms)
- Identify duplicate/redundant events, unused events, and missing standard events
- Assess event property structures for segmentation and personalization accessibility
- Diagnose nested object limitations blocking flow splits and segment conditions

### Integration Health Review
- Audit active integrations (e-commerce, review platforms, loyalty, ads)
- Identify stale/dead integrations and orphaned event sources
- Assess flow trigger architecture: direct metric triggers (robust) vs segment-entry triggers via API-synced properties (brittle)
- Evaluate catalog sync health: product coverage, variant handling, freshness

### Profile Data Utilization Analysis
- Map profile properties: what's collected vs what's used in segmentation/personalization
- Identify stale calculated properties (set once, never updated)
- Flag properties on events but not synced to profiles (limits segmentation)
- Recommend property flattening strategies for nested data accessibility

## Key Benchmarks

| Metric | Good | Great | Warning |
|--------|------|-------|---------|
| Open Rate (email) | 20-25% | 30%+ | <15% |
| Click Rate (email) | 2-3% | 4%+ | <1.5% |
| Unsubscribe Rate | <0.3% | <0.1% | >0.5% |
| Spam Complaint Rate | <0.05% | <0.02% | >0.1% |
| Flow Revenue % of Total | 30-40% | 50%+ | <20% |
| SMS Click Rate | 8-12% | 15%+ | <5% |
| List Growth Rate (monthly) | 3-5% | 8%+ | <1% |

## Essential Flows Checklist

1. **Welcome Series** (3-5 emails + optional SMS) — triggers on list subscribe
2. **Abandoned Cart** (2-3 emails + 1 SMS) — triggers on Started Checkout
3. **Browse Abandonment** (1-2 emails) — triggers on Viewed Product, exclude recent purchasers
4. **Post-Purchase** (2-4 emails) — triggers on Placed Order, split by first-time vs repeat
5. **Winback** (2-3 emails) — triggers on time since last purchase (60-90 days)
6. **Sunset/Re-engagement** (2 emails) — targets unengaged 90-180 days, then suppress
7. **Review Request** — triggers post-delivery, integrates with review platform
8. **Replenishment** (if applicable) — triggers based on expected repurchase cycle
9. **Birthday/Anniversary** — triggers on date property
10. **VIP/Loyalty** — triggers on high-CLV segment entry

## Workflow: Full Klaviyo Audit (4-Phase Deep Framework)

When asked to audit a Klaviyo account, follow this 4-phase framework:

### Phase 1: Status Inventory
1. **List/Segment/Flow/Campaign Inventory** — Count and categorize all objects by status (live, draft, inactive)
2. **Event Schema Inventory** — Pull all metrics, categorize by source (built-in, custom API, Klaviyo-internal, forms), flag zero-volume events
3. **Integration Inventory** — List all active integrations, identify stale connections
4. **Custom Profile Property Inventory** — Document all custom properties with types and usage

### Phase 2: Configuration Audit
5. **Per-Flow Configuration Teardown** — For each active flow:
   - Trigger type and conditions
   - Smart Send settings (on/off and implications)
   - Exclusion filters (segment membership, event conditions)
   - Timing between messages (compare to benchmarks)
   - Branching logic (conditional splits, A/B splits)
   - Flow duration (first message to last)
6. **Campaign Targeting Audit** — Segment exclusivity, frequency capping, send-time optimization
7. **A/B Testing Methodology Audit** — Univariate vs multivariate, KPI alignment, statistical significance practices
8. **Deliverability Configuration** — Authentication (SPF/DKIM/DMARC), dedicated IP, warmup status

### Phase 3: Data Structure Audit
9. **Event Schema Health** — Check for duplicates, missing standard events, nested objects blocking segmentation
10. **Profile Data Utilization** — What's collected vs what's used in segmentation/personalization
11. **Catalog Sync Health** — Product feed freshness, coverage, variant handling

### Phase 4: Strategic Recommendations
12. **Three-Tier Recommendations** — For each finding:
    - **Finding**: What's wrong + evidence from audit data
    - **Recommendation**: What to do (client-facing, plain language)
    - **Implementation Spec**: How to build it (internal SOW with triggers, filters, content brief, timing, testing plan)
13. **Sequential Testing Plans** — Univariate A/B tests with stat sig framework
14. **Quantified ROI** — Expected uplift % x current revenue baseline
15. **Implementation Roadmap** — Phased timeline with dependencies mapped

## Industry-Specific Benchmarks

### B2B / Wholesale E-Commerce

| Metric | Good | Great | Warning | Notes |
|--------|------|-------|---------|-------|
| Open Rate | 25-35% | 40%+ | <20% | Higher than DTC due to professional relevance |
| Click Rate | 3-5% | 6%+ | <2% | Product-focused CTAs perform well |
| CTOR | 10-15% | 18%+ | <8% | Key diagnostic — content relevance signal |
| Flow Revenue % | 25-35% | 40%+ | <15% | Reorder flows are high-value in B2B |
| Avg Order Value | Varies | — | — | Track by segment (industry, company size) |
| Reorder Rate | 60-70% | 80%+ | <50% | Critical for consumable categories |

### DTC (Direct-to-Consumer)

| Metric | Good | Great | Warning |
|--------|------|-------|---------|
| Open Rate | 20-25% | 30%+ | <15% |
| Click Rate | 2-3% | 4%+ | <1.5% |
| Flow Revenue % | 30-40% | 50%+ | <20% |
| Welcome Series Conv. | 3-5% | 8%+ | <2% |
| Cart Recovery Rate | 5-10% | 15%+ | <3% |

### Subscription / Recurring Revenue

| Metric | Good | Great | Warning |
|--------|------|-------|---------|
| Churn Rate (monthly) | <5% | <3% | >8% |
| Reactivation Rate | 5-10% | 15%+ | <3% |
| Replenishment Flow Conv. | 8-12% | 15%+ | <5% |
| Subscription Upgrade Rate | 3-5% | 8%+ | <1% |

## SMS Platform Comparison Framework

When evaluating Klaviyo SMS vs Attentive (common in audits):

| Capability | Klaviyo SMS | Attentive |
|------------|------------|-----------|
| Email + SMS unified | Yes (native) | No (separate platform) |
| Shared segments | Yes | Requires sync |
| Unified attribution | Yes | Separate reporting |
| Conversational SMS | Limited | Strong (two-way) |
| Sign-up units | Basic (popup, form) | Advanced (two-tap, link-based) |
| AI features | Predictive analytics, smart send time | AI journeys, smart sending |
| Compliance | Built-in TCPA, quiet hours | Built-in + compliance team |
| Cost | Included in Klaviyo plan (per SMS) | Separate platform fee + per SMS |
| Best for | Unified email+SMS, simplicity | SMS-first strategy, high volume SMS |

**Recommendation framework**: Use Klaviyo SMS when email is the primary channel and SMS is supplementary (most B2B and mid-market DTC). Consider Attentive when SMS is a primary revenue channel (high-frequency DTC, mobile-first brands).

## Repeatable Audit Workflow (MCP Tool Sequence)

When auditing an account via the Klaviyo MCP tools, follow this sequence:

1. `klaviyo_get_account_details` — Account config, timezone, integrations
2. `klaviyo_get_metrics` — Full event inventory (all metric names and IDs)
3. `klaviyo_get_flows` — All flows with status
4. `klaviyo_get_flow` (per flow) — Trigger details, actions, filters for each live flow
5. `klaviyo_get_campaigns` — Recent campaigns with send dates
6. `klaviyo_get_campaign_report` (per campaign) — Open/click/unsub/revenue metrics
7. `klaviyo_get_flow_report` (per flow) — Revenue, conversion, engagement per flow
8. `klaviyo_get_segments` + `klaviyo_get_segment` — Segment inventory and condition definitions
9. `klaviyo_get_lists` — List inventory
10. `klaviyo_get_catalog_items` — Catalog sync health check

After data pull, analyze using the 4-Phase Deep Framework above.

## Integration Context

### E-commerce Platforms
- **Shopify**: Native integration, syncs orders/products/customers automatically. Use Shopify-specific metrics (Placed Order, Started Checkout, Viewed Product).
- **WooCommerce / BigCommerce / Magento**: Similar event sync, may need plugin configuration.
- **Custom platforms**: Coordinate with developers using the **klaviyo-developer** skill for API event tracking and profile management.

### Common Integration Points
- Review platforms (Yotpo, Judge.me, Stamped) for post-purchase review flows
- Loyalty programs (Smile.io, LoyaltyLion) for points-based segmentation
- Subscription platforms (Recharge, Bold) for subscription lifecycle flows
- SMS: Built-in Klaviyo SMS or integration with Attentive/Postscript

## How to Use This Skill

Ask me questions like:
- "Audit my Klaviyo flows and identify gaps"
- "Design a welcome series for my DTC brand"
- "My open rates dropped — help me diagnose deliverability issues"
- "Build an RFM segmentation strategy"
- "What A/B tests should I run on my abandoned cart flow?"
- "Help me set up a sunset flow to clean my list"
- "Plan a Black Friday email/SMS campaign calendar"
- "Audit my event schema — are we tracking everything we need?"
- "Give me a three-tier recommendation for fixing our click rates"

## Analysis Examples

For complete analysis patterns, worked examples with sample output, and use cases, see [EXAMPLES.md](EXAMPLES.md).

## Scripts

The skill includes utility scripts for data fetching and analysis:

### Fetch Klaviyo Data
```bash
# List all flows
python scripts/klaviyo_client.py --resource flows

# List campaigns as table
python scripts/klaviyo_client.py --resource campaigns --format table

# Get flow performance report
python scripts/klaviyo_client.py --resource report --report-type flow --id FLOW_ID

# Export metrics to file
python scripts/klaviyo_client.py --resource metrics --output metrics.json
```

### Analyze and Generate Reports
```bash
# Full account audit
python scripts/analyze.py --analysis-type full-audit

# Flow gap analysis
python scripts/analyze.py --analysis-type flow-audit

# Segment health check
python scripts/analyze.py --analysis-type segment-health

# Campaign performance comparison
python scripts/analyze.py --analysis-type campaign-comparison --days 30

# Deliverability diagnostic
python scripts/analyze.py --analysis-type deliverability

# Revenue attribution
python scripts/analyze.py --analysis-type revenue-attribution
```

The scripts handle API authentication, data fetching, and analysis. I'll interpret the results and provide actionable recommendations.

## Troubleshooting

**Authentication Error**: Verify that:
- `KLAVIYO_API_KEY` is set as an environment variable or in a `.env` file
- The key starts with `pk_` (private API key, not public)
- The key has read scopes: `profiles:read`, `flows:read`, `campaigns:read`, `segments:read`, `lists:read`, `metrics:read`

**No Data Returned**: Check that:
- The API key is associated with the correct Klaviyo account
- The account has active flows, campaigns, or segments to analyze
- Filters are correctly formatted (e.g., `equals(status,"live")`)

**Rate Limit Errors**: The SDK handles retries automatically (up to 3 retries with 60s max delay). If you still hit limits:
- Reduce concurrent requests
- Add delays between sequential calls
- Check `RateLimit-Remaining` header

**Import Errors**: Install required packages:
```bash
pip install klaviyo-api python-dotenv pandas
```

## Security Notes

- **Never hardcode** API keys in code or commit them to version control
- Store keys in environment variables or `.env` files
- Add `.env` to `.gitignore`
- Use **read-only scopes** for analyst tasks — no write access needed
- Rotate API keys periodically in Klaviyo Settings

## Data Privacy

This skill accesses aggregated marketing data only. It does not:
- Access personally identifiable information (PII) beyond email/profile aggregates
- Store Klaviyo data persistently
- Share data with external services
- Modify your Klaviyo configuration (read-only operations)

All data is processed locally and used only to generate recommendations during the conversation.

For detailed Klaviyo data model, flow builder reference, segmentation conditions, deliverability, and SMS reference, see [REFERENCE.md](REFERENCE.md).

For API integration, SDK usage, and developer patterns, use the **klaviyo-developer** skill.
