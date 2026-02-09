# Looker Studio DTC Dashboard Examples

Practical examples of building dashboards for DTC e-commerce teams using Klaviyo, Shopify, and GA4 data.

## Example 1: CRM Performance Dashboard

**User Request**: "Build a Looker Studio dashboard to track our Klaviyo email and SMS performance"

**Setup Steps**:
1. Sync Klaviyo data to Google Sheets
2. Connect the Sheet as a data source in Looker Studio
3. Build dashboard pages with KPIs, trends, and engagement tiers

**Data Pipeline Command**:
```bash
# Create the pre-formatted sheet
python scripts/data_pipeline.py --action create-sheet --template crm-dashboard

# Sync Klaviyo data
python scripts/data_pipeline.py --action sync-klaviyo --sheet-id YOUR_SHEET_ID
```

**Dashboard Layout**:
```
Page 1: Email & SMS Overview
|- Scorecards: Total Email Revenue, Total SMS Revenue, List Size, Avg Open Rate
|- Revenue trend: Email vs SMS over time (area chart, last 90 days)
|- Campaign performance table (sortable by revenue, click rate)
|- Engagement tier donut: Active / Warm / At-Risk / Lapsed

Page 2: Flow Performance
|- Flow revenue table with conditional formatting
|- Top 5 flows by revenue (horizontal bar)
|- Click rate by flow (bar chart with benchmark line)
|- Monthly flow revenue trend
```

**Key Calculated Fields**:
```
# Open Rate (from Sheets data)
SUM(Opens) / SUM(Recipients) * 100

# Click-to-Open Rate
SUM(Clicks) / SUM(Opens) * 100

# Revenue Per Recipient
SUM(Revenue) / SUM(Recipients)

# Engagement Tier (if days_since_last_open is in your data)
CASE
  WHEN days_since_last_open <= 30 THEN "Active (0-30d)"
  WHEN days_since_last_open <= 90 THEN "Warm (31-90d)"
  WHEN days_since_last_open <= 180 THEN "At-Risk (91-180d)"
  ELSE "Lapsed (180d+)"
END
```

**Expected Insights**:
- Flow vs campaign revenue split (healthy: flows = 40-60% of email revenue)
- Engagement tier distribution (warning if Active < 30%)
- Revenue per recipient trends (declining = list fatigue)

## Example 2: Lifecycle Marketing Dashboard

**User Request**: "I want to see how our Klaviyo flows perform across the customer lifecycle"

**Setup Steps**:
1. Sync Klaviyo flow data with lifecycle stage tagging
2. Map flows to customer journey stages
3. Build stage-by-stage performance view

**Data Pipeline Command**:
```bash
python scripts/data_pipeline.py --action create-sheet --template lifecycle
python scripts/data_pipeline.py --action sync-klaviyo --sheet-id YOUR_SHEET_ID
```

**Dashboard Layout**:
```
Page 1: Lifecycle Overview
|- Stage funnel (shapes): Prospect -> New -> Active -> VIP -> At-Risk -> Lapsed
|- Revenue by stage (horizontal bar, color-coded by stage)
|- Customer count by stage (donut)
|- Stage transition rates table

Page 2: Flow Detail (with filter control)
|- Dropdown: Select lifecycle stage
|- Filtered flow table: all flows in selected stage
|- Revenue trend for selected stage (line chart)
|- Key metrics: messages sent, delivered, opened, clicked, converted
```

**Key Calculated Fields**:
```
# Lifecycle Stage from Flow Name
CASE
  WHEN REGEXP_MATCH(Flow_Name, "(?i)welcome|sign.?up|lead") THEN "Prospect -> New"
  WHEN REGEXP_MATCH(Flow_Name, "(?i)post.?purchase|thank|review") THEN "New -> Active"
  WHEN REGEXP_MATCH(Flow_Name, "(?i)abandon|browse|cart") THEN "Active Engagement"
  WHEN REGEXP_MATCH(Flow_Name, "(?i)vip|loyal|reward") THEN "VIP"
  WHEN REGEXP_MATCH(Flow_Name, "(?i)win.?back|re.?engage|sunset") THEN "At-Risk -> Lapsed"
  WHEN REGEXP_MATCH(Flow_Name, "(?i)replenish|reorder") THEN "Active Retention"
  ELSE "Other"
END

# Conversion Rate
SUM(Conversions) / SUM(Messages_Sent) * 100

# Revenue per Message
SUM(Revenue) / SUM(Messages_Sent)
```

**Expected Insights**:
- Which lifecycle stages generate the most revenue
- Gap identification: stages without flows need coverage
- Win-back effectiveness: is the sunset/re-engagement flow actually recovering customers?

## Example 3: Revenue Attribution Dashboard

**User Request**: "Help me reconcile Klaviyo-attributed revenue with Shopify actuals"

**Setup Steps**:
1. Sync both Klaviyo revenue data and Shopify order data to Sheets
2. Blend on date dimension in Looker Studio
3. Build comparison view with gap analysis

**Data Pipeline Commands**:
```bash
python scripts/data_pipeline.py --action create-sheet --template revenue-attribution
python scripts/data_pipeline.py --action sync-klaviyo --sheet-id YOUR_SHEET_ID
python scripts/data_pipeline.py --action sync-shopify --sheet-id YOUR_SHEET_ID --days 30
```

**Dashboard Layout**:
```
Page 1: Attribution Overview
|- Scorecards: Shopify Revenue, Klaviyo Attributed, Attribution %, Gap Amount
|- Daily comparison: Shopify total vs Klaviyo attributed (dual-axis combo chart)
|- Attribution percentage trend (line chart with 30-day moving average)
|- Channel breakdown table: email, SMS, flows, campaigns (Klaviyo side)

Page 2: Deep Dive
|- Shopify revenue by source (UTM-based breakdown)
|- Klaviyo revenue by channel and flow/campaign
|- Date-level reconciliation table (sortable, with gap column)
|- Notes field for explaining discrepancies
```

**Key Calculated Fields**:
```
# Attribution Percentage (blended data)
SUM(Klaviyo_Revenue) / SUM(Shopify_Revenue) * 100

# Revenue Gap
SUM(Shopify_Revenue) - SUM(Klaviyo_Revenue)

# Over-Attribution Flag
CASE
  WHEN SUM(Klaviyo_Revenue) > SUM(Shopify_Revenue) * 1.1 THEN "Over-Attributed"
  WHEN SUM(Klaviyo_Revenue) < SUM(Shopify_Revenue) * 0.15 THEN "Under-Attributed"
  ELSE "Normal Range"
END
```

**Expected Insights**:
- Typical Klaviyo attribution: 25-45% of Shopify revenue
- Over-attribution (>50%) signals overlap with other channels or double-counting
- Under-attribution (<15%) suggests tracking gaps in flows/campaigns
- Discrepancies often spike during sales events (multiple touchpoints)

## Example 4: Campaign ROI Tracker

**User Request**: "I want to compare campaign performance week-over-week and find what works"

**Setup Steps**:
1. Sync campaign data from Klaviyo
2. Build filterable campaign comparison view
3. Add A/B test result tracking

**Data Pipeline Command**:
```bash
python scripts/data_pipeline.py --action create-sheet --template campaign-performance
python scripts/data_pipeline.py --action sync-klaviyo --sheet-id YOUR_SHEET_ID
```

**Dashboard Layout**:
```
Page 1: Campaign Scorecard
|- Date range filter + channel filter (email/SMS)
|- Campaign table: date, name, subject line, recipients, opens,
   open rate, clicks, click rate, revenue, RPR
|- Conditional formatting: green if above benchmark, red if below
|- Revenue per recipient trend (line chart, weekly aggregation)
|- Top 10 subject lines by open rate (horizontal bar)

Page 2: Optimization Insights
|- Send time heatmap (day of week x hour of day -> color = open rate)
|- Audience size vs conversion rate scatter plot
|- Campaign frequency: sends per subscriber per week (trend)
|- A/B test results table (variant A vs B, winner highlighted)
```

**Key Calculated Fields**:
```
# Revenue Per Recipient
SUM(Revenue) / SUM(Recipients)

# Click-to-Open Rate
SUM(Clicks) / SUM(Opens) * 100

# Performance vs Benchmark
CASE
  WHEN Open_Rate >= 0.25 THEN "Above Benchmark"
  WHEN Open_Rate >= 0.18 THEN "At Benchmark"
  ELSE "Below Benchmark"
END

# Send Day
FORMAT_DATETIME("%A", Send_Date)

# Send Hour
FORMAT_DATETIME("%H", Send_Date)
```

**Expected Insights**:
- Revenue per recipient trend reveals list fatigue or improvement
- Send time heatmap shows optimal scheduling (typically Tue-Thu, 10am-2pm)
- A/B test patterns across multiple tests reveal audience preferences

## Example 5: Customer Cohort Dashboard

**User Request**: "Build a dashboard showing customer cohort LTV and retention"

**Setup Steps**:
1. Sync Shopify order data with customer first-order date
2. Calculate cohort metrics in Sheets or Looker Studio
3. Build cohort visualization

**Data Pipeline Command**:
```bash
python scripts/data_pipeline.py --action sync-shopify --sheet-id YOUR_SHEET_ID --days 180
```

**Dashboard Layout**:
```
Page 1: Cohort Overview
|- Monthly acquisition cohort table (rows = cohort month, columns = month 1-6 LTV)
|- Conditional formatting: darker green = higher LTV
|- Cumulative LTV curve by cohort (line chart, one line per monthly cohort)
|- Repeat purchase rate by cohort (bar chart)
|- New vs returning customer revenue split (stacked area)

Page 2: Retention Analysis
|- Retention waterfall: % of cohort that purchased in month 2, 3, 4...
|- Average time between first and second purchase (histogram)
|- Cohort size trend (bar chart of new customers per month)
|- LTV:CAC ratio by acquisition channel (if ad spend data available)
```

**Key Calculated Fields**:
```
# Cohort Month (from first order date)
FORMAT_DATETIME("%Y-%m", First_Order_Date)

# Months Since First Purchase
DATE_DIFF(Order_Date, First_Order_Date) / 30

# Cumulative LTV
SUM(Order_Total)

# Is Repeat Customer
CASE
  WHEN Order_Count > 1 THEN "Repeat"
  ELSE "One-Time"
END

# Repeat Purchase Rate
COUNT_DISTINCT(CASE WHEN Order_Count > 1 THEN Customer_Email ELSE NULL END)
  / COUNT_DISTINCT(Customer_Email) * 100
```

**Expected Insights**:
- Healthy LTV curves show steady increase over 6+ months
- Flat curves after month 1 = retention problem (need post-purchase flows)
- Compare cohorts: are newer cohorts retaining better? (validates improvements)
- Time-to-second-purchase sweet spot informs win-back flow timing

## Example 6: Data Pipeline Setup Walkthrough

**User Request**: "Walk me through setting up the data pipeline from scratch"

**Full Setup Steps**:

### Step 1: Create Google Service Account
```
1. Go to https://console.cloud.google.com
2. Create project (or select existing)
3. Enable Google Sheets API and Google Drive API
4. IAM & Admin > Service Accounts > Create Service Account
5. Download JSON key file
6. Store securely (NOT in your repo)
```

### Step 2: Configure Environment
```bash
# Create .env file in the looker-studio skill directory
cp .env.example .env

# Edit .env with your credentials path
GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/your-service-account.json
KLAVIYO_API_KEY=pk_your_key_here
SHOPIFY_STORE_URL=https://your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_your_token_here
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create a Dashboard Sheet
```bash
python scripts/data_pipeline.py --action list-templates
```
Output:
```json
{
  "templates": {
    "crm-dashboard": "CRM Performance Dashboard -- email/SMS KPIs, list growth, engagement tiers",
    "lifecycle": "Lifecycle Marketing Dashboard -- flow performance across customer journey",
    "campaign-performance": "Campaign ROI Tracker -- campaign comparison, A/B test results",
    "revenue-attribution": "Revenue Attribution Dashboard -- Klaviyo vs Shopify reconciliation"
  }
}
```

```bash
python scripts/data_pipeline.py --action create-sheet --template crm-dashboard
```
Output:
```json
{
  "status": "success",
  "spreadsheet_id": "1BxiMVs0XRA5nFMdKv...",
  "spreadsheet_url": "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKv...",
  "template": "crm-dashboard",
  "sheets_created": ["Campaign Metrics", "Flow Metrics", "List Growth"],
  "next_steps": [
    "Share the sheet with your team",
    "Run sync commands to populate",
    "Connect this Sheet as a data source in Looker Studio"
  ]
}
```

### Step 5: Sync Data
```bash
# Sync Klaviyo campaign and flow data
python scripts/data_pipeline.py --action sync-klaviyo --sheet-id 1BxiMVs0XRA5nFMdKv...

# Sync Shopify orders (last 30 days)
python scripts/data_pipeline.py --action sync-shopify --sheet-id 1BxiMVs0XRA5nFMdKv... --days 30
```

### Step 6: Connect in Looker Studio
```
1. Go to https://lookerstudio.google.com
2. Create > Report
3. Add data source > Google Sheets
4. Select your spreadsheet and sheet tab
5. Configure field types (set Date columns to Date type)
6. Start building charts
```

### Step 7: Automate (Optional)
Set up a daily cron job or n8n workflow to keep data fresh:
```bash
# crontab -e
0 6 * * * cd /path/to/looker-studio/scripts && python data_pipeline.py --action sync-klaviyo --sheet-id YOUR_ID
0 6 * * * cd /path/to/looker-studio/scripts && python data_pipeline.py --action sync-shopify --sheet-id YOUR_ID --days 7
```

## Pro Tips

### Pick the Right Template
- **Starting from scratch?** Use `crm-dashboard` for the broadest view
- **Revenue questions?** Use `revenue-attribution` to reconcile Klaviyo vs Shopify
- **Optimizing flows?** Use `lifecycle` to see journey-stage performance
- **Campaign testing?** Use `campaign-performance` for A/B and timing insights

### Blend for Cross-Platform Views
In Looker Studio, blend Klaviyo and Shopify sheets on the Date dimension to get unified views like:
- Email revenue as % of total Shopify revenue
- Campaign sends correlated with order spikes
- Discount usage in Shopify overlaid with promo campaigns in Klaviyo

### Keep Data Fresh
Google Sheets data in Looker Studio caches for ~15 minutes. For real-time needs:
- Use Looker Studio's "Data freshness" setting (1 minute minimum)
- Click the refresh button in the report for immediate update
- Schedule pipeline syncs every 6 hours for daily dashboards
