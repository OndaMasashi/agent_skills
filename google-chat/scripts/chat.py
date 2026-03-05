#!/usr/bin/env python3
"""
Google Chat API operations.
Lightweight alternative to the full Google Workspace MCP server.
"""

import argparse
import json
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
log_usage("google-chat")

from auth import get_valid_access_token

CHAT_API_BASE = "https://chat.googleapis.com/v1"


def api_request(method: str, endpoint: str, data: Optional[dict] = None,
                params: Optional[dict] = None) -> dict:
    """Make an authenticated request to the Google Chat API."""
    token = get_valid_access_token()
    if not token:
        return {"error": "Failed to get access token"}

    url = f"{CHAT_API_BASE}/{endpoint}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = json.dumps(data).encode('utf-8') if data else None

    try:
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=30) as response:
            response_data = response.read().decode('utf-8')
            if not response_data:
                return {"success": True}
            return json.loads(response_data)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        return {"error": f"HTTP {e.code}: {error_body}"}
    except urllib.error.URLError as e:
        return {"error": f"Request failed: {e.reason}"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response"}


def format_space(space: dict) -> dict:
    """Extract useful fields from a space."""
    return {
        "name": space.get("name"),
        "displayName": space.get("displayName"),
        "type": space.get("type"),
        "spaceType": space.get("spaceType"),
        "singleUserBotDm": space.get("singleUserBotDm", False),
        "threaded": space.get("threaded", False)
    }


def format_message(msg: dict) -> dict:
    """Extract useful fields from a message."""
    sender = msg.get("sender", {})
    return {
        "name": msg.get("name"),
        "text": msg.get("text"),
        "formattedText": msg.get("formattedText"),
        "sender": {
            "name": sender.get("name"),
            "displayName": sender.get("displayName"),
            "type": sender.get("type")
        },
        "createTime": msg.get("createTime"),
        "thread": msg.get("thread")
    }


def list_spaces() -> dict:
    """List all spaces the user is a member of."""
    result = api_request("GET", "spaces")

    if "error" in result:
        return result

    spaces = [format_space(s) for s in result.get("spaces", [])]
    return {"spaces": spaces}


def find_space(query: str) -> dict:
    """Find a space by name (client-side filtering)."""
    result = api_request("GET", "spaces")

    if "error" in result:
        return result

    query_lower = query.lower()
    matched = []
    for space in result.get("spaces", []):
        display_name = space.get("displayName", "")
        if query_lower in display_name.lower():
            matched.append(format_space(space))

    return {"spaces": matched}


def get_messages(space_name: str, limit: int = 25) -> dict:
    """Get messages from a space."""
    params = {
        "pageSize": str(limit)
    }

    result = api_request("GET", f"{space_name}/messages", params=params)

    if "error" in result:
        return result

    messages = [format_message(m) for m in result.get("messages", [])]
    return {
        "messages": messages,
        "nextPageToken": result.get("nextPageToken")
    }


def send_message(space_name: str, text: str) -> dict:
    """Send a message to a space."""
    result = api_request("POST", f"{space_name}/messages", data={"text": text})

    if "error" in result:
        return result

    return format_message(result)


def find_dm(email: str) -> dict:
    """Find or look up an existing DM space with a user."""
    # Use findDirectMessage to look up existing DM
    params = {"name": f"users/{email}"}
    result = api_request("GET", "spaces:findDirectMessage", params=params)

    if "error" in result:
        return result

    return {"space": format_space(result)}


def send_dm(email: str, text: str) -> dict:
    """Send a direct message to a user by email."""
    # First, find or create a DM space
    dm_result = find_dm(email)

    if "error" in dm_result:
        # If DM space doesn't exist, try to set one up
        setup_result = api_request("POST", "spaces:setup", data={
            "space": {"spaceType": "DIRECT_MESSAGE"},
            "memberships": [{"member": {"name": f"users/{email}", "type": "HUMAN"}}]
        })
        if "error" in setup_result:
            return setup_result
        space_name = setup_result.get("name")
    else:
        space_name = dm_result.get("space", {}).get("name")

    if not space_name:
        return {"error": "Could not find or create DM space"}

    # Send the message
    result = api_request("POST", f"{space_name}/messages", data={"text": text})

    if "error" in result:
        return result

    msg = format_message(result)
    msg["space"] = space_name
    return msg


def list_threads(space_name: str) -> dict:
    """List threads in a space."""
    params = {
        "pageSize": "50"
    }

    result = api_request("GET", f"{space_name}/messages", params=params)

    if "error" in result:
        return result

    # Group messages by thread
    threads = {}
    for msg in result.get("messages", []):
        thread = msg.get("thread", {})
        thread_name = thread.get("name", "")
        if thread_name not in threads:
            threads[thread_name] = {
                "threadName": thread_name,
                "messages": []
            }
        threads[thread_name]["messages"].append(format_message(msg))

    return {"threads": list(threads.values())}


def setup_space(display_name: str, members: list) -> dict:
    """Create a new space with members."""
    memberships = [
        {"member": {"name": f"users/{email}", "type": "HUMAN"}}
        for email in members
    ]

    result = api_request("POST", "spaces:setup", data={
        "space": {
            "displayName": display_name,
            "spaceType": "SPACE"
        },
        "memberships": memberships
    })

    if "error" in result:
        return result

    return format_space(result)


def main():
    parser = argparse.ArgumentParser(description="Google Chat API operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list-spaces
    subparsers.add_parser("list-spaces", help="List all spaces")

    # find-space
    find_space_parser = subparsers.add_parser("find-space", help="Find a space by name")
    find_space_parser.add_argument("query", help="Space name to search for")

    # get-messages
    get_msg_parser = subparsers.add_parser("get-messages", help="Get messages from a space")
    get_msg_parser.add_argument("space_name", help="Space name (e.g., spaces/AAAA123)")
    get_msg_parser.add_argument("--limit", type=int, default=25,
                                 help="Max messages to return (default: 25)")

    # send-message
    send_msg_parser = subparsers.add_parser("send-message", help="Send message to a space")
    send_msg_parser.add_argument("space_name", help="Space name (e.g., spaces/AAAA123)")
    send_msg_parser.add_argument("text", help="Message text")

    # send-dm
    send_dm_parser = subparsers.add_parser("send-dm", help="Send direct message to a user")
    send_dm_parser.add_argument("email", help="Recipient email address")
    send_dm_parser.add_argument("text", help="Message text")

    # find-dm
    find_dm_parser = subparsers.add_parser("find-dm", help="Find DM space with a user")
    find_dm_parser.add_argument("email", help="User email address")

    # list-threads
    list_threads_parser = subparsers.add_parser("list-threads", help="List threads in a space")
    list_threads_parser.add_argument("space_name", help="Space name (e.g., spaces/AAAA123)")

    # setup-space
    setup_parser = subparsers.add_parser("setup-space", help="Create a new space with members")
    setup_parser.add_argument("display_name", help="Space display name")
    setup_parser.add_argument("members", nargs="+", help="Member email addresses")

    args = parser.parse_args()

    if args.command == "list-spaces":
        result = list_spaces()
    elif args.command == "find-space":
        result = find_space(args.query)
    elif args.command == "get-messages":
        result = get_messages(args.space_name, args.limit)
    elif args.command == "send-message":
        result = send_message(args.space_name, args.text)
    elif args.command == "send-dm":
        result = send_dm(args.email, args.text)
    elif args.command == "find-dm":
        result = find_dm(args.email)
    elif args.command == "list-threads":
        result = list_threads(args.space_name)
    elif args.command == "setup-space":
        result = setup_space(args.display_name, args.members)
    else:
        result = {"error": f"Unknown command: {args.command}"}

    print(json.dumps(result, indent=2))

    if isinstance(result, dict) and "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
