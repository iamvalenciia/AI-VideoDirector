<!--
Only me and God know how this works...
This creates videos for my YouTube channel
-->

# XInsight Finance - Automated YouTube videos Pipeline

![Channel Logo](https://yt3.googleusercontent.com/XqPYehZWVS2VjDx-30WSUhadtFAMdu49tfVNRJrvbhljOS32Ti7ij2mBDV7nvnSzU_tzdrgZEQ=s160-c-k-c0x00ffffff-no-rj)

AI-powered system for creating YouTube videos from viral financial tweets.

**Production Stats:**
- A 1-minute video takes approximately 4 minutes to assemble
- Fully automated from tweet selection to final video output

## YouTube Channel

**XInsight Finance** - Financial insights in short format

[![Subscribe](https://img.shields.io/badge/Subscribe-YouTube-red?style=for-the-badge&logo=youtube)](https://www.youtube.com/@XInsightFinance)

## Project Structure

```
youtube_channel-crewai/
├── main.py                          # Entry point
├── .env                             # API keys
├── output/financial_shorts/         # Generated assets
│
└── src/
    ├── pipeline_steps/
    │   ├── data_collection/         # Steps 1-2: Fetch & select tweets
    │   ├── content_generation/      # Steps 3-5: Analyze, audio, transcribe
    │   └── visual_production/       # Steps 6-10: Screenshots, visuals, video
    │
    ├── handlers/                    # CLI command handler
    ├── config/                      # Configuration
    ├── ui/                          # Console UI
    └── validators/                  # File validators
```

## Pipeline Commands

Execute commands using the BaseHandler:

### Available Commands

1. **create-production-plan**
   - Selects viral tweets and creates production plan
   - Generates script and visual specifications
   - Output: `production_plan.json`

2. **create-or-download-images**
   - Downloads images from tweet URLs
   - Generates AI images from prompts (DALL-E)
   - Output: Segment images in `video_images/`

3. **create-audio-and-timestamps**
   - Generates narration audio (ElevenLabs)
   - Creates word-level timestamps (Whisper)
   - Output: `narration.mp3`, `timestamps.json`

4. **create-tweet-image**
   - Creates screenshot of selected tweet
   - Output: `tweet_image.png`

5. **create-ticker-background-image**
   - Generates ticker background (930x50)
   - Output: `ticker_background.png`

6. **create-ticker-image**
   - Creates stock ticker with live data
   - Output: `ticker.png`

7. **create-segments-with-timestamps**
   - Synchronizes audio timestamps with video segments
   - Output: `segments_with_timestamps.json`

8. **create-final-video**
   - Assembles all assets into final video
   - Adds captions, ticker, transitions
   - Output: `final_video.mp4`

## Quick Start

### Setup
```bash
pip install -r requirements.txt

# Create .env with API keys
ANTHROPIC_API_KEY=your_key        # For Claude Sonnet 4.5
OPENAI_API_KEY=your_key           # For DALL-E image generation
ELEVENLABS_API_KEY=your_key       # For voice narration
```

### Run Pipeline

Execute commands through your handler implementation:

```python
from src.handlers.base_handler import BaseHandler

handler = BaseHandler()

# Run full pipeline
handler.execute("create-production-plan")
handler.execute("create-or-download-images")
handler.execute("create-audio-and-timestamps")
handler.execute("create-tweet-image")
handler.execute("create-ticker-background-image")
handler.execute("create-ticker-image")
handler.execute("create-segments-with-timestamps")
handler.execute("create-final-video")
```

## Data Pipeline Structure

```plaintext
data/
├── create_production_plan/
│   ├── input/viral_tweets.json
│   └── output/production_plan.json
├── video_images/
│   ├── download_images/          # Downloaded from URLs
│   └── generated_images/         # AI-generated images
├── video_audio/
│   └── elevenlabs/
│       ├── narration.mp3
│       └── timestamps.json
├── tweet_image/
│   └── tweet_image.png
├── video_ticker/
│   ├── ticker_background.png
│   └── ticker.png
├── final_segments/
│   └── segments_with_timestamps.json
└── final_video/
    └── final_video.mp4
```

## AI Models Used

| Service | Model | Purpose |
|---------|-------|---------|
| **Anthropic** | Claude Sonnet 4.5 | Production planning & script generation |
| **OpenAI** | DALL-E 3 | Image generation from prompts |
| **OpenAI** | Whisper | Audio transcription & timestamps |
| **ElevenLabs** | Multilingual v2 | Voice narration (Voice ID: yl2ZDV1MzN4HbQJbMihG) |
