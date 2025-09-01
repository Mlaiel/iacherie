"""Content Crawling & Platform Monitoring Engine - IA Influencer Agent Platform
============================================================================

Industrial-grade web crawling system for automated content monitoring across 
social media platforms, content aggregators, and user-generated content sites.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

Expert Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ LEGAL WARNING: This code and concept are protected by intellectual property laws.
Any unauthorized copying, modification, or distribution without explicit written 
permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will 
result in legal action under German and international copyright laws.
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
from uuid import UUID, uuid4
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ...core.config import get_settings
from ...core.database import get_database
from ...core.exceptions import CrawlerError, PlatformAccessError
from ...core.logging import get_logger
from ...models.crawler import (
    CrawlJob, CrawlResult, PlatformContent, ContentMatch,
    CrawlerConfiguration, PlatformCredentials
)
from ...services.proxy_rotation import ProxyRotationService
from ...services.rate_limiter import RateLimiter
from ...utils.user_agent_rotation import UserAgentRotator
from ...utils.captcha_solver import CaptchaSolver
from .protection_engine import ContentProtectionEngine

logger = get_logger(__name__)
settings = get_settings()


class ContentCrawlerEngine:
    """
Industrial content crawler with anti-detection and platform integration."""
    
    def __init__(self):
        self.db = get_database()
        self.protection_engine = ContentProtectionEngine()
        self.proxy_service = ProxyRotationService()
        self.user_agent_rotator = UserAgentRotator()
        self.captcha_solver = CaptchaSolver()
        
        # Rate limiters for different platforms
        self.rate_limiters = {
            'youtube': RateLimiter(max_requests=100, time_window=3600),  # 100/hour
            'instagram': RateLimiter(max_requests=50, time_window=3600),   # 50/hour
            'tiktok': RateLimiter(max_requests=30, time_window=3600),      # 30/hour
            'twitter': RateLimiter(max_requests=150, time_window=900),     # 150/15min
            'facebook': RateLimiter(max_requests=25, time_window=3600),    # 25/hour
            'soundcloud': RateLimiter(max_requests=100, time_window=3600), # 100/hour
            'spotify': RateLimiter(max_requests=50, time_window=3600),     # 50/hour
            'twitch': RateLimiter(max_requests=75, time_window=3600),      # 75/hour
            'reddit': RateLimiter(max_requests=60, time_window=60),        # 60/minute
            'discord': RateLimiter(max_requests=50, time_window=60),       # 50/minute
            'default': RateLimiter(max_requests=20, time_window=3600)      # 20/hour
        }
        
        # Platform configurations
        self.platform_configs = {
            'youtube': {
                'api_enabled': True,
                'api_endpoints': {
                    'search': 'https://www.googleapis.com/youtube/v3/search',
                    'videos': 'https://www.googleapis.com/youtube/v3/videos'
                },
                'search_params': {
                    'part': 'snippet',
                    'type': 'video',
                    'maxResults': 50
                },
                'selectors': {
                    'video_title': 'h1.title',
                    'video_description': '#description',
                    'video_url': 'link[rel="canonical"]',
                    'channel_name': '.ytd-channel-name',
                    'view_count': '.view-count'
                },
                'requires_js': True,
                'anti_bot_measures': ['captcha', 'rate_limiting', 'ip_blocking']
            },
            'instagram': {
                'api_enabled': False,  # Requires business account
                'web_scraping_only': True,
                'selectors': {
                    'post_image': 'img[decoding="auto"]',
                    'post_video': 'video',
                    'post_caption': 'article h1',
                    'username': 'header a',
                    'likes_count': 'section button span',
                    'comments_count': 'a[href*="/comments/"]'
                },
                'requires_js': True,
                'requires_login': True,
                'anti_bot_measures': ['captcha', 'login_required', 'shadow_banning']
            },
            'tiktok': {
                'api_enabled': False,
                'web_scraping_only': True,
                'selectors': {
                    'video_title': '[data-e2e="browse-video-desc"]',
                    'video_url': 'link[rel="canonical"]',
                    'username': '[data-e2e="browse-username"]',
                    'likes_count': '[data-e2e="browse-like-count"]',
                    'video_thumbnail': 'video'
                },
                'requires_js': True,
                'requires_mobile_agent': True,
                'anti_bot_measures': ['captcha', 'region_blocking', 'dynamic_loading']
            },
            'twitter': {
                'api_enabled': True,
                'api_endpoints': {
                    'search': 'https://api.twitter.com/2/tweets/search/recent',
                    'users': 'https://api.twitter.com/2/users/by/username'
                },
                'search_params': {
                    'max_results': 100,
                    'tweet.fields': 'created_at,author_id,public_metrics'
                },
                'selectors': {
                    'tweet_text': '[data-testid="tweetText"]',
                    'username': '[data-testid="User-Names"]',
                    'media_content': '[data-testid="tweetPhoto"]'
                },
                'requires_js': True,
                'anti_bot_measures': ['rate_limiting', 'api_key_required']
            },
            'soundcloud': {
                'api_enabled': True,
                'api_endpoints': {
                    'search': 'https://api.soundcloud.com/tracks',
                    'resolve': 'https://api.soundcloud.com/resolve'
                },
                'selectors': {
                    'track_title': '.soundTitle__title',
                    'artist_name': '.soundTitle__username',
                    'play_count': '.sc-ministats-item'
                },
                'requires_js': False,
                'anti_bot_measures': ['rate_limiting']
            },
            'reddit': {
                'api_enabled': True,
                'api_endpoints': {
                    'search': 'https://www.reddit.com/search.json',
                    'subreddit': 'https://www.reddit.com/r/{subreddit}.json'
                },
                'selectors': {
                    'post_title': 'h3',
                    'post_content': '.usertext-body',
                    'username': '.author',
                    'score': '.score'
                },
                'requires_js': False,
                'anti_bot_measures': ['rate_limiting', 'user_agent_checking']
            }
        }
        
        # Active crawl jobs
        self.active_jobs = {}
        
        # Session management
        self.sessions = {}
        self.drivers = {}
        
        # Initialize components
        asyncio.create_task(self._initialize_crawler_components())
    
    async def start_monitoring_crawl(
        self,
        protection_id: UUID,
        crawl_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Start automated monitoring crawl for protected content.
        
        Args:
            protection_id: Content protection ID to monitor
            crawl_config: Crawling configuration
            
        Returns:
            Crawl job details and status
        """
        try:
            # Get protection record
            protection = await self.db.content_protection.get_by_id(protection_id)
            if not protection:
                raise CrawlerError("Protection record not found")
            
            # Generate crawl job ID
            crawl_job_id = uuid4()
            
            # Get content fingerprints for matching
            fingerprints = await self.protection_engine._get_fingerprints_from_vector_db(
                protection.fingerprint_ids, protection.content_type
            )
            
            # Configure crawl job
            job_config = {
                'job_id': crawl_job_id,
                'protection_id': protection_id,
                'content_type': protection.content_type,
                'fingerprints': fingerprints,
                'platforms_to_crawl': crawl_config.get('platforms', protection.platforms_to_monitor),
                'crawl_frequency': crawl_config.get('frequency', 'daily'),
                'search_terms': self._generate_search_terms(protection, crawl_config),
                'advanced_search': crawl_config.get('advanced_search', {}),
                'similarity_threshold': crawl_config.get('similarity_threshold', 0.85),
                'max_results_per_platform': crawl_config.get('max_results', 100),
                'deep_crawl_enabled': crawl_config.get('deep_crawl', False),
                'continuous_monitoring': crawl_config.get('continuous', True),
                'notification_settings': crawl_config.get('notifications', {}),
                'proxy_rotation': crawl_config.get('use_proxies', True),
                'stealth_mode': crawl_config.get('stealth_mode', True)
            }
            
            # Create crawl job record
            crawl_job_data = {
                'id': crawl_job_id,
                'protection_id': protection_id,
                'creator_id': protection.creator_id,
                'job_type': 'monitoring',
                'status': 'starting',
                'configuration': job_config,
                'platforms_configured': len(job_config['platforms_to_crawl']),
                'search_terms_count': len(job_config['search_terms']),
                'next_execution': self._calculate_next_execution(job_config['crawl_frequency']),
                'created_at': datetime.utcnow(),
                'metadata': {
                    'content_type': protection.content_type,
                    'fingerprints_count': len(fingerprints),
                    'estimated_daily_checks': self._estimate_daily_checks(job_config)
                }
            }
            
            crawl_job = await self.db.crawl_jobs.create(crawl_job_data)
            
            # Start crawl job execution
            self.active_jobs[crawl_job_id] = {
                'task': asyncio.create_task(self._execute_monitoring_crawl(crawl_job)),
                'status': 'running',
                'start_time': datetime.utcnow()
            }
            
            # Update job status
            await self.db.crawl_jobs.update_status(crawl_job_id, 'running')
            
            result = {
                'crawl_job_id': str(crawl_job_id),
                'protection_id': str(protection_id),
                'status': 'started',
                'platforms_to_monitor': job_config['platforms_to_crawl'],
                'search_terms_generated': len(job_config['search_terms']),
                'crawl_frequency': job_config['crawl_frequency'],
                'next_execution_time': crawl_job_data['next_execution'].isoformat(),
                'estimated_daily_content_checks': job_config['metadata']['estimated_daily_checks'],
                'monitoring_dashboard_url': f"/crawler/dashboard/{crawl_job_id}",
                'real_time_status_url': f"/crawler/status/{crawl_job_id}"
            }
            
            logger.info(f"Started monitoring crawl job: {crawl_job_id} for protection {protection_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to start monitoring crawl: {str(e)}")
            raise CrawlerError(f"Crawl job startup failed: {str(e)}")
    
    async def search_platform_content(
        self,
        platform: str,
        search_terms: List[str],
        search_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Search for content on specific platform.
        
        Args:
            platform: Platform to search
            search_terms: Terms to search for
            search_config: Search configuration
            
        Returns:
            Search results with content matches
        """
        try:
            if platform not in self.platform_configs:
                raise CrawlerError(f"Unsupported platform: {platform}")
            
            # Check rate limiting
            rate_limiter = self.rate_limiters.get(platform, self.rate_limiters['default'])
            if not await rate_limiter.can_proceed():
                wait_time = await rate_limiter.get_wait_time()
                raise CrawlerError(f"Rate limited for {platform}, wait {wait_time} seconds")
            
            # Get platform configuration
            platform_config = self.platform_configs[platform]
            search_results = []
            
            # Use API if available and enabled
            if platform_config.get('api_enabled', False):
                api_results = await self._search_platform_api(
                    platform, search_terms, search_config
                )
                search_results.extend(api_results)
            
            # Use web scraping as fallback or primary method
            if not search_results or search_config.get('web_scraping_enabled', True):
                scraping_results = await self._search_platform_web(
                    platform, search_terms, search_config
                )
                search_results.extend(scraping_results)
            
            # Remove duplicates
            unique_results = self._deduplicate_search_results(search_results)
            
            # Rate limiting record
            await rate_limiter.record_request()
            
            result = {
                'platform': platform,
                'search_terms': search_terms,
                'results_found': len(unique_results),
                'search_results': unique_results[:search_config.get('max_results', 50)],
                'search_metadata': {
                    'api_used': platform_config.get('api_enabled', False),
                    'web_scraping_used': True,
                    'deduplication_performed': len(search_results) != len(unique_results),
                    'search_timestamp': datetime.utcnow().isoformat()
                }
            }
            
            logger.info(f"Platform search completed: {platform}, found {len(unique_results)} results")
            return result
            
        except Exception as e:
            logger.error(f"Platform search failed for {platform}: {str(e)}")
            raise CrawlerError(f"Search failed: {str(e)}")
    
    async def analyze_content_matches(
        self,
        search_results: List[Dict[str, Any]],
        target_fingerprints: List[Dict[str, Any]],
        similarity_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Analyze search results for content matches using AI fingerprinting.
        
        Args:
            search_results: Content found during crawling
            target_fingerprints: Fingerprints to match against
            similarity_threshold: Minimum similarity for match
            
        Returns:
            Content match analysis results
        """
        try:
            matches = []
            potential_matches = []
            analysis_stats = {
                'total_content_analyzed': len(search_results),
                'fingerprint_comparisons': 0,
                'processing_time_seconds': 0
            }
            
            start_time = datetime.utcnow()
            
            for content_item in search_results:
                try:
                    # Generate fingerprints for found content
                    content_fingerprints = await self._generate_content_fingerprints_from_url(
                        content_item['url'], content_item['content_type']
                    )
                    
                    if not content_fingerprints:
                        continue
                    
                    # Compare against target fingerprints
                    best_match_score = 0.0
                    best_match_fingerprint = None
                    
                    for target_fp in target_fingerprints:
                        for content_fp in content_fingerprints:
                            similarity = await self._calculate_fingerprint_similarity(
                                target_fp, content_fp
                            )
                            
                            analysis_stats['fingerprint_comparisons'] += 1
                            
                            if similarity > best_match_score:
                                best_match_score = similarity
                                best_match_fingerprint = content_fp
                    
                    # Classify match
                    if best_match_score >= similarity_threshold:
                        match_data = {
                            'content_url': content_item['url'],
                            'platform': content_item['platform'],
                            'content_type': content_item['content_type'],
                            'similarity_score': best_match_score,
                            'match_confidence': self._calculate_match_confidence(
                                best_match_score, content_item
                            ),
                            'content_metadata': content_item.get('metadata', {}),
                            'fingerprint_match': best_match_fingerprint,
                            'detected_at': datetime.utcnow().isoformat(),
                            'match_type': 'exact' if best_match_score >= 0.95 else 'similar'
                        }
                        matches.append(match_data)
                        
                    elif best_match_score >= similarity_threshold - 0.15:  # Potential matches
                        potential_match_data = {
                            'content_url': content_item['url'],
                            'platform': content_item['platform'],
                            'similarity_score': best_match_score,
                            'requires_manual_review': True,
                            'content_metadata': content_item.get('metadata', {}),
                            'detected_at': datetime.utcnow().isoformat()
                        }
                        potential_matches.append(potential_match_data)
                
                except Exception as e:
                    logger.error(f"Failed to analyze content item: {str(e)}")
                    continue
            
            # Calculate processing statistics
            end_time = datetime.utcnow()
            analysis_stats['processing_time_seconds'] = (end_time - start_time).total_seconds()
            
            # Rank matches by confidence
            matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            potential_matches.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            result = {
                'matches_found': len(matches),
                'potential_matches_found': len(potential_matches),
                'confirmed_matches': matches,
                'potential_matches': potential_matches,
                'analysis_statistics': analysis_stats,
                'match_summary': {
                    'exact_matches': len([m for m in matches if m['match_type'] == 'exact']),
                    'similar_matches': len([m for m in matches if m['match_type'] == 'similar']),
                    'highest_similarity_score': max([m['similarity_score'] for m in matches], default=0.0),
                    'average_similarity_score': sum([m['similarity_score'] for m in matches]) / len(matches) if matches else 0.0,
                    'platforms_with_matches': list(set([m['platform'] for m in matches]))
                }
            }
            
            logger.info(f"Content match analysis completed: {len(matches)} matches, {len(potential_matches)} potential")
            return result
            
        except Exception as e:
            logger.error(f"Content match analysis failed: {str(e)}")
            raise CrawlerError(f"Match analysis failed: {str(e)}")
    
    async def get_crawl_job_status(
        self,
        crawl_job_id: UUID
    ) -> Dict[str, Any]:
        """
        Get real-time status of crawl job.
        
        Args:
            crawl_job_id: Crawl job to check
            
        Returns:
            Detailed job status and statistics
        """
        try:
            # Get job from database
            crawl_job = await self.db.crawl_jobs.get_by_id(crawl_job_id)
            if not crawl_job:
                raise CrawlerError("Crawl job not found")
            
            # Get real-time status from active jobs
            active_status = self.active_jobs.get(crawl_job_id, {})
            
            # Get latest crawl results
            latest_results = await self.db.crawl_results.get_latest_by_job(
                crawl_job_id, limit=5
            )
            
            # Calculate statistics
            total_results = await self.db.crawl_results.count_by_job(crawl_job_id)
            total_matches = await self.db.content_matches.count_by_job(crawl_job_id)
            
            status = {
                'crawl_job_id': str(crawl_job_id),
                'status': active_status.get('status', crawl_job.status),
                'created_at': crawl_job.created_at.isoformat(),
                'last_execution': crawl_job.last_execution.isoformat() if crawl_job.last_execution else None,
                'next_execution': crawl_job.next_execution.isoformat() if crawl_job.next_execution else None,
                'execution_statistics': {
                    'total_executions': crawl_job.execution_count,
                    'successful_executions': crawl_job.successful_executions,
                    'failed_executions': crawl_job.failed_executions,
                    'total_content_crawled': total_results,
                    'total_matches_found': total_matches,
                    'average_execution_time': crawl_job.average_execution_time
                },
                'platform_statistics': await self._get_platform_statistics(crawl_job_id),
                'recent_activity': [
                    {
                        'execution_time': result.created_at.isoformat(),
                        'platform': result.platform,
                        'results_found': result.results_count,
                        'matches_found': result.matches_count,
                        'execution_duration': result.execution_duration
                    }
                    for result in latest_results
                ],
                'configuration': {
                    'crawl_frequency': crawl_job.configuration.get('crawl_frequency'),
                    'platforms_monitored': crawl_job.configuration.get('platforms_to_crawl', []),
                    'search_terms_count': len(crawl_job.configuration.get('search_terms', [])),
                    'similarity_threshold': crawl_job.configuration.get('similarity_threshold')
                },
                'performance_metrics': {
                    'success_rate': (
                        crawl_job.successful_executions / max(crawl_job.execution_count, 1)
                    ) * 100,
                    'average_matches_per_execution': (
                        total_matches / max(crawl_job.execution_count, 1)
                    ),
                    'content_detection_rate': self._calculate_detection_rate(crawl_job_id)
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get crawl job status: {str(e)}")
            raise CrawlerError(f"Status retrieval failed: {str(e)}")
    
    # Private methods for platform-specific crawling
    
    async def _search_platform_api(
        self,
        platform: str,
        search_terms: List[str],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search platform using official API."""
        try:
            platform_config = self.platform_configs[platform]
            api_endpoints = platform_config.get('api_endpoints', {})
            results = []
            
            if platform == 'youtube':
                results = await self._search_youtube_api(search_terms, config)
            elif platform == 'twitter':
                results = await self._search_twitter_api(search_terms, config)
            elif platform == 'soundcloud':
                results = await self._search_soundcloud_api(search_terms, config)
            elif platform == 'reddit':
                results = await self._search_reddit_api(search_terms, config)
            
            return results
            
        except Exception as e:
            logger.error(f"API search failed for {platform}: {str(e)}")
            return []
    
    async def _search_platform_web(
        self,
        platform: str,
        search_terms: List[str],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search platform using web scraping."""
        try:
            platform_config = self.platform_configs[platform]
            results = []
            
            # Get or create web session
            session = await self._get_platform_session(platform)
            
            if platform_config.get('requires_js', False):
                # Use Selenium for JavaScript-heavy sites
                driver = await self._get_platform_driver(platform)
                results = await self._scrape_with_selenium(
                    platform, search_terms, config, driver
                )
            else:
                # Use requests for static content
                results = await self._scrape_with_requests(
                    platform, search_terms, config, session
                )
            
            return results
            
        except Exception as e:
            logger.error(f"Web scraping failed for {platform}: {str(e)}")
            return []
    
    async def _search_youtube_api(
        self,
        search_terms: List[str],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search YouTube using official API."""
        try:
            results = []
            api_key = settings.YOUTUBE_API_KEY
            
            if not api_key:
                logger.warning("YouTube API key not configured")
                return []
            
            async with aiohttp.ClientSession() as session:
                for search_term in search_terms:
                    search_url = self.platform_configs['youtube']['api_endpoints']['search']
                    params = {
                        'part': 'snippet',
                        'q': search_term,
                        'type': 'video',
                        'maxResults': config.get('max_results_per_term', 25),
                        'key': api_key
                    }
                    
                    async with session.get(search_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for item in data.get('items', []):
                                result = {
                                    'platform': 'youtube',
                                    'content_type': 'video',
                                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                                    'title': item['snippet']['title'],
                                    'description': item['snippet']['description'],
                                    'channel': item['snippet']['channelTitle'],
                                    'published_at': item['snippet']['publishedAt'],
                                    'thumbnail_url': item['snippet']['thumbnails']['default']['url'],
                                    'metadata': {
                                        'video_id': item['id']['videoId'],
                                        'channel_id': item['snippet']['channelId'],
                                        'search_term': search_term
                                    }
                                }
                                results.append(result)
                        
                        # Respect rate limits
                        await asyncio.sleep(0.1)
            
            return results
            
        except Exception as e:
            logger.error(f"YouTube API search failed: {str(e)}")
            return []
    
    async def _scrape_with_selenium(
        self,
        platform: str,
        search_terms: List[str],
        config: Dict[str, Any],
        driver: webdriver.Chrome
    ) -> List[Dict[str, Any]]:
        """Scrape platform using Selenium for JavaScript content."""
        try:
            results = []
            platform_config = self.platform_configs[platform]
            selectors = platform_config.get('selectors', {})
            
            for search_term in search_terms:
                try:
                    # Navigate to search page
                    search_url = self._build_search_url(platform, search_term)
                    driver.get(search_url)
                    
                    # Wait for content to load
                    await asyncio.sleep(3)
                    
                    # Handle potential captcha
                    if await self._detect_captcha(driver):
                        await self._handle_captcha(driver, platform)
                    
                    # Extract content based on platform
                    if platform == 'instagram':
                        page_results = await self._extract_instagram_content(driver, selectors)
                    elif platform == 'tiktok':
                        page_results = await self._extract_tiktok_content(driver, selectors)
                    elif platform == 'youtube':
                        page_results = await self._extract_youtube_content(driver, selectors)
                    else:
                        page_results = await self._extract_generic_content(driver, selectors)
                    
                    # Add search term metadata
                    for result in page_results:
                        result['metadata']['search_term'] = search_term
                    
                    results.extend(page_results)
                    
                    # Random delay to avoid detection
                    await asyncio.sleep(2 + (hash(search_term) % 3))
                    
                except Exception as e:
                    logger.error(f"Failed to scrape {platform} for term '{search_term}': {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Selenium scraping failed for {platform}: {str(e)}")
            return []
    
    async def _extract_instagram_content(
        self,
        driver: webdriver.Chrome,
        selectors: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Extract content from Instagram using Selenium."""
        try:
            results = []
            
            # Wait for posts to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "article"))
            )
            
            # Find all post elements
            posts = driver.find_elements(By.TAG_NAME, "article")
            
            for post in posts[:20]:  # Limit to first 20 posts
                try:
                    # Extract post data
                    post_url = post.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    
                    # Determine content type
                    content_type = 'image'
                    media_element = None
                    
                    try:
                        media_element = post.find_element(By.CSS_SELECTOR, selectors['post_video'])
                        content_type = 'video'
                    except:
                        try:
                            media_element = post.find_element(By.CSS_SELECTOR, selectors['post_image'])
                        except:
                            continue
                    
                    # Extract metadata
                    try:
                        caption = post.find_element(By.CSS_SELECTOR, selectors['post_caption']).text
                    except:
                        caption = ""
                    
                    try:
                        username = post.find_element(By.CSS_SELECTOR, selectors['username']).text
                    except:
                        username = "unknown"
                    
                    result = {
                        'platform': 'instagram',
                        'content_type': content_type,
                        'url': post_url,
                        'title': caption[:100] + "..." if len(caption) > 100 else caption,
                        'description': caption,
                        'username': username,
                        'media_url': media_element.get_attribute("src") if media_element else "",
                        'metadata': {
                            'post_type': content_type,
                            'extracted_at': datetime.utcnow().isoformat()
                        }
                    }
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"Failed to extract Instagram post: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Instagram content extraction failed: {str(e)}")
            return []
    
    # Additional platform-specific extraction methods would continue here...
    # Due to length constraints, providing the core structure
    
    def _build_search_url(self, platform: str, search_term: str) -> str:
        """Build platform-specific search URL."""
        search_urls = {
            'youtube': f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}",
            'instagram': f"https://www.instagram.com/explore/tags/{search_term.replace(' ', '').replace('#', '')}/",
            'tiktok': f"https://www.tiktok.com/search?q={search_term.replace(' ', '%20')}",
            'twitter': f"https://twitter.com/search?q={search_term.replace(' ', '%20')}",
            'reddit': f"https://www.reddit.com/search/?q={search_term.replace(' ', '%20')}"
        }
        
        return search_urls.get(platform, f"https://www.google.com/search?q={search_term} site:{platform}.com")
    
    def _generate_search_terms(
        self,
        protection_record: Any,
        config: Dict[str, Any]
    ) -> List[str]:
        """Generate search terms based on protected content."""
        search_terms = []
        
        # Add content-specific terms
        if hasattr(protection_record, 'content_metadata'):
            metadata = protection_record.content_metadata or {}
            
            # Add title/name variations
            if 'title' in metadata:
                title = metadata['title']
                search_terms.extend([
                    title,
                    f'"{title}"',  # Exact match
                    title.replace(' ', ''),  # No spaces
                ])
            
            # Add creator/artist terms
            if 'creator' in metadata:
                creator = metadata['creator']
                search_terms.extend([
                    creator,
                    f'"{creator}"'
                ])
        
        # Add custom search terms from config
        custom_terms = config.get('custom_search_terms', [])
        search_terms.extend(custom_terms)
        
        # Generate hash-based terms for exact matches
        if hasattr(protection_record, 'metadata') and 'content_hash' in protection_record.metadata:
            content_hash = protection_record.metadata['content_hash']
            search_terms.append(content_hash[:16])  # First 16 chars of hash
        
        # Remove duplicates and empty terms
        unique_terms = list(set([term.strip() for term in search_terms if term.strip()]))
        
        return unique_terms[:50]  # Limit to 50 terms
    
    def _calculate_next_execution(self, frequency: str) -> datetime:
        """Calculate next execution time based on frequency."""
        now = datetime.utcnow()
        
        if frequency == 'continuous':
            return now + timedelta(minutes=15)
        elif frequency == 'hourly':
            return now + timedelta(hours=1)
        elif frequency == 'daily':
            return now + timedelta(days=1)
        elif frequency == 'weekly':
            return now + timedelta(weeks=1)
        else:
            return now + timedelta(days=1)  # Default to daily
    
    def _estimate_daily_checks(self, config: Dict[str, Any]) -> int:
        """
Estimate daily content checks based on configuration."""
        platforms_count = len(config.get('platforms_to_crawl', []))
        search_terms_count = len(config.get('search_terms', []))
        max_results = config.get('max_results_per_platform', 100)
        frequency = config.get('crawl_frequency', 'daily')
        
        daily_multiplier = {
            'continuous': 96,  # Every 15 minutes
            'hourly': 24,
            'daily': 1,
            'weekly': 0.14
        }.get(frequency, 1)
        
        return int(platforms_count * search_terms_count * max_results * daily_multiplier)
    
    async def _get_platform_session(self, platform: str) -> aiohttp.ClientSession:
        """
Get or create HTTP session for platform."""
        if platform not in self.sessions:
            # Configure session with platform-specific settings
            headers = {
                'User-Agent': self.user_agent_rotator.get_user_agent(platform),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            # Add platform-specific headers
            if platform == 'instagram':
                headers['X-Requested-With'] = 'XMLHttpRequest'
            elif platform == 'tiktok':
                headers['Referer'] = 'https://www.tiktok.com/'
            
            # Configure proxy if enabled
            connector = None
            if self.proxy_service.is_enabled():
                proxy_url = await self.proxy_service.get_proxy()
                connector = aiohttp.ProxyConnector.from_url(proxy_url)
            
            session = aiohttp.ClientSession(
                headers=headers,
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            self.sessions[platform] = session
        
        return self.sessions[platform]
    
    async def _get_platform_driver(self, platform: str) -> webdriver.Chrome:
        """
Get or create Selenium driver for platform."""
        if platform not in self.drivers:
            chrome_options = ChromeOptions()
            
            # Stealth mode configuration
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set user agent
            user_agent = self.user_agent_rotator.get_user_agent(platform)
            chrome_options.add_argument(f'--user-agent={user_agent}')
            
            # Platform-specific configurations
            if platform in ['instagram', 'tiktok']:
                # Mobile user agent for better compatibility
                mobile_ua = self.user_agent_rotator.get_mobile_user_agent()
                chrome_options.add_argument(f'--user-agent={mobile_ua}')
                chrome_options.add_argument('--window-size=375,667')
            
            # Proxy configuration
            if self.proxy_service.is_enabled():
                proxy_url = await self.proxy_service.get_proxy()
                chrome_options.add_argument(f'--proxy-server={proxy_url}')
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Execute script to hide automation
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.drivers[platform] = driver
        
        return self.drivers[platform]
    
    async def _detect_captcha(self, driver: webdriver.Chrome) -> bool:
        """Detect if captcha is present on page."""
        captcha_indicators = [
            'captcha', 'recaptcha', 'hcaptcha', 'challenge',
            'verify', 'security', 'robot', 'human'
        ]
        
        page_text = driver.page_source.lower()
        return any(indicator in page_text for indicator in captcha_indicators)
    
    async def _handle_captcha(self, driver: webdriver.Chrome, platform: str):
        """
Handle captcha if detected."""
        try:
            # Try automated captcha solving
            if self.captcha_solver.is_available():
                success = await self.captcha_solver.solve_captcha(driver, platform)
                if success:
                    logger.info(f"Successfully solved captcha for {platform}")
                    return
            
            # Fallback: wait and retry
            logger.warning(f"Captcha detected for {platform}, waiting before retry")
            await asyncio.sleep(60)  # Wait 1 minute
            
        except Exception as e:
            logger.error(f"Captcha handling failed for {platform}: {str(e)}")
    
    def _deduplicate_search_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on URL."""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
