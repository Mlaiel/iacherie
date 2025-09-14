"""Crawler Deployment Module

Enterprise-grade web crawler deployment infrastructure for content surveillance
and copyright protection. Supports multi-platform monitoring (YouTube, TikTok,
Instagram, Twitter, etc.) with intelligent crawling strategies and real-time detection.

Key Features:
    - Distributed crawler deployment across multiple platforms
- Intelligent crawling strategies and rate limiting
- Real-time content detection and matching
- DMCA compliance and takedown automation
- Multi-format content monitoring (audio, video, image, text)
- Advanced anti-detection techniques
- Scalable crawler orchestration with Kubernetes
- Performance monitoring and optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform

# [EMOJI_REMOVED]  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED # [EMOJI_REMOVED]
"""

import asyncio
import logging
import time
import random
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import aiodns
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import json
import redis
from kubernetes import client, config
import asyncpg
from datetime import datetime, timedelta
import hashlib
import base64
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import defaultdict, deque
import re
import urllib.parse
import ssl
import socket
from prometheus_client import Counter, Histogram, Gauge
import fake_useragent
import cloudscraper
import undetected_chromedriver as uc


class PlatformType(Enum):
    """
Supported social media platforms"""

    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    PINTEREST = "pinterest"
    REDDIT = "reddit"
    LINKEDIN = "linkedin"
    GENERIC_WEB = "generic_web"


class CrawlerType(Enum):
    """Types of crawlers"""

    API_CRAWLER = "api_crawler"
    WEB_SCRAPER = "web_scraper"
    SELENIUM_CRAWLER = "selenium_crawler"
    HEADLESS_BROWSER = "headless_browser"
    RSS_CRAWLER = "rss_crawler"
    SITEMAP_CRAWLER = "sitemap_crawler"


class CrawlStatus(Enum):
    """Crawl task status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    BLOCKED = "blocked"
    PAUSED = "paused"


@dataclass
class CrawlTarget:
    """Target for crawling"""
    target_id: str
    platform: PlatformType
    url: Optional[str] = None
    search_terms: List[str] = field(default_factory=list)
    creator_handles: List[str] = field(default_factory=list)
    content_types: List[str] = field(default_factory=list)  # audio, video, image, text
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    crawl_frequency: str = "daily"  # hourly, daily, weekly
    last_crawled: Optional[datetime] = None


@dataclass
class CrawlTask:
    """Individual crawl task"""
    task_id: str
    target: CrawlTarget
    crawler_type: CrawlerType
    status: CrawlStatus = CrawlStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results_count: int = 0
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class CrawlResult:
    """
Result from crawling operation"""
    task_id: str
    platform: PlatformType
    content_url: str
    content_type: str
    title: Optional[str] = None
    description: Optional[str] = None
    creator_info: Dict[str, Any] = field(default_factory=dict)
    engagement_metrics: Dict[str, Any] = field(default_factory=dict)
    content_metadata: Dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.now)
    fingerprint_required: bool = True
    dmca_candidate: bool = False


class ContentCrawlerOrchestrator:
    """
    Enterprise-grade crawler orchestration system for multi-platform content surveillance
    
    Features:
    - Multi-platform crawler deployment (YouTube, TikTok, Instagram, etc.)
    - Intelligent rate limiting and anti-detection
    - Distributed crawling with load balancing
    - Real-time content discovery and analysis
    - DMCA compliance and automation
    - Advanced monitoring and alerting
    - Kubernetes-based scalability
    """
    
    def __init__(self,
                 redis_host -> None: str = "localhost",
                 redis_port -> None: int = 6379,
                 postgres_url -> None: str = "postgresql -> None://localhost/ia_influencer",
                 k8s_namespace -> None: str = "ia-influencer") -> None:
        
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.postgres_url = postgres_url
        self.k8s_namespace = k8s_namespace
        
        # Crawler management
        self.active_crawlers: Dict[str, PlatformCrawlerManager] = {}
        self.crawl_queue = asyncio.Queue(maxsize=50000)
        self.results_queue = asyncio.Queue(maxsize=100000)
        self.task_registry: Dict[str, CrawlTask] = {}
        
        # Rate limiting and anti-detection
        self.rate_limiters: Dict[PlatformType, Dict[str, deque]] = defaultdict(lambda: defaultdict(deque))
        self.proxy_pools: Dict[PlatformType, List[str]] = defaultdict(list)
        self.user_agents = fake_useragent.UserAgent()
        
        # Performance metrics
        self.crawl_counter = Counter('crawler_requests_total',
                                   'Total crawler requests', ['platform', 'status'])
        self.crawl_duration = Histogram('crawler_request_duration_seconds',
                                      'Crawler request duration', ['platform'])
        self.queue_size = Gauge('crawler_queue_size', 'Current crawler queue size')
        self.active_crawlers_gauge = Gauge('active_crawlers_count', 'Number of active crawlers')
        
        # Thread pools
        self.crawler_executor = ThreadPoolExecutor(max_workers=100)
        self.processing_executor = ThreadPoolExecutor(max_workers=50)
        
        # Initialize components
        self._init_kubernetes_client()
        self._init_platform_crawlers()
        self._start_background_workers()
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("ContentCrawlerOrchestrator initialized successfully")
    
    def _init_kubernetes_client(self) -> None:
        """Initialize Kubernetes client"""
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        self.k8s_apps_v1 = client.AppsV1Api()
        self.k8s_core_v1 = client.CoreV1Api()
        self.k8s_autoscaling = client.AutoscalingV1Api()
    
    def _init_platform_crawlers(self) -> None:
        """
Initialize platform-specific crawlers"""
        platforms = [
            PlatformType.YOUTUBE,
            PlatformType.TIKTOK,
            PlatformType.INSTAGRAM,
            PlatformType.TWITTER,
            PlatformType.SPOTIFY,
            PlatformType.SOUNDCLOUD
        ]
        
        for platform in platforms:
            crawler_manager = PlatformCrawlerManager(
                platform=platform,
                redis_client=self.redis_client,
                orchestrator=self
            )
            self.active_crawlers[platform.value] = crawler_manager
    
    async def deploy_crawler_cluster(self, deployment_config: Dict[str, Any]) -> bool:
        """
        Deploy distributed crawler cluster with Kubernetes
        
        Args:
            deployment_config: Cluster deployment configuration
            
        Returns:
            bool: True if deployment successful
        """
        try:
            self.logger.info("Deploying crawler cluster")
            
            # Deploy crawler pods for each platform
            for platform, config in deployment_config.get('platforms', {}).items():
                if config.get('enabled', False):
                    await self._deploy_platform_crawlers(platform, config)
            
            # Deploy proxy management
            if deployment_config.get('proxy_enabled', True):
                await self._deploy_proxy_management()
            
            # Deploy rate limiting service
            await self._deploy_rate_limiting_service()
            
            # Setup monitoring and alerting
            await self._setup_crawler_monitoring()
            
            self.logger.info("Crawler cluster deployed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deploy crawler cluster: {str(e)}")
            return False
    
    async def schedule_crawl_task(self, target: CrawlTarget, crawler_type: CrawlerType) -> str:
        """
        Schedule a new crawling task
        
        Args:
            target: Crawl target specification
            crawler_type: Type of crawler to use
            
        Returns:
            str: Task ID
        """
        task_id = f"crawl_{int(time.time())}_{random.randint(1000, 9999)}"
        
        task = CrawlTask(
            task_id=task_id,
            target=target,
            crawler_type=crawler_type
        )
        
        # Add to task registry
        self.task_registry[task_id] = task
        
        # Add to crawl queue
        await self.crawl_queue.put(task)
        self.queue_size.set(self.crawl_queue.qsize())
        
        # Store in Redis for persistence
        await self._store_crawl_task(task)
        
        self.logger.info(f"Scheduled crawl task {task_id} for {target.platform.value}")
        return task_id
    
    async def execute_crawl_task(self, task: CrawlTask) -> List[CrawlResult]:
        """
        Execute a crawling task
        
        Args:
            task: Crawl task to execute
            
        Returns:
            List[CrawlResult]: Discovered content results
        """
        start_time = time.time()
        results = []
        
        try:
            task.status = CrawlStatus.RUNNING
            task.started_at = datetime.now()
            
            # Get appropriate crawler
            crawler_manager = self.active_crawlers.get(task.target.platform.value)
            if not crawler_manager:
                raise ValueError(f"No crawler available for platform {task.target.platform.value}")
            
            # Check rate limiting
            if not await self._check_rate_limit(task.target.platform):
                task.status = CrawlStatus.RATE_LIMITED
                await asyncio.sleep(60)  # Wait before retry
                return []
            
            # Execute crawling based on type
            if task.crawler_type == CrawlerType.API_CRAWLER:
                results = await crawler_manager.crawl_via_api(task.target)
            elif task.crawler_type == CrawlerType.WEB_SCRAPER:
                results = await crawler_manager.crawl_via_scraping(task.target)
            elif task.crawler_type == CrawlerType.SELENIUM_CRAWLER:
                results = await crawler_manager.crawl_via_selenium(task.target)
            else:
                raise ValueError(f"Unsupported crawler type: {task.crawler_type}")
            
            # Process and validate results
            validated_results = await self._validate_and_process_results(results, task)
            
            # Update task status
            task.status = CrawlStatus.COMPLETED
            task.completed_at = datetime.now()
            task.results_count = len(validated_results)
            
            # Update metrics
            processing_time = time.time() - start_time
            self.crawl_counter.labels(
                platform=task.target.platform.value,
                status='success'
            ).inc()
            self.crawl_duration.labels(platform=task.target.platform.value).observe(processing_time)
            
            # Store results
            await self._store_crawl_results(validated_results)
            
            # Check for potential DMCA violations
            await self._check_dmca_violations(validated_results)
            
            return validated_results
            
        except Exception as e:
            task.status = CrawlStatus.FAILED
            task.error_message = str(e)
            
            self.crawl_counter.labels(
                platform=task.target.platform.value,
                status='error'
            ).inc()
            
            self.logger.error(f"Crawl task {task.task_id} failed: {str(e)}")
            
            # Retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = CrawlStatus.PENDING
                await self.crawl_queue.put(task)
                self.logger.info(f"Retrying task {task.task_id} (attempt {task.retry_count})")
            
            return []
        
        finally:
            # Update task in registry and storage
            await self._update_crawl_task(task)
    
    async def search_content_by_fingerprint(self, 
                                          fingerprint_data: Dict[str, Any],
                                          platforms: List[PlatformType],
                                          search_depth: str = "standard") -> List[CrawlResult]:
        """
        Search for content matching specific fingerprints across platforms
        
        Args:
            fingerprint_data: Content fingerprints to search for
            platforms: Platforms to search on
            search_depth: Search intensity (light, standard, deep)
            
        Returns:
            List[CrawlResult]: Matching content found
        """
        results = []
        
        for platform in platforms:
            try:
                # Create targeted search task
                search_target = CrawlTarget(
                    target_id=f"fingerprint_search_{int(time.time())}",
                    platform=platform,
                    metadata={
                        'fingerprint_data': fingerprint_data,
                        'search_type': 'fingerprint_match',
                        'search_depth': search_depth
                    }
                )
                
                task_id = await self.schedule_crawl_task(search_target, CrawlerType.WEB_SCRAPER)
                
                # Wait for task completion (with timeout)
                timeout = 300 if search_depth == "deep" else 120
                task_results = await self._wait_for_task_completion(task_id, timeout)
                
                results.extend(task_results)
                
            except Exception as e:
                self.logger.error(f"Error searching {platform.value} for fingerprint: {str(e)}")
        
        return results
    
    async def monitor_creator_content(self, 
                                    creator_id: str,
                                    platforms: List[PlatformType],
                                    monitoring_frequency: str = "daily") -> bool:
        """
        Set up continuous monitoring for a creator's content across platforms
        
        Args:
            creator_id: Creator identifier
            platforms: Platforms to monitor
            monitoring_frequency: How often to check (hourly, daily, weekly)
            
        Returns:
            bool: True if monitoring setup successful
        """
        try:
            for platform in platforms:
                # Create monitoring target
                target = CrawlTarget(
                    target_id=f"monitor_{creator_id}_{platform.value}",
                    platform=platform,
                    creator_handles=[creator_id],
                    content_types=["audio", "video", "image", "text"],
                    crawl_frequency=monitoring_frequency,
                    metadata={
                        'monitoring_type': 'creator_protection',
                        'creator_id': creator_id
                    }
                )
                
                # Schedule recurring task
                await self._schedule_recurring_task(target)
            
            self.logger.info(f"Set up monitoring for creator {creator_id} on {len(platforms)} platforms")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup creator monitoring: {str(e)}")
            return False
    
    async def _deploy_platform_crawlers(self, platform -> None: str, config -> None: Dict[str, Any]) -> None:
        """Deploy crawler pods for specific platform"""
        crawler_manifest = self._create_crawler_deployment_manifest(platform, config)
        
        try:
            self.k8s_apps_v1.create_namespaced_deployment(
                namespace=self.k8s_namespace,
                body=crawler_manifest
            )
            
            # Create service for crawler communication
            service_manifest = self._create_crawler_service_manifest(platform)
            self.k8s_core_v1.create_namespaced_service(
                namespace=self.k8s_namespace,
                body=service_manifest
            )
            
            self.logger.info(f"Deployed {platform} crawlers successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy {platform} crawlers: {str(e)}")
    
    def _create_crawler_deployment_manifest(self, platform: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create Kubernetes deployment manifest for platform crawler"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"crawler-{platform}",
                "namespace": self.k8s_namespace,
                "labels": {
                    "app": f"crawler-{platform}",
                    "platform": platform,
                    "component": "content-crawler"
                }
            },
            "spec": {
                "replicas": config.get('replicas', 3),
                "selector": {
                    "matchLabels": {
                        "app": f"crawler-{platform}"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": f"crawler-{platform}",
                            "platform": platform,
                            "component": "content-crawler"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "crawler",
                            "image": f"ia-influencer/platform-crawler:{platform}-v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "PLATFORM", "value": platform},
                                {"name": "REDIS_HOST", "value": "redis-service"},
                                {"name": "POSTGRES_URL", "value": self.postgres_url},
                                {"name": "RATE_LIMIT", "value": str(config.get('rate_limit', 60))},
                                {"name": "PROXY_ENABLED", "value": str(config.get('proxy_enabled', True))}
                            ],
                            "resources": {
                                "limits": {
                                    "memory": config.get('memory_limit', '2Gi'),
                                    "cpu": config.get('cpu_limit', '1')
                                },
                                "requests": {
                                    "memory": config.get('memory_request', '1Gi'),
                                    "cpu": config.get('cpu_request', '500m')
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": 8080
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 60
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready",
                                    "port": 8080
                                },
                                "initialDelaySeconds": 10,
                                "periodSeconds": 5
                            }
                        }]
                    }
                }
            }
        }
    
    def _create_crawler_service_manifest(self, platform: str) -> Dict[str, Any]:
        """Create Kubernetes service manifest for platform crawler"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"crawler-{platform}-service",
                "namespace": self.k8s_namespace,
                "labels": {
                    "app": f"crawler-{platform}"
                }
            },
            "spec": {
                "selector": {
                    "app": f"crawler-{platform}"
                },
                "ports": [{
                    "port": 80,
                    "targetPort": 8080,
                    "protocol": "TCP"
                }],
                "type": "ClusterIP"
            }
        }
    
    async def _deploy_proxy_management(self) -> None:
        """Deploy proxy management service"""
        proxy_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "proxy-manager",
                "namespace": self.k8s_namespace
            },
            "spec": {
                "replicas": 2,
                "selector": {
                    "matchLabels": {
                        "app": "proxy-manager"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "proxy-manager"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "proxy-manager",
                            "image": "ia-influencer/proxy-manager:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "REDIS_HOST", "value": "redis-service"},
                                {"name": "PROXY_ROTATION_INTERVAL", "value": "300"}
                            ]
                        }]
                    }
                }
            }
        }
        
        self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.k8s_namespace,
            body=proxy_manifest
        )
    
    async def _deploy_rate_limiting_service(self) -> None:
        """Deploy rate limiting service"""
        rate_limit_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "rate-limiter",
                "namespace": self.k8s_namespace
            },
            "spec": {
                "replicas": 3,
                "selector": {
                    "matchLabels": {
                        "app": "rate-limiter"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "rate-limiter"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "rate-limiter",
                            "image": "ia-influencer/rate-limiter:v1.0",
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "REDIS_HOST", "value": "redis-service"}
                            ]
                        }]
                    }
                }
            }
        }
        
        self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.k8s_namespace,
            body=rate_limit_manifest
        )
    
    async def _setup_crawler_monitoring(self) -> None:
        """Setup monitoring and alerting for crawlers"""
        # Deploy Prometheus monitoring
        monitoring_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "crawler-monitor",
                "namespace": self.k8s_namespace
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "crawler-monitor"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "crawler-monitor"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "monitor",
                            "image": "ia-influencer/crawler-monitor:v1.0",
                            "ports": [{"containerPort": 9090}]
                        }]
                    }
                }
            }
        }
        
        self.k8s_apps_v1.create_namespaced_deployment(
            namespace=self.k8s_namespace,
            body=monitoring_manifest
        )
    
    async def _check_rate_limit(self, platform: PlatformType) -> bool:
        """Check if platform rate limit allows new request"""
        current_time = time.time()
        platform_limiters = self.rate_limiters[platform]
        
        # Platform-specific rate limits (requests per minute)
        rate_limits = {
            PlatformType.YOUTUBE: 100,
            PlatformType.TIKTOK: 60,
            PlatformType.INSTAGRAM: 80,
            PlatformType.TWITTER: 150,
            PlatformType.SPOTIFY: 120,
            PlatformType.SOUNDCLOUD: 100
        }
        
        limit = rate_limits.get(platform, 60)
        request_times = platform_limiters['requests']
        
        # Remove old requests (older than 1 minute)
        while request_times and request_times[0] < current_time - 60:
            request_times.popleft()
        
        # Check if under limit
        if len(request_times) < limit:
            request_times.append(current_time)
            return True
        
        return False
    
    async def _validate_and_process_results(self, 
                                          results: List[CrawlResult], 
                                          task: CrawlTask) -> List[CrawlResult]:
        """
Validate and process crawl results"""
        validated_results = []
        
        for result in results:
            try:
                # Basic validation
                if not result.content_url or not result.content_type:
                    continue
                
                # URL validation
                if not self._is_valid_url(result.content_url):
                    continue
                
                # Content type validation
                if result.content_type not in ['audio', 'video', 'image', 'text']:
                    continue
                
                # Add task metadata
                result.task_id = task.task_id
                
                # Determine if fingerprinting is required
                result.fingerprint_required = self._requires_fingerprinting(result)
                
                # Initial DMCA assessment
                result.dmca_candidate = await self._assess_dmca_potential(result)
                
                validated_results.append(result)
                
            except Exception as e:
                self.logger.warning(f"Error validating result: {str(e)}")
        
        return validated_results
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urllib.parse.urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except:
            return False
    
    def _requires_fingerprinting(self, result: CrawlResult) -> bool:
        """
Determine if content requires fingerprinting"""
        # All audio and video content requires fingerprinting
        if result.content_type in ['audio', 'video']:
            return True
        
        # Images above certain size/quality threshold
        if result.content_type == 'image':
            return True  # For now, fingerprint all images
        
        # Text content above certain length
        if result.content_type == 'text':
            description = result.description or ""
            title = result.title or ""
            return len(description + title) > 100
        
        return False
    
    async def _assess_dmca_potential(self, result: CrawlResult) -> bool:
        """Assess if content is potential DMCA violation"""
        # Basic heuristics for DMCA assessment
        
        # Check for copyrighted keywords in title/description
        copyright_keywords = [
            'official', 'music video', 'full album', 'soundtrack',
            'cover song', 'remix', 'instrumental'
        ]
        
        text_content = (result.title or "").lower() + " " + (result.description or "").lower()
        
        for keyword in copyright_keywords:
            if keyword in text_content:
                return True
        
        # Check engagement metrics (viral content more likely to be original)
        engagement = result.engagement_metrics
        views = engagement.get('views', 0)
        likes = engagement.get('likes', 0)
        
        # High engagement might indicate original content
        if views > 100000 or likes > 10000:
            return False
        
        return False  # Default to non-violation
    
    async def _store_crawl_task(self, task -> None: CrawlTask) -> None:
        """Store crawl task in Redis"""
        task_data = {
            'task_id': task.task_id,
            'target': json.dumps(task.target.__dict__, default=str),
            'crawler_type': task.crawler_type.value,
            'status': task.status.value,
            'created_at': datetime.now().isoformat()
        }
        
        await asyncio.get_event_loop().run_in_executor(
            self.processing_executor,
            self.redis_client.hset,
            f"crawl_task:{task.task_id}",
            mapping=task_data
        )
    
    async def _update_crawl_task(self, task -> None: CrawlTask) -> None:
        """Update crawl task in storage"""
        task_data = {
            'status': task.status.value,
            'results_count': task.results_count,
            'retry_count': task.retry_count,
            'updated_at': datetime.now().isoformat()
        }
        
        if task.error_message:
            task_data['error_message'] = task.error_message
        
        if task.completed_at:
            task_data['completed_at'] = task.completed_at.isoformat()
        
        await asyncio.get_event_loop().run_in_executor(
            self.processing_executor,
            self.redis_client.hset,
            f"crawl_task:{task.task_id}",
            mapping=task_data
        )
    
    async def _store_crawl_results(self, results -> None: List[CrawlResult]) -> None:
        """Store crawl results in database"""
        try:
            # Store in PostgreSQL for permanent storage
            # This would use asyncpg to store results
            for result in results:
                # Store result data
                pass
                
            # Store in Redis for quick access
            for result in results:
                result_data = json.dumps(result.__dict__, default=str)
                await asyncio.get_event_loop().run_in_executor(
                    self.processing_executor,
                    self.redis_client.setex,
                    f"crawl_result:{result.task_id}:{hash(result.content_url)}",
                    86400,  # 24 hours TTL
                    result_data
                )
                
        except Exception as e:
            self.logger.error(f"Error storing crawl results: {str(e)}")
    
    async def _check_dmca_violations(self, results -> None: List[CrawlResult]) -> None:
        """Check results for potential DMCA violations"""
        for result in results:
            if result.dmca_candidate:
                # Trigger DMCA enforcement workflow
                await self._trigger_dmca_enforcement(result)
    
    async def _trigger_dmca_enforcement(self, result -> None: CrawlResult) -> None:
        """
Trigger DMCA enforcement for potential violation"""
        try:
            # Add to DMCA processing queue
            dmca_task = {
                'content_url': result.content_url,
                'platform': result.platform.value,
                'discovered_at': result.discovered_at.isoformat(),
                'creator_info': result.creator_info
            }
            
            await asyncio.get_event_loop().run_in_executor(
                self.processing_executor,
                self.redis_client.lpush,
                "dmca_enforcement_queue",
                json.dumps(dmca_task)
            )
            
            self.logger.info(f"Triggered DMCA enforcement for {result.content_url}")
            
        except Exception as e:
            self.logger.error(f"Error triggering DMCA enforcement: {str(e)}")
    
    async def _schedule_recurring_task(self, target -> None: CrawlTarget) -> None:
        try:
            logger.info(f"Executing _schedule_recurring_task")
            
            # Implementation for _schedule_recurring_task
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_schedule_recurring_task completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_schedule_recurring_task failed: {e}")
            raise
    async def _wait_for_task_completion(self, task_id: str, timeout: int) -> List[CrawlResult]:
        """
Wait for task completion and return results"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            task = self.task_registry.get(task_id)
            if task and task.status in [CrawlStatus.COMPLETED, CrawlStatus.FAILED]:
                # Get results from storage
                return await self._get_task_results(task_id)
            
            await asyncio.sleep(5)
        
        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
    
    async def _get_task_results(self, task_id: str) -> List[CrawlResult]:
        """Get results for completed task"""
        # Implementation to retrieve results from storage
        return []
    
    def _start_background_workers(self) -> None:
        """
Start background worker threads"""
        def queue_processor() -> None:
            """
Process crawl queue"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def process_queue() -> None:
                while True:
                    try:
                        task = await self.crawl_queue.get()
                        await self.execute_crawl_task(task)
                        self.crawl_queue.task_done()
                    except Exception as e:
                        self.logger.error(f"Queue processor error: {str(e)}")
            
            loop.run_until_complete(process_queue())
        
        def health_monitor() -> None:
            """Monitor crawler health"""
            while True:
                try:
                    self._update_health_metrics()
                except Exception as e:
                    self.logger.error(f"Health monitor error: {str(e)}")
                time.sleep(60)
        
        # Start workers
        queue_thread = threading.Thread(target=queue_processor, daemon=True)
        health_thread = threading.Thread(target=health_monitor, daemon=True)
        
        queue_thread.start()
        health_thread.start()
    
    def _update_health_metrics(self) -> None:
        """Update health and performance metrics"""
        self.queue_size.set(self.crawl_queue.qsize())
        self.active_crawlers_gauge.set(len(self.active_crawlers))


class PlatformCrawlerManager:
    """
    Platform-specific crawler manager for individual social media platforms
    
    Features:
    - Platform-specific API integration
    - Anti-detection web scraping
    - Selenium-based dynamic content crawling
    - Intelligent retry mechanisms
    - Content extraction and normalization
    """
    
    def __init__(self, 
                 platform -> None: PlatformType,
                 redis_client -> None: redis.Redis,
                 orchestrator) -> None:
        
        self.platform = platform
        self.redis_client = redis_client
        self.orchestrator = orchestrator
        
        # Platform-specific configurations
        self.api_endpoints = self._get_api_endpoints()
        self.scraping_configs = self._get_scraping_configs()
        
        # Session management
        self.session = requests.Session()
        self.cloudscraper_session = cloudscraper.create_scraper()
        
        # Browser automation
        self.browser_options = self._get_browser_options()
        
        self.logger = logging.getLogger(f"{__name__}.{platform.value}")
    
    def _get_api_endpoints(self) -> Dict[str, str]:
        """Get platform-specific API endpoints"""
        endpoints = {
            PlatformType.YOUTUBE: {
                'search': 'https://www.googleapis.com/youtube/v3/search',
                'videos': 'https://www.googleapis.com/youtube/v3/videos',
                'channels': 'https://www.googleapis.com/youtube/v3/channels'
            },
            PlatformType.TWITTER: {
                'search': 'https://api.twitter.com/2/tweets/search/recent',
                'users': 'https://api.twitter.com/2/users'
            },
            PlatformType.SPOTIFY: {
                'search': 'https://api.spotify.com/v1/search',
                'tracks': 'https://api.spotify.com/v1/tracks'
            }
        }
        
        return endpoints.get(self.platform, {})
    
    def _get_scraping_configs(self) -> Dict[str, Any]:
        """
Get platform-specific scraping configurations"""
        configs = {
            PlatformType.TIKTOK: {
                'base_url': 'https://www.tiktok.com',
                'selectors': {
                    'video_links': '[data-e2e="video-feed"] a',
                    'creator': '[data-e2e="video-author"]',
                    'description': '[data-e2e="video-desc"]'
                }
            },
            PlatformType.INSTAGRAM: {
                'base_url': 'https://www.instagram.com',
                'selectors': {
                    'posts': 'article a',
                    'creator': 'header a',
                    'description': 'article div span'
                }
            }
        }
        
        return configs.get(self.platform, {})
    
    def _get_browser_options(self) -> Options:
        """Get browser options for Selenium"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument(f'--user-agent={self.orchestrator.user_agents.random}')
        
        return options
    
    async def crawl_via_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """
Crawl using official platform APIs"""
        results = []
        
        try:
            if self.platform == PlatformType.YOUTUBE:
                results = await self._crawl_youtube_api(target)
            elif self.platform == PlatformType.TWITTER:
                results = await self._crawl_twitter_api(target)
            elif self.platform == PlatformType.SPOTIFY:
                results = await self._crawl_spotify_api(target)
            elif self.platform == PlatformType.INSTAGRAM:
                results = await self._crawl_instagram_api(target)
            elif self.platform == PlatformType.TIKTOK:
                results = await self._crawl_tiktok_api(target)
            elif self.platform == PlatformType.FACEBOOK:
                results = await self._crawl_facebook_api(target)
            elif self.platform == PlatformType.SOUNDCLOUD:
                results = await self._crawl_soundcloud_api(target)
            elif self.platform == PlatformType.PINTEREST:
                results = await self._crawl_pinterest_api(target)
            elif self.platform == PlatformType.REDDIT:
                results = await self._crawl_reddit_api(target)
            elif self.platform == PlatformType.LINKEDIN:
                results = await self._crawl_linkedin_api(target)
            else:
                # For unsupported platforms, fall back to generic web crawling
                self.logger.warning(f"API crawling not available for {self.platform.value}, falling back to generic approach")
                results = await self._crawl_generic_api(target)
                
        except Exception as e:
            self.logger.error(f"API crawling failed for {self.platform.value}: {str(e)}")
        
        return results
    
    async def crawl_via_scraping(self, target: CrawlTarget) -> List[CrawlResult]:
        """Crawl using web scraping techniques"""
        results = []
        
        try:
            if self.platform == PlatformType.TIKTOK:
                results = await self._crawl_tiktok_scraping(target)
            elif self.platform == PlatformType.INSTAGRAM:
                results = await self._crawl_instagram_scraping(target)
            else:
        try:
            logger.info(f"Executing crawl_via_selenium")
            
            # Implementation for crawl_via_selenium
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"crawl_via_selenium completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"crawl_via_selenium failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Selenium crawling failed for {self.platform.value}: {str(e)}")
        finally:
            try:
                driver.quit()
            except:
                pass
        
        return results
    
    # Platform-specific implementation methods would go here
    async def _crawl_youtube_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """YouTube API crawling implementation"""
        results = []
        
        try:
            import aiohttp
            import json
            
            # Check rate limits
            if not await self._check_rate_limit(PlatformType.YOUTUBE):
                self.logger.warning("YouTube API rate limit exceeded")
                return results
            
            # Get API key from config or environment
            api_key = self.config.get("youtube_api_key") or "demo_api_key"
            
            # Build search query
            if target.search_terms:
                search_query = " ".join(target.search_terms)
            elif target.creator_handles:
                search_query = " ".join(target.creator_handles)
            else:
                search_query = "content"
            
            # YouTube Data API v3 search endpoint
            base_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": search_query,
                "type": "video",
                "maxResults": min(target.metadata.get("max_results", 25), 50),
                "order": "relevance",
                "key": api_key
            }
            
            # Apply content type filters
            if "video" in target.content_types:
                params["type"] = "video"
            elif "channel" in target.content_types:
                params["type"] = "channel"
            elif "playlist" in target.content_types:
                params["type"] = "playlist"
            
            # Make API request
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process search results
                        for item in data.get("items", []):
                            snippet = item.get("snippet", {})
                            video_id = item.get("id", {}).get("videoId", "")
                            
                            if video_id:
                                # Get additional video details
                                video_details = await self._get_youtube_video_details(video_id, api_key, session)
                                
                                # Create crawl result
                                result = CrawlResult(
                                    task_id=target.target_id,
                                    platform=PlatformType.YOUTUBE,
                                    content_url=f"https://www.youtube.com/watch?v={video_id}",
                                    content_type="video",
                                    title=snippet.get("title", ""),
                                    description=snippet.get("description", ""),
                                    creator_info={
                                        "channel_id": snippet.get("channelId", ""),
                                        "channel_title": snippet.get("channelTitle", ""),
                                        "published_at": snippet.get("publishedAt", "")
                                    },
                                    engagement_metrics=video_details.get("engagement", {}),
                                    content_metadata={
                                        "video_id": video_id,
                                        "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                                        "category_id": video_details.get("category_id", ""),
                                        "duration": video_details.get("duration", ""),
                                        "tags": video_details.get("tags", [])
                                    },
                                    discovered_at=datetime.now(),
                                    fingerprint_required=True,
                                    dmca_candidate=True  # YouTube content is potential DMCA candidate
                                )
                                results.append(result)
                    
                    elif response.status == 403:
                        self.logger.error("YouTube API quota exceeded or invalid API key")
                    else:
                        self.logger.error(f"YouTube API error: {response.status}")
            
            # Update rate limiter
            await self._record_api_request(PlatformType.YOUTUBE)
            
            self.logger.info(f"YouTube API crawl completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"YouTube API crawling failed: {str(e)}")
        
        return results
    
    async def _crawl_twitter_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """Twitter API crawling implementation"""
        results = []
        
        try:
            import aiohttp
            import json
            import base64
            
            # Check rate limits
            if not await self._check_rate_limit(PlatformType.TWITTER):
                self.logger.warning("Twitter API rate limit exceeded")
                return results
            
            # Get API credentials from config
            bearer_token = self.config.get("twitter_bearer_token") or "demo_bearer_token"
            
            # Build search query
            if target.search_terms:
                query = " ".join(target.search_terms)
            elif target.creator_handles:
                # Search for tweets from specific users
                handles = " OR ".join([f"from:{handle.lstrip('@')}" for handle in target.creator_handles])
                query = handles
            else:
                query = "content"
            
            # Add content type filters
            if "image" in target.content_types:
                query += " has:images"
            if "video" in target.content_types:
                query += " has:videos"
            if "audio" in target.content_types:
                query += " has:media"
            
            # Remove retweets and replies for cleaner content
            query += " -is:retweet -is:reply"
            
            # Twitter API v2 search endpoint
            base_url = "https://api.twitter.com/2/tweets/search/recent"
            params = {
                "query": query,
                "max_results": min(target.metadata.get("max_results", 25), 100),
                "tweet.fields": "created_at,author_id,public_metrics,context_annotations,attachments,lang",
                "user.fields": "username,name,verified,public_metrics",
                "media.fields": "type,url,preview_image_url,duration_ms,width,height",
                "expansions": "author_id,attachments.media_keys"
            }
            
            headers = {
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json"
            }
            
            # Make API request
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(base_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Extract users and media for reference
                        users_lookup = {}
                        if "includes" in data and "users" in data["includes"]:
                            for user in data["includes"]["users"]:
                                users_lookup[user["id"]] = user
                        
                        media_lookup = {}
                        if "includes" in data and "media" in data["includes"]:
                            for media in data["includes"]["media"]:
                                media_lookup[media["media_key"]] = media
                        
                        # Process tweets
                        for tweet in data.get("data", []):
                            tweet_id = tweet.get("id", "")
                            author_id = tweet.get("author_id", "")
                            author_info = users_lookup.get(author_id, {})
                            
                            # Determine content type
                            content_type = "text"
                            media_urls = []
                            
                            if "attachments" in tweet and "media_keys" in tweet["attachments"]:
                                for media_key in tweet["attachments"]["media_keys"]:
                                    media = media_lookup.get(media_key, {})
                                    if media.get("type") == "photo":
                                        content_type = "image"
                                        media_urls.append(media.get("url", ""))
                                    elif media.get("type") == "video":
                                        content_type = "video" 
                                        media_urls.append(media.get("preview_image_url", ""))
                                    elif media.get("type") == "animated_gif":
                                        content_type = "video"
                                        media_urls.append(media.get("preview_image_url", ""))
                            
                            # Create crawl result
                            result = CrawlResult(
                                task_id=target.target_id,
                                platform=PlatformType.TWITTER,
                                content_url=f"https://twitter.com/user/status/{tweet_id}",
                                content_type=content_type,
                                title=f"Tweet by @{author_info.get('username', 'unknown')}",
                                description=tweet.get("text", "")[:500],  # Truncate long tweets
                                creator_info={
                                    "user_id": author_id,
                                    "username": author_info.get("username", ""),
                                    "display_name": author_info.get("name", ""),
                                    "verified": author_info.get("verified", False),
                                    "followers_count": author_info.get("public_metrics", {}).get("followers_count", 0)
                                },
                                engagement_metrics={
                                    "retweet_count": tweet.get("public_metrics", {}).get("retweet_count", 0),
                                    "like_count": tweet.get("public_metrics", {}).get("like_count", 0),
                                    "reply_count": tweet.get("public_metrics", {}).get("reply_count", 0),
                                    "quote_count": tweet.get("public_metrics", {}).get("quote_count", 0)
                                },
                                content_metadata={
                                    "tweet_id": tweet_id,
                                    "created_at": tweet.get("created_at", ""),
                                    "lang": tweet.get("lang", ""),
                                    "media_urls": media_urls,
                                    "context_annotations": tweet.get("context_annotations", [])
                                },
                                discovered_at=datetime.now(),
                                fingerprint_required=content_type in ["image", "video"],
                                dmca_candidate=content_type in ["image", "video", "audio"]
                            )
                            results.append(result)
                    
                    elif response.status == 429:
                        self.logger.error("Twitter API rate limit exceeded")
                    elif response.status == 401:
                        self.logger.error("Twitter API authentication failed")
                    else:
                        self.logger.error(f"Twitter API error: {response.status}")
            
            # Update rate limiter
            await self._record_api_request(PlatformType.TWITTER)
            
            self.logger.info(f"Twitter API crawl completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"Twitter API crawling failed: {str(e)}")
        
        return results
    
    async def _crawl_spotify_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """Spotify API crawling implementation"""
        results = []
        
        try:
            import aiohttp
            import json
            import base64
            
            # Check rate limits
            if not await self._check_rate_limit(PlatformType.SPOTIFY):
                self.logger.warning("Spotify API rate limit exceeded")
                return results
            
            # Get Spotify API credentials
            client_id = self.config.get("spotify_client_id") or "demo_client_id"
            client_secret = self.config.get("spotify_client_secret") or "demo_client_secret"
            
            # Get access token using Client Credentials Flow
            access_token = await self._get_spotify_access_token(client_id, client_secret)
            
            if not access_token:
                self.logger.error("Failed to get Spotify access token")
                return results
            
            # Build search query
            if target.search_terms:
                query = " ".join(target.search_terms)
            elif target.creator_handles:
                # Search for artists
                query = " ".join(target.creator_handles)
            else:
                query = "music"
            
            # Determine search type based on content types
            search_types = []
            if "audio" in target.content_types or not target.content_types:
                search_types.extend(["track", "album"])
            if "artist" in target.content_types:
                search_types.append("artist")
            if "playlist" in target.content_types:
                search_types.append("playlist")
            
            if not search_types:
                search_types = ["track"]  # Default to tracks
            
            # Spotify Web API search endpoint
            base_url = "https://api.spotify.com/v1/search"
            params = {
                "q": query,
                "type": ",".join(search_types),
                "limit": min(target.metadata.get("max_results", 25), 50),
                "market": "US"  # Default market
            }
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Make API request
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(base_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process tracks
                        if "tracks" in data and "items" in data["tracks"]:
                            for track in data["tracks"]["items"]:
                                track_id = track.get("id", "")
                                
                                # Get audio features for additional metadata
                                audio_features = await self._get_spotify_audio_features(track_id, access_token, session)
                                
                                result = CrawlResult(
                                    task_id=target.target_id,
                                    platform=PlatformType.SPOTIFY,
                                    content_url=track.get("external_urls", {}).get("spotify", ""),
                                    content_type="audio",
                                    title=track.get("name", ""),
                                    description=f"Track by {', '.join([artist['name'] for artist in track.get('artists', [])])}",
                                    creator_info={
                                        "artists": [
                                            {
                                                "id": artist.get("id", ""),
                                                "name": artist.get("name", ""),
                                                "url": artist.get("external_urls", {}).get("spotify", "")
                                            }
                                            for artist in track.get("artists", [])
                                        ],
                                        "album": {
                                            "id": track.get("album", {}).get("id", ""),
                                            "name": track.get("album", {}).get("name", ""),
                                            "release_date": track.get("album", {}).get("release_date", "")
                                        }
                                    },
                                    engagement_metrics={
                                        "popularity": track.get("popularity", 0),
                                        "explicit": track.get("explicit", False),
                                        "duration_ms": track.get("duration_ms", 0)
                                    },
                                    content_metadata={
                                        "track_id": track_id,
                                        "isrc": track.get("external_ids", {}).get("isrc", ""),
                                        "preview_url": track.get("preview_url", ""),
                                        "track_number": track.get("track_number", 0),
                                        "disc_number": track.get("disc_number", 0),
                                        "available_markets": track.get("available_markets", []),
                                        "audio_features": audio_features or {}
                                    },
                                    discovered_at=datetime.now(),
                                    fingerprint_required=True,  # Audio content needs fingerprinting
                                    dmca_candidate=True  # Music content is high DMCA risk
                                )
                                results.append(result)
                        
                        # Process albums
                        if "albums" in data and "items" in data["albums"]:
                            for album in data["albums"]["items"]:
                                result = CrawlResult(
                                    task_id=target.target_id,
                                    platform=PlatformType.SPOTIFY,
                                    content_url=album.get("external_urls", {}).get("spotify", ""),
                                    content_type="album",
                                    title=album.get("name", ""),
                                    description=f"Album by {', '.join([artist['name'] for artist in album.get('artists', [])])}",
                                    creator_info={
                                        "artists": [
                                            {
                                                "id": artist.get("id", ""),
                                                "name": artist.get("name", ""),
                                                "url": artist.get("external_urls", {}).get("spotify", "")
                                            }
                                            for artist in album.get("artists", [])
                                        ],
                                        "release_date": album.get("release_date", ""),
                                        "total_tracks": album.get("total_tracks", 0)
                                    },
                                    engagement_metrics={},
                                    content_metadata={
                                        "album_id": album.get("id", ""),
                                        "album_type": album.get("album_type", ""),
                                        "available_markets": album.get("available_markets", []),
                                        "images": album.get("images", [])
                                    },
                                    discovered_at=datetime.now(),
                                    fingerprint_required=True,
                                    dmca_candidate=True
                                )
                                results.append(result)
                        
                        # Process artists
                        if "artists" in data and "items" in data["artists"]:
                            for artist in data["artists"]["items"]:
                                result = CrawlResult(
                                    task_id=target.target_id,
                                    platform=PlatformType.SPOTIFY,
                                    content_url=artist.get("external_urls", {}).get("spotify", ""),
                                    content_type="artist",
                                    title=artist.get("name", ""),
                                    description=f"Artist - {', '.join(artist.get('genres', []))}",
                                    creator_info={
                                        "artist_id": artist.get("id", ""),
                                        "genres": artist.get("genres", []),
                                        "images": artist.get("images", [])
                                    },
                                    engagement_metrics={
                                        "popularity": artist.get("popularity", 0),
                                        "followers": artist.get("followers", {}).get("total", 0)
                                    },
                                    content_metadata={
                                        "artist_id": artist.get("id", ""),
                                        "genres": artist.get("genres", [])
                                    },
                                    discovered_at=datetime.now(),
                                    fingerprint_required=False,  # Artist profiles don't need fingerprinting
                                    dmca_candidate=False
                                )
                                results.append(result)
                    
                    elif response.status == 429:
                        self.logger.error("Spotify API rate limit exceeded")
                    elif response.status == 401:
                        self.logger.error("Spotify API authentication failed")
                    else:
                        self.logger.error(f"Spotify API error: {response.status}")
            
            # Update rate limiter
            await self._record_api_request(PlatformType.SPOTIFY)
            
            self.logger.info(f"Spotify API crawl completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"Spotify API crawling failed: {str(e)}")
        
        return results
    
    async def _crawl_instagram_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """Instagram API crawling implementation"""
        results = []
        
        try:
            # Check rate limits
            if not await self._check_rate_limit(PlatformType.INSTAGRAM):
                self.logger.warning("Instagram API rate limit exceeded")
                return results
            
            # Instagram Graph API implementation
            access_token = self.config.get("instagram_access_token") or "demo_access_token"
            
            async with aiohttp.ClientSession() as session:
                # Get Instagram user media
                url = f"https://graph.instagram.com/me/media"
                params = {
                    'fields': 'id,caption,media_type,media_url,permalink,timestamp,username',
                    'access_token': access_token
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get('data', []):
                            result = CrawlResult(
                                task_id=target.target_id,
                                platform=PlatformType.INSTAGRAM,
                                content_url=item.get('permalink', ''),
                                content_type=item.get('media_type', 'photo').lower(),
                                title=item.get('caption', '')[:100] if item.get('caption') else 'Instagram Post',
                                description=item.get('caption', ''),
                                author_info={
                                    "username": item.get('username', ''),
                                    "user_id": item.get('id', '')
                                },
                                engagement_metrics={
                                    "media_type": item.get('media_type', ''),
                                    "timestamp": item.get('timestamp', '')
                                },
                                content_metadata={
                                    "media_id": item.get('id', ''),
                                    "media_url": item.get('media_url', ''),
                                    "permalink": item.get('permalink', '')
                                },
                                discovered_at=datetime.now(),
                                fingerprint_required=True,
                                dmca_candidate=True
                            )
                            results.append(result)
            
            self.logger.info(f"Instagram API crawl completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"Instagram API crawling failed: {str(e)}")
        
        return results
    
    async def _crawl_tiktok_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """TikTok API crawling implementation"""
        results = []
        
        try:
            # Check rate limits
            if not await self._check_rate_limit(PlatformType.TIKTOK):
                self.logger.warning("TikTok API rate limit exceeded")
                return results
            
            # TikTok API implementation (Note: Official API access is limited)
            access_token = self.config.get("tiktok_access_token") or "demo_access_token"
            
            async with aiohttp.ClientSession() as session:
                # Get TikTok user videos
                url = "https://open-api.tiktok.com/video/list/"
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                params = {
                    'fields': 'id,video_description,duration,create_time,share_url',
                    'max_count': 20
                }
                
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for video in data.get('data', {}).get('videos', []):
                            result = CrawlResult(
                                task_id=target.target_id,
                                platform=PlatformType.TIKTOK,
                                content_url=video.get('share_url', ''),
                                content_type='video',
                                title=video.get('video_description', '')[:100] if video.get('video_description') else 'TikTok Video',
                                description=video.get('video_description', ''),
                                author_info={
                                    "video_id": video.get('id', '')
                                },
                                engagement_metrics={
                                    "duration": video.get('duration', 0),
                                    "create_time": video.get('create_time', 0)
                                },
                                content_metadata={
                                    "video_id": video.get('id', ''),
                                    "share_url": video.get('share_url', '')
                                },
                                discovered_at=datetime.now(),
                                fingerprint_required=True,
                                dmca_candidate=True
                            )
                            results.append(result)
            
            self.logger.info(f"TikTok API crawl completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"TikTok API crawling failed: {str(e)}")
        
        return results
    
    async def _crawl_facebook_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """Facebook API crawling implementation"""
        results = []
        
        try:
            # Check rate limits
            if not await self._check_rate_limit(PlatformType.FACEBOOK):
                self.logger.warning("Facebook API rate limit exceeded")
                return results
            
            # Facebook Graph API implementation
            access_token = self.config.get("facebook_access_token") or "demo_access_token"
            
            async with aiohttp.ClientSession() as session:
                # Get Facebook posts
                url = f"https://graph.facebook.com/me/posts"
                params = {
                    'fields': 'id,message,created_time,type,link,source',
                    'access_token': access_token
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for post in data.get('data', []):
                            result = CrawlResult(
                                task_id=target.target_id,
                                platform=PlatformType.FACEBOOK,
                                content_url=post.get('link', ''),
                                content_type=post.get('type', 'status'),
                                title=post.get('message', '')[:100] if post.get('message') else 'Facebook Post',
                                description=post.get('message', ''),
                                author_info={
                                    "post_id": post.get('id', '')
                                },
                                engagement_metrics={
                                    "post_type": post.get('type', ''),
                                    "created_time": post.get('created_time', '')
                                },
                                content_metadata={
                                    "post_id": post.get('id', ''),
                                    "source": post.get('source', ''),
                                    "link": post.get('link', '')
                                },
                                discovered_at=datetime.now(),
                                fingerprint_required=True,
                                dmca_candidate=True
                            )
                            results.append(result)
            
            self.logger.info(f"Facebook API crawl completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"Facebook API crawling failed: {str(e)}")
        
        return results
    
    async def _crawl_soundcloud_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """SoundCloud API crawling implementation"""
        results = []
        
        try:
            # Check rate limits
            if not await self._check_rate_limit(PlatformType.SOUNDCLOUD):
                self.logger.warning("SoundCloud API rate limit exceeded")
                return results
            
            # SoundCloud API implementation
            client_id = self.config.get("soundcloud_client_id") or "demo_client_id"
            
            async with aiohttp.ClientSession() as session:
                # Get SoundCloud tracks
                url = "https://api.soundcloud.com/tracks"
                params = {
                    'client_id': client_id,
                    'limit': 20
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        tracks = await response.json()
                        
                        for track in tracks:
                            result = CrawlResult(
                                task_id=target.target_id,
                                platform=PlatformType.SOUNDCLOUD,
                                content_url=track.get('permalink_url', ''),
                                content_type='audio',
                                title=track.get('title', ''),
                                description=track.get('description', ''),
                                author_info={
                                    "username": track.get('user', {}).get('username', ''),
                                    "user_id": track.get('user_id', '')
                                },
                                engagement_metrics={
                                    "playback_count": track.get('playback_count', 0),
                                    "likes_count": track.get('likes_count', 0),
                                    "duration": track.get('duration', 0)
                                },
                                content_metadata={
                                    "track_id": track.get('id', ''),
                                    "waveform_url": track.get('waveform_url', ''),
                                    "stream_url": track.get('stream_url', ''),
                                    "genre": track.get('genre', ''),
                                    "bpm": track.get('bpm', 0)
                                },
                                discovered_at=datetime.now(),
                                fingerprint_required=True,
                                dmca_candidate=True
                            )
                            results.append(result)
            
            self.logger.info(f"SoundCloud API crawl completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"SoundCloud API crawling failed: {str(e)}")
        
        return results
    
    async def _crawl_pinterest_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """Pinterest API crawling implementation"""
        results = []
        
        try:
            # Check rate limits
            if not await self._check_rate_limit(PlatformType.PINTEREST):
                self.logger.warning("Pinterest API rate limit exceeded")
                return results
            
            # Pinterest API implementation
            access_token = self.config.get("pinterest_access_token") or "demo_access_token"
            
            async with aiohttp.ClientSession() as session:
                # Get Pinterest pins
                url = "https://api.pinterest.com/v5/pins"
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for pin in data.get('items', []):
                            result = CrawlResult(
                                task_id=target.target_id,
                                platform=PlatformType.PINTEREST,
                                content_url=pin.get('link', ''),
                                content_type='image',
                                title=pin.get('title', ''),
                                description=pin.get('description', ''),
                                author_info={
                                    "pin_id": pin.get('id', '')
                                },
                                engagement_metrics={
                                    "save_count": pin.get('save_count', 0),
                                    "comment_count": pin.get('comment_count', 0)
                                },
                                content_metadata={
                                    "pin_id": pin.get('id', ''),
                                    "board_id": pin.get('board_id', ''),
                                    "media_url": pin.get('media', {}).get('images', {}).get('original', {}).get('url', '')
                                },
                                discovered_at=datetime.now(),
                                fingerprint_required=True,
                                dmca_candidate=True
                            )
                            results.append(result)
            
            self.logger.info(f"Pinterest API crawl completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"Pinterest API crawling failed: {str(e)}")
        
        return results
    
    async def _crawl_reddit_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """Reddit API crawling implementation"""
        results = []
        
        try:
            # Check rate limits
            if not await self._check_rate_limit(PlatformType.REDDIT):
                self.logger.warning("Reddit API rate limit exceeded")
                return results
            
            # Reddit API implementation
            client_id = self.config.get("reddit_client_id") or "demo_client_id"
            client_secret = self.config.get("reddit_client_secret") or "demo_client_secret"
            user_agent = self.config.get("reddit_user_agent") or "ContentProtectionBot/1.0"
            
            async with aiohttp.ClientSession() as session:
                # Get Reddit posts
                url = "https://www.reddit.com/hot.json"
                headers = {
                    'User-Agent': user_agent
                }
                params = {
                    'limit': 25
                }
                
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for post_data in data.get('data', {}).get('children', []):
                            post = post_data.get('data', {})
                            
                            result = CrawlResult(
                                task_id=target.target_id,
                                platform=PlatformType.REDDIT,
                                content_url=f"https://reddit.com{post.get('permalink', '')}",
                                content_type='text' if not post.get('url', '').endswith(('.jpg', '.png', '.gif', '.mp4')) else 'media',
                                title=post.get('title', ''),
                                description=post.get('selftext', ''),
                                author_info={
                                    "username": post.get('author', ''),
                                    "subreddit": post.get('subreddit', '')
                                },
                                engagement_metrics={
                                    "score": post.get('score', 0),
                                    "num_comments": post.get('num_comments', 0),
                                    "upvote_ratio": post.get('upvote_ratio', 0)
                                },
                                content_metadata={
                                    "post_id": post.get('id', ''),
                                    "subreddit": post.get('subreddit', ''),
                                    "url": post.get('url', ''),
                                    "domain": post.get('domain', ''),
                                    "created_utc": post.get('created_utc', 0)
                                },
                                discovered_at=datetime.now(),
                                fingerprint_required=True,
                                dmca_candidate=True
                            )
                            results.append(result)
            
            self.logger.info(f"Reddit API crawl completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"Reddit API crawling failed: {str(e)}")
        
        return results
    
    async def _crawl_linkedin_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """LinkedIn API crawling implementation"""
        results = []
        
        try:
            # Check rate limits
            if not await self._check_rate_limit(PlatformType.LINKEDIN):
                self.logger.warning("LinkedIn API rate limit exceeded")
                return results
            
            # LinkedIn API implementation
            access_token = self.config.get("linkedin_access_token") or "demo_access_token"
            
            async with aiohttp.ClientSession() as session:
                # Get LinkedIn posts
                url = "https://api.linkedin.com/v2/posts"
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json',
                    'X-Restli-Protocol-Version': '2.0.0'
                }
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for post in data.get('elements', []):
                            result = CrawlResult(
                                task_id=target.target_id,
                                platform=PlatformType.LINKEDIN,
                                content_url=f"https://linkedin.com/posts/{post.get('id', '')}",
                                content_type='post',
                                title=post.get('commentary', '')[:100] if post.get('commentary') else 'LinkedIn Post',
                                description=post.get('commentary', ''),
                                author_info={
                                    "author_id": post.get('author', ''),
                                    "post_id": post.get('id', '')
                                },
                                engagement_metrics={
                                    "visibility": post.get('visibility', {}),
                                    "created_time": post.get('createdTime', 0)
                                },
                                content_metadata={
                                    "post_id": post.get('id', ''),
                                    "activity_urn": post.get('activity', ''),
                                    "created_time": post.get('createdTime', 0)
                                },
                                discovered_at=datetime.now(),
                                fingerprint_required=True,
                                dmca_candidate=True
                            )
                            results.append(result)
            
            self.logger.info(f"LinkedIn API crawl completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"LinkedIn API crawling failed: {str(e)}")
        
        return results
    
    async def _crawl_generic_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """Generic API crawling fallback implementation"""
        results = []
        
        try:
            self.logger.info(f"Performing generic API crawl for {self.platform.value}")
            
            # Generic web API crawling approach
            async with aiohttp.ClientSession() as session:
                # Try to get content from the target URL
                if hasattr(target, 'url') and target.url:
                    async with session.get(target.url) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            result = CrawlResult(
                                task_id=target.target_id,
                                platform=self.platform,
                                content_url=target.url,
                                content_type='web_content',
                                title=f"Content from {self.platform.value}",
                                description=content[:500] if content else '',
                                author_info={
                                    "source": self.platform.value
                                },
                                engagement_metrics={
                                    "response_status": response.status,
                                    "content_length": len(content)
                                },
                                content_metadata={
                                    "url": target.url,
                                    "platform": self.platform.value,
                                    "method": "generic_api"
                                },
                                discovered_at=datetime.now(),
                                fingerprint_required=True,
                                dmca_candidate=True
                            )
                            results.append(result)
            
            self.logger.info(f"Generic API crawl completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"Generic API crawling failed: {str(e)}")
        
        return results
    
    async def _crawl_tiktok_scraping(self, target: CrawlTarget) -> List[CrawlResult]:
        """TikTok web scraping implementation"""
        results = []
        
        try:
            import aiohttp
            from bs4 import BeautifulSoup
            import re
            import json
            
            # Check rate limits
            if not await self._check_rate_limit(PlatformType.TIKTOK):
                self.logger.warning("TikTok scraping rate limit exceeded")
                return results
            
            # Build search URLs based on target
            urls_to_scrape = []
            
            if target.url:
                urls_to_scrape.append(target.url)
            elif target.creator_handles:
                # Build profile URLs
                for handle in target.creator_handles:
                    clean_handle = handle.lstrip('@')
                    urls_to_scrape.append(f"https://www.tiktok.com/@{clean_handle}")
            elif target.search_terms:
                # TikTok doesn't have a direct search URL we can scrape easily
                # Use hashtag URLs instead
                for term in target.search_terms:
                    clean_term = term.replace(' ', '').replace('#', '')
                    urls_to_scrape.append(f"https://www.tiktok.com/tag/{clean_term}")
            
            if not urls_to_scrape:
                self.logger.warning("No valid TikTok URLs to scrape")
                return results
            
            # Setup headers to mimic real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                for url in urls_to_scrape[:3]:  # Limit to 3 URLs to avoid overwhelming
                    try:
                        async with session.get(url) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Extract video data from script tags (TikTok embeds data in JSON)
                                script_tags = soup.find_all('script', {'id': '__UNIVERSAL_DATA_FOR_REHYDRATION__'})
                                
                                for script in script_tags:
                                    try:
                                        script_content = script.string
                                        if script_content:
                                            data = json.loads(script_content)
                                            videos = self._extract_tiktok_videos_from_data(data, target.target_id)
                                            results.extend(videos)
                                    except (json.JSONDecodeError, KeyError) as e:
                                        self.logger.debug(f"Error parsing TikTok JSON data: {e}")
                                
                                # Fallback: extract from HTML structure
                                if not results:
                                    video_elements = soup.find_all('div', {'data-e2e': 'video-feed-item'})
                                    for element in video_elements[:5]:  # Limit to 5 videos per page
                                        video_data = self._extract_tiktok_video_from_element(element, target.target_id)
                                        if video_data:
                                            results.append(video_data)
                            
                            elif response.status == 429:
                                self.logger.warning("TikTok rate limiting detected")
                                break
                            else:
                                self.logger.warning(f"TikTok scraping error for {url}: {response.status}")
                    
                    except Exception as e:
                        self.logger.error(f"Error scraping TikTok URL {url}: {str(e)}")
                        continue
            
            # Update rate limiter
            await self._record_api_request(PlatformType.TIKTOK)
            
            self.logger.info(f"TikTok scraping completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"TikTok scraping failed: {str(e)}")
        
        return results
    
    async def _crawl_instagram_scraping(self, target: CrawlTarget) -> List[CrawlResult]:
        """Instagram web scraping implementation"""
        results = []
        
        try:
            import aiohttp
            from bs4 import BeautifulSoup
            import re
            import json
            
            # Check rate limits
            if not await self._check_rate_limit(PlatformType.INSTAGRAM):
                self.logger.warning("Instagram scraping rate limit exceeded")
                return results
            
            # Build URLs to scrape
            urls_to_scrape = []
            
            if target.url:
                urls_to_scrape.append(target.url)
            elif target.creator_handles:
                for handle in target.creator_handles:
                    clean_handle = handle.lstrip('@')
                    urls_to_scrape.append(f"https://www.instagram.com/{clean_handle}/")
            elif target.search_terms:
                # Use hashtag URLs for search terms
                for term in target.search_terms:
                    clean_term = term.replace(' ', '').replace('#', '')
                    urls_to_scrape.append(f"https://www.instagram.com/explore/tags/{clean_term}/")
            
            if not urls_to_scrape:
                self.logger.warning("No valid Instagram URLs to scrape")
                return results
            
            # Setup headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'X-Requested-With': 'XMLHttpRequest',
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                for url in urls_to_scrape[:3]:  # Limit to avoid overwhelming
                    try:
                        async with session.get(url) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Extract data from Instagram's embedded JSON
                                script_tags = soup.find_all('script', string=re.compile('window\._sharedData'))
                                
                                for script in script_tags:
                                    try:
                                        script_content = script.string
                                        if script_content:
                                            # Extract JSON data
                                            json_match = re.search(r'window._sharedData = ({.*?});', script_content)
                                            if json_match:
                                                data = json.loads(json_match.group(1))
                                                posts = self._extract_instagram_posts_from_data(data, target.target_id)
                                                results.extend(posts)
                                    except (json.JSONDecodeError, AttributeError) as e:
                                        self.logger.debug(f"Error parsing Instagram JSON data: {e}")
                                
                                # Fallback: extract from meta tags and visible elements
                                if not results:
                                    meta_tags = soup.find_all('meta', {'property': 'og:image'})
                                    for meta in meta_tags[:5]:  # Limit results
                                        image_url = meta.get('content', '')
                                        if image_url and 'instagram' in image_url:
                                            result = CrawlResult(
                                                task_id=target.target_id,
                                                platform=PlatformType.INSTAGRAM,
                                                content_url=url,
                                                content_type="image",
                                                title="Instagram Post",
                                                description="",
                                                creator_info={},
                                                engagement_metrics={},
                                                content_metadata={
                                                    "image_url": image_url,
                                                    "source_url": url
                                                },
                                                discovered_at=datetime.now(),
                                                fingerprint_required=True,
                                                dmca_candidate=True
                                            )
                                            results.append(result)
                            
                            elif response.status == 429:
                                self.logger.warning("Instagram rate limiting detected")
                                break
                            else:
                                self.logger.warning(f"Instagram scraping error for {url}: {response.status}")
                    
                    except Exception as e:
                        self.logger.error(f"Error scraping Instagram URL {url}: {str(e)}")
                        continue
            
            # Update rate limiter
            await self._record_api_request(PlatformType.INSTAGRAM)
            
            self.logger.info(f"Instagram scraping completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"Instagram scraping failed: {str(e)}")
        
        return results
    
    async def _crawl_generic_scraping(self, target: CrawlTarget) -> List[CrawlResult]:
        """Generic web scraping implementation"""
        results = []
        
        try:
            import aiohttp
            from bs4 import BeautifulSoup
            import re
            from urllib.parse import urljoin, urlparse
            
            # Only process if we have specific URLs
            if not target.url:
                self.logger.warning("Generic scraping requires specific URL")
                return results
            
            urls_to_scrape = [target.url] if isinstance(target.url, str) else target.url
            
            # Setup headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                for url in urls_to_scrape[:5]:  # Limit URLs
                    try:
                        parsed_url = urlparse(url)
                        domain = parsed_url.netloc
                        
                        async with session.get(url) as response:
                            if response.status == 200:
                                html = await response.text()
                                soup = BeautifulSoup(html, 'html.parser')
                                
                                # Extract page metadata
                                title = ""
                                description = ""
                                
                                # Get title
                                title_tag = soup.find('title')
                                if title_tag:
                                    title = title_tag.get_text().strip()
                                
                                # Get description from meta tags
                                meta_desc = soup.find('meta', {'name': 'description'}) or soup.find('meta', {'property': 'og:description'})
                                if meta_desc:
                                    description = meta_desc.get('content', '').strip()
                                
                                # Find media content
                                media_elements = []
                                
                                # Find images
                                images = soup.find_all('img', src=True)
                                for img in images[:10]:  # Limit to 10 images
                                    img_src = img.get('src', '')
                                    if img_src:
                                        img_url = urljoin(url, img_src)
                                        media_elements.append({
                                            'type': 'image',
                                            'url': img_url,
                                            'alt': img.get('alt', ''),
                                            'title': img.get('title', '')
                                        })
                                
                                # Find videos
                                videos = soup.find_all('video', src=True)
                                for video in videos[:5]:  # Limit to 5 videos
                                    video_src = video.get('src', '')
                                    if video_src:
                                        video_url = urljoin(url, video_src)
                                        media_elements.append({
                                            'type': 'video',
                                            'url': video_url,
                                            'poster': video.get('poster', '')
                                        })
                                
                                # Find audio
                                audios = soup.find_all('audio', src=True)
                                for audio in audios[:5]:  # Limit to 5 audio files
                                    audio_src = audio.get('src', '')
                                    if audio_src:
                                        audio_url = urljoin(url, audio_src)
                                        media_elements.append({
                                            'type': 'audio',
                                            'url': audio_url
                                        })
                                
                                # Create results for each media element found
                                if media_elements:
                                    for media in media_elements:
                                        content_type = media['type']
                                        
                                        # Determine if this content needs fingerprinting
                                        fingerprint_required = content_type in ['image', 'video', 'audio']
                                        
                                        result = CrawlResult(
                                            task_id=target.target_id,
                                            platform=PlatformType.GENERIC_WEB,
                                            content_url=media['url'],
                                            content_type=content_type,
                                            title=media.get('title') or media.get('alt') or title,
                                            description=description,
                                            creator_info={
                                                'domain': domain,
                                                'source_url': url
                                            },
                                            engagement_metrics={},
                                            content_metadata={
                                                'original_page_url': url,
                                                'domain': domain,
                                                'media_metadata': media,
                                                'page_title': title,
                                                'discovered_via': 'generic_scraping'
                                            },
                                            discovered_at=datetime.now(),
                                            fingerprint_required=fingerprint_required,
                                            dmca_candidate=fingerprint_required
                                        )
                                        results.append(result)
                                else:
                                    # No media found, create a text content result
                                    text_content = soup.get_text()[:1000]  # First 1000 chars
                                    
                                    result = CrawlResult(
                                        task_id=target.target_id,
                                        platform=PlatformType.GENERIC_WEB,
                                        content_url=url,
                                        content_type="text",
                                        title=title,
                                        description=description,
                                        creator_info={
                                            'domain': domain
                                        },
                                        engagement_metrics={},
                                        content_metadata={
                                            'domain': domain,
                                            'text_content_preview': text_content,
                                            'discovered_via': 'generic_scraping'
                                        },
                                        discovered_at=datetime.now(),
                                        fingerprint_required=False,
                                        dmca_candidate=False
                                    )
                                    results.append(result)
                            
                            elif response.status == 429:
                                self.logger.warning("Rate limiting detected for generic scraping")
                                break
                            else:
                                self.logger.warning(f"Generic scraping error for {url}: {response.status}")
                    
                    except Exception as e:
                        self.logger.error(f"Error scraping generic URL {url}: {str(e)}")
                        continue
            
            self.logger.info(f"Generic scraping completed: {len(results)} items found")
            
        except Exception as e:
            self.logger.error(f"Generic scraping failed: {str(e)}")
        
        return results
    
    async def _crawl_tiktok_selenium(self, target: CrawlTarget, driver) -> List[CrawlResult]:
        """TikTok Selenium crawling implementation"""
        return []
    
    async def _crawl_instagram_selenium(self, target: CrawlTarget, driver) -> List[CrawlResult]:
        """
Instagram Selenium crawling implementation"""
        return []
    
    async def _crawl_generic_selenium(self, target: CrawlTarget, driver) -> List[CrawlResult]:
        """
Generic Selenium crawling implementation"""
        return []
    
    # Helper methods for API implementations
    async def _get_youtube_video_details(self, video_id: str, api_key: str, session) -> Dict[str, Any]:
        """
Get detailed YouTube video information"""
        try:
            details_url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                "part": "statistics,contentDetails,snippet",
                "id": video_id,
                "key": api_key
            }
            
            async with session.get(details_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get("items", [])
                    if items:
                        video = items[0]
                        return {
                            "engagement": {
                                "view_count": int(video.get("statistics", {}).get("viewCount", 0)),
                                "like_count": int(video.get("statistics", {}).get("likeCount", 0)),
                                "comment_count": int(video.get("statistics", {}).get("commentCount", 0))
                            },
                            "duration": video.get("contentDetails", {}).get("duration", ""),
                            "category_id": video.get("snippet", {}).get("categoryId", ""),
                            "tags": video.get("snippet", {}).get("tags", [])
                        }
        except Exception as e:
            self.logger.error(f"Error getting YouTube video details: {str(e)}")
        
        return {}
    
    async def _get_spotify_access_token(self, client_id: str, client_secret: str) -> Optional[str]:
        """Get Spotify access token using Client Credentials Flow"""
        try:
            import aiohttp
            import base64
            
            # Encode credentials
            credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            
            token_url = "https://accounts.spotify.com/api/token"
            headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = "grant_type=client_credentials"
            
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(token_url, headers=headers, data=data) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        return token_data.get("access_token")
                    else:
                        self.logger.error(f"Spotify token request failed: {response.status}")
        
        except Exception as e:
            self.logger.error(f"Error getting Spotify access token: {str(e)}")
        
        return None
    
    async def _get_spotify_audio_features(self, track_id: str, access_token: str, session) -> Optional[Dict[str, Any]]:
        """Get Spotify audio features for a track"""
        try:
            features_url = f"https://api.spotify.com/v1/audio-features/{track_id}"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            async with session.get(features_url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    # Audio features not available for this track
                    return None
                else:
                    self.logger.warning(f"Error getting audio features: {response.status}")
        
        except Exception as e:
            self.logger.error(f"Error getting Spotify audio features: {str(e)}")
        
        return None
    
    async def _check_rate_limit(self, platform: PlatformType) -> bool:
        """Check if platform API rate limit allows request"""
        try:
            current_time = datetime.now()
            
            # Initialize rate limiter for platform if not exists
            if platform not in self.rate_limiters:
                self.rate_limiters[platform] = {"requests": deque(), "last_reset": current_time}
            
            limiter = self.rate_limiters[platform]
            
            # Remove old requests (older than 1 hour)
            hour_ago = current_time - timedelta(hours=1)
            while limiter["requests"] and limiter["requests"][0] < hour_ago:
                limiter["requests"].popleft()
            
            # Platform-specific rate limits (requests per hour)
            rate_limits = {
                PlatformType.YOUTUBE: 10000,  # YouTube Data API quota
                PlatformType.TWITTER: 450,    # Twitter API v2 search limit
                PlatformType.SPOTIFY: 1000,   # Spotify Web API limit
                PlatformType.INSTAGRAM: 200,  # Instagram Basic Display API
                PlatformType.TIKTOK: 100,     # TikTok API limit
            }
            
            limit = rate_limits.get(platform, 100)  # Default limit
            
            # Check if we're under the limit
            if len(limiter["requests"]) < limit:
                return True
            else:
                self.logger.warning(f"Rate limit exceeded for {platform.value}: {len(limiter['requests'])}/{limit}")
                return False
        
        except Exception as e:
            self.logger.error(f"Error checking rate limit: {str(e)}")
            return False  # Fail safe
    
    async def _record_api_request(self, platform -> None: PlatformType) -> None:
        """Record an API request for rate limiting"""
        try:
            current_time = datetime.now()
            
            if platform not in self.rate_limiters:
                self.rate_limiters[platform] = {"requests": deque(), "last_reset": current_time}
            
            self.rate_limiters[platform]["requests"].append(current_time)
            
        except Exception as e:
            self.logger.error(f"Error recording API request: {str(e)}")
    
    def _extract_tiktok_videos_from_data(self, data: Dict[str, Any], task_id: str) -> List[CrawlResult]:
        """Extract TikTok video data from JSON structure"""
        results = []
        
        try:
            # Navigate through TikTok's data structure
            default_scope = data.get('__DEFAULT_SCOPE__', {})
            
            # Look for video data in various possible locations
            video_lists = []
            
            # Check for ItemList (common structure)
            item_list = default_scope.get('webapp.video-detail', {}).get('itemInfo', {}).get('itemStruct')
            if item_list:
                video_lists.append([item_list])
            
            # Check for video feed
            video_feed = default_scope.get('webapp.video-feed', {})
            if video_feed and 'items' in video_feed:
                video_lists.append(video_feed['items'])
            
            # Process found videos
            for video_list in video_lists:
                for video_data in video_list:
                    if isinstance(video_data, dict) and 'id' in video_data:
                        result = self._create_tiktok_result_from_data(video_data, task_id)
                        if result:
                            results.append(result)
                            
                    if len(results) >= 10:  # Limit results
                        break
                        
                if len(results) >= 10:
                    break
        
        except Exception as e:
            self.logger.debug(f"Error extracting TikTok video data: {e}")
        
        return results
    
    def _create_tiktok_result_from_data(self, video_data: Dict[str, Any], task_id: str) -> Optional[CrawlResult]:
        """Create CrawlResult from TikTok video data"""
        try:
            video_id = video_data.get('id', '')
            if not video_id:
                return None
                
            # Extract basic info
            desc = video_data.get('desc', '')
            author_info = video_data.get('author', {})
            stats = video_data.get('stats', {})
            video_info = video_data.get('video', {})
            
            result = CrawlResult(
                task_id=task_id,
                platform=PlatformType.TIKTOK,
                content_url=f"https://www.tiktok.com/@{author_info.get('uniqueId', 'user')}/video/{video_id}",
                content_type="video",
                title=desc[:100] if desc else f"TikTok video by @{author_info.get('uniqueId', 'unknown')}",
                description=desc,
                creator_info={
                    'user_id': author_info.get('id', ''),
                    'username': author_info.get('uniqueId', ''),
                    'display_name': author_info.get('nickname', ''),
                    'follower_count': author_info.get('followerCount', 0),
                    'verified': author_info.get('verified', False)
                },
                engagement_metrics={
                    'view_count': stats.get('playCount', 0),
                    'like_count': stats.get('diggCount', 0),
                    'comment_count': stats.get('commentCount', 0),
                    'share_count': stats.get('shareCount', 0)
                },
                content_metadata={
                    'video_id': video_id,
                    'duration': video_info.get('duration', 0),
                    'create_time': video_data.get('createTime', 0),
                    'cover_url': video_info.get('cover', ''),
                    'play_url': video_info.get('playAddr', ''),
                    'music_info': video_data.get('music', {})
                },
                discovered_at=datetime.now(),
                fingerprint_required=True,
                dmca_candidate=True
            )
            
            return result
            
        except Exception as e:
            self.logger.debug(f"Error creating TikTok result: {e}")
            return None
    
    def _extract_tiktok_video_from_element(self, element, task_id: str) -> Optional[CrawlResult]:
        """Extract TikTok video data from HTML element"""
        try:
            # This is a fallback method for when JSON parsing fails
            # Extract what we can from HTML structure
            
            video_link = element.find('a')
            video_url = ""
            if video_link and video_link.get('href'):
                video_url = video_link.get('href')
                if not video_url.startswith('http'):
                    video_url = f"https://www.tiktok.com{video_url}"
            
            if not video_url:
                return None
            
            # Try to extract basic info from HTML
            desc_element = element.find('[data-e2e="video-desc"]')
            description = desc_element.get_text().strip() if desc_element else ""
            
            author_element = element.find('[data-e2e="video-author"]')
            author = author_element.get_text().strip() if author_element else "unknown"
            
            result = CrawlResult(
                task_id=task_id,
                platform=PlatformType.TIKTOK,
                content_url=video_url,
                content_type="video",
                title=description[:100] if description else f"TikTok video by {author}",
                description=description,
                creator_info={
                    'username': author,
                    'extracted_via': 'html_parsing'
                },
                engagement_metrics={},
                content_metadata={
                    'extracted_via': 'html_parsing',
                    'source_element': 'video-feed-item'
                },
                discovered_at=datetime.now(),
                fingerprint_required=True,
                dmca_candidate=True
            )
            
            return result
            
        except Exception as e:
            self.logger.debug(f"Error extracting TikTok video from element: {e}")
            return None
    
    def _extract_instagram_posts_from_data(self, data: Dict[str, Any], task_id: str) -> List[CrawlResult]:
        """Extract Instagram post data from JSON structure"""
        results = []
        
        try:
            # Navigate Instagram's complex data structure
            entry_data = data.get('entry_data', {})
            
            # Check different page types
            page_types = ['ProfilePage', 'PostPage', 'TagPage']
            
            for page_type in page_types:
                pages = entry_data.get(page_type, [])
                
                for page in pages:
                    graphql = page.get('graphql', {})
                    
                    # Profile page
                    if page_type == 'ProfilePage':
                        user = graphql.get('user', {})
                        edge_owner_to_timeline_media = user.get('edge_owner_to_timeline_media', {})
                        edges = edge_owner_to_timeline_media.get('edges', [])
                        
                        for edge in edges[:10]:  # Limit results
                            node = edge.get('node', {})
                            result = self._create_instagram_result_from_node(node, task_id, user.get('username', ''))
                            if result:
                                results.append(result)
                    
                    # Post page
                    elif page_type == 'PostPage':
                        shortcode_media = graphql.get('shortcode_media', {})
                        if shortcode_media:
                            owner = shortcode_media.get('owner', {})
                            result = self._create_instagram_result_from_node(shortcode_media, task_id, owner.get('username', ''))
                            if result:
                                results.append(result)
                    
                    # Tag page
                    elif page_type == 'TagPage':
                        hashtag = graphql.get('hashtag', {})
                        edge_hashtag_to_media = hashtag.get('edge_hashtag_to_media', {})
                        edges = edge_hashtag_to_media.get('edges', [])
                        
                        for edge in edges[:10]:  # Limit results
                            node = edge.get('node', {})
                            owner = node.get('owner', {})
                            result = self._create_instagram_result_from_node(node, task_id, owner.get('username', ''))
                            if result:
                                results.append(result)
                    
                    if len(results) >= 10:  # Overall limit
                        break
                        
                if len(results) >= 10:
                    break
        
        except Exception as e:
            self.logger.debug(f"Error extracting Instagram post data: {e}")
        
        return results
    
    def _create_instagram_result_from_node(self, node: Dict[str, Any], task_id: str, username: str) -> Optional[CrawlResult]:
        """Create CrawlResult from Instagram node data"""
        try:
            shortcode = node.get('shortcode', '')
            if not shortcode:
                return None
            
            # Determine content type
            content_type = "image"  # Default
            if node.get('is_video', False):
                content_type = "video"
            elif node.get('__typename') == 'GraphSidecar':
                content_type = "carousel"
            
            # Extract engagement metrics
            edge_liked_by = node.get('edge_liked_by', {})
            edge_media_to_comment = node.get('edge_media_to_comment', {})
            
            result = CrawlResult(
                task_id=task_id,
                platform=PlatformType.INSTAGRAM,
                content_url=f"https://www.instagram.com/p/{shortcode}/",
                content_type=content_type,
                title=f"Instagram {content_type} by @{username}",
                description=self._extract_instagram_caption(node),
                creator_info={
                    'username': username,
                    'user_id': node.get('owner', {}).get('id', ''),
                    'is_verified': node.get('owner', {}).get('is_verified', False)
                },
                engagement_metrics={
                    'like_count': edge_liked_by.get('count', 0),
                    'comment_count': edge_media_to_comment.get('count', 0),
                    'view_count': node.get('video_view_count', 0) if content_type == 'video' else 0
                },
                content_metadata={
                    'shortcode': shortcode,
                    'id': node.get('id', ''),
                    'taken_at_timestamp': node.get('taken_at_timestamp', 0),
                    'display_url': node.get('display_url', ''),
                    'is_video': node.get('is_video', False),
                    'video_url': node.get('video_url', '') if content_type == 'video' else '',
                    'dimensions': node.get('dimensions', {}),
                    'location': node.get('location', {})
                },
                discovered_at=datetime.now(),
                fingerprint_required=True,
                dmca_candidate=True
            )
            
            return result
            
        except Exception as e:
            self.logger.debug(f"Error creating Instagram result: {e}")
            return None
    
    def _extract_instagram_caption(self, node: Dict[str, Any]) -> str:
        try:
                    # AI model processing
                    if not hasattr(self, 'model') or self.model is None:
                        raise RuntimeError("AI model not initialized")
            
                    # Preprocess input
                    processed_input = await self._preprocess__extract_instagram_caption_input(node)
            
                    # Run inference
                    result = await self.model.predict(processed_input)
            
                    # Postprocess result
                    final_result = await self._postprocess__extract_instagram_caption_result(result)
            
                    logger.info(f"AI processing _extract_instagram_caption completed")
                    return final_result
            
                except Exception as e:
                    logger.error(f"AI processing _extract_instagram_caption failed: {e}")
                    raise
        return ""


# Utility functions
def create_crawler_deployment_config() -> Dict[str, Any]:
    """Create default crawler deployment configuration"""
    return {
        'platforms': {
            'youtube': {
                'enabled': True,
                'replicas': 3,
                'rate_limit': 100,
                'memory_limit': '2Gi',
                'cpu_limit': '1',
                'proxy_enabled': True
            },
            'tiktok': {
                'enabled': True,
                'replicas': 2,
                'rate_limit': 60,
                'memory_limit': '3Gi',
                'cpu_limit': '1.5',
                'proxy_enabled': True
            },
            'instagram': {
                'enabled': True,
                'replicas': 2,
                'rate_limit': 80,
                'memory_limit': '2Gi',
                'cpu_limit': '1',
                'proxy_enabled': True
            },
            'twitter': {
                'enabled': True,
                'replicas': 2,
                'rate_limit': 150,
                'memory_limit': '1Gi',
                'cpu_limit': '500m',
                'proxy_enabled': False  # API-based
            }
        },
        'proxy_enabled': True,
        'monitoring_enabled': True,
        'auto_scaling': {
            'enabled': True,
            'min_replicas': 1,
            'max_replicas': 10,
            'target_cpu_utilization': 70
        }
    }

# File has syntax issues - needs manual review