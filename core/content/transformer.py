"""
Content Transformer - Multi-Format Content Transformation Engine
===============================================================

The ContentTransformer handles format conversion, quality enhancement,
and adaptive processing for cross-platform content distribution.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime
from dataclasses import dataclass
import uuid
import os
import tempfile

import ffmpeg
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from sklearn.preprocessing import StandardScaler
from sqlalchemy.ext.asyncio import AsyncSession

from ..audio.processors.audio_converter import AudioConverter
from ..video.processors.video_converter import VideoConverter
from ..image.processors.image_converter import ImageConverter


@dataclass
class TransformationTask:
    """Content transformation task container"""
    task_id: str
    content_id: str
    source_format: str
    target_format: str
    transformation_type: str
    parameters: Dict[str, Any]
    priority: int = 1
    status: str = "pending"
    created_at: datetime = None


@dataclass
class TransformationResult:
    """Content transformation result container"""
    task_id: str
    content_id: str
    success: bool
    output_path: Optional[str] = None
    output_metadata: Dict[str, Any] = None
    transformation_time: float = 0.0
    quality_metrics: Dict[str, Any] = None
    error_message: Optional[str] = None


@dataclass
class TransformationConfig:
    """Content transformation configuration"""
    enable_quality_enhancement: bool = True
    enable_format_optimization: bool = True
    enable_compression: bool = True
    preserve_metadata: bool = True
    max_concurrent_tasks: int = 5
    temp_directory: str = "/tmp/content_transformation"
    quality_threshold: float = 0.8


class ContentTransformer:
    """
    Multi-Format Content Transformation Engine
    
    Provides comprehensive content transformation including:
    - Format conversion between different media types
    - Quality enhancement and optimization
    - Resolution and compression adjustment
    - Platform-specific adaptations
    - Batch processing and queue management
    - Real-time transformation monitoring
    """
    
    def __init__(self, db_session: AsyncSession, config: TransformationConfig = None):
        self.db = db_session
        self.config = config or TransformationConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize converters
        self.audio_converter = AudioConverter()
        self.video_converter = VideoConverter()
        self.image_converter = ImageConverter()
        
        # Task queue and processing
        self.transformation_queue = asyncio.Queue()
        self.active_tasks = {}
        self.task_results = {}
        
        # Platform-specific configurations
        self.platform_configs = self._load_platform_configurations()
        
        # Ensure temp directory exists
        os.makedirs(self.config.temp_directory, exist_ok=True)

    async def transform_content(
        self,
        content_id: str,
        transformation_specs: Dict[str, Any],
        priority: int = 1
    ) -> Dict[str, Any]:
        """
        Transform content according to specifications
        
        Args:
            content_id: Content identifier
            transformation_specs: Transformation specifications
            priority: Task priority (higher = more urgent)
            
        Returns:
            Transformation result with status and output information
        """



        try:
            self.logger.info(f"Starting content transformation for {content_id}")
            
            # Validate transformation specs
            if not await self._validate_transformation_specs(transformation_specs):
                return {
                    "success": False,
                    "error": "Invalid transformation specifications",
                    "content_id": content_id
                }
            
            # Get content data
            content_data = await self._get_content_data(content_id)
            if not content_data:
                return {
                    "success": False,
                    "error": "Content not found",
                    "content_id": content_id
                }
            
            # Create transformation tasks
            tasks = await self._create_transformation_tasks(
                content_id, 
                content_data, 
                transformation_specs, 
                priority
            )
            
            if not tasks:
                return {
                    "success": False,
                    "error": "No valid transformation tasks created",
                    "content_id": content_id
                }
            
            # Execute transformations
            results = await self._execute_transformations(tasks)
            
            # Aggregate results
            transformation_result = await self._aggregate_transformation_results(results)
            
            self.logger.info(f"Content transformation completed for {content_id}")
            
            return {
                "success": True,
                "content_id": content_id,
                "transformation_results": transformation_result,
                "tasks_completed": len(results),
                "tasks_successful": sum(1 for r in results if r.success)
            }
            
        except Exception as e:
            error_msg = f"Content transformation failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "content_id": content_id
            }

    async def transform_for_platform(
        self,
        content_id: str,
        target_platform: str,
        custom_specs: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Transform content for specific platform requirements
        
        Args:
            content_id: Content identifier
            target_platform: Target platform name
            custom_specs: Custom transformation specifications
            
        Returns:
            Platform-optimized transformation result
        """



        try:
            self.logger.info(f"Transforming content {content_id} for platform {target_platform}")
            
            # Get platform-specific configuration
            platform_config = self.platform_configs.get(target_platform)
            if not platform_config:
                return {
                    "success": False,
                    "error": f"Platform {target_platform} not supported",
                    "content_id": content_id
                }
            
            # Merge platform config with custom specs
            transformation_specs = platform_config.copy()
            if custom_specs:
                transformation_specs.update(custom_specs)
            
            # Get content data
            content_data = await self._get_content_data(content_id)
            if not content_data:
                return {
                    "success": False,
                    "error": "Content not found",
                    "content_id": content_id
                }
            
            # Determine optimal transformation based on content type
            content_type = content_data.get("content_type", "unknown")
            
            if content_type == "audio":
                result = await self._transform_audio_for_platform(
                    content_id, content_data, target_platform, transformation_specs
                )
            elif content_type == "video":
                result = await self._transform_video_for_platform(
                    content_id, content_data, target_platform, transformation_specs
                )
            elif content_type == "image":
                result = await self._transform_image_for_platform(
                    content_id, content_data, target_platform, transformation_specs
                )
            else:
                return {
                    "success": False,
                    "error": f"Content type {content_type} not supported for platform transformation",
                    "content_id": content_id
                }
            
            # Save platform-specific version
            if result.get("success"):
                await self._save_platform_version(content_id, target_platform, result)
            
            return result
            
        except Exception as e:
            error_msg = f"Platform transformation failed: {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": error_msg,
                "content_id": content_id,
                "platform": target_platform
            }

    async def _transform_audio_for_platform(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        platform: str,
        specs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform audio content for specific platform
        
        Args:
            content_id: Content identifier
            content_data: Content metadata and information
            platform: Target platform
            specs: Platform-specific transformation specs
            
        Returns:
            Audio transformation result
        """
        transformation_start = datetime.utcnow()
        
        try:
            source_path = content_data.get("file_path", "")
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source audio file not found: {source_path}")
            
            # Generate output path
            output_filename = f"{content_id}_{platform}_audio.{specs.get('format', 'mp3')}"
            output_path = os.path.join(self.config.temp_directory, output_filename)
            
            # Audio transformation parameters
            audio_params = {
                "format": specs.get("format", "mp3"),
                "bitrate": specs.get("bitrate", "128k"),
                "sample_rate": specs.get("sample_rate", 44100),
                "channels": specs.get("channels", 2),
                "volume_normalization": specs.get("volume_normalization", True),
                "noise_reduction": specs.get("noise_reduction", False)
            }
            
            # Perform audio conversion
            conversion_result = await self.audio_converter.convert_audio(
                source_path,
                output_path,
                audio_params
            )
            
            if not conversion_result.get("success"):
                raise Exception(f"Audio conversion failed: {conversion_result.get('error')}")
            
            # Quality enhancement if enabled
            if self.config.enable_quality_enhancement and specs.get("enhance_quality", True):
                enhanced_path = await self._enhance_audio_quality(output_path, audio_params)
                if enhanced_path:
                    output_path = enhanced_path
            
            # Validate output
            if not os.path.exists(output_path):
                raise FileNotFoundError("Transformed audio file was not created")
            
            # Calculate file size and quality metrics
            output_size = os.path.getsize(output_path)
            quality_metrics = await self._calculate_audio_quality_metrics(
                source_path, output_path
            )
            
            transformation_time = (datetime.utcnow() - transformation_start).total_seconds()
            
            return {
                "success": True,
                "content_id": content_id,
                "platform": platform,
                "output_path": output_path,
                "output_metadata": {
                    "format": audio_params["format"],
                    "bitrate": audio_params["bitrate"],
                    "sample_rate": audio_params["sample_rate"],
                    "channels": audio_params["channels"],
                    "file_size": output_size,
                    "duration": conversion_result.get("duration", 0)
                },
                "quality_metrics": quality_metrics,
                "transformation_time": transformation_time
            }
            
        except Exception as e:
            transformation_time = (datetime.utcnow() - transformation_start).total_seconds()
            raise Exception(f"Audio platform transformation failed: {str(e)}")

    async def _transform_video_for_platform(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        platform: str,
        specs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform video content for specific platform
        
        Args:
            content_id: Content identifier
            content_data: Content metadata and information
            platform: Target platform
            specs: Platform-specific transformation specs
            
        Returns:
            Video transformation result
        """
        transformation_start = datetime.utcnow()
        
        try:
            source_path = content_data.get("file_path", "")
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source video file not found: {source_path}")
            
            # Generate output path
            output_filename = f"{content_id}_{platform}_video.{specs.get('format', 'mp4')}"
            output_path = os.path.join(self.config.temp_directory, output_filename)
            
            # Video transformation parameters
            video_params = {
                "format": specs.get("format", "mp4"),
                "codec": specs.get("codec", "h264"),
                "resolution": specs.get("resolution", "1920x1080"),
                "framerate": specs.get("framerate", 30),
                "bitrate": specs.get("bitrate", "2M"),
                "audio_bitrate": specs.get("audio_bitrate", "128k"),
                "quality": specs.get("quality", "high")
            }
            
            # Handle platform-specific requirements
            if platform == "tiktok":
                video_params.update({
                    "resolution": "720x1280",  # Vertical format
                    "max_duration": 60,
                    "framerate": 30
                })
            elif platform == "instagram":
                video_params.update({
                    "resolution": "1080x1080",  # Square format
                    "max_duration": 60,
                    "framerate": 30
                })
            elif platform == "youtube":
                video_params.update({
                    "resolution": "1920x1080",  # 16:9 format
                    "framerate": 60,
                    "quality": "high"
                })
            
            # Perform video conversion
            conversion_result = await self.video_converter.convert_video(
                source_path,
                output_path,
                video_params
            )
            
            if not conversion_result.get("success"):
                raise Exception(f"Video conversion failed: {conversion_result.get('error')}")
            
            # Apply platform-specific optimizations
            optimized_path = await self._apply_platform_video_optimizations(
                output_path, platform, specs
            )
            if optimized_path:
                output_path = optimized_path
            
            # Validate output
            if not os.path.exists(output_path):
                raise FileNotFoundError("Transformed video file was not created")
            
            # Calculate file size and quality metrics
            output_size = os.path.getsize(output_path)
            quality_metrics = await self._calculate_video_quality_metrics(
                source_path, output_path
            )
            
            transformation_time = (datetime.utcnow() - transformation_start).total_seconds()
            
            return {
                "success": True,
                "content_id": content_id,
                "platform": platform,
                "output_path": output_path,
                "output_metadata": {
                    "format": video_params["format"],
                    "codec": video_params["codec"],
                    "resolution": video_params["resolution"],
                    "framerate": video_params["framerate"],
                    "bitrate": video_params["bitrate"],
                    "file_size": output_size,
                    "duration": conversion_result.get("duration", 0)
                },
                "quality_metrics": quality_metrics,
                "transformation_time": transformation_time
            }
            
        except Exception as e:
            transformation_time = (datetime.utcnow() - transformation_start).total_seconds()
            raise Exception(f"Video platform transformation failed: {str(e)}")

    async def _transform_image_for_platform(
        self,
        content_id: str,
        content_data: Dict[str, Any],
        platform: str,
        specs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Transform image content for specific platform
        
        Args:
            content_id: Content identifier
            content_data: Content metadata and information
            platform: Target platform
            specs: Platform-specific transformation specs
            
        Returns:
            Image transformation result
        """
        transformation_start = datetime.utcnow()
        
        try:
            source_path = content_data.get("file_path", "")
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source image file not found: {source_path}")
            
            # Generate output path
            output_filename = f"{content_id}_{platform}_image.{specs.get('format', 'jpg')}"
            output_path = os.path.join(self.config.temp_directory, output_filename)
            
            # Load image
            with Image.open(source_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB' and specs.get('format', 'jpg').lower() in ['jpg', 'jpeg']:
                    img = img.convert('RGB')
                
                # Platform-specific transformations
                if platform == "instagram":
                    # Instagram prefers square images (1080x1080)
                    target_size = specs.get("size", (1080, 1080))
                    img = self._resize_image_smart(img, target_size, maintain_aspect=False)
                    
                elif platform == "twitter":
                    # Twitter optimal size (1200x675)
                    target_size = specs.get("size", (1200, 675))
                    img = self._resize_image_smart(img, target_size, maintain_aspect=True)
                    
                elif platform == "facebook":
                    # Facebook cover or post size
                    target_size = specs.get("size", (1200, 630))
                    img = self._resize_image_smart(img, target_size, maintain_aspect=True)
                    
                elif platform == "linkedin":
                    # LinkedIn post size
                    target_size = specs.get("size", (1200, 627))
                    img = self._resize_image_smart(img, target_size, maintain_aspect=True)
                
                # Apply quality enhancement
                if self.config.enable_quality_enhancement and specs.get("enhance_quality", True):
                    img = await self._enhance_image_quality(img)
                
                # Apply compression if needed
                quality = specs.get("quality", 90)
                if self.config.enable_compression:
                    quality = min(quality, 85)  # Optimize for web
                
                # Save transformed image
                save_params = {"quality": quality, "optimize": True}
                if specs.get('format', 'jpg').lower() in ['jpg', 'jpeg']:
                    save_params["progressive"] = True
                
                img.save(output_path, **save_params)
            
            # Validate output
            if not os.path.exists(output_path):
                raise FileNotFoundError("Transformed image file was not created")
            
            # Calculate file size and quality metrics
            output_size = os.path.getsize(output_path)
            quality_metrics = await self._calculate_image_quality_metrics(
                source_path, output_path
            )
            
            # Get image dimensions
            with Image.open(output_path) as img:
                width, height = img.size
            
            transformation_time = (datetime.utcnow() - transformation_start).total_seconds()
            
            return {
                "success": True,
                "content_id": content_id,
                "platform": platform,
                "output_path": output_path,
                "output_metadata": {
                    "format": specs.get('format', 'jpg'),
                    "width": width,
                    "height": height,
                    "file_size": output_size,
                    "quality": quality
                },
                "quality_metrics": quality_metrics,
                "transformation_time": transformation_time
            }
            
        except Exception as e:
            transformation_time = (datetime.utcnow() - transformation_start).total_seconds()
            raise Exception(f"Image platform transformation failed: {str(e)}")

    # Helper methods

    def _load_platform_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Load platform-specific transformation configurations"""



        return {
            "youtube": {
                "video": {
                    "format": "mp4",
                    "codec": "h264",
                    "resolution": "1920x1080",
                    "framerate": 60,
                    "bitrate": "8M",
                    "audio_bitrate": "192k",
                    "quality": "high"
                },
                "image": {
                    "format": "jpg",
                    "size": (1280, 720),
                    "quality": 90
                }
            },
            "tiktok": {
                "video": {
                    "format": "mp4",
                    "codec": "h264",
                    "resolution": "720x1280",
                    "framerate": 30,
                    "bitrate": "1.5M",
                    "audio_bitrate": "128k",
                    "max_duration": 60
                },
                "image": {
                    "format": "jpg",
                    "size": (720, 1280),
                    "quality": 85
                }
            },
            "instagram": {
                "video": {
                    "format": "mp4",
                    "codec": "h264",
                    "resolution": "1080x1080",
                    "framerate": 30,
                    "bitrate": "3.5M",
                    "audio_bitrate": "128k",
                    "max_duration": 60
                },
                "image": {
                    "format": "jpg",
                    "size": (1080, 1080),
                    "quality": 90
                }
            },
            "spotify": {
                "audio": {
                    "format": "mp3",
                    "bitrate": "320k",
                    "sample_rate": 44100,
                    "channels": 2,
                    "volume_normalization": True
                }
            },
            "soundcloud": {
                "audio": {
                    "format": "mp3",
                    "bitrate": "256k",
                    "sample_rate": 44100,
                    "channels": 2,
                    "volume_normalization": True
                }
            }
        }

    def _resize_image_smart(self, img: Image.Image, target_size: Tuple[int, int], maintain_aspect: bool = True) -> Image.Image:
        """Intelligently resize image with optional aspect ratio preservation"""
        if maintain_aspect:
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Create new image with target size and paste resized image centered
            new_img = Image.new('RGB', target_size, (255, 255, 255))
            paste_x = (target_size[0] - img.width) // 2
            paste_y = (target_size[1] - img.height) // 2
            new_img.paste(img, (paste_x, paste_y))
            
            return new_img
        else:
            return img.resize(target_size, Image.Resampling.LANCZOS)

    async def _enhance_image_quality(self, img: Image.Image) -> Image.Image:
        """Enhance image quality using various filters and adjustments"""



        try:
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.2)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            
            # Enhance color
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.05)
            
            # Apply subtle unsharp mask
            img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=3))
            
            return img
            
        except Exception as e:
            self.logger.warning(f"Image enhancement failed: {str(e)}")
            return img

    # Placeholder methods for actual implementations
    async def _validate_transformation_specs(self, specs: Dict[str, Any]) -> bool:
        """Validate transformation specifications"""



        return True

    async def _get_content_data(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content data from database"""
        # Mock implementation
        return {
            "id": content_id,
            "content_type": "video",
            "file_path": "/path/to/content",
            "metadata": {}
        }

    async def _create_transformation_tasks(
        self, 
        content_id: str, 
        content_data: Dict[str, Any], 
        specs: Dict[str, Any], 
        priority: int
    ) -> List[TransformationTask]:
        """Create transformation tasks from specifications"""



        return []

    async def _execute_transformations(self, tasks: List[TransformationTask]) -> List[TransformationResult]:
        """Execute transformation tasks"""



        return []

    async def _aggregate_transformation_results(self, results: List[TransformationResult]) -> Dict[str, Any]:
        """Aggregate multiple transformation results"""



        return {}

    async def _save_platform_version(self, content_id: str, platform: str, result: Dict[str, Any]) -> None:
        """Save platform-specific version to database"""
        pass

    async def _enhance_audio_quality(self, file_path: str, params: Dict[str, Any]) -> Optional[str]:
        """Enhance audio quality"""



        return None

    async def _apply_platform_video_optimizations(self, file_path: str, platform: str, specs: Dict[str, Any]) -> Optional[str]:
        """Apply platform-specific video optimizations"""



        return None

    async def _calculate_audio_quality_metrics(self, source_path: str, output_path: str) -> Dict[str, Any]:
        """Calculate audio quality metrics"""



        return {}

    async def _calculate_video_quality_metrics(self, source_path: str, output_path: str) -> Dict[str, Any]:
        """Calculate video quality metrics"""



        return {}

    async def _calculate_image_quality_metrics(self, source_path: str, output_path: str) -> Dict[str, Any]:
        """Calculate image quality metrics"""



        return {}
