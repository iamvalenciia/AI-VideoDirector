from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

# Importar ambas herramientas - puedes elegir cuál usar
from .tools.duckduckgo_tool import MyDuckDuckGoTool

# from .tools.improved_duckduckgo_tool import ImprovedDuckDuckGoTool  # Alternativa mejorada


@CrewBase
class YoutubeChannelCrew:
    """
    Optimized crew for crypto YouTube Shorts content creation.

    This crew has two specialized agents:
    1. News Hunter - Finds 10 relevant news articles
    2. Script Creator - Creates viral-optimized scripts

    Output: 2 JSON files ready for production
    """

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def news_hunter(self) -> Agent:
        """
        Creates the news research agent with DuckDuckGo search capabilities.
        This agent is responsible for finding the 10 most relevant and recent
        news articles about the specified topic.

        IMPORTANT: This agent MUST use the DuckDuckGo tool to find current news.
        Limited to exactly 3 searches to control costs.
        """
        return Agent(
            config=self.agents_config["news_hunter"],
            tools=[MyDuckDuckGoTool()],
            verbose=True,
            allow_delegation=False,  # Don't delegate, just search
            max_iter=5,  # Maximum 5 iterations total (3 searches + 2 for processing)
        )

    @agent
    def script_creator(self) -> Agent:
        """
        Creates the script writing agent that transforms news into
        engaging YouTube Shorts scripts optimized for viral potential
        and viewer retention.
        """
        return Agent(
            config=self.agents_config["script_creator"],
            verbose=True,
        )

    @task
    def research_news(self) -> Task:
        """
        Task for researching and collecting 10 relevant news articles.
        Output: JSON file with structured news data.
        """
        return Task(
            config=self.tasks_config["research_news"],
            output_file="output/news_collection.json",
        )

    @task
    def create_viral_script(self) -> Task:
        """
        Task for creating a viral-optimized YouTube Shorts script.
        This task depends on research_news and uses its output.
        Output: JSON file with complete script and production specifications.
        """
        return Task(
            config=self.tasks_config["create_viral_script"],
            output_file="output/video_script.json",
        )

    @crew
    def crew(self) -> Crew:
        """
        Assembles the crew with a sequential process.

        Flow:
        1. News Hunter searches and collects 10 news articles → news_collection.json
        2. Script Creator analyzes news and creates viral script → video_script.json
        """
        return Crew(
            agents=self.agents,  # Both news_hunter and script_creator
            tasks=self.tasks,  # Both research_news and create_viral_script
            process=Process.sequential,  # Execute tasks in order
            verbose=True,
        )
