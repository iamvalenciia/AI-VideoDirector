import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def create_ticker_background_image(width: int, height: int, output_path: str) -> str:
    """
    Generates a static ticker background image with XInsight branding.

    Args:
        width (int): Width of the ticker in pixels.
        height (int): Height of the ticker in pixels.
        output_path (str): File path where the PNG will be saved.

    Returns:
        str: Final path to the saved image.
    """

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ---- HTML TEMPLATE ----
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    body {{
        width: {width}px;
        height: {height}px;
        background-color: #000000;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        overflow: hidden;
    }}

    .ticker-container {{
        width: 100%;
        height: 100%;
        background: linear-gradient(180deg, #0a0a0a 0%, #000000 100%);
        border-top: 2px solid #1a1a1a;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        position: relative;
    }}

    /* Logo Section */
    .logo-section {{
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
        padding: 0 {int(height * 0.3)}px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-right: 3px solid #00ff88;
        box-shadow: 4px 0 12px rgba(0, 0, 0, 0.6);
        z-index: 10;
    }}

    .logo-text {{
        font-size: {int(height * 0.35)}px;
        font-weight: 900;
        letter-spacing: 2px;
        display: flex;
        align-items: center;
        white-space: nowrap;
    }}

    .logo-text .x-letter {{
        color: #00ff88;
        text-shadow: 
            0 0 10px rgba(0, 255, 136, 0.5),
            0 0 20px rgba(0, 255, 136, 0.3),
            0 2px 4px rgba(0, 0, 0, 0.8);
        margin-right: -2px;
    }}

    .logo-text .insight {{
        color: #ffffff;
        text-shadow: 
            0 2px 4px rgba(0, 0, 0, 0.8),
            0 0 8px rgba(255, 255, 255, 0.1);
    }}

    /* Accent Line After Logo */
    .accent-line {{
        position: absolute;
        left: {int(height * 0.3 * 2 + 80)}px;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #00ff88 0%, transparent 100%);
        top: 50%;
        transform: translateY(-50%);
        opacity: 0.6;
    }}

    /* Subtle gradient overlay for depth */
    .ticker-container::after {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, 
            rgba(0,0,0,0.4) 0%, 
            transparent 250px, 
            transparent calc(100% - 100px), 
            rgba(0,0,0,0.3) 100%
        );
        pointer-events: none;
    }}

    /* Subtle scanline effect */
    .ticker-container::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(255, 255, 255, 0.02) 2px,
            rgba(255, 255, 255, 0.02) 4px
        );
        pointer-events: none;
    }}

    /* Corner accent */
    .corner-accent {{
        position: absolute;
        bottom: 0;
        right: 0;
        width: 100px;
        height: 100%;
        background: linear-gradient(90deg, transparent 0%, rgba(0, 255, 136, 0.05) 100%);
        pointer-events: none;
    }}
</style>
</head>
<body>
    <div class="ticker-container">
        <div class="logo-section">
            <div class="logo-text">
                <span class="x-letter">X</span><span class="insight">INSIGHT</span>
            </div>
        </div>
        <div class="accent-line"></div>
        <div class="corner-accent"></div>
    </div>
</body>
</html>
"""

    # ---- PLAYWRIGHT RENDER ----
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=3  # Higher quality for crisp rendering
        )

        await page.set_content(html_content)
        await asyncio.sleep(0.5)  # Allow layout to settle

        await page.screenshot(path=str(output_path), type="png", full_page=True)
        await browser.close()

    print(f"✅ Ticker background saved: {output_path}")
    return str(output_path)


# Example usage
async def main():
    await create_ticker_background_image(
        width=1920,
        height=80,
        output_path="output/ticker_background.png"
    )


if __name__ == "__main__":
    asyncio.run(main())