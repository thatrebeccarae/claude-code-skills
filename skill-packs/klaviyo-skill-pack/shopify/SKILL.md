---
name: shopify
description: Shopify e-commerce platform marketing expertise. Audit store performance, optimize conversion funnels, configure tracking, and integrate marketing tools. Use when the user asks about Shopify, e-commerce optimization, Shopify analytics, store conversion, product feeds, or Shopify app integrations.
---

# Shopify Marketing & E-commerce

Expert-level guidance for Shopify — optimizing store conversion, marketing integrations, analytics, product feeds, and the full e-commerce marketing stack.

## Core Capabilities

### Store Performance Auditing
- Conversion funnel analysis (visit → add to cart → checkout → purchase)
- Site speed and Core Web Vitals assessment
- Mobile experience review (60-70%+ of DTC traffic is mobile)
- Checkout optimization (Shopify Checkout extensibility, one-page checkout)
- Product page optimization (layout, copy, social proof, urgency)

### Marketing Integrations
- **Email/SMS**: Klaviyo (recommended), Omnisend, Postscript, Attentive
- **Ads**: Meta Pixel + CAPI, Google Ads + Enhanced Conversions, TikTok Pixel, Pinterest Tag
- **Attribution**: Triple Whale, Northbeam, Polar Analytics, Lifetimely
- **Reviews**: Judge.me, Yotpo, Stamped, Loox (photo reviews)
- **Loyalty**: Smile.io, LoyaltyLion, Yotpo Loyalty
- **Subscriptions**: Recharge, Loop, Bold, Skio
- **SEO**: JSON-LD structured data, sitemap optimization, page speed

### Analytics & Reporting
- Shopify Analytics (built-in) — sessions, conversion rate, AOV, returning customer rate
- GA4 integration via Google & YouTube channel or GTM
- Server-side tracking setup (Shopify Pixel API + CAPI)
- Customer cohort analysis (LTV, retention, purchase frequency)
- Product analytics (sell-through rate, margin analysis)

### Product Feed Management
- Google Merchant Center feed optimization
- Facebook/Instagram Catalog (via Meta Commerce Manager)
- Feed attribute optimization: title, description, product type, custom labels
- Variant handling and inventory sync
- Disapproval diagnosis and feed error resolution

### Conversion Rate Optimization (CRO)
- A/B testing (using Shopify's built-in or tools like Shoplift, Visually)
- Collection page optimization (filters, sorting, layout)
- Cart and checkout optimization (cart drawer vs page, upsells, trust badges)
- Post-purchase upsell flows (Zipify OCU, ReConvert, AfterSell)
- Pop-up and lead capture strategy (Privy, Justuno, Wisepops)

## Key Benchmarks

| Metric | Good | Great | Warning |
|--------|------|-------|---------|
| Overall Conversion Rate | 2-3% | 4%+ | <1.5% |
| Add-to-Cart Rate | 8-10% | 12%+ | <5% |
| Cart-to-Checkout Rate | 50-60% | 70%+ | <40% |
| Checkout Completion Rate | 45-55% | 60%+ | <35% |
| AOV | Industry dependent | Growing trend | Declining |
| Returning Customer Rate | 25-30% | 40%+ | <20% |
| Mobile Conversion Rate | 1.5-2.5% | 3%+ | <1% |
| Email Revenue % | 25-35% | 40%+ | <15% |
| LTV:CAC Ratio | 3:1 | 4:1+ | <2:1 |
| Page Load (LCP) | <2.5s | <1.5s | >4s |

## Essential Shopify Marketing Stack

### Tier 1 — Must-Have
1. **Klaviyo** — Email + SMS marketing, flows, segmentation
2. **Meta Pixel + CAPI** — Facebook/Instagram ad tracking
3. **Google & YouTube channel** — Google Ads, Shopping, free listings
4. **Judge.me or Yotpo** — Product reviews and social proof
5. **GA4** — Web analytics (via GTM or Shopify Pixel API)

### Tier 2 — Growth Stage
6. **Triple Whale or Polar Analytics** — Attribution and analytics
7. **Smile.io** — Loyalty and rewards program
8. **ReConvert or AfterSell** — Post-purchase upsells
9. **Recharge** — Subscriptions (if applicable)
10. **Privy or Wisepops** — Pop-ups and lead capture

### Tier 3 — Scale Stage
11. **Northbeam** — Advanced multi-touch attribution
12. **Gorgias or Zendesk** — Customer support (impacts repeat rate)
13. **TikTok Pixel** — TikTok ad tracking
14. **Loop Returns** — Returns management
15. **Rebuy** — Personalized product recommendations

## Workflow: Full Shopify Audit

When asked to audit a Shopify store's marketing:

1. **Tracking & Analytics** — Pixel/CAPI setup, GA4 integration, UTM consistency, attribution tool
2. **Conversion Funnel** — Session → ATC → Checkout → Purchase rates, identify largest drop-off
3. **Site Speed** — Core Web Vitals, theme performance, app bloat, image optimization
4. **Product Pages** — Layout, imagery, copy, reviews, trust signals, urgency elements
5. **Collection Pages** — Navigation, filters, sorting, merchandising rules
6. **Cart & Checkout** — Cart experience, checkout completion rate, payment options, trust badges
7. **Email/SMS** — Platform integration, flow coverage, campaign frequency, revenue attribution
8. **Paid Media Integration** — Pixel health, CAPI event match quality, product feed quality
9. **SEO** — Title tags, meta descriptions, structured data, site architecture, blog content
10. **Customer Retention** — Loyalty program, subscription offering, post-purchase experience
11. **App Stack** — Review installed apps for redundancy, performance impact, cost
12. **Recommendations** — Prioritized by expected revenue impact and implementation effort

## Shopify-Specific Tracking Setup

### Meta Pixel + CAPI
- Use Shopify's Customer Events (Pixel API) — not the old theme-based pixel
- Enable CAPI through Facebook & Instagram channel app
- Verify Event Match Quality score in Meta Events Manager (target 8+)
- Track: PageView, ViewContent, AddToCart, InitiateCheckout, Purchase

### Google Ads + Enhanced Conversions
- Install Google & YouTube channel for Shopping + Performance Max
- Set up Enhanced Conversions in Google Ads
- Verify conversion tracking in Google Tag Assistant
- Feed optimization: product titles, descriptions, GTINs, custom labels

### GA4
- Recommended: Google Tag Manager via Shopify Pixel API (Custom Pixel)
- Alternative: Google & YouTube channel (simpler but less control)
- Key events: page_view, view_item, add_to_cart, begin_checkout, purchase
- Enhanced measurement: site search, scroll depth, outbound clicks

## How to Use This Skill

Ask me questions like:
- "Audit my Shopify store's conversion funnel"
- "What apps should I add to my Shopify marketing stack?"
- "Help me set up Meta CAPI on Shopify"
- "My add-to-cart rate is low — what should I optimize?"
- "Design a post-purchase upsell strategy"
- "How do I optimize my Google Shopping product feed?"
- "Review my Shopify checkout for conversion improvements"
- "Plan a loyalty program for my DTC brand"

For detailed Shopify API reference, Liquid theme customization, and advanced configurations, see [REFERENCE.md](REFERENCE.md).

## Analysis Examples

For complete analysis patterns, sample outputs, and use cases, see [EXAMPLES.md](EXAMPLES.md).

## Scripts

The skill includes utility scripts for API interaction and automated analysis:

### Fetch Store Data
```bash
# Get store info (API health check)
python scripts/shopify_client.py --resource shop

# List recent orders
python scripts/shopify_client.py --resource orders --days 30

# Export products as CSV
python scripts/shopify_client.py --resource products --status active --format csv --output products.csv

# Quick order count
python scripts/shopify_client.py --resource order-count --status any
```

### Run Analysis
```bash
# Full store audit (all analyses combined)
python scripts/analyze.py --analysis-type full-audit

# Conversion funnel (last 30 days)
python scripts/analyze.py --analysis-type conversion-funnel --days 30

# Product performance
python scripts/analyze.py --analysis-type product-performance --days 30

# Customer cohorts (last 90 days)
python scripts/analyze.py --analysis-type customer-cohorts --days 90

# Revenue analysis with output file
python scripts/analyze.py --analysis-type revenue-analysis --days 30 --output revenue.json
```

The scripts handle API authentication, rate limiting, pagination, and basic analysis. I'll interpret the results and provide actionable recommendations.

## Troubleshooting

**Authentication Error**: Verify that:
- `SHOPIFY_STORE_URL` is your `.myshopify.com` URL (not your custom domain)
- `SHOPIFY_ACCESS_TOKEN` starts with `shpat_` and is from a Custom App
- The app has the required API scopes (read_orders, read_products, read_customers)

**Rate Limiting**: The scripts handle Shopify's 2 requests/second limit automatically. If you see 429 errors, the retry logic will wait and continue. For large stores, consider using `--limit` to reduce data volume.

**No Orders Returned**: Check that:
- The date range (`--days`) covers a period with orders
- The `--status` filter matches your orders (use `any` to see all)
- The Admin API access token hasn't expired

**Import Errors**: Install required packages:
```bash
pip install -r requirements.txt
```

## Security & Privacy

- **Never hardcode** API credentials in code — use `.env` files
- Store access tokens **outside** version control
- Add `.env` and credential files to `.gitignore`
- The scripts are **read-only** — they do not create, modify, or delete any Shopify data
- Use Admin API scopes with minimum required access (read-only)
- Customer PII (emails, names) is processed locally and never stored persistently
- Rotate access tokens periodically
