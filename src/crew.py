import json
from pathlib import Path
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
    
    @agent
    def animation_director(self) -> Agent:
        """
        Creates the animation director agent that generates detailed
        frame-by-frame prompts for Gemini image generation.

        This agent analyzes the timestamps and script to create prompts
        that will result in fluid, progressive animation.
        """
        return Agent(
            config=self.agents_config["animation_director"],
            verbose=True,
            allow_delegation=False,
            max_iter=3,
        )
    
    #------------------------------
    # Task definitions
    #------------------------------

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
    
    @task
    def create_animation_prompts(self) -> Task:
        """
        Task for creating frame-by-frame animation prompts.
        This task requires:
        - timestamps.json (from Whisper)
        - video_script.json (from script_creator)

        Output: JSON file with detailed prompts for each animation frame.
        """
        # Load the required context files
        context_data = self._load_animation_context()

        return Task(
            config=self.tasks_config["create_animation_prompts"],
            agent=self.animation_director(),
            output_file="output/animation_prompts.json",
            context=[self.create_viral_script()],
            description=self.tasks_config["create_animation_prompts"]["description"]
            + f"\n\nContext data:\n{json.dumps(context_data, indent=2)}",
        )
    
    def _load_animation_context(self) -> dict:
        """
        Helper method to load timestamps and script for animation director.
        """
        context = {}

        # Load timestamps
        timestamps_path = Path("output/timestamps.json")
        if timestamps_path.exists():
            with open(timestamps_path, "r", encoding="utf-8") as f:
                context["timestamps"] = json.load(f)
        else:
            context["timestamps"] = {
                "note": "Timestamps not yet generated. Run audio pipeline first."
            }

        # Load script
        script_path = Path("output/video_script.json")
        if script_path.exists():
            with open(script_path, "r", encoding="utf-8") as f:
                context["script"] = json.load(f)
        else:
            context["script"] = {
                "note": "Script not yet generated. Run crew first."
            }

        return context

    @crew
    def crew(self) -> Crew:
        """
        Assembles the crew with a sequential process.

        Flow:
        1. News Hunter → news_collection.json
        2. Script Creator → video_script.json
        3. (External) Audio generation → narracion.mp3
        4. (External) Whisper transcription → timestamps.json
        5. Animation Director → animation_prompts.json
        6. (External) Gemini image generation → frames/*.png
        """
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

    def animation_crew(self) -> Crew:
        """
        Specialized crew that only runs the animation director.
        Use this when you already have timestamps and script.

        Flow:
        1. Animation Director → animation_prompts.json
        """
        return Crew(
            agents=[self.animation_director()],
            tasks=[self.create_animation_prompts()],
            process=Process.sequential,
            verbose=True,
        )
