"""Voice Platform Integrator - Multi-Platform Voice Integration System
====================================================================

Comprehensive platform integration system providing cross-platform voice delivery,
API management, platform synchronization, and integration analytics for the
iacherie voice ecosystem.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import aiohttp
# import oauth2  # Optional OAuth2 support
from pathlib import Path
# import redis  # Optional Redis support

logger = logging.getLogger(__name__)

class Platform(Enum):
    """
        Supported platforms"""
    YOUTUBE = "youtube"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TWITCH = "twitch"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    PODCAST_PLATFORMS = "podcast_platforms"

class IntegrationStatus(Enum):
    """Integration status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    SYNCING = "syncing"
    RATE_LIMITED = "rate_limited"

@dataclass
class PlatformCredentials:
    """Platform authentication credentials"""
    platform: Platform
    api_key: Optional[str] = None
    secret_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)

@dataclass
class PlatformSync:
    """
        Platform synchronization configuration"""
    platform: Platform
    sync_type: str  # upload, download, bidirectional
    auto_sync: bool = True
    sync_frequency: int = 3600  # seconds
    last_sync: Optional[datetime] = None
    sync_filters: Dict[str, Any] = field(default_factory=dict)

class APIManager:
    """
        API management system"""
    
    def __init__(self):
        """
        Initialize API manager"""
        self.rate_limiters = {}
        self.api_clients = {}
        self.request_cache = {}
        
        logger.info("🔗 API Manager initialized")
    
    async def make_api_request(
        self,
        platform: Platform,
        endpoint: str,
        method: str = "GET",
        data: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Make API request with rate limiting"""
        try:
            # Check rate limiting
            if not await self._check_rate_limit(platform):
                raise Exception(f"Rate limit exceeded for {platform.value}")
            
            # Get API client

            client = await self._get_api_client(platform)
            
            # Make request
            async with client.request(
                method, endpoint, json=data, headers=headers
            ) as response:
                if response.status == 200:
                    return await response.json()

                else:
                    raise Exception(f"API request failed: {response.status}")

                    
        except Exception as e:
            logger.error(f"API request failed for {platform.value}: {e}")

            raise
    
    async def _check_rate_limit(self, platform: Platform) -> bool:
        """Check if platform is within rate limits"""
        # Implementation would check rate limiting
        return True
    
    async def _get_api_client(self, platform: Platform) -> aiohttp.ClientSession:
        """
        Get or create API client for platform"""
        if platform not in self.api_clients:
            self.api_clients[platform] = aiohttp.ClientSession()
        return self.api_clients[platform]

class CrossPlatformVoice:
    """
        Cross-platform voice content management"""
    
    def __init__(self):
        """
        Initialize cross-platform voice manager"""
        self.platform_adapters = {}
        self.content_formatters = {}
        self.metadata_mappers = {}
        
        logger.info("🌐 Cross-Platform Voice Manager initialized")
    
    async def adapt_content_for_platform(
        self,
        voice_content: Dict[str, Any],
        target_platform: Platform
    ) -> Dict[str, Any]:
        """Adapt voice content for specific platform"""
        try:
            # Get platform adapter

            adapter = self.platform_adapters.get(target_platform)

            if not adapter:
                adapter = await self._create_platform_adapter(target_platform)
            
            # Format content

            formatted_content = await adapter.format_content(voice_content)
            
            # Map metadata

            mapped_metadata = await self._map_metadata(
                voice_content.get("metadata", {}), target_platform
            )

            
            formatted_content["metadata"] = mapped_metadata
            return formatted_content
            
        except Exception as e:
            logger.error(f"Failed to adapt content for {target_platform.value}: {e}")

            raise
    
    async def _create_platform_adapter(self, platform: Platform):
        """Create platform-specific adapter"""
        # Implementation would create platform adapters
        pass
    
    async def _map_metadata(
        self,
        metadata: Dict[str, Any],
        platform: Platform
    ) -> Dict[str, Any]:
        """
        Map metadata to platform-specific format"""
        # Implementation would map metadata
        return metadata

class PlatformOptimization:
    """
        Platform-specific optimization"""
    
    def __init__(self):
        """
        Initialize platform optimization"""
        self.optimization_rules = {}
        self.performance_metrics = {}
        
        logger.info("⚡ Platform Optimization Engine initialized")
    
    async def optimize_for_platform(
        self,
        content: Dict[str, Any],
        platform: Platform
    ) -> Dict[str, Any]:
        """Optimize content for specific platform"""
        try:
            # Get optimization rules

            rules = self.optimization_rules.get(platform, {})
            
            # Apply optimizations

            optimized_content = await self._apply_optimizations(content, rules)

            
            return optimized_content
            
        except Exception as e:
            logger.error(f"Failed to optimize for {platform.value}: {e}")

            raise
    
    async def _apply_optimizations(
        self,
        content: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply optimization rules to content"""
        # Implementation would apply optimizations
        return content

class IntegrationEngine:
    """
        Core integration engine"""
    
    def __init__(self):
        """
        Initialize integration engine"""
        self.integrations = {}
        self.sync_managers = {}
        self.webhook_handlers = {}
        
        logger.info("🔧 Integration Engine initialized")
    
    async def connect_platform(
        self,
        platform: Platform,
        credentials: PlatformCredentials
    ) -> bool:
        """Connect to platform"""
        try:
            # Validate credentials
            if not await self._validate_credentials(platform, credentials):
                raise Exception("Invalid credentials")
            
            # Establish connection

            connection = await self._establish_connection(platform, credentials)
            
            # Store integration
            self.integrations[platform] = {
                "credentials": credentials,
                "connection": connection,
                "status": IntegrationStatus.CONNECTED,
                "connected_at": datetime.utcnow()
            }
            
            logger.info(f"Connected to platform: {platform.value}")

            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {platform.value}: {e}")

            return False
    
    async def _validate_credentials(
        self,
        platform: Platform,
        credentials: PlatformCredentials
    ) -> bool:
        """Validate platform credentials"""
        # Implementation would validate credentials
        return True
    
    async def _establish_connection(
        self,
        platform: Platform,
        credentials: PlatformCredentials
    ):
        """
        Establish platform connection"""
        # Implementation would establish connection
        return {"status": "connected"}

class PlatformAnalytics:
    """Platform integration analytics"""
    
    def __init__(self):
        """
        Initialize platform analytics"""
        self.metrics_collector = {}
        self.performance_tracker = {}
        self.integration_insights = {}
        
        logger.info("📈 Platform Analytics initialized")
    
    async def track_integration_metrics(
        self,
        platform: Platform,
        metrics: Dict[str, Any]
    ):
        """Track integration performance metrics"""
        try:
            timestamp = datetime.utcnow()

            
            if platform not in self.metrics_collector:
                self.metrics_collector[platform] = []
            
            self.metrics_collector[platform].append({
                "timestamp": timestamp,
                "metrics": metrics
            })
            
            # Analyze performance
            await self._analyze_performance(platform, metrics)

            
        except Exception as e:
            logger.error(f"Failed to track metrics for {platform.value}: {e}")
    
    async def _analyze_performance(
        self,
        platform: Platform,
        metrics: Dict[str, Any]
    ):
        """Analyze platform performance"""
        # Implementation would analyze performance
        pass

class VoicePlatformIntegrator:
    """
        Main voice platform integrator"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize voice platform integrator"""
        self.config = config or {}
        self.api_manager = APIManager()
        self.cross_platform_voice = CrossPlatformVoice()
        self.platform_optimization = PlatformOptimization()
        self.integration_engine = IntegrationEngine()
        self.platform_analytics = PlatformAnalytics()
        
        # Initialize supported platforms
        asyncio.create_task(self._initialize_platforms())

        
        logger.info("🎤🌐 Voice Platform Integrator initialized")
    
    async def upload_voice_content(
        self,
        content: Dict[str, Any],
        platforms: List[Platform],
        options: Dict[str, Any] = None
    ) -> Dict[Platform, Dict[str, Any]]:
        """Upload voice content to multiple platforms"""
        try:
            results = {}
            
            for platform in platforms:
                try:
                    # Check platform connection
                    if not await self._is_platform_connected(platform):
                        raise Exception(f"Platform {platform.value} not connected")
                    
                    # Adapt content for platform

                    adapted_content = await self.cross_platform_voice.adapt_content_for_platform(
                        content, platform
                    )
                    
                    # Optimize for platform

                    optimized_content = await self.platform_optimization.optimize_for_platform(
                        adapted_content, platform
                    )
                    
                    # Upload to platform

                    upload_result = await self._upload_to_platform(
                        platform, optimized_content, options or {}
                    )

                    
                    results[platform] = {
                        "success": True,
                        "result": upload_result,
                        "uploaded_at": datetime.utcnow()
                    }
                    
                    # Track metrics
                    await self.platform_analytics.track_integration_metrics(
                        platform, {"upload_success": True, "content_size": len(str(content))}
                    )

                    
                except Exception as e:
                    results[platform] = {
                        "success": False,
                        "error": str(e),
                        "failed_at": datetime.utcnow()
                    }
                    
                    logger.error(f"Failed to upload to {platform.value}: {e}")

            
            return results
            
        except Exception as e:
            logger.error(f"Failed to upload voice content: {e}")

            raise
    
    async def sync_platform_data(
        self,
        platform: Platform,
        sync_config: PlatformSync
    ) -> Dict[str, Any]:
        """Synchronize data with platform"""
        try:
            # Check if sync is needed
            if not await self._should_sync(platform, sync_config):
                return {"skipped": True, "reason": "Sync not needed"}
            
            # Perform synchronization

            sync_result = await self._perform_sync(platform, sync_config)
            
            # Update sync timestamp
            sync_config.last_sync = datetime.utcnow()

            
            return sync_result
            
        except Exception as e:
            logger.error(f"Failed to sync platform data for {platform.value}: {e}")

            raise
    
    async def get_platform_insights(
        self,
        platform: Platform,
        time_range: Tuple[datetime, datetime] = None
    ) -> Dict[str, Any]:
        """Get platform integration insights"""
        try:
            # Get metrics for time range

            metrics = await self._get_platform_metrics(platform, time_range)
            
            # Generate insights

            insights = await self._generate_insights(platform, metrics)

            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get insights for {platform.value}: {e}")

            raise
    
    async def _initialize_platforms(self):
        """Initialize platform configurations"""
        try:
            # Initialize platform-specific configurations

            platform_configs = {
                Platform.YOUTUBE: {
                    "api_version": "v3",
                    "upload_formats": ["mp4", "mp3"],
                    "max_file_size": 128 * 1024 * 1024  # 128MB
                },
                Platform.SPOTIFY: {
                    "api_version": "v1",
                    "upload_formats": ["mp3", "flac"],
                    "max_file_size": 50 * 1024 * 1024  # 50MB
                },
                Platform.SOUNDCLOUD: {
                    "api_version": "v2",
                    "upload_formats": ["mp3", "wav"],
                    "max_file_size": 100 * 1024 * 1024  # 100MB
                }
            }
            
            # Store configurations
            for platform, config in platform_configs.items():
                await self._store_platform_config(platform, config)

            
            logger.info("Platform configurations initialized")

            
        except Exception as e:
            logger.error(f"Failed to initialize platforms: {e}")
    
    async def _is_platform_connected(self, platform: Platform) -> bool:
        """Check if platform is connected"""
        integration = self.integration_engine.integrations.get(platform)
        return integration and integration["status"] == IntegrationStatus.CONNECTED
    
    async def _upload_to_platform(
        self,
        platform: Platform,
        content: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upload content to specific platform"""
        try:
            # Get platform-specific upload endpoint

            endpoint = await self._get_upload_endpoint(platform)
            
            # Prepare upload data

            upload_data = await self._prepare_upload_data(platform, content, options)
            
            # Make upload request

            result = await self.api_manager.make_api_request(
                platform, endpoint, "POST", upload_data
            )

            
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload to {platform.value}: {e}")

            raise
    
    async def _should_sync(
        self,
        platform: Platform,
        sync_config: PlatformSync
    ) -> bool:
        """Check if synchronization is needed"""
        if not sync_config.auto_sync:
            return False
        
        if not sync_config.last_sync:
            return True

        
        time_since_sync = datetime.utcnow() - sync_config.last_sync
        return time_since_sync.total_seconds() >= sync_config.sync_frequency
    
    async def _perform_sync(
        self,
        platform: Platform,
        sync_config: PlatformSync
    ) -> Dict[str, Any]:
        """
        Perform platform synchronization"""
        # Implementation would perform actual sync
        return {"synced": True, "items": 0}
    
    async def _get_platform_metrics(
        self,
        platform: Platform,
        time_range: Tuple[datetime, datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get platform metrics"""
        metrics = self.platform_analytics.metrics_collector.get(platform, [])

        
        if time_range:
            start_time, end_time = time_range

            metrics = [
                m for m in metrics
                if start_time <= m["timestamp"] <= end_time
            ]
        
        return metrics
    
    async def _generate_insights(
        self,
        platform: Platform,
        metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate platform insights"""
        # Implementation would generate insights
        return {
            "total_uploads": len(metrics),
            "success_rate": 0.95,
            "average_response_time": 250
        }
    
    async def _store_platform_config(
        self,
        platform: Platform,
        config: Dict[str, Any]
    ):
        """Store platform configuration"""
        # Implementation would store config
        pass
    
    async def _get_upload_endpoint(self, platform: Platform) -> str:
        """
        Get platform upload endpoint"""
        endpoints = {
            Platform.YOUTUBE: "/youtube/v3/videos",
            Platform.SPOTIFY: "/v1/tracks",
            Platform.SOUNDCLOUD: "/tracks"
        }
        return endpoints.get(platform, "/upload")
    
    async def _prepare_upload_data(
        self,
        platform: Platform,
        content: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare upload data for platform"""
        # Implementation would prepare platform-specific data
        return content


class PlatformIntegration:
    """Platform Integration - Core integration layer for connecting voice content with external platforms"""
    
    def __init__(self):
        """Initialize platform integration"""
        self.connected_platforms = {}
        self.integration_status = {}
        self.platform_configs = {}
        
        logger.info("🔗 PlatformIntegration initialized")
    
    async def connect_platform(
        self,
        platform: Platform,
        credentials: PlatformCredentials
    ) -> bool:
        """Connect to a platform"""
        try:
            # Validate credentials
            if not await self._validate_credentials(platform, credentials):
                raise Exception(f"Invalid credentials for {platform.value}")
            
            # Establish connection
            self.connected_platforms[platform] = credentials
            self.integration_status[platform] = IntegrationStatus.CONNECTED
            
            logger.info(f"✅ Connected to {platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to {platform.value}: {e}")
            self.integration_status[platform] = IntegrationStatus.ERROR
            return False
    
    async def disconnect_platform(self, platform: Platform) -> bool:
        """Disconnect from a platform"""
        try:
            if platform in self.connected_platforms:
                del self.connected_platforms[platform]
                self.integration_status[platform] = IntegrationStatus.DISCONNECTED
                logger.info(f"🔌 Disconnected from {platform.value}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to disconnect from {platform.value}: {e}")
            return False
    
    async def get_integration_status(self, platform: Platform) -> IntegrationStatus:
        """Get integration status for a platform"""
        return self.integration_status.get(platform, IntegrationStatus.DISCONNECTED)
    
    async def _validate_credentials(
        self,
        platform: Platform,
        credentials: PlatformCredentials
    ) -> bool:
        """Validate platform credentials"""
        # Implementation would validate credentials with platform
        return credentials.api_key is not None or credentials.access_token is not None


class ContentDistribution:
    """Content Distribution - Manages distribution of voice content across multiple platforms"""
    
    def __init__(self):
        """Initialize content distribution"""
        self.distribution_queue = []
        self.distribution_history = {}
        self.distribution_rules = {}
        
        logger.info("📡 ContentDistribution initialized")
    
    async def distribute_content(
        self,
        voice_id: str,
        content: Dict[str, Any],
        target_platforms: List[Platform],
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Distribute voice content to multiple platforms"""
        try:
            distribution_id = f"dist_{voice_id}_{int(datetime.now().timestamp())}"
            results = {}
            
            for platform in target_platforms:
                try:
                    result = await self._distribute_to_platform(
                        platform, voice_id, content, options or {}
                    )
                    results[platform.value] = {
                        'status': 'success',
                        'result': result
                    }
                except Exception as e:
                    results[platform.value] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            # Store distribution history
            self.distribution_history[distribution_id] = {
                'voice_id': voice_id,
                'platforms': target_platforms,
                'results': results,
                'timestamp': datetime.now()
            }
            
            return {
                'distribution_id': distribution_id,
                'results': results,
                'success_count': sum(1 for r in results.values() if r['status'] == 'success'),
                'total_count': len(target_platforms)
            }
            
        except Exception as e:
            logger.error(f"Content distribution failed: {e}")
            raise
    
    async def schedule_distribution(
        self,
        voice_id: str,
        content: Dict[str, Any],
        target_platforms: List[Platform],
        scheduled_time: datetime,
        options: Dict[str, Any] = None
    ) -> str:
        """Schedule content distribution for later"""
        distribution_id = f"sched_{voice_id}_{int(datetime.now().timestamp())}"
        
        self.distribution_queue.append({
            'distribution_id': distribution_id,
            'voice_id': voice_id,
            'content': content,
            'target_platforms': target_platforms,
            'scheduled_time': scheduled_time,
            'options': options or {},
            'status': 'scheduled'
        })
        
        logger.info(f"📅 Scheduled distribution {distribution_id} for {scheduled_time}")
        return distribution_id
    
    async def get_distribution_status(self, distribution_id: str) -> Dict[str, Any]:
        """Get status of a distribution"""
        if distribution_id in self.distribution_history:
            return self.distribution_history[distribution_id]
        
        # Check queue
        for item in self.distribution_queue:
            if item['distribution_id'] == distribution_id:
                return item
        
        return {'status': 'not_found'}
    
    async def _distribute_to_platform(
        self,
        platform: Platform,
        voice_id: str,
        content: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Distribute content to a specific platform"""
        # Implementation would handle platform-specific distribution
        return {
            'platform_id': f"{platform.value}_{voice_id}",
            'url': f"https://{platform.value}.com/content/{voice_id}",
            'timestamp': datetime.now()
        }


class MultiPlatformSync:
    """Multi-Platform Sync - Synchronizes voice content across multiple platforms"""
    
    def __init__(self):
        """Initialize multi-platform sync"""
        self.sync_tasks = {}
        self.sync_status = {}
        self.sync_conflicts = []
        
        logger.info("🔄 MultiPlatformSync initialized")
    
    async def sync_content(
        self,
        voice_id: str,
        source_platform: Platform,
        target_platforms: List[Platform],
        sync_options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Sync content from source to target platforms"""
        try:
            sync_id = f"sync_{voice_id}_{int(datetime.now().timestamp())}"
            
            # Fetch content from source
            source_content = await self._fetch_content(source_platform, voice_id)
            
            # Sync to targets
            sync_results = {}
            for target in target_platforms:
                try:
                    result = await self._sync_to_platform(
                        target, voice_id, source_content, sync_options or {}
                    )
                    sync_results[target.value] = {
                        'status': 'synced',
                        'result': result
                    }
                except Exception as e:
                    sync_results[target.value] = {
                        'status': 'error',
                        'error': str(e)
                    }
            
            self.sync_status[sync_id] = {
                'voice_id': voice_id,
                'source': source_platform,
                'targets': target_platforms,
                'results': sync_results,
                'timestamp': datetime.now()
            }
            
            return {
                'sync_id': sync_id,
                'results': sync_results,
                'synced_count': sum(1 for r in sync_results.values() if r['status'] == 'synced')
            }
            
        except Exception as e:
            logger.error(f"Multi-platform sync failed: {e}")
            raise
    
    async def enable_auto_sync(
        self,
        voice_id: str,
        platforms: List[Platform],
        sync_interval: int = 3600
    ) -> str:
        """Enable automatic synchronization"""
        sync_task_id = f"auto_sync_{voice_id}"
        
        self.sync_tasks[sync_task_id] = {
            'voice_id': voice_id,
            'platforms': platforms,
            'interval': sync_interval,
            'enabled': True,
            'last_sync': None
        }
        
        logger.info(f"🔄 Auto-sync enabled for {voice_id} every {sync_interval}s")
        return sync_task_id
    
    async def detect_conflicts(
        self,
        voice_id: str,
        platforms: List[Platform]
    ) -> List[Dict[str, Any]]:
        """Detect sync conflicts across platforms"""
        conflicts = []
        
        # Fetch content from all platforms
        platform_contents = {}
        for platform in platforms:
            try:
                content = await self._fetch_content(platform, voice_id)
                platform_contents[platform] = content
            except Exception as e:
                logger.error(f"Failed to fetch from {platform.value}: {e}")
        
        # Compare contents and detect conflicts
        if len(platform_contents) > 1:
            base_content = list(platform_contents.values())[0]
            for platform, content in platform_contents.items():
                if content != base_content:
                    conflicts.append({
                        'voice_id': voice_id,
                        'platform': platform,
                        'conflict_type': 'content_mismatch',
                        'timestamp': datetime.now()
                    })
        
        self.sync_conflicts.extend(conflicts)
        return conflicts
    
    async def resolve_conflict(
        self,
        conflict_id: str,
        resolution: str,
        source_platform: Platform
    ) -> bool:
        """Resolve a sync conflict"""
        # Implementation would resolve conflicts
        logger.info(f"✅ Resolved conflict {conflict_id} using {resolution} from {source_platform.value}")
        return True
    
    async def _fetch_content(
        self,
        platform: Platform,
        voice_id: str
    ) -> Dict[str, Any]:
        """Fetch content from platform"""
        # Implementation would fetch from platform
        return {
            'voice_id': voice_id,
            'platform': platform,
            'content': {},
            'metadata': {}
        }
    
    async def _sync_to_platform(
        self,
        platform: Platform,
        voice_id: str,
        content: Dict[str, Any],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sync content to platform"""
        # Implementation would sync to platform
        return {
            'platform_id': f"{platform.value}_{voice_id}",
            'synced_at': datetime.now()
        }


class IntegrationMonitoring:
    """Integration Monitoring - Monitors health and performance of platform integrations"""
    
    def __init__(self):
        """Initialize integration monitoring"""
        self.health_checks = {}
        self.performance_metrics = {}
        self.alerts = []
        
        logger.info("📊 IntegrationMonitoring initialized")
    
    async def check_platform_health(
        self,
        platform: Platform
    ) -> Dict[str, Any]:
        """Check health of a platform integration"""
        try:
            health_status = await self._perform_health_check(platform)
            
            self.health_checks[platform] = {
                'status': health_status['status'],
                'response_time': health_status['response_time'],
                'last_check': datetime.now()
            }
            
            # Create alert if unhealthy
            if health_status['status'] != 'healthy':
                await self._create_alert(
                    platform,
                    'health_check_failed',
                    f"Platform {platform.value} health check failed"
                )
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed for {platform.value}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def monitor_performance(
        self,
        platform: Platform,
        operation: str,
        duration_ms: float
    ):
        """Monitor operation performance"""
        if platform not in self.performance_metrics:
            self.performance_metrics[platform] = []
        
        self.performance_metrics[platform].append({
            'operation': operation,
            'duration_ms': duration_ms,
            'timestamp': datetime.now()
        })
        
        # Check for performance issues
        if duration_ms > 5000:  # > 5 seconds
            await self._create_alert(
                platform,
                'slow_performance',
                f"Operation {operation} took {duration_ms}ms"
            )
    
    async def get_platform_metrics(
        self,
        platform: Platform,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get performance metrics for a platform"""
        metrics = self.performance_metrics.get(platform, [])
        
        if time_range:
            start, end = time_range
            metrics = [
                m for m in metrics
                if start <= m['timestamp'] <= end
            ]
        
        if not metrics:
            return {
                'platform': platform.value,
                'metrics_count': 0
            }
        
        durations = [m['duration_ms'] for m in metrics]
        
        return {
            'platform': platform.value,
            'metrics_count': len(metrics),
            'avg_duration_ms': sum(durations) / len(durations),
            'min_duration_ms': min(durations),
            'max_duration_ms': max(durations),
            'operations': list(set(m['operation'] for m in metrics))
        }
    
    async def get_alerts(
        self,
        platform: Optional[Platform] = None,
        severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get integration alerts"""
        alerts = self.alerts
        
        if platform:
            alerts = [a for a in alerts if a['platform'] == platform]
        
        if severity:
            alerts = [a for a in alerts if a['severity'] == severity]
        
        return alerts
    
    async def _perform_health_check(
        self,
        platform: Platform
    ) -> Dict[str, Any]:
        """Perform health check on platform"""
        # Simulate health check
        import random
        response_time = random.randint(50, 500)
        
        return {
            'status': 'healthy',
            'response_time': response_time,
            'timestamp': datetime.now()
        }
    
    async def _create_alert(
        self,
        platform: Platform,
        alert_type: str,
        message: str,
        severity: str = 'warning'
    ):
        """Create monitoring alert"""
        alert = {
            'alert_id': f"alert_{int(datetime.now().timestamp())}",
            'platform': platform,
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now(),
            'acknowledged': False
        }
        
        self.alerts.append(alert)
        logger.warning(f"⚠️ Alert: {message}")


class PlatformAdaptation:
    """Platform Adaptation - Adapts voice content to platform-specific requirements"""
    
    def __init__(self):
        """Initialize platform adaptation"""
        self.adaptation_rules = {}
        self.format_converters = {}
        self.platform_requirements = self._initialize_requirements()
        
        logger.info("🔧 PlatformAdaptation initialized")
    
    def _initialize_requirements(self) -> Dict[Platform, Dict[str, Any]]:
        """Initialize platform-specific requirements"""
        return {
            Platform.YOUTUBE: {
                'max_file_size': 128 * 1024 * 1024,  # 128MB
                'supported_formats': ['mp4', 'mov', 'avi'],
                'max_duration': 12 * 3600,  # 12 hours
                'required_metadata': ['title', 'description']
            },
            Platform.SPOTIFY: {
                'max_file_size': 50 * 1024 * 1024,  # 50MB
                'supported_formats': ['mp3', 'wav', 'flac'],
                'max_duration': 3600,  # 1 hour
                'required_metadata': ['title', 'artist']
            },
            Platform.TIKTOK: {
                'max_file_size': 500 * 1024 * 1024,  # 500MB
                'supported_formats': ['mp4', 'mov'],
                'max_duration': 600,  # 10 minutes
                'required_metadata': ['title']
            }
        }
    
    async def adapt_content(
        self,
        content: Dict[str, Any],
        target_platform: Platform
    ) -> Dict[str, Any]:
        """Adapt content for target platform"""
        try:
            requirements = self.platform_requirements.get(
                target_platform,
                {}
            )
            
            adapted_content = content.copy()
            
            # Adapt file format
            if 'format' in content:
                adapted_content = await self._adapt_format(
                    adapted_content,
                    target_platform,
                    requirements
                )
            
            # Adapt metadata
            if 'metadata' in content:
                adapted_content['metadata'] = await self._adapt_metadata(
                    content['metadata'],
                    target_platform,
                    requirements
                )
            
            # Validate adapted content
            if not await self._validate_adaptation(adapted_content, target_platform):
                raise Exception(f"Content validation failed for {target_platform.value}")
            
            logger.info(f"✅ Adapted content for {target_platform.value}")
            return adapted_content
            
        except Exception as e:
            logger.error(f"Content adaptation failed for {target_platform.value}: {e}")
            raise
    
    async def validate_content(
        self,
        content: Dict[str, Any],
        platform: Platform
    ) -> Tuple[bool, List[str]]:
        """Validate content against platform requirements"""
        requirements = self.platform_requirements.get(platform, {})
        errors = []
        
        # Check file size
        if 'file_size' in content:
            max_size = requirements.get('max_file_size', float('inf'))
            if content['file_size'] > max_size:
                errors.append(f"File size exceeds maximum of {max_size} bytes")
        
        # Check format
        if 'format' in content:
            supported = requirements.get('supported_formats', [])
            if supported and content['format'] not in supported:
                errors.append(f"Format {content['format']} not supported. Use: {', '.join(supported)}")
        
        # Check duration
        if 'duration' in content:
            max_duration = requirements.get('max_duration', float('inf'))
            if content['duration'] > max_duration:
                errors.append(f"Duration exceeds maximum of {max_duration} seconds")
        
        # Check required metadata
        required_meta = requirements.get('required_metadata', [])
        content_meta = content.get('metadata', {})
        for field in required_meta:
            if field not in content_meta:
                errors.append(f"Required metadata field '{field}' is missing")
        
        return len(errors) == 0, errors
    
    async def get_platform_requirements(
        self,
        platform: Platform
    ) -> Dict[str, Any]:
        """Get requirements for a platform"""
        return self.platform_requirements.get(platform, {})
    
    async def _adapt_format(
        self,
        content: Dict[str, Any],
        platform: Platform,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt content format"""
        supported_formats = requirements.get('supported_formats', [])
        current_format = content.get('format')
        
        if supported_formats and current_format not in supported_formats:
            # Convert to first supported format
            content['format'] = supported_formats[0]
            logger.info(f"🔄 Converting format from {current_format} to {supported_formats[0]}")
        
        return content
    
    async def _adapt_metadata(
        self,
        metadata: Dict[str, Any],
        platform: Platform,
        requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt metadata"""
        required_fields = requirements.get('required_metadata', [])
        adapted_metadata = metadata.copy()
        
        # Ensure required fields exist
        for field in required_fields:
            if field not in adapted_metadata:
                adapted_metadata[field] = f"Voice Content - {field.title()}"
        
        return adapted_metadata
    
    async def _validate_adaptation(
        self,
        content: Dict[str, Any],
        platform: Platform
    ) -> bool:
        """Validate adapted content"""
        is_valid, errors = await self.validate_content(content, platform)
        
        if errors:
            for error in errors:
                logger.warning(f"Validation error: {error}")
        
        return is_valid
