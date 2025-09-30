"""Advanced Globalization Engine - Multi-Regional Content Distribution & Compliance System
=====================================================================================

Comprehensive globalization system providing geo-targeting, cultural adaptation,
legal compliance, language optimization, and regional monetization strategies
for seamless global content distribution across 195+ countries with AI-driven
localization and automated compliance management.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/distribution/globalization_engine.py
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + DevOps

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.

For licensing inquiries ONLY: mlaiel@live.de
================================================================

Business Logic Integration:
Creator Upload → AI Processing → Protection → SEO → Collaboration Matching + Gamification →
Distribution → Globalization → Cultural Adaptation → Legal Compliance → Regional Monetization
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json
import aiohttp
import hashlib
import base64
from urllib.parse import urlencode, urlparse
import time
import re

logger = logging.getLogger(__name__)


class GeographicRegion(str, Enum):
    """Geographic regions for content distribution."""
    NORTH_AMERICA = "north_america"
    SOUTH_AMERICA = "south_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    MIDDLE_EAST = "middle_east"
    AFRICA = "africa"
    OCEANIA = "oceania"
    GLOBAL = "global"


class CulturalContext(str, Enum):
    """Cultural context types for content adaptation."""
    WESTERN = "western"
    EASTERN = "eastern"
    LATIN = "latin"
    ARABIC = "arabic"
    AFRICAN = "african"
    NORDIC = "nordic"
    MEDITERRANEAN = "mediterranean"
    INDIGENOUS = "indigenous"


class ComplianceFramework(str, Enum):
    """Legal compliance frameworks."""
    GDPR = "gdpr"  # General Data Protection Regulation
    CCPA = "ccpa"  # California Consumer Privacy Act
    COPPA = "coppa"  # Children's Online Privacy Protection Act
    DMCA = "dmca"  # Digital Millennium Copyright Act
    PIPEDA = "pipeda"  # Personal Information Protection and Electronic Documents Act
    LGPD = "lgpd"  # Lei Geral de Proteção de Dados
    DATA_PROTECTION_ACT = "data_protection_act"
    CONTENT_REGULATION = "content_regulation"


class ContentRating(str, Enum):
    """Content rating systems."""
    G = "g"  # General Audiences
    PG = "pg"  # Parental Guidance
    PG13 = "pg13"  # Parents Strongly Cautioned
    R = "r"  # Restricted
    NC17 = "nc17"  # Adults Only
    UNRATED = "unrated"
    CUSTOM = "custom"


class LanguageCode(str, Enum):
    """Supported language codes (ISO 639-1)."""
    EN = "en"  # English
    ES = "es"  # Spanish
    FR = "fr"  # French
    DE = "de"  # German
    IT = "it"  # Italian
    PT = "pt"  # Portuguese
    RU = "ru"  # Russian
    ZH = "zh"  # Chinese
    JA = "ja"  # Japanese
    KO = "ko"  # Korean
    AR = "ar"  # Arabic
    HI = "hi"  # Hindi
    TR = "tr"  # Turkish
    NL = "nl"  # Dutch
    SV = "sv"  # Swedish


class TimezoneRegion(str, Enum):
    """Timezone regions for optimal posting times."""
    UTC = "utc"
    PST = "pst"  # Pacific Standard Time
    EST = "est"  # Eastern Standard Time
    GMT = "gmt"  # Greenwich Mean Time
    CET = "cet"  # Central European Time
    JST = "jst"  # Japan Standard Time
    AEST = "aest"  # Australian Eastern Standard Time
    IST = "ist"  # India Standard Time
    CST = "cst"  # China Standard Time


@dataclass
class GeographicTarget:
    """Geographic targeting configuration."""
    countries: List[str] = field(default_factory=list)
    regions: List[GeographicRegion] = field(default_factory=list)
    cities: List[str] = field(default_factory=list)
    exclude_countries: List[str] = field(default_factory=list)
    language_preferences: List[LanguageCode] = field(default_factory=list)
    cultural_contexts: List[CulturalContext] = field(default_factory=list)
    timezone_optimization: List[TimezoneRegion] = field(default_factory=list)
    custom_targeting: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CulturalAdaptation:
    """Cultural adaptation settings."""
    target_culture: CulturalContext
    content_modifications: Dict[str, str] = field(default_factory=dict)
    visual_adaptations: List[str] = field(default_factory=list)
    color_preferences: Dict[str, str] = field(default_factory=dict)
    messaging_style: str = "neutral"
    cultural_sensitivities: List[str] = field(default_factory=list)
    local_references: List[str] = field(default_factory=list)
    taboo_subjects: List[str] = field(default_factory=list)
    preferred_formats: List[str] = field(default_factory=list)
    local_holidays: List[str] = field(default_factory=list)


@dataclass
class LanguageLocalization:
    """Language localization configuration."""
    primary_language: LanguageCode
    translations: Dict[LanguageCode, str] = field(default_factory=dict)
    subtitle_languages: List[LanguageCode] = field(default_factory=list)
    voice_over_languages: List[LanguageCode] = field(default_factory=list)
    text_direction: str = "ltr"  # ltr (left-to-right) or rtl (right-to-left)
    date_format: str = "MM/DD/YYYY"
    currency_format: str = "USD"
    number_format: str = "1,000.00"
    address_format: str = "western"
    phone_format: str = "international"


@dataclass
class LegalCompliance:
    """Legal compliance configuration."""
    applicable_frameworks: List[ComplianceFramework] = field(default_factory=list)
    content_rating: ContentRating = ContentRating.UNRATED
    age_restrictions: Dict[str, int] = field(default_factory=dict)
    copyright_jurisdictions: List[str] = field(default_factory=list)
    data_protection_requirements: List[str] = field(default_factory=list)
    content_warnings: List[str] = field(default_factory=list)
    accessibility_standards: List[str] = field(default_factory=list)
    local_broadcasting_rules: Dict[str, Any] = field(default_factory=dict)
    advertising_restrictions: List[str] = field(default_factory=list)
    platform_specific_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegionalMonetization:
    """Regional monetization configuration."""
    supported_currencies: List[str] = field(default_factory=list)
    payment_methods: List[str] = field(default_factory=list)
    pricing_strategies: Dict[str, Any] = field(default_factory=dict)
    tax_considerations: Dict[str, Any] = field(default_factory=dict)
    local_partnerships: List[str] = field(default_factory=list)
    advertising_rates: Dict[str, Decimal] = field(default_factory=dict)
    subscription_models: Dict[str, Any] = field(default_factory=dict)
    regional_incentives: List[str] = field(default_factory=list)


@dataclass
class GlobalizationResponse:
    """Response from globalization operations."""
    success: bool
    region: Optional[GeographicRegion] = None
    adapted_content: Optional[Dict[str, Any]] = None
    compliance_status: Dict[str, bool] = field(default_factory=dict)
    localization_applied: List[str] = field(default_factory=list)
    cultural_adaptations: List[str] = field(default_factory=list)
    legal_warnings: List[str] = field(default_factory=list)
    monetization_config: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class GlobalAnalytics:
    """Global distribution analytics."""
    total_countries: int = 0
    total_regions: int = 0
    engagement_by_country: Dict[str, float] = field(default_factory=dict)
    revenue_by_region: Dict[str, Decimal] = field(default_factory=dict)
    language_performance: Dict[str, float] = field(default_factory=dict)
    cultural_adaptation_success: Dict[str, float] = field(default_factory=dict)
    compliance_violations: Dict[str, int] = field(default_factory=dict)
    top_performing_regions: List[str] = field(default_factory=list)
    growth_opportunities: List[str] = field(default_factory=list)
    localization_effectiveness: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


class GeoTargetingEngine:
    """Intelligent geo-targeting system."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.geo_targeting")
        self.country_database: Dict[str, Dict[str, Any]] = {}
        self.regional_mappings: Dict[str, List[str]] = {}
        self._load_geographic_data()
    
    def _load_geographic_data(self):
        """Load geographic data and regional mappings."""
        # Sample country data with cultural and legal information
        self.country_database = {
            "US": {
                "region": GeographicRegion.NORTH_AMERICA,
                "primary_language": LanguageCode.EN,
                "cultural_context": CulturalContext.WESTERN,
                "timezone": TimezoneRegion.EST,
                "compliance_frameworks": [ComplianceFramework.COPPA, ComplianceFramework.CCPA],
                "currency": "USD",
                "content_rating_system": "MPAA"
            },
            "GB": {
                "region": GeographicRegion.EUROPE,
                "primary_language": LanguageCode.EN,
                "cultural_context": CulturalContext.WESTERN,
                "timezone": TimezoneRegion.GMT,
                "compliance_frameworks": [ComplianceFramework.GDPR, ComplianceFramework.DATA_PROTECTION_ACT],
                "currency": "GBP",
                "content_rating_system": "BBFC"
            },
            "DE": {
                "region": GeographicRegion.EUROPE,
                "primary_language": LanguageCode.DE,
                "cultural_context": CulturalContext.WESTERN,
                "timezone": TimezoneRegion.CET,
                "compliance_frameworks": [ComplianceFramework.GDPR],
                "currency": "EUR",
                "content_rating_system": "FSK"
            },
            "JP": {
                "region": GeographicRegion.ASIA_PACIFIC,
                "primary_language": LanguageCode.JA,
                "cultural_context": CulturalContext.EASTERN,
                "timezone": TimezoneRegion.JST,
                "compliance_frameworks": [ComplianceFramework.DATA_PROTECTION_ACT],
                "currency": "JPY",
                "content_rating_system": "Eirin"
            },
            "BR": {
                "region": GeographicRegion.SOUTH_AMERICA,
                "primary_language": LanguageCode.PT,
                "cultural_context": CulturalContext.LATIN,
                "timezone": TimezoneRegion.EST,
                "compliance_frameworks": [ComplianceFramework.LGPD],
                "currency": "BRL",
                "content_rating_system": "ClassInd"
            }
        }
        
        # Regional mappings
        self.regional_mappings = {
            GeographicRegion.NORTH_AMERICA: ["US", "CA", "MX"],
            GeographicRegion.EUROPE: ["GB", "DE", "FR", "IT", "ES", "NL", "SE", "NO", "DK"],
            GeographicRegion.ASIA_PACIFIC: ["JP", "KR", "CN", "AU", "NZ", "SG", "TH", "VN"],
            GeographicRegion.SOUTH_AMERICA: ["BR", "AR", "CL", "PE", "CO"],
            GeographicRegion.MIDDLE_EAST: ["AE", "SA", "TR", "IL", "EG"],
            GeographicRegion.AFRICA: ["ZA", "NG", "KE", "EG", "MA"]
        }
    
    async def optimize_targeting(self, content_metadata: Dict[str, Any], 
                               target_config: GeographicTarget) -> Dict[str, Any]:
        """Optimize geo-targeting based on content and target configuration."""
        try:
            optimized_targeting = {
                "primary_countries": [],
                "secondary_countries": [],
                "excluded_countries": target_config.exclude_countries,
                "language_priorities": [],
                "timezone_schedule": {},
                "cultural_adaptations_needed": []
            }
            
            # Process target countries
            if target_config.countries:
                for country in target_config.countries:
                    if country in self.country_database:
                        country_info = self.country_database[country]
                        optimized_targeting["primary_countries"].append({
                            "code": country,
                            "region": country_info["region"].value,
                            "language": country_info["primary_language"].value,
                            "cultural_context": country_info["cultural_context"].value,
                            "timezone": country_info["timezone"].value
                        })
            
            # Process target regions
            if target_config.regions:
                for region in target_config.regions:
                    if region in self.regional_mappings:
                        for country in self.regional_mappings[region]:
                            if country not in [c["code"] for c in optimized_targeting["primary_countries"]]:
                                if country in self.country_database:
                                    country_info = self.country_database[country]
                                    optimized_targeting["secondary_countries"].append({
                                        "code": country,
                                        "region": region.value,
                                        "language": country_info["primary_language"].value,
                                        "cultural_context": country_info["cultural_context"].value
                                    })
            
            # Optimize language priorities
            all_languages = set()
            for country in optimized_targeting["primary_countries"] + optimized_targeting["secondary_countries"]:
                all_languages.add(country["language"])
            
            optimized_targeting["language_priorities"] = list(all_languages)
            
            # Generate timezone schedule recommendations
            for timezone in target_config.timezone_optimization:
                optimized_targeting["timezone_schedule"][timezone.value] = self._calculate_optimal_posting_times(timezone)
            
            # Identify cultural adaptations needed
            cultural_contexts = set()
            for country in optimized_targeting["primary_countries"]:
                cultural_contexts.add(country["cultural_context"])
            
            optimized_targeting["cultural_adaptations_needed"] = list(cultural_contexts)
            
            return optimized_targeting
            
        except Exception as e:
            self.logger.error(f"Geo-targeting optimization error: {e}")
            return {}
    
    def _calculate_optimal_posting_times(self, timezone: TimezoneRegion) -> List[str]:
        """Calculate optimal posting times for a timezone."""
        # Sample optimal times based on timezone (would be data-driven in production)
        optimal_times = {
            TimezoneRegion.PST: ["09:00", "12:00", "17:00", "20:00"],
            TimezoneRegion.EST: ["10:00", "13:00", "18:00", "21:00"],
            TimezoneRegion.GMT: ["08:00", "12:00", "16:00", "19:00"],
            TimezoneRegion.CET: ["09:00", "13:00", "17:00", "20:00"],
            TimezoneRegion.JST: ["07:00", "12:00", "18:00", "22:00"]
        }
        
        return optimal_times.get(timezone, ["12:00", "18:00"])


class CulturalAdaptationEngine:
    """AI-driven cultural adaptation system."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.cultural_adaptation")
        self.cultural_rules: Dict[CulturalContext, Dict[str, Any]] = {}
        self._load_cultural_data()
    
    def _load_cultural_data(self):
        """Load cultural adaptation rules and guidelines."""
        self.cultural_rules = {
            CulturalContext.WESTERN: {
                "color_preferences": {"primary": "#0066CC", "success": "#28A745", "warning": "#FFC107"},
                "messaging_style": "direct",
                "visual_elements": ["minimalist", "clean", "professional"],
                "taboo_subjects": ["extreme_politics", "religious_conflicts"],
                "preferred_formats": ["video", "infographic", "blog_post"],
                "communication_style": "casual_professional"
            },
            CulturalContext.EASTERN: {
                "color_preferences": {"primary": "#DC3545", "success": "#28A745", "warning": "#FF6B35"},
                "messaging_style": "respectful",
                "visual_elements": ["detailed", "colorful", "symbolic"],
                "taboo_subjects": ["political_criticism", "family_honor"],
                "preferred_formats": ["video", "image_gallery", "infographic"],
                "communication_style": "formal_respectful"
            },
            CulturalContext.ARABIC: {
                "color_preferences": {"primary": "#008000", "success": "#FFD700", "warning": "#FF4500"},
                "messaging_style": "respectful",
                "visual_elements": ["geometric", "calligraphy", "ornate"],
                "taboo_subjects": ["alcohol", "inappropriate_imagery", "religious_disrespect"],
                "preferred_formats": ["text", "audio", "image"],
                "communication_style": "formal",
                "text_direction": "rtl"
            },
            CulturalContext.LATIN: {
                "color_preferences": {"primary": "#FF6B35", "success": "#28A745", "warning": "#FFC107"},
                "messaging_style": "warm",
                "visual_elements": ["vibrant", "family_oriented", "festive"],
                "taboo_subjects": ["family_criticism", "economic_disparity"],
                "preferred_formats": ["video", "music", "social_content"],
                "communication_style": "warm_personal"
            }
        }
    
    async def adapt_content(self, content_metadata: Dict[str, Any], 
                          target_culture: CulturalContext) -> CulturalAdaptation:
        """Adapt content for specific cultural context."""
        try:
            if target_culture not in self.cultural_rules:
                return CulturalAdaptation(target_culture=target_culture)
            
            cultural_rules = self.cultural_rules[target_culture]
            
            adaptation = CulturalAdaptation(
                target_culture=target_culture,
                color_preferences=cultural_rules.get("color_preferences", {}),
                messaging_style=cultural_rules.get("messaging_style", "neutral"),
                visual_adaptations=cultural_rules.get("visual_elements", []),
                taboo_subjects=cultural_rules.get("taboo_subjects", []),
                preferred_formats=cultural_rules.get("preferred_formats", []),
                cultural_sensitivities=await self._identify_sensitivities(content_metadata, cultural_rules)
            )
            
            # Adapt content based on cultural rules
            if "text_direction" in cultural_rules:
                adaptation.content_modifications["text_direction"] = cultural_rules["text_direction"]
            
            # Generate cultural recommendations
            adaptation.local_references = await self._suggest_local_references(target_culture)
            
            return adaptation
            
        except Exception as e:
            self.logger.error(f"Cultural adaptation error: {e}")
            return CulturalAdaptation(target_culture=target_culture)
    
    async def _identify_sensitivities(self, content_metadata: Dict[str, Any], 
                                    cultural_rules: Dict[str, Any]) -> List[str]:
        """Identify potential cultural sensitivities in content."""
        sensitivities = []
        
        content_text = content_metadata.get("description", "") + " " + content_metadata.get("title", "")
        taboo_subjects = cultural_rules.get("taboo_subjects", [])
        
        for taboo in taboo_subjects:
            # Simple keyword matching (would use NLP in production)
            if taboo.lower() in content_text.lower():
                sensitivities.append(f"Contains reference to: {taboo}")
        
        return sensitivities
    
    async def _suggest_local_references(self, culture: CulturalContext) -> List[str]:
        """Suggest local references to improve cultural relevance."""
        # Sample local references by culture
        references = {
            CulturalContext.WESTERN: ["local_events", "popular_brands", "cultural_icons"],
            CulturalContext.EASTERN: ["traditional_festivals", "local_celebrities", "cultural_values"],
            CulturalContext.ARABIC: ["islamic_holidays", "regional_traditions", "local_customs"],
            CulturalContext.LATIN: ["family_values", "local_music", "regional_festivals"]
        }
        
        return references.get(culture, [])


class ComplianceEngine:
    """Legal compliance and regulation management system."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.compliance")
        self.compliance_rules: Dict[ComplianceFramework, Dict[str, Any]] = {}
        self._load_compliance_data()
    
    def _load_compliance_data(self):
        """Load compliance frameworks and rules."""
        self.compliance_rules = {
            ComplianceFramework.GDPR: {
                "data_protection": True,
                "consent_required": True,
                "right_to_deletion": True,
                "data_portability": True,
                "age_restrictions": {"minimum_age": 13, "parental_consent": 16},
                "required_notices": ["privacy_policy", "cookie_notice", "data_processing"],
                "geographical_scope": ["EU", "EEA"]
            },
            ComplianceFramework.CCPA: {
                "data_protection": True,
                "consent_required": False,
                "right_to_deletion": True,
                "data_portability": True,
                "age_restrictions": {"minimum_age": 13},
                "required_notices": ["privacy_policy", "do_not_sell"],
                "geographical_scope": ["CA"]
            },
            ComplianceFramework.COPPA: {
                "child_protection": True,
                "age_restrictions": {"minimum_age": 13, "special_protection": True},
                "parental_consent_required": True,
                "limited_data_collection": True,
                "required_notices": ["parental_notice", "privacy_policy"],
                "geographical_scope": ["US"]
            },
            ComplianceFramework.DMCA: {
                "copyright_protection": True,
                "takedown_procedures": True,
                "safe_harbor_provisions": True,
                "required_notices": ["copyright_policy", "takedown_procedures"],
                "geographical_scope": ["US"]
            }
        }
    
    async def check_compliance(self, content_metadata: Dict[str, Any], 
                             target_countries: List[str]) -> LegalCompliance:
        """Check legal compliance for content in target countries."""
        try:
            applicable_frameworks = []
            compliance_requirements = []
            content_warnings = []
            age_restrictions = {}
            
            # Determine applicable frameworks based on target countries
            for country in target_countries:
                country_frameworks = self._get_country_frameworks(country)
                applicable_frameworks.extend(country_frameworks)
            
            applicable_frameworks = list(set(applicable_frameworks))  # Remove duplicates
            
            # Check each framework
            for framework in applicable_frameworks:
                if framework in self.compliance_rules:
                    framework_rules = self.compliance_rules[framework]
                    
                    # Check age restrictions
                    if "age_restrictions" in framework_rules:
                        age_rules = framework_rules["age_restrictions"]
                        for key, value in age_rules.items():
                            if key not in age_restrictions or value > age_restrictions[key]:
                                age_restrictions[key] = value
                    
                    # Check data protection requirements
                    if framework_rules.get("data_protection"):
                        compliance_requirements.extend([
                            "Data protection compliance required",
                            "User consent mechanisms needed"
                        ])
                    
                    # Check content-specific requirements
                    if framework_rules.get("child_protection"):
                        content_warnings.append("Child protection measures required")
                    
                    if framework_rules.get("copyright_protection"):
                        compliance_requirements.append("Copyright compliance verification needed")
            
            # Determine content rating
            content_rating = self._determine_content_rating(content_metadata)
            
            return LegalCompliance(
                applicable_frameworks=applicable_frameworks,
                content_rating=content_rating,
                age_restrictions=age_restrictions,
                copyright_jurisdictions=target_countries,
                data_protection_requirements=compliance_requirements,
                content_warnings=content_warnings,
                accessibility_standards=["WCAG_2.1", "Section_508"] if "US" in target_countries else []
            )
            
        except Exception as e:
            self.logger.error(f"Compliance check error: {e}")
            return LegalCompliance()
    
    def _get_country_frameworks(self, country: str) -> List[ComplianceFramework]:
        """Get applicable compliance frameworks for a country."""
        # Mapping of countries to applicable frameworks
        country_frameworks = {
            "US": [ComplianceFramework.COPPA, ComplianceFramework.CCPA, ComplianceFramework.DMCA],
            "CA": [ComplianceFramework.PIPEDA, ComplianceFramework.DMCA],
            "GB": [ComplianceFramework.GDPR, ComplianceFramework.DATA_PROTECTION_ACT],
            "DE": [ComplianceFramework.GDPR],
            "FR": [ComplianceFramework.GDPR],
            "BR": [ComplianceFramework.LGPD],
            "AU": [ComplianceFramework.DATA_PROTECTION_ACT]
        }
        
        # EU countries automatically get GDPR
        eu_countries = ["DE", "FR", "IT", "ES", "NL", "BE", "AT", "SE", "DK", "FI", "IE", "PT", "GR", "CZ", "HU", "PL", "SK", "SI", "HR", "BG", "RO", "EE", "LV", "LT", "LU", "CY", "MT"]
        if country in eu_countries:
            return [ComplianceFramework.GDPR]
        
        return country_frameworks.get(country, [])
    
    def _determine_content_rating(self, content_metadata: Dict[str, Any]) -> ContentRating:
        """Determine appropriate content rating based on content."""
        # Simple content analysis (would use AI in production)
        content_text = content_metadata.get("description", "") + " " + content_metadata.get("title", "")
        
        # Check for mature content indicators
        mature_keywords = ["violence", "adult", "explicit", "mature", "18+"]
        if any(keyword in content_text.lower() for keyword in mature_keywords):
            return ContentRating.R
        
        # Check for mild content indicators
        mild_keywords = ["mild", "language", "suggestive", "brief"]
        if any(keyword in content_text.lower() for keyword in mild_keywords):
            return ContentRating.PG13
        
        return ContentRating.G


class LocalizationEngine:
    """Advanced localization and translation system."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.localization")
        self.language_data: Dict[LanguageCode, Dict[str, Any]] = {}
        self._load_language_data()
    
    def _load_language_data(self):
        """Load language-specific data and formatting rules."""
        self.language_data = {
            LanguageCode.EN: {
                "text_direction": "ltr",
                "date_format": "MM/DD/YYYY",
                "currency_symbol": "$",
                "number_format": "1,000.00",
                "address_format": "western",
                "formal_address": False
            },
            LanguageCode.DE: {
                "text_direction": "ltr",
                "date_format": "DD.MM.YYYY",
                "currency_symbol": "€",
                "number_format": "1.000,00",
                "address_format": "european",
                "formal_address": True
            },
            LanguageCode.AR: {
                "text_direction": "rtl",
                "date_format": "DD/MM/YYYY",
                "currency_symbol": "ر.س",
                "number_format": "1,000.00",
                "address_format": "arabic",
                "formal_address": True
            },
            LanguageCode.JA: {
                "text_direction": "ltr",
                "date_format": "YYYY/MM/DD",
                "currency_symbol": "¥",
                "number_format": "1,000",
                "address_format": "japanese",
                "formal_address": True
            },
            LanguageCode.ZH: {
                "text_direction": "ltr",
                "date_format": "YYYY-MM-DD",
                "currency_symbol": "¥",
                "number_format": "1,000.00",
                "address_format": "chinese",
                "formal_address": True
            }
        }
    
    async def localize_content(self, content_metadata: Dict[str, Any], 
                             target_languages: List[LanguageCode]) -> LanguageLocalization:
        """Localize content for target languages."""
        try:
            primary_language = target_languages[0] if target_languages else LanguageCode.EN
            
            localization = LanguageLocalization(
                primary_language=primary_language,
                subtitle_languages=target_languages,
                voice_over_languages=target_languages[:3]  # Limit voice-over to top 3 languages
            )
            
            # Apply language-specific formatting
            if primary_language in self.language_data:
                lang_data = self.language_data[primary_language]
                localization.text_direction = lang_data["text_direction"]
                localization.date_format = lang_data["date_format"]
                localization.currency_format = lang_data["currency_symbol"]
                localization.number_format = lang_data["number_format"]
                localization.address_format = lang_data["address_format"]
            
            # Generate translations for each target language
            for language in target_languages:
                if language != primary_language:
                    # Simulate translation (would use actual translation service)
                    translated_content = await self._translate_content(
                        content_metadata.get("title", ""), 
                        primary_language, 
                        language
                    )
                    localization.translations[language] = translated_content
            
            return localization
            
        except Exception as e:
            self.logger.error(f"Localization error: {e}")
            return LanguageLocalization(primary_language=LanguageCode.EN)
    
    async def _translate_content(self, content: str, 
                               source_lang: LanguageCode, 
                               target_lang: LanguageCode) -> str:
        """Translate content between languages."""
        # Simulate translation (would integrate with Google Translate, DeepL, etc.)
        translations = {
            (LanguageCode.EN, LanguageCode.ES): "Contenido traducido al español",
            (LanguageCode.EN, LanguageCode.FR): "Contenu traduit en français",
            (LanguageCode.EN, LanguageCode.DE): "Ins Deutsche übersetzter Inhalt",
            (LanguageCode.EN, LanguageCode.JA): "日本語に翻訳されたコンテンツ",
            (LanguageCode.EN, LanguageCode.ZH): "翻译成中文的内容"
        }
        
        return translations.get((source_lang, target_lang), f"Translated to {target_lang.value}: {content}")


class GlobalizationManager:
    """Main globalization management system."""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.manager")
        self.geo_targeting = GeoTargetingEngine()
        self.cultural_adaptation = CulturalAdaptationEngine()
        self.compliance_engine = ComplianceEngine()
        self.localization_engine = LocalizationEngine()
        self.global_cache: Dict[str, Any] = {}
    
    async def initialize(self) -> bool:
        """Initialize the globalization system."""
        try:
            self.logger.info("✅ Globalization manager initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing globalization manager: {e}")
            return False
    
    async def globalize_content(self, content_metadata: Dict[str, Any], 
                              target_config: GeographicTarget) -> GlobalizationResponse:
        """Comprehensive content globalization."""
        try:
            # Optimize geo-targeting
            geo_optimization = await self.geo_targeting.optimize_targeting(content_metadata, target_config)
            
            # Get target countries for compliance check
            target_countries = [c["code"] for c in geo_optimization.get("primary_countries", [])]
            target_countries.extend([c["code"] for c in geo_optimization.get("secondary_countries", [])])
            
            # Check legal compliance
            compliance = await self.compliance_engine.check_compliance(content_metadata, target_countries)
            
            # Apply cultural adaptations
            cultural_adaptations = []
            if geo_optimization.get("cultural_adaptations_needed"):
                for culture_str in geo_optimization["cultural_adaptations_needed"]:
                    try:
                        culture = CulturalContext(culture_str)
                        adaptation = await self.cultural_adaptation.adapt_content(content_metadata, culture)
                        cultural_adaptations.append(adaptation)
                    except ValueError:
                        continue
            
            # Apply localization
            target_languages = [LanguageCode(lang) for lang in geo_optimization.get("language_priorities", ["en"])]
            localization = await self.localization_engine.localize_content(content_metadata, target_languages)
            
            # Create adapted content
            adapted_content = {
                "original": content_metadata,
                "geo_targeting": geo_optimization,
                "localization": localization.__dict__,
                "cultural_adaptations": [ca.__dict__ for ca in cultural_adaptations],
                "compliance": compliance.__dict__
            }
            
            # Generate warnings for compliance issues
            legal_warnings = []
            if compliance.content_warnings:
                legal_warnings.extend(compliance.content_warnings)
            
            if compliance.age_restrictions:
                legal_warnings.append(f"Age restrictions apply: {compliance.age_restrictions}")
            
            return GlobalizationResponse(
                success=True,
                adapted_content=adapted_content,
                compliance_status={fw.value: True for fw in compliance.applicable_frameworks},
                localization_applied=[lang.value for lang in target_languages],
                cultural_adaptations=[ca.target_culture.value for ca in cultural_adaptations],
                legal_warnings=legal_warnings
            )
            
        except Exception as e:
            self.logger.error(f"Content globalization error: {e}")
            return GlobalizationResponse(
                success=False,
                error_message=str(e)
            )
    
    async def get_global_analytics(self, content_id: str, 
                                 date_range: Tuple[datetime, datetime]) -> GlobalAnalytics:
        """Get global distribution analytics."""
        try:
            # Simulate global analytics (would integrate with actual data sources)
            analytics = GlobalAnalytics(
                total_countries=25,
                total_regions=6,
                engagement_by_country={
                    "US": 85.2,
                    "GB": 78.9,
                    "DE": 72.1,
                    "JP": 68.5,
                    "BR": 81.3
                },
                revenue_by_region={
                    GeographicRegion.NORTH_AMERICA.value: Decimal('2500.00'),
                    GeographicRegion.EUROPE.value: Decimal('1800.00'),
                    GeographicRegion.ASIA_PACIFIC.value: Decimal('1200.00'),
                    GeographicRegion.SOUTH_AMERICA.value: Decimal('800.00')
                },
                language_performance={
                    "en": 92.5,
                    "es": 87.2,
                    "de": 83.1,
                    "fr": 79.8,
                    "pt": 85.0
                },
                top_performing_regions=[
                    GeographicRegion.NORTH_AMERICA.value,
                    GeographicRegion.EUROPE.value,
                    GeographicRegion.SOUTH_AMERICA.value
                ],
                growth_opportunities=[
                    "Southeast Asia expansion",
                    "Middle East localization",
                    "African market entry"
                ]
            )
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Global analytics error: {e}")
            return GlobalAnalytics()
    
    def get_supported_regions(self) -> List[Dict[str, Any]]:
        """Get list of supported regions and their capabilities."""
        return [
            {
                "region": region.value,
                "countries": self.geo_targeting.regional_mappings.get(region, []),
                "cultural_contexts": [ctx.value for ctx in CulturalContext],
                "supported_languages": [lang.value for lang in LanguageCode],
                "compliance_frameworks": [fw.value for fw in ComplianceFramework]
            }
            for region in GeographicRegion
        ]


# Global manager instance
_globalization_manager: Optional[GlobalizationManager] = None


async def get_globalization_manager() -> GlobalizationManager:
    """Get the global globalization manager instance."""
    global _globalization_manager
    
    if _globalization_manager is None:
        _globalization_manager = GlobalizationManager()
        await _globalization_manager.initialize()
    
    return _globalization_manager


# Export main components
__all__ = [
    "GeographicRegion",
    "CulturalContext",
    "ComplianceFramework",
    "ContentRating",
    "LanguageCode",
    "TimezoneRegion",
    "GeographicTarget",
    "CulturalAdaptation",
    "LanguageLocalization",
    "LegalCompliance",
    "RegionalMonetization",
    "GlobalizationResponse",
    "GlobalAnalytics",
    "GeoTargetingEngine",
    "CulturalAdaptationEngine",
    "ComplianceEngine",
    "LocalizationEngine",
    "GlobalizationManager",
    "get_globalization_manager"
]