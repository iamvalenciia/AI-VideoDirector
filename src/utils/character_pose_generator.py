"""
Character Pose Generator - AI-Generated Character Poses
Uses Gemini 2.0 Flash to generate a library of character poses
Creates 50 pre-generated poses with metadata for efficient video production
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv
from PIL import Image

load_dotenv()


class CharacterPoseGenerator:
    """
    Generates a library of character poses using Gemini 2.5 Flash with image generation
    Each pose has a description and is catalogued for intelligent selection
    Uses base_image.png as reference to maintain character consistency
    """

    def __init__(
        self,
        output_dir: str = "output/character_poses",
        reference_image_path: str = "src/image/base_image.png",
        model_name: str = "gemini-2.5-flash-image"
    ):
        """
        Initialize the pose generator

        Args:
            output_dir: Directory to save generated poses
            reference_image_path: Path to base character image for reference
            model_name: Gemini model to use (default: gemini-2.5-flash-image)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Reference image path
        self.reference_image_path = Path(reference_image_path)
        if not self.reference_image_path.exists():
            print(f"[WARNING] Reference image not found: {reference_image_path}")
            print("[WARNING] Poses will be generated without reference consistency")
            self.reference_image_path = None

        # Initialize Gemini client (NEW API)
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

        # Pose categories and descriptions
        self.pose_templates = self._get_pose_templates()

    def _get_pose_templates(self) -> List[Dict[str, str]]:
        """
        Define 50 different pose templates with descriptions

        Returns:
            List of pose dictionaries with category, name, and prompt
        """
        poses = []

        # PRESENTING POSES (10)
        # Context: Character is on LEFT, presenting content that appears to their RIGHT
        presenting_poses = [
            {"category": "presenting", "name": "pointing_right_screen", "description": "Character pointing to the RIGHT toward the presentation screen with confident smile"},
            {"category": "presenting", "name": "gesturing_right_open", "description": "Character with open hand gesturing toward the RIGHT, presenting the screen content"},
            {"category": "presenting", "name": "both_hands_presenting_right", "description": "Character with both hands open, presenting toward the RIGHT side screen"},
            {"category": "presenting", "name": "gesturing_up_right", "description": "Character gesturing upward and to the RIGHT with excited expression about screen content"},
            {"category": "presenting", "name": "palm_out_right", "description": "Character with palm extended toward the RIGHT, showcasing screen information"},
            {"category": "presenting", "name": "open_arm_welcome_right", "description": "Character with arm extended toward the RIGHT in welcoming gesture to screen"},
            {"category": "presenting", "name": "explaining_hand_right", "description": "Character with hand raised, gesturing toward the RIGHT while explaining"},
            {"category": "presenting", "name": "confident_presenting", "description": "Character standing confidently while presenting, body angled slightly toward the RIGHT"},
            {"category": "presenting", "name": "thinking_looking_right", "description": "Character with hand on chin, looking thoughtfully toward the RIGHT screen"},
            {"category": "presenting", "name": "inviting_gesture_right", "description": "Character with inviting hand gesture toward the RIGHT presentation area"},
        ]
        poses.extend(presenting_poses)

        # TALKING/EXPLAINING POSES (10)
        # Context: Character is explaining content while referencing the screen to their RIGHT
        talking_poses = [
            {"category": "talking", "name": "casual_talking", "description": "Character in casual talking pose to camera, relaxed expression, body open"},
            {"category": "talking", "name": "animated_explaining", "description": "Character with animated expression while explaining, hands active near body"},
            {"category": "talking", "name": "serious_discussion", "description": "Character in serious discussion pose facing camera, focused expression"},
            {"category": "talking", "name": "enthusiastic_talking", "description": "Character talking with enthusiastic energy, gesturing naturally"},
            {"category": "talking", "name": "counting_fingers", "description": "Character counting points on fingers while facing camera"},
            {"category": "talking", "name": "emphatic_gesture", "description": "Character making emphatic hand gesture while speaking to camera"},
            {"category": "talking", "name": "questioning_pose", "description": "Character with questioning expression, hand raised inquisitively"},
            {"category": "talking", "name": "looking_at_screen", "description": "Character looking toward the RIGHT screen while talking about it"},
            {"category": "talking", "name": "hand_to_chest", "description": "Character with hand to chest, sincere expression facing camera"},
            {"category": "talking", "name": "two_hands_explaining", "description": "Character using both hands in front to explain concept to camera"},
        ]
        poses.extend(talking_poses)

        # REACTING POSES (10)
        # Context: Character is reacting to information on the screen to their RIGHT
        reacting_poses = [
            {"category": "reacting", "name": "surprised_reaction", "description": "Character with surprised expression looking toward the RIGHT, hands up in shock"},
            {"category": "reacting", "name": "shocked_disbelief", "description": "Character showing shocked disbelief, looking toward the RIGHT screen"},
            {"category": "reacting", "name": "impressed_nod", "description": "Character nodding with impressed expression toward the RIGHT"},
            {"category": "reacting", "name": "skeptical_look", "description": "Character with skeptical raised eyebrow, glancing toward the RIGHT"},
            {"category": "reacting", "name": "excited_celebration", "description": "Character celebrating with excited expression, reacting to screen content"},
            {"category": "reacting", "name": "concerned_worry", "description": "Character showing concerned worried expression looking toward the RIGHT"},
            {"category": "reacting", "name": "disappointed_sigh", "description": "Character with disappointed expression facing camera, sighing"},
            {"category": "reacting", "name": "happy_smile", "description": "Character with genuine happy smile facing camera"},
            {"category": "reacting", "name": "confused_shrug", "description": "Character shrugging with confused expression facing camera"},
            {"category": "reacting", "name": "thoughtful_consideration", "description": "Character in thoughtful consideration, looking toward the RIGHT screen"},
        ]
        poses.extend(reacting_poses)

        # EMPHASIZING POSES (10)
        # Context: Character is making strong points, often referencing the screen
        emphasizing_poses = [
            {"category": "emphasizing", "name": "fist_pump", "description": "Character with fist pump facing camera, powerful energy"},
            {"category": "emphasizing", "name": "pointing_right_emphasis", "description": "Character pointing toward the RIGHT screen with strong emphasis"},
            {"category": "emphasizing", "name": "arms_crossed_confident", "description": "Character with arms crossed facing camera, confident authority"},
            {"category": "emphasizing", "name": "leaning_forward", "description": "Character leaning forward toward camera with intensity"},
            {"category": "emphasizing", "name": "hands_together_serious", "description": "Character with hands together facing camera, serious tone"},
            {"category": "emphasizing", "name": "raised_hand_stop", "description": "Character with raised hand in stop gesture toward camera"},
            {"category": "emphasizing", "name": "clapping_hands", "description": "Character clapping hands together for emphasis"},
            {"category": "emphasizing", "name": "dramatic_pause", "description": "Character in dramatic pause facing camera"},
            {"category": "emphasizing", "name": "strong_stance", "description": "Character in strong grounded stance facing camera"},
            {"category": "emphasizing", "name": "determined_look", "description": "Character with determined expression, focused on camera"},
        ]
        poses.extend(emphasizing_poses)

        # NEUTRAL/TRANSITION POSES (10)
        # Context: Character in neutral professional poses, ready to present
        neutral_poses = [
            {"category": "neutral", "name": "standing_neutral", "description": "Character standing in neutral professional position facing camera"},
            {"category": "neutral", "name": "relaxed_waiting", "description": "Character in relaxed waiting pose, professional demeanor"},
            {"category": "neutral", "name": "professional_stance", "description": "Character in professional business stance facing camera"},
            {"category": "neutral", "name": "slight_smile", "description": "Character with slight professional smile facing camera"},
            {"category": "neutral", "name": "attentive_ready", "description": "Character in attentive ready-to-present pose"},
            {"category": "neutral", "name": "calm_composure", "description": "Character with calm composed demeanor facing camera"},
            {"category": "neutral", "name": "ready_position", "description": "Character in ready-to-present position, hands relaxed"},
            {"category": "neutral", "name": "standing_angled", "description": "Character standing at slight angle, body open to camera"},
            {"category": "neutral", "name": "hands_relaxed", "description": "Character with hands naturally relaxed at sides"},
            {"category": "neutral", "name": "professional_waiting", "description": "Character in professional waiting pose, ready to engage"},
        ]
        poses.extend(neutral_poses)

        return poses

    def _create_image_prompt(self, pose_description: str) -> str:
        """
        Create detailed prompt for Gemini image generation
        IMPORTANT: Maintains consistency with base_image.png reference

        Args:
            pose_description: Description of the pose

        Returns:
            Detailed prompt for image generation
        """
        base_prompt = f"""
Create a character pose matching the reference image EXACTLY.

CRITICAL REQUIREMENTS:
- Copy the EXACT same character appearance from the reference image
- Same face, eyes, hair, clothing, skin tone - everything identical
- SOLID WHITE BACKGROUND (not transparent, pure white #FFFFFF)
- Match the exact art style and quality of the reference image
- Do not modify or add any details to the character's appearance

Pose: {pose_description}

CONTEXT:
- Character is positioned on the LEFT side of the frame
- There is a presentation screen on the RIGHT side (off-camera)
- Character is presenting information that appears to their RIGHT
- All gestures should reference the RIGHT side where content appears

Style:
- Professional financial news presenter
- Business casual attire (same as reference)
- Clean, modern broadcast look
- Full body or upper body shot
- Centered in frame
- Professional studio lighting
- High resolution, broadcast quality

Background: SOLID WHITE (#FFFFFF), no transparency, no shadows
"""
        return base_prompt.strip()

    def _pose_already_exists(self, pose_number: int, category: str, name: str) -> bool:
        """
        Check if pose already exists to avoid regeneration

        Args:
            pose_number: Number of the pose
            category: Category name
            name: Pose name

        Returns:
            True if pose already exists
        """
        filename = f"pose_{pose_number:02d}_{category}_{name}.png"
        output_path = self.output_dir / filename
        return output_path.exists()

    def _load_reference_image(self) -> Optional[Image.Image]:
        """
        Load the reference image for character consistency

        Returns:
            PIL Image or None if not available
        """
        if not self.reference_image_path or not self.reference_image_path.exists():
            return None

        try:
            ref_image = Image.open(self.reference_image_path)
            print(f"[REF] Using reference image: {self.reference_image_path.name}")
            return ref_image
        except Exception as e:
            print(f"[WARNING] Could not load reference image: {str(e)}")
            return None

    async def generate_single_pose(
        self,
        pose_info: Dict[str, str],
        pose_number: int,
        skip_if_exists: bool = True
    ) -> Optional[Dict[str, str]]:
        """
        Generate a single character pose using Gemini with reference image

        Args:
            pose_info: Dictionary with category, name, and description
            pose_number: Number of this pose (1-50)
            skip_if_exists: Skip generation if pose already exists

        Returns:
            Dictionary with pose metadata and file path, or None if failed
        """
        category = pose_info["category"]
        name = pose_info["name"]
        description = pose_info["description"]

        # Check if already exists
        if skip_if_exists and self._pose_already_exists(pose_number, category, name):
            filename = f"pose_{pose_number:02d}_{category}_{name}.png"
            output_path = self.output_dir / filename
            print(f"[SKIP {pose_number}/50] Already exists: {filename}")
            return {
                "pose_number": pose_number,
                "category": category,
                "name": name,
                "description": description,
                "file_path": str(output_path),
                "filename": filename
            }

        print(f"[POSE {pose_number}/50] Generating: {category}/{name}")

        # Load reference image
        reference_image = self._load_reference_image()

        # Create prompt
        image_prompt = self._create_image_prompt(description)

        try:
            # Build content list for Gemini
            contents = []

            # If we have a reference image, load it and add to contents
            if reference_image and self.reference_image_path.exists():
                # Load reference image as bytes
                with open(self.reference_image_path, 'rb') as img_file:
                    image_bytes = img_file.read()

                # Create Part from bytes
                image_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type='image/png'
                )

                print(f"[REF] Using base_image.png as reference for consistency")

                # Add prompt first, then reference image
                contents = [image_prompt, image_part]
            else:
                # No reference image - just use the prompt
                contents = [image_prompt]

            # Generate content with image response using Gemini 2.5 Flash
            config = types.GenerateContentConfig(
                response_modalities=['Image'],
                temperature=0.4,  # Lower temperature for consistency
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )

            # Extract and save the generated image
            filename = f"pose_{pose_number:02d}_{category}_{name}.png"
            output_path = self.output_dir / filename

            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part in candidate.content.parts:
                        if part.inline_data and part.inline_data.data:
                            # Save image bytes to file
                            with open(output_path, 'wb') as f:
                                f.write(part.inline_data.data)
                            print(f"[OK] Saved: {filename}")

                            # Return metadata
                            return {
                                "pose_number": pose_number,
                                "category": category,
                                "name": name,
                                "description": description,
                                "file_path": str(output_path),
                                "filename": filename
                            }

            # If we got here, no image was generated
            print(f"[ERROR] No image data in response for {name}")
            return None

        except Exception as e:
            print(f"[ERROR] Failed to generate {name}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    async def generate_pose_library(self, test_mode: bool = False) -> str:
        """
        Generate character poses library and create metadata catalog

        Args:
            test_mode: If True, only generate first 5 poses for testing

        Returns:
            Path to metadata JSON file
        """
        num_poses = 5 if test_mode else 50
        mode_text = "TEST MODE (5 poses)" if test_mode else "FULL MODE (50 poses)"

        print("\n" + "="*60)
        print(f"CHARACTER POSE LIBRARY GENERATION - {mode_text}")
        print("="*60)
        print(f"\nGenerating {num_poses} character poses...")
        print(f"Output directory: {self.output_dir}")
        print(f"Reference image: {self.reference_image_path if self.reference_image_path else 'None'}")
        print(f"Skip existing: YES\n")

        metadata_list = []
        skipped_count = 0
        generated_count = 0
        failed_count = 0

        # Generate poses (all 50 or just first 5 for test)
        poses_to_generate = self.pose_templates[:num_poses]

        for i, pose_template in enumerate(poses_to_generate, start=1):
            pose_metadata = await self.generate_single_pose(pose_template, i, skip_if_exists=True)

            if pose_metadata:
                metadata_list.append(pose_metadata)
                if self._pose_already_exists(i, pose_template["category"], pose_template["name"]):
                    skipped_count += 1
                else:
                    generated_count += 1
            else:
                failed_count += 1

            # Small delay to avoid rate limiting
            await asyncio.sleep(2)

        # Save metadata catalog
        catalog_filename = "pose_catalog_test.json" if test_mode else "pose_catalog.json"
        catalog_path = self.output_dir / catalog_filename

        catalog_data = {
            "test_mode": test_mode,
            "total_poses": len(metadata_list),
            "categories": {
                "presenting": 10,
                "talking": 10,
                "reacting": 10,
                "emphasizing": 10,
                "neutral": 10
            },
            "poses": metadata_list,
            "generated_at": str(asyncio.get_event_loop().time()),
            "reference_image": str(self.reference_image_path) if self.reference_image_path else None
        }

        with open(catalog_path, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, indent=2, ensure_ascii=False)

        print(f"\n" + "="*60)
        print(f"[OK] POSE LIBRARY COMPLETE!")
        print(f"="*60)
        print(f"Mode: {mode_text}")
        print(f"Total poses: {len(metadata_list)}/{num_poses}")
        print(f"Generated new: {generated_count}")
        print(f"Skipped existing: {skipped_count}")
        print(f"Failed: {failed_count}")
        print(f"Catalog saved: {catalog_path}")
        print(f"Pose directory: {self.output_dir}")

        if test_mode:
            print(f"\n[TEST] Review the first 5 poses before generating all 50")
            print(f"[TEST] Run with test_mode=False to generate remaining poses")

        return str(catalog_path)


async def main():
    """Generate the complete pose library"""
    generator = CharacterPoseGenerator()
    catalog_path = await generator.generate_pose_library()
    print(f"\n[DONE] Pose catalog: {catalog_path}")


if __name__ == "__main__":
    asyncio.run(main())
