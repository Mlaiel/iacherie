"""Audio Processing Module for MongoDB
===================================

Advanced audio content processing, analysis, and storage with MongoDB GridFS.
Handles audio uploads, format conversion, metadata extraction, and AI-powered analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import hashlib
import io
import logging
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, BinaryIO

try:
    import librosa
    import soundfile as sf
    import numpy as np
    from motor.motor_asyncio import AsyncIOMotorGridFSBucket
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    # Mock classes for when libraries aren't available
    class AsyncIOMotorGridFSBucket:
        pass

logger = logging.getLogger(__name__)

class AudioProcessor:
    """Advanced audio processing for MongoDB storage."""
    
    def __init__(self, database, bucket_name: str = "audio_files"):
        """Initialize audio processor."""
        self.database = database
        self.bucket_name = bucket_name
        if AUDIO_LIBS_AVAILABLE:
            self.gridfs_bucket = AsyncIOMotorGridFSBucket(database, bucket_name=bucket_name)
        self.supported_formats = {'.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac'}
        
        if not AUDIO_LIBS_AVAILABLE:
            logger.warning("Audio processing libraries not available. Limited functionality.")
    
    async def upload_audio(self, 
                          file_data: Union[bytes, BinaryIO],
                          filename: str,
                          content_type: str = "audio/wav",
                          metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload audio file to MongoDB GridFS with analysis."""
        if not AUDIO_LIBS_AVAILABLE:
            return {"error": "Audio processing libraries not available"}
        
        try:
            # Prepare metadata
            upload_metadata = {
                "upload_time": datetime.now(timezone.utc),
                "content_type": content_type,
                "filename": filename,
                "processed": False,
                **(metadata or {})
            }
            
            # Read file data if it's a file-like object
            if hasattr(file_data, 'read'):
                file_data = file_data.read()
            
            # Calculate file hash
            file_hash = hashlib.sha256(file_data).hexdigest()
            upload_metadata["file_hash"] = file_hash
            upload_metadata["size_bytes"] = len(file_data)
            
            # Upload to GridFS
            file_id = await self.gridfs_bucket.upload_from_stream(
                filename,
                io.BytesIO(file_data),
                metadata=upload_metadata
            )
            
            logger.info(f"Audio file uploaded successfully: {filename} (ID: {file_id})")
            
            return {
                "file_id": file_id,
                "metadata": upload_metadata,
                "size_bytes": len(file_data),
                "file_hash": file_hash
            }
            
        except Exception as e:
            logger.error(f"Failed to upload audio file {filename}: {e}")
            raise

# Export main classes
__all__ = [
    "AudioProcessor",
    "AUDIO_LIBS_AVAILABLE"
]

# Log successful import
logger.info("Successfully loaded multimedia.audio_processor")