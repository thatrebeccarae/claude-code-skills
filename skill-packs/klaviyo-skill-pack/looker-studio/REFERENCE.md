# Looker Studio Reference

## Data Source Connectors

### Native (Free) Google Connectors
| Connector | Data Available |
|-----------|---------------|
| Google Analytics 4 | Sessions, users, events, conversions, ecommerce, demographics |
| Google Ads | Campaigns, keywords, ads, conversions, quality score, auction insights |
| Google Sheets | Any tabular data (manual or API-fed) |
| BigQuery | SQL-queryable data warehouse |
| Search Console | Queries, pages, impressions, clicks, CTR, position |
| YouTube Analytics | Views, watch time, subscribers, demographics, revenue |
| Google Cloud Storage | CSV, JSON files |
| Campaign Manager 360 | Display & video campaign data |
| Display & Video 360 | Programmatic campaign data |

### Popular Partner Connectors
| Connector | Provider | Cost |
|-----------|----------|------|
| Facebook Ads | Supermetrics, Funnel, Windsor.ai | $30-100/mo |
| Microsoft Ads | Supermetrics, Windsor.ai | $30-100/mo |
| LinkedIn Ads | Supermetrics | $30-100/mo |
| HubSpot | Supermetrics, Porter Metrics | $30-100/mo |
| Shopify | Supermetrics, Coupler.io | $30-100/mo |
| Klaviyo | Supermetrics | $30-100/mo |
| Salesforce | Supermetrics | $50-150/mo |
| TikTok Ads | Supermetrics | $30-100/mo |
| Semrush | Supermetrics | $30-100/mo |

### Free Workarounds
- Use Google Sheets as intermediary (pull data via API/Zapier/n8n -> Sheet -> Looker Studio)
- BigQuery: Load data from any source, connect natively
- CSV upload: Manual periodic updates

## Calculated Fields Reference

### Data Types
| Type | Description | Example |
|------|-------------|---------|
| Number | Numeric values | SUM(revenue) |
| Text | String values | CONCAT(first_name, " ", last_name) |
| Date | Date/datetime | TODATE(date_string, 'BASIC', '%Y%m%d') |
| Boolean | True/false | clicks > 100 |
| Geo | Geographic data | Country, city |

### Arithmetic
```
# Basic math
revenue - cost                        # Profit
(revenue - cost) / revenue * 100      # Profit Margin %
SUM(revenue) / SUM(cost)              # ROAS
SUM(conversions) / SUM(clicks) * 100  # Conversion Rate %
SUM(cost) / SUM(conversions)          # CPA
SUM(clicks) / SUM(impressions) * 100  # CTR %
```

### Text Functions
```
# Concatenation
CONCAT(source, " / ", medium)

# Substring
SUBSTR(campaign_name, 1, 10)

# Replace
REPLACE(url, "https://", "")

# Lowercase/Uppercase
LOWER(source)
UPPER(medium)

# Length
LENGTH(page_title)

# Contains check (returns boolean)
CONTAINS_TEXT(campaign_name, "brand")
```

### CASE Statements
```
# Custom channel grouping
CASE
  WHEN REGEXP_MATCH(source_medium, "(?i)google.*cpc") THEN "Google Ads"
  WHEN REGEXP_MATCH(source_medium, "(?i)(facebook|fb|meta|ig).*paid") THEN "Meta Ads"
  WHEN REGEXP_MATCH(source_medium, "(?i)bing.*cpc") THEN "Microsoft Ads"
  WHEN REGEXP_MATCH(source_medium, "(?i)linkedin.*cpc") THEN "LinkedIn Ads"
  WHEN REGEXP_MATCH(medium, "(?i)email") THEN "Email"
  WHEN REGEXP_MATCH(medium, "(?i)organic") THEN "Organic Search"
  WHEN REGEXP_MATCH(medium, "(?i)(social|facebook|instagram|twitter|linkedin)") THEN "Organic Social"
  WHEN REGEXP_MATCH(medium, "(?i)referral") THEN "Referral"
  WHEN source = "(direct)" THEN "Direct"
  ELSE "Other"
END

# Performance tier
CASE
  WHEN conversion_rate >= 5 THEN "High Performer"
  WHEN conversion_rate >= 2 THEN "Average"
  ELSE "Needs Attention"
END

# Revenue buckets
CASE
  WHEN revenue >= 1000 THEN "$1,000+"
  WHEN revenue >= 500 THEN "$500-999"
  WHEN revenue >= 100 THEN "$100-499"
  ELSE "Under $100"
END
```

### Regex Functions
```
# Match (returns boolean)
REGEXP_MATCH(page_path, "/blog/.*")

# Extract
REGEXP_EXTRACT(page_path, "/blog/(.*)")

# Replace
REGEXP_REPLACE(utm_campaign, "_", " ")

# Common patterns
REGEXP_MATCH(source, "(?i)(google|bing|yahoo|duckduckgo)")  # Search engines
REGEXP_MATCH(page_path, "^/(product|shop|store)/")           # Product pages
REGEXP_EXTRACT(url, "utm_campaign=([^&]+)")                  # Extract UTM param
```

### Date Functions
```
# Current date/time
CURRENT_DATE()
CURRENT_DATETIME()

# Date parts
YEAR(date_field)
MONTH(date_field)
WEEK(date_field)
DAY(date_field)
QUARTER(date_field)

# Date math
DATE_DIFF(date1, date2)              # Days between dates
DATETIME_ADD(date_field, INTERVAL 7 DAY)
DATETIME_SUB(date_field, INTERVAL 30 DAY)

# Date formatting
FORMAT_DATETIME("%Y-%m-%d", date_field)
FORMAT_DATETIME("%B %Y", date_field)  # "January 2024"

# Date parsing
TODATE(date_string, 'BASIC', '%Y%m%d')
PARSE_DATETIME('%Y-%m-%dT%H:%M:%S', datetime_string)
```

### Aggregation Functions
```
SUM(metric)
AVG(metric)
COUNT(dimension)
COUNT_DISTINCT(dimension)
MIN(metric)
MAX(metric)
MEDIAN(metric)
PERCENTILE(metric, 90)              # 90th percentile
```

### Conditional Aggregation
```
# Count with condition
SUM(CASE WHEN device = "mobile" THEN sessions ELSE 0 END)

# Weighted average
SUM(ctr * impressions) / SUM(impressions)  # Weighted CTR
```

## Chart Types & Best Practices

### Scorecard
- Best for: KPIs with period comparison
- Settings: Show comparison period, compact numbers, conditional formatting
- Use custom date ranges for accurate comparisons

### Time Series (Line Chart)
- Best for: Trends over time
- Settings: Smooth lines for trends, dual axis for different scales
- Limit to 3-4 series for readability

### Bar Chart
- Best for: Category comparisons
- Horizontal for long labels, vertical for time-based
- Sort by value (not alphabetical) for impact

### Table
- Best for: Detailed data exploration
- Settings: Heatmap bars, pagination, sortable columns
- Add conditional formatting for at-a-glance insights

### Pie/Donut Chart
- Best for: Simple part-of-whole (max 5-6 slices)
- Avoid for: Many categories, similar-sized slices
- Donut with KPI in center is effective

### Geo Map
- Best for: Geographic distribution
- Settings: Color scale (sequential for values, diverging for comparison)
- Bubble map for city-level data

### Combo Chart
- Best for: Two related metrics with different scales (e.g., spend + CPA)
- Line + bar combination
- Use dual Y-axes carefully

### Treemap
- Best for: Hierarchical data with size + color dimensions
- Settings: Size = volume metric, color = efficiency metric

## Controls (Interactive Filters)

### Date Range Control
- Pre-set options: Last 7/14/28/30/90 days, this/last month/quarter/year
- Custom range picker
- Comparison period: previous period, same period last year
- Applies to all charts on page (or linked chart group)

### Filter Control
- Dropdown: Single or multi-select from dimension values
- Search bar: Type-to-filter for large lists
- Slider: Numeric range selection
- Checkbox: Boolean toggle

### Data Control
- Lets viewer switch data sources (e.g., different GA4 properties)
- Useful for multi-client reports with same structure

### Parameters
- User-defined variables (text, number, date)
- Reference in calculated fields: @parameter_name
- Example: CPA goal parameter -> conditional formatting in charts

## Data Blending

### How It Works
- Joins multiple data sources on shared dimensions (join keys)
- Left outer join by default
- Max 5 data sources per blend
- Blended data can be used in charts and calculated fields

### Common Blends
```
Blend 1: Google Ads + GA4
|- Join key: Date + Campaign (UTM)
|- From Google Ads: Cost, Clicks, Impressions
|- From GA4: Sessions, Conversions, Revenue
Result: Full-funnel view with ROAS

Blend 2: Multiple Ad Platforms
|- Join key: Date
|- From Google Ads: Cost, Conversions
|- From Facebook Ads: Cost, Conversions
|- From Microsoft Ads: Cost, Conversions
Result: Cross-platform daily spend/conversion comparison

Blend 3: Google Sheets + GA4
|- Join key: Page URL
|- From Sheets: Content category, author, publish date
|- From GA4: Pageviews, engaged sessions, conversions
Result: Content performance with editorial metadata
```

### Limitations
- Cannot filter a blend on a field from only one source
- Aggregation happens before joining (pre-aggregated)
- Performance can be slower with large datasets
- Null handling: unmatched rows show null for the missing source

## Report Design Best Practices

### Layout Principles
1. **Z-pattern**: Important KPIs top-left, details flow right and down
2. **Visual hierarchy**: Largest/boldest = most important metric
3. **White space**: Don't crowd charts -- breathing room improves readability
4. **Consistent grid**: Align charts to an invisible grid (12-column recommended)
5. **Page structure**: Summary -> Detail -> Deep-dive (progressive disclosure)

### Color Guidelines
- Max 5-7 colors in a single chart
- Use brand colors consistently
- Red = negative/down, green = positive/up (universal convention)
- Sequential palette for ranges (light -> dark)
- High contrast for accessibility

### Report Sizing
- **Desktop optimized**: 1200 x 900px per page (16:9 landscape)
- **PDF export**: Standard page sizes work best
- **Embedded**: Match container width, fluid height
- **Mobile**: Use responsive layout mode, vertical scroll

### Performance Tips
- Limit data sources per page (3-4 max)
- Use date range controls to limit data pulled
- Avoid blending large datasets
- Use extract data sources for slow connections
- Reduce calculated field complexity where possible

## Sharing & Distribution

### Sharing Options
| Method | Who Can View | Real-time? |
|--------|-------------|------------|
| Link sharing (viewers) | Anyone with link | Yes |
| Link sharing (editors) | Collaborators | Yes |
| Embed (iframe) | Website visitors | Yes |
| Scheduled email (PDF) | Email recipients | Snapshot |
| Download (PDF/CSV) | Manual | Snapshot |

### Embedding
```html
<iframe
  width="800"
  height="600"
  src="https://lookerstudio.google.com/embed/reporting/REPORT_ID/page/PAGE_ID"
  frameborder="0"
  style="border:0"
  allowfullscreen
  sandbox="allow-storage-access-by-user-activation allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"
></iframe>
```

### Template Reports
- Create a report with placeholder data source
- Share as template link
- Viewers make a copy with their own data source
- Useful for: agency-client scaling, community templates
