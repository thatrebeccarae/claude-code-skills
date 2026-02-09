# Klaviyo Skill Pack

Everything a DTC marketing team needs for Klaviyo + Shopify + GA4 + Looker Studio — all in one Claude Code skill pack. Audit your email/SMS marketing, analyze store performance, build cross-platform dashboards, and create presentation-quality reports.

> **New to this pack?** Start with [GETTING_STARTED.md](GETTING_STARTED.md) for a step-by-step setup guide, or run `python scripts/setup.py` for the interactive wizard.

## How It All Connects

```
Shopify (orders, products, customers)
    |
    +--> Klaviyo (flows, segments, campaigns, email/SMS)
    |        |
    |        +--> GA4 (traffic, behavior, conversions)
    |        |
    |        +--> Looker Studio (cross-platform dashboards)
    |
    +--> Pro Deck Builder (polished presentations from any analysis)
```

The skills work independently, but they're designed to complement each other:
- Run a **Shopify** audit to find conversion issues, then check **Klaviyo** flows that address them
- Use **Looker Studio** scripts to push Klaviyo + Shopify data to Google Sheets for unified dashboards
- Analyze **GA4** traffic sources, then cross-reference with **Klaviyo** campaign performance
- Turn any analysis into a polished deck with **Pro Deck Builder**

## Skills Included

| Skill | What It Does | Maturity |
|-------|-------------|----------|
| **klaviyo-analyst** | Audit and optimize Klaviyo flows, segments, campaigns, deliverability, and revenue attribution. Marketing operations perspective with benchmarks, essential flows checklist, and full audit workflow. | Full (SKILL + REFERENCE + EXAMPLES + scripts) |
| **klaviyo-developer** | Build custom Klaviyo integrations — event tracking, SDK usage, webhooks, rate limits, catalog sync, OAuth, and data pipeline architecture. | Full (SKILL + REFERENCE + EXAMPLES + scripts) |
| **google-analytics** | Analyze GA4 data: traffic sources, engagement, content performance, conversion funnels, device comparison. | Full (SKILL + REFERENCE + EXAMPLES + scripts) |
| **shopify** | Audit Shopify store performance: orders, products, customers, conversion funnel, revenue trends. Includes API client and automated analysis. | Full (SKILL + REFERENCE + EXAMPLES + scripts) |
| **looker-studio** | Build cross-platform dashboards with Klaviyo + Shopify + GA4 data via Google Sheets pipeline. DTC dashboard templates and calculated field library. | Full (SKILL + REFERENCE + EXAMPLES + scripts) |
| **pro-deck-builder** | Create polished PowerPoint decks using PptxGenJS with VC-backed SaaS design quality (Linear/Vercel aesthetic). Dark and light modes, icon pipelines, chart formatting. | Docs (SKILL + REFERENCE) |

## Quick Start

### Option 1: Interactive Wizard (Recommended)

```bash
python scripts/setup.py
```

### Option 2: Manual Setup

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed instructions.

### Option 3: Just Install the Skills

If you already have API keys configured, copy skills to Claude Code:

```bash
for skill in klaviyo-analyst klaviyo-developer google-analytics shopify looker-studio pro-deck-builder; do
  cp -r "$skill" ~/.claude/skills/
done
```

## Prerequisites

### Klaviyo MCP Server (for Analyst + Developer skills)

The [Klaviyo MCP server](https://developers.klaviyo.com/en/docs/klaviyo_mcp_server) gives Claude direct access to your Klaviyo account data through 45 tools.

**1. Create a Klaviyo Private API Key**

1. Log in to [Klaviyo](https://www.klaviyo.com/login) (requires Owner, Admin, or Manager role)
2. Click your **organization name** in the bottom-left corner
3. Go to **Settings** > **API keys**
4. Click **Create Private API Key**
5. Name the key (e.g., `claude-code-mcp`), select **Read-only** scopes
6. Click **Create** and **copy the key immediately**

```bash
# Add to ~/.zshrc or ~/.bashrc
export KLAVIYO_API_KEY="pk_your_key_here"
```

**Recommended scopes:**

| Scope | Minimum (Read-only) | Full Access |
|-------|---------------------|-------------|
| Accounts | Read | Read |
| Campaigns | Read | Full |
| Catalogs | Read | Read |
| Events | Read | Full |
| Flows | Read | Read |
| Lists | Read | Read |
| Metrics | Read | Read |
| Profiles | Read | Full |
| Segments | Read | Full |
| Tags | Read | Read |
| Templates | Read | Full |

**2. Install the MCP Server**

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Add to `~/.mcp.json`:

```json
{
  "mcpServers": {
    "klaviyo": {
      "command": "uvx",
      "args": ["klaviyo-mcp-server@latest"],
      "env": {
        "PRIVATE_API_KEY": "${KLAVIYO_API_KEY}",
        "READ_ONLY": "true",
        "ALLOW_USER_GENERATED_CONTENT": "false"
      }
    }
  }
}
```

Restart Claude Code and verify with `/mcp`.

## Example Prompts

### Marketing Analyst (Klaviyo)
- "Audit my Klaviyo account and identify missing flows"
- "My abandoned cart flow has a 1.2% click rate -- how do I improve it?"
- "Build an RFM segmentation strategy"
- "Design an RFM segmentation strategy and present it in a slide deck"

### Developer (Klaviyo)
- "How do I track a custom event from my Node.js backend?"
- "Set up a bulk profile import script for migrating 50K contacts"
- "Help me handle Klaviyo rate limits in my integration"
- "Design a webhook handler for Klaviyo subscription events"

### Shopify
- "Audit my Shopify store and tell me what needs fixing"
- "Which products should I restock based on sales velocity?"
- "Analyze my customer cohorts for the last 90 days"
- "What Shopify apps should I add for a DTC brand doing $2M/yr?"

### Google Analytics
- "Review our GA4 performance for the last 30 days"
- "Which traffic sources are driving the most conversions?"
- "Compare mobile and desktop performance"
- "Analyze our conversion funnel and identify drop-off points"

### Looker Studio
- "Build a CRM performance dashboard with our Klaviyo data"
- "Set up a revenue attribution dashboard to reconcile Klaviyo and Shopify"
- "Create a Google Sheet template for a lifecycle marketing dashboard"
- "Push our Shopify order data to Google Sheets for Looker Studio"

### Decks
- "Build a dark-mode deck summarizing my Klaviyo flow performance"
- "Create a monthly marketing performance presentation"

## Resources

- [Klaviyo MCP Server Documentation](https://developers.klaviyo.com/en/docs/klaviyo_mcp_server)
- [Klaviyo API Reference](https://developers.klaviyo.com/en/reference/api_overview)
- [Shopify Admin API Reference](https://shopify.dev/docs/api/admin-rest)
- [Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [Looker Studio Help](https://support.google.com/looker-studio)
- [uv Package Manager Installation](https://docs.astral.sh/uv/getting-started/installation/)
