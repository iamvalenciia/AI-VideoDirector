from crewai.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun


class MyDuckDuckGoTool(BaseTool):
    name: str = "DuckDuckGo Search Tool"
    description: str = "Searches the web using DuckDuckGo for a given query."

    def _run(self, query: str) -> str:
        search = DuckDuckGoSearchRun()
        result = search.run(query)
        return result
