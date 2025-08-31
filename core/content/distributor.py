"""Content Distributor - Multi-Platform Content Distribution Engine
================================================================

The ContentDistributor manages content distribution across multiple platforms
and channels according to platform-specific requirements and user preferences.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from ..platforms.youtube_api import YouTubeAPI
from ..platforms.instagram_api import InstagramAPI
from ..platforms.tiktok_api import TikTokAPI
from ..platforms.spotify_api import SpotifyAPI
from ..platforms.soundcloud_api import SoundCloudAPI


class DistributionStatus(Enum):
    """Distribution status enumeration"""
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"
    SCHEDULED = "scheduled"


@dataclass
class DistributionConfig:
    """Distribution configuration"""
    auto_publish: bool = False
    schedule_time: Optional[datetime] = None
    platforms: List[str] = None
    custom_metadata: Dict[str, Any] = None
    notification_settings: Dict[str, bool] = None


class ContentDistributor:
    """
    Multi-Platform Content Distribution Engine
    
    Handles automated distribution of content across multiple platforms
    including YouTube, Instagram, TikTok, Spotify, SoundCloud, and more.
    
    Features:
    - Platform-specific optimization
    - Scheduled publishing
    - Cross-platform synchronization
    - Performance tracking
    - Automated metadata optimization
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.logger = logging.getLogger(__name__)
        
        # Initialize platform APIs
        self.platforms = {
            "youtube": YouTubeAPI(),
            "instagram": InstagramAPI(),
            "tiktok": TikTokAPI(),
            "spotify": SpotifyAPI(),
            "soundcloud": SoundCloudAPI()
        }
        
        # Distribution tracking
        self.active_distributions = {}

    async def distribute_content(
        self,
        content_id: str,
        platforms: List[str],
        config: DistributionConfig = None
    ) -> Dict[str, Any]:
        """
        Distribute content across specified platforms
        
        Args:
            content_id: Content identifier
            platforms: List of target platforms
            config: Distribution configuration
            
        Returns:
            Distribution result with status per platform
        """
        try:
            distribution_id = str(uuid.uuid4())
            config = config or DistributionConfig()
            
            self.logger.info(f"Starting distribution {distribution_id} for content {content_id}")
            
            # Get content details
            content = await self._get_content(content_id)
            if not content:
                return {
                    "success": False,
                    "error": "Content not found",
                    "distribution_id": distribution_id
                }
            
            # Initialize distribution tracking
            self.active_distributions[distribution_id] = {
                "content_id": content_id,
                "platforms": platforms,
                "status": DistributionStatus.PENDING.value,
                "platform_results": {},
                "started_at": datetime.utcnow()
            }
            
            distribution_results = {}
            
            # Distribute to each platform
            for platform in platforms:
                if platform not in self.platforms:
                    distribution_results[platform] = {
                        "success": False,
                        "error": f"Platform {platform} not supported"
                    }
                    continue
                
                try:
                    platform_result = await self._distribute_to_platform(
                        content, platform, config
                    )
                    distribution_results[platform] = platform_result
                    
                except Exception as e:
                    distribution_results[platform] = {
                        "success": False,
                        "error": f"Distribution to {platform} failed: {str(e)}"
                    }
            
            # Update distribution tracking
            self.active_distributions[distribution_id]["platform_results"] = distribution_results
            self.active_distributions[distribution_id]["status"] = DistributionStatus.PUBLISHED.value
            
            # Calculate overall success rate
            successful_platforms = sum(
                1 for result in distribution_results.values() 
                if result.get("success", False)
            )
            success_rate = successful_platforms / len(platforms) if platforms else 0
            
            return {
                "success": success_rate > 0,
                "distribution_id": distribution_id,
                "content_id": content_id,
                "platforms_targeted": len(platforms),
                "platforms_successful": successful_platforms,
                "success_rate": success_rate,
                "platform_results": distribution_results
            }
            
        except Exception as e:
            error_msg = f"Content distribution failed: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "distribution_id": distribution_id
            }

    async def _distribute_to_platform(
        self,
        content,
        platform: str,
        config: DistributionConfig
    ) -> Dict[str, Any]:
        """
        Distribute content to specific platform
        
        Args:
            content: Content object
            platform: Target platform name
            config: Distribution configuration
            
        Returns:
            Platform-specific distribution result
        """
        try:
            platform_api = self.platforms[platform]
            
            # Prepare platform-specific metadata
            metadata = await self._prepare_platform_metadata(content, platform, config)
            
            # Upload content to platform
            upload_result = await platform_api.upload_content(
                file_path=content.file_path,
                metadata=metadata,
                content_type=content.content_type
            )
            
            if upload_result.get("success", False):
                return {
                    "success": True,
                    "platform": platform,
                    "platform_id": upload_result.get("platform_id"),
                    "platform_url": upload_result.get("url"),
                    "upload_time": datetime.utcnow().isoformat(),
                    "metadata_used": metadata
                }
            else:
                return {
                    "success": False,
                    "platform": platform,
                    "error": upload_result.get("error", "Upload failed")
                }
                
        except Exception as e:
            return {
                "success": False,
                "platform": platform,
                "error": f"Platform distribution failed: {str(e)}"
            }

    async def _prepare_platform_metadata(
        self,
        content,
        platform: str,
        config: DistributionConfig
    ) -> Dict[str, Any]:
        """
        Prepare platform-specific metadata
        
        Args:
            content: Content object
            platform: Target platform
            config: Distribution configuration
            
        Returns:
            Platform-optimized metadata
        """
        base_metadata = {
            "title": content.title,
            "description": content.metadata.get("description", ""),
            "tags": content.metadata.get("tags", []),
            "category": content.metadata.get("category", "general")
        }
        
        # Apply custom metadata from config
        if config.custom_metadata:
            base_metadata.update(config.custom_metadata)
        
        # Platform-specific optimizations
        if platform == "youtube":
            return await self._optimize_youtube_metadata(base_metadata, content)
        elif platform == "instagram":
            return await self._optimize_instagram_metadata(base_metadata, content)
        elif platform == "tiktok":
            return await self._optimize_tiktok_metadata(base_metadata, content)
        elif platform == "spotify":
            return await self._optimize_spotify_metadata(base_metadata, content)
        elif platform == "soundcloud":
            return await self._optimize_soundcloud_metadata(base_metadata, content)
        else:
            return base_metadata

    async def _optimize_youtube_metadata(self, metadata: Dict, content) -> Dict[str, Any]:
        """Optimize metadata for YouTube"""
        optimized = metadata.copy()
        
        # YouTube-specific optimizations
        optimized["title"] = metadata["title"][:100]  # YouTube title limit
        optimized["description"] = metadata["description"][:5000]  # Description limit
        optimized["tags"] = metadata["tags"][:500]  # Tags limit
        
        # Add YouTube-specific fields
        optimized["privacy_status"] = "public"
        optimized["category_id"] = self._get_youtube_category_id(metadata.get("category"))
        
        return optimized

    async def _optimize_instagram_metadata(self, metadata: Dict, content) -> Dict[str, Any]:
        """Optimize metadata for Instagram"""
        optimized = metadata.copy()
        
        # Instagram-specific optimizations
        optimized["caption"] = f"{metadata['title']}\n\n{metadata['description']}"[:2200]
        optimized["hashtags"] = self._format_instagram_hashtags(metadata.get("tags", []))
        
        return optimized

    async def _optimize_tiktok_metadata(self, metadata: Dict, content) -> Dict[str, Any]:
        """Optimize metadata for TikTok"""
        optimized = metadata.copy()
        
        # TikTok-specific optimizations
        optimized["description"] = metadata["description"][:150]  # TikTok caption limit
        optimized["hashtags"] = self._format_tiktok_hashtags(metadata.get("tags", []))
        
        return optimized

    async def _optimize_spotify_metadata(self, metadata: Dict, content) -> Dict[str, Any]:
        """Optimize metadata for Spotify"""
        optimized = metadata.copy()
        
        # Spotify-specific fields for podcasts/music
        optimized["artist"] = content.metadata.get("artist", "Unknown Artist")
        optimized["album"] = content.metadata.get("album", metadata["title"])
        optimized["genre"] = content.metadata.get("genre", "general")
        
        return optimized

    async def _optimize_soundcloud_metadata(self, metadata: Dict, content) -> Dict[str, Any]:
        """Optimize metadata for SoundCloud"""
        optimized = metadata.copy()
        
        # SoundCloud-specific optimizations
        optimized["track_type"] = content.metadata.get("track_type", "original")
        optimized["genre"] = content.metadata.get("genre", "general")
        optimized["sharing"] = "public"
        
        return optimized

    def _get_youtube_category_id(self, category: str) -> str:
        """Map content category to YouTube category ID"""
        category_mapping = {
            "music": "10",
            "education": "27",
            "entertainment": "24",
            "gaming": "20",
            "tech": "28",
            "travel": "19",
            "sports": "17"
        }
        return category_mapping.get(category.lower(), "24")  # Default to Entertainment

    def _format_instagram_hashtags(self, tags: List[str]) -> str:
        """Format tags for Instagram hashtags"""
        hashtags = [f"#{tag.replace(' ', '').lower()}" for tag in tags[:30]]  # Instagram limit
        return " ".join(hashtags)

    def _format_tiktok_hashtags(self, tags: List[str]) -> str:
        """Format tags for TikTok hashtags"""
        hashtags = [f"#{tag.replace(' ', '').lower()}" for tag in tags[:10]]  # TikTok practical limit
        return " ".join(hashtags)

    async def get_distribution_status(self, distribution_id: str) -> Dict[str, Any]:
        """
        Get distribution status
        
        Args:
            distribution_id: Distribution identifier
            
        Returns:
            Distribution status information
        """
        try:
            if distribution_id in self.active_distributions:
                distribution = self.active_distributions[distribution_id]
                return {
                    "success": True,
                    "distribution_id": distribution_id,
                    "status": distribution["status"],
                    "content_id": distribution["content_id"],
                    "platforms": distribution["platforms"],
                    "platform_results": distribution["platform_results"],
                    "started_at": distribution["started_at"].isoformat()
                }
            
            return {
                "success": False,
                "error": "Distribution not found"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def schedule_distribution(
        self,
        content_id: str,
        platforms: List[str],
        schedule_time: datetime,
        config: DistributionConfig = None
    ) -> Dict[str, Any]:
        """
        Schedule content distribution for later
        
        Args:
            content_id: Content identifier
            platforms: Target platforms
            schedule_time: When to publish
            config: Distribution configuration
            
        Returns:
            Scheduling result
        """
        try:
            schedule_id = str(uuid.uuid4())
            
            # Store scheduled distribution
            scheduled_distribution = {
                "schedule_id": schedule_id,
                "content_id": content_id,
                "platforms": platforms,
                "schedule_time": schedule_time,
                "config": config,
                "status": DistributionStatus.SCHEDULED.value,
                "created_at": datetime.utcnow()
            }
            
            # In a real implementation, this would be stored in database
            # and processed by a scheduler service
            
            return {
                "success": True,
                "schedule_id": schedule_id,
                "content_id": content_id,
                "platforms": platforms,
                "scheduled_for": schedule_time.isoformat(),
                "status": DistributionStatus.SCHEDULED.value
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Scheduling failed: {str(e)}"
            }

    async def cancel_distribution(self, distribution_id: str) -> Dict[str, Any]:
        """
        Cancel ongoing or scheduled distribution
        
        Args:
            distribution_id: Distribution identifier
            
        Returns:
            Cancellation result
        """
        try:
            if distribution_id in self.active_distributions:
                distribution = self.active_distributions[distribution_id]
                
                # Attempt to cancel platform uploads
                cancellation_results = {}
                for platform, result in distribution["platform_results"].items():
                    if result.get("success") and result.get("platform_id"):
                        cancel_result = await self._cancel_platform_upload(
                            platform, result["platform_id"]
                        )
                        cancellation_results[platform] = cancel_result
                
                # Update status
                distribution["status"] = "cancelled"
                
                return {
                    "success": True,
                    "distribution_id": distribution_id,
                    "status": "cancelled",
                    "cancellation_results": cancellation_results
                }
            
            return {
                "success": False,
                "error": "Distribution not found"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Cancellation failed: {str(e)}"
            }

    async def _cancel_platform_upload(self, platform: str, platform_id: str) -> Dict[str, Any]:
        """Cancel upload on specific platform"""
        try:
            platform_api = self.platforms[platform]
            if hasattr(platform_api, 'cancel_upload'):
                return await platform_api.cancel_upload(platform_id)
            else:
                return {
                    "success": False,
                    "error": f"Platform {platform} does not support upload cancellation"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Platform cancellation failed: {str(e)}"
            }

    async def _get_content(self, content_id: str):
        """Get content from database"""
        # This would query the actual database
        # For now, return a mock content object
        class MockContent:
            def __init__(self):
                self.id = content_id
                self.title = "Sample Content"
                self.file_path = "/path/to/content"
                self.content_type = "video"
                self.metadata = {
                    "description": "Sample description",
                    "tags": ["sample", "content"],
                    "category": "entertainment"
                }
        
        return MockContent()

    async def get_platform_analytics(self, content_id: str) -> Dict[str, Any]:
        """
        Get analytics from all platforms for specific content
        
        Args:
            content_id: Content identifier
            
        Returns:
            Aggregated platform analytics
        """
        try:
            analytics = {}
            
            # Collect analytics from each platform
            for platform_name, platform_api in self.platforms.items():
                try:
                    if hasattr(platform_api, 'get_content_analytics'):
                        platform_analytics = await platform_api.get_content_analytics(content_id)
                        analytics[platform_name] = platform_analytics
                except Exception as e:
                    analytics[platform_name] = {
                        "error": f"Analytics retrieval failed: {str(e)}"
                    }
            
            return {
                "success": True,
                "content_id": content_id,
                "platform_analytics": analytics,
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Analytics retrieval failed: {str(e)}"
            }
