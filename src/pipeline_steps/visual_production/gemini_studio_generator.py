"""
Gemini Studio Generator
Generates black and white vector art images for financial news shorts
- Character poses (with white background for removal)
- Screen content graphics (news logos, charts, visualizations)
- News studio set background
"""

import os
import json
import time
from typing import Dict, List, Optional
import google.genai as genai
from google.genai import types


class GeminiStudioGenerator:
    """
    Generates all visual assets for the news studio:
    1. Base news studio set (black and white, minimalist)
    2. Character poses (various poses, white background)
    3. Screen graphics (tweets, logos, charts, etc.)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client

        Args:
            api_key: Google Gemini API key (uses env var if not provided)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable.")

        genai.configure(api_key=self.api_key)
        self.model_name = "gemini-2.0-flash-exp"

        # Base style for all images
        self.base_style = "black and white vector art, minimalist, high contrast, clean lines, professional, modern"

    def generate_news_studio_set(self, output_path: str) -> str:
        """
        Generate the base news studio set background

        Args:
            output_path: Path to save the generated image

        Returns:
            Path to generated image
        """
        print("🎨 Generating news studio set...")

        prompt = f"""Create a professional news studio set in {self.base_style}.

REQUIREMENTS:
- Modern, minimalist news studio environment
- Black and white only, high contrast
- Large flat screen TV/monitor on the right side (empty black screen for now)
- Professional news desk or podium on the left
- Clean, uncluttered background
- Space for a character to stand in front of the desk
- Bottom area clear for ticker bar overlay
- Professional lighting indicators (simplified)
- Vector art style, clean geometric shapes

PERSPECTIVE: Front view, wide shot
SIZE: 1080x1920 (vertical format for YouTube Shorts)

The final image should look like a professional financial news broadcast set, ready for a character to be placed in front."""

        return self._generate_image(prompt, output_path)

    def generate_character_pose(self,
                                pose_name: str,
                                pose_prompt: str,
                                output_path: str,
                                reference_image_path: Optional[str] = None) -> str:
        """
        Generate a character in specific pose

        Args:
            pose_name: Name of the pose (e.g., "explaining_hand_gesture")
            pose_prompt: Detailed prompt for the pose
            output_path: Path to save the generated image
            reference_image_path: Optional reference image for consistency

        Returns:
            Path to generated image
        """
        print(f"🎨 Generating character pose: {pose_name}...")

        prompt = f"""Create a professional news anchor character in {self.base_style}.

CHARACTER DESCRIPTION:
- Professional news anchor/financial analyst
- Business professional attire (suit or professional outfit)
- Confident, trustworthy appearance
- Black and white vector art, clean lines
- Minimalist style, no unnecessary details

POSE: {pose_prompt}

IMPORTANT REQUIREMENTS:
- PURE WHITE BACKGROUND (#FFFFFF) - No shadows, no gradients, completely white
- Character should be centered
- Full body or 3/4 body shot (waist up minimum)
- Clear silhouette for easy background removal
- Professional, natural pose
- Facing forward or slight 3/4 angle
- Hands and gestures clearly defined
- Vector art style with clean, bold lines

SIZE: 1080x1920 (vertical)

The white background is CRITICAL for background removal in post-production."""

        return self._generate_image(prompt, output_path, reference_image_path)

    def generate_screen_graphic(self,
                               content_type: str,
                               content_prompt: str,
                               output_path: str,
                               tweet_data: Optional[Dict] = None) -> str:
        """
        Generate content for the studio screen

        Args:
            content_type: Type of content (tweet_screenshot, news_logo, chart, etc.)
            content_prompt: Detailed prompt for the content
            output_path: Path to save the generated image
            tweet_data: Optional tweet data for tweet screenshots

        Returns:
            Path to generated image
        """
        print(f"🎨 Generating screen content: {content_type}...")

        if content_type == "tweet_screenshot" and tweet_data:
            # For tweet screenshots, we use the existing tweet screenshot generator
            # This is a placeholder - actual implementation uses TweetScreenshotGenerator
            prompt = f"This will use TweetScreenshotGenerator instead"
        else:
            # For other content types, generate with Gemini
            prompt = f"""Create a screen graphic in {self.base_style} for a financial news broadcast.

CONTENT TYPE: {content_type}

REQUIREMENTS: {content_prompt}

STYLE:
- Black and white vector art
- High contrast, bold text
- Professional, clean, minimalist
- Suitable for display on a news studio screen
- Clear, readable even at small sizes
- Financial/professional aesthetic

SIZE: 1920x1080 (horizontal, 16:9 for screen display)

The graphic should look professional and informative, suitable for a financial news broadcast."""

        return self._generate_image(prompt, output_path)

    def generate_news_logo_headline(self,
                                   publication: str,
                                   headline: str,
                                   output_path: str) -> str:
        """
        Generate news publication logo with headline

        Args:
            publication: Name of publication (e.g., "CNBC", "Bloomberg")
            headline: Headline text
            output_path: Path to save image

        Returns:
            Path to generated image
        """
        print(f"🎨 Generating {publication} logo with headline...")

        prompt = f"""Create a news publication graphic in {self.base_style}.

PUBLICATION: {publication}
HEADLINE: {headline}

REQUIREMENTS:
- {publication} logo style (simplified, black and white)
- Professional news publication aesthetic
- Headline text prominent and readable
- Clean, minimalist layout
- High contrast
- Professional typography
- Vector art style

SIZE: 1920x1080 (horizontal)

Should look like a professional news graphic from {publication}."""

        return self._generate_image(prompt, output_path)

    def generate_stock_chart(self,
                            stock_data: Dict,
                            output_path: str) -> str:
        """
        Generate stock chart visualization

        Args:
            stock_data: Stock data dictionary with symbol, price, change, etc.
            output_path: Path to save image

        Returns:
            Path to generated image
        """
        symbol = stock_data.get('symbol', 'STOCK')
        price = stock_data.get('price', 0)
        change = stock_data.get('change', 0)
        change_percent = stock_data.get('change_percent', '0')

        direction = "upward" if change >= 0 else "downward"

        print(f"🎨 Generating stock chart for {symbol}...")

        prompt = f"""Create a stock price chart in {self.base_style}.

STOCK: {symbol}
CURRENT PRICE: ${price}
CHANGE: ${change} ({change_percent}%)
TREND: {direction}

REQUIREMENTS:
- Professional financial chart
- Show {direction} price movement trend
- Display {symbol} prominently
- Show current price ${price}
- Include percentage change {change_percent}%
- Clean, minimalist chart design
- Black and white only
- Vector art style, bold lines
- Professional financial aesthetic

SIZE: 1920x1080 (horizontal)

Should look like a professional stock market chart from a financial news broadcast."""

        return self._generate_image(prompt, output_path)

    def _generate_image(self,
                       prompt: str,
                       output_path: str,
                       reference_image_path: Optional[str] = None) -> str:
        """
        Internal method to generate image with Gemini

        Args:
            prompt: Generation prompt
            output_path: Path to save image
            reference_image_path: Optional reference image

        Returns:
            Path to generated image
        """
        try:
            # Create output directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Generate image
            model = genai.GenerativeModel(self.model_name)

            # Add reference image if provided
            if reference_image_path and os.path.exists(reference_image_path):
                with open(reference_image_path, 'rb') as f:
                    reference_image = f.read()

                response = model.generate_content([
                    types.Part.from_bytes(data=reference_image, mime_type="image/png"),
                    prompt
                ])
            else:
                response = model.generate_content(prompt)

            # Save image
            if response.candidates and response.candidates[0].content.parts:
                image_data = response.candidates[0].content.parts[0].inline_data.data

                with open(output_path, 'wb') as f:
                    f.write(image_data)

                print(f"✅ Image saved: {output_path}")
                return output_path
            else:
                print("❌ No image data in response")
                return None

        except Exception as e:
            print(f"❌ Failed to generate image: {str(e)}")
            # Retry with exponential backoff
            time.sleep(2)
            return None


def main():
    """Example usage"""
    generator = GeminiStudioGenerator()
    output_dir = "output/studio_assets"
    os.makedirs(output_dir, exist_ok=True)

    # Generate news studio set
    set_path = generator.generate_news_studio_set(
        os.path.join(output_dir, "news_studio_set.png")
    )

    # Generate character pose
    character_path = generator.generate_character_pose(
        "explaining_hand_gesture",
        "Professional news anchor with hand raised in explanatory gesture, confident stance",
        os.path.join(output_dir, "character_explaining.png")
    )

    # Generate stock chart
    stock_data = {
        "symbol": "TSLA",
        "price": 242.50,
        "change": 5.30,
        "change_percent": "2.23"
    }
    chart_path = generator.generate_stock_chart(
        stock_data,
        os.path.join(output_dir, "tesla_chart.png")
    )

    print("\n✅ Studio assets generated!")


if __name__ == "__main__":
    main()
