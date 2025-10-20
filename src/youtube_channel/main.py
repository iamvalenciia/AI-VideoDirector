#!/usr/bin/env python
import os


def run():
    """
    Run the crew.
    """
    # import here to avoid heavy side-effects during module import (litellm/crewai)
    from youtube_channel.crew import YoutubeChannelCrew

    # Create output directory when actually running
    os.makedirs("output", exist_ok=True)

    inputs = {"topic": "Crypto World"}

    result = YoutubeChannelCrew().crew().kickoff(inputs=inputs)

    print("\n\n=== CREW EXECUTION COMPLETE ===\n")
    print("Check the output folder for:")
    print("- shorts_ideas_report.txt")
    print("- script.txt")
    print("- creative_brief.txt")


if __name__ == "__main__":
    run()
