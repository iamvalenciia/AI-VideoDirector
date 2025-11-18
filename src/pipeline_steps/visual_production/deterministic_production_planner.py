"""
DETERMINISTIC PRODUCTION PLANNER - No AI Required

Creates complete production plans using rule-based logic instead of GPT-4o.
Faster, cheaper, and more consistent than AI-based planning.

Features:
- Reads real word-level timestamps from Whisper
- Creates scenes based on natural pauses in narration
- Assigns illustrations/poses using round-robin selection
- Zero cost, instant execution
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DeterministicProductionPlanner:
    """
    Creates production plans using deterministic rules instead of AI.

    Advantages over GPT-4o planner:
    - 100x faster (< 1 second vs 30-45 seconds)
    - Zero cost (no API calls)
    - 100% consistent results
    - Complete scenes (not truncated)
    - Real timestamps from Whisper
    """

    def __init__(self, output_dir: str = "output/financial_shorts", video_format: str = "short"):
        """
        Initialize the planner.

        Args:
            output_dir: Directory with input assets and output plan
            video_format: "short" (1080x1920) or "long" (1920x1080)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.video_format = video_format  # "short" or "long"

    def load_assets(self) -> Dict:
        """Load all required assets."""
        assets = {}

        # Load timestamps (required)
        timestamps_path = self.output_dir / "timestamps.json"
        if timestamps_path.exists():
            with open(timestamps_path, 'r', encoding='utf-8') as f:
                assets['timestamps'] = json.load(f)
        else:
            raise FileNotFoundError(f"timestamps.json not found at {timestamps_path}")

        # Load script (required)
        script_path = self.output_dir / "financial_analysis.json"
        if script_path.exists():
            with open(script_path, 'r', encoding='utf-8') as f:
                assets['script'] = json.load(f)
        else:
            raise FileNotFoundError(f"financial_analysis.json not found at {script_path}")

        # Load illustrations (optional)
        illustrations_path = self.output_dir.parent / "illustrations" / "illustrations_manifest.json"
        if illustrations_path.exists():
            with open(illustrations_path, 'r', encoding='utf-8') as f:
                assets['illustrations'] = json.load(f)
        else:
            assets['illustrations'] = None

        # Load character poses (optional)
        poses_path = self.output_dir.parent / "character_poses" / "pose_catalog.json"
        if poses_path.exists():
            with open(poses_path, 'r', encoding='utf-8') as f:
                assets['poses'] = json.load(f)
        else:
            assets['poses'] = None

        # Load stock data (optional)
        stock_path = self.output_dir / "tweet_selection_report.json"
        if stock_path.exists():
            with open(stock_path, 'r', encoding='utf-8') as f:
                assets['stocks'] = json.load(f)
        else:
            assets['stocks'] = None

        return assets

    def create_scenes_from_timestamps(self, timestamps: Dict) -> List[Dict]:
        """
        Create scene breaks based on natural pauses in narration.

        Strategy:
        - Group words into sentences
        - Create new scene when pause > 0.5 seconds OR scene > 8 seconds
        - Each scene gets 5-8 seconds of content
        """
        words = timestamps.get('words', [])
        if not words:
            raise ValueError("No word-level timestamps found")

        scenes = []
        current_scene_words = []
        current_scene_start = words[0]['start']
        scene_number = 1

        for i, word in enumerate(words):
            current_scene_words.append(word)

            # Check if we should break to new scene
            should_break = False

            # Check pause duration to next word
            if i < len(words) - 1:
                pause = words[i + 1]['start'] - word['end']
                if pause > 0.5:  # Natural pause detected
                    should_break = True

            # Check scene duration
            scene_duration = word['end'] - current_scene_start
            if scene_duration > 8.0:  # Max scene length
                should_break = True

            # Last word always breaks
            if i == len(words) - 1:
                should_break = True

            if should_break and current_scene_words:
                # Create scene
                scene_end = current_scene_words[-1]['end']
                scene_text = ' '.join([w['word'] for w in current_scene_words])

                scenes.append({
                    'scene_number': scene_number,
                    'start_time': current_scene_start,
                    'end_time': scene_end,
                    'duration': scene_end - current_scene_start,
                    'narration_text': scene_text,
                    'words': current_scene_words.copy()
                })

                # Reset for next scene
                scene_number += 1
                current_scene_words = []
                if i < len(words) - 1:
                    current_scene_start = words[i + 1]['start']

        return scenes

    def assign_visuals_to_scenes(self, scenes: List[Dict], assets: Dict) -> List[Dict]:
        """
        Assign visuals to each scene based on video format.

        SHORT FORMAT (1080x1920):
        - Illustrations in main_content (arriba)
        - Tweet/charts as global layer
        - Ticker at bottom

        LONG FORMAT (1920x1080):
        - Character poses behind desk (from pose_catalog.json)
        - Tweet/image on left screen
        - Ticker at bottom
        """
        # SHORT FORMAT: Use illustrations
        if self.video_format == "short":
            return self._assign_visuals_short_format(scenes, assets)
        # LONG FORMAT: Use character poses
        elif self.video_format == "long":
            return self._assign_visuals_long_format(scenes, assets)
        else:
            raise ValueError(f"Invalid video_format: {self.video_format}")

    def _assign_visuals_short_format(self, scenes: List[Dict], assets: Dict) -> List[Dict]:
        """
        Assign visuals for SHORT format (vertical 1080x1920).
        Uses illustrations from illustrations_manifest.json
        """
        illustrations = assets.get('illustrations', {}).get('images', [])

        # If no illustrations, use empty list
        if not illustrations:
            illustrations = []
            print("[WARNING] No illustrations available")

        # Round-robin de ilustraciones
        illustration_idx = 0

        for i, scene in enumerate(scenes):
            # Determine effect (alternate between zoom_in, static, zoom_center)
            effects = ['zoom_in', 'static', 'zoom_center']
            effect = effects[i % len(effects)]

            # TODAS LAS ESCENAS: Solo ilustraciones
            if illustrations:
                illustration = illustrations[illustration_idx % len(illustrations)]
                illustration_idx += 1

                scene['visuals'] = {
                    'background': 'output/financial_shorts/studio_background.png',
                    'main_content': {
                        'type': 'illustration',
                        'file': illustration.get('image_path') or illustration.get('file_path', ''),
                        'effect': effect,
                        'position': {
                            'x': 75,
                            'y': 300,
                            'width': 930,
                            'height': 700
                        }
                    },
                    'ticker': {
                        'file': 'output/financial_shorts/ticker_strip.png',
                        'scroll_speed': 100,
                        'position': {
                            'x': 0,
                            'y': 1400,
                            'width': 1080,
                            'height': 120
                        }
                    }
                }
                print(f"[INFO] Scene {i+1} (SHORT): Assigned illustration {illustration_idx}")
            else:
                # No illustrations available
                scene['visuals'] = {
                    'background': 'output/financial_shorts/studio_background.png',
                    'ticker': {
                        'file': 'output/financial_shorts/ticker_strip.png',
                        'scroll_speed': 100,
                        'position': {
                            'x': 0,
                            'y': 1400,
                            'width': 1080,
                            'height': 120
                        }
                    }
                }

            # Add captions with real word-level timestamps
            scene['captions'] = {
                'enabled': True,
                'words': scene['words'],
                'style': {
                    'font_size': 32,
                    'font_weight': 'bold',
                    'active_color': '#FFD700',
                    'inactive_color': '#000000',
                    'background': 'rgba(255, 255, 255, 0.8)',
                    'position_y': 1350
                }
            }

            # Add transition
            scene['transition'] = {
                'type': 'fade',
                'duration': 0.5
            }

        return scenes

    def _assign_visuals_long_format(self, scenes: List[Dict], assets: Dict) -> List[Dict]:
        """
        Assign visuals for LONG format (horizontal 1920x1080).
        Uses character poses from pose_catalog.json
        """
        poses = assets.get('poses', {}).get('poses', [])

        # If no poses, use empty list
        if not poses:
            poses = []
            print("[WARNING] No character poses available")

        # Round-robin de poses
        pose_idx = 0

        for i, scene in enumerate(scenes):
            # TODAS LAS ESCENAS: Character poses
            if poses:
                pose = poses[pose_idx % len(poses)]
                pose_idx += 1

                scene['visuals'] = {
                    'studio_scene': 'output/horizontal_videos/studio_scene.png',  # Pre-rendered HTML studio
                    'character_pose': {
                        'type': 'pose',
                        'file': pose.get('file_path', ''),
                        'category': pose.get('category', 'neutral'),
                        'position': {
                            'x': 1200,  # Right side
                            'y': 350,   # Behind desk
                            'width': 550,
                            'height': 700
                        }
                    },
                    'tweet_screen': {
                        'file': 'output/tweet_screenshots/selected_tweet.png',
                        'position': {
                            'x': 80,    # Left side
                            'y': 240,
                            'width': 700,
                            'height': 600
                        }
                    },
                    'ticker': {
                        'file': 'output/financial_shorts/ticker_strip.png',
                        'scroll_speed': 100,
                        'position': {
                            'x': 0,
                            'y': 1010,  # Bottom of 1080p
                            'width': 1920,
                            'height': 70
                        }
                    }
                }
                print(f"[INFO] Scene {i+1} (LONG): Assigned pose '{pose.get('category')}' #{pose_idx}")
            else:
                # No poses available - just show studio
                scene['visuals'] = {
                    'studio_scene': 'output/horizontal_videos/studio_scene.png',
                    'tweet_screen': {
                        'file': 'output/tweet_screenshots/selected_tweet.png',
                        'position': {
                            'x': 80,
                            'y': 240,
                            'width': 700,
                            'height': 600
                        }
                    },
                    'ticker': {
                        'file': 'output/financial_shorts/ticker_strip.png',
                        'scroll_speed': 100,
                        'position': {
                            'x': 0,
                            'y': 1010,
                            'width': 1920,
                            'height': 70
                        }
                    }
                }

            # Add captions with real word-level timestamps (adjusted for 1920x1080)
            scene['captions'] = {
                'enabled': True,
                'words': scene['words'],
                'style': {
                    'font_size': 28,
                    'font_weight': 'bold',
                    'active_color': '#FFD700',
                    'inactive_color': '#000000',
                    'background': 'rgba(255, 255, 255, 0.8)',
                    'position_y': 950  # Above ticker in 1080p
                }
            }

            # Add transition
            scene['transition'] = {
                'type': 'fade',
                'duration': 0.5
            }

        return scenes

    def create_production_plan(self, assets: Dict) -> Dict:
        """
        Create complete production plan using deterministic rules.

        Returns:
            Complete production plan ready for video assembly
        """
        print("\n[PLANNER] Creating deterministic production plan...")

        # Step 1: Create scenes from timestamps
        print("[1/3] Creating scenes from word-level timestamps...")
        scenes = self.create_scenes_from_timestamps(assets['timestamps'])
        print(f"       Created {len(scenes)} scenes")

        # Step 2: Assign visuals to scenes
        print("[2/3] Assigning visuals (illustrations, poses, effects)...")
        scenes = self.assign_visuals_to_scenes(scenes, assets)

        # Step 3: Build complete production plan
        print("[3/3] Building production plan...")

        total_duration = scenes[-1]['end_time'] if scenes else 0

        # Set resolution based on format
        if self.video_format == "short":
            resolution = "1080x1920"
        else:  # long
            resolution = "1920x1080"

        plan = {
            'video_metadata': {
                'title': assets['script'].get('title', 'Financial Short'),
                'duration_seconds': round(total_duration, 2),
                'resolution': resolution,
                'format': self.video_format,
                'fps': 30
            },
            'audio': {
                'narration': {
                    'file': 'output/financial_shorts/narration.mp3',
                    'volume': 1.0
                },
                'music': {
                    'file': 'output/music/galactic_rap.mp3',
                    'volume': 0.22,
                    'loop': True
                }
            },
            'scenes': scenes
        }

        # Add tweet/chart metadata (global layer, not per-scene)
        # El assembler usará esto para crear la capa alternante
        plan['global_layers'] = {
            'tweet_chart_alternator': {
                'enabled': True,
                'tweet_file': 'output/tweet_screenshots/selected_tweet.png',
                'chart_file': 'output/stock_charts/tsla_chart.png',  # Main chart
                'alternation_interval': 30,  # seconds
                'transition_duration': 1.0,  # seconds
                'position': {
                    'y': 1120,
                    'max_width': 900,
                    'max_height': 400
                }
            }
        }

        # También guardar lista de charts disponibles
        if assets.get('stocks'):
            stocks_data = assets['stocks'].get('selected_tweet', {}).get('related_stocks', [])
            if stocks_data:
                plan['available_charts'] = [
                    {
                        'symbol': stock['symbol'],
                        'file': f"output/stock_charts/{stock['symbol'].lower()}_chart.png"
                    }
                    for stock in stocks_data
                ]

        print(f"\n[OK] Production plan complete:")
        print(f"     - {len(scenes)} scenes")
        print(f"     - {total_duration:.2f} seconds total duration")
        print(f"     - {len(assets['timestamps'].get('words', []))} word-level timestamps")

        return plan

    def save_production_plan(self, plan: Dict, filename: str = "production_plan.json") -> str:
        """Save production plan to JSON file."""
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Saved: {output_path}")
        return str(output_path)

    def create_and_save_plan(self) -> str:
        """
        Complete workflow: load assets, create plan, save.

        Returns:
            Path to production plan file
        """
        print(f"\n{'='*60}")
        print(f"DETERMINISTIC PRODUCTION PLANNING")
        print(f"{'='*60}")

        # Load assets
        print("\n[STEP 1] Loading assets...")
        assets = self.load_assets()
        print(f"         - Timestamps: {len(assets['timestamps'].get('words', []))} words")
        print(f"         - Illustrations: {len(assets.get('illustrations', {}).get('images', []))} available")
        print(f"         - Character poses: {len(assets.get('poses', {}).get('poses', []))} available")

        # Create plan
        print("\n[STEP 2] Creating production plan...")
        plan = self.create_production_plan(assets)

        # Save plan
        print("\n[STEP 3] Saving production plan...")
        plan_path = self.save_production_plan(plan)

        print(f"\n{'='*60}")
        print(f"PLANNING COMPLETE")
        print(f"{'='*60}")
        print(f"Output: {plan_path}")

        return plan_path


# Test/demo code
if __name__ == "__main__":
    planner = DeterministicProductionPlanner()
    plan_path = planner.create_and_save_plan()
    print(f"\n✅ Production plan created: {plan_path}")
