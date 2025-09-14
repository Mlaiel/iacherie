"""
SEO Business Configuration - Enterprise Configuration Management
Enterprise configuration for SEO business logic and optimization systems

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
Licensed under proprietary license - reproduction forbidden without written authorization.
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for environments without pydantic_settings
    class BaseSettings:
    """BaseSettings: class implementation"""
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)


class SEOStrategy(str, Enum):
    """SEO optimization strategies"""
    CONTENT_DRIVEN = "content_driven"
    TECHNICAL_SEO = "technical_seo"
    LOCAL_SEO = "local_seo"
    VOICE_SEARCH = "voice_search"
    MOBILE_FIRST = "mobile_first"
    SEMANTIC_SEO = "semantic_seo"
    VIDEO_SEO = "video_seo"
    IMAGE_SEO = "image_seo"


class SearchEngine(str, Enum):
    """Supported search engines"""
    GOOGLE = "google"
    BING = "bing"
    YAHOO = "yahoo"
    DUCKDUCKGO = "duckduckgo"
    YANDEX = "yandex"
    BAIDU = "baidu"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"


class ContentType(str, Enum):
    """Content types for SEO optimization"""
    ARTICLE = "article"
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    PODCAST = "podcast"
    INFOGRAPHIC = "infographic"
    TUTORIAL = "tutorial"
    REVIEW = "review"


class OptimizationLevel(str, Enum):
    """SEO optimization levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    EXPERT = "expert"
    AI_POWERED = "ai_powered"


@dataclass
class KeywordStrategy:
    """Keyword research and targeting strategy"""
    primary_keywords: List[str]
    secondary_keywords: List[str]
    long_tail_keywords: List[str]
    keyword_difficulty: Dict[str, float]
    search_volume: Dict[str, int]
    competition_level: Dict[str, str]
    intent_mapping: Dict[str, str]


@dataclass
class ContentOptimization:
    """Content optimization configuration"""
    title_optimization: Dict[str, Any]
    meta_description: Dict[str, Any]
    header_structure: Dict[str, Any]
    keyword_density: Dict[str, float]
    content_length: Dict[str, int]
    readability_score: float
    semantic_keywords: List[str]


@dataclass
class TechnicalSEO:
    """Technical SEO configuration"""
    page_speed_target: float
    mobile_optimization: bool
    structured_data: List[str]
    sitemap_generation: bool
    robots_txt_optimization: bool
    canonical_urls: bool
    ssl_certificate: bool
    core_web_vitals: Dict[str, float]


@dataclass
class SEOAnalytics:
    """SEO analytics and tracking configuration"""
    tracking_tools: List[str]
    kpi_metrics: List[str]
    reporting_frequency: str
    competitor_tracking: bool
    rank_tracking: bool
    backlink_monitoring: bool
    traffic_analysis: bool


class SEOBusinessSettings:
    """SEO business configuration settings"""
    
    def __init__(self) -> None:
        # SEO Strategies by Content Type
        self.seo_strategies = {
            ContentType.ARTICLE: {
                "primary_strategy": SEOStrategy.CONTENT_DRIVEN,
                "secondary_strategies": [SEOStrategy.SEMANTIC_SEO, SEOStrategy.TECHNICAL_SEO],
                "optimization_targets": {
                    "keyword_density": 2.0,
                    "content_length": 1500,
                    "readability_score": 60,
                    "header_count": 5,
                    "internal_links": 3,
                    "external_links": 2
                }
            },
            
            ContentType.VIDEO: {
                "primary_strategy": SEOStrategy.VIDEO_SEO,
                "secondary_strategies": [SEOStrategy.MOBILE_FIRST, SEOStrategy.VOICE_SEARCH],
                "optimization_targets": {
                    "title_length": 60,
                    "description_length": 125,
                    "tags_count": 10,
                    "thumbnail_optimization": True,
                    "transcript_inclusion": True,
                    "chapter_markers": True
                }
            },
            
            ContentType.IMAGE: {
                "primary_strategy": SEOStrategy.IMAGE_SEO,
                "secondary_strategies": [SEOStrategy.MOBILE_FIRST, SEOStrategy.TECHNICAL_SEO],
                "optimization_targets": {
                    "alt_text_length": 125,
                    "file_size_kb": 100,
                    "format_optimization": True,
                    "lazy_loading": True,
                    "responsive_images": True,
                    "structured_data": True
                }
            },
            
            ContentType.AUDIO: {
                "primary_strategy": SEOStrategy.VOICE_SEARCH,
                "secondary_strategies": [SEOStrategy.CONTENT_DRIVEN, SEOStrategy.SEMANTIC_SEO],
                "optimization_targets": {
                    "transcript_accuracy": 95,
                    "episode_descriptions": True,
                    "chapter_summaries": True,
                    "keyword_tags": 15,
                    "podcast_schema": True
                }
            }
        }
        
        # Keyword Research Configuration
        self.keyword_research = {
            "tools_integration": [
                "google_keyword_planner",
                "semrush",
                "ahrefs",
                "moz",
                "custom_ai_research"
            ],
            "research_parameters": {
                "minimum_search_volume": 100,
                "maximum_keyword_difficulty": 70,
                "language_targeting": ["en", "de", "fr", "es", "ar"],
                "location_targeting": "global",
                "device_targeting": ["desktop", "mobile", "tablet"]
            },
            "keyword_clustering": {
                "enabled": True,
                "clustering_method": "semantic_similarity",
                "cluster_size_limit": 20,
                "similarity_threshold": 0.8
            }
        }
        
        # Content Optimization Templates
        self.content_optimization_templates = {
            "blog_post": ContentOptimization(
                title_optimization={
                    "target_length": 60,
                    "keyword_placement": "beginning",
                    "power_words": True,
                    "emotional_triggers": True
                },
                meta_description={
                    "target_length": 155,
                    "call_to_action": True,
                    "keyword_inclusion": True,
                    "unique_selling_point": True
                },
                header_structure={
                    "h1_count": 1,
                    "h2_count": 3,
                    "h3_count": 5,
                    "keyword_in_headers": True
                },
                keyword_density={
                    "primary_keyword": 1.5,
                    "secondary_keywords": 0.8,
                    "lsi_keywords": 0.5
                },
                content_length={
                    "minimum_words": 1000,
                    "optimal_words": 2000,
                    "maximum_words": 4000
                },
                readability_score=65.0,
                semantic_keywords=[]
            ),
            
            "product_page": ContentOptimization(
                title_optimization={
                    "target_length": 55,
                    "product_name_first": True,
                    "brand_inclusion": True,
                    "model_number": True
                },
                meta_description={
                    "target_length": 150,
                    "price_mention": True,
                    "key_features": True,
                    "availability": True
                },
                header_structure={
                    "h1_count": 1,
                    "h2_count": 4,
                    "feature_headers": True,
                    "benefit_headers": True
                },
                keyword_density={
                    "product_keywords": 2.0,
                    "category_keywords": 1.0,
                    "brand_keywords": 0.8
                },
                content_length={
                    "minimum_words": 300,
                    "optimal_words": 800,
                    "maximum_words": 1500
                },
                readability_score=70.0,
                semantic_keywords=[]
            )
        }
        
        # Technical SEO Configuration
        self.technical_seo = TechnicalSEO(
            page_speed_target=3.0,  # seconds
            mobile_optimization=True,
            structured_data=[
                "organization",
                "person",
                "article",
                "product",
                "review",
                "event",
                "faq",
                "breadcrumb"
            ],
            sitemap_generation=True,
            robots_txt_optimization=True,
            canonical_urls=True,
            ssl_certificate=True,
            core_web_vitals={
                "largest_contentful_paint": 2.5,
                "first_input_delay": 100,
                "cumulative_layout_shift": 0.1
            }
        )
        
        # Search Engine Optimization Targets
        self.search_engine_targets = {
            SearchEngine.GOOGLE: {
                "priority": 1,
                "optimization_focus": [
                    "content_quality",
                    "user_experience",
                    "mobile_first",
                    "page_speed",
                    "expertise_authority_trust"
                ],
                "ranking_factors_weight": {
                    "content_relevance": 0.30,
                    "backlink_quality": 0.25,
                    "user_experience": 0.20,
                    "technical_seo": 0.15,
                    "social_signals": 0.10
                }
            },
            
            SearchEngine.YOUTUBE: {
                "priority": 2,
                "optimization_focus": [
                    "video_quality",
                    "engagement_metrics",
                    "watch_time",
                    "click_through_rate",
                    "subscriber_growth"
                ],
                "ranking_factors_weight": {
                    "watch_time": 0.35,
                    "engagement": 0.25,
                    "click_through_rate": 0.20,
                    "video_quality": 0.15,
                    "keyword_relevance": 0.05
                }
            },
            
            SearchEngine.BING: {
                "priority": 3,
                "optimization_focus": [
                    "social_signals",
                    "exact_match_domains",
                    "multimedia_content",
                    "local_optimization"
                ],
                "ranking_factors_weight": {
                    "social_signals": 0.25,
                    "content_quality": 0.25,
                    "backlinks": 0.20,
                    "technical_seo": 0.15,
                    "user_engagement": 0.15
                }
            }
        }
        
        # AI-Powered SEO Features
        self.ai_seo_features = {
            "content_generation": {
                "enabled": True,
                "models": ["gpt-4", "claude-3.5"],
                "generation_types": [
                    "meta_descriptions",
                    "title_tags",
                    "alt_text",
                    "schema_markup",
                    "content_outlines"
                ]
            },
            "keyword_research": {
                "enabled": True,
                "semantic_analysis": True,
                "intent_prediction": True,
                "opportunity_detection": True,
                "competitor_analysis": True
            },
            "content_optimization": {
                "enabled": True,
                "real_time_suggestions": True,
                "readability_improvement": True,
                "semantic_enhancement": True,
                "structure_optimization": True
            }
        }
        
        # Performance Monitoring
        self.performance_monitoring = {
            "tracking_tools": [
                "google_analytics",
                "google_search_console",
                "semrush",
                "ahrefs",
                "custom_analytics"
            ],
            "key_metrics": [
                "organic_traffic",
                "keyword_rankings",
                "click_through_rate",
                "bounce_rate",
                "conversion_rate",
                "page_speed",
                "mobile_usability"
            ],
            "reporting_schedule": {
                "daily": ["traffic", "rankings"],
                "weekly": ["performance_summary", "keyword_changes"],
                "monthly": ["comprehensive_report", "competitor_analysis"],
                "quarterly": ["strategy_review", "roi_analysis"]
            }
        }
        
        # Local SEO Configuration
        self.local_seo = {
            "google_my_business": {
                "optimization_enabled": True,
                "automatic_posting": True,
                "review_management": True,
                "photo_optimization": True
            },
            "local_citations": {
                "directory_submissions": True,
                "citation_monitoring": True,
                "consistency_checking": True,
                "local_schema_markup": True
            },
            "location_targeting": {
                "geo_modifiers": True,
                "local_keywords": True,
                "proximity_optimization": True,
                "local_content_creation": True
            }
        }
        
        # International SEO
        self.international_seo = {
            "multilingual_support": {
                "enabled": True,
                "languages": ["en", "de", "fr", "es", "ar", "zh", "ja"],
                "hreflang_implementation": True,
                "content_localization": True
            },
            "geo_targeting": {
                "country_targeting": True,
                "regional_optimization": True,
                "cultural_adaptation": True,
                "local_search_engines": True
            }
        }
        
        # Business Intelligence
        self.business_intelligence = {
            "roi_tracking": True,
            "conversion_attribution": True,
            "revenue_tracking": True,
            "cost_per_acquisition": True,
            "lifetime_value_calculation": True,
            "predictive_analytics": True
        }
    
    def get_strategy_for_content_type(self, content_type: ContentType) -> Optional[Dict[str, Any]]:
        """Get SEO strategy for content type"""
        return self.seo_strategies.get(content_type)
    
    def get_optimization_template(self, template_name: str) -> Optional[ContentOptimization]:
        """Get content optimization template"""
        return self.content_optimization_templates.get(template_name)
    
    def get_search_engine_config(self, search_engine: SearchEngine) -> Optional[Dict[str, Any]]:
        """Get configuration for specific search engine"""
        return self.search_engine_targets.get(search_engine)
    
    def calculate_seo_score(self, content_analysis: Dict[str, Any]) -> float:
        """Calculate SEO score based on content analysis"""
        score = 0.0
        weights = {
            "keyword_optimization": 0.25,
            "content_quality": 0.20,
            "technical_seo": 0.20,
            "user_experience": 0.15,
            "mobile_optimization": 0.10,
            "page_speed": 0.10
        }
        
        for factor, weight in weights.items():
            factor_score = content_analysis.get(factor, 0.5)
            score += factor_score * weight
        
        return min(score, 1.0)
    
    def generate_seo_recommendations(self, current_score: float, 
                                   content_type: ContentType) -> List[str]:
        """Generate SEO improvement recommendations"""
        recommendations = []
        
        if current_score < 0.7:
            recommendations.extend([
                "Improve keyword targeting and density",
                "Optimize title tags and meta descriptions",
                "Enhance content structure with proper headers",
                "Increase content length and depth"
            ])
        
        if current_score < 0.8:
            recommendations.extend([
                "Add more internal and external links",
                "Optimize images with alt text",
                "Improve page loading speed",
                "Enhance mobile responsiveness"
            ])
        
        strategy = self.get_strategy_for_content_type(content_type)
        if strategy:
            recommendations.append(f"Focus on {strategy['primary_strategy']} optimization")
        
        return recommendations
    
    def validate_configuration(self) -> List[str]:
        """Validate the complete SEO configuration"""
        errors = []
        
        # Validate SEO strategies
        for content_type, strategy in self.seo_strategies.items():
            if "optimization_targets" not in strategy:
                errors.append(f"Missing optimization targets for content type '{content_type}'")
        
        # Validate search engine configurations
        for engine, config in self.search_engine_targets.items():
            weights = config.get("ranking_factors_weight", {})
            total_weight = sum(weights.values())
            if abs(total_weight - 1.0) > 0.01:
                errors.append(f"Ranking factor weights don't sum to 1.0 for '{engine}'")
        
        # Validate technical SEO settings
        if self.technical_seo.page_speed_target <= 0:
            errors.append("Invalid page speed target")
        
        if not self.technical_seo.structured_data:
            errors.append("No structured data types configured")
        
        return errors


# Global SEO business settings instance
seo_business_settings = SEOBusinessSettings()

__all__ = [
    "SEOBusinessSettings",
    "seo_business_settings",
    "SEOStrategy",
    "SearchEngine",
    "ContentType",
    "OptimizationLevel",
    "KeywordStrategy",
    "ContentOptimization",
    "TechnicalSEO",
    "SEOAnalytics"
]