"""
Video Assembler - Combines animation frames with audio to create final video
Requires: moviepy, ffmpeg
Install: pip install moviepy
"""

import json
from pathlib import Path
from typing import List, Tuple

from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_videoclips,
)


def load_animation_data() -> dict:
    """Load animation prompts with timing data."""
    with open("output/animation_prompts.json", "r", encoding="utf-8") as f:
        return json.load(f)


def create_video_clips(animation_data: dict) -> List[ImageClip]:
    """
    Create video clips from frames with proper timing.

    Args:
        animation_data: Animation prompts data with timing

    Returns:
        List of ImageClip objects with proper durations
    """
    clips = []
    frames_dir = Path("output/frames")

    print("\n[VIDEO CLIPS] Creating video clips from frames...")

    for frame_data in animation_data["frames"]:
        frame_path = frames_dir / frame_data["frame_filename"]

        # Check if frame exists
        if not frame_path.exists():
            print(f"[WARNING] Frame not found: {frame_path}")
            continue

        # Calculate duration for this frame
        duration = frame_data["duration"]

        # Create clip
        clip = ImageClip(str(frame_path)).set_duration(duration)

        clips.append(clip)
        print(f"  [OK] {frame_data['frame_filename']} ({duration:.2f}s)")

    return clips


def assemble_final_video(
    output_filename: str = "output/final_video.mp4",
    fps: int = 24,
    resolution: Tuple[int, int] = (1080, 1920),  # 9:16 for Shorts
) -> str:
    """
    Assemble the final video from frames and audio.

    Args:
        output_filename: Path for output video
        fps: Frames per second
        resolution: Video resolution (width, height) - 1080x1920 for Shorts

    Returns:
        Path to the generated video file
    """
    print("\n" + "=" * 60)
    print("ASSEMBLING FINAL VIDEO")
    print("=" * 60)

    try:
        # 1. Load animation data
        print("\n[LOADING] Loading animation data...")
        animation_data = load_animation_data()
        total_frames = len(animation_data["frames"])
        print(f"   Total frames: {total_frames}")

        # 2. Create video clips
        video_clips = create_video_clips(animation_data)
        if not video_clips:
            raise ValueError("No valid video clips created!")

        print(f"\n[SUCCESS] Created {len(video_clips)} video clips")

        # 3. Concatenate clips
        print("\n[CONCATENATE] Concatenating clips...")
        final_video = concatenate_videoclips(video_clips, method="compose")

        # 4. Resize to target resolution (9:16 for Shorts)
        print(f"\n[RESIZE] Resizing to {resolution[0]}x{resolution[1]} (9:16)...")
        final_video = final_video.resize(resolution)

        # 5. Add audio
        audio_path = Path("output/narracion.mp3")
        if audio_path.exists():
            print("\n[AUDIO] Adding audio...")
            audio = AudioFileClip(str(audio_path))

            # Ensure audio and video have same duration
            if audio.duration > final_video.duration:
                print(
                    f"   [WARNING] Trimming audio from {audio.duration:.2f}s to {final_video.duration:.2f}s"
                )
                audio = audio.subclip(0, final_video.duration)
            elif audio.duration < final_video.duration:
                print(
                    f"   [WARNING] Video is longer than audio ({final_video.duration:.2f}s vs {audio.duration:.2f}s)"
                )

            final_video = final_video.set_audio(audio)
        else:
            print("\n[WARNING] No audio file found, creating silent video")

        # 6. Set FPS
        final_video = final_video.set_fps(fps)

        # 7. Write video file
        print(f"\n[WRITING] Writing video to {output_filename}...")
        print("   This may take a few minutes...")

        final_video.write_videofile(
            output_filename,
            codec="libx264",
            audio_codec="aac",
            fps=fps,
            preset="medium",  # balance between quality and speed
            bitrate="8000k",  # high quality for Shorts
        )

        # 8. Get final video info
        duration = final_video.duration
        size = Path(output_filename).stat().st_size / (1024 * 1024)  # MB

        print("\n" + "=" * 60)
        print("VIDEO ASSEMBLY COMPLETE!")
        print("=" * 60)
        print(f"[VIDEO INFO]")
        print(f"   Duration: {duration:.2f} seconds")
        print(f"   Resolution: {resolution[0]}x{resolution[1]} (9:16)")
        print(f"   FPS: {fps}")
        print(f"   File size: {size:.2f} MB")
        print(f"   Output: {output_filename}")
        print("\n[READY] Your YouTube Short is ready to upload!")
        print("=" * 60)

        # Cleanup
        final_video.close()
        if audio_path.exists():
            audio.close()

        return output_filename

    except Exception as e:
        print(f"\n[ERROR] Error assembling video: {str(e)}")
        raise


def create_preview_video(
    output_filename: str = "output/preview.mp4",
    max_duration: int = 10,
) -> str:
    """
    Create a quick preview video (first 10 seconds) for testing.

    Args:
        output_filename: Path for preview video
        max_duration: Maximum duration in seconds

    Returns:
        Path to preview video
    """
    print("\n" + "=" * 60)
    print("CREATING PREVIEW VIDEO")
    print("=" * 60)

    try:
        animation_data = load_animation_data()

        # Filter frames for preview duration
        preview_frames = [
            f for f in animation_data["frames"] if f["start_time"] < max_duration
        ]

        if not preview_frames:
            raise ValueError("No frames within preview duration")

        print(f"\n[PREVIEW] Creating preview with {len(preview_frames)} frames")

        # Temporarily modify data for preview
        temp_data = animation_data.copy()
        temp_data["frames"] = preview_frames

        # Save temporary data
        temp_file = Path("output/temp_preview_data.json")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(temp_data, f)

        # Create preview clips
        clips = []
        frames_dir = Path("output/frames")

        for frame_data in preview_frames:
            frame_path = frames_dir / frame_data["frame_filename"]
            if frame_path.exists():
                duration = min(
                    frame_data["duration"], max_duration - frame_data["start_time"]
                )
                clip = ImageClip(str(frame_path)).set_duration(duration)
                clips.append(clip)

        if not clips:
            raise ValueError("No valid clips for preview")

        # Concatenate
        preview = concatenate_videoclips(clips, method="compose")
        preview = preview.resize((1080, 1920))

        # Add audio if available
        audio_path = Path("output/narracion.mp3")
        if audio_path.exists():
            audio = AudioFileClip(str(audio_path)).subclip(0, min(max_duration, preview.duration))
            preview = preview.set_audio(audio)

        # Write preview
        print(f"\n[WRITING] Writing preview to {output_filename}...")
        preview.write_videofile(
            output_filename,
            codec="libx264",
            audio_codec="aac",
            fps=24,
            preset="ultrafast",  # fast for preview
        )

        print("\n[SUCCESS] Preview video created!")
        print(f"   Duration: {preview.duration:.2f}s")
        print(f"   Output: {output_filename}")

        # Cleanup
        preview.close()
        temp_file.unlink()

        return output_filename

    except Exception as e:
        print(f"\n[ERROR] Error creating preview: {str(e)}")
        raise


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        # Create quick preview
        create_preview_video()
    else:
        # Create full video
        assemble_final_video()