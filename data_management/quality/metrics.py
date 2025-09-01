"""Quality Metrics Engine - Advanced Quality Scoring and Analytics
==============================================================

Enterprise-grade quality metrics calculation system for multi-format content analysis.
Provides comprehensive quality scoring, trend analysis, and performance optimization metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

🔒 ULTRA-STRONG INTELLECTUAL PROPERTY WARNING 🔒
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use without explicit written permission from Fahed Mlaiel (mlaiel@live.de) 
is STRICTLY PROHIBITED and will be prosecuted under international copyright law.

Business Logic: Quality data aggregation → Multi-dimensional scoring → 
Trend analysis → Performance optimization → Business intelligence insights
"""

import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict, deque

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, and_, or_

from ..models.quality_models import QualityMetrics, QualityTrend, QualityBenchmark


class MetricType(Enum):
    """
Types of quality metrics"""

    TECHNICAL = "technical"
    AESTHETIC = "aesthetic"
    BUSINESS = "business"
    PERFORMANCE = "performance"
    COMPLIANCE = "compliance"
    USER_EXPERIENCE = "user_experience"


class AggregationMethod(Enum):
    """Methods for metric aggregation"""

    MEAN = "mean"
    MEDIAN = "median"
    WEIGHTED_AVERAGE = "weighted_average"
    PERCENTILE_90 = "percentile_90"
    MIN = "min"
    MAX = "max"
    SUM = "sum"


@dataclass
class QualityDimension:
    """Quality dimension with scoring parameters"""
    name: str
    weight: float
    min_score: float = 0.0
    max_score: float = 1.0
    aggregation_method: AggregationMethod = AggregationMethod.WEIGHTED_AVERAGE
    threshold_excellent: float = 0.9
    threshold_good: float = 0.75
    threshold_acceptable: float = 0.6


@dataclass
class MetricCalculationResult:
    """
Result of metric calculation"""
    overall_score: float
    dimension_scores: Dict[str, float]
    technical_metrics: Dict[str, Any]
    aesthetic_metrics: Dict[str, Any]
    business_metrics: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    compliance_metrics: Dict[str, Any]
    ux_metrics: Dict[str, Any]
    quality_indicators: Dict[str, Any]
    benchmarks: Dict[str, float]
    recommendations: List[str]
    confidence_score: float


class QualityMetricsEngine:
    """
    Advanced quality metrics calculation and analytics engine.
    
    Provides multi-dimensional quality scoring, trend analysis, benchmarking,
    and actionable insights for content quality optimization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Quality dimensions configuration
        self.quality_dimensions = {
            'audio': {
                'technical': QualityDimension(
                    name='technical_audio',
                    weight=0.4,
                    aggregation_method=AggregationMethod.WEIGHTED_AVERAGE
                ),
                'aesthetic': QualityDimension(
                    name='aesthetic_audio',
                    weight=0.3,
                    aggregation_method=AggregationMethod.MEAN
                ),
                'business': QualityDimension(
                    name='business_audio',
                    weight=0.2,
                    aggregation_method=AggregationMethod.WEIGHTED_AVERAGE
                ),
                'compliance': QualityDimension(
                    name='compliance_audio',
                    weight=0.1,
                    aggregation_method=AggregationMethod.MIN
                )
            },
            'video': {
                'technical': QualityDimension(
                    name='technical_video',
                    weight=0.35,
                    aggregation_method=AggregationMethod.WEIGHTED_AVERAGE
                ),
                'aesthetic': QualityDimension(
                    name='aesthetic_video',
                    weight=0.25,
                    aggregation_method=AggregationMethod.MEAN
                ),
                'performance': QualityDimension(
                    name='performance_video',
                    weight=0.2,
                    aggregation_method=AggregationMethod.WEIGHTED_AVERAGE
                ),
                'business': QualityDimension(
                    name='business_video',
                    weight=0.15,
                    aggregation_method=AggregationMethod.WEIGHTED_AVERAGE
                ),
                'compliance': QualityDimension(
                    name='compliance_video',
                    weight=0.05,
                    aggregation_method=AggregationMethod.MIN
                )
            },
            'image': {
                'technical': QualityDimension(
                    name='technical_image',
                    weight=0.3,
                    aggregation_method=AggregationMethod.WEIGHTED_AVERAGE
                ),
                'aesthetic': QualityDimension(
                    name='aesthetic_image',
                    weight=0.4,
                    aggregation_method=AggregationMethod.MEAN
                ),
                'business': QualityDimension(
                    name='business_image',
                    weight=0.2,
                    aggregation_method=AggregationMethod.WEIGHTED_AVERAGE
                ),
                'compliance': QualityDimension(
                    name='compliance_image',
                    weight=0.1,
                    aggregation_method=AggregationMethod.MIN
                )
            },
            'text': {
                'technical': QualityDimension(
                    name='technical_text',
                    weight=0.25,
                    aggregation_method=AggregationMethod.WEIGHTED_AVERAGE
                ),
                'aesthetic': QualityDimension(
                    name='aesthetic_text',
                    weight=0.2,
                    aggregation_method=AggregationMethod.MEAN
                ),
                'business': QualityDimension(
                    name='business_text',
                    weight=0.3,
                    aggregation_method=AggregationMethod.WEIGHTED_AVERAGE
                ),
                'ux': QualityDimension(
                    name='ux_text',
                    weight=0.15,
                    aggregation_method=AggregationMethod.MEAN
                ),
                'compliance': QualityDimension(
                    name='compliance_text',
                    weight=0.1,
                    aggregation_method=AggregationMethod.MIN
                )
            }
        }
        
        # Platform-specific quality benchmarks
        self.platform_benchmarks = {
            'spotify': {
                'audio_loudness_lufs': -14.0,
                'audio_dynamic_range_db': 12.0,
                'audio_quality_score': 0.85,
                'technical_compliance': 0.95
            },
            'youtube': {
                'video_resolution_score': 0.8,
                'audio_quality_score': 0.75,
                'engagement_optimization': 0.7,
                'seo_readiness': 0.8
            },
            'instagram': {
                'image_aesthetic_score': 0.85,
                'video_engagement_score': 0.75,
                'mobile_optimization': 0.9,
                'social_optimization': 0.8
            },
            'tiktok': {
                'video_engagement_score': 0.8,
                'mobile_first_score': 0.95,
                'viral_potential': 0.7,
                'trend_alignment': 0.65
            }
        }
        
        # Quality thresholds by content type
        self.quality_thresholds = {
            'professional': 0.85,
            'commercial': 0.8,
            'social_media': 0.7,
            'amateur': 0.6,
            'draft': 0.4
        }
        self.quality_dimensions = {
            'technical': QualityDimension(
                name='Technical Quality',
                weight=0.25,
                aggregation_method=AggregationMethod.WEIGHTED_AVERAGE
            ),
            'aesthetic': QualityDimension(
                name='Aesthetic Quality',
                weight=0.20,
                aggregation_method=AggregationMethod.MEAN
            ),
            'business': QualityDimension(
                name='Business Value',
                weight=0.25,
                aggregation_method=AggregationMethod.WEIGHTED_AVERAGE
            ),
            'performance': QualityDimension(
                name='Performance',
                weight=0.15,
                aggregation_method=AggregationMethod.PERCENTILE_90
            ),
            'compliance': QualityDimension(
                name='Compliance',
                weight=0.10,
                aggregation_method=AggregationMethod.MIN
            ),
            'user_experience': QualityDimension(
                name='User Experience',
                weight=0.05,
                aggregation_method=AggregationMethod.MEAN
            )
        }
        
        # Benchmark data (industry standards)
        self.benchmarks = {
            'audio': {
                'sample_rate': 44100,
                'bitrate': 320,
                'dynamic_range': 60,
                'snr_ratio': 40,
                'frequency_response': 0.95
            },
            'video': {
                'resolution': (1920, 1080),
                'fps': 30,
                'bitrate': 8000,
                'color_depth': 8,
                'compression_ratio': 0.1
            },
            'image': {
                'resolution': (1920, 1080),
                'color_depth': 8,
                'compression_quality': 0.9,
                'sharpness': 300,
                'noise_level': 0.05
            },
            'text': {
                'reading_ease': 70,
                'grade_level': 8,
                'keyword_density': 0.02,
                'engagement_score': 0.8,
                'seo_score': 0.85
            }
        }
        
        # Metric history for trend analysis
        self.metric_history = defaultdict(lambda: deque(maxlen=1000))
        
        self.logger.info("QualityMetricsEngine initialized successfully")
    
    async def calculate_quality_metrics(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        validation_results: Dict[str, Any],
        integrity_results: Dict[str, Any],
        compliance_results: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> MetricCalculationResult:
        """
        Calculate comprehensive quality metrics for content.
        
        Args:
            content_data: Content data to analyze
            content_type: Type of content
            validation_results: Validation check results
            integrity_results: Data integrity check results
            compliance_results: Compliance verification results
            context: Additional context for metric calculation
            
        Returns:
            MetricCalculationResult: Comprehensive quality metrics
        """
        try:
            self.logger.info(f"Calculating quality metrics for {content_type} content")
            
            # Calculate dimension-specific metrics
            technical_metrics = await self._calculate_technical_metrics(
                content_data, content_type, validation_results
            )
            
            aesthetic_metrics = await self._calculate_aesthetic_metrics(
                content_data, content_type, validation_results
            )
            
            business_metrics = await self._calculate_business_metrics(
                content_data, content_type, context or {}
            )
            
            performance_metrics = await self._calculate_performance_metrics(
                content_data, content_type, validation_results
            )
            
            compliance_metrics = await self._calculate_compliance_metrics(
                compliance_results, content_type
            )
            
            ux_metrics = await self._calculate_ux_metrics(
                content_data, content_type, validation_results
            )
            
            # Calculate dimension scores
            dimension_scores = {
                'technical': self._aggregate_dimension_score(
                    technical_metrics, self.quality_dimensions['technical']
                ),
                'aesthetic': self._aggregate_dimension_score(
                    aesthetic_metrics, self.quality_dimensions['aesthetic']
                ),
                'business': self._aggregate_dimension_score(
                    business_metrics, self.quality_dimensions['business']
                ),
                'performance': self._aggregate_dimension_score(
                    performance_metrics, self.quality_dimensions['performance']
                ),
                'compliance': self._aggregate_dimension_score(
                    compliance_metrics, self.quality_dimensions['compliance']
                ),
                'user_experience': self._aggregate_dimension_score(
                    ux_metrics, self.quality_dimensions['user_experience']
                )
            }
            
            # Calculate overall quality score
            overall_score = self._calculate_overall_score(dimension_scores)
            
            # Generate quality indicators
            quality_indicators = self._generate_quality_indicators(
                dimension_scores, technical_metrics, aesthetic_metrics
            )
            
            # Compare against benchmarks
            benchmarks = self._compare_to_benchmarks(
                content_type, technical_metrics, aesthetic_metrics
            )
            
            # Generate recommendations
            recommendations = self._generate_metric_recommendations(
                dimension_scores, quality_indicators, benchmarks
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                technical_metrics, validation_results, integrity_results
            )
            
            # Store metrics for trend analysis
            self._store_metric_history(content_type, overall_score, dimension_scores)
            
            result = MetricCalculationResult(
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                technical_metrics=technical_metrics,
                aesthetic_metrics=aesthetic_metrics,
                business_metrics=business_metrics,
                performance_metrics=performance_metrics,
                compliance_metrics=compliance_metrics,
                ux_metrics=ux_metrics,
                quality_indicators=quality_indicators,
                benchmarks=benchmarks,
                recommendations=recommendations,
                confidence_score=confidence_score
            )
            
            self.logger.info(f"Quality metrics calculated - Overall score: {overall_score:.3f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating quality metrics: {str(e)}")
            raise
    
    async def _calculate_technical_metrics(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        validation_results: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate technical quality metrics."""
        metrics = {}
        
        # Extract technical data from validation results
        technical_checks = validation_results.get('technical_checks', {})
        quality_metrics = validation_results.get('quality_metrics', {})
        
        if content_type == 'audio':
            # Audio technical metrics
            sample_rate = technical_checks.get('sample_rate', 0)
            metrics['sample_rate_score'] = min(1.0, sample_rate / 44100)
            
            duration = technical_checks.get('duration', 0)
            metrics['duration_score'] = 1.0 if 1 <= duration <= 3600 else 0.5
            
            snr = quality_metrics.get('snr_estimate', 0)
            metrics['signal_quality'] = min(1.0, max(0.0, (snr + 20) / 60))
            
            rms = quality_metrics.get('rms_energy', 0)
            metrics['audio_level'] = min(1.0, max(0.0, rms / 0.3))
            
        elif content_type == 'video':
            # Video technical metrics
            resolution = technical_checks.get('resolution', (0, 0))
            pixels = resolution[0] * resolution[1]
            metrics['resolution_score'] = min(1.0, pixels / (1920 * 1080))
            
            fps = technical_checks.get('fps', 0)
            metrics['framerate_score'] = min(1.0, fps / 60)
            
            sharpness = quality_metrics.get('avg_sharpness', 0)
            metrics['sharpness_score'] = min(1.0, sharpness / 500)
            
            brightness = quality_metrics.get('avg_brightness', 0)
            metrics['exposure_score'] = 1.0 - abs(brightness - 128) / 128
            
        elif content_type == 'image':
            # Image technical metrics
            resolution = technical_checks.get('resolution', (0, 0))
            pixels = resolution[0] * resolution[1]
            metrics['resolution_score'] = min(1.0, pixels / (1920 * 1080))
            
            sharpness = quality_metrics.get('sharpness', 0)
            metrics['sharpness_score'] = min(1.0, sharpness / 500)
            
            brightness = quality_metrics.get('brightness', 0)
            metrics['exposure_score'] = 1.0 - abs(brightness - 128) / 128
            
            color_variance = quality_metrics.get('color_variance', 0)
            metrics['color_quality'] = min(1.0, color_variance / 50)
            
        elif content_type == 'text':
            # Text technical metrics
            length = technical_checks.get('length', 0)
            metrics['length_score'] = min(1.0, length / 1000) if length < 1000 else 1.0
            
            word_count = technical_checks.get('word_count', 0)
            metrics['word_density'] = min(1.0, word_count / 500) if word_count < 500 else 1.0
            
            reading_ease = quality_metrics.get('reading_ease', 0)
            metrics['readability'] = min(1.0, reading_ease / 100)
            
            language_conf = 1.0 if quality_metrics.get('language') == 'en' else 0.8
            metrics['language_quality'] = language_conf
        
        # File format and size metrics (universal)
        file_size_valid = technical_checks.get('file_size_valid', False)
        metrics['file_format'] = 1.0 if file_size_valid else 0.5
        
        format_valid = technical_checks.get('format_detected', False)
        metrics['format_compatibility'] = 1.0 if format_valid else 0.0
        
        return metrics
    
    async def _calculate_aesthetic_metrics(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        validation_results: Dict[str, Any]
    ) -> Dict[str, float]:
        """
Calculate aesthetic quality metrics."""
        metrics = {}
        quality_metrics = validation_results.get('quality_metrics', {})
        
        if content_type in ['image', 'video']:
            # Visual aesthetic metrics
            sharpness = quality_metrics.get('sharpness', 0) or quality_metrics.get('avg_sharpness', 0)
            metrics['visual_clarity'] = min(1.0, sharpness / 300)
            
            brightness = quality_metrics.get('brightness', 0) or quality_metrics.get('avg_brightness', 0)
            # Optimal brightness around 128 (0-255 scale)
            brightness_score = 1.0 - abs(brightness - 128) / 128
            metrics['lighting_quality'] = max(0.0, brightness_score)
            
            color_variance = quality_metrics.get('color_variance', 0)
            metrics['color_richness'] = min(1.0, color_variance / 30)
            
            # Composition metrics (basic)
            aspect_ratio = quality_metrics.get('aspect_ratio', 1.0)
            standard_ratios = [16/9, 4/3, 1/1, 3/2, 2/3]
            closest_ratio = min(standard_ratios, key=lambda r: abs(r - aspect_ratio))
            ratio_score = 1.0 - min(0.3, abs(aspect_ratio - closest_ratio))
            metrics['composition'] = ratio_score
            
        elif content_type == 'audio':
            # Audio aesthetic metrics
            spectral_centroid = quality_metrics.get('spectral_centroid', 0)
            metrics['tonal_balance'] = min(1.0, spectral_centroid / 5000)
            
            rms_energy = quality_metrics.get('rms_energy', 0)
            metrics['dynamic_range'] = min(1.0, rms_energy / 0.2)
            
            zcr = quality_metrics.get('zero_crossing_rate', 0)
            metrics['audio_character'] = 1.0 - min(0.5, zcr * 10)
            
        elif content_type == 'text':
            # Text aesthetic metrics
            reading_ease = quality_metrics.get('reading_ease', 0)
            metrics['readability_appeal'] = min(1.0, reading_ease / 80)
            
            sentiment_ratio = quality_metrics.get('sentiment_ratio', 1.0)
            metrics['emotional_balance'] = min(1.0, sentiment_ratio / 2.0)
            
            # Style consistency (based on grammar issues)
            grammar_issues = quality_metrics.get('grammar_issues', [])
            style_score = max(0.5, 1.0 - len(grammar_issues) * 0.1)
            metrics['style_consistency'] = style_score
        
        # Content-agnostic aesthetic factors
        metrics['overall_appeal'] = np.mean(list(metrics.values())) if metrics else 0.5
        
        return metrics
    
    async def _calculate_business_metrics(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, float]:
        """
Calculate business value metrics."""
        metrics = {}
        
        # SEO potential
        if content_type == 'text':
            # Basic SEO scoring
            content_text = str(content_data) if isinstance(content_data, str) else ""
            word_count = len(content_text.split())
            
            # Optimal length for SEO (300-2000 words)
            if 300 <= word_count <= 2000:
                metrics['seo_length'] = 1.0
            elif word_count < 300:
                metrics['seo_length'] = word_count / 300
            else:
                metrics['seo_length'] = max(0.5, 2000 / word_count)
            
            # Keyword presence (if keywords provided in context)
            keywords = context.get('target_keywords', [])
            if keywords:
                keyword_score = 0.0
                for keyword in keywords:
                    if keyword.lower() in content_text.lower():
                        keyword_score += 1.0
                metrics['keyword_relevance'] = min(1.0, keyword_score / len(keywords))
        
        # Platform compatibility
        platform_scores = []
        target_platforms = context.get('target_platforms', ['general'])
        
        for platform in target_platforms:
            if platform == 'youtube' and content_type == 'video':
                platform_scores.append(0.9)
            elif platform == 'instagram' and content_type in ['image', 'video']:
                platform_scores.append(0.95)
            elif platform == 'spotify' and content_type == 'audio':
                platform_scores.append(0.95)
            elif platform == 'tiktok' and content_type == 'video':
                platform_scores.append(0.9)
            else:
                platform_scores.append(0.7)
        
        metrics['platform_compatibility'] = np.mean(platform_scores) if platform_scores else 0.7
        
        # Monetization potential
        quality_score = context.get('quality_score', 0.5)
        engagement_potential = context.get('engagement_potential', 0.5)
        metrics['monetization_potential'] = (quality_score * 0.6 + engagement_potential * 0.4)
        
        # Brand safety
        metrics['brand_safety'] = 0.9  # Default high safety score
        
        # Viral potential (heuristic)
        if content_type in ['video', 'image']:
            metrics['viral_potential'] = min(1.0, (
                metrics.get('platform_compatibility', 0.5) * 0.4 +
                quality_score * 0.3 +
                engagement_potential * 0.3
            ))
        else:
            metrics['viral_potential'] = 0.5
        
        return metrics
    
    async def _calculate_performance_metrics(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        validation_results: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate performance-related metrics."""
        metrics = {}
        technical_checks = validation_results.get('technical_checks', {})
        
        # File size efficiency
        file_size = technical_checks.get('file_size', 0)
        if content_type == 'audio':
            # Bytes per second of audio
            duration = technical_checks.get('duration', 1)
            efficiency = file_size / duration / 1024  # KB/second
            metrics['compression_efficiency'] = min(1.0, 64 / efficiency) if efficiency > 0 else 0.5
            
        elif content_type == 'video':
            # Bytes per pixel per frame
            resolution = technical_checks.get('resolution', (1, 1))
            fps = technical_checks.get('fps', 1)
            duration = technical_checks.get('duration', 1)
            
            total_pixels = resolution[0] * resolution[1] * fps * duration
            efficiency = file_size / total_pixels if total_pixels > 0 else 0
            metrics['compression_efficiency'] = min(1.0, 0.1 / efficiency) if efficiency > 0 else 0.5
            
        elif content_type == 'image':
            # Bytes per pixel
            resolution = technical_checks.get('resolution', (1, 1))
            total_pixels = resolution[0] * resolution[1]
            efficiency = file_size / total_pixels if total_pixels > 0 else 0
            metrics['compression_efficiency'] = min(1.0, 3.0 / efficiency) if efficiency > 0 else 0.5
            
        else:
            metrics['compression_efficiency'] = 0.8  # Default good efficiency
        
        # Loading speed estimation
        # Assumes 10 Mbps connection
        load_time = file_size / (10 * 1024 * 1024 / 8)  # seconds
        if load_time <= 2:
            metrics['load_speed'] = 1.0
        elif load_time <= 5:
            metrics['load_speed'] = 0.8
        elif load_time <= 10:
            metrics['load_speed'] = 0.6
        else:
            metrics['load_speed'] = 0.4
        
        # Processing speed (based on validation time)
        processing_time = validation_results.get('processing_time', 1.0)
        if processing_time <= 1:
            metrics['processing_speed'] = 1.0
        elif processing_time <= 5:
            metrics['processing_speed'] = 0.8
        else:
            metrics['processing_speed'] = max(0.3, 5 / processing_time)
        
        # Memory efficiency (estimated based on content type and size)
        if content_type in ['video', 'audio']:
            memory_score = min(1.0, 100 * 1024 * 1024 / file_size) if file_size > 0 else 1.0
        else:
            memory_score = min(1.0, 50 * 1024 * 1024 / file_size) if file_size > 0 else 1.0
        
        metrics['memory_efficiency'] = memory_score
        
        return metrics
    
    async def _calculate_compliance_metrics(
        self,
        compliance_results: Dict[str, Any],
        content_type: str
    ) -> Dict[str, float]:
        """
Calculate compliance-related metrics."""
        metrics = {}
        
        # Compliance score from results
        compliance_score = compliance_results.get('score', 1.0)
        metrics['regulatory_compliance'] = compliance_score
        
        # Violations impact
        violations = compliance_results.get('violations', [])
        violation_penalty = min(0.5, len(violations) * 0.1)
        metrics['violation_impact'] = max(0.0, 1.0 - violation_penalty)
        
        # Platform policy compliance
        platform_compliance = compliance_results.get('platform_compliance', {})
        platform_scores = []
        for platform, compliant in platform_compliance.items():
            platform_scores.append(1.0 if compliant else 0.0)
        
        metrics['platform_policy'] = np.mean(platform_scores) if platform_scores else 1.0
        
        # Copyright compliance
        copyright_score = compliance_results.get('copyright_score', 1.0)
        metrics['copyright_compliance'] = copyright_score
        
        # Privacy compliance
        privacy_score = compliance_results.get('privacy_score', 1.0)
        metrics['privacy_compliance'] = privacy_score
        
        return metrics
    
    async def _calculate_ux_metrics(
        self,
        content_data: Union[bytes, str, Dict[str, Any]],
        content_type: str,
        validation_results: Dict[str, Any]
    ) -> Dict[str, float]:
        """
Calculate user experience metrics."""
        metrics = {}
        quality_metrics = validation_results.get('quality_metrics', {})
        
        # Accessibility
        if content_type == 'text':
            reading_ease = quality_metrics.get('reading_ease', 0)
            metrics['accessibility'] = min(1.0, reading_ease / 70)
        elif content_type in ['video', 'image']:
            # Visual accessibility (contrast, clarity)
            brightness = quality_metrics.get('brightness', 0) or quality_metrics.get('avg_brightness', 0)
            contrast_score = 1.0 - abs(brightness - 128) / 128
            metrics['accessibility'] = max(0.5, contrast_score)
        else:
            metrics['accessibility'] = 0.8  # Default good accessibility
        
        # Engagement potential
        if content_type == 'audio':
            # Audio engagement based on dynamic range and quality
            rms = quality_metrics.get('rms_energy', 0)
            snr = quality_metrics.get('snr_estimate', 0)
            engagement = min(1.0, (rms * 2 + min(1.0, snr / 40)) / 3)
            metrics['engagement'] = engagement
        elif content_type in ['video', 'image']:
            # Visual engagement based on clarity and composition
            sharpness = quality_metrics.get('sharpness', 0) or quality_metrics.get('avg_sharpness', 0)
            color_var = quality_metrics.get('color_variance', 0)
            engagement = min(1.0, (sharpness / 300 + color_var / 30) / 2)
            metrics['engagement'] = engagement
        elif content_type == 'text':
            # Text engagement based on readability and sentiment
            reading_ease = quality_metrics.get('reading_ease', 0)
            sentiment = quality_metrics.get('sentiment_ratio', 1.0)
            engagement = min(1.0, (reading_ease / 100 + min(1.0, sentiment / 2)) / 2)
            metrics['engagement'] = engagement
        
        # User satisfaction (heuristic based on quality)
        overall_quality = np.mean([
            validation_results.get('score', 0.5),
            metrics.get('accessibility', 0.5),
            metrics.get('engagement', 0.5)
        ])
        metrics['satisfaction'] = overall_quality
        
        return metrics
    
    def _aggregate_dimension_score(
        self,
        metrics: Dict[str, float],
        dimension: QualityDimension
    ) -> float:
        """
Aggregate metrics into dimension score."""
        if not metrics:
            return 0.5
        
        values = list(metrics.values())
        
        if dimension.aggregation_method == AggregationMethod.MEAN:
            return np.mean(values)
        elif dimension.aggregation_method == AggregationMethod.MEDIAN:
            return np.median(values)
        elif dimension.aggregation_method == AggregationMethod.WEIGHTED_AVERAGE:
            # Equal weights for now, could be customized
            return np.mean(values)
        elif dimension.aggregation_method == AggregationMethod.PERCENTILE_90:
            return np.percentile(values, 90)
        elif dimension.aggregation_method == AggregationMethod.MIN:
            return np.min(values)
        elif dimension.aggregation_method == AggregationMethod.MAX:
            return np.max(values)
        elif dimension.aggregation_method == AggregationMethod.SUM:
            return min(1.0, np.sum(values))
        else:
            return np.mean(values)
    
    def _calculate_overall_score(self, dimension_scores: Dict[str, float]) -> float:
        """
Calculate overall quality score from dimension scores."""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for dimension_name, score in dimension_scores.items():
            if dimension_name in self.quality_dimensions:
                weight = self.quality_dimensions[dimension_name].weight
                weighted_sum += score * weight
                total_weight += weight
        
        if total_weight > 0:
            overall_score = weighted_sum / total_weight
        else:
            overall_score = np.mean(list(dimension_scores.values()))
        
        return round(overall_score, 3)
    
    def _generate_quality_indicators(
        self,
        dimension_scores: Dict[str, float],
        technical_metrics: Dict[str, float],
        aesthetic_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
Generate quality indicators and flags."""
        indicators = {}
        
        # Overall quality level
        overall_score = self._calculate_overall_score(dimension_scores)
        if overall_score >= 0.9:
            indicators['quality_level'] = 'excellent'
        elif overall_score >= 0.75:
            indicators['quality_level'] = 'good'
        elif overall_score >= 0.6:
            indicators['quality_level'] = 'acceptable'
        else:
            indicators['quality_level'] = 'poor'
        
        # Quality flags
        flags = []
        
        if dimension_scores.get('technical', 0) < 0.6:
            flags.append('technical_issues')
        if dimension_scores.get('aesthetic', 0) < 0.5:
            flags.append('aesthetic_concerns')
        if dimension_scores.get('compliance', 0) < 0.8:
            flags.append('compliance_risk')
        if dimension_scores.get('performance', 0) < 0.7:
            flags.append('performance_issues')
        
        indicators['quality_flags'] = flags
        
        # Strength indicators
        strengths = []
        if dimension_scores.get('technical', 0) >= 0.9:
            strengths.append('excellent_technical_quality')
        if dimension_scores.get('aesthetic', 0) >= 0.85:
            strengths.append('high_aesthetic_appeal')
        if dimension_scores.get('business', 0) >= 0.8:
            strengths.append('strong_business_value')
        
        indicators['strengths'] = strengths
        
        # Improvement opportunities
        improvements = []
        weak_dimensions = [name for name, score in dimension_scores.items() if score < 0.7]
        for dim in weak_dimensions:
            improvements.append(f'improve_{dim}_quality')
        
        indicators['improvement_opportunities'] = improvements
        
        return indicators
    
    def _compare_to_benchmarks(
        self,
        content_type: str,
        technical_metrics: Dict[str, float],
        aesthetic_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """
Compare metrics to industry benchmarks."""
        benchmark_scores = {}
        
        if content_type in self.benchmarks:
            benchmarks = self.benchmarks[content_type]
            
            # Technical benchmark comparisons
            if content_type == 'audio':
                if 'sample_rate_score' in technical_metrics:
                    benchmark_scores['sample_rate_benchmark'] = technical_metrics['sample_rate_score']
                if 'signal_quality' in technical_metrics:
                    benchmark_scores['signal_quality_benchmark'] = technical_metrics['signal_quality']
                    
            elif content_type == 'video':
                if 'resolution_score' in technical_metrics:
                    benchmark_scores['resolution_benchmark'] = technical_metrics['resolution_score']
                if 'framerate_score' in technical_metrics:
                    benchmark_scores['framerate_benchmark'] = technical_metrics['framerate_score']
                    
            elif content_type == 'image':
                if 'resolution_score' in technical_metrics:
                    benchmark_scores['resolution_benchmark'] = technical_metrics['resolution_score']
                if 'sharpness_score' in technical_metrics:
                    benchmark_scores['sharpness_benchmark'] = technical_metrics['sharpness_score']
                    
            elif content_type == 'text':
                if 'readability' in technical_metrics:
                    benchmark_scores['readability_benchmark'] = technical_metrics['readability']
        
        # Calculate overall benchmark score
        if benchmark_scores:
            benchmark_scores['overall_benchmark'] = np.mean(list(benchmark_scores.values()))
        else:
            benchmark_scores['overall_benchmark'] = 0.7  # Default good benchmark score
        
        return benchmark_scores
    
    def _generate_metric_recommendations(
        self,
        dimension_scores: Dict[str, float],
        quality_indicators: Dict[str, Any],
        benchmarks: Dict[str, float]
    ) -> List[str]:
        """
Generate actionable recommendations based on metrics."""
        recommendations = []
        
        # Dimension-based recommendations
        for dimension, score in dimension_scores.items():
            if score < 0.6:
                if dimension == 'technical':
                    recommendations.append("Improve technical specifications (resolution, bitrate, format)")
                elif dimension == 'aesthetic':
                    recommendations.append("Enhance visual/audio appeal and composition")
                elif dimension == 'business':
                    recommendations.append("Optimize for target platforms and SEO")
                elif dimension == 'performance':
                    recommendations.append("Optimize file size and compression settings")
                elif dimension == 'compliance':
                    recommendations.append("Address compliance and policy violations")
                elif dimension == 'user_experience':
                    recommendations.append("Improve accessibility and engagement factors")
        
        # Quality level recommendations
        quality_level = quality_indicators.get('quality_level', 'poor')
        if quality_level == 'poor':
            recommendations.append("Consider significant quality improvements before publication")
        elif quality_level == 'acceptable':
            recommendations.append("Minor enhancements could significantly improve quality")
        
        # Benchmark recommendations
        overall_benchmark = benchmarks.get('overall_benchmark', 0.7)
        if overall_benchmark < 0.7:
            recommendations.append("Content is below industry standards - consider professional enhancement")
        
        # Flag-based recommendations
        flags = quality_indicators.get('quality_flags', [])
        if 'technical_issues' in flags:
            recommendations.append("Address technical quality issues before publication")
        if 'compliance_risk' in flags:
            recommendations.append("Review and fix compliance violations")
        if 'performance_issues' in flags:
            recommendations.append("Optimize for better performance and user experience")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _calculate_confidence_score(
        self,
        technical_metrics: Dict[str, float],
        validation_results: Dict[str, Any],
        integrity_results: Dict[str, Any]
    ) -> float:
        """Calculate confidence score in the quality assessment."""
        confidence_factors = []
        
        # Data completeness
        if technical_metrics:
            confidence_factors.append(min(1.0, len(technical_metrics) / 5))
        
        # Validation success
        validation_score = validation_results.get('score', 0.5)
        confidence_factors.append(validation_score)
        
        # Integrity verification
        integrity_score = integrity_results.get('score', 0.5)
        confidence_factors.append(integrity_score)
        
        # Error absence
        issues = validation_results.get('issues', [])
        error_penalty = min(0.3, len(issues) * 0.05)
        confidence_factors.append(max(0.5, 1.0 - error_penalty))
        
        return round(np.mean(confidence_factors), 3) if confidence_factors else 0.7
    
    def _store_metric_history(
        self,
        content_type: str,
        overall_score: float,
        dimension_scores: Dict[str, float]
    ):
        """
Store metrics for trend analysis."""
        timestamp = datetime.utcnow()
        
        # Store overall score
        self.metric_history[f'{content_type}_overall'].append({
            'timestamp': timestamp,
            'score': overall_score
        })
        
        # Store dimension scores
        for dimension, score in dimension_scores.items():
            self.metric_history[f'{content_type}_{dimension}'].append({
                'timestamp': timestamp,
                'score': score
            })
    
    async def get_quality_trends(
        self,
        content_type: Optional[str] = None,
        dimension: Optional[str] = None,
        timeframe: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
Get quality trends and analysis."""
        trends = {}
        cutoff_time = datetime.utcnow() - timeframe
        
        # Filter relevant metrics
        if content_type and dimension:
            key = f'{content_type}_{dimension}'
            if key in self.metric_history:
                recent_data = [
                    entry for entry in self.metric_history[key]
                    if entry['timestamp'] >= cutoff_time
                ]
                trends[key] = self._analyze_trend(recent_data)
        else:
            # Analyze all available trends
            for key, data in self.metric_history.items():
                recent_data = [
                    entry for entry in data
                    if entry['timestamp'] >= cutoff_time
                ]
                if recent_data:
                    trends[key] = self._analyze_trend(recent_data)
        
        return trends
    
    def _analyze_trend(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
Analyze trend from historical data."""
        if len(data) < 2:
            return {'trend': 'insufficient_data', 'direction': 'unknown'}
        
        scores = [entry['score'] for entry in data]
        timestamps = [entry['timestamp'] for entry in data]
        
        # Calculate trend direction
        recent_avg = np.mean(scores[-5:]) if len(scores) >= 5 else np.mean(scores)
        older_avg = np.mean(scores[:5]) if len(scores) >= 10 else np.mean(scores[:-5]) if len(scores) > 5 else recent_avg
        
        trend_direction = 'improving' if recent_avg > older_avg else 'declining' if recent_avg < older_avg else 'stable'
        
        # Calculate trend strength
        if len(scores) > 1:
            trend_strength = abs(recent_avg - older_avg)
        else:
            trend_strength = 0.0
        
        return {
            'trend': trend_direction,
            'strength': trend_strength,
            'current_avg': recent_avg,
            'previous_avg': older_avg,
            'data_points': len(data),
            'min_score': min(scores),
            'max_score': max(scores),
            'std_dev': np.std(scores)
        }


class ContentQualityScorer:
    """
    Specialized content quality scoring engine for IA Influencer platform.
    
    Provides content-type specific scoring algorithms optimized for creators
    across music, video, image, and text content with platform-specific optimizations.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.ContentQualityScorer")
        
        # Content-specific scoring weights
        self.scoring_weights = {
            'audio_music': {
                'technical_quality': 0.35,
                'audio_clarity': 0.25,
                'dynamic_range': 0.15,
                'frequency_balance': 0.15,
                'platform_compliance': 0.1
            },
            'video_content': {
                'video_quality': 0.3,
                'audio_quality': 0.2,
                'visual_composition': 0.2,
                'engagement_factors': 0.15,
                'platform_optimization': 0.15
            },
            'image_photo': {
                'technical_quality': 0.3,
                'aesthetic_quality': 0.35,
                'composition': 0.2,
                'platform_optimization': 0.15
            },
            'text_content': {
                'readability': 0.25,
                'seo_optimization': 0.25,
                'content_quality': 0.25,
                'engagement_potential': 0.15,
                'platform_compliance': 0.1
            }
        }
    
    async def calculate_content_score(
        self,
        content_type: str,
        quality_metrics: Dict[str, Any],
        platform_target: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive content quality score."""
        try:
            scorer_method = getattr(self, f'_score_{content_type}', None)
            if not scorer_method:
                return self._score_generic(quality_metrics)
            
            score_result = await scorer_method(quality_metrics, platform_target)
            
            # Add platform-specific adjustments
            if platform_target:
                score_result = self._apply_platform_adjustments(
                    score_result, platform_target, content_type
                )
            
            return score_result
            
        except Exception as e:
            self.logger.error(f"Content scoring failed: {str(e)}")
            return {
                'overall_score': 0.5,
                'error': f'Scoring failed: {str(e)}'
            }
    
    async def _score_audio_music(
        self,
        metrics: Dict[str, Any],
        platform_target: Optional[str] = None
    ) -> Dict[str, Any]:
        """Score audio/music content quality."""
        scores = {}
        weights = self.scoring_weights['audio_music']
        
        # Technical quality scoring
        technical_score = 0.0
        if 'sample_rate' in metrics:
            sr = metrics['sample_rate']
            technical_score += min(1.0, max(0.0, (sr - 22050) / (96000 - 22050))) * 0.3
        
        if 'snr_estimate' in metrics:
            snr = metrics['snr_estimate']
            technical_score += min(1.0, max(0.0, (snr - 20) / 40)) * 0.4
        
        if 'dynamic_range_db' in metrics:
            dr = metrics['dynamic_range_db']
            technical_score += min(1.0, max(0.0, (dr - 6) / 30)) * 0.3
        
        scores['technical_quality'] = technical_score
        
        # Audio clarity scoring
        clarity_score = 0.0
        if 'clipping_percentage' in metrics:
            clipping = metrics['clipping_percentage']
            clarity_score += max(0.0, 1.0 - (clipping * 20)) * 0.4
        
        if 'frequency_bandwidth' in metrics:
            bandwidth = metrics['frequency_bandwidth']
            clarity_score += min(1.0, max(0.0, (bandwidth - 1000) / 19000)) * 0.6
        
        scores['audio_clarity'] = clarity_score
        
        # Dynamic range scoring
        dr_score = 0.0
        if 'dynamic_range_db' in metrics:
            dr = metrics['dynamic_range_db']
            # Optimal dynamic range is 12-20 dB for music
            if 12 <= dr <= 20:
                dr_score = 1.0
            elif dr > 20:
                dr_score = max(0.5, 1.0 - (dr - 20) / 20)
            else:
                dr_score = max(0.0, dr / 12)
        
        scores['dynamic_range'] = dr_score
        
        # Frequency balance scoring
        freq_score = 0.5  # Default
        if 'spectral_centroid_mean' in metrics:
            centroid = metrics['spectral_centroid_mean']
            # Good spectral centroid for music: 1000-4000 Hz
            if 1000 <= centroid <= 4000:
                freq_score = 1.0
            else:
                freq_score = max(0.3, 1.0 - abs(centroid - 2500) / 2500)
        
        scores['frequency_balance'] = freq_score
        
        # Platform compliance scoring
        compliance_score = 1.0  # Default full compliance
        if platform_target == 'spotify' and 'rms_db' in metrics:
            loudness = metrics['rms_db']
            # Spotify targets -14 LUFS
            target_loudness = -14.0
            compliance_score = max(0.5, 1.0 - abs(loudness - target_loudness) / 10)
        
        scores['platform_compliance'] = compliance_score
        
        # Calculate weighted overall score
        overall_score = sum(scores[key] * weights[key] for key in scores.keys() if key in weights)
        
        return {
            'overall_score': overall_score,
            'component_scores': scores,
            'quality_level': self._get_quality_level(overall_score),
            'optimization_suggestions': self._get_audio_optimization_suggestions(scores, metrics)
        }
    
    async def _score_video_content(
        self,
        metrics: Dict[str, Any],
        platform_target: Optional[str] = None
    ) -> Dict[str, Any]:
        """
Score video content quality."""
        scores = {}
        weights = self.scoring_weights['video_content']
        
        # Video quality scoring
        video_score = 0.0
        if 'avg_sharpness' in metrics:
            sharpness = metrics['avg_sharpness']
            video_score += min(1.0, max(0.0, (sharpness - 50) / 450)) * 0.4
        
        if 'resolution_width' in metrics and 'resolution_height' in metrics:
            width = metrics['resolution_width']
            height = metrics['resolution_height']
            pixel_count = width * height
            
            # Score based on resolution
            if pixel_count >= 1920 * 1080:  # 1080p+
                resolution_score = 1.0
            elif pixel_count >= 1280 * 720:  # 720p
                resolution_score = 0.8
            elif pixel_count >= 854 * 480:  # 480p
                resolution_score = 0.6
            else:
                resolution_score = 0.4
            
            video_score += resolution_score * 0.3
        
        if 'avg_contrast' in metrics:
            contrast = metrics['avg_contrast']
            video_score += min(1.0, max(0.0, (contrast - 10) / 80)) * 0.3
        
        scores['video_quality'] = video_score
        
        # Audio quality scoring (for video)
        audio_score = 0.5  # Default if no audio metrics
        if 'has_audio' in metrics and metrics['has_audio']:
            # Simplified audio scoring for video
            if 'snr_estimate' in metrics:
                snr = metrics['snr_estimate']
                audio_score = min(1.0, max(0.3, (snr - 15) / 35))
        
        scores['audio_quality'] = audio_score
        
        # Visual composition scoring
        composition_score = 0.0
        if 'edge_density' in metrics:
            edge_density = metrics['edge_density']
            # Good composition has moderate edge density
            optimal_density = 0.15
            composition_score += max(0.0, 1.0 - abs(edge_density - optimal_density) / optimal_density) * 0.5
        
        if 'aspect_ratio' in metrics:
            aspect_ratio = metrics['aspect_ratio']
            # Score based on common aspect ratios
            standard_ratios = [16/9, 4/3, 1/1, 9/16]
            ratio_scores = [max(0.0, 1.0 - abs(aspect_ratio - ratio) / ratio) for ratio in standard_ratios]
            composition_score += max(ratio_scores) * 0.5
        
        scores['visual_composition'] = composition_score
        
        # Engagement factors scoring
        engagement_score = 0.7  # Default good engagement potential
        if 'duration_seconds' in metrics:
            duration = metrics['duration_seconds']
            # Optimal duration depends on platform
            if platform_target == 'tiktok':
                optimal_duration = 30  # 15-60 seconds optimal for TikTok
                engagement_score = max(0.5, 1.0 - abs(duration - optimal_duration) / optimal_duration)
            elif platform_target == 'youtube':
                # YouTube: 2-10 minutes optimal
                if 120 <= duration <= 600:
                    engagement_score = 1.0
                else:
                    engagement_score = max(0.6, 1.0 - abs(duration - 300) / 300)
        
        scores['engagement_factors'] = engagement_score
        
        # Platform optimization scoring
        platform_score = 1.0  # Default full optimization
        if platform_target:
            if platform_target == 'instagram' and 'aspect_ratio' in metrics:
                aspect_ratio = metrics['aspect_ratio']
                # Instagram prefers 1:1, 4:5, or 9:16
                instagram_ratios = [1.0, 0.8, 9/16]
                ratio_scores = [max(0.0, 1.0 - abs(aspect_ratio - ratio) / ratio) for ratio in instagram_ratios]
                platform_score = max(ratio_scores)
        
        scores['platform_optimization'] = platform_score
        
        # Calculate weighted overall score
        overall_score = sum(scores[key] * weights[key] for key in scores.keys() if key in weights)
        
        return {
            'overall_score': overall_score,
            'component_scores': scores,
            'quality_level': self._get_quality_level(overall_score),
            'optimization_suggestions': self._get_video_optimization_suggestions(scores, metrics, platform_target)
        }
    
    async def _score_image_photo(
        self,
        metrics: Dict[str, Any],
        platform_target: Optional[str] = None
    ) -> Dict[str, Any]:
        """
Score image/photo content quality."""
        scores = {}
        weights = self.scoring_weights['image_photo']
        
        # Technical quality scoring
        technical_score = 0.0
        if 'sharpness' in metrics:
            sharpness = metrics['sharpness']
            technical_score += min(1.0, max(0.0, (sharpness - 10) / 490)) * 0.4
        
        if 'pixel_count' in metrics:
            pixel_count = metrics['pixel_count']
            # Score based on resolution
            if pixel_count >= 1920 * 1080:  # 2MP+
                resolution_score = 1.0
            elif pixel_count >= 1280 * 720:  # 0.9MP
                resolution_score = 0.8
            else:
                resolution_score = max(0.4, pixel_count / (1920 * 1080))
            
            technical_score += resolution_score * 0.3
        
        if 'noise_level' in metrics:
            noise = metrics['noise_level']
            technical_score += max(0.0, 1.0 - (noise * 10)) * 0.3
        
        scores['technical_quality'] = technical_score
        
        # Aesthetic quality scoring
        aesthetic_score = 0.0
        if 'contrast' in metrics:
            contrast = metrics['contrast']
            aesthetic_score += min(1.0, max(0.0, (contrast - 10) / 80)) * 0.3
        
        if 'brightness' in metrics:
            brightness = metrics['brightness']
            # Optimal brightness: 100-180 (on 0-255 scale)
            optimal_brightness = 140
            aesthetic_score += max(0.0, 1.0 - abs(brightness - optimal_brightness) / optimal_brightness) * 0.3
        
        if 'color_variance' in metrics:
            color_var = metrics['color_variance']
            # Good color variance indicates rich colors
            aesthetic_score += min(1.0, max(0.0, color_var / 10000)) * 0.4
        
        scores['aesthetic_quality'] = aesthetic_score
        
        # Composition scoring
        composition_score = 0.0
        if 'edge_density' in metrics:
            edge_density = metrics['edge_density']
            # Good composition has balanced edge density
            optimal_density = 0.1
            composition_score += max(0.0, 1.0 - abs(edge_density - optimal_density) / optimal_density) * 0.5
        
        if 'aspect_ratio' in metrics:
            aspect_ratio = metrics['aspect_ratio']
            # Score based on common photographic ratios
            photo_ratios = [3/2, 4/3, 16/9, 1/1]
            ratio_scores = [max(0.0, 1.0 - abs(aspect_ratio - ratio) / ratio) for ratio in photo_ratios]
            composition_score += max(ratio_scores) * 0.5
        
        scores['composition'] = composition_score
        
        # Platform optimization scoring
        platform_score = 1.0  # Default
        if platform_target == 'instagram' and 'aspect_ratio' in metrics:
            aspect_ratio = metrics['aspect_ratio']
            # Instagram prefers 1:1 or 4:5
            if abs(aspect_ratio - 1.0) < 0.1:  # Square
                platform_score = 1.0
            elif abs(aspect_ratio - 0.8) < 0.1:  # 4:5
                platform_score = 0.95
            else:
                platform_score = 0.7
        
        scores['platform_optimization'] = platform_score
        
        # Calculate weighted overall score
        overall_score = sum(scores[key] * weights[key] for key in scores.keys() if key in weights)
        
        return {
            'overall_score': overall_score,
            'component_scores': scores,
            'quality_level': self._get_quality_level(overall_score),
            'optimization_suggestions': self._get_image_optimization_suggestions(scores, metrics, platform_target)
        }
    
    async def _score_text_content(
        self,
        metrics: Dict[str, Any],
        platform_target: Optional[str] = None
    ) -> Dict[str, Any]:
        """
Score text content quality."""
        scores = {}
        weights = self.scoring_weights['text_content']
        
        # Readability scoring
        readability_score = 0.0
        if 'reading_ease' in metrics:
            reading_ease = metrics['reading_ease']
            # Target reading ease: 60-80 (fairly easy to read)
            if 60 <= reading_ease <= 80:
                readability_score += 1.0 * 0.6
            else:
                readability_score += max(0.3, 1.0 - abs(reading_ease - 70) / 70) * 0.6
        
        if 'grade_level' in metrics:
            grade_level = metrics['grade_level']
            # Target grade level: 8-12
            if 8 <= grade_level <= 12:
                readability_score += 1.0 * 0.4
            else:
                readability_score += max(0.3, 1.0 - abs(grade_level - 10) / 10) * 0.4
        
        scores['readability'] = readability_score
        
        # SEO optimization scoring
        seo_score = 0.5  # Default
        if 'keyword_density' in metrics:
            # Check if keyword densities are in optimal range (0.5-3%)
            keyword_densities = metrics['keyword_density']
            if isinstance(keyword_densities, dict):
                density_scores = []
                for keyword, density in keyword_densities.items():
                    if 0.005 <= density <= 0.03:  # 0.5-3%
                        density_scores.append(1.0)
                    else:
                        density_scores.append(max(0.0, 1.0 - abs(density - 0.015) / 0.015))
                
                if density_scores:
                    seo_score = np.mean(density_scores)
        
        scores['seo_optimization'] = seo_score
        
        # Content quality scoring
        content_score = 0.0
        if 'word_count' in metrics:
            word_count = metrics['word_count']
            # Optimal word count varies by platform/purpose
            if platform_target == 'twitter':
                optimal_words = 20  # Short and punchy
                content_score += max(0.5, 1.0 - abs(word_count - optimal_words) / optimal_words) * 0.3
            else:
                # General content: 300-1500 words optimal
                if 300 <= word_count <= 1500:
                    content_score += 1.0 * 0.3
                else:
                    content_score += max(0.5, 1.0 - abs(word_count - 900) / 900) * 0.3
        
        if 'lexical_diversity' in metrics:
            diversity = metrics['lexical_diversity']
            content_score += min(1.0, diversity / 0.7) * 0.4
        
        if 'sentence_variety' in metrics:
            variety = metrics['sentence_variety']
            content_score += min(1.0, variety / 0.5) * 0.3
        
        scores['content_quality'] = content_score
        
        # Engagement potential scoring
        engagement_score = 0.5  # Default
        if 'passive_voice_ratio' in metrics:
            passive_ratio = metrics['passive_voice_ratio']
            # Lower passive voice = higher engagement
            engagement_score += max(0.0, 1.0 - (passive_ratio / 0.3)) * 0.4
        
        if 'named_entities_count' in metrics:
            entities = metrics['named_entities_count']
            # Presence of named entities can increase engagement
            engagement_score += min(0.6, entities / 10) * 0.6
        
        scores['engagement_potential'] = engagement_score
        
        # Platform compliance scoring
        compliance_score = 1.0  # Default full compliance
        if 'detected_language' in metrics:
            language = metrics['detected_language']
            # Most platforms prefer English content
            if language in ['en', 'english']:
                compliance_score = 1.0
            else:
                compliance_score = 0.8  # Still good but may have limited reach
        
        scores['platform_compliance'] = compliance_score
        
        # Calculate weighted overall score
        overall_score = sum(scores[key] * weights[key] for key in scores.keys() if key in weights)
        
        return {
            'overall_score': overall_score,
            'component_scores': scores,
            'quality_level': self._get_quality_level(overall_score),
            'optimization_suggestions': self._get_text_optimization_suggestions(scores, metrics, platform_target)
        }
    
    def _score_generic(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
Generic scoring for unknown content types."""
        # Simple scoring based on available metrics
        score = 0.5  # Default neutral score
        
        if 'overall_quality_score' in metrics:
            score = metrics['overall_quality_score']
        elif 'quality_score' in metrics:
            score = metrics['quality_score']
        
        return {
            'overall_score': score,
            'component_scores': {'generic': score},
            'quality_level': self._get_quality_level(score),
            'optimization_suggestions': ['Content type not recognized - please verify format']
        }
    
    def _apply_platform_adjustments(
        self,
        score_result: Dict[str, Any],
        platform_target: str,
        content_type: str
    ) -> Dict[str, Any]:
        """
Apply platform-specific scoring adjustments."""
        # Platform-specific bonuses/penalties
        platform_adjustments = {
            'spotify': {
                'audio_music': {'technical_quality': 0.1, 'platform_compliance': 0.15}
            },
            'youtube': {
                'video_content': {'engagement_factors': 0.1, 'platform_optimization': 0.1}
            },
            'instagram': {
                'image_photo': {'aesthetic_quality': 0.15, 'platform_optimization': 0.1},
                'video_content': {'visual_composition': 0.1, 'engagement_factors': 0.1}
            },
            'tiktok': {
                'video_content': {'engagement_factors': 0.2, 'platform_optimization': 0.15}
            }
        }
        
        if platform_target in platform_adjustments:
            if content_type in platform_adjustments[platform_target]:
                adjustments = platform_adjustments[platform_target][content_type]
                
                # Apply adjustments to component scores
                for component, bonus in adjustments.items():
                    if component in score_result['component_scores']:
                        original_score = score_result['component_scores'][component]
                        adjusted_score = min(1.0, original_score + bonus)
                        score_result['component_scores'][component] = adjusted_score
                
                # Recalculate overall score
                weights = self.scoring_weights.get(content_type, {})
                if weights:
                    overall_score = sum(
                        score_result['component_scores'][key] * weights[key] 
                        for key in score_result['component_scores'].keys() 
                        if key in weights
                    )
                    score_result['overall_score'] = overall_score
                    score_result['quality_level'] = self._get_quality_level(overall_score)
        
        return score_result
    
    def _get_quality_level(self, score: float) -> str:
        """
Convert numerical score to quality level."""
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.8:
            return 'very_good'
        elif score >= 0.7:
            return 'good'
        elif score >= 0.6:
            return 'acceptable'
        elif score >= 0.4:
            return 'needs_improvement'
        else:
            return 'poor'
    
    def _get_audio_optimization_suggestions(
        self,
        scores: Dict[str, float],
        metrics: Dict[str, Any]
    ) -> List[str]:
        """
Generate audio-specific optimization suggestions."""
        suggestions = []
        
        if scores.get('technical_quality', 0) < 0.7:
            suggestions.append("Improve audio technical quality: use higher sample rate (44.1kHz+) and bit depth")
        
        if scores.get('audio_clarity', 0) < 0.7:
            suggestions.append("Enhance audio clarity: reduce noise and extend frequency range")
        
        if scores.get('dynamic_range', 0) < 0.7:
            suggestions.append("Improve dynamic range: avoid over-compression and maintain 12+ dB dynamic range")
        
        if 'clipping_percentage' in metrics and metrics['clipping_percentage'] > 0.01:
            suggestions.append("Reduce clipping: lower recording levels or use limiting properly")
        
        return suggestions
    
    def _get_video_optimization_suggestions(
        self,
        scores: Dict[str, float],
        metrics: Dict[str, Any],
        platform_target: Optional[str] = None
    ) -> List[str]:
        """Generate video-specific optimization suggestions."""
        suggestions = []
        
        if scores.get('video_quality', 0) < 0.7:
            suggestions.append("Improve video quality: increase resolution to 1080p+ and enhance sharpness")
        
        if scores.get('visual_composition', 0) < 0.7:
            suggestions.append("Enhance visual composition: improve framing and use standard aspect ratios")
        
        if platform_target == 'tiktok' and 'duration_seconds' in metrics:
            duration = metrics['duration_seconds']
            if duration > 60:
                suggestions.append("For TikTok: shorten video to 15-60 seconds for better engagement")
        
        if platform_target == 'instagram' and 'aspect_ratio' in metrics:
            aspect_ratio = metrics['aspect_ratio']
            if abs(aspect_ratio - 1.0) > 0.2:
                suggestions.append("For Instagram: use square (1:1) or portrait (4:5) aspect ratio")
        
        return suggestions
    
    def _get_image_optimization_suggestions(
        self,
        scores: Dict[str, float],
        metrics: Dict[str, Any],
        platform_target: Optional[str] = None
    ) -> List[str]:
        """Generate image-specific optimization suggestions."""
        suggestions = []
        
        if scores.get('technical_quality', 0) < 0.7:
            suggestions.append("Improve image technical quality: increase resolution and reduce noise")
        
        if scores.get('aesthetic_quality', 0) < 0.7:
            suggestions.append("Enhance aesthetic quality: improve contrast, brightness, and color balance")
        
        if 'sharpness' in metrics and metrics['sharpness'] < 100:
            suggestions.append("Increase image sharpness: use proper focus and avoid motion blur")
        
        if platform_target == 'instagram' and 'aspect_ratio' in metrics:
            aspect_ratio = metrics['aspect_ratio']
            if abs(aspect_ratio - 1.0) > 0.1:
                suggestions.append("For Instagram: use square (1:1) format for optimal display")
        
        return suggestions
    
    def _get_text_optimization_suggestions(
        self,
        scores: Dict[str, float],
        metrics: Dict[str, Any],
        platform_target: Optional[str] = None
    ) -> List[str]:
        """Generate text-specific optimization suggestions."""
        suggestions = []
        
        if scores.get('readability', 0) < 0.7:
            suggestions.append("Improve readability: use shorter sentences and simpler vocabulary")
        
        if scores.get('seo_optimization', 0) < 0.7:
            suggestions.append("Optimize for SEO: include target keywords with 0.5-3% density")
        
        if scores.get('engagement_potential', 0) < 0.7:
            suggestions.append("Increase engagement: use active voice and include specific details/names")
        
        if 'passive_voice_ratio' in metrics and metrics['passive_voice_ratio'] > 0.3:
            suggestions.append("Reduce passive voice: use active voice for more engaging content")
        
        return suggestions


class PerformanceMetricsCalculator:
    """
    Performance metrics calculator for system and content processing performance.
    
    Monitors processing speed, resource utilization, throughput, and system efficiency
    for the IA Influencer platform quality management system.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.PerformanceMetricsCalculator")
        
        # Performance tracking
        self.processing_times = defaultdict(list)
        self.throughput_metrics = defaultdict(list)
        self.resource_usage = defaultdict(list)
        
        # Performance thresholds
        self.performance_thresholds = {
            'audio_processing_time': 30.0,  # seconds per minute of audio
            'video_processing_time': 120.0,  # seconds per minute of video
            'image_processing_time': 5.0,  # seconds per image
            'text_processing_time': 1.0,  # seconds per 1000 words
            'max_memory_usage': 0.8,  # 80% of available memory
            'max_cpu_usage': 0.9,  # 90% CPU utilization
            'min_throughput': 10.0  # items per minute
        }
    
    async def calculate_performance_metrics(
        self,
        content_type: str,
        processing_time: float,
        content_size: int,
        resource_usage: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        try:
            metrics = {}
            current_time = datetime.now()
            
            # Processing efficiency
            efficiency_score = self._calculate_processing_efficiency(
                content_type, processing_time, content_size
            )
            metrics['processing_efficiency'] = efficiency_score
            
            # Throughput calculation
            throughput = self._calculate_throughput(content_type, processing_time)
            metrics['throughput'] = throughput
            
            # Resource utilization
            if resource_usage:
                resource_metrics = self._calculate_resource_metrics(resource_usage)
                metrics.update(resource_metrics)
            
            # Performance trend analysis
            trend_metrics = self._analyze_performance_trends(content_type)
            metrics.update(trend_metrics)
            
            # Overall performance score
            overall_score = self._calculate_overall_performance_score(metrics)
            metrics['overall_performance_score'] = overall_score
            
            # Store metrics for trend analysis
            self._store_performance_data(content_type, metrics, current_time)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Performance metrics calculation failed: {str(e)}")
            return {'error': f'Performance calculation failed: {str(e)}'}
    
    def _calculate_processing_efficiency(
        self,
        content_type: str,
        processing_time: float,
        content_size: int
    ) -> float:
        """Calculate processing efficiency score."""
        threshold_key = f'{content_type}_processing_time'
        if threshold_key not in self.performance_thresholds:
            return 0.8  # Default good efficiency
        
        threshold = self.performance_thresholds[threshold_key]
        
        # Normalize processing time based on content size
        if content_type == 'audio':
            # Assume content_size is duration in seconds
            normalized_time = processing_time / (content_size / 60.0)  # per minute
        elif content_type == 'video':
            # Assume content_size is duration in seconds
            normalized_time = processing_time / (content_size / 60.0)  # per minute
        elif content_type == 'text':
            # Assume content_size is word count
            normalized_time = processing_time / (content_size / 1000.0)  # per 1000 words
        else:
            # For images and other types
            normalized_time = processing_time
        
        # Calculate efficiency score (lower time = higher efficiency)
        efficiency = max(0.1, min(1.0, threshold / max(normalized_time, 0.1)))
        
        return efficiency
    
    def _calculate_throughput(self, content_type: str, processing_time: float) -> float:
        """
Calculate processing throughput."""
        if processing_time <= 0:
            return 0.0
        
        # Items per minute
        throughput = 60.0 / processing_time
        
        # Store for trend analysis
        self.throughput_metrics[content_type].append({
            'throughput': throughput,
            'timestamp': datetime.now()
        })
        
        # Keep only recent data (last 100 entries)
        if len(self.throughput_metrics[content_type]) > 100:
            self.throughput_metrics[content_type] = self.throughput_metrics[content_type][-100:]
        
        return throughput
    
    def _calculate_resource_metrics(self, resource_usage: Dict[str, Any]) -> Dict[str, Any]:
        """
Calculate resource utilization metrics."""
        metrics = {}
        
        # CPU utilization
        if 'cpu_percent' in resource_usage:
            cpu_usage = resource_usage['cpu_percent'] / 100.0
            metrics['cpu_utilization'] = cpu_usage
            metrics['cpu_efficiency'] = max(0.0, 1.0 - max(0.0, cpu_usage - 0.7) / 0.3)
        
        # Memory utilization
        if 'memory_percent' in resource_usage:
            memory_usage = resource_usage['memory_percent'] / 100.0
            metrics['memory_utilization'] = memory_usage
            metrics['memory_efficiency'] = max(0.0, 1.0 - max(0.0, memory_usage - 0.6) / 0.4)
        
        # Disk I/O
        if 'disk_io' in resource_usage:
            disk_io = resource_usage['disk_io']
            metrics['disk_io_rate'] = disk_io
        
        # Network I/O
        if 'network_io' in resource_usage:
            network_io = resource_usage['network_io']
            metrics['network_io_rate'] = network_io
        
        return metrics
    
    def _analyze_performance_trends(self, content_type: str) -> Dict[str, Any]:
        """
Analyze performance trends for the content type."""
        trends = {}
        
        # Recent throughput trend
        if content_type in self.throughput_metrics:
            recent_throughput = self.throughput_metrics[content_type][-10:]  # Last 10 measurements
            if len(recent_throughput) >= 3:
                throughput_values = [entry['throughput'] for entry in recent_throughput]
                
                trends['avg_throughput'] = np.mean(throughput_values)
                trends['throughput_trend'] = self._calculate_trend_direction(throughput_values)
                trends['throughput_stability'] = 1.0 - (np.std(throughput_values) / max(np.mean(throughput_values), 1.0))
        
        # Processing time trend
        if content_type in self.processing_times:
            recent_times = self.processing_times[content_type][-10:]
            if len(recent_times) >= 3:
                time_values = [entry['time'] for entry in recent_times]
                
                trends['avg_processing_time'] = np.mean(time_values)
                trends['processing_time_trend'] = self._calculate_trend_direction(time_values, reverse=True)  # Lower is better
                trends['processing_time_stability'] = 1.0 - (np.std(time_values) / max(np.mean(time_values), 1.0))
        
        return trends
    
    def _calculate_trend_direction(self, values: List[float], reverse: bool = False) -> str:
        """
Calculate trend direction from a series of values."""
        if len(values) < 2:
            return 'stable'
        
        # Simple linear trend
        x = list(range(len(values)))
        trend_slope = np.corrcoef(x, values)[0, 1] if len(values) > 2 else (values[-1] - values[0])
        
        if reverse:
            trend_slope = -trend_slope
        
        if trend_slope > 0.1:
            return 'improving'
        elif trend_slope < -0.1:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_overall_performance_score(self, metrics: Dict[str, Any]) -> float:
        """
Calculate overall performance score."""
        score_components = []
        
        # Processing efficiency (40% weight)
        if 'processing_efficiency' in metrics:
            score_components.append(metrics['processing_efficiency'] * 0.4)
        
        # Resource efficiency (30% weight)
        resource_scores = []
        if 'cpu_efficiency' in metrics:
            resource_scores.append(metrics['cpu_efficiency'])
        if 'memory_efficiency' in metrics:
            resource_scores.append(metrics['memory_efficiency'])
        
        if resource_scores:
            avg_resource_efficiency = np.mean(resource_scores)
            score_components.append(avg_resource_efficiency * 0.3)
        
        # Throughput score (20% weight)
        if 'throughput' in metrics:
            throughput = metrics['throughput']
            min_threshold = self.performance_thresholds['min_throughput']
            throughput_score = min(1.0, throughput / min_threshold)
            score_components.append(throughput_score * 0.2)
        
        # Stability score (10% weight)
        stability_scores = []
        if 'throughput_stability' in metrics:
            stability_scores.append(metrics['throughput_stability'])
        if 'processing_time_stability' in metrics:
            stability_scores.append(metrics['processing_time_stability'])
        
        if stability_scores:
            avg_stability = np.mean(stability_scores)
            score_components.append(avg_stability * 0.1)
        
        return sum(score_components) if score_components else 0.7  # Default good performance
    
    def _store_performance_data(
        self,
        content_type: str,
        metrics: Dict[str, Any],
        timestamp: datetime
    ):
        """
Store performance data for trend analysis."""
        if 'processing_efficiency' in metrics:
            self.processing_times[content_type].append({
                'time': 1.0 / max(metrics['processing_efficiency'], 0.1),  # Inverse of efficiency
                'timestamp': timestamp
            })
        
        # Keep only recent data
        if len(self.processing_times[content_type]) > 100:
            self.processing_times[content_type] = self.processing_times[content_type][-100:]
