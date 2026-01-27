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

    def categorize_file(self, file_path: str) -> FileCategory:
        """
        Categorize a single file based on extension and filename patterns.

        Args:
            file_path: Path to file

        Returns:
            FileCategory enum value
        """
        file_path_obj = Path(file_path)
        ext = file_path_obj.suffix.lower()
        filename = file_path_obj.name.lower()

        # Check for sidecar files first
        if ext in self.sidecar_exts:
            return FileCategory.SIDECAR

        # Check for screenshots (PNG files with screenshot patterns)
        if ext in self.screenshot_exts:
            # Additional heuristics for screenshot detection
            if self._is_likely_screenshot(filename):
                return FileCategory.SCREENSHOT
            # Check if it's AI-generated or heavily edited content
            if self._is_generated_content(file_path):
                return FileCategory.GENERATED
            # If PNG but not clearly a screenshot, treat as photo
            return FileCategory.PHOTO

        # Check for photos
        if ext in self.photo_exts:
            # Check if it's AI-generated or heavily edited content
            if self._is_generated_content(file_path):
                return FileCategory.GENERATED
            return FileCategory.PHOTO

        # Check for videos
        if ext in self.video_exts:
            return FileCategory.VIDEO

        # Unknown file type
        logger.warning(f"Unknown file type: {file_path}")
        return FileCategory.UNKNOWN

    def _is_likely_screenshot(self, filename: str) -> bool:
        """
        Determine if a file is likely a screenshot based on filename patterns.

        Args:
            filename: Lowercase filename

        Returns:
            True if filename suggests it's a screenshot
        """
        screenshot_patterns = [
            'screenshot',
            'screen shot',
            'img_',  # iOS screenshot pattern
            'simulator screen shot',  # iOS Simulator
            'screen recording',
            'img_3',  # iOS screenshot pattern (IMG_3XXX)
            'screen_',
            'capture',
        ]

        # iOS screenshots often have specific patterns
        # IMG_XXXX.PNG where XXXX is 4+ digits starting with 3
        if filename.startswith('img_3') and filename.endswith('.png'):
            return True

        return any(pattern in filename for pattern in screenshot_patterns)

    def _is_generated_content(self, file_path: str) -> bool:
        """
        Detect AI-generated or heavily edited content using pure Python.

        Args:
            file_path: Path to file

        Returns:
            True if file appears to be AI-generated or heavily edited
        """
        try:
            from PIL import Image

            with Image.open(file_path) as img:
                # Check for C2PA/AI metadata in PNG files
                if file_path.lower().endswith('.png'):
                    # Look for C2PA markers in PNG text chunks
                    if hasattr(img, 'text') and img.text:
                        for key, value in img.text.items():
                            if any(ai_marker in str(value).lower() for ai_marker in
                                   ['gpt', 'chatgpt', 'openai', 'c2pa', 'ai', 'generated']):
                                logger.info(
                                    f"Detected AI-generated content: {file_path}")
                                return True

                # Check EXIF data for editing software + missing original timestamps
                exif = img.getexif()
                if exif:
                    from PIL.ExifTags import TAGS

                    has_editing_software = False
                    has_original_timestamp = False

                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, str(tag_id))

                        # Check for editing software
                        if tag == 'Software' and any(editor in str(value).lower() for editor in
                                                     ['snapseed', 'photoshop', 'lightroom', 'gimp', 'canva']):
                            has_editing_software = True

                        # Check for original timestamp tags
                        if tag in ['DateTimeOriginal', 'DateTimeDigitized']:
                            has_original_timestamp = True

                    # If edited but no original timestamp, likely heavily processed
                    if has_editing_software and not has_original_timestamp:
                        logger.info(
                            f"Detected heavily edited content: {file_path}")
                        return True

                # Check for UUID-style filenames (often generated content)
                filename = Path(file_path).stem
                if len(filename) == 36 and filename.count('-') == 4:  # UUID format
                    logger.info(
                        f"Detected UUID filename (likely generated): {file_path}")
                    return True

        except Exception as e:
            logger.debug(
                f"Error checking generated content for {file_path}: {e}")

        return False
