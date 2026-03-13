---
name: content-workflow
description: "End-to-end content creation pipeline from research through editorial review to social distribution. Orchestrates a 3-stage workflow: research, draft/edit, and distribute. Supports blog posts, LinkedIn, Twitter threads, newsletters, and essays."
license: MIT
origin: custom
author: Rebecca Rae Barton
author_url: https://github.com/thatrebeccarae
metadata:
  version: 1.0.0
  category: content
  domain: workflow
  updated: 2026-03-13
---

# Content Workflow

End-to-end content creation pipeline: research, draft, review, distribute.

## Pipeline Stages

### Stage 1: Research

Gather raw material for the content piece.

1. **Topic research** — web search, RSS feeds, industry sources
2. **Source assessment** — credibility, recency, relevance
3. **Data extraction** — key statistics, quotes, data points
4. **Counter-arguments** — opposing views, nuance, caveats
5. **Angle development** — what makes this piece unique

**Output:** Research brief with sources, data points, and recommended angle.

### Stage 2: Draft & Edit

Create and refine the content.

1. **Draft** — write following the content type framework and brand voice
2. **Editorial review** against quality criteria:
   - Voice consistency
   - Structural quality (hook → body → CTA)
   - SEO optimization (if applicable)
   - Factual accuracy (all claims sourced)
   - Readability (appropriate level for audience)
3. **Revision** — apply specific feedback
4. **Final review** — verify all issues addressed

**Output:** Polished draft ready for approval.

### Stage 3: Distribute

Adapt the finished piece for cross-platform distribution.

1. **LinkedIn post** — hook, body, CTA, hashtags
2. **Twitter/X thread** — numbered tweets, hooks per tweet
3. **Email subject lines** — 3 options with preview text
4. **Pull quotes** — 3-5 shareable excerpts for social

**Output:** Distribution pack with platform-specific adaptations.

## Usage Modes

### Full Pipeline

```
/content-workflow [topic]
```

Runs all 3 stages: research → draft → review → distribute.

### Start from Draft

```
/content-workflow --from-draft [file path]
```

Skips research. Takes an existing draft through editorial review and distribution.

### Distribution Only

```
/content-workflow --distribute [file path]
```

Takes a finished, approved piece and creates the social distribution pack.

## Content Types

| Type | Research Depth | Draft Length | Distribution |
|------|---------------|-------------|--------------|
| Blog post | Deep (5+ sources) | 1,500-2,500 words | LinkedIn + Twitter + Email |
| LinkedIn post | Light (2-3 sources) | 150-300 words | Twitter adaptation only |
| Twitter thread | Light (1-2 sources) | 5-12 tweets | LinkedIn adaptation only |
| Newsletter | Medium (3-5 sources) | 500-1,000 words | Twitter + LinkedIn teasers |
| Essay | Deep (8+ sources) | 2,000-4,000 words | Full distribution pack |

## Status Tracking

Content moves through these statuses:

```
stub → draft → reviewed → approved → published → measured
                                   ↘ rejected (terminal)
```

- **stub:** Topic identified, no content yet
- **draft:** First draft complete
- **reviewed:** Editorial review complete
- **approved:** Human approval gate passed
- **published:** Live on platform
- **measured:** Performance data collected
- **rejected:** Did not pass review, will not publish

## Key Principles

1. **Research before writing.** Even short posts benefit from 10 minutes of source gathering.
2. **One piece, many platforms.** Write once, adapt to each platform's format.
3. **Human approval gate.** Never publish without explicit approval.
4. **Measure everything.** Track performance to inform future content decisions.

For editorial review criteria and platform templates, see [REFERENCE.md](REFERENCE.md).
