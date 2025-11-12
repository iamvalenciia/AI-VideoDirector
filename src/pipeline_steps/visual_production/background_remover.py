"""
Background Remover Tool
Removes white background from character images
Makes character transparent for compositing onto news studio set
"""

import os
from typing import Optional, List, Dict
from PIL import Image
import numpy as np


class BackgroundRemover:
    """
    Removes white backgrounds from character images
    Creates PNG with transparency for compositing
    """

    def __init__(self, tolerance: int = 30):
        """
        Initialize background remover

        Args:
            tolerance: Color tolerance for white detection (0-255)
        """
        self.tolerance = tolerance

    def remove_white_background(self,
                                input_path: str,
                                output_path: str,
                                tolerance: Optional[int] = None) -> str:
        """
        Remove white background from image

        Args:
            input_path: Path to input image
            output_path: Path to save output image with transparency
            tolerance: Optional custom tolerance (overrides default)

        Returns:
            Path to output image
        """
        try:
            print(f"🎭 Removing background from {os.path.basename(input_path)}...")

            # Load image
            img = Image.open(input_path).convert("RGBA")

            # Convert to numpy array
            data = np.array(img)

            # Get RGB channels
            r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]

            # Use custom tolerance if provided
            tol = tolerance if tolerance is not None else self.tolerance

            # Define white color range (accounting for tolerance)
            white_min = 255 - tol
            white_max = 255

            # Create mask for white pixels
            # A pixel is white if R, G, and B are all close to 255
            white_mask = (
                (r >= white_min) & (r <= white_max) &
                (g >= white_min) & (g <= white_max) &
                (b >= white_min) & (b <= white_max)
            )

            # Set alpha channel to 0 for white pixels (transparent)
            data[white_mask, 3] = 0

            # Create output image
            result = Image.fromarray(data, mode="RGBA")

            # Create output directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Save
            result.save(output_path, "PNG")

            print(f"✅ Background removed: {output_path}")
            return output_path

        except Exception as e:
            print(f"❌ Failed to remove background: {str(e)}")
            return None

    def remove_background_batch(self,
                                input_dir: str,
                                output_dir: str,
                                file_pattern: str = "character_*.png") -> List[str]:
        """
        Remove backgrounds from multiple images

        Args:
            input_dir: Directory with input images
            output_dir: Directory for output images
            file_pattern: Glob pattern for files to process

        Returns:
            List of paths to processed images
        """
        import glob

        # Find all matching files
        pattern_path = os.path.join(input_dir, file_pattern)
        input_files = glob.glob(pattern_path)

        print(f"🎭 Processing {len(input_files)} images...")

        output_paths = []
        for input_path in input_files:
            filename = os.path.basename(input_path)
            output_path = os.path.join(output_dir, filename)

            result_path = self.remove_white_background(input_path, output_path)
            if result_path:
                output_paths.append(result_path)

        print(f"✅ Processed {len(output_paths)} images")
        return output_paths

    def check_transparency(self, image_path: str) -> Dict:
        """
        Check transparency statistics of an image

        Args:
            image_path: Path to image

        Returns:
            Dictionary with transparency stats
        """
        img = Image.open(image_path).convert("RGBA")
        data = np.array(img)

        # Get alpha channel
        alpha = data[:,:,3]

        # Calculate stats
        total_pixels = alpha.size
        transparent_pixels = np.sum(alpha == 0)
        semi_transparent_pixels = np.sum((alpha > 0) & (alpha < 255))
        opaque_pixels = np.sum(alpha == 255)

        return {
            "total_pixels": int(total_pixels),
            "transparent_pixels": int(transparent_pixels),
            "semi_transparent_pixels": int(semi_transparent_pixels),
            "opaque_pixels": int(opaque_pixels),
            "transparency_percentage": float(transparent_pixels / total_pixels * 100)
        }


def main():
    """Example usage"""
    remover = BackgroundRemover(tolerance=30)

    # Example: Remove background from a character image
    input_path = "output/studio_assets/character_explaining.png"
    output_path = "output/studio_assets/character_explaining_nobg.png"

    if os.path.exists(input_path):
        result = remover.remove_white_background(input_path, output_path)

        if result:
            # Check transparency stats
            stats = remover.check_transparency(result)
            print("\n" + "="*50)
            print("TRANSPARENCY STATS:")
            print("="*50)
            print(f"Total pixels: {stats['total_pixels']:,}")
            print(f"Transparent: {stats['transparent_pixels']:,} ({stats['transparency_percentage']:.1f}%)")
            print(f"Opaque: {stats['opaque_pixels']:,}")
    else:
        print(f"❌ Input file not found: {input_path}")
        print("Run gemini_studio_generator.py first to generate character images")


if __name__ == "__main__":
    main()
