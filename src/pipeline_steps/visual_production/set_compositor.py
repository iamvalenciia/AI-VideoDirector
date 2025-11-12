"""
Set Compositor Tool
Composites all visual elements into final frames:
- Base news studio set
- Character (transparent background)
- Screen content (on the studio screen)
- Stock ticker bar (bottom)
- Video title (bottom)
"""

import os
from typing import Dict, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import json


class SetCompositor:
    """
    Composites all visual elements into final video frames
    """

    def __init__(self, output_size: Tuple[int, int] = (1080, 1920)):
        """
        Initialize compositor

        Args:
            output_size: Output frame size (width, height) - default 1080x1920 for vertical video
        """
        self.output_size = output_size
        self.width, self.height = output_size

    def composite_frame(self,
                       set_image_path: str,
                       character_image_path: str,
                       screen_content_path: Optional[str],
                       ticker_overlay_path: Optional[str],
                       video_title: str,
                       output_path: str,
                       character_position: Optional[Tuple[int, int]] = None,
                       character_scale: float = 0.6,
                       screen_position: Optional[Tuple[int, int]] = None,
                       screen_size: Optional[Tuple[int, int]] = None) -> str:
        """
        Composite all elements into a single frame

        Args:
            set_image_path: Path to news studio set background
            character_image_path: Path to character image (transparent background)
            screen_content_path: Path to content to display on screen (optional)
            ticker_overlay_path: Path to stock ticker overlay (optional)
            video_title: Title text to display at bottom
            output_path: Path to save composited frame
            character_position: (x, y) position for character (None = auto-center left)
            character_scale: Scale factor for character (0.0-1.0)
            screen_position: (x, y) position for screen content (None = auto-detect)
            screen_size: (width, height) for screen content (None = auto-detect)

        Returns:
            Path to composited frame
        """
        try:
            print(f"🎬 Compositing frame: {os.path.basename(output_path)}...")

            # Create base canvas
            canvas = Image.new('RGB', self.output_size, (0, 0, 0))

            # 1. Load and paste news studio set
            if os.path.exists(set_image_path):
                studio_set = Image.open(set_image_path).convert('RGB')
                studio_set = studio_set.resize(self.output_size, Image.Resampling.LANCZOS)
                canvas.paste(studio_set, (0, 0))
            else:
                # Fallback: simple background
                canvas = Image.new('RGB', self.output_size, (20, 20, 20))

            # 2. Paste screen content (on the studio screen)
            if screen_content_path and os.path.exists(screen_content_path):
                self._paste_screen_content(
                    canvas,
                    screen_content_path,
                    screen_position,
                    screen_size
                )

            # 3. Paste character (with transparency)
            if os.path.exists(character_image_path):
                self._paste_character(
                    canvas,
                    character_image_path,
                    character_position,
                    character_scale
                )

            # 4. Add video title at bottom
            self._add_video_title(canvas, video_title)

            # 5. Paste ticker overlay (if provided)
            if ticker_overlay_path and os.path.exists(ticker_overlay_path):
                self._paste_ticker_overlay(canvas, ticker_overlay_path)

            # Save composited frame
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            canvas.save(output_path, 'PNG', quality=95)

            print(f"✅ Frame composited: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Failed to composite frame: {str(e)}")
            return None

    def _paste_character(self,
                        canvas: Image.Image,
                        character_path: str,
                        position: Optional[Tuple[int, int]],
                        scale: float):
        """Paste character onto canvas with transparency"""
        character = Image.open(character_path).convert('RGBA')

        # Scale character
        char_width = int(self.width * scale)
        aspect_ratio = character.height / character.width
        char_height = int(char_width * aspect_ratio)
        character = character.resize((char_width, char_height), Image.Resampling.LANCZOS)

        # Position (default: bottom-left, centered)
        if position is None:
            x = int(self.width * 0.15)  # 15% from left
            y = self.height - char_height - 120  # 120px from bottom (space for title/ticker)
        else:
            x, y = position

        # Paste with alpha channel
        canvas.paste(character, (x, y), character)

    def _paste_screen_content(self,
                             canvas: Image.Image,
                             content_path: str,
                             position: Optional[Tuple[int, int]],
                             size: Optional[Tuple[int, int]]):
        """Paste screen content onto the studio screen"""
        screen_content = Image.open(content_path).convert('RGB')

        # Default screen size (adjust based on your set design)
        if size is None:
            screen_width = int(self.width * 0.45)  # 45% of canvas width
            screen_height = int(screen_width * 9/16)  # 16:9 aspect ratio
        else:
            screen_width, screen_height = size

        # Resize content
        screen_content = screen_content.resize(
            (screen_width, screen_height),
            Image.Resampling.LANCZOS
        )

        # Default position (adjust based on your set design)
        if position is None:
            x = int(self.width * 0.52)  # 52% from left (right side)
            y = int(self.height * 0.25)  # 25% from top
        else:
            x, y = position

        # Paste screen content
        canvas.paste(screen_content, (x, y))

    def _add_video_title(self, canvas: Image.Image, title: str):
        """Add video title at bottom of frame"""
        if not title:
            return

        draw = ImageDraw.Draw(canvas)

        # Try to load font
        try:
            font = ImageFont.truetype("arialbd.ttf", 28)  # Bold
        except:
            font = ImageFont.load_default()

        # Calculate text position (bottom-left)
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        x = 30  # 30px from left
        y = self.height - 150  # 150px from bottom (above ticker)

        # Add background bar for text
        padding = 10
        draw.rectangle(
            [(x - padding, y - padding),
             (x + text_width + padding, y + text_height + padding)],
            fill=(0, 0, 0, 200)
        )

        # Draw text
        draw.text((x, y), title, fill=(255, 255, 255), font=font)

    def _paste_ticker_overlay(self, canvas: Image.Image, ticker_path: str):
        """Paste ticker overlay at bottom"""
        ticker = Image.open(ticker_path).convert('RGBA')

        # Resize to match canvas width
        ticker_width = self.width
        ticker_height = 100  # Fixed height for ticker
        ticker = ticker.resize((ticker_width, ticker_height), Image.Resampling.LANCZOS)

        # Position at bottom
        x = 0
        y = self.height - ticker_height

        # Paste with transparency
        canvas.paste(ticker, (x, y), ticker)

    def composite_frame_sequence(self,
                                 visual_plan: Dict,
                                 assets_dir: str,
                                 output_dir: str) -> list:
        """
        Composite entire frame sequence based on visual plan

        Args:
            visual_plan: Visual plan from VisualDirector
            assets_dir: Directory with all generated assets
            output_dir: Directory to save composited frames

        Returns:
            List of composited frame paths
        """
        print(f"🎬 Compositing frame sequence...")

        segments = visual_plan.get('segments', [])
        video_title = visual_plan.get('video_title_display', '')

        # Paths to base assets
        set_path = os.path.join(assets_dir, "news_studio_set.png")
        ticker_path = os.path.join(assets_dir, "ticker_overlay.png")

        composited_frames = []

        for idx, segment in enumerate(segments):
            segment_index = segment.get('segment_index', idx)
            character_pose = segment.get('character_pose', 'neutral')
            screen_content_type = segment.get('screen_content_type', '')

            # Paths
            character_path = os.path.join(assets_dir, f"character_{character_pose}_nobg.png")
            screen_content_path = os.path.join(assets_dir, f"screen_{screen_content_type}_{segment_index}.png")
            output_path = os.path.join(output_dir, f"frame_{segment_index:03d}.png")

            # Check if screen content exists, use fallback if not
            if not os.path.exists(screen_content_path):
                screen_content_path = None

            # Composite frame
            frame_path = self.composite_frame(
                set_image_path=set_path,
                character_image_path=character_path,
                screen_content_path=screen_content_path,
                ticker_overlay_path=ticker_path,
                video_title=video_title,
                output_path=output_path
            )

            if frame_path:
                composited_frames.append({
                    'frame_path': frame_path,
                    'segment_index': segment_index,
                    'start_time': segment.get('start_time', 0),
                    'end_time': segment.get('end_time', 0),
                    'duration': segment.get('duration', 0)
                })

        print(f"✅ Composited {len(composited_frames)} frames")

        # Save frame metadata
        metadata_path = os.path.join(output_dir, "frames_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(composited_frames, f, indent=2)

        return composited_frames


def main():
    """Example usage"""
    compositor = SetCompositor()

    # Example: Composite a single frame
    compositor.composite_frame(
        set_image_path="output/studio_assets/news_studio_set.png",
        character_image_path="output/studio_assets/character_explaining_nobg.png",
        screen_content_path="output/studio_assets/tesla_chart.png",
        ticker_overlay_path="output/ticker_overlays/ticker_overlay.png",
        video_title="Tesla's $1T Pay Package Explained",
        output_path="output/composited_frames/frame_001.png"
    )

    print("\n✅ Frame composited!")


if __name__ == "__main__":
    main()
