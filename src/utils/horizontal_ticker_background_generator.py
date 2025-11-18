"""
Horizontal Ticker Background Generator
Creates static black background with XInsight branding for long-format videos
Bloomberg-style ticker background (37px height x 1920px width)
"""

from pathlib import Path
from playwright.async_api import async_playwright
import asyncio


class HorizontalTickerBackgroundGenerator:
    """
    Generates static ticker background for horizontal videos (1920x1080)
    Black stripe with XInsight branding (X in green #5eea45, rest in white)
    """

    def __init__(self, output_dir: str = "output/horizontal_videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Ticker dimensions for 1920x1080 video
        self.width = 1920
        self.height = 37  # Ticker height

    def _create_ticker_background_html(self) -> str:
        """
        Create HTML/CSS for ticker background with XInsight branding

        Returns:
            HTML string with ticker background
        """
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ticker Background</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            width: {self.width}px;
            height: {self.height}px;
            background: #000000;
            font-family: 'Arial', 'Helvetica', sans-serif;
            overflow: hidden;
            display: flex;
            align-items: center;
            padding: 0 15px;
        }}

        .ticker-container {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
        }}

        .branding {{
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 1px;
            white-space: nowrap;
            margin-right: 20px;
        }}

        .branding .x-letter {{
            color: #5eea45;
        }}

        .branding .rest {{
            color: #ffffff;
        }}

        /* Subtle separator line */
        .separator {{
            width: 1px;
            height: 24px;
            background: #333333;
            margin-right: 20px;
        }}
    </style>
</head>
<body>
    <div class="ticker-container">
        <div class="branding">
            <span class="x-letter">X</span><span class="rest">Insight</span>
        </div>
        <div class="separator"></div>
    </div>
</body>
</html>'''
        return html

    async def generate_ticker_background(
        self,
        output_filename: str = "horizontal_ticker_background.png"
    ) -> str:
        """
        Generate static ticker background image

        Args:
            output_filename: Output filename

        Returns:
            Path to generated background image
        """
        print(f"\n[TICKER BG] Generating horizontal ticker background...")

        # Create HTML
        html_content = self._create_ticker_background_html()

        output_path = self.output_dir / output_filename

        # Render with Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(
                viewport={'width': self.width, 'height': self.height},
                device_scale_factor=2  # High quality
            )

            # Load HTML
            await page.set_content(html_content)

            # Wait for rendering
            await asyncio.sleep(0.3)

            # Take screenshot
            await page.screenshot(
                path=str(output_path),
                type='png',
                full_page=True
            )

            await browser.close()

        print(f"[OK] Ticker background: {output_path}")
        print(f"     Dimensions: {self.width}x{self.height}px")
        print(f"     Style: Black with XInsight branding")

        return str(output_path)


async def main():
    """Example usage"""
    generator = HorizontalTickerBackgroundGenerator()
    bg_path = await generator.generate_ticker_background()
    print(f"\n[SUCCESS] Ticker background: {bg_path}")


if __name__ == "__main__":
    asyncio.run(main())
