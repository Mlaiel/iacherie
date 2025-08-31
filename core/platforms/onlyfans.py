"""OnlyFans Platform Integration

OnlyFans API integration for content creator platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""import asyncio
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


class OnlyFansPlatform(PlatformBase):
    """OnlyFans platform integration"""    
    def __init__(self, config: PlatformConfig):
        """Initialize OnlyFans platform"""        super().__init__(config)
        self.api_base = "https://onlyfans.com/api2/v2"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with OnlyFans"""        try:
            # OnlyFans uses cookie-based authentication
            cookie = self.config.credentials.get('cookie')
            x_bc = self.config.credentials.get('x_bc')
            user_agent = self.config.credentials.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            if cookie and x_bc:
                session = await self._get_session()
                headers = {
                    'Cookie': cookie,
                    'X-BC': x_bc,
                    'User-Agent': user_agent,
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                async with session.get(f"{self.api_base}/users/me", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        self.config.credentials['user_id'] = str(user_data.get('id'))
                        self.config.credentials['username'] = user_data.get('username')
                        
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info("OnlyFans authentication successful")
                        return True
                    else:
                        logger.error("OnlyFans authentication failed")
                        return False
            else:
                logger.error("OnlyFans requires cookie and x_bc credentials")
                return False
                
        except Exception as e:
            logger.error(f"OnlyFans authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh OnlyFans session"""        return await self.authenticate()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to OnlyFans API"""        try:
            session = await self._get_session()
            
            headers = kwargs.get('headers', {})
            headers.update({
                'Cookie': self.config.credentials.get('cookie', ''),
                'X-BC': self.config.credentials.get('x_bc', ''),
                'User-Agent': self.config.credentials.get('user_agent', 'Mozilla/5.0'),
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            })
            
            kwargs['headers'] = headers
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 401:
                    logger.error("OnlyFans authentication failed")
                    self.increment_error_count()
                    return None
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"OnlyFans API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"OnlyFans request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload content to OnlyFans"""        try:
            media_ids = []
            
            # Upload media first if file provided
            if content_path and os.path.exists(content_path):
                media_id = await self._upload_media(content_path)
                if media_id:
                    media_ids.append(media_id)
            
            # Create post
            post_data = {
                'text': metadata.description or metadata.title or '',
                'medias': media_ids,
                'price': metadata.price if hasattr(metadata, 'price') else None,
                'isScheduled': False,
                'scheduleDate': None,
                'canComment': True,
                'isProfileTeasers': False
            }
            
            # Remove None values
            post_data = {k: v for k, v in post_data.items() if v is not None}
            
            result = await self._make_request('POST', '/posts', json=post_data)
            
            if result:
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=str(result.get('id')),
                    url=f"https://onlyfans.com/{self.config.credentials.get('username')}/{result.get('id')}",
                    metadata={
                        'text': result.get('text'),
                        'price': result.get('price'),
                        'created_at': result.get('createdAt'),
                        'likes_count': result.get('likesCount', 0),
                        'comments_count': result.get('commentsCount', 0),
                        'tips_amount': result.get('tipsAmount', 0),
                        'media_count': len(result.get('media', []))
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="OnlyFans post creation failed"
                )
                
        except Exception as e:
            logger.error(f"OnlyFans upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def _upload_media(self, file_path: str) -> Optional[str]:
        """Upload media file to OnlyFans"""        try:
            session = await self._get_session()
            
            # Get upload policy
            headers = {
                'Cookie': self.config.credentials.get('cookie', ''),
                'X-BC': self.config.credentials.get('x_bc', ''),
                'User-Agent': self.config.credentials.get('user_agent', 'Mozilla/5.0')
            }
            
            async with session.get(f"{self.api_base}/upload/policy", headers=headers) as response:
                if response.status != 200:
                    return None
                    
                policy_data = await response.json()
            
            # Upload file
            data = aiohttp.FormData()
            with open(file_path, 'rb') as f:
                filename = os.path.basename(file_path)
                data.add_field('file', f, filename=filename)
                
                # Add policy fields
                for field in policy_data.get('fields', []):
                    data.add_field(field['name'], field['value'])
                
                async with session.post(policy_data['url'], data=data) as upload_response:
                    if upload_response.status == 200:
                        upload_result = await upload_response.json()
                        return upload_result.get('id')
                    else:
                        logger.error(f"OnlyFans media upload failed: {upload_response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"OnlyFans media upload error: {e}")
            return None
    
    async def get_analytics(self, content_id: str, start_date: datetime, 
                           end_date: datetime) -> AnalyticsData:
        """Get OnlyFans post analytics"""        try:
            result = await self._make_request('GET', f'/posts/{content_id}')
            
            if result:
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=result.get('viewsCount', 0),
                    likes=result.get('likesCount', 0),
                    shares=0,  # Not available
                    comments=result.get('commentsCount', 0),
                    metadata={
                        'tips_amount': result.get('tipsAmount', 0),
                        'tips_count': result.get('tipsCount', 0),
                        'bookmarks_count': result.get('bookmarksCount', 0),
                        'price': result.get('price'),
                        'earnings': result.get('earnings', 0),
                        'created_at': result.get('createdAt')
                    }
                )
            else:
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id
                )
                
        except Exception as e:
            logger.error(f"OnlyFans analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on OnlyFans"""        try:
            params = {
                'query': query,
                'type': 'all'  # users, posts
            }
            
            result = await self._make_request('GET', '/search', params=params)
            
            if result and result.get('list'):
                content = []
                for item in result['list']:
                    content.append({
                        'id': item.get('id'),
                        'text': item.get('text'),
                        'created_at': item.get('createdAt'),
                        'author': {
                            'id': item.get('author', {}).get('id'),
                            'username': item.get('author', {}).get('username'),
                            'name': item.get('author', {}).get('name')
                        },
                        'likes_count': item.get('likesCount', 0),
                        'comments_count': item.get('commentsCount', 0),
                        'price': item.get('price')
                    })
                return content
            
            return []
            
        except Exception as e:
            logger.error(f"OnlyFans search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's OnlyFans posts"""        try:
            target_user_id = user_id or self.config.credentials.get('user_id')
            if not target_user_id:
                return []
            
            params = {
                'limit': 50,
                'offset': 0,
                'order': 'publish_date_desc'
            }
            
            result = await self._make_request('GET', f'/users/{target_user_id}/posts', params=params)
            
            if result and result.get('list'):
                posts = []
                for post in result['list']:
                    posts.append({
                        'id': post.get('id'),
                        'text': post.get('text'),
                        'created_at': post.get('createdAt'),
                        'price': post.get('price'),
                        'likes_count': post.get('likesCount', 0),
                        'comments_count': post.get('commentsCount', 0),
                        'tips_amount': post.get('tipsAmount', 0),
                        'media': post.get('media', []),
                        'is_pinned': post.get('isPinned', False),
                        'can_comment': post.get('canComment', True)
                    })
                return posts
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting OnlyFans user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete OnlyFans post"""        try:
            result = await self._make_request('DELETE', f'/posts/{content_id}')
            return result is not None
                
        except Exception as e:
            logger.error(f"Error deleting OnlyFans content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update OnlyFans post"""        try:
            update_data = {
                'text': metadata.description or metadata.title or '',
                'price': metadata.price if hasattr(metadata, 'price') else None
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            result = await self._make_request('PUT', f'/posts/{content_id}', json=update_data)
            return result is not None
                
        except Exception as e:
            logger.error(f"Error updating OnlyFans content: {e}")
            return False
    
    async def get_earnings(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get earnings data"""        try:
            params = {}
            if start_date:
                params['startDate'] = start_date.isoformat()
            if end_date:
                params['endDate'] = end_date.isoformat()
            
            result = await self._make_request('GET', '/earnings', params=params)
            
            if result:
                return {
                    'total_earnings': result.get('totalEarnings', 0),
                    'subscriptions': result.get('subscriptions', 0),
                    'tips': result.get('tips', 0),
                    'messages': result.get('messages', 0),
                    'posts': result.get('posts', 0),
                    'referrals': result.get('referrals', 0),
                    'streams': result.get('streams', 0)
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting earnings: {e}")
            return {}
    
    async def get_subscribers(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get subscriber list"""        try:
            params = {
                'limit': limit,
                'offset': 0,
                'type': 'active'
            }
            
            result = await self._make_request('GET', '/subscriptions/subscribers', params=params)
            
            if result and result.get('list'):
                subscribers = []
                for subscriber in result['list']:
                    user = subscriber.get('user', {})
                    subscribers.append({
                        'id': user.get('id'),
                        'username': user.get('username'),
                        'name': user.get('name'),
                        'avatar': user.get('avatar'),
                        'subscribed_at': subscriber.get('subscribedAt'),
                        'expires_at': subscriber.get('expiredAt'),
                        'price': subscriber.get('price'),
                        'is_active': subscriber.get('isActive', True)
                    })
                return subscribers
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting subscribers: {e}")
            return []
    
    async def send_message(self, user_id: str, text: str, media_ids: List[str] = None) -> Optional[str]:
        """Send private message"""        try:
            message_data = {
                'text': text,
                'lockedText': '',
                'media': media_ids or [],
                'price': None,
                'isCouplePeopleMedia': False,
                'previews': []
            }
            
            result = await self._make_request('POST', f'/chats/{user_id}/messages', json=message_data)
            
            if result:
                return str(result.get('id'))
            
            return None
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    async def get_messages(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get messages with user"""        try:
            params = {
                'limit': limit,
                'offset': 0,
                'order': 'desc'
            }
            
            result = await self._make_request('GET', f'/chats/{user_id}/messages', params=params)
            
            if result and result.get('list'):
                messages = []
                for message in result['list']:
                    messages.append({
                        'id': message.get('id'),
                        'text': message.get('text'),
                        'created_at': message.get('createdAt'),
                        'from_user': message.get('fromUser', {}).get('id'),
                        'price': message.get('price'),
                        'is_opened': message.get('isOpened', False),
                        'media': message.get('media', [])
                    })
                return messages
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting messages: {e}")
            return []
    
    async def close(self):
        """Close HTTP session"""        if self.session and not self.session.closed:
            await self.session.close()
