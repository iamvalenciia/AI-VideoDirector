#!/usr/bin/env python
"""
XInsider - Financial Shorts Production Pipeline
Main entry point for the video production system
"""

import os
import sys

# Add src to path for imports
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

from handlers.financial_shorts_handler import FinancialShortsHandler


def main():
    """Main entry point"""
    # Get command from args
    command = sys.argv[1] if len(sys.argv) > 1 else None

    # Create handler and execute
    handler = FinancialShortsHandler()
    handler.execute(command)


if __name__ == "__main__":
    main()
