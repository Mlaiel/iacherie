"""Professional Crawlers Module Index - IA-Influencer Platform

This index provides comprehensive access to all crawler components and utilities
for content monitoring, protection, and analytics across multiple platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 IA-Influencer Project. All rights reserved.

LEGAL WARNING: All intellectual property belongs exclusively to Fahed Mlaiel.
Unauthorized use will result in immediate legal action.
"""
from typing import Dict, Any, List, Type
import importlib
import logging

# Module information
MODULE_INFO = {
    "name": "crawlers",
    "version": "1.0.0",
    "description": "Professional web crawling and content monitoring system",
    "author": "Fahed Mlaiel",
    "email": "mlaiel@live.de",
    "license": "Proprietary - All Rights Reserved",
    "components": [
        "content_protection",
        "social_media", 
        "platform_analyzers",
        "web_scraping",
        "api_integrations",
        "dmca_enforcement"
    ]
}

# Available crawler classes
CRAWLER_CLASSES = {
    "ContentProtectionCrawler": "content_protection.ContentProtectionCrawler",
    "SocialMediaCrawler": "social_media.SocialMediaCrawler", 
    "PlatformAnalyzer": "platform_analyzers.PlatformAnalyzer",
    "WebScrapingEngine": "web_scraping.WebScrapingEngine",
    "APIIntegrationEngine": "api_integrations.APIIntegrationEngine",
    "DMCAEnforcementEngine": "dmca_enforcement.DMCAEnforcementEngine"
}

# Supported platforms
SUPPORTED_PLATFORMS = {
    "social_media": [
        "youtube", "instagram", "tiktok", "twitter", "facebook",
        "linkedin", "pinterest", "snapchat", "twitch", "discord",
        "reddit", "telegram"
    ],
    "apis": [
        "youtube_data_api", "instagram_business", "twitter_api_v2",
        "tiktok_business", "spotify_web_api", "facebook_graph",
        "linkedin_api", "pinterest_api", "twitch_helix"
    ],
    "dmca_policies": [
        "youtube_copyright", "instagram_ip", "tiktok_copyright",
        "twitter_copyright", "facebook_ip", "generic_dmca"
    ]
}

# Feature capabilities
FEATURE_MATRIX = {
    "content_protection": {
        "audio_fingerprinting": True,
        "video_fingerprinting": True,
        "image_fingerprinting": True,
        "text_fingerprinting": True,
        "similarity_detection": True,
        "dmca_automation": True,
        "evidence_collection": True
    },
    "social_media": {
        "profile_analysis": True,
        "content_extraction": True,
        "engagement_metrics": True,
        "follower_analytics": True,
        "hashtag_tracking": True,
        "trend_detection": True
    },
    "platform_analysis": {
        "competitor_intelligence": True,
        "market_analysis": True,
        "trend_forecasting": True,
        "audience_insights": True,
        "performance_benchmarking": True
    },
    "web_scraping": {
        "anti_detection": True,
        "proxy_rotation": True,
        "javascript_rendering": True,
        "content_extraction": True,
        "rate_limiting": True,
        "distributed_crawling": True
    },
    "api_integration": {
        "oauth_management": True,
        "rate_limit_handling": True,
        "data_normalization": True,
        "error_recovery": True,
        "batch_processing": True
    },
    "dmca_enforcement": {
        "notice_generation": True,
        "legal_templating": True,
        "platform_submission": True,
        "case_tracking": True,
        "evidence_packaging": True
    }
}


class CrawlerModuleIndex:
    """
    Index and registry for all crawler components.
    Provides centralized access to crawler classes and utilities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("crawlers.index")
        self._loaded_classes: Dict[str, Type] = {}
        self._configurations: Dict[str, Dict[str, Any]] = {}
    
    def get_module_info(self) -> Dict[str, Any]:
        """Get complete module information."""
        return {
            **MODULE_INFO,
            "supported_platforms": SUPPORTED_PLATFORMS,
            "feature_matrix": FEATURE_MATRIX,
            "available_classes": list(CRAWLER_CLASSES.keys())
        }
    
    def load_crawler_class(self, class_name: str) -> Type:
        """Dynamically load a crawler class."""
        if class_name in self._loaded_classes:
            return self._loaded_classes[class_name]
        
        if class_name not in CRAWLER_CLASSES:
            raise ValueError(f"Unknown crawler class: {class_name}")
        
        module_path = CRAWLER_CLASSES[class_name]
        module_name, class_attr = module_path.rsplit('.', 1)
        
        try:
            module = importlib.import_module(f"backend.app.crawlers.{module_name}")
            crawler_class = getattr(module, class_attr)
            self._loaded_classes[class_name] = crawler_class
            
            self.logger.info(f"Loaded crawler class: {class_name}")
            return crawler_class
            
        except Exception as e:
            self.logger.error(f"Failed to load crawler class {class_name}: {e}")
            raise ImportError(f"Could not load {class_name}: {e}")
    
    def get_supported_platforms(self, category: str = None) -> List[str]:
        """Get list of supported platforms."""
        if category:
            return SUPPORTED_PLATFORMS.get(category, [])
        return {k: v for k, v in SUPPORTED_PLATFORMS.items()}
    
    def get_feature_capabilities(self, component: str = None) -> Dict[str, Any]:
        """Get feature capabilities for components."""
        if component:
            return FEATURE_MATRIX.get(component, {})
        return FEATURE_MATRIX
    
    def validate_configuration(self, component: str, config: Dict[str, Any]) -> bool:
        """Validate configuration for a component."""
        try:
            # Basic validation - can be extended per component
            required_fields = {
                "content_protection": ["platforms", "fingerprinting_enabled"],
                "social_media": ["platforms", "api_credentials"],
                "platform_analyzers": ["analysis_depth", "platforms"],
                "web_scraping": ["strategy", "anti_detection_level"],
                "api_integrations": ["credentials", "rate_limits"],
                "dmca_enforcement": ["copyright_owner", "email_config"]
            }
            
            component_requirements = required_fields.get(component, [])
            
            for field in component_requirements:
                if field not in config:
                    self.logger.error(f"Missing required field '{field}' for {component}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed for {component}: {e}")
            return False
    
    def create_crawler_instance(
        self, 
        class_name: str, 
        config: Dict[str, Any] = None
    ) -> Any:
        """Create an instance of a crawler class with configuration."""
        try:
            crawler_class = self.load_crawler_class(class_name)
            
            if config:
                # Validate configuration
                component_name = class_name.lower().replace("crawler", "").replace("engine", "")
                if not self.validate_configuration(component_name, config):
                    self.logger.warning(f"Configuration validation failed for {class_name}")
            
            instance = crawler_class(config or {})
            self.logger.info(f"Created instance of {class_name}")
            
            return instance
            
        except Exception as e:
            self.logger.error(f"Failed to create instance of {class_name}: {e}")
            raise RuntimeError(f"Instance creation failed: {e}")
    
    def get_crawler_documentation(self, class_name: str) -> Dict[str, Any]:
        """Get documentation for a crawler class."""
        try:
            crawler_class = self.load_crawler_class(class_name)
            
            return {
                "name": class_name,
                "module": crawler_class.__module__,
                "docstring": crawler_class.__doc__,
                "methods": [
                    method for method in dir(crawler_class)
                    if not method.startswith('_') and callable(getattr(crawler_class, method))
                ],
                "capabilities": self.get_feature_capabilities(
                    class_name.lower().replace("crawler", "").replace("engine", "")
                )
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get documentation for {class_name}: {e}")
            return {"error": str(e)}


# Global index instance
crawler_index = CrawlerModuleIndex()

# Convenience functions
def list_crawlers() -> List[str]:
    """List all available crawler classes."""
    return list(CRAWLER_CLASSES.keys())

def get_crawler(class_name: str, config: Dict[str, Any] = None):
    """Get a crawler instance by name."""
    return crawler_index.create_crawler_instance(class_name, config)

def get_platforms(category: str = None) -> List[str]:
    """Get supported platforms."""
    return crawler_index.get_supported_platforms(category)

def get_features(component: str = None) -> Dict[str, Any]:
    """Get feature capabilities."""
    return crawler_index.get_feature_capabilities(component)

def module_info() -> Dict[str, Any]:
    """Get complete module information."""
    return crawler_index.get_module_info()


# Module initialization
if __name__ == "__main__":
    print("IA-Influencer Crawlers Module")
    print("="*50)
    print(f"Version: {MODULE_INFO['version']}")
    print(f"Author: {MODULE_INFO['author']}")
    print(f"Components: {', '.join(MODULE_INFO['components'])}")
    print(f"Available Crawlers: {', '.join(list_crawlers())}")
