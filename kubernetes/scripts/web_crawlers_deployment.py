#!/usr/bin/env python3
"""
Web Crawlers Deployment Manager
Enterprise-grade deployment system for comprehensive web surveillance,
multi-platform content monitoring, and automated content detection.

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Project Team Specializations:
- Lead Dev IA + Crawler Architecture
- Backend Senior Python + FastAPI
- Data Engineer + Web Scraping
- Infrastructure Engineer + Distributed Systems
- DevOps + Kubernetes + Microservices
- Security Engineer + Anti-Detection Systems
- ML Engineer + Content Recognition

⚠️ STRONG WARNING FOR UNAUTHORIZED USE:
This code contains proprietary web crawling algorithms and trade secrets of Fahed Mlaiel.
Any unauthorized copying, modification, distribution, or use of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is
strictly prohibited and may result in severe legal action under German
and international copyright laws.

Project: IA Influencer Agent Platform - Web Surveillance & Content Monitoring
Copyright: Fahed Mlaiel - All rights reserved
"""

import os
import sys
import time
import json
import logging
import asyncio
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
import requests
import docker
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import redis
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import scrapy
from scrapy.crawler import CrawlerProcess
import beautifulsoup4
import aiohttp
import asyncpg
import boto3
from minio import Minio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CrawlerType(Enum):
    """Types of web crawlers"""
    YOUTUBE_CRAWLER = "youtube_crawler"
    INSTAGRAM_CRAWLER = "instagram_crawler"
    TIKTOK_CRAWLER = "tiktok_crawler"
    TWITTER_CRAWLER = "twitter_crawler"
    SPOTIFY_CRAWLER = "spotify_crawler"
    FACEBOOK_CRAWLER = "facebook_crawler"
    LINKEDIN_CRAWLER = "linkedin_crawler"
    PINTEREST_CRAWLER = "pinterest_crawler"
    SNAPCHAT_CRAWLER = "snapchat_crawler"
    TWITCH_CRAWLER = "twitch_crawler"
    SOUNDCLOUD_CRAWLER = "soundcloud_crawler"
    GENERIC_WEB_CRAWLER = "generic_web_crawler"
    SITEMAP_CRAWLER = "sitemap_crawler"
    RSS_FEED_CRAWLER = "rss_feed_crawler"
    API_CRAWLER = "api_crawler"


class CrawlingStrategy(Enum):
    """Web crawling strategies"""
    SELENIUM_BROWSER = "selenium_browser"
    REQUESTS_HTTP = "requests_http"
    SCRAPY_FRAMEWORK = "scrapy_framework"
    API_INTEGRATION = "api_integration"
    HEADLESS_CHROME = "headless_chrome"
    PROXY_ROTATION = "proxy_rotation"
    DISTRIBUTED_CRAWLING = "distributed_crawling"
    REAL_TIME_STREAMING = "real_time_streaming"


class AntiDetectionMode(Enum):
    """Anti-detection mechanisms"""
    USER_AGENT_ROTATION = "user_agent_rotation"
    PROXY_CHAIN = "proxy_chain"
    REQUEST_DELAY = "request_delay"
    CAPTCHA_SOLVING = "captcha_solving"
    BROWSER_FINGERPRINT = "browser_fingerprint"
    IP_ROTATION = "ip_rotation"
    SESSION_MANAGEMENT = "session_management"
    STEALTH_MODE = "stealth_mode"


class ContentType(Enum):
    """Types of content to monitor"""
    AUDIO_CONTENT = "audio_content"
    VIDEO_CONTENT = "video_content"
    IMAGE_CONTENT = "image_content"
    TEXT_CONTENT = "text_content"
    METADATA_ONLY = "metadata_only"
    FULL_CONTENT = "full_content"
    LINKS_ONLY = "links_only"
    HASHTAGS_ONLY = "hashtags_only"


class PlatformAPI(Enum):
    """Platform API integrations"""
    YOUTUBE_DATA_API = "youtube_data_api"
    INSTAGRAM_BASIC_API = "instagram_basic_api"
    TWITTER_API_V2 = "twitter_api_v2"
    TIKTOK_RESEARCH_API = "tiktok_research_api"
    SPOTIFY_WEB_API = "spotify_web_api"
    FACEBOOK_GRAPH_API = "facebook_graph_api"
    LINKEDIN_API = "linkedin_api"
    SOUNDCLOUD_API = "soundcloud_api"
    CUSTOM_API = "custom_api"


@dataclass
class CrawlerConfig:
    """Configuration for web crawler deployment"""
    crawler_id: str
    crawler_name: str
    crawler_type: CrawlerType
    crawling_strategy: CrawlingStrategy
    target_platforms: List[str]
    content_types: List[ContentType]
    anti_detection: List[AntiDetectionMode] = field(default_factory=list)
    api_integrations: List[PlatformAPI] = field(default_factory=list)
    crawl_frequency: int = 3600  # seconds
    max_concurrent_requests: int = 10
    request_delay_ms: int = 1000
    timeout_seconds: int = 30
    retry_attempts: int = 3
    proxy_rotation: bool = True
    user_agent_rotation: bool = True
    respect_robots_txt: bool = False
    follow_redirects: bool = True
    download_images: bool = True
    download_videos: bool = True
    extract_metadata: bool = True
    storage_path: str = "/crawler-data"
    max_storage_gb: float = 100.0
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'crawler_id': self.crawler_id,
            'crawler_name': self.crawler_name,
            'crawler_type': self.crawler_type.value,
            'crawling_strategy': self.crawling_strategy.value,
            'target_platforms': self.target_platforms,
            'content_types': [ct.value for ct in self.content_types],
            'anti_detection': [ad.value for ad in self.anti_detection],
            'api_integrations': [api.value for api in self.api_integrations],
            'crawl_frequency': self.crawl_frequency,
            'max_concurrent_requests': self.max_concurrent_requests,
            'request_delay_ms': self.request_delay_ms,
            'timeout_seconds': self.timeout_seconds,
            'retry_attempts': self.retry_attempts,
            'proxy_rotation': self.proxy_rotation,
            'user_agent_rotation': self.user_agent_rotation,
            'respect_robots_txt': self.respect_robots_txt,
            'follow_redirects': self.follow_redirects,
            'download_images': self.download_images,
            'download_videos': self.download_videos,
            'extract_metadata': self.extract_metadata,
            'storage_path': self.storage_path,
            'max_storage_gb': self.max_storage_gb,
            'enabled': self.enabled
        }


@dataclass
class ProxyConfig:
    """Proxy configuration for anti-detection"""
    proxy_provider: str
    proxy_list: List[str] = field(default_factory=list)
    rotation_interval: int = 300  # seconds
    authentication_required: bool = False
    username: str = ""
    password: str = ""
    proxy_type: str = "http"  # http, socks4, socks5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'proxy_provider': self.proxy_provider,
            'proxy_list': self.proxy_list,
            'rotation_interval': self.rotation_interval,
            'authentication_required': self.authentication_required,
            'username': self.username,
            'password': self.password,
            'proxy_type': self.proxy_type
        }


@dataclass
class DeploymentConfig:
    """Crawler system deployment configuration"""
    replicas: int = 3
    resource_limits: Dict[str, str] = field(default_factory=lambda: {
        'cpu': '2000m',
        'memory': '4Gi',
        'storage': '100Gi'
    })
    resource_requests: Dict[str, str] = field(default_factory=lambda: {
        'cpu': '500m',
        'memory': '1Gi',
        'storage': '50Gi'
    })
    auto_scaling: bool = True
    min_replicas: int = 2
    max_replicas: int = 20
    target_cpu_utilization: int = 70
    storage_class: str = "fast-ssd"
    environment_variables: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'replicas': self.replicas,
            'resource_limits': self.resource_limits,
            'resource_requests': self.resource_requests,
            'auto_scaling': self.auto_scaling,
            'min_replicas': self.min_replicas,
            'max_replicas': self.max_replicas,
            'target_cpu_utilization': self.target_cpu_utilization,
            'storage_class': self.storage_class,
            'environment_variables': self.environment_variables
        }


class WebCrawlersDeploymentManager:
    """
    Enterprise Web Crawlers Deployment Manager
    Handles deployment and management of comprehensive web surveillance systems
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Web Crawlers Deployment Manager"""
        self.config_path = config_path or os.getenv('CRAWLER_CONFIG_PATH', '/etc/crawlers/config.yaml')
        self.crawler_configs: Dict[str, CrawlerConfig] = {}
        self.proxy_configs: Dict[str, ProxyConfig] = {}
        self.deployments: Dict[str, DeploymentConfig] = {}
        
        # Initialize clients
        self._init_kubernetes_client()
        self._init_docker_client()
        self._init_redis_client()
        self._init_database_client()
        self._init_storage_client()
        
        # Load configuration
        self._load_config()
        
        # Initialize user agents and proxies
        self._init_user_agents()
        self._init_proxy_rotation()
        
        logger.info("Web Crawlers Deployment Manager initialized successfully")
    
    def _init_kubernetes_client(self):
        """Initialize Kubernetes client"""
        try:
            config.load_incluster_config()
        except:
            try:
                config.load_kube_config()
            except:
                logger.warning("Kubernetes config not found, some features may be unavailable")
                self.k8s_client = None
                return
        
        self.k8s_client = client.ApiClient()
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
        self.batch_v1 = client.BatchV1Api()
        self.autoscaling_v1 = client.AutoscalingV1Api()
        logger.info("Kubernetes client initialized")
    
    def _init_docker_client(self):
        """Initialize Docker client"""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized")
        except Exception as e:
            logger.warning(f"Docker client initialization failed: {e}")
            self.docker_client = None
    
    def _init_redis_client(self):
        """Initialize Redis client for caching and coordination"""
        try:
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', '6379'))
            redis_password = os.getenv('REDIS_PASSWORD')
            
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Redis client initialized")
        except Exception as e:
            logger.warning(f"Redis client initialization failed: {e}")
            self.redis_client = None
    
    def _init_database_client(self):
        """Initialize database client"""
        try:
            db_url = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost:5432/ia_influencer')
            self.db_url = db_url
            logger.info("Database client initialized")
        except Exception as e:
            logger.warning(f"Database client initialization failed: {e}")
            self.db_url = None
    
    def _init_storage_client(self):
        """Initialize storage clients"""
        # MinIO for file storage
        try:
            minio_endpoint = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
            minio_access_key = os.getenv('MINIO_ACCESS_KEY', 'minioadmin')
            minio_secret_key = os.getenv('MINIO_SECRET_KEY', 'minioadmin')
            
            self.minio_client = Minio(
                minio_endpoint,
                access_key=minio_access_key,
                secret_key=minio_secret_key,
                secure=False
            )
            logger.info("MinIO client initialized")
        except Exception as e:
            logger.warning(f"MinIO client initialization failed: {e}")
            self.minio_client = None
        
        # AWS S3 for backup storage
        try:
            self.s3_client = boto3.client('s3')
            logger.info("AWS S3 client initialized")
        except Exception as e:
            logger.warning(f"AWS S3 client initialization failed: {e}")
            self.s3_client = None
    
    def _load_config(self):
        """Load crawler configurations"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                # Load crawler configurations
                for crawler_data in config_data.get('crawlers', []):
                    crawler_config = CrawlerConfig(
                        crawler_id=crawler_data['crawler_id'],
                        crawler_name=crawler_data['crawler_name'],
                        crawler_type=CrawlerType(crawler_data['crawler_type']),
                        crawling_strategy=CrawlingStrategy(crawler_data['crawling_strategy']),
                        target_platforms=crawler_data['target_platforms'],
                        content_types=[ContentType(ct) for ct in crawler_data['content_types']],
                        anti_detection=[AntiDetectionMode(ad) for ad in crawler_data.get('anti_detection', [])],
                        api_integrations=[PlatformAPI(api) for api in crawler_data.get('api_integrations', [])],
                        crawl_frequency=crawler_data.get('crawl_frequency', 3600),
                        max_concurrent_requests=crawler_data.get('max_concurrent_requests', 10),
                        request_delay_ms=crawler_data.get('request_delay_ms', 1000),
                        timeout_seconds=crawler_data.get('timeout_seconds', 30),
                        retry_attempts=crawler_data.get('retry_attempts', 3),
                        proxy_rotation=crawler_data.get('proxy_rotation', True),
                        user_agent_rotation=crawler_data.get('user_agent_rotation', True),
                        respect_robots_txt=crawler_data.get('respect_robots_txt', False),
                        follow_redirects=crawler_data.get('follow_redirects', True),
                        download_images=crawler_data.get('download_images', True),
                        download_videos=crawler_data.get('download_videos', True),
                        extract_metadata=crawler_data.get('extract_metadata', True),
                        storage_path=crawler_data.get('storage_path', '/crawler-data'),
                        max_storage_gb=crawler_data.get('max_storage_gb', 100.0),
                        enabled=crawler_data.get('enabled', True)
                    )
                    self.crawler_configs[crawler_config.crawler_id] = crawler_config
                
                # Load proxy configurations
                for proxy_data in config_data.get('proxies', []):
                    proxy_config = ProxyConfig(
                        proxy_provider=proxy_data['proxy_provider'],
                        proxy_list=proxy_data.get('proxy_list', []),
                        rotation_interval=proxy_data.get('rotation_interval', 300),
                        authentication_required=proxy_data.get('authentication_required', False),
                        username=proxy_data.get('username', ''),
                        password=proxy_data.get('password', ''),
                        proxy_type=proxy_data.get('proxy_type', 'http')
                    )
                    self.proxy_configs[proxy_config.proxy_provider] = proxy_config
                
                logger.info(f"Loaded {len(self.crawler_configs)} crawler configurations and {len(self.proxy_configs)} proxy configurations")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
    
    def _init_user_agents(self):
        """Initialize user agent rotation pool"""
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux i686; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
        ]
        logger.info(f"Initialized {len(self.user_agents)} user agents for rotation")
    
    def _init_proxy_rotation(self):
        """Initialize proxy rotation system"""
        self.current_proxy_index = 0
        self.proxy_failures = {}
        logger.info("Proxy rotation system initialized")
    
    def deploy_crawler_system(self, deployment_config: DeploymentConfig) -> bool:
        """Deploy complete web crawler system"""
        if not self.k8s_client:
            logger.error("Kubernetes client not available")
            return False
        
        try:
            # Create namespace
            self._create_namespace("crawler-system")
            
            # Create ConfigMaps for crawler configurations
            self._create_crawler_configmaps()
            
            # Create secrets for API keys and proxy credentials
            self._create_crawler_secrets()
            
            # Create PersistentVolumeClaims for storage
            self._create_crawler_storage(deployment_config)
            
            # Deploy Redis for coordination
            self._deploy_redis_coordination()
            
            # Deploy individual crawler services
            for crawler_id, crawler_config in self.crawler_configs.items():
                if crawler_config.enabled:
                    self._deploy_crawler_service(crawler_id, crawler_config, deployment_config)
            
            # Deploy crawler orchestrator
            self._deploy_crawler_orchestrator(deployment_config)
            
            # Create services and ingress
            self._create_crawler_services()
            
            # Deploy monitoring and alerting
            self._deploy_crawler_monitoring()
            
            logger.info("Web crawler system deployed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy crawler system: {e}")
            return False
    
    def _create_crawler_configmaps(self):
        """Create ConfigMaps for crawler configurations"""
        # Main crawler configuration
        crawler_config_data = {}
        for crawler_id, config in self.crawler_configs.items():
            crawler_config_data[f"{crawler_id}.yaml"] = yaml.dump(config.to_dict())
        
        configmap_manifest = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "crawler-configs",
                "namespace": "crawler-system"
            },
            "data": crawler_config_data
        }
        self._create_or_update_configmap(configmap_manifest)
        
        # Proxy configuration
        proxy_config_data = {}
        for proxy_provider, config in self.proxy_configs.items():
            proxy_config_data[f"{proxy_provider}.yaml"] = yaml.dump(config.to_dict())
        
        proxy_configmap_manifest = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "proxy-configs",
                "namespace": "crawler-system"
            },
            "data": proxy_config_data
        }
        self._create_or_update_configmap(proxy_configmap_manifest)
        
        # User agents configuration
        user_agents_configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": "user-agents",
                "namespace": "crawler-system"
            },
            "data": {
                "user-agents.json": json.dumps(self.user_agents)
            }
        }
        self._create_or_update_configmap(user_agents_configmap)
        
        logger.info("Created crawler ConfigMaps")
    
    def _create_crawler_secrets(self):
        """Create secrets for API keys and credentials"""
        secrets_data = {
            "youtube-api-key": os.getenv('YOUTUBE_API_KEY', ''),
            "instagram-access-token": os.getenv('INSTAGRAM_ACCESS_TOKEN', ''),
            "twitter-bearer-token": os.getenv('TWITTER_BEARER_TOKEN', ''),
            "tiktok-access-token": os.getenv('TIKTOK_ACCESS_TOKEN', ''),
            "spotify-client-id": os.getenv('SPOTIFY_CLIENT_ID', ''),
            "spotify-client-secret": os.getenv('SPOTIFY_CLIENT_SECRET', ''),
            "proxy-username": os.getenv('PROXY_USERNAME', ''),
            "proxy-password": os.getenv('PROXY_PASSWORD', ''),
            "database-url": os.getenv('DATABASE_URL', ''),
            "redis-password": os.getenv('REDIS_PASSWORD', ''),
            "captcha-solver-key": os.getenv('CAPTCHA_SOLVER_KEY', '')
        }
        
        # Convert to base64 encoded values
        import base64
        encoded_secrets = {}
        for key, value in secrets_data.items():
            if value:
                encoded_secrets[key] = base64.b64encode(value.encode()).decode()
        
        secret_manifest = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": "crawler-secrets",
                "namespace": "crawler-system"
            },
            "type": "Opaque",
            "data": encoded_secrets
        }
        
        try:
            self.core_v1.create_namespaced_secret(
                namespace="crawler-system",
                body=secret_manifest
            )
            logger.info("Created crawler secrets")
        except ApiException as e:
            if e.status == 409:  # Already exists
                self.core_v1.patch_namespaced_secret(
                    name="crawler-secrets",
                    namespace="crawler-system",
                    body=secret_manifest
                )
                logger.info("Updated crawler secrets")
    
    def _create_crawler_storage(self, deployment_config: DeploymentConfig):
        """Create PersistentVolumeClaims for crawler storage"""
        storage_configs = [
            {
                "name": "crawler-data-storage",
                "size": deployment_config.resource_limits['storage'],
                "storage_class": deployment_config.storage_class,
                "access_modes": ["ReadWriteMany"]
            },
            {
                "name": "crawler-logs-storage",
                "size": "50Gi",
                "storage_class": "standard",
                "access_modes": ["ReadWriteMany"]
            },
            {
                "name": "crawler-cache-storage",
                "size": "20Gi",
                "storage_class": "fast-ssd",
                "access_modes": ["ReadWriteMany"]
            }
        ]
        
        for storage_config in storage_configs:
            pvc_manifest = {
                "apiVersion": "v1",
                "kind": "PersistentVolumeClaim",
                "metadata": {
                    "name": storage_config["name"],
                    "namespace": "crawler-system"
                },
                "spec": {
                    "accessModes": storage_config["access_modes"],
                    "storageClassName": storage_config["storage_class"],
                    "resources": {
                        "requests": {
                            "storage": storage_config["size"]
                        }
                    }
                }
            }
            
            try:
                self.core_v1.create_namespaced_persistent_volume_claim(
                    namespace="crawler-system",
                    body=pvc_manifest
                )
                logger.info(f"Created PVC: {storage_config['name']}")
            except ApiException as e:
                if e.status == 409:  # Already exists
                    logger.info(f"PVC {storage_config['name']} already exists")
                else:
                    raise
    
    def _deploy_redis_coordination(self):
        """Deploy Redis for crawler coordination"""
        redis_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "crawler-redis",
                "namespace": "crawler-system"
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app": "crawler-redis"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "crawler-redis"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "redis",
                            "image": "redis:7-alpine",
                            "ports": [{
                                "containerPort": 6379,
                                "name": "redis"
                            }],
                            "args": ["--maxmemory", "1gb", "--maxmemory-policy", "allkeys-lru"],
                            "resources": {
                                "requests": {
                                    "cpu": "100m",
                                    "memory": "256Mi"
                                },
                                "limits": {
                                    "cpu": "500m",
                                    "memory": "1Gi"
                                }
                            },
                            "volumeMounts": [{
                                "name": "redis-data",
                                "mountPath": "/data"
                            }]
                        }],
                        "volumes": [{
                            "name": "redis-data",
                            "emptyDir": {}
                        }]
                    }
                }
            }
        }
        
        self.apps_v1.create_namespaced_deployment(
            namespace="crawler-system",
            body=redis_deployment
        )
        
        # Create Redis service
        redis_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "crawler-redis-service",
                "namespace": "crawler-system"
            },
            "spec": {
                "selector": {
                    "app": "crawler-redis"
                },
                "ports": [{
                    "protocol": "TCP",
                    "port": 6379,
                    "targetPort": 6379
                }],
                "type": "ClusterIP"
            }
        }
        
        self.core_v1.create_namespaced_service(
            namespace="crawler-system",
            body=redis_service
        )
        
        logger.info("Deployed Redis coordination service")
    
    def _deploy_crawler_service(self, crawler_id: str, crawler_config: CrawlerConfig, deployment_config: DeploymentConfig):
        """Deploy individual crawler service"""
        container_image = self._get_crawler_image(crawler_config.crawler_type)
        
        deployment_manifest = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"crawler-{crawler_id}",
                "namespace": "crawler-system",
                "labels": {
                    "app": f"crawler-{crawler_id}",
                    "crawler-type": crawler_config.crawler_type.value
                }
            },
            "spec": {
                "replicas": deployment_config.replicas,
                "selector": {
                    "matchLabels": {
                        "app": f"crawler-{crawler_id}"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": f"crawler-{crawler_id}",
                            "crawler-type": crawler_config.crawler_type.value
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": f"crawler-{crawler_id}",
                            "image": container_image,
                            "env": self._get_crawler_env_vars(crawler_id, crawler_config),
                            "resources": {
                                "requests": deployment_config.resource_requests,
                                "limits": deployment_config.resource_limits
                            },
                            "volumeMounts": [
                                {
                                    "name": "crawler-config",
                                    "mountPath": "/etc/crawler/config"
                                },
                                {
                                    "name": "proxy-config",
                                    "mountPath": "/etc/crawler/proxies"
                                },
                                {
                                    "name": "user-agents",
                                    "mountPath": "/etc/crawler/user-agents"
                                },
                                {
                                    "name": "crawler-data",
                                    "mountPath": "/crawler-data"
                                },
                                {
                                    "name": "crawler-logs",
                                    "mountPath": "/var/log/crawler"
                                },
                                {
                                    "name": "crawler-cache",
                                    "mountPath": "/var/cache/crawler"
                                }
                            ],
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": 8080
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready",
                                    "port": 8080
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            }
                        }],
                        "volumes": [
                            {
                                "name": "crawler-config",
                                "configMap": {
                                    "name": "crawler-configs"
                                }
                            },
                            {
                                "name": "proxy-config",
                                "configMap": {
                                    "name": "proxy-configs"
                                }
                            },
                            {
                                "name": "user-agents",
                                "configMap": {
                                    "name": "user-agents"
                                }
                            },
                            {
                                "name": "crawler-data",
                                "persistentVolumeClaim": {
                                    "claimName": "crawler-data-storage"
                                }
                            },
                            {
                                "name": "crawler-logs",
                                "persistentVolumeClaim": {
                                    "claimName": "crawler-logs-storage"
                                }
                            },
                            {
                                "name": "crawler-cache",
                                "persistentVolumeClaim": {
                                    "claimName": "crawler-cache-storage"
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        self.apps_v1.create_namespaced_deployment(
            namespace="crawler-system",
            body=deployment_manifest
        )
        
        # Create horizontal pod autoscaler if enabled
        if deployment_config.auto_scaling:
            self._create_crawler_hpa(crawler_id, deployment_config)
        
        logger.info(f"Deployed crawler service: {crawler_id}")
    
    def _get_crawler_image(self, crawler_type: CrawlerType) -> str:
        """Get Docker image for specific crawler type"""
        image_mapping = {
            CrawlerType.YOUTUBE_CRAWLER: "ia-influencer/youtube-crawler:latest",
            CrawlerType.INSTAGRAM_CRAWLER: "ia-influencer/instagram-crawler:latest",
            CrawlerType.TIKTOK_CRAWLER: "ia-influencer/tiktok-crawler:latest",
            CrawlerType.TWITTER_CRAWLER: "ia-influencer/twitter-crawler:latest",
            CrawlerType.SPOTIFY_CRAWLER: "ia-influencer/spotify-crawler:latest",
            CrawlerType.GENERIC_WEB_CRAWLER: "ia-influencer/generic-crawler:latest"
        }
        
        return image_mapping.get(crawler_type, "ia-influencer/generic-crawler:latest")
    
    def _get_crawler_env_vars(self, crawler_id: str, crawler_config: CrawlerConfig) -> List[Dict[str, Any]]:
        """Get environment variables for crawler"""
        base_env = [
            {"name": "CRAWLER_ID", "value": crawler_id},
            {"name": "CRAWLER_TYPE", "value": crawler_config.crawler_type.value},
            {"name": "CRAWLING_STRATEGY", "value": crawler_config.crawling_strategy.value},
            {"name": "CRAWL_FREQUENCY", "value": str(crawler_config.crawl_frequency)},
            {"name": "MAX_CONCURRENT_REQUESTS", "value": str(crawler_config.max_concurrent_requests)},
            {"name": "REQUEST_DELAY_MS", "value": str(crawler_config.request_delay_ms)},
            {"name": "REDIS_HOST", "value": "crawler-redis-service"},
            {"name": "REDIS_PORT", "value": "6379"}
        ]
        
        # Add secret environment variables
        secret_env = [
            {
                "name": "DATABASE_URL",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": "crawler-secrets",
                        "key": "database-url"
                    }
                }
            },
            {
                "name": "YOUTUBE_API_KEY",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": "crawler-secrets",
                        "key": "youtube-api-key"
                    }
                }
            },
            {
                "name": "INSTAGRAM_ACCESS_TOKEN",
                "valueFrom": {
                    "secretKeyRef": {
                        "name": "crawler-secrets",
                        "key": "instagram-access-token"
                    }
                }
            }
        ]
        
        return base_env + secret_env
    
    def _create_crawler_hpa(self, crawler_id: str, deployment_config: DeploymentConfig):
        """Create Horizontal Pod Autoscaler for crawler"""
        hpa_manifest = {
            "apiVersion": "autoscaling/v1",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"crawler-{crawler_id}-hpa",
                "namespace": "crawler-system"
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": f"crawler-{crawler_id}"
                },
                "minReplicas": deployment_config.min_replicas,
                "maxReplicas": deployment_config.max_replicas,
                "targetCPUUtilizationPercentage": deployment_config.target_cpu_utilization
            }
        }
        
        self.autoscaling_v1.create_namespaced_horizontal_pod_autoscaler(
            namespace="crawler-system",
            body=hpa_manifest
        )
        
        logger.info(f"Created HPA for crawler: {crawler_id}")
    
    def _deploy_crawler_orchestrator(self, deployment_config: DeploymentConfig):
        """Deploy crawler orchestrator service"""
        orchestrator_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "crawler-orchestrator",
                "namespace": "crawler-system"
            },
            "spec": {
                "replicas": 2,
                "selector": {
                    "matchLabels": {
                        "app": "crawler-orchestrator"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": "crawler-orchestrator"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "orchestrator",
                            "image": "ia-influencer/crawler-orchestrator:latest",
                            "ports": [{
                                "containerPort": 8080,
                                "name": "http"
                            }],
                            "env": [
                                {"name": "REDIS_HOST", "value": "crawler-redis-service"},
                                {"name": "REDIS_PORT", "value": "6379"}
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "200m",
                                    "memory": "512Mi"
                                },
                                "limits": {
                                    "cpu": "1000m",
                                    "memory": "2Gi"
                                }
                            },
                            "volumeMounts": [
                                {
                                    "name": "crawler-config",
                                    "mountPath": "/etc/crawler/config"
                                }
                            ]
                        }],
                        "volumes": [
                            {
                                "name": "crawler-config",
                                "configMap": {
                                    "name": "crawler-configs"
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        self.apps_v1.create_namespaced_deployment(
            namespace="crawler-system",
            body=orchestrator_deployment
        )
        
        logger.info("Deployed crawler orchestrator")
    
    def _create_crawler_services(self):
        """Create services for crawler system"""
        # Orchestrator service
        orchestrator_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "crawler-orchestrator-service",
                "namespace": "crawler-system"
            },
            "spec": {
                "selector": {
                    "app": "crawler-orchestrator"
                },
                "ports": [{
                    "protocol": "TCP",
                    "port": 8080,
                    "targetPort": 8080
                }],
                "type": "ClusterIP"
            }
        }
        
        self.core_v1.create_namespaced_service(
            namespace="crawler-system",
            body=orchestrator_service
        )
        
        logger.info("Created crawler services")
    
    def _deploy_crawler_monitoring(self):
        """Deploy monitoring for crawler system"""
        # This would deploy Prometheus monitoring, Grafana dashboards, etc.
        # Implementation depends on existing monitoring infrastructure
        logger.info("Crawler monitoring deployment completed")
    
    def _create_namespace(self, namespace: str):
        """Create Kubernetes namespace if it doesn't exist"""
        try:
            self.core_v1.read_namespace(name=namespace)
        except ApiException as e:
            if e.status == 404:
                namespace_manifest = {
                    "apiVersion": "v1",
                    "kind": "Namespace",
                    "metadata": {"name": namespace}
                }
                self.core_v1.create_namespace(body=namespace_manifest)
                logger.info(f"Created namespace: {namespace}")
    
    def _create_or_update_configmap(self, configmap_manifest: Dict[str, Any]):
        """Create or update ConfigMap"""
        try:
            self.core_v1.read_namespaced_config_map(
                name=configmap_manifest['metadata']['name'],
                namespace=configmap_manifest['metadata']['namespace']
            )
            # Update existing ConfigMap
            self.core_v1.patch_namespaced_config_map(
                name=configmap_manifest['metadata']['name'],
                namespace=configmap_manifest['metadata']['namespace'],
                body=configmap_manifest
            )
        except ApiException as e:
            if e.status == 404:
                # Create new ConfigMap
                self.core_v1.create_namespaced_config_map(
                    namespace=configmap_manifest['metadata']['namespace'],
                    body=configmap_manifest
                )
    
    def start_crawler(self, crawler_id: str) -> bool:
        """Start specific crawler"""
        try:
            if crawler_id not in self.crawler_configs:
                logger.error(f"Crawler configuration not found: {crawler_id}")
                return False
            
            # Scale up deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=f"crawler-{crawler_id}",
                namespace="crawler-system"
            )
            
            deployment.spec.replicas = max(1, deployment.spec.replicas)
            
            self.apps_v1.patch_namespaced_deployment(
                name=f"crawler-{crawler_id}",
                namespace="crawler-system",
                body=deployment
            )
            
            logger.info(f"Started crawler: {crawler_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start crawler {crawler_id}: {e}")
            return False
    
    def stop_crawler(self, crawler_id: str) -> bool:
        """Stop specific crawler"""
        try:
            # Scale down deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=f"crawler-{crawler_id}",
                namespace="crawler-system"
            )
            
            deployment.spec.replicas = 0
            
            self.apps_v1.patch_namespaced_deployment(
                name=f"crawler-{crawler_id}",
                namespace="crawler-system",
                body=deployment
            )
            
            logger.info(f"Stopped crawler: {crawler_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop crawler {crawler_id}: {e}")
            return False
    
    def get_crawler_status(self) -> Dict[str, Any]:
        """Get status of all crawlers"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'crawlers': {},
            'system_health': 'unknown'
        }
        
        try:
            # Get deployment status for each crawler
            for crawler_id in self.crawler_configs.keys():
                try:
                    deployment = self.apps_v1.read_namespaced_deployment(
                        name=f"crawler-{crawler_id}",
                        namespace="crawler-system"
                    )
                    
                    status['crawlers'][crawler_id] = {
                        'replicas': deployment.spec.replicas,
                        'ready_replicas': deployment.status.ready_replicas or 0,
                        'available_replicas': deployment.status.available_replicas or 0,
                        'updated_replicas': deployment.status.updated_replicas or 0,
                        'status': 'running' if (deployment.status.ready_replicas or 0) > 0 else 'stopped'
                    }
                except ApiException:
                    status['crawlers'][crawler_id] = {
                        'status': 'not_deployed',
                        'replicas': 0,
                        'ready_replicas': 0
                    }
            
            # Determine overall system health
            total_crawlers = len(self.crawler_configs)
            healthy_crawlers = sum(1 for c in status['crawlers'].values() if c.get('status') == 'running')
            
            if healthy_crawlers == 0:
                status['system_health'] = 'critical'
            elif healthy_crawlers < total_crawlers * 0.5:
                status['system_health'] = 'degraded'
            elif healthy_crawlers < total_crawlers:
                status['system_health'] = 'warning'
            else:
                status['system_health'] = 'healthy'
            
        except Exception as e:
            logger.error(f"Failed to get crawler status: {e}")
            status['system_health'] = 'error'
            status['error'] = str(e)
        
        return status
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'components': {
                'kubernetes': self.k8s_client is not None,
                'docker': self.docker_client is not None,
                'redis': self.redis_client is not None,
                'database': self.db_url is not None,
                'minio': self.minio_client is not None,
                's3': self.s3_client is not None
            },
            'crawler_system': {
                'total_crawlers': len(self.crawler_configs),
                'enabled_crawlers': len([c for c in self.crawler_configs.values() if c.enabled]),
                'proxy_providers': len(self.proxy_configs),
                'user_agents': len(self.user_agents)
            }
        }
        
        # Check component health
        unhealthy_components = [k for k, v in health_status['components'].items() if not v]
        if unhealthy_components:
            health_status['overall_status'] = 'degraded'
            health_status['issues'] = f"Unhealthy components: {', '.join(unhealthy_components)}"
        
        # Get crawler status
        crawler_status = self.get_crawler_status()
        health_status['crawler_status'] = crawler_status
        
        if crawler_status['system_health'] in ['critical', 'error']:
            health_status['overall_status'] = 'critical'
        elif crawler_status['system_health'] == 'degraded':
            health_status['overall_status'] = 'degraded'
        
        return health_status


def main():
    """Main function for testing the Web Crawlers Deployment Manager"""
    # Initialize manager
    manager = WebCrawlersDeploymentManager()
    
    # Example configurations
    deployment_config = DeploymentConfig(
        replicas=3,
        auto_scaling=True,
        min_replicas=2,
        max_replicas=10,
        storage_class="fast-ssd"
    )
    
    # Example crawler configuration
    youtube_crawler_config = CrawlerConfig(
        crawler_id="youtube-content-monitor",
        crawler_name="YouTube Content Monitor",
        crawler_type=CrawlerType.YOUTUBE_CRAWLER,
        crawling_strategy=CrawlingStrategy.API_INTEGRATION,
        target_platforms=["youtube.com"],
        content_types=[ContentType.VIDEO_CONTENT, ContentType.METADATA_ONLY],
        anti_detection=[AntiDetectionMode.USER_AGENT_ROTATION, AntiDetectionMode.REQUEST_DELAY],
        api_integrations=[PlatformAPI.YOUTUBE_DATA_API],
        crawl_frequency=1800,  # 30 minutes
        max_concurrent_requests=5,
        request_delay_ms=2000
    )
    
    manager.crawler_configs[youtube_crawler_config.crawler_id] = youtube_crawler_config
    
    # Deploy crawler system
    if manager.deploy_crawler_system(deployment_config):
        print("✅ Web crawler system deployed successfully")
    
    # Start crawler
    if manager.start_crawler(youtube_crawler_config.crawler_id):
        print("✅ YouTube crawler started successfully")
    
    # Get status
    status = manager.get_crawler_status()
    print(f"✅ Crawler system status: {status['system_health']}")
    
    # Health check
    health = manager.health_check()
    print(f"✅ Health check completed: {health['overall_status']}")
    
    print("\n🎯 Web Crawlers Deployment Manager test completed")


if __name__ == "__main__":
    main()
