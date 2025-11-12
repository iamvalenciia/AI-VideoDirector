"""
Twitter/Grok AI Scraper Tool
Automates Twitter login and Grok AI interaction to fetch viral financial tweets
"""

import asyncio
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError


class TwitterGrokScraper:
    """
    Scrapes viral financial tweets using Grok AI on Twitter/X
    """

    def __init__(self,
                 twitter_username: Optional[str] = None,
                 twitter_password: Optional[str] = None,
                 headless: bool = False):
        """
        Initialize the scraper

        Args:
            twitter_username: Twitter/X username (will use env var if not provided)
            twitter_password: Twitter/X password (will use env var if not provided)
            headless: Run browser in headless mode
        """
        self.username = twitter_username or os.getenv("TWITTER_USERNAME")
        self.password = twitter_password or os.getenv("TWITTER_PASSWORD")
        self.headless = headless

        if not self.username or not self.password:
            raise ValueError("Twitter credentials not provided. Set TWITTER_USERNAME and TWITTER_PASSWORD environment variables.")

    async def _login_to_twitter(self, page: Page) -> bool:
        """
        Login to Twitter/X

        Args:
            page: Playwright page object

        Returns:
            True if login successful, False otherwise
        """
        try:
            print("🔐 Logging into Twitter/X...")
            await page.goto("https://x.com/i/flow/login", wait_until="networkidle")

            # Enter username
            username_input = await page.wait_for_selector('input[autocomplete="username"]', timeout=10000)
            await username_input.fill(self.username)
            await page.keyboard.press("Enter")
            await asyncio.sleep(2)

            # Enter password
            password_input = await page.wait_for_selector('input[name="password"]', timeout=10000)
            await password_input.fill(self.password)
            await page.keyboard.press("Enter")

            # Wait for home page to load
            await page.wait_for_url("**/home", timeout=15000)
            print("✅ Login successful!")
            return True

        except PlaywrightTimeoutError as e:
            print(f"❌ Login failed: {str(e)}")
            return False

    async def _navigate_to_grok(self, page: Page) -> bool:
        """
        Navigate to Grok AI interface

        Args:
            page: Playwright page object

        Returns:
            True if navigation successful
        """
        try:
            print("🤖 Navigating to Grok AI...")
            # Navigate to Grok - adjust URL based on actual Twitter Grok interface
            await page.goto("https://twitter.com/i/grok", wait_until="networkidle")
            await asyncio.sleep(3)
            print("✅ Grok AI loaded!")
            return True

        except Exception as e:
            print(f"❌ Failed to navigate to Grok: {str(e)}")
            return False

    async def _send_grok_prompt(self, page: Page, prompt: str) -> Optional[str]:
        """
        Send prompt to Grok AI and get response

        Args:
            page: Playwright page object
            prompt: Prompt to send to Grok

        Returns:
            Grok's response text or None if failed
        """
        try:
            print("💬 Sending prompt to Grok AI...")

            # Find and fill the input field (adjust selector based on actual Grok UI)
            input_selector = 'textarea[placeholder*="Ask"], textarea[data-testid="grok-input"], div[contenteditable="true"]'
            input_field = await page.wait_for_selector(input_selector, timeout=10000)
            await input_field.fill(prompt)

            # Send the message
            await page.keyboard.press("Enter")

            # Wait for response (adjust selector based on actual Grok UI)
            print("⏳ Waiting for Grok response...")
            await asyncio.sleep(5)  # Give Grok time to generate response

            # Extract response (adjust selector based on actual Grok UI)
            response_selector = 'div[data-testid="grok-response"], div.grok-message, pre, code'
            response_element = await page.wait_for_selector(response_selector, timeout=30000)
            response_text = await response_element.inner_text()

            print("✅ Received Grok response!")
            return response_text

        except Exception as e:
            print(f"❌ Failed to get Grok response: {str(e)}")
            return None

    def _create_enhanced_prompt(self) -> str:
        """
        Create enhanced prompt for Grok AI to fetch viral financial tweets

        Returns:
            Formatted prompt string
        """
        prompt = """I need your help to find the most viral and impactful tweets from the last 48 hours related to finance, economics, and cryptocurrencies. These tweets will be used to create educational YouTube Shorts for investors and people in the financial world.

Please provide a JSON response with the following structure for each tweet:

{
  "viral_tweets": [
    {
      "tweet_link": "full URL to the tweet",
      "content": "full text of the tweet",
      "username": "twitter handle without @",
      "name": "display name of the user",
      "verified": true/false,
      "verify_type": "blue" or "orange" or "none",
      "profile_picture_link": "direct URL to profile picture",
      "views": number of views,
      "likes": number of likes,
      "retweets": number of retweets,
      "replies": number of replies,
      "engagement_rate": calculated engagement percentage,
      "posted_date": "ISO format timestamp",
      "related_stocks": [
        {
          "symbol": "TSLA",
          "price": 242.50,
          "change": 5.30,
          "change_percent": "2.23"
        }
      ],
      "top_comments": [
        {
          "username": "commenter handle",
          "name": "commenter name",
          "comment_text": "comment content",
          "likes": number of likes on comment,
          "verified": true/false
        }
      ]
    }
  ],
  "search_metadata": {
    "search_date": "ISO timestamp",
    "total_tweets_found": number,
    "search_keywords": ["finance", "crypto", etc.],
    "timeframe": "last 48 hours"
  }
}

Requirements:
1. Find tweets with MINIMUM 100k views
2. Focus on tweets about: market crashes/rallies, major economic policy, cryptocurrency movements, stock market volatility, influential investor opinions, financial scandals, economic indicators
3. Include top 3 most-liked comments for each tweet
4. Identify stock tickers, crypto symbols, or companies mentioned and provide CURRENT market data:
   - For "related_stocks", include up to 4 most relevant tickers with:
     * symbol: Stock ticker (e.g., "TSLA", "BTC", "SPY")
     * price: Current price in USD
     * change: Dollar change from previous close
     * change_percent: Percentage change as string (e.g., "2.23" or "-2.81")
5. Calculate engagement rate as: (likes + retweets + replies) / views * 100
6. Prioritize tweets with high engagement AND informational value for investors
7. Exclude pure memes or jokes without financial substance
8. Include tweets in English or with English translations

Please return ONLY the JSON, no additional text."""

        return prompt

    async def fetch_viral_tweets(self, custom_prompt: Optional[str] = None) -> Optional[Dict]:
        """
        Main method to fetch viral financial tweets via Grok AI

        Args:
            custom_prompt: Optional custom prompt (uses default if not provided)

        Returns:
            Dictionary with viral tweets data or None if failed
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()

            try:
                # Login to Twitter
                if not await self._login_to_twitter(page):
                    return None

                # Navigate to Grok
                if not await self._navigate_to_grok(page):
                    return None

                # Send prompt and get response
                prompt = custom_prompt or self._create_enhanced_prompt()
                response = await self._send_grok_prompt(page, prompt)

                if not response:
                    return None

                # Parse JSON response
                try:
                    # Clean response - remove markdown code blocks if present
                    cleaned_response = response.strip()
                    if cleaned_response.startswith("```json"):
                        cleaned_response = cleaned_response[7:]
                    if cleaned_response.startswith("```"):
                        cleaned_response = cleaned_response[3:]
                    if cleaned_response.endswith("```"):
                        cleaned_response = cleaned_response[:-3]

                    tweet_data = json.loads(cleaned_response.strip())
                    print(f"✅ Successfully parsed {len(tweet_data.get('viral_tweets', []))} tweets!")
                    return tweet_data

                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse JSON response: {str(e)}")
                    print(f"Raw response: {response[:500]}...")
                    return None

            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                return None

            finally:
                await browser.close()

    async def save_tweets_to_file(self, output_path: str, custom_prompt: Optional[str] = None):
        """
        Fetch tweets and save to JSON file

        Args:
            output_path: Path to save JSON file
            custom_prompt: Optional custom prompt
        """
        tweets_data = await self.fetch_viral_tweets(custom_prompt)

        if tweets_data:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(tweets_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Tweets saved to {output_path}")
        else:
            print("❌ No tweets to save")


async def main():
    """Example usage"""
    scraper = TwitterGrokScraper(headless=False)

    # Fetch tweets
    tweets_data = await scraper.fetch_viral_tweets()

    if tweets_data:
        # Save to file
        output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "viral_tweets.json")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tweets_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved {len(tweets_data['viral_tweets'])} tweets to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
