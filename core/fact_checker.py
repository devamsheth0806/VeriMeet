"""Fact detection and verification module."""
from openai import OpenAI
from typing import List, Dict, Any, Optional
from core.config import settings
from core.utils import log_external_call

client = OpenAI(api_key=settings.openai_api_key)


class FactChecker:
    """Detects factual statements and triggers verification."""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
    
    def detect_factual_statements(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect factual or numerical statements in the text.
        
        Args:
            text: Transcript text to analyze
        
        Returns:
            List of detected factual statements with context
        """
        log_external_call("OpenAI", "detect_facts", {"text_length": len(text)})
        
        prompt = f"""Analyze the following meeting transcript and identify any factual statements, numerical claims, or verifiable assertions.

Transcript:
{text}

Return a JSON array of detected factual statements. Each statement should include:
- "claim": The exact factual statement or numerical claim
- "type": Type of claim (e.g., "statistical", "factual", "numerical", "date")
- "context": Brief context around the claim

Example format:
[
  {{
    "claim": "Revenue increased 20% this quarter",
    "type": "numerical",
    "context": "Discussed Q3 financial performance"
  }}
]

If no factual statements are found, return an empty array [].

Return ONLY valid JSON, no additional text."""
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a fact detection assistant. Identify verifiable factual statements, numerical claims, and statistical assertions. Return valid JSON only."},
                    {"role": "user", "content": prompt + "\n\nReturn your response as a JSON object with a 'facts' array."}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            import json
            parsed = json.loads(result)
            
            # Handle both {"facts": [...]} and [...] formats
            if isinstance(parsed, dict) and "facts" in parsed:
                facts = parsed["facts"]
            elif isinstance(parsed, list):
                facts = parsed
            else:
                facts = []
            
            return facts if isinstance(facts, list) else []
        
        except Exception as e:
            log_external_call("OpenAI", "detect_facts_error", {"error": str(e)})
            return []
    
    def format_fact_check_message(self, claim: str, verification_result: Dict[str, Any]) -> str:
        """
        Format a fact-check result as a chat message.
        
        Args:
            claim: The original claim
            verification_result: Result from web search verification
        
        Returns:
            Formatted message string for chat
        """
        if not verification_result.get("success"):
            return f"🔍 Fact Check: Unable to verify '{claim}' - {verification_result.get('error', 'Unknown error')}"
        
        verified = verification_result.get("verified", False)
        confidence = verification_result.get("confidence", "unknown")
        sources = verification_result.get("sources", [])
        
        emoji = "✅" if verified else "⚠️"
        status = "VERIFIED" if verified else "NEEDS VERIFICATION"
        
        message = f"{emoji} Fact Check: {claim}\nStatus: {status} (Confidence: {confidence})"
        
        if sources:
            top_source = sources[0]
            message += f"\n📄 Source: {top_source.get('title', 'N/A')}\n{top_source.get('snippet', '')[:150]}..."
            if top_source.get("url"):
                message += f"\n🔗 {top_source['url']}"
        
        return message

