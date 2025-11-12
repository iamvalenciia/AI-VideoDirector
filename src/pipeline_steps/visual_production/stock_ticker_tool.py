"""
Stock Ticker Tool
Creates bottom ticker overlay for videos from stock data
Data comes from Claude AI financial analysis (related_stocks field)
"""

from .bottom_ticker_generator import BottomTickerGenerator


class StockTickerTool:
    """
    Wrapper for BottomTickerGenerator - creates professional ticker strips for video overlay
    """

    def __init__(self, output_dir: str = "output/financial_shorts"):
        """Initialize stock ticker tool"""
        self.generator = BottomTickerGenerator(output_dir=output_dir)

    def create_ticker_overlay_image(self, stocks: list, output_filename: str = "ticker_strip.png") -> str:
        """
        Create bottom ticker overlay image for video

        Args:
            stocks: List of stock dictionaries from financial_analysis.json (related_stocks field)
            output_filename: Output filename for ticker image

        Returns:
            Path to generated ticker overlay image
        """
        return self.generator.create_ticker_image(stocks, output_filename)


def main():
    """Example usage"""
    ticker_tool = StockTickerTool()

    # Example stock data from Claude analysis
    example_stocks = [
        {
            "symbol": "TSLA",
            "current_price": 242.50,
            "change_percent": 2.23
        },
        {
            "symbol": "BTC-USD",
            "current_price": 43250.00,
            "change_percent": -2.81
        },
        {
            "symbol": "SPY",
            "current_price": 455.80,
            "change_percent": -0.11
        },
        {
            "symbol": "NVDA",
            "current_price": 495.30,
            "change_percent": 2.57
        }
    ]

    # Create ticker overlay
    overlay_path = ticker_tool.create_ticker_overlay_image(example_stocks)
    print(f"\n[OK] Ticker overlay created: {overlay_path}")


if __name__ == "__main__":
    main()
