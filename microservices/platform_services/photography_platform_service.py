"""
📸 PHOTOGRAPHY PLATFORM SERVICE - ENTERPRISE MICROSERVICE
Photography platform integration service for creator content distribution and monetization.

Author: Fahed Mlaiel
Copyright: © 2024-2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aioredis

logger = logging.getLogger(__name__)

class PhotoPlatform(Enum):
    """Supported photography platforms"""
    INSTAGRAM = "instagram"
    PINTEREST = "pinterest"
    FLICKR = "flickr"
    SHUTTERSTOCK = "shutterstock"
    GETTY_IMAGES = "getty_images"
    ADOBE_STOCK = "adobe_stock"
    FIVE_HUNDRED_PX = "500px"
    UNSPLASH = "unsplash"
    PEXELS = "pexels"
    SMUGMUG = "smugmug"
    DEVIANTART = "deviantart"
    BEHANCE = "behance"

class PhotoCategory(Enum):
    """Photo categories"""
    NATURE = "nature"
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    STREET = "street"
    FASHION = "fashion"
    FOOD = "food"
    ARCHITECTURE = "architecture"
    WILDLIFE = "wildlife"
    TRAVEL = "travel"
    ABSTRACT = "abstract"
    COMMERCIAL = "commercial"
    ARTISTIC = "artistic"

@dataclass
class PhotoContent:
    """Photography content definition"""
    photo_id: str
    title: str
    description: str
    category: PhotoCategory
    creator_id: str
    file_path: str
    resolution: str = "4K"
    format: str = "JPG"
    tags: List[str] = None
    location: Optional[str] = None
    camera_info: Dict[str, Any] = None
    license_type: str = "royalty_free"
    price: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.camera_info is None:
            self.camera_info = {}
        if self.metadata is None:
            self.metadata = {}

@dataclass
class PhotoPublishResult:
    """Photo publishing result"""
    result_id: str
    photo_id: str
    platform: PhotoPlatform
    status: str
    platform_photo_id: Optional[str] = None
    platform_url: Optional[str] = None
    views: int = 0
    likes: int = 0
    downloads: int = 0
    revenue: float = 0.0
    published_at: Optional[datetime] = None

class PhotographyPlatformService:
    """
    📸 Photography Platform Service
    
    Comprehensive photography platform integration service supporting multiple
    photography platforms, content distribution, and creator monetization.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.photo_cache: Dict[str, PhotoContent] = {}
        self.publish_results: Dict[str, PhotoPublishResult] = {}
        self.running = False
        
    async def initialize(self):
        """Initialize photography platform service"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            self.running = True
            logger.info("Photography Platform service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize photography platform service: {e}")
            raise
            
    async def upload_photo(self, photo: PhotoContent) -> str:
        """Upload photo content"""
        self.photo_cache[photo.photo_id] = photo
        return photo.photo_id
        
    async def publish_to_platform(self, photo_id: str, platform: PhotoPlatform) -> PhotoPublishResult:
        """Publish photo to platform"""
        # Simplified implementation
        result = PhotoPublishResult(
            result_id=f"result_{photo_id}_{platform.value}",
            photo_id=photo_id,
            platform=platform,
            status="published",
            published_at=datetime.utcnow()
        )
        self.publish_results[result.result_id] = result
        return result
        
    async def health_check(self) -> Dict[str, Any]:
        """Health check for photography platform service"""
        return {
            'service': 'photography_platform',
            'status': 'healthy',
            'cached_photos': len(self.photo_cache)
        }
        
    async def shutdown(self):
        """Shutdown photography platform service"""
        self.running = False
        if self.redis:
            await self.redis.close()
        logger.info("Photography Platform service shut down")

# Example usage
async def create_photography_platform_service():
    """Factory function to create photography platform service"""
    service = PhotographyPlatformService()
    await service.initialize()
    return service