from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional
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
    # Import effects as Effect objects for v2
    from moviepy.video.fx import FadeIn, FadeOut
    from PIL import Image
except ImportError as e:
    print(f"Error importing libraries: {e}")
    print("Install with: pip install moviepy pillow numpy")


class VideoConfig:
    """Configuration class for video assembly parameters"""
    
    def __init__(self):
        # Video dimensions
        self.video_width = 1920
        self.video_height = 1080
        self.fps = 30
        
        # Background
        self.background_color = (255, 255, 255)  # White
        
        # Character pose position (left side)
        self.character_x = 1000  # Left square center X
        self.character_y = 400  # Center Y
        self.character_width = 700
        self.character_height = 700
        
        # Generated/Downloaded image position (right side)
        self.image_x = 1300  # Right square center X
        self.image_y = 400
        self.image_width = 700
        self.image_height = 700
        
        # Captions configuration
        self.caption_font = "Montserrat"
        self.caption_font_path = Path("data/fonts/Montserrat-BoldItalic.ttf")
        self.caption_fontsize = 48
        self.caption_color = "white"
        self.caption_bg_color = (0, 0, 0, 180)  # Semi-transparent black
        self.caption_y = 720  # Below the images
        self.caption_max_width = 1600
        self.caption_stroke_color = "black"
        self.caption_stroke_width = 2
        
        # Bottom ticker configuration
        self.ticker_height = 60
        self.ticker_y = 1020  # Bottom of screen
        self.ticker_speed = 100  # pixels per second (CONFIGURABLE)
        self.ticker_fade_start_percent = 20  # Start fading at 20% from left (CONFIGURABLE)
        
        # Ticker background (channel name)
        self.ticker_bg_x = 0
        self.ticker_bg_y = self.ticker_y
        
        # Transitions
        self.image_fade_duration = 0.3
        self.pose_fade_duration = 0.3


class VideoAssembler:
    """Main class for assembling the final video"""
    
    def __init__(self, config: Optional[VideoConfig] = None):
        self.config = config or VideoConfig()
    
    def create_video(
        self,
        production_plan_path: str,
        timestamps_path: str,
        narration_audio_path: str,
        background_music_path: Optional[str],
        ticker_image_path: str,
        ticker_background_path: str,
        character_poses_dir: str,
        video_images_dir: str,
        output_path: str
    ) -> str:
        """
        Main function to create the video
        
        Args:
            production_plan_path: Path to production_plan.json
            timestamps_path: Path to timestamps.json
            narration_audio_path: Path to narration.mp3
            background_music_path: Path to background music (optional)
            ticker_image_path: Path to ticker stocks image
            ticker_background_path: Path to ticker background with channel name
            character_poses_dir: Directory containing character pose images
            video_images_dir: Directory containing generated/downloaded images
            output_path: Output video path
            
        Returns:
            Path to the created video
        """
        print("🎬 Starting video assembly...")
        
        # Load data
        production_plan = self._load_json(production_plan_path)
        timestamps = self._load_json(timestamps_path)
        
        # Load audio
        narration_audio = AudioFileClip(narration_audio_path)
        video_duration = narration_audio.duration
        
        print(f"📊 Video duration: {video_duration:.2f} seconds")
        
        # Create background
        background = self._create_background(video_duration)
        
        # Create segments (character poses + images)
        segments_clips = self._create_segment_clips(
            production_plan,
            timestamps,
            character_poses_dir,
            video_images_dir,
            video_duration
        )
        
        # Create captions
        caption_clips = self._create_caption_clips(timestamps, video_duration)
        
        # Create ticker animation
        ticker_clips = self._create_ticker_animation(
            ticker_image_path,
            ticker_background_path,
            video_duration
        )
        
        # Combine all clips
        all_clips = [background] + segments_clips + caption_clips + ticker_clips
        
        final_video = CompositeVideoClip(
            all_clips, 
            size=(self.config.video_width, self.config.video_height)
        )
        
        # Add audio
        if background_music_path and Path(background_music_path).exists():
            music = AudioFileClip(background_music_path).with_volume_scaled(0.15)
            music = music.with_duration(video_duration)
            final_audio = CompositeAudioClip([narration_audio, music])
        else:
            final_audio = narration_audio
        
        final_video = final_video.with_audio(final_audio)
        
        # Export video
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
        """Load JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _create_background(self, duration: float) -> ColorClip:
        """Create solid color background"""
        return ColorClip(
            size=(self.config.video_width, self.config.video_height),
            color=self.config.background_color,
            duration=duration
        )
    
    def _create_segment_clips(
        self,
        production_plan: Dict,
        timestamps: Dict,
        character_poses_dir: str,
        video_images_dir: str,
        video_duration: float
    ) -> List[VideoClip]:
        """Create clips for character poses and images based on segments"""
        
        clips = []
        segments = production_plan.get("segments", [])
        timestamp_segments = timestamps.get("segments", [])
        
        # Match segments with timestamps
        for i, segment in enumerate(segments):
            segment_id = segment.get("segment_id")
            
            # Find corresponding timestamp
            if i < len(timestamp_segments):
                ts = timestamp_segments[i]
                start_time = ts.get("start", 0)
                end_time = ts.get("end", video_duration)
            else:
                continue
            
            duration = end_time - start_time
            
            # Character pose (left side)
            pose_data = segment.get("pose", {})
            pose_filename = pose_data.get("filename")
            
            if pose_filename:
                pose_path = Path(character_poses_dir) / pose_filename
                if pose_path.exists():
                    pose_clip = self._create_image_clip(
                        str(pose_path),
                        start_time,
                        duration,
                        self.config.character_x,
                        self.config.character_y,
                        self.config.character_width,
                        self.config.character_height
                    )
                    clips.append(pose_clip)
            
            # Generated/Downloaded image (right side)
            image_filename = f"segment_{segment_id}.png"
            
            # Check both directories
            generated_path = Path(video_images_dir) / "generated_images" / image_filename
            downloaded_path = Path(video_images_dir) / "download_images" / image_filename
            
            image_path = None
            if generated_path.exists():
                image_path = generated_path
            elif downloaded_path.exists():
                image_path = downloaded_path
            
            if image_path:
                image_clip = self._create_image_clip(
                    str(image_path),
                    start_time,
                    duration,
                    self.config.image_x,
                    self.config.image_y,
                    self.config.image_width,
                    self.config.image_height
                )
                clips.append(image_clip)
        
        return clips
    
    def _create_image_clip(
        self,
        image_path: str,
        start_time: float,
        duration: float,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> ImageClip:
        """Create an image clip with fade in/out and positioning"""
        
        # Load and resize image
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if needed, but preserve transparency
        if img.mode == 'RGBA':
            img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
        else:
            img_resized = img.convert('RGB').resize((width, height), Image.Resampling.LANCZOS)
        
        # Create ImageClip from numpy array
        # MoviePy v2 still supports this internally
        clip = ImageClip(np.array(img_resized))
        
        # Set clip properties using v2 methods
        clip = clip.with_duration(duration)
        clip = clip.with_start(start_time)
        clip = clip.with_position((x - width // 2, y - height // 2))
        
        # Apply fade effects using with_effects() method (v2 syntax)
        fade_duration = min(self.config.image_fade_duration, duration / 4)
        clip = clip.with_effects([
            FadeIn(fade_duration),
            FadeOut(fade_duration)
        ])
        
        return clip
    
    def _create_caption_clips(self, timestamps: Dict, video_duration: float) -> List[VideoClip]:
        """Create caption clips based on word timestamps"""
        
        clips = []
        words = timestamps.get("words", [])
        
        for word_data in words:
            word = word_data.get("word", "")
            start = word_data.get("start", 0)
            end = word_data.get("end", 0)
            duration = end - start
            
            if duration <= 0:
                continue
            
            # Create text clip
            try:
                txt_clip = TextClip(
                    text=word,
                    font=self.config.caption_font_path,
                    font_size=self.config.caption_fontsize,
                    color=self.config.caption_color,
                    stroke_color=self.config.caption_stroke_color,
                    stroke_width=self.config.caption_stroke_width,
                    method='caption',
                    size=(self.config.caption_max_width, None)
                )
                
                # Set clip properties using v2 methods
                txt_clip = txt_clip.with_duration(duration)
                txt_clip = txt_clip.with_start(start)
                txt_clip = txt_clip.with_position(('center', self.config.caption_y))
                
                clips.append(txt_clip)
                
            except Exception as e:
                print(f"⚠️ Error creating caption for '{word}': {e}")
                continue
        
        return clips
    
    def _create_ticker_animation(
        self,
        ticker_image_path: str,
        ticker_background_path: str,
        video_duration: float
    ) -> List[VideoClip]:
        """Create animated ticker with background"""
        
        clips = []
        
        # Ticker background (static, with channel name)
        ticker_bg = Image.open(ticker_background_path)
        ticker_bg_resized = ticker_bg.resize((self.config.video_width, self.config.ticker_height))
        
        ticker_bg_clip = ImageClip(np.array(ticker_bg_resized))
        ticker_bg_clip = ticker_bg_clip.with_duration(video_duration)
        ticker_bg_clip = ticker_bg_clip.with_position((0, self.config.ticker_y))
        
        clips.append(ticker_bg_clip)
        
        # Ticker stocks (animated, scrolling)
        ticker_img = Image.open(ticker_image_path)
        ticker_width = ticker_img.size[0]
        ticker_resized = ticker_img.resize((ticker_width, self.config.ticker_height))
        
        # Calculate fade zone
        fade_start_x = int(self.config.video_width * (self.config.ticker_fade_start_percent / 100))
        
        # Create scrolling ticker with fade
        def make_frame(t):
            # Calculate position
            x_offset = int(self.config.video_width - (t * self.config.ticker_speed))
            
            # Create frame
            frame = np.zeros((self.config.ticker_height, self.config.video_width, 3), dtype=np.uint8)
            
            # Get ticker section
            ticker_array = np.array(ticker_resized)
            
            # Handle looping
            x_offset = x_offset % ticker_width
            
            # Calculate which part of ticker to show
            if x_offset > 0:
                # Ticker hasn't fully scrolled yet
                visible_width = min(ticker_width - x_offset, self.config.video_width)
                frame[:, :visible_width] = ticker_array[:, x_offset:x_offset + visible_width]
            else:
                # Ticker is looping
                x_offset = abs(x_offset)
                first_part_width = min(ticker_width - x_offset, self.config.video_width)
                frame[:, :first_part_width] = ticker_array[:, x_offset:x_offset + first_part_width]
                
                # Add loop part if needed
                if first_part_width < self.config.video_width:
                    remaining = self.config.video_width - first_part_width
                    frame[:, first_part_width:first_part_width + remaining] = ticker_array[:, :remaining]
            
            # Apply fade gradient near the left edge
            for x in range(fade_start_x):
                alpha = x / fade_start_x
                frame[:, x] = (frame[:, x] * alpha).astype(np.uint8)
            
            return frame
        
        ticker_clip = VideoClip(make_frame, duration=video_duration)
        ticker_clip = ticker_clip.with_position((0, self.config.ticker_y))
        
        clips.append(ticker_clip)
        
        return clips


def assemble_video(
    production_plan_path: str,
    timestamps_path: str,
    narration_audio_path: str,
    background_music_path: Optional[str],
    ticker_image_path: str,
    ticker_background_path: str,
    character_poses_dir: str,
    video_images_dir: str,
    output_path: str,
    config: Optional[VideoConfig] = None
) -> str:
    """
    Convenience function to assemble video
    
    Example usage:
        config = VideoConfig()
        config.caption_color = "yellow"
        config.ticker_speed = 150
        
        assemble_video(
            production_plan_path="data/create_production_plan/output/production_plan.json",
            timestamps_path="data/video_audio/elevenlabs/timestamps.json",
            narration_audio_path="data/video_audio/elevenlabs/narration.mp3",
            background_music_path="data/music/background.mp3",
            ticker_image_path="data/video_ticker/ticker.png",
            ticker_background_path="data/video_ticker/ticker_background.png",
            character_poses_dir="data/character_poses",
            video_images_dir="data/video_images",
            output_path="output/final_video.mp4",
            config=config
        )
    """
    assembler = VideoAssembler(config)
    return assembler.create_video(
        production_plan_path=production_plan_path,
        timestamps_path=timestamps_path,
        narration_audio_path=narration_audio_path,
        background_music_path=background_music_path,
        ticker_image_path=ticker_image_path,
        ticker_background_path=ticker_background_path,
        character_poses_dir=character_poses_dir,
        video_images_dir=video_images_dir,
        output_path=output_path
    )