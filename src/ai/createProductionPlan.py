"""
AI Production Plan Creator for XInsight YouTube Channel
Uses Anthropic's Claude model to generate a complete video production plan
from viral tweets.
"""

import os
import json
from typing import Dict, Optional, Any
from anthropic import Anthropic # type: ignore
from dotenv import load_dotenv # type: ignore


load_dotenv()


class ProductionPlanCreator:
    """
    Generates a comprehensive production plan for a YouTube video by analyzing
    financial tweets
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initializes the ProductionPlanCreator.

        Args:
            api_key: Anthropic API key. If not provided, it will use the
                     ANTHROPIC_API_KEY environment variable.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key not provided. Set the ANTHROPIC_API_KEY environment variable."
            )
        self.client = Anthropic(api_key=self.api_key)

    def create_plan(
        self, tweets_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Creates a production plan from tweets data.

        Args:
            tweets_data: Dictionary containing viral tweets

        Returns:
            Dictionary containing the production plan, or None if failed
        """

        try:
            # Validate input data
            viral_tweets = tweets_data.get("viral_tweets", [])
            if not viral_tweets:
                print("[ERROR] No viral tweets in input data.")
                return None

            # Create prompts with JSON data
            user_prompt = self._create_user_prompt(tweets_data)

            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                temperature=0.5,
                messages=[{"role": "user", "content": user_prompt}],
            )

            raw = response.content[0].text

            print("\n===== RAW AI RESPONSE =====")
            print(raw)
            print("===========================\n")

            # Extract JSON from response
            json_output = raw.strip()

            # Remove markdown code blocks if present
            if "```json" in json_output:
                start = json_output.find("```json") + 7
                end = json_output.find("```", start)
                json_output = json_output[start:end].strip()
            elif "```" in json_output:
                # Fallback: any code block
                lines = json_output.split("\n")
                start_idx = 0
                end_idx = len(lines)

                for i, line in enumerate(lines):
                    if line.strip().startswith("```"):
                        start_idx = i + 1
                        break

                for i in range(len(lines)-1, -1, -1):
                    if lines[i].strip() == "```" or lines[i].strip().startswith("```"):
                        end_idx = i
                        break

                json_output = "\n".join(lines[start_idx:end_idx]).strip()

            # Parse JSON
            try:
                production_plan = json.loads(json_output)
                print("[OK] Production plan created successfully.")
                return production_plan
            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse JSON: {e}")
                print("\n[DEBUG] First 1000 chars of output:")
                print(json_output[:1000])
                return None

        except Exception as e:
            print(f"[ERROR] Failed to create production plan: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_user_prompt(
        self, tweets_data: Dict[str, Any],
    ) -> str:
        """
        Creates the detailed user prompt with all the necessary data and instructions.
        """
        tweets_json_str = json.dumps(tweets_data, indent=2, ensure_ascii=False)

        return f"""You are an expert AI Production Planner for "XInsight," a YouTube channel that decodes viral financial and crypto tweets for investors. Your mission is to create a complete, ready-to-use production plan for a compelling, 1-minute YouTube video.

            **Input Format:**
            You will receive all input data in **JSON format**. This includes:
            - A list of viral tweets to analyze.

            Viral Tweets:
            ```json
            {tweets_json_str}
            ```

            **Output Format:**
            You must return a **single, valid JSON object** wrapped in ```json markdown block. Do NOT return TOON, YAML, or any other format. Only JSON.

            **Channel Identity: XInsight**
            - **Style:** High-retention financial analysis. We combine the urgency of news (Tweets) with the evergreen value of channels like Mark Tilbury.
            - **Tone:** Authoritative, urgent, and actionable.
            - **Description:** We decode trending financial and crypto topics in under 60 seconds. Every video breaks down what Twitter is talking about—with actual data, market context, and what it means for your portfolio. No hype. No clickbait. Just clear explanations backed by research.
            - **Audience:** Retail investors, crypto enthusiasts, and anyone interested in finance.

            **Character Base Image Description:**
            The channel uses a minimalist black and white illustration of a hooded figure. The style is graphic and simple, using flat silhouettes. The figure is completely black on a pure white background, creating a sense of mystery and anonymity. Key features:
            - Full-body black silhouette facing forward
            - Long robe or tunic falling to the bottom of the image, hiding all body shapes
            - Hands barely visible at the sides of the robe
            - Hood covering the entire head and face
            - Most distinctive feature: a white circle in the center of the face/hood area representing a single, penetrating eye
            - Style: Black and white vector graphic, high contrast, minimalist
            This character appears in all videos and must integrate naturally with segment images, interacting with visual elements rather than just standing there.

            **Your Task:**

            1. **Select the Best Tweet:** From the `viral_tweets` array, choose the single tweet with the highest potential for a viral, educational, and engaging 1-minute video.

            2. **Conduct Financial Analysis:** Research the topic of the selected tweet. Provide a deep, insightful analysis explaining what's happening, why it matters, and what it means for investors.

            3. **Determine the Angle of Attack FIRST:** Before writing the script, decide which narrative angle will make this video most compelling:
            - **Fear/Warning Angle:** Focus on risks, mistakes, urgent warnings
            - **Benefit/Outcome Angle:** Focus on money, percentages, specific results, timelines
            - **Contrarian/Curiosity Angle:** Go against conventional wisdom, challenge assumptions

            4. **Write the Video Script:** Write a complete, deep financial analysis script (~140–155 words).
            **YOUR ROLE:**
            You are NOT a news anchor. You are a **Financial Analyst**. Do not just repeat the tweet's numbers. **Explain the mechanics** behind them.
            
            **CRITICAL ANALYSIS REQUIREMENTS:**
            - **Educate the Audience:** When you mention a data point, explain *why* it is a red flag or a bullish signal. (e.g., Don't just say "Receivables are up." Say "Receivables are exploding, which is a classic accounting red flag—it means they are booking sales without collecting the cash.").
            - **Connect the Dots:** Show the relationship between the data and the stock price.
            - **Tone:** Analytical, insightful, and slightly skeptical (investigative).
            
            **STRUCTURE & TIMING:**
            1. **The Hook (0-10s):** State the Thesis clearly. What is the hidden truth the tweet reveals?
            2. **The Financial Breakdown (10-50s):** This is the core analysis. Break down the specific arguments from the tweet (Cash flow, Inventory, Fraud allegations). Use connecting logic: "This suggests...", "This creates a divergence...", "Fundamentally, this means...".
            3. **The Investor Takeaway (50-60s):** Final verdict. What should the investor do? What level must hold?

            **CONSTRAINTS:**
            - **Length:** STRICTLY 140 to 155 words (Fast-paced analysis).
            - **No Lists:** Do not say "First... Second... Third...". Weave it into a narrative.
            - **No Fluff:** Every sentence must add financial value or context.
            
            5. **Segment the Script:** Break `full_script` into logical `segments`. Each segment will include:
            - `segment_id`: Numeric ID starting from 1
            - `script_part`: The text for this segment
            - **ANIMATION SYSTEM - DYNAMIC MOVEMENT (Character + Environment):**
                For each segment, you must create a cinematic animation with 3 progressive frames. The movement should affect BOTH the character AND the environment together, creating a dynamic, professional visual experience.

                **Choose ONE animation type per segment from:**

                1. **CAMERA_PAN_RIGHT**: Camera pans from left to right
                - Frame 1: Character on left side of frame, environment shows left portion of scene
                - Frame 2: Character moves to center-right, environment shifts revealing more right-side elements (trees, buildings, objects moving left)
                - Frame 3: Character on right side, environment fully shifted showing right portion (new elements visible on right)

                2. **CAMERA_PAN_LEFT**: Camera pans from right to left
                - Frame 1: Character on right side of frame, environment shows right portion
                - Frame 2: Character moves to center-left, environment shifts revealing more left-side elements
                - Frame 3: Character on left side, environment fully shifted showing left portion

                3. **CAMERA_ZOOM_IN**: Camera zooms closer to subject
                - Frame 1: Wide shot - Character small, full environment visible (trees, mountains, sky, lots of space)
                - Frame 2: Medium shot - Character larger and more detailed, less environment visible, focus tightening
                - Frame 3: Close-up - Character fills most of frame, minimal environment, character details prominent

                4. **CAMERA_ZOOM_OUT**: Camera zooms away from subject
                - Frame 1: Close-up - Character fills frame, limited environment visible
                - Frame 2: Medium shot - Character smaller, more environment becoming visible around them
                - Frame 3: Wide shot - Character small, full environment revealed (landscape, sky, buildings)

                5. **PARALLAX_EFFECT**: Multi-layer movement at different speeds (cinematic depth)
                - Frame 1: Character center, background mountains far right, foreground trees far left, mid-ground rocks centered
                - Frame 2: Character moved right slightly, mountains moved a little (slow - far away), trees moved more (fast - close), rocks moved medium amount
                - Frame 3: Character far right, mountains barely moved (parallax far layer), trees significantly moved (parallax near layer), rocks moderately moved

                6. **ENVIRONMENTAL_DYNAMIC**: Weather/environmental effects
                - Frame 1: Calm scene - Character standing still, trees upright, clouds static, clear atmosphere
                - Frame 2: Wind begins - Character leaning slightly, trees swaying to one side, clouds moving, leaves in air
                - Frame 3: Strong wind - Character leaning more, trees bent dramatically, clouds dispersed, dynamic atmosphere, debris flying

                7. **ACTION_SEQUENCE**: Character performing action with environment reaction
                - Frame 1: Character preparing action (stance ready), environment calm and anticipatory
                - Frame 2: Character mid-action (jumping, pointing, gesturing), environment reacting (leaves flying, objects moving, energy effects)
                - Frame 3: Character completed action, environment shows aftermath (settled dust, moved objects, impact visible)

                **CRITICAL REQUIREMENTS:**
                - ALL prompts must be in ENGLISH
                - Each prompt must start with: "Create a 1024x1024 vector graphic image with white background"
                - Describe BOTH character position AND environment changes in each frame
                - Movement must be consistent with chosen animation_type
                - Maintain character consistency (same hooded figure with white eye circle)
                - Environment elements should move/change naturally with animation type
                - Use specific positioning: "Character positioned at [left/center/right]", "Trees visible on [left/right side]", "Mountains in [background position]"
            - **EXAMPLES OF DYNAMIC ANIMATION PROMPTS:**
                Example 1 - CAMERA_PAN_RIGHT (Financial theme):
                {{
                "animation_type": "CAMERA_PAN_RIGHT",
                "scene_description": "Hooded figure in Wall Street with stock market charts and skyscrapers",
                "base_image_prompt": "Create a 1024x1024 vector graphic image with white background. A mysterious hooded figure (black silhouette with single white eye circle on face) stands on the LEFT side of frame, positioned at x=256 from left edge. Behind the character on the left side: minimalist Wall Street skyscrapers in simple geometric shapes. Stock market charts with green upward arrows float in the middle ground. Clean vector style, black and white with minimal gray tones. Character is the focal point.",
                "frame_2_prompt": "FRAME 2: Same Wall Street scene, camera has panned RIGHT by 40%. The hooded figure has moved to CENTER-RIGHT position (now at x=640 from left). The skyscrapers that were on the left are now more centered in frame. MORE skyscrapers and buildings appear filling the center. Stock charts have shifted left, and NEW charts appear on the right side. The entire scene has shifted as if viewing a wider panorama. Vector style, white background, smooth transition.",
                "frame_3_prompt": "FRAME 3: Same Wall Street scene, camera panned RIGHT by 70%. The hooded figure is now positioned on FAR RIGHT side (x=900 from left). The skyscrapers completely fill the LEFT and CENTER of frame, showing a full cityscape. Multiple stock charts are scattered throughout, heavily concentrated on left and center. NEW buildings and financial elements that weren't visible before now appear on the far left. The scene shows the rightmost portion of the panorama. Vector style, white background, final dramatic composition.",
                "image_url": ""
                }}

                Example 2 - CAMERA_ZOOM_IN (Crypto theme):
                {{
                "animation_type": "CAMERA_ZOOM_IN",
                "scene_description": "Hooded figure surrounded by floating Bitcoin symbols and blockchain networks",
                "base_image_prompt": "Create a 1024x1024 vector graphic image with white background. WIDE SHOT: A small hooded figure (black silhouette with white eye) stands in the center, taking up only 20% of the frame height. Around the figure: large Bitcoin symbols (₿) float in the background, blockchain network lines connect in geometric patterns, digital nodes scatter across the scene. Mountains visible in far background. Lots of negative white space. Vector style, the figure appears distant.",
                "frame_2_prompt": "FRAME 2: Same scene, camera ZOOMED IN 50%. MEDIUM SHOT: The hooded figure now takes up 45% of frame height, showing more detail of the robe and eye. The Bitcoin symbols are now larger and closer, fewer visible but more detailed. Blockchain networks are more prominent and detailed. Mountains barely visible. Less white space. The scene feels more intimate. Vector style, white background.",
                "frame_3_prompt": "FRAME 3: Same scene, camera ZOOMED IN 80%. CLOSE-UP: The hooded figure fills 75% of frame, showing intricate details of the hood texture and the penetrating white eye clearly. Only 2-3 Bitcoin symbols visible very close and large. Blockchain lines pass right in front of viewer. Minimal background visible. Very little white space. Dramatic close composition. Vector style, white background.",
                "image_url": ""
                }}

                Example 3 - ENVIRONMENTAL_DYNAMIC (Market crash theme):
                {{
                "animation_type": "ENVIRONMENTAL_DYNAMIC",
                "scene_description": "Hooded figure in a financial storm with falling charts and turbulent atmosphere",
                "base_image_prompt": "Create a 1024x1024 vector graphic image with white background. A hooded figure stands CENTER of frame in calm atmosphere. Around them: stock charts float peacefully in vertical positions, dollar signs ($) hover statically, geometric buildings stand straight in background. Sky area is clear. Everything is orderly and stable. Vector style, clean composition.",
                "frame_2_prompt": "FRAME 2: Same scene, but WIND BEGINS. The hooded figure leans SLIGHTLY to the left, hood fabric showing movement. Stock charts begin TILTING and ROTATING 15-20 degrees. Dollar signs start DRIFTING leftward. Buildings remain stable but some chart papers are FLYING through the air. Small motion lines appear. Atmosphere becoming dynamic. Vector style, white background, energy increasing.",
                "frame_3_prompt": "FRAME 3: Same scene, STRONG FINANCIAL STORM. The hooded figure LEANS dramatically left at 30-degree angle, robe billowing. Stock charts are FALLING at 45-60 degree angles, some with RED down arrows. Dollar signs SCATTERED across frame in chaotic positions. Chart papers FLYING everywhere. Motion lines throughout. Dramatic diagonal composition suggesting crash/chaos. Vector style, white background, high energy.",
                "image_url": ""
                }}

            6. **analyze andSelect Ticker Stocks:** Choose exactly 4 relevant stock or crypto symbols related to the full_script content of the video. for the video's bottom ticker. For each stock, provide:
            - `symbol`: Ticker symbol (e.g., "AAPL", "TSLA", "BTC-USD")
            - `company_name`: Full company name
            - `price`: Current/recent price (research actual market data)
            - `change`: Absolute price change in dollars
            - `change_percent`: Percentage change (can be positive or negative),
            ensure all this market data is accurate and up-to-date.

            *CRITICAL:* These stocks should be directly related to the tweet topic and video content. Research actual current market data for accurate prices and changes.

            7. **Title Engineering (CRITICAL):** Analyze the successful style of channels like "Mark Tilbury". Generate 3 distinct title options based on these formulas:
            - **Option A (The Warning/Fear):** Focus on risk, mistakes, or urgent warnings (e.g., "The #1 Mistake...", "It's Happening Again...").
            - **Option B (The Specific Outcome):** Focus on money, percentages, or timelines (e.g., "How to turn $100 into...", "Why 2025 is different...").
            - **Option C (The Contrarian/Curiosity):** Go against the grain (e.g., "Don't Buy Bitcoin Until...", "Stop Listening to Cramer...").

            *Constraint:* Titles must be under 55 characters if possible, UPPERCASE words for emphasis allowed. Store all 3 options in `video_metadata.title_options` array.

            **CRITICAL FIELD REQUIREMENTS FOR TWEET SCREENSHOT GENERATION:**
            The following fields in `selected_tweet_details` are ABSOLUTELY REQUIRED for generating the tweet screenshot image:
            - `content`: Exact tweet text (will be displayed in screenshot)
            - `username`: Twitter username WITHOUT @ symbol (e.g., "elonmusk" not "@elonmusk")
            - `name`: Display name exactly as shown on Twitter profile
            - `verify_type`: MUST be one of: "blue", "orange", or "none" (determines verification badge)
            - `profile_picture_link`: MUST be a valid, working image URL
            - `views`, `likes`, `retweets`, `replies`: MUST be integers (not strings)
            - `posted_date`: MUST be in ISO format: "YYYY-MM-DDTHH:MM:SS" (e.g., "2025-11-20T14:30:00")

            **Final Output Structure:**
            Return a **single JSON object** with this exact structure:

            ```json
            {{
            "creator": "AI Production Planner",
            "channel_name": "XInsight",
            "angle_of_attack": "Fear/Warning | Benefit/Outcome | Contrarian/Curiosity",
            "selected_tweet_details": {{
                "tweet_link": "string (full tweet URL)",
                "content": "string (REQUIRED for tweet screenshot - exact tweet text)",
                "username": "string (REQUIRED for tweet screenshot - without @ symbol)",
                "name": "string (REQUIRED for tweet screenshot - display name)",
                "verified": boolean,
                "verify_type": "blue | orange | none (REQUIRED for tweet screenshot - verification badge type)",
                "profile_picture_link": "string (REQUIRED for tweet screenshot - valid image URL)",
                "views": number (REQUIRED for tweet screenshot - integer),
                "likes": number (REQUIRED for tweet screenshot - integer),
                "retweets": number (REQUIRED for tweet screenshot - integer),
                "replies": number (REQUIRED for tweet screenshot - integer),
                "engagement_rate": number,
                "posted_date": "string (REQUIRED for tweet screenshot - ISO format: YYYY-MM-DDTHH:MM:SS)",
                "analisis_sentimiento": "string",
                "contexto_resumido": "string",
                "punto_clave_inversor": "string",
                "contraargumento_breve": "string",
                "related_stocks": ["string"],
                "image_links": ["string"],
                "image_descriptions": ["string"],
            }},
            "video_metadata": {{
                "title_options": [
                {{
                    "type": "Warning/Fear",
                    "title": "string (under 55 chars)"
                }},
                {{
                    "type": "Specific Outcome",
                    "title": "string (under 55 chars)"
                }},
                {{
                    "type": "Contrarian/Curiosity",
                    "title": "string (under 55 chars)"
                }}
                ],
                "description": "string",
                "thumbnail_prompt": "string"
            }},
            "full_script": "string",
            # ... dentro de _create_user_prompt ...
            "segments": [
                {{
                    "segment_id": 1,
                    "script_part": "...",
                    "visual": {{
                        "animation_type": "CAMERA_PAN_RIGHT",
                        "scene_description": "Brief description...",
                        "base_image_prompt": "Prompt for Frame 1 (Start)...",
                        "frame_2_prompt": "Prompt for Frame 2 (Middle) - Describes movement...",
                        "frame_3_prompt": "Prompt for Frame 3 (End) - Final position..."
                    }}
                }}
            ],
            "ticker_stocks": [
                {{
                "symbol": "AAPL",
                "company_name": "Apple Inc.",
                "price": 175.50,
                "change": 4.25,
                "change_percent": 2.48
                }},
                {{
                "symbol": "TSLA",
                "company_name": "Tesla Inc.",
                "price": 242.80,
                "change": -5.60,
                "change_percent": -2.25
                }},
                {{
                "symbol": "BTC-USD",
                "company_name": "Bitcoin",
                "price": 43250.00,
                "change": 1250.00,
                "change_percent": 2.98
                }},
                {{
                "symbol": "SPY",
                "company_name": "S&P 500 ETF",
                "price": 455.20,
                "change": -1.80,
                "change_percent": -0.39
                }}
            ]
            }}
            ```

            **Important Rules:**
            - Must output **valid JSON only**, wrapped in ```json markdown block
            - Use proper JSON syntax: strings in quotes, arrays with [], objects with {{}}
            - Include all required fields from the structure above
            - Use `null` for optional fields that don't apply
            - For empty arrays, use `[]` not omission
            - Ensure all strings are properly escaped (quotes, newlines, etc.)
            - Be concise but comprehensive

            Now, analyze the provided JSON data and generate the **complete production plan as a single valid JSON object**.
            """

    def save_plan(self, plan: Dict[str, Any], output_path: str):
        """
        Saves the production plan to a JSON file.

        Args:
            plan: The production plan dictionary
            output_path: Path where to save the JSON file
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(plan, f, indent=2, ensure_ascii=False)
            print(f"[SAVE] Production plan saved to: {output_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save production plan: {e}")


def main():
    """
    Example usage of the ProductionPlanCreator.
    This function will load example data, create a plan, and print the result.
    """
    try:
        with open(
            "data/create_production_plan/input/viral_tweets.json", "r", encoding="utf-8"
        ) as f:
            tweets_data = json.load(f)
    except FileNotFoundError:
        print(
            "[ERROR] viral_tweets.json not found. Make sure it's in the 'data/create_production_plan/input' directory."
        )
        return

    creator = ProductionPlanCreator()
    production_plan = creator.create_plan(tweets_data)

    if production_plan:
        output_dir = "data/create_production_plan/output"
        output_file = os.path.join(output_dir, "production_plan.json")
        creator.save_plan(production_plan, output_file)

        print("\n" + "=" * 60)
        print("PRODUCTION PLAN SUMMARY")
        print("=" * 60)
        print(f"Video Title: {production_plan.get('video_metadata', {}).get('title')}")
        print(
            f"Selected Tweet: {production_plan.get('selected_tweet_details', {}).get('content', 'N/A')[:100]}..."
        )
        print(f"\nFull Script: {production_plan.get('full_script')}")
        print("\nSegments:")
        for i, segment in enumerate(production_plan.get("segments", [])):
            print(f"  {i+1}. {segment.get('script_part')}")
        print("=" * 60)


if __name__ == "__main__":
    main()
