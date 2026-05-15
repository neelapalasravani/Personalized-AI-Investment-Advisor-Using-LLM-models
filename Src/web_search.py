import requests

def tavily_search(query, api_key):
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    payload = {"api_key": api_key, "query": query, "num_results": 3}
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        results = response.json().get("results", [])
        return "\n\n".join([
            f"🔗 [{r['title']}]({r['url']})\n{r.get('content', '')}" for r in results
        ]) if results else "No results found."
    except Exception as e:
        return f"Web search error: {e}"
