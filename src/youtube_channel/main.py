#!/usr/bin/env python
import sys
from pathlib import Path

from crew import YoutubeChannelCrew
from tools.elevenlabs_tool import generate_audio_from_script


def run_full_crew():
    """Runs the full workflow: Research and Script generation."""
    inputs = {"topic": "Cryptocurrencies"}

    print("\n" + "=" * 60)
    print("CRYPTO CLARITY - Running Full Workflow")
    print("=" * 60)
    print(f"Topic: {inputs['topic']}")
    print("Starting crew execution...\n")

    try:
        # Use the crew instance directly - NO .crew() call needed!
        crew_instance = YoutubeChannelCrew()
        result = crew_instance.crew().kickoff(inputs=inputs)

        print("\n" + "=" * 60)
        print("SCRIPT GENERATION COMPLETE!")
        print("=" * 60)
        print("\nGenerated files in output/:")
        print("  - news_collection.json")
        print("  - video_script.json")

        # Now generate audio as a simple post-processing step
        print("\n" + "-" * 60)
        print("Generating audio narration...")
        print("-" * 60)

        generate_audio_from_script()

        print("\n" + "=" * 60)
        print("FULL WORKFLOW COMPLETE!")
        print("=" * 60)
        print("All files generated:")
        print("  - output/news_collection.json")
        print("  - output/video_script.json")
        print("  - output/narracion.mp3")
        print("\n" + "=" * 60 + "\n")

    except Exception as e:
        print_error(e)
        sys.exit(1)


def run_narration_only():
    """Runs ONLY the narration generation (simple function call)."""
    print("\n" + "=" * 60)
    print("CRYPTO CLARITY - Generating Audio Only")
    print("=" * 60)

    script_file = Path("output/video_script.json")
    if not script_file.exists():
        print(f"❌ ERROR: Input file '{script_file}' not found.")
        print("You must run the full workflow first to generate the script.")
        print("Use: python main.py")
        sys.exit(1)

    print(f"Using existing script: {script_file}\n")

    try:
        generate_audio_from_script()

        print("\n" + "=" * 60)
        print("AUDIO GENERATION COMPLETE!")
        print("=" * 60)
        print("Generated file:")
        print("  - output/narracion.mp3")
        print("\n" + "=" * 60 + "\n")

    except Exception as e:
        print_error(e)
        sys.exit(1)


def print_error(e):
    """Prints a formatted error message."""
    print("\n" + "=" * 60)
    print("ERROR DURING EXECUTION")
    print("=" * 60)
    print(f"\n{str(e)}\n")


def run():
    """
    Main execution function.
    Parses command-line arguments to run the full crew or just audio generation.
    """
    # Ensure output directory exists
    Path("output").mkdir(exist_ok=True)

    # Parse command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--step=narrate":
            run_narration_only()
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python main.py                (Runs full workflow + audio)")
            print("  python main.py --step=narrate (Generates audio only)")
            sys.exit(0)
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information")
            sys.exit(1)
    else:
        run_full_crew()


if __name__ == "__main__":
    run()
