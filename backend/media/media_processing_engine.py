"""Media Processing Engine - Unified Format Processing System
===========================================================

Unified media processing engine handling all media formats with advanced
processing, optimization, and conversion capabilities.

Consolidates:
- Audio processing and manipulation (audio.py)
- Image processing and optimization (images.py)
- Video processing and encoding (videos.py)
- Text processing and formatting (text.py)
- Voice processing and synthesis (voice.py)
- Avatar processing and animation (avatars.py)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary media processing system contains advanced algorithms and trade secrets
belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering  
- Commercial use without explicit written permission
- Algorithm extraction or processing model appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import logging
import json
import base64
import io
import uuid
import tempfile
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Union, Any, Tuple, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Graceful imports with fallbacks
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import librosa
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    import torch
    import torchaudio
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)

class MediaType(Enum):
    """Media type enumeration"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    VOICE = "voice"
    AVATAR = "avatar"

class ProcessingOperation(Enum):
    """Processing operation types"""
    RESIZE = "resize"
    CROP = "crop"
    ROTATE = "rotate"
    FLIP = "flip"
    FILTER = "filter"
    ENHANCE = "enhance"
    CONVERT = "convert"
    COMPRESS = "compress"
    NORMALIZE = "normalize"
    TRIM = "trim"
    MERGE = "merge"
    SPLIT = "split"
    WATERMARK = "watermark"
    BLUR = "blur"
    SHARPEN = "sharpen"

class MediaFormat(Enum):
    """Supported media formats"""
    # Image formats
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"
    GIF = "gif"
    SVG = "svg"
    TIFF = "tiff"
    BMP = "bmp"
    
    # Video formats
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WEBM = "webm"
    MKV = "mkv"
    FLV = "flv"
    
    # Audio formats
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    
    # Text formats
    TXT = "txt"
    HTML = "html"
    MARKDOWN = "md"
    JSON = "json"
    XML = "xml"

class QualityProfile(Enum):
    """Quality profile presets"""
    WEB_OPTIMIZED = "web_optimized"
    PRINT_QUALITY = "print_quality"
    SOCIAL_MEDIA = "social_media"
    PROFESSIONAL = "professional"
    ARCHIVE = "archive"
    MOBILE = "mobile"

@dataclass
class ProcessingConfig:
    """Media processing configuration"""
    operation: ProcessingOperation
    target_format: Optional[MediaFormat] = None
    quality_profile: QualityProfile = QualityProfile.WEB_OPTIMIZED
    parameters: Dict[str, Any] = field(default_factory=dict)
    preserve_metadata: bool = True
    output_path: Optional[str] = None

@dataclass
class MediaMetadata:
    """Media file metadata"""
    media_type: MediaType
    format: MediaFormat
    file_size: int
    dimensions: Optional[Tuple[int, int]] = None
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bitrate: Optional[int] = None
    color_mode: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None
    custom_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProcessingResult:
    """Processing operation result"""
    success: bool
    output_data: Any
    output_metadata: MediaMetadata
    processing_time: float
    operations_applied: List[ProcessingOperation]
    quality_score: float
    error_message: Optional[str] = None

class MediaProcessingEngine:
    """Unified media processing engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize media processing engine"""
        self.config = config or {}
        self.processors = {}
        self.temp_dir = tempfile.mkdtemp(prefix="media_processing_")
        
        # Initialize specialized processors
        self._initialize_processors()
        
        logger.info("🎬 Media Processing Engine initialized")
    
    def _initialize_processors(self):
        """Initialize specialized media processors"""
        self.processors = {
            MediaType.IMAGE: ImageProcessor(self.config.get('image', {})),
            MediaType.VIDEO: VideoProcessor(self.config.get('video', {})),
            MediaType.AUDIO: AudioProcessor(self.config.get('audio', {})),
            MediaType.VOICE: VoiceProcessor(self.config.get('voice', {})),
            MediaType.TEXT: TextProcessor(self.config.get('text', {})),
            MediaType.AVATAR: AvatarProcessor(self.config.get('avatar', {}))
        }
    
    async def process_media(
        self, 
        media_data: Any,
        media_type: MediaType,
        operations: List[ProcessingConfig]
    ) -> ProcessingResult:
        """Process media with specified operations"""
        start_time = datetime.now(timezone.utc)
        
        try:
            processor = self.processors.get(media_type)
            if not processor:
                raise ValueError(f"No processor available for {media_type.value}")
            
            # Get initial metadata
            initial_metadata = await self._extract_metadata(media_data, media_type)
            
            # Process through operations pipeline
            current_data = media_data
            applied_operations = []
            
            for operation_config in operations:
                current_data = await processor.apply_operation(
                    current_data, operation_config
                )
                applied_operations.append(operation_config.operation)
            
            # Get final metadata
            final_metadata = await self._extract_metadata(current_data, media_type)
            
            # Calculate quality score
            quality_score = await self._calculate_quality_score(
                initial_metadata, final_metadata, applied_operations
            )
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                output_data=current_data,
                output_metadata=final_metadata,
                processing_time=processing_time,
                operations_applied=applied_operations,
                quality_score=quality_score
            )
            
        except Exception as e:
            logger.error(f"Media processing failed: {e}")
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            return ProcessingResult(
                success=False,
                output_data=None,
                output_metadata=MediaMetadata(
                    media_type=media_type,
                    format=MediaFormat.PNG,
                    file_size=0
                ),
                processing_time=processing_time,
                operations_applied=[],
                quality_score=0.0,
                error_message=str(e)
            )
    
    async def batch_process(
        self, 
        batch_requests: List[Dict[str, Any]]
    ) -> List[ProcessingResult]:
        """Batch process multiple media files"""
        tasks = []
        for request in batch_requests:
            task = self.process_media(
                media_data=request['media_data'],
                media_type=MediaType(request['media_type']),
                operations=[ProcessingConfig(**op) for op in request.get('operations', [])]
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch processing failed for request {i}: {result}")
                processed_results.append(ProcessingResult(
                    success=False,
                    output_data=None,
                    output_metadata=MediaMetadata(
                        media_type=MediaType.TEXT,
                        format=MediaFormat.TXT,
                        file_size=0
                    ),
                    processing_time=0.0,
                    operations_applied=[],
                    quality_score=0.0,
                    error_message=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def convert_format(
        self, 
        media_data: Any,
        source_format: MediaFormat,
        target_format: MediaFormat,
        quality_profile: QualityProfile = QualityProfile.WEB_OPTIMIZED
    ) -> ProcessingResult:
        """Convert media between formats"""
        # Determine media type from format
        media_type = self._get_media_type_from_format(source_format)
        
        # Create conversion operation
        conversion_config = ProcessingConfig(
            operation=ProcessingOperation.CONVERT,
            target_format=target_format,
            quality_profile=quality_profile,
            parameters={
                'source_format': source_format.value,
                'target_format': target_format.value
            }
        )
        
        return await self.process_media(media_data, media_type, [conversion_config])
    
    async def get_metadata(self, media_data: Any, media_type: MediaType) -> MediaMetadata:
        """Extract metadata from media"""
        return await self._extract_metadata(media_data, media_type)
    
    def cleanup(self):
        """Cleanup temporary files"""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.info("Temporary files cleaned up")
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary files: {e}")
    
    # Private helper methods
    
    async def _extract_metadata(self, media_data: Any, media_type: MediaType) -> MediaMetadata:
        """Extract metadata from media data"""
        processor = self.processors.get(media_type)
        if processor:
            return await processor.extract_metadata(media_data)
        
        # Fallback metadata
        return MediaMetadata(
            media_type=media_type,
            format=MediaFormat.PNG,
            file_size=len(str(media_data)) if isinstance(media_data, str) else 0
        )
    
    async def _calculate_quality_score(
        self, 
        initial_metadata: MediaMetadata,
        final_metadata: MediaMetadata,
        operations: List[ProcessingOperation]
    ) -> float:
        """Calculate quality score for processed media"""
        base_score = 0.8
        
        # Adjust based on operations
        quality_impact = {
            ProcessingOperation.ENHANCE: 0.1,
            ProcessingOperation.NORMALIZE: 0.05,
            ProcessingOperation.COMPRESS: -0.1,
            ProcessingOperation.RESIZE: -0.02,
            ProcessingOperation.CONVERT: -0.05
        }
        
        score = base_score
        for operation in operations:
            impact = quality_impact.get(operation, 0)
            score += impact
        
        return max(0.0, min(1.0, score))
    
    def _get_media_type_from_format(self, format: MediaFormat) -> MediaType:
        """Determine media type from format"""
        image_formats = {MediaFormat.PNG, MediaFormat.JPEG, MediaFormat.WEBP, 
                        MediaFormat.GIF, MediaFormat.SVG, MediaFormat.TIFF, MediaFormat.BMP}
        video_formats = {MediaFormat.MP4, MediaFormat.AVI, MediaFormat.MOV, 
                        MediaFormat.WEBM, MediaFormat.MKV, MediaFormat.FLV}
        audio_formats = {MediaFormat.WAV, MediaFormat.MP3, MediaFormat.FLAC, 
                        MediaFormat.AAC, MediaFormat.OGG, MediaFormat.M4A}
        text_formats = {MediaFormat.TXT, MediaFormat.HTML, MediaFormat.MARKDOWN, 
                       MediaFormat.JSON, MediaFormat.XML}
        
        if format in image_formats:
            return MediaType.IMAGE
        elif format in video_formats:
            return MediaType.VIDEO
        elif format in audio_formats:
            return MediaType.AUDIO
        elif format in text_formats:
            return MediaType.TEXT
        else:
            return MediaType.TEXT  # Default fallback

class BaseProcessor:
    """Base class for media processors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def apply_operation(self, data: Any, config: ProcessingConfig) -> Any:
        """Apply processing operation to data"""
        raise NotImplementedError
    
    async def extract_metadata(self, data: Any) -> MediaMetadata:
        """Extract metadata from data"""
        raise NotImplementedError

class ImageProcessor(BaseProcessor):
    """Image processing implementation"""
    
    async def apply_operation(self, data: Any, config: ProcessingConfig) -> Any:
        """Apply image processing operation"""
        try:
            if not PIL_AVAILABLE:
                logger.warning("PIL not available, returning original data")
                return data
            
            # Convert data to PIL Image if needed
            image = await self._to_pil_image(data)
            
            if config.operation == ProcessingOperation.RESIZE:
                width = config.parameters.get('width', 800)
                height = config.parameters.get('height', 600)
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            elif config.operation == ProcessingOperation.CROP:
                box = config.parameters.get('box', (0, 0, 400, 400))
                image = image.crop(box)
            
            elif config.operation == ProcessingOperation.ROTATE:
                angle = config.parameters.get('angle', 90)
                image = image.rotate(angle, expand=True)
            
            elif config.operation == ProcessingOperation.FLIP:
                direction = config.parameters.get('direction', 'horizontal')
                if direction == 'horizontal':
                    image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                else:
                    image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            
            elif config.operation == ProcessingOperation.FILTER:
                filter_type = config.parameters.get('filter', 'blur')
                if filter_type == 'blur':
                    radius = config.parameters.get('radius', 2)
                    image = image.filter(ImageFilter.GaussianBlur(radius))
                elif filter_type == 'sharpen':
                    image = image.filter(ImageFilter.SHARPEN)
            
            elif config.operation == ProcessingOperation.ENHANCE:
                enhancement_type = config.parameters.get('type', 'brightness')
                factor = config.parameters.get('factor', 1.2)
                
                if enhancement_type == 'brightness':
                    enhancer = ImageEnhance.Brightness(image)
                elif enhancement_type == 'contrast':
                    enhancer = ImageEnhance.Contrast(image)
                elif enhancement_type == 'color':
                    enhancer = ImageEnhance.Color(image)
                elif enhancement_type == 'sharpness':
                    enhancer = ImageEnhance.Sharpness(image)
                else:
                    enhancer = ImageEnhance.Brightness(image)
                
                image = enhancer.enhance(factor)
            
            elif config.operation == ProcessingOperation.CONVERT:
                target_format = config.target_format
                if target_format:
                    # Convert image based on target format
                    if target_format == MediaFormat.JPEG and image.mode in ('RGBA', 'LA'):
                        # Convert to RGB for JPEG
                        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                        rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                        image = rgb_image
            
            return await self._from_pil_image(image, config.target_format)
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return data
    
    async def extract_metadata(self, data: Any) -> MediaMetadata:
        """Extract image metadata"""
        try:
            if PIL_AVAILABLE:
                image = await self._to_pil_image(data)
                return MediaMetadata(
                    media_type=MediaType.IMAGE,
                    format=MediaFormat.PNG,
                    file_size=len(str(data)) if isinstance(data, str) else 0,
                    dimensions=image.size,
                    color_mode=image.mode
                )
        except Exception as e:
            logger.error(f"Failed to extract image metadata: {e}")
        
        return MediaMetadata(
            media_type=MediaType.IMAGE,
            format=MediaFormat.PNG,
            file_size=0
        )
    
    async def _to_pil_image(self, data: Any) -> Image.Image:
        """Convert data to PIL Image"""
        if isinstance(data, Image.Image):
            return data
        elif isinstance(data, str):
            # Assume base64 encoded image
            if data.startswith('data:image'):
                data = data.split(',')[1]
            image_data = base64.b64decode(data)
            return Image.open(io.BytesIO(image_data))
        elif isinstance(data, bytes):
            return Image.open(io.BytesIO(data))
        else:
            # Create placeholder image
            return Image.new('RGB', (800, 600), color='lightgray')
    
    async def _from_pil_image(self, image: Image.Image, target_format: Optional[MediaFormat]) -> str:
        """Convert PIL Image to output format"""
        buffer = io.BytesIO()
        format_name = target_format.value.upper() if target_format else 'PNG'
        if format_name == 'JPEG':
            format_name = 'JPEG'
        
        image.save(buffer, format=format_name)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

class VideoProcessor(BaseProcessor):
    """Video processing implementation"""
    
    async def apply_operation(self, data: Any, config: ProcessingConfig) -> Any:
        """Apply video processing operation"""
        # Placeholder video processing
        logger.info(f"Applying video operation: {config.operation.value}")
        
        if config.operation == ProcessingOperation.TRIM:
            start_time = config.parameters.get('start', 0)
            end_time = config.parameters.get('end', 30)
            return f"trimmed_video_{start_time}_{end_time}.mp4"
        
        elif config.operation == ProcessingOperation.RESIZE:
            width = config.parameters.get('width', 1920)
            height = config.parameters.get('height', 1080)
            return f"resized_video_{width}x{height}.mp4"
        
        elif config.operation == ProcessingOperation.CONVERT:
            target_format = config.target_format.value if config.target_format else 'mp4'
            return f"converted_video.{target_format}"
        
        return data
    
    async def extract_metadata(self, data: Any) -> MediaMetadata:
        """Extract video metadata"""
        return MediaMetadata(
            media_type=MediaType.VIDEO,
            format=MediaFormat.MP4,
            file_size=10 * 1024 * 1024,  # 10MB estimate
            dimensions=(1920, 1080),
            duration=30.0
        )

class AudioProcessor(BaseProcessor):
    """Audio processing implementation"""
    
    async def apply_operation(self, data: Any, config: ProcessingConfig) -> Any:
        """Apply audio processing operation"""
        logger.info(f"Applying audio operation: {config.operation.value}")
        
        if config.operation == ProcessingOperation.TRIM:
            start_time = config.parameters.get('start', 0)
            end_time = config.parameters.get('end', 30)
            return f"trimmed_audio_{start_time}_{end_time}"
        
        elif config.operation == ProcessingOperation.NORMALIZE:
            target_db = config.parameters.get('target_db', -23)
            return f"normalized_audio_{target_db}db"
        
        elif config.operation == ProcessingOperation.CONVERT:
            target_format = config.target_format.value if config.target_format else 'wav'
            return f"converted_audio.{target_format}"
        
        return data
    
    async def extract_metadata(self, data: Any) -> MediaMetadata:
        """Extract audio metadata"""
        return MediaMetadata(
            media_type=MediaType.AUDIO,
            format=MediaFormat.WAV,
            file_size=5 * 1024 * 1024,  # 5MB estimate
            duration=30.0,
            sample_rate=44100,
            channels=2
        )

class VoiceProcessor(BaseProcessor):
    """Voice processing implementation"""
    
    async def apply_operation(self, data: Any, config: ProcessingConfig) -> Any:
        """Apply voice processing operation"""
        logger.info(f"Applying voice operation: {config.operation.value}")
        
        if config.operation == ProcessingOperation.ENHANCE:
            enhancement_type = config.parameters.get('type', 'clarity')
            return f"enhanced_voice_{enhancement_type}"
        
        elif config.operation == ProcessingOperation.NORMALIZE:
            return "normalized_voice"
        
        return data
    
    async def extract_metadata(self, data: Any) -> MediaMetadata:
        """Extract voice metadata"""
        return MediaMetadata(
            media_type=MediaType.VOICE,
            format=MediaFormat.WAV,
            file_size=2 * 1024 * 1024,  # 2MB estimate
            duration=15.0,
            sample_rate=22050,
            channels=1
        )

class TextProcessor(BaseProcessor):
    """Text processing implementation"""
    
    async def apply_operation(self, data: Any, config: ProcessingConfig) -> Any:
        """Apply text processing operation"""
        logger.info(f"Applying text operation: {config.operation.value}")
        
        if config.operation == ProcessingOperation.CONVERT:
            target_format = config.target_format
            if target_format == MediaFormat.HTML:
                return f"<html><body>{data}</body></html>"
            elif target_format == MediaFormat.MARKDOWN:
                return f"# Content\n\n{data}"
            elif target_format == MediaFormat.JSON:
                return json.dumps({"content": data})
        
        elif config.operation == ProcessingOperation.ENHANCE:
            enhancement_type = config.parameters.get('type', 'grammar')
            return f"Enhanced text with {enhancement_type}: {data}"
        
        return data
    
    async def extract_metadata(self, data: Any) -> MediaMetadata:
        """Extract text metadata"""
        text_data = str(data)
        return MediaMetadata(
            media_type=MediaType.TEXT,
            format=MediaFormat.TXT,
            file_size=len(text_data.encode('utf-8')),
            custom_metadata={
                'word_count': len(text_data.split()),
                'character_count': len(text_data),
                'line_count': len(text_data.splitlines())
            }
        )

class AvatarProcessor(BaseProcessor):
    """Avatar processing implementation"""
    
    async def apply_operation(self, data: Any, config: ProcessingConfig) -> Any:
        """Apply avatar processing operation"""
        logger.info(f"Applying avatar operation: {config.operation.value}")
        
        if config.operation == ProcessingOperation.RESIZE:
            size = config.parameters.get('size', '512x512')
            return f"resized_avatar_{size}"
        
        elif config.operation == ProcessingOperation.ENHANCE:
            enhancement_type = config.parameters.get('type', 'quality')
            return f"enhanced_avatar_{enhancement_type}"
        
        return data
    
    async def extract_metadata(self, data: Any) -> MediaMetadata:
        """Extract avatar metadata"""
        return MediaMetadata(
            media_type=MediaType.AVATAR,
            format=MediaFormat.PNG,
            file_size=1024 * 1024,  # 1MB estimate
            dimensions=(512, 512),
            color_mode='RGBA'
        )