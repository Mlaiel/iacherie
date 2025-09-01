"""Reddit Platform Integration

Reddit API integration for community engagement and content sharing.

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
import base64

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus
)

logger = logging.getLogger(__name__)


class RedditPlatform(PlatformBase):
    """
Reddit platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """
Initialize Reddit platform"""
        super().__init__(config)
        self.api_base = "https://oauth.reddit.com"
        self.auth_url = "https://www.reddit.com/api/v1/access_token"
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
Authenticate with Reddit OAuth2"""
        try:
            session = await self._get_session()
            
            # Reddit uses OAuth2 with client credentials
            client_id = self.config.credentials.get('client_id')
            client_secret = self.config.credentials.get('client_secret')
            username = self.config.credentials.get('username')
            password = self.config.credentials.get('password')
            
            if not all([client_id, client_secret, username, password]):
                logger.error("Reddit requires client_id, client_secret, username, and password")
                return False
            
            # Create basic auth header
            auth_string = f"{client_id}:{client_secret}"
            auth_bytes = auth_string.encode('ascii')
            auth_header = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_header}',
                'User-Agent': f'IA-Influencer-Agent/1.0 by {username}'
            }
            
            data = {
                'grant_type': 'password',
                'username': username,
                'password': password
            }
            
            async with session.post(self.auth_url, headers=headers, data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.config.credentials['access_token'] = token_data['access_token']
                    self.config.credentials['token_type'] = token_data.get('token_type', 'bearer')
                    
                    # Set token expiration
                    expires_in = token_data.get('expires_in', 3600)
                    self.config.credentials['expires_at'] = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("Reddit authentication successful")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Reddit authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Reddit authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Reddit token"""
        return await self.authenticate()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
Make authenticated request to Reddit API"""
        try:
            session = await self._get_session()
            
            # Add authentication headers
            headers = kwargs.get('headers', {})
            if self.config.credentials.get('access_token'):
                token_type = self.config.credentials.get('token_type', 'bearer')
                headers['Authorization'] = f'{token_type} {self.config.credentials["access_token"]}'
            
            headers['User-Agent'] = f'IA-Influencer-Agent/1.0 by {self.config.credentials.get("username", "user")}'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 401:
                    # Token expired, refresh
                    if await self.refresh_token():
                        return await self._make_request(method, endpoint, **kwargs)
                    return None
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Reddit API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Reddit request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Submit content to Reddit (post to subreddit)"""
        try:
            subreddit = metadata.tags[0] if metadata.tags else 'test'
            
            # Determine post type based on content
            if content_path.startswith('http'):
                # URL post
                data = {
                    'api_type': 'json',
                    'kind': 'link',
                    'sr': subreddit,
                    'title': metadata.title,
                    'url': content_path
                }
            else:
                # Text post
                data = {
                    'api_type': 'json',
                    'kind': 'self',
                    'sr': subreddit,
                    'title': metadata.title,
                    'text': metadata.description or ''
                }
            
            result = await self._make_request('POST', '/api/submit', data=data)
            
            if result and result.get('json', {}).get('errors') == []:
                post_data = result['json']['data']
                
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=post_data.get('name'),
                    url=post_data.get('url'),
                    metadata={
                        'subreddit': subreddit,
                        'permalink': post_data.get('permalink'),
                        'id': post_data.get('id')
                    }
                )
            else:
                errors = result.get('json', {}).get('errors', []) if result else []
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error=f"Reddit submission failed: {errors}"
                )
                
        except Exception as e:
            logger.error(f"Reddit upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Reddit post analytics"""
        try:
            # Get post details
            post_data = await self._make_request('GET', f'/api/info?id={content_id}')
            
            if post_data and post_data.get('data', {}).get('children'):
                post = post_data['data']['children'][0]['data']
                
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=0,  # Reddit doesn't provide view counts
                    likes=post.get('ups', 0),
                    shares=0,  # Reddit doesn't track shares directly
                    comments=post.get('num_comments', 0),
                    metadata={
                        'downvotes': post.get('downs', 0),
                        'score': post.get('score', 0),
                        'upvote_ratio': post.get('upvote_ratio', 0),
                        'gilded': post.get('gilded', 0),
                        'awards_received': post.get('total_awards_received', 0),
                        'subreddit': post.get('subreddit'),
                        'author': post.get('author'),
                        'created_utc': post.get('created_utc'),
                        'is_original_content': post.get('is_original_content'),
                        'over_18': post.get('over_18'),
                        'stickied': post.get('stickied')
                    }
                )
            else:
                raise Exception("Post not found")
                
        except Exception as e:
            logger.error(f"Reddit analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Reddit"""
        try:
            params = {
                'q': query,
                'sort': 'relevance',
                'limit': 25,
                't': 'all'
            }
            
            result = await self._make_request('GET', '/search', params=params)
            
            if result and result.get('data', {}).get('children'):
                posts = []
                for item in result['data']['children']:
                    post_data = item['data']
                    posts.append({
                        'id': post_data.get('id'),
                        'title': post_data.get('title'),
                        'description': post_data.get('selftext', ''),
                        'url': post_data.get('url'),
                        'permalink': f"https://reddit.com{post_data.get('permalink', '')}",
                        'subreddit': post_data.get('subreddit'),
                        'author': post_data.get('author'),
                        'score': post_data.get('score', 0),
                        'num_comments': post_data.get('num_comments', 0),
                        'created_utc': post_data.get('created_utc'),
                        'thumbnail': post_data.get('thumbnail')
                    })
                return posts
            
            return []
            
        except Exception as e:
            logger.error(f"Reddit search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's posts from Reddit"""
        try:
            username = user_id or self.config.credentials.get('username')
            if not username:
                return []
            
            result = await self._make_request('GET', f'/user/{username}/submitted')
            
            if result and result.get('data', {}).get('children'):
                posts = []
                for item in result['data']['children']:
                    post_data = item['data']
                    posts.append({
                        'id': post_data.get('id'),
                        'name': post_data.get('name'),
                        'title': post_data.get('title'),
                        'selftext': post_data.get('selftext', ''),
                        'url': post_data.get('url'),
                        'permalink': post_data.get('permalink'),
                        'subreddit': post_data.get('subreddit'),
                        'score': post_data.get('score', 0),
                        'num_comments': post_data.get('num_comments', 0),
                        'created_utc': post_data.get('created_utc')
                    })
                return posts
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Reddit user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Reddit post"""
        try:
            data = {'id': content_id}
            result = await self._make_request('POST', '/api/del', data=data)
            
            if result and result.get('json', {}).get('errors') == []:
                logger.info(f"Successfully deleted Reddit post {content_id}")
                return True
            else:
                errors = result.get('json', {}).get('errors', []) if result else []
                logger.error(f"Failed to delete Reddit post: {errors}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting Reddit content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update Reddit post (edit text posts only)"""
        try:
            data = {
                'thing_id': content_id,
                'text': metadata.description or ''
            }
            
            result = await self._make_request('POST', '/api/editusertext', data=data)
            
            if result and result.get('json', {}).get('errors') == []:
                logger.info(f"Successfully updated Reddit post {content_id}")
                return True
            else:
                errors = result.get('json', {}).get('errors', []) if result else []
                logger.error(f"Failed to update Reddit post: {errors}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating Reddit content: {e}")
            return False
    
    async def get_subreddit_info(self, subreddit_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a subreddit"""
        try:
            result = await self._make_request('GET', f'/r/{subreddit_name}/about')
            
            if result and result.get('data'):
                data = result['data']
                return {
                    'name': data.get('display_name'),
                    'title': data.get('title'),
                    'description': data.get('public_description'),
                    'subscribers': data.get('subscribers'),
                    'active_users': data.get('active_user_count'),
                    'created_utc': data.get('created_utc'),
                    'over18': data.get('over18'),
                    'lang': data.get('lang'),
                    'url': data.get('url'),
                    'icon_img': data.get('icon_img'),
                    'banner_img': data.get('banner_img')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting subreddit info: {e}")
            return None
    
    async def get_trending_subreddits(self) -> List[Dict[str, Any]]:
        """Get trending subreddits"""
        try:
            result = await self._make_request('GET', '/subreddits/popular')
            
            if result and result.get('data', {}).get('children'):
                subreddits = []
                for item in result['data']['children']:
                    sub_data = item['data']
                    subreddits.append({
                        'name': sub_data.get('display_name'),
                        'title': sub_data.get('title'),
                        'subscribers': sub_data.get('subscribers'),
                        'description': sub_data.get('public_description'),
                        'url': sub_data.get('url')
                    })
                return subreddits
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting trending subreddits: {e}")
            return []
    
    async def post_comment(self, post_id: str, comment_text: str) -> Optional[str]:
        """Post a comment on a Reddit post"""
        try:
            data = {
                'api_type': 'json',
                'thing_id': post_id,
                'text': comment_text
            }
            
            result = await self._make_request('POST', '/api/comment', data=data)
            
            if result and result.get('json', {}).get('errors') == []:
                comment_data = result['json']['data']['things'][0]['data']
                return comment_data.get('name')
            else:
                errors = result.get('json', {}).get('errors', []) if result else []
                logger.error(f"Failed to post comment: {errors}")
                return None
                
        except Exception as e:
            logger.error(f"Error posting comment: {e}")
            return None
    
    async def vote_on_content(self, content_id: str, direction: int) -> bool:
        """Vote on Reddit content (1 = upvote, -1 = downvote, 0 = remove vote)"""
        try:
            data = {
                'id': content_id,
                'dir': str(direction)
            }
            
            result = await self._make_request('POST', '/api/vote', data=data)
            
            # Reddit voting API doesn't return JSON response on success
            return True
            
        except Exception as e:
            logger.error(f"Error voting on content: {e}")
            return False
    
    async def get_user_karma(self, username: str = None) -> Dict[str, Any]:
        """Get user karma breakdown"""
        try:
            user = username or self.config.credentials.get('username')
            result = await self._make_request('GET', f'/user/{user}/about')
            
            if result and result.get('data'):
                data = result['data']
                return {
                    'total_karma': data.get('total_karma', 0),
                    'link_karma': data.get('link_karma', 0),
                    'comment_karma': data.get('comment_karma', 0),
                    'awardee_karma': data.get('awardee_karma', 0),
                    'awarder_karma': data.get('awarder_karma', 0)
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting user karma: {e}")
            return {}
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
