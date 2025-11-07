from crewai.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun

# Contador global de búsquedas
_search_count = 0


class MyDuckDuckGoTool(BaseTool):
    """
    Enhanced DuckDuckGo search tool optimized for finding CURRENT news.

    This tool wraps the DuckDuckGo search functionality and provides
    a clean interface for the news_hunter agent to find relevant
    and RECENT information about any crypto topic.

    IMPORTANT: This tool searches the LIVE web for current information.
    It does NOT use pre-existing knowledge from 2023 or earlier.

    COST CONTROL: Tracks number of searches to prevent excessive API calls.
    """

    name: str = "DuckDuckGo Web Search"
    description: str = (
        "MANDATORY TOOL for finding CURRENT news and information from the live web. "
        "This tool searches DuckDuckGo and returns RECENT results from 2024-2025. "
        "Use this tool to find breaking news, latest developments, and trending stories. "
        "CRITICAL: You MUST use this tool to get current information. Do NOT rely on "
        "pre-existing knowledge from 2023 or earlier. "
        "\n\nBest practices for queries:"
        "\n- Keep queries SHORT: 2-3 words work best"
        "\n- Include topic + one keyword: 'Bitcoin news', 'Ethereum latest', 'crypto 2025'"
        "\n- DO NOT use quotes, special operators, or words like 'today', 'breaking'"
        "\n\nYou should perform EXACTLY 3 searches and then stop."
    )

    def _run(self, query: str) -> str:
        """
        Execute a search query using DuckDuckGo to find CURRENT information.

        Args:
            query: The search query string (e.g., "Bitcoin news")

        Returns:
            Search results as a formatted string with titles, snippets, and URLs
            from CURRENT sources (2024-2025)
        """
        global _search_count
        _search_count += 1

        try:
            print(f"\n{'=' * 60}")
            print(f"SEARCH #{_search_count}: '{query}'")
            print("=" * 60)

            # Use DuckDuckGo with more results for better coverage
            search = DuckDuckGoSearchRun(max_results=10)
            result = search.run(query)

            # Show preview of results
            preview = result[:400] if len(result) > 400 else result
            print("Search completed successfully")
            print("\nResults preview:")
            print(f"{'-' * 60}")
            print(preview)
            print(f"{'-' * 60}\n")

            return result

        except Exception as e:
            error_msg = f"Search failed for query '{query}': {str(e)}"
            print(error_msg)
            return f"{error_msg}\n\nTry rephrasing your search query or use different keywords."


def reset_search_count():
    """Reset the global search counter. Call this at the start of each run."""
    global _search_count
    _search_count = 0


def get_search_count():
    """Get the current number of searches performed."""
    return _search_count
