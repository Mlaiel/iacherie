"""
Geographic Targeting Engine for Ainflue Distribution Platform

This module provides advanced geographic targeting and cultural adaptation
for optimized content distribution across global markets.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import pytz
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pycountry

logger = logging.getLogger(__name__)


class RegionType(Enum):
    """Types of geographic regions"""
    COUNTRY = "country"
    STATE_PROVINCE = "state_province"
    CITY = "city"
    METRO_AREA = "metro_area"
    CONTINENT = "continent"
    TIME_ZONE = "time_zone"
    LANGUAGE_REGION = "language_region"


class CulturalDimension(Enum):
    """Cultural dimensions for content adaptation"""
    POWER_DISTANCE = "power_distance"
    INDIVIDUALISM = "individualism"
    MASCULINITY = "masculinity"
    UNCERTAINTY_AVOIDANCE = "uncertainty_avoidance"
    LONG_TERM_ORIENTATION = "long_term_orientation"
    INDULGENCE = "indulgence"


@dataclass
class GeographicTarget:
    """Geographic targeting configuration"""
    target_id: str
    region_type: RegionType
    region_code: str
    region_name: str
    coordinates: Tuple[float, float]  # (latitude, longitude)
    timezone: str
    primary_language: str
    currency: str
    population: int
    internet_penetration: float
    social_media_usage: Dict[str, float]
    cultural_profile: Dict[CulturalDimension, float]
    content_preferences: Dict[str, float]
    optimal_posting_times: List[int]  # Hours in local time
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CulturalAdaptation:
    """Cultural adaptation recommendations"""
    target_region: str
    adaptations: List[str]
    content_modifications: Dict[str, str]
    visual_preferences: Dict[str, Any]
    messaging_style: str
    color_preferences: List[str]
    taboo_topics: List[str]
    celebration_dates: List[str]
    confidence_score: float


@dataclass
class GeoOptimizationResult:
    """Geographic optimization result"""
    content_id: str
    original_target: str
    optimized_targets: List[GeographicTarget]
    cultural_adaptations: Dict[str, CulturalAdaptation]
    expected_performance: Dict[str, float]
    timing_recommendations: Dict[str, List[datetime]]
    budget_allocation: Dict[str, float]
    success_probability: float


class AdvancedGeoTargetingEngine:
    """
    AI-powered geographic targeting and cultural adaptation engine
    
    Features:
    - Multi-dimensional geographic targeting
    - Cultural intelligence and content adaptation
    - Timezone-aware content scheduling
    - Regional performance prediction
    - Cross-cultural content optimization
    - Local trend integration
    - Language and currency localization
    """

    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.geographic_database = {}
        self.cultural_profiles = {}
        self.regional_performance = {}
        self.timezone_cache = {}
        
        # Initialize geographic data
        self._initialize_geographic_database()
        self._initialize_cultural_profiles()
        
        # Geocoding service
        self.geocoder = Nominatim(user_agent="ainflue_geo_targeting")

    def _initialize_geographic_database(self) -> None:
        """Initialize comprehensive geographic database"""
        
        # Major markets with detailed profiles
        major_markets = {
            'US': {
                'region_name': 'United States',
                'coordinates': (39.8283, -98.5795),
                'timezone': 'America/New_York',
                'primary_language': 'en',
                'currency': 'USD',
                'population': 331000000,
                'internet_penetration': 0.89,
                'social_media_usage': {
                    'facebook': 0.69,
                    'instagram': 0.35,
                    'tiktok': 0.21,
                    'twitter': 0.23,
                    'youtube': 0.73,
                    'linkedin': 0.28
                },
                'content_preferences': {
                    'video': 0.8,
                    'image': 0.7,
                    'text': 0.5,
                    'live_stream': 0.6,
                    'stories': 0.7
                },
                'optimal_posting_times': [9, 12, 15, 18, 20]
            },
            'GB': {
                'region_name': 'United Kingdom',
                'coordinates': (55.3781, -3.4360),
                'timezone': 'Europe/London',
                'primary_language': 'en',
                'currency': 'GBP',
                'population': 67000000,
                'internet_penetration': 0.95,
                'social_media_usage': {
                    'facebook': 0.66,
                    'instagram': 0.42,
                    'tiktok': 0.27,
                    'twitter': 0.31,
                    'youtube': 0.82,
                    'linkedin': 0.33
                },
                'content_preferences': {
                    'video': 0.75,
                    'image': 0.8,
                    'text': 0.65,
                    'live_stream': 0.55,
                    'stories': 0.6
                },
                'optimal_posting_times': [8, 12, 17, 19]
            },
            'DE': {
                'region_name': 'Germany',
                'coordinates': (51.1657, 10.4515),
                'timezone': 'Europe/Berlin',
                'primary_language': 'de',
                'currency': 'EUR',
                'population': 83000000,
                'internet_penetration': 0.92,
                'social_media_usage': {
                    'facebook': 0.52,
                    'instagram': 0.38,
                    'tiktok': 0.19,
                    'twitter': 0.16,
                    'youtube': 0.77,
                    'linkedin': 0.19
                },
                'content_preferences': {
                    'video': 0.72,
                    'image': 0.68,
                    'text': 0.58,
                    'live_stream': 0.45,
                    'stories': 0.55
                },
                'optimal_posting_times': [8, 11, 14, 18, 20]
            },
            'FR': {
                'region_name': 'France',
                'coordinates': (46.2276, 2.2137),
                'timezone': 'Europe/Paris',
                'primary_language': 'fr',
                'currency': 'EUR',
                'population': 68000000,
                'internet_penetration': 0.85,
                'social_media_usage': {
                    'facebook': 0.58,
                    'instagram': 0.35,
                    'tiktok': 0.22,
                    'twitter': 0.18,
                    'youtube': 0.79,
                    'linkedin': 0.22
                },
                'content_preferences': {
                    'video': 0.74,
                    'image': 0.73,
                    'text': 0.62,
                    'live_stream': 0.48,
                    'stories': 0.58
                },
                'optimal_posting_times': [9, 12, 15, 19]
            },
            'JP': {
                'region_name': 'Japan',
                'coordinates': (36.2048, 138.2529),
                'timezone': 'Asia/Tokyo',
                'primary_language': 'ja',
                'currency': 'JPY',
                'population': 125000000,
                'internet_penetration': 0.93,
                'social_media_usage': {
                    'facebook': 0.28,
                    'instagram': 0.33,
                    'tiktok': 0.17,
                    'twitter': 0.51,
                    'youtube': 0.89,
                    'linkedin': 0.03
                },
                'content_preferences': {
                    'video': 0.85,
                    'image': 0.78,
                    'text': 0.45,
                    'live_stream': 0.72,
                    'stories': 0.65
                },
                'optimal_posting_times': [7, 12, 15, 20, 22]
            },
            'BR': {
                'region_name': 'Brazil',
                'coordinates': (-14.2350, -51.9253),
                'timezone': 'America/Sao_Paulo',
                'primary_language': 'pt',
                'currency': 'BRL',
                'population': 215000000,
                'internet_penetration': 0.74,
                'social_media_usage': {
                    'facebook': 0.69,
                    'instagram': 0.57,
                    'tiktok': 0.32,
                    'twitter': 0.16,
                    'youtube': 0.89,
                    'linkedin': 0.08
                },
                'content_preferences': {
                    'video': 0.89,
                    'image': 0.82,
                    'text': 0.52,
                    'live_stream': 0.78,
                    'stories': 0.85
                },
                'optimal_posting_times': [9, 14, 18, 20, 22]
            }
        }
        
        # Convert to GeographicTarget objects
        for country_code, data in major_markets.items():
            target = GeographicTarget(
                target_id=f"country_{country_code}",
                region_type=RegionType.COUNTRY,
                region_code=country_code,
                region_name=data['region_name'],
                coordinates=data['coordinates'],
                timezone=data['timezone'],
                primary_language=data['primary_language'],
                currency=data['currency'],
                population=data['population'],
                internet_penetration=data['internet_penetration'],
                social_media_usage=data['social_media_usage'],
                cultural_profile=self._get_cultural_profile(country_code),
                content_preferences=data['content_preferences'],
                optimal_posting_times=data['optimal_posting_times']
            )
            
            self.geographic_database[country_code] = target

    def _initialize_cultural_profiles(self) -> None:
        """Initialize cultural profiles based on Hofstede's dimensions"""
        
        # Cultural dimension scores (0-1 scale)
        cultural_data = {
            'US': {
                CulturalDimension.POWER_DISTANCE: 0.4,
                CulturalDimension.INDIVIDUALISM: 0.91,
                CulturalDimension.MASCULINITY: 0.62,
                CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.46,
                CulturalDimension.LONG_TERM_ORIENTATION: 0.26,
                CulturalDimension.INDULGENCE: 0.68
            },
            'GB': {
                CulturalDimension.POWER_DISTANCE: 0.35,
                CulturalDimension.INDIVIDUALISM: 0.89,
                CulturalDimension.MASCULINITY: 0.66,
                CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.35,
                CulturalDimension.LONG_TERM_ORIENTATION: 0.51,
                CulturalDimension.INDULGENCE: 0.69
            },
            'DE': {
                CulturalDimension.POWER_DISTANCE: 0.35,
                CulturalDimension.INDIVIDUALISM: 0.67,
                CulturalDimension.MASCULINITY: 0.66,
                CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.65,
                CulturalDimension.LONG_TERM_ORIENTATION: 0.83,
                CulturalDimension.INDULGENCE: 0.4
            },
            'FR': {
                CulturalDimension.POWER_DISTANCE: 0.68,
                CulturalDimension.INDIVIDUALISM: 0.71,
                CulturalDimension.MASCULINITY: 0.43,
                CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.86,
                CulturalDimension.LONG_TERM_ORIENTATION: 0.63,
                CulturalDimension.INDULGENCE: 0.48
            },
            'JP': {
                CulturalDimension.POWER_DISTANCE: 0.54,
                CulturalDimension.INDIVIDUALISM: 0.46,
                CulturalDimension.MASCULINITY: 0.95,
                CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.92,
                CulturalDimension.LONG_TERM_ORIENTATION: 0.88,
                CulturalDimension.INDULGENCE: 0.42
            },
            'BR': {
                CulturalDimension.POWER_DISTANCE: 0.69,
                CulturalDimension.INDIVIDUALISM: 0.38,
                CulturalDimension.MASCULINITY: 0.49,
                CulturalDimension.UNCERTAINTY_AVOIDANCE: 0.76,
                CulturalDimension.LONG_TERM_ORIENTATION: 0.44,
                CulturalDimension.INDULGENCE: 0.59
            }
        }
        
        self.cultural_profiles = cultural_data

    def _get_cultural_profile(self, country_code: str) -> Dict[CulturalDimension, float]:
        """Get cultural profile for country"""
        return self.cultural_profiles.get(country_code, {})

    async def optimize_geographic_targeting(
        self,
        content_metadata: Dict[str, Any],
        target_regions: List[str],
        budget_constraints: Dict[str, float],
        campaign_objectives: Dict[str, float]
    ) -> GeoOptimizationResult:
        """
        Optimize geographic targeting for content distribution
        
        Args:
            content_metadata: Content characteristics and metadata
            target_regions: List of target region codes
            budget_constraints: Budget allocation constraints
            campaign_objectives: Campaign performance objectives
            
        Returns:
            Comprehensive geographic optimization result
        """
        try:
            content_id = content_metadata.get('content_id', 'unknown')
            
            # Analyze content for regional suitability
            regional_suitability = await self._analyze_regional_suitability(
                content_metadata, target_regions
            )
            
            # Optimize target selection
            optimized_targets = await self._optimize_target_selection(
                regional_suitability, budget_constraints, campaign_objectives
            )
            
            # Generate cultural adaptations
            cultural_adaptations = {}
            for target in optimized_targets:
                adaptation = await self._generate_cultural_adaptation(
                    content_metadata, target
                )
                cultural_adaptations[target.region_code] = adaptation
            
            # Predict performance
            expected_performance = await self._predict_regional_performance(
                content_metadata, optimized_targets
            )
            
            # Generate timing recommendations
            timing_recommendations = await self._generate_timing_recommendations(
                optimized_targets, content_metadata
            )
            
            # Optimize budget allocation
            budget_allocation = await self._optimize_budget_allocation(
                optimized_targets, expected_performance, budget_constraints
            )
            
            # Calculate success probability
            success_probability = await self._calculate_success_probability(
                optimized_targets, expected_performance, cultural_adaptations
            )
            
            return GeoOptimizationResult(
                content_id=content_id,
                original_target="global",
                optimized_targets=optimized_targets,
                cultural_adaptations=cultural_adaptations,
                expected_performance=expected_performance,
                timing_recommendations=timing_recommendations,
                budget_allocation=budget_allocation,
                success_probability=success_probability
            )
            
        except Exception as e:
            logger.error(f"Error optimizing geographic targeting: {e}")
            raise

    async def _analyze_regional_suitability(
        self,
        content_metadata: Dict[str, Any],
        target_regions: List[str]
    ) -> Dict[str, float]:
        """Analyze content suitability for each target region"""
        
        suitability_scores = {}
        
        content_type = content_metadata.get('type', 'unknown')
        content_language = content_metadata.get('language', 'en')
        content_topics = content_metadata.get('topics', [])
        content_style = content_metadata.get('style', 'neutral')
        
        for region_code in target_regions:
            if region_code not in self.geographic_database:
                continue
            
            target = self.geographic_database[region_code]
            score = 0.0
            
            # Language compatibility
            if content_language == target.primary_language:
                score += 0.3
            elif content_language == 'en':  # English as lingua franca
                score += 0.2
            else:
                score += 0.1
            
            # Content type preferences
            content_pref = target.content_preferences.get(content_type, 0.5)
            score += content_pref * 0.3
            
            # Cultural alignment
            cultural_alignment = await self._calculate_cultural_alignment(
                content_metadata, target.cultural_profile
            )
            score += cultural_alignment * 0.2
            
            # Platform availability
            platform = content_metadata.get('platform', 'unknown')
            if platform in target.social_media_usage:
                platform_usage = target.social_media_usage[platform]
                score += platform_usage * 0.2
            
            suitability_scores[region_code] = min(1.0, score)
        
        return suitability_scores

    async def _calculate_cultural_alignment(
        self,
        content_metadata: Dict[str, Any],
        cultural_profile: Dict[CulturalDimension, float]
    ) -> float:
        """Calculate cultural alignment score for content"""
        
        if not cultural_profile:
            return 0.5  # Neutral alignment
        
        alignment_score = 0.5  # Base score
        
        content_style = content_metadata.get('style', 'neutral')
        content_tone = content_metadata.get('tone', 'neutral')
        content_formality = content_metadata.get('formality', 'medium')
        
        # Power distance alignment
        power_distance = cultural_profile.get(CulturalDimension.POWER_DISTANCE, 0.5)
        if content_formality == 'formal' and power_distance > 0.6:
            alignment_score += 0.1
        elif content_formality == 'casual' and power_distance < 0.4:
            alignment_score += 0.1
        
        # Individualism alignment
        individualism = cultural_profile.get(CulturalDimension.INDIVIDUALISM, 0.5)
        if 'personal' in content_style and individualism > 0.6:
            alignment_score += 0.1
        elif 'community' in content_style and individualism < 0.4:
            alignment_score += 0.1
        
        # Uncertainty avoidance alignment
        uncertainty_avoidance = cultural_profile.get(CulturalDimension.UNCERTAINTY_AVOIDANCE, 0.5)
        if content_tone == 'authoritative' and uncertainty_avoidance > 0.6:
            alignment_score += 0.1
        elif content_tone == 'experimental' and uncertainty_avoidance < 0.4:
            alignment_score += 0.1
        
        return min(1.0, alignment_score)

    async def _optimize_target_selection(
        self,
        regional_suitability: Dict[str, float],
        budget_constraints: Dict[str, float],
        campaign_objectives: Dict[str, float]
    ) -> List[GeographicTarget]:
        """Select optimal target regions based on suitability and constraints"""
        
        # Sort regions by suitability score
        sorted_regions = sorted(
            regional_suitability.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        selected_targets = []
        total_budget = budget_constraints.get('total_budget', 1000)
        max_regions = budget_constraints.get('max_regions', 5)
        min_budget_per_region = budget_constraints.get('min_budget_per_region', 100)
        
        available_budget = total_budget
        
        for region_code, suitability in sorted_regions[:max_regions]:
            if region_code in self.geographic_database:
                target = self.geographic_database[region_code]
                
                # Estimate required budget for this region
                required_budget = self._estimate_required_budget(target, campaign_objectives)
                
                if (required_budget <= available_budget and 
                    required_budget >= min_budget_per_region):
                    
                    selected_targets.append(target)
                    available_budget -= required_budget
        
        return selected_targets

    def _estimate_required_budget(
        self,
        target: GeographicTarget,
        campaign_objectives: Dict[str, float]
    ) -> float:
        """Estimate required budget for target region"""
        
        # Base budget calculation factors
        population_factor = min(1.0, target.population / 100000000)  # Normalize to 100M
        internet_penetration_factor = target.internet_penetration
        
        # Platform usage factor
        avg_platform_usage = sum(target.social_media_usage.values()) / len(target.social_media_usage)
        
        # Cost multiplier based on market maturity
        cost_multipliers = {
            'US': 1.5,
            'GB': 1.3,
            'DE': 1.2,
            'FR': 1.2,
            'JP': 1.4,
            'BR': 0.8
        }
        
        cost_multiplier = cost_multipliers.get(target.region_code, 1.0)
        
        # Base budget calculation
        base_budget = (
            population_factor * 100 +
            internet_penetration_factor * 50 +
            avg_platform_usage * 50
        ) * cost_multiplier
        
        # Adjust for campaign objectives
        reach_target = campaign_objectives.get('reach', 10000)
        budget_per_reach = base_budget / 10000  # Base budget for 10K reach
        
        estimated_budget = reach_target * budget_per_reach
        
        return max(50, estimated_budget)  # Minimum budget threshold

    async def _generate_cultural_adaptation(
        self,
        content_metadata: Dict[str, Any],
        target: GeographicTarget
    ) -> CulturalAdaptation:
        """Generate cultural adaptation recommendations for target region"""
        
        adaptations = []
        content_modifications = {}
        visual_preferences = {}
        messaging_style = "neutral"
        color_preferences = []
        taboo_topics = []
        celebration_dates = []
        
        cultural_profile = target.cultural_profile
        
        # Power distance adaptations
        power_distance = cultural_profile.get(CulturalDimension.POWER_DISTANCE, 0.5)
        if power_distance > 0.6:
            adaptations.append("Use more formal language and respect hierarchical structures")
            messaging_style = "formal"
            content_modifications['tone'] = 'respectful'
        elif power_distance < 0.4:
            adaptations.append("Use casual, approachable language")
            messaging_style = "casual"
            content_modifications['tone'] = 'friendly'
        
        # Individualism adaptations
        individualism = cultural_profile.get(CulturalDimension.INDIVIDUALISM, 0.5)
        if individualism > 0.6:
            adaptations.append("Focus on personal achievement and individual benefits")
            content_modifications['focus'] = 'individual'
        else:
            adaptations.append("Emphasize community, family, and group benefits")
            content_modifications['focus'] = 'community'
        
        # Uncertainty avoidance adaptations
        uncertainty_avoidance = cultural_profile.get(CulturalDimension.UNCERTAINTY_AVOIDANCE, 0.5)
        if uncertainty_avoidance > 0.6:
            adaptations.append("Provide detailed information and clear guarantees")
            content_modifications['detail_level'] = 'high'
        else:
            adaptations.append("Allow for ambiguity and experimental approaches")
            content_modifications['detail_level'] = 'moderate'
        
        # Long-term orientation adaptations
        long_term = cultural_profile.get(CulturalDimension.LONG_TERM_ORIENTATION, 0.5)
        if long_term > 0.6:
            adaptations.append("Emphasize long-term benefits and persistence")
            content_modifications['time_focus'] = 'long_term'
        else:
            adaptations.append("Focus on immediate results and quick wins")
            content_modifications['time_focus'] = 'short_term'
        
        # Region-specific visual and color preferences
        region_specific_data = self._get_region_specific_preferences(target.region_code)
        visual_preferences = region_specific_data.get('visual_preferences', {})
        color_preferences = region_specific_data.get('color_preferences', [])
        taboo_topics = region_specific_data.get('taboo_topics', [])
        celebration_dates = region_specific_data.get('celebration_dates', [])
        
        # Calculate confidence score
        confidence_score = min(1.0, len(cultural_profile) / len(CulturalDimension))
        
        return CulturalAdaptation(
            target_region=target.region_code,
            adaptations=adaptations,
            content_modifications=content_modifications,
            visual_preferences=visual_preferences,
            messaging_style=messaging_style,
            color_preferences=color_preferences,
            taboo_topics=taboo_topics,
            celebration_dates=celebration_dates,
            confidence_score=confidence_score
        )

    def _get_region_specific_preferences(self, region_code: str) -> Dict[str, Any]:
        """Get region-specific visual and cultural preferences"""
        
        preferences = {
            'US': {
                'visual_preferences': {
                    'bright_colors': True,
                    'bold_typography': True,
                    'casual_imagery': True
                },
                'color_preferences': ['red', 'blue', 'white', 'yellow'],
                'taboo_topics': ['politics', 'religion', 'controversial_history'],
                'celebration_dates': ['2024-07-04', '2024-11-28', '2024-12-25']
            },
            'GB': {
                'visual_preferences': {
                    'understated_elegance': True,
                    'classic_typography': True,
                    'heritage_imagery': True
                },
                'color_preferences': ['navy', 'green', 'gold', 'burgundy'],
                'taboo_topics': ['brexit_criticism', 'monarchy_criticism'],
                'celebration_dates': ['2024-04-23', '2024-12-25', '2024-12-26']
            },
            'DE': {
                'visual_preferences': {
                    'clean_design': True,
                    'minimalist': True,
                    'high_quality_imagery': True
                },
                'color_preferences': ['black', 'red', 'gold', 'blue'],
                'taboo_topics': ['nazi_references', 'wwii_glorification'],
                'celebration_dates': ['2024-10-03', '2024-12-25', '2024-12-26']
            },
            'FR': {
                'visual_preferences': {
                    'sophisticated_design': True,
                    'artistic_imagery': True,
                    'elegant_typography': True
                },
                'color_preferences': ['blue', 'white', 'red', 'gold'],
                'taboo_topics': ['cultural_superiority', 'language_purity'],
                'celebration_dates': ['2024-07-14', '2024-12-25', '2024-05-01']
            },
            'JP': {
                'visual_preferences': {
                    'minimalist_design': True,
                    'harmony_balance': True,
                    'nature_imagery': True
                },
                'color_preferences': ['white', 'red', 'black', 'gold'],
                'taboo_topics': ['war_crimes', 'nuclear_weapons', 'controversial_history'],
                'celebration_dates': ['2024-01-01', '2024-05-03', '2024-12-23']
            },
            'BR': {
                'visual_preferences': {
                    'vibrant_colors': True,
                    'energetic_imagery': True,
                    'festive_elements': True
                },
                'color_preferences': ['green', 'yellow', 'blue', 'orange'],
                'taboo_topics': ['political_corruption', 'environmental_destruction'],
                'celebration_dates': ['2024-02-13', '2024-09-07', '2024-12-25']
            }
        }
        
        return preferences.get(region_code, {})

    async def _predict_regional_performance(
        self,
        content_metadata: Dict[str, Any],
        targets: List[GeographicTarget]
    ) -> Dict[str, float]:
        """Predict performance metrics for each target region"""
        
        performance_predictions = {}
        
        for target in targets:
            # Base performance factors
            base_performance = {
                'reach': target.population * target.internet_penetration * 0.001,  # 0.1% reach
                'engagement_rate': 0.05,  # 5% base engagement
                'conversion_rate': 0.02,  # 2% base conversion
                'cpm': 5.0  # $5 base CPM
            }
            
            # Content type multipliers
            content_type = content_metadata.get('type', 'image')
            content_multipliers = target.content_preferences.get(content_type, 0.5)
            
            # Platform usage multipliers
            platform = content_metadata.get('platform', 'facebook')
            platform_multiplier = target.social_media_usage.get(platform, 0.5)
            
            # Cultural alignment multiplier
            cultural_alignment = await self._calculate_cultural_alignment(
                content_metadata, target.cultural_profile
            )
            
            # Apply multipliers
            for metric, base_value in base_performance.items():
                if metric == 'cpm':
                    # CPM decreases with better alignment
                    multiplier = 1 / (content_multipliers * platform_multiplier * cultural_alignment + 0.1)
                else:
                    # Other metrics increase with better alignment
                    multiplier = content_multipliers * platform_multiplier * cultural_alignment
                
                performance_predictions[f"{target.region_code}_{metric}"] = base_value * multiplier
        
        return performance_predictions

    async def _generate_timing_recommendations(
        self,
        targets: List[GeographicTarget],
        content_metadata: Dict[str, Any]
    ) -> Dict[str, List[datetime]]:
        """Generate optimal timing recommendations for each target"""
        
        timing_recommendations = {}
        base_time = datetime.utcnow()
        
        for target in targets:
            # Get target timezone
            target_tz = pytz.timezone(target.timezone)
            
            # Generate recommendations for next 7 days
            recommendations = []
            
            for day_offset in range(7):
                target_date = base_time + timedelta(days=day_offset)
                
                # Convert to target timezone
                target_date_local = target_date.replace(tzinfo=pytz.UTC).astimezone(target_tz)
                
                # Get optimal hours for this target
                for hour in target.optimal_posting_times:
                    optimal_time = target_date_local.replace(
                        hour=hour,
                        minute=0,
                        second=0,
                        microsecond=0
                    )
                    
                    # Convert back to UTC
                    optimal_time_utc = optimal_time.astimezone(pytz.UTC)
                    recommendations.append(optimal_time_utc)
            
            timing_recommendations[target.region_code] = recommendations[:14]  # Top 14 times
        
        return timing_recommendations

    async def _optimize_budget_allocation(
        self,
        targets: List[GeographicTarget],
        expected_performance: Dict[str, float],
        budget_constraints: Dict[str, float]
    ) -> Dict[str, float]:
        """Optimize budget allocation across target regions"""
        
        total_budget = budget_constraints.get('total_budget', 1000)
        
        # Calculate efficiency scores for each target
        efficiency_scores = {}
        
        for target in targets:
            reach_key = f"{target.region_code}_reach"
            cpm_key = f"{target.region_code}_cpm"
            
            expected_reach = expected_performance.get(reach_key, 1000)
            expected_cpm = expected_performance.get(cpm_key, 5.0)
            
            # Efficiency = reach per dollar
            efficiency = expected_reach / expected_cpm
            efficiency_scores[target.region_code] = efficiency
        
        # Allocate budget proportionally to efficiency
        total_efficiency = sum(efficiency_scores.values())
        budget_allocation = {}
        
        for target in targets:
            if total_efficiency > 0:
                allocation_ratio = efficiency_scores[target.region_code] / total_efficiency
                allocated_budget = total_budget * allocation_ratio
            else:
                allocated_budget = total_budget / len(targets)
            
            budget_allocation[target.region_code] = allocated_budget
        
        return budget_allocation

    async def _calculate_success_probability(
        self,
        targets: List[GeographicTarget],
        expected_performance: Dict[str, float],
        cultural_adaptations: Dict[str, CulturalAdaptation]
    ) -> float:
        """Calculate overall success probability for geographic optimization"""
        
        success_factors = []
        
        for target in targets:
            # Performance factor
            reach_key = f"{target.region_code}_reach"
            engagement_key = f"{target.region_code}_engagement_rate"
            
            expected_reach = expected_performance.get(reach_key, 0)
            expected_engagement = expected_performance.get(engagement_key, 0)
            
            performance_score = min(1.0, (expected_reach / 10000) * expected_engagement * 10)
            
            # Cultural adaptation factor
            adaptation = cultural_adaptations.get(target.region_code)
            adaptation_score = adaptation.confidence_score if adaptation else 0.5
            
            # Market penetration factor
            penetration_score = target.internet_penetration
            
            # Combined success factor for this target
            target_success = (performance_score + adaptation_score + penetration_score) / 3
            success_factors.append(target_success)
        
        # Overall success probability
        if success_factors:
            return sum(success_factors) / len(success_factors)
        else:
            return 0.0

    async def get_timezone_optimal_times(
        self,
        timezone_name: str,
        content_type: str = 'general'
    ) -> List[int]:
        """Get optimal posting times for specific timezone"""
        
        try:
            # Cache check
            cache_key = f"{timezone_name}_{content_type}"
            if cache_key in self.timezone_cache:
                return self.timezone_cache[cache_key]
            
            # Find regions in this timezone
            regions_in_tz = [
                target for target in self.geographic_database.values()
                if target.timezone == timezone_name
            ]
            
            if not regions_in_tz:
                # Default optimal times
                optimal_times = [9, 12, 15, 18, 20]
            else:
                # Aggregate optimal times from regions in timezone
                all_times = []
                for region in regions_in_tz:
                    all_times.extend(region.optimal_posting_times)
                
                # Find most common times
                time_counts = {}
                for time_hour in all_times:
                    time_counts[time_hour] = time_counts.get(time_hour, 0) + 1
                
                # Sort by frequency and take top 5
                optimal_times = sorted(time_counts.keys(), key=lambda x: time_counts[x], reverse=True)[:5]
            
            # Cache result
            self.timezone_cache[cache_key] = optimal_times
            
            return optimal_times
            
        except Exception as e:
            logger.error(f"Error getting timezone optimal times: {e}")
            return [9, 12, 15, 18, 20]  # Safe defaults

    async def get_cultural_recommendations(
        self,
        target_region: str,
        content_topics: List[str]
    ) -> Dict[str, Any]:
        """Get cultural recommendations for specific region and topics"""
        
        try:
            if target_region not in self.geographic_database:
                return {'error': f'Region {target_region} not found'}
            
            target = self.geographic_database[target_region]
            
            # Mock content metadata for cultural analysis
            mock_content = {
                'topics': content_topics,
                'style': 'neutral',
                'tone': 'neutral',
                'formality': 'medium'
            }
            
            cultural_adaptation = await self._generate_cultural_adaptation(mock_content, target)
            
            region_preferences = self._get_region_specific_preferences(target_region)
            
            return {
                'cultural_dimensions': {dim.value: score for dim, score in target.cultural_profile.items()},
                'adaptations': cultural_adaptation.adaptations,
                'content_modifications': cultural_adaptation.content_modifications,
                'visual_preferences': region_preferences.get('visual_preferences', {}),
                'color_preferences': region_preferences.get('color_preferences', []),
                'taboo_topics': region_preferences.get('taboo_topics', []),
                'celebration_dates': region_preferences.get('celebration_dates', []),
                'messaging_style': cultural_adaptation.messaging_style,
                'confidence_score': cultural_adaptation.confidence_score
            }
            
        except Exception as e:
            logger.error(f"Error getting cultural recommendations: {e}")
            return {'error': str(e)}