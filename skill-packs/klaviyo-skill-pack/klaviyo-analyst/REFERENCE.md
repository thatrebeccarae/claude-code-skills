# Klaviyo Reference

## Data Model

### Profiles (Contacts)
- **Email** — Primary identifier
- **Phone Number** — For SMS, must include country code
- **Properties** — Custom profile fields (first name, city, loyalty tier, etc.)
- **Predictive Analytics** — CLV, churn risk, gender, next order date (auto-calculated by Klaviyo)
- **Consent** — Email subscription status, SMS consent, double opt-in status

### Events (Metrics)
Standard e-commerce events synced from integration:
- `Placed Order` — Order completed with line items, total, discount
- `Ordered Product` — Individual product from an order
- `Started Checkout` — Checkout initiated
- `Added to Cart` — Item added to cart
- `Viewed Product` — Product detail page viewed
- `Active on Site` — Web activity tracked
- `Received Email`, `Opened Email`, `Clicked Email` — Engagement events
- `Received SMS`, `Clicked SMS` — SMS engagement

### Lists vs Segments
- **Lists** — Static groups (opt-in forms, imports). Used for sending campaigns.
- **Segments** — Dynamic, condition-based. Auto-update as profiles match/unmatch criteria.
- Best practice: Use segments for targeting, lists for opt-in tracking.

## Flow Builder Reference

### Trigger Types
| Trigger | Description | Common Use |
|---------|-------------|------------|
| List | Profile added to a list | Welcome series |
| Segment | Profile enters a segment | VIP, winback |
| Metric | Event occurs | Abandoned cart, post-purchase |
| Date | Based on date property | Birthday, anniversary |
| Price Drop | Product price decreases | Price drop alerts |
| Back in Stock | Product becomes available | Restock notifications |

### Flow Actions
- **Email** — Send email with template
- **SMS** — Send SMS/MMS
- **Push Notification** — Mobile push
- **Webhook** — HTTP POST to external service
- **Update Profile Property** — Set/modify a profile field
- **Conditional Split** — IF/ELSE based on conditions
- **Trigger Split** — Branch based on event properties
- **A/B Split** — Random percentage split for testing

### Flow Filters
Applied at the flow level (not individual messages):
- Profile properties (e.g., has placed order = true)
- Segment membership (e.g., is in VIP segment)
- List membership
- Consent status
- Custom properties

### Time Delays
- **Time Delay** — Fixed wait (hours, days)
- **Smart Send Time** — Optimized per recipient
- **Wait until specific day/time** — e.g., next Tuesday at 10am

## Segmentation Conditions

### Behavioral
- Has/has not done [event] in [time period]
- [Event] count >/</= [number] in [time period]
- [Event] property matches [value]

### Profile
- Profile property is/is not/contains [value]
- Is in / not in [list]
- Is in / not in [segment]
- Consent status (subscribed, unsubscribed, never subscribed)

### Predictive (Klaviyo AI)
- Predicted CLV is above/below [value]
- Predicted churn risk is high/medium/low
- Predicted gender is male/female
- Predicted next order date is within [days]

### Engagement
- Has/has not opened email in [days]
- Has/has not clicked email in [days]
- Has/has not opened SMS in [days]

## API Reference (v2)

### Base URL
```
https://a.klaviyo.com/api/
```

### Authentication
```
Authorization: Klaviyo-API-Key {private-api-key}
```

### Key Endpoints

#### Profiles
```
GET    /profiles/                    # List profiles
POST   /profiles/                    # Create profile
GET    /profiles/{id}/               # Get profile
PATCH  /profiles/{id}/               # Update profile
POST   /profile-subscription-bulk-create-jobs/  # Subscribe profiles
```

#### Events (Metrics)
```
POST   /events/                      # Create event
GET    /events/                      # Query events
GET    /metrics/                     # List available metrics
POST   /metric-aggregates/           # Aggregate metric data
```

#### Lists & Segments
```
GET    /lists/                       # List all lists
POST   /lists/                       # Create list
GET    /segments/                    # List all segments
GET    /segments/{id}/profiles/      # Get segment members
```

#### Campaigns
```
GET    /campaigns/                   # List campaigns
POST   /campaigns/                   # Create campaign
POST   /campaign-send-jobs/          # Send campaign
```

#### Flows
```
GET    /flows/                       # List flows
GET    /flows/{id}/                  # Get flow details
PATCH  /flows/{id}/                  # Update flow status
```

#### Catalogs
```
POST   /catalog-items/              # Create catalog item
GET    /catalog-items/              # List catalog items
PATCH  /catalog-items/{id}/         # Update catalog item
```

### Webhooks
Klaviyo can send webhooks for:
- Profile subscribed/unsubscribed
- Email bounced/marked spam
- SMS consent changes
- Custom event triggers via flows

## Email Deliverability Reference

### Authentication Records
```
# SPF (add to your DNS)
v=spf1 include:_spf.klaviyo.com ~all

# DKIM (Klaviyo provides the records)
# Add CNAME records provided in Klaviyo Settings > Email > Domains

# DMARC (recommended)
v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com
```

### Sending Domain Setup
1. Add your domain in Klaviyo Settings > Email > Domains
2. Add the 3 CNAME records (2 DKIM + 1 Return-Path) to your DNS
3. Verify in Klaviyo (can take up to 48 hours)
4. Dedicated sending domain recommended for high-volume senders

### IP Warming Schedule (Dedicated IP)
| Day | Daily Volume |
|-----|-------------|
| 1-2 | 500 |
| 3-4 | 1,000 |
| 5-6 | 2,500 |
| 7-8 | 5,000 |
| 9-10 | 10,000 |
| 11-14 | 25,000 |
| 15-21 | 50,000 |
| 22-28 | 100,000 |
| 29+ | Full volume |

During warm-up: Send only to most engaged contacts. Monitor bounce rates and spam complaints daily.

## SMS Reference

### Compliance Requirements
- **TCPA** — Express written consent required before sending
- **Quiet Hours** — Default: No SMS 9pm-9am recipient's local time
- **Opt-out** — Must honor STOP/UNSUBSCRIBE immediately
- **Identification** — Business name must be in first message
- **Frequency disclosure** — "Msg frequency varies. Msg & data rates may apply."
- **Short Code vs Toll-Free** — Short codes for high-volume, toll-free for smaller senders

### SMS Character Limits
- Standard SMS: 160 characters (GSM-7 encoding)
- With special characters/emoji: 70 characters (UCS-2 encoding)
- MMS: Up to 1600 characters + media (image/GIF)
- Klaviyo recommendation: Keep under 160 chars, include clear CTA and opt-out

## Integration Setup

### Shopify
- Install Klaviyo app from Shopify App Store
- Auto-syncs: customers, orders, products, carts
- Events synced: Placed Order, Started Checkout, Added to Cart, Viewed Product
- Catalog synced for dynamic product recommendations
- Discount codes auto-generated for flows

### WooCommerce
- Install Klaviyo plugin
- Syncs orders, customers, cart events
- Requires WooCommerce webhook configuration

### Custom (API)
```python
import requests

# Track an event
requests.post(
    "https://a.klaviyo.com/api/events/",
    headers={
        "Authorization": "Klaviyo-API-Key {YOUR_KEY}",
        "Content-Type": "application/json",
        "revision": "2024-10-15"
    },
    json={
        "data": {
            "type": "event",
            "attributes": {
                "metric": {"data": {"type": "metric", "attributes": {"name": "Placed Order"}}},
                "profile": {"data": {"type": "profile", "attributes": {"email": "customer@example.com"}}},
                "properties": {"OrderId": "12345", "value": 99.99}
            }
        }
    }
)
```

## Reporting Metrics Glossary

| Metric | Definition |
|--------|-----------|
| Revenue per Recipient (RPR) | Total attributed revenue / recipients |
| Attributed Revenue | Revenue within attribution window (default: 5-day email click, 24-hour SMS click) |
| Deliverability Rate | (Sent - Bounced) / Sent |
| Unique Open Rate | Unique opens / delivered (affected by Apple MPP) |
| Unique Click Rate | Unique clicks / delivered |
| Click-to-Open Rate (CTOR) | Unique clicks / unique opens |
| Unsubscribe Rate | Unsubscribes / delivered |
| Spam Complaint Rate | Spam complaints / delivered |
| Bounce Rate | (Hard + Soft bounces) / Sent |
| List Growth Rate | (New subscribers - Unsubscribes) / Total list size |

---

## Standard E-Commerce Event Property Schemas

Reference schemas for the standard e-commerce events. Use when auditing event tracking or verifying integration completeness.

### Placed Order
```json
{
  "$value": 149.99,
  "OrderId": "ORD-12345",
  "Categories": ["Hand Tools", "Safety"],
  "ItemNames": ["Torque Wrench 3/8in", "Safety Goggles (Pack/12)"],
  "Brands": ["Stanley", "3M"],
  "DiscountCode": "WELCOME10",
  "DiscountValue": 15.00,
  "Items": [
    {
      "ProductID": "PROD-001",
      "SKU": "STN-TW-38",
      "ProductName": "Torque Wrench 3/8in",
      "Quantity": 2,
      "ItemPrice": 24.99,
      "RowTotal": 49.98,
      "ProductURL": "https://...",
      "ImageURL": "https://...",
      "Categories": ["Hand Tools"],
      "Brand": "Stanley"
    }
  ],
  "ItemCount": 3,
  "ShippingCost": 0.00,
  "Tax": 12.00
}
```
**Critical**: `$value` = revenue property for attribution. `Categories` (top-level) needed for segmentation since `Items[].Categories` is nested and not accessible in segments.

### Started Checkout
```json
{
  "$value": 149.99,
  "CheckoutURL": "https://example.com/checkout/abc123",
  "ItemNames": ["Torque Wrench 3/8in", "Safety Goggles (Pack/12)"],
  "Items": [{ "ProductID": "...", "ProductName": "...", "Quantity": 1, "ItemPrice": 24.99, "ImageURL": "..." }],
  "ItemCount": 3
}
```
**Critical**: `CheckoutURL` required for abandoned cart email CTAs. `$value` enables cart value filters.

### Viewed Product
```json
{
  "ProductName": "Torque Wrench 3/8in",
  "ProductID": "PROD-001",
  "Categories": ["Hand Tools", "Automotive"],
  "Brand": "Stanley",
  "Price": 24.99,
  "CompareAtPrice": 29.99,
  "ImageURL": "https://...",
  "URL": "https://..."
}
```
**Critical**: No `$value` (not a revenue event). `URL` and `ImageURL` required for browse abandonment personalization. `Categories` at top level enables segment filters.

### Added to Cart
```json
{
  "$value": 24.99,
  "AddedItemProductName": "Torque Wrench 3/8in",
  "AddedItemProductID": "PROD-001",
  "AddedItemPrice": 24.99,
  "AddedItemQuantity": 2,
  "ItemNames": ["Torque Wrench 3/8in", "Safety Goggles (Pack/12)"],
  "Items": [{ "ProductID": "...", "ProductName": "...", "Quantity": 1, "ItemPrice": 24.99 }]
}
```
**Critical**: `$value` = added item price (not total cart). `AddedItem*` properties are top-level and segmentable. `Items[]` = full cart for template rendering.

---

## Flow Configuration Best Practices

### Smart Send Settings

| Setting | When to Enable | When to Disable |
|---------|---------------|-----------------|
| Smart Sending ON (16h window) | Promotional flows (browse abandonment, winback) | Time-sensitive flows (abandoned cart, transactional) |
| Smart Sending OFF | Abandoned cart, order confirmation, shipping | Never for promotional flows |
| Skip recently emailed ON | Browse abandonment, cross-sell | Welcome series (first impression), abandoned cart |

### Timing Benchmarks

| Flow | Email 1 | Email 2 | Email 3 | Email 4+ |
|------|---------|---------|---------|----------|
| Welcome Series | Immediate | 1 day | 3 days | 5-7 days |
| Abandoned Cart | 1 hour | 24 hours | 48-72 hours | — |
| Browse Abandonment | 2-4 hours | 24 hours | — | — |
| Post-Purchase | Immediate (confirmation) | 3 days (cross-sell) | 7 days (review) | 14+ days (replenish) |
| Winback | 60 days post-purchase | 75 days | 90 days (last chance) | — |
| Sunset | 90 days unengaged | 104 days | Suppress at 120 days | — |

### Exclusion Filter Patterns

| Flow | Must Exclude | Why |
|------|-------------|-----|
| Welcome | Existing customers (Placed Order ever) | Different messaging for buyers vs browsers |
| Abandoned Cart | Placed Order in last 4 hours | They already bought |
| Browse Abandonment | Started Checkout in last 1 hour, Placed Order in last 24 hours | Higher-intent flow takes priority |
| Winback | Placed Order in last 60 days | They're still active |
| Sunset | Placed Order in last 90 days | Buyers get different treatment |

---

## A/B Testing Framework

### Univariate Testing Rules
1. **Test ONE variable at a time** — Subject line OR send time OR content, never multiple
2. **Define the KPI before launching** — Open rate for subject lines, click rate for content, RPR for offers
3. **Run to statistical significance** — Minimum 95% confidence (p < 0.05)
4. **Equal random split** — 50/50 for flows, 10/10/80 for campaigns (test on 20%, send winner to 80%)

### Minimum Sample Sizes

| Baseline Rate | Detectable Lift | Min Sample (per variant) |
|--------------|-----------------|-------------------------|
| 20% open rate | 10% relative (to 22%) | 7,500 |
| 20% open rate | 20% relative (to 24%) | 2,000 |
| 3% click rate | 20% relative (to 3.6%) | 12,000 |
| 3% click rate | 30% relative (to 3.9%) | 5,500 |
| 1% conversion | 30% relative (to 1.3%) | 18,000 |

### Sequential Test Plan Template

```
Test 1 (Week 1-2): Subject Line
  Variable: Urgency vs Benefit-led
  KPI: Open rate
  Duration: 7 days or 5,000 recipients per variant
  Winner → Becomes default

Test 2 (Week 3-4): CTA Placement
  Variable: Above-fold button vs Below-content button
  KPI: Click rate
  Duration: 7 days or 5,000 recipients per variant
  Winner → Becomes default

Test 3 (Week 5-6): Offer Type
  Variable: % discount vs $ discount vs free shipping
  KPI: Revenue per recipient
  Duration: 14 days or 3,000 recipients per variant
  Winner → Becomes default
```

---

## Segment Architecture Patterns

### Mutually Exclusive Engagement Tiers

Build engagement tiers that don't overlap — each profile falls into exactly one tier:

| Tier | Condition | Sending Strategy |
|------|-----------|-----------------|
| **Active** (0-30d) | Opened OR clicked email in last 30 days | Full frequency (3-5x/week) |
| **Warm** (31-90d) | NOT Active AND (opened OR clicked in last 90 days) | Moderate (2x/week) |
| **At-Risk** (91-180d) | NOT Active AND NOT Warm AND (opened OR clicked in last 180 days) | Reduced (1x/week), re-engagement content |
| **Lapsed** (180d+) | NOT Active AND NOT Warm AND NOT At-Risk AND has received email | Sunset flow only, then suppress |
| **Never Engaged** | Has received email AND has never opened or clicked | Suppress immediately |

### RFM Segment Definitions

| Segment | Recency | Frequency | Monetary | Action |
|---------|---------|-----------|----------|--------|
| **Champions** | Ordered L30d | 4+ orders L12M | Top 20% AOV | VIP treatment, early access |
| **Loyal** | Ordered L60d | 3+ orders L12M | Above avg AOV | Reward programs, referral asks |
| **Promising** | Ordered L90d | 1-2 orders L12M | Any | Nurture to loyalty, product education |
| **At Risk** | No order L90d | 2+ orders ever | Above avg lifetime | Winback flow, incentives |
| **Lost** | No order L180d | Any | Any | Last-chance offer, then sunset |

### Predictive Segment Setup (Klaviyo AI)

| Segment | Condition | Use |
|---------|-----------|-----|
| High CLV | Predicted CLV > 75th percentile | VIP flow trigger, premium offers |
| Churn Risk - High | Predicted churn risk = High | Immediate re-engagement, incentive |
| Churn Risk - Medium | Predicted churn risk = Medium | Nurture content, value reminders |
| Next Order < 14 days | Predicted next order date within 14 days | Replenishment reminder timing |
| Gender - Female | Predicted gender = Female | Content personalization (if relevant) |

---

## SOW / PRD Template Structure

When producing implementation specs (SOWs) for audit recommendations:

```markdown
# [Title]

## Summary
- **Priority**: P1/P2/P3/P4
- **Estimated Impact**: $X-$Y/year or % improvement
- **Complexity**: Low/Medium/High
- **Timeline**: X days/weeks
- **Owner**: Client / Agency / Shared

## Problem Statement
[What's wrong, with evidence from audit data]

## Recommendation (Client-Facing)
[What to do and why, in plain language]

## Implementation Spec (Internal)

### Prerequisites
[What must be done first]

### Step-by-Step Build
[Detailed Klaviyo UI steps OR API/code steps]

### Trigger & Filter Configuration
[Exact trigger type, filter conditions, segment criteria]

### Content Brief
[Subject lines, email structure, CTA copy, dynamic content blocks]

### Timing & Logic
[Delays, conditional splits, Smart Send settings]

### Testing Plan
[A/B test variables, sample size, success criteria, stat sig threshold]

### Success Metrics
[KPIs to track, measurement period, benchmarks]

## Dependencies
[What other SOWs must complete first]
```
