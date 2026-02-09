# PptxGenJS Reference — VC-Backed SaaS Aesthetic

Complete implementation patterns for both light and dark modes. Copy-paste ready.

---

## Setup & Initialization

```javascript
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10" × 5.625"
pres.author = "Author Name";
pres.title = "Presentation Title";
```

### Theme Configuration

Define your theme once at the top. Every slide references this object.

```javascript
// --- DARK MODE ---
const theme = {
  mode: "dark",
  bg:          { primary: "0A0A0C", surface: "17181A", elevated: "1E1F23" },
  text:        { primary: "FFFFFF", secondary: "A0A0A0", muted: "5A5A5E" },
  border:      "2A2A2E",  // subtle card border (8% white equivalent on dark)
  accent:      "0055FF",  // swap per palette — this is Electric Blue
  accentMuted: "0D1B3F",  // accent at ~15% on dark bg (for tinted panels)
  status:      { positive: "10B981", warning: "F59E0B", critical: "EF4444" },
  font:        { head: "Inter", body: "Inter", mono: "JetBrains Mono" },
  shadow:      () => ({ type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.25 }),
  cardShadow:  () => ({ type: "outer", blur: 10, offset: 3, color: "000000", opacity: 0.3 }),
};

// --- LIGHT MODE ---
const theme = {
  mode: "light",
  bg:          { primary: "FFFFFF", surface: "F8F9FA", elevated: "FFFFFF" },
  text:        { primary: "111111", secondary: "555555", muted: "999999" },
  border:      "E8E8E8",
  accent:      "0055FF",
  accentMuted: "EBF0FF",  // accent at ~10% on white bg
  status:      { positive: "10B981", warning: "F59E0B", critical: "EF4444" },
  font:        { head: "Inter", body: "Inter", mono: "JetBrains Mono" },
  shadow:      () => ({ type: "outer", blur: 8, offset: 2, color: "000000", opacity: 0.07 }),
  cardShadow:  () => ({ type: "outer", blur: 12, offset: 3, color: "000000", opacity: 0.1 }),
};
```

### Palette Swapping

To use a different palette, just change `accent` and `accentMuted`:

```javascript
// Electric Blue (default)
theme.accent = "0055FF"; theme.accentMuted = theme.mode === "dark" ? "0D1B3F" : "EBF0FF";

// Indigo
theme.accent = "6366F1"; theme.accentMuted = theme.mode === "dark" ? "1A1A3E" : "EEF0FF";

// Teal Trust
theme.accent = "0D9488"; theme.accentMuted = theme.mode === "dark" ? "0A2825" : "E6F7F5";

// Emerald
theme.accent = "10B981"; theme.accentMuted = theme.mode === "dark" ? "0A2E20" : "E8FAF0";

// Hot Coral
theme.accent = "FF6B6B"; theme.accentMuted = theme.mode === "dark" ? "3D1A1A" : "FFF0F0";

// Rose
theme.accent = "F43F5E"; theme.accentMuted = theme.mode === "dark" ? "3D1020" : "FFF0F3";

// Amber Signal
theme.accent = "F59E0B"; theme.accentMuted = theme.mode === "dark" ? "3D2A08" : "FFF8E6";

// Violet
theme.accent = "8B5CF6"; theme.accentMuted = theme.mode === "dark" ? "1F1540" : "F3EFFE";

// Gold Standard
theme.accent = "D4AF37"; theme.accentMuted = theme.mode === "dark" ? "332B10" : "FBF6E6";

// Neon Lime (dark mode only — fails contrast on white)
theme.accent = "39FF14"; theme.accentMuted = "0A3308";

// Cyan Edge
theme.accent = "06B6D4"; theme.accentMuted = theme.mode === "dark" ? "082F35" : "E6FAFE";

// Slate (no accent — monochrome)
theme.accent = "64748B"; theme.accentMuted = theme.mode === "dark" ? "1E2530" : "F1F5F9";
```

---

## Layout Dimensions (16:9 = 10" × 5.625")

```
Full width:  10.0"     Full height:  5.625"
Margins:     0.5" all sides
Content:     x=0.5, w=9.0    y=1.0 to 5.0 (4.0" tall)
Title zone:  y=0.3 to 0.8
Footer zone: y=5.15 to 5.4
```

### Column Math

| Columns | Card Width | Gap | x positions |
|---------|-----------|-----|-------------|
| 2 | 4.35" | 0.3" | 0.5, 5.15 |
| 3 | 2.8" | 0.3" | 0.5, 3.6, 6.7 |
| 4 | 2.025" | 0.3" | 0.5, 2.825, 5.15, 7.475 |
| 5 | 1.56" | 0.3" | 0.5, 2.36, 4.22, 6.08, 7.94 |

---

## ⚠️ Critical Pitfalls

### 1. NEVER use `#` in hex colors
```javascript
// ❌ CORRUPTS FILE
{ color: "#0055FF" }
// ✅ CORRECT
{ color: "0055FF" }
```

### 2. NEVER encode opacity in hex (8-char colors)
```javascript
// ❌ CORRUPTS FILE
{ color: "0055FF20" }
// ✅ Use separate opacity property
{ color: "0055FF", transparency: 80 }
// Note: transparency is INVERSE of opacity (80 = 20% visible)
```

### 3. Use `bullet: true`, not unicode
```javascript
// ❌ AI hallmark
{ text: "• Feature one" }
// ✅ Proper formatting
{ text: "Feature one", options: { bullet: true } }
```

### 4. Use `breakLine: true` between text array items
```javascript
// Text arrays need explicit line breaks
slide.addText([
  { text: "Line one", options: { fontSize: 14, breakLine: true } },
  { text: "Line two", options: { fontSize: 14 } },
], { x: 0.5, y: 1.0, w: 9.0 });
```

### 5. NEVER reuse option objects (mutation trap)
```javascript
// ❌ Second call gets corrupted values
const shadow = { type: "outer", blur: 6 };
slide.addShape(pres.shapes.RECTANGLE, { shadow, x: 1 });
slide.addShape(pres.shapes.RECTANGLE, { shadow, x: 3 }); // BROKEN

// ✅ Use factory functions (theme.shadow() / theme.cardShadow())
slide.addShape(pres.shapes.RECTANGLE, { shadow: theme.shadow(), x: 1 });
slide.addShape(pres.shapes.RECTANGLE, { shadow: theme.shadow(), x: 3 });
```

### 6. Fresh `pptxgen()` per presentation
```javascript
// ❌ Reusing instance from a previous deck
// ✅ Always: let pres = new pptxgen();
```

### 7. No `ROUNDED_RECTANGLE` for accent overlays
Use `RECTANGLE` for thin accent bars/overlays. Rounded corners on thin shapes look wrong.

### 8. Shadow direction
```javascript
// Downward shadow (normal)
{ type: "outer", blur: 6, offset: 2, angle: 180, color: "000000", opacity: 0.1 }
// Upward shadow (don't use negative offset — use angle)
{ type: "outer", blur: 6, offset: 2, angle: 0, color: "000000", opacity: 0.1 }
```

### 9. Gradient fills
PptxGenJS doesn't support native gradient fills on shapes. For gradient backgrounds, generate a gradient image and use it as slide/shape background.

### 10. Avoid `lineSpacing` with bullets
It causes inconsistent spacing. Control spacing with `paraSpaceAfter` instead.

---

## Text Patterns

### Basic Text
```javascript
slide.addText("Hello World", {
  x: 0.5, y: 0.3, w: 9.0, h: 0.6,
  fontSize: 36, fontFace: theme.font.head, bold: true,
  color: theme.text.primary, align: "left",
});
```

### Rich Text (Multiple Styles)
```javascript
slide.addText([
  { text: "Revenue grew ", options: { fontSize: 16, color: theme.text.secondary, fontFace: theme.font.body } },
  { text: "47%", options: { fontSize: 16, color: theme.accent, fontFace: theme.font.body, bold: true } },
  { text: " year-over-year", options: { fontSize: 16, color: theme.text.secondary, fontFace: theme.font.body } },
], { x: 0.5, y: 1.5, w: 9.0 });
```

### Bullet List
```javascript
slide.addText([
  { text: "First item", options: { bullet: true, fontSize: 15, color: theme.text.secondary, fontFace: theme.font.body, breakLine: true, paraSpaceAfter: 6 } },
  { text: "Second item", options: { bullet: true, fontSize: 15, color: theme.text.secondary, fontFace: theme.font.body, breakLine: true, paraSpaceAfter: 6 } },
  { text: "Third item", options: { bullet: true, fontSize: 15, color: theme.text.secondary, fontFace: theme.font.body } },
], { x: 0.5, y: 1.5, w: 8.0, valign: "top" });
```

### KPI Number + Label
```javascript
// Big number
slide.addText("$4.2M", {
  x: cardX, y: cardY + 0.3, w: cardW, h: 0.8,
  fontSize: 48, fontFace: theme.font.mono, bold: true,
  color: theme.accent, align: "center",
});
// Label below
slide.addText("ANNUAL REVENUE", {
  x: cardX, y: cardY + 1.1, w: cardW, h: 0.3,
  fontSize: 9, fontFace: theme.font.body, bold: true,
  color: theme.text.muted, align: "center",
  charSpacing: 2.5,  // tracking for ALL CAPS labels
});
```

---

## Shapes & Cards

### Card (Elevated Surface)
```javascript
// Card background
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.0, w: 2.8, h: 2.5,
  fill: { color: theme.bg.surface },
  line: { color: theme.border, width: 0.5 },
  rectRadius: 0.08,
  shadow: theme.cardShadow(),
});
```

### Accent Bar (Thin Vertical/Horizontal)
```javascript
// Vertical accent bar (left edge of a panel)
slide.addShape(pres.shapes.RECTANGLE, {
  x: 5.1, y: 1.5, w: 0.04, h: 2.0,
  fill: { color: theme.accent },
});

```

### Tinted Panel (Accent at Low Opacity)
```javascript
slide.addShape(pres.shapes.RECTANGLE, {
  x: 5.15, y: 1.0, w: 4.35, h: 3.5,
  fill: { color: theme.accentMuted },
  line: { color: theme.border, width: 0.5 },
  rectRadius: 0.08,
});
```

### Status Indicator Dot
```javascript
// Green dot for positive KPI
slide.addShape(pres.shapes.OVAL, {
  x: cardX + 0.15, y: cardY + 0.2, w: 0.12, h: 0.12,
  fill: { color: theme.status.positive },
});
```

---

## Images & Logos

### Logo from File
```javascript
slide.addImage({
  path: "/path/to/logo.png",
  x: 0.5, y: 0.3, w: 1.5, h: 0.5,
  sizing: { type: "contain", w: 1.5, h: 0.5 },
});
```

### Logo in Slide Master (Every Slide)
```javascript
pres.defineSlideMaster({
  title: "BRANDED",
  background: { color: theme.bg.primary },
  objects: [
    { image: {
      path: "/path/to/logo.png",
      x: 8.5, y: 0.2, w: 1.0, h: 0.35,
      sizing: { type: "contain", w: 1.0, h: 0.35 },
    }},
  ],
});

let slide = pres.addSlide({ masterName: "BRANDED" });
```

### Logo from Base64
```javascript
slide.addImage({
  data: "image/png;base64,iVBOR...",
  x: 0.5, y: 0.3, w: 1.5, h: 0.5,
  sizing: { type: "contain", w: 1.5, h: 0.5 },
});
```

### Full-Bleed Background Image with Overlay
```javascript
// Background image
slide.addImage({
  path: "/path/to/photo.jpg",
  x: 0, y: 0, w: 10, h: 5.625,
  sizing: { type: "cover", w: 10, h: 5.625 },
});
// Dark overlay for text readability
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 5.625,
  fill: { color: "000000" },
  transparency: 40,  // 60% visible (dark overlay)
});
```

---

## Icons (react-icons → PNG → PptxGenJS)

### Conversion Utility

```javascript
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

async function iconToPng(iconName, pkg, color, size = 256) {
  const icons = require(`react-icons/${pkg}`);
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(icons[iconName], { color, size: String(size) })
  );
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

// Usage — Lucide icons (preferred)
const chartIcon = await iconToPng("LuBarChart3", "lu", "#" + theme.accent);
const usersIcon = await iconToPng("LuUsers", "lu", "#FFFFFF");

// Then add to slide
slide.addImage({ data: chartIcon, x: 0.7, y: 1.3, w: 0.35, h: 0.35 });
```

### Icon in Colored Circle

```javascript
// Circle background
slide.addShape(pres.shapes.OVAL, {
  x: 0.6, y: 1.2, w: 0.55, h: 0.55,
  fill: { color: theme.accent },
});
// White icon centered in circle
const icon = await iconToPng("LuZap", "lu", "#FFFFFF", 256);
slide.addImage({ data: icon, x: 0.7, y: 1.3, w: 0.35, h: 0.35 });
```

---

## Charts

### Bar/Column Chart

**CRITICAL: Set BOTH `dataLabelFormatCode` and `valAxisLabelFormatCode`.** `valAxisLabelFormatCode` only formats the axis — data labels from `showValue: true` need `dataLabelFormatCode`. `numFmt` is NOT a valid PptxGenJS property. Use OOXML conditional formats with raw values for best results.

```javascript
// Raw values + OOXML conditional format (auto-scales to K/M)
const currFmt = '[>=1000000]"$"#,##0.0,,"M";[>=1000]"$"#,##0.00,"K";"$"#,##0';
slide.addChart(pres.charts.BAR, [
  { name: "Revenue", labels: ["Q1", "Q2", "Q3", "Q4"], values: [1200000, 1800000, 2400000, 3100000] }
], {
  x: 0.5, y: 1.2, w: 5.5, h: 3.5,
  showValue: true,
  dataLabelColor: theme.text.secondary,
  dataLabelFontSize: 9,
  dataLabelFontFace: theme.font.mono,
  dataLabelPosition: "outEnd",
  dataLabelFormatCode: currFmt,  // REQUIRED: formats data labels ($1.2M, $540.18K)
  valAxisLabelFormatCode: '"$"#,##0.0,,"M"',  // Simple format (no conditional brackets on axis)
  showLegend: false,
  catAxisLabelColor: theme.text.muted,
  valAxisLabelColor: theme.text.muted,
  catAxisLabelFontSize: 10,
  valAxisLabelFontSize: 9,
  catAxisLineShow: false,
  valAxisLineShow: false,
  valGridLine: { color: theme.border, width: 0.5 },
  chartColors: [theme.accent],
  plotArea: { fill: { color: theme.bg.primary } },
  barGapWidthPct: 80,
  shadow: theme.shadow(),
});
```

### Line Chart
```javascript
slide.addChart(pres.charts.LINE, [
  { name: "2024", labels: months, values: data2024 },
  { name: "2025", labels: months, values: data2025 },
], {
  x: 0.5, y: 1.2, w: 9.0, h: 3.5,
  showLegend: true, legendPos: "t", legendFontSize: 10, legendColor: theme.text.secondary,
  catAxisLabelColor: theme.text.muted,
  valAxisLabelColor: theme.text.muted,
  catAxisLineShow: false,
  valAxisLineShow: false,
  valGridLine: { color: theme.border, width: 0.5 },
  chartColors: [theme.accent, theme.text.muted],
  lineDataSymbol: "circle", lineDataSymbolSize: 6,
  lineSmooth: true,
  plotArea: { fill: { color: theme.bg.primary } },
});
```

### Pie / Doughnut Chart
```javascript
slide.addChart(pres.charts.DOUGHNUT, [
  { name: "Share", labels: ["Product", "Services", "Support"], values: [55, 30, 15] }
], {
  x: 0.5, y: 1.2, w: 4.0, h: 3.5,
  showLegend: true, legendPos: "r", legendFontSize: 11, legendColor: theme.text.secondary,
  showPercent: true, dataLabelColor: theme.text.primary, dataLabelFontSize: 11,
  chartColors: [theme.accent, theme.text.muted, theme.border],
  holeSize: 55,
});
```

---

## Tables

### Styled Data Table

```javascript
const headerOpts = {
  fill: { color: theme.mode === "dark" ? theme.bg.elevated : theme.accent },
  color: theme.mode === "dark" ? theme.accent : "FFFFFF",
  fontSize: 10, fontFace: theme.font.body, bold: true,
  align: "left", valign: "middle",
  border: { type: "solid", color: theme.border, pt: 0.5 },
};

const rowOpts = (i) => ({
  fill: { color: i % 2 === 0 ? theme.bg.surface : theme.bg.primary },
  color: theme.text.secondary,
  fontSize: 11, fontFace: theme.font.body,
  align: "left", valign: "middle",
  border: { type: "solid", color: theme.border, pt: 0.5 },
});

const numOpts = (i) => ({
  ...rowOpts(i),
  fontFace: theme.font.mono,
  align: "right",
});

const rows = [
  // Header row
  [
    { text: "METRIC", options: headerOpts },
    { text: "Q1", options: { ...headerOpts, align: "right" } },
    { text: "Q2", options: { ...headerOpts, align: "right" } },
    { text: "Q3", options: { ...headerOpts, align: "right" } },
  ],
  // Data rows
  ...data.map((row, i) => [
    { text: row.name, options: rowOpts(i) },
    { text: row.q1, options: numOpts(i) },
    { text: row.q2, options: numOpts(i) },
    { text: row.q3, options: numOpts(i) },
  ]),
];

slide.addTable(rows, {
  x: 0.5, y: 1.2, w: 9.0,
  colW: [3.0, 2.0, 2.0, 2.0],
  rowH: 0.4,
  margin: [4, 8, 4, 8],
});
```

---

## Complete Slide Compositions

All compositions below work in both modes — they reference `theme` tokens.

### 1. Title Slide (Dark Hero)

```javascript
let slide = pres.addSlide();
slide.background = { color: theme.bg.primary };

// Optional: logo
slide.addImage({
  path: logoPath,
  x: 0.5, y: 0.4, w: 1.5, h: 0.5,
  sizing: { type: "contain", w: 1.5, h: 0.5 },
});

// Hero title
slide.addText("Quarterly Business Review", {
  x: 0.5, y: 1.5, w: 9.0, h: 1.2,
  fontSize: 54, fontFace: theme.font.head, bold: true,
  color: theme.text.primary, align: "left",
});

// Subtitle
slide.addText("Q4 2025 — Growth & Operational Metrics", {
  x: 0.5, y: 2.7, w: 9.0, h: 0.5,
  fontSize: 20, fontFace: theme.font.body,
  color: theme.text.secondary, align: "left",
});

// Date / attribution
slide.addText("January 15, 2026  •  Confidential", {
  x: 0.5, y: 5.1, w: 9.0, h: 0.3,
  fontSize: 10, fontFace: theme.font.body,
  color: theme.text.muted, align: "left",
});
```

### 2. KPI Dashboard (3-4 Cards)

```javascript
let slide = pres.addSlide();
slide.background = { color: theme.bg.primary };

// Title
slide.addText("Executive Summary", {
  x: 0.5, y: 0.3, w: 9.0, h: 0.5,
  fontSize: 32, fontFace: theme.font.head, bold: true,
  color: theme.text.primary,
});

// KPI Cards
const kpis = [
  { value: "$4.2M", label: "REVENUE", change: "+23%", status: "positive" },
  { value: "1,847", label: "ACTIVE USERS", change: "+12%", status: "positive" },
  { value: "94.2%", label: "RETENTION", change: "-0.3%", status: "warning" },
  { value: "47", label: "NPS SCORE", change: "+8", status: "positive" },
];

const cardW = 2.025;
const cardH = 2.2;
const gap = 0.3;
const startX = 0.5;
const cardY = 1.2;

kpis.forEach((kpi, i) => {
  const cx = startX + i * (cardW + gap);

  // Card bg
  slide.addShape(pres.shapes.RECTANGLE, {
    x: cx, y: cardY, w: cardW, h: cardH,
    fill: { color: theme.bg.surface },
    line: { color: theme.border, width: 0.5 },
    rectRadius: 0.08,
    shadow: theme.cardShadow(),
  });

  // Status dot
  slide.addShape(pres.shapes.OVAL, {
    x: cx + 0.2, y: cardY + 0.25, w: 0.1, h: 0.1,
    fill: { color: theme.status[kpi.status] },
  });

  // Big number
  slide.addText(kpi.value, {
    x: cx, y: cardY + 0.5, w: cardW, h: 0.7,
    fontSize: 36, fontFace: theme.font.mono, bold: true,
    color: theme.text.primary, align: "center",
  });

  // Label
  slide.addText(kpi.label, {
    x: cx, y: cardY + 1.25, w: cardW, h: 0.3,
    fontSize: 9, fontFace: theme.font.body, bold: true,
    color: theme.text.muted, align: "center", charSpacing: 2.5,
  });

  // Change indicator
  slide.addText(kpi.change, {
    x: cx, y: cardY + 1.6, w: cardW, h: 0.3,
    fontSize: 13, fontFace: theme.font.mono,
    color: theme.status[kpi.status], align: "center",
  });
});
```

### 3. Chart + Insight (60/40 Split)

```javascript
let slide = pres.addSlide();
slide.background = { color: theme.bg.primary };

// Title
slide.addText("Revenue Trend", {
  x: 0.5, y: 0.3, w: 9.0, h: 0.5,
  fontSize: 32, fontFace: theme.font.head, bold: true,
  color: theme.text.primary,
});

// Chart area (left 60%)
slide.addChart(pres.charts.BAR, chartData, {
  x: 0.5, y: 1.0, w: 5.2, h: 3.8,
  showValue: false, showLegend: false,
  catAxisLabelColor: theme.text.muted, valAxisLabelColor: theme.text.muted,
  catAxisLabelFontSize: 10, valAxisLabelFontSize: 9,
  catAxisLineShow: false, valAxisLineShow: false,
  valGridLine: { color: theme.border, width: 0.5 },
  chartColors: [theme.accent],
  plotArea: { fill: { color: theme.bg.primary } },
  barGapWidthPct: 80,
});

// Insight panel (right 40%) — tinted background
slide.addShape(pres.shapes.RECTANGLE, {
  x: 5.9, y: 1.0, w: 3.6, h: 2.5,
  fill: { color: theme.accentMuted },
  line: { color: theme.border, width: 0.5 },
  rectRadius: 0.08,
});

// Vertical accent bar
slide.addShape(pres.shapes.RECTANGLE, {
  x: 5.9, y: 1.0, w: 0.04, h: 2.5,
  fill: { color: theme.accent },
});

// Insight content
slide.addText("Key Insight", {
  x: 6.15, y: 1.15, w: 3.1, h: 0.3,
  fontSize: 11, fontFace: theme.font.body, bold: true,
  color: theme.accent, charSpacing: 1.5,
});

// NOTE: For panels < 4" wide, use fontSize 10-11 max.
// Estimate line count: chars ÷ ~40 chars/line at 11pt in 3" width.
// Verify total lines fit in container height (line ≈ 0.18" at 11pt).
slide.addText("Revenue grew 23% QoQ driven by enterprise expansion. Deal size rose from $42K to $58K.", {
  x: 6.15, y: 1.5, w: 3.0, h: 1.5,
  fontSize: 11, fontFace: theme.font.body,
  color: theme.text.secondary, align: "left", valign: "top",
  lineSpacingMultiple: 1.25,
});

// Recommendation panel below insight
slide.addShape(pres.shapes.RECTANGLE, {
  x: 5.9, y: 3.7, w: 3.6, h: 1.1,
  fill: { color: theme.bg.surface },
  line: { color: theme.border, width: 0.5 },
  rectRadius: 0.08,
});

slide.addText("Recommendation", {
  x: 6.15, y: 3.85, w: 3.1, h: 0.25,
  fontSize: 11, fontFace: theme.font.body, bold: true,
  color: theme.status.positive, charSpacing: 1.5,
});

slide.addText("Double down on enterprise pipeline — hire 2 additional AEs for Q1.", {
  x: 6.15, y: 4.15, w: 3.1, h: 0.5,
  fontSize: 13, fontFace: theme.font.body,
  color: theme.text.secondary, valign: "top",
});
```

### 4. Section Divider

```javascript
let slide = pres.addSlide();
slide.background = { color: theme.mode === "dark" ? theme.bg.elevated : theme.accent };

// Section number
slide.addText("02", {
  x: 0.5, y: 1.2, w: 9.0, h: 0.6,
  fontSize: 18, fontFace: theme.font.mono,
  color: theme.mode === "dark" ? theme.accent : "FFFFFF",
  transparency: 30,
});

// Section title
slide.addText("Product & Engineering", {
  x: 0.5, y: 1.8, w: 9.0, h: 1.2,
  fontSize: 44, fontFace: theme.font.head, bold: true,
  color: theme.mode === "dark" ? theme.text.primary : "FFFFFF",
});

// Description
slide.addText("Sprint velocity, feature launches, and technical debt reduction", {
  x: 0.5, y: 3.4, w: 7.0, h: 0.5,
  fontSize: 16, fontFace: theme.font.body,
  color: theme.mode === "dark" ? theme.text.secondary : "FFFFFF",
  transparency: theme.mode === "dark" ? 0 : 20,
});
```

### 5. Data Table

```javascript
let slide = pres.addSlide();
slide.background = { color: theme.bg.primary };

slide.addText("Financial Summary", {
  x: 0.5, y: 0.3, w: 9.0, h: 0.5,
  fontSize: 32, fontFace: theme.font.head, bold: true,
  color: theme.text.primary,
});

const hdr = {
  fill: { color: theme.mode === "dark" ? theme.bg.elevated : theme.accent },
  color: theme.mode === "dark" ? theme.accent : "FFFFFF",
  fontSize: 10, fontFace: theme.font.body, bold: true,
  border: { type: "solid", color: theme.border, pt: 0.5 },
  valign: "middle",
};

const cell = (i, align = "left") => ({
  fill: { color: i % 2 === 0 ? theme.bg.surface : theme.bg.primary },
  color: theme.text.secondary,
  fontSize: 11, fontFace: align === "right" ? theme.font.mono : theme.font.body,
  align, valign: "middle",
  border: { type: "solid", color: theme.border, pt: 0.5 },
});

const changeCell = (i, val) => ({
  ...cell(i, "right"),
  color: val >= 0 ? theme.status.positive : theme.status.critical,
});

const tableData = [
  [
    { text: "METRIC", options: { ...hdr, align: "left" } },
    { text: "Q3 ACTUAL", options: { ...hdr, align: "right" } },
    { text: "Q4 ACTUAL", options: { ...hdr, align: "right" } },
    { text: "Δ QOQ", options: { ...hdr, align: "right" } },
  ],
  // ... map your data into rows using cell() and changeCell()
];

slide.addTable(tableData, {
  x: 0.5, y: 1.1, w: 9.0,
  colW: [3.0, 2.0, 2.0, 2.0],
  rowH: 0.4,
  margin: [4, 10, 4, 10],
});
```

### 6. Icon Feature Grid (3-4 Rows)

```javascript
let slide = pres.addSlide();
slide.background = { color: theme.bg.primary };

slide.addText("Why Choose Us", {
  x: 0.5, y: 0.3, w: 9.0, h: 0.5,
  fontSize: 32, fontFace: theme.font.head, bold: true,
  color: theme.text.primary,
});

const features = [
  { icon: "LuZap", title: "Lightning Fast", desc: "Sub-100ms response times across all endpoints" },
  { icon: "LuShield", title: "Enterprise Security", desc: "SOC 2 Type II certified with end-to-end encryption" },
  { icon: "LuBarChart3", title: "Real-Time Analytics", desc: "Live dashboards with customizable KPI tracking" },
];

for (let i = 0; i < features.length; i++) {
  const fy = 1.2 + i * 1.25;

  // Accent circle
  slide.addShape(pres.shapes.OVAL, {
    x: 0.5, y: fy, w: 0.55, h: 0.55,
    fill: { color: theme.accent },
  });

  // Icon (white on accent)
  const ico = await iconToPng(features[i].icon, "lu", "#FFFFFF", 256);
  slide.addImage({ data: ico, x: 0.6, y: fy + 0.1, w: 0.35, h: 0.35 });

  // Title
  slide.addText(features[i].title, {
    x: 1.3, y: fy, w: 7.5, h: 0.35,
    fontSize: 18, fontFace: theme.font.head, bold: true,
    color: theme.text.primary,
  });

  // Description
  slide.addText(features[i].desc, {
    x: 1.3, y: fy + 0.35, w: 7.5, h: 0.35,
    fontSize: 14, fontFace: theme.font.body,
    color: theme.text.secondary,
  });
}
```

### 7. Quote Slide

```javascript
let slide = pres.addSlide();
slide.background = { color: theme.bg.primary };

// Large decorative quotation mark
slide.addText("\u201C", {
  x: 0.5, y: 0.5, w: 2.0, h: 2.0,
  fontSize: 144, fontFace: "Georgia",
  color: theme.accent, transparency: 60,
});

// Quote text
slide.addText("The product practically sells itself. Our team adoption went from 0 to 95% in under two weeks.", {
  x: 1.5, y: 1.5, w: 7.0, h: 2.0,
  fontSize: 24, fontFace: theme.font.body, italic: true,
  color: theme.text.primary, align: "center", valign: "middle",
  lineSpacingMultiple: 1.4,
});

// Attribution
slide.addText("— Sarah Chen, VP Engineering at Stripe", {
  x: 1.5, y: 3.7, w: 7.0, h: 0.4,
  fontSize: 14, fontFace: theme.font.body,
  color: theme.text.muted, align: "center",
});
```

### 8. Big Number Slide

```javascript
let slide = pres.addSlide();
slide.background = { color: theme.bg.primary };

// Context label
slide.addText("YEAR-OVER-YEAR GROWTH", {
  x: 0.5, y: 1.2, w: 9.0, h: 0.3,
  fontSize: 11, fontFace: theme.font.body, bold: true,
  color: theme.text.muted, align: "center", charSpacing: 3,
});

// Huge number
slide.addText("247%", {
  x: 0.5, y: 1.6, w: 9.0, h: 2.0,
  fontSize: 120, fontFace: theme.font.mono, bold: true,
  color: theme.accent, align: "center",
});

// Supporting context
slide.addText("From $1.2M to $4.2M ARR in 12 months", {
  x: 1.5, y: 3.6, w: 7.0, h: 0.5,
  fontSize: 18, fontFace: theme.font.body,
  color: theme.text.secondary, align: "center",
});
```

### 9. Comparison (Side-by-Side)

```javascript
let slide = pres.addSlide();
slide.background = { color: theme.bg.primary };

slide.addText("Before & After", {
  x: 0.5, y: 0.3, w: 9.0, h: 0.5,
  fontSize: 32, fontFace: theme.font.head, bold: true,
  color: theme.text.primary,
});

// Left panel (before)
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.0, w: 4.25, h: 3.8,
  fill: { color: theme.bg.surface },
  line: { color: theme.border, width: 0.5 },
  rectRadius: 0.08,
});

slide.addText("BEFORE", {
  x: 0.5, y: 1.15, w: 4.25, h: 0.3,
  fontSize: 10, fontFace: theme.font.body, bold: true,
  color: theme.text.muted, align: "center", charSpacing: 3,
});

// Right panel (after) — accent tinted
slide.addShape(pres.shapes.RECTANGLE, {
  x: 5.25, y: 1.0, w: 4.25, h: 3.8,
  fill: { color: theme.accentMuted },
  line: { color: theme.border, width: 0.5 },
  rectRadius: 0.08,
});

slide.addText("AFTER", {
  x: 5.25, y: 1.15, w: 4.25, h: 0.3,
  fontSize: 10, fontFace: theme.font.body, bold: true,
  color: theme.accent, align: "center", charSpacing: 3,
});

// Add content to each panel...
```

### 10. Closing Slide

```javascript
let slide = pres.addSlide();
slide.background = { color: theme.bg.primary };

// Logo (large, centered)
if (logoPath) {
  slide.addImage({
    path: logoPath,
    x: 3.5, y: 0.8, w: 3.0, h: 1.0,
    sizing: { type: "contain", w: 3.0, h: 1.0 },
  });
}

// Thank you
slide.addText("Thank You", {
  x: 0.5, y: 2.0, w: 9.0, h: 0.8,
  fontSize: 44, fontFace: theme.font.head, bold: true,
  color: theme.text.primary, align: "center",
});

// CTA or next steps
slide.addText("Questions?", {
  x: 0.5, y: 2.8, w: 9.0, h: 0.5,
  fontSize: 20, fontFace: theme.font.body,
  color: theme.text.secondary, align: "center",
});

// Contact info
slide.addText("team@company.com  •  company.com", {
  x: 0.5, y: 3.8, w: 9.0, h: 0.4,
  fontSize: 13, fontFace: theme.font.body,
  color: theme.text.muted, align: "center",
});
```

---

## Save & Export

```javascript
// Save to file
await pres.writeFile({ fileName: "/path/to/output.pptx" });

// Save to buffer (for piping)
const buffer = await pres.write({ outputType: "nodebuffer" });
require("fs").writeFileSync("/path/to/output.pptx", buffer);
```

---

## Reading & Editing Existing PPTX

For reading existing presentations, extracting content, or editing templates, see [editing.md](editing.md).

Quick extraction:
```bash
python -m markitdown presentation.pptx
```
