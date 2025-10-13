"""
Cultural Adaptation Module for iaCherie Platform
=====================================

This module provides cultural adaptation capabilities for content 
and user interfaces to ensure cultural sensitivity and 
local market optimization.

Author: iaCherie Team
Version: 1.0.0
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class CulturalDimension(Enum):
    """
Cultural dimensions for adaptation"""
    POWER_DISTANCE = "power_distance"
    INDIVIDUALISM = "individualism"
    MASCULINITY = "masculinity"
    UNCERTAINTY_AVOIDANCE = "uncertainty_avoidance"
    LONG_TERM_ORIENTATION = "long_term_orientation"
    INDULGENCE = "indulgence"

class CommunicationStyle(Enum):
    """
Communication style preferences"""
    DIRECT = "direct"
    INDIRECT = "indirect"
    HIGH_CONTEXT = "high_context"
    LOW_CONTEXT = "low_context"

@dataclass
class CulturalProfile:
    """
Cultural profile for a region/country"""
    country_code: str
    region: str
    power_distance: float  # 0-100
    individualism: float   # 0-100
    masculinity: float     # 0-100
    uncertainty_avoidance: float  # 0-100
    long_term_orientation: float  # 0-100
    indulgence: float      # 0-100
    communication_style: CommunicationStyle
    color_preferences: List[str]
    visual_preferences: Dict[str, Any]
    taboos: List[str]
    preferred_content_types: List[str]
    business_etiquette: Dict[str, str]

@dataclass
class CulturalAdaptation:
    """
Cultural adaptation for content"""
    original_content: str
    adapted_content: str
    cultural_considerations: List[str]
    adaptation_level: float  # 0-1
    confidence_score: float  # 0-1
    
class CulturalAdaptationEngine:
    """
    Advanced Cultural Adaptation Engine for iaCherie Platform
    
    Provides cultural adaptation capabilities for content, UI, and user experience
    to ensure cultural sensitivity and local market optimization.
    """
    
    def __init__(self):
        """
Initialize Cultural Adaptation Engine"""
        self.cultural_profiles = self._initialize_cultural_profiles()
        self.adaptation_rules = self._initialize_adaptation_rules()
        self.color_mappings = self._initialize_color_mappings()
        self.content_filters = self._initialize_content_filters()
        
        logger.info("🌍 Cultural Adaptation Engine initialized")
        logger.info(f"📊 Loaded {len(self.cultural_profiles)} cultural profiles")
        logger.info(f"📋 Configured {len(self.adaptation_rules)} adaptation rules")
    
    def _initialize_cultural_profiles(self) -> Dict[str, CulturalProfile]:
        """
Initialize cultural profiles for different countries/regions"""
        profiles = {}
        
        # Western cultures
        profiles['US'] = CulturalProfile(
            country_code='US', region='North America',
            power_distance=40, individualism=91, masculinity=62,
            uncertainty_avoidance=46, long_term_orientation=26, indulgence=68,
            communication_style=CommunicationStyle.DIRECT,
            color_preferences=['blue', 'white', 'red'],
            visual_preferences={'layout': 'left_to_right', 'imagery': 'diverse', 'text_density': 'medium'},
            taboos=['political_extremes', 'religious_criticism'],
            preferred_content_types=['video', 'interactive', 'personalized'],
            business_etiquette={'greeting': 'handshake', 'punctuality': 'important', 'hierarchy': 'flexible'}
        )
        
        profiles['GB'] = CulturalProfile(
            country_code='GB', region='Europe',
            power_distance=35, individualism=89, masculinity=66,
            uncertainty_avoidance=35, long_term_orientation=51, indulgence=69,
            communication_style=CommunicationStyle.INDIRECT,
            color_preferences=['navy', 'green', 'gold'],
            visual_preferences={'layout': 'formal', 'imagery': 'traditional', 'text_density': 'high'},
            taboos=['personal_income', 'age_questions', 'brexit_politics'],
            preferred_content_types=['text', 'formal_video', 'educational'],
            business_etiquette={'greeting': 'formal_handshake', 'punctuality': 'critical', 'hierarchy': 'respected'}
        )
        
        # Asian cultures
        profiles['JP'] = CulturalProfile(
            country_code='JP', region='East Asia',
            power_distance=54, individualism=46, masculinity=95,
            uncertainty_avoidance=92, long_term_orientation=88, indulgence=42,
            communication_style=CommunicationStyle.HIGH_CONTEXT,
            color_preferences=['white', 'red', 'black'],
            visual_preferences={'layout': 'minimalist', 'imagery': 'harmonious', 'text_density': 'low'},
            taboos=['direct_confrontation', 'personal_failure_mention', 'shoes_indoors'],
            preferred_content_types=['visual', 'respectful', 'group_focused'],
            business_etiquette={'greeting': 'bow', 'punctuality': 'extremely_important', 'hierarchy': 'strict'}
        )
        
        profiles['CN'] = CulturalProfile(
            country_code='CN', region='East Asia',
            power_distance=80, individualism=20, masculinity=66,
            uncertainty_avoidance=30, long_term_orientation=87, indulgence=24,
            communication_style=CommunicationStyle.HIGH_CONTEXT,
            color_preferences=['red', 'gold', 'yellow'],
            visual_preferences={'layout': 'dense', 'imagery': 'prosperous', 'text_density': 'high'},
            taboos=['political_topics', 'taiwan_independence', 'death_numbers'],
            preferred_content_types=['group_achievements', 'educational', 'family_oriented'],
            business_etiquette={'greeting': 'slight_bow', 'punctuality': 'important', 'hierarchy': 'very_strict'}
        )
        
        # Middle Eastern cultures
        profiles['AE'] = CulturalProfile(
            country_code='AE', region='Middle East',
            power_distance=90, individualism=25, masculinity=50,
            uncertainty_avoidance=68, long_term_orientation=14, indulgence=34,
            communication_style=CommunicationStyle.HIGH_CONTEXT,
            color_preferences=['gold', 'green', 'white'],
            visual_preferences={'layout': 'right_to_left', 'imagery': 'respectful', 'text_density': 'medium'},
            taboos=['alcohol_promotion', 'inappropriate_dress', 'religious_criticism'],
            preferred_content_types=['family_values', 'respectful', 'traditional'],
            business_etiquette={'greeting': 'same_gender_only', 'punctuality': 'flexible', 'hierarchy': 'respected'}
        )
        
        # Latin American cultures
        profiles['BR'] = CulturalProfile(
            country_code='BR', region='South America',
            power_distance=69, individualism=38, masculinity=49,
            uncertainty_avoidance=76, long_term_orientation=44, indulgence=59,
            communication_style=CommunicationStyle.HIGH_CONTEXT,
            color_preferences=['green', 'yellow', 'blue'],
            visual_preferences={'layout': 'vibrant', 'imagery': 'colorful', 'text_density': 'medium'},
            taboos=['argentina_rivalry', 'poverty_mockery', 'political_corruption'],
            preferred_content_types=['social', 'family_oriented', 'festive'],
            business_etiquette={'greeting': 'warm_handshake', 'punctuality': 'flexible', 'hierarchy': 'moderate'}
        )
        
        return profiles
    
    def _initialize_adaptation_rules(self) -> Dict[str, Dict[str, Any]]:
        """
Initialize cultural adaptation rules"""
        return {
            'high_power_distance': {
                'ui_hierarchy': 'emphasized',
                'authority_language': 'formal',
                'decision_makers': 'highlighted',
                'submission_process': 'hierarchical'
            },
            'low_power_distance': {
                'ui_hierarchy': 'flat',
                'authority_language': 'casual',
                'decision_makers': 'collaborative',
                'submission_process': 'direct'
            },
            'high_individualism': {
                'personalization': 'high',
                'achievement_focus': 'individual',
                'privacy_settings': 'granular',
                'content_curation': 'personal'
            },
            'high_collectivism': {
                'personalization': 'group_based',
                'achievement_focus': 'team',
                'privacy_settings': 'shared',
                'content_curation': 'community'
            },
            'high_uncertainty_avoidance': {
                'information_detail': 'comprehensive',
                'security_badges': 'prominent',
                'guarantee_emphasis': 'strong',
                'change_communication': 'detailed'
            },
            'low_uncertainty_avoidance': {
                'information_detail': 'concise',
                'security_badges': 'minimal',
                'guarantee_emphasis': 'light',
                'change_communication': 'brief'
            }
        }
    
    def _initialize_color_mappings(self) -> Dict[str, Dict[str, str]]:
        """
Initialize cultural color mappings"""
        return {
            'CN': {
                'prosperity': 'red',
                'luck': 'gold',
                'mourning': 'white',
                'avoid': 'green_hats'
            },
            'IN': {
                'purity': 'white',
                'prosperity': 'yellow',
                'mourning': 'white',
                'avoid': 'leather_imagery'
            },
            'AE': {
                'luxury': 'gold',
                'nature': 'green',
                'purity': 'white',
                'avoid': 'revealing_imagery'
            },
            'JP': {
                'purity': 'white',
                'energy': 'red',
                'mourning': 'black',
                'avoid': 'four_items'
            }
        }
    
    def _initialize_content_filters(self) -> Dict[str, List[str]]:
        """
Initialize cultural content filters"""
        return {
            'religious_sensitivity': [
                'religious_imagery_check',
                'sacred_symbol_review',
                'dietary_restriction_awareness',
                'prayer_time_consideration'
            ],
            'cultural_taboos': [
                'political_neutrality',
                'historical_sensitivity',
                'social_norm_compliance',
                'gender_role_awareness'
            ],
            'visual_appropriateness': [
                'dress_code_compliance',
                'gesture_appropriateness',
                'color_symbolism_check',
                'imagery_cultural_fit'
            ],
            'linguistic_adaptation': [
                'formal_vs_informal',
                'direct_vs_indirect',
                'honorific_usage',
                'local_expressions'
            ]
        }
    
    def adapt_content(self, content: str, target_culture: str, 
                     adaptation_level: str = "moderate") -> CulturalAdaptation:
        """
        Adapt content for specific cultural context
        
        Args:
            content: Original content to adapt
            target_culture: Target culture code (e.g., 'JP', 'CN', 'AE')
            adaptation_level: Level of adaptation ('light', 'moderate', 'deep')
            
        Returns:
            CulturalAdaptation object with adapted content
        """
        if target_culture not in self.cultural_profiles:
            logger.warning(f"🚨 Cultural profile not found for: {target_culture}")
            return CulturalAdaptation(
                original_content=content,
                adapted_content=content,
                cultural_considerations=["No cultural profile available"],
                adaptation_level=0.0,
                confidence_score=0.0
            )
        
        profile = self.cultural_profiles[target_culture]
        adapted_content = content
        considerations = []
        
        # Apply cultural adaptations based on profile
        if profile.communication_style == CommunicationStyle.HIGH_CONTEXT:
            adapted_content = self._adapt_for_high_context(adapted_content, profile)
            considerations.append("Adapted for high-context communication")
        
        if profile.power_distance > 70:
            adapted_content = self._adapt_for_high_power_distance(adapted_content, profile)
            considerations.append("Adapted for high power distance culture")
        
        if profile.uncertainty_avoidance > 70:
            adapted_content = self._adapt_for_uncertainty_avoidance(adapted_content, profile)
            considerations.append("Added certainty and security elements")
        
        # Apply taboo filtering
        adapted_content = self._filter_taboos(adapted_content, profile.taboos)
        considerations.append("Filtered culturally sensitive content")
        
        # Calculate adaptation metrics
        adaptation_score = self._calculate_adaptation_level(content, adapted_content, adaptation_level)
        confidence_score = self._calculate_confidence_score(profile, adaptation_level)
        
        logger.info(f"🌍 Content adapted for {target_culture} culture")
        logger.info(f"📊 Adaptation level: {adaptation_score:.2f}")
        logger.info(f"🎯 Confidence score: {confidence_score:.2f}")
        
        return CulturalAdaptation(
            original_content=content,
            adapted_content=adapted_content,
            cultural_considerations=considerations,
            adaptation_level=adaptation_score,
            confidence_score=confidence_score
        )
    
    def _adapt_for_high_context(self, content: str, profile: CulturalProfile) -> str:
        """
Adapt content for high-context cultures"""
        # Add more context and indirect communication
        if "you should" in content.lower():
            content = content.replace("you should", "it might be beneficial to consider")
        
        if "buy now" in content.lower():
            content = content.replace("buy now", "when you feel ready, you may wish to")
        
        return content
    
    def _adapt_for_high_power_distance(self, content: str, profile: CulturalProfile) -> str:
        """
Adapt content for high power distance cultures"""
        # Add more formal language and hierarchy respect
        if "we recommend" in content.lower():
            content = content.replace("we recommend", "our experts respectfully suggest")
        
        if "team" in content.lower():
            content = content.replace("team", "esteemed colleagues")
        
        return content
    
    def _adapt_for_uncertainty_avoidance(self, content: str, profile: CulturalProfile) -> str:
        """
Adapt content for uncertainty avoidance cultures"""
        # Add more details and security assurances
        if "easy" in content.lower():
            content = content.replace("easy", "thoroughly tested and reliable")
        
        if "quick" in content.lower():
            content = content.replace("quick", "efficient and secure")
        
        return content
    
    def _filter_taboos(self, content: str, taboos: List[str]) -> str:
        """
Filter content based on cultural taboos"""
        filtered_content = content
        
        for taboo in taboos:
            if taboo in ['political_topics', 'political_extremes']:
                # Remove political references
                political_terms = ['election', 'government', 'politics', 'political']
                for term in political_terms:
                    if term in filtered_content.lower():
                        filtered_content = filtered_content.replace(term, "social")
        
        return filtered_content
    
    def _calculate_adaptation_level(self, original: str, adapted: str, level: str) -> float:
        """
Calculate adaptation level score"""
        if original == adapted:
            return 0.0
        
        level_multipliers = {
            'light': 0.3,
            'moderate': 0.6,
            'deep': 0.9
        }
        
        change_ratio = 1 - (len(set(original.split()) & set(adapted.split())) / len(set(original.split())))
        return min(change_ratio * level_multipliers.get(level, 0.6), 1.0)
    
    def _calculate_confidence_score(self, profile: CulturalProfile, level: str) -> float:
        """
Calculate confidence score for adaptation"""
        base_confidence = 0.8
        
        # Higher confidence for well-defined profiles
        if len(profile.taboos) > 3:
            base_confidence += 0.1
        
        if profile.communication_style in [CommunicationStyle.HIGH_CONTEXT, CommunicationStyle.LOW_CONTEXT]:
            base_confidence += 0.05
        
        level_confidence = {
            'light': 0.9,
            'moderate': 0.8,
            'deep': 0.7
        }
        
        return min(base_confidence * level_confidence.get(level, 0.8), 1.0)
    
    def get_cultural_recommendations(self, target_culture: str) -> Dict[str, Any]:
        """
Get cultural recommendations for specific culture"""
        if target_culture not in self.cultural_profiles:
            return {}
        
        profile = self.cultural_profiles[target_culture]
        
        return {
            'color_scheme': profile.color_preferences,
            'communication_style': profile.communication_style.value,
            'visual_preferences': profile.visual_preferences,
            'content_guidelines': {
                'avoid': profile.taboos,
                'prefer': profile.preferred_content_types
            },
            'business_etiquette': profile.business_etiquette,
            'cultural_dimensions': {
                'power_distance': profile.power_distance,
                'individualism': profile.individualism,
                'uncertainty_avoidance': profile.uncertainty_avoidance
            }
        }
    
    def validate_cultural_appropriateness(self, content: str, 
                                        target_culture: str) -> Dict[str, Any]:
        """
Validate content for cultural appropriateness"""
        if target_culture not in self.cultural_profiles:
            return {'valid': True, 'warnings': [], 'suggestions': []}
        
        profile = self.cultural_profiles[target_culture]
        warnings = []
        suggestions = []
        
        # Check for taboos
        for taboo in profile.taboos:
            if self._contains_taboo_reference(content, taboo):
                warnings.append(f"Content may contain culturally sensitive reference: {taboo}")
                suggestions.append(f"Consider removing or adapting references to {taboo}")
        
        # Check communication style appropriateness
        if profile.communication_style == CommunicationStyle.HIGH_CONTEXT:
            if self._is_too_direct(content):
                warnings.append("Content may be too direct for high-context culture")
                suggestions.append("Consider using more indirect language")
        
        # Check for cultural color considerations
        if target_culture in self.color_mappings:
            color_issues = self._check_color_appropriateness(content, target_culture)
            warnings.extend(color_issues)
        
        is_valid = len(warnings) == 0
        
        logger.info(f"🔍 Cultural validation for {target_culture}: {'✅ Valid' if is_valid else '⚠️ Issues found'}")
        
        return {
            'valid': is_valid,
            'warnings': warnings,
            'suggestions': suggestions,
            'cultural_profile': profile.country_code
        }
    
    def _contains_taboo_reference(self, content: str, taboo: str) -> bool:
        """
Check if content contains taboo references"""
        taboo_keywords = {
            'political_topics': ['election', 'government', 'politics', 'vote'],
            'religious_criticism': ['religion', 'god', 'faith', 'belief'],
            'personal_income': ['salary', 'income', 'wage', 'money'],
            'death_numbers': ['4', 'four', 'death', 'die']
        }
        
        keywords = taboo_keywords.get(taboo, [taboo])
        return any(keyword in content.lower() for keyword in keywords)
    
    def _is_too_direct(self, content: str) -> bool:
        """
Check if content is too direct for high-context cultures"""
        direct_phrases = ['you must', 'you should', 'buy now', 'act fast', 'limited time']
        return any(phrase in content.lower() for phrase in direct_phrases)
    
    def _check_color_appropriateness(self, content: str, culture: str) -> List[str]:
        """
Check color appropriateness for specific culture"""
        warnings = []
        color_rules = self.color_mappings.get(culture, {})
        
        if 'avoid' in color_rules:
            avoid_items = color_rules['avoid']
            if isinstance(avoid_items, str):
                if avoid_items in content.lower():
                    warnings.append(f"Content contains culturally inappropriate element: {avoid_items}")
        
        return warnings

# Create global instance
cultural_adapter = CulturalAdaptationEngine()

# Create alias for backward compatibility with authentication modules
CulturalAdapter = CulturalAdaptationEngine

# Export main classes and functions
__all__ = [
    'CulturalAdaptationEngine',
    'CulturalAdapter',  # Alias for authentication modules
    'CulturalProfile', 
    'CulturalAdaptation',
    'CulturalDimension',
    'CommunicationStyle',
    'cultural_adapter'
]

# Log module initialization
logger.info("🌍 Cultural Adaptation module initialized successfully")
logger.info("✅ Ready for multicultural content adaptation and validation")