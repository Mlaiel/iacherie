"""Advanced Multi-Format Processor
===============================

Professional multi-format content processing engine for the IA Influencer Agent platform.
Provides intelligent content transformation, format conversion, and AI-powered routing
with enterprise-grade performance and optimization capabilities.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is proprietary and confidential. Any unauthorized copying, distribution,
or use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and will result in legal action.
"""

import asyncio
import logging
import uuid
import tempfile
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import hashlib

# Media processing libraries
import librosa
import soundfile as sf
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import ffmpeg

# Core exceptions
try:
    from core.exceptions import ProcessingError, TransformationError, RoutingError
except ImportError:
    # Fallback exception classes
    class ProcessingError(Exception): pass
    class TransformationError(Exception): pass
    class RoutingError(Exception): pass


class ProcessingQuality(Enum):
    """Content processing quality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"
    LOSSLESS = "lossless"


class OutputFormat(Enum):
    """Supported output formats"""
    # Audio formats
    MP3 = "mp3"
    WAV = "wav"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    
    # Image formats
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"
    
    # Document formats
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"
    TXT = "txt"
    
    # Special formats
    JSON = "json"
    XML = "xml"


class TransformationType(Enum):
    """Content transformation types"""
    FORMAT_CONVERSION = "format_conversion"
    QUALITY_ENHANCEMENT = "quality_enhancement"
    COMPRESSION = "compression"
    OPTIMIZATION = "optimization"
    NORMALIZATION = "normalization"
    ENHANCEMENT = "enhancement"
    FILTERING = "filtering"
    TRANSCODING = "transcoding"


class Platform(Enum):
    """Target platform types"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PODCAST = "podcast"
    BLOG = "blog"
    WEBSITE = "website"
    UNIVERSAL = "universal"


class PlatformType(Enum):
    """Platform category types"""
    SOCIAL_MEDIA = "social_media"
    VIDEO_PLATFORM = "video_platform"
    AUDIO_PLATFORM = "audio_platform"
    PROFESSIONAL = "professional"
    BLOG_PLATFORM = "blog_platform"
    STREAMING = "streaming"


class ContentCategory(Enum):
    """Content category classifications"""
    MUSIC = "music"
    PODCAST = "podcast"
    VIDEO_CONTENT = "video_content"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"
    CREATIVE = "creative"
    NEWS = "news"
    LIFESTYLE = "lifestyle"


class RoutingStrategy(Enum):
    """Content routing strategies"""
    OPTIMAL_QUALITY = "optimal_quality"
    MAXIMUM_REACH = "maximum_reach"
    COST_EFFECTIVE = "cost_effective"
    FASTEST_DELIVERY = "fastest_delivery"
    ENGAGEMENT_FOCUSED = "engagement_focused"
    REVENUE_OPTIMIZED = "revenue_optimized"


class RoutingPriority(Enum):
    """Routing priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    IMMEDIATE = "immediate"


@dataclass
class ProcessingOptions:
    """Content processing configuration options"""
    quality: ProcessingQuality = ProcessingQuality.HIGH
    output_format: Optional[OutputFormat] = None
    target_platforms: List[Platform] = field(default_factory=list)
    compression_level: int = 5  # 1-10 scale
    preserve_metadata: bool = True
    enhance_quality: bool = True
    optimize_for_web: bool = False
    custom_parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformationParams:
    """Content transformation parameters"""
    transformation_type: TransformationType
    source_format: str
    target_format: str
    quality_settings: Dict[str, Any] = field(default_factory=dict)
    processing_options: Optional[ProcessingOptions] = None
    custom_filters: List[str] = field(default_factory=list)
    metadata_overrides: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransformationResult:
    """Content transformation result"""
    transformation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    output_data: Optional[bytes] = None
    output_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    processing_time: Optional[float] = None
    file_size_reduction: Optional[float] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ProcessingResult:
    """Multi-format processing result"""
    processing_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"
    transformations: List[TransformationResult] = field(default_factory=list)
    routing_decisions: List[Dict[str, Any]] = field(default_factory=list)
    optimization_results: Dict[str, Any] = field(default_factory=dict)
    total_processing_time: Optional[float] = None
    success_rate: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoutingRule:
    """Content routing rule specification"""
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform: Platform
    content_category: ContentCategory
    required_format: OutputFormat
    quality_requirements: Dict[str, Any] = field(default_factory=dict)
    optimization_settings: Dict[str, Any] = field(default_factory=dict)
    priority: RoutingPriority = RoutingPriority.NORMAL
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RoutingDecision:
    """Individual routing decision"""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    platform: Platform
    recommended_format: OutputFormat
    quality_level: ProcessingQuality
    optimization_score: float = 0.0
    confidence: float = 0.0
    reasons: List[str] = field(default_factory=list)
    estimated_performance: Dict[str, float] = field(default_factory=dict)


@dataclass
class RoutingPlan:
    """Complete routing plan for content"""
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strategy: RoutingStrategy
    decisions: List[RoutingDecision] = field(default_factory=list)
    total_platforms: int = 0
    estimated_reach: int = 0
    cost_estimate: float = 0.0
    processing_requirements: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoutingResult:
    """Content routing execution result"""
    routing_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    plan: RoutingPlan
    executed_decisions: List[RoutingDecision] = field(default_factory=list)
    delivery_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    success_rate: float = 0.0
    completion_time: Optional[datetime] = None


class MultiFormatProcessor:
    """
    Professional multi-format content processor for enterprise content transformation.
    
    Provides comprehensive format conversion, quality enhancement, and optimization
    capabilities for audio, video, image, and document content processing.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize multi-format processor"""
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Processing capabilities
        self.supported_inputs = {
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a', '.wma'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
            'document': ['.pdf', '.docx', '.doc', '.rtf', '.odt', '.txt', '.md']
        }
        
        # Quality profiles for different processing levels
        self.quality_profiles = {
            ProcessingQuality.LOW: {'bitrate': 128, 'resolution_scale': 0.5, 'compression': 8},
            ProcessingQuality.MEDIUM: {'bitrate': 256, 'resolution_scale': 0.75, 'compression': 6},
            ProcessingQuality.HIGH: {'bitrate': 320, 'resolution_scale': 1.0, 'compression': 4},
            ProcessingQuality.ULTRA: {'bitrate': 512, 'resolution_scale': 1.2, 'compression': 2},
            ProcessingQuality.LOSSLESS: {'bitrate': None, 'resolution_scale': 1.0, 'compression': 0}
        }
        
        # Platform optimization presets
        self.platform_presets = {
            Platform.YOUTUBE: {
                'video': {'format': 'mp4', 'max_resolution': '1920x1080', 'fps': 30},
                'audio': {'format': 'aac', 'bitrate': 128, 'sample_rate': 48000}
            },
            Platform.INSTAGRAM: {
                'video': {'format': 'mp4', 'max_resolution': '1080x1080', 'fps': 30},
                'image': {'format': 'jpeg', 'max_size': '1080x1080', 'quality': 90}
            },
            Platform.TIKTOK: {
                'video': {'format': 'mp4', 'max_resolution': '1080x1920', 'fps': 30},
                'audio': {'format': 'aac', 'bitrate': 128}
            }
        }
    
    async def process_content(self, content_data: bytes, filename: str,
                            options: ProcessingOptions) -> ProcessingResult:
        """
        Process content with multi-format transformation capabilities.
        
        Args:
            content_data: Source content data
            filename: Original filename
            options: Processing configuration options
            
        Returns:
            Complete processing result with transformations
        """
        start_time = datetime.utcnow()
        result = ProcessingResult()
        
        try:
            self.logger.info(f"Starting multi-format processing: {filename}")
            
            # Detect content type and format
            content_type, source_format = self._detect_content_type(filename, content_data)
            result.optimization_results['source_format'] = source_format
            result.optimization_results['content_type'] = content_type
            
            # Process based on content type
            if content_type == 'audio':
                transformations = await self._process_audio_content(
                    content_data, filename, options
                )
            elif content_type == 'video':
                transformations = await self._process_video_content(
                    content_data, filename, options
                )
            elif content_type == 'image':
                transformations = await self._process_image_content(
                    content_data, filename, options
                )
            elif content_type == 'document':
                transformations = await self._process_document_content(
                    content_data, filename, options
                )
            else:
                raise ProcessingError(f"Unsupported content type: {content_type}")
            
            result.transformations = transformations
            
            # Calculate success metrics
            successful_transforms = sum(1 for t in transformations if t.status == "completed")
            result.success_rate = successful_transforms / max(len(transformations), 1)
            
            # Generate optimization insights
            result.optimization_results.update({
                'total_transformations': len(transformations),
                'successful_transformations': successful_transforms,
                'processing_quality': options.quality.value,
                'platform_optimizations': len(options.target_platforms)
            })
            
            result.status = "completed" if result.success_rate > 0 else "failed"
            
        except Exception as e:
            self.logger.error(f"Multi-format processing failed: {filename} - {str(e)}")
            result.status = "failed"
            result.optimization_results['error'] = str(e)
        
        finally:
            result.total_processing_time = (
                datetime.utcnow() - start_time
            ).total_seconds()
        
        return result
    
    async def batch_process_content(self, content_items: List[Tuple[bytes, str, ProcessingOptions]]) -> List[ProcessingResult]:
        """
        Process multiple content items in batch.
        
        Args:
            content_items: List of (content_data, filename, options) tuples
            
        Returns:
            List of processing results
        """
        try:
            self.logger.info(f"Starting batch processing: {len(content_items)} items")
            
            # Process items concurrently with semaphore control
            semaphore = asyncio.Semaphore(3)  # Limit concurrent processing
            
            async def process_single(item):
                async with semaphore:
                    content_data, filename, options = item
                    return await self.process_content(content_data, filename, options)
            
            tasks = [process_single(item) for item in content_items]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            final_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_result = ProcessingResult()
                    error_result.status = "failed"
                    error_result.optimization_results['error'] = str(result)
                    final_results.append(error_result)
                else:
                    final_results.append(result)
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"Batch processing failed: {str(e)}")
            raise ProcessingError(f"Batch processing failed: {str(e)}")
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get supported input formats by content type"""
        return self.supported_inputs.copy()
    
    def get_quality_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Get available quality profiles"""
        return {k.value: v for k, v in self.quality_profiles.items()}
    
    def get_platform_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get platform optimization presets"""
        return {k.value: v for k, v in self.platform_presets.items()}
    
    # Private processing methods
    
    def _detect_content_type(self, filename: str, content_data: bytes) -> Tuple[str, str]:
        """Detect content type and format from filename and data"""
        file_ext = Path(filename).suffix.lower()
        
        for content_type, extensions in self.supported_inputs.items():
            if file_ext in extensions:
                return content_type, file_ext.strip('.')
        
        # Fallback to magic number detection
        if content_data[:4] == b'fLaC':
            return 'audio', 'flac'
        elif content_data[:3] == b'ID3' or content_data[:2] == b'\xff\xfb':
            return 'audio', 'mp3'
        elif content_data[:4] == b'\x00\x00\x00\x20' or content_data[:4] == b'\x00\x00\x00\x18':
            return 'video', 'mp4'
        elif content_data[:8] == b'\x89PNG\r\n\x1a\n':
            return 'image', 'png'
        elif content_data[:2] == b'\xff\xd8':
            return 'image', 'jpeg'
        
        return 'document', 'txt'  # Default fallback
    
    async def _process_audio_content(self, content_data: bytes, filename: str,
                                   options: ProcessingOptions) -> List[TransformationResult]:
        """Process audio content with format conversion and enhancement"""
        transformations = []
        
        try:
            # Save to temporary file for processing
            with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as temp_file:
                temp_file.write(content_data)
                temp_path = temp_file.name
            
            try:
                # Load audio data
                audio_data, sample_rate = librosa.load(temp_path, sr=None)
                
                # Apply enhancements if requested
                if options.enhance_quality:
                    audio_data = await self._enhance_audio_quality(audio_data, sample_rate)
                
                # Create transformations for different formats/platforms
                target_formats = self._determine_audio_targets(options)
                
                for target_format, format_options in target_formats.items():
                    transformation = await self._transform_audio(
                        audio_data, sample_rate, target_format, format_options
                    )
                    transformations.append(transformation)
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            self.logger.error(f"Audio processing failed: {str(e)}")
            error_transform = TransformationResult()
            error_transform.status = "failed"
            error_transform.errors.append(str(e))
            transformations.append(error_transform)
        
        return transformations
    
    async def _process_video_content(self, content_data: bytes, filename: str,
                                   options: ProcessingOptions) -> List[TransformationResult]:
        """Process video content with format conversion and optimization"""
        transformations = []
        
        try:
            with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as temp_file:
                temp_file.write(content_data)
                temp_path = temp_file.name
            
            try:
                # Get video information
                probe = ffmpeg.probe(temp_path)
                video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
                
                # Create transformations for different platforms
                target_configs = self._determine_video_targets(options, video_info)
                
                for config_name, config in target_configs.items():
                    transformation = await self._transform_video(
                        temp_path, config_name, config
                    )
                    transformations.append(transformation)
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            self.logger.error(f"Video processing failed: {str(e)}")
            error_transform = TransformationResult()
            error_transform.status = "failed"
            error_transform.errors.append(str(e))
            transformations.append(error_transform)
        
        return transformations
    
    async def _process_image_content(self, content_data: bytes, filename: str,
                                   options: ProcessingOptions) -> List[TransformationResult]:
        """Process image content with format conversion and optimization"""
        transformations = []
        
        try:
            with tempfile.NamedTemporaryFile() as temp_file:
                temp_file.write(content_data)
                temp_file.flush()
                
                # Load image
                image = Image.open(temp_file.name)
                
                # Apply enhancements if requested
                if options.enhance_quality:
                    image = await self._enhance_image_quality(image)
                
                # Create transformations for different formats/platforms
                target_configs = self._determine_image_targets(options, image)
                
                for config_name, config in target_configs.items():
                    transformation = await self._transform_image(
                        image, config_name, config
                    )
                    transformations.append(transformation)
                    
        except Exception as e:
            self.logger.error(f"Image processing failed: {str(e)}")
            error_transform = TransformationResult()
            error_transform.status = "failed"
            error_transform.errors.append(str(e))
            transformations.append(error_transform)
        
        return transformations
    
    async def _process_document_content(self, content_data: bytes, filename: str,
                                      options: ProcessingOptions) -> List[TransformationResult]:
        """Process document content with format conversion"""
        transformations = []
        
        try:
            # Simple document processing - extract text and convert formats
            source_format = Path(filename).suffix.lower().strip('.')
            
            if source_format == 'txt':
                text_content = content_data.decode('utf-8', errors='ignore')
            else:
                # Placeholder for complex document processing
                text_content = f"Document content from {filename}"
            
            # Create transformations for different target formats
            target_formats = ['txt', 'html', 'json']
            
            for target_format in target_formats:
                transformation = await self._transform_document(
                    text_content, source_format, target_format
                )
                transformations.append(transformation)
                
        except Exception as e:
            self.logger.error(f"Document processing failed: {str(e)}")
            error_transform = TransformationResult()
            error_transform.status = "failed"
            error_transform.errors.append(str(e))
            transformations.append(error_transform)
        
        return transformations
    
    async def _enhance_audio_quality(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Enhance audio quality using signal processing"""
        try:
            # Noise reduction (simplified)
            audio_data = librosa.effects.preemphasis(audio_data)
            
            # Normalize volume
            audio_data = librosa.util.normalize(audio_data)
            
            return audio_data
            
        except Exception as e:
            self.logger.warning(f"Audio enhancement failed: {str(e)}")
            return audio_data
    
    async def _enhance_image_quality(self, image: Image.Image) -> Image.Image:
        """Enhance image quality using PIL filters"""
        try:
            # Sharpen image
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Enhance contrast slightly
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.1)
            
            return image
            
        except Exception as e:
            self.logger.warning(f"Image enhancement failed: {str(e)}")
            return image
    
    def _determine_audio_targets(self, options: ProcessingOptions) -> Dict[str, Dict[str, Any]]:
        """Determine target audio formats based on options"""
        targets = {}
        
        # Default high-quality version
        targets['high_quality'] = {
            'format': 'flac',
            'quality': ProcessingQuality.HIGH,
            'bitrate': None  # Lossless
        }
        
        # Web-optimized version
        if options.optimize_for_web:
            targets['web_optimized'] = {
                'format': 'mp3',
                'quality': ProcessingQuality.MEDIUM,
                'bitrate': 256
            }
        
        # Platform-specific versions
        for platform in options.target_platforms:
            if platform in self.platform_presets:
                preset = self.platform_presets[platform].get('audio', {})
                targets[f'platform_{platform.value}'] = preset
        
        return targets
    
    def _determine_video_targets(self, options: ProcessingOptions, video_info: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Determine target video configurations based on options"""
        targets = {}
        
        # Default high-quality version
        targets['high_quality'] = {
            'format': 'mp4',
            'codec': 'h264',
            'quality': ProcessingQuality.HIGH,
            'crf': 18
        }
        
        # Platform-specific versions
        for platform in options.target_platforms:
            if platform in self.platform_presets:
                preset = self.platform_presets[platform].get('video', {})
                targets[f'platform_{platform.value}'] = preset
        
        return targets
    
    def _determine_image_targets(self, options: ProcessingOptions, image: Image.Image) -> Dict[str, Dict[str, Any]]:
        """Determine target image configurations based on options"""
        targets = {}
        
        # Default high-quality version
        targets['high_quality'] = {
            'format': 'png',
            'quality': 95,
            'optimize': True
        }
        
        # Web-optimized version
        if options.optimize_for_web:
            targets['web_optimized'] = {
                'format': 'jpeg',
                'quality': 85,
                'optimize': True
            }
        
        # Platform-specific versions
        for platform in options.target_platforms:
            if platform in self.platform_presets:
                preset = self.platform_presets[platform].get('image', {})
                targets[f'platform_{platform.value}'] = preset
        
        return targets
    
    async def _transform_audio(self, audio_data: np.ndarray, sample_rate: int,
                             target_format: str, format_options: Dict[str, Any]) -> TransformationResult:
        """Transform audio to target format"""
        start_time = datetime.utcnow()
        result = TransformationResult()
        
        try:
            result.input_format = 'wav'  # Working format
            result.output_format = format_options.get('format', target_format)
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(suffix=f'.{result.output_format}', delete=False) as temp_file:
                output_path = temp_file.name
            
            # Write audio data based on format
            if result.output_format in ['wav', 'flac']:
                sf.write(output_path, audio_data, sample_rate)
            else:
                # For other formats, write as WAV first then convert
                temp_wav = output_path + '.wav'
                sf.write(temp_wav, audio_data, sample_rate)
                
                # Convert using ffmpeg (placeholder)
                # In production, would use actual ffmpeg conversion
                os.rename(temp_wav, output_path)
            
            # Read output data
            with open(output_path, 'rb') as f:
                result.output_data = f.read()
            
            result.output_path = output_path
            result.status = "completed"
            result.metadata = {
                'sample_rate': sample_rate,
                'duration': len(audio_data) / sample_rate,
                'channels': 1 if len(audio_data.shape) == 1 else audio_data.shape[1]
            }
            
        except Exception as e:
            result.status = "failed"
            result.errors.append(str(e))
        
        finally:
            result.processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return result
    
    async def _transform_video(self, input_path: str, config_name: str,
                             config: Dict[str, Any]) -> TransformationResult:
        """Transform video to target configuration"""
        start_time = datetime.utcnow()
        result = TransformationResult()
        
        try:
            result.input_format = Path(input_path).suffix.strip('.')
            result.output_format = config.get('format', 'mp4')
            
            # Create temporary output file
            with tempfile.NamedTemporaryFile(suffix=f'.{result.output_format}', delete=False) as temp_file:
                output_path = temp_file.name
            
            # Simple video processing (placeholder)
            # In production, would use ffmpeg for actual conversion
            with open(input_path, 'rb') as f:
                video_data = f.read()
            
            with open(output_path, 'wb') as f:
                f.write(video_data)  # Placeholder - no actual conversion
            
            result.output_path = output_path
            result.status = "completed"
            result.metadata = {
                'config_name': config_name,
                'target_format': result.output_format
            }
            
        except Exception as e:
            result.status = "failed"
            result.errors.append(str(e))
        
        finally:
            result.processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return result
    
    async def _transform_image(self, image: Image.Image, config_name: str,
                             config: Dict[str, Any]) -> TransformationResult:
        """Transform image to target configuration"""
        start_time = datetime.utcnow()
        result = TransformationResult()
        
        try:
            result.input_format = image.format.lower() if image.format else 'unknown'
            result.output_format = config.get('format', 'jpeg')
            
            # Apply transformations
            output_image = image.copy()
            
            # Resize if max_size specified
            if 'max_size' in config:
                max_size = config['max_size']
                if isinstance(max_size, str) and 'x' in max_size:
                    width, height = map(int, max_size.split('x'))
                    output_image.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=f'.{result.output_format}', delete=False) as temp_file:
                output_path = temp_file.name
                
                save_options = {}
                if result.output_format.lower() == 'jpeg':
                    save_options['quality'] = config.get('quality', 90)
                    save_options['optimize'] = config.get('optimize', True)
                elif result.output_format.lower() == 'png':
                    save_options['optimize'] = config.get('optimize', True)
                
                output_image.save(output_path, format=result.output_format.upper(), **save_options)
            
            # Read output data
            with open(output_path, 'rb') as f:
                result.output_data = f.read()
            
            result.output_path = output_path
            result.status = "completed"
            result.metadata = {
                'config_name': config_name,
                'original_size': f"{image.width}x{image.height}",
                'output_size': f"{output_image.width}x{output_image.height}"
            }
            
        except Exception as e:
            result.status = "failed"
            result.errors.append(str(e))
        
        finally:
            result.processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return result
    
    async def _transform_document(self, text_content: str, source_format: str,
                                target_format: str) -> TransformationResult:
        """Transform document to target format"""
        start_time = datetime.utcnow()
        result = TransformationResult()
        
        try:
            result.input_format = source_format
            result.output_format = target_format
            
            # Convert based on target format
            if target_format == 'txt':
                output_content = text_content
            elif target_format == 'html':
                output_content = f"<html><body><pre>{text_content}</pre></body></html>"
            elif target_format == 'json':
                output_content = json.dumps({
                    'content': text_content,
                    'source_format': source_format,
                    'timestamp': datetime.utcnow().isoformat()
                })
            else:
                output_content = text_content
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{target_format}', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(output_content)
                output_path = temp_file.name
            
            result.output_data = output_content.encode('utf-8')
            result.output_path = output_path
            result.status = "completed"
            result.metadata = {
                'character_count': len(text_content),
                'word_count': len(text_content.split())
            }
            
        except Exception as e:
            result.status = "failed"
            result.errors.append(str(e))
        
        finally:
            result.processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        return result


class ContentTransformer:
    """
    Advanced content transformation engine with AI-powered optimization.
    
    Provides intelligent content transformation with quality assessment,
    format optimization, and platform-specific customization capabilities.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize content transformer"""
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.processor = MultiFormatProcessor(config)
    
    async def transform_content(self, content_data: bytes, filename: str,
                              params: TransformationParams) -> TransformationResult:
        """
        Transform content according to specified parameters.
        
        Args:
            content_data: Source content data
            filename: Original filename
            params: Transformation parameters
            
        Returns:
            Transformation result
        """
        try:
            self.logger.info(f"Starting content transformation: {params.transformation_type.value}")
            
            # Create processing options from transformation params
            processing_options = params.processing_options or ProcessingOptions()
            
            # Apply transformation-specific logic
            if params.transformation_type == TransformationType.FORMAT_CONVERSION:
                return await self._transform_format_conversion(
                    content_data, filename, params, processing_options
                )
            elif params.transformation_type == TransformationType.QUALITY_ENHANCEMENT:
                return await self._transform_quality_enhancement(
                    content_data, filename, params, processing_options
                )
            elif params.transformation_type == TransformationType.COMPRESSION:
                return await self._transform_compression(
                    content_data, filename, params, processing_options
                )
            elif params.transformation_type == TransformationType.OPTIMIZATION:
                return await self._transform_optimization(
                    content_data, filename, params, processing_options
                )
            else:
                # Generic transformation
                processing_result = await self.processor.process_content(
                    content_data, filename, processing_options
                )
                
                if processing_result.transformations:
                    return processing_result.transformations[0]
                else:
                    raise TransformationError("No transformations produced")
                    
        except Exception as e:
            self.logger.error(f"Content transformation failed: {str(e)}")
            result = TransformationResult()
            result.status = "failed"
            result.errors.append(str(e))
            return result
    
    async def batch_transform_content(self, transformation_requests: List[Tuple[bytes, str, TransformationParams]]) -> List[TransformationResult]:
        """
        Transform multiple content items in batch.
        
        Args:
            transformation_requests: List of (content_data, filename, params) tuples
            
        Returns:
            List of transformation results
        """
        try:
            self.logger.info(f"Starting batch transformation: {len(transformation_requests)} items")
            
            # Process transformations concurrently
            semaphore = asyncio.Semaphore(3)
            
            async def transform_single(request):
                async with semaphore:
                    content_data, filename, params = request
                    return await self.transform_content(content_data, filename, params)
            
            tasks = [transform_single(request) for request in transformation_requests]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            final_results = []
            for result in results:
                if isinstance(result, Exception):
                    error_result = TransformationResult()
                    error_result.status = "failed"
                    error_result.errors.append(str(result))
                    final_results.append(error_result)
                else:
                    final_results.append(result)
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"Batch transformation failed: {str(e)}")
            raise TransformationError(f"Batch transformation failed: {str(e)}")
    
    def get_transformation_capabilities(self) -> Dict[str, Any]:
        """Get transformation capabilities and options"""
        return {
            'supported_types': [t.value for t in TransformationType],
            'supported_formats': self.processor.get_supported_formats(),
            'quality_profiles': self.processor.get_quality_profiles(),
            'platform_presets': self.processor.get_platform_presets()
        }
    
    # Private transformation methods
    
    async def _transform_format_conversion(self, content_data: bytes, filename: str,
                                         params: TransformationParams,
                                         options: ProcessingOptions) -> TransformationResult:
        """Perform format conversion transformation"""
        try:
            # Set specific output format
            if params.target_format:
                options.output_format = OutputFormat(params.target_format)
            
            # Process with format-specific settings
            processing_result = await self.processor.process_content(
                content_data, filename, options
            )
            
            # Return first successful transformation
            for transform in processing_result.transformations:
                if transform.status == "completed":
                    return transform
            
            # If no successful transformation, return first one with error info
            if processing_result.transformations:
                return processing_result.transformations[0]
            
            raise TransformationError("Format conversion failed")
            
        except Exception as e:
            result = TransformationResult()
            result.status = "failed"
            result.errors.append(str(e))
            return result
    
    async def _transform_quality_enhancement(self, content_data: bytes, filename: str,
                                           params: TransformationParams,
                                           options: ProcessingOptions) -> TransformationResult:
        """Perform quality enhancement transformation"""
        try:
            # Enable quality enhancement
            options.enhance_quality = True
            options.quality = ProcessingQuality.ULTRA
            
            processing_result = await self.processor.process_content(
                content_data, filename, options
            )
            
            if processing_result.transformations:
                return processing_result.transformations[0]
            
            raise TransformationError("Quality enhancement failed")
            
        except Exception as e:
            result = TransformationResult()
            result.status = "failed"
            result.errors.append(str(e))
            return result
    
    async def _transform_compression(self, content_data: bytes, filename: str,
                                   params: TransformationParams,
                                   options: ProcessingOptions) -> TransformationResult:
        """Perform compression transformation"""
        try:
            # Set compression-focused options
            options.quality = ProcessingQuality.MEDIUM
            options.compression_level = 8
            options.optimize_for_web = True
            
            processing_result = await self.processor.process_content(
                content_data, filename, options
            )
            
            if processing_result.transformations:
                return processing_result.transformations[0]
            
            raise TransformationError("Compression failed")
            
        except Exception as e:
            result = TransformationResult()
            result.status = "failed"
            result.errors.append(str(e))
            return result
    
    async def _transform_optimization(self, content_data: bytes, filename: str,
                                    params: TransformationParams,
                                    options: ProcessingOptions) -> TransformationResult:
        """Perform optimization transformation"""
        try:
            # Set optimization-focused options
            options.enhance_quality = True
            options.optimize_for_web = True
            options.quality = ProcessingQuality.HIGH
            
            processing_result = await self.processor.process_content(
                content_data, filename, options
            )
            
            if processing_result.transformations:
                return processing_result.transformations[0]
            
            raise TransformationError("Optimization failed")
            
        except Exception as e:
            result = TransformationResult()
            result.status = "failed"
            result.errors.append(str(e))
            return result


class IntelligentContentRouter:
    """
    AI-powered content routing engine for optimal platform distribution.
    
    Provides intelligent routing decisions based on content analysis, platform
    requirements, audience targeting, and performance optimization strategies.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize intelligent content router"""
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Initialize routing rules and strategies
        self._routing_rules: Dict[str, RoutingRule] = {}
        self._initialize_default_rules()
        
        # Platform performance data (would be loaded from analytics in production)
        self.platform_performance = {
            Platform.YOUTUBE: {'engagement_rate': 0.65, 'reach_multiplier': 2.5},
            Platform.INSTAGRAM: {'engagement_rate': 0.85, 'reach_multiplier': 1.8},
            Platform.TIKTOK: {'engagement_rate': 0.92, 'reach_multiplier': 3.2},
            Platform.FACEBOOK: {'engagement_rate': 0.45, 'reach_multiplier': 2.0},
            Platform.TWITTER: {'engagement_rate': 0.38, 'reach_multiplier': 1.5},
            Platform.LINKEDIN: {'engagement_rate': 0.55, 'reach_multiplier': 1.2}
        }
    
    def _initialize_default_rules(self):
        """Initialize default routing rules"""
        try:
            # Video content rules
            video_rule = RoutingRule(
                platform=Platform.YOUTUBE,
                content_category=ContentCategory.VIDEO_CONTENT,
                required_format=OutputFormat.MP4,
                quality_requirements={'min_resolution': '720p', 'max_bitrate': '5000k'},
                optimization_settings={'target_duration': '5-15min'}
            )
            self._routing_rules[f"{Platform.YOUTUBE.value}_video"] = video_rule
            
            # Audio content rules
            audio_rule = RoutingRule(
                platform=Platform.PODCAST,
                content_category=ContentCategory.MUSIC,
                required_format=OutputFormat.MP3,
                quality_requirements={'min_bitrate': '128k', 'sample_rate': '44100'},
                optimization_settings={'normalize_volume': True}
            )
            self._routing_rules[f"{Platform.PODCAST.value}_audio"] = audio_rule
            
            # Image content rules
            image_rule = RoutingRule(
                platform=Platform.INSTAGRAM,
                content_category=ContentCategory.CREATIVE,
                required_format=OutputFormat.JPEG,
                quality_requirements={'max_size': '1080x1080', 'quality': 90},
                optimization_settings={'square_aspect': True}
            )
            self._routing_rules[f"{Platform.INSTAGRAM.value}_image"] = image_rule
            
        except Exception as e:
            self.logger.error(f"Default rules initialization failed: {str(e)}")
    
    async def create_routing_plan(self, content_metadata: Dict[str, Any],
                                strategy: RoutingStrategy,
                                target_platforms: List[Platform] = None) -> RoutingPlan:
        """
        Create intelligent routing plan for content distribution.
        
        Args:
            content_metadata: Content analysis metadata
            strategy: Routing strategy to optimize for
            target_platforms: Optional list of target platforms
            
        Returns:
            Complete routing plan with decisions
        """
        try:
            self.logger.info(f"Creating routing plan with strategy: {strategy.value}")
            
            plan = RoutingPlan(strategy=strategy)
            
            # Determine target platforms if not specified
            if target_platforms is None:
                target_platforms = self._recommend_platforms(content_metadata, strategy)
            
            # Create routing decisions for each platform
            for platform in target_platforms:
                decision = await self._create_routing_decision(
                    content_metadata, platform, strategy
                )
                plan.decisions.append(decision)
            
            # Calculate plan metrics
            plan.total_platforms = len(plan.decisions)
            plan.estimated_reach = sum(
                d.estimated_performance.get('reach', 0) for d in plan.decisions
            )
            plan.cost_estimate = sum(
                d.estimated_performance.get('cost', 0) for d in plan.decisions
            )
            
            # Set processing requirements
            plan.processing_requirements = self._calculate_processing_requirements(plan.decisions)
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Routing plan creation failed: {str(e)}")
            raise RoutingError(f"Routing plan creation failed: {str(e)}")
    
    async def execute_routing_plan(self, plan: RoutingPlan,
                                 content_data: bytes, filename: str) -> RoutingResult:
        """
        Execute routing plan with content processing and distribution.
        
        Args:
            plan: Routing plan to execute
            content_data: Content data to route
            filename: Original filename
            
        Returns:
            Routing execution result
        """
        try:
            self.logger.info(f"Executing routing plan: {plan.plan_id}")
            
            result = RoutingResult(plan=plan)
            result.executed_decisions = []
            
            # Process content for each routing decision
            for decision in plan.decisions:
                try:
                    # Execute individual routing decision
                    execution_result = await self._execute_routing_decision(
                        decision, content_data, filename
                    )
                    
                    result.executed_decisions.append(decision)
                    result.delivery_results[decision.platform.value] = execution_result
                    
                except Exception as e:
                    self.logger.warning(f"Routing decision failed for {decision.platform.value}: {str(e)}")
                    result.delivery_results[decision.platform.value] = {
                        'status': 'failed',
                        'error': str(e)
                    }
            
            # Calculate success metrics
            successful_deliveries = sum(
                1 for r in result.delivery_results.values() 
                if r.get('status') == 'completed'
            )
            result.success_rate = successful_deliveries / max(len(plan.decisions), 1)
            
            # Performance metrics
            result.performance_metrics = {
                'total_decisions': len(plan.decisions),
                'successful_deliveries': successful_deliveries,
                'failed_deliveries': len(plan.decisions) - successful_deliveries,
                'average_processing_time': sum(
                    r.get('processing_time', 0) for r in result.delivery_results.values()
                ) / max(len(result.delivery_results), 1)
            }
            
            result.completion_time = datetime.utcnow()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Routing plan execution failed: {str(e)}")
            raise RoutingError(f"Routing plan execution failed: {str(e)}")
    
    async def optimize_routing_strategy(self, content_metadata: Dict[str, Any],
                                      performance_data: Dict[str, Any] = None) -> RoutingStrategy:
        """
        Optimize routing strategy based on content and performance data.
        
        Args:
            content_metadata: Content analysis metadata
            performance_data: Historical performance data
            
        Returns:
            Optimized routing strategy
        """
        try:
            # Analyze content characteristics
            content_type = content_metadata.get('content_type', 'unknown')
            quality_score = content_metadata.get('quality_score', 0.5)
            
            # Simple strategy optimization logic
            if quality_score > 0.8:
                return RoutingStrategy.OPTIMAL_QUALITY
            elif content_type in ['music', 'audio']:
                return RoutingStrategy.ENGAGEMENT_FOCUSED
            elif 'business' in content_metadata.get('tags', []):
                return RoutingStrategy.REVENUE_OPTIMIZED
            else:
                return RoutingStrategy.MAXIMUM_REACH
                
        except Exception as e:
            self.logger.warning(f"Strategy optimization failed: {str(e)}")
            return RoutingStrategy.MAXIMUM_REACH
    
    def add_routing_rule(self, rule: RoutingRule):
        """Add custom routing rule"""
        rule_key = f"{rule.platform.value}_{rule.content_category.value}"
        self._routing_rules[rule_key] = rule
        self.logger.info(f"Added routing rule: {rule_key}")
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing system statistics"""
        return {
            'total_rules': len(self._routing_rules),
            'supported_platforms': [p.value for p in Platform],
            'supported_strategies': [s.value for s in RoutingStrategy],
            'platform_performance': {k.value: v for k, v in self.platform_performance.items()}
        }
    
    # Private routing methods
    
    def _recommend_platforms(self, content_metadata: Dict[str, Any],
                           strategy: RoutingStrategy) -> List[Platform]:
        """Recommend platforms based on content and strategy"""
        try:
            content_type = content_metadata.get('content_type', 'unknown')
            
            # Platform recommendations based on content type
            if content_type == 'video':
                platforms = [Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM]
            elif content_type == 'audio':
                platforms = [Platform.PODCAST, Platform.YOUTUBE]
            elif content_type == 'image':
                platforms = [Platform.INSTAGRAM, Platform.FACEBOOK, Platform.TWITTER]
            else:
                platforms = [Platform.BLOG, Platform.LINKEDIN, Platform.WEBSITE]
            
            # Filter based on strategy
            if strategy == RoutingStrategy.MAXIMUM_REACH:
                return platforms[:3]  # Top 3 platforms
            elif strategy == RoutingStrategy.ENGAGEMENT_FOCUSED:
                # Sort by engagement rate
                return sorted(platforms, 
                            key=lambda p: self.platform_performance.get(p, {}).get('engagement_rate', 0),
                            reverse=True)[:2]
            else:
                return platforms[:2]  # Default to top 2
                
        except Exception as e:
            self.logger.warning(f"Platform recommendation failed: {str(e)}")
            return [Platform.UNIVERSAL]
    
    async def _create_routing_decision(self, content_metadata: Dict[str, Any],
                                     platform: Platform,
                                     strategy: RoutingStrategy) -> RoutingDecision:
        """Create routing decision for specific platform"""
        try:
            decision = RoutingDecision(platform=platform)
            
            # Determine optimal format for platform
            content_type = content_metadata.get('content_type', 'unknown')
            
            if content_type == 'video':
                decision.recommended_format = OutputFormat.MP4
                decision.quality_level = ProcessingQuality.HIGH
            elif content_type == 'audio':
                decision.recommended_format = OutputFormat.MP3
                decision.quality_level = ProcessingQuality.MEDIUM
            elif content_type == 'image':
                decision.recommended_format = OutputFormat.JPEG
                decision.quality_level = ProcessingQuality.HIGH
            else:
                decision.recommended_format = OutputFormat.HTML
                decision.quality_level = ProcessingQuality.MEDIUM
            
            # Calculate optimization score based on platform performance
            platform_perf = self.platform_performance.get(platform, {})
            engagement_rate = platform_perf.get('engagement_rate', 0.5)
            reach_multiplier = platform_perf.get('reach_multiplier', 1.0)
            
            decision.optimization_score = (engagement_rate * 0.6 + 
                                         (reach_multiplier / 3.0) * 0.4) * 100
            decision.confidence = min(decision.optimization_score / 100, 1.0)
            
            # Add reasoning
            decision.reasons = [
                f"Platform engagement rate: {engagement_rate:.2f}",
                f"Reach multiplier: {reach_multiplier:.1f}x",
                f"Recommended format: {decision.recommended_format.value}"
            ]
            
            # Estimate performance
            base_reach = content_metadata.get('estimated_audience', 1000)
            decision.estimated_performance = {
                'reach': int(base_reach * reach_multiplier),
                'engagement': engagement_rate,
                'cost': base_reach * 0.001,  # $0.001 per impression
                'processing_time': 30  # seconds
            }
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Routing decision creation failed: {str(e)}")
            decision = RoutingDecision(platform=platform)
            decision.confidence = 0.0
            decision.reasons = [f"Error: {str(e)}"]
            return decision
    
    async def _execute_routing_decision(self, decision: RoutingDecision,
                                      content_data: bytes, filename: str) -> Dict[str, Any]:
        """Execute individual routing decision"""
        start_time = datetime.utcnow()
        
        try:
            # Simulate content processing and delivery
            # In production, this would integrate with actual platform APIs
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'status': 'completed',
                'platform': decision.platform.value,
                'format': decision.recommended_format.value,
                'processing_time': processing_time,
                'delivery_id': str(uuid.uuid4()),
                'estimated_reach': decision.estimated_performance.get('reach', 0)
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'platform': decision.platform.value,
                'error': str(e),
                'processing_time': (datetime.utcnow() - start_time).total_seconds()
            }
    
    def _calculate_processing_requirements(self, decisions: List[RoutingDecision]) -> Dict[str, Any]:
        """Calculate processing requirements for routing decisions"""
        try:
            required_formats = set(d.recommended_format for d in decisions)
            quality_levels = set(d.quality_level for d in decisions)
            
            return {
                'required_formats': [f.value for f in required_formats],
                'quality_levels': [q.value for q in quality_levels],
                'total_transformations': len(decisions),
                'estimated_total_time': sum(
                    d.estimated_performance.get('processing_time', 30) for d in decisions
                ),
                'parallel_processing': len(decisions) > 1
            }
            
        except Exception as e:
            self.logger.warning(f"Processing requirements calculation failed: {str(e)}")
            return {
                'error': str(e),
                'total_transformations': len(decisions)
            }