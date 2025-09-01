"""Image Processor - Advanced Image Processing Engine

Industrial-grade image processing and analysis system providing comprehensive
image manipulation, format conversion, and quality optimization capabilities.

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
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

import cv2
import numpy as np
import torch
import torchvision.transforms.functional as TF
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import rawpy
from sklearn.cluster import KMeans
import scipy.ndimage as ndi
from skimage import filters, morphology, segmentation, feature, measure

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


class ProcessingProfile(Enum):
    """Image processing quality profiles"""
    FAST = "fast"
    BALANCED = "balanced" 
    QUALITY = "quality"
    PROFESSIONAL = "professional"
    ULTRA = "ultra"


class FilterType(Enum):
    """Available image filters"""
    BLUR = "blur"
    GAUSSIAN_BLUR = "gaussian_blur"
    MOTION_BLUR = "motion_blur"
    SHARPEN = "sharpen"
    UNSHARP_MASK = "unsharp_mask"
    EDGE_ENHANCE = "edge_enhance"
    EMBOSS = "emboss"
    FIND_EDGES = "find_edges"
    SMOOTH = "smooth"
    DETAIL = "detail"
    NOISE_REDUCTION = "noise_reduction"
    BILATERAL = "bilateral"


class ColorSpace(Enum):
    """Supported color spaces"""
    RGB = "rgb"
    RGBA = "rgba" 
    GRAYSCALE = "grayscale"
    HSV = "hsv"
    LAB = "lab"
    CMYK = "cmyk"
    XYZ = "xyz"


@dataclass
class ProcessingParams:
    """Image processing parameters"""
    profile: ProcessingProfile = ProcessingProfile.BALANCED
    preserve_exif: bool = True
    auto_orient: bool = True
    color_correct: bool = True
    noise_reduction: bool = True
    sharpening: bool = True
    gamma_correction: float = 1.0
    contrast_enhancement: float = 1.0
    saturation_boost: float = 1.0
    brightness_adjustment: float = 0.0
    temperature_adjustment: float = 0.0
    tint_adjustment: float = 0.0


@dataclass
class ProcessingResult:
    """Processing operation result"""
    success: bool
    processing_time: float
    input_size: Tuple[int, int]
    output_size: Tuple[int, int]
    operations_applied: List[str] = field(default_factory=list)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ImageProcessor:
    """
    Advanced Image Processing Engine
    
    Provides comprehensive image processing capabilities including:
    - Format conversion and optimization
    - Quality enhancement and restoration
    - Advanced filtering and effects
    - Color space manipulation
    - Batch processing operations
    """
    
    def __init__(
        self,
        enable_gpu: bool = True,
        default_profile: ProcessingProfile = ProcessingProfile.BALANCED,
        cache_size: int = 100,
        max_image_size: int = 8192
    ):
        """
        Initialize Image Processor
        
        Args:
            enable_gpu: Enable GPU acceleration when available
            default_profile: Default processing quality profile
            cache_size: Maximum number of cached results
            max_image_size: Maximum supported image dimension
        """
        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.default_profile = default_profile
        self.cache_size = cache_size
        self.max_image_size = max_image_size
        
        # Processing cache for frequently accessed images
        self.processing_cache = {}
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(
            component="image_processor",
            enable_detailed_metrics=True
        )
        
        # Initialize GPU device if available
        self.device = torch.device("cuda" if self.enable_gpu else "cpu")
        
        logger.info(f"ImageProcessor initialized - GPU: {self.enable_gpu}, Device: {self.device}")

    async def process_image(
        self,
        image_input: Union[str, Path, Image.Image, np.ndarray],
        operations: List[Dict[str, Any]],
        params: Optional[ProcessingParams] = None,
        output_path: Optional[Union[str, Path]] = None
    ) -> ProcessingResult:
        """
        Process image with specified operations
        
        Args:
            image_input: Input image (path, PIL Image, or numpy array)
            operations: List of processing operations to apply
            params: Processing parameters
            output_path: Optional output file path
            
        Returns:
            ProcessingResult with operation details and metrics
        """
        start_time = time.time()
        params = params or ProcessingParams()
        
        try:
            # Load and validate image
            image = await self._load_image(image_input)
            original_size = image.size
            
            # Store original for quality comparison
            original_image = image.copy()
            
            # Apply processing operations
            processed_image = image.copy()
            applied_operations = []
            warnings = []
            
            for operation in operations:
                try:
                    processed_image = await self._apply_operation(
                        processed_image, operation, params
                    )
                    applied_operations.append(operation.get('type', 'unknown'))
                    
                except Exception as e:
                    warning_msg = f"Operation {operation.get('type')} failed: {str(e)}"
                    warnings.append(warning_msg)
                    logger.warning(warning_msg)
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                original_image, processed_image
            )
            
            # Save processed image if output path specified
            if output_path:
                await self._save_image(processed_image, output_path, params)
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                success=True,
                processing_time=processing_time,
                input_size=original_size,
                output_size=processed_image.size,
                operations_applied=applied_operations,
                quality_metrics=quality_metrics,
                warnings=warnings,
                metadata={
                    "profile": params.profile.value,
                    "gpu_used": self.enable_gpu,
                    "device": str(self.device)
                }
            )
            
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return ProcessingResult(
                success=False,
                processing_time=time.time() - start_time,
                input_size=(0, 0),
                output_size=(0, 0),
                warnings=[str(e)]
            )

    async def _load_image(self, image_input: Union[str, Path, Image.Image, np.ndarray]) -> Image.Image:
        """Load image from various input types"""
        try:
            if isinstance(image_input, Image.Image):
                image = image_input.copy()
                
            elif isinstance(image_input, np.ndarray):
                # Convert numpy array to PIL Image
                if image_input.ndim == 3:
                    if image_input.shape[2] == 3:
                        image = Image.fromarray(image_input, 'RGB')
                    elif image_input.shape[2] == 4:
                        image = Image.fromarray(image_input, 'RGBA')
                    else:
                        raise ValidationError(f"Unsupported array shape: {image_input.shape}")
                elif image_input.ndim == 2:
                    image = Image.fromarray(image_input, 'L')
                else:
                    raise ValidationError(f"Unsupported array dimensions: {image_input.ndim}")
                    
            else:
                # Load from file path
                image_path = Path(image_input)
                if not image_path.exists():
                    raise ValidationError(f"Image file not found: {image_path}")
                
                # Handle RAW files
                if image_path.suffix.lower() in ['.cr2', '.nef', '.arw', '.dng', '.raf']:
                    image = await self._load_raw_image(image_path)
                else:
                    image = Image.open(image_path)
            
            # Validate image size
            if max(image.size) > self.max_image_size:
                raise ValidationError(
                    f"Image too large: {image.size} > {self.max_image_size}px"
                )
            
            # Auto-orient if EXIF orientation data exists
            image = ImageOps.exif_transpose(image)
            
            # Ensure RGB mode for most operations
            if image.mode not in ['RGB', 'RGBA', 'L']:
                image = image.convert('RGB')
            
            return image
            
        except Exception as e:
            raise ValidationError(f"Failed to load image: {str(e)}")

    async def _load_raw_image(self, raw_path: Path) -> Image.Image:
        """Load and process RAW image files"""
        try:
            with rawpy.imread(str(raw_path)) as raw:
                # Apply basic RAW processing
                rgb = raw.postprocess(
                    use_camera_wb=True,
                    use_auto_wb=False,
                    output_color=rawpy.ColorSpace.sRGB,
                    output_bps=8,
                    no_auto_bright=False,
                    auto_bright_thr=0.01
                )
                
                # Convert to PIL Image
                image = Image.fromarray(rgb)
                return image
                
        except ImportError:
            raise ValidationError("rawpy package required for RAW file support")
        except Exception as e:
            raise ProcessingError(f"Failed to load RAW image: {str(e)}")

    async def _apply_operation(
        self, 
        image: Image.Image, 
        operation: Dict[str, Any], 
        params: ProcessingParams
    ) -> Image.Image:
        """Apply single processing operation to image"""
        operation_type = operation.get('type', '').lower()
        operation_params = operation.get('params', {})
        
        operation_handlers = {
            'resize': self._resize_image,
            'crop': self._crop_image,
            'rotate': self._rotate_image,
            'flip': self._flip_image,
            'filter': self._apply_filter,
            'adjust_brightness': self._adjust_brightness,
            'adjust_contrast': self._adjust_contrast,
            'adjust_saturation': self._adjust_saturation,
            'adjust_hue': self._adjust_hue,
            'adjust_gamma': self._adjust_gamma,
            'color_balance': self._adjust_color_balance,
            'sharpen': self._sharpen_image,
            'blur': self._blur_image,
            'noise_reduction': self._reduce_noise,
            'enhance': self._enhance_image,
            'color_correct': self._color_correct,
            'histogram_equalization': self._histogram_equalization,
            'local_adjustment': self._local_adjustment,
            'artistic_effect': self._apply_artistic_effect,
            'watermark': self._add_watermark
        }
        
        handler = operation_handlers.get(operation_type)
        if not handler:
            raise ValidationError(f"Unknown operation type: {operation_type}")
        
        return await handler(image, operation_params, params)

    async def _resize_image(
        self, 
        image: Image.Image, 
        operation_params: Dict[str, Any], 
        params: ProcessingParams
    ) -> Image.Image:
        """Resize image with advanced resampling"""
        try:
            width = operation_params.get('width')
            height = operation_params.get('height')
            method = operation_params.get('method', 'lanczos')
            maintain_aspect = operation_params.get('maintain_aspect', True)
            
            if not width and not height:
                raise ValidationError("Either width or height must be specified")
            
            # Calculate dimensions maintaining aspect ratio
            original_width, original_height = image.size
            
            if maintain_aspect:
                if width and height:
                    # Fit within specified dimensions
                    ratio = min(width / original_width, height / original_height)
                    new_width = int(original_width * ratio)
                    new_height = int(original_height * ratio)
                elif width:
                    ratio = width / original_width
                    new_width = width
                    new_height = int(original_height * ratio)
                else:  # height specified
                    ratio = height / original_height
                    new_width = int(original_width * ratio)
                    new_height = height
            else:
                new_width = width or original_width
                new_height = height or original_height
            
            # Choose resampling method
            resampling_methods = {
                'nearest': Image.Resampling.NEAREST,
                'bilinear': Image.Resampling.BILINEAR,
                'bicubic': Image.Resampling.BICUBIC,
                'lanczos': Image.Resampling.LANCZOS,
                'hamming': Image.Resampling.HAMMING,
                'box': Image.Resampling.BOX
            }
            
            resampling = resampling_methods.get(method.lower(), Image.Resampling.LANCZOS)
            
            return image.resize((new_width, new_height), resampling)
            
        except Exception as e:
            raise ProcessingError(f"Resize operation failed: {str(e)}")

    async def _crop_image(
        self, 
        image: Image.Image, 
        operation_params: Dict[str, Any], 
        params: ProcessingParams
    ) -> Image.Image:
        """Crop image with various crop modes"""
        try:
            crop_mode = operation_params.get('mode', 'box')
            
            if crop_mode == 'box':
                # Standard box crop
                left = operation_params.get('left', 0)
                top = operation_params.get('top', 0)
                right = operation_params.get('right', image.size[0])
                bottom = operation_params.get('bottom', image.size[1])
                
                return image.crop((left, top, right, bottom))
                
            elif crop_mode == 'center':
                # Center crop to specified dimensions
                width = operation_params['width']
                height = operation_params['height']
                
                img_width, img_height = image.size
                left = (img_width - width) // 2
                top = (img_height - height) // 2
                right = left + width
                bottom = top + height
                
                return image.crop((left, top, right, bottom))
                
            elif crop_mode == 'smart':
                # Smart crop using content-aware cropping
                return await self._smart_crop(image, operation_params)
                
            else:
                raise ValidationError(f"Unknown crop mode: {crop_mode}")
                
        except Exception as e:
            raise ProcessingError(f"Crop operation failed: {str(e)}")

    async def _smart_crop(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Smart crop using edge detection and interest points"""
        try:
            target_width = params['width']
            target_height = params['height']
            
            # Convert to numpy array for analysis
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Edge detection to find interesting regions
            edges = cv2.Canny(gray, 100, 200)
            
            # Find contours (interesting regions)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find the largest contour as the main subject
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Center the crop around the main subject
                center_x = x + w // 2
                center_y = y + h // 2
                
                # Calculate crop box
                left = max(0, center_x - target_width // 2)
                top = max(0, center_y - target_height // 2)
                right = min(image.size[0], left + target_width)
                bottom = min(image.size[1], top + target_height)
                
                # Adjust if crop extends beyond image
                if right - left < target_width:
                    left = max(0, right - target_width)
                if bottom - top < target_height:
                    top = max(0, bottom - target_height)
                
                return image.crop((left, top, right, bottom))
            
            # Fallback to center crop if no interesting regions found
            return await self._crop_image(image, {'mode': 'center', 'width': target_width, 'height': target_height}, None)
            
        except Exception as e:
            logger.warning(f"Smart crop failed, using center crop: {str(e)}")
            return await self._crop_image(image, {'mode': 'center', 'width': params['width'], 'height': params['height']}, None)

    async def _apply_filter(
        self, 
        image: Image.Image, 
        operation_params: Dict[str, Any], 
        params: ProcessingParams
    ) -> Image.Image:
        """Apply various image filters"""
        try:
            filter_type = operation_params.get('type', 'blur')
            intensity = operation_params.get('intensity', 1.0)
            
            filter_type_enum = FilterType(filter_type.lower())
            
            if filter_type_enum == FilterType.BLUR:
                radius = operation_params.get('radius', 2.0)
                return image.filter(ImageFilter.GaussianBlur(radius=radius * intensity))
                
            elif filter_type_enum == FilterType.GAUSSIAN_BLUR:
                radius = operation_params.get('radius', 2.0)
                return image.filter(ImageFilter.GaussianBlur(radius=radius * intensity))
                
            elif filter_type_enum == FilterType.MOTION_BLUR:
                return await self._apply_motion_blur(image, operation_params)
                
            elif filter_type_enum == FilterType.SHARPEN:
                return image.filter(ImageFilter.UnsharpMask(
                    radius=2.0,
                    percent=150 * intensity,
                    threshold=3
                ))
                
            elif filter_type_enum == FilterType.UNSHARP_MASK:
                radius = operation_params.get('radius', 2.0)
                percent = operation_params.get('percent', 150)
                threshold = operation_params.get('threshold', 3)
                return image.filter(ImageFilter.UnsharpMask(
                    radius=radius,
                    percent=int(percent * intensity),
                    threshold=threshold
                ))
                
            elif filter_type_enum == FilterType.EDGE_ENHANCE:
                return image.filter(ImageFilter.EDGE_ENHANCE_MORE if intensity > 0.5 else ImageFilter.EDGE_ENHANCE)
                
            elif filter_type_enum == FilterType.EMBOSS:
                return image.filter(ImageFilter.EMBOSS)
                
            elif filter_type_enum == FilterType.FIND_EDGES:
                return image.filter(ImageFilter.FIND_EDGES)
                
            elif filter_type_enum == FilterType.SMOOTH:
                return image.filter(ImageFilter.SMOOTH_MORE if intensity > 0.5 else ImageFilter.SMOOTH)
                
            elif filter_type_enum == FilterType.DETAIL:
                return image.filter(ImageFilter.DETAIL)
                
            elif filter_type_enum == FilterType.NOISE_REDUCTION:
                return await self._advanced_noise_reduction(image, operation_params)
                
            elif filter_type_enum == FilterType.BILATERAL:
                return await self._bilateral_filter(image, operation_params)
                
            else:
                raise ValidationError(f"Unknown filter type: {filter_type}")
                
        except Exception as e:
            raise ProcessingError(f"Filter application failed: {str(e)}")

    async def _apply_motion_blur(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Apply motion blur effect"""
        try:
            angle = params.get('angle', 0)
            distance = params.get('distance', 10)
            
            # Create motion blur kernel
            size = int(distance * 2) + 1
            kernel = np.zeros((size, size))
            
            # Calculate kernel values based on angle
            angle_rad = np.radians(angle)
            dx = int(np.cos(angle_rad) * distance)
            dy = int(np.sin(angle_rad) * distance)
            
            center = size // 2
            x_start, y_start = center - dx, center - dy
            x_end, y_end = center + dx, center + dy
            
            # Draw line in kernel
            cv2.line(kernel, (x_start, y_start), (x_end, y_end), 1, 1)
            kernel = kernel / np.sum(kernel)
            
            # Apply convolution
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                blurred = np.zeros_like(img_array)
                for i in range(3):  # RGB channels
                    blurred[:, :, i] = cv2.filter2D(img_array[:, :, i], -1, kernel)
            else:
                blurred = cv2.filter2D(img_array, -1, kernel)
            
            return Image.fromarray(np.uint8(blurred))
            
        except Exception as e:
            raise ProcessingError(f"Motion blur failed: {str(e)}")

    async def _advanced_noise_reduction(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Advanced noise reduction using multiple techniques"""
        try:
            strength = params.get('strength', 10)
            preserve_edges = params.get('preserve_edges', True)
            
            img_array = np.array(image)
            
            if preserve_edges:
                # Use bilateral filter for edge-preserving denoising
                if len(img_array.shape) == 3:
                    denoised = cv2.bilateralFilter(img_array, 9, strength * 2, strength * 2)
                else:
                    denoised = cv2.bilateralFilter(img_array, 9, strength, strength)
            else:
                # Use Gaussian blur for simple denoising
                kernel_size = min(15, max(3, int(strength / 2)))
                if kernel_size % 2 == 0:
                    kernel_size += 1
                denoised = cv2.GaussianBlur(img_array, (kernel_size, kernel_size), 0)
            
            return Image.fromarray(denoised)
            
        except Exception as e:
            raise ProcessingError(f"Noise reduction failed: {str(e)}")

    async def _bilateral_filter(self, image: Image.Image, params: Dict[str, Any]) -> Image.Image:
        """Apply bilateral filter for edge-preserving smoothing"""
        try:
            d = params.get('d', 9)
            sigma_color = params.get('sigma_color', 75)
            sigma_space = params.get('sigma_space', 75)
            
            img_array = np.array(image)
            filtered = cv2.bilateralFilter(img_array, d, sigma_color, sigma_space)
            
            return Image.fromarray(filtered)
            
        except Exception as e:
            raise ProcessingError(f"Bilateral filter failed: {str(e)}")

    async def _adjust_brightness(
        self, 
        image: Image.Image, 
        operation_params: Dict[str, Any], 
        params: ProcessingParams
    ) -> Image.Image:
        """Adjust image brightness"""
        try:
            factor = operation_params.get('factor', 1.0)
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(factor)
            
        except Exception as e:
            raise ProcessingError(f"Brightness adjustment failed: {str(e)}")

    async def _adjust_contrast(
        self, 
        image: Image.Image, 
        operation_params: Dict[str, Any], 
        params: ProcessingParams
    ) -> Image.Image:
        """Adjust image contrast"""
        try:
            factor = operation_params.get('factor', 1.0)
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(factor)
            
        except Exception as e:
            raise ProcessingError(f"Contrast adjustment failed: {str(e)}")

    async def _adjust_saturation(
        self, 
        image: Image.Image, 
        operation_params: Dict[str, Any], 
        params: ProcessingParams
    ) -> Image.Image:
        """Adjust color saturation"""
        try:
            factor = operation_params.get('factor', 1.0)
            enhancer = ImageEnhance.Color(image)
            return enhancer.enhance(factor)
            
        except Exception as e:
            raise ProcessingError(f"Saturation adjustment failed: {str(e)}")

    async def _calculate_quality_metrics(
        self, 
        original: Image.Image, 
        processed: Image.Image
    ) -> Dict[str, float]:
        """Calculate quality metrics comparing original and processed images"""
        try:
            # Convert to numpy arrays
            orig_array = np.array(original)
            proc_array = np.array(processed)
            
            # Resize processed image to match original if different sizes
            if orig_array.shape != proc_array.shape:
                processed_resized = processed.resize(original.size, Image.Resampling.LANCZOS)
                proc_array = np.array(processed_resized)
            
            # Calculate MSE (Mean Squared Error)
            mse = np.mean((orig_array.astype(float) - proc_array.astype(float)) ** 2)
            
            # Calculate PSNR (Peak Signal-to-Noise Ratio)
            if mse == 0:
                psnr = float('inf')
            else:
                max_pixel = 255.0
                psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
            
            # Calculate SSIM (Structural Similarity Index)
            ssim = self._calculate_ssim(orig_array, proc_array)
            
            # Calculate sharpness metrics
            orig_sharpness = self._calculate_sharpness(orig_array)
            proc_sharpness = self._calculate_sharpness(proc_array)
            
            # Calculate contrast metrics
            orig_contrast = np.std(orig_array)
            proc_contrast = np.std(proc_array)
            
            return {
                'mse': float(mse),
                'psnr': float(psnr),
                'ssim': float(ssim),
                'original_sharpness': float(orig_sharpness),
                'processed_sharpness': float(proc_sharpness),
                'sharpness_improvement': float(proc_sharpness - orig_sharpness),
                'original_contrast': float(orig_contrast),
                'processed_contrast': float(proc_contrast),
                'contrast_improvement': float(proc_contrast - orig_contrast)
            }
            
        except Exception as e:
            logger.warning(f"Quality metrics calculation failed: {str(e)}")
            return {}

    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """Calculate Structural Similarity Index"""
        try:
            from skimage.metrics import structural_similarity as ssim
            
            if len(img1.shape) == 3:
                # For color images, calculate SSIM for each channel and average
                ssim_values = []
                for i in range(img1.shape[2]):
                    ssim_val = ssim(img1[:, :, i], img2[:, :, i])
                    ssim_values.append(ssim_val)
                return np.mean(ssim_values)
            else:
                return ssim(img1, img2)
                
        except ImportError:
            # Fallback simple correlation coefficient
            return np.corrcoef(img1.flatten(), img2.flatten())[0, 1]

    def _calculate_sharpness(self, image: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance"""
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            return cv2.Laplacian(gray, cv2.CV_64F).var()
            
        except Exception:
            return 0.0

    async def _save_image(
        self, 
        image: Image.Image, 
        output_path: Union[str, Path], 
        params: ProcessingParams
    ) -> None:
        """Save processed image with optimized settings"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Determine format and save parameters
            format_name = output_path.suffix.lower()
            
            save_kwargs = {}
            
            if format_name in ['.jpg', '.jpeg']:
                save_kwargs.update({
                    'format': 'JPEG',
                    'quality': 95,
                    'optimize': True,
                    'progressive': True
                })
                
            elif format_name == '.png':
                save_kwargs.update({
                    'format': 'PNG',
                    'optimize': True,
                    'compress_level': 6
                })
                
            elif format_name == '.webp':
                save_kwargs.update({
                    'format': 'WEBP',
                    'quality': 90,
                    'optimize': True
                })
            
            # Save with EXIF preservation if requested
            if params.preserve_exif and hasattr(image, 'info') and 'exif' in image.info:
                save_kwargs['exif'] = image.info['exif']
            
            image.save(output_path, **save_kwargs)
            logger.info(f"Image saved: {output_path}")
            
        except Exception as e:
            raise ProcessingError(f"Failed to save image: {str(e)}")

    # Additional placeholder methods for complex operations
    async def _rotate_image(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Rotate image by specified angle"""
        angle = operation_params.get('angle', 0)
        expand = operation_params.get('expand', False)
        fillcolor = operation_params.get('fillcolor', (255, 255, 255))
        return image.rotate(angle, expand=expand, fillcolor=fillcolor)

    async def _flip_image(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Flip image horizontally or vertically"""
        direction = operation_params.get('direction', 'horizontal')
        if direction == 'horizontal':
            return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        elif direction == 'vertical':
            return image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        else:
            raise ValidationError(f"Invalid flip direction: {direction}")

    async def _adjust_hue(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Adjust image hue"""
        # Convert to HSV, adjust hue, convert back
        hsv = image.convert('HSV')
        h, s, v = hsv.split()
        
        # Apply hue adjustment
        hue_shift = operation_params.get('shift', 0)
        h_array = np.array(h)
        h_array = (h_array + hue_shift) % 256
        h = Image.fromarray(h_array)
        
        return Image.merge('HSV', (h, s, v)).convert('RGB')

    async def _adjust_gamma(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Apply gamma correction"""
        gamma = operation_params.get('gamma', 1.0)
        
        # Create gamma correction lookup table
        inv_gamma = 1.0 / gamma
        table = [((i / 255.0) ** inv_gamma) * 255 for i in range(256)]
        
        return image.point(table * 3)  # Apply to RGB

    async def _adjust_color_balance(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Adjust color balance"""
        shadows = operation_params.get('shadows', (1.0, 1.0, 1.0))
        midtones = operation_params.get('midtones', (1.0, 1.0, 1.0))
        highlights = operation_params.get('highlights', (1.0, 1.0, 1.0))
        
        # This is a simplified implementation
        # Real color balance would require more sophisticated algorithms
        r, g, b = image.split()
        
        # Apply midtone adjustments (simplified)
        if midtones != (1.0, 1.0, 1.0):
            r_table = [int(i * midtones[0]) for i in range(256)]
            g_table = [int(i * midtones[1]) for i in range(256)]
            b_table = [int(i * midtones[2]) for i in range(256)]
            
            r = r.point(r_table)
            g = g.point(g_table)
            b = b.point(b_table)
        
        return Image.merge('RGB', (r, g, b))

    async def _sharpen_image(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Apply sharpening filter"""
        strength = operation_params.get('strength', 1.0)
        radius = operation_params.get('radius', 2.0)
        
        return image.filter(ImageFilter.UnsharpMask(
            radius=radius,
            percent=int(150 * strength),
            threshold=3
        ))

    async def _blur_image(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Apply blur filter"""
        radius = operation_params.get('radius', 2.0)
        return image.filter(ImageFilter.GaussianBlur(radius=radius))

    async def _reduce_noise(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Reduce image noise"""
        return await self._advanced_noise_reduction(image, operation_params)

    async def _enhance_image(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """General image enhancement"""
        # Apply multiple enhancements based on analysis
        enhanced = image.copy()
        
        # Auto-enhance contrast
        enhancer = ImageEnhance.Contrast(enhanced)
        enhanced = enhancer.enhance(1.1)
        
        # Auto-enhance color
        enhancer = ImageEnhance.Color(enhanced)
        enhanced = enhancer.enhance(1.05)
        
        # Auto-enhance sharpness
        enhancer = ImageEnhance.Sharpness(enhanced)
        enhanced = enhancer.enhance(1.1)
        
        return enhanced

    async def _color_correct(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Apply color correction"""
        # Auto white balance and color correction
        img_array = np.array(image).astype(np.float32)
        
        # Simple gray world assumption
        avg_r = np.mean(img_array[:, :, 0])
        avg_g = np.mean(img_array[:, :, 1])
        avg_b = np.mean(img_array[:, :, 2])
        
        gray_value = (avg_r + avg_g + avg_b) / 3
        
        # Calculate correction factors
        r_factor = gray_value / avg_r if avg_r > 0 else 1.0
        g_factor = gray_value / avg_g if avg_g > 0 else 1.0
        b_factor = gray_value / avg_b if avg_b > 0 else 1.0
        
        # Apply correction
        img_array[:, :, 0] *= r_factor
        img_array[:, :, 1] *= g_factor
        img_array[:, :, 2] *= b_factor
        
        # Clamp values
        img_array = np.clip(img_array, 0, 255)
        
        return Image.fromarray(img_array.astype(np.uint8))

    async def _histogram_equalization(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Apply histogram equalization"""
        img_array = np.array(image)
        
        if len(img_array.shape) == 3:
            # Convert to LAB color space for better results
            lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge and convert back
            lab = cv2.merge([l, a, b])
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        else:
            # Grayscale histogram equalization
            result = cv2.equalizeHist(img_array)
        
        return Image.fromarray(result)

    async def _local_adjustment(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Apply local adjustments to specific regions"""
        # Placeholder for advanced local adjustment algorithms
        # This would involve mask creation and selective processing
        return image

    async def _apply_artistic_effect(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Apply artistic effects"""
        effect_type = operation_params.get('type', 'oil_painting')
        
        if effect_type == 'oil_painting':
            # Simple oil painting effect using bilateral filter
            img_array = np.array(image)
            for _ in range(3):
                img_array = cv2.bilateralFilter(img_array, 9, 200, 200)
            return Image.fromarray(img_array)
        
        # Add more artistic effects as needed
        return image

    async def _add_watermark(self, image: Image.Image, operation_params: Dict[str, Any], params: ProcessingParams) -> Image.Image:
        """Add watermark to image"""
        watermark_text = operation_params.get('text', '© 2025')
        position = operation_params.get('position', 'bottom_right')
        opacity = operation_params.get('opacity', 0.5)
        
        # Create a copy for watermarking
        watermarked = image.copy()
        
        # Create transparent overlay
        overlay = Image.new('RGBA', watermarked.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Try to load a font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # Calculate text position
        text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        if position == 'bottom_right':
            x = watermarked.size[0] - text_width - 10
            y = watermarked.size[1] - text_height - 10
        elif position == 'bottom_left':
            x = 10
            y = watermarked.size[1] - text_height - 10
        elif position == 'top_right':
            x = watermarked.size[0] - text_width - 10
            y = 10
        else:  # top_left
            x = 10
            y = 10
        
        # Draw text with opacity
        draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, int(255 * opacity)))
        
        # Composite the watermark
        if watermarked.mode != 'RGBA':
            watermarked = watermarked.convert('RGBA')
        
        watermarked = Image.alpha_composite(watermarked, overlay)
        
        # Convert back to original mode if needed
        if image.mode != 'RGBA':
            watermarked = watermarked.convert(image.mode)
        
        return watermarked


class ImageAnalyzer:
    """
    Advanced Image Analysis Engine
    
    Provides comprehensive image analysis capabilities including:
    - Quality assessment and scoring
    - Content analysis and object detection
    - Technical parameter analysis
    - Composition and aesthetic evaluation
    """
    
    def __init__(self, enable_ai: bool = True):
        """
        Initialize Image Analyzer
        
        Args:
            enable_ai: Enable AI-powered analysis features
        """
        self.enable_ai = enable_ai
        
        logger.info(f"ImageAnalyzer initialized - AI enabled: {enable_ai}")

    async def analyze_comprehensive(self, image: Image.Image) -> Dict[str, Any]:
        """Perform comprehensive image analysis"""
        try:
            results = {}
            
            # Basic technical analysis
            results['technical'] = await self._analyze_technical(image)
            
            # Quality assessment
            results['quality'] = await self._assess_quality(image)
            
            # Composition analysis
            results['composition'] = await self._analyze_composition(image)
            
            # Color analysis
            results['color'] = await self._analyze_color(image)
            
            if self.enable_ai:
                # AI-powered content analysis
                results['content'] = await self._analyze_content_ai(image)
            
            return results
            
        except Exception as e:
            logger.error(f"Comprehensive analysis failed: {str(e)}")
            return {"error": str(e)}

    async def _analyze_technical(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze technical image parameters"""
        img_array = np.array(image)
        
        # Basic metrics
        width, height = image.size
        aspect_ratio = width / height
        total_pixels = width * height
        
        # Color metrics
        if len(img_array.shape) == 3:
            channels = img_array.shape[2]
            mean_rgb = np.mean(img_array, axis=(0, 1))
            std_rgb = np.std(img_array, axis=(0, 1))
        else:
            channels = 1
            mean_rgb = [np.mean(img_array)]
            std_rgb = [np.std(img_array)]
        
        # Histogram analysis
        if len(img_array.shape) == 3:
            hist_r = np.histogram(img_array[:, :, 0], bins=256, range=(0, 256))[0]
            hist_g = np.histogram(img_array[:, :, 1], bins=256, range=(0, 256))[0]
            hist_b = np.histogram(img_array[:, :, 2], bins=256, range=(0, 256))[0]
            
            # Dynamic range
            dynamic_range = {
                'red': float(np.max(img_array[:, :, 0]) - np.min(img_array[:, :, 0])),
                'green': float(np.max(img_array[:, :, 1]) - np.min(img_array[:, :, 1])),
                'blue': float(np.max(img_array[:, :, 2]) - np.min(img_array[:, :, 2]))
            }
        else:
            hist = np.histogram(img_array, bins=256, range=(0, 256))[0]
            dynamic_range = float(np.max(img_array) - np.min(img_array))
        
        return {
            'dimensions': {'width': width, 'height': height},
            'aspect_ratio': float(aspect_ratio),
            'total_pixels': int(total_pixels),
            'channels': int(channels),
            'mean_values': [float(x) for x in mean_rgb],
            'std_values': [float(x) for x in std_rgb],
            'dynamic_range': dynamic_range,
            'bit_depth': 8,  # Assuming 8-bit images
            'color_space': image.mode
        }

    async def _assess_quality(self, image: Image.Image) -> Dict[str, Any]:
        """Assess overall image quality"""
        img_array = np.array(image)
        
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Sharpness (Laplacian variance)
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Contrast (standard deviation)
        contrast = np.std(gray)
        
        # Noise estimation
        noise = np.std(cv2.medianBlur(gray, 5) - gray)
        
        # Exposure analysis
        hist = np.histogram(gray, bins=256, range=(0, 256))[0]
        underexposed = np.sum(hist[:25]) / gray.size
        overexposed = np.sum(hist[230:]) / gray.size
        
        # Overall quality score (0-1)
        sharpness_score = min(1.0, sharpness / 1000.0)
        contrast_score = min(1.0, contrast / 64.0)
        noise_score = max(0.0, 1.0 - noise / 10.0)
        exposure_score = 1.0 - (underexposed + overexposed)
        
        quality_score = (
            sharpness_score * 0.3 +
            contrast_score * 0.3 +
            noise_score * 0.2 +
            exposure_score * 0.2
        )
        
        return {
            'overall_score': float(quality_score),
            'sharpness': float(sharpness),
            'sharpness_score': float(sharpness_score),
            'contrast': float(contrast),
            'contrast_score': float(contrast_score),
            'noise_level': float(noise),
            'noise_score': float(noise_score),
            'exposure_score': float(exposure_score),
            'underexposed_ratio': float(underexposed),
            'overexposed_ratio': float(overexposed)
        }

    async def _analyze_composition(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze image composition"""
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY) if len(img_array.shape) == 3 else img_array
        
        height, width = gray.shape
        
        # Rule of thirds analysis
        third_x = [width // 3, 2 * width // 3]
        third_y = [height // 3, 2 * height // 3]
        
        # Edge detection for interest points
        edges = cv2.Canny(gray, 100, 200)
        
        # Calculate edge density at rule of thirds lines
        vertical_edges = np.sum(edges[:, third_x[0]-2:third_x[0]+3]) + np.sum(edges[:, third_x[1]-2:third_x[1]+3])
        horizontal_edges = np.sum(edges[third_y[0]-2:third_y[0]+3, :]) + np.sum(edges[third_y[1]-2:third_y[1]+3, :])
        
        # Interest points at intersections
        intersection_density = 0
        for y in third_y:
            for x in third_x:
                intersection_density += np.sum(edges[y-5:y+6, x-5:x+6])
        
        # Balance analysis
        left_weight = np.sum(gray[:, :width//2])
        right_weight = np.sum(gray[:, width//2:])
        horizontal_balance = 1.0 - abs(left_weight - right_weight) / max(left_weight, right_weight)
        
        top_weight = np.sum(gray[:height//2, :])
        bottom_weight = np.sum(gray[height//2:, :])
        vertical_balance = 1.0 - abs(top_weight - bottom_weight) / max(top_weight, bottom_weight)
        
        # Symmetry analysis
        left_half = gray[:, :width//2]
        right_half = np.fliplr(gray[:, width//2:])
        if left_half.shape == right_half.shape:
            horizontal_symmetry = np.corrcoef(left_half.flatten(), right_half.flatten())[0, 1]
        else:
            horizontal_symmetry = 0.0
        
        return {
            'rule_of_thirds_score': float((vertical_edges + horizontal_edges) / (width * height * 0.01)),
            'intersection_interest': float(intersection_density / 1000.0),
            'horizontal_balance': float(horizontal_balance),
            'vertical_balance': float(vertical_balance),
            'overall_balance': float((horizontal_balance + vertical_balance) / 2),
            'horizontal_symmetry': float(horizontal_symmetry) if not np.isnan(horizontal_symmetry) else 0.0
        }

    async def _analyze_color(self, image: Image.Image) -> Dict[str, Any]:
        """Analyze color characteristics"""
        img_array = np.array(image)
        
        if len(img_array.shape) != 3:
            return {"error": "Color analysis requires RGB image"}
        
        # Convert to different color spaces for analysis
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
        
        # Dominant colors using K-means
        pixels = img_array.reshape(-1, 3)
        kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
        kmeans.fit(pixels)
        dominant_colors = kmeans.cluster_centers_.astype(int)
        
        # Color distribution
        color_std = np.std(img_array, axis=(0, 1))
        
        # Saturation analysis
        saturation_mean = np.mean(hsv[:, :, 1])
        saturation_std = np.std(hsv[:, :, 1])
        
        # Hue distribution
        hue_hist = np.histogram(hsv[:, :, 0], bins=180, range=(0, 180))[0]
        hue_entropy = -np.sum((hue_hist + 1e-7) * np.log(hue_hist + 1e-7))
        
        # Color harmony analysis (simplified)
        hue_dominant = np.argmax(hue_hist)
        complementary_hue = (hue_dominant + 90) % 180
        harmony_score = hue_hist[complementary_hue] / np.max(hue_hist) if np.max(hue_hist) > 0 else 0
        
        return {
            'dominant_colors': dominant_colors.tolist(),
            'color_variance': {
                'red': float(color_std[0]),
                'green': float(color_std[1]),
                'blue': float(color_std[2])
            },
            'saturation': {
                'mean': float(saturation_mean),
                'std': float(saturation_std)
            },
            'hue_entropy': float(hue_entropy),
            'color_harmony_score': float(harmony_score),
            'temperature': float(np.mean(img_array[:, :, 0]) - np.mean(img_array[:, :, 2]))  # Simplified
        }

    async def _analyze_content_ai(self, image: Image.Image) -> Dict[str, Any]:
        """AI-powered content analysis (placeholder)"""
        # This would integrate with actual AI models for:
        # - Object detection
        # - Scene classification
        # - Face detection
        # - Text recognition
        # - Aesthetic scoring
        
        return {
            "ai_analysis": "placeholder",
            "detected_objects": [],
            "scene_classification": {},
            "aesthetic_score": 0.5,
            "faces_detected": 0,
            "text_detected": False
        }
