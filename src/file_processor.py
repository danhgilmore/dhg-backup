"""
File processing module for timestamp-based renaming and organization
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime

from exif_handler import ExifHandler
from heic_converter import HeicConverter
from file_categorizer import FileCategorizer, FileCategory

logger = logging.getLogger(__name__)


class FileProcessor:
    """Main file processing coordinator"""

    def __init__(self, export_dir: str = "export", backup_dir: str = "backup"):
        """
        Initialize file processor.

        Args:
            export_dir: Directory containing exported files
            backup_dir: Directory for organized output files
        """
        self.export_dir = export_dir
        self.backup_dir = backup_dir

        # Initialize component handlers
        self.exif_handler = ExifHandler()
        self.heic_converter = HeicConverter()
        self.categorizer = FileCategorizer()

        # Track processed files and timestamps
        self.processed_files = []
        self.used_timestamps = set()
        self.failed_files = []
        self.conversion_log = []
