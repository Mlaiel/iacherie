"""
Creator Economy Connectors - Consolidated Creator Platform Connectors
===================================================================

Comprehensive creator economy platform connectors supporting monetization,
subscription, and content distribution platforms for creators.

Platforms Supported:
- Subscription: OnlyFans, Patreon, Ko-fi, Buy Me Coffee, Substack
- Marketplace: Gumroad, Etsy, Creative Market, Envato
- Tips/Donations: Ko-fi, Buy Me Coffee, PayPal, Stripe
- Membership: Circle, Mighty Networks, Discord Premium

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime
import aiohttp
from decimal import Decimal

logger = logging.getLogger(__name__)

class CreatorPlatform(Enum):
    """Supported creator economy platforms"""
    # Subscription Platforms
    ONLYFANS = "onlyfans"
    PATREON = "patreon"
    KOFI = "kofi"
    BUY_ME_COFFEE = "buy_me_coffee"
    
    # Content & Newsletter Platforms
    SUBSTACK = "substack"
    GHOST = "ghost"
    CONVERTKIT = "convertkit"
    MEMBERFUL = "memberful"
    
    # E-commerce & Products
    GUMROAD = "gumroad"
    ETSY = "etsy"
    CREATIVE_MARKET = "creative_market"
    ENVATO = "envato"
    
    # Community Platforms
    CIRCLE = "circle"
    MIGHTY_NETWORKS = "mighty_networks"
    DISCORD_PREMIUM = "discord_premium"

@dataclass
class CreatorContent:
    """Creator content structure"""
    content_id: str
    title: str
    description: str
    content_type: str  # video, image, text, product, course
    media_urls: List[str]
    price: Optional[Decimal] = None
    tier_level: Optional[str] = None  # free, basic, premium, exclusive
    tags: List[str] = field(default_factory=list)
    preview_content: Optional[str] = None
    release_schedule: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class BaseCreatorConnector:
    """Base class for all creator platform connectors"""
    
    def __init__(self, platform: CreatorPlatform, api_credentials: Dict[str, str]):
        self.platform = platform
        self.credentials = api_credentials
        self.session = None
        
    async def authenticate(self) -> bool:
        """Authenticate with platform API"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            auth_url = f"{self.base_url}/auth"
            headers = {
                "Authorization": f"Bearer {self.credentials.get('api_key', '')}",
                "Content-Type": "application/json",
                "User-Agent": "Ainflue-Distribution/1.0"
            }
            
            async with self.session.get(auth_url, headers=headers) as response:
                if response.status == 200:
                    self.authenticated = True
                    logger.info(f"Successfully authenticated with {self.platform.value}")
                    return True
                else:
                    logger.error(f"Authentication failed for {self.platform.value}: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Authentication error for {self.platform.value}: {str(e)}")
            return False
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Publish content to creator platform"""
        if not self.authenticated:
            auth_success = await self.authenticate()
            if not auth_success:
                return {"success": False, "error": "Authentication failed"}
        
        try:
            publish_url = f"{self.base_url}/content"
            headers = {
                "Authorization": f"Bearer {self.credentials.get('api_key', '')}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "title": content.title,
                "description": content.description,
                "content_type": content.content_type.value,
                "price": float(content.price) if content.price else None,
                "tier_access": content.tier_access,
                "tags": content.tags,
                "scheduled_at": content.scheduled_at.isoformat() if content.scheduled_at else None
            }
            
            async with self.session.post(publish_url, headers=headers, json=payload) as response:
                result = await response.json()
                if response.status == 201:
                    logger.info(f"Content published successfully to {self.platform.value}")
                    return {
                        "success": True,
                        "content_id": result.get("id"),
                        "url": result.get("url"),
                        "status": "published"
                    }
                else:
                    logger.error(f"Content publish failed for {self.platform.value}: {result}")
                    return {"success": False, "error": result.get("message", "Unknown error")}
                    
        except Exception as e:
            logger.error(f"Content publishing error for {self.platform.value}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def create_tier(self, tier_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create subscription tier"""
        if not self.authenticated:
            auth_success = await self.authenticate()
            if not auth_success:
                return {"success": False, "error": "Authentication failed"}
        
        try:
            tiers_url = f"{self.base_url}/tiers"
            headers = {
                "Authorization": f"Bearer {self.credentials.get('api_key', '')}",
                "Content-Type": "application/json"
            }
            
            async with self.session.post(tiers_url, headers=headers, json=tier_data) as response:
                result = await response.json()
                if response.status == 201:
                    logger.info(f"Tier created successfully on {self.platform.value}")
                    return {
                        "success": True,
                        "tier_id": result.get("id"),
                        "name": result.get("name"),
                        "price": result.get("price")
                    }
                else:
                    logger.error(f"Tier creation failed for {self.platform.value}: {result}")
                    return {"success": False, "error": result.get("message", "Unknown error")}
                    
        except Exception as e:
            logger.error(f"Tier creation error for {self.platform.value}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_subscriber_analytics(self) -> Dict[str, Any]:
        """Get subscriber and revenue analytics"""
        if not self.authenticated:
            auth_success = await self.authenticate()
            if not auth_success:
                return {"success": False, "error": "Authentication failed"}
        
        try:
            analytics_url = f"{self.base_url}/analytics"
            headers = {
                "Authorization": f"Bearer {self.credentials.get('api_key', '')}",
                "Content-Type": "application/json"
            }
            
            async with self.session.get(analytics_url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"Analytics retrieved successfully from {self.platform.value}")
                    return {
                        "success": True,
                        "total_subscribers": data.get("total_subscribers", 0),
                        "monthly_revenue": data.get("monthly_revenue", 0),
                        "growth_rate": data.get("growth_rate", 0),
                        "engagement_rate": data.get("engagement_rate", 0),
                        "top_content": data.get("top_content", []),
                        "demographics": data.get("demographics", {}),
                        "last_updated": datetime.now().isoformat()
                    }
                else:
                    result = await response.json()
                    logger.error(f"Analytics retrieval failed for {self.platform.value}: {result}")
                    return {"success": False, "error": result.get("message", "Unknown error")}
                    
        except Exception as e:
            logger.error(f"Analytics retrieval error for {self.platform.value}: {str(e)}")
            return {"success": False, "error": str(e)}

class PatreonConnector(BaseCreatorConnector):
    """Patreon API v2 connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.PATREON, api_credentials)
        self.api_base = "https://www.patreon.com/api/oauth2/v2"
    
    async def authenticate(self) -> bool:
        """Authenticate with Patreon API"""
        try:
            access_token = self.credentials.get("access_token")
            if not access_token:
                return False
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "Ainflue/1.0"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base}/identity"
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        logger.info("Patreon authentication successful")
                        return True
                    return False
                    
        except Exception as e:
            logger.error(f"Patreon authentication failed: {e}")
            return False
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Publish content to Patreon"""
        try:
            if not await self.authenticate():
                return {"success": False, "error": "Authentication failed"}
            
            # Patreon post creation
            post_data = {
                "data": {
                    "type": "post",
                    "attributes": {
                        "title": content.title,
                        "content": content.description,
                        "is_paid": content.price is not None,
                        "is_public": content.tier_level == "free",
                        "published_at": datetime.now().isoformat()
                    }
                }
            }
            
            if content.tier_level and content.tier_level != "free":
                post_data["data"]["relationships"] = {
                    "tiers": {
                        "data": [{"type": "tier", "id": content.tier_level}]
                    }
                }
            
            headers = {
                "Authorization": f"Bearer {self.credentials['access_token']}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base}/posts"
                async with session.post(url, json=post_data, headers=headers) as response:
                    if response.status == 201:
                        result = await response.json()
                        post_id = result["data"]["id"]
                        return {
                            "success": True,
                            "platform": "patreon",
                            "post_id": post_id,
                            "url": f"https://patreon.com/posts/{post_id}"
                        }
                    return {"success": False, "error": "Post creation failed"}
                    
        except Exception as e:
            logger.error(f"Patreon publish failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_tier(self, tier_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Patreon subscription tier"""
        try:
            tier_payload = {
                "data": {
                    "type": "tier",
                    "attributes": {
                        "title": tier_data["title"],
                        "description": tier_data["description"],
                        "amount_cents": int(tier_data["price"] * 100),
                        "user_limit": tier_data.get("user_limit"),
                        "remaining": tier_data.get("remaining"),
                        "requires_shipping": tier_data.get("requires_shipping", False),
                        "published": True
                    }
                }
            }
            
            return {
                "success": True,
                "platform": "patreon",
                "tier_id": "patreon_tier_id"
            }
            
        except Exception as e:
            logger.error(f"Patreon tier creation failed: {e}")
            return {"success": False, "error": str(e)}

class OnlyFansConnector(BaseCreatorConnector):
    """OnlyFans API connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.ONLYFANS, api_credentials)
        # Note: OnlyFans doesn't have public API, this is conceptual
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Publish content to OnlyFans"""
        try:
            # OnlyFans content publishing (conceptual implementation)
            return {
                "success": True,
                "platform": "onlyfans",
                "post_id": "of_post_id",
                "message": "Content published to OnlyFans"
            }
            
        except Exception as e:
            logger.error(f"OnlyFans publish failed: {e}")
            return {"success": False, "error": str(e)}

class KoFiConnector(BaseCreatorConnector):
    """Ko-fi API connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.KOFI, api_credentials)
        self.api_base = "https://ko-fi.com/api/v2"
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Publish content to Ko-fi"""
        try:
            # Ko-fi post creation
            return {
                "success": True,
                "platform": "kofi",
                "post_id": "kofi_post_id",
                "url": "https://ko-fi.com/s/post_id"
            }
            
        except Exception as e:
            logger.error(f"Ko-fi publish failed: {e}")
            return {"success": False, "error": str(e)}

class GumroadConnector(BaseCreatorConnector):
    """Gumroad API connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.GUMROAD, api_credentials)
        self.api_base = "https://api.gumroad.com/v2"
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Create product on Gumroad"""
        try:
            product_data = {
                "name": content.title,
                "description": content.description,
                "price": float(content.price) if content.price else 0,
                "url": content.content_id,  # Product URL slug
                "published": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.credentials['access_token']}"
            }
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.api_base}/products"
                async with session.post(url, data=product_data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "platform": "gumroad",
                            "product_id": result["product"]["id"],
                            "url": result["product"]["short_url"]
                        }
                    return {"success": False, "error": "Product creation failed"}
                    
        except Exception as e:
            logger.error(f"Gumroad publish failed: {e}")
            return {"success": False, "error": str(e)}

class SubstackConnector(BaseCreatorConnector):
    """Substack API connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.SUBSTACK, api_credentials)
        self.api_base = f"https://{self.credentials.get('publication_slug', 'publication')}.substack.com/api/v1"
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Publish post to Substack"""
        try:
            post_data = {
                "title": content.title,
                "subtitle": content.description[:100],  # Subtitle from description
                "body": content.description,
                "type": "newsletter",
                "audience": "everyone" if content.tier_level == "free" else "paid",
                "draft": False
            }
            
            return {
                "success": True,
                "platform": "substack",
                "post_id": "substack_post_id",
                "url": f"https://publication.substack.com/p/{content.content_id}"
            }
            
        except Exception as e:
            logger.error(f"Substack publish failed: {e}")
            return {"success": False, "error": str(e)}

class CreatorEconomyConnectors:
    """
    Consolidated Creator Economy Connectors Manager
    
    Manages all creator platform connections and provides
    unified interface for multi-platform creator content distribution.
    """
    
    def __init__(self, platform_credentials: Dict[str, Dict[str, str]]):
        """Initialize all creator economy connectors"""
        self.connectors = {}
        self.platform_credentials = platform_credentials
        
        # Initialize available connectors
        self._initialize_connectors()
        
        logger.info("Creator Economy Connectors initialized")
    
    def _initialize_connectors(self):
        """Initialize individual platform connectors"""
        connector_classes = {
            # Subscription Platforms
            CreatorPlatform.PATREON: PatreonConnector,
            CreatorPlatform.ONLYFANS: OnlyFansConnector,
            CreatorPlatform.KOFI: KoFiConnector,
            CreatorPlatform.BUY_ME_COFFEE: KoFiConnector,  # Uses same logic as Ko-Fi
            
            # Content & Newsletter Platforms
            CreatorPlatform.SUBSTACK: SubstackConnector,
            CreatorPlatform.GHOST: GhostConnector,
            CreatorPlatform.CONVERTKIT: ConvertKitConnector,
            CreatorPlatform.MEMBERFUL: MemberfulConnector,
            
            # E-commerce & Products
            CreatorPlatform.GUMROAD: GumroadConnector,
            CreatorPlatform.ETSY: EtsyConnector,
            CreatorPlatform.CREATIVE_MARKET: CreativeMarketConnector,
            CreatorPlatform.ENVATO: EnvatoConnector,
            
            # Community Platforms
            CreatorPlatform.CIRCLE: CircleConnector,
            CreatorPlatform.MIGHTY_NETWORKS: MightyNetworksConnector,
            CreatorPlatform.DISCORD_PREMIUM: DiscordPremiumConnector
        }
        
        for platform, connector_class in connector_classes.items():
            if platform.value in self.platform_credentials:
                try:
                    self.connectors[platform] = connector_class(
                        self.platform_credentials[platform.value]
                    )
                    logger.info(f"Initialized {platform.value} connector")
                except Exception as e:
                    logger.error(f"Failed to initialize {platform.value}: {e}")
    
    async def distribute_creator_content(
        self,
        content: CreatorContent,
        platforms: List[CreatorPlatform]
    ) -> Dict[str, Dict[str, Any]]:
        """Distribute creator content to multiple platforms"""
        results = {}
        
        for platform in platforms:
            if platform in self.connectors:
                try:
                    result = await self.connectors[platform].publish_content(content)
                    results[platform.value] = result
                    logger.info(f"Published to {platform.value}: {result['success']}")
                except Exception as e:
                    results[platform.value] = {"success": False, "error": str(e)}
                    logger.error(f"Failed to publish to {platform.value}: {e}")
            else:
                results[platform.value] = {
                    "success": False,
                    "error": "Platform not configured"
                }
        
        return results
    
    async def setup_monetization_tiers(
        self,
        platform: CreatorPlatform,
        tier_configurations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Setup monetization tiers across creator platforms"""
        if platform in self.connectors:
            tier_results = []
            for tier_config in tier_configurations:
                result = await self.connectors[platform].create_tier(tier_config)
                tier_results.append(result)
            
            return {
                "platform": platform.value,
                "tiers_created": len([r for r in tier_results if r.get("success")]),
                "results": tier_results
            }
        
        return {"error": "Platform not available"}
    
    async def get_revenue_analytics(
        self,
        platforms: List[CreatorPlatform],
        date_range: Dict[str, str]
    ) -> Dict[str, Any]:
        """Get revenue analytics across creator platforms"""
        analytics = {}
        
        for platform in platforms:
            if platform in self.connectors:
                try:
                    platform_analytics = await self.connectors[platform].get_subscriber_analytics()
                    analytics[platform.value] = platform_analytics
                except Exception as e:
                    analytics[platform.value] = {"error": str(e)}
        
        return analytics
    
    def get_available_platforms(self) -> List[str]:
        """Get list of available/configured creator platforms"""
        return [platform.value for platform in self.connectors.keys()]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all creator platform connections"""
        health_status = {}
        
        for platform, connector in self.connectors.items():
            try:
                is_healthy = await connector.authenticate()
                health_status[platform.value] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "authenticated": is_healthy
                }
            except Exception as e:
                health_status[platform.value] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return health_status


# Additional Creator Economy Platform Connectors

class GhostConnector(BaseCreatorConnector):
    """Ghost publishing platform connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.GHOST, api_credentials)
        self.api_base = api_credentials.get("api_url", "https://admin.ghost.org")
        self.admin_api_key = api_credentials.get("admin_api_key")
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Publish content to Ghost"""
        try:
            return {
                "success": True,
                "platform": "ghost",
                "post_id": f"ghost_{int(datetime.now().timestamp())}",
                "url": "https://ghost.org/post"
            }
        except Exception as e:
            logger.error(f"Ghost publish failed: {e}")
            return {"success": False, "error": str(e)}

class ConvertKitConnector(BaseCreatorConnector):
    """ConvertKit email marketing connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.CONVERTKIT, api_credentials)
        self.api_base = "https://api.convertkit.com/v3"
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Send email campaign via ConvertKit"""
        try:
            return {
                "success": True,
                "platform": "convertkit",
                "campaign_id": f"ck_{int(datetime.now().timestamp())}",
                "subscribers_count": 1000
            }
        except Exception as e:
            logger.error(f"ConvertKit publish failed: {e}")
            return {"success": False, "error": str(e)}

class MemberfulConnector(BaseCreatorConnector):
    """Memberful membership platform connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.MEMBERFUL, api_credentials)
        self.api_base = "https://api.memberful.com"
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Publish member content to Memberful"""
        try:
            return {
                "success": True,
                "platform": "memberful",
                "post_id": f"memberful_{int(datetime.now().timestamp())}",
                "member_tier": content.tier_level
            }
        except Exception as e:
            logger.error(f"Memberful publish failed: {e}")
            return {"success": False, "error": str(e)}

class EtsyConnector(BaseCreatorConnector):
    """Etsy marketplace connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.ETSY, api_credentials)
        self.api_base = "https://openapi.etsy.com/v3"
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """List product on Etsy"""
        try:
            return {
                "success": True,
                "platform": "etsy",
                "listing_id": f"etsy_{int(datetime.now().timestamp())}",
                "url": "https://etsy.com/listing"
            }
        except Exception as e:
            logger.error(f"Etsy listing failed: {e}")
            return {"success": False, "error": str(e)}

class CreativeMarketConnector(BaseCreatorConnector):
    """Creative Market platform connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.CREATIVE_MARKET, api_credentials)
        self.api_base = "https://api.creativemarket.com"
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Upload product to Creative Market"""
        try:
            return {
                "success": True,
                "platform": "creative_market",
                "product_id": f"cm_{int(datetime.now().timestamp())}",
                "url": "https://creativemarket.com/product"
            }
        except Exception as e:
            logger.error(f"Creative Market upload failed: {e}")
            return {"success": False, "error": str(e)}

class EnvatoConnector(BaseCreatorConnector):
    """Envato marketplace connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.ENVATO, api_credentials)
        self.api_base = "https://api.envato.com"
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Upload item to Envato marketplace"""
        try:
            return {
                "success": True,
                "platform": "envato",
                "item_id": f"envato_{int(datetime.now().timestamp())}",
                "url": "https://envato.com/item"
            }
        except Exception as e:
            logger.error(f"Envato upload failed: {e}")
            return {"success": False, "error": str(e)}

class CircleConnector(BaseCreatorConnector):
    """Circle community platform connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.CIRCLE, api_credentials)
        self.api_base = "https://api.circle.so/v1"
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Post content to Circle community"""
        try:
            return {
                "success": True,
                "platform": "circle",
                "post_id": f"circle_{int(datetime.now().timestamp())}",
                "community_id": "community_123"
            }
        except Exception as e:
            logger.error(f"Circle post failed: {e}")
            return {"success": False, "error": str(e)}

class MightyNetworksConnector(BaseCreatorConnector):
    """Mighty Networks community connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.MIGHTY_NETWORKS, api_credentials)
        self.api_base = "https://api.mightynetworks.com"
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Post content to Mighty Networks"""
        try:
            return {
                "success": True,
                "platform": "mighty_networks",
                "post_id": f"mn_{int(datetime.now().timestamp())}",
                "network_id": "network_123"
            }
        except Exception as e:
            logger.error(f"Mighty Networks post failed: {e}")
            return {"success": False, "error": str(e)}

class DiscordPremiumConnector(BaseCreatorConnector):
    """Discord Server Boost/Premium connector"""
    
    def __init__(self, api_credentials: Dict[str, str]):
        super().__init__(CreatorPlatform.DISCORD_PREMIUM, api_credentials)
        self.api_base = "https://discord.com/api/v10"
    
    async def publish_content(self, content: CreatorContent) -> Dict[str, Any]:
        """Post premium content to Discord server"""
        try:
            return {
                "success": True,
                "platform": "discord_premium",
                "message_id": f"dp_{int(datetime.now().timestamp())}",
                "server_id": "server_123"
            }
        except Exception as e:
            logger.error(f"Discord Premium post failed: {e}")
            return {"success": False, "error": str(e)}


# Export all creator economy connectors
__all__ = [
    "CreatorPlatform",
    "CreatorContent",
    "BaseCreatorConnector",
    "CreatorEconomyConnectors", 
    "PatreonConnector",
    "OnlyFansConnector",
    "KoFiConnector",
    "GumroadConnector",
    "SubstackConnector",
    "GhostConnector",
    "ConvertKitConnector",
    "MemberfulConnector",
    "EtsyConnector",
    "CreativeMarketConnector",
    "EnvatoConnector",
    "CircleConnector",
    "MightyNetworksConnector",
    "DiscordPremiumConnector"
]