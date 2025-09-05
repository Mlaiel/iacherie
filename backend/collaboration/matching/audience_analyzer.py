"""Audience Analyzer - Advanced Audience Overlap and Demographic Analysis
========================================================================

Sophisticated audience analysis system for creator collaboration optimization:
- Demographic overlap analysis
- Audience engagement patterns  
- Cross-platform audience mapping
- Psychographic profiling
- Market segment identification
- Audience growth prediction

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class AudienceSegment(Enum):
    """Audience demographic segments"""
    TEENS_13_17 = "teens_13_17"
    YOUNG_ADULTS_18_24 = "young_adults_18_24"
    ADULTS_25_34 = "adults_25_34"
    ADULTS_35_44 = "adults_35_44"
    ADULTS_45_54 = "adults_45_54"
    SENIORS_55_PLUS = "seniors_55_plus"


class InterestCategory(Enum):
    """Audience interest categories"""
    ENTERTAINMENT = "entertainment"
    TECHNOLOGY = "technology"
    FASHION = "fashion"
    SPORTS = "sports"
    MUSIC = "music"
    GAMING = "gaming"
    FOOD = "food"
    TRAVEL = "travel"
    FITNESS = "fitness"
    EDUCATION = "education"
    BUSINESS = "business"
    LIFESTYLE = "lifestyle"


@dataclass
class DemographicProfile:
    """Comprehensive demographic profile"""
    creator_id: str
    age_distribution: Dict[AudienceSegment, float] = field(default_factory=dict)
    gender_distribution: Dict[str, float] = field(default_factory=dict)
    location_distribution: Dict[str, float] = field(default_factory=dict)
    income_distribution: Dict[str, float] = field(default_factory=dict)
    education_distribution: Dict[str, float] = field(default_factory=dict)
    interest_distribution: Dict[InterestCategory, float] = field(default_factory=dict)
    device_distribution: Dict[str, float] = field(default_factory=dict)
    language_distribution: Dict[str, float] = field(default_factory=dict)
    timezone_distribution: Dict[str, float] = field(default_factory=dict)
    platform_usage: Dict[str, float] = field(default_factory=dict)
    
    def get_primary_segment(self) -> AudienceSegment:
        """Get primary audience segment"""
        if self.age_distribution:
            return max(self.age_distribution.items(), key=lambda x: x[1])[0]
        return AudienceSegment.ADULTS_25_34
    
    def get_diversity_score(self) -> float:
        """Calculate audience diversity score"""
        distributions = [
            self.age_distribution,
            self.gender_distribution,
            self.location_distribution,
            self.interest_distribution
        ]
        
        diversity_scores = []
        for dist in distributions:
            if dist:
                # Calculate Shannon entropy for diversity
                values = list(dist.values())
                total = sum(values)
                if total > 0:
                    normalized = [v/total for v in values]
                    entropy = -sum(p * np.log2(p) for p in normalized if p > 0)
                    max_entropy = np.log2(len(values))
                    diversity = entropy / max_entropy if max_entropy > 0 else 0
                    diversity_scores.append(diversity)
        
        return np.mean(diversity_scores) if diversity_scores else 0.0


@dataclass
class AudienceOverlap:
    """Audience overlap analysis between creators"""
    creator_a_id: str
    creator_b_id: str
    overlap_percentage: float
    overlap_size: int
    unique_to_a: int
    unique_to_b: int
    shared_segments: Dict[str, float] = field(default_factory=dict)
    overlap_quality: float = 0.0
    demographic_similarity: float = 0.0
    interest_alignment: float = 0.0
    geographic_overlap: float = 0.0
    temporal_overlap: float = 0.0
    
    def get_collaboration_potential(self) -> str:
        """Assess collaboration potential based on overlap"""
        if self.overlap_percentage > 0.7:
            return "high_cannibalization_risk"
        elif self.overlap_percentage > 0.4:
            return "moderate_overlap_good_synergy"
        elif self.overlap_percentage > 0.1:
            return "complementary_audiences"
        else:
            return "distinct_audiences_cross_promotion"


@dataclass
class AudienceInsights:
    """Deep audience insights and recommendations"""
    creator_id: str
    audience_size: int
    engagement_rate: float
    growth_rate: float
    audience_quality_score: float
    brand_affinity: Dict[str, float] = field(default_factory=dict)
    purchase_intent: Dict[str, float] = field(default_factory=dict)
    content_preferences: Dict[str, float] = field(default_factory=dict)
    optimal_posting_times: List[str] = field(default_factory=list)
    trending_topics: List[str] = field(default_factory=list)
    competitor_overlap: Dict[str, float] = field(default_factory=dict)
    collaboration_opportunities: List[str] = field(default_factory=list)


@dataclass
class OverlapMetrics:
    """Detailed overlap metrics"""
    jaccard_index: float
    cosine_similarity: float
    pearson_correlation: float
    mutual_information: float
    kl_divergence: float
    demographic_distance: float
    engagement_similarity: float
    content_affinity: float


class AudienceAnalyzer:
    """
    Advanced audience analysis engine for creator collaboration optimization
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize audience analyzer"""
        self.config = config or {}
        self.audience_cache = {}
        self.overlap_cache = {}
        self.demographic_models = {}
        self.similarity_threshold = self.config.get('similarity_threshold', 0.7)
        self.min_audience_size = self.config.get('min_audience_size', 1000)
        
        # Initialize demographic analysis models
        self.segment_weights = {
            AudienceSegment.TEENS_13_17: 0.8,      # High engagement
            AudienceSegment.YOUNG_ADULTS_18_24: 1.0,  # Premium segment
            AudienceSegment.ADULTS_25_34: 0.9,     # High value
            AudienceSegment.ADULTS_35_44: 0.7,     # Moderate engagement
            AudienceSegment.ADULTS_45_54: 0.6,     # Lower engagement
            AudienceSegment.SENIORS_55_PLUS: 0.5   # Lowest engagement
        }
        
        logger.info("📊 Audience Analyzer initialized")
    
    async def analyze_audience_profile(self, creator_profile: Dict[str, Any]) -> DemographicProfile:
        """Analyze comprehensive audience demographic profile"""
        try:
            creator_id = creator_profile['creator_id']
            
            # Check cache first
            if creator_id in self.audience_cache:
                return self.audience_cache[creator_id]
            
            profile = DemographicProfile(creator_id=creator_id)
            
            # Extract audience data
            audience_data = creator_profile.get('audience_analytics', {})
            
            # Age distribution
            age_data = audience_data.get('age_distribution', {})
            for segment_str, percentage in age_data.items():
                try:
                    segment = AudienceSegment(segment_str)
                    profile.age_distribution[segment] = float(percentage)
                except ValueError:
                    continue
            
            # Gender distribution
            gender_data = audience_data.get('gender_distribution', {})
            profile.gender_distribution = {k: float(v) for k, v in gender_data.items()}
            
            # Location distribution
            location_data = audience_data.get('location_distribution', {})
            profile.location_distribution = {k: float(v) for k, v in location_data.items()}
            
            # Income distribution
            income_data = audience_data.get('income_distribution', {})
            profile.income_distribution = {k: float(v) for k, v in income_data.items()}
            
            # Education distribution
            education_data = audience_data.get('education_distribution', {})
            profile.education_distribution = {k: float(v) for k, v in education_data.items()}
            
            # Interest distribution
            interest_data = audience_data.get('interest_distribution', {})
            for interest_str, percentage in interest_data.items():
                try:
                    interest = InterestCategory(interest_str)
                    profile.interest_distribution[interest] = float(percentage)
                except ValueError:
                    continue
            
            # Device distribution
            device_data = audience_data.get('device_distribution', {})
            profile.device_distribution = {k: float(v) for k, v in device_data.items()}
            
            # Language distribution
            language_data = audience_data.get('language_distribution', {})
            profile.language_distribution = {k: float(v) for k, v in language_data.items()}
            
            # Timezone distribution
            timezone_data = audience_data.get('timezone_distribution', {})
            profile.timezone_distribution = {k: float(v) for k, v in timezone_data.items()}
            
            # Platform usage
            platform_data = audience_data.get('platform_usage', {})
            profile.platform_usage = {k: float(v) for k, v in platform_data.items()}
            
            # Cache the profile
            self.audience_cache[creator_id] = profile
            
            return profile
            
        except Exception as e:
            logger.error(f"❌ Error analyzing audience profile: {e}")
            return DemographicProfile(creator_id=creator_profile.get('creator_id', 'unknown'))
    
    async def calculate_audience_overlap(
        self,
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any]
    ) -> AudienceOverlap:
        """Calculate detailed audience overlap between two creators"""
        try:
            creator_a_id = creator_a['creator_id']
            creator_b_id = creator_b['creator_id']
            
            # Check cache
            cache_key = f"{creator_a_id}_{creator_b_id}"
            if cache_key in self.overlap_cache:
                return self.overlap_cache[cache_key]
            
            # Get demographic profiles
            profile_a = await self.analyze_audience_profile(creator_a)
            profile_b = await self.analyze_audience_profile(creator_b)
            
            # Calculate overlap metrics
            overlap_metrics = await self._calculate_overlap_metrics(profile_a, profile_b)
            
            # Get audience sizes
            audience_a_size = creator_a.get('audience_analytics', {}).get('total_audience', 0)
            audience_b_size = creator_b.get('audience_analytics', {}).get('total_audience', 0)
            
            # Estimate overlap size (simplified calculation)
            estimated_overlap_size = int(
                min(audience_a_size, audience_b_size) * overlap_metrics.jaccard_index
            )
            
            # Calculate unique audiences
            unique_to_a = audience_a_size - estimated_overlap_size
            unique_to_b = audience_b_size - estimated_overlap_size
            
            # Calculate overlap percentage
            total_combined = unique_to_a + unique_to_b + estimated_overlap_size
            overlap_percentage = estimated_overlap_size / total_combined if total_combined > 0 else 0
            
            # Analyze shared segments
            shared_segments = await self._analyze_shared_segments(profile_a, profile_b)
            
            # Calculate demographic similarity
            demographic_similarity = await self._calculate_demographic_similarity(profile_a, profile_b)
            
            # Calculate interest alignment
            interest_alignment = await self._calculate_interest_alignment(profile_a, profile_b)
            
            # Calculate geographic overlap
            geographic_overlap = await self._calculate_geographic_overlap(profile_a, profile_b)
            
            # Calculate temporal overlap
            temporal_overlap = await self._calculate_temporal_overlap(profile_a, profile_b)
            
            # Calculate overlap quality (engagement potential)
            overlap_quality = await self._calculate_overlap_quality(
                creator_a, creator_b, overlap_metrics
            )
            
            overlap = AudienceOverlap(
                creator_a_id=creator_a_id,
                creator_b_id=creator_b_id,
                overlap_percentage=overlap_percentage,
                overlap_size=estimated_overlap_size,
                unique_to_a=unique_to_a,
                unique_to_b=unique_to_b,
                shared_segments=shared_segments,
                overlap_quality=overlap_quality,
                demographic_similarity=demographic_similarity,
                interest_alignment=interest_alignment,
                geographic_overlap=geographic_overlap,
                temporal_overlap=temporal_overlap
            )
            
            # Cache the result
            self.overlap_cache[cache_key] = overlap
            
            return overlap
            
        except Exception as e:
            logger.error(f"❌ Error calculating audience overlap: {e}")
            return AudienceOverlap(
                creator_a_id=creator_a.get('creator_id', 'unknown'),
                creator_b_id=creator_b.get('creator_id', 'unknown'),
                overlap_percentage=0.0,
                overlap_size=0,
                unique_to_a=0,
                unique_to_b=0
            )
    
    async def _calculate_overlap_metrics(
        self,
        profile_a: DemographicProfile,
        profile_b: DemographicProfile
    ) -> OverlapMetrics:
        """Calculate various overlap metrics"""
        
        # Jaccard Index for age distribution
        jaccard_index = self._calculate_jaccard_similarity(
            profile_a.age_distribution,
            profile_b.age_distribution
        )
        
        # Cosine similarity for interests
        cosine_similarity = self._calculate_cosine_similarity(
            profile_a.interest_distribution,
            profile_b.interest_distribution
        )
        
        # Pearson correlation for demographic distributions
        pearson_correlation = self._calculate_pearson_correlation(
            profile_a.gender_distribution,
            profile_b.gender_distribution
        )
        
        # Mutual information for location overlap
        mutual_information = self._calculate_mutual_information(
            profile_a.location_distribution,
            profile_b.location_distribution
        )
        
        # KL divergence for overall demographic distance
        kl_divergence = self._calculate_kl_divergence(
            profile_a.age_distribution,
            profile_b.age_distribution
        )
        
        # Demographic distance (composite metric)
        demographic_distance = 1.0 - np.mean([
            jaccard_index,
            cosine_similarity,
            1.0 - min(kl_divergence, 1.0)  # Invert KL divergence
        ])
        
        # Engagement similarity (based on audience quality)
        engagement_similarity = self._calculate_engagement_similarity(profile_a, profile_b)
        
        # Content affinity (based on interest overlap)
        content_affinity = cosine_similarity
        
        return OverlapMetrics(
            jaccard_index=jaccard_index,
            cosine_similarity=cosine_similarity,
            pearson_correlation=pearson_correlation,
            mutual_information=mutual_information,
            kl_divergence=kl_divergence,
            demographic_distance=demographic_distance,
            engagement_similarity=engagement_similarity,
            content_affinity=content_affinity
        )
    
    def _calculate_jaccard_similarity(
        self,
        dist_a: Dict[Any, float],
        dist_b: Dict[Any, float]
    ) -> float:
        """Calculate Jaccard similarity between two distributions"""
        if not dist_a or not dist_b:
            return 0.0
        
        keys_a = set(dist_a.keys())
        keys_b = set(dist_b.keys())
        
        intersection = len(keys_a & keys_b)
        union = len(keys_a | keys_b)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_cosine_similarity(
        self,
        dist_a: Dict[Any, float],
        dist_b: Dict[Any, float]
    ) -> float:
        """Calculate cosine similarity between two distributions"""
        if not dist_a or not dist_b:
            return 0.0
        
        # Get common keys
        all_keys = set(dist_a.keys()) | set(dist_b.keys())
        
        vec_a = np.array([dist_a.get(key, 0.0) for key in all_keys])
        vec_b = np.array([dist_b.get(key, 0.0) for key in all_keys])
        
        # Calculate cosine similarity
        dot_product = np.dot(vec_a, vec_b)
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def _calculate_pearson_correlation(
        self,
        dist_a: Dict[Any, float],
        dist_b: Dict[Any, float]
    ) -> float:
        """Calculate Pearson correlation between two distributions"""
        if not dist_a or not dist_b:
            return 0.0
        
        all_keys = set(dist_a.keys()) | set(dist_b.keys())
        
        if len(all_keys) < 2:
            return 0.0
        
        vec_a = np.array([dist_a.get(key, 0.0) for key in all_keys])
        vec_b = np.array([dist_b.get(key, 0.0) for key in all_keys])
        
        try:
            correlation = np.corrcoef(vec_a, vec_b)[0, 1]
            return correlation if not np.isnan(correlation) else 0.0
        except:
            return 0.0
    
    def _calculate_mutual_information(
        self,
        dist_a: Dict[Any, float],
        dist_b: Dict[Any, float]
    ) -> float:
        """Calculate mutual information between two distributions"""
        if not dist_a or not dist_b:
            return 0.0
        
        # Simplified mutual information calculation
        common_keys = set(dist_a.keys()) & set(dist_b.keys())
        
        if not common_keys:
            return 0.0
        
        mi = 0.0
        for key in common_keys:
            p_a = dist_a[key]
            p_b = dist_b[key]
            p_joint = min(p_a, p_b)  # Simplified joint probability
            
            if p_a > 0 and p_b > 0 and p_joint > 0:
                mi += p_joint * np.log2(p_joint / (p_a * p_b))
        
        return max(0.0, mi)
    
    def _calculate_kl_divergence(
        self,
        dist_a: Dict[Any, float],
        dist_b: Dict[Any, float]
    ) -> float:
        """Calculate KL divergence between two distributions"""
        if not dist_a or not dist_b:
            return 1.0  # Maximum divergence
        
        all_keys = set(dist_a.keys()) | set(dist_b.keys())
        
        # Normalize distributions
        sum_a = sum(dist_a.values())
        sum_b = sum(dist_b.values())
        
        if sum_a == 0 or sum_b == 0:
            return 1.0
        
        kl_div = 0.0
        for key in all_keys:
            p = dist_a.get(key, 0.0) / sum_a
            q = dist_b.get(key, 0.0) / sum_b
            
            if p > 0:
                if q > 0:
                    kl_div += p * np.log2(p / q)
                else:
                    kl_div += p * np.log2(p / 1e-10)  # Add small epsilon
        
        return min(kl_div, 10.0)  # Cap at reasonable maximum
    
    def _calculate_engagement_similarity(
        self,
        profile_a: DemographicProfile,
        profile_b: DemographicProfile
    ) -> float:
        """Calculate engagement similarity based on audience quality"""
        
        # Calculate weighted engagement score for each profile
        score_a = self._calculate_weighted_engagement_score(profile_a)
        score_b = self._calculate_weighted_engagement_score(profile_b)
        
        # Calculate similarity (inverse of difference)
        difference = abs(score_a - score_b)
        similarity = 1.0 / (1.0 + difference)
        
        return similarity
    
    def _calculate_weighted_engagement_score(self, profile: DemographicProfile) -> float:
        """Calculate weighted engagement score for a profile"""
        score = 0.0
        total_weight = 0.0
        
        for segment, percentage in profile.age_distribution.items():
            weight = self.segment_weights.get(segment, 0.5)
            score += percentage * weight
            total_weight += percentage
        
        return score / total_weight if total_weight > 0 else 0.5
    
    async def _analyze_shared_segments(
        self,
        profile_a: DemographicProfile,
        profile_b: DemographicProfile
    ) -> Dict[str, float]:
        """Analyze shared audience segments"""
        shared_segments = {}
        
        # Age segments
        for segment in AudienceSegment:
            percent_a = profile_a.age_distribution.get(segment, 0.0)
            percent_b = profile_b.age_distribution.get(segment, 0.0)
            
            if percent_a > 0 and percent_b > 0:
                shared_segments[f"age_{segment.value}"] = min(percent_a, percent_b)
        
        # Interest segments
        for interest in InterestCategory:
            percent_a = profile_a.interest_distribution.get(interest, 0.0)
            percent_b = profile_b.interest_distribution.get(interest, 0.0)
            
            if percent_a > 0 and percent_b > 0:
                shared_segments[f"interest_{interest.value}"] = min(percent_a, percent_b)
        
        # Geographic segments
        common_locations = set(profile_a.location_distribution.keys()) & set(profile_b.location_distribution.keys())
        for location in common_locations:
            percent_a = profile_a.location_distribution[location]
            percent_b = profile_b.location_distribution[location]
            shared_segments[f"location_{location}"] = min(percent_a, percent_b)
        
        return shared_segments
    
    async def _calculate_demographic_similarity(
        self,
        profile_a: DemographicProfile,
        profile_b: DemographicProfile
    ) -> float:
        """Calculate overall demographic similarity"""
        
        similarities = []
        
        # Age similarity
        age_sim = self._calculate_cosine_similarity(
            profile_a.age_distribution,
            profile_b.age_distribution
        )
        similarities.append(age_sim * 0.3)  # 30% weight
        
        # Gender similarity
        gender_sim = self._calculate_cosine_similarity(
            profile_a.gender_distribution,
            profile_b.gender_distribution
        )
        similarities.append(gender_sim * 0.2)  # 20% weight
        
        # Location similarity
        location_sim = self._calculate_cosine_similarity(
            profile_a.location_distribution,
            profile_b.location_distribution
        )
        similarities.append(location_sim * 0.25)  # 25% weight
        
        # Income similarity
        income_sim = self._calculate_cosine_similarity(
            profile_a.income_distribution,
            profile_b.income_distribution
        )
        similarities.append(income_sim * 0.25)  # 25% weight
        
        return sum(similarities)
    
    async def _calculate_interest_alignment(
        self,
        profile_a: DemographicProfile,
        profile_b: DemographicProfile
    ) -> float:
        """Calculate interest alignment between audiences"""
        return self._calculate_cosine_similarity(
            profile_a.interest_distribution,
            profile_b.interest_distribution
        )
    
    async def _calculate_geographic_overlap(
        self,
        profile_a: DemographicProfile,
        profile_b: DemographicProfile
    ) -> float:
        """Calculate geographic audience overlap"""
        return self._calculate_cosine_similarity(
            profile_a.location_distribution,
            profile_b.location_distribution
        )
    
    async def _calculate_temporal_overlap(
        self,
        profile_a: DemographicProfile,
        profile_b: DemographicProfile
    ) -> float:
        """Calculate temporal audience overlap (timezone alignment)"""
        return self._calculate_cosine_similarity(
            profile_a.timezone_distribution,
            profile_b.timezone_distribution
        )
    
    async def _calculate_overlap_quality(
        self,
        creator_a: Dict[str, Any],
        creator_b: Dict[str, Any],
        overlap_metrics: OverlapMetrics
    ) -> float:
        """Calculate the quality of audience overlap for collaboration"""
        
        quality_factors = []
        
        # Engagement rate factor
        engagement_a = creator_a.get('engagement_rate', 0.0)
        engagement_b = creator_b.get('engagement_rate', 0.0)
        avg_engagement = (engagement_a + engagement_b) / 2
        quality_factors.append(min(avg_engagement * 10, 1.0))  # Normalize to 0-1
        
        # Audience size factor (prefer complementary sizes)
        size_a = creator_a.get('audience_analytics', {}).get('total_audience', 0)
        size_b = creator_b.get('audience_analytics', {}).get('total_audience', 0)
        
        if size_a > 0 and size_b > 0:
            size_ratio = min(size_a, size_b) / max(size_a, size_b)
            quality_factors.append(size_ratio)  # Higher is better for balanced collaboration
        
        # Content affinity factor
        quality_factors.append(overlap_metrics.content_affinity)
        
        # Demographic diversity factor
        quality_factors.append(1.0 - overlap_metrics.demographic_distance)
        
        return np.mean(quality_factors)
    
    async def generate_audience_insights(self, creator_profile: Dict[str, Any]) -> AudienceInsights:
        """Generate comprehensive audience insights and recommendations"""
        try:
            creator_id = creator_profile['creator_id']
            
            # Get demographic profile
            demographic_profile = await self.analyze_audience_profile(creator_profile)
            
            # Extract audience analytics
            audience_analytics = creator_profile.get('audience_analytics', {})
            
            insights = AudienceInsights(
                creator_id=creator_id,
                audience_size=audience_analytics.get('total_audience', 0),
                engagement_rate=creator_profile.get('engagement_rate', 0.0),
                growth_rate=audience_analytics.get('growth_rate', 0.0),
                audience_quality_score=self._calculate_weighted_engagement_score(demographic_profile)
            )
            
            # Brand affinity analysis
            insights.brand_affinity = await self._analyze_brand_affinity(creator_profile)
            
            # Purchase intent analysis
            insights.purchase_intent = await self._analyze_purchase_intent(creator_profile)
            
            # Content preferences
            insights.content_preferences = await self._analyze_content_preferences(creator_profile)
            
            # Optimal posting times
            insights.optimal_posting_times = await self._analyze_optimal_posting_times(creator_profile)
            
            # Trending topics
            insights.trending_topics = await self._analyze_trending_topics(creator_profile)
            
            # Competitor overlap
            insights.competitor_overlap = await self._analyze_competitor_overlap(creator_profile)
            
            # Collaboration opportunities
            insights.collaboration_opportunities = await self._identify_collaboration_opportunities(creator_profile)
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating audience insights: {e}")
            return AudienceInsights(
                creator_id=creator_profile.get('creator_id', 'unknown'),
                audience_size=0,
                engagement_rate=0.0,
                growth_rate=0.0,
                audience_quality_score=0.0
            )
    
    async def _analyze_brand_affinity(self, creator_profile: Dict[str, Any]) -> Dict[str, float]:
        """Analyze audience brand affinity"""
        brand_data = creator_profile.get('audience_analytics', {}).get('brand_affinity', {})
        return {k: float(v) for k, v in brand_data.items()}
    
    async def _analyze_purchase_intent(self, creator_profile: Dict[str, Any]) -> Dict[str, float]:
        """Analyze audience purchase intent"""
        purchase_data = creator_profile.get('audience_analytics', {}).get('purchase_intent', {})
        return {k: float(v) for k, v in purchase_data.items()}
    
    async def _analyze_content_preferences(self, creator_profile: Dict[str, Any]) -> Dict[str, float]:
        """Analyze audience content preferences"""
        content_data = creator_profile.get('audience_analytics', {}).get('content_preferences', {})
        return {k: float(v) for k, v in content_data.items()}
    
    async def _analyze_optimal_posting_times(self, creator_profile: Dict[str, Any]) -> List[str]:
        """Analyze optimal posting times for audience"""
        timing_data = creator_profile.get('audience_analytics', {}).get('optimal_times', [])
        return timing_data[:5] if timing_data else ["12:00", "18:00", "20:00"]
    
    async def _analyze_trending_topics(self, creator_profile: Dict[str, Any]) -> List[str]:
        """Analyze trending topics among audience"""
        trending_data = creator_profile.get('audience_analytics', {}).get('trending_topics', [])
        return trending_data[:10] if trending_data else []
    
    async def _analyze_competitor_overlap(self, creator_profile: Dict[str, Any]) -> Dict[str, float]:
        """Analyze overlap with competitor audiences"""
        competitor_data = creator_profile.get('audience_analytics', {}).get('competitor_overlap', {})
        return {k: float(v) for k, v in competitor_data.items()}
    
    async def _identify_collaboration_opportunities(self, creator_profile: Dict[str, Any]) -> List[str]:
        """Identify collaboration opportunities based on audience analysis"""
        opportunities = []
        
        # Get demographic profile
        demographic_profile = await self.analyze_audience_profile(creator_profile)
        
        # Analyze primary segments
        primary_segment = demographic_profile.get_primary_segment()
        
        if primary_segment == AudienceSegment.TEENS_13_17:
            opportunities.extend([
                "gaming_collaborations",
                "education_content",
                "entertainment_partnerships"
            ])
        elif primary_segment == AudienceSegment.YOUNG_ADULTS_18_24:
            opportunities.extend([
                "lifestyle_brands",
                "technology_reviews",
                "career_content"
            ])
        elif primary_segment == AudienceSegment.ADULTS_25_34:
            opportunities.extend([
                "business_partnerships",
                "family_content",
                "financial_advice"
            ])
        
        # Analyze interests
        top_interests = sorted(
            demographic_profile.interest_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        for interest, _ in top_interests:
            if interest == InterestCategory.TECHNOLOGY:
                opportunities.append("tech_brand_partnerships")
            elif interest == InterestCategory.FITNESS:
                opportunities.append("health_wellness_collabs")
            elif interest == InterestCategory.FASHION:
                opportunities.append("fashion_brand_deals")
        
        return list(set(opportunities))  # Remove duplicates
    
    async def find_complementary_audiences(
        self,
        creator_profile: Dict[str, Any],
        candidate_creators: List[Dict[str, Any]],
        max_overlap: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Find creators with complementary (non-overlapping) audiences"""
        complementary_creators = []
        
        for candidate in candidate_creators:
            try:
                overlap = await self.calculate_audience_overlap(creator_profile, candidate)
                
                if overlap.overlap_percentage <= max_overlap:
                    collaboration_score = await self._calculate_collaboration_score(overlap)
                    
                    complementary_creators.append({
                        'creator': candidate,
                        'overlap_analysis': overlap,
                        'collaboration_score': collaboration_score,
                        'synergy_potential': self._assess_synergy_potential(overlap)
                    })
                    
            except Exception as e:
                logger.warning(f"⚠️ Error analyzing candidate {candidate.get('creator_id')}: {e}")
        
        # Sort by collaboration score
        complementary_creators.sort(key=lambda x: x['collaboration_score'], reverse=True)
        
        return complementary_creators
    
    async def _calculate_collaboration_score(self, overlap: AudienceOverlap) -> float:
        """Calculate collaboration potential score"""
        factors = [
            overlap.overlap_quality * 0.3,
            overlap.interest_alignment * 0.25,
            overlap.demographic_similarity * 0.2,
            overlap.geographic_overlap * 0.15,
            overlap.temporal_overlap * 0.1
        ]
        
        return sum(factors)
    
    def _assess_synergy_potential(self, overlap: AudienceOverlap) -> str:
        """Assess synergy potential based on overlap analysis"""
        collaboration_type = overlap.get_collaboration_potential()
        
        synergy_map = {
            "high_cannibalization_risk": "low_synergy",
            "moderate_overlap_good_synergy": "medium_synergy",
            "complementary_audiences": "high_synergy",
            "distinct_audiences_cross_promotion": "maximum_synergy"
        }
        
        return synergy_map.get(collaboration_type, "unknown_synergy")
    
    async def batch_analyze_overlaps(
        self,
        creator_profile: Dict[str, Any],
        candidate_creators: List[Dict[str, Any]]
    ) -> List[AudienceOverlap]:
        """Batch analyze audience overlaps for multiple candidates"""
        overlaps = []
        
        for candidate in candidate_creators:
            try:
                overlap = await self.calculate_audience_overlap(creator_profile, candidate)
                overlaps.append(overlap)
                
            except Exception as e:
                logger.warning(f"⚠️ Error analyzing overlap with {candidate.get('creator_id')}: {e}")
        
        return overlaps
    
    async def clear_cache(self):
        """Clear audience analysis cache"""
        self.audience_cache.clear()
        self.overlap_cache.clear()
        logger.info("🗑️ Audience analysis cache cleared")
    
    async def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            'audience_profiles_cached': len(self.audience_cache),
            'overlaps_cached': len(self.overlap_cache)
        }