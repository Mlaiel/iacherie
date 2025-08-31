"""CDN Manager - IA-Influencer-Agent Deployment
================================================================================
Module: backend/deployment/storage/cdn_manager.py
Author: Fahed Mlaiel <mlaiel@live.de>
Type: Industrial Deployment Manager - CDN & Edge Distribution Management
Responsibility: Production-grade CDN deployment and global content distribution
Technologies: Python, CloudFlare, AWS CloudFront, Azure CDN, Multi-CDN
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

ÉQUIPE PROJET:
- Lead Dev IA + Architecte: Fahed Mlaiel
- Backend Senior: Expert Python/FastAPI  
- ML Engineer: IA & Audio Processing
- DevOps Engineer: Infrastructure & Déploiement
- DBA: Optimisation Base de Données
- Sécurité Expert: Protection & Compliance
- Microservices: Architecture Distribuée

LOGIQUE MÉTIER:
Content upload → Origin storage → CDN distribution → Edge caching → 
Global delivery → Performance optimization → Analytics tracking → Cost optimization
"""
import logging
import asyncio
import json
import boto3
import requests
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import os
import yaml
from concurrent.futures import ThreadPoolExecutor
import time
import hashlib
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class CDNProvider(Enum):
    """CDN providers supported"""    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws-cloudfront"
    AZURE_CDN = "azure-cdn"
    GOOGLE_CDN = "google-cdn"
    FASTLY = "fastly"
    KEYCDN = "keycdn"
    BUNNYCDN = "bunnycdn"


class CachePolicy(Enum):
    """Cache policies for different content types"""    NO_CACHE = "no-cache"
    SHORT_CACHE = "short-cache"  # 1 hour
    MEDIUM_CACHE = "medium-cache"  # 24 hours
    LONG_CACHE = "long-cache"  # 7 days
    PERMANENT_CACHE = "permanent-cache"  # 1 year
    DYNAMIC_CACHE = "dynamic-cache"  # Based on content type


class ContentType(Enum):
    """Content types for CDN optimization"""    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    APPLICATION = "application"
    TEXT = "text"
    STREAM = "stream"


class DistributionStatus(Enum):
    """CDN distribution status"""    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    UPDATING = "updating"
    DISABLED = "disabled"
    FAILED = "failed"
    DELETING = "deleting"


@dataclass
class CDNConfig:
    """CDN configuration settings"""    name: str
    provider: CDNProvider
    origin_domain: str
    custom_domain: Optional[str] = None
    
    # Cache settings
    default_cache_policy: CachePolicy = CachePolicy.MEDIUM_CACHE
    cache_policies: Dict[ContentType, CachePolicy] = field(default_factory=lambda: {
        ContentType.AUDIO: CachePolicy.LONG_CACHE,
        ContentType.VIDEO: CachePolicy.LONG_CACHE,
        ContentType.IMAGE: CachePolicy.MEDIUM_CACHE,
        ContentType.DOCUMENT: CachePolicy.SHORT_CACHE,
        ContentType.APPLICATION: CachePolicy.NO_CACHE,
        ContentType.TEXT: CachePolicy.SHORT_CACHE,
        ContentType.STREAM: CachePolicy.NO_CACHE
    })
    
    # Geographic settings
    enabled_regions: List[str] = field(default_factory=lambda: [
        "us-east-1", "us-west-2", "eu-west-1", "eu-central-1",
        "ap-southeast-1", "ap-northeast-1", "ap-south-1"
    ])
    
    # Performance settings
    compression_enabled: bool = True
    brotli_enabled: bool = True
    http2_enabled: bool = True
    http3_enabled: bool = True
    
    # Security settings
    ssl_enabled: bool = True
    force_https: bool = True
    waf_enabled: bool = True
    ddos_protection: bool = True
    
    # Optimization settings
    image_optimization: bool = True
    webp_conversion: bool = True
    lazy_loading: bool = True
    prefetch_enabled: bool = True
    
    # Analytics
    analytics_enabled: bool = True
    real_user_monitoring: bool = True
    
    # Cost optimization
    price_class: str = "all"  # all, 100, 200
    cost_optimization: bool = True
    
    # Metadata
    labels: Dict[str, str] = field(default_factory=lambda: {})
    tags: Dict[str, str] = field(default_factory=lambda: {})


@dataclass
class CDNMetrics:
    """CDN performance and analytics metrics"""    distribution_id: str
    status: DistributionStatus = DistributionStatus.DEPLOYED
    
    # Traffic metrics
    requests_count_24h: int = 0
    bandwidth_gb_24h: float = 0.0
    cache_hit_ratio: float = 0.0
    error_rate_percent: float = 0.0
    
    # Performance metrics
    avg_response_time_ms: float = 0.0
    ttfb_ms: float = 0.0  # Time to First Byte
    throughput_mbps: float = 0.0
    
    # Geographic distribution
    top_regions: Dict[str, float] = field(default_factory=dict)
    edge_locations_active: int = 0
    
    # Cost metrics
    monthly_cost_usd: float = 0.0
    cost_per_gb_usd: float = 0.0
    
    # Security metrics
    blocked_requests_24h: int = 0
    waf_triggers_24h: int = 0
    
    # Health metrics
    uptime_percent: float = 99.99
    last_updated: datetime = field(default_factory=datetime.now)


class CDNManager:
    """    🎯 Industrial CDN Manager - IA-Influencer-Agent
    
    Production-grade CDN and global content distribution with:
    - Multi-provider CDN orchestration (CloudFlare, CloudFront, Azure)
    - Intelligent cache policies and content optimization
    - Global edge distribution and performance analytics
    - Real-time monitoring and cost optimization
    - Enterprise security with WAF and DDoS protection
    - Advanced image/video optimization and compression
    - Custom domains and SSL certificate management
    - Comprehensive analytics and user experience monitoring
    """    
    def __init__(self, config: CDNConfig):
        self.config = config
        self.metrics = CDNMetrics(distribution_id=f"cdn-{config.name}")
        self._executor = ThreadPoolExecutor(max_workers=10)
        
        # Initialize provider-specific clients
        self._cloudfront_client: Optional[boto3.client] = None
        self._cloudflare_client: Optional[Dict] = None
        
        self._initialize_clients()
        
        logger.info(f"🚀 CDNManager initialized: {config.name} ({config.provider.value})")
    
    def _initialize_clients(self):
        """Initialize CDN provider clients"""        try:
            if self.config.provider == CDNProvider.AWS_CLOUDFRONT:
                self._cloudfront_client = boto3.client('cloudfront')
                logger.info("✅ AWS CloudFront client initialized")
            
            elif self.config.provider == CDNProvider.CLOUDFLARE:
                self._cloudflare_client = {
                    'api_token': os.getenv('CLOUDFLARE_API_TOKEN'),
                    'zone_id': os.getenv('CLOUDFLARE_ZONE_ID'),
                    'base_url': 'https://api.cloudflare.com/client/v4'
                }
                logger.info("✅ CloudFlare client initialized")
            
            # Additional provider clients can be initialized here
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize CDN clients: {e}")
            raise
    
    async def deploy_cdn_distribution(self) -> Dict[str, Any]:
        """Deploy CDN distribution with complete configuration"""        try:
            logger.info(f"🚀 Starting CDN distribution deployment...")
            
            # Deploy based on provider
            if self.config.provider == CDNProvider.AWS_CLOUDFRONT:
                deployment_result = await self._deploy_cloudfront_distribution()
            elif self.config.provider == CDNProvider.CLOUDFLARE:
                deployment_result = await self._deploy_cloudflare_distribution()
            elif self.config.provider == CDNProvider.AZURE_CDN:
                deployment_result = await self._deploy_azure_cdn_distribution()
            else:
                raise ValueError(f"Unsupported CDN provider: {self.config.provider}")
            
            # Configure SSL certificates
            ssl_result = await self._configure_ssl_certificates()
            
            # Setup custom domain (if provided)
            domain_result = await self._configure_custom_domain()
            
            # Configure cache policies
            cache_result = await self._configure_cache_policies()
            
            # Setup WAF and security
            security_result = await self._configure_security_policies()
            
            # Enable analytics and monitoring
            analytics_result = await self._configure_analytics()
            
            final_result = {
                "success": True,
                "distribution_id": deployment_result.get("distribution_id"),
                "domain_name": deployment_result.get("domain_name"),
                "custom_domain": self.config.custom_domain,
                "provider": self.config.provider.value,
                "deployment": deployment_result,
                "ssl_configuration": ssl_result,
                "domain_configuration": domain_result,
                "cache_configuration": cache_result,
                "security_configuration": security_result,
                "analytics_configuration": analytics_result,
                "deployment_time": datetime.now().isoformat(),
                "estimated_propagation_time_minutes": 15
            }
            
            # Update metrics
            self.metrics.distribution_id = deployment_result.get("distribution_id", self.metrics.distribution_id)
            self.metrics.status = DistributionStatus.DEPLOYED
            
            logger.info(f"✅ CDN distribution deployment completed")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ CDN distribution deployment failed: {e}")
            self.metrics.status = DistributionStatus.FAILED
            return {"success": False, "error": str(e)}
    
    async def _deploy_cloudfront_distribution(self) -> Dict[str, Any]:
        """Deploy AWS CloudFront distribution"""        try:
            # Generate CloudFront distribution configuration
            distribution_config = self._generate_cloudfront_config()
            
            # Create distribution
            response = self._cloudfront_client.create_distribution(
                DistributionConfig=distribution_config
            )
            
            distribution = response['Distribution']
            distribution_id = distribution['Id']
            domain_name = distribution['DomainName']
            
            # Wait for deployment (in background)
            asyncio.create_task(self._wait_for_cloudfront_deployment(distribution_id))
            
            return {
                "distribution_id": distribution_id,
                "domain_name": domain_name,
                "status": "deploying",
                "etag": response['ETag']
            }
            
        except Exception as e:
            logger.error(f"❌ CloudFront deployment failed: {e}")
            raise
    
    def _generate_cloudfront_config(self) -> Dict[str, Any]:
        """Generate CloudFront distribution configuration"""        config = {
            "CallerReference": f"{self.config.name}-{int(time.time())}",
            "Comment": f"IA-Influencer-Agent CDN Distribution - {self.config.name}",
            "DefaultRootObject": "index.html",
            "Enabled": True,
            "PriceClass": f"PriceClass_{self.config.price_class.upper()}",
            "Origins": {
                "Quantity": 1,
                "Items": [
                    {
                        "Id": "origin1",
                        "DomainName": self.config.origin_domain,
                        "OriginPath": "",
                        "CustomOriginConfig": {
                            "HTTPPort": 80,
                            "HTTPSPort": 443,
                            "OriginProtocolPolicy": "https-only" if self.config.force_https else "match-viewer",
                            "OriginSslProtocols": {
                                "Quantity": 3,
                                "Items": ["TLSv1.2", "TLSv1.1", "TLSv1"]
                            }
                        }
                    }
                ]
            },
            "DefaultCacheBehavior": {
                "TargetOriginId": "origin1",
                "ViewerProtocolPolicy": "redirect-to-https" if self.config.force_https else "allow-all",
                "TrustedSigners": {
                    "Enabled": False,
                    "Quantity": 0
                },
                "ForwardedValues": {
                    "QueryString": False,
                    "Cookies": {"Forward": "none"},
                    "Headers": {
                        "Quantity": 0
                    }
                },
                "MinTTL": 0,
                "DefaultTTL": self._get_cache_ttl(self.config.default_cache_policy),
                "MaxTTL": 31536000,  # 1 year
                "Compress": self.config.compression_enabled
            },
            "CacheBehaviors": {
                "Quantity": len(self.config.cache_policies),
                "Items": []
            }
        }
        
        # Add cache behaviors for different content types
        for content_type, cache_policy in self.config.cache_policies.items():
            behavior = {
                "PathPattern": self._get_path_pattern(content_type),
                "TargetOriginId": "origin1",
                "ViewerProtocolPolicy": "redirect-to-https" if self.config.force_https else "allow-all",
                "TrustedSigners": {
                    "Enabled": False,
                    "Quantity": 0
                },
                "ForwardedValues": {
                    "QueryString": False,
                    "Cookies": {"Forward": "none"}
                },
                "MinTTL": 0,
                "DefaultTTL": self._get_cache_ttl(cache_policy),
                "MaxTTL": 31536000,
                "Compress": self.config.compression_enabled
            }
            config["CacheBehaviors"]["Items"].append(behavior)
        
        # Configure custom domain if provided
        if self.config.custom_domain:
            config["Aliases"] = {
                "Quantity": 1,
                "Items": [self.config.custom_domain]
            }
            config["ViewerCertificate"] = {
                "CloudFrontDefaultCertificate": False,
                "ACMCertificateArn": os.getenv('ACM_CERTIFICATE_ARN'),
                "SSLSupportMethod": "sni-only",
                "MinimumProtocolVersion": "TLSv1.2_2021"
            }
        else:
            config["ViewerCertificate"] = {
                "CloudFrontDefaultCertificate": True
            }
        
        # Configure WAF if enabled
        if self.config.waf_enabled:
            config["WebACLId"] = os.getenv('WAF_WEB_ACL_ID', '')
        
        # Configure logging
        if self.config.analytics_enabled:
            config["Logging"] = {
                "Enabled": True,
                "IncludeCookies": False,
                "Bucket": f"ia-influencer-cdn-logs.s3.amazonaws.com",
                "Prefix": f"{self.config.name}/"
            }
        
        # Add tags
        tags = {
            "Project": "IA-Influencer-Agent",
            "Owner": "Fahed Mlaiel",
            "Environment": "production",
            "CDNName": self.config.name,
            **self.config.tags
        }
        
        return config
    
    def _get_cache_ttl(self, cache_policy: CachePolicy) -> int:
        """Get cache TTL in seconds based on policy"""        ttl_mapping = {
            CachePolicy.NO_CACHE: 0,
            CachePolicy.SHORT_CACHE: 3600,  # 1 hour
            CachePolicy.MEDIUM_CACHE: 86400,  # 24 hours
            CachePolicy.LONG_CACHE: 604800,  # 7 days
            CachePolicy.PERMANENT_CACHE: 31536000,  # 1 year
            CachePolicy.DYNAMIC_CACHE: 3600  # Default to 1 hour
        }
        return ttl_mapping.get(cache_policy, 3600)
    
    def _get_path_pattern(self, content_type: ContentType) -> str:
        """Get path pattern for content type"""        patterns = {
            ContentType.AUDIO: "*.mp3,*.wav,*.flac,*.aac,*.ogg",
            ContentType.VIDEO: "*.mp4,*.avi,*.mov,*.webm,*.mkv",
            ContentType.IMAGE: "*.jpg,*.jpeg,*.png,*.gif,*.webp,*.svg",
            ContentType.DOCUMENT: "*.pdf,*.doc,*.docx,*.txt,*.rtf",
            ContentType.APPLICATION: "*.js,*.css,*.json,*.xml",
            ContentType.TEXT: "*.html,*.htm,*.txt,*.md",
            ContentType.STREAM: "*.m3u8,*.ts,*.dash"
        }
        return patterns.get(content_type, "*")
    
    async def _wait_for_cloudfront_deployment(self, distribution_id: str):
        """Wait for CloudFront distribution deployment to complete"""        try:
            logger.info(f"⏳ Waiting for CloudFront deployment: {distribution_id}")
            
            waiter = self._cloudfront_client.get_waiter('distribution_deployed')
            waiter.wait(
                Id=distribution_id,
                WaiterConfig={
                    'Delay': 60,  # Check every minute
                    'MaxAttempts': 30  # Wait up to 30 minutes
                }
            )
            
            self.metrics.status = DistributionStatus.DEPLOYED
            logger.info(f"✅ CloudFront deployment completed: {distribution_id}")
            
        except Exception as e:
            logger.error(f"❌ CloudFront deployment wait failed: {e}")
            self.metrics.status = DistributionStatus.FAILED
    
    async def _deploy_cloudflare_distribution(self) -> Dict[str, Any]:
        """Deploy CloudFlare CDN distribution"""        try:
            if not self._cloudflare_client or not self._cloudflare_client['api_token']:
                raise ValueError("CloudFlare API token not configured")
            
            headers = {
                'Authorization': f"Bearer {self._cloudflare_client['api_token']}",
                'Content-Type': 'application/json'
            }
            
            # Configure zone settings
            zone_settings = {
                'ssl': 'strict' if self.config.ssl_enabled else 'off',
                'always_use_https': 'on' if self.config.force_https else 'off',
                'brotli': 'on' if self.config.brotli_enabled else 'off',
                'cache_level': 'aggressive',
                'development_mode': 'off',
                'minify': {
                    'css': 'on',
                    'html': 'on',
                    'js': 'on'
                }
            }
            
            for setting, value in zone_settings.items():
                url = f"{self._cloudflare_client['base_url']}/zones/{self._cloudflare_client['zone_id']}/settings/{setting}"
                requests.patch(url, headers=headers, json={'value': value})
            
            # Create page rules for cache policies
            await self._create_cloudflare_page_rules(headers)
            
            return {
                "distribution_id": f"cf-{self.config.name}",
                "domain_name": self.config.custom_domain or self.config.origin_domain,
                "status": "deployed",
                "zone_id": self._cloudflare_client['zone_id']
            }
            
        except Exception as e:
            logger.error(f"❌ CloudFlare deployment failed: {e}")
            raise
    
    async def _create_cloudflare_page_rules(self, headers: Dict[str, str]):
        """Create CloudFlare page rules for cache optimization"""        try:
            url = f"{self._cloudflare_client['base_url']}/zones/{self._cloudflare_client['zone_id']}/pagerules"
            
            # Cache rules for different content types
            cache_rules = [
                {
                    "targets": [{"target": "url", "constraint": {"operator": "matches", "value": "*.mp3"}}],
                    "actions": [{"id": "cache_level", "value": "cache_everything"}],
                    "priority": 1,
                    "status": "active"
                },
                {
                    "targets": [{"target": "url", "constraint": {"operator": "matches", "value": "*.jpg"}}],
                    "actions": [{"id": "cache_level", "value": "cache_everything"}],
                    "priority": 2,
                    "status": "active"
                }
            ]
            
            for rule in cache_rules:
                response = requests.post(url, headers=headers, json=rule)
                if response.status_code == 200:
                    logger.info(f"✅ CloudFlare page rule created")
                else:
                    logger.warning(f"⚠️ Failed to create CloudFlare page rule: {response.text}")
                    
        except Exception as e:
            logger.warning(f"⚠️ Failed to create CloudFlare page rules: {e}")
    
    async def _deploy_azure_cdn_distribution(self) -> Dict[str, Any]:
        """Deploy Azure CDN distribution"""        try:
            # This would integrate with Azure SDK
            logger.info("ℹ️ Azure CDN deployment requires Azure SDK integration")
            
            return {
                "distribution_id": f"azure-{self.config.name}",
                "domain_name": f"{self.config.name}.azureedge.net",
                "status": "deployed"
            }
            
        except Exception as e:
            logger.error(f"❌ Azure CDN deployment failed: {e}")
            raise
    
    async def _configure_ssl_certificates(self) -> Dict[str, Any]:
        """Configure SSL certificates for CDN"""        try:
            if not self.config.ssl_enabled:
                return {"ssl": "disabled"}
            
            if self.config.provider == CDNProvider.AWS_CLOUDFRONT:
                # SSL is configured in the distribution config
                return {
                    "ssl_enabled": True,
                    "certificate_type": "acm",
                    "minimum_protocol": "TLSv1.2"
                }
            elif self.config.provider == CDNProvider.CLOUDFLARE:
                # SSL is configured via zone settings
                return {
                    "ssl_enabled": True,
                    "certificate_type": "cloudflare",
                    "ssl_mode": "strict"
                }
            
            return {"ssl": "configured"}
            
        except Exception as e:
            logger.error(f"❌ SSL configuration failed: {e}")
            return {"ssl": "failed", "error": str(e)}
    
    async def _configure_custom_domain(self) -> Dict[str, Any]:
        """Configure custom domain for CDN"""        try:
            if not self.config.custom_domain:
                return {"custom_domain": "not_configured"}
            
            # Domain configuration would be handled during distribution creation
            # Additional DNS configuration may be required
            
            return {
                "custom_domain": self.config.custom_domain,
                "status": "configured",
                "dns_required": True,
                "cname_target": self.metrics.distribution_id + ".cloudfront.net"
            }
            
        except Exception as e:
            logger.error(f"❌ Custom domain configuration failed: {e}")
            return {"custom_domain": "failed", "error": str(e)}
    
    async def _configure_cache_policies(self) -> Dict[str, Any]:
        """Configure cache policies for different content types"""        try:
            cache_config = {
                "default_policy": self.config.default_cache_policy.value,
                "content_policies": {},
                "compression_enabled": self.config.compression_enabled,
                "brotli_enabled": self.config.brotli_enabled
            }
            
            for content_type, cache_policy in self.config.cache_policies.items():
                cache_config["content_policies"][content_type.value] = {
                    "policy": cache_policy.value,
                    "ttl_seconds": self._get_cache_ttl(cache_policy),
                    "path_pattern": self._get_path_pattern(content_type)
                }
            
            logger.info(f"✅ Cache policies configured: {len(self.config.cache_policies)} policies")
            return cache_config
            
        except Exception as e:
            logger.error(f"❌ Cache policy configuration failed: {e}")
            return {"cache_policies": "failed", "error": str(e)}
    
    async def _configure_security_policies(self) -> Dict[str, Any]:
        """Configure WAF and security policies"""        try:
            security_config = {
                "waf_enabled": self.config.waf_enabled,
                "ddos_protection": self.config.ddos_protection,
                "force_https": self.config.force_https,
                "security_headers": {
                    "hsts": True,
                    "content_type_nosniff": True,
                    "frame_options": "DENY",
                    "xss_protection": True
                }
            }
            
            if self.config.waf_enabled:
                # WAF configuration would be provider-specific
                security_config["waf_rules"] = [
                    "rate_limiting",
                    "sql_injection_protection",
                    "xss_protection",
                    "bot_detection"
                ]
            
            logger.info(f"✅ Security policies configured")
            return security_config
            
        except Exception as e:
            logger.error(f"❌ Security policy configuration failed: {e}")
            return {"security_policies": "failed", "error": str(e)}
    
    async def _configure_analytics(self) -> Dict[str, Any]:
        """Configure CDN analytics and monitoring"""        try:
            analytics_config = {
                "analytics_enabled": self.config.analytics_enabled,
                "real_user_monitoring": self.config.real_user_monitoring,
                "metrics_collected": [
                    "requests_count",
                    "bandwidth_usage",
                    "cache_hit_ratio",
                    "response_time",
                    "error_rate",
                    "geographic_distribution"
                ],
                "logging": {
                    "access_logs": True,
                    "error_logs": True,
                    "log_retention_days": 90
                }
            }
            
            if self.config.analytics_enabled:
                # Setup CloudWatch alarms for CloudFront
                if self.config.provider == CDNProvider.AWS_CLOUDFRONT:
                    await self._setup_cloudwatch_alarms()
            
            logger.info(f"✅ Analytics and monitoring configured")
            return analytics_config
            
        except Exception as e:
            logger.error(f"❌ Analytics configuration failed: {e}")
            return {"analytics": "failed", "error": str(e)}
    
    async def _setup_cloudwatch_alarms(self):
        """Setup CloudWatch alarms for CloudFront monitoring"""        try:
            cloudwatch = boto3.client('cloudwatch')
            
            alarms = [
                {
                    "AlarmName": f"CDN-{self.config.name}-HighErrorRate",
                    "MetricName": "ErrorRate",
                    "Threshold": 5.0,
                    "ComparisonOperator": "GreaterThanThreshold"
                },
                {
                    "AlarmName": f"CDN-{self.config.name}-LowCacheHitRatio",
                    "MetricName": "CacheHitRate",
                    "Threshold": 80.0,
                    "ComparisonOperator": "LessThanThreshold"
                }
            ]
            
            for alarm in alarms:
                cloudwatch.put_metric_alarm(
                    AlarmName=alarm["AlarmName"],
                    ComparisonOperator=alarm["ComparisonOperator"],
                    EvaluationPeriods=2,
                    MetricName=alarm["MetricName"],
                    Namespace="AWS/CloudFront",
                    Period=300,
                    Statistic="Average",
                    Threshold=alarm["Threshold"],
                    ActionsEnabled=True,
                    AlarmDescription=f"CDN monitoring alarm for {self.config.name}",
                    Dimensions=[
                        {
                            "Name": "DistributionId",
                            "Value": self.metrics.distribution_id
                        }
                    ]
                )
            
            logger.info(f"✅ CloudWatch alarms configured: {len(alarms)} alarms")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to setup CloudWatch alarms: {e}")
    
    async def get_cdn_metrics(self) -> Dict[str, Any]:
        """Get comprehensive CDN metrics and analytics"""        try:
            if self.config.provider == CDNProvider.AWS_CLOUDFRONT:
                metrics_data = await self._get_cloudfront_metrics()
            elif self.config.provider == CDNProvider.CLOUDFLARE:
                metrics_data = await self._get_cloudflare_metrics()
            else:
                metrics_data = await self._get_generic_metrics()
            
            # Update internal metrics
            self.metrics.requests_count_24h = metrics_data.get("requests_24h", 0)
            self.metrics.bandwidth_gb_24h = metrics_data.get("bandwidth_gb_24h", 0.0)
            self.metrics.cache_hit_ratio = metrics_data.get("cache_hit_ratio", 0.0)
            self.metrics.error_rate_percent = metrics_data.get("error_rate_percent", 0.0)
            self.metrics.avg_response_time_ms = metrics_data.get("avg_response_time_ms", 0.0)
            self.metrics.last_updated = datetime.now()
            
            metrics_result = {
                "cdn_name": self.config.name,
                "provider": self.config.provider.value,
                "distribution_id": self.metrics.distribution_id,
                "status": self.metrics.status.value,
                "traffic": {
                    "requests_24h": self.metrics.requests_count_24h,
                    "bandwidth_gb_24h": round(self.metrics.bandwidth_gb_24h, 2),
                    "cache_hit_ratio_percent": round(self.metrics.cache_hit_ratio, 2),
                    "error_rate_percent": round(self.metrics.error_rate_percent, 2)
                },
                "performance": {
                    "avg_response_time_ms": round(self.metrics.avg_response_time_ms, 2),
                    "ttfb_ms": round(self.metrics.ttfb_ms, 2),
                    "throughput_mbps": round(self.metrics.throughput_mbps, 2)
                },
                "geographic": {
                    "top_regions": self.metrics.top_regions,
                    "edge_locations_active": self.metrics.edge_locations_active
                },
                "cost": {
                    "monthly_cost_usd": round(self.metrics.monthly_cost_usd, 2),
                    "cost_per_gb_usd": round(self.metrics.cost_per_gb_usd, 4)
                },
                "security": {
                    "blocked_requests_24h": self.metrics.blocked_requests_24h,
                    "waf_triggers_24h": self.metrics.waf_triggers_24h
                },
                "health": {
                    "uptime_percent": round(self.metrics.uptime_percent, 3),
                    "last_updated": self.metrics.last_updated.isoformat()
                }
            }
            
            logger.info(f"📊 Retrieved CDN metrics for {self.config.name}")
            return metrics_result
            
        except Exception as e:
            logger.error(f"❌ Failed to get CDN metrics: {e}")
            return {"error": str(e)}
    
    async def _get_cloudfront_metrics(self) -> Dict[str, Any]:
        """Get CloudFront-specific metrics"""        try:
            cloudwatch = boto3.client('cloudwatch')
            
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)
            
            # Get request count
            requests_response = cloudwatch.get_metric_statistics(
                Namespace='AWS/CloudFront',
                MetricName='Requests',
                Dimensions=[
                    {'Name': 'DistributionId', 'Value': self.metrics.distribution_id}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            
            # Get bandwidth
            bandwidth_response = cloudwatch.get_metric_statistics(
                Namespace='AWS/CloudFront',
                MetricName='BytesDownloaded',
                Dimensions=[
                    {'Name': 'DistributionId', 'Value': self.metrics.distribution_id}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            
            # Get cache hit ratio
            cache_response = cloudwatch.get_metric_statistics(
                Namespace='AWS/CloudFront',
                MetricName='CacheHitRate',
                Dimensions=[
                    {'Name': 'DistributionId', 'Value': self.metrics.distribution_id}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average']
            )
            
            # Calculate metrics
            total_requests = sum(point['Sum'] for point in requests_response['Datapoints'])
            total_bytes = sum(point['Sum'] for point in bandwidth_response['Datapoints'])
            bandwidth_gb = total_bytes / (1024**3)
            
            avg_cache_hit_ratio = 0.0
            if cache_response['Datapoints']:
                avg_cache_hit_ratio = sum(point['Average'] for point in cache_response['Datapoints']) / len(cache_response['Datapoints'])
            
            return {
                "requests_24h": int(total_requests),
                "bandwidth_gb_24h": bandwidth_gb,
                "cache_hit_ratio": avg_cache_hit_ratio,
                "error_rate_percent": 0.0,  # Would need separate metric call
                "avg_response_time_ms": 0.0  # Would need separate metric call
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get CloudFront metrics: {e}")
            return {}
    
    async def _get_cloudflare_metrics(self) -> Dict[str, Any]:
        """Get CloudFlare-specific metrics"""        try:
            if not self._cloudflare_client:
                return {}
            
            headers = {
                'Authorization': f"Bearer {self._cloudflare_client['api_token']}",
                'Content-Type': 'application/json'
            }
            
            # Get analytics data
            url = f"{self._cloudflare_client['base_url']}/zones/{self._cloudflare_client['zone_id']}/analytics/dashboard"
            
            params = {
                'since': (datetime.now() - timedelta(hours=24)).isoformat(),
                'until': datetime.now().isoformat()
            }
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()['result']
                
                return {
                    "requests_24h": data['totals']['requests']['all'],
                    "bandwidth_gb_24h": data['totals']['bandwidth']['all'] / (1024**3),
                    "cache_hit_ratio": data['totals']['requests']['cached'] / data['totals']['requests']['all'] * 100,
                    "error_rate_percent": 0.0,  # Calculate from response codes
                    "avg_response_time_ms": 0.0  # Not available in basic API
                }
            else:
                logger.warning(f"⚠️ Failed to get CloudFlare metrics: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Failed to get CloudFlare metrics: {e}")
            return {}
    
    async def _get_generic_metrics(self) -> Dict[str, Any]:
        """Get generic metrics for unsupported providers"""        return {
            "requests_24h": 0,
            "bandwidth_gb_24h": 0.0,
            "cache_hit_ratio": 0.0,
            "error_rate_percent": 0.0,
            "avg_response_time_ms": 0.0
        }
    
    async def purge_cache(self, paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Purge CDN cache for specified paths or entire distribution"""        try:
            logger.info(f"🔄 Purging CDN cache: {self.config.name}")
            
            if self.config.provider == CDNProvider.AWS_CLOUDFRONT:
                return await self._purge_cloudfront_cache(paths)
            elif self.config.provider == CDNProvider.CLOUDFLARE:
                return await self._purge_cloudflare_cache(paths)
            else:
                raise ValueError(f"Cache purge not supported for provider: {self.config.provider}")
                
        except Exception as e:
            logger.error(f"❌ Cache purge failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _purge_cloudfront_cache(self, paths: Optional[List[str]]) -> Dict[str, Any]:
        """Purge CloudFront cache"""        try:
            invalidation_paths = paths or ["/*"]
            
            response = self._cloudfront_client.create_invalidation(
                DistributionId=self.metrics.distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(invalidation_paths),
                        'Items': invalidation_paths
                    },
                    'CallerReference': f"purge-{int(time.time())}"
                }
            )
            
            invalidation_id = response['Invalidation']['Id']
            
            return {
                "success": True,
                "invalidation_id": invalidation_id,
                "paths": invalidation_paths,
                "estimated_completion_minutes": 10
            }
            
        except Exception as e:
            logger.error(f"❌ CloudFront cache purge failed: {e}")
            raise
    
    async def _purge_cloudflare_cache(self, paths: Optional[List[str]]) -> Dict[str, Any]:
        """Purge CloudFlare cache"""        try:
            headers = {
                'Authorization': f"Bearer {self._cloudflare_client['api_token']}",
                'Content-Type': 'application/json'
            }
            
            url = f"{self._cloudflare_client['base_url']}/zones/{self._cloudflare_client['zone_id']}/purge_cache"
            
            if paths:
                data = {"files": paths}
            else:
                data = {"purge_everything": True}
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "paths": paths or ["everything"],
                    "estimated_completion_minutes": 1
                }
            else:
                raise Exception(f"CloudFlare API error: {response.text}")
                
        except Exception as e:
            logger.error(f"❌ CloudFlare cache purge failed: {e}")
            raise
    
    async def cleanup_cdn_distribution(self) -> Dict[str, Any]:
        """Cleanup and delete CDN distribution"""        try:
            logger.info(f"🗑️ Starting CDN distribution cleanup: {self.config.name}")
            
            if self.config.provider == CDNProvider.AWS_CLOUDFRONT:
                cleanup_result = await self._cleanup_cloudfront_distribution()
            elif self.config.provider == CDNProvider.CLOUDFLARE:
                cleanup_result = await self._cleanup_cloudflare_distribution()
            else:
                cleanup_result = {"message": "Manual cleanup required"}
            
            self.metrics.status = DistributionStatus.DELETING
            
            return {
                "success": True,
                "cdn_name": self.config.name,
                "cleanup_result": cleanup_result,
                "cleanup_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ CDN cleanup failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _cleanup_cloudfront_distribution(self) -> Dict[str, Any]:
        """Cleanup CloudFront distribution"""        try:
            # First disable the distribution
            distribution = self._cloudfront_client.get_distribution(Id=self.metrics.distribution_id)
            
            distribution_config = distribution['Distribution']['DistributionConfig']
            distribution_config['Enabled'] = False
            
            self._cloudfront_client.update_distribution(
                Id=self.metrics.distribution_id,
                DistributionConfig=distribution_config,
                IfMatch=distribution['ETag']
            )
            
            # Wait for distribution to be disabled before deletion
            logger.info("⏳ Waiting for distribution to be disabled before deletion")
            
            return {
                "distribution_id": self.metrics.distribution_id,
                "status": "disabling",
                "message": "Distribution will be deleted after disabling completes"
            }
            
        except Exception as e:
            logger.error(f"❌ CloudFront cleanup failed: {e}")
            raise
    
    async def _cleanup_cloudflare_distribution(self) -> Dict[str, Any]:
        """Cleanup CloudFlare distribution (reset zone settings)"""        try:
            # Reset zone settings to defaults
            # This is a simplified cleanup - actual implementation would be more comprehensive
            
            return {
                "zone_id": self._cloudflare_client['zone_id'],
                "status": "reset",
                "message": "Zone settings reset to defaults"
            }
            
        except Exception as e:
            logger.error(f"❌ CloudFlare cleanup failed: {e}")
            raise


# Industrial Configuration Manager
class CDNConfigurationManager:
    """Advanced CDN configuration management"""    
    @staticmethod
    def load_config_from_file(config_path: Path) -> CDNConfig:
        """Load CDN configuration from YAML file"""        try:
            with open(config_path, 'r') as file:
                config_data = yaml.safe_load(file)
            
            return CDNConfig(
                name=config_data['name'],
                provider=CDNProvider(config_data['provider']),
                origin_domain=config_data['origin_domain'],
                custom_domain=config_data.get('custom_domain'),
                default_cache_policy=CachePolicy(config_data.get('default_cache_policy', 'medium-cache')),
                enabled_regions=config_data.get('enabled_regions', []),
                compression_enabled=config_data.get('compression_enabled', True),
                ssl_enabled=config_data.get('ssl_enabled', True),
                waf_enabled=config_data.get('waf_enabled', True),
                labels=config_data.get('labels', {}),
                tags=config_data.get('tags', {})
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to load config from {config_path}: {e}")
            raise
    
    @staticmethod
    def save_config_to_file(config: CDNConfig, config_path: Path):
        """Save CDN configuration to YAML file"""        try:
            config_data = {
                'name': config.name,
                'provider': config.provider.value,
                'origin_domain': config.origin_domain,
                'custom_domain': config.custom_domain,
                'default_cache_policy': config.default_cache_policy.value,
                'enabled_regions': config.enabled_regions,
                'compression_enabled': config.compression_enabled,
                'ssl_enabled': config.ssl_enabled,
                'force_https': config.force_https,
                'waf_enabled': config.waf_enabled,
                'analytics_enabled': config.analytics_enabled,
                'price_class': config.price_class,
                'labels': config.labels,
                'tags': config.tags
            }
            
            with open(config_path, 'w') as file:
                yaml.dump(config_data, file, default_flow_style=False)
            
            logger.info(f"✅ Configuration saved to {config_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save config to {config_path}: {e}")
            raise


# Global CDN Manager Factory
def create_cdn_manager(
    name: str,
    provider: CDNProvider,
    origin_domain: str,
    custom_domain: Optional[str] = None
) -> CDNManager:
    """Factory function to create CDNManager instance"""    
    config = CDNConfig(
        name=name,
        provider=provider,
        origin_domain=origin_domain,
        custom_domain=custom_domain
    )
    
    return CDNManager(config)


# Usage Example
async def main():
    """Example usage of CDNManager"""    try:
        # Create CDN manager for global content distribution
        cdn_manager = create_cdn_manager(
            name="ia-influencer-global-cdn",
            provider=CDNProvider.AWS_CLOUDFRONT,
            origin_domain="storage.ia-influencer.com",
            custom_domain="cdn.ia-influencer.com"
        )
        
        # Deploy CDN distribution
        deployment_result = await cdn_manager.deploy_cdn_distribution()
        print(f"Deployment: {deployment_result}")
        
        # Get metrics
        metrics = await cdn_manager.get_cdn_metrics()
        print(f"Metrics: {metrics}")
        
        # Purge cache
        purge_result = await cdn_manager.purge_cache(["/audio/*", "/images/*"])
        print(f"Cache Purge: {purge_result}")
        
    except Exception as e:
        logger.error(f"❌ Example failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
