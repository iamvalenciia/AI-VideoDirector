"""
Test script to generate production plan for LONG format videos
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline_steps.visual_production.deterministic_production_planner import DeterministicProductionPlanner

def main():
    print("="*60)
    print("TESTING LONG FORMAT PRODUCTION PLAN")
    print("="*60)

    # Create planner with LONG format
    planner = DeterministicProductionPlanner(
        output_dir="output/financial_shorts",
        video_format="long"  # ← Key parameter
    )

    try:
        # Generate plan
        plan_path = planner.create_and_save_plan()

        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print(f"Plan saved to: {plan_path}")

        # Show sample scene structure
        import json
        with open(plan_path, 'r') as f:
            plan = json.load(f)

        print(f"\nVideo format: {plan['video_metadata']['format']}")
        print(f"Resolution: {plan['video_metadata']['resolution']}")
        print(f"Total scenes: {len(plan['scenes'])}")

        if plan['scenes']:
            print(f"\nSample scene structure:")
            scene = plan['scenes'][0]
            print(f"  - scene_number: {scene['scene_number']}")
            print(f"  - duration: {scene['duration']:.2f}s")
            print(f"  - visuals keys: {list(scene['visuals'].keys())}")
            if 'character_pose' in scene['visuals']:
                print(f"  - character_pose file: {scene['visuals']['character_pose']['file']}")
                print(f"  - character_pose category: {scene['visuals']['character_pose']['category']}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
