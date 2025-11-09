import sys
from typing import Optional
from config import PipelineConfig
from orchestrators import PipelineOrchestrator
from ui import ConsoleUI

SEPARATOR = "=" * 60


class CommandHandler:
    """Handles command-line argument routing"""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.orchestrator = PipelineOrchestrator(config)

        # Command mapping
        self.commands = {
            "--step=narrate": self._handle_narrate,
            "--step=transcribe": self._handle_transcribe,
            "--step=audio-pipeline": self._handle_audio_pipeline,
            "--step=animation-prompts": self._handle_animation_prompts,
            "--step=calculate-cost": self._handle_calculate_cost,
            "--step=test-frames": self._handle_test_frames,
            "--step=generate-frames": self._handle_generate_frames,
            "--step=animation-pipeline": self._handle_animation_pipeline,
            "--step=assemble-video": self._handle_assemble_video,
            "--help": self._handle_help,
        }

    def execute(self, command: Optional[str] = None):
        """Execute command or run full pipeline"""
        try:
            if command is None:
                self.orchestrator.run_full_pipeline()
            elif command in self.commands:
                self.commands[command]()
            else:
                print(f"[ERROR] Unknown argument: {command}")
                self._handle_help()
                sys.exit(1)
        except Exception as e:
            ConsoleUI.print_error(e)
            sys.exit(1)

    def _handle_narrate(self):
        ConsoleUI.print_header("NARRATION GENERATION")
        self.orchestrator.audio_stage.generate_audio()

    def _handle_transcribe(self):
        ConsoleUI.print_header("TRANSCRIPTION GENERATION")
        self.orchestrator.audio_stage.generate_timestamps()

    def _handle_audio_pipeline(self):
        self.orchestrator.run_audio_pipeline()

    def _handle_animation_prompts(self):
        ConsoleUI.print_header("ANIMATION PROMPTS GENERATION")
        self.orchestrator.crew_stage.run_animation_prompts()
        ConsoleUI.print_header("ANIMATION PROMPTS COMPLETE!")
        ConsoleUI.print_file_list("Generated file", ["output/animation_prompts.json"])
        ConsoleUI.print_next_step("Generate frames with: python main.py --step=generate-frames")
        print(f"{SEPARATOR}\n")

    def _handle_calculate_cost(self):
        ConsoleUI.print_header("COST CALCULATION")
        self.orchestrator.frame_stage.calculate_cost()
        print(f"\n{SEPARATOR}\n")

    def _handle_test_frames(self):
        ConsoleUI.print_header("TEST FRAME GENERATION (First 10 frames)")
        stats = self.orchestrator.frame_stage.generate_test_frames(num_frames=10)
        ConsoleUI.print_header("TEST FRAME GENERATION COMPLETE!")
        print(f"Generated {stats['frames_generated']} test frames")
        print(f"Review frames in: output/frames/")
        ConsoleUI.print_next_step("Generate all frames with: python main.py --step=generate-frames")
        print(f"{SEPARATOR}\n")

    def _handle_generate_frames(self):
        ConsoleUI.print_header("FRAME GENERATION")
        stats = self.orchestrator.frame_stage.generate_frames(confirm_cost=True)

        if not stats.get("cancelled"):
            ConsoleUI.print_header("FRAME GENERATION COMPLETE!")
            print(f"Generated {stats['frames_generated']} frames")
            print(f"Saved to: output/frames/")
            ConsoleUI.print_next_step("Assemble video with: python main.py --step=assemble-video")
            print(f"{SEPARATOR}\n")

    def _handle_animation_pipeline(self):
        self.orchestrator.run_animation_pipeline()

    def _handle_assemble_video(self):
        ConsoleUI.print_header("VIDEO ASSEMBLY")
        self.orchestrator.video_stage.assemble_video()
        ConsoleUI.print_header("VIDEO ASSEMBLY COMPLETE!")
        print(f"{SEPARATOR}\n")

    def _handle_help(self):
        """Print help message"""
        ConsoleUI.print_header("CRYPTO CLARITY - YouTube Shorts Production Pipeline")
        print("\nAVAILABLE COMMANDS:\n")

        print("FULL WORKFLOWS:")
        print("  python main.py")
        print("    → Full pipeline: Research → Script → Audio → Timestamps → Prompts → Frames")
        print()
        print("  python main.py --step=audio-pipeline")
        print("    → Audio → Timestamps (requires video_script.json)")
        print()
        print("  python main.py --step=animation-pipeline")
        print("    → Animation Prompts → Frames (requires timestamps.json)")
        print()

        print("\nINDIVIDUAL STEPS:")
        print("  python main.py --step=narrate")
        print("    → Generate audio only (requires video_script.json)")
        print()
        print("  python main.py --step=transcribe")
        print("    → Generate timestamps only (requires narracion.mp3)")
        print()
        print("  python main.py --step=animation-prompts")
        print("    → Create animation prompts (requires timestamps.json)")
        print()
        print("  python main.py --step=calculate-cost")
        print("    → Calculate frame generation cost (requires animation_prompts.json)")
        print()
        print("  python main.py --step=test-frames")
        print("    → Generate first 10 frames as test (requires animation_prompts.json)")
        print()
        print("  python main.py --step=generate-frames")
        print("    → Generate ALL images with Gemini (requires animation_prompts.json)")
        print()
        print("  python main.py --step=assemble-video")
        print("    → Assemble final video (requires frames/ and audio)")
        print()

        print("\nOTHER:")
        print("  python main.py --help")
        print("    → Show this help message")
        print()

        print("\nTYPICAL WORKFLOWS:\n")
        print("New video from scratch:")
        print("  1. python main.py")
        print("     (runs everything)")
        print()
        print("Resume after audio:")
        print("  1. python main.py --step=animation-pipeline")
        print("  2. python main.py --step=assemble-video")
        print()
        print("Regenerate frames only:")
        print("  1. Delete output/frames/")
        print("  2. python main.py --step=generate-frames")
        print()

        print(f"{SEPARATOR}\n")
