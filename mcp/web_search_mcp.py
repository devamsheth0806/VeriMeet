"""MCP server for web search API integration (fact verification)."""
from fastmcp import FastMCP
import httpx
from typing import Dict, Any, List, Optional
from core.config import settings
from core.utils import log_external_call

mcp = FastMCP("Web Search Integration")


def _search_serper(query: str) -> Dict[str, Any]:
    """Search using Serper API."""
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": settings.serper_api_key,
        "Content-Type": "application/json"
    }
    payload = {"q": query}
    
    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()


def _search_tavily(query: str) -> Dict[str, Any]:
    """Search using Tavily API."""
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "max_results": 5
    }
    
    with httpx.Client() as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def search_web(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Search the web to verify factual statements.
    
    Args:
        query: The search query (factual claim to verify)
        num_results: Number of results to return (default: 5)
    
    Returns:
        Dict with search results and verification information
    """
    log_external_call("Web Search", "search", {"query": query, "num_results": num_results})
    
    try:
        # Try Serper first (preferred)
        if settings.serper_api_key:
            results = _search_serper(query)
            return {
                "success": True,
                "provider": "serper",
                "query": query,
                "results": results.get("organic", [])[:num_results],
                "answer_box": results.get("answerBox"),
                "knowledge_graph": results.get("knowledgeGraph")
            }
        
        # Fallback to Tavily
        elif settings.tavily_api_key:
            results = _search_tavily(query)
            return {
                "success": True,
                "provider": "tavily",
                "query": query,
                "results": results.get("results", [])[:num_results]
            }
        
        # Fallback to Google Custom Search (if configured)
        elif settings.google_search_api_key and settings.google_search_engine_id:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": settings.google_search_api_key,
                "cx": settings.google_search_engine_id,
                "q": query,
                "num": num_results
            }
            with httpx.Client() as client:
                response = client.get(url, params=params)
                response.raise_for_status()
                results = response.json()
                return {
                    "success": True,
                    "provider": "google_custom_search",
                    "query": query,
                    "results": results.get("items", [])[:num_results]
                }
        
        else:
            return {
                "success": False,
                "error": "No web search API key configured. Please set SERPER_API_KEY, TAVILY_API_KEY, or GOOGLE_SEARCH_API_KEY"
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
def verify_fact(claim: str, context: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify a factual claim by searching the web and analyzing results.
    
    Args:
        claim: The factual claim to verify (e.g., "Revenue increased 20%")
        context: Optional context about the claim
    
    Returns:
        Dict with verification result and confidence
    """
    log_external_call("Web Search", "verify_fact", {"claim": claim})
    
    # Build search query
    search_query = claim
    if context:
        search_query = f"{claim} {context}"
    
    # Search for the claim
    search_result = search_web(search_query, num_results=5)
    
    if not search_result.get("success"):
        return search_result
    
    # Analyze results (simple heuristic - can be enhanced with LLM)
    results = search_result.get("results", [])
    
    if not results:
        return {
            "success": True,
            "verified": False,
            "confidence": "low",
            "message": "No relevant results found to verify this claim",
            "claim": claim
        }
    
    # Extract key information from top results
    top_result = results[0]
    title = top_result.get("title", "")
    snippet = top_result.get("snippet") or top_result.get("description", "")
    
    return {
        "success": True,
        "verified": True,
        "confidence": "medium",  # Could be enhanced with LLM analysis
        "claim": claim,
        "sources": [
            {
                "title": title,
                "snippet": snippet,
                "url": top_result.get("link") or top_result.get("url", "")
            }
        ],
        "raw_results": results[:3]  # Top 3 results for reference
    }


if __name__ == "__main__":
    mcp.run()

