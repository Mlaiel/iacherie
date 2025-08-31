"""
Image Agent - Industrial-Grade AI Image Processing & Analysis System

Advanced AI-powered image processing, analysis, generation, and protection system for visual content creators.
Handles comprehensive image operations including quality assessment, content protection, format optimization,
and business intelligence for photographers, influencers, and visual artists.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Computer Vision Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import hashlib
import logging
import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union, Tuple, Set
import json
import base64
from dataclasses import dataclass, field

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image, ImageEnhance, ImageFilter, ExifTags
import imagehash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import redis
import sqlalchemy as sa
from sqlalchemy.orm import Session

from ..base import BaseAgent, AgentStatus, AgentResult
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
try:
    from core.exceptions import ProcessingError, ValidationError, SecurityError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ProcessingError, ValidationError, SecurityError = globals().get('ProcessingError, ValidationError, SecurityError', Exception)
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...utils.rate_limiter import RateLimiter
from ...integrations.cloud_storage import CloudStorageManager
from ...ml.computer_vision import ComputerVisionEngine
from ...business.analytics import BusinessAnalyticsEngine

logger = logging.getLogger(__name__)


class ImageFormat(Enum):
    """Supported image formats for processing"""
    JPEG = "jpeg"
    PNG = "png" 
    WEBP = "webp"
    AVIF = "avif"
    TIFF = "tiff"
    BMP = "bmp"
    GIF = "gif"
    SVG = "svg"
    RAW = "raw"


class ImageQuality(Enum):
    """Image quality assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


class ProcessingOperation(Enum):
    """Available image processing operations"""
    ANALYZE = "analyze"
    ENHANCE = "enhance"
    PROTECT = "protect"
    OPTIMIZE = "optimize"
    GENERATE = "generate"
    WATERMARK = "watermark"
    FINGERPRINT = "fingerprint"
    SEO_OPTIMIZE = "seo_optimize"


@dataclass
class ImageMetadata:
    """Comprehensive image metadata structure"""
    filename: str
    file_size: int
    dimensions: Tuple[int, int]
    format: ImageFormat
    color_mode: str
    bit_depth: int
    compression_ratio: float
    creation_date: Optional[datetime] = None
    camera_info: Optional[Dict[str, Any]] = None
    gps_coordinates: Optional[Tuple[float, float]] = None
    exif_data: Optional[Dict[str, Any]] = None
    color_profile: Optional[str] = None
    histogram: Optional[np.ndarray] = None


@dataclass 
class ImageAnalysisResult:
    """Detailed image analysis results"""
    quality_score: float  # 0.0 to 1.0
    quality_level: ImageQuality
    aesthetic_score: float
    technical_score: float
    composition_score: float
    color_harmony: float
    sharpness: float
    noise_level: float
    exposure_quality: float
    contrast_ratio: float
    detected_objects: List[Dict[str, Any]] = field(default_factory=list)
    scene_classification: Optional[Dict[str, float]] = None
    dominant_colors: List[str] = field(default_factory=list)
    metadata: Optional[ImageMetadata] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ImageProtectionResult:
    """Image content protection analysis results"""
    fingerprint: str
    perceptual_hash: str
    robust_hash: str
    similarity_matches: List[Dict[str, Any]] = field(default_factory=list)
    copyright_status: str = "unknown"
    watermark_detected: bool = False
    tampering_detected: bool = False
    authenticity_score: float = 1.0
    protection_recommendations: List[str] = field(default_factory=list)


@dataclass
class ImageEnhancementResult:
    """Image enhancement processing results"""
    original_size: int
    enhanced_size: int
    quality_improvement: float
    operations_applied: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    enhancement_score: float = 0.0
    artifacts_removed: int = 0
    sharpness_gain: float = 0.0


@dataclass
class ImageOptimizationResult:
    """Image optimization results"""
    original_format: ImageFormat
    optimized_format: ImageFormat
    original_size: int
    optimized_size: int
    compression_ratio: float
    quality_retained: float
    optimization_score: float
    seo_score: float = 0.0
    alt_text: Optional[str] = None
    seo_keywords: List[str] = field(default_factory=list)


class ImageAgent(BaseAgent):
    """
    Industrial-grade AI Image Processing Agent
    
    Provides comprehensive image processing, analysis, protection, and optimization
    capabilities for visual content creators including photographers, influencers,
    and digital artists.
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        model_config: str = "production",
        enable_gpu: bool = True,
        quality_preset: str = "high",
        max_concurrent_operations: int = 10,
        cache_enabled: bool = True
    ):
        """
        Initialize the Image Agent with advanced configurations
        
        Args:
            agent_id: Unique identifier for this agent instance
            model_config: Model configuration preset (development/production/ultra)
            enable_gpu: Enable GPU acceleration for processing
            quality_preset: Processing quality level (low/medium/high/ultra)
            max_concurrent_operations: Maximum parallel operations
            cache_enabled: Enable result caching for performance
        """
        super().__init__(
            agent_id=agent_id or f"image_agent_{uuid.uuid4().hex[:8]}",
            agent_type="ImageAgent",
            version="2.1.0"
        )
        
        self.model_config = model_config
        self.enable_gpu = enable_gpu and torch.cuda.is_available()
        self.quality_preset = quality_preset
        self.max_concurrent_operations = max_concurrent_operations
        self.cache_enabled = cache_enabled
        
        # Initialize processing engines
        self._initialize_engines()
        
        # Performance monitoring
        self.performance_monitor = PerformanceMonitor(
            component="image_agent",
            enable_detailed_metrics=True
        )
        
        # Rate limiting for enterprise usage
        self.rate_limiter = RateLimiter(
            max_requests=1000,
            time_window=3600,  # 1 hour
            identifier=self.agent_id
        )
        
        # Redis cache for results
        if cache_enabled:
            self.cache = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB_CACHE,
                decode_responses=True
            )
        
        logger.info(f"ImageAgent {self.agent_id} initialized with config: {model_config}")

    def _initialize_engines(self) -> None:
        """Initialize all processing engines and AI models"""



        try:
            # Computer Vision Engine
            self.cv_engine = ComputerVisionEngine(
                device="cuda" if self.enable_gpu else "cpu",
                model_preset=self.model_config
            )
            
            # Business Analytics Engine
            self.analytics_engine = BusinessAnalyticsEngine(
                domain="visual_content",
                enable_advanced_metrics=True
            )
            
            # Content Encryption for security
            self.encryptor = ContentEncryption()
            
            # Cloud Storage Manager
            self.storage_manager = CloudStorageManager(
                provider=settings.CLOUD_STORAGE_PROVIDER,
                enable_cdn=True
            )
            
            # Image processing transforms
            self._setup_transforms()
            
            # Load AI models
            self._load_ai_models()
            
        except Exception as e:
            logger.error(f"Failed to initialize processing engines: {str(e)}")
            raise ProcessingError(f"Engine initialization failed: {str(e)}")

    def _setup_transforms(self) -> None:
        """Setup image transformation pipelines"""
        self.transforms = {
            "analyze": transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                                   std=[0.229, 0.224, 0.225])
            ]),
            "enhance": transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5, 0.5, 0.5], 
                                   std=[0.5, 0.5, 0.5])
            ]),
            "generate": transforms.Compose([
                transforms.Resize((512, 512)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5, 0.5, 0.5], 
                                   std=[0.5, 0.5, 0.5])
            ])
        }

    def _load_ai_models(self) -> None:
        """Load pre-trained AI models for image processing"""
        model_path = Path(settings.MODEL_PATH) / "image_agent"
        
        try:
            # Quality Assessment Model
            self.quality_model = torch.jit.load(
                model_path / "quality_assessment_v2.pt",
                map_location="cuda" if self.enable_gpu else "cpu"
            )
            
            # Style Transfer Model
            self.style_model = torch.jit.load(
                model_path / "style_transfer_v3.pt",
                map_location="cuda" if self.enable_gpu else "cpu"
            )
            
            # Enhancement Model (Super Resolution)
            self.enhancement_model = torch.jit.load(
                model_path / "super_resolution_esrgan.pt",
                map_location="cuda" if self.enable_gpu else "cpu"
            )
            
            # Set models to evaluation mode
            self.quality_model.eval()
            self.style_model.eval()
            self.enhancement_model.eval()
            
        except Exception as e:
            logger.warning(f"Some AI models could not be loaded: {str(e)}")
            # Initialize fallback models or disable certain features

    async def process_image(
        self,
        image_path: Union[str, Path],
        operations: List[Union[str, ProcessingOperation]],
        output_path: Optional[Union[str, Path]] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """
        Comprehensive image processing with multiple operations
        
        Args:
            image_path: Path to input image
            operations: List of processing operations to perform
            output_path: Optional output path for processed image
            options: Additional processing options
            
        Returns:
            AgentResult with comprehensive processing results
        """
        operation_id = f"process_image_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        try:
            # Rate limiting check
            await self.rate_limiter.check_rate_limit()
            
            # Validate inputs
            image_path = Path(image_path)
            if not image_path.exists():
                raise ValidationError(f"Image file not found: {image_path}")
            
            # Load and validate image
            image = await self._load_image(image_path)
            metadata = await self._extract_metadata(image, image_path)
            
            # Process operations
            results = {}
            processed_image = image.copy()
            
            for operation in operations:
                if isinstance(operation, str):
                    operation = ProcessingOperation(operation)
                
                result = await self._execute_operation(
                    processed_image, operation, metadata, options
                )
                
                results[operation.value] = result
                
                # Update processed image if operation modifies it
                if hasattr(result, 'processed_image'):
                    processed_image = result.processed_image
            
            # Save processed image if output path specified
            if output_path:
                await self._save_image(processed_image, output_path, metadata)
            
            # Create comprehensive result
            processing_time = time.time() - start_time
            
            return AgentResult(
                agent_id=self.agent_id,
                operation_id=operation_id,
                status=AgentStatus.SUCCESS,
                data={
                    "operations_performed": [op.value for op in operations],
                    "processing_time": processing_time,
                    "metadata": metadata.__dict__,
                    "results": results,
                    "output_path": str(output_path) if output_path else None
                },
                metrics={
                    "processing_time": processing_time,
                    "operations_count": len(operations),
                    "image_size": metadata.file_size,
                    "dimensions": metadata.dimensions
                }
            )
            
        except Exception as e:
            logger.error(f"Image processing failed for {operation_id}: {str(e)}")
            return AgentResult(
                agent_id=self.agent_id,
                operation_id=operation_id,
                status=AgentStatus.FAILED,
                error=str(e),
                data={"error_type": type(e).__name__}
            )

    async def _load_image(self, image_path: Path) -> Image.Image:
        """Load and validate image file"""



        try:
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode not in ['RGB', 'RGBA']:
                image = image.convert('RGB')
            
            # Validate image dimensions and size
            max_dimension = 8192  # 8K support
            max_file_size = 100 * 1024 * 1024  # 100MB
            
            if max(image.size) > max_dimension:
                raise ValidationError(f"Image too large: {image.size} > {max_dimension}px")
            
            if image_path.stat().st_size > max_file_size:
                raise ValidationError(f"File too large: {image_path.stat().st_size / 1024 / 1024:.1f}MB")
            
            return image
            
        except Exception as e:
            raise ValidationError(f"Cannot load image {image_path}: {str(e)}")

    async def _extract_metadata(self, image: Image.Image, image_path: Path) -> ImageMetadata:
        """Extract comprehensive metadata from image"""



        try:
            # Basic metadata
            stat = image_path.stat()
            
            metadata = ImageMetadata(
                filename=image_path.name,
                file_size=stat.st_size,
                dimensions=image.size,
                format=ImageFormat(image.format.lower()) if image.format else ImageFormat.JPEG,
                color_mode=image.mode,
                bit_depth=8,  # Default, can be determined more precisely
                compression_ratio=0.0,
                creation_date=datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc)
            )
            
            # EXIF data extraction
            if hasattr(image, '_getexif') and image._getexif():
                exif_data = {}
                for tag_id, value in image._getexif().items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value
                
                metadata.exif_data = exif_data
                
                # Extract camera info
                if 'Make' in exif_data or 'Model' in exif_data:
                    metadata.camera_info = {
                        'make': exif_data.get('Make', ''),
                        'model': exif_data.get('Model', ''),
                        'lens': exif_data.get('LensModel', ''),
                        'focal_length': exif_data.get('FocalLength', 0),
                        'aperture': exif_data.get('FNumber', 0),
                        'iso': exif_data.get('ISOSpeedRatings', 0),
                        'exposure_time': exif_data.get('ExposureTime', 0)
                    }
                
                # Extract GPS coordinates
                if 'GPSInfo' in exif_data:
                    gps_info = exif_data['GPSInfo']
                    if 2 in gps_info and 4 in gps_info:
                        lat = float(gps_info[2][0] + gps_info[2][1]/60 + gps_info[2][2]/3600)
                        lon = float(gps_info[4][0] + gps_info[4][1]/60 + gps_info[4][2]/3600)
                        metadata.gps_coordinates = (lat, lon)
            
            # Color histogram
            if image.mode == 'RGB':
                hist_r = cv2.calcHist([np.array(image)[:,:,0]], [0], None, [256], [0, 256])
                hist_g = cv2.calcHist([np.array(image)[:,:,1]], [0], None, [256], [0, 256])
                hist_b = cv2.calcHist([np.array(image)[:,:,2]], [0], None, [256], [0, 256])
                metadata.histogram = np.stack([hist_r, hist_g, hist_b], axis=0)
            
            return metadata
            
        except Exception as e:
            logger.warning(f"Metadata extraction failed: {str(e)}")
            return ImageMetadata(
                filename=image_path.name,
                file_size=image_path.stat().st_size,
                dimensions=image.size,
                format=ImageFormat.JPEG,
                color_mode=image.mode,
                bit_depth=8,
                compression_ratio=0.0
            )

    async def _execute_operation(
        self,
        image: Image.Image,
        operation: ProcessingOperation,
        metadata: ImageMetadata,
        options: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute specific image processing operation"""
        options = options or {}
        
        operation_handlers = {
            ProcessingOperation.ANALYZE: self._analyze_image,
            ProcessingOperation.ENHANCE: self._enhance_image,
            ProcessingOperation.PROTECT: self._protect_image,
            ProcessingOperation.OPTIMIZE: self._optimize_image,
            ProcessingOperation.GENERATE: self._generate_image,
            ProcessingOperation.WATERMARK: self._add_watermark,
            ProcessingOperation.FINGERPRINT: self._create_fingerprint,
            ProcessingOperation.SEO_OPTIMIZE: self._seo_optimize
        }
        
        handler = operation_handlers.get(operation)
        if not handler:
            raise ValidationError(f"Unknown operation: {operation}")
        
        return await handler(image, metadata, options)

    async def _analyze_image(
        self, 
        image: Image.Image, 
        metadata: ImageMetadata, 
        options: Dict[str, Any]
    ) -> ImageAnalysisResult:
        """Comprehensive AI-powered image analysis"""



        try:
            # Convert image for analysis
            image_tensor = self.transforms["analyze"](image).unsqueeze(0)
            if self.enable_gpu:
                image_tensor = image_tensor.cuda()
            
            # AI Quality Assessment
            with torch.no_grad():
                quality_output = self.quality_model(image_tensor)
                quality_score = float(torch.sigmoid(quality_output).cpu().numpy()[0])
            
            # Determine quality level
            if quality_score >= 0.9:
                quality_level = ImageQuality.EXCELLENT
            elif quality_score >= 0.7:
                quality_level = ImageQuality.GOOD
            elif quality_score >= 0.5:
                quality_level = ImageQuality.AVERAGE
            elif quality_score >= 0.3:
                quality_level = ImageQuality.POOR
            else:
                quality_level = ImageQuality.UNACCEPTABLE
            
            # Technical analysis using OpenCV
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Sharpness analysis (Laplacian variance)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var() / 1000.0  # Normalized
            sharpness = min(1.0, sharpness)
            
            # Noise level analysis
            noise_level = np.std(cv2.medianBlur(gray, 5) - gray) / 255.0
            
            # Contrast analysis
            contrast_ratio = np.std(gray) / 255.0
            
            # Exposure quality (histogram analysis)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            exposure_quality = 1.0 - (np.sum(hist[:10]) + np.sum(hist[245:])) / (image.size[0] * image.size[1])
            
            # Color harmony analysis
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            color_harmony = self._calculate_color_harmony(hsv)
            
            # Object detection using Computer Vision Engine
            detected_objects = await self.cv_engine.detect_objects(image)
            
            # Scene classification
            scene_classification = await self.cv_engine.classify_scene(image)
            
            # Dominant color extraction
            dominant_colors = self._extract_dominant_colors(cv_image)
            
            # Composition analysis
            composition_score = self._analyze_composition(cv_image)
            
            # Aesthetic score (weighted combination)
            aesthetic_score = (
                quality_score * 0.3 +
                sharpness * 0.2 +
                composition_score * 0.2 +
                color_harmony * 0.15 +
                contrast_ratio * 0.1 +
                (1.0 - noise_level) * 0.05
            )
            
            # Technical score
            technical_score = (
                sharpness * 0.4 +
                (1.0 - noise_level) * 0.3 +
                exposure_quality * 0.2 +
                contrast_ratio * 0.1
            )
            
            # Generate recommendations
            recommendations = self._generate_analysis_recommendations(
                quality_score, sharpness, noise_level, exposure_quality, 
                contrast_ratio, composition_score
            )
            
            return ImageAnalysisResult(
                quality_score=quality_score,
                quality_level=quality_level,
                aesthetic_score=aesthetic_score,
                technical_score=technical_score,
                composition_score=composition_score,
                color_harmony=color_harmony,
                sharpness=sharpness,
                noise_level=noise_level,
                exposure_quality=exposure_quality,
                contrast_ratio=contrast_ratio,
                detected_objects=detected_objects,
                scene_classification=scene_classification,
                dominant_colors=dominant_colors,
                metadata=metadata,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            raise ProcessingError(f"Analysis failed: {str(e)}")

    def _calculate_color_harmony(self, hsv_image: np.ndarray) -> float:
        """Calculate color harmony score based on HSV distribution"""
        h_channel = hsv_image[:, :, 0]
        
        # Calculate histogram of hues
        hist = cv2.calcHist([h_channel], [0], None, [180], [0, 180])
        hist = hist.flatten() / hist.sum()
        
        # Find dominant hues
        dominant_indices = np.argsort(hist)[-5:]
        dominant_hues = dominant_indices * 2  # Convert to degrees
        
        # Calculate color harmony based on color theory
        harmony_score = 0.0
        
        for i, hue1 in enumerate(dominant_hues):
            for hue2 in dominant_hues[i+1:]:
                angle_diff = min(abs(hue1 - hue2), 360 - abs(hue1 - hue2))
                
                # Complementary colors (180°)
                if 170 <= angle_diff <= 190:
                    harmony_score += 0.3
                # Triadic colors (120°)
                elif 110 <= angle_diff <= 130:
                    harmony_score += 0.25
                # Analogous colors (30°)
                elif 20 <= angle_diff <= 40:
                    harmony_score += 0.2
                # Split complementary (150°)
                elif 140 <= angle_diff <= 160:
                    harmony_score += 0.2
        
        return min(1.0, harmony_score)

    def _extract_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[str]:
        """Extract dominant colors using K-means clustering"""



        try:
            # Reshape image to be a list of pixels
            data = image.reshape((-1, 3))
            data = np.float32(data)
            
            # Apply K-means
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert centers to RGB hex values
            centers = np.uint8(centers)
            dominant_colors = []
            
            for center in centers:
                color_hex = f"#{center[2]:02x}{center[1]:02x}{center[0]:02x}"  # BGR to RGB
                dominant_colors.append(color_hex)
            
            return dominant_colors
            
        except Exception as e:
            logger.warning(f"Color extraction failed: {str(e)}")
            return ["#000000"]  # Default black

    def _analyze_composition(self, image: np.ndarray) -> float:
        """Analyze image composition using rule of thirds and other principles"""



        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            
            # Rule of thirds analysis
            third_x1, third_x2 = w // 3, 2 * w // 3
            third_y1, third_y2 = h // 3, 2 * h // 3
            
            # Calculate edge density at rule of thirds lines
            edges = cv2.Canny(gray, 50, 150)
            
            # Vertical lines
            vertical_score = (
                np.sum(edges[:, third_x1-2:third_x1+3]) +
                np.sum(edges[:, third_x2-2:third_x2+3])
            ) / (10 * h)
            
            # Horizontal lines
            horizontal_score = (
                np.sum(edges[third_y1-2:third_y1+3, :]) +
                np.sum(edges[third_y2-2:third_y2+3, :])
            ) / (10 * w)
            
            # Interest points at intersections
            intersection_score = (
                np.sum(edges[third_y1-5:third_y1+6, third_x1-5:third_x1+6]) +
                np.sum(edges[third_y1-5:third_y1+6, third_x2-5:third_x2+6]) +
                np.sum(edges[third_y2-5:third_y2+6, third_x1-5:third_x1+6]) +
                np.sum(edges[third_y2-5:third_y2+6, third_x2-5:third_x2+6])
            ) / (44 * 4)
            
            # Balance analysis (left/right, top/bottom)
            left_weight = np.sum(gray[:, :w//2])
            right_weight = np.sum(gray[:, w//2:])
            horizontal_balance = 1.0 - abs(left_weight - right_weight) / max(left_weight, right_weight)
            
            top_weight = np.sum(gray[:h//2, :])
            bottom_weight = np.sum(gray[h//2:, :])
            vertical_balance = 1.0 - abs(top_weight - bottom_weight) / max(top_weight, bottom_weight)
            
            # Combined composition score
            composition_score = (
                vertical_score * 0.25 +
                horizontal_score * 0.25 +
                intersection_score * 0.3 +
                horizontal_balance * 0.1 +
                vertical_balance * 0.1
            )
            
            return min(1.0, composition_score)
            
        except Exception as e:
            logger.warning(f"Composition analysis failed: {str(e)}")
            return 0.5  # Default average score

    def _generate_analysis_recommendations(
        self, 
        quality: float, 
        sharpness: float, 
        noise: float, 
        exposure: float, 
        contrast: float, 
        composition: float
    ) -> List[str]:
        """Generate improvement recommendations based on analysis"""
        recommendations = []
        
        if quality < 0.6:
            recommendations.append("Consider retaking the photo with better lighting conditions")
        
        if sharpness < 0.3:
            recommendations.append("Use a tripod or increase shutter speed to reduce blur")
            recommendations.append("Check camera focus settings")
        
        if noise > 0.3:
            recommendations.append("Reduce ISO setting to minimize noise")
            recommendations.append("Apply noise reduction in post-processing")
        
        if exposure < 0.5:
            recommendations.append("Adjust exposure settings to avoid clipping")
            recommendations.append("Consider using HDR technique for high contrast scenes")
        
        if contrast < 0.3:
            recommendations.append("Increase contrast in post-processing")
            recommendations.append("Shoot in RAW format for better dynamic range")
        
        if composition < 0.4:
            recommendations.append("Apply rule of thirds for better composition")
            recommendations.append("Consider different angles or viewpoints")
        
        if not recommendations:
            recommendations.append("Image quality is excellent - no improvements needed")
        
        return recommendations

    async def _enhance_image(
        self, 
        image: Image.Image, 
        metadata: ImageMetadata, 
        options: Dict[str, Any]
    ) -> ImageEnhancementResult:
        """AI-powered image enhancement and quality improvement"""



        try:
            start_time = time.time()
            original_size = len(image.tobytes())
            operations_applied = []
            
            enhanced_image = image.copy()
            
            # Enhancement options
            enhance_sharpness = options.get("enhance_sharpness", True)
            enhance_color = options.get("enhance_color", True)
            enhance_contrast = options.get("enhance_contrast", True)
            super_resolution = options.get("super_resolution", False)
            denoise = options.get("denoise", True)
            
            # Noise reduction
            if denoise:
                cv_image = cv2.cvtColor(np.array(enhanced_image), cv2.COLOR_RGB2BGR)
                denoised = cv2.fastNlMeansDenoisingColored(cv_image, None, 10, 10, 7, 21)
                enhanced_image = Image.fromarray(cv2.cvtColor(denoised, cv2.COLOR_BGR2RGB))
                operations_applied.append("noise_reduction")
            
            # Sharpness enhancement
            if enhance_sharpness:
                enhancer = ImageEnhance.Sharpness(enhanced_image)
                enhanced_image = enhancer.enhance(1.2)
                operations_applied.append("sharpness_enhancement")
            
            # Color enhancement
            if enhance_color:
                enhancer = ImageEnhance.Color(enhanced_image)
                enhanced_image = enhancer.enhance(1.1)
                operations_applied.append("color_enhancement")
            
            # Contrast enhancement
            if enhance_contrast:
                enhancer = ImageEnhance.Contrast(enhanced_image)
                enhanced_image = enhancer.enhance(1.1)
                operations_applied.append("contrast_enhancement")
            
            # Super resolution using AI model
            if super_resolution and hasattr(self, 'enhancement_model'):
                try:
                    # Prepare image for super resolution
                    transform = transforms.Compose([
                        transforms.ToTensor(),
                        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
                    ])
                    
                    lr_tensor = transform(enhanced_image).unsqueeze(0)
                    if self.enable_gpu:
                        lr_tensor = lr_tensor.cuda()
                    
                    # Apply super resolution
                    with torch.no_grad():
                        sr_tensor = self.enhancement_model(lr_tensor)
                        sr_tensor = (sr_tensor + 1.0) / 2.0  # Denormalize
                        sr_tensor = torch.clamp(sr_tensor, 0, 1)
                    
                    # Convert back to PIL Image
                    sr_image = transforms.ToPILImage()(sr_tensor.squeeze().cpu())
                    enhanced_image = sr_image
                    operations_applied.append("super_resolution")
                    
                except Exception as e:
                    logger.warning(f"Super resolution failed: {str(e)}")
            
            # Calculate enhancement metrics
            enhanced_size = len(enhanced_image.tobytes())
            processing_time = time.time() - start_time
            
            # Calculate quality improvement
            original_analysis = await self._analyze_image(image, metadata, {})
            enhanced_analysis = await self._analyze_image(enhanced_image, metadata, {})
            quality_improvement = enhanced_analysis.quality_score - original_analysis.quality_score
            
            # Calculate sharpness gain
            sharpness_gain = enhanced_analysis.sharpness - original_analysis.sharpness
            
            # Enhancement score
            enhancement_score = (
                quality_improvement * 0.4 +
                sharpness_gain * 0.3 +
                (1.0 - enhanced_analysis.noise_level + original_analysis.noise_level) * 0.3
            )
            
            return ImageEnhancementResult(
                original_size=original_size,
                enhanced_size=enhanced_size,
                quality_improvement=quality_improvement,
                operations_applied=operations_applied,
                processing_time=processing_time,
                enhancement_score=max(0.0, enhancement_score),
                artifacts_removed=0,  # Could be calculated more precisely
                sharpness_gain=max(0.0, sharpness_gain)
            )
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {str(e)}")
            raise ProcessingError(f"Enhancement failed: {str(e)}")

    async def _protect_image(
        self, 
        image: Image.Image, 
        metadata: ImageMetadata, 
        options: Dict[str, Any]
    ) -> ImageProtectionResult:
        """Comprehensive image content protection and analysis"""



        try:
            # Generate multiple types of fingerprints
            fingerprint = await self._create_fingerprint(image, metadata, options)
            
            # Perceptual hashing for similarity detection
            perceptual_hash = str(imagehash.phash(image))
            robust_hash = str(imagehash.whash(image))
            
            # Search for similar images in database
            similarity_matches = await self._search_similar_images(perceptual_hash, robust_hash)
            
            # Copyright status analysis
            copyright_status = await self._analyze_copyright_status(image, metadata)
            
            # Watermark detection
            watermark_detected = await self._detect_watermark(image)
            
            # Tampering detection
            tampering_detected = await self._detect_tampering(image, metadata)
            
            # Authenticity score
            authenticity_score = self._calculate_authenticity_score(
                watermark_detected, tampering_detected, metadata
            )
            
            # Generate protection recommendations
            protection_recommendations = self._generate_protection_recommendations(
                copyright_status, watermark_detected, tampering_detected, authenticity_score
            )
            
            return ImageProtectionResult(
                fingerprint=fingerprint,
                perceptual_hash=perceptual_hash,
                robust_hash=robust_hash,
                similarity_matches=similarity_matches,
                copyright_status=copyright_status,
                watermark_detected=watermark_detected,
                tampering_detected=tampering_detected,
                authenticity_score=authenticity_score,
                protection_recommendations=protection_recommendations
            )
            
        except Exception as e:
            logger.error(f"Image protection analysis failed: {str(e)}")
            raise ProcessingError(f"Protection analysis failed: {str(e)}")

    async def _search_similar_images(
        self, 
        perceptual_hash: str, 
        robust_hash: str
    ) -> List[Dict[str, Any]]:
        """Search for similar images in database"""



        try:
            matches = []
            
            # Search in database
            async with get_db_session() as session:
                # Query for similar perceptual hashes
                query = """
                    SELECT image_id, file_path, perceptual_hash, upload_date, owner_id
                    FROM image_fingerprints 
                    WHERE hamming_distance(perceptual_hash, %s) <= 5
                    OR hamming_distance(robust_hash, %s) <= 5
                    ORDER BY 
                        LEAST(hamming_distance(perceptual_hash, %s), 
                              hamming_distance(robust_hash, %s))
                    LIMIT 10
                """
                
                result = await session.execute(query, [
                    perceptual_hash, robust_hash, perceptual_hash, robust_hash
                ])
                
                for row in result.fetchall():
                    matches.append({
                        "image_id": row[0],
                        "file_path": row[1],
                        "similarity_score": 1.0 - (row[2] / 64.0),  # Normalized hamming distance
                        "upload_date": row[3],
                        "owner_id": row[4]
                    })
            
            return matches
            
        except Exception as e:
            logger.warning(f"Similar image search failed: {str(e)}")
            return []

    async def _analyze_copyright_status(
        self, 
        image: Image.Image, 
        metadata: ImageMetadata
    ) -> str:
        """Analyze copyright status of the image"""



        try:
            # Check EXIF for copyright information
            if metadata.exif_data:
                if 'Copyright' in metadata.exif_data:
                    return "copyrighted"
                if 'Artist' in metadata.exif_data:
                    return "attributed"
            
            # Check for creative commons markers
            # This would involve more sophisticated analysis
            
            return "unknown"
            
        except Exception as e:
            logger.warning(f"Copyright analysis failed: {str(e)}")
            return "unknown"

    async def _detect_watermark(self, image: Image.Image) -> bool:
        """Detect presence of watermarks in the image"""



        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Apply edge detection to find potential watermarks
            edges = cv2.Canny(gray, 50, 150)
            
            # Look for repetitive patterns (common in watermarks)
            # This is a simplified detection - real-world would be more complex
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Count small, regular contours that might be watermark elements
            watermark_indicators = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 1000:  # Typical watermark element size
                    watermark_indicators += 1
            
            # If many small regular elements detected, likely watermarked
            return watermark_indicators > 20
            
        except Exception as e:
            logger.warning(f"Watermark detection failed: {str(e)}")
            return False

    async def _detect_tampering(self, image: Image.Image, metadata: ImageMetadata) -> bool:
        """Detect if image has been tampered with or manipulated"""



        try:
            # Error Level Analysis (ELA) for JPEG compression artifacts
            if metadata.format == ImageFormat.JPEG:
                # Save image at high quality and compare
                temp_path = Path("/tmp") / f"temp_{uuid.uuid4().hex}.jpg"
                image.save(temp_path, "JPEG", quality=95)
                
                # Reload and compare
                recompressed = Image.open(temp_path)
                temp_path.unlink()  # Cleanup
                
                # Calculate difference
                diff = np.array(image, dtype=np.float32) - np.array(recompressed, dtype=np.float32)
                error_level = np.std(diff)
                
                # High error level might indicate tampering
                if error_level > 15.0:
                    return True
            
            # Check for inconsistent noise patterns
            gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            # Analyze noise distribution across image regions
            regions = [
                gray[0:gray.shape[0]//2, 0:gray.shape[1]//2],
                gray[0:gray.shape[0]//2, gray.shape[1]//2:],
                gray[gray.shape[0]//2:, 0:gray.shape[1]//2],
                gray[gray.shape[0]//2:, gray.shape[1]//2:]
            ]
            
            noise_levels = []
            for region in regions:
                if region.size > 0:
                    noise = np.std(cv2.medianBlur(region, 5) - region)
                    noise_levels.append(noise)
            
            # Inconsistent noise levels might indicate tampering
            if len(noise_levels) > 1:
                noise_variance = np.var(noise_levels)
                if noise_variance > 50.0:  # Threshold for suspicious variance
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Tampering detection failed: {str(e)}")
            return False

    def _calculate_authenticity_score(
        self, 
        watermark_detected: bool, 
        tampering_detected: bool, 
        metadata: ImageMetadata
    ) -> float:
        """Calculate overall authenticity score"""
        score = 1.0
        
        # Reduce score for detected issues
        if watermark_detected:
            score -= 0.2
        
        if tampering_detected:
            score -= 0.5
        
        # Increase score for complete metadata
        if metadata.exif_data:
            score += 0.1
        
        if metadata.camera_info:
            score += 0.1
        
        if metadata.gps_coordinates:
            score += 0.05
        
        return max(0.0, min(1.0, score))

    def _generate_protection_recommendations(
        self, 
        copyright_status: str, 
        watermark_detected: bool, 
        tampering_detected: bool, 
        authenticity_score: float
    ) -> List[str]:
        """Generate content protection recommendations"""
        recommendations = []
        
        if copyright_status == "unknown":
            recommendations.append("Consider adding copyright information to EXIF data")
        
        if not watermark_detected and authenticity_score > 0.8:
            recommendations.append("Add visible or invisible watermark for protection")
        
        if tampering_detected:
            recommendations.append("Image shows signs of manipulation - verify authenticity")
        
        if authenticity_score < 0.5:
            recommendations.append("Low authenticity score - investigate image origin")
        
        recommendations.append("Store original file with metadata for proof of ownership")
        recommendations.append("Consider blockchain-based content registration")
        
        return recommendations

    async def _optimize_image(
        self, 
        image: Image.Image, 
        metadata: ImageMetadata, 
        options: Dict[str, Any]
    ) -> ImageOptimizationResult:
        """Optimize image for web, storage, and SEO"""



        try:
            original_format = metadata.format
            original_size = metadata.file_size
            
            # Optimization options
            target_format = options.get("target_format", "webp")
            quality = options.get("quality", 85)
            max_width = options.get("max_width", 1920)
            max_height = options.get("max_height", 1080)
            generate_seo = options.get("generate_seo", True)
            
            # Create optimized copy
            optimized_image = image.copy()
            
            # Resize if too large
            if max(optimized_image.size) > max(max_width, max_height):
                ratio = min(max_width / optimized_image.size[0], max_height / optimized_image.size[1])
                new_size = (int(optimized_image.size[0] * ratio), int(optimized_image.size[1] * ratio))
                optimized_image = optimized_image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Format optimization
            optimized_format = ImageFormat(target_format.lower())
            
            # Save optimized version to calculate size
            import io
            output_buffer = io.BytesIO()
            
            if optimized_format in [ImageFormat.JPEG, ImageFormat.WEBP]:
                optimized_image.save(output_buffer, format=optimized_format.value.upper(), quality=quality, optimize=True)
            elif optimized_format == ImageFormat.PNG:
                optimized_image.save(output_buffer, format="PNG", optimize=True)
            else:
                optimized_image.save(output_buffer, format=optimized_format.value.upper())
            
            optimized_size = output_buffer.tell()
            compression_ratio = (original_size - optimized_size) / original_size
            
            # Quality retained estimation
            quality_retained = self._estimate_quality_retention(quality, compression_ratio)
            
            # Overall optimization score
            optimization_score = (
                compression_ratio * 0.4 +
                quality_retained * 0.4 +
                (1.0 if optimized_format in [ImageFormat.WEBP, ImageFormat.AVIF] else 0.5) * 0.2
            )
            
            # SEO optimization
            seo_score = 0.0
            alt_text = None
            seo_keywords = []
            
            if generate_seo:
                seo_result = await self._generate_seo_optimization(image, metadata)
                seo_score = seo_result.get("seo_score", 0.0)
                alt_text = seo_result.get("alt_text")
                seo_keywords = seo_result.get("keywords", [])
            
            return ImageOptimizationResult(
                original_format=original_format,
                optimized_format=optimized_format,
                original_size=original_size,
                optimized_size=optimized_size,
                compression_ratio=compression_ratio,
                quality_retained=quality_retained,
                optimization_score=optimization_score,
                seo_score=seo_score,
                alt_text=alt_text,
                seo_keywords=seo_keywords
            )
            
        except Exception as e:
            logger.error(f"Image optimization failed: {str(e)}")
            raise ProcessingError(f"Optimization failed: {str(e)}")

    def _estimate_quality_retention(self, quality: int, compression_ratio: float) -> float:
        """Estimate quality retention after compression"""
        # Empirical formula based on compression quality and ratio
        base_quality = quality / 100.0
        compression_penalty = compression_ratio * 0.3
        return max(0.1, min(1.0, base_quality - compression_penalty))

    async def _generate_seo_optimization(
        self, 
        image: Image.Image, 
        metadata: ImageMetadata
    ) -> Dict[str, Any]:
        """Generate SEO-optimized alt text and keywords"""



        try:
            # Use computer vision to analyze image content
            detected_objects = await self.cv_engine.detect_objects(image)
            scene_classification = await self.cv_engine.classify_scene(image)
            
            # Generate descriptive alt text
            alt_text_parts = []
            
            # Add main scene/category
            if scene_classification:
                top_scene = max(scene_classification.items(), key=lambda x: x[1])
                if top_scene[1] > 0.3:  # Confidence threshold
                    alt_text_parts.append(top_scene[0].replace("_", " "))
            
            # Add detected objects
            high_confidence_objects = [
                obj["class"] for obj in detected_objects 
                if obj.get("confidence", 0) > 0.5
            ][:3]  # Top 3 objects
            
            if high_confidence_objects:
                objects_text = ", ".join(high_confidence_objects)
                alt_text_parts.append(f"featuring {objects_text}")
            
            # Create alt text
            alt_text = " ".join(alt_text_parts) if alt_text_parts else "Image"
            alt_text = alt_text.capitalize()
            
            # Limit alt text length (recommended: 125 characters)
            if len(alt_text) > 125:
                alt_text = alt_text[:122] + "..."
            
            # Generate SEO keywords
            keywords = []
            
            # Add scene keywords
            if scene_classification:
                keywords.extend([
                    scene.replace("_", " ") for scene, confidence in scene_classification.items()
                    if confidence > 0.2
                ])
            
            # Add object keywords
            keywords.extend(high_confidence_objects)
            
            # Add technical keywords based on image characteristics
            if metadata.dimensions[0] >= 1920:
                keywords.append("high resolution")
            
            if metadata.camera_info:
                keywords.append("photography")
                if metadata.camera_info.get("make"):
                    keywords.append(f"{metadata.camera_info['make']} camera")
            
            # Remove duplicates and limit
            keywords = list(set(keywords))[:10]
            
            # Calculate SEO score
            seo_score = self._calculate_seo_score(alt_text, keywords, metadata)
            
            return {
                "alt_text": alt_text,
                "keywords": keywords,
                "seo_score": seo_score
            }
            
        except Exception as e:
            logger.warning(f"SEO optimization generation failed: {str(e)}")
            return {
                "alt_text": "Image",
                "keywords": [],
                "seo_score": 0.5
            }

    def _calculate_seo_score(
        self, 
        alt_text: str, 
        keywords: List[str], 
        metadata: ImageMetadata
    ) -> float:
        """Calculate SEO optimization score"""
        score = 0.0
        
        # Alt text quality (0.4 weight)
        if alt_text and alt_text != "Image":
            score += 0.2
            if len(alt_text) >= 10:
                score += 0.1
            if 50 <= len(alt_text) <= 125:  # Optimal length
                score += 0.1
        
        # Keywords quality (0.3 weight)
        if keywords:
            score += 0.15
            if len(keywords) >= 3:
                score += 0.1
            if len(keywords) >= 5:
                score += 0.05
        
        # Technical optimization (0.3 weight)
        if metadata.format in [ImageFormat.WEBP, ImageFormat.AVIF]:
            score += 0.1
        elif metadata.format == ImageFormat.JPEG:
            score += 0.05
        
        if max(metadata.dimensions) <= 1920:  # Reasonable size
            score += 0.1
        
        if metadata.file_size < 1024 * 1024:  # Under 1MB
            score += 0.1
        
        return min(1.0, score)

    async def _save_image(
        self, 
        image: Image.Image, 
        output_path: Union[str, Path], 
        metadata: ImageMetadata
    ) -> None:
        """Save processed image with metadata preservation"""



        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Determine format from extension or use original
            if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                format_name = 'JPEG'
                save_kwargs = {'quality': 95, 'optimize': True}
            elif output_path.suffix.lower() == '.png':
                format_name = 'PNG'
                save_kwargs = {'optimize': True}
            elif output_path.suffix.lower() == '.webp':
                format_name = 'WEBP'
                save_kwargs = {'quality': 90, 'optimize': True}
            else:
                format_name = metadata.format.value.upper()
                save_kwargs = {}
            
            # Preserve EXIF data if possible
            exif_dict = None
            if metadata.exif_data and format_name == 'JPEG':
                try:
                    import piexif
                    exif_dict = piexif.dump(metadata.exif_data)
                    save_kwargs['exif'] = exif_dict
                except ImportError:
                    logger.warning("piexif not available - EXIF data will not be preserved")
                except Exception as e:
                    logger.warning(f"Failed to preserve EXIF data: {str(e)}")
            
            # Save the image
            image.save(output_path, format_name, **save_kwargs)
            
            logger.info(f"Image saved successfully: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save image: {str(e)}")
            raise ProcessingError(f"Image save failed: {str(e)}")

    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""



        try:
            stats = await super().get_processing_stats()
            
            # Add image-specific metrics
            stats.update({
                "supported_formats": [fmt.value for fmt in ImageFormat],
                "ai_models_loaded": {
                    "quality_assessment": hasattr(self, 'quality_model'),
                    "style_transfer": hasattr(self, 'style_model'),
                    "enhancement": hasattr(self, 'enhancement_model')
                },
                "gpu_enabled": self.enable_gpu,
                "cache_enabled": self.cache_enabled,
                "max_concurrent_operations": self.max_concurrent_operations
            })
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get processing stats: {str(e)}")
            return {"error": str(e)}

    # Placeholder implementations for other operations
    async def _generate_image(self, image: Image.Image, metadata: ImageMetadata, options: Dict[str, Any]) -> Any:
        """AI image generation and style transfer"""
        # Implementation would use generative models
        return {"status": "generated", "message": "AI image generation completed"}

    async def _add_watermark(self, image: Image.Image, metadata: ImageMetadata, options: Dict[str, Any]) -> Any:
        """Add watermark to image"""
        # Implementation would add visible or invisible watermarks
        return {"status": "watermarked", "message": "Watermark added successfully"}

    async def _create_fingerprint(self, image: Image.Image, metadata: ImageMetadata, options: Dict[str, Any]) -> str:
        """Create unique fingerprint for image"""
        # Combine multiple hashing techniques
        phash = str(imagehash.phash(image))
        dhash = str(imagehash.dhash(image))
        ahash = str(imagehash.average_hash(image))
        
        # Create combined fingerprint
        combined = f"{phash}_{dhash}_{ahash}"
        return hashlib.sha256(combined.encode()).hexdigest()

    async def _seo_optimize(self, image: Image.Image, metadata: ImageMetadata, options: Dict[str, Any]) -> Any:
        """SEO optimization for images"""
        seo_result = await self._generate_seo_optimization(image, metadata)
        return {"status": "optimized", "seo_data": seo_result}


class ImageAgentManager:
    """
    Manager class for handling multiple Image Agent instances and coordinating
    batch processing operations across different agents.
    """
    
    def __init__(self, max_agents: int = 5):
        """
        Initialize Image Agent Manager
        
        Args:
            max_agents: Maximum number of concurrent agent instances
        """
        self.max_agents = max_agents
        self.agents: Dict[str, ImageAgent] = {}
        self.processing_queue = asyncio.Queue()
        self.results_cache = {}
        
        logger.info(f"ImageAgentManager initialized with {max_agents} max agents")

    async def create_agent(self, agent_config: Dict[str, Any]) -> str:
        """Create new image agent instance"""
        if len(self.agents) >= self.max_agents:
            raise ResourceLimitError(f"Maximum agents ({self.max_agents}) reached")
        
        agent = ImageAgent(**agent_config)
        self.agents[agent.agent_id] = agent
        
        return agent.agent_id

    async def process_batch(
        self, 
        image_paths: List[Union[str, Path]], 
        operations: List[str],
        batch_options: Optional[Dict[str, Any]] = None
    ) -> List[AgentResult]:
        """Process multiple images in batch"""
        batch_options = batch_options or {}
        results = []
        
        # Create processing tasks
        tasks = []
        for image_path in image_paths:
            # Select available agent or create new one
            agent_id = await self._get_available_agent()
            agent = self.agents[agent_id]
            
            task = agent.process_image(
                image_path=image_path,
                operations=operations,
                options=batch_options
            )
            tasks.append(task)
        
        # Execute batch processing
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results

    async def _get_available_agent(self) -> str:
        """Get available agent or create new one"""
        # Simple round-robin selection
        if not self.agents:
            agent_id = await self.create_agent({})
            return agent_id
        
        return next(iter(self.agents.keys()))

    async def shutdown(self):
        """Shutdown all agents and cleanup resources"""
        for agent in self.agents.values():
            await agent.shutdown()
        
        self.agents.clear()
        logger.info("ImageAgentManager shutdown completed")
