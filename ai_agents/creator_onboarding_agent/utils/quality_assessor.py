"""Quality Assessor - Advanced Content Quality Analysis System

Enterprise-grade content quality assessment with AI-powered scoring,
multi-dimensional quality metrics, and optimization recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import QualityAssessmentError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    QualityAssessmentError = globals().get('QualityAssessmentError', Exception)
from ...ml.quality_models import QualityAnalyzer, TechnicalAnalyzer, AestheticAnalyzer
from ...utils.performance_metrics import PerformanceMetrics

logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """
Quality assessment dimensions"""

    TECHNICAL = "technical"
    AESTHETIC = "aesthetic"
    CONTENT = "content"
    ENGAGEMENT = "engagement"
    PROFESSIONAL = "professional"
    COMMERCIAL = "commercial"

class QualityLevel(Enum):
    """Content quality levels"""

    POOR = "poor"           # 0.0 - 0.3
    FAIR = "fair"           # 0.3 - 0.5
    GOOD = "good"           # 0.5 - 0.7
    EXCELLENT = "excellent" # 0.7 - 0.9
    EXCEPTIONAL = "exceptional"  # 0.9 - 1.0

@dataclass
class QualityAssessment:
    """Comprehensive quality assessment results"""
    content_id: str
    user_id: str
    content_type: str
    
    # Overall Quality Metrics
    overall_score: float = 0.0
    quality_level: QualityLevel = QualityLevel.FAIR
    
    # Dimension Scores
    technical_score: float = 0.0
    aesthetic_score: float = 0.0
    content_score: float = 0.0
    engagement_score: float = 0.0
    professional_score: float = 0.0
    commercial_score: float = 0.0
    
    # Detailed Technical Metrics
    technical_metrics: Dict[str, float] = field(default_factory=dict)
    aesthetic_metrics: Dict[str, float] = field(default_factory=dict)
    
    # Quality Indicators
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_areas: List[str] = field(default_factory=list)
    
    # Recommendations
    optimization_recommendations: List[str] = field(default_factory=list)
    technical_improvements: List[str] = field(default_factory=list)
    aesthetic_improvements: List[str] = field(default_factory=list)
    
    # Comparison Data
    industry_percentile: float = 0.0
    creator_type_percentile: float = 0.0
    improvement_potential: float = 0.0
    
    # Metadata
    assessment_timestamp: datetime = field(default_factory=datetime.utcnow)
    assessment_version: str = "2.1.0"
    processing_time: float = 0.0

class QualityAssessor:
    """
    Advanced content quality assessment system with AI-powered analysis.
    
    Core Capabilities:
    - Multi-dimensional quality scoring
    - Technical quality analysis (resolution, audio quality, etc.)
    - Aesthetic quality evaluation (composition, color, design)
    - Content quality assessment (originality, relevance, engagement)
    - Professional quality benchmarking
    - Commercial viability scoring
    - Industry-standard comparison
    - Detailed improvement recommendations
    """
    
    def __init__(self):
        # Initialize AI quality models
        self.quality_analyzer = QualityAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.aesthetic_analyzer = AestheticAnalyzer()
        
        # Performance tracking
        self.performance_metrics = PerformanceMetrics()
        
        # Quality benchmarks by content type
        self.quality_benchmarks = self._initialize_benchmarks()
        
        # Industry standards
        self.industry_standards = self._initialize_industry_standards()
        
        logger.info("QualityAssessor initialized successfully")
    
    def _initialize_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Initialize quality benchmarks by content type."""
        return {
            'audio': {
                'minimum_bitrate': 128,  # kbps
                'recommended_bitrate': 320,
                'minimum_sample_rate': 44100,  # Hz
                'dynamic_range_minimum': 0.3,
                'snr_minimum': 0.6,
                'frequency_balance_minimum': 0.5
            },
            'image': {
                'minimum_resolution': 720,  # Height
                'recommended_resolution': 1080,
                'minimum_sharpness': 0.4,
                'brightness_optimal_range': [0.4, 0.6],
                'contrast_minimum': 0.3,
                'composition_minimum': 0.5
            },
            'video': {
                'minimum_resolution': 720,
                'recommended_resolution': 1080,
                'minimum_fps': 24,
                'recommended_fps': 30,
                'audio_sync_tolerance': 0.05,
                'compression_quality_minimum': 0.6
            },
            'text': {
                'readability_minimum': 0.6,
                'engagement_minimum': 0.4,
                'originality_minimum': 0.7,
                'structure_minimum': 0.5
            }
        }
    
    def _initialize_industry_standards(self) -> Dict[str, Dict[str, float]]:
        """
Initialize industry quality standards."""
        return {
            'musician': {
                'audio_quality_weight': 0.4,
                'production_quality_weight': 0.3,
                'composition_weight': 0.2,
                'commercial_appeal_weight': 0.1
            },
            'photographer': {
                'technical_quality_weight': 0.3,
                'aesthetic_quality_weight': 0.4,
                'composition_weight': 0.2,
                'commercial_appeal_weight': 0.1
            },
            'video_creator': {
                'video_quality_weight': 0.25,
                'audio_quality_weight': 0.25,
                'content_quality_weight': 0.3,
                'engagement_weight': 0.2
            },
            'influencer': {
                'visual_appeal_weight': 0.3,
                'content_relevance_weight': 0.3,
                'engagement_potential_weight': 0.3,
                'brand_consistency_weight': 0.1
            }
        }
    
    async def assess_quality(self, content: Dict[str, Any], 
                           analysis: Dict[str, Any] = None,
                           creator_type: str = None) -> QualityAssessment:
        """
        Perform comprehensive quality assessment of content.
        """
        start_time = datetime.utcnow()
        
        try:
            content_id = content.get('id', 'unknown')
            user_id = content.get('user_id', 'unknown')
            content_type = content.get('type', 'unknown').lower()
            
            # Initialize assessment
            assessment = QualityAssessment(
                content_id=content_id,
                user_id=user_id,
                content_type=content_type
            )
            
            # Perform dimension-specific assessments
            await self._assess_technical_quality(assessment, content, analysis)
            await self._assess_aesthetic_quality(assessment, content, analysis)
            await self._assess_content_quality(assessment, content, analysis)
            await self._assess_engagement_potential(assessment, content, analysis)
            await self._assess_professional_quality(assessment, content, analysis, creator_type)
            await self._assess_commercial_viability(assessment, content, analysis, creator_type)
            
            # Calculate overall score
            self._calculate_overall_score(assessment, creator_type)
            
            # Determine quality level
            assessment.quality_level = self._determine_quality_level(assessment.overall_score)
            
            # Generate recommendations
            await self._generate_quality_recommendations(assessment, creator_type)
            
            # Calculate industry percentiles
            await self._calculate_industry_percentiles(assessment, creator_type)
            
            # Identify strengths and weaknesses
            self._identify_strengths_weaknesses(assessment)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            assessment.processing_time = processing_time
            
            # Track performance
            self.performance_metrics.record_assessment(assessment)
            
            logger.info(f"Quality assessment completed for content {content_id}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing quality: {str(e)}")
            raise QualityAssessmentError(f"Quality assessment failed: {str(e)}")
    
    async def batch_assess_quality(self, content_items: List[Dict[str, Any]],
                                 creator_type: str = None,
                                 concurrent_limit: int = 5) -> List[QualityAssessment]:
        """
        Perform batch quality assessment with concurrency control.
        """
        try:
            semaphore = asyncio.Semaphore(concurrent_limit)
            
            async def assess_single(content_item):
        try:
            logger.info(f"Executing assess_single")
            
            # Implementation for assess_single
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"assess_single completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"assess_single failed: {e}")
            raise
                    return await self.assess_quality(content_item, creator_type=creator_type)
            
            # Process all items concurrently
            tasks = [assess_single(item) for item in content_items]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and log errors
            valid_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error assessing item {i}: {str(result)}")
                else:
                    valid_results.append(result)
            
            logger.info(f"Batch quality assessment completed: {len(valid_results)}/{len(content_items)} successful")
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch quality assessment: {str(e)}")
            raise QualityAssessmentError(f"Batch assessment failed: {str(e)}")
    
    async def _assess_technical_quality(self, assessment: QualityAssessment,
                                      content: Dict[str, Any],
                                      analysis: Dict[str, Any] = None) -> None:
        """Assess technical quality aspects of content."""
        try:
            technical_metrics = {}
            content_type = assessment.content_type
            benchmarks = self.quality_benchmarks.get(content_type, {})
            
            if analysis and analysis.get('technical_quality'):
                # Use existing analysis data
                tech_data = analysis['technical_quality']
                
                if content_type == 'audio':
                    # Audio technical metrics
                    technical_metrics = {
                        'bitrate_score': self._score_against_benchmark(
                            tech_data.get('bitrate', 128),
                            benchmarks.get('minimum_bitrate', 128),
                            benchmarks.get('recommended_bitrate', 320)
                        ),
                        'sample_rate_score': self._score_against_benchmark(
                            tech_data.get('sample_rate', 44100),
                            benchmarks.get('minimum_sample_rate', 44100),
                            48000
                        ),
                        'dynamic_range_score': tech_data.get('dynamic_range', 0.5),
                        'snr_score': tech_data.get('signal_to_noise_ratio', 0.5),
                        'frequency_balance_score': tech_data.get('frequency_balance', 0.5),
                        'clipping_penalty': 1.0 - tech_data.get('clipping_detection', 0.0)
                    }
                
                elif content_type == 'image':
                    # Image technical metrics
                    technical_metrics = {
                        'resolution_score': tech_data.get('resolution_score', 0.5),
                        'sharpness_score': tech_data.get('sharpness_score', 0.5),
                        'brightness_score': tech_data.get('brightness_score', 0.5),
                        'contrast_score': tech_data.get('contrast_score', 0.5),
                        'color_balance_score': tech_data.get('color_balance', 0.5),
                        'noise_score': 1.0 - tech_data.get('noise_level', 0.2)
                    }
                
                elif content_type == 'video':
                    # Video technical metrics
                    technical_metrics = {
                        'video_quality_score': tech_data.get('video_quality', 0.5),
                        'audio_sync_score': tech_data.get('audio_sync', 0.9),
                        'frame_rate_score': self._score_frame_rate(tech_data.get('frame_rate', 30)),
                        'compression_score': tech_data.get('compression_quality', 0.7),
                        'stabilization_score': tech_data.get('stabilization', 0.8)
                    }
                
                elif content_type == 'text':
                    # Text technical metrics
                    technical_metrics = {
                        'readability_score': tech_data.get('readability_flesch', 0.6),
                        'grammar_score': tech_data.get('grammar_score', 0.8),
                        'structure_score': tech_data.get('structure_score', 0.7),
                        'formatting_score': tech_data.get('formatting_score', 0.7)
                    }
            
            else:
                # Default technical scores if no analysis available
                technical_metrics = self._generate_default_technical_scores(content_type)
            
            # Store technical metrics
            assessment.technical_metrics = technical_metrics
            
            # Calculate overall technical score
            if technical_metrics:
                assessment.technical_score = sum(technical_metrics.values()) / len(technical_metrics)
            else:
                assessment.technical_score = 0.5  # Default
            
        except Exception as e:
            logger.error(f"Error assessing technical quality: {str(e)}")
            assessment.technical_score = 0.3  # Low default on error
    
    async def _assess_aesthetic_quality(self, assessment: QualityAssessment,
                                      content: Dict[str, Any],
                                      analysis: Dict[str, Any] = None) -> None:
        """Assess aesthetic and visual quality aspects."""
        try:
            aesthetic_metrics = {}
            content_type = assessment.content_type
            
            if analysis and analysis.get('aesthetic_quality'):
                # Use existing aesthetic analysis
                aesthetic_data = analysis['aesthetic_quality']
                
                if content_type in ['image', 'video']:
                    aesthetic_metrics = {
                        'composition_score': aesthetic_data.get('composition_score', 0.6),
                        'color_harmony_score': aesthetic_data.get('color_harmony', 0.6),
                        'visual_balance_score': aesthetic_data.get('visual_balance', 0.6),
                        'lighting_score': aesthetic_data.get('lighting_score', 0.7),
                        'style_consistency_score': aesthetic_data.get('style_consistency', 0.7)
                    }
                
                elif content_type == 'audio':
                    aesthetic_metrics = {
                        'musical_harmony_score': aesthetic_data.get('harmony_score', 0.7),
                        'production_aesthetics_score': aesthetic_data.get('production_quality', 0.6),
                        'arrangement_score': aesthetic_data.get('arrangement_quality', 0.6),
                        'sonic_aesthetics_score': aesthetic_data.get('sonic_quality', 0.7)
                    }
                
                elif content_type == 'text':
                    aesthetic_metrics = {
                        'writing_style_score': aesthetic_data.get('style_score', 0.7),
                        'narrative_flow_score': aesthetic_data.get('flow_score', 0.6),
                        'tone_consistency_score': aesthetic_data.get('tone_score', 0.7),
                        'language_elegance_score': aesthetic_data.get('elegance_score', 0.6)
                    }
            
            else:
                # Generate default aesthetic scores
                aesthetic_metrics = self._generate_default_aesthetic_scores(content_type)
            
            # Store aesthetic metrics
            assessment.aesthetic_metrics = aesthetic_metrics
            
            # Calculate overall aesthetic score
            if aesthetic_metrics:
                assessment.aesthetic_score = sum(aesthetic_metrics.values()) / len(aesthetic_metrics)
            else:
                assessment.aesthetic_score = 0.6  # Default
            
        except Exception as e:
            logger.error(f"Error assessing aesthetic quality: {str(e)}")
            assessment.aesthetic_score = 0.5  # Default on error
    
    async def _assess_content_quality(self, assessment: QualityAssessment,
                                    content: Dict[str, Any],
                                    analysis: Dict[str, Any] = None) -> None:
        """Assess content relevance, originality, and value."""
        try:
            content_factors = []
            
            # Originality assessment
            originality_score = analysis.get('originality_score', 0.7) if analysis else 0.7
            content_factors.append(originality_score)
            
            # Relevance assessment
            if analysis and analysis.get('categories'):
                # Content has clear categories - good for relevance
                relevance_score = 0.8
            else:
                relevance_score = 0.6
            content_factors.append(relevance_score)
            
            # Complexity and depth
            complexity_score = analysis.get('complexity_score', 0.6) if analysis else 0.6
            # Moderate complexity is often better for engagement
            if 0.4 <= complexity_score <= 0.7:
                complexity_factor = 0.8
            else:
                complexity_factor = complexity_score
            content_factors.append(complexity_factor)
            
            # Educational or entertainment value
            if analysis and (analysis.get('themes') or analysis.get('keywords')):
                value_score = 0.8  # Content has clear themes/keywords
            else:
                value_score = 0.6
            content_factors.append(value_score)
            
            # Calculate overall content score
            assessment.content_score = sum(content_factors) / len(content_factors)
            
        except Exception as e:
            logger.error(f"Error assessing content quality: {str(e)}")
            assessment.content_score = 0.6
    
    async def _assess_engagement_potential(self, assessment: QualityAssessment,
                                         content: Dict[str, Any],
                                         analysis: Dict[str, Any] = None) -> None:
        """Assess potential for audience engagement."""
        try:
            engagement_factors = []
            
            # Sentiment analysis impact
            if analysis and 'sentiment_score' in analysis:
                sentiment = analysis['sentiment_score']
                # Positive sentiment generally better for engagement
                if sentiment > 0:
                    sentiment_factor = min(0.7 + sentiment * 0.3, 1.0)
                else:
                    sentiment_factor = max(0.3 + sentiment * 0.2, 0.1)
                engagement_factors.append(sentiment_factor)
            
            # Content format engagement potential
            content_type = assessment.content_type
            format_engagement = {
                'video': 0.8,    # High engagement potential
                'image': 0.7,    # Good visual engagement
                'audio': 0.6,    # Moderate engagement
                'text': 0.5      # Lower but stable engagement
            }
            engagement_factors.append(format_engagement.get(content_type, 0.6))
            
            # Length/duration optimization
            if content_type == 'video':
                duration = content.get('duration', 60)  # seconds
                if 30 <= duration <= 180:  # 30s to 3min optimal for most platforms
                    duration_factor = 0.9
                elif duration <= 600:  # Up to 10 minutes still good
                    duration_factor = 0.7
                else:
                    duration_factor = 0.5
                engagement_factors.append(duration_factor)
            
            # Quality correlation with engagement
            if assessment.technical_score > 0:
                # Higher technical quality typically correlates with better engagement
                quality_engagement_factor = min(0.5 + assessment.technical_score * 0.5, 1.0)
                engagement_factors.append(quality_engagement_factor)
            
            # Platform suitability
            if analysis and analysis.get('platform_suitability'):
                platform_scores = analysis['platform_suitability'].values()
                avg_platform_suitability = sum(platform_scores) / len(platform_scores)
                engagement_factors.append(avg_platform_suitability)
            
            # Calculate engagement score
            if engagement_factors:
                assessment.engagement_score = sum(engagement_factors) / len(engagement_factors)
            else:
                assessment.engagement_score = 0.6
            
        except Exception as e:
            logger.error(f"Error assessing engagement potential: {str(e)}")
            assessment.engagement_score = 0.5
    
    async def _assess_professional_quality(self, assessment: QualityAssessment,
                                         content: Dict[str, Any],
                                         analysis: Dict[str, Any] = None,
                                         creator_type: str = None) -> None:
        """Assess professional production quality standards."""
        try:
            professional_factors = []
            
            # Technical professionalism
            tech_professional_score = min(assessment.technical_score * 1.2, 1.0)
            professional_factors.append(tech_professional_score)
            
            # Aesthetic professionalism
            aesthetic_professional_score = min(assessment.aesthetic_score * 1.1, 1.0)
            professional_factors.append(aesthetic_professional_score)
            
            # Consistency indicators
            if analysis:
                # Check for consistent branding, style, quality
                consistency_indicators = [
                    'brand_consistency' in analysis,
                    len(analysis.get('tags', [])) > 3,  # Good tagging
                    analysis.get('optimization_suggestions', []) != []  # Shows analysis depth
                ]
                consistency_score = sum(consistency_indicators) / len(consistency_indicators)
                professional_factors.append(consistency_score)
            
            # Creator type specific professional standards
            if creator_type:
                type_standards = self.industry_standards.get(creator_type, {})
                if type_standards:
                    # Weight scores according to creator type importance
                    weighted_score = (
                        assessment.technical_score * type_standards.get('technical_quality_weight', 0.3) +
                        assessment.aesthetic_score * type_standards.get('aesthetic_quality_weight', 0.3) +
                        assessment.content_score * type_standards.get('content_quality_weight', 0.4)
                    )
                    professional_factors.append(weighted_score)
            
            # Calculate professional score
            if professional_factors:
                assessment.professional_score = sum(professional_factors) / len(professional_factors)
            else:
                assessment.professional_score = (assessment.technical_score + assessment.aesthetic_score) / 2
            
        except Exception as e:
            logger.error(f"Error assessing professional quality: {str(e)}")
            assessment.professional_score = 0.6
    
    async def _assess_commercial_viability(self, assessment: QualityAssessment,
                                         content: Dict[str, Any],
                                         analysis: Dict[str, Any] = None,
                                         creator_type: str = None) -> None:
        """Assess commercial potential and marketability."""
        try:
            commercial_factors = []
            
            # Quality threshold for commercial viability
            quality_threshold = assessment.overall_score if assessment.overall_score > 0 else (
                (assessment.technical_score + assessment.aesthetic_score + assessment.content_score) / 3
            )
            
            # Professional quality is crucial for commercial success
            commercial_factors.append(min(assessment.professional_score * 1.3, 1.0))
            
            # Engagement potential affects commercial value
            commercial_factors.append(assessment.engagement_score)
            
            # Content uniqueness/originality
            originality = analysis.get('originality_score', 0.7) if analysis else 0.7
            commercial_factors.append(originality)
            
            # Market demand indicators (simplified)
            content_type = assessment.content_type
            market_demand = {
                'video': 0.9,    # High market demand
                'audio': 0.8,    # Good market for music/podcasts
                'image': 0.7,    # Strong visual content market
                'text': 0.6      # Stable but competitive text market
            }
            commercial_factors.append(market_demand.get(content_type, 0.6))
            
            # Platform compatibility (affects monetization options)
            if analysis and analysis.get('platform_suitability'):
                platform_compatibility = sum(analysis['platform_suitability'].values()) / len(analysis['platform_suitability'])
                commercial_factors.append(platform_compatibility)
            
            # Creator type specific commercial factors
            if creator_type == 'musician' and content_type == 'audio':
                # Music has specific commercial considerations
                commercial_factors.append(0.9)  # High commercial potential for music
            elif creator_type == 'influencer' and content_type in ['image', 'video']:
                # Visual content for influencers has high commercial value
                commercial_factors.append(0.85)
            
            # Calculate commercial score
            if commercial_factors:
                assessment.commercial_score = sum(commercial_factors) / len(commercial_factors)
            else:
                assessment.commercial_score = quality_threshold * 0.8
            
        except Exception as e:
            logger.error(f"Error assessing commercial viability: {str(e)}")
            assessment.commercial_score = 0.5
    
    def _calculate_overall_score(self, assessment: QualityAssessment, creator_type: str = None) -> None:
        """Calculate overall quality score with appropriate weighting."""
        # Default weights
        weights = {
            'technical': 0.25,
            'aesthetic': 0.20,
            'content': 0.25,
            'engagement': 0.15,
            'professional': 0.10,
            'commercial': 0.05
        }
        
        # Adjust weights based on creator type
        if creator_type:
            type_weights = self.industry_standards.get(creator_type, {})
            if type_weights:
                weights['technical'] = type_weights.get('technical_quality_weight', weights['technical'])
                weights['aesthetic'] = type_weights.get('aesthetic_quality_weight', weights['aesthetic'])
                weights['content'] = type_weights.get('content_quality_weight', weights['content'])
                weights['engagement'] = type_weights.get('engagement_weight', weights['engagement'])
        
        # Calculate weighted score
        weighted_scores = [
            assessment.technical_score * weights['technical'],
            assessment.aesthetic_score * weights['aesthetic'],
            assessment.content_score * weights['content'],
            assessment.engagement_score * weights['engagement'],
            assessment.professional_score * weights['professional'],
            assessment.commercial_score * weights['commercial']
        ]
        
        assessment.overall_score = sum(weighted_scores)
    
    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """
Determine quality level based on overall score."""
        if overall_score >= 0.9:
            return QualityLevel.EXCEPTIONAL
        elif overall_score >= 0.7:
            return QualityLevel.EXCELLENT
        elif overall_score >= 0.5:
            return QualityLevel.GOOD
        elif overall_score >= 0.3:
            return QualityLevel.FAIR
        else:
            return QualityLevel.POOR
    
    async def _generate_quality_recommendations(self, assessment: QualityAssessment,
                                              creator_type: str = None) -> None:
        """
Generate specific quality improvement recommendations."""
        recommendations = []
        technical_improvements = []
        aesthetic_improvements = []
        
        # Technical recommendations
        if assessment.technical_score < 0.7:
            if assessment.content_type == 'audio':
                if assessment.technical_metrics.get('bitrate_score', 1.0) < 0.7:
                    technical_improvements.append("Increase audio bitrate to at least 256kbps for better quality")
                if assessment.technical_metrics.get('snr_score', 1.0) < 0.6:
                    technical_improvements.append("Reduce background noise and improve recording environment")
                if assessment.technical_metrics.get('dynamic_range_score', 1.0) < 0.5:
                    technical_improvements.append("Improve dynamic range by avoiding over-compression")
            
            elif assessment.content_type == 'image':
                if assessment.technical_metrics.get('resolution_score', 1.0) < 0.7:
                    technical_improvements.append("Increase image resolution to at least 1080p")
                if assessment.technical_metrics.get('sharpness_score', 1.0) < 0.6:
                    technical_improvements.append("Improve image sharpness and focus")
                if assessment.technical_metrics.get('brightness_score', 1.0) < 0.6:
                    technical_improvements.append("Optimize lighting and exposure")
            
            elif assessment.content_type == 'video':
                if assessment.technical_metrics.get('video_quality_score', 1.0) < 0.7:
                    technical_improvements.append("Improve video resolution and compression settings")
                if assessment.technical_metrics.get('audio_sync_score', 1.0) < 0.9:
                    technical_improvements.append("Ensure proper audio-video synchronization")
        
        # Aesthetic recommendations
        if assessment.aesthetic_score < 0.7:
            if assessment.content_type in ['image', 'video']:
                if assessment.aesthetic_metrics.get('composition_score', 1.0) < 0.6:
                    aesthetic_improvements.append("Apply composition techniques like rule of thirds")
                if assessment.aesthetic_metrics.get('color_harmony_score', 1.0) < 0.6:
                    aesthetic_improvements.append("Improve color harmony and balance")
                if assessment.aesthetic_metrics.get('lighting_score', 1.0) < 0.7:
                    aesthetic_improvements.append("Enhance lighting setup for better visual appeal")
            
            elif assessment.content_type == 'audio':
                if assessment.aesthetic_metrics.get('production_aesthetics_score', 1.0) < 0.6:
                    aesthetic_improvements.append("Enhance production quality and mixing")
                if assessment.aesthetic_metrics.get('arrangement_score', 1.0) < 0.6:
                    aesthetic_improvements.append("Improve musical arrangement and structure")
        
        # General recommendations
        if assessment.overall_score < 0.6:
            recommendations.append("Focus on overall quality improvement to meet professional standards")
        
        if assessment.engagement_score < 0.6:
            recommendations.append("Optimize content for better audience engagement")
        
        if assessment.commercial_score < 0.5:
            recommendations.append("Consider commercial viability factors to improve monetization potential")
        
        # Creator type specific recommendations
        if creator_type == 'musician' and assessment.content_type == 'audio':
            if assessment.aesthetic_score < 0.7:
                recommendations.append("Focus on production quality and musical arrangement")
        
        elif creator_type == 'photographer' and assessment.content_type == 'image':
            if assessment.technical_score < 0.8:
                recommendations.append("Invest in technical photography skills and equipment")
        
        # Store recommendations
        assessment.optimization_recommendations = recommendations
        assessment.technical_improvements = technical_improvements
        assessment.aesthetic_improvements = aesthetic_improvements
    
    async def _calculate_industry_percentiles(self, assessment: QualityAssessment,
                                            creator_type: str = None) -> None:
        """Calculate industry and creator type percentiles."""
        # Simulate industry percentile calculation
        # In production, this would compare against actual industry data
        
        # Industry percentile (simplified calculation)
        score_multiplier = assessment.overall_score * 100
        assessment.industry_percentile = min(score_multiplier, 95.0)  # Cap at 95th percentile
        
        # Creator type percentile
        if creator_type:
            # Adjust based on creator type competitive landscape
            type_adjustments = {
                'musician': -5,     # Highly competitive
                'photographer': -3,  # Competitive
                'video_creator': -7, # Very competitive
                'influencer': -10,   # Extremely competitive
                'blogger': 0,        # Moderate competition
                'podcaster': 2       # Less competitive
            }
            
            adjustment = type_adjustments.get(creator_type, 0)
            assessment.creator_type_percentile = max(5.0, min(95.0, assessment.industry_percentile + adjustment))
        else:
            assessment.creator_type_percentile = assessment.industry_percentile
        
        # Calculate improvement potential
        assessment.improvement_potential = (1.0 - assessment.overall_score) * 100
    
    def _identify_strengths_weaknesses(self, assessment: QualityAssessment) -> None:
        """
Identify content strengths and weaknesses."""
        scores = {
            'technical': assessment.technical_score,
            'aesthetic': assessment.aesthetic_score,
            'content': assessment.content_score,
            'engagement': assessment.engagement_score,
            'professional': assessment.professional_score,
            'commercial': assessment.commercial_score
        }
        
        # Sort scores to identify strengths and weaknesses
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Top 2 scores are strengths (if above 0.7)
        strengths = [area.title() + " Quality" for area, score in sorted_scores[:2] if score >= 0.7]
        assessment.strengths = strengths
        
        # Bottom 2 scores are weaknesses (if below 0.6)
        weaknesses = [area.title() + " Quality" for area, score in sorted_scores[-2:] if score < 0.6]
        assessment.weaknesses = weaknesses
        
        # Areas for improvement (scores between 0.4 and 0.7)
        improvement_areas = [area.title() + " Quality" for area, score in scores.items() if 0.4 <= score < 0.7]
        assessment.improvement_areas = improvement_areas
    
    # Helper methods for scoring
    def _score_against_benchmark(self, value: float, minimum: float, optimal: float) -> float:
        """Score a value against minimum and optimal benchmarks."""
        if value >= optimal:
            return 1.0
        elif value >= minimum:
            return 0.5 + 0.5 * (value - minimum) / (optimal - minimum)
        else:
            return max(0.1, value / minimum * 0.5)
    
    def _score_frame_rate(self, fps: float) -> float:
        """
Score frame rate for video content."""
        if fps >= 60:
            return 1.0
        elif fps >= 30:
            return 0.9
        elif fps >= 24:
            return 0.7
        else:
            return 0.4
    
    def _generate_default_technical_scores(self, content_type: str) -> Dict[str, float]:
        """
Generate default technical scores when analysis is not available."""
        defaults = {
            'audio': {
                'bitrate_score': 0.6,
                'sample_rate_score': 0.7,
                'dynamic_range_score': 0.5,
                'snr_score': 0.6,
                'frequency_balance_score': 0.6,
                'clipping_penalty': 0.9
            },
            'image': {
                'resolution_score': 0.7,
                'sharpness_score': 0.6,
                'brightness_score': 0.6,
                'contrast_score': 0.6,
                'color_balance_score': 0.7,
                'noise_score': 0.8
            },
            'video': {
                'video_quality_score': 0.7,
                'audio_sync_score': 0.9,
                'frame_rate_score': 0.8,
                'compression_score': 0.7,
                'stabilization_score': 0.8
            },
            'text': {
                'readability_score': 0.7,
                'grammar_score': 0.8,
                'structure_score': 0.6,
                'formatting_score': 0.7
            }
        }
        
        return defaults.get(content_type, {'overall': 0.6})
    
    def _generate_default_aesthetic_scores(self, content_type: str) -> Dict[str, float]:
        """
Generate default aesthetic scores when analysis is not available."""
        defaults = {
            'image': {
                'composition_score': 0.6,
                'color_harmony_score': 0.6,
                'visual_balance_score': 0.6,
                'lighting_score': 0.6,
                'style_consistency_score': 0.7
            },
            'video': {
                'composition_score': 0.6,
                'color_harmony_score': 0.6,
                'visual_balance_score': 0.6,
                'lighting_score': 0.6,
                'style_consistency_score': 0.7
            },
            'audio': {
                'musical_harmony_score': 0.7,
                'production_aesthetics_score': 0.6,
                'arrangement_score': 0.6,
                'sonic_aesthetics_score': 0.7
            },
            'text': {
                'writing_style_score': 0.7,
                'narrative_flow_score': 0.6,
                'tone_consistency_score': 0.7,
                'language_elegance_score': 0.6
            }
        }
        
        return defaults.get(content_type, {'overall': 0.6})
