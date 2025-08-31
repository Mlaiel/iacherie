"""
Professional File Manager - IA Influencer Agent Platform
========================================================
Module: backend/data/storage/file_manager.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Data Storage Core - Professional File Management
Responsibility: Multi-format file handling for content protection & monetization
Technologies: Python, FastAPI, Multi-cloud, Content-aware optimization
========================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET:
- Lead Dev IA + Architecte: Fahed Mlaiel
- Backend Senior + ML Engineer: Expertise multi-domaines  
- Audio + DevOps + DBA + Sécurité: Compétences industrielles
- Microservices + IA Prompt Engineer: Innovation avancée

LOGIQUE MÉTIER:
Content Upload → File Validation → Format Detection → 
Security Scan → Storage Optimization → Fingerprint Generation → 
Metadata Extraction → Multi-provider Storage → Access Control
"""

import asyncio
import logging
import mimetypes
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from dataclasses import dataclass, field
from enum import Enum
import magic
import os
import aiofiles
import tempfile
import shutil
import json
from urllib.parse import urlparse
import uuid
import stat
from concurrent.futures import ThreadPoolExecutor

# AI and ML libraries for content analysis
import cv2
import numpy as np
from PIL import Image, ExifTags
import librosa
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC
import soundfile as sf

# Security and validation
import pydantic
from pydantic import BaseModel, validator
import bleach
import requests

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Professional content type enumeration for multi-format platform"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"


class FileStatus(Enum):
    """File processing status enumeration"""
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    PROCESSING = "processing"
    FINGERPRINTING = "fingerprinting"
    PROTECTED = "protected"
    PUBLISHED = "published"
    ERROR = "error"
    QUARANTINED = "quarantined"


class CompressionLevel(Enum):
    """Compression optimization levels"""
    NONE = "none"
    LIGHT = "light"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    MAXIMUM = "maximum"


@dataclass
class FileMetadata:
    """Comprehensive file metadata structure"""
    file_id: str
    original_filename: str
    file_size: int
    content_type: ContentType
    mime_type: str
    file_hash: str
    upload_timestamp: datetime
    user_id: str
    
    # Content-specific metadata
    dimensions: Optional[Tuple[int, int]] = None
    duration: Optional[float] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    resolution: Optional[str] = None
    format_version: Optional[str] = None
    
    # Security metadata
    virus_scan_result: Optional[str] = None
    content_policy_check: Optional[Dict[str, bool]] = None
    adult_content_score: Optional[float] = None
    
    # Processing metadata
    status: FileStatus = FileStatus.UPLOADED
    compression_applied: Optional[CompressionLevel] = None
    optimization_savings: Optional[float] = None
    fingerprint_hash: Optional[str] = None
    
    # Platform metadata
    tags: List[str] = field(default_factory=list)
    description: Optional[str] = None
    copyright_info: Optional[Dict[str, Any]] = None
    licensing_terms: Optional[Dict[str, Any]] = None
    
    # Technical metadata
    exif_data: Optional[Dict[str, Any]] = None
    codec_info: Optional[Dict[str, Any]] = None
    container_format: Optional[str] = None
    
    # Access control
    access_level: str = "private"
    shared_with: List[str] = field(default_factory=list)
    download_permissions: Dict[str, bool] = field(default_factory=dict)


@dataclass
class FileValidationResult:
    """File validation result structure"""
    is_valid: bool
    content_type: ContentType
    mime_type: str
    file_size: int
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    security_issues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FileProcessingResult:
    """File processing operation result"""
    success: bool
    file_id: str
    processed_path: Optional[str] = None
    thumbnails: List[str] = field(default_factory=list)
    optimized_versions: Dict[str, str] = field(default_factory=dict)
    extracted_metadata: Optional[FileMetadata] = None
    processing_time: float = 0.0
    error_message: Optional[str] = None


class FileValidationConfig(BaseModel):
    """Configuration for file validation rules"""
    max_file_size: int = 500 * 1024 * 1024  # 500MB default
    allowed_mime_types: List[str] = [
        # Audio
        "audio/mpeg", "audio/wav", "audio/flac", "audio/aac", "audio/ogg",
        "audio/mp4", "audio/x-ms-wma", "audio/webm",
        # Video
        "video/mp4", "video/mpeg", "video/quicktime", "video/x-msvideo",
        "video/webm", "video/x-flv", "video/3gpp", "video/x-ms-wmv",
        # Images
        "image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml",
        "image/tiff", "image/bmp", "image/x-icon",
        # Documents
        "application/pdf", "text/plain", "text/markdown", "application/json",
        "application/xml", "text/csv",
        # Archives
        "application/zip", "application/x-rar-compressed", "application/x-7z-compressed"
    ]
    scan_for_malware: bool = True
    check_content_policy: bool = True
    extract_metadata: bool = True
    generate_thumbnails: bool = True
    auto_optimize: bool = True


class FileManager:
    """
    Industrial-grade file manager for IA Influencer Agent platform.
    
    Handles multi-format content upload, validation, processing, and optimization
    for creators across music, video, image, and text content types.
    """
    
    def __init__(self, 
                 storage_path: Union[str, Path] = "/tmp/ia_influencer_storage",
                 validation_config: Optional[FileValidationConfig] = None):
        """
        Initialize FileManager with professional configuration.
        
        Args:
            storage_path: Base path for file storage
            validation_config: File validation configuration
        """
        self.storage_path = Path(storage_path)
        self.validation_config = validation_config or FileValidationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize storage directories
        self._create_storage_structure()
        
        # Thread pool for CPU-intensive operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Content type detection
        self.magic_detector = magic.Magic(mime=True)
        
        # Processing statistics
        self.stats = {
            "files_processed": 0,
            "total_size_processed": 0,
            "processing_errors": 0,
            "optimization_savings": 0.0
        }
        
        self.logger.info(" FileManager initialized with industrial-grade capabilities")
    
    def _create_storage_structure(self):
        """Create organized storage directory structure"""
        directories = [
            "uploads/pending",
            "uploads/processing", 
            "uploads/completed",
            "uploads/quarantine",
            "processed/originals",
            "processed/optimized",
            "processed/thumbnails",
            "processed/previews",
            "metadata",
            "temp",
            "backup"
        ]
        
        for directory in directories:
            (self.storage_path / directory).mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f" Storage structure created at {self.storage_path}")
    
    async def upload_file(self,
                         file_data: Union[bytes, BinaryIO],
                         filename: str,
                         user_id: str,
                         metadata: Optional[Dict[str, Any]] = None) -> FileProcessingResult:
        """
        Upload and process file with comprehensive validation and optimization.
        
        Args:
            file_data: File content as bytes or file-like object
            filename: Original filename
            user_id: User identifier
            metadata: Optional additional metadata
            
        Returns:
            Complete file processing result
        """



        try:
            start_time = datetime.now()
            
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Save temporary file
            temp_path = await self._save_temp_file(file_data, filename, file_id)
            
            # Validate file
            validation_result = await self._validate_file(temp_path, filename)
            if not validation_result.is_valid:
                await self._quarantine_file(temp_path, file_id, validation_result.errors)
                return FileProcessingResult(
                    success=False,
                    file_id=file_id,
                    error_message=f"Validation failed: {', '.join(validation_result.errors)}"
                )
            
            # Move to processing directory
            processing_path = await self._move_to_processing(temp_path, file_id)
            
            # Extract comprehensive metadata
            file_metadata = await self._extract_metadata(
                processing_path, filename, user_id, file_id, validation_result
            )
            
            # Process based on content type
            processed_result = await self._process_by_content_type(
                processing_path, file_metadata
            )
            
            # Move to completed directory
            final_path = await self._move_to_completed(processing_path, file_id)
            
            # Save metadata
            await self._save_metadata(file_metadata)
            
            # Update statistics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_stats(file_metadata, processing_time)
            
            self.logger.info(f" File processed successfully: {file_id} in {processing_time:.2f}s")
            
            return FileProcessingResult(
                success=True,
                file_id=file_id,
                processed_path=str(final_path),
                thumbnails=processed_result.get("thumbnails", []),
                optimized_versions=processed_result.get("optimized_versions", {}),
                extracted_metadata=file_metadata,
                processing_time=processing_time
            )
            
        except Exception as e:
            self.logger.error(f" File upload failed: {str(e)}")
            return FileProcessingResult(
                success=False,
                file_id=file_id if 'file_id' in locals() else "unknown",
                error_message=str(e)
            )
    
    async def _save_temp_file(self, file_data: Union[bytes, BinaryIO], 
                             filename: str, file_id: str) -> Path:
        """Save uploaded file to temporary location"""
        if hasattr(file_data, 'read'):
            content = file_data.read()
            if hasattr(file_data, 'seek'):
                file_data.seek(0)
        else:
            content = file_data
        
        # Create safe filename
        safe_filename = self._sanitize_filename(filename)
        temp_path = self.storage_path / "uploads" / "pending" / f"{file_id}_{safe_filename}"
        
        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(content)
        
        return temp_path
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove dangerous characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
        safe_filename = ''.join(c for c in filename if c in safe_chars)
        
        # Ensure reasonable length
        if len(safe_filename) > 100:
            name, ext = os.path.splitext(safe_filename)
            safe_filename = name[:95] + ext
        
        return safe_filename or "unknown_file"
    
    async def _validate_file(self, file_path: Path, filename: str) -> FileValidationResult:
        """Comprehensive file validation with security checks"""



        try:
            file_size = file_path.stat().st_size
            warnings = []
            errors = []
            security_issues = []
            
            # Size check
            if file_size > self.validation_config.max_file_size:
                errors.append(f"File too large: {file_size} bytes > {self.validation_config.max_file_size}")
            
            if file_size == 0:
                errors.append("Empty file not allowed")
            
            # MIME type detection
            mime_type = await self._detect_mime_type(file_path)
            if mime_type not in self.validation_config.allowed_mime_types:
                errors.append(f"MIME type not allowed: {mime_type}")
            
            # Content type classification
            content_type = self._classify_content_type(mime_type)
            
            # Security scans
            if self.validation_config.scan_for_malware:
                malware_result = await self._scan_for_malware(file_path)
                if malware_result.get("threat_found"):
                    security_issues.append(f"Malware detected: {malware_result.get('threat_name')}")
                    errors.append("File contains malicious content")
            
            # Content policy check
            if self.validation_config.check_content_policy:
                policy_result = await self._check_content_policy(file_path, content_type)
                if policy_result.get("violations"):
                    warnings.extend(policy_result["violations"])
            
            # File integrity check
            integrity_check = await self._check_file_integrity(file_path, content_type)
            if not integrity_check["valid"]:
                errors.append(f"File integrity check failed: {integrity_check['reason']}")
            
            return FileValidationResult(
                is_valid=len(errors) == 0,
                content_type=content_type,
                mime_type=mime_type,
                file_size=file_size,
                warnings=warnings,
                errors=errors,
                security_issues=security_issues,
                metadata={"integrity_check": integrity_check}
            )
            
        except Exception as e:
            return FileValidationResult(
                is_valid=False,
                content_type=ContentType.UNKNOWN,
                mime_type="unknown",
                file_size=0,
                errors=[f"Validation error: {str(e)}"]
            )
    
    async def _detect_mime_type(self, file_path: Path) -> str:
        """Detect MIME type using multiple methods for accuracy"""



        try:
            # Primary: python-magic
            mime_type = self.magic_detector.from_file(str(file_path))
            
            # Fallback: mimetypes module
            if not mime_type or mime_type == "application/octet-stream":
                fallback_mime, _ = mimetypes.guess_type(str(file_path))
                if fallback_mime:
                    mime_type = fallback_mime
            
            # Content-based detection for media files
            if mime_type.startswith(('audio/', 'video/', 'image/')):
                verified_mime = await self._verify_media_mime_type(file_path, mime_type)
                if verified_mime:
                    mime_type = verified_mime
            
            return mime_type or "application/octet-stream"
            
        except Exception as e:
            self.logger.warning(f"MIME type detection failed: {e}")
            return "application/octet-stream"
    
    def _classify_content_type(self, mime_type: str) -> ContentType:
        """Classify content type from MIME type"""
        if mime_type.startswith('audio/'):
            return ContentType.AUDIO
        elif mime_type.startswith('video/'):
            return ContentType.VIDEO
        elif mime_type.startswith('image/'):
            return ContentType.IMAGE
        elif mime_type.startswith('text/') or mime_type in ['application/json', 'application/xml']:
            return ContentType.TEXT
        elif mime_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument']:
            return ContentType.DOCUMENT
        elif mime_type in ['application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed']:
            return ContentType.ARCHIVE
        else:
            return ContentType.UNKNOWN
    
    async def _verify_media_mime_type(self, file_path: Path, detected_mime: str) -> Optional[str]:
        """Verify MIME type for media files using content analysis"""



        try:
            if detected_mime.startswith('audio/'):
                return await self._verify_audio_mime(file_path)
            elif detected_mime.startswith('video/'):
                return await self._verify_video_mime(file_path)
            elif detected_mime.startswith('image/'):
                return await self._verify_image_mime(file_path)
            return None
        except Exception as e:
            self.logger.warning(f"Media MIME verification failed: {e}")
            return None
    
    async def _verify_audio_mime(self, file_path: Path) -> Optional[str]:
        """Verify audio file MIME type using librosa"""



        try:
            # Use soundfile for initial check
            info = sf.info(str(file_path))
            if info.format.lower() == 'wav':
                return 'audio/wav'
            elif info.format.lower() == 'flac':
                return 'audio/flac'
            elif info.format.lower() in ['mp3', 'mpeg']:
                return 'audio/mpeg'
            elif info.format.lower() == 'aac':
                return 'audio/aac'
            elif info.format.lower() == 'ogg':
                return 'audio/ogg'
            return None
        except:
            return None
    
    async def _verify_video_mime(self, file_path: Path) -> Optional[str]:
        """Verify video file MIME type using OpenCV"""



        try:
            cap = cv2.VideoCapture(str(file_path))
            if cap.isOpened():
                # Get codec information
                fourcc = cap.get(cv2.CAP_PROP_FOURCC)
                cap.release()
                
                # Basic classification based on common containers
                suffix = file_path.suffix.lower()
                if suffix == '.mp4':
                    return 'video/mp4'
                elif suffix == '.avi':
                    return 'video/x-msvideo'
                elif suffix == '.mov':
                    return 'video/quicktime'
                elif suffix == '.webm':
                    return 'video/webm'
                elif suffix == '.mkv':
                    return 'video/x-matroska'
            return None
        except:
            return None
    
    async def _verify_image_mime(self, file_path: Path) -> Optional[str]:
        """Verify image file MIME type using PIL"""



        try:
            with Image.open(file_path) as img:
                format_lower = img.format.lower()
                if format_lower == 'jpeg':
                    return 'image/jpeg'
                elif format_lower == 'png':
                    return 'image/png'
                elif format_lower == 'gif':
                    return 'image/gif'
                elif format_lower == 'webp':
                    return 'image/webp'
                elif format_lower == 'tiff':
                    return 'image/tiff'
                elif format_lower == 'bmp':
                    return 'image/bmp'
            return None
        except:
            return None
    
    async def _scan_for_malware(self, file_path: Path) -> Dict[str, Any]:
        """Malware scanning simulation (integrate with real scanner in production)"""



        try:
            # In production, integrate with ClamAV, VirusTotal API, or similar
            # For now, implement basic suspicious pattern detection
            
            file_size = file_path.stat().st_size
            
            # Check for suspicious file sizes (empty or extremely large)
            if file_size == 0:
                return {"threat_found": True, "threat_name": "Empty file"}
            
            if file_size > 1024 * 1024 * 1024:  # 1GB
                return {"threat_found": True, "threat_name": "Suspicious large file"}
            
            # Check for double extensions
            if file_path.name.count('.') > 2:
                return {"threat_found": True, "threat_name": "Suspicious multiple extensions"}
            
            # Basic signature check for known malicious patterns
            suspicious_patterns = [b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR']  # EICAR test signature
            
            async with aiofiles.open(file_path, 'rb') as f:
                chunk = await f.read(1024)  # Read first 1KB
                for pattern in suspicious_patterns:
                    if pattern in chunk:
                        return {"threat_found": True, "threat_name": "EICAR test signature"}
            
            return {"threat_found": False, "scan_timestamp": datetime.now().isoformat()}
            
        except Exception as e:
            self.logger.error(f"Malware scan error: {e}")
            return {"threat_found": False, "error": str(e)}
    
    async def _check_content_policy(self, file_path: Path, content_type: ContentType) -> Dict[str, Any]:
        """Content policy verification for platform compliance"""
        violations = []
        
        try:
            if content_type == ContentType.IMAGE:
                # Basic adult content detection for images
                violations.extend(await self._check_image_content_policy(file_path))
            elif content_type == ContentType.TEXT:
                # Text content moderation
                violations.extend(await self._check_text_content_policy(file_path))
            elif content_type in [ContentType.AUDIO, ContentType.VIDEO]:
                # Media content basic checks
                violations.extend(await self._check_media_content_policy(file_path))
            
            return {
                "violations": violations,
                "check_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Content policy check failed: {e}")
            return {"violations": [], "error": str(e)}
    
    async def _check_image_content_policy(self, file_path: Path) -> List[str]:
        """Image content policy checks"""
        violations = []
        
        try:
            with Image.open(file_path) as img:
                # Check image dimensions for suspicious aspect ratios
                width, height = img.size
                aspect_ratio = width / height if height > 0 else 0
                
                if aspect_ratio > 10 or aspect_ratio < 0.1:
                    violations.append("Suspicious image aspect ratio")
                
                # Check for extremely small images (possible tracking pixels)
                if width * height < 100:
                    violations.append("Suspicious small image dimensions")
                
                # Check for metadata that might contain inappropriate content
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    if exif and any(key in str(exif.get(270, "")) for key in ["adult", "nsfw", "xxx"]):
                        violations.append("Inappropriate content markers in metadata")
            
        except Exception as e:
            self.logger.warning(f"Image content check error: {e}")
        
        return violations
    
    async def _check_text_content_policy(self, file_path: Path) -> List[str]:
        """Text content policy checks"""
        violations = []
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = await f.read(10000)  # Read first 10KB
                
                # Basic profanity and harmful content detection
                harmful_keywords = [
                    "spam", "scam", "phishing", "malware", "virus",
                    "hack", "crack", "pirated", "illegal", "copyright violation"
                ]
                
                content_lower = content.lower()
                for keyword in harmful_keywords:
                    if keyword in content_lower:
                        violations.append(f"Potentially harmful content detected: {keyword}")
                
                # Check for excessive special characters (potential spam)
                special_char_ratio = sum(1 for c in content if not c.isalnum() and not c.isspace()) / len(content)
                if special_char_ratio > 0.3:
                    violations.append("Excessive special characters (potential spam)")
                
        except Exception as e:
            self.logger.warning(f"Text content check error: {e}")
        
        return violations
    
    async def _check_media_content_policy(self, file_path: Path) -> List[str]:
        """Media content policy checks"""
        violations = []
        
        try:
            file_size = file_path.stat().st_size
            
            # Check for suspiciously large files
            if file_size > 500 * 1024 * 1024:  # 500MB
                violations.append("Unusually large media file")
            
            # Check for filename patterns
            filename_lower = file_path.name.lower()
            suspicious_patterns = ["crack", "keygen", "patch", "hack", "pirated"]
            
            for pattern in suspicious_patterns:
                if pattern in filename_lower:
                    violations.append(f"Suspicious filename pattern: {pattern}")
            
        except Exception as e:
            self.logger.warning(f"Media content check error: {e}")
        
        return violations
    
    async def _check_file_integrity(self, file_path: Path, content_type: ContentType) -> Dict[str, Any]:
        """Check file integrity based on content type"""



        try:
            if content_type == ContentType.AUDIO:
                return await self._check_audio_integrity(file_path)
            elif content_type == ContentType.VIDEO:
                return await self._check_video_integrity(file_path)
            elif content_type == ContentType.IMAGE:
                return await self._check_image_integrity(file_path)
            else:
                return {"valid": True, "reason": "Basic file checks passed"}
                
        except Exception as e:
            return {"valid": False, "reason": f"Integrity check failed: {str(e)}"}
    
    async def _check_audio_integrity(self, file_path: Path) -> Dict[str, Any]:
        """Check audio file integrity"""



        try:
            # Use soundfile to verify audio file structure
            info = sf.info(str(file_path))
            
            if info.frames <= 0:
                return {"valid": False, "reason": "Audio file has no frames"}
            
            if info.samplerate <= 0:
                return {"valid": False, "reason": "Invalid sample rate"}
            
            if info.channels <= 0:
                return {"valid": False, "reason": "Invalid channel count"}
            
            # Try to read a small portion to verify readability
            data, sr = sf.read(str(file_path), frames=1024)
            
            return {"valid": True, "info": {
                "frames": info.frames,
                "sample_rate": info.samplerate,
                "channels": info.channels,
                "duration": info.frames / info.samplerate
            }}
            
        except Exception as e:
            return {"valid": False, "reason": f"Audio integrity check failed: {str(e)}"}
    
    async def _check_video_integrity(self, file_path: Path) -> Dict[str, Any]:
        """Check video file integrity"""



        try:
            cap = cv2.VideoCapture(str(file_path))
            
            if not cap.isOpened():
                return {"valid": False, "reason": "Cannot open video file"}
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            cap.release()
            
            if frame_count <= 0:
                return {"valid": False, "reason": "Video has no frames"}
            
            if fps <= 0:
                return {"valid": False, "reason": "Invalid frame rate"}
            
            if width <= 0 or height <= 0:
                return {"valid": False, "reason": "Invalid video dimensions"}
            
            return {"valid": True, "info": {
                "frame_count": frame_count,
                "fps": fps,
                "width": width,
                "height": height,
                "duration": frame_count / fps if fps > 0 else 0
            }}
            
        except Exception as e:
            return {"valid": False, "reason": f"Video integrity check failed: {str(e)}"}
    
    async def _check_image_integrity(self, file_path: Path) -> Dict[str, Any]:
        """Check image file integrity"""



        try:
            with Image.open(file_path) as img:
                img.verify()  # Verify image integrity
                
            # Re-open for info extraction (verify() closes the image)
            with Image.open(file_path) as img:
                width, height = img.size
                mode = img.mode
                format_name = img.format
                
                if width <= 0 or height <= 0:
                    return {"valid": False, "reason": "Invalid image dimensions"}
                
                return {"valid": True, "info": {
                    "width": width,
                    "height": height,
                    "mode": mode,
                    "format": format_name
                }}
                
        except Exception as e:
            return {"valid": False, "reason": f"Image integrity check failed: {str(e)}"}
    
    async def _quarantine_file(self, file_path: Path, file_id: str, errors: List[str]):
        """Move suspicious or invalid files to quarantine"""



        try:
            quarantine_path = self.storage_path / "uploads" / "quarantine" / f"{file_id}_{file_path.name}"
            shutil.move(str(file_path), str(quarantine_path))
            
            # Log quarantine details
            quarantine_log = {
                "file_id": file_id,
                "original_name": file_path.name,
                "quarantine_timestamp": datetime.now().isoformat(),
                "reasons": errors
            }
            
            log_path = self.storage_path / "uploads" / "quarantine" / f"{file_id}_log.json"
            async with aiofiles.open(log_path, 'w') as f:
                await f.write(json.dumps(quarantine_log, indent=2))
            
            self.logger.warning(f" File quarantined: {file_id} - Reasons: {', '.join(errors)}")
            
        except Exception as e:
            self.logger.error(f"Failed to quarantine file {file_id}: {e}")
    
    async def _move_to_processing(self, temp_path: Path, file_id: str) -> Path:
        """Move file to processing directory"""
        processing_path = self.storage_path / "uploads" / "processing" / f"{file_id}_{temp_path.name}"
        shutil.move(str(temp_path), str(processing_path))
        return processing_path
    
    async def _move_to_completed(self, processing_path: Path, file_id: str) -> Path:
        """Move file to completed directory"""
        completed_path = self.storage_path / "uploads" / "completed" / f"{file_id}_{processing_path.name}"
        shutil.move(str(processing_path), str(completed_path))
        return completed_path
    
    async def _extract_metadata(self, file_path: Path, filename: str, user_id: str, 
                               file_id: str, validation_result: FileValidationResult) -> FileMetadata:
        """Extract comprehensive metadata from file"""
        file_hash = await self._calculate_file_hash(file_path)
        
        metadata = FileMetadata(
            file_id=file_id,
            original_filename=filename,
            file_size=validation_result.file_size,
            content_type=validation_result.content_type,
            mime_type=validation_result.mime_type,
            file_hash=file_hash,
            upload_timestamp=datetime.now(),
            user_id=user_id,
            status=FileStatus.PROCESSING
        )
        
        # Extract content-specific metadata
        if validation_result.content_type == ContentType.AUDIO:
            await self._extract_audio_metadata(file_path, metadata)
        elif validation_result.content_type == ContentType.VIDEO:
            await self._extract_video_metadata(file_path, metadata)
        elif validation_result.content_type == ContentType.IMAGE:
            await self._extract_image_metadata(file_path, metadata)
        
        return metadata
    
    async def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file"""
        hash_sha256 = hashlib.sha256()
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    async def _extract_audio_metadata(self, file_path: Path, metadata: FileMetadata):
        """Extract audio-specific metadata"""



        try:
            # Use soundfile for basic audio info
            info = sf.info(str(file_path))
            metadata.duration = info.frames / info.samplerate if info.samplerate > 0 else 0
            metadata.sample_rate = info.samplerate
            metadata.channels = info.channels
            
            # Use mutagen for ID3 tags and detailed metadata
            audio_file = mutagen.File(str(file_path))
            if audio_file:
                tags = {}
                if hasattr(audio_file, 'tags') and audio_file.tags:
                    for key, value in audio_file.tags.items():
                        if isinstance(value, list) and value:
                            tags[key] = str(value[0])
                        else:
                            tags[key] = str(value)
                
                metadata.codec_info = {
                    "codec": getattr(audio_file.info, 'codec', 'unknown'),
                    "bitrate": getattr(audio_file.info, 'bitrate', 0),
                    "length": getattr(audio_file.info, 'length', 0)
                }
                
                # Extract common tags
                if 'TIT2' in tags or 'TITLE' in tags:
                    metadata.tags.append(f"title:{tags.get('TIT2', tags.get('TITLE', ''))}")
                if 'TPE1' in tags or 'ARTIST' in tags:
                    metadata.tags.append(f"artist:{tags.get('TPE1', tags.get('ARTIST', ''))}")
                if 'TALB' in tags or 'ALBUM' in tags:
                    metadata.tags.append(f"album:{tags.get('TALB', tags.get('ALBUM', ''))}")
            
        except Exception as e:
            self.logger.warning(f"Audio metadata extraction failed: {e}")
    
    async def _extract_video_metadata(self, file_path: Path, metadata: FileMetadata):
        """Extract video-specific metadata"""



        try:
            cap = cv2.VideoCapture(str(file_path))
            
            if cap.isOpened():
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                metadata.dimensions = (width, height)
                metadata.duration = frame_count / fps if fps > 0 else 0
                metadata.resolution = f"{width}x{height}"
                
                metadata.codec_info = {
                    "frame_count": frame_count,
                    "fps": fps,
                    "fourcc": int(cap.get(cv2.CAP_PROP_FOURCC))
                }
                
                cap.release()
            
        except Exception as e:
            self.logger.warning(f"Video metadata extraction failed: {e}")
    
    async def _extract_image_metadata(self, file_path: Path, metadata: FileMetadata):
        """Extract image-specific metadata"""



        try:
            with Image.open(file_path) as img:
                width, height = img.size
                metadata.dimensions = (width, height)
                metadata.resolution = f"{width}x{height}"
                
                # Extract EXIF data
                if hasattr(img, '_getexif') and img._getexif():
                    exif_dict = {}
                    exif = img._getexif()
                    
                    for tag_id, value in exif.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        exif_dict[tag] = str(value)
                    
                    metadata.exif_data = exif_dict
                    
                    # Extract useful tags
                    if 'Make' in exif_dict:
                        metadata.tags.append(f"camera_make:{exif_dict['Make']}")
                    if 'Model' in exif_dict:
                        metadata.tags.append(f"camera_model:{exif_dict['Model']}")
                    if 'DateTime' in exif_dict:
                        metadata.tags.append(f"capture_date:{exif_dict['DateTime']}")
            
        except Exception as e:
            self.logger.warning(f"Image metadata extraction failed: {e}")
    
    async def _process_by_content_type(self, file_path: Path, metadata: FileMetadata) -> Dict[str, Any]:
        """Process file based on content type"""
        result = {"thumbnails": [], "optimized_versions": {}}
        
        try:
            if metadata.content_type == ContentType.AUDIO:
                result.update(await self._process_audio_file(file_path, metadata))
            elif metadata.content_type == ContentType.VIDEO:
                result.update(await self._process_video_file(file_path, metadata))
            elif metadata.content_type == ContentType.IMAGE:
                result.update(await self._process_image_file(file_path, metadata))
            
            metadata.status = FileStatus.PROTECTED
            
        except Exception as e:
            self.logger.error(f"Content processing failed: {e}")
            metadata.status = FileStatus.ERROR
        
        return result
    
    async def _process_audio_file(self, file_path: Path, metadata: FileMetadata) -> Dict[str, Any]:
        """Process audio file for optimization and previews"""
        result = {"thumbnails": [], "optimized_versions": {}}
        
        try:
            # Generate waveform thumbnail
            waveform_path = await self._generate_audio_waveform(file_path, metadata.file_id)
            if waveform_path:
                result["thumbnails"].append(str(waveform_path))
            
            # Generate optimized versions for different bitrates
            optimized_versions = await self._optimize_audio_file(file_path, metadata)
            result["optimized_versions"].update(optimized_versions)
            
        except Exception as e:
            self.logger.warning(f"Audio processing failed: {e}")
        
        return result
    
    async def _process_video_file(self, file_path: Path, metadata: FileMetadata) -> Dict[str, Any]:
        """Process video file for optimization and thumbnails"""
        result = {"thumbnails": [], "optimized_versions": {}}
        
        try:
            # Generate video thumbnails
            thumbnails = await self._generate_video_thumbnails(file_path, metadata.file_id)
            result["thumbnails"].extend(thumbnails)
            
            # Generate optimized versions for different resolutions
            optimized_versions = await self._optimize_video_file(file_path, metadata)
            result["optimized_versions"].update(optimized_versions)
            
        except Exception as e:
            self.logger.warning(f"Video processing failed: {e}")
        
        return result
    
    async def _process_image_file(self, file_path: Path, metadata: FileMetadata) -> Dict[str, Any]:
        """Process image file for optimization and thumbnails"""
        result = {"thumbnails": [], "optimized_versions": {}}
        
        try:
            # Generate thumbnails in different sizes
            thumbnails = await self._generate_image_thumbnails(file_path, metadata.file_id)
            result["thumbnails"].extend(thumbnails)
            
            # Generate optimized versions
            optimized_versions = await self._optimize_image_file(file_path, metadata)
            result["optimized_versions"].update(optimized_versions)
            
        except Exception as e:
            self.logger.warning(f"Image processing failed: {e}")
        
        return result
    
    async def _generate_audio_waveform(self, file_path: Path, file_id: str) -> Optional[str]:
        """Generate audio waveform visualization"""



        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            
            # Load audio data
            data, sr = librosa.load(str(file_path), duration=30)  # First 30 seconds
            
            # Generate waveform
            plt.figure(figsize=(12, 4))
            plt.plot(data)
            plt.title('Audio Waveform')
            plt.xlabel('Time')
            plt.ylabel('Amplitude')
            
            # Save waveform
            waveform_path = self.storage_path / "processed" / "thumbnails" / f"{file_id}_waveform.png"
            plt.savefig(waveform_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            return str(waveform_path)
            
        except Exception as e:
            self.logger.warning(f"Waveform generation failed: {e}")
            return None
    
    async def _optimize_audio_file(self, file_path: Path, metadata: FileMetadata) -> Dict[str, str]:
        """Generate optimized audio versions"""
        optimized = {}
        
        try:
            # This would typically use ffmpeg or similar tools
            # For now, we'll create placeholders for different quality levels
            base_name = f"{metadata.file_id}_audio"
            
            quality_levels = [
                ("high", "320kbps"),
                ("medium", "192kbps"),
                ("low", "128kbps")
            ]
            
            for quality, bitrate in quality_levels:
                output_path = self.storage_path / "processed" / "optimized" / f"{base_name}_{quality}.mp3"
                
                # In production, use ffmpeg:
                # ffmpeg -i input -b:a {bitrate} output
                # For now, copy original as placeholder
                shutil.copy2(file_path, output_path)
                optimized[quality] = str(output_path)
            
        except Exception as e:
            self.logger.warning(f"Audio optimization failed: {e}")
        
        return optimized
    
    async def _generate_video_thumbnails(self, file_path: Path, file_id: str) -> List[str]:
        """Generate video thumbnails at different timestamps"""
        thumbnails = []
        
        try:
            cap = cv2.VideoCapture(str(file_path))
            
            if cap.isOpened():
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                
                # Generate thumbnails at 10%, 50%, and 90% of video duration
                positions = [0.1, 0.5, 0.9]
                
                for i, pos in enumerate(positions):
                    frame_number = int(frame_count * pos)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                    
                    ret, frame = cap.read()
                    if ret:
                        thumbnail_path = self.storage_path / "processed" / "thumbnails" / f"{file_id}_thumb_{i}.jpg"
                        
                        # Resize frame to thumbnail size
                        height, width = frame.shape[:2]
                        max_size = 400
                        
                        if width > height:
                            new_width = max_size
                            new_height = int(height * max_size / width)
                        else:
                            new_height = max_size
                            new_width = int(width * max_size / height)
                        
                        resized_frame = cv2.resize(frame, (new_width, new_height))
                        cv2.imwrite(str(thumbnail_path), resized_frame)
                        thumbnails.append(str(thumbnail_path))
                
                cap.release()
            
        except Exception as e:
            self.logger.warning(f"Video thumbnail generation failed: {e}")
        
        return thumbnails
    
    async def _optimize_video_file(self, file_path: Path, metadata: FileMetadata) -> Dict[str, str]:
        """Generate optimized video versions"""
        optimized = {}
        
        try:
            base_name = f"{metadata.file_id}_video"
            
            # Different resolution/quality presets
            presets = [
                ("1080p", "1920x1080"),
                ("720p", "1280x720"),
                ("480p", "854x480")
            ]
            
            for quality, resolution in presets:
                output_path = self.storage_path / "processed" / "optimized" / f"{base_name}_{quality}.mp4"
                
                # In production, use ffmpeg:
                # ffmpeg -i input -vf scale={resolution} -crf 23 output
                # For now, copy original as placeholder
                shutil.copy2(file_path, output_path)
                optimized[quality] = str(output_path)
            
        except Exception as e:
            self.logger.warning(f"Video optimization failed: {e}")
        
        return optimized
    
    async def _generate_image_thumbnails(self, file_path: Path, file_id: str) -> List[str]:
        """Generate image thumbnails in different sizes"""
        thumbnails = []
        
        try:
            with Image.open(file_path) as img:
                # Generate thumbnails in different sizes
                sizes = [(150, 150), (300, 300), (600, 600)]
                
                for i, size in enumerate(sizes):
                    thumbnail = img.copy()
                    thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
                    
                    thumbnail_path = self.storage_path / "processed" / "thumbnails" / f"{file_id}_thumb_{size[0]}x{size[1]}.jpg"
                    
                    # Convert to RGB if necessary
                    if thumbnail.mode in ('RGBA', 'LA', 'P'):
                        thumbnail = thumbnail.convert('RGB')
                    
                    thumbnail.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
                    thumbnails.append(str(thumbnail_path))
            
        except Exception as e:
            self.logger.warning(f"Image thumbnail generation failed: {e}")
        
        return thumbnails
    
    async def _optimize_image_file(self, file_path: Path, metadata: FileMetadata) -> Dict[str, str]:
        """Generate optimized image versions"""
        optimized = {}
        
        try:
            with Image.open(file_path) as img:
                base_name = f"{metadata.file_id}_image"
                
                # Different quality levels
                quality_levels = [
                    ("high", 95),
                    ("medium", 80),
                    ("low", 60)
                ]
                
                for quality_name, quality_value in quality_levels:
                    output_path = self.storage_path / "processed" / "optimized" / f"{base_name}_{quality_name}.jpg"
                    
                    # Convert to RGB if necessary
                    optimized_img = img.copy()
                    if optimized_img.mode in ('RGBA', 'LA', 'P'):
                        optimized_img = optimized_img.convert('RGB')
                    
                    optimized_img.save(output_path, 'JPEG', quality=quality_value, optimize=True)
                    optimized[quality_name] = str(output_path)
            
        except Exception as e:
            self.logger.warning(f"Image optimization failed: {e}")
        
        return optimized
    
    async def _save_metadata(self, metadata: FileMetadata):
        """Save file metadata to storage"""



        try:
            metadata_path = self.storage_path / "metadata" / f"{metadata.file_id}.json"
            
            # Convert metadata to dictionary
            metadata_dict = {
                "file_id": metadata.file_id,
                "original_filename": metadata.original_filename,
                "file_size": metadata.file_size,
                "content_type": metadata.content_type.value,
                "mime_type": metadata.mime_type,
                "file_hash": metadata.file_hash,
                "upload_timestamp": metadata.upload_timestamp.isoformat(),
                "user_id": metadata.user_id,
                "dimensions": metadata.dimensions,
                "duration": metadata.duration,
                "bitrate": metadata.bitrate,
                "sample_rate": metadata.sample_rate,
                "channels": metadata.channels,
                "resolution": metadata.resolution,
                "format_version": metadata.format_version,
                "virus_scan_result": metadata.virus_scan_result,
                "content_policy_check": metadata.content_policy_check,
                "adult_content_score": metadata.adult_content_score,
                "status": metadata.status.value,
                "compression_applied": metadata.compression_applied.value if metadata.compression_applied else None,
                "optimization_savings": metadata.optimization_savings,
                "fingerprint_hash": metadata.fingerprint_hash,
                "tags": metadata.tags,
                "description": metadata.description,
                "copyright_info": metadata.copyright_info,
                "licensing_terms": metadata.licensing_terms,
                "exif_data": metadata.exif_data,
                "codec_info": metadata.codec_info,
                "container_format": metadata.container_format,
                "access_level": metadata.access_level,
                "shared_with": metadata.shared_with,
                "download_permissions": metadata.download_permissions
            }
            
            async with aiofiles.open(metadata_path, 'w') as f:
                await f.write(json.dumps(metadata_dict, indent=2, default=str))
            
        except Exception as e:
            self.logger.error(f"Failed to save metadata for {metadata.file_id}: {e}")
    
    def _update_stats(self, metadata: FileMetadata, processing_time: float):
        """Update processing statistics"""
        self.stats["files_processed"] += 1
        self.stats["total_size_processed"] += metadata.file_size
        
        if metadata.optimization_savings:
            self.stats["optimization_savings"] += metadata.optimization_savings
        
        self.logger.info(f" Processing stats updated - Total files: {self.stats['files_processed']}")
    
    async def get_file_metadata(self, file_id: str) -> Optional[FileMetadata]:
        """Retrieve file metadata by ID"""



        try:
            metadata_path = self.storage_path / "metadata" / f"{file_id}.json"
            
            if not metadata_path.exists():
                return None
            
            async with aiofiles.open(metadata_path, 'r') as f:
                metadata_dict = json.loads(await f.read())
            
            # Convert back to FileMetadata object
            metadata = FileMetadata(
                file_id=metadata_dict["file_id"],
                original_filename=metadata_dict["original_filename"],
                file_size=metadata_dict["file_size"],
                content_type=ContentType(metadata_dict["content_type"]),
                mime_type=metadata_dict["mime_type"],
                file_hash=metadata_dict["file_hash"],
                upload_timestamp=datetime.fromisoformat(metadata_dict["upload_timestamp"]),
                user_id=metadata_dict["user_id"]
            )
            
            # Set optional fields
            for field in ["dimensions", "duration", "bitrate", "sample_rate", "channels", 
                         "resolution", "format_version", "virus_scan_result", "content_policy_check",
                         "adult_content_score", "optimization_savings", "fingerprint_hash",
                         "tags", "description", "copyright_info", "licensing_terms", 
                         "exif_data", "codec_info", "container_format", "access_level",
                         "shared_with", "download_permissions"]:
                if field in metadata_dict and metadata_dict[field] is not None:
                    setattr(metadata, field, metadata_dict[field])
            
            if metadata_dict.get("status"):
                metadata.status = FileStatus(metadata_dict["status"])
            
            if metadata_dict.get("compression_applied"):
                metadata.compression_applied = CompressionLevel(metadata_dict["compression_applied"])
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve metadata for {file_id}: {e}")
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete file and all associated data"""



        try:
            success = True
            
            # Delete main file
            for directory in ["uploads/completed", "uploads/processing", "uploads/pending"]:
                pattern = f"{file_id}_*"
                directory_path = self.storage_path / directory
                
                for file_path in directory_path.glob(pattern):
                    try:
                        file_path.unlink()
                        self.logger.info(f" Deleted: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Failed to delete {file_path}: {e}")
                        success = False
            
            # Delete processed files
            for directory in ["processed/originals", "processed/optimized", "processed/thumbnails", "processed/previews"]:
                pattern = f"{file_id}_*"
                directory_path = self.storage_path / directory
                
                for file_path in directory_path.glob(pattern):
                    try:
                        file_path.unlink()
                    except Exception as e:
                        self.logger.error(f"Failed to delete processed file {file_path}: {e}")
                        success = False
            
            # Delete metadata
            metadata_path = self.storage_path / "metadata" / f"{file_id}.json"
            if metadata_path.exists():
                try:
                    metadata_path.unlink()
                except Exception as e:
                    self.logger.error(f"Failed to delete metadata {metadata_path}: {e}")
                    success = False
            
            return success
            
        except Exception as e:
            self.logger.error(f"File deletion failed for {file_id}: {e}")
            return False
    
    async def list_files(self, user_id: Optional[str] = None, 
                        content_type: Optional[ContentType] = None,
                        limit: int = 100) -> List[FileMetadata]:
        """List files with optional filtering"""



        try:
            files = []
            metadata_dir = self.storage_path / "metadata"
            
            for metadata_file in metadata_dir.glob("*.json"):
                try:
                    metadata = await self.get_file_metadata(metadata_file.stem)
                    if metadata:
                        # Apply filters
                        if user_id and metadata.user_id != user_id:
                            continue
                        if content_type and metadata.content_type != content_type:
                            continue
                        
                        files.append(metadata)
                        
                        if len(files) >= limit:
                            break
                            
                except Exception as e:
                    self.logger.warning(f"Failed to load metadata from {metadata_file}: {e}")
                    continue
            
            # Sort by upload timestamp (newest first)
            files.sort(key=lambda x: x.upload_timestamp, reverse=True)
            
            return files
            
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return []
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""



        try:
            stats = self.stats.copy()
            
            # Add storage statistics
            storage_stats = {}
            for directory in ["uploads", "processed", "metadata"]:
                dir_path = self.storage_path / directory
                total_size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                file_count = len(list(dir_path.rglob('*')))
                storage_stats[directory] = {
                    "total_size": total_size,
                    "file_count": file_count
                }
            
            stats["storage_stats"] = storage_stats
            stats["storage_path"] = str(self.storage_path)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get processing stats: {e}")
            return self.stats.copy()
    
    async def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours"""



        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            # Clean temp directory
            temp_dir = self.storage_path / "temp"
            for file_path in temp_dir.rglob('*'):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                        except Exception as e:
                            self.logger.warning(f"Failed to clean temp file {file_path}: {e}")
            
            # Clean pending uploads older than cutoff
            pending_dir = self.storage_path / "uploads" / "pending"
            for file_path in pending_dir.rglob('*'):
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                        except Exception as e:
                            self.logger.warning(f"Failed to clean pending file {file_path}: {e}")
            
            self.logger.info(f"🧹 Cleaned up {cleaned_count} temporary files")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
            return 0
    
    def __del__(self):
        """Cleanup resources on destruction"""



        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=False)
        except:
            pass
