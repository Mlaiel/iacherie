"""Facebook Platform Integration

Facebook Graph API integration for content sharing and analytics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""import asyncio
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


class FacebookPlatform(PlatformBase):
    """Facebook platform integration"""    
    def __init__(self, config: PlatformConfig):
        """Initialize Facebook platform"""        super().__init__(config)
        self.api_base = "https://graph.facebook.com/v18.0"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Facebook using OAuth2"""        try:
            if self.config.credentials.access_token:
                if await self._validate_token():
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    return True
            
            logger.error("Facebook authentication requires OAuth2 flow or valid access token")
            return False
            
        except Exception as e:
            logger.error(f"Facebook authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Facebook long-lived access token"""        if not self.config.credentials.access_token:
            logger.error("No access token available for Facebook")
            return False
        
        try:
            params = {
                'grant_type': 'fb_exchange_token',
                'client_id': self.config.credentials.client_id,
                'client_secret': self.config.credentials.client_secret,
                'fb_exchange_token': self.config.credentials.access_token
            }
            
            session = await self._get_session()
            async with session.get(f"{self.api_base}/oauth/access_token", params=params) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.config.credentials.access_token = token_data['access_token']
                    
                    expires_in = token_data.get('expires_in', 5184000)  # 60 days default
                    self.config.credentials.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("Facebook token refreshed successfully")
                    return True
                else:
                    logger.error(f"Facebook token refresh failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Facebook token refresh error: {e}")
            return False
    
    async def _validate_token(self) -> bool:
        """Validate Facebook access token"""        try:
            params = {
                'fields': 'id,name',
                'access_token': self.config.credentials.access_token
            }
            
            result = await self._make_request('GET', 'me', params=params)
            return result is not None
            
        except Exception as e:
            logger.error(f"Facebook token validation error: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Facebook API"""        if not self.is_authenticated:
            if not await self.authenticate():
                return None
        
        try:
            session = await self._get_session()
            
            params = kwargs.get('params', {})
            params['access_token'] = self.config.credentials.access_token
            kwargs['params'] = params
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    if await self.refresh_token():
                        params['access_token'] = self.config.credentials.access_token
                        async with session.request(method, url, **kwargs) as retry_response:
                            if retry_response.status == 200:
                                return await retry_response.json()
                    return None
                
                elif response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 200:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Facebook API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Facebook request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload content to Facebook"""        try:
            if not os.path.exists(content_path):
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Content file not found"
                )
            
            mime_type = mimetypes.guess_type(content_path)[0]
            is_video = mime_type and mime_type.startswith('video/')
            is_image = mime_type and mime_type.startswith('image/')
            
            if is_video:
                return await self._upload_video(content_path, metadata)
            elif is_image:
                return await self._upload_photo(content_path, metadata)
            else:
                # Text post
                return await self._create_text_post(metadata)
                
        except Exception as e:
            logger.error(f"Facebook upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def _upload_photo(self, file_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload photo to Facebook"""        try:
            session = await self._get_session()
            
            async with aiofiles.open(file_path, 'rb') as photo_file:
                photo_data = await photo_file.read()
            
            data = aiohttp.FormData()
            data.add_field('source', photo_data, filename=os.path.basename(file_path))
            data.add_field('message', f"{metadata.title}\n\n{metadata.description}")
            data.add_field('access_token', self.config.credentials.access_token)
            
            async with session.post(f"{self.api_base}/me/photos", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    post_id = result.get('post_id')
                    
                    return UploadResult(
                        success=True,
                        platform_id=self.platform_id,
                        content_id=post_id,
                        url=f"https://www.facebook.com/{post_id}",
                        message="Photo uploaded successfully",
                        metadata={
                            'post_id': post_id,
                            'photo_id': result.get('id')
                        }
                    )
                else:
                    error_text = await response.text()
                    return UploadResult(
                        success=False,
                        platform_id=self.platform_id,
                        error=f"Photo upload failed: {error_text}"
                    )
                    
        except Exception as e:
            logger.error(f"Facebook photo upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def _upload_video(self, file_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload video to Facebook"""        try:
            session = await self._get_session()
            
            async with aiofiles.open(file_path, 'rb') as video_file:
                video_data = await video_file.read()
            
            data = aiohttp.FormData()
            data.add_field('source', video_data, filename=os.path.basename(file_path))
            data.add_field('description', f"{metadata.title}\n\n{metadata.description}")
            data.add_field('access_token', self.config.credentials.access_token)
            
            async with session.post(f"{self.api_base}/me/videos", data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    video_id = result.get('id')
                    
                    return UploadResult(
                        success=True,
                        platform_id=self.platform_id,
                        content_id=video_id,
                        url=f"https://www.facebook.com/{video_id}",
                        message="Video uploaded successfully",
                        metadata={
                            'video_id': video_id
                        }
                    )
                else:
                    error_text = await response.text()
                    return UploadResult(
                        success=False,
                        platform_id=self.platform_id,
                        error=f"Video upload failed: {error_text}"
                    )
                    
        except Exception as e:
            logger.error(f"Facebook video upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def _create_text_post(self, metadata: ContentMetadata) -> UploadResult:
        """Create text post on Facebook"""        try:
            data = {
                'message': f"{metadata.title}\n\n{metadata.description}",
                'access_token': self.config.credentials.access_token
            }
            
            result = await self._make_request('POST', 'me/feed', data=data)
            
            if result and result.get('id'):
                post_id = result['id']
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=post_id,
                    url=f"https://www.facebook.com/{post_id}",
                    message="Text post created successfully",
                    metadata={'post_id': post_id}
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Failed to create text post"
                )
                
        except Exception as e:
            logger.error(f"Facebook text post error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Facebook analytics for a post"""        try:
            params = {
                'fields': 'insights.metric(post_impressions,post_engaged_users,post_clicks,post_reactions_like_total,post_reactions_love_total,post_reactions_wow_total,post_reactions_haha_total,post_reactions_sorry_total,post_reactions_anger_total),message,created_time,shares'
            }
            
            result = await self._make_request('GET', content_id, params=params)
            
            if not result:
                raise Exception(f"Post {content_id} not found")
            
            insights_data = {}
            if 'insights' in result and 'data' in result['insights']:
                for insight in result['insights']['data']:
                    metric_name = insight.get('name')
                    metric_values = insight.get('values', [])
                    if metric_values:
                        insights_data[metric_name] = metric_values[0].get('value', 0)
            
            # Calculate total reactions (likes)
            total_reactions = sum([
                insights_data.get('post_reactions_like_total', 0),
                insights_data.get('post_reactions_love_total', 0),
                insights_data.get('post_reactions_wow_total', 0),
                insights_data.get('post_reactions_haha_total', 0),
                insights_data.get('post_reactions_sorry_total', 0),
                insights_data.get('post_reactions_anger_total', 0)
            ])
            
            return AnalyticsData(
                platform_id=self.platform_id,
                content_id=content_id,
                views=insights_data.get('post_impressions', 0),
                likes=total_reactions,
                shares=result.get('shares', {}).get('count', 0),
                comments=0,  # Would need separate API call
                engagement_rate=self._calculate_engagement_rate(insights_data, total_reactions),
                metadata={
                    'message': result.get('message'),
                    'created_time': result.get('created_time'),
                    'post_clicks': insights_data.get('post_clicks', 0),
                    'engaged_users': insights_data.get('post_engaged_users', 0),
                    'reaction_breakdown': {
                        'like': insights_data.get('post_reactions_like_total', 0),
                        'love': insights_data.get('post_reactions_love_total', 0),
                        'wow': insights_data.get('post_reactions_wow_total', 0),
                        'haha': insights_data.get('post_reactions_haha_total', 0),
                        'sorry': insights_data.get('post_reactions_sorry_total', 0),
                        'anger': insights_data.get('post_reactions_anger_total', 0)
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Facebook analytics error: {e}")
            raise
    
    def _calculate_engagement_rate(self, insights_data: Dict[str, Any], total_reactions: int) -> float:
        """Calculate engagement rate"""        impressions = insights_data.get('post_impressions', 0)
        engaged_users = insights_data.get('post_engaged_users', 0)
        
        if impressions == 0:
            return 0.0
        
        return (engaged_users / impressions) * 100
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Facebook (limited by API)"""        # Facebook Graph API doesn't support public content search
        logger.warning("Facebook content search not available with Graph API")
        return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's posts from Facebook"""        try:
            params = {
                'fields': 'id,message,created_time,type,status_type,shares,reactions.summary(true)'
            }
            
            endpoint = f"{user_id}/posts" if user_id else "me/posts"
            result = await self._make_request('GET', endpoint, params=params)
            
            if not result:
                return []
            
            posts = []
            for item in result.get('data', []):
                reactions = item.get('reactions', {}).get('summary', {})
                shares = item.get('shares', {})
                
                posts.append({
                    'id': item.get('id'),
                    'message': item.get('message'),
                    'created_time': item.get('created_time'),
                    'type': item.get('type'),
                    'status_type': item.get('status_type'),
                    'reactions_count': reactions.get('total_count', 0),
                    'shares_count': shares.get('count', 0)
                })
            
            return posts
            
        except Exception as e:
            logger.error(f"Error getting Facebook user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete post from Facebook"""        try:
            result = await self._make_request('DELETE', content_id)
            return result is not None and result.get('success') is True
        except Exception as e:
            logger.error(f"Error deleting Facebook content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update post metadata on Facebook"""        try:
            data = {
                'message': f"{metadata.title}\n\n{metadata.description}"
            }
            
            result = await self._make_request('POST', content_id, data=data)
            return result is not None and result.get('success') is True
            
        except Exception as e:
            logger.error(f"Error updating Facebook content: {e}")
            return False
    
    async def get_page_info(self, page_id: str = None) -> Optional[Dict[str, Any]]:
        """Get page information"""        try:
            params = {
                'fields': 'id,name,about,category,fan_count,followers_count,engagement'
            }
            
            endpoint = page_id if page_id else 'me'
            return await self._make_request('GET', endpoint, params=params)
            
        except Exception as e:
            logger.error(f"Error getting Facebook page info: {e}")
            return None
    
    async def get_post_comments(self, post_id: str) -> List[Dict[str, Any]]:
        """Get comments for a post"""        try:
            params = {
                'fields': 'id,message,created_time,from,like_count'
            }
            
            result = await self._make_request('GET', f"{post_id}/comments", params=params)
            
            if not result:
                return []
            
            return result.get('data', [])
            
        except Exception as e:
            logger.error(f"Error getting Facebook post comments: {e}")
            return []
    
    async def like_post(self, post_id: str) -> bool:
        """Like a post"""        try:
            result = await self._make_request('POST', f"{post_id}/likes")
            return result is not None and result.get('success') is True
        except Exception as e:
            logger.error(f"Error liking Facebook post: {e}")
            return False
    
    async def close(self):
        """Close HTTP session"""        if self.session and not self.session.closed:
            await self.session.close()
