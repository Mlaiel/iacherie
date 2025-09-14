"""Content Ingestion Pipeline for Multi-Format Creator Content
===========================================================

Professional content ingestion system handling upload, validation, and initial
processing of creator content (audio, video, image, text) with metadata extraction.

Team Specialties:
- Lead Developer AI: Fahed Mlaiel - Advanced pipeline architecture
- Backend Senior Engineer: High-performance file processing
- ML Engineer: Content analysis and metadata extraction
- Audio Engineer: Professional audio format handling
- Security Engineer: Content validation and threat detection

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT WARNING ⚠️
Unauthorized use, copying, or theft of this code is strictly prohibited.
Legal action will be taken against violators.
"""

import asyncio
import logging
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from uuid import uuid4

import aiofiles
from PIL import Image
import cv2
import librosa
import magic
from pydantic import BaseModel, ValidationError

from backend.core.config import get_settings
from backend.core.database import AsyncDatabaseSession
from backend.core.exceptions import (
    ContentIngestionError, 
    UnsupportedFormatError,
    ContentValidationError,
    MetadataExtractionError
)
from backend.data.storage import StorageManager
from backend.data.validators import ContentValidator, SecurityValidator
from backend.models.content import ContentModel, ContentMetadata
from backend.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ContentUploadRequest(BaseModel):
    """
Content upload request model"""
    user_id: int
    content_type: str  # audio, video, image, text
    filename: str
    file_size: int
    mime_type: str
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    privacy_level: str = "private"  # private, public, unlisted


class ContentUploadResponse(BaseModel):
    """Content upload response model"""
    content_id: str
    upload_url: str
    status: str
    metadata: Dict[str, Any]
    processing_id: str


class MultiFormatProcessor:
    """
    Professional multi-format content processor for creator uploads
    """
    
    def __init__(self) -> None:
        self.storage_manager = StorageManager()
        self.content_validator = ContentValidator()
        self.security_validator = SecurityValidator()
        
        # Supported formats configuration
        self.supported_formats = {
            "audio": [".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac"],
            "video": [".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"],
            "image": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"],
            "text": [".txt", ".md", ".docx", ".pdf", ".html"]
        }
        
        # Processing limits
        self.max_file_sizes = {
            "audio": 500 * 1024 * 1024,  # 500MB
            "video": 5 * 1024 * 1024 * 1024,  # 5GB
            "image": 50 * 1024 * 1024,  # 50MB
            "text": 10 * 1024 * 1024  # 10MB
        }

    async def validate_upload(
        self, 
        file_path: Path, 
        request: ContentUploadRequest
    ) -> Dict[str, Any]:
        """
        Validate uploaded content for security and format compliance
        """
        try:
            # Basic file validation
            if not file_path.exists():
                raise ContentValidationError("File not found")
            
            file_size = file_path.stat().st_size
            if file_size != request.file_size:
                raise ContentValidationError("File size mismatch")
            
            # MIME type validation
            detected_mime = magic.from_file(str(file_path), mime=True)
            if detected_mime != request.mime_type:
                logger.warning(
                    f"MIME type mismatch: detected {detected_mime}, "
                    f"declared {request.mime_type}"
                )
            
            # File extension validation
            file_extension = file_path.suffix.lower()
            if file_extension not in self.supported_formats.get(request.content_type, []):
                raise UnsupportedFormatError(
                    f"Unsupported format {file_extension} for {request.content_type}"
                )
            
            # Size limit validation
            max_size = self.max_file_sizes.get(request.content_type, 0)
            if file_size > max_size:
                raise ContentValidationError(
                    f"File size {file_size} exceeds limit {max_size}"
                )
            
            # Security validation
            security_result = await self.security_validator.scan_file(file_path)
            if not security_result.is_safe:
                raise ContentValidationError(
                    f"Security scan failed: {security_result.threats}"
                )
            
            return {
                "status": "valid",
                "detected_mime": detected_mime,
                "file_size": file_size,
                "security_scan": security_result.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Content validation failed: {str(e)}")
            raise ContentValidationError(f"Validation failed: {str(e)}")

    async def extract_metadata(
        self, 
        file_path: Path, 
        content_type: str
    ) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from uploaded content
        """
        try:
            metadata = {
                "file_info": {
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "created_at": datetime.fromtimestamp(
                        file_path.stat().st_ctime
                    ).isoformat(),
                    "modified_at": datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).isoformat()
                }
            }
            
            if content_type == "audio":
                metadata.update(await self._extract_audio_metadata(file_path))
            elif content_type == "video":
                metadata.update(await self._extract_video_metadata(file_path))
            elif content_type == "image":
                metadata.update(await self._extract_image_metadata(file_path))
            elif content_type == "text":
                metadata.update(await self._extract_text_metadata(file_path))
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            raise MetadataExtractionError(f"Metadata extraction failed: {str(e)}")

    async def _extract_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract audio-specific metadata"""
        try:
            # Load audio for analysis
            y, sr = librosa.load(str(file_path), sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Extract audio features
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
            mfccs = librosa.feature.mfcc(y=y, sr=sr)
            
            return {
                "audio": {
                    "duration": float(duration),
                    "sample_rate": int(sr),
                    "channels": 1 if len(y.shape) == 1 else y.shape[0],
                    "tempo": float(tempo),
                    "spectral_centroid_mean": float(spectral_centroids.mean()),
                    "zero_crossing_rate_mean": float(zero_crossing_rate.mean()),
                    "mfcc_mean": mfccs.mean(axis=1).tolist(),
                    "energy": float((y ** 2).sum())
                }
            }
            
        except Exception as e:
            logger.error(f"Audio metadata extraction failed: {str(e)}")
            return {"audio": {"error": str(e)}}

    async def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract video-specific metadata"""
        try:
            cap = cv2.VideoCapture(str(file_path))
            
            # Basic video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Sample frames for analysis
            frames_analyzed = 0
            brightness_values = []
            
            while frames_analyzed < 10 and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Calculate frame brightness
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = gray.mean()
                brightness_values.append(brightness)
                frames_analyzed += 1
                
                # Skip frames for sampling
                for _ in range(max(1, frame_count // 10)):
                    cap.read()
            
            cap.release()
            
            return {
                "video": {
                    "duration": float(duration),
                    "fps": float(fps),
                    "frame_count": frame_count,
                    "width": width,
                    "height": height,
                    "aspect_ratio": width / height if height > 0 else 0,
                    "resolution": f"{width}x{height}",
                    "average_brightness": float(sum(brightness_values) / len(brightness_values)) 
                        if brightness_values else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Video metadata extraction failed: {str(e)}")
            return {"video": {"error": str(e)}}

    async def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract image-specific metadata"""
        try:
            with Image.open(file_path) as img:
                # Basic image properties
                width, height = img.size
                mode = img.mode
                format_type = img.format
                
                # EXIF data if available
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = dict(img._getexif().items())
                
                # Color analysis
                if mode == 'RGB':
                    # Convert to numpy array for analysis
                    import numpy as np
                    img_array = np.array(img)
                    
                    # Calculate color statistics
                    mean_color = img_array.mean(axis=(0, 1)).tolist()
                    std_color = img_array.std(axis=(0, 1)).tolist()
                else:
                    mean_color = []
                    std_color = []
                
                return {
                    "image": {
                        "width": width,
                        "height": height,
                        "mode": mode,
                        "format": format_type,
                        "aspect_ratio": width / height if height > 0 else 0,
                        "resolution": f"{width}x{height}",
                        "pixel_count": width * height,
                        "mean_color": mean_color,
                        "std_color": std_color,
                        "has_exif": bool(exif_data),
                        "exif_keys": list(exif_data.keys()) if exif_data else []
                    }
                }
                
        except Exception as e:
            logger.error(f"Image metadata extraction failed: {str(e)}")
            return {"image": {"error": str(e)}}

    async def _extract_text_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract text-specific metadata"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Basic text statistics
            char_count = len(content)
            word_count = len(content.split())
            line_count = content.count('\n') + 1
            
            # Language detection (simplified)
            import re
            
            # Count different character types
            alpha_count = len(re.findall(r'[a-zA-Z]', content))
            digit_count = len(re.findall(r'[0-9]', content))
            space_count = content.count(' ')
            
            return {
                "text": {
                    "character_count": char_count,
                    "word_count": word_count,
                    "line_count": line_count,
                    "alpha_count": alpha_count,
                    "digit_count": digit_count,
                    "space_count": space_count,
                    "alpha_ratio": alpha_count / char_count if char_count > 0 else 0,
                    "avg_word_length": char_count / word_count if word_count > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Text metadata extraction failed: {str(e)}")
            return {"text": {"error": str(e)}}


class ContentIngestionPipeline:
    """
    Professional content ingestion pipeline orchestrating the complete
    upload, validation, processing, and storage workflow
    """
    
    def __init__(self) -> None:
        self.processor = MultiFormatProcessor()
        self.storage_manager = StorageManager()
        
    async def process_upload(
        self, 
        file_data: bytes, 
        request: ContentUploadRequest
    ) -> ContentUploadResponse:
        """
        Complete content upload processing pipeline
        """
        processing_id = str(uuid4())
        content_id = str(uuid4())
        
        try:
            logger.info(
                f"Starting content ingestion for user {request.user_id}, "
                f"processing_id: {processing_id}"
            )
            
            # Step 1: Create temporary file
            temp_file_path = await self._create_temp_file(
                file_data, request.filename, processing_id
            )
            
            try:
                # Step 2: Validate content
                validation_result = await self.processor.validate_upload(
                    temp_file_path, request
                )
                
                if validation_result["status"] != "valid":
                    raise ContentValidationError("Content validation failed")
                
                # Step 3: Extract metadata
                metadata = await self.processor.extract_metadata(
                    temp_file_path, request.content_type
                )
                
                # Step 4: Store content permanently
                storage_path = await self.storage_manager.store_content(
                    temp_file_path, content_id, request.content_type
                )
                
                # Step 5: Save to database
                content_model = await self._save_content_record(
                    content_id, request, metadata, storage_path
                )
                
                # Step 6: Generate response
                response = ContentUploadResponse(
                    content_id=content_id,
                    upload_url=storage_path,
                    status="completed",
                    metadata=metadata,
                    processing_id=processing_id
                )
                
                logger.info(
                    f"Content ingestion completed successfully for {content_id}"
                )
                
                return response
                
            finally:
                # Cleanup temporary file
                await self._cleanup_temp_file(temp_file_path)
                
        except Exception as e:
            logger.error(
                f"Content ingestion failed for processing_id {processing_id}: {str(e)}"
            )
            raise ContentIngestionError(f"Ingestion failed: {str(e)}")

    async def _create_temp_file(
        self, 
        file_data: bytes, 
        filename: str, 
        processing_id: str
    ) -> Path:
        """Create temporary file for processing"""
        temp_dir = Path(settings.TEMP_UPLOAD_DIR)
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique temporary filename
        file_extension = Path(filename).suffix
        temp_filename = f"{processing_id}_{filename}"
        temp_file_path = temp_dir / temp_filename
        
        # Write file data
        async with aiofiles.open(temp_file_path, 'wb') as f:
            await f.write(file_data)
        
        return temp_file_path

    async def _cleanup_temp_file(self, temp_file_path -> None: Path) -> None:
        """Cleanup temporary file"""
        try:
            if temp_file_path.exists():
                temp_file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {temp_file_path}: {str(e)}")

    async def _save_content_record(
        self,
        content_id: str,
        request: ContentUploadRequest,
        metadata: Dict[str, Any],
        storage_path: str
    ) -> ContentModel:
        """Save content record to database"""
        async with AsyncDatabaseSession() as session:
            content_metadata = ContentMetadata(
                **metadata,
                processing_version="2.0.0",
                ingestion_timestamp=datetime.utcnow()
            )
            
            content_model = ContentModel(
                id=content_id,
                user_id=request.user_id,
                content_type=request.content_type,
                filename=request.filename,
                mime_type=request.mime_type,
                file_size=request.file_size,
                storage_path=storage_path,
                metadata=content_metadata.dict(),
                tags=request.tags or [],
                description=request.description,
                privacy_level=request.privacy_level,
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(content_model)
            await session.commit()
            await session.refresh(content_model)
            
            return content_model

    async def get_ingestion_status(self, processing_id: str) -> Dict[str, Any]:
        """Get ingestion processing status"""
        # Implementation would check processing status from cache/database
        # This is a simplified version
        return {
            "processing_id": processing_id,
            "status": "completed",
            "progress": 100,
            "message": "Content ingestion completed successfully"
        }

    async def list_user_content(
        self, 
        user_id: int, 
        content_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List user's uploaded content"""
        async with AsyncDatabaseSession() as session:
            query = session.query(ContentModel).filter(
                ContentModel.user_id == user_id,
                ContentModel.status == "active"
            )
            
            if content_type:
                query = query.filter(ContentModel.content_type == content_type)
            
            query = query.offset(offset).limit(limit)
            results = await query.all()
            
            return [
                {
                    "content_id": content.id,
                    "content_type": content.content_type,
                    "filename": content.filename,
                    "file_size": content.file_size,
                    "created_at": content.created_at.isoformat(),
                    "tags": content.tags,
                    "description": content.description
                }
                for content in results
            ]
