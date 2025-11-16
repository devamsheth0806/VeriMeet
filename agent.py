"""Main agent orchestrating summarization, fact-checking, and MCP integrations."""
from typing import List, Dict, Any, Optional
from core.summarizer import Summarizer
from core.fact_checker import FactChecker
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
        self.transcripts = []
        self.verified_facts = []
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
        3. Update summary
        
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
        
        # 3. Update summary
        self.current_summary = self.summarizer.summarize(
            transcript,
            previous_summary=self.current_summary
        )
        logger.info(f"Summary updated (length: {len(self.current_summary)})")
        
        return {
            "facts_detected": len(facts),
            "facts_verified": len(self.verified_facts),
            "summary_length": len(self.current_summary)
        }
    
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

