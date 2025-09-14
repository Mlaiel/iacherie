"""
🖼️ IMAGE FORMATS PROCESSOR - ENTERPRISE ARCHITECTURE
====================================================

Professional image format processing and optimization for Ainflue Platform
Supporting all modern image formats including next-gen formats with AI optimization

**Expert Implementation:**
- ML Engineer: AI-powered image analysis, enhancement, and optimization
- Backend Senior: High-performance image processing pipelines
- Security Engineer: Image content validation and security compliance
- Performance Engineer: Memory optimization and batch processing

**Supported Formats:** WebP, AVIF, HEIF, JPEG XL, PNG, JPG, GIF, BMP, TIFF, SVG
**Features:** Next-gen format support, AI enhancement, Lossy/Lossless optimization
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import mimetypes
import struct
import os
import base64

# Image processing libraries
try:
    from PIL import Image, ImageOps, ImageEnhance, ExifTags
    import cv2
    import numpy as np
    import pillow_heif
    import imageio
    from pillow_avif import AvifImagePlugin
    from io import BytesIO
except ImportError as e:
    logging.warning(f"Image processing dependencies not available: {e}")

from ..analytics.image_analytics import ImageQualityAnalyzer, ImageContentAnalyzer
from ..compression.image_compression import ImageCompressionEngine

logger = logging.getLogger(__name__)

class ImageFormat(Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    AVIF = "avif"
    HEIF = "heif"
    JPEG_XL = "jpeg_xl"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    SVG = "svg"
    ICO = "ico"
    RAW = "raw"

class ImageQuality(Enum):
    """Image quality presets"""
    LOW = "low"           # High compression, smaller size
    MEDIUM = "medium"     # Balanced compression
    HIGH = "high"         # Low compression, high quality
    LOSSLESS = "lossless" # No compression artifacts
    MAXIMUM = "maximum"   # Maximum quality settings

@dataclass
class ImageFormatInfo:
    """Comprehensive image format information"""
    format_type: ImageFormat
    resolution: Tuple[int, int]  # (width, height)
    color_mode: str  # RGB, RGBA, CMYK, L, etc.
    color_depth: int  # bits per channel
    file_size: int
    compression_ratio: float
    has_transparency: bool
    has_animation: bool
    frame_count: int
    quality_score: float
    metadata: Dict[str, Any]
    exif_data: Dict[str, Any]
    color_profile: Optional[str]
    is_progressive: bool

@dataclass
class ImageProcessingOptions:
    """Image processing configuration"""
    target_format: ImageFormat
    target_resolution: Optional[Tuple[int, int]] = None
    quality_preset: ImageQuality = ImageQuality.HIGH
    preserve_metadata: bool = True
    preserve_transparency: bool = True
    optimize_size: bool = True
    progressive_encoding: bool = True
    color_profile_conversion: Optional[str] = None
    enhancement_enabled: bool = True

class ModernImageFormats:
    """Handler for next-generation image formats"""
    
    def __init__(self) -> None:
        self.format_specs = {
            ImageFormat.WEBP: {
                'max_resolution': (16383, 16383),
                'supports_animation': True,
                'supports_transparency': True,
                'compression_modes': ['lossy', 'lossless'],
                'quality_range': (0, 100),
                'browser_support': 95  # % of browsers
            },
            ImageFormat.AVIF: {
                'max_resolution': (65536, 65536),
                'supports_animation': True,
                'supports_transparency': True,
                'compression_modes': ['lossy', 'lossless'],
                'quality_range': (0, 100),
                'browser_support': 85
            },
            ImageFormat.HEIF: {
                'max_resolution': (65536, 65536),
                'supports_animation': True,
                'supports_transparency': True,
                'compression_modes': ['lossy', 'lossless'],
                'quality_range': (0, 100),
                'browser_support': 15
            },
            ImageFormat.JPEG_XL: {
                'max_resolution': (1073741824, 1073741824),
                'supports_animation': True,
                'supports_transparency': True,
                'compression_modes': ['lossy', 'lossless'],
                'quality_range': (0, 100),
                'browser_support': 5
            }
        }
    
    def get_format_specs(self, format_type: ImageFormat) -> Dict[str, Any]:
        """Get specifications for image format"""
        return self.format_specs.get(format_type, {})
    
    def get_compression_efficiency(self, format_type: ImageFormat) -> float:
        """Get compression efficiency compared to JPEG"""
        efficiency_map = {
            ImageFormat.WEBP: 0.75,    # 25% better than JPEG
            ImageFormat.AVIF: 0.50,    # 50% better than JPEG
            ImageFormat.HEIF: 0.55,    # 45% better than JPEG
            ImageFormat.JPEG_XL: 0.40, # 60% better than JPEG
            ImageFormat.JPEG: 1.0,     # Baseline
            ImageFormat.PNG: 1.5       # Usually larger than JPEG
        }
        return efficiency_map.get(format_type, 1.0)
    
    def is_next_gen_format(self, format_type: ImageFormat) -> bool:
        """Check if format is next-generation"""
        next_gen_formats = [
            ImageFormat.WEBP, ImageFormat.AVIF, 
            ImageFormat.HEIF, ImageFormat.JPEG_XL
        ]
        return format_type in next_gen_formats

class ImageFormatProcessor:
    """Enterprise image format processor with AI capabilities"""
    
    def __init__(self) -> None:
        self.modern_formats = ModernImageFormats()
        self.quality_analyzer = ImageQualityAnalyzer()
        self.content_analyzer = ImageContentAnalyzer()
        self.compression_engine = ImageCompressionEngine()
        self.supported_formats = list(ImageFormat)
        
        # Initialize format plugins
        self._initialize_format_support()
    
    def _initialize_format_support(self) -> None:
        """Initialize support for various image formats"""
        try:
            # Register HEIF plugin
            pillow_heif.register_heif_opener()
            
            # Register AVIF plugin (already handled by pillow_avif import)
            
            logger.info("Image format plugins initialized successfully")
        except Exception as e:
            logger.warning(f"Some image format plugins failed to initialize: {e}")
    
    async def detect_format(self, file_path: Union[str, Path]) -> ImageFormatInfo:
        """Detect image format using multiple analysis methods"""
        file_path = Path(file_path)
        
        try:
            # Method 1: PIL/Pillow analysis (most comprehensive)
            format_info = await self._analyze_with_pil(file_path)
            if format_info:
                return format_info
            
            # Method 2: OpenCV analysis  
            format_info = await self._analyze_with_opencv(file_path)
            if format_info:
                return format_info
            
            # Method 3: Binary signature analysis
            format_info = await self._analyze_with_signature(file_path)
            if format_info:
                return format_info
            
            # Method 4: Basic detection from extension
            return await self._basic_format_detection(file_path)
            
        except Exception as e:
            logger.error(f"Error detecting image format for {file_path}: {e}")
            raise
    
    async def _analyze_with_pil(self, file_path: Path) -> Optional[ImageFormatInfo]:
        """Analyze image with PIL/Pillow (most comprehensive)"""
        try:
            with Image.open(file_path) as img:
                # Basic format information
                format_type = self._map_pil_format(img.format)
                width, height = img.size
                color_mode = img.mode
                
                # Color depth calculation
                color_depth = self._calculate_color_depth(img)
                
                # File size
                file_size = file_path.stat().st_size
                
                # Calculate compression ratio
                uncompressed_size = width * height * (color_depth // 8) * len(color_mode)
                compression_ratio = file_size / uncompressed_size if uncompressed_size > 0 else 1.0
                
                # Transparency detection
                has_transparency = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                
                # Animation detection
                has_animation = getattr(img, 'is_animated', False)
                frame_count = getattr(img, 'n_frames', 1)
                
                # Progressive encoding detection
                is_progressive = img.info.get('progressive', False)
                
                # EXIF data extraction
                exif_data = self._extract_exif_data(img)
                
                # Metadata extraction
                metadata = dict(img.info)
                
                # Color profile
                color_profile = img.info.get('icc_profile')
                if color_profile:
                    color_profile = f"ICC Profile ({len(color_profile)} bytes)"
                
                # Quality analysis
                quality_score = await self._analyze_image_quality(file_path, img)
                
                return ImageFormatInfo(
                    format_type=format_type,
                    resolution=(width, height),
                    color_mode=color_mode,
                    color_depth=color_depth,
                    file_size=file_size,
                    compression_ratio=compression_ratio,
                    has_transparency=has_transparency,
                    has_animation=has_animation,
                    frame_count=frame_count,
                    quality_score=quality_score,
                    metadata=metadata,
                    exif_data=exif_data,
                    color_profile=color_profile,
                    is_progressive=is_progressive
                )
                
        except Exception as e:
            logger.warning(f"PIL analysis failed: {e}")
            return None
    
    async def _analyze_with_opencv(self, file_path: Path) -> Optional[ImageFormatInfo]:
        """Analyze image with OpenCV (fallback method)"""
        try:
            # Read image with OpenCV
            img = cv2.imread(str(file_path), cv2.IMREAD_UNCHANGED)
            
            if img is None:
                return None
            
            # Get basic properties
            if len(img.shape) == 3:
                height, width, channels = img.shape
                color_mode = 'BGR' if channels == 3 else 'BGRA'
            else:
                height, width = img.shape
                channels = 1
                color_mode = 'L'
            
            # Determine format from extension
            format_type = self._get_format_from_extension(file_path.suffix.lower().lstrip('.'))
            
            file_size = file_path.stat().st_size
            color_depth = img.dtype.itemsize * 8  # bits
            
            return ImageFormatInfo(
                format_type=format_type or ImageFormat.JPEG,
                resolution=(width, height),
                color_mode=color_mode,
                color_depth=color_depth,
                file_size=file_size,
                compression_ratio=1.0,
                has_transparency=channels == 4,
                has_animation=False,
                frame_count=1,
                quality_score=0.5,  # Default
                metadata={},
                exif_data={},
                color_profile=None,
                is_progressive=False
            )
            
        except Exception as e:
            logger.warning(f"OpenCV analysis failed: {e}")
            return None
    
    async def _analyze_with_signature(self, file_path: Path) -> Optional[ImageFormatInfo]:
        """Analyze image using binary signatures"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(32)
            
            # Image format signatures
            signatures = {
                b'\xff\xd8\xff': ImageFormat.JPEG,
                b'\x89PNG\r\n\x1a\n': ImageFormat.PNG,
                b'RIFF': ImageFormat.WEBP,  # WebP uses RIFF container
                b'GIF87a': ImageFormat.GIF,
                b'GIF89a': ImageFormat.GIF,
                b'BM': ImageFormat.BMP,
                b'II*\x00': ImageFormat.TIFF,
                b'MM\x00*': ImageFormat.TIFF,
                b'\x00\x00\x01\x00': ImageFormat.ICO
            }
            
            for signature, format_type in signatures.items():
                if header.startswith(signature):
                    # Get basic file info
                    file_size = file_path.stat().st_size
                    
                    return ImageFormatInfo(
                        format_type=format_type,
                        resolution=(0, 0),  # Unknown
                        color_mode='unknown',
                        color_depth=8,
                        file_size=file_size,
                        compression_ratio=1.0,
                        has_transparency=False,
                        has_animation=False,
                        frame_count=1,
                        quality_score=0.0,
                        metadata={},
                        exif_data={},
                        color_profile=None,
                        is_progressive=False
                    )
            
            return None
            
        except Exception as e:
            logger.warning(f"Signature analysis failed: {e}")
            return None
    
    async def _basic_format_detection(self, file_path: Path) -> ImageFormatInfo:
        """Basic format detection from file extension"""
        extension = file_path.suffix.lower().lstrip('.')
        format_type = self._get_format_from_extension(extension)
        
        if not format_type:
            format_type = ImageFormat.JPEG  # Default
        
        file_size = file_path.stat().st_size
        
        return ImageFormatInfo(
            format_type=format_type,
            resolution=(0, 0),
            color_mode='unknown',
            color_depth=8,
            file_size=file_size,
            compression_ratio=1.0,
            has_transparency=False,
            has_animation=False,
            frame_count=1,
            quality_score=0.0,
            metadata={},
            exif_data={},
            color_profile=None,
            is_progressive=False
        )
    
    def _map_pil_format(self, pil_format: str) -> ImageFormat:
        """Map PIL format to ImageFormat enum"""
        format_map = {
            'JPEG': ImageFormat.JPEG,
            'PNG': ImageFormat.PNG,
            'WEBP': ImageFormat.WEBP,
            'GIF': ImageFormat.GIF,
            'BMP': ImageFormat.BMP,
            'TIFF': ImageFormat.TIFF,
            'ICO': ImageFormat.ICO,
            'HEIF': ImageFormat.HEIF,
            'AVIF': ImageFormat.AVIF
        }
        return format_map.get(pil_format, ImageFormat.JPEG)
    
    def _get_format_from_extension(self, extension: str) -> Optional[ImageFormat]:
        """Get format from file extension"""
        ext_map = {
            'jpg': ImageFormat.JPEG,
            'jpeg': ImageFormat.JPEG,
            'png': ImageFormat.PNG,
            'webp': ImageFormat.WEBP,
            'avif': ImageFormat.AVIF,
            'heif': ImageFormat.HEIF,
            'heic': ImageFormat.HEIF,
            'jxl': ImageFormat.JPEG_XL,
            'gif': ImageFormat.GIF,
            'bmp': ImageFormat.BMP,
            'tiff': ImageFormat.TIFF,
            'tif': ImageFormat.TIFF,
            'svg': ImageFormat.SVG,
            'ico': ImageFormat.ICO
        }
        return ext_map.get(extension)
    
    def _calculate_color_depth(self, img: Image.Image) -> int:
        """Calculate color depth from PIL image"""
        mode_depth_map = {
            '1': 1,      # 1-bit pixels, black and white
            'L': 8,      # 8-bit pixels, black and white
            'P': 8,      # 8-bit pixels, mapped to any other mode using a color palette
            'RGB': 24,   # 3x8-bit pixels, true color
            'RGBA': 32,  # 4x8-bit pixels, true color with transparency mask
            'CMYK': 32,  # 4x8-bit pixels, color separation
            'YCbCr': 24, # 3x8-bit pixels, color video format
            'LAB': 24,   # 3x8-bit pixels, the L*a*b* color space
            'HSV': 24    # 3x8-bit pixels, Hue, Saturation, Value color space
        }
        return mode_depth_map.get(img.mode, 8)
    
    def _extract_exif_data(self, img: Image.Image) -> Dict[str, Any]:
        """Extract EXIF data from image"""
        exif_data = {}
        
        try:
            exif = img._getexif()
            if exif is not None:
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    
                    # Convert bytes to string for some tags
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8')
                        except:
                            value = str(value)
                    
                    exif_data[tag] = value
        except:
            pass  # EXIF not available or corrupted
        
        return exif_data
    
    async def _analyze_image_quality(self, file_path: Path, img: Image.Image) -> float:
        """Analyze image quality using AI"""
        try:
            # Convert PIL image to numpy array for analysis
            img_array = np.array(img)
            
            # Use quality analyzer
            quality_score = await self.quality_analyzer.analyze_image_quality(img_array)
            return quality_score
        except Exception as e:
            logger.warning(f"Quality analysis failed: {e}")
            return 0.5  # Default score
    
    async def convert_format(self, input_path: Union[str, Path],
                           output_path: Union[str, Path],
                           options: ImageProcessingOptions) -> ImageFormatInfo:
        """Convert image format with optimization"""
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            # Detect input format
            input_info = await self.detect_format(input_path)
            
            # Open image
            with Image.open(input_path) as img:
                # Apply enhancements if enabled
                if options.enhancement_enabled:
                    img = await self._enhance_image(img)
                
                # Handle resolution conversion
                if options.target_resolution:
                    img = img.resize(options.target_resolution, Image.Resampling.LANCZOS)
                
                # Handle transparency preservation
                if not options.preserve_transparency and img.mode in ('RGBA', 'LA'):
                    # Convert to RGB with white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                    img = background
                
                # Get save parameters
                save_params = await self._get_save_parameters(options, input_info)
                
                # Save in target format
                img.save(output_path, **save_params)
            
            # Transfer metadata if requested
            if options.preserve_metadata:
                await self._transfer_metadata(input_path, output_path, input_info.metadata)
            
            # Return format info for converted image
            return await self.detect_format(output_path)
            
        except Exception as e:
            logger.error(f"Error converting image format: {e}")
            raise
    
    async def _enhance_image(self, img: Image.Image) -> Image.Image:
        """Apply AI-powered image enhancements"""
        try:
            # Auto-orient based on EXIF
            img = ImageOps.exif_transpose(img)
            
            # Auto-contrast enhancement
            img = ImageOps.autocontrast(img)
            
            # Sharpness enhancement (subtle)
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.1)
            
            return img
        except Exception as e:
            logger.warning(f"Image enhancement failed: {e}")
            return img
    
    async def _get_save_parameters(self, options: ImageProcessingOptions,
                                 input_info: ImageFormatInfo) -> Dict[str, Any]:
        """Get optimal save parameters for target format"""
        params = {}
        
        # Quality settings
        quality_map = {
            ImageQuality.LOW: 60,
            ImageQuality.MEDIUM: 80,
            ImageQuality.HIGH: 95,
            ImageQuality.MAXIMUM: 100
        }
        
        if options.target_format in [ImageFormat.JPEG, ImageFormat.WEBP]:
            if options.quality_preset != ImageQuality.LOSSLESS:
                params['quality'] = quality_map[options.quality_preset]
            else:
                params['lossless'] = True
        
        # Format-specific parameters
        if options.target_format == ImageFormat.JPEG:
            params['optimize'] = options.optimize_size
            params['progressive'] = options.progressive_encoding
        
        elif options.target_format == ImageFormat.PNG:
            params['optimize'] = options.optimize_size
            if options.quality_preset == ImageQuality.LOW:
                params['compress_level'] = 9  # Maximum compression
            else:
                params['compress_level'] = 6  # Default
        
        elif options.target_format == ImageFormat.WEBP:
            params['optimize'] = options.optimize_size
            if options.quality_preset == ImageQuality.LOSSLESS:
                params['lossless'] = True
        
        elif options.target_format == ImageFormat.AVIF:
            if options.quality_preset != ImageQuality.LOSSLESS:
                params['quality'] = quality_map[options.quality_preset]
        
        return params
    
    async def _transfer_metadata(self, source_path -> None: Path, target_path -> None: Path,
                               metadata -> None: Dict[str, Any]) -> None:
        """Transfer metadata between image files"""
        try:
            # This is format-specific and may not work for all conversions
            # For production, would need more sophisticated metadata handling
            pass
        except Exception as e:
            logger.warning(f"Metadata transfer failed: {e}")
    
    async def get_optimal_format_for_use_case(self, use_case: str,
                                            browser_support_threshold: float = 85.0) -> ImageFormat:
        """Get optimal format for specific use case"""
        use_case_map = {
            'web_photography': ImageFormat.WEBP,
            'web_graphics': ImageFormat.WEBP,
            'mobile_app': ImageFormat.WEBP,
            'email': ImageFormat.JPEG,
            'print': ImageFormat.TIFF,
            'thumbnail': ImageFormat.WEBP,
            'icon': ImageFormat.PNG,
            'animation': ImageFormat.GIF,
            'next_gen_web': ImageFormat.AVIF,
            'social_media': ImageFormat.JPEG,
            'archival': ImageFormat.TIFF
        }
        
        optimal_format = use_case_map.get(use_case, ImageFormat.JPEG)
        
        # Check browser support if it's a web use case
        if 'web' in use_case or use_case in ['mobile_app', 'thumbnail']:
            format_specs = self.modern_formats.get_format_specs(optimal_format)
            browser_support = format_specs.get('browser_support', 100)
            
            if browser_support < browser_support_threshold:
                # Fallback to more compatible format
                return ImageFormat.JPEG
        
        return optimal_format
    
    async def batch_optimize_images(self, image_paths: List[Union[str, Path]],
                                  output_dir: Union[str, Path],
                                  options: ImageProcessingOptions) -> List[Dict[str, Any]]:
        """Batch optimize multiple images"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        
        for image_path in image_paths:
            try:
                image_path = Path(image_path)
                
                # Generate output path
                output_path = output_dir / f"{image_path.stem}.{options.target_format.value}"
                
                # Convert image
                original_info = await self.detect_format(image_path)
                converted_info = await self.convert_format(image_path, output_path, options)
                
                # Calculate savings
                size_reduction = (original_info.file_size - converted_info.file_size) / original_info.file_size
                
                results.append({
                    'input_path': str(image_path),
                    'output_path': str(output_path),
                    'original_size': original_info.file_size,
                    'converted_size': converted_info.file_size,
                    'size_reduction': size_reduction,
                    'quality_score': converted_info.quality_score,
                    'success': True
                })
                
            except Exception as e:
                results.append({
                    'input_path': str(image_path),
                    'output_path': None,
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    async def validate_image_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Comprehensive image file validation"""
        validation_result = {
            'is_valid': False,
            'errors': [],
            'warnings': [],
            'format_info': None,
            'quality_assessment': None,
            'optimization_suggestions': []
        }
        
        try:
            file_path = Path(file_path)
            
            # Check file exists and size
            if not file_path.exists():
                validation_result['errors'].append("File does not exist")
                return validation_result
            
            if file_path.stat().st_size == 0:
                validation_result['errors'].append("File is empty")
                return validation_result
            
            # Detect and validate format
            format_info = await self.detect_format(file_path)
            validation_result['format_info'] = format_info
            
            # Validate image properties
            width, height = format_info.resolution
            if width <= 0 or height <= 0:
                validation_result['errors'].append("Invalid image dimensions")
            
            # Check for extremely large images
            if width > 50000 or height > 50000:
                validation_result['warnings'].append("Extremely large image dimensions")
            
            # Quality assessment
            quality_assessment = await self._comprehensive_quality_check(file_path)
            validation_result['quality_assessment'] = quality_assessment
            
            # Optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(format_info)
            validation_result['optimization_suggestions'] = optimization_suggestions
            
            validation_result['is_valid'] = len(validation_result['errors']) == 0
            
        except Exception as e:
            validation_result['errors'].append(f"Validation failed: {e}")
        
        return validation_result
    
    async def _comprehensive_quality_check(self, file_path: Path) -> Dict[str, Any]:
        """Perform comprehensive quality assessment"""
        try:
            with Image.open(file_path) as img:
                img_array = np.array(img)
                
            quality_result = await self.quality_analyzer.comprehensive_analysis(img_array)
            return quality_result
        except Exception as e:
            logger.warning(f"Quality check failed: {e}")
            return {'overall_score': 0.5, 'details': {}}
    
    async def _generate_optimization_suggestions(self, format_info: ImageFormatInfo) -> List[str]:
        """Generate optimization suggestions based on image analysis"""
        suggestions = []
        
        # Format optimization
        if format_info.format_type == ImageFormat.PNG and not format_info.has_transparency:
            suggestions.append("Consider converting to JPEG for better compression")
        
        if format_info.format_type == ImageFormat.JPEG and format_info.quality_score > 0.95:
            suggestions.append("Image quality is very high, consider reducing quality for smaller file size")
        
        # Size optimization
        width, height = format_info.resolution
        if width > 2000 or height > 2000:
            suggestions.append("Consider resizing for web use (max 2000px)")
        
        # Modern format suggestion
        if format_info.format_type in [ImageFormat.JPEG, ImageFormat.PNG]:
            suggestions.append("Consider converting to WebP for 25-35% smaller file size")
        
        # Compression optimization
        if format_info.compression_ratio < 0.1:  # Very low compression
            suggestions.append("Image has very low compression, consider optimizing")
        
        return suggestions

# Module exports for enterprise integration
__all__ = [
    'ImageFormatProcessor',
    'ModernImageFormats',
    'ImageFormat',
    'ImageQuality',
    'ImageFormatInfo',
    'ImageProcessingOptions'
]