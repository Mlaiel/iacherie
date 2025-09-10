"""
Patreon Platform Connector
=========================

Enterprise-grade Patreon API connector for Ainflue Distribution Platform.
Supports patron management, content publishing, subscription tiers, and revenue tracking.

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
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone, timedelta
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

class PatreonTierType(Enum):
    """Patreon tier types"""
    PER_MONTH = "per_month"
    PER_CREATION = "per_creation"

class PatreonPostType(Enum):
    """Patreon post types"""
    TEXT_ONLY = "text_only"
    IMAGE_FILE = "image_file"
    VIDEO_FILE = "video_file"
    AUDIO_FILE = "audio_file"
    LINK = "link"

class PatreonPostVisibility(Enum):
    """Patreon post visibility options"""
    PUBLIC = "public"
    PATRONS = "patrons"
    PAID_MEMBERS = "paid_members"

@dataclass
class PatreonTier:
    """Patreon tier data structure"""
    title: str
    description: str
    amount_cents: int
    type: str = "per_month"
    published: bool = True
    patron_count: Optional[int] = None
    remaining: Optional[int] = None
    requires_shipping: bool = False
    created_at: Optional[datetime] = None
    edited_at: Optional[datetime] = None
    image_url: Optional[str] = None
    discord_role_ids: List[str] = field(default_factory=list)

@dataclass
class PatreonPost:
    """Patreon post data structure"""
    title: str
    content: str
    is_paid: bool = False
    is_public: bool = False
    tags: List[str] = field(default_factory=list)
    teaser_text: Optional[str] = None
    change_visibility_at: Optional[datetime] = None
    is_nsfw: bool = False
    tier_ids: List[str] = field(default_factory=list)

@dataclass
class PatreonPatron:
    """Patreon patron data structure"""
    id: str
    attributes: Dict
    full_name: str
    email: str
    pledge_amount_cents: int
    patron_status: str
    created_at: datetime
    declined_since: Optional[datetime] = None

class PatreonConnector:
    """
    Enterprise Patreon API Connector
    
    Provides comprehensive integration with Patreon platform for:
    - Creator content publishing and management
    - Patron relationship management
    - Subscription tier configuration
    - Revenue tracking and analytics
    - Community engagement features
    """
    
    def __init__(self, access_token: str, client_id: str = None, client_secret: str = None):
        """
        Initialize Patreon connector
        
        Args:
            access_token: Patreon API access token
            client_id: Optional OAuth client ID
            client_secret: Optional OAuth client secret
        """
        self.access_token = access_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://www.patreon.com/api/oauth2/v2"
        self.session: Optional[aiohttp.ClientSession] = None
        self.campaign_info: Optional[Dict] = None
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
        Authenticate with Patreon and get campaign info
        
        Returns:
            bool: Authentication success status
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers={
                        'Authorization': f'Bearer {self.access_token}',
                        'User-Agent': 'Ainflue-Platform/1.0'
                    }
                )
            
            # Get campaign information
            response = await self._make_request(
                'GET',
                '/campaigns',
                params={'include': 'tiers,creator,goals,benefits'}
            )
            
            if response and 'data' in response and len(response['data']) > 0:
                self.campaign_info = response['data'][0]
                campaign_name = self.campaign_info.get('attributes', {}).get('creation_name', 'Unknown')
                logger.info(f"Successfully authenticated with Patreon for campaign: {campaign_name}")
                return True
            else:
                logger.error("Patreon authentication failed - no campaigns found")
                return False
                
        except Exception as e:
            logger.error(f"Patreon authentication error: {str(e)}")
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
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            async with self.session.request(method, url, **kwargs) as response:
                # Update rate limiting info from headers
                self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 1000))
                reset_time = response.headers.get('X-RateLimit-Reset')
                if reset_time:
                    self.rate_limit_reset = datetime.fromtimestamp(int(reset_time))
                
                if response.status in [200, 201, 204]:
                    if response.status == 204:
                        return {}
                    return await response.json()
                elif response.status == 429:
                    logger.warning("Patreon rate limit exceeded")
                    return None
                else:
                    error_text = await response.text()
                    logger.error(f"Patreon API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Patreon API request error: {str(e)}")
            return None
    
    async def create_post(self, post: PatreonPost) -> Optional[str]:
        """
        Create a new post on Patreon
        
        Args:
            post: Post data
            
        Returns:
            Optional[str]: Post ID if successful
        """
        try:
            if not self.campaign_info:
                await self.authenticate()
            
            # Prepare post data according to Patreon API v2 format
            post_data = {
                "data": {
                    "type": "post",
                    "attributes": {
                        "title": post.title,
                        "content": post.content,
                        "is_paid": post.is_paid,
                        "is_public": post.is_public,
                        "tags": post.tags
                    },
                    "relationships": {}
                }
            }
            
            if post.teaser_text:
                post_data["data"]["attributes"]["teaser_text"] = post.teaser_text
            
            if post.change_visibility_at:
                post_data["data"]["attributes"]["change_visibility_at"] = post.change_visibility_at.isoformat()
            
            if post.is_nsfw:
                post_data["data"]["attributes"]["is_nsfw"] = post.is_nsfw
            
            # Add campaign relationship
            if self.campaign_info:
                post_data["data"]["relationships"]["campaign"] = {
                    "data": {
                        "type": "campaign",
                        "id": self.campaign_info["id"]
                    }
                }
            
            # Add tier relationships if specified
            if post.tier_ids:
                post_data["data"]["relationships"]["tiers"] = {
                    "data": [{"type": "tier", "id": tier_id} for tier_id in post.tier_ids]
                }
            
            response = await self._make_request(
                'POST',
                '/posts',
                json=post_data
            )
            
            if response and 'data' in response:
                post_id = response['data']['id']
                logger.info(f"Successfully created post: {post.title}")
                return post_id
            else:
                logger.error(f"Failed to create post: {post.title}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating post: {str(e)}")
            return None
    
    async def create_tier(self, tier: PatreonTier) -> Optional[str]:
        """
        Create a new patron tier
        
        Args:
            tier: Tier data
            
        Returns:
            Optional[str]: Tier ID if successful
        """
        try:
            if not self.campaign_info:
                await self.authenticate()
            
            tier_data = {
                "data": {
                    "type": "tier",
                    "attributes": {
                        "title": tier.title,
                        "description": tier.description,
                        "amount_cents": tier.amount_cents,
                        "type": tier.type,
                        "published": tier.published,
                        "requires_shipping": tier.requires_shipping
                    },
                    "relationships": {
                        "campaign": {
                            "data": {
                                "type": "campaign",
                                "id": self.campaign_info["id"]
                            }
                        }
                    }
                }
            }
            
            if tier.image_url:
                tier_data["data"]["attributes"]["image_url"] = tier.image_url
            
            if tier.discord_role_ids:
                tier_data["data"]["attributes"]["discord_role_ids"] = tier.discord_role_ids
            
            response = await self._make_request(
                'POST',
                '/tiers',
                json=tier_data
            )
            
            if response and 'data' in response:
                tier_id = response['data']['id']
                logger.info(f"Successfully created tier: {tier.title}")
                return tier_id
            else:
                logger.error(f"Failed to create tier: {tier.title}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating tier: {str(e)}")
            return None
    
    async def get_patrons(self, include_declined: bool = False) -> List[PatreonPatron]:
        """
        Get list of patrons
        
        Args:
            include_declined: Whether to include declined patrons
            
        Returns:
            List[PatreonPatron]: List of patrons
        """
        try:
            if not self.campaign_info:
                await self.authenticate()
            
            campaign_id = self.campaign_info["id"]
            
            params = {
                'include': 'user,currently_entitled_tiers',
                'fields[member]': 'full_name,email,patron_status,pledge_relationship_start,will_pay_amount_cents',
                'fields[user]': 'email,full_name,image_url'
            }
            
            response = await self._make_request(
                'GET',
                f'/campaigns/{campaign_id}/members',
                params=params
            )
            
            patrons = []
            if response and 'data' in response:
                for member_data in response['data']:
                    # Filter declined patrons if requested
                    patron_status = member_data['attributes'].get('patron_status')
                    if not include_declined and patron_status == 'declined_patron':
                        continue
                    
                    # Find user info from included data
                    user_info = None
                    if 'included' in response:
                        user_id = member_data['relationships'].get('user', {}).get('data', {}).get('id')
                        for included in response['included']:
                            if included['type'] == 'user' and included['id'] == user_id:
                                user_info = included['attributes']
                                break
                    
                    patron = PatreonPatron(
                        id=member_data['id'],
                        attributes=member_data['attributes'],
                        full_name=user_info.get('full_name', '') if user_info else '',
                        email=user_info.get('email', '') if user_info else '',
                        pledge_amount_cents=member_data['attributes'].get('will_pay_amount_cents', 0),
                        patron_status=patron_status,
                        created_at=datetime.fromisoformat(
                            member_data['attributes']['pledge_relationship_start'].replace('Z', '+00:00')
                        ) if member_data['attributes'].get('pledge_relationship_start') else datetime.now(),
                        declined_since=datetime.fromisoformat(
                            member_data['attributes']['declined_since'].replace('Z', '+00:00')
                        ) if member_data['attributes'].get('declined_since') else None
                    )
                    patrons.append(patron)
                
                logger.info(f"Retrieved {len(patrons)} patrons")
            
            return patrons
            
        except Exception as e:
            logger.error(f"Error retrieving patrons: {str(e)}")
            return []
    
    async def get_campaign_analytics(self, start_date: datetime, end_date: datetime) -> Optional[Dict]:
        """
        Get campaign analytics and metrics
        
        Args:
            start_date: Analytics start date
            end_date: Analytics end date
            
        Returns:
            Optional[Dict]: Analytics data
        """
        try:
            if not self.campaign_info:
                await self.authenticate()
            
            campaign_id = self.campaign_info["id"]
            
            # Get basic campaign info with current metrics
            response = await self._make_request(
                'GET',
                f'/campaigns/{campaign_id}',
                params={
                    'include': 'tiers,creator,goals,benefits',
                    'fields[campaign]': 'creation_name,patron_count,pledge_sum,published_at,is_monthly'
                }
            )
            
            if response and 'data' in response:
                campaign_data = response['data']['attributes']
                
                # Get patrons for detailed analytics
                patrons = await self.get_patrons(include_declined=True)
                
                # Calculate metrics
                active_patrons = [p for p in patrons if p.patron_status == 'active_patron']
                declined_patrons = [p for p in patrons if p.patron_status == 'declined_patron']
                
                analytics = {
                    'campaign_name': campaign_data.get('creation_name'),
                    'total_patrons': campaign_data.get('patron_count', 0),
                    'active_patrons': len(active_patrons),
                    'declined_patrons': len(declined_patrons),
                    'monthly_revenue_cents': campaign_data.get('pledge_sum', 0),
                    'monthly_revenue_dollars': campaign_data.get('pledge_sum', 0) / 100,
                    'average_pledge_cents': sum(p.pledge_amount_cents for p in active_patrons) // len(active_patrons) if active_patrons else 0,
                    'published_at': campaign_data.get('published_at'),
                    'is_monthly': campaign_data.get('is_monthly', True),
                    'period_start': start_date.isoformat(),
                    'period_end': end_date.isoformat()
                }
                
                logger.info("Successfully retrieved campaign analytics")
                return analytics
            else:
                logger.error("Failed to retrieve campaign analytics")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving campaign analytics: {str(e)}")
            return None
    
    async def get_posts(self, limit: int = 25, cursor: Optional[str] = None) -> Optional[Dict]:
        """
        Get campaign posts
        
        Args:
            limit: Number of posts to retrieve
            cursor: Pagination cursor
            
        Returns:
            Optional[Dict]: Posts data with pagination info
        """
        try:
            if not self.campaign_info:
                await self.authenticate()
            
            campaign_id = self.campaign_info["id"]
            
            params = {
                'filter[campaign_id]': campaign_id,
                'include': 'user,campaign,access_rules.tier',
                'fields[post]': 'title,content,is_paid,is_public,published_at,url,comment_count,like_count,teaser_text',
                'page[count]': limit
            }
            
            if cursor:
                params['page[cursor]'] = cursor
            
            response = await self._make_request(
                'GET',
                '/posts',
                params=params
            )
            
            if response:
                logger.info(f"Successfully retrieved posts")
                return response
            else:
                logger.error("Failed to retrieve posts")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving posts: {str(e)}")
            return None
    
    async def update_tier(self, tier_id: str, updates: Dict) -> bool:
        """
        Update an existing tier
        
        Args:
            tier_id: Tier ID to update
            updates: Dictionary of updates to apply
            
        Returns:
            bool: Success status
        """
        try:
            tier_data = {
                "data": {
                    "type": "tier",
                    "id": tier_id,
                    "attributes": updates
                }
            }
            
            response = await self._make_request(
                'PATCH',
                f'/tiers/{tier_id}',
                json=tier_data
            )
            
            if response:
                logger.info(f"Successfully updated tier: {tier_id}")
                return True
            else:
                logger.error(f"Failed to update tier: {tier_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating tier: {str(e)}")
            return False
    
    async def send_message_to_patrons(self, subject: str, message: str, tier_ids: Optional[List[str]] = None) -> bool:
        """
        Send message to patrons (Note: This may require special permissions)
        
        Args:
            subject: Message subject
            message: Message content
            tier_ids: Optional list of tier IDs to target
            
        Returns:
            bool: Success status
        """
        try:
            # Note: Patreon API may have limitations on direct messaging
            # This is a conceptual implementation
            logger.warning("Direct messaging through API may require special permissions")
            
            message_data = {
                "data": {
                    "type": "message",
                    "attributes": {
                        "subject": subject,
                        "body": message
                    }
                }
            }
            
            if tier_ids:
                message_data["data"]["relationships"] = {
                    "tiers": {
                        "data": [{"type": "tier", "id": tier_id} for tier_id in tier_ids]
                    }
                }
            
            # This endpoint may not exist in public API
            response = await self._make_request(
                'POST',
                '/messages',
                json=message_data
            )
            
            if response:
                logger.info("Successfully sent message to patrons")
                return True
            else:
                logger.error("Failed to send message to patrons")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message to patrons: {str(e)}")
            return False
    
    async def get_tier_insights(self, tier_id: str) -> Optional[Dict]:
        """
        Get insights for a specific tier
        
        Args:
            tier_id: Tier ID
            
        Returns:
            Optional[Dict]: Tier insights
        """
        try:
            response = await self._make_request(
                'GET',
                f'/tiers/{tier_id}',
                params={
                    'include': 'benefits',
                    'fields[tier]': 'title,description,amount_cents,patron_count,remaining,published,discord_role_ids'
                }
            )
            
            if response and 'data' in response:
                tier_data = response['data']['attributes']
                
                insights = {
                    'tier_id': tier_id,
                    'title': tier_data.get('title'),
                    'amount_dollars': tier_data.get('amount_cents', 0) / 100,
                    'patron_count': tier_data.get('patron_count', 0),
                    'monthly_revenue': (tier_data.get('patron_count', 0) * tier_data.get('amount_cents', 0)) / 100,
                    'remaining_slots': tier_data.get('remaining'),
                    'is_published': tier_data.get('published', False),
                    'has_discord_integration': bool(tier_data.get('discord_role_ids'))
                }
                
                logger.info(f"Successfully retrieved tier insights: {tier_id}")
                return insights
            else:
                logger.error(f"Failed to retrieve tier insights: {tier_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving tier insights: {str(e)}")
            return None
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

# Usage example
async def main():
    """Example usage of PatreonConnector"""
    async with PatreonConnector(
        access_token="your_patreon_access_token"
    ) as patreon:
        
        # Create a new tier
        tier = PatreonTier(
            title="Premium Supporter",
            description="Get exclusive access to premium content and early releases",
            amount_cents=1000,  # $10.00
            type="per_month",
            requires_shipping=False
        )
        
        tier_id = await patreon.create_tier(tier)
        print(f"Created tier: {tier_id}")
        
        # Create a post
        post = PatreonPost(
            title="New Premium Content Available!",
            content="Check out this exclusive content for our premium supporters.",
            is_paid=True,
            is_public=False,
            tags=["premium", "exclusive"],
            tier_ids=[tier_id] if tier_id else []
        )
        
        post_id = await patreon.create_post(post)
        print(f"Created post: {post_id}")
        
        # Get analytics
        analytics = await patreon.get_campaign_analytics(
            datetime.now() - timedelta(days=30),
            datetime.now()
        )
        print(f"Analytics: {analytics}")

if __name__ == "__main__":
    asyncio.run(main())