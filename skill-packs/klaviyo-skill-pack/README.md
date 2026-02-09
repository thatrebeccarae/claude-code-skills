# Klaviyo Skill Pack for Claude Code

A complete DTC marketing toolkit for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Six skills covering Klaviyo email/SMS, Shopify analytics, Google Analytics, Looker Studio dashboards, and presentation generation -- all designed to work together.

> **New to this pack?** Start with [GETTING_STARTED.md](GETTING_STARTED.md) for a step-by-step setup guide, or run `python scripts/setup.py` for the interactive wizard.

## What's Included

| Skill | What It Does | Includes |
|-------|-------------|----------|
| **klaviyo-analyst** | Audit and optimize flows, segments, campaigns, deliverability, and revenue attribution. 4-phase deep audit framework with industry benchmarks and three-tier recommendation format. | SKILL + REFERENCE + EXAMPLES + scripts |
| **klaviyo-developer** | Build custom integrations: event tracking, SDK usage, webhooks, rate limits, catalog sync, OAuth. Integration health audit workflow with event schema best practices. | SKILL + REFERENCE + EXAMPLES + scripts |
| **shopify** | Audit store performance: orders, products, customers, conversion funnels, revenue trends. | SKILL + REFERENCE + EXAMPLES + scripts |
| **google-analytics** | Analyze GA4 data: traffic sources, engagement, content performance, conversion funnels, device comparison. | SKILL + REFERENCE + EXAMPLES + scripts |
| **looker-studio** | Build cross-platform dashboards with Klaviyo + Shopify + GA4 data via Google Sheets pipeline. DTC dashboard templates and calculated field library. | SKILL + REFERENCE + EXAMPLES + scripts |
| **pro-deck-builder** | Create polished PowerPoint decks using PptxGenJS. VC-backed SaaS design quality with dark/light modes, icon pipelines, and chart formatting. | SKILL + REFERENCE |

## How the Skills Connect

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

The skills work independently, but they complement each other:
- Run a **Shopify** audit to find conversion issues, then check **Klaviyo** flows that address them
- Use **Looker Studio** scripts to push Klaviyo + Shopify data to Google Sheets for unified dashboards
- Analyze **GA4** traffic sources, then cross-reference with **Klaviyo** campaign performance
- Turn any analysis into a polished deck with **Pro Deck Builder**

## Quick Start

### Option 1: Interactive Wizard (Recommended)

```bash
python scripts/setup.py
```

The wizard checks prerequisites, walks you through API key setup, installs dependencies, and tests connections.

### Option 2: Manual Setup

See [GETTING_STARTED.md](GETTING_STARTED.md) for detailed step-by-step instructions.

### Option 3: Copy Skills Directly

If you already have API keys configured:

```bash
for skill in klaviyo-analyst klaviyo-developer google-analytics shopify looker-studio pro-deck-builder; do
  cp -r "$skill" ~/.claude/skills/
done
```

## Prerequisites

### Klaviyo MCP Server (for Analyst + Developer skills)

The [Klaviyo MCP server](https://developers.klaviyo.com/en/docs/klaviyo_mcp_server) gives Claude direct access to your Klaviyo account data.

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

### Klaviyo Marketing Analyst
- "Audit my Klaviyo account and identify missing flows"
- "My abandoned cart flow has a 1.2% click rate -- how do I improve it?"
- "Build an RFM segmentation strategy for my DTC brand"
- "Give me a three-tier recommendation with implementation spec for fixing my click rates"
- "Design an RFM segmentation strategy and present it in a slide deck"

### Klaviyo Developer
- "How do I track a custom event from my Node.js backend?"
- "Set up a bulk profile import script for migrating 50K contacts"
- "Help me handle Klaviyo rate limits in my integration"
- "Design a webhook handler for Klaviyo subscription events"
- "Audit my integration -- are events structured correctly?"

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

### Presentations
- "Build a dark-mode deck summarizing my Klaviyo flow performance"
- "Create a monthly marketing performance presentation"

## Frequently Asked Questions

### Do I need all six skills?

No. Install only the skills for platforms you use. Each skill works independently. The Klaviyo Analyst skill is the most popular starting point.

### Do I need the Klaviyo MCP server?

The MCP server lets Claude pull live data from your Klaviyo account (flows, segments, campaigns, metrics). Without it, Claude still has full Klaviyo expertise but you'll need to provide data manually (paste metrics, share screenshots, or use the included scripts).

### What Klaviyo API scopes are needed?

Read-only scopes are sufficient for all audit and analysis tasks. Only enable write scopes if you want Claude to help build integrations that modify data.

### Can I use this with multiple Klaviyo accounts?

Yes. Configure multiple MCP server entries in `~/.mcp.json` with different environment variable names (e.g., `KLAVIYO_API_KEY_BRAND1`, `KLAVIYO_API_KEY_BRAND2`).

### How is this different from Klaviyo's built-in AI?

Klaviyo's AI features work within the Klaviyo UI for specific tasks (subject line generation, segment suggestions). This skill pack gives Claude deep, cross-platform expertise: it can audit your entire marketing stack, compare Klaviyo data with Shopify and GA4, produce implementation specs, and generate presentation decks -- all from natural language prompts in your terminal.

## Resources

- [Klaviyo MCP Server Documentation](https://developers.klaviyo.com/en/docs/klaviyo_mcp_server)
- [Klaviyo API Reference](https://developers.klaviyo.com/en/reference/api_overview)
- [Shopify Admin API Reference](https://shopify.dev/docs/api/admin-rest)
- [Google Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1)
- [Looker Studio Help](https://support.google.com/looker-studio)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
