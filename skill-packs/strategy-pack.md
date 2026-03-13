<div align="center">

# Strategy & Research Pack

**3 skills for market research, ICP development, and research synthesis.**

[![GitHub stars](https://img.shields.io/github/stars/thatrebeccarae/dgtldept?style=for-the-badge&logo=github&color=181717)](https://github.com/thatrebeccarae/dgtldept/stargazers)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](../LICENSE)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Rebecca%20Rae%20Barton-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/rebeccaraebarton)
[![Substack](https://img.shields.io/badge/Substack-dgtl%20dept*-FF6719?style=for-the-badge&logo=substack&logoColor=white)](https://dgtldept.substack.com/welcome)

The research team you don't have, available on demand.

[**Back to Repo**](../README.md)

</div>

---

## Who This Is For

- **Consultants** building pitch decks and competitive analyses for client engagements
- **Founders** validating market size, mapping competitors, or preparing investor materials
- **Marketing strategists** who need buyer personas grounded in real community research, not assumptions

## What's Included

| Skill | What It Does | Includes |
|-------|-------------|----------|
| **[market-research](../skills/market-research/)** | Consulting-grade market research reports (50+ pages) with LaTeX formatting. Includes Porter's Five Forces, PESTLE, SWOT, TAM/SAM/SOM analysis, and competitive positioning matrices. | SKILL + REFERENCE + EXAMPLES |
| **[icp-research](../skills/icp-research/)** | ICP development using community research (Reddit, forums, LinkedIn), pain point scoring matrices, buying trigger analysis, objection mapping, and voice-of-customer extraction. Output includes real community excerpts and channel-level recommendations. | SKILL + REFERENCE + EXAMPLES |
| **[research-digest](../skills/research-digest/)** | Structured research briefs from RSS feeds and web sources. Source credibility framework, multi-source synthesis, and content angle identification. | SKILL + REFERENCE + EXAMPLES |

## How the Skills Connect

```
Research Digest (source monitoring and synthesis)
    |
    +--> Market Research (deep analysis and strategic frameworks)
    |
    +--> ICP Research (buyer personas and targeting)
```

**Research Digest** monitors and synthesizes sources. Those findings feed into **Market Research** for deep strategic analysis or into **ICP Research** for buyer persona development. **Market Research** and **ICP Research** also complement each other — build buyer personas first, then validate positioning against the competitive landscape.

## Quick Start

```bash
cd dgtldept
for skill in market-research icp-research research-digest; do
  cp -r "skills/$skill" ~/.claude/skills/
done
```

No API keys required for core functionality. Research Digest benefits from RSS feed access but works with web search alone.

## Example Prompts

### Market Research
- "Generate a market research report on the project management SaaS space"
- "Run a full Porter's Five Forces and SWOT analysis for a DTC supplement brand entering the EU market"
- "Run a competitive analysis of Klaviyo vs. Mailchimp vs. Braze for mid-market DTC"
- "What's the TAM/SAM/SOM for AI-powered marketing analytics?"

### ICP Research
- "Build an ICP for our SaaS product targeting VP of Marketing at mid-market companies"
- "Research where our target buyers hang out online — communities, forums, podcasts"
- "Map the buying triggers and objections for enterprise security software"

### Research Digest
- "Generate a research brief on AI in email marketing from the last 30 days"
- "Synthesize the latest trends in DTC retention marketing"
- "Build a research digest on privacy regulation changes affecting ad targeting"

## FAQ

<details>
<summary><strong>Can Market Research replace a consulting engagement?</strong></summary>

It depends on what you need. For desk research, competitive analysis, and strategic framework application, it covers the same ground as a junior analyst doing secondary research. For primary research (interviews, surveys, proprietary data), you still need human researchers. The skill is strongest when paired with real data or used to structure and accelerate existing research.

</details>

<details>
<summary><strong>Where does ICP Research pull community data from?</strong></summary>

The skill structures research across Reddit, industry forums, LinkedIn, and other public communities. It extracts voice-of-customer language, recurring pain points, and buying triggers from real conversations — then scores and prioritizes them. The output reads like a strategy document, not a scrape dump.

</details>

<details>
<summary><strong>Are API keys needed?</strong></summary>

No. All three skills work with web search and text input. Research Digest can optionally pull from RSS feeds if an RSS reader is available, but it's not required.

</details>

## License

MIT — see [LICENSE](../LICENSE) for details.
