from crew import YoutubeChannelCrew
from config import PipelineConfig
from ui import ConsoleUI
from validators import FileValidator


class CrewStage:
    """Handles CrewAI research and script generation"""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.crew = YoutubeChannelCrew()

    def run_research_and_script(self):
        """Execute research and script creation"""
        ConsoleUI.print_step(1, 5, "Research & Script Creation")
        result = self.crew.crew().kickoff(inputs={"topic": self.config.topic})
        ConsoleUI.print_success("Research and script complete")
        return result

    def run_animation_prompts(self):
        """Execute animation prompts creation"""
        FileValidator.validate_files({
            self.config.timestamps_file: "timestamps.json",
            self.config.script_file: "video_script.json"
        })

        animation_crew = self.crew.animation_crew()
        result = animation_crew.kickoff(inputs={})
        ConsoleUI.print_success("Animation prompts complete")
        return result
