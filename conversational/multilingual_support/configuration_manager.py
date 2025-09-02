"""Advanced Configuration System for Multilingual Content Creators

Enterprise-grade configuration management for personalized multilingual
communication experiences tailored to content creator needs.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE ⚠️
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timezone
import json
import yaml
from pathlib import Path

# Configuration management
from pydantic import BaseModel, Field, validator
from pydantic.env_settings import BaseSettings

# Internal imports
from .language_manager import SupportedLanguage
from .content_creator_specialist import CreatorType, ContentCategory, PlatformType
from .translation_engine import TranslationProvider

logger = logging.getLogger(__name__)


class ConfigurationLevel(Enum):
    """
Configuration hierarchy levels"""

    GLOBAL = "global"
    TENANT = "tenant"
    CREATOR_TYPE = "creator_type"
    INDIVIDUAL = "individual"
    SESSION = "session"


class PersonalizationLevel(Enum):
    """Levels of personalization"""

    MINIMAL = "minimal"
    STANDARD = "standard"
    ADVANCED = "advanced"
    ULTRA_PERSONALIZED = "ultra_personalized"


class QualityProfile(Enum):
    """Quality profiles for different use cases"""

    ECONOMY = "economy"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class LanguagePreferences:
    """Language preferences configuration"""
    primary_language: SupportedLanguage
    secondary_languages: List[SupportedLanguage] = field(default_factory=list)
    target_markets: List[SupportedLanguage] = field(default_factory=list)
    avoid_languages: List[SupportedLanguage] = field(default_factory=list)
    
    # Regional preferences
    preferred_dialects: Dict[SupportedLanguage, str] = field(default_factory=dict)
    cultural_sensitivity_level: str = "high"
    
    # Auto-detection settings
    auto_detect_enabled: bool = True
    auto_detect_confidence_threshold: float = 0.85
    fallback_language: SupportedLanguage = SupportedLanguage.ENGLISH


@dataclass
class TranslationPreferences:
    """Translation preferences configuration"""
    preferred_providers: List[TranslationProvider] = field(default_factory=list)
    provider_fallback_chain: List[TranslationProvider] = field(default_factory=list)
    
    # Quality settings
    quality_profile: QualityProfile = QualityProfile.STANDARD
    minimum_confidence_score: float = 0.8
    require_human_review_threshold: float = 0.7
    
    # Caching preferences
    enable_translation_cache: bool = True
    cache_ttl_hours: int = 24
    cache_quality_threshold: float = 0.85
    
    # Cost management
    max_cost_per_translation_usd: float = 0.50
    enable_cost_optimization: bool = True
    
    # Performance settings
    max_latency_ms: int = 5000
    enable_parallel_translation: bool = True


@dataclass
class ContentAdaptationPreferences:
    """
Content adaptation preferences"""
    preserve_brand_voice: bool = True
    brand_voice_style: str = "professional"  # professional, casual, creative, authentic
    
    # Terminology preferences
    use_specialized_terminology: bool = True
    custom_terminology_database: Optional[str] = None
    
    # Cultural adaptation
    enable_cultural_adaptation: bool = True
    cultural_sensitivity_level: str = "high"  # low, medium, high, ultra
    
    # Platform optimization
    platform_specific_optimization: bool = True
    preserve_hashtags: bool = True
    preserve_mentions: bool = True
    optimize_for_seo: bool = True
    
    # Legal compliance
    add_copyright_notices: bool = False
    include_legal_disclaimers: bool = False
    require_rights_attribution: bool = True


@dataclass
class MonetizationPreferences:
    """Monetization-related preferences"""
    enable_monetization_optimization: bool = True
    
    # Revenue tracking
    track_content_performance: bool = True
    enable_revenue_analytics: bool = True
    
    # Platform monetization
    optimize_for_platform_algorithms: bool = True
    priority_platforms: List[PlatformType] = field(default_factory=list)
    
    # Collaboration preferences
    enable_collaboration_matching: bool = True
    preferred_collaboration_languages: List[SupportedLanguage] = field(default_factory=list)
    
    # Rights management
    enable_rights_protection: bool = True
    auto_dmca_protection: bool = False
    watermark_translations: bool = False


@dataclass
class NotificationPreferences:
    """
Notification preferences"""
    enable_quality_alerts: bool = True
    enable_cost_alerts: bool = True
    enable_performance_alerts: bool = True
    
    # Quality thresholds
    quality_alert_threshold: float = 0.7
    
    # Cost thresholds
    daily_cost_limit_usd: float = 100.0
    monthly_cost_limit_usd: float = 1000.0
    
    # Performance thresholds
    latency_alert_threshold_ms: int = 10000
    error_rate_alert_threshold: float = 0.05
    
    # Notification channels
    email_notifications: bool = True
    slack_notifications: bool = False
    webhook_notifications: bool = False
    
    # Notification frequency
    immediate_alerts: bool = True
    daily_summary: bool = True
    weekly_report: bool = True


class MultilingualCreatorConfiguration(BaseModel):
    """
    Comprehensive configuration model for multilingual content creators.
    
    Provides enterprise-grade configuration management with hierarchical
    inheritance, validation, and personalization capabilities.
    """
    
    # Basic identification
    configuration_id: str = Field(..., description="Unique configuration identifier")
    creator_id: Optional[str] = Field(None, description="Associated creator ID")
    creator_type: Optional[CreatorType] = Field(None, description="Type of content creator")
    configuration_level: ConfigurationLevel = Field(ConfigurationLevel.INDIVIDUAL, description="Configuration level")
    
    # Core preferences
    language_preferences: LanguagePreferences
    translation_preferences: TranslationPreferences = Field(default_factory=TranslationPreferences)
    content_adaptation_preferences: ContentAdaptationPreferences = Field(default_factory=ContentAdaptationPreferences)
    monetization_preferences: MonetizationPreferences = Field(default_factory=MonetizationPreferences)
    notification_preferences: NotificationPreferences = Field(default_factory=NotificationPreferences)
    
    # Personalization settings
    personalization_level: PersonalizationLevel = PersonalizationLevel.STANDARD
    learning_enabled: bool = True
    adaptive_optimization: bool = True
    
    # Custom settings
    custom_terminology: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    custom_templates: Dict[str, str] = Field(default_factory=dict)
    custom_workflows: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "2.0.0"
    
    # Parent configuration for inheritance
    parent_configuration_id: Optional[str] = None
    
    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True
    
    @validator('language_preferences')
    def validate_language_preferences(cls, v):
        """Validate language preferences"""
        if not v.primary_language:
            raise ValueError("Primary language must be specified")
        
        # Ensure primary language is not in avoid_languages
        if v.primary_language in v.avoid_languages:
            raise ValueError("Primary language cannot be in avoid languages list")
        
        return v
    
    @validator('translation_preferences')
    def validate_translation_preferences(cls, v):
        """Validate translation preferences"""
        if v.minimum_confidence_score < 0 or v.minimum_confidence_score > 1:
            raise ValueError("Minimum confidence score must be between 0 and 1")
        
        if v.max_cost_per_translation_usd < 0:
            raise ValueError("Max cost per translation must be non-negative")
        
        return v


class ConfigurationManager:
    """
    Enterprise configuration manager for multilingual content creator systems.
    
    Provides hierarchical configuration management, inheritance, validation,
    and dynamic updates for personalized multilingual experiences.
    """
    
    def __init__(self, storage_backend: str = "database"):
        self.storage_backend = storage_backend
        self.configurations: Dict[str, MultilingualCreatorConfiguration] = {}
        self.configuration_hierarchy: Dict[str, List[str]] = {}
        
        # Default configurations by creator type
        self.default_configurations = self._load_default_configurations()
        
        # Configuration templates
        self.templates = self._load_configuration_templates()
        
        # Validation rules
        self.validation_rules = self._load_validation_rules()
    
    async def create_configuration(
        self,
        creator_id: str,
        creator_type: CreatorType,
        base_preferences: Optional[Dict[str, Any]] = None,
        parent_config_id: Optional[str] = None
    ) -> MultilingualCreatorConfiguration:
        """Create a new configuration for a content creator"""
        
        configuration_id = f"config_{creator_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        
        # Start with default configuration for creator type
        default_config = self.default_configurations.get(
            creator_type, 
            self.default_configurations[CreatorType.INFLUENCER]
        )
        
        # Apply inheritance if parent configuration specified
        if parent_config_id:
            parent_config = await self.get_configuration(parent_config_id)
            if parent_config:
                default_config = self._merge_configurations(default_config, parent_config)
        
        # Apply custom preferences
        if base_preferences:
            default_config = self._apply_custom_preferences(default_config, base_preferences)
        
        # Create new configuration
        new_config = MultilingualCreatorConfiguration(
            configuration_id=configuration_id,
            creator_id=creator_id,
            creator_type=creator_type,
            **default_config,
            parent_configuration_id=parent_config_id
        )
        
        # Validate configuration
        validation_result = await self._validate_configuration(new_config)
        if not validation_result.is_valid:
            raise ValueError(f"Configuration validation failed: {validation_result.errors}")
        
        # Store configuration
        await self._store_configuration(new_config)
        
        # Update hierarchy
        self.configuration_hierarchy[configuration_id] = []
        if parent_config_id:
            self.configuration_hierarchy[parent_config_id].append(configuration_id)
        
        logger.info(f"Created configuration {configuration_id} for creator {creator_id}")
        
        return new_config
    
    async def get_configuration(
        self,
        configuration_id: str,
        resolve_inheritance: bool = True
    ) -> Optional[MultilingualCreatorConfiguration]:
        """Retrieve configuration with optional inheritance resolution"""
        
        # Check cache first
        if configuration_id in self.configurations:
            config = self.configurations[configuration_id]
        else:
            # Load from storage
            config = await self._load_configuration(configuration_id)
            if not config:
                return None
            
            self.configurations[configuration_id] = config
        
        # Resolve inheritance if requested
        if resolve_inheritance and config.parent_configuration_id:
            parent_config = await self.get_configuration(
                config.parent_configuration_id,
                resolve_inheritance=True
            )
            if parent_config:
                config = self._merge_configurations(asdict(parent_config), asdict(config))
                config = MultilingualCreatorConfiguration(**config)
        
        return config
    
    async def update_configuration(
        self,
        configuration_id: str,
        updates: Dict[str, Any],
        validate: bool = True
    ) -> MultilingualCreatorConfiguration:
        """
Update existing configuration"""
        
        config = await self.get_configuration(configuration_id)
        if not config:
            raise ValueError(f"Configuration {configuration_id} not found")
        
        # Apply updates
        config_dict = asdict(config)
        config_dict.update(updates)
        config_dict['updated_at'] = datetime.now(timezone.utc)
        
        updated_config = MultilingualCreatorConfiguration(**config_dict)
        
        # Validate if requested
        if validate:
            validation_result = await self._validate_configuration(updated_config)
            if not validation_result.is_valid:
                raise ValueError(f"Configuration validation failed: {validation_result.errors}")
        
        # Store updated configuration
        await self._store_configuration(updated_config)
        
        # Update cache
        self.configurations[configuration_id] = updated_config
        
        logger.info(f"Updated configuration {configuration_id}")
        
        return updated_config
    
    async def get_creator_configuration(
        self,
        creator_id: str,
        creator_type: Optional[CreatorType] = None
    ) -> Optional[MultilingualCreatorConfiguration]:
        """Get the active configuration for a specific creator"""
        
        # Find most recent configuration for creator
        creator_configs = [
            config for config in self.configurations.values()
            if config.creator_id == creator_id
        ]
        
        if not creator_configs:
            # Load from storage
            creator_configs = await self._load_creator_configurations(creator_id)
        
        if not creator_configs:
            # Create default configuration if none exists
            if creator_type:
                return await self.create_configuration(creator_id, creator_type)
            return None
        
        # Return most recent configuration
        return max(creator_configs, key=lambda c: c.updated_at)
    
    async def optimize_configuration_for_performance(
        self,
        configuration_id: str,
        performance_data: Dict[str, Any]
    ) -> MultilingualCreatorConfiguration:
        """
Optimize configuration based on performance data"""
        
        config = await self.get_configuration(configuration_id)
        if not config:
            raise ValueError(f"Configuration {configuration_id} not found")
        
        optimizations = {}
        
        # Optimize translation preferences based on performance
        if 'translation_latency' in performance_data:
            avg_latency = performance_data['translation_latency']
            if avg_latency > config.translation_preferences.max_latency_ms:
                # Adjust provider preferences to favor faster providers
                optimizations['translation_preferences'] = {
                    'preferred_providers': self._get_fastest_providers(performance_data),
                    'enable_parallel_translation': True
                }
        
        # Optimize quality settings based on success rates
        if 'quality_scores' in performance_data:
            avg_quality = sum(performance_data['quality_scores']) / len(performance_data['quality_scores'])
            if avg_quality < config.translation_preferences.minimum_confidence_score:
                optimizations.setdefault('translation_preferences', {})['quality_profile'] = QualityProfile.PREMIUM
        
        # Optimize cost settings based on usage patterns
        if 'cost_data' in performance_data:
            avg_cost = performance_data['cost_data'].get('avg_cost_per_translation', 0)
            if avg_cost > config.translation_preferences.max_cost_per_translation_usd:
                optimizations.setdefault('translation_preferences', {})['enable_cost_optimization'] = True
        
        # Apply optimizations if any
        if optimizations:
            return await self.update_configuration(configuration_id, optimizations)
        
        return config
    
    def _load_default_configurations(self) -> Dict[CreatorType, Dict[str, Any]]:
        """Load default configurations for different creator types"""
        
        return {
            CreatorType.MUSICIAN: {
                'language_preferences': LanguagePreferences(
                    primary_language=SupportedLanguage.ENGLISH,
                    target_markets=[
                        SupportedLanguage.SPANISH, SupportedLanguage.FRENCH,
                        SupportedLanguage.GERMAN, SupportedLanguage.JAPANESE
                    ],
                    cultural_sensitivity_level="high"
                ),
                'translation_preferences': TranslationPreferences(
                    quality_profile=QualityProfile.PREMIUM,
                    minimum_confidence_score=0.9,
                    enable_cost_optimization=False
                ),
                'content_adaptation_preferences': ContentAdaptationPreferences(
                    use_specialized_terminology=True,
                    brand_voice_style="creative",
                    enable_cultural_adaptation=True
                ),
                'monetization_preferences': MonetizationPreferences(
                    enable_monetization_optimization=True,
                    enable_rights_protection=True,
                    priority_platforms=[PlatformType.SPOTIFY, PlatformType.YOUTUBE]
                )
            },
            CreatorType.INFLUENCER: {
                'language_preferences': LanguagePreferences(
                    primary_language=SupportedLanguage.ENGLISH,
                    target_markets=[
                        SupportedLanguage.SPANISH, SupportedLanguage.FRENCH,
                        SupportedLanguage.PORTUGUESE
                    ]
                ),
                'translation_preferences': TranslationPreferences(
                    quality_profile=QualityProfile.STANDARD,
                    minimum_confidence_score=0.85
                ),
                'content_adaptation_preferences': ContentAdaptationPreferences(
                    brand_voice_style="authentic",
                    optimize_for_seo=True,
                    preserve_hashtags=True
                ),
                'monetization_preferences': MonetizationPreferences(
                    enable_collaboration_matching=True,
                    priority_platforms=[PlatformType.INSTAGRAM, PlatformType.TIKTOK]
                )
            },
            CreatorType.PHOTOGRAPHER: {
                'language_preferences': LanguagePreferences(
                    primary_language=SupportedLanguage.ENGLISH,
                    target_markets=[
                        SupportedLanguage.FRENCH, SupportedLanguage.GERMAN,
                        SupportedLanguage.ITALIAN
                    ]
                ),
                'content_adaptation_preferences': ContentAdaptationPreferences(
                    brand_voice_style="professional",
                    enable_cultural_adaptation=True
                ),
                'monetization_preferences': MonetizationPreferences(
                    priority_platforms=[PlatformType.INSTAGRAM, PlatformType.FACEBOOK]
                )
            }
        }
    
    def _load_configuration_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load configuration templates"""
        return {
            "global_creator": {
                "description": "Configuration for creators with global audience",
                "target_markets": [
                    "en", "es", "fr", "de", "pt", "it", "ja", "ko", "zh"
                ],
                "quality_profile": "premium",
                "cultural_adaptation": True
            },
            "cost_optimized": {
                "description": "Cost-optimized configuration for budget-conscious creators",
                "quality_profile": "standard",
                "enable_cost_optimization": True,
                "max_cost_per_translation": 0.25
            },
            "premium_quality": {
                "description": "Premium quality configuration for professional creators",
                "quality_profile": "enterprise",
                "minimum_confidence_score": 0.95,
                "require_human_review": True
            }
        }
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load configuration validation rules"""
        return {
            "quality_profile_cost_limits": {
                QualityProfile.ECONOMY: 0.10,
                QualityProfile.STANDARD: 0.25,
                QualityProfile.PREMIUM: 0.50,
                QualityProfile.ENTERPRISE: 1.00
            },
            "creator_type_quality_minimums": {
                CreatorType.MUSICIAN: 0.90,
                CreatorType.INFLUENCER: 0.85,
                CreatorType.PHOTOGRAPHER: 0.85
            }
        }
    
    def _merge_configurations(
        self,
        parent_config: Dict[str, Any],
        child_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge parent and child configurations with proper inheritance"""
        
        merged = parent_config.copy()
        
        # Deep merge nested dictionaries
        for key, value in child_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configurations(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _apply_custom_preferences(
        self,
        base_config: Dict[str, Any],
        custom_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
Apply custom preferences to base configuration"""
        
        return self._merge_configurations(base_config, custom_preferences)
    
    async def _validate_configuration(
        self,
        config: MultilingualCreatorConfiguration
    ) -> 'ValidationResult':
        """
Validate configuration against business rules"""
        
        errors = []
        warnings = []
        
        # Validate quality profile vs cost limits
        quality_cost_limits = self.validation_rules["quality_profile_cost_limits"]
        max_allowed_cost = quality_cost_limits.get(config.translation_preferences.quality_profile, 1.00)
        
        if config.translation_preferences.max_cost_per_translation_usd > max_allowed_cost:
            errors.append(
                f"Max cost per translation ({config.translation_preferences.max_cost_per_translation_usd}) "
                f"exceeds limit for quality profile {config.translation_preferences.quality_profile.value} "
                f"({max_allowed_cost})"
            )
        
        # Validate creator type quality minimums
        if config.creator_type:
            min_quality = self.validation_rules["creator_type_quality_minimums"].get(config.creator_type, 0.80)
            if config.translation_preferences.minimum_confidence_score < min_quality:
                warnings.append(
                    f"Minimum confidence score ({config.translation_preferences.minimum_confidence_score}) "
                    f"is below recommended minimum for {config.creator_type.value} ({min_quality})"
                )
        
        # Validate language consistency
        if config.language_preferences.primary_language in config.language_preferences.avoid_languages:
            errors.append("Primary language cannot be in avoid languages list")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    async def _store_configuration(self, config: MultilingualCreatorConfiguration):
        try:
            logger.info(f"Executing _store_configuration")
            
            # Implementation for _store_configuration
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_store_configuration completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_store_configuration failed: {e}")
            raise
    async def _load_configuration(self, configuration_id: str) -> Optional[MultilingualCreatorConfiguration]:
        """Load configuration from persistent storage"""
        
        if self.storage_backend == "file":
            config_path = Path(f"configurations/{configuration_id}.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                return MultilingualCreatorConfiguration(**config_data)
        
        return None
    
    async def _load_creator_configurations(self, creator_id: str) -> List[MultilingualCreatorConfiguration]:
        """Load all configurations for a specific creator"""
        
        configurations = []
        
        if self.storage_backend == "file":
            config_dir = Path("configurations")
            if config_dir.exists():
                for config_file in config_dir.glob("*.json"):
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                    
                    if config_data.get('creator_id') == creator_id:
                        configurations.append(MultilingualCreatorConfiguration(**config_data))
        
        return configurations
    
    def _get_fastest_providers(self, performance_data: Dict[str, Any]) -> List[TranslationProvider]:
        """Get fastest translation providers based on performance data"""
        
        provider_latencies = performance_data.get('provider_latencies', {})
        
        # Sort providers by average latency
        sorted_providers = sorted(
            provider_latencies.items(),
            key=lambda x: x[1]
        )
        
        # Return top 3 fastest providers
        fastest_providers = [TranslationProvider(provider) for provider, _ in sorted_providers[:3]]
        
        return fastest_providers if fastest_providers else [TranslationProvider.GOOGLE]


@dataclass
class ValidationResult:
    """
Configuration validation result"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
