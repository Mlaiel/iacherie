"""Cultural Keyword Adaptation Engine - Ainflue Platform
================================================================================
Module: core/i18n/cultural_keyword_adapter.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Cultural Keyword Optimization Engine - SEO Cultural Adaptation
Responsibility: Cultural adaptation of keywords for regional SEO optimization
Technologies: Python, Cultural AI, SEO Analysis, Regional Marketing
================================================================================

⚠️  PROPRIETARY SOFTWARE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

BUSINESS LOGIC:
Keyword analysis → Cultural context detection → Regional preferences → 
Local terminology mapping → Cultural sensitivity check → Adapted keywords
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import re

from .cultural_localization import CulturalLocalization, CulturalContext
from .regional_compliance import RegionalCompliance

logger = logging.getLogger(__name__)


class KeywordAdaptationType(Enum):
    """
Types of keyword adaptations"""

    CULTURAL_TRANSLATION = "cultural_translation"
    LOCAL_TERMINOLOGY = "local_terminology"
    CULTURAL_SENSITIVITY = "cultural_sensitivity"
    REGIONAL_PREFERENCE = "regional_preference"
    PLATFORM_OPTIMIZATION = "platform_optimization"


@dataclass
class CulturalKeywordResult:
    """Result of cultural keyword adaptation"""
    original_keyword: str
    adapted_keywords: List[str]
    cultural_context: str
    adaptation_type: KeywordAdaptationType
    confidence_score: float
    cultural_notes: List[str]
    local_variations: Dict[str, str]
    search_volume_estimates: Dict[str, int]
    regional_popularity: Dict[str, float]
    cultural_sensitivity_flags: List[str]
    recommended_usage: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegionalKeywordPreferences:
    """
Regional keyword preferences and patterns"""
    region: str
    preferred_terms: Dict[str, List[str]]
    avoided_terms: List[str]
    cultural_modifiers: List[str]
    local_slang: Dict[str, str]
    formal_vs_informal: str
    trending_keywords: List[str]
    seasonal_keywords: Dict[str, List[str]]


class CulturalKeywordAdapter:
    """
Advanced cultural keyword adaptation engine"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.cultural_localization = CulturalLocalization()
        self.regional_compliance = RegionalCompliance()
        self.logger = logging.getLogger(__name__)
        
        # Cultural keyword mappings
        self.cultural_mappings = {
            "AR": {  # Arabic
                "business": ["أعمال", "تجارة", "شركة"],
                "technology": ["تكنولوجيا", "تقنية", "تكنولوجيا حديثة"],
                "family": ["عائلة", "أسرة", "عشيرة"],
                "food": ["طعام", "أكل", "مأكولات"],
                "fashion": ["أزياء", "موضة", "أناقة"]
            },
            "HE": {  # Hebrew
                "business": ["עסק", "עסקים", "חברה"],
                "technology": ["טכנולוgiה", "טכנולוגיה", "היטק"],
                "family": ["משפחה", "בית", "משפחת"],
                "food": ["אוכל", "מזון", "מאכלים"],
                "fashion": ["אופנה", "סטייל", "לבוש"]
            },
            "AMAZIGH": {  # Amazigh/Berber
                "business": ["tamdint", "adlis", "tamurt"],
                "technology": ["tatiknulujit", "tiknulujit", "taqniyin"],
                "family": ["tawacult", "ahl", "agraw"],
                "food": ["akal", "tucca", "azaay"],
                "fashion": ["alkisu", "aselway", "tikkelt"]
            }
        }
        
        # Regional preferences
        self.regional_preferences = {
            "MENA": {  # Middle East & North Africa
                "formal_tone": True,
                "religious_sensitivity": True,
                "family_oriented": True,
                "respect_hierarchy": True
            },
            "NA": {  # North Africa (Maghreb)
                "multilingual": True,
                "french_influence": True,
                "arabic_script": True,
                "amazigh_support": True
            },
            "GCC": {  # Gulf Cooperation Council
                "luxury_preference": True,
                "traditional_values": True,
                "english_business": True,
                "conservative_approach": True
            }
        }
        
        # Platform-specific preferences by region
        self.platform_preferences = {
            "MENA": {
                "instagram": {"hashtag_style": "arabic_english_mix", "content_type": "visual_heavy"},
                "tiktok": {"trending_sounds": "arabic_music", "content_style": "family_friendly"},
                "youtube": {"title_language": "arabic_primary", "description": "bilingual"},
                "twitter": {"hashtag_limit": 3, "language_mix": "ar_en"}
            },
            "NA": {
                "instagram": {"hashtag_style": "trilingual", "content_type": "lifestyle"},
                "tiktok": {"trending_sounds": "amazigh_arabic", "content_style": "cultural_mix"},
                "youtube": {"title_language": "local_dialect", "description": "multilingual"},
                "twitter": {"hashtag_limit": 5, "language_mix": "ar_fr_ber"}
            }
        }

    async def adapt_keywords_culturally(
        self,
        keywords: List[str],
        source_culture: str,
        target_culture: str,
        platform: str = None,
        region: str = None
    ) -> List[CulturalKeywordResult]:
        """
        Adapt keywords for cultural context
        
        Args:
            keywords: List of original keywords
            source_culture: Source cultural context
            target_culture: Target cultural context
            platform: Target platform (optional)
            region: Target region (optional)
            
        Returns:
            List of culturally adapted keyword results
        """
        try:
            results = []
            
            # Get cultural context
            target_context = await self.cultural_localization.get_cultural_context(target_culture)
            
            for keyword in keywords:
                adapted_result = await self._adapt_single_keyword(
                    keyword, source_culture, target_culture, target_context, platform, region
                )
                results.append(adapted_result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in cultural keyword adaptation: {e}")
            raise

    async def _adapt_single_keyword(
        self,
        keyword: str,
        source_culture: str,
        target_culture: str,
        target_context: CulturalContext,
        platform: str = None,
        region: str = None
    ) -> CulturalKeywordResult:
        """Adapt a single keyword culturally"""
        
        # Analyze keyword for cultural context
        cultural_analysis = await self._analyze_keyword_cultural_context(keyword, target_culture)
        
        # Generate cultural adaptations
        adapted_keywords = await self._generate_cultural_adaptations(
            keyword, target_culture, target_context, platform, region
        )
        
        # Check cultural sensitivity
        sensitivity_flags = await self._check_cultural_sensitivity(
            keyword, adapted_keywords, target_culture
        )
        
        # Estimate search volumes and popularity
        search_estimates = await self._estimate_search_volumes(adapted_keywords, target_culture)
        regional_popularity = await self._estimate_regional_popularity(adapted_keywords, region)
        
        return CulturalKeywordResult(
            original_keyword=keyword,
            adapted_keywords=adapted_keywords,
            cultural_context=target_culture,
            adaptation_type=cultural_analysis.get('adaptation_type', KeywordAdaptationType.CULTURAL_TRANSLATION),
            confidence_score=cultural_analysis.get('confidence', 0.8),
            cultural_notes=cultural_analysis.get('notes', []),
            local_variations=cultural_analysis.get('variations', {}),
            search_volume_estimates=search_estimates,
            regional_popularity=regional_popularity,
            cultural_sensitivity_flags=sensitivity_flags,
            recommended_usage=self._generate_usage_recommendations(keyword, target_culture, platform)
        )

    async def _analyze_keyword_cultural_context(
        self, keyword: str, target_culture: str
    ) -> Dict[str, Any]:
        """
Analyze keyword for cultural context"""
        
        analysis = {
            'adaptation_type': KeywordAdaptationType.CULTURAL_TRANSLATION,
            'confidence': 0.8,
            'notes': [],
            'variations': {}
        }
        
        # Check if keyword exists in cultural mappings
        culture_key = target_culture.upper()
        if culture_key in self.cultural_mappings:
            mapping = self.cultural_mappings[culture_key]
            for category, terms in mapping.items():
                if keyword.lower() in category or any(term in keyword.lower() for term in terms):
                    analysis['adaptation_type'] = KeywordAdaptationType.LOCAL_TERMINOLOGY
                    analysis['confidence'] = 0.9
                    analysis['variations'][category] = terms
                    analysis['notes'].append(f"Found cultural mapping for category: {category}")
        
        # Check for sensitive terms
        sensitive_terms = ['alcohol', 'pork', 'gambling', 'dating']
        if any(term in keyword.lower() for term in sensitive_terms):
            if target_culture.upper() in ['AR', 'AMAZIGH']:
                analysis['adaptation_type'] = KeywordAdaptationType.CULTURAL_SENSITIVITY
                analysis['confidence'] = 0.95
                analysis['notes'].append("Cultural sensitivity adjustment required")
        
        return analysis

    async def _generate_cultural_adaptations(
        self,
        keyword: str,
        target_culture: str,
        target_context: CulturalContext,
        platform: str = None,
        region: str = None
    ) -> List[str]:
        """Generate culturally adapted keyword variations"""
        
        adaptations = [keyword]  # Include original
        
        # Cultural mappings
        culture_key = target_culture.upper()
        if culture_key in self.cultural_mappings:
            mapping = self.cultural_mappings[culture_key]
            for category, terms in mapping.items():
                if category in keyword.lower():
                    adaptations.extend(terms)
        
        # Platform-specific adaptations
        if platform and region:
            platform_prefs = self.platform_preferences.get(region, {}).get(platform, {})
            if platform_prefs.get('hashtag_style') == 'arabic_english_mix':
                # Add hashtag variations
                adaptations.extend([f"#{keyword}", f"#{keyword}_ar"])
        
        # Regional variations
        if region == "NA":  # North Africa
            # Add French variants for Maghreb region
            french_variants = await self._generate_french_variants(keyword)
            adaptations.extend(french_variants)
            
            # Add Amazigh variants
            amazigh_variants = await self._generate_amazigh_variants(keyword)
            adaptations.extend(amazigh_variants)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(adaptations))

    async def _generate_french_variants(self, keyword: str) -> List[str]:
        """Generate French variants for Maghreb region"""
        
        french_mappings = {
            'business': ['entreprise', 'affaires', 'commerce'],
            'technology': ['technologie', 'numérique', 'digital'],
            'fashion': ['mode', 'style', 'tendance'],
            'food': ['cuisine', 'gastronomie', 'nourriture'],
            'family': ['famille', 'foyer', 'maison']
        }
        
        variants = []
        for english_term, french_terms in french_mappings.items():
            if english_term in keyword.lower():
                variants.extend(french_terms)
        
        return variants

    async def _generate_amazigh_variants(self, keyword: str) -> List[str]:
        """
Generate Amazigh/Berber variants"""
        
        if "AMAZIGH" in self.cultural_mappings:
            mapping = self.cultural_mappings["AMAZIGH"]
            for category, terms in mapping.items():
                if category in keyword.lower():
                    return terms
        
        return []

    async def _check_cultural_sensitivity(
        self, original: str, adaptations: List[str], target_culture: str
    ) -> List[str]:
        """Check for cultural sensitivity issues"""
        
        flags = []
        
        # Religious sensitivity
        if target_culture.upper() in ['AR', 'AMAZIGH']:
            religious_sensitive = ['alcohol', 'pork', 'gambling', 'interest', 'casino']
            for term in religious_sensitive:
                if any(term in adaptation.lower() for adaptation in [original] + adaptations):
                    flags.append(f"Religious sensitivity: {term}")
        
        # Cultural taboos
        cultural_taboos = {
            'AR': ['nude', 'dating', 'lgbtq'],
            'HE': ['nazi', 'antisemitic'],
            'AMAZIGH': ['colonial', 'primitive']
        }
        
        culture_taboos = cultural_taboos.get(target_culture.upper(), [])
        for taboo in culture_taboos:
            if any(taboo in adaptation.lower() for adaptation in [original] + adaptations):
                flags.append(f"Cultural taboo: {taboo}")
        
        return flags

    async def _estimate_search_volumes(
        self, keywords: List[str], target_culture: str
    ) -> Dict[str, int]:
        """Estimate search volumes for adapted keywords"""
        
        # Simulated search volume estimation
        # In production, this would integrate with actual search APIs
        estimates = {}
        
        base_volume = 1000
        for keyword in keywords:
            # Simulate volume based on keyword characteristics
            volume = base_volume
            
            if len(keyword) > 20:  # Long-tail keywords
                volume = int(volume * 0.3)
            elif len(keyword.split()) > 1:  # Multi-word
                volume = int(volume * 0.6)
            
            # Cultural adjustment
            if target_culture.upper() in ['AR', 'HE', 'AMAZIGH']:
                volume = int(volume * 0.7)  # Smaller search market
            
            estimates[keyword] = volume
        
        return estimates

    async def _estimate_regional_popularity(
        self, keywords: List[str], region: str
    ) -> Dict[str, float]:
        """
Estimate regional popularity scores"""
        
        popularity = {}
        
        for keyword in keywords:
            score = 0.5  # Base popularity
            
            # Regional adjustments
            if region == "MENA":
                if any(char in keyword for char in "أعءغض"):  # Arabic characters
                    score += 0.3
            elif region == "NA":
                if any(char in keyword for char in "àéèêç"):  # French characters
                    score += 0.2
                if keyword in self.cultural_mappings.get("AMAZIGH", {}).get("", []):
                    score += 0.4
            
            popularity[keyword] = min(score, 1.0)
        
        return popularity

    def _generate_usage_recommendations(
        self, keyword: str, target_culture: str, platform: str = None
    ) -> str:
        """Generate usage recommendations for adapted keywords"""
        
        recommendations = []
        
        # Cultural recommendations
        if target_culture.upper() in ['AR', 'AMAZIGH']:
            recommendations.append("Use formal tone and respectful language")
            recommendations.append("Consider religious sensitivities")
        
        if target_culture.upper() == 'HE':
            recommendations.append("Right-to-left text support required")
        
        # Platform recommendations
        if platform == 'instagram':
            recommendations.append("Use hashtags strategically with local variants")
        elif platform == 'tiktok':
            recommendations.append("Incorporate trending local sounds and challenges")
        elif platform == 'youtube':
            recommendations.append("Include native language in titles and descriptions")
        
        return "; ".join(recommendations)

    async def get_regional_keyword_preferences(self, region: str) -> RegionalKeywordPreferences:
        """Get keyword preferences for a specific region"""
        
        # Sample regional preferences - in production, this would be data-driven
        preferences_data = {
            "MENA": {
                "preferred_terms": {
                    "business": ["أعمال", "تجارة", "استثمار"],
                    "lifestyle": ["حياة", "نمط الحياة", "أسلوب"]
                },
                "avoided_terms": ["alcohol", "casino", "pork"],
                "cultural_modifiers": ["halal", "family-friendly", "traditional"],
                "local_slang": {"cool": "رائع", "awesome": "مذهل"},
                "formal_vs_informal": "formal",
                "trending_keywords": ["رمضان", "عيد", "حج"],
                "seasonal_keywords": {
                    "ramadan": ["إفطار", "سحور", "رمضان كريم"],
                    "eid": ["عيد مبارك", "عيدية", "احتفال"]
                }
            },
            "NA": {
                "preferred_terms": {
                    "business": ["entreprise", "أعمال", "tamdint"],
                    "culture": ["thaqafa", "culture", "tussna"]
                },
                "avoided_terms": ["colonial", "primitive"],
                "cultural_modifiers": ["amazigh", "maghreb", "afrique du nord"],
                "local_slang": {"great": "zwina", "beautiful": "jamil"},
                "formal_vs_informal": "mixed",
                "trending_keywords": ["yennayer", "tamazgha", "atlas"],
                "seasonal_keywords": {
                    "yennayer": ["yennayer", "asseggas ameggaz", "nouvel an amazigh"]
                }
            }
        }
        
        data = preferences_data.get(region, {})
        
        return RegionalKeywordPreferences(
            region=region,
            preferred_terms=data.get("preferred_terms", {}),
            avoided_terms=data.get("avoided_terms", []),
            cultural_modifiers=data.get("cultural_modifiers", []),
            local_slang=data.get("local_slang", {}),
            formal_vs_informal=data.get("formal_vs_informal", "mixed"),
            trending_keywords=data.get("trending_keywords", []),
            seasonal_keywords=data.get("seasonal_keywords", {})
        )

    async def health_check(self) -> bool:
        """Health check for cultural keyword adapter"""
        try:
            # Test basic functionality
            test_result = await self.adapt_keywords_culturally(
                ["test"], "EN", "AR", "instagram", "MENA"
            )
            return len(test_result) > 0
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False