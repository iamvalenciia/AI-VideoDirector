"""
Frame Compositor - Combines all visual layers into final frames
Creates preview frames by compositing:
- Studio background
- Character (from base_image.png with background removed)
- Tweet screenshot
- Bottom ticker
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from rembg import remove
import os


class FrameCompositor:
    """
    Composites all visual layers into final frames for video
    """

    def __init__(self, output_dir: str = "output/financial_shorts"):
        """
        Initialize the frame compositor

        Args:
            output_dir: Directory to save composed frames
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # YouTube Shorts dimensions
        self.width = 1080
        self.height = 1920

    def remove_background(self, image_path: str, output_path: str = None) -> str:
        """
        Remove background from character image using rembg

        Args:
            image_path: Path to input image
            output_path: Optional output path (auto-generated if None)

        Returns:
            Path to background-removed image
        """
        print(f"[BG REMOVAL] Removing background from {Path(image_path).name}...")

        input_img = Image.open(image_path)

        # Remove background
        output_img = remove(input_img)

        # Save
        if output_path is None:
            output_path = self.output_dir / "character_nobg.png"
        else:
            output_path = Path(output_path)

        output_img.save(output_path, 'PNG')
        print(f"[OK] Background removed: {output_path}")

        return str(output_path)

    def compose_frame(
        self,
        studio_bg_path: str,
        character_path: str,
        tweet_path: str,
        ticker_path: str,
        output_filename: str = "preview_frame.png"
    ) -> str:
        """
        Compose all layers into a single frame

        NEW LAYOUT:
        1. Studio background (white top, black bottom)
        2. Tweet screenshot (LARGE, covering almost entire screen as background)
        3. Character (on top of tweet, as if presenting/talking)
        4. Bottom ticker (overlay at bottom)

        Args:
            studio_bg_path: Path to studio background
            character_path: Path to character image (will remove bg if needed)
            tweet_path: Path to tweet screenshot
            ticker_path: Path to ticker strip
            output_filename: Output filename

        Returns:
            Path to composed frame
        """
        print(f"\n[COMPOSITOR] Composing frame...")

        # Load base studio background
        studio_bg = Image.open(studio_bg_path).convert('RGBA')
        if studio_bg.size != (self.width, self.height):
            studio_bg = studio_bg.resize((self.width, self.height), Image.LANCZOS)

        # Create composite canvas
        canvas = studio_bg.copy()

        # ========== LAYER 1: Tweet Screenshot (CENTERED WITH PADDING) ==========
        print("[COMPOSITOR] Adding tweet as main background...")
        tweet = Image.open(tweet_path).convert('RGBA')

        # Tweet area with decent padding on sides
        # Content area: y=180 to y=1400 (height=1220px)
        tweet_area_top = 180
        tweet_area_bottom = 1400
        tweet_area_height = tweet_area_bottom - tweet_area_top  # 1220px

        # Add padding (75px each side - half of previous 150px)
        horizontal_padding = 75
        tweet_area_width = self.width - (horizontal_padding * 2)  # 930px

        # Scale tweet to fit with padding
        tweet_ratio = tweet.width / tweet.height

        # Scale by width first
        new_width = tweet_area_width
        new_height = int(new_width / tweet_ratio)

        # If height is too large, scale by height instead
        if new_height > tweet_area_height:
            new_height = tweet_area_height
            new_width = int(new_height * tweet_ratio)

        tweet_resized = tweet.resize((new_width, new_height), Image.LANCZOS)

        # Center the tweet in the content area
        tweet_x = (self.width - new_width) // 2
        tweet_y = tweet_area_top + (tweet_area_height - new_height) // 2

        canvas.paste(tweet_resized, (tweet_x, tweet_y), tweet_resized)

        # ========== LAYER 2: Character (ON TOP OF TWEET) ==========
        print("[COMPOSITOR] Adding character on top...")

        # Check if character already has no background
        character = Image.open(character_path).convert('RGBA')

        # If character has solid background, remove it
        if character_path.endswith('.png') and 'nobg' not in character_path:
            # Remove background
            temp_nobg = self.output_dir / "temp_character_nobg.png"
            character_nobg_path = self.remove_background(character_path, str(temp_nobg))
            character = Image.open(character_nobg_path).convert('RGBA')

        # Scale character to be prominent but not cover entire tweet
        # Character max size: 600x1000px
        char_max_height = 1000
        char_max_width = 600

        # Resize maintaining aspect ratio
        char_ratio = character.width / character.height
        if char_ratio > (char_max_width / char_max_height):
            new_width = char_max_width
            new_height = int(char_max_width / char_ratio)
        else:
            new_height = char_max_height
            new_width = int(char_max_height * char_ratio)

        character_resized = character.resize((new_width, new_height), Image.LANCZOS)

        # Position character on LEFT side (instead of centered)
        # This makes it look like they're presenting the tweet from the side
        char_x = 50  # 50px from left edge
        char_y = 600  # Start at 600px from top

        canvas.paste(character_resized, (char_x, char_y), character_resized)

        # ========== LAYER 3: Bottom Ticker ==========
        print("[COMPOSITOR] Adding ticker...")
        ticker = Image.open(ticker_path).convert('RGBA')

        # Position ticker at the BORDER between white and black areas
        # White area ends at 1400px, black area starts at 1400px
        # We want ticker right at this border, on top of black background
        ticker_y = 1400  # Exactly at the white/black border
        ticker_height = 120  # Increased from 100px to match new ticker generator height

        # Crop ticker to fit width and height
        if ticker.height != ticker_height:
            ticker = ticker.resize((ticker.width, ticker_height), Image.LANCZOS)

        # Create scrolling effect by taking a section from the ticker
        ticker_section_width = self.width
        if ticker.width >= ticker_section_width:
            # Crop from the beginning (you can animate this later)
            ticker_cropped = ticker.crop((0, 0, ticker_section_width, ticker_height))
        else:
            # If ticker is narrower, tile it
            ticker_tiled = Image.new('RGBA', (ticker_section_width, ticker_height), (0, 0, 0, 255))
            x_offset = 0
            while x_offset < ticker_section_width:
                ticker_tiled.paste(ticker, (x_offset, 0), ticker)
                x_offset += ticker.width
            ticker_cropped = ticker_tiled

        # Paste ticker
        canvas.paste(ticker_cropped, (0, ticker_y), ticker_cropped)

        # ========== Save composed frame ==========
        output_path = self.output_dir / output_filename

        # Convert back to RGB for final save (no alpha)
        final = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        final.paste(canvas, (0, 0), canvas)

        final.save(output_path, 'PNG', quality=100)

        print(f"\n[OK] Frame composed: {output_path}")
        print(f"     Layers: Studio BG + Character + Tweet + Ticker")
        print(f"     Dimensions: {self.width}x{self.height}px")

        return str(output_path)


async def main():
    """Example usage"""
    compositor = FrameCompositor()

    # Paths (update these to your actual files)
    studio_bg = "output/financial_shorts/studio_background.png"
    character = "src/image/base_image.png"
    tweet = "output/tweet_screenshots/selected_tweet.png"
    ticker = "output/financial_shorts/ticker_strip.png"

    # Compose frame
    frame_path = compositor.compose_frame(
        studio_bg_path=studio_bg,
        character_path=character,
        tweet_path=tweet,
        ticker_path=ticker,
        output_filename="preview_frame.png"
    )

    print(f"\n[OK] Preview frame: {frame_path}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
