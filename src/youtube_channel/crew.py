from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task

from .tools.duckduckgo_tool import MyDuckDuckGoTool


@CrewBase
class YoutubeChannelCrew:
    """Youtube Channel crew for crypto educational content"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def crypto_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["crypto_researcher"],
            tools=[MyDuckDuckGoTool()],
            verbose=True,
        )

    @agent
    def script_strategist(self) -> Agent:
        return Agent(config=self.agents_config["script_strategist"], verbose=True)

    @task
    def research_crypto_topics(self) -> Task:
        return Task(
            config=self.tasks_config["research_crypto_topics"],
            output_file="output/shorts_ideas_report.txt",
        )

    @task
    def create_script(self) -> Task:
        return Task(
            config=self.tasks_config["create_script"], output_file="output/script.txt"
        )

    @task
    def create_creative_brief(self) -> Task:
        return Task(
            config=self.tasks_config["create_creative_brief"],
            output_file="output/creative_brief.txt",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Youtube Channel crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
