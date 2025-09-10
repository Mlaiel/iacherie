"""
Search Optimization Configuration - Enterprise Configuration Management  
Enterprise configuration for search optimization and analytics business logic

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    class BaseSettings:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        class Config:
            env_prefix = ""
            extra = "allow"
    def Field(**kwargs):
        return kwargs.get('default_factory', kwargs.get('default'))()


class SearchEngine(str, Enum):
    """Search engines"""
    GOOGLE = "google"
    BING = "bing" 
    YAHOO = "yahoo"
    DUCKDUCKGO = "duckduckgo"
    YANDEX = "yandex"
    BAIDU = "baidu"


class OptimizationStrategy(str, Enum):
    """SEO optimization strategies"""
    KEYWORD_OPTIMIZATION = "keyword_optimization"
    CONTENT_OPTIMIZATION = "content_optimization"
    TECHNICAL_SEO = "technical_seo"
    LOCAL_SEO = "local_seo"
    MOBILE_OPTIMIZATION = "mobile_optimization"
    VOICE_SEARCH = "voice_search"
    VIDEO_SEO = "video_seo"
    IMAGE_SEO = "image_seo"


@dataclass
class SearchEngineConfiguration:
    """Search engine configuration"""
    engine: SearchEngine
    enabled: bool
    api_credentials: Dict[str, str]
    ranking_factors: Dict[str, float]
    tracking_enabled: bool
    analytics_integration: bool


class SearchOptimizationSettings(BaseSettings):
    """Search optimization configuration settings"""
    
    # Search Engine Configurations
    search_engines: Dict[str, SearchEngineConfiguration] = Field(
        default_factory=lambda: {
            "google": SearchEngineConfiguration(
                engine=SearchEngine.GOOGLE,
                enabled=True,
                api_credentials={"search_console_key": "", "analytics_key": ""},
                ranking_factors={
                    "content_quality": 0.30,
                    "user_experience": 0.25,
                    "technical_seo": 0.20,
                    "backlinks": 0.15,
                    "mobile_optimization": 0.10
                },
                tracking_enabled=True,
                analytics_integration=True
            ),
            "bing": SearchEngineConfiguration(
                engine=SearchEngine.BING,
                enabled=True,
                api_credentials={"webmaster_key": ""},
                ranking_factors={
                    "content_relevance": 0.35,
                    "technical_optimization": 0.25,
                    "user_engagement": 0.20,
                    "social_signals": 0.20
                },
                tracking_enabled=True,
                analytics_integration=True
            )
        }
    )
    
    # Keyword Research & Analysis
    keyword_research: Dict[str, Any] = Field(
        default_factory=lambda: {
            "ai_powered_research": True,
            "competitor_analysis": True,
            "trending_keywords": True,
            "long_tail_optimization": True,
            "semantic_search": True,
            "intent_analysis": True,
            "difficulty_scoring": True,
            "opportunity_identification": True,
            "keyword_clustering": True,
            "content_gap_analysis": True
        }
    )
    
    # Content Optimization
    content_optimization: Dict[str, Any] = Field(
        default_factory=lambda: {
            "automated_optimization": True,
            "meta_tag_generation": True,
            "heading_optimization": True,
            "content_structure": True,
            "readability_analysis": True,
            "keyword_density": True,
            "internal_linking": True,
            "schema_markup": True,
            "featured_snippets": True,
            "content_freshness": True
        }
    )
    
    # Technical SEO
    technical_seo: Dict[str, Any] = Field(
        default_factory=lambda: {
            "site_speed_optimization": True,
            "mobile_optimization": True,
            "core_web_vitals": True,
            "crawlability": True,
            "indexability": True,
            "sitemap_optimization": True,
            "robots_txt_optimization": True,
            "canonical_urls": True,
            "ssl_optimization": True,
            "structured_data": True
        }
    )
    
    # Analytics & Tracking
    analytics_tracking: Dict[str, Any] = Field(
        default_factory=lambda: {
            "ranking_tracking": True,
            "traffic_analysis": True,
            "conversion_tracking": True,
            "competitor_monitoring": True,
            "backlink_analysis": True,
            "content_performance": True,
            "user_behavior": True,
            "search_console_integration": True,
            "custom_reporting": True,
            "predictive_analytics": True
        }
    )
    
    # Performance Monitoring
    performance_monitoring: Dict[str, Any] = Field(
        default_factory=lambda: {
            "real_time_monitoring": True,
            "automated_alerts": True,
            "ranking_changes": True,
            "traffic_anomalies": True,
            "technical_issues": True,
            "content_performance": True,
            "competitor_updates": True,
            "algorithm_updates": True
        }
    )
    
    class Config:
        env_prefix = "SEARCH_OPTIMIZATION_"
        case_sensitive = False
        extra = "allow"
    
    def validate_configuration(self) -> List[str]:
        """Validate search optimization configuration"""
        errors = []
        enabled_engines = [name for name, config in self.search_engines.items() if config.enabled]
        if not enabled_engines:
            errors.append("No search engines enabled")
        return errors


# Global search optimization settings instance
search_optimization_settings = SearchOptimizationSettings()

__all__ = [
    "SearchOptimizationSettings",
    "search_optimization_settings",
    "SearchEngine",
    "OptimizationStrategy", 
    "SearchEngineConfiguration"
]