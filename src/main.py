#!/usr/bin/env python3
import sys
# import io
import os
import click
import configparser
import config as Config
# import cli_interface as CLI

try:
    from cli_interface import CLIInterface, setup_logging
except ImportError:
    from .cli_interface import CLIInterface, setup_logging


@click.command()
@click.option('--export-dir', default=None, help='Directory to export processed files to.')
@click.option('--backup-dir', default=None, help='Directory to backup original files to.')
@click.option('--dry-run', is_flag=True, default=False, help='Perform a dry run without making any changes.')
@click.option('--verbose', is_flag=True, default=True, help='Enable verbose logging output.')
@click.version_option(version='1.0.0', prog_name='dhg-monthly-backup')
def main(dry_run, verbose, export_dir, backup_dir):
    """
    Main entry point for the dhg-monthly-backup application.
    """
    setup_logging(verbose)

    config = configparser.ConfigParser()
    # Construct an absolute path relative to the script's directory
    config_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "config.ini")

    files_read = config.read(config_path)
    if not files_read:
        raise IOError(f"Cannot load config file: {config_path}")
    export_dir = config.get('DEFAULT', 'export_dir')

    export_dir = config.get('DEFAULT', 'export_dir')
    backup_dir = config.get('DEFAULT', 'backup_dir')
    # print(f"export_dir from config: {export_dir}")
    # print(f"backup_dir from config: {backup_dir}")

    # Intialize CLI interface
    cli = CLIInterface(export_dir, backup_dir)

    # Display welcome banner
    cli.display_welcome()

    # Check directories and prerequisites
    if not cli.check_directories():
        cli.console.print("[red]Cannot proceed due to directory issues.[/red]")
        sys.exit(1)

    try:
        # Process files with progress display
        results = cli.process_with_progress(dry_run=dry_run)

        # Display results summary
        cli.display_results(results, dry_run=dry_run)

        # Exit with the appropriate status code
        if results.get('failed_files', 0) > 0:
            cli.console.print(
                f"\n[yellow]Completed with {results['files_failed']} failures.[/yellow]")
            sys.exit(1)
        else:

            if not dry_run and results.get('files_processed', 0) > 0:
                cli.console.print(
                    "\n[bold green]All files processed successfully![/bold green]")
            elif dry_run:
                cli.console.print(
                    "\n[blue]Dry run completed. Use without --dry-run to process files.[/blue]")
            sys.exit(0)

    except KeyboardInterrupt:
        cli.console.print("\n[yellow]Processing interrupted by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        cli.console.print(f"\n[red]Unexpected error: {e}[/red]")
        if verbose:
            import traceback
            cli.console.print(traceback.format_exc())
        sys.exit(1)


def getConfig():
    configFile = 'config.ini'
    # if not os.path.isfile(configFile):
    #     raise FileNotFoundError(f"Configuration file not found: {configFile}")
    config = configparser.ConfigParser()
    # Construct an absolute path relative to the script's directory
    config_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "config.ini")

    files_read = config.read(config_path)
    if not files_read:
        raise IOError(f"Cannot load config file: {config_path}")
    export_dir = config.get('DEFAULT', 'export_dir')
    return config


if __name__ == "__main__":
    main()
