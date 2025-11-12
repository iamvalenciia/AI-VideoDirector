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

    def __init__(self, output_dir: str = "output/financial_shorts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

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
        Assign illustrations to each scene.

        Strategy NUEVA (V3):
        - TODAS las escenas: SOLO ilustraciones en main_content (arriba)
        - Tweet/gráficos: Se manejan como capa global separada (no en escenas)
        - Round-robin de ilustraciones disponibles
        - NO más tweets/charts en main_content
        - El assembler renderiza tweet/chart como capa global independiente
        """
        illustrations = assets.get('illustrations', {}).get('images', [])

        # If no illustrations, use empty list
        if not illustrations:
            illustrations = []
            print("[WARNING] No illustrations available")

        # NUEVO: Round-robin simple de ilustraciones
        # TODAS las escenas obtienen ilustraciones (sin tweets ni charts aquí)
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
                print(f"[INFO] Scene {i+1}: Assigned illustration {illustration_idx}")
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

            # NOTE: Character poses are NO LONGER assigned (removed as requested)

            # Add captions with real word-level timestamps
            scene['captions'] = {
                'enabled': True,
                'words': scene['words'],  # Real timestamps from Whisper
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

        plan = {
            'video_metadata': {
                'title': assets['script'].get('title', 'Financial Short'),
                'duration_seconds': round(total_duration, 2),
                'resolution': '1080x1920',
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
