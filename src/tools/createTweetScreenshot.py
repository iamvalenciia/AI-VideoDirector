"""
Tweet Screenshot Generator
Creates realistic tweet images from tweet data using HTML/CSS rendering
No API needed - fully local generation
"""

import os
from typing import Dict, Optional
from datetime import datetime
import base64
import requests
import asyncio
from playwright.async_api import async_playwright


async def generate_tweet_screenshot(
    tweet_data: Dict,
    output_path: str,
    max_content_length: int = 316,
    show_ellipsis: bool = True,
    device_scale_factor: int = 2
) -> str:
    """
    Generate a tweet screenshot from tweet data
    
    Args:
        tweet_data: Dictionary containing tweet information with keys:
            - content (str): Tweet text
            - username (str): Twitter username
            - name (str): Display name
            - verify_type (str): 'blue', 'orange', or 'none'
            - profile_picture_link (str): URL to profile picture
            - views (int): Number of views
            - likes (int): Number of likes
            - retweets (int): Number of retweets
            - replies (int): Number of replies
            - posted_date (str): ISO format date string
        output_path: Full path where the screenshot will be saved (including .png extension)
        device_scale_factor: Scale factor for rendering quality (default: 2 for high-res)
    
    Returns:
        str: Path to the generated screenshot
    
    Example:
        tweet_data = {
            "content": "This is my tweet!",
            "username": "johndoe",
            "name": "John Doe",
            "verify_type": "blue",
            "profile_picture_link": "https://...",
            "views": 1000000,
            "likes": 50000,
            "retweets": 10000,
            "replies": 2000,
            "posted_date": "2025-11-18T14:30:00"
        }
        await generate_tweet_screenshot(tweet_data, "output/my_tweet.png")
    """
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Helper function: Download image as base64
    def download_image_as_base64(url: str) -> Optional[str]:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            img_data = base64.b64encode(response.content).decode('utf-8')
            
            # Detect image type
            img_type = 'jpeg'
            if '.png' in url.lower():
                img_type = 'png'
            elif '.webp' in url.lower():
                img_type = 'webp'
            
            return f"data:image/{img_type};base64,{img_data}"
        except Exception as e:
            print(f"⚠️ Failed to download image from {url}: {str(e)}")
            return None
    
    # Helper function: Get verification badge SVG
    def get_verification_badge(verify_type: str) -> str:
        badges = {
            "blue": '''<svg viewBox="0 0 22 22" aria-label="Verified account" role="img" class="verify-badge blue">
                <g><path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.606-.274 1.263-.144 1.896.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z"></path></g>
            </svg>''',
            "orange": '''<svg viewBox="0 0 22 22" aria-label="Verified Organization" role="img" class="verify-badge orange">
                <g><path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.606-.274 1.263-.144 1.896.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z"></path></g>
            </svg>'''
        }
        return badges.get(verify_type, "")
    
    # Helper function: Format numbers
    def format_number(num: int) -> str:
        if num >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.1f}K"
        return str(num)
    
    # Download profile picture
    profile_pic_base64 = download_image_as_base64(tweet_data.get('profile_picture_link', ''))
    profile_pic_src = profile_pic_base64 if profile_pic_base64 else 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"%3E%3Cpath fill="%23536471" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/%3E%3C/svg%3E'
    
    # Format stats
    views = format_number(tweet_data.get('views', 0))
    likes = format_number(tweet_data.get('likes', 0))
    retweets = format_number(tweet_data.get('retweets', 0))
    replies = format_number(tweet_data.get('replies', 0))
    
    # Format date
    try:
        posted_date = datetime.fromisoformat(tweet_data.get('posted_date', ''))
        date_str = posted_date.strftime('%I:%M %p · %b %d, %Y')
    except:
        date_str = datetime.now().strftime('%I:%M %p · %b %d, %Y')
    
    verification_badge = get_verification_badge(tweet_data.get('verify_type', 'none'))
    
    # Truncar contenido del tweet si es necesario
    original_content = tweet_data.get('content', '')
    tweet_content = original_content

    if len(tweet_content) > max_content_length:
        # Truncar al límite especificado
        tweet_content = tweet_content[:max_content_length]
        
        # Buscar el último espacio para no cortar palabras
        last_space = tweet_content.rfind(' ')
        if last_space > 0:
            tweet_content = tweet_content[:last_space]
        
        # Agregar puntos suspensivos si está habilitado
        if show_ellipsis:
            tweet_content = tweet_content + "..."
        
        print(f"[TWEET TRUNCATED] Original: {len(original_content)} chars → Truncated: {len(tweet_content)} chars")
    
    # Create HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tweet Screenshot</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 40px;
        }}

        .tweet-container {{
            background-color: #ffffff;
            max-width: 600px;
            width: 100%;
            border: 1px solid #eff3f4;
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 0 15px rgba(101, 119, 134, 0.15);
        }}

        .tweet-header {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 12px;
        }}

        .profile-pic {{
            width: 48px;
            height: 48px;
            border-radius: 50%;
            margin-right: 12px;
            flex-shrink: 0;
        }}

        .user-info {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}

        .user-names {{
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        .display-name {{
            color: #0f1419;
            font-weight: 700;
            font-size: 15px;
        }}

        .verify-badge {{
            width: 20px;
            height: 20px;
            flex-shrink: 0;
        }}

        .verify-badge.blue {{
            fill: #1d9bf0;
        }}

        .verify-badge.orange {{
            fill: #ffd400;
        }}

        .username {{
            color: #536471;
            font-size: 15px;
        }}

        .tweet-content {{
            color: #0f1419;
            font-size: 23px;
            line-height: 28px;
            margin-bottom: 12px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .tweet-date {{
            color: #536471;
            font-size: 15px;
            margin-bottom: 16px;
            padding-bottom: 16px;
            border-bottom: 1px solid #eff3f4;
        }}

        .tweet-stats {{
            display: flex;
            gap: 20px;
            margin-bottom: 16px;
            padding-bottom: 16px;
            border-bottom: 1px solid #eff3f4;
        }}

        .stat {{
            display: flex;
            gap: 4px;
            color: #536471;
            font-size: 15px;
        }}

        .stat-value {{
            color: #0f1419;
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <div class="tweet-container">
        <div class="tweet-header">
            <img src="{profile_pic_src}" alt="Profile" class="profile-pic">
            <div class="user-info">
                <div class="user-names">
                    <span class="display-name">{tweet_data.get('name', 'User')}</span>
                    {verification_badge}
                </div>
                <span class="username">@{tweet_data.get('username', 'username')}</span>
            </div>
        </div>

        <div class="tweet-content">{tweet_content}</div>

        <div class="tweet-date">{date_str}</div>

        <div class="tweet-stats">
            <div class="stat">
                <span class="stat-value">{views}</span>
                <span>Views</span>
            </div>
            <div class="stat">
                <span class="stat-value">{retweets}</span>
                <span>Reposts</span>
            </div>
            <div class="stat">
                <span class="stat-value">{likes}</span>
                <span>Likes</span>
            </div>
            <div class="stat">
                <span class="stat-value">{replies}</span>
                <span>Replies</span>
            </div>
        </div>
    </div>
</body>
</html>'''
    
    # Render with Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={'width': 1200, 'height': 1600},
            device_scale_factor=device_scale_factor
        )
        
        await page.set_content(html_content)
        await asyncio.sleep(1)  # Wait for fonts to load
        
        tweet_element = await page.query_selector('.tweet-container')
        await tweet_element.screenshot(
            path=output_path,
            type='png',
            omit_background=False
        )
        
        await browser.close()
    
    print(f"✅ Screenshot saved: {output_path}")
    return output_path