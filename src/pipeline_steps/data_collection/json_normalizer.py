"""
JSON Normalizer Tool
Uses OpenAI to normalize and validate Grok AI responses into consistent JSON format
"""

import os
import json
from typing import Dict, Optional
from openai import OpenAI


class JSONNormalizer:
    """
    Normalizes Grok AI responses into consistent, structured JSON format
    Ensures data consistency across the pipeline
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI client

        Args:
            api_key: OpenAI API key (uses env var if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)

    def get_expected_schema(self) -> Dict:
        """
        Get the expected JSON schema for tweet data

        Returns:
            Dictionary with expected schema structure
        """
        return {
            "viral_tweets": [
                {
                    "tweet_link": "string (full URL)",
                    "content": "string (full tweet text)",
                    "username": "string (handle without @)",
                    "name": "string (display name)",
                    "verified": "boolean",
                    "verify_type": "string (blue/orange/none)",
                    "profile_picture_link": "string (direct URL)",
                    "views": "number",
                    "likes": "number",
                    "retweets": "number",
                    "replies": "number",
                    "engagement_rate": "number (percentage)",
                    "posted_date": "string (ISO format)",
                    "related_stocks": [
                        {
                            "symbol": "string (e.g., TSLA)",
                            "price": "number (current USD price)",
                            "change": "number (dollar change)",
                            "change_percent": "string (e.g., '2.23' or '-2.81')"
                        }
                    ],
                    "top_comments": [
                        {
                            "username": "string",
                            "name": "string",
                            "comment_text": "string",
                            "likes": "number",
                            "verified": "boolean"
                        }
                    ]
                }
            ],
            "search_metadata": {
                "search_date": "string (ISO timestamp)",
                "total_tweets_found": "number",
                "search_keywords": ["array of strings"],
                "timeframe": "string (e.g., 'last 48 hours')"
            }
        }

    def normalize_grok_response(self, grok_response: str) -> Optional[Dict]:
        """
        Normalize Grok AI response into consistent JSON format

        Args:
            grok_response: Raw response text from Grok AI

        Returns:
            Normalized JSON dictionary or None if failed
        """
        try:
            print("🔄 Normalizing Grok response with OpenAI...")

            # Create prompt for OpenAI
            prompt = f"""You are a JSON formatter. Your task is to take the following response from Grok AI and convert it into a perfectly structured JSON format.

EXPECTED SCHEMA:
{json.dumps(self.get_expected_schema(), indent=2)}

GROK AI RESPONSE:
{grok_response}

INSTRUCTIONS:
1. Extract all tweet information from the Grok response
2. Ensure all fields match the expected schema exactly
3. Convert any malformed data to the correct type
4. If a field is missing, use appropriate defaults:
   - Strings: "" (empty string)
   - Numbers: 0
   - Booleans: false
   - Arrays: []
5. Ensure dates are in ISO 8601 format
6. Ensure stock data includes symbol, price, change, and change_percent
7. Return ONLY valid JSON, no markdown, no code blocks, no explanations

OUTPUT (JSON only):"""

            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap for JSON formatting
                messages=[
                    {
                        "role": "system",
                        "content": "You are a JSON formatting expert. You only output valid JSON, nothing else."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistency
                response_format={"type": "json_object"}  # Force JSON output
            )

            # Extract JSON
            normalized_json = response.choices[0].message.content

            # Parse to validate
            parsed_data = json.loads(normalized_json)

            print("✅ Grok response normalized successfully!")
            return parsed_data

        except Exception as e:
            print(f"❌ Failed to normalize Grok response: {str(e)}")
            return None

    def validate_tweet_data(self, tweet_data: Dict) -> bool:
        """
        Validate that tweet data has all required fields

        Args:
            tweet_data: Single tweet data dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            'tweet_link', 'content', 'username', 'name',
            'views', 'likes', 'retweets', 'replies'
        ]

        for field in required_fields:
            if field not in tweet_data:
                print(f"⚠️ Missing required field: {field}")
                return False

        return True

    def save_normalized_data(self, data: Dict, output_path: str):
        """
        Save normalized data to JSON file

        Args:
            data: Normalized data dictionary
            output_path: Path to save file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Normalized data saved to: {output_path}")


def main():
    """Example usage"""
    # Example Grok response (might be messy)
    example_grok_response = """
    Here are the viral tweets:

    Tweet 1:
    - Link: https://x.com/example/status/123
    - Content: "Breaking news about Tesla!"
    - User: @elonmusk
    - Views: 5000000
    - Likes: 100000

    [... more tweets ...]
    """

    normalizer = JSONNormalizer()

    # Normalize
    normalized = normalizer.normalize_grok_response(example_grok_response)

    if normalized:
        print("\n" + "="*60)
        print("NORMALIZED JSON:")
        print("="*60)
        print(json.dumps(normalized, indent=2))


if __name__ == "__main__":
    main()
