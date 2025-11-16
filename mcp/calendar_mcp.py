"""MCP server for Google Calendar API integration."""
from fastmcp import FastMCP
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from core.config import settings
from core.utils import log_external_call

mcp = FastMCP("Google Calendar Integration")


def _get_google_oauth_token() -> Optional[str]:
    """
    Get Google OAuth token for API calls.
    For MVP, this can use a service account or stored token.
    """
    # TODO: Implement OAuth flow or service account authentication
    # For now, return None to indicate not configured
    return getattr(settings, "google_calendar_token", None)


@mcp.tool()
def create_calendar_event(
    title: str,
    date: Optional[str] = None,
    time: Optional[str] = None,
    description: str = "",
    duration_minutes: int = 60
) -> Dict[str, Any]:
    """
    Create a calendar event in Google Calendar.
    
    Args:
        title: Event title
        date: Date in YYYY-MM-DD format (default: today)
        time: Time in HH:MM format (default: current time + 1 hour)
        description: Event description
        duration_minutes: Event duration in minutes (default: 60)
    
    Returns:
        Dict with event creation result
    """
    log_external_call("Google Calendar", "create_event", {"title": title, "date": date, "time": time})
    
    # Get OAuth token
    token = _get_google_oauth_token()
    if not token:
        return {
            "success": False,
            "error": "Google Calendar not configured. Please set GOOGLE_CALENDAR_TOKEN or configure OAuth."
        }
    
    # Parse date and time
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    if not time:
        # Default to 1 hour from now
        start_time = datetime.now() + timedelta(hours=1)
        time = start_time.strftime("%H:%M")
    
    # Combine date and time
    try:
        datetime_str = f"{date}T{time}:00"
        start_datetime = datetime.fromisoformat(datetime_str)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
    except ValueError as e:
        return {
            "success": False,
            "error": f"Invalid date/time format: {e}"
        }
    
    # Format for Google Calendar API (RFC3339)
    start_rfc3339 = start_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    end_rfc3339 = end_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    
    # Get calendar ID (default: primary)
    calendar_id = getattr(settings, "google_calendar_id", "primary")
    
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_rfc3339,
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": end_rfc3339,
            "timeZone": "UTC"
        }
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "event_id": result.get("id"),
                "html_link": result.get("htmlLink"),
                "title": title,
                "start": start_rfc3339,
                "end": end_rfc3339
            }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP {e.response.status_code}: {e.response.text}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def list_upcoming_events(max_results: int = 10) -> Dict[str, Any]:
    """
    List upcoming calendar events.
    
    Args:
        max_results: Maximum number of events to return (default: 10)
    
    Returns:
        Dict with list of upcoming events
    """
    log_external_call("Google Calendar", "list_events", {"max_results": max_results})
    
    token = _get_google_oauth_token()
    if not token:
        return {
            "success": False,
            "error": "Google Calendar not configured."
        }
    
    calendar_id = getattr(settings, "google_calendar_id", "primary")
    url = f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    params = {
        "timeMin": datetime.now().isoformat() + "Z",
        "maxResults": max_results,
        "singleEvents": True,
        "orderBy": "startTime"
    }
    
    try:
        with httpx.Client() as client:
            response = client.get(url, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
            events = result.get("items", [])
            return {
                "success": True,
                "events": [
                    {
                        "id": event.get("id"),
                        "title": event.get("summary"),
                        "start": event.get("start", {}).get("dateTime"),
                        "end": event.get("end", {}).get("dateTime"),
                        "html_link": event.get("htmlLink")
                    }
                    for event in events
                ],
                "count": len(events)
            }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP {e.response.status_code}: {e.response.text}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    mcp.run()

