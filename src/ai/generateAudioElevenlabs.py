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

def generate_audio_from_script(script_text: str, output_file: str, voice_id_narrator: str,) -> str:
    print("[ELEVENLABS] Starting ElevenLabs audio generation...")
    print(f"   Input: {script_text[:30]}...")
    print(f"   Output: {output_file}")

    # 1. Validate API Key
    api_key = os.getenv("ELEVEN_LABS_API_KEY")

    # 4. Generate audio using ElevenLabs
    try:
        client = ElevenLabs(api_key=api_key)

        print(f"[AUDIO] Generating audio with voice ID: {voice_id_narrator}")
        audio = client.text_to_speech.convert(
            text=script_text,
            voice_id=voice_id_narrator,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
            voice_settings=VoiceSettings(
                speed=1.10,  # Velocidad normal
                stability=0.5,  # 50% de estabilidad
                similarity_boost=0.75,  # 75% de similitud
                style=0.0,  # 0% de estilo exagerado
                use_speaker_boost=True,
            ),
        )

        # 5. Save the audio file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        save(audio, str(output_path))

        success_msg = f"[SUCCESS] Audio successfully saved to {output_file}"
        print(f"\n{success_msg}")
        return success_msg

    except Exception as e:
        error_msg = f"[ERROR] ElevenLabs API error: {str(e)}"
        print(f"\n{error_msg}")
        raise RuntimeError(error_msg)