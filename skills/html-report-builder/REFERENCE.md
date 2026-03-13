# HTML Report Builder — Reference

## HTML Boilerplate

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Report Title</title>
  <link href="https://api.fontshare.com/v2/css?f[]=switzer@300,400,500,600&display=swap" rel="stylesheet">
  <style>
    /* Paste full CSS framework below */
  </style>
</head>
<body>
  <div class="page page--dark cover">
    <!-- Cover page content -->
  </div>
  <div class="page">
    <!-- Content pages -->
  </div>
</body>
</html>
```

## Full CSS Framework

```css
/* === Reset === */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

/* === Design Tokens === */
:root {
  /* Dark mode (cover) */
  --bg-deep: #141414;
  --bg-surface: #1E1E1E;
  --bg-elevated: #282828;
  --border-subtle: rgba(255, 255, 255, 0.08);
  --text-bright: #f0f3f6;
  --text-secondary-dark: #9ca3af;
  --text-muted-dark: #6e7681;

  /* Light mode (content — default) */
  --bg-light: #FAF7F2;
  --bg-light-surface: #F2EDE6;
  --border-light: rgba(15, 14, 14, 0.1);
  --text-primary: #0f0e0e;
  --text-secondary: #57606a;
  --text-muted: #8b949e;

  /* Accent */
  --accent: #3D7A5C;
  --accent-light: #6AB88A;

  /* Semantic */
  --green: #2e8b57;
  --red: #c0392b;
  --amber: #D97706;

  /* Shadows */
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.04);
  --shadow-md: 0 2px 8px rgba(0,0,0,0.06);
}

/* === Typography === */
body {
  font-family: 'Switzer', system-ui, -apple-system, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: var(--text-primary);
  background: var(--bg-light);
}

.mono {
  font-family: 'Cartograph CF', 'JetBrains Mono', 'Consolas', monospace;
}

h1 {
  font-weight: 300;
  font-size: 48px;
  letter-spacing: -0.04em;
  line-height: 1.1;
}

h2 {
  font-weight: 400;
  font-size: 28px;
  letter-spacing: -0.02em;
  line-height: 1.2;
  margin-bottom: 16px;
}

h3 {
  font-weight: 500;
  font-size: 20px;
  line-height: 1.3;
  margin-bottom: 12px;
}

p { margin-bottom: 12px; }

.label {
  font-family: 'Cartograph CF', 'JetBrains Mono', monospace;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
}

/* === Page Layout === */
.page {
  max-width: 900px;
  margin: 0 auto;
  padding: 60px 80px;
  background: var(--bg-light);
  min-height: 100vh;
}

.page--dark {
  background: var(--bg-deep);
  color: var(--text-bright);
}

.page + .page {
  border-top: 1px solid var(--border-light);
}

/* === Cover Page === */
.cover {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  padding-bottom: 80px;
}

.cover h1 {
  font-size: 64px;
  margin-bottom: 16px;
}

.cover .subtitle {
  font-size: 20px;
  color: var(--text-secondary-dark);
  margin-bottom: 40px;
  max-width: 600px;
}

.cover-meta {
  font-family: 'Cartograph CF', monospace;
  font-size: 13px;
  color: var(--text-muted-dark);
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.cover-meta span + span::before {
  content: " · ";
  color: var(--text-muted-dark);
}

/* === Section Spacing === */
.section {
  margin-bottom: 48px;
}

.section-label {
  font-family: 'Cartograph CF', monospace;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  margin-bottom: 8px;
}

/* === KPI Cards === */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card {
  background: var(--bg-light-surface);
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 24px;
}

.kpi-card .label {
  margin-bottom: 8px;
}

.kpi-value {
  font-family: 'Cartograph CF', monospace;
  font-size: 36px;
  font-weight: 700;
  line-height: 1.1;
  margin-bottom: 4px;
}

.kpi-detail {
  font-size: 14px;
  color: var(--text-secondary);
}

.kpi-value--good { color: var(--green); }
.kpi-value--warning { color: var(--amber); }
.kpi-value--critical { color: var(--red); }

/* === Data Tables === */
.data-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 24px;
}

.data-table th {
  font-family: 'Cartograph CF', monospace;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  text-align: left;
  padding: 12px 16px;
  border-bottom: 2px solid var(--border-light);
  font-weight: 400;
}

.data-table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border-light);
  font-size: 15px;
}

.data-table td.mono,
.data-table td:nth-child(n+2) {
  font-family: 'Cartograph CF', monospace;
  font-size: 14px;
}

.data-table tr:last-child td {
  border-bottom: none;
}

.data-table .status-good { color: var(--green); font-weight: 600; }
.data-table .status-warning { color: var(--amber); font-weight: 600; }
.data-table .status-critical { color: var(--red); font-weight: 600; }

/* === Callout Boxes === */
.callout {
  background: var(--bg-light-surface);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  padding: 20px 24px;
  margin-bottom: 24px;
}

.callout--accent {
  background: #eaf2ed;
  border-color: rgba(61, 122, 92, 0.2);
}

.callout--warning {
  background: #fef3cd;
  border-color: rgba(217, 119, 6, 0.2);
}

.callout--critical {
  background: #fde8e8;
  border-color: rgba(192, 57, 43, 0.2);
}

.callout strong {
  display: inline;
}

.callout p {
  margin-bottom: 0;
  font-size: 15px;
  line-height: 1.5;
}

/* === Priority Banners === */
.banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 24px;
}

.banner--critical {
  background: #fde8e8;
  color: var(--red);
  border: 1px solid rgba(192, 57, 43, 0.2);
}

.banner--warning {
  background: #fef3cd;
  color: #92400e;
  border: 1px solid rgba(217, 119, 6, 0.2);
}

.banner--info {
  background: #eaf2ed;
  color: #1a5632;
  border: 1px solid rgba(61, 122, 92, 0.2);
}

.banner-icon {
  font-size: 18px;
  flex-shrink: 0;
}

/* === Recommendation Cards === */
.rec-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.rec-card {
  background: var(--bg-light-surface);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  padding: 20px 24px;
  display: flex;
  gap: 16px;
}

.rec-number {
  font-family: 'Cartograph CF', monospace;
  font-size: 24px;
  font-weight: 700;
  color: var(--accent);
  min-width: 32px;
}

.rec-content { flex: 1; }

.rec-title {
  font-weight: 500;
  font-size: 16px;
  margin-bottom: 4px;
}

.rec-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.rec-badges {
  display: flex;
  gap: 8px;
}

.badge {
  font-family: 'Cartograph CF', monospace;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 3px 8px;
  border-radius: 4px;
  background: var(--bg-light);
  border: 1px solid var(--border-light);
  color: var(--text-muted);
}

.badge--high-impact {
  background: #eaf2ed;
  border-color: rgba(61, 122, 92, 0.2);
  color: var(--accent);
}

.badge--low-effort {
  background: #e8f0fe;
  border-color: rgba(58, 134, 255, 0.2);
  color: #2563eb;
}

/* === Section Dividers === */
.divider {
  border: none;
  height: 1px;
  background: var(--border-light);
  margin: 48px 0;
}

/* === Lists === */
.bullet-list {
  list-style: none;
  padding-left: 0;
  margin-bottom: 20px;
}

.bullet-list li {
  padding: 6px 0 6px 20px;
  position: relative;
  font-size: 15px;
}

.bullet-list li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 14px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent);
}

.numbered-list {
  list-style: none;
  padding-left: 0;
  counter-reset: item;
  margin-bottom: 20px;
}

.numbered-list li {
  padding: 6px 0 6px 32px;
  position: relative;
  font-size: 15px;
  counter-increment: item;
}

.numbered-list li::before {
  content: counter(item);
  position: absolute;
  left: 0;
  top: 6px;
  font-family: 'Cartograph CF', monospace;
  font-weight: 700;
  font-size: 14px;
  color: var(--accent);
  width: 24px;
  text-align: center;
}

/* === Table of Contents === */
.toc {
  margin-bottom: 48px;
}

.toc-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-light);
  font-size: 15px;
}

.toc-item .toc-page {
  font-family: 'Cartograph CF', monospace;
  font-size: 14px;
  color: var(--text-muted);
}

/* === Print Styles === */
@media print {
  * { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
  body { background: white; margin: 0; }
  .page {
    break-after: page;
    break-inside: avoid;
    min-height: auto;
    box-shadow: none;
    border: none;
  }
  .page:last-child { break-after: avoid; }
  .kpi-card, .rec-card, .callout { box-shadow: none !important; }
}
```

## HTML Composition Patterns

### Cover Page

```html
<div class="page page--dark cover">
  <div class="cover-meta">
    <span>Prepared for Client Name</span>
    <span>March 2026</span>
  </div>
  <h1>Report Title</h1>
  <p class="subtitle">A comprehensive analysis of performance, opportunities, and strategic recommendations.</p>
</div>
```

### Executive Summary

```html
<div class="page">
  <div class="section">
    <div class="section-label">Executive Summary</div>
    <h2>Key Findings at a Glance</h2>

    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="label">Revenue</div>
        <div class="kpi-value kpi-value--good">$2.4M</div>
        <div class="kpi-detail">+18% vs target</div>
      </div>
      <div class="kpi-card">
        <div class="label">Conversion Rate</div>
        <div class="kpi-value kpi-value--warning">2.1%</div>
        <div class="kpi-detail">Below 2.5% benchmark</div>
      </div>
      <!-- more cards -->
    </div>

    <div class="callout">
      <p><strong>Bottom line:</strong> Revenue exceeded targets but conversion efficiency is declining. Recommend prioritizing funnel optimization over acquisition spend increase.</p>
    </div>
  </div>
</div>
```

### Data Section with Table

```html
<div class="section">
  <div class="section-label">Channel Performance</div>
  <h2>Revenue by Channel</h2>

  <table class="data-table">
    <thead>
      <tr>
        <th>Channel</th>
        <th>Revenue</th>
        <th>% of Total</th>
        <th style="text-align: right;">Status</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Organic Search</td>
        <td>$1.01M</td>
        <td>42%</td>
        <td style="text-align: right;" class="status-good">Above Target</td>
      </tr>
      <tr>
        <td>Paid Search</td>
        <td>$744K</td>
        <td>31%</td>
        <td style="text-align: right;" class="status-warning">At Target</td>
      </tr>
      <!-- more rows -->
    </tbody>
  </table>
</div>
```

### Recommendation Section

```html
<div class="section">
  <div class="section-label">Recommendations</div>
  <h2>Prioritized Actions</h2>

  <div class="rec-grid">
    <div class="rec-card">
      <div class="rec-number">1</div>
      <div class="rec-content">
        <div class="rec-title">Optimize checkout funnel</div>
        <div class="rec-desc">Cart abandonment at 68% — implement exit-intent recovery and streamline the 4-step checkout to 2 steps.</div>
        <div class="rec-badges">
          <span class="badge badge--high-impact">High Impact</span>
          <span class="badge badge--low-effort">Low Effort</span>
        </div>
      </div>
    </div>
    <!-- more rec-cards -->
  </div>
</div>
```

### Priority Banner

```html
<div class="banner banner--critical">
  <span class="banner-icon">&#9888;</span>
  <span>Churn rate at 4.2% — exceeds 3% target. Immediate action required.</span>
</div>
```
