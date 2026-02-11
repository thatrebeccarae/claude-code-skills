---
name: linkedin-data-viz
description: >
  Analyze and visualize LinkedIn data exports. Generates 10 interactive
  HTML visualizations from CSV files including network force graphs,
  message analysis, connection quality scoring, and career timelines.
  Use when the user mentions LinkedIn data export, LinkedIn visualization,
  LinkedIn network analysis, or wants to analyze their LinkedIn connections.
---

# LinkedIn Data Viz Skill

This skill transforms a LinkedIn data export into 10 interactive HTML visualizations with a unified dashboard. It walks the user through a wizard flow: checking prerequisites, locating their export, previewing analysis, selecting a theme, and generating output. All data stays local on the user's machine.

---

## Wizard Flow

### Step 1: Preflight Check

Before anything else, verify the user's environment can run the skill.

**Claude actions:**

1. Check Python version:
   ```
   python3 --version
   ```
   Require **Python 3.9 or later**. If the user has an older version or `python3` is not found, give them platform-specific install guidance:
   - **macOS:** `brew install python` or download from python.org
   - **Windows:** Download from python.org (check "Add to PATH" during install)
   - **Linux:** `sudo apt install python3` (Ubuntu/Debian) or `sudo dnf install python3` (Fedora)

2. Confirm the skill directory is accessible by checking that `scripts/parse_export.py` exists relative to the skill install path.

3. Create (or confirm) an output directory. Suggest a default:
   ```
   mkdir -p ~/linkedin-viz-output
   ```
   Ask the user if they want to use this location or specify their own.

**Example response to user:**

```
Let's make sure everything is set up.

  Python 3.12.1 -- good to go
  Skill scripts found at ~/.claude/skills/linkedin-data-viz/scripts/
  Output directory: ~/linkedin-viz-output/

All clear. Let's get started.
```

**If Python is missing or too old**, stop here and help the user install it before continuing. Do not proceed to Step 2 until the preflight passes.

---

### Step 2: Export Guidance

Tell the user how to request their LinkedIn data archive if they have not already done so. If they already have their export, skip ahead to Step 3.

**Instructions to share with the user:**

> Here's how to get your LinkedIn data export:
>
> 1. Go to [LinkedIn Settings](https://www.linkedin.com/mypreferences/d/download-my-data) (or click your profile photo > "Settings & Privacy" > "Data privacy")
> 2. Click **Get a copy of your data**
> 3. Select **all categories** (or at minimum: Connections, Messages, Invitations, Company Follows, Inferences, Ad Targeting)
> 4. Click **Request archive**
> 5. LinkedIn will email you a download link within ~24 hours
> 6. Download and unzip the archive -- it will contain a folder of CSV files
>
> Already have your export? Just tell me the folder path and we'll jump right in.

**Key files the skill uses:**

| File | Required? | Purpose |
|------|-----------|---------|
| `Connections.csv` | Required | Core network data (name, company, position, date) |
| `messages.csv` | Required | Full message history with conversation threads |
| `Company Follows.csv` | Required | Companies the user follows |
| `Invitations.csv` | Optional | Inbound/outbound connection requests |
| `Inferences_about_you.csv` | Optional | LinkedIn's algorithmic guesses about the user |
| `Ad_Targeting.csv` | Optional | Advertiser targeting categories applied to the user |
| `Shares.csv` | Optional | Posts/shares created by the user (enables posting correlation) |

**Gate:** Ask the user to confirm they have their LinkedIn data export ready before proceeding.

---

### Step 3: Locate Files

Ask the user for the path to their CSV folder.

**Claude actions:**

1. Ask: "Where is your LinkedIn data export folder? You can drag the folder into this terminal window to paste the path, or type it out."
2. Validate the folder exists using `ls` or a file check.
3. Check for the presence of key files. At minimum, these three **must** exist:
   - `Connections.csv`
   - `messages.csv`
   - `Company Follows.csv`
4. Scan for all recognized CSV files and report what was found.

**Common locations to suggest if the user isn't sure:**
- macOS: `~/Downloads/` (look for a folder like `Basic_LinkedInDataExport_MM-DD-YYYY`)
- Windows: `C:\Users\<name>\Downloads\`
- Linux: `~/Downloads/`

**Example response to user:**

```
Found your LinkedIn export at /Users/you/Downloads/Basic_LinkedInDataExport_01-15-2026/

  [found] Connections.csv          (required)
  [found] messages.csv             (required)
  [found] Company Follows.csv      (required)
  [found] Invitations.csv          (optional -- enables inbound/outbound analysis)
  [found] Inferences_about_you.csv (optional -- enables inference verdicts)
  [found] Ad_Targeting.csv         (optional -- enables ad targeting analysis)
  [skip]  Shares.csv               (not found -- posting correlation will be skipped)

6 of 7 data files detected. Ready to analyze.
```

**If required files are missing**, stop and help the user:
- Confirm they unzipped the archive (common mistake: trying to use the .zip directly)
- Check if the CSVs are in a subdirectory
- Verify they selected the right categories when requesting their export

**Gate:** Confirm files are located and ask user to proceed to analysis preview.

---

### Step 4: Analysis Preview

Parse the CSV files and display summary statistics so the user can see their data before committing to generation.

**Claude actions:**

1. Run the parser to extract and validate all CSV data:
   ```
   python3 <skill_path>/scripts/parse_export.py <csv_folder> -o <output_dir>/parsed.json
   ```
2. If the parser succeeds, read the output and display summary stats:
   - Total connections and date range (earliest to latest)
   - Message count and unique conversation count
   - Companies followed
   - Invitations sent vs received (if available)
   - Number of inferences LinkedIn made (if available)
   - Number of ad targeting categories (if available)

3. **What to expect:** Give the user a preview of what they'll get:

```
Here's what your export contains:

  2,264 connections (2012 to 2026)
  8,412 messages across 1,847 conversations
  186 companies followed
  1,124 invitations (638 inbound, 486 outbound)
  47 inferences LinkedIn made about you
  312 ad targeting categories

Based on your data, I can generate these 10 visualizations:

  1.  Network Universe        -- Force-directed graph of connections by role
  2.  Inferences vs Reality   -- LinkedIn's guesses vs actual data
  3.  High-Value Messages     -- Unanswered messages ranked by value
  4.  Company Follows         -- Followed companies by industry
  5.  Inbound vs Outbound     -- Connection request patterns over time
  6.  Connection Quality      -- Relationship depth analysis
  7.  Connection Timeline     -- Recent connections with engagement
  8.  Inbox Quality           -- Genuine vs noise messages over time
  9.  Does Posting Work?      -- Posting frequency vs connection growth
  10. Career Strata           -- Network as geological layers by career phase

Plus a unified dashboard that links them all together.

  (a) Generate all 10 + dashboard (recommended)
  (b) Pick specific ones
  (c) Quick sample (Network Universe + Career Strata only)
```

**If the parser fails**, check for common issues before showing the error:
- `UnicodeDecodeError` -- the CSV might have unusual encoding. Try: `python3 <script> <folder> -o <output> -v` for verbose output.
- `KeyError` on a column name -- LinkedIn may have changed their export format. Show the user the actual column names found and suggest checking for renamed columns.
- Empty data -- the file exists but has no rows. Confirm the user exported with the right categories selected.

**Gate:** Wait for user selection before generating.

---

### Step 5: Theme Selection

Ask the user which visual theme to apply.

**Claude actions:**

1. Present options:
   - **Carrier Dark** (recommended) -- dark-mode SaaS aesthetic with teal accents. Ships with the skill at `assets/carrier-dark.css`.
   - **Custom** -- user provides a path to their own CSS file, or the skill can copy Carrier Dark as a starting point for modification.
2. If user picks Carrier Dark (most will), use `assets/carrier-dark.css`. Move on.
3. If user picks custom, copy `assets/carrier-dark.css` to a new file and point the user to the CSS custom properties section in REFERENCE.md.

For most users, just default to Carrier Dark and keep moving.

**Gate:** Confirm theme selection before generating.

---

### Step 6: Generation

Run the full analysis and generation pipeline. Show progress throughout so the user knows things are working.

**Claude actions:**

1. **Parse** -- convert CSVs to structured data:
   ```
   python3 <skill_path>/scripts/parse_export.py <csv_folder> -o <output_dir>/parsed.json
   ```
   (Skip if already completed in Step 4.)

2. **Analyze** -- run all analysis algorithms on the parsed data:
   ```
   python3 <skill_path>/scripts/analyze.py <output_dir>/parsed.json -o <output_dir>/analysis.json
   ```

3. **Generate** -- inject data and theme into HTML templates:
   ```
   python3 <skill_path>/scripts/generate_viz.py \
     --templates <skill_path>/templates/ \
     --data <output_dir>/analysis.json \
     --output <output_dir> \
     --theme <skill_path>/assets/carrier-dark.css
   ```

4. Show progress for each step:

```
[1/3] Parsing CSV files...              done (2,264 connections, 8,412 messages)
[2/3] Running analysis algorithms...     done (8 analyses complete)
[3/3] Generating HTML visualizations...  done (10 files + dashboard)

Output directory: ~/linkedin-viz-output/

Generated files:
  01-network-universe.html
  02-inferences-vs-reality.html
  03-high-value-messages.html
  04-company-follows.html
  05-inbound-outbound.html
  06-connection-quality.html
  07-connection-timeline.html
  08-inbox-quality.html
  09-posting-correlation.html
  10-career-strata.html
  dashboard.html
```

5. **Help the user open their results:**

```
To view your visualizations, open any HTML file in your browser:

  macOS:  open ~/linkedin-viz-output/dashboard.html
  Windows: start ~/linkedin-viz-output/dashboard.html
  Linux:  xdg-open ~/linkedin-viz-output/dashboard.html

No server required -- everything runs locally in your browser.
```

Run the appropriate `open` command for the user's platform to launch the dashboard automatically.

**If a script fails during generation:**
- Show the full error message to the user.
- If it's a Python error, check the traceback for the specific file and line.
- Common fix: if analyze.py fails on date parsing, run with `-v` flag for verbose output to identify which CSV row has the malformed date.
- Do not silently skip errors -- always surface them clearly.

**Gate:** Confirm output was generated successfully before proceeding to the next step.

---

### Step 7: What's Next

After successful generation, offer the user three optional next steps.

**Claude actions:**

Present these options conversationally -- do not require the user to pick one. They can say "that's it" and the wizard is complete.

**Option A: Narrative Insights**

> Want me to walk through your visualizations and give you a narrative analysis? I can highlight patterns, surprises, and actionable takeaways from your data -- like which part of your network is strongest, whether posting actually helped you grow, and who you should probably message back.

If the user says yes, use the prompts in `references/prompts.md` to generate narrative insights for each visualization. Read the `analysis.json` output and provide a written summary covering:
- Network composition and blind spots (from Network Universe data)
- Whether LinkedIn's inferences are accurate (from Inferences data)
- High-priority messages to respond to (from High-Value Messages data)
- Career network evolution (from Career Strata data)
- Whether posting drives growth (from Posting Correlation data)
- Overall network health score (from Connection Quality data)

**Option B: Sanitize for Sharing**

> Want to share your visualizations publicly? I can run the sanitizer to replace real names and companies with plausible fakes -- all the patterns stay intact but your contacts' privacy is protected.

If the user says yes, run the sanitizer:
```
python3 <skill_path>/scripts/sanitize.py <output_dir>/analysis.json -o <output_dir>/sanitized.json
```
Then regenerate the HTML files using the sanitized data:
```
python3 <skill_path>/scripts/generate_viz.py \
  --templates <skill_path>/templates/ \
  --data <output_dir>/sanitized.json \
  --output <output_dir>/public/ \
  --theme <skill_path>/assets/carrier-dark.css
```

**Option C: Custom Theme**

> Want to customize the look? I can set up a copy of the theme CSS for you to modify -- colors, fonts, spacing are all configurable via CSS custom properties.

If the user says yes, copy the theme and point them to the relevant section in REFERENCE.md.

---

## The 10 Visualizations

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

### 9. Does Posting Actually Work?

Dual-axis chart correlating posting frequency (line) with new connection growth (bars) over time. Calculates the Pearson correlation coefficient and surfaces key metrics: percentage increase in connections during active posting periods, and average connections per month before vs after consistent posting. Uses `Shares.csv`, `Connections.csv`.

### 10. Career Strata

The user's network visualized as geological layers by career phase. Each stratum represents a time period, colored from deep (oldest) to elevated (newest). Shows connection count and percentage per era. Uses `Connections.csv`.

---

## Script Reference

All scripts live in `scripts/` and are invoked by Claude during the wizard flow. They use only Python 3.9+ stdlib -- no pip installs required.

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `parse_export.py` | Parse and validate all CSV files | CSV folder path | `parsed.json` (structured data) |
| `analyze.py` | Run all analysis algorithms | `parsed.json` from parse step | `analysis.json` (analysis results) |
| `generate_viz.py` | Inject data + theme into HTML templates | `analysis.json`, templates dir, theme CSS | HTML files in output dir |
| `sanitize.py` | Strip PII from analysis data for sharing | `analysis.json` | `sanitized.json` with fake names/companies |

**Pipeline order:** `parse_export.py` -> `analyze.py` -> `generate_viz.py`

Templates live in `templates/` and use `{{DATA}}` and `{{THEME_CSS}}` placeholders.

The theme CSS file lives in `assets/carrier-dark.css`.

Prompt references for analysis customization and narrative insights are in `references/prompts.md`.

---

## Troubleshooting

Common issues and how to resolve them:

| Problem | Cause | Fix |
|---------|-------|-----|
| `python3: command not found` | Python not installed or not in PATH | Install Python 3.9+ (see Step 1) |
| `SyntaxError` on script run | Python version too old (3.8 or earlier) | Upgrade to Python 3.9+ |
| `FileNotFoundError` on a CSV | File missing from export | Re-export from LinkedIn with all categories selected |
| `UnicodeDecodeError` | Unusual characters in CSV | Run with `-v` flag; the verbose output will show which file/row fails |
| `KeyError` on column name | LinkedIn changed their export format | Run `head -1 <file>.csv` to check actual column names; report the issue |
| Parser succeeds but analysis fails | Date format not recognized | Run `analyze.py` with `-v` to see which row has the bad date |
| HTML files are blank | `analysis.json` is empty or malformed | Check that `analyze.py` completed without errors; re-run with `-v` |
| Charts don't render in browser | JavaScript blocked or old browser | Try Chrome, Firefox, or Edge; ensure JavaScript is enabled |
| `Shares.csv` not found | User didn't post on LinkedIn, or didn't select Shares in export | Safe to skip -- posting correlation visualization will be omitted |
| `Permission denied` on output dir | Output path is not writable | Choose a different output directory (e.g., `~/linkedin-viz-output/`) |
