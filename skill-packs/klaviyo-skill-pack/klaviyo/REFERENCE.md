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
