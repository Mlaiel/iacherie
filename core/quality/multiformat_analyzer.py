"""
Multi-Format Content Quality Analyzer - Enterprise Content Intelligence System

Ultra-advanced multi-format content quality analysis system with AI-powered
assessment, protection readiness scoring, and optimization recommendations
for creators on the IA-Influencer platform.

Business Logic:
Content upload → Format detection → Quality analysis → Protection scoring →
SEO optimization → Platform compatibility → Quality report generation

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 STRICT COPYRIGHT WARNING 
This software is proprietary and confidential. 
Unauthorized use, modification, or distribution by any individual or entity 
without explicit written permission from Fahed Mlaiel is strictly prohibited.
Violators will face immediate legal action under German and international law.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import time
import hashlib
import mimetypes
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import json
import base64

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageStat, ImageFilter
    import librosa
    import soundfile as sf
    from moviepy.editor import VideoFileClip
    MULTIMEDIA_AVAILABLE = True
except ImportError:
    MULTIMEDIA_AVAILABLE = False

try:
    import torch
    import transformers
    from transformers import pipeline
    from sentence_transformers import SentenceTransformer
    import tensorflow as tf
    AI_MODELS_AVAILABLE = True
except ImportError:
    AI_MODELS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ContentFormat(Enum):
    """Supported content formats"""
    # Audio formats
    AUDIO_MP3 = "audio_mp3"
    AUDIO_WAV = "audio_wav"
    AUDIO_FLAC = "audio_flac"
    AUDIO_AAC = "audio_aac"
    AUDIO_OGG = "audio_ogg"
    
    # Video formats
    VIDEO_MP4 = "video_mp4"
    VIDEO_AVI = "video_avi"
    VIDEO_MOV = "video_mov"
    VIDEO_MKV = "video_mkv"
    VIDEO_WEBM = "video_webm"
    
    # Image formats
    IMAGE_JPEG = "image_jpeg"
    IMAGE_PNG = "image_png"
    IMAGE_GIF = "image_gif"
    IMAGE_WEBP = "image_webp"
    IMAGE_TIFF = "image_tiff"
    
    # Text formats
    TEXT_PLAIN = "text_plain"
    TEXT_MARKDOWN = "text_markdown"
    TEXT_HTML = "text_html"
    TEXT_JSON = "text_json"


class QualityLevel(Enum):
    """Content quality levels"""
    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"           # 80-89
    FAIR = "fair"           # 60-79
    POOR = "poor"           # 40-59
    UNACCEPTABLE = "unacceptable"  # 0-39


class ProtectionReadiness(Enum):
    """Content protection readiness levels"""
    READY = "ready"              # 90-100 - Ready for protection
    MOSTLY_READY = "mostly_ready"  # 70-89 - Minor improvements needed
    NEEDS_WORK = "needs_work"    # 50-69 - Significant improvements needed
    NOT_READY = "not_ready"      # 0-49 - Major issues must be resolved


@dataclass
class TechnicalSpecs:
    """Technical specifications of content"""
    file_size: int = 0
    duration: Optional[float] = None  # For audio/video
    dimensions: Optional[Tuple[int, int]] = None  # For images/video
    bit_rate: Optional[int] = None
    sample_rate: Optional[int] = None  # For audio
    frame_rate: Optional[float] = None  # For video
    color_depth: Optional[int] = None
    compression_ratio: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'file_size': self.file_size,
            'duration': self.duration,
            'dimensions': self.dimensions,
            'bit_rate': self.bit_rate,
            'sample_rate': self.sample_rate,
            'frame_rate': self.frame_rate,
            'color_depth': self.color_depth,
            'compression_ratio': self.compression_ratio
        }


@dataclass
class QualityMetrics:
    """Comprehensive quality metrics"""
    technical_quality_score: float = 0.0
    content_quality_score: float = 0.0
    aesthetic_quality_score: float = 0.0
    uniqueness_score: float = 0.0
    engagement_potential_score: float = 0.0
    protection_readiness_score: float = 0.0
    seo_optimization_score: float = 0.0
    platform_compatibility_score: float = 0.0
    
    # Detailed breakdowns
    audio_quality: Optional[Dict[str, float]] = None
    video_quality: Optional[Dict[str, float]] = None
    image_quality: Optional[Dict[str, float]] = None
    text_quality: Optional[Dict[str, float]] = None
    
    def calculate_overall_score(self) -> float:
        """Calculate weighted overall quality score"""
        weights = {
            'technical': 0.20,
            'content': 0.25,
            'aesthetic': 0.15,
            'uniqueness': 0.15,
            'engagement': 0.10,
            'protection': 0.10,
            'seo': 0.03,
            'platform': 0.02
        }
        
        score = (
            self.technical_quality_score * weights['technical'] +
            self.content_quality_score * weights['content'] +
            self.aesthetic_quality_score * weights['aesthetic'] +
            self.uniqueness_score * weights['uniqueness'] +
            self.engagement_potential_score * weights['engagement'] +
            self.protection_readiness_score * weights['protection'] +
            self.seo_optimization_score * weights['seo'] +
            self.platform_compatibility_score * weights['platform']
        )
        
        return round(score, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'technical_quality_score': self.technical_quality_score,
            'content_quality_score': self.content_quality_score,
            'aesthetic_quality_score': self.aesthetic_quality_score,
            'uniqueness_score': self.uniqueness_score,
            'engagement_potential_score': self.engagement_potential_score,
            'protection_readiness_score': self.protection_readiness_score,
            'seo_optimization_score': self.seo_optimization_score,
            'platform_compatibility_score': self.platform_compatibility_score,
            'overall_score': self.calculate_overall_score(),
            'audio_quality': self.audio_quality,
            'video_quality': self.video_quality,
            'image_quality': self.image_quality,
            'text_quality': self.text_quality
        }


@dataclass
class ContentIssue:
    """Individual content quality issue"""
    issue_id: str
    category: str
    severity: str  # critical, high, medium, low
    title: str
    description: str
    impact: str
    suggested_fix: str
    auto_fixable: bool = False
    estimated_fix_time: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'issue_id': self.issue_id,
            'category': self.category,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'impact': self.impact,
            'suggested_fix': self.suggested_fix,
            'auto_fixable': self.auto_fixable,
            'estimated_fix_time': self.estimated_fix_time
        }


@dataclass
class OptimizationRecommendation:
    """Content optimization recommendation"""
    recommendation_id: str
    category: str
    priority: str  # high, medium, low
    title: str
    description: str
    expected_improvement: str
    implementation_steps: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    estimated_time: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'recommendation_id': self.recommendation_id,
            'category': self.category,
            'priority': self.priority,
            'title': self.title,
            'description': self.description,
            'expected_improvement': self.expected_improvement,
            'implementation_steps': self.implementation_steps,
            'tools_required': self.tools_required,
            'estimated_time': self.estimated_time
        }


@dataclass
class MultiFormatQualityAnalysis:
    """Comprehensive multi-format content quality analysis result"""
    content_id: str
    content_format: ContentFormat
    analysis_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Technical specifications
    technical_specs: TechnicalSpecs = field(default_factory=TechnicalSpecs)
    
    # Quality metrics
    quality_metrics: QualityMetrics = field(default_factory=QualityMetrics)
    
    # Quality classification
    overall_quality_level: Optional[QualityLevel] = None
    protection_readiness: Optional[ProtectionReadiness] = None
    
    # Issues and recommendations
    issues: List[ContentIssue] = field(default_factory=list)
    optimization_recommendations: List[OptimizationRecommendation] = field(default_factory=list)
    
    # Platform-specific insights
    platform_compatibility: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # AI analysis results
    ai_insights: Dict[str, Any] = field(default_factory=dict)
    
    def determine_quality_level(self):
        """Determine overall quality level based on score"""
        overall_score = self.quality_metrics.calculate_overall_score()
        
        if overall_score >= 90:
            self.overall_quality_level = QualityLevel.EXCELLENT
        elif overall_score >= 80:
            self.overall_quality_level = QualityLevel.GOOD
        elif overall_score >= 60:
            self.overall_quality_level = QualityLevel.FAIR
        elif overall_score >= 40:
            self.overall_quality_level = QualityLevel.POOR
        else:
            self.overall_quality_level = QualityLevel.UNACCEPTABLE
    
    def determine_protection_readiness(self):
        """Determine protection readiness based on score"""
        protection_score = self.quality_metrics.protection_readiness_score
        
        if protection_score >= 90:
            self.protection_readiness = ProtectionReadiness.READY
        elif protection_score >= 70:
            self.protection_readiness = ProtectionReadiness.MOSTLY_READY
        elif protection_score >= 50:
            self.protection_readiness = ProtectionReadiness.NEEDS_WORK
        else:
            self.protection_readiness = ProtectionReadiness.NOT_READY
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content_id': self.content_id,
            'content_format': self.content_format.value,
            'analysis_timestamp': self.analysis_timestamp.isoformat(),
            'technical_specs': self.technical_specs.to_dict(),
            'quality_metrics': self.quality_metrics.to_dict(),
            'overall_quality_level': self.overall_quality_level.value if self.overall_quality_level else None,
            'protection_readiness': self.protection_readiness.value if self.protection_readiness else None,
            'issues': [issue.to_dict() for issue in self.issues],
            'optimization_recommendations': [rec.to_dict() for rec in self.optimization_recommendations],
            'platform_compatibility': self.platform_compatibility,
            'ai_insights': self.ai_insights
        }


class MultiFormatContentQualityAnalyzer:
    """
    Ultra-advanced multi-format content quality analyzer with AI-powered assessment
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = {
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
            'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.tiff'],
            'text': ['.txt', '.md', '.html', '.json']
        }
        
        # Quality thresholds for different content types
        self.quality_thresholds = {
            'audio': {
                'sample_rate_min': 44100,
                'bit_rate_min': 128000,
                'dynamic_range_min': 20,
                'signal_to_noise_min': 60
            },
            'video': {
                'resolution_min': (720, 480),
                'frame_rate_min': 24,
                'bit_rate_min': 1000000,
                'audio_quality_min': 70
            },
            'image': {
                'resolution_min': (800, 600),
                'quality_score_min': 70,
                'noise_level_max': 20,
                'sharpness_min': 0.5
            },
            'text': {
                'readability_min': 60,
                'uniqueness_min': 80,
                'keyword_density_max': 3.0,
                'sentiment_min': 0.2
            }
        }
        
        # Initialize AI models if available
        self.ai_models = {}
        if AI_MODELS_AVAILABLE:
            self._initialize_ai_models()
    
    def _initialize_ai_models(self):
        """Initialize AI models for content analysis"""



        try:
            # Text analysis models
            self.ai_models['sentiment'] = pipeline("sentiment-analysis")
            self.ai_models['text_similarity'] = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Image analysis models would be initialized here
            # self.ai_models['image_classifier'] = ...
            
            self.logger.info("AI models initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize some AI models: {str(e)}")
    
    async def analyze_content_quality(
        self,
        content_path: Union[str, Path],
        content_metadata: Optional[Dict[str, Any]] = None,
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> MultiFormatQualityAnalysis:
        """
        Perform comprehensive multi-format content quality analysis
        
        Args:
            content_path: Path to the content file
            content_metadata: Additional metadata about the content
            analysis_options: Analysis configuration options
            
        Returns:
            MultiFormatQualityAnalysis: Comprehensive analysis result
        """
        start_time = time.time()
        content_path = Path(content_path)
        content_id = content_metadata.get('content_id', str(content_path.stem)) if content_metadata else str(content_path.stem)
        
        try:
            self.logger.info(f"Starting multi-format quality analysis for content {content_id}")
            
            # Detect content format
            content_format = await self._detect_content_format(content_path)
            
            # Initialize analysis result
            analysis = MultiFormatQualityAnalysis(
                content_id=content_id,
                content_format=content_format
            )
            
            # Extract technical specifications
            analysis.technical_specs = await self._extract_technical_specs(content_path, content_format)
            
            # Perform format-specific quality analysis
            if content_format.value.startswith('audio'):
                analysis.quality_metrics = await self._analyze_audio_quality(
                    content_path, analysis.technical_specs, content_metadata
                )
            elif content_format.value.startswith('video'):
                analysis.quality_metrics = await self._analyze_video_quality(
                    content_path, analysis.technical_specs, content_metadata
                )
            elif content_format.value.startswith('image'):
                analysis.quality_metrics = await self._analyze_image_quality(
                    content_path, analysis.technical_specs, content_metadata
                )
            elif content_format.value.startswith('text'):
                analysis.quality_metrics = await self._analyze_text_quality(
                    content_path, analysis.technical_specs, content_metadata
                )
            
            # Perform AI-powered analysis if available
            if AI_MODELS_AVAILABLE:
                analysis.ai_insights = await self._perform_ai_analysis(content_path, content_format)
            
            # Analyze platform compatibility
            analysis.platform_compatibility = await self._analyze_platform_compatibility(
                content_path, content_format, analysis.technical_specs
            )
            
            # Identify issues and generate recommendations
            await self._identify_issues(analysis)
            await self._generate_optimization_recommendations(analysis)
            
            # Determine quality levels
            analysis.determine_quality_level()
            analysis.determine_protection_readiness()
            
            processing_time = (time.time() - start_time) * 1000
            self.logger.info(
                f"Multi-format quality analysis completed for content {content_id} "
                f"in {processing_time:.2f}ms with overall score {analysis.quality_metrics.calculate_overall_score():.1f}"
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing content quality for {content_id}: {str(e)}")
            raise
    
    async def _detect_content_format(self, content_path: Path) -> ContentFormat:
        """Detect content format based on file extension and MIME type"""
        file_extension = content_path.suffix.lower()
        mime_type, _ = mimetypes.guess_type(str(content_path))
        
        # Audio formats
        if file_extension in ['.mp3']:
            return ContentFormat.AUDIO_MP3
        elif file_extension in ['.wav']:
            return ContentFormat.AUDIO_WAV
        elif file_extension in ['.flac']:
            return ContentFormat.AUDIO_FLAC
        elif file_extension in ['.aac']:
            return ContentFormat.AUDIO_AAC
        elif file_extension in ['.ogg']:
            return ContentFormat.AUDIO_OGG
        
        # Video formats
        elif file_extension in ['.mp4']:
            return ContentFormat.VIDEO_MP4
        elif file_extension in ['.avi']:
            return ContentFormat.VIDEO_AVI
        elif file_extension in ['.mov']:
            return ContentFormat.VIDEO_MOV
        elif file_extension in ['.mkv']:
            return ContentFormat.VIDEO_MKV
        elif file_extension in ['.webm']:
            return ContentFormat.VIDEO_WEBM
        
        # Image formats
        elif file_extension in ['.jpg', '.jpeg']:
            return ContentFormat.IMAGE_JPEG
        elif file_extension in ['.png']:
            return ContentFormat.IMAGE_PNG
        elif file_extension in ['.gif']:
            return ContentFormat.IMAGE_GIF
        elif file_extension in ['.webp']:
            return ContentFormat.IMAGE_WEBP
        elif file_extension in ['.tiff', '.tif']:
            return ContentFormat.IMAGE_TIFF
        
        # Text formats
        elif file_extension in ['.txt']:
            return ContentFormat.TEXT_PLAIN
        elif file_extension in ['.md']:
            return ContentFormat.TEXT_MARKDOWN
        elif file_extension in ['.html', '.htm']:
            return ContentFormat.TEXT_HTML
        elif file_extension in ['.json']:
            return ContentFormat.TEXT_JSON
        
        # Default to plain text if unknown
        return ContentFormat.TEXT_PLAIN
    
    async def _extract_technical_specs(
        self,
        content_path: Path,
        content_format: ContentFormat
    ) -> TechnicalSpecs:
        """Extract technical specifications from content"""
        specs = TechnicalSpecs()
        
        try:
            # Basic file info
            specs.file_size = content_path.stat().st_size
            
            if content_format.value.startswith('audio') and MULTIMEDIA_AVAILABLE:
                # Audio specifications
                try:
                    y, sr = librosa.load(str(content_path), sr=None)
                    specs.duration = len(y) / sr
                    specs.sample_rate = sr
                    
                    # Estimate bit rate
                    specs.bit_rate = int((specs.file_size * 8) / specs.duration) if specs.duration > 0 else 0
                except Exception as e:
                    self.logger.warning(f"Failed to extract audio specs: {str(e)}")
            
            elif content_format.value.startswith('video') and MULTIMEDIA_AVAILABLE:
                # Video specifications
                try:
                    with VideoFileClip(str(content_path)) as video:
                        specs.duration = video.duration
                        specs.dimensions = (video.w, video.h)
                        specs.frame_rate = video.fps
                        
                        # Estimate bit rate
                        specs.bit_rate = int((specs.file_size * 8) / specs.duration) if specs.duration > 0 else 0
                except Exception as e:
                    self.logger.warning(f"Failed to extract video specs: {str(e)}")
            
            elif content_format.value.startswith('image') and MULTIMEDIA_AVAILABLE:
                # Image specifications
                try:
                    with Image.open(content_path) as img:
                        specs.dimensions = img.size
                        specs.color_depth = len(img.getbands()) * 8
                        
                        # Calculate compression ratio estimate
                        uncompressed_size = specs.dimensions[0] * specs.dimensions[1] * (specs.color_depth // 8)
                        specs.compression_ratio = specs.file_size / uncompressed_size if uncompressed_size > 0 else 1.0
                except Exception as e:
                    self.logger.warning(f"Failed to extract image specs: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Error extracting technical specs: {str(e)}")
        
        return specs
    
    async def _analyze_audio_quality(
        self,
        content_path: Path,
        technical_specs: TechnicalSpecs,
        metadata: Optional[Dict[str, Any]]
    ) -> QualityMetrics:
        """Analyze audio content quality"""
        metrics = QualityMetrics()
        
        if not MULTIMEDIA_AVAILABLE:
            self.logger.warning("Multimedia libraries not available for audio analysis")
            return metrics
        
        try:
            # Load audio
            y, sr = librosa.load(str(content_path), sr=None)
            
            # Technical quality analysis
            technical_score = 0.0
            
            # Sample rate check
            if technical_specs.sample_rate and technical_specs.sample_rate >= self.quality_thresholds['audio']['sample_rate_min']:
                technical_score += 25
            
            # Bit rate check
            if technical_specs.bit_rate and technical_specs.bit_rate >= self.quality_thresholds['audio']['bit_rate_min']:
                technical_score += 25
            
            # Dynamic range analysis
            dynamic_range = np.max(y) - np.min(y)
            if dynamic_range >= self.quality_thresholds['audio']['dynamic_range_min'] / 100:
                technical_score += 25
            
            # Signal-to-noise ratio estimate
            signal_power = np.mean(y ** 2)
            noise_power = np.var(y - np.mean(y))
            snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 100
            
            if snr >= self.quality_thresholds['audio']['signal_to_noise_min']:
                technical_score += 25
            
            metrics.technical_quality_score = technical_score
            
            # Audio-specific quality metrics
            metrics.audio_quality = {
                'dynamic_range': float(dynamic_range),
                'signal_to_noise_ratio': float(snr),
                'peak_amplitude': float(np.max(np.abs(y))),
                'rms_level': float(np.sqrt(np.mean(y ** 2))),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y))),
                'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            }
            
            # Content quality (placeholder - would use more sophisticated analysis)
            metrics.content_quality_score = min(100, technical_score + 10)
            
            # Aesthetic quality (placeholder)
            metrics.aesthetic_quality_score = 75.0
            
            # Uniqueness score (placeholder - would use fingerprinting)
            metrics.uniqueness_score = 80.0
            
            # Engagement potential
            metrics.engagement_potential_score = min(100, technical_score + 5)
            
            # Protection readiness
            metrics.protection_readiness_score = technical_score
            
        except Exception as e:
            self.logger.error(f"Error analyzing audio quality: {str(e)}")
        
        return metrics
    
    async def _analyze_video_quality(
        self,
        content_path: Path,
        technical_specs: TechnicalSpecs,
        metadata: Optional[Dict[str, Any]]
    ) -> QualityMetrics:
        """Analyze video content quality"""
        metrics = QualityMetrics()
        
        if not MULTIMEDIA_AVAILABLE:
            self.logger.warning("Multimedia libraries not available for video analysis")
            return metrics
        
        try:
            # Technical quality analysis
            technical_score = 0.0
            
            # Resolution check
            if technical_specs.dimensions:
                min_res = self.quality_thresholds['video']['resolution_min']
                if technical_specs.dimensions[0] >= min_res[0] and technical_specs.dimensions[1] >= min_res[1]:
                    technical_score += 25
            
            # Frame rate check
            if technical_specs.frame_rate and technical_specs.frame_rate >= self.quality_thresholds['video']['frame_rate_min']:
                technical_score += 25
            
            # Bit rate check
            if technical_specs.bit_rate and technical_specs.bit_rate >= self.quality_thresholds['video']['bit_rate_min']:
                technical_score += 25
            
            # Video analysis using OpenCV
            cap = cv2.VideoCapture(str(content_path))
            if cap.isOpened():
                # Sample frames for quality analysis
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                sample_frames = min(10, frame_count)
                
                blur_scores = []
                brightness_scores = []
                
                for i in range(0, frame_count, max(1, frame_count // sample_frames)):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                    ret, frame = cap.read()
                    
                    if ret:
                        # Blur detection
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
                        blur_scores.append(blur_score)
                        
                        # Brightness analysis
                        brightness = np.mean(gray)
                        brightness_scores.append(brightness)
                
                cap.release()
                
                # Video quality assessment
                if blur_scores:
                    avg_blur = np.mean(blur_scores)
                    if avg_blur > 100:  # Threshold for acceptable sharpness
                        technical_score += 25
                
                metrics.video_quality = {
                    'average_blur_score': float(np.mean(blur_scores)) if blur_scores else 0.0,
                    'average_brightness': float(np.mean(brightness_scores)) if brightness_scores else 0.0,
                    'frame_consistency': 85.0,  # Placeholder
                    'color_accuracy': 80.0,     # Placeholder
                }
            
            metrics.technical_quality_score = technical_score
            
            # Content quality (placeholder)
            metrics.content_quality_score = min(100, technical_score + 5)
            
            # Aesthetic quality (placeholder)
            metrics.aesthetic_quality_score = 75.0
            
            # Uniqueness score (placeholder)
            metrics.uniqueness_score = 80.0
            
            # Engagement potential
            metrics.engagement_potential_score = min(100, technical_score + 10)
            
            # Protection readiness
            metrics.protection_readiness_score = technical_score
            
        except Exception as e:
            self.logger.error(f"Error analyzing video quality: {str(e)}")
        
        return metrics
    
    async def _analyze_image_quality(
        self,
        content_path: Path,
        technical_specs: TechnicalSpecs,
        metadata: Optional[Dict[str, Any]]
    ) -> QualityMetrics:
        """Analyze image content quality"""
        metrics = QualityMetrics()
        
        if not MULTIMEDIA_AVAILABLE:
            self.logger.warning("Multimedia libraries not available for image analysis")
            return metrics
        
        try:
            with Image.open(content_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Technical quality analysis
                technical_score = 0.0
                
                # Resolution check
                if technical_specs.dimensions:
                    min_res = self.quality_thresholds['image']['resolution_min']
                    if technical_specs.dimensions[0] >= min_res[0] and technical_specs.dimensions[1] >= min_res[1]:
                        technical_score += 25
                
                # Convert to numpy array for analysis
                img_array = np.array(img)
                
                # Sharpness analysis using Laplacian variance
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
                
                if sharpness > 500:  # Threshold for acceptable sharpness
                    technical_score += 25
                
                # Noise analysis
                noise_level = np.std(gray)
                if noise_level < self.quality_thresholds['image']['noise_level_max']:
                    technical_score += 25
                
                # Brightness and contrast analysis
                brightness = np.mean(gray)
                contrast = np.std(gray)
                
                # Good exposure check (not too dark or bright)
                if 50 < brightness < 200 and contrast > 30:
                    technical_score += 25
                
                metrics.technical_quality_score = technical_score
                
                # Image-specific quality metrics
                metrics.image_quality = {
                    'sharpness_score': float(sharpness),
                    'noise_level': float(noise_level),
                    'brightness': float(brightness),
                    'contrast': float(contrast),
                    'color_richness': float(np.mean(np.std(img_array, axis=(0, 1)))),
                    'composition_score': 75.0  # Placeholder for composition analysis
                }
                
                # Content quality (placeholder)
                metrics.content_quality_score = min(100, technical_score + 5)
                
                # Aesthetic quality
                aesthetic_score = 0.0
                
                # Rule of thirds compliance (simplified)
                h, w = gray.shape
                grid_x = [w // 3, 2 * w // 3]
                grid_y = [h // 3, 2 * h // 3]
                
                # Check for interesting points near grid intersections
                for gx in grid_x:
                    for gy in grid_y:
                        region = gray[max(0, gy-20):min(h, gy+20), max(0, gx-20):min(w, gx+20)]
                        if region.size > 0 and np.std(region) > 20:
                            aesthetic_score += 12.5
                
                metrics.aesthetic_quality_score = min(100, aesthetic_score)
                
                # Uniqueness score (placeholder)
                metrics.uniqueness_score = 80.0
                
                # Engagement potential
                metrics.engagement_potential_score = min(100, (technical_score + aesthetic_score) / 2)
                
                # Protection readiness
                metrics.protection_readiness_score = technical_score
                
        except Exception as e:
            self.logger.error(f"Error analyzing image quality: {str(e)}")
        
        return metrics
    
    async def _analyze_text_quality(
        self,
        content_path: Path,
        technical_specs: TechnicalSpecs,
        metadata: Optional[Dict[str, Any]]
    ) -> QualityMetrics:
        """Analyze text content quality"""
        metrics = QualityMetrics()
        
        try:
            # Read text content
            with open(content_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            # Basic text metrics
            word_count = len(text_content.split())
            char_count = len(text_content)
            sentence_count = text_content.count('.') + text_content.count('!') + text_content.count('?')
            
            # Technical quality analysis
            technical_score = 0.0
            
            # Length appropriateness
            if 100 <= word_count <= 2000:
                technical_score += 25
            
            # Readability (simplified Flesch score approximation)
            if sentence_count > 0:
                avg_sentence_length = word_count / sentence_count
                avg_syllables = 1.5  # Simplified estimate
                
                flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
                
                if flesch_score >= self.quality_thresholds['text']['readability_min']:
                    technical_score += 25
            
            # Grammar and spelling (placeholder - would use proper NLP)
            error_ratio = text_content.count('teh') / max(1, word_count)  # Simplified
            if error_ratio < 0.01:
                technical_score += 25
            
            # Structure quality
            paragraph_count = text_content.count('\n\n') + 1
            if paragraph_count >= 3 and word_count / paragraph_count < 150:
                technical_score += 25
            
            metrics.technical_quality_score = technical_score
            
            # Text-specific quality metrics
            metrics.text_quality = {
                'word_count': word_count,
                'character_count': char_count,
                'sentence_count': sentence_count,
                'paragraph_count': paragraph_count,
                'readability_score': flesch_score if sentence_count > 0 else 0,
                'keyword_density': 2.5,  # Placeholder
                'sentiment_score': 0.6   # Placeholder
            }
            
            # Content quality
            content_score = technical_score
            
            # Check for AI analysis if available
            if AI_MODELS_AVAILABLE and 'sentiment' in self.ai_models:
                try:
                    sentiment_result = self.ai_models['sentiment'](text_content[:512])  # Limit length
                    if sentiment_result and isinstance(sentiment_result, list):
                        sentiment_score = sentiment_result[0].get('score', 0.5)
                        if sentiment_score > 0.6:
                            content_score += 10
                        
                        metrics.text_quality['sentiment_score'] = sentiment_score
                except Exception as e:
                    self.logger.warning(f"Sentiment analysis failed: {str(e)}")
            
            metrics.content_quality_score = min(100, content_score)
            
            # Aesthetic quality (for text, this relates to formatting and structure)
            metrics.aesthetic_quality_score = min(100, technical_score - 10)
            
            # Uniqueness score (placeholder - would use proper similarity analysis)
            metrics.uniqueness_score = 85.0
            
            # Engagement potential
            engagement_score = (technical_score + content_score) / 2
            
            # Bonus for good length
            if 300 <= word_count <= 1500:
                engagement_score += 10
            
            metrics.engagement_potential_score = min(100, engagement_score)
            
            # Protection readiness
            metrics.protection_readiness_score = technical_score
            
        except Exception as e:
            self.logger.error(f"Error analyzing text quality: {str(e)}")
        
        return metrics
    
    async def _perform_ai_analysis(
        self,
        content_path: Path,
        content_format: ContentFormat
    ) -> Dict[str, Any]:
        """Perform AI-powered content analysis"""
        ai_insights = {}
        
        if not AI_MODELS_AVAILABLE:
            return ai_insights
        
        try:
            if content_format.value.startswith('text'):
                # Text AI analysis
                with open(content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                
                # Sentiment analysis
                if 'sentiment' in self.ai_models:
                    sentiment_result = self.ai_models['sentiment'](text_content[:512])
                    ai_insights['sentiment_analysis'] = sentiment_result
                
                # Text similarity (for uniqueness detection)
                if 'text_similarity' in self.ai_models:
                    embeddings = self.ai_models['text_similarity'].encode([text_content[:512]])
                    ai_insights['content_embeddings'] = embeddings.tolist()
            
            # Add more AI analysis for other content types as models become available
            
        except Exception as e:
            self.logger.error(f"Error in AI analysis: {str(e)}")
        
        return ai_insights
    
    async def _analyze_platform_compatibility(
        self,
        content_path: Path,
        content_format: ContentFormat,
        technical_specs: TechnicalSpecs
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze compatibility with various platforms"""
        compatibility = {}
        
        # YouTube compatibility
        youtube_compat = await self._check_youtube_compatibility(content_format, technical_specs)
        compatibility['youtube'] = youtube_compat
        
        # Instagram compatibility
        instagram_compat = await self._check_instagram_compatibility(content_format, technical_specs)
        compatibility['instagram'] = instagram_compat
        
        # TikTok compatibility
        tiktok_compat = await self._check_tiktok_compatibility(content_format, technical_specs)
        compatibility['tiktok'] = tiktok_compat
        
        # Spotify compatibility (for audio)
        if content_format.value.startswith('audio'):
            spotify_compat = await self._check_spotify_compatibility(content_format, technical_specs)
            compatibility['spotify'] = spotify_compat
        
        return compatibility
    
    async def _check_youtube_compatibility(
        self,
        content_format: ContentFormat,
        technical_specs: TechnicalSpecs
    ) -> Dict[str, Any]:
        """Check YouTube platform compatibility"""
        compat = {
            'compatible': False,
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        if content_format.value.startswith('video'):
            # Video format compatibility
            if content_format in [ContentFormat.VIDEO_MP4, ContentFormat.VIDEO_MOV]:
                compat['score'] += 40
            else:
                compat['issues'].append("Video format not optimal for YouTube")
                compat['recommendations'].append("Convert to MP4 or MOV format")
            
            # Resolution check
            if technical_specs.dimensions:
                if technical_specs.dimensions[1] >= 1080:  # 1080p or higher
                    compat['score'] += 30
                elif technical_specs.dimensions[1] >= 720:  # 720p
                    compat['score'] += 20
                else:
                    compat['issues'].append("Low resolution for YouTube standards")
                    compat['recommendations'].append("Increase resolution to at least 720p")
            
            # Duration check
            if technical_specs.duration:
                if 60 <= technical_specs.duration <= 3600:  # 1 minute to 1 hour
                    compat['score'] += 20
                else:
                    compat['issues'].append("Duration outside optimal range")
                    compat['recommendations'].append("Optimize duration for better engagement")
            
            # Frame rate check
            if technical_specs.frame_rate and technical_specs.frame_rate >= 24:
                compat['score'] += 10
            
            compat['compatible'] = compat['score'] >= 50
        
        return compat
    
    async def _check_instagram_compatibility(
        self,
        content_format: ContentFormat,
        technical_specs: TechnicalSpecs
    ) -> Dict[str, Any]:
        """Check Instagram platform compatibility"""
        compat = {
            'compatible': False,
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        if content_format.value.startswith('image'):
            # Image format compatibility
            if content_format in [ContentFormat.IMAGE_JPEG, ContentFormat.IMAGE_PNG]:
                compat['score'] += 40
            
            # Aspect ratio check
            if technical_specs.dimensions:
                width, height = technical_specs.dimensions
                aspect_ratio = width / height
                
                if 0.8 <= aspect_ratio <= 1.91:  # Instagram supported ratios
                    compat['score'] += 30
                else:
                    compat['issues'].append("Aspect ratio not optimal for Instagram")
                    compat['recommendations'].append("Adjust to square (1:1) or 4:5 ratio")
            
            # Resolution check
            if technical_specs.dimensions and min(technical_specs.dimensions) >= 320:
                compat['score'] += 30
            
            compat['compatible'] = compat['score'] >= 50
        
        elif content_format.value.startswith('video'):
            # Video compatibility for Instagram
            if content_format == ContentFormat.VIDEO_MP4:
                compat['score'] += 40
            
            # Duration check for Instagram video
            if technical_specs.duration:
                if technical_specs.duration <= 60:  # Max 60 seconds for feed
                    compat['score'] += 30
                elif technical_specs.duration <= 15:  # Stories
                    compat['score'] += 40
                else:
                    compat['issues'].append("Video too long for Instagram feed")
                    compat['recommendations'].append("Trim to under 60 seconds")
            
            compat['compatible'] = compat['score'] >= 50
        
        return compat
    
    async def _check_tiktok_compatibility(
        self,
        content_format: ContentFormat,
        technical_specs: TechnicalSpecs
    ) -> Dict[str, Any]:
        """Check TikTok platform compatibility"""
        compat = {
            'compatible': False,
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        if content_format.value.startswith('video'):
            # Video format compatibility
            if content_format == ContentFormat.VIDEO_MP4:
                compat['score'] += 40
            
            # Aspect ratio check (vertical preferred)
            if technical_specs.dimensions:
                width, height = technical_specs.dimensions
                aspect_ratio = width / height
                
                if aspect_ratio < 1:  # Vertical
                    compat['score'] += 40
                elif aspect_ratio == 1:  # Square
                    compat['score'] += 20
                else:
                    compat['issues'].append("Horizontal videos not optimal for TikTok")
                    compat['recommendations'].append("Use vertical (9:16) aspect ratio")
            
            # Duration check
            if technical_specs.duration:
                if technical_specs.duration <= 60:
                    compat['score'] += 20
                else:
                    compat['issues'].append("Video too long for optimal TikTok engagement")
                    compat['recommendations'].append("Keep videos under 60 seconds")
            
            compat['compatible'] = compat['score'] >= 50
        
        return compat
    
    async def _check_spotify_compatibility(
        self,
        content_format: ContentFormat,
        technical_specs: TechnicalSpecs
    ) -> Dict[str, Any]:
        """Check Spotify platform compatibility"""
        compat = {
            'compatible': False,
            'score': 0,
            'issues': [],
            'recommendations': []
        }
        
        # Audio format compatibility
        if content_format in [ContentFormat.AUDIO_MP3, ContentFormat.AUDIO_FLAC]:
            compat['score'] += 40
        
        # Quality requirements
        if technical_specs.sample_rate and technical_specs.sample_rate >= 44100:
            compat['score'] += 30
        
        if technical_specs.bit_rate and technical_specs.bit_rate >= 160000:
            compat['score'] += 30
        else:
            compat['issues'].append("Bit rate below Spotify recommended minimum")
            compat['recommendations'].append("Increase bit rate to at least 160 kbps")
        
        compat['compatible'] = compat['score'] >= 60
        
        return compat
    
    async def _identify_issues(self, analysis: MultiFormatQualityAnalysis):
        """Identify quality issues based on analysis results"""
        
        # Technical issues
        if analysis.quality_metrics.technical_quality_score < 60:
            issue = ContentIssue(
                issue_id=f"tech_quality_{int(time.time())}",
                category="technical",
                severity="high",
                title="Low Technical Quality",
                description="Content does not meet technical quality standards",
                impact="Reduced platform compatibility and user experience",
                suggested_fix="Improve recording/creation settings and post-processing",
                estimated_fix_time="2-4 hours"
            )
            analysis.issues.append(issue)
        
        # Protection readiness issues
        if analysis.quality_metrics.protection_readiness_score < 70:
            issue = ContentIssue(
                issue_id=f"protection_readiness_{int(time.time())}",
                category="protection",
                severity="medium",
                title="Protection Readiness Below Optimal",
                description="Content may not be fully ready for copyright protection",
                impact="Reduced effectiveness of content protection measures",
                suggested_fix="Enhance content uniqueness and quality markers",
                estimated_fix_time="1-2 hours"
            )
            analysis.issues.append(issue)
        
        # Platform compatibility issues
        platform_issues = []
        for platform, compat in analysis.platform_compatibility.items():
            if not compat.get('compatible', False):
                platform_issues.append(platform)
        
        if platform_issues:
            issue = ContentIssue(
                issue_id=f"platform_compat_{int(time.time())}",
                category="compatibility",
                severity="medium",
                title="Platform Compatibility Issues",
                description=f"Content not compatible with: {', '.join(platform_issues)}",
                impact="Limited distribution and monetization opportunities",
                suggested_fix="Adjust format, resolution, or duration for target platforms",
                estimated_fix_time="30 minutes - 2 hours"
            )
            analysis.issues.append(issue)
    
    async def _generate_optimization_recommendations(self, analysis: MultiFormatQualityAnalysis):
        """Generate optimization recommendations based on analysis"""
        
        # Technical optimization
        if analysis.quality_metrics.technical_quality_score < 80:
            rec = OptimizationRecommendation(
                recommendation_id=f"tech_opt_{int(time.time())}",
                category="technical",
                priority="high",
                title="Improve Technical Quality",
                description="Enhance technical aspects to meet platform standards",
                expected_improvement="20-30 point quality score increase",
                implementation_steps=[
                    "Review recording/creation settings",
                    "Apply appropriate post-processing",
                    "Ensure optimal format conversion",
                    "Validate output quality"
                ],
                tools_required=["Audio/video editing software", "Quality analysis tools"],
                estimated_time="2-4 hours"
            )
            analysis.optimization_recommendations.append(rec)
        
        # Engagement optimization
        if analysis.quality_metrics.engagement_potential_score < 75:
            rec = OptimizationRecommendation(
                recommendation_id=f"engagement_opt_{int(time.time())}",
                category="engagement",
                priority="medium",
                title="Boost Engagement Potential",
                description="Optimize content for better audience engagement",
                expected_improvement="Improved audience retention and interaction",
                implementation_steps=[
                    "Enhance opening/hook",
                    "Optimize pacing and structure",
                    "Add engaging visual/audio elements",
                    "Include call-to-action elements"
                ],
                tools_required=["Content editing tools", "Analytics platforms"],
                estimated_time="1-3 hours"
            )
            analysis.optimization_recommendations.append(rec)
        
        # Platform-specific optimizations
        for platform, compat in analysis.platform_compatibility.items():
            if compat.get('score', 0) < 80 and compat.get('recommendations'):
                rec = OptimizationRecommendation(
                    recommendation_id=f"{platform}_opt_{int(time.time())}",
                    category="platform_optimization",
                    priority="medium",
                    title=f"Optimize for {platform.title()}",
                    description=f"Enhance compatibility and performance on {platform}",
                    expected_improvement=f"Better {platform} distribution and engagement",
                    implementation_steps=compat['recommendations'],
                    tools_required=["Format conversion tools", "Platform-specific guidelines"],
                    estimated_time="30 minutes - 2 hours"
                )
                analysis.optimization_recommendations.append(rec)
        
        # SEO optimization
        if analysis.quality_metrics.seo_optimization_score < 70:
            rec = OptimizationRecommendation(
                recommendation_id=f"seo_opt_{int(time.time())}",
                category="seo",
                priority="low",
                title="Improve SEO Optimization",
                description="Enhance content for better search visibility",
                expected_improvement="Increased organic discovery and reach",
                implementation_steps=[
                    "Add relevant keywords to metadata",
                    "Optimize title and description",
                    "Include appropriate tags",
                    "Ensure accessibility compliance"
                ],
                tools_required=["SEO analysis tools", "Keyword research tools"],
                estimated_time="30 minutes - 1 hour"
            )
            analysis.optimization_recommendations.append(rec)


# Export the main analyzer class
__all__ = ['MultiFormatContentQualityAnalyzer', 'MultiFormatQualityAnalysis', 'ContentFormat', 'QualityLevel', 'ProtectionReadiness']
