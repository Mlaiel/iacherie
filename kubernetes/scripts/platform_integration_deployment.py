#!/usr/bin/env python3
"""Platform Integration Deployment Manager
Handles deployment of platform APIs integration for multi-platform content monitoring
"""import os
import sys
import time
import json
import logging
import subprocess
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import yaml
import requests
import docker
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import redis
import psycopg2
from sqlalchemy import create_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SupportedPlatform(Enum):
    """Supported platforms for integration"""    SPOTIFY = "spotify"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    SOUNDCLOUD = "soundcloud"
    BANDCAMP = "bandcamp"
    APPLE_MUSIC = "apple_music"
    DEEZER = "deezer"
    TIDAL = "tidal"


class IntegrationType(Enum):
    """Type of platform integration"""    API_OFFICIAL = "api_official"
    API_UNOFFICIAL = "api_unofficial"
    WEB_SCRAPING = "web_scraping"
    RSS_FEED = "rss_feed"
    WEBHOOK = "webhook"


class MonitoringMode(Enum):
    """Content monitoring mode"""    PASSIVE_MONITORING = "passive_monitoring"
    ACTIVE_SCANNING = "active_scanning"
    REAL_TIME_ALERTS = "real_time_alerts"
    BATCH_PROCESSING = "batch_processing"


class DataCollectionScope(Enum):
    """Scope of data collection"""    METADATA_ONLY = "metadata_only"
    FULL_CONTENT = "full_content"
    ANALYTICS_DATA = "analytics_data"
    USER_INTERACTIONS = "user_interactions"
    REVENUE_DATA = "revenue_data"


@dataclass
class PlatformIntegrationConfig:
    """Platform integration configuration"""    platform: SupportedPlatform
    integration_type: IntegrationType
    monitoring_mode: MonitoringMode
    data_scope: DataCollectionScope
    api_credentials: Dict[str, str]
    rate_limits: Dict[str, int]
    content_types: List[str]
    filtering_rules: Dict[str, Any]
    compliance_settings: Dict[str, bool]


@dataclass
class PlatformDeploymentConfig:
    """Platform deployment configuration"""    platforms: List[PlatformIntegrationConfig]
    global_settings: Dict[str, Any]
    monitoring_config: Dict[str, Any]
    storage_config: Dict[str, Any]
    security_config: Dict[str, Any]
    scaling_config: Dict[str, Any]


@dataclass
class PlatformStatus:
    """Status of platform integration"""    platform: SupportedPlatform
    status: str
    last_sync: datetime
    api_health: bool
    rate_limit_remaining: int
    error_count: int
    data_collected_24h: int
    compliance_status: str


class PlatformIntegrationDeploymentManager:
    """    Manages deployment of platform integration services for content monitoring
    and revenue tracking across multiple platforms
    """    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize platform integration deployment manager"""        self.config_path = config_path or "/etc/ia-influencer/platform-integration-deployment.yaml"
        self.config = self._load_configuration()
        self.docker_client = docker.from_env()
        self.redis_client = redis.Redis(
            host=self.config.get('redis', {}).get('host', 'localhost'),
            port=self.config.get('redis', {}).get('port', 6379),
            db=self.config.get('redis', {}).get('db', 3)
        )
        self.k8s_apps_v1 = client.AppsV1Api()
        self.k8s_core_v1 = client.CoreV1Api()
        
        # Initialize platform configurations
        self._initialize_platform_configurations()
        
    def _load_configuration(self) -> Dict[str, Any]:
        """Load platform integration deployment configuration"""        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Platform integration configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {self.config_path}")
            return self._get_default_platform_config()
    
    def _get_default_platform_config(self) -> Dict[str, Any]:
        """Get default platform integration configuration"""        return {
            'platforms': {
                'spotify': {
                    'enabled': True,
                    'integration_type': 'api_official',
                    'api_endpoints': {
                        'base_url': 'https://api.spotify.com/v1',
                        'auth_url': 'https://accounts.spotify.com/api/token',
                        'scopes': ['user-read-private', 'user-read-email', 'playlist-read-private']
                    },
                    'rate_limits': {
                        'requests_per_second': 10,
                        'requests_per_hour': 1000,
                        'requests_per_day': 10000
                    },
                    'content_types': ['track', 'album', 'playlist', 'artist'],
                    'monitoring_mode': 'real_time_alerts',
                    'data_scope': 'analytics_data',
                    'compliance': {
                        'gdpr_compliant': True,
                        'ccpa_compliant': True,
                        'data_retention_days': 365
                    }
                },
                'youtube': {
                    'enabled': True,
                    'integration_type': 'api_official',
                    'api_endpoints': {
                        'base_url': 'https://www.googleapis.com/youtube/v3',
                        'auth_url': 'https://oauth2.googleapis.com/token',
                        'scopes': ['youtube.readonly', 'yt-analytics.readonly']
                    },
                    'rate_limits': {
                        'requests_per_second': 5,
                        'requests_per_hour': 5000,
                        'requests_per_day': 50000
                    },
                    'content_types': ['video', 'channel', 'playlist', 'comment'],
                    'monitoring_mode': 'active_scanning',
                    'data_scope': 'full_content',
                    'compliance': {
                        'coppa_compliant': True,
                        'gdpr_compliant': True,
                        'data_retention_days': 730
                    }
                },
                'instagram': {
                    'enabled': True,
                    'integration_type': 'api_official',
                    'api_endpoints': {
                        'base_url': 'https://graph.instagram.com',
                        'auth_url': 'https://api.instagram.com/oauth/access_token',
                        'scopes': ['instagram_basic', 'instagram_content_publish']
                    },
                    'rate_limits': {
                        'requests_per_second': 2,
                        'requests_per_hour': 200,
                        'requests_per_day': 5000
                    },
                    'content_types': ['post', 'story', 'reel', 'igtv'],
                    'monitoring_mode': 'passive_monitoring',
                    'data_scope': 'metadata_only',
                    'compliance': {
                        'gdpr_compliant': True,
                        'meta_policy_compliant': True,
                        'data_retention_days': 365
                    }
                },
                'tiktok': {
                    'enabled': True,
                    'integration_type': 'api_unofficial',
                    'api_endpoints': {
                        'base_url': 'https://open-api.tiktok.com',
                        'auth_url': 'https://open-api.tiktok.com/platform/oauth/connect',
                        'scopes': ['user.info.basic', 'user.info.stats', 'video.list']
                    },
                    'rate_limits': {
                        'requests_per_second': 1,
                        'requests_per_hour': 100,
                        'requests_per_day': 1000
                    },
                    'content_types': ['video', 'profile', 'hashtag', 'sound'],
                    'monitoring_mode': 'batch_processing',
                    'data_scope': 'analytics_data',
                    'compliance': {
                        'coppa_compliant': True,
                        'gdpr_compliant': True,
                        'data_retention_days': 180
                    }
                },
                'twitter': {
                    'enabled': True,
                    'integration_type': 'api_official',
                    'api_endpoints': {
                        'base_url': 'https://api.twitter.com/2',
                        'auth_url': 'https://api.twitter.com/oauth2/token',
                        'scopes': ['tweet.read', 'users.read', 'offline.access']
                    },
                    'rate_limits': {
                        'requests_per_second': 3,
                        'requests_per_hour': 300,
                        'requests_per_day': 5000
                    },
                    'content_types': ['tweet', 'thread', 'media', 'profile'],
                    'monitoring_mode': 'real_time_alerts',
                    'data_scope': 'full_content',
                    'compliance': {
                        'gdpr_compliant': True,
                        'twitter_policy_compliant': True,
                        'data_retention_days': 365
                    }
                }
            },
            'global_settings': {
                'concurrent_workers': 10,
                'retry_attempts': 3,
                'timeout_seconds': 30,
                'proxy_rotation': True,
                'user_agent_rotation': True,
                'respect_robots_txt': True
            },
            'monitoring': {
                'health_check_interval': 60,
                'metrics_collection_interval': 30,
                'alert_on_failure': True,
                'alert_on_rate_limit': True,
                'performance_tracking': True
            },
            'storage': {
                'raw_data_retention_days': 30,
                'processed_data_retention_days': 365,
                'compression_enabled': True,
                'encryption_enabled': True
            },
            'security': {
                'api_key_rotation_days': 90,
                'access_token_refresh_hours': 1,
                'ip_whitelisting': True,
                'request_signing': True,
                'ssl_verification': True
            }
        }
    
    def _initialize_platform_configurations(self) -> None:
        """Initialize platform-specific configurations"""        platforms_config = self.config.get('platforms', {})
        
        for platform, config in platforms_config.items():
            if config.get('enabled', False):
                # Store platform configuration in Redis
                self.redis_client.hset(
                    f'platform:config:{platform}',
                    mapping={
                        'integration_type': config.get('integration_type', ''),
                        'monitoring_mode': config.get('monitoring_mode', ''),
                        'data_scope': config.get('data_scope', ''),
                        'rate_limits': json.dumps(config.get('rate_limits', {})),
                        'content_types': json.dumps(config.get('content_types', [])),
                        'compliance': json.dumps(config.get('compliance', {}))
                    }
                )
                logger.info(f"Platform configuration initialized: {platform}")
    
    def deploy_platform_integrations(self, deployment_config: PlatformDeploymentConfig) -> str:
        """Deploy platform integration services"""        deployment_id = f"platform-integration-{int(time.time())}"
        
        try:
            logger.info(f"Starting platform integration deployment: {deployment_id}")
            
            # Deploy shared infrastructure
            self._deploy_shared_infrastructure(deployment_config)
            
            # Deploy individual platform integrations
            for platform_config in deployment_config.platforms:
                self._deploy_platform_integration(platform_config, deployment_config)
            
            # Deploy platform orchestrator
            self._deploy_platform_orchestrator(deployment_config)
            
            # Deploy monitoring and analytics
            self._deploy_platform_monitoring(deployment_config.monitoring_config)
            
            # Deploy compliance system
            self._deploy_compliance_system(deployment_config)
            
            # Initialize integration workflows
            self._initialize_integration_workflows(deployment_config)
            
            # Verify deployment
            if self._verify_platform_deployment(deployment_id):
                logger.info(f"Platform integration deployment completed: {deployment_id}")
                return deployment_id
            else:
                raise Exception("Platform integration deployment verification failed")
                
        except Exception as e:
            logger.error(f"Platform integration deployment failed: {str(e)}")
            self._rollback_platform_deployment(deployment_id)
            raise
    
    def _deploy_shared_infrastructure(self, config: PlatformDeploymentConfig) -> None:
        """Deploy shared infrastructure for platform integrations"""        logger.info("Deploying shared infrastructure...")
        
        # Deploy API gateway
        gateway_manifest = self._create_api_gateway_manifest(config)
        
        try:
            self.k8s_apps_v1.create_namespaced_deployment(
                namespace="ia-influencer",
                body=gateway_manifest
            )
            
            # Create service
            service_manifest = self._create_api_gateway_service()
            self.k8s_core_v1.create_namespaced_service(
                namespace="ia-influencer",
                body=service_manifest
            )
            
            logger.info("API gateway deployed successfully")
            
        except ApiException as e:
            logger.error(f"Failed to deploy API gateway: {e}")
            raise
        
        # Deploy rate limiter
        self._deploy_rate_limiter(config.global_settings)
        
        # Deploy proxy service
        self._deploy_proxy_service(config.global_settings)
    
    def _deploy_platform_integration(self, platform_config: PlatformIntegrationConfig, deployment_config: PlatformDeploymentConfig) -> None:
        """Deploy specific platform integration"""        logger.info(f"Deploying platform integration: {platform_config.platform.value}")
        
        # Create deployment manifest
        deployment_manifest = self._create_platform_integration_manifest(platform_config, deployment_config)
        
        try:
            self.k8s_apps_v1.create_namespaced_deployment(
                namespace="ia-influencer",
                body=deployment_manifest
            )
            
            # Create service
            service_manifest = self._create_platform_integration_service(platform_config.platform)
            self.k8s_core_v1.create_namespaced_service(
                namespace="ia-influencer",
                body=service_manifest
            )
            
            # Initialize platform-specific configuration
            self._initialize_platform_integration(platform_config)
            
            logger.info(f"Platform integration {platform_config.platform.value} deployed successfully")
            
        except ApiException as e:
            logger.error(f"Failed to deploy platform integration {platform_config.platform.value}: {e}")
            raise
    
    def _deploy_platform_orchestrator(self, config: PlatformDeploymentConfig) -> None:
        """Deploy platform orchestrator for coordinating integrations"""        logger.info("Deploying platform orchestrator...")
        
        orchestrator_manifest = self._create_platform_orchestrator_manifest(config)
        
        try:
            self.k8s_apps_v1.create_namespaced_deployment(
                namespace="ia-influencer",
                body=orchestrator_manifest
            )
            
            # Create service
            service_manifest = self._create_platform_orchestrator_service()
            self.k8s_core_v1.create_namespaced_service(
                namespace="ia-influencer",
                body=service_manifest
            )
            
            logger.info("Platform orchestrator deployed successfully")
            
        except ApiException as e:
            logger.error(f"Failed to deploy platform orchestrator: {e}")
            raise
    
    def _deploy_compliance_system(self, config: PlatformDeploymentConfig) -> None:
        """Deploy compliance monitoring system"""        logger.info("Deploying compliance system...")
        
        compliance_manifest = self._create_compliance_system_manifest(config)
        
        try:
            self.k8s_apps_v1.create_namespaced_deployment(
                namespace="ia-influencer",
                body=compliance_manifest
            )
            
            logger.info("Compliance system deployed successfully")
            
        except ApiException as e:
            logger.error(f"Failed to deploy compliance system: {e}")
            raise
    
    def _initialize_integration_workflows(self, config: PlatformDeploymentConfig) -> None:
        """Initialize integration workflows and automation"""        logger.info("Initializing integration workflows...")
        
        # Setup data collection workflows
        self._setup_data_collection_workflows(config.platforms)
        
        # Configure monitoring workflows
        self._configure_monitoring_workflows(config.monitoring_config)
        
        # Initialize compliance workflows
        self._initialize_compliance_workflows(config)
        
        # Setup alert workflows
        self._setup_alert_workflows(config.monitoring_config)
    
    def _setup_data_collection_workflows(self, platforms: List[PlatformIntegrationConfig]) -> None:
        """Setup data collection workflows for each platform"""        logger.info("Setting up data collection workflows...")
        
        for platform_config in platforms:
            workflow_config = {
                'platform': platform_config.platform.value,
                'monitoring_mode': platform_config.monitoring_mode.value,
                'data_scope': platform_config.data_scope.value,
                'content_types': platform_config.content_types,
                'rate_limits': platform_config.rate_limits,
                'last_sync': datetime.now().isoformat()
            }
            
            # Store workflow configuration
            self.redis_client.hset(
                f'platform:workflow:{platform_config.platform.value}',
                mapping=workflow_config
            )
        
        logger.info("Data collection workflows configured")
    
    def _create_platform_integration_manifest(self, platform_config: PlatformIntegrationConfig, deployment_config: PlatformDeploymentConfig) -> Dict[str, Any]:
        """Create platform integration deployment manifest"""        platform_name = platform_config.platform.value.replace('_', '-')
        
        # Environment variables
        env_vars = [
            {'name': 'PLATFORM', 'value': platform_config.platform.value},
            {'name': 'INTEGRATION_TYPE', 'value': platform_config.integration_type.value},
            {'name': 'MONITORING_MODE', 'value': platform_config.monitoring_mode.value},
            {'name': 'DATA_SCOPE', 'value': platform_config.data_scope.value},
            {'name': 'CONTENT_TYPES', 'value': json.dumps(platform_config.content_types)},
            {'name': 'RATE_LIMITS', 'value': json.dumps(platform_config.rate_limits)},
            {'name': 'FILTERING_RULES', 'value': json.dumps(platform_config.filtering_rules)},
            {'name': 'COMPLIANCE_SETTINGS', 'value': json.dumps(platform_config.compliance_settings)}
        ]
        
        # Add API credentials as environment variables (from secrets)
        for key, value in platform_config.api_credentials.items():
            env_vars.append({
                'name': f'API_{key.upper()}',
                'valueFrom': {
                    'secretKeyRef': {
                        'name': f'{platform_name}-api-credentials',
                        'key': key
                    }
                }
            })
        
        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': f'platform-integration-{platform_name}',
                'namespace': 'ia-influencer',
                'labels': {
                    'app': f'platform-integration-{platform_name}',
                    'component': 'platform-integration',
                    'platform': platform_config.platform.value
                }
            },
            'spec': {
                'replicas': deployment_config.scaling_config.get('replicas', 2),
                'selector': {
                    'matchLabels': {
                        'app': f'platform-integration-{platform_name}'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': f'platform-integration-{platform_name}',
                            'platform': platform_config.platform.value
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': f'{platform_name}-integration',
                            'image': f'ia-influencer/platform-{platform_name}:latest',
                            'ports': [{'containerPort': 8080}],
                            'env': env_vars,
                            'resources': {
                                'limits': {
                                    'cpu': '1',
                                    'memory': '2Gi'
                                },
                                'requests': {
                                    'cpu': '500m',
                                    'memory': '1Gi'
                                }
                            },
                            'livenessProbe': {
                                'httpGet': {
                                    'path': '/health',
                                    'port': 8080
                                },
                                'initialDelaySeconds': 30,
                                'periodSeconds': 10
                            },
                            'readinessProbe': {
                                'httpGet': {
                                    'path': '/ready',
                                    'port': 8080
                                },
                                'initialDelaySeconds': 5,
                                'periodSeconds': 5
                            }
                        }]
                    }
                }
            }
        }
    
    def _create_platform_orchestrator_manifest(self, config: PlatformDeploymentConfig) -> Dict[str, Any]:
        """Create platform orchestrator deployment manifest"""        return {
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': 'platform-orchestrator',
                'namespace': 'ia-influencer',
                'labels': {
                    'app': 'platform-orchestrator',
                    'component': 'platform-integration'
                }
            },
            'spec': {
                'replicas': 3,
                'selector': {
                    'matchLabels': {
                        'app': 'platform-orchestrator'
                    }
                },
                'template': {
                    'metadata': {
                        'labels': {
                            'app': 'platform-orchestrator'
                        }
                    },
                    'spec': {
                        'containers': [{
                            'name': 'orchestrator',
                            'image': 'ia-influencer/platform-orchestrator:latest',
                            'ports': [{'containerPort': 8080}],
                            'env': [
                                {'name': 'PLATFORMS', 'value': json.dumps([p.platform.value for p in config.platforms])},
                                {'name': 'CONCURRENT_WORKERS', 'value': str(config.global_settings.get('concurrent_workers', 10))},
                                {'name': 'RETRY_ATTEMPTS', 'value': str(config.global_settings.get('retry_attempts', 3))},
                                {'name': 'TIMEOUT_SECONDS', 'value': str(config.global_settings.get('timeout_seconds', 30))}
                            ],
                            'resources': {
                                'limits': {
                                    'cpu': '2',
                                    'memory': '4Gi'
                                },
                                'requests': {
                                    'cpu': '1',
                                    'memory': '2Gi'
                                }
                            }
                        }]
                    }
                }
            }
        }
    
    def get_platform_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive platform integration status"""        status = {
            'timestamp': datetime.now().isoformat(),
            'platforms': self._get_platforms_status(),
            'orchestrator': self._get_orchestrator_status(),
            'api_gateway': self._get_api_gateway_status(),
            'compliance': self._get_compliance_status(),
            'performance_metrics': self._get_platform_performance_metrics(),
            'overall_health': 'unknown'
        }
        
        # Determine overall health
        platforms_healthy = all(platform['healthy'] for platform in status['platforms'].values())
        orchestrator_healthy = status['orchestrator']['healthy']
        gateway_healthy = status['api_gateway']['healthy']
        
        all_healthy = platforms_healthy and orchestrator_healthy and gateway_healthy
        status['overall_health'] = 'healthy' if all_healthy else 'degraded'
        
        return status
    
    def _get_platforms_status(self) -> Dict[str, Any]:
        """Get status of all platform integrations"""        platforms_status = {}
        
        for platform in SupportedPlatform:
            platform_name = platform.value.replace('_', '-')
            
            try:
                deployment = self.k8s_apps_v1.read_namespaced_deployment(
                    name=f'platform-integration-{platform_name}',
                    namespace='ia-influencer'
                )
                
                ready_replicas = deployment.status.ready_replicas or 0
                total_replicas = deployment.spec.replicas
                
                # Get platform-specific metrics
                platform_status = self._get_platform_status(platform)
                
                platforms_status[platform.value] = {
                    'healthy': ready_replicas == total_replicas and platform_status.api_health,
                    'ready_replicas': ready_replicas,
                    'total_replicas': total_replicas,
                    'status': 'running' if ready_replicas > 0 else 'down',
                    'api_health': platform_status.api_health,
                    'last_sync': platform_status.last_sync.isoformat() if platform_status.last_sync else None,
                    'rate_limit_remaining': platform_status.rate_limit_remaining,
                    'error_count': platform_status.error_count,
                    'data_collected_24h': platform_status.data_collected_24h,
                    'compliance_status': platform_status.compliance_status
                }
                
            except ApiException:
                platforms_status[platform.value] = {
                    'healthy': False,
                    'ready_replicas': 0,
                    'total_replicas': 0,
                    'status': 'not_deployed',
                    'api_health': False,
                    'last_sync': None,
                    'rate_limit_remaining': 0,
                    'error_count': 0,
                    'data_collected_24h': 0,
                    'compliance_status': 'unknown'
                }
        
        return platforms_status
    
    def _get_platform_status(self, platform: SupportedPlatform) -> PlatformStatus:
        """Get detailed status for specific platform"""        # In production, these would be real metrics from monitoring system
        return PlatformStatus(
            platform=platform,
            status="active",
            last_sync=datetime.now() - timedelta(minutes=5),
            api_health=True,
            rate_limit_remaining=850,
            error_count=2,
            data_collected_24h=15420,
            compliance_status="compliant"
        )
    
    def _verify_platform_deployment(self, deployment_id: str) -> bool:
        """Verify platform integration deployment"""        logger.info(f"Verifying platform integration deployment: {deployment_id}")
        
        try:
            status = self.get_platform_integration_status()
            
            # Check if all required components are healthy
            platforms_healthy = all(platform['healthy'] for platform in status['platforms'].values())
            orchestrator_healthy = status['orchestrator']['healthy']
            gateway_healthy = status['api_gateway']['healthy']
            
            all_healthy = platforms_healthy and orchestrator_healthy and gateway_healthy
            
            if all_healthy:
                logger.info("Platform integration deployment verification successful")
                return True
            else:
                logger.error("Platform integration deployment verification failed")
                return False
                
        except Exception as e:
            logger.error(f"Platform integration deployment verification error: {str(e)}")
            return False
    
    def _rollback_platform_deployment(self, deployment_id: str) -> None:
        """Rollback failed platform deployment"""        logger.info(f"Rolling back platform integration deployment: {deployment_id}")
        
        try:
            # Delete failed deployments
            deployments = [
                'platform-orchestrator',
                'api-gateway',
                'rate-limiter',
                'proxy-service',
                'compliance-system'
            ]
            
            # Add platform-specific deployments
            for platform in SupportedPlatform:
                platform_name = platform.value.replace('_', '-')
                deployments.append(f'platform-integration-{platform_name}')
            
            for deployment_name in deployments:
                try:
                    self.k8s_apps_v1.delete_namespaced_deployment(
                        name=deployment_name,
                        namespace='ia-influencer'
                    )
                    logger.info(f"Deleted deployment: {deployment_name}")
                except ApiException:
                    logger.warning(f"Deployment not found or already deleted: {deployment_name}")
            
            logger.info("Platform integration deployment rollback completed")
            
        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")
            raise


def main():
    """Main function for CLI usage"""    import argparse
    
    parser = argparse.ArgumentParser(description='Platform Integration Deployment Manager')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--deploy', action='store_true', help='Deploy platform integrations')
    parser.add_argument('--status', action='store_true', help='Get platform integration status')
    parser.add_argument('--platforms', nargs='+', help='Platforms to deploy')
    
    args = parser.parse_args()
    
    manager = PlatformIntegrationDeploymentManager(config_path=args.config)
    
    if args.deploy:
        # Parse platforms from command line or use defaults
        platforms = []
        if args.platforms:
            for platform_name in args.platforms:
                try:
                    platform = SupportedPlatform(platform_name)
                    platform_config = PlatformIntegrationConfig(
                        platform=platform,
                        integration_type=IntegrationType.API_OFFICIAL,
                        monitoring_mode=MonitoringMode.REAL_TIME_ALERTS,
                        data_scope=DataCollectionScope.ANALYTICS_DATA,
                        api_credentials={},
                        rate_limits={'requests_per_hour': 1000},
                        content_types=['default'],
                        filtering_rules={},
                        compliance_settings={'gdpr': True}
                    )
                    platforms.append(platform_config)
                except ValueError:
                    logger.warning(f"Unknown platform: {platform_name}")
        else:
            # Default platforms
            default_platforms = [SupportedPlatform.SPOTIFY, SupportedPlatform.YOUTUBE, SupportedPlatform.INSTAGRAM]
            for platform in default_platforms:
                platform_config = PlatformIntegrationConfig(
                    platform=platform,
                    integration_type=IntegrationType.API_OFFICIAL,
                    monitoring_mode=MonitoringMode.REAL_TIME_ALERTS,
                    data_scope=DataCollectionScope.ANALYTICS_DATA,
                    api_credentials={},
                    rate_limits={'requests_per_hour': 1000},
                    content_types=['default'],
                    filtering_rules={},
                    compliance_settings={'gdpr': True}
                )
                platforms.append(platform_config)
        
        # Create deployment config
        deployment_config = PlatformDeploymentConfig(
            platforms=platforms,
            global_settings={'concurrent_workers': 10, 'retry_attempts': 3},
            monitoring_config={'health_check_interval': 60},
            storage_config={'retention_days': 365},
            security_config={'api_key_rotation_days': 90},
            scaling_config={'replicas': 2, 'min_replicas': 1, 'max_replicas': 10}
        )
        
        deployment_id = manager.deploy_platform_integrations(deployment_config)
        print(f"Platform integration system deployed: {deployment_id}")
    
    elif args.status:
        status = manager.get_platform_integration_status()
        print(json.dumps(status, indent=2, default=str))


if __name__ == "__main__":
    main()
