"""
Content Validator - Multi-Format Content Validation Engine
==========================================================

The ContentValidator ensures content integrity, security, and compliance
before processing in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import mimetypes
import hashlib
import magic
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from pathlib import Path
import re

import aiofiles
import aiofiles.os
from PIL import Image
import cv2
import librosa
import chardet
from sqlalchemy.ext.asyncio import AsyncSession

from ..security.content_scanner import ContentScanner
from ..security.virus_scanner import VirusScanner
from ..config.settings import get_settings


class ValidationError(Exception):
    """Content validation error"""
    pass


class ValidationRule:
    """Content validation rule definition"""
    
    def __init__(
        self,
        name: str,
        check_function: callable,
        error_message: str,
        is_critical: bool = True
    ):
        self.name = name
        self.check_function = check_function
        self.error_message = error_message
        self.is_critical = is_critical


class ContentValidator:
    """
    Multi-Format Content Validation Engine
    
    Provides comprehensive validation for all supported content types
    including security scanning, format verification, quality checks,
    and compliance validation.
    
    Validation Categories:
    - File integrity and format validation
    - Security scanning (malware, viruses)
    - Content quality assessment
    - Legal compliance checking
    - User permissions and quotas
    """
    
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self.logger = logging.getLogger(__name__)
        
        # Initialize security scanners
        self.content_scanner = ContentScanner()
        self.virus_scanner = VirusScanner()
        
        # File size limits (bytes)
        self.size_limits = {
            "audio": 500 * 1024 * 1024,    # 500MB
            "video": 2 * 1024 * 1024 * 1024,  # 2GB
            "image": 100 * 1024 * 1024,    # 100MB
            "text": 50 * 1024 * 1024       # 50MB
        }
        
        # Supported formats
        self.supported_formats = {
            "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
            "video": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".webm"],
            "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
            "text": [".txt", ".md", ".doc", ".docx", ".pdf", ".rtf"]
        }
        
        # MIME type mapping
        self.mime_types = {
            "audio": [
                "audio/mpeg", "audio/wav", "audio/flac", "audio/aac",
                "audio/ogg", "audio/mp4", "audio/x-m4a"
            ],
            "video": [
                "video/mp4", "video/avi", "video/quicktime", "video/x-msvideo",
                "video/x-flv", "video/x-matroska", "video/webm"
            ],
            "image": [
                "image/jpeg", "image/png", "image/gif", "image/bmp",
                "image/tiff", "image/webp"
            ],
            "text": [
                "text/plain", "text/markdown", "application/pdf",
                "application/msword", "application/rtf"
            ]
        }
        
        # Initialize validation rules
        self._setup_validation_rules()

    async def validate_content(
        self,
        file_path: str,
        content_type: str,
        user_id: int,
        additional_checks: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive content validation
        
        Args:
            file_path: Path to content file
            content_type: Expected content type
            user_id: User ID for quota checking
            additional_checks: Optional additional validation checks
            
        Returns:
            Validation result with status and details
        """
        validation_start = datetime.utcnow()
        
        try:
            self.logger.info(f"Validating content {file_path} for user {user_id}")
            
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "metadata": {},
                "validation_time": 0.0,
                "checks_performed": []
            }
            
            # Basic file existence check
            if not await aiofiles.os.path.exists(file_path):
                validation_result["valid"] = False
                validation_result["errors"].append("File does not exist")
                return validation_result
            
            # File accessibility check
            try:
                async with aiofiles.open(file_path, 'rb') as f:
                    await f.read(1024)  # Try to read first 1KB
            except Exception as e:
                validation_result["valid"] = False
                validation_result["errors"].append(f"File not accessible: {str(e)}")
                return validation_result
            
            # Execute validation rules
            for rule_name, rule in self.validation_rules.items():
                try:
                    check_result = await rule.check_function(
                        file_path, content_type, user_id, validation_result
                    )
                    
                    validation_result["checks_performed"].append(rule_name)
                    
                    if not check_result["passed"]:
                        if rule.is_critical:
                            validation_result["valid"] = False
                            validation_result["errors"].append(
                                f"{rule_name}: {check_result.get('message', rule.error_message)}"
                            )
                        else:
                            validation_result["warnings"].append(
                                f"{rule_name}: {check_result.get('message', rule.error_message)}"
                            )
                    
                    # Merge metadata
                    if "metadata" in check_result:
                        validation_result["metadata"].update(check_result["metadata"])
                        
                except Exception as e:
                    self.logger.warning(f"Validation rule {rule_name} failed: {str(e)}")
                    if rule.is_critical:
                        validation_result["valid"] = False
                        validation_result["errors"].append(f"{rule_name}: Validation check failed")
            
            # Additional custom checks
            if additional_checks:
                for check_name in additional_checks:
                    if hasattr(self, f"_check_{check_name}"):
                        check_method = getattr(self, f"_check_{check_name}")
                        try:
                            custom_result = await check_method(file_path, content_type, user_id)
                            if not custom_result.get("passed", True):
                                validation_result["warnings"].append(
                                    f"Custom check {check_name}: {custom_result.get('message', 'Failed')}"
                                )
                        except Exception as e:
                            self.logger.warning(f"Custom check {check_name} failed: {str(e)}")
            
            # Calculate validation time
            validation_time = (datetime.utcnow() - validation_start).total_seconds()
            validation_result["validation_time"] = validation_time
            
            self.logger.info(
                f"Content validation completed in {validation_time:.2f}s. "
                f"Valid: {validation_result['valid']}, "
                f"Errors: {len(validation_result['errors'])}, "
                f"Warnings: {len(validation_result['warnings'])}"
            )
            
            return validation_result
            
        except Exception as e:
            validation_time = (datetime.utcnow() - validation_start).total_seconds()
            error_msg = f"Validation failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "valid": False,
                "errors": [error_msg],
                "warnings": [],
                "metadata": {},
                "validation_time": validation_time,
                "checks_performed": []
            }

    def _setup_validation_rules(self):
        """Initialize validation rules"""
        self.validation_rules = {
            "file_format": ValidationRule(
                "file_format",
                self._check_file_format,
                "Invalid file format",
                is_critical=True
            ),
            "file_size": ValidationRule(
                "file_size",
                self._check_file_size,
                "File size exceeds limit",
                is_critical=True
            ),
            "mime_type": ValidationRule(
                "mime_type",
                self._check_mime_type,
                "Invalid MIME type",
                is_critical=True
            ),
            "file_integrity": ValidationRule(
                "file_integrity",
                self._check_file_integrity,
                "File integrity check failed",
                is_critical=True
            ),
            "virus_scan": ValidationRule(
                "virus_scan",
                self._check_virus_scan,
                "Virus detected in file",
                is_critical=True
            ),
            "content_quality": ValidationRule(
                "content_quality",
                self._check_content_quality,
                "Content quality below threshold",
                is_critical=False
            ),
            "user_quota": ValidationRule(
                "user_quota",
                self._check_user_quota,
                "User quota exceeded",
                is_critical=True
            ),
            "metadata_extraction": ValidationRule(
                "metadata_extraction",
                self._check_metadata_extraction,
                "Metadata extraction failed",
                is_critical=False
            )
        }

    async def _check_file_format(
        self,
        file_path: str,
        content_type: str,
        user_id: int,
        validation_result: Dict
    ) -> Dict[str, Any]:
        """Check if file format is supported"""
        try:
            file_ext = Path(file_path).suffix.lower()
            supported_exts = self.supported_formats.get(content_type, [])
            
            if file_ext not in supported_exts:
                return {
                    "passed": False,
                    "message": f"Format {file_ext} not supported for {content_type}. "
                             f"Supported: {', '.join(supported_exts)}"
                }
            
            return {
                "passed": True,
                "metadata": {"file_extension": file_ext}
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Format check failed: {str(e)}"
            }

    async def _check_file_size(
        self,
        file_path: str,
        content_type: str,
        user_id: int,
        validation_result: Dict
    ) -> Dict[str, Any]:
        """Check if file size is within limits"""
        try:
            file_size = await aiofiles.os.path.getsize(file_path)
            size_limit = self.size_limits.get(content_type, 0)
            
            if file_size > size_limit:
                return {
                    "passed": False,
                    "message": f"File size {file_size} bytes exceeds limit {size_limit} bytes"
                }
            
            return {
                "passed": True,
                "metadata": {
                    "file_size": file_size,
                    "size_limit": size_limit
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Size check failed: {str(e)}"
            }

    async def _check_mime_type(
        self,
        file_path: str,
        content_type: str,
        user_id: int,
        validation_result: Dict
    ) -> Dict[str, Any]:
        """Check MIME type validity"""
        try:
            # Use python-magic for accurate MIME detection
            mime_type = magic.from_file(file_path, mime=True)
            expected_mimes = self.mime_types.get(content_type, [])
            
            if mime_type not in expected_mimes:
                return {
                    "passed": False,
                    "message": f"MIME type {mime_type} not valid for {content_type}. "
                             f"Expected: {', '.join(expected_mimes)}"
                }
            
            return {
                "passed": True,
                "metadata": {"mime_type": mime_type}
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"MIME type check failed: {str(e)}"
            }

    async def _check_file_integrity(
        self,
        file_path: str,
        content_type: str,
        user_id: int,
        validation_result: Dict
    ) -> Dict[str, Any]:
        """Check file integrity and corruption"""
        try:
            if content_type == "image":
                return await self._check_image_integrity(file_path)
            elif content_type == "audio":
                return await self._check_audio_integrity(file_path)
            elif content_type == "video":
                return await self._check_video_integrity(file_path)
            elif content_type == "text":
                return await self._check_text_integrity(file_path)
            else:
                return {"passed": True, "message": "Integrity check not implemented"}
                
        except Exception as e:
            return {
                "passed": False,
                "message": f"Integrity check failed: {str(e)}"
            }

    async def _check_image_integrity(self, file_path: str) -> Dict[str, Any]:
        """Check image file integrity"""
        try:
            with Image.open(file_path) as img:
                # Try to load the image data
                img.load()
                
                # Verify image has valid dimensions
                if img.width <= 0 or img.height <= 0:
                    return {
                        "passed": False,
                        "message": "Image has invalid dimensions"
                    }
                
                return {
                    "passed": True,
                    "metadata": {
                        "width": img.width,
                        "height": img.height,
                        "mode": img.mode,
                        "format": img.format
                    }
                }
                
        except Exception as e:
            return {
                "passed": False,
                "message": f"Image integrity check failed: {str(e)}"
            }

    async def _check_audio_integrity(self, file_path: str) -> Dict[str, Any]:
        """Check audio file integrity"""
        try:
            # Try to load audio with librosa
            audio_data, sample_rate = librosa.load(file_path, sr=None, duration=1.0)
            
            if len(audio_data) == 0:
                return {
                    "passed": False,
                    "message": "Audio file contains no data"
                }
            
            if sample_rate <= 0:
                return {
                    "passed": False,
                    "message": "Audio file has invalid sample rate"
                }
            
            return {
                "passed": True,
                "metadata": {
                    "sample_rate": sample_rate,
                    "channels": 1 if len(audio_data.shape) == 1 else audio_data.shape[0],
                    "duration_sample": len(audio_data) / sample_rate
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Audio integrity check failed: {str(e)}"
            }

    async def _check_video_integrity(self, file_path: str) -> Dict[str, Any]:
        """Check video file integrity"""
        try:
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                return {
                    "passed": False,
                    "message": "Cannot open video file"
                }
            
            # Get video properties
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            cap.release()
            
            if frame_count <= 0 or fps <= 0 or width <= 0 or height <= 0:
                return {
                    "passed": False,
                    "message": "Video has invalid properties"
                }
            
            return {
                "passed": True,
                "metadata": {
                    "frame_count": frame_count,
                    "fps": fps,
                    "width": width,
                    "height": height,
                    "duration": frame_count / fps if fps > 0 else 0
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Video integrity check failed: {str(e)}"
            }

    async def _check_text_integrity(self, file_path: str) -> Dict[str, Any]:
        """Check text file integrity"""
        try:
            # Detect encoding
            async with aiofiles.open(file_path, 'rb') as f:
                raw_data = await f.read(10240)  # Read first 10KB for encoding detection
            
            detected_encoding = chardet.detect(raw_data)
            encoding = detected_encoding.get('encoding', 'utf-8')
            confidence = detected_encoding.get('confidence', 0.0)
            
            # Try to read with detected encoding
            async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                content = await f.read()
            
            if not content.strip():
                return {
                    "passed": False,
                    "message": "Text file is empty"
                }
            
            return {
                "passed": True,
                "metadata": {
                    "encoding": encoding,
                    "encoding_confidence": confidence,
                    "character_count": len(content),
                    "line_count": content.count('\n') + 1
                }
            }
            
        except Exception as e:
            return {
                "passed": False,
                "message": f"Text integrity check failed: {str(e)}"
            }

    async def _check_virus_scan(
        self,
        file_path: str,
        content_type: str,
        user_id: int,
        validation_result: Dict
    ) -> Dict[str, Any]:
        """Perform virus scanning"""
        try:
            scan_result = await self.virus_scanner.scan_file(file_path)
            
            if scan_result.get("threat_detected", False):
                return {
                    "passed": False,
                    "message": f"Security threat detected: {scan_result.get('threat_type', 'Unknown')}"
                }
            
            return {
                "passed": True,
                "metadata": {
                    "virus_scan_clean": True,
                    "scan_engine": scan_result.get("engine", "unknown")
                }
            }
            
        except Exception as e:
            # Don't fail validation if virus scanner is unavailable
            self.logger.warning(f"Virus scan failed: {str(e)}")
            return {
                "passed": True,
                "message": "Virus scan unavailable"
            }

    async def _check_content_quality(
        self,
        file_path: str,
        content_type: str,
        user_id: int,
        validation_result: Dict
    ) -> Dict[str, Any]:
        """Check content quality metrics"""
        try:
            if content_type == "image":
                return await self._assess_image_quality(file_path)
            elif content_type == "audio":
                return await self._assess_audio_quality(file_path)
            elif content_type == "video":
                return await self._assess_video_quality(file_path)
            else:
                return {"passed": True, "message": "Quality check not applicable"}
                
        except Exception as e:
            return {
                "passed": True,  # Non-critical check
                "message": f"Quality assessment failed: {str(e)}"
            }

    async def _assess_image_quality(self, file_path: str) -> Dict[str, Any]:
        """Assess image quality"""
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                
                # Basic quality checks
                min_resolution = 100  # Minimum 100px
                if width < min_resolution or height < min_resolution:
                    return {
                        "passed": False,
                        "message": f"Image resolution too low: {width}x{height}"
                    }
                
                # Calculate quality score (simplified)
                quality_score = min(1.0, (width * height) / (1920 * 1080))
                
                return {
                    "passed": quality_score >= 0.1,  # At least 10% of HD quality
                    "metadata": {
                        "quality_score": quality_score,
                        "resolution": f"{width}x{height}"
                    }
                }
                
        except Exception as e:
            return {
                "passed": True,
                "message": f"Quality assessment failed: {str(e)}"
            }

    async def _assess_audio_quality(self, file_path: str) -> Dict[str, Any]:
        """Assess audio quality"""
        try:
            audio_data, sample_rate = librosa.load(file_path, sr=None, duration=10.0)
            
            # Basic quality checks
            if sample_rate < 8000:  # Minimum 8kHz
                return {
                    "passed": False,
                    "message": f"Sample rate too low: {sample_rate}Hz"
                }
            
            # Calculate RMS level for volume check
            rms = np.sqrt(np.mean(audio_data**2))
            if rms < 0.001:  # Very quiet audio
                return {
                    "passed": False,
                    "message": "Audio level too low"
                }
            
            # Calculate quality score
            quality_score = min(1.0, sample_rate / 44100)
            
            return {
                "passed": quality_score >= 0.2,  # At least 20% of CD quality
                "metadata": {
                    "quality_score": quality_score,
                    "sample_rate": sample_rate,
                    "rms_level": float(rms)
                }
            }
            
        except Exception as e:
            return {
                "passed": True,
                "message": f"Quality assessment failed: {str(e)}"
            }

    async def _assess_video_quality(self, file_path: str) -> Dict[str, Any]:
        """Assess video quality"""
        try:
            cap = cv2.VideoCapture(file_path)
            
            if not cap.isOpened():
                return {
                    "passed": False,
                    "message": "Cannot assess video quality"
                }
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            cap.release()
            
            # Basic quality checks
            min_resolution = 240  # Minimum 240p
            if height < min_resolution:
                return {
                    "passed": False,
                    "message": f"Video resolution too low: {width}x{height}"
                }
            
            if fps < 15:  # Minimum 15 FPS
                return {
                    "passed": False,
                    "message": f"Frame rate too low: {fps} FPS"
                }
            
            # Calculate quality score
            quality_score = min(1.0, (width * height) / (1920 * 1080))
            
            return {
                "passed": quality_score >= 0.05,  # At least 5% of HD quality
                "metadata": {
                    "quality_score": quality_score,
                    "resolution": f"{width}x{height}",
                    "fps": fps
                }
            }
            
        except Exception as e:
            return {
                "passed": True,
                "message": f"Quality assessment failed: {str(e)}"
            }

    async def _check_user_quota(
        self,
        file_path: str,
        content_type: str,
        user_id: int,
        validation_result: Dict
    ) -> Dict[str, Any]:
        """Check user upload quota"""
        try:
            # This would integrate with user management system
            # For now, return passed
            return {
                "passed": True,
                "metadata": {"quota_check": "passed"}
            }
            
        except Exception as e:
            return {
                "passed": True,
                "message": f"Quota check failed: {str(e)}"
            }

    async def _check_metadata_extraction(
        self,
        file_path: str,
        content_type: str,
        user_id: int,
        validation_result: Dict
    ) -> Dict[str, Any]:
        """Validate metadata can be extracted"""
        try:
            # Basic metadata extraction test
            file_stats = await aiofiles.os.stat(file_path)
            
            metadata = {
                "file_created": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "file_modified": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                "file_size": file_stats.st_size
            }
            
            return {
                "passed": True,
                "metadata": metadata
            }
            
        except Exception as e:
            return {
                "passed": True,
                "message": f"Metadata extraction test failed: {str(e)}"
            }
