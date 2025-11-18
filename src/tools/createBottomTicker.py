"""
Bloomberg-Style Bottom Ticker Generator
Creates crisp, vector-like ticker images with market data
"""

import os
from typing import List, Dict
from playwright.async_api import async_playwright
import asyncio


async def generate_bottom_ticker(
    stocks: List[Dict],
    output_path: str,
    width: int = 1920,
    height: int = 80,
    device_scale_factor: int = 3
) -> str:
    """
    Generate Bloomberg-style bottom ticker image with stock data
    
    Args:
        stocks: List of stock dictionaries with keys:
            - symbol (str): Stock symbol (e.g., "AAPL")
            - company_name (str): Full company name
            - price (float): Current price
            - change (float): Price change
            - change_percent (float): Percentage change
        output_path: Full path where the image will be saved (including .png extension)
        width: Width of the ticker in pixels (default: 1920 for Full HD)
        height: Height of the ticker in pixels (default: 80)
        device_scale_factor: Scale factor for crisp rendering (default: 3 for vector-like quality)
    
    Returns:
        str: Path to the generated ticker image
    
    Example:
        stocks = [
            {
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "price": 185.50,
                "change": 2.30,
                "change_percent": 1.26
            }
        ]
        await generate_bottom_ticker(stocks, "output/ticker.png", width=1920, height=80)
    """
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Calculate how many times to repeat stocks to fill the width
    # Each stock item is approximately 280px wide
    stock_item_width = 280
    repeats_needed = (width // stock_item_width) + 3  # +3 for smooth looping
    
    # Repeat stock list to fill the ticker
    repeated_stocks = (stocks * repeats_needed)[:repeats_needed * len(stocks)]
    
    # Generate stock items HTML
    stock_items_html = ""
    for stock in repeated_stocks:
        change = stock['change']
        change_percent = stock['change_percent']
        is_positive = change >= 0
        
        arrow = "▲" if is_positive else "▼"
        color_class = "positive" if is_positive else "negative"
        sign = "+" if is_positive else ""
        
        stock_items_html += f'''
        <div class="stock-item">
            <span class="symbol">{stock['symbol']}</span>
            <span class="price">{stock['price']:.2f}</span>
            <span class="change {color_class}">
                {arrow} {sign}{change:.2f} ({sign}{change_percent:.2f}%)
            </span>
        </div>
        '''
    
    # Create HTML with vector-quality styling
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bottom Ticker</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Helvetica Neue', 'Arial', sans-serif;
            background-color: #000000;
            overflow: hidden;
            width: {width}px;
            height: {height}px;
        }}

        .ticker-container {{
            background: linear-gradient(180deg, #0a0a0a 0%, #000000 100%);
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            position: relative;
            overflow: hidden;
            border-top: 2px solid #1a1a1a;
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.8);
        }}

        .ticker-content {{
            display: flex;
            align-items: center;
            height: 100%;
            gap: 0;
        }}

        .stock-item {{
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 0 20px;
            height: 100%;
            border-right: 1px solid #2a2a2a;
            flex-shrink: 0;
            white-space: nowrap;
        }}

        .symbol {{
            color: #ffffff;
            font-size: {int(height * 0.32)}px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
        }}

        .price {{
            color: #e0e0e0;
            font-size: {int(height * 0.30)}px;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}

        .change {{
            font-size: {int(height * 0.26)}px;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 4px;
            letter-spacing: 0.3px;
        }}

        .change.positive {{
            color: #00ff88;
            background-color: rgba(0, 255, 136, 0.15);
            text-shadow: 0 0 8px rgba(0, 255, 136, 0.3);
        }}

        .change.negative {{
            color: #ff3366;
            background-color: rgba(255, 51, 102, 0.15);
            text-shadow: 0 0 8px rgba(255, 51, 102, 0.3);
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
                rgba(0,0,0,0.3) 0%, 
                transparent 100px, 
                transparent calc(100% - 100px), 
                rgba(0,0,0,0.3) 100%
            );
            pointer-events: none;
        }}
    </style>
</head>
<body>
    <div class="ticker-container">
        <div class="ticker-content">
            {stock_items_html}
        </div>
    </div>
</body>
</html>'''
    
    # Render with Playwright at very high resolution for vector-like quality
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={'width': width, 'height': height},
            device_scale_factor=device_scale_factor  # 3x for ultra-crisp rendering
        )
        
        await page.set_content(html_content)
        await asyncio.sleep(0.5)  # Wait for rendering
        
        # Take full page screenshot
        await page.screenshot(
            path=output_path,
            type='png',
            full_page=False,
            omit_background=False
        )
        
        await browser.close()
    
    print(f"✅ Bottom ticker saved: {output_path}")
    return output_path


# Example usage
async def main():
    stocks = [
        {
            "symbol": "BRK.B",
            "company_name": "Berkshire Hathaway",
            "price": 458.32,
            "change": -5.67,
            "change_percent": -1.22
        },
        {
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "price": 225.12,
            "change": -2.34,
            "change_percent": -1.03
        },
        {
            "symbol": "SPY",
            "company_name": "S&P 500 ETF",
            "price": 589.45,
            "change": -8.23,
            "change_percent": -1.38
        },
        {
            "symbol": "TLT",
            "company_name": "20+ Year Treasury ETF",
            "price": 91.78,
            "change": 0.45,
            "change_percent": 0.49
        }
    ]
    
    # Generate Full HD ticker
    await generate_bottom_ticker(
        stocks=stocks,
        output_path="output/bottom_ticker.png",
        width=1920,
        height=80,
        device_scale_factor=3
    )
