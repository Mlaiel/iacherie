"""
Psychographic Analyzer - Advanced Personality and Lifestyle Analysis
==================================================================

Advanced AI-powered psychographic analysis for deep audience understanding.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PersonalityTraits(Enum):
    """Standard personality traits for psychographic analysis"""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"


class LifestyleSegments(Enum):
    """Lifestyle segmentation categories"""
    ACHIEVERS = "achievers"
    EXPERIENCERS = "experiencers"
    BELIEVERS = "believers"
    STRIVERS = "strivers"
    MAKERS = "makers"
    INNOVATORS = "innovators"
    THINKERS = "thinkers"
    SURVIVORS = "survivors"


@dataclass
class PsychographicProfile:
    """Comprehensive psychographic profile structure"""
    personality_traits: Dict[str, float]
    lifestyle_segment: str
    values: List[str]
    interests: List[str]
    attitudes: Dict[str, float]
    motivations: List[str]
    lifestyle_indicators: Dict[str, Any]
    confidence_score: float


class PsychographicAnalyzer:
    """
    Advanced Psychographic Analyzer
    ==============================
    
    Analyzes user behavior, content preferences, and interaction patterns
    to create comprehensive psychographic profiles for better targeting.
    """
    
    def __init__(self):
        """Initialize the Psychographic Analyzer"""
        self.personality_models = self._load_personality_models()
        self.lifestyle_classifiers = self._load_lifestyle_classifiers()
        self.values_detector = self._initialize_values_detector()
        
        logger.info("PsychographicAnalyzer initialized successfully")
    
    async def analyze_psychographics(
        self, 
        user_id: str, 
        behavioral_data: Dict[str, Any],
        content_preferences: Dict[str, Any],
        social_signals: Dict[str, Any]
    ) -> PsychographicProfile:
        """
        Perform comprehensive psychographic analysis
        
        Args:
            user_id: Unique user identifier
            behavioral_data: User behavior patterns
            content_preferences: Content interaction preferences
            social_signals: Social media behavior signals
            
        Returns:
            Comprehensive psychographic profile
        """
        try:
            logger.info(f"Starting psychographic analysis for user: {user_id}")
            
            # Analyze personality traits using Big Five model
            personality_traits = await self._analyze_personality_traits(
                behavioral_data, content_preferences, social_signals
            )
            
            # Determine lifestyle segment using VALS framework
            lifestyle_segment = await self._classify_lifestyle_segment(
                personality_traits, behavioral_data
            )
            
            # Extract core values and beliefs
            values = await self._extract_values(
                content_preferences, social_signals
            )
            
            # Identify interests and hobbies
            interests = await self._identify_interests(
                content_preferences, behavioral_data
            )
            
            # Analyze attitudes toward various topics
            attitudes = await self._analyze_attitudes(
                social_signals, content_preferences
            )
            
            # Determine motivational drivers
            motivations = await self._identify_motivations(
                personality_traits, lifestyle_segment
            )
            
            # Calculate lifestyle indicators
            lifestyle_indicators = await self._calculate_lifestyle_indicators(
                behavioral_data, content_preferences
            )
            
            # Calculate overall confidence score
            confidence_score = await self._calculate_confidence_score(
                personality_traits, lifestyle_segment, values
            )
            
            profile = PsychographicProfile(
                personality_traits=personality_traits,
                lifestyle_segment=lifestyle_segment,
                values=values,
                interests=interests,
                attitudes=attitudes,
                motivations=motivations,
                lifestyle_indicators=lifestyle_indicators,
                confidence_score=confidence_score
            )
            
            logger.info(f"Psychographic analysis completed for user: {user_id}")
            return profile
            
        except Exception as e:
            logger.error(f"Error in psychographic analysis: {str(e)}")
            raise
    
    async def _analyze_personality_traits(
        self, 
        behavioral_data: Dict[str, Any],
        content_preferences: Dict[str, Any],
        social_signals: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analyze Big Five personality traits"""
        
        # Simulate ML-based personality analysis
        await asyncio.sleep(0.01)  # Simulate processing time
        
        traits = {}
        
        # Openness to Experience
        traits[PersonalityTraits.OPENNESS.value] = self._calculate_openness(
            content_preferences, social_signals
        )
        
        # Conscientiousness
        traits[PersonalityTraits.CONSCIENTIOUSNESS.value] = self._calculate_conscientiousness(
            behavioral_data
        )
        
        # Extraversion
        traits[PersonalityTraits.EXTRAVERSION.value] = self._calculate_extraversion(
            social_signals, behavioral_data
        )
        
        # Agreeableness
        traits[PersonalityTraits.AGREEABLENESS.value] = self._calculate_agreeableness(
            social_signals
        )
        
        # Neuroticism
        traits[PersonalityTraits.NEUROTICISM.value] = self._calculate_neuroticism(
            behavioral_data, social_signals
        )
        
        return traits
    
    def _calculate_openness(
        self, 
        content_preferences: Dict[str, Any], 
        social_signals: Dict[str, Any]
    ) -> float:
        """Calculate openness to experience score"""
        score = 0.5  # Base score
        
        # Content diversity indicates openness
        content_types = content_preferences.get('content_types', [])
        if len(content_types) > 5:
            score += 0.2
        
        # New platform adoption
        platforms = social_signals.get('platforms', [])
        if 'tiktok' in platforms or 'clubhouse' in platforms:
            score += 0.15
        
        # Interest in trending topics
        if social_signals.get('trending_engagement', 0) > 0.7:
            score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_conscientiousness(self, behavioral_data: Dict[str, Any]) -> float:
        """Calculate conscientiousness score"""
        score = 0.5  # Base score
        
        # Consistent posting schedule
        posting_consistency = behavioral_data.get('posting_consistency', 0)
        score += posting_consistency * 0.3
        
        # Profile completeness
        profile_completeness = behavioral_data.get('profile_completeness', 0)
        score += profile_completeness * 0.2
        
        return min(score, 1.0)
    
    def _calculate_extraversion(
        self, 
        social_signals: Dict[str, Any], 
        behavioral_data: Dict[str, Any]
    ) -> float:
        """Calculate extraversion score"""
        score = 0.5  # Base score
        
        # Social interaction frequency
        interactions_per_day = social_signals.get('interactions_per_day', 0)
        if interactions_per_day > 20:
            score += 0.2
        elif interactions_per_day > 10:
            score += 0.1
        
        # Public content sharing
        if behavioral_data.get('public_sharing', False):
            score += 0.15
        
        # Group participation
        group_activity = social_signals.get('group_activity', 0)
        score += group_activity * 0.15
        
        return min(score, 1.0)
    
    def _calculate_agreeableness(self, social_signals: Dict[str, Any]) -> float:
        """Calculate agreeableness score"""
        score = 0.5  # Base score
        
        # Positive sentiment in interactions
        sentiment_score = social_signals.get('sentiment_score', 0)
        score += sentiment_score * 0.25
        
        # Supportive behavior
        supportive_actions = social_signals.get('supportive_actions', 0)
        score += supportive_actions * 0.2
        
        return min(score, 1.0)
    
    def _calculate_neuroticism(
        self, 
        behavioral_data: Dict[str, Any], 
        social_signals: Dict[str, Any]
    ) -> float:
        """Calculate neuroticism score (reversed)"""
        score = 0.5  # Base score
        
        # Emotional stability indicators
        emotional_variance = behavioral_data.get('emotional_variance', 0.5)
        score -= emotional_variance * 0.3
        
        # Stress indicators in content
        stress_indicators = social_signals.get('stress_indicators', 0)
        score -= stress_indicators * 0.2
        
        return max(score, 0.0)
    
    async def _classify_lifestyle_segment(
        self, 
        personality_traits: Dict[str, float], 
        behavioral_data: Dict[str, Any]
    ) -> str:
        """Classify user into VALS lifestyle segment"""
        await asyncio.sleep(0.01)  # Simulate ML classification
        
        # Simplified classification logic based on traits and behavior
        openness = personality_traits.get('openness', 0.5)
        conscientiousness = personality_traits.get('conscientiousness', 0.5)
        extraversion = personality_traits.get('extraversion', 0.5)
        
        income_indicators = behavioral_data.get('income_indicators', 0.5)
        innovation_adoption = behavioral_data.get('innovation_adoption', 0.5)
        
        # Classification logic
        if openness > 0.7 and income_indicators > 0.7:
            return LifestyleSegments.INNOVATORS.value
        elif openness > 0.6 and extraversion > 0.6:
            return LifestyleSegments.EXPERIENCERS.value
        elif conscientiousness > 0.7 and income_indicators > 0.6:
            return LifestyleSegments.ACHIEVERS.value
        elif conscientiousness > 0.6:
            return LifestyleSegments.THINKERS.value
        elif extraversion > 0.6:
            return LifestyleSegments.STRIVERS.value
        elif innovation_adoption < 0.4:
            return LifestyleSegments.BELIEVERS.value
        elif behavioral_data.get('hands_on_activities', False):
            return LifestyleSegments.MAKERS.value
        else:
            return LifestyleSegments.SURVIVORS.value
    
    async def _extract_values(
        self, 
        content_preferences: Dict[str, Any], 
        social_signals: Dict[str, Any]
    ) -> List[str]:
        """Extract core values from user behavior"""
        await asyncio.sleep(0.01)
        
        values = []
        
        # Analyze content topics for value indicators
        topics = content_preferences.get('topics', [])
        
        if 'sustainability' in topics or 'environment' in topics:
            values.append('environmental_consciousness')
        
        if 'family' in topics or 'parenting' in topics:
            values.append('family_values')
        
        if 'career' in topics or 'entrepreneurship' in topics:
            values.append('achievement')
        
        if 'travel' in topics or 'culture' in topics:
            values.append('adventure')
        
        if 'charity' in topics or 'volunteer' in topics:
            values.append('benevolence')
        
        # Social behavior indicators
        if social_signals.get('charitable_engagement', 0) > 0.5:
            values.append('altruism')
        
        if social_signals.get('political_engagement', 0) > 0.5:
            values.append('civic_duty')
        
        return list(set(values))  # Remove duplicates
    
    async def _identify_interests(
        self, 
        content_preferences: Dict[str, Any], 
        behavioral_data: Dict[str, Any]
    ) -> List[str]:
        """Identify user interests from behavior patterns"""
        await asyncio.sleep(0.01)
        
        interests = []
        
        # Extract from content preferences
        topics = content_preferences.get('topics', [])
        interests.extend(topics)
        
        # Extract from behavioral patterns
        activity_types = behavioral_data.get('activity_types', [])
        interests.extend(activity_types)
        
        # Extract from purchase behavior if available
        purchase_categories = behavioral_data.get('purchase_categories', [])
        interests.extend(purchase_categories)
        
        return list(set(interests))  # Remove duplicates
    
    async def _analyze_attitudes(
        self, 
        social_signals: Dict[str, Any], 
        content_preferences: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analyze attitudes toward various topics"""
        await asyncio.sleep(0.01)
        
        attitudes = {}
        
        # Technology attitude
        tech_engagement = content_preferences.get('tech_content_engagement', 0.5)
        attitudes['technology'] = tech_engagement
        
        # Brand attitude
        brand_loyalty = social_signals.get('brand_loyalty_score', 0.5)
        attitudes['brands'] = brand_loyalty
        
        # Social causes attitude
        social_cause_engagement = social_signals.get('social_cause_engagement', 0.5)
        attitudes['social_causes'] = social_cause_engagement
        
        # Innovation attitude
        innovation_adoption = social_signals.get('early_adoption_score', 0.5)
        attitudes['innovation'] = innovation_adoption
        
        return attitudes
    
    async def _identify_motivations(
        self, 
        personality_traits: Dict[str, float], 
        lifestyle_segment: str
    ) -> List[str]:
        """Identify key motivational drivers"""
        await asyncio.sleep(0.01)
        
        motivations = []
        
        # Based on personality traits
        if personality_traits.get('openness', 0) > 0.7:
            motivations.append('novelty_seeking')
        
        if personality_traits.get('conscientiousness', 0) > 0.7:
            motivations.append('achievement')
        
        if personality_traits.get('extraversion', 0) > 0.7:
            motivations.append('social_recognition')
        
        # Based on lifestyle segment
        segment_motivations = {
            LifestyleSegments.INNOVATORS.value: ['innovation', 'self_expression'],
            LifestyleSegments.ACHIEVERS.value: ['success', 'status'],
            LifestyleSegments.EXPERIENCERS.value: ['excitement', 'adventure'],
            LifestyleSegments.BELIEVERS.value: ['tradition', 'community'],
            LifestyleSegments.STRIVERS.value: ['approval', 'belonging'],
            LifestyleSegments.MAKERS.value: ['self_sufficiency', 'practicality'],
            LifestyleSegments.THINKERS.value: ['knowledge', 'understanding'],
            LifestyleSegments.SURVIVORS.value: ['security', 'stability']
        }
        
        motivations.extend(segment_motivations.get(lifestyle_segment, []))
        
        return list(set(motivations))
    
    async def _calculate_lifestyle_indicators(
        self, 
        behavioral_data: Dict[str, Any], 
        content_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate various lifestyle indicators"""
        await asyncio.sleep(0.01)
        
        indicators = {}
        
        # Digital lifestyle indicators
        indicators['digital_native_score'] = behavioral_data.get('platform_adoption_speed', 0.5)
        indicators['content_creation_activity'] = behavioral_data.get('content_creation_frequency', 0)
        
        # Consumption patterns
        indicators['luxury_affinity'] = content_preferences.get('luxury_content_engagement', 0)
        indicators['budget_consciousness'] = behavioral_data.get('price_sensitivity', 0.5)
        
        # Social lifestyle indicators
        indicators['social_influence_score'] = behavioral_data.get('follower_count_normalized', 0)
        indicators['community_involvement'] = behavioral_data.get('group_participation', 0)
        
        # Health and wellness
        indicators['wellness_focus'] = content_preferences.get('health_content_engagement', 0)
        
        return indicators
    
    async def _calculate_confidence_score(
        self, 
        personality_traits: Dict[str, float], 
        lifestyle_segment: str, 
        values: List[str]
    ) -> float:
        """Calculate overall confidence score for the psychographic profile"""
        await asyncio.sleep(0.01)
        
        # Base confidence
        confidence = 0.7
        
        # Adjust based on data completeness
        trait_completeness = len(personality_traits) / 5  # 5 Big Five traits
        confidence *= trait_completeness
        
        # Adjust based on lifestyle classification confidence
        if lifestyle_segment != LifestyleSegments.SURVIVORS.value:  # Default fallback
            confidence += 0.1
        
        # Adjust based on values identification
        if len(values) > 2:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _load_personality_models(self) -> Dict[str, Any]:
        """Load pre-trained personality analysis models"""
        # In a real implementation, this would load actual ML models
        return {
            'big_five_classifier': 'mock_model',
            'trait_extractors': 'mock_extractors'
        }
    
    def _load_lifestyle_classifiers(self) -> Dict[str, Any]:
        """Load lifestyle classification models"""
        # In a real implementation, this would load actual ML models
        return {
            'vals_classifier': 'mock_vals_model',
            'lifestyle_predictors': 'mock_predictors'
        }
    
    def _initialize_values_detector(self) -> Dict[str, Any]:
        """Initialize values detection system"""
        # In a real implementation, this would initialize NLP models
        return {
            'values_nlp_model': 'mock_nlp_model',
            'sentiment_analyzer': 'mock_sentiment_model'
        }


# Utility functions for psychographic analysis
async def batch_psychographic_analysis(
    analyzer: PsychographicAnalyzer,
    user_data_batch: List[Dict[str, Any]]
) -> List[PsychographicProfile]:
    """Process multiple users for psychographic analysis"""
    tasks = []
    
    for user_data in user_data_batch:
        task = analyzer.analyze_psychographics(
            user_data['user_id'],
            user_data['behavioral_data'],
            user_data['content_preferences'],
            user_data['social_signals']
        )
        tasks.append(task)
    
    return await asyncio.gather(*tasks)


def get_personality_insights(profile: PsychographicProfile) -> Dict[str, str]:
    """Generate human-readable personality insights"""
    insights = {}
    
    traits = profile.personality_traits
    
    # Openness insights
    if traits.get('openness', 0) > 0.7:
        insights['creativity'] = "Highly creative and open to new experiences"
    elif traits.get('openness', 0) > 0.5:
        insights['creativity'] = "Moderately open to new ideas and experiences"
    else:
        insights['creativity'] = "Prefers familiar and traditional approaches"
    
    # Conscientiousness insights
    if traits.get('conscientiousness', 0) > 0.7:
        insights['organization'] = "Highly organized and goal-oriented"
    elif traits.get('conscientiousness', 0) > 0.5:
        insights['organization'] = "Moderately organized with some structure"
    else:
        insights['organization'] = "Flexible and spontaneous approach"
    
    # Extraversion insights
    if traits.get('extraversion', 0) > 0.7:
        insights['social'] = "Highly social and outgoing"
    elif traits.get('extraversion', 0) > 0.5:
        insights['social'] = "Moderately social with balanced social needs"
    else:
        insights['social'] = "Prefers smaller groups and quieter environments"
    
    return insights