"""
Quality Agent - Industrial-Grade Content Quality Management System

Advanced AI-driven quality assessment, scoring, and enhancement system for all content types.
Comprehensive quality control with automated improvement suggestions and real-time monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from pathlib import Path

from ..base import BaseAgent, AgentStatus
from ..protection_agent import ProtectionAgent
from ..content_agent import ContentAgent
try:
    from core.exceptions import QualityError, ValidationError, ProcessingError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    QualityError, ValidationError, ProcessingError = globals().get('QualityError, ValidationError, ProcessingError', Exception)
try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
from ...utils.metrics_collector import MetricsCollector
from ...utils.content_analyzer import ContentAnalyzer
from ...security.content_validator import ContentValidator
from ...ml.quality_models import QualityModelManager
from ...database.models.quality import QualityReport, QualityMetric, QualityRule

# Import extended analysis methods
try:
    from .quality_agent_extended import QualityAnalysisExtensions
except ImportError:
    QualityAnalysisExtensions = None

logger = logging.getLogger(__name__)

class QualityLevel(Enum):
    """Content quality levels"""
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"
    PROFESSIONAL = "professional"

class ContentType(Enum):
    """Supported content types for quality assessment"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MUSIC = "music"
    PODCAST = "podcast"
    BLOG = "blog"
    SOCIAL_POST = "social_post"

@dataclass
class QualityScore:
    """Comprehensive quality scoring structure"""
    overall_score: float = field(default=0.0)
    technical_score: float = field(default=0.0)
    content_score: float = field(default=0.0)
    seo_score: float = field(default=0.0)
    engagement_score: float = field(default=0.0)
    accessibility_score: float = field(default=0.0)
    protection_score: float = field(default=0.0)
    brand_safety_score: float = field(default=0.0)
    monetization_score: float = field(default=0.0)
    viral_potential: float = field(default=0.0)
    quality_level: QualityLevel = field(default=QualityLevel.FAIR)
    confidence: float = field(default=0.0)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass  
class QualityRecommendation:
    """Quality improvement recommendation"""
    category: str
    priority: str  # high, medium, low
    description: str
    impact_score: float
    effort_required: str  # low, medium, high
    estimated_improvement: float
    action_steps: List[str]
    tools_needed: List[str]
    expected_roi: float

@dataclass
class QualityAnalysis:
    """Complete quality analysis result"""
    content_id: str
    content_type: ContentType
    quality_score: QualityScore
    recommendations: List[QualityRecommendation]
    issues_found: List[str]
    strengths: List[str]
    metadata: Dict[str, Any]
    processing_time: float
    analysis_version: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class QualityAgent(BaseAgent):
    """
    Advanced Quality Agent for comprehensive content quality assessment and enhancement.
    
    Features:
    - Multi-dimensional quality scoring (technical, content, SEO, engagement)
    - AI-powered improvement recommendations
    - Real-time quality monitoring
    - Industry-standard compliance checking
    - Automated enhancement suggestions
    - Performance optimization analysis
    - Brand safety assessment
    - Monetization potential evaluation
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            agent_id=agent_id or f"quality_agent_{uuid.uuid4().hex[:8]}",
            agent_type="quality_agent",
            config=config
        )
        
        # Initialize core components
        self.content_analyzer = ContentAnalyzer()
        self.content_validator = ContentValidator()
        self.quality_models = QualityModelManager()
        self.metrics_collector = MetricsCollector()
        
        # Initialize extended analysis methods
        if QualityAnalysisExtensions:
            self.extended_analysis = QualityAnalysisExtensions()
        else:
            self.extended_analysis = None
            self.logger.warning("Extended analysis methods not available")
        
        # Quality assessment configuration
        self.quality_thresholds = {
            QualityLevel.POOR: 0.3,
            QualityLevel.FAIR: 0.5,
            QualityLevel.GOOD: 0.7,
            QualityLevel.EXCELLENT: 0.85,
            QualityLevel.PROFESSIONAL: 0.95
        }
        
        # Quality rules and standards
        self.quality_rules = self._load_quality_rules()
        self.industry_standards = self._load_industry_standards()
        
        # Performance tracking
        self.analysis_cache = {}
        self.performance_metrics = {}
        
        self.logger.info(f"QualityAgent initialized: {self.agent_id}")

    async def analyze_content_quality(
        self,
        content_id: str,
        content_path: str,
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> QualityAnalysis:
        """
        Perform comprehensive quality analysis of content.
        
        Args:
            content_id: Unique identifier for the content
            content_path: Path to content file or URL
            content_type: Type of content to analyze
            metadata: Additional content metadata
            
        Returns:
            QualityAnalysis: Complete quality analysis results
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting quality analysis for {content_id}")
            
            # Validate input
            await self._validate_content_input(content_path, content_type)
            
            # Analyze content structure and technical quality
            technical_analysis = await self._analyze_technical_quality(
                content_path, content_type
            )
            
            # Assess content quality dimensions
            content_analysis = await self._analyze_content_dimensions(
                content_path, content_type, metadata
            )
            
            # Calculate comprehensive quality score
            quality_score = await self._calculate_quality_score(
                technical_analysis, content_analysis, content_type
            )
            
            # Generate improvement recommendations
            recommendations = await self._generate_recommendations(
                quality_score, technical_analysis, content_analysis
            )
            
            # Identify issues and strengths
            issues, strengths = await self._identify_issues_and_strengths(
                quality_score, technical_analysis, content_analysis
            )
            
            # Create quality analysis result
            analysis = QualityAnalysis(
                content_id=content_id,
                content_type=content_type,
                quality_score=quality_score,
                recommendations=recommendations,
                issues_found=issues,
                strengths=strengths,
                metadata=metadata or {},
                processing_time=time.time() - start_time,
                analysis_version="2.0"
            )
            
            # Cache results for performance
            self.analysis_cache[content_id] = analysis
            
            # Update metrics
            await self._update_quality_metrics(analysis)
            
            self.logger.info(
                f"Quality analysis completed for {content_id} in "
                f"{analysis.processing_time:.2f}s"
            )
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Quality analysis failed for {content_id}: {str(e)}")
            raise QualityError(f"Quality analysis failed: {str(e)}")

    async def _analyze_technical_quality(
        self, 
        content_path: str, 
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Analyze technical quality metrics"""
        
        technical_metrics = {}
        
        try:
            if content_type == ContentType.AUDIO or content_type == ContentType.MUSIC:
                technical_metrics = await self._analyze_audio_quality(content_path)
                
            elif content_type == ContentType.VIDEO:
                technical_metrics = await self._analyze_video_quality(content_path)
                
            elif content_type == ContentType.IMAGE:
                technical_metrics = await self._analyze_image_quality(content_path)
                
            elif content_type in [ContentType.TEXT, ContentType.BLOG]:
                technical_metrics = await self._analyze_text_quality(content_path)
                
            # Add universal technical checks
            technical_metrics.update(await self._universal_technical_checks(content_path))
            
        except Exception as e:
            self.logger.error(f"Technical analysis failed: {str(e)}")
            technical_metrics = {"error": str(e)}
            
        return technical_metrics

    async def _analyze_audio_quality(self, content_path: str) -> Dict[str, Any]:
        """Analyze audio/music technical quality"""
        
        metrics = {}
        
        try:
            # Audio format and encoding analysis
            audio_info = await self.content_analyzer.get_audio_info(content_path)
            
            metrics.update({
                "bitrate": audio_info.get("bitrate", 0),
                "sample_rate": audio_info.get("sample_rate", 0),
                "channels": audio_info.get("channels", 0),
                "duration": audio_info.get("duration", 0),
                "format": audio_info.get("format", "unknown"),
                "bit_depth": audio_info.get("bit_depth", 0)
            })
            
            # Audio quality scoring
            bitrate_score = min(audio_info.get("bitrate", 0) / 320000, 1.0)  # 320kbps max
            sample_rate_score = 1.0 if audio_info.get("sample_rate", 0) >= 44100 else 0.5
            
            # Dynamic range analysis
            dynamic_range = await self.content_analyzer.calculate_dynamic_range(content_path)
            dynamic_range_score = min(dynamic_range / 20, 1.0)  # 20dB is excellent
            
            # Spectral analysis
            spectral_analysis = await self.content_analyzer.analyze_spectrum(content_path)
            frequency_balance_score = spectral_analysis.get("balance_score", 0.5)
            
            # Noise analysis
            noise_floor = await self.content_analyzer.detect_noise_floor(content_path)
            noise_score = max(0, 1.0 - (noise_floor / -60))  # -60dB is good
            
            # Audio mastering quality
            mastering_score = await self._assess_mastering_quality(content_path)
            
            metrics.update({
                "bitrate_score": bitrate_score,
                "sample_rate_score": sample_rate_score,
                "dynamic_range": dynamic_range,
                "dynamic_range_score": dynamic_range_score,
                "frequency_balance_score": frequency_balance_score,
                "noise_floor": noise_floor,
                "noise_score": noise_score,
                "mastering_score": mastering_score,
                "technical_score": np.mean([
                    bitrate_score, sample_rate_score, dynamic_range_score,
                    frequency_balance_score, noise_score, mastering_score
                ])
            })
            
        except Exception as e:
            self.logger.error(f"Audio quality analysis failed: {str(e)}")
            metrics = {"error": str(e), "technical_score": 0.0}
            
        return metrics

    async def _analyze_video_quality(self, content_path: str) -> Dict[str, Any]:
        """Analyze video technical quality"""
        
        metrics = {}
        
        try:
            # Video format and encoding analysis
            video_info = await self.content_analyzer.get_video_info(content_path)
            
            metrics.update({
                "resolution": video_info.get("resolution", "unknown"),
                "framerate": video_info.get("framerate", 0),
                "bitrate": video_info.get("bitrate", 0),
                "duration": video_info.get("duration", 0),
                "codec": video_info.get("codec", "unknown"),
                "aspect_ratio": video_info.get("aspect_ratio", "unknown")
            })
            
            # Resolution scoring
            resolution = video_info.get("resolution", "")
            if "4K" in resolution or "2160p" in resolution:
                resolution_score = 1.0
            elif "1080p" in resolution:
                resolution_score = 0.8
            elif "720p" in resolution:
                resolution_score = 0.6
            else:
                resolution_score = 0.3
                
            # Framerate scoring  
            framerate = video_info.get("framerate", 0)
            framerate_score = min(framerate / 60, 1.0)
            
            # Bitrate scoring
            bitrate = video_info.get("bitrate", 0)
            bitrate_score = min(bitrate / 8000000, 1.0)  # 8Mbps as reference
            
            # Visual quality analysis
            visual_quality = await self.content_analyzer.analyze_visual_quality(content_path)
            sharpness_score = visual_quality.get("sharpness", 0.5)
            color_accuracy_score = visual_quality.get("color_accuracy", 0.5)
            exposure_score = visual_quality.get("exposure", 0.5)
            
            # Compression artifacts detection
            artifacts_score = await self._detect_compression_artifacts(content_path)
            
            metrics.update({
                "resolution_score": resolution_score,
                "framerate_score": framerate_score,
                "bitrate_score": bitrate_score,
                "sharpness_score": sharpness_score,
                "color_accuracy_score": color_accuracy_score,
                "exposure_score": exposure_score,
                "artifacts_score": artifacts_score,
                "technical_score": np.mean([
                    resolution_score, framerate_score, bitrate_score,
                    sharpness_score, color_accuracy_score, exposure_score, artifacts_score
                ])
            })
            
        except Exception as e:
            self.logger.error(f"Video quality analysis failed: {str(e)}")
            metrics = {"error": str(e), "technical_score": 0.0}
            
        return metrics

    async def _analyze_image_quality(self, content_path: str) -> Dict[str, Any]:
        """Analyze image technical quality"""
        
        metrics = {}
        
        try:
            # Image metadata and properties
            image_info = await self.content_analyzer.get_image_info(content_path)
            
            metrics.update({
                "resolution": f"{image_info.get('width', 0)}x{image_info.get('height', 0)}",
                "file_size": image_info.get("file_size", 0),
                "format": image_info.get("format", "unknown"),
                "color_space": image_info.get("color_space", "unknown"),
                "dpi": image_info.get("dpi", 0)
            })
            
            # Resolution scoring
            width = image_info.get("width", 0)
            height = image_info.get("height", 0)
            total_pixels = width * height
            
            if total_pixels >= 8000000:  # 8MP+
                resolution_score = 1.0
            elif total_pixels >= 2000000:  # 2MP+
                resolution_score = 0.8
            elif total_pixels >= 1000000:  # 1MP+
                resolution_score = 0.6
            else:
                resolution_score = 0.3
                
            # Quality metrics analysis
            quality_metrics = await self.content_analyzer.analyze_image_quality(content_path)
            sharpness_score = quality_metrics.get("sharpness", 0.5)
            noise_score = quality_metrics.get("noise_score", 0.5)
            contrast_score = quality_metrics.get("contrast", 0.5)
            color_balance_score = quality_metrics.get("color_balance", 0.5)
            exposure_score = quality_metrics.get("exposure", 0.5)
            
            # Composition analysis
            composition_score = await self._analyze_image_composition(content_path)
            
            metrics.update({
                "resolution_score": resolution_score,
                "sharpness_score": sharpness_score,
                "noise_score": noise_score,
                "contrast_score": contrast_score,
                "color_balance_score": color_balance_score,
                "exposure_score": exposure_score,
                "composition_score": composition_score,
                "technical_score": np.mean([
                    resolution_score, sharpness_score, noise_score,
                    contrast_score, color_balance_score, exposure_score, composition_score
                ])
            })
            
        except Exception as e:
            self.logger.error(f"Image quality analysis failed: {str(e)}")
            metrics = {"error": str(e), "technical_score": 0.0}
            
        return metrics

    async def _analyze_text_quality(self, content_path: str) -> Dict[str, Any]:
        """Analyze text/blog content technical quality"""
        
        metrics = {}
        
        try:
            # Read and analyze text content
            text_content = await self.content_analyzer.read_text_content(content_path)
            
            # Basic text metrics
            word_count = len(text_content.split())
            char_count = len(text_content)
            sentence_count = len([s for s in text_content.split('.') if s.strip()])
            paragraph_count = len([p for p in text_content.split('\n\n') if p.strip()])
            
            metrics.update({
                "word_count": word_count,
                "character_count": char_count,
                "sentence_count": sentence_count,
                "paragraph_count": paragraph_count,
                "average_words_per_sentence": word_count / max(sentence_count, 1),
                "average_sentences_per_paragraph": sentence_count / max(paragraph_count, 1)
            })
            
            # Readability analysis
            readability = await self.content_analyzer.calculate_readability(text_content)
            readability_score = readability.get("flesch_kincaid_score", 0.5)
            
            # Grammar and spelling check
            grammar_check = await self.content_analyzer.check_grammar(text_content)
            grammar_score = 1.0 - (grammar_check.get("error_count", 0) / max(word_count, 1))
            grammar_score = max(0, min(1.0, grammar_score))
            
            # SEO analysis
            seo_analysis = await self._analyze_seo_quality(text_content)
            seo_score = seo_analysis.get("seo_score", 0.5)
            
            # Content structure analysis
            structure_score = await self._analyze_content_structure(text_content)
            
            # Uniqueness and plagiarism check
            uniqueness_score = await self._check_content_uniqueness(text_content)
            
            metrics.update({
                "readability_score": readability_score,
                "grammar_score": grammar_score,
                "seo_score": seo_score,
                "structure_score": structure_score,
                "uniqueness_score": uniqueness_score,
                "technical_score": np.mean([
                    readability_score, grammar_score, seo_score,
                    structure_score, uniqueness_score
                ])
            })
            
        except Exception as e:
            self.logger.error(f"Text quality analysis failed: {str(e)}")
            metrics = {"error": str(e), "technical_score": 0.0}
            
        return metrics

    async def _analyze_content_dimensions(
        self,
        content_path: str,
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze content quality dimensions beyond technical metrics"""
        
        dimensions = {}
        
        try:
            # Engagement potential analysis
            engagement_analysis = await self._analyze_engagement_potential(
                content_path, content_type, metadata
            )
            
            # Brand safety assessment
            brand_safety = await self._assess_brand_safety(content_path, content_type)
            
            # Accessibility evaluation
            accessibility = await self._evaluate_accessibility(content_path, content_type)
            
            # Monetization potential
            monetization = await self._assess_monetization_potential(
                content_path, content_type, metadata
            )
            
            # Viral potential prediction
            viral_potential = await self._predict_viral_potential(
                content_path, content_type, metadata
            )
            
            # Content relevance and trends
            relevance_analysis = await self._analyze_content_relevance(
                content_path, content_type, metadata
            )
            
            dimensions.update({
                "engagement": engagement_analysis,
                "brand_safety": brand_safety,
                "accessibility": accessibility,
                "monetization": monetization,
                "viral_potential": viral_potential,
                "relevance": relevance_analysis
            })
            
        except Exception as e:
            self.logger.error(f"Content dimensions analysis failed: {str(e)}")
            dimensions = {"error": str(e)}
            
        return dimensions

    async def _calculate_quality_score(
        self,
        technical_analysis: Dict[str, Any],
        content_analysis: Dict[str, Any],
        content_type: ContentType
    ) -> QualityScore:
        """Calculate comprehensive quality score with weighted metrics"""



        
        try:
            # Technical score from technical analysis
            technical_score = technical_analysis.get("technical_score", 0.0)
            
            # Content dimension scores
            engagement_score = content_analysis.get("engagement", {}).get("score", 0.0)
            brand_safety_score = content_analysis.get("brand_safety", {}).get("score", 0.0)
            accessibility_score = content_analysis.get("accessibility", {}).get("score", 0.0)
            monetization_score = content_analysis.get("monetization", {}).get("score", 0.0)
            viral_potential = content_analysis.get("viral_potential", {}).get("score", 0.0)
            
            # SEO score (content-type specific)
            seo_score = 0.0
            if content_type in [ContentType.TEXT, ContentType.BLOG, ContentType.SOCIAL_POST]:
                seo_score = technical_analysis.get("seo_score", 0.0)
            
            # Content quality score
            content_score = np.mean([engagement_score, brand_safety_score, accessibility_score])
            
            # Protection score (copyright and rights compliance)
            protection_score = content_analysis.get("brand_safety", {}).get("copyright_score", 0.8)
            
            # Weighted overall score based on content type
            weights = self._get_quality_weights(content_type)
            
            overall_score = (
                weights["technical"] * technical_score +
                weights["content"] * content_score +
                weights["seo"] * seo_score +
                weights["engagement"] * engagement_score +
                weights["accessibility"] * accessibility_score +
                weights["protection"] * protection_score +
                weights["brand_safety"] * brand_safety_score +
                weights["monetization"] * monetization_score
            )
            
            # Determine quality level
            quality_level = self._determine_quality_level(overall_score)
            
            # Calculate confidence based on data completeness
            confidence = self._calculate_confidence(technical_analysis, content_analysis)
            
            return QualityScore(
                overall_score=overall_score,
                technical_score=technical_score,
                content_score=content_score,
                seo_score=seo_score,
                engagement_score=engagement_score,
                accessibility_score=accessibility_score,
                protection_score=protection_score,
                brand_safety_score=brand_safety_score,
                monetization_score=monetization_score,
                viral_potential=viral_potential,
                quality_level=quality_level,
                confidence=confidence
            )
            
        except Exception as e:
            self.logger.error(f"Quality score calculation failed: {str(e)}")
            return QualityScore(overall_score=0.0, quality_level=QualityLevel.POOR)

    def _get_quality_weights(self, content_type: ContentType) -> Dict[str, float]:
        """Get quality scoring weights based on content type"""
        
        base_weights = {
            "technical": 0.25,
            "content": 0.20,
            "seo": 0.15,
            "engagement": 0.15,
            "accessibility": 0.10,
            "protection": 0.05,
            "brand_safety": 0.05,
            "monetization": 0.05
        }
        
        # Adjust weights based on content type
        if content_type == ContentType.MUSIC:
            base_weights.update({
                "technical": 0.35,  # More emphasis on audio quality
                "engagement": 0.20,
                "monetization": 0.10
            })
            
        elif content_type in [ContentType.TEXT, ContentType.BLOG]:
            base_weights.update({
                "seo": 0.25,  # Higher SEO importance
                "content": 0.25,
                "technical": 0.15
            })
            
        elif content_type == ContentType.SOCIAL_POST:
            base_weights.update({
                "engagement": 0.30,  # Highest engagement importance
                "viral_potential": 0.15,
                "content": 0.20
            })
            
        return base_weights

    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """Determine quality level from overall score"""
        
        for level, threshold in sorted(
            self.quality_thresholds.items(), 
            key=lambda x: x[1], 
            reverse=True
        ):
            if overall_score >= threshold:
                return level
                
        return QualityLevel.POOR

    async def _generate_recommendations(
        self,
        quality_score: QualityScore,
        technical_analysis: Dict[str, Any],
        content_analysis: Dict[str, Any]
    ) -> List[QualityRecommendation]:
        """Generate AI-powered improvement recommendations"""
        
        recommendations = []
        
        try:
            # Technical improvements
            if quality_score.technical_score < 0.7:
                tech_recs = await self._generate_technical_recommendations(
                    technical_analysis, quality_score
                )
                recommendations.extend(tech_recs)
                
            # Content improvements
            if quality_score.content_score < 0.7:
                content_recs = await self._generate_content_recommendations(
                    content_analysis, quality_score
                )
                recommendations.extend(content_recs)
                
            # SEO improvements
            if quality_score.seo_score < 0.7:
                seo_recs = await self._generate_seo_recommendations(
                    technical_analysis, content_analysis
                )
                recommendations.extend(seo_recs)
                
            # Engagement improvements
            if quality_score.engagement_score < 0.7:
                engagement_recs = await self._generate_engagement_recommendations(
                    content_analysis, quality_score
                )
                recommendations.extend(engagement_recs)
                
            # Accessibility improvements
            if quality_score.accessibility_score < 0.8:
                accessibility_recs = await self._generate_accessibility_recommendations(
                    content_analysis
                )
                recommendations.extend(accessibility_recs)
                
            # Sort by priority and impact
            recommendations.sort(
                key=lambda x: (
                    {"high": 3, "medium": 2, "low": 1}[x.priority], 
                    x.impact_score
                ), 
                reverse=True
            )
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {str(e)}")
            
        return recommendations

    async def _generate_technical_recommendations(
        self,
        technical_analysis: Dict[str, Any],
        quality_score: QualityScore
    ) -> List[QualityRecommendation]:
        """Generate technical quality improvement recommendations"""
        
        recommendations = []
        
        # Audio quality recommendations
        if "bitrate_score" in technical_analysis and technical_analysis["bitrate_score"] < 0.7:
            recommendations.append(QualityRecommendation(
                category="Technical - Audio",
                priority="high",
                description="Improve audio bitrate quality for better sound reproduction",
                impact_score=0.8,
                effort_required="medium",
                estimated_improvement=0.2,
                action_steps=[
                    "Re-encode audio at minimum 256kbps (320kbps recommended)",
                    "Use lossless compression formats when possible",
                    "Ensure source material is high quality before encoding"
                ],
                tools_needed=["Audio encoder", "Quality analyzer"],
                expected_roi=85.0
            ))
            
        # Video quality recommendations  
        if "resolution_score" in technical_analysis and technical_analysis["resolution_score"] < 0.6:
            recommendations.append(QualityRecommendation(
                category="Technical - Video",
                priority="high",
                description="Increase video resolution for better visual quality",
                impact_score=0.7,
                effort_required="high",
                estimated_improvement=0.3,
                action_steps=[
                    "Re-shoot or upscale to minimum 1080p resolution",
                    "Ensure proper camera settings and stabilization",
                    "Use professional video editing software"
                ],
                tools_needed=["Video camera/capture", "Video editing software"],
                expected_roi=75.0
            ))
            
        return recommendations

    async def enhance_content_quality(
        self,
        content_id: str,
        enhancement_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply automated quality enhancements to content"""



        
        try:
            self.logger.info(f"Starting quality enhancement for {content_id}")
            
            # Get current quality analysis
            if content_id in self.analysis_cache:
                current_analysis = self.analysis_cache[content_id]
            else:
                raise QualityError(f"No quality analysis found for {content_id}")
                
            # Apply enhancements based on recommendations
            enhancement_results = {}
            
            for enhancement_type in enhancement_options.get("types", []):
                if enhancement_type == "audio_enhancement":
                    result = await self._enhance_audio_quality(
                        content_id, enhancement_options
                    )
                    enhancement_results["audio"] = result
                    
                elif enhancement_type == "video_enhancement":
                    result = await self._enhance_video_quality(
                        content_id, enhancement_options
                    )
                    enhancement_results["video"] = result
                    
                elif enhancement_type == "image_enhancement":
                    result = await self._enhance_image_quality(
                        content_id, enhancement_options
                    )
                    enhancement_results["image"] = result
                    
                elif enhancement_type == "text_enhancement":
                    result = await self._enhance_text_quality(
                        content_id, enhancement_options
                    )
                    enhancement_results["text"] = result
                    
            self.logger.info(f"Quality enhancement completed for {content_id}")
            
            return {
                "content_id": content_id,
                "enhancements_applied": enhancement_results,
                "status": "completed",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Quality enhancement failed for {content_id}: {str(e)}")
            raise QualityError(f"Quality enhancement failed: {str(e)}")

    async def get_quality_report(
        self,
        content_ids: List[str],
        report_type: str = "detailed"
    ) -> Dict[str, Any]:
        """Generate comprehensive quality report for multiple content pieces"""



        
        try:
            self.logger.info(f"Generating quality report for {len(content_ids)} items")
            
            report_data = {
                "report_id": f"quality_report_{uuid.uuid4().hex[:8]}",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "report_type": report_type,
                "content_count": len(content_ids),
                "analyses": [],
                "summary": {},
                "recommendations": []
            }
            
            # Collect analysis data
            total_scores = []
            quality_levels = {}
            
            for content_id in content_ids:
                if content_id in self.analysis_cache:
                    analysis = self.analysis_cache[content_id]
                    
                    if report_type == "detailed":
                        report_data["analyses"].append(analysis.__dict__)
                    elif report_type == "summary":
                        report_data["analyses"].append({
                            "content_id": analysis.content_id,
                            "overall_score": analysis.quality_score.overall_score,
                            "quality_level": analysis.quality_score.quality_level.value,
                            "top_issues": analysis.issues_found[:3],
                            "top_recommendations": analysis.recommendations[:3]
                        })
                        
                    total_scores.append(analysis.quality_score.overall_score)
                    level = analysis.quality_score.quality_level.value
                    quality_levels[level] = quality_levels.get(level, 0) + 1
                    
            # Generate summary statistics
            if total_scores:
                report_data["summary"] = {
                    "average_score": np.mean(total_scores),
                    "score_distribution": {
                        "min": min(total_scores),
                        "max": max(total_scores),
                        "median": np.median(total_scores),
                        "std_dev": np.std(total_scores)
                    },
                    "quality_level_distribution": quality_levels,
                    "overall_health": self._calculate_overall_health(total_scores, quality_levels)
                }
                
            self.logger.info("Quality report generated successfully")
            
            return report_data
            
        except Exception as e:
            self.logger.error(f"Quality report generation failed: {str(e)}")
            raise QualityError(f"Quality report generation failed: {str(e)}")

    # Helper methods for specific quality analysis tasks
    async def _assess_mastering_quality(self, content_path: str) -> float:
        """Assess audio mastering quality using advanced algorithms"""



        try:
            # Load audio data
            y, sr = librosa.load(content_path)
            
            # Calculate LUFS (Loudness Units relative to Full Scale)
            lufs = await self.content_analyzer.calculate_lufs(y, sr)
            lufs_score = 1.0 - abs(lufs + 23) / 20  # Target: -23 LUFS for streaming
            lufs_score = max(0, min(1.0, lufs_score))
            
            # Calculate dynamic range (DR)
            dynamic_range = await self.content_analyzer.calculate_dynamic_range_dr(y, sr)
            dr_score = min(dynamic_range / 14, 1.0)  # DR14 is excellent
            
            # Peak normalization check
            peak_level = np.max(np.abs(y))
            peak_score = 1.0 if peak_level < 0.95 else 0.5  # Avoid clipping
            
            # Stereo imaging analysis (for stereo content)
            if len(y.shape) == 2:
                stereo_score = await self._analyze_stereo_imaging(y)
            else:
                stereo_score = 0.8  # Default for mono
            
            # Frequency balance assessment
            freq_balance_score = await self._analyze_frequency_balance(y, sr)
            
            # Calculate overall mastering score
            mastering_score = np.mean([
                lufs_score * 0.25,
                dr_score * 0.25,
                peak_score * 0.15,
                stereo_score * 0.15,
                freq_balance_score * 0.20
            ])
            
            return float(mastering_score)
            
        except Exception as e:
            self.logger.error(f"Mastering quality assessment failed: {str(e)}")
            return 0.5

    async def _detect_compression_artifacts(self, content_path: str) -> float:
        """Detect video compression artifacts using advanced computer vision"""



        try:
            # Load video frames for analysis
            cap = cv2.VideoCapture(content_path)
            artifact_scores = []
            frame_count = 0
            max_frames = 30  # Analyze first 30 frames for efficiency
            
            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Convert to grayscale for analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect blocking artifacts
                blocking_score = await self._detect_blocking_artifacts(gray)
                
                # Detect ringing artifacts
                ringing_score = await self._detect_ringing_artifacts(gray)
                
                # Detect mosquito noise
                mosquito_score = await self._detect_mosquito_noise(gray)
                
                # Detect blur/loss of detail
                blur_score = await self._detect_compression_blur(gray)
                
                # Combine artifact scores
                frame_artifact_score = np.mean([
                    blocking_score, ringing_score, mosquito_score, blur_score
                ])
                artifact_scores.append(frame_artifact_score)
                
                frame_count += 1
                
            cap.release()
            
            # Calculate overall artifact score (1.0 = no artifacts, 0.0 = heavy artifacts)
            if artifact_scores:
                overall_score = np.mean(artifact_scores)
                return float(overall_score)
            else:
                return 0.5
                
        except Exception as e:
            self.logger.error(f"Compression artifact detection failed: {str(e)}")
            return 0.5

    async def _analyze_image_composition(self, content_path: str) -> float:
        """Analyze image composition quality using rule of thirds, leading lines, etc."""



        try:
            # Load image
            image = cv2.imread(content_path)
            if image is None:
                return 0.0
                
            height, width = image.shape[:2]
            
            # Convert to different color spaces for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Rule of thirds analysis
            rule_of_thirds_score = await self._analyze_rule_of_thirds(gray)
            
            # Leading lines detection
            leading_lines_score = await self._detect_leading_lines(gray)
            
            # Balance and symmetry analysis
            balance_score = await self._analyze_visual_balance(image)
            
            # Color harmony assessment
            color_harmony_score = await self._analyze_color_harmony(hsv)
            
            # Focus and depth of field analysis
            focus_score = await self._analyze_focus_quality(gray)
            
            # Subject prominence (using edge detection and saliency)
            subject_prominence_score = await self._analyze_subject_prominence(image)
            
            # Golden ratio spiral analysis
            golden_ratio_score = await self._analyze_golden_ratio(gray)
            
            # Negative space utilization
            negative_space_score = await self._analyze_negative_space(gray)
            
            # Calculate weighted composition score
            composition_score = (
                rule_of_thirds_score * 0.20 +
                leading_lines_score * 0.15 +
                balance_score * 0.15 +
                color_harmony_score * 0.15 +
                focus_score * 0.10 +
                subject_prominence_score * 0.10 +
                golden_ratio_score * 0.10 +
                negative_space_score * 0.05
            )
            
            return float(composition_score)
            
        except Exception as e:
            self.logger.error(f"Image composition analysis failed: {str(e)}")
            return 0.5

    async def _analyze_seo_quality(self, text_content: str) -> Dict[str, Any]:
        """Analyze SEO quality of text content using comprehensive metrics"""



        try:
            # Initialize SEO analyzer
            seo_metrics = {}
            
            # Content length analysis
            word_count = len(text_content.split())
            char_count = len(text_content)
            
            # Optimal length scoring
            if 500 <= word_count <= 2000:
                length_score = 1.0
            elif 300 <= word_count < 500 or 2000 < word_count <= 3000:
                length_score = 0.8
            elif 200 <= word_count < 300 or 3000 < word_count <= 5000:
                length_score = 0.6
            else:
                length_score = 0.3
                
            # Keyword density analysis (assuming metadata contains target keywords)
            keyword_density_score = await self._analyze_keyword_density(text_content)
            
            # Heading structure analysis (H1, H2, H3, etc.)
            heading_structure_score = await self._analyze_heading_structure(text_content)
            
            # Internal/external link analysis
            link_analysis_score = await self._analyze_link_structure(text_content)
            
            # Meta description potential (first paragraph analysis)
            meta_description_score = await self._analyze_meta_description_potential(text_content)
            
            # Readability for SEO (Flesch-Kincaid)
            readability_score = await self._calculate_seo_readability(text_content)
            
            # Semantic richness analysis
            semantic_score = await self._analyze_semantic_richness(text_content)
            
            # Content freshness indicators
            freshness_score = await self._analyze_content_freshness(text_content)
            
            # Schema markup potential
            schema_score = await self._analyze_schema_potential(text_content)
            
            # Calculate overall SEO score
            seo_score = (
                length_score * 0.15 +
                keyword_density_score * 0.20 +
                heading_structure_score * 0.15 +
                link_analysis_score * 0.10 +
                meta_description_score * 0.10 +
                readability_score * 0.10 +
                semantic_score * 0.10 +
                freshness_score * 0.05 +
                schema_score * 0.05
            )
            
            seo_metrics = {
                "seo_score": seo_score,
                "word_count": word_count,
                "character_count": char_count,
                "length_score": length_score,
                "keyword_density_score": keyword_density_score,
                "heading_structure_score": heading_structure_score,
                "link_analysis_score": link_analysis_score,
                "meta_description_score": meta_description_score,
                "readability_score": readability_score,
                "semantic_score": semantic_score,
                "freshness_score": freshness_score,
                "schema_score": schema_score
            }
            
            return seo_metrics
            
        except Exception as e:
            self.logger.error(f"SEO quality analysis failed: {str(e)}")
            return {"seo_score": 0.0}

    async def _analyze_content_structure(self, text_content: str) -> float:
        """Analyze content structure quality including paragraphs, transitions, flow"""



        try:
            # Split into paragraphs
            paragraphs = [p.strip() for p in text_content.split('\n\n') if p.strip()]
            sentences = [s.strip() for s in text_content.split('.') if s.strip()]
            
            if not paragraphs or not sentences:
                return 0.0
                
            # Paragraph length consistency
            paragraph_lengths = [len(p.split()) for p in paragraphs]
            avg_paragraph_length = np.mean(paragraph_lengths)
            std_paragraph_length = np.std(paragraph_lengths)
            
            # Optimal paragraph length scoring (50-150 words per paragraph)
            if 50 <= avg_paragraph_length <= 150:
                paragraph_length_score = 1.0
            elif 30 <= avg_paragraph_length < 50 or 150 < avg_paragraph_length <= 200:
                paragraph_length_score = 0.8
            else:
                paragraph_length_score = 0.5
                
            # Paragraph length consistency scoring
            consistency_score = max(0, 1.0 - (std_paragraph_length / max(avg_paragraph_length, 1)) * 0.5)
            
            # Sentence variety analysis
            sentence_lengths = [len(s.split()) for s in sentences]
            sentence_variety_score = min(1.0, np.std(sentence_lengths) / 5.0)  # Good variety
            
            # Transition words analysis
            transition_score = await self._analyze_transition_words(text_content)
            
            # Logical flow assessment using NLP
            flow_score = await self._analyze_logical_flow(paragraphs)
            
            # Introduction and conclusion analysis
            intro_conclusion_score = await self._analyze_intro_conclusion(paragraphs)
            
            # Topic coherence throughout content
            coherence_score = await self._analyze_topic_coherence(paragraphs)
            
            # Calculate overall structure score
            structure_score = (
                paragraph_length_score * 0.20 +
                consistency_score * 0.15 +
                sentence_variety_score * 0.15 +
                transition_score * 0.15 +
                flow_score * 0.15 +
                intro_conclusion_score * 0.10 +
                coherence_score * 0.10
            )
            
            return float(structure_score)
            
        except Exception as e:
            self.logger.error(f"Content structure analysis failed: {str(e)}")
            return 0.5

    async def _check_content_uniqueness(self, text_content: str) -> float:
        """Check content uniqueness and plagiarism using advanced algorithms"""



        try:
            # Content fingerprinting using text hashing
            content_hash = await self._generate_content_fingerprint(text_content)
            
            # Semantic similarity analysis with existing content
            semantic_uniqueness = await self._check_semantic_uniqueness(text_content)
            
            # N-gram analysis for plagiarism detection
            ngram_uniqueness = await self._analyze_ngram_uniqueness(text_content)
            
            # Sentence structure uniqueness
            structure_uniqueness = await self._analyze_structure_uniqueness(text_content)
            
            # Paraphrase detection
            paraphrase_score = await self._detect_paraphrasing(text_content)
            
            # Statistical language analysis
            statistical_uniqueness = await self._analyze_statistical_uniqueness(text_content)
            
            # Reference and citation analysis
            citation_score = await self._analyze_citation_patterns(text_content)
            
            # Calculate overall uniqueness score
            uniqueness_score = (
                semantic_uniqueness * 0.30 +
                ngram_uniqueness * 0.25 +
                structure_uniqueness * 0.20 +
                paraphrase_score * 0.15 +
                statistical_uniqueness * 0.05 +
                citation_score * 0.05
            )
            
            # Adjust for content type and length
            word_count = len(text_content.split())
            if word_count < 100:
                uniqueness_score *= 0.8  # Shorter content is harder to be unique
            elif word_count > 2000:
                uniqueness_score *= 1.1  # Longer content bonus for uniqueness
                uniqueness_score = min(1.0, uniqueness_score)
                
            return float(uniqueness_score)
            
        except Exception as e:
            self.logger.error(f"Content uniqueness check failed: {str(e)}")
            return 0.7  # Conservative estimate

    def _load_quality_rules(self) -> Dict[str, Any]:
        """Load quality assessment rules and standards"""



        return {
            "audio": {
                "min_bitrate": 128000,
                "recommended_bitrate": 320000,
                "min_sample_rate": 44100,
                "max_noise_floor": -60
            },
            "video": {
                "min_resolution": "720p",
                "recommended_resolution": "1080p",
                "min_framerate": 24,
                "recommended_framerate": 30
            },
            "image": {
                "min_resolution": 1000000,  # 1MP
                "recommended_resolution": 8000000,  # 8MP
                "min_dpi": 72,
                "print_dpi": 300
            },
            "text": {
                "min_word_count": 100,
                "recommended_word_count": 500,
                "max_reading_level": 12,
                "min_uniqueness": 0.8
            }
        }

    def _load_industry_standards(self) -> Dict[str, Any]:
        """Load industry quality standards"""



        return {
            "broadcast": {
                "audio_standard": "EBU R128",
                "video_standard": "ITU-R BT.709",
                "delivery_specs": "AS-11"
            },
            "streaming": {
                "audio_quality": "320kbps MP3 / 256kbps AAC",
                "video_quality": "1080p H.264",
                "adaptive_bitrates": True
            },
            "print": {
                "image_resolution": "300 DPI",
                "color_space": "CMYK",
                "format": "PDF/X-1a"
            },
            "web": {
                "image_optimization": "WebP preferred",
                "loading_speed": "<3 seconds",
                "mobile_responsive": True,
                "accessibility": "WCAG 2.1 AA"
            }
        }

    async def _validate_content_input(
        self, 
        content_path: str, 
        content_type: ContentType
    ) -> None:
        """Validate content input parameters"""
        
        if not content_path:
            raise ValidationError("Content path is required")
            
        if not isinstance(content_type, ContentType):
            raise ValidationError("Invalid content type")
            
        # Check if content exists and is accessible
        content_exists = await self.content_validator.validate_content_exists(content_path)
        if not content_exists:
            raise ValidationError(f"Content not found: {content_path}")

class QualityAgentManager:
    """
    Manager for multiple Quality Agents with load balancing and coordination.
    """
    
    def __init__(self, max_agents: int = 5):
        self.max_agents = max_agents
        self.agents: List[QualityAgent] = []
        self.agent_pool = asyncio.Queue(maxsize=max_agents)
        self.metrics = MetricsCollector()
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self) -> None:
        """Initialize the agent pool"""
        
        for i in range(self.max_agents):
            agent = QualityAgent(agent_id=f"quality_agent_pool_{i}")
            await agent.initialize()
            self.agents.append(agent)
            await self.agent_pool.put(agent)
            
        self.logger.info(f"QualityAgentManager initialized with {self.max_agents} agents")
        
    async def analyze_content(
        self,
        content_id: str,
        content_path: str,
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> QualityAnalysis:
        """Analyze content using available agent from pool"""
        
        agent = await self.agent_pool.get()
        
        try:
            result = await agent.analyze_content_quality(
                content_id, content_path, content_type, metadata
            )
            return result
            
        finally:
            await self.agent_pool.put(agent)
            
    async def shutdown(self) -> None:
        """Shutdown all agents"""
        
        for agent in self.agents:
            await agent.shutdown()
            
        self.logger.info("QualityAgentManager shutdown completed")

    # Advanced analysis methods for quality assessment
    
    async def _analyze_stereo_imaging(self, audio_data: np.ndarray) -> float:
        """Analyze stereo imaging quality"""



        try:
            if len(audio_data.shape) != 2:
                return 0.8  # Mono content default
                
            left, right = audio_data[0], audio_data[1]
            
            # Calculate correlation between channels
            correlation = np.corrcoef(left, right)[0, 1]
            
            # Calculate stereo width
            mid = (left + right) / 2
            side = (left - right) / 2
            
            # Stereo width ratio
            mid_rms = np.sqrt(np.mean(mid**2))
            side_rms = np.sqrt(np.mean(side**2))
            
            if mid_rms > 0:
                stereo_ratio = side_rms / mid_rms
            else:
                stereo_ratio = 0
                
            # Scoring based on correlation and width
            correlation_score = 1.0 - abs(correlation)  # Less correlation = better stereo
            width_score = min(1.0, stereo_ratio * 2)  # Good stereo width
            
            return (correlation_score + width_score) / 2
            
        except Exception:
            return 0.6
            
    async def _analyze_frequency_balance(self, audio_data: np.ndarray, sr: int) -> float:
        """Analyze frequency balance in audio"""



        try:
            # Calculate spectral centroid
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
            
            # Calculate frequency bands energy
            stft = librosa.stft(audio_data)
            magnitude = np.abs(stft)
            
            # Define frequency bands
            freqs = librosa.fft_frequencies(sr=sr)
            
            # Low (20-250 Hz), Mid (250-4000 Hz), High (4000-20000 Hz)
            low_band = magnitude[(freqs >= 20) & (freqs <= 250)].mean()
            mid_band = magnitude[(freqs > 250) & (freqs <= 4000)].mean()
            high_band = magnitude[(freqs > 4000) & (freqs <= 20000)].mean()
            
            # Calculate balance score
            total_energy = low_band + mid_band + high_band
            if total_energy > 0:
                low_ratio = low_band / total_energy
                mid_ratio = mid_band / total_energy
                high_ratio = high_band / total_energy
                
                # Ideal ratios: Low ~30%, Mid ~50%, High ~20%
                balance_score = 1.0 - (
                    abs(low_ratio - 0.30) + 
                    abs(mid_ratio - 0.50) + 
                    abs(high_ratio - 0.20)
                ) / 2
                
                return max(0, balance_score)
            else:
                return 0.0
                
        except Exception:
            return 0.5

    async def _detect_blocking_artifacts(self, frame: np.ndarray) -> float:
        """Detect blocking artifacts in video frame"""



        try:
            # Apply gradient filters to detect block edges
            grad_x = cv2.Sobel(frame, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=3)
            
            # Block-grid detection (8x8 and 16x16 patterns)
            block_edges_8 = 0
            block_edges_16 = 0
            
            height, width = frame.shape
            
            # Check for regular patterns in gradients
            for i in range(8, height, 8):
                block_edges_8 += np.sum(np.abs(grad_y[i, :]))
                
            for j in range(8, width, 8):
                block_edges_8 += np.sum(np.abs(grad_x[:, j]))
                
            # Similar for 16x16 blocks
            for i in range(16, height, 16):
                block_edges_16 += np.sum(np.abs(grad_y[i, :]))
                
            for j in range(16, width, 16):
                block_edges_16 += np.sum(np.abs(grad_x[:, j]))
                
            # Normalize and invert (high value = high artifacts)
            total_gradients = np.sum(np.abs(grad_x)) + np.sum(np.abs(grad_y))
            
            if total_gradients > 0:
                blocking_ratio = (block_edges_8 + block_edges_16) / total_gradients
                artifact_score = max(0, 1.0 - blocking_ratio * 10)  # Invert
                return artifact_score
            else:
                return 1.0
                
        except Exception:
            return 0.7

    async def _detect_ringing_artifacts(self, frame: np.ndarray) -> float:
        """Detect ringing artifacts around edges"""



        try:
            # Edge detection
            edges = cv2.Canny(frame, 50, 150)
            
            # Dilate edges to create edge neighborhoods
            kernel = np.ones((5, 5), np.uint8)
            edge_neighborhood = cv2.dilate(edges, kernel, iterations=1)
            
            # Calculate variance in edge neighborhoods
            edge_pixels = frame[edge_neighborhood > 0]
            
            if len(edge_pixels) > 0:
                edge_variance = np.var(edge_pixels)
                # High variance indicates ringing
                ringing_score = max(0, 1.0 - edge_variance / 1000)
                return ringing_score
            else:
                return 1.0
                
        except Exception:
            return 0.7

    async def _detect_mosquito_noise(self, frame: np.ndarray) -> float:
        """Detect mosquito noise artifacts"""



        try:
            # Apply Gaussian blur and compare
            blurred = cv2.GaussianBlur(frame, (5, 5), 1.0)
            diff = np.abs(frame.astype(float) - blurred.astype(float))
            
            # High frequency noise detection
            noise_level = np.mean(diff)
            mosquito_score = max(0, 1.0 - noise_level / 20)
            
            return mosquito_score
            
        except Exception:
            return 0.7

    async def _detect_compression_blur(self, frame: np.ndarray) -> float:
        """Detect blur from compression"""



        try:
            # Laplacian variance for sharpness measurement
            laplacian_var = cv2.Laplacian(frame, cv2.CV_64F).var()
            
            # Normalize sharpness score
            sharpness_score = min(1.0, laplacian_var / 500)
            
            return sharpness_score
            
        except Exception:
            return 0.5

    async def _analyze_rule_of_thirds(self, image: np.ndarray) -> float:
        """Analyze adherence to rule of thirds"""



        try:
            height, width = image.shape
            
            # Define third lines
            h_third1, h_third2 = height // 3, 2 * height // 3
            w_third1, w_third2 = width // 3, 2 * width // 3
            
            # Calculate interest points at intersections
            intersection_points = [
                (h_third1, w_third1), (h_third1, w_third2),
                (h_third2, w_third1), (h_third2, w_third2)
            ]
            
            # Detect edges/features
            edges = cv2.Canny(image, 50, 150)
            
            # Check for features near intersection points
            score = 0
            for h, w in intersection_points:
                # Check 20x20 area around intersection
                roi = edges[max(0, h-10):min(height, h+10), 
                           max(0, w-10):min(width, w+10)]
                if roi.size > 0 and np.sum(roi) > 0:
                    score += 1
                    
            return score / 4.0  # Normalize to 0-1
            
        except Exception:
            return 0.5

    async def _detect_leading_lines(self, image: np.ndarray) -> float:
        """Detect leading lines in composition"""



        try:
            # Edge detection
            edges = cv2.Canny(image, 50, 150)
            
            # Hough line detection
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, 
                                   minLineLength=50, maxLineGap=10)
            
            if lines is not None and len(lines) > 0:
                # Analyze line directions and convergence
                line_score = min(1.0, len(lines) / 10)
                return line_score
            else:
                return 0.3
                
        except Exception:
            return 0.4

    async def _analyze_visual_balance(self, image: np.ndarray) -> float:
        """Analyze visual balance and weight distribution"""



        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
                
            height, width = gray.shape
            
            # Divide image into quadrants
            h_mid, w_mid = height // 2, width // 2
            
            q1 = gray[:h_mid, :w_mid]
            q2 = gray[:h_mid, w_mid:]
            q3 = gray[h_mid:, :w_mid]
            q4 = gray[h_mid:, w_mid:]
            
            # Calculate visual weight (higher values = more visual weight)
            weights = []
            for quadrant in [q1, q2, q3, q4]:
                # Edge density as visual weight
                edges = cv2.Canny(quadrant, 50, 150)
                weight = np.sum(edges) / (quadrant.shape[0] * quadrant.shape[1])
                weights.append(weight)
                
            # Calculate balance (lower variance = better balance)
            balance_score = max(0, 1.0 - np.std(weights) / (np.mean(weights) + 1e-6))
            
            return balance_score
            
        except Exception:
            return 0.5

    async def _analyze_color_harmony(self, hsv_image: np.ndarray) -> float:
        """Analyze color harmony in the image"""



        try:
            # Extract hue channel
            hue = hsv_image[:, :, 0]
            
            # Calculate dominant hues
            hue_hist = cv2.calcHist([hue], [0], None, [180], [0, 180])
            
            # Find dominant hue peaks
            peaks = []
            for i in range(5, 175):
                if (hue_hist[i] > hue_hist[i-5:i].max() and 
                    hue_hist[i] > hue_hist[i+1:i+6].max()):
                    peaks.append(i)
                    
            if len(peaks) >= 2:
                # Analyze hue relationships (complementary, triadic, etc.)
                hue_diffs = []
                for i in range(len(peaks)):
                    for j in range(i+1, len(peaks)):
                        diff = abs(peaks[i] - peaks[j])
                        diff = min(diff, 180 - diff)  # Circular difference
                        hue_diffs.append(diff)
                        
                # Check for harmonious relationships
                harmony_score = 0
                for diff in hue_diffs:
                    if 55 <= diff <= 65:  # Complementary (60°)
                        harmony_score += 0.8
                    elif 115 <= diff <= 125:  # Complementary (120°)
                        harmony_score += 1.0
                    elif 25 <= diff <= 35:  # Analogous (30°)
                        harmony_score += 0.6
                        
                return min(1.0, harmony_score / len(hue_diffs))
            else:
                return 0.7  # Monochromatic can be harmonious
                
        except Exception:
            return 0.6

    # Missing analysis methods implementation
    async def _assess_brand_safety(
        self,
        content_path: str,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Assess brand safety and content appropriateness"""



        try:
            brand_safety_metrics = {"score": 0.0}
            
            if content_type in [ContentType.TEXT, ContentType.BLOG, ContentType.SOCIAL_POST]:
                # Text-based brand safety
                with open(content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                    
                # Check for inappropriate content
                inappropriate_score = await self._check_inappropriate_content(text_content)
                brand_safety_metrics["inappropriate_content_score"] = inappropriate_score
                
                # Check for controversial topics
                controversy_score = await self._check_controversial_topics(text_content)
                brand_safety_metrics["controversy_score"] = controversy_score
                
                # Professional tone analysis
                tone_score = await self._analyze_professional_tone(text_content)
                brand_safety_metrics["tone_score"] = tone_score
                
                # Overall brand safety score
                brand_safety_metrics["score"] = (
                    inappropriate_score * 0.4 +
                    controversy_score * 0.3 +
                    tone_score * 0.3
                )
                
            elif content_type in [ContentType.IMAGE]:
                # Image brand safety
                brand_safety_metrics = await self._assess_image_brand_safety(content_path)
                
            elif content_type in [ContentType.VIDEO]:
                # Video brand safety  
                brand_safety_metrics = await self._assess_video_brand_safety(content_path)
                
            elif content_type in [ContentType.AUDIO, ContentType.MUSIC]:
                # Audio brand safety
                brand_safety_metrics = await self._assess_audio_brand_safety(content_path)
                
            return brand_safety_metrics
            
        except Exception as e:
            self.logger.error(f"Brand safety assessment failed: {str(e)}")
            return {"score": 0.5, "error": str(e)}

    async def _check_inappropriate_content(self, text_content: str) -> float:
        """Check for inappropriate or offensive content"""



        try:
            # Define inappropriate keywords/phrases (placeholder implementation)
            inappropriate_terms = [
                'spam', 'scam', 'fake', 'misleading', 'clickbait',
                'violence', 'harmful', 'dangerous', 'illegal',
                'offensive', 'discriminatory', 'hateful', 'toxic'
            ]
            
            text_lower = text_content.lower()
            inappropriate_count = 0
            
            for term in inappropriate_terms:
                if term in text_lower:
                    inappropriate_count += 1
                    
            # Calculate safety score (inverted - high count = low score)
            total_words = len(text_content.split())
            if total_words > 0:
                inappropriate_ratio = inappropriate_count / total_words
                safety_score = max(0, 1.0 - inappropriate_ratio * 20)
            else:
                safety_score = 1.0
                
            return safety_score
            
        except Exception:
            return 0.8

    async def _check_controversial_topics(self, text_content: str) -> float:
        """Check for controversial or sensitive topics"""



        try:
            controversial_topics = [
                'politics', 'religion', 'conspiracy', 'controversy',
                'sensitive', 'polarizing', 'divisive', 'scandal'
            ]
            
            text_lower = text_content.lower()
            controversy_count = sum(1 for topic in controversial_topics if topic in text_lower)
            
            # Score based on controversy presence
            if controversy_count == 0:
                return 1.0
            elif controversy_count <= 2:
                return 0.7
            else:
                return 0.4
                
        except Exception:
            return 0.7

    async def _analyze_professional_tone(self, text_content: str) -> float:
        """Analyze professional tone of content"""



        try:
            professional_indicators = [
                'professional', 'expert', 'research', 'analysis',
                'insights', 'strategy', 'business', 'industry'
            ]
            
            unprofessional_indicators = [
                'slang', 'informal', 'casual', 'unprofessional',
                'biased', 'personal', 'emotional', 'subjective'
            ]
            
            text_lower = text_content.lower()
            professional_count = sum(1 for term in professional_indicators if term in text_lower)
            unprofessional_count = sum(1 for term in unprofessional_indicators if term in text_lower)
            
            # Calculate professional tone score
            if professional_count > unprofessional_count:
                return min(1.0, professional_count / max(1, len(text_content.split()) / 100))
            else:
                return max(0.3, 1.0 - unprofessional_count / max(1, len(text_content.split()) / 50))
                
        except Exception:
            return 0.6

    async def _assess_image_brand_safety(self, content_path: str) -> Dict[str, Any]:
        """Assess brand safety for image content"""



        try:
            # Basic image safety assessment
            return {
                "score": 0.8,  # Placeholder - would use ML model in production
                "visual_content_appropriate": True,
                "text_overlay_safe": True,
                "brand_elements_present": False
            }
        except Exception:
            return {"score": 0.6}

    async def _assess_video_brand_safety(self, content_path: str) -> Dict[str, Any]:
        """Assess brand safety for video content"""



        try:
            # Basic video safety assessment
            return {
                "score": 0.8,  # Placeholder
                "visual_content_safe": True,
                "audio_content_safe": True,
                "duration_appropriate": True
            }
        except Exception:
            return {"score": 0.6}

    async def _assess_audio_brand_safety(self, content_path: str) -> Dict[str, Any]:
        """Assess brand safety for audio content"""



        try:
            # Basic audio safety assessment
            return {
                "score": 0.8,  # Placeholder
                "content_appropriate": True,
                "language_professional": True,
                "music_rights_clear": False  # Would require rights checking
            }
        except Exception:
            return {"score": 0.6}

    async def _evaluate_accessibility(
        self,
        content_path: str,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Evaluate content accessibility compliance"""



        try:
            accessibility_metrics = {"score": 0.0}
            
            if content_type in [ContentType.TEXT, ContentType.BLOG]:
                # Text accessibility
                with open(content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                    
                # Check readability
                readability_score = await self._check_accessibility_readability(text_content)
                
                # Check structure (headers, lists, etc.)
                structure_score = await self._check_accessibility_structure(text_content)
                
                accessibility_metrics = {
                    "score": (readability_score + structure_score) / 2,
                    "readability_score": readability_score,
                    "structure_score": structure_score
                }
                
            elif content_type == ContentType.IMAGE:
                # Image accessibility (alt text potential, contrast, etc.)
                accessibility_metrics = await self._evaluate_image_accessibility(content_path)
                
            elif content_type == ContentType.VIDEO:
                # Video accessibility (captions, audio description potential)
                accessibility_metrics = await self._evaluate_video_accessibility(content_path)
                
            wcag_level = "AAA" if accessibility_metrics["score"] > 0.9 else \
                        "AA" if accessibility_metrics["score"] > 0.7 else \
                        "A" if accessibility_metrics["score"] > 0.5 else "Below A"
                        
            accessibility_metrics["wcag_compliance"] = wcag_level
            accessibility_metrics["improvements_needed"] = accessibility_metrics["score"] < 0.8
            
            return accessibility_metrics
            
        except Exception as e:
            self.logger.error(f"Accessibility evaluation failed: {str(e)}")
            return {"score": 0.6, "wcag_compliance": "A"}

    async def _check_accessibility_readability(self, text_content: str) -> float:
        """Check readability for accessibility"""



        try:
            # Simple readability metrics
            sentences = text_content.count('.') + text_content.count('!') + text_content.count('?')
            words = len(text_content.split())
            
            if sentences == 0:
                return 0.5
                
            avg_sentence_length = words / sentences
            
            # Score based on sentence length (shorter is more accessible)
            if avg_sentence_length <= 15:
                return 1.0
            elif avg_sentence_length <= 20:
                return 0.8
            elif avg_sentence_length <= 25:
                return 0.6
            else:
                return 0.4
                
        except Exception:
            return 0.6

    async def _check_accessibility_structure(self, text_content: str) -> float:
        """Check structural accessibility elements"""



        try:
            structure_score = 0.0
            
            # Check for headers (markdown-style)
            if '#' in text_content:
                structure_score += 0.3
                
            # Check for lists
            if ('- ' in text_content or '* ' in text_content or 
                any(f'{i}.' in text_content for i in range(1, 10))):
                structure_score += 0.3
                
            # Check for paragraphs (double newlines)
            if '\n\n' in text_content:
                structure_score += 0.4
                
            return min(1.0, structure_score)
            
        except Exception:
            return 0.5

    async def _evaluate_image_accessibility(self, content_path: str) -> Dict[str, Any]:
        """Evaluate image accessibility"""



        try:
            return {
                "score": 0.7,  # Placeholder - would analyze contrast, text, etc.
                "has_alt_text_potential": True,
                "sufficient_contrast": True,
                "text_readable": True
            }
        except Exception:
            return {"score": 0.5}

    async def _evaluate_video_accessibility(self, content_path: str) -> Dict[str, Any]:
        """Evaluate video accessibility"""



        try:
            return {
                "score": 0.6,  # Placeholder
                "has_captions": False,
                "audio_description_needed": True,
                "visual_content_described": False
            }
        except Exception:
            return {"score": 0.4}

    async def _assess_monetization_potential(
        self,
        content_path: str,
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Assess monetization potential of content"""



        try:
            monetization_factors = {
                "quality_score": 0.0,
                "engagement_potential": 0.0,
                "commercial_viability": 0.0,
                "brand_safety": 0.0,
                "audience_appeal": 0.0
            }
            
            # Quality factor based on content type
            if content_type == ContentType.AUDIO or content_type == ContentType.MUSIC:
                audio_info = await self.content_analyzer.get_audio_info(content_path)
                bitrate = audio_info.get("bitrate", 0)
                monetization_factors["quality_score"] = min(1.0, bitrate / 320000)
                
            elif content_type == ContentType.VIDEO:
                video_info = await self.content_analyzer.get_video_info(content_path)
                resolution = video_info.get("resolution", "")
                if "4K" in resolution or "2160p" in resolution:
                    monetization_factors["quality_score"] = 1.0
                elif "1080p" in resolution:
                    monetization_factors["quality_score"] = 0.9
                elif "720p" in resolution:
                    monetization_factors["quality_score"] = 0.7
                else:
                    monetization_factors["quality_score"] = 0.4
                    
            elif content_type in [ContentType.TEXT, ContentType.BLOG]:
                # Text quality for monetization
                with open(content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                word_count = len(text_content.split())
                
                # Optimal length for monetization
                if 1000 <= word_count <= 3000:
                    monetization_factors["quality_score"] = 1.0
                elif 500 <= word_count < 1000:
                    monetization_factors["quality_score"] = 0.8
                else:
                    monetization_factors["quality_score"] = 0.6
                    
            # Engagement potential analysis
            engagement_score = await self._analyze_engagement_potential(content_path, content_type)
            monetization_factors["engagement_potential"] = engagement_score
            
            # Commercial viability
            commercial_score = await self._analyze_commercial_viability(content_path, content_type)
            monetization_factors["commercial_viability"] = commercial_score
            
            # Brand safety affects monetization
            brand_safety = await self._assess_brand_safety(content_path, content_type)
            monetization_factors["brand_safety"] = brand_safety.get("score", 0.5)
            
            # Audience appeal
            audience_score = await self._analyze_audience_appeal(content_path, content_type)
            monetization_factors["audience_appeal"] = audience_score
            
            # Calculate overall monetization score
            overall_score = np.mean(list(monetization_factors.values()))
            
            # Monetization readiness assessment
            if overall_score > 0.8:
                readiness = "High"
            elif overall_score > 0.6:
                readiness = "Medium"
            else:
                readiness = "Low"
            
            return {
                "score": overall_score,
                "factors": monetization_factors,
                "monetization_readiness": readiness,
                "estimated_revenue_potential": "High" if overall_score > 0.8 else "Medium" if overall_score > 0.6 else "Low"
            }
            
        except Exception as e:
            self.logger.error(f"Monetization assessment failed: {str(e)}")
            return {"score": 0.5, "monetization_readiness": "Low"}

    async def _analyze_engagement_potential(self, content_path: str, content_type: ContentType) -> float:
        """Analyze potential for audience engagement"""



        try:
            if content_type in [ContentType.TEXT, ContentType.BLOG, ContentType.SOCIAL_POST]:
                with open(content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                    
                # Check for engagement elements
                engagement_score = 0.0
                
                # Questions increase engagement
                questions = text_content.count('?')
                if questions > 0:
                    engagement_score += min(0.3, questions * 0.1)
                    
                # Calls to action
                cta_phrases = ['comment', 'share', 'like', 'subscribe', 'follow', 'click', 'visit']
                cta_count = sum(1 for phrase in cta_phrases if phrase.lower() in text_content.lower())
                if cta_count > 0:
                    engagement_score += min(0.4, cta_count * 0.1)
                    
                # Emotional language
                emotional_words = ['amazing', 'incredible', 'love', 'hate', 'excited', 'surprised', 'shocked']
                emotional_count = sum(1 for word in emotional_words if word.lower() in text_content.lower())
                if emotional_count > 0:
                    engagement_score += min(0.3, emotional_count * 0.05)
                    
                return min(1.0, engagement_score)
            else:
                return 0.6  # Default for non-text content
                
        except Exception:
            return 0.5

    async def _analyze_commercial_viability(self, content_path: str, content_type: ContentType) -> float:
        """Analyze commercial viability of content"""



        try:
            if content_type in [ContentType.TEXT, ContentType.BLOG]:
                with open(content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                    
                # Commercial keywords
                commercial_terms = [
                    'buy', 'purchase', 'product', 'service', 'business',
                    'solution', 'review', 'comparison', 'best', 'top',
                    'guide', 'how to', 'tutorial', 'tips'
                ]
                
                text_lower = text_content.lower()
                commercial_count = sum(1 for term in commercial_terms if term in text_lower)
                
                # Calculate commercial viability
                word_count = len(text_content.split())
                if word_count > 0:
                    commercial_ratio = commercial_count / word_count
                    return min(1.0, commercial_ratio * 20)
                else:
                    return 0.0
                    
            return 0.5  # Default for other content types
            
        except Exception:
            return 0.4

    async def _analyze_audience_appeal(self, content_path: str, content_type: ContentType) -> float:
        """Analyze general audience appeal"""



        try:
            if content_type in [ContentType.TEXT, ContentType.BLOG, ContentType.SOCIAL_POST]:
                with open(content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                    
                # Trending topics and popular themes
                popular_topics = [
                    'technology', 'ai', 'health', 'fitness', 'travel',
                    'food', 'lifestyle', 'entertainment', 'news',
                    'education', 'career', 'money', 'finance'
                ]
                
                text_lower = text_content.lower()
                topic_matches = sum(1 for topic in popular_topics if topic in text_lower)
                
                # Base appeal score
                appeal_score = min(0.8, topic_matches * 0.2)
                
                # Boost for evergreen content
                evergreen_terms = ['guide', 'tutorial', 'tips', 'how to', 'basics', 'fundamentals']
                evergreen_count = sum(1 for term in evergreen_terms if term in text_lower)
                if evergreen_count > 0:
                    appeal_score += 0.2
                    
                return min(1.0, appeal_score)
            else:
                return 0.6  # Default for media content
                
        except Exception:
            return 0.5

    async def _predict_viral_potential(
        self,
        content_path: str,
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Predict viral potential of content using advanced analysis"""



        try:
            viral_factors = {
                "emotional_impact": 0.0,
                "shareability": 0.0,
                "trending_alignment": 0.0,
                "timing_relevance": 0.0,
                "format_popularity": 0.0,
                "novelty_factor": 0.0
            }
            
            # Format popularity scoring
            format_scores = {
                ContentType.VIDEO: 0.9,
                ContentType.IMAGE: 0.8,
                ContentType.SOCIAL_POST: 0.9,
                ContentType.MUSIC: 0.7,
                ContentType.AUDIO: 0.6,
                ContentType.TEXT: 0.5,
                ContentType.BLOG: 0.4
            }
            
            viral_factors["format_popularity"] = format_scores.get(content_type, 0.5)
            
            # Content-specific viral analysis
            if content_type in [ContentType.TEXT, ContentType.BLOG, ContentType.SOCIAL_POST]:
                with open(content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                    
                # Emotional impact analysis
                viral_factors["emotional_impact"] = await self._analyze_emotional_impact(text_content)
                
                # Shareability analysis
                viral_factors["shareability"] = await self._analyze_shareability(text_content)
                
                # Trending topics alignment
                viral_factors["trending_alignment"] = await self._analyze_trending_alignment(text_content)
                
                # Novelty factor
                viral_factors["novelty_factor"] = await self._analyze_novelty_factor(text_content)
                
            # Timing relevance (simplified - would use real-time trend data)
            viral_factors["timing_relevance"] = 0.7  # Placeholder
            
            # Calculate overall viral potential
            viral_score = np.mean(list(viral_factors.values()))
            
            # Viral probability classification
            if viral_score > 0.8:
                probability = "High"
            elif viral_score > 0.6:
                probability = "Medium"
            else:
                probability = "Low"
                
            return {
                "score": viral_score,
                "factors": viral_factors,
                "viral_probability": probability,
                "estimated_reach": "1M+" if viral_score > 0.8 else "100K+" if viral_score > 0.6 else "10K+"
            }
            
        except Exception as e:
            self.logger.error(f"Viral potential prediction failed: {str(e)}")
            return {"score": 0.5, "viral_probability": "Low"}

    async def _analyze_emotional_impact(self, text_content: str) -> float:
        """Analyze emotional impact of content for viral potential"""



        try:
            # Strong emotional words that drive sharing
            high_emotion_words = [
                'amazing', 'incredible', 'shocking', 'unbelievable',
                'outrageous', 'hilarious', 'heartwarming', 'inspiring',
                'devastating', 'mind-blowing', 'revolutionary', 'breakthrough'
            ]
            
            medium_emotion_words = [
                'great', 'good', 'bad', 'interesting', 'cool',
                'nice', 'wonderful', 'terrible', 'awesome', 'fantastic'
            ]
            
            text_lower = text_content.lower()
            
            high_count = sum(1 for word in high_emotion_words if word in text_lower)
            medium_count = sum(1 for word in medium_emotion_words if word in text_lower)
            
            # Calculate emotional impact score
            total_words = len(text_content.split())
            if total_words > 0:
                emotional_density = (high_count * 2 + medium_count) / total_words
                return min(1.0, emotional_density * 10)
            else:
                return 0.0
                
        except Exception:
            return 0.3

    async def _analyze_shareability(self, text_content: str) -> float:
        """Analyze how shareable content is"""



        try:
            shareability_score = 0.0
            
            # Social sharing indicators
            social_words = ['share', 'tell', 'friends', 'everyone', 'must see', 'check this out']
            social_count = sum(1 for word in social_words if word.lower() in text_content.lower())
            
            # Questions that prompt discussion
            question_count = text_content.count('?')
            
            # Controversial or debate-worthy content
            debate_words = ['opinion', 'think', 'believe', 'controversial', 'debate', 'discuss']
            debate_count = sum(1 for word in debate_words if word.lower() in text_content.lower())
            
            # Lists and tips (highly shareable)
            list_indicators = ['top', 'best', 'worst', 'tips', 'ways', 'reasons', 'things']
            list_count = sum(1 for word in list_indicators if word.lower() in text_content.lower())
            
            # Calculate shareability
            shareability_score = (
                min(0.3, social_count * 0.1) +
                min(0.3, question_count * 0.05) +
                min(0.2, debate_count * 0.05) +
                min(0.2, list_count * 0.05)
            )
            
            return min(1.0, shareability_score)
            
        except Exception:
            return 0.4

    async def _analyze_trending_alignment(self, text_content: str) -> float:
        """Analyze alignment with trending topics"""



        try:
            # Current trending topics (simplified - would use real API data)
            trending_topics = [
                'artificial intelligence', 'ai', 'machine learning',
                'sustainability', 'climate change', 'renewable energy',
                'cryptocurrency', 'blockchain', 'web3', 'nft',
                'remote work', 'digital nomad', 'work from home',
                'mental health', 'wellness', 'self care',
                'social media', 'influencer', 'content creator',
                'startup', 'entrepreneurship', 'business',
                'technology', 'innovation', 'future'
            ]
            
            text_lower = text_content.lower()
            trend_matches = sum(1 for topic in trending_topics if topic in text_lower)
            
            # Score based on trend alignment
            if trend_matches >= 3:
                return 1.0
            elif trend_matches >= 2:
                return 0.8
            elif trend_matches >= 1:
                return 0.6
            else:
                return 0.3
                
        except Exception:
            return 0.4

    async def _analyze_novelty_factor(self, text_content: str) -> float:
        """Analyze novelty and uniqueness factor"""



        try:
            novelty_indicators = [
                'new', 'first time', 'never before', 'breakthrough',
                'discovery', 'revealed', 'secret', 'hidden',
                'exclusive', 'leaked', 'insider', 'behind the scenes'
            ]
            
            text_lower = text_content.lower()
            novelty_count = sum(1 for indicator in novelty_indicators if indicator in text_lower)
            
            # Calculate novelty score
            if novelty_count >= 3:
                return 1.0
            elif novelty_count >= 2:
                return 0.8
            elif novelty_count >= 1:
                return 0.6
            else:
                return 0.4
                
        except Exception:
            return 0.5

    # Additional helper methods for comprehensive analysis
    async def _analyze_content_relevance(
        self,
        content_path: str,
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze content relevance and trends alignment"""



        try:
            relevance_metrics = {
                "trend_alignment": 0.0,
                "seasonal_relevance": 0.0,
                "audience_interest": 0.0,
                "topic_popularity": 0.0
            }
            
            # Basic trend analysis
            if content_type in [ContentType.TEXT, ContentType.BLOG, ContentType.SOCIAL_POST]:
                with open(content_path, 'r', encoding='utf-8') as f:
                    text_content = f.read()
                    
                # Check for trending topics
                trending_topics = [
                    'artificial intelligence', 'ai', 'machine learning',
                    'sustainability', 'climate change', 'renewable',
                    'cryptocurrency', 'blockchain', 'web3',
                    'remote work', 'digital transformation',
                    'mental health', 'wellness', 'self-care'
                ]
                
                text_lower = text_content.lower()
                trend_matches = sum(text_lower.count(topic) for topic in trending_topics)
                
                word_count = len(text_content.split())
                if word_count > 0:
                    relevance_metrics["trend_alignment"] = min(1.0, trend_matches / word_count * 10)
                    
            # Overall relevance score
            overall_relevance = np.mean(list(relevance_metrics.values()))
            
            return {
                "score": overall_relevance,
                "metrics": relevance_metrics,
                "relevance_level": "High" if overall_relevance > 0.7 else 
                                "Medium" if overall_relevance > 0.4 else "Low"
            }
            
        except Exception:
            return {"score": 0.5, "relevance_level": "Medium"}

    async def _check_accessibility_compliance(
        self,
        content_path: str
    ) -> float:
        """Check accessibility compliance score"""



        try:
            # Basic accessibility score calculation
            # Would implement WCAG 2.1 guidelines in production
            return 0.7  # Placeholder score
            
        except Exception:
            return 0.6

    # Audio analysis helper methods
    async def _detect_blocking_artifacts(self, frame: np.ndarray) -> float:
        """Detect blocking artifacts in video frame"""



        try:
            # Simplified blocking artifact detection
            # Would use more sophisticated algorithms in production
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) if len(frame.shape) == 3 else frame
            
            # Use Sobel operator to detect edges (blocking creates artificial edges)
            sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            
            # Calculate gradient magnitude
            gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            
            # High gradient values at block boundaries indicate artifacts
            avg_gradient = np.mean(gradient_magnitude)
            
            # Normalize and invert (high gradient = more artifacts = lower score)
            artifact_score = max(0, 1.0 - avg_gradient / 255.0 * 5)
            
            return float(artifact_score)
            
        except Exception:
            return 0.7

    async def _detect_ringing_artifacts(self, frame: np.ndarray) -> float:
        """Detect ringing artifacts in video frame"""



        try:
            # Ringing artifacts appear as oscillations near edges
            # Use Laplacian to detect high-frequency oscillations
            laplacian = cv2.Laplacian(frame, cv2.CV_64F)
            
            # Calculate variance (high variance indicates ringing)
            variance = np.var(laplacian)
            
            # Normalize and invert
            ringing_score = max(0, 1.0 - variance / 10000.0)
            
            return float(ringing_score)
            
        except Exception:
            return 0.7

    async def _detect_mosquito_noise(self, frame: np.ndarray) -> float:
        """Detect mosquito noise artifacts"""



        try:
            # Mosquito noise appears as fluctuating noise around edges
            # Use Canny edge detection + noise analysis
            edges = cv2.Canny(frame, 50, 150)
            
            # Dilate edges to create regions around edges
            kernel = np.ones((5,5), np.uint8)
            edge_regions = cv2.dilate(edges, kernel, iterations=1)
            
            # Calculate noise in edge regions
            noise_in_edges = np.std(frame[edge_regions > 0]) if np.any(edge_regions > 0) else 0
            
            # Normalize and invert
            mosquito_score = max(0, 1.0 - noise_in_edges / 50.0)
            
            return float(mosquito_score)
            
        except Exception:
            return 0.7

    async def _detect_compression_blur(self, frame: np.ndarray) -> float:
        """Detect compression-induced blur"""



        try:
            # Use Laplacian variance to measure sharpness
            laplacian_var = cv2.Laplacian(frame, cv2.CV_64F).var()
            
            # Higher variance = sharper image
            # Normalize based on typical values
            if laplacian_var > 1000:
                blur_score = 1.0
            elif laplacian_var > 500:
                blur_score = 0.8
            elif laplacian_var > 100:
                blur_score = 0.6
            else:
                blur_score = 0.3
                
            return float(blur_score)
            
        except Exception:
            return 0.6

    # Advanced image analysis methods
    async def _analyze_rule_of_thirds(self, gray_image: np.ndarray) -> float:
        """Analyze composition using rule of thirds"""



        try:
            height, width = gray_image.shape
            
            # Define rule of thirds grid lines
            third_x1, third_x2 = width // 3, 2 * width // 3
            third_y1, third_y2 = height // 3, 2 * height // 3
            
            # Calculate interest points (using corner detection)
            corners = cv2.goodFeaturesToTrack(
                gray_image, maxCorners=100, qualityLevel=0.01, minDistance=10
            )
            
            if corners is None:
                return 0.5
                
            # Check how many interest points are near rule of thirds intersections
            intersection_points = [
                (third_x1, third_y1), (third_x2, third_y1),
                (third_x1, third_y2), (third_x2, third_y2)
            ]
            
            near_intersections = 0
            threshold = min(width, height) * 0.1  # 10% of image dimension
            
            for corner in corners:
                x, y = corner.ravel()
                for ix, iy in intersection_points:
                    distance = np.sqrt((x - ix)**2 + (y - iy)**2)
                    if distance < threshold:
                        near_intersections += 1
                        break
                        
            # Score based on how well subjects align with rule of thirds
            alignment_score = min(1.0, near_intersections / max(1, len(corners)) * 4)
            
            return float(alignment_score)
            
        except Exception:
            return 0.5

    async def _detect_leading_lines(self, gray_image: np.ndarray) -> float:
        """Detect leading lines in composition"""



        try:
            # Use Hough line detection
            edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is None:
                return 0.3
                
            # Analyze line directions and convergence
            line_count = len(lines)
            
            # Score based on presence of lines (leading lines improve composition)
            if line_count > 20:
                return 0.9
            elif line_count > 10:
                return 0.7
            elif line_count > 5:
                return 0.5
            else:
                return 0.3
                
        except Exception:
            return 0.4

    async def _analyze_visual_balance(self, image: np.ndarray) -> float:
        """Analyze visual balance in the image"""



        try:
            # Convert to grayscale for analysis
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
                
            height, width = gray.shape
            
            # Divide image into quadrants
            mid_x, mid_y = width // 2, height // 2
            
            quadrants = [
                gray[:mid_y, :mid_x],      # Top-left
                gray[:mid_y, mid_x:],      # Top-right
                gray[mid_y:, :mid_x],      # Bottom-left
                gray[mid_y:, mid_x:]       # Bottom-right
            ]
            
            # Calculate average intensity for each quadrant
            quad_intensities = [np.mean(quad) for quad in quadrants]
            
            # Calculate balance (lower variance = better balance)
            intensity_variance = np.var(quad_intensities)
            
            # Normalize and invert (lower variance = higher score)
            balance_score = max(0, 1.0 - intensity_variance / 10000.0)
            
            return float(balance_score)
            
        except Exception:
            return 0.6

    async def _analyze_focus_quality(self, gray_image: np.ndarray) -> float:
        """Analyze focus and depth of field quality"""



        try:
            # Use Laplacian variance to measure overall sharpness
            laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
            
            # Use Tenengrad operator for additional focus analysis
            sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            tenengrad = np.mean(sobel_x**2 + sobel_y**2)
            
            # Combine metrics
            focus_score = (laplacian_var / 2000.0 + tenengrad / 10000.0) / 2
            
            return float(min(1.0, focus_score))
            
        except Exception:
            return 0.5

    async def _analyze_subject_prominence(self, image: np.ndarray) -> float:
        """Analyze how prominent the main subject is"""



        try:
            # Use edge detection and contour analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return 0.3
                
            # Find the largest contour (assumed to be main subject)
            largest_contour = max(contours, key=cv2.contourArea)
            subject_area = cv2.contourArea(largest_contour)
            
            # Calculate subject area relative to image
            image_area = gray.shape[0] * gray.shape[1]
            area_ratio = subject_area / image_area
            
            # Optimal ratio is around 20-40% of image
            if 0.2 <= area_ratio <= 0.4:
                prominence_score = 1.0
            elif 0.1 <= area_ratio < 0.2 or 0.4 < area_ratio <= 0.6:
                prominence_score = 0.8
            else:
                prominence_score = 0.5
                
            return float(prominence_score)
            
        except Exception:
            return 0.5

    async def _analyze_golden_ratio(self, gray_image: np.ndarray) -> float:
        """Analyze composition using golden ratio spiral"""



        try:
            height, width = gray_image.shape
            
            # Golden ratio point (approximately)
            golden_x = int(width * 0.618)
            golden_y = int(height * 0.618)
            
            # Check for interest points near golden ratio position
            corners = cv2.goodFeaturesToTrack(
                gray_image, maxCorners=50, qualityLevel=0.01, minDistance=10
            )
            
            if corners is None:
                return 0.4
                
            # Find corners near golden ratio point
            threshold = min(width, height) * 0.15
            near_golden_ratio = 0
            
            for corner in corners:
                x, y = corner.ravel()
                distance = np.sqrt((x - golden_x)**2 + (y - golden_y)**2)
                if distance < threshold:
                    near_golden_ratio += 1
                    
            # Score based on alignment with golden ratio
            golden_score = min(1.0, near_golden_ratio / max(1, len(corners)) * 5)
            
            return float(golden_score)
            
        except Exception:
            return 0.4

    async def _analyze_negative_space(self, gray_image: np.ndarray) -> float:
        """Analyze negative space utilization"""



        try:
            # Use thresholding to separate subjects from background
            _, binary = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Calculate ratio of negative (background) space
            total_pixels = binary.size
            background_pixels = np.count_nonzero(binary == 0)
            negative_space_ratio = background_pixels / total_pixels
            
            # Optimal negative space is around 30-60%
            if 0.3 <= negative_space_ratio <= 0.6:
                space_score = 1.0
            elif 0.2 <= negative_space_ratio < 0.3 or 0.6 < negative_space_ratio <= 0.7:
                space_score = 0.8
            else:
                space_score = 0.5
                
            return float(space_score)
            
        except Exception:
            return 0.6

    # SEO Analysis Helper Methods
    async def _analyze_keyword_density(self, text_content: str) -> float:
        """Analyze keyword density for SEO optimization"""



        try:
            # Simplified keyword density analysis
            # In production, would use actual target keywords
            words = text_content.lower().split()
            word_count = len(words)
            
            if word_count == 0:
                return 0.0
                
            # Common important keywords (simplified)
            important_keywords = [
                'quality', 'best', 'guide', 'how to', 'tips',
                'professional', 'expert', 'review', 'comparison'
            ]
            
            keyword_occurrences = 0
            for keyword in important_keywords:
                keyword_occurrences += text_content.lower().count(keyword.lower())
                
            # Calculate density (optimal is 1-3%)
            density = keyword_occurrences / word_count
            
            if 0.01 <= density <= 0.03:
                return 1.0
            elif 0.005 <= density < 0.01 or 0.03 < density <= 0.05:
                return 0.8
            else:
                return 0.5
                
        except Exception:
            return 0.6

    async def _analyze_heading_structure(self, text_content: str) -> float:
        """Analyze heading structure for SEO"""



        try:
            # Count different heading levels (markdown style)
            h1_count = text_content.count('\n# ')
            h2_count = text_content.count('\n## ')
            h3_count = text_content.count('\n### ')
            
            # Ideal structure: 1 H1, multiple H2s, some H3s
            structure_score = 0.0
            
            # H1 scoring (should have exactly 1)
            if h1_count == 1:
                structure_score += 0.4
            elif h1_count == 0:
                structure_score += 0.2  # Might be using different format
            
            # H2 scoring (should have several)
            if 2 <= h2_count <= 6:
                structure_score += 0.4
            elif h2_count > 0:
                structure_score += 0.3
                
            # H3 scoring (optional but good for long content)
            if h3_count > 0:
                structure_score += 0.2
                
            return float(structure_score)
            
        except Exception:
            return 0.5

    async def _analyze_link_structure(self, text_content: str) -> float:
        """Analyze internal/external link structure"""



        try:
            # Count markdown links
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            import re
            links = re.findall(link_pattern, text_content)
            
            if not links:
                return 0.3  # Some content doesn't need links
                
            # Analyze link types (simplified)
            internal_links = 0
            external_links = 0
            
            for _, url in links:
                if url.startswith('http'):
                    external_links += 1
                else:
                    internal_links += 1
                    
            # Good balance of internal and external links
            total_links = len(links)
            if total_links > 0:
                if internal_links > 0 and external_links > 0:
                    return 1.0
                elif total_links >= 3:
                    return 0.8
                else:
                    return 0.6
            else:
                return 0.5
                
        except Exception:
            return 0.5

    async def _analyze_meta_description_potential(self, text_content: str) -> float:
        """Analyze potential for good meta description"""



        try:
            # Use first paragraph or first few sentences
            sentences = text_content.split('.')
            if not sentences:
                return 0.0
                
            first_paragraph = sentences[0].strip()
            
            # Optimal meta description length: 150-160 characters
            length = len(first_paragraph)
            
            if 140 <= length <= 160:
                return 1.0
            elif 120 <= length < 140 or 160 < length <= 180:
                return 0.8
            elif 100 <= length < 120 or 180 < length <= 200:
                return 0.6
            else:
                return 0.4
                
        except Exception:
            return 0.5

    async def _calculate_seo_readability(self, text_content: str) -> float:
        """Calculate readability score for SEO"""



        try:
            # Simplified Flesch Reading Ease calculation
            sentences = len([s for s in text_content.split('.') if s.strip()])
            words = len(text_content.split())
            syllables = sum(self._count_syllables(word) for word in text_content.split())
            
            if sentences == 0 or words == 0:
                return 0.0
                
            # Flesch Reading Ease formula
            avg_sentence_length = words / sentences
            avg_syllables_per_word = syllables / words
            
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            
            # Convert to 0-1 scale (60-70 is good for SEO)
            if 60 <= flesch_score <= 70:
                return 1.0
            elif 50 <= flesch_score < 60 or 70 < flesch_score <= 80:
                return 0.8
            elif 40 <= flesch_score < 50 or 80 < flesch_score <= 90:
                return 0.6
            else:
                return 0.4
                
        except Exception:
            return 0.6

    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified)"""



        try:
            word = word.lower()
            vowels = 'aeiouy'
            syllables = 0
            prev_char_was_vowel = False
            
            for char in word:
                if char in vowels:
                    if not prev_char_was_vowel:
                        syllables += 1
                    prev_char_was_vowel = True
                else:
                    prev_char_was_vowel = False
                    
            # Handle silent 'e'
            if word.endswith('e') and syllables > 1:
                syllables -= 1
                
            return max(1, syllables)
            
        except Exception:
            return 1

    async def _analyze_semantic_richness(self, text_content: str) -> float:
        """Analyze semantic richness of content"""



        try:
            words = text_content.lower().split()
            unique_words = set(words)
            
            if len(words) == 0:
                return 0.0
                
            # Lexical diversity (unique words / total words)
            lexical_diversity = len(unique_words) / len(words)
            
            # Good range is 0.4-0.7 for semantic richness
            if 0.4 <= lexical_diversity <= 0.7:
                return 1.0
            elif 0.3 <= lexical_diversity < 0.4 or 0.7 < lexical_diversity <= 0.8:
                return 0.8
            else:
                return 0.6
                
        except Exception:
            return 0.6

    async def _analyze_content_freshness(self, text_content: str) -> float:
        """Analyze content freshness indicators"""



        try:
            # Look for freshness indicators
            fresh_terms = [
                'new', 'latest', 'recent', 'updated', 'current',
                '2024', '2023', 'now', 'today', 'modern'
            ]
            
            text_lower = text_content.lower()
            freshness_count = sum(1 for term in fresh_terms if term in text_lower)
            
            # Score based on freshness indicators
            word_count = len(text_content.split())
            if word_count > 0:
                freshness_ratio = freshness_count / word_count
                return min(1.0, freshness_ratio * 20)
            else:
                return 0.0
                
        except Exception:
            return 0.5

    async def _analyze_schema_potential(self, text_content: str) -> float:
        """Analyze potential for schema markup"""



        try:
            # Look for structured data indicators
            schema_indicators = [
                'review', 'rating', 'price', 'product', 'service',
                'recipe', 'event', 'person', 'organization',
                'article', 'faq', 'how to', 'guide'
            ]
            
            text_lower = text_content.lower()
            schema_matches = sum(1 for indicator in schema_indicators if indicator in text_lower)
            
            # Score based on schema potential
            if schema_matches >= 3:
                return 1.0
            elif schema_matches >= 2:
                return 0.8
            elif schema_matches >= 1:
                return 0.6
            else:
                return 0.4
                
        except Exception:
            return 0.5
