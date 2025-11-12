"""
VISUAL PRODUCTION - Pipeline Steps 6-10

Tools for creating visual assets:
- tweet_screenshot_generator: Generate tweet screenshot images (Step 6)
- bottom_ticker_generator: Create scrolling bottom ticker (Step 7)
- studio_set_generator: Generate newsroom background (Step 8)
- frame_compositor: Compose all layers into frames (Step 9)
- visual_director: Plan visual production (GPT-4o)
- gemini_studio_generator: Generate studio assets (Gemini 2.0 Flash)
- background_remover: Remove backgrounds from images
- set_compositor: Composite visual elements
- stock_ticker_tool: Wrapper for bottom ticker generator
- video_assembler_tool: Assemble final video (MoviePy)
"""

from .tweet_screenshot_generator import TweetScreenshotGenerator
from .bottom_ticker_generator import BottomTickerGenerator
from .studio_set_generator import StudioSetGenerator
from .frame_compositor import FrameCompositor
from .visual_director import VisualDirector
from .gemini_studio_generator import GeminiStudioGenerator
from .stock_ticker_tool import StockTickerTool
from .background_remover import BackgroundRemover
from .set_compositor import SetCompositor
from .video_assembler_tool import assemble_youtube_short
from .character_pose_generator import CharacterPoseGenerator
from .pose_selector import PoseSelector
from .stock_chart_generator import StockChartGenerator
from .illustration_generator import IllustrationGenerator
from .production_planner import ProductionPlanner
from .deterministic_production_planner import DeterministicProductionPlanner
from .final_video_assembler import FinalVideoAssembler

__all__ = [
    "TweetScreenshotGenerator",
    "BottomTickerGenerator",
    "StudioSetGenerator",
    "FrameCompositor",
    "VisualDirector",
    "GeminiStudioGenerator",
    "StockTickerTool",
    "BackgroundRemover",
    "SetCompositor",
    "assemble_youtube_short",
    "CharacterPoseGenerator",
    "PoseSelector",
    "StockChartGenerator",
    "IllustrationGenerator",
    "ProductionPlanner",
    "DeterministicProductionPlanner",
    "FinalVideoAssembler"
]
