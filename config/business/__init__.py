"""Ainflue Business Logic Configuration
====================================

Business logic configurations for creator management, content processing,
monetization, collaboration, gamification, SEO, and distribution.

Enterprise business configuration management for Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

# Business logic imports
from .creator_multi_format_config import CreatorMultiFormatConfiguration
from .creator_types_config import CreatorTypesConfiguration
from .creator_matching_config import CreatorMatchingConfiguration
from .content_format_config import ContentFormatConfiguration
from .content_ingestion_config import ContentIngestionConfiguration
from .monetization_business_config import MonetizationBusinessConfiguration
from .collaboration_business_config import CollaborationBusinessConfiguration
from .gamification_business_config import GamificationBusinessConfiguration
from .seo_business_config import SEOBusinessConfiguration
from .distribution_business_config import DistributionBusinessConfiguration
from .multi_platform_distribution_config import MultiPlatformDistributionConfiguration
from .search_optimization_config import SearchOptimizationConfiguration
from .achievement_engagement_config import AchievementEngagementConfiguration

logger = logging.getLogger(__name__)

class BusinessConfigurationLevel(str, Enum):
    """Business configuration levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    QUANTUM = "quantum"

class BusinessLogicConfigurationManager:
    """Business logic configuration manager"""
    
    def __init__(self, level -> None: BusinessConfigurationLevel = BusinessConfigurationLevel.ENTERPRISE) -> None:
        self.level = level
        self.configurations = {}
        self._initialize_business_configs()
    
    def _initialize_business_configs(self) -> None:
        """Initialize all business configurations"""
        self.configurations = {
            "creator_multi_format": CreatorMultiFormatConfiguration(level=self.level),
            "creator_types": CreatorTypesConfiguration(level=self.level),
            "creator_matching": CreatorMatchingConfiguration(level=self.level),
            "content_format": ContentFormatConfiguration(level=self.level),
            "content_ingestion": ContentIngestionConfiguration(level=self.level),
            "monetization": MonetizationBusinessConfiguration(level=self.level),
            "collaboration": CollaborationBusinessConfiguration(level=self.level),
            "gamification": GamificationBusinessConfiguration(level=self.level),
            "seo": SEOBusinessConfiguration(level=self.level),
            "distribution": DistributionBusinessConfiguration(level=self.level),
            "multi_platform_distribution": MultiPlatformDistributionConfiguration(level=self.level),
            "search_optimization": SearchOptimizationConfiguration(level=self.level),
            "achievement_engagement": AchievementEngagementConfiguration(level=self.level)
        }
        
        logger.info(f"💼 Business configurations initialized - Level: {self.level.value}")
    
    def get_config(self, config_name: str) -> Optional[Any]:
        """Get specific business configuration"""
        return self.configurations.get(config_name)
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Get all business configurations"""
        return self.configurations.copy()
    
    def get_creator_configs(self) -> Dict[str, Any]:
        """Get all creator-related configurations"""
        return {
            k: v for k, v in self.configurations.items() 
            if k.startswith("creator_")
        }
    
    def get_content_configs(self) -> Dict[str, Any]:
        """Get all content-related configurations"""
        return {
            k: v for k, v in self.configurations.items() 
            if k.startswith("content_")
        }
    
    def get_monetization_configs(self) -> Dict[str, Any]:
        """Get monetization and revenue configurations"""
        return {
            k: v for k, v in self.configurations.items() 
            if "monetization" in k or "revenue" in k
        }
    
    def get_distribution_configs(self) -> Dict[str, Any]:
        """Get distribution and platform configurations"""
        return {
            k: v for k, v in self.configurations.items() 
            if "distribution" in k or "platform" in k
        }

# Global business configuration manager
business_config_manager = BusinessLogicConfigurationManager()

# Module exports
__all__ = [
    "CreatorMultiFormatConfiguration",
    "CreatorTypesConfiguration",
    "CreatorMatchingConfiguration",
    "ContentFormatConfiguration",
    "ContentIngestionConfiguration",
    "MonetizationBusinessConfiguration",
    "CollaborationBusinessConfiguration",
    "GamificationBusinessConfiguration",
    "SEOBusinessConfiguration",
    "DistributionBusinessConfiguration",
    "MultiPlatformDistributionConfiguration",
    "SearchOptimizationConfiguration",
    "AchievementEngagementConfiguration",
    "BusinessLogicConfigurationManager",
    "BusinessConfigurationLevel",
    "business_config_manager"
]

logger.info("💼 Ainflue Business Logic Configuration Module loaded")
logger.info("⚠️ Protected by copyright - All Rights Reserved")
