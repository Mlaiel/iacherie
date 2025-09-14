"""
Advanced Demographic Mapping Engine for Ainflue Distribution Platform

This module provides sophisticated demographic analysis and intelligent mapping capabilities
for audience segmentation and targeted content distribution across platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import json

logger = logging.getLogger(__name__)


class DemographicCategory(Enum):
    """Demographic categories for analysis"""
    AGE_GROUP = "age_group"
    GENDER = "gender"
    LOCATION = "location"
    EDUCATION = "education"
    INCOME_LEVEL = "income_level"
    OCCUPATION = "occupation"
    INTERESTS = "interests"
    LIFESTYLE = "lifestyle"
    DEVICE_USAGE = "device_usage"
    PLATFORM_BEHAVIOR = "platform_behavior"


class AgeGroup(Enum):
    """Age group classifications"""
    GEN_Z = "gen_z"  # 16-24
    MILLENNIAL = "millennial"  # 25-40
    GEN_X = "gen_x"  # 41-56
    BOOMER = "boomer"  # 57+
    UNKNOWN = "unknown"


class DeviceType(Enum):
    """Device usage patterns"""
    MOBILE_PRIMARY = "mobile_primary"
    DESKTOP_PRIMARY = "desktop_primary"
    TABLET_PRIMARY = "tablet_primary"
    MULTI_DEVICE = "multi_device"


@dataclass
class DemographicProfile:
    """Complete demographic profile for a user"""
    user_id: str
    platform: str
    age_group: AgeGroup
    age_confidence: float
    gender: Optional[str]
    gender_confidence: float
    location_country: Optional[str]
    location_region: Optional[str]
    location_city: Optional[str]
    location_confidence: float
    education_level: Optional[str]
    education_confidence: float
    income_bracket: Optional[str]
    income_confidence: float
    occupation_category: Optional[str]
    occupation_confidence: float
    interests: List[str]
    lifestyle_indicators: Dict[str, float]
    device_preferences: Dict[DeviceType, float]
    platform_activity_patterns: Dict[str, float]
    demographic_segments: List[str]
    last_updated: datetime
    profile_completeness: float


@dataclass
class DemographicInsight:
    """Actionable demographic insights"""
    insight_type: str
    demographic_segment: str
    description: str
    confidence: float
    market_size: int
    engagement_potential: float
    recommended_strategies: List[str]
    content_preferences: Dict[str, float]
    optimal_timing: Dict[str, float]
    platform_recommendations: List[str]


class IntelligentDemographicMapper:
    """
    AI-powered demographic analysis and mapping engine
    
    Features:
    - Multi-dimensional demographic profiling
    - Behavioral pattern analysis
    - Geographic intelligence
    - Device and platform usage analysis
    - Lifestyle and interest mapping
    - Predictive demographic modeling
    """

    def __init__(self) -> None:
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.demographic_models = {}
        self.clustering_model = KMeans(n_clusters=12, random_state=42)
        self.segment_cache = {}
        self.geo_intelligence = {}
        
    async def analyze_user_demographics(
        self,
        user_id: str,
        platform: str,
        user_data: Dict[str, Any],
        interaction_history: List[Dict[str, Any]],
        external_signals: Optional[Dict[str, Any]] = None
    ) -> DemographicProfile:
        """
        Analyze comprehensive user demographics from multiple data sources
        
        Args:
            user_id: Unique user identifier
            platform: Platform being analyzed
            user_data: Direct user profile data
            interaction_history: Historical interaction data
            external_signals: Additional demographic signals
            
        Returns:
            Complete demographic profile
        """
        try:
            # Analyze age group
            age_analysis = await self._analyze_age_group(
                user_data, interaction_history, external_signals
            )
            
            # Analyze gender
            gender_analysis = await self._analyze_gender(
                user_data, interaction_history, external_signals
            )
            
            # Analyze location
            location_analysis = await self._analyze_location(
                user_data, interaction_history, external_signals
            )
            
            # Analyze education
            education_analysis = await self._analyze_education_level(
                user_data, interaction_history, external_signals
            )
            
            # Analyze income
            income_analysis = await self._analyze_income_bracket(
                user_data, interaction_history, external_signals
            )
            
            # Analyze occupation
            occupation_analysis = await self._analyze_occupation(
                user_data, interaction_history, external_signals
            )
            
            # Extract interests and lifestyle
            interests = await self._extract_interests(interaction_history)
            lifestyle = await self._analyze_lifestyle_indicators(interaction_history)
            
            # Analyze device preferences
            device_prefs = await self._analyze_device_preferences(interaction_history)
            
            # Analyze platform activity patterns
            platform_patterns = await self._analyze_platform_patterns(interaction_history)
            
            # Generate demographic segments
            segments = await self._generate_demographic_segments(
                age_analysis, gender_analysis, location_analysis,
                education_analysis, income_analysis, interests, lifestyle
            )
            
            # Calculate profile completeness
            completeness = self._calculate_profile_completeness([
                age_analysis[1], gender_analysis[1], location_analysis[1],
                education_analysis[1], income_analysis[1], occupation_analysis[1]
            ])
            
            return DemographicProfile(
                user_id=user_id,
                platform=platform,
                age_group=age_analysis[0],
                age_confidence=age_analysis[1],
                gender=gender_analysis[0],
                gender_confidence=gender_analysis[1],
                location_country=location_analysis[0].get('country'),
                location_region=location_analysis[0].get('region'),
                location_city=location_analysis[0].get('city'),
                location_confidence=location_analysis[1],
                education_level=education_analysis[0],
                education_confidence=education_analysis[1],
                income_bracket=income_analysis[0],
                income_confidence=income_analysis[1],
                occupation_category=occupation_analysis[0],
                occupation_confidence=occupation_analysis[1],
                interests=interests,
                lifestyle_indicators=lifestyle,
                device_preferences=device_prefs,
                platform_activity_patterns=platform_patterns,
                demographic_segments=segments,
                last_updated=datetime.utcnow(),
                profile_completeness=completeness
            )
            
        except Exception as e:
            logger.error(f"Error analyzing user demographics: {e}")
            raise

    async def _analyze_age_group(
        self,
        user_data: Dict[str, Any],
        interaction_history: List[Dict[str, Any]],
        external_signals: Optional[Dict[str, Any]]
    ) -> Tuple[AgeGroup, float]:
        """Analyze and predict user age group"""
        
        confidence_factors = []
        age_indicators = {}
        
        # Direct age data
        if user_data.get('age'):
            age = int(user_data['age'])
            if 16 <= age <= 24:
                return AgeGroup.GEN_Z, 0.95
            elif 25 <= age <= 40:
                return AgeGroup.MILLENNIAL, 0.95
            elif 41 <= age <= 56:
                return AgeGroup.GEN_X, 0.95
            elif age >= 57:
                return AgeGroup.BOOMER, 0.95
        
        # Birth year analysis
        if user_data.get('birth_year'):
            birth_year = int(user_data['birth_year'])
            current_year = datetime.now().year
            age = current_year - birth_year
            if 16 <= age <= 24:
                return AgeGroup.GEN_Z, 0.9
            elif 25 <= age <= 40:
                return AgeGroup.MILLENNIAL, 0.9
            elif 41 <= age <= 56:
                return AgeGroup.GEN_X, 0.9
            elif age >= 57:
                return AgeGroup.BOOMER, 0.9
        
        # Behavioral age indicators
        behavioral_indicators = self._analyze_age_behavioral_patterns(interaction_history)
        
        # Platform usage patterns
        platform_indicators = self._analyze_age_platform_patterns(interaction_history)
        
        # Content preferences
        content_indicators = self._analyze_age_content_patterns(interaction_history)
        
        # Combine indicators
        all_indicators = {**behavioral_indicators, **platform_indicators, **content_indicators}
        
        if all_indicators:
            # Weighted voting for age group
            age_scores = {
                AgeGroup.GEN_Z: 0,
                AgeGroup.MILLENNIAL: 0,
                AgeGroup.GEN_X: 0,
                AgeGroup.BOOMER: 0
            }
            
            for indicator, score in all_indicators.items():
                if 'mobile' in indicator or 'tiktok' in indicator or 'instagram' in indicator:
                    age_scores[AgeGroup.GEN_Z] += score
                elif 'facebook' in indicator or 'linkedin' in indicator:
                    age_scores[AgeGroup.MILLENNIAL] += score * 0.7
                    age_scores[AgeGroup.GEN_X] += score * 0.3
                elif 'email' in indicator or 'traditional' in indicator:
                    age_scores[AgeGroup.GEN_X] += score * 0.6
                    age_scores[AgeGroup.BOOMER] += score * 0.4
            
            if any(score > 0 for score in age_scores.values()):
                predicted_age = max(age_scores, key=age_scores.get)
                confidence = min(0.8, age_scores[predicted_age] / sum(age_scores.values()))
                return predicted_age, confidence
        
        return AgeGroup.UNKNOWN, 0.1

    def _analyze_age_behavioral_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze behavioral patterns that indicate age"""
        
        indicators = {}
        
        # Activity timing patterns
        if interactions:
            hours = []
            for interaction in interactions:
                timestamp = interaction.get('timestamp')
                if timestamp:
                    hour = datetime.fromisoformat(timestamp).hour
                    hours.append(hour)
            
            if hours:
                # Late night activity (Gen Z pattern)
                late_night_ratio = sum(1 for h in hours if h >= 22 or h <= 2) / len(hours)
                indicators['late_night_activity'] = late_night_ratio
                
                # Business hours activity (older demographics)
                business_hours_ratio = sum(1 for h in hours if 9 <= h <= 17) / len(hours)
                indicators['business_hours_activity'] = business_hours_ratio
        
        # Interaction types
        interaction_types = [i.get('type') for i in interactions if i.get('type')]
        if interaction_types:
            total_interactions = len(interaction_types)
            
            # Quick reactions (younger users)
            quick_reactions = sum(1 for t in interaction_types if t in ['like', 'react'])
            indicators['quick_reaction_ratio'] = quick_reactions / total_interactions
            
            # Comments and shares (older users)
            thoughtful_interactions = sum(1 for t in interaction_types if t in ['comment', 'share'])
            indicators['thoughtful_interaction_ratio'] = thoughtful_interactions / total_interactions
        
        return indicators

    def _analyze_age_platform_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze platform usage patterns that indicate age"""
        
        indicators = {}
        platforms = [i.get('platform') for i in interactions if i.get('platform')]
        
        if platforms:
            total_platforms = len(platforms)
            
            # Platform preferences by age
            platform_counts = {}
            for platform in platforms:
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            for platform, count in platform_counts.items():
                ratio = count / total_platforms
                
                if platform.lower() in ['tiktok', 'snapchat', 'discord']:
                    indicators[f'{platform}_usage'] = ratio * 2.0  # Strong Gen Z indicator
                elif platform.lower() in ['instagram', 'twitter']:
                    indicators[f'{platform}_usage'] = ratio * 1.5  # Moderate youth indicator
                elif platform.lower() in ['facebook', 'linkedin']:
                    indicators[f'{platform}_usage'] = ratio * 1.0  # Older demographics
        
        return indicators

    def _analyze_age_content_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze content preferences that indicate age"""
        
        indicators = {}
        content_categories = []
        
        for interaction in interactions:
            categories = interaction.get('content_categories', [])
            content_categories.extend(categories)
        
        if content_categories:
            total_content = len(content_categories)
            category_counts = {}
            
            for category in content_categories:
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Age-related content preferences
            young_content_keywords = ['gaming', 'memes', 'viral', 'trending', 'challenge']
            mature_content_keywords = ['news', 'politics', 'business', 'finance', 'health']
            
            young_content_count = 0
            mature_content_count = 0
            
            for category, count in category_counts.items():
                if any(keyword in category.lower() for keyword in young_content_keywords):
                    young_content_count += count
                elif any(keyword in category.lower() for keyword in mature_content_keywords):
                    mature_content_count += count
            
            if total_content > 0:
                indicators['young_content_preference'] = young_content_count / total_content
                indicators['mature_content_preference'] = mature_content_count / total_content
        
        return indicators

    async def _analyze_gender(
        self,
        user_data: Dict[str, Any],
        interaction_history: List[Dict[str, Any]],
        external_signals: Optional[Dict[str, Any]]
    ) -> Tuple[Optional[str], float]:
        """Analyze and predict user gender"""
        
        # Direct gender data
        if user_data.get('gender'):
            return user_data['gender'], 0.95
        
        # Behavioral gender indicators
        behavioral_indicators = self._analyze_gender_behavioral_patterns(interaction_history)
        
        # Content preference indicators
        content_indicators = self._analyze_gender_content_patterns(interaction_history)
        
        # Combine indicators for prediction
        all_indicators = {**behavioral_indicators, **content_indicators}
        
        if all_indicators:
            # Simple scoring model (can be enhanced with ML)
            male_score = 0
            female_score = 0
            
            for indicator, score in all_indicators.items():
                if 'sports' in indicator or 'tech' in indicator or 'gaming' in indicator:
                    male_score += score
                elif 'fashion' in indicator or 'beauty' in indicator or 'lifestyle' in indicator:
                    female_score += score
            
            total_score = male_score + female_score
            if total_score > 0:
                if male_score > female_score:
                    confidence = min(0.7, male_score / total_score)
                    return 'male', confidence
                else:
                    confidence = min(0.7, female_score / total_score)
                    return 'female', confidence
        
        return None, 0.1

    def _analyze_gender_behavioral_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze behavioral patterns that may indicate gender preferences"""
        
        indicators = {}
        
        # Interaction style analysis
        interaction_types = [i.get('type') for i in interactions if i.get('type')]
        if interaction_types:
            total_interactions = len(interaction_types)
            
            # Comment engagement (generally higher for certain demographics)
            comments = sum(1 for t in interaction_types if t == 'comment')
            indicators['comment_engagement'] = comments / total_interactions
            
            # Sharing behavior
            shares = sum(1 for t in interaction_types if t == 'share')
            indicators['sharing_behavior'] = shares / total_interactions
        
        return indicators

    def _analyze_gender_content_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze content preferences that may indicate gender"""
        
        indicators = {}
        content_categories = []
        
        for interaction in interactions:
            categories = interaction.get('content_categories', [])
            content_categories.extend(categories)
        
        if content_categories:
            total_content = len(content_categories)
            category_counts = {}
            
            for category in content_categories:
                category_counts[category] = category_counts.get(category, 0) + 1
            
            # Content preference analysis
            for category, count in category_counts.items():
                ratio = count / total_content
                category_lower = category.lower()
                
                if any(keyword in category_lower for keyword in ['sports', 'tech', 'gaming', 'cars']):
                    indicators[f'{category}_preference'] = ratio
                elif any(keyword in category_lower for keyword in ['fashion', 'beauty', 'lifestyle', 'wellness']):
                    indicators[f'{category}_preference'] = ratio
        
        return indicators

    async def _analyze_location(
        self,
        user_data: Dict[str, Any],
        interaction_history: List[Dict[str, Any]],
        external_signals: Optional[Dict[str, Any]]
    ) -> Tuple[Dict[str, str], float]:
        """Analyze and predict user location"""
        
        location_info = {}
        confidence = 0.1
        
        # Direct location data
        if user_data.get('country'):
            location_info['country'] = user_data['country']
            confidence = max(confidence, 0.9)
        
        if user_data.get('region') or user_data.get('state'):
            location_info['region'] = user_data.get('region') or user_data.get('state')
            confidence = max(confidence, 0.8)
        
        if user_data.get('city'):
            location_info['city'] = user_data['city']
            confidence = max(confidence, 0.7)
        
        # IP-based location (from external signals)
        if external_signals and external_signals.get('ip_location'):
            ip_location = external_signals['ip_location']
            if not location_info.get('country') and ip_location.get('country'):
                location_info['country'] = ip_location['country']
                confidence = max(confidence, 0.6)
            if not location_info.get('region') and ip_location.get('region'):
                location_info['region'] = ip_location['region']
                confidence = max(confidence, 0.5)
        
        # Behavioral location indicators
        timezone_indicators = self._analyze_timezone_patterns(interaction_history)
        if timezone_indicators:
            # Map timezone to likely regions
            estimated_location = self._map_timezone_to_location(timezone_indicators)
            if estimated_location and not location_info:
                location_info.update(estimated_location)
                confidence = max(confidence, 0.4)
        
        return location_info, confidence

    def _analyze_timezone_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze activity patterns to infer timezone"""
        
        if not interactions:
            return {}
        
        timestamps = [i.get('timestamp') for i in interactions if i.get('timestamp')]
        if not timestamps:
            return {}
        
        hours = []
        for timestamp in timestamps:
            try:
                dt = datetime.fromisoformat(timestamp)
                hours.append(dt.hour)
            except:
                continue
        
        if not hours:
            return {}
        
        # Find peak activity hours
        hour_counts = np.bincount(hours, minlength=24)
        peak_hour = np.argmax(hour_counts)
        
        return {
            'peak_activity_hour': peak_hour,
            'hour_distribution': hour_counts.tolist(),
            'total_interactions': len(hours)
        }

    def _map_timezone_to_location(self, timezone_data: Dict[str, Any]) -> Dict[str, str]:
        """Map timezone patterns to likely geographic locations"""
        
        peak_hour = timezone_data.get('peak_activity_hour')
        if peak_hour is None:
            return {}
        
        # Simple mapping based on peak activity hours (assumes UTC timestamps)
        # This is a simplified approach - real implementation would be more sophisticated
        location_mapping = {
            range(6, 10): {'region': 'Asia-Pacific', 'timezone': 'UTC+8 to +10'},
            range(14, 18): {'region': 'Europe', 'timezone': 'UTC+1 to +3'},
            range(20, 24): {'region': 'Americas', 'timezone': 'UTC-8 to -5'}
        }
        
        for hour_range, location in location_mapping.items():
            if peak_hour in hour_range:
                return location
        
        return {}

    async def _analyze_education_level(
        self,
        user_data: Dict[str, Any],
        interaction_history: List[Dict[str, Any]],
        external_signals: Optional[Dict[str, Any]]
    ) -> Tuple[Optional[str], float]:
        """Analyze and predict education level"""
        
        # Direct education data
        if user_data.get('education'):
            return user_data['education'], 0.9
        
        # Behavioral education indicators
        content_complexity = self._analyze_content_complexity_preferences(interaction_history)
        language_complexity = self._analyze_language_complexity(interaction_history)
        platform_sophistication = self._analyze_platform_sophistication(interaction_history)
        
        # Combine indicators
        education_score = (content_complexity + language_complexity + platform_sophistication) / 3
        
        if education_score > 0.7:
            return 'higher_education', min(0.8, education_score)
        elif education_score > 0.4:
            return 'secondary_education', min(0.7, education_score)
        elif education_score > 0.2:
            return 'primary_education', min(0.6, education_score)
        
        return None, 0.2

    def _analyze_content_complexity_preferences(self, interactions: List[Dict[str, Any]]) -> float:
        """Analyze preference for complex content"""
        
        if not interactions:
            return 0.0
        
        complex_content_keywords = [
            'analysis', 'research', 'study', 'academic', 'technical',
            'scientific', 'detailed', 'comprehensive', 'professional'
        ]
        
        complex_interactions = 0
        total_interactions = 0
        
        for interaction in interactions:
            content_title = interaction.get('content_title', '').lower()
            content_description = interaction.get('content_description', '').lower()
            combined_text = f"{content_title} {content_description}"
            
            if combined_text.strip():
                total_interactions += 1
                if any(keyword in combined_text for keyword in complex_content_keywords):
                    complex_interactions += 1
        
        return complex_interactions / total_interactions if total_interactions > 0 else 0.0

    def _analyze_language_complexity(self, interactions: List[Dict[str, Any]]) -> float:
        """Analyze language complexity in user interactions"""
        
        user_comments = []
        for interaction in interactions:
            if interaction.get('type') == 'comment' and interaction.get('comment_text'):
                user_comments.append(interaction['comment_text'])
        
        if not user_comments:
            return 0.5  # Neutral when no comments available
        
        # Simple complexity indicators
        complexity_score = 0.0
        for comment in user_comments:
            words = comment.split()
            if len(words) > 10:  # Longer comments
                complexity_score += 0.3
            if any(len(word) > 8 for word in words):  # Complex vocabulary
                complexity_score += 0.2
            if any(char in comment for char in '.,;:'):  # Proper punctuation
                complexity_score += 0.1
        
        return min(1.0, complexity_score / len(user_comments))

    def _analyze_platform_sophistication(self, interactions: List[Dict[str, Any]]) -> float:
        """Analyze sophistication of platform usage"""
        
        if not interactions:
            return 0.0
        
        sophisticated_platforms = ['linkedin', 'medium', 'reddit', 'github']
        sophisticated_features = ['share', 'bookmark', 'create_list', 'tag']
        
        platform_score = 0.0
        feature_score = 0.0
        
        platforms = [i.get('platform', '').lower() for i in interactions]
        features = [i.get('type', '').lower() for i in interactions]
        
        # Platform sophistication
        if platforms:
            sophisticated_platform_count = sum(
                1 for p in platforms if p in sophisticated_platforms
            )
            platform_score = sophisticated_platform_count / len(platforms)
        
        # Feature usage sophistication
        if features:
            sophisticated_feature_count = sum(
                1 for f in features if f in sophisticated_features
            )
            feature_score = sophisticated_feature_count / len(features)
        
        return (platform_score + feature_score) / 2

    async def _analyze_income_bracket(
        self,
        user_data: Dict[str, Any],
        interaction_history: List[Dict[str, Any]],
        external_signals: Optional[Dict[str, Any]]
    ) -> Tuple[Optional[str], float]:
        """Analyze and predict income bracket"""
        
        # Direct income data
        if user_data.get('income'):
            income = float(user_data['income'])
            if income < 30000:
                return 'low_income', 0.9
            elif income < 75000:
                return 'middle_income', 0.9
            else:
                return 'high_income', 0.9
        
        # Behavioral income indicators
        premium_indicators = self._analyze_premium_behavior_patterns(interaction_history)
        spending_indicators = self._analyze_spending_behavior_indicators(interaction_history)
        
        # Combine indicators
        income_score = (premium_indicators + spending_indicators) / 2
        
        if income_score > 0.7:
            return 'high_income', min(0.7, income_score)
        elif income_score > 0.4:
            return 'middle_income', min(0.6, income_score)
        elif income_score < 0.3:
            return 'low_income', min(0.5, 1 - income_score)
        
        return None, 0.2

    def _analyze_premium_behavior_patterns(self, interactions: List[Dict[str, Any]]) -> float:
        """Analyze patterns that indicate premium/paid service usage"""
        
        premium_indicators = 0
        total_indicators = 0
        
        for interaction in interactions:
            total_indicators += 1
            
            # Premium platform features
            if interaction.get('premium_feature_used'):
                premium_indicators += 1
            
            # High-quality content preference
            content_quality = interaction.get('content_quality_score', 0)
            if content_quality > 8:  # Assuming 1-10 scale
                premium_indicators += 0.5
            
            # Engagement with premium creators
            if interaction.get('creator_tier') == 'premium':
                premium_indicators += 0.3
        
        return premium_indicators / total_indicators if total_indicators > 0 else 0.0

    def _analyze_spending_behavior_indicators(self, interactions: List[Dict[str, Any]]) -> float:
        """Analyze spending behavior indicators from interactions"""
        
        spending_indicators = []
        
        for interaction in interactions:
            # Device quality indicators
            device_type = interaction.get('device_type', '').lower()
            if 'iphone' in device_type or 'ipad' in device_type or 'premium' in device_type:
                spending_indicators.append(0.7)
            elif 'android' in device_type:
                spending_indicators.append(0.4)
            
            # Engagement with luxury/premium content
            content_categories = interaction.get('content_categories', [])
            premium_categories = ['luxury', 'premium', 'high-end', 'exclusive']
            if any(cat.lower() in premium_categories for cat in content_categories):
                spending_indicators.append(0.8)
        
        return np.mean(spending_indicators) if spending_indicators else 0.0

    async def _analyze_occupation(
        self,
        user_data: Dict[str, Any],
        interaction_history: List[Dict[str, Any]],
        external_signals: Optional[Dict[str, Any]]
    ) -> Tuple[Optional[str], float]:
        """Analyze and predict occupation category"""
        
        # Direct occupation data
        if user_data.get('occupation'):
            return user_data['occupation'], 0.9
        
        # Professional content engagement
        professional_indicators = self._analyze_professional_content_engagement(interaction_history)
        
        # Activity timing patterns
        work_schedule_indicators = self._analyze_work_schedule_patterns(interaction_history)
        
        # Platform usage patterns
        professional_platform_usage = self._analyze_professional_platform_usage(interaction_history)
        
        # Combine indicators to predict occupation category
        if professional_platform_usage > 0.3:
            return 'professional', min(0.7, professional_platform_usage)
        elif professional_indicators > 0.4:
            return 'skilled_worker', min(0.6, professional_indicators)
        elif work_schedule_indicators.get('regular_hours', False):
            return 'employed', 0.5
        
        return None, 0.2

    def _analyze_professional_content_engagement(self, interactions: List[Dict[str, Any]]) -> float:
        """Analyze engagement with professional content"""
        
        professional_keywords = [
            'business', 'career', 'professional', 'industry', 'corporate',
            'management', 'leadership', 'strategy', 'productivity', 'networking'
        ]
        
        professional_interactions = 0
        total_interactions = len(interactions)
        
        for interaction in interactions:
            content_text = f"{interaction.get('content_title', '')} {interaction.get('content_description', '')}"
            if any(keyword in content_text.lower() for keyword in professional_keywords):
                professional_interactions += 1
        
        return professional_interactions / total_interactions if total_interactions > 0 else 0.0

    def _analyze_work_schedule_patterns(self, interactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze activity patterns that indicate work schedule"""
        
        if not interactions:
            return {}
        
        weekday_hours = []
        weekend_hours = []
        
        for interaction in interactions:
            timestamp = interaction.get('timestamp')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    hour = dt.hour
                    
                    if dt.weekday() < 5:  # Monday-Friday
                        weekday_hours.append(hour)
                    else:  # Saturday-Sunday
                        weekend_hours.append(hour)
                except:
                    continue
        
        patterns = {}
        
        # Regular work hours pattern (9-5)
        if weekday_hours:
            work_hours_activity = sum(1 for h in weekday_hours if 9 <= h <= 17)
            work_hours_ratio = work_hours_activity / len(weekday_hours)
            patterns['work_hours_activity'] = work_hours_ratio
            patterns['regular_hours'] = work_hours_ratio > 0.3
        
        # Evening/weekend activity
        if weekend_hours:
            patterns['weekend_activity'] = len(weekend_hours) / (len(weekday_hours) + len(weekend_hours))
        
        return patterns

    def _analyze_professional_platform_usage(self, interactions: List[Dict[str, Any]]) -> float:
        """Analyze usage of professional platforms"""
        
        professional_platforms = ['linkedin', 'xing', 'behance', 'dribbble', 'github']
        platforms = [i.get('platform', '').lower() for i in interactions]
        
        if not platforms:
            return 0.0
        
        professional_usage = sum(1 for p in platforms if p in professional_platforms)
        return professional_usage / len(platforms)

    async def _extract_interests(self, interaction_history: List[Dict[str, Any]]) -> List[str]:
        """Extract user interests from interaction history"""
        
        interests = {}
        
        for interaction in interactions:
            # Extract from content categories
            categories = interaction.get('content_categories', [])
            for category in categories:
                interests[category] = interests.get(category, 0) + 1
            
            # Extract from topics
            topics = interaction.get('topics', [])
            for topic in topics:
                interests[topic] = interests.get(topic, 0) + 1
            
            # Extract from hashtags
            hashtags = interaction.get('hashtags', [])
            for hashtag in hashtags:
                clean_hashtag = hashtag.replace('#', '')
                interests[clean_hashtag] = interests.get(clean_hashtag, 0) + 1
        
        # Return top interests
        sorted_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)
        return [interest for interest, count in sorted_interests[:10] if count >= 2]

    async def _analyze_lifestyle_indicators(self, interaction_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze lifestyle indicators from interactions"""
        
        lifestyle_indicators = {}
        
        # Activity timing patterns
        if interaction_history:
            timestamps = [i.get('timestamp') for i in interaction_history if i.get('timestamp')]
            if timestamps:
                hours = []
                for timestamp in timestamps:
                    try:
                        hour = datetime.fromisoformat(timestamp).hour
                        hours.append(hour)
                    except:
                        continue
                
                if hours:
                    # Night owl vs early bird
                    late_night_ratio = sum(1 for h in hours if h >= 22 or h <= 6) / len(hours)
                    early_morning_ratio = sum(1 for h in hours if 6 <= h <= 9) / len(hours)
                    
                    lifestyle_indicators['night_owl_tendency'] = late_night_ratio
                    lifestyle_indicators['early_bird_tendency'] = early_morning_ratio
        
        # Content engagement patterns
        content_categories = []
        for interaction in interaction_history:
            content_categories.extend(interaction.get('content_categories', []))
        
        if content_categories:
            total_content = len(content_categories)
            
            # Health and wellness
            health_keywords = ['fitness', 'health', 'wellness', 'nutrition', 'exercise']
            health_content = sum(1 for cat in content_categories 
                               if any(keyword in cat.lower() for keyword in health_keywords))
            lifestyle_indicators['health_conscious'] = health_content / total_content
            
            # Travel and adventure
            travel_keywords = ['travel', 'adventure', 'vacation', 'explore', 'wanderlust']
            travel_content = sum(1 for cat in content_categories 
                               if any(keyword in cat.lower() for keyword in travel_keywords))
            lifestyle_indicators['travel_enthusiast'] = travel_content / total_content
            
            # Technology adoption
            tech_keywords = ['tech', 'gadget', 'innovation', 'digital', 'startup']
            tech_content = sum(1 for cat in content_categories 
                             if any(keyword in cat.lower() for keyword in tech_keywords))
            lifestyle_indicators['tech_adoption'] = tech_content / total_content
        
        return lifestyle_indicators

    async def _analyze_device_preferences(self, interaction_history: List[Dict[str, Any]]) -> Dict[DeviceType, float]:
        """Analyze device usage preferences"""
        
        device_counts = {}
        total_interactions = len(interaction_history)
        
        if total_interactions == 0:
            return {device_type: 0.0 for device_type in DeviceType}
        
        for interaction in interaction_history:
            device = interaction.get('device_type', 'unknown').lower()
            device_counts[device] = device_counts.get(device, 0) + 1
        
        # Map devices to categories
        device_preferences = {device_type: 0.0 for device_type in DeviceType}
        
        for device, count in device_counts.items():
            ratio = count / total_interactions
            
            if 'mobile' in device or 'phone' in device:
                device_preferences[DeviceType.MOBILE_PRIMARY] += ratio
            elif 'desktop' in device or 'computer' in device:
                device_preferences[DeviceType.DESKTOP_PRIMARY] += ratio
            elif 'tablet' in device or 'ipad' in device:
                device_preferences[DeviceType.TABLET_PRIMARY] += ratio
        
        # Determine multi-device usage
        used_devices = len([ratio for ratio in device_preferences.values() if ratio > 0.1])
        if used_devices >= 2:
            device_preferences[DeviceType.MULTI_DEVICE] = min(1.0, used_devices / 3.0)
        
        return device_preferences

    async def _analyze_platform_patterns(self, interaction_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze platform activity patterns"""
        
        platform_counts = {}
        total_interactions = len(interaction_history)
        
        if total_interactions == 0:
            return {}
        
        for interaction in interaction_history:
            platform = interaction.get('platform', 'unknown')
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        # Convert to ratios
        platform_patterns = {}
        for platform, count in platform_counts.items():
            platform_patterns[platform] = count / total_interactions
        
        return platform_patterns

    async def _generate_demographic_segments(
        self,
        age_analysis: Tuple[AgeGroup, float],
        gender_analysis: Tuple[Optional[str], float],
        location_analysis: Tuple[Dict[str, str], float],
        education_analysis: Tuple[Optional[str], float],
        income_analysis: Tuple[Optional[str], float],
        interests: List[str],
        lifestyle: Dict[str, float]
    ) -> List[str]:
        """Generate demographic segments based on analysis"""
        
        segments = []
        
        # Age-based segments
        age_group, age_confidence = age_analysis
        if age_confidence > 0.5:
            segments.append(f"age_{age_group.value}")
        
        # Income-based segments
        income_bracket, income_confidence = income_analysis
        if income_confidence > 0.5 and income_bracket:
            segments.append(f"income_{income_bracket}")
        
        # Education-based segments
        education_level, education_confidence = education_analysis
        if education_confidence > 0.5 and education_level:
            segments.append(f"education_{education_level}")
        
        # Interest-based segments
        if interests:
            primary_interest = interests[0]
            segments.append(f"interest_{primary_interest.lower().replace(' ', '_')}")
        
        # Lifestyle-based segments
        for lifestyle_indicator, score in lifestyle.items():
            if score > 0.6:
                segments.append(f"lifestyle_{lifestyle_indicator}")
        
        # Geographic segments
        location_info, location_confidence = location_analysis
        if location_confidence > 0.5 and location_info.get('country'):
            segments.append(f"geo_{location_info['country'].lower().replace(' ', '_')}")
        
        return segments[:5]  # Return top 5 segments

    def _calculate_profile_completeness(self, confidence_scores: List[float]) -> float:
        """Calculate overall profile completeness"""
        
        # Weight different factors
        weights = [0.2, 0.15, 0.2, 0.15, 0.15, 0.15]  # Age, gender, location, education, income, occupation
        
        weighted_scores = []
        for i, score in enumerate(confidence_scores):
            if i < len(weights):
                weighted_scores.append(score * weights[i])
        
        return sum(weighted_scores) / sum(weights[:len(confidence_scores)])

    async def generate_demographic_insights(
        self,
        demographic_profile: DemographicProfile
    ) -> List[DemographicInsight]:
        """Generate actionable insights from demographic analysis"""
        
        insights = []
        
        # Age group insights
        if demographic_profile.age_confidence > 0.7:
            age_insights = self._generate_age_group_insights(demographic_profile)
            insights.extend(age_insights)
        
        # Location insights
        if demographic_profile.location_confidence > 0.6:
            location_insights = self._generate_location_insights(demographic_profile)
            insights.extend(location_insights)
        
        # Interest-based insights
        if demographic_profile.interests:
            interest_insights = self._generate_interest_insights(demographic_profile)
            insights.extend(interest_insights)
        
        # Device preference insights
        device_insights = self._generate_device_insights(demographic_profile)
        insights.extend(device_insights)
        
        return insights

    def _generate_age_group_insights(self, profile: DemographicProfile) -> List[DemographicInsight]:
        """Generate age group specific insights"""
        
        insights = []
        age_group = profile.age_group
        
        if age_group == AgeGroup.GEN_Z:
            insights.append(DemographicInsight(
                insight_type="age_targeting",
                demographic_segment="gen_z",
                description="Gen Z audience prefers short-form, visual content with high entertainment value",
                confidence=0.9,
                market_size=1800000000,  # Estimated global Gen Z population
                engagement_potential=0.85,
                recommended_strategies=[
                    "Focus on TikTok and Instagram content",
                    "Use trending hashtags and challenges",
                    "Create mobile-first content",
                    "Emphasize authenticity and social causes"
                ],
                content_preferences={
                    "video": 0.8,
                    "short_form": 0.9,
                    "interactive": 0.7,
                    "trending": 0.85
                },
                optimal_timing={
                    "evening": 0.8,
                    "weekend": 0.7,
                    "late_night": 0.6
                },
                platform_recommendations=["tiktok", "instagram", "youtube_shorts", "snapchat"]
            ))
        
        elif age_group == AgeGroup.MILLENNIAL:
            insights.append(DemographicInsight(
                insight_type="age_targeting",
                demographic_segment="millennial",
                description="Millennials value quality content and brand authenticity",
                confidence=0.85,
                market_size=1800000000,
                engagement_potential=0.75,
                recommended_strategies=[
                    "Focus on Instagram and Facebook content",
                    "Emphasize brand values and sustainability",
                    "Create informative and educational content",
                    "Use influencer partnerships"
                ],
                content_preferences={
                    "educational": 0.8,
                    "brand_story": 0.75,
                    "lifestyle": 0.7,
                    "professional": 0.6
                },
                optimal_timing={
                    "lunch_time": 0.7,
                    "evening": 0.8,
                    "weekday": 0.6
                },
                platform_recommendations=["instagram", "facebook", "linkedin", "youtube"]
            ))
        
        return insights

    def _generate_location_insights(self, profile: DemographicProfile) -> List[DemographicInsight]:
        """Generate location-specific insights"""
        
        insights = []
        
        if profile.location_country:
            # Example for US market
            if profile.location_country.lower() == 'united states':
                insights.append(DemographicInsight(
                    insight_type="geographic_targeting",
                    demographic_segment="us_market",
                    description="US audience shows high engagement with premium content",
                    confidence=0.8,
                    market_size=330000000,
                    engagement_potential=0.9,
                    recommended_strategies=[
                        "Premium content positioning",
                        "English language optimization",
                        "US timezone scheduling",
                        "Local cultural references"
                    ],
                    content_preferences={
                        "premium": 0.8,
                        "english": 1.0,
                        "local_culture": 0.7
                    },
                    optimal_timing={
                        "us_prime_time": 0.9,
                        "us_business_hours": 0.6
                    },
                    platform_recommendations=["youtube", "instagram", "tiktok", "facebook"]
                ))
        
        return insights

    def _generate_interest_insights(self, profile: DemographicProfile) -> List[DemographicInsight]:
        """Generate interest-based insights"""
        
        insights = []
        
        if profile.interests:
            primary_interest = profile.interests[0]
            
            insights.append(DemographicInsight(
                insight_type="interest_targeting",
                demographic_segment=f"interest_{primary_interest.lower()}",
                description=f"Strong interest in {primary_interest} provides targeted content opportunity",
                confidence=0.8,
                market_size=50000000,  # Estimated based on interest
                engagement_potential=0.85,
                recommended_strategies=[
                    f"Create {primary_interest}-focused content",
                    "Partner with relevant influencers",
                    "Use interest-specific hashtags",
                    "Target similar interest groups"
                ],
                content_preferences={
                    primary_interest.lower(): 0.9,
                    "related_topics": 0.7
                },
                optimal_timing={
                    "interest_peak_hours": 0.8
                },
                platform_recommendations=["instagram", "youtube", "tiktok"]
            ))
        
        return insights

    def _generate_device_insights(self, profile: DemographicProfile) -> List[DemographicInsight]:
        """Generate device preference insights"""
        
        insights = []
        
        mobile_preference = profile.device_preferences.get(DeviceType.MOBILE_PRIMARY, 0)
        
        if mobile_preference > 0.7:
            insights.append(DemographicInsight(
                insight_type="device_optimization",
                demographic_segment="mobile_first",
                description="Strong mobile preference requires mobile-optimized content strategy",
                confidence=0.85,
                market_size=4500000000,  # Global mobile users
                engagement_potential=0.8,
                recommended_strategies=[
                    "Mobile-first content design",
                    "Vertical video format",
                    "Touch-optimized interactions",
                    "Fast loading content"
                ],
                content_preferences={
                    "mobile_optimized": 0.9,
                    "vertical_video": 0.85,
                    "short_form": 0.8
                },
                optimal_timing={
                    "mobile_peak_hours": 0.8,
                    "commute_times": 0.7
                },
                platform_recommendations=["tiktok", "instagram", "snapchat", "youtube_shorts"]
            ))
        
        return insights