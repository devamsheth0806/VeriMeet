"""MCP server for Meetstream API integration."""
from fastmcp import FastMCP
import httpx
from typing import Dict, Any, Optional
from core.config import settings
from core.utils import log_external_call

mcp = FastMCP("Meetstream Integration")


@mcp.tool()
def create_bot(meeting_url: str, bot_name: str = "VeriMeet Assistant") -> Dict[str, Any]:
    """
    Create and send a bot to a Google Meet meeting.
    
    Args:
        meeting_url: The Google Meet meeting URL
        bot_name: Name of the bot (default: VeriMeet Assistant)
    
    Returns:
        Dict with bot creation result including bot_id
    """
    log_external_call("Meetstream", "create_bot", {"meeting_url": meeting_url, "bot_name": bot_name})
    
    url = f"{settings.meetstream_api_url}/v1/bots"
    headers = {
        "Authorization": f"Bearer {settings.meetstream_api_key}",
        "Content-Type": "application/json"
    }
    
    # Webhook URL for callbacks
    webhook_url = f"{settings.ngrok_url}/webhook/meetstream"
    
    payload = {
        "meeting_url": meeting_url,
        "bot_name": bot_name,
        "webhook_url": webhook_url,
        "platform": "google_meet"  # Specify Google Meet
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "bot_id": result.get("bot_id"),
                "status": result.get("status"),
                "meeting_url": meeting_url
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
def send_chat_message(bot_id: str, message: str) -> Dict[str, Any]:
    """
    Send a message to the meeting chat via the bot.
    
    Args:
        bot_id: The ID of the bot in the meeting
        message: The message to send to chat
    
    Returns:
        Dict with message sending result
    """
    log_external_call("Meetstream", "send_chat_message", {"bot_id": bot_id, "message_preview": message[:50]})
    
    url = f"{settings.meetstream_api_url}/v1/bots/{bot_id}/chat"
    headers = {
        "Authorization": f"Bearer {settings.meetstream_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": message
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "message_id": result.get("message_id"),
                "sent": True
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
def get_bot_status(bot_id: str) -> Dict[str, Any]:
    """
    Get the current status of a bot.
    
    Args:
        bot_id: The ID of the bot
    
    Returns:
        Dict with bot status information
    """
    log_external_call("Meetstream", "get_bot_status", {"bot_id": bot_id})
    
    url = f"{settings.meetstream_api_url}/v1/bots/{bot_id}"
    headers = {
        "Authorization": f"Bearer {settings.meetstream_api_key}"
    }
    
    try:
        with httpx.Client() as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "bot_id": bot_id,
                "status": result.get("status"),
                "meeting_url": result.get("meeting_url")
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

