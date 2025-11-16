"""Main agent orchestrating summarization, fact-checking, and MCP integrations."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from core.summarizer import Summarizer
from core.fact_checker import FactChecker
from core.intent_parser import IntentParser
from core.utils import setup_logging, log_external_call
from mcp.notion_mcp import create_notion_page
from mcp.meetstream_mcp import send_chat_message
from mcp.web_search_mcp import verify_fact
import json

logger = setup_logging()


class VeriMeetAgent:
    """Main agent that orchestrates all VeriMeet capabilities."""
    
    def __init__(self, bot_id: str = None):
        self.bot_id = bot_id
        self.summarizer = Summarizer()
        self.fact_checker = FactChecker()
        self.intent_parser = IntentParser()
        self.transcripts = []
        self.verified_facts = []
        self.detected_intents = []
        self.current_summary = None
    
    def set_bot_id(self, bot_id: str):
        """Set the Meetstream bot ID for chat posting."""
        self.bot_id = bot_id
        logger.info(f"Bot ID set: {bot_id}")
    
    def process_transcript(self, transcript: str, meeting_id: str = None):
        """
        Process a transcript segment:
        1. Detect factual statements
        2. Verify facts and post to chat
        3. Detect intents (scheduling, email requests)
        4. Update summary
        
        Args:
            transcript: Transcript text to process
            meeting_id: Optional meeting identifier
        """
        logger.info(f"Processing transcript segment (length: {len(transcript)})")
        self.transcripts.append(transcript)
        
        # 1. Detect factual statements
        facts = self.fact_checker.detect_factual_statements(transcript)
        logger.info(f"Detected {len(facts)} factual statements")
        
        # 2. Verify each fact and post to chat
        for fact in facts:
            claim = fact.get("claim", "")
            if claim:
                logger.info(f"Verifying claim: {claim}")
                
                # Verify using web search MCP
                verification_result = verify_fact(claim, context=fact.get("context"))
                
                if verification_result.get("success"):
                    # Format and post to chat
                    chat_message = self.fact_checker.format_fact_check_message(claim, verification_result)
                    
                    # Post to meeting chat via Meetstream MCP
                    if self.bot_id:
                        chat_result = send_chat_message(self.bot_id, chat_message)
                        if chat_result.get("success"):
                            logger.info(f"Posted fact-check to chat: {claim[:50]}...")
                        else:
                            logger.error(f"Failed to post to chat: {chat_result.get('error')}")
                    else:
                        logger.warning("Bot ID not set - skipping chat post")
                    
                    # Store verified fact
                    self.verified_facts.append({
                        "claim": claim,
                        "context": fact.get("context"),
                        "verification": verification_result
                    })
        
        # 3. Detect intents (scheduling, email requests)
        intents = self.intent_parser.detect_intents(transcript, context=self.current_summary)
        logger.info(f"Detected {len(intents)} intents")
        
        # Process each intent
        for intent in intents:
            intent_type = intent.get("type")
            confidence = intent.get("confidence", "low")
            
            # Only process high/medium confidence intents
            if confidence in ["high", "medium"]:
                self.detected_intents.append(intent)
                
                if intent_type == "schedule":
                    logger.info(f"Scheduling intent detected: {intent.get('action')}")
                    # Will be handled by Calendar MCP
                    self._handle_schedule_intent(intent)
                elif intent_type == "email":
                    logger.info(f"Email intent detected: {intent.get('action')}")
                    # Will be handled by Gmail MCP
                    self._handle_email_intent(intent)
        
        # 4. Update summary
        self.current_summary = self.summarizer.summarize(
            transcript,
            previous_summary=self.current_summary
        )
        logger.info(f"Summary updated (length: {len(self.current_summary)})")
        
        return {
            "facts_detected": len(facts),
            "facts_verified": len(self.verified_facts),
            "intents_detected": len(intents),
            "summary_length": len(self.current_summary)
        }
    
    def _handle_schedule_intent(self, intent: Dict[str, Any]):
        """Handle a scheduling intent by creating a calendar event."""
        try:
            from mcp.calendar_mcp import create_calendar_event
            
            details = intent.get("details", {})
            action = intent.get("action", "Schedule meeting")
            
            # Extract event information
            title = details.get("topic") or action
            date = details.get("date") or intent.get("parsed_datetime", {}).get("date")
            time = details.get("time") or intent.get("parsed_datetime", {}).get("time")
            description = intent.get("context", "")
            
            result = create_calendar_event(
                title=title,
                date=date,
                time=time,
                description=description
            )
            
            if result.get("success"):
                logger.info(f"Created calendar event: {result.get('event_id')}")
                # Post confirmation to chat
                if self.bot_id:
                    chat_message = f"✅ Calendar event created: {title}"
                    if date:
                        chat_message += f" on {date}"
                    if time:
                        chat_message += f" at {time}"
                    send_chat_message(self.bot_id, chat_message)
            else:
                logger.error(f"Failed to create calendar event: {result.get('error')}")
        
        except ImportError:
            logger.warning("Calendar MCP not available - scheduling intent not processed")
        except Exception as e:
            logger.error(f"Error handling schedule intent: {e}", exc_info=True)
    
    def _handle_email_intent(self, intent: Dict[str, Any]):
        """Handle an email intent by sending the summary."""
        try:
            from mcp.gmail_mcp import send_email_summary
            
            details = intent.get("details", {})
            recipients = details.get("recipients", [])
            
            # If no recipients specified, use a default or ask
            if not recipients:
                logger.warning("No recipients specified for email intent")
                if self.bot_id:
                    send_chat_message(
                        self.bot_id,
                        "📧 Email requested but no recipients specified. Please provide email addresses."
                    )
                return
            
            # Get current summary
            summary = self.current_summary or "Meeting summary not yet available."
            
            result = send_email_summary(
                recipients=recipients,
                subject=f"Meeting Summary - {datetime.now().strftime('%Y-%m-%d')}",
                summary=summary,
                verified_facts=self.verified_facts
            )
            
            if result.get("success"):
                logger.info(f"Email sent to {recipients}")
                if self.bot_id:
                    send_chat_message(
                        self.bot_id,
                        f"✅ Email summary sent to {', '.join(recipients)}"
                    )
            else:
                logger.error(f"Failed to send email: {result.get('error')}")
        
        except ImportError:
            logger.warning("Gmail MCP not available - email intent not processed")
        except Exception as e:
            logger.error(f"Error handling email intent: {e}", exc_info=True)
    
    def finalize_meeting(self, meeting_title: str = None) -> Dict[str, Any]:
        """
        Finalize the meeting:
        1. Generate final summary
        2. Save to Notion
        
        Args:
            meeting_title: Title for the Notion page (default: auto-generated)
        
        Returns:
            Dict with finalization result
        """
        logger.info("Finalizing meeting...")
        
        # Generate final summary
        final_summary = self.summarizer.finalize_summary(
            self.transcripts,
            self.verified_facts
        )
        
        # Create title
        if not meeting_title:
            from datetime import datetime
            meeting_title = f"Meeting Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Format summary with verified facts
        summary_content = final_summary
        
        if self.verified_facts:
            summary_content += "\n\n## Verified Facts\n\n"
            for fact in self.verified_facts:
                claim = fact.get("claim", "N/A")
                verification = fact.get("verification", {})
                status = "✅ VERIFIED" if verification.get("verified") else "⚠️ NEEDS VERIFICATION"
                summary_content += f"- {claim}: {status}\n"
        
        # Save to Notion via MCP
        notion_result = create_notion_page(
            title=meeting_title,
            content=summary_content
        )
        
        if notion_result.get("success"):
            logger.info(f"Saved summary to Notion: {notion_result.get('url')}")
        else:
            logger.error(f"Failed to save to Notion: {notion_result.get('error')}")
        
        return {
            "success": notion_result.get("success"),
            "notion_url": notion_result.get("url"),
            "summary_length": len(final_summary),
            "facts_verified": len(self.verified_facts),
            "transcript_segments": len(self.transcripts)
        }
    
    def get_current_summary(self) -> str:
        """Get the current rolling summary."""
        return self.current_summary or "No summary yet."


# Global agent instance (will be initialized per meeting)
current_agent: Optional[VeriMeetAgent] = None


def get_or_create_agent(bot_id: str = None) -> VeriMeetAgent:
    """Get or create the current agent instance."""
    global current_agent
    if current_agent is None:
        current_agent = VeriMeetAgent(bot_id=bot_id)
    elif bot_id and current_agent.bot_id != bot_id:
        current_agent.set_bot_id(bot_id)
    return current_agent

