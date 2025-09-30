"""Unsplash API Integration
========================

Complete Unsplash API integration for high-quality stock photography and image management.
Handles photo search, downloads, collections, and user management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urlencode
import os

logger = logging.getLogger(__name__)


@dataclass
class UnsplashPhoto:
    """Unsplash photo information"""
    photo_id: str
    description: str
    alt_description: str
    urls: Dict[str, str]  # raw, full, regular, small, thumb
    width: int
    height: int
    color: str
    likes: int
    downloads: int
    created_at: datetime
    updated_at: datetime
    photographer: Dict[str, Any]
    tags: List[str] = None
    exif: Dict[str, Any] = None
    location: Dict[str, Any] = None


@dataclass
class UnsplashCollection:
    """Unsplash collection information"""
    collection_id: str
    title: str
    description: str
    total_photos: int
    private: bool
    share_key: str
    cover_photo: Dict[str, Any]
    user: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class UnsplashUser:
    """Unsplash user information"""
    user_id: str
    username: str
    name: str
    portfolio_url: str = None
    bio: str = None
    location: str = None
    total_likes: int = 0
    total_photos: int = 0
    total_collections: int = 0
    instagram_username: str = None
    twitter_username: str = None
    profile_image: Dict[str, str] = None


@dataclass
class UnsplashStats:
    """Unsplash photo statistics"""
    photo_id: str
    downloads: int
    views: int
    likes: int
    historical_downloads: List[Dict[str, Any]] = None
    historical_views: List[Dict[str, Any]] = None


class UnsplashAPI:
    """Unsplash API integration for stock photography"""
    
    def __init__(self, access_key: str = None, secret_key: str = None):
        self.access_key = access_key or os.getenv('UNSPLASH_ACCESS_KEY')
        self.secret_key = secret_key or os.getenv('UNSPLASH_SECRET_KEY')
        self.base_url = "https://api.unsplash.com"
        self.session = None
        
        if not self.access_key:
            raise ValueError("Unsplash access key is required")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make authenticated API request"""
        
        url = f"{self.base_url}/{endpoint}"
        
        headers = {
            "Authorization": f"Client-ID {self.access_key}",
            "Accept": "application/json"
        }
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 403:
                        raise Exception("Rate limit exceeded - 50 requests per hour")
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
            elif method.upper() == "POST":
                headers["Content-Type"] = "application/json"
                async with self.session.post(url, json=data, headers=headers, params=params) as response:
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
                        
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {e}")
            raise Exception(f"Network error: {e}")
    
    # =================== PHOTO SEARCH & DISCOVERY ===================
    
    async def search_photos(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20,
        order_by: str = "relevant",
        orientation: str = None,
        size: str = None,
        color: str = None
    ) -> Dict[str, Any]:
        """Search for photos by keyword"""
        
        params = {
            "query": query,
            "page": page,
            "per_page": min(per_page, 30),  # Max 30 per page
            "order_by": order_by  # relevant, latest, popular
        }
        
        # Optional filters
        if orientation:  # landscape, portrait, squarish
            params["orientation"] = orientation
        if size:  # large, medium, small
            params["size"] = size
        if color:  # black_and_white, black, white, yellow, orange, red, purple, magenta, green, teal, blue
            params["color"] = color
            
        response = await self._make_request("GET", "search/photos", params)
        
        # Convert to UnsplashPhoto objects
        photos = []
        for photo_data in response.get("results", []):
            photos.append(self._parse_photo(photo_data))
        
        return {
            "total": response.get("total", 0),
            "total_pages": response.get("total_pages", 0),
            "photos": photos
        }
    
    async def get_random_photos(
        self,
        count: int = 1,
        featured: bool = None,
        username: str = None,
        query: str = None,
        orientation: str = None,
        content_filter: str = "low"
    ) -> List[UnsplashPhoto]:
        """Get random photos"""
        
        params = {"count": min(count, 30)}  # Max 30 photos
        
        if featured is not None:
            params["featured"] = str(featured).lower()
        if username:
            params["username"] = username
        if query:
            params["query"] = query
        if orientation:
            params["orientation"] = orientation
        if content_filter:  # low, high
            params["content_filter"] = content_filter
            
        response = await self._make_request("GET", "photos/random", params)
        
        # Handle single photo or array
        if isinstance(response, list):
            return [self._parse_photo(photo) for photo in response]
        else:
            return [self._parse_photo(response)]
    
    async def get_photo(self, photo_id: str) -> UnsplashPhoto:
        """Get specific photo by ID"""
        
        response = await self._make_request("GET", f"photos/{photo_id}")
        return self._parse_photo(response)
    
    async def get_photo_statistics(self, photo_id: str) -> UnsplashStats:
        """Get photo download/view statistics"""
        
        response = await self._make_request("GET", f"photos/{photo_id}/statistics")
        
        return UnsplashStats(
            photo_id=photo_id,
            downloads=response.get("downloads", {}).get("total", 0),
            views=response.get("views", {}).get("total", 0),
            likes=response.get("likes", {}).get("total", 0),
            historical_downloads=response.get("downloads", {}).get("historical", []),
            historical_views=response.get("views", {}).get("historical", [])
        )
    
    # =================== COLLECTIONS ===================
    
    async def get_collections(
        self,
        page: int = 1,
        per_page: int = 20
    ) -> List[UnsplashCollection]:
        """Get featured collections"""
        
        params = {
            "page": page,
            "per_page": min(per_page, 30)
        }
        
        response = await self._make_request("GET", "collections", params)
        
        collections = []
        for collection_data in response:
            collections.append(self._parse_collection(collection_data))
        
        return collections
    
    async def get_collection(self, collection_id: str) -> UnsplashCollection:
        """Get specific collection"""
        
        response = await self._make_request("GET", f"collections/{collection_id}")
        return self._parse_collection(response)
    
    async def get_collection_photos(
        self,
        collection_id: str,
        page: int = 1,
        per_page: int = 20
    ) -> List[UnsplashPhoto]:
        """Get photos from a collection"""
        
        params = {
            "page": page,
            "per_page": min(per_page, 30)
        }
        
        response = await self._make_request("GET", f"collections/{collection_id}/photos", params)
        
        photos = []
        for photo_data in response:
            photos.append(self._parse_photo(photo_data))
        
        return photos
    
    # =================== USERS ===================
    
    async def get_user(self, username: str) -> UnsplashUser:
        """Get user profile"""
        
        response = await self._make_request("GET", f"users/{username}")
        return self._parse_user(response)
    
    async def get_user_photos(
        self,
        username: str,
        page: int = 1,
        per_page: int = 20,
        order_by: str = "latest"
    ) -> List[UnsplashPhoto]:
        """Get user's photos"""
        
        params = {
            "page": page,
            "per_page": min(per_page, 30),
            "order_by": order_by  # latest, oldest, popular
        }
        
        response = await self._make_request("GET", f"users/{username}/photos", params)
        
        photos = []
        for photo_data in response:
            photos.append(self._parse_photo(photo_data))
        
        return photos
    
    async def get_user_collections(
        self,
        username: str,
        page: int = 1,
        per_page: int = 20
    ) -> List[UnsplashCollection]:
        """Get user's collections"""
        
        params = {
            "page": page,
            "per_page": min(per_page, 30)
        }
        
        response = await self._make_request("GET", f"users/{username}/collections", params)
        
        collections = []
        for collection_data in response:
            collections.append(self._parse_collection(collection_data))
        
        return collections
    
    # =================== DOWNLOAD TRACKING ===================
    
    async def track_download(self, photo_id: str) -> Dict[str, Any]:
        """Track photo download (required by Unsplash API Guidelines)"""
        
        response = await self._make_request("GET", f"photos/{photo_id}/download")
        return response
    
    # =================== UTILITY METHODS ===================
    
    def _parse_photo(self, photo_data: Dict[str, Any]) -> UnsplashPhoto:
        """Parse photo data from API response"""
        
        return UnsplashPhoto(
            photo_id=photo_data.get("id"),
            description=photo_data.get("description", ""),
            alt_description=photo_data.get("alt_description", ""),
            urls=photo_data.get("urls", {}),
            width=photo_data.get("width", 0),
            height=photo_data.get("height", 0),
            color=photo_data.get("color", "#000000"),
            likes=photo_data.get("likes", 0),
            downloads=photo_data.get("downloads", 0),
            created_at=datetime.fromisoformat(photo_data.get("created_at", "").replace("Z", "+00:00")) if photo_data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(photo_data.get("updated_at", "").replace("Z", "+00:00")) if photo_data.get("updated_at") else datetime.now(),
            photographer=photo_data.get("user", {}),
            tags=[tag.get("title", "") for tag in photo_data.get("tags", [])],
            exif=photo_data.get("exif"),
            location=photo_data.get("location")
        )
    
    def _parse_collection(self, collection_data: Dict[str, Any]) -> UnsplashCollection:
        """Parse collection data from API response"""
        
        return UnsplashCollection(
            collection_id=collection_data.get("id"),
            title=collection_data.get("title", ""),
            description=collection_data.get("description", ""),
            total_photos=collection_data.get("total_photos", 0),
            private=collection_data.get("private", False),
            share_key=collection_data.get("share_key", ""),
            cover_photo=collection_data.get("cover_photo", {}),
            user=collection_data.get("user", {}),
            created_at=datetime.fromisoformat(collection_data.get("created_at", "").replace("Z", "+00:00")) if collection_data.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(collection_data.get("updated_at", "").replace("Z", "+00:00")) if collection_data.get("updated_at") else datetime.now()
        )
    
    def _parse_user(self, user_data: Dict[str, Any]) -> UnsplashUser:
        """Parse user data from API response"""
        
        return UnsplashUser(
            user_id=user_data.get("id"),
            username=user_data.get("username", ""),
            name=user_data.get("name", ""),
            portfolio_url=user_data.get("portfolio_url"),
            bio=user_data.get("bio"),
            location=user_data.get("location"),
            total_likes=user_data.get("total_likes", 0),
            total_photos=user_data.get("total_photos", 0),
            total_collections=user_data.get("total_collections", 0),
            instagram_username=user_data.get("instagram_username"),
            twitter_username=user_data.get("twitter_username"),
            profile_image=user_data.get("profile_image", {})
        )
    
    async def test_connection(self) -> bool:
        """Test API connection"""
        try:
            await self._make_request("GET", "photos", {"per_page": 1})
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    # =================== CONTENT CREATION HELPERS ===================
    
    async def get_photos_for_content(
        self,
        topic: str,
        count: int = 5,
        orientation: str = "landscape",
        quality: str = "high"
    ) -> List[UnsplashPhoto]:
        """Get curated photos for content creation"""
        
        # Search for high-quality photos
        search_result = await self.search_photos(
            query=topic,
            per_page=count * 2,  # Get more to filter
            order_by="popular",
            orientation=orientation,
            size="large" if quality == "high" else "medium"
        )
        
        # Filter for best quality photos
        quality_photos = []
        for photo in search_result["photos"]:
            if photo.width >= 1920 and photo.height >= 1080:  # HD minimum
                quality_photos.append(photo)
                if len(quality_photos) >= count:
                    break
        
        return quality_photos[:count]
    
    async def get_trending_photos(self, limit: int = 20) -> List[UnsplashPhoto]:
        """Get currently trending photos"""
        
        # Get popular recent photos
        search_result = await self.search_photos(
            query="trending",
            per_page=limit,
            order_by="popular"
        )
        
        return search_result["photos"]