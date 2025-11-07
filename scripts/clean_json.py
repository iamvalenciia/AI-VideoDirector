#!/usr/bin/env python
"""
Clean JSON files that may have markdown formatting.
Removes ```json and ``` markers from JSON files.
"""

import json
import sys
from pathlib import Path


def clean_json_file(filepath: str) -> bool:
    """
    Clean a JSON file by removing markdown code blocks.

    Args:
        filepath: Path to the JSON file to clean

    Returns:
        True if file was cleaned successfully, False otherwise
    """
    file_path = Path(filepath)

    if not file_path.exists():
        print(f"❌ File not found: {filepath}")
        return False

    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Remove markdown code blocks
    content = content.strip()

    # Remove starting ```json or ```
    if content.startswith('```json'):
        content = content[7:].lstrip()
        print("✓ Removed ```json from start")
    elif content.startswith('```'):
        content = content[3:].lstrip()
        print("✓ Removed ``` from start")

    # Remove ending ```
    if content.endswith('```'):
        content = content[:-3].rstrip()
        print("✓ Removed ``` from end")

    # Verify it's valid JSON
    try:
        json_data = json.loads(content)
        print("✓ JSON is valid")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON after cleaning: {e}")
        return False

    # Only write if content changed
    if content != original_content:
        # Create backup
        backup_path = file_path.with_suffix('.json.bak')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"✓ Backup created: {backup_path}")

        # Write cleaned content
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"✓ File cleaned: {filepath}")
        return True
    else:
        print("✓ File was already clean")
        return True


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python clean_json.py <path_to_json_file>")
        print("\nExample:")
        print("  python scripts/clean_json.py output/animation_prompts.json")
        sys.exit(1)

    filepath = sys.argv[1]

    print("\n" + "=" * 60)
    print("JSON CLEANER")
    print("=" * 60)
    print(f"File: {filepath}\n")

    success = clean_json_file(filepath)

    print("=" * 60)
    if success:
        print("✓ SUCCESS")
    else:
        print("❌ FAILED")
    print("=" * 60 + "\n")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
