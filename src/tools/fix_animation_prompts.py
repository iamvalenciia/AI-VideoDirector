"""
Fix Animation Prompts Generator
Generates ONE image prompt per segment from timestamps.json
"""
import json
from pathlib import Path


def fix_animation_prompts(
    timestamps_path: str = "output/timestamps.json",
    output_path: str = "output/animation_prompts.json"
):
    """
    Create a corrected animation_prompts.json with ONE frame per segment.

    Args:
        timestamps_path: Path to timestamps.json from Whisper
        output_path: Where to save the corrected animation_prompts.json
    """

    # Load timestamps
    timestamps_file = Path(timestamps_path)
    if not timestamps_file.exists():
        raise FileNotFoundError(f"Timestamps file not found: {timestamps_path}")

    with open(timestamps_file, 'r', encoding='utf-8') as f:
        timestamps_data = json.load(f)

    segments = timestamps_data.get("segments", [])
    audio_duration = segments[-1]["end"] if segments else 0
    total_segments = len(segments)

    print(f"\n{'='*60}")
    print("FIXING ANIMATION PROMPTS")
    print(f"{'='*60}")
    print(f"Total segments found: {total_segments}")
    print(f"Audio duration: {audio_duration:.2f}s")
    print(f"Generating ONE image per segment...")

    # Create frames - ONE per segment
    frames = []

    # Alternate between zoom in and zoom out
    zoom_types = ["subtle_zoom_in", "subtle_zoom_out"]

    # Vary frame types for visual interest
    frame_types = [
        "character_close_up",
        "character_medium",
        "abstract_concept",
        "detail_shot",
        "wide_shot"
    ]

    for i, segment in enumerate(segments):
        frame = {
            "frame_id": i + 1,
            "frame_filename": f"frame_{i+1:04d}.png",
            "start_time": segment["start"],
            "end_time": segment["end"],
            "duration": segment["end"] - segment["start"],
            "segment_index": i,
            "segment_text": segment["text"],
            "frame_type": frame_types[i % len(frame_types)],
            "shot_type": "medium_shot",
            "prompt": f"Hooded figure representing the concept: '{segment['text']}'. "
                     f"Black and white vector art, minimalist, high contrast, "
                     f"dynamic composition, professional YouTube Short style. "
                     f"Visual metaphor for the narrated concept.",
            "composition": "centered",
            "emotional_tone": "engaging",
            "visual_metaphor": "concept_visualization",
            "transition_in": "crossfade",
            "zoom_effect": zoom_types[i % 2]  # Alternate zoom in/out
        }

        frames.append(frame)

    # Create the complete animation prompts structure
    animation_prompts = {
        "base_image": "character_0001.png",
        "total_frames": total_segments,
        "video_duration": audio_duration,
        "approach": "one_image_per_segment",
        "style_guidelines": "Black and white vector art, minimalist, high contrast",
        "frames": frames
    }

    # Save to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(animation_prompts, f, indent=2, ensure_ascii=False)

    print(f"\n[OK] Fixed animation prompts saved to: {output_file}")
    print(f"  Total frames: {total_segments}")
    print(f"  Coverage: 0.00s - {audio_duration:.2f}s")
    print(f"\nNow you need to generate {total_segments} images using Gemini.")
    print(f"{'='*60}\n")

    return str(output_file)


if __name__ == "__main__":
    # Fix from src/output to output
    fix_animation_prompts(
        timestamps_path="output/timestamps.json",
        output_path="output/animation_prompts.json"
    )
