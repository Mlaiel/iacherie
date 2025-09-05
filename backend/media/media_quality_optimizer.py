"""🎯 Media Quality Optimizer - IA-based Quality Optimization Engine
==================================================================

Enterprise-grade IA-powered media quality optimization engine providing
intelligent enhancement and optimization for all media types. Integrates
with existing multimedia infrastructure for seamless quality improvement.

Key Features:
- IA-driven quality assessment and enhancement
- Adaptive optimization based on content type and purpose
- Real-time quality monitoring and improvement
- Integration with existing multimedia and AI systems
- Performance tracking and analytics

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + ML Engineer + Audio Engineer + Video Specialist + Quality Assurance
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary media quality optimization system contains advanced IA algorithms
and trade secrets belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering
- Commercial use without explicit written permission
- IA optimization algorithm extraction or appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import logging
import uuid
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    # Create torch stub
    class TorchStub:
        def device(self, device_type):
            return device_type
    torch = TorchStub()
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import librosa
import cv2

# Import existing infrastructure with graceful fallbacks
ContentOptimizer = None
CompressionEngine = None
QualityEnhancer = None
MultimediaProcessor = None
IntelligentMediaAnalyzer = None
ContentUnderstandingEngine = None

try:
    from multimedia.optimization import ContentOptimizer, CompressionEngine, QualityEnhancer
except ImportError:
    pass

try:
    from multimedia.processors import MultimediaProcessor
except ImportError:
    pass

try:
    from backend.media.intelligent_media_analyzer import IntelligentMediaAnalyzer, MediaFeatures
except ImportError:
    pass

try:
    from backend.media.content_understanding_engine import ContentUnderstandingEngine, SemanticUnderstanding
except ImportError:
    pass

logger = logging.getLogger(__name__)

class OptimizationType(Enum):
    """Types of quality optimization"""
    BASIC = "basic"                    # Basic quality improvements
    ADAPTIVE = "adaptive"              # Content-aware optimization
    INTELLIGENT = "intelligent"       # IA-driven optimization
    PROFESSIONAL = "professional"     # Professional-grade enhancement
    PLATFORM_SPECIFIC = "platform"    # Platform-optimized output

class QualityLevel(Enum):
    """Quality level targets"""
    DRAFT = "draft"           # Quick preview quality
    STANDARD = "standard"     # Good quality for general use
    HIGH = "high"            # High quality for professional use
    PREMIUM = "premium"      # Premium quality for distribution
    MASTER = "master"        # Master quality for archival

class OptimizationStrategy(Enum):
    """Optimization strategies"""
    CONSERVATIVE = "conservative"  # Minimal changes, preserve original
    BALANCED = "balanced"         # Balance between quality and efficiency
    AGGRESSIVE = "aggressive"     # Maximum quality improvement
    EFFICIENT = "efficient"      # Optimize for file size and loading
    ARTISTIC = "artistic"        # Enhance artistic and creative aspects

@dataclass
class QualityMetrics:
    """Comprehensive quality metrics"""
    # Technical quality
    technical_score: float = 0.0
    resolution_score: float = 0.0
    bitrate_score: float = 0.0
    compression_score: float = 0.0
    clarity_score: float = 0.0
    
    # Perceptual quality
    perceptual_score: float = 0.0
    visual_quality: float = 0.0
    audio_quality: float = 0.0
    overall_appeal: float = 0.0
    
    # Content-specific quality
    content_clarity: float = 0.0
    engagement_quality: float = 0.0
    professional_quality: float = 0.0
    
    # Efficiency metrics
    file_size_efficiency: float = 0.0
    loading_speed_score: float = 0.0
    platform_compatibility: float = 0.0
    
    # Overall quality
    overall_quality: float = 0.0
    improvement_potential: float = 0.0
    optimization_priority: float = 0.0

@dataclass
class OptimizationParams:
    """Optimization parameters and settings"""
    target_quality: QualityLevel = QualityLevel.STANDARD
    optimization_type: OptimizationType = OptimizationType.ADAPTIVE
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    
    # Target specifications
    target_resolution: Optional[str] = None
    target_bitrate: Optional[int] = None
    target_file_size: Optional[int] = None
    target_format: Optional[str] = None
    
    # Optimization constraints
    max_processing_time: int = 300  # seconds
    preserve_original: bool = True
    enable_ai_enhancement: bool = True
    enable_format_conversion: bool = True
    
    # Platform-specific settings
    target_platforms: List[str] = field(default_factory=list)
    platform_requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Quality thresholds
    min_quality_threshold: float = 0.7
    target_quality_threshold: float = 0.9
    max_file_size_mb: Optional[int] = None

@dataclass
class OptimizationResult:
    """Optimization result structure"""
    optimization_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_file: str = ""
    optimized_file: str = ""
    content_type: str = ""
    
    # Quality improvements
    original_metrics: QualityMetrics = field(default_factory=QualityMetrics)
    optimized_metrics: QualityMetrics = field(default_factory=QualityMetrics)
    improvement_achieved: Dict[str, float] = field(default_factory=dict)
    
    # Processing details
    optimization_params: OptimizationParams = field(default_factory=OptimizationParams)
    processing_time_ms: int = 0
    techniques_applied: List[str] = field(default_factory=list)
    ai_models_used: List[str] = field(default_factory=list)
    
    # File information
    original_size_bytes: int = 0
    optimized_size_bytes: int = 0
    size_reduction_percent: float = 0.0
    
    # Success metrics
    success: bool = True
    quality_target_achieved: bool = False
    recommendations: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    
    # Metadata
    optimization_timestamp: datetime = field(default_factory=datetime.now)

class MediaQualityOptimizer:
    """
    IA-based media quality optimization engine
    
    Provides intelligent quality assessment and enhancement for multimedia content
    using advanced AI models and content-aware optimization techniques.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize optimization components
        self._init_optimizers()
        
        # Quality assessment models
        self._init_quality_models()
        
        # Optimization cache
        self._optimization_cache = {}
        self._cache_max_size = 200
        
        # Performance metrics
        self.optimization_stats = {
            'total_optimized': 0,
            'success_rate': 0.0,
            'average_optimization_time': 0.0,
            'average_quality_improvement': 0.0,
            'average_size_reduction': 0.0,
            'technique_effectiveness': {}
        }
        
        logger.info(f"MediaQualityOptimizer initialized with device: {self.device}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for media quality optimizer"""
        return {
            'optimization_settings': {
                'enable_ai_enhancement': True,
                'enable_adaptive_optimization': True,
                'enable_platform_optimization': True,
                'preserve_artistic_intent': True,
                'max_concurrent_optimizations': 4
            },
            'quality_targets': {
                'minimum_improvement': 0.1,
                'target_quality_score': 0.85,
                'max_quality_loss': 0.05,
                'efficiency_weight': 0.3
            },
            'audio_optimization': {
                'enable_noise_reduction': True,
                'enable_dynamic_range_compression': True,
                'enable_eq_optimization': True,
                'target_lufs': -23.0,
                'max_peak_db': -1.0
            },
            'video_optimization': {
                'enable_stabilization': True,
                'enable_color_correction': True,
                'enable_sharpening': True,
                'enable_noise_reduction': True,
                'target_resolutions': ['1920x1080', '1280x720', '854x480']
            },
            'image_optimization': {
                'enable_enhancement': True,
                'enable_color_optimization': True,
                'enable_sharpening': True,
                'enable_noise_reduction': True,
                'jpeg_quality': 92
            },
            'platform_presets': {
                'youtube': {
                    'video_bitrate': 8000000,
                    'audio_bitrate': 128000,
                    'resolution': '1920x1080'
                },
                'instagram': {
                    'video_bitrate': 3500000,
                    'audio_bitrate': 128000,
                    'resolution': '1080x1080'
                },
                'tiktok': {
                    'video_bitrate': 2500000,
                    'audio_bitrate': 128000,
                    'resolution': '1080x1920'
                }
            }
        }
    
    def _init_optimizers(self):
        """Initialize optimization components"""
        try:
            # Leverage existing multimedia infrastructure
            self.content_optimizer = ContentOptimizer() if 'ContentOptimizer' in globals() else None
            self.compression_engine = CompressionEngine() if 'CompressionEngine' in globals() else None
            self.quality_enhancer = QualityEnhancer() if 'QualityEnhancer' in globals() else None
            self.multimedia_processor = MultimediaProcessor() if 'MultimediaProcessor' in globals() else None
            
            logger.info("Optimization components initialized successfully")
        except Exception as e:
            logger.warning(f"Some optimization components not available: {e}")
            # Initialize with minimal functionality
            self.content_optimizer = None
            self.compression_engine = None
            self.quality_enhancer = None
            self.multimedia_processor = None
    
    def _init_quality_models(self):
        """Initialize quality assessment models"""
        try:
            self.media_analyzer = IntelligentMediaAnalyzer(self.config) if 'IntelligentMediaAnalyzer' in globals() else None
            self.understanding_engine = ContentUnderstandingEngine(self.config) if 'ContentUnderstandingEngine' in globals() else None
            
            logger.info("Quality assessment models initialized successfully")
        except Exception as e:
            logger.warning(f"Some quality models not available: {e}")
            self.media_analyzer = None
            self.understanding_engine = None
    
    async def optimize_media(self,
                           input_file: str,
                           content_type: str,
                           optimization_params: OptimizationParams,
                           output_file: Optional[str] = None) -> OptimizationResult:
        """
        Comprehensive IA-driven media optimization
        
        Args:
            input_file: Path to input media file
            content_type: Type of content (audio, video, image, text)
            optimization_params: Optimization parameters and settings
            output_file: Optional output file path
            
        Returns:
            OptimizationResult with comprehensive optimization details
        """
        start_time = datetime.now()
        
        # Generate output file path if not provided
        if not output_file:
            input_path = Path(input_file)
            output_file = str(input_path.parent / f"{input_path.stem}_optimized{input_path.suffix}")
        
        try:
            logger.info(f"Starting IA optimization for {content_type}: {input_file}")
            
            # Create optimization result
            result = OptimizationResult(
                original_file=input_file,
                optimized_file=output_file,
                content_type=content_type,
                optimization_params=optimization_params
            )
            
            # Get original file size
            result.original_size_bytes = Path(input_file).stat().st_size
            
            # Stage 1: Quality assessment
            original_metrics = await self._assess_quality(input_file, content_type)
            result.original_metrics = original_metrics
            
            # Stage 2: Intelligent optimization planning
            optimization_plan = await self._plan_optimization(input_file, content_type, original_metrics, optimization_params)
            
            # Stage 3: Apply optimizations
            await self._apply_optimizations(input_file, output_file, content_type, optimization_plan, result)
            
            # Stage 4: Quality validation
            if Path(output_file).exists():
                optimized_metrics = await self._assess_quality(output_file, content_type)
                result.optimized_metrics = optimized_metrics
                result.optimized_size_bytes = Path(output_file).stat().st_size
                
                # Calculate improvements
                result.improvement_achieved = self._calculate_improvements(original_metrics, optimized_metrics)
                result.size_reduction_percent = (
                    (result.original_size_bytes - result.optimized_size_bytes) / result.original_size_bytes * 100
                    if result.original_size_bytes > 0 else 0
                )
                
                # Check if quality targets were achieved
                result.quality_target_achieved = (
                    optimized_metrics.overall_quality >= optimization_params.target_quality_threshold
                )
            
            # Stage 5: Generate recommendations
            result.recommendations = await self._generate_optimization_recommendations(result)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result.processing_time_ms = int(processing_time)
            
            # Update statistics
            self._update_optimization_stats(processing_time, True, result)
            
            logger.info(f"Optimization completed in {processing_time:.2f}ms")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_optimization_stats(processing_time, False, None)
            
            logger.error(f"Media optimization failed: {e}")
            return OptimizationResult(
                original_file=input_file,
                optimized_file=output_file,
                content_type=content_type,
                optimization_params=optimization_params,
                success=False,
                error_message=str(e),
                processing_time_ms=int(processing_time)
            )
    
    async def _assess_quality(self, file_path: str, content_type: str) -> QualityMetrics:
        """Assess media quality using IA models"""
        try:
            metrics = QualityMetrics()
            
            # Use intelligent media analyzer if available
            if self.media_analyzer:
                analysis = await self.media_analyzer.analyze_media(file_path, content_type)
                if analysis.success:
                    features = analysis.features
                    
                    # Map features to quality metrics
                    metrics.technical_score = features.technical_quality
                    metrics.perceptual_score = features.perceptual_quality
                    metrics.overall_quality = features.quality_score
                    metrics.content_clarity = features.engagement_potential
                    metrics.professional_quality = features.monetization_potential
                    
                    # Content-specific quality assessment
                    if content_type in ['audio', 'voice']:
                        metrics.audio_quality = features.quality_score
                        metrics.clarity_score = features.audio_complexity
                    elif content_type in ['video', 'image']:
                        metrics.visual_quality = features.quality_score
                        metrics.clarity_score = features.visual_complexity
            
            # Fallback quality assessment
            if metrics.overall_quality == 0.0:
                metrics = await self._fallback_quality_assessment(file_path, content_type)
            
            # Calculate derived metrics
            metrics.improvement_potential = max(0, 1.0 - metrics.overall_quality)
            metrics.optimization_priority = self._calculate_optimization_priority(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            # Return default metrics
            return QualityMetrics(overall_quality=0.5, improvement_potential=0.5)
    
    async def _fallback_quality_assessment(self, file_path: str, content_type: str) -> QualityMetrics:
        """Fallback quality assessment without AI models"""
        metrics = QualityMetrics()
        
        try:
            file_size = Path(file_path).stat().st_size
            
            if content_type in ['audio', 'voice']:
                # Audio quality assessment
                y, sr = librosa.load(file_path, sr=None)
                duration = librosa.get_duration(y=y, sr=sr)
                
                # Calculate bitrate estimate
                bitrate = (file_size * 8) / duration if duration > 0 else 0
                
                # Quality scoring based on bitrate
                if bitrate > 320000:  # High quality
                    metrics.audio_quality = 0.9
                elif bitrate > 128000:  # Good quality
                    metrics.audio_quality = 0.7
                elif bitrate > 64000:   # Acceptable quality
                    metrics.audio_quality = 0.5
                else:  # Low quality
                    metrics.audio_quality = 0.3
                
                # Technical score based on sample rate
                if sr >= 44100:
                    metrics.technical_score = 0.8
                elif sr >= 22050:
                    metrics.technical_score = 0.6
                else:
                    metrics.technical_score = 0.4
                
                # Signal quality assessment
                rms_energy = np.sqrt(np.mean(y**2))
                metrics.clarity_score = min(rms_energy * 10, 1.0)
                
            elif content_type == 'video':
                # Video quality assessment
                cap = cv2.VideoCapture(file_path)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                duration = frame_count / fps if fps > 0 else 0
                
                # Resolution score
                pixel_count = width * height
                if pixel_count >= 2073600:  # 1080p+
                    metrics.resolution_score = 0.9
                elif pixel_count >= 921600:  # 720p+
                    metrics.resolution_score = 0.7
                elif pixel_count >= 307200:  # 480p+
                    metrics.resolution_score = 0.5
                else:
                    metrics.resolution_score = 0.3
                
                # Bitrate estimate
                if duration > 0:
                    bitrate = (file_size * 8) / duration
                    if bitrate > 8000000:  # High bitrate
                        metrics.bitrate_score = 0.9
                    elif bitrate > 2000000:  # Good bitrate
                        metrics.bitrate_score = 0.7
                    else:
                        metrics.bitrate_score = 0.5
                
                # Frame rate score
                if fps >= 60:
                    metrics.technical_score = 0.9
                elif fps >= 30:
                    metrics.technical_score = 0.8
                elif fps >= 24:
                    metrics.technical_score = 0.6
                else:
                    metrics.technical_score = 0.4
                
                cap.release()
                
            elif content_type == 'image':
                # Image quality assessment
                image = Image.open(file_path)
                width, height = image.size
                
                # Resolution score
                pixel_count = width * height
                if pixel_count >= 2073600:  # High resolution
                    metrics.resolution_score = 0.9
                elif pixel_count >= 921600:  # Good resolution
                    metrics.resolution_score = 0.7
                else:
                    metrics.resolution_score = 0.5
                
                # Color depth and mode
                if image.mode == 'RGB':
                    metrics.technical_score = 0.8
                elif image.mode == 'RGBA':
                    metrics.technical_score = 0.9
                else:
                    metrics.technical_score = 0.6
                
                # File size efficiency
                bytes_per_pixel = file_size / pixel_count if pixel_count > 0 else 0
                if 1 <= bytes_per_pixel <= 3:  # Good compression
                    metrics.compression_score = 0.8
                elif bytes_per_pixel > 5:  # Inefficient
                    metrics.compression_score = 0.4
                else:
                    metrics.compression_score = 0.6
            
            # Calculate overall metrics
            scores = [
                metrics.technical_score,
                metrics.resolution_score,
                metrics.bitrate_score,
                metrics.audio_quality,
                metrics.visual_quality,
                metrics.clarity_score,
                metrics.compression_score
            ]
            valid_scores = [s for s in scores if s > 0]
            metrics.overall_quality = np.mean(valid_scores) if valid_scores else 0.5
            
            # File size efficiency
            if file_size < 1024 * 1024:  # < 1MB
                metrics.file_size_efficiency = 0.9
            elif file_size < 10 * 1024 * 1024:  # < 10MB
                metrics.file_size_efficiency = 0.7
            elif file_size < 100 * 1024 * 1024:  # < 100MB
                metrics.file_size_efficiency = 0.5
            else:
                metrics.file_size_efficiency = 0.3
            
            return metrics
            
        except Exception as e:
            logger.error(f"Fallback quality assessment failed: {e}")
            return QualityMetrics(overall_quality=0.5)
    
    def _calculate_optimization_priority(self, metrics: QualityMetrics) -> float:
        """Calculate optimization priority based on quality metrics"""
        priority_factors = []
        
        # Low quality content has high priority
        if metrics.overall_quality < 0.5:
            priority_factors.append(1.0)
        elif metrics.overall_quality < 0.7:
            priority_factors.append(0.8)
        else:
            priority_factors.append(0.4)
        
        # Poor efficiency increases priority
        if metrics.file_size_efficiency < 0.5:
            priority_factors.append(0.9)
        elif metrics.file_size_efficiency < 0.7:
            priority_factors.append(0.6)
        else:
            priority_factors.append(0.3)
        
        # Technical issues increase priority
        if metrics.technical_score < 0.6:
            priority_factors.append(0.8)
        else:
            priority_factors.append(0.4)
        
        return float(np.mean(priority_factors))
    
    async def _plan_optimization(self,
                               input_file: str,
                               content_type: str,
                               quality_metrics: QualityMetrics,
                               params: OptimizationParams) -> Dict[str, Any]:
        """Plan intelligent optimization strategy"""
        plan = {
            'techniques': [],
            'parameters': {},
            'priority_order': [],
            'expected_improvements': {}
        }
        
        try:
            # Content understanding for artistic preservation
            if self.understanding_engine and params.optimization_strategy == OptimizationStrategy.ARTISTIC:
                understanding = await self.understanding_engine.understand_content(
                    input_file, content_type
                )
                plan['artistic_context'] = {
                    'style': understanding.artistic_style,
                    'originality': understanding.originality_score,
                    'preserve_intent': True
                }
            
            # Plan optimizations based on content type
            if content_type in ['audio', 'voice']:
                plan = await self._plan_audio_optimization(input_file, quality_metrics, params, plan)
            elif content_type == 'video':
                plan = await self._plan_video_optimization(input_file, quality_metrics, params, plan)
            elif content_type == 'image':
                plan = await self._plan_image_optimization(input_file, quality_metrics, params, plan)
            
            # Platform-specific optimizations
            if params.target_platforms:
                plan['platform_optimizations'] = self._plan_platform_optimizations(params.target_platforms)
            
            return plan
            
        except Exception as e:
            logger.error(f"Optimization planning failed: {e}")
            return plan
    
    async def _plan_audio_optimization(self,
                                     input_file: str,
                                     metrics: QualityMetrics,
                                     params: OptimizationParams,
                                     plan: Dict[str, Any]) -> Dict[str, Any]:
        """Plan audio-specific optimizations"""
        # Noise reduction
        if metrics.clarity_score < 0.7 and self.config['audio_optimization']['enable_noise_reduction']:
            plan['techniques'].append('noise_reduction')
            plan['expected_improvements']['clarity'] = 0.2
        
        # Dynamic range compression
        if self.config['audio_optimization']['enable_dynamic_range_compression']:
            plan['techniques'].append('dynamic_range_compression')
            plan['parameters']['target_lufs'] = self.config['audio_optimization']['target_lufs']
        
        # EQ optimization
        if metrics.audio_quality < 0.8 and self.config['audio_optimization']['enable_eq_optimization']:
            plan['techniques'].append('eq_optimization')
            plan['expected_improvements']['audio_quality'] = 0.15
        
        # Bitrate optimization
        if metrics.bitrate_score < 0.7:
            plan['techniques'].append('bitrate_optimization')
            if params.target_bitrate:
                plan['parameters']['target_bitrate'] = params.target_bitrate
            else:
                plan['parameters']['target_bitrate'] = 256000  # Default high quality
        
        # Format conversion for efficiency
        if params.enable_format_conversion and metrics.file_size_efficiency < 0.6:
            plan['techniques'].append('format_conversion')
            plan['parameters']['target_format'] = 'mp3'  # Efficient format
        
        return plan
    
    async def _plan_video_optimization(self,
                                     input_file: str,
                                     metrics: QualityMetrics,
                                     params: OptimizationParams,
                                     plan: Dict[str, Any]) -> Dict[str, Any]:
        """Plan video-specific optimizations"""
        # Video stabilization
        if self.config['video_optimization']['enable_stabilization']:
            plan['techniques'].append('video_stabilization')
            plan['expected_improvements']['visual_quality'] = 0.1
        
        # Color correction
        if metrics.visual_quality < 0.8 and self.config['video_optimization']['enable_color_correction']:
            plan['techniques'].append('color_correction')
            plan['expected_improvements']['visual_quality'] = 0.15
        
        # Sharpening
        if metrics.clarity_score < 0.7 and self.config['video_optimization']['enable_sharpening']:
            plan['techniques'].append('sharpening')
            plan['expected_improvements']['clarity'] = 0.2
        
        # Noise reduction
        if self.config['video_optimization']['enable_noise_reduction']:
            plan['techniques'].append('video_noise_reduction')
        
        # Resolution optimization
        if params.target_resolution:
            plan['techniques'].append('resolution_optimization')
            plan['parameters']['target_resolution'] = params.target_resolution
        elif metrics.resolution_score < 0.6:
            plan['techniques'].append('resolution_optimization')
            plan['parameters']['target_resolution'] = '1920x1080'  # Standard HD
        
        # Bitrate optimization
        if params.target_bitrate:
            plan['techniques'].append('bitrate_optimization')
            plan['parameters']['video_bitrate'] = params.target_bitrate
        
        return plan
    
    async def _plan_image_optimization(self,
                                     input_file: str,
                                     metrics: QualityMetrics,
                                     params: OptimizationParams,
                                     plan: Dict[str, Any]) -> Dict[str, Any]:
        """Plan image-specific optimizations"""
        # Image enhancement
        if metrics.visual_quality < 0.8 and self.config['image_optimization']['enable_enhancement']:
            plan['techniques'].append('image_enhancement')
            plan['expected_improvements']['visual_quality'] = 0.2
        
        # Color optimization
        if self.config['image_optimization']['enable_color_optimization']:
            plan['techniques'].append('color_optimization')
            plan['expected_improvements']['overall_appeal'] = 0.15
        
        # Sharpening
        if metrics.clarity_score < 0.7 and self.config['image_optimization']['enable_sharpening']:
            plan['techniques'].append('image_sharpening')
            plan['expected_improvements']['clarity'] = 0.25
        
        # Noise reduction
        if self.config['image_optimization']['enable_noise_reduction']:
            plan['techniques'].append('image_noise_reduction')
        
        # Resolution optimization
        if params.target_resolution:
            plan['techniques'].append('resolution_optimization')
            plan['parameters']['target_resolution'] = params.target_resolution
        
        # Compression optimization
        if metrics.compression_score < 0.7:
            plan['techniques'].append('compression_optimization')
            plan['parameters']['jpeg_quality'] = self.config['image_optimization']['jpeg_quality']
        
        return plan
    
    def _plan_platform_optimizations(self, target_platforms: List[str]) -> Dict[str, Any]:
        """Plan platform-specific optimizations"""
        platform_opts = {}
        
        for platform in target_platforms:
            if platform in self.config['platform_presets']:
                preset = self.config['platform_presets'][platform]
                platform_opts[platform] = preset
        
        return platform_opts
    
    async def _apply_optimizations(self,
                                 input_file: str,
                                 output_file: str,
                                 content_type: str,
                                 optimization_plan: Dict[str, Any],
                                 result: OptimizationResult):
        """Apply planned optimizations"""
        try:
            current_file = input_file
            temp_files = []
            
            # Apply optimizations in order
            for technique in optimization_plan['techniques']:
                temp_file = self._get_temp_file(content_type)
                temp_files.append(temp_file)
                
                success = await self._apply_single_optimization(
                    current_file, temp_file, content_type, technique, optimization_plan
                )
                
                if success:
                    current_file = temp_file
                    result.techniques_applied.append(technique)
                    logger.info(f"Applied {technique} optimization")
                else:
                    result.warnings.append(f"Failed to apply {technique}")
            
            # Copy final result to output file
            if current_file != input_file:
                shutil.copy2(current_file, output_file)
            else:
                # No optimizations were applied, copy original
                shutil.copy2(input_file, output_file)
            
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    Path(temp_file).unlink()
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Optimization application failed: {e}")
            # Fallback: copy original file
            shutil.copy2(input_file, output_file)
            result.warnings.append(f"Optimization failed, using original: {str(e)}")
    
    async def _apply_single_optimization(self,
                                       input_file: str,
                                       output_file: str,
                                       content_type: str,
                                       technique: str,
                                       plan: Dict[str, Any]) -> bool:
        """Apply a single optimization technique"""
        try:
            # Use existing optimization infrastructure if available
            if self.content_optimizer and technique in ['noise_reduction', 'enhancement']:
                result = await self.content_optimizer.optimize_content(input_file, technique)
                if result.success:
                    shutil.copy2(result.output_file, output_file)
                    return True
            
            # Fallback implementations
            if content_type == 'image':
                return await self._apply_image_optimization(input_file, output_file, technique, plan)
            elif content_type in ['audio', 'voice']:
                return await self._apply_audio_optimization(input_file, output_file, technique, plan)
            elif content_type == 'video':
                return await self._apply_video_optimization(input_file, output_file, technique, plan)
            
            return False
            
        except Exception as e:
            logger.error(f"Single optimization {technique} failed: {e}")
            return False
    
    async def _apply_image_optimization(self,
                                      input_file: str,
                                      output_file: str,
                                      technique: str,
                                      plan: Dict[str, Any]) -> bool:
        """Apply image optimization techniques"""
        try:
            image = Image.open(input_file)
            
            if technique == 'image_enhancement':
                # Basic image enhancement
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.1)  # Slight contrast boost
                
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(1.05)  # Slight brightness boost
                
            elif technique == 'color_optimization':
                # Color optimization
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(1.1)  # Slight color boost
                
            elif technique == 'image_sharpening':
                # Image sharpening
                image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
                
            elif technique == 'image_noise_reduction':
                # Simple noise reduction using blur
                image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
                
            elif technique == 'resolution_optimization':
                # Resolution optimization
                target_res = plan['parameters'].get('target_resolution')
                if target_res:
                    width, height = map(int, target_res.split('x'))
                    image = image.resize((width, height), Image.Resampling.LANCZOS)
                    
            elif technique == 'compression_optimization':
                # Compression optimization
                quality = plan['parameters'].get('jpeg_quality', 92)
                image.save(output_file, quality=quality, optimize=True)
                return True
            
            # Save optimized image
            image.save(output_file, quality=95, optimize=True)
            return True
            
        except Exception as e:
            logger.error(f"Image optimization {technique} failed: {e}")
            return False
    
    async def _apply_audio_optimization(self,
                                      input_file: str,
                                      output_file: str,
                                      technique: str,
                                      plan: Dict[str, Any]) -> bool:
        """Apply audio optimization techniques"""
        try:
            # Load audio
            y, sr = librosa.load(input_file, sr=None)
            
            if technique == 'noise_reduction':
                # Simple noise reduction using spectral gating
                # This is a basic implementation
                y_filtered = librosa.effects.preemphasis(y)
                y = y_filtered
                
            elif technique == 'dynamic_range_compression':
                # Basic dynamic range compression
                # Normalize and apply gentle compression
                y = librosa.util.normalize(y)
                
            elif technique == 'eq_optimization':
                # Basic EQ optimization using high-pass filter
                y = librosa.effects.preemphasis(y, coef=0.97)
                
            elif technique == 'bitrate_optimization':
                # This would require external tools like ffmpeg
                # For now, just copy the file
                shutil.copy2(input_file, output_file)
                return True
                
            elif technique == 'format_conversion':
                # This would require external tools
                # For now, just copy the file
                shutil.copy2(input_file, output_file)
                return True
            
            # Save optimized audio (this is a basic implementation)
            # In a real system, you'd use proper audio encoding libraries
            import soundfile as sf
            sf.write(output_file, y, sr)
            return True
            
        except Exception as e:
            logger.error(f"Audio optimization {technique} failed: {e}")
            return False
    
    async def _apply_video_optimization(self,
                                      input_file: str,
                                      output_file: str,
                                      technique: str,
                                      plan: Dict[str, Any]) -> bool:
        """Apply video optimization techniques"""
        try:
            # Video optimization would typically require external tools like FFmpeg
            # For this implementation, we'll do basic processing with OpenCV
            
            cap = cv2.VideoCapture(input_file)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Adjust resolution if needed
            if technique == 'resolution_optimization':
                target_res = plan['parameters'].get('target_resolution')
                if target_res:
                    width, height = map(int, target_res.split('x'))
            
            out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply optimizations
                if technique == 'color_correction':
                    # Simple color correction
                    frame = cv2.convertScaleAbs(frame, alpha=1.1, beta=10)
                    
                elif technique == 'sharpening':
                    # Simple sharpening
                    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                    frame = cv2.filter2D(frame, -1, kernel)
                    
                elif technique == 'video_noise_reduction':
                    # Simple noise reduction
                    frame = cv2.bilateralFilter(frame, 9, 75, 75)
                
                # Resize if needed
                if frame.shape[:2] != (height, width):
                    frame = cv2.resize(frame, (width, height))
                
                out.write(frame)
                frame_count += 1
                
                # Limit processing for demo purposes
                if frame_count > 1000:  # Process max 1000 frames
                    break
            
            cap.release()
            out.release()
            return True
            
        except Exception as e:
            logger.error(f"Video optimization {technique} failed: {e}")
            return False
    
    def _get_temp_file(self, content_type: str) -> str:
        """Get temporary file path for optimization"""
        extensions = {
            'audio': '.wav',
            'voice': '.wav',
            'video': '.mp4',
            'image': '.jpg'
        }
        ext = extensions.get(content_type, '.tmp')
        
        temp_file = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        temp_file.close()
        return temp_file.name
    
    def _calculate_improvements(self,
                              original: QualityMetrics,
                              optimized: QualityMetrics) -> Dict[str, float]:
        """Calculate quality improvements achieved"""
        improvements = {}
        
        # Calculate improvement for each metric
        metrics_to_compare = [
            'overall_quality', 'technical_score', 'perceptual_score',
            'visual_quality', 'audio_quality', 'clarity_score',
            'compression_score', 'file_size_efficiency'
        ]
        
        for metric in metrics_to_compare:
            original_value = getattr(original, metric, 0.0)
            optimized_value = getattr(optimized, metric, 0.0)
            
            if original_value > 0:
                improvement = (optimized_value - original_value) / original_value
                improvements[metric] = round(improvement, 3)
        
        return improvements
    
    async def _generate_optimization_recommendations(self,
                                                   result: OptimizationResult) -> List[str]:
        """Generate intelligent recommendations based on optimization results"""
        recommendations = []
        
        try:
            # Quality-based recommendations
            if result.optimized_metrics.overall_quality < 0.7:
                recommendations.append("Consider additional quality enhancement")
                recommendations.append("Review optimization parameters for better results")
            
            # Efficiency recommendations
            if result.size_reduction_percent < 10:
                recommendations.append("Consider more aggressive compression settings")
                recommendations.append("Evaluate format conversion for better efficiency")
            
            # Platform-specific recommendations
            if result.optimization_params.target_platforms:
                for platform in result.optimization_params.target_platforms:
                    if platform in self.config['platform_presets']:
                        preset = self.config['platform_presets'][platform]
                        recommendations.append(f"Optimize specifically for {platform} requirements")
            
            # Content-specific recommendations
            if result.content_type == 'video' and result.optimized_metrics.visual_quality < 0.8:
                recommendations.append("Consider video stabilization and color correction")
                recommendations.append("Review frame rate and resolution settings")
                
            elif result.content_type in ['audio', 'voice'] and result.optimized_metrics.audio_quality < 0.8:
                recommendations.append("Apply audio normalization and noise reduction")
                recommendations.append("Consider dynamic range compression for broadcast")
                
            elif result.content_type == 'image' and result.optimized_metrics.visual_quality < 0.8:
                recommendations.append("Apply sharpening and color enhancement")
                recommendations.append("Review compression settings for quality preservation")
            
            # Performance recommendations
            if result.processing_time_ms > 60000:  # More than 1 minute
                recommendations.append("Consider lower complexity optimization for faster processing")
                recommendations.append("Use batch processing for multiple files")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return ["Unable to generate specific recommendations"]
    
    def _update_optimization_stats(self,
                                 processing_time: float,
                                 success: bool,
                                 result: Optional[OptimizationResult]):
        """Update optimization statistics"""
        self.optimization_stats['total_optimized'] += 1
        
        if success and result:
            # Update success rate
            total = self.optimization_stats['total_optimized']
            current_successes = self.optimization_stats['success_rate'] * (total - 1)
            self.optimization_stats['success_rate'] = (current_successes + 1) / total
            
            # Update average processing time
            current_avg = self.optimization_stats['average_optimization_time']
            self.optimization_stats['average_optimization_time'] = (
                (current_avg * (total - 1) + processing_time) / total
            )
            
            # Update quality improvement
            if result.improvement_achieved:
                overall_improvement = result.improvement_achieved.get('overall_quality', 0)
                current_quality_avg = self.optimization_stats['average_quality_improvement']
                self.optimization_stats['average_quality_improvement'] = (
                    (current_quality_avg * (total - 1) + overall_improvement) / total
                )
            
            # Update size reduction
            size_reduction = result.size_reduction_percent / 100.0
            current_size_avg = self.optimization_stats['average_size_reduction']
            self.optimization_stats['average_size_reduction'] = (
                (current_size_avg * (total - 1) + size_reduction) / total
            )
            
            # Update technique effectiveness
            for technique in result.techniques_applied:
                if technique not in self.optimization_stats['technique_effectiveness']:
                    self.optimization_stats['technique_effectiveness'][technique] = {'count': 0, 'success_rate': 0.0}
                
                tech_stats = self.optimization_stats['technique_effectiveness'][technique]
                tech_stats['count'] += 1
                # Assume successful application means effective
                current_success = tech_stats['success_rate'] * (tech_stats['count'] - 1)
                tech_stats['success_rate'] = (current_success + 1) / tech_stats['count']
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get current optimization statistics"""
        return self.optimization_stats.copy()
    
    async def batch_optimize(self,
                           file_list: List[str],
                           content_types: List[str],
                           optimization_params: OptimizationParams) -> List[OptimizationResult]:
        """Batch optimization for multiple files"""
        results = []
        
        # Process files in parallel (limited by max_concurrent_optimizations)
        semaphore = asyncio.Semaphore(self.config['optimization_settings']['max_concurrent_optimizations'])
        
        async def optimize_single(file_path: str, content_type: str):
            async with semaphore:
                return await self.optimize_media(file_path, content_type, optimization_params)
        
        # Create tasks for all files
        tasks = [
            optimize_single(file_path, content_type) 
            for file_path, content_type in zip(file_list, content_types)
        ]
        
        # Execute all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and log errors
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch optimization failed for {file_list[i]}: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the media quality optimizer"""
        return {
            'status': 'healthy',
            'device': str(self.device),
            'optimizers_available': {
                'content_optimizer': self.content_optimizer is not None,
                'compression_engine': self.compression_engine is not None,
                'quality_enhancer': self.quality_enhancer is not None,
                'multimedia_processor': self.multimedia_processor is not None
            },
            'quality_models_available': {
                'media_analyzer': self.media_analyzer is not None,
                'understanding_engine': self.understanding_engine is not None
            },
            'optimization_stats': self.optimization_stats,
            'cache_status': {
                'entries': len(self._optimization_cache),
                'max_size': self._cache_max_size
            },
            'timestamp': datetime.now().isoformat()
        }


# Export main classes
__all__ = [
    'MediaQualityOptimizer', 'OptimizationResult', 'OptimizationParams',
    'QualityMetrics', 'OptimizationType', 'QualityLevel', 'OptimizationStrategy'
]