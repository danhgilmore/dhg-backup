"""
HEIC to JPEG conversion module with EXIF preservation
"""

import os
import logging
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import pillow_heif

# Enable HEIF support in Pillow
pillow_heif.register_heif_opener()

logger = logging.getLogger(__name__)


class HeicConverter:
    """"Handles HEIC to JPEG conversion with EXIF preservation."""

    def __init__(self, jpeg_quality: int = 95):
        """
        Initialize HEIC converter

        Args:
            jpeg_quality: JPEG quality (1-100, default 95 for high quality)
        """
        self.jpeg_quality = jpeg_quality
        self.converted_files = []
        self.failed_conversions = []

    def is_heic_file(self, file_path: str) -> bool:
        """
        Check if file is a HEIC/HEIF file.

        Args:
            file_path: Path to file

        Returns:
            True if file is HEIC/HEIF format
        """
        ext = Path(file_path).suffix.lower()
        return ext in ['.heic', '.heif']

    def convert_heic_to_jpeg(self, heic_path: str, output_dir: str = None) -> Optional[str]:
        """
        Convert HEIC file to JPEG with EXIF preservation.

        Args:
            heic_path: Path to HEIC file
            output_dir: Output directory (default: same as input file)

        Returns:
            Path to converted JPEG file, None if conversion failed
        """
        try:
            if not self.is_heic_file(heic_path):
                logger.warning(f"File is not HEIC format: {heic_path}")
                return None

            # Determine output path
            heic_file = Path(heic_path)
            if output_dir:
                output_path = Path(output_dir) / f"{heic_file.stem}.jpg"
            else:
                output_path = heic_file.parent / f"{heic_file.stem}.jpg"

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Open and convert HEIC image
            with Image.open(heic_path) as image:
                # Convert to RGB if necessary (HEIC can be in different color spaces)
                if image.mode not in ['RGB', 'L']:
                    image = image.convert('RGB')

                # Get EXIF data before conversion
                exif_data = image.getexif()

                # Save as JPEG with EXIF preservation
                save_kwargs = {
                    'format': 'JPEG',
                    'quality': self.jpeg_quality,
                    'optimize': True
                }

                # Preserve EXIF data if present
                if exif_data:
                    save_kwargs['exif'] = exif_data

                image.save(output_path, **save_kwargs)

            logger.info(
                f"Successfully converted HEIC to JPEG: {heic_path} -> {output_path}")
            self.converted_files.append((heic_path, str(output_path)))
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to convert HEIC file {heic_path}: {e}")
            self.failed_conversions.append((heic_path, str(e)))
            return None
