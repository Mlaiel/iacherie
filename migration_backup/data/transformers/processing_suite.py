"""Processing Suite - Professional format conversion and encoding for IA Influencer Agent Platform
===============================================================================================

Advanced processing suite providing industrial-grade format conversion, encoding management,
and rule-based transformation for creator workflows and enterprise content management.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple, BinaryIO, Callable
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import json
import time
import re
import hashlib
import tempfile
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class SupportedFormat(Enum):
    """Comprehensive list of supported formats."""
    
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    WMA = "wma"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WEBM = "webm"
    MKV = "mkv"
    FLV = "flv"
    WMV = "wmv"
    
    # Image formats
    JPG = "jpg"
    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    SVG = "svg"
    BMP = "bmp"
    TIFF = "tiff"
    
    # Document formats
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    RTF = "rtf"
    
    # Archive formats
    ZIP = "zip"
    RAR = "rar"
    SEVENZ = "7z"
    TAR = "tar"
    GZ = "gz"


class ConversionPriority(Enum):
    """Priority levels for conversion operations."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class QualityPreset(Enum):
    """Quality presets for conversion."""
    
    ULTRA = "ultra"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MOBILE = "mobile"
    WEB = "web"


class EncodingProfile(Enum):
    """Encoding profiles for different use cases."""
    
    STREAMING = "streaming"
    BROADCAST = "broadcast"
    ARCHIVE = "archive"
    WEB_OPTIMIZED = "web_optimized"
    MOBILE_OPTIMIZED = "mobile_optimized"
    SOCIAL_MEDIA = "social_media"


@dataclass
class ConversionRule:
    """Rule definition for format conversion."""
    
    source_format: str
    target_format: str
    quality_preset: QualityPreset = QualityPreset.MEDIUM
    encoding_profile: Optional[EncodingProfile] = None
    custom_parameters: Dict[str, Any] = field(default_factory=dict)
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: ConversionPriority = ConversionPriority.NORMAL
    enabled: bool = True
    rule_name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class ConversionRequest:
    """Request for format conversion."""
    
    input_data: Union[str, Path, bytes, BinaryIO]
    source_format: str
    target_format: str
    conversion_rule: Optional[ConversionRule] = None
    custom_parameters: Optional[Dict[str, Any]] = None
    output_path: Optional[str] = None
    preserve_metadata: bool = True
    validate_output: bool = True
    priority: ConversionPriority = ConversionPriority.NORMAL


@dataclass
class ConversionResult:
    """Result of format conversion operation."""
    
    success: bool
    output_data: Optional[bytes] = None
    output_path: Optional[str] = None
    source_format: Optional[str] = None
    target_format: Optional[str] = None
    file_size_original: Optional[int] = None
    file_size_converted: Optional[int] = None
    compression_ratio: Optional[float] = None
    processing_time: float = 0.0
    quality_score: Optional[float] = None
    metadata_preserved: bool = False
    conversion_rule_applied: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    validation_passed: bool = False


@dataclass
class EncodingSettings:
    """Configuration for encoding operations."""
    
    codec: Optional[str] = None
    bitrate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    quality: Optional[int] = None
    compression_level: Optional[int] = None
    profile: Optional[str] = None
    preset: Optional[str] = None
    custom_options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EncodingResult:
    """Result of encoding operation."""
    
    success: bool
    encoded_data: Optional[bytes] = None
    encoding_settings: Optional[EncodingSettings] = None
    original_size: Optional[int] = None
    encoded_size: Optional[int] = None
    compression_achieved: Optional[float] = None
    quality_retained: Optional[float] = None
    encoding_time: float = 0.0
    error_message: Optional[str] = None


class FormatConverter:
    """Universal format converter with intelligent processing."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize format converter with configuration."""
        self.config = config or {}
        self.supported_formats = [fmt.value for fmt in SupportedFormat]
        self.conversion_rules = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Initialize format support matrix
        self._init_format_support_matrix()
        
        # Load default conversion rules
        self._load_default_conversion_rules()
        
        logger.info("FormatConverter initialized")
    
    def _init_format_support_matrix(self):
        """Initialize the format support matrix."""
        self.format_categories = {
            "audio": ["mp3", "wav", "flac", "aac", "ogg", "m4a", "wma"],
            "video": ["mp4", "avi", "mov", "webm", "mkv", "flv", "wmv"],
            "image": ["jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "tiff"],
            "document": ["pdf", "docx", "txt", "md", "html", "rtf"],
            "archive": ["zip", "rar", "7z", "tar", "gz"]
        }
        
        # Create reverse mapping
        self.format_to_category = {}
        for category, formats in self.format_categories.items():
            for fmt in formats:
                self.format_to_category[fmt] = category
    
    def _load_default_conversion_rules(self):
        """Load default conversion rules for common scenarios."""
        default_rules = [
            # Audio conversions
            ConversionRule(
                source_format="wav",
                target_format="mp3",
                quality_preset=QualityPreset.HIGH,
                rule_name="wav_to_mp3_high_quality"
            ),
            ConversionRule(
                source_format="flac",
                target_format="mp3",
                quality_preset=QualityPreset.HIGH,
                rule_name="flac_to_mp3_high_quality"
            ),
            
            # Video conversions
            ConversionRule(
                source_format="avi",
                target_format="mp4",
                quality_preset=QualityPreset.HIGH,
                encoding_profile=EncodingProfile.WEB_OPTIMIZED,
                rule_name="avi_to_mp4_web"
            ),
            ConversionRule(
                source_format="mov",
                target_format="mp4",
                quality_preset=QualityPreset.HIGH,
                rule_name="mov_to_mp4_high_quality"
            ),
            
            # Image conversions
            ConversionRule(
                source_format="png",
                target_format="jpg",
                quality_preset=QualityPreset.HIGH,
                rule_name="png_to_jpg_high_quality"
            ),
            ConversionRule(
                source_format="bmp",
                target_format="png",
                quality_preset=QualityPreset.MEDIUM,
                rule_name="bmp_to_png_optimize"
            ),
            
            # Document conversions
            ConversionRule(
                source_format="docx",
                target_format="pdf",
                quality_preset=QualityPreset.HIGH,
                rule_name="docx_to_pdf_high_quality"
            ),
            ConversionRule(
                source_format="md",
                target_format="html",
                quality_preset=QualityPreset.HIGH,
                rule_name="markdown_to_html"
            )
        ]
        
        for rule in default_rules:
            rule_key = f"{rule.source_format}_to_{rule.target_format}"
            self.conversion_rules[rule_key] = rule
    
    async def convert(self, request: ConversionRequest) -> ConversionResult:
        """
        Convert file from source format to target format.
        
        Args:
            request: Conversion request with all parameters
            
        Returns:
            ConversionResult with processing details
        """
        start_time = time.time()
        
        try:
            # Validate formats
            validation_result = await self._validate_conversion_request(request)
            if not validation_result["valid"]:
                return ConversionResult(
                    success=False,
                    error_message=validation_result["error"]
                )
            
            # Determine conversion rule
            conversion_rule = await self._determine_conversion_rule(request)
            
            # Prepare conversion parameters
            conversion_params = await self._prepare_conversion_parameters(request, conversion_rule)
            
            # Perform the conversion
            conversion_result = await self._perform_conversion(request, conversion_params)
            
            # Validate output if requested
            if request.validate_output and conversion_result.success:
                validation_passed = await self._validate_conversion_output(conversion_result)
                conversion_result.validation_passed = validation_passed
            
            # Calculate metrics
            conversion_result.processing_time = time.time() - start_time
            conversion_result.conversion_rule_applied = conversion_rule.rule_name if conversion_rule else None
            
            return conversion_result
            
        except Exception as e:
            logger.error(f"Format conversion failed: {str(e)}")
            return ConversionResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    async def _validate_conversion_request(self, request: ConversionRequest) -> Dict[str, Any]:
        """Validate the conversion request."""
        if request.source_format not in self.supported_formats:
            return {
                "valid": False,
                "error": f"Unsupported source format: {request.source_format}"
            }
        
        if request.target_format not in self.supported_formats:
            return {
                "valid": False,
                "error": f"Unsupported target format: {request.target_format}"
            }
        
        # Check if conversion is possible (same category or supported cross-category)
        source_category = self.format_to_category.get(request.source_format)
        target_category = self.format_to_category.get(request.target_format)
        
        if source_category != target_category:
            # Check if cross-category conversion is supported
            supported_cross_conversions = [
                ("document", "image"),  # Document to image (screenshot)
                ("video", "audio"),     # Video to audio extraction
                ("video", "image")      # Video to image (frame extraction)
            ]
            
            if (source_category, target_category) not in supported_cross_conversions:
                return {
                    "valid": False,
                    "error": f"Cross-category conversion not supported: {source_category} to {target_category}"
                }
        
        return {"valid": True}
    
    async def _determine_conversion_rule(self, request: ConversionRequest) -> Optional[ConversionRule]:
        """Determine the appropriate conversion rule to use."""
        # Use explicitly provided rule if available
        if request.conversion_rule:
            return request.conversion_rule
        
        # Look for existing rule
        rule_key = f"{request.source_format}_to_{request.target_format}"
        if rule_key in self.conversion_rules:
            return self.conversion_rules[rule_key]
        
        # Create default rule
        return ConversionRule(
            source_format=request.source_format,
            target_format=request.target_format,
            quality_preset=QualityPreset.MEDIUM,
            priority=request.priority,
            rule_name=f"default_{rule_key}"
        )
    
    async def _prepare_conversion_parameters(
        self, request: ConversionRequest, rule: ConversionRule
    ) -> Dict[str, Any]:
        """Prepare parameters for the conversion operation."""
        params = {
            "source_format": request.source_format,
            "target_format": request.target_format,
            "quality_preset": rule.quality_preset,
            "encoding_profile": rule.encoding_profile,
            "preserve_metadata": request.preserve_metadata,
            "priority": request.priority
        }
        
        # Merge custom parameters from rule and request
        if rule.custom_parameters:
            params.update(rule.custom_parameters)
        
        if request.custom_parameters:
            params.update(request.custom_parameters)
        
        return params
    
    async def _perform_conversion(
        self, request: ConversionRequest, params: Dict[str, Any]
    ) -> ConversionResult:
        """Perform the actual format conversion."""
        try:
            # Get input data size
            input_size = await self._get_data_size(request.input_data)
            
            # Perform format-specific conversion
            source_category = self.format_to_category.get(request.source_format)
            target_category = self.format_to_category.get(request.target_format)
            
            if source_category == target_category:
                # Same category conversion
                output_data = await self._convert_same_category(request, params)
            else:
                # Cross-category conversion
                output_data = await self._convert_cross_category(request, params)
            
            # Calculate metrics
            output_size = len(output_data) if output_data else 0
            compression_ratio = output_size / input_size if input_size > 0 else 0.0
            quality_score = await self._estimate_quality_score(request, params)
            
            return ConversionResult(
                success=True,
                output_data=output_data,
                source_format=request.source_format,
                target_format=request.target_format,
                file_size_original=input_size,
                file_size_converted=output_size,
                compression_ratio=compression_ratio,
                quality_score=quality_score,
                metadata_preserved=request.preserve_metadata
            )
            
        except Exception as e:
            logger.error(f"Conversion operation failed: {str(e)}")
            return ConversionResult(
                success=False,
                error_message=str(e)
            )
    
    async def _convert_same_category(self, request: ConversionRequest, params: Dict[str, Any]) -> bytes:
        """Convert within the same format category."""
        # Placeholder implementation - would use appropriate libraries in production
        logger.info(f"Converting {request.source_format} to {request.target_format}")
        
        # Simulate conversion processing
        await asyncio.sleep(0.1)
        
        # Return placeholder converted data
        return f"converted_{request.target_format}_data_placeholder".encode()
    
    async def _convert_cross_category(self, request: ConversionRequest, params: Dict[str, Any]) -> bytes:
        """Convert across different format categories."""
        # Placeholder implementation for cross-category conversions
        logger.info(f"Cross-category conversion: {request.source_format} to {request.target_format}")
        
        # Simulate more complex processing
        await asyncio.sleep(0.3)
        
        # Return placeholder converted data
        return f"cross_converted_{request.target_format}_data_placeholder".encode()
    
    async def _get_data_size(self, data: Union[str, Path, bytes, BinaryIO]) -> int:
        """Get the size of input data."""
        if isinstance(data, bytes):
            return len(data)
        elif isinstance(data, (str, Path)):
            try:
                return Path(data).stat().st_size
            except:
                return 0
        else:
            # For file-like objects, try to get size
            try:
                current_pos = data.tell()
                data.seek(0, 2)  # Seek to end
                size = data.tell()
                data.seek(current_pos)  # Restore position
                return size
            except:
                return 0
    
    async def _estimate_quality_score(self, request: ConversionRequest, params: Dict[str, Any]) -> float:
        """Estimate quality score for the conversion."""
        quality_preset = params.get("quality_preset", QualityPreset.MEDIUM)
        
        quality_scores = {
            QualityPreset.ULTRA: 0.95,
            QualityPreset.HIGH: 0.85,
            QualityPreset.MEDIUM: 0.75,
            QualityPreset.LOW: 0.60,
            QualityPreset.MOBILE: 0.65,
            QualityPreset.WEB: 0.70
        }
        
        return quality_scores.get(quality_preset, 0.75)
    
    async def _validate_conversion_output(self, result: ConversionResult) -> bool:
        """Validate the conversion output."""
        # Basic validation
        if not result.output_data:
            return False
        
        if len(result.output_data) == 0:
            return False
        
        # Format-specific validation would go here
        # For now, return True for placeholder implementation
        return True
    
    def add_conversion_rule(self, rule: ConversionRule) -> bool:
        """
        Add a new conversion rule.
        
        Args:
            rule: ConversionRule to add
            
        Returns:
            True if rule was added successfully
        """
        try:
            rule_key = f"{rule.source_format}_to_{rule.target_format}"
            rule.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
            rule.updated_at = rule.created_at
            
            self.conversion_rules[rule_key] = rule
            logger.info(f"Added conversion rule: {rule_key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add conversion rule: {str(e)}")
            return False
    
    def remove_conversion_rule(self, source_format: str, target_format: str) -> bool:
        """Remove a conversion rule."""
        try:
            rule_key = f"{source_format}_to_{target_format}"
            if rule_key in self.conversion_rules:
                del self.conversion_rules[rule_key]
                logger.info(f"Removed conversion rule: {rule_key}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove conversion rule: {str(e)}")
            return False
    
    def get_supported_conversions(self, source_format: str) -> List[str]:
        """Get list of supported target formats for a source format."""
        source_category = self.format_to_category.get(source_format)
        if not source_category:
            return []
        
        # Same category conversions
        supported = list(self.format_categories[source_category])
        
        # Add supported cross-category conversions
        if source_category == "video":
            supported.extend(self.format_categories["audio"])  # Video to audio
            supported.extend(self.format_categories["image"])  # Video to image
        elif source_category == "document":
            supported.extend(self.format_categories["image"])  # Document to image
        
        # Remove source format from list
        if source_format in supported:
            supported.remove(source_format)
        
        return supported


class EncodingManager:
    """Advanced encoding management for media optimization."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize encoding manager with configuration."""
        self.config = config or {}
        self.encoding_profiles = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=2)
        
        # Initialize encoding profiles
        self._init_encoding_profiles()
        
        logger.info("EncodingManager initialized")
    
    def _init_encoding_profiles(self):
        """Initialize predefined encoding profiles."""
        self.encoding_profiles = {
            EncodingProfile.STREAMING: {
                "video": {
                    "codec": "h264",
                    "bitrate": 2000000,  # 2 Mbps
                    "fps": 30,
                    "preset": "fast"
                },
                "audio": {
                    "codec": "aac",
                    "bitrate": 128000,  # 128 kbps
                    "sample_rate": 44100,
                    "channels": 2
                }
            },
            
            EncodingProfile.BROADCAST: {
                "video": {
                    "codec": "h264",
                    "bitrate": 8000000,  # 8 Mbps
                    "fps": 30,
                    "preset": "slow"
                },
                "audio": {
                    "codec": "aac",
                    "bitrate": 320000,  # 320 kbps
                    "sample_rate": 48000,
                    "channels": 2
                }
            },
            
            EncodingProfile.ARCHIVE: {
                "video": {
                    "codec": "h265",
                    "quality": 23,  # CRF value
                    "preset": "veryslow"
                },
                "audio": {
                    "codec": "flac",
                    "sample_rate": 48000,
                    "channels": 2
                }
            },
            
            EncodingProfile.WEB_OPTIMIZED: {
                "video": {
                    "codec": "h264",
                    "bitrate": 1500000,  # 1.5 Mbps
                    "width": 1280,
                    "height": 720,
                    "fps": 30,
                    "preset": "medium"
                },
                "audio": {
                    "codec": "aac",
                    "bitrate": 128000,
                    "sample_rate": 44100,
                    "channels": 2
                }
            },
            
            EncodingProfile.MOBILE_OPTIMIZED: {
                "video": {
                    "codec": "h264",
                    "bitrate": 800000,  # 800 kbps
                    "width": 854,
                    "height": 480,
                    "fps": 24,
                    "preset": "fast"
                },
                "audio": {
                    "codec": "aac",
                    "bitrate": 96000,
                    "sample_rate": 44100,
                    "channels": 2
                }
            },
            
            EncodingProfile.SOCIAL_MEDIA: {
                "video": {
                    "codec": "h264",
                    "bitrate": 1200000,  # 1.2 Mbps
                    "width": 1080,
                    "height": 1080,  # Square format
                    "fps": 30,
                    "preset": "medium"
                },
                "audio": {
                    "codec": "aac",
                    "bitrate": 128000,
                    "sample_rate": 44100,
                    "channels": 2
                }
            }
        }
    
    async def encode(
        self,
        input_data: Union[str, Path, bytes, BinaryIO],
        settings: EncodingSettings,
        profile: Optional[EncodingProfile] = None
    ) -> EncodingResult:
        """
        Encode media with specified settings.
        
        Args:
            input_data: Input media data
            settings: Encoding settings to apply
            profile: Optional encoding profile to use
            
        Returns:
            EncodingResult with processing details
        """
        start_time = time.time()
        
        try:
            # Apply profile settings if specified
            if profile:
                settings = await self._apply_profile_settings(settings, profile)
            
            # Validate encoding settings
            validation_result = await self._validate_encoding_settings(settings)
            if not validation_result["valid"]:
                return EncodingResult(
                    success=False,
                    error_message=validation_result["error"]
                )
            
            # Get input data size
            original_size = await self._get_input_size(input_data)
            
            # Perform encoding
            encoded_data = await self._perform_encoding(input_data, settings)
            
            # Calculate metrics
            encoded_size = len(encoded_data) if encoded_data else 0
            compression_achieved = 1.0 - (encoded_size / original_size) if original_size > 0 else 0.0
            quality_retained = await self._estimate_quality_retention(settings)
            
            return EncodingResult(
                success=True,
                encoded_data=encoded_data,
                encoding_settings=settings,
                original_size=original_size,
                encoded_size=encoded_size,
                compression_achieved=compression_achieved,
                quality_retained=quality_retained,
                encoding_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Encoding failed: {str(e)}")
            return EncodingResult(
                success=False,
                error_message=str(e),
                encoding_time=time.time() - start_time
            )
    
    async def _apply_profile_settings(self, settings: EncodingSettings, profile: EncodingProfile) -> EncodingSettings:
        """Apply encoding profile settings to the encoding settings."""
        profile_data = self.encoding_profiles.get(profile, {})
        
        # Determine media type based on settings
        media_type = "video" if settings.width or settings.height or settings.fps else "audio"
        profile_settings = profile_data.get(media_type, {})
        
        # Apply profile settings (original settings take precedence)
        for key, value in profile_settings.items():
            if not hasattr(settings, key) or getattr(settings, key) is None:
                setattr(settings, key, value)
        
        return settings
    
    async def _validate_encoding_settings(self, settings: EncodingSettings) -> Dict[str, Any]:
        """Validate encoding settings."""
        # Basic validation
        if settings.bitrate and settings.bitrate <= 0:
            return {"valid": False, "error": "Bitrate must be positive"}
        
        if settings.sample_rate and settings.sample_rate not in [8000, 16000, 22050, 44100, 48000, 96000]:
            return {"valid": False, "error": "Invalid sample rate"}
        
        if settings.channels and settings.channels not in [1, 2, 6, 8]:
            return {"valid": False, "error": "Invalid channel count"}
        
        if settings.width and settings.width <= 0:
            return {"valid": False, "error": "Width must be positive"}
        
        if settings.height and settings.height <= 0:
            return {"valid": False, "error": "Height must be positive"}
        
        if settings.fps and settings.fps <= 0:
            return {"valid": False, "error": "FPS must be positive"}
        
        return {"valid": True}
    
    async def _get_input_size(self, input_data: Union[str, Path, bytes, BinaryIO]) -> int:
        """Get input data size."""
        if isinstance(input_data, bytes):
            return len(input_data)
        elif isinstance(input_data, (str, Path)):
            try:
                return Path(input_data).stat().st_size
            except:
                return 0
        else:
            try:
                current_pos = input_data.tell()
                input_data.seek(0, 2)
                size = input_data.tell()
                input_data.seek(current_pos)
                return size
            except:
                return 0
    
    async def _perform_encoding(self, input_data: Union[str, Path, bytes, BinaryIO], settings: EncodingSettings) -> bytes:
        """Perform the actual encoding operation."""
        # Placeholder implementation - would use FFmpeg/other encoders in production
        logger.info(f"Encoding with codec: {settings.codec}, bitrate: {settings.bitrate}")
        
        # Simulate encoding processing
        await asyncio.sleep(0.2)
        
        # Return placeholder encoded data
        return f"encoded_data_with_{settings.codec or 'default'}_codec".encode()
    
    async def _estimate_quality_retention(self, settings: EncodingSettings) -> float:
        """Estimate quality retention based on encoding settings."""
        # Simple heuristic based on bitrate and quality settings
        base_quality = 0.8
        
        if settings.quality:
            # Lower CRF/quality values typically mean higher quality
            if settings.quality <= 18:
                base_quality = 0.95
            elif settings.quality <= 23:
                base_quality = 0.85
            elif settings.quality <= 28:
                base_quality = 0.75
            else:
                base_quality = 0.65
        elif settings.bitrate:
            # Higher bitrates typically mean better quality
            if settings.bitrate >= 5000000:  # 5 Mbps+
                base_quality = 0.90
            elif settings.bitrate >= 2000000:  # 2 Mbps+
                base_quality = 0.80
            elif settings.bitrate >= 1000000:  # 1 Mbps+
                base_quality = 0.70
            else:
                base_quality = 0.60
        
        return base_quality
    
    def get_profile_settings(self, profile: EncodingProfile, media_type: str = "video") -> Dict[str, Any]:
        """Get settings for a specific encoding profile."""
        return self.encoding_profiles.get(profile, {}).get(media_type, {})
    
    def add_custom_profile(self, profile_name: str, settings: Dict[str, Dict[str, Any]]) -> bool:
        """Add a custom encoding profile."""
        try:
            # Convert string to enum-like key for consistency
            custom_profile_key = f"CUSTOM_{profile_name.upper()}"
            self.encoding_profiles[custom_profile_key] = settings
            logger.info(f"Added custom encoding profile: {profile_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add custom profile: {str(e)}")
            return False


class QualityController:
    """Quality control and validation for conversion operations."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize quality controller with configuration."""
        self.config = config or {}
        self.quality_thresholds = {
            "minimum_quality": 0.6,
            "target_quality": 0.8,
            "maximum_compression": 0.9,
            "minimum_bitrate": 64000,  # 64 kbps minimum
        }
        
        logger.info("QualityController initialized")
    
    async def validate_quality(self, result: ConversionResult) -> Dict[str, Any]:
        """
        Validate the quality of conversion result.
        
        Args:
            result: ConversionResult to validate
            
        Returns:
            Quality validation report
        """
        try:
            validation_report = {
                "passed": True,
                "issues": [],
                "warnings": [],
                "metrics": {},
                "recommendations": []
            }
            
            # Check quality score
            if result.quality_score is not None:
                validation_report["metrics"]["quality_score"] = result.quality_score
                
                if result.quality_score < self.quality_thresholds["minimum_quality"]:
                    validation_report["passed"] = False
                    validation_report["issues"].append(
                        f"Quality score {result.quality_score:.2f} below minimum threshold "
                        f"{self.quality_thresholds['minimum_quality']}"
                    )
                elif result.quality_score < self.quality_thresholds["target_quality"]:
                    validation_report["warnings"].append(
                        f"Quality score {result.quality_score:.2f} below target threshold "
                        f"{self.quality_thresholds['target_quality']}"
                    )
            
            # Check compression ratio
            if result.compression_ratio is not None:
                validation_report["metrics"]["compression_ratio"] = result.compression_ratio
                
                if result.compression_ratio > self.quality_thresholds["maximum_compression"]:
                    validation_report["warnings"].append(
                        f"High compression ratio {result.compression_ratio:.2f} may affect quality"
                    )
            
            # Check file size reduction
            if result.file_size_original and result.file_size_converted:
                size_reduction = 1.0 - (result.file_size_converted / result.file_size_original)
                validation_report["metrics"]["size_reduction"] = size_reduction
                
                if size_reduction > 0.95:  # More than 95% reduction
                    validation_report["warnings"].append(
                        f"Extreme size reduction {size_reduction:.2f} detected"
                    )
            
            # Generate recommendations
            if validation_report["issues"] or validation_report["warnings"]:
                validation_report["recommendations"] = await self._generate_quality_recommendations(
                    result, validation_report
                )
            
            return validation_report
            
        except Exception as e:
            logger.error(f"Quality validation failed: {str(e)}")
            return {
                "passed": False,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _generate_quality_recommendations(
        self, result: ConversionResult, validation_report: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for quality improvement."""
        recommendations = []
        
        # Quality-based recommendations
        if result.quality_score and result.quality_score < self.quality_thresholds["target_quality"]:
            recommendations.append("Consider using higher quality preset")
            recommendations.append("Review encoding parameters for quality optimization")
        
        # Compression-based recommendations
        if result.compression_ratio and result.compression_ratio > 0.8:
            recommendations.append("Consider reducing compression level")
            recommendations.append("Use lossless format if file size permits")
        
        # Format-specific recommendations
        if result.target_format in ["jpg", "jpeg"]:
            recommendations.append("For photos, consider PNG for better quality")
        elif result.target_format == "mp3":
            recommendations.append("For music, consider FLAC for archival quality")
        
        return recommendations
    
    def update_quality_thresholds(self, thresholds: Dict[str, float]) -> bool:
        """Update quality validation thresholds."""
        try:
            self.quality_thresholds.update(thresholds)
            logger.info("Quality thresholds updated")
            return True
        except Exception as e:
            logger.error(f"Failed to update quality thresholds: {str(e)}")
            return False


class BatchConverter:
    """Batch processing for multiple file conversions."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize batch converter with configuration."""
        self.config = config or {}
        self.format_converter = FormatConverter(config)
        self.max_concurrent = config.get("max_concurrent_conversions", 3)
        
        logger.info("BatchConverter initialized")
    
    async def convert_batch(
        self,
        requests: List[ConversionRequest],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[ConversionResult]:
        """
        Convert multiple files in batch.
        
        Args:
            requests: List of conversion requests
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of conversion results
        """
        try:
            results = []
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            async def convert_single(request: ConversionRequest, index: int) -> ConversionResult:
                async with semaphore:
                    result = await self.format_converter.convert(request)
                    if progress_callback:
                        progress_callback(index + 1, len(requests))
                    return result
            
            # Create tasks for all conversions
            tasks = [
                convert_single(request, i)
                for i, request in enumerate(requests)
            ]
            
            # Execute all conversions
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(ConversionResult(
                        success=False,
                        error_message=str(result)
                    ))
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Batch conversion failed: {str(e)}")
            return [ConversionResult(success=False, error_message=str(e)) for _ in requests]
    
    async def get_batch_statistics(self, results: List[ConversionResult]) -> Dict[str, Any]:
        """Get statistics for batch conversion results."""
        total_conversions = len(results)
        successful_conversions = sum(1 for r in results if r.success)
        failed_conversions = total_conversions - successful_conversions
        
        total_processing_time = sum(r.processing_time for r in results)
        avg_processing_time = total_processing_time / total_conversions if total_conversions > 0 else 0
        
        total_original_size = sum(r.file_size_original or 0 for r in results)
        total_converted_size = sum(r.file_size_converted or 0 for r in results)
        overall_compression = 1.0 - (total_converted_size / total_original_size) if total_original_size > 0 else 0
        
        return {
            "total_conversions": total_conversions,
            "successful_conversions": successful_conversions,
            "failed_conversions": failed_conversions,
            "success_rate": successful_conversions / total_conversions if total_conversions > 0 else 0,
            "total_processing_time": total_processing_time,
            "average_processing_time": avg_processing_time,
            "total_original_size": total_original_size,
            "total_converted_size": total_converted_size,
            "overall_compression_ratio": overall_compression
        }


class FormatRegistry:
    """Registry for managing supported formats and their capabilities."""
    
    def __init__(self):
        """Initialize format registry."""
        self.formats = {}
        self._register_default_formats()
        
        logger.info("FormatRegistry initialized")
    
    def _register_default_formats(self):
        """Register default supported formats."""
        # Audio formats
        audio_formats = {
            "mp3": {"category": "audio", "lossy": True, "quality": "good", "compatibility": "excellent"},
            "wav": {"category": "audio", "lossy": False, "quality": "excellent", "compatibility": "excellent"},
            "flac": {"category": "audio", "lossy": False, "quality": "excellent", "compatibility": "good"},
            "aac": {"category": "audio", "lossy": True, "quality": "good", "compatibility": "good"},
            "ogg": {"category": "audio", "lossy": True, "quality": "good", "compatibility": "fair"},
            "m4a": {"category": "audio", "lossy": True, "quality": "good", "compatibility": "good"}
        }
        
        # Video formats
        video_formats = {
            "mp4": {"category": "video", "lossy": True, "quality": "good", "compatibility": "excellent"},
            "avi": {"category": "video", "lossy": True, "quality": "good", "compatibility": "good"},
            "mov": {"category": "video", "lossy": True, "quality": "good", "compatibility": "good"},
            "webm": {"category": "video", "lossy": True, "quality": "good", "compatibility": "fair"},
            "mkv": {"category": "video", "lossy": True, "quality": "excellent", "compatibility": "fair"}
        }
        
        # Image formats
        image_formats = {
            "jpg": {"category": "image", "lossy": True, "quality": "good", "compatibility": "excellent"},
            "png": {"category": "image", "lossy": False, "quality": "excellent", "compatibility": "excellent"},
            "gif": {"category": "image", "lossy": True, "quality": "fair", "compatibility": "excellent"},
            "webp": {"category": "image", "lossy": True, "quality": "good", "compatibility": "good"},
            "svg": {"category": "image", "lossy": False, "quality": "excellent", "compatibility": "good"}
        }
        
        # Document formats
        document_formats = {
            "pdf": {"category": "document", "lossy": False, "quality": "excellent", "compatibility": "excellent"},
            "docx": {"category": "document", "lossy": False, "quality": "good", "compatibility": "good"},
            "txt": {"category": "document", "lossy": False, "quality": "basic", "compatibility": "excellent"},
            "html": {"category": "document", "lossy": False, "quality": "good", "compatibility": "excellent"},
            "md": {"category": "document", "lossy": False, "quality": "good", "compatibility": "good"}
        }
        
        # Register all formats
        self.formats.update(audio_formats)
        self.formats.update(video_formats)
        self.formats.update(image_formats)
        self.formats.update(document_formats)
    
    def get_format_info(self, format_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific format."""
        return self.formats.get(format_name.lower())
    
    def is_format_supported(self, format_name: str) -> bool:
        """Check if a format is supported."""
        return format_name.lower() in self.formats
    
    def get_formats_by_category(self, category: str) -> List[str]:
        """Get all formats in a specific category."""
        return [
            fmt for fmt, info in self.formats.items()
            if info.get("category") == category
        ]
    
    def get_lossless_formats(self) -> List[str]:
        """Get all lossless formats."""
        return [
            fmt for fmt, info in self.formats.items()
            if not info.get("lossy", True)
        ]


# Export all classes for module imports
__all__ = [
    "FormatConverter",
    "EncodingManager",
    "QualityController",
    "BatchConverter",
    "FormatRegistry",
    "SupportedFormat",
    "ConversionPriority",
    "QualityPreset",
    "EncodingProfile",
    "ConversionRule",
    "ConversionRequest",
    "ConversionResult",
    "EncodingSettings",
    "EncodingResult"
]

logger.info("Processing suite module loaded successfully")