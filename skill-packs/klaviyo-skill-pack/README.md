# Klaviyo Skill Pack

A skill pack for Klaviyo-powered e-commerce marketing. Covers the full stack: email/SMS lifecycle marketing in Klaviyo, Shopify storefront optimization, and presentation-quality reporting.

## Skills Included

| Skill | What It Does |
|-------|-------------|
| **klaviyo** | Audit and optimize Klaviyo flows, segments, campaigns, deliverability, and revenue attribution. Includes benchmarks, an essential flows checklist, and a full audit workflow. |
| **shopify** | Audit Shopify store performance, conversion funnels, tracking setup (Meta CAPI, GA4, Google Ads), product feeds, and the marketing app stack. Includes a tiered app stack recommendation and CRO playbook. |
| **pro-deck-builder** | Create polished PowerPoint decks using PptxGenJS with VC-backed SaaS design quality (Linear/Vercel aesthetic). Dark and light modes, icon pipelines, chart formatting, and built-in QA. |

## Installation

Copy the skill folders into your Claude Code skills directory:

```bash
cp -r klaviyo shopify pro-deck-builder ~/.claude/skills/
```

Or symlink them:

```bash
for skill in klaviyo shopify pro-deck-builder; do
  ln -s "$(pwd)/$skill" ~/.claude/skills/$skill
done
```

## Example Prompts

- "Audit my Klaviyo account and identify missing flows"
- "What Shopify apps should I add for a DTC brand doing $2M/yr?"
- "My abandoned cart flow has a 1.2% click rate -- how do I improve it?"
- "Build a dark-mode deck summarizing my Klaviyo flow performance"
- "Help me set up Meta CAPI on Shopify"
- "Design an RFM segmentation strategy and present it in a slide deck"
