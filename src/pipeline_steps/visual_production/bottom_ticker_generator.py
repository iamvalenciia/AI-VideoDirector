"""
Bottom Ticker Generator - Financial News Style
Creates a long horizontal ticker image that can scroll across the bottom of the video
"""

from pathlib import Path
from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont
import os


class BottomTickerGenerator:
    """
    Generates a horizontal ticker strip showing stock prices
    Designed to be scrolled horizontally in the video (right to left loop)
    """

    def __init__(self, output_dir: str = "output/financial_shorts"):
        """
        Initialize the ticker generator

        Args:
            output_dir: Directory to save generated ticker images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Ticker dimensions (for 1080x1920 vertical video)
        self.ticker_height = 120  # Height of ticker bar (increased from 80px for better quality)
        self.video_width = 1080  # YouTube Shorts width

        # Styling (news channel aesthetic - black & white clean)
        self.bg_color = (0, 0, 0)  # Black background
        self.text_color = (255, 255, 255)  # White text
        self.positive_color = (34, 197, 94)  # Green for positive change
        self.negative_color = (239, 68, 68)  # Red for negative change
        self.separator_color = (64, 64, 64)  # Dark gray separator

    def _get_font(self, size: int):
        """
        Get font for rendering

        Args:
            size: Font size

        Returns:
            ImageFont object
        """
        try:
            # Try to use a professional font
            return ImageFont.truetype("arial.ttf", size)
        except:
            try:
                return ImageFont.truetype("Arial.ttf", size)
            except:
                # Fallback to default
                return ImageFont.load_default()

    def create_ticker_image(
        self,
        stocks: List[Dict],
        output_filename: str = "ticker_strip.png"
    ) -> str:
        """
        Create a long horizontal ticker image with all stocks

        The image will be wider than the screen so it can scroll

        Args:
            stocks: List of stock dictionaries with 'symbol', 'price', 'change_percent'
            output_filename: Output filename

        Returns:
            Path to generated ticker image
        """
        if not stocks:
            print("[WARNING] No stocks provided for ticker")
            return None

        print(f"\n[TICKER] Creating bottom ticker with {len(stocks)} stocks...")

        # Calculate width needed for all stocks
        # Each stock entry: SYMBOL $PRICE ±CHANGE% |
        stock_width = 450  # Approximate width per stock (increased for larger fonts)
        # Make it 18x wider than screen for smooth scrolling loop (TRIPLED from 6x)
        total_width = max(stock_width * len(stocks), self.video_width * 18)

        # Create image
        img = Image.new('RGB', (total_width, self.ticker_height), self.bg_color)
        draw = ImageDraw.Draw(img)

        # Fonts (increased sizes for better quality)
        symbol_font = self._get_font(36)  # Larger for stock symbol (was 28)
        price_font = self._get_font(32)   # Medium for price (was 24)
        change_font = self._get_font(30)  # Slightly smaller for change (was 22)

        # Draw stocks repeatedly to fill the width (for seamless loop)
        x_position = 20
        stock_index = 0

        while x_position < total_width:
            stock = stocks[stock_index % len(stocks)]

            # Extract data
            symbol = stock.get('symbol', 'N/A')
            price = stock.get('current_price', stock.get('price', 0))
            change_percent = stock.get('change_percent', 0)

            # Format price
            if isinstance(price, (int, float)):
                price_str = f"${price:,.2f}"
            else:
                price_str = f"${price}"

            # Format change with sign
            if isinstance(change_percent, (int, float)):
                if change_percent >= 0:
                    change_str = f"+{change_percent:.2f}%"
                    change_color = self.positive_color
                else:
                    change_str = f"{change_percent:.2f}%"
                    change_color = self.negative_color
            else:
                change_str = f"{change_percent}%"
                change_color = self.text_color

            # Draw symbol (bold, white) - centered vertically
            draw.text((x_position, 35), symbol, fill=self.text_color, font=symbol_font)
            x_position += 140

            # Draw price (white) - centered vertically
            draw.text((x_position, 38), price_str, fill=self.text_color, font=price_font)
            x_position += 160

            # Draw change percent (colored) - centered vertically
            draw.text((x_position, 40), change_str, fill=change_color, font=change_font)
            x_position += 120

            # Draw separator line (taller for new height)
            draw.line(
                [(x_position, 30), (x_position, self.ticker_height - 30)],
                fill=self.separator_color,
                width=3
            )
            x_position += 30

            stock_index += 1

        # Save image
        output_path = self.output_dir / output_filename
        img.save(output_path, 'PNG', quality=100)

        print(f"[OK] Ticker image created: {output_path}")
        print(f"     Dimensions: {total_width}x{self.ticker_height}px")
        print(f"     Stocks included: {len(stocks)}")

        return str(output_path)


def main():
    """Example usage"""
    # Example stock data
    example_stocks = [
        {
            "symbol": "TSLA",
            "current_price": 245.67,
            "change_percent": -2.34
        },
        {
            "symbol": "AAPL",
            "current_price": 178.23,
            "change_percent": 1.56
        },
        {
            "symbol": "NVDA",
            "current_price": 512.89,
            "change_percent": 3.21
        },
        {
            "symbol": "SPY",
            "current_price": 498.45,
            "change_percent": 0.78
        }
    ]

    generator = BottomTickerGenerator()
    ticker_path = generator.create_ticker_image(example_stocks)
    print(f"\n[OK] Ticker image: {ticker_path}")


if __name__ == "__main__":
    main()
