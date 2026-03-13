<div align="center">

# Paid Media Pack

**6 skills for cross-platform paid media — Google Ads, Meta Ads, Microsoft Ads, competitive analysis, waste detection, and account structure review.**

[![GitHub stars](https://img.shields.io/github/stars/thatrebeccarae/dgtldept?style=for-the-badge&logo=github&color=181717)](https://github.com/thatrebeccarae/dgtldept/stargazers)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](../LICENSE)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Rebecca%20Rae%20Barton-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/rebeccaraebarton)
[![Substack](https://img.shields.io/badge/Substack-dgtl%20dept*-FF6719?style=for-the-badge&logo=substack&logoColor=white)](https://dgtldept.substack.com/welcome)

Cross-platform paid media expertise, on demand. Audit campaigns, find wasted spend, extract competitor creative from public ad libraries, and build consolidation roadmaps with migration plans.

[**Getting Started**](paid-media-getting-started.md) · [**Back to Repo**](../README.md)

</div>

---

## Who This Is For

- **Paid media managers** running $10K–$500K+/month across Google and Meta who need diagnostic depth beyond what platform dashboards surface
- **Agencies** managing multiple client accounts who want consistent audit methodology across platforms
- **In-house teams** evaluating account structure decisions — campaign consolidation, budget reallocation, platform expansion

## What's Included

| Skill | What It Does | Includes |
|-------|-------------|----------|
| **[google-ads](../skills/google-ads/)** | Full Google Ads audit: campaigns, keywords, Quality Scores, bidding, Performance Max, Shopping, conversion tracking. Industry benchmarks and GAQL query patterns. | SKILL + REFERENCE + EXAMPLES + .env |
| **[facebook-ads](../skills/facebook-ads/)** | Meta Ads audit: campaign structure, audiences, creative fatigue, pixel/CAPI health, iOS 14.5+ attribution, Advantage+ campaign readiness. | SKILL + REFERENCE + EXAMPLES + .env |
| **[microsoft-ads](../skills/microsoft-ads/)** | Microsoft Ads audit: Google import optimization, LinkedIn Profile Targeting, UET tracking, Shopping, Clarity integration. | SKILL + REFERENCE + EXAMPLES + .env |
| **[competitor-ads-analyst](../skills/competitor-ads-analyst/)** | Competitor ad creative analysis from public ad libraries (Meta Ad Library, Google Ads Transparency Center, LinkedIn). Messaging pattern tracking, creative format analysis, positioning gap identification. | SKILL + REFERENCE + EXAMPLES |
| **[wasted-spend-finder](../skills/wasted-spend-finder/)** | Systematic Google Ads and Meta waste analysis with statistical significance thresholds. Produces thematically categorized exclusion lists in uploadable CSV format. | SKILL + REFERENCE + EXAMPLES |
| **[account-structure-review](../skills/account-structure-review/)** | Cross-platform structural audit: conversion volume thresholds, budget fragmentation, targeting overlap, consolidation roadmaps with migration plans. | SKILL + REFERENCE + EXAMPLES |

## How the Skills Connect

```
Competitor Ads Analyst (what competitors are running)
    |
    +--> Google Ads (search, shopping, PMax, display, YouTube)
    |        |
    |        +--> Wasted Spend Finder (waste detection + exclusion lists)
    |
    +--> Microsoft Ads (import optimization, LinkedIn targeting)
    |
    +--> Meta Ads (prospecting, retargeting, Advantage+)
    |        |
    |        +--> Wasted Spend Finder (waste detection + exclusion lists)
    |
    +--> Account Structure Review (cross-platform structural health)
```

Start with **Competitor Ads Analyst** to understand competitor positioning, then audit individual platform accounts. Use **Wasted Spend Finder** to generate exclusion lists from the audit data, and **Account Structure Review** to evaluate whether the campaign architecture can sustain the budget.

## How This Is Different From Platform Tools

Platform-native optimization tools work within their own ecosystem. This skill pack gives Claude cross-platform diagnostic expertise — comparing Google Ads and Meta Ads structure simultaneously, identifying where budget fragmentation or audience overlap is costing money, extracting competitor intelligence from public ad libraries, and producing implementation-ready consolidation plans with migration roadmaps. Platform tools won't tell you that your Google and Meta campaigns are competing for the same audience, or that your account has too many campaigns for the conversion volume to support algorithmic optimization.

## Quick Start

### Option 1: Interactive Wizard (Recommended)

```bash
git clone https://github.com/thatrebeccarae/dgtldept.git
cd dgtldept
python skill-packs/scripts/setup-paid-media.py
```

The wizard checks prerequisites, walks through API key setup, installs dependencies, and tests connections.

### Option 2: Copy Skills Directly

```bash
cd dgtldept
for skill in google-ads facebook-ads microsoft-ads competitor-ads-analyst wasted-spend-finder account-structure-review; do
  cp -r "skills/$skill" ~/.claude/skills/
done
```

> [!TIP]
> See [paid-media-getting-started.md](paid-media-getting-started.md) for detailed step-by-step instructions and API key setup per platform.

## Example Prompts

### Google Ads
- "Audit my Google Ads account and find wasted spend"
- "My Quality Scores are low — help me diagnose and fix"
- "Design a Performance Max campaign structure for my ecommerce store"

### Meta Ads (Facebook & Instagram)
- "Audit my Facebook Ads account performance"
- "My ROAS is declining — what should I investigate?"
- "Help me set up Conversions API (CAPI)"
- "Design a creative testing framework for my brand"

### Microsoft Ads
- "My Google Ads import isn't performing well on Microsoft — what should I change?"
- "Help me set up LinkedIn Profile Targeting for B2B"
- "Audit my Microsoft Ads account structure"

### Competitor Ads Analyst
- "Pull competitor ads from Meta Ad Library for these 3 brands and find messaging gaps"
- "What creative formats are our top competitors running on LinkedIn?"
- "Analyze competitor messaging patterns and identify positioning opportunities"

### Wasted Spend Finder
- "Analyze my Google Ads search terms and categorize wasted spend"
- "Generate negative keyword exclusion lists I can upload directly to Google Ads"
- "Find statistical outliers in my Meta ad set spending"

### Account Structure Review
- "Audit my Google + Meta account structure and identify consolidation opportunities"
- "My campaigns keep re-entering learning phase — is my structure the problem?"
- "What's the right campaign structure for a $50K/month budget?"

## FAQ

<details>
<summary><strong>Do all six skills need to be installed together?</strong></summary>

No. Install only the skills for platforms you manage. If you only run Google Ads and Meta Ads, install those two plus Wasted Spend Finder and Account Structure Review for cross-platform analysis. Competitor Ads Analyst works independently of the platform skills.

</details>

<details>
<summary><strong>What API access is needed?</strong></summary>

Each platform skill needs its own API credentials for automated data pulling. See [paid-media-getting-started.md](paid-media-getting-started.md) for step-by-step setup. Most skills work with read-only access. Account Structure Review, Competitor Ads Analyst, and Wasted Spend Finder need no API access — they work with pasted data, screenshots, or exported CSVs.

</details>

<details>
<summary><strong>Can these skills work without API keys?</strong></summary>

Yes. Claude still has full platform expertise without API access — the skills load diagnostic frameworks, industry benchmarks, and optimization patterns regardless. You'll need to provide data manually (paste metrics, share screenshots, export CSVs). API keys enable the included scripts to pull data automatically.

</details>

## Resources

- [Google Ads API Documentation](https://developers.google.com/google-ads/api/docs/start)
- [Meta Marketing API Documentation](https://developers.facebook.com/docs/marketing-apis/)
- [Microsoft Advertising API Documentation](https://learn.microsoft.com/en-us/advertising/guides/get-started)
- [Meta Ad Library](https://www.facebook.com/ads/library/)
- [Google Ads Transparency Center](https://adstransparency.google.com/)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)

## License

MIT — see [LICENSE](../LICENSE) for details.
