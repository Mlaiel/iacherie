"""Platform Connector and Manager
Multi-platform API integration and data synchronization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, asdict
import aiohttp
import json
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from ...integrations.spotify import SpotifyAPIClient
from ...integrations.youtube import YouTubeAPIClient
from ...integrations.instagram import InstagramAPIClient
from ...integrations.tiktok import TikTokAPIClient
from ...security.api_security import APIKeyManager
from ...core.exceptions import PlatformConnectionError, APIRateLimitError


class PlatformStatus(Enum):
    """Platform connection status"""    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"


class DataSyncStatus(Enum):
    """Data synchronization status"""    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class PlatformCredentials:
    """Platform API credentials"""    platform: str
    api_key: str
    secret_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = None
    
    def is_expired(self) -> bool:
        """Check if credentials are expired"""        if not self.expires_at:
            return False
        return datetime.now() >= self.expires_at


@dataclass
class PlatformMetrics:
    """Platform performance metrics"""    platform: str
    user_id: int
    followers_count: int
    total_plays: int
    total_revenue: float
    engagement_rate: float
    last_updated: datetime
    content_count: int
    monthly_growth: float
    top_content: List[Dict[str, Any]]


@dataclass
class SyncResult:
    """Data synchronization result"""    platform: str
    status: DataSyncStatus
    records_synced: int
    errors: List[str]
    duration_seconds: float
    last_sync: datetime


class PlatformConnector:
    """Individual platform API connector"""    
    def __init__(self, platform: str, credentials: PlatformCredentials):
        self.platform = platform
        self.credentials = credentials
        self.logger = logging.getLogger(f"{__name__}.{platform}")
        self.client = None
        self.status = PlatformStatus.DISCONNECTED
        self.last_error = None
        self.rate_limit_reset = None
        
    async def connect(self) -> bool:
        """Establish connection to platform API"""        try:
            if self.credentials.is_expired():
                await self.refresh_credentials()
            
            # Initialize platform-specific client
            if self.platform == "spotify":
                self.client = SpotifyAPIClient(self.credentials)
            elif self.platform == "youtube":
                self.client = YouTubeAPIClient(self.credentials)
            elif self.platform == "instagram":
                self.client = InstagramAPIClient(self.credentials)
            elif self.platform == "tiktok":
                self.client = TikTokAPIClient(self.credentials)
            else:
                raise PlatformConnectionError(f"Unsupported platform: {self.platform}")
            
            # Test connection
            await self.client.test_connection()
            self.status = PlatformStatus.CONNECTED
            self.last_error = None
            
            self.logger.info(f"Successfully connected to {self.platform}")
            return True
            
        except Exception as e:
            self.status = PlatformStatus.ERROR
            self.last_error = str(e)
            self.logger.error(f"Failed to connect to {self.platform}: {str(e)}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from platform API"""        if self.client:
            await self.client.close()
            self.client = None
        self.status = PlatformStatus.DISCONNECTED
    
    async def refresh_credentials(self) -> bool:
        """Refresh expired credentials"""        try:
            if not self.credentials.refresh_token:
                raise PlatformConnectionError("No refresh token available")
            
            # Platform-specific token refresh logic
            if self.platform == "spotify":
                new_creds = await self._refresh_spotify_token()
            elif self.platform == "youtube":
                new_creds = await self._refresh_youtube_token()
            else:
                raise PlatformConnectionError(f"Token refresh not implemented for {self.platform}")
            
            # Update credentials
            self.credentials.access_token = new_creds["access_token"]
            self.credentials.expires_at = new_creds["expires_at"]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to refresh credentials for {self.platform}: {str(e)}")
            return False
    
    async def fetch_user_metrics(self, user_id: int) -> Optional[PlatformMetrics]:
        """Fetch user metrics from platform"""        try:
            if self.status != PlatformStatus.CONNECTED:
                await self.connect()
            
            if not self.client:
                return None
            
            # Fetch platform-specific metrics
            raw_metrics = await self.client.get_user_metrics(user_id)
            
            return PlatformMetrics(
                platform=self.platform,
                user_id=user_id,
                followers_count=raw_metrics.get("followers", 0),
                total_plays=raw_metrics.get("total_plays", 0),
                total_revenue=raw_metrics.get("revenue", 0.0),
                engagement_rate=raw_metrics.get("engagement_rate", 0.0),
                content_count=raw_metrics.get("content_count", 0),
                monthly_growth=raw_metrics.get("monthly_growth", 0.0),
                top_content=raw_metrics.get("top_content", []),
                last_updated=datetime.now()
            )
            
        except APIRateLimitError as e:
            self.status = PlatformStatus.RATE_LIMITED
            self.rate_limit_reset = e.reset_time
            self.logger.warning(f"Rate limited for {self.platform}: {str(e)}")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to fetch metrics from {self.platform}: {str(e)}")
            return None
    
    async def sync_revenue_data(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> SyncResult:
        """Synchronize revenue data from platform"""        sync_start = datetime.now()
        records_synced = 0
        errors = []
        
        try:
            if self.status != PlatformStatus.CONNECTED:
                await self.connect()
            
            if not self.client:
                raise PlatformConnectionError(f"No client for platform {self.platform}")
            
            # Fetch revenue data
            revenue_data = await self.client.get_revenue_data(
                user_id, start_date, end_date
            )
            
            # Process and store revenue records
            for record in revenue_data:
                try:
                    # Validate and normalize data
                    normalized_record = await self._normalize_revenue_record(record)
                    records_synced += 1
                    
                except Exception as e:
                    errors.append(f"Failed to process record {record.get('id', 'unknown')}: {str(e)}")
            
            status = DataSyncStatus.COMPLETED if not errors else DataSyncStatus.PARTIAL
            
        except Exception as e:
            status = DataSyncStatus.FAILED
            errors.append(str(e))
            self.logger.error(f"Revenue sync failed for {self.platform}: {str(e)}")
        
        duration = (datetime.now() - sync_start).total_seconds()
        
        return SyncResult(
            platform=self.platform,
            status=status,
            records_synced=records_synced,
            errors=errors,
            duration_seconds=duration,
            last_sync=datetime.now()
        )
    
    async def _normalize_revenue_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize platform-specific revenue record format"""        # Platform-specific normalization logic
        normalized = {
            "platform": self.platform,
            "external_id": record.get("id"),
            "amount": float(record.get("amount", 0)),
            "currency": record.get("currency", "USD"),
            "date": record.get("date"),
            "source": record.get("source", "streaming"),
            "metadata": record.get("metadata", {})
        }
        
        return normalized
    
    async def _refresh_spotify_token(self) -> Dict[str, Any]:
        """Refresh Spotify access token"""        # Spotify token refresh implementation
        refresh_url = "https://accounts.spotify.com/api/token"
        
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.credentials.refresh_token
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials.api_key}"
            }
            
            async with session.post(refresh_url, data=data, headers=headers) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return {
                        "access_token": token_data["access_token"],
                        "expires_at": datetime.now() + timedelta(seconds=token_data["expires_in"])
                    }
                else:
                    raise PlatformConnectionError("Failed to refresh Spotify token")
    
    async def _refresh_youtube_token(self) -> Dict[str, Any]:
        """Refresh YouTube access token"""        # YouTube token refresh implementation
        refresh_url = "https://oauth2.googleapis.com/token"
        
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": self.credentials.refresh_token,
                "client_id": self.credentials.api_key,
                "client_secret": self.credentials.secret_key
            }
            
            async with session.post(refresh_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    return {
                        "access_token": token_data["access_token"],
                        "expires_at": datetime.now() + timedelta(seconds=token_data["expires_in"])
                    }
                else:
                    raise PlatformConnectionError("Failed to refresh YouTube token")


class PlatformManager:
    """Manage multiple platform connections and data synchronization"""    
    def __init__(self, api_key_manager: APIKeyManager):
        self.api_key_manager = api_key_manager
        self.logger = logging.getLogger(__name__)
        self.connectors: Dict[str, PlatformConnector] = {}
        self.sync_scheduler = None
        
    async def add_platform(
        self, 
        user_id: int, 
        platform: str, 
        credentials: PlatformCredentials
    ) -> bool:
        """Add platform connection for user"""        try:
            # Store credentials securely
            await self.api_key_manager.store_credentials(
                user_id, platform, credentials
            )
            
            # Create connector
            connector = PlatformConnector(platform, credentials)
            connector_key = f"{user_id}_{platform}"
            
            # Test connection
            if await connector.connect():
                self.connectors[connector_key] = connector
                self.logger.info(f"Added platform {platform} for user {user_id}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to add platform {platform} for user {user_id}: {str(e)}")
            return False
    
    async def remove_platform(self, user_id: int, platform: str) -> bool:
        """Remove platform connection for user"""        try:
            connector_key = f"{user_id}_{platform}"
            
            # Disconnect and remove connector
            if connector_key in self.connectors:
                await self.connectors[connector_key].disconnect()
                del self.connectors[connector_key]
            
            # Remove stored credentials
            await self.api_key_manager.remove_credentials(user_id, platform)
            
            self.logger.info(f"Removed platform {platform} for user {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove platform {platform} for user {user_id}: {str(e)}")
            return False
    
    async def get_user_platforms(self, user_id: int) -> List[str]:
        """Get list of connected platforms for user"""        platforms = []
        
        for connector_key, connector in self.connectors.items():
            if connector_key.startswith(f"{user_id}_"):
                platforms.append(connector.platform)
        
        return platforms
    
    async def get_platform_status(self, user_id: int, platform: str) -> PlatformStatus:
        """Get connection status for specific platform"""        connector_key = f"{user_id}_{platform}"
        
        if connector_key in self.connectors:
            return self.connectors[connector_key].status
        else:
            return PlatformStatus.DISCONNECTED
    
    async def sync_user_data(
        self, 
        user_id: int, 
        platforms: Optional[List[str]] = None
    ) -> Dict[str, SyncResult]:
        """Synchronize data for user across platforms"""        results = {}
        
        # Get platforms to sync
        if platforms is None:
            platforms = await self.get_user_platforms(user_id)
        
        # Sync each platform
        sync_tasks = []
        for platform in platforms:
            connector_key = f"{user_id}_{platform}"
            if connector_key in self.connectors:
                connector = self.connectors[connector_key]
                
                # Calculate sync period (last 30 days)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                
                # Add sync task
                task = connector.sync_revenue_data(user_id, start_date, end_date)
                sync_tasks.append((platform, task))
        
        # Execute sync tasks concurrently
        for platform, task in sync_tasks:
            try:
                result = await task
                results[platform] = result
            except Exception as e:
                results[platform] = SyncResult(
                    platform=platform,
                    status=DataSyncStatus.FAILED,
                    records_synced=0,
                    errors=[str(e)],
                    duration_seconds=0,
                    last_sync=datetime.now()
                )
        
        return results
    
    async def get_aggregated_metrics(
        self, 
        user_id: int
    ) -> Dict[str, PlatformMetrics]:
        """Get aggregated metrics from all connected platforms"""        metrics = {}
        
        platforms = await self.get_user_platforms(user_id)
        
        # Fetch metrics from each platform
        metric_tasks = []
        for platform in platforms:
            connector_key = f"{user_id}_{platform}"
            if connector_key in self.connectors:
                connector = self.connectors[connector_key]
                task = connector.fetch_user_metrics(user_id)
                metric_tasks.append((platform, task))
        
        # Execute metric fetching concurrently
        for platform, task in metric_tasks:
            try:
                platform_metrics = await task
                if platform_metrics:
                    metrics[platform] = platform_metrics
            except Exception as e:
                self.logger.error(f"Failed to fetch metrics for {platform}: {str(e)}")
        
        return metrics
    
    async def schedule_automated_sync(
        self, 
        interval_hours: int = 6
    ) -> None:
        """Schedule automated data synchronization"""        while True:
            try:
                # Get all users with connected platforms
                users_to_sync = await self._get_users_for_sync()
                
                # Sync each user's data
                for user_id in users_to_sync:
                    try:
                        await self.sync_user_data(user_id)
                        self.logger.info(f"Completed automated sync for user {user_id}")
                    except Exception as e:
                        self.logger.error(f"Automated sync failed for user {user_id}: {str(e)}")
                
                # Wait for next sync interval
                await asyncio.sleep(interval_hours * 3600)
                
            except Exception as e:
                self.logger.error(f"Automated sync scheduler error: {str(e)}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def _get_users_for_sync(self) -> List[int]:
        """Get list of users that need data synchronization"""        users = set()
        
        for connector_key in self.connectors.keys():
            user_id = int(connector_key.split("_")[0])
            users.add(user_id)
        
        return list(users)
    
    async def reconnect_failed_platforms(self) -> None:
        """Attempt to reconnect failed platform connections"""        for connector_key, connector in self.connectors.items():
            if connector.status in [PlatformStatus.ERROR, PlatformStatus.DISCONNECTED]:
                try:
                    await connector.connect()
                    if connector.status == PlatformStatus.CONNECTED:
                        self.logger.info(f"Reconnected platform {connector.platform}")
                except Exception as e:
                    self.logger.error(f"Failed to reconnect {connector.platform}: {str(e)}")
    
    async def get_connection_health(self) -> Dict[str, Any]:
        """Get overall connection health status"""        total_connections = len(self.connectors)
        connected_count = sum(
            1 for connector in self.connectors.values()
            if connector.status == PlatformStatus.CONNECTED
        )
        
        error_count = sum(
            1 for connector in self.connectors.values()
            if connector.status == PlatformStatus.ERROR
        )
        
        rate_limited_count = sum(
            1 for connector in self.connectors.values()
            if connector.status == PlatformStatus.RATE_LIMITED
        )
        
        return {
            "total_connections": total_connections,
            "connected": connected_count,
            "errors": error_count,
            "rate_limited": rate_limited_count,
            "health_percentage": (connected_count / total_connections * 100) if total_connections > 0 else 0,
            "last_check": datetime.now().isoformat()
        }
    
    async def close_all_connections(self) -> None:
        """Close all platform connections"""        for connector in self.connectors.values():
            await connector.disconnect()
        
        self.connectors.clear()
        self.logger.info("All platform connections closed")
