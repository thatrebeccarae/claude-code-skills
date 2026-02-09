# Klaviyo Skill Pack

A skill pack for Klaviyo-powered e-commerce marketing. Covers the full stack: email/SMS lifecycle marketing strategy, API developer integration, Shopify storefront optimization, and presentation-quality reporting.

## Skills Included

| Skill | What It Does |
|-------|-------------|
| **klaviyo-analyst** | Audit and optimize Klaviyo flows, segments, campaigns, deliverability, and revenue attribution. Marketing operations perspective with benchmarks, an essential flows checklist, and a full audit workflow. |
| **klaviyo-developer** | Build custom Klaviyo integrations — event tracking, SDK usage, webhooks, rate limits, catalog sync, OAuth, and data pipeline architecture. Includes API endpoint reference, code patterns, and migration guide. |
| **shopify** | Audit Shopify store performance, conversion funnels, tracking setup (Meta CAPI, GA4, Google Ads), product feeds, and the marketing app stack. Includes a tiered app stack recommendation and CRO playbook. |
| **pro-deck-builder** | Create polished PowerPoint decks using PptxGenJS with VC-backed SaaS design quality (Linear/Vercel aesthetic). Dark and light modes, icon pipelines, chart formatting, and built-in QA. |

## Installation

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
