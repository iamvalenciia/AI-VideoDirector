"""
CONTENT GENERATION - Pipeline Steps 3-5

Tools for generating audio and visual content:
- claude_financial_analyst: Financial analysis and script generation (Claude Sonnet 4.5)
- elevenlabs_tool: Text-to-speech audio generation (ElevenLabs)
- whisper_tool: Audio transcription with word-level timestamps (Whisper)
- image_prompt_generator: Generate image prompts from script (GPT-4o)
"""

from .claude_financial_analyst import ClaudeFinancialAnalyst
from .elevenlabs_tool import generate_audio_from_script
from .whisper_tool import transcribe_audio, generate_timestamps_from_audio
from .image_prompt_generator import ImagePromptGenerator

__all__ = [
    "ClaudeFinancialAnalyst",
    "generate_audio_from_script",
    "transcribe_audio",
    "generate_timestamps_from_audio",
    "ImagePromptGenerator"
]
