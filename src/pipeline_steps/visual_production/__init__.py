"""
VISUAL PRODUCTION - Pipeline Steps 6-10

Core production tools:
- bottom_ticker_generator: Create scrolling bottom ticker (Step 7)
- frame_compositor: Compose all layers into frames (Step 9)
- visual_director: Plan visual production (GPT-4o)
- gemini_studio_generator: Generate studio assets (Gemini 2.0 Flash)
- background_remover: Remove backgrounds from images
- set_compositor: Composite visual elements
- stock_ticker_tool: Wrapper for bottom ticker generator
- video_assembler_tool: Assemble final video (MoviePy)
- production_planner: AI-based production planning
- deterministic_production_planner: Rule-based production planning
- final_video_assembler: Final video assembly with MoviePy

Note: One-time generators (tweets, charts, illustrations, poses, studio) moved to src/utils/
"""

from .bottom_ticker_generator import BottomTickerGenerator
from .frame_compositor import FrameCompositor
from .visual_director import VisualDirector
from .gemini_studio_generator import GeminiStudioGenerator
from .stock_ticker_tool import StockTickerTool
from .background_remover import BackgroundRemover
from .set_compositor import SetCompositor
from .video_assembler_tool import assemble_youtube_short
from .pose_selector import PoseSelector
from .production_planner import ProductionPlanner
from .deterministic_production_planner import DeterministicProductionPlanner
from .final_video_assembler import FinalVideoAssembler

__all__ = [
    "BottomTickerGenerator",
    "FrameCompositor",
    "VisualDirector",
    "GeminiStudioGenerator",
    "StockTickerTool",
    "BackgroundRemover",
    "SetCompositor",
    "assemble_youtube_short",
    "PoseSelector",
    "ProductionPlanner",
    "DeterministicProductionPlanner",
    "FinalVideoAssembler"
]
