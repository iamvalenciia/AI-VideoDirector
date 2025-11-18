"""
Batch Background Remover for Character Poses
Removes backgrounds from all character poses and updates pose_catalog.json with new paths
Run this once after generating poses to optimize them for video composition
"""

import json
import os
from pathlib import Path
from PIL import Image
from rembg import remove
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class BatchBackgroundRemover:
    """
    Removes backgrounds from all poses and updates catalog
    """

    def __init__(
        self,
        poses_dir: str = "output/character_poses",
        catalog_file: str = "output/character_poses/pose_catalog.json"
    ):
        self.poses_dir = Path(poses_dir)
        self.catalog_file = Path(catalog_file)
        self.output_dir = self.poses_dir / "nobg"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def remove_background_from_pose(self, input_path: str) -> str:
        """
        Remove background from a single pose image

        Args:
            input_path: Path to input image

        Returns:
            Path to output image without background
        """
        input_path = Path(input_path)
        output_filename = f"{input_path.stem}_nobg.png"
        output_path = self.output_dir / output_filename

        # Skip if already processed
        if output_path.exists():
            print(f"[SKIP] {input_path.name} (already processed)")
            return str(output_path)

        print(f"[PROCESSING] {input_path.name}...", end=" ")

        try:
            # Load image
            input_img = Image.open(input_path).convert('RGBA')

            # Remove background
            output_img = remove(input_img)

            # Save
            output_img.save(output_path, 'PNG')

            print(f"[OK] Saved to {output_filename}")
            return str(output_path)
        except Exception as e:
            print(f"[ERROR] {e}")
            return None

    def process_all_poses(self) -> dict:
        """
        Process all poses from catalog and update paths

        Returns:
            Updated catalog dictionary
        """
        print("="*60)
        print("BATCH BACKGROUND REMOVAL")
        print("="*60)

        # Load catalog
        if not self.catalog_file.exists():
            raise FileNotFoundError(f"Catalog not found: {self.catalog_file}")

        with open(self.catalog_file, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        poses = catalog.get('poses', [])
        if not poses:
            raise ValueError("No poses found in catalog")

        print(f"\nFound {len(poses)} poses in catalog")
        print(f"Processing to: {self.output_dir}\n")

        # Process each pose
        processed_count = 0
        failed_count = 0
        skipped_count = 0

        for i, pose in enumerate(poses, 1):
            original_path = pose.get('file_path', '')
            if not original_path:
                print(f"[WARNING] Pose #{i} has no file_path")
                failed_count += 1
                continue

            # Check if already processed (path contains 'nobg')
            if 'nobg' in original_path:
                print(f"[SKIP] Pose #{i} already has nobg in path")
                skipped_count += 1
                continue

            # Remove background
            new_path = self.remove_background_from_pose(original_path)

            if new_path:
                # Update catalog entry
                pose['file_path'] = new_path
                pose['original_file_path'] = original_path  # Keep original reference
                pose['background_removed'] = True
                processed_count += 1
            else:
                failed_count += 1

        # Update catalog metadata
        catalog['metadata']['background_removed'] = True
        catalog['metadata']['nobg_directory'] = str(self.output_dir)

        # Save updated catalog
        updated_catalog_path = self.catalog_file.parent / "pose_catalog_nobg.json"
        with open(updated_catalog_path, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)

        # Also update original catalog
        with open(self.catalog_file, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"[OK] Processed:  {processed_count}")
        print(f"[SKIP] Skipped:  {skipped_count}")
        print(f"[ERROR] Failed:  {failed_count}")
        print(f"\nCatalog updated: {self.catalog_file}")
        print(f"Backup saved:    {updated_catalog_path}")
        print("="*60)

        return catalog

    def verify_nobg_images(self) -> bool:
        """
        Verify all nobg images exist and are valid

        Returns:
            True if all valid, False otherwise
        """
        print("\n[VERIFY] Checking all nobg images...")

        with open(self.catalog_file, 'r', encoding='utf-8') as f:
            catalog = json.load(f)

        poses = catalog.get('poses', [])
        missing_count = 0
        invalid_count = 0

        for pose in poses:
            file_path = pose.get('file_path', '')
            if not file_path:
                continue

            path = Path(file_path)
            if not path.exists():
                print(f"[ERROR] Missing: {file_path}")
                missing_count += 1
                continue

            # Check if valid image
            try:
                img = Image.open(path)
                img.verify()
            except Exception as e:
                print(f"[ERROR] Invalid: {file_path} - {e}")
                invalid_count += 1

        if missing_count == 0 and invalid_count == 0:
            print("[OK] All images verified successfully")
            return True
        else:
            print(f"[ERROR] Verification failed: {missing_count} missing, {invalid_count} invalid")
            return False


def main():
    """Example usage"""
    remover = BatchBackgroundRemover()

    try:
        # Process all poses
        updated_catalog = remover.process_all_poses()

        # Verify
        verification_passed = remover.verify_nobg_images()

        if verification_passed:
            print("\n[SUCCESS] All poses processed successfully!")
            print("You can now use the updated pose_catalog.json in your video pipeline")
        else:
            print("\n[WARNING] Some issues found during verification")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
