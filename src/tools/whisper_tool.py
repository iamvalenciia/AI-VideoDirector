"""
Whisper transcription - Implemented as a simple function.
Generates word-level timestamps from audio files using OpenAI Whisper.
"""

import json
from pathlib import Path

import whisper
from dotenv import load_dotenv

load_dotenv()


def generate_timestamps_from_audio(
    audio_file: str = "output/narracion.mp3",
    output_file: str = "output/timestamps.json",
    language: str = "en",  # Cambia a "en" para inglés
    model_size: str = "base",  # tiny, base, small, medium, large
) -> str:
    """
    Generates word-level timestamps from an audio file using Whisper.

    Args:
        audio_file: Path to the MP3 audio file
        output_file: Path where the timestamps JSON will be saved
        language: Language code (es, en, etc.)
        model_size: Whisper model size (tiny, base, small, medium, large)

    Returns:
        Success message with output file path

    Raises:
        FileNotFoundError: If audio file doesn't exist
        RuntimeError: If Whisper processing fails
    """
    print("[WHISPER] Starting Whisper transcription...")
    print(f"   Input: {audio_file}")
    print(f"   Output: {output_file}")
    print(f"   Language: {language}")
    print(f"   Model: {model_size}")

    # 1. Validate audio file exists
    audio_path = Path(audio_file)
    if not audio_path.exists():
        raise FileNotFoundError(
            f"Audio file not found: {audio_file}\n"
            f"Please run the narration step first to generate the audio."
        )

    try:
        # 2. Load Whisper model
        print(f"\n[LOADING] Loading Whisper '{model_size}' model...")
        print("   (First run will download model from HuggingFace)")
        model = whisper.load_model(model_size)

        # 3. Transcribe audio with word timestamps
        print("[TRANSCRIBE] Transcribing audio with word-level timestamps...")
        result = model.transcribe(
            str(audio_path),
            language=language,
            word_timestamps=True,  # Enable word-level timestamps
            verbose=False,
        )

        # 4. Format output
        print("[FORMAT] Formatting timestamps...")
        formatted_data = {
            "audio_file": audio_file,
            "language": result.get("language", language),
            "full_transcript": result["text"].strip(),
            "segments": [],
            "words": [],
        }

        # Add segments and words with timestamps
        for segment in result["segments"]:
            # Add segment info
            formatted_data["segments"].append(
                {
                    "start": round(segment["start"], 2),
                    "end": round(segment["end"], 2),
                    "text": segment["text"].strip(),
                }
            )

            # Add individual words with timestamps
            if "words" in segment:
                for word_data in segment["words"]:
                    formatted_data["words"].append(
                        {
                            "word": word_data["word"].strip(),
                            "start": round(word_data["start"], 2),
                            "end": round(word_data["end"], 2),
                        }
                    )

        # 5. Save to JSON file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=2)

        # 6. Print summary
        word_count = len(formatted_data["words"])
        segment_count = len(formatted_data["segments"])
        duration = (
            formatted_data["segments"][-1]["end"] if formatted_data["segments"] else 0
        )

        print("\n" + "=" * 60)
        print("TRANSCRIPTION COMPLETE!")
        print("=" * 60)
        print("[STATISTICS]")
        print(f"   - Total segments: {segment_count}")
        print(f"   - Total words: {word_count}")
        print(f"   - Duration: {duration:.2f} seconds")
        if duration > 0:
            print(f"   - Speed: {word_count / duration:.2f} words/second")
        print(f"   - Language detected: {formatted_data['language']}")
        print(f"\n[OUTPUT] Output file: {output_file}")
        print("=" * 60)

        success_msg = f"[SUCCESS] Timestamps successfully saved to {output_file}"
        return success_msg

    except Exception as e:
        error_msg = f"[ERROR] Whisper error: {str(e)}"
        print(f"\n{error_msg}")
        raise RuntimeError(error_msg)


def get_word_at_time(timestamps_file: str, time_seconds: float) -> dict:
    """
    Utility function to find which word is being spoken at a specific time.

    Args:
        timestamps_file: Path to the timestamps JSON file
        time_seconds: Time in seconds to query

    Returns:
        Dictionary with word information or None if not found
    """
    with open(timestamps_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for word_info in data["words"]:
        if word_info["start"] <= time_seconds <= word_info["end"]:
            return word_info

    return None


def get_segment_at_time(timestamps_file: str, time_seconds: float) -> dict:
    """
    Utility function to find which segment is being spoken at a specific time.

    Args:
        timestamps_file: Path to the timestamps JSON file
        time_seconds: Time in seconds to query

    Returns:
        Dictionary with segment information or None if not found
    """
    with open(timestamps_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    for segment in data["segments"]:
        if segment["start"] <= time_seconds <= segment["end"]:
            return segment

    return None


# Optional: Keep the BaseTool version if you need it as a CrewAI tool
from crewai.tools import BaseTool


class WhisperTool(BaseTool):
    """
    CrewAI tool wrapper for Whisper (optional - function approach is better).
    Only use this if you need an agent to call it dynamically.
    """

    name: str = "Whisper Transcription Tool"
    description: str = (
        "Generates word-level timestamps from an audio file using Whisper. "
        "Input must be the file path to the audio file (e.g., 'output/narracion.mp3')."
    )

    def _run(self, audio_file_path: str) -> str:
        """Wrapper around the generate_timestamps_from_audio function."""
        try:
            return generate_timestamps_from_audio(audio_file=audio_file_path)
        except Exception as e:
            return f"Error: {str(e)}"
