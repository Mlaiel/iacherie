"""
Pinterest Platform Integration

Pinterest API integration for visual content sharing and discovery.

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


class PinterestPlatform(PlatformBase):
    """Pinterest platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """Initialize Pinterest platform"""
        super().__init__(config)
        self.api_base = "https://api.pinterest.com/v5"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Pinterest OAuth2"""
        try:
            access_token = self.config.credentials.get('access_token')
            
            if access_token:
                # Test token validity
                session = await self._get_session()
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.get(f"{self.api_base}/user_account", headers=headers) as response:
                    if response.status == 200:
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info("Pinterest authentication successful")
                        return True
                    else:
                        logger.error("Pinterest token validation failed")
                        return False
            else:
                logger.error("Pinterest requires valid access_token")
                return False
                
        except Exception as e:
            logger.error(f"Pinterest authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Pinterest token"""
        # Pinterest tokens are long-lived, refresh requires re-authorization
        return await self.authenticate()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Pinterest API"""
        try:
            session = await self._get_session()
            
            # Add authentication headers
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
                    logger.error("Pinterest authentication failed")
                    self.increment_error_count()
                    return None
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Pinterest API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Pinterest request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Create a Pin on Pinterest"""
        try:
            # Create pin data
            pin_data = {
                "link": content_path if content_path.startswith('http') else None,
                "title": metadata.title,
                "description": metadata.description or "",
                "alt_text": metadata.alt_text if hasattr(metadata, 'alt_text') else metadata.title
            }
            
            # Handle board assignment
            board_id = None
            if metadata.tags:
                # Try to find or create board based on first tag
                board_name = metadata.tags[0]
                boards = await self.get_user_boards()
                
                for board in boards:
                    if board.get('name', '').lower() == board_name.lower():
                        board_id = board.get('id')
                        break
                
                if not board_id:
                    # Create new board
                    new_board = await self.create_board(board_name, metadata.description or f"Board for {board_name}")
                    if new_board:
                        board_id = new_board.get('id')
            
            if not board_id:
                # Use default board or create one
                boards = await self.get_user_boards()
                if boards:
                    board_id = boards[0].get('id')
                else:
                    default_board = await self.create_board("My Pins", "Default board for pins")
                    if default_board:
                        board_id = default_board.get('id')
            
            pin_data["board_id"] = board_id
            
            # Handle media upload
            if content_path and not content_path.startswith('http'):
                # For local files, we need to upload to Pinterest first
                # This is a simplified version - full implementation would handle file upload
                pin_data["media_source"] = {
                    "source_type": "image_url",
                    "url": content_path  # Assuming it's already a URL
                }
            elif content_path and content_path.startswith('http'):
                pin_data["media_source"] = {
                    "source_type": "image_url",
                    "url": content_path
                }
            
            result = await self._make_request('POST', '/pins', json=pin_data)
            
            if result and result.get('id'):
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=result['id'],
                    url=result.get('url'),
                    metadata={
                        'board_id': board_id,
                        'created_at': result.get('created_at'),
                        'pin_metrics': result.get('pin_metrics', {})
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Pinterest pin creation failed"
                )
                
        except Exception as e:
            logger.error(f"Pinterest upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Pinterest pin analytics"""
        try:
            # Get pin details and metrics
            pin_data = await self._make_request('GET', f'/pins/{content_id}')
            
            if pin_data:
                pin_metrics = pin_data.get('pin_metrics', {})
                
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=pin_metrics.get('impression', 0),
                    likes=pin_metrics.get('save', 0),  # Pinterest uses "saves" instead of likes
                    shares=pin_metrics.get('pin_click', 0),
                    comments=pin_metrics.get('comment', 0),
                    metadata={
                        'outbound_click': pin_metrics.get('outbound_click', 0),
                        'save_rate': pin_metrics.get('save_rate', 0),
                        'impression': pin_metrics.get('impression', 0),
                        'engagement_rate': pin_metrics.get('engagement_rate', 0),
                        'created_at': pin_data.get('created_at'),
                        'board_id': pin_data.get('board_id'),
                        'media_type': pin_data.get('media', {}).get('media_type')
                    }
                )
            else:
                raise Exception("Pin not found")
                
        except Exception as e:
            logger.error(f"Pinterest analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search pins on Pinterest"""
        try:
            params = {
                'query': query,
                'limit': 25
            }
            
            result = await self._make_request('GET', '/search/pins', params=params)
            
            if result and result.get('items'):
                pins = []
                for item in result['items']:
                    pins.append({
                        'id': item.get('id'),
                        'title': item.get('title'),
                        'description': item.get('description'),
                        'url': item.get('url'),
                        'link': item.get('link'),
                        'media': item.get('media', {}),
                        'board_id': item.get('board_id'),
                        'created_at': item.get('created_at'),
                        'pin_metrics': item.get('pin_metrics', {})
                    })
                return pins
            
            return []
            
        except Exception as e:
            logger.error(f"Pinterest search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's pins from Pinterest"""
        try:
            result = await self._make_request('GET', '/user_account/pins')
            
            if result and result.get('items'):
                pins = []
                for item in result['items']:
                    pins.append({
                        'id': item.get('id'),
                        'title': item.get('title'),
                        'description': item.get('description'),
                        'url': item.get('url'),
                        'link': item.get('link'),
                        'media': item.get('media', {}),
                        'board_id': item.get('board_id'),
                        'created_at': item.get('created_at'),
                        'pin_metrics': item.get('pin_metrics', {})
                    })
                return pins
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Pinterest user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Pinterest pin"""
        try:
            result = await self._make_request('DELETE', f'/pins/{content_id}')
            
            # Pinterest DELETE returns 204 No Content on success
            logger.info(f"Successfully deleted Pinterest pin {content_id}")
            return True
                
        except Exception as e:
            logger.error(f"Error deleting Pinterest content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update Pinterest pin"""
        try:
            update_data = {}
            
            if metadata.title:
                update_data['title'] = metadata.title
            
            if metadata.description:
                update_data['description'] = metadata.description
            
            if hasattr(metadata, 'alt_text') and metadata.alt_text:
                update_data['alt_text'] = metadata.alt_text
            
            if update_data:
                result = await self._make_request('PATCH', f'/pins/{content_id}', json=update_data)
                
                if result and result.get('id'):
                    logger.info(f"Successfully updated Pinterest pin {content_id}")
                    return True
                else:
                    logger.error("Failed to update Pinterest pin")
                    return False
            
            return True  # No updates needed
                
        except Exception as e:
            logger.error(f"Error updating Pinterest content: {e}")
            return False
    
    async def get_user_boards(self) -> List[Dict[str, Any]]:
        """Get user's Pinterest boards"""
        try:
            result = await self._make_request('GET', '/boards')
            
            if result and result.get('items'):
                boards = []
                for item in result['items']:
                    boards.append({
                        'id': item.get('id'),
                        'name': item.get('name'),
                        'description': item.get('description'),
                        'privacy': item.get('privacy'),
                        'url': item.get('url'),
                        'created_at': item.get('created_at'),
                        'pin_count': item.get('pin_count', 0),
                        'follower_count': item.get('follower_count', 0),
                        'media': item.get('media', {}),
                        'owner': item.get('owner', {})
                    })
                return boards
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Pinterest boards: {e}")
            return []
    
    async def create_board(self, name: str, description: str = "", privacy: str = "PUBLIC") -> Optional[Dict[str, Any]]:
        """Create a new Pinterest board"""
        try:
            board_data = {
                'name': name,
                'description': description,
                'privacy': privacy
            }
            
            result = await self._make_request('POST', '/boards', json=board_data)
            
            if result and result.get('id'):
                logger.info(f"Successfully created Pinterest board: {name}")
                return result
            else:
                logger.error(f"Failed to create Pinterest board: {name}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Pinterest board: {e}")
            return None
    
    async def get_board_pins(self, board_id: str) -> List[Dict[str, Any]]:
        """Get pins from a specific board"""
        try:
            result = await self._make_request('GET', f'/boards/{board_id}/pins')
            
            if result and result.get('items'):
                pins = []
                for item in result['items']:
                    pins.append({
                        'id': item.get('id'),
                        'title': item.get('title'),
                        'description': item.get('description'),
                        'url': item.get('url'),
                        'link': item.get('link'),
                        'media': item.get('media', {}),
                        'created_at': item.get('created_at'),
                        'pin_metrics': item.get('pin_metrics', {})
                    })
                return pins
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting board pins: {e}")
            return []
    
    async def follow_board(self, board_id: str) -> bool:
        """Follow a Pinterest board"""
        try:
            result = await self._make_request('POST', f'/user_account/following/boards/{board_id}')
            
            if result:
                logger.info(f"Successfully followed board {board_id}")
                return True
            else:
                logger.error(f"Failed to follow board {board_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error following board: {e}")
            return False
    
    async def unfollow_board(self, board_id: str) -> bool:
        """Unfollow a Pinterest board"""
        try:
            result = await self._make_request('DELETE', f'/user_account/following/boards/{board_id}')
            
            logger.info(f"Successfully unfollowed board {board_id}")
            return True
                
        except Exception as e:
            logger.error(f"Error unfollowing board: {e}")
            return False
    
    async def get_trending_topics(self) -> List[str]:
        """Get trending topics on Pinterest"""
        try:
            # Pinterest doesn't have a direct trending topics API
            # This would require analyzing popular searches or categories
            logger.warning("Pinterest trending topics require custom analysis")
            
            # Return common Pinterest categories as placeholder
            return [
                'home decor', 'fashion', 'food', 'wedding', 'diy',
                'travel', 'beauty', 'fitness', 'art', 'gardening',
                'photography', 'recipes', 'hair', 'quotes', 'animals'
            ]
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return []
    
    async def get_user_profile(self) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        try:
            result = await self._make_request('GET', '/user_account')
            
            if result:
                return {
                    'account_type': result.get('account_type'),
                    'profile_image': result.get('profile_image'),
                    'website_url': result.get('website_url'),
                    'username': result.get('username'),
                    'about': result.get('about'),
                    'business_name': result.get('business_name'),
                    'follower_count': result.get('follower_count', 0),
                    'following_count': result.get('following_count', 0),
                    'monthly_views': result.get('monthly_views', 0),
                    'pin_count': result.get('pin_count', 0),
                    'board_count': result.get('board_count', 0)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    async def get_audience_insights(self) -> Dict[str, Any]:
        """Get Pinterest audience insights"""
        try:
            # Audience insights require Pinterest Business API
            result = await self._make_request('GET', '/user_account/analytics')
            
            if result:
                return {
                    'monthly_views': result.get('monthly_views', 0),
                    'monthly_engaged_audience': result.get('monthly_engaged_audience', 0),
                    'top_pins': result.get('top_pins', []),
                    'top_boards': result.get('top_boards', []),
                    'audience_insights': result.get('audience_insights', {})
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting audience insights: {e}")
            return {}
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
