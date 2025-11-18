"""
Command Handler for XInsider Financial Shorts Pipeline
"""

import sys
import os
import json
import asyncio
from typing import Optional
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pipeline_steps.data_collection import TwitterGrokScraper, JSONNormalizer, TweetSelector
from pipeline_steps.content_generation import ClaudeFinancialAnalyst, generate_audio_from_script, transcribe_audio
from pipeline_steps.visual_production import (
    StockTickerTool, FrameCompositor,
    DeterministicProductionPlanner, FinalVideoAssembler
)
# One-time generators moved to utils
from src.tools.createTweetScreenshot import TweetScreenshotGenerator
from utils.stock_chart_generator import StockChartGenerator
from utils.image_prompt_generator import ImagePromptGenerator
from utils.illustration_generator import IllustrationGenerator
from utils.studio_set_generator import StudioSetGenerator
from utils.character_pose_generator import CharacterPoseGenerator
from config.pipeline_config import PipelineConfig
from ui.console import Console

SEPARATOR = "=" * 60


class FinancialShortsHandler:
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.console = Console()
        self.output_dir = Path(os.path.join(os.path.dirname(__file__), "..", "..", "output", "financial_shorts")).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._twitter_scraper = None
        self._json_normalizer = None
        self._tweet_selector = None
        self._claude_analyst = None
        self._screenshot_gen = None
        self._stock_ticker = None
        self._studio_set_gen = None
        self._frame_compositor = None
        self._pose_generator = None
        self._stock_chart_gen = None
        self._image_prompt_gen = None
        self._illustration_gen = None
        self._production_planner = None
        self._video_assembler = None

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
            "--help": self._handle_help,
        }

    @property
    def twitter_scraper(self):
        if self._twitter_scraper is None:
            self._twitter_scraper = TwitterGrokScraper()
        return self._twitter_scraper

    @property
    def json_normalizer(self):
        if self._json_normalizer is None:
            self._json_normalizer = JSONNormalizer()
        return self._json_normalizer

    @property
    def tweet_selector(self):
        if self._tweet_selector is None:
            self._tweet_selector = TweetSelector()
        return self._tweet_selector

    @property
    def claude_analyst(self):
        if self._claude_analyst is None:
            self._claude_analyst = ClaudeFinancialAnalyst()
        return self._claude_analyst

    @property
    def screenshot_gen(self):
        if self._screenshot_gen is None:
            self._screenshot_gen = TweetScreenshotGenerator()
        return self._screenshot_gen

    @property
    def stock_ticker(self):
        if self._stock_ticker is None:
            self._stock_ticker = StockTickerTool()
        return self._stock_ticker

    @property
    def studio_set_gen(self):
        if self._studio_set_gen is None:
            self._studio_set_gen = StudioSetGenerator()
        return self._studio_set_gen

    @property
    def frame_compositor(self):
        if self._frame_compositor is None:
            self._frame_compositor = FrameCompositor()
        return self._frame_compositor

    @property
    def pose_generator(self):
        if self._pose_generator is None:
            self._pose_generator = CharacterPoseGenerator()
        return self._pose_generator

    @property
    def stock_chart_gen(self):
        if self._stock_chart_gen is None:
            self._stock_chart_gen = StockChartGenerator()
        return self._stock_chart_gen

    @property
    def image_prompt_gen(self):
        if self._image_prompt_gen is None:
            self._image_prompt_gen = ImagePromptGenerator()
        return self._image_prompt_gen

    @property
    def illustration_gen(self):
        if self._illustration_gen is None:
            self._illustration_gen = IllustrationGenerator()
        return self._illustration_gen

    @property
    def production_planner(self):
        if self._production_planner is None:
            self._production_planner = DeterministicProductionPlanner()
        return self._production_planner

    @property
    def video_assembler(self):
        if self._video_assembler is None:
            self._video_assembler = FinalVideoAssembler()
        return self._video_assembler

    def _get_output_path(self, filename: str) -> str:
        return str(self.output_dir / filename)

    def execute(self, command: Optional[str] = None):
        try:
            if command is None:
                asyncio.run(self._handle_full_pipeline())
            elif command in self.commands:
                if asyncio.iscoroutinefunction(self.commands[command]):
                    asyncio.run(self.commands[command]())
                else:
                    self.commands[command]()
            else:
                print(f"[ERROR] Unknown command: {command}")
                self._handle_help()
                sys.exit(1)
        except KeyboardInterrupt:
            print("\n\n[WARNING] Pipeline interrupted")
            sys.exit(0)
        except Exception as e:
            print(f"[ERROR] Pipeline failed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    async def _handle_fetch_tweets(self):
        self.console.print_header("STEP 1: FETCH VIRAL TWEETS")
        raw_grok_response = await self.twitter_scraper.fetch_viral_tweets()
        if not raw_grok_response:
            print("[ERROR] Failed to fetch tweets")
            return
        tweets_data = self.json_normalizer.normalize_grok_response(json.dumps(raw_grok_response))
        output_path = self._get_output_path("viral_tweets_normalized.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tweets_data, f, indent=2, ensure_ascii=False)
        num_tweets = len(tweets_data.get('viral_tweets', []))
        print(f"\n[OK] Fetched {num_tweets} viral tweets")
        print(f"[SAVE] {output_path}")

    async def _handle_select_tweet(self):
        self.console.print_header("STEP 2: SELECT BEST TWEET")
        tweets_path = self._get_output_path("viral_tweets_normalized.json")
        try:
            with open(tweets_path, 'r', encoding='utf-8') as f:
                tweets_data = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Tweets file not found: {tweets_path}")
            return
        selection_result = self.tweet_selector.select_best_tweet(tweets_data)
        if selection_result:
            report_path = self._get_output_path("tweet_selection_report.json")
            self.tweet_selector.save_selection_report(selection_result, report_path)

    async def _handle_analyze(self):
        self.console.print_header("STEP 3: FINANCIAL ANALYSIS & SCRIPT")
        report_path = self._get_output_path("tweet_selection_report.json")
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                selection_report = json.load(f)
                selected_tweet = selection_report['selected_tweet']
        except FileNotFoundError:
            print(f"[ERROR] Selection report not found")
            return
        print("\n[AI] Claude is analyzing...")
        analysis_data = await self.claude_analyst.analyze_tweet_and_generate_script(selected_tweet)
        if analysis_data:
            output_path = self._get_output_path("financial_analysis.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            print(f"\n[OK] Analysis saved: {output_path}")

    async def _handle_generate_audio(self):
        self.console.print_header("STEP 4: GENERATE AUDIO")
        analysis_path = self._get_output_path("financial_analysis.json")
        audio_output_path = self._get_output_path("narration.mp3")
        try:
            generate_audio_from_script(
                script_file=analysis_path,
                output_file=audio_output_path
            )
            print(f"\n[OK] Audio: {audio_output_path}")
        except Exception as e:
            print(f"[ERROR] Audio generation failed: {str(e)}")

    async def _handle_transcribe(self):
        self.console.print_header("STEP 5: TRANSCRIBE AUDIO")
        audio_path = self._get_output_path("narration.mp3")
        try:
            timestamp_data = transcribe_audio(audio_path)
            output_path = self._get_output_path("timestamps.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(timestamp_data, f, indent=2, ensure_ascii=False)
            print(f"\n[OK] Timestamps: {output_path}")
        except Exception as e:
            print(f"[ERROR] Transcription failed: {str(e)}")

    async def _handle_generate_screenshot(self):
        self.console.print_header("STEP 6: GENERATE SCREENSHOT")
        report_path = self._get_output_path("tweet_selection_report.json")
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                selection_report = json.load(f)
                selected_tweet = selection_report['selected_tweet']
        except FileNotFoundError:
            print(f"[ERROR] Selection report not found")
            return
        screenshot_path = await self.screenshot_gen.generate_screenshot(selected_tweet, filename="selected_tweet")
        if screenshot_path:
            print(f"\n[OK] Screenshot: {screenshot_path}")

    async def _handle_generate_stock_charts(self):
        self.console.print_header("STEP 6B: GENERATE STOCK CHARTS")
        report_path = self._get_output_path("tweet_selection_report.json")
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                selection_report = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Selection report not found")
            return

        # Extract stocks from related_stocks field (nested inside selected_tweet)
        selected_tweet = selection_report.get('selected_tweet', {})
        related_stocks = selected_tweet.get('related_stocks', [])

        if not related_stocks:
            print("[WARNING] No stock data found in tweet_selection_report.json")
            print("[INFO] Expected structure: selected_tweet.related_stocks")
            return

        print(f"\n[INFO] Found {len(related_stocks)} stock(s) to generate charts for")

        # Generate charts for all stocks
        chart_paths = self.stock_chart_gen.generate_charts_from_stocks(
            stocks=related_stocks,
            period="1y"  # 1 year period for monthly data visualization
        )

        if chart_paths:
            print(f"\n[OK] Generated {len(chart_paths)} stock chart(s)")
            for path in chart_paths:
                print(f"[CHART] {path}")
        else:
            print("[WARNING] No charts generated")

    def _handle_generate_image_prompts(self):
        self.console.print_header("STEP 6C: GENERATE IMAGE PROMPTS")
        analysis_path = self._get_output_path("financial_analysis.json")

        try:
            # Generate prompts using GPT-4o
            prompts_path = self.image_prompt_gen.generate_and_save(
                financial_analysis_path=analysis_path,
                target_image_count=12
            )
            print(f"\n[OK] Image prompts generated: {prompts_path}")
        except Exception as e:
            print(f"[ERROR] Failed to generate image prompts: {str(e)}")

    async def _handle_generate_illustrations(self):
        self.console.print_header("STEP 6D: GENERATE ILLUSTRATIONS")
        prompts_path = self._get_output_path("image_prompts.json")

        try:
            if not Path(prompts_path).exists():
                print(f"[ERROR] Image prompts file not found: {prompts_path}")
                print("[INFO] Run --step=generate-image-prompts first")
                return

            # Generate illustrations using Gemini
            manifest_path = await self.illustration_gen.generate_from_prompts_file(
                prompts_file_path=prompts_path,
                skip_if_exists=True
            )
            print(f"\n[OK] Illustrations manifest: {manifest_path}")
        except Exception as e:
            print(f"[ERROR] Failed to generate illustrations: {str(e)}")

    def _handle_plan_production(self):
        self.console.print_header("STEP 10: PLAN PRODUCTION")
        try:
            # Create production plan
            plan_path = self.production_planner.create_and_save_plan()
            print(f"\n[OK] Production plan created: {plan_path}")
        except Exception as e:
            print(f"[ERROR] Failed to create production plan: {str(e)}")

    def _handle_assemble_video(self):
        self.console.print_header("STEP 11: ASSEMBLE VIDEO")
        plan_path = self._get_output_path("production_plan.json")

        try:
            if not Path(plan_path).exists():
                print(f"[ERROR] Production plan not found: {plan_path}")
                print("[INFO] Run --step=plan-production first")
                return

            # Assemble final video
            video_path = self.video_assembler.assemble_from_plan_file(plan_path)
            print(f"\n[OK] Final video created: {video_path}")
        except Exception as e:
            print(f"[ERROR] Failed to assemble video: {str(e)}")

    async def _handle_create_ticker(self):
        self.console.print_header("STEP 7: CREATE BOTTOM TICKER")
        analysis_path = self._get_output_path("financial_analysis.json")
        try:
            with open(analysis_path, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Analysis not found")
            return

        # Extract stocks directly from financial_analysis.json
        related_stocks = analysis_data.get('related_stocks', [])
        if not related_stocks:
            print("[WARNING] No stock data found in analysis")
            return

        # Create ticker image
        overlay_path = self.stock_ticker.create_ticker_overlay_image(related_stocks)
        if overlay_path:
            print(f"\n[OK] Ticker: {overlay_path}")

    async def _handle_generate_studio(self):
        self.console.print_header("STEP 8: GENERATE STUDIO BACKGROUND")
        try:
            background_path = await self.studio_set_gen.generate_studio_background(
                branding_text="XINSIDER",
                output_filename="studio_background.png"
            )
            print(f"\n[OK] Studio background: {background_path}")
        except Exception as e:
            print(f"[ERROR] Studio generation failed: {str(e)}")

    async def _handle_compose_preview(self):
        self.console.print_header("STEP 9: COMPOSE PREVIEW FRAME")
        try:
            # Paths to all required assets
            studio_bg = self._get_output_path("studio_background.png")
            character = os.path.join(os.path.dirname(__file__), "..", "image", "base_image.png")
            tweet = os.path.join(os.path.dirname(__file__), "..", "..", "output", "tweet_screenshots", "selected_tweet.png")
            ticker = self._get_output_path("ticker_strip.png")

            # Compose frame
            frame_path = self.frame_compositor.compose_frame(
                studio_bg_path=studio_bg,
                character_path=character,
                tweet_path=tweet,
                ticker_path=ticker,
                output_filename="preview_frame.png"
            )
            print(f"\n[OK] Preview frame: {frame_path}")
        except Exception as e:
            print(f"[ERROR] Frame composition failed: {str(e)}")
            import traceback
            traceback.print_exc()

    async def _handle_test_poses(self):
        self.console.print_header("STEP 10: TEST CHARACTER POSE GENERATION")
        try:
            print("\n[INFO] This will generate first 5 AI character poses with Gemini 2.0 Flash")
            print("[INFO] Test mode - verify quality before generating all 50 poses")
            print("[INFO] Poses will be saved to: output/character_poses/\n")

            catalog_path = await self.pose_generator.generate_pose_library(test_mode=True)

            print(f"\n[OK] Test poses generated!")
            print(f"[OK] Catalog: {catalog_path}")
            print(f"[OK] Total poses: 5 (test mode)")
            print(f"[NEXT] Review the poses, then run: python main.py --step=generate-pose-library")
        except Exception as e:
            print(f"[ERROR] Test pose generation failed: {str(e)}")
            import traceback
            traceback.print_exc()

    async def _handle_generate_pose_library(self):
        self.console.print_header("STEP 10: GENERATE CHARACTER POSE LIBRARY")
        try:
            print("\n[INFO] This will generate 50 AI character poses with Gemini 2.0 Flash")
            print("[INFO] This process may take 5-10 minutes...")
            print("[INFO] Poses will be saved to: output/character_poses/\n")

            catalog_path = await self.pose_generator.generate_pose_library(test_mode=False)

            print(f"\n[OK] Pose library generated!")
            print(f"[OK] Catalog: {catalog_path}")
            print(f"[OK] Total poses: 50")
            print(f"[OK] Categories: presenting, talking, reacting, emphasizing, neutral")
        except Exception as e:
            print(f"[ERROR] Pose generation failed: {str(e)}")
            import traceback
            traceback.print_exc()

    async def _handle_full_pipeline(self):
        self.console.print_header("FINANCIAL SHORTS PIPELINE - FULL RUN")
        try:
            await self._handle_fetch_tweets()
            await self._handle_select_tweet()
            await self._handle_analyze()
            await self._handle_generate_audio()
            await self._handle_transcribe()
            await self._handle_generate_screenshot()
            await self._handle_create_ticker()
            await self._handle_generate_studio()
            self.console.print_header("[OK] PIPELINE COMPLETE!")
            print(f"\n[OK] All files: {self.output_dir}")
        except Exception as e:
            print(f"[ERROR] Pipeline failed: {str(e)}")
            raise

    def _handle_help(self):
        self.console.print_header("XINSIDER - Financial Shorts Pipeline")
        print("\n" + "="*60)
        print("FULL WORKFLOWS:")
        print("="*60)
        print("\n  python main.py\n    > Complete pipeline (all steps)\n")
        print("\n" + "="*60)
        print("INDIVIDUAL STEPS:")
        print("="*60)
        print()
        print("DATA COLLECTION:")
        print("  --step=fetch-tweets       Fetch viral tweets from Grok AI")
        print("  --step=select-tweet       AI-powered tweet selection (GPT-4o)")
        print()
        print("CONTENT GENERATION:")
        print("  --step=analyze            Financial analysis + script generation (Claude)")
        print("  --step=generate-audio     Generate audio narration (ElevenLabs)")
        print("  --step=transcribe         Generate word-level timestamps (Whisper)")
        print()
        print("VISUAL PRODUCTION:")
        print("  --step=generate-screenshot     Generate tweet screenshot image")
        print("  --step=generate-stock-charts   Generate stock chart screenshots (B&W)")
        print("  --step=generate-image-prompts  Generate image prompts from script (GPT-4o)")
        print("  --step=generate-illustrations  Generate B&W illustrations (Gemini 2.0)")
        print("  --step=create-ticker           Create bottom ticker overlay")
        print("  --step=generate-studio         Generate studio newsroom background")
        print("  --step=compose-preview         Compose preview frame (all layers)")
        print("  --step=test-poses              Generate first 5 test poses (verify quality)")
        print("  --step=generate-pose-library   Generate 50 AI character poses (Gemini 2.0)")
        print()
        print("FINAL ASSEMBLY:")
        print("  --step=plan-production         Create production plan with GPT-4o")
        print("  --step=assemble-video          Assemble final video (MoviePy)")
        print()
        print(f"\n{SEPARATOR}\n")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else None
    handler = FinancialShortsHandler()
    handler.execute(command)


if __name__ == "__main__":
    main()
