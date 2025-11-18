from abc import ABC, abstractmethod
import asyncio
import json
from pathlib import Path
from typing import Optional
import os

from src.ai.createProductionPlan import ProductionPlanCreator
from src.ai.generateAudioElevenlabs import generate_audio_from_script
from src.ai.generateImages import generate_transparent_square_image
from src.tools.createTickerBackground import create_ticker_background_image
from src.tools.createTweetScreenshot import generate_tweet_screenshot
from src.tools.videoAssembler import VideoConfig, assemble_video
from src.tools.whisperTool import generate_timestamps_from_audio
from src.tools.download_images import download_image
from src.tools.createBottomTicker import generate_bottom_ticker

class BaseHandler(ABC):

    def __init__(self):
        self.current_dir = os.path.dirname(__file__)
        self.root_dir = os.path.abspath(os.path.join(self.current_dir, "..", ".."))
        self.base_dir = Path(self.root_dir)

        self.commands = {
            "create-production-plan": self._create_production_plan,
            "create-or-download-images": self._create_or_download_images,
            "create-audio-and-timestamps": self._create_audio_and_timestamps,
            "create-tweet-image": self._create_tweet_image,
            "create-ticker-background-image": self._create_ticket_background_image,
            "create-ticker-image": self._create_ticker_image,
            "create-final-video": self._create_final_video,
        }
        
    def execute(self, command: Optional[str]):
        """Ejecuta el comando exacto que el usuario pide."""
        if command in self.commands:
            handler = self.commands[command]
            try:
                handler()
            except Exception as e:
                print(f"[ERROR] Step failed: {e}")
        else:
            print(f"[ERROR] Unknown command: {command}")
            self.print_help()

    def _fetch_tweets(self):
        print("Fetching tweets...")
        print("Tweets fetched.")

    def _create_production_plan(self):
        print("Selecting tweets...")
        viral_tweets_path = (Path(self.root_dir) / "data" / "create_production_plan" / "input" / "viral_tweets.json")
        character_poses = (Path(self.root_dir) / "data" / "character_poses" / "character_poses.json")

        if not viral_tweets_path.is_file():
            print(f"[ERROR] Expected file but found nothing: {viral_tweets_path}")
            return
        if not character_poses.is_file():
            print(f"[ERROR] Expected file but found nothing: {character_poses}")
            return
        
        with open(viral_tweets_path, 'r', encoding='utf-8') as f: 
            viral_tweets_data = json.load(f)

        with open(character_poses, 'r', encoding='utf-8') as f:
            character_poses_data = json.load(f)

        try:
            creator = ProductionPlanCreator()
            plan = creator.create_plan(
                viral_tweets_data,
                character_poses_data
            )
        except Exception as e:
            print(f"[ERROR] Failed to create production plan: {e}")
            return

        if plan:
            creator.save_plan(plan, Path(self.root_dir) / "data" / "create_production_plan" / "output" / "production_plan.json")

    def _create_or_download_images(self):
        print("Creating or downloading images...")

        production_plan_path = (
            Path(self.root_dir) / "data" / "create_production_plan" / "output" / "production_plan.json"
        )

        # Validar si existe el archivo JSON
        if not production_plan_path.is_file():
            print(f"[ERROR] Expected file but found nothing: {production_plan_path}")
            return

        # Cargar JSON
        try:
            with open(production_plan_path, "r", encoding="utf-8") as f:
                production_plan_data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load JSON: {e}")
            return

        # Iterar segmentos
        for item in production_plan_data.get("segments", []):
            
            # Obtener visual
            visual = item.get("visual", {})
            if not isinstance(visual, dict):
                print(f"[WARNING] Invalid 'visual' structure for segment {item.get('segment_id')}. Skipping...")
                continue

            x_image_url = visual.get("image_url")
            image_prompt = visual.get("image_prompt")
            segment_id = item.get("segment_id", "unknown")

            filename = f"segment_{segment_id}.png"

            # ------------------------
            # 1. DESCARGAR IMAGEN SI HAY URL
            # ------------------------
            if not x_image_url or str(x_image_url).strip() == "":
                print(f"[WARNING] No image URL found for segment {segment_id}. Skipping download...")
            else:
                output_path = (
                    Path(self.root_dir) / "data" / "video_images" / "download_images" / filename
                )
                try:
                    download_image(x_image_url, output_path)
                except Exception as e:
                    print(f"[ERROR] Failed downloading image for segment {segment_id}: {e}")

            # ------------------------
            # 2. GENERAR IMAGEN SI HAY PROMPT
            # ------------------------
            if not image_prompt or str(image_prompt).strip() == "":
                print(f"[WARNING] No image prompt found for segment {segment_id}. Skipping generation...")
            else:
                output_folder = (
                    Path(self.root_dir) / "data" / "video_images" / "generated_images"
                )

                try:
                    generated_file = generate_transparent_square_image(
                        image_prompt, output_folder, filename
                    )
                    print(f"Generated file: {generated_file}")
                except Exception as e:
                    print(f"[ERROR] Failed generating image for segment {segment_id}: {e}")
                    print("Images created or downloaded.")
    
    def _create_audio_and_timestamps(self):
        print("Creating audio and timestamps...")

        # ==========================
        # 1. Paths & Config
        # ==========================
        voice_id_narrator = "yl2ZDV1MzN4HbQJbMihG"

        production_plan_path = (
            self.base_dir / "data" / "create_production_plan" / "output" / "production_plan.json"
        )

        output_audio_path = (
            self.base_dir / "data" / "video_audio" / "elevenlabs" / "narration.mp3"
        )

        output_timestamps_path = (
            self.base_dir / "data" / "video_audio" / "elevenlabs" / "timestamps.json"
        )

        # ==========================
        # 2. Validate JSON
        # ==========================
        if not production_plan_path.is_file():
            print(f"[ERROR] Expected file but found nothing: {production_plan_path}")
            return

        try:
            with open(production_plan_path, "r", encoding="utf-8") as f:
                production_plan_data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load JSON: {e}")
            return

        # ==========================
        # 3. Extract script
        # ==========================
        script_text = production_plan_data.get("full_script", "")

        # ==========================
        # 4. Generate audio
        # ==========================
        generate_audio_from_script(
            script_text,
            output_audio_path,
            voice_id_narrator
        )

        # ==========================
        # 5. Generate timestamps
        # ==========================
        generate_timestamps_from_audio(
            audio_file=str(output_audio_path),
            output_file=str(output_timestamps_path)
        )

        # ==========================
        # 6. Debug info
        # ==========================
        print(f"Script text: {script_text}")
        print("Audio and timestamps created.")

    def _create_tweet_image(self):  # SIN async
        print("Creating tweet image...")

        # ==========================
        # 1. Paths & Config
        # ==========================

        production_plan_path = (
            self.base_dir / "data" / "create_production_plan" / "output" / "production_plan.json"
        )

        output_tweet_image_path = (
            self.base_dir / "data" / "tweet_image" / "tweet_image.png"
        )

        # Validar si existe el archivo JSON
        if not production_plan_path.is_file():
            print(f"[ERROR] Expected file but found nothing: {production_plan_path}")
            return

        # Cargar JSON
        try:
            with open(production_plan_path, "r", encoding="utf-8") as f:
                production_plan_data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load JSON: {e}")
            return
        
        tweet_data = production_plan_data.get("selected_tweet_details", {})

        # ✅ Ejecutar la función async desde contexto síncrono
        asyncio.run(generate_tweet_screenshot(tweet_data, str(output_tweet_image_path)))
        
        print("Tweet image created.")

    def _create_ticket_background_image(self):
        print("Creating ticker background image...")
        ticker_width = 930
        ticker_height = 50
        asyncio.run(create_ticker_background_image(ticker_width, ticker_height, str(self.base_dir / "data" / "video_ticker" / "ticker_background.png")))
        print("Ticker background image created.")

    def _create_ticker_image(self):
        print("Creating ticker image...")

        production_plan_path = (
           self.base_dir / "data" / "create_production_plan" / "output" / "production_plan.json"
        )
        output_ticker_image_path = (
            self.base_dir / "data" / "video_ticker" / "ticker.png"
        )

        # Validar si existe el archivo JSON

        # Cargar JSON
        try:
            with open(production_plan_path, "r", encoding="utf-8") as f:
                production_plan_data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load JSON: {e}")
            return
        
        stocks_data = production_plan_data.get("ticker_stocks", [])

        asyncio.run(generate_bottom_ticker(
            stocks=stocks_data,
            output_path=str(output_ticker_image_path),
            width=20000,
            height=35
        ))
        print("Ticker image created.")

    def _create_final_video(self):
        """Create the final assembled video"""
        print("Creating final video...")

        font_path = str(
            self.base_dir / "data" / "fonts" / "Montserrat-Bold.ttf"
        )
        
        # =============================
        # 1. Configure Video Settings
        # =============================
        config = VideoConfig()
        
        # Customize settings (EDITABLE)
        # Video dimensions
        config.video_width = 1920
        config.video_height = 1080
        config.fps = 30
        
        # Background color (RGB)
        config.background_color = (255, 255, 255)  # White
        
        # Character pose position (left side)
        config.character_x = 1000        # X position (center of square)
        config.character_y = 400        # Y position (center of square)
        config.character_width = 700    # Width of character
        config.character_height = 700   # Height of character
        
        # Generated/Downloaded image position (right side)
        config.image_x = 1300          # X position (center of square)
        config.image_y = 400           # Y position (center of square)
        config.image_width = 700       # Width of image
        config.image_height = 700      # Height of image
        
        # Caption configuration
        config.caption_font = "Montserrat"      # Font name
        config.font_path = font_path  # Path to font file
        config.caption_fontsize = 48            # Font size
        config.caption_color = (95, 235, 69, 180)   # Caption text color
        config.caption_bg_color = (0, 0, 0, 180)  # Background (RGBA)
        config.caption_y = 720                  # Y position (below images)
        config.caption_max_width = 1600         # Max width for text wrap
        config.caption_stroke_color = "black"   # Outline color
        config.caption_stroke_width = 2         # Outline thickness
        
        # Ticker configuration
        config.ticker_height = 120               # Height of ticker bar
        config.ticker_y = 1020                  # Y position (near bottom)
        config.ticker_speed = 100               # Speed in pixels/second (EDITABLE)
        config.ticker_fade_start_percent = 20   # Fade starts at 20% from left (EDITABLE)
        
        # Transition effects
        config.image_fade_duration = 0.3        # Fade in/out duration
        config.pose_fade_duration = 0.3         # Fade in/out duration
        
        # =============================
        # 2. Define File Paths
        # =============================
        
        # Input files
        production_plan_path = str(
            self.base_dir / "data" / "create_production_plan" / "output" / "production_plan.json"
        )
        
        timestamps_path = str(
            self.base_dir / "data" / "video_audio" / "elevenlabs" / "timestamps.json"
        )
        
        narration_audio_path = str(
            self.base_dir / "data" / "video_audio" / "elevenlabs" / "narration.mp3"
        )
        
        # Optional background music
        background_music_path = str(
            self.base_dir / "data" / "music" / "background.mp3"
        )
        if not Path(background_music_path).exists():
            background_music_path = None
        
        # Ticker images
        ticker_image_path = str(
            self.base_dir / "data" / "video_ticker" / "ticker.png"
        )
        
        ticker_background_path = str(
            self.base_dir / "data" / "video_ticker" / "ticker_background.png"
        )
        
        # Character poses directory
        character_poses_dir = str(
            self.base_dir / "data" / "character_poses"
        )
        
        # Video images directory
        video_images_dir = str(
            self.base_dir / "data" / "video_images"
        )
        
        # Output video
        output_path = str(
            self.base_dir / "data" / "final_video" / "final_video.mp4"
        )
        
        # Create output directory if it doesn't exist
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        # =============================
        # 3. Validate Files
        # =============================
        required_files = [
            production_plan_path,
            timestamps_path,
            narration_audio_path,
            ticker_image_path,
            ticker_background_path
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                print(f"[ERROR] Required file not found: {file_path}")
                return
        
        if not Path(character_poses_dir).exists():
            print(f"[ERROR] Character poses directory not found: {character_poses_dir}")
            return
        
        if not Path(video_images_dir).exists():
            print(f"[ERROR] Video images directory not found: {video_images_dir}")
            return
        
        # =============================
        # 4. Assemble Video
        # =============================
        try:
            final_video_path = assemble_video(
                production_plan_path=production_plan_path,
                timestamps_path=timestamps_path,
                narration_audio_path=narration_audio_path,
                background_music_path=background_music_path,
                ticker_image_path=ticker_image_path,
                ticker_background_path=ticker_background_path,
                character_poses_dir=character_poses_dir,
                video_images_dir=video_images_dir,
                output_path=output_path,
                config=config
            )
            
            print(f"✅ Final video created successfully: {final_video_path}")
            
        except Exception as e:
            print(f"[ERROR] Failed to create video: {e}")
            import traceback
            traceback.print_exc()