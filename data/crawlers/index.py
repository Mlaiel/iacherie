"""Crawlers Module Index - Easy Access Point
========================================

Simplified access point for the professional web crawling system.
Provides quick initialization and common usage patterns.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is proprietary and confidential. Any unauthorized use, 
reproduction, or distribution is strictly prohibited and may result in 
severe legal consequences.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any

from . import (
    CrawlerManager, CrawlerConfig, CrawlerPriority, ScheduleType,
    YouTubeCrawler, InstagramCrawler, TikTokCrawler, GenericWebCrawler,
    PlatformCrawler, ContentMatch, CrawlerResult
)


class CrawlerFactory:
    """    Factory class for easy crawler initialization and management.
    Simplifies the process of setting up and using crawlers.
    """    
    def __init__(self, vector_matcher, logger: Optional[logging.Logger] = None):
        """        Initialize crawler factory.
        
        Args:
            vector_matcher: Vector matching service instance
            logger: Optional logger instance
        """        self.vector_matcher = vector_matcher
        self.logger = logger or logging.getLogger(__name__)
        self.manager = None
        self.default_configs = self._get_default_configs()
    
    async def initialize_manager(self, max_concurrent_crawlers: int = 5) -> CrawlerManager:
        """        Initialize and return crawler manager.
        
        Args:
            max_concurrent_crawlers: Maximum number of concurrent crawlers
            
        Returns:
            Initialized CrawlerManager instance
        """        if not self.manager:
            self.manager = CrawlerManager(self.vector_matcher, max_concurrent_crawlers)
            await self.manager.initialize()
            
            # Register default configurations
            for crawler_type, config in self.default_configs.items():
                self.manager.register_crawler_config(crawler_type, config)
            
            self.logger.info("Crawler manager initialized with default configurations")
        
        return self.manager
    
    async def quick_search(self, 
                          search_terms: List[str],
                          platforms: List[str] = None,
                          similarity_threshold: float = 0.8,
                          max_results_per_platform: int = 50) -> Dict[str, List[Dict[str, Any]]]:
        """        Quick search across platforms with minimal configuration.
        
        Args:
            search_terms: Terms to search for
            platforms: List of platforms (default: all available)
            similarity_threshold: Minimum similarity threshold
            max_results_per_platform: Maximum results per platform
            
        Returns:
            Dictionary of results per platform
        """        try:
            # Initialize manager if needed
            if not self.manager:
                await self.initialize_manager()
            
            # Prepare fingerprint data
            fingerprint_data = {
                'search_terms': search_terms,
                'similarity_threshold': similarity_threshold
            }
            
            # Default platforms if not specified
            if platforms is None:
                platforms = ['youtube', 'instagram', 'tiktok', 'web']
            
            # Perform search
            results = await self.manager.search_across_platforms(
                fingerprint_data=fingerprint_data,
                platforms=platforms,
                max_results_per_platform=max_results_per_platform
            )
            
            self.logger.info(f"Quick search completed for terms: {search_terms}")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in quick search: {str(e)}")
            return {}
    
    async def setup_monitoring(self,
                             fingerprint_data: Dict[str, Any],
                             platforms: List[str],
                             interval_minutes: int = 60,
                             similarity_threshold: float = 0.85,
                             callback_url: Optional[str] = None) -> List[str]:
        """        Set up continuous monitoring for content across platforms.
        
        Args:
            fingerprint_data: Fingerprint data to monitor for
            platforms: List of platforms to monitor
            interval_minutes: Monitoring interval in minutes
            similarity_threshold: Minimum similarity threshold
            callback_url: Optional callback URL for notifications
            
        Returns:
            List of created task IDs
        """        try:
            # Initialize manager if needed
            if not self.manager:
                await self.initialize_manager()
            
            task_ids = []
            
            for platform in platforms:
                task_id = await self.manager.create_crawler_task(
                    crawler_type=platform,
                    fingerprint_data=fingerprint_data,
                    search_config={
                        'search_terms': fingerprint_data.get('search_terms', []),
                        'similarity_threshold': similarity_threshold,
                        'max_results': 100,
                        'interval_minutes': interval_minutes
                    },
                    schedule_config={
                        'type': 'interval',
                        'interval_minutes': interval_minutes
                    },
                    priority=CrawlerPriority.NORMAL,
                    callback_url=callback_url,
                    tags=['monitoring', 'continuous']
                )
                
                task_ids.append(task_id)
                self.logger.info(f"Created monitoring task for {platform}: {task_id}")
            
            return task_ids
            
        except Exception as e:
            self.logger.error(f"Error setting up monitoring: {str(e)}")
            return []
    
    async def create_single_crawler(self, 
                                  crawler_type: str,
                                  config_overrides: Dict[str, Any] = None) -> PlatformCrawler:
        """        Create a single crawler instance with custom configuration.
        
        Args:
            crawler_type: Type of crawler (youtube, instagram, tiktok, web)
            config_overrides: Optional configuration overrides
            
        Returns:
            Configured crawler instance
        """        try:
            # Merge default config with overrides
            base_config = self.default_configs.get(crawler_type, {})
            if config_overrides:
                base_config.update(config_overrides)
            
            # Create crawler config
            crawler_config = CrawlerConfig(
                platform_name=crawler_type,
                search_terms=[],
                similarity_threshold=0.8,
                max_results_per_search=100,
                crawl_interval_minutes=60,
                respect_robots_txt=base_config.get('respect_robots_txt', True),
                rate_limit_delay=base_config.get('rate_limit_delay', 1.0),
                user_agent=base_config.get('user_agent', 'IA-Influencer-Agent/1.0'),
                timeout_seconds=base_config.get('timeout_seconds', 30),
                retry_attempts=base_config.get('retry_attempts', 3)
            )
            
            # Create specific crawler instance
            if crawler_type == 'youtube':
                api_key = base_config.get('api_key')
                if not api_key:
                    raise ValueError("YouTube API key is required")
                return YouTubeCrawler(crawler_config, self.vector_matcher, api_key)
            
            elif crawler_type == 'instagram':
                access_token = base_config.get('access_token')
                app_secret = base_config.get('app_secret')
                return InstagramCrawler(crawler_config, self.vector_matcher, access_token, app_secret)
            
            elif crawler_type == 'tiktok':
                return TikTokCrawler(crawler_config, self.vector_matcher)
            
            elif crawler_type == 'web':
                return GenericWebCrawler(crawler_config, self.vector_matcher)
            
            else:
                raise ValueError(f"Unknown crawler type: {crawler_type}")
                
        except Exception as e:
            self.logger.error(f"Error creating crawler {crawler_type}: {str(e)}")
            raise
    
    def _get_default_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get default configurations for all crawler types"""        return {
            'youtube': {
                'api_key': None,  # Must be provided
                'quota_limit': 10000,
                'rate_limit_delay': 1.0,
                'respect_robots_txt': True,
                'timeout_seconds': 30,
                'retry_attempts': 3,
                'user_agent': 'IA-Influencer-Agent/1.0'
            },
            'instagram': {
                'access_token': None,  # Optional
                'app_secret': None,  # Optional
                'rate_limit_delay': 2.0,
                'respect_robots_txt': True,
                'timeout_seconds': 45,
                'retry_attempts': 3,
                'user_agent': 'IA-Influencer-Agent/1.0'
            },
            'tiktok': {
                'rate_limit_delay': 3.0,
                'respect_robots_txt': True,
                'timeout_seconds': 60,
                'retry_attempts': 3,
                'user_agent': 'IA-Influencer-Agent/1.0'
            },
            'web': {
                'rate_limit_delay': 1.0,
                'respect_robots_txt': True,
                'timeout_seconds': 30,
                'retry_attempts': 3,
                'user_agent': 'IA-Influencer-Agent/1.0',
                'max_file_size': 50 * 1024 * 1024,  # 50MB
                'max_concurrent_requests': 10
            }
        }
    
    async def get_manager_status(self) -> Dict[str, Any]:
        """Get current status of crawler manager"""        if not self.manager:
            return {'status': 'not_initialized'}
        
        return {
            'status': 'active',
            'metrics': self.manager.get_metrics(),
            'tasks': await self.manager.get_all_tasks_status()
        }
    
    async def cleanup(self):
        """Cleanup resources"""        if self.manager:
            await self.manager.shutdown()
            self.manager = None
            self.logger.info("Crawler factory cleaned up")


# Convenience functions for quick usage
async def quick_search(search_terms: List[str],
                      vector_matcher,
                      platforms: List[str] = None,
                      max_results_per_platform: int = 50) -> Dict[str, List[Dict[str, Any]]]:
    """    Quick convenience function for simple searches.
    
    Args:
        search_terms: Terms to search for
        vector_matcher: Vector matching service
        platforms: Platforms to search (default: all)
        max_results_per_platform: Max results per platform
        
    Returns:
        Search results dictionary
    """    factory = CrawlerFactory(vector_matcher)
    try:
        return await factory.quick_search(search_terms, platforms, max_results_per_platform=max_results_per_platform)
    finally:
        await factory.cleanup()


async def setup_content_monitoring(fingerprint_data: Dict[str, Any],
                                 vector_matcher,
                                 platforms: List[str],
                                 interval_minutes: int = 60,
                                 callback_url: Optional[str] = None) -> List[str]:
    """    Quick convenience function for setting up monitoring.
    
    Args:
        fingerprint_data: Content fingerprint data
        vector_matcher: Vector matching service
        platforms: Platforms to monitor
        interval_minutes: Monitoring interval
        callback_url: Optional webhook URL
        
    Returns:
        List of created monitoring task IDs
    """    factory = CrawlerFactory(vector_matcher)
    try:
        return await factory.setup_monitoring(
            fingerprint_data=fingerprint_data,
            platforms=platforms,
            interval_minutes=interval_minutes,
            callback_url=callback_url
        )
    except Exception as e:
        await factory.cleanup()
        raise


# Export main classes and functions
__all__ = [
    'CrawlerFactory',
    'quick_search',
    'setup_content_monitoring'
]
