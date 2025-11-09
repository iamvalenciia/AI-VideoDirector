from typing import List

SEPARATOR = "=" * 60


class ConsoleUI:
    """Handles all console output formatting"""

    @staticmethod
    def print_header(title: str):
        """Print formatted header"""
        print(f"\n{SEPARATOR}")
        print(title)
        print(SEPARATOR)

    @staticmethod
    def print_step(step_num: int, total_steps: int, description: str):
        """Print step progress"""
        print(f"\n[STEP {step_num}/{total_steps}] {description}...")

    @staticmethod
    def print_success(message: str):
        """Print success message"""
        print(f"[SUCCESS] {message}")

    @staticmethod
    def print_info(message: str):
        """Print info message"""
        print(f"[INFO] {message}")

    @staticmethod
    def print_error(error: Exception):
        """Print formatted error"""
        print(f"\n{SEPARATOR}")
        print("ERROR DURING EXECUTION")
        print(SEPARATOR)
        print(f"\n{str(error)}\n")
        print(f"{SEPARATOR}\n")

    @staticmethod
    def print_file_list(title: str, files: List[str]):
        """Print list of generated files"""
        print(f"{title}:")
        for file in files:
            print(f"  [OK] {file}")

    @staticmethod
    def print_next_step(command: str):
        """Print next step suggestion"""
        print(f"\nNext step: {command}")
