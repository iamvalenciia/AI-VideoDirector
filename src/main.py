#!/usr/bin/env python
"""YouTube Shorts Production Pipeline - Main Entry Point"""

import sys
from config import PipelineConfig
from handlers import CommandHandler


def main():
    """Main entry point"""
    config = PipelineConfig()
    handler = CommandHandler(config)
    command = sys.argv[1] if len(sys.argv) > 1 else None
    handler.execute(command)


if __name__ == "__main__":
    main()
