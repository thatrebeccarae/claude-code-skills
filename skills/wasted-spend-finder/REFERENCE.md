# Wasted Spend Finder — Reference

## GAQL Queries (Google Ads Query Language)

### Search Terms Report

```sql
SELECT
  search_term_view.search_term,
  campaign.name,
  ad_group.name,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value
FROM search_term_view
WHERE segments.date DURING LAST_30_DAYS
  AND metrics.cost_micros > 0
ORDER BY metrics.cost_micros DESC
```

### Placement Report (Display + YouTube)

```sql
SELECT
  detail_placement_view.display_name,
  detail_placement_view.target_url,
  detail_placement_view.placement_type,
  campaign.name,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions
FROM detail_placement_view
WHERE segments.date DURING LAST_30_DAYS
  AND metrics.cost_micros > 0
ORDER BY metrics.cost_micros DESC
```

### Keyword Performance

```sql
SELECT
  ad_group_criterion.keyword.text,
  ad_group_criterion.keyword.match_type,
  campaign.name,
  ad_group.name,
  metrics.impressions,
  metrics.clicks,
  metrics.cost_micros,
  metrics.conversions,
  metrics.conversions_value
FROM keyword_view
WHERE segments.date DURING LAST_30_DAYS
  AND metrics.cost_micros > 0
ORDER BY metrics.cost_micros DESC
```

### Campaign CPA Benchmark

```sql
SELECT
  campaign.name,
  campaign.id,
  metrics.cost_micros,
  metrics.conversions
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
  AND metrics.conversions > 0
```

## Meta Ads API Queries

### Placement Breakdown

```
GET /{ad_account_id}/insights
?level=ad
&breakdowns=publisher_platform,platform_position
&fields=spend,impressions,clicks,actions,cost_per_action_type
&time_range={"since":"2026-02-13","until":"2026-03-13"}
```

### Audience Breakdown

```
GET /{ad_account_id}/insights
?level=adset
&fields=spend,impressions,clicks,actions,cost_per_action_type,frequency
&time_range={"since":"2026-02-13","until":"2026-03-13"}
```

### Creative Fatigue Detection

```
GET /{ad_account_id}/insights
?level=ad
&fields=ad_name,spend,impressions,frequency,actions,cost_per_action_type
&filtering=[{"field":"frequency","operator":"GREATER_THAN","value":"3"}]
&time_range={"since":"2026-02-13","until":"2026-03-13"}
```

## CSV Output Formats

### Negative Keywords CSV

```csv
Keyword,Match Type,Campaign,Ad Group,Spend Wasted,Clicks,Theme
"competitor product name",Exact,Search - Non-Brand,General,[cost],[clicks],Competitor
"how to do it yourself",Phrase,Search - Non-Brand,General,[cost],[clicks],Informational
"free alternative",Phrase,Search - Non-Brand,General,[cost],[clicks],Free Intent
```

### Placement Exclusions CSV

```csv
Placement,Type,Campaign,Spend Wasted,Impressions,Clicks,Conversions,Category
"game-app.example.com",App,Display - Prospecting,[cost],[impr],[clicks],0,Low-Quality App
"lyrics-channel",YouTube,Video - Awareness,[cost],[impr],[clicks],0,Music/Lyrics
```

### Audience Exclusions CSV

```csv
Audience,Type,Campaign,Spend,Impressions,Conversions,CPA,Recommendation
"Lookalike 5%",Lookalike,Prospecting,[spend],[impr],0,N/A,Exclude or narrow
"Interest: Cooking",Interest,Awareness,[spend],[impr],0,N/A,Exclude
```

## Savings Estimation

```
Estimated Monthly Savings = Sum of waste spend over analysis period / months

Confidence levels:
- HIGH: Zero conversions, 3x CPA threshold exceeded, 50+ clicks
- MEDIUM: Zero conversions, 2x CPA threshold exceeded, 25+ clicks
- LOW: Low conversion rate but some conversions present
```

## Common False Positives

| Scenario | Why It Looks Like Waste | Why It Might Not Be |
|----------|------------------------|-------------------|
| Brand terms from competitors | Zero direct conversions | May drive brand awareness |
| Broad educational queries | No immediate conversion | Top-of-funnel consideration |
| High-ticket items | Long conversion window | Attribution window too short |
| New campaigns (<14 days) | Insufficient data | Learning phase |
| View-through heavy platforms | Low click conversions | View-through conversions not counted |

Always check assisted conversions and extend the attribution window before excluding.
