# Klaviyo Skills for Claude Code

Open-source skill pack that gives [Claude Code](https://docs.anthropic.com/en/docs/claude-code) deep Klaviyo, Shopify, GA4, and Looker Studio expertise. Audit your email/SMS flows, diagnose deliverability, benchmark campaigns, build cross-platform dashboards, and generate polished decks — all from natural language prompts.

## What's Inside

| Skill | What Claude Can Do |
|-------|-------------------|
| **Klaviyo Analyst** | 4-phase account audit, flow gap analysis, segment health, deliverability diagnostics, revenue attribution, three-tier recommendations with implementation specs |
| **Klaviyo Developer** | Event schema design, SDK integration, webhook handling, rate limit strategy, catalog sync, integration health audit |
| **Shopify** | Store performance audit, product velocity, customer cohorts, conversion funnel analysis |
| **Google Analytics** | GA4 traffic analysis, channel comparison, conversion funnels, content performance |
| **Looker Studio** | Cross-platform dashboards via Google Sheets pipeline, DTC dashboard templates |
| **Pro Deck Builder** | Presentation-quality PowerPoint decks with dark/light modes (PptxGenJS) |

## Quick Start

```bash
git clone https://github.com/thatrebeccarae/claude-code-skills.git
cd claude-code-skills/skill-packs/klaviyo-skill-pack
python scripts/setup.py
```

The interactive wizard handles API keys, dependencies, and connection testing. For manual setup, see [GETTING_STARTED.md](skill-packs/klaviyo-skill-pack/GETTING_STARTED.md).

## Documentation

- [**README**](skill-packs/klaviyo-skill-pack/README.md) — Skill details, MCP server setup, example prompts, FAQ
- [**Getting Started**](skill-packs/klaviyo-skill-pack/GETTING_STARTED.md) — Step-by-step setup for each platform

## Security

All scripts include input validation, path sanitization, SSRF protection, and secure credential handling. API keys are stored in `.env` files (gitignored) and never hardcoded.

## License

MIT
