# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-03-09

### Added

- **Analytics Agents** — autonomous GA4 monitoring + GTM implementation pipeline (`agent-workflows/analytics-agents/`)
  - Daily GA4 event monitoring with tracking spec comparison
  - Claude Sonnet gap analysis with GTM implementation recommendations
  - Claude Haiku anomaly detection for event volume drops/spikes
  - Rate-limited, idempotent GTM tag/trigger/variable creation in isolated workspaces
  - Slack notifications at every pipeline stage
  - Multi-tenant design (one pipeline, multiple GA4 properties)
  - JSON schemas for client config and event spec validation
  - Comprehensive getting-started guide for non-technical users
- New top-level `agent-workflows/` category for autonomous n8n + Claude pipelines

### Changed

- Repositioned dgtldept from "Claude Code skills" to a broader toolkit: skills, agent workflows, and automation pipelines for solo marketers and small teams
- Updated root README with new positioning, "What's Inside" overview, and Agent Workflows section
- Private development repo (`dgtldept-dev`) with `sync-public.sh` for PII-safe downstream sync

### Removed

- LinkedIn Data Viz (moved to [linkedin-toolkit](https://github.com/thatrebeccarae/linkedin-toolkit))

## [1.0.0] - 2026-02-23

### Added

- **DTC Skill Pack** — 6 production-tested skills for e-commerce marketing
  - Klaviyo Analyst: 4-phase account audit, flow gap analysis, segment health, deliverability diagnostics, revenue attribution
  - Klaviyo Developer: Event schema design, SDK integration, webhook handling, rate limit strategy, catalog sync
  - Shopify: 12-step store audit, conversion funnel analysis, site speed diagnostics
  - Google Analytics: GA4 traffic analysis, channel comparison, conversion funnels
  - Looker Studio: Cross-platform dashboards via Google Sheets pipeline, DTC templates
  - Pro Deck Builder: Polished HTML slide decks and PDF-ready reports
- **LinkedIn Data Viz** — 9 interactive visualizations from LinkedIn data exports (D3.js, Chart.js)
- Interactive setup wizard with API key validation and health checks
- Live demos for [DTC Skill Pack](https://thatrebeccarae.github.io/dgtldept/skill-packs/dtc-skill-pack/demo/) and [LinkedIn Data Viz](https://thatrebeccarae.github.io/dgtldept/skills/linkedin-data-viz/demo/)
- SECURITY.md, CONTRIBUTING.md, and GitHub issue/PR templates
