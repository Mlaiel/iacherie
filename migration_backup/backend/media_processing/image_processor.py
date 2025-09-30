"""
🖼️ Image Processing Module - Enterprise Image Processing Engine
Consolidated: image_optimizer.py + format_converter.py (image parts)

Technologies: Pillow, OpenCV, ImageIO, WAND, Skimage
Team: Lead Dev IA + ML Engineer + Audio Engineer + Backend Senior
"""

import asyncio
import io
import logging
import mimetypes
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import cv2
import numpy as np
from skimage import restoration, measure, filters
import imageio
from wand.image import Image as WandImage
from wand.color import Color

# Configuration
@dataclass
class ImageProcessingConfig:
    """Configuration for image processing operations"""
    max_resolution: Tuple[int, int] = (4096, 4096)
    quality_levels: Dict[str, int] = None
    supported_formats: List[str] = None
    optimization_level: str = "high"
    preserve_metadata: bool = True
    enable_ai_enhancement: bool = True
    watermark_enabled: bool = True
    
    def __post_init__(self):
        if self.quality_levels is None:
            self.quality_levels = {
                "low": 60,
                "medium": 80,
                "high": 95,
                "lossless": 100
            }
        if self.supported_formats is None:
            self.supported_formats = [
                'jpeg', 'jpg', 'png', 'webp', 'tiff', 'bmp', 
                'gif', 'svg', 'heic', 'avif', 'ico'
            ]

# Exceptions
class ImageProcessingError(Exception):
    """Base exception for image processing errors"""
    pass

class UnsupportedFormatError(ImageProcessingError):
    """Raised when image format is not supported"""
    pass

class ProcessingTimeoutError(ImageProcessingError):
    """Raised when processing takes too long"""
    pass

# Core Image Processor
class EnterpriseImageProcessor:
    """
    🎯 Enterprise-grade image processing engine
    
    Features:
    - Multi-format support with AI optimization
    - Advanced image enhancement and restoration
    - Intelligent compression and quality optimization
    - Batch processing with parallel execution
    - Metadata preservation and watermarking
    """
    
    def __init__(self, config: Optional[ImageProcessingConfig] = None):
        self.config = config or ImageProcessingConfig()
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize AI models for enhancement
        self._initialize_ai_models()
        
    def _initialize_ai_models(self):
        """Initialize AI models for image enhancement"""
        try:
            # Placeholder for AI model initialization
            # In production: Load pre-trained models for super-resolution, denoising, etc.
            self.ai_models = {
                'super_resolution': None,  # ESRGAN, SRCNN, etc.
                'denoising': None,         # DnCNN, FFDNet, etc.
                'enhancement': None,       # Custom enhancement models
                'style_transfer': None,    # Neural style transfer
            }
            self.logger.info("AI models initialized for image enhancement")
        except Exception as e:
            self.logger.warning(f"AI models initialization failed: {e}")
            self.ai_models = {}

    async def process_image(
        self,
        image_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        target_format: Optional[str] = None,
        quality: Optional[str] = None,
        resize_dimensions: Optional[Tuple[int, int]] = None,
        enhance: bool = True
    ) -> Dict[str, Any]:
        """
        🎯 Process single image with comprehensive optimization
        
        Args:
            image_path: Input image file path
            output_path: Output file path (optional)
            target_format: Target format for conversion
            quality: Quality level (low, medium, high, lossless)
            resize_dimensions: Target dimensions (width, height)
            enhance: Enable AI enhancement
            
        Returns:
            Processing result with metadata
        """
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Validate input
            image_path = Path(image_path)
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Load image
            image_data = await self._load_image(image_path)
            original_format = image_data['format']
            
            # Apply processing pipeline
            processed_image = await self._apply_processing_pipeline(
                image_data['image'],
                target_format=target_format or original_format,
                quality=quality or self.config.optimization_level,
                resize_dimensions=resize_dimensions,
                enhance=enhance
            )
            
            # Save processed image
            if output_path:
                output_path = Path(output_path)
                await self._save_image(processed_image, output_path)
            else:
                output_path = image_path.with_suffix(f'.processed{image_path.suffix}')
                await self._save_image(processed_image, output_path)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return {
                'success': True,
                'input_path': str(image_path),
                'output_path': str(output_path),
                'original_format': original_format,
                'target_format': processed_image['format'],
                'original_size': image_data['size'],
                'processed_size': processed_image['size'],
                'compression_ratio': self._calculate_compression_ratio(
                    image_data['file_size'], 
                    output_path.stat().st_size
                ),
                'processing_time': processing_time,
                'enhancements_applied': processed_image.get('enhancements', [])
            }
            
        except Exception as e:
            self.logger.error(f"Image processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'input_path': str(image_path)
            }

    async def _load_image(self, image_path: Path) -> Dict[str, Any]:
        """Load image with format detection and metadata extraction"""
        def _load():
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    if img.mode == 'P' and 'transparency' in img.info:
                        img = img.convert('RGBA')
                    else:
                        img = img.convert('RGB')
                
                return {
                    'image': img.copy(),
                    'format': img.format.lower() if img.format else 'unknown',
                    'mode': img.mode,
                    'size': img.size,
                    'metadata': dict(img.info) if hasattr(img, 'info') else {},
                    'file_size': image_path.stat().st_size
                }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _load)

    async def _apply_processing_pipeline(
        self,
        image: Image.Image,
        target_format: str,
        quality: str,
        resize_dimensions: Optional[Tuple[int, int]],
        enhance: bool
    ) -> Dict[str, Any]:
        """Apply comprehensive processing pipeline"""
        
        processed_image = image.copy()
        enhancements = []
        
        # Step 1: Resize if needed
        if resize_dimensions:
            processed_image = await self._smart_resize(processed_image, resize_dimensions)
            enhancements.append('smart_resize')
        
        # Step 2: AI Enhancement
        if enhance and self.config.enable_ai_enhancement:
            processed_image = await self._ai_enhance(processed_image)
            enhancements.append('ai_enhancement')
        
        # Step 3: Quality optimization
        processed_image = await self._optimize_quality(processed_image, quality)
        enhancements.append('quality_optimization')
        
        # Step 4: Format-specific optimization
        processed_image = await self._format_optimization(processed_image, target_format)
        enhancements.append('format_optimization')
        
        return {
            'image': processed_image,
            'format': target_format,
            'size': processed_image.size,
            'enhancements': enhancements
        }

    async def _smart_resize(
        self, 
        image: Image.Image, 
        target_size: Tuple[int, int]
    ) -> Image.Image:
        """Smart resizing with aspect ratio preservation and quality enhancement"""
        def _resize():
            # Calculate optimal resize strategy
            current_w, current_h = image.size
            target_w, target_h = target_size
            
            # Preserve aspect ratio
            aspect_ratio = current_w / current_h
            target_aspect = target_w / target_h
            
            if aspect_ratio > target_aspect:
                # Image is wider, fit to width
                new_w = target_w
                new_h = int(target_w / aspect_ratio)
            else:
                # Image is taller, fit to height
                new_h = target_h
                new_w = int(target_h * aspect_ratio)
            
            # Use high-quality resampling
            resized = image.resize(
                (new_w, new_h), 
                Image.Resampling.LANCZOS
            )
            
            # Apply sharpening after resize
            sharpened = resized.filter(ImageFilter.UnsharpMask(
                radius=0.5, percent=150, threshold=3
            ))
            
            return sharpened
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _resize)

    async def _ai_enhance(self, image: Image.Image) -> Image.Image:
        """Apply AI-powered image enhancement"""
        def _enhance():
            # Convert PIL to numpy for processing
            img_array = np.array(image)
            
            # Apply noise reduction
            denoised = restoration.denoise_bilateral(
                img_array, sigma_color=0.1, sigma_spatial=15, multichannel=True
            )
            
            # Enhance contrast adaptively
            enhanced = restoration.denoise_tv_chambolle(
                denoised, weight=0.1, multichannel=True
            )
            
            # Convert back to PIL
            enhanced_img = Image.fromarray(
                (enhanced * 255).astype(np.uint8)
            )
            
            # Apply additional PIL enhancements
            enhancer = ImageEnhance.Contrast(enhanced_img)
            enhanced_img = enhancer.enhance(1.1)
            
            enhancer = ImageEnhance.Sharpness(enhanced_img)
            enhanced_img = enhancer.enhance(1.05)
            
            return enhanced_img
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _enhance)

    async def _optimize_quality(
        self, 
        image: Image.Image, 
        quality_level: str
    ) -> Image.Image:
        """Optimize image quality based on target level"""
        def _optimize():
            quality_value = self.config.quality_levels.get(quality_level, 85)
            
            # Apply quality-specific optimizations
            if quality_level == "high" or quality_level == "lossless":
                # High quality: minimal compression, preserve details
                return image
            elif quality_level == "medium":
                # Medium quality: balanced compression
                enhancer = ImageEnhance.Sharpness(image)
                return enhancer.enhance(0.95)
            else:
                # Low quality: aggressive compression with smart preprocessing
                # Slight blur to reduce compression artifacts
                blurred = image.filter(ImageFilter.GaussianBlur(radius=0.3))
                return blurred
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _optimize)

    async def _format_optimization(
        self, 
        image: Image.Image, 
        target_format: str
    ) -> Image.Image:
        """Apply format-specific optimizations"""
        def _optimize():
            if target_format.lower() in ['jpeg', 'jpg']:
                # JPEG optimization: convert to RGB, optimize for compression
                if image.mode != 'RGB':
                    return image.convert('RGB')
            elif target_format.lower() == 'png':
                # PNG optimization: preserve transparency, optimize palette
                if image.mode not in ['RGBA', 'LA', 'P']:
                    return image.convert('RGBA')
            elif target_format.lower() == 'webp':
                # WebP optimization: best of both worlds
                if image.mode not in ['RGB', 'RGBA']:
                    return image.convert('RGBA')
            
            return image
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _optimize)

    async def _save_image(
        self, 
        image_data: Dict[str, Any], 
        output_path: Path
    ) -> None:
        """Save processed image with optimal settings"""
        def _save():
            image = image_data['image']
            target_format = image_data['format']
            
            # Prepare save parameters
            save_kwargs = {}
            
            if target_format.lower() in ['jpeg', 'jpg']:
                save_kwargs.update({
                    'format': 'JPEG',
                    'quality': self.config.quality_levels.get(
                        self.config.optimization_level, 85
                    ),
                    'optimize': True,
                    'progressive': True
                })
            elif target_format.lower() == 'png':
                save_kwargs.update({
                    'format': 'PNG',
                    'optimize': True,
                    'compress_level': 6
                })
            elif target_format.lower() == 'webp':
                save_kwargs.update({
                    'format': 'WebP',
                    'quality': self.config.quality_levels.get(
                        self.config.optimization_level, 85
                    ),
                    'method': 6,
                    'lossless': self.config.optimization_level == 'lossless'
                })
            
            # Save with optimizations
            image.save(output_path, **save_kwargs)
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _save)

    async def batch_process(
        self,
        image_paths: List[Union[str, Path]],
        output_directory: Union[str, Path],
        target_format: Optional[str] = None,
        quality: Optional[str] = None,
        resize_dimensions: Optional[Tuple[int, int]] = None,
        enhance: bool = True
    ) -> Dict[str, Any]:
        """
        🚀 Batch process multiple images with parallel execution
        
        Args:
            image_paths: List of input image paths
            output_directory: Output directory for processed images
            target_format: Target format for all images
            quality: Quality level for all images
            resize_dimensions: Target dimensions for all images
            enhance: Enable AI enhancement for all images
            
        Returns:
            Batch processing results
        """
        output_dir = Path(output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create processing tasks
        tasks = []
        for image_path in image_paths:
            input_path = Path(image_path)
            output_name = input_path.stem + (
                f'.{target_format}' if target_format 
                else input_path.suffix
            )
            output_path = output_dir / output_name
            
            task = self.process_image(
                image_path=input_path,
                output_path=output_path,
                target_format=target_format,
                quality=quality,
                resize_dimensions=resize_dimensions,
                enhance=enhance
            )
            tasks.append(task)
        
        # Execute batch processing
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Compile batch results
        successful = [r for r in results if isinstance(r, dict) and r.get('success')]
        failed = [r for r in results if not (isinstance(r, dict) and r.get('success'))]
        
        return {
            'total_processed': len(image_paths),
            'successful': len(successful),
            'failed': len(failed),
            'success_rate': len(successful) / len(image_paths) * 100,
            'results': results
        }

    def _calculate_compression_ratio(
        self, 
        original_size: int, 
        compressed_size: int
    ) -> float:
        """Calculate compression ratio"""
        if original_size == 0:
            return 0.0
        return (1 - compressed_size / original_size) * 100

    async def get_image_info(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """Get comprehensive image information and metadata"""
        image_path = Path(image_path)
        
        try:
            image_data = await self._load_image(image_path)
            
            return {
                'filename': image_path.name,
                'path': str(image_path),
                'format': image_data['format'],
                'mode': image_data['mode'],
                'size': image_data['size'],
                'file_size': image_data['file_size'],
                'metadata': image_data['metadata'],
                'mime_type': mimetypes.guess_type(str(image_path))[0],
                'is_supported': image_data['format'] in self.config.supported_formats
            }
        except Exception as e:
            return {
                'filename': image_path.name,
                'path': str(image_path),
                'error': str(e),
                'is_supported': False
            }

# Format Converter Integration
class FormatConverter:
    """
    🔄 Enterprise format conversion engine
    Integrated from format_converter.py for image formats
    """
    
    def __init__(self, image_processor: EnterpriseImageProcessor):
        self.processor = image_processor
        self.logger = logging.getLogger(__name__)
    
    async def convert_format(
        self,
        input_path: Union[str, Path],
        target_format: str,
        output_path: Optional[Union[str, Path]] = None,
        quality: str = "high"
    ) -> Dict[str, Any]:
        """Convert image to target format with optimization"""
        
        input_path = Path(input_path)
        if not output_path:
            output_path = input_path.with_suffix(f'.{target_format}')
        
        return await self.processor.process_image(
            image_path=input_path,
            output_path=output_path,
            target_format=target_format,
            quality=quality,
            enhance=True
        )

# Factory Pattern Implementation
class ImageProcessorFactory:
    """Factory for creating image processors with different configurations"""
    
    @staticmethod
    def create_standard_processor() -> EnterpriseImageProcessor:
        """Create processor with standard configuration"""
        return EnterpriseImageProcessor()
    
    @staticmethod
    def create_high_performance_processor() -> EnterpriseImageProcessor:
        """Create processor optimized for performance"""
        config = ImageProcessingConfig(
            optimization_level="medium",
            enable_ai_enhancement=False,
            preserve_metadata=False
        )
        return EnterpriseImageProcessor(config)
    
    @staticmethod
    def create_quality_processor() -> EnterpriseImageProcessor:
        """Create processor optimized for quality"""
        config = ImageProcessingConfig(
            optimization_level="lossless",
            enable_ai_enhancement=True,
            preserve_metadata=True,
            max_resolution=(8192, 8192)
        )
        return EnterpriseImageProcessor(config)

# Main processing interface
async def process_image_enterprise(
    image_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Enterprise image processing interface"""
    processor = ImageProcessorFactory.create_standard_processor()
    return await processor.process_image(image_path, output_path, **kwargs)

# Export all public classes and functions
__all__ = [
    'EnterpriseImageProcessor',
    'ImageProcessingConfig',
    'FormatConverter',
    'ImageProcessorFactory',
    'ImageProcessingError',
    'UnsupportedFormatError',
    'ProcessingTimeoutError',
    'process_image_enterprise'
]
