from pathlib import Path
from typing import Dict


class FileValidator:
    """Validates required files exist before operations"""

    @staticmethod
    def validate_file(file_path: Path, description: str):
        """Validate single file exists"""
        if not file_path.exists():
            raise FileNotFoundError(
                f"{description} not found at {file_path}. "
                f"Please run the previous pipeline steps first."
            )

    @staticmethod
    def validate_files(files: Dict[Path, str]):
        """Validate multiple files exist"""
        for file_path, description in files.items():
            FileValidator.validate_file(file_path, description)
