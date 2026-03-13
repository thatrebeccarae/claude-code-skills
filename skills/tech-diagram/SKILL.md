---
name: tech-diagram
description: "Generate technical architecture diagrams, pipeline flows, layer/stack diagrams, and system illustrations as standalone HTML files. Uses a dark-mode design system with embedded CSS and inline SVG. Use when the user needs architecture diagrams, system illustrations, flow charts, or technical visualizations."
license: MIT
origin: custom
author: Rebecca Rae Barton
author_url: https://github.com/thatrebeccarae
metadata:
  version: 1.0.0
  category: creative
  domain: design
  updated: 2026-03-13
---

# Technical Diagram Generator

Generate technical architecture diagrams and system illustrations as standalone HTML files with embedded CSS + inline SVG. No external dependencies.

## Core Capabilities

- Pipeline flow diagrams (data pipelines, CI/CD, ETL)
- Layer/stack diagrams (tech stack, OSI model, infrastructure)
- Component diagrams (microservices, system architecture)
- Before/after split comparisons
- Timeline diagrams (roadmaps, migration phases)
- Metric callout rows (KPI summaries)

## Design System

### Color Tokens

```css
:root {
  /* Dark mode (default canvas) */
  --bg-deep: #0d1117;
  --bg-surface: #161b22;
  --bg-elevated: #21262d;
  --border-subtle: rgba(240, 246, 252, 0.1);
  --text-bright: #f0f6fc;
  --text-secondary: #8b949e;
  --text-muted: #6e7681;

  /* Accent palette */
  --accent-blue: #58a6ff;
  --accent-green: #3fb950;
  --accent-purple: #bc8cff;
  --accent-orange: #d29922;
  --accent-red: #f85149;
  --accent-cyan: #39d2c0;
  --accent-pink: #f778ba;

  /* Light mode (optional, for embedded diagrams) */
  --bg-light: #ffffff;
  --bg-light-surface: #f6f8fa;
  --text-light-primary: #1f2328;
  --text-light-secondary: #656d76;
}
```

### Color Rules

- Dark mode is default for all diagrams
- Each pipeline stage or layer gets a distinct accent color
- Use `--text-secondary` for labels and annotations
- Use `--border-subtle` for connecting lines and borders
- Semantic colors: green = healthy/success, red = error/alert, orange = warning

### Typography

| Role | Font | Weight | Size |
|------|------|--------|------|
| Diagram title | system-ui | 600 | 28-32px |
| Section/stage label | system-ui | 600 | 16-18px |
| Description text | system-ui | 400 | 13-14px |
| Annotation | monospace | 400 | 12px |
| Metric value | monospace | 700 | 36-48px |

### Canvas

```
Width:  1200px (default, responsive down to 800px)
Height: auto (content-driven)
Padding: 48px
```

## Component Library

### Pipeline Flow

Horizontal or vertical sequence of stages with connecting arrows. Each stage has an icon area, label, and description.

### Layer/Stack Diagram

Vertical stack of labeled layers with optional descriptions. Top = highest abstraction, bottom = lowest.

### Component Diagram

Grid or freeform layout of service boxes with connection lines. Each component shows name, tech, and status.

### Before/After Split

Side-by-side comparison with a vertical divider. Left = before state, right = after state.

### Timeline

Horizontal or vertical sequence of milestones with dates, descriptions, and status indicators.

### Metric Callout Row

Horizontal row of KPI cards with large numbers, labels, and optional trend indicators.

## Key Principles

1. **One concept per diagram.** If it needs two diagrams, make two files.
2. **Labels on everything.** Every box, arrow, and region should be labeled.
3. **Consistent spacing.** Use CSS grid or flexbox, not absolute positioning.
4. **No external deps.** Everything inline — CSS in `<style>`, icons as inline SVG.
5. **Print-friendly.** Include `@media print` with light background override.

## Anti-Patterns

- No raster images (PNG/JPG) — use inline SVG for all icons
- No external CSS/JS — everything embedded
- No gradients as primary fill — use flat colors with subtle borders
- No more than 8 items in a single row — wrap or use grid
- No decorative elements that do not convey information

## File Conventions

- **Filename:** `{project}-{diagram-type}.html` (e.g., `pipeline-architecture.html`)
- **Single file:** All CSS inline in `<style>`, all SVG inline
- **Responsive:** Works at 800-1400px width range

For complete HTML/CSS patterns and full examples, see [REFERENCE.md](REFERENCE.md).
