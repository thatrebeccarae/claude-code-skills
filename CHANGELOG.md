# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.3.0] - 2026-03-13

### Added

- **14 new skills** across 5 categories:
  - **Content**: SEO Content Writer, Content Workflow, Email Composer
  - **Strategy & Research**: Market Research, ICP Research, Research Digest
  - **Creative & Design**: Frontend Design, Tech Diagram, Remotion Video
  - **Reporting & Deliverables**: HTML Report Builder
  - **Developer Tools**: Safe Push, GitHub README
  - **Paid Media**: Competitor Ads Analyst, Wasted Spend Finder
- **4 new skill packs** with pack-specific taglines, "Who This Is For" sections, and FAQ:
  - Content Pack (3 skills)
  - Strategy & Research Pack (3 skills)
  - Creative & Design Pack (3 skills)
  - Developer Tools Pack (2 skills)

### Changed

- **Paid Media Pack** expanded from 4 to 6 skills (added Competitor Ads Analyst, Wasted Spend Finder)
- **README rewritten**: 7 category tables, Claude Code definition for first-time visitors, "Why This Exists" replacing first-person "Why I Built This," heading hierarchy fixes, nav updated
- **Skill Packs section** promoted to H2, "How It Works > Skill Packs" renamed to "How Skills Work" with AEO-ready skill definition
- CONTRIBUTING.md frontmatter example updated to match actual SKILL.md schema
- Total skill count: 11 → 25
- Total skill packs: 2 → 6

## [1.2.0] - 2026-03-11

### Added

- **Paid Media Pack** — 4 skills for paid advertising (`skill-packs/paid-media-pack.md`)
  - Google Ads: Campaign auditing, Quality Score optimization, PMax, Shopping, bidding strategies, GAQL queries
  - Meta Ads (Facebook & Instagram): Account audit, creative fatigue diagnosis, pixel/CAPI health, Advantage+ evaluation, iOS 14.5+ attribution
  - Microsoft Ads (Bing): Google import optimization, LinkedIn Profile Targeting, UET tracking, Shopping campaigns, Clarity integration
  - Account Structure Review: Cross-platform structural audit with conversion volume thresholds, budget fragmentation analysis, targeting overlap detection, consolidation roadmaps
- **Braze** — Standalone skill for Braze customer engagement (`skills/braze/`)
  - Canvas audit, segmentation review, cross-channel orchestration, data architecture, deliverability and IP warming
- Interactive setup wizard for Paid Media Pack (`skill-packs/scripts/setup-paid-media.py`)
- Getting started guide for paid media platforms (`skill-packs/paid-media-getting-started.md`)

### Changed

- **Restructured repo layout**: flat `skills/` for all 11 individual skills, `skill-packs/` for curated collection docs and setup wizards, `agents/` for standalone agent logic, `workflows/` for n8n orchestration
- Extracted 3 standalone agents from analytics-agents workflow: GA4 Monitor, GA4 Gap Analyzer, GTM Implementer — each usable independently without n8n
- Renamed `workflows/analytics-agents/` → `workflows/ga4-gtm-pipeline/` for platform-clear naming
- Updated root README with Paid Media Pack in "What's Inside" table and new "Skill Packs" section
- Updated "Coming Soon" — Google Ads and Meta Ads are now shipped

## [1.1.0] - 2026-03-09

### Added

- **Analytics Agents** — autonomous GA4 monitoring + GTM implementation pipeline (`workflows/analytics-agents/`)
  - Daily GA4 event monitoring with tracking spec comparison
  - Claude Sonnet gap analysis with GTM implementation recommendations
  - Claude Haiku anomaly detection for event volume drops/spikes
  - Rate-limited, idempotent GTM tag/trigger/variable creation in isolated workspaces
  - Slack notifications at every pipeline stage
  - Multi-tenant design (one pipeline, multiple GA4 properties)
  - JSON schemas for client config and event spec validation
  - Comprehensive getting-started guide for non-technical users
- New top-level `workflows/` category for autonomous n8n + Claude pipelines

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
- Live demos for [DTC Skill Pack](https://thatrebeccarae.github.io/dgtldept/skills/dtc-skill-pack/demo/) and [LinkedIn Data Viz](https://thatrebeccarae.github.io/dgtldept/skills/linkedin-data-viz/demo/)
- SECURITY.md, CONTRIBUTING.md, and GitHub issue/PR templates
