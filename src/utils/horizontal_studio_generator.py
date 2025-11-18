"""
Horizontal Studio Generator - News Studio for Long-Format Videos
Creates a professional newsroom-style scene for horizontal videos (1920x1080)
Layout: Tweet/image on left screen, character behind desk on right
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rembg import remove
import os


class HorizontalStudioGenerator:
    """
    Generates professional news studio scenes for horizontal (landscape) videos
    Designed for long-format content (not shorts)
    """

    def __init__(self, output_dir: str = "output/horizontal_videos"):
        """
        Initialize the horizontal studio generator

        Args:
            output_dir: Directory to save generated scenes
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Standard HD horizontal video dimensions
        self.width = 1920
        self.height = 1080

    def remove_background(self, image_path: str) -> Image.Image:
        """
        Remove background from character image using rembg

        Args:
            image_path: Path to input image

        Returns:
            PIL Image with background removed
        """
        print(f"[BG REMOVAL] Removing background from {Path(image_path).name}...")
        input_img = Image.open(image_path).convert('RGBA')
        output_img = remove(input_img)
        print(f"[OK] Background removed")
        return output_img

    def create_news_desk(self, canvas: Image.Image, desk_x: int, desk_y: int, desk_width: int, desk_height: int):
        """
        Draw a minimalist news desk on the canvas

        Args:
            canvas: PIL Image canvas to draw on
            desk_x: X position of desk
            desk_y: Y position of desk
            desk_width: Width of desk
            desk_height: Height of desk
        """
        draw = ImageDraw.Draw(canvas)

        # Desk color - dark gray/black
        desk_color = (40, 40, 40)
        desk_highlight = (60, 60, 60)

        # Main desk surface (top view perspective)
        # Top surface with slight 3D effect
        desk_top_height = desk_height // 3
        draw.rectangle(
            [desk_x, desk_y, desk_x + desk_width, desk_y + desk_top_height],
            fill=desk_highlight,
            outline=(30, 30, 30),
            width=2
        )

        # Front panel
        draw.rectangle(
            [desk_x, desk_y + desk_top_height, desk_x + desk_width, desk_y + desk_height],
            fill=desk_color,
            outline=(30, 30, 30),
            width=2
        )

        # Add subtle gradient effect for depth
        for i in range(10):
            alpha = int(255 * (1 - i/10))
            shade = Image.new('RGBA', (desk_width, 3), (0, 0, 0, alpha))
            canvas.paste(shade, (desk_x, desk_y + desk_top_height + i * 3), shade)

    def create_screen_frame(self, canvas: Image.Image, screen_x: int, screen_y: int, screen_width: int, screen_height: int):
        """
        Draw a minimalist screen frame on the canvas

        Args:
            canvas: PIL Image canvas to draw on
            screen_x: X position of screen
            screen_y: Y position of screen
            screen_width: Width of screen
            screen_height: Height of screen
        """
        draw = ImageDraw.Draw(canvas)

        # Screen frame - thin black border
        frame_thickness = 15
        draw.rectangle(
            [screen_x - frame_thickness, screen_y - frame_thickness,
             screen_x + screen_width + frame_thickness, screen_y + screen_height + frame_thickness],
            fill=(20, 20, 20),
            outline=(0, 0, 0),
            width=3
        )

    def generate_studio_scene(
        self,
        tweet_image_path: str,
        character_image_path: str,
        ticker_text: str = "",
        output_filename: str = "horizontal_studio_scene.png"
    ) -> str:
        """
        Generate complete news studio scene for horizontal video

        Layout:
        - Left side: Tweet/image displayed on screen
        - Right side: Character behind news desk
        - Bottom: Ticker strip
        - Background: Clean white/gray gradient

        Args:
            tweet_image_path: Path to tweet screenshot or image to display
            character_image_path: Path to character image (background will be removed)
            ticker_text: Text for bottom ticker (optional)
            output_filename: Output filename

        Returns:
            Path to generated scene image
        """
        print(f"\n[STUDIO] Generating horizontal news studio scene...")

        # Create base canvas with gradient background
        canvas = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)

        # Add subtle gradient background (white to light gray)
        for y in range(self.height):
            # Gradient from white (240) to light gray (200)
            shade = int(240 - (40 * y / self.height))
            draw.line([(0, y), (self.width, y)], fill=(shade, shade, shade))

        # Convert to RGBA for transparency support
        canvas = canvas.convert('RGBA')

        # ========== LEFT SIDE: SCREEN WITH TWEET/IMAGE ==========
        print("[STUDIO] Adding screen with content on left side...")

        # Screen dimensions and position (left side)
        screen_margin = 80
        screen_width = 700
        screen_height = 600
        screen_x = screen_margin
        screen_y = (self.height - screen_height) // 2 - 50  # Slightly above center

        # Draw screen frame
        self.create_screen_frame(canvas, screen_x, screen_y, screen_width, screen_height)

        # Load and fit tweet/image into screen
        try:
            tweet_img = Image.open(tweet_image_path).convert('RGBA')

            # Scale to fit screen while maintaining aspect ratio
            tweet_ratio = tweet_img.width / tweet_img.height
            screen_ratio = screen_width / screen_height

            if tweet_ratio > screen_ratio:
                # Scale by width
                new_width = screen_width
                new_height = int(screen_width / tweet_ratio)
            else:
                # Scale by height
                new_height = screen_height
                new_width = int(screen_height * tweet_ratio)

            tweet_resized = tweet_img.resize((new_width, new_height), Image.LANCZOS)

            # Center in screen
            paste_x = screen_x + (screen_width - new_width) // 2
            paste_y = screen_y + (screen_height - new_height) // 2

            canvas.paste(tweet_resized, (paste_x, paste_y), tweet_resized)
            print(f"[OK] Tweet/image added to screen")
        except Exception as e:
            print(f"[WARNING] Could not load tweet image: {e}")
            # Draw placeholder
            draw.rectangle(
                [screen_x, screen_y, screen_x + screen_width, screen_y + screen_height],
                fill=(200, 200, 200)
            )

        # ========== RIGHT SIDE: NEWS DESK ==========
        print("[STUDIO] Adding news desk on right side...")

        # Desk dimensions and position (right side)
        desk_width = 800
        desk_height = 200
        desk_x = self.width - desk_width - 100  # 100px margin from right
        desk_y = self.height - desk_height - 150  # 150px from bottom (space for ticker)

        # Draw desk
        self.create_news_desk(canvas, desk_x, desk_y, desk_width, desk_height)

        # ========== CHARACTER BEHIND DESK ==========
        print("[STUDIO] Adding character behind desk...")

        try:
            # Remove background from character
            character_nobg = self.remove_background(character_image_path)

            # Scale character appropriately
            # Character should be visible from waist up behind desk
            char_max_height = 650  # Taller to show upper body
            char_max_width = 500

            char_ratio = character_nobg.width / character_nobg.height
            if char_ratio > (char_max_width / char_max_height):
                new_width = char_max_width
                new_height = int(char_max_width / char_ratio)
            else:
                new_height = char_max_height
                new_width = int(char_max_height * char_ratio)

            character_resized = character_nobg.resize((new_width, new_height), Image.LANCZOS)

            # Position character behind desk (centered on desk, upper body visible)
            char_x = desk_x + (desk_width - new_width) // 2
            char_y = desk_y - new_height + 100  # 100px overlap with desk

            canvas.paste(character_resized, (char_x, char_y), character_resized)
            print(f"[OK] Character positioned behind desk")
        except Exception as e:
            print(f"[WARNING] Could not load character: {e}")

        # ========== BOTTOM TICKER ==========
        print("[STUDIO] Adding bottom ticker...")

        ticker_height = 60
        ticker_y = self.height - ticker_height

        # Black background for ticker
        ticker_bg = Image.new('RGBA', (self.width, ticker_height), (0, 0, 0, 255))
        canvas.paste(ticker_bg, (0, ticker_y), ticker_bg)

        # Add ticker text if provided
        if ticker_text:
            try:
                # Try to use a nice font
                font_size = 28
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()

                draw = ImageDraw.Draw(canvas)
                text_color = (255, 255, 255)

                # Draw ticker text with some padding
                text_x = 20
                text_y = ticker_y + (ticker_height - font_size) // 2

                draw.text((text_x, text_y), ticker_text, fill=text_color, font=font)
            except Exception as e:
                print(f"[WARNING] Could not add ticker text: {e}")

        # ========== SAVE FINAL SCENE ==========
        output_path = self.output_dir / output_filename

        # Convert back to RGB for final save
        final = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        final.paste(canvas, (0, 0), canvas)

        final.save(output_path, 'PNG', quality=95)

        print(f"\n[OK] Studio scene created: {output_path}")
        print(f"     Dimensions: {self.width}x{self.height}px (HD horizontal)")
        print(f"     Layout: Tweet screen (left) + Character at desk (right)")
        print(f"     Style: Minimalist news studio")

        return str(output_path)


def main():
    """Example usage"""
    generator = HorizontalStudioGenerator()

    # Example paths (update these to your actual files)
    tweet_path = "output/tweet_screenshots/selected_tweet.png"
    character_path = "src/image/base_image.png"
    ticker_text = "BREAKING: Market Analysis • TSLA $234.56 ↑2.3% • AAPL $178.90 ↓1.2%"

    try:
        scene_path = generator.generate_studio_scene(
            tweet_image_path=tweet_path,
            character_image_path=character_path,
            ticker_text=ticker_text,
            output_filename="test_horizontal_studio.png"
        )
        print(f"\n[SUCCESS] Scene generated: {scene_path}")
    except Exception as e:
        print(f"\n[ERROR] Failed to generate scene: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
