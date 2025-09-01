"""Enterprise Content Ingestion Service - Multi-Format Media Processing
Handles upload, validation, storage, and initial AI processing for all content types

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + Audio Engineer + DevOps Expert

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are proprietary to Fahed Mlaiel.
Unauthorized copying, distribution, or use without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import os
import uuid
import asyncio
import hashlib
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import logging

import aiofiles
from PIL import Image
import magic
from moviepy.editor import VideoFileClip
import librosa
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.app.models.domain import Creator, ContentAsset
from backend.app.core.exceptions import ContentValidationError, StorageError
from backend.app.services.audio_fingerprint_engine import AudioFingerprintEngine
from backend.app.services.video_fingerprint_engine import VideoFingerprintEngine
from backend.app.services.image_fingerprint_engine import ImageFingerprintEngine
from backend.app.services.text_fingerprint_engine import TextFingerprintEngine

logger = logging.getLogger(__name__)


class ContentIngestionService:
    """
    Professional content ingestion service supporting multi-format uploads
    with enterprise-grade validation, storage, and AI processing pipeline
    """

    
    SUPPORTED_FORMATS = {
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'],
        'text': ['.txt', '.md', '.rtf', '.doc', '.docx', '.pdf']
    }
    
    MAX_FILE_SIZES = {
        'audio': 500 * 1024 * 1024,  # 500MB
        'video': 2 * 1024 * 1024 * 1024,  # 2GB
        'image': 50 * 1024 * 1024,  # 50MB
        'text': 10 * 1024 * 1024   # 10MB
    }

    def __init__(self, storage_root: str = "/data/storage") -> None:
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        # Initialize fingerprinting engines
        self.audio_engine = AudioFingerprintEngine()
        self.video_engine = VideoFingerprintEngine()
        self.image_engine = ImageFingerprintEngine()
        self.text_engine = TextFingerprintEngine()
        
        # Content validation settings
        self.virus_scanner_enabled = True
        self.content_moderation_enabled = True

    def _detect_content_type(self, file_path: Path) -> str:
        """Detect content type using file magic and extension validation"""
        try:
            mime_type = magic.from_file(str(file_path), mime=True)
            extension = file_path.suffix.lower()
            
            if mime_type.startswith('audio/') or extension in self.SUPPORTED_FORMATS['audio']:
                return 'audio'
            elif mime_type.startswith('video/') or extension in self.SUPPORTED_FORMATS['video']:
                return 'video'
            elif mime_type.startswith('image/') or extension in self.SUPPORTED_FORMATS['image']:
                return 'image'
            elif mime_type.startswith('text/') or extension in self.SUPPORTED_FORMATS['text']:
                return 'text'
            else:
                raise ContentValidationError(f"Unsupported content type: {mime_type}")
                
        except Exception as e:
            logger.error(f"Content type detection failed: {str(e)}")
            raise ContentValidationError(f"Failed to detect content type: {str(e)}")

    def _validate_file_security(self, file_path: Path, content_type: str) -> bool:
        """Enterprise security validation including virus scanning"""
        try:
            # Check file size limits
            file_size = file_path.stat().st_size
            if file_size > self.MAX_FILE_SIZES.get(content_type, 0):
                raise ContentValidationError(f"File size exceeds limit for {content_type}")
            
            # Basic malware patterns check
            if self.virus_scanner_enabled:
                with open(file_path, 'rb') as f:
                    content = f.read(1024)  # First 1KB check
                    suspicious_patterns = [b'<script', b'javascript:', b'vbscript:', b'<?php']
                    if any(pattern in content.lower() for pattern in suspicious_patterns):
                        raise ContentValidationError("Suspicious content detected")
            
            return True
            
        except Exception as e:
            logger.error(f"Security validation failed: {str(e)}")
            raise ContentValidationError(f"Security validation failed: {str(e)}")

    async def _extract_content_metadata(self, file_path: Path, content_type: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from content files"""
        metadata = {
            'file_size': file_path.stat().st_size,
            'created_at': datetime.now().isoformat(),
            'mime_type': magic.from_file(str(file_path), mime=True),
            'file_hash': self._calculate_file_hash(file_path)
        }
        
        try:
            if content_type == 'audio':
                metadata.update(await self._extract_audio_metadata(file_path))
            elif content_type == 'video':
                metadata.update(await self._extract_video_metadata(file_path))
            elif content_type == 'image':
                metadata.update(await self._extract_image_metadata(file_path))
            elif content_type == 'text':
                metadata.update(await self._extract_text_metadata(file_path))
                
        except Exception as e:
            logger.warning(f"Metadata extraction failed for {content_type}: {str(e)}")
            metadata['metadata_error'] = str(e)
            
        return metadata

    async def _extract_audio_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract audio-specific metadata using librosa"""
        try:
            y, sr = librosa.load(str(file_path))
            duration = len(y) / sr
            
            # Audio features
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            zero_crossings = librosa.feature.zero_crossing_rate(y)
            
            return {
                'duration': float(duration),
                'sample_rate': sr,
                'tempo': float(tempo),
                'spectral_centroid_mean': float(np.mean(spectral_centroids)),
                'zero_crossing_rate_mean': float(np.mean(zero_crossings)),
                'audio_channels': y.shape[0] if y.ndim > 1 else 1
            }
        except Exception as e:
            logger.error(f"Audio metadata extraction failed: {str(e)}")
            return {'audio_metadata_error': str(e)}

    async def _extract_video_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract video-specific metadata using moviepy"""
        try:
            with VideoFileClip(str(file_path)) as clip:
                return {
                    'duration': float(clip.duration),
                    'fps': float(clip.fps),
                    'width': int(clip.w),
                    'height': int(clip.h),
                    'aspect_ratio': float(clip.w / clip.h),
                    'has_audio': clip.audio is not None
                }
        except Exception as e:
            logger.error(f"Video metadata extraction failed: {str(e)}")
            return {'video_metadata_error': str(e)}

    async def _extract_image_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract image-specific metadata using PIL"""
        try:
            with Image.open(file_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format,
                    'aspect_ratio': float(img.width / img.height),
                    'has_transparency': img.mode in ('RGBA', 'LA', 'P')
                }
        except Exception as e:
            logger.error(f"Image metadata extraction failed: {str(e)}")
            return {'image_metadata_error': str(e)}

    async def _extract_text_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract text-specific metadata"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                
            words = len(content.split())
            characters = len(content)
            lines = len(content.splitlines())
            
            return {
                'word_count': words,
                'character_count': characters,
                'line_count': lines,
                'language_detected': 'en'  # Would integrate language detection
            }
        except Exception as e:
            logger.error(f"Text metadata extraction failed: {str(e)}")
            return {'text_metadata_error': str(e)}

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file for integrity verification"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def _reserve_storage_path(self, creator_email: str, filename: str, content_type: str) -> Path:
        """Generate secure storage path with proper organization"""
        ext = Path(filename).suffix
        unique_id = f"{uuid.uuid4().hex}{ext}"
        safe_email = creator_email.replace("@", "_").replace(".", "_")
        
        # Organize by content type and date
        date_folder = datetime.now().strftime("%Y/%m")
        storage_path = self.storage_root / safe_email / content_type / date_folder / unique_id
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        return storage_path

    async def _generate_content_fingerprint(self, file_path: Path, content_type: str) -> Optional[str]:
        """Generate AI fingerprint for content protection"""
        try:
            if content_type == 'audio':
                return await self.audio_engine.generate_fingerprint(str(file_path))
            elif content_type == 'video':
                return await self.video_engine.generate_fingerprint(str(file_path))
            elif content_type == 'image':
                return await self.image_engine.generate_fingerprint(str(file_path))
            elif content_type == 'text':
                return await self.text_engine.generate_fingerprint(str(file_path))
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {str(e)}")
            return None

    async def persist_upload(
        self, 
        db: Session, 
        creator_email: str, 
        title: str, 
        filename: str, 
        data: bytes, 
        metadata: Optional[Dict] = None
    ) -> Tuple[Creator, ContentAsset]:
        """
        Enterprise upload persistence with comprehensive processing pipeline
        """
        try:
            # Create temporary file for processing
            temp_path = Path(f"/tmp/{uuid.uuid4().hex}_{filename}")
            
            async with aiofiles.open(temp_path, 'wb') as f:
                await f.write(data)
            
            try:
                # Detect and validate content
                content_type = self._detect_content_type(temp_path)
                self._validate_file_security(temp_path, content_type)
                
                # Extract comprehensive metadata
                extracted_metadata = await self._extract_content_metadata(temp_path, content_type)
                if metadata:
                    extracted_metadata.update(metadata)
                
                # Get or create creator
                creator = db.query(Creator).filter(Creator.email == creator_email).first()
                if not creator:
                    creator = Creator(
                        name=creator_email.split("@")[0], 
                        email=creator_email,
                        created_at=datetime.now()
                    )
                    db.add(creator)
                    db.flush()
                
                # Store file in organized structure
                final_path = self._reserve_storage_path(creator_email, filename, content_type)
                
                async with aiofiles.open(temp_path, 'rb') as src, aiofiles.open(final_path, 'wb') as dst:
                    content = await src.read()
                    await dst.write(content)
                
                # Generate AI fingerprint for protection
                fingerprint = await self._generate_content_fingerprint(final_path, content_type)
                if fingerprint:
                    extracted_metadata['ai_fingerprint'] = fingerprint
                
                # Create content asset record
                asset = ContentAsset(
                    creator_id=creator.id,
                    media_type=content_type,
                    title=title,
                    original_filename=filename,
                    storage_uri=str(final_path),
                    metadata=extracted_metadata,
                    file_hash=extracted_metadata.get('file_hash'),
                    file_size=extracted_metadata.get('file_size'),
                    status='processed',
                    created_at=datetime.now()
                )
                
                db.add(asset)
                db.commit()
                
                logger.info(f"Successfully processed upload: {filename} for {creator_email}")
                return creator, asset
                
            finally:
                # Cleanup temporary file
                if temp_path.exists():
                    temp_path.unlink()
                    
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error during upload: {str(e)}")
            raise StorageError(f"Database error: {str(e)}")
        except Exception as e:
            logger.error(f"Upload processing failed: {str(e)}")
            raise StorageError(f"Upload failed: {str(e)}")

    async def batch_process_uploads(
        self, 
        db: Session, 
        uploads: List[Dict[str, Any]]
    ) -> List[Tuple[Creator, ContentAsset]]:
        """Process multiple uploads in parallel with proper error handling"""
        results = []
        
        async def process_single_upload(upload_data):
            try:
                return await self.persist_upload(
                    db=db,
                    creator_email=upload_data['creator_email'],
                    title=upload_data['title'],
                    filename=upload_data['filename'],
                    data=upload_data['data'],
                    metadata=upload_data.get('metadata')
                )
            except Exception as e:
                logger.error(f"Batch upload failed for {upload_data['filename']}: {str(e)}")
                return None
        
        # Process uploads with concurrency control
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent uploads
        
        async def sem_process(upload_data):
            async with semaphore:
                return await process_single_upload(upload_data)
        
        tasks = [sem_process(upload) for upload in uploads]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        successful_results = [r for r in results if r is not None and not isinstance(r, Exception)]
        
        logger.info(f"Batch processing complete: {len(successful_results)}/{len(uploads)} successful")
        return successful_results

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get comprehensive storage statistics"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_type': {},
            'storage_root': str(self.storage_root)
        }
        
        for content_type in self.SUPPORTED_FORMATS.keys():
            type_path = self.storage_root / "**" / content_type / "**" / "*"
            type_files = list(Path().glob(str(type_path)))
            type_size = sum(f.stat().st_size for f in type_files if f.is_file())
            
            stats['by_type'][content_type] = {
                'count': len(type_files),
                'size': type_size
            }
            stats['total_files'] += len(type_files)
            stats['total_size'] += type_size
        
        return stats
