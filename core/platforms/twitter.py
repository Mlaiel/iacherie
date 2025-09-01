"""Twitter/X Platform Integration

Twitter API v2 integration for social media engagement and content sharing.

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
import base64
import hashlib
import hmac
import time
import urllib.parse
import os

from .base import (
    PlatformBase, PlatformConfig, PlatformType, ContentType,
    ContentMetadata, UploadResult, AnalyticsData, PlatformStatus
)

logger = logging.getLogger(__name__)


class TwitterPlatform(PlatformBase):
    """
Twitter/X platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """
Initialize Twitter platform"""
        super().__init__(config)
        self.api_base = "https://api.twitter.com/2"
        self.upload_base = "https://upload.twitter.com/1.1"
        self.auth_base = "https://api.twitter.com"
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
Authenticate with Twitter using OAuth 2.0"""
        try:
            # If we have an access token, validate it
            if self.config.credentials.access_token:
                if await self._validate_token():
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    return True
            
            # For initial authentication, would need OAuth2 flow
            logger.error("Twitter authentication requires OAuth2 flow or valid access token")
            return False
            
        except Exception as e:
            logger.error(f"Twitter authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Twitter access token"""
        if not self.config.credentials.refresh_token:
            logger.error("No refresh token available for Twitter")
            return False
        
        try:
            session = await self._get_session()
            
            # Prepare client credentials
            client_creds = f"{self.config.credentials.client_id}:{self.config.credentials.client_secret}"
            client_creds_b64 = base64.b64encode(client_creds.encode()).decode()
            
            headers = {
                'Authorization': f'Basic {client_creds_b64}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            data = {
                'refresh_token': self.config.credentials.refresh_token,
                'grant_type': 'refresh_token'
            }
            
            async with session.post(
                f"{self.auth_base}/2/oauth2/token",
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.config.credentials.access_token = token_data['access_token']
                    
                    if 'refresh_token' in token_data:
                        self.config.credentials.refresh_token = token_data['refresh_token']
                    
                    expires_in = token_data.get('expires_in', 7200)
                    self.config.credentials.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                    
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("Twitter token refreshed successfully")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Twitter token refresh failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Twitter token refresh error: {e}")
            return False
    
    async def _validate_token(self) -> bool:
        """Validate Twitter access token"""
        try:
            result = await self._make_request('GET', '/users/me')
            return result is not None and result.get('data') is not None
            
        except Exception as e:
            logger.error(f"Twitter token validation error: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Twitter API"""
        if not self.is_authenticated:
            if not await self.authenticate():
                return None
        
        try:
            session = await self._get_session()
            
            # Prepare headers
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.config.credentials.access_token}'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}{endpoint}" if endpoint.startswith('/') else f"{self.api_base}/{endpoint}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    # Token expired, try to refresh
                    if await self.refresh_token():
                        headers['Authorization'] = f'Bearer {self.config.credentials.access_token}'
                        async with session.request(method, url, **kwargs) as retry_response:
                            if retry_response.status in [200, 201]:
                                return await retry_response.json()
                    return None
                
                elif response.status == 429:
                    # Rate limited
                    reset_time = response.headers.get('x-rate-limit-reset')
                    if reset_time:
                        wait_time = int(reset_time) - int(time.time())
                        await self.handle_rate_limit(max(wait_time, 60))
                    else:
                        await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Twitter API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Twitter request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload content to Twitter"""
        try:
            if not os.path.exists(content_path):
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Content file not found"
                )
            
            # Determine content type
            mime_type = mimetypes.guess_type(content_path)[0]
            is_video = mime_type and mime_type.startswith('video/')
            is_image = mime_type and mime_type.startswith('image/')
            
            media_ids = []
            
            if is_image or is_video:
                # Upload media first
                media_id = await self._upload_media(content_path, mime_type)
                if not media_id:
                    return UploadResult(
                        success=False,
                        platform_id=self.platform_id,
                        error="Failed to upload media"
                    )
                media_ids.append(media_id)
            
            # Create tweet
            tweet_text = f"{metadata.title}\n\n{metadata.description}"
            if metadata.tags:
                hashtags = ' '.join(f'#{tag.replace(" ", "")}' for tag in metadata.tags[:5])  # Max 5 hashtags
                tweet_text += f"\n\n{hashtags}"
            
            # Truncate if too long
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."
            
            tweet_data = {
                'text': tweet_text
            }
            
            if media_ids:
                tweet_data['media'] = {'media_ids': media_ids}
            
            result = await self._make_request(
                'POST',
                '/tweets',
                json=tweet_data
            )
            
            if not result or not result.get('data'):
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Failed to create tweet"
                )
            
            tweet_id = result['data']['id']
            username = await self._get_username()
            
            return UploadResult(
                success=True,
                platform_id=self.platform_id,
                content_id=tweet_id,
                url=f"https://twitter.com/{username}/status/{tweet_id}",
                message="Tweet posted successfully",
                metadata={
                    'tweet_id': tweet_id,
                    'text': result['data']['text'],
                    'media_ids': media_ids
                }
            )
            
        except Exception as e:
            logger.error(f"Twitter upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def _upload_media(self, file_path: str, mime_type: str) -> Optional[str]:
        """Upload media to Twitter"""
        try:
            session = await self._get_session()
            
            async with aiofiles.open(file_path, 'rb') as media_file:
                media_data = await media_file.read()
            
            # Initialize upload
            headers = {
                'Authorization': f'Bearer {self.config.credentials.access_token}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            init_data = {
                'command': 'INIT',
                'total_bytes': len(media_data),
                'media_type': mime_type
            }
            
            async with session.post(
                f"{self.upload_base}/media/upload.json",
                headers=headers,
                data=init_data
            ) as response:
                if response.status != 200:
                    return None
                
                init_result = await response.json()
                media_id = init_result['media_id_string']
            
            # Upload media chunks
            chunk_size = 1024 * 1024  # 1MB chunks
            segment_index = 0
            
            for i in range(0, len(media_data), chunk_size):
                chunk = media_data[i:i + chunk_size]
                
                append_data = {
                    'command': 'APPEND',
                    'media_id': media_id,
                    'segment_index': segment_index
                }
                
                files = {'media': chunk}
                
                async with session.post(
                    f"{self.upload_base}/media/upload.json",
                    headers={'Authorization': f'Bearer {self.config.credentials.access_token}'},
                    data=append_data
                ) as response:
                    if response.status != 204:
                        return None
                
                segment_index += 1
            
            # Finalize upload
            finalize_data = {
                'command': 'FINALIZE',
                'media_id': media_id
            }
            
            async with session.post(
                f"{self.upload_base}/media/upload.json",
                headers=headers,
                data=finalize_data
            ) as response:
                if response.status == 200:
                    return media_id
                
            return None
            
        except Exception as e:
            logger.error(f"Twitter media upload error: {e}")
            return None
    
    async def _get_username(self) -> str:
        """Get current user's username"""
        try:
            result = await self._make_request('GET', '/users/me')
            if result and result.get('data'):
                return result['data'].get('username', 'unknown')
            return 'unknown'
        except:
            return 'unknown'
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """
Get Twitter analytics for a tweet"""
        try:
            # Get tweet data
            params = {
                'tweet.fields': 'public_metrics,created_at,author_id',
                'expansions': 'author_id'
            }
            
            result = await self._make_request(
                'GET',
                f'/tweets/{content_id}',
                params=params
            )
            
            if not result or not result.get('data'):
                raise Exception(f"Tweet {content_id} not found")
            
            tweet = result['data']
            metrics = tweet.get('public_metrics', {})
            
            return AnalyticsData(
                platform_id=self.platform_id,
                content_id=content_id,
                views=metrics.get('impression_count', 0),
                likes=metrics.get('like_count', 0),
                shares=metrics.get('retweet_count', 0),
                comments=metrics.get('reply_count', 0),
                engagement_rate=self._calculate_engagement_rate(metrics),
                metadata={
                    'text': tweet.get('text'),
                    'created_at': tweet.get('created_at'),
                    'author_id': tweet.get('author_id'),
                    'quote_count': metrics.get('quote_count', 0),
                    'bookmark_count': metrics.get('bookmark_count', 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Twitter analytics error: {e}")
            raise
    
    def _calculate_engagement_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate engagement rate"""
        impressions = metrics.get('impression_count', 0)
        likes = metrics.get('like_count', 0)
        retweets = metrics.get('retweet_count', 0)
        replies = metrics.get('reply_count', 0)
        quotes = metrics.get('quote_count', 0)
        
        if impressions == 0:
            return 0.0
        
        total_engagement = likes + retweets + replies + quotes
        return (total_engagement / impressions) * 100
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """
Search content on Twitter"""
        try:
            params = {
                'query': query,
                'tweet.fields': 'public_metrics,created_at,author_id',
                'expansions': 'author_id',
                'max_results': 100
            }
            
            result = await self._make_request(
                'GET',
                '/tweets/search/recent',
                params=params
            )
            
            if not result or not result.get('data'):
                return []
            
            tweets = []
            users = {user['id']: user for user in result.get('includes', {}).get('users', [])}
            
            for tweet in result['data']:
                author = users.get(tweet.get('author_id'), {})
                metrics = tweet.get('public_metrics', {})
                
                tweets.append({
                    'id': tweet.get('id'),
                    'text': tweet.get('text'),
                    'created_at': tweet.get('created_at'),
                    'author_id': tweet.get('author_id'),
                    'author_username': author.get('username'),
                    'author_name': author.get('name'),
                    'like_count': metrics.get('like_count', 0),
                    'retweet_count': metrics.get('retweet_count', 0),
                    'reply_count': metrics.get('reply_count', 0),
                    'quote_count': metrics.get('quote_count', 0)
                })
            
            return tweets
            
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's tweets from Twitter"""
        try:
            if not user_id:
                # Get current user ID
                me_result = await self._make_request('GET', '/users/me')
                if not me_result or not me_result.get('data'):
                    return []
                user_id = me_result['data']['id']
            
            params = {
                'tweet.fields': 'public_metrics,created_at',
                'max_results': 100
            }
            
            result = await self._make_request(
                'GET',
                f'/users/{user_id}/tweets',
                params=params
            )
            
            if not result or not result.get('data'):
                return []
            
            tweets = []
            for tweet in result['data']:
                metrics = tweet.get('public_metrics', {})
                tweets.append({
                    'id': tweet.get('id'),
                    'text': tweet.get('text'),
                    'created_at': tweet.get('created_at'),
                    'like_count': metrics.get('like_count', 0),
                    'retweet_count': metrics.get('retweet_count', 0),
                    'reply_count': metrics.get('reply_count', 0),
                    'quote_count': metrics.get('quote_count', 0),
                    'impression_count': metrics.get('impression_count', 0)
                })
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error getting Twitter user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete tweet from Twitter"""
        try:
            result = await self._make_request('DELETE', f'/tweets/{content_id}')
            return result is not None and result.get('data', {}).get('deleted') is True
        except Exception as e:
            logger.error(f"Error deleting Twitter content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update tweet metadata on Twitter (not supported)"""
        # Twitter doesn't support editing tweets
        logger.warning("Twitter doesn't support editing tweets")
        return False
    
    async def get_user_info(self, user_id: str = None, username: str = None) -> Optional[Dict[str, Any]]:
        """Get user information"""
        try:
            params = {
                'user.fields': 'public_metrics,description,location,url,verified,created_at'
            }
            
            if user_id:
                endpoint = f'/users/{user_id}'
            elif username:
                endpoint = f'/users/by/username/{username}'
            else:
                endpoint = '/users/me'
            
            return await self._make_request('GET', endpoint, params=params)
            
        except Exception as e:
            logger.error(f"Error getting Twitter user info: {e}")
            return None
    
    async def follow_user(self, target_user_id: str) -> bool:
        """Follow a user"""
        try:
            data = {'target_user_id': target_user_id}
            result = await self._make_request('POST', '/users/{id}/following', json=data)
            return result is not None and result.get('data', {}).get('following') is True
        except Exception as e:
            logger.error(f"Error following Twitter user: {e}")
            return False
    
    async def unfollow_user(self, target_user_id: str) -> bool:
        """Unfollow a user"""
        try:
            result = await self._make_request('DELETE', f'/users/{self.config.credentials.user_id}/following/{target_user_id}')
            return result is not None and result.get('data', {}).get('following') is False
        except Exception as e:
            logger.error(f"Error unfollowing Twitter user: {e}")
            return False
    
    async def like_tweet(self, tweet_id: str) -> bool:
        """Like a tweet"""
        try:
            data = {'tweet_id': tweet_id}
            result = await self._make_request('POST', '/users/{id}/likes', json=data)
            return result is not None and result.get('data', {}).get('liked') is True
        except Exception as e:
            logger.error(f"Error liking Twitter tweet: {e}")
            return False
    
    async def retweet(self, tweet_id: str) -> bool:
        """Retweet a tweet"""
        try:
            data = {'tweet_id': tweet_id}
            result = await self._make_request('POST', '/users/{id}/retweets', json=data)
            return result is not None and result.get('data', {}).get('retweeted') is True
        except Exception as e:
            logger.error(f"Error retweeting Twitter tweet: {e}")
            return False
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
