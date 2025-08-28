"""
Platform Crawlers Index
=======================

Main entry point and orchestrator for platform crawlers module.
Provides unified interface for multi-platform content discovery and monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json

from . import (
    get_crawler_by_platform, 
    get_supported_platforms,
    get_platforms_by_category,
    PLATFORM_METADATA,
    SOCIAL_MEDIA_CRAWLERS,
    STREAMING_CRAWLERS,
    MUSIC_CRAWLERS,
    VIDEO_CRAWLERS,
    CONTENT_CRAWLERS
)

from ..utils.rate_limiter import GlobalRateLimiter
from ..utils.proxy_manager import ProxyManager
from ...core.config import get_settings
from ...core.exceptions import CrawlerError, PlatformNotSupportedError

logger = logging.getLogger(__name__)
settings = get_settings()

@dataclass
class CrawlerConfig:
    """Configuration for platform crawler."""
    platform: str
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    rate_limit: Optional[str] = None
    proxy_enabled: bool = False
    user_agent_rotation: bool = True
    delay_range: tuple = (1, 3)
    max_retries: int = 3
    timeout: int = 30
    batch_size: int = 50

@dataclass
class CrawlTask:
    """Individual crawling task configuration."""
    platform: str
    task_type: str  # search, profile, content, monitor
    query: str
    target_id: Optional[str] = None
    filters: Optional[Dict] = None
    limit: int = 100
    since: Optional[datetime] = None
    until: Optional[datetime] = None

@dataclass
class CrawlResult:
    """Unified crawl result structure."""
    platform: str
    task_type: str
    query: str
    total_results: int
    success: bool
    error_message: Optional[str] = None
    execution_time: float = 0.0
    data: List[Dict] = None
    metadata: Dict = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.data is None:
            self.data = []
        if self.metadata is None:
            self.metadata = {}

class PlatformCrawlerOrchestrator:
    """
    Orchestrates multiple platform crawlers for unified content discovery.
    Provides high-level interface for multi-platform monitoring and analysis.
    """
    
    def __init__(self, 
                 configs: Dict[str, CrawlerConfig] = None,
                 proxy_manager: ProxyManager = None,
                 rate_limiter: GlobalRateLimiter = None):
        """
        Initialize platform crawler orchestrator.
        
        Args:
            configs: Platform-specific configurations
            proxy_manager: Shared proxy manager instance
            rate_limiter: Global rate limiter instance
        """
        self.configs = configs or {}
        self.proxy_manager = proxy_manager or ProxyManager()
        self.rate_limiter = rate_limiter or GlobalRateLimiter()
        self.active_crawlers = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    async def initialize_crawler(self, platform: str, config: CrawlerConfig = None) -> Any:
        """
        Initialize crawler for specific platform.
        
        Args:
            platform: Platform name
            config: Platform-specific configuration
            
        Returns:
            Initialized crawler instance
            
        Raises:
            PlatformNotSupportedError: If platform is not supported
        """
        try:
            if platform not in get_supported_platforms():
                raise PlatformNotSupportedError(f"Platform '{platform}' is not supported")
            
            # Get configuration
            crawler_config = config or self.configs.get(platform, CrawlerConfig(platform=platform))
            
            # Get crawler class
            crawler_class = get_crawler_by_platform(platform)
            
            # Initialize crawler with configuration
            crawler_kwargs = {
                'proxy_manager': self.proxy_manager,
                'rate_limiter': self.rate_limiter,
            }
            
            # Add API credentials if available
            if crawler_config.api_key:
                crawler_kwargs['api_key'] = crawler_config.api_key
            if crawler_config.access_token:
                crawler_kwargs['access_token'] = crawler_config.access_token
                
            crawler = crawler_class(**crawler_kwargs)
            
            # Store active crawler
            self.active_crawlers[platform] = crawler
            
            self.logger.info(f"Initialized crawler for platform: {platform}")
            return crawler
            
        except Exception as e:
            self.logger.error(f"Failed to initialize crawler for {platform}: {str(e)}")
            raise CrawlerError(f"Crawler initialization failed: {str(e)}")
    
    async def execute_single_task(self, task: CrawlTask) -> CrawlResult:
        """
        Execute single crawling task.
        
        Args:
            task: Crawling task configuration
            
        Returns:
            Crawl result with data and metadata
        """
        start_time = datetime.utcnow()
        
        try:
            # Initialize crawler if needed
            if task.platform not in self.active_crawlers:
                await self.initialize_crawler(task.platform)
            
            crawler = self.active_crawlers[task.platform]
            
            # Execute task based on type
            if task.task_type == 'search':
                data = await self._execute_search(crawler, task)
            elif task.task_type == 'profile':
                data = await self._execute_profile(crawler, task)
            elif task.task_type == 'content':
                data = await self._execute_content(crawler, task)
            elif task.task_type == 'monitor':
                data = await self._execute_monitor(crawler, task)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Create result
            result = CrawlResult(
                platform=task.platform,
                task_type=task.task_type,
                query=task.query,
                total_results=len(data),
                success=True,
                execution_time=execution_time,
                data=data,
                metadata={
                    'filters': task.filters,
                    'limit': task.limit,
                    'since': task.since.isoformat() if task.since else None,
                    'until': task.until.isoformat() if task.until else None,
                }
            )
            
            self.logger.info(f"Task completed: {task.platform}/{task.task_type} - {len(data)} results")
            return result
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = str(e)
            
            self.logger.error(f"Task failed: {task.platform}/{task.task_type} - {error_msg}")
            
            return CrawlResult(
                platform=task.platform,
                task_type=task.task_type,
                query=task.query,
                total_results=0,
                success=False,
                error_message=error_msg,
                execution_time=execution_time
            )
    
    async def execute_batch_tasks(self, tasks: List[CrawlTask], 
                                 concurrent_limit: int = 5) -> List[CrawlResult]:
        """
        Execute multiple crawling tasks concurrently.
        
        Args:
            tasks: List of crawling tasks
            concurrent_limit: Maximum concurrent tasks
            
        Returns:
            List of crawl results
        """
        self.logger.info(f"Executing batch of {len(tasks)} tasks with limit {concurrent_limit}")
        
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def execute_with_semaphore(task):
            async with semaphore:
                return await self.execute_single_task(task)
        
        results = await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                task = tasks[i]
                final_results.append(CrawlResult(
                    platform=task.platform,
                    task_type=task.task_type,
                    query=task.query,
                    total_results=0,
                    success=False,
                    error_message=str(result)
                ))
            else:
                final_results.append(result)
        
        success_count = sum(1 for r in final_results if r.success)
        self.logger.info(f"Batch completed: {success_count}/{len(tasks)} successful")
        
        return final_results
    
    async def monitor_platforms(self, 
                               queries: List[str],
                               platforms: List[str] = None,
                               interval: int = 300,
                               duration: int = 3600) -> AsyncGenerator[List[CrawlResult], None]:
        """
        Continuous monitoring across multiple platforms.
        
        Args:
            queries: Search queries to monitor
            platforms: Platforms to monitor (default: all supported)
            interval: Monitoring interval in seconds
            duration: Total monitoring duration in seconds
            
        Yields:
            List of crawl results for each monitoring cycle
        """
        if platforms is None:
            platforms = get_supported_platforms()
        
        self.logger.info(f"Starting monitoring: {len(queries)} queries across {len(platforms)} platforms")
        
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(seconds=duration)
        
        while datetime.utcnow() < end_time:
            cycle_start = datetime.utcnow()
            
            # Create tasks for this monitoring cycle
            tasks = []
            for query in queries:
                for platform in platforms:
                    tasks.append(CrawlTask(
                        platform=platform,
                        task_type='search',
                        query=query,
                        limit=50,
                        since=cycle_start - timedelta(seconds=interval)
                    ))
            
            # Execute monitoring tasks
            results = await self.execute_batch_tasks(tasks)
            
            self.logger.info(f"Monitoring cycle completed: {len(results)} results")
            yield results
            
            # Wait for next cycle
            cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
            sleep_time = max(0, interval - cycle_duration)
            
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
    
    async def _execute_search(self, crawler, task: CrawlTask) -> List[Dict]:
        """Execute search task on crawler."""
        if hasattr(crawler, 'search_content'):
            return await crawler.search_content(
                query=task.query,
                limit=task.limit,
                filters=task.filters or {}
            )
        else:
            # Fallback: Try generic search if available
            if hasattr(crawler, 'search'):
                self.logger.warning(f"Using fallback search for {task.platform}")
                return await crawler.search(task.query, limit=task.limit)
            else:
                self.logger.warning(
                    f"Search not implemented for {task.platform}. "
                    f"Crawler {crawler.__class__.__name__} must implement either "
                    f"'search_content' or 'search' method."
                )
                # Return empty result with information instead of raising error
                return [{
                    "status": "not_implemented",
                    "platform": task.platform,
                    "message": f"Search functionality not available for {task.platform}",
                    "crawler_class": crawler.__class__.__name__,
                    "required_methods": ["search_content", "search"],
                    "query": task.query,
                    "timestamp": datetime.utcnow().isoformat()
                }]
    
    async def _execute_profile(self, crawler, task: CrawlTask) -> List[Dict]:
        """Execute profile task on crawler."""
        if hasattr(crawler, 'get_profile_data'):
            return await crawler.get_profile_data(
                profile_id=task.target_id or task.query
            )
        else:
            # Fallback: Try generic profile method if available
            if hasattr(crawler, 'get_profile'):
                self.logger.warning(f"Using fallback profile method for {task.platform}")
                return await crawler.get_profile(task.target_id or task.query)
            else:
                self.logger.warning(
                    f"Profile crawling not implemented for {task.platform}. "
                    f"Crawler {crawler.__class__.__name__} must implement either "
                    f"'get_profile_data' or 'get_profile' method."
                )
                # Return empty result with information instead of raising error
                return [{
                    "status": "not_implemented",
                    "platform": task.platform,
                    "message": f"Profile crawling functionality not available for {task.platform}",
                    "crawler_class": crawler.__class__.__name__,
                    "required_methods": ["get_profile_data", "get_profile"],
                    "profile_id": task.target_id or task.query,
                    "timestamp": datetime.utcnow().isoformat()
                }]
    
    async def _execute_content(self, crawler, task: CrawlTask) -> List[Dict]:
        """Execute content task on crawler."""
        if hasattr(crawler, 'get_content_data'):
            return await crawler.get_content_data(
                content_id=task.target_id or task.query,
                content_type=task.filters.get('content_type') if task.filters else None
            )
        else:
            # Fallback: Try generic content method if available
            if hasattr(crawler, 'get_content'):
                self.logger.warning(f"Using fallback content method for {task.platform}")
                return await crawler.get_content(task.target_id or task.query)
            else:
                self.logger.warning(
                    f"Content crawling not implemented for {task.platform}. "
                    f"Crawler {crawler.__class__.__name__} must implement either "
                    f"'get_content_data' or 'get_content' method."
                )
                # Return empty result with information instead of raising error
                return [{
                    "status": "not_implemented",
                    "platform": task.platform,
                    "message": f"Content crawling functionality not available for {task.platform}",
                    "crawler_class": crawler.__class__.__name__,
                    "required_methods": ["get_content_data", "get_content"],
                    "content_id": task.target_id or task.query,
                    "content_type": task.filters.get('content_type') if task.filters else None,
                    "timestamp": datetime.utcnow().isoformat()
                }]
    
    async def _execute_monitor(self, crawler, task: CrawlTask) -> List[Dict]:
        """Execute monitoring task on crawler."""
        if hasattr(crawler, 'monitor_content'):
            return await crawler.monitor_content(
                query=task.query,
                since=task.since,
                until=task.until,
                filters=task.filters or {}
            )
        else:
            # Fallback to search for monitoring
            return await self._execute_search(crawler, task)
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Get statistics about supported platforms and active crawlers."""
        return {
            'total_platforms': len(get_supported_platforms()),
            'active_crawlers': len(self.active_crawlers),
            'platform_categories': {
                'social_media': len(SOCIAL_MEDIA_CRAWLERS),
                'streaming': len(STREAMING_CRAWLERS),
                'music': len(MUSIC_CRAWLERS),
                'video': len(VIDEO_CRAWLERS),
                'content': len(CONTENT_CRAWLERS),
            },
            'supported_platforms': get_supported_platforms(),
            'active_platforms': list(self.active_crawlers.keys())
        }
    
    async def cleanup(self):
        """Cleanup resources and close active crawlers."""
        self.logger.info("Cleaning up platform crawlers")
        
        for platform, crawler in self.active_crawlers.items():
            try:
                if hasattr(crawler, 'close'):
                    await crawler.close()
            except Exception as e:
                self.logger.warning(f"Failed to close crawler for {platform}: {str(e)}")
        
        self.active_crawlers.clear()

# Convenience functions for common operations
async def search_across_platforms(query: str, 
                                 platforms: List[str] = None,
                                 limit: int = 50) -> Dict[str, CrawlResult]:
    """
    Search for content across multiple platforms.
    
    Args:
        query: Search query
        platforms: List of platforms to search (default: all)
        limit: Results limit per platform
        
    Returns:
        Dictionary mapping platform to crawl results
    """
    if platforms is None:
        platforms = get_platforms_by_category('social')
    
    orchestrator = PlatformCrawlerOrchestrator()
    
    try:
        tasks = [
            CrawlTask(platform=platform, task_type='search', query=query, limit=limit)
            for platform in platforms
        ]
        
        results = await orchestrator.execute_batch_tasks(tasks)
        
        return {result.platform: result for result in results}
        
    finally:
        await orchestrator.cleanup()

async def monitor_content_violations(content_fingerprint: str,
                                   platforms: List[str] = None,
                                   monitoring_duration: int = 3600) -> List[CrawlResult]:
    """
    Monitor platforms for potential content violations.
    
    Args:
        content_fingerprint: Content identifier/fingerprint to monitor
        platforms: Platforms to monitor (default: major platforms)
        monitoring_duration: Monitoring duration in seconds
        
    Returns:
        List of potential violation results
    """
    if platforms is None:
        platforms = ['youtube', 'instagram', 'tiktok', 'twitter', 'facebook']
    
    orchestrator = PlatformCrawlerOrchestrator()
    violations = []
    
    try:
        async for results in orchestrator.monitor_platforms(
            queries=[content_fingerprint],
            platforms=platforms,
            interval=300,  # Check every 5 minutes
            duration=monitoring_duration
        ):
            # Filter results that might indicate violations
            for result in results:
                if result.success and result.total_results > 0:
                    violations.extend(result.data)
        
        return violations
        
    finally:
        await orchestrator.cleanup()

if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        # Search example
        results = await search_across_platforms("music copyright", platforms=['youtube', 'spotify'])
        for platform, result in results.items():
            print(f"{platform}: {result.total_results} results, Success: {result.success}")
    
    asyncio.run(main())
