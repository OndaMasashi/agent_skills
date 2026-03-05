#!/usr/bin/env python3
"""
Google Slides API operations.
Lightweight alternative to the full Google Workspace MCP server.
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
import urllib.parse
from typing import Optional
import os
from datetime import datetime

# 使用状況ロギング定数
LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../usage.log"))

def log_usage(skill_name):
    """スキルの使用をログに記録する（低負荷な追記方式）"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{timestamp}, {skill_name}\n")
    except Exception:
        pass

# スクリプト実行時にログを記録
log_usage("google-slides")

from auth import get_valid_access_token

SLIDES_API_BASE = "https://slides.googleapis.com/v1"
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"

# MIME type for Google Slides
SLIDES_MIME_TYPE = "application/vnd.google-apps.presentation"


def extract_presentation_id(presentation_id_or_url: str) -> str:
    """
    Extract presentation ID from a URL or return the ID as-is.

    Handles URLs like:
    - https://docs.google.com/presentation/d/PRESENTATION_ID/edit
    - https://docs.google.com/presentation/d/PRESENTATION_ID
    """
    url_pattern = r'docs\.google\.com/presentation/d/([a-zA-Z0-9_-]+)'
    match = re.search(url_pattern, presentation_id_or_url)
    if match:
        return match.group(1)
    return presentation_id_or_url


def api_request(base_url: str, endpoint: str, params: Optional[dict] = None) -> dict:
    """Make an authenticated GET request to a Google API."""
    token = get_valid_access_token()
    if not token:
        return {"error": "Failed to get access token"}

    url = f"{base_url}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        req = urllib.request.Request(url, headers=headers, method="GET")
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        return {"error": f"HTTP {e.code}: {error_body}"}
    except urllib.error.URLError as e:
        return {"error": f"Request failed: {e.reason}"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}


def get_text(presentation_id: str) -> dict:
    """
    Extract all text content from a presentation.

    Args:
        presentation_id: Presentation ID or URL
    """
    pres_id = extract_presentation_id(presentation_id)

    result = api_request(SLIDES_API_BASE, f"presentations/{pres_id}")

    if "error" in result:
        return result

    title = result.get("title", "Untitled")
    slides = result.get("slides", [])

    text_content = f"Presentation Title: {title}\n\n"

    for i, slide in enumerate(slides, 1):
        slide_texts = []

        for element in slide.get("pageElements", []):
            # Extract text from shapes/text boxes
            shape = element.get("shape")
            if shape:
                text_content_obj = shape.get("text")
                if text_content_obj:
                    for text_element in text_content_obj.get("textElements", []):
                        text_run = text_element.get("textRun")
                        if text_run:
                            content = text_run.get("content", "").strip()
                            if content:
                                slide_texts.append(content)

            # Extract text from tables
            table = element.get("table")
            if table:
                for row in table.get("tableRows", []):
                    row_texts = []
                    for cell in row.get("tableCells", []):
                        cell_text_parts = []
                        text_obj = cell.get("text")
                        if text_obj:
                            for text_element in text_obj.get("textElements", []):
                                text_run = text_element.get("textRun")
                                if text_run:
                                    content = text_run.get("content", "").strip()
                                    if content:
                                        cell_text_parts.append(content)
                        row_texts.append(" ".join(cell_text_parts))
                    slide_texts.append(" | ".join(row_texts))

        text_content += f"--- Slide {i} ---\n"
        if slide_texts:
            text_content += "\n".join(slide_texts) + "\n"
        else:
            text_content += "(No text content)\n"
        text_content += "\n"

    return {
        "presentationId": pres_id,
        "title": title,
        "slideCount": len(slides),
        "text": text_content.strip()
    }


def find_presentations(query: str, page_size: int = 10, page_token: Optional[str] = None) -> dict:
    """
    Find presentations by search query.

    Args:
        query: Search query (searches name and content)
        page_size: Number of results to return
        page_token: Pagination token
    """
    search_query = f"mimeType='{SLIDES_MIME_TYPE}' and (name contains '{query}' or fullText contains '{query}')"

    params = {
        "q": search_query,
        "pageSize": str(page_size),
        "fields": "nextPageToken, files(id, name, createdTime, modifiedTime, webViewLink)"
    }

    if page_token:
        params["pageToken"] = page_token

    result = api_request(DRIVE_API_BASE, "files", params)

    if "error" in result:
        return result

    return {
        "presentations": result.get("files", []),
        "nextPageToken": result.get("nextPageToken")
    }


def get_metadata(presentation_id: str) -> dict:
    """
    Get presentation metadata.

    Args:
        presentation_id: Presentation ID or URL
    """
    pres_id = extract_presentation_id(presentation_id)

    result = api_request(SLIDES_API_BASE, f"presentations/{pres_id}")

    if "error" in result:
        return result

    slides = result.get("slides", [])
    page_size = result.get("pageSize", {})
    masters = result.get("masters", [])
    layouts = result.get("layouts", [])

    return {
        "presentationId": result.get("presentationId"),
        "title": result.get("title"),
        "slideCount": len(slides),
        "pageSize": {
            "width": page_size.get("width", {}),
            "height": page_size.get("height", {})
        },
        "hasMasters": len(masters) > 0,
        "hasLayouts": len(layouts) > 0
    }


def main():
    parser = argparse.ArgumentParser(description="Google Slides API operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get-text
    get_text_parser = subparsers.add_parser("get-text", help="Extract text from a presentation")
    get_text_parser.add_argument("presentation_id", help="Presentation ID or URL")

    # find
    find_parser = subparsers.add_parser("find", help="Find presentations by search query")
    find_parser.add_argument("query", help="Search query")
    find_parser.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    find_parser.add_argument("--page-token", help="Pagination token")

    # get-metadata
    get_metadata_parser = subparsers.add_parser("get-metadata", help="Get presentation metadata")
    get_metadata_parser.add_argument("presentation_id", help="Presentation ID or URL")

    args = parser.parse_args()

    if args.command == "get-text":
        result = get_text(args.presentation_id)
    elif args.command == "find":
        result = find_presentations(args.query, args.limit, getattr(args, 'page_token', None))
    elif args.command == "get-metadata":
        result = get_metadata(args.presentation_id)
    else:
        result = {"error": f"Unknown command: {args.command}"}

    print(json.dumps(result, indent=2))

    if isinstance(result, dict) and "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
