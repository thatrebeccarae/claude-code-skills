# Getting Started with Analytics Agents

A step-by-step guide to setting up autonomous GA4 monitoring with n8n and Claude. No prior automation experience required -- this guide explains everything in plain English.

## What This Workflow Does

This pipeline monitors your Google Analytics 4 properties every day and tells you what needs fixing:

1. **Fetches** your GA4 event data via the GA4 Data API
2. **Compares** what's firing against your event spec (the events you *expect* to see)
3. **Analyzes** gaps and anomalies using Claude (Anthropic's AI)
4. **Notifies** you in Slack with a summary and recommended fixes
5. **Optionally** creates GTM tags, triggers, and variables in a draft workspace for you to review

It runs daily on a schedule. Most days it confirms everything looks good. When something breaks or is missing, you get a Slack alert with context and next steps.

### Multi-Tenant Support

One pipeline handles multiple GA4 properties. Each property gets its own config file, event spec, Slack channel, and schedule. Adding a new property means creating two JSON files -- no workflow duplication.

### What It Never Does

- Publishes GTM changes (the service account lacks permission -- this is a hard safety boundary)
- Modifies your GA4 configuration (read-only access only)
- Pushes code to any repository
- Makes changes without your explicit approval

## Prerequisites

You will need all of the following before starting setup:

| Prerequisite | What It Is | Time to Set Up |
|---|---|---|
| **n8n** | Open-source workflow automation (self-hosted) | 15-30 min |
| **Google Cloud service account** | Lets the pipeline read your GA4 data | 10 min |
| **GA4 property access** | Viewer role for the service account | 5 min |
| **Slack app** | Bot that sends notifications to your channels | 10 min |
| **Anthropic API key** | Powers the Claude analysis step | 5 min |
| **GTM API access** *(optional)* | Only needed if you want auto-implementation of tags | 10 min |

**Estimated total setup time:** 45-60 minutes for your first property. 10 minutes for each additional property after that.

---

## Step 1: Set Up n8n

n8n is the orchestration layer. It runs your schedules, calls the APIs, and routes the results. You need a self-hosted instance (the cloud version works too, but self-hosted gives you full control over file access and credentials).

### Option A: Docker (Recommended)

If you have Docker installed, this is the fastest path.

Create a `docker-compose.yml` file:

```yaml
services:
  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=your-secure-password-here
      - GENERIC_TIMEZONE=America/New_York
    volumes:
      - n8n_data:/home/node/.n8n
      - ./credentials:/credentials:ro
      - ./configs:/configs:ro
      - ./event-specs:/event-specs:ro
      - ./reports:/reports

volumes:
  n8n_data:
```

Start it:

```bash
docker compose up -d
```

Open `http://localhost:5678` in your browser. You should see the n8n setup screen.

> **What are these volume mounts?**
> - `n8n_data` -- n8n's internal storage (workflows, settings)
> - `./credentials` -- where you'll put your Google service account JSON files (mounted read-only)
> - `./configs` -- where your client config files live (mounted read-only)
> - `./event-specs` -- where your event spec files live (mounted read-only)
> - `./reports` -- where the pipeline writes daily monitoring reports

Create the local directories:

```bash
mkdir -p credentials configs event-specs reports
```

### Option B: npm (No Docker)

```bash
npm install n8n -g
n8n start
```

If you go this route, you'll reference file paths on your local filesystem instead of Docker container paths. Everywhere this guide says `/credentials/...`, use the actual path on your machine (e.g., `/home/yourname/analytics-pipeline/credentials/...`).

> **n8n docs:** [https://docs.n8n.io/hosting/installation/](https://docs.n8n.io/hosting/installation/)

---

## Step 2: Create a Google Cloud Service Account

The service account is how the pipeline authenticates with Google's APIs. Think of it as a robot user that can read your GA4 data (and optionally edit your GTM container).

### 2a. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the project dropdown at the top of the page
3. Click **New Project**
4. Name it something like `analytics-pipeline` (the name doesn't matter to the pipeline)
5. Click **Create**
6. Make sure the new project is selected in the dropdown

### 2b. Enable the GA4 Data API

1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for **Google Analytics Data API**
3. Click on it, then click **Enable**

If you also want GTM auto-implementation (optional), enable these too:
- **Tag Manager API**

### 2c. Create the Service Account

1. Go to **IAM & Admin** > **Service Accounts**
2. Click **Create Service Account**
3. Name: `analytics-pipeline` (or whatever you prefer)
4. Description: `Reads GA4 data and manages GTM workspaces for the analytics monitoring pipeline`
5. Click **Create and Continue**
6. Skip the "Grant this service account access to project" step (click **Continue**)
7. Skip the "Grant users access" step (click **Done**)

### 2d. Download the JSON Key

1. Click on the service account you just created
2. Go to the **Keys** tab
3. Click **Add Key** > **Create new key**
4. Select **JSON** and click **Create**
5. A `.json` file will download. This is your credentials file.

**Move this file into your credentials directory:**

```bash
mv ~/Downloads/analytics-pipeline-*.json ./credentials/my-property-sa.json
```

> **Security note:** This file grants access to your GA4 data. Keep it out of version control. Never commit it to a repository. The Docker volume mount uses `:ro` (read-only) as an extra precaution.

### 2e. Grant GA4 Access to the Service Account

1. Open the JSON file you just downloaded and find the `client_email` field. It looks like: `analytics-pipeline@your-project.iam.gserviceaccount.com`
2. Go to [Google Analytics](https://analytics.google.com)
3. Click **Admin** (gear icon, bottom-left)
4. Under your property, click **Property access management**
5. Click the **+** button, then **Add users**
6. Paste the `client_email` address
7. Set the role to **Viewer**
8. Uncheck "Notify new users by email" (it's a service account, not a person)
9. Click **Add**

### 2f. Find Your GA4 Property ID

You'll need this for the config file in Step 4.

1. In Google Analytics, go to **Admin**
2. Under your property name, you'll see the **Property ID** -- it's a number like `123456789`
3. Write it down

> **GA4 Data API docs:** [https://developers.google.com/analytics/devguides/reporting/data/v1](https://developers.google.com/analytics/devguides/reporting/data/v1)

---

## Step 3: Set Up GTM Access (Optional)

Skip this step if you only want monitoring and Slack alerts. GTM access is only needed if you want the pipeline to automatically create tags, triggers, and variables in a draft workspace for you to review.

### 3a. Grant GTM Access to the Service Account

1. Go to [Google Tag Manager](https://tagmanager.google.com)
2. Click **Admin**
3. Under **Container**, click **User Management**
4. Click the **+** button, then **Add user**
5. Paste the same `client_email` from your service account JSON
6. Set the permission to **Edit** (NOT Approve, NOT Publish)
7. Click **Save**

> **Why "Edit" and not higher?** Edit permission lets the pipeline create tags, triggers, and variables in draft workspaces. It physically cannot publish changes -- the API will return a 403 error if it tries. This is a hard safety boundary.

### 3b. Find Your GTM Account and Container IDs

1. In GTM, click **Admin**
2. Your **Account ID** is the number in the URL after `/accounts/`
3. Your **Container ID** is the number after `/containers/`
4. Write both down for Step 4

> **GTM API docs:** [https://developers.google.com/tag-platform/tag-manager/api/v2](https://developers.google.com/tag-platform/tag-manager/api/v2)

---

## Step 4: Create Your Client Config

The client config tells the pipeline which GA4 property to monitor, which GTM container to use, where to send Slack messages, and when to run.

Create a JSON file in your `configs` directory. Name it after your property (e.g., `my-store.json`):

```json
{
  "client_id": "my-store",
  "client_name": "My Store",
  "ga4": {
    "property_id": "123456789",
    "credentials_file": "/credentials/my-property-sa.json"
  },
  "gtm": {
    "account_id": "1234567",
    "container_id": "7654321",
    "credentials_file": "/credentials/my-property-sa.json",
    "workspace_name_prefix": "claude",
    "tier": "free"
  },
  "vault": {
    "base_path": "/reports/my-store",
    "event_spec": "/event-specs/my-store-events.json",
    "monitoring_dir": "/reports/my-store/monitoring",
    "implementation_dir": "/reports/my-store/implementation"
  },
  "slack": {
    "channel": "#my-store-analytics",
    "alert_channel": "#analytics-alerts",
    "approvers": ["your-slack-username"]
  },
  "schedule": {
    "monitoring": "0 7 * * 1-5",
    "description": "Weekdays at 7am ET"
  }
}
```

**Field-by-field breakdown:**

| Field | What to Put Here |
|---|---|
| `client_id` | A short slug with no spaces. Used in filenames and report paths. |
| `client_name` | The human-readable name that appears in Slack messages. |
| `ga4.property_id` | Your GA4 property ID from Step 2f. |
| `ga4.credentials_file` | Path to the service account JSON *inside the Docker container*. If you followed the Docker setup, this starts with `/credentials/`. |
| `gtm.account_id` | Your GTM account ID from Step 3b. Set to `"0"` if skipping GTM. |
| `gtm.container_id` | Your GTM container ID from Step 3b. Set to `"0"` if skipping GTM. |
| `gtm.credentials_file` | Can be the same file as `ga4.credentials_file` if you used one service account for both. |
| `gtm.workspace_name_prefix` | The prefix for auto-created GTM workspaces. Default `"claude"` is fine. |
| `gtm.tier` | `"free"` for standard GTM (3-workspace limit) or `"360"` for GTM 360. |
| `vault.base_path` | Root directory for this property's reports. |
| `vault.event_spec` | Path to the event spec file you'll create in Step 5. |
| `vault.monitoring_dir` | Where daily status reports are written. |
| `vault.implementation_dir` | Where implementation docs are written (only used with GTM). |
| `slack.channel` | The Slack channel for daily status updates for this property. |
| `slack.alert_channel` | The Slack channel for urgent cross-property alerts. |
| `slack.approvers` | Slack usernames who can approve GTM changes. |
| `schedule.monitoring` | Cron expression for when monitoring runs. `0 7 * * 1-5` = weekdays at 7am. |

### Validate Your Config

Run the validation script to check for errors:

```bash
python scripts/validate-client-config.py configs/my-store.json
```

If you get an error about `jsonschema`, install it first:

```bash
pip install jsonschema
```

Create the report directories:

```bash
mkdir -p reports/my-store/monitoring reports/my-store/implementation
```

---

## Step 5: Create Your Event Spec

The event spec is the heart of the pipeline. It defines what GA4 events you *expect* to see firing on your property. The pipeline compares this spec against actual GA4 data every day to find gaps.

Create a JSON file in your `event-specs` directory (e.g., `my-store-events.json`):

```json
{
  "version": "1.0",
  "client": "my-store",
  "ga4_property": "123456789",
  "last_updated": "2026-03-09",
  "event_groups": [
    {
      "group_id": "ecommerce_core",
      "group_name": "Core E-commerce",
      "phase": 1,
      "description": "Standard e-commerce funnel events",
      "events": [
        {
          "name": "view_item",
          "type": "ga4_recommended",
          "ga4_type": "recommended",
          "description": "User views a product detail page",
          "fires_on": "Product detail page load",
          "required_params": ["item_id", "item_name", "price", "currency"],
          "gtm": {
            "tag_type": "gaawe",
            "trigger_type": "CUSTOM_EVENT",
            "trigger_event_name": "view_item",
            "requires_datalayer": true,
            "datalayer_variables": ["ecommerce.items"]
          },
          "replaces": null,
          "status": "not_implemented",
          "priority": "high"
        },
        {
          "name": "add_to_cart",
          "type": "ga4_recommended",
          "ga4_type": "recommended",
          "description": "User adds an item to cart",
          "fires_on": "Add-to-cart button click",
          "required_params": ["item_id", "item_name", "price", "currency", "quantity"],
          "gtm": {
            "tag_type": "gaawe",
            "trigger_type": "CUSTOM_EVENT",
            "trigger_event_name": "add_to_cart",
            "requires_datalayer": true,
            "datalayer_variables": ["ecommerce.items"]
          },
          "replaces": null,
          "status": "not_implemented",
          "priority": "high"
        },
        {
          "name": "begin_checkout",
          "type": "ga4_recommended",
          "ga4_type": "recommended",
          "description": "User starts the checkout process",
          "fires_on": "Checkout page load or checkout button click",
          "required_params": ["item_id", "item_name", "price", "currency"],
          "gtm": {
            "tag_type": "gaawe",
            "trigger_type": "CUSTOM_EVENT",
            "trigger_event_name": "begin_checkout",
            "requires_datalayer": true,
            "datalayer_variables": ["ecommerce.items"]
          },
          "replaces": null,
          "status": "not_implemented",
          "priority": "critical"
        },
        {
          "name": "purchase",
          "type": "ga4_recommended",
          "ga4_type": "recommended",
          "description": "User completes a purchase",
          "fires_on": "Order confirmation page load",
          "required_params": ["transaction_id", "value", "currency", "items"],
          "gtm": {
            "tag_type": "gaawe",
            "trigger_type": "CUSTOM_EVENT",
            "trigger_event_name": "purchase",
            "requires_datalayer": true,
            "datalayer_variables": ["ecommerce.transaction_id", "ecommerce.value", "ecommerce.items"]
          },
          "replaces": null,
          "status": "not_implemented",
          "priority": "critical"
        }
      ]
    },
    {
      "group_id": "lead_gen",
      "group_name": "Lead Generation",
      "phase": 2,
      "description": "Form submissions and signup events",
      "events": [
        {
          "name": "generate_lead",
          "type": "ga4_recommended",
          "ga4_type": "recommended",
          "description": "User submits a lead form",
          "fires_on": "Form submission success",
          "required_params": ["form_id", "form_name"],
          "gtm": {
            "tag_type": "gaawe",
            "trigger_type": "CUSTOM_EVENT",
            "trigger_event_name": "generate_lead",
            "requires_datalayer": true,
            "datalayer_variables": ["form_id", "form_name"]
          },
          "replaces": null,
          "status": "not_implemented",
          "priority": "high"
        }
      ]
    }
  ],
  "deprecated_events": [],
  "custom_dimensions_needed": [
    {
      "name": "form_id",
      "scope": "event",
      "description": "Identifier for the form that was submitted"
    }
  ]
}
```

### Tips for Writing Your Event Spec

- **Start small.** You don't need to spec every event on day one. Start with your core conversion funnel (e.g., product views through purchase) and expand later.
- **Use GA4 recommended events** where possible. GA4 gives you richer reporting when you use its standard event names (`view_item`, `add_to_cart`, `purchase`, etc.). See [GA4 recommended events](https://support.google.com/analytics/answer/9267735).
- **Set priorities.** `critical` = must-have for business reporting. `high` = important for funnel analysis. `medium` = nice-to-have. `low` = aspirational.
- **Group by funnel stage.** This makes the daily reports easier to scan.
- **Update `status`** as events get implemented: `not_implemented` > `in_workspace` > `published`.

### Validate Your Event Spec

```bash
python scripts/validate-event-spec.py event-specs/my-store-events.json
```

---

## Step 6: Set Up Slack Notifications

The pipeline sends daily status updates and urgent alerts to Slack. You need a Slack app with a bot token.

### 6a. Create a Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App** > **From scratch**
3. Name it `Analytics Agent` (or whatever you prefer)
4. Select your workspace
5. Click **Create App**

### 6b. Add Bot Permissions

1. In the app settings, go to **OAuth & Permissions**
2. Scroll to **Scopes** > **Bot Token Scopes**
3. Add these scopes:
   - `chat:write` -- send messages
   - `files:write` -- upload report files
   - `channels:read` -- list channels (for validation)
4. Scroll back up and click **Install to Workspace**
5. Authorize the app

### 6c. Copy the Bot Token

After installing, you'll see a **Bot User OAuth Token** starting with `xoxb-`. Copy this -- you'll need it for n8n.

### 6d. Invite the Bot to Your Channels

In Slack, go to each channel you specified in your client config and invite the bot:

```
/invite @Analytics Agent
```

Do this for both the per-property channel (e.g., `#my-store-analytics`) and the alerts channel (e.g., `#analytics-alerts`).

> **Slack API docs:** [https://api.slack.com/docs](https://api.slack.com/docs)

---

## Step 7: Get an Anthropic API Key

Claude analyzes the event gaps and anomalies. You need an Anthropic API key.

1. Go to [https://console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in
3. Go to **API Keys**
4. Click **Create Key**
5. Name it `analytics-pipeline`
6. Copy the key (starts with `sk-ant-`)

The pipeline uses Claude Sonnet for gap analysis and GTM spec generation. A typical daily run costs $0.02-0.10 when gaps are found, and $0 when everything is clear (Claude is only called when there's something to analyze).

> **Anthropic API docs:** [https://docs.anthropic.com/en/api](https://docs.anthropic.com/en/api)

---

## Step 8: Configure n8n Credentials

Before importing the workflows, set up the API credentials in n8n so the workflows can reference them.

### 8a. Add the Anthropic API Key

1. In n8n, go to **Settings** > **Credentials**
2. Click **Add Credential**
3. Search for **Header Auth** (we'll use this for the Anthropic API)
4. Name it `Anthropic API Key`
5. Set:
   - Name: `x-api-key`
   - Value: your `sk-ant-...` key
6. Click **Save**

### 8b. Add the Slack Bot Token

1. Click **Add Credential**
2. Search for **Slack API**
3. Name it `Analytics Agent Slack`
4. Paste your `xoxb-...` bot token
5. Click **Save**

### 8c. Verify Credential File Access

If you're using Docker, verify n8n can read your service account JSON:

```bash
docker compose exec n8n ls /credentials/
```

You should see your service account file(s) listed. If not, check your volume mounts in `docker-compose.yml`.

---

## Step 9: Import the n8n Workflows

The pipeline consists of three n8n workflows. Import them in this order:

### 9a. Import the Error Handler

1. In n8n, click **Workflows** > **Add Workflow** (the + button)
2. Click the **...** menu > **Import from File**
3. Select `scripts/n8n-workflows/error-workflow.json`
4. Update the Slack channel in the error notification node to match your `alert_channel`
5. Save and activate the workflow

### 9b. Import the Main Pipeline

1. Import `scripts/n8n-workflows/main-pipeline.json`
2. In each HTTP Request node, connect the credentials you created in Step 8:
   - **GA4 Fetch** and **GTM** nodes: no credential needed (the workflow handles auth via service account JSON)
   - **Claude Analysis** nodes: select your `Anthropic API Key` credential
   - **Slack** nodes: select your `Analytics Agent Slack` credential
3. Set the **Error Workflow** in workflow settings to the error handler you imported in 9a
4. Save the workflow (don't activate yet)

### 9c. Import the Triggers

1. Import `scripts/n8n-workflows/triggers.json`
2. Update the schedule triggers to match your client config's cron schedule
3. Update the config file path in the "Read Config" node to point to your config file (e.g., `/configs/my-store.json`)
4. Save and activate the workflow

---

## Step 10: Test the Pipeline

Before relying on the daily schedule, run a manual test.

### 10a. Trigger a Manual Run

1. Open the **Triggers** workflow in n8n
2. Click **Test Workflow** (or use the webhook trigger if one is configured)
3. Watch the execution in real time -- n8n shows each node lighting up as it runs

### 10b. What to Expect on First Run

Your first run will likely show gaps (unless your GA4 property already has every event in your spec). You should see:

1. **GA4 Fetch** pulls your event data (takes 1-2 seconds)
2. **Compare Events** identifies missing events and calculates coverage percentage
3. **Claude Analysis** generates a summary of what's missing and why it matters
4. **Slack Notification** sends a message to your channel with the results

Check your Slack channel. You should see something like:

```
Analytics Agent  10:02 AM

GA4 Status: My Store - 3 Event Gaps Found

Coverage: 25% (1/4 spec events)

Missing (critical):
  - begin_checkout
  - purchase

Missing (high):
  - view_item

Full report: /reports/my-store/monitoring/2026-03-09-status.md
```

### 10c. Verify the Report File

Check that the monitoring report was written:

```bash
# Docker
docker compose exec n8n cat /reports/my-store/monitoring/2026-03-09-status.md

# Non-Docker
cat reports/my-store/monitoring/2026-03-09-status.md
```

### 10d. Common First-Run Issues

| Problem | Fix |
|---|---|
| GA4 Fetch returns 403 | The service account doesn't have Viewer access on your GA4 property. Go back to Step 2e. |
| GA4 Fetch returns 403 with "API not enabled" | You didn't enable the Google Analytics Data API. Go back to Step 2b. |
| "File not found" on credential or config | Check your Docker volume mounts. The path inside the container must match your config. |
| Slack message not received | Make sure you invited the bot to the channel (Step 6d). Check the bot token is correct. |
| Claude analysis fails with 401 | Your Anthropic API key is invalid or expired. Regenerate it at console.anthropic.com. |
| "No rows returned" from GA4 | Your property may have no data for the last 7 days, or the property ID is wrong. |

---

## Adding More Properties

To monitor additional GA4 properties:

1. Create a new service account JSON (or reuse the same one if it has access)
2. Grant Viewer access on the new GA4 property (Step 2e)
3. Create a new client config JSON in `configs/`
4. Create a new event spec JSON in `event-specs/`
5. Create the report directories: `mkdir -p reports/{new-property}/monitoring reports/{new-property}/implementation`
6. Add a new schedule trigger in the Triggers workflow pointing to the new config file
7. Invite the Slack bot to the new property's channel

No workflow changes needed. The main pipeline handles everything based on the config.

---

## Cost Estimate

| Component | Cost |
|---|---|
| GA4 Data API | Free |
| GTM API | Free |
| n8n (self-hosted) | Free |
| Slack | Free (standard plan is sufficient) |
| Claude API (per daily run, no gaps found) | ~$0 |
| Claude API (per run with gaps + GTM implementation) | ~$0.05-0.18 |
| **Monthly estimate, 1 property, daily monitoring** | **< $1** |
| **Monthly estimate, 3 properties, daily monitoring** | **$1-3** |

---

## What's in This Directory

```
analytics-agents/
  README.md                       <- Overview and architecture
  GETTING_STARTED.md              <- You are here

  schemas/
    client-config.schema.json     <- JSON Schema for client configs
    event-spec.schema.json        <- JSON Schema for event specs

  scripts/
    validate-client-config.py     <- Config file validator
    validate-event-spec.py        <- Event spec validator
    n8n-nodes/                    <- JavaScript for n8n Code nodes
      ga4-auth.js                 <- GA4 service account authentication
      gtm-auth.js                 <- GTM service account authentication
      compare-events.js           <- Event inventory vs spec comparison
      build-gap-analysis-prompt.js
      build-anomaly-prompt.js
      parse-gap-analysis-response.js
      parse-anomaly-response.js
      build-gtm-resources.js      <- Constructs GTM tag/trigger/variable payloads
      execute-gtm-writes.js       <- Rate-limited GTM API writes
      workspace-preflight.js      <- Checks workspace availability
      format-slack-messages.js
      format-gtm-slack.js
      write-monitoring-report.js
      write-implementation-prd.js
      write-gtm-implementation-doc.js

  templates/
    implementation-doc.md.tmpl    <- Template for GTM implementation docs
    monitoring-status.md.tmpl     <- Template for daily monitoring reports
```

## Troubleshooting

### n8n can't read files inside the container

If you see "ENOENT: no such file or directory" errors, your Docker volume mounts aren't configured correctly. Verify:

```bash
docker compose exec n8n ls /credentials/
docker compose exec n8n ls /configs/
docker compose exec n8n ls /event-specs/
```

Each should list your files. If a directory is empty, check the `volumes:` section in your `docker-compose.yml`.

### GTM workspace limit reached

Free GTM allows 3 workspaces per container (including the Default Workspace). If your team is already using the extra slots, the pipeline will skip GTM implementation and alert you in Slack. Free a workspace in the GTM UI and re-trigger the pipeline.

### Claude analysis returns unexpected results

The analysis quality depends on your event spec. The more context you provide in the `description` and `fires_on` fields, the better Claude's recommendations will be.

### Rate limit errors from GTM API

The GTM API allows 1 request every 4 seconds. The pipeline includes built-in delays between API calls. If you still hit rate limits, increase the Wait node duration in the main pipeline workflow.

## Getting Help

- **n8n Community:** [https://community.n8n.io](https://community.n8n.io)
- **GA4 Data API Reference:** [https://developers.google.com/analytics/devguides/reporting/data/v1](https://developers.google.com/analytics/devguides/reporting/data/v1)
- **GTM API Reference:** [https://developers.google.com/tag-platform/tag-manager/api/v2](https://developers.google.com/tag-platform/tag-manager/api/v2)
- **Anthropic API Docs:** [https://docs.anthropic.com/en/api](https://docs.anthropic.com/en/api)
- **Issues:** Open an issue on this repository
