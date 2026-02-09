#!/usr/bin/env python3
"""
Klaviyo Developer API Client

Read-write SDK wrapper for Klaviyo event tracking, profile management,
bulk imports, catalog sync, and data export.

Usage:
    python klaviyo_client.py --action track-event --email user@example.com --event "Placed Order" --properties '{"value": 99.99}'
    python klaviyo_client.py --action upsert-profile --email user@example.com --properties '{"first_name": "Jane"}'
    python klaviyo_client.py --action bulk-import --file contacts.csv --list-id LIST_ID
    python klaviyo_client.py --action catalog-items --format table
    python klaviyo_client.py --action export-profiles --max-pages 5 --output profiles.csv

Environment Variables:
    KLAVIYO_API_KEY: Klaviyo private API key (required, starts with "pk_")
"""

import os
import sys
import json
import csv
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


def _safe_input_file(path: str) -> str:
    """Validate input file path: must be .csv and exist."""
    resolved = os.path.realpath(path)
    if not os.path.exists(resolved):
        raise FileNotFoundError(f"File not found: {path}")
    if not resolved.lower().endswith(".csv"):
        raise ValueError("Input file must be a .csv file")
    return resolved


class KlaviyoDevClient:
    """Read-write client for Klaviyo developer operations."""

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

    def track_event(
        self,
        event_name: str,
        email: str,
        properties: Optional[Dict] = None,
        unique_id: Optional[str] = None,
    ) -> Dict:
        """
        Track a custom event.

        Args:
            event_name: Name of the event (e.g., "Placed Order")
            email: Profile email address
            properties: Event properties dict
            unique_id: Idempotency key to prevent duplicates

        Returns:
            API response dictionary
        """
        body = self._build_event_body(event_name, email, properties, unique_id)

        try:
            response = self.client.Events.create_event(body)
            return {"status": "success", "event": event_name, "email": email}
        except Exception:
            raise RuntimeError("Failed to track event. Check your API key and event data.")

    def upsert_profile(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        properties: Optional[Dict] = None,
    ) -> Dict:
        """
        Create or update a profile.

        Args:
            email: Profile email address
            phone: Profile phone number (with country code)
            properties: Custom profile properties

        Returns:
            API response with profile data
        """
        body = self._build_profile_body(email, phone, properties)

        try:
            response = self.client.Profiles.create_profile(body)
            return self._parse_jsonapi_response(response)
        except Exception:
            raise RuntimeError("Failed to upsert profile. Check your API key and profile data.")

    def bulk_import(
        self, profiles: List[Dict], list_id: Optional[str] = None
    ) -> Dict:
        """
        Submit a bulk profile import job (max 10,000 profiles per job).

        Args:
            profiles: List of profile dicts with email, phone, and/or properties
            list_id: Optional list ID to add profiles to

        Returns:
            Dictionary with job ID and status
        """
        if len(profiles) > 10000:
            raise ValueError("Bulk import limited to 10,000 profiles per job")

        profile_data = []
        for p in profiles:
            attrs = {}
            if p.get("email"):
                attrs["email"] = p["email"]
            if p.get("phone"):
                attrs["phone_number"] = p["phone"]
            if p.get("first_name"):
                attrs["first_name"] = p["first_name"]
            if p.get("last_name"):
                attrs["last_name"] = p["last_name"]

            # Custom properties
            custom_props = {
                k: v
                for k, v in p.items()
                if k not in ("email", "phone", "first_name", "last_name")
            }
            if custom_props:
                attrs["properties"] = custom_props

            profile_data.append({"type": "profile", "attributes": attrs})

        body = {
            "data": {
                "type": "profile-bulk-import-job",
                "attributes": {"profiles": {"data": profile_data}},
            }
        }

        if list_id:
            body["data"]["relationships"] = {
                "lists": {"data": [{"type": "list", "id": list_id}]}
            }

        try:
            response = self.client.Profiles.spawn_bulk_profile_import_job(body)
            result = self._parse_jsonapi_response(response)
            return {
                "status": "submitted",
                "job_id": result.get("id") if isinstance(result, dict) else None,
                "profiles_submitted": len(profiles),
            }
        except Exception:
            raise RuntimeError("Failed to submit bulk import. Check your API key and profile data.")

    def get_import_job_status(self, job_id: str) -> Dict:
        """
        Check status of a bulk import job.

        Args:
            job_id: The import job ID

        Returns:
            Dictionary with job status and progress
        """
        try:
            response = self.client.Profiles.get_bulk_profile_import_job(job_id)
            return self._parse_jsonapi_response(response)
        except Exception:
            raise RuntimeError("Failed to get import job status. Check job ID and API key.")

    def get_catalog_items(self, filter_str: Optional[str] = None) -> List[Dict]:
        """
        List catalog items.

        Args:
            filter_str: Optional filter expression

        Returns:
            List of catalog item dictionaries
        """
        try:
            kwargs = {}
            if filter_str:
                kwargs["filter"] = filter_str

            response = self.client.Catalogs.get_catalog_items(**kwargs)
            return self._parse_jsonapi_response(response)
        except Exception:
            raise RuntimeError("Failed to fetch catalog items. Check your API key and catalog scopes.")

    def create_catalog_item(self, item_data: Dict) -> Dict:
        """
        Create a catalog item.

        Args:
            item_data: Dictionary with title, description, url, image_url, price, etc.

        Returns:
            Created catalog item data
        """
        body = {
            "data": {
                "type": "catalog-item",
                "attributes": {
                    "external_id": item_data.get("external_id", item_data.get("id")),
                    "title": item_data.get("title"),
                    "description": item_data.get("description", ""),
                    "url": item_data.get("url", ""),
                    "image_full_url": item_data.get("image_url", ""),
                    "custom_metadata": {
                        k: v
                        for k, v in item_data.items()
                        if k
                        not in (
                            "external_id",
                            "id",
                            "title",
                            "description",
                            "url",
                            "image_url",
                            "price",
                        )
                    },
                },
            }
        }

        if item_data.get("price"):
            body["data"]["attributes"]["price"] = float(item_data["price"])

        try:
            response = self.client.Catalogs.create_catalog_item(body)
            return self._parse_jsonapi_response(response)
        except Exception:
            raise RuntimeError("Failed to create catalog item. Check your API key and item data.")

    def export_profiles(
        self, page_size: int = 100, max_pages: Optional[int] = None
    ) -> List[Dict]:
        """
        Export profiles with cursor-based pagination.

        Args:
            page_size: Number of profiles per page (max 100)
            max_pages: Maximum pages to fetch (None for all)

        Returns:
            List of profile dictionaries
        """
        profiles = []
        cursor = None
        page_count = 0

        while True:
            try:
                kwargs = {"page_size": min(page_size, 100)}
                if cursor:
                    kwargs["page_cursor"] = cursor

                response = self.client.Profiles.get_profiles(**kwargs)

                if hasattr(response, "to_dict"):
                    response = response.to_dict()
                elif isinstance(response, str):
                    response = json.loads(response)

                data = response.get("data", [])
                for item in data:
                    flat = {"id": item.get("id")}
                    attrs = item.get("attributes", {})
                    flat.update(attrs)
                    profiles.append(flat)

                page_count += 1
                print(
                    f"Page {page_count}: fetched {len(data)} profiles "
                    f"(total: {len(profiles)})",
                    file=sys.stderr,
                )

                # Check pagination
                next_link = response.get("links", {}).get("next")
                if not next_link:
                    break

                if max_pages and page_count >= max_pages:
                    print(
                        f"Reached max pages limit ({max_pages})", file=sys.stderr
                    )
                    break

                # Extract cursor from next link
                from urllib.parse import urlparse, parse_qs

                parsed = urlparse(next_link)
                cursor = parse_qs(parsed.query).get("page[cursor]", [None])[0]

                if not cursor:
                    break

            except Exception:
                raise RuntimeError(
                    "Failed to export profiles. Check your API key and profile scopes."
                )

        return profiles

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
            raise RuntimeError("Failed to fetch metrics. Check your API key and metrics scopes.")

    def _parse_jsonapi_response(self, response) -> List[Dict]:
        """Flatten JSON:API envelope into simple dictionaries."""
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

    def _build_event_body(
        self,
        event_name: str,
        email: str,
        properties: Optional[Dict] = None,
        unique_id: Optional[str] = None,
    ) -> Dict:
        """Build JSON:API event body."""
        body = {
            "data": {
                "type": "event",
                "attributes": {
                    "metric": {
                        "data": {
                            "type": "metric",
                            "attributes": {"name": event_name},
                        }
                    },
                    "profile": {
                        "data": {
                            "type": "profile",
                            "attributes": {"email": email},
                        }
                    },
                    "properties": properties or {},
                },
            }
        }

        if unique_id:
            body["data"]["attributes"]["unique_id"] = unique_id

        return body

    def _build_profile_body(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        properties: Optional[Dict] = None,
    ) -> Dict:
        """Build JSON:API profile body."""
        attrs = {}
        if email:
            attrs["email"] = email
        if phone:
            attrs["phone_number"] = phone

        if properties:
            # Separate standard fields from custom properties
            standard_fields = {
                "first_name",
                "last_name",
                "organization",
                "title",
                "image",
                "location",
            }
            for key in list(properties.keys()):
                if key in standard_fields:
                    attrs[key] = properties.pop(key)

            if properties:
                attrs["properties"] = properties

        return {"data": {"type": "profile", "attributes": attrs}}


def main():
    parser = argparse.ArgumentParser(
        description="Klaviyo developer operations client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Track a custom event
  python klaviyo_client.py --action track-event \\
      --email user@example.com --event "Placed Order" \\
      --properties '{"value": 99.99, "OrderId": "ORD-123"}'

  # Upsert a profile
  python klaviyo_client.py --action upsert-profile \\
      --email user@example.com \\
      --properties '{"first_name": "Jane", "loyalty_tier": "Gold"}'

  # Check import job status
  python klaviyo_client.py --action import-status --job-id JOB_ID

  # List catalog items
  python klaviyo_client.py --action catalog-items --format table

  # Export profiles to CSV
  python klaviyo_client.py --action export-profiles \\
      --max-pages 10 --format csv --output profiles.csv

  # List available metrics
  python klaviyo_client.py --action metrics
        """,
    )

    parser.add_argument(
        "--action",
        required=True,
        choices=[
            "track-event",
            "upsert-profile",
            "bulk-import",
            "import-status",
            "catalog-items",
            "create-catalog-item",
            "export-profiles",
            "metrics",
        ],
        help="Action to perform",
    )
    parser.add_argument("--email", help="Profile email address")
    parser.add_argument("--event", help="Event name (for track-event)")
    parser.add_argument(
        "--properties", help="JSON properties string (for events or profiles)"
    )
    parser.add_argument("--file", help="CSV file path (for bulk-import)")
    parser.add_argument("--list-id", help="List ID (for bulk-import)")
    parser.add_argument("--job-id", help="Import job ID (for import-status)")
    parser.add_argument(
        "--max-pages",
        type=int,
        help="Max pages to fetch (for export-profiles)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "table", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument("--output", help="Output file path (default: stdout)")

    args = parser.parse_args()

    try:
        client = KlaviyoDevClient()

        # Parse properties
        properties = None
        if args.properties:
            properties = json.loads(args.properties)

        # Execute action
        if args.action == "track-event":
            if not args.email:
                parser.error("--email is required for track-event")
            if not args.event:
                parser.error("--event is required for track-event")
            result = client.track_event(
                event_name=args.event,
                email=args.email,
                properties=properties,
            )

        elif args.action == "upsert-profile":
            if not args.email:
                parser.error("--email is required for upsert-profile")
            result = client.upsert_profile(
                email=args.email, properties=properties
            )

        elif args.action == "bulk-import":
            if not args.file:
                parser.error("--file is required for bulk-import")
            # Read CSV
            profiles = []
            safe_file = _safe_input_file(args.file)
            with open(safe_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    profiles.append(dict(row))
            result = client.bulk_import(profiles, list_id=args.list_id)

        elif args.action == "import-status":
            if not args.job_id:
                parser.error("--job-id is required for import-status")
            result = client.get_import_job_status(args.job_id)

        elif args.action == "catalog-items":
            result = client.get_catalog_items()

        elif args.action == "create-catalog-item":
            if not properties:
                parser.error(
                    "--properties is required for create-catalog-item (JSON with title, etc.)"
                )
            result = client.create_catalog_item(properties)

        elif args.action == "export-profiles":
            result = client.export_profiles(max_pages=args.max_pages)

        elif args.action == "metrics":
            result = client.get_metrics()

        # Format output
        if args.format == "csv" and isinstance(result, list):
            output = format_as_csv(result)
        elif args.format == "json":
            output = json.dumps(result, indent=2, default=str)
        else:
            output = json.dumps(result, indent=2, default=str)

        # Write output
        if args.output:
            safe_path = _safe_output_path(args.output)
            with open(safe_path, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Data saved to {args.output}", file=sys.stderr)
        else:
            print(output)

    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("Error: Operation failed. Check your API key and network connection.", file=sys.stderr)
        sys.exit(1)


def format_as_csv(data: List[Dict]) -> str:
    """Format list of dicts as CSV string."""
    if not data:
        return ""

    import io

    output = io.StringIO()
    # Collect all keys across all rows
    all_keys = []
    for row in data:
        for key in row.keys():
            if key not in all_keys:
                all_keys.append(key)

    writer = csv.DictWriter(output, fieldnames=all_keys, extrasaction="ignore")
    writer.writeheader()
    for row in data:
        # Stringify nested dicts/lists
        clean_row = {}
        for k, v in row.items():
            if isinstance(v, (dict, list)):
                clean_row[k] = json.dumps(v)
            else:
                clean_row[k] = v
        writer.writerow(clean_row)

    return output.getvalue()


if __name__ == "__main__":
    main()
