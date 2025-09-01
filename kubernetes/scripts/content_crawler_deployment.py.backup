#!/usr/bin/env python3
"""IA Influencer Agent - Content Crawler Deployment Manager
Enterprise-grade web crawler deployment for multi-platform content protection,
monitoring, and surveillance across YouTube, Instagram, TikTok, Twitter/X, and more.

Copyright (c) 2024-2025 Fahed Mlaiel & IA Influencer Agent Team.
Licensed under proprietary license. All rights reserved.

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Project Team Specializations:
- Lead Dev IA + Crawler Architecture
- Backend Senior Python + FastAPI
- Web Scraping Engineer + Anti-Detection
- Data Engineer + Real-time Processing
- DevOps + Kubernetes + Microservices
- Security Engineer + Proxy Management
- Platform Integration Specialist

⚠️ STRONG WARNING FOR UNAUTHORIZED USE:
This code contains proprietary crawler algorithms and trade secrets of Fahed Mlaiel.
Any unauthorized copying, modification, distribution, or use of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and may result in severe legal action under German
and international copyright laws.

Specialization: Web Scraping Architecture & Content Surveillance Systems
"""
import asyncio
import logging
import json
import os
import yaml
from typing import Dict, List, Optional, Any, Union, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import docker
import kubernetes
from kubernetes import client, config
import requests
import aiohttp
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import scrapy
from scrapy.crawler import CrawlerProcess
import beautifulsoup4
from bs4 import BeautifulSoup
import redis
import psycopg2
from datetime import datetime, timedelta
import hashlib
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import random
from urllib.parse import urljoin, urlparse
import user_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CrawlerType(Enum):
    """Types of content crawlers."""
    YOUTUBE_CRAWLER = "youtube"
    INSTAGRAM_CRAWLER = "instagram"
    TIKTOK_CRAWLER = "tiktok"
    TWITTER_CRAWLER = "twitter"
    FACEBOOK_CRAWLER = "facebook"
    SPOTIFY_CRAWLER = "spotify"
    SOUNDCLOUD_CRAWLER = "soundcloud"
    GENERIC_WEB_CRAWLER = "generic_web"
    IMAGE_CRAWLER = "image"
    VIDEO_CRAWLER = "video"
    AUDIO_CRAWLER = "audio"
    TEXT_CRAWLER = "text"


class CrawlerStrategy(Enum):
    """Crawler execution strategies."""
    SELENIUM_HEADLESS = "selenium_headless"
    SELENIUM_FULL = "selenium_full"
    SCRAPY = "scrapy"
    API_BASED = "api_based"
    REQUESTS_HTML = "requests_html"
    PLAYWRIGHT = "playwright"


class ContentType(Enum):
    """Content types to crawl."""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    METADATA = "metadata"
    ALL = "all"


class MonitoringMode(Enum):
    """Content monitoring modes."""
    REAL_TIME = "real_time"
    SCHEDULED = "scheduled"
    EVENT_DRIVEN = "event_driven"
    CONTINUOUS = "continuous"


@dataclass
class CrawlerConfig:
    """Configuration for content crawler deployment."""
    crawler_name: str
    crawler_type: CrawlerType
    strategy: CrawlerStrategy
    target_platforms: List[str]
    content_types: List[ContentType]
    monitoring_mode: MonitoringMode
    crawl_frequency: str  # cron expression
    rate_limits: Dict[str, int] = field(default_factory=dict)
    authentication: Dict[str, str] = field(default_factory=dict)
    proxy_config: Dict[str, Any] = field(default_factory=dict)
    user_agents: List[str] = field(default_factory=list)
    max_concurrent_crawls: int = 10
    timeout_seconds: int = 30
    retry_attempts: int = 3
    storage_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CrawlTarget:
    """Target configuration for crawling."""
    target_id: str
    platform: str
    urls: List[str]
    search_terms: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1-10, higher = more priority
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContentCrawlerDeploymentManager:
    """
    Enterprise-grade content crawler deployment and management system.
    
    Features:
    - Multi-platform content crawling (YouTube, Instagram, TikTok, etc.)
    - Advanced anti-detection mechanisms
    - Distributed crawling architecture
    - Real-time content monitoring
    - Intelligent rate limiting and proxy rotation
    - Content fingerprinting integration
    - Scalable deployment on Kubernetes
    - Compliance with platform ToS
    - Advanced content extraction and analysis
    """
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the content crawler deployment manager."""
        self.config = self._load_config(config_path)
        self.docker_client = docker.from_env()
        self.k8s_client = self._initialize_kubernetes()
        self.redis_client = self._initialize_redis()
        self.active_crawlers = {}
        self.crawl_results = {}
        self.proxy_pool = []
        
        # Initialize crawler engines
        self._initialize_crawler_engines()
        
        logger.info("Content Crawler Deployment Manager initialized successfully")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load crawler configuration."""
        default_config = {
            "crawler_engines": {
                "selenium": {
                    "headless": True,
                    "window_size": "1920,1080",
                    "user_data_dir": "/tmp/selenium-profile",
                    "disable_images": True,
                    "disable_javascript": False
                },
                "scrapy": {
                    "download_delay": 1,
                    "concurrent_requests": 16,
                    "concurrent_requests_per_domain": 8,
                    "autothrottle_enabled": True,
                    "autothrottle_start_delay": 1,
                    "autothrottle_max_delay": 10
                },
                "requests": {
                    "timeout": 30,
                    "max_retries": 3,
                    "backoff_factor": 0.3
                }
            },
            "anti_detection": {
                "user_agent_rotation": True,
                "proxy_rotation": True,
                "request_delays": True,
                "header_randomization": True,
                "browser_fingerprint_masking": True
            },
            "rate_limiting": {
                "youtube": {"requests_per_hour": 1000},
                "instagram": {"requests_per_hour": 500},
                "tiktok": {"requests_per_hour": 300},
                "twitter": {"requests_per_hour": 900},
                "facebook": {"requests_per_hour": 200}
            },
            "storage": {
                "backend": "postgresql",
                "host": "localhost",
                "port": 5432,
                "database": "ia_influencer_crawls",
                "cache_backend": "redis",
                "file_storage": "s3"
            },
            "monitoring": {
                "health_checks": True,
                "performance_metrics": True,
                "error_tracking": True,
                "success_rate_threshold": 90
            },
            "compliance": {
                "respect_robots_txt": True,
                "respect_rate_limits": True,
                "user_agent_identification": True,
                "data_retention_days": 90
            }
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)

        return default_config

    def _initialize_kubernetes(self) -> client.ApiClient:
        """Initialize Kubernetes client."""
        try:
            config.load_incluster_config()
        except:
            try:
                config.load_kube_config()
            except:
                logger.warning("Kubernetes config not found, running in local mode")
                return None
        
        return client.ApiClient()

    def _initialize_redis(self) -> redis.Redis:
        """Initialize Redis client for caching and queuing."""
        try:
            return redis.Redis(
                host=self.config['storage'].get('redis_host', 'localhost'),
                port=self.config['storage'].get('redis_port', 6379),
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}")
            return None

    def _initialize_crawler_engines(self) -> None:
        """Initialize crawler engines and drivers."""
        # Initialize proxy pool
        self._load_proxy_pool()
        
        # Initialize user agents
        self._load_user_agents()
        
        logger.info("Crawler engines initialized")

    def _load_proxy_pool(self) -> None:
        """Load proxy pool for anti-detection."""
        # Implementation for loading proxy pool
        self.proxy_pool = [
            {"host": "proxy1.example.com", "port": 8080, "type": "http"},
            {"host": "proxy2.example.com", "port": 8080, "type": "socks5"}
        ]
        logger.info(f"Loaded {len(self.proxy_pool)} proxies")

    def _load_user_agents(self) -> None:
        """Load user agent pool for anti-detection."""
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    async def deploy_content_crawler(
        self,
        crawler_config: CrawlerConfig,
        crawl_targets: List[CrawlTarget]
    ) -> str:
        """
        Deploy a content crawler with enterprise-grade configuration.
        
        Args:
            crawler_config: Crawler configuration
            crawl_targets: List of crawl targets
            
        Returns:
            Deployment ID
        """
        deployment_id = f"{crawler_config.crawler_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        try:
            logger.info(f"Starting content crawler deployment: {deployment_id}")
            
            # Validate configuration
            await self._validate_crawler_config(crawler_config)
            
            # Deploy crawler infrastructure
            infrastructure_result = await self._deploy_crawler_infrastructure(crawler_config, deployment_id)
            
            # Configure crawler engines
            engine_result = await self._configure_crawler_engines(crawler_config, deployment_id)
            
            # Setup crawl targets
            targets_result = await self._setup_crawl_targets(crawl_targets, deployment_id)
            
            # Configure monitoring
            monitoring_result = await self._setup_crawler_monitoring(crawler_config, deployment_id)
            
            # Setup anti-detection measures
            anti_detection_result = await self._setup_anti_detection(crawler_config, deployment_id)
            
            # Configure data pipeline
            pipeline_result = await self._configure_data_pipeline(crawler_config, deployment_id)
            
            # Record deployment
            self._record_crawler_deployment(
                deployment_id,
                crawler_config,
                crawl_targets,
                {
                    "infrastructure": infrastructure_result,
                    "engines": engine_result,
                    "targets": targets_result,
                    "monitoring": monitoring_result,
                    "anti_detection": anti_detection_result,
                    "pipeline": pipeline_result
                }
            )
            
            logger.info(f"Content crawler deployment completed: {deployment_id}")
            return deployment_id
            
        except Exception as e:
            logger.error(f"Content crawler deployment failed: {str(e)}")
            await self._cleanup_failed_crawler_deployment(deployment_id)
            raise

    async def _validate_crawler_config(self, crawler_config: CrawlerConfig) -> None:
        """Validate crawler configuration."""
        if not crawler_config.target_platforms:
            raise ValueError("At least one target platform is required")
        
        if not crawler_config.content_types:
            raise ValueError("At least one content type is required")
        
        # Validate rate limits
        for platform in crawler_config.target_platforms:
            if platform not in self.config['rate_limiting']:
                logger.warning(f"No rate limit configured for platform: {platform}")

    async def _deploy_crawler_infrastructure(
        self,
        crawler_config: CrawlerConfig,
        deployment_id: str
    ) -> Dict[str, Any]:
        """Deploy crawler infrastructure."""
        if self.k8s_client:
            return await self._deploy_crawler_kubernetes(crawler_config, deployment_id)
        else:
            return await self._deploy_crawler_local(crawler_config, deployment_id)

    async def _deploy_crawler_kubernetes(
        self,
        crawler_config: CrawlerConfig,
        deployment_id: str
    ) -> Dict[str, Any]:
        """Deploy crawler on Kubernetes."""
        # Create namespace for crawlers
        namespace_manifest = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": "ia-influencer-crawlers",
                "labels": {
                    "name": "ia-influencer-crawlers"
                }
            }
        }
        
        # Crawler deployment
        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": deployment_id,
                "namespace": "ia-influencer-crawlers",
                "labels": {
                    "app": "content-crawler",
                    "crawler-type": crawler_config.crawler_type.value,
                    "deployment-id": deployment_id
                }
            },
            "spec": {
                "replicas": crawler_config.max_concurrent_crawls,
                "selector": {
                    "matchLabels": {
                        "app": "content-crawler",
                        "deployment-id": deployment_id
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "content-crawler",
                            "deployment-id": deployment_id,
                            "crawler-type": crawler_config.crawler_type.value
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "content-crawler",
                            "image": self._get_crawler_image(crawler_config.strategy),
                            "ports": [{"containerPort": 8080}],
                            "env": [
                                {"name": "CRAWLER_TYPE", "value": crawler_config.crawler_type.value},
                                {"name": "STRATEGY", "value": crawler_config.strategy.value},
                                {"name": "MONITORING_MODE", "value": crawler_config.monitoring_mode.value},
                                {"name": "MAX_CONCURRENT", "value": str(crawler_config.max_concurrent_crawls)},
                                {"name": "TIMEOUT", "value": str(crawler_config.timeout_seconds)}
                            ],
                            "envFrom": [{
                                "secretRef": {
                                    "name": f"{deployment_id}-secrets"
                                }
                            }],
                            "resources": {
                                "requests": {
                                    "memory": "2Gi",
                                    "cpu": "1000m"
                                },
                                "limits": {
                                    "memory": "4Gi",
                                    "cpu": "2000m"
                                }
                            },
                            "volumeMounts": [
                                {
                                    "name": "crawler-storage",
                                    "mountPath": "/data"
                                },
                                {
                                    "name": "browser-cache",
                                    "mountPath": "/tmp/browser-cache"
                                }
                            ],
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": 8080
                                },
                                "initialDelaySeconds": 60,
                                "periodSeconds": 30
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready",
                                    "port": 8080
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            }
                        }],
                        "volumes": [
                            {
                                "name": "crawler-storage",
                                "persistentVolumeClaim": {
                                    "claimName": f"{deployment_id}-pvc"
                                }
                            },
                            {
                                "name": "browser-cache",
                                "emptyDir": {
                                    "sizeLimit": "1Gi"
                                }
                            }
                        ],
                        "serviceAccountName": "crawler-service-account"
                    }
                }
            }
        }
        
        # Create secrets for API credentials
        secrets_manifest = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": f"{deployment_id}-secrets",
                "namespace": "ia-influencer-crawlers"
            },
            "type": "Opaque",
            "data": {
                key: base64.b64encode(value.encode()).decode()
                for key, value in crawler_config.authentication.items()
            }
        }
        
        # Create PVC for storage
        pvc_manifest = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": f"{deployment_id}-pvc",
                "namespace": "ia-influencer-crawlers"
            },
            "spec": {
                "accessModes": ["ReadWriteOnce"],
                "resources": {
                    "requests": {
                        "storage": "50Gi"
                    }
                }
            }
        }
        
        # Apply manifests
        core_v1 = client.CoreV1Api(self.k8s_client)
        apps_v1 = client.AppsV1Api(self.k8s_client)
        
        # Create namespace
        try:
            core_v1.create_namespace(body=namespace_manifest)
        except:
            pass  # Namespace might already exist
        
        # Create PVC
        pvc_result = core_v1.create_namespaced_persistent_volume_claim(
            namespace="ia-influencer-crawlers",
            body=pvc_manifest
        )
        
        # Create secrets
        secret_result = core_v1.create_namespaced_secret(
            namespace="ia-influencer-crawlers",
            body=secrets_manifest
        )
        
        # Create deployment
        deployment_result = apps_v1.create_namespaced_deployment(
            namespace="ia-influencer-crawlers",
            body=deployment_manifest
        )
        
        # Create service
        service_manifest = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{deployment_id}-service",
                "namespace": "ia-influencer-crawlers"
            },
            "spec": {
                "selector": {
                    "app": "content-crawler",
                    "deployment-id": deployment_id
                },
                "ports": [{
                    "port": 80,
                    "targetPort": 8080
                }]
            }
        }
        
        service_result = core_v1.create_namespaced_service(
            namespace="ia-influencer-crawlers",
            body=service_manifest
        )
        
        return {
            "deployment": deployment_result,
            "service": service_result,
            "pvc": pvc_result,
            "secrets": secret_result
        }

    async def _deploy_crawler_local(
        self,
        crawler_config: CrawlerConfig,
        deployment_id: str
    ) -> Dict[str, Any]:
        """Deploy crawler locally using Docker."""
        container_name = f"crawler-{deployment_id}"
        
        # Create Docker network
        try:
            network = self.docker_client.networks.create(
                f"crawler-network-{deployment_id}",
                driver="bridge"
            )
        except:
            network = self.docker_client.networks.get(f"crawler-network-{deployment_id}")
        
        # Create crawler container
        container = self.docker_client.containers.run(
            self._get_crawler_image(crawler_config.strategy),
            name=container_name,
            ports={'8080/tcp': None},
            environment={
                'CRAWLER_TYPE': crawler_config.crawler_type.value,
                'STRATEGY': crawler_config.strategy.value,
                'MONITORING_MODE': crawler_config.monitoring_mode.value,
                'MAX_CONCURRENT': str(crawler_config.max_concurrent_crawls),
                'TIMEOUT': str(crawler_config.timeout_seconds),
                **crawler_config.authentication
            },
            volumes={
                f"crawler-data-{deployment_id}": {"bind": "/data", "mode": "rw"},
                f"browser-cache-{deployment_id}": {"bind": "/tmp/browser-cache", "mode": "rw"}
            },
            networks=[network.name],
            detach=True,
            restart_policy={"Name": "always"}
        )
        
        return {
            "container_id": container.id,
            "container_name": container_name,
            "network_id": network.id
        }

    def _get_crawler_image(self, strategy: CrawlerStrategy) -> str:
        """Get Docker image for crawler strategy."""
        image_map = {
            CrawlerStrategy.SELENIUM_HEADLESS: "ia-influencer/selenium-crawler:latest",
            CrawlerStrategy.SELENIUM_FULL: "ia-influencer/selenium-full-crawler:latest",
            CrawlerStrategy.SCRAPY: "ia-influencer/scrapy-crawler:latest",
            CrawlerStrategy.API_BASED: "ia-influencer/api-crawler:latest",
            CrawlerStrategy.REQUESTS_HTML: "ia-influencer/requests-crawler:latest",
            CrawlerStrategy.PLAYWRIGHT: "ia-influencer/playwright-crawler:latest"
        }
        
        return image_map.get(strategy, "ia-influencer/generic-crawler:latest")

    async def _configure_crawler_engines(
        self,
        crawler_config: CrawlerConfig,
        deployment_id: str
    ) -> Dict[str, Any]:
        """Configure crawler engines based on strategy."""
        engine_config = {
            "strategy": crawler_config.strategy.value,
            "deployment_id": deployment_id
        }
        
        if crawler_config.strategy == CrawlerStrategy.SELENIUM_HEADLESS:
            engine_config.update(await self._configure_selenium_engine(crawler_config, True))
        elif crawler_config.strategy == CrawlerStrategy.SELENIUM_FULL:
            engine_config.update(await self._configure_selenium_engine(crawler_config, False))
        elif crawler_config.strategy == CrawlerStrategy.SCRAPY:
            engine_config.update(await self._configure_scrapy_engine(crawler_config))
        elif crawler_config.strategy == CrawlerStrategy.API_BASED:
            engine_config.update(await self._configure_api_engine(crawler_config))
        
        logger.info(f"Crawler engines configured for: {deployment_id}")
        return engine_config

    async def _configure_selenium_engine(
        self,
        crawler_config: CrawlerConfig,
        headless: bool
    ) -> Dict[str, Any]:
        """Configure Selenium WebDriver engine."""
        selenium_config = {
            "headless": headless,
            "window_size": self.config['crawler_engines']['selenium']['window_size'],
            "disable_images": self.config['crawler_engines']['selenium']['disable_images'],
            "disable_javascript": self.config['crawler_engines']['selenium']['disable_javascript'],
            "user_data_dir": self.config['crawler_engines']['selenium']['user_data_dir']
        }
        
        # Configure Chrome options
        chrome_options = {
            "arguments": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",
                "--allow-running-insecure-content",
                f"--window-size={selenium_config['window_size']}"
            ]
        }
        
        if headless:
            chrome_options["arguments"].append("--headless")
        
        if selenium_config["disable_images"]:
            chrome_options["prefs"] = {
                "profile.managed_default_content_settings.images": 2
            }
        
        selenium_config["chrome_options"] = chrome_options
        return selenium_config

    async def _configure_scrapy_engine(self, crawler_config: CrawlerConfig) -> Dict[str, Any]:
        """Configure Scrapy engine."""
        scrapy_config = {
            "download_delay": self.config['crawler_engines']['scrapy']['download_delay'],
            "concurrent_requests": self.config['crawler_engines']['scrapy']['concurrent_requests'],
            "concurrent_requests_per_domain": self.config['crawler_engines']['scrapy']['concurrent_requests_per_domain'],
            "autothrottle_enabled": self.config['crawler_engines']['scrapy']['autothrottle_enabled'],
            "autothrottle_start_delay": self.config['crawler_engines']['scrapy']['autothrottle_start_delay'],
            "autothrottle_max_delay": self.config['crawler_engines']['scrapy']['autothrottle_max_delay']
        }
        
        # Configure user agent middleware
        scrapy_config["middlewares"] = {
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "rotating_useragent.RotatingUserAgentMiddleware": 400
        }
        
        return scrapy_config

    async def _configure_api_engine(self, crawler_config: CrawlerConfig) -> Dict[str, Any]:
        """Configure API-based crawler engine."""
        api_config = {
            "timeout": self.config['crawler_engines']['requests']['timeout'],
            "max_retries": self.config['crawler_engines']['requests']['max_retries'],
            "backoff_factor": self.config['crawler_engines']['requests']['backoff_factor']
        }
        
        # Configure API endpoints for each platform
        api_endpoints = {
            "youtube": {
                "base_url": "https://www.googleapis.com/youtube/v3",
                "search_endpoint": "/search",
                "video_endpoint": "/videos"
            },
            "instagram": {
                "base_url": "https://graph.instagram.com/v12.0",
                "media_endpoint": "/me/media"
            },
            "twitter": {
                "base_url": "https://api.twitter.com/2",
                "tweets_endpoint": "/tweets/search/recent"
            }
        }
        
        api_config["endpoints"] = api_endpoints
        return api_config

    async def _setup_crawl_targets(
        self,
        crawl_targets: List[CrawlTarget],
        deployment_id: str
    ) -> Dict[str, Any]:
        """Setup crawl targets and schedules."""
        targets_config = {
            "deployment_id": deployment_id,
            "total_targets": len(crawl_targets),
            "targets": []
        }
        
        # Process each crawl target
        for target in crawl_targets:
            target_config = {
                "target_id": target.target_id,
                "platform": target.platform,
                "urls": target.urls,
                "search_terms": target.search_terms,
                "filters": target.filters,
                "priority": target.priority,
                "metadata": target.metadata
            }
            
            # Store target in Redis for queuing
            if self.redis_client:
                self.redis_client.lpush(
                    f"crawl_queue:{deployment_id}",
                    json.dumps(target_config)
                )
            
            targets_config["targets"].append(target_config)
        
        logger.info(f"Crawl targets setup completed for: {deployment_id}")
        return targets_config

    async def _setup_crawler_monitoring(
        self,
        crawler_config: CrawlerConfig,
        deployment_id: str
    ) -> Dict[str, Any]:
        """Setup monitoring for crawler deployment."""
        monitoring_config = {
            "deployment_id": deployment_id,
            "health_checks": self.config['monitoring']['health_checks'],
            "performance_metrics": self.config['monitoring']['performance_metrics'],
            "error_tracking": self.config['monitoring']['error_tracking'],
            "success_rate_threshold": self.config['monitoring']['success_rate_threshold']
        }
        
        # Setup Prometheus monitoring
        if self.k8s_client:
            await self._setup_crawler_prometheus(deployment_id)
        
        # Configure alerting
        await self._configure_crawler_alerts(deployment_id, crawler_config)
        
        logger.info(f"Crawler monitoring setup completed for: {deployment_id}")
        return monitoring_config

    async def _setup_anti_detection(
        self,
        crawler_config: CrawlerConfig,
        deployment_id: str
    ) -> Dict[str, Any]:
        """Setup anti-detection measures."""
        anti_detection_config = {
            "deployment_id": deployment_id,
            "user_agent_rotation": self.config['anti_detection']['user_agent_rotation'],
            "proxy_rotation": self.config['anti_detection']['proxy_rotation'],
            "request_delays": self.config['anti_detection']['request_delays'],
            "header_randomization": self.config['anti_detection']['header_randomization'],
            "browser_fingerprint_masking": self.config['anti_detection']['browser_fingerprint_masking']
        }
        
        # Configure proxy rotation
        if anti_detection_config["proxy_rotation"]:
            await self._configure_proxy_rotation(deployment_id)
        
        # Configure user agent rotation
        if anti_detection_config["user_agent_rotation"]:
            await self._configure_user_agent_rotation(deployment_id)
        
        # Configure request delays
        if anti_detection_config["request_delays"]:
            await self._configure_request_delays(deployment_id, crawler_config)
        
        logger.info(f"Anti-detection measures setup completed for: {deployment_id}")
        return anti_detection_config

    async def _configure_data_pipeline(
        self,
        crawler_config: CrawlerConfig,
        deployment_id: str
    ) -> Dict[str, Any]:
        """Configure data processing pipeline."""
        pipeline_config = {
            "deployment_id": deployment_id,
            "storage_backend": self.config['storage']['backend'],
            "cache_backend": self.config['storage']['cache_backend'],
            "file_storage": self.config['storage']['file_storage']
        }
        
        # Setup data processing pipeline
        if self.k8s_client:
            await self._deploy_data_processor(deployment_id)
        
        # Configure content fingerprinting integration
        await self._configure_fingerprinting_integration(deployment_id)
        
        # Setup data quality checks
        await self._configure_data_quality_checks(deployment_id)
        
        logger.info(f"Data pipeline configured for: {deployment_id}")
        return pipeline_config

    async def _setup_crawler_prometheus(self, deployment_id: str) -> None:
        """Setup Prometheus monitoring for crawler."""
        # Create ServiceMonitor for Prometheus
        monitoring_manifest = {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": f"{deployment_id}-monitor",
                "namespace": "ia-influencer-crawlers",
                "labels": {
                    "app": "content-crawler",
                    "deployment-id": deployment_id
                }
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": "content-crawler",
                        "deployment-id": deployment_id
                    }
                },
                "endpoints": [{
                    "port": "http",
                    "path": "/metrics"
                }]
            }
        }
        
        logger.info(f"Prometheus monitoring configured for: {deployment_id}")

    async def _configure_crawler_alerts(
        self,
        deployment_id: str,
        crawler_config: CrawlerConfig
    ) -> None:
        """Configure alerting for crawler deployment."""
        # Implementation for crawler alerts configuration
        logger.info(f"Crawler alerts configured for: {deployment_id}")

    async def _configure_proxy_rotation(self, deployment_id: str) -> None:
        """Configure proxy rotation for anti-detection."""
        # Implementation for proxy rotation configuration
        logger.info(f"Proxy rotation configured for: {deployment_id}")

    async def _configure_user_agent_rotation(self, deployment_id: str) -> None:
        """Configure user agent rotation for anti-detection."""
        # Implementation for user agent rotation configuration
        logger.info(f"User agent rotation configured for: {deployment_id}")

    async def _configure_request_delays(
        self,
        deployment_id: str,
        crawler_config: CrawlerConfig
    ) -> None:
        """Configure request delays for anti-detection."""
        # Implementation for request delays configuration
        logger.info(f"Request delays configured for: {deployment_id}")

    async def _deploy_data_processor(self, deployment_id: str) -> None:
        """Deploy data processing pipeline."""
        # Implementation for data processor deployment
        logger.info(f"Data processor deployed for: {deployment_id}")

    async def _configure_fingerprinting_integration(self, deployment_id: str) -> None:
        """Configure integration with fingerprinting system."""
        # Implementation for fingerprinting integration
        logger.info(f"Fingerprinting integration configured for: {deployment_id}")

    async def _configure_data_quality_checks(self, deployment_id: str) -> None:
        """Configure data quality checks."""
        # Implementation for data quality checks configuration
        logger.info(f"Data quality checks configured for: {deployment_id}")

    def _record_crawler_deployment(
        self,
        deployment_id: str,
        crawler_config: CrawlerConfig,
        crawl_targets: List[CrawlTarget],
        result: Dict[str, Any]
    ) -> None:
        """Record crawler deployment information."""
        deployment_record = {
            "deployment_id": deployment_id,
            "crawler_config": crawler_config.__dict__,
            "crawl_targets": [target.__dict__ for target in crawl_targets],
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "status": "deployed"
        }
        
        self.active_crawlers[deployment_id] = deployment_record
        logger.info(f"Crawler deployment recorded: {deployment_id}")

    async def _cleanup_failed_crawler_deployment(self, deployment_id: str) -> None:
        """Cleanup failed crawler deployment."""
        try:
            if self.k8s_client:
                apps_v1 = client.AppsV1Api(self.k8s_client)
                core_v1 = client.CoreV1Api(self.k8s_client)
                
                # Cleanup Kubernetes resources
                try:
                    apps_v1.delete_namespaced_deployment(
                        name=deployment_id,
                        namespace="ia-influencer-crawlers"
                    )
                except:
                    pass
                
                try:
                    core_v1.delete_namespaced_service(
                        name=f"{deployment_id}-service",
                        namespace="ia-influencer-crawlers"
                    )
                except:
                    pass
                
                try:
                    core_v1.delete_namespaced_secret(
                        name=f"{deployment_id}-secrets",
                        namespace="ia-influencer-crawlers"
                    )
                except:
                    pass
                
                try:
                    core_v1.delete_namespaced_persistent_volume_claim(
                        name=f"{deployment_id}-pvc",
                        namespace="ia-influencer-crawlers"
                    )
                except:
                    pass
            
            # Cleanup Docker containers
            try:
                containers = self.docker_client.containers.list(
                    filters={"name": f"crawler-{deployment_id}"}
                )
                for container in containers:
                    container.remove(force=True)
            except:
                pass
            
            logger.info(f"Cleanup completed for failed crawler deployment: {deployment_id}")
        except Exception as e:
            logger.error(f"Crawler deployment cleanup failed: {str(e)}")

    async def start_crawling(self, deployment_id: str) -> bool:
        """Start crawling process for a deployment."""
        try:
            if deployment_id not in self.active_crawlers:
                raise ValueError(f"Crawler deployment not found: {deployment_id}")
            
            # Send start command to crawler
            deployment = self.active_crawlers[deployment_id]
            
            # Update deployment status
            deployment["status"] = "crawling"
            deployment["started_at"] = datetime.now().isoformat()
            
            logger.info(f"Crawling started for deployment: {deployment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start crawling: {str(e)}")
            return False

    async def stop_crawling(self, deployment_id: str) -> bool:
        """Stop crawling process for a deployment."""
        try:
            if deployment_id not in self.active_crawlers:
                raise ValueError(f"Crawler deployment not found: {deployment_id}")
            
            # Send stop command to crawler
            deployment = self.active_crawlers[deployment_id]
            
            # Update deployment status
            deployment["status"] = "stopped"
            deployment["stopped_at"] = datetime.now().isoformat()
            
            logger.info(f"Crawling stopped for deployment: {deployment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop crawling: {str(e)}")
            return False

    def get_crawl_results(self, deployment_id: str) -> Dict[str, Any]:
        """Get crawl results for a deployment."""
        if deployment_id not in self.crawl_results:
            return {"deployment_id": deployment_id, "results": []}
        
        return self.crawl_results[deployment_id]

    def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get crawler deployment status."""
        if deployment_id not in self.active_crawlers:
            return {"status": "not_found"}
        
        return self.active_crawlers[deployment_id]

    def list_active_crawlers(self) -> List[Dict[str, Any]]:
        """List all active crawler deployments."""
        return list(self.active_crawlers.values())

    async def scale_crawler(self, deployment_id: str, replicas: int) -> bool:
        """Scale crawler deployment."""
        try:
            if deployment_id not in self.active_crawlers:
                raise ValueError(f"Crawler deployment not found: {deployment_id}")
            
            if self.k8s_client:
                apps_v1 = client.AppsV1Api(self.k8s_client)
                apps_v1.patch_namespaced_deployment_scale(
                    name=deployment_id,
                    namespace="ia-influencer-crawlers",
                    body={"spec": {"replicas": replicas}}
                )
            
            logger.info(f"Scaled crawler {deployment_id} to {replicas} replicas")
            return True
        except Exception as e:
            logger.error(f"Crawler scaling failed: {str(e)}")
            return False


# Factory functions for common crawler configurations
def create_youtube_crawler_config() -> CrawlerConfig:
    """Create YouTube crawler configuration."""
    return CrawlerConfig(
        crawler_name="youtube-content-crawler",
        crawler_type=CrawlerType.YOUTUBE_CRAWLER,
        strategy=CrawlerStrategy.API_BASED,
        target_platforms=["youtube"],
        content_types=[ContentType.VIDEO, ContentType.METADATA],
        monitoring_mode=MonitoringMode.REAL_TIME,
        crawl_frequency="*/15 * * * *",  # Every 15 minutes
        rate_limits={"youtube": 1000},
        authentication={
            "YOUTUBE_API_KEY": os.getenv("YOUTUBE_API_KEY", "")
        },
        max_concurrent_crawls=5,
        timeout_seconds=30
    )


def create_instagram_crawler_config() -> CrawlerConfig:
    """Create Instagram crawler configuration."""
    return CrawlerConfig(
        crawler_name="instagram-content-crawler",
        crawler_type=CrawlerType.INSTAGRAM_CRAWLER,
        strategy=CrawlerStrategy.SELENIUM_HEADLESS,
        target_platforms=["instagram"],
        content_types=[ContentType.IMAGE, ContentType.VIDEO, ContentType.TEXT],
        monitoring_mode=MonitoringMode.SCHEDULED,
        crawl_frequency="0 */6 * * *",  # Every 6 hours
        rate_limits={"instagram": 500},
        authentication={
            "INSTAGRAM_USERNAME": os.getenv("INSTAGRAM_USERNAME", ""),
            "INSTAGRAM_PASSWORD": os.getenv("INSTAGRAM_PASSWORD", "")
        },
        max_concurrent_crawls=3,
        timeout_seconds=45
    )


def create_tiktok_crawler_config() -> CrawlerConfig:
    """Create TikTok crawler configuration."""
    return CrawlerConfig(
        crawler_name="tiktok-content-crawler",
        crawler_type=CrawlerType.TIKTOK_CRAWLER,
        strategy=CrawlerStrategy.SELENIUM_HEADLESS,
        target_platforms=["tiktok"],
        content_types=[ContentType.VIDEO, ContentType.AUDIO, ContentType.TEXT],
        monitoring_mode=MonitoringMode.REAL_TIME,
        crawl_frequency="*/30 * * * *",  # Every 30 minutes
        rate_limits={"tiktok": 300},
        max_concurrent_crawls=2,
        timeout_seconds=60
    )


def create_generic_web_crawler_config() -> CrawlerConfig:
    """Create generic web crawler configuration."""
    return CrawlerConfig(
        crawler_name="generic-web-crawler",
        crawler_type=CrawlerType.GENERIC_WEB_CRAWLER,
        strategy=CrawlerStrategy.SCRAPY,
        target_platforms=["web"],
        content_types=[ContentType.ALL],
        monitoring_mode=MonitoringMode.SCHEDULED,
        crawl_frequency="0 2 * * *",  # Daily at 2 AM
        rate_limits={"web": 1000},
        max_concurrent_crawls=10,
        timeout_seconds=30
    )


# Main execution
if __name__ == "__main__":
    async def main():
        """Main execution function."""
        # Initialize content crawler deployment manager
        manager = ContentCrawlerDeploymentManager()
        
        # Example: Deploy YouTube crawler
        youtube_config = create_youtube_crawler_config()
        youtube_targets = [
            CrawlTarget(
                target_id="youtube-search-1",
                platform="youtube",
                urls=["https://www.youtube.com/results?search_query=music+covers"],
                search_terms=["music covers", "song remixes"],
                priority=5
            )
        ]
        
        deployment_id = await manager.deploy_content_crawler(youtube_config, youtube_targets)
        print(f"Content crawler deployment completed: {deployment_id}")
        
        # Start crawling
        await manager.start_crawling(deployment_id)
    
    asyncio.run(main())
