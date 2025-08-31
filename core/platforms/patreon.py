"""Patreon Platform Integration

Patreon API integration for creator membership platform.

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


class PatreonPlatform(PlatformBase):
    """Patreon platform integration"""    
    def __init__(self, config: PlatformConfig):
        """Initialize Patreon platform"""        super().__init__(config)
        self.api_base = "https://www.patreon.com/api/oauth2/v2"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with Patreon OAuth2"""        try:
            access_token = self.config.credentials.get('access_token')
            
            if access_token:
                session = await self._get_session()
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                params = {
                    'fields[user]': 'email,first_name,last_name,full_name,is_email_verified,vanity,url'
                }
                
                async with session.get(f"{self.api_base}/identity", 
                                     headers=headers, params=params) as response:
                    if response.status == 200:
                        user_data = await response.json()
                        user_attributes = user_data['data']['attributes']
                        
                        self.config.credentials['user_id'] = user_data['data']['id']
                        self.config.credentials['username'] = user_attributes.get('vanity')
                        self.config.credentials['email'] = user_attributes.get('email')
                        
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info("Patreon authentication successful")
                        return True
                    else:
                        logger.error("Patreon token validation failed")
                        return False
            else:
                logger.error("Patreon requires access_token")
                return False
                
        except Exception as e:
            logger.error(f"Patreon authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Patreon token"""        try:
            refresh_token = self.config.credentials.get('refresh_token')
            client_id = self.config.credentials.get('client_id')
            client_secret = self.config.credentials.get('client_secret')
            
            if not all([refresh_token, client_id, client_secret]):
                return False
            
            session = await self._get_session()
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': client_id,
                'client_secret': client_secret
            }
            
            async with session.post('https://www.patreon.com/api/oauth2/token', 
                                  json=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.config.credentials['access_token'] = token_data.get('access_token')
                    self.config.credentials['refresh_token'] = token_data.get('refresh_token')
                    return True
                else:
                    logger.error("Patreon token refresh failed")
                    return False
                    
        except Exception as e:
            logger.error(f"Patreon token refresh error: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Patreon API"""        try:
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
                    # Try to refresh token
                    if await self.refresh_token():
                        headers['Authorization'] = f'Bearer {self.config.credentials["access_token"]}'
                        kwargs['headers'] = headers
                        return await self._make_request(method, endpoint, **kwargs)
                    else:
                        logger.error("Patreon authentication failed")
                        self.increment_error_count()
                        return None
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Patreon API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"Patreon request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Create Patreon post"""        try:
            # Get campaign ID first
            campaign_id = await self._get_campaign_id()
            if not campaign_id:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Campaign ID not found"
                )
            
            # Prepare post data
            post_data = {
                'data': {
                    'type': 'post',
                    'attributes': {
                        'title': metadata.title,
                        'content': metadata.description or '',
                        'is_paid': True,
                        'is_public': False,
                        'published_at': datetime.utcnow().isoformat() + 'Z'
                    },
                    'relationships': {
                        'campaign': {
                            'data': {
                                'type': 'campaign',
                                'id': campaign_id
                            }
                        }
                    }
                }
            }
            
            # Add tier restrictions if specified
            if hasattr(metadata, 'tier_ids') and metadata.tier_ids:
                post_data['data']['relationships']['tiers'] = {
                    'data': [{'type': 'tier', 'id': tier_id} for tier_id in metadata.tier_ids]
                }
            
            params = {
                'fields[post]': 'content,is_paid,is_public,published_at,title,url,embed_data,embed_url,app_id,app_status',
                'fields[user]': 'full_name,url',
                'fields[campaign]': 'creation_name,url',
                'include': 'user,campaign,attachments'
            }
            
            result = await self._make_request('POST', '/posts', json=post_data, params=params)
            
            if result and result.get('data'):
                post = result['data']
                attributes = post.get('attributes', {})
                
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=post.get('id'),
                    url=attributes.get('url'),
                    metadata={
                        'title': attributes.get('title'),
                        'published_at': attributes.get('published_at'),
                        'is_paid': attributes.get('is_paid'),
                        'is_public': attributes.get('is_public'),
                        'like_count': attributes.get('like_count', 0),
                        'comment_count': attributes.get('comment_count', 0)
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Patreon post creation failed"
                )
                
        except Exception as e:
            logger.error(f"Patreon upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def _get_campaign_id(self) -> Optional[str]:
        """Get user's campaign ID"""        try:
            user_id = self.config.credentials.get('user_id')
            if not user_id:
                return None
            
            params = {
                'fields[campaign]': 'creation_name,url,patron_count,creation_count',
                'include': 'campaign'
            }
            
            result = await self._make_request('GET', f'/members/{user_id}', params=params)
            
            if result and result.get('included'):
                for item in result['included']:
                    if item.get('type') == 'campaign':
                        return item.get('id')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting campaign ID: {e}")
            return None
    
    async def get_analytics(self, content_id: str, start_date: datetime, 
                           end_date: datetime) -> AnalyticsData:
        """Get Patreon post analytics"""        try:
            params = {
                'fields[post]': 'like_count,comment_count,published_at,title,content',
                'include': 'user,campaign'
            }
            
            result = await self._make_request('GET', f'/posts/{content_id}', params=params)
            
            if result and result.get('data'):
                attributes = result['data'].get('attributes', {})
                
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=0,  # Not available in Patreon API
                    likes=attributes.get('like_count', 0),
                    shares=0,  # Not available
                    comments=attributes.get('comment_count', 0),
                    metadata={
                        'like_count': attributes.get('like_count', 0),
                        'comment_count': attributes.get('comment_count', 0),
                        'published_at': attributes.get('published_at'),
                        'is_paid': attributes.get('is_paid'),
                        'is_public': attributes.get('is_public')
                    }
                )
            else:
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id
                )
                
        except Exception as e:
            logger.error(f"Patreon analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Patreon (limited API support)"""        try:
            # Patreon doesn't have a public search API
            logger.warning("Patreon doesn't support content search via API")
            return []
            
        except Exception as e:
            logger.error(f"Patreon search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's Patreon posts"""        try:
            campaign_id = await self._get_campaign_id()
            if not campaign_id:
                return []
            
            params = {
                'fields[post]': 'content,is_paid,is_public,published_at,title,url,like_count,comment_count',
                'filter[campaign_id]': campaign_id,
                'sort': '-published_at'
            }
            
            result = await self._make_request('GET', '/posts', params=params)
            
            if result and result.get('data'):
                posts = []
                for post in result['data']:
                    attributes = post.get('attributes', {})
                    posts.append({
                        'id': post.get('id'),
                        'title': attributes.get('title'),
                        'content': attributes.get('content'),
                        'published_at': attributes.get('published_at'),
                        'url': attributes.get('url'),
                        'is_paid': attributes.get('is_paid'),
                        'is_public': attributes.get('is_public'),
                        'like_count': attributes.get('like_count', 0),
                        'comment_count': attributes.get('comment_count', 0)
                    })
                return posts
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Patreon user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Patreon post"""        try:
            result = await self._make_request('DELETE', f'/posts/{content_id}')
            return result is not None
                
        except Exception as e:
            logger.error(f"Error deleting Patreon content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update Patreon post"""        try:
            update_data = {
                'data': {
                    'type': 'post',
                    'id': content_id,
                    'attributes': {
                        'title': metadata.title,
                        'content': metadata.description or ''
                    }
                }
            }
            
            params = {
                'fields[post]': 'content,title,published_at,url'
            }
            
            result = await self._make_request('PATCH', f'/posts/{content_id}', 
                                            json=update_data, params=params)
            return result is not None
                
        except Exception as e:
            logger.error(f"Error updating Patreon content: {e}")
            return False
    
    async def get_patrons(self, campaign_id: str = None) -> List[Dict[str, Any]]:
        """Get campaign patrons"""        try:
            target_campaign_id = campaign_id or await self._get_campaign_id()
            if not target_campaign_id:
                return []
            
            params = {
                'fields[member]': 'currently_entitled_amount_cents,lifetime_support_cents,last_charge_status,patron_status,last_charge_date,pledge_relationship_start',
                'fields[user]': 'first_name,full_name,email,thumb_url',
                'filter[campaign_id]': target_campaign_id,
                'include': 'user,currently_entitled_tiers'
            }
            
            result = await self._make_request('GET', '/members', params=params)
            
            if result and result.get('data'):
                patrons = []
                for member in result['data']:
                    attributes = member.get('attributes', {})
                    
                    # Find user data in included
                    user_data = {}
                    if result.get('included'):
                        for item in result['included']:
                            if item.get('type') == 'user' and item.get('id') == member.get('relationships', {}).get('user', {}).get('data', {}).get('id'):
                                user_data = item.get('attributes', {})
                                break
                    
                    patrons.append({
                        'id': member.get('id'),
                        'user_id': member.get('relationships', {}).get('user', {}).get('data', {}).get('id'),
                        'full_name': user_data.get('full_name', ''),
                        'email': user_data.get('email', ''),
                        'thumb_url': user_data.get('thumb_url'),
                        'currently_entitled_amount_cents': attributes.get('currently_entitled_amount_cents', 0),
                        'lifetime_support_cents': attributes.get('lifetime_support_cents', 0),
                        'last_charge_status': attributes.get('last_charge_status'),
                        'patron_status': attributes.get('patron_status'),
                        'pledge_relationship_start': attributes.get('pledge_relationship_start')
                    })
                return patrons
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting patrons: {e}")
            return []
    
    async def get_campaign_info(self, campaign_id: str = None) -> Optional[Dict[str, Any]]:
        """Get campaign information"""        try:
            target_campaign_id = campaign_id or await self._get_campaign_id()
            if not target_campaign_id:
                return None
            
            params = {
                'fields[campaign]': 'creation_name,creation_count,published_at,patron_count,creation_count,main_video_embed,main_video_url,image_small_url,image_url,thanks_video_url,summary,pay_per_name,one_liner,created_at,url'
            }
            
            result = await self._make_request('GET', f'/campaigns/{target_campaign_id}', params=params)
            
            if result and result.get('data'):
                attributes = result['data'].get('attributes', {})
                return {
                    'id': result['data'].get('id'),
                    'creation_name': attributes.get('creation_name'),
                    'summary': attributes.get('summary'),
                    'patron_count': attributes.get('patron_count', 0),
                    'creation_count': attributes.get('creation_count', 0),
                    'published_at': attributes.get('published_at'),
                    'url': attributes.get('url'),
                    'image_url': attributes.get('image_url'),
                    'main_video_url': attributes.get('main_video_url'),
                    'pay_per_name': attributes.get('pay_per_name'),
                    'one_liner': attributes.get('one_liner')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting campaign info: {e}")
            return None
    
    async def get_tiers(self, campaign_id: str = None) -> List[Dict[str, Any]]:
        """Get campaign tiers"""        try:
            target_campaign_id = campaign_id or await self._get_campaign_id()
            if not target_campaign_id:
                return []
            
            params = {
                'fields[tier]': 'amount_cents,created_at,description,discord_role_ids,edited_at,patron_count,published,published_at,remaining,requires_shipping,title,url,user_limit',
                'filter[campaign_id]': target_campaign_id
            }
            
            result = await self._make_request('GET', '/tiers', params=params)
            
            if result and result.get('data'):
                tiers = []
                for tier in result['data']:
                    attributes = tier.get('attributes', {})
                    tiers.append({
                        'id': tier.get('id'),
                        'title': attributes.get('title'),
                        'description': attributes.get('description'),
                        'amount_cents': attributes.get('amount_cents', 0),
                        'patron_count': attributes.get('patron_count', 0),
                        'published': attributes.get('published', False),
                        'user_limit': attributes.get('user_limit'),
                        'requires_shipping': attributes.get('requires_shipping', False),
                        'url': attributes.get('url'),
                        'created_at': attributes.get('created_at')
                    })
                return tiers
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting tiers: {e}")
            return []
    
    async def close(self):
        """Close HTTP session"""        if self.session and not self.session.closed:
            await self.session.close()
