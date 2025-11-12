"""
Stock Chart Generator - Creates clean B&W stock charts for video overlays
Generates professional financial charts using yfinance data
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np


class StockChartGenerator:
    """
    Generates professional black & white stock charts for video production
    Same dimensions as tweet screenshots for consistent compositing
    """

    def __init__(self, output_dir: str = "output/stock_charts"):
        """
        Initialize the stock chart generator

        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Chart dimensions (match tweet screenshot dimensions)
        # Typical tweet screenshot is ~800x600 at high DPI
        self.width = 10  # inches
        self.height = 7.5  # inches
        self.dpi = 150  # High quality

    def _fetch_stock_data(self, symbol: str, period: str = "1mo") -> Optional[yf.Ticker]:
        """
        Fetch stock data from yfinance

        Args:
            symbol: Stock symbol (e.g., "TSLA")
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)

        Returns:
            yfinance Ticker object or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            # Verify data exists
            hist = ticker.history(period=period)
            if hist.empty:
                print(f"[WARNING] No data found for {symbol}")
                return None
            return ticker
        except Exception as e:
            print(f"[ERROR] Failed to fetch data for {symbol}: {str(e)}")
            return None

    def generate_stock_chart(
        self,
        symbol: str,
        current_price: float,
        change_percent: str,
        period: str = "1mo",
        output_filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate a clean black & white stock chart

        Args:
            symbol: Stock symbol (e.g., "TSLA")
            current_price: Current price of the stock
            change_percent: Change percentage (e.g., "-3.68")
            period: Time period for chart (default: 1mo)
            output_filename: Custom output filename (optional)

        Returns:
            Path to generated chart image
        """
        print(f"\n[CHART] Generating chart for {symbol}...")

        # Fetch stock data
        ticker = self._fetch_stock_data(symbol, period)
        if not ticker:
            return None

        # Get historical data
        hist = ticker.history(period=period)
        if hist.empty:
            print(f"[ERROR] No historical data for {symbol}")
            return None

        # Resample to monthly data (end of month prices)
        hist_monthly = hist['Close'].resample('ME').last().dropna()

        if hist_monthly.empty:
            print(f"[ERROR] No monthly data available for {symbol}")
            return None

        # Filter out future months (only keep up to current month)
        from datetime import datetime
        import pandas as pd

        # Get timezone from hist_monthly if available
        tz = hist_monthly.index.tz if hasattr(hist_monthly.index, 'tz') else None
        now = pd.Timestamp.now(tz=tz)
        hist_monthly = hist_monthly[hist_monthly.index <= now]

        # Add current price as the last data point (use provided current_price)
        current_date = pd.Timestamp.now(tz=tz)
        hist_monthly[current_date] = current_price

        # Create figure with white background
        fig, ax = plt.subplots(figsize=(self.width, self.height), facecolor='white')
        ax.set_facecolor('white')

        # Plot closing price - black line (monthly data)
        ax.plot(hist_monthly.index, hist_monthly.values, color='black', linewidth=2.5,
                solid_capstyle='round', marker='o', markersize=6)

        # Fill area under curve - light gray
        ax.fill_between(hist_monthly.index, hist_monthly.values, color='#E5E5E5', alpha=0.3)

        # Style the chart
        ax.set_xlabel('Date', fontsize=14, fontweight='bold', color='black')
        ax.set_ylabel('Price (USD)', fontsize=14, fontweight='bold', color='black')

        # Title with stock info
        change_sign = "+" if not change_percent.startswith("-") else ""
        title = f"{symbol} - ${current_price:.2f} ({change_sign}{change_percent}%)"
        ax.set_title(title, fontsize=20, fontweight='bold', color='black', pad=20)

        # Format date axis - show months only
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))  # Only month name
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Tick at start of each month
        plt.xticks(rotation=0, ha='center')  # No rotation for month labels

        # Grid - light gray, dotted
        ax.grid(True, linestyle=':', alpha=0.3, color='gray')

        # Spines - black
        for spine in ax.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(1.5)

        # Tick parameters - black
        ax.tick_params(colors='black', which='both', labelsize=12)

        # Add min annotation only (using monthly data, excluding current price point)
        # Get historical data without the current price we just added
        hist_monthly_historical = hist_monthly[:-1]  # All except the last (current) point

        min_price = hist_monthly_historical.min()
        min_date = hist_monthly_historical.idxmin()

        # Annotate min
        ax.annotate(
            f'${min_price:.2f}',
            xy=(min_date, min_price),
            xytext=(10, -20),
            textcoords='offset points',
            fontsize=11,
            fontweight='bold',
            color='black',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='black', linewidth=1.5),
            arrowprops=dict(arrowstyle='->', color='black', lw=1.5)
        )

        # Annotate current price at the end (most important!)
        ax.annotate(
            f'Current\n${current_price:.2f}',
            xy=(current_date, current_price),
            xytext=(15, 15),
            textcoords='offset points',
            fontsize=12,
            fontweight='bold',
            color='white',
            bbox=dict(boxstyle='round,pad=0.6', facecolor='black', edgecolor='black', linewidth=2),
            arrowprops=dict(arrowstyle='->', color='black', lw=2),
            ha='left'
        )

        # Tight layout
        plt.tight_layout()

        # Save
        if output_filename is None:
            output_filename = f"{symbol}_chart.png"

        output_path = self.output_dir / output_filename

        # Save as high-quality PNG
        plt.savefig(
            output_path,
            dpi=self.dpi,
            facecolor='white',
            edgecolor='none',
            bbox_inches='tight',
            format='png'
        )
        plt.close(fig)

        print(f"[OK] Chart saved: {output_path}")
        return str(output_path)

    def generate_charts_from_stocks(
        self,
        stocks: List[Dict],
        period: str = "1mo"
    ) -> List[str]:
        """
        Generate charts for multiple stocks dynamically

        Args:
            stocks: List of stock dictionaries from tweet_selection_report
                   Each dict should have: symbol, price, change, change_percent
            period: Time period for charts (default: 1mo)

        Returns:
            List of paths to generated chart images
        """
        if not stocks:
            print("[WARNING] No stocks provided")
            return []

        print(f"\n[CHART GENERATOR] Generating charts for {len(stocks)} stocks...")

        chart_paths = []
        for i, stock in enumerate(stocks, 1):
            symbol = stock.get("symbol")
            price = stock.get("price")
            change_percent = stock.get("change_percent")

            if not all([symbol, price, change_percent]):
                print(f"[WARNING] Skipping incomplete stock data: {stock}")
                continue

            print(f"[{i}/{len(stocks)}] Processing {symbol}...")

            # Generate chart
            chart_path = self.generate_stock_chart(
                symbol=symbol,
                current_price=price,
                change_percent=change_percent,
                period=period,
                output_filename=f"{symbol.lower()}_chart.png"
            )

            if chart_path:
                chart_paths.append(chart_path)

        print(f"\n[OK] Generated {len(chart_paths)} charts")
        return chart_paths


def main():
    """Example usage"""
    # Example stock data (from tweet_selection_report)
    example_stocks = [
        {
            "symbol": "TSLA",
            "price": 429.52,
            "change": -16.39,
            "change_percent": "-3.68"
        }
    ]

    generator = StockChartGenerator()
    chart_paths = generator.generate_charts_from_stocks(example_stocks, period="1mo")

    print(f"\n[DONE] Generated charts: {chart_paths}")


if __name__ == "__main__":
    main()
