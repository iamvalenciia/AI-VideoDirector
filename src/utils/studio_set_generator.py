"""
Studio Set Generator - Professional News Studio Background
Creates clean, minimalist newsroom-style backgrounds for financial shorts
Inspired by modern financial news channels (Bloomberg, CNBC style)
"""

from pathlib import Path
from playwright.async_api import async_playwright
import asyncio
import os


class StudioSetGenerator:
    """
    Generates professional studio newsroom backgrounds using HTML/CSS
    Rendered to high-quality PNG images using Playwright
    """

    def __init__(self, output_dir: str = "output/financial_shorts"):
        """
        Initialize the studio set generator

        Args:
            output_dir: Directory to save generated backgrounds
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # YouTube Shorts dimensions
        self.width = 1080
        self.height = 1920

    def _create_newsroom_html(self, branding_text: str = "XINSIDER") -> str:
        """
        Create HTML/CSS for newsroom studio background

        Args:
            branding_text: Text to display as channel branding

        Returns:
            HTML string
        """
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Studio Background</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            width: {self.width}px;
            height: {self.height}px;
            background: #ffffff;
            font-family: 'Arial', 'Helvetica', sans-serif;
            overflow: hidden;
            position: relative;
        }}

        /* Top area - White background */
        .top-area {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 180px;
            background: #ffffff;
        }}

        /* Branding removed - top area is now plain white */

        /* Bottom area - Completely black (ticker + YouTube UI space) */
        /* Reduced to 150px (71% reduction from original 520px) */
        .bottom-area {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 150px;
            background: #000000;
        }}

        /* Bottom bar removed - eliminating second black stripe */
    </style>
</head>
<body>
    <!-- Top area - White (no branding) -->
    <div class="top-area"></div>

    <!-- Bottom area - Black (ticker + YouTube UI) -->
    <div class="bottom-area"></div>
</body>
</html>'''

        return html

    async def generate_studio_background(
        self,
        branding_text: str = "XINSIDER",
        output_filename: str = "studio_background.png"
    ) -> str:
        """
        Generate studio newsroom background image

        Args:
            branding_text: Channel branding text
            output_filename: Output filename

        Returns:
            Path to generated background image
        """
        print(f"\n[STUDIO] Generating newsroom background...")

        # Create HTML
        html_content = self._create_newsroom_html(branding_text)

        output_path = self.output_dir / output_filename

        # Render with Playwright at high resolution
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(
                viewport={'width': self.width, 'height': self.height},
                device_scale_factor=2  # High quality rendering
            )

            # Load HTML
            await page.set_content(html_content)

            # Wait for rendering
            await asyncio.sleep(0.5)

            # Take screenshot
            await page.screenshot(
                path=str(output_path),
                type='png',
                full_page=True
            )

            await browser.close()

        print(f"[OK] Studio background created: {output_path}")
        print(f"     Dimensions: {self.width}x{self.height}px")
        print(f"     Style: Professional newsroom (black & white)")

        return str(output_path)


async def main():
    """Example usage"""
    generator = StudioSetGenerator()
    background_path = await generator.generate_studio_background(
        branding_text="XINSIDER"
    )
    print(f"\n[OK] Background image: {background_path}")


if __name__ == "__main__":
    asyncio.run(main())
