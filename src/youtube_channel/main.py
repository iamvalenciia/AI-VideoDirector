#!/usr/bin/env python
import os
import sys


def run():
    """
    Execute the YouTube Shorts content creation crew.

    Usage:
        python main.py
    """
    from youtube_channel.crew import YoutubeChannelCrew
    from youtube_channel.tools.duckduckgo_tool import (
        get_search_count,
        reset_search_count,
    )

    os.makedirs("output", exist_ok=True)
    reset_search_count()

    inputs = {"topic": "Cryptocurrencies"}

    print("\n" + "=" * 60)
    print("CRYPTO CLARITY - YouTube Shorts Content Creator")
    print("=" * 60)
    print(f"Topic: {inputs['topic']}")
    print("Starting crew execution...\n")

    try:
        result = YoutubeChannelCrew().crew().kickoff(inputs=inputs)
        total_searches = get_search_count()

        print("\n" + "=" * 60)
        print("CREW EXECUTION COMPLETE!")
        print("=" * 60)
        print(f"Total web searches performed: {total_searches}")
        if total_searches > 3:
            print(f"WARNING: Expected 3 searches, but performed {total_searches}!")
        else:
            print("Search budget respected!")

        print("\nGenerated files in output/ folder:")
        print("  - news_collection.json  (10 relevant news articles)")
        print("  - video_script.json     (Complete script for ElevenLabs)")

        print("\nNext steps:")
        print("  1. Review news_collection.json")
        print("  2. Use video_script.json directly with ElevenLabs")
        print("  3. Script is optimized for viewer retention")
        print("\n" + "=" * 60 + "\n")

    except Exception as e:
        print("\n" + "=" * 60)
        print("ERROR DURING EXECUTION")
        print("=" * 60)
        print(f"\n{str(e)}\n")
        sys.exit(1)


if __name__ == "__main__":
    run()
