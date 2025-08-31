"""LinkedIn Platform Integration

LinkedIn API integration for professional networking and content sharing.

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


class LinkedInPlatform(PlatformBase):
    """LinkedIn platform integration"""    
    def __init__(self, config: PlatformConfig):
        """Initialize LinkedIn platform"""        super().__init__(config)
        self.api_base = "https://api.linkedin.com/v2"
        self.auth_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self.session
    
    async def authenticate(self) -> bool:
        """Authenticate with LinkedIn OAuth2"""        try:
            # LinkedIn uses OAuth2 authorization code flow
            access_token = self.config.credentials.get('access_token')
            
            if access_token:
                # Validate existing token
                session = await self._get_session()
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'X-Restli-Protocol-Version': '2.0.0'
                }
                
                async with session.get(f"{self.api_base}/me", headers=headers) as response:
                    if response.status == 200:
                        self.status = PlatformStatus.ACTIVE
                        self.reset_error_count()
                        logger.info("LinkedIn authentication successful")
                        return True
                    else:
                        logger.error("LinkedIn token validation failed")
                        return False
            else:
                logger.error("LinkedIn requires valid access_token")
                return False
                
        except Exception as e:
            logger.error(f"LinkedIn authentication error: {e}")
            self.increment_error_count()
            return False
    
    async def refresh_token(self) -> bool:
        """Refresh LinkedIn token (requires re-authorization)"""        # LinkedIn tokens are long-lived, refresh requires user re-authorization
        return await self.authenticate()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Make authenticated request to LinkedIn API"""        try:
            session = await self._get_session()
            
            # Add authentication headers
            headers = kwargs.get('headers', {})
            if self.config.credentials.get('access_token'):
                headers['Authorization'] = f'Bearer {self.config.credentials["access_token"]}'
            
            headers['X-Restli-Protocol-Version'] = '2.0.0'
            headers['Content-Type'] = 'application/json'
            kwargs['headers'] = headers
            
            url = f"{self.api_base}/{endpoint.lstrip('/')}"
            
            async with session.request(method, url, **kwargs) as response:
                if response.status == 429:
                    await self.handle_rate_limit()
                    return await self._make_request(method, endpoint, **kwargs)
                
                elif response.status == 401:
                    # Token expired or invalid
                    logger.error("LinkedIn authentication failed")
                    self.increment_error_count()
                    return None
                
                elif response.status in [200, 201]:
                    return await response.json()
                
                else:
                    error_text = await response.text()
                    logger.error(f"LinkedIn API error: {response.status} - {error_text}")
                    self.increment_error_count()
                    return None
                    
        except Exception as e:
            logger.error(f"LinkedIn request error: {e}")
            self.increment_error_count()
            return None
    
    async def upload_content(self, content_path: str, metadata: ContentMetadata) -> UploadResult:
        """Share content on LinkedIn"""        try:
            # Get user profile to get person URN
            profile = await self._make_request('GET', '/me')
            if not profile:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="Failed to get user profile"
                )
            
            person_urn = f"urn:li:person:{profile['id']}"
            
            # Create share content
            share_data = {
                "author": person_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": metadata.description or metadata.title
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Handle media content
            if content_path and not content_path.startswith('http'):
                # For media uploads, we need to use LinkedIn's media upload flow
                # This is a simplified version - full implementation would handle file upload
                share_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
            elif content_path and content_path.startswith('http'):
                # Article/link sharing
                share_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                    "status": "READY",
                    "description": {
                        "text": metadata.description or ""
                    },
                    "originalUrl": content_path,
                    "title": {
                        "text": metadata.title
                    }
                }]
                share_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
            
            result = await self._make_request('POST', '/ugcPosts', json=share_data)
            
            if result and result.get('id'):
                return UploadResult(
                    success=True,
                    platform_id=self.platform_id,
                    content_id=result['id'],
                    url=f"https://www.linkedin.com/feed/update/{result['id']}/",
                    metadata={
                        'author': person_urn,
                        'lifecycleState': result.get('lifecycleState'),
                        'created': result.get('created')
                    }
                )
            else:
                return UploadResult(
                    success=False,
                    platform_id=self.platform_id,
                    error="LinkedIn post creation failed"
                )
                
        except Exception as e:
            logger.error(f"LinkedIn upload error: {e}")
            return UploadResult(
                success=False,
                platform_id=self.platform_id,
                error=str(e)
            )
    
    async def get_analytics(self, content_id: str, start_date: datetime, end_date: datetime) -> AnalyticsData:
        """Get LinkedIn post analytics"""        try:
            # LinkedIn analytics require specific permissions and endpoints
            # Using share statistics endpoint
            result = await self._make_request('GET', f'/socialActions/{content_id}')
            
            if result:
                return AnalyticsData(
                    platform_id=self.platform_id,
                    content_id=content_id,
                    views=0,  # Views require additional API access
                    likes=result.get('likesSummary', {}).get('totalLikes', 0),
                    shares=result.get('sharesSummary', {}).get('totalShares', 0),
                    comments=result.get('commentsSummary', {}).get('totalComments', 0),
                    metadata={
                        'aggregatedTotalLikes': result.get('likesSummary', {}).get('aggregatedTotalLikes', 0),
                        'aggregatedTotalShares': result.get('sharesSummary', {}).get('aggregatedTotalShares', 0),
                        'aggregatedTotalComments': result.get('commentsSummary', {}).get('aggregatedTotalComments', 0)
                    }
                )
            else:
                # Fallback to basic post data
                post_data = await self._make_request('GET', f'/ugcPosts/{content_id}')
                if post_data:
                    return AnalyticsData(
                        platform_id=self.platform_id,
                        content_id=content_id,
                        views=0,
                        likes=0,
                        shares=0,
                        comments=0,
                        metadata={
                            'lifecycleState': post_data.get('lifecycleState'),
                            'created': post_data.get('created'),
                            'lastModified': post_data.get('lastModified')
                        }
                    )
                else:
                    raise Exception("Post not found")
                
        except Exception as e:
            logger.error(f"LinkedIn analytics error: {e}")
            raise
    
    async def search_content(self, query: str, content_type: ContentType = None) -> List[Dict[str, Any]]:
        """Search content on LinkedIn (limited API access)"""        try:
            # LinkedIn search requires specific permissions
            # This is a basic implementation using people search
            params = {
                'q': 'keywords',
                'keywords': query,
                'start': 0,
                'count': 10
            }
            
            result = await self._make_request('GET', '/people-search', params=params)
            
            if result and result.get('elements'):
                profiles = []
                for element in result['elements']:
                    profiles.append({
                        'id': element.get('id'),
                        'firstName': element.get('firstName', {}).get('localized', {}),
                        'lastName': element.get('lastName', {}).get('localized', {}),
                        'headline': element.get('headline', {}).get('localized', {}),
                        'profilePicture': element.get('profilePicture'),
                        'publicProfileUrl': element.get('publicProfileUrl')
                    })
                return profiles
            
            return []
            
        except Exception as e:
            logger.error(f"LinkedIn search error: {e}")
            return []
    
    async def get_user_content(self, user_id: str = None) -> List[Dict[str, Any]]:
        """Get user's posts from LinkedIn"""        try:
            # Get current user's posts
            params = {
                'q': 'authors',
                'authors': f'urn:li:person:{user_id}' if user_id else 'urn:li:person:CURRENT_USER',
                'sortBy': 'CREATED',
                'count': 20
            }
            
            result = await self._make_request('GET', '/ugcPosts', params=params)
            
            if result and result.get('elements'):
                posts = []
                for element in result['elements']:
                    posts.append({
                        'id': element.get('id'),
                        'author': element.get('author'),
                        'created': element.get('created'),
                        'lastModified': element.get('lastModified'),
                        'lifecycleState': element.get('lifecycleState'),
                        'specificContent': element.get('specificContent'),
                        'visibility': element.get('visibility')
                    })
                return posts
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn user content: {e}")
            return []
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete LinkedIn post"""        try:
            result = await self._make_request('DELETE', f'/ugcPosts/{content_id}')
            
            # LinkedIn DELETE returns 204 No Content on success
            logger.info(f"Successfully deleted LinkedIn post {content_id}")
            return True
                
        except Exception as e:
            logger.error(f"Error deleting LinkedIn content: {e}")
            return False
    
    async def update_content(self, content_id: str, metadata: ContentMetadata) -> bool:
        """Update LinkedIn post (limited editing capabilities)"""        try:
            # LinkedIn doesn't support post editing after publication
            # This is a placeholder for potential future functionality
            logger.warning("LinkedIn doesn't support post editing after publication")
            return False
                
        except Exception as e:
            logger.error(f"Error updating LinkedIn content: {e}")
            return False
    
    async def get_profile_info(self, user_id: str = None) -> Optional[Dict[str, Any]]:
        """Get LinkedIn profile information"""        try:
            endpoint = '/me' if not user_id else f'/people/{user_id}'
            result = await self._make_request('GET', endpoint)
            
            if result:
                return {
                    'id': result.get('id'),
                    'firstName': result.get('firstName', {}).get('localized', {}),
                    'lastName': result.get('lastName', {}).get('localized', {}),
                    'headline': result.get('headline', {}).get('localized', {}),
                    'location': result.get('location'),
                    'industry': result.get('industry'),
                    'summary': result.get('summary'),
                    'profilePicture': result.get('profilePicture'),
                    'publicProfileUrl': result.get('publicProfileUrl')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn profile: {e}")
            return None
    
    async def get_company_info(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get LinkedIn company information"""        try:
            result = await self._make_request('GET', f'/companies/{company_id}')
            
            if result:
                return {
                    'id': result.get('id'),
                    'name': result.get('name', {}).get('localized', {}),
                    'description': result.get('description', {}).get('localized', {}),
                    'website': result.get('website'),
                    'industry': result.get('industry'),
                    'companyType': result.get('companyType'),
                    'employeeCountRange': result.get('employeeCountRange'),
                    'foundedOn': result.get('foundedOn'),
                    'locations': result.get('locations'),
                    'logo': result.get('logo')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn company info: {e}")
            return None
    
    async def get_connections(self) -> List[Dict[str, Any]]:
        """Get user's LinkedIn connections"""        try:
            result = await self._make_request('GET', '/people/~/connections')
            
            if result and result.get('elements'):
                connections = []
                for element in result['elements']:
                    connections.append({
                        'id': element.get('id'),
                        'firstName': element.get('firstName', {}).get('localized', {}),
                        'lastName': element.get('lastName', {}).get('localized', {}),
                        'headline': element.get('headline', {}).get('localized', {}),
                        'profilePicture': element.get('profilePicture')
                    })
                return connections
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn connections: {e}")
            return []
    
    async def send_message(self, recipient_id: str, message_text: str) -> bool:
        """Send direct message on LinkedIn"""        try:
            # LinkedIn messaging requires specific permissions
            message_data = {
                "recipients": [f"urn:li:person:{recipient_id}"],
                "body": message_text,
                "subject": "Message from IA Influencer Agent"
            }
            
            result = await self._make_request('POST', '/messaging/conversations', json=message_data)
            
            if result and result.get('id'):
                logger.info(f"Successfully sent LinkedIn message to {recipient_id}")
                return True
            else:
                logger.error("Failed to send LinkedIn message")
                return False
                
        except Exception as e:
            logger.error(f"Error sending LinkedIn message: {e}")
            return False
    
    async def get_industry_insights(self) -> Dict[str, Any]:
        """Get industry insights and trends"""        try:
            # This would require LinkedIn Marketing API access
            # Placeholder for industry insights functionality
            logger.warning("Industry insights require LinkedIn Marketing API access")
            return {
                'insights_available': False,
                'message': 'Requires LinkedIn Marketing API access'
            }
            
        except Exception as e:
            logger.error(f"Error getting industry insights: {e}")
            return {}
    
    async def get_page_analytics(self, page_id: str) -> Dict[str, Any]:
        """Get LinkedIn company page analytics"""        try:
            # Company page analytics require specific permissions
            params = {
                'q': 'organizationalEntity',
                'organizationalEntity': f'urn:li:organization:{page_id}'
            }
            
            result = await self._make_request('GET', '/organizationPageStatistics', params=params)
            
            if result and result.get('elements'):
                stats = result['elements'][0] if result['elements'] else {}
                return {
                    'page_id': page_id,
                    'followers': stats.get('followerCount', 0),
                    'views': stats.get('viewCount', 0),
                    'unique_views': stats.get('uniqueViewCount', 0),
                    'clicks': stats.get('clickCount', 0)
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting page analytics: {e}")
            return {}
    
    async def close(self):
        """Close HTTP session"""        if self.session and not self.session.closed:
            await self.session.close()
