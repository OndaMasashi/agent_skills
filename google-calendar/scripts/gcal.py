#!/usr/bin/env python3
"""
Google Calendar API operations.
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
from datetime import datetime, timedelta, timezone

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
log_usage("google-calendar")

from auth import get_valid_access_token

CALENDAR_API_BASE = "https://www.googleapis.com/calendar/v3"


def api_request(method: str, endpoint: str, data: Optional[dict] = None,
                params: Optional[dict] = None) -> dict:
    """Make an authenticated request to the Google Calendar API."""
    token = get_valid_access_token()
    if not token:
        return {"error": "Failed to get access token"}

    url = f"{CALENDAR_API_BASE}/{endpoint}"
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


def list_calendars() -> dict:
    """List all calendars the user has access to."""
    result = api_request("GET", "users/me/calendarList")

    if "error" in result:
        return result

    calendars = []
    for cal in result.get("items", []):
        calendars.append({
            "id": cal.get("id"),
            "summary": cal.get("summary"),
            "primary": cal.get("primary", False),
            "accessRole": cal.get("accessRole"),
            "timeZone": cal.get("timeZone"),
            "backgroundColor": cal.get("backgroundColor")
        })

    return {"calendars": calendars}


def format_event(event: dict) -> dict:
    """Extract useful fields from an event."""
    return {
        "id": event.get("id"),
        "summary": event.get("summary"),
        "description": event.get("description"),
        "location": event.get("location"),
        "start": event.get("start"),
        "end": event.get("end"),
        "status": event.get("status"),
        "htmlLink": event.get("htmlLink"),
        "attendees": [
            {
                "email": a.get("email"),
                "displayName": a.get("displayName"),
                "responseStatus": a.get("responseStatus"),
                "self": a.get("self", False)
            }
            for a in event.get("attendees", [])
        ],
        "organizer": event.get("organizer"),
        "creator": event.get("creator"),
        "recurrence": event.get("recurrence"),
        "recurringEventId": event.get("recurringEventId")
    }


def list_events(calendar_id: str = "primary", time_min: Optional[str] = None,
                time_max: Optional[str] = None, max_results: int = 25) -> dict:
    """List events from a calendar."""
    if not time_min:
        time_min = datetime.now(timezone.utc).isoformat()
    if not time_max:
        time_max = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

    params = {
        "timeMin": time_min,
        "timeMax": time_max,
        "maxResults": str(max_results),
        "singleEvents": "true",
        "orderBy": "startTime"
    }

    result = api_request("GET", f"calendars/{urllib.parse.quote(calendar_id, safe='')}/events",
                         params=params)

    if "error" in result:
        return result

    events = [format_event(e) for e in result.get("items", [])]
    return {
        "events": events,
        "nextPageToken": result.get("nextPageToken")
    }


def get_event(event_id: str, calendar_id: str = "primary") -> dict:
    """Get details for a specific event."""
    result = api_request("GET",
                         f"calendars/{urllib.parse.quote(calendar_id, safe='')}/events/{event_id}")

    if "error" in result:
        return result

    return format_event(result)


def create_event(summary: str, start: str, end: str,
                 description: Optional[str] = None,
                 location: Optional[str] = None,
                 attendees: Optional[list] = None,
                 calendar_id: str = "primary") -> dict:
    """Create a new calendar event."""
    event_data = {
        "summary": summary,
        "start": {"dateTime": start},
        "end": {"dateTime": end}
    }

    if description:
        event_data["description"] = description
    if location:
        event_data["location"] = location
    if attendees:
        event_data["attendees"] = [{"email": email} for email in attendees]

    result = api_request("POST",
                         f"calendars/{urllib.parse.quote(calendar_id, safe='')}/events",
                         data=event_data)

    if "error" in result:
        return result

    return {
        "id": result.get("id"),
        "summary": result.get("summary"),
        "htmlLink": result.get("htmlLink"),
        "status": result.get("status"),
        "start": result.get("start"),
        "end": result.get("end")
    }


def update_event(event_id: str, calendar_id: str = "primary",
                 summary: Optional[str] = None,
                 start: Optional[str] = None,
                 end: Optional[str] = None,
                 description: Optional[str] = None,
                 location: Optional[str] = None,
                 attendees: Optional[list] = None) -> dict:
    """Update an existing calendar event."""
    patch_data = {}

    if summary is not None:
        patch_data["summary"] = summary
    if start is not None:
        patch_data["start"] = {"dateTime": start}
    if end is not None:
        patch_data["end"] = {"dateTime": end}
    if description is not None:
        patch_data["description"] = description
    if location is not None:
        patch_data["location"] = location
    if attendees is not None:
        patch_data["attendees"] = [{"email": email} for email in attendees]

    if not patch_data:
        return {"error": "No fields to update. Specify at least one of: --summary, --start, --end, --description, --location, --attendees"}

    result = api_request("PATCH",
                         f"calendars/{urllib.parse.quote(calendar_id, safe='')}/events/{event_id}",
                         data=patch_data)

    if "error" in result:
        return result

    return {
        "id": result.get("id"),
        "summary": result.get("summary"),
        "updated": result.get("updated"),
        "status": result.get("status")
    }


def delete_event(event_id: str, calendar_id: str = "primary") -> dict:
    """Delete a calendar event."""
    result = api_request("DELETE",
                         f"calendars/{urllib.parse.quote(calendar_id, safe='')}/events/{event_id}")

    if "error" in result:
        return result

    return {"success": True, "eventId": event_id}


def find_free_time(attendees: list, time_min: str, time_max: str,
                   duration_minutes: int = 30) -> dict:
    """Find available meeting slots for given attendees."""
    freebusy_data = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": [{"id": email} for email in attendees]
    }

    result = api_request("POST", "freeBusy", data=freebusy_data)

    if "error" in result:
        return result

    # Collect all busy periods
    all_busy = []
    calendars = result.get("calendars", {})
    for cal_id, cal_info in calendars.items():
        for busy in cal_info.get("busy", []):
            all_busy.append({
                "start": busy.get("start"),
                "end": busy.get("end"),
                "calendar": cal_id
            })

    # Sort busy periods by start time
    all_busy.sort(key=lambda x: x["start"])

    # Find first available slot
    duration = timedelta(minutes=duration_minutes)
    current = datetime.fromisoformat(time_min.replace("Z", "+00:00"))
    end_boundary = datetime.fromisoformat(time_max.replace("Z", "+00:00"))

    free_slot = None
    for busy in all_busy:
        busy_start = datetime.fromisoformat(busy["start"].replace("Z", "+00:00"))
        if busy_start - current >= duration:
            free_slot = {
                "start": current.isoformat(),
                "end": (current + duration).isoformat()
            }
            break
        busy_end = datetime.fromisoformat(busy["end"].replace("Z", "+00:00"))
        if busy_end > current:
            current = busy_end

    if not free_slot and end_boundary - current >= duration:
        free_slot = {
            "start": current.isoformat(),
            "end": (current + duration).isoformat()
        }

    return {
        "freeSlot": free_slot,
        "busySlots": all_busy,
        "durationMinutes": duration_minutes
    }


def respond_to_event(event_id: str, response: str,
                     calendar_id: str = "primary",
                     no_notify: bool = False) -> dict:
    """Respond to an event invitation (accept/decline/tentative)."""
    # First get the event to find self in attendees
    event = api_request("GET",
                        f"calendars/{urllib.parse.quote(calendar_id, safe='')}/events/{event_id}")

    if "error" in event:
        return event

    # Find self in attendees and update response
    attendees = event.get("attendees", [])
    found_self = False
    for attendee in attendees:
        if attendee.get("self"):
            attendee["responseStatus"] = response
            found_self = True
            break

    if not found_self:
        return {"error": "Could not find self in event attendees"}

    params = {}
    if no_notify:
        params["sendUpdates"] = "none"
    else:
        params["sendUpdates"] = "all"

    result = api_request("PATCH",
                         f"calendars/{urllib.parse.quote(calendar_id, safe='')}/events/{event_id}",
                         data={"attendees": attendees},
                         params=params)

    if "error" in result:
        return result

    return {
        "success": True,
        "eventId": event_id,
        "responseStatus": response
    }


def main():
    parser = argparse.ArgumentParser(description="Google Calendar API operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list-calendars
    subparsers.add_parser("list-calendars", help="List all calendars")

    # list-events
    list_events_parser = subparsers.add_parser("list-events", help="List events from a calendar")
    list_events_parser.add_argument("--calendar", default="primary",
                                     help="Calendar ID (default: primary)")
    list_events_parser.add_argument("--time-min", help="Start time (ISO 8601)")
    list_events_parser.add_argument("--time-max", help="End time (ISO 8601)")
    list_events_parser.add_argument("--max-results", type=int, default=25,
                                     help="Max events to return (default: 25)")

    # get-event
    get_event_parser = subparsers.add_parser("get-event", help="Get event details")
    get_event_parser.add_argument("event_id", help="Event ID")
    get_event_parser.add_argument("--calendar", default="primary",
                                   help="Calendar ID (default: primary)")

    # create-event
    create_parser = subparsers.add_parser("create-event", help="Create a new event")
    create_parser.add_argument("summary", help="Event title")
    create_parser.add_argument("start", help="Start time (ISO 8601, e.g., 2024-01-15T10:00:00+09:00)")
    create_parser.add_argument("end", help="End time (ISO 8601)")
    create_parser.add_argument("--description", help="Event description")
    create_parser.add_argument("--location", help="Event location")
    create_parser.add_argument("--attendees", nargs="+", help="Attendee email addresses")
    create_parser.add_argument("--calendar", default="primary",
                                help="Calendar ID (default: primary)")

    # update-event
    update_parser = subparsers.add_parser("update-event", help="Update an existing event")
    update_parser.add_argument("event_id", help="Event ID")
    update_parser.add_argument("--summary", help="New event title")
    update_parser.add_argument("--start", help="New start time (ISO 8601)")
    update_parser.add_argument("--end", help="New end time (ISO 8601)")
    update_parser.add_argument("--description", help="New description")
    update_parser.add_argument("--location", help="New location")
    update_parser.add_argument("--attendees", nargs="+", help="New attendee email addresses")
    update_parser.add_argument("--calendar", default="primary",
                                help="Calendar ID (default: primary)")

    # delete-event
    delete_parser = subparsers.add_parser("delete-event", help="Delete an event")
    delete_parser.add_argument("event_id", help="Event ID")
    delete_parser.add_argument("--calendar", default="primary",
                                help="Calendar ID (default: primary)")

    # find-free-time
    free_parser = subparsers.add_parser("find-free-time", help="Find available meeting slots")
    free_parser.add_argument("--attendees", nargs="+", required=True,
                              help="Attendee email addresses")
    free_parser.add_argument("--time-min", required=True, help="Search start (ISO 8601)")
    free_parser.add_argument("--time-max", required=True, help="Search end (ISO 8601)")
    free_parser.add_argument("--duration", type=int, default=30,
                              help="Meeting duration in minutes (default: 30)")

    # respond-to-event
    respond_parser = subparsers.add_parser("respond-to-event",
                                            help="Respond to an event invitation")
    respond_parser.add_argument("event_id", help="Event ID")
    respond_parser.add_argument("response", choices=["accepted", "declined", "tentative"],
                                 help="Response status")
    respond_parser.add_argument("--calendar", default="primary",
                                 help="Calendar ID (default: primary)")
    respond_parser.add_argument("--no-notify", action="store_true",
                                 help="Don't send notification to organizer")

    args = parser.parse_args()

    if args.command == "list-calendars":
        result = list_calendars()
    elif args.command == "list-events":
        result = list_events(args.calendar, args.time_min, args.time_max, args.max_results)
    elif args.command == "get-event":
        result = get_event(args.event_id, args.calendar)
    elif args.command == "create-event":
        result = create_event(args.summary, args.start, args.end,
                              args.description, args.location, args.attendees, args.calendar)
    elif args.command == "update-event":
        result = update_event(args.event_id, args.calendar,
                              args.summary, args.start, args.end,
                              args.description, args.location, args.attendees)
    elif args.command == "delete-event":
        result = delete_event(args.event_id, args.calendar)
    elif args.command == "find-free-time":
        result = find_free_time(args.attendees, args.time_min, args.time_max, args.duration)
    elif args.command == "respond-to-event":
        result = respond_to_event(args.event_id, args.response, args.calendar, args.no_notify)
    else:
        result = {"error": f"Unknown command: {args.command}"}

    print(json.dumps(result, indent=2))

    if isinstance(result, dict) and "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
