"""Data Transformer - Main transformation interface for IA Influencer Agent Platform
================================================================================

Professional data transformation coordinator handling multi-format content processing,
encoding, and format conversion workflows for creators.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""
import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from .audio_transformer import AudioTransformer
from .video_transformer import VideoTransformer  
from .image_transformer import ImageTransformer
from .text_transformer import TextTransformer
from .metadata_transformer import MetadataTransformer
from .format_converter import FormatConverter
from .encoding_manager import EncodingManager
from .batch_processor import BatchProcessor
from .realtime_converter import RealtimeConverter
from .quality_optimizer import QualityOptimizer

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Supported content types for transformation."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    DOCUMENT = "document"
    METADATA = "metadata"


class TransformationMode(Enum):
    """Transformation processing modes."""
    SINGLE = "single"
    BATCH = "batch"
    REALTIME = "realtime"
    STREAMING = "streaming"


class QualityLevel(Enum):
    """Quality levels for transformation."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    LOSSLESS = "lossless"
    CUSTOM = "custom"


@dataclass
class TransformationRequest:
    """Transformation request configuration."""
    input_path: str
    output_path: Optional[str] = None
    content_type: ContentType = ContentType.AUDIO
    target_format: Optional[str] = None
    quality: QualityLevel = QualityLevel.HIGH
    mode: TransformationMode = TransformationMode.SINGLE
    metadata: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
    preserve_metadata: bool = True
    enhance_quality: bool = False
    custom_pipeline: Optional[List[str]] = None


@dataclass
class TransformationResult:
    """Transformation result with metrics."""
    success: bool
    output_path: Optional[str] = None
    processing_time: float = 0.0
    input_size: int = 0
    output_size: int = 0
    compression_ratio: float = 0.0
    quality_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    warnings: Optional[List[str]] = None
    metrics: Optional[Dict[str, Any]] = None


class DataTransformer:
    """
    Main data transformation coordinator for the IA Influencer Agent Platform.
    
    Handles multi-format content transformation, encoding optimization,
    and quality enhancement for creator content workflows.
    """
    
    def __init__(
        self,
        max_workers: int = 4,
        enable_gpu: bool = True,
        cache_enabled: bool = True,
        temp_dir: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize data transformer with configuration.
        
        Args:
            max_workers: Maximum concurrent workers
            enable_gpu: Enable GPU acceleration if available
            cache_enabled: Enable result caching
            temp_dir: Temporary directory for processing
            config: Additional configuration options
        """
        self.max_workers = max_workers
        self.enable_gpu = enable_gpu
        self.cache_enabled = cache_enabled
        self.temp_dir = Path(temp_dir) if temp_dir else Path("/tmp/transformers")
        self.config = config or {}
        
        # Create temp directory
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize specialized transformers
        self._init_transformers()
        
        # Execution pools
        self.thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=max_workers)
        
        # Caching
        self._cache = {} if cache_enabled else None
        
        # Metrics
        self.metrics = {
            "total_transformations": 0,
            "successful_transformations": 0,
            "failed_transformations": 0,
            "total_processing_time": 0.0,
            "average_processing_time": 0.0,
            "total_input_size": 0,
            "total_output_size": 0,
            "compression_efficiency": 0.0
        }
        
        logger.info(f"DataTransformer initialized with {max_workers} workers")
    
    def _init_transformers(self):
        """Initialize specialized transformer instances."""
        transformer_config = self.config.get("transformers", {})
        
        self.audio_transformer = AudioTransformer(
            enable_gpu=self.enable_gpu,
            config=transformer_config.get("audio", {})
        )
        
        self.video_transformer = VideoTransformer(
            enable_gpu=self.enable_gpu,
            config=transformer_config.get("video", {})
        )
        
        self.image_transformer = ImageTransformer(
            enable_gpu=self.enable_gpu,
            config=transformer_config.get("image", {})
        )
        
        self.text_transformer = TextTransformer(
            config=transformer_config.get("text", {})
        )
        
        self.metadata_transformer = MetadataTransformer(
            config=transformer_config.get("metadata", {})
        )
        
        self.format_converter = FormatConverter(
            config=transformer_config.get("format", {})
        )
        
        self.encoding_manager = EncodingManager(
            enable_gpu=self.enable_gpu,
            config=transformer_config.get("encoding", {})
        )
        
        self.batch_processor = BatchProcessor(
            max_workers=self.max_workers,
            config=transformer_config.get("batch", {})
        )
        
        self.realtime_converter = RealtimeConverter(
            enable_gpu=self.enable_gpu,
            config=transformer_config.get("realtime", {})
        )
        
        self.quality_optimizer = QualityOptimizer(
            enable_gpu=self.enable_gpu,
            config=transformer_config.get("quality", {})
        )
    
    async def transform(self, request: TransformationRequest) -> TransformationResult:
        """
        Transform content based on request configuration.
        
        Args:
            request: Transformation request configuration
            
        Returns:
            TransformationResult with processing metrics
        """
        start_time = time.time()
        
        try:
            # Validate request
            self._validate_request(request)
            
            # Check cache
            if self._cache and request.mode == TransformationMode.SINGLE:
                cache_key = self._generate_cache_key(request)
                if cache_key in self._cache:
                    logger.info(f"Cache hit for transformation: {cache_key}")
                    return self._cache[cache_key]
            
            # Route to appropriate transformer
            result = await self._route_transformation(request)
            
            # Update metrics
            processing_time = time.time() - start_time
            self._update_metrics(result, processing_time)
            
            # Cache result
            if self._cache and result.success and request.mode == TransformationMode.SINGLE:
                self._cache[cache_key] = result
            
            result.processing_time = processing_time
            return result
            
        except Exception as e:
            logger.error(f"Transformation failed: {str(e)}")
            self.metrics["failed_transformations"] += 1
            
            return TransformationResult(
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    async def batch_transform(
        self, 
        requests: List[TransformationRequest]
    ) -> List[TransformationResult]:
        """
        Process multiple transformation requests in batch.
        
        Args:
            requests: List of transformation requests
            
        Returns:
            List of transformation results
        """
        return await self.batch_processor.process_batch(requests, self.transform)
    
    async def convert_audio(
        self,
        input_file: str,
        output_format: str,
        quality: Union[str, QualityLevel] = QualityLevel.HIGH,
        **kwargs
    ) -> TransformationResult:
        """
        Convert audio file to specified format.
        
        Args:
            input_file: Input audio file path
            output_format: Target audio format (mp3, wav, flac, etc.)
            quality: Output quality level
            **kwargs: Additional conversion options
            
        Returns:
            TransformationResult with conversion metrics
        """
        request = TransformationRequest(
            input_path=input_file,
            content_type=ContentType.AUDIO,
            target_format=output_format,
            quality=quality if isinstance(quality, QualityLevel) else QualityLevel(quality),
            options=kwargs
        )
        
        return await self.transform(request)
    
    async def convert_video(
        self,
        input_file: str,
        output_format: str,
        quality: Union[str, QualityLevel] = QualityLevel.HIGH,
        **kwargs
    ) -> TransformationResult:
        """
        Convert video file to specified format.
        
        Args:
            input_file: Input video file path
            output_format: Target video format (mp4, avi, mov, etc.)
            quality: Output quality level
            **kwargs: Additional conversion options
            
        Returns:
            TransformationResult with conversion metrics
        """
        request = TransformationRequest(
            input_path=input_file,
            content_type=ContentType.VIDEO,
            target_format=output_format,
            quality=quality if isinstance(quality, QualityLevel) else QualityLevel(quality),
            options=kwargs
        )
        
        return await self.transform(request)
    
    async def convert_image(
        self,
        input_file: str,
        output_format: str,
        quality: Union[str, QualityLevel] = QualityLevel.HIGH,
        **kwargs
    ) -> TransformationResult:
        """
        Convert image file to specified format.
        
        Args:
            input_file: Input image file path
            output_format: Target image format (jpg, png, webp, etc.)
            quality: Output quality level
            **kwargs: Additional conversion options
            
        Returns:
            TransformationResult with conversion metrics
        """
        request = TransformationRequest(
            input_path=input_file,
            content_type=ContentType.IMAGE,
            target_format=output_format,
            quality=quality if isinstance(quality, QualityLevel) else QualityLevel(quality),
            options=kwargs
        )
        
        return await self.transform(request)
    
    async def enhance_quality(
        self,
        input_file: str,
        content_type: Union[str, ContentType],
        enhancement_level: Union[str, QualityLevel] = QualityLevel.HIGH,
        **kwargs
    ) -> TransformationResult:
        """
        Enhance content quality using AI optimization.
        
        Args:
            input_file: Input file path
            content_type: Type of content to enhance
            enhancement_level: Quality enhancement level
            **kwargs: Additional enhancement options
            
        Returns:
            TransformationResult with enhancement metrics
        """
        request = TransformationRequest(
            input_path=input_file,
            content_type=content_type if isinstance(content_type, ContentType) else ContentType(content_type),
            quality=enhancement_level if isinstance(enhancement_level, QualityLevel) else QualityLevel(enhancement_level),
            enhance_quality=True,
            options=kwargs
        )
        
        return await self.transform(request)
    
    async def _route_transformation(self, request: TransformationRequest) -> TransformationResult:
        """Route transformation request to appropriate transformer."""
        if request.content_type == ContentType.AUDIO:
            return await self.audio_transformer.transform(request)
        elif request.content_type == ContentType.VIDEO:
            return await self.video_transformer.transform(request)
        elif request.content_type == ContentType.IMAGE:
            return await self.image_transformer.transform(request)
        elif request.content_type == ContentType.TEXT:
            return await self.text_transformer.transform(request)
        elif request.content_type == ContentType.METADATA:
            return await self.metadata_transformer.transform(request)
        else:
            raise ValueError(f"Unsupported content type: {request.content_type}")
    
    def _validate_request(self, request: TransformationRequest):
        """Validate transformation request."""
        if not request.input_path:
            raise ValueError("Input path is required")
        
        input_path = Path(request.input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {request.input_path}")
        
        if request.target_format and not self._is_format_supported(
            request.content_type, request.target_format
        ):
            raise ValueError(f"Unsupported format {request.target_format} for {request.content_type}")
    
    def _is_format_supported(self, content_type: ContentType, format_name: str) -> bool:
        """Check if format is supported for content type."""
        supported_formats = {
            ContentType.AUDIO: ["mp3", "wav", "flac", "aac", "ogg", "m4a"],
            ContentType.VIDEO: ["mp4", "avi", "mov", "mkv", "webm", "wmv"],
            ContentType.IMAGE: ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"],
            ContentType.TEXT: ["txt", "json", "xml", "html", "md", "csv"],
            ContentType.METADATA: ["json", "xml", "yaml", "csv"]
        }
        
        return format_name.lower() in supported_formats.get(content_type, [])
    
    def _generate_cache_key(self, request: TransformationRequest) -> str:
        """Generate cache key for transformation request."""
        import hashlib
        
        key_data = {
            "input_path": request.input_path,
            "content_type": request.content_type.value,
            "target_format": request.target_format,
            "quality": request.quality.value,
            "options": request.options or {}
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _update_metrics(self, result: TransformationResult, processing_time: float):
        """Update transformation metrics."""
        self.metrics["total_transformations"] += 1
        self.metrics["total_processing_time"] += processing_time
        
        if result.success:
            self.metrics["successful_transformations"] += 1
            if result.input_size > 0:
                self.metrics["total_input_size"] += result.input_size
            if result.output_size > 0:
                self.metrics["total_output_size"] += result.output_size
        else:
            self.metrics["failed_transformations"] += 1
        
        # Calculate averages
        if self.metrics["total_transformations"] > 0:
            self.metrics["average_processing_time"] = (
                self.metrics["total_processing_time"] / self.metrics["total_transformations"]
            )
        
        if self.metrics["total_input_size"] > 0 and self.metrics["total_output_size"] > 0:
            self.metrics["compression_efficiency"] = (
                1.0 - (self.metrics["total_output_size"] / self.metrics["total_input_size"])
            ) * 100
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get transformation metrics."""
        return self.metrics.copy()
    
    def clear_cache(self):
        """Clear transformation cache."""
        if self._cache:
            self._cache.clear()
            logger.info("Transformation cache cleared")
    
    def get_supported_formats(self, content_type: Union[str, ContentType]) -> List[str]:
        """Get supported formats for content type."""
        if isinstance(content_type, str):
            content_type = ContentType(content_type)
        
        supported_formats = {
            ContentType.AUDIO: ["mp3", "wav", "flac", "aac", "ogg", "m4a"],
            ContentType.VIDEO: ["mp4", "avi", "mov", "mkv", "webm", "wmv"],
            ContentType.IMAGE: ["jpg", "jpeg", "png", "webp", "gif", "bmp", "tiff"],
            ContentType.TEXT: ["txt", "json", "xml", "html", "md", "csv"],
            ContentType.METADATA: ["json", "xml", "yaml", "csv"]
        }
        
        return supported_formats.get(content_type, [])
    
    async def cleanup(self):
        """Cleanup resources and temporary files."""
        # Close thread pools
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
        # Clean up transformers
        if hasattr(self.audio_transformer, 'cleanup'):
            await self.audio_transformer.cleanup()
        if hasattr(self.video_transformer, 'cleanup'):
            await self.video_transformer.cleanup()
        if hasattr(self.image_transformer, 'cleanup'):
            await self.image_transformer.cleanup()
        if hasattr(self.text_transformer, 'cleanup'):
            await self.text_transformer.cleanup()
        if hasattr(self.metadata_transformer, 'cleanup'):
            await self.metadata_transformer.cleanup()
        
        # Clear cache
        self.clear_cache()
        
        logger.info("DataTransformer cleanup completed")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            asyncio.create_task(self.cleanup())
        except:
            pass


# Factory function for easy instantiation
def create_transformer(
    max_workers: int = 4,
    enable_gpu: bool = True,
    cache_enabled: bool = True,
    **kwargs
) -> DataTransformer:
    """
    Factory function to create DataTransformer instance.
    
    Args:
        max_workers: Maximum concurrent workers
        enable_gpu: Enable GPU acceleration
        cache_enabled: Enable result caching
        **kwargs: Additional configuration options
        
    Returns:
        Configured DataTransformer instance
    """
    return DataTransformer(
        max_workers=max_workers,
        enable_gpu=enable_gpu,
        cache_enabled=cache_enabled,
        config=kwargs
    )
