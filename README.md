<div align="center">

# dgtl dept*

**A full marketing department for Claude Code.** Klaviyo, Shopify, GA4, Looker Studio, paid media, content strategy — install the skills you need and get expert-level analysis from your terminal.

[![Substack](https://img.shields.io/badge/Substack-dgtl%20dept*-5865F2?style=for-the-badge&logo=substack&logoColor=white)](https://dgtldept.substack.com/welcome)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Rebecca%20Rae%20Barton-007EC6?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/rebeccaraebarton)
[![X](https://img.shields.io/badge/X-@rebeccarae-000000?style=for-the-badge&logo=x&logoColor=white)](https://x.com/rebeccarae)
[![Website](https://img.shields.io/badge/rebeccaraebarton.com-1C1C1C?style=for-the-badge&logo=google-chrome&logoColor=white)](https://rebeccaraebarton.com)
[![GitHub stars](https://img.shields.io/github/stars/thatrebeccarae/dgtldept?style=for-the-badge&logo=github&color=181717)](https://github.com/thatrebeccarae/dgtldept/stargazers)
[![License](https://img.shields.io/badge/License-MIT-007EC6?style=for-the-badge)](LICENSE)
[![Clone](https://img.shields.io/badge/Clone-git%20clone-f78166?style=for-the-badge&logo=git&logoColor=white)](https://github.com/thatrebeccarae/dgtldept)

<br>

```bash
git clone https://github.com/thatrebeccarae/dgtldept.git
```

<br>

**Works on Mac, Windows, and Linux.**

<br>

<br>

<a href="https://thatrebeccarae.github.io/dgtldept/skill-packs/dtc-skill-pack/demo/">
  <img src="assets/terminal.svg" alt="dgtl dept skill pack installation" width="760">
</a>

<!--
### What people are saying

> "Quote here" — **Name**, Role at Company

> "Quote here" — **Name**, Role at Company

> "Quote here" — **Name**, Role at Company
-->

<br>
<br>

[Why I Built This](#why-i-built-this) · [Who This Is For](#who-this-is-for) · [Getting Started](#getting-started) · [How It Works](#how-it-works) · [Skill Packs](#skill-packs) · [Contributing](CONTRIBUTING.md)

</div>

---

## Why I Built This

Most marketing teams are either too small or too stretched. You need a Klaviyo specialist, a GA4 analyst, a Shopify conversion expert, a dashboard builder, a paid media strategist — but you've got maybe one or two people doing all of it.

Claude Code is powerful out of the box, but it doesn't know that a 1.2% click rate on your welcome series is below benchmark, or that your Shopify checkout completion rate signals a shipping cost surprise. It gives structurally correct answers that miss the domain context entirely.

**dgtl dept fixes that.** Each skill pack gives Claude the same benchmarks, diagnostic frameworks, and platform expertise that a senior marketing consultant brings to an engagement. Install the department you need, ask in plain English, get implementation-ready answers.

## Who This Is For

- **Solo marketers and small teams** who need specialist depth without specialist headcount
- **DTC and e-commerce operators** running Klaviyo, Shopify, GA4, or Looker Studio
- **Growth teams** that need cross-platform analysis, not platform-by-platform reports
- **Agencies and consultants** who want to scale their diagnostic process
- **Founders** who are tired of paying for audits they could run themselves

If you want implementation-ready answers — not tutorials, not blog-post-level overviews — this is your department.

## Getting Started

### Setup Wizard (Recommended)

```bash
git clone https://github.com/thatrebeccarae/dgtldept.git
cd dgtldept/skill-packs/dtc-skill-pack
python scripts/setup.py
```

The wizard checks prerequisites, walks you through API key setup, installs dependencies, and tests connections.

> [!TIP]
> The setup wizard validates API keys as you enter them and tests live connections before finishing. If something is misconfigured, it tells you exactly what to fix.

<details>
<summary><strong>Manual install (skip the wizard)</strong></summary>

```bash
# Copy all 6 skills to Claude Code
for skill in klaviyo-analyst klaviyo-developer google-analytics shopify looker-studio pro-deck-builder; do
  cp -r dgtldept/skill-packs/dtc-skill-pack/$skill ~/.claude/skills/
done
```

See [GETTING_STARTED.md](skill-packs/dtc-skill-pack/GETTING_STARTED.md) for detailed API key setup per platform.

</details>

<details>
<summary><strong>LinkedIn Data Viz install</strong></summary>

```bash
git clone https://github.com/thatrebeccarae/dgtldept.git
cp -r dgtldept/skills/linkedin-data-viz ~/.claude/skills/
```

Then say: **"Analyze my LinkedIn data export"**

</details>

## How It Works

Claude Code skills are structured knowledge packs that load automatically when you invoke them. Each skill gives Claude specific domain expertise it doesn't have out of the box.

### What a Skill Contains

| File | Purpose |
|------|---------|
| **SKILL.md** | Frontmatter + instructions Claude reads at invocation — frameworks, decision trees, diagnostic patterns |
| **REFERENCE.md** | Platform-specific data: industry benchmarks, API schemas, field mappings, rate limits |
| **EXAMPLES.md** | Working examples with realistic prompts and expected output format |
| **scripts/** | Utility scripts for setup, data fetching, health checks (where applicable) |

### How Claude Uses Them

1. You ask a question in natural language (e.g., *"Audit my Klaviyo flows"*)
2. Claude loads the relevant skill's SKILL.md, which contains the diagnostic framework
3. Claude references REFERENCE.md for benchmarks, thresholds, and platform-specific data
4. If an MCP server is configured (e.g., Klaviyo), Claude pulls live data from your account
5. Claude delivers structured analysis with specific recommendations — not generic advice

> [!NOTE]
> Skills work without MCP servers too. You can paste data, share screenshots, or use the included scripts to export data manually. The MCP server just makes it seamless.

## Skill Packs

### [DTC Skill Pack](skill-packs/dtc-skill-pack/) — 6 skills for e-commerce marketing

> [**View Live Demo**](https://thatrebeccarae.github.io/dgtldept/skill-packs/dtc-skill-pack/demo/) — See all 6 skills in action with example terminal output.

| Skill | What Claude Can Do |
|-------|-------------------|
| **[Klaviyo Analyst](skill-packs/dtc-skill-pack/klaviyo-analyst/)** | 4-phase account audit, flow gap analysis, segment health, deliverability diagnostics, revenue attribution, three-tier recommendations with implementation specs |
| **[Klaviyo Developer](skill-packs/dtc-skill-pack/klaviyo-developer/)** | Event schema design, SDK integration, webhook handling, rate limit strategy, catalog sync, integration health audit |
| **[Shopify](skill-packs/dtc-skill-pack/shopify/)** | 12-step store audit, conversion funnel analysis, site speed diagnostics, marketing stack integration |
| **[Google Analytics](skill-packs/dtc-skill-pack/google-analytics/)** | GA4 traffic analysis, channel comparison, conversion funnels, content performance |
| **[Looker Studio](skill-packs/dtc-skill-pack/looker-studio/)** | Cross-platform dashboards via Google Sheets pipeline, DTC dashboard templates, calculated field library |
| **[Pro Deck Builder](skill-packs/dtc-skill-pack/pro-deck-builder/)** | Polished HTML slide decks and PDF-ready reports with dark cover pages and warm light content slides |

### [LinkedIn Data Viz](skills/linkedin-data-viz/) — Interactive career visualizations

> [**View Live Demo**](https://thatrebeccarae.github.io/dgtldept/skills/linkedin-data-viz/demo/)

Turn a LinkedIn data export into 9 interactive visualizations: D3.js network graphs, Chart.js charts, career timelines. Includes onboarding wizard, dark theme, and privacy-safe sanitization for publishing.

### Coming Soon

The department is growing. Skill packs for Google Ads, Meta Ads, content strategy, and multi-channel attribution are in development. [Star the repo](https://github.com/thatrebeccarae/dgtldept/stargazers) to get notified when they drop.

## Example Prompts

```
"Audit my Klaviyo flows and identify which essential flows I'm missing"

"My checkout completion rate is 31% — what's causing the drop-off?"

"Which traffic sources are driving the most conversions this month?"

"Plan a CRM dashboard reconciling Klaviyo and Shopify data"

"Create a dark-mode deck summarizing this month's email performance"

"Debug why my webhook events aren't triggering flows"
```

## Configuration

### Setup Wizard Options

| Flag | What It Does |
|------|-------------|
| `python scripts/setup.py` | Full interactive setup |
| `--skip-install` | Skip dependency installation |
| `--skills klaviyo,shopify` | Install specific skills only |
| `--non-interactive` | Use environment variables, skip prompts |

### API Keys by Platform

| Platform | Key Required | Where to Get It |
|----------|-------------|-----------------|
| **Klaviyo** | Private API Key (`pk_...`) | Klaviyo > Settings > API Keys |
| **Google Analytics** | Service account JSON + Property ID | Google Cloud Console > IAM > Service Accounts |
| **Shopify** | Admin API access token | Shopify Admin > Apps > Develop Apps |
| **Looker Studio** | Google Sheets API credentials | Google Cloud Console > APIs & Services |

> [!IMPORTANT]
> API keys are stored in `.env` files which are gitignored by default. Never hardcode keys in skill files or commit them to version control. See [SECURITY.md](SECURITY.md) for full credential handling guidance.

<details>
<summary><strong>Klaviyo MCP server setup</strong></summary>

The [Klaviyo MCP server](https://developers.klaviyo.com/en/docs/klaviyo_mcp_server) gives Claude direct access to your Klaviyo account data.

1. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Add to `~/.mcp.json`:

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

3. Restart Claude Code and verify with `/mcp`

See the [DTC Skill Pack README](skill-packs/dtc-skill-pack/README.md) for recommended Klaviyo API scopes.

</details>

## Security

All scripts include input validation, path sanitization, SSRF protection, and secure credential handling. Key principles:

- **API keys** stored in `.env` files (gitignored), never hardcoded
- **Read-only API access** by default — write scopes are opt-in
- **No PII extraction** — skills work with aggregates, not individual customer data
- **No persistent storage** — analysis runs in-memory, output goes to local files you control

For vulnerability reporting and full security design details, see [SECURITY.md](SECURITY.md).

## Troubleshooting

<details>
<summary><strong>Skills not loading in Claude Code</strong></summary>

1. Verify skills are in the right directory: `ls ~/.claude/skills/`
2. Each skill folder should contain at least a `SKILL.md` file
3. Restart Claude Code after copying skills
4. Check that SKILL.md frontmatter is valid YAML

</details>

<details>
<summary><strong>API key errors</strong></summary>

1. Confirm your `.env` file is in the project root (not inside a skill folder)
2. Klaviyo keys must start with `pk_` — if yours doesn't, you may have copied a public key
3. Google service account JSON path must be absolute, not relative
4. Run `python scripts/setup.py` to re-validate all keys

</details>

<details>
<summary><strong>Python version issues</strong></summary>

The setup wizard requires Python 3.8+. Check your version:

```bash
python --version
# or
python3 --version
```

On macOS, `python` may point to Python 2. Use `python3` explicitly or install via Homebrew: `brew install python`

</details>

<details>
<summary><strong>MCP server not connecting</strong></summary>

1. Verify `~/.mcp.json` syntax is valid JSON (no trailing commas)
2. Confirm `uv` is installed: `uv --version`
3. Check that your `KLAVIYO_API_KEY` environment variable is set: `echo $KLAVIYO_API_KEY`
4. Restart Claude Code — MCP servers load at startup

</details>

## Documentation

| Resource | Description |
|----------|-------------|
| [DTC Skill Pack README](skill-packs/dtc-skill-pack/README.md) | Skill details, architecture, MCP server setup, example prompts, FAQ |
| [DTC Getting Started](skill-packs/dtc-skill-pack/GETTING_STARTED.md) | Step-by-step setup for each platform |
| [LinkedIn Data Viz SKILL.md](skills/linkedin-data-viz/SKILL.md) | Wizard flow, visualization descriptions |
| [LinkedIn Data Viz REFERENCE.md](skills/linkedin-data-viz/REFERENCE.md) | CSV schemas, parsing quirks, theme customization |
| [CHANGELOG](CHANGELOG.md) | Version history and release notes |
| [SECURITY](SECURITY.md) | Security design and vulnerability reporting |
| [CONTRIBUTING](CONTRIBUTING.md) | How to contribute skills, report bugs, submit PRs |

## Contributing

Contributions are welcome — bug reports, documentation fixes, skill suggestions, and new skills. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting skills, the required file structure, and the PR process.

## License

MIT License. See [LICENSE](LICENSE) for details.

<div align="center">

---

**Your marketing department lives here now.**<br>Install the skills. Ask in plain English. Get answers that actually know your stack.

</div>
