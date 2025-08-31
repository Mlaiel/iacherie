"""Integrations Package - Advanced Multi-Platform Integration Hub
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or use of this code without explicit written permission from 
Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in 
legal action.

Team Specialties: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

This comprehensive package provides enterprise-grade integration capabilities for:
- Social Media Platforms (YouTube, Instagram, Spotify, etc.)
- External APIs and Services (Streaming, Payment, Analytics)
- Content Distribution Networks (Multi-platform delivery)
- Analytics Integration (Google Analytics, Mixpanel, etc.)
- Cloud Services (AWS, Azure, GCP multi-cloud orchestration)

Following the core business logic:
User (Musician/Blogger/Photographer/Influencer/Comedian) → 
Upload Multi-format Content → 
IA Protection & Rights Management → 
SEO Optimization → 
Collaboration Matching → 
Multi-Platform Distribution
"""
import logging
from typing import Dict, List, Any, Optional

# Import all integration modules
from .social_platforms import (
    SocialPlatformManager,
    BasePlatformConnector,
    YouTubeConnector,
    InstagramConnector,
    TwitterConnector,
    LinkedInConnector,
    PlatformCredentials,
    ContentPost,
    PostResult,
    PlatformType,
    PlatformStatus,
    PostStatus
)

from .api_connectors import (
    APIConnectorManager,
    BaseAPIConnector,
    StreamingPlatformConnector,
    PaymentGatewayConnector,
    APICredentials,
    APIRequestConfig,
    APIResponse,
    APIProvider,
    APIConnectionStatus,
    APIAuthType,
    APIConnectorError,
    RateLimiter
)

from .content_distribution import (
    ContentDistributionNetwork,
    ContentOptimizer,
    BasePlatformDistributor,
    YouTubeDistributor,
    SpotifyDistributor,
    ContentAsset,
    ContentMetadata,
    DistributionJob,
    DistributionResult,
    ContentType,
    DistributionPlatform,
    ContentStatus,
    OptimizationLevel,
    PlatformRequirements
)

from .analytics_hub import (
    AnalyticsHub,
    BaseAnalyticsConnector,
    GoogleAnalyticsConnector,
    SpotifyAnalyticsConnector,
    YouTubeAnalyticsConnector,
    TrendAnalyzer,
    InsightGenerator,
    MetricDefinition,
    DataPoint,
    MetricSeries,
    AnalyticsReport,
    AnalyticsProvider,
    MetricType,
    TimeGranularity,
    AggregationType
)

from .cloud_services import (
    CloudOrchestrator,
    BaseCloudConnector,
    AWSConnector,
    AzureConnector,
    GCPConnector,
    CloudCostTracker,
    CloudCredentials,
    CloudResource,
    StorageObject,
    CloudProvider,
    ResourceType,
    ResourceStatus
)

logger = logging.getLogger(__name__)

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel <mlaiel@live.de>"

class IntegrationOrchestrator:
    """    Master orchestrator for all integration services
    
    This class provides a unified interface for managing all external integrations
    including social platforms, APIs, content distribution, analytics, and cloud services.
    """    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize all integration managers
        self.social_manager = SocialPlatformManager()
        self.api_manager = APIConnectorManager()
        self.content_distribution = ContentDistributionNetwork()
        self.analytics_hub = AnalyticsHub()
        self.cloud_orchestrator = CloudOrchestrator()
        
        self.logger.info("Integration orchestrator initialized with all services")
    
    async def initialize_all_services(self) -> Dict[str, bool]:
        """Initialize all integration services"""        results = {}
        
        try:
            # Start content distribution workers
            await self.content_distribution.start_workers()
            results['content_distribution'] = True
            
            # Authenticate analytics hub
            analytics_auth = await self.analytics_hub.authenticate_all()
            results['analytics_hub'] = any(analytics_auth.values()) if analytics_auth else True
            
            # Cloud services are initialized per-provider
            results['cloud_services'] = True
            
            # Social platforms and API connectors are added per-platform
            results['social_platforms'] = True
            results['api_connectors'] = True
            
            self.logger.info("All integration services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize integration services: {e}")
            results['error'] = str(e)
        
        return results
    
    async def add_platform_integration(self, platform_type: str, 
                                     credentials: Dict[str, Any]) -> bool:
        """Add a new platform integration"""        try:
            success = False
            
            # Add to appropriate manager based on platform type
            if platform_type in ['youtube', 'instagram', 'facebook', 'twitter', 'linkedin']:
                platform_creds = PlatformCredentials(
                    platform=PlatformType(platform_type.upper()),
                    access_token=credentials.get('access_token'),
                    refresh_token=credentials.get('refresh_token'),
                    client_id=credentials.get('client_id'),
                    client_secret=credentials.get('client_secret')
                )
                success = self.social_manager.add_platform(platform_creds)
                
                if success:
                    # Also add to content distribution
                    dist_platform = DistributionPlatform(platform_type.upper())
                    # Content distribution platforms are initialized automatically
            
            elif platform_type in ['spotify', 'apple_music', 'soundcloud']:
                api_creds = APICredentials(
                    provider=APIProvider(platform_type.upper()),
                    auth_type=APIAuthType.OAUTH2,
                    access_token=credentials.get('access_token'),
                    refresh_token=credentials.get('refresh_token'),
                    client_id=credentials.get('client_id'),
                    client_secret=credentials.get('client_secret')
                )
                success = await self.api_manager.add_connector(api_creds)
            
            elif platform_type in ['google_analytics', 'mixpanel', 'amplitude']:
                analytics_provider = AnalyticsProvider(platform_type.upper())
                success = await self.analytics_hub.add_connector(analytics_provider, credentials)
            
            elif platform_type in ['aws', 'azure', 'gcp']:
                cloud_creds = CloudCredentials(
                    provider=CloudProvider(platform_type.upper()),
                    access_key_id=credentials.get('access_key_id'),
                    secret_access_key=credentials.get('secret_access_key'),
                    region=credentials.get('region', 'us-east-1'),
                    client_id=credentials.get('client_id'),
                    client_secret=credentials.get('client_secret'),
                    project_id=credentials.get('project_id')
                )
                success = await self.cloud_orchestrator.add_provider(
                    CloudProvider(platform_type.upper()), cloud_creds
                )
            
            if success:
                self.logger.info(f"Successfully added {platform_type} integration")
            else:
                self.logger.error(f"Failed to add {platform_type} integration")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error adding platform integration {platform_type}: {e}")
            return False
    
    async def distribute_content_everywhere(self, content_data: Dict[str, Any], 
                                          target_platforms: List[str]) -> Dict[str, Any]:
        """Distribute content across all specified platforms"""        try:
            # Create content asset
            metadata = ContentMetadata(
                title=content_data['title'],
                description=content_data.get('description', ''),
                tags=content_data.get('tags', []),
                content_type=ContentType(content_data.get('content_type', 'audio'))
            )
            
            asset = self.content_distribution.create_asset(
                file_path=content_data['file_path'],
                metadata=metadata
            )
            
            # Convert platform names to enums
            distribution_platforms = []
            for platform_name in target_platforms:
                try:
                    platform = DistributionPlatform(platform_name.upper())
                    distribution_platforms.append(platform)
                except ValueError:
                    self.logger.warning(f"Unknown distribution platform: {platform_name}")
            
            # Submit distribution job
            job_id = await self.content_distribution.submit_distribution_job(
                asset=asset,
                target_platforms=distribution_platforms,
                optimization_level=OptimizationLevel(content_data.get('optimization', 'standard')),
                priority=content_data.get('priority', 5)
            )
            
            return {
                'success': True,
                'job_id': job_id,
                'platforms': target_platforms,
                'asset_id': asset.asset_id
            }
            
        except Exception as e:
            self.logger.error(f"Content distribution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_unified_analytics(self, date_range: tuple, 
                                  metrics: List[str]) -> Dict[str, Any]:
        """Get unified analytics across all platforms"""        try:
            # Get analytics from all connected providers
            providers = list(self.analytics_hub.connectors.keys())
            
            if not providers:
                return {'error': 'No analytics providers configured'}
            
            start_date, end_date = date_range
            
            # Generate comprehensive report
            report = await self.analytics_hub.generate_comprehensive_report(
                providers=providers,
                metric_names=metrics,
                start_date=start_date,
                end_date=end_date,
                title="Unified Platform Analytics Report"
            )
            
            return {
                'success': True,
                'report_id': report.report_id,
                'metrics_count': len(report.metrics),
                'insights': report.insights,
                'recommendations': report.recommendations,
                'data_points': sum(len(m.data_points) for m in report.metrics)
            }
            
        except Exception as e:
            self.logger.error(f"Unified analytics failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def optimize_cloud_costs(self) -> Dict[str, Any]:
        """Optimize costs across all cloud providers"""        try:
            # Discover all resources
            await self.cloud_orchestrator.discover_all_resources()
            
            # Get optimization recommendations
            optimization_report = await self.cloud_orchestrator.optimize_costs()
            
            return {
                'success': True,
                'optimization_report': optimization_report
            }
            
        except Exception as e:
            self.logger.error(f"Cloud cost optimization failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all integrated services"""        health_status = {
            'timestamp': logger.handlers[0].format(logger.makeRecord(
                'health_check', 20, '', 0, '', (), None
            )) if logger.handlers else 'unknown',
            'services': {}
        }
        
        try:
            # Social platforms status
            social_status = self.social_manager.get_platform_status()
            health_status['services']['social_platforms'] = {
                'status': 'healthy' if social_status else 'no_platforms',
                'connected_platforms': len(social_status),
                'platform_details': {k.value: v.value for k, v in social_status.items()}
            }
            
            # API connectors status
            api_status = self.api_manager.get_all_statuses()
            health_status['services']['api_connectors'] = {
                'status': 'healthy' if api_status else 'no_connectors',
                'connected_apis': len(api_status),
                'api_details': {k.value: v.value for k, v in api_status.items()}
            }
            
            # Content distribution status
            dist_stats = self.content_distribution.get_platform_statistics()
            health_status['services']['content_distribution'] = {
                'status': 'healthy',
                'active_jobs': dist_stats.get('active_jobs', 0),
                'total_jobs': dist_stats.get('total_jobs', 0),
                'success_rate': dist_stats.get('success_rate', 0)
            }
            
            # Analytics hub status
            available_metrics = self.analytics_hub.get_available_metrics()
            health_status['services']['analytics_hub'] = {
                'status': 'healthy' if available_metrics else 'no_providers',
                'available_metrics': len(available_metrics),
                'connected_providers': len(self.analytics_hub.connectors)
            }
            
            # Cloud services status
            if self.cloud_orchestrator.connectors:
                cloud_health = await self.cloud_orchestrator.monitor_resource_health()
                health_status['services']['cloud_services'] = {
                    'status': 'healthy',
                    'connected_providers': len(self.cloud_orchestrator.connectors),
                    'resource_health': cloud_health
                }
            else:
                health_status['services']['cloud_services'] = {
                    'status': 'no_providers',
                    'connected_providers': 0
                }
            
        except Exception as e:
            health_status['error'] = str(e)
            self.logger.error(f"Health check failed: {e}")
        
        return health_status
    
    async def cleanup_all_services(self):
        """Cleanup all integration services"""        try:
            await self.content_distribution.cleanup()
            await self.analytics_hub.cleanup()
            await self.cloud_orchestrator.cleanup_all()
            await self.api_manager.cleanup()
            
            self.logger.info("All integration services cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")

# Package-level exports
__all__ = [
    # Main orchestrator
    'IntegrationOrchestrator',
    
    # Social platforms
    'SocialPlatformManager',
    'BasePlatformConnector',
    'YouTubeConnector',
    'InstagramConnector',
    'TwitterConnector',
    'LinkedInConnector',
    'PlatformCredentials',
    'ContentPost',
    'PostResult',
    'PlatformType',
    'PlatformStatus',
    'PostStatus',
    
    # API connectors
    'APIConnectorManager',
    'BaseAPIConnector',
    'StreamingPlatformConnector',
    'PaymentGatewayConnector',
    'APICredentials',
    'APIRequestConfig',
    'APIResponse',
    'APIProvider',
    'APIConnectionStatus',
    'APIAuthType',
    'APIConnectorError',
    'RateLimiter',
    
    # Content distribution
    'ContentDistributionNetwork',
    'ContentOptimizer',
    'BasePlatformDistributor',
    'YouTubeDistributor',
    'SpotifyDistributor',
    'ContentAsset',
    'ContentMetadata',
    'DistributionJob',
    'DistributionResult',
    'ContentType',
    'DistributionPlatform',
    'ContentStatus',
    'OptimizationLevel',
    'PlatformRequirements',
    
    # Analytics
    'AnalyticsHub',
    'BaseAnalyticsConnector',
    'GoogleAnalyticsConnector',
    'SpotifyAnalyticsConnector',
    'YouTubeAnalyticsConnector',
    'TrendAnalyzer',
    'InsightGenerator',
    'MetricDefinition',
    'DataPoint',
    'MetricSeries',
    'AnalyticsReport',
    'AnalyticsProvider',
    'MetricType',
    'TimeGranularity',
    'AggregationType',
    
    # Cloud services
    'CloudOrchestrator',
    'BaseCloudConnector',
    'AWSConnector',
    'AzureConnector', 
    'GCPConnector',
    'CloudCostTracker',
    'CloudCredentials',
    'CloudResource',
    'StorageObject',
    'CloudProvider',
    'ResourceType',
    'ResourceStatus'
]

logger.info(f"Advanced integrations package v{__version__} initialized successfully - {len(__all__)} exports available")
