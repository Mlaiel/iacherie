"""
Geographic Optimization Configurations
=====================================

Geographic targeting and optimization settings for Ainflue Distribution Platform.
Handles timezone-aware scheduling, cultural adaptation, and regional compliance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import time
import os
import json

class Region(Enum):
    """Major world regions for geographic optimization"""
    NORTH_AMERICA = "north_america"
    SOUTH_AMERICA = "south_america"
    EUROPE = "europe"
    ASIA_PACIFIC = "asia_pacific"
    MIDDLE_EAST_AFRICA = "middle_east_africa"
    OCEANIA = "oceania"

class ContentAdaptationLevel(Enum):
    """Levels of content adaptation for different regions"""
    NONE = "none"
    BASIC = "basic"  # Language and timezone only
    MODERATE = "moderate"  # Include cultural considerations
    FULL = "full"  # Complete localization

@dataclass
class TimezoneConfig:
    """Configuration for timezone-specific settings"""
    timezone: str
    region: Region
    peak_hours: List[int] = field(default_factory=lambda: [9, 12, 18, 21])
    active_hours: List[int] = field(default_factory=lambda: list(range(7, 23)))
    weekend_behavior: str = "normal"  # normal, reduced, increased
    cultural_considerations: Dict[str, Any] = field(default_factory=dict)
    content_preferences: List[str] = field(default_factory=list)
    language_codes: List[str] = field(default_factory=list)
    
@dataclass
class RegionalComplianceConfig:
    """Regional compliance and legal requirements"""
    region: Region
    data_privacy_laws: List[str] = field(default_factory=list)
    content_restrictions: Dict[str, List[str]] = field(default_factory=dict)
    age_verification_required: bool = False
    consent_requirements: List[str] = field(default_factory=list)
    localization_requirements: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class CulturalAdaptationConfig:
    """Cultural adaptation settings for content optimization"""
    region: Region
    adaptation_level: ContentAdaptationLevel
    color_preferences: Dict[str, str] = field(default_factory=dict)
    communication_style: str = "neutral"  # formal, casual, neutral
    emoji_preferences: List[str] = field(default_factory=list)
    hashtag_conventions: Dict[str, List[str]] = field(default_factory=dict)
    seasonal_considerations: Dict[str, Any] = field(default_factory=dict)
    religious_considerations: List[str] = field(default_factory=list)
    
class GeographicConfigs:
    """
    Geographic optimization configuration manager
    
    Features:
    - Timezone-specific optimization
    - Cultural content adaptation  
    - Regional compliance handling
    - Market penetration strategies
    - Language localization settings
    - Seasonal adaptation
    """
    
    def __init__(self):
        self.timezone_configs: Dict[str, TimezoneConfig] = {}
        self.regional_compliance: Dict[Region, RegionalComplianceConfig] = {}
        self.cultural_adaptations: Dict[Region, CulturalAdaptationConfig] = {}
        self._load_default_configurations()
        
    def _load_default_configurations(self):
        """Load default geographic configurations"""
        
        # North American timezones
        self.timezone_configs.update({
            "America/New_York": TimezoneConfig(
                timezone="America/New_York",
                region=Region.NORTH_AMERICA,
                peak_hours=[9, 12, 17, 19, 21],
                active_hours=list(range(7, 24)),
                weekend_behavior="reduced",
                cultural_considerations={
                    "business_hours": "9-17 EST",
                    "major_holidays": ["christmas", "thanksgiving", "july_4", "new_years"],
                    "cultural_events": ["super_bowl", "black_friday", "cyber_monday"]
                },
                content_preferences=["video", "stories", "carousel"],
                language_codes=["en-US", "es-US"]
            ),
            "America/Los_Angeles": TimezoneConfig(
                timezone="America/Los_Angeles",
                region=Region.NORTH_AMERICA,
                peak_hours=[8, 11, 16, 18, 20],
                active_hours=list(range(6, 23)),
                weekend_behavior="increased",
                cultural_considerations={
                    "business_hours": "9-17 PST",
                    "entertainment_focus": True,
                    "tech_audience": True,
                    "influencer_culture": "high"
                },
                content_preferences=["video", "live", "stories"],
                language_codes=["en-US", "es-US"]
            ),
            "America/Chicago": TimezoneConfig(
                timezone="America/Chicago",
                region=Region.NORTH_AMERICA,
                peak_hours=[9, 12, 17, 20],
                active_hours=list(range(7, 23)),
                weekend_behavior="normal",
                cultural_considerations={
                    "business_hours": "9-17 CST",
                    "family_oriented": True,
                    "sports_culture": "high"
                },
                content_preferences=["image", "video", "text"],
                language_codes=["en-US"]
            )
        })
        
        # European timezones
        self.timezone_configs.update({
            "Europe/London": TimezoneConfig(
                timezone="Europe/London",
                region=Region.EUROPE,
                peak_hours=[8, 13, 17, 20],
                active_hours=list(range(7, 23)),
                weekend_behavior="reduced",
                cultural_considerations={
                    "business_hours": "9-17 GMT",
                    "tea_time": "16:00",
                    "formal_communication": True,
                    "privacy_conscious": True
                },
                content_preferences=["text", "image", "video"],
                language_codes=["en-GB"]
            ),
            "Europe/Paris": TimezoneConfig(
                timezone="Europe/Paris",
                region=Region.EUROPE,
                peak_hours=[9, 13, 18, 21],
                active_hours=list(range(8, 23)),
                weekend_behavior="reduced",
                cultural_considerations={
                    "business_hours": "9-17 CET",
                    "lunch_break": "12:00-14:00",
                    "art_culture": True,
                    "fashion_focus": True
                },
                content_preferences=["image", "video", "carousel"],
                language_codes=["fr-FR"]
            ),
            "Europe/Berlin": TimezoneConfig(
                timezone="Europe/Berlin",
                region=Region.EUROPE,
                peak_hours=[8, 12, 17, 20],
                active_hours=list(range(7, 22)),
                weekend_behavior="normal",
                cultural_considerations={
                    "business_hours": "9-17 CET",
                    "efficiency_focused": True,
                    "privacy_strict": True,
                    "quality_over_quantity": True
                },
                content_preferences=["text", "image", "video"],
                language_codes=["de-DE"]
            )
        })
        
        # Asian timezones
        self.timezone_configs.update({
            "Asia/Tokyo": TimezoneConfig(
                timezone="Asia/Tokyo",
                region=Region.ASIA_PACIFIC,
                peak_hours=[7, 12, 18, 22],
                active_hours=list(range(6, 24)),
                weekend_behavior="increased",
                cultural_considerations={
                    "business_hours": "9-18 JST",
                    "mobile_first": True,
                    "visual_content": True,
                    "kawaii_culture": True,
                    "respect_hierarchy": True
                },
                content_preferences=["image", "video", "stories"],
                language_codes=["ja-JP"]
            ),
            "Asia/Shanghai": TimezoneConfig(
                timezone="Asia/Shanghai",
                region=Region.ASIA_PACIFIC,
                peak_hours=[8, 12, 19, 21],
                active_hours=list(range(7, 23)),
                weekend_behavior="normal",
                cultural_considerations={
                    "business_hours": "9-18 CST",
                    "social_commerce": True,
                    "group_oriented": True,
                    "live_streaming": True
                },
                content_preferences=["video", "live", "carousel"],
                language_codes=["zh-CN"]
            ),
            "Asia/Seoul": TimezoneConfig(
                timezone="Asia/Seoul",
                region=Region.ASIA_PACIFIC,
                peak_hours=[9, 12, 19, 22],
                active_hours=list(range(8, 24)),
                weekend_behavior="increased",
                cultural_considerations={
                    "business_hours": "9-18 KST",
                    "beauty_culture": True,
                    "k_pop_influence": True,
                    "technology_advanced": True
                },
                content_preferences=["video", "image", "stories"],
                language_codes=["ko-KR"]
            )
        })
        
        # Set up regional compliance
        self.regional_compliance[Region.EUROPE] = RegionalComplianceConfig(
            region=Region.EUROPE,
            data_privacy_laws=["GDPR", "ePrivacy Directive"],
            content_restrictions={
                "advertising": ["misleading_claims", "health_claims"],
                "data_collection": ["explicit_consent_required"],
                "cookies": ["consent_required"]
            },
            age_verification_required=True,
            consent_requirements=["data_processing", "marketing", "analytics"],
            localization_requirements={
                "privacy_policy": "local_language",
                "terms_of_service": "local_language",
                "customer_support": "local_language"
            }
        )
        
        self.regional_compliance[Region.NORTH_AMERICA] = RegionalComplianceConfig(
            region=Region.NORTH_AMERICA,
            data_privacy_laws=["CCPA", "COPPA"],
            content_restrictions={
                "advertising": ["deceptive_practices"],
                "children": ["coppa_compliance"]
            },
            age_verification_required=False,
            consent_requirements=["data_sale_opt_out"],
            localization_requirements={
                "accessibility": "ada_compliance"
            }
        )
        
        # Set up cultural adaptations
        self.cultural_adaptations[Region.NORTH_AMERICA] = CulturalAdaptationConfig(
            region=Region.NORTH_AMERICA,
            adaptation_level=ContentAdaptationLevel.MODERATE,
            color_preferences={
                "primary": "#1DA1F2",  # Twitter blue
                "success": "#00C851",
                "warning": "#FF8800",
                "danger": "#FF4444"
            },
            communication_style="casual",
            emoji_preferences=["🇺🇸", "💪", "🔥", "💯", "✨"],
            hashtag_conventions={
                "trending": ["#MondayMotivation", "#ThrowbackThursday", "#TGIF"],
                "seasonal": ["#SummerVibes", "#BackToSchool", "#HolidaySpirit"]
            },
            seasonal_considerations={
                "back_to_school": "august-september",
                "holiday_season": "november-december",
                "summer_break": "june-august"
            }
        )
        
        self.cultural_adaptations[Region.EUROPE] = CulturalAdaptationConfig(
            region=Region.EUROPE,
            adaptation_level=ContentAdaptationLevel.FULL,
            color_preferences={
                "primary": "#003399",  # EU blue
                "elegant": "#2C3E50",
                "warm": "#E74C3C"
            },
            communication_style="formal",
            emoji_preferences=["🇪🇺", "✨", "🌟", "💫"],
            hashtag_conventions={
                "multilingual": True,
                "formal_tone": True
            },
            seasonal_considerations={
                "summer_holidays": "july-august",
                "christmas_markets": "december",
                "spring_festivals": "march-may"
            },
            religious_considerations=["christian_holidays", "islamic_holidays", "jewish_holidays"]
        )
        
    def get_timezone_config(self, timezone: str) -> Optional[TimezoneConfig]:
        """Get configuration for a specific timezone"""
        return self.timezone_configs.get(timezone)
        
    def get_regional_compliance(self, region: Region) -> Optional[RegionalComplianceConfig]:
        """Get compliance configuration for a region"""
        return self.regional_compliance.get(region)
        
    def get_cultural_adaptation(self, region: Region) -> Optional[CulturalAdaptationConfig]:
        """Get cultural adaptation configuration for a region"""
        return self.cultural_adaptations.get(region)
        
    def get_optimal_posting_times(self, timezone: str) -> List[int]:
        """Get optimal posting times for a timezone"""
        config = self.get_timezone_config(timezone)
        return config.peak_hours if config else [9, 12, 18, 21]
        
    def get_content_preferences(self, timezone: str) -> List[str]:
        """Get content type preferences for a timezone"""
        config = self.get_timezone_config(timezone)
        return config.content_preferences if config else ["image", "text"]
        
    def get_language_codes(self, timezone: str) -> List[str]:
        """Get supported language codes for a timezone"""
        config = self.get_timezone_config(timezone)
        return config.language_codes if config else ["en-US"]
        
    def is_privacy_strict_region(self, region: Region) -> bool:
        """Check if region has strict privacy requirements"""
        compliance = self.get_regional_compliance(region)
        if not compliance:
            return False
        return "GDPR" in compliance.data_privacy_laws
        
    def get_cultural_colors(self, region: Region) -> Dict[str, str]:
        """Get culturally appropriate colors for a region"""
        adaptation = self.get_cultural_adaptation(region)
        return adaptation.color_preferences if adaptation else {}
        
    def get_communication_style(self, region: Region) -> str:
        """Get appropriate communication style for a region"""
        adaptation = self.get_cultural_adaptation(region)
        return adaptation.communication_style if adaptation else "neutral"
        
    def get_regional_hashtags(self, region: Region, category: str = "trending") -> List[str]:
        """Get region-appropriate hashtags"""
        adaptation = self.get_cultural_adaptation(region)
        if not adaptation or not adaptation.hashtag_conventions:
            return []
        return adaptation.hashtag_conventions.get(category, [])
        
    def validate_content_compliance(self, content: Dict[str, Any], region: Region) -> Dict[str, Any]:
        """Validate content against regional compliance requirements"""
        compliance = self.get_regional_compliance(region)
        if not compliance:
            return {"valid": True, "warnings": []}
            
        warnings = []
        
        # Check age verification requirements
        if compliance.age_verification_required and not content.get("age_verified"):
            warnings.append("Age verification required for this region")
            
        # Check data privacy compliance
        if "GDPR" in compliance.data_privacy_laws:
            if not content.get("gdpr_compliant"):
                warnings.append("GDPR compliance verification required")
                
        # Check content restrictions
        for restriction_type, restrictions in compliance.content_restrictions.items():
            if content.get("type") == restriction_type:
                for restriction in restrictions:
                    if not content.get(f"compliant_{restriction}"):
                        warnings.append(f"Content must comply with {restriction}")
                        
        return {
            "valid": len(warnings) == 0,
            "warnings": warnings,
            "region": region.value
        }
        
    def get_localization_requirements(self, region: Region) -> Dict[str, Any]:
        """Get localization requirements for a region"""
        compliance = self.get_regional_compliance(region)
        return compliance.localization_requirements if compliance else {}
        
    def adapt_content_for_culture(self, content: Dict[str, Any], region: Region) -> Dict[str, Any]:
        """Adapt content for cultural preferences"""
        adaptation = self.get_cultural_adaptation(region)
        if not adaptation:
            return content
            
        adapted_content = content.copy()
        
        # Adapt communication style
        if adaptation.communication_style == "formal":
            adapted_content["tone"] = "formal"
        elif adaptation.communication_style == "casual":
            adapted_content["tone"] = "casual"
            
        # Add cultural colors
        if adaptation.color_preferences:
            adapted_content["color_scheme"] = adaptation.color_preferences
            
        # Add region-appropriate emojis
        if adaptation.emoji_preferences:
            adapted_content["suggested_emojis"] = adaptation.emoji_preferences
            
        # Add seasonal considerations
        if adaptation.seasonal_considerations:
            adapted_content["seasonal_hints"] = adaptation.seasonal_considerations
            
        # Add religious considerations
        if adaptation.religious_considerations:
            adapted_content["religious_considerations"] = adaptation.religious_considerations
            
        return adapted_content
        
    def get_timezone_by_region(self, region: Region) -> List[str]:
        """Get all timezones for a specific region"""
        return [
            tz for tz, config in self.timezone_configs.items()
            if config.region == region
        ]
        
    def export_config(self, output_path: str):
        """Export configuration to JSON file"""
        config_data = {
            "timezones": {
                tz: {
                    "timezone": config.timezone,
                    "region": config.region.value,
                    "peak_hours": config.peak_hours,
                    "active_hours": config.active_hours,
                    "weekend_behavior": config.weekend_behavior,
                    "cultural_considerations": config.cultural_considerations,
                    "content_preferences": config.content_preferences,
                    "language_codes": config.language_codes
                }
                for tz, config in self.timezone_configs.items()
            },
            "regional_compliance": {
                region.value: {
                    "region": config.region.value,
                    "data_privacy_laws": config.data_privacy_laws,
                    "content_restrictions": config.content_restrictions,
                    "age_verification_required": config.age_verification_required,
                    "consent_requirements": config.consent_requirements,
                    "localization_requirements": config.localization_requirements
                }
                for region, config in self.regional_compliance.items()
            },
            "cultural_adaptations": {
                region.value: {
                    "region": config.region.value,
                    "adaptation_level": config.adaptation_level.value,
                    "color_preferences": config.color_preferences,
                    "communication_style": config.communication_style,
                    "emoji_preferences": config.emoji_preferences,
                    "hashtag_conventions": config.hashtag_conventions,
                    "seasonal_considerations": config.seasonal_considerations,
                    "religious_considerations": config.religious_considerations
                }
                for region, config in self.cultural_adaptations.items()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
            
    def load_config(self, config_path: str):
        """Load configuration from JSON file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            
        # Load timezone configs
        for tz, data in config_data.get("timezones", {}).items():
            self.timezone_configs[tz] = TimezoneConfig(
                timezone=data["timezone"],
                region=Region(data["region"]),
                peak_hours=data["peak_hours"],
                active_hours=data["active_hours"],
                weekend_behavior=data["weekend_behavior"],
                cultural_considerations=data["cultural_considerations"],
                content_preferences=data["content_preferences"],
                language_codes=data["language_codes"]
            )
            
        # Load compliance configs
        for region_str, data in config_data.get("regional_compliance", {}).items():
            region = Region(region_str)
            self.regional_compliance[region] = RegionalComplianceConfig(
                region=region,
                data_privacy_laws=data["data_privacy_laws"],
                content_restrictions=data["content_restrictions"],
                age_verification_required=data["age_verification_required"],
                consent_requirements=data["consent_requirements"],
                localization_requirements=data["localization_requirements"]
            )
            
        # Load cultural adaptations
        for region_str, data in config_data.get("cultural_adaptations", {}).items():
            region = Region(region_str)
            self.cultural_adaptations[region] = CulturalAdaptationConfig(
                region=region,
                adaptation_level=ContentAdaptationLevel(data["adaptation_level"]),
                color_preferences=data["color_preferences"],
                communication_style=data["communication_style"],
                emoji_preferences=data["emoji_preferences"],
                hashtag_conventions=data["hashtag_conventions"],
                seasonal_considerations=data["seasonal_considerations"],
                religious_considerations=data["religious_considerations"]
            )

# Global instance
geographic_configs = GeographicConfigs()

# Environment-based configuration loading
config_file = os.getenv('GEOGRAPHIC_CONFIG_FILE')
if config_file and os.path.exists(config_file):
    geographic_configs.load_config(config_file)

# Export configuration for external use
def get_geographic_configs() -> GeographicConfigs:
    """Get the global geographic configurations instance"""
    return geographic_configs

def get_timezone_config(timezone: str) -> Optional[TimezoneConfig]:
    """Get timezone configuration"""
    return geographic_configs.get_timezone_config(timezone)

def get_optimal_times(timezone: str) -> List[int]:
    """Get optimal posting times for timezone"""
    return geographic_configs.get_optimal_posting_times(timezone)

def validate_regional_compliance(content: Dict[str, Any], region: Region) -> Dict[str, Any]:
    """Validate content for regional compliance"""
    return geographic_configs.validate_content_compliance(content, region)

def adapt_content_culturally(content: Dict[str, Any], region: Region) -> Dict[str, Any]:
    """Adapt content for cultural preferences"""
    return geographic_configs.adapt_content_for_culture(content, region)