"""Geographic Matcher Module - Location and Timezone Compatibility Analysis
========================================================================

Advanced geographic analysis system for creator collaboration optimization based on
location proximity, timezone compatibility, cultural factors, and regional market
considerations for optimal collaboration planning.

This module implements:
- Geographic proximity and distance analysis
- Timezone compatibility and optimal meeting windows
- Cultural and language compatibility assessment
- Regional market opportunity analysis
- Travel and logistics optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import math
import pytz
import numpy as np
import statistics

logger = logging.getLogger(__name__)


class ProximityLevel(Enum):
    """Geographic proximity levels"""
    SAME_CITY = "same_city"
    SAME_REGION = "same_region"
    SAME_COUNTRY = "same_country"
    SAME_CONTINENT = "same_continent"
    DIFFERENT_CONTINENT = "different_continent"


class TimezoneCompatibility(Enum):
    """Timezone compatibility levels"""
    EXCELLENT = "excellent"    # 0-2 hour difference
    GOOD = "good"             # 3-5 hour difference
    MODERATE = "moderate"     # 6-8 hour difference
    CHALLENGING = "challenging" # 9-11 hour difference
    DIFFICULT = "difficult"   # 12+ hour difference


class CulturalAlignment(Enum):
    """Cultural alignment levels"""
    IDENTICAL = "identical"
    SIMILAR = "similar"
    COMPATIBLE = "compatible"
    DIFFERENT = "different"
    CHALLENGING = "challenging"


@dataclass
class GeographicLocation:
    """Geographic location information"""
    creator_id: str
    latitude: float
    longitude: float
    city: str
    region: str
    country: str
    country_code: str
    continent: str
    timezone: str
    primary_language: str
    secondary_languages: List[str] = field(default_factory=list)
    cultural_context: Dict[str, Any] = field(default_factory=dict)
    market_tier: str = "tier_2"  # tier_1, tier_2, tier_3
    cost_of_living_index: float = 100.0  # Base 100
    internet_quality: float = 0.8  # 0-1 scale
    business_hours: Tuple[int, int] = (9, 17)  # 24-hour format
    work_preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimezoneAnalysis:
    """Timezone compatibility analysis"""
    creator_timezones: Dict[str, str]
    time_difference_hours: Dict[Tuple[str, str], float]
    optimal_meeting_windows: List[Dict[str, Any]]
    collaboration_difficulty_score: float
    recommended_schedule: Dict[str, Any]
    timezone_advantages: List[str]
    timezone_challenges: List[str]
    follow_the_sun_potential: bool


@dataclass
class LocationCompatibility:
    """Location compatibility analysis"""
    creators: List[str]
    proximity_level: ProximityLevel
    distance_km: float
    travel_time_hours: Optional[float]
    travel_cost_estimate: Optional[float]
    in_person_collaboration_feasible: bool
    shared_market_opportunities: List[str]
    regional_advantages: List[str]
    logistical_considerations: List[str]


@dataclass
class ProximityScore:
    """Proximity scoring between creators"""
    creator_pair: Tuple[str, str]
    geographic_score: float
    timezone_score: float
    cultural_score: float
    market_opportunity_score: float
    logistical_score: float
    overall_proximity_score: float
    collaboration_recommendation: str
    optimal_interaction_methods: List[str]


@dataclass
class GeographicProfile:
    """Comprehensive geographic profile for collaboration"""
    creator_locations: List[GeographicLocation]
    proximity_analysis: List[ProximityScore]
    timezone_analysis: TimezoneAnalysis
    cultural_compatibility: Dict[str, Any]
    market_synergies: List[Dict[str, Any]]
    logistical_recommendations: List[Dict[str, Any]]
    optimal_collaboration_structure: Dict[str, Any]
    geographic_advantages: List[str]
    geographic_challenges: List[str]
    confidence_score: float


class GeographicMatcher:
    """Advanced geographic and timezone compatibility analysis engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the geographic matcher"""
        self.config = config or {}
        self.timezone_cache = {}
        self.distance_cache = {}
        self.cultural_compatibility_matrix = self._init_cultural_matrix()
        self.market_data = self._init_market_data()
        
        logger.info("🌍 Geographic Matcher initialized")
    
    def _init_cultural_matrix(self) -> Dict[Tuple[str, str], float]:
        """Initialize cultural compatibility matrix"""
        # Simplified cultural compatibility scores (0-1)
        # In production, this would be based on comprehensive cultural research
        return {
            ("en", "en"): 1.0,  # Same language
            ("en", "es"): 0.7,  # English-Spanish
            ("en", "fr"): 0.7,  # English-French
            ("en", "de"): 0.8,  # English-German
            ("en", "it"): 0.7,  # English-Italian
            ("en", "pt"): 0.7,  # English-Portuguese
            ("es", "pt"): 0.8,  # Spanish-Portuguese
            ("fr", "es"): 0.7,  # French-Spanish
            ("de", "fr"): 0.7,  # German-French
            ("ar", "ar"): 1.0,  # Same language (Arabic)
            ("ar", "en"): 0.6,  # Arabic-English
            ("zh", "zh"): 1.0,  # Same language (Chinese)
            ("zh", "en"): 0.6,  # Chinese-English
            ("ja", "en"): 0.6,  # Japanese-English
            ("ko", "en"): 0.6,  # Korean-English
        }
    
    def _init_market_data(self) -> Dict[str, Dict[str, Any]]:
        """Initialize market data for different regions"""
        return {
            "north_america": {
                "social_media_penetration": 0.85,
                "digital_ad_spend": "high",
                "creator_economy_maturity": "mature",
                "avg_cpm": 5.0,
                "primary_platforms": ["youtube", "instagram", "tiktok", "twitter"]
            },
            "europe": {
                "social_media_penetration": 0.78,
                "digital_ad_spend": "high",
                "creator_economy_maturity": "mature",
                "avg_cpm": 4.5,
                "primary_platforms": ["youtube", "instagram", "tiktok"]
            },
            "asia_pacific": {
                "social_media_penetration": 0.70,
                "digital_ad_spend": "medium_high",
                "creator_economy_maturity": "growing",
                "avg_cpm": 3.0,
                "primary_platforms": ["youtube", "tiktok", "instagram"]
            },
            "middle_east": {
                "social_media_penetration": 0.65,
                "digital_ad_spend": "medium",
                "creator_economy_maturity": "emerging",
                "avg_cpm": 2.5,
                "primary_platforms": ["youtube", "instagram", "snapchat"]
            },
            "africa": {
                "social_media_penetration": 0.45,
                "digital_ad_spend": "low_medium",
                "creator_economy_maturity": "emerging",
                "avg_cpm": 1.5,
                "primary_platforms": ["youtube", "instagram", "tiktok"]
            },
            "latin_america": {
                "social_media_penetration": 0.68,
                "digital_ad_spend": "medium",
                "creator_economy_maturity": "growing",
                "avg_cpm": 2.0,
                "primary_platforms": ["youtube", "instagram", "tiktok"]
            }
        }
    
    async def analyze_geographic_compatibility(
        self,
        creator_locations: List[GeographicLocation]
    ) -> GeographicProfile:
        """Analyze comprehensive geographic compatibility"""
        try:
            logger.info(f"🌍 Analyzing geographic compatibility for {len(creator_locations)} creators")
            
            if len(creator_locations) < 2:
                raise ValueError("Need at least 2 locations for geographic analysis")
            
            # Calculate proximity scores between all pairs
            proximity_analysis = await self._calculate_proximity_scores(creator_locations)
            
            # Analyze timezone compatibility
            timezone_analysis = await self._analyze_timezone_compatibility(creator_locations)
            
            # Assess cultural compatibility
            cultural_compatibility = await self._assess_cultural_compatibility(creator_locations)
            
            # Identify market synergies
            market_synergies = await self._identify_market_synergies(creator_locations)
            
            # Generate logistical recommendations
            logistical_recommendations = await self._generate_logistical_recommendations(
                creator_locations, proximity_analysis
            )
            
            # Determine optimal collaboration structure
            optimal_structure = await self._determine_optimal_collaboration_structure(
                creator_locations, proximity_analysis, timezone_analysis
            )
            
            # Identify advantages and challenges
            advantages = await self._identify_geographic_advantages(
                creator_locations, market_synergies
            )
            challenges = await self._identify_geographic_challenges(
                creator_locations, proximity_analysis
            )
            
            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                creator_locations, proximity_analysis
            )
            
            profile = GeographicProfile(
                creator_locations=creator_locations,
                proximity_analysis=proximity_analysis,
                timezone_analysis=timezone_analysis,
                cultural_compatibility=cultural_compatibility,
                market_synergies=market_synergies,
                logistical_recommendations=logistical_recommendations,
                optimal_collaboration_structure=optimal_structure,
                geographic_advantages=advantages,
                geographic_challenges=challenges,
                confidence_score=confidence_score
            )
            
            logger.info(f"✅ Geographic compatibility analysis completed")
            return profile
            
        except Exception as e:
            logger.error(f"❌ Error in geographic compatibility analysis: {e}")
            raise
    
    async def _calculate_proximity_scores(
        self,
        locations: List[GeographicLocation]
    ) -> List[ProximityScore]:
        """Calculate proximity scores between all creator pairs"""
        proximity_scores = []
        
        for i, loc_a in enumerate(locations):
            for j, loc_b in enumerate(locations[i+1:], i+1):
                # Calculate geographic score
                distance_km = self._calculate_distance(
                    loc_a.latitude, loc_a.longitude,
                    loc_b.latitude, loc_b.longitude
                )
                geographic_score = self._distance_to_score(distance_km)
                
                # Calculate timezone score
                timezone_score = await self._calculate_timezone_score(
                    loc_a.timezone, loc_b.timezone
                )
                
                # Calculate cultural score
                cultural_score = self._calculate_cultural_score(
                    loc_a.primary_language, loc_b.primary_language,
                    loc_a.cultural_context, loc_b.cultural_context
                )
                
                # Calculate market opportunity score
                market_score = self._calculate_market_opportunity_score(loc_a, loc_b)
                
                # Calculate logistical score
                logistical_score = self._calculate_logistical_score(loc_a, loc_b, distance_km)
                
                # Calculate overall proximity score
                weights = {
                    'geographic': 0.25,
                    'timezone': 0.25,
                    'cultural': 0.20,
                    'market': 0.15,
                    'logistical': 0.15
                }
                
                overall_score = (
                    geographic_score * weights['geographic'] +
                    timezone_score * weights['timezone'] +
                    cultural_score * weights['cultural'] +
                    market_score * weights['market'] +
                    logistical_score * weights['logistical']
                )
                
                # Generate collaboration recommendation
                recommendation = self._generate_collaboration_recommendation(overall_score)
                
                # Determine optimal interaction methods
                interaction_methods = self._determine_interaction_methods(
                    distance_km, timezone_score, cultural_score
                )
                
                proximity_score = ProximityScore(
                    creator_pair=(loc_a.creator_id, loc_b.creator_id),
                    geographic_score=geographic_score,
                    timezone_score=timezone_score,
                    cultural_score=cultural_score,
                    market_opportunity_score=market_score,
                    logistical_score=logistical_score,
                    overall_proximity_score=overall_score,
                    collaboration_recommendation=recommendation,
                    optimal_interaction_methods=interaction_methods
                )
                
                proximity_scores.append(proximity_score)
        
        return proximity_scores
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        earth_radius = 6371.0
        
        return earth_radius * c
    
    def _distance_to_score(self, distance_km: float) -> float:
        """Convert distance to compatibility score (0-1)"""
        if distance_km <= 50:  # Same city
            return 1.0
        elif distance_km <= 500:  # Same region
            return 0.8
        elif distance_km <= 2000:  # Same country or nearby
            return 0.6
        elif distance_km <= 8000:  # Same continent
            return 0.4
        else:  # Different continent
            return 0.2
    
    async def _calculate_timezone_score(self, tz1: str, tz2: str) -> float:
        """Calculate timezone compatibility score"""
        try:
            # Get timezone objects
            timezone1 = pytz.timezone(tz1)
            timezone2 = pytz.timezone(tz2)
            
            # Get current time in both timezones
            now = datetime.now(pytz.UTC)
            time1 = now.astimezone(timezone1)
            time2 = now.astimezone(timezone2)
            
            # Calculate time difference in hours
            diff = abs((time1.utcoffset() - time2.utcoffset()).total_seconds() / 3600)
            
            # Convert to score
            if diff <= 2:
                return 1.0  # Excellent
            elif diff <= 5:
                return 0.8  # Good
            elif diff <= 8:
                return 0.6  # Moderate
            elif diff <= 11:
                return 0.4  # Challenging
            else:
                return 0.2  # Difficult
                
        except Exception as e:
            logger.warning(f"Error calculating timezone score: {e}")
            return 0.5  # Default moderate score
    
    def _calculate_cultural_score(
        self,
        lang1: str, lang2: str,
        context1: Dict[str, Any], context2: Dict[str, Any]
    ) -> float:
        """Calculate cultural compatibility score"""
        # Base score from language compatibility
        lang_score = self.cultural_compatibility_matrix.get((lang1, lang2), 0.3)
        
        # Adjust based on cultural context
        context_factors = []
        
        # Business culture similarity
        if context1.get('business_culture') and context2.get('business_culture'):
            similarity = 1 - abs(
                context1.get('business_culture', 0.5) - 
                context2.get('business_culture', 0.5)
            )
            context_factors.append(similarity)
        
        # Work style compatibility
        if context1.get('work_style') and context2.get('work_style'):
            style1 = context1.get('work_style', 'collaborative')
            style2 = context2.get('work_style', 'collaborative')
            style_score = 1.0 if style1 == style2 else 0.7
            context_factors.append(style_score)
        
        # Communication style
        if context1.get('communication_style') and context2.get('communication_style'):
            comm1 = context1.get('communication_style', 'direct')
            comm2 = context2.get('communication_style', 'direct')
            comm_score = 1.0 if comm1 == comm2 else 0.6
            context_factors.append(comm_score)
        
        # Combine language and context scores
        if context_factors:
            context_score = statistics.mean(context_factors)
            return (lang_score * 0.6) + (context_score * 0.4)
        else:
            return lang_score
    
    def _calculate_market_opportunity_score(
        self,
        loc_a: GeographicLocation,
        loc_b: GeographicLocation
    ) -> float:
        """Calculate market opportunity score for collaboration"""
        # Get market data for both regions
        continent_a = loc_a.continent.lower().replace(' ', '_')
        continent_b = loc_b.continent.lower().replace(' ', '_')
        
        market_a = self.market_data.get(continent_a, {})
        market_b = self.market_data.get(continent_b, {})
        
        if not market_a or not market_b:
            return 0.5  # Default moderate score
        
        # Calculate market factors
        factors = []
        
        # Social media penetration synergy
        penetration_a = market_a.get('social_media_penetration', 0.5)
        penetration_b = market_b.get('social_media_penetration', 0.5)
        penetration_score = (penetration_a + penetration_b) / 2
        factors.append(penetration_score)
        
        # CPM opportunity (higher CPM = better monetization)
        cpm_a = market_a.get('avg_cpm', 2.0)
        cpm_b = market_b.get('avg_cpm', 2.0)
        cpm_score = min((cpm_a + cpm_b) / 10.0, 1.0)  # Normalize to 0-1
        factors.append(cpm_score)
        
        # Platform overlap
        platforms_a = set(market_a.get('primary_platforms', []))
        platforms_b = set(market_b.get('primary_platforms', []))
        platform_overlap = len(platforms_a.intersection(platforms_b)) / max(len(platforms_a.union(platforms_b)), 1)
        factors.append(platform_overlap)
        
        # Market tier compatibility
        tier_compatibility = 1.0 if loc_a.market_tier == loc_b.market_tier else 0.7
        factors.append(tier_compatibility)
        
        return statistics.mean(factors)
    
    def _calculate_logistical_score(
        self,
        loc_a: GeographicLocation,
        loc_b: GeographicLocation,
        distance_km: float
    ) -> float:
        """Calculate logistical compatibility score"""
        factors = []
        
        # Distance factor (already calculated)
        distance_score = self._distance_to_score(distance_km)
        factors.append(distance_score)
        
        # Internet quality for remote collaboration
        internet_score = min(loc_a.internet_quality, loc_b.internet_quality)
        factors.append(internet_score)
        
        # Cost of living compatibility (for potential travel/meetings)
        col_diff = abs(loc_a.cost_of_living_index - loc_b.cost_of_living_index)
        col_score = max(0, 1 - (col_diff / 200))  # Normalize large differences
        factors.append(col_score)
        
        # Business hours overlap
        overlap_score = self._calculate_business_hours_overlap(loc_a, loc_b)
        factors.append(overlap_score)
        
        return statistics.mean(factors)
    
    def _calculate_business_hours_overlap(
        self,
        loc_a: GeographicLocation,
        loc_b: GeographicLocation
    ) -> float:
        """Calculate business hours overlap between locations"""
        try:
            # Convert business hours to UTC
            tz_a = pytz.timezone(loc_a.timezone)
            tz_b = pytz.timezone(loc_b.timezone)
            
            # Create dummy date for calculation
            base_date = datetime(2024, 1, 1)  # Monday
            
            # Business hours in local time
            start_a = tz_a.localize(base_date.replace(hour=loc_a.business_hours[0]))
            end_a = tz_a.localize(base_date.replace(hour=loc_a.business_hours[1]))
            
            start_b = tz_b.localize(base_date.replace(hour=loc_b.business_hours[0]))
            end_b = tz_b.localize(base_date.replace(hour=loc_b.business_hours[1]))
            
            # Convert to UTC
            start_a_utc = start_a.astimezone(pytz.UTC)
            end_a_utc = end_a.astimezone(pytz.UTC)
            start_b_utc = start_b.astimezone(pytz.UTC)
            end_b_utc = end_b.astimezone(pytz.UTC)
            
            # Calculate overlap
            overlap_start = max(start_a_utc, start_b_utc)
            overlap_end = min(end_a_utc, end_b_utc)
            
            if overlap_start < overlap_end:
                overlap_hours = (overlap_end - overlap_start).total_seconds() / 3600
                # Normalize to 0-1 (assuming 8-hour workday)
                return min(overlap_hours / 8.0, 1.0)
            else:
                return 0.0  # No overlap
                
        except Exception as e:
            logger.warning(f"Error calculating business hours overlap: {e}")
            return 0.5  # Default moderate score
    
    def _generate_collaboration_recommendation(self, overall_score: float) -> str:
        """Generate collaboration recommendation based on overall score"""
        if overall_score >= 0.8:
            return "Excellent collaboration potential - ideal geographic compatibility"
        elif overall_score >= 0.6:
            return "Good collaboration potential - minor geographic considerations"
        elif overall_score >= 0.4:
            return "Moderate collaboration potential - requires planning for geographic factors"
        elif overall_score >= 0.2:
            return "Challenging collaboration - significant geographic barriers to address"
        else:
            return "Difficult collaboration - major geographic obstacles"
    
    def _determine_interaction_methods(
        self,
        distance_km: float,
        timezone_score: float,
        cultural_score: float
    ) -> List[str]:
        """Determine optimal interaction methods"""
        methods = []
        
        # Always possible
        methods.append("asynchronous_communication")
        
        # Based on timezone compatibility
        if timezone_score >= 0.6:
            methods.append("real_time_video_calls")
            methods.append("collaborative_live_streams")
        
        if timezone_score >= 0.4:
            methods.append("scheduled_meetings")
        
        # Based on distance
        if distance_km <= 500:
            methods.append("in_person_meetings")
            methods.append("local_event_collaboration")
        
        if distance_km <= 2000:
            methods.append("regional_meetups")
        
        # Based on cultural compatibility
        if cultural_score >= 0.7:
            methods.append("direct_communication")
        else:
            methods.append("structured_communication")
            methods.append("cultural_liaison")
        
        # Digital-first methods
        methods.extend([
            "shared_digital_workspace",
            "project_management_tools",
            "file_sharing_platforms"
        ])
        
        return list(set(methods))  # Remove duplicates
    
    async def _analyze_timezone_compatibility(
        self,
        locations: List[GeographicLocation]
    ) -> TimezoneAnalysis:
        """Comprehensive timezone compatibility analysis"""
        try:
            creator_timezones = {loc.creator_id: loc.timezone for loc in locations}
            
            # Calculate time differences between all pairs
            time_differences = {}
            for i, loc_a in enumerate(locations):
                for j, loc_b in enumerate(locations[i+1:], i+1):
                    tz_a = pytz.timezone(loc_a.timezone)
                    tz_b = pytz.timezone(loc_b.timezone)
                    
                    now = datetime.now(pytz.UTC)
                    time_a = now.astimezone(tz_a)
                    time_b = now.astimezone(tz_b)
                    
                    diff_hours = (time_a.utcoffset() - time_b.utcoffset()).total_seconds() / 3600
                    time_differences[(loc_a.creator_id, loc_b.creator_id)] = diff_hours
            
            # Find optimal meeting windows
            optimal_windows = await self._find_optimal_meeting_windows(locations)
            
            # Calculate collaboration difficulty
            avg_time_diff = statistics.mean([abs(diff) for diff in time_differences.values()])
            difficulty_score = min(avg_time_diff / 12.0, 1.0)  # Normalize to 0-1
            
            # Generate recommended schedule
            recommended_schedule = await self._generate_timezone_schedule(locations, optimal_windows)
            
            # Identify advantages and challenges
            advantages, challenges = self._analyze_timezone_advantages_challenges(
                locations, time_differences
            )
            
            # Assess follow-the-sun potential
            follow_sun_potential = await self._assess_follow_the_sun_potential(locations)
            
            return TimezoneAnalysis(
                creator_timezones=creator_timezones,
                time_difference_hours=time_differences,
                optimal_meeting_windows=optimal_windows,
                collaboration_difficulty_score=difficulty_score,
                recommended_schedule=recommended_schedule,
                timezone_advantages=advantages,
                timezone_challenges=challenges,
                follow_the_sun_potential=follow_sun_potential
            )
            
        except Exception as e:
            logger.error(f"Error in timezone analysis: {e}")
            raise
    
    async def _find_optimal_meeting_windows(
        self,
        locations: List[GeographicLocation]
    ) -> List[Dict[str, Any]]:
        """Find optimal meeting windows for all creators"""
        windows = []
        
        # For each hour of the day (UTC), check if it's reasonable for all creators
        for utc_hour in range(24):
            local_times = []
            all_reasonable = True
            
            for location in locations:
                tz = pytz.timezone(location.timezone)
                utc_time = datetime.now(pytz.UTC).replace(hour=utc_hour, minute=0, second=0, microsecond=0)
                local_time = utc_time.astimezone(tz)
                local_hour = local_time.hour
                
                # Check if this is a reasonable meeting time (7 AM - 10 PM)
                if not (7 <= local_hour <= 22):
                    all_reasonable = False
                    break
                
                local_times.append({
                    'creator_id': location.creator_id,
                    'local_time': local_time.strftime('%H:%M'),
                    'local_hour': local_hour
                })
            
            if all_reasonable:
                # Calculate quality score based on how close to business hours
                quality_scores = []
                for location in locations:
                    tz = pytz.timezone(location.timezone)
                    utc_time = datetime.now(pytz.UTC).replace(hour=utc_hour, minute=0, second=0, microsecond=0)
                    local_time = utc_time.astimezone(tz)
                    local_hour = local_time.hour
                    
                    # Business hours quality (9-17 = 1.0, gradual decline outside)
                    if 9 <= local_hour <= 17:
                        quality = 1.0
                    elif 8 <= local_hour <= 18:
                        quality = 0.8
                    elif 7 <= local_hour <= 19:
                        quality = 0.6
                    else:
                        quality = 0.4
                    
                    quality_scores.append(quality)
                
                avg_quality = statistics.mean(quality_scores)
                
                windows.append({
                    'utc_hour': utc_hour,
                    'local_times': local_times,
                    'quality_score': avg_quality,
                    'window_type': 'business_hours' if avg_quality >= 0.8 else 'acceptable'
                })
        
        # Sort by quality score
        windows.sort(key=lambda x: x['quality_score'], reverse=True)
        
        return windows[:5]  # Return top 5 windows
    
    async def _generate_timezone_schedule(
        self,
        locations: List[GeographicLocation],
        optimal_windows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate recommended collaboration schedule"""
        if not optimal_windows:
            return {
                "recommendation": "asynchronous_only",
                "reason": "No suitable real-time meeting windows found"
            }
        
        best_window = optimal_windows[0]
        
        schedule = {
            "primary_meeting_time": {
                "utc_hour": best_window['utc_hour'],
                "local_times": best_window['local_times'],
                "frequency": "weekly"
            },
            "secondary_meeting_times": [],
            "asynchronous_work_periods": [],
            "rotation_schedule": None
        }
        
        # Add secondary windows if available
        if len(optimal_windows) > 1:
            schedule["secondary_meeting_times"] = optimal_windows[1:3]
        
        # Define asynchronous work periods
        for location in locations:
            tz = pytz.timezone(location.timezone)
            
            # Find their best productive hours outside meeting times
            productive_hours = []
            for hour in range(24):
                utc_time = datetime.now(pytz.UTC).replace(hour=hour, minute=0, second=0, microsecond=0)
                local_time = utc_time.astimezone(tz)
                local_hour = local_time.hour
                
                # Productive hours: 8-12, 14-18
                if (8 <= local_hour <= 12) or (14 <= local_hour <= 18):
                    if hour not in [w['utc_hour'] for w in optimal_windows[:2]]:
                        productive_hours.append({
                            'utc_hour': hour,
                            'local_hour': local_hour
                        })
            
            schedule["asynchronous_work_periods"].append({
                'creator_id': location.creator_id,
                'productive_hours': productive_hours[:4]  # Top 4 hours
            })
        
        return schedule
    
    def _analyze_timezone_advantages_challenges(
        self,
        locations: List[GeographicLocation],
        time_differences: Dict[Tuple[str, str], float]
    ) -> Tuple[List[str], List[str]]:
        """Analyze timezone advantages and challenges"""
        advantages = []
        challenges = []
        
        max_diff = max([abs(diff) for diff in time_differences.values()]) if time_differences else 0
        min_diff = min([abs(diff) for diff in time_differences.values()]) if time_differences else 0
        
        # Advantages
        if max_diff <= 3:
            advantages.append("Excellent real-time collaboration potential")
        
        if max_diff >= 6:
            advantages.append("Potential for 'follow the sun' work model")
            advantages.append("Extended productive hours across time zones")
        
        if len(set(loc.continent for loc in locations)) > 1:
            advantages.append("Global market reach and diverse perspectives")
        
        # Challenges
        if max_diff >= 8:
            challenges.append("Limited real-time meeting opportunities")
        
        if max_diff >= 12:
            challenges.append("Significant coordination complexity")
        
        if min_diff >= 4:
            challenges.append("No overlapping business hours")
        
        # Check for awkward meeting times
        awkward_times = 0
        for location in locations:
            for diff in time_differences.values():
                if isinstance(diff, (int, float)):
                    # Check if meetings would be at awkward hours
                    meeting_hour = (12 + diff) % 24  # Assuming 12 UTC as base
                    if meeting_hour < 7 or meeting_hour > 22:
                        awkward_times += 1
        
        if awkward_times > len(locations):
            challenges.append("Meetings require awkward hours for some participants")
        
        return advantages, challenges
    
    async def _assess_follow_the_sun_potential(self, locations: List[GeographicLocation]) -> bool:
        """Assess potential for follow-the-sun collaboration model"""
        if len(locations) < 3:
            return False
        
        # Get all timezones
        timezones = [loc.timezone for loc in locations]
        
        # Calculate spread across 24 hours
        utc_offsets = []
        for tz_name in timezones:
            tz = pytz.timezone(tz_name)
            offset = datetime.now(tz).utcoffset().total_seconds() / 3600
            utc_offsets.append(offset)
        
        # Check if there's good coverage across different time zones
        utc_offsets.sort()
        
        # Look for gaps larger than 8 hours
        max_gap = 0
        for i in range(len(utc_offsets)):
            next_offset = utc_offsets[(i + 1) % len(utc_offsets)]
            gap = (next_offset - utc_offsets[i]) % 24
            max_gap = max(max_gap, gap)
        
        # Good follow-the-sun potential if max gap is <= 12 hours
        return max_gap <= 12
    
    async def _assess_cultural_compatibility(
        self,
        locations: List[GeographicLocation]
    ) -> Dict[str, Any]:
        """Assess cultural compatibility between creators"""
        # Language analysis
        languages = set()
        for location in locations:
            languages.add(location.primary_language)
            languages.update(location.secondary_languages)
        
        # Primary language overlap
        primary_languages = [loc.primary_language for loc in locations]
        common_primary = len(set(primary_languages)) == 1
        
        # Cultural context analysis
        cultural_factors = []
        for location in locations:
            cultural_factors.append(location.cultural_context)
        
        # Business culture similarity
        business_cultures = [
            ctx.get('business_culture', 'collaborative') 
            for ctx in cultural_factors if ctx
        ]
        business_alignment = len(set(business_cultures)) <= 2
        
        return {
            "language_diversity": len(languages),
            "common_primary_language": common_primary,
            "business_culture_alignment": business_alignment,
            "overall_compatibility": "high" if common_primary and business_alignment else "medium",
            "recommendations": self._generate_cultural_recommendations(locations)
        }
    
    def _generate_cultural_recommendations(self, locations: List[GeographicLocation]) -> List[str]:
        """Generate cultural compatibility recommendations"""
        recommendations = []
        
        # Language recommendations
        primary_languages = [loc.primary_language for loc in locations]
        if len(set(primary_languages)) > 1:
            most_common = max(set(primary_languages), key=primary_languages.count)
            recommendations.append(f"Consider using {most_common} as primary collaboration language")
            
            if 'en' not in primary_languages and any(
                'en' in loc.secondary_languages for loc in locations
            ):
                recommendations.append("English could serve as a common secondary language")
        
        # Cultural recommendations
        recommendations.extend([
            "Establish clear communication protocols early",
            "Be mindful of cultural holidays and observances",
            "Consider cultural differences in feedback styles",
            "Plan for potential differences in meeting etiquette"
        ])
        
        return recommendations
    
    async def _identify_market_synergies(
        self,
        locations: List[GeographicLocation]
    ) -> List[Dict[str, Any]]:
        """Identify market synergies between creator locations"""
        synergies = []
        
        # Regional market combinations
        continents = list(set(loc.continent for loc in locations))
        
        for continent in continents:
            continent_key = continent.lower().replace(' ', '_')
            market_data = self.market_data.get(continent_key, {})
            
            if market_data:
                synergy = {
                    "region": continent,
                    "opportunity_type": "regional_expansion",
                    "market_data": market_data,
                    "creators_in_region": [
                        loc.creator_id for loc in locations 
                        if loc.continent == continent
                    ],
                    "potential": "high" if market_data.get('creator_economy_maturity') == 'mature' else "medium"
                }
                synergies.append(synergy)
        
        # Cross-continental opportunities
        if len(continents) > 1:
            synergies.append({
                "opportunity_type": "global_collaboration",
                "description": "Multi-continental creator collaboration for global reach",
                "advantages": [
                    "24/7 content production potential",
                    "Diverse cultural perspectives",
                    "Multiple market access"
                ],
                "potential": "high"
            })
        
        # Time zone arbitrage opportunities
        time_zones = [loc.timezone for loc in locations]
        if len(set(time_zones)) >= 3:
            synergies.append({
                "opportunity_type": "timezone_arbitrage",
                "description": "Leverage time zone differences for content optimization",
                "advantages": [
                    "Optimal posting times for different markets",
                    "Extended customer support hours",
                    "Continuous content pipeline"
                ],
                "potential": "medium"
            })
        
        return synergies
    
    async def _generate_logistical_recommendations(
        self,
        locations: List[GeographicLocation],
        proximity_scores: List[ProximityScore]
    ) -> List[Dict[str, Any]]:
        """Generate logistical recommendations"""
        recommendations = []
        
        # Communication recommendations
        avg_timezone_score = statistics.mean([score.timezone_score for score in proximity_scores])
        
        if avg_timezone_score >= 0.7:
            recommendations.append({
                "type": "communication",
                "priority": "high",
                "recommendation": "Schedule regular real-time meetings",
                "details": "Good timezone compatibility allows for frequent synchronous communication"
            })
        else:
            recommendations.append({
                "type": "communication",
                "priority": "high",
                "recommendation": "Implement robust asynchronous communication protocols",
                "details": "Use project management tools, detailed documentation, and scheduled updates"
            })
        
        # Meeting recommendations
        avg_geographic_score = statistics.mean([score.geographic_score for score in proximity_scores])
        
        if avg_geographic_score >= 0.7:
            recommendations.append({
                "type": "meetings",
                "priority": "medium",
                "recommendation": "Plan periodic in-person meetings",
                "details": "Geographic proximity allows for cost-effective face-to-face collaboration"
            })
        else:
            recommendations.append({
                "type": "meetings",
                "priority": "medium",
                "recommendation": "Invest in high-quality video conferencing setup",
                "details": "Excellent remote meeting infrastructure essential for distant collaboration"
            })
        
        # Technology recommendations
        min_internet_quality = min(loc.internet_quality for loc in locations)
        
        if min_internet_quality < 0.7:
            recommendations.append({
                "type": "technology",
                "priority": "high",
                "recommendation": "Ensure reliable internet connectivity for all participants",
                "details": "Consider backup internet options for critical collaboration sessions"
            })
        
        # Cultural recommendations
        avg_cultural_score = statistics.mean([score.cultural_score for score in proximity_scores])
        
        if avg_cultural_score < 0.6:
            recommendations.append({
                "type": "cultural",
                "priority": "medium",
                "recommendation": "Implement cultural awareness training",
                "details": "Address cultural differences proactively to improve collaboration effectiveness"
            })
        
        return recommendations
    
    async def _determine_optimal_collaboration_structure(
        self,
        locations: List[GeographicLocation],
        proximity_scores: List[ProximityScore],
        timezone_analysis: TimezoneAnalysis
    ) -> Dict[str, Any]:
        """Determine optimal collaboration structure"""
        avg_proximity = statistics.mean([score.overall_proximity_score for score in proximity_scores])
        
        if avg_proximity >= 0.8:
            structure_type = "highly_integrated"
            description = "Frequent real-time collaboration with regular synchronous meetings"
        elif avg_proximity >= 0.6:
            structure_type = "hybrid"
            description = "Mix of real-time and asynchronous collaboration"
        elif avg_proximity >= 0.4:
            structure_type = "asynchronous_primary"
            description = "Primarily asynchronous with scheduled synchronous touchpoints"
        else:
            structure_type = "distributed_async"
            description = "Fully distributed asynchronous collaboration model"
        
        # Determine coordination model
        if timezone_analysis.follow_the_sun_potential:
            coordination_model = "follow_the_sun"
        elif len(timezone_analysis.optimal_meeting_windows) > 0:
            coordination_model = "scheduled_sync"
        else:
            coordination_model = "pure_async"
        
        # Meeting frequency
        if avg_proximity >= 0.7:
            meeting_frequency = "weekly"
        elif avg_proximity >= 0.5:
            meeting_frequency = "bi_weekly"
        else:
            meeting_frequency = "monthly"
        
        return {
            "structure_type": structure_type,
            "description": description,
            "coordination_model": coordination_model,
            "meeting_frequency": meeting_frequency,
            "primary_communication_method": "video_calls" if avg_proximity >= 0.6 else "async_messaging",
            "decision_making_process": "consensus" if avg_proximity >= 0.7 else "delegated",
            "work_distribution": "collaborative" if avg_proximity >= 0.6 else "modular"
        }
    
    async def _identify_geographic_advantages(
        self,
        locations: List[GeographicLocation],
        market_synergies: List[Dict[str, Any]]
    ) -> List[str]:
        """Identify geographic advantages"""
        advantages = []
        
        # Market reach
        continents = set(loc.continent for loc in locations)
        if len(continents) > 1:
            advantages.append("Global market reach across multiple continents")
        
        # Language diversity
        languages = set()
        for loc in locations:
            languages.add(loc.primary_language)
            languages.update(loc.secondary_languages)
        
        if len(languages) > 2:
            advantages.append("Multilingual capabilities for diverse audience reach")
        
        # Time zone coverage
        timezones = [loc.timezone for loc in locations]
        if len(set(timezones)) >= 3:
            advantages.append("Extended time zone coverage for global engagement")
        
        # Market maturity diversity
        market_tiers = set(loc.market_tier for loc in locations)
        if len(market_tiers) > 1:
            advantages.append("Diverse market maturity levels providing growth opportunities")
        
        # High-value markets
        tier_1_count = sum(1 for loc in locations if loc.market_tier == "tier_1")
        if tier_1_count > 0:
            advantages.append("Access to high-value tier 1 markets")
        
        return advantages
    
    async def _identify_geographic_challenges(
        self,
        locations: List[GeographicLocation],
        proximity_scores: List[ProximityScore]
    ) -> List[str]:
        """Identify geographic challenges"""
        challenges = []
        
        # Low proximity scores
        avg_proximity = statistics.mean([score.overall_proximity_score for score in proximity_scores])
        if avg_proximity < 0.4:
            challenges.append("Low overall geographic compatibility")
        
        # Timezone difficulties
        min_timezone_score = min([score.timezone_score for score in proximity_scores])
        if min_timezone_score < 0.4:
            challenges.append("Significant timezone coordination challenges")
        
        # Cultural barriers
        min_cultural_score = min([score.cultural_score for score in proximity_scores])
        if min_cultural_score < 0.5:
            challenges.append("Cultural and language barriers")
        
        # Large distances
        max_geographic_score = max([score.geographic_score for score in proximity_scores])
        if max_geographic_score < 0.3:
            challenges.append("Very large geographic distances limiting in-person collaboration")
        
        # Internet quality issues
        min_internet = min(loc.internet_quality for loc in locations)
        if min_internet < 0.6:
            challenges.append("Internet connectivity concerns for remote collaboration")
        
        # Cost of living disparities
        col_indices = [loc.cost_of_living_index for loc in locations]
        col_variance = np.var(col_indices)
        if col_variance > 2500:  # High variance in cost of living
            challenges.append("Significant cost of living disparities affecting collaboration economics")
        
        return challenges
    
    async def _calculate_confidence_score(
        self,
        locations: List[GeographicLocation],
        proximity_scores: List[ProximityScore]
    ) -> float:
        """Calculate confidence score for geographic analysis"""
        confidence_factors = []
        
        # Data completeness
        complete_profiles = sum(
            1 for loc in locations 
            if all([loc.latitude, loc.longitude, loc.timezone, loc.primary_language])
        )
        completeness_score = complete_profiles / len(locations)
        confidence_factors.append(completeness_score)
        
        # Location accuracy (assume high for this implementation)
        accuracy_score = 0.9  # Would be based on location data source quality
        confidence_factors.append(accuracy_score)
        
        # Analysis consistency
        score_variance = np.var([score.overall_proximity_score for score in proximity_scores])
        consistency_score = max(0, 1 - (score_variance * 2))
        confidence_factors.append(consistency_score)
        
        # Sample size adequacy
        sample_score = min(len(locations) / 5.0, 1.0)  # Assume 5 creators = good sample
        confidence_factors.append(sample_score)
        
        return statistics.mean(confidence_factors)


# Export main classes
__all__ = [
    'GeographicMatcher',
    'GeographicLocation',
    'GeographicProfile',
    'LocationCompatibility',
    'TimezoneAnalysis',
    'ProximityScore',
    'ProximityLevel',
    'TimezoneCompatibility',
    'CulturalAlignment'
]