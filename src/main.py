#!/usr/bin/env python3
import io
import os

import configparser
import boto3
from boto3.s3.transfer import S3UploadFailedError

import config as Config
import cli_interface as CLI

try:
    from cli_interface import CLIInterface, setup_logging
except ImportError:
    from .cli_interface import CLIInterface, setup_logging

xport = ''


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


def main():
    print("starting main")
    # config = getConfig()
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
    print(f"export_dir from config: {export_dir}")
    print(f"backup_dir from config: {backup_dir}")

    cli = CLI.CLIInterface()
    cli.display_welcome()
    print("checking directories")

    cli.check_directories(export_dir, backup_dir)
    print("done checking directories")


if __name__ == "__main__":
    main()
