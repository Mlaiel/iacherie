"""
Image Quality Assessment Module

Advanced image quality analysis for photographers, visual content creators, and influencers.
Implements professional image metrics and industry-standard quality assessment.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING 
This software and all associated concepts, algorithms, and implementations are the exclusive 
intellectual property of Fahed Mlaiel (mlaiel@live.de). Any unauthorized use, reproduction, 
distribution, modification, or appropriation of this code, in whole or in part, without 
explicit written permission from Fahed Mlaiel is strictly prohibited and will be prosecuted 
to the full extent of the law.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import cv2
from PIL import Image, ImageStat, ImageEnhance
from PIL.ExifTags import TAGS

from ..core.base_models import BaseAIModel, ModelConfig, ModelType, ModelProvider
from ..core.exceptions import QualityCheckError, ContentValidationError
from ..core.performance import PerformanceMonitor, monitor_performance
from ..core.metrics import MetricsCollector, metrics_collector

logger = logging.getLogger(__name__)


class ImageFormat(Enum):
    """Supported image formats"""
    JPEG = "jpeg"
    PNG = "png"
    TIFF = "tiff"
    RAW = "raw"
    WEBP = "webp"
    HEIC = "heic"


class ImageSharpness(Enum):
    """Image sharpness categories"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    SOFT = "soft"
    BLURRY = "blurry"


class ColorAccuracy(Enum):
    """Color accuracy categories"""
    PROFESSIONAL = "professional"
    ACCURATE = "accurate"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    OVERSATURATED = "oversaturated"
    UNDERSATURATED = "undersaturated"


@dataclass
class CompositionAnalysis:
    """Image composition analysis results"""
    rule_of_thirds_score: float = field(default=0.0)
    symmetry_score: float = field(default=0.0)
    balance_score: float = field(default=0.0)
    leading_lines_score: float = field(default=0.0)
    depth_of_field_score: float = field(default=0.0)
    
    # Visual weight distribution
    top_left_weight: float = field(default=0.0)
    top_right_weight: float = field(default=0.0)
    bottom_left_weight: float = field(default=0.0)
    bottom_right_weight: float = field(default=0.0)
    
    # Focus analysis
    subject_focus: float = field(default=0.0)
    background_blur: float = field(default=0.0)
    depth_layers: int = field(default=1)
    
    # Overall composition score
    composition_score: float = field(default=0.0)


@dataclass
class ImageQualityProfile:
    """Comprehensive image quality profile"""
    # Basic properties
    width: int = field(default=0)
    height: int = field(default=0)
    megapixels: float = field(default=0.0)
    aspect_ratio: float = field(default=0.0)
    file_size: int = field(default=0)
    format: str = field(default="unknown")
    color_mode: str = field(default="unknown")  # RGB, CMYK, Grayscale
    bit_depth: int = field(default=8)
    
    # EXIF data
    camera_make: str = field(default="unknown")
    camera_model: str = field(default="unknown")
    lens_model: str = field(default="unknown")
    focal_length: str = field(default="unknown")
    aperture: str = field(default="unknown")
    shutter_speed: str = field(default="unknown")
    iso: str = field(default="unknown")
    flash: str = field(default="unknown")
    
    # Technical quality
    sharpness_score: float = field(default=0.0)
    sharpness_category: ImageSharpness = field(default=ImageSharpness.ACCEPTABLE)
    noise_level: float = field(default=0.0)
    contrast: float = field(default=0.0)
    brightness: float = field(default=0.0)
    saturation: float = field(default=0.0)
    
    # Color analysis
    color_accuracy: ColorAccuracy = field(default=ColorAccuracy.ACCEPTABLE)
    color_temperature: float = field(default=0.0)  # Kelvin
    white_balance_score: float = field(default=0.0)
    color_gamut_coverage: float = field(default=0.0)
    histogram_balance: float = field(default=0.0)
    
    # Exposure analysis
    exposure_score: float = field(default=0.0)
    highlight_clipping: float = field(default=0.0)
    shadow_clipping: float = field(default=0.0)
    dynamic_range: float = field(default=0.0)
    
    # Composition analysis
    composition: CompositionAnalysis = field(default_factory=CompositionAnalysis)
    
    # Quality scores
    technical_score: float = field(default=0.0)
    artistic_score: float = field(default=0.0)
    commercial_score: float = field(default=0.0)
    
    # Overall quality
    overall_quality_score: float = field(default=0.0)
    quality_level: str = field(default="acceptable")
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    enhancement_suggestions: List[str] = field(default_factory=list)


@dataclass
class ImageQualityMetrics:
    """Image quality metrics container"""
    profile: ImageQualityProfile = field(default_factory=ImageQualityProfile)
    
    # Platform readiness
    instagram_ready: bool = field(default=False)
    facebook_ready: bool = field(default=False)
    pinterest_ready: bool = field(default=False)
    linkedin_ready: bool = field(default=False)
    print_ready: bool = field(default=False)
    web_ready: bool = field(default=False)
    
    # Content analysis
    image_type: str = field(default="unknown")  # portrait, landscape, macro, street, etc.
    subject_type: str = field(default="unknown")  # person, object, scene, abstract
    lighting_type: str = field(default="unknown")  # natural, artificial, mixed, low_light
    
    # Advanced metrics
    aesthetic_score: float = field(default=0.0)
    emotional_impact: float = field(default=0.0)
    technical_excellence: float = field(default=0.0)
    
    # Metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = field(default=0.0)
    confidence: float = field(default=0.0)


class ImageQualityAnalyzer(BaseAIModel):
    """
    Professional Image Quality Analyzer
    
    Provides comprehensive image quality assessment for:
    - Photographers and visual artists
    - Social media content creators
    - E-commerce product photography
    - Print and digital media optimization
    - Platform-specific requirements
    """
    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Initialize image quality analyzer"""
        super().__init__(config or ModelConfig(
            name="image_quality_analyzer",
            model_type=ModelType.IMAGE_MODEL,
            provider=ModelProvider.LOCAL
        ))
        
        # self.performance_monitor = performance_monitor
        # self.metrics_collector = metrics_collector
        
        # Platform requirements
        self.platform_requirements = {
            'instagram': {
                'min_resolution': (1080, 1080),
                'max_resolution': (2048, 2048),
                'aspect_ratios': [(1, 1), (4, 5), (9, 16)],
                'max_file_size_mb': 30,
                'supported_formats': ['JPEG', 'PNG']
            },
            'facebook': {
                'min_resolution': (720, 720),
                'recommended_resolution': (1200, 1200),
                'max_file_size_mb': 4,
                'supported_formats': ['JPEG', 'PNG', 'GIF']
            },
            'pinterest': {
                'min_resolution': (600, 900),
                'recommended_resolution': (1000, 1500),
                'aspect_ratio': (2, 3),
                'max_file_size_mb': 32,
                'supported_formats': ['JPEG', 'PNG']
            },
            'linkedin': {
                'min_resolution': (1200, 627),
                'recommended_resolution': (1200, 1200),
                'max_file_size_mb': 10,
                'supported_formats': ['JPEG', 'PNG', 'GIF']
            },
            'print': {
                'min_dpi': 300,
                'recommended_dpi': 600,
                'color_mode': 'CMYK',
                'bit_depth': 16,
                'supported_formats': ['TIFF', 'PNG']
            },
            'web': {
                'max_file_size_mb': 1,
                'recommended_formats': ['JPEG', 'WebP', 'PNG'],
                'max_resolution': (2048, 2048)
            }
        }
        
        logger.info("Image Quality Analyzer initialized successfully")
    
    @monitor_performance
    async def analyze_quality(
        self,
        image_path: Union[str, Path],
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive image quality analysis
        
        Args:
            image_path: Path to image file
            analysis_options: Analysis configuration options
            
        Returns:
            Dict containing complete image quality analysis
            
        Raises:
            QualityCheckError: If analysis fails
            ContentValidationError: If image file is invalid
        """
        start_time = datetime.now()
        
        try:
            image_path = Path(image_path)
            if not image_path.exists():
                raise ContentValidationError(f"Image file not found: {image_path}")
            
            # Load image
            pil_image = Image.open(image_path)
            cv_image = cv2.imread(str(image_path))
            
            if pil_image is None or cv_image is None:
                raise ContentValidationError(f"Cannot load image file: {image_path}")
            
            # Create quality profile
            profile = ImageQualityProfile()
            await self._extract_basic_properties(pil_image, image_path, profile)
            await self._extract_exif_data(pil_image, profile)
            
            # Perform comprehensive analysis
            await self._analyze_technical_quality(pil_image, cv_image, profile)
            await self._analyze_color_quality(pil_image, cv_image, profile)
            await self._analyze_exposure_quality(pil_image, cv_image, profile)
            await self._analyze_composition(cv_image, profile)
            
            # Calculate quality scores
            self._calculate_quality_scores(profile)
            
            # Generate recommendations
            self._generate_image_recommendations(profile)
            
            # Create metrics
            metrics = ImageQualityMetrics(profile=profile)
            await self._analyze_platform_compliance(profile, metrics)
            await self._analyze_content_characteristics(pil_image, cv_image, metrics)
            
            end_time = datetime.now()
            metrics.processing_time = (end_time - start_time).total_seconds()
            metrics.confidence = self._calculate_confidence(profile)
            
            # Prepare result
            result = {
                'technical_score': profile.technical_score,
                'confidence': metrics.confidence,
                'technical_details': {
                    'resolution': f"{profile.width}x{profile.height}",
                    'megapixels': profile.megapixels,
                    'aspect_ratio': profile.aspect_ratio,
                    'file_size': profile.file_size,
                    'format': profile.format,
                    'color_mode': profile.color_mode,
                    'bit_depth': profile.bit_depth,
                    'sharpness_score': profile.sharpness_score,
                    'sharpness_category': profile.sharpness_category.value,
                    'noise_level': profile.noise_level,
                    'contrast': profile.contrast,
                    'brightness': profile.brightness,
                    'saturation': profile.saturation,
                    'color_accuracy': profile.color_accuracy.value,
                    'exposure_score': profile.exposure_score,
                    'dynamic_range': profile.dynamic_range,
                    'overall_quality_score': profile.overall_quality_score,
                    'quality_level': profile.quality_level
                },
                'technical_recommendations': profile.recommendations,
                'platform_compliance': {
                    'instagram_ready': metrics.instagram_ready,
                    'facebook_ready': metrics.facebook_ready,
                    'pinterest_ready': metrics.pinterest_ready,
                    'linkedin_ready': metrics.linkedin_ready,
                    'print_ready': metrics.print_ready,
                    'web_ready': metrics.web_ready
                },
                'composition_analysis': {
                    'rule_of_thirds_score': profile.composition.rule_of_thirds_score,
                    'symmetry_score': profile.composition.symmetry_score,
                    'balance_score': profile.composition.balance_score,
                    'depth_of_field_score': profile.composition.depth_of_field_score,
                    'composition_score': profile.composition.composition_score
                },
                'exif_data': {
                    'camera_make': profile.camera_make,
                    'camera_model': profile.camera_model,
                    'lens_model': profile.lens_model,
                    'focal_length': profile.focal_length,
                    'aperture': profile.aperture,
                    'shutter_speed': profile.shutter_speed,
                    'iso': profile.iso
                },
                'content_analysis': {
                    'image_type': metrics.image_type,
                    'subject_type': metrics.subject_type,
                    'lighting_type': metrics.lighting_type,
                    'aesthetic_score': metrics.aesthetic_score,
                    'emotional_impact': metrics.emotional_impact,
                    'technical_excellence': metrics.technical_excellence
                },
                'quality_scores': {
                    'artistic_score': profile.artistic_score,
                    'commercial_score': profile.commercial_score
                }
            }
            
            # Log metrics
            self.metrics_collector.track_business_metric(
                metric_name="image_quality_analysis_completed",
                value=1,
                metadata={
                    'quality_score': profile.overall_quality_score,
                    'resolution': f"{profile.width}x{profile.height}",
                    'megapixels': profile.megapixels,
                    'processing_time': metrics.processing_time
                }
            )
            
            logger.info(f"Image quality analysis completed: {profile.overall_quality_score:.2f}/100")
            return result
            
        except Exception as e:
            logger.error(f"Image quality analysis failed: {str(e)}")
            self.metrics_collector.capture_errors("image_quality_analysis_error", str(e))
            raise QualityCheckError(f"Image quality analysis failed: {str(e)}") from e
    
    async def connect(self) -> bool:
        """Connect to image processing services."""



        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from image processing services."""



        return True
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process image quality assessment."""



        return await self.analyze_image_quality(data.get('image_data', b''), 
                                               data.get('profile', ImageQualityProfile()))
    
    async def _extract_basic_properties(
        self,
        pil_image: Image.Image,
        image_path: Path,
        profile: ImageQualityProfile
    ):
        """Extract basic image properties"""



        try:
            profile.width, profile.height = pil_image.size
            profile.megapixels = (profile.width * profile.height) / 1000000
            profile.aspect_ratio = profile.width / profile.height if profile.height > 0 else 1.0
            profile.file_size = image_path.stat().st_size
            profile.format = pil_image.format or "unknown"
            profile.color_mode = pil_image.mode
            
            # Estimate bit depth
            if pil_image.mode in ['1']:
                profile.bit_depth = 1
            elif pil_image.mode in ['L', 'P']:
                profile.bit_depth = 8
            elif pil_image.mode in ['RGB', 'YCbCr', 'LAB', 'HSV']:
                profile.bit_depth = 8
            elif pil_image.mode in ['RGBA', 'CMYK']:
                profile.bit_depth = 8
            elif pil_image.mode in ['I', 'F']:
                profile.bit_depth = 32
            else:
                profile.bit_depth = 8
            
        except Exception as e:
            logger.warning(f"Basic properties extraction failed: {str(e)}")
    
    async def _extract_exif_data(
        self,
        pil_image: Image.Image,
        profile: ImageQualityProfile
    ):
        """Extract EXIF metadata"""



        try:
            exif_data = pil_image._getexif()
            if exif_data is not None:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    if tag == "Make":
                        profile.camera_make = str(value)
                    elif tag == "Model":
                        profile.camera_model = str(value)
                    elif tag == "LensModel":
                        profile.lens_model = str(value)
                    elif tag == "FocalLength":
                        profile.focal_length = str(value)
                    elif tag == "FNumber":
                        profile.aperture = f"f/{value}"
                    elif tag == "ExposureTime":
                        profile.shutter_speed = str(value)
                    elif tag == "ISOSpeedRatings":
                        profile.iso = str(value)
                    elif tag == "Flash":
                        profile.flash = "Yes" if value else "No"
            
        except Exception as e:
            logger.warning(f"EXIF extraction failed: {str(e)}")
    
    async def _analyze_technical_quality(
        self,
        pil_image: Image.Image,
        cv_image: np.ndarray,
        profile: ImageQualityProfile
    ):
        """Analyze technical image quality"""



        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Sharpness analysis using Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness_variance = laplacian.var()
            
            # Normalize sharpness score (0-100)
            profile.sharpness_score = min(100, max(0, (sharpness_variance / 1000) * 100))
            
            # Classify sharpness
            if profile.sharpness_score >= 80:
                profile.sharpness_category = ImageSharpness.EXCELLENT
            elif profile.sharpness_score >= 65:
                profile.sharpness_category = ImageSharpness.GOOD
            elif profile.sharpness_score >= 50:
                profile.sharpness_category = ImageSharpness.ACCEPTABLE
            elif profile.sharpness_score >= 30:
                profile.sharpness_category = ImageSharpness.SOFT
            else:
                profile.sharpness_category = ImageSharpness.BLURRY
            
            # Noise analysis
            profile.noise_level = self._estimate_noise_level(gray)
            
            # Contrast analysis
            profile.contrast = gray.std()
            
            # Brightness analysis
            profile.brightness = gray.mean()
            
            # Saturation analysis (using PIL)
            stat = ImageStat.Stat(pil_image)
            if pil_image.mode == 'RGB':
                profile.saturation = np.std(stat.mean)
            
        except Exception as e:
            logger.warning(f"Technical quality analysis failed: {str(e)}")
    
    def _estimate_noise_level(self, gray_image: np.ndarray) -> float:
        """Estimate noise level in image"""



        try:
            # Use high-pass filter to detect noise
            kernel = np.array([[-1, -1, -1],
                              [-1,  8, -1],
                              [-1, -1, -1]], dtype=np.float32)
            
            filtered = cv2.filter2D(gray_image, cv2.CV_32F, kernel)
            noise_estimate = np.std(filtered)
            
            # Normalize to 0-100 scale
            return min(100, max(0, (noise_estimate / 50) * 100))
            
        except Exception:
            return 20.0  # Default low noise level
    
    async def _analyze_color_quality(
        self,
        pil_image: Image.Image,
        cv_image: np.ndarray,
        profile: ImageQualityProfile
    ):
        """Analyze color quality and accuracy"""



        try:
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
            
            # Analyze color saturation
            h, s, v = cv2.split(hsv)
            saturation_mean = s.mean()
            saturation_std = s.std()
            
            # Color accuracy assessment based on saturation distribution
            if saturation_std < 20 and saturation_mean < 50:
                profile.color_accuracy = ColorAccuracy.UNDERSATURATED
            elif saturation_std < 30 and 50 <= saturation_mean <= 150:
                profile.color_accuracy = ColorAccuracy.ACCURATE
            elif saturation_std < 40 and 120 <= saturation_mean <= 200:
                profile.color_accuracy = ColorAccuracy.ACCEPTABLE
            elif saturation_mean > 200:
                profile.color_accuracy = ColorAccuracy.OVERSATURATED
            else:
                profile.color_accuracy = ColorAccuracy.POOR
            
            # White balance analysis using color temperature estimation
            b, g, r = cv2.split(cv_image)
            avg_b = b.mean()
            avg_g = g.mean()
            avg_r = r.mean()
            
            # Simplified color temperature estimation
            if avg_r > avg_b * 1.3:
                profile.color_temperature = 3000  # Warm
                profile.white_balance_score = 70 if abs(avg_r - avg_b) < 50 else 50
            elif avg_b > avg_r * 1.3:
                profile.color_temperature = 7000  # Cool
                profile.white_balance_score = 70 if abs(avg_b - avg_r) < 50 else 50
            else:
                profile.color_temperature = 5500  # Neutral
                profile.white_balance_score = 90
            
            # Histogram balance analysis
            hist_r = cv2.calcHist([r], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([g], [0], None, [256], [0, 256])
            hist_b = cv2.calcHist([b], [0], None, [256], [0, 256])
            
            # Check for balanced histogram
            hist_balance = 1.0 - abs(np.std([hist_r.mean(), hist_g.mean(), hist_b.mean()]) / 255)
            profile.histogram_balance = hist_balance * 100
            
        except Exception as e:
            logger.warning(f"Color quality analysis failed: {str(e)}")
    
    async def _analyze_exposure_quality(
        self,
        pil_image: Image.Image,
        cv_image: np.ndarray,
        profile: ImageQualityProfile
    ):
        """Analyze exposure and dynamic range"""



        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Calculate histogram
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist_norm = hist.flatten() / hist.sum()
            
            # Analyze clipping
            profile.highlight_clipping = (hist_norm[250:].sum()) * 100
            profile.shadow_clipping = (hist_norm[:5].sum()) * 100
            
            # Dynamic range analysis
            non_zero_bins = np.where(hist_norm > 0.001)[0]
            if len(non_zero_bins) > 0:
                profile.dynamic_range = (non_zero_bins[-1] - non_zero_bins[0]) / 255 * 100
            
            # Exposure score based on histogram distribution
            ideal_distribution = np.ones(256) / 256  # Uniform distribution
            histogram_distance = np.sum(np.abs(hist_norm - ideal_distribution))
            profile.exposure_score = max(0, 100 - histogram_distance * 100)
            
            # Adjust for clipping
            if profile.highlight_clipping > 5 or profile.shadow_clipping > 5:
                profile.exposure_score *= 0.7
            
        except Exception as e:
            logger.warning(f"Exposure analysis failed: {str(e)}")
    
    async def _analyze_composition(
        self,
        cv_image: np.ndarray,
        profile: ImageQualityProfile
    ):
        """Analyze image composition"""



        try:
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            
            # Rule of thirds analysis
            # Divide image into 9 sections and analyze subject placement
            third_w = w // 3
            third_h = h // 3
            
            # Calculate edge density in each third
            edges = cv2.Canny(gray, 50, 150)
            
            # Analyze composition based on edge distribution
            sections = []
            for i in range(3):
                for j in range(3):
                    section = edges[i*third_h:(i+1)*third_h, j*third_w:(j+1)*third_w]
                    edge_density = np.sum(section > 0) / section.size
                    sections.append(edge_density)
            
            # Rule of thirds score (higher edge density at intersection points)
            intersection_points = [sections[1], sections[3], sections[5], sections[7]]
            profile.composition.rule_of_thirds_score = np.mean(intersection_points) * 100
            
            # Symmetry analysis
            left_half = gray[:, :w//2]
            right_half = cv2.flip(gray[:, w//2:], 1)
            
            # Resize to match if needed
            min_width = min(left_half.shape[1], right_half.shape[1])
            left_half = left_half[:, :min_width]
            right_half = right_half[:, :min_width]
            
            symmetry_diff = np.mean(np.abs(left_half.astype(float) - right_half.astype(float)))
            profile.composition.symmetry_score = max(0, 100 - (symmetry_diff / 255 * 100))
            
            # Balance analysis using visual weight
            # Divide into quadrants and analyze weight distribution
            quad_tl = gray[:h//2, :w//2]
            quad_tr = gray[:h//2, w//2:]
            quad_bl = gray[h//2:, :w//2]
            quad_br = gray[h//2:, w//2:]
            
            weights = [np.mean(quad_tl), np.mean(quad_tr), np.mean(quad_bl), np.mean(quad_br)]
            profile.composition.top_left_weight = weights[0] / 255
            profile.composition.top_right_weight = weights[1] / 255
            profile.composition.bottom_left_weight = weights[2] / 255
            profile.composition.bottom_right_weight = weights[3] / 255
            
            # Balance score based on weight distribution
            weight_variance = np.var(weights)
            profile.composition.balance_score = max(0, 100 - (weight_variance / 1000))
            
            # Depth of field analysis using focus gradient
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            focus_map = np.abs(laplacian)
            
            # Analyze focus distribution
            center_focus = focus_map[h//4:3*h//4, w//4:3*w//4].mean()
            edge_focus = (focus_map[:h//4, :].mean() + focus_map[3*h//4:, :].mean() + 
                         focus_map[:, :w//4].mean() + focus_map[:, 3*w//4:].mean()) / 4
            
            if center_focus > edge_focus * 1.5:
                profile.composition.depth_of_field_score = 85  # Good subject isolation
            elif center_focus > edge_focus:
                profile.composition.depth_of_field_score = 70  # Moderate depth
            else:
                profile.composition.depth_of_field_score = 60  # Uniform focus
            
            # Overall composition score
            profile.composition.composition_score = (
                profile.composition.rule_of_thirds_score * 0.3 +
                profile.composition.symmetry_score * 0.2 +
                profile.composition.balance_score * 0.3 +
                profile.composition.depth_of_field_score * 0.2
            )
            
        except Exception as e:
            logger.warning(f"Composition analysis failed: {str(e)}")
    
    def _calculate_quality_scores(self, profile: ImageQualityProfile):
        """Calculate comprehensive quality scores"""



        try:
            # Technical score
            tech_score = (
                profile.sharpness_score * 0.35 +
                (100 - profile.noise_level) * 0.25 +
                min(100, profile.contrast * 2) * 0.20 +
                profile.exposure_score * 0.20
            )
            profile.technical_score = tech_score
            
            # Artistic score
            artistic_score = (
                profile.composition.composition_score * 0.4 +
                profile.white_balance_score * 0.2 +
                profile.histogram_balance * 0.2 +
                min(100, profile.saturation * 2) * 0.2
            )
            profile.artistic_score = artistic_score
            
            # Commercial score
            commercial_factors = []
            
            # Resolution adequacy
            if profile.megapixels >= 24:
                commercial_factors.append(95)  # Excellent for commercial use
            elif profile.megapixels >= 12:
                commercial_factors.append(85)  # Good for most uses
            elif profile.megapixels >= 6:
                commercial_factors.append(75)  # Acceptable for web
            else:
                commercial_factors.append(60)  # Limited use
            
            # Format suitability
            if profile.format.upper() in ['TIFF', 'RAW']:
                commercial_factors.append(95)  # Professional formats
            elif profile.format.upper() == 'PNG':
                commercial_factors.append(85)  # High quality
            elif profile.format.upper() == 'JPEG':
                commercial_factors.append(75)  # Standard quality
            else:
                commercial_factors.append(65)  # Other formats
            
            # Color accuracy for commercial use
            if profile.color_accuracy == ColorAccuracy.PROFESSIONAL:
                commercial_factors.append(95)
            elif profile.color_accuracy == ColorAccuracy.ACCURATE:
                commercial_factors.append(85)
            elif profile.color_accuracy == ColorAccuracy.ACCEPTABLE:
                commercial_factors.append(75)
            else:
                commercial_factors.append(60)
            
            profile.commercial_score = np.mean(commercial_factors)
            
            # Overall quality score
            profile.overall_quality_score = (
                profile.technical_score * 0.4 +
                profile.artistic_score * 0.3 +
                profile.commercial_score * 0.3
            )
            
            # Quality level classification
            if profile.overall_quality_score >= 90:
                profile.quality_level = "professional"
            elif profile.overall_quality_score >= 80:
                profile.quality_level = "excellent"
            elif profile.overall_quality_score >= 70:
                profile.quality_level = "good"
            elif profile.overall_quality_score >= 60:
                profile.quality_level = "acceptable"
            else:
                profile.quality_level = "needs_improvement"
            
        except Exception as e:
            logger.warning(f"Quality score calculation failed: {str(e)}")
            profile.overall_quality_score = 50.0
            profile.quality_level = "needs_improvement"
    
    def _generate_image_recommendations(self, profile: ImageQualityProfile):
        """Generate image-specific recommendations"""
        recommendations = []
        
        # Resolution recommendations
        if profile.megapixels < 6:
            recommendations.append("Increase image resolution for better quality and versatility")
        elif profile.megapixels < 12:
            recommendations.append("Consider higher resolution for professional applications")
        
        # Sharpness recommendations
        if profile.sharpness_category in [ImageSharpness.SOFT, ImageSharpness.BLURRY]:
            recommendations.append("Improve image sharpness - check focus, camera shake, or lens quality")
            recommendations.append("Consider using tripod and proper focusing techniques")
        
        # Noise recommendations
        if profile.noise_level > 30:
            recommendations.append("Reduce image noise - use lower ISO or noise reduction software")
        
        # Exposure recommendations
        if profile.highlight_clipping > 5:
            recommendations.append("Reduce exposure to avoid highlight clipping")
        if profile.shadow_clipping > 5:
            recommendations.append("Increase exposure or use shadow recovery to avoid shadow clipping")
        if profile.dynamic_range < 60:
            recommendations.append("Improve dynamic range using HDR techniques or exposure bracketing")
        
        # Color recommendations
        if profile.color_accuracy == ColorAccuracy.OVERSATURATED:
            recommendations.append("Reduce saturation for more natural colors")
        elif profile.color_accuracy == ColorAccuracy.UNDERSATURATED:
            recommendations.append("Increase saturation for more vibrant colors")
        
        if profile.white_balance_score < 70:
            recommendations.append("Correct white balance for more accurate colors")
        
        # Composition recommendations
        if profile.composition.rule_of_thirds_score < 50:
            recommendations.append("Consider rule of thirds for better composition")
        if profile.composition.balance_score < 60:
            recommendations.append("Improve visual balance in the composition")
        
        profile.recommendations = recommendations
        
        # Enhancement suggestions
        enhancements = []
        if profile.overall_quality_score < 80:
            enhancements.extend([
                "Consider professional color grading or editing",
                "Use RAW format for maximum editing flexibility",
                "Apply selective adjustments to enhance specific areas"
            ])
        
        if profile.composition.composition_score < 70:
            enhancements.extend([
                "Experiment with different compositions and angles",
                "Consider the background and its impact on the subject",
                "Use leading lines and depth to create visual interest"
            ])
        
        profile.enhancement_suggestions = enhancements
    
    async def _analyze_platform_compliance(
        self,
        profile: ImageQualityProfile,
        metrics: ImageQualityMetrics
    ):
        """Analyze compliance with platform requirements"""



        try:
            # Instagram compliance
            instagram_req = self.platform_requirements['instagram']
            metrics.instagram_ready = (
                profile.width >= instagram_req['min_resolution'][0] and
                profile.height >= instagram_req['min_resolution'][1] and
                profile.width <= instagram_req['max_resolution'][0] and
                profile.height <= instagram_req['max_resolution'][1] and
                profile.file_size <= instagram_req['max_file_size_mb'] * 1024**2 and
                profile.format.upper() in instagram_req['supported_formats'] and
                profile.overall_quality_score >= 65
            )
            
            # Facebook compliance
            facebook_req = self.platform_requirements['facebook']
            metrics.facebook_ready = (
                profile.width >= facebook_req['min_resolution'][0] and
                profile.height >= facebook_req['min_resolution'][1] and
                profile.file_size <= facebook_req['max_file_size_mb'] * 1024**2 and
                profile.format.upper() in facebook_req['supported_formats'] and
                profile.overall_quality_score >= 60
            )
            
            # Pinterest compliance
            pinterest_req = self.platform_requirements['pinterest']
            metrics.pinterest_ready = (
                profile.width >= pinterest_req['min_resolution'][0] and
                profile.height >= pinterest_req['min_resolution'][1] and
                abs(profile.aspect_ratio - (2/3)) < 0.2 and  # Close to 2:3 ratio
                profile.file_size <= pinterest_req['max_file_size_mb'] * 1024**2 and
                profile.format.upper() in pinterest_req['supported_formats'] and
                profile.overall_quality_score >= 70
            )
            
            # LinkedIn compliance
            linkedin_req = self.platform_requirements['linkedin']
            metrics.linkedin_ready = (
                profile.width >= linkedin_req['min_resolution'][0] and
                profile.height >= linkedin_req['min_resolution'][1] and
                profile.file_size <= linkedin_req['max_file_size_mb'] * 1024**2 and
                profile.format.upper() in linkedin_req['supported_formats'] and
                profile.overall_quality_score >= 65
            )
            
            # Print compliance
            print_req = self.platform_requirements['print']
            estimated_dpi = 300 if profile.width >= 3000 else 150  # Simplified estimation
            metrics.print_ready = (
                estimated_dpi >= print_req['min_dpi'] and
                profile.bit_depth >= 8 and
                profile.format.upper() in print_req['supported_formats'] and
                profile.overall_quality_score >= 85 and
                profile.color_accuracy in [ColorAccuracy.PROFESSIONAL, ColorAccuracy.ACCURATE]
            )
            
            # Web compliance
            web_req = self.platform_requirements['web']
            metrics.web_ready = (
                profile.file_size <= web_req['max_file_size_mb'] * 1024**2 and
                profile.format.upper() in [f.upper() for f in web_req['recommended_formats']] and
                profile.width <= web_req['max_resolution'][0] and
                profile.height <= web_req['max_resolution'][1] and
                profile.overall_quality_score >= 60
            )
            
        except Exception as e:
            logger.warning(f"Platform compliance analysis failed: {str(e)}")
    
    async def _analyze_content_characteristics(
        self,
        pil_image: Image.Image,
        cv_image: np.ndarray,
        metrics: ImageQualityMetrics
    ):
        """Analyze image content characteristics"""



        try:
            # Image type classification based on aspect ratio and composition
            aspect_ratio = metrics.profile.aspect_ratio
            
            if aspect_ratio > 1.5:
                metrics.image_type = "landscape"
            elif aspect_ratio < 0.7:
                metrics.image_type = "portrait"
            elif 0.9 <= aspect_ratio <= 1.1:
                metrics.image_type = "square"
            else:
                metrics.image_type = "standard"
            
            # Lighting analysis
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            brightness = gray.mean()
            
            if brightness < 80:
                metrics.lighting_type = "low_light"
            elif brightness > 180:
                metrics.lighting_type = "bright"
            else:
                metrics.lighting_type = "normal"
            
            # Subject type estimation (simplified)
            edge_density = np.sum(cv2.Canny(gray, 50, 150) > 0) / gray.size
            
            if edge_density > 0.15:
                metrics.subject_type = "complex_scene"
            elif edge_density > 0.08:
                metrics.subject_type = "detailed_subject"
            else:
                metrics.subject_type = "simple_subject"
            
            # Advanced quality metrics
            metrics.aesthetic_score = (
                metrics.profile.composition.composition_score * 0.4 +
                metrics.profile.artistic_score * 0.3 +
                metrics.profile.white_balance_score * 0.3
            )
            
            metrics.emotional_impact = (
                metrics.profile.contrast * 0.4 +
                metrics.profile.saturation * 0.3 +
                metrics.profile.composition.depth_of_field_score * 0.3
            )
            
            metrics.technical_excellence = metrics.profile.technical_score
            
        except Exception as e:
            logger.warning(f"Content characteristics analysis failed: {str(e)}")
            metrics.image_type = "unknown"
            metrics.subject_type = "unknown"
            metrics.lighting_type = "unknown"
    
    def _calculate_confidence(self, profile: ImageQualityProfile) -> float:
        """Calculate analysis confidence score"""
        confidence = 0.85  # Base confidence
        
        # Adjust based on image resolution
        if profile.megapixels >= 12:
            confidence += 0.1
        elif profile.megapixels < 2:
            confidence -= 0.2
        
        # Adjust based on image quality
        if profile.sharpness_category == ImageSharpness.EXCELLENT:
            confidence += 0.05
        elif profile.sharpness_category in [ImageSharpness.SOFT, ImageSharpness.BLURRY]:
            confidence -= 0.1
        
        # Adjust based on noise level
        if profile.noise_level < 20:
            confidence += 0.05
        elif profile.noise_level > 50:
            confidence -= 0.1
        
        return max(0.4, min(1.0, confidence))


# Global image quality analyzer instance
# image_quality_analyzer = ImageQualityAnalyzer()  # Commented out for testing


async def analyze_image_quality(image_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Convenient function for image quality analysis
    
    Args:
        image_path: Path to image file
        
    Returns:
        Dict containing image quality analysis results
    """



    try:
        result = await image_quality_analyzer.analyze_quality(image_path)
        return result
    except Exception as e:
        logger.error(f"Image quality analysis error: {str(e)}")
        return {
            'error': str(e),
            'success': False
        }
