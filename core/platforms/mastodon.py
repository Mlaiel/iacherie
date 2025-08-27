"""
Mastodon Platform Integration

Mastodon API integration for decentralized social networking.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging
import json
import os
from urllib.parse import quote

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus
)

logger = logging.getLogger(__name__)


class MastodonPlatform(PlatformBase):
    """Mastodon platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """Initialize Mastodon platform"""
        super().__init__(config)
        
        # Instance URL must be provided
        self.instance_url = config.credentials.get('instance_url', 'https://mastodon.social')
        if not self.instance_url.startswith('http'):
            self.instance_url = f"https://{self.instance_url}"
        
        self.api_base = f"{self.instance_url}/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Mastodon"""
        try:
            access_token = self.config.credentials.get('access_token')
            
            if access_token:
                session = await self._get_session()
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.get(f"{self.api_base}/accounts/verify_credentials", 
                                     headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        self.config.credentials['user_id'] = user_data.get('id')
                        self.config.credentials['username'] = user_data.get('username')
                        
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info(f"Mastodon authentication successful for {self.instance_url}")
                        return True
                    else:
                        logger.error("Mastodon token validation failed")
                        return False
            else:
                logger.error("Mastodon requires access_token")
                return False
                
        except Exception as e:
            logger.error(f"Mastodon authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Mastodon token"""
        return await self.authenticate()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Mastodon API"""
        try:
            session = await self._get_session()
            
            headers = kwargs.get('headers', {})
            if self.config.credentials.get('access_token'):
                headers['Authorization'] = f'Bearer {self.config.credentials["access_token"]}'
            
            headers['User-Agent'] = 'IAInfluencerAgent/1.0'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 401:
                    logger.error("Mastodon authentication failed")
                    self.increment_error_count()
                    return None
                
                elif response.status in [200, 201]:
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        return await response.json()
                    else:
                        return {'text': await response.text()}
                
                else:
                    error_text = await response.text()
                    logger.error(f"Mastodon API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Mastodon request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Post content on Mastodon"""
        try:
            media_ids = []
            
            # Handle media upload if content_path is provided
            if content_path and os.path.exists(content_path):
                media_id = await self._upload_media(content_path, metadata.title)
                if media_id:
                    media_ids.append(media_id)
            
            # Prepare status content
            status_text = metadata.description or metadata.title or ""
            
            # Add hashtags from tags
            if metadata.tags:
                hashtags = [f"#{tag.replace(' ', '').replace('#', '')}" for tag in metadata.tags]
                status_text += "\n\n" + " ".join(hashtags)
            
            # Mastodon status limit is typically 500 characters
            if len(status_text) > 500:
                status_text = status_text[:497] + "..."
            
            post_data = {
                'status': status_text,
                'visibility': 'public',  # public, unlisted, private, direct
                'language': 'de'  # or detect from content
            }
            
            if media_ids:
                post_data['media_ids'] = media_ids
            
            result = await self._make_request('POST', '/statuses', json=post_data)
            
            if result:
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=result.get('id'),
                    url=result.get('url'),
                    metadata={
                        'uri': result.get('uri'),
                        'visibility': result.get('visibility'),
                        'created_at': result.get('created_at'),
                        'favourites_count': result.get('favourites_count', 0),
                        'reblogs_count': result.get('reblogs_count', 0),
                        'replies_count': result.get('replies_count', 0),
                        'media_attachments': result.get('media_attachments', [])
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Mastodon status posting failed"
                )
                
        except Exception as e:
            logger.error(f"Mastodon upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def _upload_media(self, file_path: str, description: str = None) -> Optional[str]:
        """Upload media file to Mastodon"""
        try:
            session = await self._get_session()
            
            data = aiohttp.FormData()
            with open(file_path, 'rb') as f:
                filename = os.path.basename(file_path)
                data.add_field('file', f, filename=filename)
                
                if description:
                    data.add_field('description', description)
                
                headers = {
                    'Authorization': f'Bearer {self.config.credentials["access_token"]}'
                }
                
                async with session.post(f"{self.api_base}/media", 
                                      data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('id')
                    else:
                        logger.error(f"Media upload failed: {response.status}")
                        return None
                        
        except Exception as e:
            logger.error(f"Media upload error: {e}")
            return None
    
    async def get_analytics(self, content_id: str, start_date: datetime, 
                           end_date: datetime) -> AnalyticsData:
        """Get Mastodon post analytics"""
        try:
            result = await self._make_request('GET', f'/statuses/{content_id}')
            
            if result:
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=0,  # Not available on Mastodon
                    likes=result.get('favourites_count', 0),
                    shares=result.get('reblogs_count', 0),
                    comments=result.get('replies_count', 0),
                    metadata={
                        'boosts': result.get('reblogs_count', 0),
                        'favourites': result.get('favourites_count', 0),
                        'replies': result.get('replies_count', 0),
                        'created_at': result.get('created_at'),
                        'visibility': result.get('visibility'),
                        'language': result.get('language')
                    }
                )
            else:
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id
                )
                
        except Exception as e:
            logger.error(f"Mastodon analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Mastodon"""
        try:
            params = {
                'q': query,
                'type': 'statuses',  # accounts, hashtags, statuses
                'limit': 20
            }
            
            result = await self._make_request('GET', '/search', params=params)
            
            if result and result.get('statuses'):
                statuses = []
                for status in result['statuses']:
                    statuses.append({
                        'id': status.get('id'),
                        'content': status.get('content'),
                        'created_at': status.get('created_at'),
                        'url': status.get('url'),
                        'account': {
                            'username': status['account'].get('username'),
                            'display_name': status['account'].get('display_name')
                        },
                        'favourites_count': status.get('favourites_count', 0),
                        'reblogs_count': status.get('reblogs_count', 0),
                        'replies_count': status.get('replies_count', 0)
                    })
                return statuses
            
            return []
            
        except Exception as e:
            logger.error(f"Mastodon search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's statuses from Mastodon"""
        try:
            target_user_id = user_id or self.config.credentials.get('user_id')
            if not target_user_id:
                return []
            
            params = {
                'limit': 40,
                'exclude_replies': 'false',
                'exclude_reblogs': 'false'
            }
            
            result = await self._make_request('GET', f'/accounts/{target_user_id}/statuses', 
                                            params=params)
            
            if result:
                statuses = []
                for status in result:
                    statuses.append({
                        'id': status.get('id'),
                        'content': status.get('content'),
                        'created_at': status.get('created_at'),
                        'url': status.get('url'),
                        'visibility': status.get('visibility'),
                        'favourites_count': status.get('favourites_count', 0),
                        'reblogs_count': status.get('reblogs_count', 0),
                        'replies_count': status.get('replies_count', 0),
                        'media_attachments': status.get('media_attachments', [])
                    })
                return statuses
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Mastodon user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Mastodon status"""
        try:
            result = await self._make_request('DELETE', f'/statuses/{content_id}')
            return result is not None
                
        except Exception as e:
            logger.error(f"Error deleting Mastodon content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update Mastodon status (edit if supported)"""
        try:
            # Check if instance supports editing
            edit_data = {
                'status': metadata.description or metadata.title or ""
            }
            
            result = await self._make_request('PUT', f'/statuses/{content_id}', json=edit_data)
            return result is not None
                
        except Exception as e:
            logger.error(f"Error updating Mastodon content: {e}")
            return False
    
    async def get_home_timeline(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get home timeline"""
        try:
            params = {'limit': min(limit, 40)}
            result = await self._make_request('GET', '/timelines/home', params=params)
            
            if result:
                timeline = []
                for status in result:
                    timeline.append({
                        'id': status.get('id'),
                        'content': status.get('content'),
                        'created_at': status.get('created_at'),
                        'url': status.get('url'),
                        'account': {
                            'username': status['account'].get('username'),
                            'display_name': status['account'].get('display_name')
                        },
                        'favourites_count': status.get('favourites_count', 0),
                        'reblogs_count': status.get('reblogs_count', 0)
                    })
                return timeline
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting home timeline: {e}")
            return []
    
    async def get_public_timeline(self, local: bool = False, limit: int = 20) -> List[Dict[str, Any]]:
        """Get public timeline"""
        try:
            params = {
                'local': 'true' if local else 'false',
                'limit': min(limit, 40)
            }
            
            result = await self._make_request('GET', '/timelines/public', params=params)
            
            if result:
                timeline = []
                for status in result:
                    timeline.append({
                        'id': status.get('id'),
                        'content': status.get('content'),
                        'created_at': status.get('created_at'),
                        'url': status.get('url'),
                        'account': {
                            'username': status['account'].get('username'),
                            'display_name': status['account'].get('display_name')
                        }
                    })
                return timeline
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting public timeline: {e}")
            return []
    
    async def follow_user(self, user_id: str) -> bool:
        """Follow a user"""
        try:
            result = await self._make_request('POST', f'/accounts/{user_id}/follow')
            return result is not None
            
        except Exception as e:
            logger.error(f"Error following user: {e}")
            return False
    
    async def unfollow_user(self, user_id: str) -> bool:
        """Unfollow a user"""
        try:
            result = await self._make_request('POST', f'/accounts/{user_id}/unfollow')
            return result is not None
            
        except Exception as e:
            logger.error(f"Error unfollowing user: {e}")
            return False
    
    async def favourite_status(self, status_id: str) -> bool:
        """Favourite a status"""
        try:
            result = await self._make_request('POST', f'/statuses/{status_id}/favourite')
            return result is not None
            
        except Exception as e:
            logger.error(f"Error favouriting status: {e}")
            return False
    
    async def boost_status(self, status_id: str) -> bool:
        """Boost (reblog) a status"""
        try:
            result = await self._make_request('POST', f'/statuses/{status_id}/reblog')
            return result is not None
            
        except Exception as e:
            logger.error(f"Error boosting status: {e}")
            return False
    
    async def get_instance_info(self) -> Optional[Dict[str, Any]]:
        """Get Mastodon instance information"""
        try:
            result = await self._make_request('GET', '/instance')
            
            if result:
                return {
                    'uri': result.get('uri'),
                    'title': result.get('title'),
                    'description': result.get('description'),
                    'version': result.get('version'),
                    'stats': result.get('stats', {}),
                    'languages': result.get('languages', []),
                    'contact_account': result.get('contact_account')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting instance info: {e}")
            return None
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
