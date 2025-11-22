from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import numpy as np

try:
    from moviepy import (
        ImageClip, 
        AudioFileClip, 
        CompositeVideoClip, 
        VideoClip,
        TextClip, 
        ColorClip,
        CompositeAudioClip
    )
    from moviepy.audio.fx import AudioLoop
    from PIL import Image, ImageDraw, ImageFont, ImageColor
except ImportError as e:
    print(f"Error importing libraries: {e}")
    print("Install with: pip install moviepy>=2.0.0.dev2 pillow numpy")


class VideoConfig:
    """Configuration class for video assembly parameters"""
    
    def __init__(self):

        # X (horizontal):
        # Menor valor ← → Mayor valor
        # IZQUIERDA       DERECHA

        # Y (vertical):
        # Menor valor ↑ ↓ Mayor valor
        # ARRIBA        ABAJO

        # Video dimensions
        self.video_width = 2560
        self.video_height = 1440
        self.fps = 30
        
        # Background
        self.background_color = (255, 255, 255)

        # --- TWEET IMAGE CONFIGURATION (Layer 2 - Foreground) ---
        self.tweet_width = 968     # 30% del ancho
        self.tweet_x = 700         # Centro del 30% izquierdo
        self.tweet_y = 720         # Puedes dejarlo o cambiarlo 
        self.tweet_padding = 100    # Padding entre tweet y bordes   

        # Generated/Downloaded image position (right side)
        self.image_width = 1024    # 70% del ancho
        self.image_x = 1800        # Centro del 70% derecho
        self.image_y = 620         # Puedes dejarlo o cambiarlo
        self.image_padding = 100    # Padding entre imagen y bordes
        
        # Captions configuration
        self.caption_font = "Montserrat ExtraBold"
        self.caption_font_path = Path("data/fonts/Montserrat-ExtraBold.ttf")
        self.caption_fontsize = 80
        self.caption_color = "black"
        self.caption_bg_color = None 
        self.caption_x = 1100
        self.caption_y = 1150
        self.caption_max_width = 1600
        self.caption_stroke_color = "#5eea45"
        self.caption_stroke_width = 5 

        # Caption box configuration
        self.caption_box_enabled = True           # Activar el cuadrado de fondo
        self.caption_box_color = "#5eea45"        # Color verde del cuadrado
        self.caption_box_padding_x = 20           # Padding horizontal (izq/der)
        self.caption_box_padding_y = 15           # Padding vertical (arriba/abajo)
        self.caption_box_opacity = 255            # Opacidad del fondo (0-255, 255=sólido)
        self.caption_box_border_radius = 10       # Radio de esquinas redondeadas (opcional)
        
        # --- PROFESSIONAL TICKER CONFIGURATION ---
        self.ticker_height = 140
        self.ticker_y = 1300
        self.ticker_speed = 150
        self.ticker_bg_color = (0, 0, 0) 
        
        # Branding (Logo a la izquierda)
        self.branding_text_1 = "X"
        self.branding_color_1 = "#00FF00" # Verde
        self.branding_text_2 = "Insight"
        self.branding_color_2 = "#FFFFFF" # Blanco
        self.branding_width = 220 
        
        self.ticker_fade_start_percent = 0 
        
        # Ticker Styling
        self.ticker_font_path = Path("data/fonts/Montserrat-ExtraBold.ttf")
        self.ticker_font_size = 50
        self.ticker_logo_font_size = 40
        self.ticker_text_font = "Montserrat ExtraBold"
        
        # Colors
        self.ticker_color_up = "#00FF00"      
        self.ticker_color_down = "#FF3333"    
        self.ticker_color_neutral = "#FFFFFF" 
        
        self.ticker_separator = "  |  "
        self.ticker_item_padding = 60

        # --- AUDIO CONFIGURATION ---
        self.narration_volume = 1.1    # Volumen de la narración (0.0-2.0)
        self.music_volume = 0.30       # Volumen de la música de fondo (0.0-1.0)


class VideoAssembler:
    """Main class for assembling the final video"""
    
    def __init__(self, config: Optional[VideoConfig] = None):
        self.config = config or VideoConfig()
    
    def create_video(
        self,
        synced_plan_path: str,
        timestamps_path: str,
        narration_audio_path: str,
        background_music_path: Optional[str],
        ticker_image_path: str, 
        ticker_background_path: str, 
        video_images_dir: str,
        output_path: str,
        tweet_image_path: Optional[str] = None, 
        manual_ticker_data: Optional[List[Dict]] = None 
    ) -> str:
        """Main function to create the video"""
        print("🎬 Starting video assembly...")
        
        # 1. Load Data
        synced_plan = self._load_json(synced_plan_path)
        original_timestamps = self._load_json(timestamps_path)
        ticker_data = manual_ticker_data or synced_plan.get("ticker_stocks", [])
        
        # Load audio
        narration_audio = AudioFileClip(narration_audio_path)
        video_duration = narration_audio.duration
        
        print(f"📊 Video duration: {video_duration:.2f} seconds")
        
        # 2. Create Layers
        
        # Layer 0: Background
        background = self._create_background(video_duration)
        
        # --- UPDATED: Passing video_duration to fix gaps ---
        segments_clips = self._create_segment_clips(
            synced_plan,
            video_images_dir,
            video_duration
        )
        
        # Layer 2: Tweet Image (Foreground - On top of Character feet)
        tweet_clip = None
        if tweet_image_path:
            print(f"🐦 Processing Tweet Image: {tweet_image_path}")
            tweet_clip = self._create_tweet_clip(tweet_image_path, video_duration)
        
        # Layer 3: Captions (Generated via PIL for quality)
        caption_clips = self._create_caption_clips_pil(original_timestamps, video_duration)
        
        # Layer 4: Ticker (With Branding)
        ticker_clips = self._create_ticker_animation(
            ticker_data,
            video_duration
        )
        
        # 3. Combine Clips (ORDER IS CRITICAL)
        all_clips = [background] + segments_clips
        
        if tweet_clip:
            all_clips.append(tweet_clip)
            
        all_clips = all_clips + caption_clips + ticker_clips
        
        final_video = CompositeVideoClip(
            all_clips, 
            size=(self.config.video_width, self.config.video_height)
        )

        # Add audio with volume control
        # Ajustar volumen de la narración
        narration_audio_adjusted = narration_audio.with_volume_scaled(self.config.narration_volume)
        
        # Add audio
        if background_music_path and Path(background_music_path).exists():
            # Ajustar volumen de la música
            music = AudioFileClip(background_music_path).with_volume_scaled(self.config.music_volume)
            if music.duration < video_duration:
                music = music.with_effects([AudioLoop(duration=video_duration)])
            else:
                music = music.with_duration(video_duration)
            final_audio = CompositeAudioClip([narration_audio_adjusted, music])
        else:
            final_audio = narration_audio_adjusted
        
        final_video = final_video.with_audio(final_audio)
        
        # Export
        print(f"💾 Exporting video to: {output_path}")
        final_video.write_videofile(
            output_path,
            fps=self.config.fps,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            threads=4
        )
        
        print("✅ Video assembly complete!")
        return output_path
    
    def _load_json(self, path: str) -> Dict:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_background(self, duration: float) -> ColorClip:
        return ColorClip(
            size=(self.config.video_width, self.config.video_height),
            color=self.config.background_color,
            duration=duration
        )
    
    def _create_tweet_clip(self, image_path: str, duration: float) -> Optional[ImageClip]:
        if not image_path or not Path(image_path).exists():
            return None
        try:
            img = Image.open(image_path)
            w_percent = (self.config.tweet_width / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            
            if img.mode == 'RGBA':
                img_resized = img.resize((self.config.tweet_width, h_size), Image.Resampling.LANCZOS)
            else:
                img_resized = img.convert('RGB').resize((self.config.tweet_width, h_size), Image.Resampling.LANCZOS)
            
            clip = ImageClip(np.array(img_resized))
            clip = clip.with_duration(duration)
            
            pos_x = self.config.tweet_x - (self.config.tweet_width // 2)
            pos_y = self.config.tweet_y - (h_size // 2)
            
            clip = clip.with_position((pos_x, pos_y))
            return clip
        except Exception as e:
            print(f"❌ Error creating tweet clip: {e}")
            return None

    # --- GAP FIX IMPLEMENTED HERE ---
    def _create_segment_clips(self, synced_plan: Dict, video_images_dir: str, total_video_duration: float) -> List[VideoClip]:
        """
        Creates visual segment clips.
        UPDATED LOGIC: Splits each segment into 3 progressive frames (Frame 1, 2, 3).
        Each frame gets 1/3 of the segment's total duration.
        """
        clips = []
        segments = synced_plan.get("segments", [])
        num_segments = len(segments)
        
        for i, segment in enumerate(segments):
            segment_id = segment.get("segment_id")
            start_time = segment.get("start", 0)
            
            # 1. Calculate the TOTAL duration of this segment
            if i < num_segments - 1:
                next_start = segments[i+1].get("start", 0)
                segment_duration = next_start - start_time
            else:
                # Last segment goes until the end of the video
                segment_duration = total_video_duration - start_time

            # Safety check
            if segment_duration <= 0: segment_duration = 0.1
            
            # 2. Calculate duration per FRAME (3 frames per segment)
            frame_duration = segment_duration / 3.0
            
            # 3. Loop through the 3 frames
            for frame_num in range(1, 4): # Iterates: 1, 2, 3
                
                # Construct the expected filename: segment_image_1_frame_1.png
                image_filename = f"segment_image_{segment_id}_frame_{frame_num}.png"
                img_path = Path(video_images_dir) / "generated_images" / image_filename
                
                # Calculate exact start time for THIS frame
                # Frame 1 starts at: start_time
                # Frame 2 starts at: start_time + frame_duration
                # Frame 3 starts at: start_time + (frame_duration * 2)
                current_frame_start = start_time + ((frame_num - 1) * frame_duration)

                if img_path.exists():
                    clips.append(self._create_image_clip(
                        str(img_path), 
                        current_frame_start, # Calculated start
                        frame_duration,      # Calculated duration
                        self.config.image_x, 
                        self.config.image_y,
                        self.config.image_width,
                    ))
                else:
                    print(f"⚠️ Missing frame image: {image_filename}")
                    # Optional: You could add logic here to reuse the previous frame if one is missing
                    
        return clips
    
    def _create_image_clip(self, image_path: str, start_time: float, duration: float, x: int, y: int, width: int) -> ImageClip:
        img = Image.open(image_path)
        # OPCIÓN B: Mantener proporción (como el tweet)
        w_percent = (width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        
        if img.mode == 'RGBA':
            img_resized = img.resize((width, h_size), Image.Resampling.LANCZOS)
        else:
            img_resized = img.convert('RGB').resize((width, h_size), Image.Resampling.LANCZOS)
        
        clip = ImageClip(np.array(img_resized))
        clip = clip.with_duration(duration).with_start(start_time).with_position((x - width // 2, y - h_size // 2))
        return clip

    # --- CAPTION GENERATOR (PIL) ---
    def _create_caption_clips_pil(self, timestamps: Dict, video_duration: float) -> List[VideoClip]:
        clips = []
        words = timestamps.get("words", [])
        
        try:
            font = ImageFont.truetype(str(self.config.caption_font_path), self.config.caption_fontsize)
        except:
            font = ImageFont.load_default()

        text_color = self.config.caption_color
        if isinstance(text_color, tuple):
            text_color = tuple(int(c) for c in text_color)
        
        stroke_color = self.config.caption_stroke_color
        stroke_width = self.config.caption_stroke_width
        
        pad_x = self.config.caption_box_padding_x 
        pad_y = self.config.caption_box_padding_y

        dummy_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

        for word_data in words:
            word = word_data.get("word", "")
            start = word_data.get("start", 0)
            end = word_data.get("end", 0)
            duration = end - start
            if duration <= 0: continue
            
            try:
                bbox = dummy_draw.textbbox((0, 0), word, font=font, stroke_width=stroke_width)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                
                img_w = text_w + (pad_x * 2)
                img_h = text_h + (pad_y * 2)
                
                # Calcular color del cuadrado de fondo
                if self.config.caption_box_enabled:
                    # Convertir color hex a RGB
                    box_color = ImageColor.getrgb(self.config.caption_box_color)
                    box_color_rgba = box_color + (self.config.caption_box_opacity,)
                    
                    # Crear imagen con fondo verde
                    img = Image.new("RGBA", (img_w, img_h), box_color_rgba)
                else:
                    # Crear imagen transparente (comportamiento original)
                    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))

                draw = ImageDraw.Draw(img)
                
                draw_x = pad_x - bbox[0]
                draw_y = pad_y - bbox[1]
                
                draw.text(
                    (draw_x, draw_y), 
                    word, 
                    font=font, 
                    fill=text_color,
                    # Opcional: quitar stroke si tienes fondo
                    # stroke_fill=stroke_color, 
                    # stroke_width=stroke_width
                )
                
                txt_clip = ImageClip(np.array(img))
                txt_clip = txt_clip.with_duration(duration).with_start(start)
                txt_clip = txt_clip.with_position((self.config.caption_x, self.config.caption_y))
                
                clips.append(txt_clip)
                
            except Exception as e:
                print(f"Error creating caption for '{word}': {e}")
                continue
                
        return clips

    # --- BRANDING BADGE GENERATOR ---
    def _create_branding_clip(self, duration: float) -> VideoClip:
        """Generates the XInsight Logo Badge"""
        scale = 3
        width = self.config.branding_width * scale
        height = self.config.ticker_height * scale
        font_size = int(self.config.ticker_logo_font_size * 1.3 * scale) 
        
        try:
            font = ImageFont.truetype(str(self.config.ticker_font_path), font_size)
        except:
            font = ImageFont.load_default()
            
        bg_color = self.config.ticker_bg_color + (255,) 
        img = Image.new("RGBA", (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        x_text = self.config.branding_text_1
        insight_text = self.config.branding_text_2
        
        x_width = draw.textlength(x_text, font=font)
        insight_width = draw.textlength(insight_text, font=font)
        
        total_text_width = x_width + insight_width
        start_x = (width - total_text_width) // 2
        
        ascent, descent = font.getmetrics()
        text_height = ascent + descent
        y_pos = (height - text_height) // 2
        
        draw.text((start_x, y_pos), x_text, font=font, fill=self.config.branding_color_1, anchor='lt')
        draw.text((start_x + x_width, y_pos), insight_text, font=font, fill=self.config.branding_color_2, anchor='lt')
        
        final_w = self.config.branding_width
        final_h = self.config.ticker_height
        img_resized = img.resize((final_w, final_h), resample=Image.Resampling.LANCZOS)
        
        clip = ImageClip(np.array(img_resized))
        clip = clip.with_duration(duration)
        clip = clip.with_position((0, self.config.ticker_y))
        
        return clip

    # --- TICKER GENERATOR ---
    def _generate_dynamic_ticker_strip(self, ticker_data: List[Dict]) -> VideoClip:
        scale_factor = 3 
        looped_data = ticker_data * 5
        
        font_path = str(self.config.ticker_font_path)
        scaled_font_size = self.config.ticker_font_size * scale_factor
        
        try:
            font = ImageFont.truetype(font_path, scaled_font_size)
        except:
            font = ImageFont.load_default()

        color_up = ImageColor.getrgb(self.config.ticker_color_up)
        color_down = ImageColor.getrgb(self.config.ticker_color_down)
        color_neutral = ImageColor.getrgb(self.config.ticker_color_neutral)
        
        padding = self.config.ticker_item_padding * scale_factor
        separator = self.config.ticker_separator
        
        total_width = 0
        draw_items = [] 
        dummy_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        
        for item in looped_data:
            symbol = item.get("symbol", "???")
            price = item.get("price", 0.0)
            change = item.get("change_percent", 0.0)
            
            arrow = "▲" if change >= 0 else "▼"
            change_color = color_up if change >= 0 else color_down
            
            sym_text = f"{symbol} "
            sym_w = int(dummy_draw.textlength(sym_text, font=font))
            
            price_text = f"${price:.2f} "
            price_w = int(dummy_draw.textlength(price_text, font=font))
            
            change_text = f"{arrow}{abs(change):.2f}%"
            change_w = int(dummy_draw.textlength(change_text, font=font))
            
            sep_text = separator
            sep_w = int(dummy_draw.textlength(sep_text, font=font))
            
            draw_items.append({
                "sym": sym_text, "sym_w": sym_w,
                "price": price_text, "price_w": price_w,
                "change": change_text, "change_w": change_w, "change_color": change_color,
                "sep": sep_text, "sep_w": sep_w
            })
            
            total_width += sym_w + price_w + change_w + sep_w + (padding * 2)
            
        scaled_height = self.config.ticker_height * scale_factor
        img = Image.new("RGBA", (total_width, scaled_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        current_x = 0
        ascent, descent = font.getmetrics()
        text_height = ascent + descent
        y_pos = (scaled_height - text_height) // 2
        
        t_stroke_w = 2 * scale_factor
        t_stroke_col = (0,0,0,150)
        
        for item in draw_items:
            draw.text((current_x, y_pos), item['sym'], font=font, fill=color_neutral, anchor='lt', stroke_width=t_stroke_w, stroke_fill=t_stroke_col)
            current_x += item['sym_w']
            draw.text((current_x, y_pos), item['price'], font=font, fill=color_neutral, anchor='lt', stroke_width=t_stroke_w, stroke_fill=t_stroke_col)
            current_x += item['price_w']
            draw.text((current_x, y_pos), item['change'], font=font, fill=item['change_color'], anchor='lt', stroke_width=t_stroke_w, stroke_fill=t_stroke_col)
            current_x += item['change_w'] + padding
            draw.text((current_x, y_pos), item['sep'], font=font, fill=color_neutral, anchor='lt')
            current_x += item['sep_w'] + padding
            
        final_width = int(total_width / scale_factor)
        final_height = self.config.ticker_height
        img_resized = img.resize((final_width, final_height), resample=Image.Resampling.LANCZOS)
        return ImageClip(np.array(img_resized))

    def _create_ticker_animation(self, ticker_data: List[Dict], video_duration: float) -> List[VideoClip]:
        clips = []
        
        # 1. Background (Black)
        ticker_bg_clip = ColorClip(
            size=(self.config.video_width, self.config.ticker_height),
            color=self.config.ticker_bg_color
        )
        ticker_bg_clip = ticker_bg_clip.with_duration(video_duration)
        ticker_bg_clip = ticker_bg_clip.with_position((0, self.config.ticker_y))
        clips.append(ticker_bg_clip)
        
        # 2. Scrolling Text
        ticker_content_clip = None
        if ticker_data and len(ticker_data) > 0:
            print(f"📈 Generando ticker profesional con {len(ticker_data)} acciones...")
            ticker_content_clip = self._generate_dynamic_ticker_strip(ticker_data)
            
        if ticker_content_clip:
            ticker_content_clip = ticker_content_clip.with_duration(video_duration)
            ticker_content_clip = ticker_content_clip.with_position(
                lambda t: (int(self.config.video_width - (t * self.config.ticker_speed)), 0)
            )
            
            mask_w = self.config.video_width
            mask_h = self.config.ticker_height
            
            fade_start_x = self.config.branding_width
            fade_width = 60 
            
            mask_array = np.ones((mask_h, mask_w), dtype=float)
            mask_array[:, :fade_start_x] = 0.0 
            
            for i in range(fade_width):
                if fade_start_x + i < mask_w:
                    mask_array[:, fade_start_x + i] = i / fade_width
            
            mask_clip = ImageClip(mask_array, is_mask=True).with_duration(video_duration)
            
            ticker_container = CompositeVideoClip(
                [ticker_content_clip], 
                size=(self.config.video_width, self.config.ticker_height)
            )
            ticker_container = ticker_container.with_mask(mask_clip)
            ticker_container = ticker_container.with_position((0, self.config.ticker_y))
            
            clips.append(ticker_container)
        
        # 3. Branding Badge (The "XInsight" Logo) - sits on top
        branding_clip = self._create_branding_clip(video_duration)
        clips.append(branding_clip)
            
        return clips


def assemble_video(
    manual_ticker_data: Optional[list],
    synced_plan_path: str,
    timestamps_path: str,
    narration_audio_path: str,
    background_music_path: Optional[str],
    ticker_image_path: str,
    ticker_background_path: str,
    video_images_dir: str,
    output_path: str,
    tweet_image_path: Optional[str] = None,
    config: Optional[VideoConfig] = None
) -> str:
    assembler = VideoAssembler(config)
    return assembler.create_video(
        manual_ticker_data=manual_ticker_data,
        synced_plan_path=synced_plan_path,
        timestamps_path=timestamps_path,
        narration_audio_path=narration_audio_path,
        background_music_path=background_music_path,
        ticker_image_path=ticker_image_path,
        ticker_background_path=ticker_background_path,
        video_images_dir=video_images_dir,
        output_path=output_path,
        tweet_image_path=tweet_image_path
    )