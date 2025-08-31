"""
Image Processor - Enterprise Image Processing & Enhancement System
=================================================================

Advanced image processing system with AI-powered enhancement, format conversion,
quality optimization, and professional-grade image manipulation capabilities
for content creators and digital influencers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import cv2
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from datetime import datetime
import torch
import torchvision.transforms as transforms
from PIL import Image, ImageFilter, ImageEnhance, ExifTags, ImageOps, ImageDraw, ImageFont
import io
import hashlib
import base64
import os
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing

# Advanced image processing libraries
from skimage import measure, filters, restoration, exposure, segmentation, feature, morphology
from skimage.metrics import structural_similarity as ssim, peak_signal_noise_ratio as psnr
from sklearn.cluster import KMeans
import imagehash
import rawpy
from wand.image import Image as WandImage
from wand.color import Color
import face_recognition
import dlib

from ..base import BaseAgent, AgentStatus, AgentCapability
try:
    from core.exceptions import ImageProcessingError, ValidationError, SecurityError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ImageProcessingError, ValidationError, SecurityError = globals().get('ImageProcessingError, ValidationError, SecurityError', Exception)
from ...utils.performance_monitor import PerformanceMonitor
from ...security.watermark_manager import WatermarkManager
from ...utils.cache_manager import CacheManager
from .config import VisionAgentConfig, ProcessingMode

logger = logging.getLogger(__name__)

class ImageQuality(Enum):
    """Image quality assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair" 
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

class ProcessingLevel(Enum):
    """Image processing complexity levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    STUDIO = "studio"
    ENTERPRISE = "enterprise"

class EnhancementType(Enum):
    """Types of image enhancement"""
    AUTOMATIC = "automatic"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    MACRO = "macro"
    NIGHT_MODE = "night_mode"
    HDR = "hdr"
    ARTISTIC = "artistic"
    RESTORATION = "restoration"

@dataclass
class ImageMetrics:
    """Comprehensive image quality metrics"""
    resolution: Tuple[int, int]
    file_size_bytes: int
    format: str
    color_space: str
    bit_depth: int
    has_transparency: bool
    dpi: Tuple[int, int]
    aspect_ratio: float
    
    # Quality metrics
    blur_score: float
    noise_level: float
    brightness_score: float
    contrast_score: float
    saturation_score: float
    sharpness_score: float
    exposure_score: float
    
    # Advanced metrics
    dynamic_range: float
    color_temperature: float
    white_balance_score: float
    histogram_uniformity: float
    edge_density: float
    texture_complexity: float

@dataclass
class ProcessingResult:
    """Image processing operation result"""
    success: bool
    processed_image: Optional[np.ndarray] = None
    processing_time: float = 0.0
    operations_applied: List[str] = None
    quality_improvement: float = 0.0
    metrics: Optional[ImageMetrics] = None
    warnings: List[str] = None
    errors: List[str] = None

class ImageProcessor(BaseAgent):
    """
    Enterprise-grade image processing system providing comprehensive
    image manipulation, enhancement, quality assessment, and format conversion
    capabilities for professional content creation workflows.
    """
    
    def __init__(self, config: Optional[VisionAgentConfig] = None):
        super().__init__(
            agent_id="image_processor",
            name="Image Processor",
            version="2.1.0",
            capabilities=[
                AgentCapability.IMAGE_PROCESSING,
                AgentCapability.QUALITY_ASSESSMENT,
                AgentCapability.FORMAT_CONVERSION,
                AgentCapability.ENHANCEMENT,
                AgentCapability.RESTORATION,
                AgentCapability.WATERMARKING,
                AgentCapability.COMPRESSION
            ]
        )
        
        self.config = config or VisionAgentConfig()
        self.performance_monitor = PerformanceMonitor("image_processing")
        self.cache_manager = CacheManager("image_cache")
        self.watermark_manager = WatermarkManager()
        
        # Initialize thread and process pools
        self.thread_pool = ThreadPoolExecutor(max_workers=self.config.performance.cpu_threads or 4)
        self.process_pool = ProcessPoolExecutor(max_workers=2)
        
        # Processing configuration
        self.max_dimension = 8192
        self.min_dimension = 32
        self.max_file_size = self.config.security.max_file_size_mb * 1024 * 1024
        
        # Quality assessment thresholds
        self.quality_thresholds = {
            'blur_threshold_excellent': 500.0,
            'blur_threshold_good': 200.0,
            'blur_threshold_fair': 100.0,
            'noise_threshold_excellent': 20.0,
            'noise_threshold_good': 40.0,
            'noise_threshold_fair': 60.0,
            'brightness_optimal': (50, 200),
            'brightness_acceptable': (30, 225),
            'contrast_excellent': 0.8,
            'contrast_good': 0.5,
            'contrast_fair': 0.3,
            'sharpness_excellent': 0.8,
            'sharpness_good': 0.6,
            'sharpness_fair': 0.4
        }
        
        # Enhancement parameters
        self.enhancement_params = {
            'gaussian_blur_sigma': 1.0,
            'denoise_h': 10,
            'denoise_template_window_size': 7,
            'denoise_search_window_size': 21,
            'unsharp_mask_radius': 1.0,
            'unsharp_mask_amount': 150,
            'unsharp_mask_threshold': 3,
            'gamma_correction_range': (0.5, 2.5),
            'histogram_equalization_clip_limit': 3.0,
            'bilateral_filter_d': 9,
            'bilateral_filter_sigma_color': 75,
            'bilateral_filter_sigma_space': 75
        }
        
        # Advanced processing kernels
        self.kernels = {
            'sharpen_light': np.array([[0, -0.5, 0], [-0.5, 3, -0.5], [0, -0.5, 0]]),
            'sharpen_strong': np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]),
            'edge_detection': np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]),
            'emboss': np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]]),
            'motion_blur': np.ones((15, 15), dtype=np.float32) / 225
        }
        
        # Color space conversion matrices
        self.color_matrices = {
            'warm_filter': np.array([
                [1.1, 0.1, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 0.8]
            ]),
            'cool_filter': np.array([
                [0.8, 0.0, 0.0],
                [0.0, 1.0, 0.1],
                [0.0, 0.1, 1.1]
            ]),
            'vintage_filter': np.array([
                [1.0, 0.2, 0.1],
                [0.1, 0.9, 0.1],
                [0.1, 0.1, 0.7]
            ])
        }
        
        # Supported formats with their characteristics
        self.format_specs = {
            'JPEG': {'quality_range': (10, 100), 'supports_transparency': False, 'lossy': True},
            'PNG': {'quality_range': (0, 9), 'supports_transparency': True, 'lossy': False},
            'WEBP': {'quality_range': (0, 100), 'supports_transparency': True, 'lossy': True},
            'TIFF': {'quality_range': (1, 10), 'supports_transparency': True, 'lossy': False},
            'BMP': {'quality_range': (1, 1), 'supports_transparency': False, 'lossy': False},
            'GIF': {'quality_range': (1, 1), 'supports_transparency': True, 'lossy': True},
            'AVIF': {'quality_range': (0, 100), 'supports_transparency': True, 'lossy': True}
        }

    async def initialize(self) -> bool:
        """Initialize image processing components with advanced ML models"""
        try:
            logger.info("Initializing Enterprise Image Processor...")
            
            # Initialize device and GPU optimization
            self.device = torch.device("cuda" if torch.cuda.is_available() and 
                                     self.config.models['similarity'].gpu_acceleration else "cpu")
            
            if self.device.type == 'cuda':
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
                logger.info(f"GPU acceleration enabled: {torch.cuda.get_device_name(0)}")
            
            # Initialize deep learning models for enhancement
            self._init_enhancement_models()
            
            # Initialize face detection for portrait processing
            self._init_face_detection_models()
            
            # Initialize advanced transforms
            self._init_image_transforms()
            
            # Warm up models with sample data
            await self._warm_up_models()
            
            # Create processing directories
            self._ensure_directories()
            
            self.status = AgentStatus.READY
            logger.info("Image Processor initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Image Processor: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    def _init_enhancement_models(self):
        """Initialize AI models for image enhancement"""
        try:
            # Super-resolution model (ESRGAN)
            self.sr_model = None  # Would load actual ESRGAN model
            
            # Denoising model (DnCNN)
            self.denoise_model = None  # Would load actual DnCNN model
            
            # HDR enhancement model
            self.hdr_model = None  # Would load actual HDR model
            
            # Style transfer models
            self.style_models = {}  # Would load various artistic style models
            
            logger.info("Enhancement models initialized")
            
        except Exception as e:
            logger.warning(f"Some enhancement models could not be loaded: {e}")
    
    def _init_face_detection_models(self):
        """Initialize face detection and landmark models"""
        try:
            # Initialize dlib face detector
            self.face_detector = dlib.get_frontal_face_detector()
            
            # Initialize face landmark predictor (would need model file)
            try:
                self.landmark_predictor = dlib.shape_predictor(
                    "/models/shape_predictor_68_face_landmarks.dat"
                )
            except:
                self.landmark_predictor = None
                logger.warning("Face landmark model not available")
            
            logger.info("Face detection models initialized")
            
        except Exception as e:
            logger.warning(f"Face detection initialization failed: {e}")
            self.face_detector = None
            self.landmark_predictor = None
    
    def _init_image_transforms(self):
        """Initialize comprehensive image transform pipelines"""
        # Standard preprocessing transforms
        self.preprocess_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Enhancement transforms
        self.enhancement_transforms = {
            'normalize': transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
            'resize_high_quality': transforms.Resize((512, 512), antialias=True),
            'center_crop': transforms.CenterCrop(224),
            'random_crop': transforms.RandomCrop(256, padding=32),
            'horizontal_flip': transforms.RandomHorizontalFlip(0.5)
        }
        
        # Post-processing transforms
        self.postprocess_transform = transforms.Compose([
            transforms.Normalize(mean=[-0.485/0.229, -0.456/0.224, -0.406/0.225], 
                               std=[1/0.229, 1/0.224, 1/0.225])
        ])
    
    async def _warm_up_models(self):
        """Warm up models with sample data for optimal performance"""
        try:
            # Create dummy image for warm-up
            dummy_image = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
            
            # Warm up basic processing functions
            await self.assess_quality(dummy_image)
            
            logger.info("Model warm-up completed")
            
        except Exception as e:
            logger.warning(f"Model warm-up failed: {e}")
    
    def _ensure_directories(self):
        """Ensure all necessary directories exist"""
        directories = [
            self.config.storage.temp_path,
            self.config.storage.cache_path,
            self.config.storage.results_path,
            f"{self.config.storage.cache_path}/thumbnails",
            f"{self.config.storage.cache_path}/processed"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    async def process_image(self, 
                          image_input: Union[str, bytes, np.ndarray, Image.Image],
                          processing_level: ProcessingLevel = ProcessingLevel.STANDARD,
                          enhancement_type: EnhancementType = EnhancementType.AUTOMATIC,
                          custom_operations: Optional[List[str]] = None,
                          preserve_original: bool = True) -> ProcessingResult:
        """
        Process image with comprehensive enhancement and optimization
        
        Args:
            image_input: Input image (file path, bytes, array, or PIL Image)
            processing_level: Level of processing to apply
            enhancement_type: Type of enhancement to perform
            custom_operations: List of custom operations to apply
            preserve_original: Whether to preserve original image data
            
        Returns:
            ProcessingResult with processed image and metrics
        """
        start_time = time.time()
        
        try:
            # Load and validate image
            image_array, original_format = await self._load_image(image_input)
            
            if image_array is None:
                return ProcessingResult(
                    success=False,
                    errors=["Failed to load image"]
                )
            
            # Cache key for processed results
            cache_key = self._generate_cache_key(image_input, processing_level, enhancement_type)
            
            # Check cache first
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result and not self.config.performance.cache_enabled is False:
                logger.info("Returning cached processing result")
                return cached_result
            
            # Assess original image quality
            original_metrics = await self.assess_quality(image_array)
            
            # Apply processing pipeline based on level
            processed_image = await self._apply_processing_pipeline(
                image_array, processing_level, enhancement_type, custom_operations
            )
            
            # Assess processed image quality
            processed_metrics = await self.assess_quality(processed_image)
            
            # Calculate quality improvement
            quality_improvement = self._calculate_quality_improvement(
                original_metrics, processed_metrics
            )
            
            # Create result
            result = ProcessingResult(
                success=True,
                processed_image=processed_image,
                processing_time=time.time() - start_time,
                operations_applied=self._get_applied_operations(processing_level, enhancement_type),
                quality_improvement=quality_improvement,
                metrics=processed_metrics,
                warnings=[],
                errors=[]
            )
            
            # Cache result if appropriate
            if self.config.performance.cache_enabled and result.success:
                await self.cache_manager.set(cache_key, result, ttl=3600)
            
            # Record performance metrics
            await self.performance_monitor.record_metric(
                "image_processing_time", result.processing_time
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return ProcessingResult(
                success=False,
                processing_time=time.time() - start_time,
                errors=[str(e)]
            )
            
            self.status = AgentStatus.READY
            logger.info("Image Processor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Image Processor initialization failed: {e}")
            self.status = AgentStatus.ERROR
            return False

    async def process_image(
        self, 
        image_data: Union[np.ndarray, bytes, str],
        operations: List[str] = None,
        quality_target: str = "high",
        preserve_metadata: bool = True
    ) -> Dict[str, Any]:
        """
        Process image with specified operations
        
        Args:
            image_data: Image as numpy array, bytes, or file path
            operations: List of operations to perform
            quality_target: Target quality level
            preserve_metadata: Whether to preserve EXIF metadata
            
        Returns:
            Processing results with enhanced image and metrics
        """
        start_time = datetime.now()
        
        try:
            # Load and validate image
            image = await self._load_image(image_data)
            original_shape = image.shape
            
            # Extract metadata if needed
            metadata = {}
            if preserve_metadata and isinstance(image_data, str):
                metadata = await self._extract_image_metadata(image_data)
            
            # Assess initial quality
            initial_quality = await self._assess_image_quality(image)
            
            # Apply requested operations
            processed_image = image.copy()
            operation_results = {}
            
            async def _load_image(self, image_input: Union[str, bytes, np.ndarray, Image.Image]) -> Tuple[Optional[np.ndarray], str]:
        """Load image from various input formats with comprehensive validation"""
        try:
            original_format = "unknown"
            
            if isinstance(image_input, np.ndarray):
                if len(image_input.shape) == 3 and image_input.shape[2] in [1, 3, 4]:
                    return image_input, "array"
                else:
                    raise ValidationError("Invalid image array shape")
                    
            elif isinstance(image_input, Image.Image):
                image_array = np.array(image_input)
                if len(image_array.shape) == 2:
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2BGR)
                elif image_array.shape[2] == 4:  # RGBA
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2BGR)
                return image_array, image_input.format or "PIL"
                
            elif isinstance(image_input, bytes):
                # Validate file size
                if len(image_input) > self.max_file_size:
                    raise ValidationError(f"File size exceeds limit: {len(image_input)} bytes")
                
                # Decode image from bytes
                nparr = np.frombuffer(image_input, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    # Try with PIL as fallback
                    try:
                        pil_image = Image.open(io.BytesIO(image_input))
                        image = np.array(pil_image)
                        if len(image.shape) == 3 and image.shape[2] == 4:
                            image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
                        original_format = pil_image.format
                    except:
                        raise ImageProcessingError("Failed to decode image from bytes")
                
                return image, original_format
                
            elif isinstance(image_input, str):
                # Validate file path
                if not os.path.exists(image_input):
                    raise ValidationError(f"Image file not found: {image_input}")
                
                file_path = Path(image_input)
                if file_path.suffix.lower() not in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.gif']:
                    raise ValidationError(f"Unsupported image format: {file_path.suffix}")
                
                # Check file size
                if file_path.stat().st_size > self.max_file_size:
                    raise ValidationError(f"File size exceeds limit: {file_path.stat().st_size} bytes")
                
                # Load with OpenCV first
                image = cv2.imread(str(file_path), cv2.IMREAD_COLOR)
                original_format = file_path.suffix.upper()[1:]
                
                if image is None:
                    # Try with PIL as fallback
                    try:
                        with Image.open(file_path) as pil_image:
                            image = np.array(pil_image)
                            if len(image.shape) == 3 and image.shape[2] == 4:
                                image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
                            elif len(image.shape) == 2:
                                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
                            original_format = pil_image.format
                    except:
                        raise ImageProcessingError(f"Failed to load image from {image_input}")
                
                return image, original_format
            
            else:
                raise ValidationError("Unsupported image input type")
                
        except Exception as e:
            logger.error(f"Image loading failed: {e}")
            return None, "error"

    async def _apply_processing_pipeline(self,
                                       image: np.ndarray,
                                       processing_level: ProcessingLevel,
                                       enhancement_type: EnhancementType,
                                       custom_operations: Optional[List[str]] = None) -> np.ndarray:
        """Apply comprehensive processing pipeline based on level and type"""
        
        processed_image = image.copy()
        
        # Define operation sets for different processing levels
        operation_sets = {
            ProcessingLevel.BASIC: ['resize', 'brightness_contrast'],
            ProcessingLevel.STANDARD: ['resize', 'denoise', 'brightness_contrast', 'sharpen'],
            ProcessingLevel.PROFESSIONAL: [
                'resize', 'denoise', 'brightness_contrast', 'color_correction',
                'sharpen', 'histogram_equalization'
            ],
            ProcessingLevel.STUDIO: [
                'resize', 'advanced_denoise', 'brightness_contrast', 'color_correction',
                'unsharp_mask', 'histogram_equalization', 'local_enhancement'
            ],
            ProcessingLevel.ENTERPRISE: [
                'resize', 'ml_denoise', 'advanced_color_correction', 'hdr_tone_mapping',
                'detail_enhancement', 'adaptive_sharpening', 'professional_grading'
            ]
        }
        
        # Use custom operations if provided
        operations = custom_operations or operation_sets.get(processing_level, operation_sets[ProcessingLevel.STANDARD])
        
        # Apply operations sequentially
        for operation in operations:
            try:
                processed_image = await self._apply_single_operation(
                    processed_image, operation, enhancement_type
                )
            except Exception as e:
                logger.warning(f"Operation {operation} failed: {e}")
                continue
        
        return processed_image

    async def _apply_single_operation(self,
                                    image: np.ndarray,
                                    operation: str,
                                    enhancement_type: EnhancementType) -> np.ndarray:
        """Apply a single image processing operation"""
        
        if operation == 'resize':
            return await self._smart_resize(image)
        elif operation == 'denoise':
            return await self._denoise_image(image)
        elif operation == 'advanced_denoise':
            return await self._advanced_denoise(image)
        elif operation == 'ml_denoise':
            return await self._ml_denoise(image)
        elif operation == 'brightness_contrast':
            return await self._adjust_brightness_contrast(image, enhancement_type)
        elif operation == 'color_correction':
            return await self._color_correction(image)
        elif operation == 'advanced_color_correction':
            return await self._advanced_color_correction(image, enhancement_type)
        elif operation == 'sharpen':
            return await self._sharpen_image(image)
        elif operation == 'unsharp_mask':
            return await self._unsharp_mask(image)
        elif operation == 'adaptive_sharpening':
            return await self._adaptive_sharpen(image)
        elif operation == 'histogram_equalization':
            return await self._histogram_equalization(image)
        elif operation == 'local_enhancement':
            return await self._local_contrast_enhancement(image)
        elif operation == 'hdr_tone_mapping':
            return await self._hdr_tone_mapping(image)
        elif operation == 'detail_enhancement':
            return await self._enhance_details(image)
        elif operation == 'professional_grading':
            return await self._professional_color_grading(image, enhancement_type)
        else:
            logger.warning(f"Unknown operation: {operation}")
            return image

    async def _smart_resize(self, image: np.ndarray) -> np.ndarray:
        """Intelligent image resizing with quality preservation"""
        height, width = image.shape[:2]
        
        # Don't resize if already within acceptable range
        if width <= self.max_dimension and height <= self.max_dimension:
            return image
        
        # Calculate optimal dimensions
        if width > height:
            new_width = min(width, self.max_dimension)
            new_height = int((height * new_width) / width)
        else:
            new_height = min(height, self.max_dimension)
            new_width = int((width * new_height) / height)
        
        # Use high-quality interpolation
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        return resized

    async def _denoise_image(self, image: np.ndarray) -> np.ndarray:
        """Basic image denoising"""
        return cv2.fastNlMeansDenoisingColored(
            image,
            None,
            h=self.enhancement_params['denoise_h'],
            hColor=self.enhancement_params['denoise_h'],
            templateWindowSize=self.enhancement_params['denoise_template_window_size'],
            searchWindowSize=self.enhancement_params['denoise_search_window_size']
        )

    async def _advanced_denoise(self, image: np.ndarray) -> np.ndarray:
        """Advanced denoising using bilateral filter and morphological operations"""
        # Apply bilateral filter
        bilateral = cv2.bilateralFilter(
            image,
            d=self.enhancement_params['bilateral_filter_d'],
            sigmaColor=self.enhancement_params['bilateral_filter_sigma_color'],
            sigmaSpace=self.enhancement_params['bilateral_filter_sigma_space']
        )
        
        # Apply morphological operations for noise reduction
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        opened = cv2.morphologyEx(bilateral, cv2.MORPH_OPEN, kernel)
        
        return opened

    async def _ml_denoise(self, image: np.ndarray) -> np.ndarray:
        """ML-based denoising (placeholder for actual ML model)"""
        if self.denoise_model is not None:
            # Would apply actual ML denoising model
            pass
        
        # Fallback to advanced denoising
        return await self._advanced_denoise(image)

    async def _adjust_brightness_contrast(self, image: np.ndarray, enhancement_type: EnhancementType) -> np.ndarray:
        """Adjust brightness and contrast based on enhancement type"""
        
        # Convert to LAB color space for better control
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Calculate automatic adjustments based on histogram
        hist = cv2.calcHist([l], [0], None, [256], [0, 256])
        mean_brightness = np.mean(l)
        
        # Enhancement type specific adjustments
        if enhancement_type == EnhancementType.PORTRAIT:
            # Brighten skin tones
            alpha = 1.1  # Contrast
            beta = 10    # Brightness
        elif enhancement_type == EnhancementType.LANDSCAPE:
            # Enhance natural colors
            alpha = 1.2
            beta = 5
        elif enhancement_type == EnhancementType.NIGHT_MODE:
            # Significant brightening
            alpha = 1.3
            beta = 20
        else:  # AUTOMATIC
            # Automatic adjustment based on image characteristics
            if mean_brightness < 100:
                alpha, beta = 1.2, 15
            elif mean_brightness > 180:
                alpha, beta = 0.9, -10
            else:
                alpha, beta = 1.0, 0
        
        # Apply CLAHE for local contrast enhancement
        clahe = cv2.createCLAHE(
            clipLimit=self.enhancement_params['histogram_equalization_clip_limit'],
            tileGridSize=(8, 8)
        )
        l_enhanced = clahe.apply(l)
        
        # Apply global brightness/contrast adjustment
        l_final = cv2.convertScaleAbs(l_enhanced, alpha=alpha, beta=beta)
        
        # Merge channels back
        enhanced_lab = cv2.merge([l_final, a, b])
        enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        return enhanced_bgr

    async def _color_correction(self, image: np.ndarray) -> np.ndarray:
        """Basic color correction and white balance"""
        
        # Simple gray world white balance
        result = image.copy().astype(np.float32)
        
        for i in range(3):
            channel_mean = np.mean(result[:, :, i])
            overall_mean = np.mean(result)
            if channel_mean > 0:
                result[:, :, i] = result[:, :, i] * (overall_mean / channel_mean)
        
        return np.clip(result, 0, 255).astype(np.uint8)

    async def _advanced_color_correction(self, image: np.ndarray, enhancement_type: EnhancementType) -> np.ndarray:
        """Advanced color correction with enhancement type specific processing"""
        
        # Convert to different color spaces for processing
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)
        
        if enhancement_type == EnhancementType.VINTAGE:
            # Apply vintage color grading
            s = s * 0.8  # Reduce saturation
            v = v * 0.95  # Slightly reduce brightness
            # Add warm tint
            h = np.where((h > 10) & (h < 25), h - 5, h)
        
        elif enhancement_type == EnhancementType.ARTISTIC:
            # Enhance saturation and contrast
            s = np.clip(s * 1.3, 0, 255)
            v = np.clip(v * 1.1, 0, 255)
        
        # Merge back and convert
        enhanced_hsv = cv2.merge([h, s, v])
        enhanced_bgr = cv2.cvtColor(enhanced_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return enhanced_bgr

    async def _sharpen_image(self, image: np.ndarray) -> np.ndarray:
        """Basic image sharpening"""
        kernel = self.kernels['sharpen_light']
        sharpened = cv2.filter2D(image, -1, kernel)
        return cv2.addWeighted(image, 0.7, sharpened, 0.3, 0)

    async def _unsharp_mask(self, image: np.ndarray) -> np.ndarray:
        """Unsharp masking for professional sharpening"""
        
        # Create Gaussian blur
        blurred = cv2.GaussianBlur(
            image, 
            (0, 0), 
            self.enhancement_params['unsharp_mask_radius']
        )
        
        # Create mask
        mask = cv2.subtract(image, blurred)
        
        # Apply sharpening
        sharpened = cv2.addWeighted(
            image, 
            1.0, 
            mask, 
            self.enhancement_params['unsharp_mask_amount'] / 100.0, 
            0
        )
        
        return sharpened

    async def _adaptive_sharpen(self, image: np.ndarray) -> np.ndarray:
        """Adaptive sharpening based on local image characteristics"""
        
        # Calculate local variance to identify areas needing sharpening
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        local_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Adjust sharpening strength based on content
        if local_var < 100:  # Low detail image
            strength = 1.5
        elif local_var > 500:  # High detail image
            strength = 0.5
        else:
            strength = 1.0
        
        # Apply adaptive unsharp mask
        sigma = self.enhancement_params['unsharp_mask_radius'] / strength
        blurred = cv2.GaussianBlur(image, (0, 0), sigma)
        mask = cv2.subtract(image, blurred)
        
        sharpened = cv2.addWeighted(
            image, 1.0, mask, 
            (self.enhancement_params['unsharp_mask_amount'] * strength) / 100.0, 
            0
        )
        
        return sharpened

    async def _histogram_equalization(self, image: np.ndarray) -> np.ndarray:
        """Histogram equalization for contrast enhancement"""
        
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(
            clipLimit=self.enhancement_params['histogram_equalization_clip_limit'],
            tileGridSize=(8, 8)
        )
        l_eq = clahe.apply(l)
        
        # Merge and convert back
        enhanced_lab = cv2.merge([l_eq, a, b])
        enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        
        return enhanced_bgr

    async def _local_contrast_enhancement(self, image: np.ndarray) -> np.ndarray:
        """Local contrast enhancement using guided filter"""
        
        # Convert to float for processing
        img_float = image.astype(np.float32) / 255.0
        
        # Apply guided filter (simplified version)
        # This would normally use a proper guided filter implementation
        enhanced = cv2.detailEnhance(image, sigma_s=10, sigma_r=0.15)
        
        return enhanced

    async def _hdr_tone_mapping(self, image: np.ndarray) -> np.ndarray:
        """HDR tone mapping for high dynamic range enhancement"""
        
        # Create HDR image (single image case)
        img_float = image.astype(np.float32) / 255.0
        
        # Apply Reinhard tone mapping
        tonemap = cv2.createTonemapReinhard(gamma=2.2, intensity=0.0, light_adapt=1.0, color_adapt=0.0)
        ldr = tonemap.process(img_float)
        
        # Convert back to 8-bit
        result = np.clip(ldr * 255, 0, 255).astype(np.uint8)
        
        return result

    async def _enhance_details(self, image: np.ndarray) -> np.ndarray:
        """Enhance fine details in the image"""
        
        # Edge-preserving smoothing
        smooth = cv2.edgePreservingFilter(image, flags=1, sigma_s=50, sigma_r=0.4)
        
        # Create detail layer
        details = cv2.subtract(image, smooth)
        
        # Enhance details
        enhanced_details = cv2.multiply(details, 1.5)
        
        # Add back to smooth image
        result = cv2.add(smooth, enhanced_details)
        
        return result

    async def _professional_color_grading(self, image: np.ndarray, enhancement_type: EnhancementType) -> np.ndarray:
        """Professional color grading based on enhancement type"""
        
        if enhancement_type == EnhancementType.PORTRAIT:
            # Warm, pleasing skin tones
            return self._apply_color_matrix(image, self.color_matrices['warm_filter'])
        elif enhancement_type == EnhancementType.LANDSCAPE:
            # Enhanced natural colors
            return self._apply_color_matrix(image, self.color_matrices['cool_filter'])
        elif enhancement_type == EnhancementType.ARTISTIC:
            # Stylized look
            return self._apply_color_matrix(image, self.color_matrices['vintage_filter'])
        else:
            return image

    def _apply_color_matrix(self, image: np.ndarray, color_matrix: np.ndarray) -> np.ndarray:
        """Apply color transformation matrix"""
        
        # Reshape image for matrix multiplication
        img_reshaped = image.reshape(-1, 3).astype(np.float32)
        
        # Apply color matrix
        transformed = np.dot(img_reshaped, color_matrix.T)
        
        # Reshape back and clip values
        result = np.clip(transformed, 0, 255).astype(np.uint8)
        return result.reshape(image.shape)

    def _generate_cache_key(self, image_input: Any, processing_level: ProcessingLevel, enhancement_type: EnhancementType) -> str:
        """Generate cache key for processing results"""
        
        # Create hash from input
        if isinstance(image_input, str):
            input_hash = hashlib.md5(image_input.encode()).hexdigest()
        elif isinstance(image_input, bytes):
            input_hash = hashlib.md5(image_input).hexdigest()[:16]
        else:
            input_hash = hashlib.md5(str(image_input).encode()).hexdigest()[:16]
        
        return f"img_proc_{input_hash}_{processing_level.value}_{enhancement_type.value}"

    def _get_applied_operations(self, processing_level: ProcessingLevel, enhancement_type: EnhancementType) -> List[str]:
        """Get list of operations that would be applied"""
        
        operation_sets = {
            ProcessingLevel.BASIC: ['resize', 'brightness_contrast'],
            ProcessingLevel.STANDARD: ['resize', 'denoise', 'brightness_contrast', 'sharpen'],
            ProcessingLevel.PROFESSIONAL: [
                'resize', 'denoise', 'brightness_contrast', 'color_correction',
                'sharpen', 'histogram_equalization'
            ],
            ProcessingLevel.STUDIO: [
                'resize', 'advanced_denoise', 'brightness_contrast', 'color_correction',
                'unsharp_mask', 'histogram_equalization', 'local_enhancement'
            ],
            ProcessingLevel.ENTERPRISE: [
                'resize', 'ml_denoise', 'advanced_color_correction', 'hdr_tone_mapping',
                'detail_enhancement', 'adaptive_sharpening', 'professional_grading'
            ]
        }
        
        return operation_sets.get(processing_level, operation_sets[ProcessingLevel.STANDARD])

    def _calculate_quality_improvement(self, original_metrics: ImageMetrics, processed_metrics: ImageMetrics) -> float:
        """Calculate quality improvement score"""
        
        improvements = []
        
        # Compare key metrics
        if original_metrics.blur_score > 0:
            blur_improvement = (processed_metrics.blur_score - original_metrics.blur_score) / original_metrics.blur_score
            improvements.append(max(0, blur_improvement))
        
        if original_metrics.noise_level > 0:
            noise_improvement = (original_metrics.noise_level - processed_metrics.noise_level) / original_metrics.noise_level
            improvements.append(max(0, noise_improvement))
        
        if original_metrics.contrast_score > 0:
            contrast_improvement = (processed_metrics.contrast_score - original_metrics.contrast_score) / original_metrics.contrast_score
            improvements.append(max(0, contrast_improvement))
        
        return np.mean(improvements) if improvements else 0.0

    async def _load_image(self, image_data: Union[np.ndarray, bytes, str]) -> np.ndarray:
        """Load image from various input formats"""
        if isinstance(image_data, np.ndarray):
            return image_data
        elif isinstance(image_data, bytes):
            image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                raise ImageProcessingError("Failed to decode image from bytes")
            return image
        elif isinstance(image_data, str):
            image = cv2.imread(image_data, cv2.IMREAD_COLOR)
            if image is None:
                raise ImageProcessingError(f"Failed to load image from {image_data}")
            return image
        else:
            raise ValidationError("Unsupported image data format")

    async def _extract_image_metadata(self, image_path: str) -> Dict[str, Any]:
        """Extract comprehensive image metadata"""
        try:
            with Image.open(image_path) as img:
                metadata = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'has_transparency': 'transparency' in img.info
                }
                
                # Extract EXIF data
                if hasattr(img, '_getexif'):
                    exif_data = img._getexif()
                    if exif_data:
                        exif = {}
                        for tag_id, value in exif_data.items():
                            tag = ExifTags.TAGS.get(tag_id, tag_id)
                            exif[tag] = value
                        metadata['exif'] = exif
                
                return metadata
                
        except Exception as e:
            logger.warning(f"Failed to extract metadata: {e}")
            return {}

    async def _assess_image_quality(self, image: np.ndarray) -> Dict[str, Any]:
        """Comprehensive image quality assessment"""
        try:
            # Convert to grayscale for some calculations
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Blur detection using Laplacian variance
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Noise estimation
            noise_score = self._estimate_noise(gray)
            
            # Brightness assessment
            brightness = np.mean(gray)
            
            # Contrast assessment
            contrast = gray.std()
            
            # Sharpness assessment using gradient magnitude
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            sharpness = np.mean(np.sqrt(sobelx**2 + sobely**2))
            
            # Color distribution analysis
            color_diversity = self._analyze_color_distribution(image)
            
            # Overall quality score calculation
            blur_normalized = min(blur_score / self.quality_thresholds['blur_threshold'], 1.0)
            noise_normalized = max(0, 1.0 - noise_score / self.quality_thresholds['noise_threshold'])
            brightness_normalized = self._normalize_brightness(brightness)
            contrast_normalized = min(contrast / 100.0, 1.0)
            
            overall_score = np.mean([
                blur_normalized * 0.3,
                noise_normalized * 0.2,
                brightness_normalized * 0.2,
                contrast_normalized * 0.2,
                color_diversity * 0.1
            ])
            
            # Quality classification
            if overall_score >= 0.8:
                quality_class = ImageQuality.EXCELLENT
            elif overall_score >= 0.6:
                quality_class = ImageQuality.GOOD
            elif overall_score >= 0.4:
                quality_class = ImageQuality.FAIR
            else:
                quality_class = ImageQuality.POOR
            
            return {
                'overall_score': overall_score,
                'quality_class': quality_class,
                'blur_score': blur_score,
                'noise_score': noise_score,
                'brightness': brightness,
                'contrast': contrast,
                'sharpness': sharpness,
                'color_diversity': color_diversity,
                'recommendations': self._generate_quality_recommendations(
                    blur_score, noise_score, brightness, contrast
    async def assess_quality(self, image: np.ndarray) -> ImageMetrics:
        """
        Comprehensive image quality assessment with detailed metrics
        
        Args:
            image: Input image array
            
        Returns:
            ImageMetrics object with comprehensive quality assessment
        """
        try:
            # Basic image information
            height, width = image.shape[:2]
            channels = image.shape[2] if len(image.shape) == 3 else 1
            
            # Convert to different color spaces for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if channels == 3 else image
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) if channels == 3 else None
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB) if channels == 3 else None
            
            # === TECHNICAL METRICS ===
            
            # Blur detection using multiple methods
            blur_laplacian = cv2.Laplacian(gray, cv2.CV_64F).var()
            blur_sobel = self._calculate_sobel_variance(gray)
            blur_score = (blur_laplacian + blur_sobel) / 2
            
            # Noise estimation using different techniques
            noise_level = self._estimate_noise_level(gray)
            
            # Brightness analysis
            brightness_mean = np.mean(gray)
            brightness_std = np.std(gray)
            brightness_score = self._evaluate_brightness_quality(brightness_mean, brightness_std)
            
            # Contrast assessment
            contrast_rms = np.sqrt(np.mean((gray - brightness_mean) ** 2))
            contrast_michelson = self._calculate_michelson_contrast(gray)
            contrast_score = (contrast_rms / 128.0 + contrast_michelson) / 2
            
            # Sharpness evaluation
            sharpness_score = self._calculate_sharpness_score(gray)
            
            # Exposure analysis
            exposure_score = self._analyze_exposure(gray)
            
            # === COLOR ANALYSIS (if color image) ===
            if channels == 3:
                saturation_score = self._analyze_saturation(hsv)
                color_temperature = self._estimate_color_temperature(image)
                white_balance_score = self._evaluate_white_balance(image)
            else:
                saturation_score = 0.0
                color_temperature = 6500.0  # Neutral
                white_balance_score = 1.0
            
            # === ADVANCED METRICS ===
            
            # Dynamic range
            dynamic_range = self._calculate_dynamic_range(gray)
            
            # Histogram analysis
            histogram_uniformity = self._analyze_histogram_uniformity(gray)
            
            # Edge density and texture complexity
            edge_density = self._calculate_edge_density(gray)
            texture_complexity = self._calculate_texture_complexity(gray)
            
            # === FILE CHARACTERISTICS ===
            file_size_bytes = image.nbytes
            bit_depth = 8 if image.dtype == np.uint8 else 16 if image.dtype == np.uint16 else 32
            has_transparency = channels == 4
            aspect_ratio = width / height
            
            # Create comprehensive metrics object
            metrics = ImageMetrics(
                resolution=(width, height),
                file_size_bytes=file_size_bytes,
                format="array",  # Will be updated if loaded from file
                color_space="BGR" if channels == 3 else "GRAY",
                bit_depth=bit_depth,
                has_transparency=has_transparency,
                dpi=(72, 72),  # Default, will be updated if available
                aspect_ratio=aspect_ratio,
                
                # Quality metrics
                blur_score=blur_score,
                noise_level=noise_level,
                brightness_score=brightness_score,
                contrast_score=contrast_score,
                saturation_score=saturation_score,
                sharpness_score=sharpness_score,
                exposure_score=exposure_score,
                
                # Advanced metrics
                dynamic_range=dynamic_range,
                color_temperature=color_temperature,
                white_balance_score=white_balance_score,
                histogram_uniformity=histogram_uniformity,
                edge_density=edge_density,
                texture_complexity=texture_complexity
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            # Return basic metrics on failure
            return ImageMetrics(
                resolution=(image.shape[1], image.shape[0]),
                file_size_bytes=image.nbytes,
                format="unknown",
                color_space="unknown",
                bit_depth=8,
                has_transparency=False,
                dpi=(72, 72),
                aspect_ratio=1.0,
                blur_score=0.0,
                noise_level=0.0,
                brightness_score=0.5,
                contrast_score=0.5,
                saturation_score=0.5,
                sharpness_score=0.5,
                exposure_score=0.5,
                dynamic_range=128.0,
                color_temperature=6500.0,
                white_balance_score=1.0,
                histogram_uniformity=0.5,
                edge_density=0.5,
                texture_complexity=0.5
            )

    def _calculate_sobel_variance(self, gray_image: np.ndarray) -> float:
        """Calculate blur using Sobel operator variance"""
        sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        return np.var(sobel_magnitude)

    def _estimate_noise_level(self, gray_image: np.ndarray) -> float:
        """Estimate noise level using multiple methods"""
        
        # Method 1: High-frequency noise estimation
        noise_kernel = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]])
        noise_response = cv2.filter2D(gray_image.astype(np.float32), -1, noise_kernel)
        noise_std = np.std(noise_response)
        
        # Method 2: Wavelet-based noise estimation (simplified)
        # In a full implementation, you'd use actual wavelet transforms
        gaussian_blur = cv2.GaussianBlur(gray_image.astype(np.float32), (5, 5), 1.0)
        high_freq = gray_image.astype(np.float32) - gaussian_blur
        high_freq_std = np.std(high_freq)
        
        # Combine both methods
        noise_estimate = (noise_std + high_freq_std) / 2
        
        # Normalize to 0-100 scale
        return min(noise_estimate / 5.0, 100.0)

    def _evaluate_brightness_quality(self, brightness_mean: float, brightness_std: float) -> float:
        """Evaluate brightness quality (0-1 scale)"""
        
        # Optimal brightness range
        optimal_min, optimal_max = 80, 170
        acceptable_min, acceptable_max = 50, 200
        
        # Check if mean brightness is in optimal range
        if optimal_min <= brightness_mean <= optimal_max:
            brightness_quality = 1.0
        elif acceptable_min <= brightness_mean <= acceptable_max:
            # Linear interpolation for acceptable range
            if brightness_mean < optimal_min:
                brightness_quality = 0.5 + 0.5 * (brightness_mean - acceptable_min) / (optimal_min - acceptable_min)
            else:
                brightness_quality = 0.5 + 0.5 * (acceptable_max - brightness_mean) / (acceptable_max - optimal_max)
        else:
            # Poor brightness
            brightness_quality = 0.1
        
        # Adjust for brightness distribution (standard deviation)
        # Good images should have reasonable brightness variation
        if 20 <= brightness_std <= 60:
            distribution_quality = 1.0
        elif 10 <= brightness_std <= 80:
            distribution_quality = 0.7
        else:
            distribution_quality = 0.3
        
        return (brightness_quality + distribution_quality) / 2

    def _calculate_michelson_contrast(self, gray_image: np.ndarray) -> float:
        """Calculate Michelson contrast"""
        max_luminance = np.max(gray_image)
        min_luminance = np.min(gray_image)
        
        if max_luminance + min_luminance == 0:
            return 0.0
        
        return (max_luminance - min_luminance) / (max_luminance + min_luminance)

    def _calculate_sharpness_score(self, gray_image: np.ndarray) -> float:
        """Calculate comprehensive sharpness score"""
        
        # Method 1: Laplacian variance (edge-based)
        laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        
        # Method 2: Gradient magnitude
        sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.mean(np.sqrt(sobel_x**2 + sobel_y**2))
        
        # Method 3: Modified Laplacian
        kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
        modified_laplacian = cv2.filter2D(gray_image.astype(np.float32), -1, kernel)
        modified_laplacian_mean = np.mean(np.abs(modified_laplacian))
        
        # Combine methods and normalize
        sharpness_raw = (laplacian_var / 1000 + gradient_magnitude / 50 + modified_laplacian_mean / 20) / 3
        
        return min(sharpness_raw, 1.0)

    def _analyze_exposure(self, gray_image: np.ndarray) -> float:
        """Analyze exposure quality"""
        
        histogram = cv2.calcHist([gray_image], [0], None, [256], [0, 256]).flatten()
        
        # Check for clipping
        shadows_clipped = histogram[0] / histogram.sum() > 0.01  # More than 1% pure black
        highlights_clipped = histogram[255] / histogram.sum() > 0.01  # More than 1% pure white
        
        # Calculate histogram distribution
        total_pixels = histogram.sum()
        
        # Ideal distribution has most pixels in mid-tones
        midtone_range = histogram[64:192].sum() / total_pixels
        shadow_range = histogram[0:64].sum() / total_pixels
        highlight_range = histogram[192:256].sum() / total_pixels
        
        # Calculate exposure score
        exposure_score = 1.0
        
        if shadows_clipped:
            exposure_score -= 0.3
        if highlights_clipped:
            exposure_score -= 0.3
        
        # Reward balanced distribution
        if midtone_range > 0.4:  # Good midtone content
            exposure_score += 0.1
        
        # Penalize extreme distributions
        if shadow_range > 0.4 or highlight_range > 0.4:
            exposure_score -= 0.2
        
        return max(0.0, min(1.0, exposure_score))

    def _analyze_saturation(self, hsv_image: np.ndarray) -> float:
        """Analyze color saturation quality"""
        if hsv_image is None:
            return 0.0
        
        s_channel = hsv_image[:, :, 1]
        
        # Calculate mean saturation
        mean_saturation = np.mean(s_channel)
        std_saturation = np.std(s_channel)
        
        # Optimal saturation range (out of 255)
        optimal_min, optimal_max = 50, 150
        
        if optimal_min <= mean_saturation <= optimal_max:
            saturation_quality = 1.0
        elif mean_saturation < optimal_min:
            saturation_quality = 0.3 + 0.7 * (mean_saturation / optimal_min)
        else:
            saturation_quality = 1.0 - 0.5 * ((mean_saturation - optimal_max) / (255 - optimal_max))
        
        # Adjust for saturation variation
        if 20 <= std_saturation <= 50:
            variation_quality = 1.0
        else:
            variation_quality = 0.7
        
        return (saturation_quality + variation_quality) / 2

    def _estimate_color_temperature(self, image: np.ndarray) -> float:
        """Estimate color temperature in Kelvin"""
        
        # Calculate average RGB values
        b_mean = np.mean(image[:, :, 0])
        g_mean = np.mean(image[:, :, 1])
        r_mean = np.mean(image[:, :, 2])
        
        # Simple color temperature estimation
        if r_mean == 0 or b_mean == 0:
            return 6500.0  # Default daylight
        
        ratio = r_mean / b_mean
        
        # Approximate color temperature based on R/B ratio
        if ratio < 1.0:
            # Cooler (more blue)
            temp = 6500 + (1.0 - ratio) * 2000
        else:
            # Warmer (more red)  
            temp = 6500 - (ratio - 1.0) * 2000
        
        return max(2000, min(10000, temp))

    def _evaluate_white_balance(self, image: np.ndarray) -> float:
        """Evaluate white balance quality (0-1 scale)"""
        
        # Calculate channel means
        b_mean = np.mean(image[:, :, 0])
        g_mean = np.mean(image[:, :, 1])
        r_mean = np.mean(image[:, :, 2])
        
        # Calculate color cast
        total_mean = (r_mean + g_mean + b_mean) / 3
        
        if total_mean == 0:
            return 1.0
        
        r_deviation = abs(r_mean - total_mean) / total_mean
        g_deviation = abs(g_mean - total_mean) / total_mean
        b_deviation = abs(b_mean - total_mean) / total_mean
        
        max_deviation = max(r_deviation, g_deviation, b_deviation)
        
        # Good white balance has minimal color cast
        if max_deviation < 0.05:
            return 1.0
        elif max_deviation < 0.1:
            return 0.8
        elif max_deviation < 0.2:
            return 0.6
        else:
            return 0.3

    def _calculate_dynamic_range(self, gray_image: np.ndarray) -> float:
        """Calculate dynamic range of the image"""
        return float(np.max(gray_image) - np.min(gray_image))

    def _analyze_histogram_uniformity(self, gray_image: np.ndarray) -> float:
        """Analyze histogram uniformity (0-1 scale)"""
        
        histogram = cv2.calcHist([gray_image], [0], None, [256], [0, 256]).flatten()
        
        # Normalize histogram
        histogram_norm = histogram / histogram.sum()
        
        # Calculate entropy (higher entropy = more uniform)
        entropy = -np.sum(histogram_norm[histogram_norm > 0] * np.log2(histogram_norm[histogram_norm > 0]))
        
        # Normalize entropy to 0-1 scale (max entropy for uniform is log2(256) = 8)
        return entropy / 8.0

    def _calculate_edge_density(self, gray_image: np.ndarray) -> float:
        """Calculate edge density as a texture measure"""
        
        # Use Canny edge detection
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Calculate edge density
        edge_pixels = np.sum(edges > 0)
        total_pixels = gray_image.shape[0] * gray_image.shape[1]
        
        return edge_pixels / total_pixels

    def _calculate_texture_complexity(self, gray_image: np.ndarray) -> float:
        """Calculate texture complexity using Local Binary Pattern concept"""
        
        # Simple texture measure using standard deviation in local windows
        kernel_size = 5
        kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)
        
        # Calculate local mean
        local_mean = cv2.filter2D(gray_image.astype(np.float32), -1, kernel)
        
        # Calculate local variance
        local_variance = cv2.filter2D((gray_image.astype(np.float32) - local_mean)**2, -1, kernel)
        
        # Mean variance as texture complexity measure
        texture_complexity = np.mean(local_variance) / (255**2)  # Normalize
        
        return min(texture_complexity, 1.0)

    async def convert_format(self, 
                           image: np.ndarray,
                           target_format: str,
                           quality: int = 95,
                           optimize: bool = True) -> bytes:
        """
        Convert image to target format with optimization
        
        Args:
            image: Input image array
            target_format: Target format (JPEG, PNG, WEBP, etc.)
            quality: Compression quality (format dependent)
            optimize: Enable optimization
            
        Returns:
            Converted image as bytes
        """
        try:
            # Convert from BGR to RGB for PIL
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            # Create PIL image
            pil_image = Image.fromarray(image_rgb)
            
            # Create output buffer
            output_buffer = io.BytesIO()
            
            # Format-specific conversion
            target_format = target_format.upper()
            
            if target_format in ['JPEG', 'JPG']:
                # JPEG conversion
                if pil_image.mode in ('RGBA', 'LA', 'P'):
                    # Convert to RGB for JPEG (no transparency support)
                    pil_image = pil_image.convert('RGB')
                
                pil_image.save(
                    output_buffer,
                    format='JPEG',
                    quality=quality,
                    optimize=optimize,
                    progressive=True if optimize else False
                )
                
            elif target_format == 'PNG':
                # PNG conversion
                pil_image.save(
                    output_buffer,
                    format='PNG',
                    optimize=optimize,
                    compress_level=9 - (quality // 11) if quality < 100 else 6
                )
                
            elif target_format == 'WEBP':
                # WebP conversion
                pil_image.save(
                    output_buffer,
                    format='WEBP',
                    quality=quality,
                    optimize=optimize,
                    lossless=quality == 100
                )
                
            elif target_format == 'TIFF':
                # TIFF conversion
                pil_image.save(
                    output_buffer,
                    format='TIFF',
                    compression='tiff_lzw' if optimize else None
                )
                
            else:
                # Default conversion
                pil_image.save(output_buffer, format=target_format)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            raise ImageProcessingError(f"Failed to convert to {target_format}: {e}")

    async def generate_fingerprint(self, image: np.ndarray) -> str:
        """
        Generate unique fingerprint for image content
        
        Args:
            image: Input image array
            
        Returns:
            Unique fingerprint string
        """
        try:
            # Convert to PIL Image for hashing
            if len(image.shape) == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            pil_image = Image.fromarray(image_rgb)
            
            # Generate multiple hash types
            ahash = str(imagehash.average_hash(pil_image, hash_size=16))
            phash = str(imagehash.phash(pil_image, hash_size=16))
            dhash = str(imagehash.dhash(pil_image, hash_size=16))
            whash = str(imagehash.whash(pil_image, hash_size=16))
            
            # Combine hashes for robust fingerprint
            combined_hash = f"{ahash}:{phash}:{dhash}:{whash}"
            
            # Generate SHA-256 hash of combined hashes
            fingerprint = hashlib.sha256(combined_hash.encode()).hexdigest()
            
            return fingerprint
            
        except Exception as e:
            logger.error(f"Fingerprint generation failed: {e}")
            return hashlib.md5(str(time.time()).encode()).hexdigest()

    async def batch_process(self,
                           images: List[Union[str, bytes, np.ndarray]],
                           processing_level: ProcessingLevel = ProcessingLevel.STANDARD,
                           enhancement_type: EnhancementType = EnhancementType.AUTOMATIC,
                           max_concurrent: Optional[int] = None) -> List[ProcessingResult]:
        """
        Process multiple images concurrently
        
        Args:
            images: List of images to process
            processing_level: Processing level to apply
            enhancement_type: Enhancement type to use
            max_concurrent: Maximum concurrent processes
            
        Returns:
            List of processing results
        """
        max_concurrent = max_concurrent or self.config.performance.max_concurrent_tasks
        
        # Create semaphore to limit concurrent processing
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single(image_input):
            async with semaphore:
                return await self.process_image(image_input, processing_level, enhancement_type)
        
        # Process all images concurrently
        tasks = [process_single(image) for image in images]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch processing failed for image {i}: {result}")
                processed_results.append(ProcessingResult(
                    success=False,
                    errors=[str(result)]
                ))
            else:
                processed_results.append(result)
        
        return processed_results

    async def cleanup(self):
        """Cleanup resources and temporary files"""
        try:
            # Close thread and process pools
            if hasattr(self, 'thread_pool'):
                self.thread_pool.shutdown(wait=True)
            
            if hasattr(self, 'process_pool'):
                self.process_pool.shutdown(wait=True)
            
            # Clear caches
            if hasattr(self, 'cache_manager'):
                await self.cache_manager.clear()
            
            # Clean temporary files
            temp_path = Path(self.config.storage.temp_path)
            if temp_path.exists():
                for file in temp_path.glob("*"):
                    try:
                        file.unlink()
                    except:
                        pass
            
            logger.info("Image Processor cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    async def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            'status': self.status.value,
            'version': self.version,
            'device': str(self.device) if hasattr(self, 'device') else 'unknown',
            'supported_formats': list(self.format_specs.keys()),
            'cache_enabled': self.config.performance.cache_enabled,
            'max_concurrent': self.config.performance.max_concurrent_tasks,
            'processing_capabilities': [cap.value for cap in self.capabilities]
        }
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return {'overall_score': 0.0, 'quality_class': ImageQuality.POOR, 'error': str(e)}

    def _estimate_noise(self, gray_image: np.ndarray) -> float:
        """Estimate noise level in grayscale image"""
        # Using Sobel operator to estimate noise
        sobelx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        # Standard deviation of gradient as noise estimate
        return np.std(gradient_magnitude)

    def _analyze_color_distribution(self, image: np.ndarray) -> float:
        """Analyze color distribution diversity"""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Calculate histogram for hue channel
        hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        
        # Normalize histogram
        hist_norm = hist / np.sum(hist)
        
        # Calculate entropy as measure of color diversity
        entropy = -np.sum(hist_norm * np.log2(hist_norm + 1e-7))
        
        # Normalize to 0-1 range
        return min(entropy / 8.0, 1.0)

    def _normalize_brightness(self, brightness: float) -> float:
        """Normalize brightness score"""
        optimal_brightness = 128  # Middle gray
        distance_from_optimal = abs(brightness - optimal_brightness)
        return max(0, 1.0 - distance_from_optimal / 128.0)

    def _generate_quality_recommendations(
        self, 
        blur_score: float, 
        noise_score: float, 
        brightness: float, 
        contrast: float
    ) -> List[str]:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        if blur_score < self.quality_thresholds['blur_threshold']:
            recommendations.append("Apply sharpening filter to reduce blur")
        
        if noise_score > self.quality_thresholds['noise_threshold']:
            recommendations.append("Apply noise reduction filter")
        
        if brightness < self.quality_thresholds['brightness_range'][0]:
            recommendations.append("Increase brightness")
        elif brightness > self.quality_thresholds['brightness_range'][1]:
            recommendations.append("Decrease brightness")
        
        if contrast < self.quality_thresholds['contrast_min'] * 100:
            recommendations.append("Enhance contrast")
        
        return recommendations

    async def _apply_image_operation(
        self, 
        image: np.ndarray, 
        operation: str, 
        quality_target: str
    ) -> Dict[str, Any]:
        """Apply specific image operation"""
        try:
            operation_start = datetime.now()
            
            if operation == 'enhance':
                result_image = await self._enhance_image(image, quality_target)
            elif operation == 'denoise':
                result_image = await self._denoise_image(image)
            elif operation == 'sharpen':
                result_image = await self._sharpen_image(image)
            elif operation == 'brightness':
                result_image = await self._adjust_brightness(image)
            elif operation == 'contrast':
                result_image = await self._enhance_contrast(image)
            elif operation == 'color_correct':
                result_image = await self._color_correction(image)
            elif operation == 'resize':
                result_image = await self._intelligent_resize(image, quality_target)
            elif operation == 'watermark':
                result_image = await self._apply_watermark(image)
            else:
                logger.warning(f"Unknown operation: {operation}")
                return {'image': image, 'applied': False, 'error': 'Unknown operation'}
            
            processing_time = (datetime.now() - operation_start).total_seconds()
            
            return {
                'image': result_image,
                'applied': True,
                'processing_time': processing_time,
                'operation': operation
            }
            
        except Exception as e:
            logger.error(f"Operation {operation} failed: {e}")
            return {'image': image, 'applied': False, 'error': str(e)}

    async def _enhance_image(self, image: np.ndarray, quality_target: str) -> np.ndarray:
        """Apply comprehensive image enhancement"""
        enhanced = image.copy()
        
        # Apply histogram equalization for better contrast
        if len(image.shape) == 3:
            # Convert to YUV and equalize Y channel
            yuv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2YUV)
            yuv[:,:,0] = cv2.equalizeHist(yuv[:,:,0])
            enhanced = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            enhanced = cv2.equalizeHist(enhanced)
        
        # Apply gamma correction based on brightness
        gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        if mean_brightness < 100:
            gamma = 0.7  # Brighten dark images
        elif mean_brightness > 150:
            gamma = 1.3  # Darken bright images
        else:
            gamma = 1.0  # No gamma correction needed
        
        if gamma != 1.0:
            enhanced = np.power(enhanced / 255.0, gamma) * 255.0
            enhanced = np.uint8(enhanced)
        
        return enhanced

    async def _denoise_image(self, image: np.ndarray) -> np.ndarray:
        """Apply advanced noise reduction"""
        # Use Non-Local Means Denoising
        if len(image.shape) == 3:
            denoised = cv2.fastNlMeansDenoisingColored(
                image,
                None,
                h=self.enhancement_params['denoise_h'],
                hColor=self.enhancement_params['denoise_h'],
                templateWindowSize=self.enhancement_params['denoise_template_window_size'],
                searchWindowSize=self.enhancement_params['denoise_search_window_size']
            )
        else:
            denoised = cv2.fastNlMeansDenoising(
                image,
                None,
                h=self.enhancement_params['denoise_h'],
                templateWindowSize=self.enhancement_params['denoise_template_window_size'],
                searchWindowSize=self.enhancement_params['denoise_search_window_size']
            )
        
        return denoised

    async def _sharpen_image(self, image: np.ndarray) -> np.ndarray:
        """Apply intelligent sharpening"""
        # Use unsharp masking for better results
        gaussian_blur = cv2.GaussianBlur(image, (9, 9), 2.0)
        sharpened = cv2.addWeighted(image, 1.5, gaussian_blur, -0.5, 0)
        
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    async def _adjust_brightness(self, image: np.ndarray) -> np.ndarray:
        """Intelligently adjust brightness"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        # Calculate adjustment needed
        target_brightness = 128
        adjustment = target_brightness - mean_brightness
        
        # Apply adjustment with limiting
        adjusted = cv2.add(image, np.ones(image.shape, dtype=np.uint8) * int(adjustment * 0.5))
        
        return adjusted

    async def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE"""
        if len(image.shape) == 3:
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            lab[:,:,0] = clahe.apply(lab[:,:,0])
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        else:
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(image)
        
        return enhanced

    async def _color_correction(self, image: np.ndarray) -> np.ndarray:
        """Apply automatic color correction"""
        # Convert to LAB color space for better color correction
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Apply white balance correction
        l_channel = lab[:,:,0]
        a_channel = lab[:,:,1]
        b_channel = lab[:,:,2]
        
        # Normalize A and B channels
        a_mean = np.mean(a_channel)
        b_mean = np.mean(b_channel)
        
        a_channel = a_channel - (a_mean - 128)
        b_channel = b_channel - (b_mean - 128)
        
        lab[:,:,1] = np.clip(a_channel, 0, 255)
        lab[:,:,2] = np.clip(b_channel, 0, 255)
        
        corrected = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        return corrected

    async def _intelligent_resize(self, image: np.ndarray, quality_target: str) -> np.ndarray:
        """Intelligent resizing with quality preservation"""
        height, width = image.shape[:2]
        
        # Determine target size based on quality target
        if quality_target == "high":
            max_size = 2048
        elif quality_target == "medium":
            max_size = 1024
        else:
            max_size = 512
        
        # Only resize if image is larger than target
        if max(width, height) > max_size:
            if width > height:
                new_width = max_size
                new_height = int(height * (max_size / width))
            else:
                new_height = max_size
                new_width = int(width * (max_size / height))
            
            # Use high-quality interpolation
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            return resized
        
        return image

    async def _apply_watermark(self, image: np.ndarray) -> np.ndarray:
        """Apply watermark for content protection"""
        return await self.watermark_manager.apply_watermark(image)

    async def _generate_image_hash(self, image: np.ndarray) -> str:
        """Generate perceptual hash for image fingerprinting"""
        # Convert to PIL Image for hashing
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        # Generate multiple hash types for better matching
        dhash = str(imagehash.dhash(pil_image))
        phash = str(imagehash.phash(pil_image))
        whash = str(imagehash.whash(pil_image))
        
        # Combine hashes
        combined_hash = f"{dhash}:{phash}:{whash}"
        
        # Generate SHA256 hash of the combined hash
        return hashlib.sha256(combined_hash.encode()).hexdigest()

    def _calculate_size_reduction(
        self, 
        original: np.ndarray, 
        processed: np.ndarray
    ) -> Dict[str, Any]:
        """Calculate file size reduction metrics"""
        original_size = original.nbytes
        processed_size = processed.nbytes
        
        reduction_bytes = original_size - processed_size
        reduction_percent = (reduction_bytes / original_size) * 100 if original_size > 0 else 0
        
        return {
            'original_bytes': original_size,
            'processed_bytes': processed_size,
            'reduction_bytes': reduction_bytes,
            'reduction_percent': reduction_percent
        }

    async def batch_process_images(
        self, 
        image_list: List[Union[str, np.ndarray, bytes]],
        operations: List[str] = None,
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """Process multiple images concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single_image(image_data):
            async with semaphore:
                return await self.process_image(image_data, operations)
        
        tasks = [process_single_image(img) for img in image_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [result if not isinstance(result, Exception) 
                else {'status': 'error', 'error': str(result)} 
                for result in results]

    async def convert_format(
        self, 
        image: np.ndarray, 
        target_format: str,
        quality: int = 95
    ) -> bytes:
        """Convert image to different format"""
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Save to bytes buffer
            buffer = io.BytesIO()
            
            if target_format.lower() in ['jpg', 'jpeg']:
                pil_image.save(buffer, format='JPEG', quality=quality, optimize=True)
            elif target_format.lower() == 'png':
                pil_image.save(buffer, format='PNG', optimize=True)
            elif target_format.lower() == 'webp':
                pil_image.save(buffer, format='WEBP', quality=quality, method=6)
            else:
                pil_image.save(buffer, format=target_format.upper())
            
            return buffer.getvalue()
            
        except Exception as e:
            raise ImageProcessingError(f"Format conversion failed: {e}")

    async def assess_quality(self, image: np.ndarray) -> Dict[str, Any]:
        """Public method for image quality assessment"""
        return await self._assess_image_quality(image)

    async def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            await self.performance_monitor.close()
            await self.watermark_manager.cleanup()
            logger.info("Image Processor cleanup completed")
        except Exception as e:
            logger.error(f"Image Processor cleanup failed: {e}")

    def get_supported_operations(self) -> List[str]:
        """Get list of supported image operations"""
        return [
            'enhance', 'denoise', 'sharpen', 'brightness', 
            'contrast', 'color_correct', 'resize', 'watermark'
        ]
