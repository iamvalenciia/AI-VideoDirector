"""
ILLUSTRATION GENERATOR - Visual Production Step

Uses Gemini 2.0 Flash Image to generate black & white vector-style illustrations
based on prompts created by the Image Prompt Generator.
"""

import json
import os
import base64
from pathlib import Path
from typing import Dict, List, Optional
from google import genai
from google.genai import types


class IllustrationGenerator:
    """
    Generates black & white vector-style illustrations for video content.

    Uses Gemini 2.0 Flash Image to create simple, clean illustrations
    that visualize key concepts from the video script.
    """

    def __init__(
        self,
        output_dir: str = "output/illustrations",
        model_name: str = "gemini-2.5-flash-image"
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def _enhance_prompt(self, base_prompt: str) -> str:
        """
        Enhance prompt to ensure black & white vector style with white background.

        Args:
            base_prompt: Base prompt from image_prompts.json

        Returns:
            Enhanced prompt with style specifications
        """
        # Ensure prompt specifies black and white vector style
        style_keywords = [
            "black and white",
            "vector graphic",
            "white background"
        ]

        # Check if prompt already has these keywords
        prompt_lower = base_prompt.lower()
        has_bw = any(kw in prompt_lower for kw in ["black and white", "monochrome", "b&w"])
        has_vector = any(kw in prompt_lower for kw in ["vector", "flat", "simple"])
        has_bg = any(kw in prompt_lower for kw in ["white background", "white bg"])

        # Build enhanced prompt
        enhancements = []
        if not has_bw:
            enhancements.append("black and white")
        if not has_vector:
            enhancements.append("vector graphic style")
        if not has_bg:
            enhancements.append("solid white background")

        if enhancements:
            enhanced = f"{base_prompt.rstrip('.')}. " + ", ".join(enhancements) + "."
        else:
            enhanced = base_prompt

        # Add quality and style specifications
        final_prompt = f"""{enhanced}

CRITICAL REQUIREMENTS:
- ONLY black and white colors (no grays, no colors)
- Pure white background (#FFFFFF)
- Vector graphic style (clean lines, simple shapes)
- High contrast for clarity
- Minimalist and iconic design
- NO photorealistic elements
- NO complex textures or gradients"""

        return final_prompt

    async def generate_single_illustration(
        self,
        prompt: str,
        image_number: int,
        concept: str,
        skip_if_exists: bool = True
    ) -> Optional[str]:
        """
        Generate a single illustration using Gemini.

        Args:
            prompt: Image generation prompt
            image_number: Number for filename
            concept: Brief concept description for filename
            skip_if_exists: Skip if file already exists

        Returns:
            Path to generated image or None if failed
        """
        # Create filename from concept
        safe_concept = "".join(c if c.isalnum() or c in (' ', '_') else '' for c in concept)
        safe_concept = safe_concept.replace(' ', '_').lower()[:50]
        filename = f"illustration_{image_number:02d}_{safe_concept}.png"
        output_path = self.output_dir / filename

        # Skip if exists
        if skip_if_exists and output_path.exists():
            print(f"[SKIP] Image {image_number} already exists: {filename}")
            return str(output_path)

        print(f"\n[{image_number}] Generating: {concept}")
        print(f"[PROMPT] {prompt[:100]}...")

        try:
            # Enhance prompt for B&W vector style
            enhanced_prompt = self._enhance_prompt(prompt)

            # Generate image with Gemini
            config = types.GenerateContentConfig(
                response_modalities=['Image'],
                temperature=0.4,  # Lower temperature for consistency
                safety_settings=[
                    types.SafetySetting(
                        category='HARM_CATEGORY_HATE_SPEECH',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_DANGEROUS_CONTENT',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_HARASSMENT',
                        threshold='BLOCK_NONE'
                    ),
                    types.SafetySetting(
                        category='HARM_CATEGORY_SEXUALLY_EXPLICIT',
                        threshold='BLOCK_NONE'
                    )
                ]
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=enhanced_prompt,
                config=config
            )

            # Extract image data
            if not response.candidates:
                print(f"[ERROR] No candidates in response for image {image_number}")
                return None

            candidate = response.candidates[0]

            # Find image part in response
            image_data = None
            for part in candidate.content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data
                    break

            if not image_data:
                print(f"[ERROR] No image data in response for image {image_number}")
                return None

            # Save image
            with open(output_path, 'wb') as f:
                f.write(image_data)

            print(f"[OK] Saved: {filename}")
            return str(output_path)

        except Exception as e:
            print(f"[ERROR] Failed to generate image {image_number}: {str(e)}")
            return None

    async def generate_all_illustrations(
        self,
        prompts_data: Dict,
        skip_if_exists: bool = True
    ) -> List[Dict]:
        """
        Generate all illustrations from prompts data.

        Args:
            prompts_data: Data from image_prompts.json
            skip_if_exists: Skip existing images

        Returns:
            List of results with paths
        """
        images = prompts_data.get("images", [])
        total = len(images)

        print(f"\n{'='*60}")
        print(f"GENERATING {total} ILLUSTRATIONS")
        print(f"{'='*60}")

        results = []

        for img in images:
            image_number = img.get("image_number", 0)
            prompt = img.get("prompt", "")
            concept = img.get("concept", "")

            if not prompt:
                print(f"[WARNING] No prompt for image {image_number}, skipping")
                continue

            # Generate image
            image_path = await self.generate_single_illustration(
                prompt=prompt,
                image_number=image_number,
                concept=concept,
                skip_if_exists=skip_if_exists
            )

            # Add result
            result = {
                **img,
                "image_path": image_path,
                "generated": image_path is not None
            }
            results.append(result)

        # Summary
        successful = sum(1 for r in results if r["generated"])
        print(f"\n{'='*60}")
        print(f"GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"Total: {total} images")
        print(f"Generated: {successful} images")
        print(f"Failed: {total - successful} images")

        return results

    def save_results(
        self,
        results: List[Dict],
        filename: str = "illustrations_manifest.json"
    ) -> str:
        """Save generation results to JSON file."""
        output_path = self.output_dir / filename

        manifest = {
            "total_images": len(results),
            "generated_count": sum(1 for r in results if r.get("generated")),
            "images": results
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Manifest saved: {output_path}")
        return str(output_path)

    async def generate_from_prompts_file(
        self,
        prompts_file_path: str,
        skip_if_exists: bool = True
    ) -> str:
        """
        Complete workflow: load prompts, generate images, save results.

        Args:
            prompts_file_path: Path to image_prompts.json
            skip_if_exists: Skip existing images

        Returns:
            Path to manifest file
        """
        # Load prompts
        with open(prompts_file_path, 'r', encoding='utf-8') as f:
            prompts_data = json.load(f)

        # Generate illustrations
        results = await self.generate_all_illustrations(prompts_data, skip_if_exists)

        # Save manifest
        manifest_path = self.save_results(results)

        return manifest_path


# Test/demo code
if __name__ == "__main__":
    import asyncio

    async def main():
        generator = IllustrationGenerator()

        # Generate illustrations from prompts file
        manifest_path = await generator.generate_from_prompts_file(
            prompts_file_path="output/financial_shorts/image_prompts.json",
            skip_if_exists=True
        )

        print(f"\n✅ Illustrations generated! Manifest: {manifest_path}")

    asyncio.run(main())
