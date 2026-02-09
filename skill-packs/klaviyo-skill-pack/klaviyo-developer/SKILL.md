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
| 2024-10-15 | Current stable. JSON:API format, new filtering. |
| 2024-07-15 | Catalog bulk operations, segment membership. |
| 2024-02-15 | Reporting API, campaign message content. |
| 2023-10-15 | Flows API, template cloning. |
| 2023-06-15 | Bulk profile import, campaign creation. |

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

For detailed API endpoint reference, code patterns, authentication, and architecture diagrams, see [REFERENCE.md](REFERENCE.md).

For marketing strategy, flow optimization, and campaign auditing, use the **klaviyo-analyst** skill.
