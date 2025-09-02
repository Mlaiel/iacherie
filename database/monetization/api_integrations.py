"""API Integrations Engine - Multi-Platform Revenue and Analytics Integration

Ultra-advanced API integration system for seamless data synchronization across all
major content platforms with real-time updates, intelligent retry logic, and comprehensive analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use, modification, or distribution prohibited.

🚨 CRITICAL LEGAL WARNING:
This code and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, distribution, or commercialization 
is STRICTLY PROHIBITED and will result in immediate legal action.

Contact: mlaiel@live.de for licensing inquiries and authorization.

Expert Project Team - Fahed Mlaiel:
- Lead AI Developer & Solution Architect
- Senior Backend Engineer (Python/FastAPI/Django)
- Machine Learning Engineer (TensorFlow/PyTorch/Hugging Face)
- Database Administrator & Data Engineer (PostgreSQL/Redis/MongoDB)
- Backend Security Specialist
- Microservices Architect
- Audio Processing Engineer
- DevOps Engineer
- AI Prompt Engineer & Automation Specialist
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, Any, List, Optional, Union, Tuple
from enum import Enum
import uuid
from dataclasses import dataclass
import aiohttp
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, desc
from sqlalchemy.orm import selectinload

from .platform_connections import (
    PlatformConnection, PlatformSyncLog, PlatformAnalytics,
    PlatformRevenue, PlatformContentMetadata, Platform,
    ConnectionStatus, DataSyncFrequency
)
from ..core.exceptions import APIIntegrationError, RateLimitError, AuthenticationError
from ..core.security import SecurityManager
from ..core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """
Standardized API response structure"""
    success: bool
    data: Dict[str, Any]
    status_code: int
    rate_limit_remaining: Optional[int] = None
    rate_limit_reset: Optional[datetime] = None
    error_message: Optional[str] = None
    request_id: Optional[str] = None


class PlatformAPIIntegrator:
    """
    Ultra-advanced platform API integration engine supporting all major content
    platforms with intelligent rate limiting, error recovery, and data synchronization
    """
    
    def __init__(self):
        self.security_manager = SecurityManager()
        self.session_pools = {}
        self.rate_limiters = {}
        self.retry_strategies = {}
        
        # Initialize platform-specific configurations
        self._initialize_platform_configs()
    
    def _initialize_platform_configs(self):
        """
Initialize platform-specific API configurations"""
        self.platform_configs = {
            Platform.SPOTIFY: {
                "base_url": "https://api.spotify.com/v1",
                "auth_url": "https://accounts.spotify.com/api/token",
                "scope": "user-read-private user-read-email streaming user-library-read",
                "rate_limit": {"requests": 100, "window": 60},
                "retry_delays": [1, 2, 4, 8, 16]
            },
            Platform.YOUTUBE: {
                "base_url": "https://www.googleapis.com/youtube/v3",
                "auth_url": "https://oauth2.googleapis.com/token",
                "scope": "https://www.googleapis.com/auth/youtube.readonly",
                "rate_limit": {"requests": 10000, "window": 86400},
                "retry_delays": [1, 3, 7, 15, 30]
            },
            Platform.INSTAGRAM: {
                "base_url": "https://graph.instagram.com",
                "auth_url": "https://graph.facebook.com/oauth/access_token",
                "scope": "instagram_basic,instagram_content_publish",
                "rate_limit": {"requests": 200, "window": 3600},
                "retry_delays": [2, 5, 10, 20, 40]
            },
            Platform.TIKTOK: {
                "base_url": "https://open-api.tiktok.com/v1.2",
                "auth_url": "https://open-api.tiktok.com/oauth/access_token",
                "scope": "user.info.basic,video.list",
                "rate_limit": {"requests": 1000, "window": 86400},
                "retry_delays": [1, 2, 4, 8, 16]
            },
            Platform.APPLE_MUSIC: {
                "base_url": "https://api.music.apple.com/v1",
                "auth_url": "https://appleid.apple.com/auth/oauth2/token",
                "scope": "media-user-access",
                "rate_limit": {"requests": 1000, "window": 3600},
                "retry_delays": [1, 3, 6, 12, 24]
            }
        }
    
    async def sync_platform_data(
        self,
        session: AsyncSession,
        connection_id: str,
        sync_types: List[str] = None,
        force_full_sync: bool = False
    ) -> Dict[str, Any]:
        """
        Synchronize data from a platform connection with comprehensive
        error handling and intelligent retry logic
        """
        try:
            # Get platform connection
            connection = await self._get_platform_connection(session, connection_id)
            if not connection:
                raise APIIntegrationError(f"Platform connection not found: {connection_id}")
            
            if connection.status != ConnectionStatus.CONNECTED:
                raise APIIntegrationError(f"Platform connection not active: {connection.status.value}")
            
            # Create sync log
            sync_log = PlatformSyncLog(
                connection_id=connection.id,
                sync_type="full" if force_full_sync else "incremental",
                sync_scope=sync_types or ["analytics", "revenue", "content"],
                started_at=datetime.now(timezone.utc)
            )
            session.add(sync_log)
            await session.flush()
            
            # Initialize platform-specific API client
            api_client = await self._get_platform_client(connection)
            
            sync_results = {
                "analytics": {"processed": 0, "created": 0, "updated": 0, "errors": 0},
                "revenue": {"processed": 0, "created": 0, "updated": 0, "errors": 0},
                "content": {"processed": 0, "created": 0, "updated": 0, "errors": 0}
            }
            
            # Sync analytics data
            if not sync_types or "analytics" in sync_types:
                analytics_result = await self._sync_analytics_data(
                    session, connection, api_client, force_full_sync
                )
                sync_results["analytics"] = analytics_result
            
            # Sync revenue data
            if not sync_types or "revenue" in sync_types:
                revenue_result = await self._sync_revenue_data(
                    session, connection, api_client, force_full_sync
                )
                sync_results["revenue"] = revenue_result
            
            # Sync content metadata
            if not sync_types or "content" in sync_types:
                content_result = await self._sync_content_metadata(
                    session, connection, api_client, force_full_sync
                )
                sync_results["content"] = content_result
            
            # Update sync log with results
            sync_log.completed_at = datetime.now(timezone.utc)
            sync_log.status = "completed"
            sync_log.records_processed = sum(r["processed"] for r in sync_results.values())
            sync_log.records_created = sum(r["created"] for r in sync_results.values())
            sync_log.records_updated = sum(r["updated"] for r in sync_results.values())
            sync_log.records_failed = sum(r["errors"] for r in sync_results.values())
            
            # Update connection last sync time
            connection.last_sync_at = datetime.now(timezone.utc)
            connection.next_sync_at = self._calculate_next_sync(connection.sync_frequency)
            
            await session.commit()
            
            logger.info(f"Platform sync completed for {connection.platform.value}: {sync_results}")
            return {
                "sync_log_id": str(sync_log.id),
                "status": "completed",
                "results": sync_results,
                "duration_seconds": sync_log.duration_seconds
            }
            
        except Exception as e:
            await session.rollback()
            
            if 'sync_log' in locals():
                sync_log.status = "failed"
                sync_log.error_message = str(e)
                sync_log.completed_at = datetime.now(timezone.utc)
                await session.commit()
            
            logger.error(f"Platform sync failed for {connection_id}: {str(e)}")
            raise APIIntegrationError(f"Platform sync failed: {str(e)}")
    
    async def _sync_analytics_data(
        self,
        session: AsyncSession,
        connection: PlatformConnection,
        api_client: Any,
        force_full_sync: bool
    ) -> Dict[str, int]:
        """Sync analytics data from platform"""
        
        results = {"processed": 0, "created": 0, "updated": 0, "errors": 0}
        
        # Determine date range for sync
        if force_full_sync or not connection.last_sync_at:
            start_date = datetime.now(timezone.utc) - timedelta(days=365)  # Full year
        else:
            start_date = connection.last_sync_at - timedelta(hours=1)  # Overlap for safety
        
        end_date = datetime.now(timezone.utc)
        
        try:
            if connection.platform == Platform.SPOTIFY:
                analytics_data = await self._fetch_spotify_analytics(
                    api_client, start_date, end_date
                )
            elif connection.platform == Platform.YOUTUBE:
                analytics_data = await self._fetch_youtube_analytics(
                    api_client, start_date, end_date
                )
            elif connection.platform == Platform.INSTAGRAM:
                analytics_data = await self._fetch_instagram_analytics(
                    api_client, start_date, end_date
                )
            elif connection.platform == Platform.TIKTOK:
                analytics_data = await self._fetch_tiktok_analytics(
                    api_client, start_date, end_date
                )
            else:
                logger.warning(f"Analytics sync not implemented for {connection.platform.value}")
                return results
            
            # Process and store analytics data
            for analytics_record in analytics_data:
                try:
                    # Check if record exists
                    existing_record = await self._find_existing_analytics(
                        session, connection.id, analytics_record
                    )
                    
                    if existing_record:
                        # Update existing record
                        await self._update_analytics_record(existing_record, analytics_record)
                        results["updated"] += 1
                    else:
                        # Create new record
                        new_record = PlatformAnalytics(
                            connection_id=connection.id,
                            user_id=connection.user_id,
                            platform=connection.platform,
                            **self._map_analytics_data(analytics_record)
                        )
                        session.add(new_record)
                        results["created"] += 1
                    
                    results["processed"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process analytics record: {str(e)}")
                    results["errors"] += 1
            
            await session.flush()
            
        except Exception as e:
            logger.error(f"Analytics sync failed for {connection.platform.value}: {str(e)}")
            results["errors"] += 1
        
        return results
    
    async def _sync_revenue_data(
        self,
        session: AsyncSession,
        connection: PlatformConnection,
        api_client: Any,
        force_full_sync: bool
    ) -> Dict[str, int]:
        """Sync revenue data from platform"""
        
        results = {"processed": 0, "created": 0, "updated": 0, "errors": 0}
        
        # Determine date range for sync
        if force_full_sync or not connection.last_sync_at:
            start_date = datetime.now(timezone.utc) - timedelta(days=365)
        else:
            start_date = connection.last_sync_at - timedelta(hours=1)
        
        end_date = datetime.now(timezone.utc)
        
        try:
            if connection.platform == Platform.SPOTIFY:
                revenue_data = await self._fetch_spotify_revenue(
                    api_client, start_date, end_date
                )
            elif connection.platform == Platform.YOUTUBE:
                revenue_data = await self._fetch_youtube_revenue(
                    api_client, start_date, end_date
                )
            elif connection.platform == Platform.INSTAGRAM:
                revenue_data = await self._fetch_instagram_revenue(
                    api_client, start_date, end_date
                )
            else:
                logger.warning(f"Revenue sync not implemented for {connection.platform.value}")
                return results
            
            # Process and store revenue data
            for revenue_record in revenue_data:
                try:
                    # Check if record exists
                    existing_record = await self._find_existing_revenue(
                        session, connection.id, revenue_record
                    )
                    
                    if existing_record:
                        # Update existing record
                        await self._update_revenue_record(existing_record, revenue_record)
                        results["updated"] += 1
                    else:
                        # Create new record
                        new_record = PlatformRevenue(
                            connection_id=connection.id,
                            user_id=connection.user_id,
                            platform=connection.platform,
                            **self._map_revenue_data(revenue_record)
                        )
                        session.add(new_record)
                        results["created"] += 1
                    
                    results["processed"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process revenue record: {str(e)}")
                    results["errors"] += 1
            
            await session.flush()
            
        except Exception as e:
            logger.error(f"Revenue sync failed for {connection.platform.value}: {str(e)}")
            results["errors"] += 1
        
        return results
    
    async def _fetch_spotify_analytics(
        self,
        api_client: Any,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch analytics data from Spotify API"""
        
        analytics_data = []
        
        try:
            # Get user's top tracks
            response = await self._make_api_request(
                api_client,
                "/me/top/tracks",
                params={"limit": 50, "time_range": "medium_term"}
            )
            
            if response.success:
                for track in response.data.get("items", []):
                    analytics_data.append({
                        "content_id": track["id"],
                        "content_title": track["name"],
                        "content_type": "track",
                        "metric_type": "popularity",
                        "date": datetime.now(timezone.utc).date(),
                        "period_type": "daily",
                        "views": track.get("popularity", 0),
                        "platform_specific_metrics": {
                            "duration_ms": track.get("duration_ms"),
                            "explicit": track.get("explicit"),
                            "artists": [artist["name"] for artist in track.get("artists", [])]
                        }
                    })
            
            # Get user's recently played tracks
            response = await self._make_api_request(
                api_client,
                "/me/player/recently-played",
                params={"limit": 50}
            )
            
            if response.success:
                for item in response.data.get("items", []):
                    track = item["track"]
                    played_at = datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))
                    
                    if start_date <= played_at <= end_date:
                        analytics_data.append({
                            "content_id": track["id"],
                            "content_title": track["name"],
                            "content_type": "track",
                            "metric_type": "play",
                            "date": played_at.date(),
                            "period_type": "daily",
                            "views": 1,
                            "platform_specific_metrics": {
                                "played_at": played_at.isoformat(),
                                "context": item.get("context")
                            }
                        })
            
        except Exception as e:
            logger.error(f"Failed to fetch Spotify analytics: {str(e)}")
        
        return analytics_data
    
    async def _fetch_youtube_analytics(
        self,
        api_client: Any,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch analytics data from YouTube Analytics API"""
        
        analytics_data = []
        
        try:
            # Get channel analytics
            response = await self._make_api_request(
                api_client,
                "/channels",
                params={
                    "part": "statistics,contentDetails",
                    "mine": "true"
                }
            )
            
            if response.success and response.data.get("items"):
                channel = response.data["items"][0]
                statistics = channel.get("statistics", {})
                
                analytics_data.append({
                    "content_id": channel["id"],
                    "content_title": "Channel Statistics",
                    "content_type": "channel",
                    "metric_type": "channel_stats",
                    "date": datetime.now(timezone.utc).date(),
                    "period_type": "daily",
                    "views": int(statistics.get("viewCount", 0)),
                    "subscriber_count": int(statistics.get("subscriberCount", 0)),
                    "platform_specific_metrics": {
                        "video_count": int(statistics.get("videoCount", 0)),
                        "hidden_subscriber_count": statistics.get("hiddenSubscriberCount", False)
                    }
                })
            
            # Get video analytics (requires YouTube Analytics API)
            # This would require additional API calls to YouTube Analytics API
            # for detailed video-level metrics
            
        except Exception as e:
            logger.error(f"Failed to fetch YouTube analytics: {str(e)}")
        
        return analytics_data
    
    async def _fetch_instagram_analytics(
        self,
        api_client: Any,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch analytics data from Instagram Basic Display API"""
        
        analytics_data = []
        
        try:
            # Get user's media
            response = await self._make_api_request(
                api_client,
                "/me/media",
                params={
                    "fields": "id,caption,media_type,media_url,timestamp,like_count,comments_count",
                    "limit": 100
                }
            )
            
            if response.success:
                for media in response.data.get("data", []):
                    timestamp = datetime.fromisoformat(media["timestamp"].replace("Z", "+00:00"))
                    
                    if start_date <= timestamp <= end_date:
                        analytics_data.append({
                            "content_id": media["id"],
                            "content_title": media.get("caption", "")[:100],
                            "content_type": media.get("media_type", "").lower(),
                            "metric_type": "engagement",
                            "date": timestamp.date(),
                            "period_type": "daily",
                            "likes": media.get("like_count", 0),
                            "comments": media.get("comments_count", 0),
                            "platform_specific_metrics": {
                                "media_url": media.get("media_url"),
                                "timestamp": timestamp.isoformat()
                            }
                        })
            
        except Exception as e:
            logger.error(f"Failed to fetch Instagram analytics: {str(e)}")
        
        return analytics_data
    
    async def _fetch_tiktok_analytics(
        self,
        api_client: Any,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch analytics data from TikTok API"""
        
        analytics_data = []
        
        try:
            # Get user's videos
            response = await self._make_api_request(
                api_client,
                "/video/list/",
                params={
                    "fields": "id,title,create_time,share_count,view_count,like_count,comment_count",
                    "max_count": 20
                }
            )
            
            if response.success:
                for video in response.data.get("videos", []):
                    create_time = datetime.fromtimestamp(video["create_time"], tz=timezone.utc)
                    
                    if start_date <= create_time <= end_date:
                        analytics_data.append({
                            "content_id": video["id"],
                            "content_title": video.get("title", ""),
                            "content_type": "video",
                            "metric_type": "engagement",
                            "date": create_time.date(),
                            "period_type": "daily",
                            "views": video.get("view_count", 0),
                            "likes": video.get("like_count", 0),
                            "comments": video.get("comment_count", 0),
                            "shares": video.get("share_count", 0),
                            "platform_specific_metrics": {
                                "create_time": create_time.isoformat()
                            }
                        })
            
        except Exception as e:
            logger.error(f"Failed to fetch TikTok analytics: {str(e)}")
        
        return analytics_data
    
    async def _make_api_request(
        self,
        api_client: Any,
        endpoint: str,
        method: str = "GET",
        params: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> APIResponse:
        """Make API request with rate limiting and error handling"""
        
        try:
            # Implement rate limiting
            await self._check_rate_limit(api_client.platform)
            
            # Make request
            if isinstance(api_client, httpx.AsyncClient):
                response = await api_client.request(
                    method=method,
                    url=endpoint,
                    params=params,
                    json=data,
                    headers=headers
                )
                
                return APIResponse(
                    success=response.status_code < 400,
                    data=response.json() if response.content else {},
                    status_code=response.status_code,
                    rate_limit_remaining=response.headers.get("X-RateLimit-Remaining"),
                    error_message=response.text if response.status_code >= 400 else None
                )
            
            # Handle other client types (Spotify SDK, etc.)
            # Implementation would depend on the specific client library
            
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            return APIResponse(
                success=False,
                data={},
                status_code=500,
                error_message=str(e)
            )
    
    async def _check_rate_limit(self, platform: Platform):
        """Check and enforce rate limits for platform API"""
        
        config = self.platform_configs.get(platform)
        if not config:
            return
        
        rate_limit = config["rate_limit"]
        current_time = time.time()
        
        # Simple in-memory rate limiting
        # In production, this would use Redis or similar
        if platform not in self.rate_limiters:
            self.rate_limiters[platform] = {
                "requests": [],
                "window_start": current_time
            }
        
        limiter = self.rate_limiters[platform]
        window_size = rate_limit["window"]
        max_requests = rate_limit["requests"]
        
        # Clean old requests outside the window
        limiter["requests"] = [
            req_time for req_time in limiter["requests"]
            if current_time - req_time < window_size
        ]
        
        # Check if we've exceeded the limit
        if len(limiter["requests"]) >= max_requests:
            wait_time = window_size - (current_time - limiter["requests"][0])
            if wait_time > 0:
                logger.warning(f"Rate limit hit for {platform.value}, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
        
        # Add current request
        limiter["requests"].append(current_time)
    
    async def _get_platform_connection(
        self,
        session: AsyncSession,
        connection_id: str
    ) -> Optional[PlatformConnection]:
        """Get platform connection by ID"""
        
        stmt = select(PlatformConnection).where(
            PlatformConnection.id == uuid.UUID(connection_id)
        )
        
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _get_platform_client(self, connection: PlatformConnection) -> Any:
        """
Get authenticated API client for platform"""
        
        # Decrypt access token
        access_token = self.security_manager.decrypt(connection.access_token)
        
        # Create platform-specific client
        config = self.platform_configs[connection.platform]
        
        if connection.platform in [Platform.SPOTIFY, Platform.YOUTUBE, Platform.INSTAGRAM]:
            client = httpx.AsyncClient(
                base_url=config["base_url"],
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
            )
            client.platform = connection.platform
            return client
        
        # Handle other platform-specific clients
        return None
    
    def _calculate_next_sync(self, frequency: DataSyncFrequency) -> datetime:
        """Calculate next synchronization time based on frequency"""
        
        now = datetime.now(timezone.utc)
        
        if frequency == DataSyncFrequency.HOURLY:
            return now + timedelta(hours=1)
        elif frequency == DataSyncFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == DataSyncFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        elif frequency == DataSyncFrequency.MONTHLY:
            return now + timedelta(days=30)
        else:
            return now + timedelta(days=1)  # Default to daily
    
    def _map_analytics_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Map raw API data to standardized analytics format"""
        
        mapped_data = {
            "metric_type": raw_data.get("metric_type", "unknown"),
            "content_id": raw_data.get("content_id"),
            "content_title": raw_data.get("content_title"),
            "content_type": raw_data.get("content_type"),
            "date": raw_data.get("date"),
            "period_type": raw_data.get("period_type", "daily"),
            "views": raw_data.get("views", 0),
            "likes": raw_data.get("likes", 0),
            "comments": raw_data.get("comments", 0),
            "shares": raw_data.get("shares", 0),
            "platform_specific_metrics": raw_data.get("platform_specific_metrics", {})
        }
        
        return {k: v for k, v in mapped_data.items() if v is not None}
    
    def _map_revenue_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map raw API data to standardized revenue format"""
        
        mapped_data = {
            "revenue_stream": raw_data.get("revenue_stream", "unknown"),
            "content_id": raw_data.get("content_id"),
            "content_title": raw_data.get("content_title"),
            "content_type": raw_data.get("content_type"),
            "date": raw_data.get("date"),
            "gross_revenue": Decimal(str(raw_data.get("gross_revenue", 0))),
            "net_revenue": Decimal(str(raw_data.get("net_revenue", 0))),
            "currency": raw_data.get("currency", "EUR"),
            "platform_specific_data": raw_data.get("platform_specific_data", {})
        }
        
        return {k: v for k, v in mapped_data.items() if v is not None}
    
    async def batch_sync_platforms(
        self,
        session: AsyncSession,
        user_id: Optional[str] = None,
        platforms: Optional[List[Platform]] = None,
        sync_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Batch synchronization across multiple platforms"""
        
        # Get connections to sync
        conditions = [PlatformConnection.status == ConnectionStatus.CONNECTED]
        
        if user_id:
            conditions.append(PlatformConnection.user_id == uuid.UUID(user_id))
        
        if platforms:
            conditions.append(PlatformConnection.platform.in_(platforms))
        
        stmt = select(PlatformConnection).where(and_(*conditions))
        result = await session.execute(stmt)
        connections = result.scalars().all()
        
        # Execute syncs in parallel with controlled concurrency
        semaphore = asyncio.Semaphore(5)  # Limit concurrent syncs
        
        async def sync_connection(connection):
        try:
            logger.info(f"Executing sync_connection")
            
            # Implementation for sync_connection
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"sync_connection completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"sync_connection failed: {e}")
            raise
                try:
                    return await self.sync_platform_data(
                        session, str(connection.id), sync_types
                    )
                except Exception as e:
                    logger.error(f"Batch sync failed for {connection.platform.value}: {str(e)}")
                    return {"status": "failed", "error": str(e)}
        
        # Execute all syncs
        sync_tasks = [sync_connection(conn) for conn in connections]
        results = await asyncio.gather(*sync_tasks, return_exceptions=True)
        
        # Compile batch results
        batch_results = {
            "total_connections": len(connections),
            "successful_syncs": 0,
            "failed_syncs": 0,
            "results": {}
        }
        
        for i, result in enumerate(results):
            connection = connections[i]
            platform_key = f"{connection.platform.value}_{connection.platform_user_id}"
            
            if isinstance(result, Exception):
                batch_results["failed_syncs"] += 1
                batch_results["results"][platform_key] = {
                    "status": "failed",
                    "error": str(result)
                }
            elif result.get("status") == "completed":
                batch_results["successful_syncs"] += 1
                batch_results["results"][platform_key] = result
            else:
                batch_results["failed_syncs"] += 1
                batch_results["results"][platform_key] = result
        
        return batch_results
    
    async def get_platform_health_status(
        self,
        session: AsyncSession,
        platform: Optional[Platform] = None
    ) -> Dict[str, Any]:
        """Get health status of platform integrations"""
        
        conditions = []
        if platform:
            conditions.append(PlatformConnection.platform == platform)
        
        stmt = select(PlatformConnection)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        result = await session.execute(stmt)
        connections = result.scalars().all()
        
        health_status = {
            "total_connections": len(connections),
            "by_status": {},
            "by_platform": {},
            "recent_sync_failures": 0,
            "avg_sync_success_rate": 0,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
        # Aggregate status information
        for connection in connections:
            # By status
            status = connection.status.value
            if status not in health_status["by_status"]:
                health_status["by_status"][status] = 0
            health_status["by_status"][status] += 1
            
            # By platform
            platform_name = connection.platform.value
            if platform_name not in health_status["by_platform"]:
                health_status["by_platform"][platform_name] = {
                    "total": 0,
                    "connected": 0,
                    "last_sync": None,
                    "sync_frequency": None
                }
            
            platform_info = health_status["by_platform"][platform_name]
            platform_info["total"] += 1
            
            if connection.status == ConnectionStatus.CONNECTED:
                platform_info["connected"] += 1
            
            if connection.last_sync_at:
                if not platform_info["last_sync"] or connection.last_sync_at > platform_info["last_sync"]:
                    platform_info["last_sync"] = connection.last_sync_at.isoformat()
                    platform_info["sync_frequency"] = connection.sync_frequency.value if connection.sync_frequency else None
        
        return health_status


# Utility functions for API integration
async def refresh_platform_token(
    session: AsyncSession,
    connection_id: str
) -> bool:
    """Refresh expired platform authentication token"""
    
    try:
        connection = await session.get(PlatformConnection, uuid.UUID(connection_id))
        if not connection:
            return False
        
        # Platform-specific token refresh logic
        if connection.platform == Platform.SPOTIFY:
            return await _refresh_spotify_token(connection)
        elif connection.platform == Platform.YOUTUBE:
            return await _refresh_google_token(connection)
        elif connection.platform == Platform.INSTAGRAM:
            return await _refresh_facebook_token(connection)
        
        return False
        
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        return False


async def validate_platform_credentials(
    platform: Platform,
    credentials: Dict[str, str]
) -> bool:
    """Validate platform API credentials"""
    
    try:
        # Platform-specific credential validation
        if platform == Platform.SPOTIFY:
            return await _validate_spotify_credentials(credentials)
        elif platform == Platform.YOUTUBE:
            return await _validate_youtube_credentials(credentials)
        elif platform == Platform.INSTAGRAM:
            return await _validate_instagram_credentials(credentials)
        
        return False
        
    except Exception as e:
        logger.error(f"Credential validation failed: {str(e)}")
        return False


# Export main classes and functions
__all__ = [
    'PlatformAPIIntegrator',
    'APIResponse',
    'refresh_platform_token',
    'validate_platform_credentials'
]
