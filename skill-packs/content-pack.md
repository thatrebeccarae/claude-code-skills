<div align="center">

# Content Pack

**3 skills for SEO content, editorial pipelines, and client communication.**

[![GitHub stars](https://img.shields.io/github/stars/thatrebeccarae/dgtldept?style=for-the-badge&logo=github&color=181717)](https://github.com/thatrebeccarae/dgtldept/stargazers)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](../LICENSE)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Rebecca%20Rae%20Barton-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/rebeccaraebarton)
[![Substack](https://img.shields.io/badge/Substack-dgtl%20dept*-FF6719?style=for-the-badge&logo=substack&logoColor=white)](https://dgtldept.substack.com/welcome)

Research, write, review, and distribute — without switching tools.

[**Back to Repo**](../README.md)

</div>

---

## Who This Is For

- **Content marketers** producing blog posts, landing pages, and email campaigns on a regular cadence
- **Marketing agencies** writing content for multiple clients who each have a distinct brand voice
- **Solo operators** who need to move from idea to published piece without a full editorial team

## What's Included

| Skill | What It Does | Includes |
|-------|-------------|----------|
| **[seo-content-writer](../skills/seo-content-writer/)** | SEO-optimized content with brand voice analysis. Loads keyword research frameworks, on-page optimization checklists, and voice matching patterns. Produces drafts with target keyword placement, header structure, meta descriptions, and internal linking suggestions. | SKILL + REFERENCE + EXAMPLES |
| **[content-workflow](../skills/content-workflow/)** | End-to-end content pipeline: research → draft/editorial review → social distribution. Configurable stages with quality gates between each phase. | SKILL + REFERENCE + EXAMPLES |
| **[email-composer](../skills/email-composer/)** | Client outreach, deliverable handoffs, scope discussions, and follow-up sequences. Tone calibration adjusts formality based on context — cold outreach reads differently than a project update to an existing client. | SKILL + REFERENCE + EXAMPLES |

## How the Skills Connect

```
Content Workflow (pipeline orchestration)
    |
    +--> SEO Content Writer (drafting stage — blog, social, landing pages)
    |
    +--> Email Composer (distribution and outreach — promotion, follow-ups)
```

The pipeline orchestrates stages while the writing skills handle production. Use **Content Workflow** to structure the process, **SEO Content Writer** to produce the drafts, and **Email Composer** to handle outreach and follow-ups around published content. Each also works well on its own for one-off tasks.

## Quick Start

```bash
cd dgtldept
for skill in seo-content-writer content-workflow email-composer; do
  cp -r "skills/$skill" ~/.claude/skills/
done
```

No API keys required — all three skills work with text input and Claude's built-in knowledge.

## Example Prompts

### SEO Content Writer
- "Write a 1,500-word SEO article targeting 'email marketing benchmarks for DTC brands' with H2 headers and meta description"
- "Create a LinkedIn post about our new product launch — match our brand voice from these 5 sample posts"
- "Draft an email campaign for our spring sale — 3 emails, spaced 3 days apart"

### Content Workflow
- "Set up a content pipeline for our weekly blog: research → draft → review → publish"
- "Run the research stage for a piece on AI in email marketing"
- "Take this draft through editorial review and generate social distribution posts"

### Email Composer
- "Write a cold outreach email to a DTC brand founder about creative fatigue"
- "Draft a follow-up email for a client who hasn't responded in a week"
- "Write a scope change email — the client wants TikTok ads added at $2K/month"

## FAQ

<details>
<summary><strong>How is this different from just asking Claude to write?</strong></summary>

The SEO Content Writer skill loads keyword research frameworks, on-page optimization checklists, and brand voice analysis patterns that vanilla Claude doesn't have. The difference shows up in structure — proper header hierarchy, keyword placement, meta descriptions, internal linking suggestions — and in voice consistency across multiple pieces.

</details>

<details>
<summary><strong>Does this handle long-form SEO content?</strong></summary>

Yes. The SEO Content Writer produces content at any length with proper keyword density, header structure, and semantic markup. It works best when given a target keyword, audience context, and any brand voice examples.

</details>

<details>
<summary><strong>Are API keys needed?</strong></summary>

No. All three skills work with text input alone. No external API access, no MCP servers, no configuration beyond copying the skill files.

</details>

## License

MIT — see [LICENSE](../LICENSE) for details.
