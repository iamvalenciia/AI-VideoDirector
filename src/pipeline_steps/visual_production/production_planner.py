"""
PRODUCTION PLANNER - Visual Production Planning

Uses OpenAI GPT-4o to analyze all generated assets and create a comprehensive
production plan for video assembly. This is the "brain" that coordinates all
elements: illustrations, character poses, stock charts, timing, music, etc.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI


class ProductionPlanner:
    """
    Creates a comprehensive production plan by analyzing all available assets
    and organizing them into a timeline-based production blueprint.

    This planner:
    - Reads timestamps, script, illustrations, poses, charts
    - Uses GPT-4o to intelligently plan visual transitions
    - Creates zoom/pan effects for dramatic emphasis
    - Times everything perfectly with narration
    - Outputs a single production_plan.json for assembly
    """

    def __init__(self, output_dir: str = "output/financial_shorts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"

    def load_all_assets(self) -> Dict:
        """Load all available assets for planning."""
        assets = {}

        # Required files
        required_files = {
            "timestamps": "timestamps.json",
            "financial_analysis": "financial_analysis.json",
            "image_prompts": "image_prompts.json"
        }

        for key, filename in required_files.items():
            file_path = self.output_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    assets[key] = json.load(f)
            else:
                print(f"[WARNING] Missing {filename}")
                assets[key] = None

        # Optional files
        optional_files = {
            "pose_catalog": "../character_poses/pose_catalog.json",
            "illustrations_manifest": "../illustrations/illustrations_manifest.json",
            "tweet_selection": "tweet_selection_report.json"
        }

        for key, filename in optional_files.items():
            file_path = self.output_dir / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    assets[key] = json.load(f)
            else:
                print(f"[INFO] Optional file not found: {filename}")
                assets[key] = None

        return assets

    def create_production_plan(self, assets: Dict) -> Dict:
        """
        Use GPT-4o to create intelligent production plan.

        This analyzes all assets and creates a timeline with:
        - Scene timings based on timestamps
        - Visual assignments (illustrations, poses, charts)
        - Camera movements (zoom in/out, pan)
        - Transition effects
        - Text captions with word-level highlighting
        """
        print("\n[PLANNER] Creating production plan with GPT-4o...")

        # Prepare data for GPT-4o
        timestamps = assets.get("timestamps", {})
        script_data = assets.get("financial_analysis", {}).get("script", {})
        image_prompts = assets.get("image_prompts", {})
        pose_catalog = assets.get("pose_catalog", {})
        illustrations = assets.get("illustrations_manifest", {})
        tweet_data = assets.get("tweet_selection", {})

        # Create comprehensive prompt
        system_prompt = """You are an expert video production planner for financial YouTube Shorts.

Your task is to create a detailed production plan that coordinates:
1. VISUALS: Illustrations, character poses, stock charts, tweet screenshots
2. TIMING: Word-level timestamps for perfect synchronization
3. EFFECTS: Zoom, pan, fade transitions
4. CAPTIONS: Word-level text with highlight on active word
5. AUDIO: Narration volume, background music volume
6. LAYOUT: Character on left, content on right, ticker at bottom

LAYOUT SPECIFICATIONS:
- Video: 1080x1920 (vertical YouTube Shorts)
- Top area (white): 0-180px
- Main content: 180-1400px
- Bottom ticker: 1400-1520px
- Bottom black area: 1520-1920px

VISUAL HIERARCHY:
- Layer 1 (back): Studio background (white)
- Layer 2: Tweet screenshot OR Illustration OR Stock chart
- Layer 3: Character pose (left side, on top of content)
- Layer 4: Bottom ticker (scrolling)
- Layer 5: Text captions (above ticker, 1350px Y position)

TIMING RULES:
- Match illustrations to narration using timestamps
- Change character pose every 5-8 seconds or on topic shifts
- Show stock charts when stocks are mentioned
- Keep each visual element visible for at least 3 seconds
- Transition duration: 0.5 seconds (smooth fade)

ZOOM EFFECTS:
- "zoom_in": Dramatic emphasis (1.0 → 1.3 scale, 2 seconds)
- "zoom_center": Center focus (1.0 → 1.5 scale, 3 seconds)
- "static": No movement (default)

TEXT CAPTIONS:
- Show current sentence being narrated
- Highlight active word in YELLOW (#FFD700)
- Inactive words in BLACK (#000000)
- Font: Bold, 32px
- Position: 1350px Y (above ticker)
- Background: Semi-transparent white box

AUDIO MIXING:
- Narration: 100% volume (primary)
- Background music: 20-25% volume (subtle, non-intrusive)
- Music file: "division/music/background_music.mp3"
- Music loops if video is longer than track

OUTPUT FORMAT (JSON):
{
  "video_metadata": {
    "title": "video title",
    "duration_seconds": total duration,
    "resolution": "1080x1920",
    "fps": 30
  },
  "audio": {
    "narration": {
      "file": "path to audio file",
      "volume": 1.0
    },
    "music": {
      "file": "division/music/background_music.mp3",
      "volume": 0.22,
      "loop": true
    }
  },
  "scenes": [
    {
      "scene_number": 1,
      "start_time": 0.0,
      "end_time": 5.2,
      "duration": 5.2,
      "narration_text": "text being narrated",
      "visuals": {
        "background": "studio_background.png",
        "main_content": {
          "type": "illustration",
          "file": "path to illustration",
          "effect": "zoom_in",
          "position": {"x": 75, "y": 300, "width": 930, "height": 700}
        },
        "character": {
          "pose_file": "path to character pose",
          "position": {"x": 50, "y": 600, "width": 400, "height": 700}
        },
        "ticker": {
          "file": "bottom_ticker.png",
          "scroll_speed": 100,
          "position": {"x": 0, "y": 1400, "width": 1080, "height": 120}
        }
      },
      "captions": {
        "enabled": true,
        "words": [
          {"word": "A", "start": 0.0, "end": 0.1},
          {"word": "one", "start": 0.1, "end": 0.3},
          {"word": "trillion", "start": 0.3, "end": 0.8}
        ],
        "style": {
          "font_size": 32,
          "font_weight": "bold",
          "active_color": "#FFD700",
          "inactive_color": "#000000",
          "background": "rgba(255, 255, 255, 0.8)",
          "position_y": 1350
        }
      },
      "transition": {
        "type": "fade",
        "duration": 0.5
      }
    }
  ],
  "stock_charts": [
    {
      "symbol": "TSLA",
      "file": "output/stock_charts/tsla_chart.png",
      "show_at_scenes": [6, 7]
    }
  ]
}

Be strategic and intelligent. Create smooth, professional pacing."""

        # Prepare user prompt with all data
        user_prompt = f"""Create a production plan for this financial video.

TIMESTAMPS DATA:
{json.dumps(timestamps, indent=2)[:3000]}

SCRIPT DATA:
{json.dumps(script_data, indent=2)[:2000]}

IMAGE PROMPTS (Illustrations available):
{json.dumps(image_prompts, indent=2)[:2000]}

CHARACTER POSES AVAILABLE:
{json.dumps(pose_catalog.get('poses', [])[:10] if pose_catalog else [], indent=2)[:1500]}

ILLUSTRATIONS MANIFEST:
{json.dumps(illustrations.get('images', [])[:5] if illustrations else [], indent=2)[:1500]}

STOCK DATA:
{json.dumps(tweet_data.get('selected_tweet', {}).get('related_stocks', []) if tweet_data else [], indent=2)[:500]}

Create a complete production plan with intelligent scene breaks, visual assignments, and perfect timing."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=8000
            )

            plan = json.loads(response.choices[0].message.content)
            print(f"[OK] Production plan created with {len(plan.get('scenes', []))} scenes")
            return plan

        except Exception as e:
            print(f"[ERROR] Failed to create production plan: {str(e)}")
            raise

    def save_production_plan(self, plan: Dict, filename: str = "production_plan.json") -> str:
        """Save production plan to JSON file."""
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)

        print(f"[OK] Production plan saved: {output_path}")
        return str(output_path)

    def create_and_save_plan(self) -> str:
        """
        Complete workflow: load assets, create plan, save results.

        Returns:
            Path to production plan file
        """
        print(f"\n{'='*60}")
        print(f"PRODUCTION PLANNING")
        print(f"{'='*60}")

        # Load all assets
        print("\n[1/3] Loading assets...")
        assets = self.load_all_assets()

        # Create plan
        print("\n[2/3] Creating intelligent production plan...")
        plan = self.create_production_plan(assets)

        # Save plan
        print("\n[3/3] Saving production plan...")
        plan_path = self.save_production_plan(plan)

        # Print summary
        print(f"\n{'='*60}")
        print(f"PRODUCTION PLANNING COMPLETE")
        print(f"{'='*60}")
        print(f"Total scenes: {len(plan.get('scenes', []))}")
        print(f"Total duration: {plan.get('video_metadata', {}).get('duration_seconds', 0)} seconds")
        print(f"Output file: {plan_path}")

        return plan_path


# Test/demo code
if __name__ == "__main__":
    planner = ProductionPlanner()
    plan_path = planner.create_and_save_plan()
    print(f"\n✅ Production plan created: {plan_path}")
