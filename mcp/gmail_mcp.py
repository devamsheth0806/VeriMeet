"""MCP server for Gmail API integration."""
from fastmcp import FastMCP
import httpx
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from core.config import settings
from core.utils import log_external_call

mcp = FastMCP("Gmail Integration")


def _get_google_oauth_token() -> Optional[str]:
    """
    Get Google OAuth token for API calls.
    For MVP, this can use a service account or stored token.
    """
    # TODO: Implement OAuth flow or service account authentication
    # For now, return None to indicate not configured
    return getattr(settings, "google_gmail_token", None)


def _format_email_body(summary: str, verified_facts: List[Dict[str, Any]] = None) -> str:
    """
    Format the email body with summary and verified facts.
    
    Args:
        summary: Meeting summary text
        verified_facts: List of verified facts
    
    Returns:
        Formatted HTML email body
    """
    html_body = f"""
    <html>
    <body>
        <h2>Meeting Summary</h2>
        <div style="white-space: pre-wrap; font-family: Arial, sans-serif;">
{summary}
        </div>
    """
    
    if verified_facts:
        html_body += """
        <h3>Verified Facts</h3>
        <ul>
        """
        for fact in verified_facts:
            claim = fact.get("claim", "N/A")
            verification = fact.get("verification", {})
            status = "✅ VERIFIED" if verification.get("verified") else "⚠️ NEEDS VERIFICATION"
            html_body += f"<li><strong>{claim}</strong>: {status}</li>\n"
        
        html_body += """
        </ul>
        """
    
    html_body += """
    </body>
    </html>
    """
    
    return html_body


@mcp.tool()
def send_email_summary(
    recipients: List[str],
    subject: str,
    summary: str,
    verified_facts: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send an email with meeting summary and verified facts.
    
    Args:
        recipients: List of email addresses to send to
        subject: Email subject line
        summary: Meeting summary text
        verified_facts: Optional list of verified facts to include
    
    Returns:
        Dict with email sending result
    """
    log_external_call("Gmail", "send_email", {"recipients": recipients, "subject": subject})
    
    token = _get_google_oauth_token()
    if not token:
        return {
            "success": False,
            "error": "Gmail not configured. Please set GOOGLE_GMAIL_TOKEN or configure OAuth."
        }
    
    # Format email
    html_body = _format_email_body(summary, verified_facts)
    
    # Create email message
    message = MIMEMultipart("alternative")
    message["To"] = ", ".join(recipients)
    message["From"] = getattr(settings, "gmail_sender_email", "noreply@verimeet.com")
    message["Subject"] = subject
    
    # Add plain text version
    text_part = MIMEText(summary, "plain")
    message.attach(text_part)
    
    # Add HTML version
    html_part = MIMEText(html_body, "html")
    message.attach(html_part)
    
    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    
    url = "https://www.googleapis.com/gmail/v1/users/me/messages/send"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "raw": raw_message
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "message_id": result.get("id"),
                "recipients": recipients,
                "subject": subject
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
def send_simple_email(
    recipients: List[str],
    subject: str,
    body: str,
    is_html: bool = False
) -> Dict[str, Any]:
    """
    Send a simple email message.
    
    Args:
        recipients: List of email addresses
        subject: Email subject
        body: Email body text
        is_html: Whether body is HTML (default: False)
    
    Returns:
        Dict with email sending result
    """
    log_external_call("Gmail", "send_simple_email", {"recipients": recipients, "subject": subject})
    
    token = _get_google_oauth_token()
    if not token:
        return {
            "success": False,
            "error": "Gmail not configured."
        }
    
    # Create email message
    message = MIMEText(body, "html" if is_html else "plain")
    message["To"] = ", ".join(recipients)
    message["From"] = getattr(settings, "gmail_sender_email", "noreply@verimeet.com")
    message["Subject"] = subject
    
    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    
    url = "https://www.googleapis.com/gmail/v1/users/me/messages/send"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "raw": raw_message
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            return {
                "success": True,
                "message_id": result.get("id"),
                "recipients": recipients
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

