from config import PipelineConfig
from ui import ConsoleUI

SEPARATOR = "=" * 60


class VideoStage:
    """Handles final video assembly"""

    def __init__(self, config: PipelineConfig):
        self.config = config

    def assemble_video(self):
        """Assemble final video from frames and audio"""
        try:
            from tools.video_assembler_tool import assemble_youtube_short
        except ImportError:
            self._print_moviepy_error()
            raise

        output_file = assemble_youtube_short(
            animation_prompts_path=str(self.config.prompts_file),
            audio_path=str(self.config.audio_file),
            frames_dir=str(self.config.frames_dir),
            output_path="output/final_video.mp4",
            apply_effects=True,
            fps=30
        )

        ConsoleUI.print_success(f"Final video: {output_file}")
        ConsoleUI.print_info("Your YouTube Short is ready to upload!")

    def _print_moviepy_error(self):
        """Print MoviePy installation instructions"""
        ConsoleUI.print_header("ERROR: Missing Dependencies")
        print("\nMoviePy is required for video assembly.")
        print("\nInstall with:")
        print("  pip install moviepy")
        print("\nOr add to pyproject.toml dependencies:")
        print('  "moviepy>=1.0.3",')
        print(f"\n{SEPARATOR}\n")
