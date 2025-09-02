"""Snapchat Platform Integration

Snapchat API integration for multimedia content sharing and analytics.

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


class SnapchatPlatform(PlatformBase):
    """
Snapchat platform integration"""
    
    def __init__(self, config: PlatformConfig):
        """
        try:
            logger.info(f"Executing __init__")
            
            # Implement operation logic
            result = await self._execute_operation()
            
            logger.info(f"__init__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__init__ failed: {e}")
            raise
Initialize Snapchat platform"""
        super().__init__(config)
        self.api_base = "https://adsapi.snapchat.com/v1"
        self.marketing_api_base = "https://marketingapi.snapchat.com/v1"
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
Authenticate with Snapchat OAuth2"""
        try:
            access_token = self.config.credentials.get('access_token')
            
            if access_token:
                # Test token validity
                session = await self._get_session()
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                async with session.get(f"{self.api_base}/me", headers=headers) as response:
                    if response.status == 200:
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info("Snapchat authentication successful")
                        return True
                    else:
                        logger.error("Snapchat token validation failed")
                        return False
            else:
                logger.error("Snapchat requires valid access_token")
                return False
                
        except Exception as e:
            logger.error(f"Snapchat authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh Snapchat token"""
        try:
            refresh_token = self.config.credentials.get('refresh_token')
            client_id = self.config.credentials.get('client_id')
            client_secret = self.config.credentials.get('client_secret')
            
            if not all([refresh_token, client_id, client_secret]):
                return await self.authenticate()
            
            session = await self._get_session()
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': client_id,
                'client_secret': client_secret
            }
            
            async with session.post('https://accounts.snapchat.com/login/oauth2/access_token', data=data) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.config.credentials['access_token'] = token_data['access_token']
                    if 'refresh_token' in token_data:
                        self.config.credentials['refresh_token'] = token_data['refresh_token']
                    
                    self.status = PlatformStatus.ACTIVE
                    self.reset_error_count()
                    logger.info("Snapchat token refreshed successfully")
                    return True
                else:
                    logger.error("Snapchat token refresh failed")
                    return False
                    
        except Exception as e:
            logger.error(f"Snapchat token refresh error: {e}")
            return False
    
    async def _make_request(self, method: str, endpoint: str, use_marketing_api: bool = False, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Snapchat API"""
        try:
            session = await self._get_session()
            
            # Add authentication headers
            headers = kwargs.get('headers', {})
            if self.config.credentials.get('access_token'):
                headers['Authorization'] = f'Bearer {self.config.credentials["access_token"]}'
            
            headers['Content-Type'] = 'application/json'
            kwargs['headers'] = headers
            
            base_url = self.marketing_api_base if use_marketing_api else self.api_base
            url = f"{base_url}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, use_marketing_api, **kwargs)
                
                elif response.status == 401:
                    # Token expired, try refresh
                    if await self.refresh_token():
                        return await self._make_request(method, endpoint, use_marketing_api, **kwargs)
                    return True
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"Snapchat API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return True
                    
        except Exception as e:
            logger.error(f"Snapchat request error: {e}")
            self.increment_error_count()
            return True
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Upload content to Snapchat (Story or Ad)"""
        try:
            # Snapchat API primarily supports advertising content
            # For organic content, this would typically be done through Snap Kit
            
            # Create media upload
            if content_path and not content_path.startswith('http'):
                # For local files, need to upload to Snapchat's media library first
                upload_result = await self._upload_media(content_path)
                if not upload_result:
                    return UploadResult(
                        success=False,
                        platform_id=self.platform_id,
                        error="Failed to upload media to Snapchat"
                    )
                media_id = upload_result.get('media_id')
            else:
                # For URLs, create creative from URL
                media_id = None
            
            # Create creative/ad content
            creative_data = {
                'name': metadata.title,
                'type': 'SNAP_AD',
                'packaging_status': 'PENDING'
            }
            
            if media_id:
                creative_data['top_snap_media_id'] = media_id
            elif content_path and content_path.startswith('http'):
                creative_data['web_view_properties'] = {
                    'url': content_path,
                    'allow_snap_javascript_sdk': True
                }
            
            result = await self._make_request('POST', '/creatives', json=creative_data, use_marketing_api=True)
            
            if result and result.get('creatives'):
                creative = result['creatives'][0]
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=creative.get('id'),
                    url=None,  # Snapchat doesn't provide public URLs for ads
                    metadata={
                        'creative_id': creative.get('id'),
                        'name': creative.get('name'),
                        'type': creative.get('type'),
                        'status': creative.get('packaging_status'),
                        'created_at': creative.get('created_at')
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Snapchat creative creation failed"
                )
                
        except Exception as e:
            logger.error(f"Snapchat upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def _upload_media(self, media_path: str) -> Optional[Dict[str, Any]]:
        """Upload media file to Snapchat"""
        try:
            # This would require actual file upload implementation
            # Snapchat requires specific media formats and upload process
            logger.warning("Snapchat media upload requires file handling implementation")
            return True
            
        except Exception as e:
            logger.error(f"Snapchat media upload error: {e}")
            return True
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get Snapchat content analytics"""
        try:
            # Get creative stats
            params = {
                'granularity': 'DAY',
                'start_time': start_date.strftime('%Y-%m-%d'),
                'end_time': end_date.strftime('%Y-%m-%d'),
                'fields': 'impressions,swipes,view_completion,spend,video_views'
            }
            
            result = await self._make_request('GET', f'/creatives/{content_id}/stats', 
                                            params=params, use_marketing_api=True)
            
            if result and result.get('timeseries_stats'):
                stats = result['timeseries_stats'][0] if result['timeseries_stats'] else {}
                timeseries = stats.get('timeseries', [{}])[0] if stats.get('timeseries') else {}
                
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=timeseries.get('impressions', 0),
                    likes=0,  # Snapchat doesn't track likes for ads
                    shares=timeseries.get('swipes', 0),
                    comments=0,  # Snapchat ads don't have comments
                    metadata={
                        'impressions': timeseries.get('impressions', 0),
                        'swipes': timeseries.get('swipes', 0),
                        'view_completion': timeseries.get('view_completion', 0),
                        'video_views': timeseries.get('video_views', 0),
                        'spend': timeseries.get('spend', 0),
                        'cpm': timeseries.get('cpm', 0),
                        'ctr': timeseries.get('ctr', 0)
                    }
                )
            else:
                raise Exception("Creative stats not found")
                
        except Exception as e:
            logger.error(f"Snapchat analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on Snapchat (limited API access)"""
        try:
            # Snapchat doesn't provide public content search API
            # This would typically require Snap Kit integration
            logger.warning("Snapchat content search requires Snap Kit integration")
            return []
            
        except Exception as e:
            logger.error(f"Snapchat search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's creatives from Snapchat"""
        try:
            result = await self._make_request('GET', '/creatives', use_marketing_api=True)
            
            if result and result.get('creatives'):
                creatives = []
                for creative in result['creatives']:
                    creatives.append({
                        'id': creative.get('id'),
                        'name': creative.get('name'),
                        'type': creative.get('type'),
                        'packaging_status': creative.get('packaging_status'),
                        'created_at': creative.get('created_at'),
                        'updated_at': creative.get('updated_at'),
                        'review_status': creative.get('review_status')
                    })
                return creatives
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Snapchat user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete Snapchat creative"""
        try:
            result = await self._make_request('DELETE', f'/creatives/{content_id}', use_marketing_api=True)
            
            logger.info(f"Successfully deleted Snapchat creative {content_id}")
            return True
                
        except Exception as e:
            logger.error(f"Error deleting Snapchat content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update Snapchat creative"""
        try:
            update_data = {}
            
            if metadata.title:
                update_data['name'] = metadata.title
            
            if update_data:
                result = await self._make_request('PUT', f'/creatives/{content_id}', 
                                                json=update_data, use_marketing_api=True)
                
                if result and result.get('creatives'):
                    logger.info(f"Successfully updated Snapchat creative {content_id}")
                    return True
                else:
                    logger.error("Failed to update Snapchat creative")
                    return False
            
            return True  # No updates needed
                
        except Exception as e:
            logger.error(f"Error updating Snapchat content: {e}")
            return False
    
    async def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get Snapchat account information"""
        try:
            result = await self._make_request('GET', '/me')
            
            if result:
                return {
                    'id': result.get('id'),
                    'name': result.get('name'),
                    'email': result.get('email'),
                    'display_name': result.get('display_name'),
                    'created_at': result.get('created_at'),
                    'updated_at': result.get('updated_at')
                }
            
            return True
            
        except Exception as e:
            logger.error(f"Error getting Snapchat account info: {e}")
            return True
    
    async def get_ad_accounts(self) -> List[Dict[str, Any]]:
        """Get Snapchat ad accounts"""
        try:
            result = await self._make_request('GET', '/adaccounts', use_marketing_api=True)
            
            if result and result.get('adaccounts'):
                accounts = []
                for account in result['adaccounts']:
                    accounts.append({
                        'id': account.get('id'),
                        'name': account.get('name'),
                        'type': account.get('type'),
                        'status': account.get('status'),
                        'currency': account.get('currency'),
                        'timezone': account.get('timezone'),
                        'created_at': account.get('created_at')
                    })
                return accounts
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting Snapchat ad accounts: {e}")
            return []
    
    async def get_audience_insights(self, ad_account_id: str) -> Dict[str, Any]:
        """Get Snapchat audience insights"""
        try:
            params = {
                'granularity': 'TOTAL',
                'fields': 'impressions,swipes,conversion_purchases,conversion_save'
            }
            
            result = await self._make_request('GET', f'/adaccounts/{ad_account_id}/stats', 
                                            params=params, use_marketing_api=True)
            
            if result and result.get('total_stats'):
                stats = result['total_stats'][0] if result['total_stats'] else {}
                
                return {
                    'total_impressions': stats.get('impressions', 0),
                    'total_swipes': stats.get('swipes', 0),
                    'total_conversions': stats.get('conversion_purchases', 0),
                    'total_saves': stats.get('conversion_save', 0),
                    'account_id': ad_account_id
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting audience insights: {e}")
            return {}
    
    async def create_audience(self, ad_account_id: str, audience_name: str, 
                            audience_spec: Dict[str, Any]) -> Optional[str]:
        """Create custom audience on Snapchat"""
        try:
            audience_data = {
                'name': audience_name,
                'description': f'Custom audience: {audience_name}',
                'source_type': 'CUSTOM',
                **audience_spec
            }
            
            result = await self._make_request('POST', f'/adaccounts/{ad_account_id}/audiences', 
                                            json=audience_data, use_marketing_api=True)
            
            if result and result.get('audiences'):
                audience_id = result['audiences'][0].get('id')
                logger.info(f"Successfully created Snapchat audience: {audience_name}")
                return audience_id
            else:
                logger.error(f"Failed to create Snapchat audience: {audience_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error creating Snapchat audience: {e}")
            return True
    
    async def get_pixel_stats(self, pixel_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get Snapchat pixel statistics"""
        try:
            params = {
                'granularity': 'DAY',
                'start_time': start_date.strftime('%Y-%m-%d'),
                'end_time': end_date.strftime('%Y-%m-%d'),
                'fields': 'pixel_views,pixel_custom_events'
            }
            
            result = await self._make_request('GET', f'/pixels/{pixel_id}/stats', 
                                            params=params, use_marketing_api=True)
            
            if result and result.get('timeseries_stats'):
                stats = result['timeseries_stats'][0] if result['timeseries_stats'] else {}
                timeseries = stats.get('timeseries', [{}])[0] if stats.get('timeseries') else {}
                
                return {
                    'pixel_id': pixel_id,
                    'pixel_views': timeseries.get('pixel_views', 0),
                    'custom_events': timeseries.get('pixel_custom_events', 0),
                    'period': f"{start_date.date()} to {end_date.date()}"
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting pixel stats: {e}")
            return {}
    
    async def get_lens_analytics(self, lens_id: str) -> Dict[str, Any]:
        """Get Snapchat Lens analytics"""
        try:
            # Lens analytics would require Lens Studio API access
            logger.warning("Lens analytics require Lens Studio API access")
            return {
                'lens_id': lens_id,
                'analytics_available': False,
                'message': 'Requires Lens Studio API access'
            }
            
        except Exception as e:
            logger.error(f"Error getting lens analytics: {e}")
            return {}
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
