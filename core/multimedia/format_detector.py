"""
Multimedia Format Detector - Advanced Format Detection Engine

Enterprise-grade format detection system for multimedia content with deep analysis capabilities.
Provides intelligent format identification, validation, and metadata extraction.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
import mimetypes
import struct
import hashlib
from pathlib import Path

from ..monitoring.metrics import MetricsCollector
from ..events.dispatcher import EventDispatcher

logger = logging.getLogger(__name__)


class MediaFormat(Enum):
    """Supported media formats"""
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    FLV = "flv"
    WMV = "wmv"
    M4V = "m4v"
    _3GP = "3gp"
    OGV = "ogv"
    
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"
    OPUS = "opus"
    AIFF = "aiff"
    
    # Image formats
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"
    HEIC = "heic"
    SVG = "svg"
    RAW = "raw"
    ICO = "ico"
    
    # Unknown
    UNKNOWN = "unknown"


class MediaType(Enum):
    """Media type categories"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    CONTAINER = "container"
    UNKNOWN = "unknown"


class FormatConfidence(Enum):
    """Format detection confidence levels"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


@dataclass
class FormatSignature:
    """Format detection signature"""
    format: MediaFormat
    magic_bytes: bytes
    offset: int = 0
    mask: Optional[bytes] = None
    additional_checks: Optional[List[str]] = None
    confidence_boost: float = 1.0


@dataclass
class FormatDetectionResult:
    """Format detection result"""
    detected_format: MediaFormat
    media_type: MediaType
    confidence: FormatConfidence
    confidence_score: float
    file_extension: Optional[str] = None
    mime_type: Optional[str] = None
    container_format: Optional[str] = None
    codec_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    validation_errors: List[str] = field(default_factory=list)
    detection_time: float = 0.0


class MultimediaFormatDetector:
    """
    Advanced multimedia format detection engine with deep analysis.
    
    Features:
    - Magic byte signature detection
    - Container format analysis
    - Codec identification
    - Metadata extraction
    - Format validation
    - Confidence scoring
    - Support for corrupted files
    - Performance optimization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize format detector"""
        self.config = config or {}
        self.metrics = MetricsCollector()
        self.events = EventDispatcher()
        
        # Format signatures database
        self.format_signatures = self._initialize_format_signatures()
        
        # MIME type mappings
        self.mime_mappings = self._initialize_mime_mappings()
        
        # Format to media type mappings
        self.format_type_mappings = self._initialize_format_type_mappings()
        
        # Detection statistics
        self.stats = {
            'detections_performed': 0,
            'successful_detections': 0,
            'failed_detections': 0,
            'format_counts': {},
            'confidence_distribution': {
                'very_high': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'very_low': 0
            }
        }
        
        logger.info("Multimedia format detector initialized successfully")
    
    def _initialize_format_signatures(self) -> List[FormatSignature]:
        """Initialize format detection signatures"""



        return [
            # Video formats
            FormatSignature(MediaFormat.MP4, b'\x00\x00\x00\x18ftypmp4', 0),
            FormatSignature(MediaFormat.MP4, b'\x00\x00\x00\x1cftypisom', 0),
            FormatSignature(MediaFormat.MP4, b'\x00\x00\x00\x20ftypM4V', 0),
            FormatSignature(MediaFormat.AVI, b'RIFF', 0, additional_checks=['avi_header']),
            FormatSignature(MediaFormat.MOV, b'\x00\x00\x00\x14ftypqt', 0),
            FormatSignature(MediaFormat.MKV, b'\x1aEߣ', 0),
            FormatSignature(MediaFormat.WEBM, b'\x1aEߣ', 0, additional_checks=['webm_header']),
            FormatSignature(MediaFormat.FLV, b'FLV', 0),
            FormatSignature(MediaFormat.WMV, b'0&²u\x8ef\xcf\x11\xa6ÙÀ\xaa\x00b\xceÌ', 0),
            FormatSignature(MediaFormat._3GP, b'\x00\x00\x00\x14ftyp3gp', 0),
            FormatSignature(MediaFormat.OGV, b'OggS', 0, additional_checks=['ogv_header']),
            
            # Audio formats
            FormatSignature(MediaFormat.MP3, b'ID3', 0),
            FormatSignature(MediaFormat.MP3, b'\xff\xfb', 0),
            FormatSignature(MediaFormat.MP3, b'\xff\xfa', 0),
            FormatSignature(MediaFormat.WAV, b'RIFF', 0, additional_checks=['wav_header']),
            FormatSignature(MediaFormat.FLAC, b'fLaC', 0),
            FormatSignature(MediaFormat.OGG, b'OggS', 0, additional_checks=['ogg_header']),
            FormatSignature(MediaFormat.M4A, b'\x00\x00\x00\x18ftypM4A', 0),
            FormatSignature(MediaFormat.AIFF, b'FORM', 0, additional_checks=['aiff_header']),
            
            # Image formats
            FormatSignature(MediaFormat.JPEG, b'\xff\xd8\xff', 0),
            FormatSignature(MediaFormat.PNG, b'\x89PNG\r\n\x1a\n', 0),
            FormatSignature(MediaFormat.GIF, b'GIF87a', 0),
            FormatSignature(MediaFormat.GIF, b'GIF89a', 0),
            FormatSignature(MediaFormat.WEBP, b'RIFF', 0, additional_checks=['webp_header']),
            FormatSignature(MediaFormat.BMP, b'BM', 0),
            FormatSignature(MediaFormat.TIFF, b'II*\x00', 0),
            FormatSignature(MediaFormat.TIFF, b'MM\x00*', 0),
            FormatSignature(MediaFormat.HEIC, b'\x00\x00\x00\x18ftypheic', 0),
            FormatSignature(MediaFormat.ICO, b'\x00\x00\x01\x00', 0),
        ]
    
    def _initialize_mime_mappings(self) -> Dict[str, MediaFormat]:
        """Initialize MIME type to format mappings"""



        return {
            # Video
            'video/mp4': MediaFormat.MP4,
            'video/avi': MediaFormat.AVI,
            'video/quicktime': MediaFormat.MOV,
            'video/x-msvideo': MediaFormat.AVI,
            'video/webm': MediaFormat.WEBM,
            'video/x-flv': MediaFormat.FLV,
            'video/x-ms-wmv': MediaFormat.WMV,
            'video/3gpp': MediaFormat._3GP,
            'video/ogg': MediaFormat.OGV,
            
            # Audio
            'audio/mpeg': MediaFormat.MP3,
            'audio/mp3': MediaFormat.MP3,
            'audio/wav': MediaFormat.WAV,
            'audio/wave': MediaFormat.WAV,
            'audio/x-wav': MediaFormat.WAV,
            'audio/flac': MediaFormat.FLAC,
            'audio/ogg': MediaFormat.OGG,
            'audio/mp4': MediaFormat.M4A,
            'audio/aac': MediaFormat.AAC,
            'audio/x-ms-wma': MediaFormat.WMA,
            'audio/opus': MediaFormat.OPUS,
            'audio/aiff': MediaFormat.AIFF,
            
            # Image
            'image/jpeg': MediaFormat.JPEG,
            'image/png': MediaFormat.PNG,
            'image/gif': MediaFormat.GIF,
            'image/webp': MediaFormat.WEBP,
            'image/tiff': MediaFormat.TIFF,
            'image/bmp': MediaFormat.BMP,
            'image/heic': MediaFormat.HEIC,
            'image/svg+xml': MediaFormat.SVG,
            'image/x-icon': MediaFormat.ICO,
        }
    
    def _initialize_format_type_mappings(self) -> Dict[MediaFormat, MediaType]:
        """Initialize format to media type mappings"""



        return {
            # Video formats
            MediaFormat.MP4: MediaType.VIDEO,
            MediaFormat.AVI: MediaType.VIDEO,
            MediaFormat.MOV: MediaType.VIDEO,
            MediaFormat.MKV: MediaType.VIDEO,
            MediaFormat.WEBM: MediaType.VIDEO,
            MediaFormat.FLV: MediaType.VIDEO,
            MediaFormat.WMV: MediaType.VIDEO,
            MediaFormat.M4V: MediaType.VIDEO,
            MediaFormat._3GP: MediaType.VIDEO,
            MediaFormat.OGV: MediaType.VIDEO,
            
            # Audio formats
            MediaFormat.MP3: MediaType.AUDIO,
            MediaFormat.WAV: MediaType.AUDIO,
            MediaFormat.FLAC: MediaType.AUDIO,
            MediaFormat.AAC: MediaType.AUDIO,
            MediaFormat.OGG: MediaType.AUDIO,
            MediaFormat.M4A: MediaType.AUDIO,
            MediaFormat.WMA: MediaType.AUDIO,
            MediaFormat.OPUS: MediaType.AUDIO,
            MediaFormat.AIFF: MediaType.AUDIO,
            
            # Image formats
            MediaFormat.JPEG: MediaType.IMAGE,
            MediaFormat.PNG: MediaType.IMAGE,
            MediaFormat.GIF: MediaType.IMAGE,
            MediaFormat.WEBP: MediaType.IMAGE,
            MediaFormat.TIFF: MediaType.IMAGE,
            MediaFormat.BMP: MediaType.IMAGE,
            MediaFormat.HEIC: MediaType.IMAGE,
            MediaFormat.SVG: MediaType.IMAGE,
            MediaFormat.RAW: MediaType.IMAGE,
            MediaFormat.ICO: MediaType.IMAGE,
        }
    
    async def detect_format(
        self,
        source: Union[str, bytes, BinaryIO],
        max_bytes: int = 8192
    ) -> FormatDetectionResult:
        """
        Detect multimedia format from various sources
        
        Args:
            source: File path, raw bytes, or file-like object
            max_bytes: Maximum bytes to read for detection
            
        Returns:
            FormatDetectionResult: Detection result with confidence score
        """
        import time
        start_time = time.time()
        
        try:
            # Read data for analysis
            data, file_path, file_extension = await self._prepare_data_for_detection(source, max_bytes)
            
            if not data:
                return self._create_unknown_result(detection_time=time.time() - start_time)
            
            # Multiple detection methods
            detection_results = []
            
            # 1. Magic byte detection
            magic_result = await self._detect_by_magic_bytes(data)
            if magic_result:
                detection_results.append(magic_result)
            
            # 2. File extension detection
            if file_extension:
                ext_result = await self._detect_by_extension(file_extension)
                if ext_result:
                    detection_results.append(ext_result)
            
            # 3. MIME type detection
            if file_path:
                mime_result = await self._detect_by_mime_type(file_path)
                if mime_result:
                    detection_results.append(mime_result)
            
            # 4. Content analysis
            content_result = await self._detect_by_content_analysis(data)
            if content_result:
                detection_results.append(content_result)
            
            # Combine results and determine best match
            best_result = await self._combine_detection_results(detection_results, data)
            
            # Add metadata
            best_result.file_extension = file_extension
            best_result.detection_time = time.time() - start_time
            
            # Validate detected format
            validation_errors = await self._validate_format(data, best_result.detected_format)
            best_result.validation_errors = validation_errors
            
            # Update statistics
            self.stats['detections_performed'] += 1
            if best_result.detected_format != MediaFormat.UNKNOWN:
                self.stats['successful_detections'] += 1
                format_name = best_result.detected_format.value
                self.stats['format_counts'][format_name] = self.stats['format_counts'].get(format_name, 0) + 1
            else:
                self.stats['failed_detections'] += 1
            
            confidence_key = best_result.confidence.value
            self.stats['confidence_distribution'][confidence_key] += 1
            
            # Emit event
            await self.events.emit('format_detected', {
                'format': best_result.detected_format.value,
                'media_type': best_result.media_type.value,
                'confidence': best_result.confidence.value,
                'detection_time': best_result.detection_time
            })
            
            return best_result
            
        except Exception as e:
            logger.error(f"Format detection failed: {str(e)}")
            self.stats['failed_detections'] += 1
            return self._create_unknown_result(
                detection_time=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _prepare_data_for_detection(
        self,
        source: Union[str, bytes, BinaryIO],
        max_bytes: int
    ) -> Tuple[bytes, Optional[str], Optional[str]]:
        """Prepare data for format detection"""
        data = b''
        file_path = None
        file_extension = None
        
        if isinstance(source, str):
            # File path
            file_path = source
            file_extension = Path(source).suffix.lower().lstrip('.')
            try:
                with open(source, 'rb') as f:
                    data = f.read(max_bytes)
            except Exception as e:
                logger.error(f"Failed to read file {source}: {str(e)}")
        elif isinstance(source, bytes):
            # Raw bytes
            data = source[:max_bytes]
        else:
            # File-like object
            try:
                current_pos = source.tell()
                data = source.read(max_bytes)
                source.seek(current_pos)
            except Exception as e:
                logger.error(f"Failed to read from file object: {str(e)}")
        
        return data, file_path, file_extension
    
    async def _detect_by_magic_bytes(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Detect format using magic byte signatures"""
        for signature in self.format_signatures:
            if len(data) < signature.offset + len(signature.magic_bytes):
                continue
            
            # Extract bytes at specified offset
            sample_bytes = data[signature.offset:signature.offset + len(signature.magic_bytes)]
            
            # Apply mask if specified
            if signature.mask:
                sample_bytes = bytes(a & b for a, b in zip(sample_bytes, signature.mask))
                magic_bytes = bytes(a & b for a, b in zip(signature.magic_bytes, signature.mask))
            else:
                magic_bytes = signature.magic_bytes
            
            if sample_bytes == magic_bytes:
                # Additional checks if specified
                if signature.additional_checks:
                    if not await self._perform_additional_checks(data, signature.additional_checks):
                        continue
                
                confidence_score = 0.9 * signature.confidence_boost
                return {
                    'format': signature.format,
                    'method': 'magic_bytes',
                    'confidence_score': confidence_score
                }
        
        return None
    
    async def _detect_by_extension(self, file_extension: str) -> Optional[Dict[str, Any]]:
        """Detect format using file extension"""



        try:
            format_enum = MediaFormat(file_extension.lower())
            return {
                'format': format_enum,
                'method': 'file_extension',
                'confidence_score': 0.6  # Lower confidence than magic bytes
            }
        except ValueError:
            return None
    
    async def _detect_by_mime_type(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Detect format using MIME type"""
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type and mime_type in self.mime_mappings:
            return {
                'format': self.mime_mappings[mime_type],
                'method': 'mime_type',
                'confidence_score': 0.5,
                'mime_type': mime_type
            }
        return None
    
    async def _detect_by_content_analysis(self, data: bytes) -> Optional[Dict[str, Any]]:
        """Detect format using content analysis"""
        # Analyze content patterns
        if len(data) < 16:
            return None
        
        # Look for common patterns
        patterns = {
            MediaFormat.MP3: [b'\xff\xfb', b'\xff\xfa', b'ID3'],
            MediaFormat.JPEG: [b'\xff\xd8', b'\xff\xe0', b'JFIF'],
            MediaFormat.PNG: [b'\x89PNG', b'IHDR'],
            MediaFormat.GIF: [b'GIF8'],
            MediaFormat.MP4: [b'ftyp', b'moov', b'mdat'],
        }
        
        for format_type, pattern_list in patterns.items():
            matches = sum(1 for pattern in pattern_list if pattern in data[:1024])
            if matches >= 2:  # Require multiple pattern matches
                return {
                    'format': format_type,
                    'method': 'content_analysis',
                    'confidence_score': 0.7
                }
        
        return None
    
    async def _perform_additional_checks(
        self,
        data: bytes,
        checks: List[str]
    ) -> bool:
        """Perform additional format-specific checks"""
        for check in checks:
            if check == 'avi_header':
                # Check for AVI-specific header
                if len(data) >= 12 and data[8:12] == b'AVI ':
                    continue
                else:
                    return False
            elif check == 'wav_header':
                # Check for WAV-specific header
                if len(data) >= 12 and data[8:12] == b'WAVE':
                    continue
                else:
                    return False
            elif check == 'webp_header':
                # Check for WebP-specific header
                if len(data) >= 12 and data[8:12] == b'WEBP':
                    continue
                else:
                    return False
            elif check == 'webm_header':
                # Check for WebM-specific elements
                if b'webm' in data[:100].lower():
                    continue
                else:
                    return False
            elif check == 'ogg_header':
                # Check for Ogg-specific patterns
                if b'vorbis' in data[:100].lower():
                    continue
                else:
                    return False
            elif check == 'ogv_header':
                # Check for Ogg video patterns
                if b'theora' in data[:100].lower():
                    continue
                else:
                    return False
            elif check == 'aiff_header':
                # Check for AIFF-specific header
                if len(data) >= 12 and data[8:12] == b'AIFF':
                    continue
                else:
                    return False
            else:
                # Unknown check, assume passed
                continue
        
        return True
    
    async def _combine_detection_results(
        self,
        results: List[Dict[str, Any]],
        data: bytes
    ) -> FormatDetectionResult:
        """Combine multiple detection results"""
        if not results:
            return self._create_unknown_result()
        
        # Weight results by confidence and method
        method_weights = {
            'magic_bytes': 1.0,
            'content_analysis': 0.8,
            'file_extension': 0.6,
            'mime_type': 0.5
        }
        
        # Calculate weighted scores
        format_scores = {}
        for result in results:
            format_type = result['format']
            method = result['method']
            base_score = result['confidence_score']
            weight = method_weights.get(method, 0.5)
            
            weighted_score = base_score * weight
            
            if format_type in format_scores:
                format_scores[format_type] = max(format_scores[format_type], weighted_score)
            else:
                format_scores[format_type] = weighted_score
        
        # Get best format
        best_format = max(format_scores.keys(), key=lambda k: format_scores[k])
        best_score = format_scores[best_format]
        
        # Determine confidence level
        confidence = self._score_to_confidence(best_score)
        
        # Get media type
        media_type = self.format_type_mappings.get(best_format, MediaType.UNKNOWN)
        
        # Extract additional metadata
        metadata = await self._extract_format_metadata(data, best_format)
        
        # Get MIME type
        mime_type = None
        for result in results:
            if result['format'] == best_format and 'mime_type' in result:
                mime_type = result['mime_type']
                break
        
        return FormatDetectionResult(
            detected_format=best_format,
            media_type=media_type,
            confidence=confidence,
            confidence_score=best_score,
            mime_type=mime_type,
            metadata=metadata
        )
    
    def _score_to_confidence(self, score: float) -> FormatConfidence:
        """Convert confidence score to confidence level"""
        if score >= 0.9:
            return FormatConfidence.VERY_HIGH
        elif score >= 0.75:
            return FormatConfidence.HIGH
        elif score >= 0.6:
            return FormatConfidence.MEDIUM
        elif score >= 0.4:
            return FormatConfidence.LOW
        else:
            return FormatConfidence.VERY_LOW
    
    async def _extract_format_metadata(
        self,
        data: bytes,
        format_type: MediaFormat
    ) -> Dict[str, Any]:
        """Extract format-specific metadata"""
        metadata = {}
        
        try:
            if format_type == MediaFormat.JPEG:
                metadata.update(await self._extract_jpeg_metadata(data))
            elif format_type == MediaFormat.PNG:
                metadata.update(await self._extract_png_metadata(data))
            elif format_type == MediaFormat.MP3:
                metadata.update(await self._extract_mp3_metadata(data))
            elif format_type == MediaFormat.MP4:
                metadata.update(await self._extract_mp4_metadata(data))
            # Add more format-specific metadata extraction as needed
        except Exception as e:
            logger.debug(f"Metadata extraction failed for {format_type}: {str(e)}")
        
        return metadata
    
    async def _extract_jpeg_metadata(self, data: bytes) -> Dict[str, Any]:
        """Extract JPEG-specific metadata"""
        metadata = {}
        
        # Look for EXIF data
        if b'\xff\xe1' in data[:1000]:
            metadata['has_exif'] = True
        
        # Basic JPEG validation
        if data.startswith(b'\xff\xd8') and data.endswith(b'\xff\xd9'):
            metadata['valid_jpeg'] = True
        
        return metadata
    
    async def _extract_png_metadata(self, data: bytes) -> Dict[str, Any]:
        """Extract PNG-specific metadata"""
        metadata = {}
        
        # Check for text chunks
        if b'tEXt' in data or b'iTXt' in data:
            metadata['has_text_chunks'] = True
        
        # Check for transparency
        if b'tRNS' in data:
            metadata['has_transparency'] = True
        
        return metadata
    
    async def _extract_mp3_metadata(self, data: bytes) -> Dict[str, Any]:
        """Extract MP3-specific metadata"""
        metadata = {}
        
        # Check for ID3 tags
        if data.startswith(b'ID3'):
            metadata['id3_version'] = f"{data[3]}.{data[4]}"
            metadata['has_id3'] = True
        
        return metadata
    
    async def _extract_mp4_metadata(self, data: bytes) -> Dict[str, Any]:
        """Extract MP4-specific metadata"""
        metadata = {}
        
        # Look for common MP4 atoms
        atoms = [b'ftyp', b'moov', b'mdat', b'free']
        found_atoms = [atom.decode() for atom in atoms if atom in data[:1000]]
        
        if found_atoms:
            metadata['atoms_found'] = found_atoms
        
        return metadata
    
    async def _validate_format(
        self,
        data: bytes,
        detected_format: MediaFormat
    ) -> List[str]:
        """Validate detected format"""
        errors = []
        
        try:
            if detected_format == MediaFormat.JPEG:
                if not (data.startswith(b'\xff\xd8') and b'\xff\xd9' in data[-10:]):
                    errors.append("Invalid JPEG structure")
            elif detected_format == MediaFormat.PNG:
                if not data.startswith(b'\x89PNG\r\n\x1a\n'):
                    errors.append("Invalid PNG signature")
            elif detected_format == MediaFormat.GIF:
                if not (data.startswith(b'GIF87a') or data.startswith(b'GIF89a')):
                    errors.append("Invalid GIF signature")
            # Add more validation rules as needed
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return errors
    
    def _create_unknown_result(
        self,
        detection_time: float = 0.0,
        error_message: Optional[str] = None
    ) -> FormatDetectionResult:
        """Create result for unknown format"""
        result = FormatDetectionResult(
            detected_format=MediaFormat.UNKNOWN,
            media_type=MediaType.UNKNOWN,
            confidence=FormatConfidence.VERY_LOW,
            confidence_score=0.0,
            detection_time=detection_time
        )
        
        if error_message:
            result.validation_errors = [error_message]
        
        return result
    
    async def batch_detect_formats(
        self,
        sources: List[Union[str, bytes]],
        max_concurrent: int = 10
    ) -> List[FormatDetectionResult]:
        """
        Batch detect formats for multiple sources
        
        Args:
            sources: List of sources to analyze
            max_concurrent: Maximum concurrent detections
            
        Returns:
            List[FormatDetectionResult]: Detection results
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def detect_single(source: Union[str, bytes]) -> FormatDetectionResult:
            async with semaphore:
                return await self.detect_format(source)
        
        tasks = [detect_single(source) for source in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, FormatDetectionResult):
                valid_results.append(result)
            else:
                logger.error(f"Batch detection error: {str(result)}")
                valid_results.append(self._create_unknown_result(error_message=str(result)))
        
        return valid_results
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported formats by media type"""
        formats_by_type = {
            'video': [],
            'audio': [],
            'image': []
        }
        
        for format_type, media_type in self.format_type_mappings.items():
            if media_type == MediaType.VIDEO:
                formats_by_type['video'].append(format_type.value)
            elif media_type == MediaType.AUDIO:
                formats_by_type['audio'].append(format_type.value)
            elif media_type == MediaType.IMAGE:
                formats_by_type['image'].append(format_type.value)
        
        return formats_by_type
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics"""
        stats = self.stats.copy()
        
        if stats['detections_performed'] > 0:
            stats['success_rate'] = stats['successful_detections'] / stats['detections_performed']
        else:
            stats['success_rate'] = 0.0
        
        return stats
    
    def reset_statistics(self):
        """Reset detection statistics"""
        self.stats = {
            'detections_performed': 0,
            'successful_detections': 0,
            'failed_detections': 0,
            'format_counts': {},
            'confidence_distribution': {
                'very_high': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
                'very_low': 0
            }
        }
        logger.info("Detection statistics reset")
    
    async def is_format_supported(self, format_name: str) -> bool:
        """Check if format is supported"""



        try:
            MediaFormat(format_name.lower())
            return True
        except ValueError:
            return False
    
    async def get_format_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific format"""



        try:
            format_enum = MediaFormat(format_name.lower())
            media_type = self.format_type_mappings.get(format_enum, MediaType.UNKNOWN)
            
            # Find MIME types for this format
            mime_types = [mime for mime, fmt in self.mime_mappings.items() if fmt == format_enum]
            
            # Find signature information
            signatures = [sig for sig in self.format_signatures if sig.format == format_enum]
            
            return {
                'format': format_enum.value,
                'media_type': media_type.value,
                'mime_types': mime_types,
                'signature_count': len(signatures),
                'magic_bytes': [sig.magic_bytes.hex() for sig in signatures]
            }
        except ValueError:
            return None
