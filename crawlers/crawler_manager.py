"""
Crawler Manager
Orchestration and management system for all platform crawlers.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .youtube_crawler import YouTubeCrawler
from .tiktok_crawler import TikTokCrawler
from .instagram_crawler import InstagramCrawler
from .twitter_crawler import TwitterCrawler
from .generic_web_crawler import GenericWebCrawler
# Music Platform Crawlers
from .spotify_crawler import SpotifyCrawler
from .apple_music_crawler import AppleMusicCrawler
from .soundcloud_crawler import SoundCloudCrawler
from .deezer_crawler import DeezerCrawler
from .youtube_music_crawler import YouTubeMusicCrawler
# Emerging Platform Crawlers
from .bereal_crawler import BeRealCrawler
from .twitch_crawler import TwitchCrawler
from .threads_crawler import ThreadsCrawler
# Social Platform Crawlers
from .reddit_crawler import RedditCrawler
from .discord_crawler import DiscordCrawler
from .facebook_crawler import FacebookCrawler
# Monetization Platform Crawlers
from .patreon_crawler import PatreonCrawler
from .substack_crawler import SubstackCrawler

logger = logging.getLogger(__name__)


class CrawlerStatus(Enum):
    """Crawler status"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"


@dataclass
class CrawlerJob:
    """Crawler job definition"""
    id: str
    crawler_type: str
    content_id: str
    fingerprint: str
    schedule: str  # cron-like schedule
    priority: int = 1
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: CrawlerStatus = CrawlerStatus.IDLE


@dataclass
class CrawlerResult:
    """Aggregated crawler result"""
    job_id: str
    crawler_type: str
    content_id: str
    violations_found: int
    total_scanned: int
    execution_time: float
    timestamp: datetime
    status: str = "completed"


class CrawlerManager:
    """Central management system for all crawlers"""
    
    def __init__(self):
        self.crawlers = {}
        self.jobs = {}
        self.results = {}
        self.running = False
        
    async def initialize_crawlers(self, config: Dict[str, Any]):
        """Initialize all crawler instances"""
        try:
            # Initialize YouTube crawler
            if config.get("youtube", {}).get("api_key"):
                self.crawlers["youtube"] = YouTubeCrawler(
                    api_key=config["youtube"]["api_key"]
                )
                
            # Initialize TikTok crawler
            if config.get("tiktok", {}).get("enabled", False):
                self.crawlers["tiktok"] = TikTokCrawler()
                
            # Initialize Instagram crawler
            if config.get("instagram", {}).get("enabled", False):
                self.crawlers["instagram"] = InstagramCrawler()
                
            # Initialize Twitter crawler
            if config.get("twitter", {}).get("enabled", False):
                self.crawlers["twitter"] = TwitterCrawler()
                
            # Initialize generic crawler
            self.crawlers["generic"] = GenericWebCrawler()
            
            # Initialize Music Platform Crawlers
            if config.get("spotify", {}).get("enabled", False):
                self.crawlers["spotify"] = SpotifyCrawler()
                
            if config.get("apple_music", {}).get("enabled", False):
                self.crawlers["apple_music"] = AppleMusicCrawler()
                
            if config.get("soundcloud", {}).get("enabled", False):
                self.crawlers["soundcloud"] = SoundCloudCrawler()
                
            if config.get("deezer", {}).get("enabled", False):
                self.crawlers["deezer"] = DeezerCrawler()
                
            if config.get("youtube_music", {}).get("enabled", False):
                self.crawlers["youtube_music"] = YouTubeMusicCrawler()
            
            # Initialize Emerging Platform Crawlers
            if config.get("bereal", {}).get("enabled", False):
                self.crawlers["bereal"] = BeRealCrawler()
                
            if config.get("twitch", {}).get("enabled", False):
                self.crawlers["twitch"] = TwitchCrawler()
                
            if config.get("threads", {}).get("enabled", False):
                self.crawlers["threads"] = ThreadsCrawler()
            
            # Initialize Social Platform Crawlers
            if config.get("reddit", {}).get("enabled", False):
                self.crawlers["reddit"] = RedditCrawler()
                
            if config.get("discord", {}).get("enabled", False):
                self.crawlers["discord"] = DiscordCrawler()
                
            if config.get("facebook", {}).get("enabled", False):
                self.crawlers["facebook"] = FacebookCrawler()
            
            # Initialize Monetization Platform Crawlers
            if config.get("patreon", {}).get("enabled", False):
                self.crawlers["patreon"] = PatreonCrawler()
                
            if config.get("substack", {}).get("enabled", False):
                self.crawlers["substack"] = SubstackCrawler()
            
            logger.info(f"Initialized {len(self.crawlers)} crawlers")
            
        except Exception as e:
            logger.error(f"Error initializing crawlers: {str(e)}")
            raise
    
    async def schedule_monitoring_job(
        self,
        content_id: str,
        fingerprint: str,
        platforms: List[str],
        schedule: str = "0 */6 * * *",  # Every 6 hours
        priority: int = 1
    ) -> List[str]:
        """Schedule monitoring jobs for content across platforms"""
        try:
            job_ids = []
            
            for platform in platforms:
                if platform not in self.crawlers:
                    logger.warning(f"Crawler not available for platform: {platform}")
                    continue
                    
                job_id = f"{content_id}_{platform}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                job = CrawlerJob(
                    id=job_id,
                    crawler_type=platform,
                    content_id=content_id,
                    fingerprint=fingerprint,
                    schedule=schedule,
                    priority=priority,
                    next_run=self._calculate_next_run(schedule)
                )
                
                self.jobs[job_id] = job
                job_ids.append(job_id)
            
            logger.info(f"Scheduled {len(job_ids)} monitoring jobs for content {content_id}")
            return job_ids
            
        except Exception as e:
            logger.error(f"Error scheduling monitoring jobs: {str(e)}")
            return []
    
    async def run_immediate_scan(
        self,
        content_id: str,
        fingerprint: str,
        platforms: List[str]
    ) -> Dict[str, CrawlerResult]:
        """Run immediate scan across specified platforms"""
        try:
            results = {}
            tasks = []
            
            for platform in platforms:
                if platform not in self.crawlers:
                    continue
                    
                task = self._execute_crawler_job(
                    platform, content_id, fingerprint
                )
                tasks.append((platform, task))
            
            # Execute all crawlers concurrently
            for platform, task in tasks:
                try:
                    result = await task
                    results[platform] = result
                except Exception as e:
                    logger.error(f"Error in {platform} crawler: {str(e)}")
                    results[platform] = CrawlerResult(
                        job_id=f"immediate_{platform}",
                        crawler_type=platform,
                        content_id=content_id,
                        violations_found=0,
                        total_scanned=0,
                        execution_time=0.0,
                        timestamp=datetime.now(),
                        status="error"
                    )
            
            logger.info(f"Immediate scan completed for content {content_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error running immediate scan: {str(e)}")
            return {}
    
    async def start_scheduler(self):
        """Start the job scheduler"""
        try:
            self.running = True
            logger.info("Crawler scheduler started")
            
            while self.running:
                current_time = datetime.now()
                
                # Check for jobs that need to run
                for job_id, job in self.jobs.items():
                    if (job.enabled and 
                        job.status == CrawlerStatus.IDLE and
                        job.next_run and 
                        current_time >= job.next_run):
                        
                        # Execute job
                        asyncio.create_task(
                            self._execute_scheduled_job(job)
                        )
                
                # Sleep for a short interval
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"Error in scheduler: {str(e)}")
        finally:
            self.running = False
    
    async def stop_scheduler(self):
        """Stop the job scheduler"""
        self.running = False
        logger.info("Crawler scheduler stopped")
    
    async def _execute_scheduled_job(self, job: CrawlerJob):
        """Execute a scheduled crawler job"""
        try:
            job.status = CrawlerStatus.RUNNING
            job.last_run = datetime.now()
            
            result = await self._execute_crawler_job(
                job.crawler_type,
                job.content_id,
                job.fingerprint
            )
            
            result.job_id = job.id
            self.results[job.id] = result
            
            # Schedule next run
            job.next_run = self._calculate_next_run(job.schedule)
            job.status = CrawlerStatus.IDLE
            
            logger.info(f"Job {job.id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error executing job {job.id}: {str(e)}")
            job.status = CrawlerStatus.ERROR
    
    async def _execute_crawler_job(
        self,
        crawler_type: str,
        content_id: str,
        fingerprint: str
    ) -> CrawlerResult:
        """Execute specific crawler job"""
        try:
            start_time = datetime.now()
            crawler = self.crawlers.get(crawler_type)
            
            if not crawler:
                raise ValueError(f"Crawler not found: {crawler_type}")
            
            violations = []
            total_scanned = 0
            
            if crawler_type == "youtube":
                async with crawler:
                    violations = await crawler.search_by_audio_fingerprint(
                        fingerprint, content_id, similarity_threshold=0.8
                    )
                    total_scanned = len(violations)
                    
            elif crawler_type == "tiktok":
                violations = await crawler.search_by_audio(fingerprint, content_id)
                total_scanned = len(violations)
                
            elif crawler_type == "instagram":
                violations = await crawler.search_content(content_id, fingerprint)
                total_scanned = len(violations)
                
            elif crawler_type == "twitter":
                violations = await crawler.search_media_content(content_id)
                total_scanned = len(violations)
                
            elif crawler_type == "generic":
                violations = await crawler.crawl_websites(fingerprint)
                total_scanned = len(violations)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Filter for actual violations (high similarity)
            actual_violations = [v for v in violations if getattr(v, 'similarity_score', 0) >= 0.8]
            
            return CrawlerResult(
                job_id="",  # Will be set by caller
                crawler_type=crawler_type,
                content_id=content_id,
                violations_found=len(actual_violations),
                total_scanned=total_scanned,
                execution_time=execution_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error executing {crawler_type} crawler: {str(e)}")
            return CrawlerResult(
                job_id="",
                crawler_type=crawler_type,
                content_id=content_id,
                violations_found=0,
                total_scanned=0,
                execution_time=0.0,
                timestamp=datetime.now(),
                status="error"
            )
    
    def _calculate_next_run(self, schedule: str) -> datetime:
        """Calculate next run time from cron-like schedule"""
        try:
            # Simplified cron parsing - in production use proper cron library
            # Format: minute hour day month dayofweek
            # Example: "0 */6 * * *" = every 6 hours
            
            if "*/6" in schedule:
                return datetime.now() + timedelta(hours=6)
            elif "*/4" in schedule:
                return datetime.now() + timedelta(hours=4)
            elif "*/2" in schedule:
                return datetime.now() + timedelta(hours=2)
            elif "*/1" in schedule:
                return datetime.now() + timedelta(hours=1)
            else:
                return datetime.now() + timedelta(hours=24)  # Default daily
                
        except Exception as e:
            logger.error(f"Error calculating next run: {str(e)}")
            return datetime.now() + timedelta(hours=24)
    
    async def get_job_status(self, job_id: str) -> Optional[CrawlerJob]:
        """Get status of specific job"""
        return self.jobs.get(job_id)
    
    async def get_recent_results(
        self,
        content_id: Optional[str] = None,
        hours: int = 24
    ) -> List[CrawlerResult]:
        """Get recent crawler results"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            results = []
            for result in self.results.values():
                if result.timestamp >= cutoff_time:
                    if not content_id or result.content_id == content_id:
                        results.append(result)
            
            # Sort by timestamp descending
            results.sort(key=lambda x: x.timestamp, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting recent results: {str(e)}")
            return []
    
    async def pause_job(self, job_id: str) -> bool:
        """Pause a scheduled job"""
        try:
            job = self.jobs.get(job_id)
            if job:
                job.enabled = False
                job.status = CrawlerStatus.PAUSED
                logger.info(f"Job {job_id} paused")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error pausing job: {str(e)}")
            return False
    
    async def resume_job(self, job_id: str) -> bool:
        """Resume a paused job"""
        try:
            job = self.jobs.get(job_id)
            if job:
                job.enabled = True
                job.status = CrawlerStatus.IDLE
                job.next_run = self._calculate_next_run(job.schedule)
                logger.info(f"Job {job_id} resumed")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error resuming job: {str(e)}")
            return False
    
    async def get_crawler_statistics(self) -> Dict[str, Any]:
        """Get overall crawler statistics"""
        try:
            stats = {
                "total_jobs": len(self.jobs),
                "active_jobs": len([j for j in self.jobs.values() if j.enabled]),
                "total_crawlers": len(self.crawlers),
                "recent_scans": len(self.get_recent_results()),
                "total_violations_found": sum(r.violations_found for r in self.results.values()),
                "total_content_scanned": sum(r.total_scanned for r in self.results.values()),
                "crawler_status": {
                    name: "available" if crawler else "unavailable"
                    for name, crawler in self.crawlers.items()
                }
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting crawler statistics: {str(e)}")
            return {}