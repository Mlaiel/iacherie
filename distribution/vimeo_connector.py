"""
Vimeo Platform Connector
=======================

Enterprise-grade Vimeo API connector for Ainflue Distribution Platform.
Supports video publishing, live streaming, portfolio management, and analytics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written
permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)

class VimeoPrivacy(Enum):
    """Vimeo privacy settings"""
    ANYBODY = "anybody"
    NOBODY = "nobody"
    CONTACTS = "contacts"
    PASSWORD = "password"
    USERS = "users"
    DISABLE = "disable"

class VimeoLicense(Enum):
    """Vimeo license options"""
    BY = "by"
    BY_SA = "by-sa"
    BY_ND = "by-nd"
    BY_NC = "by-nc"
    BY_NC_SA = "by-nc-sa"
    BY_NC_ND = "by-nc-nd"
    CC0 = "cc0"

class VimeoVideoQuality(Enum):
    """Vimeo video quality options"""
    SD = "sd"
    HD = "hd"
    UHD = "uhd"

@dataclass
class VimeoVideo:
    """Vimeo video data structure"""
    name: str
    description: str
    privacy: str = "anybody"
    password: Optional[str] = None
    license: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    allow_download: bool = False
    allow_add_to_collections: bool = True
    allow_share: bool = True
    embed_domains: List[str] = field(default_factory=list)
    folder_uri: Optional[str] = None

@dataclass
class VimeoLiveStream:
    """Vimeo live stream data structure"""
    title: str
    description: str
    privacy: str = "anybody"
    password: Optional[str] = None
    auto_cc_enabled: bool = False
    auto_cc_language: str = "en-US"
    chat_enabled: bool = True
    embed_domains: List[str] = field(default_factory=list)

@dataclass
class VimeoShowcase:
    """Vimeo showcase (portfolio) data structure"""
    name: str
    description: str
    privacy: str = "anybody"
    password: Optional[str] = None
    theme: str = "standard"
    sort: str = "manual"
    
class VimeoConnector:
    """
    Enterprise Vimeo API Connector
    
    Provides comprehensive integration with Vimeo platform for:
    - Video upload and management
    - Live streaming setup and control
    - Portfolio/showcase management
    - Video analytics and insights
    - Team and collaboration features
    """
    
    def __init__(self, access_token: str, client_id: str = None, client_secret: str = None):
        """
        Initialize Vimeo connector
        
        Args:
            access_token: Vimeo API access token
            client_id: Optional client ID for OAuth
            client_secret: Optional client secret for OAuth
        """
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.vimeo.com"
        self.session: Optional[aiohttp.ClientSession] = None
        self.user_info: Optional[Dict] = None
        self.rate_limit_remaining = 1000
        self.rate_limit_reset = datetime.now()
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.authenticate()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def authenticate(self) -> bool:
        """
        Authenticate with Vimeo and get user info
        
        Returns:
            bool: Authentication success status
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers={
                        'Authorization': f'Bearer {self.access_token}',
                        'Content-Type': 'application/json',
                        'Accept': 'application/vnd.vimeo.*+json;version=3.4'
                    }
                )
            
            # Get user information
            response = await self._make_request('GET', '/me')
            
            if response:
                self.user_info = response
                logger.info(f"Successfully authenticated with Vimeo for user: {response.get('name', 'Unknown')}")
                return True
            else:
                logger.error("Vimeo authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"Vimeo authentication error: {str(e)}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """
        Make authenticated API request with rate limiting
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Optional[Dict]: API response data
        """
        # Check rate limits
        if self.rate_limit_remaining <= 0:
            if datetime.now() < self.rate_limit_reset:
                wait_time = (self.rate_limit_reset - datetime.now()).total_seconds()
                await asyncio.sleep(wait_time)
        
        try:
            url = f"{self.base_url}{endpoint}"
            
            async with self.session.request(method, url, **kwargs) as response:
                # Update rate limiting info
                self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 1000))
                reset_time = response.headers.get('X-RateLimit-Reset')
                if reset_time:
                    self.rate_limit_reset = datetime.fromtimestamp(int(reset_time))
                
                if response.status in [200, 201, 204]:
                    if response.status == 204:
                        return {}
                    return await response.json()
                elif response.status == 429:
                    logger.warning("Vimeo rate limit exceeded")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"Vimeo API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Vimeo API request error: {str(e)}")
            return None
    
    async def upload_video(self, video_path: str, video_data: VimeoVideo, 
                          progress_callback: Optional[callable] = None) -> Optional[str]:
        """
        Upload a video to Vimeo
        
        Args:
            video_path: Path to video file
            video_data: Video metadata
            progress_callback: Optional progress callback function
            
        Returns:
            Optional[str]: Video URI if successful
        """
        try:
            # Get file size
            file_size = os.path.getsize(video_path)
            
            # Create upload ticket
            upload_data = {
                'upload': {
                    'approach': 'tus',
                    'size': file_size
                },
                'name': video_data.name,
                'description': video_data.description,
                'privacy': {
                    'view': video_data.privacy,
                    'embed': 'public' if video_data.privacy == 'anybody' else 'private',
                    'download': video_data.allow_download,
                    'add': video_data.allow_add_to_collections
                }
            }
            
            if video_data.password:
                upload_data['privacy']['password'] = video_data.password
            
            if video_data.license:
                upload_data['license'] = video_data.license
            
            response = await self._make_request(
                'POST',
                '/me/videos',
                json=upload_data
            )
            
            if not response:
                logger.error("Failed to create upload ticket")
                return None
            
            video_uri = response['uri']
            upload_link = response['upload']['upload_link']
            
            # Upload video file using tus protocol
            await self._upload_file_tus(video_path, upload_link, progress_callback)
            
            # Set video metadata
            await self._set_video_metadata(video_uri, video_data)
            
            logger.info(f"Successfully uploaded video: {video_data.name}")
            return video_uri
            
        except Exception as e:
            logger.error(f"Error uploading video: {str(e)}")
            return None
    
    async def _upload_file_tus(self, file_path: str, upload_url: str, 
                              progress_callback: Optional[callable] = None):
        """
        Upload file using TUS resumable upload protocol
        
        Args:
            file_path: Path to file
            upload_url: TUS upload URL
            progress_callback: Optional progress callback
        """
        chunk_size = 1024 * 1024  # 1MB chunks
        file_size = os.path.getsize(file_path)
        uploaded = 0
        
        async with aiohttp.ClientSession() as tus_session:
            with open(file_path, 'rb') as f:
                while uploaded < file_size:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    headers = {
                        'Tus-Resumable': '1.0.0',
                        'Upload-Offset': str(uploaded),
                        'Content-Type': 'application/offset+octet-stream'
                    }
                    
                    async with tus_session.patch(upload_url, data=chunk, headers=headers) as response:
                        if response.status == 204:
                            uploaded += len(chunk)
                            if progress_callback:
                                progress_callback(uploaded, file_size)
                        else:
                            raise Exception(f"Upload failed with status: {response.status}")
    
    async def _set_video_metadata(self, video_uri: str, video_data: VimeoVideo):
        """
        Set video metadata after upload
        
        Args:
            video_uri: Video URI
            video_data: Video metadata
        """
        try:
            # Set tags
            if video_data.tags:
                for tag in video_data.tags[:20]:  # Vimeo limit
                    await self._make_request(
                        'PUT',
                        f'{video_uri}/tags/{tag}'
                    )
            
            # Set categories
            if video_data.categories:
                category_data = {'category': video_data.categories[0]}  # Vimeo allows one category
                await self._make_request(
                    'PUT',
                    f'{video_uri}/categories',
                    json=category_data
                )
            
            # Add to folder if specified
            if video_data.folder_uri:
                await self._make_request(
                    'PUT',
                    f'{video_data.folder_uri}/videos/{video_uri.split("/")[-1]}'
                )
            
        except Exception as e:
            logger.error(f"Error setting video metadata: {str(e)}")
    
    async def create_live_stream(self, stream_data: VimeoLiveStream) -> Optional[Dict]:
        """
        Create a live stream event
        
        Args:
            stream_data: Live stream configuration
            
        Returns:
            Optional[Dict]: Live stream details if successful
        """
        try:
            live_data = {
                'title': stream_data.title,
                'description': stream_data.description,
                'privacy': {
                    'view': stream_data.privacy
                },
                'auto_cc_enabled': stream_data.auto_cc_enabled,
                'auto_cc_language': stream_data.auto_cc_language,
                'chat_enabled': stream_data.chat_enabled
            }
            
            if stream_data.password:
                live_data['privacy']['password'] = stream_data.password
            
            response = await self._make_request(
                'POST',
                '/me/live_events',
                json=live_data
            )
            
            if response:
                logger.info(f"Successfully created live stream: {stream_data.title}")
                return response
            else:
                logger.error(f"Failed to create live stream: {stream_data.title}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating live stream: {str(e)}")
            return None
    
    async def start_live_stream(self, live_event_id: str) -> bool:
        """
        Start a live stream
        
        Args:
            live_event_id: Live event ID
            
        Returns:
            bool: Success status
        """
        try:
            response = await self._make_request(
                'PATCH',
                f'/live_events/{live_event_id}',
                json={'status': 'streaming'}
            )
            
            if response:
                logger.info(f"Successfully started live stream: {live_event_id}")
                return True
            else:
                logger.error(f"Failed to start live stream: {live_event_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting live stream: {str(e)}")
            return False
    
    async def end_live_stream(self, live_event_id: str) -> bool:
        """
        End a live stream
        
        Args:
            live_event_id: Live event ID
            
        Returns:
            bool: Success status
        """
        try:
            response = await self._make_request(
                'PATCH',
                f'/live_events/{live_event_id}',
                json={'status': 'done'}
            )
            
            if response:
                logger.info(f"Successfully ended live stream: {live_event_id}")
                return True
            else:
                logger.error(f"Failed to end live stream: {live_event_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error ending live stream: {str(e)}")
            return False
    
    async def create_showcase(self, showcase_data: VimeoShowcase) -> Optional[str]:
        """
        Create a showcase (portfolio)
        
        Args:
            showcase_data: Showcase configuration
            
        Returns:
            Optional[str]: Showcase URI if successful
        """
        try:
            showcase_request = {
                'name': showcase_data.name,
                'description': showcase_data.description,
                'privacy': showcase_data.privacy,
                'theme': showcase_data.theme,
                'sort': showcase_data.sort
            }
            
            if showcase_data.password:
                showcase_request['password'] = showcase_data.password
            
            response = await self._make_request(
                'POST',
                '/me/albums',
                json=showcase_request
            )
            
            if response:
                showcase_uri = response['uri']
                logger.info(f"Successfully created showcase: {showcase_data.name}")
                return showcase_uri
            else:
                logger.error(f"Failed to create showcase: {showcase_data.name}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating showcase: {str(e)}")
            return None
    
    async def add_video_to_showcase(self, showcase_uri: str, video_uri: str) -> bool:
        """
        Add video to showcase
        
        Args:
            showcase_uri: Showcase URI
            video_uri: Video URI
            
        Returns:
            bool: Success status
        """
        try:
            video_id = video_uri.split('/')[-1]
            
            response = await self._make_request(
                'PUT',
                f'{showcase_uri}/videos/{video_id}'
            )
            
            if response is not None:
                logger.info(f"Successfully added video to showcase")
                return True
            else:
                logger.error(f"Failed to add video to showcase")
                return False
                
        except Exception as e:
            logger.error(f"Error adding video to showcase: {str(e)}")
            return False
    
    async def get_video_analytics(self, video_uri: str, start_date: datetime, end_date: datetime) -> Optional[Dict]:
        """
        Get video analytics
        
        Args:
            video_uri: Video URI
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Optional[Dict]: Analytics data
        """
        try:
            params = {
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d')
            }
            
            response = await self._make_request(
                'GET',
                f'{video_uri}/stats',
                params=params
            )
            
            if response:
                logger.info(f"Successfully retrieved video analytics")
                return response
            else:
                logger.error(f"Failed to retrieve video analytics")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving video analytics: {str(e)}")
            return None
    
    async def get_user_analytics(self, start_date: datetime, end_date: datetime) -> Optional[Dict]:
        """
        Get user account analytics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Optional[Dict]: Analytics data
        """
        try:
            params = {
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d')
            }
            
            response = await self._make_request(
                'GET',
                '/me/analytics',
                params=params
            )
            
            if response:
                logger.info(f"Successfully retrieved user analytics")
                return response
            else:
                logger.error(f"Failed to retrieve user analytics")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving user analytics: {str(e)}")
            return None
    
    async def search_videos(self, query: str, sort: str = "relevant", 
                           page: int = 1, per_page: int = 25) -> Optional[Dict]:
        """
        Search for videos on Vimeo
        
        Args:
            query: Search query
            sort: Sort order (relevant, date, alphabetical, plays, likes, comments, duration)
            page: Page number
            per_page: Results per page
            
        Returns:
            Optional[Dict]: Search results
        """
        try:
            params = {
                'query': query,
                'sort': sort,
                'page': page,
                'per_page': per_page
            }
            
            response = await self._make_request(
                'GET',
                '/videos',
                params=params
            )
            
            if response:
                logger.info(f"Successfully searched videos for: {query}")
                return response
            else:
                logger.error(f"Failed to search videos for: {query}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching videos: {str(e)}")
            return None
    
    async def update_video_thumbnail(self, video_uri: str, thumbnail_path: str) -> bool:
        """
        Update video thumbnail
        
        Args:
            video_uri: Video URI
            thumbnail_path: Path to thumbnail image
            
        Returns:
            bool: Success status
        """
        try:
            # Upload thumbnail
            with open(thumbnail_path, 'rb') as f:
                thumbnail_data = f.read()
            
            response = await self._make_request(
                'POST',
                f'{video_uri}/pictures',
                data=thumbnail_data,
                headers={'Content-Type': 'image/jpeg'}
            )
            
            if response and 'uri' in response:
                # Set as active thumbnail
                picture_uri = response['uri']
                await self._make_request(
                    'PATCH',
                    picture_uri,
                    json={'active': True}
                )
                
                logger.info(f"Successfully updated video thumbnail")
                return True
            else:
                logger.error(f"Failed to update video thumbnail")
                return False
                
        except Exception as e:
            logger.error(f"Error updating video thumbnail: {str(e)}")
            return False
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

# Usage example
async def main():
    """Example usage of VimeoConnector"""
    async with VimeoConnector(
        access_token="your_vimeo_access_token"
    ) as vimeo:
        
        # Upload a video
        video = VimeoVideo(
            name="My Awesome Video",
            description="A great video demonstrating our product",
            privacy="anybody",
            tags=["demo", "product", "tutorial"],
            allow_download=False
        )
        
        def progress_callback(uploaded, total):
            percent = (uploaded / total) * 100
            print(f"Upload progress: {percent:.1f}%")
        
        video_uri = await vimeo.upload_video(
            "path/to/video.mp4",
            video,
            progress_callback
        )
        print(f"Video uploaded: {video_uri}")
        
        # Create live stream
        live_stream = VimeoLiveStream(
            title="Live Product Demo",
            description="Join us for a live demonstration",
            privacy="anybody",
            chat_enabled=True
        )
        
        stream_info = await vimeo.create_live_stream(live_stream)
        print(f"Live stream created: {stream_info}")

if __name__ == "__main__":
    asyncio.run(main())