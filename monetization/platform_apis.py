"""
Platform APIs Manager
Integration with various platform APIs for monetization data.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class PlatformCredentials:
    """Platform API credentials structure"""
    platform: str
    access_token: str
    refresh_token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = None


@dataclass
class PlatformAnalytics:
    """Platform analytics data structure"""
    platform: str
    content_id: str
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    revenue: float = 0.0
    engagement_rate: float = 0.0
    timestamp: datetime = None


class PlatformAPIManager:
    """Manages integrations with platform APIs"""
    
    def __init__(self):
        self.session = None
        self.rate_limits = {}
        self.cache = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def authenticate_youtube(
        self,
        client_id: str,
        client_secret: str,
        authorization_code: str
    ) -> PlatformCredentials:
        """Authenticate with YouTube API"""



        try:
            token_url = "https://oauth2.googleapis.com/token"
            
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": authorization_code,
                "grant_type": "authorization_code",
                "redirect_uri": "urn:ietf:wg:oauth:2.0:oob"
            }
            
            async with self.session.post(token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    
                    return PlatformCredentials(
                        platform="youtube",
                        access_token=token_data["access_token"],
                        refresh_token=token_data.get("refresh_token"),
                        client_id=client_id,
                        client_secret=client_secret,
                        expires_at=datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600)),
                        scopes=["https://www.googleapis.com/auth/youtube.readonly", 
                               "https://www.googleapis.com/auth/yt-analytics.readonly"]
                    )
                else:
                    logger.error(f"YouTube authentication failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error authenticating YouTube: {str(e)}")
            return None
    
    async def get_youtube_analytics(
        self,
        credentials: PlatformCredentials,
        channel_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[PlatformAnalytics]:
        """Get YouTube analytics data"""



        try:
            if not await self._check_rate_limit("youtube"):
                logger.warning("YouTube rate limit exceeded")
                return None
                
            # Refresh token if needed
            if credentials.expires_at and datetime.now() >= credentials.expires_at:
                credentials = await self._refresh_youtube_token(credentials)
                
            base_url = "https://youtubeanalytics.googleapis.com/v2/reports"
            
            params = {
                "ids": f"channel=={channel_id}",
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d"),
                "metrics": "views,likes,shares,comments,estimatedMinutesWatched,estimatedRevenue",
                "dimensions": "day"
            }
            
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Accept": "application/json"
            }
            
            async with self.session.get(base_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Process analytics data
                    rows = data.get("rows", [])
                    if rows:
                        totals = {
                            "views": sum(row[1] for row in rows),
                            "likes": sum(row[2] for row in rows),
                            "shares": sum(row[3] for row in rows),
                            "comments": sum(row[4] for row in rows),
                            "watch_time_minutes": sum(row[5] for row in rows),
                            "revenue": sum(row[6] for row in rows) if len(rows[0]) > 6 else 0.0
                        }
                        
                        engagement_rate = (totals["likes"] + totals["shares"] + totals["comments"]) / max(totals["views"], 1)
                        
                        return PlatformAnalytics(
                            platform="youtube",
                            content_id=channel_id,
                            views=totals["views"],
                            likes=totals["likes"],
                            shares=totals["shares"],
                            comments=totals["comments"],
                            revenue=totals["revenue"],
                            engagement_rate=engagement_rate,
                            timestamp=datetime.now()
                        )
                else:
                    logger.error(f"YouTube Analytics API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting YouTube analytics: {str(e)}")
            return None
    
    async def authenticate_instagram(
        self,
        access_token: str
    ) -> PlatformCredentials:
        """Authenticate with Instagram Basic Display API"""



        try:
            # Validate token
            validate_url = f"https://graph.instagram.com/me?fields=id,username&access_token={access_token}"
            
            async with self.session.get(validate_url) as response:
                if response.status == 200:
                    user_data = await response.json()
                    
                    return PlatformCredentials(
                        platform="instagram",
                        access_token=access_token,
                        scopes=["user_profile", "user_media"]
                    )
                else:
                    logger.error(f"Instagram token validation failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error authenticating Instagram: {str(e)}")
            return None
    
    async def get_instagram_insights(
        self,
        credentials: PlatformCredentials,
        user_id: str
    ) -> Optional[PlatformAnalytics]:
        """Get Instagram insights data"""



        try:
            if not await self._check_rate_limit("instagram"):
                logger.warning("Instagram rate limit exceeded")
                return None
                
            # Get recent media
            media_url = f"https://graph.instagram.com/{user_id}/media"
            params = {
                "fields": "id,media_type,timestamp,insights.metric(impressions,reach,likes,comments,shares)",
                "access_token": credentials.access_token,
                "limit": 25
            }
            
            async with self.session.get(media_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    media_items = data.get("data", [])
                    
                    total_stats = {
                        "views": 0,  # Impressions
                        "reach": 0,
                        "likes": 0,
                        "comments": 0,
                        "shares": 0
                    }
                    
                    for item in media_items:
                        insights = item.get("insights", {}).get("data", [])
                        for insight in insights:
                            metric = insight.get("name")
                            value = insight.get("values", [{}])[0].get("value", 0)
                            
                            if metric == "impressions":
                                total_stats["views"] += value
                            elif metric == "reach":
                                total_stats["reach"] += value
                            elif metric == "likes":
                                total_stats["likes"] += value
                            elif metric == "comments":
                                total_stats["comments"] += value
                            elif metric == "shares":
                                total_stats["shares"] += value
                    
                    engagement_rate = (total_stats["likes"] + total_stats["comments"] + total_stats["shares"]) / max(total_stats["views"], 1)
                    
                    return PlatformAnalytics(
                        platform="instagram",
                        content_id=user_id,
                        views=total_stats["views"],
                        likes=total_stats["likes"],
                        shares=total_stats["shares"],
                        comments=total_stats["comments"],
                        engagement_rate=engagement_rate,
                        timestamp=datetime.now()
                    )
                else:
                    logger.error(f"Instagram Insights API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting Instagram insights: {str(e)}")
            return None
    
    async def authenticate_tiktok(
        self,
        client_id: str,
        client_secret: str,
        authorization_code: str
    ) -> PlatformCredentials:
        """Authenticate with TikTok API"""



        try:
            token_url = "https://open-api.tiktok.com/oauth/access_token/"
            
            data = {
                "client_key": client_id,
                "client_secret": client_secret,
                "code": authorization_code,
                "grant_type": "authorization_code"
            }
            
            async with self.session.post(token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    
                    if token_data.get("data"):
                        return PlatformCredentials(
                            platform="tiktok",
                            access_token=token_data["data"]["access_token"],
                            refresh_token=token_data["data"].get("refresh_token"),
                            client_id=client_id,
                            client_secret=client_secret,
                            expires_at=datetime.now() + timedelta(seconds=token_data["data"].get("expires_in", 3600)),
                            scopes=["user.info.basic", "video.list"]
                        )
                else:
                    logger.error(f"TikTok authentication failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error authenticating TikTok: {str(e)}")
            return None
    
    async def authenticate_spotify(
        self,
        client_id: str,
        client_secret: str,
        authorization_code: str
    ) -> PlatformCredentials:
        """Authenticate with Spotify Web API"""



        try:
            token_url = "https://accounts.spotify.com/api/token"
            
            import base64
            credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
            
            headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": "http://localhost:8000/callback"
            }
            
            async with self.session.post(token_url, headers=headers, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    
                    return PlatformCredentials(
                        platform="spotify",
                        access_token=token_data["access_token"],
                        refresh_token=token_data.get("refresh_token"),
                        client_id=client_id,
                        client_secret=client_secret,
                        expires_at=datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600)),
                        scopes=token_data.get("scope", "").split()
                    )
                else:
                    logger.error(f"Spotify authentication failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error authenticating Spotify: {str(e)}")
            return None
    
    async def get_spotify_analytics(
        self,
        credentials: PlatformCredentials,
        artist_id: str
    ) -> Optional[PlatformAnalytics]:
        """Get Spotify analytics data"""



        try:
            if not await self._check_rate_limit("spotify"):
                logger.warning("Spotify rate limit exceeded")
                return None
                
            # Get artist's top tracks
            tracks_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
            params = {"market": "US"}
            
            headers = {
                "Authorization": f"Bearer {credentials.access_token}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(tracks_url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    tracks = data.get("tracks", [])
                    
                    total_popularity = sum(track.get("popularity", 0) for track in tracks)
                    
                    # Note: Spotify doesn't provide actual play counts or revenue through the Web API
                    # This would require Spotify for Artists API access
                    estimated_streams = total_popularity * 1000  # Rough estimation
                    
                    return PlatformAnalytics(
                        platform="spotify",
                        content_id=artist_id,
                        views=estimated_streams,  # Using "views" as streams
                        likes=0,  # Not available via Web API
                        shares=0,  # Not available via Web API
                        comments=0,  # Not available via Web API
                        engagement_rate=0.0,
                        timestamp=datetime.now()
                    )
                else:
                    logger.error(f"Spotify API error: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting Spotify analytics: {str(e)}")
            return None
    
    async def _check_rate_limit(self, platform: str) -> bool:
        """Check if platform rate limit allows request"""
        now = datetime.now()
        
        if platform not in self.rate_limits:
            self.rate_limits[platform] = {
                "requests": 0,
                "reset_time": now + timedelta(hours=1)
            }
            
        rate_info = self.rate_limits[platform]
        
        # Reset if time window passed
        if now >= rate_info["reset_time"]:
            rate_info["requests"] = 0
            rate_info["reset_time"] = now + timedelta(hours=1)
            
        # Platform-specific limits
        limits = {
            "youtube": 10000,  # Per day
            "instagram": 200,  # Per hour
            "tiktok": 1000,    # Per day
            "spotify": 100     # Per hour
        }
        
        if rate_info["requests"] >= limits.get(platform, 100):
            return False
            
        rate_info["requests"] += 1
        return True
    
    async def _refresh_youtube_token(self, credentials: PlatformCredentials) -> PlatformCredentials:
        """Refresh YouTube access token"""



        try:
            token_url = "https://oauth2.googleapis.com/token"
            
            data = {
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "refresh_token": credentials.refresh_token,
                "grant_type": "refresh_token"
            }
            
            async with self.session.post(token_url, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    
                    credentials.access_token = token_data["access_token"]
                    credentials.expires_at = datetime.now() + timedelta(seconds=token_data.get("expires_in", 3600))
                    
                    return credentials
                else:
                    logger.error(f"Token refresh failed: {response.status}")
                    return credentials
                    
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return credentials
    
    async def get_aggregated_analytics(
        self,
        platform_credentials: Dict[str, PlatformCredentials],
        content_mappings: Dict[str, str]  # platform -> content_id
    ) -> Dict[str, PlatformAnalytics]:
        """Get analytics from all connected platforms"""



        try:
            results = {}
            tasks = []
            
            for platform, credentials in platform_credentials.items():
                content_id = content_mappings.get(platform)
                if not content_id:
                    continue
                    
                if platform == "youtube":
                    task = self.get_youtube_analytics(
                        credentials, content_id, 
                        datetime.now() - timedelta(days=30),
                        datetime.now()
                    )
                elif platform == "instagram":
                    task = self.get_instagram_insights(credentials, content_id)
                elif platform == "spotify":
                    task = self.get_spotify_analytics(credentials, content_id)
                else:
                    continue
                    
                tasks.append((platform, task))
            
            # Execute all requests concurrently
            for platform, task in tasks:
                try:
                    result = await task
                    if result:
                        results[platform] = result
                except Exception as e:
                    logger.error(f"Error getting {platform} analytics: {str(e)}")
                    
            return results
            
        except Exception as e:
            logger.error(f"Error getting aggregated analytics: {str(e)}")
            return {}
    
    def cache_analytics_data(self, data: PlatformAnalytics, ttl_hours: int = 1):
        """Cache analytics data"""
        cache_key = f"{data.platform}_{data.content_id}_{datetime.now().strftime('%Y%m%d%H')}"
        expiry = datetime.now() + timedelta(hours=ttl_hours)
        
        self.cache[cache_key] = {
            "data": asdict(data),
            "expires": expiry
        }
    
    def get_cached_analytics(self, platform: str, content_id: str) -> Optional[PlatformAnalytics]:
        """Get cached analytics data"""
        cache_key = f"{platform}_{content_id}_{datetime.now().strftime('%Y%m%d%H')}"
        
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if datetime.now() < cached["expires"]:
                return PlatformAnalytics(**cached["data"])
                
        return None