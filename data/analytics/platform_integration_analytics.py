"""
Platform Integration Analytics Engine
====================================

Advanced platform integration analytics for seamless data collection and
unified performance tracking across all major content platforms.

Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices 
- Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

WARNING: This code is the intellectual property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized copying, distribution, or modification without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import aiohttp
import ssl
from urllib.parse import urlencode
import hashlib
import hmac
import base64

import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from redis import Redis
from cryptography.fernet import Fernet
import jwt

from ..models.platform_integration_model import PlatformIntegrationModel
from ..models.api_credentials_model import APICredentialsModel
from ..storage.storage_manager import StorageManager
from ..vector_db.vector_db_manager import VectorDBManager


class IntegrationType(Enum):
    """Platform integration types"""
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    WEBHOOK = "webhook"
    RSS_FEED = "rss_feed"
    SCRAPING = "scraping"
    SDK = "sdk"


class DataSyncStatus(Enum):
    """Data synchronization status"""
    CONNECTED = "connected"
    SYNCING = "syncing"
    ERROR = "error"
    DISCONNECTED = "disconnected"
    RATE_LIMITED = "rate_limited"
    EXPIRED = "expired"


class PlatformCapability(Enum):
    """Platform capability types"""
    READ_ANALYTICS = "read_analytics"
    WRITE_CONTENT = "write_content"
    MANAGE_ACCOUNT = "manage_account"
    ACCESS_AUDIENCE = "access_audience"
    MONETIZATION = "monetization"
    LIVE_STREAMING = "live_streaming"


@dataclass
class PlatformConnection:
    """Platform connection configuration"""
    platform: str
    integration_type: IntegrationType
    status: DataSyncStatus
    capabilities: List[PlatformCapability]
    credentials: Dict[str, Any]
    last_sync: Optional[datetime]
    next_sync: Optional[datetime]
    sync_frequency: int  # minutes
    rate_limit: Dict[str, int]
    webhook_url: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncResult:
    """Data synchronization result"""
    platform: str
    status: DataSyncStatus
    records_processed: int
    errors: List[str]
    sync_duration: float
    data_quality_score: float
    timestamp: datetime
    next_sync_time: datetime


@dataclass
class PlatformHealthCheck:
    """Platform health monitoring result"""
    platform: str
    is_healthy: bool
    response_time: float
    api_quota_remaining: int
    error_rate: float
    uptime_percentage: float
    last_successful_sync: datetime
    issues: List[str]
    recommendations: List[str]


class PlatformIntegrationAnalytics:
    """
    Professional platform integration analytics engine for IA Influencer Agent platform.
    
    Manages seamless integration with all major content platforms, handles authentication,
    data synchronization, and provides unified analytics across platforms.
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: Redis,
                 storage_manager: StorageManager, vector_db: VectorDBManager):
        """
        Initialize Platform Integration Analytics engine.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
            storage_manager: Storage management service
            vector_db: Vector database manager
        """
        self.db_session = db_session
        self.redis_client = redis_client
        self.storage_manager = storage_manager
        self.vector_db = vector_db
        self.logger = logging.getLogger(__name__)
        
        # Encryption for credentials
        self.encryption_key = self._get_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # HTTP session with custom configurations
        self.http_session = None
        
        # Platform configurations
        self.platform_configs = self._initialize_platform_configurations()
        
        # Active connections
        self.active_connections: Dict[str, PlatformConnection] = {}
        
        # Webhook handlers
        self.webhook_handlers: Dict[str, Callable] = {}
        
        # Rate limiting
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}
        
        # Caching
        self.cache_ttl = 300  # 5 minutes for API responses
        self.connection_cache_ttl = 3600  # 1 hour for connections
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            ssl=ssl.create_default_context()
        )
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.http_session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": "IA-Influencer-Agent/1.0"}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.http_session:
            await self.http_session.close()
    
    async def connect_platform(self, user_id: str, platform: str,
                             credentials: Dict[str, Any],
                             capabilities: List[PlatformCapability] = None) -> PlatformConnection:
        """
        Connect to a content platform with proper authentication.
        
        Args:
            user_id: User identifier
            platform: Platform name
            credentials: Platform credentials
            capabilities: Requested capabilities
            
        Returns:
            PlatformConnection object
        """
        try:
            if capabilities is None:
                capabilities = [PlatformCapability.READ_ANALYTICS]
            
            # Validate platform support
            if platform not in self.platform_configs:
                raise ValueError(f"Platform {platform} not supported")
            
            config = self.platform_configs[platform]
            
            # Validate credentials
            await self._validate_credentials(platform, credentials)
            
            # Establish connection
            connection = await self._establish_platform_connection(
                user_id, platform, credentials, capabilities, config
            )
            
            # Store encrypted credentials
            await self._store_encrypted_credentials(user_id, platform, credentials)
            
            # Initialize sync schedule
            await self._setup_sync_schedule(connection)
            
            # Store connection
            connection_key = f"{user_id}:{platform}"
            self.active_connections[connection_key] = connection
            
            # Cache connection
            cache_key = f"platform_connection:{user_id}:{platform}"
            await self._cache_result(cache_key, connection.__dict__, self.connection_cache_ttl)
            
            self.logger.info(f"Successfully connected to {platform} for user {user_id}")
            
            return connection
            
        except Exception as e:
            self.logger.error(f"Error connecting to platform {platform}: {str(e)}")
            raise
    
    async def sync_platform_data(self, user_id: str, platform: str,
                               force_sync: bool = False) -> SyncResult:
        """
        Synchronize data from a connected platform.
        
        Args:
            user_id: User identifier
            platform: Platform name
            force_sync: Force immediate sync regardless of schedule
            
        Returns:
            SyncResult with synchronization details
        """
        try:
            # Get platform connection
            connection = await self._get_platform_connection(user_id, platform)
            if not connection:
                raise ValueError(f"No active connection for platform {platform}")
            
            if connection.status != DataSyncStatus.CONNECTED and not force_sync:
                raise ValueError(f"Platform {platform} is not connected")
            
            # Check if sync is needed
            if not force_sync and not await self._is_sync_needed(connection):
                return SyncResult(
                    platform=platform,
                    status=DataSyncStatus.CONNECTED,
                    records_processed=0,
                    errors=[],
                    sync_duration=0.0,
                    data_quality_score=1.0,
                    timestamp=datetime.now(),
                    next_sync_time=connection.next_sync
                )
            
            start_time = datetime.now()
            
            # Update connection status
            connection.status = DataSyncStatus.SYNCING
            await self._update_connection_status(user_id, platform, connection.status)
            
            # Perform platform-specific sync
            sync_data = await self._perform_platform_sync(connection, user_id)
            
            # Process and validate data
            processed_records = await self._process_sync_data(
                user_id, platform, sync_data
            )
            
            # Calculate data quality score
            quality_score = await self._calculate_data_quality(sync_data)
            
            # Update connection
            connection.status = DataSyncStatus.CONNECTED
            connection.last_sync = datetime.now()
            connection.next_sync = self._calculate_next_sync_time(connection)
            
            await self._update_connection_status(user_id, platform, connection.status)
            
            sync_duration = (datetime.now() - start_time).total_seconds()
            
            result = SyncResult(
                platform=platform,
                status=DataSyncStatus.CONNECTED,
                records_processed=processed_records,
                errors=[],
                sync_duration=sync_duration,
                data_quality_score=quality_score,
                timestamp=datetime.now(),
                next_sync_time=connection.next_sync
            )
            
            # Log successful sync
            self.logger.info(f"Successfully synced {processed_records} records from {platform}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error syncing platform {platform}: {str(e)}")
            
            # Update connection status to error
            await self._update_connection_status(user_id, platform, DataSyncStatus.ERROR)
            
            return SyncResult(
                platform=platform,
                status=DataSyncStatus.ERROR,
                records_processed=0,
                errors=[str(e)],
                sync_duration=0.0,
                data_quality_score=0.0,
                timestamp=datetime.now(),
                next_sync_time=datetime.now() + timedelta(hours=1)  # Retry in 1 hour
            )
    
    async def get_platform_health(self, user_id: str, platform: str) -> PlatformHealthCheck:
        """
        Perform health check on platform connection.
        
        Args:
            user_id: User identifier
            platform: Platform name
            
        Returns:
            PlatformHealthCheck result
        """
        try:
            connection = await self._get_platform_connection(user_id, platform)
            if not connection:
                return PlatformHealthCheck(
                    platform=platform,
                    is_healthy=False,
                    response_time=0.0,
                    api_quota_remaining=0,
                    error_rate=1.0,
                    uptime_percentage=0.0,
                    last_successful_sync=datetime.min,
                    issues=["No active connection"],
                    recommendations=["Reconnect to platform"]
                )
            
            start_time = datetime.now()
            
            # Test API connectivity
            test_result = await self._test_api_connectivity(connection)
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Check API quota
            quota_info = await self._check_api_quota(connection)
            
            # Calculate error rate
            error_rate = await self._calculate_error_rate(user_id, platform)
            
            # Calculate uptime
            uptime_percentage = await self._calculate_uptime(user_id, platform)
            
            # Identify issues
            issues = await self._identify_platform_issues(connection, test_result, quota_info)
            
            # Generate recommendations
            recommendations = await self._generate_health_recommendations(
                connection, issues, quota_info
            )
            
            is_healthy = len(issues) == 0 and test_result.get("success", False)
            
            return PlatformHealthCheck(
                platform=platform,
                is_healthy=is_healthy,
                response_time=response_time,
                api_quota_remaining=quota_info.get("remaining", 0),
                error_rate=error_rate,
                uptime_percentage=uptime_percentage,
                last_successful_sync=connection.last_sync or datetime.min,
                issues=issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error checking platform health for {platform}: {str(e)}")
            
            return PlatformHealthCheck(
                platform=platform,
                is_healthy=False,
                response_time=0.0,
                api_quota_remaining=0,
                error_rate=1.0,
                uptime_percentage=0.0,
                last_successful_sync=datetime.min,
                issues=[f"Health check failed: {str(e)}"],
                recommendations=["Check platform configuration and credentials"]
            )
    
    async def setup_webhook_handler(self, platform: str, user_id: str,
                                  webhook_url: str, events: List[str]) -> Dict[str, Any]:
        """
        Setup webhook handler for real-time platform updates.
        
        Args:
            platform: Platform name
            user_id: User identifier
            webhook_url: Webhook endpoint URL
            events: List of events to subscribe to
            
        Returns:
            Webhook configuration details
        """
        try:
            connection = await self._get_platform_connection(user_id, platform)
            if not connection:
                raise ValueError(f"No active connection for platform {platform}")
            
            # Validate webhook support
            if not self._supports_webhooks(platform):
                raise ValueError(f"Platform {platform} does not support webhooks")
            
            # Generate webhook secret
            webhook_secret = self._generate_webhook_secret()
            
            # Register webhook with platform
            webhook_config = await self._register_platform_webhook(
                connection, webhook_url, events, webhook_secret
            )
            
            # Store webhook configuration
            await self._store_webhook_config(user_id, platform, webhook_config)
            
            # Setup local webhook handler
            handler_key = f"{platform}:{user_id}"
            self.webhook_handlers[handler_key] = self._create_webhook_handler(
                platform, user_id, webhook_secret
            )
            
            # Update connection
            connection.webhook_url = webhook_url
            connection.metadata["webhook_config"] = webhook_config
            
            return {
                "webhook_id": webhook_config.get("id"),
                "webhook_url": webhook_url,
                "events": events,
                "status": "active",
                "verification_token": webhook_config.get("verification_token")
            }
            
        except Exception as e:
            self.logger.error(f"Error setting up webhook for {platform}: {str(e)}")
            raise
    
    async def get_unified_analytics(self, user_id: str, 
                                  timeframe_days: int = 30) -> Dict[str, Any]:
        """
        Get unified analytics across all connected platforms.
        
        Args:
            user_id: User identifier
            timeframe_days: Analysis timeframe
            
        Returns:
            Unified analytics data
        """
        try:
            # Get all connected platforms
            connected_platforms = await self._get_connected_platforms(user_id)
            
            if not connected_platforms:
                return {}
            
            # Collect data from all platforms
            platform_data = {}
            sync_tasks = []
            
            for platform in connected_platforms:
                task = asyncio.create_task(
                    self._collect_platform_analytics(user_id, platform, timeframe_days)
                )
                sync_tasks.append((platform, task))
            
            # Wait for all collections to complete
            for platform, task in sync_tasks:
                try:
                    data = await task
                    if data:
                        platform_data[platform] = data
                except Exception as e:
                    self.logger.error(f"Error collecting data from {platform}: {str(e)}")
            
            # Unify and normalize data
            unified_data = await self._unify_platform_data(platform_data)
            
            # Calculate cross-platform metrics
            cross_platform_metrics = await self._calculate_cross_platform_metrics(unified_data)
            
            # Generate insights
            insights = await self._generate_unified_insights(unified_data, cross_platform_metrics)
            
            return {
                "timeframe_days": timeframe_days,
                "connected_platforms": list(platform_data.keys()),
                "platform_data": platform_data,
                "unified_metrics": unified_data,
                "cross_platform_metrics": cross_platform_metrics,
                "insights": insights,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting unified analytics: {str(e)}")
            raise
    
    async def migrate_platform_data(self, user_id: str, source_platform: str,
                                  target_platform: str, data_types: List[str]) -> Dict[str, Any]:
        """
        Migrate data between platforms.
        
        Args:
            user_id: User identifier
            source_platform: Source platform
            target_platform: Target platform
            data_types: Types of data to migrate
            
        Returns:
            Migration result
        """
        try:
            # Validate connections
            source_conn = await self._get_platform_connection(user_id, source_platform)
            target_conn = await self._get_platform_connection(user_id, target_platform)
            
            if not source_conn or not target_conn:
                raise ValueError("Both platforms must be connected for migration")
            
            # Check migration compatibility
            compatibility = await self._check_migration_compatibility(
                source_platform, target_platform, data_types
            )
            
            if not compatibility["is_compatible"]:
                raise ValueError(f"Migration not compatible: {compatibility['reason']}")
            
            migration_results = {}
            
            for data_type in data_types:
                try:
                    # Extract data from source
                    source_data = await self._extract_migration_data(
                        source_conn, data_type
                    )
                    
                    # Transform data for target platform
                    transformed_data = await self._transform_migration_data(
                        source_data, source_platform, target_platform, data_type
                    )
                    
                    # Load data to target platform
                    load_result = await self._load_migration_data(
                        target_conn, transformed_data, data_type
                    )
                    
                    migration_results[data_type] = {
                        "status": "success",
                        "records_migrated": len(transformed_data),
                        "details": load_result
                    }
                    
                except Exception as e:
                    migration_results[data_type] = {
                        "status": "error",
                        "error": str(e),
                        "records_migrated": 0
                    }
            
            return {
                "migration_id": self._generate_migration_id(),
                "source_platform": source_platform,
                "target_platform": target_platform,
                "data_types": data_types,
                "results": migration_results,
                "overall_status": "completed" if all(
                    r["status"] == "success" for r in migration_results.values()
                ) else "partial",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error migrating data: {str(e)}")
            raise
    
    # Private helper methods
    
    def _initialize_platform_configurations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize platform-specific configurations"""
        return {
            "spotify": {
                "auth_url": "https://accounts.spotify.com/authorize",
                "token_url": "https://accounts.spotify.com/api/token",
                "api_base": "https://api.spotify.com/v1",
                "scopes": ["user-read-private", "user-read-email", "user-library-read"],
                "rate_limit": {"requests": 100, "window": 60},
                "webhook_support": False,
                "capabilities": [
                    PlatformCapability.READ_ANALYTICS,
                    PlatformCapability.ACCESS_AUDIENCE,
                    PlatformCapability.MONETIZATION
                ]
            },
            "youtube": {
                "auth_url": "https://accounts.google.com/o/oauth2/auth",
                "token_url": "https://oauth2.googleapis.com/token",
                "api_base": "https://www.googleapis.com/youtube/v3",
                "scopes": ["https://www.googleapis.com/auth/youtube.readonly"],
                "rate_limit": {"requests": 10000, "window": 60},
                "webhook_support": True,
                "capabilities": [
                    PlatformCapability.READ_ANALYTICS,
                    PlatformCapability.WRITE_CONTENT,
                    PlatformCapability.ACCESS_AUDIENCE,
                    PlatformCapability.LIVE_STREAMING
                ]
            },
            "tiktok": {
                "auth_url": "https://open-api.tiktok.com/platform/oauth/connect/",
                "token_url": "https://open-api.tiktok.com/oauth/access_token/",
                "api_base": "https://open-api.tiktok.com",
                "scopes": ["user.info.basic", "video.list"],
                "rate_limit": {"requests": 100, "window": 60},
                "webhook_support": True,
                "capabilities": [
                    PlatformCapability.READ_ANALYTICS,
                    PlatformCapability.WRITE_CONTENT,
                    PlatformCapability.ACCESS_AUDIENCE
                ]
            },
            "instagram": {
                "auth_url": "https://api.instagram.com/oauth/authorize",
                "token_url": "https://api.instagram.com/oauth/access_token",
                "api_base": "https://graph.instagram.com",
                "scopes": ["user_profile", "user_media"],
                "rate_limit": {"requests": 200, "window": 60},
                "webhook_support": True,
                "capabilities": [
                    PlatformCapability.READ_ANALYTICS,
                    PlatformCapability.WRITE_CONTENT,
                    PlatformCapability.ACCESS_AUDIENCE
                ]
            }
            # Add more platforms as needed
        }
    
    def _get_encryption_key(self) -> bytes:
        """Get or generate encryption key for credentials"""
        # In production, this should come from secure key management
        import os
        key = os.environ.get("PLATFORM_ENCRYPTION_KEY")
        if not key:
            key = Fernet.generate_key()
            # Store securely in production
        return key if isinstance(key, bytes) else key.encode()
    
    async def _cache_result(self, cache_key: str, data: Dict[str, Any], 
                          ttl: int = None) -> None:
        """Cache result in Redis"""
        try:
            if ttl is None:
                ttl = self.cache_ttl
            serialized_data = json.dumps(data, default=str)
            self.redis_client.setex(cache_key, ttl, serialized_data)
        except Exception as e:
            self.logger.error(f"Error caching result: {str(e)}")
    
    # Additional helper methods would continue here...
    # Due to length constraints, focusing on core functionality
