# Utils - One-Time Generators

This directory contains tools that are run **once** to generate assets. These are separated from the main pipeline to keep the codebase clean and modular.

## 📁 Directory Structure

```
src/utils/
├── Short Format Generators (1080x1920)
│   ├── tweet_screenshot_generator.py
│   ├── stock_chart_generator.py
│   ├── image_prompt_generator.py
│   ├── illustration_generator.py
│   ├── studio_set_generator.py
│   └── character_pose_generator.py
│
├── Long Format Generators (1920x1080)
│   ├── horizontal_studio_generator.py (PIL-based, deprecated)
│   ├── horizontal_studio_html_generator.py (HTML/CSS-based, recommended)
│   ├── horizontal_ticker_background_generator.py
│   └── horizontal_ticker_generator.py
│
└── Utilities
    └── batch_remove_backgrounds.py
```

---

## 🎬 Short Format (Vertical - 1080x1920)

### tweet_screenshot_generator.py
Generates tweet screenshot images using Playwright.

**Usage:**
```python
from utils.tweet_screenshot_generator import TweetScreenshotGenerator

generator = TweetScreenshotGenerator()
await generator.generate_screenshot(tweet_data, filename="selected_tweet")
```

**Output:** `output/tweet_screenshots/selected_tweet.png`

---

### stock_chart_generator.py
Generates B&W stock price charts using yfinance and matplotlib.

**Usage:**
```python
from utils.stock_chart_generator import StockChartGenerator

generator = StockChartGenerator()
charts = generator.generate_charts_from_stocks(stocks, period="1y")
```

**Output:** `output/stock_charts/{symbol}_chart.png`

---

### image_prompt_generator.py
Generates image prompts from script using GPT-4o.

**Usage:**
```python
from utils.image_prompt_generator import ImagePromptGenerator

generator = ImagePromptGenerator()
prompts_path = generator.generate_and_save(
    financial_analysis_path="output/financial_shorts/financial_analysis.json",
    target_image_count=12
)
```

**Output:** `output/financial_shorts/image_prompts.json`

---

### illustration_generator.py
Generates B&W illustrations using Gemini 2.0 Flash.

**Usage:**
```python
from utils.illustration_generator import IllustrationGenerator

generator = IllustrationGenerator()
manifest = await generator.generate_from_prompts_file(
    prompts_file_path="output/financial_shorts/image_prompts.json"
)
```

**Output:** `output/illustrations/illustrations_manifest.json`

---

### studio_set_generator.py
Generates vertical studio background using HTML/CSS + Playwright.

**Usage:**
```python
from utils.studio_set_generator import StudioSetGenerator

generator = StudioSetGenerator()
bg_path = await generator.generate_studio_background(
    branding_text="XINSIDER"
)
```

**Output:** `output/financial_shorts/studio_background.png`

---

### character_pose_generator.py
Generates AI character poses using Gemini 2.0 Flash.

**Usage:**
```python
from utils.character_pose_generator import CharacterPoseGenerator

generator = CharacterPoseGenerator()

# Test mode (5 poses)
catalog = await generator.generate_pose_library(test_mode=True)

# Full mode (50 poses)
catalog = await generator.generate_pose_library(test_mode=False)
```

**Output:** `output/character_poses/pose_catalog.json`

---

## 🖥️ Long Format (Horizontal - 1920x1080)

### horizontal_studio_html_generator.py ⭐ **RECOMMENDED**
Generates horizontal news studio scene using HTML/CSS + Playwright.

**Features:**
- Tweet/image on left screen
- Character behind desk on right
- Ticker at bottom
- Professional Bloomberg-style design

**Usage:**
```python
from utils.horizontal_studio_html_generator import HorizontalStudioHTMLGenerator

generator = HorizontalStudioHTMLGenerator()
scene_path = await generator.generate_studio_scene(
    tweet_image_path="output/tweet_screenshots/selected_tweet.png",
    character_image_path="src/image/base_image.png",
    ticker_text="BREAKING: Market Analysis • TSLA ↑2.3%",
    branding_text="XINSIDER"
)
```

**Output:** `output/horizontal_videos/horizontal_studio_scene.png`

---

### horizontal_ticker_background_generator.py
Generates static black ticker background with XInsight branding.

**Features:**
- Black background (37px height x 1920px width)
- "XInsight" logo (X in green #5eea45, rest white)
- Bloomberg-style design

**Usage:**
```python
from utils.horizontal_ticker_background_generator import HorizontalTickerBackgroundGenerator

generator = HorizontalTickerBackgroundGenerator()
bg_path = await generator.generate_ticker_background()
```

**Output:** `output/horizontal_videos/horizontal_ticker_background.png`

---

### horizontal_ticker_generator.py
Generates animated stock ticker strip for long-format videos.

**Features:**
- White ticker bar with black text
- Red for negative changes, green for positive
- Seamless loop (repeats 3x)
- 37px height, variable width

**Usage:**
```python
from utils.horizontal_ticker_generator import HorizontalTickerGenerator

generator = HorizontalTickerGenerator()

# From analysis file
ticker_path = generator.create_ticker_from_analysis(
    analysis_path="output/financial_shorts/financial_analysis.json"
)

# Or manual stocks
stocks = [
    {"symbol": "TSLA", "price": 429.52, "change": -16.43, "change_percent": "-3.68"},
    {"symbol": "AAPL", "price": 178.90, "change": 2.14, "change_percent": "+1.18"}
]
ticker_path = generator.create_ticker_strip(stocks)
```

**Output:** `output/horizontal_videos/horizontal_ticker_strip.png`

---

## 🛠️ Utilities

### batch_remove_backgrounds.py
Batch removes backgrounds from all character poses and updates catalog.

**Features:**
- Processes all poses from `pose_catalog.json`
- Uses `rembg` for background removal
- Saves to `output/character_poses/nobg/`
- Updates catalog with new paths automatically

**Usage:**
```bash
python src/utils/batch_remove_backgrounds.py
```

**Output:**
- Images: `output/character_poses/nobg/*.png`
- Updated catalog: `output/character_poses/pose_catalog.json`
- Backup: `output/character_poses/pose_catalog_nobg.json`

---

## 📝 Notes

### Why are these in utils/?
- **Run once:** These tools generate assets that are reused across videos
- **Separation of concerns:** Keep pipeline code clean and focused
- **Easy to find:** All one-time generators in one place
- **No pipeline coupling:** Can be run independently

### Short vs Long Format
- **Short (1080x1920):** Vertical videos for TikTok, Instagram Reels, YouTube Shorts
- **Long (1920x1080):** Horizontal videos for YouTube, traditional social media

### When to run these?
1. **Once per project:** `character_pose_generator`, `batch_remove_backgrounds`
2. **Once per video:** All other generators (tweet, charts, illustrations, studio, ticker)

---

## 🚀 Quick Start

### Generate all assets for a short video:
```bash
# 1. Screenshots and charts
python -c "from utils.tweet_screenshot_generator import TweetScreenshotGenerator; import asyncio; asyncio.run(TweetScreenshotGenerator().generate_screenshot(tweet_data))"
python -c "from utils.stock_chart_generator import StockChartGenerator; StockChartGenerator().generate_charts_from_stocks(stocks)"

# 2. Image generation
python -c "from utils.image_prompt_generator import ImagePromptGenerator; ImagePromptGenerator().generate_and_save(analysis_path)"
python -c "from utils.illustration_generator import IllustrationGenerator; import asyncio; asyncio.run(IllustrationGenerator().generate_from_prompts_file(prompts_path))"

# 3. Studio and poses (first time only)
python -c "from utils.studio_set_generator import StudioSetGenerator; import asyncio; asyncio.run(StudioSetGenerator().generate_studio_background())"
python -c "from utils.character_pose_generator import CharacterPoseGenerator; import asyncio; asyncio.run(CharacterPoseGenerator().generate_pose_library())"
python src/utils/batch_remove_backgrounds.py
```

### Generate all assets for a long video:
```bash
# 1. Generate horizontal studio scene
python -c "from utils.horizontal_studio_html_generator import HorizontalStudioHTMLGenerator; import asyncio; asyncio.run(HorizontalStudioHTMLGenerator().generate_studio_scene(tweet_path, character_path, ticker_text))"

# 2. Generate ticker components
python -c "from utils.horizontal_ticker_background_generator import HorizontalTickerBackgroundGenerator; import asyncio; asyncio.run(HorizontalTickerBackgroundGenerator().generate_ticker_background())"
python -c "from utils.horizontal_ticker_generator import HorizontalTickerGenerator; HorizontalTickerGenerator().create_ticker_from_analysis(analysis_path)"
```

---

## ⚠️ Important

- **Don't import from pipeline_steps:** These are standalone utilities
- **Background removal:** Run `batch_remove_backgrounds.py` after generating poses
- **HTML generators:** Require Playwright to be installed (`playwright install chromium`)
- **Image generators:** Require valid API keys (Gemini, OpenAI)
