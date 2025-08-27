"""
Crawler Deployment Module

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

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
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
    """Supported social media platforms"""
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
    """Result from crawling operation"""
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
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 postgres_url: str = "postgresql://localhost/ia_influencer",
                 k8s_namespace: str = "ia-influencer"):
        
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
    
    def _init_kubernetes_client(self):
        """Initialize Kubernetes client"""
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        
        self.k8s_apps_v1 = client.AppsV1Api()
        self.k8s_core_v1 = client.CoreV1Api()
        self.k8s_autoscaling = client.AutoscalingV1Api()
    
    def _init_platform_crawlers(self):
        """Initialize platform-specific crawlers"""
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
    
    async def _deploy_platform_crawlers(self, platform: str, config: Dict[str, Any]):
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
    
    async def _deploy_proxy_management(self):
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
    
    async def _deploy_rate_limiting_service(self):
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
    
    async def _setup_crawler_monitoring(self):
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
        """Validate and process crawl results"""
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
        """Determine if content requires fingerprinting"""
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
    
    async def _store_crawl_task(self, task: CrawlTask):
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
    
    async def _update_crawl_task(self, task: CrawlTask):
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
    
    async def _store_crawl_results(self, results: List[CrawlResult]):
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
    
    async def _check_dmca_violations(self, results: List[CrawlResult]):
        """Check results for potential DMCA violations"""
        for result in results:
            if result.dmca_candidate:
                # Trigger DMCA enforcement workflow
                await self._trigger_dmca_enforcement(result)
    
    async def _trigger_dmca_enforcement(self, result: CrawlResult):
        """Trigger DMCA enforcement for potential violation"""
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
    
    async def _schedule_recurring_task(self, target: CrawlTarget):
        """Schedule recurring crawl task"""
        # Implementation for scheduling recurring tasks
        # This would typically use a job scheduler like Celery
        pass
    
    async def _wait_for_task_completion(self, task_id: str, timeout: int) -> List[CrawlResult]:
        """Wait for task completion and return results"""
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
    
    def _start_background_workers(self):
        """Start background worker threads"""
        def queue_processor():
            """Process crawl queue"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def process_queue():
                while True:
                    try:
                        task = await self.crawl_queue.get()
                        await self.execute_crawl_task(task)
                        self.crawl_queue.task_done()
                    except Exception as e:
                        self.logger.error(f"Queue processor error: {str(e)}")
            
            loop.run_until_complete(process_queue())
        
        def health_monitor():
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
    
    def _update_health_metrics(self):
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
                 platform: PlatformType,
                 redis_client: redis.Redis,
                 orchestrator):
        
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
        """Get platform-specific scraping configurations"""
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
        """Crawl using official platform APIs"""
        results = []
        
        try:
            if self.platform == PlatformType.YOUTUBE:
                results = await self._crawl_youtube_api(target)
            elif self.platform == PlatformType.TWITTER:
                results = await self._crawl_twitter_api(target)
            elif self.platform == PlatformType.SPOTIFY:
                results = await self._crawl_spotify_api(target)
            else:
                raise NotImplementedError(f"API crawling not implemented for {self.platform.value}")
                
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
                results = await self._crawl_generic_scraping(target)
                
        except Exception as e:
            self.logger.error(f"Web scraping failed for {self.platform.value}: {str(e)}")
        
        return results
    
    async def crawl_via_selenium(self, target: CrawlTarget) -> List[CrawlResult]:
        """Crawl using Selenium browser automation"""
        results = []
        
        try:
            driver = uc.Chrome(options=self.browser_options)
            
            if self.platform == PlatformType.TIKTOK:
                results = await self._crawl_tiktok_selenium(target, driver)
            elif self.platform == PlatformType.INSTAGRAM:
                results = await self._crawl_instagram_selenium(target, driver)
            else:
                results = await self._crawl_generic_selenium(target, driver)
                
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
        return []
    
    async def _crawl_twitter_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """Twitter API crawling implementation"""
        return []
    
    async def _crawl_spotify_api(self, target: CrawlTarget) -> List[CrawlResult]:
        """Spotify API crawling implementation"""
        return []
    
    async def _crawl_tiktok_scraping(self, target: CrawlTarget) -> List[CrawlResult]:
        """TikTok web scraping implementation"""
        return []
    
    async def _crawl_instagram_scraping(self, target: CrawlTarget) -> List[CrawlResult]:
        """Instagram web scraping implementation"""
        return []
    
    async def _crawl_generic_scraping(self, target: CrawlTarget) -> List[CrawlResult]:
        """Generic web scraping implementation"""
        return []
    
    async def _crawl_tiktok_selenium(self, target: CrawlTarget, driver) -> List[CrawlResult]:
        """TikTok Selenium crawling implementation"""
        return []
    
    async def _crawl_instagram_selenium(self, target: CrawlTarget, driver) -> List[CrawlResult]:
        """Instagram Selenium crawling implementation"""
        return []
    
    async def _crawl_generic_selenium(self, target: CrawlTarget, driver) -> List[CrawlResult]:
        """Generic Selenium crawling implementation"""
        return []


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
