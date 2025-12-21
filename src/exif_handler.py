import os
import logging
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS
import pillow_heif

try:
    from hachoir.parser import createParser
    from hachoir.metadata import extractMetadata
    HACHOIR_AVAILABLE = True
except ImportError:
    HACHOIR_AVAILABLE = False

# Enable HEIF support in Pillow
pillow_heif.register_heif_opener()

logger = logging.getLogger(__name__)


class ExifHandler:
    """Handles EXIF data extraction and timestamp conversion for photos and videos."""
    # EXIF timestamp tags in order of preference
    TIMESTAMP_TAGS = [
        "DateTimeOriginal",  # Camera capture time (preferred)
        "DateTimeDigitized",  # File modification time
        "DateTime"  # Digitalization time
    ]
    # Video file extensions that need special handling
    VIDEO_EXTENSIONS = {
        '.mov', '.mp4', '.m4v', '.avi', '.mkv', '.wmv',
        '.flv', '.webm', '.3gp', '.mpg', '.mpeg'
    }

    def __init__(self):
        self.missing_exif_files = []

    def _is_video_file(self, file_path: str) -> bool:
        """Check if the file is a video file."""
        return Path(file_path).suffix.lower() in self.VIDEO_EXTENSIONS

    def extract_timestamp(self, file_path: str) -> Optional[datetime]:
        """
        Extract timestamp from EXIF data (photos) or metadata (videos).

        Args:
            file_path: Path to image or video file

        Returns:
            datetime object if found, None if missing/invalid
        """
        # Handle video files differently
        if self._is_video_file(file_path):
            return self._extract_video_timestamp(file_path)

        # Handle image files with EXIF data
        try:
            with Image.open(file_path) as image:
                exif_data = image.getexif()

                if not exif_data:
                    logger.warning(f"No EXIF data found in {file_path}")
                    self.missing_exif_files.append(file_path)
                    return None

                # Try each timestamp tag in order of preference
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)

                    if tag_name in self.TIMESTAMP_TAGS:
                        return self._parse_exif_datetime(value, file_path)

                logger.warning(
                    f"No timestamp tags found in EXIF data for {file_path}")
                self.missing_exif_files.append(file_path)
                return None

        except Exception as e:
            logger.error(f"Error reading EXIF data from {file_path}: {e}")
            self.missing_exif_files.append(file_path)
            return None

    def _extract_video_timestamp(self, file_path: str) -> Optional[datetime]:
        """
        Extract creation timestamp from video metadata.

        Args:
            file_path: Path to video file

        Returns:
            datetime object if found, None if missing/invalid
        """
        if not HACHOIR_AVAILABLE:
            logger.warning(
                f"Hachoir not available for video metadata extraction: {file_path}")
            self.missing_exif_files.append(file_path)
            return None

        try:
            parser = createParser(file_path)
            if not parser:
                logger.warning(
                    f"Could not create parser for video file: {file_path}")
                self.missing_exif_files.append(file_path)
                return None

            with parser:
                metadata = extractMetadata(parser)
                if not metadata:
                    logger.warning(
                        f"No metadata found in video file: {file_path}")
                    self.missing_exif_files.append(file_path)
                    return None

                # Try to get creation date from various metadata fields
                creation_date = None

                # Common metadata fields for creation date
                for field_name in ['creation_date', 'date', 'creation_time', 'media_creation']:
                    try:
                        if hasattr(metadata, field_name):
                            creation_date = getattr(metadata, field_name)
                            break
                    except:
                        continue

                # If no direct field, try iterating through all metadata
                if not creation_date:
                    for line in metadata.exportPlaintext():
                        line_lower = line.lower()
                        if any(keyword in line_lower for keyword in ['creation', 'date', 'time']):
                            # Extract timestamp from metadata line
                            try:
                                import re
                                # Look for date patterns
                                date_match = re.search(
                                    r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', line)
                                if date_match:
                                    date_str = date_match.group(
                                        1).replace('T', ' ')
                                    creation_date = datetime.strptime(
                                        date_str, '%Y-%m-%d %H:%M:%S')
                                    break
                            except:
                                continue

                if creation_date:
                    logger.info(
                        f"Extracted video creation date: {file_path} -> {creation_date}")
                    return creation_date
                else:
                    logger.warning(
                        f"No creation date found in video metadata: {file_path}")
                    self.missing_exif_files.append(file_path)
                    return None

        except Exception as e:
            logger.error(
                f"Error extracting video metadata from {file_path}: {e}")
            self.missing_exif_files.append(file_path)
            return None

    def _parse_exif_datetime(self, datetime_str: str, file_path: str) -> Optional[datetime]:
        """
        Parse EXIF datetime string to datetime object.

        Args:
            datetime_str: EXIF datetime string (format: "YYYY:MM:DD HH:MM:SS")
            file_path: File path for logging

        Returns:
            datetime object if valid, None if invalid
        """
        try:
            # EXIF datetime format: "YYYY:MM:DD HH:MM:SS"
            return datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
        except ValueError as e:
            logger.error(
                f"Invalid EXIF datetime format in {file_path}: {datetime_str} - {e}")
            self.missing_exif_files.append(file_path)
            return None
