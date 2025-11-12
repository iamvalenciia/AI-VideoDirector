"""
Video Assembler Tool - Professional YouTube Shorts Creator
Uses MoviePy 2.x to create a professional video with synchronized frames and audio
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Tuple
import random

try:
    from moviepy import ImageClip, AudioFileClip, CompositeVideoClip
    from moviepy.video.fx import Resize, Crop
    from moviepy.video.fx.FadeIn import FadeIn
    from moviepy.video.fx.FadeOut import FadeOut
    from moviepy.video.fx.CrossFadeIn import CrossFadeIn
    from moviepy.video.fx.CrossFadeOut import CrossFadeOut
    import numpy as np
    from PIL import Image
    MOVIEPY_AVAILABLE = True
except ImportError as e:
    MOVIEPY_AVAILABLE = False
    print(f"[WARNING] MoviePy not installed properly: {e}")
    print("Install with: pip install moviepy pillow numpy")


# YouTube Shorts optimal dimensions
YOUTUBE_SHORTS_WIDTH = 1080
YOUTUBE_SHORTS_HEIGHT = 1920
ASPECT_RATIO = YOUTUBE_SHORTS_HEIGHT / YOUTUBE_SHORTS_WIDTH  # 16:9 vertical


def apply_ken_burns_zoom(image_array: np.ndarray, duration: float, zoom_factor: float = 1.08, zoom_type: str = "in"):
    """
    Apply subtle Ken Burns effect (anime-style zoom) by creating a function for MoviePy.

    NEW: Reduced to subtle 8% zoom for elegant, anime-inspired effect.
    This keeps the viewer engaged without being distracting.

    Args:
        image_array: Numpy array of the image
        duration: Duration of the effect in seconds
        zoom_factor: How much to zoom (1.0 = no zoom, 1.08 = 8% zoom - subtle)
        zoom_type: "in" for zoom in, "out" for zoom out

    Returns:
        Function that generates frames with zoom effect
    """
    from PIL import Image as PILImage

    original_h, original_w = image_array.shape[:2]

    def make_frame(t):
        # Calculate zoom progress (0 to 1) with easing for smoothness
        progress = t / duration if duration > 0 else 0
        # Apply ease-in-out for smoother, more natural motion
        eased_progress = progress * progress * (3.0 - 2.0 * progress)

        if zoom_type == "in":
            # Start at 1.0, end at zoom_factor
            current_zoom = 1.0 + (zoom_factor - 1.0) * eased_progress
        else:  # zoom out
            # Start at zoom_factor, end at 1.0
            current_zoom = zoom_factor - (zoom_factor - 1.0) * eased_progress

        # Calculate new dimensions
        new_w = int(original_w * current_zoom)
        new_h = int(original_h * current_zoom)

        # Resize image
        pil_img = PILImage.fromarray(image_array.astype('uint8'), 'RGB')
        zoomed_img = pil_img.resize((new_w, new_h), PILImage.LANCZOS)

        # Convert back to numpy array
        zoomed_array = np.array(zoomed_img)

        # Crop to center (back to original size)
        y_offset = (new_h - original_h) // 2
        x_offset = (new_w - original_w) // 2

        cropped = zoomed_array[y_offset:y_offset + original_h, x_offset:x_offset + original_w]

        return cropped

    return make_frame


def resize_and_pad_image(
    image_path: str,
    target_width: int = YOUTUBE_SHORTS_WIDTH,
    target_height: int = YOUTUBE_SHORTS_HEIGHT,
    background_color: Tuple[int, int, int] = (0, 0, 0)
) -> np.ndarray:
    """
    Resize image to fit YouTube Shorts format while maintaining aspect ratio.
    Adds padding if necessary.

    Args:
        image_path: Path to the image file
        target_width: Target width (1080 for YouTube Shorts)
        target_height: Target height (1920 for YouTube Shorts)
        background_color: RGB color for padding (default: black)

    Returns:
        Numpy array of the processed image
    """
    # Load image
    img = Image.open(image_path)
    original_width, original_height = img.size
    original_ratio = original_height / original_width

    # Calculate scaling to fit within target dimensions
    target_ratio = target_height / target_width

    if original_ratio > target_ratio:
        # Image is taller - fit to height
        new_height = target_height
        new_width = int(target_height / original_ratio)
    else:
        # Image is wider - fit to width
        new_width = target_width
        new_height = int(target_width * original_ratio)

    # Resize image
    img_resized = img.resize((new_width, new_height), Image.LANCZOS)

    # Create background canvas
    canvas = Image.new('RGB', (target_width, target_height), background_color)

    # Calculate position to center image
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2

    # Paste resized image onto canvas
    canvas.paste(img_resized, (x_offset, y_offset))

    # Convert to numpy array for MoviePy
    return np.array(canvas)


def create_frame_clip(
    frame_data: Dict,
    frames_dir: Path,
    apply_effects: bool = True
) -> ImageClip:
    """
    Create a video clip from a frame with subtle zoom effects.

    NEW: Uses zoom_effect from JSON to determine zoom direction.
    All zooms are subtle (8%) for anime-style elegance.

    Args:
        frame_data: Frame metadata from animation_prompts.json
        frames_dir: Directory containing frame images
        apply_effects: Whether to apply zoom effects

    Returns:
        ImageClip with duration and effects applied
    """
    frame_path = frames_dir / frame_data["frame_filename"]

    if not frame_path.exists():
        raise FileNotFoundError(f"Frame not found: {frame_path}")

    # Load and prepare image
    image_array = resize_and_pad_image(str(frame_path))
    duration = frame_data["duration"]

    # Create base ImageClip first
    clip = ImageClip(image_array, duration=duration)

    # Apply subtle zoom effects based on JSON specification
    if apply_effects and duration > 0.1:
        # Get zoom direction from JSON (defaults to "in" if not specified)
        zoom_effect = frame_data.get("zoom_effect", "subtle_zoom_in")

        # Parse zoom type from effect name
        if "zoom_out" in zoom_effect:
            zoom_type = "out"
        else:
            zoom_type = "in"

        # Use consistent subtle zoom (8%) for all frames - anime style
        zoom_factor = 1.08

        # Apply zoom effect using a custom effect class
        # This will zoom from/to the CENTER of the image
        try:
            from moviepy.Effect import Effect

            class CenteredZoom(Effect):
                """Custom effect for centered zoom"""

                def __init__(self, zoom_factor, zoom_type, duration):
                    self.zoom_factor = zoom_factor
                    self.zoom_type = zoom_type
                    self.effect_duration = duration

                def apply(self, clip):
                    """Apply the centered zoom effect to the clip"""
                    def make_frame(t):
                        # Get original frame
                        frame = clip.get_frame(t)

                        # Calculate zoom progress with easing
                        progress = t / self.effect_duration if self.effect_duration > 0 else 0
                        eased_progress = progress * progress * (3.0 - 2.0 * progress)

                        if self.zoom_type == "in":
                            current_zoom = 1.0 + (self.zoom_factor - 1.0) * eased_progress
                        else:
                            current_zoom = self.zoom_factor - (self.zoom_factor - 1.0) * eased_progress

                        # Only zoom if needed
                        if abs(current_zoom - 1.0) < 0.001:
                            return frame

                        h, w = frame.shape[:2]

                        # Calculate new size
                        new_w = int(w * current_zoom)
                        new_h = int(h * current_zoom)

                        # Resize image
                        pil_img = Image.fromarray(frame.astype('uint8'), 'RGB')
                        zoomed = pil_img.resize((new_w, new_h), Image.LANCZOS)
                        zoomed_array = np.array(zoomed)

                        # Crop from CENTER to maintain original dimensions
                        y_start = (new_h - h) // 2
                        x_start = (new_w - w) // 2

                        # Ensure we don't go out of bounds
                        y_start = max(0, y_start)
                        x_start = max(0, x_start)
                        y_end = min(new_h, y_start + h)
                        x_end = min(new_w, x_start + w)

                        cropped = zoomed_array[y_start:y_end, x_start:x_end]

                        # If cropped is smaller than expected, pad it
                        if cropped.shape[0] < h or cropped.shape[1] < w:
                            padded = np.zeros((h, w, 3), dtype=np.uint8)
                            padded[:cropped.shape[0], :cropped.shape[1]] = cropped
                            return padded

                        return cropped

                    # Create new clip with zoomed frames
                    from moviepy import VideoClip as VC
                    zoomed = VC(make_frame, duration=clip.duration)
                    # Copy size from original clip
                    zoomed.size = clip.size
                    return zoomed

            # Apply the custom zoom effect
            zoom_effect = CenteredZoom(zoom_factor, zoom_type, duration)
            clip = clip.with_effects([zoom_effect])

        except Exception as e:
            print(f"[WARNING] Could not apply zoom effect to {frame_data['frame_filename']}: {e}")
            import traceback
            traceback.print_exc()
            # Continue with non-zoomed clip

    return clip


def assemble_youtube_short(
    animation_prompts_path: str = "output/animation_prompts.json",
    audio_path: str = "output/narracion.mp3",
    frames_dir: str = "output/frames",
    output_path: str = "output/final_video.mp4",
    apply_effects: bool = True,
    fps: int = 30
) -> str:
    """
    Assemble the final YouTube Short video from frames and audio.

    Args:
        animation_prompts_path: Path to animation_prompts.json
        audio_path: Path to narration audio file
        frames_dir: Directory containing frame images
        output_path: Where to save the final video
        apply_effects: Whether to apply zoom effects
        fps: Frames per second for output video

    Returns:
        Path to the created video file
    """
    if not MOVIEPY_AVAILABLE:
        raise ImportError(
            "MoviePy is required for video assembly. "
            "Install with: pip install moviepy pillow numpy"
        )

    print("\n" + "=" * 60)
    print("ASSEMBLING YOUTUBE SHORT")
    print("=" * 60)

    # Convert paths to Path objects
    prompts_path = Path(animation_prompts_path)
    audio_file = Path(audio_path)
    frames_path = Path(frames_dir)
    output_file = Path(output_path)

    # Validate inputs
    if not prompts_path.exists():
        raise FileNotFoundError(f"Animation prompts not found: {prompts_path}")

    if not audio_file.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    if not frames_path.exists():
        raise FileNotFoundError(f"Frames directory not found: {frames_path}")

    # Load animation prompts
    print(f"\n[1/5] Loading animation data from {prompts_path.name}...")
    with open(prompts_path, 'r', encoding='utf-8') as f:
        animation_data = json.load(f)

    frames_data = animation_data.get("frames", [])
    total_frames = len(frames_data)
    print(f"       Found {total_frames} frames to process")

    # Load audio
    print(f"\n[2/5] Loading audio from {audio_file.name}...")
    audio_clip = AudioFileClip(str(audio_file))
    audio_duration = audio_clip.duration
    print(f"       Audio duration: {audio_duration:.2f} seconds")

    # Create video clips from frames with crossfade transitions
    print(f"\n[3/5] Creating video clips from frames...")
    print(f"       Applying crossfade transitions between images...")
    video_clips = []

    # Crossfade duration (in seconds) - subtle transition
    crossfade_duration = 0.3  # 300ms crossfade

    for i, frame_data in enumerate(frames_data, 1):
        try:
            print(f"       Processing frame {i}/{total_frames}: {frame_data['frame_filename']}", end="\r")
            clip = create_frame_clip(frame_data, frames_path, apply_effects)

            # Apply crossfade transitions using MoviePy 2.x effects
            effects = []

            # Apply CrossFadeIn (except for first frame)
            if i > 1:
                effects.append(CrossFadeIn(crossfade_duration))

            # Apply CrossFadeOut (except for last frame)
            if i < total_frames:
                effects.append(CrossFadeOut(crossfade_duration))

            # Apply effects if any
            if effects:
                clip = clip.with_effects(effects)

            clip = clip.with_start(frame_data["start_time"])
            video_clips.append(clip)
        except Exception as e:
            print(f"\n       [ERROR] Failed to process {frame_data['frame_filename']}: {e}")
            raise

    print(f"\n       Successfully created {len(video_clips)} video clips with crossfade transitions")

    # Assemble final video
    print(f"\n[4/5] Assembling final video...")
    print(f"       Format: {YOUTUBE_SHORTS_WIDTH}x{YOUTUBE_SHORTS_HEIGHT} (YouTube Shorts)")
    print(f"       FPS: {fps}")
    print(f"       Effects: {'Enabled' if apply_effects else 'Disabled'}")

    # Create composite video
    final_video = CompositeVideoClip(
        video_clips,
        size=(YOUTUBE_SHORTS_WIDTH, YOUTUBE_SHORTS_HEIGHT)
    )

    # Set duration to match audio
    final_video = final_video.with_duration(audio_duration)

    # Add audio
    final_video = final_video.with_audio(audio_clip)

    # Export video
    print(f"\n[5/5] Exporting video to {output_file}...")
    print(f"       This may take several minutes...")

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write video file
    final_video.write_videofile(
        str(output_file),
        fps=fps,
        codec='libx264',
        audio_codec='aac',
        preset='medium',
        bitrate='5000k',
        threads=4,
        logger='bar'  # Show progress bar
    )

    # Clean up
    audio_clip.close()
    final_video.close()
    for clip in video_clips:
        clip.close()

    print("\n" + "=" * 60)
    print("VIDEO ASSEMBLY COMPLETE!")
    print("=" * 60)
    print(f"Output file: {output_file}")
    print(f"Format: {YOUTUBE_SHORTS_WIDTH}x{YOUTUBE_SHORTS_HEIGHT} (YouTube Shorts)")
    print(f"Duration: {audio_duration:.2f} seconds")
    print(f"Frames: {total_frames}")
    print("=" * 60 + "\n")

    return str(output_file)


def main():
    """Main function for standalone execution."""
    try:
        output_file = assemble_youtube_short()
        print(f"\n✓ Video created successfully: {output_file}")
        print("\n[READY] Your YouTube Short is ready to upload!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
