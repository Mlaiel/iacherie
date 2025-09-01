"""Image Transformer - Professional image processing for IA Influencer Agent Platform
===================================================================================

Advanced image transformation, conversion, and enhancement capabilities
for creators' image content workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
Warning: Unauthorized use strictly prohibited
"""

import asyncio
import logging
import os
import tempfile
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
import time
import numpy as np

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ExifTags
    import cv2
    import imageio
    from skimage import restoration, filters, exposure
    IMAGE_LIBS_AVAILABLE = True
except ImportError:
    IMAGE_LIBS_AVAILABLE = False
    logging.warning("Image processing libraries not available. Some features may be limited.")

logger = logging.getLogger(__name__)


class ImageFormat(Enum):
    """Supported image formats."""

    JPEG = "jpg"
    PNG = "png"
    WEBP = "webp"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    SVG = "svg"
    ICO = "ico"


class ImageQuality(Enum):
    """Image quality presets."""

    LOW = "low"          # Compressed, small file size
    MEDIUM = "medium"    # Balanced quality/size
    HIGH = "high"        # High quality, larger size
    LOSSLESS = "lossless"  # No compression
    CUSTOM = "custom"    # Custom settings


class ColorSpace(Enum):
    """Color space options."""

    RGB = "RGB"
    RGBA = "RGBA"
    GRAYSCALE = "L"
    CMYK = "CMYK"
    HSV = "HSV"
    LAB = "LAB"


@dataclass
class ImageSettings:
    """Image processing settings."""
    format: ImageFormat = ImageFormat.JPEG
    quality: ImageQuality = ImageQuality.HIGH
    width: Optional[int] = None
    height: Optional[int] = None
    maintain_aspect: bool = True
    color_space: Optional[ColorSpace] = None
    compression_level: Optional[int] = None
    progressive: bool = False
    optimize: bool = True
    dpi: Optional[Tuple[int, int]] = None
    
    # Enhancement options
    enhance_brightness: Optional[float] = None
    enhance_contrast: Optional[float] = None
    enhance_saturation: Optional[float] = None
    enhance_sharpness: Optional[float] = None
    noise_reduction: bool = False
    auto_enhance: bool = False
    
    # Filters
    blur: Optional[float] = None
    sharpen: bool = False
    edge_enhance: bool = False
    emboss: bool = False
    find_edges: bool = False
    
    # Watermark
    watermark: Optional[str] = None
    watermark_position: str = "bottom-right"
    watermark_opacity: float = 0.5


@dataclass
class ImageMetadata:
    """Image file metadata."""
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    mode: Optional[str] = None
    size: Optional[int] = None
    dpi: Optional[Tuple[int, int]] = None
    has_transparency: bool = False
    color_profile: Optional[str] = None
    creation_date: Optional[str] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    exposure_time: Optional[str] = None
    f_number: Optional[str] = None
    iso_speed: Optional[str] = None
    focal_length: Optional[str] = None
    flash: Optional[str] = None
    gps_info: Optional[Dict[str, Any]] = None


class ImageTransformer:
    """
    Professional image transformation engine for the IA Influencer Agent Platform.
    
    Provides advanced image processing, conversion, and enhancement capabilities
    optimized for creator content workflows.
    """
    
    def __init__(
        self,
        enable_gpu: bool = True,
        config: Optional[Dict[str, Any]] = None,
        temp_dir: Optional[str] = None
    ):
        """
        Initialize image transformer.
        
        Args:
            enable_gpu: Enable GPU acceleration if available
            config: Configuration options
            temp_dir: Temporary directory for processing
        """
        self.enable_gpu = enable_gpu
        self.config = config or {}
        self.temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir()) / "image_transform"
        
        # Create temp directory
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Quality presets
        self.quality_presets = {
            ImageQuality.LOW: {"compression": 60, "optimize": True},
            ImageQuality.MEDIUM: {"compression": 80, "optimize": True},
            ImageQuality.HIGH: {"compression": 95, "optimize": True},
            ImageQuality.LOSSLESS: {"compression": 100, "optimize": False}
        }
        
        # Format settings
        self.format_settings = {
            ImageFormat.JPEG: {"quality_param": "quality", "supports_transparency": False},
            ImageFormat.PNG: {"quality_param": "compress_level", "supports_transparency": True},
            ImageFormat.WEBP: {"quality_param": "quality", "supports_transparency": True},
            ImageFormat.GIF: {"quality_param": None, "supports_transparency": True},
            ImageFormat.TIFF: {"quality_param": "compression", "supports_transparency": True},
        }
        
        logger.info(f"ImageTransformer initialized (GPU: {enable_gpu})")
    
    async def transform(self, request) -> Any:
        """
        Transform image based on request configuration.
        
        Args:
            request: Transformation request with image settings
            
        Returns:
            TransformationResult with processing metrics
        """
        start_time = time.time()
        
        try:
            if not IMAGE_LIBS_AVAILABLE:
                raise RuntimeError("Image processing libraries not available")
            
            # Parse request
            input_path = Path(request.input_path)
            settings = self._parse_image_settings(request)
            
            # Generate output path
            output_path = self._generate_output_path(input_path, settings, request.output_path)
            
            # Get input metadata
            input_metadata = await self.get_metadata(str(input_path))
            input_size = input_path.stat().st_size
            
            # Load image
            image = Image.open(str(input_path))
            
            # Apply transformations
            processed_image = await self._process_image(image, settings)
            
            # Apply enhancements if requested
            if request.enhance_quality:
                processed_image = await self._enhance_image(processed_image, settings)
            
            # Save processed image
            await self._save_image(processed_image, output_path, settings)
            
            # Get output metadata
            output_metadata = await self.get_metadata(str(output_path))
            output_size = output_path.stat().st_size
            
            # Calculate metrics
            compression_ratio = (input_size - output_size) / input_size if input_size > 0 else 0.0
            quality_score = await self._calculate_quality_score(str(input_path), str(output_path))
            
            return type('TransformationResult', (), {
                'success': True,
                'output_path': str(output_path),
                'input_size': input_size,
                'output_size': output_size,
                'compression_ratio': compression_ratio,
                'quality_score': quality_score,
                'metadata': {
                    'input': input_metadata.__dict__,
                    'output': output_metadata.__dict__,
                    'settings': settings.__dict__
                },
                'processing_time': time.time() - start_time
            })()
            
        except Exception as e:
            logger.error(f"Image transformation failed: {str(e)}")
            return type('TransformationResult', (), {
                'success': False,
                'error_message': str(e),
                'processing_time': time.time() - start_time
            })()
    
    async def convert(
        self,
        input_path: str,
        output_path: str,
        format: Union[str, ImageFormat] = ImageFormat.JPEG,
        quality: Union[str, ImageQuality] = ImageQuality.HIGH,
        **kwargs
    ) -> bool:
        """
        Convert image file to specified format and quality.
        
        Args:
            input_path: Input image file path
            output_path: Output image file path
            format: Target image format
            quality: Output quality level
            **kwargs: Additional settings
            
        Returns:
            Success status
        """
        if not IMAGE_LIBS_AVAILABLE:
            logger.error("Image processing libraries not available")
            return False
        
        settings = ImageSettings(
            format=format if isinstance(format, ImageFormat) else ImageFormat(format),
            quality=quality if isinstance(quality, ImageQuality) else ImageQuality(quality),
            **kwargs
        )
        
        try:
            # Load and process image
            image = Image.open(input_path)
            processed_image = await self._process_image(image, settings)
            
            # Save image
            await self._save_image(processed_image, Path(output_path), settings)
            return True
            
        except Exception as e:
            logger.error(f"Image conversion failed: {str(e)}")
            return False
    
    async def enhance(
        self,
        input_path: str,
        output_path: str,
        enhancement_options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Enhance image quality using AI and image processing.
        
        Args:
            input_path: Input image file path
            output_path: Output image file path
            enhancement_options: Enhancement configuration
            
        Returns:
            Success status
        """
        if not IMAGE_LIBS_AVAILABLE:
            logger.error("Image processing libraries not available")
            return False
        
        try:
            options = enhancement_options or {}
            
            # Load image
            image = Image.open(input_path)
            
            # Apply enhancements
            enhanced_image = await self._enhance_image(image, ImageSettings(**options))
            
            # Save enhanced image
            enhanced_image.save(output_path, quality=95, optimize=True)
            return True
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {str(e)}")
            return False
    
    async def resize(
        self,
        input_path: str,
        output_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect: bool = True
    ) -> bool:
        """
        Resize image to specified dimensions.
        
        Args:
            input_path: Input image file path
            output_path: Output image file path
            width: Target width
            height: Target height
            maintain_aspect: Maintain aspect ratio
            
        Returns:
            Success status
        """
        if not IMAGE_LIBS_AVAILABLE:
            return False
        
        try:
            image = Image.open(input_path)
            
            if maintain_aspect and width and height:
                # Calculate size maintaining aspect ratio
                image.thumbnail((width, height), Image.Resampling.LANCZOS)
                resized_image = image
            elif width and height:
                # Exact resize
                resized_image = image.resize((width, height), Image.Resampling.LANCZOS)
            elif width:
                # Resize by width
                ratio = width / image.width
                new_height = int(image.height * ratio)
                resized_image = image.resize((width, new_height), Image.Resampling.LANCZOS)
            elif height:
                # Resize by height
                ratio = height / image.height
                new_width = int(image.width * ratio)
                resized_image = image.resize((new_width, height), Image.Resampling.LANCZOS)
            else:
                resized_image = image
            
            resized_image.save(output_path, quality=95, optimize=True)
            return True
            
        except Exception as e:
            logger.error(f"Image resize failed: {str(e)}")
            return False
    
    async def get_metadata(self, file_path: str) -> ImageMetadata:
        """
        Extract comprehensive image metadata.
        
        Args:
            file_path: Image file path
            
        Returns:
            ImageMetadata object
        """
        try:
            metadata = ImageMetadata()
            file_path_obj = Path(file_path)
            
            if not file_path_obj.exists():
                return metadata
            
            metadata.size = file_path_obj.stat().st_size
            
            if IMAGE_LIBS_AVAILABLE:
                try:
                    with Image.open(file_path) as image:
                        metadata.width = image.width
                        metadata.height = image.height
                        metadata.format = image.format
                        metadata.mode = image.mode
                        metadata.has_transparency = image.mode in ('RGBA', 'LA') or 'transparency' in image.info
                        
                        # DPI information
                        if hasattr(image, 'info') and 'dpi' in image.info:
                            metadata.dpi = image.info['dpi']
                        
                        # EXIF data
                        if hasattr(image, '_getexif') and image._getexif():
                            exif = image._getexif()
                            
                            for tag_id, value in exif.items():
                                tag = ExifTags.TAGS.get(tag_id, tag_id)
                                
                                if tag == 'Make':
                                    metadata.camera_make = str(value)
                                elif tag == 'Model':
                                    metadata.camera_model = str(value)
                                elif tag == 'DateTime':
                                    metadata.creation_date = str(value)
                                elif tag == 'ExposureTime':
                                    metadata.exposure_time = str(value)
                                elif tag == 'FNumber':
                                    metadata.f_number = str(value)
                                elif tag == 'ISOSpeedRatings':
                                    metadata.iso_speed = str(value)
                                elif tag == 'FocalLength':
                                    metadata.focal_length = str(value)
                                elif tag == 'Flash':
                                    metadata.flash = str(value)
                                elif tag == 'GPSInfo':
                                    metadata.gps_info = dict(value) if isinstance(value, dict) else None
                        
                        # Color profile
                        if hasattr(image, 'info') and 'icc_profile' in image.info:
                            metadata.color_profile = "ICC Profile Present"
                    
                except Exception as e:
                    logger.warning(f"Could not extract image metadata: {e}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            return ImageMetadata()
    
    async def _process_image(self, image: Image.Image, settings: ImageSettings) -> Image.Image:
        """Process image according to settings."""
        processed = image.copy()
        
        try:
            # Convert color space
            if settings.color_space and settings.color_space != ColorSpace(processed.mode):
                if settings.color_space == ColorSpace.GRAYSCALE:
                    processed = processed.convert('L')
                elif settings.color_space == ColorSpace.RGB:
                    processed = processed.convert('RGB')
                elif settings.color_space == ColorSpace.RGBA:
                    processed = processed.convert('RGBA')
            
            # Resize if specified
            if settings.width or settings.height:
                processed = await self._resize_image(processed, settings)
            
            # Apply filters
            processed = await self._apply_filters(processed, settings)
            
            # Apply enhancements
            if any([settings.enhance_brightness, settings.enhance_contrast, 
                   settings.enhance_saturation, settings.enhance_sharpness]):
                processed = await self._apply_enhancements(processed, settings)
            
            # Add watermark
            if settings.watermark:
                processed = await self._add_watermark(processed, settings)
            
            return processed
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return image
    
    async def _resize_image(self, image: Image.Image, settings: ImageSettings) -> Image.Image:
        """Resize image according to settings."""
        try:
            width = settings.width
            height = settings.height
            
            if settings.maintain_aspect:
                if width and height:
                    # Calculate size maintaining aspect ratio
                    image.thumbnail((width, height), Image.Resampling.LANCZOS)
                    return image
                elif width:
                    # Resize by width
                    ratio = width / image.width
                    new_height = int(image.height * ratio)
                    return image.resize((width, new_height), Image.Resampling.LANCZOS)
                elif height:
                    # Resize by height
                    ratio = height / image.height
                    new_width = int(image.width * ratio)
                    return image.resize((new_width, height), Image.Resampling.LANCZOS)
            else:
                # Exact resize
                if width and height:
                    return image.resize((width, height), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Image resize failed: {str(e)}")
            return image
    
    async def _apply_filters(self, image: Image.Image, settings: ImageSettings) -> Image.Image:
        """Apply image filters."""
        try:
            filtered = image
            
            if settings.blur:
                filtered = filtered.filter(ImageFilter.GaussianBlur(radius=settings.blur))
            
            if settings.sharpen:
                filtered = filtered.filter(ImageFilter.SHARPEN)
            
            if settings.edge_enhance:
                filtered = filtered.filter(ImageFilter.EDGE_ENHANCE)
            
            if settings.emboss:
                filtered = filtered.filter(ImageFilter.EMBOSS)
            
            if settings.find_edges:
                filtered = filtered.filter(ImageFilter.FIND_EDGES)
            
            return filtered
            
        except Exception as e:
            logger.error(f"Filter application failed: {str(e)}")
            return image
    
    async def _apply_enhancements(self, image: Image.Image, settings: ImageSettings) -> Image.Image:
        """Apply image enhancements."""
        try:
            enhanced = image
            
            if settings.enhance_brightness:
                enhancer = ImageEnhance.Brightness(enhanced)
                enhanced = enhancer.enhance(settings.enhance_brightness)
            
            if settings.enhance_contrast:
                enhancer = ImageEnhance.Contrast(enhanced)
                enhanced = enhancer.enhance(settings.enhance_contrast)
            
            if settings.enhance_saturation:
                enhancer = ImageEnhance.Color(enhanced)
                enhanced = enhancer.enhance(settings.enhance_saturation)
            
            if settings.enhance_sharpness:
                enhancer = ImageEnhance.Sharpness(enhanced)
                enhanced = enhancer.enhance(settings.enhance_sharpness)
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Enhancement application failed: {str(e)}")
            return image
    
    async def _enhance_image(self, image: Image.Image, settings: ImageSettings) -> Image.Image:
        """Advanced image enhancement using AI and image processing."""
        try:
            enhanced = image.copy()
            
            # Auto enhancement
            if settings.auto_enhance:
                enhanced = ImageOps.autocontrast(enhanced)
                enhanced = ImageOps.equalize(enhanced)
            
            # Noise reduction
            if settings.noise_reduction:
                # Convert to numpy array for advanced processing
                img_array = np.array(enhanced)
                
                if len(img_array.shape) == 3:  # Color image
                    # Apply denoising
                    denoised = restoration.denoise_tv_chambolle(
                        img_array, weight=0.1, channel_axis=-1
                    )
                    denoised = (denoised * 255).astype(np.uint8)
                    enhanced = Image.fromarray(denoised)
                elif len(img_array.shape) == 2:  # Grayscale
                    denoised = restoration.denoise_tv_chambolle(img_array, weight=0.1)
                    denoised = (denoised * 255).astype(np.uint8)
                    enhanced = Image.fromarray(denoised, mode='L')
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Advanced enhancement failed: {str(e)}")
            return image
    
    async def _add_watermark(self, image: Image.Image, settings: ImageSettings) -> Image.Image:
        """Add watermark to image."""
        try:
            from PIL import ImageDraw, ImageFont
            
            # Create a copy for watermarking
            watermarked = image.copy()
            
            # Create drawing context
            draw = ImageDraw.Draw(watermarked)
            
            # Try to use a nice font
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            # Get text size
            bbox = draw.textbbox((0, 0), settings.watermark, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position
            margin = 10
            if settings.watermark_position == "top-left":
                position = (margin, margin)
            elif settings.watermark_position == "top-right":
                position = (image.width - text_width - margin, margin)
            elif settings.watermark_position == "bottom-left":
                position = (margin, image.height - text_height - margin)
            else:  # bottom-right (default)
                position = (image.width - text_width - margin, image.height - text_height - margin)
            
            # Calculate color with opacity
            opacity = int(255 * settings.watermark_opacity)
            color = (255, 255, 255, opacity) if image.mode == 'RGBA' else (255, 255, 255)
            
            # Draw watermark
            if image.mode == 'RGBA':
                # Create a transparent overlay
                overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.text(position, settings.watermark, font=font, fill=color)
                watermarked = Image.alpha_composite(watermarked.convert('RGBA'), overlay)
            else:
                draw.text(position, settings.watermark, font=font, fill=color)
            
            return watermarked
            
        except Exception as e:
            logger.error(f"Watermark application failed: {str(e)}")
            return image
    
    async def _save_image(self, image: Image.Image, output_path: Path, settings: ImageSettings) -> None:
        """Save image with format-specific settings."""
        try:
            # Prepare save parameters
            save_kwargs = {}
            
            # Get quality settings
            quality_settings = self.quality_presets.get(settings.quality, {})
            format_info = self.format_settings.get(settings.format, {})
            
            # Handle transparency for formats that don't support it
            if not format_info.get("supports_transparency", False) and image.mode in ('RGBA', 'LA'):
                # Convert to RGB with white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Format-specific settings
            if settings.format == ImageFormat.JPEG:
                save_kwargs['format'] = 'JPEG'
                save_kwargs['quality'] = settings.compression_level or quality_settings.get('compression', 95)
                save_kwargs['optimize'] = settings.optimize
                save_kwargs['progressive'] = settings.progressive
                
            elif settings.format == ImageFormat.PNG:
                save_kwargs['format'] = 'PNG'
                save_kwargs['optimize'] = settings.optimize
                if settings.compression_level:
                    save_kwargs['compress_level'] = min(9, max(0, settings.compression_level // 10))
                
            elif settings.format == ImageFormat.WEBP:
                save_kwargs['format'] = 'WEBP'
                save_kwargs['quality'] = settings.compression_level or quality_settings.get('compression', 95)
                save_kwargs['optimize'] = settings.optimize
                
            elif settings.format == ImageFormat.GIF:
                save_kwargs['format'] = 'GIF'
                save_kwargs['optimize'] = settings.optimize
                
            elif settings.format == ImageFormat.TIFF:
                save_kwargs['format'] = 'TIFF'
                save_kwargs['compression'] = 'lzw'
            
            # Set DPI if specified
            if settings.dpi:
                save_kwargs['dpi'] = settings.dpi
            
            # Save image
            image.save(str(output_path), **save_kwargs)
            
        except Exception as e:
            logger.error(f"Image save failed: {str(e)}")
            raise
    
    async def _calculate_quality_score(self, input_path: str, output_path: str) -> Optional[float]:
        """Calculate image quality score comparing input and output."""
        try:
            if not IMAGE_LIBS_AVAILABLE:
                return None
            
            # Load images
            original = cv2.imread(input_path)
            processed = cv2.imread(output_path)
            
            if original is None or processed is None:
                return None
            
            # Resize to same dimensions if needed
            if original.shape != processed.shape:
                processed = cv2.resize(processed, (original.shape[1], original.shape[0]))
            
            # Calculate SSIM (Structural Similarity Index)
            from skimage.metrics import structural_similarity as ssim
            
            # Convert to grayscale for SSIM calculation
            original_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
            processed_gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            
            ssim_score = ssim(original_gray, processed_gray)
            
            return ssim_score * 100  # Convert to percentage
            
        except Exception as e:
            logger.error(f"Quality score calculation failed: {str(e)}")
            return None
    
    def _parse_image_settings(self, request) -> ImageSettings:
        """Parse transformation request into image settings."""
        settings = ImageSettings()
        
        if hasattr(request, 'target_format') and request.target_format:
            settings.format = ImageFormat(request.target_format)
        
        if hasattr(request, 'quality') and request.quality:
            if hasattr(request.quality, 'value'):
                settings.quality = ImageQuality(request.quality.value)
            else:
                settings.quality = ImageQuality(request.quality)
        
        if hasattr(request, 'options') and request.options:
            options = request.options
            settings.width = options.get('width')
            settings.height = options.get('height')
            settings.maintain_aspect = options.get('maintain_aspect', True)
            settings.compression_level = options.get('compression_level')
            settings.optimize = options.get('optimize', True)
            settings.progressive = options.get('progressive', False)
            
            # Enhancement options
            settings.enhance_brightness = options.get('enhance_brightness')
            settings.enhance_contrast = options.get('enhance_contrast')
            settings.enhance_saturation = options.get('enhance_saturation')
            settings.enhance_sharpness = options.get('enhance_sharpness')
            settings.noise_reduction = options.get('noise_reduction', False)
            settings.auto_enhance = options.get('auto_enhance', False)
            
            # Filter options
            settings.blur = options.get('blur')
            settings.sharpen = options.get('sharpen', False)
            settings.edge_enhance = options.get('edge_enhance', False)
            
            # Watermark
            settings.watermark = options.get('watermark')
            settings.watermark_position = options.get('watermark_position', 'bottom-right')
            settings.watermark_opacity = options.get('watermark_opacity', 0.5)
            
            if options.get('color_space'):
                settings.color_space = ColorSpace(options['color_space'])
        
        return settings
    
    def _generate_output_path(
        self,
        input_path: Path,
        settings: ImageSettings,
        requested_output: Optional[str] = None
    ) -> Path:
        """
Generate output file path."""
        if requested_output:
            return Path(requested_output)
        
        # Generate based on input and settings
        output_name = f"{input_path.stem}_{settings.quality.value}.{settings.format.value}"
        return input_path.parent / output_name
    
    async def cleanup(self):
        """Cleanup temporary files and resources."""
        try:
            # Clean temp directory
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            logger.info("ImageTransformer cleanup completed")
            
        except Exception as e:
            logger.error(f"ImageTransformer cleanup failed: {str(e)}")


class ImageConverter:
    """Simplified image converter interface."""
    
    def __init__(self, transformer: Optional[ImageTransformer] = None):
        self.transformer = transformer or ImageTransformer()
    
    async def convert(
        self,
        input_path: str,
        output_path: str,
        format: str = "jpg",
        quality: str = "high"
    ) -> bool:
        """Convert image file."""
        return await self.transformer.convert(input_path, output_path, format, quality)


class ImageEnhancer:
    """
Simplified image enhancer interface."""
    
    def __init__(self, transformer: Optional[ImageTransformer] = None):
        self.transformer = transformer or ImageTransformer()
    
    async def enhance(
        self,
        input_path: str,
        output_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
Enhance image quality."""
        return await self.transformer.enhance(input_path, output_path, options)
