---
name: github-readme
description: "Generate, audit, or update GitHub READMEs. Three modes: generate (new), audit (check existing), update (patch). Detects repo type (library/CLI/app/API/monorepo), selects appropriate badges, and generates sections following conventions for the detected type."
license: MIT
origin: custom
author: Rebecca Rae Barton
author_url: https://github.com/thatrebeccarae
metadata:
  version: 1.0.0
  category: dev-tools
  domain: github
  updated: 2026-03-13
---

# GitHub README Generator

Generate, audit, or update GitHub READMEs against a standard template. Detects repo type and adapts structure accordingly.

## Modes

### 1. Generate (New README)

Create a README from scratch by analyzing the repo.

**Steps:**
1. Detect repo type (library, CLI tool, web app, API, monorepo, skill pack)
2. Read package.json/pyproject.toml/Cargo.toml for metadata
3. Scan directory structure for key patterns
4. Select badge set based on repo type and detected CI/tooling
5. Generate sections appropriate to repo type
6. Write README.md

### 2. Audit (Check Existing)

Evaluate an existing README for completeness and quality.

**Checks:**
- All required sections present for the repo type
- Badge URLs resolve (not broken)
- Version numbers are current
- Install commands work
- Code examples are syntactically valid
- Links are not broken
- No placeholder text remaining
- PII/infrastructure scrub (no internal IPs, hostnames, credentials)

**Output:** Score (0-100) + findings report with specific fix recommendations.

### 3. Update (Patch Existing)

Modify an existing README while preserving its structure.

**Steps:**
1. Read current README
2. Identify sections and their content
3. Plan changes (add missing sections, update stale content)
4. Show diff-style preview
5. Apply updates on approval

## Repo Type Detection

| Signal | Type |
|--------|------|
| `src/` + `package.json` with `main`/`exports` | Library |
| `bin` field in package.json or CLI entry point | CLI Tool |
| `app/` or `pages/` directory, framework config | Web App |
| `routes/` or OpenAPI spec | API |
| `packages/` or workspace config | Monorepo |
| `skills/` with SKILL.md files | Skill Pack |

## Section Order by Type

### Library
1. Title + badges
2. One-line description
3. Features
4. Installation
5. Quick Start
6. API Reference
7. Configuration
8. Contributing
9. License

### CLI Tool
1. Title + badges
2. One-line description
3. Installation (brew, npm, cargo, etc.)
4. Quick Start
5. Commands reference
6. Configuration
7. Contributing
8. License

### Web App
1. Title + badges
2. One-line description
3. Screenshots/demo
4. Features
5. Getting Started (prerequisites, install, run)
6. Environment Variables
7. Deployment
8. Contributing
9. License

### API
1. Title + badges
2. One-line description
3. Base URL + authentication
4. Quick Start
5. Endpoints reference
6. Error handling
7. Rate limits
8. Contributing
9. License

## Badge Selection

| Badge | When to Include |
|-------|----------------|
| Build/CI status | CI config detected (.github/workflows/) |
| Coverage | Coverage config detected (codecov, coveralls) |
| npm version | package.json with npm publish |
| PyPI version | pyproject.toml with PyPI config |
| License | Always |
| Node/Python version | When runtime version matters |
| TypeScript | tsconfig.json present |
| Docker | Dockerfile present |

## Key Principles

1. **Lead with what it does.** First sentence should explain the tool in one line.
2. **Show, don't tell.** Code examples > descriptions.
3. **Install command must work.** Test it mentally — does it reference the right package name?
4. **No placeholder text.** Every `TODO`, `YOUR_`, `CHANGEME` must be resolved.
5. **No stale badges.** Remove badges for services not configured.

## Anti-Patterns

- Walls of text without code examples
- Broken badge URLs or badges for unconfigured services
- Generic descriptions ("A tool for doing things")
- Missing install instructions
- Stale version numbers in examples
- Internal URLs, IPs, or credentials in examples
- Placeholder text left in ("TODO", "Add description here")

For badge URL patterns and section templates, see [REFERENCE.md](REFERENCE.md).
