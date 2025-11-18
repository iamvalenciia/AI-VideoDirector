"""
CONTENT GENERATION - Pipeline Steps 3-5

Tools for generating audio and visual content:
- claude_financial_analyst: Financial analysis and script generation (Claude Sonnet 4.5)
- elevenlabs_tool: Text-to-speech audio generation (ElevenLabs)
- whisper_tool: Audio transcription with word-level timestamps (Whisper)

Note: image_prompt_generator moved to src/utils/ (one-time generator)
"""

from .claude_financial_analyst import ClaudeFinancialAnalyst
from ...ai.generateAudioElevenlabs import generate_audio_from_script
from ...tools.whisperTool import transcribe_audio, generate_timestamps_from_audio

__all__ = [
    "ClaudeFinancialAnalyst",
    "generate_audio_from_script",
    "transcribe_audio",
    "generate_timestamps_from_audio"
]
