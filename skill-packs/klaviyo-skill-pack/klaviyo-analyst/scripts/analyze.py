#!/usr/bin/env python3
"""
Klaviyo Marketing Analysis Tool

Performs higher-level analysis on Klaviyo data including:
- Flow audit against essential flows checklist
- Segment health assessment
- Campaign performance comparison
- Deliverability diagnostics
- Revenue attribution analysis

Usage:
    python analyze.py --analysis-type full-audit
    python analyze.py --analysis-type flow-audit
    python analyze.py --analysis-type segment-health
    python analyze.py --analysis-type campaign-comparison --days 30
    python analyze.py --analysis-type deliverability
    python analyze.py --analysis-type revenue-attribution
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Optional

try:
    from klaviyo_client import KlaviyoAnalyticsClient
except ImportError:
    print("Error: klaviyo_client.py not found in the same directory", file=sys.stderr)
    sys.exit(1)


def _safe_output_path(path: str) -> str:
    """Validate output path does not escape working directory."""
    resolved = os.path.realpath(path)
    cwd = os.path.realpath(os.getcwd())
    if not resolved.startswith(cwd + os.sep) and resolved != cwd:
        raise ValueError(f"Output path must be within working directory: {cwd}")
    return resolved


class KlaviyoAnalyzer:
    """Performs marketing analysis on Klaviyo account data."""

    ESSENTIAL_FLOWS = [
        {"name": "Welcome Series", "trigger": "List Subscribe", "priority": "CRITICAL"},
        {"name": "Abandoned Cart", "trigger": "Started Checkout", "priority": "CRITICAL"},
        {"name": "Browse Abandonment", "trigger": "Viewed Product", "priority": "HIGH"},
        {"name": "Post-Purchase", "trigger": "Placed Order", "priority": "CRITICAL"},
        {"name": "Winback", "trigger": "Time Since Last Purchase", "priority": "HIGH"},
        {"name": "Sunset/Re-engagement", "trigger": "Engagement Date", "priority": "HIGH"},
        {"name": "Review Request", "trigger": "Fulfilled Order", "priority": "MEDIUM"},
        {"name": "Replenishment", "trigger": "Predicted Next Order", "priority": "MEDIUM"},
        {"name": "Birthday/Anniversary", "trigger": "Date Property", "priority": "LOW"},
        {"name": "VIP/Loyalty", "trigger": "Segment Entry", "priority": "MEDIUM"},
    ]

    BENCHMARKS = {
        "open_rate": {"good": 0.20, "great": 0.30, "warning": 0.15},
        "click_rate": {"good": 0.02, "great": 0.04, "warning": 0.015},
        "unsubscribe_rate": {"good": 0.003, "great": 0.001, "warning": 0.005},
        "spam_complaint_rate": {"good": 0.0005, "great": 0.0002, "warning": 0.001},
        "flow_revenue_pct": {"good": 0.30, "great": 0.50, "warning": 0.20},
        "bounce_rate": {"good": 0.02, "great": 0.01, "warning": 0.05},
        "list_growth_rate": {"good": 0.03, "great": 0.08, "warning": 0.01},
    }

    def __init__(self):
        """Initialize the analyzer with Klaviyo client."""
        self.client = KlaviyoAnalyticsClient()

    def audit_flows(self) -> Dict:
        """
        Audit flows against the essential flows checklist.

        Returns:
            Dictionary with flow inventory, gaps, and recommendations
        """
        flows = self.client.get_flows()

        # Map existing flows
        flow_names_lower = [f.get("name", "").lower() for f in flows]

        checklist = []
        found_count = 0
        for essential in self.ESSENTIAL_FLOWS:
            # Fuzzy match: check if essential flow name keywords appear
            keywords = essential["name"].lower().split()
            matched = any(
                all(kw in flow_name for kw in keywords)
                for flow_name in flow_names_lower
            )

            # Also check common alternate names
            alt_names = {
                "welcome series": ["welcome", "onboarding"],
                "abandoned cart": ["abandon", "cart recovery", "checkout abandon"],
                "browse abandonment": ["browse abandon", "viewed product"],
                "post-purchase": ["post purchase", "thank you", "order follow"],
                "winback": ["win back", "win-back", "lapsed", "re-engage"],
                "sunset/re-engagement": ["sunset", "re-engagement", "sunsetting"],
                "review request": ["review", "feedback request"],
                "replenishment": ["replenish", "reorder", "restock"],
                "birthday/anniversary": ["birthday", "anniversary", "bday"],
                "vip/loyalty": ["vip", "loyalty", "high value"],
            }

            if not matched:
                alts = alt_names.get(essential["name"].lower(), [])
                matched = any(
                    any(alt in flow_name for alt in alts)
                    for flow_name in flow_names_lower
                )

            status = "found" if matched else "missing"
            if matched:
                found_count += 1

            checklist.append({
                "flow": essential["name"],
                "trigger": essential["trigger"],
                "priority": essential["priority"],
                "status": status,
            })

        # Count active vs inactive
        active_flows = [f for f in flows if f.get("status") == "live"]

        audit = {
            "summary": {
                "total_flows": len(flows),
                "active_flows": len(active_flows),
                "inactive_flows": len(flows) - len(active_flows),
                "essential_found": found_count,
                "essential_missing": len(self.ESSENTIAL_FLOWS) - found_count,
                "coverage_score": f"{found_count}/{len(self.ESSENTIAL_FLOWS)}",
            },
            "checklist": checklist,
            "all_flows": [
                {
                    "name": f.get("name"),
                    "status": f.get("status"),
                    "id": f.get("id"),
                }
                for f in flows
            ],
            "recommendations": self._recommend_flow_improvements(checklist),
        }

        return audit

    def analyze_segments(self) -> Dict:
        """
        Assess segment health including engagement tiers and structure.

        Returns:
            Dictionary with segment analysis and recommendations
        """
        segments = self.client.get_segments()
        lists = self.client.get_lists()

        # Categorize segments by engagement keywords
        engagement_tiers = {
            "active": [],
            "warm": [],
            "at_risk": [],
            "lapsed": [],
            "suppression": [],
            "other": [],
        }

        tier_keywords = {
            "active": ["active", "engaged", "30 day", "30d", "recent"],
            "warm": ["warm", "60 day", "90 day", "60d", "90d"],
            "at_risk": ["at risk", "at-risk", "cooling", "fading"],
            "lapsed": ["lapsed", "inactive", "unengaged", "180 day", "180d"],
            "suppression": ["suppress", "sunset", "never engaged", "do not"],
        }

        for segment in segments:
            seg_name = segment.get("name", "").lower()
            categorized = False

            for tier, keywords in tier_keywords.items():
                if any(kw in seg_name for kw in keywords):
                    engagement_tiers[tier].append(segment.get("name"))
                    categorized = True
                    break

            if not categorized:
                engagement_tiers["other"].append(segment.get("name"))

        # Check for RFM segments
        rfm_keywords = ["rfm", "recency", "frequency", "monetary", "clv", "ltv"]
        has_rfm = any(
            any(kw in seg.get("name", "").lower() for kw in rfm_keywords)
            for seg in segments
        )

        # Check for predictive segments
        predictive_keywords = ["predicted", "churn", "next order", "likely to"]
        has_predictive = any(
            any(kw in seg.get("name", "").lower() for kw in predictive_keywords)
            for seg in segments
        )

        analysis = {
            "summary": {
                "total_segments": len(segments),
                "total_lists": len(lists),
                "has_engagement_tiers": bool(
                    engagement_tiers["active"] or engagement_tiers["warm"]
                ),
                "has_rfm_segments": has_rfm,
                "has_predictive_segments": has_predictive,
                "has_suppression_segment": bool(engagement_tiers["suppression"]),
            },
            "engagement_tiers": {
                tier: {"count": len(segs), "segments": segs}
                for tier, segs in engagement_tiers.items()
            },
            "lists": [{"name": l.get("name"), "id": l.get("id")} for l in lists],
            "recommendations": self._recommend_segment_improvements(
                engagement_tiers, has_rfm, has_predictive
            ),
        }

        return analysis

    def compare_campaigns(self, days: int = 30) -> Dict:
        """
        Compare campaign performance against benchmarks.

        Args:
            days: Number of days to analyze

        Returns:
            Dictionary with campaign metrics and benchmark comparison
        """
        campaigns = self.client.get_campaigns()

        # Attempt to get reports for recent campaigns
        campaign_data = []
        for campaign in campaigns[:20]:
            campaign_id = campaign.get("id")
            if not campaign_id:
                continue

            try:
                report = self.client.get_campaign_report(campaign_id)
                if report:
                    campaign_data.append({
                        "name": campaign.get("name"),
                        "id": campaign_id,
                        "status": campaign.get("status"),
                        "report": report,
                    })
            except Exception:
                campaign_data.append({
                    "name": campaign.get("name"),
                    "id": campaign_id,
                    "status": campaign.get("status"),
                    "report": None,
                })

        # Calculate aggregate metrics where reports are available
        total_recipients = 0
        total_opens = 0
        total_clicks = 0
        total_bounces = 0
        total_unsubscribes = 0
        total_complaints = 0
        total_revenue = 0.0
        campaigns_with_data = 0

        for c in campaign_data:
            report = c.get("report")
            if not report:
                continue

            stats = report if isinstance(report, dict) else {}
            recipients = stats.get("recipients", 0) or 0
            if recipients > 0:
                campaigns_with_data += 1
                total_recipients += recipients
                total_opens += stats.get("unique_opens", 0) or 0
                total_clicks += stats.get("unique_clicks", 0) or 0
                total_bounces += stats.get("bounces", 0) or 0
                total_unsubscribes += stats.get("unsubscribes", 0) or 0
                total_complaints += stats.get("spam_complaints", 0) or 0
                total_revenue += float(stats.get("revenue", 0) or 0)

        # Calculate rates
        if total_recipients > 0:
            avg_metrics = {
                "open_rate": total_opens / total_recipients,
                "click_rate": total_clicks / total_recipients,
                "bounce_rate": total_bounces / total_recipients,
                "unsubscribe_rate": total_unsubscribes / total_recipients,
                "spam_complaint_rate": total_complaints / total_recipients,
            }
        else:
            avg_metrics = {
                "open_rate": 0,
                "click_rate": 0,
                "bounce_rate": 0,
                "unsubscribe_rate": 0,
                "spam_complaint_rate": 0,
            }

        # Assess each metric against benchmarks
        assessments = {}
        for metric, value in avg_metrics.items():
            assessments[metric] = self._assess_metric(metric, value)

        analysis = {
            "period": f"Last {days} days",
            "summary": {
                "total_campaigns": len(campaigns),
                "campaigns_analyzed": campaigns_with_data,
                "total_recipients": total_recipients,
                "total_revenue": round(total_revenue, 2),
            },
            "aggregate_metrics": {
                k: round(v * 100, 2) for k, v in avg_metrics.items()
            },
            "benchmark_assessment": assessments,
            "campaigns": [
                {"name": c["name"], "status": c["status"]} for c in campaign_data
            ],
            "recommendations": self._recommend_campaign_improvements(
                avg_metrics, assessments
            ),
        }

        return analysis

    def check_deliverability(self) -> Dict:
        """
        Run deliverability diagnostics on recent sending data.

        Returns:
            Dictionary with deliverability status and recommendations
        """
        campaigns = self.client.get_campaigns()

        # Aggregate deliverability metrics
        total_sent = 0
        total_bounces = 0
        total_complaints = 0
        total_delivered = 0
        campaigns_checked = 0

        for campaign in campaigns[:20]:
            campaign_id = campaign.get("id")
            if not campaign_id:
                continue

            try:
                report = self.client.get_campaign_report(campaign_id)
                if not report:
                    continue

                stats = report if isinstance(report, dict) else {}
                recipients = stats.get("recipients", 0) or 0
                if recipients > 0:
                    campaigns_checked += 1
                    total_sent += recipients
                    total_bounces += stats.get("bounces", 0) or 0
                    total_complaints += stats.get("spam_complaints", 0) or 0
                    total_delivered += stats.get("deliveries", 0) or 0
            except Exception:
                continue

        # Calculate rates
        if total_sent > 0:
            bounce_rate = total_bounces / total_sent
            complaint_rate = total_complaints / total_sent
            delivery_rate = total_delivered / total_sent
        else:
            bounce_rate = 0
            complaint_rate = 0
            delivery_rate = 0

        # Assess
        bounce_assessment = self._assess_metric("bounce_rate", bounce_rate)
        complaint_assessment = self._assess_metric("spam_complaint_rate", complaint_rate)

        # Check for critical thresholds
        issues = []
        if bounce_rate > 0.05:
            issues.append({
                "severity": "CRITICAL",
                "issue": "High bounce rate",
                "detail": f"Bounce rate {bounce_rate * 100:.2f}% exceeds 5% threshold",
                "impact": "ISPs may throttle or block your sending",
            })
        if complaint_rate > 0.001:
            issues.append({
                "severity": "CRITICAL",
                "issue": "High spam complaint rate",
                "detail": f"Complaint rate {complaint_rate * 100:.3f}% exceeds 0.1% threshold",
                "impact": "Risk of being blacklisted by major ISPs",
            })
        if bounce_rate > 0.02:
            issues.append({
                "severity": "HIGH",
                "issue": "Elevated bounce rate",
                "detail": f"Bounce rate {bounce_rate * 100:.2f}% above 2% benchmark",
                "impact": "Sender reputation degradation over time",
            })
        if complaint_rate > 0.0005:
            issues.append({
                "severity": "HIGH",
                "issue": "Elevated complaint rate",
                "detail": f"Complaint rate {complaint_rate * 100:.3f}% above 0.05% benchmark",
                "impact": "Gradual inbox placement decline",
            })

        analysis = {
            "summary": {
                "campaigns_checked": campaigns_checked,
                "total_sent": total_sent,
                "total_delivered": total_delivered,
                "delivery_rate": round(delivery_rate * 100, 2),
                "bounce_rate": round(bounce_rate * 100, 2),
                "complaint_rate": round(complaint_rate * 100, 3),
            },
            "assessments": {
                "bounce_rate": bounce_assessment,
                "complaint_rate": complaint_assessment,
            },
            "issues": issues,
            "authentication_checklist": [
                {"record": "SPF", "note": "Verify include:_spf.klaviyo.com in DNS"},
                {"record": "DKIM", "note": "Verify CNAME records from Klaviyo Settings"},
                {"record": "DMARC", "note": "Verify DMARC policy (p=quarantine or p=reject)"},
            ],
            "recommendations": self._recommend_deliverability_fixes(
                bounce_rate, complaint_rate, issues
            ),
        }

        return analysis

    def revenue_attribution(self) -> Dict:
        """
        Analyze revenue split between flows and campaigns.

        Returns:
            Dictionary with revenue attribution data and recommendations
        """
        # Get flow and campaign revenue
        flows = self.client.get_flows()
        campaigns = self.client.get_campaigns()

        flow_revenue = 0.0
        flow_data = []
        for flow in flows:
            flow_id = flow.get("id")
            if not flow_id:
                continue
            try:
                report = self.client.get_flow_report(flow_id)
                if report:
                    stats = report if isinstance(report, dict) else {}
                    rev = float(stats.get("revenue", 0) or 0)
                    flow_revenue += rev
                    if rev > 0:
                        flow_data.append({
                            "name": flow.get("name"),
                            "revenue": round(rev, 2),
                            "status": flow.get("status"),
                        })
            except Exception:
                continue

        campaign_revenue = 0.0
        campaign_data = []
        for campaign in campaigns[:20]:
            campaign_id = campaign.get("id")
            if not campaign_id:
                continue
            try:
                report = self.client.get_campaign_report(campaign_id)
                if report:
                    stats = report if isinstance(report, dict) else {}
                    rev = float(stats.get("revenue", 0) or 0)
                    campaign_revenue += rev
                    if rev > 0:
                        campaign_data.append({
                            "name": campaign.get("name"),
                            "revenue": round(rev, 2),
                        })
            except Exception:
                continue

        total_revenue = flow_revenue + campaign_revenue
        flow_pct = (flow_revenue / total_revenue * 100) if total_revenue > 0 else 0
        campaign_pct = (campaign_revenue / total_revenue * 100) if total_revenue > 0 else 0

        # Sort by revenue
        flow_data.sort(key=lambda x: x["revenue"], reverse=True)
        campaign_data.sort(key=lambda x: x["revenue"], reverse=True)

        # Assess flow revenue percentage
        flow_rev_assessment = self._assess_metric(
            "flow_revenue_pct", flow_pct / 100 if flow_pct else 0
        )

        analysis = {
            "summary": {
                "total_revenue": round(total_revenue, 2),
                "flow_revenue": round(flow_revenue, 2),
                "campaign_revenue": round(campaign_revenue, 2),
                "flow_revenue_pct": round(flow_pct, 1),
                "campaign_revenue_pct": round(campaign_pct, 1),
            },
            "assessment": flow_rev_assessment,
            "top_flows": flow_data[:10],
            "top_campaigns": campaign_data[:10],
            "recommendations": self._recommend_revenue_improvements(
                flow_pct, flow_data, campaign_data
            ),
        }

        return analysis

    def full_audit(self) -> Dict:
        """
        Run a complete account audit combining all analysis types.

        Returns:
            Dictionary with all audit sections
        """
        return {
            "flow_audit": self.audit_flows(),
            "segment_health": self.analyze_segments(),
            "campaign_performance": self.compare_campaigns(),
            "deliverability": self.check_deliverability(),
            "revenue_attribution": self.revenue_attribution(),
        }

    def _assess_metric(self, name: str, value: float) -> Dict:
        """
        Compare a metric against benchmarks.

        Args:
            name: Metric name (must exist in BENCHMARKS)
            value: Metric value as decimal (e.g., 0.25 for 25%)

        Returns:
            Dictionary with rating and context
        """
        bench = self.BENCHMARKS.get(name)
        if not bench:
            return {"rating": "unknown", "value": value}

        # For rates where lower is better
        lower_is_better = name in [
            "unsubscribe_rate",
            "spam_complaint_rate",
            "bounce_rate",
        ]

        if lower_is_better:
            if value <= bench["great"]:
                rating = "great"
            elif value <= bench["good"]:
                rating = "good"
            elif value <= bench["warning"]:
                rating = "warning"
            else:
                rating = "critical"
        else:
            if value >= bench["great"]:
                rating = "great"
            elif value >= bench["good"]:
                rating = "good"
            elif value >= bench["warning"]:
                rating = "warning"
            else:
                rating = "critical"

        return {
            "rating": rating,
            "value": round(value * 100, 2),
            "benchmark_good": round(bench["good"] * 100, 2),
            "benchmark_great": round(bench["great"] * 100, 2),
        }

    def _recommend_flow_improvements(self, checklist: List[Dict]) -> List[Dict]:
        """Generate recommendations for flow gaps and improvements."""
        recommendations = []

        missing_flows = [f for f in checklist if f["status"] == "missing"]

        for flow in missing_flows:
            recommendations.append({
                "priority": flow["priority"],
                "action": f"Create {flow['flow']} flow",
                "reason": f"Missing essential flow (trigger: {flow['trigger']})",
                "expected_impact": self._flow_impact_estimate(flow["name"]),
            })

        if not missing_flows:
            recommendations.append({
                "priority": "INFO",
                "action": "All essential flows present",
                "reason": "Focus on optimizing existing flows",
                "expected_impact": "Incremental 10-20% improvement per flow",
            })

        return recommendations

    def _recommend_segment_improvements(
        self, tiers: Dict, has_rfm: bool, has_predictive: bool
    ) -> List[Dict]:
        """Generate recommendations for segment strategy."""
        recommendations = []

        if not tiers.get("active") and not tiers.get("warm"):
            recommendations.append({
                "priority": "HIGH",
                "action": "Create engagement tier segments",
                "reason": "No engagement-based segmentation found",
                "expected_impact": "20-30% improvement in campaign targeting",
            })

        if not tiers.get("suppression"):
            recommendations.append({
                "priority": "HIGH",
                "action": "Create suppression segment",
                "reason": "No suppression segment for unengaged contacts",
                "expected_impact": "Protect deliverability, reduce costs",
            })

        if not has_rfm:
            recommendations.append({
                "priority": "MEDIUM",
                "action": "Implement RFM segmentation",
                "reason": "No RFM-based segments detected",
                "expected_impact": "15-25% lift in campaign revenue",
            })

        if not has_predictive:
            recommendations.append({
                "priority": "MEDIUM",
                "action": "Enable predictive segments",
                "reason": "Not using Klaviyo predictive analytics (CLV, churn risk)",
                "expected_impact": "10-20% better targeting for winback and VIP flows",
            })

        return recommendations

    def _recommend_campaign_improvements(
        self, metrics: Dict, assessments: Dict
    ) -> List[Dict]:
        """Generate recommendations for campaign performance."""
        recommendations = []

        if assessments.get("open_rate", {}).get("rating") in ["warning", "critical"]:
            recommendations.append({
                "priority": "HIGH",
                "action": "Improve subject lines and sender reputation",
                "reason": f"Open rate {metrics['open_rate'] * 100:.1f}% below benchmark",
                "expected_impact": "20-40% increase in open rates",
            })

        if assessments.get("click_rate", {}).get("rating") in ["warning", "critical"]:
            recommendations.append({
                "priority": "HIGH",
                "action": "Optimize email content and CTAs",
                "reason": f"Click rate {metrics['click_rate'] * 100:.1f}% below benchmark",
                "expected_impact": "30-50% increase in click rates",
            })

        if assessments.get("unsubscribe_rate", {}).get("rating") in [
            "warning",
            "critical",
        ]:
            recommendations.append({
                "priority": "HIGH",
                "action": "Reduce send frequency or improve segmentation",
                "reason": f"Unsubscribe rate {metrics['unsubscribe_rate'] * 100:.2f}% above threshold",
                "expected_impact": "50% reduction in unsubscribes",
            })

        return recommendations

    def _recommend_deliverability_fixes(
        self, bounce_rate: float, complaint_rate: float, issues: List[Dict]
    ) -> List[Dict]:
        """Generate recommendations for deliverability improvement."""
        recommendations = []

        if bounce_rate > 0.02:
            recommendations.append({
                "priority": "HIGH",
                "action": "Implement list cleaning",
                "reason": "Elevated bounce rate indicates stale email addresses",
                "expected_impact": "Reduce bounces by 60-80%",
            })

        if complaint_rate > 0.0005:
            recommendations.append({
                "priority": "HIGH",
                "action": "Review sending frequency and content relevance",
                "reason": "Spam complaints above safe threshold",
                "expected_impact": "Reduce complaints by 50-70%",
            })

        recommendations.append({
            "priority": "MEDIUM",
            "action": "Verify DNS authentication (SPF, DKIM, DMARC)",
            "reason": "Authentication protects sender reputation",
            "expected_impact": "Improved inbox placement across all ISPs",
        })

        if not issues:
            recommendations.insert(0, {
                "priority": "INFO",
                "action": "Deliverability metrics within healthy range",
                "reason": "No critical issues detected",
                "expected_impact": "Continue monitoring",
            })

        return recommendations

    def _recommend_revenue_improvements(
        self, flow_pct: float, flow_data: List[Dict], campaign_data: List[Dict]
    ) -> List[Dict]:
        """Generate recommendations for revenue optimization."""
        recommendations = []

        if flow_pct < 30:
            recommendations.append({
                "priority": "HIGH",
                "action": "Increase flow automation coverage",
                "reason": f"Flow revenue at {flow_pct:.0f}% (benchmark: 30-50%)",
                "expected_impact": "Shift 10-20% more revenue to automated flows",
            })

        if flow_pct > 70:
            recommendations.append({
                "priority": "MEDIUM",
                "action": "Invest in campaign strategy",
                "reason": f"Over-reliant on flows ({flow_pct:.0f}% of revenue)",
                "expected_impact": "Diversify revenue sources, reduce flow fatigue",
            })

        if len(flow_data) < 5:
            recommendations.append({
                "priority": "HIGH",
                "action": "Add more revenue-generating flows",
                "reason": f"Only {len(flow_data)} flows generating revenue",
                "expected_impact": "Each new flow adds 5-15% incremental revenue",
            })

        return recommendations

    def _flow_impact_estimate(self, flow_name: str) -> str:
        """Estimate revenue impact of adding a missing flow."""
        impact_map = {
            "Welcome Series": "10-15% of total email revenue",
            "Abandoned Cart": "15-25% of total email revenue",
            "Browse Abandonment": "5-10% of total email revenue",
            "Post-Purchase": "8-12% of total email revenue",
            "Winback": "5-8% of total email revenue",
            "Sunset/Re-engagement": "Protect deliverability, reduce costs",
            "Review Request": "Indirect: increases social proof and conversion",
            "Replenishment": "5-10% of total email revenue (if applicable)",
            "Birthday/Anniversary": "2-5% of total email revenue",
            "VIP/Loyalty": "3-8% of total email revenue from high-value segment",
        }
        return impact_map.get(flow_name, "Incremental revenue improvement")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Klaviyo marketing data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full account audit
  python analyze.py --analysis-type full-audit

  # Audit flows against essential checklist
  python analyze.py --analysis-type flow-audit

  # Check segment health
  python analyze.py --analysis-type segment-health

  # Compare campaign performance
  python analyze.py --analysis-type campaign-comparison --days 30

  # Run deliverability diagnostics
  python analyze.py --analysis-type deliverability

  # Analyze revenue attribution
  python analyze.py --analysis-type revenue-attribution

  # Export audit to file
  python analyze.py --analysis-type full-audit --output audit.json
        """,
    )

    parser.add_argument(
        "--analysis-type",
        required=True,
        choices=[
            "flow-audit",
            "segment-health",
            "campaign-comparison",
            "deliverability",
            "revenue-attribution",
            "full-audit",
        ],
        help="Type of analysis to perform",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to analyze (default: 30)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--output",
        help="Output file path (default: stdout)",
    )

    args = parser.parse_args()

    try:
        analyzer = KlaviyoAnalyzer()

        # Run analysis
        if args.analysis_type == "flow-audit":
            result = analyzer.audit_flows()
        elif args.analysis_type == "segment-health":
            result = analyzer.analyze_segments()
        elif args.analysis_type == "campaign-comparison":
            result = analyzer.compare_campaigns(days=args.days)
        elif args.analysis_type == "deliverability":
            result = analyzer.check_deliverability()
        elif args.analysis_type == "revenue-attribution":
            result = analyzer.revenue_attribution()
        elif args.analysis_type == "full-audit":
            result = analyzer.full_audit()

        # Format output
        output = json.dumps(result, indent=2, default=str)

        # Write output
        if args.output:
            safe_path = _safe_output_path(args.output)
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Analysis saved to {args.output}", file=sys.stderr)
        else:
            print(output)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("Error: Analysis failed. Check your API key and network connection.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
