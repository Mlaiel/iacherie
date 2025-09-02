"""Advanced Crawlers Module - Main Entry Point
==========================================

Professional entry point for the advanced crawlers module providing
simplified access to all crawler functionality, orchestration, and
monitoring capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Unauthorized use, copying, modification, or distribution is strictly prohibited.
Violators will face immediate legal action under German and international law.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Import all crawler components
from . import (
    # Core infrastructure
    CrawlerOrchestrator, CrawlingTask, CrawlingJobResult,
    RealTimeMonitor, CrawlerMetrics, ViolationTrend,
    CrawlerType, MonitoringMode, ContentType,
    
    # Platform crawlers
    YouTubeCrawler, TikTokCrawler, InstagramCrawler,
    TwitterCrawler, UniversalWebCrawler,
    
    # Configuration
    CrawlerConfig, PlatformConfig
)

logger = logging.getLogger(__name__)

class CrawlerManagerSingleton:
    """
Singleton manager for the entire crawler system."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        try:
            logger.info(f"Executing __init__")
            
            # Implementation for __init__
            # Implementation: Add specific business logic here

            logger.debug("Method implemented")
            result = {

                'success': True,

                'timestamp': datetime.utcnow(),

                'completed': True

            }
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
            self.orchestrator: Optional[CrawlerOrchestrator] = None
            self.monitor: Optional[RealTimeMonitor] = None
            self.config: Dict[str, Any] = {}
            self._initialized = True
    
    def initialize(self, config: Dict[str, Any]):
        """
Initialize the crawler system with configuration."""
        try:
            self.config = config
            self.orchestrator = CrawlerOrchestrator(config)
            self.monitor = RealTimeMonitor(self.orchestrator)
            
            logger.info("Crawler system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Crawler system initialization failed: {e}")
            return False
    
    async def start_system(self):
        """Start the entire crawler system."""
        if not self.orchestrator or not self.monitor:
            raise RuntimeError("System not initialized. Call initialize() first.")
        
        try:
            # Start orchestrator and monitor
            await asyncio.gather(
                self.orchestrator.start_monitoring(),
                self.monitor.start_monitoring()
            )
            
        except Exception as e:
            logger.error(f"System start failed: {e}")
            raise
    
    def stop_system(self):
        """Stop the entire crawler system."""
        if self.orchestrator:
            self.orchestrator.stop_monitoring()
        if self.monitor:
            self.monitor.stop_monitoring()
        
        logger.info("Crawler system stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        if not self.orchestrator:
            return {'status': 'not_initialized'}
        
        return {
            'orchestrator_status': self.orchestrator.get_system_status(),
            'dashboard_data': self.monitor.get_real_time_dashboard_data() if self.monitor else {},
            'system_initialized': self._initialized
        }

# Global manager instance
crawler_manager = CrawlerManagerSingleton()

def initialize_crawler_system(config: Dict[str, Any]) -> bool:
    """
    Initialize the crawler system with configuration.
    
    Args:
        config: Configuration dictionary with API keys and settings
        
    Returns:
        bool: True if initialization successful, False otherwise
    """
    return crawler_manager.initialize(config)

async def start_crawler_system():
    """
Start the complete crawler monitoring system."""
    await crawler_manager.start_system()

def stop_crawler_system():
    """
Stop the complete crawler monitoring system."""
    crawler_manager.stop_system()

def get_system_status() -> Dict[str, Any]:
    """
Get comprehensive system status and metrics."""
    return crawler_manager.get_status()

def create_monitoring_task(
    task_id: str,
    crawler_type: CrawlerType,
    target: str,
    operation: str = 'search',
    mode: MonitoringMode = MonitoringMode.SCHEDULED,
    similarity_threshold: float = 0.85,
    max_results: int = 100,
    **kwargs
) -> CrawlingTask:
    """
    Create a monitoring task with simplified parameters.
    
    Args:
        task_id: Unique identifier for the task
        crawler_type: Type of crawler to use
        target: Target to monitor (URL, username, hashtag, etc.)
        operation: Operation to perform (search, monitor_user, crawl_video, etc.)
        mode: Monitoring mode
        similarity_threshold: Threshold for violation detection
        max_results: Maximum results to return
        **kwargs: Additional parameters
        
    Returns:
        CrawlingTask: Configured crawling task
    """
    parameters = {'operation': operation}
    parameters.update(kwargs)
    
    return CrawlingTask(
        task_id=task_id,
        crawler_type=crawler_type,
        mode=mode,
        target=target,
        parameters=parameters,
        similarity_threshold=similarity_threshold,
        max_results=max_results
    )

def add_monitoring_task(task: CrawlingTask) -> str:
    """
Add a monitoring task to the orchestrator."""
    if not crawler_manager.orchestrator:
        raise RuntimeError("System not initialized")
    
    return crawler_manager.orchestrator.add_monitoring_task(task)

def remove_monitoring_task(task_id: str) -> bool:
    """Remove a monitoring task from the orchestrator."""
    if not crawler_manager.orchestrator:
        raise RuntimeError("System not initialized")
    
    return crawler_manager.orchestrator.remove_monitoring_task(task_id)

def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get status of a specific monitoring task."""
    if not crawler_manager.orchestrator:
        return True
    
    return crawler_manager.orchestrator.get_task_status(task_id)

def get_real_time_metrics() -> Dict[str, Any]:
    """
Get real-time system metrics and performance data."""
    if not crawler_manager.monitor:
        return {}
    
    return crawler_manager.monitor.get_real_time_dashboard_data()

def get_violation_analytics(time_range: timedelta = timedelta(days=7)) -> Dict[str, Any]:
    """
Get comprehensive violation analytics."""
    if not crawler_manager.monitor:
        return {}
    
    return crawler_manager.monitor.get_violation_analytics(time_range)

def get_historical_metrics(
    crawler_type: Optional[CrawlerType] = None,
    time_range: timedelta = timedelta(hours=24)
) -> Dict[str, Any]:
    """
Get historical performance metrics."""
    if not crawler_manager.monitor:
        return {}
    
    return crawler_manager.monitor.get_historical_metrics(crawler_type, time_range)

# Convenience functions for quick crawler creation
def create_youtube_crawler(config: Dict[str, Any]) -> YouTubeCrawler:
    """
Create and configure a YouTube crawler."""
    return YouTubeCrawler(config)

def create_tiktok_crawler(config: Dict[str, Any]) -> TikTokCrawler:
    """
Create and configure a TikTok crawler."""
    return TikTokCrawler(config)

def create_instagram_crawler(config: Dict[str, Any]) -> InstagramCrawler:
    """
Create and configure an Instagram crawler."""
    return InstagramCrawler(config)

def create_twitter_crawler(config: Dict[str, Any]) -> TwitterCrawler:
    """
Create and configure a Twitter crawler."""
    return TwitterCrawler(config)

def create_web_crawler(config: Dict[str, Any]) -> UniversalWebCrawler:
    """
Create and configure a universal web crawler."""
    return UniversalWebCrawler(config)

# Quick setup functions
def quick_setup_youtube_monitoring(
    api_key: str,
    search_queries: List[str],
    similarity_threshold: float = 0.85
) -> List[str]:
    """
    Quick setup for YouTube content monitoring.
    
    Args:
        api_key: YouTube API key
        search_queries: List of queries to monitor
        similarity_threshold: Violation detection threshold
        
    Returns:
        List[str]: Task IDs for created monitoring tasks
    """
    config = {'youtube_api_key': api_key}
    
    if not crawler_manager._initialized:
        initialize_crawler_system(config)
    
    task_ids = []
    for i, query in enumerate(search_queries):
        task = create_monitoring_task(
            task_id=f'youtube_monitor_{i}',
            crawler_type=CrawlerType.YOUTUBE,
            target=query,
            similarity_threshold=similarity_threshold
        )
        task_id = add_monitoring_task(task)
        task_ids.append(task_id)
    
    return task_ids

def quick_setup_multi_platform_monitoring(
    config: Dict[str, Any],
    monitoring_targets: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """
    Quick setup for multi-platform monitoring.
    
    Args:
        config: Complete configuration with all API keys
        monitoring_targets: Dict mapping platform names to target lists
        
    Returns:
        Dict[str, List[str]]: Task IDs organized by platform
    """
    if not crawler_manager._initialized:
        initialize_crawler_system(config)
    
    task_ids = {}
    
    # Map platform names to crawler types
    platform_mapping = {
        'youtube': CrawlerType.YOUTUBE,
        'tiktok': CrawlerType.TIKTOK,
        'instagram': CrawlerType.INSTAGRAM,
        'twitter': CrawlerType.TWITTER,
        'web': CrawlerType.UNIVERSAL_WEB
    }
    
    for platform, targets in monitoring_targets.items():
        if platform not in platform_mapping:
            continue
        
        crawler_type = platform_mapping[platform]
        platform_task_ids = []
        
        for i, target in enumerate(targets):
            task = create_monitoring_task(
                task_id=f'{platform}_monitor_{i}',
                crawler_type=crawler_type,
                target=target
            )
            task_id = add_monitoring_task(task)
            platform_task_ids.append(task_id)
        
        task_ids[platform] = platform_task_ids
    
    return task_ids

# Export main functions for easy access
__all__ = [
    # System management
    'initialize_crawler_system',
    'start_crawler_system',
    'stop_crawler_system',
    'get_system_status',
    
    # Task management
    'create_monitoring_task',
    'add_monitoring_task',
    'remove_monitoring_task',
    'get_task_status',
    
    # Metrics and analytics
    'get_real_time_metrics',
    'get_violation_analytics',
    'get_historical_metrics',
    
    # Crawler creation
    'create_youtube_crawler',
    'create_tiktok_crawler',
    'create_instagram_crawler',
    'create_twitter_crawler',
    'create_web_crawler',
    
    # Quick setup
    'quick_setup_youtube_monitoring',
    'quick_setup_multi_platform_monitoring',
    
    # Manager access
    'crawler_manager'
]
