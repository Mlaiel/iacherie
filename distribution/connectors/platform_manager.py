"""
Platform Manager - Consolidated Platform Connection Manager
=========================================================

Enterprise-grade platform management system that orchestrates all
platform connectors and provides unified interface for multi-platform
content distribution across social media, music, and creator platforms.

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
import uuid

# Import all consolidated connectors
from .social_media_connectors import SocialMediaConnectors, SocialContent, SocialPlatform
from .music_streaming_connectors import MusicStreamingConnectors, MusicContent, MusicPlatform
from .creator_economy_connectors import CreatorEconomyConnectors, CreatorContent, CreatorPlatform

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Content type enumeration"""
    SOCIAL_POST = "social_post"
    MUSIC_TRACK = "music_track"
    CREATOR_CONTENT = "creator_content"
    VIDEO = "video"
    PODCAST = "podcast"
    BLOG_POST = "blog_post"

@dataclass
class DistributionRequest:
    """Universal distribution request"""
    content_id: str
    creator_id: str
    content_type: ContentType
    platforms: List[str]
    content_data: Dict[str, Any]
    scheduling: Optional[Dict[str, Any]] = None
    monetization: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributionResult:
    """Universal distribution result"""
    request_id: str
    content_id: str
    platform_results: Dict[str, Dict[str, Any]]
    overall_success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    analytics_data: Dict[str, Any] = field(default_factory=dict)

class PlatformManager:
    """
    Main Platform Management System
    
    Orchestrates all platform connectors and provides unified interface
    for multi-platform content distribution across all supported platforms.
    """
    
    def __init__(self, platform_credentials -> None: Dict[str, Dict[str, str]]) -> None:
        """Initialize platform manager with all connector systems"""
        self.platform_credentials = platform_credentials
        
        # Initialize connector managers
        self.social_connectors = SocialMediaConnectors(
            platform_credentials.get("social_media", {})
        )
        self.music_connectors = MusicStreamingConnectors(
            platform_credentials.get("music_streaming", {})
        )
        self.creator_connectors = CreatorEconomyConnectors(
            platform_credentials.get("creator_economy", {})
        )
        
        # Distribution tracking
        self.active_distributions: Dict[str, DistributionRequest] = {}
        self.distribution_history: List[DistributionResult] = []
        
        logger.info("Platform Manager initialized with all connector systems")
    
    async def distribute_content(self, request: DistributionRequest) -> DistributionResult:
        """
        Universal content distribution across all platform types
        
        Args:
            request: Distribution request with content and platform details
            
        Returns:
            DistributionResult with comprehensive distribution outcome
        """
        request_id = str(uuid.uuid4())
        self.active_distributions[request_id] = request
        
        try:
            # Route content based on type
            if request.content_type == ContentType.SOCIAL_POST:
                platform_results = await self._distribute_social_content(request)
            elif request.content_type == ContentType.MUSIC_TRACK:
                platform_results = await self._distribute_music_content(request)
            elif request.content_type == ContentType.CREATOR_CONTENT:
                platform_results = await self._distribute_creator_content(request)
            else:
                platform_results = await self._distribute_mixed_content(request)
            
            # Determine overall success
            successful_platforms = [
                p for p, r in platform_results.items() 
                if r.get("success", False)
            ]
            overall_success = len(successful_platforms) > 0
            
            # Create result
            result = DistributionResult(
                request_id=request_id,
                content_id=request.content_id,
                platform_results=platform_results,
                overall_success=overall_success
            )
            
            # Store result and cleanup
            self.distribution_history.append(result)
            if request_id in self.active_distributions:
                del self.active_distributions[request_id]
            
            logger.info(f"Distribution {request_id} completed: {overall_success}")
            return result
            
        except Exception as e:
            logger.error(f"Distribution {request_id} failed: {e}")
            
            # Cleanup on failure
            if request_id in self.active_distributions:
                del self.active_distributions[request_id]
            
            return DistributionResult(
                request_id=request_id,
                content_id=request.content_id,
                platform_results={"error": str(e)},
                overall_success=False
            )
    
    async def _distribute_social_content(self, request: DistributionRequest) -> Dict[str, Any]:
        """Distribute social media content"""
        # Convert to SocialContent format
        social_content = SocialContent(
            content_id=request.content_id,
            title=request.content_data.get("title", ""),
            description=request.content_data.get("description", ""),
            media_urls=request.content_data.get("media_urls", []),
            hashtags=request.content_data.get("hashtags", []),
            mentions=request.content_data.get("mentions", [])
        )
        
        # Convert platform strings to enums
        social_platforms = []
        for platform_name in request.platforms:
            try:
                platform = SocialPlatform(platform_name)
                social_platforms.append(platform)
            except ValueError:
                logger.warning(f"Unknown social platform: {platform_name}")
        
        return await self.social_connectors.distribute_to_platforms(
            social_content, social_platforms
        )
    
    async def _distribute_music_content(self, request: DistributionRequest) -> Dict[str, Any]:
        """Distribute music content"""
        # Convert to MusicContent format
        music_content = MusicContent(
            content_id=request.content_id,
            title=request.content_data.get("title", ""),
            artist=request.content_data.get("artist", ""),
            album=request.content_data.get("album", ""),
            genre=request.content_data.get("genre", ""),
            audio_file_url=request.content_data.get("audio_file_url", ""),
            cover_art_url=request.content_data.get("cover_art_url")
        )
        
        # Convert platform strings to enums
        music_platforms = []
        for platform_name in request.platforms:
            try:
                platform = MusicPlatform(platform_name)
                music_platforms.append(platform)
            except ValueError:
                logger.warning(f"Unknown music platform: {platform_name}")
        
        return await self.music_connectors.distribute_music(
            music_content, music_platforms
        )
    
    async def _distribute_creator_content(self, request: DistributionRequest) -> Dict[str, Any]:
        """Distribute creator economy content"""
        # Convert to CreatorContent format
        creator_content = CreatorContent(
            content_id=request.content_id,
            title=request.content_data.get("title", ""),
            description=request.content_data.get("description", ""),
            content_type=request.content_data.get("content_type", ""),
            media_urls=request.content_data.get("media_urls", []),
            price=request.content_data.get("price"),
            tier_level=request.content_data.get("tier_level")
        )
        
        # Convert platform strings to enums
        creator_platforms = []
        for platform_name in request.platforms:
            try:
                platform = CreatorPlatform(platform_name)
                creator_platforms.append(platform)
            except ValueError:
                logger.warning(f"Unknown creator platform: {platform_name}")
        
        return await self.creator_connectors.distribute_creator_content(
            creator_content, creator_platforms
        )
    
    async def _distribute_mixed_content(self, request: DistributionRequest) -> Dict[str, Any]:
        """Distribute content to mixed platform types"""
        results = {}
        
        # Categorize platforms by type
        social_platforms = []
        music_platforms = []
        creator_platforms = []
        
        for platform_name in request.platforms:
            # Try to categorize platform
            try:
                SocialPlatform(platform_name)
                social_platforms.append(platform_name)
            except ValueError:
                try:
                    MusicPlatform(platform_name)
                    music_platforms.append(platform_name)
                except ValueError:
                    try:
                        CreatorPlatform(platform_name)
                        creator_platforms.append(platform_name)
                    except ValueError:
                        results[platform_name] = {
                            "success": False,
                            "error": "Unknown platform type"
                        }
        
        # Distribute to each platform type
        if social_platforms:
            social_request = DistributionRequest(
                content_id=request.content_id,
                creator_id=request.creator_id,
                content_type=ContentType.SOCIAL_POST,
                platforms=social_platforms,
                content_data=request.content_data
            )
            social_results = await self._distribute_social_content(social_request)
            results.update(social_results)
        
        if music_platforms:
            music_request = DistributionRequest(
                content_id=request.content_id,
                creator_id=request.creator_id,
                content_type=ContentType.MUSIC_TRACK,
                platforms=music_platforms,
                content_data=request.content_data
            )
            music_results = await self._distribute_music_content(music_request)
            results.update(music_results)
        
        if creator_platforms:
            creator_request = DistributionRequest(
                content_id=request.content_id,
                creator_id=request.creator_id,
                content_type=ContentType.CREATOR_CONTENT,
                platforms=creator_platforms,
                content_data=request.content_data
            )
            creator_results = await self._distribute_creator_content(creator_request)
            results.update(creator_results)
        
        return results
    
    async def get_all_available_platforms(self) -> Dict[str, List[str]]:
        """Get all available platforms across all connector types"""
        return {
            "social_media": self.social_connectors.get_available_platforms(),
            "music_streaming": self.music_connectors.get_available_platforms(),
            "creator_economy": self.creator_connectors.get_available_platforms()
        }
    
    async def health_check_all_platforms(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all platform connections"""
        return {
            "social_media": await self.social_connectors.health_check(),
            "music_streaming": await self.music_connectors.health_check(),
            "creator_economy": await self.creator_connectors.health_check()
        }
    
    async def get_platform_analytics(
        self,
        platform_type: str,
        platform_name: str,
        content_id: str
    ) -> Dict[str, Any]:
        """Get analytics for specific platform and content"""
        try:
            if platform_type == "social_media":
                platform = SocialPlatform(platform_name)
                return await self.social_connectors.get_platform_analytics(platform, content_id)
            elif platform_type == "music_streaming":
                platform = MusicPlatform(platform_name)
                return await self.music_connectors.get_streaming_analytics(platform, content_id, {})
            elif platform_type == "creator_economy":
                platforms = [CreatorPlatform(platform_name)]
                return await self.creator_connectors.get_revenue_analytics(platforms, {})
            else:
                return {"error": "Unknown platform type"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_distribution_history(self, creator_id: Optional[str] = None) -> List[DistributionResult]:
        """Get distribution history, optionally filtered by creator"""
        if creator_id:
            return [
                result for result in self.distribution_history
                if any(req.creator_id == creator_id for req in self.active_distributions.values())
            ]
        return self.distribution_history
    
    async def emergency_stop_distribution(self, request_id: str) -> Dict[str, Any]:
        """Emergency stop for active distribution"""
        if request_id in self.active_distributions:
            # Remove from active distributions
            del self.active_distributions[request_id]
            
            return {
                "success": True,
                "request_id": request_id,
                "message": "Distribution stopped"
            }
        
        return {
            "success": False,
            "error": "Distribution not found or already completed"
        }