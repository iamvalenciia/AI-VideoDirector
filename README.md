# XInsider - Financial Shorts Production Pipeline

AI-powered system for creating YouTube Shorts from viral financial tweets.

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

## Pipeline Steps

### DATA COLLECTION
1. **fetch-tweets** - Fetch viral financial tweets (Grok AI)
2. **select-tweet** - AI-powered selection (GPT-4o)

### CONTENT GENERATION
3. **analyze** - Financial analysis + script (Claude Sonnet 4.5)
4. **generate-audio** - Audio narration (ElevenLabs)
5. **transcribe** - Word-level timestamps (Whisper)

### VISUAL PRODUCTION
6. **generate-screenshot** - Tweet screenshot
7. **extract-stock-data** - Stock ticker data
8. **create-ticker** - Stock ticker overlay
9. **generate-assets** - Visual assets (Gemini) [Coming Soon]
10. **assemble-video** - Final video (MoviePy) [Coming Soon]

## Quick Start

### Setup
```bash
pip install -r requirements.txt

# Create .env with API keys
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
ELEVEN_LABS_API_KEY=your_key
GROK_API_KEY=your_key
```

### Run
```bash
# Full pipeline
python main.py

# Individual steps
python main.py --step=fetch-tweets
python main.py --step=select-tweet
python main.py --step=analyze
python main.py --step=generate-audio
python main.py --step=transcribe
python main.py --step=generate-screenshot
python main.py --step=extract-stock-data
python main.py --step=create-ticker

# Help
python main.py --help
```

## Output Files

- `viral_tweets_normalized.json` - Fetched tweets
- `tweet_selection_report.json` - Selection reasoning
- `financial_analysis.json` - Analysis + script
- `narration.mp3` - Audio
- `timestamps.json` - Word timestamps
- `selected_tweet.png` - Screenshot
- `stock_data.json` - Stock data
- `ticker_overlay.png` - Ticker overlay

## AI Models

- **Claude Sonnet 4.5** - Financial analysis
- **GPT-4o** - Tweet selection
- **Whisper** - Transcription
- **ElevenLabs** - Text-to-speech
- **Gemini 2.0 Flash** - Visuals (coming soon)
