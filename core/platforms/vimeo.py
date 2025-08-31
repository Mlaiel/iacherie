"""Vimeo Platform Integration

Vimeo API integration for professional video hosting and analytics.

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


class VimeoPlatform(PlatformBase):
    """Vimeo platform integration"""    
    def __init__(self, config: PlatformConfig):
        """Initialize Vimeo platform"""        super().__init__(config)
        self.api_base = "https://api.vimeo.com"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Vimeo OAuth2"""        try:
            access_token = self.config.credentials.get('access_token')
            
            if access_token:
                session = await self._get_session()
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.get(f"{self.api_base}/me", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        self.config.credentials['user_id'] = user_data.get('uri', '').split('/')[-1]
                        
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info("Vimeo authentication successful")
                        return True
                    else:
                        logger.error("Vimeo token validation failed")
                        return False
            else:
                logger.error("Vimeo requires access_token")
                return False
                
        except Exception as e:
            logger.error(f"Vimeo authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Vimeo token"""        return await self.authenticate()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Vimeo API"""        try:
            session = await self._get_session()
            
            headers = kwargs.get('headers', {})
            if self.config.credentials.get('access_token'):
                headers['Authorization'] = f'Bearer {self.config.credentials["access_token"]}'
            
            headers['Content-Type'] = 'application/json'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 401:
                    logger.error("Vimeo authentication failed")
                    self.increment_error_count()
                    return None
                
                elif response.status in [200, 201, 204]:
                    if response.status == 204:
                        return {'success': True}
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Vimeo API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Vimeo request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload video to Vimeo"""        try:
            # Create video upload ticket
            upload_data = {
                'upload': {
                    'approach': 'tus',
                    'size': 0  # Would need actual file size
                },
                'name': metadata.title,
                'description': metadata.description or '',
                'privacy': {
                    'view': 'anybody',  # public, password, nobody, contacts, users
                    'embed': 'public'
                }
            }
            
            if metadata.tags:
                upload_data['tags'] = ','.join(metadata.tags)
            
            result = await self._make_request('POST', '/me/videos', json=upload_data)
            
            if result and result.get('uri'):
                video_id = result['uri'].split('/')[-1]
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=video_id,
                    url=result.get('link'),
                    metadata={
                        'upload_link': result.get('upload', {}).get('upload_link'),
                        'status': result.get('status'),
                        'privacy': result.get('privacy', {}),
                        'created_time': result.get('created_time')
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Vimeo video upload creation failed"
                )
                
        except Exception as e:
            logger.error(f"Vimeo upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Vimeo video analytics"""        try:
            # Get video stats
            video_data = await self._make_request('GET', f'/videos/{content_id}')
            
            if video_data:
                stats = video_data.get('stats', {})
                
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=stats.get('plays', 0),
                    likes=video_data.get('metadata', {}).get('connections', {}).get('likes', {}).get('total', 0),
                    shares=0,  # Vimeo doesn't provide direct share count
                    comments=video_data.get('metadata', {}).get('connections', {}).get('comments', {}).get('total', 0),
                    metadata={
                        'duration': video_data.get('duration', 0),
                        'downloads': stats.get('downloads', 0),
                        'finishes': stats.get('finishes', 0),
                        'watch_time': stats.get('watch_time', 0),
                        'average_percent_watched': stats.get('average_percent_watched', 0),
                        'privacy': video_data.get('privacy', {}),
                        'status': video_data.get('status'),
                        'created_time': video_data.get('created_time'),
                        'width': video_data.get('width'),
                        'height': video_data.get('height')
                    }
                )
            else:
                raise Exception("Video not found")
                
        except Exception as e:
            logger.error(f"Vimeo analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search videos on Vimeo"""        try:
            params = {
                'query': query,
                'per_page': 25,
                'sort': 'relevant'
            }
            
            result = await self._make_request('GET', '/videos', params=params)
            
            if result and result.get('data'):
                videos = []
                for video in result['data']:
                    videos.append({
                        'id': video.get('uri', '').split('/')[-1],
                        'name': video.get('name'),
                        'description': video.get('description'),
                        'link': video.get('link'),
                        'duration': video.get('duration'),
                        'width': video.get('width'),
                        'height': video.get('height'),
                        'created_time': video.get('created_time'),
                        'stats': video.get('stats', {}),
                        'user': video.get('user', {}),
                        'pictures': video.get('pictures', {})
                    })
                return videos
            
            return []
            
        except Exception as e:
            logger.error(f"Vimeo search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's videos from Vimeo"""        try:
            endpoint = f'/users/{user_id}/videos' if user_id else '/me/videos'
            result = await self._make_request('GET', endpoint)
            
            if result and result.get('data'):
                videos = []
                for video in result['data']:
                    videos.append({
                        'id': video.get('uri', '').split('/')[-1],
                        'name': video.get('name'),
                        'description': video.get('description'),
                        'link': video.get('link'),
                        'duration': video.get('duration'),
                        'status': video.get('status'),
                        'privacy': video.get('privacy', {}),
                        'created_time': video.get('created_time'),
                        'modified_time': video.get('modified_time'),
                        'stats': video.get('stats', {})
                    })
                return videos
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Vimeo user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Vimeo video"""        try:
            result = await self._make_request('DELETE', f'/videos/{content_id}')
            
            if result and result.get('success'):
                logger.info(f"Successfully deleted Vimeo video {content_id}")
                return True
            else:
                logger.error("Failed to delete Vimeo video")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting Vimeo content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update Vimeo video"""        try:
            update_data = {}
            
            if metadata.title:
                update_data['name'] = metadata.title
            
            if metadata.description:
                update_data['description'] = metadata.description
            
            if metadata.tags:
                update_data['tags'] = ','.join(metadata.tags)
            
            if update_data:
                result = await self._make_request('PATCH', f'/videos/{content_id}', json=update_data)
                
                if result:
                    logger.info(f"Successfully updated Vimeo video {content_id}")
                    return True
                else:
                    logger.error("Failed to update Vimeo video")
                    return False
            
            return True
                
        except Exception as e:
            logger.error(f"Error updating Vimeo content: {e}")
            return False
    
    async def get_video_chapters(self, video_id: str) -> List[Dict[str, Any]]:
        """Get video chapters"""        try:
            result = await self._make_request('GET', f'/videos/{video_id}/chapters')
            
            if result and result.get('data'):
                return result['data']
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting video chapters: {e}")
            return []
    
    async def add_video_to_collection(self, video_id: str, collection_id: str) -> bool:
        """Add video to collection/showcase"""        try:
            result = await self._make_request('PUT', f'/me/albums/{collection_id}/videos/{video_id}')
            
            if result and result.get('success'):
                logger.info(f"Successfully added video {video_id} to collection {collection_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error adding video to collection: {e}")
            return False
    
    async def close(self):
        """Close HTTP session"""        if self.session and not self.session.closed:
            await self.session.close()
