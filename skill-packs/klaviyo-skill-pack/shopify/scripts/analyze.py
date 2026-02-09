#!/usr/bin/env python3
"""
Shopify Store Analysis Tool

Performs higher-level analysis on Shopify data including:
- Store health audits
- Conversion funnel analysis
- Product performance
- Customer cohort analysis
- Revenue trends and patterns

Usage:
    python analyze.py --analysis-type full-audit
    python analyze.py --analysis-type conversion-funnel --days 30
    python analyze.py --analysis-type product-performance --days 30
    python analyze.py --analysis-type customer-cohorts --days 90
    python analyze.py --analysis-type revenue-analysis --days 30
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

try:
    from shopify_client import ShopifyAnalyticsClient
except ImportError:
    print("Error: shopify_client.py not found in the same directory", file=sys.stderr)
    sys.exit(1)


class ShopifyAnalyzer:
    """Performs analysis on Shopify store data."""

    BENCHMARKS = {
        "conversion_rate": {"good": 2.5, "great": 4.0, "warning": 1.5},
        "aov": {"good": 60, "great": 100, "warning": 30},
        "returning_customer_pct": {"good": 25, "great": 40, "warning": 15},
        "cart_completion_rate": {"good": 45, "great": 60, "warning": 30},
        "orders_per_day": {"good": 10, "great": 50, "warning": 3},
        "product_count": {"good": 20, "great": 100, "warning": 5},
        "active_product_pct": {"good": 80, "great": 95, "warning": 50},
        "discount_rate": {"good": 10, "great": 5, "warning": 25},
    }

    def __init__(self):
        """Initialize the analyzer with Shopify client."""
        self.client = ShopifyAnalyticsClient()

    def store_health_audit(self) -> Dict:
        """
        Comprehensive store health audit: shop info, order volume,
        product catalog, and customer base.
        """
        shop = self.client.get_shop_info().get("shop", {})
        order_count = self.client.get_order_count(status="any")
        open_orders = self.client.get_order_count(status="open")
        customer_count = self.client.get_customer_count()

        # Recent orders for quick metrics
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat() + "Z"
        recent_orders = self.client.get_orders(
            status="any", created_at_min=thirty_days_ago, limit=250
        )

        # Products
        products = self.client.get_products(status="active", limit=250)

        # Calculate metrics
        revenue_30d = sum(
            float(o.get("total_price", 0)) for o in recent_orders
            if o.get("financial_status") in ("paid", "partially_paid")
        )
        paid_orders_30d = [
            o for o in recent_orders
            if o.get("financial_status") in ("paid", "partially_paid")
        ]
        aov = revenue_30d / len(paid_orders_30d) if paid_orders_30d else 0

        # Product health
        products_with_inventory = [
            p for p in products
            if any(
                v.get("inventory_quantity", 0) > 0
                for v in p.get("variants", [])
            )
        ]
        total_variants = sum(len(p.get("variants", [])) for p in products)

        audit = {
            "store": {
                "name": shop.get("name", "Unknown"),
                "domain": shop.get("domain", "Unknown"),
                "plan": shop.get("plan_name", "Unknown"),
                "currency": shop.get("currency", "USD"),
                "country": shop.get("country_name", "Unknown"),
            },
            "orders": {
                "total_all_time": order_count,
                "open_orders": open_orders,
                "last_30_days": len(recent_orders),
                "paid_last_30_days": len(paid_orders_30d),
                "orders_per_day": round(len(recent_orders) / 30, 1),
                "assessment": self._assess_metric(
                    "orders_per_day", len(recent_orders) / 30
                ),
            },
            "revenue": {
                "last_30_days": round(revenue_30d, 2),
                "aov": round(aov, 2),
                "aov_assessment": self._assess_metric("aov", aov),
            },
            "products": {
                "total_active": len(products),
                "total_variants": total_variants,
                "in_stock": len(products_with_inventory),
                "out_of_stock": len(products) - len(products_with_inventory),
                "active_pct": round(
                    len(products_with_inventory) / len(products) * 100, 1
                ) if products else 0,
                "assessment": self._assess_metric("product_count", len(products)),
            },
            "customers": {
                "total": customer_count,
            },
            "recommendations": [],
        }

        # Generate recommendations
        audit["recommendations"] = self._recommend_store_health(audit)

        return audit

    def conversion_funnel(self, days: int = 30) -> Dict:
        """
        Analyze conversion funnel from order data.
        Note: Full funnel (sessions → ATC) requires Shopify Analytics access.
        This uses order-level data for AOV, order trends, and completion metrics.
        """
        created_at_min = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        orders = self.client.get_orders(
            status="any", created_at_min=created_at_min, limit=250
        )

        paid_orders = [
            o for o in orders
            if o.get("financial_status") in ("paid", "partially_paid")
        ]
        cancelled = [o for o in orders if o.get("cancelled_at")]
        refunded = [
            o for o in orders if o.get("financial_status") == "refunded"
        ]

        revenue = sum(float(o.get("total_price", 0)) for o in paid_orders)
        discount_total = sum(
            float(o.get("total_discounts", 0)) for o in paid_orders
        )
        aov = revenue / len(paid_orders) if paid_orders else 0

        # Returning vs new customers
        customer_emails = [
            o.get("email") for o in paid_orders if o.get("email")
        ]
        unique_customers = set(customer_emails)
        returning_count = len(customer_emails) - len(unique_customers)

        # Daily order trend
        daily_orders = defaultdict(int)
        daily_revenue = defaultdict(float)
        for order in paid_orders:
            day = order.get("created_at", "")[:10]
            daily_orders[day] += 1
            daily_revenue[day] += float(order.get("total_price", 0))

        funnel = {
            "period": f"Last {days} days",
            "summary": {
                "total_orders": len(orders),
                "paid_orders": len(paid_orders),
                "cancelled_orders": len(cancelled),
                "refunded_orders": len(refunded),
                "cancellation_rate": round(
                    len(cancelled) / len(orders) * 100, 2
                ) if orders else 0,
            },
            "revenue": {
                "total": round(revenue, 2),
                "aov": round(aov, 2),
                "aov_assessment": self._assess_metric("aov", aov),
                "total_discounts": round(discount_total, 2),
                "discount_rate": round(
                    discount_total / revenue * 100, 2
                ) if revenue else 0,
            },
            "customers": {
                "unique_buyers": len(unique_customers),
                "returning_buyers": returning_count,
                "returning_pct": round(
                    returning_count / len(customer_emails) * 100, 2
                ) if customer_emails else 0,
            },
            "daily_trend": {
                "avg_orders_per_day": round(
                    len(paid_orders) / max(days, 1), 1
                ),
                "avg_revenue_per_day": round(revenue / max(days, 1), 2),
                "peak_day": max(daily_orders, key=daily_orders.get)
                if daily_orders else "N/A",
                "peak_orders": max(daily_orders.values()) if daily_orders else 0,
            },
            "recommendations": [],
        }

        funnel["recommendations"] = self._recommend_conversion(funnel)
        return funnel

    def product_performance(self, days: int = 30) -> Dict:
        """
        Analyze product performance: top sellers, slow movers, variant analysis.
        """
        created_at_min = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        orders = self.client.get_orders(
            status="any",
            created_at_min=created_at_min,
            financial_status="paid",
            limit=250,
        )
        products = self.client.get_products(status="active", limit=250)

        # Aggregate product sales from line items
        product_sales = defaultdict(lambda: {"units": 0, "revenue": 0.0, "orders": 0})
        for order in orders:
            seen_products = set()
            for item in order.get("line_items", []):
                product_id = str(item.get("product_id", "unknown"))
                product_sales[product_id]["units"] += item.get("quantity", 0)
                product_sales[product_id]["revenue"] += float(
                    item.get("price", 0)
                ) * item.get("quantity", 1)
                product_sales[product_id]["title"] = item.get("title", "Unknown")
                if product_id not in seen_products:
                    product_sales[product_id]["orders"] += 1
                    seen_products.add(product_id)

        # Sort by revenue
        sorted_products = sorted(
            product_sales.items(), key=lambda x: x[1]["revenue"], reverse=True
        )

        top_sellers = [
            {
                "product_id": pid,
                "title": data["title"],
                "units_sold": data["units"],
                "revenue": round(data["revenue"], 2),
                "orders": data["orders"],
            }
            for pid, data in sorted_products[:10]
        ]

        # Slow movers: active products with zero sales
        sold_product_ids = set(product_sales.keys())
        slow_movers = [
            {
                "product_id": str(p.get("id")),
                "title": p.get("title", "Unknown"),
                "variants": len(p.get("variants", [])),
                "created_at": p.get("created_at", "")[:10],
            }
            for p in products
            if str(p.get("id")) not in sold_product_ids
        ][:20]

        # Inventory alerts
        low_stock = []
        for product in products:
            for variant in product.get("variants", []):
                qty = variant.get("inventory_quantity", 0)
                if 0 < qty <= 5:
                    low_stock.append({
                        "product": product.get("title", "Unknown"),
                        "variant": variant.get("title", "Default"),
                        "sku": variant.get("sku", "N/A"),
                        "quantity": qty,
                    })

        analysis = {
            "period": f"Last {days} days",
            "top_sellers": top_sellers,
            "slow_movers": {
                "count": len(slow_movers),
                "products": slow_movers[:10],
            },
            "inventory_alerts": {
                "low_stock_count": len(low_stock),
                "items": low_stock[:10],
            },
            "summary": {
                "total_products_sold": len(product_sales),
                "total_active_products": len(products),
                "catalog_sell_through": round(
                    len(product_sales) / len(products) * 100, 2
                ) if products else 0,
            },
            "recommendations": [],
        }

        analysis["recommendations"] = self._recommend_products(analysis)
        return analysis

    def customer_cohort_analysis(self, days: int = 90) -> Dict:
        """
        Analyze customer cohorts: first-time vs repeat, purchase frequency, LTV.
        """
        created_at_min = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        orders = self.client.get_orders(
            status="any",
            created_at_min=created_at_min,
            financial_status="paid",
            limit=250,
        )

        # Group by customer
        customer_orders = defaultdict(list)
        for order in orders:
            email = order.get("email", "")
            if email:
                customer_orders[email].append(order)

        # Classify customers
        one_time = []
        repeat = []
        for email, cust_orders in customer_orders.items():
            total_spent = sum(float(o.get("total_price", 0)) for o in cust_orders)
            if len(cust_orders) == 1:
                one_time.append({"email": email, "spent": total_spent})
            else:
                repeat.append({
                    "email": email,
                    "orders": len(cust_orders),
                    "spent": total_spent,
                    "avg_order": round(total_spent / len(cust_orders), 2),
                })

        # Sort repeat by spend
        repeat.sort(key=lambda x: x["spent"], reverse=True)

        total_customers = len(customer_orders)
        repeat_pct = (len(repeat) / total_customers * 100) if total_customers else 0
        avg_ltv = (
            sum(
                sum(float(o.get("total_price", 0)) for o in orders_list)
                for orders_list in customer_orders.values()
            )
            / total_customers
            if total_customers
            else 0
        )

        # Purchase frequency
        all_order_counts = [len(o) for o in customer_orders.values()]
        avg_frequency = sum(all_order_counts) / len(all_order_counts) if all_order_counts else 0

        cohorts = {
            "period": f"Last {days} days",
            "summary": {
                "total_unique_customers": total_customers,
                "one_time_buyers": len(one_time),
                "repeat_buyers": len(repeat),
                "repeat_rate": round(repeat_pct, 2),
                "repeat_assessment": self._assess_metric(
                    "returning_customer_pct", repeat_pct
                ),
            },
            "purchase_frequency": {
                "average_orders_per_customer": round(avg_frequency, 2),
                "single_purchase": len(one_time),
                "two_purchases": len([r for r in repeat if r["orders"] == 2]),
                "three_plus": len([r for r in repeat if r["orders"] >= 3]),
            },
            "lifetime_value": {
                "average_ltv": round(avg_ltv, 2),
                "one_time_avg_spend": round(
                    sum(c["spent"] for c in one_time) / len(one_time), 2
                ) if one_time else 0,
                "repeat_avg_spend": round(
                    sum(c["spent"] for c in repeat) / len(repeat), 2
                ) if repeat else 0,
            },
            "top_customers": [
                {
                    "orders": c["orders"],
                    "total_spent": round(c["spent"], 2),
                    "avg_order": c["avg_order"],
                }
                for c in repeat[:10]
            ],
            "recommendations": [],
        }

        cohorts["recommendations"] = self._recommend_cohorts(cohorts)
        return cohorts

    def revenue_analysis(self, days: int = 30) -> Dict:
        """
        Revenue trends: daily patterns, discount impact, day-of-week analysis.
        """
        created_at_min = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        orders = self.client.get_orders(
            status="any",
            created_at_min=created_at_min,
            financial_status="paid",
            limit=250,
        )

        # Daily breakdown
        daily = defaultdict(lambda: {"revenue": 0.0, "orders": 0, "discounts": 0.0})
        dow = defaultdict(lambda: {"revenue": 0.0, "orders": 0})

        for order in orders:
            created = order.get("created_at", "")
            if created:
                day = created[:10]
                daily[day]["revenue"] += float(order.get("total_price", 0))
                daily[day]["orders"] += 1
                daily[day]["discounts"] += float(order.get("total_discounts", 0))

                try:
                    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    day_name = dt.strftime("%A")
                    dow[day_name]["revenue"] += float(order.get("total_price", 0))
                    dow[day_name]["orders"] += 1
                except (ValueError, TypeError):
                    pass

        # Sort daily
        sorted_daily = sorted(daily.items())

        total_revenue = sum(d["revenue"] for d in daily.values())
        total_discounts = sum(d["discounts"] for d in daily.values())
        total_orders = sum(d["orders"] for d in daily.values())

        # Best/worst days of week
        dow_sorted = sorted(dow.items(), key=lambda x: x[1]["revenue"], reverse=True)

        analysis = {
            "period": f"Last {days} days",
            "totals": {
                "revenue": round(total_revenue, 2),
                "orders": total_orders,
                "aov": round(total_revenue / total_orders, 2) if total_orders else 0,
                "discounts": round(total_discounts, 2),
                "discount_rate": round(
                    total_discounts / total_revenue * 100, 2
                ) if total_revenue else 0,
            },
            "daily_trend": [
                {
                    "date": d,
                    "revenue": round(data["revenue"], 2),
                    "orders": data["orders"],
                    "aov": round(data["revenue"] / data["orders"], 2) if data["orders"] else 0,
                }
                for d, data in sorted_daily[-14:]  # Last 14 days
            ],
            "day_of_week": [
                {
                    "day": d,
                    "revenue": round(data["revenue"], 2),
                    "orders": data["orders"],
                    "avg_revenue": round(
                        data["revenue"] / max(days // 7, 1), 2
                    ),
                }
                for d, data in dow_sorted
            ],
            "discount_impact": {
                "total_discounts": round(total_discounts, 2),
                "discount_rate": round(
                    total_discounts / total_revenue * 100, 2
                ) if total_revenue else 0,
                "assessment": self._assess_metric(
                    "discount_rate",
                    total_discounts / total_revenue * 100 if total_revenue else 0,
                ),
            },
            "recommendations": [],
        }

        analysis["recommendations"] = self._recommend_revenue(analysis)
        return analysis

    def full_audit(self) -> Dict:
        """Run all analyses and combine into a comprehensive audit."""
        return {
            "audit_date": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
            "store_health": self.store_health_audit(),
            "conversion_funnel": self.conversion_funnel(days=30),
            "product_performance": self.product_performance(days=30),
            "customer_cohorts": self.customer_cohort_analysis(days=90),
            "revenue_analysis": self.revenue_analysis(days=30),
        }

    def _assess_metric(self, name: str, value: float) -> Dict:
        """Compare a metric value against benchmarks."""
        benchmark = self.BENCHMARKS.get(name, {})
        if not benchmark:
            return {"status": "no_benchmark", "value": round(value, 2)}

        # For discount_rate, lower is better
        if name == "discount_rate":
            if value <= benchmark["great"]:
                status = "great"
            elif value <= benchmark["good"]:
                status = "good"
            elif value >= benchmark["warning"]:
                status = "warning"
            else:
                status = "ok"
        else:
            if value >= benchmark["great"]:
                status = "great"
            elif value >= benchmark["good"]:
                status = "good"
            elif value <= benchmark["warning"]:
                status = "warning"
            else:
                status = "ok"

        return {
            "status": status,
            "value": round(value, 2),
            "benchmark_good": benchmark["good"],
            "benchmark_great": benchmark["great"],
        }

    def _recommend_store_health(self, audit: Dict) -> List[Dict]:
        """Generate store health recommendations."""
        recs = []

        if audit["orders"]["assessment"]["status"] == "warning":
            recs.append({
                "priority": "HIGH",
                "area": "Order Volume",
                "action": "Increase traffic and conversion — order volume is below average",
                "expected_impact": "2-3x order volume with paid acquisition + CRO",
            })

        if audit["revenue"]["aov_assessment"]["status"] == "warning":
            recs.append({
                "priority": "HIGH",
                "area": "AOV",
                "action": "Implement AOV-boosting tactics: bundles, upsells, free shipping threshold",
                "expected_impact": "+20-40% AOV increase",
            })

        out_of_stock = audit["products"]["out_of_stock"]
        total = audit["products"]["total_active"]
        if total and out_of_stock / total > 0.2:
            recs.append({
                "priority": "MEDIUM",
                "area": "Inventory",
                "action": f"{out_of_stock} products out of stock ({round(out_of_stock / total * 100)}%) — review inventory planning",
                "expected_impact": "Recover lost sales from stockouts",
            })

        return recs

    def _recommend_conversion(self, funnel: Dict) -> List[Dict]:
        """Generate conversion funnel recommendations."""
        recs = []

        cancel_rate = funnel["summary"]["cancellation_rate"]
        if cancel_rate > 5:
            recs.append({
                "priority": "HIGH",
                "area": "Cancellations",
                "action": f"Cancellation rate is {cancel_rate}% — investigate causes and reduce friction",
                "expected_impact": "Recover 30-50% of cancelled orders",
            })

        discount_rate = funnel["revenue"]["discount_rate"]
        if discount_rate > 25:
            recs.append({
                "priority": "MEDIUM",
                "area": "Discount Strategy",
                "action": f"Discount rate at {discount_rate}% — risk of margin erosion. Shift to value-add offers",
                "expected_impact": "+5-10% margin improvement",
            })

        repeat_pct = funnel["customers"]["returning_pct"]
        if repeat_pct < 15:
            recs.append({
                "priority": "HIGH",
                "area": "Retention",
                "action": "Low repeat purchase rate — implement post-purchase flows and loyalty program",
                "expected_impact": "+25-40% customer retention",
            })

        return recs

    def _recommend_products(self, analysis: Dict) -> List[Dict]:
        """Generate product performance recommendations."""
        recs = []

        sell_through = analysis["summary"]["catalog_sell_through"]
        if sell_through < 50:
            recs.append({
                "priority": "HIGH",
                "area": "Catalog Efficiency",
                "action": f"Only {sell_through}% of catalog had sales — prune or promote underperformers",
                "expected_impact": "Improved catalog focus and inventory turns",
            })

        slow_count = analysis["slow_movers"]["count"]
        if slow_count > 10:
            recs.append({
                "priority": "MEDIUM",
                "area": "Slow Movers",
                "action": f"{slow_count} products with zero sales — consider clearance, bundles, or removal",
                "expected_impact": "Free up working capital and reduce catalog clutter",
            })

        low_stock = analysis["inventory_alerts"]["low_stock_count"]
        if low_stock > 5:
            recs.append({
                "priority": "HIGH",
                "area": "Inventory",
                "action": f"{low_stock} items at critically low stock — reorder to avoid stockouts",
                "expected_impact": "Prevent lost sales from popular items going OOS",
            })

        return recs

    def _recommend_cohorts(self, cohorts: Dict) -> List[Dict]:
        """Generate customer cohort recommendations."""
        recs = []

        repeat_rate = cohorts["summary"]["repeat_rate"]
        if repeat_rate < 20:
            recs.append({
                "priority": "HIGH",
                "area": "Repeat Purchase Rate",
                "action": "Implement win-back flows, loyalty rewards, and subscription options",
                "expected_impact": "+10-20pp repeat purchase rate",
            })
        elif repeat_rate >= 40:
            recs.append({
                "priority": "INFO",
                "area": "Repeat Purchase Rate",
                "action": f"Strong repeat rate at {repeat_rate}% — focus on scaling acquisition",
                "expected_impact": "Leverage loyal base for referrals and reviews",
            })

        ltv = cohorts["lifetime_value"]["average_ltv"]
        one_time_avg = cohorts["lifetime_value"]["one_time_avg_spend"]
        if one_time_avg and ltv < one_time_avg * 1.5:
            recs.append({
                "priority": "MEDIUM",
                "area": "LTV Growth",
                "action": "LTV barely above first purchase — improve second-purchase rate with post-purchase flows",
                "expected_impact": "+30-50% LTV increase",
            })

        return recs

    def _recommend_revenue(self, analysis: Dict) -> List[Dict]:
        """Generate revenue recommendations."""
        recs = []

        discount_assessment = analysis["discount_impact"]["assessment"]
        if discount_assessment.get("status") == "warning":
            recs.append({
                "priority": "HIGH",
                "area": "Discount Dependency",
                "action": "High discount rate eroding margins — transition to value-add offers",
                "expected_impact": "+5-15% margin improvement",
            })

        # Day-of-week optimization
        if analysis["day_of_week"]:
            best_day = analysis["day_of_week"][0]
            recs.append({
                "priority": "LOW",
                "area": "Timing Optimization",
                "action": f"Best sales day is {best_day['day']} — align campaigns and promotions accordingly",
                "expected_impact": "+5-10% campaign performance",
            })

        return recs


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Shopify store performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full store audit
  python analyze.py --analysis-type full-audit

  # Conversion funnel (last 30 days)
  python analyze.py --analysis-type conversion-funnel --days 30

  # Product performance
  python analyze.py --analysis-type product-performance --days 30

  # Customer cohorts (last 90 days)
  python analyze.py --analysis-type customer-cohorts --days 90

  # Revenue analysis with output file
  python analyze.py --analysis-type revenue-analysis --days 30 --output revenue.json
        """,
    )

    parser.add_argument(
        "--analysis-type",
        choices=[
            "store-audit", "conversion-funnel", "product-performance",
            "customer-cohorts", "revenue-analysis", "full-audit",
        ],
        default="full-audit",
        help="Type of analysis to perform (default: full-audit)",
    )
    parser.add_argument(
        "--days", type=int, default=30,
        help="Number of days to analyze (default: 30)",
    )
    parser.add_argument(
        "--format", choices=["json", "table"], default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--output", help="Output file path (default: stdout)",
    )

    args = parser.parse_args()

    try:
        analyzer = ShopifyAnalyzer()

        if args.analysis_type == "store-audit":
            result = analyzer.store_health_audit()
        elif args.analysis_type == "conversion-funnel":
            result = analyzer.conversion_funnel(days=args.days)
        elif args.analysis_type == "product-performance":
            result = analyzer.product_performance(days=args.days)
        elif args.analysis_type == "customer-cohorts":
            result = analyzer.customer_cohort_analysis(days=args.days)
        elif args.analysis_type == "revenue-analysis":
            result = analyzer.revenue_analysis(days=args.days)
        elif args.analysis_type == "full-audit":
            result = analyzer.full_audit()
        else:
            result = analyzer.full_audit()

        output = json.dumps(result, indent=2, default=str)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Analysis saved to {args.output}", file=sys.stderr)
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
