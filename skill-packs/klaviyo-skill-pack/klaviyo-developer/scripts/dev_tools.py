#!/usr/bin/env python3
"""
Klaviyo Developer Tools

Higher-level developer utilities for Klaviyo integration management:
- Integration health check
- Event validation
- Webhook testing
- CSV import with progress
- Paginated data export

Usage:
    python dev_tools.py --tool health-check
    python dev_tools.py --tool validate-events --events "Placed Order,Started Checkout"
    python dev_tools.py --tool test-webhook --webhook-url https://example.com/webhook
    python dev_tools.py --tool import-csv --file contacts.csv --list-id LIST_ID
    python dev_tools.py --tool export-data --resource profiles --max-records 1000
"""

import os
import sys
import json
import csv
import time
import argparse
import hashlib
import hmac
from typing import Dict, List, Optional
from datetime import datetime

try:
    from klaviyo_client import KlaviyoDevClient
except ImportError:
    print("Error: klaviyo_client.py not found in the same directory", file=sys.stderr)
    sys.exit(1)


class KlaviyoDevTools:
    """Developer utilities for Klaviyo integration management."""

    def __init__(self):
        """Initialize with Klaviyo developer client."""
        self.client = KlaviyoDevClient()

    def health_check(self) -> Dict:
        """
        Check API connectivity, scopes, rate limits, and event health.

        Returns:
            Dictionary with health check results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "status": "healthy",
        }

        # Check 1: API connectivity
        try:
            metrics = self.client.get_metrics()
            results["checks"].append({
                "check": "API Connectivity",
                "status": "pass",
                "detail": "Successfully connected to Klaviyo API",
            })
        except Exception as e:
            results["checks"].append({
                "check": "API Connectivity",
                "status": "fail",
                "detail": f"Failed to connect: {e}",
            })
            results["status"] = "unhealthy"
            return results

        # Check 2: Read scopes (profiles)
        try:
            profiles = self.client.export_profiles(page_size=1, max_pages=1)
            results["checks"].append({
                "check": "Profile Read Scope",
                "status": "pass",
                "detail": "profiles:read scope verified",
            })
        except Exception as e:
            results["checks"].append({
                "check": "Profile Read Scope",
                "status": "fail",
                "detail": f"profiles:read may not be enabled: {e}",
            })

        # Check 3: Metrics availability
        try:
            metric_count = len(metrics) if isinstance(metrics, list) else 0
            results["checks"].append({
                "check": "Metrics Available",
                "status": "pass",
                "detail": f"{metric_count} event types found",
            })

            # Check for essential e-commerce events
            metric_names = [
                m.get("name", "").lower()
                for m in metrics
                if isinstance(m, dict)
            ]
            essential_events = [
                "placed order",
                "started checkout",
                "viewed product",
                "added to cart",
            ]
            found_events = [
                e for e in essential_events if e in metric_names
            ]
            missing_events = [
                e for e in essential_events if e not in metric_names
            ]

            if missing_events:
                results["checks"].append({
                    "check": "E-commerce Events",
                    "status": "warning",
                    "detail": f"Missing: {', '.join(missing_events)}",
                })
            else:
                results["checks"].append({
                    "check": "E-commerce Events",
                    "status": "pass",
                    "detail": f"All {len(essential_events)} essential events present",
                })

        except Exception as e:
            results["checks"].append({
                "check": "Metrics Available",
                "status": "fail",
                "detail": str(e),
            })

        # Check 4: Catalog access
        try:
            catalog = self.client.get_catalog_items()
            item_count = len(catalog) if isinstance(catalog, list) else 0
            results["checks"].append({
                "check": "Catalog Access",
                "status": "pass",
                "detail": f"catalogs:read verified ({item_count} items found)",
            })
        except Exception as e:
            results["checks"].append({
                "check": "Catalog Access",
                "status": "warning",
                "detail": f"catalogs:read may not be enabled: {e}",
            })

        # Set overall status
        statuses = [c["status"] for c in results["checks"]]
        if "fail" in statuses:
            results["status"] = "unhealthy"
        elif "warning" in statuses:
            results["status"] = "degraded"

        results["recommendations"] = self._recommend_health_fixes(results["checks"])

        return results

    def validate_events(self, event_names: List[str]) -> Dict:
        """
        Check that expected events exist and are being tracked.

        Args:
            event_names: List of event names to validate

        Returns:
            Dictionary with validation results
        """
        metrics = self.client.get_metrics()
        metric_names = [
            m.get("name", "") for m in metrics if isinstance(m, dict)
        ]
        metric_names_lower = [n.lower() for n in metric_names]

        results = []
        for event in event_names:
            found = event.lower() in metric_names_lower
            results.append({
                "event": event,
                "status": "found" if found else "missing",
            })

        found_count = sum(1 for r in results if r["status"] == "found")

        return {
            "summary": {
                "events_checked": len(event_names),
                "events_found": found_count,
                "events_missing": len(event_names) - found_count,
            },
            "results": results,
            "available_events": metric_names,
            "recommendations": self._recommend_event_fixes(results),
        }

    def test_webhook(self, url: str, secret: Optional[str] = None) -> Dict:
        """
        Send a test payload to a webhook URL and report results.

        Args:
            url: Webhook endpoint URL
            secret: Optional webhook secret for signature generation

        Returns:
            Dictionary with test results
        """
        import urllib.request
        import urllib.error

        test_payload = json.dumps({
            "type": "test",
            "data": {
                "type": "event",
                "attributes": {
                    "metric_name": "webhook_test",
                    "timestamp": datetime.now().isoformat(),
                    "properties": {"source": "klaviyo-dev-tools"},
                },
            },
        })

        headers = {"Content-Type": "application/json"}

        if secret:
            signature = hmac.new(
                secret.encode(), test_payload.encode(), hashlib.sha256
            ).hexdigest()
            headers["X-Klaviyo-Webhook-Signature"] = signature

        results = {
            "url": url,
            "payload_size": len(test_payload),
            "signature_included": bool(secret),
        }

        try:
            req = urllib.request.Request(
                url,
                data=test_payload.encode(),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                results["status"] = "pass"
                results["response_code"] = response.status
                results["response_body"] = response.read().decode()[:500]

        except urllib.error.HTTPError as e:
            results["status"] = "fail"
            results["response_code"] = e.code
            results["error"] = str(e)

        except urllib.error.URLError as e:
            results["status"] = "fail"
            results["error"] = f"Connection failed: {e.reason}"

        except Exception as e:
            results["status"] = "fail"
            results["error"] = str(e)

        return results

    def import_csv(
        self, filepath: str, list_id: Optional[str] = None
    ) -> Dict:
        """
        Import profiles from CSV with batching and progress reporting.

        Args:
            filepath: Path to CSV file
            list_id: Optional list ID to add profiles to

        Returns:
            Dictionary with import results
        """
        # Read CSV
        profiles = []
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                profiles.append(dict(row))

        total = len(profiles)
        batch_size = 10000
        results = {
            "file": filepath,
            "total_profiles": total,
            "batches": [],
            "errors": [],
        }

        # Process in batches
        for i in range(0, total, batch_size):
            batch = profiles[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size

            print(
                f"Batch {batch_num}/{total_batches}: "
                f"importing {len(batch)} profiles...",
                file=sys.stderr,
            )

            try:
                result = self.client.bulk_import(batch, list_id=list_id)
                results["batches"].append({
                    "batch": batch_num,
                    "profiles": len(batch),
                    "status": "submitted",
                    "job_id": result.get("job_id"),
                })
            except Exception as e:
                results["batches"].append({
                    "batch": batch_num,
                    "profiles": len(batch),
                    "status": "failed",
                    "error": str(e),
                })
                results["errors"].append(str(e))

        # Summary
        successful = sum(
            1 for b in results["batches"] if b["status"] == "submitted"
        )
        results["summary"] = {
            "batches_submitted": successful,
            "batches_failed": len(results["batches"]) - successful,
            "profiles_submitted": sum(
                b["profiles"]
                for b in results["batches"]
                if b["status"] == "submitted"
            ),
        }

        return results

    def export_data(
        self,
        resource: str,
        output_path: Optional[str] = None,
        max_records: Optional[int] = None,
    ) -> Dict:
        """
        Export data with pagination to CSV.

        Args:
            resource: Resource type (profiles, events, catalog)
            output_path: Output CSV file path
            max_records: Maximum records to export

        Returns:
            Dictionary with export summary
        """
        max_pages = None
        if max_records:
            max_pages = (max_records + 99) // 100

        if resource == "profiles":
            data = self.client.export_profiles(
                page_size=100, max_pages=max_pages
            )
        elif resource == "catalog":
            data = self.client.get_catalog_items()
        elif resource == "events":
            # Events don't have a simple paginated export via SDK
            data = []
            print(
                "Note: Event export requires metric aggregation API. "
                "Use --resource profiles or catalog instead.",
                file=sys.stderr,
            )
        else:
            raise ValueError(f"Unsupported resource type: {resource}")

        if max_records and len(data) > max_records:
            data = data[:max_records]

        # Write CSV if output specified
        if output_path and data:
            all_keys = []
            for row in data:
                for key in row.keys():
                    if key not in all_keys:
                        all_keys.append(key)

            with open(output_path, "w", newline="") as f:
                writer = csv.DictWriter(
                    f, fieldnames=all_keys, extrasaction="ignore"
                )
                writer.writeheader()
                for row in data:
                    clean_row = {}
                    for k, v in row.items():
                        if isinstance(v, (dict, list)):
                            clean_row[k] = json.dumps(v)
                        else:
                            clean_row[k] = v
                    writer.writerow(clean_row)

            print(f"Exported {len(data)} records to {output_path}", file=sys.stderr)

        return {
            "resource": resource,
            "records_exported": len(data),
            "output_file": output_path,
        }

    def _recommend_health_fixes(self, checks: List[Dict]) -> List[Dict]:
        """Generate recommendations from health check results."""
        recommendations = []

        for check in checks:
            if check["status"] == "fail":
                if "connectivity" in check["check"].lower():
                    recommendations.append({
                        "priority": "CRITICAL",
                        "action": "Fix API authentication",
                        "reason": check["detail"],
                        "expected_impact": "Restore all Klaviyo integrations",
                    })
                elif "scope" in check["check"].lower():
                    recommendations.append({
                        "priority": "HIGH",
                        "action": f"Enable missing scope for {check['check']}",
                        "reason": check["detail"],
                        "expected_impact": "Restore access to this resource",
                    })
            elif check["status"] == "warning":
                if "events" in check["check"].lower():
                    recommendations.append({
                        "priority": "HIGH",
                        "action": "Implement missing e-commerce event tracking",
                        "reason": check["detail"],
                        "expected_impact": "Enable automated flows for missing events",
                    })

        if not recommendations:
            recommendations.append({
                "priority": "INFO",
                "action": "All health checks passed",
                "reason": "Integration is healthy",
                "expected_impact": "Continue monitoring",
            })

        return recommendations

    def _recommend_event_fixes(self, results: List[Dict]) -> List[Dict]:
        """Generate recommendations from event validation results."""
        recommendations = []

        missing = [r for r in results if r["status"] == "missing"]

        for event in missing:
            recommendations.append({
                "priority": "HIGH",
                "action": f"Implement tracking for '{event['event']}'",
                "reason": f"Event '{event['event']}' not found in Klaviyo",
                "expected_impact": "Enable flows and segments triggered by this event",
            })

        if not missing:
            recommendations.append({
                "priority": "INFO",
                "action": "All expected events are being tracked",
                "reason": "Event validation passed",
                "expected_impact": "Continue monitoring event freshness",
            })

        return recommendations


def main():
    parser = argparse.ArgumentParser(
        description="Klaviyo developer tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run integration health check
  python dev_tools.py --tool health-check

  # Validate expected events exist
  python dev_tools.py --tool validate-events \\
      --events "Placed Order,Started Checkout,Viewed Product"

  # Test a webhook endpoint
  python dev_tools.py --tool test-webhook \\
      --webhook-url https://example.com/webhooks/klaviyo

  # Test webhook with signature verification
  python dev_tools.py --tool test-webhook \\
      --webhook-url https://example.com/webhooks/klaviyo \\
      --webhook-secret your-secret-here

  # Import profiles from CSV
  python dev_tools.py --tool import-csv \\
      --file contacts.csv --list-id LIST_ID

  # Export profiles to CSV
  python dev_tools.py --tool export-data \\
      --resource profiles --max-records 5000 --output profiles.csv
        """,
    )

    parser.add_argument(
        "--tool",
        required=True,
        choices=[
            "health-check",
            "validate-events",
            "test-webhook",
            "import-csv",
            "export-data",
        ],
        help="Tool to run",
    )
    parser.add_argument(
        "--events",
        help="Comma-separated event names (for validate-events)",
    )
    parser.add_argument(
        "--webhook-url",
        help="Webhook URL to test (for test-webhook)",
    )
    parser.add_argument(
        "--webhook-secret",
        help="Webhook secret for signature (for test-webhook)",
    )
    parser.add_argument(
        "--file",
        help="CSV file path (for import-csv)",
    )
    parser.add_argument(
        "--list-id",
        help="List ID (for import-csv)",
    )
    parser.add_argument(
        "--resource",
        choices=["profiles", "events", "catalog"],
        help="Resource to export (for export-data)",
    )
    parser.add_argument(
        "--max-records",
        type=int,
        help="Max records to export (for export-data)",
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
        tools = KlaviyoDevTools()

        if args.tool == "health-check":
            result = tools.health_check()

        elif args.tool == "validate-events":
            if not args.events:
                parser.error("--events is required for validate-events")
            event_list = [e.strip() for e in args.events.split(",")]
            result = tools.validate_events(event_list)

        elif args.tool == "test-webhook":
            if not args.webhook_url:
                parser.error("--webhook-url is required for test-webhook")
            result = tools.test_webhook(
                args.webhook_url, secret=args.webhook_secret
            )

        elif args.tool == "import-csv":
            if not args.file:
                parser.error("--file is required for import-csv")
            result = tools.import_csv(args.file, list_id=args.list_id)

        elif args.tool == "export-data":
            if not args.resource:
                parser.error("--resource is required for export-data")
            result = tools.export_data(
                args.resource,
                output_path=args.output,
                max_records=args.max_records,
            )

        # Format output
        output = json.dumps(result, indent=2, default=str)

        # Write output
        if args.output and args.tool != "export-data":
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Results saved to {args.output}", file=sys.stderr)
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
