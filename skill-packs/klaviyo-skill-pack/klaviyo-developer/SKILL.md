---
name: klaviyo-developer
description: Klaviyo API and developer integration expertise. Event tracking, SDKs, webhooks, rate limits, OAuth, catalog sync, and code patterns. Use when the user asks about Klaviyo API, integrating with Klaviyo, tracking events, building custom integrations, webhook handling, or developer implementation. For marketing strategy, flow optimization, and campaign auditing, see the klaviyo-analyst skill.
---

# Klaviyo Developer

Expert-level guidance for building with the Klaviyo API — custom event tracking, profile management, SDK integration, webhooks, catalog sync, and data pipeline architecture.

> For marketing strategy, flow auditing, segmentation, deliverability, and campaign optimization, see the **klaviyo-analyst** skill.

## Core Capabilities

### API Authentication & Versioning
- Private API key setup and key management best practices
- Public API key usage for client-side tracking (klaviyo.js)
- OAuth 2.0 authorization flow for third-party apps
- API revision headers and version lifecycle management

### Custom Event Tracking
- Server-side event tracking via Events API
- Client-side tracking with klaviyo.js
- Event schema design and property naming conventions
- Idempotent event submission patterns

### Profile Management
- Profile create, upsert, and bulk import patterns
- Custom property management and data types
- Subscription management (email, SMS consent)
- Profile merge and deduplication strategies

### Webhooks
- Webhook subscription setup and event types
- Payload verification and signature validation
- Retry handling and idempotent webhook processing

### SDK Usage & Libraries
- Python SDK (klaviyo-api)
- Node.js SDK (klaviyo-api-node)
- Ruby, PHP, and other community SDKs
- SDK initialization, error handling, and retry configuration

### Catalog & Product Feed Sync
- Catalog item create/update/delete via API
- Category and variant management
- Product feed sync architecture for recommendations
- Handling large catalogs with bulk operations

### Data Export & Warehouse Sync
- Metric aggregation API for reporting
- Profile and event export patterns
- Cursor-based pagination for large datasets
- ETL pipeline design for data warehouse integration

## SDK Quick Reference

| Language | Package | Install |
|----------|---------|---------|
| Python | `klaviyo-api` | `pip install klaviyo-api` |
| Node.js | `klaviyo-api` | `npm install klaviyo-api` |
| Ruby | `klaviyo-api-sdk` | `gem install klaviyo-api-sdk` |
| PHP | `klaviyo/api` | `composer require klaviyo/api` |

## Rate Limits

| Endpoint Category | Limit | Window |
|-------------------|-------|--------|
| Most endpoints | 75 requests | per second |
| Bulk imports | 10 requests | per second |
| Profile/Event create | 350 requests | per second |
| Campaign send | 10 requests | per second |

Headers returned: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`

## API Revision Timeline

| Revision | Key Changes |
|----------|-------------|
| 2026-01-15 | Latest. Custom Objects Ingestion, Geofencing API (beta). |
| 2025-10-15 | Forms API, Flow Actions API, SMS ROI reporting. |
| 2025-07-15 | Mapped Metrics API, Custom Objects API (GA). |
| 2025-04-15 | Web Feeds API, Custom Metrics, Push Token registration. |
| 2025-01-15 | Reviews APIs, Flows Create API, Campaign image management. |
| 2024-10-15 | Universal Content API, Form/Segment Reporting, Reviews API. |
| 2024-07-15 | Forms API (retrieval), Webhooks API. |
| 2024-02-15 | Reporting API, Create or Update Profile (upsert). |

Always include the `revision` header in API requests.

## Essential Developer Checklist

1. **API key management** — Store private keys in environment variables, never commit to source. Rotate keys periodically.
2. **Revision header** — Always include `revision: YYYY-MM-DD` header. Pin to a specific version.
3. **Rate limit handling** — Implement exponential backoff with jitter on 429 responses.
4. **Idempotent events** — Include a unique `unique_id` property to prevent duplicate event tracking.
5. **Profile upserts** — Use `POST /profiles/` with existing identifier for upsert behavior (creates or updates).
6. **Webhook verification** — Validate webhook signatures before processing payloads.
7. **Pagination** — Use cursor-based pagination for list endpoints. Never assume result counts.
8. **Error handling** — Parse JSON:API error responses. Handle 4xx (client) and 5xx (server) differently.
9. **SDK initialization** — Configure SDK with API key at app startup, not per-request.
10. **Testing** — Use Klaviyo test/sandbox accounts. Mock API responses in unit tests.

## Workflow: Custom Integration Setup

When building a custom Klaviyo integration:

1. **Define requirements** — What events to track, what profile data to sync, what triggers are needed
2. **API key provisioning** — Create a private API key with minimum required scopes
3. **Event schema design** — Map business events to Klaviyo metric names and properties
4. **Profile sync strategy** — Determine identifier (email vs phone vs external_id), upsert frequency
5. **Implement tracking** — Server-side event tracking with proper error handling and retries
6. **Catalog sync** (if applicable) — Product feed sync for recommendations and browse abandonment
7. **Webhook setup** — Subscribe to relevant events, implement handler with signature verification
8. **Rate limit strategy** — Queue and throttle API calls, implement backoff
9. **Monitoring** — Log API errors, track event delivery rates, alert on failures
10. **Testing & validation** — Verify events appear in Klaviyo, test flow triggers, validate profile data

## Workflow: Integration Health Audit

When auditing an existing Klaviyo integration for health and data quality:

1. **Inventory active integrations** — List all configured integrations (built-in and custom). Identify active vs stale connections.
2. **Map event sources** — For each metric in the account, identify its source (built-in integration, custom API, Klaviyo-internal, form). Flag metrics with zero recent volume.
3. **Audit event schemas** — Pull property structures for key events (Placed Order, Started Checkout, Viewed Product, Added to Cart). Check for:
   - Missing standard properties (e.g., `$value`, `ItemNames`, line items)
   - Duplicate/redundant metrics (e.g., "Placed Order" and "Order Placed" from different sources)
   - Inconsistent property naming (camelCase vs snake_case across events)
4. **Check profile data pipeline** — Verify profile properties are being synced correctly. Look for:
   - Properties set by API vs properties set by events
   - Stale properties (set once, never updated)
   - Properties used in segmentation vs properties sitting unused
5. **Review catalog sync** — Verify product catalog is synced and fresh. Check:
   - Total catalog items vs expected product count
   - Last sync timestamp
   - Variant coverage (are variants synced or just parent products?)
   - Category structure completeness
6. **Assess flow trigger architecture** — Map how flows are triggered:
   - Direct metric triggers (robust) vs segment-entry triggers via API-synced properties (brittle)
   - Single points of failure (if API sync breaks, do all flows stop?)
   - Trigger redundancy and fallback patterns
7. **Identify data accessibility gaps** — Check for data that exists in event payloads but isn't usable:
   - Nested objects in event properties (can use in templates, cannot use in segments/splits)
   - Properties available in events but not synced to profiles (can't segment on them)
   - Events tracked but not used in any flow or segment
8. **Produce integration health report** — Document findings with severity ratings:
   - **Critical**: Integration failures, broken event tracking, data loss
   - **High**: Missing standard events, duplicate metrics, flow trigger fragility
   - **Medium**: Unused events, incomplete catalog, stale profile properties
   - **Low**: Naming inconsistencies, optimization opportunities

## Event Schema Best Practices

### Property Naming Conventions
- Use **PascalCase** for standard Klaviyo properties: `ProductName`, `ItemPrice`, `OrderId`
- Use **snake_case** for custom properties: `business_type`, `account_id`, `reorder_count`
- Never mix conventions within a single event — pick one and be consistent
- Prefix custom properties to avoid collision with Klaviyo-reserved names

### Required Properties by Event

| Event | Required Properties | Revenue Property |
|-------|-------------------|------------------|
| Placed Order | `$value`, `OrderId`, `Items[]` (line items) | `$value` |
| Started Checkout | `$value`, `CheckoutURL`, `Items[]` | `$value` |
| Viewed Product | `ProductName`, `ProductID`, `URL`, `ImageURL` | — |
| Added to Cart | `$value`, `AddedItemProductName`, `AddedItemProductID`, `Items[]` | `$value` |
| Fulfilled Order | `$value`, `OrderId` | — |

### Nesting Rules and Limitations

Klaviyo handles nested objects differently depending on where you access them:

| Context | Access Level | Example |
|---------|-------------|---------|
| **Email/SMS templates** | Full access via Jinja — can loop over arrays, access nested properties | `{% for item in event.Items %}{{ item.ProductName }}{% endfor %}` |
| **Flow conditional splits** | Top-level properties ONLY — cannot access nested object fields | Can split on `event.OrderId`, cannot split on `event.Items[0].ProductName` |
| **Segments** | Top-level properties ONLY — cannot filter by nested object fields | Can segment on "has done Placed Order where $value > 100", cannot segment on "where Items contains ProductName = X" |
| **Flow triggers** | Top-level properties for trigger filters | Same as conditional splits |

**Workaround for nested data**: If you need to segment or split on nested data, flatten it to top-level properties:
```python
# Instead of relying on Items[] array for segmentation:
properties = {
    "$value": 149.99,
    "OrderId": "ORD-123",
    "Items": [{"ProductName": "Wireless Headphones", "Category": "Electronics"}],
    # Flatten for segmentation:
    "ItemCategories": "Electronics,Accessories",  # Comma-joined for "contains" filter
    "HasElectronics": True,                        # Boolean flag for split
    "TopItemCategory": "Electronics"               # Top category for split
}
```

### Custom Event Patterns (DTC / Subscription / Marketplace)

Additional events beyond the standard Shopify/e-commerce schema:

| Event Name | Trigger | Key Properties |
|------------|---------|----------------|
| `Account Created` | New account registered | `account_type`, `referral_source`, `signup_channel` |
| `Subscription Started` | Recurring order activated | `$value`, `frequency`, `product_ids`, `plan_name` |
| `Subscription Cancelled` | Recurring order stopped | `reason`, `plan_name`, `lifetime_charges` |
| `Reorder Placed` | Repeat purchase of consumable | `$value`, `OrderId`, `days_since_last_order`, `reorder_items` |
| `Wishlist Added` | Item saved for later | `ProductName`, `ProductID`, `Categories`, `Price` |
| `Catalog Browsed` | Category/search activity | `category`, `search_term`, `results_count` |

Sync key customer properties to profiles for segmentation:
```python
profile_properties = {
    "customer_type": "Subscriber",
    "interests": ["Skincare", "Wellness"],
    "subscription_plan": "Monthly Box",
    "account_tier": "VIP",
    "first_order_date": "2024-03-15",
    "lifetime_order_count": 8,
    "avg_order_value": 72.50,
    "preferred_categories": ["Skincare", "Supplements"]
}
```

## Data Accessibility Diagnosis

When data exists in Klaviyo but isn't usable where expected:

### Symptoms
- "We track [event] but can't segment on [property]"
- "Flow split doesn't see the property we're sending"
- "Profile has the data but segment doesn't pick it up"

### Root Causes and Solutions

| Symptom | Root Cause | Solution |
|---------|-----------|----------|
| Can't segment on event property | Property is nested inside an array/object | Flatten to top-level property on the event |
| Can't split flow on event property | Property is nested | Flatten, or use profile property instead |
| Segment doesn't match profiles | Property is on events, not profiles | Sync property to profile via API or "Update Profile Property" flow action |
| Profile property exists but segment empty | Property value format mismatch (string "true" vs boolean `true`) | Standardize data types in API sync |
| Event tracked but no flow triggers | Metric name mismatch (case-sensitive) | Verify exact metric name in Klaviyo matches API call |
| Flow triggers but filter excludes everyone | Segment used as flow filter evaluates incorrectly | Check segment conditions — may reference stale or incorrectly-typed properties |

### Diagnosis Workflow
1. **Check metric exists**: Use GET `/metrics/` to verify the event name appears
2. **Check event properties**: Use GET `/events/?filter=...` to pull recent events and inspect property structure
3. **Check profile properties**: Use GET `/profiles/{id}/` to verify expected properties are on the profile
4. **Test segment conditions**: Compare segment definition against actual profile data — look for type mismatches, case sensitivity issues
5. **Test flow trigger**: Send a test event and trace whether the flow fires, where it stops, and why

## How to Use This Skill

Ask me questions like:
- "How do I track a custom event from my Node.js backend?"
- "Help me set up a bulk profile import script"
- "What are Klaviyo's rate limits and how should I handle them?"
- "How do I verify Klaviyo webhook signatures?"
- "Set up catalog sync for my custom e-commerce platform"
- "How do I implement OAuth for a Klaviyo app?"
- "Design a data pipeline to export Klaviyo data to BigQuery"
- "Help me migrate from Klaviyo v1/v2 API to the current API"
- "Audit my integration — are events structured correctly?"
- "Why can't I segment on a property I'm tracking in events?"

## Integration Examples

For complete integration patterns, worked examples with sample output, and code snippets, see [EXAMPLES.md](EXAMPLES.md).

## Scripts

The skill includes utility scripts for API interaction and integration management:

### Developer Client
```bash
# Track a custom event
python scripts/klaviyo_client.py --action track-event \
    --email user@example.com --event "Placed Order" \
    --properties '{"value": 99.99, "OrderId": "ORD-123"}'

# Upsert a profile
python scripts/klaviyo_client.py --action upsert-profile \
    --email user@example.com \
    --properties '{"first_name": "Jane", "loyalty_tier": "Gold"}'

# List catalog items
python scripts/klaviyo_client.py --action catalog-items --format table

# Export profiles to CSV
python scripts/klaviyo_client.py --action export-profiles \
    --max-pages 10 --format csv --output profiles.csv
```

### Developer Tools
```bash
# Integration health check
python scripts/dev_tools.py --tool health-check

# Validate event tracking
python scripts/dev_tools.py --tool validate-events \
    --events "Placed Order,Started Checkout,Viewed Product"

# Test webhook endpoint
python scripts/dev_tools.py --tool test-webhook \
    --webhook-url https://example.com/webhooks/klaviyo

# Import profiles from CSV
python scripts/dev_tools.py --tool import-csv \
    --file contacts.csv --list-id LIST_ID

# Export data with pagination
python scripts/dev_tools.py --tool export-data \
    --resource profiles --max-records 5000 --output profiles.csv
```

The scripts handle API authentication, rate limiting, and JSON:API formatting. I'll help interpret results and provide implementation guidance.

## Troubleshooting

**Authentication Error**: Verify that:
- `KLAVIYO_API_KEY` is set as an environment variable or in a `.env` file
- The key starts with `pk_` (private API key, not public)
- The key has the required scopes for your operation (e.g., `events:write` for tracking, `profiles:write` for imports)

**Rate Limit Errors (429)**: The SDK handles retries automatically (up to 3 retries with 60s max delay). If you still hit limits:
- Queue and throttle bulk operations (max 10 req/s for imports)
- Check `RateLimit-Remaining` header proactively
- Implement exponential backoff with jitter for raw HTTP

**Bulk Import Errors**: Check that:
- Batch size does not exceed 10,000 profiles per job
- Email or phone is provided for each profile (at least one identifier)
- CSV column names match expected field names

**Import Errors**: Install required packages:
```bash
pip install klaviyo-api python-dotenv pandas
```

## Security Notes

- **Never hardcode** API keys in code or commit them to version control
- Store keys in environment variables or `.env` files
- Add `.env` to `.gitignore`
- Use **minimum required scopes** — only enable write access where needed
- Rotate API keys periodically in Klaviyo Settings
- For OAuth integrations, store client secrets securely and refresh tokens before expiry

## Data Privacy

This skill interacts with the Klaviyo API for integration development. When using write operations:
- Validate data before sending to avoid corrupting profile records
- Never log or store API keys, webhook secrets, or PII in plain text
- Use idempotency keys to prevent duplicate events
- Implement webhook signature verification to prevent spoofing
- Follow GDPR/CCPA requirements when handling profile data
- Use the Data Privacy Deletion endpoint for right-to-erasure requests

All operations are performed via the official Klaviyo API with proper authentication.

For detailed API endpoint reference, code patterns, authentication, and architecture diagrams, see [REFERENCE.md](REFERENCE.md).

For marketing strategy, flow optimization, and campaign auditing, use the **klaviyo-analyst** skill.
