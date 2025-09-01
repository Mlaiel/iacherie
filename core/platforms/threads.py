"""Threads Platform Integration

Meta Threads API integration for text-based conversations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import json
import os

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus
)

logger = logging.getLogger(__name__)


class ThreadsPlatform(PlatformBase):
    """
Meta Threads platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """
Initialize Threads platform"""
        super().__init__(config)
        self.api_base = "https://graph.threads.net/v1.0"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """
Authenticate with Threads API"""
        try:
            access_token = self.config.credentials.get('access_token')
            
            if access_token:
                session = await self._get_session()
                params = {
                    'fields': 'id,username,account_type,name,profile_picture_url',
                    'access_token': access_token
                }
                
                async with session.get(f"{self.api_base}/me", params=params) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        self.config.credentials['user_id'] = user_data.get('id')
                        self.config.credentials['username'] = user_data.get('username')
                        
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info("Threads authentication successful")
                        return True
                    else:
                        logger.error("Threads token validation failed")
                        return False
            else:
                logger.error("Threads requires access_token")
                return False
                
        except Exception as e:
            logger.error(f"Threads authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Threads token"""
        try:
            access_token = self.config.credentials.get('access_token')
            if not access_token:
                return False
            
            session = await self._get_session()
            params = {
                'grant_type': 'th_refresh_token',
                'access_token': access_token
            }
            
            async with session.get(f"{self.api_base}/refresh_access_token", params=params) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.config.credentials['access_token'] = token_data.get('access_token')
                    return True
                else:
                    logger.error("Threads token refresh failed")
                    return False
                    
        except Exception as e:
            logger.error(f"Threads token refresh error: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Threads API"""
        try:
            session = await self._get_session()
            
            # Add access token to params for Threads API
            params = kwargs.get('params', {})
            params['access_token'] = self.config.credentials.get('access_token')
            kwargs['params'] = params
            
            headers = kwargs.get('headers', {})
            headers['Content-Type'] = 'application/json'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 401:
                    # Try to refresh token
                    if await self.refresh_token():
                        params['access_token'] = self.config.credentials.get('access_token')
                        kwargs['params'] = params
                        return await self._make_request(method, endpoint, **kwargs)
                    else:
                        logger.error("Threads authentication failed")
                        self.increment_error_count()
                        return None
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Threads API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Threads request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Create Threads post"""
        try:
            user_id = self.config.credentials.get('user_id')
            if not user_id:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="User ID not found"
                )
            
            media_id = None
            media_type = 'TEXT'
            
            # Handle media upload if file provided
            if content_path and os.path.exists(content_path):
                media_id = await self._upload_media(content_path)
                if media_id:
                    # Determine media type based on file extension
                    if content_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        media_type = 'IMAGE'
                    elif content_path.lower().endswith(('.mp4', '.mov', '.avi')):
                        media_type = 'VIDEO'
            
            # Step 1: Create media container
            container_data = {
                'media_type': media_type,
                'text': metadata.description or metadata.title or ""
            }
            
            if media_id:
                if media_type == 'IMAGE':
                    container_data['image_url'] = media_id
                elif media_type == 'VIDEO':
                    container_data['video_url'] = media_id
            
            # Add hashtags
            if metadata.tags:
                text_with_tags = container_data['text']
                hashtags = [f"#{tag.replace(' ', '').replace('#', '')}" for tag in metadata.tags]
                container_data['text'] = f"{text_with_tags}\n\n{' '.join(hashtags)}"
            
            # Threads text limit is 500 characters
            if len(container_data['text']) > 500:
                container_data['text'] = container_data['text'][:497] + "..."
            
            container_result = await self._make_request('POST', f'/{user_id}/threads', json=container_data)
            
            if not container_result or not container_result.get('id'):
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Failed to create media container"
                )
            
            container_id = container_result['id']
            
            # Step 2: Publish the container
            publish_data = {
                'creation_id': container_id
            }
            
            publish_result = await self._make_request('POST', f'/{user_id}/threads_publish', json=publish_data)
            
            if publish_result and publish_result.get('id'):
                thread_id = publish_result['id']
                
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=thread_id,
                    url=f"https://threads.net/@{self.config.credentials.get('username')}/post/{thread_id}",
                    metadata={
                        'container_id': container_id,
                        'media_type': media_type,
                        'text': container_data['text'],
                        'permalink': f"https://threads.net/@{self.config.credentials.get('username')}/post/{thread_id}"
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Failed to publish Threads post"
                )
                
        except Exception as e:
            logger.error(f"Threads upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def _upload_media(self, file_path: str) -> Optional[str]:
        """Upload media file and return URL"""
        try:
            # For Threads, we need to upload to a hosting service first
            # This is a placeholder - in real implementation, you'd upload to
            # a service like AWS S3, Cloudinary, etc.
            
            # For now, return a placeholder URL
            filename = os.path.basename(file_path)
            return f"https://example.com/uploads/{filename}"
            
        except Exception as e:
            logger.error(f"Threads media upload error: {e}")
            return None
    
    async def get_analytics(self, content_id: str, start_date: datetime, 
                           end_date: datetime) -> AnalyticsData:
        """Get Threads post analytics"""
        try:
            params = {
                'fields': 'id,media_product_type,media_type,media_url,permalink,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post'
            }
            
            result = await self._make_request('GET', f'/{content_id}', params=params)
            
            if result:
                # Get insights (requires business account)
                insights_params = {
                    'metric': 'views,likes,replies,reposts,quotes'
                }
                
                insights_result = await self._make_request('GET', f'/{content_id}/insights', 
                                                         params=insights_params)
                
                views = 0
                likes = 0
                replies = 0
                reposts = 0
                quotes = 0
                
                if insights_result and insights_result.get('data'):
                    for insight in insights_result['data']:
                        metric_name = insight.get('name')
                        value = insight.get('values', [{}])[0].get('value', 0)
                        
                        if metric_name == 'views':
                            views = value
                        elif metric_name == 'likes':
                            likes = value
                        elif metric_name == 'replies':
                            replies = value
                        elif metric_name == 'reposts':
                            reposts = value
                        elif metric_name == 'quotes':
                            quotes = value
                
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=views,
                    likes=likes,
                    shares=reposts + quotes,
                    comments=replies,
                    metadata={
                        'reposts': reposts,
                        'quotes': quotes,
                        'replies': replies,
                        'media_type': result.get('media_type'),
                        'timestamp': result.get('timestamp'),
                        'permalink': result.get('permalink'),
                        'is_quote_post': result.get('is_quote_post', False)
                    }
                )
            else:
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id
                )
                
        except Exception as e:
            logger.error(f"Threads analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Threads (limited API support)"""
        try:
            # Threads search API is limited - placeholder implementation
            logger.warning("Threads search API has limited public access")
            return []
            
        except Exception as e:
            logger.error(f"Threads search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's Threads posts"""
        try:
            target_user_id = user_id or self.config.credentials.get('user_id')
            if not target_user_id:
                return []
            
            params = {
                'fields': 'id,media_product_type,media_type,media_url,permalink,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post',
                'limit': 25
            }
            
            result = await self._make_request('GET', f'/{target_user_id}/threads', params=params)
            
            if result and result.get('data'):
                threads = []
                for thread in result['data']:
                    threads.append({
                        'id': thread.get('id'),
                        'text': thread.get('text'),
                        'media_type': thread.get('media_type'),
                        'media_url': thread.get('media_url'),
                        'permalink': thread.get('permalink'),
                        'timestamp': thread.get('timestamp'),
                        'shortcode': thread.get('shortcode'),
                        'thumbnail_url': thread.get('thumbnail_url'),
                        'is_quote_post': thread.get('is_quote_post', False),
                        'children': thread.get('children', [])
                    })
                return threads
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Threads user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Threads post (not supported via API)"""
        try:
            logger.warning("Threads doesn't support post deletion via API")
            return False
                
        except Exception as e:
            logger.error(f"Error deleting Threads content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update Threads post (not supported via API)"""
        try:
            logger.warning("Threads doesn't support post editing via API")
            return False
                
        except Exception as e:
            logger.error(f"Error updating Threads content: {e}")
            return False
    
    async def reply_to_thread(self, thread_id: str, text: str, media_path: str = None) -> Optional[str]:
        """Reply to a thread"""
        try:
            user_id = self.config.credentials.get('user_id')
            if not user_id:
                return None
            
            reply_data = {
                'media_type': 'TEXT',
                'text': text,
                'reply_to_id': thread_id
            }
            
            if media_path and os.path.exists(media_path):
                media_url = await self._upload_media(media_path)
                if media_url:
                    if media_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        reply_data['media_type'] = 'IMAGE'
                        reply_data['image_url'] = media_url
                    elif media_path.lower().endswith(('.mp4', '.mov', '.avi')):
                        reply_data['media_type'] = 'VIDEO'
                        reply_data['video_url'] = media_url
            
            # Create container
            container_result = await self._make_request('POST', f'/{user_id}/threads', json=reply_data)
            
            if container_result and container_result.get('id'):
                container_id = container_result['id']
                
                # Publish reply
                publish_data = {
                    'creation_id': container_id
                }
                
                publish_result = await self._make_request('POST', f'/{user_id}/threads_publish', 
                                                        json=publish_data)
                
                if publish_result and publish_result.get('id'):
                    return publish_result['id']
            
            return None
            
        except Exception as e:
            logger.error(f"Error replying to thread: {e}")
            return None
    
    async def get_thread_conversation(self, thread_id: str) -> List[Dict[str, Any]]:
        """Get thread conversation/replies"""
        try:
            params = {
                'fields': 'id,text,timestamp,username,media_type,media_url,children'
            }
            
            result = await self._make_request('GET', f'/{thread_id}/conversation', params=params)
            
            if result and result.get('data'):
                conversation = []
                for reply in result['data']:
                    conversation.append({
                        'id': reply.get('id'),
                        'text': reply.get('text'),
                        'timestamp': reply.get('timestamp'),
                        'username': reply.get('username'),
                        'media_type': reply.get('media_type'),
                        'media_url': reply.get('media_url'),
                        'children': reply.get('children', [])
                    })
                return conversation
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting thread conversation: {e}")
            return []
    
    async def get_user_profile(self, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        try:
            target_user_id = user_id or self.config.credentials.get('user_id')
            if not target_user_id:
                return None
            
            params = {
                'fields': 'id,username,account_type,name,biography,profile_picture_url,followers_count,media_count'
            }
            
            result = await self._make_request('GET', f'/{target_user_id}', params=params)
            
            if result:
                return {
                    'id': result.get('id'),
                    'username': result.get('username'),
                    'name': result.get('name'),
                    'biography': result.get('biography'),
                    'profile_picture_url': result.get('profile_picture_url'),
                    'account_type': result.get('account_type'),
                    'followers_count': result.get('followers_count', 0),
                    'media_count': result.get('media_count', 0)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
