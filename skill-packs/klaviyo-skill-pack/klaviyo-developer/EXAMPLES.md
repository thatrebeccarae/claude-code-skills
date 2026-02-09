# Klaviyo Developer Examples

Practical examples of common Klaviyo integration tasks and developer patterns.

## Example 1: Track Custom E-commerce Events

**User Request**: "How do I track a custom 'Placed Order' event from my backend?"

**Analysis Steps**:
1. Design the event payload with required fields
2. Include idempotency key to prevent duplicates
3. Show both SDK and raw HTTP approaches
4. Provide multi-language examples

**Script Command**:
```bash
python scripts/klaviyo_client.py --action track-event \
    --email customer@example.com \
    --event "Placed Order" \
    --properties '{"OrderId": "ORD-12345", "value": 149.99, "ItemNames": ["Widget A", "Gadget B"], "ItemCount": 2}'
```

**Sample Output**:
```json
{
  "status": "success",
  "event": "Placed Order",
  "email": "customer@example.com"
}
```

**Python SDK Example**:
```python
from klaviyo_api import KlaviyoAPI

klaviyo = KlaviyoAPI("pk_abc123...", max_delay=60, max_retries=3)

body = {
    "data": {
        "type": "event",
        "attributes": {
            "metric": {
                "data": {"type": "metric", "attributes": {"name": "Placed Order"}}
            },
            "profile": {
                "data": {"type": "profile", "attributes": {"email": "customer@example.com"}}
            },
            "properties": {
                "OrderId": "ORD-12345",
                "value": 149.99,
                "ItemNames": ["Widget A", "Gadget B"],
                "ItemCount": 2,
                "Items": [
                    {"ProductID": "PROD-001", "ProductName": "Widget A", "Quantity": 1, "ItemPrice": 79.99},
                    {"ProductID": "PROD-002", "ProductName": "Gadget B", "Quantity": 1, "ItemPrice": 70.00}
                ]
            },
            "unique_id": "ORD-12345"  # Idempotency key
        }
    }
}

klaviyo.Events.create_event(body)
```

**Node.js Example**:
```javascript
const { ApiClient, EventsApi } = require('klaviyo-api');

const defaultClient = ApiClient.instance;
defaultClient.authentications['ApiKeyAuth'].apiKey = 'pk_abc123...';

const eventsApi = new EventsApi();
await eventsApi.createEvent({
  data: {
    type: 'event',
    attributes: {
      metric: { data: { type: 'metric', attributes: { name: 'Placed Order' } } },
      profile: { data: { type: 'profile', attributes: { email: 'customer@example.com' } } },
      properties: {
        OrderId: 'ORD-12345',
        value: 149.99,
        ItemNames: ['Widget A', 'Gadget B'],
        ItemCount: 2
      },
      unique_id: 'ORD-12345'
    }
  }
});
```

**Key Points**:
- Always include `unique_id` for idempotent event submission
- The `value` property is used by Klaviyo for revenue attribution
- `Items` array enables product-level reporting in flows
- Profile is auto-created if it doesn't exist

## Example 2: Bulk Profile Import

**User Request**: "I need to import 50,000 contacts from a CSV into Klaviyo"

**Analysis Steps**:
1. Read CSV file and validate structure
2. Batch into 10,000-profile chunks (API limit)
3. Submit each batch as a bulk import job
4. Track job status for completion

**Script Command**:
```bash
python scripts/dev_tools.py --tool import-csv \
    --file contacts.csv \
    --list-id YOUR_LIST_ID
```

**Sample CSV** (`contacts.csv`):
```csv
email,first_name,last_name,phone,loyalty_tier,source
jane@example.com,Jane,Doe,+15551234567,Gold,migration
john@example.com,John,Smith,+15559876543,Silver,migration
```

**Sample Output**:
```
Batch 1/5: importing 10000 profiles...
Batch 2/5: importing 10000 profiles...
Batch 3/5: importing 10000 profiles...
Batch 4/5: importing 10000 profiles...
Batch 5/5: importing 10000 profiles...

{
  "file": "contacts.csv",
  "total_profiles": 50000,
  "summary": {
    "batches_submitted": 5,
    "batches_failed": 0,
    "profiles_submitted": 50000
  },
  "batches": [
    {"batch": 1, "profiles": 10000, "status": "submitted", "job_id": "JOB-001"},
    {"batch": 2, "profiles": 10000, "status": "submitted", "job_id": "JOB-002"},
    {"batch": 3, "profiles": 10000, "status": "submitted", "job_id": "JOB-003"},
    {"batch": 4, "profiles": 10000, "status": "submitted", "job_id": "JOB-004"},
    {"batch": 5, "profiles": 10000, "status": "submitted", "job_id": "JOB-005"}
  ]
}
```

**Check Job Status**:
```bash
python scripts/klaviyo_client.py --action import-status --job-id JOB-001
```

**Key Points**:
- Maximum 10,000 profiles per bulk import job
- Jobs are async — use `import-status` to check completion
- Include `--list-id` to add profiles to a list during import
- Custom properties in CSV columns are automatically mapped

## Example 3: Webhook Handler Setup

**User Request**: "How do I set up a webhook to handle Klaviyo events?"

**Analysis Steps**:
1. Test webhook endpoint connectivity
2. Verify signature validation works
3. Provide handler code example
4. Cover retry and idempotency patterns

**Script Command**:
```bash
# Test webhook endpoint
python scripts/dev_tools.py --tool test-webhook \
    --webhook-url https://example.com/webhooks/klaviyo

# Test with signature verification
python scripts/dev_tools.py --tool test-webhook \
    --webhook-url https://example.com/webhooks/klaviyo \
    --webhook-secret your-webhook-secret
```

**Sample Output**:
```json
{
  "url": "https://example.com/webhooks/klaviyo",
  "payload_size": 198,
  "signature_included": true,
  "status": "pass",
  "response_code": 200,
  "response_body": "{\"received\": true}"
}
```

**Express.js Webhook Handler**:
```javascript
const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.raw({ type: 'application/json' }));

const WEBHOOK_SECRET = process.env.KLAVIYO_WEBHOOK_SECRET;

function verifySignature(payload, signature, secret) {
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(payload);
  const expected = hmac.digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}

app.post('/webhooks/klaviyo', (req, res) => {
  // 1. Verify signature
  const signature = req.headers['x-klaviyo-webhook-signature'];
  if (!verifySignature(req.body, signature, WEBHOOK_SECRET)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // 2. Parse event
  const event = JSON.parse(req.body);

  // 3. Idempotency check (use event ID to prevent duplicate processing)
  const eventId = event.data?.id;
  // Check if eventId was already processed (use Redis/DB)

  // 4. Process by type
  switch (event.type) {
    case 'profile.subscribed':
      handleNewSubscriber(event.data);
      break;
    case 'profile.unsubscribed':
      handleUnsubscribe(event.data);
      break;
    case 'email.bounced':
      handleBounce(event.data);
      break;
    default:
      console.log(`Unhandled: ${event.type}`);
  }

  res.status(200).json({ received: true });
});
```

**Key Points**:
- Always verify webhook signatures before processing
- Use `timingSafeEqual` to prevent timing attacks
- Implement idempotency using event IDs
- Return 200 quickly — process asynchronously for heavy work
- Klaviyo retries failed webhook deliveries (non-2xx responses)

## Example 4: Catalog Sync Pipeline

**User Request**: "How do I sync my product catalog with Klaviyo for recommendations?"

**Analysis Steps**:
1. List existing catalog items to check current state
2. Define the catalog item schema
3. Create/update items via the API
4. Set up ongoing sync pattern

**Script Command**:
```bash
# List current catalog items
python scripts/klaviyo_client.py --action catalog-items --format table

# Create a catalog item
python scripts/klaviyo_client.py --action create-catalog-item \
    --properties '{"external_id": "PROD-001", "title": "Widget A", "description": "Premium widget", "url": "https://shop.example.com/widget-a", "image_url": "https://shop.example.com/images/widget-a.jpg", "price": 79.99}'
```

**Sample Catalog Listing**:
```json
[
  {
    "id": "CATALOG-ITEM-001",
    "type": "catalog-item",
    "external_id": "PROD-001",
    "title": "Widget A",
    "description": "Premium widget",
    "url": "https://shop.example.com/widget-a",
    "price": 79.99
  },
  {
    "id": "CATALOG-ITEM-002",
    "type": "catalog-item",
    "external_id": "PROD-002",
    "title": "Gadget B",
    "description": "Advanced gadget",
    "url": "https://shop.example.com/gadget-b",
    "price": 70.00
  }
]
```

**Nightly Sync Pattern (Python)**:
```python
from klaviyo_client import KlaviyoDevClient
import json

client = KlaviyoDevClient()

# Fetch products from your database/API
products = fetch_products_from_db()

for product in products:
    try:
        client.create_catalog_item({
            "external_id": product["sku"],
            "title": product["name"],
            "description": product["description"],
            "url": product["url"],
            "image_url": product["image_url"],
            "price": product["price"],
            "category": product["category"],
            "in_stock": product["inventory"] > 0,
        })
    except Exception as e:
        if "conflict" in str(e).lower():
            # Item already exists — update instead
            pass
        else:
            print(f"Error syncing {product['sku']}: {e}")
```

**Key Points**:
- Catalog items power product recommendations and Back in Stock flows
- Use `external_id` to match your internal product IDs
- For large catalogs (1000+), use bulk create/update endpoints
- Run sync nightly to keep prices and availability current
- Custom metadata fields can store any additional product attributes

## Example 5: Data Export with Pagination

**User Request**: "I need to export all our Klaviyo profiles to a CSV for analysis"

**Analysis Steps**:
1. Use cursor-based pagination to fetch all profiles
2. Handle rate limits with built-in SDK retries
3. Write results to CSV incrementally
4. Report progress during export

**Script Command**:
```bash
# Export all profiles to CSV
python scripts/dev_tools.py --tool export-data \
    --resource profiles \
    --output profiles.csv

# Export first 5000 profiles
python scripts/dev_tools.py --tool export-data \
    --resource profiles \
    --max-records 5000 \
    --output profiles.csv

# Export catalog to CSV
python scripts/dev_tools.py --tool export-data \
    --resource catalog \
    --output catalog.csv
```

**Sample Output**:
```
Page 1: fetched 100 profiles (total: 100)
Page 2: fetched 100 profiles (total: 200)
Page 3: fetched 100 profiles (total: 300)
...
Page 50: fetched 100 profiles (total: 5000)
Reached max pages limit (50)
Exported 5000 records to profiles.csv

{
  "resource": "profiles",
  "records_exported": 5000,
  "output_file": "profiles.csv"
}
```

**Sample CSV Output**:
```csv
id,email,phone_number,first_name,last_name,properties,created
PROF-001,jane@example.com,+15551234567,Jane,Doe,"{""loyalty_tier"": ""Gold""}",2025-01-15T10:30:00Z
PROF-002,john@example.com,+15559876543,John,Smith,"{""loyalty_tier"": ""Silver""}",2025-02-20T14:15:00Z
```

**Key Points**:
- Cursor-based pagination handles large datasets efficiently
- Max 100 profiles per page (API limit)
- SDK handles rate limiting with automatic retries
- Use `--max-records` to limit export size for testing
- Properties column contains JSON for nested custom fields
- For data warehouse pipelines, schedule exports via cron or Airflow

## Example 6: Integration Health Check

**User Request**: "Is my Klaviyo integration working correctly?"

**Analysis Steps**:
1. Verify API connectivity and authentication
2. Check API key scopes
3. Validate e-commerce event tracking
4. Test catalog access
5. Provide fix recommendations

**Script Command**:
```bash
python scripts/dev_tools.py --tool health-check
```

**Sample Output**:
```json
{
  "timestamp": "2026-02-09T14:30:00",
  "status": "degraded",
  "checks": [
    {
      "check": "API Connectivity",
      "status": "pass",
      "detail": "Successfully connected to Klaviyo API"
    },
    {
      "check": "Profile Read Scope",
      "status": "pass",
      "detail": "profiles:read scope verified"
    },
    {
      "check": "Metrics Available",
      "status": "pass",
      "detail": "24 event types found"
    },
    {
      "check": "E-commerce Events",
      "status": "warning",
      "detail": "Missing: started checkout"
    },
    {
      "check": "Catalog Access",
      "status": "pass",
      "detail": "catalogs:read verified (156 items found)"
    }
  ],
  "recommendations": [
    {
      "priority": "HIGH",
      "action": "Implement missing e-commerce event tracking",
      "reason": "Missing: started checkout",
      "expected_impact": "Enable automated flows for missing events"
    }
  ]
}
```

**Validate Specific Events**:
```bash
python scripts/dev_tools.py --tool validate-events \
    --events "Placed Order,Started Checkout,Viewed Product,Added to Cart"
```

**Sample Validation Output**:
```json
{
  "summary": {
    "events_checked": 4,
    "events_found": 3,
    "events_missing": 1
  },
  "results": [
    {"event": "Placed Order", "status": "found"},
    {"event": "Started Checkout", "status": "missing"},
    {"event": "Viewed Product", "status": "found"},
    {"event": "Added to Cart", "status": "found"}
  ],
  "recommendations": [
    {
      "priority": "HIGH",
      "action": "Implement tracking for 'Started Checkout'",
      "reason": "Event 'Started Checkout' not found in Klaviyo",
      "expected_impact": "Enable flows and segments triggered by this event"
    }
  ]
}
```

**Key Points**:
- Run health checks after initial setup and periodically (weekly/monthly)
- Missing events mean flows that depend on them won't trigger
- "degraded" status means some features work but others need attention
- "unhealthy" status means core connectivity is broken
- Pair with event validation to verify specific tracking implementations

## Common Developer Patterns

### Event Tracking Template
```python
# 1. Define event schema (name, required properties, unique_id source)
# 2. Implement server-side tracking with error handling
# 3. Include unique_id for idempotency
# 4. Log failures for monitoring
# 5. Verify events appear in Klaviyo metrics
```

### Bulk Operation Template
```python
# 1. Read data source (CSV, database, API)
# 2. Validate and clean data
# 3. Batch into chunks (max 10K for profiles)
# 4. Submit each batch with error handling
# 5. Track job IDs for status checking
# 6. Report results and errors
```

### Integration Testing Template
```python
# 1. Health check: API connectivity + scopes
# 2. Event validation: all expected events tracked
# 3. Profile sync: test create/update/read cycle
# 4. Webhook test: endpoint reachable + signature valid
# 5. Export test: pagination works for your data volume
```

### Rate Limit Strategy Template
```python
# 1. SDK: Use max_delay and max_retries for automatic handling
# 2. Raw HTTP: Implement exponential backoff with jitter
# 3. Bulk operations: Queue and throttle (10 req/s limit)
# 4. Monitor RateLimit-Remaining header for proactive throttling
# 5. Log 429 responses for capacity planning
```

## Pro Tips

### Ask Better Questions
Instead of: "How do I use the Klaviyo API?"
Ask: "Help me implement server-side event tracking for my checkout flow"

### Request Working Code
Instead of: "What's the event format?"
Ask: "Give me a complete Python script to track Placed Order with line items"

### Test Before Deploying
Instead of: "Deploy this integration"
Ask: "Run a health check and validate my event tracking before I go live"

### Focus on Error Handling
Instead of: "Track this event"
Ask: "Track this event with proper retry logic, rate limit handling, and error logging"

### Plan for Scale
Instead of: "Import these profiles"
Ask: "Import 100K profiles with batching, progress reporting, and error recovery"
