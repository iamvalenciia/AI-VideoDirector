"""
Gemini Image Generation Tool
Generates progressive animation frames using Google Gen AI SDK (Imagen 3)
"""

import json
import os
import time
from pathlib import Path
from typing import Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class GeminiImageGenerator:
    """
    Handles image generation using Google Gen AI SDK with Imagen 3.
    Supports progressive generation where each image references the previous one.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash-image",
        output_dir: str = "output/frames",
    ):
        """
        Initialize the Gemini Image Generator.

        Args:
            api_key: Gemini API key (reads from env if not provided)
            model_name: Model to use for generation (default: gemini-2.5-flash)
            output_dir: Directory to save generated frames
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. Set it in .env or pass as parameter."
            )

        # Create client with new google-genai library
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

        # Setup output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        print(f"[SUCCESS] Gemini Image Generator initialized")
        print(f"   Model: {model_name}")
        print(f"   Output: {output_dir}")

    def generate_frame(
        self,
        prompt: str,
        reference_image_path: Optional[str] = None,
        output_filename: str = "frame.png",
        retry_attempts: int = 3,
    ) -> str:
        """
        Generate a single animation frame using Gemini 2.5 Flash with image generation.

        Args:
            prompt: Text prompt for image generation
            reference_image_path: Path to previous frame (for consistency)
            output_filename: Name for the output file
            retry_attempts: Number of retry attempts on failure

        Returns:
            Path to the generated image file

        Raises:
            RuntimeError: If generation fails after all retries
        """
        output_path = self.output_dir / output_filename

        for attempt in range(retry_attempts):
            try:
                print(f"\n[GENERATING] {output_filename}")
                print(f"   Prompt: {prompt[:100]}...")
                if reference_image_path:
                    print(f"   Reference: {reference_image_path}")

                # Build content list
                contents = []

                # If we have a reference image, load it and add to contents
                if reference_image_path and Path(reference_image_path).exists():
                    # Load reference image as bytes
                    with open(reference_image_path, 'rb') as img_file:
                        image_bytes = img_file.read()

                    # Create Part from bytes
                    image_part = types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/png'
                    )

                    # Enhanced prompt to maintain consistency
                    full_prompt = (
                        f"Generate an image using the EXACT same visual style, character design, "
                        f"art style, colors, lighting, and aesthetic as the reference image provided. "
                        f"Keep the character identical but modify the pose/action as follows: {prompt}"
                    )

                    # Add reference image first, then prompt
                    contents = [full_prompt, image_part]
                else:
                    # No reference image - just use the prompt
                    full_prompt = f"Generate a high-quality image: {prompt}"
                    contents = [full_prompt]

                # Generate content with image response
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
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.inline_data and part.inline_data.data:
                                # Save image bytes to file
                                with open(output_path, 'wb') as f:
                                    f.write(part.inline_data.data)
                                print(f"   [SAVED] {output_path}")
                                return str(output_path)

                # If we got here, no image was found
                print(f"   [WARNING] No image in response, attempt {attempt + 1}")
                if attempt == retry_attempts - 1:
                    raise RuntimeError("Failed to generate image after all retries")

            except Exception as e:
                print(f"   [ERROR] Attempt {attempt + 1}: {str(e)}")
                if attempt == retry_attempts - 1:
                    raise RuntimeError(
                        f"Failed to generate {output_filename} after {retry_attempts} attempts: {str(e)}"
                    )

                # Wait before retry
                time.sleep(2 ** attempt)  # Exponential backoff

        raise RuntimeError(f"Failed to generate {output_filename}")

    def generate_animation_sequence(
        self,
        prompts_file: str = "output/animation_prompts.json",
        base_image: str = "character_0001.png",
        start_frame: int = 1,
        end_frame: Optional[int] = None,
    ) -> dict:
        """
        Generate a complete animation sequence from prompts file.

        Args:
            prompts_file: Path to animation_prompts.json
            base_image: Path to the base character image
            start_frame: Frame number to start from (for resuming)
            end_frame: Frame number to end at (None = all frames)

        Returns:
            Dictionary with generation statistics and metadata
        """
        print("\n" + "=" * 60)
        print("STARTING ANIMATION SEQUENCE GENERATION")
        print("=" * 60)

        # Load prompts
        with open(prompts_file, "r", encoding="utf-8") as f:
            prompts_data = json.load(f)

        frames = prompts_data["frames"]
        total_frames = len(frames)

        if end_frame is None:
            end_frame = total_frames

        print(f"\n[CONFIGURATION]")
        print(f"   Total frames in file: {total_frames}")
        print(f"   Generating frames: {start_frame} to {end_frame}")
        print(f"   Base image: {base_image}")

        # Track generation
        stats = {
            "total_frames": total_frames,
            "frames_generated": 0,
            "frames_skipped": 0,
            "frames_failed": 0,
            "start_time": time.time(),
            "generated_files": [],
        }

        previous_frame_path = None

        # Generate each frame
        for i, frame_data in enumerate(frames, 1):
            # Skip if outside range
            if i < start_frame or i > end_frame:
                stats["frames_skipped"] += 1
                continue

            frame_id = frame_data["frame_id"]
            output_filename = frame_data["frame_filename"]
            prompt = frame_data["prompt"]

            # Check if frame already exists
            output_path = self.output_dir / output_filename
            if output_path.exists():
                print(f"\n[SKIP] Frame {frame_id} already exists, skipping...")
                stats["frames_skipped"] += 1
                previous_frame_path = str(output_path)
                continue

            # Use base image for first frame, previous frame for others
            if frame_id == 1:
                reference = base_image if Path(base_image).exists() else None
            else:
                reference = previous_frame_path

            try:
                # Generate the frame
                generated_path = self.generate_frame(
                    prompt=prompt,
                    reference_image_path=reference,
                    output_filename=output_filename,
                )

                stats["frames_generated"] += 1
                stats["generated_files"].append(generated_path)
                previous_frame_path = generated_path

                # Progress indicator
                progress = (i / total_frames) * 100
                print(f"\n[PROGRESS] {progress:.1f}% ({i}/{total_frames})")

                # Small delay to respect rate limits
                time.sleep(1)

            except Exception as e:
                print(f"\n[FAILED] Frame {frame_id}: {str(e)}")
                stats["frames_failed"] += 1
                # Continue with next frame even if this one fails

        # Calculate final statistics
        stats["end_time"] = time.time()
        stats["total_duration"] = stats["end_time"] - stats["start_time"]
        stats["average_time_per_frame"] = (
            stats["total_duration"] / stats["frames_generated"]
            if stats["frames_generated"] > 0
            else 0
        )

        # Save generation metadata
        metadata_path = self.output_dir.parent / "animation_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

        # Print final summary
        print("\n" + "=" * 60)
        print("ANIMATION GENERATION COMPLETE")
        print("=" * 60)
        print(f"[STATISTICS]")
        print(f"   Frames generated: {stats['frames_generated']}")
        print(f"   Frames skipped: {stats['frames_skipped']}")
        print(f"   Frames failed: {stats['frames_failed']}")
        print(f"   Total duration: {stats['total_duration']:.1f}s")
        print(
            f"   Avg time per frame: {stats['average_time_per_frame']:.1f}s"
        )
        print(f"\n[METADATA] Saved: {metadata_path}")
        print(f"[FRAMES] Directory: {self.output_dir}")
        print("=" * 60)

        return stats


# Standalone function for easy import
def calculate_generation_cost(prompts_file: str = "output/animation_prompts.json") -> dict:
    """
    Calculate the cost of generating all frames before execution.

    Gemini 2.5 Flash Image pricing:
    - Input: $0.30 per 1M tokens (text/image)
    - Output: $0.039 per image (1024x1024px = 1290 tokens)

    Args:
        prompts_file: Path to animation_prompts.json

    Returns:
        Dictionary with cost breakdown
    """
    import json
    from pathlib import Path

    if not Path(prompts_file).exists():
        raise FileNotFoundError(f"Prompts file not found: {prompts_file}")

    with open(prompts_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    total_frames = len(data["frames"])

    # Pricing constants
    OUTPUT_COST_PER_IMAGE = 0.039  # USD per image
    INPUT_COST_PER_1M_TOKENS = 0.30  # USD per 1M tokens

    # Estimate input tokens per frame (prompt text + reference image)
    # Average prompt: ~200 words = ~300 tokens
    # Reference image (1024x1024): ~1290 tokens
    TOKENS_PER_PROMPT = 300
    TOKENS_PER_REFERENCE = 1290

    # Calculate costs
    output_cost = total_frames * OUTPUT_COST_PER_IMAGE

    # First frame: base image + prompt
    # Subsequent frames: previous frame + prompt
    input_tokens = (TOKENS_PER_REFERENCE + TOKENS_PER_PROMPT) + \
                   ((total_frames - 1) * (TOKENS_PER_REFERENCE + TOKENS_PER_PROMPT))
    input_cost = (input_tokens / 1_000_000) * INPUT_COST_PER_1M_TOKENS

    total_cost = output_cost + input_cost

    cost_breakdown = {
        "total_frames": total_frames,
        "output_cost_usd": round(output_cost, 2),
        "input_cost_usd": round(input_cost, 2),
        "total_cost_usd": round(total_cost, 2),
        "cost_per_frame_usd": round(total_cost / total_frames, 4),
        "estimated_tokens": input_tokens,
        "pricing_info": {
            "output_per_image": OUTPUT_COST_PER_IMAGE,
            "input_per_1m_tokens": INPUT_COST_PER_1M_TOKENS
        }
    }

    return cost_breakdown


def generate_test_frames(
    prompts_file: str = "output/animation_prompts.json",
    base_image: str = "image/base_image.png",
    num_frames: int = 10,
    api_key: Optional[str] = None,
) -> dict:
    """
    Generate only the first N frames as a test before full generation.

    Args:
        prompts_file: Path to animation_prompts.json
        base_image: Path to base character image
        num_frames: Number of test frames to generate (default: 10)
        api_key: Gemini API key (optional, reads from env)

    Returns:
        Generation statistics dictionary
    """
    print("\n" + "=" * 60)
    print("TEST FRAME GENERATION")
    print("=" * 60)
    print(f"Generating first {num_frames} frames as test...")
    print("Review these before generating all frames!")
    print("=" * 60)

    generator = GeminiImageGenerator(api_key=api_key)
    return generator.generate_animation_sequence(
        prompts_file=prompts_file,
        base_image=base_image,
        start_frame=1,
        end_frame=num_frames
    )


def generate_animation_from_prompts(
    prompts_file: str = "output/animation_prompts.json",
    base_image: str = "image/base_image.png",
    api_key: Optional[str] = None,
    confirm_cost: bool = True,
) -> dict:
    """
    Generate animation from prompts file with cost calculation and confirmation.

    Args:
        prompts_file: Path to animation_prompts.json
        base_image: Path to base character image (defaults to image/base_image.png)
        api_key: Gemini API key (optional, reads from env)
        confirm_cost: If True, calculates cost and requires confirmation

    Returns:
        Generation statistics dictionary
    """
    # Calculate and display cost
    if confirm_cost:
        print("\n" + "=" * 60)
        print("COST ESTIMATION")
        print("=" * 60)

        cost_info = calculate_generation_cost(prompts_file)

        print(f"\n[FRAMES] Total frames to generate: {cost_info['total_frames']}")
        print(f"\n[COST BREAKDOWN]")
        print(f"  Output cost (images):  ${cost_info['output_cost_usd']:.2f}")
        print(f"  Input cost (prompts):  ${cost_info['input_cost_usd']:.2f}")
        print(f"  {'─' * 40}")
        print(f"  TOTAL ESTIMATED COST:  ${cost_info['total_cost_usd']:.2f}")
        print(f"  Cost per frame:        ${cost_info['cost_per_frame_usd']:.4f}")
        print(f"\n[TOKENS] Estimated: {cost_info['estimated_tokens']:,} tokens")
        print("\n" + "=" * 60)

        # Ask for confirmation
        response = input("\nProceed with generation? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("[CANCELLED] Frame generation cancelled by user")
            return {
                "total_frames": cost_info['total_frames'],
                "frames_generated": 0,
                "frames_skipped": 0,
                "frames_failed": 0,
                "cancelled": True
            }
        print("\n[CONFIRMED] Starting frame generation...")

    generator = GeminiImageGenerator(api_key=api_key)
    return generator.generate_animation_sequence(
        prompts_file=prompts_file,
        base_image=base_image,
    )


# Example usage
if __name__ == "__main__":
    # Test the generator
    try:
        stats = generate_animation_from_prompts()
        print(f"\n[SUCCESS] Generation complete! Generated {stats['frames_generated']} frames")
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")