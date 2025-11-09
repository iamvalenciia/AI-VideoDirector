from tools.elevenlabs_tool import generate_audio_from_script
from tools.whisper_tool import generate_timestamps_from_audio
from config import PipelineConfig
from ui import ConsoleUI
from validators import FileValidator


class AudioStage:
    """Handles audio generation and transcription"""

    def __init__(self, config: PipelineConfig):
        self.config = config

    def generate_audio(self):
        """Generate audio from script"""
        FileValidator.validate_file(
            self.config.script_file,
            "video_script.json"
        )
        generate_audio_from_script()
        ConsoleUI.print_success("Audio generation complete")

    def generate_timestamps(self):
        """Generate timestamps from audio"""
        FileValidator.validate_file(
            self.config.audio_file,
            "narracion.mp3"
        )
        generate_timestamps_from_audio()
        ConsoleUI.print_success("Timestamp generation complete")
