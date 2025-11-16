"""Summarization module using OpenAI."""
from openai import OpenAI
from typing import List, Dict, Any
from core.config import settings
from core.utils import log_external_call

client = OpenAI(api_key=settings.openai_api_key)


class Summarizer:
    """Handles meeting summarization using OpenAI."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.summary_context = []
        self.max_context_items = 20  # Sliding window
    
    def summarize(self, transcript: str, previous_summary: str = None) -> str:
        """
        Generate or update a summary of the meeting.
        
        Args:
            transcript: New transcript text to summarize
            previous_summary: Previous summary to build upon
        
        Returns:
            Updated summary string
        """
        log_external_call("OpenAI", "summarize", {"model": self.model, "transcript_length": len(transcript)})
        
        # Build context
        if previous_summary:
            prompt = f"""Previous meeting summary:
{previous_summary}

New transcript segment:
{transcript}

Please update the summary to include the new information. Maintain a concise, structured format with key points."""
        else:
            prompt = f"""Create a concise summary of this meeting transcript segment:
{transcript}

Include key discussion points, decisions, and action items."""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a meeting summarization assistant. Create clear, concise summaries focusing on key points and action items."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            summary = response.choices[0].message.content
            return summary.strip()
        
        except Exception as e:
            log_external_call("OpenAI", "summarize_error", {"error": str(e)})
            return f"Summary generation failed: {str(e)}"
    
    def finalize_summary(self, all_transcripts: List[str], verified_facts: List[Dict[str, Any]] = None) -> str:
        """
        Create a final comprehensive summary of the entire meeting.
        
        Args:
            all_transcripts: List of all transcript segments
            verified_facts: List of verified facts from the meeting
        
        Returns:
            Final comprehensive summary
        """
        log_external_call("OpenAI", "finalize_summary", {"segments": len(all_transcripts)})
        
        combined_transcript = "\n\n".join(all_transcripts)
        
        facts_section = ""
        if verified_facts:
            facts_list = "\n".join([
                f"- {fact.get('claim', 'N/A')}: {fact.get('verification_status', 'N/A')}"
                for fact in verified_facts
            ])
            facts_section = f"\n\nVerified Facts:\n{facts_list}"
        
        prompt = f"""Create a comprehensive final summary of this meeting:
{combined_transcript}{facts_section}

Format the summary with:
1. Meeting Overview
2. Key Discussion Points
3. Decisions Made
4. Action Items
5. Verified Facts (if any)
"""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional meeting summarization assistant. Create well-structured, comprehensive meeting minutes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            summary = response.choices[0].message.content
            return summary.strip()
        
        except Exception as e:
            log_external_call("OpenAI", "finalize_summary_error", {"error": str(e)})
            return f"Final summary generation failed: {str(e)}"

