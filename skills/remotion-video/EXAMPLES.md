# Remotion Video — Examples

## Example 1: Animated KPI Dashboard

**Prompt:**
> Create a 10-second video showing Q4 metrics: Revenue $2.4M (up 18%), New Customers 1,247 (up 23%), Churn Rate 2.1% (down 15%), NPS 72 (up 8 points). Each metric should count up with a staggered reveal.

**Expected output:** A 1080x1080 square composition at 30fps (300 frames). Dark background with 4 metric cards arranged in a 2x2 grid. Each card fades in and scales up (bouncy spring) with a 10-frame stagger. Numbers count up from 0 to target over 45 frames. Trend arrows animate in after the count completes. Green for positive trends, red for negative.

---

## Example 2: Product Feature Walkthrough

**Prompt:**
> Build a 30-second landscape video walking through 3 features of our app: Dashboard, Analytics, and Reports. Each feature gets a screenshot with a zoom-in effect and callout annotations.

**Expected output:** A 1920x1080 composition using TransitionSeries with 3 scenes (10s each) and fade transitions (0.5s). Each scene: screenshot enters with a smooth spring scale from 0.9 to 1.0, then a camera zoom interpolation to 1.3x focusing on the feature area. Text callouts fade in with staggered delays pointing to key UI elements.

---

## Example 3: Social Media Promo with Audio

**Prompt:**
> Create a 15-second Instagram Reel announcing a sale: "50% OFF" text animation, product images cycling through, background music, and a CTA at the end.

**Expected output:** A 1080x1920 portrait composition. Opens with "50% OFF" text using elastic spring (dramatic overshoot). Product images cycle via TransitionSeries with slide transitions every 3 seconds. Background music at 0.3 volume with fade-in (0-15 frames) and fade-out (last 15 frames). CTA slide at the end with a crisp spring scale-up.

---

## Example 4: Animated Bar Chart Race

**Prompt:**
> Create a bar chart showing monthly revenue growth from Jan ($120K) to Jun ($340K). Bars should grow in sequence with count-up labels.

**Expected output:** A 1920x1080 composition. 6 horizontal bars, each animating from 0 width to proportional width using smooth spring. Staggered by 15 frames per bar. Monospace count-up labels showing dollar values. Bars colored with a gradient from cool blue (Jan) to warm green (Jun). Y-axis labels fade in with their respective bars.
