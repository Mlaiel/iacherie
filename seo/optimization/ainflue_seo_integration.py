#!/usr/bin/env python3
"""
Unified SEO Multi-Platform Integration with 644+ Languages
===========================================================

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

This module provides the main integration point for the industrial multi-platform
SEO system with 644+ language support and multi-provider translation APIs.

Features:
- Complete integration of all SEO components
- Easy-to-use API for developers
- Configuration management
- Performance monitoring
- Comprehensive examples and documentation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import asdict
import json
from datetime import datetime

from .extended_languages import ExtendedLanguageSupport
from .multi_provider_translation import (
    MultiProviderTranslationManager,
    TranslationProvider,
    TranslationQuality,
    ProviderConfig
)
from .industrial_seo_system import (
    IndustrialSEOOptimizer,
    Platform,
    ContentType,
    SEOObjective,
    MultilingualSEOResult
)

logger = logging.getLogger(__name__)


class AinflueSEOConfiguration:
    """Configuration class for Ainflue SEO system"""
    
    def __init__(self):
        self.translation_providers = {}
        self.default_quality = TranslationQuality.STANDARD
        self.cache_enabled = True
        self.analytics_enabled = True
        self.performance_monitoring = True
        self.max_languages_per_request = 50
        self.max_platforms_per_request = 10
        
    def configure_google_translate(self, api_key: str, project_id: Optional[str] = None):
        """Configure Google Translate API"""
        config = ProviderConfig(
            name=TranslationProvider.GOOGLE,
            api_key=api_key,
            endpoint="https://translation.googleapis.com/language/translate/v2"
        )
        self.translation_providers[TranslationProvider.GOOGLE] = config
        
    def configure_deepl(self, api_key: str, pro_account: bool = False):
        """Configure DeepL API"""
        endpoint = "https://api.deepl.com/v2/translate" if pro_account else "https://api-free.deepl.com/v2/translate"
        config = ProviderConfig(
            name=TranslationProvider.DEEPL,
            api_key=api_key,
            endpoint=endpoint
        )
        self.translation_providers[TranslationProvider.DEEPL] = config
        
    def configure_microsoft_translator(self, api_key: str, region: str = "global"):
        """Configure Microsoft Translator API"""
        config = ProviderConfig(
            name=TranslationProvider.MICROSOFT,
            api_key=api_key,
            region=region,
            endpoint="https://api.cognitive.microsofttranslator.com/translate"
        )
        self.translation_providers[TranslationProvider.MICROSOFT] = config
        
    def configure_amazon_translate(self, access_key: str, secret_key: str, region: str = "us-east-1"):
        """Configure Amazon Translate"""
        config = ProviderConfig(
            name=TranslationProvider.AMAZON,
            api_key=access_key,
            api_secret=secret_key,
            region=region
        )
        self.translation_providers[TranslationProvider.AMAZON] = config


class AinflueSEOEngine:
    """
    Main Ainflue SEO Engine with 644+ language support and multi-provider translation
    
    This is the primary interface for the industrial SEO optimization system.
    """
    
    def __init__(self, config: Optional[AinflueSEOConfiguration] = None):
        """Initialize the Ainflue SEO Engine"""
        self.config = config or AinflueSEOConfiguration()
        self.language_support = ExtendedLanguageSupport()
        self.translation_manager = MultiProviderTranslationManager()
        self.seo_optimizer = IndustrialSEOOptimizer()
        self.is_initialized = False
        
        # Performance tracking
        self.optimization_history = []
        self.performance_metrics = {
            "total_optimizations": 0,
            "total_languages_processed": 0,
            "total_platforms_optimized": 0,
            "average_processing_time": 0.0,
            "success_rate": 0.0
        }
        
    async def initialize(self):
        """Initialize the SEO engine with all components"""
        try:
            # Initialize translation providers
            for provider_type, provider_config in self.config.translation_providers.items():
                self.translation_manager.configure_provider(provider_type, provider_config)
            
            # Validate language support
            language_stats = self.language_support.get_language_statistics()
            logger.info(f"Language support initialized: {language_stats['total_languages']} languages")
            
            # Initialize SEO optimizer
            self.seo_optimizer.translation_manager = self.translation_manager
            
            self.is_initialized = True
            logger.info("Ainflue SEO Engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SEO engine: {str(e)}")
            raise
    
    async def optimize_content_global(
        self,
        content: str,
        title: str,
        description: str,
        source_language: str = "en",
        target_languages: Optional[List[str]] = None,
        platforms: Optional[List[Platform]] = None,
        content_type: ContentType = ContentType.TEXT,
        objectives: Optional[List[SEOObjective]] = None,
        translation_quality: TranslationQuality = None
    ) -> MultilingualSEOResult:
        """
        Main method to optimize content for global reach across multiple platforms
        
        Args:
            content: The main content to optimize
            title: Content title
            description: Content description
            source_language: Source language code (default: "en")
            target_languages: List of target language codes (default: major languages)
            platforms: List of platforms to optimize for (default: major platforms)
            content_type: Type of content being optimized
            objectives: SEO objectives (default: discoverability + engagement)
            translation_quality: Translation quality level
            
        Returns:
            MultilingualSEOResult with complete optimization data
        """
        
        if not self.is_initialized:
            await self.initialize()
        
        start_time = datetime.now()
        
        try:
            # Set defaults
            if target_languages is None:
                target_languages = self._get_default_target_languages()
            
            if platforms is None:
                platforms = self._get_default_platforms(content_type)
            
            if objectives is None:
                objectives = [SEOObjective.DISCOVERABILITY, SEOObjective.ENGAGEMENT]
            
            if translation_quality is None:
                translation_quality = self.config.default_quality
            
            # Validate inputs
            self._validate_global_optimization_inputs(
                source_language, target_languages, platforms, content_type
            )
            
            # Perform optimization
            result = await self.seo_optimizer.optimize_content_multilingual(
                content=content,
                title=title,
                description=description,
                source_language=source_language,
                target_languages=target_languages,
                platforms=platforms,
                content_type=content_type,
                objectives=objectives,
                translation_quality=translation_quality
            )
            
            # Update performance metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(result, processing_time, success=True)
            
            # Store in history if analytics enabled
            if self.config.analytics_enabled:
                self.optimization_history.append({
                    "timestamp": start_time.isoformat(),
                    "languages": len(target_languages) + 1,
                    "platforms": len(platforms),
                    "processing_time": processing_time,
                    "global_score": result.global_optimization_score
                })
            
            logger.info(f"Global content optimization completed successfully in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(None, processing_time, success=False)
            logger.error(f"Global content optimization failed: {str(e)}")
            raise
    
    def _get_default_target_languages(self) -> List[str]:
        """Get default target languages for global optimization"""
        # Major world languages by speaker count and digital presence
        return [
            "es",    # Spanish - 500M speakers
            "fr",    # French - 280M speakers  
            "de",    # German - 130M speakers
            "pt",    # Portuguese - 260M speakers
            "zh",    # Chinese - 1.1B speakers
            "ja",    # Japanese - 125M speakers
            "ko",    # Korean - 77M speakers
            "ar",    # Arabic - 422M speakers
            "hi",    # Hindi - 341M speakers
            "ru",    # Russian - 258M speakers
            "it",    # Italian - 65M speakers
            "nl",    # Dutch - 24M speakers
            "sv",    # Swedish - 10M speakers
            "da",    # Danish - 6M speakers
            "no",    # Norwegian - 5M speakers
        ]
    
    def _get_default_platforms(self, content_type: ContentType) -> List[Platform]:
        """Get default platforms based on content type"""
        
        platform_mapping = {
            ContentType.VIDEO: [
                Platform.YOUTUBE, Platform.TIKTOK, Platform.INSTAGRAM, 
                Platform.FACEBOOK, Platform.TWITTER, Platform.VIMEO
            ],
            ContentType.MUSIC: [
                Platform.SPOTIFY, Platform.SOUNDCLOUD, Platform.APPLE_MUSIC,
                Platform.AMAZON_MUSIC, Platform.YOUTUBE, Platform.BANDCAMP
            ],
            ContentType.IMAGE: [
                Platform.INSTAGRAM, Platform.PINTEREST, Platform.FACEBOOK,
                Platform.TWITTER, Platform.BEHANCE, Platform.DRIBBBLE
            ],
            ContentType.TEXT: [
                Platform.TWITTER, Platform.LINKEDIN, Platform.FACEBOOK,
                Platform.MEDIUM, Platform.WORDPRESS, Platform.REDDIT
            ],
            ContentType.ARTICLE: [
                Platform.MEDIUM, Platform.LINKEDIN, Platform.WORDPRESS,
                Platform.BLOGGER, Platform.FACEBOOK, Platform.TWITTER
            ],
            ContentType.PODCAST: [
                Platform.SPOTIFY, Platform.SOUNDCLOUD, Platform.APPLE_MUSIC,
                Platform.YOUTUBE, Platform.LINKEDIN
            ]
        }
        
        return platform_mapping.get(content_type, [
            Platform.FACEBOOK, Platform.TWITTER, Platform.INSTAGRAM, 
            Platform.LINKEDIN, Platform.YOUTUBE
        ])
    
    def _validate_global_optimization_inputs(
        self,
        source_language: str,
        target_languages: List[str],
        platforms: List[Platform],
        content_type: ContentType
    ):
        """Validate inputs for global optimization"""
        
        # Check language limits
        total_languages = len(target_languages) + 1
        if total_languages > self.config.max_languages_per_request:
            raise ValueError(f"Too many languages requested: {total_languages}. Maximum: {self.config.max_languages_per_request}")
        
        # Check platform limits
        if len(platforms) > self.config.max_platforms_per_request:
            raise ValueError(f"Too many platforms requested: {len(platforms)}. Maximum: {self.config.max_platforms_per_request}")
        
        # Validate language support
        if not self.language_support.validate_language_code(source_language):
            raise ValueError(f"Unsupported source language: {source_language}")
        
        for lang in target_languages:
            if not self.language_support.validate_language_code(lang):
                raise ValueError(f"Unsupported target language: {lang}")
    
    def _update_performance_metrics(
        self, 
        result: Optional[MultilingualSEOResult], 
        processing_time: float, 
        success: bool
    ):
        """Update performance metrics"""
        
        self.performance_metrics["total_optimizations"] += 1
        
        if success and result:
            self.performance_metrics["total_languages_processed"] += len(result.localized_versions)
            self.performance_metrics["total_platforms_optimized"] += len(result.platform_variations)
        
        # Update average processing time
        current_avg = self.performance_metrics["average_processing_time"]
        total_ops = self.performance_metrics["total_optimizations"]
        new_avg = ((current_avg * (total_ops - 1)) + processing_time) / total_ops
        self.performance_metrics["average_processing_time"] = new_avg
        
        # Update success rate
        successful_ops = sum(1 for h in self.optimization_history if "global_score" in h)
        if success:
            successful_ops += 1
        self.performance_metrics["success_rate"] = successful_ops / total_ops
    
    async def get_language_suggestions(
        self, 
        content: str, 
        target_audience: Optional[str] = None,
        business_objectives: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get intelligent language suggestions based on content analysis
        """
        
        suggestions = {
            "recommended_languages": [],
            "language_analysis": {},
            "market_opportunities": {},
            "cultural_considerations": {}
        }
        
        # Analyze content for language detection
        # (In real implementation, would use NLP for content analysis)
        
        # Get major languages with high digital presence
        major_languages = self.language_support.get_major_languages(min_speakers=50000000)
        
        # Score languages based on various factors
        language_scores = {}
        
        for lang_info in major_languages[:30]:  # Top 30 major languages
            score = 0
            
            # Base score from speaker count
            score += min(lang_info.speakers / 100000000, 5)  # Max 5 points
            
            # Official language bonus
            if lang_info.is_official:
                score += 2
            
            # Digital presence (simplified estimation)
            if lang_info.code in ["en", "zh", "es", "fr", "de", "ja", "pt", "ar", "ru", "ko"]:
                score += 3
            
            # Business opportunity (simplified)
            if target_audience:
                if target_audience.lower() in ["global", "international"]:
                    score += 2
                elif target_audience.lower() in ["european", "europe"] and lang_info.family.value == "indo_european":
                    score += 3
                elif target_audience.lower() in ["asian", "asia"] and lang_info.code in ["zh", "ja", "ko", "hi", "th", "vi"]:
                    score += 3
            
            language_scores[lang_info.code] = {
                "score": score,
                "language_info": lang_info,
                "speakers": lang_info.speakers,
                "regions": lang_info.regions
            }
        
        # Sort by score and take top recommendations
        sorted_languages = sorted(language_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        
        for lang_code, data in sorted_languages[:15]:  # Top 15 recommendations
            lang_info = data["language_info"]
            suggestions["recommended_languages"].append({
                "code": lang_code,
                "name": lang_info.name,
                "native_name": lang_info.native_name,
                "speakers": lang_info.speakers,
                "regions": lang_info.regions,
                "score": data["score"],
                "script": lang_info.script.value,
                "direction": lang_info.direction.value
            })
        
        # Add analysis data
        suggestions["language_analysis"] = {
            "total_languages_available": len(self.language_support.languages),
            "major_languages_count": len(major_languages),
            "rtl_languages_available": len(self.language_support.get_rtl_languages()),
            "script_distribution": {
                script.value: len(self.language_support.get_languages_by_script(script))
                for script in self.language_support.script_languages.keys()
            }
        }
        
        return suggestions
    
    async def get_platform_optimization_preview(
        self,
        title: str,
        description: str,
        platforms: List[Platform],
        language: str = "en"
    ) -> Dict[Platform, Dict[str, Any]]:
        """
        Get a preview of how content would be optimized for different platforms
        """
        
        if not self.is_initialized:
            await self.initialize()
        
        previews = {}
        
        for platform in platforms:
            try:
                # Get platform requirements
                requirements = self.seo_optimizer.platform_requirements.get(platform)
                
                if not requirements:
                    continue
                
                # Simulate optimization
                optimized_title = title
                optimized_description = description
                
                # Apply length limits
                if len(optimized_title) > requirements.title_max_length:
                    optimized_title = optimized_title[:requirements.title_max_length-3] + "..."
                
                if len(optimized_description) > requirements.description_max_length:
                    optimized_description = optimized_description[:requirements.description_max_length-3] + "..."
                
                # Generate sample tags and hashtags
                sample_keywords = ["content", "optimization", "seo", "marketing"]
                sample_tags = sample_keywords[:requirements.tags_max_count]
                sample_hashtags = [f"#{kw}" for kw in sample_keywords[:5]] if requirements.supports_hashtags else []
                
                previews[platform] = {
                    "optimized_title": optimized_title,
                    "optimized_description": optimized_description,
                    "sample_tags": sample_tags,
                    "sample_hashtags": sample_hashtags,
                    "requirements": {
                        "title_max_length": requirements.title_max_length,
                        "description_max_length": requirements.description_max_length,
                        "tags_max_count": requirements.tags_max_count,
                        "supports_hashtags": requirements.supports_hashtags,
                        "supports_mentions": requirements.supports_mentions
                    },
                    "estimated_score": 75.0  # Placeholder score
                }
                
            except Exception as e:
                logger.error(f"Error generating preview for {platform.value}: {str(e)}")
                previews[platform] = {"error": str(e)}
        
        return previews
    
    def get_translation_cost_estimate(
        self,
        content_length: int,
        target_languages: List[str],
        quality: TranslationQuality = TranslationQuality.STANDARD
    ) -> Dict[str, Any]:
        """
        Get cost estimates for translation across different providers
        """
        
        estimates = {
            "content_length": content_length,
            "target_languages": len(target_languages),
            "quality": quality.value,
            "provider_costs": {},
            "recommendations": []
        }
        
        # Provider cost rates (per character)
        provider_rates = {
            TranslationProvider.GOOGLE: 0.00002,
            TranslationProvider.DEEPL: 0.00003,
            TranslationProvider.MICROSOFT: 0.000015,
            TranslationProvider.AMAZON: 0.000012
        }
        
        # Quality multipliers
        quality_multipliers = {
            TranslationQuality.BASIC: 0.8,
            TranslationQuality.STANDARD: 1.0,
            TranslationQuality.PROFESSIONAL: 1.3,
            TranslationQuality.PREMIUM: 1.8
        }
        
        total_chars = content_length * len(target_languages)
        multiplier = quality_multipliers[quality]
        
        for provider, rate in provider_rates.items():
            cost = total_chars * rate * multiplier
            estimates["provider_costs"][provider.value] = {
                "cost_usd": round(cost, 4),
                "rate_per_char": rate,
                "total_chars": total_chars,
                "quality_multiplier": multiplier
            }
        
        # Add recommendations
        cheapest_provider = min(provider_rates.items(), key=lambda x: x[1])
        most_expensive = max(provider_rates.items(), key=lambda x: x[1])
        
        estimates["recommendations"] = [
            f"Most cost-effective: {cheapest_provider[0].value}",
            f"Highest quality: {TranslationProvider.DEEPL.value} (recommended for premium content)",
            f"Best balance: {TranslationProvider.MICROSOFT.value} or {TranslationProvider.GOOGLE.value}",
            f"Enterprise scaling: {TranslationProvider.AMAZON.value}"
        ]
        
        return estimates
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive performance dashboard data
        """
        
        language_stats = self.language_support.get_language_statistics()
        optimization_stats = self.seo_optimizer.get_optimization_statistics()
        
        dashboard = {
            "system_status": {
                "initialized": self.is_initialized,
                "translation_providers_configured": len(self.config.translation_providers),
                "cache_enabled": self.config.cache_enabled,
                "analytics_enabled": self.config.analytics_enabled
            },
            "language_support": language_stats,
            "optimization_engine": optimization_stats,
            "performance_metrics": self.performance_metrics,
            "recent_optimizations": self.optimization_history[-10:] if self.optimization_history else [],
            "provider_status": {}
        }
        
        # Add provider status if translation manager is available
        if hasattr(self.translation_manager, 'get_provider_status'):
            dashboard["provider_status"] = self.translation_manager.get_provider_status()
        
        return dashboard
    
    def export_optimization_data(self, result: MultilingualSEOResult, format: str = "json") -> str:
        """
        Export optimization results in various formats
        """
        
        return self.seo_optimizer.export_optimization_report(result, format)
    
    async def bulk_optimize_content(
        self,
        content_items: List[Dict[str, Any]],
        global_settings: Optional[Dict[str, Any]] = None
    ) -> List[MultilingualSEOResult]:
        """
        Optimize multiple content items in bulk
        """
        
        if not self.is_initialized:
            await self.initialize()
        
        results = []
        global_settings = global_settings or {}
        
        # Set default global settings
        default_target_languages = global_settings.get("target_languages", self._get_default_target_languages()[:5])
        default_platforms = global_settings.get("platforms", [Platform.FACEBOOK, Platform.TWITTER, Platform.INSTAGRAM])
        default_quality = TranslationQuality(global_settings.get("translation_quality", "standard"))
        
        # Process items in batches to manage resources
        batch_size = 5
        for i in range(0, len(content_items), batch_size):
            batch = content_items[i:i + batch_size]
            batch_tasks = []
            
            for item in batch:
                # Override defaults with item-specific settings
                target_languages = item.get("target_languages", default_target_languages)
                platforms = [Platform(p) if isinstance(p, str) else p for p in item.get("platforms", default_platforms)]
                content_type = ContentType(item.get("content_type", "text"))
                quality = TranslationQuality(item.get("translation_quality", default_quality.value))
                
                task = self.optimize_content_global(
                    content=item["content"],
                    title=item["title"],
                    description=item["description"],
                    source_language=item.get("source_language", "en"),
                    target_languages=target_languages,
                    platforms=platforms,
                    content_type=content_type,
                    translation_quality=quality
                )
                batch_tasks.append(task)
            
            # Execute batch
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Bulk optimization failed for item {i+j}: {str(result)}")
                    # Create error result
                    error_result = MultilingualSEOResult(
                        original_content=None,
                        localized_versions={},
                        hreflang_tags=[],
                        platform_variations={},
                        global_optimization_score=0.0,
                        translation_costs={},
                        performance_predictions={},
                        recommendations=[f"Optimization failed: {str(result)}"],
                        processing_time=0.0,
                        metadata={"error": str(result)}
                    )
                    results.append(error_result)
                else:
                    results.append(result)
        
        logger.info(f"Bulk optimization completed: {len(results)} items processed")
        return results


# Convenience functions for quick usage

async def quick_optimize(
    content: str,
    title: str,
    description: str,
    target_languages: Optional[List[str]] = None,
    platforms: Optional[List[str]] = None
) -> MultilingualSEOResult:
    """
    Quick optimization function for simple use cases
    """
    
    # Create minimal configuration
    config = AinflueSEOConfiguration()
    
    # Initialize engine
    engine = AinflueSEOEngine(config)
    await engine.initialize()
    
    # Convert platform strings to enums if provided
    platform_enums = []
    if platforms:
        for platform in platforms:
            try:
                platform_enums.append(Platform(platform.lower()))
            except ValueError:
                logger.warning(f"Unknown platform: {platform}")
    
    # Perform optimization
    result = await engine.optimize_content_global(
        content=content,
        title=title,
        description=description,
        target_languages=target_languages,
        platforms=platform_enums if platform_enums else None
    )
    
    return result


def get_supported_languages() -> Dict[str, Any]:
    """Get information about all supported languages"""
    language_support = ExtendedLanguageSupport()
    return language_support.get_language_statistics()


def get_supported_platforms() -> List[str]:
    """Get list of all supported platforms"""
    return [platform.value for platform in Platform]


# Module exports
__all__ = [
    "AinflueSEOEngine",
    "AinflueSEOConfiguration", 
    "quick_optimize",
    "get_supported_languages",
    "get_supported_platforms",
    "Platform",
    "ContentType",
    "SEOObjective",
    "TranslationProvider",
    "TranslationQuality"
]

logger.info("Ainflue SEO Multi-Platform Integration loaded successfully")