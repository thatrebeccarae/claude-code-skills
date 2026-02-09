# Klaviyo Skill Pack

A Claude Code skill pack for Klaviyo-powered e-commerce marketing. Covers the full stack: email/SMS lifecycle marketing strategy, API developer integration, Shopify storefront optimization, and presentation-quality reporting.

> **Requires the [Klaviyo MCP Server](https://developers.klaviyo.com/en/docs/klaviyo_mcp_server) and a Klaviyo private API key.** The klaviyo-analyst and klaviyo-developer skills query your Klaviyo account data (profiles, flows, segments, campaigns, metrics) through the MCP server. Without it, these skills provide general Klaviyo guidance but cannot read or act on your account.

## Prerequisites

### 1. Create a Klaviyo Private API Key

You need a [Klaviyo private API key](https://help.klaviyo.com/hc/en-us/articles/7423954176283) to authenticate the MCP server. Private keys start with `pk_` and are 36 characters long.

**Steps** ([Klaviyo docs: manage API keys](https://help.klaviyo.com/hc/en-us/articles/115005062267)):

1. Log in to [Klaviyo](https://www.klaviyo.com/login) (requires Owner, Admin, or Manager role)
2. Click your **organization name** in the bottom-left corner
3. Go to **Settings** > **API keys**
4. Click **Create Private API Key**
5. Name the key (e.g., `claude-code-mcp`)
6. Select scopes — choose **Read-only** for safe auditing, or **Full** if you want write access
7. Click **Create** and **copy the key immediately** — Klaviyo will not show it again

Store the key in an environment variable:

```bash
# Add to ~/.zshrc or ~/.bashrc
export KLAVIYO_API_KEY="pk_your_key_here"
```

**Recommended scopes for these skills:**

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

### 2. Install the Klaviyo MCP Server

The official [Klaviyo MCP server](https://developers.klaviyo.com/en/docs/klaviyo_mcp_server) runs via `uvx` (from the [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager). It exposes 45 tools for reading and managing Klaviyo data through any MCP-compatible client.

**Install uv** (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Add the MCP server to your Claude Code config** (`~/.mcp.json`):

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

**Environment variables:**

| Variable | Options | Default | Description |
|----------|---------|---------|-------------|
| `PRIVATE_API_KEY` | `pk_...` | required | Your Klaviyo private API key |
| `READ_ONLY` | `true` / `false` | `false` | Set `true` to disable all write operations (recommended for auditing) |
| `ALLOW_USER_GENERATED_CONTENT` | `true` / `false` | `true` | Set `false` to prevent the LLM from interpreting user-generated content in your account (recommended) |

Restart Claude Code after saving. Verify the server is running:

```
/mcp
```

You should see `klaviyo` listed with available tools like `klaviyo_get_flows`, `klaviyo_get_campaigns`, `klaviyo_get_profiles`, etc.

### 3. Install the Skills

Copy the skill folders into your Claude Code skills directory:

```bash
cp -r klaviyo-analyst klaviyo-developer shopify pro-deck-builder ~/.claude/skills/
```

Or symlink them:

```bash
for skill in klaviyo-analyst klaviyo-developer shopify pro-deck-builder; do
  ln -s "$(pwd)/$skill" ~/.claude/skills/$skill
done
```

## Skills Included

| Skill | What It Does |
|-------|-------------|
| **klaviyo-analyst** | Audit and optimize Klaviyo flows, segments, campaigns, deliverability, and revenue attribution. Marketing operations perspective with benchmarks, an essential flows checklist, and a full audit workflow. |
| **klaviyo-developer** | Build custom Klaviyo integrations — event tracking, SDK usage, webhooks, rate limits, catalog sync, OAuth, and data pipeline architecture. Includes API endpoint reference, code patterns, and migration guide. |
| **shopify** | Audit Shopify store performance, conversion funnels, tracking setup (Meta CAPI, GA4, Google Ads), product feeds, and the marketing app stack. Includes a tiered app stack recommendation and CRO playbook. |
| **pro-deck-builder** | Create polished PowerPoint decks using PptxGenJS with VC-backed SaaS design quality (Linear/Vercel aesthetic). Dark and light modes, icon pipelines, chart formatting, and built-in QA. |

## Example Prompts

### Marketing Analyst
- "Audit my Klaviyo account and identify missing flows"
- "My abandoned cart flow has a 1.2% click rate -- how do I improve it?"
- "Build an RFM segmentation strategy"
- "Design an RFM segmentation strategy and present it in a slide deck"

### Developer
- "How do I track a custom event from my Node.js backend?"
- "Set up a bulk profile import script for migrating 50K contacts"
- "Help me handle Klaviyo rate limits in my integration"
- "Design a webhook handler for Klaviyo subscription events"
- "How do I migrate from Klaviyo v1 API to the current JSON:API format?"

### Shopify & Decks
- "What Shopify apps should I add for a DTC brand doing $2M/yr?"
- "Help me set up Meta CAPI on Shopify"
- "Build a dark-mode deck summarizing my Klaviyo flow performance"

## Resources

- [Klaviyo MCP Server Documentation](https://developers.klaviyo.com/en/docs/klaviyo_mcp_server)
- [Klaviyo API Reference](https://developers.klaviyo.com/en/reference/api_overview)
- [Manage API Keys (Klaviyo Help Center)](https://help.klaviyo.com/hc/en-us/articles/115005062267)
- [Create a Private API Key (Klaviyo Help Center)](https://help.klaviyo.com/hc/en-us/articles/7423954176283)
- [Authenticate API Requests](https://developers.klaviyo.com/en/docs/authenticate_)
- [uv Package Manager Installation](https://docs.astral.sh/uv/getting-started/installation/)
