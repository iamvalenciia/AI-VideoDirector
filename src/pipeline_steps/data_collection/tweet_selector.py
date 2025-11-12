"""
Intelligent Tweet Selector
Uses OpenAI GPT-4o to select the best tweet for maximum YouTube Shorts engagement
Analyzes multiple factors beyond just metrics
"""

import os
import json
from typing import Dict, List, Optional
from openai import OpenAI


class TweetSelector:
    """
    Intelligently selects the best tweet for YouTube Shorts using AI analysis
    Considers: engagement metrics, content quality, viral potential, investor value
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tweet Selector

        Args:
            api_key: OpenAI API key (uses env var if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)

    def select_best_tweet(self, tweets_data: Dict, target_audience: str = "investors") -> Optional[Dict]:
        """
        Select the best tweet for YouTube Shorts using AI analysis

        Args:
            tweets_data: Dictionary with 'viral_tweets' array
            target_audience: Target audience (investors, traders, crypto enthusiasts, etc.)

        Returns:
            Selected tweet dictionary with selection reasoning
        """
        try:
            viral_tweets = tweets_data.get('viral_tweets', [])

            if not viral_tweets:
                print("[ERROR] No tweets to select from")
                return None

            if len(viral_tweets) == 1:
                print("[INFO] Only one tweet available, selecting by default")
                return {
                    'selected_tweet': viral_tweets[0],
                    'tweet': viral_tweets[0],  # For backward compatibility
                    'selection_reasoning': 'Only tweet available',
                    'confidence_score': 100,
                    'investor_value': 'N/A - Only one option',
                    'engagement_potential': 100,
                    'content_quality': 100,
                    'viral_potential': 100,
                    'viral_factors': 'N/A - Single option',
                    'production_value': 100,
                    'alternatives_considered': 0,
                    'ranking': []
                }

            print(f"🤖 Analyzing {len(viral_tweets)} tweets for best YouTube Shorts potential...")

            # Create selection prompt
            prompt = self._create_selection_prompt(viral_tweets, target_audience)

            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4o for intelligent analysis
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                response_format={"type": "json_object"}
            )

            # Parse response
            selection_result = json.loads(response.choices[0].message.content)

            # Get selected tweet
            selected_index = selection_result.get('selected_tweet_index', 0)
            selected_tweet = viral_tweets[selected_index]

            # Add selection metadata
            result = {
                'tweet': selected_tweet,
                'selection_reasoning': selection_result.get('reasoning', ''),
                'confidence_score': selection_result.get('confidence_score', 0),
                'engagement_potential': selection_result.get('engagement_potential', ''),
                'content_quality': selection_result.get('content_quality', ''),
                'viral_factors': selection_result.get('viral_factors', []),
                'investor_value': selection_result.get('investor_value', ''),
                'alternatives_considered': len(viral_tweets),
                'ranking': selection_result.get('ranking', [])
            }

            print(f"[OK] Selected tweet by @{selected_tweet['username']}")
            print(f"   Confidence: {result['confidence_score']}/100")
            print(f"   Reason: {result['selection_reasoning'][:100]}...")

            return result

        except Exception as e:
            print(f"[ERROR] Failed to select tweet: {str(e)}")
            # Fallback to simple engagement rate calculation
            return self._fallback_selection(viral_tweets)

    def _get_system_prompt(self) -> str:
        """Get system prompt for tweet selector"""
        return """You are an expert YouTube Shorts content strategist specializing in financial content.

Your job is to analyze viral financial tweets and select THE BEST one for creating a YouTube Short that will:
1. Get maximum views and engagement
2. Provide real value to investors
3. Generate discussion and shares
4. Stand out in the YouTube Shorts algorithm

You consider multiple factors:
- Engagement metrics (views, likes, comments)
- Content quality and substance
- Controversy/discussion potential
- Educational value for investors
- Timeliness and relevance
- Visual potential for short-form video
- Hook strength (will people stop scrolling?)
- Sharability factor

You think like a viral content creator who also deeply understands finance."""

    def _create_selection_prompt(self, tweets: List[Dict], target_audience: str) -> str:
        """Create detailed prompt for tweet selection"""

        # Format tweets for analysis
        tweets_summary = []
        for idx, tweet in enumerate(tweets):
            summary = {
                "index": idx,
                "username": tweet.get('username'),
                "name": tweet.get('name'),
                "verified": tweet.get('verified'),
                "content": tweet.get('content'),
                "views": tweet.get('views', 0),
                "likes": tweet.get('likes', 0),
                "retweets": tweet.get('retweets', 0),
                "replies": tweet.get('replies', 0),
                "engagement_rate": round((tweet.get('likes', 0) + tweet.get('retweets', 0) + tweet.get('replies', 0)) / max(tweet.get('views', 1), 1) * 100, 3),
                "related_stocks": [s.get('symbol') if isinstance(s, dict) else s for s in tweet.get('related_stocks', [])],
                "top_comments_summary": f"{len(tweet.get('top_comments', []))} comments available"
            }
            tweets_summary.append(summary)

        prompt = f"""Analyze these viral financial tweets and select THE BEST ONE for creating a YouTube Short.

TARGET AUDIENCE: {target_audience}

TWEETS TO ANALYZE:
{json.dumps(tweets_summary, indent=2)}

YOUR TASK:
Select the single best tweet that will perform best as a YouTube Short. Consider:

1. **Engagement Potential** (30%)
   - Current engagement metrics (views, likes, replies)
   - Engagement rate quality
   - Comment quality (controversy/discussion)
   - Author credibility and following

2. **Content Quality** (25%)
   - Substantive information vs. pure opinion
   - Educational value for investors
   - Fact-based claims vs. speculation
   - Depth of financial insight

3. **Viral Potential** (25%)
   - Hook strength (shocking, surprising, contrarian)
   - Emotional response trigger
   - Sharability factor
   - Discussion/debate potential
   - Timeliness (breaking news vs. ongoing topic)

4. **Video Production Potential** (20%)
   - Visual storytelling opportunities
   - Clear narrative structure
   - Related stock charts/graphics available
   - Script potential (can we make 60-75s of quality content?)
   - Complexity (too simple = boring, too complex = confusing)

SELECTION CRITERIA:
- Must have substantive financial content (not just memes)
- Should generate discussion/comments
- Must be explainable in 60-75 seconds
- Should provide actionable insights for investors
- Bonus: Controversial but factual claims
- Bonus: Clear related stocks/companies for visuals
- Bonus: Recent news hooks

OUTPUT FORMAT (JSON):
{{
  "selected_tweet_index": 0,
  "confidence_score": 95,
  "reasoning": "Detailed explanation of why this tweet is the best choice (2-3 sentences)",
  "engagement_potential": "High/Medium/Low with explanation",
  "content_quality": "Excellent/Good/Fair with explanation",
  "viral_factors": ["Factor 1", "Factor 2", "Factor 3"],
  "investor_value": "What investors will learn from this Short",
  "production_notes": "Notes for video production",
  "ranking": [
    {{
      "tweet_index": 0,
      "score": 95,
      "brief_reason": "Why ranked here"
    }},
    {{
      "tweet_index": 1,
      "score": 78,
      "brief_reason": "Why ranked here"
    }}
  ]
}}

IMPORTANT:
- confidence_score should be 0-100 (how confident you are this is the best choice)
- ranking should include ALL tweets, sorted by score (highest first)
- Be honest: if none are great, say so (but still pick the best of the bunch)
- Focus on what will perform well on YouTube Shorts specifically

Make your selection now:"""

        return prompt

    def _fallback_selection(self, tweets: List[Dict]) -> Dict:
        """Fallback selection using simple engagement rate if AI fails"""
        print("⚠️ Using fallback selection method (engagement rate)")

        for tweet in tweets:
            views = tweet.get('views', 1)
            engagement = (
                tweet.get('likes', 0) +
                tweet.get('retweets', 0) * 1.5 +
                tweet.get('replies', 0) * 1.2
            )
            tweet['_engagement_score'] = (engagement / views) * 100

        best_tweet = max(tweets, key=lambda x: x.get('_engagement_score', 0))

        return {
            'tweet': best_tweet,
            'selection_reasoning': 'Selected based on highest engagement rate (fallback method)',
            'confidence_score': 50,
            'engagement_potential': 'Unknown (AI analysis failed)',
            'content_quality': 'Unknown',
            'viral_factors': ['High engagement rate'],
            'investor_value': 'To be determined',
            'alternatives_considered': len(tweets),
            'ranking': []
        }

    def save_selection_report(self, selection_result: Dict, output_path: str):
        """
        Save detailed selection report

        Args:
            selection_result: Result from select_best_tweet
            output_path: Path to save report
        """
        # Create comprehensive report
        report = {
            "selected_tweet": selection_result['tweet'],
            "selection_metadata": {
                "reasoning": selection_result['selection_reasoning'],
                "confidence_score": selection_result['confidence_score'],
                "engagement_potential": selection_result['engagement_potential'],
                "content_quality": selection_result['content_quality'],
                "viral_factors": selection_result['viral_factors'],
                "investor_value": selection_result['investor_value'],
                "alternatives_considered": selection_result['alternatives_considered']
            },
            "ranking": selection_result.get('ranking', [])
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"[SAVE] Selection report saved: {output_path}")


def main():
    """Example usage"""
    # Example tweets data
    example_tweets = {
        "viral_tweets": [
            {
                "username": "financenews",
                "name": "Finance News",
                "verified": True,
                "content": "BREAKING: Tesla shareholders approve $1 TRILLION pay package for Elon Musk. This could be the largest executive compensation in history.",
                "views": 5000000,
                "likes": 120000,
                "retweets": 25000,
                "replies": 8000,
                "related_stocks": ["TSLA"],
                "top_comments": [
                    {"username": "user1", "comment_text": "This is insane!", "likes": 5000}
                ]
            },
            {
                "username": "cryptoexpert",
                "name": "Crypto Expert",
                "verified": False,
                "content": "Bitcoin just hit $50k again. Time to buy? 🚀",
                "views": 2000000,
                "likes": 50000,
                "retweets": 10000,
                "replies": 3000,
                "related_stocks": ["BTC"],
                "top_comments": []
            },
            {
                "username": "marketanalyst",
                "name": "Market Analyst",
                "verified": True,
                "content": "Fed announces emergency rate hike. Markets plunge 5% in minutes. This is unprecedented.",
                "views": 8000000,
                "likes": 200000,
                "retweets": 45000,
                "replies": 15000,
                "related_stocks": ["SPY", "QQQ"],
                "top_comments": [
                    {"username": "trader", "comment_text": "Time to buy puts", "likes": 12000}
                ]
            }
        ]
    }

    selector = TweetSelector()
    result = selector.select_best_tweet(example_tweets, target_audience="investors")

    if result:
        print("\n" + "="*60)
        print("SELECTION RESULT:")
        print("="*60)
        print(f"Selected: @{result['tweet']['username']}")
        print(f"Content: {result['tweet']['content'][:100]}...")
        print(f"Confidence: {result['confidence_score']}/100")
        print(f"\nReasoning: {result['selection_reasoning']}")
        print(f"\nEngagement Potential: {result['engagement_potential']}")
        print(f"Content Quality: {result['content_quality']}")
        print(f"Investor Value: {result['investor_value']}")

        if result.get('ranking'):
            print("\n" + "="*60)
            print("FULL RANKING:")
            print("="*60)
            for rank in result['ranking']:
                print(f"{rank['score']}/100 - Tweet #{rank['tweet_index']}: {rank['brief_reason']}")


if __name__ == "__main__":
    main()
