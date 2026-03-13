# Contributing

Thanks for your interest in contributing to dgtl dept*. Whether it's a bug report, a new skill idea, or a documentation improvement — it all helps.

## What We're Looking For

- **Bug reports** — something broken? [Open an issue](https://github.com/thatrebeccarae/dgtldept/issues/new?template=bug_report.md)
- **Skill suggestions** — ideas for new skills or improvements to existing ones
- **Documentation fixes** — typos, unclear instructions, missing steps
- **New skills** — production-tested skills for marketing platforms, analytics, or data visualization

## Getting Started

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/dgtldept.git
   cd dgtldept
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-skill-name
   ```

## Submitting a Skill

Every skill needs at minimum:

| File | Purpose |
|------|---------|
| `SKILL.md` | Frontmatter + instructions Claude reads at invocation |
| `REFERENCE.md` | Platform-specific reference data (benchmarks, API schemas, field mappings) |
| `EXAMPLES.md` | Working examples with realistic prompts and expected output |

### SKILL.md Frontmatter

```yaml
---
name: your-skill-name
description: "One-line description of what the skill does"
license: MIT
origin: custom
author: Your Name
author_url: https://github.com/your-username
metadata:
  version: 1.0.0
  category: paid-media | dtc | content | strategy | creative | reporting | dev-tools
  domain: the-platform-or-focus-area
  updated: YYYY-MM-DD
---
```

### Quality Checklist

Before submitting, verify:

- [ ] Skill has been tested with Claude Code (not just written — actually used)
- [ ] REFERENCE.md contains real benchmarks, schemas, or platform data
- [ ] EXAMPLES.md prompts produce useful, accurate output
- [ ] No API keys, secrets, or PII in any files
- [ ] Scripts include input validation and error handling
- [ ] Works without MCP servers (graceful degradation if no live API access)

## Pull Request Process

1. **Branch naming:** `feature/skill-name`, `fix/issue-description`, or `docs/what-changed`
2. **Keep PRs focused** — one skill or one fix per PR
3. **Fill out the PR template** — it's short, and it helps review go faster
4. **Test your changes** — run the skill with Claude Code and confirm the output makes sense

PRs are reviewed within a week. If your skill needs iteration, you'll get specific feedback on what to adjust.

## Style Guide

### Skill Naming

- Lowercase, hyphenated: `klaviyo-analyst`, `google-analytics`, `pro-deck-builder`
- Name describes the platform or capability, not the implementation

### Documentation

- Write for someone who knows their platform but is new to Claude Code skills
- Be specific — "click the gear icon" beats "go to settings"
- Include real numbers in benchmarks (with sources or date ranges)

### Scripts

- Python 3.8+ compatible
- Include input validation for file paths, API keys, and user input
- Use `argparse` for CLI scripts
- Follow the existing patterns in `scripts/` directories

## Code of Conduct

Be kind. Be constructive. Assume good intent.

This is a small project. We don't need a 2,000-word conduct policy to treat each other well. If you're here to help people do better marketing with better tools, you're welcome.

If someone's behavior makes contributing feel unwelcome, email **security@rebeccaraebarton.com** and it'll be handled directly.
