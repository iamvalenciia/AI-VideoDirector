#!/usr/bin/env python
import sys
from pathlib import Path

from crew import YoutubeChannelCrew
from tools.elevenlabs_tool import generate_audio_from_script

from youtube_channel.tools.whisper_tool import generate_timestamps_from_audio


def run_full_crew():
    """Runs the full workflow: Research, Script, Audio, and Transcription."""
    inputs = {"topic": "Cryptocurrencies"}

    try:
        # Step 1: Run CrewAI agents for research and script creation
        crew_instance = YoutubeChannelCrew()
        result = crew_instance.crew().kickoff(inputs=inputs)

        # Step 2: Generate audio narration
        generate_audio_from_script()

        # Step 3: Generate timestamps with WhisperX
        generate_timestamps_from_audio()

    except Exception as e:
        print_error(e)
        sys.exit(1)


def run_narration_only():
    """Runs ONLY the narration generation (simple function call)."""
    try:
        generate_audio_from_script()

    except Exception as e:
        print_error(e)
        sys.exit(1)


def run_transcription_only():
    """Runs ONLY the transcription generation (simple function call)."""

    try:
        generate_timestamps_from_audio()

    except Exception as e:
        print_error(e)
        sys.exit(1)


def run_audio_and_transcription():
    """Runs audio generation + transcription (skips CrewAI agents)."""

    try:
        # Step 1: Generate audio
        generate_audio_from_script()

        # Step 2: Generate timestamps
        generate_timestamps_from_audio()

        print("\n" + "=" * 60)
        print("🎉 AUDIO PIPELINE COMPLETE!")
        print("=" * 60)
        print("Generated files:")
        print("  ✅ output/narracion.mp3")
        print("  ✅ output/timestamps.json")
        print("\n" + "=" * 60 + "\n")

    except Exception as e:
        print_error(e)
        sys.exit(1)


def print_error(e):
    """Prints a formatted error message."""
    print("ERROR DURING EXECUTION")
    print(f"\n{str(e)}\n")


def print_help():
    """Prints usage instructions."""
    print("\n" + "=" * 60)
    print("CRYPTO CLARITY - YouTube Shorts Production Pipeline")
    print("=" * 60)
    print("\nUsage:")
    print("  python main.py")
    print("    → Runs full workflow: Research + Script + Audio + Transcription")
    print()
    print("  python main.py --step=narrate")
    print("    → Generates audio only (requires video_script.json)")
    print()
    print("  python main.py --step=transcribe")
    print("    → Generates timestamps only (requires narracion.mp3)")
    print()
    print("  python main.py --step=audio-pipeline")
    print("    → Generates audio + timestamps (requires video_script.json)")
    print()
    print("  python main.py --help")
    print("    → Shows this help message")
    print("\n" + "=" * 60 + "\n")


def run():
    """
    Main execution function.
    Parses command-line arguments to run different pipeline stages.
    """
    # Ensure output directory exists
    Path("output").mkdir(exist_ok=True)

    # Parse command-line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--step=narrate":
            run_narration_only()
        elif arg == "--step=transcribe":
            run_transcription_only()
        elif arg == "--step=audio-pipeline":
            run_audio_and_transcription()
        elif arg == "--help":
            print_help()
            sys.exit(0)
        else:
            print(f"❌ Unknown argument: {arg}")
            print_help()
            sys.exit(1)
    else:
        # Default: run full workflow
        run_full_crew()


if __name__ == "__main__":
    run()
