"""
Horizontal Ticker Generator for Long-Format Videos
Uses a pre-generated animated stock ticker strip.
"""

from pathlib import Path
import shutil
from typing import List, Dict
import json


class HorizontalTickerGenerator:
    """
    Copies a pre-generated stock ticker strip for horizontal videos.
    """

    def __init__(self, output_dir: str = "output/horizontal_videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_ticker_strip(
        self,
        stocks: List[Dict],
        output_filename: str = "horizontal_ticker_strip.png"
    ) -> str:
        """
        Copies the pre-generated scrolling ticker strip.
        The `stocks` parameter is no longer used for generation but is kept
        for compatibility with the existing pipeline.

        Args:
            stocks: List of stock dictionaries (no longer used).
            output_filename: Output filename.

        Returns:
            Path to the ticker strip.
        """
        print(f"\n[TICKER] Using pre-generated horizontal stock ticker...")

        # Path to the source ticker image
        source_ticker_path = Path("src/utils/output/horizontal_videos/test_horizontal_ticker.png")

        # Ensure the source file exists
        if not source_ticker_path.exists():
            raise FileNotFoundError(f"Source ticker image not found at: {source_ticker_path}")

        # Define the output path
        output_path = self.output_dir / output_filename

        # Copy the source image to the output path
        shutil.copy(source_ticker_path, output_path)

        print(f"[OK] Ticker strip copied from: {source_ticker_path}")
        print(f"     Saved to: {output_path}")

        return str(output_path)

    def create_ticker_from_analysis(
        self,
        analysis_path: str,
        output_filename: str = "horizontal_ticker_strip.png"
    ) -> str:
        """
        Provides the ticker strip. The analysis file is no longer used
        to generate it, but the parameter is kept for compatibility with
        the existing pipeline.

        Args:
            analysis_path: Path to financial_analysis.json (no longer used)
            output_filename: Output filename

        Returns:
            Path to generated ticker strip
        """
        print(f"\n[TICKER] Providing pre-generated ticker strip (analysis file no longer used for generation)...")
        # We pass an empty list for the `stocks` parameter as it's no longer used.
        return self.create_ticker_strip([], output_filename)


def main():
    """Example usage"""
    generator = HorizontalTickerGenerator()

    try:
        # This will copy the pre-generated ticker.
        # We pass an empty list for the `stocks` parameter as it's no longer used.
        ticker_path = generator.create_ticker_strip(
            stocks=[],
            output_filename="test_horizontal_ticker.png"
        )
        print(f"\n[SUCCESS] Ticker strip prepared: {ticker_path}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
