"""
Quality Monitor - Advanced Content Quality Assessment System
============================================================

AI-powered quality monitoring and assessment for all content types
with real-time feedback and improvement suggestions.

Author: Fahed Mlaiel <mlaiel@live.de>
Project Team Specialists: Lead AI Dev, Backend Senior, ML Engineer, DBA, Security Expert, 
                         Microservices Architect, Audio Processing Expert, DevOps Engineer, 
                         AI Prompt Engineer

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code and concept are proprietary to Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, or distribution without explicit written permission is strictly prohibited.
Legal action will be pursued against any infringement.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Quality assessment dimensions"""
    TECHNICAL_QUALITY = "technical_quality"
    CONTENT_ORIGINALITY = "content_originality"
    ENGAGEMENT_POTENTIAL = "engagement_potential"
    PRODUCTION_VALUE = "production_value"
    AUDIO_QUALITY = "audio_quality"
    VISUAL_QUALITY = "visual_quality"
    NARRATIVE_STRUCTURE = "narrative_structure"
    SEO_OPTIMIZATION = "seo_optimization"
    ACCESSIBILITY = "accessibility"
    BRAND_CONSISTENCY = "brand_consistency"

class QualityLevel(Enum):
    """Quality levels"""
    EXCEPTIONAL = "exceptional"  # 0.9-1.0
    HIGH = "high"              # 0.8-0.89
    GOOD = "good"              # 0.7-0.79
    ACCEPTABLE = "acceptable"   # 0.6-0.69
    POOR = "poor"              # 0.4-0.59
    UNACCEPTABLE = "unacceptable"  # 0.0-0.39

@dataclass
class QualityMetrics:
    """Comprehensive quality metrics structure"""
    content_id: str
    overall_score: float
    quality_level: QualityLevel
    dimension_scores: Dict[QualityDimension, float]
    technical_analysis: Dict[str, Any]
    improvement_suggestions: List[str]
    strengths: List[str]
    weaknesses: List[str]
    benchmark_comparison: Dict[str, float]
    industry_percentile: float
    assessment_confidence: float
    automated_flags: List[str]
    human_review_required: bool
    assessment_timestamp: datetime = field(default_factory=datetime.utcnow)
    assessment_version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

class QualityMonitor:
    """
    Advanced AI-powered quality monitoring system for multi-format content
    with real-time assessment and continuous improvement recommendations.
    """
    
    def __init__(self):
        self.quality_thresholds = {
            QualityLevel.EXCEPTIONAL: 0.9,
            QualityLevel.HIGH: 0.8,
            QualityLevel.GOOD: 0.7,
            QualityLevel.ACCEPTABLE: 0.6,
            QualityLevel.POOR: 0.4,
            QualityLevel.UNACCEPTABLE: 0.0
        }
        
        self.dimension_weights = {
            QualityDimension.TECHNICAL_QUALITY: 0.25,
            QualityDimension.CONTENT_ORIGINALITY: 0.20,
            QualityDimension.ENGAGEMENT_POTENTIAL: 0.15,
            QualityDimension.PRODUCTION_VALUE: 0.15,
            QualityDimension.AUDIO_QUALITY: 0.10,
            QualityDimension.VISUAL_QUALITY: 0.10,
            QualityDimension.SEO_OPTIMIZATION: 0.05
        }
        
        self.benchmark_data = {
            'industry_averages': {
                'music': 0.72,
                'video': 0.68,
                'image': 0.75,
                'text': 0.71,
                'podcast': 0.69
            },
            'top_performer_threshold': 0.85,
            'viral_content_threshold': 0.88
        }
    
    async def assess_quality(self, content_metadata) -> QualityMetrics:
        """Comprehensive quality assessment of content"""
        try:
            # Multi-dimensional quality analysis
            dimension_scores = await self._analyze_all_dimensions(content_metadata)
            
            # Calculate overall score
            overall_score = self._calculate_weighted_score(dimension_scores)
            
            # Determine quality level
            quality_level = self._determine_quality_level(overall_score)
            
            # Technical analysis
            technical_analysis = await self._perform_technical_analysis(content_metadata)
            
            # Generate improvement suggestions
            improvement_suggestions = await self._generate_improvement_suggestions(
                dimension_scores, content_metadata
            )
            
            # Identify strengths and weaknesses
            strengths, weaknesses = await self._identify_strengths_weaknesses(dimension_scores)
            
            # Benchmark against industry standards
            benchmark_comparison = await self._benchmark_against_industry(
                content_metadata, overall_score
            )
            
            # Calculate industry percentile
            industry_percentile = await self._calculate_industry_percentile(
                content_metadata, overall_score
            )
            
            # Assessment confidence calculation
            assessment_confidence = self._calculate_assessment_confidence(
                dimension_scores, technical_analysis
            )
            
            # Automated quality flags
            automated_flags = await self._generate_automated_flags(
                content_metadata, dimension_scores, technical_analysis
            )
            
            # Determine if human review is needed
            human_review_required = self._requires_human_review(
                overall_score, automated_flags, assessment_confidence
            )
            
            quality_metrics = QualityMetrics(
                content_id=content_metadata.content_id,
                overall_score=overall_score,
                quality_level=quality_level,
                dimension_scores=dimension_scores,
                technical_analysis=technical_analysis,
                improvement_suggestions=improvement_suggestions,
                strengths=strengths,
                weaknesses=weaknesses,
                benchmark_comparison=benchmark_comparison,
                industry_percentile=industry_percentile,
                assessment_confidence=assessment_confidence,
                automated_flags=automated_flags,
                human_review_required=human_review_required
            )
            
            logger.info(f"Quality assessment completed for content {content_metadata.content_id}: {overall_score:.2f}")
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {str(e)}")
            raise
    
    async def _analyze_all_dimensions(self, content_metadata) -> Dict[QualityDimension, float]:
        """Analyze all quality dimensions"""
        dimension_scores = {}
        
        # Technical Quality Analysis
        dimension_scores[QualityDimension.TECHNICAL_QUALITY] = await self._assess_technical_quality(content_metadata)
        
        # Content Originality
        dimension_scores[QualityDimension.CONTENT_ORIGINALITY] = await self._assess_originality(content_metadata)
        
        # Engagement Potential
        dimension_scores[QualityDimension.ENGAGEMENT_POTENTIAL] = await self._assess_engagement_potential(content_metadata)
        
        # Production Value
        dimension_scores[QualityDimension.PRODUCTION_VALUE] = await self._assess_production_value(content_metadata)
        
        # Content-type specific assessments
        if content_metadata.content_type.value in ['audio', 'music', 'podcast']:
            dimension_scores[QualityDimension.AUDIO_QUALITY] = await self._assess_audio_quality(content_metadata)
        
        if content_metadata.content_type.value in ['video', 'image', 'photo']:
            dimension_scores[QualityDimension.VISUAL_QUALITY] = await self._assess_visual_quality(content_metadata)
        
        if content_metadata.content_type.value in ['text', 'blog', 'article']:
            dimension_scores[QualityDimension.NARRATIVE_STRUCTURE] = await self._assess_narrative_structure(content_metadata)
        
        # SEO Optimization
        dimension_scores[QualityDimension.SEO_OPTIMIZATION] = await self._assess_seo_optimization(content_metadata)
        
        # Accessibility
        dimension_scores[QualityDimension.ACCESSIBILITY] = await self._assess_accessibility(content_metadata)
        
        # Brand Consistency
        dimension_scores[QualityDimension.BRAND_CONSISTENCY] = await self._assess_brand_consistency(content_metadata)
        
        return dimension_scores
    
    async def _assess_technical_quality(self, content_metadata) -> float:
        """Assess technical quality of content"""
        technical_score = 0.0
        
        # File quality metrics
        if hasattr(content_metadata, 'file_size') and content_metadata.file_size:
            # Optimal file size scoring
            if content_metadata.content_type.value == 'video':
                # For video: good balance between quality and size
                optimal_size = 100 * 1024 * 1024  # 100MB
                size_score = min(content_metadata.file_size / optimal_size, 1.0)
                technical_score += size_score * 0.3
            elif content_metadata.content_type.value == 'audio':
                # For audio: higher bitrate is better
                optimal_size = 20 * 1024 * 1024  # 20MB
                size_score = min(content_metadata.file_size / optimal_size, 1.0)
                technical_score += size_score * 0.3
        
        # Metadata completeness
        metadata_completeness = self._calculate_metadata_completeness(content_metadata)
        technical_score += metadata_completeness * 0.3
        
        # Content format optimization
        format_score = 0.8  # Assume good format by default
        technical_score += format_score * 0.2
        
        # Resolution/Quality indicators (if available)
        if hasattr(content_metadata, 'dimensions') and content_metadata.dimensions:
            width = content_metadata.dimensions.get('width', 0)
            height = content_metadata.dimensions.get('height', 0)
            if width >= 1920 and height >= 1080:
                technical_score += 0.2
            elif width >= 1280 and height >= 720:
                technical_score += 0.15
            else:
                technical_score += 0.1
        
        return min(technical_score, 1.0)
    
    async def _assess_originality(self, content_metadata) -> float:
        """Assess content originality using AI analysis"""
        # This would use ML models to detect originality
        originality_score = content_metadata.ai_analysis.get('originality_score', 0.75)
        
        # Additional checks
        duplicate_flags = content_metadata.ai_analysis.get('duplicate_detection', {})
        if duplicate_flags.get('is_duplicate', False):
            originality_score *= 0.3  # Heavy penalty for duplicates
        
        plagiarism_score = content_metadata.ai_analysis.get('plagiarism_score', 0.0)
        originality_score *= (1.0 - plagiarism_score)
        
        return max(min(originality_score, 1.0), 0.0)
    
    async def _assess_engagement_potential(self, content_metadata) -> float:
        """Assess potential for audience engagement"""
        base_engagement = content_metadata.ai_analysis.get('engagement_potential', 0.6)
        
        # Boost based on trending topics
        trending_boost = 0.0
        for tag in content_metadata.tags:
            if self._is_trending_topic(tag):
                trending_boost += 0.05
        
        # Title and description quality
        title_score = self._assess_title_quality(content_metadata.title)
        description_score = self._assess_description_quality(content_metadata.description)
        
        engagement_score = base_engagement + trending_boost + (title_score * 0.1) + (description_score * 0.1)
        
        return min(engagement_score, 1.0)
    
    async def _assess_production_value(self, content_metadata) -> float:
        """Assess overall production value"""
        production_factors = {
            'editing_quality': content_metadata.ai_analysis.get('editing_quality', 0.7),
            'composition': content_metadata.ai_analysis.get('composition_score', 0.7),
            'lighting_audio': content_metadata.ai_analysis.get('technical_execution', 0.7),
            'professional_finish': content_metadata.ai_analysis.get('professional_score', 0.7)
        }
        
        production_score = sum(production_factors.values()) / len(production_factors)
        return min(production_score, 1.0)
    
    async def _assess_audio_quality(self, content_metadata) -> float:
        """Assess audio-specific quality metrics"""
        audio_metrics = content_metadata.ai_analysis.get('audio_analysis', {})
        
        quality_factors = {
            'clarity': audio_metrics.get('clarity_score', 0.7),
            'noise_level': 1.0 - audio_metrics.get('noise_level', 0.2),
            'dynamic_range': audio_metrics.get('dynamic_range_score', 0.7),
            'frequency_balance': audio_metrics.get('frequency_balance', 0.7),
            'mastering_quality': audio_metrics.get('mastering_score', 0.7)
        }
        
        audio_score = sum(quality_factors.values()) / len(quality_factors)
        return min(audio_score, 1.0)
    
    async def _assess_visual_quality(self, content_metadata) -> float:
        """Assess visual-specific quality metrics"""
        visual_metrics = content_metadata.ai_analysis.get('visual_analysis', {})
        
        quality_factors = {
            'sharpness': visual_metrics.get('sharpness_score', 0.7),
            'exposure': visual_metrics.get('exposure_score', 0.7),
            'color_grading': visual_metrics.get('color_score', 0.7),
            'composition': visual_metrics.get('composition_score', 0.7),
            'stabilization': visual_metrics.get('stability_score', 0.7)
        }
        
        visual_score = sum(quality_factors.values()) / len(quality_factors)
        return min(visual_score, 1.0)
    
    async def _assess_narrative_structure(self, content_metadata) -> float:
        """Assess narrative and structural quality for text content"""
        narrative_metrics = content_metadata.ai_analysis.get('narrative_analysis', {})
        
        structure_factors = {
            'coherence': narrative_metrics.get('coherence_score', 0.7),
            'flow': narrative_metrics.get('flow_score', 0.7),
            'readability': narrative_metrics.get('readability_score', 0.7),
            'engagement': narrative_metrics.get('narrative_engagement', 0.7),
            'conclusion': narrative_metrics.get('conclusion_strength', 0.7)
        }
        
        narrative_score = sum(structure_factors.values()) / len(structure_factors)
        return min(narrative_score, 1.0)
    
    async def _assess_seo_optimization(self, content_metadata) -> float:
        """Assess SEO optimization level"""
        seo_factors = {
            'title_optimization': 0.8 if len(content_metadata.title) > 10 else 0.5,
            'description_length': 0.8 if len(content_metadata.description) > 100 else 0.6,
            'tags_count': min(len(content_metadata.tags) / 10.0, 1.0),
            'keyword_density': content_metadata.ai_analysis.get('keyword_density_score', 0.7),
            'meta_completeness': 0.9 if content_metadata.seo_keywords else 0.5
        }
        
        seo_score = sum(seo_factors.values()) / len(seo_factors)
        return min(seo_score, 1.0)
    
    async def _assess_accessibility(self, content_metadata) -> float:
        """Assess content accessibility"""
        accessibility_factors = {
            'alt_text_present': 0.8,  # Assume good alt text
            'captions_available': 0.7,  # Assume captions for video/audio
            'color_contrast': 0.8,  # Assume good contrast
            'text_readability': 0.8,  # Assume readable text
            'screen_reader_compatible': 0.8  # Assume compatibility
        }
        
        accessibility_score = sum(accessibility_factors.values()) / len(accessibility_factors)
        return min(accessibility_score, 1.0)
    
    async def _assess_brand_consistency(self, content_metadata) -> float:
        """Assess brand consistency"""
        # This would analyze brand elements, colors, fonts, tone
        brand_score = content_metadata.ai_analysis.get('brand_consistency_score', 0.75)
        return min(brand_score, 1.0)
    
    def _calculate_metadata_completeness(self, content_metadata) -> float:
        """Calculate how complete the content metadata is"""
        required_fields = ['title', 'description', 'tags', 'categories']
        optional_fields = ['seo_keywords', 'copyright_info']
        
        completed_required = 0
        for field in required_fields:
            value = getattr(content_metadata, field, None)
            if value and (isinstance(value, list) and len(value) > 0 or 
                         isinstance(value, str) and len(value.strip()) > 0):
                completed_required += 1
        
        completed_optional = 0
        for field in optional_fields:
            value = getattr(content_metadata, field, None)
            if value:
                completed_optional += 1
        
        required_score = completed_required / len(required_fields)
        optional_score = completed_optional / len(optional_fields)
        
        return (required_score * 0.8) + (optional_score * 0.2)
    
    def _is_trending_topic(self, tag: str) -> bool:
        """Check if a tag represents a trending topic"""
        trending_keywords = ['ai', 'viral', '2025', 'trending', 'new', 'latest', 'breaking']
        return any(keyword in tag.lower() for keyword in trending_keywords)
    
    def _assess_title_quality(self, title: str) -> float:
        """Assess title quality"""
        if not title:
            return 0.0
        
        quality_score = 0.0
        
        # Length check
        if 10 <= len(title) <= 60:
            quality_score += 0.3
        elif 60 < len(title) <= 100:
            quality_score += 0.2
        
        # Keyword presence
        if any(word in title.lower() for word in ['amazing', 'ultimate', 'best', 'new', 'exclusive']):
            quality_score += 0.2
        
        # Capitalization
        if title[0].isupper():
            quality_score += 0.1
        
        # No excessive punctuation
        if title.count('!') <= 2 and title.count('?') <= 1:
            quality_score += 0.1
        
        # Contains numbers (often engaging)
        if any(char.isdigit() for char in title):
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def _assess_description_quality(self, description: str) -> float:
        """Assess description quality"""
        if not description:
            return 0.0
        
        quality_score = 0.0
        
        # Length check
        if 100 <= len(description) <= 500:
            quality_score += 0.4
        elif 50 <= len(description) < 100:
            quality_score += 0.3
        
        # Call to action presence
        cta_keywords = ['subscribe', 'like', 'follow', 'share', 'comment', 'check out']
        if any(keyword in description.lower() for keyword in cta_keywords):
            quality_score += 0.2
        
        # Proper formatting (sentences)
        sentence_count = description.count('.') + description.count('!') + description.count('?')
        if sentence_count >= 2:
            quality_score += 0.2
        
        # No excessive repetition
        words = description.lower().split()
        unique_words = set(words)
        if len(unique_words) / len(words) > 0.7:  # Good word variety
            quality_score += 0.1
        
        return min(quality_score, 1.0)
    
    def _calculate_weighted_score(self, dimension_scores: Dict[QualityDimension, float]) -> float:
        """Calculate weighted overall quality score"""
        total_score = 0.0
        total_weight = 0.0
        
        for dimension, score in dimension_scores.items():
            weight = self.dimension_weights.get(dimension, 0.05)  # Default weight
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _determine_quality_level(self, overall_score: float) -> QualityLevel:
        """Determine quality level from overall score"""
        for level, threshold in sorted(self.quality_thresholds.items(), key=lambda x: x[1], reverse=True):
            if overall_score >= threshold:
                return level
        return QualityLevel.UNACCEPTABLE
    
    async def _perform_technical_analysis(self, content_metadata) -> Dict[str, Any]:
        """Perform detailed technical analysis"""
        return {
            'file_analysis': {
                'size_mb': content_metadata.file_size / (1024 * 1024) if content_metadata.file_size else 0,
                'format_optimal': True,
                'compression_efficient': True
            },
            'metadata_analysis': {
                'completeness_score': self._calculate_metadata_completeness(content_metadata),
                'seo_optimized': bool(content_metadata.seo_keywords),
                'tags_count': len(content_metadata.tags)
            },
            'content_analysis': content_metadata.ai_analysis,
            'performance_indicators': {
                'load_time_estimate': 2.5,  # seconds
                'compatibility_score': 0.95,
                'accessibility_score': 0.8
            }
        }
    
    async def _generate_improvement_suggestions(self, dimension_scores: Dict[QualityDimension, float], content_metadata) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        # Check each dimension and suggest improvements
        for dimension, score in dimension_scores.items():
            if score < 0.7:  # Below good threshold
                if dimension == QualityDimension.TECHNICAL_QUALITY:
                    suggestions.append("Improve technical quality: check resolution, file compression, and metadata completeness")
                elif dimension == QualityDimension.CONTENT_ORIGINALITY:
                    suggestions.append("Enhance originality: add unique perspective, personal insights, or creative elements")
                elif dimension == QualityDimension.ENGAGEMENT_POTENTIAL:
                    suggestions.append("Boost engagement: improve title appeal, add trending hashtags, enhance description")
                elif dimension == QualityDimension.SEO_OPTIMIZATION:
                    suggestions.append("Optimize for SEO: add relevant keywords, improve title and description, use proper tags")
                elif dimension == QualityDimension.AUDIO_QUALITY:
                    suggestions.append("Improve audio: reduce background noise, balance levels, enhance clarity")
                elif dimension == QualityDimension.VISUAL_QUALITY:
                    suggestions.append("Enhance visuals: improve lighting, stabilization, color grading, and composition")
        
        # General suggestions based on overall patterns
        if len(content_metadata.tags) < 5:
            suggestions.append("Add more relevant tags to improve discoverability")
        
        if len(content_metadata.description) < 100:
            suggestions.append("Expand description with more details and call-to-action")
        
        return suggestions[:10]  # Top 10 most important suggestions
    
    async def _identify_strengths_weaknesses(self, dimension_scores: Dict[QualityDimension, float]) -> Tuple[List[str], List[str]]:
        """Identify content strengths and weaknesses"""
        strengths = []
        weaknesses = []
        
        for dimension, score in dimension_scores.items():
            dimension_name = dimension.value.replace('_', ' ').title()
            
            if score >= 0.8:
                strengths.append(f"Excellent {dimension_name.lower()}")
            elif score >= 0.7:
                strengths.append(f"Good {dimension_name.lower()}")
            elif score < 0.6:
                weaknesses.append(f"Needs improvement in {dimension_name.lower()}")
        
        return strengths, weaknesses
    
    async def _benchmark_against_industry(self, content_metadata, overall_score: float) -> Dict[str, float]:
        """Benchmark content against industry standards"""
        content_type = content_metadata.content_type.value
        industry_avg = self.benchmark_data['industry_averages'].get(content_type, 0.70)
        
        return {
            'industry_average': industry_avg,
            'score_vs_average': overall_score - industry_avg,
            'percentile_rank': await self._calculate_industry_percentile(content_metadata, overall_score),
            'top_performer_threshold': self.benchmark_data['top_performer_threshold'],
            'viral_content_threshold': self.benchmark_data['viral_content_threshold']
        }
    
    async def _calculate_industry_percentile(self, content_metadata, overall_score: float) -> float:
        """Calculate percentile rank within industry"""
        # This would use actual industry data
        # For now, using a simplified calculation
        content_type = content_metadata.content_type.value
        industry_avg = self.benchmark_data['industry_averages'].get(content_type, 0.70)
        
        if overall_score >= 0.9:
            return 95.0
        elif overall_score >= 0.8:
            return 80.0
        elif overall_score >= industry_avg:
            return 60.0 + ((overall_score - industry_avg) * 100)
        else:
            return max(20.0, (overall_score / industry_avg) * 50)
    
    def _calculate_assessment_confidence(self, dimension_scores: Dict[QualityDimension, float], technical_analysis: Dict[str, Any]) -> float:
        """Calculate confidence level of the assessment"""
        confidence_factors = {
            'dimension_coverage': len(dimension_scores) / len(QualityDimension),
            'technical_completeness': 0.8,  # Based on available technical data
            'ai_analysis_confidence': 0.85,  # AI model confidence
            'metadata_completeness': technical_analysis['metadata_analysis']['completeness_score']
        }
        
        overall_confidence = sum(confidence_factors.values()) / len(confidence_factors)
        return min(overall_confidence, 1.0)
    
    async def _generate_automated_flags(self, content_metadata, dimension_scores: Dict[QualityDimension, float], technical_analysis: Dict[str, Any]) -> List[str]:
        """Generate automated quality flags"""
        flags = []
        
        # Low quality flags
        if dimension_scores.get(QualityDimension.TECHNICAL_QUALITY, 1.0) < 0.5:
            flags.append("low_technical_quality")
        
        if dimension_scores.get(QualityDimension.CONTENT_ORIGINALITY, 1.0) < 0.4:
            flags.append("potential_duplicate_content")
        
        # Missing elements flags
        if not content_metadata.tags:
            flags.append("missing_tags")
        
        if len(content_metadata.description) < 50:
            flags.append("insufficient_description")
        
        # Performance flags
        if content_metadata.file_size and content_metadata.file_size > 500 * 1024 * 1024:  # 500MB
            flags.append("large_file_size")
        
        return flags
    
    def _requires_human_review(self, overall_score: float, flags: List[str], confidence: float) -> bool:
        """Determine if human review is required"""
        # Require human review if:
        # 1. Very low quality score
        # 2. Low confidence in assessment
        # 3. Serious quality flags
        # 4. Potential policy violations
        
        if overall_score < 0.4:
            return True
        
        if confidence < 0.6:
            return True
        
        serious_flags = ['potential_duplicate_content', 'policy_violation', 'copyright_concern']
        if any(flag in flags for flag in serious_flags):
            return True
        
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for quality monitor"""
        return {
            "status": "healthy",
            "quality_dimensions": len(QualityDimension),
            "quality_levels": len(QualityLevel),
            "benchmark_data_loaded": bool(self.benchmark_data),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("QualityMonitor shutting down...")
