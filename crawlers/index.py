"""Crawlers Module Index
====================

Central index for all crawler modules and intelligence engines.
Provides easy access to all crawling, intelligence, and collaboration features.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

from typing import Dict, List, Optional, Any, Type
import logging

# Core engines
from .content_intelligence import ContentIntelligenceEngine, create_content_intelligence_engine
from .trend_detection import TrendDetectionEngine, create_trend_detection_engine
from .collaboration_matching import CollaborationMatchingEngine, create_collaboration_matching_engine
from .orchestration_engine import OrchestrationEngine, create_orchestration_engine
from .revenue_intelligence import RevenueIntelligenceEngine, create_revenue_intelligence_engine

# Platform crawlers
from .platforms import *

# Managers and coordinators
from .crawler_manager import CrawlerManager

logger = logging.getLogger(__name__)

class CrawlerModuleIndex:
    """
    Central index for all crawler modules and intelligence engines.
    Provides factory methods and unified access to all crawling capabilities.
    """
    
    def __init__(self):
        self._engines = {}
        self._crawlers = {}
        self._initialized = False
    
    async def initialize(self):
        """
Initialize all engines and crawlers."""
        if self._initialized:
            return
        
        try:
            # Initialize intelligence engines
            self._engines['content_intelligence'] = create_content_intelligence_engine()
            self._engines['trend_detection'] = create_trend_detection_engine()
            self._engines['collaboration_matching'] = create_collaboration_matching_engine()
            self._engines['orchestration'] = create_orchestration_engine()
            self._engines['revenue_intelligence'] = create_revenue_intelligence_engine()
            
            # Initialize platform crawlers
            self._crawlers['youtube'] = YouTubeCrawler()
            self._crawlers['instagram'] = InstagramCrawler()
            self._crawlers['tiktok'] = TikTokCrawler()
            self._crawlers['twitter'] = TwitterCrawler()
            self._crawlers['facebook'] = FacebookCrawler()
            self._crawlers['spotify'] = SpotifyCrawler()
            
            self._initialized = True
            logger.info("Crawler module index initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize crawler module index: {e}")
            raise
    
    def get_content_intelligence_engine(self) -> ContentIntelligenceEngine:
        """Get content intelligence engine."""
        if not self._initialized:
            raise RuntimeError("Module index not initialized. Call initialize() first.")
        return self._engines['content_intelligence']
    
    def get_trend_detection_engine(self) -> TrendDetectionEngine:
        """Get trend detection engine."""
        if not self._initialized:
            raise RuntimeError("Module index not initialized. Call initialize() first.")
        return self._engines['trend_detection']
    
    def get_collaboration_matching_engine(self) -> CollaborationMatchingEngine:
        """Get collaboration matching engine."""
        if not self._initialized:
            raise RuntimeError("Module index not initialized. Call initialize() first.")
        return self._engines['collaboration_matching']
    
    def get_orchestration_engine(self) -> OrchestrationEngine:
        """Get orchestration engine."""
        if not self._initialized:
            raise RuntimeError("Module index not initialized. Call initialize() first.")
        return self._engines['orchestration']
    
    def get_revenue_intelligence_engine(self) -> RevenueIntelligenceEngine:
        """Get revenue intelligence engine."""
        if not self._initialized:
            raise RuntimeError("Module index not initialized. Call initialize() first.")
        return self._engines['revenue_intelligence']
    
    def get_platform_crawler(self, platform: str):
        """Get platform-specific crawler."""
        if not self._initialized:
            raise RuntimeError("Module index not initialized. Call initialize() first.")
        
        platform_lower = platform.lower()
        if platform_lower not in self._crawlers:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return self._crawlers[platform_lower]
    
    def get_all_engines(self) -> Dict[str, Any]:
        """Get all intelligence engines."""
        if not self._initialized:
            raise RuntimeError("Module index not initialized. Call initialize() first.")
        return self._engines.copy()
    
    def get_all_crawlers(self) -> Dict[str, Any]:
        """Get all platform crawlers."""
        if not self._initialized:
            raise RuntimeError("Module index not initialized. Call initialize() first.")
        return self._crawlers.copy()
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms."""
        return list(self._crawlers.keys()) if self._initialized else []
    
    def get_available_engines(self) -> List[str]:
        """
Get list of available intelligence engines."""
        return list(self._engines.keys()) if self._initialized else []

# Global module index instance
crawler_index = CrawlerModuleIndex()

# Convenience functions
async def initialize_crawlers():
    """
Initialize the global crawler index."""
    await crawler_index.initialize()

def get_content_intelligence() -> ContentIntelligenceEngine:
    """
Get content intelligence engine."""
    return crawler_index.get_content_intelligence_engine()

def get_trend_detection() -> TrendDetectionEngine:
    """
Get trend detection engine."""
    return crawler_index.get_trend_detection_engine()

def get_collaboration_matching() -> CollaborationMatchingEngine:
    """
Get collaboration matching engine."""
    return crawler_index.get_collaboration_matching_engine()

def get_orchestration() -> OrchestrationEngine:
    """
Get orchestration engine."""
    return crawler_index.get_orchestration_engine()

def get_revenue_intelligence() -> RevenueIntelligenceEngine:
    """
Get revenue intelligence engine."""
    return crawler_index.get_revenue_intelligence_engine()

def get_platform_crawler(platform: str):
    """
Get platform-specific crawler."""
    return crawler_index.get_platform_crawler(platform)

# Module exports
__all__ = [
    'CrawlerModuleIndex',
    'crawler_index',
    'initialize_crawlers',
    'get_content_intelligence',
    'get_trend_detection',
    'get_collaboration_matching',
    'get_orchestration',
    'get_revenue_intelligence',
    'get_platform_crawler',
    # Engine classes
    'ContentIntelligenceEngine',
    'TrendDetectionEngine',
    'CollaborationMatchingEngine',
    'OrchestrationEngine',
    'RevenueIntelligenceEngine',
    # Factory functions
    'create_content_intelligence_engine',
    'create_trend_detection_engine',
    'create_collaboration_matching_engine',
    'create_orchestration_engine',
    'create_revenue_intelligence_engine'
]
