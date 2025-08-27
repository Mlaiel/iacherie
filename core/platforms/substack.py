"""
Substack Platform Integration

Substack API integration for newsletter publishing platform.

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


class SubstackPlatform(PlatformBase):
    """Substack platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """Initialize Substack platform"""
        super().__init__(config)
        
        # Substack uses publication-specific API endpoints
        self.publication_url = config.credentials.get('publication_url', '')
        if self.publication_url:
            self.api_base = f"{self.publication_url}/api/v1"
        else:
            self.api_base = "https://substack.com/api/v1"
        
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Substack"""
        try:
            # Substack uses email/password or API key authentication
            api_key = self.config.credentials.get('api_key')
            email = self.config.credentials.get('email')
            password = self.config.credentials.get('password')
            
            if api_key:
                # API key authentication
                session = await self._get_session()
                headers = {
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                }
                
                async with session.get(f"{self.api_base}/user", headers=headers) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        self.config.credentials['user_id'] = str(user_data.get('id'))
                        self.config.credentials['username'] = user_data.get('handle')
                        
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info("Substack authentication successful (API key)")
                        return True
                    else:
                        logger.error("Substack API key validation failed")
                        return False
                        
            elif email and password:
                # Email/password authentication
                success = await self._login_with_credentials(email, password)
                if success:
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("Substack authentication successful (credentials)")
                    return True
                else:
                    logger.error("Substack credential authentication failed")
                    return False
            else:
                logger.error("Substack requires api_key or email/password")
                return False
                
        except Exception as e:
            logger.error(f"Substack authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def _login_with_credentials(self, email: str, password: str) -> bool:
        """Login with email and password"""
        try:
            session = await self._get_session()
            
            login_data = {
                'email': email,
                'password': password,
                'captcha_response': None
            }
            
            async with session.post(f"{self.api_base}/login", json=login_data) as response:
                if response.status == 200:
                    result = await response.json()
                    self.config.credentials['access_token'] = result.get('token')
                    self.config.credentials['user_id'] = str(result.get('user_id'))
                    return True
                else:
                    logger.error(f"Substack login failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Substack login error: {e}")
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Substack token"""
        return await self.authenticate()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Substack API"""
        try:
            session = await self._get_session()
            
            headers = kwargs.get('headers', {})
            
            # Try API key first, then access token
            api_key = self.config.credentials.get('api_key')
            access_token = self.config.credentials.get('access_token')
            
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            elif access_token:
                headers['Authorization'] = f'Bearer {access_token}'
            
            headers['Content-Type'] = 'application/json'
            headers['User-Agent'] = 'IAInfluencerAgent/1.0'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 401:
                    logger.error("Substack authentication failed")
                    self.increment_error_count()
                    return None
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Substack API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Substack request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Publish article on Substack"""
        try:
            # Read content if file provided
            content_body = ""
            if content_path:
                try:
                    with open(content_path, 'r', encoding='utf-8') as f:
                        content_body = f.read()
                except FileNotFoundError:
                    content_body = content_path  # Treat as direct content
            
            if not content_body:
                content_body = metadata.description or ""
            
            # Prepare post data
            post_data = {
                'title': metadata.title,
                'subtitle': metadata.description[:100] if metadata.description else "",
                'type': 'newsletter',  # newsletter, podcast, thread
                'audience': 'everyone',  # everyone, only_paid, only_founding
                'email_sent_at': None,  # For drafts
                'draft': True,  # Start as draft
                'cover_image': None,
                'podcast_duration': None,
                'podcast_upload_id': None,
                'podcast_url': None,
                'podcast_preview_upload_id': None,
                'section_chosen': False,
                'section_id': None,
                'slug': None,
                'word_count': len(content_body.split()),
                'description': metadata.description or "",
                'canonical_url': content_path if content_path and content_path.startswith('http') else None,
                'body_json': json.dumps({
                    'blocks': [
                        {
                            'key': 'content',
                            'text': content_body,
                            'type': 'unstyled',
                            'depth': 0,
                            'inlineStyleRanges': [],
                            'entityRanges': [],
                            'data': {}
                        }
                    ],
                    'entityMap': {}
                })
            }
            
            # Create draft first
            result = await self._make_request('POST', '/posts', json=post_data)
            
            if result and result.get('id'):
                post_id = result['id']
                
                # Publish if not keeping as draft
                if not metadata.draft if hasattr(metadata, 'draft') else True:
                    publish_result = await self._publish_post(post_id)
                    if publish_result:
                        result.update(publish_result)
                
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=str(post_id),
                    url=result.get('canonical_url') or f"{self.publication_url}/p/{result.get('slug')}",
                    metadata={
                        'title': result.get('title'),
                        'subtitle': result.get('subtitle'),
                        'slug': result.get('slug'),
                        'type': result.get('type'),
                        'audience': result.get('audience'),
                        'draft': result.get('draft', True),
                        'word_count': result.get('word_count', 0),
                        'reactions': result.get('reactions', {}),
                        'comment_count': result.get('comment_count', 0)
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Substack post creation failed"
                )
                
        except Exception as e:
            logger.error(f"Substack upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def _publish_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Publish a draft post"""
        try:
            publish_data = {
                'email_sent_at': datetime.utcnow().isoformat() + 'Z',
                'draft': False
            }
            
            result = await self._make_request('PUT', f'/posts/{post_id}', json=publish_data)
            return result
            
        except Exception as e:
            logger.error(f"Error publishing post: {e}")
            return None
    
    async def get_analytics(self, content_id: str, start_date: datetime, 
                           end_date: datetime) -> AnalyticsData:
        """Get Substack post analytics"""
        try:
            result = await self._make_request('GET', f'/posts/{content_id}')
            
            if result:
                reactions = result.get('reactions', {})
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=result.get('view_count', 0),
                    likes=reactions.get('❤️', 0),
                    shares=result.get('share_count', 0),
                    comments=result.get('comment_count', 0),
                    metadata={
                        'email_opens': result.get('email_opens', 0),
                        'email_clicks': result.get('email_clicks', 0),
                        'subscribers_gained': result.get('subscribers_gained', 0),
                        'reactions': reactions,
                        'word_count': result.get('word_count', 0),
                        'read_time': result.get('read_time', 0),
                        'audience': result.get('audience'),
                        'type': result.get('type')
                    }
                )
            else:
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id
                )
                
        except Exception as e:
            logger.error(f"Substack analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Substack"""
        try:
            params = {
                'q': query,
                'limit': 20
            }
            
            result = await self._make_request('GET', '/search', params=params)
            
            if result and result.get('posts'):
                posts = []
                for post in result['posts']:
                    posts.append({
                        'id': post.get('id'),
                        'title': post.get('title'),
                        'subtitle': post.get('subtitle'),
                        'slug': post.get('slug'),
                        'type': post.get('type'),
                        'audience': post.get('audience'),
                        'post_date': post.get('post_date'),
                        'cover_image': post.get('cover_image'),
                        'word_count': post.get('word_count', 0),
                        'comment_count': post.get('comment_count', 0),
                        'canonical_url': post.get('canonical_url')
                    })
                return posts
            
            return []
            
        except Exception as e:
            logger.error(f"Substack search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's Substack posts"""
        try:
            params = {
                'limit': 50,
                'offset': 0,
                'sort': 'new'
            }
            
            result = await self._make_request('GET', '/posts', params=params)
            
            if result and result.get('posts'):
                posts = []
                for post in result['posts']:
                    posts.append({
                        'id': post.get('id'),
                        'title': post.get('title'),
                        'subtitle': post.get('subtitle'),
                        'slug': post.get('slug'),
                        'type': post.get('type'),
                        'audience': post.get('audience'),
                        'draft': post.get('draft', False),
                        'post_date': post.get('post_date'),
                        'cover_image': post.get('cover_image'),
                        'word_count': post.get('word_count', 0),
                        'view_count': post.get('view_count', 0),
                        'comment_count': post.get('comment_count', 0),
                        'reactions': post.get('reactions', {}),
                        'canonical_url': post.get('canonical_url')
                    })
                return posts
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Substack user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Substack post"""
        try:
            result = await self._make_request('DELETE', f'/posts/{content_id}')
            return result is not None
                
        except Exception as e:
            logger.error(f"Error deleting Substack content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update Substack post"""
        try:
            update_data = {
                'title': metadata.title,
                'subtitle': metadata.description[:100] if metadata.description else "",
                'description': metadata.description or ""
            }
            
            result = await self._make_request('PUT', f'/posts/{content_id}', json=update_data)
            return result is not None
                
        except Exception as e:
            logger.error(f"Error updating Substack content: {e}")
            return False
    
    async def get_subscribers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get publication subscribers"""
        try:
            params = {
                'limit': limit,
                'offset': 0,
                'sort': 'created_at'
            }
            
            result = await self._make_request('GET', '/subscribers', params=params)
            
            if result and result.get('subscribers'):
                subscribers = []
                for subscriber in result['subscribers']:
                    subscribers.append({
                        'id': subscriber.get('id'),
                        'email': subscriber.get('email'),
                        'created_at': subscriber.get('created_at'),
                        'stripe_customer_id': subscriber.get('stripe_customer_id'),
                        'comp_subscription': subscriber.get('comp_subscription'),
                        'paid_subscription': subscriber.get('paid_subscription'),
                        'founding_subscription': subscriber.get('founding_subscription'),
                        'email_disabled': subscriber.get('email_disabled', False)
                    })
                return subscribers
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting subscribers: {e}")
            return []
    
    async def get_publication_stats(self) -> Optional[Dict[str, Any]]:
        """Get publication statistics"""
        try:
            result = await self._make_request('GET', '/pub')
            
            if result:
                return {
                    'id': result.get('id'),
                    'name': result.get('name'),
                    'subdomain': result.get('subdomain'),
                    'custom_domain': result.get('custom_domain'),
                    'hero_text': result.get('hero_text'),
                    'hero_image': result.get('hero_image'),
                    'logo': result.get('logo'),
                    'author_id': result.get('author_id'),
                    'theme': result.get('theme'),
                    'stripe_user_id': result.get('stripe_user_id'),
                    'stripe_country': result.get('stripe_country'),
                    'stripe_publishable_key': result.get('stripe_publishable_key'),
                    'subscriber_count': result.get('subscriber_count', 0),
                    'paid_subscriber_count': result.get('paid_subscriber_count', 0),
                    'founding_subscriber_count': result.get('founding_subscriber_count', 0),
                    'post_count': result.get('post_count', 0),
                    'email_enabled': result.get('email_enabled', False),
                    'payments_enabled': result.get('payments_enabled', False)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting publication stats: {e}")
            return None
    
    async def send_newsletter(self, post_id: str, audience: str = 'everyone') -> bool:
        """Send newsletter to subscribers"""
        try:
            send_data = {
                'audience': audience,  # everyone, only_paid, only_founding
                'email_sent_at': datetime.utcnow().isoformat() + 'Z'
            }
            
            result = await self._make_request('POST', f'/posts/{post_id}/email', json=send_data)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error sending newsletter: {e}")
            return False
    
    async def get_email_stats(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get email statistics for a post"""
        try:
            result = await self._make_request('GET', f'/posts/{post_id}/email_stats')
            
            if result:
                return {
                    'sent_count': result.get('sent_count', 0),
                    'delivered_count': result.get('delivered_count', 0),
                    'opened_count': result.get('opened_count', 0),
                    'clicked_count': result.get('clicked_count', 0),
                    'unsubscribed_count': result.get('unsubscribed_count', 0),
                    'open_rate': result.get('open_rate', 0.0),
                    'click_rate': result.get('click_rate', 0.0),
                    'unsubscribe_rate': result.get('unsubscribe_rate', 0.0)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting email stats: {e}")
            return None
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
