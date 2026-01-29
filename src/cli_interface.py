import os
import logging

from typing import Dict, List, Set, Tuple, Optional

from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.logging import RichHandler
from rich.prompt import Confirm

from file_processor import FileProcessor
# from .file_categorizer import FileCategory

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

        export_path = Path(self.processor.export_dir)
        backup_path = Path(self.processor.backup_dir)

        # Check export directory
        if not export_path.exists():
            self.console.print(
                f"[red]Error: Export directory does not exist: {export_path}[/red]")
            self.console.print(
                f"[yellow]Please create the directory and place your exported photos there:[/yellow]")
            self.console.print(f"[dim]  mkdir {export_path}[/dim]")
            self.console.print(
                f"[dim]  # Then copy your iCloud Photos export files to {export_path}/[/dim]")
            return False

        if not any(export_path.iterdir()):
            self.console.print(
                f"[yellow]Warning: Export directory is empty: {export_path}[/yellow]")
            if not Confirm.ask("Continue anyway?"):
                return False

        # Create backup directory if it doesn't exist
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            self.console.print(
                f"[green]Backup directory is ready: {backup_path}[/green]")
        except Exception as e:
            self.console.print(
                f"[red]Error: Cannot create backup directory: {backup_path} {e}[/red]")
            return False

        return True

    def display_file_scan_results(self, files: List[str]):
        """
        Display results of file scanning.

        Args:
            files: List of files found
        """
        if not files:
            self.console.print("[yellow]No files found to process.[/yellow]")
            return

        # Categorize files for display
        self.processor.categorizer.batch_categorize(files)
        stats = self.processor.categorizer.get_categorization_stats()

        # Create summary table

        table = Table(title="File Scan Results", show_lines=True)
        table.add_column("Category", style="cyan", width=15)
        table.add_column("Count", justify="right", style="green")
        table.add_column("Description", style="dim")

        table.add_row("Photos", str(stats['photos']), "JPEG, PNG, HEIC, etc.")
        table.add_row("Videos", str(stats['videos']), "MOV, MP4, M4V, etc.")
        table.add_row("Screenshots", str(
            stats['screenshots']), "PNG files with screenshot patterns")
        table.add_row("Sidecar Files", str(
            stats['sidecar']), "Apple .aae files (will be deleted)")

        if stats['unknown'] > 0:
            table.add_row("Unknown", str(
                stats['unknown']), "Unrecognized file types", style="yellow")

        table.add_column("Total Files Found", justify="right", style="cyan")
        table.add_column("Sample Files", style="magenta")

        table.add_row("", "", "", style="dim")
        table.add_row("Total", str(stats['total']),
                      "Files to process", style="bold")
        # sample_files = "\n".join(files[:5])  # Show first 5 files as sample
        # table.add_row(str(len(files)), sample_files)

        self.console.print(table)

    def process_with_progress(self, dry_run: bool = False) -> Dict:
        """
        Process files with progress display.

        Args:
            dry_run: If True, simulate processing without making changes

        Returns:
            Dictionary with processing results
        """
        with self.console.status("[bold green]Scanning export directory...") as status:
            files = self.processor._scan_export_directory()

        if not files:
            self.console.print(
                "[yellow]No files found to process.[/yellow]")
            return {}
        self.display_file_scan_results(files)

        if dry_run:
            self.console.print(
                f"\n[bold blue]DRY RUN MODE ENABLED[/bold blue] - No changes will be made.\n")

        # Confirm before proceeding
        if not dry_run:
            if not Confirm.ask(f"\nProceed with processing {len(files)} files?"):
                self.console.print("[yellow]Processing cancelled[/yellow]")
                return {}
        # Process with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:

            # # Add tasks for different phases
            # categorize_task = progress.add_task("Categorizing files...", total=1)
            # sidecar_task = progress.add_task("Processing sidecar files...", total=1)
            # convert_task = progress.add_task("Converting HEIC files...", total=None)
            # organize_task = progress.add_task("Organizing files...", total=None)

            # Categorize files
            # categorized = self.processor.categorizer.batch_categorize(files)
            # progress.update(categorize_task, completed=1)

            # Delete sidecar files
            # sidecar_files = categorized.get(FileCategory.SIDECAR, [])
            # if sidecar_files:
            #     progress.update(sidecar_task, total=len(sidecar_files))
            #     self.processor._delete_sidecar_files(sidecar_files, dry_run)
            # progress.update(sidecar_task, completed=progress.tasks[sidecar_task].total or 1)

            # Process all files using the FileProcessor's main method
            # This replaces the duplicate processing loop that was causing duplicates
            self.processor.process_all_files(dry_run=dry_run)

        # Generate and return summary
        return self.processor._generate_summary()

    def display_results(self, results: Dict, dry_run: bool = False):
        """

        Display processing results.
        Args:
            results: Dictionary with processing results
            dry_run: If True, indicates dry run mode
        """
        if not results:
            return

        # Success/failure summary
        success_count = results.get('files_processed', 0)
        failure_count = results.get('files_failed', 0)

        if dry_run:
            title = "Dry Run Processing Results"
            title_style = "bold blue"
        elif failure_count == 0:
            title = "Processing Results - All Successful"
            title_style = "bold green"
        else:
            title = "Processing Results - Some Failures"
            title_style = "bold red"

        table = Table(title=title, show_header=True,
                      header_style="bold magenta")
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Count", justify="right", style="green")

        table.add_row("Files Processed", str(success_count))
        table.add_row("Files Failed", str(failure_count))

        if failure_count > 0:
            table.add_row(
                "Check Failed Files Below", str(failure_count), style="red")

        self.console.print(table)
