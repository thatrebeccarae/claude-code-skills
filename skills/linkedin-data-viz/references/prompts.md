# LinkedIn Data Viz -- Prompt Library

Analysis prompts for each of the 10 visualizations. Use these to customize analysis behavior, extend the skill, or generate narrative insights alongside the visual output.

---

## 1. Network Universe

### Purpose

Reveals the structural composition of a LinkedIn network. Shows which professional domains dominate, where clusters overlap, and how connections group by role. Useful for identifying network gaps (e.g., "I have no finance connections") and strengths.

### Data Sources

- `Connections.csv` -- name, company, position, connection date

### Analysis Prompt

```
Analyze the following LinkedIn connection data and produce a network clustering analysis.

For each connection, classify them into one of these role clusters based on their Position field:
Engineering, Marketing, Sales, Product, Design, Data, Operations, Finance, HR/People, Executive, Other.

Use case-insensitive keyword matching. If a position matches multiple clusters, assign the first match in the order listed.

For each cluster, compute:
- Total connection count
- Top 5 companies by frequency within the cluster
- Percentage of total network

Then identify:
- Cross-cluster links: clusters that share many of the same companies (suggesting industry/company overlap)
- The largest cluster and what that says about the network's professional center of gravity
- Any notably small or absent clusters that represent networking blind spots

Return the results as structured JSON matching the Network Universe data schema.
```

### Customization Ideas

- **Custom clusters:** Replace the default role categories with industry-specific ones (e.g., for healthcare: Clinician, Research, Pharma, Payer, HealthTech, Admin).
- **Company-based clustering:** Instead of clustering by role, cluster by company to see which organizations dominate the network.
- **Time-weighted nodes:** Scale node size not just by count but by recency of connection, so recently added connections appear larger.
- **Geographic overlay:** If you have location data from Ad_Targeting.csv, add a geographic dimension to the force graph.

---

## 2. Inferences vs Reality

### Purpose

Exposes what LinkedIn's algorithms think they know about the user and checks those assumptions against the actual export data. Highlights where the platform's model is accurate, partially right, or flat-out wrong. Useful for understanding how LinkedIn's ad targeting and content algorithms perceive you.

### Data Sources

- `Inferences_about_you.csv` -- category, type, description
- `Ad_Targeting.csv` -- demographic and behavioral targeting categories
- `Connections.csv` -- used to cross-reference inferred industry/role against actual network composition

### Analysis Prompt

```
Compare LinkedIn's inferences about this user with their actual data.

Inferences data contains LinkedIn's binary algorithmic predictions — statements like "Is a Marketing Professional", "Not an HR Professional", "Is a Job Seeker", "Is a Business Decision Maker". Each inference is a yes/no classification LinkedIn assigns to the user's profile.
Ad targeting data contains the categories advertisers can use to target this user.
Connection data provides ground truth about the user's actual professional network.

For each inference:
1. State the exact inference text as the label (e.g., "Not an HR Professional", "Is a Job Seeker").
2. Determine what the actual data shows:
   - Cross-reference against the user's connection positions, industries, and ad targeting data.
   - Check if the binary classification matches the user's actual profile and network composition.
3. Assign a verdict:
   - "accurate" if the inference closely matches reality
   - "partial" if it's directionally correct but oversimplified or misses nuance
   - "wrong" if the data contradicts the inference
4. Write a brief explanation of why.

Also analyze the ad targeting data:
- List all targeting categories with counts.
- Flag any surprising or incorrect targeting labels.
- Identify the most relevant vs most irrelevant targeting categories.

Return structured JSON matching the Inferences vs Reality data schema.
```

### Customization Ideas

- **Accuracy scoring:** Add a numerical accuracy score (0-100) to each inference instead of just three-tier verdicts.
- **Temporal analysis:** If the user has multiple exports over time, compare how inferences have changed.
- **Privacy audit mode:** Focus the analysis on which inferences feel invasive or are based on data the user did not explicitly provide.
- **Advertiser exposure:** Estimate how many advertisers can target the user based on the ad targeting categories.

---

## 3. High-Value Messages

### Purpose

Surfaces unanswered messages that deserve a response, ranked by potential professional value. Helps users identify missed opportunities like recruiter outreach, partnership proposals, or relationship-building conversations that went cold.

### Data Sources

- `messages.csv` -- full message history
- `Connections.csv` -- to enrich sender context (company, position)

### Analysis Prompt

```
Analyze the user's LinkedIn message history to find high-value unanswered messages.

An "unanswered message" is the most recent message in a conversation where:
- The user is NOT the sender of the last message
- No subsequent message from the user exists in that conversation

For each unanswered message, compute a value score (0.0 to 1.0) based on:
- Recency (0.35 weight): Inverse of days since message, capped at 365 days. Score = max(0, 1 - (days / 365))
- Sender Role (0.25 weight): Check if the sender appears in Connections.csv. Score higher for VP+, Director, Founder, C-suite, Recruiter positions. 1.0 for executive, 0.7 for director/recruiter, 0.4 for manager, 0.2 for other, 0.0 if not found in connections.
- Content Signals (0.20 weight): Scan message content for opportunity keywords: "opportunity," "role," "interested," "collaborate," "project," "hiring," "budget," "partnership," "proposal." Score = min(1.0, keyword_count * 0.25)
- Relationship Depth (0.20 weight): Count total messages exchanged in this conversation. Score = min(1.0, message_count / 20)

Classify each message by urgency:
- Hot (>= 0.7): High-value, respond soon
- Warm (0.4 to 0.69): Worth responding to
- Cool (< 0.4): Low priority

Tag each message with categories: "opportunity" (job/project-related), "relationship" (personal/networking), "network" (new connection outreach).

Return the top 30 messages sorted by score descending, as structured JSON matching the High-Value Messages data schema.
```

### Customization Ideas

- **Custom scoring weights:** Adjust the four factor weights based on what matters most to the user (e.g., heavily weight recruiter messages during a job search).
- **Industry filter:** Only surface messages from people in specific industries or companies.
- **Response draft generation:** For each high-value message, generate a suggested response based on the conversation context.
- **Time-decay adjustment:** Make the recency curve steeper or gentler depending on the user's response habits.

---

## 4. Company Follows Clustering

### Purpose

Groups the companies the user follows into industry categories, revealing professional interest patterns. Shows where attention is concentrated and which industries the user tracks most closely.

### Data Sources

- `Company Follows.csv` -- organization name, follow date

### Analysis Prompt

```
Analyze the user's LinkedIn company follows and group them by industry.

For each company in the follows list, assign it to an industry category using keyword matching against the company name:
- Tech / SaaS: software, tech, cloud, platform, AI, data, digital, labs, io
- Finance / Fintech: bank, capital, financial, fintech, payments, invest, fund, wealth
- E-commerce / Retail: shop, retail, commerce, marketplace, brand, store, fashion
- Media / Publishing: media, news, publish, content, entertainment, studio
- Consulting / Services: consulting, advisory, agency, partners, group, solutions
- Healthcare: health, medical, pharma, biotech, wellness, care, clinical
- Education: university, academy, school, edtech, learning, institute
- Other: no keyword match

For each cluster, compute:
- Company count
- List of company names
- Percentage of total follows
- Date range of follows within the cluster

Also identify:
- The dominant cluster and what it suggests about the user's professional focus
- Any clusters with recent follow spikes (many follows in a short period)
- Temporal patterns: has the user's industry interest shifted over time?

Return structured JSON matching the Company Follows Clustering data schema.
```

### Customization Ideas

- **Manual category overrides:** Let the user provide a mapping of company names to categories for companies that are miscategorized by keyword matching.
- **Company enrichment:** Use an external API to fetch actual company industry data instead of relying on name keywords.
- **Follow timeline:** Visualize when companies were followed over time, showing interest migration across industries.
- **Competitor grouping:** Let the user define competitor sets and see which competitive landscapes they track most.

---

## 5. Inbound vs Outbound

### Purpose

Visualizes the balance between connection requests received (inbound) and sent (outbound) over time. Reveals whether the user's network growth is passive (people find them) or active (they reach out), and how that balance has shifted.

### Data Sources

- `Invitations.csv` -- sender, recipient, date, direction

### Analysis Prompt

```
Analyze LinkedIn invitation data to show inbound vs outbound connection request patterns.

Group invitations by month (YYYY-MM format) and direction (INCOMING vs OUTGOING).

For each month, compute:
- Inbound count (INCOMING direction)
- Outbound count (OUTGOING direction)
- Net direction (inbound minus outbound; positive = more people reaching out)

Across the full dataset, compute:
- Total inbound and outbound counts
- Overall inbound ratio (inbound / total)
- Peak inbound month (highest inbound count)
- Peak outbound month (highest outbound count)
- Trend analysis: is the inbound ratio increasing or decreasing over the most recent 6 months?

Identify notable patterns:
- Months with unusual spikes (conferences, job changes, viral content)
- Sustained periods of high inbound (> 60% of total) indicating passive growth
- Sustained periods of high outbound (> 60% of total) indicating active networking campaigns

Return structured JSON matching the Inbound vs Outbound data schema.
```

### Customization Ideas

- **Event correlation:** Let the user annotate specific months with events (conference, job change, post went viral) and overlay those on the chart.
- **Acceptance rate:** If data is available, calculate what percentage of outbound invitations were accepted.
- **Message inclusion rate:** Track how many invitations included a personal message vs blank invitations.
- **Response time analysis:** Measure how quickly the user responds to inbound invitations.

---

## 6. Connection Quality

### Purpose

Assesses the depth of every connection relationship. Most LinkedIn networks have a large "never messaged" tier -- this visualization quantifies exactly how much of the network is active vs dormant vs purely superficial.

### Data Sources

- `Connections.csv` -- the full connection list
- `messages.csv` -- message history for relationship depth

### Analysis Prompt

```
Analyze connection quality by cross-referencing the connection list with message history.

For each connection in Connections.csv, check messages.csv to determine relationship depth.

Classification tiers:
- **Active**: At least 1 message exchanged in the last 6 months. These are live, engaged relationships.
- **Dormant**: Messages exist but the most recent is older than 6 months. The relationship has gone cold.
- **Never Messaged**: No messages found between the user and this connection. Purely a LinkedIn link with no conversation history.

For each tier, compute:
- Connection count
- Percentage of total network
- For Active: average messages per connection, most active connection (by message count)
- For Dormant: average months since last message, connections most worth re-engaging (highest historical message count)
- For Never Messaged: most common companies and roles (to identify where the user adds connections but never follows up)

Also compute:
- Overall active rate (active / total)
- Engagement quality score (weighted: active * 1.0 + dormant * 0.3 + never * 0.0, divided by total)

Return structured JSON matching the Connection Quality data schema.
```

### Customization Ideas

- **Custom time thresholds:** Let the user define what "active" and "dormant" mean (e.g., 3 months instead of 6).
- **Re-engagement list:** Generate a prioritized list of dormant connections worth re-engaging, based on their role and historical interaction.
- **Company heatmap:** Show which companies have the most active vs dormant connections.
- **Trend over time:** Track how the active/dormant/never ratio has changed as the network has grown.

---

## 7. Connection Timeline

### Purpose

Provides a tabular, chronological view of recent connections with key metadata at a glance. Shows who was added, when, from which company, whether the connection was inbound or outbound, and how much messaging has occurred since connecting.

### Data Sources

- `Connections.csv` -- name, company, position, date
- `Invitations.csv` -- to determine direction (inbound/outbound)
- `messages.csv` -- to count messages per connection

### Analysis Prompt

```
Build a connection timeline showing the most recent connections with engagement context.

For each connection (sorted by Connected On date, most recent first):
1. Extract name, company, position, and connection date from Connections.csv.
2. Determine direction by matching the connection name against Invitations.csv:
   - If the connection appears as the "From" in an INCOMING invitation: "inbound"
   - If the connection appears as the "To" in an OUTGOING invitation: "outbound"
   - If no matching invitation found: "unknown"
3. Count total messages exchanged with this connection from messages.csv (matching by name in FROM/TO fields).

Return the 50 most recent connections with all fields populated.

Also compute summary stats:
- Total connections in the recent window
- Date range of the timeline
- Most common company among recent connections
- Percentage that were inbound vs outbound

Return structured JSON matching the Connection Timeline data schema.
```

### Customization Ideas

- **Extended timeline:** Show all connections instead of just the most recent 50.
- **Engagement scoring:** Add a column showing an engagement score based on message frequency and recency.
- **Company grouping:** Group timeline entries by company to see batch-connection patterns (e.g., connecting with 5 people from the same company in one week).
- **Search and filter:** Add interactive filters by company, role, direction, or date range.

---

## 8. Inbox Quality

### Purpose

Tracks the ratio of genuine, meaningful messages to noise (spam, InMail, automated outreach) over time. Reveals whether the user's inbox is getting noisier and helps quantify the signal-to-noise ratio of their LinkedIn messaging experience.

### Data Sources

- `messages.csv` -- full message history

### Analysis Prompt

```
Classify LinkedIn messages as Genuine or Noise and analyze the trend over time.

For each message, apply these classification rules:

**Noise indicators** (any one triggers Noise classification):
- Sender name is "LinkedIn" or "LinkedIn Member"
- Subject line contains "InMail" or "Sponsored"
- Message content matches cold outreach patterns:
  - "I came across your profile"
  - "We have an exciting opportunity"
  - "I'd like to add you to my professional network" (default invite text)
  - Template-style intros with [brackets] or generic greetings
- The conversation has exactly 1 message total (one-sided cold outreach)
- CONVERSATION ID is null or empty

**Genuine indicators** (override Noise if conversation shows real engagement):
- Multiple messages in the conversation (back-and-forth exchange)
- Message content references specific work, projects, or shared context
- The sender appears in the user's Connections.csv

If a message has both Noise and Genuine signals, classify as Genuine (benefit of the doubt for real conversations).

Group messages by month (YYYY-MM) and compute:
- Genuine message count per month
- Noise message count per month

Across the full dataset, compute:
- Total genuine and noise counts
- Genuine rate (genuine / total)
- Noise trend: compare the noise rate in the most recent 3 months to the 3 months before that. Is it increasing, decreasing, or stable (within 5% change)?

Return structured JSON matching the Inbox Quality data schema.
```

### Customization Ideas

- **Custom noise patterns:** Let the user add their own regex patterns for messages they consider noise (e.g., specific recruiter templates).
- **Sender reputation:** Track which senders generate the most noise and flag repeat offenders.
- **Response correlation:** Analyze whether genuine messages get faster responses than noise, and what the user's average response time is for genuine messages.
- **Weekly granularity:** Switch from monthly to weekly aggregation for more granular trend detection.

---

## 9. Does Posting Actually Work?

### Purpose

Answers the question every LinkedIn user asks: does posting content actually grow your network? Correlates posting frequency (from Shares.csv) with new connection growth (from Connections.csv) by month, calculates the Pearson correlation coefficient, and visualizes both series on a dual-axis chart.

### Data Sources

- `Shares.csv` -- post dates and content
- `Connections.csv` -- connection dates for monthly growth calculation

### Analysis Prompt

```
Analyze whether posting on LinkedIn correlates with new connection growth.

Algorithm:
1. Parse Shares.csv and group posts by month (YYYY-MM).
2. Parse Connections.csv and count new connections per month (by Connected On date).
3. Align the two series to the same month range (earliest to latest that appears in either dataset).
4. Fill months with zero posts or zero connections as 0.
5. Calculate the Pearson correlation coefficient between monthly post count and monthly new connections.
6. Identify "before" and "after" periods:
   - "Before consistent posting" = months where post count is 0-1.
   - "After consistent posting" = months where post count is 3+.
   - Calculate average new connections per month for each period.
7. Calculate percentage increase: ((avg_after - avg_before) / avg_before) * 100.

Generate a chart_title that includes the correlation coefficient and a plain-English interpretation:
- r >= 0.7: "Posting drives connection growth"
- r >= 0.4: "Posting moderately correlates with growth"
- r < 0.4: "Weak correlation between posting and growth"

Generate three highlight cards:
- Correlation coefficient with interpretation
- Percentage increase in connections during active posting
- Average connections per month: before vs after

Return structured JSON matching the Posting Correlation data schema.
```

### Customization Ideas

- **Lag analysis:** Check if connections spike 1-2 months after posting (delayed effect) rather than same-month.
- **Content type breakdown:** If ShareCommentary data is rich enough, categorize posts (original content, reshares, polls) and see which type drives the most connections.
- **Engagement overlay:** If Reactions.csv is available, overlay reaction counts as a third axis.
- **Posting cadence:** Calculate optimal posting frequency (e.g., "posting 6+ times/month yields 3x more connections than 1-2 times").

---

## 10. Career Strata

### Purpose

Visualizes the user's network as geological layers, with each stratum representing a career phase. The oldest connections form the deepest layer, and the most recent sit at the surface. Reveals how the network's composition has evolved across career transitions.

### Data Sources

- `Connections.csv` -- name, company, position, connection date

### Analysis Prompt

```
Divide the user's LinkedIn connection history into career strata (geological layers) by time period.

Algorithm:
1. Sort all connections by Connected On date (ascending).
2. Determine the full date range (earliest connection to most recent).
3. Create time-based strata:
   - If the history spans 8 years or fewer: one stratum per year.
   - If the history spans more than 8 years: divide into 6-8 multi-year buckets of roughly equal duration.
   - Never create fewer than 4 or more than 9 strata.
4. For each stratum, compute:
   - Era label (e.g., "2020-2021" or "Early Career (2015-2017)")
   - Date range
   - Connection count
   - Percentage of total network
   - Top 3 companies by frequency within this stratum
   - Top 3 roles by frequency within this stratum
5. Assign CSS layer classes from layer-0 (deepest/oldest) to layer-N (most elevated/newest).

Also identify:
- The peak era (stratum with the most connections)
- Career transitions: strata where the top companies or roles shift significantly from the previous stratum
- Growth acceleration: strata with notably higher connection rates than adjacent periods

Provide narrative context for each stratum based on the data patterns (e.g., "This period shows heavy tech industry networking, likely aligned with a role change").

Return structured JSON matching the Career Strata data schema.
```

### Customization Ideas

- **Manual era labels:** Let the user provide custom labels for each stratum (e.g., "Startup Phase," "Agency Years," "Enterprise Pivot") instead of auto-generated date ranges.
- **Company-based strata:** Instead of time-based layers, create strata based on the user's own job history (one layer per employer).
- **Role evolution:** Track how the user's connections' seniority levels have changed across strata (e.g., early career = mostly peers, later = more executives).
- **Interactive drill-down:** Click on a stratum to see the full list of connections in that era with their details.
