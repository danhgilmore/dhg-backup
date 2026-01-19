#!/usr/bin/env python3
import sys
# import io
import os
import click
import configparser
import config as Config
import cli_interface as CLI

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
# python3 main.py --dry-run=true --verbose=true --export-dir=/Volumes/Users/dan/Documents/CHSongs --backup-dir=/Users/dangilmore/export-test
def main(dry_run, verbose, export_dir, backup_dir):
    """Main entry point for the dhg-monthly-backup application."""
    setup_logging(verbose)

    config = configparser.ConfigParser()
    # Construct an absolute path relative to the script's directory
    config_path = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), "config.ini")

    files_read = config.read(config_path)
    if not files_read:
        raise IOError(f"Cannot load config file: {config_path}")
    export_dir = config.get('DEFAULT', 'export_dir')

    print("--------------------")
    export_dir = config.get('DEFAULT', 'export_dir')
    backup_dir = config.get('DEFAULT', 'backup_dir')
    # print(f"export_dir from config: {export_dir}")
    # print(f"backup_dir from config: {backup_dir}")

    cli = CLI.CLIInterface(export_dir, backup_dir)

    cli.display_welcome()
    # print("checking directories")
    if not cli.check_directories(export_dir, backup_dir):
        cli.console.print("[red]Cannot proceed due to directory issues.[/red]")
        sys.exit(1)

    try:
        # Process files with progress display
        results = cli.process_with_progress(dry_run=dry_run)
        cli.display_results(results, dry_run=dry_run)

    except Exception as e:
        cli.console.print(f"[red]Error during file processing: {e}[/red]")
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
