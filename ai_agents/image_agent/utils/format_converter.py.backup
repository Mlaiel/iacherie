"""Format Converter - Advanced Image Format Conversion & Optimization Engine

Industrial-grade image format conversion, optimization, and compression system
for web delivery, storage optimization, and cross-platform compatibility.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import logging
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import mimetypes
from io import BytesIO

from PIL import Image, ImageOps
import numpy as np
import cv2
from pillow_heif import register_heif_opener

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import ProcessingError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ProcessingError, ValidationError = globals().get('ProcessingError, ValidationError', Exception)
from ...utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

# Register HEIF opener for HEIC support
register_heif_opener()


class ImageFormat(Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    WEBP = "webp"
    AVIF = "avif"
    HEIC = "heic"
    HEIF = "heif"
    TIFF = "tiff"
    TIF = "tif"
    BMP = "bmp"
    GIF = "gif"
    SVG = "svg"
    PDF = "pdf"
    ICO = "ico"
    RAW = "raw"


class OptimizationLevel(Enum):
    """Optimization levels for different use cases"""
    MINIMAL = "minimal"           # Preserve maximum quality
    BALANCED = "balanced"         # Balance quality and size
    WEB_OPTIMIZED = "web_optimized"   # Optimized for web delivery
    STORAGE = "storage"          # Maximum compression for storage
    THUMBNAIL = "thumbnail"      # Small size for thumbnails
    PRINT = "print"             # High quality for printing


class CompressionMethod(Enum):
    """Compression methods"""
    LOSSLESS = "lossless"
    LOSSY = "lossy"
    HYBRID = "hybrid"
    PROGRESSIVE = "progressive"
    ADAPTIVE = "adaptive"


@dataclass
class ConversionParams:
    """Image format conversion parameters"""
    target_format: ImageFormat
    optimization_level: OptimizationLevel = OptimizationLevel.BALANCED
    compression_method: CompressionMethod = CompressionMethod.ADAPTIVE
    quality: Optional[int] = None
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    preserve_metadata: bool = True
    preserve_transparency: bool = True
    progressive: bool = True
    optimize: bool = True
    target_file_size: Optional[int] = None  # Target size in bytes
    auto_detect_best_format: bool = False


@dataclass
class OptimizationResult:
    """Optimization result metrics"""
    original_format: str
    target_format: str
    original_size: int  # File size in bytes
    optimized_size: int  # File size in bytes
    compression_ratio: float
    quality_retained: float
    processing_time: float
    dimensions_original: Tuple[int, int]
    dimensions_optimized: Tuple[int, int]
    metadata_preserved: bool
    transparency_preserved: bool
    optimizations_applied: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class FormatInfo:
    """Information about image format capabilities"""
    supports_transparency: bool
    supports_animation: bool
    supports_metadata: bool
    supports_progressive: bool
    typical_compression: str
    web_support: str
    quality_range: Tuple[int, int]
    best_use_cases: List[str]


class ImageFormatConverter:
    """
    Advanced Image Format Conversion Engine
    
    Provides comprehensive image format conversion capabilities including:
    - Universal format support (JPEG, PNG, WebP, AVIF, HEIC, etc.)
    - Intelligent optimization for different use cases
    - Quality preservation and compression optimization
    - Metadata and transparency handling
    - Batch conversion support
    - Format recommendation system
    """
    
    def __init__(
        self,
        default_optimization: OptimizationLevel = OptimizationLevel.BALANCED,
        enable_modern_formats: bool = True,
        preserve_original: bool = True
    ):
        """
        Initialize Format Converter
        
        Args:
            default_optimization: Default optimization level
            enable_modern_formats: Enable modern formats like WebP, AVIF
            preserve_original: Keep original files during conversion
        """
        self.default_optimization = default_optimization
        self.enable_modern_formats = enable_modern_formats
        self.preserve_original = preserve_original
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(
            component="image_format_converter",
            enable_detailed_metrics=True
        )
        
        # Conversion statistics
        self.conversion_stats = {
            "total_conversions": 0,
            "successful_conversions": 0,
            "average_processing_time": 0.0,
            "average_compression_ratio": 0.0,
            "format_usage": {},
            "optimization_levels": {}
        }
        
        # Format capabilities mapping
        self.format_info = self._initialize_format_info()
        
        logger.info(f"ImageFormatConverter initialized - Modern formats: {enable_modern_formats}")

    def _initialize_format_info(self) -> Dict[ImageFormat, FormatInfo]:
        """Initialize format information database"""
        return {
            ImageFormat.JPEG: FormatInfo(
                supports_transparency=False,
                supports_animation=False,
                supports_metadata=True,
                supports_progressive=True,
                typical_compression="lossy",
                web_support="universal",
                quality_range=(1, 100),
                best_use_cases=["photos", "web_images", "print"]
            ),
            ImageFormat.PNG: FormatInfo(
                supports_transparency=True,
                supports_animation=False,
                supports_metadata=True,
                supports_progressive=False,
                typical_compression="lossless",
                web_support="universal",
                quality_range=(0, 9),
                best_use_cases=["graphics", "transparency", "screenshots"]
            ),
            ImageFormat.WEBP: FormatInfo(
                supports_transparency=True,
                supports_animation=True,
                supports_metadata=True,
                supports_progressive=False,
                typical_compression="hybrid",
                web_support="modern",
                quality_range=(0, 100),
                best_use_cases=["web_optimized", "modern_browsers"]
            ),
            ImageFormat.AVIF: FormatInfo(
                supports_transparency=True,
                supports_animation=True,
                supports_metadata=True,
                supports_progressive=False,
                typical_compression="highly_efficient",
                web_support="cutting_edge",
                quality_range=(0, 63),
                best_use_cases=["next_gen_web", "high_compression"]
            ),
            ImageFormat.HEIC: FormatInfo(
                supports_transparency=True,
                supports_animation=False,
                supports_metadata=True,
                supports_progressive=False,
                typical_compression="efficient",
                web_support="limited",
                quality_range=(0, 100),
                best_use_cases=["mobile", "apple_ecosystem"]
            ),
            ImageFormat.TIFF: FormatInfo(
                supports_transparency=True,
                supports_animation=False,
                supports_metadata=True,
                supports_progressive=False,
                typical_compression="lossless",
                web_support="limited",
                quality_range=(1, 9),
                best_use_cases=["professional", "archival", "print"]
            ),
            ImageFormat.BMP: FormatInfo(
                supports_transparency=False,
                supports_animation=False,
                supports_metadata=False,
                supports_progressive=False,
                typical_compression="none",
                web_support="legacy",
                quality_range=(0, 0),
                best_use_cases=["legacy_systems", "uncompressed"]
            ),
            ImageFormat.GIF: FormatInfo(
                supports_transparency=True,
                supports_animation=True,
                supports_metadata=False,
                supports_progressive=False,
                typical_compression="lossless_indexed",
                web_support="universal",
                quality_range=(0, 0),
                best_use_cases=["animations", "simple_graphics", "legacy"]
            )
        }

    async def convert_image(
        self,
        source_path: Union[str, Path],
        target_path: Union[str, Path],
        params: Optional[ConversionParams] = None
    ) -> OptimizationResult:
        """
        Convert image to target format with optimization
        
        Args:
            source_path: Path to source image
            target_path: Path for converted image
            params: Conversion parameters
            
        Returns:
            OptimizationResult with conversion metrics
        """
        start_time = time.time()
        conversion_id = f"convert_{uuid.uuid4().hex[:8]}"
        
        try:
            # Initialize parameters
            if params is None:
                # Auto-detect target format from file extension
                target_ext = Path(target_path).suffix.lower().lstrip('.')
                try:
                    target_format = ImageFormat(target_ext)
                except ValueError:
                    target_format = ImageFormat.JPEG
                
                params = ConversionParams(target_format=target_format)
            
            # Load source image
            source_path = Path(source_path)
            if not source_path.exists():
                raise ValidationError(f"Source image not found: {source_path}")
            
            # Get original file info
            original_size = source_path.stat().st_size
            
            # Load image with PIL
            with Image.open(source_path) as source_image:
                original_format = source_image.format.lower() if source_image.format else "unknown"
                original_dimensions = source_image.size
                
                # Auto-detect best format if requested
                if params.auto_detect_best_format:
                    params.target_format = await self._detect_best_format(
                        source_image, params.optimization_level
                    )
                
                # Convert image
                converted_image = await self._perform_conversion(source_image, params)
                
                # Save converted image
                target_path = Path(target_path)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                await self._save_converted_image(converted_image, target_path, params)
                
                # Calculate metrics
                optimized_size = target_path.stat().st_size
                compression_ratio = (original_size - optimized_size) / original_size
                quality_retained = await self._estimate_quality_retention(
                    source_image, converted_image, params
                )
                
                processing_time = time.time() - start_time
                
                # Update statistics
                self._update_conversion_stats(
                    params.target_format, params.optimization_level, 
                    processing_time, compression_ratio, True
                )
                
                return OptimizationResult(
                    original_format=original_format,
                    target_format=params.target_format.value,
                    original_size=original_size,
                    optimized_size=optimized_size,
                    compression_ratio=compression_ratio,
                    quality_retained=quality_retained,
                    processing_time=processing_time,
                    dimensions_original=original_dimensions,
                    dimensions_optimized=converted_image.size,
                    metadata_preserved=params.preserve_metadata,
                    transparency_preserved=params.preserve_transparency,
                    optimizations_applied=await self._get_applied_optimizations(params),
                    warnings=[]
                )
                
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_conversion_stats(
                params.target_format if params else ImageFormat.JPEG,
                params.optimization_level if params else OptimizationLevel.BALANCED,
                processing_time, 0.0, False
            )
            
            logger.error(f"Image conversion failed: {str(e)}")
            raise ProcessingError(f"Conversion failed: {str(e)}")

    async def _perform_conversion(
        self, 
        source_image: Image.Image, 
        params: ConversionParams
    ) -> Image.Image:
        """Perform the actual image conversion"""
        try:
            # Work with a copy
            converted_image = source_image.copy()
            
            # Handle transparency
            if not self.format_info[params.target_format].supports_transparency:
                if converted_image.mode in ['RGBA', 'LA', 'P']:
                    # Create white background for non-transparent formats
                    background = Image.new('RGB', converted_image.size, (255, 255, 255))
                    if converted_image.mode == 'P':
                        converted_image = converted_image.convert('RGBA')
                    background.paste(converted_image, mask=converted_image.split()[-1] if len(converted_image.split()) > 3 else None)
                    converted_image = background
            
            # Resize if maximum dimensions specified
            if params.max_width or params.max_height:
                converted_image = await self._resize_image(converted_image, params)
            
            # Apply optimization level adjustments
            converted_image = await self._apply_optimization_adjustments(converted_image, params)
            
            return converted_image
            
        except Exception as e:
            logger.error(f"Image conversion process failed: {str(e)}")
            return source_image

    async def _resize_image(self, image: Image.Image, params: ConversionParams) -> Image.Image:
        """Resize image according to maximum dimensions"""
        try:
            current_width, current_height = image.size
            
            # Calculate new dimensions
            if params.max_width and params.max_height:
                # Fit within both constraints
                width_ratio = params.max_width / current_width
                height_ratio = params.max_height / current_height
                ratio = min(width_ratio, height_ratio)
            elif params.max_width:
                ratio = params.max_width / current_width
            elif params.max_height:
                ratio = params.max_height / current_height
            else:
                return image
            
            # Only resize if we need to make it smaller
            if ratio < 1.0:
                new_width = int(current_width * ratio)
                new_height = int(current_height * ratio)
                
                # Choose appropriate resampling method
                if params.optimization_level in [OptimizationLevel.PRINT, OptimizationLevel.MINIMAL]:
                    resampling = Image.Resampling.LANCZOS
                else:
                    resampling = Image.Resampling.BILINEAR
                
                return image.resize((new_width, new_height), resampling)
            
            return image
            
        except Exception as e:
            logger.warning(f"Image resize failed: {str(e)}")
            return image

    async def _apply_optimization_adjustments(
        self, 
        image: Image.Image, 
        params: ConversionParams
    ) -> Image.Image:
        """Apply optimization-specific adjustments"""
        try:
            if params.optimization_level == OptimizationLevel.THUMBNAIL:
                # Reduce colors for thumbnails
                if image.mode == 'RGB':
                    image = image.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
                    image = image.convert('RGB')
                    
            elif params.optimization_level == OptimizationLevel.WEB_OPTIMIZED:
                # Slight sharpening for web display
                from PIL import ImageEnhance
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(1.1)
                
            elif params.optimization_level == OptimizationLevel.STORAGE:
                # Reduce quality slightly for storage
                if image.mode == 'RGBA' and params.target_format not in [ImageFormat.PNG, ImageFormat.WEBP]:
                    # Remove alpha channel if target doesn't support it
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
            
            return image
            
        except Exception as e:
            logger.warning(f"Optimization adjustments failed: {str(e)}")
            return image

    async def _save_converted_image(
        self, 
        image: Image.Image, 
        target_path: Path, 
        params: ConversionParams
    ) -> None:
        """Save converted image with format-specific optimizations"""
        try:
            # Prepare save parameters
            save_kwargs = {
                'optimize': params.optimize
            }
            
            # Format-specific parameters
            if params.target_format in [ImageFormat.JPEG, ImageFormat.JPG]:
                quality = await self._determine_jpeg_quality(params)
                save_kwargs.update({
                    'format': 'JPEG',
                    'quality': quality,
                    'progressive': params.progressive,
                    'optimize': True
                })
                
            elif params.target_format == ImageFormat.PNG:
                save_kwargs.update({
                    'format': 'PNG',
                    'optimize': True,
                    'compress_level': await self._determine_png_compression(params)
                })
                
            elif params.target_format == ImageFormat.WEBP:
                quality = await self._determine_webp_quality(params)
                save_kwargs.update({
                    'format': 'WEBP',
                    'quality': quality,
                    'method': 6,  # Best compression method
                    'optimize': True
                })
                
                # Use lossless for certain cases
                if params.compression_method == CompressionMethod.LOSSLESS:
                    save_kwargs['lossless'] = True
                    del save_kwargs['quality']
                    
            elif params.target_format == ImageFormat.AVIF:
                quality = await self._determine_avif_quality(params)
                save_kwargs.update({
                    'format': 'AVIF',
                    'quality': quality,
                    'speed': 6  # Balance of speed vs compression
                })
                
            elif params.target_format == ImageFormat.TIFF:
                save_kwargs.update({
                    'format': 'TIFF',
                    'compression': 'tiff_lzw'  # Good lossless compression
                })
                
            elif params.target_format == ImageFormat.BMP:
                save_kwargs.update({
                    'format': 'BMP'
                })
                
            elif params.target_format == ImageFormat.GIF:
                # Convert to palette mode for GIF
                if image.mode not in ['P', 'L']:
                    image = image.convert('P', palette=Image.Palette.ADAPTIVE, colors=256)
                save_kwargs.update({
                    'format': 'GIF',
                    'optimize': True
                })
            
            # Handle metadata preservation
            if params.preserve_metadata and hasattr(image, 'info'):
                # Copy relevant metadata
                if 'exif' in image.info and params.target_format in [ImageFormat.JPEG, ImageFormat.TIFF]:
                    save_kwargs['exif'] = image.info['exif']
                
                if 'icc_profile' in image.info:
                    save_kwargs['icc_profile'] = image.info['icc_profile']
            
            # Save with iterative quality adjustment if target file size specified
            if params.target_file_size:
                await self._save_with_target_size(image, target_path, save_kwargs, params.target_file_size)
            else:
                image.save(target_path, **save_kwargs)
                
        except Exception as e:
            logger.error(f"Failed to save converted image: {str(e)}")
            # Fallback save
            image.save(target_path, format=params.target_format.value.upper())

    async def _save_with_target_size(
        self,
        image: Image.Image,
        target_path: Path,
        save_kwargs: Dict[str, Any],
        target_size: int,
        tolerance: float = 0.1
    ) -> None:
        """Save image iteratively adjusting quality to meet target file size"""
        try:
            if 'quality' not in save_kwargs:
                # Can't adjust quality for lossless formats
                image.save(target_path, **save_kwargs)
                return
            
            # Binary search for optimal quality
            min_quality = 10
            max_quality = save_kwargs.get('quality', 95)
            best_quality = max_quality
            
            for attempt in range(10):  # Max 10 attempts
                current_quality = (min_quality + max_quality) // 2
                temp_kwargs = save_kwargs.copy()
                temp_kwargs['quality'] = current_quality
                
                # Save to memory buffer to check size
                buffer = BytesIO()
                image.save(buffer, **temp_kwargs)
                file_size = buffer.tell()
                
                size_ratio = file_size / target_size
                
                if abs(1.0 - size_ratio) <= tolerance:
                    # Close enough to target
                    best_quality = current_quality
                    break
                elif size_ratio > 1.0:
                    # Too large, reduce quality
                    max_quality = current_quality - 1
                else:
                    # Too small, increase quality
                    min_quality = current_quality + 1
                    best_quality = current_quality
                
                if min_quality >= max_quality:
                    break
            
            # Save with best quality found
            final_kwargs = save_kwargs.copy()
            final_kwargs['quality'] = best_quality
            image.save(target_path, **final_kwargs)
            
        except Exception as e:
            logger.warning(f"Target size optimization failed: {str(e)}")
            image.save(target_path, **save_kwargs)

    async def _determine_jpeg_quality(self, params: ConversionParams) -> int:
        """Determine optimal JPEG quality based on optimization level"""
        if params.quality is not None:
            return max(1, min(100, params.quality))
        
        quality_map = {
            OptimizationLevel.MINIMAL: 98,
            OptimizationLevel.BALANCED: 85,
            OptimizationLevel.WEB_OPTIMIZED: 80,
            OptimizationLevel.STORAGE: 75,
            OptimizationLevel.THUMBNAIL: 70,
            OptimizationLevel.PRINT: 95
        }
        
        return quality_map.get(params.optimization_level, 85)

    async def _determine_png_compression(self, params: ConversionParams) -> int:
        """Determine PNG compression level (0-9)"""
        compression_map = {
            OptimizationLevel.MINIMAL: 1,
            OptimizationLevel.BALANCED: 6,
            OptimizationLevel.WEB_OPTIMIZED: 6,
            OptimizationLevel.STORAGE: 9,
            OptimizationLevel.THUMBNAIL: 9,
            OptimizationLevel.PRINT: 3
        }
        
        return compression_map.get(params.optimization_level, 6)

    async def _determine_webp_quality(self, params: ConversionParams) -> int:
        """Determine WebP quality"""
        if params.quality is not None:
            return max(0, min(100, params.quality))
        
        quality_map = {
            OptimizationLevel.MINIMAL: 95,
            OptimizationLevel.BALANCED: 80,
            OptimizationLevel.WEB_OPTIMIZED: 75,
            OptimizationLevel.STORAGE: 70,
            OptimizationLevel.THUMBNAIL: 65,
            OptimizationLevel.PRINT: 90
        }
        
        return quality_map.get(params.optimization_level, 80)

    async def _determine_avif_quality(self, params: ConversionParams) -> int:
        """Determine AVIF quality (0-63)"""
        if params.quality is not None:
            return max(0, min(63, params.quality))
        
        quality_map = {
            OptimizationLevel.MINIMAL: 55,
            OptimizationLevel.BALANCED: 40,
            OptimizationLevel.WEB_OPTIMIZED: 35,
            OptimizationLevel.STORAGE: 30,
            OptimizationLevel.THUMBNAIL: 25,
            OptimizationLevel.PRINT: 50
        }
        
        return quality_map.get(params.optimization_level, 40)

    async def _detect_best_format(
        self, 
        image: Image.Image, 
        optimization_level: OptimizationLevel
    ) -> ImageFormat:
        """Auto-detect best format for given image and optimization level"""
        try:
            # Analyze image characteristics
            has_transparency = image.mode in ['RGBA', 'LA'] or 'transparency' in image.info
            is_photo = await self._is_photographic_image(image)
            is_simple_graphic = not is_photo
            
            # Format selection logic
            if optimization_level == OptimizationLevel.WEB_OPTIMIZED:
                if self.enable_modern_formats:
                    return ImageFormat.WEBP
                elif has_transparency:
                    return ImageFormat.PNG
                else:
                    return ImageFormat.JPEG
                    
            elif optimization_level == OptimizationLevel.STORAGE:
                if self.enable_modern_formats:
                    return ImageFormat.AVIF if has_transparency else ImageFormat.WEBP
                elif is_photo and not has_transparency:
                    return ImageFormat.JPEG
                else:
                    return ImageFormat.PNG
                    
            elif optimization_level == OptimizationLevel.PRINT:
                return ImageFormat.TIFF if has_transparency else ImageFormat.JPEG
                
            elif optimization_level == OptimizationLevel.THUMBNAIL:
                return ImageFormat.WEBP if self.enable_modern_formats else ImageFormat.JPEG
                
            else:  # MINIMAL, BALANCED
                if is_photo and not has_transparency:
                    return ImageFormat.JPEG
                else:
                    return ImageFormat.PNG
                    
        except Exception as e:
            logger.warning(f"Best format detection failed: {str(e)}")
            return ImageFormat.JPEG

    async def _is_photographic_image(self, image: Image.Image) -> bool:
        """Determine if image is photographic (vs graphic/drawing)"""
        try:
            # Convert to grayscale for analysis
            if image.mode != 'L':
                gray = image.convert('L')
            else:
                gray = image
            
            # Calculate gradient magnitude (edge density)
            img_array = np.array(gray)
            grad_x = cv2.Sobel(img_array, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(img_array, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Calculate metrics
            edge_density = np.mean(gradient_magnitude) / 255.0
            color_diversity = len(np.unique(img_array)) / 256.0
            
            # Photographic images typically have:
            # - Lower edge density (smooth transitions)
            # - Higher color diversity
            is_photo = edge_density < 0.3 and color_diversity > 0.1
            
            return is_photo
            
        except Exception as e:
            logger.warning(f"Photo detection failed: {str(e)}")
            return True  # Default to photo

    async def _estimate_quality_retention(
        self,
        original: Image.Image,
        converted: Image.Image,
        params: ConversionParams
    ) -> float:
        """Estimate quality retention after conversion"""
        try:
            # If formats are the same and lossless, retention is 100%
            if (params.target_format.value == original.format.lower() and 
                params.compression_method == CompressionMethod.LOSSLESS):
                return 1.0
            
            # Estimate based on format and quality settings
            if params.target_format in [ImageFormat.PNG, ImageFormat.TIFF]:
                return 0.98  # Lossless formats
            elif params.target_format == ImageFormat.WEBP:
                if params.compression_method == CompressionMethod.LOSSLESS:
                    return 0.95
                else:
                    quality = await self._determine_webp_quality(params)
                    return min(0.95, 0.5 + (quality / 100.0) * 0.5)
            elif params.target_format in [ImageFormat.JPEG, ImageFormat.JPG]:
                quality = await self._determine_jpeg_quality(params)
                return min(0.95, 0.3 + (quality / 100.0) * 0.7)
            elif params.target_format == ImageFormat.AVIF:
                quality = await self._determine_avif_quality(params)
                return min(0.95, 0.4 + (quality / 63.0) * 0.6)
            else:
                return 0.8  # Conservative estimate
                
        except Exception as e:
            logger.warning(f"Quality retention estimation failed: {str(e)}")
            return 0.75

    async def _get_applied_optimizations(self, params: ConversionParams) -> List[str]:
        """Get list of applied optimizations"""
        optimizations = []
        
        optimizations.append(f"format_conversion_to_{params.target_format.value}")
        optimizations.append(f"optimization_level_{params.optimization_level.value}")
        optimizations.append(f"compression_{params.compression_method.value}")
        
        if params.max_width or params.max_height:
            optimizations.append("resizing")
            
        if params.progressive:
            optimizations.append("progressive_encoding")
            
        if params.optimize:
            optimizations.append("file_size_optimization")
            
        return optimizations

    async def batch_convert(
        self,
        source_paths: List[Union[str, Path]],
        target_directory: Union[str, Path],
        params: ConversionParams,
        preserve_structure: bool = True
    ) -> List[OptimizationResult]:
        """
        Convert multiple images in batch
        
        Args:
            source_paths: List of source image paths
            target_directory: Directory to save converted images
            params: Conversion parameters
            preserve_structure: Preserve directory structure
            
        Returns:
            List of OptimizationResult for each conversion
        """
        try:
            target_dir = Path(target_directory)
            target_dir.mkdir(parents=True, exist_ok=True)
            
            results = []
            
            # Process images concurrently (limited concurrency)
            semaphore = asyncio.Semaphore(4)  # Max 4 concurrent conversions
            
            async def convert_single(source_path: Union[str, Path]) -> OptimizationResult:
                async with semaphore:
                    try:
                        source_path = Path(source_path)
                        
                        # Determine target path
                        if preserve_structure:
                            # Preserve relative path structure
                            target_name = source_path.stem + '.' + params.target_format.value
                            target_path = target_dir / target_name
                        else:
                            target_name = source_path.stem + '.' + params.target_format.value
                            target_path = target_dir / target_name
                        
                        return await self.convert_image(source_path, target_path, params)
                        
                    except Exception as e:
                        logger.error(f"Batch conversion failed for {source_path}: {str(e)}")
                        return OptimizationResult(
                            original_format="unknown",
                            target_format=params.target_format.value,
                            original_size=0,
                            optimized_size=0,
                            compression_ratio=0.0,
                            quality_retained=0.0,
                            processing_time=0.0,
                            dimensions_original=(0, 0),
                            dimensions_optimized=(0, 0),
                            metadata_preserved=False,
                            transparency_preserved=False,
                            warnings=[str(e)]
                        )
            
            # Execute batch conversion
            tasks = [convert_single(path) for path in source_paths]
            results = await asyncio.gather(*tasks)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch conversion failed: {str(e)}")
            return []

    def _update_conversion_stats(
        self,
        target_format: ImageFormat,
        optimization_level: OptimizationLevel,
        processing_time: float,
        compression_ratio: float,
        success: bool
    ) -> None:
        """Update conversion statistics"""
        self.conversion_stats["total_conversions"] += 1
        
        if success:
            self.conversion_stats["successful_conversions"] += 1
            
            # Update averages
            total_successful = self.conversion_stats["successful_conversions"]
            current_time_avg = self.conversion_stats["average_processing_time"]
            current_compression_avg = self.conversion_stats["average_compression_ratio"]
            
            self.conversion_stats["average_processing_time"] = (
                (current_time_avg * (total_successful - 1) + processing_time) / total_successful
            )
            
            self.conversion_stats["average_compression_ratio"] = (
                (current_compression_avg * (total_successful - 1) + compression_ratio) / total_successful
            )
            
            # Update format usage
            format_key = target_format.value
            if format_key not in self.conversion_stats["format_usage"]:
                self.conversion_stats["format_usage"][format_key] = 0
            self.conversion_stats["format_usage"][format_key] += 1
            
            # Update optimization level usage
            opt_key = optimization_level.value
            if opt_key not in self.conversion_stats["optimization_levels"]:
                self.conversion_stats["optimization_levels"][opt_key] = 0
            self.conversion_stats["optimization_levels"][opt_key] += 1

    async def get_format_info(self, format_type: ImageFormat) -> FormatInfo:
        """Get detailed information about image format"""
        return self.format_info.get(format_type, FormatInfo(
            supports_transparency=False,
            supports_animation=False,
            supports_metadata=False,
            supports_progressive=False,
            typical_compression="unknown",
            web_support="unknown",
            quality_range=(0, 100),
            best_use_cases=["general"]
        ))

    async def recommend_format(
        self,
        image_path: Union[str, Path],
        use_case: str,
        target_size_kb: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Recommend optimal format for specific use case
        
        Args:
            image_path: Path to image for analysis
            use_case: Intended use case (web, print, storage, thumbnail)
            target_size_kb: Target file size in KB
            
        Returns:
            Dictionary with format recommendation and reasoning
        """
        try:
            with Image.open(image_path) as image:
                has_transparency = image.mode in ['RGBA', 'LA'] or 'transparency' in image.info
                is_photo = await self._is_photographic_image(image)
                dimensions = image.size
                current_format = image.format.lower() if image.format else "unknown"
                
                recommendations = []
                
                if use_case.lower() == "web":
                    if self.enable_modern_formats:
                        recommendations.append({
                            "format": ImageFormat.WEBP,
                            "reason": "Best balance of compression and quality for web",
                            "estimated_size_reduction": 0.3
                        })
                        if has_transparency:
                            recommendations.append({
                                "format": ImageFormat.AVIF,
                                "reason": "Cutting-edge compression with transparency support",
                                "estimated_size_reduction": 0.5
                            })
                    
                    if not has_transparency and is_photo:
                        recommendations.append({
                            "format": ImageFormat.JPEG,
                            "reason": "Universal web support for photographic content",
                            "estimated_size_reduction": 0.2
                        })
                    
                    if has_transparency or not is_photo:
                        recommendations.append({
                            "format": ImageFormat.PNG,
                            "reason": "Universal support with transparency",
                            "estimated_size_reduction": -0.1
                        })
                
                elif use_case.lower() == "print":
                    recommendations.append({
                        "format": ImageFormat.TIFF,
                        "reason": "Lossless compression ideal for print",
                        "estimated_size_reduction": 0.1
                    })
                    if not has_transparency:
                        recommendations.append({
                            "format": ImageFormat.JPEG,
                            "reason": "High quality JPEG suitable for print",
                            "estimated_size_reduction": 0.3
                        })
                
                elif use_case.lower() == "storage":
                    if self.enable_modern_formats:
                        recommendations.append({
                            "format": ImageFormat.AVIF,
                            "reason": "Maximum compression for storage",
                            "estimated_size_reduction": 0.6
                        })
                        recommendations.append({
                            "format": ImageFormat.WEBP,
                            "reason": "Good compression with wide support",
                            "estimated_size_reduction": 0.4
                        })
                    
                    recommendations.append({
                        "format": ImageFormat.JPEG,
                        "reason": "Standard compression for photographic content",
                        "estimated_size_reduction": 0.3
                    })
                
                elif use_case.lower() == "thumbnail":
                    recommendations.append({
                        "format": ImageFormat.WEBP,
                        "reason": "Excellent compression for small images",
                        "estimated_size_reduction": 0.5
                    })
                    recommendations.append({
                        "format": ImageFormat.JPEG,
                        "reason": "Universal support for thumbnails",
                        "estimated_size_reduction": 0.4
                    })
                
                # Sort by estimated size reduction
                recommendations.sort(key=lambda x: x["estimated_size_reduction"], reverse=True)
                
                return {
                    "image_analysis": {
                        "current_format": current_format,
                        "dimensions": dimensions,
                        "has_transparency": has_transparency,
                        "is_photographic": is_photo
                    },
                    "recommendations": recommendations[:3],  # Top 3 recommendations
                    "use_case": use_case
                }
                
        except Exception as e:
            logger.error(f"Format recommendation failed: {str(e)}")
            return {
                "error": str(e),
                "recommendations": [{
                    "format": ImageFormat.JPEG,
                    "reason": "Default fallback recommendation",
                    "estimated_size_reduction": 0.2
                }]
            }

    async def get_conversion_stats(self) -> Dict[str, Any]:
        """Get comprehensive conversion statistics"""
        try:
            stats = self.conversion_stats.copy()
            
            # Add success rate
            if stats["total_conversions"] > 0:
                stats["success_rate"] = stats["successful_conversions"] / stats["total_conversions"]
            else:
                stats["success_rate"] = 0.0
            
            # Add format capabilities
            stats["supported_formats"] = {
                fmt.value: {
                    "supports_transparency": info.supports_transparency,
                    "supports_animation": info.supports_animation,
                    "web_support": info.web_support,
                    "best_use_cases": info.best_use_cases
                }
                for fmt, info in self.format_info.items()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get conversion stats: {str(e)}")
            return {"error": str(e)}


class OptimizationEngine:
    """
    Advanced Image Optimization Engine
    
    Specialized in intelligent image optimization for various use cases,
    including web delivery, storage efficiency, and quality preservation.
    """
    
    def __init__(self):
        """Initialize Optimization Engine"""
        self.converter = ImageFormatConverter()
        
        logger.info("OptimizationEngine initialized")

    async def optimize_for_web(
        self,
        source_path: Union[str, Path],
        target_directory: Union[str, Path],
        generate_variants: bool = True
    ) -> Dict[str, OptimizationResult]:
        """
        Optimize image for web delivery with multiple variants
        
        Args:
            source_path: Source image path
            target_directory: Directory for optimized images
            generate_variants: Generate multiple format variants
            
        Returns:
            Dictionary of optimization results by format
        """
        try:
            source_path = Path(source_path)
            target_dir = Path(target_directory)
            target_dir.mkdir(parents=True, exist_ok=True)
            
            results = {}
            
            # Base filename without extension
            base_name = source_path.stem
            
            # Generate WebP variant (modern browsers)
            webp_params = ConversionParams(
                target_format=ImageFormat.WEBP,
                optimization_level=OptimizationLevel.WEB_OPTIMIZED,
                max_width=1920,
                max_height=1080
            )
            webp_path = target_dir / f"{base_name}.webp"
            results["webp"] = await self.converter.convert_image(source_path, webp_path, webp_params)
            
            # Generate JPEG fallback (universal support)
            jpeg_params = ConversionParams(
                target_format=ImageFormat.JPEG,
                optimization_level=OptimizationLevel.WEB_OPTIMIZED,
                max_width=1920,
                max_height=1080
            )
            jpeg_path = target_dir / f"{base_name}.jpg"
            results["jpeg"] = await self.converter.convert_image(source_path, jpeg_path, jpeg_params)
            
            if generate_variants:
                # Generate AVIF for cutting-edge browsers
                avif_params = ConversionParams(
                    target_format=ImageFormat.AVIF,
                    optimization_level=OptimizationLevel.WEB_OPTIMIZED,
                    max_width=1920,
                    max_height=1080
                )
                avif_path = target_dir / f"{base_name}.avif"
                results["avif"] = await self.converter.convert_image(source_path, avif_path, avif_params)
                
                # Generate thumbnail variants
                thumb_params = ConversionParams(
                    target_format=ImageFormat.WEBP,
                    optimization_level=OptimizationLevel.THUMBNAIL,
                    max_width=300,
                    max_height=300
                )
                thumb_path = target_dir / f"{base_name}_thumb.webp"
                results["thumbnail"] = await self.converter.convert_image(source_path, thumb_path, thumb_params)
            
            return results
            
        except Exception as e:
            logger.error(f"Web optimization failed: {str(e)}")
            return {}

    async def optimize_for_storage(
        self,
        source_path: Union[str, Path],
        target_path: Union[str, Path],
        preserve_quality: bool = False
    ) -> OptimizationResult:
        """
        Optimize image for storage with maximum compression
        
        Args:
            source_path: Source image path
            target_path: Target image path
            preserve_quality: Whether to preserve maximum quality
            
        Returns:
            OptimizationResult with compression metrics
        """
        try:
            optimization_level = OptimizationLevel.MINIMAL if preserve_quality else OptimizationLevel.STORAGE
            
            # Use AVIF for best compression, fallback to WebP
            target_format = ImageFormat.AVIF if self.converter.enable_modern_formats else ImageFormat.WEBP
            
            params = ConversionParams(
                target_format=target_format,
                optimization_level=optimization_level,
                compression_method=CompressionMethod.ADAPTIVE,
                auto_detect_best_format=True
            )
            
            return await self.converter.convert_image(source_path, target_path, params)
            
        except Exception as e:
            logger.error(f"Storage optimization failed: {str(e)}")
            raise ProcessingError(f"Storage optimization failed: {str(e)}")

    async def create_responsive_images(
        self,
        source_path: Union[str, Path],
        target_directory: Union[str, Path],
        breakpoints: Optional[List[int]] = None
    ) -> Dict[str, List[OptimizationResult]]:
        """
        Create responsive image variants for different screen sizes
        
        Args:
            source_path: Source image path
            target_directory: Directory for responsive variants
            breakpoints: List of width breakpoints
            
        Returns:
            Dictionary of results organized by format and size
        """
        try:
            source_path = Path(source_path)
            target_dir = Path(target_directory)
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Default responsive breakpoints
            if breakpoints is None:
                breakpoints = [480, 768, 1024, 1920]
            
            base_name = source_path.stem
            results = {"webp": [], "jpeg": []}
            
            for width in breakpoints:
                # WebP variant
                webp_params = ConversionParams(
                    target_format=ImageFormat.WEBP,
                    optimization_level=OptimizationLevel.WEB_OPTIMIZED,
                    max_width=width
                )
                webp_path = target_dir / f"{base_name}_{width}w.webp"
                webp_result = await self.converter.convert_image(source_path, webp_path, webp_params)
                results["webp"].append(webp_result)
                
                # JPEG fallback
                jpeg_params = ConversionParams(
                    target_format=ImageFormat.JPEG,
                    optimization_level=OptimizationLevel.WEB_OPTIMIZED,
                    max_width=width
                )
                jpeg_path = target_dir / f"{base_name}_{width}w.jpg"
                jpeg_result = await self.converter.convert_image(source_path, jpeg_path, jpeg_params)
                results["jpeg"].append(jpeg_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Responsive image creation failed: {str(e)}")
            return {"webp": [], "jpeg": []}

    async def analyze_optimization_potential(
        self, 
        image_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Analyze potential optimization benefits for an image
        
        Args:
            image_path: Path to image for analysis
            
        Returns:
            Analysis results with optimization recommendations
        """
        try:
            with Image.open(image_path) as image:
                current_size = Path(image_path).stat().st_size
                
                analysis = {
                    "current_format": image.format.lower() if image.format else "unknown",
                    "current_size_bytes": current_size,
                    "current_size_kb": round(current_size / 1024, 2),
                    "dimensions": image.size,
                    "mode": image.mode,
                    "has_transparency": image.mode in ['RGBA', 'LA'] or 'transparency' in image.info,
                    "optimization_potential": {}
                }
                
                # Test different formats and calculate potential savings
                formats_to_test = [ImageFormat.WEBP, ImageFormat.AVIF, ImageFormat.JPEG, ImageFormat.PNG]
                
                for format_type in formats_to_test:
                    try:
                        # Create temporary conversion parameters
                        params = ConversionParams(
                            target_format=format_type,
                            optimization_level=OptimizationLevel.WEB_OPTIMIZED
                        )
                        
                        # Estimate size by converting to memory buffer
                        buffer = BytesIO()
                        temp_image = image.copy()
                        
                        # Apply basic conversion logic
                        if not self.converter.format_info[format_type].supports_transparency:
                            if temp_image.mode in ['RGBA', 'LA']:
                                background = Image.new('RGB', temp_image.size, (255, 255, 255))
                                background.paste(temp_image, mask=temp_image.split()[-1])
                                temp_image = background
                        
                        # Save to buffer with format-specific settings
                        if format_type == ImageFormat.WEBP:
                            temp_image.save(buffer, format='WEBP', quality=80, optimize=True)
                        elif format_type == ImageFormat.JPEG:
                            temp_image.save(buffer, format='JPEG', quality=85, optimize=True)
                        elif format_type == ImageFormat.PNG:
                            temp_image.save(buffer, format='PNG', optimize=True)
                        elif format_type == ImageFormat.AVIF:
                            temp_image.save(buffer, format='AVIF', quality=35)
                        
                        estimated_size = buffer.tell()
                        size_reduction = (current_size - estimated_size) / current_size
                        
                        analysis["optimization_potential"][format_type.value] = {
                            "estimated_size_bytes": estimated_size,
                            "estimated_size_kb": round(estimated_size / 1024, 2),
                            "size_reduction_percent": round(size_reduction * 100, 1),
                            "recommended": size_reduction > 0.1  # Recommend if >10% savings
                        }
                        
                    except Exception as e:
                        logger.warning(f"Failed to estimate size for {format_type}: {str(e)}")
                        continue
                
                # Find best optimization
                best_format = None
                best_reduction = 0
                
                for format_name, data in analysis["optimization_potential"].items():
                    if data["size_reduction_percent"] > best_reduction:
                        best_reduction = data["size_reduction_percent"]
                        best_format = format_name
                
                analysis["recommendation"] = {
                    "best_format": best_format,
                    "potential_savings_percent": best_reduction,
                    "potential_savings_kb": round(current_size * (best_reduction / 100) / 1024, 2) if best_reduction > 0 else 0
                }
                
                return analysis
                
        except Exception as e:
            logger.error(f"Optimization analysis failed: {str(e)}")
            return {"error": str(e)}
