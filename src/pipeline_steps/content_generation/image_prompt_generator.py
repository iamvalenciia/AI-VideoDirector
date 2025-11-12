"""
IMAGE PROMPT GENERATOR - Content Generation Step

Uses OpenAI GPT-4 to analyze the video script and generate detailed image prompts
for illustrations throughout the short video. Each prompt is mapped to specific
sections of the narration.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from openai import OpenAI


class ImagePromptGenerator:
    """
    Generates image prompts for video illustrations based on script content.

    Uses GPT-4 to analyze the script and create 10-13 strategic image prompts
    that visualize key concepts and ideas throughout the narration.
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

    def generate_image_prompts(
        self,
        script_data: Dict,
        target_image_count: int = 12
    ) -> Dict:
        """
        Generate image prompts based on script content.

        Args:
            script_data: Script data from financial_analysis.json
            target_image_count: Target number of images (10-13)

        Returns:
            Dictionary with image prompts and timing information
        """
        print(f"\n[IMAGE PROMPTS] Analyzing script to generate {target_image_count} image prompts...")

        # Extract dialogue sections
        dialogue = script_data.get("dialogue", [])
        full_script = script_data.get("full_script", "")

        # Create prompt for GPT-4
        system_prompt = """You are an expert at creating image prompts for financial video content.
Your task is to analyze a video script and generate detailed image prompts for illustrations.

IMPORTANT REQUIREMENTS:
1. All images must be BLACK AND WHITE vector graphics with WHITE BACKGROUND
2. Images should be simple, clean, and iconic (like infographic illustrations)
3. Each image should visualize ONE KEY CONCEPT from that section
4. Generate 10-13 strategic image prompts distributed across the script
5. Map each image to specific narration text (start_text and end_text)

OUTPUT FORMAT (JSON):
{
  "images": [
    {
      "image_number": 1,
      "section": "hook",
      "concept": "Brief description of the concept being visualized",
      "prompt": "Detailed prompt for black and white vector graphic image with white background",
      "start_text": "First few words of narration when this image should appear",
      "end_text": "Last few words of narration when this image should end",
      "duration_seconds": estimated duration based on narration length
    }
  ]
}

PROMPT STYLE GUIDELINES:
- Always start with: "Black and white vector graphic illustration with white background showing..."
- Focus on: icons, symbols, charts, simple human figures, conceptual representations
- Avoid: photographs, complex scenes, realistic portraits, colors
- Examples of good concepts: dollar signs, stock charts, buildings, simplified people, geometric shapes, arrows, scales

Be strategic about which concepts need visualization. Not every sentence needs an image.
Focus on key moments: hook, important statistics, turning points, main arguments, conclusion."""

        user_prompt = f"""Analyze this financial video script and generate {target_image_count} strategic image prompts.

FULL SCRIPT:
{full_script}

SCRIPT SECTIONS WITH TIMING:
{json.dumps(dialogue, indent=2)}

Generate {target_image_count} black and white vector graphic image prompts that will help visualize this content."""

        # Call GPT-4
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=4000
            )

            # Parse response
            result = json.loads(response.choices[0].message.content)

            # Add metadata
            result["total_images"] = len(result.get("images", []))
            result["script_duration_seconds"] = script_data.get("total_duration_seconds", 70)
            result["generated_with"] = "gpt-4o"

            print(f"[OK] Generated {result['total_images']} image prompts")

            return result

        except Exception as e:
            print(f"[ERROR] Failed to generate image prompts: {str(e)}")
            raise

    def save_prompts(self, prompts_data: Dict, filename: str = "image_prompts.json") -> str:
        """Save image prompts to JSON file."""
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(prompts_data, f, indent=2, ensure_ascii=False)

        print(f"[OK] Prompts saved: {output_path}")
        return str(output_path)

    def generate_and_save(
        self,
        financial_analysis_path: str,
        target_image_count: int = 12
    ) -> str:
        """
        Complete workflow: load script, generate prompts, save results.

        Args:
            financial_analysis_path: Path to financial_analysis.json
            target_image_count: Target number of images (10-13)

        Returns:
            Path to saved prompts file
        """
        # Load financial analysis data
        with open(financial_analysis_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        script_data = data.get("script", {})

        # Generate prompts
        prompts_data = self.generate_image_prompts(script_data, target_image_count)

        # Save prompts
        output_path = self.save_prompts(prompts_data)

        # Print summary
        print(f"\n{'='*60}")
        print(f"IMAGE PROMPT GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"Total images: {prompts_data['total_images']}")
        print(f"Output file: {output_path}")

        # Print image concepts
        print(f"\nImage Concepts:")
        for img in prompts_data.get("images", []):
            section = img.get("section", "unknown")
            concept = img.get("concept", "")
            print(f"  {img['image_number']}. [{section}] {concept}")

        return output_path


# Test/demo code
if __name__ == "__main__":
    generator = ImagePromptGenerator()

    # Generate prompts from existing financial analysis
    prompts_path = generator.generate_and_save(
        financial_analysis_path="output/financial_shorts/financial_analysis.json",
        target_image_count=12
    )

    print(f"\n✅ Image prompts generated: {prompts_path}")
