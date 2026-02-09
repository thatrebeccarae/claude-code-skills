#!/usr/bin/env python3
"""
Shopify Admin API Client

Read-only wrapper for the Shopify Admin REST API. Fetches orders, products,
customers, inventory, and store metadata for analytics and auditing.

Usage:
    python shopify_client.py --resource orders --days 30
    python shopify_client.py --resource products --status active
    python shopify_client.py --resource customers --days 90 --limit 50
    python shopify_client.py --resource shop
    python shopify_client.py --resource order-count --status any
    python shopify_client.py --resource inventory --location-id 12345

Environment Variables:
    SHOPIFY_STORE_URL: Your myshopify.com URL (required)
    SHOPIFY_ACCESS_TOKEN: Admin API access token (required)
    SHOPIFY_API_VERSION: API version (default: 2024-10)
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse, parse_qs

try:
    import requests
    from dotenv import load_dotenv
except ImportError as e:
    print("Error: Required packages not installed.", file=sys.stderr)
    print("Install with: pip install requests python-dotenv", file=sys.stderr)
    sys.exit(1)


def _safe_output_path(path: str) -> str:
    """Validate output path does not escape working directory."""
    resolved = os.path.realpath(path)
    cwd = os.path.realpath(os.getcwd())
    if not resolved.startswith(cwd + os.sep) and resolved != cwd:
        raise ValueError(f"Output path must be within working directory: {cwd}")
    return resolved


class ShopifyAnalyticsClient:
    """Read-only client for Shopify Admin REST API."""

    RATE_LIMIT_DELAY = 0.5  # 2 requests per second

    def __init__(self):
        """Initialize the client with credentials from environment."""
        load_dotenv()

        self.store_url = os.environ.get("SHOPIFY_STORE_URL", "").rstrip("/")
        if not self.store_url:
            raise ValueError(
                "SHOPIFY_STORE_URL environment variable not set. "
                "Set it to your myshopify.com URL (e.g., https://my-store.myshopify.com)"
            )

        self.access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN")
        if not self.access_token:
            raise ValueError(
                "SHOPIFY_ACCESS_TOKEN environment variable not set. "
                "Create an Admin API access token in Shopify: "
                "Settings > Apps > Develop apps"
            )

        self.api_version = os.environ.get("SHOPIFY_API_VERSION", "2024-10")
        self.base_url = f"{self.store_url}/admin/api/{self.api_version}"
        self.session = requests.Session()
        self.session.headers.update({
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        })
        self._last_request_time = 0

    def get_shop_info(self) -> Dict:
        """Get store metadata, plan, and currency info."""
        return self._request("GET", "/shop.json")

    def get_orders(
        self,
        status: str = "any",
        created_at_min: Optional[str] = None,
        created_at_max: Optional[str] = None,
        limit: int = 250,
        financial_status: Optional[str] = None,
    ) -> List[Dict]:
        """
        Fetch orders with financials.

        Args:
            status: Order status filter (open, closed, cancelled, any)
            created_at_min: ISO 8601 date string for earliest order
            created_at_max: ISO 8601 date string for latest order
            limit: Maximum orders to return (paginated in batches of 250)
            financial_status: Filter by financial status (paid, pending, refunded, etc.)
        """
        params = {"status": status, "limit": min(limit, 250)}
        if created_at_min:
            params["created_at_min"] = created_at_min
        if created_at_max:
            params["created_at_max"] = created_at_max
        if financial_status:
            params["financial_status"] = financial_status

        return self._paginate("/orders.json", "orders", params, max_items=limit)

    def get_products(self, status: Optional[str] = None, limit: int = 250) -> List[Dict]:
        """
        Fetch products with variants and inventory.

        Args:
            status: Product status filter (active, draft, archived)
            limit: Maximum products to return
        """
        params = {"limit": min(limit, 250)}
        if status:
            params["status"] = status

        return self._paginate("/products.json", "products", params, max_items=limit)

    def get_customers(
        self, created_at_min: Optional[str] = None, limit: int = 250
    ) -> List[Dict]:
        """
        Fetch customers with order history.

        Args:
            created_at_min: ISO 8601 date for earliest customer creation
            limit: Maximum customers to return
        """
        params = {"limit": min(limit, 250)}
        if created_at_min:
            params["created_at_min"] = created_at_min

        return self._paginate("/customers.json", "customers", params, max_items=limit)

    def get_order_count(self, status: str = "any") -> int:
        """Get total order count by status."""
        data = self._request("GET", "/orders/count.json", params={"status": status})
        return data.get("count", 0)

    def get_customer_count(self) -> int:
        """Get total customer count."""
        data = self._request("GET", "/customers/count.json")
        return data.get("count", 0)

    def get_inventory_levels(self, location_id: str, limit: int = 250) -> List[Dict]:
        """
        Fetch inventory levels by location.

        Args:
            location_id: Shopify location ID
            limit: Maximum items to return
        """
        params = {"location_ids": location_id, "limit": min(limit, 250)}
        return self._paginate(
            "/inventory_levels.json", "inventory_levels", params, max_items=limit
        )

    def _paginate(
        self,
        endpoint: str,
        resource_key: str,
        params: Dict,
        max_items: int = 250,
    ) -> List[Dict]:
        """
        Handle Link-header cursor pagination.

        Shopify uses rel="next" Link headers for pagination.
        """
        all_items = []
        url = f"{self.base_url}{endpoint}"

        while url and len(all_items) < max_items:
            response = self._raw_request("GET", url, params=params)
            data = response.json()
            items = data.get(resource_key, [])
            all_items.extend(items)

            # Clear params after first request (pagination URL includes them)
            params = {}

            # Check for next page via Link header
            url = None
            link_header = response.headers.get("Link", "")
            if 'rel="next"' in link_header:
                for part in link_header.split(","):
                    if 'rel="next"' in part:
                        url = part.split("<")[1].split(">")[0]
                        break

        return all_items[:max_items]

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a rate-limited API request and return JSON data."""
        url = f"{self.base_url}{endpoint}"
        response = self._raw_request(method, url, params=params)
        return response.json()

    def _raw_request(
        self, method: str, url: str, params: Optional[Dict] = None
    ) -> requests.Response:
        """Make a rate-limited HTTP request with retry logic."""
        # Rate limiting: 2 requests per second
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)

        retries = 3
        for attempt in range(retries):
            try:
                self._last_request_time = time.time()
                response = self.session.request(method, url, params=params, timeout=30)

                if response.status_code == 429:
                    # Rate limited — wait and retry
                    retry_after = float(response.headers.get("Retry-After", 2))
                    print(
                        f"Rate limited. Waiting {retry_after}s...", file=sys.stderr
                    )
                    time.sleep(retry_after)
                    continue

                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    raise RuntimeError(
                        f"Shopify API request failed after {retries} attempts. Check store URL and access token."
                    )
                time.sleep(2 ** attempt)

        raise RuntimeError("Shopify API request failed: max retries exceeded")


def format_output(data, fmt: str) -> str:
    """Format data as JSON, table, or CSV."""
    if fmt == "json":
        return json.dumps(data, indent=2, default=str)
    elif fmt == "csv":
        if isinstance(data, list) and data:
            import csv
            import io
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            return output.getvalue()
        return json.dumps(data, indent=2, default=str)
    else:  # table
        if isinstance(data, list) and data:
            headers = list(data[0].keys())[:8]  # Limit columns for readability
            col_widths = {h: max(len(h), 12) for h in headers}
            lines = [" | ".join(h.ljust(col_widths[h]) for h in headers)]
            lines.append("-" * len(lines[0]))
            for row in data[:50]:  # Limit rows for readability
                values = []
                for h in headers:
                    val = str(row.get(h, ""))[:col_widths[h]]
                    values.append(val.ljust(col_widths[h]))
                lines.append(" | ".join(values))
            return "\n".join(lines)
        elif isinstance(data, dict):
            lines = []
            for k, v in data.items():
                if isinstance(v, dict):
                    lines.append(f"\n{k}:")
                    for k2, v2 in v.items():
                        lines.append(f"  {k2}: {v2}")
                else:
                    lines.append(f"{k}: {v}")
            return "\n".join(lines)
        return json.dumps(data, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch data from Shopify Admin API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get store info
  python shopify_client.py --resource shop

  # List recent orders
  python shopify_client.py --resource orders --days 30

  # Active products
  python shopify_client.py --resource products --status active

  # Customer count
  python shopify_client.py --resource customer-count

  # Export orders as CSV
  python shopify_client.py --resource orders --days 7 --format csv --output orders.csv
        """,
    )

    parser.add_argument(
        "--resource",
        required=True,
        choices=[
            "orders", "products", "customers", "shop",
            "inventory", "order-count", "customer-count",
        ],
        help="Shopify resource to fetch",
    )
    parser.add_argument(
        "--status", help="Status filter (e.g., active, open, any)"
    )
    parser.add_argument(
        "--days", type=int, help="Fetch data from the last N days"
    )
    parser.add_argument(
        "--limit", type=int, default=250, help="Maximum items to return (default: 250)"
    )
    parser.add_argument(
        "--location-id", help="Location ID for inventory queries"
    )
    parser.add_argument(
        "--format",
        choices=["json", "table", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--output", help="Output file path (default: stdout)"
    )

    args = parser.parse_args()

    try:
        client = ShopifyAnalyticsClient()

        # Calculate date range
        created_at_min = None
        if args.days:
            created_at_min = (
                datetime.utcnow() - timedelta(days=args.days)
            ).isoformat() + "Z"

        # Fetch data
        if args.resource == "shop":
            data = client.get_shop_info()
        elif args.resource == "orders":
            data = client.get_orders(
                status=args.status or "any",
                created_at_min=created_at_min,
                limit=args.limit,
            )
        elif args.resource == "products":
            data = client.get_products(status=args.status, limit=args.limit)
        elif args.resource == "customers":
            data = client.get_customers(
                created_at_min=created_at_min, limit=args.limit
            )
        elif args.resource == "order-count":
            data = {"count": client.get_order_count(status=args.status or "any")}
        elif args.resource == "customer-count":
            data = {"count": client.get_customer_count()}
        elif args.resource == "inventory":
            if not args.location_id:
                print("Error: --location-id required for inventory queries", file=sys.stderr)
                sys.exit(1)
            data = client.get_inventory_levels(args.location_id, limit=args.limit)
        else:
            print(f"Error: Unknown resource: {args.resource}", file=sys.stderr)
            sys.exit(1)

        # Format output
        output = format_output(data, args.format)

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
        print("Error: Failed to fetch Shopify data. Check store URL and access token.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
