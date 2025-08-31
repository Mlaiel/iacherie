"""TikTok Platform Integration

TikTok API integration for content sharing and analytics.

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
import hashlib
import hmac
import time
import urllib.parse

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus
)

logger = logging.getLogger(__name__)


class TikTokPlatform(PlatformBase):
    """TikTok platform integration"""    
    def __init__(self, config: PlatformConfig):
        """Initialize TikTok platform"""        super().__init__(config)
        self.api_base = "https://open-api.tiktok.com"
        self.auth_base = "https://www.tiktok.com"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with TikTok using OAuth2"""        try:
            # If we have an access token, validate it
            if self.config.credentials.access_token:
                if await self._validate_token():
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    return True
            
            # For initial authentication, would need OAuth2 flow
            logger.error("TikTok authentication requires OAuth2 flow or valid access token")
            return False
            
        except Exception as e:
            logger.error(f"TikTok authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh TikTok access token"""        if not self.config.credentials.refresh_token:
            logger.error("No refresh token available for TikTok")
            return False
        
        try:
            session = await self._get_session()
            
            data = {
                'client_key': self.config.credentials.client_id,
                'client_secret': self.config.credentials.client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': self.config.credentials.refresh_token
            }
            
            async with session.post(
                f"{self.api_base}/oauth/refresh_token/",
                json=data
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    
                    if token_data.get('data'):
                        self.config.credentials.access_token = token_data['data']['access_token']
                        self.config.credentials.refresh_token = token_data['data']['refresh_token']
                        
                        expires_in = token_data['data'].get('expires_in', 86400)
                        self.config.credentials.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                        
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info("TikTok token refreshed successfully")
                        return True
                    else:
                        logger.error(f"TikTok token refresh failed: {token_data}")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"TikTok token refresh failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"TikTok token refresh error: {e}")
            return False
    
    async def _validate_token(self) -> bool:
        """Validate TikTok access token"""        try:
            result = await self._make_request('POST', '/user/info/')
            return result is not None and result.get('data') is not None
            
        except Exception as e:
            logger.error(f"TikTok token validation error: {e}")
            return False
    
    def _generate_signature(self, params: Dict[str, Any], body: str = "") -> str:
        """Generate signature for TikTok API request"""        # Sort parameters
        sorted_params = sorted(params.items())
        query_string = urllib.parse.urlencode(sorted_params)
        
        # Create string to sign
        string_to_sign = query_string + body
        
        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.config.credentials.client_secret.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to TikTok API"""        if not self.is_authenticated:
            if not await self.authenticate():
                return None
        
        try:
            session = await self._get_session()
            
            # Prepare headers
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.config.credentials.access_token}'
            headers['Content-Type'] = 'application/json'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}{endpoint}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    # Token expired, try to refresh
                    if await self.refresh_token():
                        headers['Authorization'] = f'Bearer {self.config.credentials.access_token}'
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
                    logger.error(f"TikTok API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"TikTok request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload video content to TikTok"""        try:
            if not os.path.exists(content_path):
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Content file not found"
                )
            
            # Step 1: Initialize upload
            init_data = {
                'source_info': {
                    'source': 'FILE_UPLOAD',
                    'video_size': os.path.getsize(content_path)
                }
            }
            
            init_result = await self._make_request(
                'POST',
                '/share/video/upload/init/',
                json=init_data
            )
            
            if not init_result or not init_result.get('data'):
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Failed to initialize upload"
                )
            
            upload_url = init_result['data']['upload_url']
            upload_id = init_result['data']['upload_id']
            
            # Step 2: Upload video file
            async with aiofiles.open(content_path, 'rb') as video_file:
                video_content = await video_file.read()
                
                session = await self._get_session()
                async with session.put(upload_url, data=video_content) as upload_response:
                    if upload_response.status not in [200, 201]:
                        return UploadResult(
                            success=False,
                            platform_id=self.platform_id,
                            error="Failed to upload video file"
                        )
            
            # Step 3: Create post
            post_data = {
                'source_info': {
                    'source': 'FILE_UPLOAD',
                    'upload_id': upload_id
                },
                'post_info': {
                    'title': metadata.title,
                    'description': metadata.description,
                    'privacy_level': 'SELF_ONLY',  # Can be made configurable
                    'disable_duet': False,
                    'disable_comment': False,
                    'disable_stitch': False,
                    'video_cover_timestamp_ms': 1000
                }
            }
            
            post_result = await self._make_request(
                'POST',
                '/share/video/upload/',
                json=post_data
            )
            
            if not post_result or not post_result.get('data'):
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Failed to create post"
                )
            
            share_id = post_result['data']['share_id']
            
            return UploadResult(
                success=True,
                platform_id=self.platform_id,
                content_id=share_id,
                url=f"https://www.tiktok.com/@username/video/{share_id}",  # Would need actual username
                message="Video uploaded successfully",
                metadata={
                    'share_id': share_id,
                    'upload_id': upload_id,
                    'status': post_result['data'].get('status')
                }
            )
            
        except Exception as e:
            logger.error(f"TikTok upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get TikTok analytics for a video"""        try:
            # Get video info
            video_data = {
                'fields': ['id', 'create_time', 'cover_image_url', 'share_url', 'view_count', 'like_count', 'comment_count', 'share_count']
            }
            
            video_result = await self._make_request(
                'POST',
                f'/video/query/?video_id={content_id}',
                json=video_data
            )
            
            if not video_result or not video_result.get('data', {}).get('videos'):
                raise Exception(f"Video {content_id} not found")
            
            video = video_result['data']['videos'][0]
            
            return AnalyticsData(
                platform_id=self.platform_id,
                content_id=content_id,
                views=video.get('view_count', 0),
                likes=video.get('like_count', 0),
                shares=video.get('share_count', 0),
                comments=video.get('comment_count', 0),
                engagement_rate=self._calculate_engagement_rate(video),
                metadata={
                    'create_time': video.get('create_time'),
                    'cover_image_url': video.get('cover_image_url'),
                    'share_url': video.get('share_url'),
                    'video_id': video.get('id')
                }
            )
            
        except Exception as e:
            logger.error(f"TikTok analytics error: {e}")
            raise
    
    def _calculate_engagement_rate(self, video_data: Dict[str, Any]) -> float:
        """Calculate engagement rate"""        views = video_data.get('view_count', 0)
        likes = video_data.get('like_count', 0)
        comments = video_data.get('comment_count', 0)
        shares = video_data.get('share_count', 0)
        
        if views == 0:
            return 0.0
        
        return ((likes + comments + shares) / views) * 100
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on TikTok"""        try:
            search_data = {
                'query': query,
                'search_id': str(int(time.time())),
                'cursor': 0,
                'count': 20
            }
            
            result = await self._make_request(
                'POST',
                '/research/video/query/',
                json=search_data
            )
            
            if not result or not result.get('data'):
                return []
            
            videos = []
            for video in result['data'].get('videos', []):
                videos.append({
                    'id': video.get('id'),
                    'create_time': video.get('create_time'),
                    'username': video.get('username'),
                    'region_code': video.get('region_code'),
                    'video_description': video.get('video_description'),
                    'music_id': video.get('music_id'),
                    'like_count': video.get('like_count'),
                    'comment_count': video.get('comment_count'),
                    'share_count': video.get('share_count'),
                    'view_count': video.get('view_count')
                })
            
            return videos
            
        except Exception as e:
            logger.error(f"TikTok search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's videos from TikTok"""        try:
            video_data = {
                'fields': ['id', 'create_time', 'cover_image_url', 'share_url', 'view_count', 'like_count', 'comment_count', 'share_count']
            }
            
            result = await self._make_request(
                'POST',
                '/video/list/',
                json=video_data
            )
            
            if not result or not result.get('data'):
                return []
            
            videos = []
            for video in result['data'].get('videos', []):
                videos.append({
                    'id': video.get('id'),
                    'create_time': video.get('create_time'),
                    'cover_image_url': video.get('cover_image_url'),
                    'share_url': video.get('share_url'),
                    'view_count': video.get('view_count'),
                    'like_count': video.get('like_count'),
                    'comment_count': video.get('comment_count'),
                    'share_count': video.get('share_count')
                })
            
            return videos
            
        except Exception as e:
            logger.error(f"Error getting TikTok user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete video from TikTok"""        try:
            delete_data = {
                'video_id': content_id
            }
            
            result = await self._make_request(
                'POST',
                '/video/delete/',
                json=delete_data
            )
            
            return result is not None and result.get('error', {}).get('code') == 'ok'
            
        except Exception as e:
            logger.error(f"Error deleting TikTok content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update video metadata on TikTok (limited support)"""        # TikTok API has limited support for updating video metadata
        logger.warning("TikTok API has limited support for updating video metadata")
        return False
    
    async def get_user_info(self, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get user information"""        try:
            user_data = {
                'fields': ['open_id', 'union_id', 'avatar_url', 'display_name', 'bio_description', 'profile_deep_link', 'is_verified', 'follower_count', 'following_count', 'likes_count', 'video_count']
            }
            
            return await self._make_request('POST', '/user/info/', json=user_data)
            
        except Exception as e:
            logger.error(f"Error getting TikTok user info: {e}")
            return None
    
    async def get_video_comments(self, video_id: str, cursor: int = 0, count: int = 20) -> List[Dict[str, Any]]:
        """Get comments for a video"""        try:
            comment_data = {
                'video_id': video_id,
                'cursor': cursor,
                'count': count
            }
            
            result = await self._make_request(
                'POST',
                '/video/comment/list/',
                json=comment_data
            )
            
            if not result or not result.get('data'):
                return []
            
            return result['data'].get('comments', [])
            
        except Exception as e:
            logger.error(f"Error getting TikTok video comments: {e}")
            return []
    
    async def get_trending_videos(self, cursor: int = 0, count: int = 20) -> List[Dict[str, Any]]:
        """Get trending videos"""        try:
            trending_data = {
                'cursor': cursor,
                'count': count
            }
            
            result = await self._make_request(
                'POST',
                '/research/trending/video/',
                json=trending_data
            )
            
            if not result or not result.get('data'):
                return []
            
            return result['data'].get('videos', [])
            
        except Exception as e:
            logger.error(f"Error getting TikTok trending videos: {e}")
            return []
    
    async def close(self):
        """Close HTTP session"""        if self.session and not self.session.closed:
            await self.session.close()
