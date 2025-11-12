"""
Claude Financial Analyst Tool
Uses Claude Sonnet 4.5 for deep financial analysis and script generation
"""

import os
import json
from typing import Dict, List, Optional
from anthropic import Anthropic


class ClaudeFinancialAnalyst:
    """
    Financial analysis and script generation using Claude Sonnet 4.5
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key (uses env var if not provided)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable.")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"

    def _create_analysis_prompt(self, tweet_data: Dict, top_comments: Optional[List[Dict]] = None) -> str:
        """
        Create prompt for Claude to analyze tweet and generate script

        Args:
            tweet_data: Tweet data dictionary
            top_comments: Optional list of top comments for context

        Returns:
            Formatted prompt string
        """
        # Extract related stocks
        related_stocks_list = tweet_data.get('related_stocks', [])
        if related_stocks_list and isinstance(related_stocks_list[0], dict):
            # New format: list of dicts with symbol, price, change
            related_stocks = ", ".join([
                f"{s['symbol']} (${s.get('price', 'N/A')}, {s.get('change_percent', 'N/A')}%)"
                for s in related_stocks_list
            ])
        else:
            # Old format: list of strings
            related_stocks = ", ".join(related_stocks_list) if related_stocks_list else ""
        stocks_section = f"\n\nRelated Stock Tickers: {related_stocks}" if related_stocks else ""

        # Format top comments
        comments_section = ""
        if top_comments:
            comments_text = "\n".join([
                f"- {c['name']} (@{c['username']}): \"{c['comment_text']}\" ({c['likes']} likes)"
                for c in top_comments[:5]
            ])
            comments_section = f"\n\nTop Public Reactions:\n{comments_text}\n\nAnalyze these comments to understand public sentiment and incorporate relevant perspectives into the script."

        prompt = f"""You are a financial analyst creating content for "XInsider," a YouTube Shorts channel focused on providing valuable insights for investors and people in the financial world.

## VIRAL TWEET TO ANALYZE:

**Tweet by {tweet_data['name']} (@{tweet_data['username']})**
Engagement: {tweet_data.get('views', 0):,} views | {tweet_data.get('likes', 0):,} likes | {tweet_data.get('retweets', 0):,} retweets

**Content:**
{tweet_data['content']}{stocks_section}{comments_section}

## YOUR TASK:

1. **Research & Fact-Check:** Search for recent news, financial reports, market analysis, and credible sources related to this tweet's claims. Verify facts and provide context.

2. **Financial Analysis:** Provide professional analysis covering:
   - Market implications and impact on relevant sectors
   - Historical context and precedents
   - Expert opinions and institutional perspectives
   - Potential risks and opportunities for investors
   - Contrarian viewpoints (if the tweet is one-sided)

3. **Script Creation:** Write a compelling 60-75 second YouTube Short script with:
   - **Hook (0-5 seconds):** Attention-grabbing opening that makes viewers want to watch
   - **Context (5-20 seconds):** What happened and why it matters
   - **Analysis (20-55 seconds):** Deep dive into the financial implications, backed by facts
   - **Key Takeaway (55-75 seconds):** What investors should know, actionable insight

## SCRIPT REQUIREMENTS:

- **Language:** English only, clear and professional
- **Tone:** Balanced, analytical, not sensationalist
- **Target Audience:** Investors, finance professionals, crypto enthusiasts
- **Goal:** Educational value - viewers should learn something useful
- **Format:** Natural speech, ready for text-to-speech (no special formatting)
- **Credibility:** Cite sources when making claims (e.g., "according to Tesla's Q4 report...")
- **Balance:** Present multiple perspectives, not just confirming the tweet's narrative

## OUTPUT FORMAT:

Return ONLY a JSON object with this structure (no markdown, no code blocks):

{{
  "financial_analysis": {{
    "summary": "Brief overview of the situation",
    "key_facts": [
      "Fact 1 with source",
      "Fact 2 with source",
      "Fact 3 with source"
    ],
    "market_impact": "Analysis of market implications",
    "investor_perspective": "What investors should consider",
    "risks_and_opportunities": "Potential risks and opportunities",
    "credibility_assessment": "Assessment of the tweet's claims (verified/misleading/opinion/mixed)"
  }},
  "script": {{
    "video_title": "Compelling title for the Short (max 60 characters)",
    "hook": "5-second attention-grabbing opening",
    "full_script": "Complete narration script ready for text-to-speech. This should be the ENTIRE voiceover text from start to finish, combining all sections into one continuous narrative.",
    "dialogue": [
      {{
        "section": "hook",
        "text": "Opening line...",
        "duration_seconds": 5
      }},
      {{
        "section": "context",
        "text": "Context paragraph...",
        "duration_seconds": 15
      }},
      {{
        "section": "analysis",
        "text": "Analysis paragraph...",
        "duration_seconds": 35
      }},
      {{
        "section": "takeaway",
        "text": "Key takeaway...",
        "duration_seconds": 20
      }}
    ],
    "total_duration_seconds": 75,
    "voiceover_notes": "Tone and pacing guidance for narrator"
  }},
  "related_stocks": [
    {{
      "symbol": "TSLA",
      "price": 242.50,
      "change": 5.30,
      "change_percent": "2.23"
    }},
    {{
      "symbol": "BTC",
      "price": 43250.00,
      "change": -1250.00,
      "change_percent": "-2.81"
    }}
  ],
  "sources": [
    "Source 1 citation",
    "Source 2 citation"
  ]
}}

IMPORTANT: For "related_stocks", provide current market data with:
- symbol: Stock ticker (e.g., "TSLA", "BTC", "SPY")
- price: Current price in USD
- change: Dollar change from previous close
- change_percent: Percentage change as string (e.g., "2.23" or "-2.81")

Research the actual current prices for the stocks/crypto mentioned in the tweet. Include up to 4 most relevant tickers.

Remember: The goal is to provide value to investors, not just react to a viral tweet. Be thorough, balanced, and educational."""

        return prompt

    async def analyze_tweet_and_generate_script(self, tweet_data: Dict) -> Optional[Dict]:
        """
        Analyze tweet using Claude and generate script

        Args:
            tweet_data: Tweet data dictionary

        Returns:
            Analysis and script data or None if failed
        """
        try:
            print("[AI] Sending tweet to Claude for financial analysis...")

            # Get top comments if available
            top_comments = tweet_data.get('top_comments', [])

            # Create prompt
            prompt = self._create_analysis_prompt(tweet_data, top_comments)

            # Call Claude API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract response
            response_text = message.content[0].text

            # Parse JSON
            try:
                # Clean response
                cleaned_response = response_text.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]

                analysis_data = json.loads(cleaned_response.strip())
                print("[OK] Analysis complete!")
                return analysis_data

            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse Claude response as JSON: {str(e)}")
                print(f"Raw response: {response_text[:500]}...")
                return None

        except Exception as e:
            print(f"[ERROR] Error during Claude analysis: {str(e)}")
            return None


    async def analyze_and_save(self, tweet_data: Dict, output_path: str) -> Optional[str]:
        """
        Analyze tweet and save results to file

        Args:
            tweet_data: Tweet data dictionary
            output_path: Path to save analysis JSON

        Returns:
            Path to saved file or None if failed
        """
        analysis_data = await self.analyze_tweet_and_generate_script(tweet_data)

        if analysis_data:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            print(f"[SAVE] Analysis saved to {output_path}")
            return output_path
        else:
            print("[ERROR] No analysis to save")
            return None


async def main():
    """Example usage"""
    import asyncio

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
        "related_stocks": ["TSLA"],
        "top_comments": [
            {
                "username": "investor123",
                "name": "John Investor",
                "comment_text": "This is absolutely insane. Shareholders are clearly delusional.",
                "likes": 5432,
                "verified": False
            }
        ]
    }

    analyst = ClaudeFinancialAnalyst()
    analysis = await analyst.analyze_tweet_and_generate_script(example_tweet)

    if analysis:
        print("\n" + "="*50)
        print("FINANCIAL ANALYSIS:")
        print("="*50)
        print(json.dumps(analysis, indent=2))

        print("\n" + "="*50)
        print("ELEVENLABS SCRIPT:")
        print("="*50)
        elevenlabs_script = analyst.prepare_elevenlabs_script(analysis)
        print(json.dumps(elevenlabs_script, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
