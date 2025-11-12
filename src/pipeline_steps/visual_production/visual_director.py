"""
Visual Director Tool
Creates visual production plan for financial news shorts
Determines character poses and screen content for each segment
"""

import os
import json
from typing import Dict, List, Optional
from openai import OpenAI


class VisualDirector:
    """
    Plans visual elements for each segment of the video:
    - Character poses (different poses per segment)
    - Screen content (tweet, news logos, financial charts, etc.)
    - Timing and transitions
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Visual Director

        Args:
            api_key: OpenAI API key (uses env var if not provided)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)

        # Character pose library
        self.character_poses = [
            "neutral_standing",
            "explaining_hand_gesture",
            "pointing_up",
            "arms_crossed_confident",
            "hand_on_chin_thinking",
            "presenting_both_hands",
            "excited_gesture",
            "serious_pointing",
            "welcoming_arms_open",
            "concern_hand_raised"
        ]

        # Screen content types
        self.screen_content_types = [
            "tweet_screenshot",
            "news_logo_with_headline",
            "stock_chart",
            "financial_data_visualization",
            "company_logo",
            "news_publication_logo",
            "percentage_change_graphic",
            "market_indicator"
        ]

    def create_visual_plan(self,
                          script_data: Dict,
                          timestamp_data: Dict,
                          tweet_data: Dict,
                          analysis_data: Dict) -> Optional[Dict]:
        """
        Create comprehensive visual plan for the video

        Args:
            script_data: Script with dialogue sections from Claude
            timestamp_data: Word-level timestamps from Whisper
            tweet_data: Original tweet data
            analysis_data: Financial analysis from Claude

        Returns:
            Visual plan dictionary or None if failed
        """
        try:
            print("🎬 Creating visual production plan...")

            # Create prompt for visual planning
            prompt = self._create_visual_planning_prompt(
                script_data,
                timestamp_data,
                tweet_data,
                analysis_data
            )

            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Use GPT-4 for creative visual planning
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
                temperature=0.7,
                response_format={"type": "json_object"}
            )

            # Parse response
            visual_plan = json.loads(response.choices[0].message.content)

            print(f"✅ Visual plan created: {len(visual_plan.get('segments', []))} segments")
            return visual_plan

        except Exception as e:
            print(f"❌ Failed to create visual plan: {str(e)}")
            return None

    def _get_system_prompt(self) -> str:
        """Get system prompt for Visual Director"""
        return """You are a Visual Director for XInsider, a modern financial news YouTube Shorts channel.

VISUAL STYLE:
- Black and white vector art (minimalist, high contrast)
- News studio set with character and large screen
- Professional, clean, modern aesthetic
- Character uses natural poses and gestures
- Screen displays relevant visual content

YOUR JOB:
Plan the visual elements for each segment of the narration:
1. Character pose (natural, varied, matching the tone)
2. Screen content (tweet, news logos, charts, data visualizations)
3. Timing (when to change visuals)

IMPORTANT:
- One character pose per segment (varies based on narration tone)
- Screen content changes strategically (not every segment)
- Keep it professional but engaging
- Match visuals to the financial content being discussed"""

    def _create_visual_planning_prompt(self,
                                      script_data: Dict,
                                      timestamp_data: Dict,
                                      tweet_data: Dict,
                                      analysis_data: Dict) -> str:
        """Create detailed prompt for visual planning"""

        # Extract dialogue sections
        dialogue_sections = script_data.get('dialogue', [])

        # Extract key information
        video_title = script_data.get('video_title', '')
        related_stocks = analysis_data.get('related_stocks', [])
        sources = analysis_data.get('sources', [])

        prompt = f"""Create a visual production plan for this financial news short.

VIDEO TITLE: {video_title}

NARRATION SEGMENTS:
{json.dumps(dialogue_sections, indent=2)}

TWEET CONTENT:
{tweet_data.get('content', '')}
By @{tweet_data.get('username', '')}

RELATED STOCKS:
{json.dumps(related_stocks, indent=2)}

NEWS SOURCES MENTIONED:
{json.dumps(sources, indent=2)}

AVAILABLE CHARACTER POSES:
{json.dumps(self.character_poses, indent=2)}

AVAILABLE SCREEN CONTENT TYPES:
{json.dumps(self.screen_content_types, indent=2)}

OUTPUT REQUIREMENTS:

Return a JSON object with this structure:

{{
  "video_title_display": "Title text to show at bottom of video",
  "segments": [
    {{
      "segment_index": 0,
      "segment_name": "hook",
      "start_time": 0.0,
      "end_time": 5.0,
      "duration": 5.0,
      "narration_text": "Text from dialogue",
      "character_pose": "explaining_hand_gesture",
      "character_pose_prompt": "Detailed prompt for Gemini to generate this pose in black and white vector art style",
      "screen_content_type": "tweet_screenshot",
      "screen_content_prompt": "Detailed prompt for what to show on screen (if not tweet)",
      "screen_change": true/false,
      "visual_notes": "Notes about this segment's visual impact"
    }}
  ],
  "screen_changes": [
    {{
      "timestamp": 0.0,
      "content_type": "tweet_screenshot",
      "reason": "Why we're showing this",
      "duration": 15.0
    }}
  ],
  "production_notes": "Overall notes for video production"
}}

GUIDELINES:
1. Match character poses to narration tone (excited → excited_gesture, serious → serious_pointing)
2. Show tweet screenshot early (first 5-15 seconds)
3. Change screen to relevant graphics when mentioning:
   - News publications → Show logo + headline
   - Stock tickers → Show chart or price data
   - Statistics → Show data visualization
4. Keep character poses varied but natural
5. Don't change visuals too frequently (every 5-10 seconds minimum)
6. For character_pose_prompt: Describe the character in news anchor style, black and white vector art, minimalist, professional, the specific pose, clear background
7. For screen_content_prompt: Describe what visual would best illustrate this point

Return ONLY valid JSON."""

        return prompt

    def save_visual_plan(self, visual_plan: Dict, output_path: str):
        """
        Save visual plan to JSON file

        Args:
            visual_plan: Visual plan dictionary
            output_path: Path to save file
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(visual_plan, f, indent=2, ensure_ascii=False)
        print(f"💾 Visual plan saved to: {output_path}")


def main():
    """Example usage"""
    # Example data
    example_script = {
        "video_title": "Tesla's $1T Pay Package Explained",
        "dialogue": [
            {
                "section": "hook",
                "text": "A one trillion dollar pay package just got approved.",
                "duration_seconds": 5
            },
            {
                "section": "context",
                "text": "75% of Tesla shareholders voted to approve Elon Musk's compensation plan.",
                "duration_seconds": 10
            }
        ]
    }

    example_tweet = {
        "content": "Tesla shareholders approved $1T pay package for Elon Musk",
        "username": "financenews"
    }

    example_analysis = {
        "related_stocks": [
            {"symbol": "TSLA", "price": 242.50}
        ],
        "sources": ["Tesla Q4 Report", "CNBC"]
    }

    director = VisualDirector()
    visual_plan = director.create_visual_plan(
        example_script,
        {},
        example_tweet,
        example_analysis
    )

    if visual_plan:
        print("\n" + "="*60)
        print("VISUAL PLAN:")
        print("="*60)
        print(json.dumps(visual_plan, indent=2))


if __name__ == "__main__":
    main()
