"""
AI Production Plan Creator for XInsight YouTube Channel
Uses Anthropic's Claude model to generate a complete video production plan
from viral tweets and a character pose library.
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
    financial tweets and a library of character poses.
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
        self, tweets_data: Dict[str, Any], poses_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Creates a production plan from tweets and poses data.

        Args:
            tweets_data: Dictionary containing viral tweets
            poses_data: Dictionary containing character poses

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
            system_prompt = self._get_system_prompt()
            user_prompt = self._create_user_prompt(tweets_data, poses_data)

            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                temperature=0.5,
                system=system_prompt,
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

    def _get_system_prompt(self) -> str:
        """
        Creates the system prompt that defines the AI's role and context.
        """
        return """You are an expert AI Production Planner for "XInsight," a YouTube channel that decodes viral financial and crypto tweets for investors. Your mission is to create a complete, ready-to-use production plan for a compelling, 1-minute YouTube video.

**Channel Identity: XInsight**
- **Tagline:** Viral tweets, real analysis.
- **Description:** We decode trending financial and crypto topics in under 60 seconds. Every video breaks down what Twitter is talking about—with actual data, market context, and what it means for your portfolio. No hype. No clickbait. Just clear explanations backed by research.
- **Audience:** Retail investors, crypto enthusiasts, and anyone interested in finance.
- **Style:** Authoritative, insightful, fast-paced, and visually engaging. The narrator is a financial expert.

Your task is to analyze a set of viral tweets and a catalog of character poses to generate a single, comprehensive JSON output. Your analysis must be sharp, your script engaging, and your visual choices strategic to maximize viewer retention and educational value. You must research the topic of the selected tweet to provide a deep, insightful financial analysis. Your output MUST be a single, valid JSON object wrapped in ```json markdown block.
"""

    def _create_user_prompt(
        self, tweets_data: Dict[str, Any], poses_data: Dict[str, Any]
    ) -> str:
        """
        Creates the detailed user prompt with all the necessary data and instructions.
        """
        tweets_json_str = json.dumps(tweets_data, indent=2, ensure_ascii=False)
        poses_json_str = json.dumps(poses_data, indent=2, ensure_ascii=False)

        return f"""You are an expert AI Production Planner for "XInsight," a YouTube channel that decodes viral financial and crypto tweets for investors. Your mission is to create a complete, ready-to-use production plan for a compelling, 1-minute YouTube video.

**Input Format:**
You will receive all input data in **JSON format**. This includes:
- A list of viral tweets to analyze.
- A catalog of character poses for the narrator.

Viral Tweets:
```json
{tweets_json_str}
```

Character Poses:
```json
{poses_json_str}
```

**Output Format:**
You must return a **single, valid JSON object** wrapped in ```json markdown block. Do NOT return TOON, YAML, or any other format. Only JSON.

**Channel Identity: XInsight**
- **Tagline:** Viral tweets, real analysis.
- **Description:** We decode trending financial and crypto topics in under 60 seconds. Every video breaks down what Twitter is talking about—with actual data, market context, and what it means for your portfolio. No hype. No clickbait. Just clear explanations backed by research.
- **Audience:** Retail investors, crypto enthusiasts, and anyone interested in finance.
- **Style:** Authoritative, insightful, fast-paced, and visually engaging. The narrator is a financial expert.

**Your Task:**

1. **Select the Best Tweet:** From the `viral_tweets` array, choose the single tweet with the highest potential for a viral, educational, and engaging 1-minute video.

2. **Conduct Financial Analysis:** Research the topic of the selected tweet. Provide a deep, insightful financial analysis explaining what's happening, why it matters, and what it means for investors.

3. **Write the Video Script:** Write a complete, natural-sounding script for the narrator (~150–180 words). Must have a strong hook, clear explanation, and concise conclusion. Store it in `full_script`.

4. **Segment the Script:** Break `full_script` into logical `segments`. Each segment will include:
   - `segment_id`: Numeric ID starting from 1
   - `script_part`: The text for this segment
   - `pose`: Object with either:
     - `pose_number`, `description`, `filename` (from catalog), OR
     - `pose_prompt` (if no suitable pose exists)
   - `visual`: Object with either:
     - `image_url` (existing image from tweet), OR
     - `image_prompt` (for generation, ending with "style: black and white vector graphic.")

5. **Select Ticker Stocks:** Choose exactly 4 relevant stock or crypto symbols for the video's bottom ticker.

6. **Create Metadata:** Generate a catchy `title`, informative `description`, and a detailed `thumbnail_prompt`.

**Final Output Structure:**
Return a **single JSON object** with this exact structure:

```json
{{
  "creator": "AI Production Planner",
  "channel_name": "XInsight",
  "selected_tweet_details": {{
    "tweet_link": "string",
    "content": "string",
    "username": "string",
    "name": "string",
    "verified": boolean,
    "verify_type": "string",
    "profile_picture_link": "string",
    "views": number,
    "likes": number,
    "retweets": number,
    "replies": number,
    "engagement_rate": number,
    "posted_date": "string",
    "analisis_sentimiento": "string",
    "contexto_resumido": "string",
    "punto_clave_inversor": "string",
    "contraargumento_breve": "string",
    "related_stocks": ["string"],
    "image_links": ["string"],
    "image_descriptions": ["string"],
    "top_comments": [
      {{
        "username": "string",
        "name": "string",
        "comment_text": "string",
        "likes": number,
        "verified": boolean,
        "verify_type": "string",
        "profile_picture_link": "string",
        "profile_link": "string",
        "retweets": number,
        "views": number
      }}
    ]
  }},
  "video_metadata": {{
    "title": "string",
    "description": "string",
    "thumbnail_prompt": "string"
  }},
  "financial_analysis": {{
    "summary": "string",
    "hook": "string",
    "main_points": ["string"],
    "conclusion": "string"
  }},
  "full_script": "string",
  "segments": [
    {{
      "segment_id": number,
      "script_part": "string",
      "pose": {{
        "pose_number": number,
        "description": "string",
        "filename": "string",
        "pose_prompt": null
      }},
      "visual": {{
        "image_url": "string or null",
        "image_prompt": "string or null"
      }}
    }}
  ],
  "ticker_stocks": [
    {{
      "symbol": "string",
      "company_name": "string",
      "price": number,
      "change": number,
      "change_percent": number
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

    try:
        with open("data/character_poses/character_poses.json", "r", encoding="utf-8") as f:
            poses_data = json.load(f)
    except FileNotFoundError:
        print(
            "[ERROR] character_poses.json not found. Make sure it's in the 'data/character_poses' directory."
        )
        return

    creator = ProductionPlanCreator()
    production_plan = creator.create_plan(tweets_data, poses_data)

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
