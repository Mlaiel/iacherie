"""Image Optimizer

HDR image optimization and advanced image processing for content creators.
Supports AI-powered enhancement, format optimization, and quality analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Union, BinaryIO, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import uuid
import tempfile
import os

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    import cv2
    IMAGE_AVAILABLE = True
except ImportError:
    IMAGE_AVAILABLE = False

logger = logging.getLogger(__name__)


class ImageFormat(Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"
    HEIC = "heic"


class OptimizationMode(Enum):
    """Image optimization modes"""
    QUALITY = "quality"
    SIZE = "size"
    BALANCED = "balanced"
    HDR = "hdr"
    WEB = "web"
    PRINT = "print"


@dataclass
class ImageMetrics:
    """Image quality and analysis metrics"""
    width: int
    height: int
    channels: int
    bit_depth: int
    file_size: int
    format: str
    color_space: str
    has_transparency: bool
    compression_ratio: float
    quality_score: float
    sharpness: float
    brightness: float
    contrast: float
    saturation: float


@dataclass
class OptimizationResult:
    """Image optimization result"""
    success: bool
    optimized_image: Optional[bytes]
    output_format: ImageFormat
    processing_time: float
    quality_metrics: ImageMetrics
    optimization_applied: List[str]
    file_size_reduction: float
    error: Optional[str] = None


class ImageOptimizer:
    """HDR image optimization and processing engine"""
    
    def __init__(self, enable_ai_enhancement: bool = True):
        """
        Initialize image optimizer
        
        Args:
            enable_ai_enhancement: Enable AI-powered enhancements
        """
        self.enable_ai_enhancement = enable_ai_enhancement
        
        if not IMAGE_AVAILABLE:
            logger.warning("Image processing libraries not available")
    
    async def optimize_image(self,
                           image_data: Union[bytes, BinaryIO],
                           optimization_mode: OptimizationMode,
                           output_format: ImageFormat = ImageFormat.WEBP,
                           target_size: Optional[int] = None,
                           custom_params: Optional[Dict[str, Any]] = None) -> OptimizationResult:
        """
        Optimize image with specified mode and parameters
        
        Args:
            image_data: Input image data
            optimization_mode: Optimization mode to apply
            output_format: Desired output format
            target_size: Target file size in bytes
            custom_params: Additional optimization parameters
            
        Returns:
            Optimization result with enhanced image
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            if not IMAGE_AVAILABLE:
                raise Exception("Image processing libraries not available")
            
            # Convert input to bytes if needed
            if isinstance(image_data, bytes):
                image_bytes = image_data
            else:
                image_bytes = image_data.read()
                image_data.seek(0)
            
            # Load image
            with tempfile.NamedTemporaryFile() as tmp_file:
                tmp_file.write(image_bytes)
                tmp_file.flush()
                
                img = Image.open(tmp_file.name)
                original_metrics = await self._calculate_image_metrics(img, len(image_bytes))
                
                # Apply optimization based on mode
                optimized_img, optimizations = await self._apply_optimization(
                    img, optimization_mode, custom_params
                )
                
                # Convert to output format
                output_bytes = await self._convert_to_format(
                    optimized_img, output_format, target_size, optimization_mode
                )
                
                # Load optimized image for metrics
                with tempfile.NamedTemporaryFile() as tmp_output:
                    tmp_output.write(output_bytes)
                    tmp_output.flush()
                    
                    optimized_img_metrics = Image.open(tmp_output.name)
                    output_metrics = await self._calculate_image_metrics(
                        optimized_img_metrics, len(output_bytes)
                    )
                
                # Calculate file size reduction
                size_reduction = ((len(image_bytes) - len(output_bytes)) / len(image_bytes)) * 100
                processing_time = asyncio.get_event_loop().time() - start_time
                
                return OptimizationResult(
                    success=True,
                    optimized_image=output_bytes,
                    output_format=output_format,
                    processing_time=processing_time,
                    quality_metrics=output_metrics,
                    optimization_applied=optimizations,
                    file_size_reduction=size_reduction
                )
                
        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            return OptimizationResult(
                success=False,
                optimized_image=None,
                output_format=output_format,
                processing_time=0,
                quality_metrics=ImageMetrics(0, 0, 0, 0, 0, "", "", False, 0, 0, 0, 0, 0, 0),
                optimization_applied=[],
                file_size_reduction=0,
                error=str(e)
            )
    
    async def enhance_hdr_image(self,
                              image_data: Union[bytes, BinaryIO],
                              enhancement_level: str = "high") -> OptimizationResult:
        """
        Apply HDR enhancement to image
        
        Args:
            image_data: Input image data
            enhancement_level: Level of HDR enhancement
            
        Returns:
            HDR enhanced image result
        """
        return await self.optimize_image(
            image_data,
            OptimizationMode.HDR,
            ImageFormat.TIFF,
            custom_params={'enhancement_level': enhancement_level}
        )
    
    async def optimize_for_web(self,
                             image_data: Union[bytes, BinaryIO],
                             max_width: int = 1920,
                             quality: int = 85) -> OptimizationResult:
        """
        Optimize image for web delivery
        
        Args:
            image_data: Input image data
            max_width: Maximum width for web
            quality: JPEG quality (1-100)
            
        Returns:
            Web-optimized image result
        """
        return await self.optimize_image(
            image_data,
            OptimizationMode.WEB,
            ImageFormat.WEBP,
            custom_params={'max_width': max_width, 'quality': quality}
        )
    
    async def batch_optimize_images(self,
                                  image_files: List[Dict[str, Any]],
                                  optimization_mode: OptimizationMode) -> List[OptimizationResult]:
        """
        Optimize multiple images in batch
        
        Args:
            image_files: List of image files with metadata
            optimization_mode: Optimization mode to apply
            
        Returns:
            List of optimization results
        """
        tasks = []
        
        for image_file in image_files:
            task = self.optimize_image(
                image_file['data'],
                optimization_mode,
                image_file.get('output_format', ImageFormat.WEBP),
                image_file.get('target_size'),
                image_file.get('custom_params')
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                results[i] = OptimizationResult(
                    success=False,
                    optimized_image=None,
                    output_format=ImageFormat.WEBP,
                    processing_time=0,
                    quality_metrics=ImageMetrics(0, 0, 0, 0, 0, "", "", False, 0, 0, 0, 0, 0, 0),
                    optimization_applied=[],
                    file_size_reduction=0,
                    error=str(result)
                )
        
        return results
    
    async def _apply_optimization(self,
                                img: Image.Image,
                                mode: OptimizationMode,
                                params: Optional[Dict[str, Any]]) -> Tuple[Image.Image, List[str]]:
        """Apply optimization based on mode"""
        optimized_img = img.copy()
        optimizations = []
        
        try:
            if mode == OptimizationMode.QUALITY:
                # High quality processing
                if img.mode != 'RGB':
                    optimized_img = optimized_img.convert('RGB')
                    optimizations.append("color_mode_conversion")
                
                # Enhance sharpness
                enhancer = ImageEnhance.Sharpness(optimized_img)
                optimized_img = enhancer.enhance(1.2)
                optimizations.append("sharpness_enhancement")
                
                # Enhance contrast
                enhancer = ImageEnhance.Contrast(optimized_img)
                optimized_img = enhancer.enhance(1.1)
                optimizations.append("contrast_enhancement")
                
            elif mode == OptimizationMode.SIZE:
                # Size optimization
                max_dimension = params.get('max_dimension', 1200) if params else 1200
                
                if max(optimized_img.size) > max_dimension:
                    ratio = max_dimension / max(optimized_img.size)
                    new_size = tuple(int(dim * ratio) for dim in optimized_img.size)
                    optimized_img = optimized_img.resize(new_size, Image.Resampling.LANCZOS)
                    optimizations.append("size_reduction")
                
            elif mode == OptimizationMode.HDR:
                # HDR enhancement
                if optimized_img.mode != 'RGB':
                    optimized_img = optimized_img.convert('RGB')
                
                # Enhance dynamic range
                optimized_img = ImageOps.autocontrast(optimized_img)
                optimizations.append("auto_contrast")
                
                # Enhance brightness
                enhancer = ImageEnhance.Brightness(optimized_img)
                optimized_img = enhancer.enhance(1.1)
                optimizations.append("brightness_enhancement")
                
            elif mode == OptimizationMode.WEB:
                # Web optimization
                max_width = params.get('max_width', 1920) if params else 1920
                
                if optimized_img.width > max_width:
                    ratio = max_width / optimized_img.width
                    new_height = int(optimized_img.height * ratio)
                    optimized_img = optimized_img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    optimizations.append("web_resize")
                
                # Convert to RGB for web
                if optimized_img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', optimized_img.size, (255, 255, 255))
                    background.paste(optimized_img, mask=optimized_img.split()[-1])
                    optimized_img = background
                    optimizations.append("transparency_removal")
                
            return optimized_img, optimizations
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return img, []
    
    async def _convert_to_format(self,
                               img: Image.Image,
                               output_format: ImageFormat,
                               target_size: Optional[int],
                               mode: OptimizationMode) -> bytes:
        """Convert image to specified format"""
        try:
            with tempfile.NamedTemporaryFile() as tmp_file:
                
                save_kwargs = {}
                
                if output_format == ImageFormat.JPEG:
                    quality = 85 if mode == OptimizationMode.QUALITY else 75
                    save_kwargs = {'format': 'JPEG', 'quality': quality, 'optimize': True}
                    
                elif output_format == ImageFormat.PNG:
                    save_kwargs = {'format': 'PNG', 'optimize': True}
                    
                elif output_format == ImageFormat.WEBP:
                    quality = 85 if mode == OptimizationMode.QUALITY else 80
                    save_kwargs = {'format': 'WEBP', 'quality': quality, 'optimize': True}
                    
                elif output_format == ImageFormat.TIFF:
                    save_kwargs = {'format': 'TIFF', 'compression': 'lzw'}
                    
                else:
                    save_kwargs = {'format': output_format.value.upper()}
                
                img.save(tmp_file, **save_kwargs)
                tmp_file.flush()
                
                with open(tmp_file.name, 'rb') as f:
                    output_bytes = f.read()
                
                # If target size specified, adjust quality
                if target_size and len(output_bytes) > target_size:
                    output_bytes = await self._adjust_for_target_size(
                        img, output_format, target_size
                    )
                
                return output_bytes
                
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            raise
    
    async def _adjust_for_target_size(self,
                                    img: Image.Image,
                                    output_format: ImageFormat,
                                    target_size: int) -> bytes:
        """Adjust image quality to meet target file size"""
        try:
            quality = 85
            
            while quality > 10:
                with tempfile.NamedTemporaryFile() as tmp_file:
                    
                    if output_format in [ImageFormat.JPEG, ImageFormat.WEBP]:
                        img.save(tmp_file, format=output_format.value.upper(), 
                               quality=quality, optimize=True)
                    else:
                        img.save(tmp_file, format=output_format.value.upper())
                    
                    tmp_file.flush()
                    
                    with open(tmp_file.name, 'rb') as f:
                        output_bytes = f.read()
                    
                    if len(output_bytes) <= target_size:
                        return output_bytes
                
                quality -= 5
            
            # If still too large, resize image
            scale_factor = 0.9
            resized_img = img.resize(
                (int(img.width * scale_factor), int(img.height * scale_factor)),
                Image.Resampling.LANCZOS
            )
            
            return await self._adjust_for_target_size(resized_img, output_format, target_size)
            
        except Exception as e:
            logger.error(f"Size adjustment failed: {e}")
            raise
    
    async def _calculate_image_metrics(self, img: Image.Image, file_size: int) -> ImageMetrics:
        """Calculate comprehensive image metrics"""
        try:
            # Basic properties
            width, height = img.size
            channels = len(img.getbands())
            bit_depth = 8  # Most common, would need more analysis for actual bit depth
            format_name = img.format or "unknown"
            has_transparency = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
            
            # Convert to numpy for analysis
            img_array = np.array(img)
            
            # Calculate quality metrics
            sharpness = await self._calculate_sharpness(img_array)
            brightness = np.mean(img_array) / 255.0
            contrast = np.std(img_array) / 255.0
            
            # Saturation (for color images)
            if len(img_array.shape) == 3:
                hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV) if IMAGE_AVAILABLE else img_array
                saturation = np.mean(hsv[:, :, 1]) / 255.0 if IMAGE_AVAILABLE else 0.5
            else:
                saturation = 0.0
            
            # Quality score
            quality_score = await self._calculate_quality_score(
                width, height, sharpness, contrast, file_size
            )
            
            return ImageMetrics(
                width=width,
                height=height,
                channels=channels,
                bit_depth=bit_depth,
                file_size=file_size,
                format=format_name,
                color_space=img.mode,
                has_transparency=has_transparency,
                compression_ratio=1.0,  # Would need original uncompressed size
                quality_score=quality_score,
                sharpness=sharpness,
                brightness=brightness,
                contrast=contrast,
                saturation=saturation
            )
            
        except Exception as e:
            logger.error(f"Metrics calculation failed: {e}")
            return ImageMetrics(0, 0, 0, 0, 0, "", "", False, 0, 0, 0, 0, 0, 0)
    
    async def _calculate_sharpness(self, img_array: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance"""
        try:
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY) if IMAGE_AVAILABLE else np.mean(img_array, axis=2)
            else:
                gray = img_array
            
            if IMAGE_AVAILABLE:
                return cv2.Laplacian(gray, cv2.CV_64F).var()
            else:
                # Simple gradient-based sharpness
                grad_x = np.gradient(gray, axis=1)
                grad_y = np.gradient(gray, axis=0)
                return np.mean(grad_x**2 + grad_y**2)
            
        except Exception as e:
            logger.error(f"Sharpness calculation failed: {e}")
            return 0.0
    
    async def _calculate_quality_score(self,
                                     width: int,
                                     height: int,
                                     sharpness: float,
                                     contrast: float,
                                     file_size: int) -> float:
        """Calculate overall image quality score"""
        score = 50  # Base score
        
        # Resolution score
        megapixels = (width * height) / 1000000
        if megapixels >= 24:  # 6K+
            score += 25
        elif megapixels >= 8:  # 4K
            score += 20
        elif megapixels >= 2:  # 1080p
            score += 15
        elif megapixels >= 1:  # 720p
            score += 10
        
        # Sharpness score
        if sharpness > 1000:
            score += 15
        elif sharpness > 500:
            score += 10
        elif sharpness > 100:
            score += 5
        
        # Contrast score
        if contrast > 0.3:
            score += 10
        elif contrast > 0.2:
            score += 5
        
        return min(score, 100)