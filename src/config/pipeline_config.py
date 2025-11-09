from pathlib import Path
from dataclasses import dataclass


@dataclass
class PipelineConfig:
    """Configuration for pipeline execution"""
    topic: str = "Cryptocurrencies"
    output_dir: Path = Path("output")
    frames_dir: Path = Path("output/frames")
    base_image: Path = Path("image/base_image.png")

    # File paths
    script_file: Path = Path("output/video_script.json")
    audio_file: Path = Path("output/narracion.mp3")
    timestamps_file: Path = Path("output/timestamps.json")
    prompts_file: Path = Path("output/animation_prompts.json")

    def __post_init__(self):
        """Ensure output directories exist"""
        self.output_dir.mkdir(exist_ok=True)
        self.frames_dir.mkdir(exist_ok=True)
