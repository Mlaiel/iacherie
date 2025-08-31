"""
Platform Connector Module

Connection management and pooling for platform integrations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Type, Union
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
from dataclasses import dataclass
import weakref
import time
from contextlib import asynccontextmanager

from .base import PlatformBase, PlatformConfig, PlatformType, PlatformStatus
from .spotify import SpotifyPlatform
from .youtube import YouTubePlatform
from .instagram import InstagramPlatform
from .tiktok import TikTokPlatform
from .twitter import TwitterPlatform
from .facebook import FacebookPlatform
from .twitch import TwitchPlatform
from .soundcloud import SoundCloudPlatform
from .apple_music import AppleMusicPlatform
from .bandcamp import BandcampPlatform
from .reddit import RedditPlatform
from .linkedin import LinkedInPlatform
from .pinterest import PinterestPlatform
from .snapchat import SnapchatPlatform
from .discord import DiscordPlatform
from .telegram import TelegramPlatform

logger = logging.getLogger(__name__)


class ConnectionState(Enum):
    """Connection state enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


@dataclass
class ConnectionMetrics:
    """Connection performance metrics"""
    platform_id: str
    connection_time: float
    last_activity: datetime
    requests_count: int
    errors_count: int
    avg_response_time: float
    total_bytes_sent: int
    total_bytes_received: int


class PlatformConnectionPool:
    """Connection pool for platform instances"""
    
    def __init__(self, max_connections: int = 10, idle_timeout: int = 300):
        """
        Initialize connection pool
        
        Args:
            max_connections: Maximum concurrent connections per platform
            idle_timeout: Idle timeout in seconds before closing connections
        """
        self.max_connections = max_connections
        self.idle_timeout = idle_timeout
        self.connections: Dict[str, List[PlatformBase]] = {}
        self.active_connections: Dict[str, set] = {}
        self.connection_metrics: Dict[str, ConnectionMetrics] = {}
        self.lock = asyncio.Lock()
        
    async def get_connection(self, platform_type: PlatformType, 
                           config: PlatformConfig) -> PlatformBase:
        """Get connection from pool or create new one"""
        platform_key = f"{platform_type.value}_{config.user_id}"
        
        async with self.lock:
            # Check for available idle connections
            if platform_key in self.connections and self.connections[platform_key]:
                connection = self.connections[platform_key].pop()
                self.active_connections.setdefault(platform_key, set()).add(id(connection))
                
                # Update metrics
                if platform_key in self.connection_metrics:
                    self.connection_metrics[platform_key].last_activity = datetime.utcnow()
                
                logger.debug(f"Reused connection for {platform_key}")
                return connection
            
            # Create new connection if under limit
            active_count = len(self.active_connections.get(platform_key, set()))
            if active_count < self.max_connections:
                connection = await self._create_connection(platform_type, config)
                self.active_connections.setdefault(platform_key, set()).add(id(connection))
                
                # Initialize metrics
                self.connection_metrics[platform_key] = ConnectionMetrics(
                    platform_id=platform_key,
                    connection_time=time.time(),
                    last_activity=datetime.utcnow(),
                    requests_count=0,
                    errors_count=0,
                    avg_response_time=0,
                    total_bytes_sent=0,
                    total_bytes_received=0
                )
                
                logger.debug(f"Created new connection for {platform_key}")
                return connection
            
            # Wait for available connection
            logger.warning(f"Connection limit reached for {platform_key}, waiting...")
            raise Exception(f"Connection pool exhausted for {platform_key}")
    
    async def _create_connection(self, platform_type: PlatformType, 
                               config: PlatformConfig) -> PlatformBase:
        """Create new platform connection"""
        platform_classes = {
            PlatformType.SPOTIFY: SpotifyPlatform,
            PlatformType.YOUTUBE: YouTubePlatform,
            PlatformType.INSTAGRAM: InstagramPlatform,
            PlatformType.TIKTOK: TikTokPlatform,
            PlatformType.TWITTER: TwitterPlatform,
            PlatformType.FACEBOOK: FacebookPlatform,
            PlatformType.TWITCH: TwitchPlatform,
            PlatformType.SOUNDCLOUD: SoundCloudPlatform,
            PlatformType.APPLE_MUSIC: AppleMusicPlatform,
            PlatformType.BANDCAMP: BandcampPlatform,
            PlatformType.REDDIT: RedditPlatform,
            PlatformType.LINKEDIN: LinkedInPlatform,
            PlatformType.PINTEREST: PinterestPlatform,
            PlatformType.SNAPCHAT: SnapchatPlatform,
            PlatformType.DISCORD: DiscordPlatform,
            PlatformType.TELEGRAM: TelegramPlatform
        }
        
        platform_class = platform_classes.get(platform_type)
        if not platform_class:
            raise ValueError(f"Unsupported platform type: {platform_type}")
        
        platform = platform_class(config)
        
        # Authenticate the connection
        if not await platform.authenticate():
            raise Exception(f"Failed to authenticate {platform_type.value}")
        
        return platform
    
    async def release_connection(self, connection: PlatformBase):
        """Release connection back to pool"""
        platform_key = f"{connection.config.platform_type.value}_{connection.config.user_id}"
        connection_id = id(connection)
        
        async with self.lock:
            # Remove from active connections
            if platform_key in self.active_connections:
                self.active_connections[platform_key].discard(connection_id)
            
            # Add to idle connections if not expired
            if connection.status == PlatformStatus.ACTIVE:
                self.connections.setdefault(platform_key, []).append(connection)
                
                # Limit idle connections
                if len(self.connections[platform_key]) > self.max_connections // 2:
                    oldest = self.connections[platform_key].pop(0)
                    if hasattr(oldest, 'close'):
                        await oldest.close()
            else:
                # Close unhealthy connections
                if hasattr(connection, 'close'):
                    await connection.close()
        
        logger.debug(f"Released connection for {platform_key}")
    
    async def cleanup_idle_connections(self):
        """Clean up idle connections that have timed out"""
        async with self.lock:
            current_time = datetime.utcnow()
            
            for platform_key, connections in list(self.connections.items()):
                cleaned_connections = []
                
                for connection in connections:
                    # Check if connection is still healthy and not expired
                    time_since_activity = current_time - self.connection_metrics.get(
                        platform_key, ConnectionMetrics(
                            platform_id=platform_key,
                            connection_time=0,
                            last_activity=current_time,
                            requests_count=0,
                            errors_count=0,
                            avg_response_time=0,
                            total_bytes_sent=0,
                            total_bytes_received=0
                        )
                    ).last_activity
                    
                    if time_since_activity.total_seconds() < self.idle_timeout:
                        cleaned_connections.append(connection)
                    else:
                        # Close expired connection
                        if hasattr(connection, 'close'):
                            await connection.close()
                        logger.debug(f"Closed idle connection for {platform_key}")
                
                self.connections[platform_key] = cleaned_connections
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        stats = {
            'total_platforms': len(self.connections),
            'active_connections': sum(len(active) for active in self.active_connections.values()),
            'idle_connections': sum(len(idle) for idle in self.connections.values()),
            'max_connections_per_platform': self.max_connections,
            'idle_timeout_seconds': self.idle_timeout,
            'platform_stats': {}
        }
        
        for platform_key in set(list(self.connections.keys()) + list(self.active_connections.keys())):
            active = len(self.active_connections.get(platform_key, set()))
            idle = len(self.connections.get(platform_key, []))
            metrics = self.connection_metrics.get(platform_key)
            
            stats['platform_stats'][platform_key] = {
                'active_connections': active,
                'idle_connections': idle,
                'total_connections': active + idle,
                'metrics': metrics.__dict__ if metrics else None
            }
        
        return stats


class PlatformConnector:
    """Main connector for managing platform connections"""
    
    def __init__(self, pool_size: int = 10, cleanup_interval: int = 300):
        """
        Initialize platform connector
        
        Args:
            pool_size: Maximum connections per platform
            cleanup_interval: Cleanup interval in seconds
        """
        self.pool = PlatformConnectionPool(max_connections=pool_size)
        self.cleanup_interval = cleanup_interval
        self.cleanup_task: Optional[asyncio.Task] = None
        self.connection_cache: Dict[str, weakref.ReferenceType] = {}
        self.active_sessions: Dict[str, aiohttp.ClientSession] = {}
        
    async def start(self):
        """Start the connector and cleanup tasks"""
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Platform connector started")
    
    async def stop(self):
        """Stop the connector and cleanup resources"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all active sessions
        for session in self.active_sessions.values():
            if not session.closed:
                await session.close()
        
        # Close all pooled connections
        for connections in self.pool.connections.values():
            for connection in connections:
                if hasattr(connection, 'close'):
                    await connection.close()
        
        logger.info("Platform connector stopped")
    
    @asynccontextmanager
    async def get_platform(self, platform_type: PlatformType, config: PlatformConfig):
        """Context manager for getting platform connections"""
        connection = None
        try:
            connection = await self.pool.get_connection(platform_type, config)
            yield connection
        finally:
            if connection:
                await self.pool.release_connection(connection)
    
    async def create_platform(self, platform_type: PlatformType, 
                            config: PlatformConfig) -> PlatformBase:
        """Create a new platform instance (not pooled)"""



        return await self.pool._create_connection(platform_type, config)
    
    async def test_connection(self, platform_type: PlatformType, 
                            config: PlatformConfig) -> bool:
        """Test platform connection without using pool"""



        try:
            async with self.get_platform(platform_type, config) as platform:
                return await platform.authenticate()
        except Exception as e:
            logger.error(f"Connection test failed for {platform_type.value}: {e}")
            return False
    
    async def test_all_platforms(self, configs: Dict[PlatformType, PlatformConfig]) -> Dict[PlatformType, bool]:
        """Test connections to all configured platforms"""
        results = {}
        
        # Test connections concurrently
        tasks = []
        for platform_type, config in configs.items():
            task = asyncio.create_task(
                self.test_connection(platform_type, config),
                name=f"test_{platform_type.value}"
            )
            tasks.append((platform_type, task))
        
        # Collect results
        for platform_type, task in tasks:
            try:
                results[platform_type] = await task
            except Exception as e:
                logger.error(f"Test failed for {platform_type.value}: {e}")
                results[platform_type] = False
        
        return results
    
    async def get_platform_health(self, platform_type: PlatformType, 
                                config: PlatformConfig) -> Dict[str, Any]:
        """Get detailed health information for a platform"""



        try:
            start_time = time.time()
            
            async with self.get_platform(platform_type, config) as platform:
                # Test authentication
                auth_success = await platform.authenticate()
                auth_time = time.time() - start_time
                
                # Get platform status
                status = {
                    'platform_type': platform_type.value,
                    'platform_id': platform.platform_id,
                    'authentication_successful': auth_success,
                    'authentication_time_ms': round(auth_time * 1000, 2),
                    'platform_status': platform.status.value if platform.status else None,
                    'error_count': platform.error_count,
                    'last_error': platform.last_error,
                    'rate_limit_remaining': getattr(platform, 'rate_limit_remaining', None),
                    'rate_limit_reset': getattr(platform, 'rate_limit_reset', None)
                }
                
                # Test basic functionality if authentication successful
                if auth_success:
                    try:
                        if hasattr(platform, 'get_user_info'):
                            user_info = await platform.get_user_info()
                            status['user_info_available'] = user_info is not None
                    except Exception as e:
                        status['user_info_error'] = str(e)
                
                return status
                
        except Exception as e:
            return {
                'platform_type': platform_type.value,
                'error': str(e),
                'health_check_failed': True
            }
    
    async def bulk_platform_health(self, configs: Dict[PlatformType, PlatformConfig]) -> Dict[str, Any]:
        """Get health information for multiple platforms"""
        results = {}
        
        # Check health concurrently
        tasks = []
        for platform_type, config in configs.items():
            task = asyncio.create_task(
                self.get_platform_health(platform_type, config),
                name=f"health_{platform_type.value}"
            )
            tasks.append((platform_type, task))
        
        # Collect results
        for platform_type, task in tasks:
            try:
                results[platform_type.value] = await task
            except Exception as e:
                results[platform_type.value] = {
                    'platform_type': platform_type.value,
                    'error': str(e),
                    'health_check_failed': True
                }
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_platforms': len(configs),
            'platforms': results,
            'pool_stats': self.pool.get_pool_stats()
        }
    
    async def refresh_all_tokens(self, configs: Dict[PlatformType, PlatformConfig]) -> Dict[str, bool]:
        """Refresh tokens for all platforms"""
        results = {}
        
        for platform_type, config in configs.items():
            try:
                async with self.get_platform(platform_type, config) as platform:
                    success = await platform.refresh_token()
                    results[platform_type.value] = success
                    
                    if success:
                        logger.info(f"Token refreshed for {platform_type.value}")
                    else:
                        logger.warning(f"Token refresh failed for {platform_type.value}")
                        
            except Exception as e:
                logger.error(f"Token refresh error for {platform_type.value}: {e}")
                results[platform_type.value] = False
        
        return results
    
    async def get_session(self, session_key: str) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if session_key not in self.active_sessions or self.active_sessions[session_key].closed:
            self.active_sessions[session_key] = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=100, limit_per_host=10)
            )
        
        return self.active_sessions[session_key]
    
    async def close_session(self, session_key: str):
        """Close specific HTTP session"""
        if session_key in self.active_sessions:
            session = self.active_sessions.pop(session_key)
            if not session.closed:
                await session.close()
    
    async def _cleanup_loop(self):
        """Background cleanup task"""



        try:
            while True:
                await asyncio.sleep(self.cleanup_interval)
                
                try:
                    await self.pool.cleanup_idle_connections()
                    
                    # Clean up closed sessions
                    closed_sessions = [
                        key for key, session in self.active_sessions.items()
                        if session.closed
                    ]
                    for key in closed_sessions:
                        del self.active_sessions[key]
                    
                    logger.debug("Completed connection cleanup")
                    
                except Exception as e:
                    logger.error(f"Cleanup error: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
        except Exception as e:
            logger.error(f"Cleanup loop error: {e}")
    
    def get_connector_stats(self) -> Dict[str, Any]:
        """Get connector statistics"""



        return {
            'pool_stats': self.pool.get_pool_stats(),
            'active_sessions': len(self.active_sessions),
            'cleanup_interval': self.cleanup_interval,
            'session_keys': list(self.active_sessions.keys())
        }


# Global connector instance
_global_connector: Optional[PlatformConnector] = None


async def get_connector() -> PlatformConnector:
    """Get global connector instance"""
    global _global_connector
    
    if _global_connector is None:
        _global_connector = PlatformConnector()
        await _global_connector.start()
    
    return _global_connector


async def cleanup_connector():
    """Cleanup global connector"""
    global _global_connector
    
    if _global_connector:
        await _global_connector.stop()
        _global_connector = None
