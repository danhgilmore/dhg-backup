"""
File categorization module for organizing files by type
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class FileCategory(Enum):
    """File category enumeration"""
    PHOTO = "photos"
    VIDEO = "videos"
    SCREENSHOT = "screenshots"
    GENERATED = "generated"  # AI-generated or heavily edited content
    UNKNOWN = "unknown"
    SIDECAR = "sidecar"


class FileCategorizer:
    """Categorizes files by type based on extension and content analysis"""

    # File extension mappings
    PHOTO_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.heic', '.heif',
        '.tiff', '.tif', '.bmp', '.webp', '.dng', '.raw',
        '.cr2', '.nef', '.arw', '.orf', '.rw2'
    }

    VIDEO_EXTENSIONS = {
        '.mov', '.mp4', '.m4v', '.avi', '.mkv', '.wmv',
        '.flv', '.webm', '.3gp', '.mpg', '.mpeg'
    }

    SCREENSHOT_EXTENSIONS = {
        '.png'  # Screenshots are typically PNG on iOS/macOS
    }

    SIDECAR_EXTENSIONS = {
        '.aae'  # Apple's sidecar files
    }

    def __init__(self):
        self.categorized_files = {
            FileCategory.PHOTO: [],
            FileCategory.VIDEO: [],
            FileCategory.SCREENSHOT: [],
            FileCategory.GENERATED: [],
            FileCategory.UNKNOWN: [],
            FileCategory.SIDECAR: []
        }

        # Convert to lowercase for case-insensitive matching
        self.photo_exts = {ext.lower() for ext in self.PHOTO_EXTENSIONS}
        self.video_exts = {ext.lower() for ext in self.VIDEO_EXTENSIONS}
        self.screenshot_exts = {ext.lower()
                                for ext in self.SCREENSHOT_EXTENSIONS}
        self.sidecar_exts = {ext.lower() for ext in self.SIDECAR_EXTENSIONS}
