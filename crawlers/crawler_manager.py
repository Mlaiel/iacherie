"""Crawler Manager
===============

Central manager for web crawlers and surveillance operations.
Coordinates multiple platform crawlers for comprehensive content monitoring.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .youtube_crawler import YouTubeCrawler
from .instagram_crawler import InstagramCrawler
from .tiktok_crawler import TikTokCrawler
from .twitter_crawler import TwitterCrawler
from .facebook_crawler import FacebookCrawler
from .generic_crawler import GenericWebCrawler
from .surveillance_engine import SurveillanceEngine
from ..database.repositories import CrawlRepository
from ..core.exceptions import CrawlerError
from ..utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class CrawlerStatus(Enum):
    """
Crawler status types."""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class SurveillanceMode(Enum):
    """Surveillance mode types."""

    REAL_TIME = "real_time"
    SCHEDULED = "scheduled"
    ON_DEMAND = "on_demand"

@dataclass
class CrawlResult:
    """Crawl result data structure."""
    platform: str
    query: str
    results: List[Dict]
    total_found: int
    crawl_duration: float
    timestamp: datetime
    metadata: Dict

@dataclass
class SurveillanceTask:
    """
Surveillance task data structure."""
    id: str
    content_id: int
    platforms: List[str]
    mode: SurveillanceMode
    status: CrawlerStatus
    created_at: datetime
    last_scan: Optional[datetime]
    next_scan: Optional[datetime]

class CrawlerManager:
    """
    Professional web crawler manager.
    
    Features:
    - Multi-platform crawler coordination
    - Rate limiting and quota management
    - Intelligent surveillance scheduling
    - Real-time content discovery
    - Violation detection integration
    - Performance monitoring
    - Error handling and recovery
    """
    
    def __init__(self):
        """
Initialize crawler manager."""
        # Initialize platform crawlers
        self.crawlers = {
            "youtube": YouTubeCrawler(),
            "instagram": InstagramCrawler(),
            "tiktok": TikTokCrawler(),
            "twitter": TwitterCrawler(),
            "facebook": FacebookCrawler(),
            "generic": GenericWebCrawler()
        }
        
        # Surveillance engine
        self.surveillance_engine = SurveillanceEngine()
        
        # Repository
        self.crawl_repo = CrawlRepository()
        
        # Rate limiters for each platform
        self.rate_limiters = {
            platform: RateLimiter(max_requests=100, time_window=60)
            for platform in self.crawlers.keys()
        }
        
        # Configuration
        self.config = {
            "max_concurrent_crawls": 5,
            "default_timeout": 30,
            "retry_attempts": 3,
            "surveillance_interval": 300,  # 5 minutes
            "batch_size": 50
        }
        
        # Active surveillance tasks
        self.surveillance_tasks = {}
        
        # Crawler status tracking
        self.crawler_status = {
            platform: CrawlerStatus.IDLE for platform in self.crawlers.keys()
        }
        
        logger.info("CrawlerManager initialized successfully")
    
    async def search_platform_content(self, 
                                     platform: str,
                                     query: str,
                                     max_results: int = 50) -> CrawlResult:
        """
        Search for content on specific platform.
        
        Args:
            platform: Platform name (youtube, instagram, etc.)
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            CrawlResult object with search results
        """
        try:
            start_time = datetime.utcnow()
            
            logger.info(f"Searching {platform} for: {query}")
            
            # Validate platform
            if platform not in self.crawlers:
                raise CrawlerError(f"Unsupported platform: {platform}")
            
            # Check rate limit
            if not await self.rate_limiters[platform].acquire():
                raise CrawlerError(f"Rate limit exceeded for {platform}")
            
            # Update crawler status
            self.crawler_status[platform] = CrawlerStatus.RUNNING
            
            try:
                # Get platform crawler
                crawler = self.crawlers[platform]
                
                # Perform search
                results = await crawler.search_content(query, max_results)
                
                # Calculate duration
                duration = (datetime.utcnow() - start_time).total_seconds()
                
                # Create crawl result
                crawl_result = CrawlResult(
                    platform=platform,
                    query=query,
                    results=results,
                    total_found=len(results),
                    crawl_duration=duration,
                    timestamp=datetime.utcnow(),
                    metadata={
                        "max_results": max_results,
                        "crawler_version": crawler.get_version()
                    }
                )
                
                # Store crawl result
                await self.crawl_repo.store_crawl_result(crawl_result)
                
                # Update status
                self.crawler_status[platform] = CrawlerStatus.IDLE
                
                logger.info(f"Search completed: {len(results)} results in {duration:.2f}s")
                return crawl_result
                
            except Exception as e:
                self.crawler_status[platform] = CrawlerStatus.ERROR
                raise CrawlerError(f"Search failed on {platform}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error searching platform content: {str(e)}")
            raise CrawlerError(f"Failed to search platform content: {str(e)}")
    
    async def start_surveillance(self, 
                                content_id: int,
                                platforms: List[str] = None,
                                mode: SurveillanceMode = SurveillanceMode.REAL_TIME) -> str:
        """
        Start surveillance for content.
        
        Args:
            content_id: ID of content to monitor
            platforms: List of platforms to monitor (default: all)
            mode: Surveillance mode
            
        Returns:
            Surveillance task ID
        """
        try:
            logger.info(f"Starting surveillance for content {content_id}")
            
            # Use all platforms if none specified
            if platforms is None:
                platforms = list(self.crawlers.keys())
            
            # Validate platforms
            invalid_platforms = [p for p in platforms if p not in self.crawlers]
            if invalid_platforms:
                raise CrawlerError(f"Invalid platforms: {invalid_platforms}")
            
            # Generate task ID
            task_id = f"surveillance_{content_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Create surveillance task
            task = SurveillanceTask(
                id=task_id,
                content_id=content_id,
                platforms=platforms,
                mode=mode,
                status=CrawlerStatus.RUNNING,
                created_at=datetime.utcnow(),
                last_scan=None,
                next_scan=datetime.utcnow()
            )
            
            # Start surveillance loop
            surveillance_coroutine = asyncio.create_task(
                self._surveillance_loop(task)
            )
            
            self.surveillance_tasks[task_id] = {
                "task": task,
                "coroutine": surveillance_coroutine
            }
            
            logger.info(f"Surveillance started: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error starting surveillance: {str(e)}")
            raise CrawlerError(f"Failed to start surveillance: {str(e)}")
    
    async def stop_surveillance(self, task_id: str) -> bool:
        """Stop surveillance task."""
        try:
            if task_id in self.surveillance_tasks:
                task_info = self.surveillance_tasks[task_id]
                task_info["coroutine"].cancel()
                task_info["task"].status = CrawlerStatus.IDLE
                
                del self.surveillance_tasks[task_id]
                
                logger.info(f"Surveillance stopped: {task_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error stopping surveillance: {str(e)}")
            return False
    
    async def get_crawler(self, platform: str):
        """Get specific platform crawler."""
        if platform not in self.crawlers:
            raise CrawlerError(f"Crawler not found for platform: {platform}")
        
        return self.crawlers[platform]
    
    async def get_platform_status(self, platform: str) -> Dict:
        """Get platform crawler status and statistics."""
        try:
            if platform not in self.crawlers:
                return {"error": f"Platform not found: {platform}"}
            
            crawler = self.crawlers[platform]
            rate_limiter = self.rate_limiters[platform]
            
            # Get crawler statistics
            stats = await crawler.get_stats()
            
            status = {
                "platform": platform,
                "status": self.crawler_status[platform].value,
                "rate_limit": {
                    "remaining": rate_limiter.remaining_requests(),
                    "reset_time": rate_limiter.reset_time(),
                    "max_requests": rate_limiter.max_requests
                },
                "statistics": stats,
                "last_activity": stats.get("last_crawl_time"),
                "error_rate": stats.get("error_rate", 0.0),
                "success_rate": stats.get("success_rate", 100.0)
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting platform status: {str(e)}")
            return {"error": str(e)}
    
    async def get_surveillance_status(self) -> Dict:
        """Get overall surveillance status."""
        try:
            active_tasks = []
            
            for task_id, task_info in self.surveillance_tasks.items():
                task = task_info["task"]
                active_tasks.append({
                    "task_id": task_id,
                    "content_id": task.content_id,
                    "platforms": task.platforms,
                    "mode": task.mode.value,
                    "status": task.status.value,
                    "created_at": task.created_at.isoformat(),
                    "last_scan": task.last_scan.isoformat() if task.last_scan else None,
                    "next_scan": task.next_scan.isoformat() if task.next_scan else None
                })
            
            platform_status = {}
            for platform in self.crawlers.keys():
                platform_status[platform] = await self.get_platform_status(platform)
            
            return {
                "active_surveillance_tasks": len(active_tasks),
                "tasks": active_tasks,
                "platform_status": platform_status,
                "configuration": {
                    "max_concurrent_crawls": self.config["max_concurrent_crawls"],
                    "surveillance_interval": self.config["surveillance_interval"],
                    "supported_platforms": list(self.crawlers.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting surveillance status: {str(e)}")
            return {"error": str(e)}
    
    async def _surveillance_loop(self, task: SurveillanceTask):
        """Main surveillance loop for a task."""
        try:
            while task.status == CrawlerStatus.RUNNING:
                logger.debug(f"Surveillance scan for task {task.id}")
                
                # Update scan time
                task.last_scan = datetime.utcnow()
                
                # Get content information for search terms
                content_info = await self._get_content_info(task.content_id)
                search_terms = self._generate_search_terms(content_info)
                
                # Scan each platform
                for platform in task.platforms:
                    try:
                        await self._scan_platform_for_task(task, platform, search_terms)
                    except Exception as e:
                        logger.error(f"Error scanning {platform} for task {task.id}: {str(e)}")
                
                # Calculate next scan time based on mode
                if task.mode == SurveillanceMode.REAL_TIME:
                    task.next_scan = datetime.utcnow() + timedelta(seconds=self.config["surveillance_interval"])
                elif task.mode == SurveillanceMode.SCHEDULED:
                    task.next_scan = datetime.utcnow() + timedelta(hours=1)  # Hourly scans
                
                # Wait until next scan
                if task.next_scan:
                    wait_time = (task.next_scan - datetime.utcnow()).total_seconds()
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)
                
        except asyncio.CancelledError:
            logger.info(f"Surveillance task cancelled: {task.id}")
            task.status = CrawlerStatus.IDLE
        except Exception as e:
            logger.error(f"Error in surveillance loop for task {task.id}: {str(e)}")
            task.status = CrawlerStatus.ERROR
    
    async def _scan_platform_for_task(self, 
                                     task: SurveillanceTask,
                                     platform: str,
                                     search_terms: List[str]):
        """Scan specific platform for surveillance task."""
        try:
            # Check rate limit
            if not await self.rate_limiters[platform].acquire():
                logger.warning(f"Rate limit exceeded for {platform}, skipping scan")
                return
            
            # Perform searches for each term
            all_results = []
            
            for term in search_terms:
                try:
                    crawl_result = await self.search_platform_content(
                        platform, term, max_results=20
                    )
                    all_results.extend(crawl_result.results)
                except Exception as e:
                    logger.error(f"Error searching {platform} for term '{term}': {str(e)}")
            
            # Process results through surveillance engine
            if all_results:
                await self.surveillance_engine.analyze_results(
                    task.content_id, platform, all_results
                )
            
        except Exception as e:
            logger.error(f"Error scanning platform {platform} for task {task.id}: {str(e)}")
    
    async def _get_content_info(self, content_id: int) -> Dict:
        """Get content information for surveillance."""
        # This would typically fetch from content repository
        # For now, return mock data
        return {
            "id": content_id,
            "title": "Sample Content",
            "artist": "Sample Artist",
            "description": "Sample description",
            "filename": "sample_file.mp3"
        }
    
    def _generate_search_terms(self, content_info: Dict) -> List[str]:
        """Generate search terms from content information."""
        terms = []
        
        # Add title
        if "title" in content_info:
            terms.append(content_info["title"])
        
        # Add artist
        if "artist" in content_info:
            terms.append(content_info["artist"])
        
        # Add filename (without extension)
        if "filename" in content_info:
            filename = content_info["filename"]
            if "." in filename:
                filename = filename.rsplit(".", 1)[0]
            terms.append(filename)
        
        # Add combined terms
        if len(terms) >= 2:
            terms.append(f"{terms[0]} {terms[1]}")
        
        return terms[:5]  # Limit to 5 search terms
    
    async def batch_search(self, 
                          searches: List[Dict],
                          max_concurrent: int = None) -> List[CrawlResult]:
        """Perform batch searches across platforms."""
        try:
            if max_concurrent is None:
                max_concurrent = self.config["max_concurrent_crawls"]
            
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def search_with_semaphore(search_config):
        try:
            logger.info(f"Executing search_with_semaphore")
            
            # Implementation for search_with_semaphore
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"search_with_semaphore completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"search_with_semaphore failed: {e}")
            raise
                    return await self.search_platform_content(
                        search_config["platform"],
                        search_config["query"],
                        search_config.get("max_results", 50)
                    )
            
            # Execute searches concurrently
            tasks = [search_with_semaphore(search) for search in searches]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = [r for r in results if isinstance(r, CrawlResult)]
            
            logger.info(f"Batch search completed: {len(valid_results)}/{len(searches)} successful")
            return valid_results
            
        except Exception as e:
            logger.error(f"Error in batch search: {str(e)}")
            raise CrawlerError(f"Batch search failed: {str(e)}")
    
    def get_manager_stats(self) -> Dict:
        """Get crawler manager statistics."""
        return {
            "version": "1.0.0",
            "supported_platforms": list(self.crawlers.keys()),
            "active_surveillance_tasks": len(self.surveillance_tasks),
            "crawler_status": {
                platform: status.value for platform, status in self.crawler_status.items()
            },
            "configuration": self.config,
            "rate_limits": {
                platform: {
                    "remaining": limiter.remaining_requests(),
                    "max_requests": limiter.max_requests
                }
                for platform, limiter in self.rate_limiters.items()
            }
        }
