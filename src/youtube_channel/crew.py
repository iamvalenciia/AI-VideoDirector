from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from tools.duckduckgo_tool import MyDuckDuckGoTool


@CrewBase
class YoutubeChannelCrew:
    """
    Optimized crew for crypto YouTube Shorts content creation.

    This crew has two specialized agents:
    1. News Hunter - Finds 10 relevant news articles
    2. Script Creator - Creates viral-optimized scripts

    Audio generation is handled separately to save API tokens.
    """

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def news_hunter(self) -> Agent:
        """
        Creates the news research agent with DuckDuckGo search capabilities.
        This agent is responsible for finding the 10 most relevant and recent
        news articles about the specified topic.
        """
        return Agent(
            config=self.agents_config["news_hunter"],
            tools=[MyDuckDuckGoTool()],
            verbose=True,
            allow_delegation=False,
            max_iter=5,
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
            allow_delegation=False,
        )

    @task
    def research_news(self) -> Task:
        """
        Task for researching and collecting 10 relevant news articles.
        Output: JSON file with structured news data.
        """
        return Task(
            config=self.tasks_config["research_news"],
            agent=self.news_hunter(),
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
            agent=self.script_creator(),
            context=[self.research_news()],
            output_file="output/video_script.json",
        )

    @crew
    def crew(self) -> Crew:
        """
        Assembles the crew with a sequential process.

        Flow:
        1. News Hunter searches and collects 10 news articles → news_collection.json
        2. Script Creator analyzes news and creates viral script → video_script.json
        3. Audio generation happens outside the crew (in main.py) to save tokens
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
