"""
FINAL VIDEO ASSEMBLER - Complete Video Production

Assembles the final YouTube Short video with ALL features:
- Background removal for character poses (transparent)
- Dynamic word-level captions with highlighting
- Scrolling bottom ticker
- Background music
- Studio background with XINSIDER branding
- Black bottom area for YouTube UI
"""

import json
import os
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips, CompositeAudioClip, TextClip
import numpy as np
from PIL import Image, ImageDraw, ImageFont

try:
    from rembg import remove
    REMBG_AVAILABLE = True
except ImportError:
    REMBG_AVAILABLE = False
    print("[WARNING] rembg not installed. Background removal will be skipped.")


class FinalVideoAssembler:
    """
    Assembles the final video from production plan with ALL features.
    """

    def __init__(
        self,
        output_dir: str = "output/financial_shorts",
        fps: int = 30,
        resolution: Tuple[int, int] = (1080, 1920)
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.fps = fps
        self.resolution = resolution
        self.width, self.height = resolution

    def load_production_plan(self, plan_path: str) -> Dict:
        """Load production plan JSON."""
        with open(plan_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def remove_background_from_pose(self, pose_path: str) -> np.ndarray:
        """
        Remove background from character pose using rembg.
        Returns RGBA numpy array with transparent background.
        """
        if not REMBG_AVAILABLE:
            # Fallback: return original image with alpha channel
            img = Image.open(pose_path).convert("RGBA")
            return np.array(img)

        try:
            # Read image
            with open(pose_path, 'rb') as f:
                input_data = f.read()

            # Remove background
            output_data = remove(input_data)

            # Convert to PIL Image
            img = Image.open(io.BytesIO(output_data)).convert("RGBA")

            # Convert to numpy array
            return np.array(img)
        except Exception as e:
            print(f"[WARNING] Could not remove background from {pose_path}: {str(e)}")
            # Fallback: return original image
            img = Image.open(pose_path).convert("RGBA")
            return np.array(img)

    def create_tweet_chart_alternator(self, tweet_path: str, chart_path: str, total_duration: float) -> ImageClip:
        """
        Crea alternancia entre tweet y gráfico de stock cada 30s con transición suave.

        Args:
            tweet_path: Path al screenshot del tweet
            chart_path: Path al gráfico de stock
            total_duration: Duración total del video

        Returns:
            VideoClip con alternancia entre tweet y gráfico
        """
        try:
            from moviepy import VideoClip

            # Cargar imágenes
            tweet_img = Image.open(tweet_path) if Path(tweet_path).exists() else None
            chart_img = Image.open(chart_path) if Path(chart_path).exists() else None

            if not tweet_img and not chart_img:
                print("[WARNING] No se encontraron ni tweet ni gráfico")
                return None

            # Redimensionar manteniendo aspect ratio
            # Tamaño máximo disponible (no forzar estas dimensiones)
            max_width = 1000
            max_height = 600

            tweet_array = None
            chart_array = None

            # IMPORTANTE: Redimensionar manteniendo aspect ratio, luego hacer padding
            # para que ambas imágenes tengan el mismo tamaño final

            def resize_with_padding(img, target_width, target_height, bg_color=(255, 255, 255)):
                """Resize manteniendo aspect ratio y agrega padding para alcanzar dimensiones exactas."""
                # Calcular escala para mantener aspect ratio
                img_width, img_height = img.size
                scale = min(target_width / img_width, target_height / img_height)

                # Nuevo tamaño manteniendo aspect ratio
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)

                # Redimensionar
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Crear imagen con padding (fondo blanco)
                padded_img = Image.new('RGB', (target_width, target_height), bg_color)

                # Centrar imagen redimensionada
                offset_x = (target_width - new_width) // 2
                offset_y = (target_height - new_height) // 2
                padded_img.paste(img_resized, (offset_x, offset_y))

                return padded_img, new_width, new_height

            if tweet_img:
                # Redimensionar tweet manteniendo aspect ratio
                img_width, img_height = tweet_img.size
                print(f"[DEBUG] Tweet original size: {img_width}x{img_height}")
                tweet_img_padded, resized_w, resized_h = resize_with_padding(tweet_img, max_width, max_height)
                print(f"[DEBUG] Tweet resized to: {resized_w}x{resized_h}, padded to: {max_width}x{max_height}")
                tweet_array = np.array(tweet_img_padded)

            if chart_img:
                # Redimensionar gráfico manteniendo aspect ratio
                img_width, img_height = chart_img.size
                print(f"[DEBUG] Chart original size: {img_width}x{img_height}")
                chart_img_padded, resized_w, resized_h = resize_with_padding(chart_img, max_width, max_height)
                print(f"[DEBUG] Chart resized to: {resized_w}x{resized_h}, padded to: {max_width}x{max_height}")
                chart_array = np.array(chart_img_padded)

            # Usar tweet si no hay gráfico y viceversa
            if tweet_array is None:
                tweet_array = chart_array
            if chart_array is None:
                chart_array = tweet_array

            # Verificar que ambos arrays tienen el mismo tamaño
            print(f"[DEBUG] Final array shapes - Tweet: {tweet_array.shape}, Chart: {chart_array.shape}")

            def make_frame(t):
                """
                Genera frame en tiempo t.
                Alterna cada 30s entre tweet (20-30s) y gráfico (30s).
                """
                # Determinar ciclo actual (60s total: 30s tweet + 30s gráfico)
                cycle_time = t % 60
                transition_duration = 1.0  # 1 segundo de transición

                # Tweet: 0-30s, Gráfico: 30-60s
                if cycle_time < 30:
                    # Mostrar tweet
                    if cycle_time < transition_duration:
                        # Fade in desde gráfico
                        alpha = cycle_time / transition_duration
                        frame = (chart_array * (1 - alpha) + tweet_array * alpha).astype(np.uint8)
                    else:
                        frame = tweet_array
                else:
                    # Mostrar gráfico
                    local_time = cycle_time - 30
                    if local_time < transition_duration:
                        # Fade in desde tweet
                        alpha = local_time / transition_duration
                        frame = (tweet_array * (1 - alpha) + chart_array * alpha).astype(np.uint8)
                    else:
                        frame = chart_array

                return frame

            # Crear clip con animación
            print(f"[DEBUG] Creating VideoClip with duration={total_duration:.2f}s, fps={self.fps}")
            clip = VideoClip(make_frame, duration=total_duration)
            clip = clip.with_fps(self.fps)

            # Verificar que el clip se creó correctamente
            print(f"[DEBUG] VideoClip created:")
            print(f"[DEBUG]   - Duration: {clip.duration:.2f}s")
            print(f"[DEBUG]   - FPS: {clip.fps}")
            print(f"[OK] Creada alternancia tweet/gráfico para {total_duration:.2f}s")
            return clip

        except Exception as e:
            print(f"[ERROR] No se pudo crear alternancia tweet/gráfico: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def create_scrolling_ticker(self, ticker_path: str, duration: float, scroll_speed: int = 100) -> ImageClip:
        """
        Create a SEAMLESS INFINITE scrolling ticker that loops perfectly.

        SIMPLIFIED: Since ticker is now 3x wider (18x screen width), we only need
        one instance that scrolls left. Starts visible on left side.

        Args:
            ticker_path: Path to ticker image
            duration: Duration of the clip (total video duration)
            scroll_speed: Pixels per second to scroll

        Returns:
            VideoClip with seamless infinite scrolling animation
        """
        try:
            from moviepy import VideoClip

            # Load ticker image
            ticker_img = Image.open(ticker_path)
            ticker_width = ticker_img.width
            ticker_height = ticker_img.height

            # Convert to RGB numpy array once (performance)
            ticker_array = np.array(ticker_img.convert('RGB'))

            print(f"[DEBUG] Ticker dimensions: {ticker_width}x{ticker_height}px")
            print(f"[DEBUG] Scroll speed: {scroll_speed}px/s")
            print(f"[DEBUG] Video duration: {duration:.2f}s")
            print(f"[DEBUG] Total scroll distance: {scroll_speed * duration}px")

            def make_frame(t):
                """
                Generate frame at time t.
                Simplified: single ticker scrolling left, starts visible.
                """
                # Calculate how many pixels we've scrolled (starts at 0, so ticker is visible immediately)
                pixels_scrolled = int(scroll_speed * t)

                # Use modulo to create infinite loop
                offset = pixels_scrolled % ticker_width

                # Create blank frame
                frame = np.zeros((ticker_height, self.width, 3), dtype=np.uint8)

                # SINGLE IMAGE: Start at left edge (x=0), scroll left
                # Position: move left as time progresses
                x_pos = -offset  # Starts at 0, moves left

                # Draw visible portion of ticker
                if x_pos < self.width and x_pos + ticker_width > 0:
                    # Calculate visible portion
                    src_start = max(0, -x_pos)
                    src_end = min(ticker_width, self.width - x_pos)
                    dst_start = max(0, x_pos)
                    dst_end = min(self.width, x_pos + ticker_width)

                    if dst_end > dst_start and src_end > src_start:
                        frame[:, dst_start:dst_end] = ticker_array[:, src_start:src_end]

                return frame

            # Create clip with animation
            clip = VideoClip(make_frame, duration=duration)
            clip = clip.with_fps(self.fps)

            print(f"[OK] Created seamless infinite scrolling ticker for {duration:.2f}s")

            return clip

        except Exception as e:
            print(f"[ERROR] Could not create scrolling ticker: {str(e)}")
            import traceback
            traceback.print_exc()

            # Fallback: static ticker (better than nothing)
            print("[WARNING] Using static ticker as fallback")
            return ImageClip(ticker_path).with_duration(duration)

    def create_word_by_word_captions(self, all_words: List[Dict], total_duration: float) -> List:
        """
        Create word-by-word captions that show ONE word at a time.
        OPTIMIZED: Pre-load font once, cache rendered text images.

        Args:
            all_words: All words from all scenes with absolute timestamps
            total_duration: Total video duration

        Returns:
            List of ImageClip objects for each word
        """
        caption_clips = []

        font_size = 144  # DUPLICADO: era 72, ahora 144 para mayor visibilidad
        position_y = 680  # CENTRADO en área blanca: entre ilustraciones (~850px) y tweet (~1120px)

        # Try to load a bold font, fallback to default (LOAD ONCE)
        try:
            # Try common Windows fonts in order of preference
            font_paths = [
                "C:/Windows/Fonts/impact.ttf",      # Impact
                "C:/Windows/Fonts/arialbd.ttf",     # Arial Bold
                "C:/Windows/Fonts/comic.ttf",       # Comic Sans (bold effect)
                "C:/Windows/Fonts/calibrib.ttf",    # Calibri Bold
            ]
            font = None
            for font_path in font_paths:
                if Path(font_path).exists():
                    font = ImageFont.truetype(font_path, font_size)
                    print(f"[OK] Using font: {font_path}")
                    break

            if font is None:
                # Fallback to default font
                font = ImageFont.load_default()
                print("[WARNING] Using default font - no bold fonts found")
        except Exception as e:
            font = ImageFont.load_default()
            print(f"[WARNING] Could not load font, using default: {str(e)}")

        # OPTIMIZATION: Batch process captions (faster than one-by-one)
        print(f"[INFO] Rendering {len(all_words)} caption images...")

        for i, word_data in enumerate(all_words):
            word = word_data['word']
            word_start = word_data['start']
            word_end = word_data['end']

            try:
                # Create text image using PIL
                # Get text size (use dummy for bbox)
                dummy_img = Image.new('RGBA', (1, 1))
                draw = ImageDraw.Draw(dummy_img)
                bbox = draw.textbbox((0, 0), word, font=font)

                # FIX: bbox puede tener offsets negativos para descendentes (g, y, p, q)
                # bbox = (left, top, right, bottom)
                bbox_left = bbox[0]
                bbox_top = bbox[1]
                bbox_right = bbox[2]
                bbox_bottom = bbox[3]

                text_width = bbox_right - bbox_left
                text_height = bbox_bottom - bbox_top

                # Add padding
                padding = 20
                img_width = text_width + 2 * padding
                img_height = text_height + 2 * padding

                # Create image with transparent background
                img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)

                # Draw text in black
                # IMPORTANTE: Ajustar posición Y para incluir descendentes
                # Si bbox_top es negativo, necesitamos offset adicional
                text_x = padding - bbox_left
                text_y = padding - bbox_top
                draw.text((text_x, text_y), word, font=font, fill=(0, 0, 0, 255))

                # Convert to numpy array (cached in memory)
                img_array = np.array(img)

                # Create ImageClip from array
                word_clip = ImageClip(img_array)
                word_clip = word_clip.with_duration(word_end - word_start)
                word_clip = word_clip.with_start(word_start)
                word_clip = word_clip.with_position(('center', position_y))

                caption_clips.append(word_clip)

                # Progress indicator every 50 words
                if (i + 1) % 50 == 0:
                    print(f"[PROGRESS] Rendered {i+1}/{len(all_words)} captions...")

            except Exception as e:
                print(f"[WARNING] Could not create caption for '{word}': {str(e)}")

        print(f"[OK] All {len(caption_clips)} captions rendered")
        return caption_clips

    def create_scene_clip(self, scene: Dict, scene_index: int, cached_images: Dict = None) -> ImageClip:
        """
        Create a scene clip with NUEVO LAYOUT VERTICAL.
        OPTIMIZED: Uses cached pre-loaded images to avoid repeated file I/O.

        Layout (NUEVO):
        - Background (studio)
        - ARRIBA: Ilustraciones (first, second, third) - secuencia normal
        - CENTRO: Captions (duplicados de tamaño, centrados en área blanca)
        - MEDIO: Tweet/Gráfico alternando (entre captions y ticker, aspect ratio preservado)
        - ABAJO: Bottom ticker (justo encima del área negra)

        Spacing (actualizado):
        - Top: 0-50px (padding superior)
        - Ilustraciones: 50-750px (700px height máximo, con 50px padding arriba)
        - Captions: 780px (centrado en área blanca, renderizado al frente)
        - Tweet/Gráfico: 900-1500px (600px height máximo, aspect ratio preservado con padding)
        - Ticker: 1520-1640px (120px height, justo encima del área negra)
        - Bottom: 1640-1920px (280px área negra para UI de YouTube)

        Layer Order (front to back):
        1. Captions (TOP - always visible)
        2. Ticker
        3. Tweet/Chart alternator
        4. Illustrations
        5. Background (BOTTOM)

        Args:
            scene: Scene configuration
            scene_index: Scene index number
            cached_images: Dictionary of pre-loaded images {filepath: numpy_array}
        """
        duration = scene.get("duration", 5)
        visuals = scene.get("visuals", {})

        if cached_images is None:
            cached_images = {}

        clips = []

        # Image dimensions and positioning
        # Ilustraciones arriba: más grandes verticalmente, 50px padding top
        max_illustration_width = 1080
        max_illustration_height = 700  # Aumentado de 600 a 700px
        illustration_y_position = 50  # Padding top de 50px

        # Layer 1: Studio background
        bg_file = visuals.get("background", "")
        if bg_file and Path(bg_file).exists():
            try:
                if bg_file in cached_images:
                    bg_array = cached_images[bg_file]
                else:
                    bg_img = Image.open(bg_file)
                    if bg_img.size != (self.width, self.height):
                        bg_img = bg_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                    bg_array = np.array(bg_img.convert('RGB'))
                    cached_images[bg_file] = bg_array

                bg_clip = ImageClip(bg_array).with_duration(duration)
                clips.append(bg_clip)
            except Exception as e:
                print(f"[ERROR] Could not load studio background: {str(e)}")
                white_bg = np.full((self.height, self.width, 3), 255, dtype=np.uint8)
                bg_clip = ImageClip(white_bg).with_duration(duration)
                clips.append(bg_clip)
        else:
            white_bg = np.full((self.height, self.width, 3), 255, dtype=np.uint8)
            bg_clip = ImageClip(white_bg).with_duration(duration)
            clips.append(bg_clip)

        # Layer 2: ILUSTRACIÓN ARRIBA (secuencia first, second, third)
        # IMPORTANTE: Filtrar tweets - solo mostrar ilustraciones aquí
        main_content = visuals.get("main_content", {})
        if main_content:
            content_file = main_content.get("file", "")
            content_type = main_content.get("type", "illustration")

            # FILTRO: Skip si es tweet o chart (esos van en la capa global abajo)
            if content_type in ["tweet", "chart", "stock_chart"]:
                print(f"[INFO] Skipping {content_type} in top area - will render in bottom layer")
            elif content_file and Path(content_file).exists():
                try:
                    # Use cached illustration image
                    cache_key = f"{content_file}_illustration_top"
                    if cache_key in cached_images:
                        content_array = cached_images[cache_key]
                        content_clip = ImageClip(content_array).with_duration(duration)
                    else:
                        # Load and resize to fit top illustration area
                        content_img = Image.open(content_file)
                        img_width, img_height = content_img.size

                        # Calculate scale to fit in illustration dimensions
                        scale = min(max_illustration_width / img_width, max_illustration_height / img_height)
                        new_width = int(img_width * scale)
                        new_height = int(img_height * scale)

                        content_img = content_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                        content_array = np.array(content_img.convert('RGB'))
                        cached_images[cache_key] = content_array
                        content_clip = ImageClip(content_array).with_duration(duration)

                    # Center horizontally, position at top
                    content_clip = content_clip.with_position(('center', illustration_y_position))
                    clips.append(content_clip)
                    print(f"[OK] Added top illustration for scene {scene_index + 1}")
                except Exception as e:
                    print(f"[WARNING] Could not load illustration: {str(e)}")
                else:
                    print(f"[WARNING] Illustration file not found: {content_file}")

        # Composite all layers
        if clips:
            scene_clip = CompositeVideoClip(clips, size=self.resolution)
            scene_clip = scene_clip.with_duration(duration)
            scene_clip = scene_clip.with_fps(self.fps)
            return scene_clip
        else:
            # Return blank clip
            blank = np.full((self.height, self.width, 3), 255, dtype=np.uint8)
            return ImageClip(blank).with_duration(duration).with_fps(self.fps)

    def assemble_video(self, production_plan: Dict) -> str:
        """
        Assemble the complete video from production plan.

        Returns:
            Path to final video file
        """
        print(f"\n{'='*60}")
        print(f"VIDEO ASSEMBLY (COMPLETE VERSION)")
        print(f"{'='*60}")

        scenes = production_plan.get("scenes", [])
        audio_config = production_plan.get("audio", {})

        print(f"\n[INFO] Assembling {len(scenes)} scenes...")

        # OPTIMIZATION: Pre-load and cache all images (avoid repeated file I/O)
        print("[INFO] Pre-loading images into cache...")
        image_cache = {}

        # Pre-cache background (used in all scenes)
        bg_file = scenes[0].get('visuals', {}).get('background', '') if scenes else ""
        if bg_file and Path(bg_file).exists():
            try:
                bg_img = Image.open(bg_file)
                if bg_img.size != (self.width, self.height):
                    bg_img = bg_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                image_cache[bg_file] = np.array(bg_img.convert('RGB'))
                print("[OK] Cached studio background")
            except Exception as e:
                print(f"[WARNING] Could not cache background: {str(e)}")

        # Pre-cache all illustration images (top area)
        # Aumentadas para usar más espacio vertical: 1080x700
        max_illustration_width = 1080
        max_illustration_height = 700
        unique_files = set()
        for scene in scenes:
            main_content = scene.get('visuals', {}).get('main_content', {})
            if main_content:
                content_file = main_content.get('file', '')
                content_type = main_content.get('type', 'illustration')
                # Solo cachear ilustraciones, no tweets ni charts
                if content_file and Path(content_file).exists() and content_type not in ["tweet", "chart", "stock_chart"]:
                    unique_files.add(content_file)

        for content_file in unique_files:
            try:
                cache_key = f"{content_file}_illustration_top"
                content_img = Image.open(content_file)
                img_width, img_height = content_img.size

                # Calculate scale to fit in top illustration area
                scale = min(max_illustration_width / img_width, max_illustration_height / img_height)
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)

                content_img = content_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                image_cache[cache_key] = np.array(content_img.convert('RGB'))
            except Exception as e:
                print(f"[WARNING] Could not cache {content_file}: {str(e)}")

        print(f"[OK] Cached {len(image_cache)} illustration images")

        # Create scene clips (only visual layers) using cached images
        scene_clips = []
        for i, scene in enumerate(scenes):
            print(f"\n[{i+1}/{len(scenes)}] Creating scene {scene.get('scene_number', i+1)}...")
            try:
                clip = self.create_scene_clip(scene, i, image_cache)
                scene_clips.append(clip)
            except Exception as e:
                print(f"[ERROR] Failed to create scene {i+1}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue

        if not scene_clips:
            print("[ERROR] No scenes created")
            return None

        # Collect all words from all scenes (with absolute timestamps)
        print("\n[INFO] Collecting all words for captions...")
        all_words = []
        for scene in scenes:
            captions_config = scene.get("captions", {})
            if captions_config.get("enabled", False):
                words = captions_config.get("words", [])
                all_words.extend(words)
        print(f"[OK] Collected {len(all_words)} words")

        # Calculate total duration from captions
        if all_words:
            last_word_end = max(word['end'] for word in all_words)
            total_duration = last_word_end + 1.0  # Add 1s buffer
            print(f"[INFO] Last caption ends at: {last_word_end:.2f}s")
            print(f"[INFO] Target total duration: {total_duration:.2f}s")
        else:
            total_duration = sum(clip.duration for clip in scene_clips)
            print(f"[INFO] Using scenes duration: {total_duration:.2f}s")

        # NUEVA ESTRATEGIA: Crear UNA SOLA escena continua con ilustraciones cambiantes
        # En lugar de concatenar escenas, creamos clips individuales para cada ilustración
        # y los componemos en una sola línea de tiempo
        print("\n[INFO] Creating continuous base video with timed illustrations...")

        # Create studio background for entire duration
        bg_file = scenes[0].get('visuals', {}).get('background', '') if scenes else ''
        if bg_file and Path(bg_file).exists():
            bg_array = image_cache.get(bg_file)
            if bg_array is None:
                bg_img = Image.open(bg_file)
                if bg_img.size != (self.width, self.height):
                    bg_img = bg_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                bg_array = np.array(bg_img.convert('RGB'))
            base_bg_clip = ImageClip(bg_array).with_duration(total_duration)
        else:
            white_bg = np.full((self.height, self.width, 3), 255, dtype=np.uint8)
            base_bg_clip = ImageClip(white_bg).with_duration(total_duration)

        # Create illustration clips with start times and durations
        illustration_clips = []
        current_time = 0
        for i, scene in enumerate(scenes):
            scene_duration = scene.get("duration", 5)
            main_content = scene.get('visuals', {}).get('main_content', {})

            if main_content:
                content_file = main_content.get("file", "")
                content_type = main_content.get("type", "illustration")

                if content_type not in ["tweet", "chart", "stock_chart"] and content_file and Path(content_file).exists():
                    cache_key = f"{content_file}_illustration_top"
                    if cache_key in image_cache:
                        content_array = image_cache[cache_key]

                        # Calculate remaining duration for last illustration
                        if i == len(scenes) - 1:
                            # Last illustration extends to end
                            illustration_duration = total_duration - current_time
                        else:
                            illustration_duration = scene_duration

                        illustration_clip = ImageClip(content_array).with_duration(illustration_duration)
                        illustration_clip = illustration_clip.with_start(current_time)
                        illustration_clip = illustration_clip.with_position(('center', 50))
                        illustration_clips.append(illustration_clip)
                        print(f"[OK] Illustration {i+1}: {current_time:.2f}s - {current_time + illustration_duration:.2f}s")

            current_time += scene_duration

        # Composite background + all illustrations
        base_clips = [base_bg_clip] + illustration_clips
        base_video = CompositeVideoClip(base_clips, size=self.resolution)
        base_video = base_video.with_duration(total_duration)
        base_video = base_video.with_fps(self.fps)
        print(f"[OK] Base video created: {base_video.duration:.2f}s with {len(illustration_clips)} illustrations")

        # Create tweet/chart alternator (middle area, between captions and ticker)
        print("\n[INFO] Creating tweet/chart alternator...")
        tweet_file = "output/tweet_screenshots/selected_tweet.png"
        chart_file = "output/stock_charts/tsla_chart.png"
        tweet_chart_clip = None

        # DEBUG: Verificar archivos
        print(f"[DEBUG] Tweet file exists: {Path(tweet_file).exists()} - {tweet_file}")
        print(f"[DEBUG] Chart file exists: {Path(chart_file).exists()} - {chart_file}")

        if Path(tweet_file).exists() or Path(chart_file).exists():
            try:
                print(f"[DEBUG] Calling create_tweet_chart_alternator with duration={total_duration:.2f}s")
                tweet_chart_clip = self.create_tweet_chart_alternator(tweet_file, chart_file, total_duration)

                if tweet_chart_clip:
                    # Posición: 900px (entre captions en 780 y ticker en 1520)
                    tweet_chart_clip = tweet_chart_clip.with_position(('center', 900))
                    print("[DEBUG] Tweet/chart clip created successfully:")
                    print(f"[DEBUG]   - Duration: {tweet_chart_clip.duration:.2f}s")
                    print(f"[DEBUG]   - FPS: {tweet_chart_clip.fps}")
                    print(f"[DEBUG]   - Size: {tweet_chart_clip.size if hasattr(tweet_chart_clip, 'size') else 'N/A'}")
                    print("[DEBUG]   - Position: center, 1120px")
                    print("[OK] Created tweet/chart alternator")
                else:
                    print("[WARNING] create_tweet_chart_alternator returned None")
            except Exception as e:
                print(f"[ERROR] Could not create tweet/chart alternator: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print("[WARNING] Neither tweet nor chart file found")

        # Create ONE continuous scrolling ticker for entire video
        print("\n[INFO] Creating continuous scrolling ticker...")
        ticker_file = "output/financial_shorts/ticker_strip.png"
        if Path(ticker_file).exists():
            try:
                ticker_clip = self.create_scrolling_ticker(ticker_file, total_duration, scroll_speed=100)
                # NUEVA POSICIÓN: 1520px (justo encima del área negra que empieza en 1640)
                ticker_clip = ticker_clip.with_position((0, 1520))

                # Validation: Verify ticker duration matches video duration
                print(f"[VALIDATION] Ticker clip duration: {ticker_clip.duration:.2f}s")
                print(f"[VALIDATION] Video duration: {total_duration:.2f}s")
                print(f"[VALIDATION] Ticker FPS: {ticker_clip.fps}")

                if abs(ticker_clip.duration - total_duration) > 0.1:
                    print(f"[WARNING] Ticker duration mismatch! Expected {total_duration:.2f}s, got {ticker_clip.duration:.2f}s")
                else:
                    print(f"[OK] Ticker duration validation PASSED ✓")

                print(f"[OK] Created continuous ticker for {total_duration:.2f} seconds")
            except Exception as e:
                print(f"[WARNING] Could not create ticker: {str(e)}")
                ticker_clip = None
        else:
            print(f"[WARNING] Ticker file not found: {ticker_file}")
            ticker_clip = None

        # Create word-by-word captions
        print("\n[INFO] Creating word-by-word captions...")
        caption_clips = self.create_word_by_word_captions(all_words, total_duration)
        print(f"[OK] Created {len(caption_clips)} caption clips")

        # Composite everything: base video + tweet/chart + ticker + captions
        # IMPORTANTE: Los captions deben ir AL FINAL para renderizarse ARRIBA de todo
        print("\n[INFO] Compositing all layers...")
        final_layers = [base_video]

        # Layer 2: Tweet/Chart (si existe)
        if tweet_chart_clip:
            final_layers.append(tweet_chart_clip)

        # Layer 3: Ticker (si existe)
        if ticker_clip:
            final_layers.append(ticker_clip)

        # Layer 4 (TOP): Captions - SIEMPRE AL FINAL para estar arriba de todo
        if caption_clips:
            final_layers.extend(caption_clips)

        final_video = CompositeVideoClip(final_layers, size=self.resolution)
        final_video = final_video.with_duration(total_duration)
        final_video = final_video.with_fps(self.fps)

        # Add audio (narration + music)
        print("\n[INFO] Adding audio...")
        narration_config = audio_config.get("narration", {})
        music_config = audio_config.get("music", {})

        audio_clips = []
        audio_readers = []  # Track audio readers for cleanup

        # Add narration
        narration_file = narration_config.get("file", "")
        if narration_file and Path(narration_file).exists():
            try:
                narration_audio = AudioFileClip(narration_file)
                narration_volume = narration_config.get("volume", 1.0)
                if narration_volume != 1.0:
                    narration_audio = narration_audio.with_volume_scaled(narration_volume)
                audio_clips.append(narration_audio)
                print(f"[OK] Added narration: {narration_file}")
            except Exception as e:
                print(f"[WARNING] Could not load narration: {str(e)}")

        # Add background music
        music_file = music_config.get("file", "")
        if music_file and Path(music_file).exists():
            try:
                music_audio = AudioFileClip(music_file)
                music_volume = music_config.get("volume", 0.22)
                if music_volume != 1.0:
                    music_audio = music_audio.with_volume_scaled(music_volume)

                # Loop music if needed
                if music_config.get("loop", True) and music_audio.duration < final_video.duration:
                    loops_needed = int(final_video.duration / music_audio.duration) + 1
                    music_clips = [music_audio] * loops_needed
                    from moviepy import concatenate_audioclips
                    music_audio = concatenate_audioclips(music_clips)

                # Trim to match video duration
                music_audio = music_audio.subclipped(0, min(music_audio.duration, final_video.duration))
                audio_clips.append(music_audio)
                print(f"[OK] Added background music: {music_file}")
            except Exception as e:
                print(f"[WARNING] Could not load music: {str(e)}")

        # Composite audio
        if audio_clips:
            try:
                final_audio = CompositeAudioClip(audio_clips)
                final_video = final_video.with_audio(final_audio)
            except Exception as e:
                print(f"[WARNING] Could not composite audio: {str(e)}")

        # Export final video
        output_filename = "final_short.mp4"
        output_path = self.output_dir / output_filename

        print(f"\n[INFO] Exporting final video...")
        print(f"[INFO] Output: {output_path}")
        print(f"[INFO] Resolution: {self.width}x{self.height}")
        print(f"[INFO] FPS: {self.fps}")
        print(f"[INFO] Duration: {final_video.duration:.2f} seconds")

        # OPTIMIZED FOR NVIDIA GPU (RTX 3060 Ti)
        # Using h264_nvenc for GPU-accelerated encoding (~10x faster than CPU)
        print("[INFO] Using NVIDIA GPU acceleration (h264_nvenc)...")

        try:
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='h264_nvenc',           # NVIDIA GPU encoding
                audio_codec='aac',
                preset='p4',                   # NVENC preset: p1 (fastest) to p7 (slowest), p4 = balanced
                bitrate='8000k',
                threads=8,                     # More threads for parallel processing
                ffmpeg_params=[
                    '-rc', 'vbr',              # Variable bitrate (better quality/speed)
                    '-cq', '23',               # Constant quality (23 = high quality)
                    '-b:v', '8000k',           # Target bitrate
                    '-maxrate', '12000k',      # Max bitrate
                    '-bufsize', '16000k',      # Buffer size
                    '-gpu', '0',               # Use first GPU
                    '-rc-lookahead', '20',     # Lookahead frames for better quality
                ]
            )
            print(f"\n[OK] Video exported with GPU acceleration: {output_path}")
        except Exception as e:
            # Fallback to CPU encoding if GPU fails
            print(f"[WARNING] GPU encoding failed: {str(e)}")
            print("[INFO] Falling back to CPU encoding (libx264)...")
            final_video.write_videofile(
                str(output_path),
                fps=self.fps,
                codec='libx264',              # CPU fallback
                audio_codec='aac',
                preset='veryfast',            # Fast CPU preset
                bitrate='8000k',
                threads=8
            )
            print(f"\n[OK] Video exported with CPU: {output_path}")

        return str(output_path)

    def assemble_from_plan_file(self, plan_path: str) -> str:
        """
        Complete workflow: load plan and assemble video.

        Args:
            plan_path: Path to production_plan.json

        Returns:
            Path to final video file
        """
        print("\n[1/2] Loading production plan...")
        plan = self.load_production_plan(plan_path)

        print("\n[2/2] Assembling video...")
        video_path = self.assemble_video(plan)

        print(f"\n{'='*60}")
        print(f"VIDEO ASSEMBLY COMPLETE")
        print(f"{'='*60}")
        print(f"Final video: {video_path}")

        return video_path


# Test/demo code
if __name__ == "__main__":
    assembler = FinalVideoAssembler()
    video_path = assembler.assemble_from_plan_file(
        plan_path="output/financial_shorts/production_plan.json"
    )
    print(f"\n✅ Final video created: {video_path}")
