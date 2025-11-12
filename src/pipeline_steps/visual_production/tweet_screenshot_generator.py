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
from io import BytesIO
from playwright.async_api import async_playwright
import asyncio


class TweetScreenshotGenerator:
    """
    Generates realistic tweet screenshots from tweet data
    """

    def __init__(self, output_dir: str = "output/tweet_screenshots"):
        """
        Initialize the generator

        Args:
            output_dir: Directory to save generated screenshots
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _download_image_as_base64(self, url: str) -> Optional[str]:
        """
        Download image and convert to base64 for embedding

        Args:
            url: Image URL

        Returns:
            Base64 encoded image string or None
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            img_data = base64.b64encode(response.content).decode('utf-8')
            # Detect image type from URL
            img_type = 'jpeg'
            if '.png' in url.lower():
                img_type = 'png'
            elif '.webp' in url.lower():
                img_type = 'webp'
            return f"data:image/{img_type};base64,{img_data}"
        except Exception as e:
            print(f"⚠️ Failed to download image from {url}: {str(e)}")
            return None

    def _get_verification_badge(self, verify_type: str) -> str:
        """
        Get verification badge SVG based on type

        Args:
            verify_type: 'blue', 'orange', or 'none'

        Returns:
            SVG badge HTML
        """
        if verify_type == "blue":
            return '''<svg viewBox="0 0 22 22" aria-label="Verified account" role="img" class="verify-badge blue">
                <g><path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.606-.274 1.263-.144 1.896.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z"></path></g>
            </svg>'''
        elif verify_type == "orange":
            return '''<svg viewBox="0 0 22 22" aria-label="Verified Organization" role="img" class="verify-badge orange">
                <g><path d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.606-.274 1.263-.144 1.896.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z"></path></g>
            </svg>'''
        else:
            return ""

    def _create_tweet_html(self, tweet_data: Dict) -> str:
        """
        Create HTML representation of a tweet

        Args:
            tweet_data: Tweet data dictionary

        Returns:
            HTML string
        """
        # Download profile picture
        profile_pic_base64 = self._download_image_as_base64(tweet_data.get('profile_picture_link', ''))
        profile_pic_src = profile_pic_base64 if profile_pic_base64 else 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"%3E%3Cpath fill="%23536471" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08 1.99 0 5.97 1.09 6 3.08-1.29 1.94-3.5 3.22-6 3.22z"/%3E%3C/svg%3E'

        # Format numbers
        def format_number(num):
            if num >= 1_000_000:
                return f"{num / 1_000_000:.1f}M"
            elif num >= 1_000:
                return f"{num / 1_000:.1f}K"
            return str(num)

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

        verification_badge = self._get_verification_badge(tweet_data.get('verify_type', 'none'))

        html = f'''<!DOCTYPE html>
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

        <div class="tweet-content">{tweet_data.get('content', '')}</div>

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

        return html

    async def generate_screenshot(self, tweet_data: Dict, filename: Optional[str] = None) -> str:
        """
        Generate screenshot from tweet data

        Args:
            tweet_data: Tweet data dictionary
            filename: Optional custom filename (without extension)

        Returns:
            Path to generated screenshot
        """
        if not filename:
            username = tweet_data.get('username', 'tweet')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{username}_{timestamp}"

        output_path = os.path.join(self.output_dir, f"{filename}.png")

        # Create HTML
        html_content = self._create_tweet_html(tweet_data)

        # Render with Playwright at high resolution
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            # Increase viewport size for higher resolution
            page = await browser.new_page(
                viewport={'width': 1200, 'height': 1600},
                device_scale_factor=2  # 2x scale for crisp rendering
            )

            # Load HTML
            await page.set_content(html_content)

            # Wait for fonts to load
            await asyncio.sleep(1)

            # Take screenshot at high quality
            tweet_element = await page.query_selector('.tweet-container')
            await tweet_element.screenshot(
                path=output_path,
                type='png',
                omit_background=False
            )

            await browser.close()

        print(f"[OK] Screenshot saved: {output_path}")
        return output_path

    async def generate_screenshots_batch(self, tweets_data: Dict) -> list:
        """
        Generate screenshots for multiple tweets

        Args:
            tweets_data: Dictionary with 'viral_tweets' key

        Returns:
            List of generated screenshot paths
        """
        screenshots = []
        viral_tweets = tweets_data.get('viral_tweets', [])

        for idx, tweet in enumerate(viral_tweets):
            print(f"[SCREENSHOT] Generating screenshot {idx + 1}/{len(viral_tweets)}...")
            screenshot_path = await self.generate_screenshot(tweet, filename=f"tweet_{idx + 1:02d}")
            screenshots.append(screenshot_path)

        print(f"[OK] Generated {len(screenshots)} screenshots!")
        return screenshots


async def main():
    """Example usage"""
    # Example tweet data
    example_tweet = {
        "tweet_link": "https://x.com/BenjaminNorton/status/1987001773253701640",
        "content": "The US economy is not real; it's just a big billionaire Ponzi scheme.\n\n75% of Tesla shareholders approved a $1 TRILLION pay package for Elon Musk.\n\n$1,000,000,000,000.\n\nTesla only made $7.13 billion in net income in 2024.\n\nThis is so stupid it defies basic math and reality itself",
        "username": "BenjaminNorton",
        "name": "Ben Norton",
        "verified": True,
        "verify_type": "blue",
        "profile_picture_link": "https://pbs.twimg.com/profile_images/1778611522828410881/Sq-3OMW8.jpg",
        "views": 5234567,
        "likes": 123456,
        "retweets": 23456,
        "replies": 3456,
        "posted_date": "2025-11-08T14:30:00"
    }

    generator = TweetScreenshotGenerator()
    screenshot_path = await generator.generate_screenshot(example_tweet)
    print(f"Screenshot saved to: {screenshot_path}")


if __name__ == "__main__":
    asyncio.run(main())
