"""Intent detection module for parsing scheduling and email requests from transcripts."""
from openai import OpenAI
from typing import List, Dict, Any, Optional
from core.config import settings
from core.utils import log_external_call
import json
import re
from datetime import datetime, timedelta

client = OpenAI(api_key=settings.openai_api_key)


class IntentParser:
    """Detects user intents from meeting transcripts (scheduling, email, etc.)."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
    
    def detect_intents(self, transcript: str, context: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Detect intents from transcript text.
        
        Args:
            transcript: Transcript text to analyze
            context: Optional context about the meeting
        
        Returns:
            List of detected intents with metadata
        """
        log_external_call("OpenAI", "detect_intents", {"text_length": len(transcript)})
        
        prompt = f"""Analyze the following meeting transcript and identify any actionable intents or requests.

Transcript:
{transcript}

{("Context: " + context) if context else ""}

Look for:
1. **Scheduling requests**: Mentions of scheduling meetings, follow-ups, appointments, or calendar events
   - Examples: "schedule a meeting", "let's meet next week", "follow up on Friday", "book a call"
2. **Email requests**: Requests to send summaries, minutes, or information via email
   - Examples: "email the summary", "send me the minutes", "email this to the team"

Return a JSON object with an "intents" array. Each intent should include:
- "type": "schedule" or "email"
- "confidence": "high", "medium", or "low"
- "action": Brief description of the requested action
- "details": Extracted details (dates, times, recipients, etc.)
- "context": Relevant context from the transcript

Example format:
{{
  "intents": [
    {{
      "type": "schedule",
      "confidence": "high",
      "action": "Schedule a follow-up meeting",
      "details": {{
        "date": "next Friday",
        "time": "2pm",
        "topic": "project review"
      }},
      "context": "Let's schedule a follow-up meeting next Friday at 2pm to review the project"
    }}
  ]
}}

If no intents are found, return {{"intents": []}}.

Return ONLY valid JSON, no additional text."""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an intent detection assistant. Identify actionable requests like scheduling meetings or sending emails. Return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            parsed = json.loads(result)
            
            intents = parsed.get("intents", [])
            if not isinstance(intents, list):
                intents = []
            
            # Enhance intents with parsed date/time information
            for intent in intents:
                if intent.get("type") == "schedule":
                    intent["parsed_datetime"] = self._parse_datetime(intent.get("details", {}))
            
            return intents
        
        except Exception as e:
            log_external_call("OpenAI", "detect_intents_error", {"error": str(e)})
            logger = __import__("core.utils", fromlist=["setup_logging"]).setup_logging()
            logger.error(f"Error detecting intents: {e}")
            return []
    
    def _parse_datetime(self, details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse date/time information from intent details.
        
        Args:
            details: Intent details dictionary
        
        Returns:
            Dict with parsed datetime information or None
        """
        date_str = details.get("date", "")
        time_str = details.get("time", "")
        
        if not date_str and not time_str:
            return None
        
        # Simple date/time parsing (can be enhanced with dateutil)
        parsed = {
            "raw_date": date_str,
            "raw_time": time_str,
            "needs_parsing": True  # Flag for manual parsing or LLM enhancement
        }
        
        # Try to extract relative dates
        today = datetime.now()
        date_lower = date_str.lower() if date_str else ""
        
        if "tomorrow" in date_lower:
            parsed["date"] = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "next week" in date_lower:
            # Next Monday
            days_ahead = 7 - today.weekday()
            parsed["date"] = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        elif "next friday" in date_lower or "friday" in date_lower:
            # Find next Friday
            days_ahead = (4 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            parsed["date"] = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        # Try to parse time
        if time_str:
            # Extract hour from strings like "2pm", "14:00", "2:00 PM"
            time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm)?', time_str.lower())
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2)) if time_match.group(2) else 0
                period = time_match.group(3)
                
                if period == "pm" and hour != 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                
                parsed["time"] = f"{hour:02d}:{minute:02d}"
        
        return parsed if parsed.get("date") or parsed.get("time") else None

