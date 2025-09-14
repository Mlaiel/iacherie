"""🔍 Content Quality Monitoring - IA Influencer Agent Platform
==============================================================

Real-time content quality monitoring system with AI-powered quality assessment,
technical analysis, and optimization recommendations for all content formats.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Business Logic Integration:
Content Upload → Quality Analysis → AI Enhancement → Quality Monitoring → Optimization Recommendations
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from decimal import Decimal
import json
from collections import defaultdict
import statistics
import hashlib

logger = logging.getLogger(__name__)


class QualityDimension(Enum):
    """Quality dimensions for content assessment"""
    TECHNICAL_QUALITY = "technical_quality"
    AESTHETIC_QUALITY = "aesthetic_quality"
    CONTENT_RELEVANCE = "content_relevance"
    ENGAGEMENT_POTENTIAL = "engagement_potential"
    SEO_OPTIMIZATION = "seo_optimization"
    ACCESSIBILITY = "accessibility"
    BRAND_CONSISTENCY = "brand_consistency"
    ORIGINALITY = "originality"


class QualityLevel(Enum):
    """Quality levels"""
    EXCEPTIONAL = "exceptional"  # 90-100%
    HIGH = "high"               # 70-89%
    MEDIUM = "medium"           # 50-69%
    LOW = "low"                 # 30-49%
    POOR = "poor"               # 0-29%


class ContentFormat(Enum):
    """Content formats for quality monitoring"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    VOICE = "voice"
    AVATAR = "avatar"
    PODCAST = "podcast"
    LIVE_STREAM = "live_stream"


class QualityIssueType(Enum):
    """Types of quality issues"""
    TECHNICAL_ISSUE = "technical_issue"
    CONTENT_ISSUE = "content_issue"
    OPTIMIZATION_ISSUE = "optimization_issue"
    COMPLIANCE_ISSUE = "compliance_issue"
    ACCESSIBILITY_ISSUE = "accessibility_issue"


@dataclass
class QualityMetrics:
    """Comprehensive quality metrics for content"""
    content_id: str
    content_format: ContentFormat
    
    # Overall quality scores (0-1)
    overall_quality_score: float = 0.0
    technical_quality_score: float = 0.0
    aesthetic_quality_score: float = 0.0
    content_relevance_score: float = 0.0
    engagement_potential_score: float = 0.0
    
    # Dimension-specific scores
    quality_dimensions: Dict[QualityDimension, float] = field(default_factory=dict)
    
    # Technical specifications
    technical_specs: Dict[str, Any] = field(default_factory=dict)
    
    # Quality issues detected
    quality_issues: List[Dict[str, Any]] = field(default_factory=list)
    
    # AI enhancement metrics
    ai_enhancement_applied: bool = False
    ai_improvement_score: float = 0.0
    pre_enhancement_score: Optional[float] = None
    ai_optimization_level: float = 0.0
    
    # Performance correlation
    quality_performance_correlation: float = 0.0
    predicted_engagement: float = 0.0
    
    # Optimization recommendations
    optimization_recommendations: List[str] = field(default_factory=list)
    priority_improvements: List[str] = field(default_factory=list)
    
    # Metadata
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    quality_level: QualityLevel = QualityLevel.MEDIUM
    quality_trend: str = "stable"  # improving, declining, stable
    
    # Compliance and guidelines
    platform_compliance: Dict[str, bool] = field(default_factory=dict)
    content_guidelines_score: float = 0.0
    copyright_compliance: bool = True


@dataclass
class QualityAnalysisResult:
    """Result of comprehensive quality analysis"""
    content_id: str
    analysis_id: str
    
    # Quality assessment
    quality_metrics: QualityMetrics
    
    # Detailed analysis results
    format_specific_analysis: Dict[str, Any] = field(default_factory=dict)
    ai_analysis_results: Dict[str, Any] = field(default_factory=dict)
    
    # Comparison data
    peer_comparison: Dict[str, Any] = field(default_factory=dict)
    historical_comparison: Dict[str, Any] = field(default_factory=dict)
    
    # Recommendations
    immediate_actions: List[str] = field(default_factory=list)
    long_term_improvements: List[str] = field(default_factory=list)
    
    # Processing metadata
    analysis_duration_ms: int = 0
    analysis_confidence: float = 0.0
    analysis_completeness: float = 0.0


class ContentQualityMonitor:
    """
    Advanced Content Quality Monitoring System
    
    Provides real-time quality assessment, monitoring, and optimization
    recommendations for all content formats with AI-powered analysis.
    """
    
    def __init__(self) -> None:
        self.quality_metrics_cache: Dict[str, QualityMetrics] = {}
        self.analysis_history: Dict[str, List[QualityAnalysisResult]] = defaultdict(list)
        self.quality_benchmarks: Dict[ContentFormat, Dict[str, float]] = defaultdict(dict)
        
        # Quality monitoring configuration
        self.monitoring_config = {
            "real_time_threshold": 300,  # 5 minutes for real-time monitoring
            "quality_alert_threshold": 0.5,  # Alert if quality drops below 50%
            "analysis_timeout_seconds": 30,
            "min_confidence_threshold": 0.7,
            "enhancement_threshold": 0.6  # Apply AI enhancement if quality < 60%
        }
        
        # Format-specific quality criteria
        self.format_quality_criteria = self._initialize_format_criteria()
        
        # Quality issue detection patterns
        self.issue_detection_patterns = self._initialize_issue_patterns()
        
        logger.info("🔍 Content Quality Monitor initialized")
    
    def _initialize_format_criteria(self) -> Dict[ContentFormat, Dict[str, Any]]:
        """Initialize format-specific quality criteria"""
        return {
            ContentFormat.AUDIO: {
                "technical_criteria": {
                    "min_bitrate": 128,  # kbps
                    "max_distortion": 0.1,
                    "min_dynamic_range": 40,  # dB
                    "optimal_loudness": -23  # LUFS
                },
                "content_criteria": {
                    "min_duration": 30,  # seconds
                    "max_silence_ratio": 0.1,
                    "speech_clarity_threshold": 0.8,
                    "music_quality_threshold": 0.7
                }
            },
            ContentFormat.VIDEO: {
                "technical_criteria": {
                    "min_resolution": "720p",
                    "min_fps": 24,
                    "max_compression_artifacts": 0.1,
                    "min_brightness": 20,
                    "max_shake_level": 0.2
                },
                "content_criteria": {
                    "min_duration": 15,  # seconds
                    "visual_appeal_threshold": 0.7,
                    "narrative_coherence": 0.6,
                    "editing_quality": 0.7
                }
            },
            ContentFormat.IMAGE: {
                "technical_criteria": {
                    "min_resolution": 1080,  # pixels (shortest side)
                    "max_noise_level": 0.1,
                    "min_sharpness": 0.7,
                    "optimal_contrast": 0.6
                },
                "content_criteria": {
                    "composition_score": 0.6,
                    "color_harmony": 0.6,
                    "visual_impact": 0.7,
                    "subject_clarity": 0.8
                }
            },
            ContentFormat.TEXT: {
                "technical_criteria": {
                    "min_readability_score": 60,  # Flesch reading ease
                    "max_grammatical_errors": 2,  # per 100 words
                    "min_word_count": 100,
                    "optimal_paragraph_length": 150  # words
                },
                "content_criteria": {
                    "content_depth": 0.6,
                    "originality_score": 0.7,
                    "relevance_score": 0.8,
                    "engagement_potential": 0.6
                }
            }
        }
    
    def _initialize_issue_patterns(self) -> Dict[QualityIssueType, List[str]]:
        """Initialize quality issue detection patterns"""
        return {
            QualityIssueType.TECHNICAL_ISSUE: [
                "low_resolution", "poor_audio_quality", "compression_artifacts",
                "color_issues", "exposure_problems", "noise_issues"
            ],
            QualityIssueType.CONTENT_ISSUE: [
                "poor_composition", "lack_of_focus", "irrelevant_content",
                "poor_narrative", "insufficient_depth", "unclear_message"
            ],
            QualityIssueType.OPTIMIZATION_ISSUE: [
                "missing_keywords", "poor_seo", "suboptimal_format",
                "inefficient_compression", "missing_metadata", "poor_tagging"
            ],
            QualityIssueType.COMPLIANCE_ISSUE: [
                "copyright_violation", "platform_guideline_violation",
                "content_policy_breach", "inappropriate_content"
            ],
            QualityIssueType.ACCESSIBILITY_ISSUE: [
                "missing_alt_text", "no_captions", "poor_contrast",
                "missing_transcripts", "audio_only_content"
            ]
        }
    
    async def analyze_content_quality(
        self,
        content_id: str,
        content_format: ContentFormat,
        content_data: Dict[str, Any],
        detailed_analysis: bool = True
    ) -> QualityAnalysisResult:
        """Perform comprehensive content quality analysis"""
        start_time = datetime.now()
        analysis_id = hashlib.md5(f"{content_id}_{start_time.isoformat()}".encode()).hexdigest()[:16]
        
        try:
            # Initialize quality metrics
            quality_metrics = QualityMetrics(
                content_id=content_id,
                content_format=content_format
            )
            
            # Perform format-specific analysis
            format_analysis = await self._analyze_format_specific_quality(
                content_format, content_data
            )
            
            # Calculate technical quality score
            quality_metrics.technical_quality_score = await self._calculate_technical_quality(
                content_format, content_data, format_analysis
            )
            
            # Calculate aesthetic quality score
            quality_metrics.aesthetic_quality_score = await self._calculate_aesthetic_quality(
                content_format, content_data, format_analysis
            )
            
            # Calculate content relevance score
            quality_metrics.content_relevance_score = await self._calculate_content_relevance(
                content_format, content_data
            )
            
            # Calculate engagement potential score
            quality_metrics.engagement_potential_score = await self._calculate_engagement_potential(
                content_format, content_data, quality_metrics
            )
            
            # Calculate dimension-specific scores
            quality_metrics.quality_dimensions = await self._calculate_quality_dimensions(
                content_format, content_data, quality_metrics
            )
            
            # Calculate overall quality score
            quality_metrics.overall_quality_score = await self._calculate_overall_quality(quality_metrics)
            
            # Determine quality level
            quality_metrics.quality_level = self._determine_quality_level(quality_metrics.overall_quality_score)
            
            # Detect quality issues
            quality_metrics.quality_issues = await self._detect_quality_issues(
                content_format, content_data, quality_metrics
            )
            
            # Check platform compliance
            quality_metrics.platform_compliance = await self._check_platform_compliance(
                content_format, content_data
            )
            
            # Generate optimization recommendations
            quality_metrics.optimization_recommendations = await self._generate_optimization_recommendations(
                quality_metrics, format_analysis
            )
            
            # Prioritize improvements
            quality_metrics.priority_improvements = await self._prioritize_improvements(quality_metrics)
            
            # Check if AI enhancement is needed
            if quality_metrics.overall_quality_score < self.monitoring_config["enhancement_threshold"]:
                enhancement_results = await self._suggest_ai_enhancement(quality_metrics)
                quality_metrics.ai_improvement_score = enhancement_results.get("potential_improvement", 0.0)
            
            # Predict engagement based on quality
            quality_metrics.predicted_engagement = await self._predict_engagement_from_quality(quality_metrics)
            
            # Store metrics in cache
            self.quality_metrics_cache[content_id] = quality_metrics
            
            # Create analysis result
            analysis_result = QualityAnalysisResult(
                content_id=content_id,
                analysis_id=analysis_id,
                quality_metrics=quality_metrics,
                format_specific_analysis=format_analysis,
                analysis_duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                analysis_confidence=0.85,  # Placeholder confidence score
                analysis_completeness=1.0 if detailed_analysis else 0.8
            )
            
            # Add historical comparison if available
            if content_id in self.analysis_history:
                analysis_result.historical_comparison = await self._compare_with_history(
                    content_id, quality_metrics
                )
            
            # Add peer comparison
            analysis_result.peer_comparison = await self._compare_with_peers(
                content_format, quality_metrics
            )
            
            # Generate immediate actions
            analysis_result.immediate_actions = await self._generate_immediate_actions(quality_metrics)
            
            # Generate long-term improvements
            analysis_result.long_term_improvements = await self._generate_long_term_improvements(quality_metrics)
            
            # Store in history
            self.analysis_history[content_id].append(analysis_result)
            
            logger.info(f"✅ Quality analysis completed for {content_id}: {quality_metrics.overall_quality_score:.2f}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze content quality: {e}")
            # Return minimal analysis result with error
            return QualityAnalysisResult(
                content_id=content_id,
                analysis_id=analysis_id,
                quality_metrics=QualityMetrics(content_id=content_id, content_format=content_format),
                analysis_duration_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
    
    async def _analyze_format_specific_quality(
        self,
        content_format: ContentFormat,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform format-specific quality analysis"""
        analysis = {"format": content_format.value}
        
        try:
            if content_format == ContentFormat.AUDIO:
                analysis.update(await self._analyze_audio_quality(content_data))
            elif content_format == ContentFormat.VIDEO:
                analysis.update(await self._analyze_video_quality(content_data))
            elif content_format == ContentFormat.IMAGE:
                analysis.update(await self._analyze_image_quality(content_data))
            elif content_format == ContentFormat.TEXT:
                analysis.update(await self._analyze_text_quality(content_data))
            elif content_format == ContentFormat.VOICE:
                analysis.update(await self._analyze_voice_quality(content_data))
            
        except Exception as e:
            logger.error(f"❌ Failed format-specific analysis: {e}")
            analysis["error"] = str(e)
        
        return analysis
    
    async def _analyze_audio_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audio content quality"""
        analysis = {
            "bitrate": content_data.get("bitrate", 128),
            "sample_rate": content_data.get("sample_rate", 44100),
            "duration": content_data.get("duration", 0),
            "loudness": content_data.get("loudness", -23),
            "dynamic_range": content_data.get("dynamic_range", 40)
        }
        
        # Calculate audio quality scores
        criteria = self.format_quality_criteria[ContentFormat.AUDIO]["technical_criteria"]
        
        bitrate_score = min(1.0, analysis["bitrate"] / criteria["min_bitrate"])
        loudness_score = 1.0 - abs(analysis["loudness"] - criteria["optimal_loudness"]) / 20
        dynamic_range_score = min(1.0, analysis["dynamic_range"] / criteria["min_dynamic_range"])
        
        analysis["quality_scores"] = {
            "bitrate_score": bitrate_score,
            "loudness_score": max(0.0, loudness_score),
            "dynamic_range_score": dynamic_range_score
        }
        
        return analysis
    
    async def _analyze_video_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze video content quality"""
        analysis = {
            "resolution": content_data.get("resolution", "720p"),
            "fps": content_data.get("fps", 24),
            "duration": content_data.get("duration", 0),
            "bitrate": content_data.get("bitrate", 2000),
            "aspect_ratio": content_data.get("aspect_ratio", "16:9")
        }
        
        # Calculate video quality scores
        resolution_score = 1.0 if analysis["resolution"] >= "720p" else 0.7
        fps_score = min(1.0, analysis["fps"] / 30)
        bitrate_score = min(1.0, analysis["bitrate"] / 2000)
        
        analysis["quality_scores"] = {
            "resolution_score": resolution_score,
            "fps_score": fps_score,
            "bitrate_score": bitrate_score
        }
        
        return analysis
    
    async def _analyze_image_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image content quality"""
        analysis = {
            "resolution": content_data.get("resolution", [1920, 1080]),
            "file_size": content_data.get("file_size", 0),
            "format": content_data.get("format", "JPEG"),
            "color_depth": content_data.get("color_depth", 24),
            "aspect_ratio": content_data.get("aspect_ratio", 1.78)
        }
        
        # Calculate image quality scores
        min_dimension = min(analysis["resolution"]) if isinstance(analysis["resolution"], list) else 1080
        resolution_score = min(1.0, min_dimension / 1080)
        
        # Format scoring (PNG > JPEG > others)
        format_scores = {"PNG": 1.0, "JPEG": 0.9, "WebP": 0.95}
        format_score = format_scores.get(analysis["format"], 0.8)
        
        color_depth_score = min(1.0, analysis["color_depth"] / 24)
        
        analysis["quality_scores"] = {
            "resolution_score": resolution_score,
            "format_score": format_score,
            "color_depth_score": color_depth_score
        }
        
        return analysis
    
    async def _analyze_text_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text content quality"""
        text_content = content_data.get("text", "")
        word_count = len(text_content.split()) if text_content else 0
        
        analysis = {
            "word_count": word_count,
            "character_count": len(text_content),
            "paragraph_count": text_content.count('\n\n') + 1 if text_content else 0,
            "average_sentence_length": word_count / max(1, text_content.count('.'))
        }
        
        # Calculate text quality scores
        criteria = self.format_quality_criteria[ContentFormat.TEXT]["technical_criteria"]
        
        word_count_score = min(1.0, word_count / criteria["min_word_count"])
        readability_score = 0.8  # Placeholder - would use actual readability analysis
        
        analysis["quality_scores"] = {
            "word_count_score": word_count_score,
            "readability_score": readability_score,
            "structure_score": 0.8  # Placeholder
        }
        
        return analysis
    
    async def _analyze_voice_quality(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze voice content quality"""
        # Voice analysis is similar to audio but with speech-specific metrics
        analysis = await self._analyze_audio_quality(content_data)
        
        # Add voice-specific metrics
        analysis.update({
            "speech_clarity": content_data.get("speech_clarity", 0.8),
            "emotion_detection": content_data.get("emotion_score", 0.7),
            "pace_score": content_data.get("pace_score", 0.8),
            "pronunciation_score": content_data.get("pronunciation_score", 0.9)
        })
        
        return analysis
    
    async def _calculate_technical_quality(
        self,
        content_format: ContentFormat,
        content_data: Dict[str, Any],
        format_analysis: Dict[str, Any]
    ) -> float:
        """Calculate technical quality score"""
        try:
            quality_scores = format_analysis.get("quality_scores", {})
            if not quality_scores:
                return 0.7  # Default score
            
            # Average all technical quality scores
            scores = list(quality_scores.values())
            return statistics.mean(scores) if scores else 0.7
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate technical quality: {e}")
            return 0.7
    
    async def _calculate_aesthetic_quality(
        self,
        content_format: ContentFormat,
        content_data: Dict[str, Any],
        format_analysis: Dict[str, Any]
    ) -> float:
        """Calculate aesthetic quality score"""
        try:
            # Aesthetic quality is format-dependent
            if content_format in [ContentFormat.IMAGE, ContentFormat.VIDEO]:
                # Visual aesthetic scoring
                composition_score = content_data.get("composition_score", 0.7)
                color_harmony_score = content_data.get("color_harmony", 0.7)
                visual_appeal_score = content_data.get("visual_appeal", 0.7)
                
                return statistics.mean([composition_score, color_harmony_score, visual_appeal_score])
            
            elif content_format in [ContentFormat.AUDIO, ContentFormat.VOICE, ContentFormat.PODCAST]:
                # Audio aesthetic scoring
                clarity_score = content_data.get("clarity_score", 0.8)
                balance_score = content_data.get("balance_score", 0.8)
                production_quality = content_data.get("production_quality", 0.7)
                
                return statistics.mean([clarity_score, balance_score, production_quality])
            
            elif content_format == ContentFormat.TEXT:
                # Text aesthetic scoring (readability, structure)
                structure_score = content_data.get("structure_score", 0.8)
                flow_score = content_data.get("flow_score", 0.7)
                formatting_score = content_data.get("formatting_score", 0.8)
                
                return statistics.mean([structure_score, flow_score, formatting_score])
            
            else:
                return 0.7  # Default for other formats
                
        except Exception as e:
            logger.error(f"❌ Failed to calculate aesthetic quality: {e}")
            return 0.7
    
    async def _calculate_content_relevance(
        self,
        content_format: ContentFormat,
        content_data: Dict[str, Any]
    ) -> float:
        """Calculate content relevance score"""
        try:
            # Analyze content relevance factors
            topic_relevance = content_data.get("topic_relevance", 0.8)
            target_audience_match = content_data.get("audience_match", 0.7)
            trending_factor = content_data.get("trending_factor", 0.6)
            keyword_relevance = content_data.get("keyword_relevance", 0.7)
            
            # Weight the factors
            relevance_score = (
                topic_relevance * 0.3 +
                target_audience_match * 0.3 +
                trending_factor * 0.2 +
                keyword_relevance * 0.2
            )
            
            return min(1.0, relevance_score)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate content relevance: {e}")
            return 0.7
    
    async def _calculate_engagement_potential(
        self,
        content_format: ContentFormat,
        content_data: Dict[str, Any],
        quality_metrics: QualityMetrics
    ) -> float:
        """Calculate engagement potential score"""
        try:
            # Base engagement potential on various factors
            technical_contribution = quality_metrics.technical_quality_score * 0.3
            aesthetic_contribution = quality_metrics.aesthetic_quality_score * 0.3
            relevance_contribution = quality_metrics.content_relevance_score * 0.2
            
            # Format-specific engagement factors
            format_engagement_factor = 0.2
            if content_format == ContentFormat.VIDEO:
                # Videos typically have higher engagement potential
                format_engagement_factor = min(1.0, content_data.get("duration", 60) / 300) * 0.2  # Optimal around 5 minutes
            elif content_format == ContentFormat.IMAGE:
                # Images with faces or vibrant colors have higher engagement
                visual_impact = content_data.get("visual_impact", 0.7)
                format_engagement_factor = visual_impact * 0.2
            elif content_format == ContentFormat.TEXT:
                # Text engagement depends on readability and structure
                readability = content_data.get("readability_score", 0.7)
                format_engagement_factor = (readability / 100) * 0.2  # Normalize readability score
            
            engagement_potential = (
                technical_contribution +
                aesthetic_contribution +
                relevance_contribution +
                format_engagement_factor
            )
            
            return min(1.0, engagement_potential)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate engagement potential: {e}")
            return 0.7
    
    async def _calculate_quality_dimensions(
        self,
        content_format: ContentFormat,
        content_data: Dict[str, Any],
        quality_metrics: QualityMetrics
    ) -> Dict[QualityDimension, float]:
        """Calculate scores for all quality dimensions"""
        dimensions = {}
        
        try:
            # Technical quality dimension
            dimensions[QualityDimension.TECHNICAL_QUALITY] = quality_metrics.technical_quality_score
            
            # Aesthetic quality dimension
            dimensions[QualityDimension.AESTHETIC_QUALITY] = quality_metrics.aesthetic_quality_score
            
            # Content relevance dimension
            dimensions[QualityDimension.CONTENT_RELEVANCE] = quality_metrics.content_relevance_score
            
            # Engagement potential dimension
            dimensions[QualityDimension.ENGAGEMENT_POTENTIAL] = quality_metrics.engagement_potential_score
            
            # SEO optimization dimension
            dimensions[QualityDimension.SEO_OPTIMIZATION] = content_data.get("seo_score", 0.6)
            
            # Accessibility dimension
            dimensions[QualityDimension.ACCESSIBILITY] = content_data.get("accessibility_score", 0.8)
            
            # Brand consistency dimension
            dimensions[QualityDimension.BRAND_CONSISTENCY] = content_data.get("brand_consistency", 0.8)
            
            # Originality dimension
            dimensions[QualityDimension.ORIGINALITY] = content_data.get("originality_score", 0.7)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate quality dimensions: {e}")
        
        return dimensions
    
    async def _calculate_overall_quality(self, quality_metrics: QualityMetrics) -> float:
        """Calculate overall quality score from all dimensions"""
        try:
            # Weight the main quality components
            weights = {
                "technical": 0.25,
                "aesthetic": 0.25,
                "relevance": 0.25,
                "engagement": 0.25
            }
            
            overall_score = (
                quality_metrics.technical_quality_score * weights["technical"] +
                quality_metrics.aesthetic_quality_score * weights["aesthetic"] +
                quality_metrics.content_relevance_score * weights["relevance"] +
                quality_metrics.engagement_potential_score * weights["engagement"]
            )
            
            return min(1.0, overall_score)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate overall quality: {e}")
            return 0.7
    
    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """Determine quality level from overall score"""
        if overall_score >= 0.9:
            return QualityLevel.EXCEPTIONAL
        elif overall_score >= 0.7:
            return QualityLevel.HIGH
        elif overall_score >= 0.5:
            return QualityLevel.MEDIUM
        elif overall_score >= 0.3:
            return QualityLevel.LOW
        else:
            return QualityLevel.POOR
    
    async def _detect_quality_issues(
        self,
        content_format: ContentFormat,
        content_data: Dict[str, Any],
        quality_metrics: QualityMetrics
    ) -> List[Dict[str, Any]]:
        """Detect quality issues in content"""
        issues = []
        
        try:
            # Check technical quality issues
            if quality_metrics.technical_quality_score < 0.6:
                issues.append({
                    "type": QualityIssueType.TECHNICAL_ISSUE.value,
                    "severity": "high" if quality_metrics.technical_quality_score < 0.4 else "medium",
                    "description": "Technical quality below acceptable threshold",
                    "score": quality_metrics.technical_quality_score
                })
            
            # Check aesthetic quality issues
            if quality_metrics.aesthetic_quality_score < 0.6:
                issues.append({
                    "type": QualityIssueType.CONTENT_ISSUE.value,
                    "severity": "medium",
                    "description": "Aesthetic quality could be improved",
                    "score": quality_metrics.aesthetic_quality_score
                })
            
            # Check optimization issues
            seo_score = quality_metrics.quality_dimensions.get(QualityDimension.SEO_OPTIMIZATION, 0.6)
            if seo_score < 0.5:
                issues.append({
                    "type": QualityIssueType.OPTIMIZATION_ISSUE.value,
                    "severity": "low",
                    "description": "SEO optimization needs improvement",
                    "score": seo_score
                })
            
            # Check accessibility issues
            accessibility_score = quality_metrics.quality_dimensions.get(QualityDimension.ACCESSIBILITY, 0.8)
            if accessibility_score < 0.7:
                issues.append({
                    "type": QualityIssueType.ACCESSIBILITY_ISSUE.value,
                    "severity": "medium",
                    "description": "Accessibility features missing or inadequate",
                    "score": accessibility_score
                })
        
        except Exception as e:
            logger.error(f"❌ Failed to detect quality issues: {e}")
        
        return issues
    
    async def _check_platform_compliance(
        self,
        content_format: ContentFormat,
        content_data: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Check compliance with platform guidelines"""
        compliance = {
            "youtube": True,
            "instagram": True,
            "tiktok": True,
            "facebook": True,
            "twitter": True
        }
        
        try:
            # Check format-specific compliance
            if content_format == ContentFormat.VIDEO:
                duration = content_data.get("duration", 0)
                if duration > 900:  # 15 minutes
                    compliance["instagram"] = False  # Instagram has limits on video length
                
            elif content_format == ContentFormat.AUDIO:
                duration = content_data.get("duration", 0)
                if duration > 600:  # 10 minutes
                    compliance["twitter"] = False  # Twitter has audio length limits
            
            # Check general content compliance (placeholder)
            content_rating = content_data.get("content_rating", "safe")
            if content_rating != "safe":
                for platform in compliance:
                    compliance[platform] = False
        
        except Exception as e:
            logger.error(f"❌ Failed to check platform compliance: {e}")
        
        return compliance
    
    async def _generate_optimization_recommendations(
        self,
        quality_metrics: QualityMetrics,
        format_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        try:
            # Technical optimization recommendations
            if quality_metrics.technical_quality_score < 0.7:
                recommendations.append("Improve technical quality through better recording/capture equipment")
                
                if quality_metrics.content_format == ContentFormat.AUDIO:
                    recommendations.append("Consider audio post-processing to enhance sound quality")
                elif quality_metrics.content_format == ContentFormat.VIDEO:
                    recommendations.append("Optimize video encoding settings for better quality")
                elif quality_metrics.content_format == ContentFormat.IMAGE:
                    recommendations.append("Increase image resolution and reduce compression artifacts")
            
            # Aesthetic optimization recommendations
            if quality_metrics.aesthetic_quality_score < 0.7:
                recommendations.append("Enhance visual/aesthetic appeal through better composition and design")
                
                if quality_metrics.content_format in [ContentFormat.IMAGE, ContentFormat.VIDEO]:
                    recommendations.append("Apply color grading and improve visual composition")
                elif quality_metrics.content_format in [ContentFormat.AUDIO, ContentFormat.VOICE]:
                    recommendations.append("Improve audio mixing and production quality")
            
            # Content relevance recommendations
            if quality_metrics.content_relevance_score < 0.7:
                recommendations.append("Improve content relevance by targeting trending topics and keywords")
                recommendations.append("Better align content with target audience preferences")
            
            # Engagement potential recommendations
            if quality_metrics.engagement_potential_score < 0.7:
                recommendations.append("Add interactive elements to increase engagement potential")
                recommendations.append("Optimize content length and pacing for better audience retention")
            
            # SEO optimization recommendations
            seo_score = quality_metrics.quality_dimensions.get(QualityDimension.SEO_OPTIMIZATION, 0.6)
            if seo_score < 0.7:
                recommendations.append("Optimize titles, descriptions, and tags for better discoverability")
                recommendations.append("Include relevant keywords naturally in content")
            
            # Accessibility recommendations
            accessibility_score = quality_metrics.quality_dimensions.get(QualityDimension.ACCESSIBILITY, 0.8)
            if accessibility_score < 0.8:
                recommendations.append("Add captions, alt text, and other accessibility features")
        
        except Exception as e:
            logger.error(f"❌ Failed to generate optimization recommendations: {e}")
        
        return recommendations
    
    async def _prioritize_improvements(self, quality_metrics: QualityMetrics) -> List[str]:
        """Prioritize improvement areas based on impact and feasibility"""
        improvements = []
        
        try:
            # Priority 1: Critical technical issues
            if quality_metrics.technical_quality_score < 0.5:
                improvements.append("CRITICAL: Fix technical quality issues immediately")
            
            # Priority 2: Major content issues
            if quality_metrics.aesthetic_quality_score < 0.5:
                improvements.append("HIGH: Improve aesthetic quality and visual appeal")
            
            # Priority 3: Optimization opportunities
            if quality_metrics.content_relevance_score < 0.6:
                improvements.append("MEDIUM: Enhance content relevance and targeting")
            
            # Priority 4: Engagement improvements
            if quality_metrics.engagement_potential_score < 0.6:
                improvements.append("MEDIUM: Optimize for better audience engagement")
            
            # Priority 5: SEO and discoverability
            seo_score = quality_metrics.quality_dimensions.get(QualityDimension.SEO_OPTIMIZATION, 0.6)
            if seo_score < 0.6:
                improvements.append("LOW: Improve SEO and discoverability")
        
        except Exception as e:
            logger.error(f"❌ Failed to prioritize improvements: {e}")
        
        return improvements
    
    async def _suggest_ai_enhancement(self, quality_metrics: QualityMetrics) -> Dict[str, Any]:
        """Suggest AI enhancement opportunities"""
        suggestions = {
            "enhancement_needed": True,
            "potential_improvement": 0.0,
            "recommended_enhancements": []
        }
        
        try:
            current_score = quality_metrics.overall_quality_score
            
            # Calculate potential improvement
            if quality_metrics.content_format == ContentFormat.IMAGE:
                # Image AI enhancements
                potential_improvement = min(0.3, (0.8 - current_score))
                suggestions["recommended_enhancements"] = [
                    "AI-powered image upscaling",
                    "Automatic color correction",
                    "Noise reduction"
                ]
            
            elif quality_metrics.content_format == ContentFormat.AUDIO:
                # Audio AI enhancements
                potential_improvement = min(0.25, (0.8 - current_score))
                suggestions["recommended_enhancements"] = [
                    "AI audio enhancement",
                    "Noise reduction",
                    "Dynamic range optimization"
                ]
            
            elif quality_metrics.content_format == ContentFormat.VIDEO:
                # Video AI enhancements
                potential_improvement = min(0.2, (0.8 - current_score))
                suggestions["recommended_enhancements"] = [
                    "AI video stabilization",
                    "Automatic color grading",
                    "Resolution upscaling"
                ]
            
            elif quality_metrics.content_format == ContentFormat.TEXT:
                # Text AI enhancements
                potential_improvement = min(0.15, (0.8 - current_score))
                suggestions["recommended_enhancements"] = [
                    "AI grammar and style correction",
                    "SEO optimization",
                    "Readability improvement"
                ]
            
            else:
                potential_improvement = min(0.1, (0.8 - current_score))
            
            suggestions["potential_improvement"] = potential_improvement
        
        except Exception as e:
            logger.error(f"❌ Failed to suggest AI enhancement: {e}")
        
        return suggestions
    
    async def _predict_engagement_from_quality(self, quality_metrics: QualityMetrics) -> float:
        """Predict engagement rate based on quality metrics"""
        try:
            # Simple correlation model between quality and engagement
            base_engagement = quality_metrics.overall_quality_score * 0.1  # 10% max base engagement
            
            # Boost for exceptional quality
            if quality_metrics.quality_level == QualityLevel.EXCEPTIONAL:
                base_engagement *= 1.5
            elif quality_metrics.quality_level == QualityLevel.HIGH:
                base_engagement *= 1.2
            
            # Format-specific adjustments
            format_multipliers = {
                ContentFormat.VIDEO: 1.3,
                ContentFormat.IMAGE: 1.1,
                ContentFormat.AUDIO: 0.9,
                ContentFormat.TEXT: 0.8,
                ContentFormat.VOICE: 0.9
            }
            
            multiplier = format_multipliers.get(quality_metrics.content_format, 1.0)
            predicted_engagement = base_engagement * multiplier
            
            return min(0.2, predicted_engagement)  # Cap at 20% engagement rate
            
        except Exception as e:
            logger.error(f"❌ Failed to predict engagement: {e}")
            return 0.05  # Default 5% engagement rate
    
    async def _compare_with_history(
        self,
        content_id: str,
        current_metrics: QualityMetrics
    ) -> Dict[str, Any]:
        """Compare current quality with historical data"""
        try:
            history = self.analysis_history.get(content_id, [])
            if len(history) < 2:
                return {"trend": "insufficient_data"}
            
            # Get previous quality score
            previous_score = history[-2].quality_metrics.overall_quality_score
            current_score = current_metrics.overall_quality_score
            
            improvement = current_score - previous_score
            
            return {
                "trend": "improving" if improvement > 0.05 else "declining" if improvement < -0.05 else "stable",
                "improvement": improvement,
                "previous_score": previous_score,
                "current_score": current_score
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to compare with history: {e}")
            return {"trend": "unknown"}
    
    async def _compare_with_peers(
        self,
        content_format: ContentFormat,
        quality_metrics: QualityMetrics
    ) -> Dict[str, Any]:
        """Compare quality with peer content of same format"""
        try:
            # Get all content of same format
            peer_scores = [
                metrics.overall_quality_score
                for metrics in self.quality_metrics_cache.values()
                if metrics.content_format == content_format
            ]
            
            if len(peer_scores) < 5:
                return {"comparison": "insufficient_peer_data"}
            
            current_score = quality_metrics.overall_quality_score
            avg_peer_score = statistics.mean(peer_scores)
            
            percentile = len([score for score in peer_scores if score <= current_score]) / len(peer_scores)
            
            return {
                "peer_average": avg_peer_score,
                "current_score": current_score,
                "percentile": percentile,
                "comparison": "above_average" if current_score > avg_peer_score else "below_average"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to compare with peers: {e}")
            return {"comparison": "unknown"}
    
    async def _generate_immediate_actions(self, quality_metrics: QualityMetrics) -> List[str]:
        """Generate immediate actions needed"""
        actions = []
        
        if quality_metrics.overall_quality_score < 0.4:
            actions.append("URGENT: Content quality critically low - consider re-creating or major enhancement")
        
        if quality_metrics.quality_issues:
            high_severity_issues = [issue for issue in quality_metrics.quality_issues if issue.get("severity") == "high"]
            if high_severity_issues:
                actions.append("Fix high-severity quality issues before publishing")
        
        if not quality_metrics.copyright_compliance:
            actions.append("CRITICAL: Resolve copyright compliance issues immediately")
        
        return actions
    
    async def _generate_long_term_improvements(self, quality_metrics: QualityMetrics) -> List[str]:
        """Generate long-term improvement strategies"""
        improvements = []
        
        if quality_metrics.overall_quality_score < 0.7:
            improvements.append("Develop content quality improvement strategy")
            improvements.append("Invest in better tools and training for content creation")
        
        if quality_metrics.ai_optimization_level < 0.5:
            improvements.append("Explore AI-powered content enhancement tools")
        
        improvements.append("Establish quality benchmarks and regular quality audits")
        improvements.append("Create quality guidelines and best practices documentation")
        
        return improvements
    
    async def get_quality_metrics(self, content_id: str) -> Optional[QualityMetrics]:
        """Get quality metrics for specific content"""
        return self.quality_metrics_cache.get(content_id)
    
    async def get_quality_dashboard(self) -> Dict[str, Any]:
        """Get quality monitoring dashboard"""
        try:
            current_time = datetime.now()
            recent_threshold = current_time - timedelta(minutes=self.monitoring_config["real_time_threshold"])
            
            # Get recent content
            recent_metrics = [
                metrics for metrics in self.quality_metrics_cache.values()
                if metrics.analysis_timestamp >= recent_threshold
            ]
            
            if not recent_metrics:
                return {"message": "No recent content to analyze"}
            
            # Calculate dashboard metrics
            avg_quality = statistics.mean(m.overall_quality_score for m in recent_metrics)
            quality_distribution = {level.value: 0 for level in QualityLevel}
            
            for metrics in recent_metrics:
                quality_distribution[metrics.quality_level.value] += 1
            
            # Identify quality alerts
            quality_alerts = [
                {
                    "content_id": m.content_id,
                    "quality_score": m.overall_quality_score,
                    "issues": len(m.quality_issues)
                }
                for m in recent_metrics
                if m.overall_quality_score < self.monitoring_config["quality_alert_threshold"]
            ]
            
            return {
                "timestamp": current_time.isoformat(),
                "total_content_analyzed": len(recent_metrics),
                "average_quality_score": avg_quality,
                "quality_distribution": quality_distribution,
                "quality_alerts": quality_alerts,
                "top_quality_content": max(recent_metrics, key=lambda x: x.overall_quality_score).content_id if recent_metrics else None,
                "improvement_opportunities": sum(len(m.optimization_recommendations) for m in recent_metrics)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate quality dashboard: {e}")
            return {"error": str(e)}


# Global instance for easy access
content_quality_monitor = ContentQualityMonitor()

# Convenience functions
async def analyze_content_quality(content_id: str, content_format: ContentFormat, content_data: Dict[str, Any]) -> QualityAnalysisResult:
    """Analyze content quality - convenience function"""
    return await content_quality_monitor.analyze_content_quality(content_id, content_format, content_data)

async def get_quality_metrics(content_id: str) -> Optional[QualityMetrics]:
    """Get quality metrics - convenience function"""
    return await content_quality_monitor.get_quality_metrics(content_id)

async def get_quality_dashboard() -> Dict[str, Any]:
    """Get quality dashboard - convenience function"""
    return await content_quality_monitor.get_quality_dashboard()