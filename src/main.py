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


def getConfig():
    config = configparser.ConfigParser()
    config.read('../docs/config.ini')
    return config


def main():
    print("Testing")
    config = getConfig()
    print("--------------------")
    cli = CLI.CLIInterface()
    cli.display_welcome()

    # for dirpath, _, filenames in os.walk('.'):
    #     for filename in filenames:
    #         print(os.path.join(dirpath, filename))
    #         print('-' * 20)


if __name__ == "__main__":
    main()
