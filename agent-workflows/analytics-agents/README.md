<div align="center">

# Analytics Agents

**Autonomous GA4 monitoring and GTM implementation pipeline, built on n8n + Claude.**

[![GitHub stars](https://img.shields.io/github/stars/thatrebeccarae/dgtldept?style=for-the-badge&logo=github&color=181717)](https://github.com/thatrebeccarae/dgtldept/stargazers)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](../../LICENSE)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Rebecca%20Rae%20Barton-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/rebeccaraebarton)
[![Substack](https://img.shields.io/badge/Substack-dgtl%20dept*-FF6719?style=for-the-badge&logo=substack&logoColor=white)](https://dgtldept.substack.com/welcome)

A daily pipeline that watches your GA4 event data, compares it against your tracking spec, flags anomalies, uses Claude to diagnose gaps, and auto-creates GTM tags, triggers, and variables in an unpublished workspace for human review.

Works for in-house teams monitoring a single property or agencies and consultants managing multiple GA4 properties and GTM containers.

[**Back to Repo**](../../README.md)

</div>

---

## What It Does

Most analytics teams discover GA4 tracking gaps reactively — a dashboard goes blank, a stakeholder asks why conversions dropped, or someone notices a missing event six weeks after a deploy broke it.

This pipeline flips that. It runs daily, compares your live GA4 event data against a defined tracking spec, and catches tracking gaps and anomalies before anyone notices. GA4 anomaly detection flags volume drops and spikes; gap analysis identifies missing or misconfigured events. When it finds issues, it uses Claude to diagnose root causes, generate GTM implementation specs, and create the actual tags, triggers, and variables in a GTM workspace — all without publishing. A human reviews and approves before anything goes live.

**What it never does:**
- Publish a GTM container (workspace changes stay unpublished until a human publishes)
- Modify GA4 configuration (read-only access to GA4 Data API)
- Push code to any repository (dataLayer changes are flagged for eng teams)
- Skip the human approval gate

## Architecture Overview

```
Schedule Trigger (per property)
    │
    ▼
Read property config JSON
    │
    ▼
GA4 Data API ──► Fetch current event inventory + counts
    │
    ▼
Compare events vs tracking spec (Code node)
    │
    ├── All Clear ──► Slack: "100% coverage" ──► Write report ──► END
    │
    └── Issues Found
            │
            ├── Anomalies? ──► Slack URGENT alert
            │                  Claude Haiku: root cause analysis
            │
            └── Gaps? ──► Claude Sonnet: gap analysis + GTM specs
                           │
                           ▼
                      Slack: "Found N gaps. Proposed changes: ..."
                           │
                           ▼
                      Wait for human approval
                           │
                      ┌────┴────┐
                      │         │
                 APPROVED   REJECTED ──► END
                      │
                      ▼
                 Preflight: check GTM workspace availability
                      │
                      ▼
                 Create GTM workspace
                 Create variables (rate-limited)
                 Create triggers  (rate-limited)
                 Create tags      (rate-limited)
                      │
                      ▼
                 Slack: "Workspace ready. Review in GTM UI."
                      │
                      ▼
                 END
```

## What's Included

```
analytics-agents/
├── schemas/
│   ├── client-config.schema.json     # Per-property configuration schema
│   └── event-spec.schema.json        # Tracking spec schema (expected events)
├── scripts/
│   ├── validate-client-config.py     # Config validation script
│   ├── validate-event-spec.py        # Event spec validation script
│   ├── n8n-nodes/                    # Individual n8n Code node scripts
│   │   ├── ga4-auth.js               # GA4 service account authentication
│   │   ├── gtm-auth.js               # GTM service account authentication
│   │   ├── compare-events.js         # Event inventory vs spec comparison
│   │   ├── build-gap-analysis-prompt.js
│   │   ├── build-anomaly-prompt.js
│   │   ├── parse-gap-analysis-response.js
│   │   ├── parse-anomaly-response.js
│   │   ├── build-gtm-resources.js    # Constructs GTM tag/trigger/variable payloads
│   │   ├── workspace-preflight.js    # Checks workspace availability
│   │   ├── execute-gtm-writes.js     # Rate-limited GTM API writes
│   │   ├── format-slack-messages.js
│   │   ├── format-gtm-slack.js
│   │   ├── slack-templates.json
│   │   ├── write-monitoring-report.js
│   │   ├── write-implementation-prd.js
│   │   └── write-gtm-implementation-doc.js
│   └── n8n-workflows/               # Importable n8n workflow JSONs
│       ├── main-pipeline.json        # Core pipeline (shared across properties)
│       ├── triggers.json             # Per-property schedule triggers
│       └── error-workflow.json       # Global error handler
├── templates/
│   ├── implementation-doc.md.tmpl    # GTM implementation doc template
│   └── monitoring-status.md.tmpl    # Daily monitoring report template
├── test-data/
│   └── ga4-sample-response.json     # Sample GA4 API response for testing
└── README.md
```

## Prerequisites

| Requirement                      | Purpose                                                                         |
| -------------------------------- | ------------------------------------------------------------------------------- |
| **n8n** (self-hosted)            | Workflow orchestration and scheduling                                           |
| **Google Cloud service account** | GA4 Data API (read) + GTM API (read/write)                                      |
| **GA4 property**                 | The property you want to monitor                                                |
| **GTM container**                | Where implementation changes are created                                        |
| **Claude API key**               | Sonnet for gap analysis, Haiku for anomaly detection                            |
| **Slack app**                    | Notifications, alerts, and approval requests (requires Slack admin permissions) |

### Google Cloud Setup

The service account needs two API scopes:

- **GA4 Data API v1** — read-only access to event data
- **GTM API v2** — read/write access to workspaces, tags, triggers, and variables (but **not** publish permission)

> [!IMPORTANT]
> The service account should intentionally lack GTM publish permission. This is the technical enforcement of the approval gate — the agent literally cannot publish a container, even if the code tried.

## Setup

### 1. Create a Property Config

Define a JSON config per GA4 property following `schemas/client-config.schema.json`. This specifies the GA4 property ID, GTM container ID, schedule, Slack channel, and approvers. (One config per property — whether that's your own property or a client's.) Store config files outside version control in a directory your n8n instance can access — the trigger node references the config by file path.

```bash
# Validate your config
python scripts/validate-client-config.py path/to/client-config.json
```

### 2. Create an Event Spec

Define the expected events for the property following `schemas/event-spec.schema.json`. This is the source of truth the pipeline compares against.

```bash
# Validate your spec
python scripts/validate-event-spec.py path/to/event-spec.json
```

### 3. Import n8n Workflows

Import the three workflow JSONs from `scripts/n8n-workflows/` into your n8n instance:

1. **main-pipeline.json** — the shared pipeline logic
2. **triggers.json** — per-property schedule triggers (customize for your properties)
3. **error-workflow.json** — global error handler with Slack alerts

### 4. Configure Credentials in n8n

Set up the following credentials in n8n:

- Google service account JSON (for GA4 + GTM)
- Claude API key
- Slack bot token

### 5. Test with Sample Data

Use `test-data/ga4-sample-response.json` to dry-run the pipeline without hitting live APIs.

## How It Works

### The Daily Cycle

1. **Scheduled trigger fires** (per property, configurable cadence)
2. **GA4 fetch** pulls the current event inventory with counts from the last 7 days
3. **Comparison engine** checks events against the tracking spec — identifies missing events, unexpected events, and count anomalies (volume drops/spikes)
4. **If all clear:** Slack gets a green status message, a monitoring report is written, done
5. **If anomalies detected:** Slack gets an urgent alert, Claude Haiku analyzes root cause patterns
6. **If gaps detected:** Claude Sonnet generates a full gap analysis with GTM implementation specs (tag type, trigger conditions, variable dependencies)
7. **Human reviews** the proposed changes in Slack, approves or rejects
8. **If approved:** the pipeline runs a preflight check on GTM workspace availability, then creates the workspace and writes all resources (variables first, then triggers, then tags) with 4-second delays between API calls
9. **Implementation docs** are generated from templates and saved alongside the monitoring report
10. **Final Slack message** includes a direct link to the GTM workspace for review before publishing

### Multiple Properties

One pipeline, many properties. The workflow logic is identical across all properties — only the configuration changes:

| Per-Property | Shared |
|--------------|--------|
| GA4 property ID + credentials | n8n workflow logic |
| GTM container ID + credentials | Claude analysis prompts |
| Event spec (expected events) | GTM tag creation patterns |
| Slack channel | Monitoring report templates |
| Schedule cadence | Approval flow pattern |
| Approvers list | Workspace lifecycle rules |

Adding a new property = creating a config JSON + event spec + scheduling a trigger. No workflow duplication.

### Claude Model Usage

| Task | Model | Why | Approx. Cost |
|------|-------|-----|-------------|
| Gap analysis + GTM spec generation | Sonnet | Needs deep reasoning about event relationships, trigger logic, and implementation tradeoffs | ~$0.05-0.10/run |
| Anomaly root cause analysis | Haiku | Pattern matching on volume changes, faster turnaround for urgent alerts | ~$0.01/run |

### GTM Write Safety

- **Rate-limited:** 4-second delays between GTM API calls (respects API quotas)
- **Idempotent:** reruns detect existing resources by name and skip duplicates
- **Workspace-isolated:** all changes land in a named workspace (`claude-{purpose}-{date}`), never in the default workspace
- **Preflight checks:** verifies workspace availability before attempting creation (free GTM accounts allow 3 workspaces total)
- **No publish permission:** the service account cannot publish containers by design

## Security Model

### Credential Isolation

- Service account JSON files are stored outside any synced directory and never committed to version control
- Each property gets its own service account with scoped permissions
- n8n credential storage handles encryption at rest

### Approval Gate

The pipeline has a hard stop before any GTM writes. Proposed changes are sent to Slack with full specs. A designated approver must explicitly approve before the pipeline continues. Rejection ends the run with logged reasoning.

### Workspace Isolation

GTM workspaces act like branches — changes are invisible to the live container until explicitly published by a human with publish permission. The service account intentionally lacks this permission, making accidental publication impossible at the API level.

### Audit Trail

Every pipeline run produces timestamped documentation:
- Monitoring reports (what was checked, what was found)
- Implementation docs (what was created, GTM resource IDs)
- Slack message history (approvals, rejections, alerts)

## FAQ

<details>
<summary><strong>Does this publish GTM changes automatically?</strong></summary>

No. The service account is configured without publish permission, and the pipeline creates changes in an isolated workspace. A human must review in the GTM UI and publish manually.

</details>

<details>
<summary><strong>What happens if GTM already has 3 workspaces?</strong></summary>

The preflight check detects this and sends a Slack alert instead of failing. Free GTM accounts allow 3 workspaces total (including the default). The pipeline will not attempt to create a workspace if none are available.

</details>

<details>
<summary><strong>Can I run this without the GTM implementation step?</strong></summary>

Yes. The monitoring and gap analysis stages work independently. You can use this purely for daily tracking health checks — just skip the approval step and the pipeline ends after the Slack notification with gap analysis results.

</details>

<details>
<summary><strong>How do I add a new property?</strong></summary>

1. Create a property config JSON (validate with `scripts/validate-client-config.py`)
2. Create an event spec JSON (validate with `scripts/validate-event-spec.py`)
3. Add a schedule trigger in n8n pointing to the new config
4. Set up the Google service account with GA4 read + GTM write access for the property

No workflow changes needed.

</details>

## Resources

- [GA4 Data API v1 Documentation](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [Google Tag Manager API v2 Reference](https://developers.google.com/tag-platform/tag-manager/api/v2)
- [n8n Documentation](https://docs.n8n.io/)
- [Claude API Documentation](https://docs.anthropic.com/en/docs/api-reference)

## License

MIT — see [LICENSE](../../LICENSE) for details.
