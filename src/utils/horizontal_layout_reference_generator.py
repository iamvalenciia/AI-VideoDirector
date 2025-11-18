"""
Horizontal Layout Reference Generator
Creates reference image showing the layout structure for long-format videos
Two squares: left for character, right for illustrations
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import os


class HorizontalLayoutReferenceGenerator:
    """
    Generates layout reference image for horizontal videos (1920x1080)
    """

    def __init__(self, output_dir: str = "output/horizontal_videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Video dimensions
        self.width = 1920
        self.height = 1080

    def _load_font(self, size: int = 24):
        """Load font, fallback to default if custom not available"""
        try:
            # Try to load Arial (common on Windows)
            return ImageFont.truetype("arial.ttf", size)
        except IOError:
            try:
                # Try to load Arial (common on macOS/Linux)
                return ImageFont.truetype("Arial.ttf", size)
            except IOError:
                # Fallback to default PIL font
                return ImageFont.load_default()
            
    BASE_DIR = Path(__file__).resolve().parent.parent

    def generate_layout_reference(
        self,
        output_filename: str = "horizontal_layout_reference.png",
        BASE_DIR: Path = BASE_DIR
    ) -> str:
        """
        Generate layout reference image

        Layout structure:
        - Top section: Two squares (character left, illustration right)
        - Middle section: Captions under character + Title under character box
        - Bottom section: Ticker background + animated ticker

        Returns:
            Path to generated reference image
        """
        print(f"\n[LAYOUT] Generating horizontal layout reference...")

        # Create white canvas
        img = Image.new('RGB', (self.width, self.height), (255, 255, 255))
        draw = ImageDraw.Draw(img)

        # Fonts
        title_font = self._load_font(32)
        label_font = self._load_font(24)
        small_font = self._load_font(18)

        # Colors
        black = (0, 0, 0)
        gray = (150, 150, 150)
        light_gray = (220, 220, 220)

        ticker_bg_height = 74

        # ==================== CENTERED SQUARES ====================
        # Square dimensions
        square_size = 500
        gap_between_squares = 120  # Gap between the two squares

        # Calculate total width of both squares + gap
        total_squares_width = (square_size * 2) + gap_between_squares

        # Center both squares horizontally
        start_x = (self.width - total_squares_width) // 2
        
        # Center both squares vertically on the *entire* screen
        start_y = ((self.height - square_size) // 2) - 100 # Move squares and captions up

        # Left square (character)
        left_square_x = start_x
        left_square_y = start_y

        # Draw left square (character area)
        draw.rectangle(
            [left_square_x, left_square_y,
             left_square_x + square_size, left_square_y + square_size],
            outline=black,
            width=4
        )

        # Label for left square
        draw.text(
            (left_square_x + square_size//2, left_square_y + square_size//2),
            "CHARACTER\nWITH NO\nBACKGROUND",
            fill=gray,
            font=label_font,
            anchor="mm",
            align="center"
        )

        # Right square (illustration)
        right_square_x = left_square_x + square_size + gap_between_squares
        right_square_y = start_y

        # Draw right square (illustration area)
        draw.rectangle(
            [right_square_x, right_square_y,
             right_square_x + square_size, right_square_y + square_size],
            outline=black,
            width=4
        )

        # Label for right square
        draw.text(
            (right_square_x + square_size//2, right_square_y + square_size//2),
            "ILLUSTRATION\n(B&W AI ART)",
            fill=gray,
            font=label_font,
            anchor="mm",
            align="center"
        )

        # ==================== CAPTIONS AREA ====================
        # Below left square only
        captions_y = left_square_y + square_size + 20
        captions_height = 80

        # Draw captions area (only under character, left side)
        draw.rectangle(
            [left_square_x, captions_y,
             left_square_x + square_size, captions_y + captions_height],
            outline=light_gray,
            fill=(250, 250, 250),
            width=2
        )

        # Label for captions
        draw.text(
            (left_square_x + square_size//2, captions_y + captions_height//2),
            "WORD-LEVEL CAPTIONS\n(karaoke style)",
            fill=gray,
            font=small_font,
            anchor="mm",
            align="center"
        )

        # ==================== TITLE AREA ====================
        # Full width, above ticker
        title_height = 100
        title_y = self.height - ticker_bg_height - title_height  # 10px margin

        # Draw title area (full width)
        draw.rectangle(
            [0, title_y, self.width, title_y + title_height],
            outline=black,
            fill=(245, 245, 245),
            width=3
        )

        # Label for title
        draw.text(
            (self.width//2, title_y + 30),
            "VIDEO TITLE (FULL WIDTH)",
            fill=black,
            font=title_font,
            anchor="mm"
        )
        draw.text(
            (self.width//2, title_y + 70),
            "The Truth About Elon's  Trillion Tesla Pay Package",
            fill=gray,
            font=small_font,
            anchor="mm"
        )
        draw.text(
            (self.width//2, title_y + 95),
            "(from financial_analysis.json - video_title)",
            fill=light_gray,
            font=self._load_font(14),
            anchor="mm"
        )

        # ==================== TICKER BACKGROUND ====================
        ticker_bg_y = self.height - ticker_bg_height

        ticker_bg_path = BASE_DIR / "utils" / "output" / "horizontal_videos" / "horizontal_ticker_background.png"

        if ticker_bg_path.exists():
            try:
                ticker_bg_img = Image.open(ticker_bg_path).convert("RGBA")
                ticker_bg_img = ticker_bg_img.resize((self.width, ticker_bg_height), Image.LANCZOS)
                img.paste(ticker_bg_img, (0, ticker_bg_y), ticker_bg_img)
            except Exception as e:
                print(f"[WARNING] Could not load ticker background: {e}")
                draw.rectangle([0, ticker_bg_y, self.width, self.height], fill=(0, 0, 0))
        else:
            print(f"[WARNING] Missing ticker background image → using black fallback.")
            draw.rectangle([0, ticker_bg_y, self.width, self.height], fill=(0, 0, 0))

        # ==================== TICKER FOREGROUND ====================
        ticker_width = int(self.width * 0.80)
        ticker_x = self.width - ticker_width
        ticker_y = ticker_bg_y

        ticker_path = BASE_DIR / "utils" / "output" / "horizontal_videos" / "test_horizontal_ticker.png"

        if ticker_path.exists():
            try:
                ticker_img = Image.open(ticker_path).convert("RGBA")
                ticker_img = ticker_img.resize((ticker_width, ticker_bg_height), Image.LANCZOS)
                img.paste(ticker_img, (ticker_x, ticker_y), ticker_img)
            except Exception as e:
                print(f"[WARNING] Could not load ticker foreground: {e}")
        else:
            print(f"[WARNING] Missing ticker image → skipping ticker layer.")


        # ==================== ANNOTATIONS ====================
        # Add dimension annotations
        annotation_font = self._load_font(16)

        # Width annotations
        draw.text((self.width//2, 25), f"Total: {self.width}px", fill=gray, font=annotation_font, anchor="mm")
        draw.text((left_square_x + square_size//2, 40), f"{square_size}px", fill=gray, font=annotation_font, anchor="mm")
        draw.text((right_square_x + square_size//2, 40), f"{square_size}px", fill=gray, font=annotation_font, anchor="mm")
        draw.text(((left_square_x + square_size + right_square_x)//2, left_square_y + square_size//2),
                 f"{gap_between_squares}px gap", fill=light_gray, font=annotation_font, anchor="mm", angle=90)

        # Height annotation
        draw.text((30, self.height//2), f"{self.height}px", fill=gray, font=annotation_font, anchor="mm", angle=90)

        # Ticker height
        draw.text((self.width - 100, ticker_bg_y - 15), f"{ticker_bg_height}px", fill=gray, font=annotation_font, anchor="mm")

        # Title height
        draw.text((30, title_y + title_height//2), f"{title_height}px", fill=gray, font=annotation_font, anchor="lm")

        # ==================== SAVE ====================
        output_path = self.output_dir / output_filename
        img.save(output_path, 'PNG', quality=95)

        print(f"[OK] Layout reference: {output_path}")
        print(f"     Dimensions: {self.width}x{self.height}px")
        print(f"     Layout: Two-column (character + illustration)")

        return str(output_path)


def main():
    """Example usage"""
    generator = HorizontalLayoutReferenceGenerator()

    try:
        layout_path = generator.generate_layout_reference()
        print(f"\n[SUCCESS] Layout reference generated: {layout_path}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()