"""
BeReal Platform Integration

BeReal API integration for authentic social sharing.

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


class BeRealPlatform(PlatformBase):
    """BeReal platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """Initialize BeReal platform"""
        super().__init__(config)
        self.api_base = "https://mobile.bereal.com/api"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # BeReal specific settings
        self.app_version = "0.31.0"
        self.device_id = config.credentials.get('device_id', 'default_device_id')
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with BeReal"""
        try:
            # Note: BeReal has no official public API
            # This is a placeholder implementation for when/if they provide one
            
            phone_number = self.config.credentials.get('phone_number')
            verification_code = self.config.credentials.get('verification_code')
            refresh_token = self.config.credentials.get('refresh_token')
            
            if refresh_token:
                # Try to use existing refresh token
                success = await self._refresh_with_token(refresh_token)
                if success:
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("BeReal authentication successful (refresh token)")
                    return True
            
            if phone_number and verification_code:
                # Phone verification flow
                success = await self._authenticate_with_phone(phone_number, verification_code)
                if success:
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("BeReal authentication successful (phone)")
                    return True
            
            logger.warning("BeReal API not officially available - using placeholder implementation")
            self.status = PlatformStatus.LIMITED
            return False
                
        except Exception as e:
            logger.error(f"BeReal authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def _refresh_with_token(self, refresh_token: str) -> bool:
        """Refresh BeReal token"""
        try:
            session = await self._get_session()
            
            headers = {
                'bereal-app-version-code': '14549',
                'bereal-signature': 'placeholder_signature',
                'bereal-device-id': self.device_id,
                'bereal-timezone': 'Europe/Berlin',
                'Content-Type': 'application/json'
            }
            
            data = {
                'grant_type': 'refresh_token',
                'client_id': 'android',
                'client_secret': '',
                'refresh_token': refresh_token
            }
            
            async with session.post(f"{self.api_base}/auth/refresh", 
                                  json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self.config.credentials['access_token'] = result.get('access_token')
                    self.config.credentials['refresh_token'] = result.get('refresh_token')
                    self.config.credentials['user_id'] = result.get('user_id')
                    return True
                else:
                    logger.error(f"BeReal token refresh failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"BeReal token refresh error: {e}")
            return False
    
    async def _authenticate_with_phone(self, phone_number: str, verification_code: str) -> bool:
        """Authenticate with phone number"""
        try:
            # Step 1: Request verification code
            await self._send_verification_code(phone_number)
            
            # Step 2: Verify code and get tokens
            session = await self._get_session()
            
            headers = {
                'bereal-app-version-code': '14549',
                'bereal-signature': 'placeholder_signature',
                'bereal-device-id': self.device_id,
                'Content-Type': 'application/json'
            }
            
            data = {
                'phoneNumber': phone_number,
                'verificationCode': verification_code
            }
            
            async with session.post(f"{self.api_base}/auth/verify", 
                                  json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    self.config.credentials['access_token'] = result.get('token')
                    self.config.credentials['refresh_token'] = result.get('refreshToken')
                    self.config.credentials['user_id'] = result.get('userId')
                    return True
                else:
                    logger.error(f"BeReal phone verification failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"BeReal phone authentication error: {e}")
            return False
    
    async def _send_verification_code(self, phone_number: str) -> bool:
        """Send verification code to phone"""
        try:
            session = await self._get_session()
            
            headers = {
                'bereal-app-version-code': '14549',
                'bereal-signature': 'placeholder_signature',
                'bereal-device-id': self.device_id,
                'Content-Type': 'application/json'
            }
            
            data = {'phoneNumber': phone_number}
            
            async with session.post(f"{self.api_base}/auth/send-code", 
                                  json=data, headers=headers) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"Error sending verification code: {e}")
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh BeReal token"""
        refresh_token = self.config.credentials.get('refresh_token')
        if refresh_token:
            return await self._refresh_with_token(refresh_token)
        return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to BeReal API"""
        try:
            session = await self._get_session()
            
            headers = kwargs.get('headers', {})
            if self.config.credentials.get('access_token'):
                headers['Authorization'] = f'Bearer {self.config.credentials["access_token"]}'
            
            headers.update({
                'bereal-app-version-code': '14549',
                'bereal-signature': 'placeholder_signature',
                'bereal-device-id': self.device_id,
                'bereal-timezone': 'Europe/Berlin',
                'User-Agent': 'BeReal/1.0 CFNetwork/1240.0.4 Darwin/20.6.0'
            })
            
            kwargs['headers'] = headers
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 401:
                    logger.error("BeReal authentication failed")
                    self.increment_error_count()
                    return None
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"BeReal API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"BeReal request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload BeReal post"""
        try:
            # BeReal requires both front and back camera photos
            # For now, we'll use a placeholder implementation
            
            if not os.path.exists(content_path):
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="BeReal requires image file"
                )
            
            # Upload media first
            media_data = await self._upload_media(content_path, metadata.description)
            if not media_data:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Media upload failed"
                )
            
            # Create BeReal post
            post_data = {
                'backCamera': {
                    'bucket': media_data.get('bucket'),
                    'height': media_data.get('height', 1920),
                    'width': media_data.get('width', 1080),
                    'path': media_data.get('path')
                },
                'frontCamera': {
                    'bucket': media_data.get('bucket'),
                    'height': media_data.get('height', 1920),
                    'width': media_data.get('width', 1080),
                    'path': media_data.get('path')  # Using same image for both cameras
                },
                'location': {
                    'latitude': 52.5200,  # Berlin coordinates as placeholder
                    'longitude': 13.4050
                },
                'caption': metadata.description or '',
                'visibility': ['friends'],  # friends, discovery
                'late': False,
                'retakeCounter': 0
            }
            
            result = await self._make_request('POST', '/content/posts', json=post_data)
            
            if result:
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=result.get('id'),
                    url=f"https://bereal.com/post/{result.get('id')}",
                    metadata={
                        'creation_date': result.get('creationDate'),
                        'late': result.get('isLate', False),
                        'retake_counter': result.get('retakeCounter', 0),
                        'location': result.get('location'),
                        'real_moji_count': result.get('realMojis', {}).get('total', 0),
                        'comment_count': result.get('comment', 0)
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="BeReal post creation failed"
                )
                
        except Exception as e:
            logger.error(f"BeReal upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def _upload_media(self, file_path: str, description: str = None) -> Optional[Dict[str, Any]]:
        """Upload media to BeReal"""
        try:
            # Get upload URL
            session = await self._get_session()
            headers = {
                'Authorization': f'Bearer {self.config.credentials["access_token"]}',
                'Content-Type': 'application/json'
            }
            
            async with session.post(f"{self.api_base}/content/posts/upload-url", 
                                  headers=headers) as response:
                if response.status != 200:
                    return None
                
                upload_data = await response.json()
                
            # Upload file to the provided URL
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            async with session.put(upload_data['url'], data=file_data) as response:
                if response.status == 200:
                    return {
                        'bucket': upload_data.get('bucket'),
                        'path': upload_data.get('path'),
                        'width': 1080,  # Default values
                        'height': 1920
                    }
                
            return None
            
        except Exception as e:
            logger.error(f"BeReal media upload error: {e}")
            return None
    
    async def get_analytics(self, content_id: str, start_date: datetime, 
                           end_date: datetime) -> AnalyticsData:
        """Get BeReal post analytics"""
        try:
            result = await self._make_request('GET', f'/content/posts/{content_id}')
            
            if result:
                real_mojis = result.get('realMojis', {})
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=0,  # Not available
                    likes=real_mojis.get('total', 0),  # RealMojis count
                    shares=0,  # Not applicable
                    comments=result.get('comment', 0),
                    metadata={
                        'real_mojis': real_mojis.get('total', 0),
                        'comments': result.get('comment', 0),
                        'creation_date': result.get('creationDate'),
                        'is_late': result.get('isLate', False),
                        'retake_counter': result.get('retakeCounter', 0),
                        'screenshot_count': result.get('screenshotCount', 0)
                    }
                )
            else:
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id
                )
                
        except Exception as e:
            logger.error(f"BeReal analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on BeReal (limited API)"""
        try:
            # BeReal doesn't have a traditional search API
            logger.warning("BeReal doesn't support content search")
            return []
            
        except Exception as e:
            logger.error(f"BeReal search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's BeReal posts"""
        try:
            target_user_id = user_id or self.config.credentials.get('user_id')
            if not target_user_id:
                return []
            
            result = await self._make_request('GET', f'/feeds/friends')
            
            if result and result.get('data'):
                posts = []
                for post in result['data']:
                    if post.get('user', {}).get('id') == target_user_id:
                        posts.append({
                            'id': post.get('id'),
                            'creation_date': post.get('creationDate'),
                            'caption': post.get('caption', ''),
                            'location': post.get('location'),
                            'is_late': post.get('isLate', False),
                            'retake_counter': post.get('retakeCounter', 0),
                            'real_mojis_count': post.get('realMojis', {}).get('total', 0),
                            'comment_count': post.get('comment', 0),
                            'primary_photo': post.get('photoURL'),
                            'secondary_photo': post.get('secondaryPhotoURL')
                        })
                return posts
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting BeReal user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete BeReal post"""
        try:
            result = await self._make_request('DELETE', f'/content/posts/{content_id}')
            return result is not None
                
        except Exception as e:
            logger.error(f"Error deleting BeReal content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update BeReal post (limited editing)"""
        try:
            # BeReal typically doesn't allow editing posts
            logger.warning("BeReal doesn't support post editing")
            return False
                
        except Exception as e:
            logger.error(f"Error updating BeReal content: {e}")
            return False
    
    async def get_friends_feed(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get friends' BeReal feed"""
        try:
            result = await self._make_request('GET', '/feeds/friends')
            
            if result and result.get('data'):
                feed = []
                for post in result['data'][:limit]:
                    feed.append({
                        'id': post.get('id'),
                        'user': {
                            'id': post['user'].get('id'),
                            'username': post['user'].get('username'),
                            'fullname': post['user'].get('fullname'),
                            'profile_picture': post['user'].get('profilePicture', {}).get('url')
                        },
                        'creation_date': post.get('creationDate'),
                        'caption': post.get('caption', ''),
                        'location': post.get('location'),
                        'is_late': post.get('isLate', False),
                        'retake_counter': post.get('retakeCounter', 0),
                        'primary_photo': post.get('photoURL'),
                        'secondary_photo': post.get('secondaryPhotoURL'),
                        'real_mojis_count': post.get('realMojis', {}).get('total', 0)
                    })
                return feed
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting friends feed: {e}")
            return []
    
    async def add_real_moji(self, post_id: str, emoji: str) -> bool:
        """Add RealMoji reaction to a post"""
        try:
            data = {
                'emoji': emoji,
                'isInstant': False
            }
            
            result = await self._make_request('POST', f'/content/realmojis', json=data)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error adding RealMoji: {e}")
            return False
    
    async def get_discovery_feed(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get discovery feed"""
        try:
            result = await self._make_request('GET', '/feeds/discovery')
            
            if result and result.get('posts'):
                feed = []
                for post in result['posts'][:limit]:
                    feed.append({
                        'id': post.get('id'),
                        'region': post.get('region'),
                        'creation_date': post.get('creationDate'),
                        'caption': post.get('caption', ''),
                        'location': post.get('location'),
                        'primary_photo': post.get('photoURL'),
                        'secondary_photo': post.get('secondaryPhotoURL')
                    })
                return feed
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting discovery feed: {e}")
            return []
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
