"""
ElevenLabs audio generation - Implemented as a simple function instead of a CrewAI tool.
This saves OpenAI API tokens by not requiring an agent to use it.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from elevenlabs import VoiceSettings, save
from elevenlabs.client import ElevenLabs

load_dotenv()


def generate_audio_from_script(
    script_file: str = "output/video_script.json",
    output_file: str = "output/narracion.mp3",
    voice_id_narrator: str = "1SM7GgM6IMuvQlz2BwM3",
) -> str:
    """
    Generates an MP3 audio file from a script JSON file using ElevenLabs.

    Args:
        script_file: Path to the JSON file containing the script
        output_file: Path where the MP3 will be saved
        voice_id: ElevenLabs voice ID to use

    Returns:
        Success message with output file path

    Raises:
        ValueError: If API key not found or script file invalid
        FileNotFoundError: If script file doesn't exist
    """
    print("🎙️ Starting ElevenLabs audio generation...")
    print(f"   Input: {script_file}")
    print(f"   Output: {output_file}")

    # 1. Validate API Key
    api_key = os.getenv("ELEVEN_LABS_API_KEY")
    if not api_key:
        raise ValueError(
            "ELEVEN_LABS_API_KEY not found in environment variables. "
            "Please add it to your .env file."
        )

    # 2. Read the script file
    script_path = Path(script_file)
    if not script_path.exists():
        raise FileNotFoundError(
            f"Script file not found: {script_file}\n"
            f"Please run the full workflow first to generate the script."
        )

    try:
        with open(script_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {script_file}: {str(e)}")

    # 3. Extract script text
    script_text = data.get("script")
    if not script_text:
        raise ValueError(f"'script' key not found in {script_file}")

    print(f"\n📝 Script preview: {script_text[:100]}...")

    # 4. Generate audio using ElevenLabs
    try:
        client = ElevenLabs(api_key=api_key)

        print(f"🔊 Generating audio with voice ID: {voice_id_narrator}")
        audio = client.text_to_speech.convert(
            text=script_text,
            voice_id=voice_id_narrator,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.7,  # 70% de estabilidad
                similarity_boost=0.75,  # 75% de similitud
                style=0.0,  # 0% de estilo exagerado
                use_speaker_boost=True,
            ),
        )

        # 5. Save the audio file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        save(audio, str(output_path))

        success_msg = f"✅ Audio successfully saved to {output_file}"
        print(f"\n{success_msg}")
        return success_msg

    except Exception as e:
        error_msg = f"❌ ElevenLabs API error: {str(e)}"
        print(f"\n{error_msg}")
        raise RuntimeError(error_msg)


# Optional: Keep the BaseTool version if you still want to use it as a tool
# But for your use case, the function above is better
from crewai.tools import BaseTool


class ElevenLabsTool(BaseTool):
    """
    CrewAI tool wrapper for ElevenLabs (optional - function approach is better).
    Only use this if you need an agent to call it dynamically.
    """

    name: str = "ElevenLabs Audio Generation Tool"
    description: str = (
        "Generates an MP3 audio file from a script text using ElevenLabs. "
        "Input must be the file path to the JSON script (e.g., 'output/video_script.json')."
    )

    def _run(self, script_file_path: str) -> str:
        """Wrapper around the generate_audio_from_script function."""
        try:
            return generate_audio_from_script(script_file=script_file_path)
        except Exception as e:
            return f"Error: {str(e)}"
