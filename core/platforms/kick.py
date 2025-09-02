"""Kick Platform Integration

Kick.com streaming platform integration.

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

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus
)

logger = logging.getLogger(__name__)


class KickPlatform(PlatformBase):
    """
Kick streaming platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """
        try:
            logger.info(f"Executing __init__")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
Initialize Kick platform"""
        super().__init__(config)
        self.api_base = "https://kick.com/api/v1"
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
Authenticate with Kick"""
        try:
            # Kick uses cookie-based authentication
            username = self.config.credentials.get('username')
            password = self.config.credentials.get('password')
            cookies = self.config.credentials.get('cookies')
            
            if cookies:
                # Use existing cookies
                session = await self._get_session()
                headers = {
                    'Cookie': cookies,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
                
                async with session.get(f"{self.api_base}/user", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        self.config.credentials['user_id'] = str(user_data.get('id'))
                        self.config.credentials['username'] = user_data.get('username')
                        
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info("Kick authentication successful")
                        return True
                    else:
                        logger.error("Kick cookie authentication failed")
                        return False
                        
            elif username and password:
                # Login with credentials
                success = await self._login_with_credentials(username, password)
                if success:
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("Kick login successful")
                    return True
                else:
                    logger.error("Kick login failed")
                    return False
            else:
                logger.error("Kick requires username/password or cookies")
                return False
                
        except Exception as e:
            logger.error(f"Kick authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def _login_with_credentials(self, username: str, password: str) -> bool:
        try:
            logger.info(f"Executing _login_with_credentials")
            
            # Implementation for _login_with_credentials
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"_login_with_credentials completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"_login_with_credentials failed: {e}")
            raise
            session = await self._get_session()
            
            # Get CSRF token first
            async with session.get("https://kick.com/") as response:
                csrf_token = None
                for cookie in response.cookies:
                    if cookie.key == 'XSRF-TOKEN':
                        csrf_token = cookie.value
                        break
                
                if not csrf_token:
                    logger.error("Could not get CSRF token")
                    return False
            
            # Login request
            login_data = {
                'email': username,
                'password': password,
                'one_time_password': ''
            }
            
            headers = {
                'X-XSRF-TOKEN': csrf_token,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with session.post(f"{self.api_base}/login", 
                                  json=login_data, headers=headers) as response:
                if response.status == 200:
                    # Save cookies for future requests
                    cookie_string = "; ".join([f"{cookie.key}={cookie.value}" 
                                             for cookie in session.cookie_jar])
                    self.config.credentials['cookies'] = cookie_string
                    
                    # Get user info
                    user_data = await response.json()
                    self.config.credentials['user_id'] = str(user_data.get('id'))
                    self.config.credentials['username'] = user_data.get('username')
                    return True
                else:
                    logger.error(f"Kick login failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Kick login error: {e}")
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Kick session"""
        return await self.authenticate()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
Make authenticated request to Kick API"""
        try:
            session = await self._get_session()
            
            headers = kwargs.get('headers', {})
            headers.update({
                'Cookie': self.config.credentials.get('cookies', ''),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
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
                    logger.error("Kick authentication failed")
                    self.increment_error_count()
                    return None
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Kick API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Kick request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload content to Kick (clips, highlights)"""
        try:
            # Kick primarily supports live streaming, but we can upload clips
            # This is a placeholder for when Kick adds more upload features
            
            logger.info("Kick is primarily a live streaming platform")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error="Kick doesn't support direct video uploads - use live streaming instead"
            )
                
        except Exception as e:
            logger.error(f"Kick upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def start_stream(self, title: str, category_id: int, thumbnail_path: str = None) -> Optional[Dict[str, Any]]:
        """Start a live stream on Kick"""
        try:
            stream_data = {
                'title': title,
                'category_id': category_id,
                'is_mature': False
            }
            
            # Upload thumbnail if provided
            if thumbnail_path:
                thumbnail_url = await self._upload_thumbnail(thumbnail_path)
                if thumbnail_url:
                    stream_data['thumbnail'] = thumbnail_url
            
            result = await self._make_request('POST', '/streams', json=stream_data)
            
            if result:
                return {
                    'stream_key': result.get('stream_key'),
                    'server_url': result.get('server_url', 'rtmp://ingest.kick.com/live/'),
                    'stream_id': result.get('id'),
                    'title': result.get('title'),
                    'category_id': result.get('category_id'),
                    'is_live': result.get('is_live', False)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error starting stream: {e}")
            return None
    
    async def _upload_thumbnail(self, thumbnail_path: str) -> Optional[str]:
        """Upload stream thumbnail"""
        try:
            session = await self._get_session()
            
            data = aiohttp.FormData()
            with open(thumbnail_path, 'rb') as f:
                data.add_field('thumbnail', f, filename='thumbnail.jpg', 
                             content_type='image/jpeg')
                
                headers = {
                    'Cookie': self.config.credentials.get('cookies', ''),
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.post(f"{self.api_base}/upload/thumbnail", 
                                      data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('url')
                    else:
                        logger.error(f"Thumbnail upload failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Thumbnail upload error: {e}")
            return None
    
    async def get_analytics(self, content_id: str, start_date: datetime, 
                           end_date: datetime) -> AnalyticsData:
        """Get Kick stream analytics"""
        try:
            result = await self._make_request('GET', f'/streams/{content_id}')
            
            if result:
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=result.get('viewer_count', 0),
                    likes=0,  # Kick doesn't have likes for streams
                    shares=0,  # Not available
                    comments=result.get('chatters_count', 0),
                    metadata={
                        'duration': result.get('duration'),
                        'peak_viewers': result.get('peak_viewers', 0),
                        'average_viewers': result.get('average_viewers', 0),
                        'chatters_count': result.get('chatters_count', 0),
                        'followers_gained': result.get('followers_gained', 0),
                        'category': result.get('category', {}).get('name'),
                        'language': result.get('language'),
                        'is_mature': result.get('is_mature', False)
                    }
                )
            else:
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id
                )
                
        except Exception as e:
            logger.error(f"Kick analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Kick"""
        try:
            params = {
                'query': query,
                'limit': 20
            }
            
            result = await self._make_request('GET', '/search/channels', params=params)
            
            if result:
                channels = []
                for channel in result:
                    channels.append({
                        'id': channel.get('id'),
                        'username': channel.get('username'),
                        'display_name': channel.get('display_name'),
                        'avatar': channel.get('user', {}).get('profile_pic'),
                        'followers_count': channel.get('followers_count', 0),
                        'is_live': channel.get('livestream') is not None,
                        'category': channel.get('livestream', {}).get('category', {}).get('name') if channel.get('livestream') else None,
                        'viewer_count': channel.get('livestream', {}).get('viewer_count', 0) if channel.get('livestream') else 0
                    })
                return channels
            
            return []
            
        except Exception as e:
            logger.error(f"Kick search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's Kick streams/content"""
        try:
            target_username = self.config.credentials.get('username')
            if user_id:
                # Get username from user_id
                user_info = await self._make_request('GET', f'/users/{user_id}')
                if user_info:
                    target_username = user_info.get('username')
                else:
                    return []
            
            if not target_username:
                return []
            
            result = await self._make_request('GET', f'/channels/{target_username}')
            
            if result:
                streams = []
                
                # Current/recent livestreams
                if result.get('livestream'):
                    livestream = result['livestream']
                    streams.append({
                        'id': livestream.get('id'),
                        'title': livestream.get('session_title'),
                        'thumbnail': livestream.get('thumbnail', {}).get('url'),
                        'created_at': livestream.get('created_at'),
                        'duration': livestream.get('duration'),
                        'viewer_count': livestream.get('viewer_count', 0),
                        'category': livestream.get('category', {}).get('name'),
                        'language': livestream.get('language'),
                        'is_live': True,
                        'is_mature': livestream.get('is_mature', False)
                    })
                
                # Get previous streams if available
                previous_streams = await self._make_request('GET', f'/channels/{target_username}/livestreams')
                if previous_streams and previous_streams.get('data'):
                    for stream in previous_streams['data']:
                        streams.append({
                            'id': stream.get('id'),
                            'title': stream.get('session_title'),
                            'thumbnail': stream.get('thumbnail', {}).get('url'),
                            'created_at': stream.get('created_at'),
                            'duration': stream.get('duration'),
                            'viewer_count': stream.get('viewer_count', 0),
                            'category': stream.get('category', {}).get('name'),
                            'language': stream.get('language'),
                            'is_live': False,
                            'is_mature': stream.get('is_mature', False)
                        })
                
                return streams
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Kick user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Kick content (limited support)"""
        try:
            logger.warning("Kick has limited content deletion support")
            return False
                
        except Exception as e:
            logger.error(f"Error deleting Kick content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update Kick stream info"""
        try:
            update_data = {
                'title': metadata.title,
                'category_id': metadata.category_id if hasattr(metadata, 'category_id') else None
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            result = await self._make_request('PUT', f'/streams/{content_id}', json=update_data)
            return result is not None
                
        except Exception as e:
            logger.error(f"Error updating Kick content: {e}")
            return False
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get Kick stream categories"""
        try:
            result = await self._make_request('GET', '/categories')
            
            if result:
                categories = []
                for category in result:
                    categories.append({
                        'id': category.get('id'),
                        'name': category.get('name'),
                        'slug': category.get('slug'),
                        'icon': category.get('icon'),
                        'viewers': category.get('viewers', 0),
                        'tags': category.get('tags', [])
                    })
                return categories
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    async def get_channel_info(self, username: str = None) -> Optional[Dict[str, Any]]:
        """Get channel information"""
        try:
            target_username = username or self.config.credentials.get('username')
            if not target_username:
                return None
            
            result = await self._make_request('GET', f'/channels/{target_username}')
            
            if result:
                user = result.get('user', {})
                return {
                    'id': result.get('id'),
                    'username': result.get('username'),
                    'display_name': user.get('username'),
                    'bio': user.get('bio'),
                    'profile_pic': user.get('profile_pic'),
                    'banner': result.get('banner'),
                    'followers_count': result.get('followers_count', 0),
                    'is_live': result.get('livestream') is not None,
                    'verified': result.get('verified', False),
                    'vod_enabled': result.get('vod_enabled', False),
                    'subscription_enabled': result.get('subscription_enabled', False),
                    'can_host': result.get('can_host', False),
                    'chatroom': result.get('chatroom', {})
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            return None
    
    async def follow_channel(self, username: str) -> bool:
        """Follow a channel"""
        try:
            result = await self._make_request('POST', f'/channels/{username}/follow')
            return result is not None
            
        except Exception as e:
            logger.error(f"Error following channel: {e}")
            return False
    
    async def unfollow_channel(self, username: str) -> bool:
        """Unfollow a channel"""
        try:
            result = await self._make_request('DELETE', f'/channels/{username}/follow')
            return result is not None
            
        except Exception as e:
            logger.error(f"Error unfollowing channel: {e}")
            return False
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
