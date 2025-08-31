"""
Instagram Platform Integration

Complete Instagram Basic Display API integration for content sharing and analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import aiohttp
import aiofiles
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import json
import mimetypes
import os

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus
)

logger = logging.getLogger(__name__)


class InstagramPlatform(PlatformBase):
    """Instagram platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """Initialize Instagram platform"""
        super().__init__(config)
        self.api_base = "https://graph.facebook.com/v18.0"
        self.auth_base = "https://api.instagram.com"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Instagram using OAuth2"""



        try:
            # If we have a long-lived token, validate it
            if self.config.credentials.access_token:
                if await self._validate_token():
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    return True
            
            # For initial authentication, would need OAuth2 flow
            logger.error("Instagram authentication requires OAuth2 flow or valid access token")
            return False
            
        except Exception as e:
            logger.error(f"Instagram authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Instagram long-lived access token"""
        if not self.config.credentials.access_token:
            logger.error("No access token available for Instagram")
            return False
        
        try:
            session = await self._get_session()
            
            params = {
                'grant_type': 'ig_refresh_token',
                'access_token': self.config.credentials.access_token
            }
            
            async with session.get(
                f"{self.api_base}/refresh_access_token",
                params=params
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.config.credentials.access_token = token_data['access_token']
                    
                    expires_in = token_data.get('expires_in', 5184000)  # 60 days default
                    self.config.credentials.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("Instagram token refreshed successfully")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Instagram token refresh failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Instagram token refresh error: {e}")
            return False
    
    async def _validate_token(self) -> bool:
        """Validate Instagram access token"""



        try:
            params = {
                'fields': 'id,username',
                'access_token': self.config.credentials.access_token
            }
            
            result = await self._make_request('GET', 'me', params=params)
            return result is not None
            
        except Exception as e:
            logger.error(f"Instagram token validation error: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Instagram API"""
        if not self.is_authenticated:
            if not await self.authenticate():
                return None
        
        try:
            session = await self._get_session()
            
            # Add access token to params
            params = kwargs.get('params', {})
            params['access_token'] = self.config.credentials.access_token
            kwargs['params'] = params
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    # Token expired or invalid
                    if await self.refresh_token():
                        params['access_token'] = self.config.credentials.access_token
                        async with session.request(method, url, **kwargs) as retry_response:
                            if retry_response.status == 200:
                                return await retry_response.json()
                    return None
                
                elif response.status == 429:
                    # Rate limited
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 200:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Instagram API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Instagram request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload content to Instagram"""



        try:
            if not os.path.exists(content_path):
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Content file not found"
                )
            
            # Determine content type
            mime_type = mimetypes.guess_type(content_path)[0]
            is_video = mime_type and mime_type.startswith('video/')
            
            # Step 1: Create media container
            media_type = 'VIDEO' if is_video else 'IMAGE'
            
            container_data = {
                'image_url' if not is_video else 'video_url': content_path,  # This would need to be a public URL
                'caption': f"{metadata.title}\n\n{metadata.description}\n\n{' '.join(f'#{tag}' for tag in metadata.tags)}",
                'media_type': media_type
            }
            
            # Note: Instagram requires media to be uploaded to a publicly accessible URL first
            # This is a limitation of the Instagram Basic Display API
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error="Instagram API requires media to be hosted on a public URL. Direct file upload not supported."
            )
            
        except Exception as e:
            logger.error(f"Instagram upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def upload_from_url(self, media_url: str, metadata: ContentMetadata) -> UploadResult:
        """Upload content to Instagram from a public URL"""



        try:
            # Determine if it's a video or image
            mime_type = mimetypes.guess_type(media_url)[0]
            is_video = mime_type and mime_type.startswith('video/')
            media_type = 'VIDEO' if is_video else 'IMAGE'
            
            # Step 1: Create media container
            container_params = {
                'image_url' if not is_video else 'video_url': media_url,
                'caption': f"{metadata.title}\n\n{metadata.description}\n\n{' '.join(f'#{tag}' for tag in metadata.tags)}",
                'media_type': media_type
            }
            
            container_result = await self._make_request(
                'POST',
                'me/media',
                params=container_params
            )
            
            if not container_result:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Failed to create media container"
                )
            
            container_id = container_result.get('id')
            
            # Step 2: Publish the media
            publish_params = {
                'creation_id': container_id
            }
            
            publish_result = await self._make_request(
                'POST',
                'me/media_publish',
                params=publish_params
            )
            
            if not publish_result:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Failed to publish media"
                )
            
            media_id = publish_result.get('id')
            
            return UploadResult(
                success=True,
                platform_id=self.platform_id,
                content_id=media_id,
                url=f"https://www.instagram.com/p/{media_id}/",
                message="Content uploaded successfully",
                metadata={
                    'media_id': media_id,
                    'media_type': media_type,
                    'container_id': container_id
                }
            )
            
        except Exception as e:
            logger.error(f"Instagram upload from URL error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Instagram analytics for a media"""



        try:
            # Get media insights
            insights_params = {
                'metric': 'engagement,impressions,reach,saved'
            }
            
            insights_result = await self._make_request(
                'GET',
                f"{content_id}/insights",
                params=insights_params
            )
            
            # Get basic media info
            media_params = {
                'fields': 'id,media_type,media_url,permalink,timestamp,caption,like_count,comments_count'
            }
            
            media_result = await self._make_request(
                'GET',
                content_id,
                params=media_params
            )
            
            if not media_result:
                raise Exception(f"Media {content_id} not found")
            
            # Process insights data
            insights_data = {}
            if insights_result and 'data' in insights_result:
                for insight in insights_result['data']:
                    metric_name = insight.get('name')
                    metric_values = insight.get('values', [])
                    if metric_values:
                        insights_data[metric_name] = metric_values[0].get('value', 0)
            
            return AnalyticsData(
                platform_id=self.platform_id,
                content_id=content_id,
                views=0,  # Not available in basic insights
                likes=media_result.get('like_count', 0),
                shares=0,  # Not available
                comments=media_result.get('comments_count', 0),
                reach=insights_data.get('reach', 0),
                impressions=insights_data.get('impressions', 0),
                engagement_rate=self._calculate_engagement_rate(media_result, insights_data),
                metadata={
                    'media_type': media_result.get('media_type'),
                    'media_url': media_result.get('media_url'),
                    'permalink': media_result.get('permalink'),
                    'timestamp': media_result.get('timestamp'),
                    'caption': media_result.get('caption'),
                    'saved': insights_data.get('saved', 0),
                    'engagement': insights_data.get('engagement', 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Instagram analytics error: {e}")
            raise
    
    def _calculate_engagement_rate(self, media_data: Dict[str, Any], insights_data: Dict[str, Any]) -> float:
        """Calculate engagement rate"""
        likes = media_data.get('like_count', 0)
        comments = media_data.get('comments_count', 0)
        impressions = insights_data.get('impressions', 0)
        
        if impressions == 0:
            return 0.0
        
        return ((likes + comments) / impressions) * 100
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Instagram (limited by API)"""
        # Instagram Basic Display API doesn't support content search
        # This would require Instagram Graph API with appropriate permissions
        logger.warning("Instagram content search not available with Basic Display API")
        return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's media from Instagram"""



        try:
            params = {
                'fields': 'id,media_type,media_url,permalink,thumbnail_url,timestamp,caption,like_count,comments_count'
            }
            
            endpoint = f"{user_id}/media" if user_id else "me/media"
            result = await self._make_request('GET', endpoint, params=params)
            
            if not result:
                return []
            
            media_list = []
            for item in result.get('data', []):
                media_list.append({
                    'id': item.get('id'),
                    'media_type': item.get('media_type'),
                    'media_url': item.get('media_url'),
                    'thumbnail_url': item.get('thumbnail_url'),
                    'permalink': item.get('permalink'),
                    'timestamp': item.get('timestamp'),
                    'caption': item.get('caption'),
                    'like_count': item.get('like_count'),
                    'comments_count': item.get('comments_count')
                })
            
            return media_list
            
        except Exception as e:
            logger.error(f"Error getting Instagram user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete media from Instagram"""



        try:
            result = await self._make_request('DELETE', content_id)
            return result is not None
        except Exception as e:
            logger.error(f"Error deleting Instagram content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update media metadata on Instagram (very limited)"""
        # Instagram API doesn't allow updating media content or captions
        # Only some fields can be updated on certain media types
        logger.warning("Instagram API doesn't support updating media content")
        return False
    
    async def get_user_info(self, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get user information"""



        try:
            params = {
                'fields': 'id,username,account_type,media_count'
            }
            
            endpoint = user_id if user_id else 'me'
            return await self._make_request('GET', endpoint, params=params)
            
        except Exception as e:
            logger.error(f"Error getting Instagram user info: {e}")
            return None
    
    async def get_media_comments(self, media_id: str) -> List[Dict[str, Any]]:
        """Get comments for a media"""



        try:
            params = {
                'fields': 'id,text,timestamp,username'
            }
            
            result = await self._make_request(
                'GET',
                f"{media_id}/comments",
                params=params
            )
            
            if not result:
                return []
            
            return result.get('data', [])
            
        except Exception as e:
            logger.error(f"Error getting Instagram media comments: {e}")
            return []
    
    async def get_hashtag_media(self, hashtag: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get recent media for a hashtag (requires Instagram Graph API)"""
        # This requires Instagram Graph API and specific permissions
        logger.warning("Hashtag media search requires Instagram Graph API")
        return []
    
    async def get_account_insights(self, period: str = "day") -> Dict[str, Any]:
        """Get account insights"""



        try:
            params = {
                'metric': 'impressions,reach,profile_views,website_clicks',
                'period': period
            }
            
            result = await self._make_request(
                'GET',
                'me/insights',
                params=params
            )
            
            if not result:
                return {}
            
            insights = {}
            for insight in result.get('data', []):
                metric_name = insight.get('name')
                metric_values = insight.get('values', [])
                if metric_values:
                    insights[metric_name] = metric_values[0].get('value', 0)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting Instagram account insights: {e}")
            return {}
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
