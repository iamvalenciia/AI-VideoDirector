#!/usr/bin/env python
"""
Updated main.py with complete animation pipeline support
"""

import sys
from pathlib import Path

from crew import YoutubeChannelCrew
from tools.elevenlabs_tool import generate_audio_from_script
from tools.gemini_image_tool import (
    generate_animation_from_prompts,
    generate_test_frames,
    calculate_generation_cost
)
from tools.whisper_tool import generate_timestamps_from_audio


def run_full_pipeline():
    """
    Runs the COMPLETE workflow:
    1. Research + Script (CrewAI agents)
    2. Audio generation (ElevenLabs)
    3. Timestamps (Whisper)
    4. Animation prompts (Animation Director agent)
    5. Image generation (Gemini)
    """
    inputs = {"topic": "Cryptocurrencies"}

    try:
        print("\n" + "=" * 60)
        print("STARTING FULL YOUTUBE SHORTS PIPELINE")
        print("=" * 60)

        # Step 1: Research and Script
        print("\n[STEP 1/5] Research & Script Creation...")
        crew_instance = YoutubeChannelCrew()
        result = crew_instance.crew().kickoff(inputs=inputs)
        print("[SUCCESS] Research and script complete")

        # Step 2: Audio generation
        print("\n[STEP 2/5] Audio Generation...")
        generate_audio_from_script()
        print("[SUCCESS] Audio generation complete")

        # Step 3: Timestamps
        print("\n[STEP 3/5] Timestamp Generation...")
        generate_timestamps_from_audio()
        print("[SUCCESS] Timestamp generation complete")

        # Step 4: Animation prompts
        print("\n[STEP 4/5] Animation Prompts Creation...")
        animation_crew = crew_instance.animation_crew()
        animation_crew.kickoff(inputs={})
        print("[SUCCESS] Animation prompts complete")

        # Step 5: Image generation
        print("\n[STEP 5/5] Frame Generation...")
        stats = generate_animation_from_prompts()
        print(f"[SUCCESS] Generated {stats['frames_generated']} frames")

        # Final summary
        print("\n" + "=" * 60)
        print("FULL PIPELINE COMPLETE!")
        print("=" * 60)
        print("Generated files:")
        print("  [OK] output/news_collection.json")
        print("  [OK] output/video_script.json")
        print("  [OK] output/narracion.mp3")
        print("  [OK] output/timestamps.json")
        print("  [OK] output/animation_prompts.json")
        print(f"  [OK] output/frames/ ({stats['frames_generated']} frames)")
        print("\nNext step: Assemble video with:")
        print("  python main.py --step=assemble-video")
        print("=" * 60 + "\n")

    except Exception as e:
        print_error(e)
        sys.exit(1)


def run_narration_only():
    """Runs ONLY the narration generation."""
    try:
        generate_audio_from_script()
    except Exception as e:
        print_error(e)
        sys.exit(1)


def run_transcription_only():
    """Runs ONLY the transcription generation."""
    try:
        generate_timestamps_from_audio()
    except Exception as e:
        print_error(e)
        sys.exit(1)


def run_audio_and_transcription():
    """Runs audio generation + transcription (skips CrewAI agents)."""
    try:
        print("\n" + "=" * 60)
        print("AUDIO PIPELINE")
        print("=" * 60)

        # Step 1: Generate audio
        print("\n[AUDIO] Generating audio...")
        generate_audio_from_script()

        # Step 2: Generate timestamps
        print("\n[TIMESTAMPS] Generating timestamps...")
        generate_timestamps_from_audio()

        print("\n" + "=" * 60)
        print("AUDIO PIPELINE COMPLETE!")
        print("=" * 60)
        print("Generated files:")
        print("  [OK] output/narracion.mp3")
        print("  [OK] output/timestamps.json")
        print("\n" + "=" * 60 + "\n")

    except Exception as e:
        print_error(e)
        sys.exit(1)


def run_animation_prompts_only():
    """
    Runs ONLY the animation director to create prompts.
    Requires: timestamps.json and video_script.json
    """
    try:
        # Verify required files exist
        if not Path("output/timestamps.json").exists():
            raise FileNotFoundError(
                "timestamps.json not found. Run audio pipeline first."
            )
        if not Path("output/video_script.json").exists():
            raise FileNotFoundError(
                "video_script.json not found. Run crew first."
            )

        print("\n" + "=" * 60)
        print("ANIMATION PROMPTS GENERATION")
        print("=" * 60)

        crew_instance = YoutubeChannelCrew()
        animation_crew = crew_instance.animation_crew()
        result = animation_crew.kickoff(inputs={})

        print("\n" + "=" * 60)
        print("ANIMATION PROMPTS COMPLETE!")
        print("=" * 60)
        print("Generated file:")
        print("  [OK] output/animation_prompts.json")
        print("\nNext step: Generate frames with:")
        print("  python main.py --step=generate-frames")
        print("=" * 60 + "\n")

    except Exception as e:
        print_error(e)
        sys.exit(1)


def run_frame_generation_only():
    """
    Runs ONLY the Gemini image generation.
    Requires: animation_prompts.json and base character image
    """
    try:
        # Verify required files exist
        prompts_file = Path("output/animation_prompts.json")
        if not prompts_file.exists():
            raise FileNotFoundError(
                "animation_prompts.json not found. Run animation prompts step first."
            )

        # Verify base image exists
        base_image = Path("image/base_image.png")
        if not base_image.exists():
            raise FileNotFoundError(
                "base_image.png not found at image/base_image.png. "
                "Please provide a base character image."
            )

        print("\n" + "=" * 60)
        print("FRAME GENERATION")
        print("=" * 60)

        stats = generate_animation_from_prompts(confirm_cost=True)

        if stats.get("cancelled"):
            print("\n[INFO] Frame generation was cancelled")
            return

        print("\n" + "=" * 60)
        print("FRAME GENERATION COMPLETE!")
        print("=" * 60)
        print(f"Generated {stats['frames_generated']} frames")
        print(f"Saved to: output/frames/")
        print("\nNext step: Assemble video with:")
        print("  python main.py --step=assemble-video")
        print("=" * 60 + "\n")

    except Exception as e:
        print_error(e)
        sys.exit(1)


def run_test_frame_generation():
    """
    Generate only first 10 frames as test.
    Requires: animation_prompts.json and base character image
    """
    try:
        # Verify required files exist
        prompts_file = Path("output/animation_prompts.json")
        if not prompts_file.exists():
            raise FileNotFoundError(
                "animation_prompts.json not found. Run animation prompts step first."
            )

        # Verify base image exists
        base_image = Path("image/base_image.png")
        if not base_image.exists():
            raise FileNotFoundError(
                "base_image.png not found at image/base_image.png. "
                "Please provide a base character image."
            )

        print("\n" + "=" * 60)
        print("TEST FRAME GENERATION (First 10 frames)")
        print("=" * 60)

        # Calculate cost for 10 frames only
        print("\n[COST ESTIMATION - Test Run]")
        cost_info = calculate_generation_cost(str(prompts_file))
        test_cost = (cost_info['total_cost_usd'] / cost_info['total_frames']) * 10
        print(f"  Test frames: 10")
        print(f"  Estimated cost: ${test_cost:.2f}")
        print(f"  Full generation would cost: ${cost_info['total_cost_usd']:.2f}")
        print()

        stats = generate_test_frames(num_frames=10)

        print("\n" + "=" * 60)
        print("TEST FRAME GENERATION COMPLETE!")
        print("=" * 60)
        print(f"Generated {stats['frames_generated']} test frames")
        print(f"Review frames in: output/frames/")
        print("\nIf satisfied, generate all frames with:")
        print("  python main.py --step=generate-frames")
        print("=" * 60 + "\n")

    except Exception as e:
        print_error(e)
        sys.exit(1)


def calculate_cost_only():
    """
    Calculate and display cost without generating frames.
    """
    try:
        prompts_file = Path("output/animation_prompts.json")
        if not prompts_file.exists():
            raise FileNotFoundError(
                "animation_prompts.json not found. Run animation prompts step first."
            )

        print("\n" + "=" * 60)
        print("COST CALCULATION")
        print("=" * 60)

        cost_info = calculate_generation_cost(str(prompts_file))

        print(f"\n[FRAMES] Total frames: {cost_info['total_frames']}")
        print(f"\n[COST BREAKDOWN]")
        print(f"  Output cost (images):  ${cost_info['output_cost_usd']:.2f}")
        print(f"  Input cost (prompts):  ${cost_info['input_cost_usd']:.2f}")
        print(f"  ────────────────────────────────────────")
        print(f"  TOTAL ESTIMATED COST:  ${cost_info['total_cost_usd']:.2f}")
        print(f"  Cost per frame:        ${cost_info['cost_per_frame_usd']:.4f}")
        print(f"\n[TOKENS] Estimated: {cost_info['estimated_tokens']:,} tokens")
        print(f"\n[PRICING INFO]")
        print(f"  Gemini 2.5 Flash Image rates:")
        print(f"    - Output: ${cost_info['pricing_info']['output_per_image']:.3f} per image")
        print(f"    - Input:  ${cost_info['pricing_info']['input_per_1m_tokens']:.2f} per 1M tokens")
        print("\n" + "=" * 60 + "\n")

    except Exception as e:
        print_error(e)
        sys.exit(1)


def run_animation_pipeline():
    """
    Runs the complete animation pipeline:
    1. Animation prompts (Animation Director)
    2. Frame generation (Gemini)

    Requires: timestamps.json and video_script.json
    """
    try:
        print("\n" + "=" * 60)
        print("ANIMATION PIPELINE")
        print("=" * 60)

        # Step 1: Generate animation prompts
        print("\n[STEP 1/2] Creating animation prompts...")
        crew_instance = YoutubeChannelCrew()
        animation_crew = crew_instance.animation_crew()
        animation_crew.kickoff(inputs={})
        print("[SUCCESS] Animation prompts complete")

        # Step 2: Generate frames
        print("\n[STEP 2/2] Generating frames...")
        stats = generate_animation_from_prompts()
        print(f"[SUCCESS] Generated {stats['frames_generated']} frames")

        print("\n" + "=" * 60)
        print("ANIMATION PIPELINE COMPLETE!")
        print("=" * 60)
        print("Generated files:")
        print("  [OK] output/animation_prompts.json")
        print(f"  [OK] output/frames/ ({stats['frames_generated']} frames)")
        print(f"  [OK] output/animation_metadata.json")
        print("\nNext step: Assemble video with:")
        print("  python main.py --step=assemble-video")
        print("=" * 60 + "\n")

    except Exception as e:
        print_error(e)
        sys.exit(1)


def run_assemble_video():
    """
    Assembles the final video from frames and audio.
    Requires: frames/, narracion.mp3, animation_prompts.json
    """
    try:
        # Import the video assembler tool
        from tools.video_assembler_tool import assemble_youtube_short

        print("\n" + "=" * 60)
        print("VIDEO ASSEMBLY")
        print("=" * 60)

        # Assemble the video
        output_file = assemble_youtube_short(
            animation_prompts_path="output/animation_prompts.json",
            audio_path="output/narracion.mp3",
            frames_dir="output/frames",
            output_path="output/final_video.mp4",
            apply_effects=True,
            fps=30
        )

        print("\n" + "=" * 60)
        print("VIDEO ASSEMBLY COMPLETE!")
        print("=" * 60)
        print(f"Final video: {output_file}")
        print("\n[READY] Your YouTube Short is ready to upload!")
        print("=" * 60 + "\n")

    except ImportError as e:
        print("\n" + "=" * 60)
        print("ERROR: Missing Dependencies")
        print("=" * 60)
        print("\nMoviePy is required for video assembly.")
        print("\nInstall with:")
        print("  pip install moviepy")
        print("\nOr add to pyproject.toml dependencies:")
        print('  "moviepy>=1.0.3",')
        print("\n" + "=" * 60 + "\n")
        sys.exit(1)
    except Exception as e:
        print_error(e)
        sys.exit(1)


def print_error(e):
    """Prints a formatted error message."""
    print("\n" + "=" * 60)
    print("ERROR DURING EXECUTION")
    print("=" * 60)
    print(f"\n{str(e)}\n")
    print("=" * 60 + "\n")


def print_help():
    """Prints usage instructions."""
    print("\n" + "=" * 60)
    print("CRYPTO CLARITY - YouTube Shorts Production Pipeline")
    print("=" * 60)
    print("\nAVAILABLE COMMANDS:\n")

    print("FULL WORKFLOWS:")
    print("  python main.py")
    print("    → Full pipeline: Research → Script → Audio → Timestamps → Prompts → Frames")
    print()
    print("  python main.py --step=audio-pipeline")
    print("    → Audio → Timestamps (requires video_script.json)")
    print()
    print("  python main.py --step=animation-pipeline")
    print("    → Animation Prompts → Frames (requires timestamps.json)")
    print()

    print("\nINDIVIDUAL STEPS:")
    print("  python main.py --step=narrate")
    print("    → Generate audio only (requires video_script.json)")
    print()
    print("  python main.py --step=transcribe")
    print("    → Generate timestamps only (requires narracion.mp3)")
    print()
    print("  python main.py --step=animation-prompts")
    print("    → Create animation prompts (requires timestamps.json)")
    print()
    print("  python main.py --step=calculate-cost")
    print("    → Calculate frame generation cost (requires animation_prompts.json)")
    print()
    print("  python main.py --step=test-frames")
    print("    → Generate first 10 frames as test (requires animation_prompts.json)")
    print()
    print("  python main.py --step=generate-frames")
    print("    → Generate ALL images with Gemini (requires animation_prompts.json)")
    print()
    print("  python main.py --step=assemble-video")
    print("    → Assemble final video (requires frames/ and audio)")
    print()

    print("\nOTHER:")
    print("  python main.py --help")
    print("    → Show this help message")
    print()

    print("\nTYPICAL WORKFLOWS:\n")
    print("New video from scratch:")
    print("  1. python main.py")
    print("     (runs everything)")
    print()
    print("Resume after audio:")
    print("  1. python main.py --step=animation-pipeline")
    print("  2. python main.py --step=assemble-video")
    print()
    print("Regenerate frames only:")
    print("  1. Delete output/frames/")
    print("  2. python main.py --step=generate-frames")
    print()

    print("=" * 60 + "\n")


def run():
    """
    Main execution function.
    Parses command-line arguments to run different pipeline stages.
    """
    # Ensure output directory exists
    Path("output").mkdir(exist_ok=True)
    Path("output/frames").mkdir(exist_ok=True)

    # Parse command-line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == "--step=narrate":
            run_narration_only()
        elif arg == "--step=transcribe":
            run_transcription_only()
        elif arg == "--step=audio-pipeline":
            run_audio_and_transcription()
        elif arg == "--step=animation-prompts":
            run_animation_prompts_only()
        elif arg == "--step=calculate-cost":
            calculate_cost_only()
        elif arg == "--step=test-frames":
            run_test_frame_generation()
        elif arg == "--step=generate-frames":
            run_frame_generation_only()
        elif arg == "--step=animation-pipeline":
            run_animation_pipeline()
        elif arg == "--step=assemble-video":
            run_assemble_video()
        elif arg == "--help":
            print_help()
            sys.exit(0)
        else:
            print(f"[ERROR] Unknown argument: {arg}")
            print_help()
            sys.exit(1)
    else:
        # Default: run full pipeline
        run_full_pipeline()


if __name__ == "__main__":
    run()