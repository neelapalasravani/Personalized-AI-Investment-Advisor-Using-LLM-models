import logging
import os
from typing import Optional

import requests

logger = logging.getLogger(__name__)

TAVILY_API_URL = "https://api.tavily.com/search"


def tavily_search(query: str, api_key: Optional[str] = None) -> str:
    key = api_key or os.getenv("TAVILY_API_KEY")
    if not key:
        logger.error("TAVILY_API_KEY is not set.")
        return "Web search unavailable: API key not configured."

    headers = {"Content-Type": "application/json"}
    payload = {"api_key": key, "query": query, "num_results": 3}
    logger.info("Performing web search for query: %r", query)
    try:
        response = requests.post(TAVILY_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            logger.info("Web search returned no results for query: %r", query)
            return "No results found."
        logger.info("Web search returned %d results for query: %r", len(results), query)
        return "\n\n".join(
            [f"[{r['title']}]({r['url']})\n{r.get('content', '')}" for r in results]
        )
    except requests.exceptions.Timeout:
        logger.error("Web search timed out for query: %r", query)
        return "Web search error: request timed out."
    except Exception as e:
        logger.error("Web search error for query %r: %s", query, e, exc_info=True)
        return f"Web search error: {e}"
