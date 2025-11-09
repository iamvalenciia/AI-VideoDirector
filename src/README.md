# Source Code Structure

```
src/
├── main.py                    # Entry point (15 lines)
│
├── config/                    # Configuration
│   └── pipeline_config.py     # Pipeline settings & paths
│
├── ui/                        # User Interface
│   └── console.py             # Console output formatting
│
├── validators/                # Validation Logic
│   └── file_validator.py      # File existence checks
│
├── stages/                    # Pipeline Stages
│   ├── crew_stage.py          # CrewAI research & prompts
│   ├── audio_stage.py         # Audio & timestamps
│   ├── frame_stage.py         # Frame generation
│   └── video_stage.py         # Video assembly
│
├── orchestrators/             # Workflow Orchestration
│   └── pipeline_orchestrator.py  # Combines stages into workflows
│
├── handlers/                  # Command Handling
│   └── command_handler.py     # CLI argument routing
│
├── tools/                     # External Tools
│   ├── elevenlabs_tool.py     # Audio generation
│   ├── whisper_tool.py        # Transcription
│   ├── gemini_image_tool.py   # Image generation
│   ├── video_assembler_tool.py # Video assembly
│   └── duckduckgo_tool.py     # Web search
│
└── crew.py                    # CrewAI configuration
```

## Usage

```bash
# Run from project root
cd src
python main.py                        # Full pipeline
python main.py --step=audio-pipeline  # Audio only
python main.py --help                 # Show help
```
