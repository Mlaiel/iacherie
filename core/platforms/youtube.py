"""YouTube Platform Integration

Complete YouTube Data API v3 integration for video distribution, analytics and monitoring.

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


class YouTubePlatform(PlatformBase):
    """
YouTube platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """
Initialize YouTube platform"""
        super().__init__(config)
        self.api_base = "https://www.googleapis.com/youtube/v3"
        self.upload_base = "https://www.googleapis.com/upload/youtube/v3"
        self.auth_base = "https://oauth2.googleapis.com"
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
Authenticate with YouTube using OAuth2"""
        try:
            # If we have a refresh token, use it
            if self.config.credentials.refresh_token:
                return await self.refresh_token()
            
            # For initial authentication, would need OAuth2 flow
            # This is typically handled by the frontend
            if self.config.credentials.access_token:
                self.status = PlatformStatus.ACTIVE
                self.reset_error_count()
                return True
            
            logger.error("YouTube authentication requires OAuth2 flow or existing tokens")
            return False
            
        except Exception as e:
            logger.error(f"YouTube authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh YouTube access token"""
        if not self.config.credentials.refresh_token:
            logger.error("No refresh token available for YouTube")
            return False
        
        try:
            session = await self._get_session()
            
            data = {
                'client_id': self.config.credentials.client_id,
                'client_secret': self.config.credentials.client_secret,
                'refresh_token': self.config.credentials.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            async with session.post(f"{self.auth_base}/token", data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.config.credentials.access_token = token_data['access_token']
                    
                    expires_in = token_data.get('expires_in', 3600)
                    self.config.credentials.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    if 'refresh_token' in token_data:
                        self.config.credentials.refresh_token = token_data['refresh_token']
                    
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("YouTube token refreshed successfully")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"YouTube token refresh failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"YouTube token refresh error: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to YouTube API"""
        if not self.is_authenticated or self._token_expired():
            if not await self.refresh_token():
                return None
        
        try:
            session = await self._get_session()
            headers = kwargs.get('headers', {})
            
            # Add API key for some endpoints, Bearer token for others
            if 'key' not in kwargs.get('params', {}):
                headers['Authorization'] = f'Bearer {self.config.credentials.access_token}'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    # Token expired, try to refresh
                    if await self.refresh_token():
                        headers['Authorization'] = f'Bearer {self.config.credentials.access_token}'
                        async with session.request(method, url, **kwargs) as retry_response:
                            if retry_response.status == 200:
                                return await retry_response.json()
                    return None
                
                elif response.status == 403:
                    # Quota exceeded or forbidden
                    error_data = await response.json()
                    error_reason = error_data.get('error', {}).get('errors', [{}])[0].get('reason')
                    
                    if error_reason == 'quotaExceeded':
                        await self.handle_rate_limit(3600)  # Wait 1 hour for quota reset
                        return None
                    else:
                        logger.error(f"YouTube API forbidden: {error_data}")
                        return None
                
                elif response.status == 200:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"YouTube API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"YouTube request error: {e}")
            self.increment_error_count()
            return None
    
    def _token_expired(self) -> bool:
        """Check if token is expired"""
        if not self.config.credentials.expires_at:
            return True
        return datetime.utcnow() >= self.config.credentials.expires_at
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """
Upload video content to YouTube"""
        try:
            if not os.path.exists(content_path):
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Content file not found"
                )
            
            # Prepare video metadata
            video_data = {
                'snippet': {
                    'title': metadata.title,
                    'description': metadata.description,
                    'tags': metadata.tags,
                    'categoryId': self._get_category_id(metadata.category),
                    'defaultLanguage': metadata.language
                },
                'status': {
                    'privacyStatus': 'private',  # Start as private, can be changed later
                    'embeddable': True,
                    'license': 'youtube'
                }
            }
            
            # Start resumable upload
            session = await self._get_session()
            
            # Initial upload request
            headers = {
                'Authorization': f'Bearer {self.config.credentials.access_token}',
                'Content-Type': 'application/json; charset=UTF-8',
                'X-Upload-Content-Type': mimetypes.guess_type(content_path)[0] or 'video/*',
                'X-Upload-Content-Length': str(os.path.getsize(content_path))
            }
            
            params = {'uploadType': 'resumable', 'part': 'snippet,status'}
            
            async with session.post(
                f"{self.upload_base}/videos",
                headers=headers,
                params=params,
                json=video_data
            ) as response:
                if response.status not in [200, 201]:
                    error_text = await response.text()
                    return UploadResult(
                        success=False,
                        platform_id=self.platform_id,
                        error=f"Upload initialization failed: {error_text}"
                    )
                
                upload_url = response.headers.get('Location')
                if not upload_url:
                    return UploadResult(
                        success=False,
                        platform_id=self.platform_id,
                        error="No upload URL received"
                    )
            
            # Upload video file
            async with aiofiles.open(content_path, 'rb') as video_file:
                video_content = await video_file.read()
                
                upload_headers = {
                    'Authorization': f'Bearer {self.config.credentials.access_token}',
                    'Content-Type': mimetypes.guess_type(content_path)[0] or 'video/*',
                    'Content-Length': str(len(video_content))
                }
                
                async with session.put(
                    upload_url,
                    headers=upload_headers,
                    data=video_content
                ) as upload_response:
                    if upload_response.status in [200, 201]:
                        result = await upload_response.json()
                        video_id = result.get('id')
                        
                        return UploadResult(
                            success=True,
                            platform_id=self.platform_id,
                            content_id=video_id,
                            url=f"https://www.youtube.com/watch?v={video_id}",
                            message="Video uploaded successfully",
                            metadata={
                                'video_id': video_id,
                                'title': result.get('snippet', {}).get('title'),
                                'status': result.get('status', {}).get('uploadStatus')
                            }
                        )
                    else:
                        error_text = await upload_response.text()
                        return UploadResult(
                            success=False,
                            platform_id=self.platform_id,
                            error=f"Video upload failed: {error_text}"
                        )
            
        except Exception as e:
            logger.error(f"YouTube upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    def _get_category_id(self, category: str) -> str:
        """Map category name to YouTube category ID"""
        category_map = {
            'music': '10',
            'entertainment': '24',
            'education': '27',
            'howto': '26',
            'gaming': '20',
            'comedy': '23',
            'sports': '17',
            'news': '25',
            'technology': '28'
        }
        return category_map.get(category.lower(), '22')  # Default to People & Blogs
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """
Get YouTube analytics for a video"""
        try:
            # Get video statistics
            video_stats = await self._make_request(
                'GET',
                'videos',
                params={
                    'part': 'statistics,snippet',
                    'id': content_id
                }
            )
            
            if not video_stats or not video_stats.get('items'):
                raise Exception(f"Video {content_id} not found")
            
            video = video_stats['items'][0]
            stats = video.get('statistics', {})
            snippet = video.get('snippet', {})
            
            # Get detailed analytics (requires YouTube Analytics API)
            analytics_data = await self._get_video_analytics(content_id, start_date, end_date)
            
            return AnalyticsData(
                platform_id=self.platform_id,
                content_id=content_id,
                views=int(stats.get('viewCount', 0)),
                likes=int(stats.get('likeCount', 0)),
                shares=0,  # Not available in basic stats
                comments=int(stats.get('commentCount', 0)),
                engagement_rate=self._calculate_engagement_rate(stats),
                metadata={
                    'title': snippet.get('title'),
                    'description': snippet.get('description'),
                    'published_at': snippet.get('publishedAt'),
                    'duration': snippet.get('duration'),
                    'tags': snippet.get('tags', []),
                    'category_id': snippet.get('categoryId'),
                    'analytics': analytics_data
                }
            )
            
        except Exception as e:
            logger.error(f"YouTube analytics error: {e}")
            raise
    
    async def _get_video_analytics(self, video_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get detailed video analytics using YouTube Analytics API"""
        # This would require YouTube Analytics API access
        # For now, return empty analytics
        return {
            'watch_time': 0,
            'average_view_duration': 0,
            'subscriber_gained': 0,
            'revenue': 0.0
        }
    
    def _calculate_engagement_rate(self, stats: Dict[str, Any]) -> float:
        """
Calculate engagement rate"""
        views = int(stats.get('viewCount', 0))
        likes = int(stats.get('likeCount', 0))
        comments = int(stats.get('commentCount', 0))
        
        if views == 0:
            return 0.0
        
        return ((likes + comments) / views) * 100
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """
Search content on YouTube"""
        search_type = 'video'  # YouTube API default
        if content_type == ContentType.PLAYLIST:
            search_type = 'playlist'
        
        params = {
            'part': 'snippet',
            'q': query,
            'type': search_type,
            'maxResults': 50,
            'order': 'relevance'
        }
        
        results = await self._make_request('GET', 'search', params=params)
        
        if not results:
            return []
        
        formatted_results = []
        for item in results.get('items', []):
            snippet = item.get('snippet', {})
            formatted_results.append({
                'id': item.get('id', {}).get('videoId') or item.get('id', {}).get('playlistId'),
                'title': snippet.get('title'),
                'description': snippet.get('description'),
                'channel_title': snippet.get('channelTitle'),
                'channel_id': snippet.get('channelId'),
                'published_at': snippet.get('publishedAt'),
                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                'type': search_type
            })
        
        return formatted_results
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
Get user's videos from YouTube"""
        try:
            # Get channel info first
            if user_id:
                channel_params = {'part': 'contentDetails', 'id': user_id}
            else:
                channel_params = {'part': 'contentDetails', 'mine': 'true'}
            
            channel_data = await self._make_request('GET', 'channels', params=channel_params)
            
            if not channel_data or not channel_data.get('items'):
                return []
            
            uploads_playlist_id = channel_data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            playlist_params = {
                'part': 'snippet,contentDetails',
                'playlistId': uploads_playlist_id,
                'maxResults': 50
            }
            
            playlist_data = await self._make_request('GET', 'playlistItems', params=playlist_params)
            
            if not playlist_data:
                return []
            
            videos = []
            for item in playlist_data.get('items', []):
                snippet = item.get('snippet', {})
                content_details = item.get('contentDetails', {})
                
                videos.append({
                    'id': content_details.get('videoId'),
                    'title': snippet.get('title'),
                    'description': snippet.get('description'),
                    'published_at': snippet.get('publishedAt'),
                    'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url'),
                    'position': snippet.get('position'),
                    'type': 'video'
                })
            
            return videos
            
        except Exception as e:
            logger.error(f"Error getting YouTube user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete video from YouTube"""
        try:
            result = await self._make_request(
                'DELETE',
                'videos',
                params={'id': content_id}
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error deleting YouTube content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update video metadata on YouTube"""
        try:
            # First get current video data
            current_data = await self._make_request(
                'GET',
                'videos',
                params={
                    'part': 'snippet,status',
                    'id': content_id
                }
            )
            
            if not current_data or not current_data.get('items'):
                return False
            
            video = current_data['items'][0]
            
            # Update snippet with new metadata
            video['snippet']['title'] = metadata.title
            video['snippet']['description'] = metadata.description
            video['snippet']['tags'] = metadata.tags
            video['snippet']['categoryId'] = self._get_category_id(metadata.category)
            
            # Update video
            result = await self._make_request(
                'PUT',
                'videos',
                params={'part': 'snippet,status'},
                json=video
            )
            
            return result is not None
            
        except Exception as e:
            logger.error(f"Error updating YouTube content: {e}")
            return False
    
    async def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Get comments for a video"""
        params = {
            'part': 'snippet',
            'videoId': video_id,
            'maxResults': min(max_results, 100),
            'order': 'time'
        }
        
        result = await self._make_request('GET', 'commentThreads', params=params)
        
        if not result:
            return []
        
        comments = []
        for item in result.get('items', []):
            snippet = item.get('snippet', {}).get('topLevelComment', {}).get('snippet', {})
            comments.append({
                'id': item.get('id'),
                'text': snippet.get('textDisplay'),
                'author': snippet.get('authorDisplayName'),
                'author_channel_id': snippet.get('authorChannelId', {}).get('value'),
                'like_count': snippet.get('likeCount'),
                'published_at': snippet.get('publishedAt'),
                'updated_at': snippet.get('updatedAt')
            })
        
        return comments
    
    async def create_playlist(self, title: str, description: str = "", privacy_status: str = "private") -> Optional[str]:
        """Create a new playlist"""
        data = {
            'snippet': {
                'title': title,
                'description': description
            },
            'status': {
                'privacyStatus': privacy_status
            }
        }
        
        result = await self._make_request(
            'POST',
            'playlists',
            params={'part': 'snippet,status'},
            json=data
        )
        
        if result:
            return result.get('id')
        return None
    
    async def add_video_to_playlist(self, playlist_id: str, video_id: str) -> bool:
        """
Add video to playlist"""
        data = {
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
        
        result = await self._make_request(
            'POST',
            'playlistItems',
            params={'part': 'snippet'},
            json=data
        )
        
        return result is not None
    
    async def close(self):
        """
Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
