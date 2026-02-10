---
name: linkedin-data-viz
description: >
  Analyze and visualize LinkedIn data exports. Generates 9 interactive
  HTML visualizations from CSV files including network force graphs,
  message analysis, connection quality scoring, and career timelines.
  Use when the user mentions LinkedIn data export, LinkedIn visualization,
  LinkedIn network analysis, or wants to analyze their LinkedIn connections.
---

# LinkedIn Data Viz Skill

This skill transforms a LinkedIn data export into 9 interactive HTML visualizations with a unified dashboard. It walks the user through a wizard flow: locating their export, previewing analysis, selecting a theme, and generating output. All data stays local on the user's machine.

---

## Wizard Flow

### Step 1: Export Guidance

Tell the user how to request their LinkedIn data archive if they have not already done so.

**Instructions to share with the user:**

1. Go to LinkedIn Settings (click your profile photo, then "Settings & Privacy").
2. Navigate to **Data privacy** in the left sidebar.
3. Click **Get a copy of your data**.
4. Select **all categories** (or at minimum: Connections, Messages, Invitations, Company Follows, Inferences, Ad Targeting).
5. Click **Request archive**.
6. LinkedIn will email a download link within approximately 24 hours.
7. Download and unzip the archive. It will contain a folder of CSV files.

**Key files the skill uses:**

| File | Purpose |
|------|---------|
| `Connections.csv` | Core network data (name, company, position, date) |
| `messages.csv` | Full message history with conversation threads |
| `Invitations.csv` | Inbound/outbound connection requests |
| `Company Follows.csv` | Companies the user follows |
| `Inferences_about_you.csv` | LinkedIn's algorithmic guesses about the user |
| `Ad_Targeting.csv` | Advertiser targeting categories applied to the user |

**Gate:** Ask the user to confirm they have their LinkedIn data export ready before proceeding.

---

### Step 2: Locate Files

Ask the user for the path to their CSV folder.

**Claude actions:**

1. Ask: "Where is your LinkedIn data export folder? Provide the full path to the directory containing the CSV files."
2. Validate the folder exists.
3. Check for the presence of key files. At minimum, these three must exist:
   - `Connections.csv`
   - `messages.csv`
   - `Company Follows.csv`
4. Scan for all recognized CSV files and report what was found.

**Example response to user:**

```
Found your LinkedIn export at /Users/you/Downloads/linkedin-data/

  [found] Connections.csv
  [found] messages.csv
  [found] Invitations.csv
  [found] Company Follows.csv
  [found] Inferences_about_you.csv
  [found] Ad_Targeting.csv

All 6 data files detected. Ready to analyze.
```

If optional files are missing, note which visualizations will be skipped but proceed with what is available.

**Gate:** Confirm files are located and ask user to proceed to analysis preview.

---

### Step 3: Analysis Preview

Parse the CSV files and display summary statistics. Then let the user choose which visualizations to generate.

**Claude actions:**

1. Run `scripts/parse_csvs.py <input_dir>` to parse all CSV files.
2. Display summary stats:
   - Total connections and date range (earliest to latest)
   - Message count and unique conversation count
   - Companies followed
   - Invitations sent vs received
   - Number of inferences LinkedIn made
   - Number of ad targeting categories
3. Present visualization options:

```
Which visualizations would you like to generate?

  (a) All 9 visualizations + unified dashboard
  (b) Pick specific ones:
      1. Network Universe — Force-directed graph of connections by role
      2. Inferences vs Reality — LinkedIn's guesses vs actual data
      3. High-Value Messages — Unanswered messages ranked by value
      4. Company Follows Clustering — Followed companies by industry
      5. Inbound vs Outbound — Connection request patterns over time
      6. Connection Quality — Relationship depth analysis
      7. Connection Timeline — Recent connections with engagement
      8. Inbox Quality — Genuine vs noise messages over time
      9. Career Strata — Network as geological layers by career phase
  (c) Quick sample (Network Universe + Career Strata only)
```

**Gate:** Wait for user selection before generating.

---

### Step 4: Theme Selection

Ask the user which theme to apply.

**Claude actions:**

1. Present options:
   - **Carrier Dark** (default) -- dark-mode SaaS aesthetic with teal accents. Ships with the skill at `assets/carrier-dark.css`.
   - **Custom** -- user provides a path to their own CSS file, or the skill can generate a copy of Carrier Dark for them to modify.
2. If user picks Carrier Dark, use `assets/carrier-dark.css`.
3. If user picks custom, either accept a file path or copy `assets/carrier-dark.css` to a new file and tell the user which CSS custom properties to modify (see REFERENCE.md for details).

**Gate:** Confirm theme selection before generating.

---

### Step 5: Generation

Parse, analyze, and generate HTML files. Show progress throughout.

**Claude actions:**

1. Run `scripts/analyze.py <input_dir> --output <output_dir>` to perform all analysis and produce `analysis.json`.
2. Run `scripts/generate.py <output_dir> --theme <theme_css_path> --vizzes <comma_separated_list>` to inject data and theme into HTML templates.
3. Show progress for each step:

```
[1/4] Parsing CSV files...              done (1,247 connections)
[2/4] Running analysis algorithms...     done (9 analyses complete)
[3/4] Generating HTML visualizations...  done (9 files + dashboard)
[4/4] Copying assets...                  done

Output directory: /Users/you/linkedin-viz-output/

Generated files:
  01-network-universe.html
  02-inferences-vs-reality.html
  03-high-value-messages.html
  04-company-follows-clustering.html
  05-inbound-vs-outbound.html
  06-connection-quality.html
  07-connection-timeline.html
  08-inbox-quality.html
  09-career-strata.html
  dashboard.html
```

4. Tell the user they can open any HTML file directly in a browser -- no server required.

**Gate:** Confirm output was generated successfully. The wizard is complete.

---

## The 9 Visualizations

### 1. Network Universe

D3.js force-directed graph. Connections are nodes clustered into role-based groups (Engineering, Marketing, Sales, etc.). Node size reflects connection count within each cluster. Hovering reveals company and position details. Uses `Connections.csv`.

### 2. Inferences vs Reality

Side-by-side comparison of what LinkedIn's algorithms infer about the user versus what the actual data shows. Each inference gets a verdict: Accurate, Partial, or Wrong. Uses `Inferences_about_you.csv`, `Ad_Targeting.csv`, `Connections.csv`.

### 3. High-Value Messages

Unanswered messages ranked by potential value. Scores based on sender role, recency, message content signals, and relationship strength. Filterable by urgency tier (Hot, Warm, Cool). Uses `messages.csv`, `Connections.csv`.

### 4. Company Follows Clustering

Companies the user follows grouped by industry via keyword matching. Displayed as cluster cards with company counts and tag clouds. Uses `Company Follows.csv`.

### 5. Inbound vs Outbound

Connection request patterns visualized over time. Shows ratio of sent vs received invitations with trend lines. Uses `Invitations.csv`.

### 6. Connection Quality

Relationship depth analysis. Categorizes every connection into tiers: Active (regular messaging), Dormant (connected but no recent messages), and Never Messaged. Doughnut chart + breakdown rows. Uses `Connections.csv`, `messages.csv`.

### 7. Connection Timeline

Tabular view of the most recent connections with engagement data. Shows direction (inbound/outbound), company, date connected, and message count. Uses `Connections.csv`, `Invitations.csv`, `messages.csv`.

### 8. Inbox Quality

Message volume over time split into Genuine (real conversations) vs Noise (spam, InMail, automated). Stacked area chart with trend analysis. Uses `messages.csv`.

### 9. Career Strata

The user's network visualized as geological layers by career phase. Each stratum represents a time period, colored from deep (oldest) to elevated (newest). Shows connection count and percentage per era. Uses `Connections.csv`.

---

## Script Reference

All scripts live in `scripts/` and are invoked by Claude during the wizard flow.

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `parse_csvs.py` | Parse and validate all CSV files | CSV directory path | Parsed data structures (stdout summary) |
| `analyze.py` | Run all analysis algorithms | CSV directory, output directory | `analysis.json` in output dir |
| `generate.py` | Inject data + theme into HTML templates | Output dir, theme CSS path, viz list | HTML files in output dir |

Templates live in `templates/` and use `{{DATA}}` and `{{THEME_CSS}}` placeholders.

The theme CSS file lives in `assets/carrier-dark.css`.

Prompt references for analysis customization are in `references/prompts.md`.
