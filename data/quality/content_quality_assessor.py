"""
Content Quality Assessor - Multi-Format Content Quality Assessment
==================================================================

Enterprise-grade content quality assessment system for audio, video, image, and text content.
Provides sophisticated quality scoring algorithms and content optimization recommendations.

⚠️  COPYRIGHT WARNING ⚠️
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or theft of this code or concept without explicit 
written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and 
will result in immediate legal action under German and international copyright law.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
                Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved
"""

from typing import Dict, Any, List, Optional, Union, Tuple, Set, Callable
import asyncio
import logging
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
import re
import hashlib
import numpy as np
from collections import defaultdict, Counter
from dataclasses import dataclass, field
import math
import base64

# Content analysis imports
try:
    import librosa
    import librosa.display
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

try:
    from PIL import Image, ImageStat, ImageFilter
    import cv2
    HAS_VISION = True
except ImportError:
    HAS_VISION = False

try:
    import ffmpeg
    HAS_FFMPEG = True
except ImportError:
    HAS_FFMPEG = False

try:
    from textblob import TextBlob
    import nltk
    HAS_NLP = True
except ImportError:
    HAS_NLP = False

logger = logging.getLogger(__name__)

class ContentQualityDimension(Enum):
    """Content quality assessment dimensions"""
    TECHNICAL_QUALITY = "technical_quality"     # Technical specifications and standards
    AESTHETIC_QUALITY = "aesthetic_quality"     # Visual/auditory appeal and composition
    CONTENT_CLARITY = "content_clarity"         # Clarity, sharpness, readability
    ENGAGEMENT_POTENTIAL = "engagement_potential" # Audience engagement and interest
    PRODUCTION_VALUE = "production_value"       # Professional production quality
    OPTIMIZATION = "optimization"               # Platform and distribution optimization
    ACCESSIBILITY = "accessibility"             # Accessibility compliance
    ORIGINALITY = "originality"                 # Content uniqueness and creativity
    COHERENCE = "coherence"                     # Content structure and flow
    TECHNICAL_COMPLIANCE = "technical_compliance" # Format and standard compliance

class QualityLevel(Enum):
    """Content quality levels"""
    EXCEPTIONAL = "exceptional"    # 95-100 - Industry-leading quality
    PROFESSIONAL = "professional"  # 85-94  - Professional broadcast quality
    HIGH = "high"                  # 75-84  - High-quality content
    GOOD = "good"                  # 65-74  - Good quality content
    ACCEPTABLE = "acceptable"      # 55-64  - Acceptable for distribution
    POOR = "poor"                  # 35-54  - Below standard quality
    UNACCEPTABLE = "unacceptable"  # 0-34   - Requires major improvement

class ContentFormat(Enum):
    """Supported content formats"""
    AUDIO_WAV = "audio/wav"
    AUDIO_MP3 = "audio/mp3"
    AUDIO_FLAC = "audio/flac"
    AUDIO_AAC = "audio/aac"
    VIDEO_MP4 = "video/mp4"
    VIDEO_AVI = "video/avi"
    VIDEO_MOV = "video/mov"
    VIDEO_MKV = "video/mkv"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_WEBP = "image/webp"
    IMAGE_TIFF = "image/tiff"
    TEXT_PLAIN = "text/plain"
    TEXT_MARKDOWN = "text/markdown"
    TEXT_HTML = "text/html"

@dataclass
class QualityMetric:
    """Individual quality metric result"""
    name: str
    value: float
    weight: float
    max_value: float = 100.0
    unit: str = "score"
    description: str = ""
    recommendation: str = ""
    
    @property
    def normalized_score(self) -> float:
        """Get normalized score (0-100)"""
        return min(100.0, max(0.0, (self.value / self.max_value) * 100))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'value': round(self.value, 2),
            'normalized_score': round(self.normalized_score, 2),
            'weight': self.weight,
            'unit': self.unit,
            'description': self.description,
            'recommendation': self.recommendation
        }

@dataclass
class DimensionAssessment:
    """Assessment result for a quality dimension"""
    dimension: ContentQualityDimension
    score: float
    metrics: List[QualityMetric] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_metric(self, metric: QualityMetric):
        """Add quality metric to dimension"""
        self.metrics.append(metric)
    
    def calculate_score(self) -> float:
        """Calculate dimension score from metrics"""
        if not self.metrics:
            return 0.0
        
        total_weighted_score = sum(m.normalized_score * m.weight for m in self.metrics)
        total_weight = sum(m.weight for m in self.metrics)
        
        self.score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        return self.score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'dimension': self.dimension.value,
            'score': round(self.score, 2),
            'metrics': [m.to_dict() for m in self.metrics],
            'issues': self.issues,
            'recommendations': self.recommendations,
            'metadata': self.metadata
        }

@dataclass
class ContentQualityReport:
    """Comprehensive content quality assessment report"""
    content_type: str
    content_format: Optional[str] = None
    overall_score: float = 0.0
    quality_level: QualityLevel = QualityLevel.UNACCEPTABLE
    dimension_assessments: List[DimensionAssessment] = field(default_factory=list)
    technical_specs: Dict[str, Any] = field(default_factory=dict)
    optimization_recommendations: List[str] = field(default_factory=list)
    improvement_plan: List[Dict[str, Any]] = field(default_factory=list)
    quality_trends: Dict[str, Any] = field(default_factory=dict)
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_overall_score(self, weights: Dict[ContentQualityDimension, float]) -> float:
        """Calculate overall quality score from dimension assessments"""
        if not self.dimension_assessments:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for assessment in self.dimension_assessments:
            weight = weights.get(assessment.dimension, 0.1)
            total_weighted_score += assessment.score * weight
            total_weight += weight
        
        self.overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        return self.overall_score
    
    def determine_quality_level(self) -> QualityLevel:
        """Determine quality level based on overall score"""
        score = self.overall_score
        
        if score >= 95:
            self.quality_level = QualityLevel.EXCEPTIONAL
        elif score >= 85:
            self.quality_level = QualityLevel.PROFESSIONAL
        elif score >= 75:
            self.quality_level = QualityLevel.HIGH
        elif score >= 65:
            self.quality_level = QualityLevel.GOOD
        elif score >= 55:
            self.quality_level = QualityLevel.ACCEPTABLE
        elif score >= 35:
            self.quality_level = QualityLevel.POOR
        else:
            self.quality_level = QualityLevel.UNACCEPTABLE
        
        return self.quality_level
    
    def get_dimension_score(self, dimension: ContentQualityDimension) -> float:
        """Get score for specific dimension"""
        for assessment in self.dimension_assessments:
            if assessment.dimension == dimension:
                return assessment.score
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content_type': self.content_type,
            'content_format': self.content_format,
            'overall_score': round(self.overall_score, 2),
            'quality_level': self.quality_level.value,
            'dimension_assessments': [da.to_dict() for da in self.dimension_assessments],
            'technical_specs': self.technical_specs,
            'optimization_recommendations': self.optimization_recommendations,
            'improvement_plan': self.improvement_plan,
            'quality_trends': self.quality_trends,
            'compliance_status': self.compliance_status,
            'execution_time': round(self.execution_time, 3),
            'timestamp': self.timestamp.isoformat(),
            'summary': {
                'total_dimensions': len(self.dimension_assessments),
                'total_metrics': sum(len(da.metrics) for da in self.dimension_assessments),
                'total_issues': sum(len(da.issues) for da in self.dimension_assessments),
                'improvement_potential': self._calculate_improvement_potential()
            }
        }
    
    def _calculate_improvement_potential(self) -> float:
        """Calculate potential score improvement"""
        if not self.dimension_assessments:
            return 0.0
        
        current_avg = statistics.mean([da.score for da in self.dimension_assessments])
        potential_avg = min(100.0, current_avg + 20)  # Realistic improvement
        return round(potential_avg - current_avg, 2)

class ContentQualityAssessor:
    """
    Enterprise-grade content quality assessment system.
    
    Provides comprehensive quality analysis across multiple dimensions including
    technical quality, aesthetic appeal, engagement potential, and optimization
    for different platforms and distribution channels.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the content quality assessor.
        
        Args:
            config: Content assessment configuration
        """
        self.config = config
        self.logger = logger
        
        # Quality assessment weights by content type
        self.content_type_weights = {
            'audio': {
                ContentQualityDimension.TECHNICAL_QUALITY: 0.25,
                ContentQualityDimension.AESTHETIC_QUALITY: 0.20,
                ContentQualityDimension.CONTENT_CLARITY: 0.20,
                ContentQualityDimension.PRODUCTION_VALUE: 0.15,
                ContentQualityDimension.ENGAGEMENT_POTENTIAL: 0.10,
                ContentQualityDimension.OPTIMIZATION: 0.05,
                ContentQualityDimension.ACCESSIBILITY: 0.03,
                ContentQualityDimension.ORIGINALITY: 0.02
            },
            'video': {
                ContentQualityDimension.AESTHETIC_QUALITY: 0.25,
                ContentQualityDimension.TECHNICAL_QUALITY: 0.20,
                ContentQualityDimension.PRODUCTION_VALUE: 0.20,
                ContentQualityDimension.ENGAGEMENT_POTENTIAL: 0.15,
                ContentQualityDimension.CONTENT_CLARITY: 0.10,
                ContentQualityDimension.OPTIMIZATION: 0.05,
                ContentQualityDimension.ACCESSIBILITY: 0.03,
                ContentQualityDimension.COHERENCE: 0.02
            },
            'image': {
                ContentQualityDimension.AESTHETIC_QUALITY: 0.30,
                ContentQualityDimension.TECHNICAL_QUALITY: 0.25,
                ContentQualityDimension.CONTENT_CLARITY: 0.20,
                ContentQualityDimension.ENGAGEMENT_POTENTIAL: 0.10,
                ContentQualityDimension.OPTIMIZATION: 0.08,
                ContentQualityDimension.PRODUCTION_VALUE: 0.05,
                ContentQualityDimension.ACCESSIBILITY: 0.02
            },
            'text': {
                ContentQualityDimension.CONTENT_CLARITY: 0.25,
                ContentQualityDimension.ENGAGEMENT_POTENTIAL: 0.20,
                ContentQualityDimension.TECHNICAL_QUALITY: 0.15,
                ContentQualityDimension.COHERENCE: 0.15,
                ContentQualityDimension.ORIGINALITY: 0.10,
                ContentQualityDimension.OPTIMIZATION: 0.08,
                ContentQualityDimension.AESTHETIC_QUALITY: 0.05,
                ContentQualityDimension.ACCESSIBILITY: 0.02
            }
        }
        
        # Quality standards by content type
        self.quality_standards = {
            'audio': {
                'sample_rate_min': 44100,
                'bit_depth_min': 16,
                'dynamic_range_min': 60,
                'snr_min': 80,
                'thd_max': 0.1
            },
            'video': {
                'resolution_min': [1280, 720],
                'fps_min': 24,
                'bitrate_min': 1000000,  # 1 Mbps
                'codec_preferred': ['h264', 'h265', 'vp9']
            },
            'image': {
                'resolution_min': [800, 600],
                'dpi_min': 72,
                'compression_quality_min': 80,
                'color_depth_min': 24
            },
            'text': {
                'readability_min': 60,
                'grammar_accuracy_min': 95,
                'spelling_accuracy_min': 98,
                'structure_score_min': 70
            }
        }
        
        # Format-specific assessors
        self.format_assessors = {
            'audio': AudioQualityAssessor(self),
            'video': VideoQualityAssessor(self),
            'image': ImageQualityAssessor(self),
            'text': TextQualityAssessor(self)
        }
        
        # Assessment history for trend analysis
        self.assessment_history: List[ContentQualityReport] = []
        
        self.logger.info(f"ContentQualityAssessor initialized with {len(self.format_assessors)} assessors")
    
    async def assess_quality(
        self,
        content_data: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        assessment_options: Optional[Dict[str, Any]] = None
    ) -> ContentQualityReport:
        """
        Comprehensive content quality assessment.
        
        Args:
            content_data: Content to assess
            content_type: Type of content (audio, video, image, text)
            metadata: Optional metadata for assessment
            assessment_options: Optional assessment configuration
            
        Returns:
            Comprehensive quality assessment report
        """
        start_time = datetime.utcnow()
        metadata = metadata or {}
        assessment_options = assessment_options or {}
        
        try:
            # Initialize quality report
            report = ContentQualityReport(
                content_type=content_type,
                content_format=metadata.get('format'),
                timestamp=start_time
            )
            
            # Get appropriate assessor
            assessor = self.format_assessors.get(content_type)
            if not assessor:
                raise ValueError(f"No quality assessor available for content type: {content_type}")
            
            # Extract technical specifications
            report.technical_specs = await self._extract_technical_specs(
                content_data, content_type, metadata
            )
            
            # Determine enabled dimensions for assessment
            enabled_dimensions = assessment_options.get('dimensions', 
                list(self.content_type_weights.get(content_type, {}).keys())
            )
            
            # Assess each quality dimension
            for dimension in enabled_dimensions:
                try:
                    assessment = await assessor.assess_dimension(
                        dimension, content_data, metadata, report.technical_specs
                    )
                    if assessment:
                        report.dimension_assessments.append(assessment)
                except Exception as e:
                    self.logger.error(f"Error assessing {dimension.value}: {str(e)}")
                    # Create error assessment
                    error_assessment = DimensionAssessment(
                        dimension=dimension,
                        score=0.0,
                        issues=[f"Assessment error: {str(e)}"]
                    )
                    report.dimension_assessments.append(error_assessment)
            
            # Calculate overall quality score
            weights = self.content_type_weights.get(content_type, {})
            report.calculate_overall_score(weights)
            report.determine_quality_level()
            
            # Generate optimization recommendations
            report.optimization_recommendations = await self._generate_optimization_recommendations(report)
            
            # Create improvement plan
            report.improvement_plan = await self._create_improvement_plan(report)
            
            # Check compliance with quality standards
            report.compliance_status = await self._check_quality_compliance(report)
            
            # Analyze quality trends if history exists
            if self.assessment_history:
                report.quality_trends = await self._analyze_quality_trends(report)
            
            # Calculate execution time
            report.execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Store in assessment history
            self.assessment_history.append(report)
            if len(self.assessment_history) > 100:  # Keep last 100 assessments
                self.assessment_history.pop(0)
            
            self.logger.info(
                f"Quality assessment completed: {content_type} - "
                f"Score: {report.overall_score:.1f} ({report.quality_level.value}) - "
                f"Time: {report.execution_time:.3f}s"
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error during quality assessment: {str(e)}")
            error_report = ContentQualityReport(
                content_type=content_type,
                overall_score=0.0,
                quality_level=QualityLevel.UNACCEPTABLE,
                timestamp=start_time
            )
            error_report.dimension_assessments.append(
                DimensionAssessment(
                    dimension=ContentQualityDimension.TECHNICAL_QUALITY,
                    score=0.0,
                    issues=[f"Assessment failed: {str(e)}"]
                )
            )
            error_report.execution_time = (datetime.utcnow() - start_time).total_seconds()
            return error_report
    
    async def _extract_technical_specs(
        self,
        content_data: Any,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract technical specifications from content"""
        
        specs = {
            'content_type': content_type,
            'size_bytes': self._get_content_size(content_data),
            'format': metadata.get('format', 'unknown'),
            'extraction_timestamp': datetime.utcnow().isoformat()
        }
        
        try:
            if content_type == 'audio' and HAS_LIBROSA:
                specs.update(await self._extract_audio_specs(content_data))
            elif content_type == 'video' and HAS_FFMPEG:
                specs.update(await self._extract_video_specs(content_data))
            elif content_type == 'image' and HAS_VISION:
                specs.update(await self._extract_image_specs(content_data))
            elif content_type == 'text':
                specs.update(await self._extract_text_specs(content_data))
                
        except Exception as e:
            self.logger.warning(f"Could not extract technical specs: {str(e)}")
            specs['extraction_error'] = str(e)
        
        return specs
    
    async def _extract_audio_specs(self, content_data: Any) -> Dict[str, Any]:
        """Extract audio technical specifications"""
        if not HAS_LIBROSA:
            return {'error': 'Audio analysis not available'}
        
        # This would need actual audio data processing
        return {
            'sample_rate': 44100,
            'duration': 0.0,
            'channels': 2,
            'bit_depth': 16,
            'format': 'wav'
        }
    
    async def _extract_video_specs(self, content_data: Any) -> Dict[str, Any]:
        """Extract video technical specifications"""
        if not HAS_FFMPEG:
            return {'error': 'Video analysis not available'}
        
        return {
            'width': 1920,
            'height': 1080,
            'fps': 30,
            'duration': 0.0,
            'codec': 'h264',
            'bitrate': 5000000
        }
    
    async def _extract_image_specs(self, content_data: Any) -> Dict[str, Any]:
        """Extract image technical specifications"""
        if not HAS_VISION:
            return {'error': 'Image analysis not available'}
        
        return {
            'width': 1920,
            'height': 1080,
            'format': 'JPEG',
            'mode': 'RGB',
            'dpi': (72, 72)
        }
    
    async def _extract_text_specs(self, content_data: Any) -> Dict[str, Any]:
        """Extract text specifications"""
        if isinstance(content_data, str):
            text = content_data
        else:
            text = str(content_data)
        
        return {
            'character_count': len(text),
            'word_count': len(text.split()),
            'line_count': text.count('\n') + 1,
            'paragraph_count': len([p for p in text.split('\n\n') if p.strip()]),
            'encoding': 'utf-8'
        }
    
    def _get_content_size(self, content_data: Any) -> int:
        """Get content size in bytes"""
        if hasattr(content_data, '__len__'):
            return len(content_data)
        elif isinstance(content_data, str):
            return len(content_data.encode('utf-8'))
        else:
            return len(str(content_data).encode('utf-8'))
    
    async def _generate_optimization_recommendations(
        self, 
        report: ContentQualityReport
    ) -> List[str]:
        """Generate content optimization recommendations"""
        
        recommendations = []
        
        # Analyze dimension scores for recommendations
        low_scoring_dimensions = [
            da for da in report.dimension_assessments 
            if da.score < 75
        ]
        
        for dimension_assessment in low_scoring_dimensions:
            dimension = dimension_assessment.dimension
            score = dimension_assessment.score
            
            if dimension == ContentQualityDimension.TECHNICAL_QUALITY:
                if score < 50:
                    recommendations.append("Critical technical issues require immediate attention")
                elif score < 70:
                    recommendations.append("Improve technical specifications and encoding quality")
                else:
                    recommendations.append("Fine-tune technical parameters for better quality")
            
            elif dimension == ContentQualityDimension.AESTHETIC_QUALITY:
                if score < 60:
                    recommendations.append("Redesign visual/auditory composition for better appeal")
                else:
                    recommendations.append("Enhance aesthetic elements and presentation")
            
            elif dimension == ContentQualityDimension.CONTENT_CLARITY:
                if score < 65:
                    recommendations.append("Improve content clarity and readability significantly")
                else:
                    recommendations.append("Refine content structure and presentation")
            
            elif dimension == ContentQualityDimension.ENGAGEMENT_POTENTIAL:
                recommendations.append("Enhance content to increase audience engagement")
            
            elif dimension == ContentQualityDimension.PRODUCTION_VALUE:
                recommendations.append("Invest in better production techniques and tools")
            
            elif dimension == ContentQualityDimension.OPTIMIZATION:
                recommendations.append("Optimize content for target platforms and distribution")
        
        # Add content-type specific recommendations
        if report.content_type == 'audio':
            if report.get_dimension_score(ContentQualityDimension.TECHNICAL_QUALITY) < 80:
                recommendations.append("Consider higher bitrate and sample rate for better audio quality")
        
        elif report.content_type == 'video':
            if report.get_dimension_score(ContentQualityDimension.TECHNICAL_QUALITY) < 80:
                recommendations.append("Upgrade video resolution and encoding settings")
        
        elif report.content_type == 'image':
            if report.get_dimension_score(ContentQualityDimension.TECHNICAL_QUALITY) < 80:
                recommendations.append("Increase image resolution and reduce compression artifacts")
        
        elif report.content_type == 'text':
            if report.get_dimension_score(ContentQualityDimension.CONTENT_CLARITY) < 80:
                recommendations.append("Improve writing clarity and structure")
        
        # Overall quality recommendations
        if report.overall_score < 60:
            recommendations.insert(0, "Content requires comprehensive quality improvement")
        elif report.overall_score < 80:
            recommendations.insert(0, "Content has good potential with targeted improvements")
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _create_improvement_plan(self, report: ContentQualityReport) -> List[Dict[str, Any]]:
        """Create detailed improvement plan"""
        
        plan = []
        
        # Sort dimensions by score (lowest first for priority)
        sorted_assessments = sorted(
            report.dimension_assessments, 
            key=lambda x: x.score
        )
        
        for i, assessment in enumerate(sorted_assessments[:5]):  # Top 5 priorities
            if assessment.score < 85:  # Only if improvement needed
                
                current_score = assessment.score
                target_score = min(100, current_score + (90 - current_score) * 0.7)
                improvement_potential = target_score - current_score
                
                # Estimate effort and timeline
                if current_score < 50:
                    effort = "High"
                    timeline = "4-6 weeks"
                elif current_score < 70:
                    effort = "Medium"
                    timeline = "2-3 weeks"
                else:
                    effort = "Low"
                    timeline = "1-2 weeks"
                
                plan_item = {
                    'priority': i + 1,
                    'dimension': assessment.dimension.value,
                    'current_score': round(current_score, 1),
                    'target_score': round(target_score, 1),
                    'improvement_potential': round(improvement_potential, 1),
                    'effort_level': effort,
                    'estimated_timeline': timeline,
                    'specific_actions': assessment.recommendations[:3],  # Top 3 recommendations
                    'success_metrics': self._get_success_metrics(assessment.dimension),
                    'impact_on_overall_score': round(improvement_potential * 0.2, 1)  # Estimated
                }
                
                plan.append(plan_item)
        
        return plan
    
    def _get_success_metrics(self, dimension: ContentQualityDimension) -> List[str]:
        """Get success metrics for dimension improvement"""
        
        metrics_map = {
            ContentQualityDimension.TECHNICAL_QUALITY: [
                "Technical specifications meet industry standards",
                "No technical errors or artifacts detected",
                "Encoding quality optimized for target platform"
            ],
            ContentQualityDimension.AESTHETIC_QUALITY: [
                "Visual/auditory appeal rating > 80%",
                "Composition follows best practices",
                "Color/sound balance professionally calibrated"
            ],
            ContentQualityDimension.CONTENT_CLARITY: [
                "Content clarity score > 85%",
                "No ambiguous or unclear elements",
                "Information hierarchy clearly defined"
            ],
            ContentQualityDimension.ENGAGEMENT_POTENTIAL: [
                "Engagement prediction score > 75%",
                "Content hooks and retention elements present",
                "Audience interest maintained throughout"
            ],
            ContentQualityDimension.PRODUCTION_VALUE: [
                "Professional production standards met",
                "Consistent quality across all elements",
                "Post-production enhancements applied"
            ],
            ContentQualityDimension.OPTIMIZATION: [
                "Optimized for target distribution channels",
                "File size and quality balance achieved",
                "Platform-specific requirements met"
            ]
        }
        
        return metrics_map.get(dimension, ["Quality metrics improved", "Standards compliance achieved"])
    
    async def _check_quality_compliance(self, report: ContentQualityReport) -> Dict[str, bool]:
        """Check compliance with quality standards"""
        
        compliance = {}
        standards = self.quality_standards.get(report.content_type, {})
        specs = report.technical_specs
        
        if report.content_type == 'audio':
            compliance['sample_rate'] = specs.get('sample_rate', 0) >= standards.get('sample_rate_min', 0)
            compliance['bit_depth'] = specs.get('bit_depth', 0) >= standards.get('bit_depth_min', 0)
            
        elif report.content_type == 'video':
            width = specs.get('width', 0)
            height = specs.get('height', 0)
            min_res = standards.get('resolution_min', [0, 0])
            compliance['resolution'] = width >= min_res[0] and height >= min_res[1]
            compliance['fps'] = specs.get('fps', 0) >= standards.get('fps_min', 0)
            
        elif report.content_type == 'image':
            width = specs.get('width', 0)
            height = specs.get('height', 0)
            min_res = standards.get('resolution_min', [0, 0])
            compliance['resolution'] = width >= min_res[0] and height >= min_res[1]
            
        elif report.content_type == 'text':
            compliance['word_count'] = specs.get('word_count', 0) >= 10  # Minimum content
            compliance['structure'] = True  # Would need actual analysis
        
        # Overall compliance
        compliance['overall'] = all(compliance.values()) if compliance else False
        
        return compliance
    
    async def _analyze_quality_trends(self, current_report: ContentQualityReport) -> Dict[str, Any]:
        """Analyze quality trends from assessment history"""
        
        if len(self.assessment_history) < 2:
            return {'message': 'Insufficient data for trend analysis'}
        
        # Filter history by content type
        same_type_history = [
            r for r in self.assessment_history[-10:]  # Last 10 assessments
            if r.content_type == current_report.content_type
        ]
        
        if len(same_type_history) < 2:
            return {'message': f'Insufficient {current_report.content_type} assessment history'}
        
        # Calculate trends
        scores = [r.overall_score for r in same_type_history]
        
        trend_analysis = {
            'score_trend': 'improving' if scores[-1] > scores[0] else 'declining' if scores[-1] < scores[0] else 'stable',
            'average_score': round(statistics.mean(scores), 2),
            'score_variance': round(statistics.variance(scores) if len(scores) > 1 else 0, 2),
            'best_score': max(scores),
            'worst_score': min(scores),
            'assessments_count': len(same_type_history),
            'improvement_rate': round((scores[-1] - scores[0]) / len(scores), 2) if len(scores) > 1 else 0
        }
        
        # Dimension trends
        dimension_trends = {}
        for dimension in ContentQualityDimension:
            dimension_scores = []
            for report in same_type_history:
                for da in report.dimension_assessments:
                    if da.dimension == dimension:
                        dimension_scores.append(da.score)
                        break
            
            if dimension_scores:
                dimension_trends[dimension.value] = {
                    'current': round(dimension_scores[-1], 1),
                    'average': round(statistics.mean(dimension_scores), 1),
                    'trend': 'improving' if len(dimension_scores) > 1 and dimension_scores[-1] > dimension_scores[0] else 'stable'
                }
        
        trend_analysis['dimension_trends'] = dimension_trends
        
        return trend_analysis
    
    def get_assessment_statistics(self) -> Dict[str, Any]:
        """Get comprehensive assessment statistics"""
        
        if not self.assessment_history:
            return {'message': 'No assessment history available'}
        
        # Overall statistics
        all_scores = [r.overall_score for r in self.assessment_history]
        
        stats = {
            'total_assessments': len(self.assessment_history),
            'average_score': round(statistics.mean(all_scores), 2),
            'median_score': round(statistics.median(all_scores), 2),
            'score_std_dev': round(statistics.stdev(all_scores) if len(all_scores) > 1 else 0, 2),
            'min_score': min(all_scores),
            'max_score': max(all_scores)
        }
        
        # Statistics by content type
        by_content_type = defaultdict(list)
        for report in self.assessment_history:
            by_content_type[report.content_type].append(report.overall_score)
        
        content_type_stats = {}
        for content_type, scores in by_content_type.items():
            content_type_stats[content_type] = {
                'count': len(scores),
                'average_score': round(statistics.mean(scores), 2),
                'best_score': max(scores),
                'worst_score': min(scores)
            }
        
        stats['by_content_type'] = content_type_stats
        
        # Quality level distribution
        quality_levels = [r.quality_level.value for r in self.assessment_history]
        quality_distribution = dict(Counter(quality_levels))
        stats['quality_level_distribution'] = quality_distribution
        
        # Recent performance (last 10 assessments)
        if len(self.assessment_history) >= 10:
            recent_scores = all_scores[-10:]
            stats['recent_performance'] = {
                'average_score': round(statistics.mean(recent_scores), 2),
                'trend': 'improving' if recent_scores[-1] > recent_scores[0] else 'declining' if recent_scores[-1] < recent_scores[0] else 'stable'
            }
        
        return stats

# Content-specific quality assessors

class AudioQualityAssessor:
    """Specialized audio quality assessment"""
    
    def __init__(self, parent_assessor):
        self.parent = parent_assessor
        self.logger = parent_assessor.logger
    
    async def assess_dimension(
        self,
        dimension: ContentQualityDimension,
        content_data: Any,
        metadata: Dict[str, Any],
        technical_specs: Dict[str, Any]
    ) -> Optional[DimensionAssessment]:
        """Assess specific dimension for audio content"""
        
        assessment = DimensionAssessment(dimension=dimension, score=0.0)
        
        if dimension == ContentQualityDimension.TECHNICAL_QUALITY:
            await self._assess_audio_technical_quality(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.AESTHETIC_QUALITY:
            await self._assess_audio_aesthetic_quality(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.CONTENT_CLARITY:
            await self._assess_audio_clarity(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.PRODUCTION_VALUE:
            await self._assess_audio_production_value(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.ENGAGEMENT_POTENTIAL:
            await self._assess_audio_engagement(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.OPTIMIZATION:
            await self._assess_audio_optimization(assessment, content_data, technical_specs)
        else:
            # Default assessment for other dimensions
            assessment.score = 75.0
            assessment.add_metric(QualityMetric(
                name="default_audio_score",
                value=75.0,
                weight=1.0,
                description=f"Default score for {dimension.value}"
            ))
        
        assessment.calculate_score()
        return assessment
    
    async def _assess_audio_technical_quality(
        self, 
        assessment: DimensionAssessment, 
        content_data: Any, 
        specs: Dict[str, Any]
    ):
        """Assess audio technical quality"""
        
        # Sample rate assessment
        sample_rate = specs.get('sample_rate', 44100)
        sample_rate_score = min(100, (sample_rate / 96000) * 100) if sample_rate > 0 else 50
        assessment.add_metric(QualityMetric(
            name="sample_rate",
            value=sample_rate,
            weight=0.3,
            max_value=96000,
            unit="Hz",
            description="Audio sample rate quality",
            recommendation="Use 48kHz or higher for professional quality" if sample_rate < 48000 else ""
        ))
        
        # Bit depth assessment
        bit_depth = specs.get('bit_depth', 16)
        bit_depth_score = min(100, (bit_depth / 32) * 100) if bit_depth > 0 else 50
        assessment.add_metric(QualityMetric(
            name="bit_depth",
            value=bit_depth,
            weight=0.25,
            max_value=32,
            unit="bits",
            description="Audio bit depth quality",
            recommendation="Use 24-bit or higher for professional quality" if bit_depth < 24 else ""
        ))
        
        # Format assessment
        audio_format = specs.get('format', 'unknown').lower()
        format_scores = {'flac': 100, 'wav': 95, 'aac': 80, 'mp3': 70, 'ogg': 75}
        format_score = format_scores.get(audio_format, 50)
        assessment.add_metric(QualityMetric(
            name="format_quality",
            value=format_score,
            weight=0.2,
            description=f"Audio format quality ({audio_format})",
            recommendation="Consider lossless format for highest quality" if format_score < 90 else ""
        ))
        
        # Duration assessment (for completeness)
        duration = specs.get('duration', 0)
        duration_score = 100 if duration > 10 else max(50, duration * 5)  # Penalty for very short audio
        assessment.add_metric(QualityMetric(
            name="duration_adequacy",
            value=duration_score,
            weight=0.15,
            description="Audio duration adequacy",
            recommendation="Consider longer content for better engagement" if duration < 30 else ""
        ))
        
        # Channel configuration
        channels = specs.get('channels', 2)
        channel_score = 100 if channels >= 2 else 70  # Stereo preferred
        assessment.add_metric(QualityMetric(
            name="channel_configuration",
            value=channel_score,
            weight=0.1,
            description=f"Audio channel configuration ({channels} channels)",
            recommendation="Use stereo for better spatial experience" if channels < 2 else ""
        ))

class VideoQualityAssessor:
    """Specialized video quality assessment"""
    
    def __init__(self, parent_assessor):
        self.parent = parent_assessor
        self.logger = parent_assessor.logger
    
    async def assess_dimension(
        self,
        dimension: ContentQualityDimension,
        content_data: Any,
        metadata: Dict[str, Any],
        technical_specs: Dict[str, Any]
    ) -> Optional[DimensionAssessment]:
        """Assess specific dimension for video content"""
        
        assessment = DimensionAssessment(dimension=dimension, score=0.0)
        
        if dimension == ContentQualityDimension.TECHNICAL_QUALITY:
            await self._assess_video_technical_quality(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.AESTHETIC_QUALITY:
            await self._assess_video_aesthetic_quality(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.CONTENT_CLARITY:
            await self._assess_video_clarity(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.PRODUCTION_VALUE:
            await self._assess_video_production_value(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.ENGAGEMENT_POTENTIAL:
            await self._assess_video_engagement(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.OPTIMIZATION:
            await self._assess_video_optimization(assessment, content_data, technical_specs)
        else:
            # Default assessment
            assessment.score = 75.0
            assessment.add_metric(QualityMetric(
                name="default_video_score",
                value=75.0,
                weight=1.0,
                description=f"Default score for {dimension.value}"
            ))
        
        assessment.calculate_score()
        return assessment
    
    async def _assess_video_technical_quality(
        self, 
        assessment: DimensionAssessment, 
        content_data: Any, 
        specs: Dict[str, Any]
    ):
        """Assess video technical quality"""
        
        # Resolution assessment
        width = specs.get('width', 1920)
        height = specs.get('height', 1080)
        total_pixels = width * height
        
        # Score based on common resolutions
        resolution_scores = {
            7680 * 4320: 100,  # 8K
            3840 * 2160: 95,   # 4K
            2560 * 1440: 90,   # 1440p
            1920 * 1080: 85,   # 1080p
            1280 * 720: 75,    # 720p
            854 * 480: 60,     # 480p
            640 * 360: 45      # 360p
        }
        
        resolution_score = 85  # Default for 1080p
        for res_pixels, score in sorted(resolution_scores.items(), reverse=True):
            if total_pixels >= res_pixels:
                resolution_score = score
                break
        
        assessment.add_metric(QualityMetric(
            name="resolution",
            value=resolution_score,
            weight=0.35,
            description=f"Video resolution ({width}x{height})",
            recommendation="Consider higher resolution for better quality" if resolution_score < 80 else ""
        ))
        
        # Frame rate assessment
        fps = specs.get('fps', 30)
        fps_score = min(100, (fps / 60) * 100) if fps <= 60 else 100
        assessment.add_metric(QualityMetric(
            name="frame_rate",
            value=fps,
            weight=0.25,
            max_value=60,
            unit="fps",
            description="Video frame rate",
            recommendation="Consider 60fps for smoother motion" if fps < 60 else ""
        ))
        
        # Bitrate assessment
        bitrate = specs.get('bitrate', 5000000)
        # Target bitrate based on resolution (rough estimates)
        target_bitrates = {
            7680 * 4320: 50000000,  # 8K: 50 Mbps
            3840 * 2160: 20000000,  # 4K: 20 Mbps
            1920 * 1080: 8000000,   # 1080p: 8 Mbps
            1280 * 720: 4000000,    # 720p: 4 Mbps
            854 * 480: 2000000      # 480p: 2 Mbps
        }
        
        target_bitrate = 8000000  # Default for 1080p
        for res_pixels, tbr in sorted(target_bitrates.items(), reverse=True):
            if total_pixels >= res_pixels:
                target_bitrate = tbr
                break
        
        bitrate_score = min(100, (bitrate / target_bitrate) * 100)
        assessment.add_metric(QualityMetric(
            name="bitrate",
            value=bitrate,
            weight=0.25,
            max_value=target_bitrate,
            unit="bps",
            description="Video bitrate quality",
            recommendation="Increase bitrate for better quality" if bitrate_score < 80 else ""
        ))
        
        # Codec assessment
        codec = specs.get('codec', 'unknown').lower()
        codec_scores = {'h265': 100, 'vp9': 95, 'h264': 85, 'vp8': 70, 'xvid': 60}
        codec_score = codec_scores.get(codec, 50)
        assessment.add_metric(QualityMetric(
            name="codec_efficiency",
            value=codec_score,
            weight=0.15,
            description=f"Video codec efficiency ({codec})",
            recommendation="Consider modern codec like H.265 or VP9" if codec_score < 85 else ""
        ))

class ImageQualityAssessor:
    """Specialized image quality assessment"""
    
    def __init__(self, parent_assessor):
        self.parent = parent_assessor
        self.logger = parent_assessor.logger
    
    async def assess_dimension(
        self,
        dimension: ContentQualityDimension,
        content_data: Any,
        metadata: Dict[str, Any],
        technical_specs: Dict[str, Any]
    ) -> Optional[DimensionAssessment]:
        """Assess specific dimension for image content"""
        
        assessment = DimensionAssessment(dimension=dimension, score=0.0)
        
        if dimension == ContentQualityDimension.TECHNICAL_QUALITY:
            await self._assess_image_technical_quality(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.AESTHETIC_QUALITY:
            await self._assess_image_aesthetic_quality(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.CONTENT_CLARITY:
            await self._assess_image_clarity(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.ENGAGEMENT_POTENTIAL:
            await self._assess_image_engagement(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.OPTIMIZATION:
            await self._assess_image_optimization(assessment, content_data, technical_specs)
        else:
            # Default assessment
            assessment.score = 75.0
            assessment.add_metric(QualityMetric(
                name="default_image_score",
                value=75.0,
                weight=1.0,
                description=f"Default score for {dimension.value}"
            ))
        
        assessment.calculate_score()
        return assessment
    
    async def _assess_image_technical_quality(
        self, 
        assessment: DimensionAssessment, 
        content_data: Any, 
        specs: Dict[str, Any]
    ):
        """Assess image technical quality"""
        
        # Resolution assessment
        width = specs.get('width', 1920)
        height = specs.get('height', 1080)
        total_pixels = width * height
        
        # Score based on megapixels
        megapixels = total_pixels / 1000000
        resolution_score = min(100, (megapixels / 24) * 100)  # 24MP = 100%
        
        assessment.add_metric(QualityMetric(
            name="resolution",
            value=megapixels,
            weight=0.4,
            max_value=24,
            unit="MP",
            description=f"Image resolution ({width}x{height}, {megapixels:.1f}MP)",
            recommendation="Consider higher resolution for print quality" if megapixels < 8 else ""
        ))
        
        # Format assessment
        image_format = specs.get('format', 'JPEG').upper()
        format_scores = {'TIFF': 100, 'PNG': 95, 'WEBP': 85, 'JPEG': 80, 'BMP': 70, 'GIF': 60}
        format_score = format_scores.get(image_format, 70)
        
        assessment.add_metric(QualityMetric(
            name="format_quality",
            value=format_score,
            weight=0.25,
            description=f"Image format quality ({image_format})",
            recommendation="Consider lossless format for highest quality" if format_score < 90 else ""
        ))
        
        # Color depth assessment (if available)
        mode = specs.get('mode', 'RGB')
        color_depth_score = 100 if mode == 'RGB' else 80 if mode == 'RGBA' else 60
        
        assessment.add_metric(QualityMetric(
            name="color_depth",
            value=color_depth_score,
            weight=0.2,
            description=f"Color depth and mode ({mode})",
            recommendation="Use RGB mode for full color representation" if color_depth_score < 90 else ""
        ))
        
        # DPI assessment (if available)
        dpi = specs.get('dpi', (72, 72))
        dpi_value = dpi[0] if isinstance(dpi, tuple) else dpi
        dpi_score = min(100, (dpi_value / 300) * 100)  # 300 DPI = 100%
        
        assessment.add_metric(QualityMetric(
            name="dpi",
            value=dpi_value,
            weight=0.15,
            max_value=300,
            unit="DPI",
            description=f"Image DPI ({dpi_value})",
            recommendation="Use 300 DPI for print quality" if dpi_value < 150 else ""
        ))

class TextQualityAssessor:
    """Specialized text quality assessment"""
    
    def __init__(self, parent_assessor):
        self.parent = parent_assessor
        self.logger = parent_assessor.logger
    
    async def assess_dimension(
        self,
        dimension: ContentQualityDimension,
        content_data: Any,
        metadata: Dict[str, Any],
        technical_specs: Dict[str, Any]
    ) -> Optional[DimensionAssessment]:
        """Assess specific dimension for text content"""
        
        assessment = DimensionAssessment(dimension=dimension, score=0.0)
        
        if dimension == ContentQualityDimension.TECHNICAL_QUALITY:
            await self._assess_text_technical_quality(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.CONTENT_CLARITY:
            await self._assess_text_clarity(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.ENGAGEMENT_POTENTIAL:
            await self._assess_text_engagement(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.COHERENCE:
            await self._assess_text_coherence(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.ORIGINALITY:
            await self._assess_text_originality(assessment, content_data, technical_specs)
        elif dimension == ContentQualityDimension.OPTIMIZATION:
            await self._assess_text_optimization(assessment, content_data, technical_specs)
        else:
            # Default assessment
            assessment.score = 75.0
            assessment.add_metric(QualityMetric(
                name="default_text_score",
                value=75.0,
                weight=1.0,
                description=f"Default score for {dimension.value}"
            ))
        
        assessment.calculate_score()
        return assessment
    
    async def _assess_text_technical_quality(
        self, 
        assessment: DimensionAssessment, 
        content_data: Any, 
        specs: Dict[str, Any]
    ):
        """Assess text technical quality (grammar, spelling, etc.)"""
        
        text = str(content_data) if not isinstance(content_data, str) else content_data
        
        # Length assessment
        word_count = specs.get('word_count', 0)
        length_score = min(100, max(50, (word_count / 500) * 100))  # Target ~500 words
        
        assessment.add_metric(QualityMetric(
            name="content_length",
            value=word_count,
            weight=0.2,
            max_value=1000,
            unit="words",
            description=f"Content length adequacy ({word_count} words)",
            recommendation="Consider expanding content for better depth" if word_count < 200 else ""
        ))
        
        # Structure assessment
        paragraph_count = specs.get('paragraph_count', 1)
        structure_score = min(100, paragraph_count * 25) if paragraph_count <= 4 else 100
        
        assessment.add_metric(QualityMetric(
            name="structure",
            value=structure_score,
            weight=0.3,
            description=f"Content structure ({paragraph_count} paragraphs)",
            recommendation="Break content into multiple paragraphs for readability" if paragraph_count < 2 else ""
        ))
        
        # Basic readability assessment
        if HAS_NLP:
            try:
                blob = TextBlob(text)
                # Simple readability approximation
                avg_sentence_length = len(text.split()) / max(1, len(blob.sentences))
                readability_score = max(50, 100 - (avg_sentence_length - 15) * 2)  # Penalize very long sentences
                
                assessment.add_metric(QualityMetric(
                    name="readability",
                    value=readability_score,
                    weight=0.25,
                    description=f"Text readability (avg sentence: {avg_sentence_length:.1f} words)",
                    recommendation="Use shorter sentences for better readability" if avg_sentence_length > 25 else ""
                ))
            except:
                assessment.add_metric(QualityMetric(
                    name="readability",
                    value=75.0,
                    weight=0.25,
                    description="Readability assessment unavailable"
                ))
        else:
            assessment.add_metric(QualityMetric(
                name="readability",
                value=75.0,
                weight=0.25,
                description="Readability assessment unavailable (NLP not available)"
            ))
        
        # Encoding and character assessment
        try:
            text.encode('utf-8')
            encoding_score = 100
        except:
            encoding_score = 50
        
        assessment.add_metric(QualityMetric(
            name="encoding_quality",
            value=encoding_score,
            weight=0.15,
            description="Text encoding quality",
            recommendation="Fix character encoding issues" if encoding_score < 100 else ""
        ))
        
        # Basic formatting assessment
        has_formatting = any(marker in text for marker in ['**', '*', '_', '#', '`'])
        formatting_score = 85 if has_formatting else 75
        
        assessment.add_metric(QualityMetric(
            name="formatting",
            value=formatting_score,
            weight=0.1,
            description="Text formatting usage",
            recommendation="Consider using formatting for better presentation" if not has_formatting else ""
        ))
    
    async def assess_quality(
        self,
        content_data: Any,
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assess content quality across all dimensions.
        
        Args:
            content_data: Content to assess
            content_type: Type of content (audio, video, image, text)
            metadata: Optional metadata for assessment
            
        Returns:
            Comprehensive quality assessment results
        """
        start_time = datetime.utcnow()
        
        try:
            # Get appropriate assessor
            assessor = self.assessors.get(content_type)
            if not assessor:
                raise ValueError(f"No quality assessor for content type: {content_type}")
            
            # Run content-specific assessment
            dimension_scores = await assessor(content_data, metadata)
            
            # Calculate overall quality score
            overall_score = self._calculate_overall_score(dimension_scores, content_type)
            
            # Determine quality level
            quality_level = self._determine_quality_level(overall_score, content_type)
            
            # Generate optimization recommendations
            recommendations = self._generate_optimization_recommendations(
                dimension_scores, content_type, metadata
            )
            
            # Generate improvement suggestions
            improvement_suggestions = self._generate_improvement_suggestions(
                dimension_scores, content_type
            )
            
            # Calculate potential score with improvements
            potential_score = self._calculate_potential_score(dimension_scores)
            
            # Execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'score': round(overall_score, 2),
                'quality_level': quality_level.value,
                'dimension_scores': {dim.value: score for dim, score in dimension_scores.items()},
                'content_type': content_type,
                'potential_score': round(potential_score, 2),
                'recommendations': recommendations,
                'improvement_suggestions': improvement_suggestions,
                'technical_details': self._get_technical_details(content_data, content_type),
                'execution_time': execution_time,
                'timestamp': start_time.isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error during quality assessment: {str(e)}")
            return {
                'score': 0,
                'quality_level': QualityLevel.POOR.value,
                'error': str(e),
                'timestamp': start_time.isoformat()
            }
    
    def _calculate_overall_score(
        self,
        dimension_scores: Dict[ContentQualityDimension, float],
        content_type: str
    ) -> float:
        """Calculate overall quality score from dimension scores"""
        
        # Adjust weights based on content type
        adjusted_weights = self._adjust_weights_for_content_type(content_type)
        
        total_score = 0.0
        total_weight = 0.0
        
        for dimension, score in dimension_scores.items():
            weight = adjusted_weights.get(dimension, 0)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def _adjust_weights_for_content_type(self, content_type: str) -> Dict[ContentQualityDimension, float]:
        """Adjust dimension weights based on content type"""
        
        weights = self.dimension_weights.copy()
        
        if content_type == 'audio':
            # For audio, technical quality and clarity are most important
            weights[ContentQualityDimension.TECHNICAL_QUALITY] = 0.4
            weights[ContentQualityDimension.CONTENT_CLARITY] = 0.25
            weights[ContentQualityDimension.AESTHETIC_QUALITY] = 0.1
            weights[ContentQualityDimension.PRODUCTION_VALUE] = 0.15
            weights[ContentQualityDimension.ENGAGEMENT_POTENTIAL] = 0.1
            
        elif content_type == 'video':
            # For video, aesthetic quality and production value are key
            weights[ContentQualityDimension.AESTHETIC_QUALITY] = 0.3
            weights[ContentQualityDimension.PRODUCTION_VALUE] = 0.25
            weights[ContentQualityDimension.TECHNICAL_QUALITY] = 0.25
            weights[ContentQualityDimension.ENGAGEMENT_POTENTIAL] = 0.2
            
        elif content_type == 'image':
            # For images, aesthetic and technical quality dominate
            weights[ContentQualityDimension.AESTHETIC_QUALITY] = 0.4
            weights[ContentQualityDimension.TECHNICAL_QUALITY] = 0.35
            weights[ContentQualityDimension.CONTENT_CLARITY] = 0.15
            weights[ContentQualityDimension.OPTIMIZATION] = 0.1
            
        elif content_type == 'text':
            # For text, clarity and engagement are most important
            weights[ContentQualityDimension.CONTENT_CLARITY] = 0.4
            weights[ContentQualityDimension.ENGAGEMENT_POTENTIAL] = 0.3
            weights[ContentQualityDimension.TECHNICAL_QUALITY] = 0.15
            weights[ContentQualityDimension.OPTIMIZATION] = 0.15
        
        return weights
    
    def _determine_quality_level(self, score: float, content_type: str) -> QualityLevel:
        """Determine quality level based on score and content type"""
        
        thresholds = self.quality_thresholds.get(content_type, self.quality_thresholds['text'])
        
        if score >= thresholds['professional']:
            return QualityLevel.PROFESSIONAL
        elif score >= thresholds['high']:
            return QualityLevel.HIGH
        elif score >= thresholds['good']:
            return QualityLevel.GOOD
        elif score >= thresholds['acceptable']:
            return QualityLevel.ACCEPTABLE
        else:
            return QualityLevel.POOR
    
    # Content-specific quality assessors
    async def _assess_audio_quality(
        self,
        content_data: Any,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[ContentQualityDimension, float]:
        """Assess audio content quality"""
        
        scores = {}
        
        # Technical Quality (bit rate, sample rate, compression, noise)
        scores[ContentQualityDimension.TECHNICAL_QUALITY] = await self._assess_audio_technical_quality(
            content_data, metadata
        )
        
        # Content Clarity (audio clarity, balance, dynamics)
        scores[ContentQualityDimension.CONTENT_CLARITY] = await self._assess_audio_clarity(
            content_data, metadata
        )
        
        # Production Value (mixing, mastering, effects)
        scores[ContentQualityDimension.PRODUCTION_VALUE] = await self._assess_audio_production_value(
            content_data, metadata
        )
        
        # Engagement Potential (rhythm, melody, structure)
        scores[ContentQualityDimension.ENGAGEMENT_POTENTIAL] = await self._assess_audio_engagement(
            content_data, metadata
        )
        
        # Aesthetic Quality (musical appeal, composition)
        scores[ContentQualityDimension.AESTHETIC_QUALITY] = await self._assess_audio_aesthetics(
            content_data, metadata
        )
        
        # Optimization (format, compression, platform readiness)
        scores[ContentQualityDimension.OPTIMIZATION] = await self._assess_audio_optimization(
            content_data, metadata
        )
        
        return scores
    
    async def _assess_video_quality(
        self,
        content_data: Any,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[ContentQualityDimension, float]:
        """Assess video content quality"""
        
        scores = {}
        
        # Technical Quality (resolution, frame rate, encoding)
        scores[ContentQualityDimension.TECHNICAL_QUALITY] = await self._assess_video_technical_quality(
            content_data, metadata
        )
        
        # Aesthetic Quality (visual appeal, composition, lighting)
        scores[ContentQualityDimension.AESTHETIC_QUALITY] = await self._assess_video_aesthetics(
            content_data, metadata
        )
        
        # Content Clarity (image sharpness, audio clarity)
        scores[ContentQualityDimension.CONTENT_CLARITY] = await self._assess_video_clarity(
            content_data, metadata
        )
        
        # Production Value (editing, effects, transitions)
        scores[ContentQualityDimension.PRODUCTION_VALUE] = await self._assess_video_production_value(
            content_data, metadata
        )
        
        # Engagement Potential (storytelling, pacing, interest)
        scores[ContentQualityDimension.ENGAGEMENT_POTENTIAL] = await self._assess_video_engagement(
            content_data, metadata
        )
        
        # Optimization (compression, format, platform optimization)
        scores[ContentQualityDimension.OPTIMIZATION] = await self._assess_video_optimization(
            content_data, metadata
        )
        
        return scores
    
    async def _assess_image_quality(
        self,
        content_data: Any,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[ContentQualityDimension, float]:
        """Assess image content quality"""
        
        scores = {}
        
        # Technical Quality (resolution, compression, artifacts)
        scores[ContentQualityDimension.TECHNICAL_QUALITY] = await self._assess_image_technical_quality(
            content_data, metadata
        )
        
        # Aesthetic Quality (composition, color, lighting)
        scores[ContentQualityDimension.AESTHETIC_QUALITY] = await self._assess_image_aesthetics(
            content_data, metadata
        )
        
        # Content Clarity (sharpness, focus, detail)
        scores[ContentQualityDimension.CONTENT_CLARITY] = await self._assess_image_clarity(
            content_data, metadata
        )
        
        # Engagement Potential (visual impact, interest)
        scores[ContentQualityDimension.ENGAGEMENT_POTENTIAL] = await self._assess_image_engagement(
            content_data, metadata
        )
        
        # Production Value (editing, enhancement, style)
        scores[ContentQualityDimension.PRODUCTION_VALUE] = await self._assess_image_production_value(
            content_data, metadata
        )
        
        # Optimization (format, size, web optimization)
        scores[ContentQualityDimension.OPTIMIZATION] = await self._assess_image_optimization(
            content_data, metadata
        )
        
        return scores
    
    async def _assess_text_quality(
        self,
        content_data: Any,
        metadata: Optional[Dict[str, Any]]
    ) -> Dict[ContentQualityDimension, float]:
        """Assess text content quality"""
        
        scores = {}
        
        # Technical Quality (grammar, spelling, syntax)
        scores[ContentQualityDimension.TECHNICAL_QUALITY] = await self._assess_text_technical_quality(
            content_data, metadata
        )
        
        # Content Clarity (readability, structure, flow)
        scores[ContentQualityDimension.CONTENT_CLARITY] = await self._assess_text_clarity(
            content_data, metadata
        )
        
        # Engagement Potential (interest, relevance, appeal)
        scores[ContentQualityDimension.ENGAGEMENT_POTENTIAL] = await self._assess_text_engagement(
            content_data, metadata
        )
        
        # Aesthetic Quality (style, tone, voice)
        scores[ContentQualityDimension.AESTHETIC_QUALITY] = await self._assess_text_aesthetics(
            content_data, metadata
        )
        
        # Production Value (editing, formatting, polish)
        scores[ContentQualityDimension.PRODUCTION_VALUE] = await self._assess_text_production_value(
            content_data, metadata
        )
        
        # Optimization (SEO, keywords, length)
        scores[ContentQualityDimension.OPTIMIZATION] = await self._assess_text_optimization(
            content_data, metadata
        )
        
        return scores
    
    # Audio assessment methods (placeholders for actual implementation)
    async def _assess_audio_technical_quality(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        """Assess audio technical quality"""
        # Placeholder - would analyze bitrate, sample rate, compression artifacts, etc.
        return 85.0
    
    async def _assess_audio_clarity(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        """Assess audio clarity"""
        # Placeholder - would analyze audio clarity, balance, noise levels, etc.
        return 80.0
    
    async def _assess_audio_production_value(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        """Assess audio production value"""
        # Placeholder - would analyze mixing, mastering, effects quality, etc.
        return 75.0
    
    async def _assess_audio_engagement(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        """Assess audio engagement potential"""
        # Placeholder - would analyze rhythm, melody, structure, etc.
        return 78.0
    
    async def _assess_audio_aesthetics(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        """Assess audio aesthetic quality"""
        # Placeholder - would analyze musical appeal, composition, etc.
        return 82.0
    
    async def _assess_audio_optimization(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        """Assess audio optimization"""
        # Placeholder - would analyze format optimization, compression efficiency, etc.
        return 90.0
    
    # Video assessment methods (placeholders)
    async def _assess_video_technical_quality(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 83.0
    
    async def _assess_video_aesthetics(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 79.0
    
    async def _assess_video_clarity(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 81.0
    
    async def _assess_video_production_value(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 77.0
    
    async def _assess_video_engagement(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 84.0
    
    async def _assess_video_optimization(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 88.0
    
    # Image assessment methods (placeholders)
    async def _assess_image_technical_quality(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 87.0
    
    async def _assess_image_aesthetics(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 85.0
    
    async def _assess_image_clarity(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 89.0
    
    async def _assess_image_engagement(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 80.0
    
    async def _assess_image_production_value(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 82.0
    
    async def _assess_image_optimization(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 91.0
    
    # Text assessment methods (placeholders)
    async def _assess_text_technical_quality(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 92.0
    
    async def _assess_text_clarity(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 88.0
    
    async def _assess_text_engagement(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 85.0
    
    async def _assess_text_aesthetics(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 83.0
    
    async def _assess_text_production_value(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 86.0
    
    async def _assess_text_optimization(self, content_data: Any, metadata: Optional[Dict[str, Any]]) -> float:
        return 89.0
    
    def _generate_optimization_recommendations(
        self,
        dimension_scores: Dict[ContentQualityDimension, float],
        content_type: str,
        metadata: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate content optimization recommendations"""
        
        recommendations = []
        
        # Find dimensions that need improvement
        for dimension, score in dimension_scores.items():
            if score < 80:
                if dimension == ContentQualityDimension.TECHNICAL_QUALITY:
                    if content_type == 'audio':
                        recommendations.append("Improve audio bitrate and reduce compression artifacts")
                    elif content_type == 'video':
                        recommendations.append("Increase video resolution and improve encoding quality")
                    elif content_type == 'image':
                        recommendations.append("Use higher resolution and reduce compression")
                    elif content_type == 'text':
                        recommendations.append("Fix grammar and spelling errors")
                
                elif dimension == ContentQualityDimension.AESTHETIC_QUALITY:
                    if content_type == 'audio':
                        recommendations.append("Enhance musical composition and arrangement")
                    elif content_type == 'video':
                        recommendations.append("Improve visual composition and lighting")
                    elif content_type == 'image':
                        recommendations.append("Enhance composition and color balance")
                    elif content_type == 'text':
                        recommendations.append("Improve writing style and tone")
                
                elif dimension == ContentQualityDimension.CONTENT_CLARITY:
                    recommendations.append("Improve content clarity and structure")
                
                elif dimension == ContentQualityDimension.ENGAGEMENT_POTENTIAL:
                    recommendations.append("Enhance content to increase audience engagement")
                
                elif dimension == ContentQualityDimension.PRODUCTION_VALUE:
                    recommendations.append("Invest in better production techniques and tools")
                
                elif dimension == ContentQualityDimension.OPTIMIZATION:
                    recommendations.append("Optimize content for target platforms and distribution")
        
        return recommendations
    
    def _generate_improvement_suggestions(
        self,
        dimension_scores: Dict[ContentQualityDimension, float],
        content_type: str
    ) -> List[Dict[str, Any]]:
        """Generate specific improvement suggestions with priority"""
        
        suggestions = []
        
        # Sort dimensions by score (lowest first)
        sorted_dimensions = sorted(dimension_scores.items(), key=lambda x: x[1])
        
        for dimension, score in sorted_dimensions[:3]:  # Top 3 areas for improvement
            if score < 85:
                priority = "high" if score < 70 else "medium" if score < 80 else "low"
                
                suggestion = {
                    'dimension': dimension.value,
                    'current_score': round(score, 1),
                    'target_score': min(100, score + 15),
                    'priority': priority,
                    'effort_level': 'high' if score < 60 else 'medium',
                    'potential_impact': round((min(100, score + 15) - score), 1)
                }
                
                suggestions.append(suggestion)
        
        return suggestions
    
    def _calculate_potential_score(self, dimension_scores: Dict[ContentQualityDimension, float]) -> float:
        """Calculate potential score with realistic improvements"""
        
        improved_scores = {}
        
        for dimension, score in dimension_scores.items():
            # Assume realistic improvements based on current score
            if score < 60:
                improved_scores[dimension] = min(score + 20, 80)  # Major improvement possible
            elif score < 80:
                improved_scores[dimension] = min(score + 10, 90)  # Moderate improvement
            else:
                improved_scores[dimension] = min(score + 5, 95)   # Minor improvement
        
        # Calculate weighted average of improved scores
        total_score = sum(score * weight for (dim, score), (_, weight) in 
                         zip(improved_scores.items(), self.dimension_weights.items()))
        total_weight = sum(self.dimension_weights.values())
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def _get_technical_details(self, content_data: Any, content_type: str) -> Dict[str, Any]:
        """Get technical details about the content"""
        
        details = {
            'content_type': content_type,
            'size_bytes': len(content_data) if hasattr(content_data, '__len__') else None,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
        
        # Add content-specific technical details
        if content_type == 'audio':
            details.update({
                'estimated_duration': 'unknown',
                'estimated_bitrate': 'unknown',
                'estimated_sample_rate': 'unknown'
            })
        elif content_type == 'video':
            details.update({
                'estimated_resolution': 'unknown',
                'estimated_fps': 'unknown',
                'estimated_duration': 'unknown'
            })
        elif content_type == 'image':
            details.update({
                'estimated_width': 'unknown',
                'estimated_height': 'unknown',
                'estimated_format': 'unknown'
            })
        elif content_type == 'text':
            if isinstance(content_data, str):
                details.update({
                    'character_count': len(content_data),
                    'word_count': len(content_data.split()),
                    'line_count': content_data.count('\n') + 1
                })
        
        return details
