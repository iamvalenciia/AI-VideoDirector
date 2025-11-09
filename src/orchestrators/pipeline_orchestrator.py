from typing import Dict
from config import PipelineConfig
from stages import CrewStage, AudioStage, FrameStage, VideoStage
from ui import ConsoleUI

SEPARATOR = "=" * 60


class PipelineOrchestrator:
    """Orchestrates different pipeline configurations"""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.crew_stage = CrewStage(config)
        self.audio_stage = AudioStage(config)
        self.frame_stage = FrameStage(config)
        self.video_stage = VideoStage(config)

    def run_full_pipeline(self):
        """Execute complete pipeline"""
        ConsoleUI.print_header("STARTING FULL YOUTUBE SHORTS PIPELINE")

        # Step 1: Research and Script
        self.crew_stage.run_research_and_script()

        # Step 2: Audio
        ConsoleUI.print_step(2, 5, "Audio Generation")
        self.audio_stage.generate_audio()

        # Step 3: Timestamps
        ConsoleUI.print_step(3, 5, "Timestamp Generation")
        self.audio_stage.generate_timestamps()

        # Step 4: Animation Prompts
        ConsoleUI.print_step(4, 5, "Animation Prompts Creation")
        self.crew_stage.run_animation_prompts()

        # Step 5: Frame Generation
        ConsoleUI.print_step(5, 5, "Frame Generation")
        stats = self.frame_stage.generate_frames()

        # Summary
        self._print_full_pipeline_summary(stats)

    def run_audio_pipeline(self):
        """Execute audio generation and transcription"""
        ConsoleUI.print_header("AUDIO PIPELINE")

        print("\n[AUDIO] Generating audio...")
        self.audio_stage.generate_audio()

        print("\n[TIMESTAMPS] Generating timestamps...")
        self.audio_stage.generate_timestamps()

        ConsoleUI.print_header("AUDIO PIPELINE COMPLETE!")
        ConsoleUI.print_file_list("Generated files", [
            "output/narracion.mp3",
            "output/timestamps.json"
        ])
        print(f"\n{SEPARATOR}\n")

    def run_animation_pipeline(self):
        """Execute animation prompts and frame generation"""
        ConsoleUI.print_header("ANIMATION PIPELINE")

        # Step 1: Animation Prompts
        ConsoleUI.print_step(1, 2, "Creating animation prompts")
        self.crew_stage.run_animation_prompts()

        # Step 2: Frame Generation
        ConsoleUI.print_step(2, 2, "Generating frames")
        stats = self.frame_stage.generate_frames()

        ConsoleUI.print_header("ANIMATION PIPELINE COMPLETE!")
        ConsoleUI.print_file_list("Generated files", [
            "output/animation_prompts.json",
            f"output/frames/ ({stats['frames_generated']} frames)",
            "output/animation_metadata.json"
        ])
        ConsoleUI.print_next_step("Assemble video with: python main.py --step=assemble-video")
        print(f"{SEPARATOR}\n")

    def _print_full_pipeline_summary(self, stats: Dict):
        """Print summary for full pipeline"""
        ConsoleUI.print_header("FULL PIPELINE COMPLETE!")
        ConsoleUI.print_file_list("Generated files", [
            "output/news_collection.json",
            "output/video_script.json",
            "output/narracion.mp3",
            "output/timestamps.json",
            "output/animation_prompts.json",
            f"output/frames/ ({stats['frames_generated']} frames)"
        ])
        ConsoleUI.print_next_step("Assemble video with: python main.py --step=assemble-video")
        print(f"{SEPARATOR}\n")
