# 🔧 TECHNICAL WORKFLOW DOCUMENTATION

**Análisis Técnico Completo a Nivel de Código**
Inputs, Outputs, Referencias entre Archivos, Funciones Específicas

---

## 📋 TABLE OF CONTENTS

1. [Entry Point & Handler](#entry-point--handler)
2. [Step-by-Step Code Analysis](#step-by-step-code-analysis)
3. [File Interdependencies Graph](#file-interdependencies-graph)
4. [JSON Schema Documentation](#json-schema-documentation)
5. [Function Call Chain](#function-call-chain)

---

## 🚀 ENTRY POINT & HANDLER

### Entry Point
**File:** `main.py`
```python
from handlers.financial_shorts_handler import FinancialShortsHandler

def main():
    command = sys.argv[1] if len(sys.argv) > 1 else None
    handler = FinancialShortsHandler()
    handler.execute(command)
```

### Handler Core
**File:** `src/handlers/financial_shorts_handler.py`

**Class:** `FinancialShortsHandler`
- **Purpose:** Orquestador principal de todos los pasos
- **Properties (Lazy Loading):**
  - `twitter_scraper` → `TwitterGrokScraper()`
  - `json_normalizer` → `JSONNormalizer()`
  - `tweet_selector` → `TweetSelector()`
  - `claude_analyst` → `ClaudeFinancialAnalyst()`
  - `screenshot_gen` → `TweetScreenshotGenerator()`
  - `stock_ticker` → `StockTickerTool()`
  - `studio_set_gen` → `StudioSetGenerator()`
  - `frame_compositor` → `FrameCompositor()`
  - `pose_generator` → `CharacterPoseGenerator()`
  - `stock_chart_gen` → `StockChartGenerator()`
  - `image_prompt_gen` → `ImagePromptGenerator()`
  - `illustration_gen` → `IllustrationGenerator()`
  - `production_planner` → `DeterministicProductionPlanner()`
  - `video_assembler` → `FinalVideoAssembler()`

**Command Mapping:**
```python
self.commands = {
    "--step=fetch-tweets": self._handle_fetch_tweets,
    "--step=select-tweet": self._handle_select_tweet,
    "--step=analyze": self._handle_analyze,
    "--step=generate-audio": self._handle_generate_audio,
    "--step=transcribe": self._handle_transcribe,
    "--step=generate-screenshot": self._handle_generate_screenshot,
    "--step=generate-stock-charts": self._handle_generate_stock_charts,
    "--step=generate-image-prompts": self._handle_generate_image_prompts,
    "--step=generate-illustrations": self._handle_generate_illustrations,
    "--step=create-ticker": self._handle_create_ticker,
    "--step=generate-studio": self._handle_generate_studio,
    "--step=compose-preview": self._handle_compose_preview,
    "--step=plan-production": self._handle_plan_production,
    "--step=assemble-video": self._handle_assemble_video,
    "--step=test-poses": self._handle_test_poses,
    "--step=generate-pose-library": self._handle_generate_pose_library,
    "--step=full-pipeline": self._handle_full_pipeline,
}
```

---

## 📊 STEP-BY-STEP CODE ANALYSIS

### STEP 1: FETCH TWEETS

**Command:** `--step=fetch-tweets`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
async def _handle_fetch_tweets(self):
    # Line 179-191
```

**Module Called:**
```python
# File: src/pipeline_steps/data_collection/twitter_grok_scraper.py
class TwitterGrokScraper:
    async def fetch_viral_tweets(self):
        # Llama a Twitter/X API usando credenciales de .env
```

**Environment Variables Used:**
- `TWITTER_USERNAME` (from `.env`)
- `TWITTER_PASSWORD` (from `.env`)

**Process Flow:**
1. **Line 181:** `raw_grok_response = await self.twitter_scraper.fetch_viral_tweets()`
   - Calls: `TwitterGrokScraper.fetch_viral_tweets()`
   - Returns: Raw JSON response from Grok AI

2. **Line 185:** `tweets_data = self.json_normalizer.normalize_grok_response(json.dumps(raw_grok_response))`
   - File: `src/pipeline_steps/data_collection/json_normalizer.py`
   - Class: `JSONNormalizer`
   - Method: `normalize_grok_response(grok_json: str) -> Dict`
   - Purpose: Convierte respuesta cruda de Grok a formato normalizado

3. **Line 186-188:** Save to JSON
   ```python
   output_path = self._get_output_path("viral_tweets_normalized.json")
   with open(output_path, 'w', encoding='utf-8') as f:
       json.dump(tweets_data, f, indent=2, ensure_ascii=False)
   ```

**Input:**
- None (uses Twitter API)

**Output:**
- **File:** `output/financial_shorts/viral_tweets_normalized.json`
- **Schema:**
```json
{
  "viral_tweets": [
    {
      "id": "1234567890",
      "text": "Tweet content...",
      "author": {
        "username": "@username",
        "display_name": "Display Name"
      },
      "metrics": {
        "likes": 1234,
        "retweets": 567,
        "replies": 89
      },
      "created_at": "2025-01-12T10:30:00Z"
    }
  ],
  "fetched_at": "2025-01-12T10:35:00Z",
  "total_count": 10
}
```

**Code References:**
- Reads: None
- Writes: `viral_tweets_normalized.json`
- Called by: `_handle_full_pipeline()` (line 450)
- Next step: `--step=select-tweet`

---

### STEP 2: SELECT TWEET

**Command:** `--step=select-tweet`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
async def _handle_select_tweet(self):
    # Line 193-205
```

**Module Called:**
```python
# File: src/pipeline_steps/data_collection/tweet_selector.py
class TweetSelector:
    def select_best_tweet(self, tweets_data: Dict) -> Dict:
        # Uses OpenAI GPT-4o to select best tweet
```

**Process Flow:**
1. **Line 195-199:** Load input file
   ```python
   tweets_path = self._get_output_path("viral_tweets_normalized.json")
   with open(tweets_path, 'r', encoding='utf-8') as f:
       tweets_data = json.load(f)
   ```
   - Reads: `output/financial_shorts/viral_tweets_normalized.json`

2. **Line 202:** `selection_result = self.tweet_selector.select_best_tweet(tweets_data)`
   - File: `src/pipeline_steps/data_collection/tweet_selector.py`
   - Method: `select_best_tweet(tweets_data: Dict) -> Dict`
   - API Call: OpenAI GPT-4o
   - Purpose: Analiza tweets y selecciona el mejor basado en engagement, relevancia, stocks mencionados

3. **Line 204-205:** Save result
   ```python
   report_path = self._get_output_path("tweet_selection_report.json")
   self.tweet_selector.save_selection_report(selection_result, report_path)
   ```

**Input:**
- **File:** `output/financial_shorts/viral_tweets_normalized.json`
- **Required Keys:** `viral_tweets[]`

**Output:**
- **File:** `output/financial_shorts/tweet_selection_report.json`
- **Schema:**
```json
{
  "selected_tweet": {
    "id": "1234567890",
    "text": "Tesla stock surges 15% after...",
    "author": {
      "username": "@elonmusk",
      "display_name": "Elon Musk"
    },
    "metrics": {
      "likes": 50000,
      "retweets": 12000,
      "replies": 3000
    },
    "related_stocks": [
      {
        "symbol": "TSLA",
        "current_price": 245.67,
        "change_percent": -2.34,
        "market_cap": 780000000000
      }
    ],
    "created_at": "2025-01-12T08:00:00Z"
  },
  "selection_reason": "High engagement, mentions major stock movement, timely news",
  "engagement_score": 95,
  "timestamp": "2025-01-12T10:40:00Z"
}
```

**Code References:**
- Reads: `viral_tweets_normalized.json`
- Writes: `tweet_selection_report.json`
- Called by: `_handle_full_pipeline()` (line 451)
- Next step: `--step=analyze`
- **IMPORTANT:** `related_stocks[]` es usado por múltiples pasos downstream

---

### STEP 3: ANALYZE (Financial Analysis & Script)

**Command:** `--step=analyze`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
async def _handle_analyze(self):
    # Line 207-223
```

**Module Called:**
```python
# File: src/pipeline_steps/content_generation/claude_financial_analyst.py
class ClaudeFinancialAnalyst:
    async def analyze_tweet_and_generate_script(self, selected_tweet: Dict) -> Dict:
        # Uses Anthropic Claude 3.5 Sonnet
```

**Process Flow:**
1. **Line 209-215:** Load tweet selection
   ```python
   report_path = self._get_output_path("tweet_selection_report.json")
   with open(report_path, 'r', encoding='utf-8') as f:
       selection_report = json.load(f)
       selected_tweet = selection_report['selected_tweet']
   ```
   - Reads: `output/financial_shorts/tweet_selection_report.json`
   - Extracts: `selected_tweet` object

2. **Line 218:** `analysis_data = await self.claude_analyst.analyze_tweet_and_generate_script(selected_tweet)`
   - File: `src/pipeline_steps/content_generation/claude_financial_analyst.py`
   - Method: `analyze_tweet_and_generate_script(selected_tweet: Dict) -> Dict`
   - API Call: Anthropic Claude 3.5 Sonnet
   - Purpose:
     - Analiza el contexto financiero del tweet
     - Genera script de narración (~90-120 segundos)
     - Extrae stocks relacionados
     - Identifica puntos clave para visuales

3. **Line 220-222:** Save analysis
   ```python
   output_path = self._get_output_path("financial_analysis.json")
   with open(output_path, 'w', encoding='utf-8') as f:
       json.dump(analysis_data, f, indent=2, ensure_ascii=False)
   ```

**Input:**
- **File:** `output/financial_shorts/tweet_selection_report.json`
- **Required Keys:** `selected_tweet{}`

**Output:**
- **File:** `output/financial_shorts/financial_analysis.json`
- **Schema:**
```json
{
  "title": "Tesla Stock Surge Analysis",
  "script": "Tesla's stock price just made headlines again...[full narration script]",
  "duration_estimate": 95.5,
  "key_points": [
    "Stock price increased 15%",
    "New factory announcement",
    "Analyst upgrades"
  ],
  "related_stocks": [
    {
      "symbol": "TSLA",
      "current_price": 245.67,
      "change_percent": -2.34,
      "relevance": "Primary subject"
    },
    {
      "symbol": "NVDA",
      "current_price": 512.89,
      "change_percent": 3.21,
      "relevance": "Supplier mention"
    }
  ],
  "visual_suggestions": [
    "Tesla factory aerial view",
    "Stock price chart",
    "CEO announcement"
  ],
  "tone": "Informative, professional",
  "target_audience": "Retail investors",
  "generated_at": "2025-01-12T10:45:00Z"
}
```

**Code References:**
- Reads: `tweet_selection_report.json`
- Writes: `financial_analysis.json`
- Called by: `_handle_full_pipeline()` (line 452)
- Used by:
  - `--step=generate-audio` (reads `script` field)
  - `--step=create-ticker` (reads `related_stocks[]`)
  - `--step=generate-image-prompts` (reads entire file)
  - `--step=plan-production` (reads for metadata)

---

### STEP 4: GENERATE AUDIO

**Command:** `--step=generate-audio`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
async def _handle_generate_audio(self):
    # Line 225-236
```

**Module Called:**
```python
# File: src/pipeline_steps/content_generation/elevenlabs_tool.py
def generate_audio_from_script(script_file: str, output_file: str):
    # Uses ElevenLabs API
```

**Process Flow:**
1. **Line 227-228:** Setup paths
   ```python
   analysis_path = self._get_output_path("financial_analysis.json")
   audio_output_path = self._get_output_path("narration.mp3")
   ```

2. **Line 230-233:** Generate audio
   ```python
   generate_audio_from_script(
       script_file=analysis_path,
       output_file=audio_output_path
   )
   ```
   - File: `src/pipeline_steps/content_generation/elevenlabs_tool.py`
   - Function: `generate_audio_from_script(script_file, output_file)`
   - Internal Process:
     ```python
     # Read script from JSON
     with open(script_file) as f:
         data = json.load(f)
         script_text = data['script']

     # Call ElevenLabs API
     audio_bytes = elevenlabs.generate(
         text=script_text,
         voice="Adam",  # Professional male voice
         model="eleven_monolingual_v1"
     )

     # Save to file
     with open(output_file, 'wb') as f:
         f.write(audio_bytes)
     ```

**Environment Variables Used:**
- `ELEVENLABS_API_KEY` (from `.env`)

**Input:**
- **File:** `output/financial_shorts/financial_analysis.json`
- **Required Keys:** `script` (string)

**Output:**
- **File:** `output/financial_shorts/narration.mp3`
- **Format:** MP3 audio
- **Duration:** ~90-120 seconds
- **Sample Rate:** 44.1kHz
- **Bitrate:** 128kbps
- **Channels:** Mono

**Code References:**
- Reads: `financial_analysis.json` (field: `script`)
- Writes: `narration.mp3`
- Called by: `_handle_full_pipeline()` (line 453)
- Next step: `--step=transcribe`

---

### STEP 5: TRANSCRIBE AUDIO

**Command:** `--step=transcribe`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
async def _handle_transcribe(self):
    # Line 238-248
```

**Module Called:**
```python
# File: src/pipeline_steps/content_generation/whisper_tool.py
def transcribe_audio(audio_path: str) -> Dict:
    # Uses OpenAI Whisper API
```

**Process Flow:**
1. **Line 240:** `audio_path = self._get_output_path("narration.mp3")`

2. **Line 242:** `timestamp_data = transcribe_audio(audio_path)`
   - File: `src/pipeline_steps/content_generation/whisper_tool.py`
   - Function: `transcribe_audio(audio_path: str) -> Dict`
   - API Call: OpenAI Whisper
   - Purpose: Generar timestamps a nivel de palabra (word-level timestamps)
   - Internal Process:
     ```python
     from openai import OpenAI

     client = OpenAI()

     with open(audio_path, 'rb') as audio_file:
         transcript = client.audio.transcriptions.create(
             model="whisper-1",
             file=audio_file,
             response_format="verbose_json",
             timestamp_granularities=["word"]
         )

     return {
         "words": transcript.words,
         "segments": transcript.segments,
         "text": transcript.text,
         "duration": transcript.duration
     }
     ```

3. **Line 243-245:** Save timestamps
   ```python
   output_path = self._get_output_path("timestamps.json")
   with open(output_path, 'w', encoding='utf-8') as f:
       json.dump(timestamp_data, f, indent=2, ensure_ascii=False)
   ```

**Environment Variables Used:**
- `OPENAI_API_KEY` (from `.env`)

**Input:**
- **File:** `output/financial_shorts/narration.mp3`

**Output:**
- **File:** `output/financial_shorts/timestamps.json`
- **Schema:**
```json
{
  "words": [
    {
      "word": "Tesla",
      "start": 0.0,
      "end": 0.42
    },
    {
      "word": "stock",
      "start": 0.48,
      "end": 0.84
    },
    {
      "word": "price",
      "start": 0.90,
      "end": 1.26
    }
  ],
  "segments": [
    {
      "id": 0,
      "start": 0.0,
      "end": 5.2,
      "text": "Tesla stock price surged 15% today following...",
      "tokens": [...]
    }
  ],
  "text": "Full transcript text...",
  "duration": 108.52
}
```

**Code References:**
- Reads: `narration.mp3`
- Writes: `timestamps.json`
- Called by: `_handle_full_pipeline()` (line 454)
- **CRITICAL:** Used by `--step=plan-production` para crear escenas y captions
- **CRITICAL:** Used by `--step=assemble-video` para word-by-word captions

---

### STEP 6A: GENERATE SCREENSHOT

**Command:** `--step=generate-screenshot`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
async def _handle_generate_screenshot(self):
    # Line 250-262
```

**Module Called:**
```python
# File: src/pipeline_steps/visual_production/tweet_screenshot_generator.py
class TweetScreenshotGenerator:
    async def generate_screenshot(self, tweet_data: Dict, filename: str) -> str:
        # Uses Playwright for browser automation
```

**Process Flow:**
1. **Line 252-258:** Load tweet data
   ```python
   report_path = self._get_output_path("tweet_selection_report.json")
   with open(report_path, 'r', encoding='utf-8') as f:
       selection_report = json.load(f)
       selected_tweet = selection_report['selected_tweet']
   ```

2. **Line 260:** `screenshot_path = await self.screenshot_gen.generate_screenshot(selected_tweet, filename="selected_tweet")`
   - File: `src/pipeline_steps/visual_production/tweet_screenshot_generator.py`
   - Method: `generate_screenshot(tweet_data, filename)`
   - Process:
     ```python
     from playwright.async_api import async_playwright

     async with async_playwright() as p:
         browser = await p.chromium.launch()
         page = await browser.new_page(viewport={'width': 600, 'height': 800})

         # Render tweet HTML
         html_content = self._generate_tweet_html(tweet_data)
         await page.set_content(html_content)

         # Take screenshot
         screenshot_path = f"output/tweet_screenshots/{filename}.png"
         await page.screenshot(path=screenshot_path)

         await browser.close()

     return screenshot_path
     ```

**Dependencies:**
- Playwright (browser automation)

**Input:**
- **File:** `output/financial_shorts/tweet_selection_report.json`
- **Required Keys:** `selected_tweet{text, author, metrics}`

**Output:**
- **File:** `output/tweet_screenshots/selected_tweet.png`
- **Format:** PNG image
- **Dimensions:** ~600x800px (variable based on content)
- **Contents:** Rendered tweet with author info, text, and engagement metrics

**Code References:**
- Reads: `tweet_selection_report.json`
- Writes: `output/tweet_screenshots/selected_tweet.png`
- Used by: `--step=assemble-video` (tweets layer)

---

### STEP 6B: GENERATE STOCK CHARTS

**Command:** `--step=generate-stock-charts`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
async def _handle_generate_stock_charts(self):
    # Line 264-296
```

**Module Called:**
```python
# File: src/pipeline_steps/visual_production/stock_chart_generator.py
class StockChartGenerator:
    def generate_charts_from_stocks(self, stocks: List[Dict], period: str) -> List[str]:
        # Uses yfinance + matplotlib
```

**Process Flow:**
1. **Line 266-271:** Load stock data
   ```python
   report_path = self._get_output_path("tweet_selection_report.json")
   with open(report_path, 'r', encoding='utf-8') as f:
       selection_report = json.load(f)

   selected_tweet = selection_report.get('selected_tweet', {})
   related_stocks = selected_tweet.get('related_stocks', [])
   ```
   - **IMPORTANT:** Stocks come from `selected_tweet.related_stocks[]`

2. **Line 286-289:** Generate charts
   ```python
   chart_paths = self.stock_chart_gen.generate_charts_from_stocks(
       stocks=related_stocks,
       period="1y"  # 1 year period for monthly data
   )
   ```
   - File: `src/pipeline_steps/visual_production/stock_chart_generator.py`
   - Method: `generate_charts_from_stocks(stocks, period)`
   - Process for each stock:
     ```python
     import yfinance as yf
     import matplotlib.pyplot as plt

     for stock in stocks:
         symbol = stock['symbol']

         # Fetch data from Yahoo Finance
         ticker = yf.Ticker(symbol)
         hist = ticker.history(period=period)

         # Create B&W chart
         fig, ax = plt.subplots(figsize=(10, 6))
         ax.plot(hist.index, hist['Close'], color='black', linewidth=2)
         ax.fill_between(hist.index, hist['Close'], alpha=0.3, color='gray')

         # Styling (black & white, newspaper style)
         ax.set_facecolor('white')
         ax.grid(True, color='gray', linestyle='--', alpha=0.3)

         # Save
         output_path = f"output/stock_charts/{symbol.lower()}_chart.png"
         plt.savefig(output_path, dpi=150, bbox_inches='tight')
         plt.close()

         chart_paths.append(output_path)

     return chart_paths
     ```

**Dependencies:**
- `yfinance` (Yahoo Finance API)
- `matplotlib` (chart rendering)

**Input:**
- **File:** `output/financial_shorts/tweet_selection_report.json`
- **Required Keys:** `selected_tweet.related_stocks[]{symbol}`

**Output:**
- **Files:** `output/stock_charts/{SYMBOL}_chart.png` (one per stock)
  - Example: `output/stock_charts/tsla_chart.png`
  - Example: `output/stock_charts/nvda_chart.png`
- **Format:** PNG image
- **Dimensions:** 1000x600px
- **Style:** Black & white, newspaper-style chart
- **Period:** 1 year of historical data

**Code References:**
- Reads: `tweet_selection_report.json` (field: `selected_tweet.related_stocks[]`)
- Writes: `output/stock_charts/{symbol}_chart.png` (múltiples archivos)
- Used by: `--step=assemble-video` (chart alternator layer)

---

### STEP 6C: GENERATE IMAGE PROMPTS

**Command:** `--step=generate-image-prompts`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
def _handle_generate_image_prompts(self):
    # Line 298-310
```

**Module Called:**
```python
# File: src/pipeline_steps/content_generation/image_prompt_generator.py
class ImagePromptGenerator:
    def generate_and_save(self, financial_analysis_path: str, target_image_count: int) -> str:
        # Uses OpenAI GPT-4o
```

**Process Flow:**
1. **Line 300:** `analysis_path = self._get_output_path("financial_analysis.json")`

2. **Line 304-307:** Generate prompts
   ```python
   prompts_path = self.image_prompt_gen.generate_and_save(
       financial_analysis_path=analysis_path,
       target_image_count=12
   )
   ```
   - File: `src/pipeline_steps/content_generation/image_prompt_generator.py`
   - Method: `generate_and_save(financial_analysis_path, target_image_count)`
   - API Call: OpenAI GPT-4o
   - Process:
     ```python
     from openai import OpenAI

     # Load analysis
     with open(financial_analysis_path) as f:
         analysis = json.load(f)

     client = OpenAI()

     # Generate prompts
     response = client.chat.completions.create(
         model="gpt-4o",
         messages=[{
             "role": "system",
             "content": "Generate 12 B&W newspaper-style illustration prompts..."
         }, {
             "role": "user",
             "content": f"Script: {analysis['script']}\nKey points: {analysis['key_points']}"
         }],
         response_format={"type": "json_object"}
     )

     prompts_data = json.loads(response.choices[0].message.content)

     # Save
     output_path = "output/financial_shorts/image_prompts.json"
     with open(output_path, 'w') as f:
         json.dump(prompts_data, f, indent=2)

     return output_path
     ```

**Environment Variables Used:**
- `OPENAI_API_KEY` (from `.env`)

**Input:**
- **File:** `output/financial_shorts/financial_analysis.json`
- **Required Keys:** `script`, `key_points`, `visual_suggestions`

**Output:**
- **File:** `output/financial_shorts/image_prompts.json`
- **Schema:**
```json
{
  "prompts": [
    {
      "id": 1,
      "prompt": "Black and white newspaper illustration of Tesla factory aerial view, industrial style, high contrast, editorial illustration",
      "scene_match": "Opening - factory announcement",
      "duration": "0-8s",
      "style": "B&W editorial illustration, newspaper style"
    },
    {
      "id": 2,
      "prompt": "Black and white illustration of upward trending stock chart with dramatic angle, financial newspaper style",
      "scene_match": "Stock price surge discussion",
      "duration": "8-15s",
      "style": "B&W editorial illustration, newspaper style"
    }
    // ... 10 more prompts
  ],
  "total_count": 12,
  "style_guide": "Black and white, newspaper editorial style, high contrast",
  "generated_at": "2025-01-12T11:00:00Z"
}
```

**Code References:**
- Reads: `financial_analysis.json`
- Writes: `image_prompts.json`
- Next step: `--step=generate-illustrations`

---

### STEP 6D: GENERATE ILLUSTRATIONS

**Command:** `--step=generate-illustrations`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
async def _handle_generate_illustrations(self):
    # Line 312-329
```

**Module Called:**
```python
# File: src/pipeline_steps/visual_production/illustration_generator.py
class IllustrationGenerator:
    async def generate_from_prompts_file(self, prompts_file_path: str, skip_if_exists: bool) -> str:
        # Uses Google Gemini 2.0 Flash
```

**Process Flow:**
1. **Line 314:** `prompts_path = self._get_output_path("image_prompts.json")`

2. **Line 323-326:** Generate illustrations
   ```python
   manifest_path = await self.illustration_gen.generate_from_prompts_file(
       prompts_file_path=prompts_path,
       skip_if_exists=True
   )
   ```
   - File: `src/pipeline_steps/visual_production/illustration_generator.py`
   - Method: `generate_from_prompts_file(prompts_file_path, skip_if_exists)`
   - API Call: Google Gemini 2.0 Flash (image generation)
   - Process:
     ```python
     import google.generativeai as genai

     # Load prompts
     with open(prompts_file_path) as f:
         data = json.load(f)
         prompts = data['prompts']

     # Configure Gemini
     genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
     model = genai.GenerativeModel('gemini-2.0-flash-exp')

     generated_images = []

     # SEQUENTIAL (Current implementation)
     for i, prompt_data in enumerate(prompts):
         output_path = f"output/illustrations/img_{i+1:03d}.png"

         if skip_if_exists and Path(output_path).exists():
             continue

         # Generate image
         response = model.generate_image(
             prompt=prompt_data['prompt'],
             aspect_ratio="16:9",
             style="photographic"
         )

         # Save
         with open(output_path, 'wb') as f:
             f.write(response.image_bytes)

         generated_images.append({
             "image_id": i+1,
             "image_path": output_path,
             "prompt": prompt_data['prompt'],
             "scene_match": prompt_data.get('scene_match', '')
         })

         # Rate limiting
         await asyncio.sleep(1)

     # Save manifest
     manifest = {
         "images": generated_images,
         "total_count": len(generated_images),
         "generated_at": datetime.now().isoformat()
     }

     manifest_path = "output/illustrations/illustrations_manifest.json"
     with open(manifest_path, 'w') as f:
         json.dump(manifest, f, indent=2)

     return manifest_path
     ```

**Environment Variables Used:**
- `GEMINI_API_KEY` (from `.env`)

**Input:**
- **File:** `output/financial_shorts/image_prompts.json`
- **Required Keys:** `prompts[]{prompt}`

**Output:**
- **Files:**
  - `output/illustrations/img_001.png` through `img_012.png` (12 images)
  - `output/illustrations/illustrations_manifest.json`

- **Manifest Schema:**
```json
{
  "images": [
    {
      "image_id": 1,
      "image_path": "output/illustrations/img_001.png",
      "file_path": "output/illustrations/img_001.png",
      "prompt": "Black and white newspaper illustration of...",
      "scene_match": "Opening - factory announcement",
      "generated_at": "2025-01-12T11:05:23Z"
    }
    // ... 11 more
  ],
  "total_count": 12,
  "generated_at": "2025-01-12T11:10:45Z"
}
```

**Image Specs:**
- Format: PNG
- Dimensions: 1024x576px (16:9 aspect ratio)
- Style: Black & white editorial illustrations
- Quality: High contrast, newspaper style

**Code References:**
- Reads: `image_prompts.json`
- Writes:
  - `output/illustrations/img_*.png` (12 files)
  - `illustrations_manifest.json`
- Used by:
  - `--step=plan-production` (reads manifest)
  - `--step=assemble-video` (loads actual images)

**OPTIMIZATION NOTE:**
- ⚠️ **CURRENT BOTTLENECK:** Sequential generation (60-90s)
- ✅ **OPTIMIZATION:** Parallel generation can reduce to 15-20s

---

### STEP 7: CREATE TICKER

**Command:** `--step=create-ticker`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
async def _handle_create_ticker(self):
    # Line 356-375
```

**Module Called:**
```python
# File: src/pipeline_steps/visual_production/stock_ticker_tool.py
class StockTickerTool:
    def create_ticker_overlay_image(self, stocks: List[Dict]) -> str:
        # Delegates to BottomTickerGenerator
```

**Process Flow:**
1. **Line 358-363:** Load stock data
   ```python
   analysis_path = self._get_output_path("financial_analysis.json")
   with open(analysis_path, 'r', encoding='utf-8') as f:
       analysis_data = json.load(f)

   related_stocks = analysis_data.get('related_stocks', [])
   ```
   - **IMPORTANT:** Stocks from `financial_analysis.json`, NOT `tweet_selection_report.json`

2. **Line 373:** `overlay_path = self.stock_ticker.create_ticker_overlay_image(related_stocks)`
   - File: `src/pipeline_steps/visual_production/stock_ticker_tool.py`
   - Method: `create_ticker_overlay_image(stocks)`
   - Delegates to:
     ```python
     # File: src/pipeline_steps/visual_production/bottom_ticker_generator.py
     from bottom_ticker_generator import BottomTickerGenerator

     generator = BottomTickerGenerator()
     ticker_path = generator.create_ticker_image(stocks, "ticker_strip.png")
     ```

3. **Bottom Ticker Generation:**
   - File: `src/pipeline_steps/visual_production/bottom_ticker_generator.py`
   - Class: `BottomTickerGenerator`
   - Method: `create_ticker_image(stocks, output_filename)`
   - Process:
     ```python
     from PIL import Image, ImageDraw, ImageFont

     # Calculate width (18x screen width for smooth scrolling)
     stock_width = 450  # px per stock
     total_width = max(stock_width * len(stocks), 1080 * 18)  # 19,440px
     ticker_height = 120  # px

     # Create image
     img = Image.new('RGB', (total_width, ticker_height), (0, 0, 0))
     draw = ImageDraw.Draw(img)

     # Fonts
     symbol_font = ImageFont.truetype("arial.ttf", 36)
     price_font = ImageFont.truetype("arial.ttf", 32)
     change_font = ImageFont.truetype("arial.ttf", 30)

     # Draw stocks repeatedly to fill width
     x_position = 20
     stock_index = 0

     while x_position < total_width:
         stock = stocks[stock_index % len(stocks)]

         # Draw symbol (white)
         draw.text((x_position, 35), stock['symbol'], fill=(255,255,255), font=symbol_font)
         x_position += 140

         # Draw price (white)
         price_str = f"${stock['current_price']:,.2f}"
         draw.text((x_position, 38), price_str, fill=(255,255,255), font=price_font)
         x_position += 160

         # Draw change (green/red)
         change = stock['change_percent']
         color = (34, 197, 94) if change >= 0 else (239, 68, 68)
         change_str = f"+{change:.2f}%" if change >= 0 else f"{change:.2f}%"
         draw.text((x_position, 40), change_str, fill=color, font=change_font)
         x_position += 120

         # Separator
         draw.line([(x_position, 30), (x_position, 90)], fill=(64,64,64), width=3)
         x_position += 30

         stock_index += 1

     # Save
     output_path = "output/financial_shorts/ticker_strip.png"
     img.save(output_path, 'PNG', quality=100)

     return output_path
     ```

**Input:**
- **File:** `output/financial_shorts/financial_analysis.json`
- **Required Keys:** `related_stocks[]{symbol, current_price, change_percent}`

**Output:**
- **File:** `output/financial_shorts/ticker_strip.png`
- **Format:** PNG image
- **Dimensions:** 19,440 x 120px (18x screen width)
- **Contents:** Repeating stock ticker (SYMBOL $PRICE ±CHANGE%)
- **Colors:**
  - Background: Black (0,0,0)
  - Text: White (255,255,255)
  - Positive change: Green (34,197,94)
  - Negative change: Red (239,68,68)

**Code References:**
- Reads: `financial_analysis.json` (field: `related_stocks[]`)
- Writes: `ticker_strip.png`
- Used by: `--step=assemble-video` (scrolling ticker layer)

---

### STEP 8: GENERATE STUDIO

**Command:** `--step=generate-studio`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
async def _handle_generate_studio(self):
    # Line 377-386
```

**Module Called:**
```python
# File: src/pipeline_steps/visual_production/studio_set_generator.py
class StudioSetGenerator:
    async def generate_studio_background(self, branding_text: str, output_filename: str) -> str:
        # Uses Google Gemini 2.0 Flash
```

**Process Flow:**
1. **Line 380-383:** Generate studio background
   ```python
   background_path = await self.studio_set_gen.generate_studio_background(
       branding_text="XINSIDER",
       output_filename="studio_background.png"
   )
   ```
   - File: `src/pipeline_steps/visual_production/studio_set_generator.py`
   - Method: `generate_studio_background(branding_text, output_filename)`
   - API Call: Google Gemini 2.0 Flash
   - Process:
     ```python
     import google.generativeai as genai

     genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
     model = genai.GenerativeModel('gemini-2.0-flash-exp')

     # Studio prompt
     prompt = f"""
     Create a professional financial news studio background for vertical video (1080x1920).

     Style: Modern, clean, minimalist newsroom
     Colors: White/gray palette with subtle blue accents
     Branding: "{branding_text}" logo subtle in corner
     Layout: Optimized for vertical video format
     Quality: High resolution, broadcast quality

     The background should have:
     - Clean white/light gray base
     - Subtle depth with soft shadows
     - Professional lighting simulation
     - Space for overlaid content (captions, graphics)
     - No distracting elements
     """

     # Generate
     response = model.generate_image(
         prompt=prompt,
         aspect_ratio="9:16",
         style="photographic"
     )

     # Save
     output_path = f"output/financial_shorts/{output_filename}"
     with open(output_path, 'wb') as f:
         f.write(response.image_bytes)

     return output_path
     ```

**Environment Variables Used:**
- `GEMINI_API_KEY` (from `.env`)

**Input:**
- None (uses hardcoded branding text)

**Output:**
- **File:** `output/financial_shorts/studio_background.png`
- **Format:** PNG image
- **Dimensions:** 1080 x 1920px (vertical 9:16)
- **Style:** Professional newsroom studio, white/gray palette
- **Quality:** High resolution for full-screen background

**Code References:**
- Reads: None
- Writes: `studio_background.png`
- Used by: `--step=assemble-video` (base background layer)

---

### STEP 10: PLAN PRODUCTION

**Command:** `--step=plan-production`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
def _handle_plan_production(self):
    # Line 331-338
```

**Module Called:**
```python
# File: src/pipeline_steps/visual_production/deterministic_production_planner.py
class DeterministicProductionPlanner:
    def create_and_save_plan(self) -> str:
        # Rule-based planning (NO AI)
```

**Process Flow:**
1. **Line 335:** `plan_path = self.production_planner.create_and_save_plan()`
   - File: `src/pipeline_steps/visual_production/deterministic_production_planner.py`
   - Method: `create_and_save_plan()`

2. **Internal Process:**
   ```python
   class DeterministicProductionPlanner:
       def create_and_save_plan(self):
           # Step 1: Load all assets
           assets = self.load_assets()

           # Step 2: Create production plan
           plan = self.create_production_plan(assets)

           # Step 3: Save plan
           plan_path = self.save_production_plan(plan)

           return plan_path
   ```

3. **Load Assets (Line 36-80):**
   ```python
   def load_assets(self) -> Dict:
       assets = {}

       # REQUIRED: timestamps
       timestamps_path = Path("output/financial_shorts/timestamps.json")
       with open(timestamps_path) as f:
           assets['timestamps'] = json.load(f)

       # REQUIRED: script
       script_path = Path("output/financial_shorts/financial_analysis.json")
       with open(script_path) as f:
           assets['script'] = json.load(f)

       # OPTIONAL: illustrations
       illustrations_path = Path("output/illustrations/illustrations_manifest.json")
       if illustrations_path.exists():
           with open(illustrations_path) as f:
               assets['illustrations'] = json.load(f)

       # OPTIONAL: character poses (not used in v2)
       poses_path = Path("output/character_poses/pose_catalog.json")
       if poses_path.exists():
           with open(poses_path) as f:
               assets['poses'] = json.load(f)

       # OPTIONAL: stock data
       stock_path = Path("output/financial_shorts/tweet_selection_report.json")
       if stock_path.exists():
           with open(stock_path) as f:
               assets['stocks'] = json.load(f)

       return assets
   ```

4. **Create Scenes (Line 82-141):**
   ```python
   def create_scenes_from_timestamps(self, timestamps: Dict) -> List[Dict]:
       words = timestamps.get('words', [])
       scenes = []

       current_scene_words = []
       current_scene_start = words[0]['start']
       scene_number = 1

       for i, word in enumerate(words):
           current_scene_words.append(word)

           # Break conditions:
           should_break = False

           # 1. Natural pause (> 0.5s)
           if i < len(words) - 1:
               pause = words[i + 1]['start'] - word['end']
               if pause > 0.5:
                   should_break = True

           # 2. Max scene length (8s)
           scene_duration = word['end'] - current_scene_start
           if scene_duration > 8.0:
               should_break = True

           # 3. Last word
           if i == len(words) - 1:
               should_break = True

           if should_break:
               # Create scene
               scene_end = current_scene_words[-1]['end']
               scene_text = ' '.join([w['word'] for w in current_scene_words])

               scenes.append({
                   'scene_number': scene_number,
                   'start_time': current_scene_start,
                   'end_time': scene_end,
                   'duration': scene_end - current_scene_start,
                   'narration_text': scene_text,
                   'words': current_scene_words.copy()
               })

               scene_number += 1
               current_scene_words = []
               if i < len(words) - 1:
                   current_scene_start = words[i + 1]['start']

       return scenes
   ```

5. **Assign Visuals (Line 143-238):**
   ```python
   def assign_visuals_to_scenes(self, scenes: List[Dict], assets: Dict) -> List[Dict]:
       illustrations = assets.get('illustrations', {}).get('images', [])

       # Round-robin assignment
       illustration_idx = 0

       for i, scene in enumerate(scenes):
           # Alternate effects
           effects = ['zoom_in', 'static', 'zoom_center']
           effect = effects[i % len(effects)]

           # Assign illustration
           if illustrations:
               illustration = illustrations[illustration_idx % len(illustrations)]
               illustration_idx += 1

               scene['visuals'] = {
                   'background': 'output/financial_shorts/studio_background.png',
                   'main_content': {
                       'type': 'illustration',
                       'file': illustration.get('image_path') or illustration.get('file_path', ''),
                       'effect': effect,
                       'position': {'x': 75, 'y': 300, 'width': 930, 'height': 700}
                   },
                   'ticker': {
                       'file': 'output/financial_shorts/ticker_strip.png',
                       'scroll_speed': 100,
                       'position': {'x': 0, 'y': 1400, 'width': 1080, 'height': 120}
                   }
               }

           # Add captions (word-level timestamps)
           scene['captions'] = {
               'enabled': True,
               'words': scene['words'],  # Real timestamps from Whisper
               'style': {
                   'font_size': 32,
                   'font_weight': 'bold',
                   'active_color': '#FFD700',
                   'inactive_color': '#000000',
                   'background': 'rgba(255, 255, 255, 0.8)',
                   'position_y': 1350
               }
           }

           # Add transition
           scene['transition'] = {'type': 'fade', 'duration': 0.5}

       return scenes
   ```

6. **Build Production Plan (Line 240-318):**
   ```python
   def create_production_plan(self, assets: Dict) -> Dict:
       # Create scenes from timestamps
       scenes = self.create_scenes_from_timestamps(assets['timestamps'])

       # Assign visuals to scenes
       scenes = self.assign_visuals_to_scenes(scenes, assets)

       # Calculate total duration
       total_duration = scenes[-1]['end_time'] if scenes else 0

       plan = {
           'video_metadata': {
               'title': assets['script'].get('title', 'Financial Short'),
               'duration_seconds': round(total_duration, 2),
               'resolution': '1080x1920',
               'fps': 30
           },
           'audio': {
               'narration': {
                   'file': 'output/financial_shorts/narration.mp3',
                   'volume': 1.0
               },
               'music': {
                   'file': 'output/music/galactic_rap.mp3',
                   'volume': 0.22,
                   'loop': True
               }
           },
           'scenes': scenes,
           'global_layers': {
               'tweet_chart_alternator': {
                   'enabled': True,
                   'tweet_file': 'output/tweet_screenshots/selected_tweet.png',
                   'chart_file': 'output/stock_charts/tsla_chart.png',
                   'alternation_interval': 30,
                   'transition_duration': 1.0,
                   'position': {'y': 1120, 'max_width': 900, 'max_height': 400}
               }
           }
       }

       return plan
   ```

**Input Files:**
- **REQUIRED:**
  - `output/financial_shorts/timestamps.json`
  - `output/financial_shorts/financial_analysis.json`
- **OPTIONAL:**
  - `output/illustrations/illustrations_manifest.json`
  - `output/character_poses/pose_catalog.json`
  - `output/financial_shorts/tweet_selection_report.json`

**Output:**
- **File:** `output/financial_shorts/production_plan.json`
- **Schema:** (See full schema in PIPELINE_ANALYSIS.md)

**Code References:**
- Reads:
  - `timestamps.json` (REQUIRED)
  - `financial_analysis.json` (REQUIRED)
  - `illustrations_manifest.json` (optional)
  - `pose_catalog.json` (optional)
  - `tweet_selection_report.json` (optional)
- Writes: `production_plan.json`
- Next step: `--step=assemble-video`

---

### STEP 11: ASSEMBLE VIDEO

**Command:** `--step=assemble-video`

**Handler Function:**
```python
# File: src/handlers/financial_shorts_handler.py
def _handle_assemble_video(self):
    # Line 340-354
```

**Module Called:**
```python
# File: src/pipeline_steps/visual_production/final_video_assembler.py
class FinalVideoAssembler:
    def assemble_from_plan_file(self, plan_path: str) -> str:
        # Uses MoviePy for video composition
```

**Process Flow:**
1. **Line 342:** `plan_path = self._get_output_path("production_plan.json")`

2. **Line 351:** `video_path = self.video_assembler.assemble_from_plan_file(plan_path)`
   - File: `src/pipeline_steps/visual_production/final_video_assembler.py`
   - Method: `assemble_from_plan_file(plan_path)`

3. **Internal Process (Simplified):**
   ```python
   from moviepy import *
   from PIL import Image
   import numpy as np

   def assemble_from_plan_file(self, plan_path: str) -> str:
       # Load plan
       with open(plan_path) as f:
           plan = json.load(f)

       scenes = plan['scenes']

       # PHASE 1: Pre-cache all images (Line 393-438)
       image_cache = {}

       # Cache studio background
       bg_file = scenes[0].get('visuals', {}).get('background', '')
       bg_img = Image.open(bg_file).resize((1080, 1920))
       image_cache[bg_file] = np.array(bg_img.convert('RGB'))

       # Cache all illustrations
       for scene in scenes:
           content_file = scene.get('visuals', {}).get('main_content', {}).get('file', '')
           if content_file:
               content_img = Image.open(content_file).resize((1080, 700))
               cache_key = f"{content_file}_illustration_top"
               image_cache[cache_key] = np.array(content_img.convert('RGB'))

       # PHASE 2: Calculate total duration (Line 454-472)
       all_words = []
       for scene in scenes:
           all_words.extend(scene.get('captions', {}).get('words', []))

       last_word_end = max(word['end'] for word in all_words)
       total_duration = last_word_end + 1.0  # Add 1s buffer

       # PHASE 3: Create continuous base video (Line 474-529)
       # Background clip (full duration)
       bg_array = image_cache[bg_file]
       base_bg_clip = ImageClip(bg_array).with_duration(total_duration)

       # Illustration clips (timed)
       illustration_clips = []
       current_time = 0

       for i, scene in enumerate(scenes):
           scene_duration = scene.get("duration", 5)
           content_file = scene.get('visuals', {}).get('main_content', {}).get('file', '')

           if content_file:
               cache_key = f"{content_file}_illustration_top"
               content_array = image_cache[cache_key]

               # Last illustration extends to end
               if i == len(scenes) - 1:
                   illustration_duration = total_duration - current_time
               else:
                   illustration_duration = scene_duration

               illustration_clip = ImageClip(content_array)
               illustration_clip = illustration_clip.with_duration(illustration_duration)
               illustration_clip = illustration_clip.with_start(current_time)
               illustration_clip = illustration_clip.with_position(('center', 50))
               illustration_clips.append(illustration_clip)

           current_time += scene_duration

       # Composite background + illustrations
       base_clips = [base_bg_clip] + illustration_clips
       base_video = CompositeVideoClip(base_clips, size=(1080, 1920))
       base_video = base_video.with_duration(total_duration)
       base_video = base_video.with_fps(30)

       # PHASE 4: Create tweet/chart alternator (Line 531-562)
       tweet_chart_clip = self.create_tweet_chart_alternator(
           tweet_path="output/tweet_screenshots/selected_tweet.png",
           chart_path="output/stock_charts/tsla_chart.png",
           total_duration=total_duration
       )
       tweet_chart_clip = tweet_chart_clip.with_position(('center', 900))

       # PHASE 5: Create scrolling ticker (Line 564-581)
       ticker_clip = self.create_scrolling_ticker(
           ticker_path="output/financial_shorts/ticker_strip.png",
           duration=total_duration,
           scroll_speed=100
       )
       ticker_clip = ticker_clip.with_position((0, 1520))

       # PHASE 6: Create word-by-word captions (Line 495-498)
       caption_clips = self.create_word_by_word_captions(all_words, total_duration)

       # PHASE 7: Composite all layers (Line 500-519)
       final_layers = [
           base_video,              # Layer 1: Background + illustrations
           tweet_chart_clip,        # Layer 2: Tweet/chart alternator
           ticker_clip,             # Layer 3: Scrolling ticker
           *caption_clips           # Layer 4: Captions (on top)
       ]

       final_video = CompositeVideoClip(final_layers, size=(1080, 1920))
       final_video = final_video.with_duration(total_duration)
       final_video = final_video.with_fps(30)

       # PHASE 8: Add audio (Line 521-537)
       # Narration
       narration = AudioFileClip("output/financial_shorts/narration.mp3")

       # Background music
       music = AudioFileClip("output/music/galactic_rap.mp3")
       music = music.with_volume(0.22)
       music = music.audio_loop(duration=total_duration)

       # Mix audio
       final_audio = CompositeAudioClip([narration, music])
       final_video = final_video.with_audio(final_audio)

       # PHASE 9: Render video (Line 539-552)
       output_path = "output/financial_shorts/final_video.mp4"

       final_video.write_videofile(
           output_path,
           fps=30,
           codec='libx264',
           audio_codec='aac',
           temp_audiofile='temp-audio.m4a',
           remove_temp=True,
           preset='medium',
           threads=4
       )

       return output_path
   ```

**Dependencies:**
- `moviepy` (video composition)
- `PIL/Pillow` (image processing)
- `numpy` (array operations)
- `ffmpeg` (video encoding)

**Input Files:**
- **REQUIRED:**
  - `output/financial_shorts/production_plan.json`
  - `output/financial_shorts/studio_background.png`
  - `output/illustrations/*.png` (all illustrations)
  - `output/financial_shorts/narration.mp3`
  - `output/financial_shorts/ticker_strip.png`
  - `output/tweet_screenshots/selected_tweet.png`
  - `output/stock_charts/tsla_chart.png`
- **OPTIONAL:**
  - `output/music/galactic_rap.mp3` (background music)

**Output:**
- **File:** `output/financial_shorts/final_video.mp4`
- **Format:** MP4 (H.264 + AAC)
- **Resolution:** 1080 x 1920px (9:16 vertical)
- **FPS:** 30
- **Duration:** ~90-120 seconds (matches audio)
- **Audio:** Stereo, 44.1kHz, AAC codec
- **Bitrate:** ~5-8 Mbps (video), 128 kbps (audio)

**Video Layers (bottom to top):**
1. Studio background (1080x1920, full duration)
2. Illustrations (timed, with start times)
3. Tweet/Chart alternator (30s cycles, fade transitions)
4. Scrolling ticker (seamless loop, 19,440px width)
5. Captions (word-by-word, Impact font, 144px)

**Code References:**
- Reads:
  - `production_plan.json`
  - `studio_background.png`
  - `illustrations/*.png`
  - `narration.mp3`
  - `ticker_strip.png`
  - `selected_tweet.png`
  - `{symbol}_chart.png`
  - `galactic_rap.mp3` (optional)
- Writes: `final_video.mp4`

---

## 🔗 FILE INTERDEPENDENCIES GRAPH

```
viral_tweets_normalized.json
    ↓
tweet_selection_report.json ──────┐
    ↓                              │
financial_analysis.json ───────────┼──────┐
    ↓                              │      │
narration.mp3                      │      │
    ↓                              │      │
timestamps.json ───────────────────┼──────┼──────┐
                                   │      │      │
image_prompts.json                 │      │      │
    ↓                              │      │      │
illustrations_manifest.json ───────┼──────┼──────┤
                                   │      │      │
selected_tweet.png                 │      │      │
{symbol}_chart.png ────────────────┘      │      │
ticker_strip.png ─────────────────────────┘      │
studio_background.png ───────────────────────────┘
                                                  ↓
                                        production_plan.json
                                                  ↓
                                           final_video.mp4
```

---

## 📄 JSON SCHEMA DOCUMENTATION

### Complete schemas documented in separate sections above

---

## 🔄 FUNCTION CALL CHAIN

### Full Pipeline Flow:

```
main.py:main()
  ↓
FinancialShortsHandler.execute(command)
  ↓
_handle_full_pipeline()
  ├─> _handle_fetch_tweets()
  │     ├─> TwitterGrokScraper.fetch_viral_tweets()
  │     └─> JSONNormalizer.normalize_grok_response()
  │
  ├─> _handle_select_tweet()
  │     ├─> TweetSelector.select_best_tweet()
  │     └─> TweetSelector.save_selection_report()
  │
  ├─> _handle_analyze()
  │     └─> ClaudeFinancialAnalyst.analyze_tweet_and_generate_script()
  │
  ├─> _handle_generate_audio()
  │     └─> generate_audio_from_script()
  │
  ├─> _handle_transcribe()
  │     └─> transcribe_audio()
  │
  ├─> _handle_generate_screenshot()
  │     └─> TweetScreenshotGenerator.generate_screenshot()
  │
  ├─> _handle_generate_stock_charts()
  │     └─> StockChartGenerator.generate_charts_from_stocks()
  │
  ├─> _handle_generate_image_prompts()
  │     └─> ImagePromptGenerator.generate_and_save()
  │
  ├─> _handle_generate_illustrations()
  │     └─> IllustrationGenerator.generate_from_prompts_file()
  │
  ├─> _handle_create_ticker()
  │     ├─> StockTickerTool.create_ticker_overlay_image()
  │     └─> BottomTickerGenerator.create_ticker_image()
  │
  ├─> _handle_generate_studio()
  │     └─> StudioSetGenerator.generate_studio_background()
  │
  ├─> _handle_plan_production()
  │     ├─> DeterministicProductionPlanner.load_assets()
  │     ├─> DeterministicProductionPlanner.create_scenes_from_timestamps()
  │     ├─> DeterministicProductionPlanner.assign_visuals_to_scenes()
  │     └─> DeterministicProductionPlanner.create_production_plan()
  │
  └─> _handle_assemble_video()
        ├─> FinalVideoAssembler.assemble_from_plan_file()
        │     ├─> Pre-cache images
        │     ├─> Create continuous base video
        │     ├─> create_tweet_chart_alternator()
        │     ├─> create_scrolling_ticker()
        │     ├─> create_word_by_word_captions()
        │     └─> Composite all layers
        └─> MoviePy.write_videofile()
```

---

**Generated:** 2025-01-12
**Pipeline Version:** v3-dev
**Author:** Claude Code + Juan Valencia
