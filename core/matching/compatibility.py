"""Compatibility Analyzer for Content Creator Matching

This module provides advanced compatibility analysis between content creators,
evaluating multiple dimensions including content style, audience demographics,
brand alignment, and collaboration potential.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.
Warning: Unauthorized use, reproduction, or distribution of this code is strictly prohibited.
"""
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import asyncio
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from scipy.stats import pearsonr
import pandas as pd

from backend.core.analytics.metrics import MetricsCollector
from backend.core.cache.strategies import CacheManager


class CompatibilityDimension(Enum):
    """Compatibility analysis dimensions"""    CONTENT_STYLE = "content_style"
    AUDIENCE_DEMOGRAPHICS = "audience_demographics"
    BRAND_ALIGNMENT = "brand_alignment"
    ENGAGEMENT_PATTERNS = "engagement_patterns"
    QUALITY_STANDARDS = "quality_standards"
    PLATFORM_PRESENCE = "platform_presence"
    COMMUNICATION_STYLE = "communication_style"
    COLLABORATION_HISTORY = "collaboration_history"
    GEOGRAPHIC_COMPATIBILITY = "geographic_compatibility"
    SCHEDULE_ALIGNMENT = "schedule_alignment"


@dataclass
class CompatibilityScore:
    """Compatibility score with detailed breakdown"""    overall_score: float
    dimension_scores: Dict[CompatibilityDimension, float]
    confidence_level: float
    compatibility_factors: List[str]
    incompatibility_risks: List[str]
    recommendations: List[str]
    analyzed_at: datetime


@dataclass
class CreatorCompatibilityProfile:
    """Extended creator profile for compatibility analysis"""    user_id: int
    content_style_vector: np.ndarray
    audience_profile: Dict[str, Any]
    brand_attributes: Dict[str, Any]
    engagement_patterns: Dict[str, Any]
    quality_metrics: Dict[str, float]
    platform_analytics: Dict[str, Dict[str, Any]]
    communication_preferences: Dict[str, Any]
    collaboration_preferences: Dict[str, Any]
    geographic_info: Dict[str, Any]
    schedule_preferences: Dict[str, Any]
    past_collaborations: List[Dict[str, Any]]


class CompatibilityAnalyzer:
    """    Advanced compatibility analyzer for content creator matching
    
    This class implements sophisticated algorithms to analyze compatibility
    between content creators across multiple dimensions using AI models
    and statistical analysis.
    """    
    def __init__(
        self,
        cache_manager: CacheManager,
        metrics_collector: MetricsCollector,
        config: Dict[str, Any]
    ):
        self.cache_manager = cache_manager
        self.metrics_collector = metrics_collector
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize analysis weights
        self.dimension_weights = {
            CompatibilityDimension.CONTENT_STYLE: 0.20,
            CompatibilityDimension.AUDIENCE_DEMOGRAPHICS: 0.15,
            CompatibilityDimension.BRAND_ALIGNMENT: 0.15,
            CompatibilityDimension.ENGAGEMENT_PATTERNS: 0.12,
            CompatibilityDimension.QUALITY_STANDARDS: 0.10,
            CompatibilityDimension.PLATFORM_PRESENCE: 0.10,
            CompatibilityDimension.COMMUNICATION_STYLE: 0.08,
            CompatibilityDimension.COLLABORATION_HISTORY: 0.05,
            CompatibilityDimension.GEOGRAPHIC_COMPATIBILITY: 0.03,
            CompatibilityDimension.SCHEDULE_ALIGNMENT: 0.02
        }
        
        # Compatibility thresholds
        self.compatibility_thresholds = {
            'excellent': 0.85,
            'good': 0.70,
            'moderate': 0.55,
            'poor': 0.40
        }
        
        # Initialize scalers
        self.scaler = MinMaxScaler()
    
    async def analyze_compatibility(
        self,
        creator_a_profile: CreatorCompatibilityProfile,
        creator_b_profile: CreatorCompatibilityProfile,
        dimensions: Optional[List[CompatibilityDimension]] = None
    ) -> CompatibilityScore:
        """        Analyze comprehensive compatibility between two creators
        
        Args:
            creator_a_profile: First creator's compatibility profile
            creator_b_profile: Second creator's compatibility profile
            dimensions: Optional specific dimensions to analyze
            
        Returns:
            Detailed compatibility score with breakdown
        """        try:
            # Use all dimensions if none specified
            if dimensions is None:
                dimensions = list(CompatibilityDimension)
            
            # Calculate dimension scores
            dimension_scores = {}
            
            for dimension in dimensions:
                score = await self._analyze_dimension(
                    creator_a_profile, creator_b_profile, dimension
                )
                dimension_scores[dimension] = score
            
            # Calculate overall weighted score
            overall_score = sum(
                score * self.dimension_weights.get(dim, 0.0)
                for dim, score in dimension_scores.items()
            )
            
            # Calculate confidence level
            confidence_level = self._calculate_confidence_level(dimension_scores)
            
            # Generate compatibility factors and risks
            compatibility_factors = self._identify_compatibility_factors(
                creator_a_profile, creator_b_profile, dimension_scores
            )
            
            incompatibility_risks = self._identify_incompatibility_risks(
                creator_a_profile, creator_b_profile, dimension_scores
            )
            
            # Generate recommendations
            recommendations = self._generate_compatibility_recommendations(
                creator_a_profile, creator_b_profile, dimension_scores
            )
            
            compatibility_score = CompatibilityScore(
                overall_score=overall_score,
                dimension_scores=dimension_scores,
                confidence_level=confidence_level,
                compatibility_factors=compatibility_factors,
                incompatibility_risks=incompatibility_risks,
                recommendations=recommendations,
                analyzed_at=datetime.utcnow()
            )
            
            # Record metrics
            self.metrics_collector.record_event(
                'compatibility_analysis_completed',
                {
                    'creator_a_id': creator_a_profile.user_id,
                    'creator_b_id': creator_b_profile.user_id,
                    'overall_score': overall_score,
                    'dimensions_analyzed': len(dimensions)
                }
            )
            
            return compatibility_score
            
        except Exception as e:
            self.logger.error(f"Error analyzing compatibility: {str(e)}")
            self.metrics_collector.record_error('compatibility_analysis_error', str(e))
            raise
    
    async def _analyze_dimension(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile,
        dimension: CompatibilityDimension
    ) -> float:
        """Analyze specific compatibility dimension"""        try:
            if dimension == CompatibilityDimension.CONTENT_STYLE:
                return self._analyze_content_style_compatibility(creator_a, creator_b)
            
            elif dimension == CompatibilityDimension.AUDIENCE_DEMOGRAPHICS:
                return self._analyze_audience_compatibility(creator_a, creator_b)
            
            elif dimension == CompatibilityDimension.BRAND_ALIGNMENT:
                return self._analyze_brand_alignment(creator_a, creator_b)
            
            elif dimension == CompatibilityDimension.ENGAGEMENT_PATTERNS:
                return self._analyze_engagement_patterns(creator_a, creator_b)
            
            elif dimension == CompatibilityDimension.QUALITY_STANDARDS:
                return self._analyze_quality_compatibility(creator_a, creator_b)
            
            elif dimension == CompatibilityDimension.PLATFORM_PRESENCE:
                return self._analyze_platform_compatibility(creator_a, creator_b)
            
            elif dimension == CompatibilityDimension.COMMUNICATION_STYLE:
                return self._analyze_communication_compatibility(creator_a, creator_b)
            
            elif dimension == CompatibilityDimension.COLLABORATION_HISTORY:
                return self._analyze_collaboration_history(creator_a, creator_b)
            
            elif dimension == CompatibilityDimension.GEOGRAPHIC_COMPATIBILITY:
                return self._analyze_geographic_compatibility(creator_a, creator_b)
            
            elif dimension == CompatibilityDimension.SCHEDULE_ALIGNMENT:
                return self._analyze_schedule_alignment(creator_a, creator_b)
            
            else:
                self.logger.warning(f"Unknown dimension: {dimension}")
                return 0.0
                
        except Exception as e:
            self.logger.error(f"Error analyzing dimension {dimension}: {str(e)}")
            return 0.0
    
    def _analyze_content_style_compatibility(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> float:
        """Analyze content style compatibility using vector similarity"""        try:
            # Calculate cosine similarity between content style vectors
            similarity = cosine_similarity(
                creator_a.content_style_vector.reshape(1, -1),
                creator_b.content_style_vector.reshape(1, -1)
            )[0][0]
            
            # Normalize to 0-1 range
            normalized_score = (similarity + 1) / 2
            
            return max(0.0, min(1.0, normalized_score))
            
        except Exception as e:
            self.logger.error(f"Error analyzing content style: {str(e)}")
            return 0.0
    
    def _analyze_audience_compatibility(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> float:
        """Analyze audience demographic compatibility"""        try:
            audience_a = creator_a.audience_profile
            audience_b = creator_b.audience_profile
            
            compatibility_score = 0.0
            factors_analyzed = 0
            
            # Age distribution compatibility
            if 'age_distribution' in audience_a and 'age_distribution' in audience_b:
                age_compatibility = self._calculate_distribution_overlap(
                    audience_a['age_distribution'],
                    audience_b['age_distribution']
                )
                compatibility_score += age_compatibility * 0.3
                factors_analyzed += 1
            
            # Gender distribution compatibility
            if 'gender_distribution' in audience_a and 'gender_distribution' in audience_b:
                gender_compatibility = self._calculate_distribution_overlap(
                    audience_a['gender_distribution'],
                    audience_b['gender_distribution']
                )
                compatibility_score += gender_compatibility * 0.2
                factors_analyzed += 1
            
            # Interest overlap
            if 'interests' in audience_a and 'interests' in audience_b:
                interest_overlap = self._calculate_interest_overlap(
                    audience_a['interests'],
                    audience_b['interests']
                )
                compatibility_score += interest_overlap * 0.3
                factors_analyzed += 1
            
            # Geographic distribution
            if 'geographic_distribution' in audience_a and 'geographic_distribution' in audience_b:
                geo_compatibility = self._calculate_distribution_overlap(
                    audience_a['geographic_distribution'],
                    audience_b['geographic_distribution']
                )
                compatibility_score += geo_compatibility * 0.2
                factors_analyzed += 1
            
            return compatibility_score / factors_analyzed if factors_analyzed > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing audience compatibility: {str(e)}")
            return 0.0
    
    def _analyze_brand_alignment(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> float:
        """Analyze brand values and aesthetic alignment"""        try:
            brand_a = creator_a.brand_attributes
            brand_b = creator_b.brand_attributes
            
            alignment_score = 0.0
            factors_analyzed = 0
            
            # Brand values alignment
            if 'values' in brand_a and 'values' in brand_b:
                values_alignment = self._calculate_values_alignment(
                    brand_a['values'],
                    brand_b['values']
                )
                alignment_score += values_alignment * 0.4
                factors_analyzed += 1
            
            # Aesthetic compatibility
            if 'aesthetic_style' in brand_a and 'aesthetic_style' in brand_b:
                aesthetic_compatibility = self._calculate_aesthetic_compatibility(
                    brand_a['aesthetic_style'],
                    brand_b['aesthetic_style']
                )
                alignment_score += aesthetic_compatibility * 0.3
                factors_analyzed += 1
            
            # Brand tone compatibility
            if 'communication_tone' in brand_a and 'communication_tone' in brand_b:
                tone_compatibility = self._calculate_tone_compatibility(
                    brand_a['communication_tone'],
                    brand_b['communication_tone']
                )
                alignment_score += tone_compatibility * 0.3
                factors_analyzed += 1
            
            return alignment_score / factors_analyzed if factors_analyzed > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing brand alignment: {str(e)}")
            return 0.0
    
    def _analyze_engagement_patterns(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> float:
        """Analyze engagement pattern compatibility"""        try:
            patterns_a = creator_a.engagement_patterns
            patterns_b = creator_b.engagement_patterns
            
            compatibility_score = 0.0
            factors_analyzed = 0
            
            # Posting frequency compatibility
            if 'posting_frequency' in patterns_a and 'posting_frequency' in patterns_b:
                freq_compatibility = self._calculate_frequency_compatibility(
                    patterns_a['posting_frequency'],
                    patterns_b['posting_frequency']
                )
                compatibility_score += freq_compatibility * 0.3
                factors_analyzed += 1
            
            # Engagement timing patterns
            if 'optimal_posting_times' in patterns_a and 'optimal_posting_times' in patterns_b:
                timing_compatibility = self._calculate_timing_compatibility(
                    patterns_a['optimal_posting_times'],
                    patterns_b['optimal_posting_times']
                )
                compatibility_score += timing_compatibility * 0.3
                factors_analyzed += 1
            
            # Audience engagement levels
            if 'engagement_rates' in patterns_a and 'engagement_rates' in patterns_b:
                engagement_compatibility = self._calculate_engagement_level_compatibility(
                    patterns_a['engagement_rates'],
                    patterns_b['engagement_rates']
                )
                compatibility_score += engagement_compatibility * 0.4
                factors_analyzed += 1
            
            return compatibility_score / factors_analyzed if factors_analyzed > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error analyzing engagement patterns: {str(e)}")
            return 0.0
    
    def _analyze_quality_compatibility(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> float:
        """Analyze content quality standards compatibility"""        try:
            quality_a = creator_a.quality_metrics
            quality_b = creator_b.quality_metrics
            
            if not quality_a or not quality_b:
                return 0.5  # Neutral score if no data
            
            quality_scores = []
            
            # Compare quality metrics
            for metric in ['content_quality', 'production_value', 'consistency', 'originality']:
                if metric in quality_a and metric in quality_b:
                    # Calculate compatibility based on quality level similarity
                    score_diff = abs(quality_a[metric] - quality_b[metric])
                    compatibility = 1.0 - score_diff  # Lower difference = higher compatibility
                    quality_scores.append(max(0.0, compatibility))
            
            return np.mean(quality_scores) if quality_scores else 0.5
            
        except Exception as e:
            self.logger.error(f"Error analyzing quality compatibility: {str(e)}")
            return 0.0
    
    def _analyze_platform_compatibility(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> float:
        """Analyze platform presence compatibility"""        try:
            platforms_a = set(creator_a.platform_analytics.keys())
            platforms_b = set(creator_b.platform_analytics.keys())
            
            # Calculate platform overlap
            common_platforms = platforms_a.intersection(platforms_b)
            total_platforms = platforms_a.union(platforms_b)
            
            if not total_platforms:
                return 0.0
            
            # Base compatibility on overlap
            overlap_score = len(common_platforms) / len(total_platforms)
            
            # Bonus for complementary platforms
            complementary_platforms = platforms_a.symmetric_difference(platforms_b)
            complementary_bonus = min(0.3, len(complementary_platforms) * 0.1)
            
            return min(1.0, overlap_score + complementary_bonus)
            
        except Exception as e:
            self.logger.error(f"Error analyzing platform compatibility: {str(e)}")
            return 0.0
    
    def _analyze_communication_compatibility(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> float:
        """Analyze communication style compatibility"""        try:
            comm_a = creator_a.communication_preferences
            comm_b = creator_b.communication_preferences
            
            compatibility_score = 0.0
            factors_analyzed = 0
            
            # Response time compatibility
            if 'response_time_preference' in comm_a and 'response_time_preference' in comm_b:
                response_compatibility = self._calculate_response_time_compatibility(
                    comm_a['response_time_preference'],
                    comm_b['response_time_preference']
                )
                compatibility_score += response_compatibility * 0.3
                factors_analyzed += 1
            
            # Communication channel preferences
            if 'preferred_channels' in comm_a and 'preferred_channels' in comm_b:
                channel_compatibility = self._calculate_channel_compatibility(
                    comm_a['preferred_channels'],
                    comm_b['preferred_channels']
                )
                compatibility_score += channel_compatibility * 0.4
                factors_analyzed += 1
            
            # Meeting preferences
            if 'meeting_preferences' in comm_a and 'meeting_preferences' in comm_b:
                meeting_compatibility = self._calculate_meeting_compatibility(
                    comm_a['meeting_preferences'],
                    comm_b['meeting_preferences']
                )
                compatibility_score += meeting_compatibility * 0.3
                factors_analyzed += 1
            
            return compatibility_score / factors_analyzed if factors_analyzed > 0 else 0.5
            
        except Exception as e:
            self.logger.error(f"Error analyzing communication compatibility: {str(e)}")
            return 0.0
    
    def _analyze_collaboration_history(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> float:
        """Analyze collaboration history and success patterns"""        try:
            # Check if creators have collaborated before
            past_collaborations = self._find_past_collaborations(creator_a, creator_b)
            
            if past_collaborations:
                # Analyze success of past collaborations
                success_scores = [collab.get('success_score', 0.5) for collab in past_collaborations]
                return np.mean(success_scores)
            
            # Analyze collaboration patterns with similar creators
            pattern_compatibility = self._analyze_collaboration_patterns(creator_a, creator_b)
            
            return pattern_compatibility
            
        except Exception as e:
            self.logger.error(f"Error analyzing collaboration history: {str(e)}")
            return 0.5
    
    def _analyze_geographic_compatibility(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> float:
        """Analyze geographic compatibility for collaboration"""        try:
            geo_a = creator_a.geographic_info
            geo_b = creator_b.geographic_info
            
            if not geo_a or not geo_b:
                return 0.5  # Neutral if no geographic data
            
            # Time zone compatibility
            timezone_compatibility = self._calculate_timezone_compatibility(
                geo_a.get('timezone'),
                geo_b.get('timezone')
            )
            
            # Physical proximity (for in-person collaborations)
            proximity_score = self._calculate_proximity_score(
                geo_a.get('location'),
                geo_b.get('location')
            )
            
            # Weighted average
            return timezone_compatibility * 0.7 + proximity_score * 0.3
            
        except Exception as e:
            self.logger.error(f"Error analyzing geographic compatibility: {str(e)}")
            return 0.0
    
    def _analyze_schedule_alignment(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile
    ) -> float:
        """Analyze schedule and availability alignment"""        try:
            schedule_a = creator_a.schedule_preferences
            schedule_b = creator_b.schedule_preferences
            
            if not schedule_a or not schedule_b:
                return 0.5  # Neutral if no schedule data
            
            # Working hours overlap
            hours_overlap = self._calculate_working_hours_overlap(
                schedule_a.get('working_hours'),
                schedule_b.get('working_hours')
            )
            
            # Availability patterns
            availability_compatibility = self._calculate_availability_compatibility(
                schedule_a.get('availability_pattern'),
                schedule_b.get('availability_pattern')
            )
            
            # Deadline preferences
            deadline_compatibility = self._calculate_deadline_compatibility(
                schedule_a.get('deadline_preferences'),
                schedule_b.get('deadline_preferences')
            )
            
            # Weighted average
            return (hours_overlap * 0.4 + 
                   availability_compatibility * 0.4 + 
                   deadline_compatibility * 0.2)
            
        except Exception as e:
            self.logger.error(f"Error analyzing schedule alignment: {str(e)}")
            return 0.0
    
    # Helper methods for compatibility calculations
    
    def _calculate_distribution_overlap(
        self,
        dist_a: Dict[str, float],
        dist_b: Dict[str, float]
    ) -> float:
        """Calculate overlap between two distributions"""        try:
            all_keys = set(dist_a.keys()).union(set(dist_b.keys()))
            overlap = 0.0
            
            for key in all_keys:
                val_a = dist_a.get(key, 0.0)
                val_b = dist_b.get(key, 0.0)
                overlap += min(val_a, val_b)
            
            return overlap
            
        except Exception:
            return 0.0
    
    def _calculate_interest_overlap(
        self,
        interests_a: List[str],
        interests_b: List[str]
    ) -> float:
        """Calculate interest overlap using Jaccard similarity"""        try:
            set_a = set(interests_a)
            set_b = set(interests_b)
            
            intersection = len(set_a.intersection(set_b))
            union = len(set_a.union(set_b))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_confidence_level(
        self,
        dimension_scores: Dict[CompatibilityDimension, float]
    ) -> float:
        """Calculate confidence level based on score consistency"""        try:
            scores = list(dimension_scores.values())
            if not scores:
                return 0.0
            
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            
            # Higher consistency = higher confidence
            confidence = mean_score * (1 - std_score)
            
            return max(0.0, min(1.0, confidence))
            
        except Exception:
            return 0.0
    
    def _identify_compatibility_factors(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile,
        dimension_scores: Dict[CompatibilityDimension, float]
    ) -> List[str]:
        """Identify key compatibility factors"""        factors = []
        
        for dimension, score in dimension_scores.items():
            if score > 0.75:
                if dimension == CompatibilityDimension.CONTENT_STYLE:
                    factors.append("Highly compatible content styles")
                elif dimension == CompatibilityDimension.AUDIENCE_DEMOGRAPHICS:
                    factors.append("Strong audience overlap and complementarity")
                elif dimension == CompatibilityDimension.BRAND_ALIGNMENT:
                    factors.append("Excellent brand values alignment")
                # Add more factor descriptions
        
        return factors
    
    def _identify_incompatibility_risks(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile,
        dimension_scores: Dict[CompatibilityDimension, float]
    ) -> List[str]:
        """Identify potential incompatibility risks"""        risks = []
        
        for dimension, score in dimension_scores.items():
            if score < 0.40:
                if dimension == CompatibilityDimension.QUALITY_STANDARDS:
                    risks.append("Significant quality standards mismatch")
                elif dimension == CompatibilityDimension.BRAND_ALIGNMENT:
                    risks.append("Potential brand values conflict")
                elif dimension == CompatibilityDimension.COMMUNICATION_STYLE:
                    risks.append("Communication style incompatibility")
                # Add more risk descriptions
        
        return risks
    
    def _generate_compatibility_recommendations(
        self,
        creator_a: CreatorCompatibilityProfile,
        creator_b: CreatorCompatibilityProfile,
        dimension_scores: Dict[CompatibilityDimension, float]
    ) -> List[str]:
        """Generate recommendations to improve compatibility"""        recommendations = []
        
        for dimension, score in dimension_scores.items():
            if 0.40 <= score < 0.70:
                if dimension == CompatibilityDimension.ENGAGEMENT_PATTERNS:
                    recommendations.append("Consider synchronizing posting schedules")
                elif dimension == CompatibilityDimension.PLATFORM_PRESENCE:
                    recommendations.append("Explore cross-platform promotion opportunities")
                # Add more recommendations
        
        return recommendations
    
    # Additional helper methods would be implemented for:
    # - _calculate_values_alignment
    # - _calculate_aesthetic_compatibility
    # - _calculate_tone_compatibility
    # - _calculate_frequency_compatibility
    # - _calculate_timing_compatibility
    # - _calculate_engagement_level_compatibility
    # - _calculate_response_time_compatibility
    # - _calculate_channel_compatibility
    # - _calculate_meeting_compatibility
    # - _find_past_collaborations
    # - _analyze_collaboration_patterns
    # - _calculate_timezone_compatibility
    # - _calculate_proximity_score
    # - _calculate_working_hours_overlap
    # - _calculate_availability_compatibility
    # - _calculate_deadline_compatibility
