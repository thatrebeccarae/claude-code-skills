#!/usr/bin/env python3
"""
Klaviyo Analytics API Client

Read-only SDK wrapper for fetching Klaviyo marketing data including
flows, campaigns, segments, lists, metrics, and performance reports.

Usage:
    python klaviyo_client.py --resource flows
    python klaviyo_client.py --resource campaigns --format table
    python klaviyo_client.py --resource report --report-type flow --id FLOW_ID
    python klaviyo_client.py --resource metrics --format json --output metrics.json

Environment Variables:
    KLAVIYO_API_KEY: Klaviyo private API key (required, starts with "pk_")
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Optional

try:
    from klaviyo_api import KlaviyoAPI
    from dotenv import load_dotenv
except ImportError:
    print("Error: Required packages not installed.", file=sys.stderr)
    print("Install with: pip install klaviyo-api python-dotenv", file=sys.stderr)
    sys.exit(1)


def _safe_output_path(path: str) -> str:
    """Validate output path does not escape working directory."""
    resolved = os.path.realpath(path)
    cwd = os.path.realpath(os.getcwd())
    if not resolved.startswith(cwd + os.sep) and resolved != cwd:
        raise ValueError(f"Output path must be within working directory: {cwd}")
    return resolved


class KlaviyoAnalyticsClient:
    """Read-only client for fetching Klaviyo marketing analytics data."""

    API_REVISION = "2025-10-15"

    def __init__(self):
        """Initialize the client with credentials from environment."""
        load_dotenv()

        api_key = os.environ.get("KLAVIYO_API_KEY")
        if not api_key:
            raise ValueError(
                "KLAVIYO_API_KEY environment variable not set. "
                "Find your API key in Klaviyo: Settings > Account > API Keys"
            )

        if not api_key.startswith("pk_"):
            raise ValueError(
                "KLAVIYO_API_KEY should start with 'pk_'. "
                "Use a Private API Key, not a Public API Key."
            )

        try:
            self.client = KlaviyoAPI(api_key, max_delay=60, max_retries=3)
        except Exception:
            raise RuntimeError("Failed to initialize Klaviyo client. Check your API key.")

    def get_flows(self, filter_str: Optional[str] = None) -> List[Dict]:
        """
        List all flows with status and trigger information.

        Args:
            filter_str: Optional filter (e.g., 'equals(status,"live")')

        Returns:
            List of flow dictionaries with id, name, status, trigger_type
        """
        try:
            kwargs = {}
            if filter_str:
                kwargs["filter"] = filter_str

            response = self.client.Flows.get_flows(**kwargs)
            return self._parse_jsonapi_response(response)
        except Exception:
            raise RuntimeError("Failed to fetch flows. Check API key scopes.")

    def get_campaigns(self, filter_str: Optional[str] = None) -> List[Dict]:
        """
        List campaigns with send status and performance summary.

        Args:
            filter_str: Optional filter (e.g., 'equals(messages.channel,"email")')

        Returns:
            List of campaign dictionaries
        """
        try:
            kwargs = {}
            if filter_str:
                kwargs["filter"] = filter_str

            response = self.client.Campaigns.get_campaigns(**kwargs)
            return self._parse_jsonapi_response(response)
        except Exception:
            raise RuntimeError("Failed to fetch campaigns. Check API key scopes.")

    def get_segments(self) -> List[Dict]:
        """
        List all segments.

        Returns:
            List of segment dictionaries with id, name, and profile count
        """
        try:
            response = self.client.Segments.get_segments()
            return self._parse_jsonapi_response(response)
        except Exception:
            raise RuntimeError("Failed to fetch segments. Check API key scopes.")

    def get_lists(self) -> List[Dict]:
        """
        List all lists.

        Returns:
            List of list dictionaries with id, name, and profile count
        """
        try:
            response = self.client.Lists.get_lists()
            return self._parse_jsonapi_response(response)
        except Exception:
            raise RuntimeError("Failed to fetch lists. Check API key scopes.")

    def get_flow_report(self, flow_id: str) -> Dict:
        """
        Get performance metrics for a specific flow.

        Args:
            flow_id: The flow ID to get a report for

        Returns:
            Dictionary with flow performance metrics
        """
        try:
            body = {
                "data": {
                    "type": "flow-values-report",
                    "attributes": {
                        "statistics": [
                            "opens",
                            "unique_opens",
                            "clicks",
                            "unique_clicks",
                            "recipients",
                            "deliveries",
                            "bounces",
                            "unsubscribes",
                            "spam_complaints",
                            "revenue",
                        ],
                        "timeframe": {"key": "last_365_days"},
                        "conversion_metric_id": "placed_order",
                        "filter": f"equals(flow_id,\"{flow_id}\")",
                    },
                }
            }
            response = self.client.Reporting.query_flow_values(body)
            return self._parse_jsonapi_response(response)
        except Exception:
            raise RuntimeError(f"Failed to fetch flow report for {flow_id}.")

    def get_campaign_report(self, campaign_id: str) -> Dict:
        """
        Get performance metrics for a specific campaign.

        Args:
            campaign_id: The campaign ID to get a report for

        Returns:
            Dictionary with campaign performance metrics
        """
        try:
            body = {
                "data": {
                    "type": "campaign-values-report",
                    "attributes": {
                        "statistics": [
                            "opens",
                            "unique_opens",
                            "clicks",
                            "unique_clicks",
                            "recipients",
                            "deliveries",
                            "bounces",
                            "unsubscribes",
                            "spam_complaints",
                            "revenue",
                        ],
                        "timeframe": {"key": "last_365_days"},
                        "conversion_metric_id": "placed_order",
                        "filter": f"equals(campaign_id,\"{campaign_id}\")",
                    },
                }
            }
            response = self.client.Reporting.query_campaign_values(body)
            return self._parse_jsonapi_response(response)
        except Exception:
            raise RuntimeError(
                f"Failed to fetch campaign report for {campaign_id}."
            )

    def get_metrics(self) -> List[Dict]:
        """
        List all available event types (metrics).

        Returns:
            List of metric dictionaries with id and name
        """
        try:
            response = self.client.Metrics.get_metrics()
            return self._parse_jsonapi_response(response)
        except Exception:
            raise RuntimeError("Failed to fetch metrics. Check API key scopes.")

    def _parse_jsonapi_response(self, response) -> List[Dict]:
        """
        Flatten JSON:API envelope into simple dictionaries.

        Args:
            response: SDK response object

        Returns:
            List of flattened dictionaries or a single dictionary
        """
        if hasattr(response, "to_dict"):
            response = response.to_dict()
        elif isinstance(response, str):
            response = json.loads(response)

        data = response.get("data", response)

        if isinstance(data, list):
            return [self._flatten_resource(item) for item in data]
        elif isinstance(data, dict):
            return self._flatten_resource(data)
        else:
            return data

    def _flatten_resource(self, resource: Dict) -> Dict:
        """Flatten a single JSON:API resource object."""
        flat = {
            "id": resource.get("id"),
            "type": resource.get("type"),
        }

        attributes = resource.get("attributes", {})
        if attributes:
            flat.update(attributes)

        return flat


def format_as_table(data, resource_type: str) -> str:
    """Format result as a human-readable table."""
    if not data:
        return "No data found."

    if isinstance(data, dict):
        data = [data]

    # Select columns based on resource type
    column_map = {
        "flows": ["id", "name", "status", "trigger_type"],
        "campaigns": ["id", "name", "status", "send_strategy"],
        "segments": ["id", "name"],
        "lists": ["id", "name"],
        "metrics": ["id", "name"],
        "report": None,
    }

    columns = column_map.get(resource_type)

    if columns is None:
        return json.dumps(data, indent=2, default=str)

    # Filter to available columns
    available_cols = [c for c in columns if any(c in item for item in data)]
    if not available_cols:
        available_cols = list(data[0].keys())[:5]

    # Build header
    lines = []
    header = " | ".join(col.replace("_", " ").title() for col in available_cols)
    lines.append(header)
    lines.append("-" * len(header))

    # Build rows
    for item in data:
        values = [str(item.get(col, "")) for col in available_cols]
        lines.append(" | ".join(values))

    lines.append("")
    lines.append(f"Total: {len(data)} {resource_type}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch Klaviyo analytics data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all flows
  python klaviyo_client.py --resource flows

  # List only live flows
  python klaviyo_client.py --resource flows --filter 'equals(status,"live")'

  # Get campaign report
  python klaviyo_client.py --resource report --report-type campaign --id CAMPAIGN_ID

  # List segments as table
  python klaviyo_client.py --resource segments --format table

  # Export metrics to file
  python klaviyo_client.py --resource metrics --output metrics.json
        """,
    )

    parser.add_argument(
        "--resource",
        required=True,
        choices=["flows", "campaigns", "segments", "lists", "metrics", "report"],
        help="Resource type to fetch",
    )
    parser.add_argument(
        "--report-type",
        choices=["flow", "campaign"],
        help="Report type (required when --resource report)",
    )
    parser.add_argument(
        "--id",
        help="Resource ID (required for report)",
    )
    parser.add_argument(
        "--filter",
        help="API filter expression (e.g., 'equals(status,\"live\")')",
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

    # Validate report arguments
    if args.resource == "report":
        if not args.report_type:
            parser.error("--report-type is required when --resource is 'report'")
        if not args.id:
            parser.error("--id is required when --resource is 'report'")

    try:
        client = KlaviyoAnalyticsClient()

        # Fetch data
        if args.resource == "flows":
            result = client.get_flows(filter_str=args.filter)
        elif args.resource == "campaigns":
            result = client.get_campaigns(filter_str=args.filter)
        elif args.resource == "segments":
            result = client.get_segments()
        elif args.resource == "lists":
            result = client.get_lists()
        elif args.resource == "metrics":
            result = client.get_metrics()
        elif args.resource == "report":
            if args.report_type == "flow":
                result = client.get_flow_report(args.id)
            else:
                result = client.get_campaign_report(args.id)

        # Format output
        if args.format == "json":
            output = json.dumps(result, indent=2, default=str)
        else:
            output = format_as_table(result, args.resource)

        # Write output
        if args.output:
            safe_path = _safe_output_path(args.output)
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Data saved to {args.output}", file=sys.stderr)
        else:
            print(output)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("Error: Operation failed. Check your API key and network connection.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
