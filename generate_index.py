#!/usr/bin/env python3
"""
generate_index.py
 
Reads services_status.json and renders index.html from the
index.html.mustache template. All three files live in the same
directory.
 
Requirements:
    pip install pystache
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pystache

BASE_DIR = Path(__file__).resolve().parent
JSON_PATH = BASE_DIR / "services_status.json"
TEMPLATE_PATH = BASE_DIR / "index_template.html"
OUTPUT_PATH = BASE_DIR / "index.html"

PAGE_TITLE = "OEG Services Status"


def load_services(json_path: Path) -> list[dict]:
    with json_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def format_timestamp(timestamp_ms: int) -> str:
    """Convert a millisecond epoch timestamp to a readable UTC date/time."""
    dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


def build_context(services: list[dict]) -> dict:
    sorted_services = sorted(services, key=lambda s: s["name"].lower())
    enriched_services = []
    for service in sorted_services:
        status_code = service["status_http_code"]
        enriched_services.append(
            {
                "name": service["name"],
                "service_url": service["service_url"],
                "status_http_code": status_code,
                "is_ok": 200 <= status_code < 300,
                "formatted_timestamp": format_timestamp(service["timestamp"]),
            }
        )

    return {
        "web_title": PAGE_TITLE,
        "page_title": PAGE_TITLE,
        "services": enriched_services,
    }


def render(context: dict, template_path: Path) -> str:
    with template_path.open("r", encoding="utf-8") as f:
        template_content = f.read()
    renderer = pystache.Renderer()
    return renderer.render(template_content, context)


def main() -> None:
    if not JSON_PATH.exists():
        print(f"Error: {JSON_PATH} not found", file=sys.stderr)
        sys.exit(1)

    if not TEMPLATE_PATH.exists():
        print(f"Error: {TEMPLATE_PATH} not found", file=sys.stderr)
        sys.exit(1)

    services = load_services(JSON_PATH)
    context = build_context(services)
    html = render(context, TEMPLATE_PATH)

    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH} from {len(services)} services.")

if __name__ == "__main__":
    main()