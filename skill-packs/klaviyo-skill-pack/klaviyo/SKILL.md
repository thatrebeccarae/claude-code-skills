---
name: klaviyo
description: Klaviyo email and SMS marketing platform expertise. Audit flows, segments, campaigns, deliverability, and revenue attribution. Use when the user asks about Klaviyo, email marketing automation, SMS marketing, customer segmentation, flow optimization, or lifecycle marketing.
---

# Klaviyo Marketing Platform

Expert-level guidance for Klaviyo email and SMS marketing — auditing, building, and optimizing flows, segments, campaigns, and integrations.

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

## Workflow: Full Klaviyo Audit

When asked to audit a Klaviyo account:

1. **Flow Inventory** — List all active flows, identify gaps from the essential checklist above
2. **Flow Performance** — For each flow: revenue/recipient, conversion rate, open/click rates, timing between messages
3. **Segment Health** — Review engagement tiers, suppression lists, segment overlap
4. **Campaign Analysis** — Frequency, A/B test history, send-time optimization
5. **Deliverability Check** — Bounce rates, complaint rates, authentication status
6. **Integration Review** — E-commerce platform sync, review platform, loyalty program
7. **Revenue Attribution** — Flow vs campaign revenue split, attribution window settings
8. **Recommendations** — Prioritized by expected revenue impact (High/Medium/Low)

## Integration Context

### E-commerce Platforms
- **Shopify**: Native integration, syncs orders/products/customers automatically. Use Shopify-specific metrics (Placed Order, Started Checkout, Viewed Product).
- **WooCommerce / BigCommerce / Magento**: Similar event sync, may need plugin configuration.
- **Custom platforms**: Use Klaviyo API v2 for event tracking and profile management.

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

For detailed Klaviyo API reference, data model, and advanced configurations, see [REFERENCE.md](REFERENCE.md).
