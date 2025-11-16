"""MCP server for Notion API integration."""
from fastmcp import FastMCP
import httpx
from typing import Dict, Any
from core.config import settings
from core.utils import log_external_call

mcp = FastMCP("Notion Integration")


@mcp.tool()
def create_notion_page(title: str, content: str, database_id: str = None) -> Dict[str, Any]:
    """
    Create a new page in Notion with the given title and content.
    
    Args:
        title: The title of the page
        content: The content/body text of the page
        database_id: The Notion database ID (uses default from config if not provided)
    
    Returns:
        Dict with page creation result
    """
    database_id = database_id or settings.notion_database_id
    log_external_call("Notion", "create_page", {"title": title, "database_id": database_id})
    
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {settings.notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Create page with rich text content
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "page_id": result.get("id"),
                "url": result.get("url"),
                "title": title
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
def update_notion_page(page_id: str, content: str) -> Dict[str, Any]:
    """
    Update an existing Notion page with new content.
    
    Args:
        page_id: The ID of the page to update
        content: The new content to append
    
    Returns:
        Dict with update result
    """
    log_external_call("Notion", "update_page", {"page_id": page_id})
    
    url = f"https://api.notion.com/v1/blocks/{page_id}/children"
    headers = {
        "Authorization": f"Bearer {settings.notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    payload = {
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content
                            }
                        }
                    ]
                }
            }
        ]
    }
    
    try:
        with httpx.Client() as client:
            response = client.patch(url, headers=headers, json=payload)
            response.raise_for_status()
            return {
                "success": True,
                "page_id": page_id,
                "message": "Page updated successfully"
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

