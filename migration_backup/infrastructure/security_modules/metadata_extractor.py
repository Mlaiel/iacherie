"""Metadata Extractor - Infrastructure Security Modules
Author: Fahed Mlaiel (mlaiel@live.de)
"""

import os
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def extract_metadata(file_path: str) -> Dict[str, Any]:
    """Extract metadata from file."""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return {}
        
        stat = file_path.stat()
        return {
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'created': stat.st_ctime,
            'extension': file_path.suffix,
            'name': file_path.name,
            'is_file': file_path.is_file(),
            'is_dir': file_path.is_dir()
        }
    except Exception as e:
        logger.error(f"Error extracting metadata from {file_path}: {e}")
        return {}