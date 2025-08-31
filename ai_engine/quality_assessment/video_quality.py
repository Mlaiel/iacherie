"""Video Quality Assessment Module

Advanced video quality analysis for content creators, filmmakers, and video influencers.
Implements professional video metrics and industry-standard quality assessment.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING ⚠️
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

from ..core.base_models import BaseAIModel, ModelConfig, ModelType, ModelProvider
from ..core.exceptions import QualityCheckError, ContentValidationError
from ..core.performance import PerformanceMonitor, monitor_performance
from ..core.metrics import MetricsCollector, metrics_collector

logger = logging.getLogger(__name__)


class VideoResolution(Enum):
    """Standard video resolutions"""    SD_480P = "480p"
    HD_720P = "720p"
    FULL_HD_1080P = "1080p"
    QHD_1440P = "1440p"
    UHD_4K = "4k"
    UHD_8K = "8k"


class FrameRate(Enum):
    """Standard frame rates"""    CINEMA_24 = 24
    PAL_25 = 25
    NTSC_30 = 30
    WEB_60 = 60
    GAMING_120 = 120
    HIGH_SPEED_240 = 240


class Bitrate(Enum):
    """Bitrate quality levels"""    LOW = "low"          # < 1 Mbps
    MEDIUM = "medium"    # 1-5 Mbps
    HIGH = "high"        # 5-15 Mbps
    VERY_HIGH = "very_high"  # 15-50 Mbps
    EXTREME = "extreme"  # > 50 Mbps


class CompressionArtifacts(Enum):
    """Compression artifact levels"""    NONE = "none"
    MINIMAL = "minimal"
    MODERATE = "moderate"
    SEVERE = "severe"
    EXTREME = "extreme"


@dataclass
class VideoQualityProfile:
    """Comprehensive video quality profile"""    # Basic properties
    width: int = field(default=0)
    height: int = field(default=0)
    frame_rate: float = field(default=0.0)
    duration: float = field(default=0.0)
    total_frames: int = field(default=0)
    file_size: int = field(default=0)
    codec: str = field(default="unknown")
    
    # Quality metrics
    bitrate: float = field(default=0.0)  # Mbps
    bitrate_category: Bitrate = field(default=Bitrate.MEDIUM)
    
    # Visual quality
    sharpness_score: float = field(default=0.0)
    contrast_score: float = field(default=0.0)
    brightness_score: float = field(default=0.0)
    color_accuracy: float = field(default=0.0)
    saturation_score: float = field(default=0.0)
    
    # Technical quality
    noise_level: float = field(default=0.0)
    blocking_artifacts: float = field(default=0.0)
    motion_blur: float = field(default=0.0)
    compression_artifacts: CompressionArtifacts = field(default=CompressionArtifacts.MINIMAL)
    
    # Motion analysis
    motion_intensity: float = field(default=0.0)
    camera_stability: float = field(default=0.0)
    scene_complexity: float = field(default=0.0)
    
    # Audio-visual sync
    av_sync_offset: float = field(default=0.0)  # milliseconds
    lip_sync_quality: float = field(default=0.0)
    
    # Quality scores
    technical_score: float = field(default=0.0)
    visual_score: float = field(default=0.0)
    motion_score: float = field(default=0.0)
    encoding_score: float = field(default=0.0)
    
    # Overall quality
    overall_quality_score: float = field(default=0.0)
    quality_level: str = field(default="acceptable")
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    enhancement_suggestions: List[str] = field(default_factory=list)


@dataclass
class VideoQualityMetrics:
    """Video quality metrics container"""    profile: VideoQualityProfile = field(default_factory=VideoQualityProfile)
    
    # Platform compliance
    youtube_ready: bool = field(default=False)
    instagram_ready: bool = field(default=False)
    tiktok_ready: bool = field(default=False)
    facebook_ready: bool = field(default=False)
    broadcast_ready: bool = field(default=False)
    cinema_ready: bool = field(default=False)
    
    # Content analysis
    content_type: str = field(default="unknown")  # documentary, entertainment, education, etc.
    scene_types: List[str] = field(default_factory=list)  # indoor, outdoor, low_light, etc.
    motion_type: str = field(default="unknown")  # static, slow, moderate, fast, extreme
    
    # Advanced metrics
    perceptual_quality: float = field(default=0.0)
    temporal_consistency: float = field(default=0.0)
    spatial_quality: float = field(default=0.0)
    
    # Metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = field(default=0.0)
    confidence: float = field(default=0.0)


class VideoQualityAnalyzer(BaseAIModel):
    """    Professional Video Quality Analyzer
    
    Provides comprehensive video quality assessment for:
    - Content creators and influencers
    - Filmmakers and videographers
    - Streaming platform optimization
    - Broadcast compliance checking
    - Social media content optimization
    """    
    def __init__(self, config: Optional[ModelConfig] = None):
        """Initialize video quality analyzer"""        super().__init__(config or ModelConfig(
            name="video_quality_analyzer",
            model_type=ModelType.VIDEO_MODEL,
            provider=ModelProvider.LOCAL
        ))
        
        # self.performance_monitor = performance_monitor
        # self.metrics_collector = metrics_collector
        
        # Video analysis parameters
        self.sample_frame_count = 30  # Number of frames to analyze
        self.motion_threshold = 30.0
        self.noise_detection_kernel_size = 5
        
        # Quality thresholds for different platforms
        self.platform_requirements = {
            'youtube': {
                'min_resolution': (1280, 720),
                'recommended_bitrate': {'720p': 5, '1080p': 8, '4k': 35},
                'max_file_size_gb': 128,
                'supported_frame_rates': [24, 25, 30, 48, 50, 60]
            },
            'instagram': {
                'min_resolution': (1080, 1080),
                'max_resolution': (1080, 1920),
                'recommended_bitrate': {'1080p': 3.5},
                'max_duration': 60,
                'supported_aspect_ratios': [(1, 1), (4, 5), (9, 16)]
            },
            'tiktok': {
                'min_resolution': (540, 960),
                'recommended_resolution': (1080, 1920),
                'recommended_bitrate': {'1080p': 3},
                'max_duration': 180,
                'aspect_ratio': (9, 16)
            },
            'broadcast': {
                'min_resolution': (1920, 1080),
                'recommended_bitrate': {'1080p': 50, '4k': 100},
                'required_frame_rates': [25, 29.97, 30, 50, 59.94, 60],
                'min_quality_score': 85
            }
        }
        
        logger.info("Video Quality Analyzer initialized successfully")
    
    @monitor_performance
    async def analyze_quality(
        self,
        video_path: Union[str, Path],
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Comprehensive video quality analysis
        
        Args:
            video_path: Path to video file
            analysis_options: Analysis configuration options
            
        Returns:
            Dict containing complete video quality analysis
            
        Raises:
            QualityCheckError: If analysis fails
            ContentValidationError: If video file is invalid
        """        start_time = datetime.now()
        
        try:
            video_path = Path(video_path)
            if not video_path.exists():
                raise ContentValidationError(f"Video file not found: {video_path}")
            
            # Load video and extract basic properties
            cap = cv2.VideoCapture(str(video_path))
            if not cap.isOpened():
                raise ContentValidationError(f"Cannot open video file: {video_path}")
            
            # Create quality profile
            profile = VideoQualityProfile()
            await self._extract_basic_properties(cap, video_path, profile)
            
            # Perform comprehensive analysis
            await self._analyze_visual_quality(cap, profile)
            await self._analyze_technical_quality(cap, profile)
            await self._analyze_motion_characteristics(cap, profile)
            await self._analyze_encoding_quality(cap, profile)
            
            # Calculate quality scores
            self._calculate_quality_scores(profile)
            
            # Generate recommendations
            self._generate_video_recommendations(profile)
            
            # Create metrics
            metrics = VideoQualityMetrics(profile=profile)
            await self._analyze_platform_compliance(profile, metrics)
            await self._analyze_content_characteristics(cap, metrics)
            
            cap.release()
            
            end_time = datetime.now()
            metrics.processing_time = (end_time - start_time).total_seconds()
            metrics.confidence = self._calculate_confidence(profile)
            
            # Prepare result
            result = {
                'technical_score': profile.technical_score,
                'confidence': metrics.confidence,
                'technical_details': {
                    'resolution': f"{profile.width}x{profile.height}",
                    'frame_rate': profile.frame_rate,
                    'duration': profile.duration,
                    'total_frames': profile.total_frames,
                    'file_size': profile.file_size,
                    'codec': profile.codec,
                    'bitrate': profile.bitrate,
                    'bitrate_category': profile.bitrate_category.value,
                    'sharpness_score': profile.sharpness_score,
                    'contrast_score': profile.contrast_score,
                    'brightness_score': profile.brightness_score,
                    'color_accuracy': profile.color_accuracy,
                    'noise_level': profile.noise_level,
                    'compression_artifacts': profile.compression_artifacts.value,
                    'motion_intensity': profile.motion_intensity,
                    'camera_stability': profile.camera_stability,
                    'overall_quality_score': profile.overall_quality_score,
                    'quality_level': profile.quality_level
                },
                'technical_recommendations': profile.recommendations,
                'platform_compliance': {
                    'youtube_ready': metrics.youtube_ready,
                    'instagram_ready': metrics.instagram_ready,
                    'tiktok_ready': metrics.tiktok_ready,
                    'facebook_ready': metrics.facebook_ready,
                    'broadcast_ready': metrics.broadcast_ready,
                    'cinema_ready': metrics.cinema_ready
                },
                'content_analysis': {
                    'content_type': metrics.content_type,
                    'scene_types': metrics.scene_types,
                    'motion_type': metrics.motion_type,
                    'perceptual_quality': metrics.perceptual_quality,
                    'temporal_consistency': metrics.temporal_consistency,
                    'spatial_quality': metrics.spatial_quality
                },
                'visual_metrics': {
                    'visual_score': profile.visual_score,
                    'motion_score': profile.motion_score,
                    'encoding_score': profile.encoding_score
                }
            }
            
            # Log metrics
            self.metrics_collector.track_business_metric(
                metric_name="video_quality_analysis_completed",
                value=1,
                metadata={
                    'quality_score': profile.overall_quality_score,
                    'resolution': f"{profile.width}x{profile.height}",
                    'duration': profile.duration,
                    'processing_time': metrics.processing_time
                }
            )
            
            logger.info(f"Video quality analysis completed: {profile.overall_quality_score:.2f}/100")
            return result
            
        except Exception as e:
            logger.error(f"Video quality analysis failed: {str(e)}")
            self.metrics_collector.capture_errors("video_quality_analysis_error", str(e))
            raise QualityCheckError(f"Video quality analysis failed: {str(e)}") from e
    
    async def connect(self) -> bool:
        """Connect to video processing services."""        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from video processing services."""        return True
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process video quality assessment."""        return await self.analyze_video_quality(data.get('video_data', b''), 
                                               data.get('profile', VideoQualityProfile()))
    
    async def _extract_basic_properties(
        self,
        cap: cv2.VideoCapture,
        video_path: Path,
        profile: VideoQualityProfile
    ):
        """Extract basic video properties"""        try:
            # Get video properties
            profile.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            profile.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            profile.frame_rate = cap.get(cv2.CAP_PROP_FPS)
            profile.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if profile.frame_rate > 0:
                profile.duration = profile.total_frames / profile.frame_rate
            
            profile.file_size = video_path.stat().st_size
            
            # Estimate bitrate
            if profile.duration > 0:
                profile.bitrate = (profile.file_size * 8) / (profile.duration * 1000000)  # Mbps
            
            # Classify bitrate
            if profile.bitrate < 1:
                profile.bitrate_category = Bitrate.LOW
            elif profile.bitrate < 5:
                profile.bitrate_category = Bitrate.MEDIUM
            elif profile.bitrate < 15:
                profile.bitrate_category = Bitrate.HIGH
            elif profile.bitrate < 50:
                profile.bitrate_category = Bitrate.VERY_HIGH
            else:
                profile.bitrate_category = Bitrate.EXTREME
            
            # Try to get codec info (simplified)
            fourcc = cap.get(cv2.CAP_PROP_FOURCC)
            if fourcc:
                profile.codec = "".join([chr((int(fourcc) >> 8 * i) & 0xFF) for i in range(4)])
            else:
                profile.codec = "unknown"
            
        except Exception as e:
            logger.warning(f"Basic properties extraction failed: {str(e)}")
    
    async def _analyze_visual_quality(
        self,
        cap: cv2.VideoCapture,
        profile: VideoQualityProfile
    ):
        """Analyze visual quality metrics"""        try:
            # Sample frames for analysis
            frame_indices = np.linspace(
                0, 
                profile.total_frames - 1, 
                min(self.sample_frame_count, profile.total_frames),
                dtype=int
            )
            
            sharpness_scores = []
            contrast_scores = []
            brightness_scores = []
            color_scores = []
            noise_levels = []
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                # Convert to different color spaces for analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
                # Sharpness analysis using Laplacian variance
                laplacian = cv2.Laplacian(gray, cv2.CV_64F)
                sharpness = laplacian.var()
                sharpness_scores.append(sharpness)
                
                # Contrast analysis using standard deviation
                contrast = gray.std()
                contrast_scores.append(contrast)
                
                # Brightness analysis using mean intensity
                brightness = gray.mean()
                brightness_scores.append(brightness)
                
                # Color analysis using HSV
                h, s, v = cv2.split(hsv)
                color_variance = s.std() + h.std()
                color_scores.append(color_variance)
                
                # Noise analysis using high-frequency content
                noise = self._estimate_noise_level(gray)
                noise_levels.append(noise)
            
            # Calculate average scores
            if sharpness_scores:
                profile.sharpness_score = np.mean(sharpness_scores)
                profile.contrast_score = np.mean(contrast_scores)
                profile.brightness_score = np.mean(brightness_scores)
                profile.color_accuracy = np.mean(color_scores)
                profile.noise_level = np.mean(noise_levels)
            
            # Normalize scores to 0-100 range
            profile.sharpness_score = min(100, max(0, (profile.sharpness_score / 1000) * 100))
            profile.contrast_score = min(100, max(0, (profile.contrast_score / 128) * 100))
            profile.brightness_score = 100 - abs(profile.brightness_score - 128) / 128 * 100
            profile.color_accuracy = min(100, max(0, (profile.color_accuracy / 100) * 100))
            profile.saturation_score = profile.color_accuracy  # Simplified
            
        except Exception as e:
            logger.warning(f"Visual quality analysis failed: {str(e)}")
    
    def _estimate_noise_level(self, gray_frame: np.ndarray) -> float:
        """Estimate noise level in a frame"""        try:
            # Use high-pass filter to detect noise
            kernel = np.array([[-1, -1, -1],
                              [-1,  8, -1],
                              [-1, -1, -1]], dtype=np.float32)
            
            filtered = cv2.filter2D(gray_frame, cv2.CV_32F, kernel)
            noise_estimate = np.std(filtered)
            
            return min(100, noise_estimate)
            
        except Exception:
            return 50.0  # Default moderate noise level
    
    async def _analyze_technical_quality(
        self,
        cap: cv2.VideoCapture,
        profile: VideoQualityProfile
    ):
        """Analyze technical quality aspects"""        try:
            # Compression artifacts detection
            artifacts_score = self._detect_compression_artifacts(cap, profile)
            
            # Classify compression artifacts
            if artifacts_score < 10:
                profile.compression_artifacts = CompressionArtifacts.NONE
            elif artifacts_score < 25:
                profile.compression_artifacts = CompressionArtifacts.MINIMAL
            elif artifacts_score < 50:
                profile.compression_artifacts = CompressionArtifacts.MODERATE
            elif artifacts_score < 75:
                profile.compression_artifacts = CompressionArtifacts.SEVERE
            else:
                profile.compression_artifacts = CompressionArtifacts.EXTREME
            
            profile.blocking_artifacts = artifacts_score
            
        except Exception as e:
            logger.warning(f"Technical quality analysis failed: {str(e)}")
    
    def _detect_compression_artifacts(
        self,
        cap: cv2.VideoCapture,
        profile: VideoQualityProfile
    ) -> float:
        """Detect compression artifacts in video"""        try:
            # Sample a few frames for artifact detection
            sample_frames = min(5, profile.total_frames)
            frame_indices = np.linspace(0, profile.total_frames - 1, sample_frames, dtype=int)
            
            artifact_scores = []
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect blocking artifacts using gradients
                grad_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
                grad_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
                
                # Look for regular patterns that indicate blocking
                gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
                
                # Simple artifact score based on gradient irregularities
                artifact_score = np.std(gradient_magnitude) / np.mean(gradient_magnitude + 1e-10)
                artifact_scores.append(artifact_score * 20)  # Scale to 0-100
            
            return np.mean(artifact_scores) if artifact_scores else 50.0
            
        except Exception:
            return 50.0  # Default moderate artifacts
    
    async def _analyze_motion_characteristics(
        self,
        cap: cv2.VideoCapture,
        profile: VideoQualityProfile
    ):
        """Analyze motion characteristics and camera stability"""        try:
            # Sample frames for motion analysis
            sample_count = min(10, profile.total_frames - 1)
            frame_indices = np.linspace(0, profile.total_frames - 2, sample_count, dtype=int)
            
            motion_scores = []
            stability_scores = []
            
            prev_frame = None
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # Calculate optical flow for motion analysis
                    flow = cv2.calcOpticalFlowPyrLK(
                        prev_frame, gray, 
                        np.array([[100, 100]], dtype=np.float32).reshape(-1, 1, 2),
                        None
                    )[0]
                    
                    if flow is not None and len(flow) > 0:
                        motion_magnitude = np.linalg.norm(flow[0][0])
                        motion_scores.append(motion_magnitude)
                    
                    # Camera stability using frame difference
                    frame_diff = cv2.absdiff(prev_frame, gray)
                    stability = 100 - (np.mean(frame_diff) / 255 * 100)
                    stability_scores.append(stability)
                
                prev_frame = gray.copy()
            
            # Calculate motion characteristics
            if motion_scores:
                profile.motion_intensity = np.mean(motion_scores)
                profile.camera_stability = np.mean(stability_scores)
            
            # Estimate motion blur (simplified)
            profile.motion_blur = max(0, (profile.motion_intensity - 10) * 2)
            
            # Scene complexity based on edge density
            cap.set(cv2.CAP_PROP_POS_FRAMES, profile.total_frames // 2)
            ret, sample_frame = cap.read()
            if ret:
                gray = cv2.cvtColor(sample_frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                profile.scene_complexity = (np.sum(edges > 0) / edges.size) * 100
            
        except Exception as e:
            logger.warning(f"Motion analysis failed: {str(e)}")
    
    async def _analyze_encoding_quality(
        self,
        cap: cv2.VideoCapture,
        profile: VideoQualityProfile
    ):
        """Analyze encoding quality and efficiency"""        try:
            # Resolution efficiency
            pixel_count = profile.width * profile.height
            
            # Bitrate efficiency analysis
            if pixel_count > 0 and profile.duration > 0:
                bits_per_pixel = (profile.bitrate * 1000000) / (pixel_count * profile.frame_rate)
                
                # Optimal bits per pixel varies by content type
                # For general content: 0.1-0.3 is typical
                if bits_per_pixel < 0.05:
                    encoding_efficiency = 40  # Under-encoded
                elif bits_per_pixel < 0.1:
                    encoding_efficiency = 70  # Low quality
                elif bits_per_pixel < 0.3:
                    encoding_efficiency = 90  # Good quality
                elif bits_per_pixel < 0.5:
                    encoding_efficiency = 85  # High quality
                else:
                    encoding_efficiency = 60  # Over-encoded
                
                profile.encoding_score = encoding_efficiency
            
        except Exception as e:
            logger.warning(f"Encoding analysis failed: {str(e)}")
            profile.encoding_score = 70.0
    
    def _calculate_quality_scores(self, profile: VideoQualityProfile):
        """Calculate comprehensive quality scores"""        try:
            # Technical score (resolution, frame rate, bitrate)
            tech_score = 0.0
            
            # Resolution score
            if profile.width >= 3840:  # 4K
                tech_score += 30
            elif profile.width >= 1920:  # 1080p
                tech_score += 25
            elif profile.width >= 1280:  # 720p
                tech_score += 20
            elif profile.width >= 854:   # 480p
                tech_score += 15
            else:
                tech_score += 10
            
            # Frame rate score
            if profile.frame_rate >= 60:
                tech_score += 25
            elif profile.frame_rate >= 30:
                tech_score += 20
            elif profile.frame_rate >= 24:
                tech_score += 15
            else:
                tech_score += 10
            
            # Bitrate adequacy score
            expected_bitrate = self._get_expected_bitrate(profile.width, profile.height)
            bitrate_ratio = profile.bitrate / expected_bitrate if expected_bitrate > 0 else 0.5
            
            if 0.8 <= bitrate_ratio <= 1.5:
                tech_score += 25  # Optimal bitrate
            elif 0.5 <= bitrate_ratio < 0.8 or 1.5 < bitrate_ratio <= 2.0:
                tech_score += 20  # Acceptable bitrate
            elif 0.3 <= bitrate_ratio < 0.5 or 2.0 < bitrate_ratio <= 3.0:
                tech_score += 15  # Suboptimal bitrate
            else:
                tech_score += 10  # Poor bitrate
            
            # Codec and compression score
            if profile.compression_artifacts == CompressionArtifacts.NONE:
                tech_score += 20
            elif profile.compression_artifacts == CompressionArtifacts.MINIMAL:
                tech_score += 18
            elif profile.compression_artifacts == CompressionArtifacts.MODERATE:
                tech_score += 15
            elif profile.compression_artifacts == CompressionArtifacts.SEVERE:
                tech_score += 10
            else:
                tech_score += 5
            
            profile.technical_score = min(tech_score, 100.0)
            
            # Visual score
            visual_score = (
                profile.sharpness_score * 0.3 +
                profile.contrast_score * 0.25 +
                profile.brightness_score * 0.2 +
                profile.color_accuracy * 0.15 +
                (100 - profile.noise_level) * 0.1
            )
            profile.visual_score = visual_score
            
            # Motion score
            motion_score = (
                profile.camera_stability * 0.4 +
                max(0, 100 - profile.motion_blur) * 0.3 +
                min(100, profile.scene_complexity) * 0.3
            )
            profile.motion_score = motion_score
            
            # Overall quality score
            profile.overall_quality_score = (
                profile.technical_score * 0.4 +
                profile.visual_score * 0.3 +
                profile.motion_score * 0.2 +
                profile.encoding_score * 0.1
            )
            
            # Quality level classification
            if profile.overall_quality_score >= 90:
                profile.quality_level = "professional"
            elif profile.overall_quality_score >= 80:
                profile.quality_level = "broadcast"
            elif profile.overall_quality_score >= 70:
                profile.quality_level = "commercial"
            elif profile.overall_quality_score >= 60:
                profile.quality_level = "streaming"
            else:
                profile.quality_level = "basic"
            
        except Exception as e:
            logger.warning(f"Quality score calculation failed: {str(e)}")
            profile.overall_quality_score = 50.0
            profile.quality_level = "basic"
    
    def _get_expected_bitrate(self, width: int, height: int) -> float:
        """Get expected bitrate for given resolution"""        pixel_count = width * height
        
        if pixel_count >= 3840 * 2160:  # 4K
            return 35.0
        elif pixel_count >= 1920 * 1080:  # 1080p
            return 8.0
        elif pixel_count >= 1280 * 720:   # 720p
            return 5.0
        elif pixel_count >= 854 * 480:    # 480p
            return 2.5
        else:
            return 1.0
    
    def _generate_video_recommendations(self, profile: VideoQualityProfile):
        """Generate video-specific recommendations"""        recommendations = []
        
        # Resolution recommendations
        if profile.width < 1280:
            recommendations.append("Increase resolution to at least 720p (1280x720) for better quality")
        elif profile.width < 1920:
            recommendations.append("Consider upgrading to 1080p (1920x1080) for professional content")
        
        # Frame rate recommendations
        if profile.frame_rate < 24:
            recommendations.append("Increase frame rate to at least 24fps for smooth playback")
        elif profile.frame_rate < 30:
            recommendations.append("Consider 30fps or higher for smoother motion")
        
        # Bitrate recommendations
        expected_bitrate = self._get_expected_bitrate(profile.width, profile.height)
        if profile.bitrate < expected_bitrate * 0.5:
            recommendations.append("Increase bitrate for better quality - current bitrate is too low")
        elif profile.bitrate > expected_bitrate * 2:
            recommendations.append("Consider reducing bitrate for more efficient encoding")
        
        # Visual quality recommendations
        if profile.sharpness_score < 60:
            recommendations.append("Improve focus and sharpness - check camera settings and lens quality")
        
        if profile.contrast_score < 60:
            recommendations.append("Improve contrast - consider better lighting or color correction")
        
        if profile.brightness_score < 70:
            recommendations.append("Optimize brightness levels - avoid over/under exposure")
        
        if profile.noise_level > 40:
            recommendations.append("Reduce video noise - use better lighting or noise reduction")
        
        # Motion recommendations
        if profile.camera_stability < 70:
            recommendations.append("Improve camera stability - use tripod or stabilization")
        
        if profile.motion_blur > 30:
            recommendations.append("Reduce motion blur - use higher shutter speed or reduce camera movement")
        
        # Compression recommendations
        if profile.compression_artifacts in [CompressionArtifacts.SEVERE, CompressionArtifacts.EXTREME]:
            recommendations.append("Reduce compression artifacts - use higher quality encoding settings")
        
        profile.recommendations = recommendations
        
        # Enhancement suggestions
        enhancements = []
        if profile.overall_quality_score < 80:
            enhancements.extend([
                "Consider professional color grading for better visual appeal",
                "Use proper lighting setup for optimal image quality",
                "Apply sharpening filters in post-production if needed"
            ])
        
        if profile.encoding_score < 80:
            enhancements.extend([
                "Optimize encoding settings for target platform",
                "Use two-pass encoding for better quality",
                "Consider modern codecs like H.265/HEVC for efficiency"
            ])
        
        profile.enhancement_suggestions = enhancements
    
    async def _analyze_platform_compliance(
        self,
        profile: VideoQualityProfile,
        metrics: VideoQualityMetrics
    ):
        """Analyze compliance with various platform requirements"""        try:
            # YouTube compliance
            youtube_req = self.platform_requirements['youtube']
            metrics.youtube_ready = (
                profile.width >= youtube_req['min_resolution'][0] and
                profile.height >= youtube_req['min_resolution'][1] and
                profile.frame_rate in youtube_req['supported_frame_rates'] and
                profile.file_size <= youtube_req['max_file_size_gb'] * 1024**3 and
                profile.overall_quality_score >= 60
            )
            
            # Instagram compliance
            instagram_req = self.platform_requirements['instagram']
            aspect_ratio = profile.width / profile.height if profile.height > 0 else 1
            metrics.instagram_ready = (
                profile.width >= instagram_req['min_resolution'][0] and
                profile.height >= instagram_req['min_resolution'][1] and
                profile.width <= instagram_req['max_resolution'][0] and
                profile.height <= instagram_req['max_resolution'][1] and
                profile.duration <= instagram_req['max_duration'] and
                profile.overall_quality_score >= 65
            )
            
            # TikTok compliance
            tiktok_req = self.platform_requirements['tiktok']
            metrics.tiktok_ready = (
                profile.width >= tiktok_req['min_resolution'][0] and
                profile.height >= tiktok_req['min_resolution'][1] and
                abs(aspect_ratio - (9/16)) < 0.1 and  # Vertical aspect ratio
                profile.duration <= tiktok_req['max_duration'] and
                profile.overall_quality_score >= 60
            )
            
            # Facebook compliance (similar to YouTube with some variations)
            metrics.facebook_ready = (
                profile.width >= 1280 and
                profile.height >= 720 and
                profile.overall_quality_score >= 65
            )
            
            # Broadcast compliance
            broadcast_req = self.platform_requirements['broadcast']
            metrics.broadcast_ready = (
                profile.width >= broadcast_req['min_resolution'][0] and
                profile.height >= broadcast_req['min_resolution'][1] and
                profile.frame_rate in broadcast_req['required_frame_rates'] and
                profile.overall_quality_score >= broadcast_req['min_quality_score'] and
                profile.compression_artifacts in [CompressionArtifacts.NONE, CompressionArtifacts.MINIMAL]
            )
            
            # Cinema compliance
            metrics.cinema_ready = (
                profile.width >= 1920 and
                profile.height >= 1080 and
                profile.frame_rate in [24, 25, 30] and
                profile.overall_quality_score >= 85 and
                profile.compression_artifacts == CompressionArtifacts.NONE and
                profile.bitrate >= 25
            )
            
        except Exception as e:
            logger.warning(f"Platform compliance analysis failed: {str(e)}")
    
    async def _analyze_content_characteristics(
        self,
        cap: cv2.VideoCapture,
        metrics: VideoQualityMetrics
    ):
        """Analyze content characteristics and type"""        try:
            # Sample a few frames for content analysis
            sample_frames = 3
            frame_indices = np.linspace(0, metrics.profile.total_frames - 1, sample_frames, dtype=int)
            
            scene_brightness = []
            scene_complexity = []
            color_variety = []
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
                # Analyze brightness
                brightness = gray.mean()
                scene_brightness.append(brightness)
                
                # Analyze scene complexity
                edges = cv2.Canny(gray, 50, 150)
                complexity = np.sum(edges > 0) / edges.size
                scene_complexity.append(complexity)
                
                # Analyze color variety
                h, s, v = cv2.split(hsv)
                color_var = s.std() + h.std()
                color_variety.append(color_var)
            
            # Classify content characteristics
            avg_brightness = np.mean(scene_brightness) if scene_brightness else 128
            avg_complexity = np.mean(scene_complexity) if scene_complexity else 0.1
            avg_color_variety = np.mean(color_variety) if color_variety else 50
            
            # Scene type classification
            scene_types = []
            if avg_brightness < 80:
                scene_types.append("low_light")
            elif avg_brightness > 200:
                scene_types.append("bright")
            else:
                scene_types.append("normal_light")
            
            if avg_complexity > 0.2:
                scene_types.append("complex")
            else:
                scene_types.append("simple")
            
            if avg_color_variety > 60:
                scene_types.append("colorful")
            else:
                scene_types.append("monochrome")
            
            metrics.scene_types = scene_types
            
            # Motion type classification
            if metrics.profile.motion_intensity < 5:
                metrics.motion_type = "static"
            elif metrics.profile.motion_intensity < 15:
                metrics.motion_type = "slow"
            elif metrics.profile.motion_intensity < 30:
                metrics.motion_type = "moderate"
            elif metrics.profile.motion_intensity < 50:
                metrics.motion_type = "fast"
            else:
                metrics.motion_type = "extreme"
            
            # Content type estimation (simplified)
            if "low_light" in scene_types and "simple" in scene_types:
                metrics.content_type = "interview"
            elif "complex" in scene_types and metrics.motion_type in ["moderate", "fast"]:
                metrics.content_type = "action"
            elif "colorful" in scene_types and "complex" in scene_types:
                metrics.content_type = "entertainment"
            else:
                metrics.content_type = "general"
            
            # Advanced quality metrics
            metrics.perceptual_quality = (
                metrics.profile.visual_score * 0.6 +
                metrics.profile.motion_score * 0.4
            )
            
            metrics.temporal_consistency = metrics.profile.camera_stability
            metrics.spatial_quality = metrics.profile.sharpness_score
            
        except Exception as e:
            logger.warning(f"Content characteristics analysis failed: {str(e)}")
            metrics.content_type = "unknown"
            metrics.motion_type = "unknown"
            metrics.scene_types = ["unknown"]
    
    def _calculate_confidence(self, profile: VideoQualityProfile) -> float:
        """Calculate analysis confidence score"""        confidence = 0.8  # Base confidence
        
        # Adjust based on video duration
        if profile.duration > 10:
            confidence += 0.1  # More data for analysis
        elif profile.duration < 2:
            confidence -= 0.2  # Less data for analysis
        
        # Adjust based on resolution
        if profile.width >= 1920 and profile.height >= 1080:
            confidence += 0.05
        elif profile.width < 640:
            confidence -= 0.1
        
        # Adjust based on quality indicators
        if profile.compression_artifacts == CompressionArtifacts.NONE:
            confidence += 0.05
        elif profile.compression_artifacts in [CompressionArtifacts.SEVERE, CompressionArtifacts.EXTREME]:
            confidence -= 0.1
        
        return max(0.3, min(1.0, confidence))


# Global video quality analyzer instance
# video_quality_analyzer = VideoQualityAnalyzer()  # Commented out for testing


async def analyze_video_quality(video_path: Union[str, Path]) -> Dict[str, Any]:
    """    Convenient function for video quality analysis
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dict containing video quality analysis results
    """    try:
        result = await video_quality_analyzer.analyze_quality(video_path)
        return result
    except Exception as e:
        logger.error(f"Video quality analysis error: {str(e)}")
        return {
            'error': str(e),
            'success': False
        }
