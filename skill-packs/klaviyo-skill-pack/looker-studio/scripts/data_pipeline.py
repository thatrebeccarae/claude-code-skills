#!/usr/bin/env python3
"""
Looker Studio Data Pipeline

Pushes Klaviyo, Shopify, and GA4 data to Google Sheets for
Looker Studio ingestion. Solves the common DTC problem where
free Looker Studio connectors for Klaviyo are limited.

Pattern: Klaviyo/Shopify API -> Google Sheets -> Looker Studio

Usage:
    python data_pipeline.py --action sync-klaviyo --sheet-id SPREADSHEET_ID
    python data_pipeline.py --action sync-shopify --sheet-id SPREADSHEET_ID --days 30
    python data_pipeline.py --action create-sheet --template crm-dashboard
    python data_pipeline.py --action list-templates

Environment Variables:
    GOOGLE_SHEETS_CREDENTIALS_PATH: Path to Google service account JSON (required)
    GOOGLE_SHEETS_SPREADSHEET_ID: Default spreadsheet ID (optional)
    KLAVIYO_API_KEY: Klaviyo private API key (for sync-klaviyo)
    SHOPIFY_STORE_URL: Shopify store URL (for sync-shopify)
    SHOPIFY_ACCESS_TOKEN: Shopify Admin API token (for sync-shopify)
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    import gspread
    from google.oauth2.service_account import Credentials
    from dotenv import load_dotenv
except ImportError:
    print("Error: Required packages not installed.", file=sys.stderr)
    print(
        "Install with: pip install gspread google-auth python-dotenv",
        file=sys.stderr,
    )
    sys.exit(1)


SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

TEMPLATES = {
    "crm-dashboard": {
        "description": "CRM Performance Dashboard — email/SMS KPIs, list growth, engagement tiers",
        "sheets": [
            {
                "name": "Campaign Metrics",
                "headers": [
                    "Date", "Campaign Name", "Channel", "Recipients",
                    "Opens", "Open Rate", "Clicks", "Click Rate",
                    "Conversions", "Revenue", "Unsubscribes",
                ],
            },
            {
                "name": "Flow Metrics",
                "headers": [
                    "Date", "Flow Name", "Flow Type", "Messages Sent",
                    "Opens", "Open Rate", "Clicks", "Click Rate",
                    "Conversions", "Revenue",
                ],
            },
            {
                "name": "List Growth",
                "headers": [
                    "Date", "List Name", "New Subscribers", "Unsubscribes",
                    "Net Growth", "Total Size",
                ],
            },
        ],
    },
    "lifecycle": {
        "description": "Lifecycle Marketing Dashboard — flow performance across customer journey",
        "sheets": [
            {
                "name": "Lifecycle Flows",
                "headers": [
                    "Date", "Flow Name", "Stage", "Messages Sent",
                    "Delivered", "Opens", "Clicks", "Conversions",
                    "Revenue", "Revenue Per Recipient",
                ],
            },
            {
                "name": "Customer Stages",
                "headers": [
                    "Date", "Stage", "Customer Count", "Revenue",
                    "Avg Order Value", "Repeat Rate",
                ],
            },
        ],
    },
    "campaign-performance": {
        "description": "Campaign ROI Tracker — campaign comparison, A/B test results, send-time analysis",
        "sheets": [
            {
                "name": "Campaigns",
                "headers": [
                    "Date", "Campaign Name", "Subject Line", "Channel",
                    "Audience", "Recipients", "Opens", "Open Rate",
                    "Clicks", "Click Rate", "CTR", "Revenue",
                    "Revenue Per Recipient", "Unsubscribes", "Bounces",
                ],
            },
            {
                "name": "A/B Tests",
                "headers": [
                    "Date", "Campaign", "Variant", "Subject Line",
                    "Recipients", "Open Rate", "Click Rate", "Winner",
                ],
            },
        ],
    },
    "revenue-attribution": {
        "description": "Revenue Attribution Dashboard — Klaviyo vs Shopify revenue reconciliation",
        "sheets": [
            {
                "name": "Klaviyo Revenue",
                "headers": [
                    "Date", "Source", "Campaign/Flow Name", "Channel",
                    "Attributed Revenue", "Orders", "AOV",
                ],
            },
            {
                "name": "Shopify Revenue",
                "headers": [
                    "Date", "Source", "Channel", "Orders",
                    "Gross Revenue", "Discounts", "Net Revenue", "AOV",
                ],
            },
            {
                "name": "Reconciliation",
                "headers": [
                    "Date", "Klaviyo Attributed", "Shopify Total",
                    "Attribution %", "Gap", "Notes",
                ],
            },
        ],
    },
}


class LookerDataPipeline:
    """Push marketing data to Google Sheets for Looker Studio."""

    def __init__(self):
        """Initialize with Google Sheets credentials."""
        load_dotenv()

        creds_path = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_PATH")
        if not creds_path:
            raise ValueError(
                "GOOGLE_SHEETS_CREDENTIALS_PATH environment variable not set. "
                "Set it to the path of your Google service account JSON file."
            )
        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"Credentials file not found: {creds_path}")

        credentials = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        self.gc = gspread.authorize(credentials)
        self.default_spreadsheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")

    def sync_klaviyo_metrics(
        self, sheet_name: str = "Klaviyo Metrics", spreadsheet_id: Optional[str] = None
    ) -> Dict:
        """
        Pull Klaviyo flow + campaign metrics and push to Google Sheets.

        Requires KLAVIYO_API_KEY environment variable.
        """
        api_key = os.environ.get("KLAVIYO_API_KEY")
        if not api_key:
            raise ValueError("KLAVIYO_API_KEY not set — required for Klaviyo sync")

        import requests

        headers = {
            "Authorization": f"Klaviyo-API-Key {api_key}",
            "accept": "application/json",
            "revision": "2024-10-15",
        }

        # Fetch campaigns
        campaigns_url = "https://a.klaviyo.com/api/campaigns/?filter=equals(messages.channel,'email')"
        resp = requests.get(campaigns_url, headers=headers, timeout=30)
        resp.raise_for_status()
        campaigns = resp.json().get("data", [])

        campaign_rows = []
        for c in campaigns[:50]:  # Limit for Sheets
            attrs = c.get("attributes", {})
            campaign_rows.append([
                attrs.get("created_at", "")[:10],
                attrs.get("name", ""),
                "email",
                attrs.get("audiences", {}).get("included", [{}])[0].get("id", "")
                if attrs.get("audiences", {}).get("included") else "",
                attrs.get("status", ""),
            ])

        # Fetch flows
        flows_url = "https://a.klaviyo.com/api/flows/"
        resp = requests.get(flows_url, headers=headers, timeout=30)
        resp.raise_for_status()
        flows = resp.json().get("data", [])

        flow_rows = []
        for f in flows[:50]:
            attrs = f.get("attributes", {})
            flow_rows.append([
                attrs.get("created", "")[:10],
                attrs.get("name", ""),
                attrs.get("status", ""),
                attrs.get("trigger_type", ""),
            ])

        # Write to Sheets
        sid = spreadsheet_id or self.default_spreadsheet_id
        if not sid:
            raise ValueError("No spreadsheet ID provided. Use --sheet-id or set GOOGLE_SHEETS_SPREADSHEET_ID")

        spreadsheet = self.gc.open_by_key(sid)

        # Campaigns sheet
        self._write_to_sheet(
            spreadsheet, "Campaigns",
            [["Date", "Campaign Name", "Channel", "Audience ID", "Status"]] + campaign_rows,
        )

        # Flows sheet
        self._write_to_sheet(
            spreadsheet, "Flows",
            [["Date", "Flow Name", "Status", "Trigger Type"]] + flow_rows,
        )

        return {
            "status": "success",
            "campaigns_synced": len(campaign_rows),
            "flows_synced": len(flow_rows),
            "spreadsheet_id": sid,
        }

    def sync_shopify_orders(
        self,
        sheet_name: str = "Shopify Orders",
        spreadsheet_id: Optional[str] = None,
        days: int = 30,
    ) -> Dict:
        """
        Pull Shopify order data and push to Google Sheets.

        Requires SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN.
        """
        store_url = os.environ.get("SHOPIFY_STORE_URL", "").rstrip("/")
        access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN")
        if not store_url or not access_token:
            raise ValueError(
                "SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN required for Shopify sync"
            )

        import requests

        api_version = os.environ.get("SHOPIFY_API_VERSION", "2024-10")
        base_url = f"{store_url}/admin/api/{api_version}"
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        }

        created_at_min = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        url = f"{base_url}/orders.json"
        params = {
            "status": "any",
            "created_at_min": created_at_min,
            "limit": 250,
        }

        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        orders = resp.json().get("orders", [])

        order_rows = []
        for o in orders:
            order_rows.append([
                o.get("created_at", "")[:10],
                o.get("name", ""),
                o.get("email", ""),
                o.get("financial_status", ""),
                o.get("fulfillment_status", "") or "unfulfilled",
                float(o.get("total_price", 0)),
                float(o.get("total_discounts", 0)),
                float(o.get("subtotal_price", 0)),
                len(o.get("line_items", [])),
                o.get("source_name", ""),
                "Yes" if o.get("cancelled_at") else "No",
            ])

        sid = spreadsheet_id or self.default_spreadsheet_id
        if not sid:
            raise ValueError("No spreadsheet ID. Use --sheet-id or set GOOGLE_SHEETS_SPREADSHEET_ID")

        spreadsheet = self.gc.open_by_key(sid)
        self._write_to_sheet(
            spreadsheet, sheet_name,
            [[
                "Date", "Order", "Email", "Financial Status",
                "Fulfillment", "Total Price", "Discounts",
                "Subtotal", "Items", "Source", "Cancelled",
            ]] + order_rows,
        )

        return {
            "status": "success",
            "orders_synced": len(order_rows),
            "spreadsheet_id": sid,
            "period": f"Last {days} days",
        }

    def sync_ga4_summary(
        self,
        sheet_name: str = "GA4 Summary",
        spreadsheet_id: Optional[str] = None,
        days: int = 30,
    ) -> Dict:
        """
        Pull GA4 report data and push to Google Sheets.

        Requires GOOGLE_ANALYTICS_PROPERTY_ID and GOOGLE_APPLICATION_CREDENTIALS.
        """
        property_id = os.environ.get("GOOGLE_ANALYTICS_PROPERTY_ID")
        ga_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not property_id or not ga_creds:
            raise ValueError(
                "GOOGLE_ANALYTICS_PROPERTY_ID and GOOGLE_APPLICATION_CREDENTIALS "
                "required for GA4 sync"
            )

        try:
            from google.analytics.data_v1beta import BetaAnalyticsDataClient
            from google.analytics.data_v1beta.types import (
                DateRange, Dimension, Metric, RunReportRequest,
            )
        except ImportError:
            raise ImportError(
                "google-analytics-data package required for GA4 sync. "
                "Install with: pip install google-analytics-data"
            )

        ga_client = BetaAnalyticsDataClient()
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="yesterday")],
            metrics=[
                Metric(name="sessions"),
                Metric(name="activeUsers"),
                Metric(name="bounceRate"),
                Metric(name="conversions"),
            ],
            dimensions=[Dimension(name="date")],
            limit=days,
        )

        response = ga_client.run_report(request)

        rows = [["Date", "Sessions", "Active Users", "Bounce Rate", "Conversions"]]
        for row in response.rows:
            date_val = row.dimension_values[0].value
            rows.append([
                f"{date_val[:4]}-{date_val[4:6]}-{date_val[6:8]}",
                row.metric_values[0].value,
                row.metric_values[1].value,
                row.metric_values[2].value,
                row.metric_values[3].value,
            ])

        sid = spreadsheet_id or self.default_spreadsheet_id
        if not sid:
            raise ValueError("No spreadsheet ID. Use --sheet-id or set GOOGLE_SHEETS_SPREADSHEET_ID")

        spreadsheet = self.gc.open_by_key(sid)
        self._write_to_sheet(spreadsheet, sheet_name, rows)

        return {
            "status": "success",
            "rows_synced": len(rows) - 1,
            "spreadsheet_id": sid,
            "period": f"Last {days} days",
        }

    def create_dashboard_sheet(self, template: str) -> Dict:
        """
        Create a pre-formatted Google Sheet for a dashboard template.

        Args:
            template: Template name (crm-dashboard, lifecycle, campaign-performance, revenue-attribution)
        """
        if template not in TEMPLATES:
            raise ValueError(
                f"Unknown template: {template}. "
                f"Available: {', '.join(TEMPLATES.keys())}"
            )

        tmpl = TEMPLATES[template]
        title = f"Klaviyo Pack — {template.replace('-', ' ').title()} ({datetime.now():%Y-%m-%d})"

        spreadsheet = self.gc.create(title)

        # Create sheets from template
        for i, sheet_def in enumerate(tmpl["sheets"]):
            if i == 0:
                # Rename default sheet
                worksheet = spreadsheet.sheet1
                worksheet.update_title(sheet_def["name"])
            else:
                worksheet = spreadsheet.add_worksheet(
                    title=sheet_def["name"],
                    rows=1000,
                    cols=len(sheet_def["headers"]),
                )
            worksheet.update([sheet_def["headers"]], value_input_option="RAW")

            # Bold headers
            worksheet.format("1:1", {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.95},
            })

        return {
            "status": "success",
            "spreadsheet_id": spreadsheet.id,
            "spreadsheet_url": spreadsheet.url,
            "template": template,
            "description": tmpl["description"],
            "sheets_created": [s["name"] for s in tmpl["sheets"]],
            "next_steps": [
                "Share the sheet with your team",
                f"Run sync commands to populate: python data_pipeline.py --action sync-klaviyo --sheet-id {spreadsheet.id}",
                "Connect this Sheet as a data source in Looker Studio",
            ],
        }

    def list_templates(self) -> Dict:
        """List available dashboard templates."""
        return {
            "templates": {
                name: tmpl["description"]
                for name, tmpl in TEMPLATES.items()
            },
            "usage": "python data_pipeline.py --action create-sheet --template TEMPLATE_NAME",
        }

    def _write_to_sheet(
        self, spreadsheet, sheet_name: str, data: List[List]
    ) -> None:
        """Write data rows to a sheet, creating it if needed."""
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
            worksheet.clear()
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(
                title=sheet_name,
                rows=max(len(data), 100),
                cols=len(data[0]) if data else 10,
            )

        if data:
            worksheet.update(data, value_input_option="RAW")
            # Bold header row
            worksheet.format("1:1", {
                "textFormat": {"bold": True},
                "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.95},
            })


def main():
    parser = argparse.ArgumentParser(
        description="Push marketing data to Google Sheets for Looker Studio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available templates
  python data_pipeline.py --action list-templates

  # Create a new dashboard sheet
  python data_pipeline.py --action create-sheet --template crm-dashboard

  # Sync Klaviyo data to existing sheet
  python data_pipeline.py --action sync-klaviyo --sheet-id YOUR_SPREADSHEET_ID

  # Sync Shopify orders (last 30 days)
  python data_pipeline.py --action sync-shopify --sheet-id YOUR_SPREADSHEET_ID --days 30

  # Sync GA4 summary
  python data_pipeline.py --action sync-ga4 --sheet-id YOUR_SPREADSHEET_ID --days 30
        """,
    )

    parser.add_argument(
        "--action",
        required=True,
        choices=[
            "sync-klaviyo", "sync-shopify", "sync-ga4",
            "create-sheet", "list-templates",
        ],
        help="Action to perform",
    )
    parser.add_argument(
        "--sheet-id", help="Google Spreadsheet ID (from the Sheet URL)",
    )
    parser.add_argument(
        "--sheet-name", help="Target sheet/tab name within the spreadsheet",
    )
    parser.add_argument(
        "--template",
        choices=list(TEMPLATES.keys()),
        help="Dashboard template for create-sheet action",
    )
    parser.add_argument(
        "--days", type=int, default=30,
        help="Number of days of data to sync (default: 30)",
    )

    args = parser.parse_args()

    try:
        if args.action == "list-templates":
            # list-templates doesn't need credentials
            result = {
                "templates": {
                    name: tmpl["description"]
                    for name, tmpl in TEMPLATES.items()
                },
                "usage": "python data_pipeline.py --action create-sheet --template TEMPLATE_NAME",
            }
        else:
            pipeline = LookerDataPipeline()

            if args.action == "sync-klaviyo":
                result = pipeline.sync_klaviyo_metrics(
                    sheet_name=args.sheet_name or "Klaviyo Metrics",
                    spreadsheet_id=args.sheet_id,
                )
            elif args.action == "sync-shopify":
                result = pipeline.sync_shopify_orders(
                    sheet_name=args.sheet_name or "Shopify Orders",
                    spreadsheet_id=args.sheet_id,
                    days=args.days,
                )
            elif args.action == "sync-ga4":
                result = pipeline.sync_ga4_summary(
                    sheet_name=args.sheet_name or "GA4 Summary",
                    spreadsheet_id=args.sheet_id,
                    days=args.days,
                )
            elif args.action == "create-sheet":
                if not args.template:
                    print(
                        "Error: --template required for create-sheet action",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                result = pipeline.create_dashboard_sheet(template=args.template)
            else:
                print(f"Error: Unknown action: {args.action}", file=sys.stderr)
                sys.exit(1)

        print(json.dumps(result, indent=2))

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("Error: Pipeline operation failed. Check credentials and spreadsheet ID.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
