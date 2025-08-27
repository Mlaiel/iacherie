"""
Medium Platform Integration

Medium API integration for publishing and content distribution.

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


class MediumPlatform(PlatformBase):
    """Medium platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """Initialize Medium platform"""
        super().__init__(config)
        self.api_base = "https://api.medium.com/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Medium OAuth2"""
        try:
            access_token = self.config.credentials.get('access_token')
            
            if access_token:
                session = await self._get_session()
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
                
                async with session.get(f"{self.api_base}/me", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        self.config.credentials['user_id'] = user_data['data'].get('id')
                        self.config.credentials['username'] = user_data['data'].get('username')
                        
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info("Medium authentication successful")
                        return True
                    else:
                        logger.error("Medium token validation failed")
                        return False
            else:
                logger.error("Medium requires access_token")
                return False
                
        except Exception as e:
            logger.error(f"Medium authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Medium token"""
        return await self.authenticate()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Medium API"""
        try:
            session = await self._get_session()
            
            headers = kwargs.get('headers', {})
            if self.config.credentials.get('access_token'):
                headers['Authorization'] = f'Bearer {self.config.credentials["access_token"]}'
            
            headers['Content-Type'] = 'application/json'
            headers['Accept'] = 'application/json'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 401:
                    logger.error("Medium authentication failed")
                    self.increment_error_count()
                    return None
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Medium API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Medium request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Publish article on Medium"""
        try:
            user_id = self.config.credentials.get('user_id')
            if not user_id:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Medium user_id not found"
                )
            
            # Prepare article content
            if content_path and not content_path.startswith('http'):
                # For local content files, read content
                content_body = f"Content from: {content_path}"
            elif content_path and content_path.startswith('http'):
                content_body = f"Source: {content_path}"
            else:
                content_body = metadata.description or ""
            
            article_data = {
                'title': metadata.title,
                'contentFormat': 'html',  # or 'markdown'
                'content': f"<p>{content_body}</p>",
                'publishStatus': 'public',  # public, draft, unlisted
                'tags': metadata.tags[:5] if metadata.tags else []  # Medium allows max 5 tags
            }
            
            # Add canonical URL if provided
            if content_path and content_path.startswith('http'):
                article_data['canonicalUrl'] = content_path
            
            result = await self._make_request('POST', f'/users/{user_id}/posts', json=article_data)
            
            if result and result.get('data'):
                post_data = result['data']
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=post_data.get('id'),
                    url=post_data.get('url'),
                    metadata={
                        'title': post_data.get('title'),
                        'author_id': post_data.get('authorId'),
                        'publish_status': post_data.get('publishStatus'),
                        'published_at': post_data.get('publishedAt'),
                        'tags': post_data.get('tags', [])
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Medium article publishing failed"
                )
                
        except Exception as e:
            logger.error(f"Medium upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Medium article analytics"""
        try:
            # Medium API has limited analytics access
            # Most analytics require Medium Partner Program
            
            return AnalyticsData(
                platform_id=self.platform_id,
                content_id=content_id,
                views=0,  # Requires Partner Program
                likes=0,  # Claps - requires Partner Program
                shares=0,  # Not directly available
                comments=0,  # Not available via API
                metadata={
                    'note': 'Medium analytics require Partner Program access',
                    'claps': 0,
                    'reading_time': 0,
                    'word_count': 0
                }
            )
                
        except Exception as e:
            logger.error(f"Medium analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Medium (not available via API)"""
        try:
            logger.warning("Medium doesn't provide search API")
            return []
            
        except Exception as e:
            logger.error(f"Medium search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's posts from Medium"""
        try:
            target_user_id = user_id or self.config.credentials.get('user_id')
            if not target_user_id:
                return []
            
            result = await self._make_request('GET', f'/users/{target_user_id}/posts')
            
            if result and result.get('data'):
                posts = []
                for post in result['data']:
                    posts.append({
                        'id': post.get('id'),
                        'title': post.get('title'),
                        'author_id': post.get('authorId'),
                        'tags': post.get('tags', []),
                        'url': post.get('url'),
                        'publish_status': post.get('publishStatus'),
                        'published_at': post.get('publishedAt'),
                        'license': post.get('license'),
                        'license_url': post.get('licenseUrl')
                    })
                return posts
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Medium user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Medium post (not available via API)"""
        try:
            logger.warning("Medium doesn't support post deletion via API")
            return False
                
        except Exception as e:
            logger.error(f"Error deleting Medium content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update Medium post (not available via API)"""
        try:
            logger.warning("Medium doesn't support post editing via API")
            return False
                
        except Exception as e:
            logger.error(f"Error updating Medium content: {e}")
            return False
    
    async def get_publications(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's publications"""
        try:
            target_user_id = user_id or self.config.credentials.get('user_id')
            if not target_user_id:
                return []
            
            result = await self._make_request('GET', f'/users/{target_user_id}/publications')
            
            if result and result.get('data'):
                publications = []
                for pub in result['data']:
                    publications.append({
                        'id': pub.get('id'),
                        'name': pub.get('name'),
                        'description': pub.get('description'),
                        'url': pub.get('url'),
                        'image_url': pub.get('imageUrl')
                    })
                return publications
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting publications: {e}")
            return []
    
    async def publish_to_publication(self, publication_id: str, metadata: ContentMetadata, 
                                   content_body: str) -> Optional[str]:
        """Publish article to a publication"""
        try:
            article_data = {
                'title': metadata.title,
                'contentFormat': 'html',
                'content': f"<p>{content_body}</p>",
                'publishStatus': 'public',
                'tags': metadata.tags[:5] if metadata.tags else []
            }
            
            result = await self._make_request('POST', f'/publications/{publication_id}/posts', 
                                            json=article_data)
            
            if result and result.get('data'):
                return result['data'].get('id')
            
            return None
            
        except Exception as e:
            logger.error(f"Error publishing to publication: {e}")
            return None
    
    async def get_user_info(self, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get Medium user information"""
        try:
            endpoint = '/me' if not user_id else f'/users/{user_id}'
            result = await self._make_request('GET', endpoint)
            
            if result and result.get('data'):
                user_data = result['data']
                return {
                    'id': user_data.get('id'),
                    'username': user_data.get('username'),
                    'name': user_data.get('name'),
                    'url': user_data.get('url'),
                    'image_url': user_data.get('imageUrl')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
