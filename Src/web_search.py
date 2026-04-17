import logging
import requests

logger = logging.getLogger(__name__)

TAVILY_API_URL = "https://api.tavily.com/search"


def tavily_search(query: str, api_key: str, num_results: int = 3) -> str:
    if not api_key or not api_key.strip():
        logger.error("Tavily API key is missing")
        return "Web search unavailable: API key not configured."

    logger.info("Running Tavily web search for: %r", query)
    payload = {"api_key": api_key, "query": query, "num_results": num_results}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(TAVILY_API_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", [])
        if not results:
            logger.info("Tavily search returned no results for: %r", query)
            return "No results found."
        logger.info("Tavily search returned %d results", len(results))
        return "\n\n".join(
            [f"[{r['title']}]({r['url']})\n{r.get('content', '')}" for r in results]
        )
    except requests.exceptions.Timeout:
        logger.error("Tavily search timed out for query: %r", query)
        return "Web search timed out. Please try again."
    except requests.exceptions.HTTPError as exc:
        logger.error("Tavily HTTP error for query %r: %s", query, exc)
        return f"Web search error: {exc}"
    except Exception as exc:
        logger.error("Unexpected web search error for query %r: %s", query, exc, exc_info=True)
        return f"Web search error: {exc}"
