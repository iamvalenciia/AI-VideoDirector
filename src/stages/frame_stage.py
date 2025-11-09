from typing import Dict
from tools.gemini_image_tool import (
    generate_animation_from_prompts,
    generate_test_frames,
    calculate_generation_cost
)
from config import PipelineConfig
from ui import ConsoleUI
from validators import FileValidator


class FrameStage:
    """Handles frame generation"""

    def __init__(self, config: PipelineConfig):
        self.config = config

    def validate_prerequisites(self):
        """Validate required files for frame generation"""
        FileValidator.validate_files({
            self.config.prompts_file: "animation_prompts.json",
            self.config.base_image: "base_image.png"
        })

    def generate_frames(self, confirm_cost: bool = True) -> Dict:
        """Generate animation frames"""
        self.validate_prerequisites()
        stats = generate_animation_from_prompts(confirm_cost=confirm_cost)

        if stats.get("cancelled"):
            ConsoleUI.print_info("Frame generation was cancelled")
            return stats

        ConsoleUI.print_success(
            f"Generated {stats['frames_generated']} frames"
        )
        return stats

    def generate_test_frames(self, num_frames: int = 10) -> Dict:
        """Generate test frames"""
        self.validate_prerequisites()
        self._print_test_cost_estimate(num_frames)

        stats = generate_test_frames(num_frames=num_frames)
        ConsoleUI.print_success(
            f"Generated {stats['frames_generated']} test frames"
        )
        return stats

    def calculate_cost(self) -> Dict:
        """Calculate and display generation cost"""
        FileValidator.validate_file(
            self.config.prompts_file,
            "animation_prompts.json"
        )

        cost_info = calculate_generation_cost(str(self.config.prompts_file))
        self._print_cost_breakdown(cost_info)
        return cost_info

    def _print_test_cost_estimate(self, num_frames: int):
        """Print cost estimate for test run"""
        cost_info = calculate_generation_cost(str(self.config.prompts_file))
        test_cost = (cost_info['total_cost_usd'] / cost_info['total_frames']) * num_frames

        print(f"\n[COST ESTIMATION - Test Run]")
        print(f"  Test frames: {num_frames}")
        print(f"  Estimated cost: ${test_cost:.2f}")
        print(f"  Full generation would cost: ${cost_info['total_cost_usd']:.2f}\n")

    def _print_cost_breakdown(self, cost_info: Dict):
        """Print detailed cost breakdown"""
        print(f"\n[FRAMES] Total frames: {cost_info['total_frames']}")
        print(f"\n[COST BREAKDOWN]")
        print(f"  Output cost (images):  ${cost_info['output_cost_usd']:.2f}")
        print(f"  Input cost (prompts):  ${cost_info['input_cost_usd']:.2f}")
        print(f"  ────────────────────────────────────────")
        print(f"  TOTAL ESTIMATED COST:  ${cost_info['total_cost_usd']:.2f}")
        print(f"  Cost per frame:        ${cost_info['cost_per_frame_usd']:.4f}")
        print(f"\n[TOKENS] Estimated: {cost_info['estimated_tokens']:,} tokens")
        print(f"\n[PRICING INFO]")
        print(f"  Gemini 2.5 Flash Image rates:")
        print(f"    - Output: ${cost_info['pricing_info']['output_per_image']:.3f} per image")
        print(f"    - Input:  ${cost_info['pricing_info']['input_per_1m_tokens']:.2f} per 1M tokens")
