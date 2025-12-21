import os
import sys
import logging
from typing import Dict, List
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.logging import RichHandler
from rich.prompt import Confirm

from .file_processor import FileProcessor
#from .file_categorizer import FileCategory

console = Console()


def setup_logging(verbose: bool = False):
    """
    Setup logging with rich handler for beautiful output.

    Args:
        verbose: Enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO

    # Configure rich logging handler
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=verbose,
        markup=True
    )

    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[rich_handler]
    )

    # Reduce pillow logging noise
    logging.getLogger('PIL').setLevel(logging.WARNING)


class CLIInterface:
    def __init__(self, export_dir: str = "export", backup_dir: str = "backup"):
        """
        Initialize CLI interface.

        Args:
            export_dir: Export directory path
            backup_dir: Backup directory path
        """
        self.processor = FileProcessor(export_dir, backup_dir)
        self.console = console

    def display_welcome(self):
        """Display welcome banner"""
        welcome_text = Text("dhg-monthly-backup", style="bold blue")
        welcome_text.append(
            "\nAutomated Media Organization Tool", style="dim")

        panel = Panel(
            welcome_text,
            title="Welcome",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)

    def check_directories(self) -> bool:
        """
        Check if export and backup directories exist.

        Returns:
            True if both directories exist, False otherwise
        """
        export_dir = Path(self.processor.export_dir)
        backup_dir = Path(self.processor.backup_dir)

        if not export_dir.exists():
            self.console.print(
                f"Export directory '{export_dir}' does not exist.", style="bold red")
            return False

        if not backup_dir.exists():
            self.console.print(
                f"Backup directory '{backup_dir}' does not exist.", style="bold red")
            return False

        return True
