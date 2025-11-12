"""
Intelligent Pose Selector - Selects appropriate character poses for video segments
Uses AI to match poses with segment content and timing
"""

import json
import os
import random
from pathlib import Path
from typing import List, Dict, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()


class PoseSelector:
    """
    Intelligently selects character poses based on:
    - Segment content/script
    - Timing in the video
    - Emotional tone
    - Action type (explaining, reacting, emphasizing, etc.)
    """

    def __init__(self, pose_catalog_path: str = "output/character_poses/pose_catalog.json"):
        """
        Initialize the pose selector

        Args:
            pose_catalog_path: Path to pose catalog JSON file
        """
        self.pose_catalog_path = Path(pose_catalog_path)

        # Load pose catalog
        if not self.pose_catalog_path.exists():
            raise FileNotFoundError(f"Pose catalog not found: {pose_catalog_path}")

        with open(self.pose_catalog_path, 'r', encoding='utf-8') as f:
            self.catalog = json.load(f)

        self.poses = self.catalog["poses"]
        self.poses_by_category = self._organize_by_category()

        # Initialize Claude for intelligent selection
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=api_key)

    def _organize_by_category(self) -> Dict[str, List[Dict]]:
        """
        Organize poses by category for quick filtering

        Returns:
            Dictionary mapping category to list of poses
        """
        organized = {}
        for pose in self.poses:
            category = pose["category"]
            if category not in organized:
                organized[category] = []
            organized[category].append(pose)
        return organized

    def get_random_pose(self, category: Optional[str] = None) -> Dict:
        """
        Get a random pose, optionally filtered by category

        Args:
            category: Optional category filter (presenting, talking, reacting, emphasizing, neutral)

        Returns:
            Random pose metadata
        """
        if category and category in self.poses_by_category:
            return random.choice(self.poses_by_category[category])
        return random.choice(self.poses)

    def select_pose_for_segment(
        self,
        segment_text: str,
        segment_index: int,
        total_segments: int
    ) -> Dict:
        """
        Intelligently select a pose based on segment content using Claude

        Args:
            segment_text: Text/script for this segment
            segment_index: Index of current segment (0-based)
            total_segments: Total number of segments

        Returns:
            Selected pose metadata
        """
        # Create prompt for Claude to analyze segment and suggest pose
        prompt = f"""Analyze this video segment and select the most appropriate character pose category.

Segment {segment_index + 1} of {total_segments}:
Text: "{segment_text}"

Available pose categories:
1. PRESENTING - pointing, gesturing, showing something (confident, welcoming)
2. TALKING - explaining, discussing, conversing (animated, casual, serious)
3. REACTING - surprised, shocked, impressed, concerned (emotional responses)
4. EMPHASIZING - making strong points, being authoritative (powerful, dramatic)
5. NEUTRAL - standing, waiting, listening (calm, professional)

Based on the segment content, which ONE category is most appropriate?
Respond with ONLY the category name (presenting/talking/reacting/emphasizing/neutral).

Consider:
- Opening segments often use "presenting" or "neutral"
- Explanations use "talking"
- Surprising facts use "reacting"
- Key points use "emphasizing"
- Transitions use "neutral"
"""

        try:
            # Ask Claude to select category
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=50,
                messages=[{"role": "user", "content": prompt}]
            )

            category = response.content[0].text.strip().lower()

            # Validate category
            valid_categories = ["presenting", "talking", "reacting", "emphasizing", "neutral"]
            if category not in valid_categories:
                print(f"[WARNING] Invalid category '{category}', using 'talking' as fallback")
                category = "talking"

            # Get random pose from selected category
            selected_pose = self.get_random_pose(category)

            print(f"[POSE SELECTOR] Segment {segment_index + 1}: '{segment_text[:50]}...' → {category} → {selected_pose['name']}")

            return selected_pose

        except Exception as e:
            print(f"[ERROR] Pose selection failed: {str(e)}, using random pose")
            return self.get_random_pose()

    def select_poses_for_segments(
        self,
        segments: List[str]
    ) -> List[Dict]:
        """
        Select appropriate poses for multiple segments

        Args:
            segments: List of segment texts

        Returns:
            List of selected pose metadata (one per segment)
        """
        print(f"\n[POSE SELECTOR] Selecting poses for {len(segments)} segments...")

        selected_poses = []
        for i, segment_text in enumerate(segments):
            pose = self.select_pose_for_segment(segment_text, i, len(segments))
            selected_poses.append(pose)

        print(f"[OK] Selected {len(selected_poses)} poses\n")
        return selected_poses

    def get_pose_by_name(self, pose_name: str) -> Optional[Dict]:
        """
        Get specific pose by name

        Args:
            pose_name: Name of the pose

        Returns:
            Pose metadata or None if not found
        """
        for pose in self.poses:
            if pose["name"] == pose_name:
                return pose
        return None

    def get_poses_by_category(self, category: str) -> List[Dict]:
        """
        Get all poses in a specific category

        Args:
            category: Category name

        Returns:
            List of poses in that category
        """
        return self.poses_by_category.get(category, [])


def main():
    """Example usage"""
    # Example segments from a financial short
    example_segments = [
        "Welcome to today's financial update on the markets.",
        "Tesla stock has surged by 15% this week, shocking analysts.",
        "This massive gain is primarily due to strong Q4 delivery numbers.",
        "Investors are now questioning whether this rally is sustainable.",
        "Let's break down the key factors driving this movement."
    ]

    selector = PoseSelector()

    # Select poses for all segments
    selected_poses = selector.select_poses_for_segments(example_segments)

    print("\n" + "="*60)
    print("SELECTED POSES:")
    print("="*60)
    for i, (segment, pose) in enumerate(zip(example_segments, selected_poses)):
        print(f"\nSegment {i + 1}: {segment[:50]}...")
        print(f"  → Pose: {pose['category']}/{pose['name']}")
        print(f"  → File: {pose['filename']}")


if __name__ == "__main__":
    main()
