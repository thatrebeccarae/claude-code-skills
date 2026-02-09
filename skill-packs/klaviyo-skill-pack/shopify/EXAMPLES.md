# Shopify Analysis Examples

Practical examples of common Shopify store analysis tasks and optimization patterns.

## Example 1: Full Store Health Audit

**User Request**: "Audit my Shopify store and tell me where we stand"

**Analysis Steps**:
1. Fetch store metadata, order volume, product catalog, customer count
2. Calculate 30-day revenue, AOV, and order velocity
3. Assess product catalog health (in-stock vs out-of-stock)
4. Compare metrics against DTC benchmarks
5. Generate prioritized recommendations

**Script Command**:
```bash
python scripts/analyze.py --analysis-type full-audit --output audit.json
```

**Sample Output Analysis**:
```
Full Store Health Audit
=======================

=== STORE INFO ===
Name: Coastal Candle Co.
Domain: coastalcandle.myshopify.com
Plan: Shopify (Basic)
Currency: USD

=== ORDER VOLUME (Last 30 Days) ===
Total Orders: 342
Paid Orders: 318
Open Orders: 12
Orders/Day: 11.4 [GOOD - benchmark: 10+]

=== REVENUE ===
30-Day Revenue: $24,156.00
AOV: $75.96 [GOOD - benchmark: $60+]

=== PRODUCT CATALOG ===
Active Products: 47
Total Variants: 128
In Stock: 41 (87%)
Out of Stock: 6 (13%)
Assessment: [GOOD]

=== CUSTOMERS ===
Total: 2,840

=== RECOMMENDATIONS ===
1. HIGH: 6 products out of stock (13%) -- restock top sellers
   to avoid lost revenue from stockouts
2. MEDIUM: AOV at $76 is good but not great -- test bundles and
   free shipping threshold ($99) to push toward $100+
3. LOW: Consider upgrading from Basic plan for better reporting
   and lower transaction fees as volume grows
```

## Example 2: Conversion Funnel Analysis

**User Request**: "Analyze our conversion funnel for the last 30 days"

**Analysis Steps**:
1. Fetch all orders (paid, cancelled, refunded) for the period
2. Calculate completion rates, cancellation rate, refund rate
3. Analyze AOV trends and discount usage
4. Segment new vs returning customers
5. Identify daily order patterns

**Script Command**:
```bash
python scripts/analyze.py --analysis-type conversion-funnel --days 30
```

**Sample Output Analysis**:
```
Conversion Funnel Analysis (Last 30 Days)
==========================================

=== ORDER STATUS ===
Total Orders: 342
Paid: 318 (93.0%)
Cancelled: 14 (4.1%)
Refunded: 10 (2.9%)
Cancellation Rate: 4.1% [OK]

=== REVENUE ===
Total Revenue: $24,156.00
AOV: $75.96 [GOOD]
Total Discounts: $3,420.00
Discount Rate: 14.2% [OK - under 25%]

=== CUSTOMER MIX ===
Unique Buyers: 278
Returning Buyers: 40 (12.6%)
Returning Rate Assessment: [WARNING - below 15%]

=== DAILY TREND ===
Avg Orders/Day: 10.6
Avg Revenue/Day: $805.20
Peak Day: 2026-01-18 (Saturday, 24 orders)

=== RECOMMENDATIONS ===
1. HIGH: Returning customer rate at 12.6% is below the 15% floor.
   Implement post-purchase email flows, loyalty program, and
   subscription options for consumable products.
2. MEDIUM: Discount rate at 14.2% is manageable but trending up.
   Shift from percentage discounts to value-add offers (free gift
   with purchase, free shipping) to protect margins.
3. LOW: Peak sales on Saturday -- schedule email campaigns for
   Friday evening to capture weekend shoppers.
```

## Example 3: Product Performance

**User Request**: "Which products are selling best and which need attention?"

**Analysis Steps**:
1. Aggregate sales by product from order line items
2. Rank by revenue and units sold
3. Identify zero-sale products (slow movers)
4. Check inventory levels for low-stock alerts
5. Calculate catalog sell-through rate

**Script Command**:
```bash
python scripts/analyze.py --analysis-type product-performance --days 30
```

**Sample Output Analysis**:
```
Product Performance (Last 30 Days)
===================================

=== TOP SELLERS (by Revenue) ===
#  Product                     Units    Revenue    Orders
1. Driftwood Soy Candle (lg)   142     $4,970     128
2. Sea Salt Gift Set            89     $4,450      89
3. Coastal Breeze 3-Pack        67     $3,015      67
4. Lavender & Sage Candle       94     $2,820      88
5. Reed Diffuser (Ocean)        73     $2,555      70

=== SLOW MOVERS (Zero Sales) ===
12 products with zero sales in 30 days:
- Seasonal: Winter Pine (created 2025-11-15) -- seasonal, expected
- Wax Melt Sampler (created 2025-08-20) -- 5 months, no sales
- Ceramic Holder (Black) (created 2025-09-10) -- stale listing
... and 9 more

=== INVENTORY ALERTS ===
5 items at critically low stock:
- Driftwood Soy Candle (lg): 3 remaining
- Sea Salt Gift Set: 5 remaining
- Coastal Breeze 3-Pack: 2 remaining

=== SUMMARY ===
Products Sold: 35 of 47 active (74.5% sell-through)

=== RECOMMENDATIONS ===
1. HIGH: Top 3 sellers are critically low on stock -- rush reorder
   to avoid lost revenue. Driftwood Candle alone drives 20% of revenue.
2. HIGH: 12 zero-sale products -- review and either promote, bundle,
   discount to clear, or archive to reduce catalog clutter.
3. MEDIUM: Gift Set is #2 by revenue -- create a dedicated collection
   page and feature in email campaigns.
```

## Example 4: Customer Cohort Analysis

**User Request**: "Break down our customer base -- who's buying, how often, and what's LTV?"

**Analysis Steps**:
1. Group all orders by customer email
2. Classify one-time vs repeat buyers
3. Calculate purchase frequency distribution
4. Estimate average LTV across cohorts
5. Identify top customers by total spend

**Script Command**:
```bash
python scripts/analyze.py --analysis-type customer-cohorts --days 90
```

**Sample Output Analysis**:
```
Customer Cohort Analysis (Last 90 Days)
========================================

=== CUSTOMER SUMMARY ===
Unique Customers: 712
One-Time Buyers: 583 (81.9%)
Repeat Buyers: 129 (18.1%)
Repeat Rate: 18.1% [OK - below 25% "good" benchmark]

=== PURCHASE FREQUENCY ===
1 purchase: 583 customers
2 purchases: 87 customers
3+ purchases: 42 customers

=== LIFETIME VALUE ===
Average LTV (all): $98.42
One-Time Avg Spend: $72.15
Repeat Avg Spend: $214.30
LTV Multiplier: 2.97x (repeat vs one-time)

=== TOP CUSTOMERS ===
#  Orders  Total Spent  Avg Order
1.   8     $612.40      $76.55
2.   7     $534.20      $76.31
3.   6     $489.00      $81.50
4.   6     $467.80      $77.97
5.   5     $398.50      $79.70

=== RECOMMENDATIONS ===
1. HIGH: 82% are one-time buyers. Every 1% improvement in repeat
   rate = ~7 additional repeat customers = ~$1,500 incremental
   revenue. Priority: post-purchase email flow + second-purchase
   incentive (10% off next order within 30 days).
2. MEDIUM: LTV multiplier of 3x proves repeat customers are
   significantly more valuable. Invest in loyalty program
   (points-based with VIP tiers) to encourage frequency.
3. LOW: Top customers average 5-8 orders -- ideal candidates
   for subscription offering or VIP early-access program.
```

## Example 5: Revenue Deep Dive

**User Request**: "Show me revenue trends and patterns -- where's the money?"

**Analysis Steps**:
1. Aggregate daily revenue and order counts
2. Analyze day-of-week patterns
3. Measure discount impact on margins
4. Identify peak and trough periods
5. Calculate revenue per order trends

**Script Command**:
```bash
python scripts/analyze.py --analysis-type revenue-analysis --days 30
```

**Sample Output Analysis**:
```
Revenue Analysis (Last 30 Days)
================================

=== TOTALS ===
Revenue: $24,156.00
Orders: 318
AOV: $75.96
Discounts: $3,420.00
Discount Rate: 14.2%

=== DAILY TREND (Last 14 Days) ===
Date        Revenue     Orders    AOV
2026-01-27  $892.00     12       $74.33
2026-01-28  $1,045.00   14       $74.64
2026-01-29  $756.00      9       $84.00
2026-01-30  $623.00      8       $77.88
2026-01-31  $1,234.00   16       $77.13
...

=== DAY OF WEEK ===
Day         Revenue     Orders   Avg/Week
Saturday    $5,240.00   68       $1,310
Friday      $4,680.00   61       $1,170
Sunday      $4,120.00   54       $1,030
Thursday    $3,210.00   42         $803
Wednesday   $2,890.00   38         $723
Tuesday     $2,240.00   30         $560
Monday      $1,776.00   25         $444

=== DISCOUNT IMPACT ===
Total Discounts: $3,420.00
Discount Rate: 14.2%
Assessment: [OK - moderate but monitor]

=== RECOMMENDATIONS ===
1. HIGH: Weekend drives 56% of revenue (Fri-Sun). Optimize
   campaign timing: send email Thursday evening, run paid ads
   with increased budget Friday-Saturday.
2. MEDIUM: Monday-Tuesday revenue is 40% below average. Test
   midweek flash sales or "Monday Motivation" campaigns.
3. LOW: Discount rate at 14.2% -- manageable but track trend.
   If rising above 20%, shift to free shipping threshold
   or gift-with-purchase to protect margins.
```

## Example 6: Integration Health Check

**User Request**: "Is my Shopify API connection working? Show me store info."

**Analysis Steps**:
1. Fetch store metadata via Admin API
2. Verify API connectivity and permissions
3. Display store configuration summary

**Script Command**:
```bash
python scripts/shopify_client.py --resource shop
```

**Sample Output**:
```json
{
  "shop": {
    "id": 12345678,
    "name": "Coastal Candle Co.",
    "email": "hello@coastalcandle.com",
    "domain": "coastalcandle.com",
    "myshopify_domain": "coastal-candle.myshopify.com",
    "plan_name": "basic",
    "currency": "USD",
    "country_name": "United States",
    "timezone": "America/New_York",
    "weight_unit": "lb",
    "has_storefront": true,
    "checkout_api_supported": true
  }
}
```

**What to check**:
- API returns data without errors = connection is healthy
- `plan_name` shows your Shopify plan (affects API rate limits)
- `currency` and `timezone` should match your expectations
- If you get a 401 error, your access token is invalid or expired

## Common Analysis Patterns

### Quick Order Count
```bash
python scripts/shopify_client.py --resource order-count --status any
```

### Export Recent Orders to CSV
```bash
python scripts/shopify_client.py --resource orders --days 7 --format csv --output recent_orders.csv
```

### Active Products Overview
```bash
python scripts/shopify_client.py --resource products --status active --format table
```

### Customer Export
```bash
python scripts/shopify_client.py --resource customers --days 90 --format csv --output customers.csv
```

## Pro Tips

### Ask Better Questions
Instead of: "Show me Shopify data"
Ask: "Which products should I restock this week based on sales velocity?"

### Combine Analyses
Instead of running one analysis at a time:
```bash
python scripts/analyze.py --analysis-type full-audit
```
This runs all five analyses in sequence for a complete picture.

### Track Over Time
Export weekly analyses to build a trend:
```bash
python scripts/analyze.py --analysis-type revenue-analysis --days 7 --output "revenue-$(date +%Y-%m-%d).json"
```

### Cross-Reference with Klaviyo
After running a Shopify audit, check if email/SMS flows align:
- Low repeat rate? -> Check Klaviyo post-purchase and win-back flows
- High AOV products? -> Feature them in Klaviyo browse abandonment
- Seasonal slow movers? -> Create clearance email campaign in Klaviyo
