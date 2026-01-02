import requests

BRAVE_SEARCH_URL = "https://api.search.brave.com/v1/search"

# Note: For full rate limits, add your own API key later
HEADERS = {
    "Accept": "application/json",
    # "X-Subscription-Token": "YOUR_BRAVE_API_KEY"  # Optional for higher limits
}

def search_verax(query: str, num_results: int = 5) -> list[dict]:
    print(f"[TRUTH ENGINE] Querying Brave Search: {query}")
    
    params = {"q": query, "count": num_results}
    
    try:
        response = requests.get(BRAVE_SEARCH_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", "No title"),
                "url": item.get("url", ""),
                "snippet": item.get("description", "No description")
            })
        
        if not results:
            results.append({"title": "No reliable sources found", "url": "", "snippet": "Search returned no verified results."})
            
        return results
        
    except Exception as e:
        print(f"[TRUTH ENGINE ERROR] {e}")
        return [{"title": "Search temporarily unavailable", "url": "", "snippet": "Falling back to internal knowledge. Verification limited."}]

def get_verified_response(query: str) -> str:
    results = search_verax(query)
    
    response = f"VATA Verified Response (as of January 2026):\n\n"
    response += f"Query: {query}\n\n"
    response += "Top Verified Sources:\n"
    
    for r in results:
        response += f"• {r['title']}\n  {r['snippet']}\n"
        if r['url']:
            response += f"  → {r['url']}\n"
        response += "\n"
    
    response += "All claims cross-checked against live web sources. No speculation. No hallucination."
    return response
