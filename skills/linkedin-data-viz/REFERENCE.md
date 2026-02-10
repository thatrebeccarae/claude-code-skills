# LinkedIn Data Viz -- Technical Reference

This document covers CSV schemas, parsing quirks, analysis algorithms, template placeholders, and theme customization for the LinkedIn Data Viz skill.

---

## CSV Schemas

### Connections.csv

The primary network data file. Contains one row per connection.

**Important:** The first 3 lines are junk header lines inserted by LinkedIn (notes, blank line, etc.). The real CSV header starts on line 4. Parsers must skip the first 3 lines.

| Column | Data Type | Notes |
|--------|-----------|-------|
| First Name | string | May be empty for deactivated accounts |
| Last Name | string | May be empty for deactivated accounts |
| URL | string | LinkedIn profile URL (https://www.linkedin.com/in/...) |
| Email Address | string | Often empty; only populated if the connection shared it |
| Company | string | Current company at time of export; may be empty |
| Position | string | Current position at time of export; may be empty |
| Connected On | string | Date format: `DD Mon YYYY` (e.g., `15 Jan 2023`) |

**Example (after skipping 3 header lines):**

```csv
First Name,Last Name,URL,Email Address,Company,Position,Connected On
Jane,Doe,https://www.linkedin.com/in/janedoe,,Acme Corp,VP Marketing,08 Mar 2022
John,Smith,https://www.linkedin.com/in/johnsmith,john@example.com,TechCo,Software Engineer,22 Nov 2020
```

---

### messages.csv

Full message history across all conversations. One row per message.

| Column | Data Type | Notes |
|--------|-----------|-------|
| CONVERSATION ID | string | Groups messages into threads; may be null for some edge cases |
| CONVERSATION TITLE | string | Often the other participant's name or group name |
| FROM | string | Sender display name |
| SENDER PROFILE URL | string | LinkedIn profile URL of the sender |
| TO | string | Recipient display name(s); comma-separated for group messages |
| DATE | string | Format: `YYYY-MM-DD HH:MM:SS UTC` |
| SUBJECT | string | Message subject line; often empty for direct messages |
| CONTENT | string | Message body text; may contain newlines (quoted in CSV) |

**Example:**

```csv
CONVERSATION ID,CONVERSATION TITLE,FROM,SENDER PROFILE URL,TO,DATE,SUBJECT,CONTENT
abc-123,Jane Doe,Jane Doe,https://www.linkedin.com/in/janedoe,You,2024-01-15 09:30:00 UTC,,Hey! Wanted to connect about the marketing role.
abc-123,Jane Doe,You,https://www.linkedin.com/in/you,Jane Doe,2024-01-15 14:22:00 UTC,,Thanks for reaching out! Let me take a look.
```

---

### Invitations.csv

Connection request history (both sent and received).

| Column | Data Type | Notes |
|--------|-----------|-------|
| From | string | Sender display name |
| To | string | Recipient display name |
| Sent At | string | Format: `YYYY-MM-DD HH:MM:SS UTC` |
| Message | string | Optional invitation note; often empty |
| Direction | string | `INCOMING` or `OUTGOING` |

**Example:**

```csv
From,To,Sent At,Message,Direction
Jane Doe,You,2024-01-10 08:15:00 UTC,Hi! I saw your talk at the conference.,INCOMING
You,John Smith,2024-01-12 16:45:00 UTC,,OUTGOING
```

---

### Company Follows.csv

Companies the user follows on LinkedIn.

| Column | Data Type | Notes |
|--------|-----------|-------|
| Organization Name | string | Company display name |
| Followed On | string | Format: `DD Mon YYYY` (same as Connections.csv) |

**Example:**

```csv
Organization Name,Followed On
Stripe,14 Jun 2021
Figma,02 Sep 2022
```

---

### Inferences_about_you.csv

LinkedIn's algorithmic inferences about the user.

| Column | Data Type | Notes |
|--------|-----------|-------|
| Category | string | Inference category (e.g., "Industry", "Job Function") |
| Type Of Inference | string | Inference type label |
| Description | string | The actual inference value |

**Example:**

```csv
Category,Type Of Inference,Description
Industry,Predicted Industry,Computer Software
Job Function,Predicted Job Function,Marketing
Seniority,Predicted Seniority,Senior
```

---

### Ad_Targeting.csv

Advertiser targeting categories applied to the user's profile. This file has an unusual structure: a single data row with semicolon-separated values within cells.

| Column | Data Type | Notes |
|--------|-----------|-------|
| Member Age | string | Age range (e.g., "25-34") |
| Member Gender | string | Gender category |
| Member Industry | string | Semicolon-separated list of industries |
| Company Connections | string | Semicolon-separated company names |
| Company Follower of | string | Semicolon-separated company names |
| Company Names | string | Semicolon-separated company names |
| Company Size | string | Semicolon-separated size ranges |
| Degrees | string | Semicolon-separated degree types |
| Fields of Study | string | Semicolon-separated fields |
| Graduation Year | string | Semicolon-separated years |
| Job Functions | string | Semicolon-separated functions |
| Job Seniority | string | Semicolon-separated seniority levels |
| Job Titles | string | Semicolon-separated titles |
| Member Groups | string | Semicolon-separated group names |
| Member Interests | string | Semicolon-separated interest topics |
| Member Schools | string | Semicolon-separated school names |
| Member Skills | string | Semicolon-separated skills |
| Locale | string | Locale code (e.g., "en_US") |
| Profile Locations | string | Semicolon-separated locations |
| Years of Experience | string | Experience range |

**Example:**

```csv
Member Age,Member Gender,Member Industry,...
25-34,Female,Computer Software;Internet;Marketing and Advertising,...
```

**Parsing note:** After reading the CSV, split each cell value on `;` to get individual items. Trim whitespace from each item.

---

## Parsing Quirks

### Connections.csv 3-Line Header Skip

LinkedIn prepends 3 lines of metadata before the actual CSV header. These lines contain notes like "Notes:," blank lines, or export metadata. The parser must:

1. Read the file.
2. Skip the first 3 lines.
3. Treat line 4 as the CSV header row.
4. Parse remaining lines as data rows.

```python
# Example
with open('Connections.csv', 'r', encoding='utf-8') as f:
    for _ in range(3):
        f.readline()  # skip junk lines
    reader = csv.DictReader(f)
```

### Ad_Targeting.csv Semicolon Splitting

Each cell in the single data row may contain multiple values separated by semicolons. After standard CSV parsing, split each value:

```python
industries = row['Member Industry'].split(';')
industries = [i.strip() for i in industries if i.strip()]
```

### messages.csv Null CONVERSATION IDs

Some messages have empty or null `CONVERSATION ID` fields. These are typically:
- System messages
- InMail messages
- Messages from deleted accounts

The parser should:
- Group messages by `CONVERSATION ID` where available.
- Place null-ID messages into a special "ungrouped" bucket.
- Still include them in message counts and inbox quality analysis.

### Mixed Date Format Handling

LinkedIn uses two date formats across its CSV files:

| Format | Used In | Example |
|--------|---------|---------|
| `DD Mon YYYY` | Connections.csv, Company Follows.csv | `08 Mar 2022` |
| `YYYY-MM-DD HH:MM:SS UTC` | messages.csv, Invitations.csv | `2024-01-15 09:30:00 UTC` |

The parser should detect and handle both formats:

```python
from datetime import datetime

def parse_date(date_str):
    date_str = date_str.strip()
    for fmt in ('%d %b %Y', '%Y-%m-%d %H:%M:%S %Z', '%Y-%m-%d %H:%M:%S UTC'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {date_str}")
```

### UTF-8 Encoding Issues

Some LinkedIn exports contain non-UTF-8 characters, particularly in:
- Names with diacritics or non-Latin scripts
- Company names with special characters
- Message content with emoji or special punctuation

Always open CSV files with `encoding='utf-8'` and `errors='replace'` as a fallback:

```python
with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
    reader = csv.DictReader(f)
```

---

## Analysis Algorithms

### Network Clustering (Network Universe)

Assigns each connection to a role cluster based on keyword matching against the `Position` field.

**Cluster definitions:**

| Cluster | Keywords |
|---------|----------|
| Engineering | engineer, developer, software, sre, devops, architect, CTO, technical |
| Marketing | marketing, brand, content, growth, SEO, demand gen, communications, CMO |
| Sales | sales, account executive, business development, SDR, BDR, revenue, CRO |
| Product | product manager, product lead, product owner, head of product, CPO |
| Design | design, UX, UI, creative, art director, visual |
| Data | data, analytics, machine learning, AI, scientist, BI |
| Operations | operations, ops, supply chain, logistics, COO |
| Finance | finance, accounting, CFO, controller, treasury, FP&A |
| HR/People | HR, human resources, people, talent, recruiting, recruiter, CHRO |
| Executive | CEO, founder, co-founder, president, managing director, partner, VP, C-suite |
| Other | (no keyword match) |

Matching is case-insensitive. If a position matches multiple clusters, the first match wins in the order listed above.

### Company Categorization (Company Follows Clustering)

Groups followed companies by industry using keyword matching against the `Organization Name` field and known company databases.

**Category keywords:**

| Category | Matching Logic |
|----------|---------------|
| Tech / SaaS | Known tech companies + keywords: software, tech, cloud, platform, AI, data |
| Finance / Fintech | Keywords: bank, capital, financial, fintech, payments, invest |
| E-commerce / Retail | Keywords: shop, retail, commerce, marketplace, brand, DTC |
| Media / Publishing | Keywords: media, news, publish, content, entertainment |
| Consulting / Services | Keywords: consulting, advisory, agency, partners, group |
| Healthcare | Keywords: health, medical, pharma, biotech, wellness |
| Education | Keywords: university, academy, school, edtech, learning |
| Other | (no keyword match) |

### Message Scoring (High-Value Messages)

Scores unanswered messages to surface high-value opportunities. The score is a weighted sum of:

| Factor | Weight | Calculation |
|--------|--------|-------------|
| Recency | 0.35 | Inverse days since message (capped at 365). More recent = higher. |
| Sender Role | 0.25 | Bonus for VP+, Director, Founder, Recruiter roles (from Connections.csv position). |
| Content Signals | 0.20 | Keyword scan for opportunity signals: "opportunity," "role," "interested," "collaborate," "project," "hiring," "budget." |
| Relationship Depth | 0.20 | Based on total message count in conversation. More messages = stronger relationship = higher urgency to reply. |

Messages are classified into urgency tiers:
- **Hot** (score >= 0.7): High-value, respond soon.
- **Warm** (score 0.4-0.69): Worth responding to.
- **Cool** (score < 0.4): Low priority but noted.

### Invitation Direction Detection (Inbound vs Outbound)

Uses the `Direction` field in `Invitations.csv` directly:
- `INCOMING` = someone sent the user a request.
- `OUTGOING` = the user sent a request.

Aggregates by month for trend visualization. Calculates rolling ratios and identifies periods of high inbound (passive growth) vs high outbound (active networking).

### Inbox Quality Classification (Inbox Quality)

Classifies each message as Genuine or Noise using heuristics:

**Noise indicators:**
- Sender is "LinkedIn" or "LinkedIn Member"
- Subject contains "InMail" or "Sponsored"
- Content matches spam patterns: "I came across your profile," "We have an exciting opportunity," form-letter intros
- Conversation has exactly 1 message and no reply (cold outreach)
- CONVERSATION ID is null

**Genuine indicators:**
- Multiple messages in the conversation (back-and-forth)
- Sender is in the user's connections
- Content is personalized (contains the user's name, references specific work)

Each message gets a classification. Aggregated by month for the stacked area chart.

### Career Strata Date-Range Bucketing (Career Strata)

Divides the user's connection history into career phases based on connection dates.

**Algorithm:**
1. Sort all connections by `Connected On` date.
2. Determine the full date range (earliest to latest connection).
3. Divide into phases. Default: split by year. If the history spans more than 8 years, group into multi-year buckets to keep the number of strata between 4 and 9.
4. For each phase, compute:
   - Connection count
   - Percentage of total
   - Top companies in that phase
   - Top roles in that phase
5. Assign layer classes (`layer-0` through `layer-8`) from oldest (deepest) to newest (most elevated).

---

## Template Placeholder Reference

Each HTML template in `templates/` uses two placeholders that are replaced during generation:

### `{{DATA}}`

Replaced with a JSON object containing all analysis results. Injected into a `<script>` tag in the HTML:

```html
<script>
  const DATA = {{DATA}};
</script>
```

### `{{THEME_CSS}}`

Replaced with the full CSS content from the selected theme file. Injected into a `<style>` tag:

```html
<style>
  {{THEME_CSS}}
</style>
```

### Per-Template Data Keys

Each template expects specific keys in the `DATA` object.

#### 01-network-universe.html

```json
{
  "nodes": [
    { "id": "string", "name": "string", "company": "string", "position": "string", "cluster": "string" }
  ],
  "clusters": [
    { "name": "string", "count": 0, "color": "#hex", "topCompanies": ["string"] }
  ],
  "links": [
    { "source": "cluster_name", "target": "cluster_name", "strength": 0.0 }
  ],
  "stats": {
    "totalConnections": 0,
    "clusterCount": 0,
    "largestCluster": "string",
    "dateRange": "string"
  }
}
```

#### 02-inferences-vs-reality.html

```json
{
  "inferences": [
    {
      "category": "string",
      "linkedinSays": "string",
      "reality": "string",
      "verdict": "accurate|partial|wrong",
      "explanation": "string"
    }
  ],
  "adTargeting": {
    "industries": ["string"],
    "jobTitles": ["string"],
    "skills": ["string"],
    "interests": ["string"],
    "schools": ["string"],
    "demographics": { "age": "string", "gender": "string", "location": "string" }
  },
  "stats": {
    "totalInferences": 0,
    "accurateCount": 0,
    "partialCount": 0,
    "wrongCount": 0,
    "accuracyRate": "string"
  }
}
```

#### 03-high-value-messages.html

```json
{
  "messages": [
    {
      "from": "string",
      "profileUrl": "string",
      "date": "string",
      "daysAgo": 0,
      "subject": "string",
      "content": "string",
      "score": 0.0,
      "urgency": "hot|warm|cool",
      "tags": ["opportunity", "relationship", "network"],
      "conversationLength": 0
    }
  ],
  "stats": {
    "totalUnanswered": 0,
    "hotCount": 0,
    "warmCount": 0,
    "coolCount": 0,
    "oldestUnanswered": "string"
  }
}
```

#### 04-company-follows-clustering.html

```json
{
  "clusters": [
    {
      "name": "string",
      "color": "#hex",
      "count": 0,
      "companies": ["string"]
    }
  ],
  "stats": {
    "totalFollowed": 0,
    "clusterCount": 0,
    "largestCluster": "string",
    "earliestFollow": "string",
    "latestFollow": "string"
  }
}
```

#### 05-inbound-vs-outbound.html

```json
{
  "monthly": [
    { "month": "YYYY-MM", "inbound": 0, "outbound": 0 }
  ],
  "stats": {
    "totalInvitations": 0,
    "totalInbound": 0,
    "totalOutbound": 0,
    "inboundRatio": "string",
    "peakInboundMonth": "string",
    "peakOutboundMonth": "string"
  }
}
```

#### 06-connection-quality.html

```json
{
  "tiers": [
    {
      "name": "Active",
      "count": 0,
      "percentage": "string",
      "color": "#hex",
      "description": "string"
    },
    {
      "name": "Dormant",
      "count": 0,
      "percentage": "string",
      "color": "#hex",
      "description": "string"
    },
    {
      "name": "Never Messaged",
      "count": 0,
      "percentage": "string",
      "color": "#hex",
      "description": "string"
    }
  ],
  "stats": {
    "totalConnections": 0,
    "activeRate": "string",
    "avgMessagesPerActive": 0.0,
    "mostActiveConnection": "string"
  }
}
```

#### 07-connection-timeline.html

```json
{
  "connections": [
    {
      "name": "string",
      "company": "string",
      "position": "string",
      "connectedOn": "string",
      "direction": "inbound|outbound|unknown",
      "messageCount": 0
    }
  ],
  "stats": {
    "recentCount": 0,
    "dateRange": "string",
    "topCompany": "string",
    "inboundPercent": "string"
  }
}
```

#### 08-inbox-quality.html

```json
{
  "monthly": [
    { "month": "YYYY-MM", "genuine": 0, "noise": 0 }
  ],
  "stats": {
    "totalMessages": 0,
    "genuineCount": 0,
    "noiseCount": 0,
    "genuineRate": "string",
    "noiseTrend": "increasing|decreasing|stable"
  }
}
```

#### 09-career-strata.html

```json
{
  "strata": [
    {
      "era": "string",
      "dateRange": "string",
      "count": 0,
      "percentage": "string",
      "topCompanies": ["string"],
      "topRoles": ["string"],
      "layerClass": "layer-0"
    }
  ],
  "stats": {
    "totalConnections": 0,
    "careerSpanYears": 0,
    "strataCount": 0,
    "peakEra": "string"
  }
}
```

#### dashboard.html

The unified dashboard expects the full combined data object with all keys from all 9 visualizations, namespaced under top-level keys:

```json
{
  "networkUniverse": { ... },
  "inferencesVsReality": { ... },
  "highValueMessages": { ... },
  "companyFollows": { ... },
  "inboundOutbound": { ... },
  "connectionQuality": { ... },
  "connectionTimeline": { ... },
  "inboxQuality": { ... },
  "careerStrata": { ... },
  "summary": {
    "totalConnections": 0,
    "totalMessages": 0,
    "totalCompaniesFollowed": 0,
    "dateRange": "string",
    "exportDate": "string"
  }
}
```

---

## Theme Customization

The skill ships with the Carrier Dark theme at `assets/carrier-dark.css`. To create a custom theme:

### Step 1: Copy the Base Theme

```bash
cp assets/carrier-dark.css assets/my-custom-theme.css
```

### Step 2: Modify CSS Custom Properties

All visual styling is controlled via CSS custom properties in the `:root` selector. The key properties to modify:

**Backgrounds:**

```css
:root {
  --bg-primary:     #0D1117;   /* Page background */
  --bg-surface:     #161B22;   /* Card/section background */
  --bg-elevated:    #1E2329;   /* Elevated elements (headers, hover states) */
  --bg-glass:       rgba(255, 255, 255, 0.04);  /* Glass-morphism panels */
}
```

**Text colors:**

```css
:root {
  --text-primary:   #fdfdfe;   /* Headings, important text */
  --text-secondary: #8b949e;   /* Body text */
  --text-muted:     #7d8590;   /* Labels, captions */
}
```

**Accent colors:**

```css
:root {
  --accent-primary:  #4eadab;  /* Primary interactive color (links, active states) */
  --accent-hover:    #6bc0be;  /* Hover state for accents */
}
```

**Visualization palette:**

```css
:root {
  --viz-teal:    #4eadab;  /* Primary chart color */
  --viz-lime:    #39FF14;  /* Highlight/excellent */
  --viz-cyan:    #6bc0be;  /* Secondary chart color */
  --viz-purple:  #A855F7;  /* Tertiary/special */
  --viz-orange:  #FF5F1F;  /* Warning/marginal */
  --viz-gold:    #FFD700;  /* Important/offer */
  --viz-muted:   #8b949e;  /* Neutral data */
  --viz-deep:    #4a9f9d;  /* Deep variant */
  --viz-slate:   #7d8590;  /* Muted variant */
  --viz-pink:    #FF2D55;  /* Error/rejected */
}
```

**Borders:**

```css
:root {
  --border-subtle:   rgba(255, 255, 255, 0.08);  /* Default borders */
  --border-hover:    rgba(255, 255, 255, 0.12);  /* Hover-state borders */
}
```

**Layout:**

```css
:root {
  --max-w: 1100px;       /* Max content width */
  --radius-sm: 6px;      /* Small border radius */
  --radius-md: 10px;     /* Medium border radius */
  --radius-lg: 12px;     /* Large border radius */
}
```

### Step 3: Career Strata Layer Colors

The Career Strata visualization uses numbered layer classes (`.layer-0` through `.layer-8`) for its geological aesthetic. These are defined outside of `:root` and must be modified directly:

```css
/* Deep (old) to elevated (new) */
.layer-0 { background: #0D1117; color: #4eadab; }
.layer-1 { background: #111820; color: #5ab8b6; }
/* ... through layer-8 */
```

### Step 4: Chart.js Defaults

If modifying chart colors, also update the Chart.js defaults comment block at the bottom of the CSS file. These values are applied via JavaScript at runtime:

```javascript
Chart.defaults.color = '#8b949e';             // Axis labels, legend text
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.plugins.tooltip.backgroundColor = '#1E2329';
Chart.defaults.scale.grid.color = 'rgba(255,255,255,0.08)';
```

### Step 5: Use Your Theme

Pass your custom theme to the generation step:

```bash
python scripts/generate.py output/ --theme assets/my-custom-theme.css --vizzes all
```

### Light Theme Tips

To create a light theme, invert the background and text values:

```css
:root {
  --bg-primary:     #FFFFFF;
  --bg-surface:     #F6F8FA;
  --bg-elevated:    #EAEEF2;
  --text-primary:   #1F2328;
  --text-secondary: #656D76;
  --text-muted:     #8B949E;
  --border-subtle:  rgba(0, 0, 0, 0.08);
  --border-hover:   rgba(0, 0, 0, 0.12);
}
```

Adjust the Career Strata `.layer-*` classes accordingly, using light-to-dark shading instead of dark-to-light.
