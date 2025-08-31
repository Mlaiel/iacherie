"""
Platform Registry Manager for IA Influencer Agent - Professional Content Distribution Platform
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

 LEGAL WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written permission is strictly prohibited.
Violators will be prosecuted to the full extent of the law.

 Professional Team Expertise:
- Lead IA Developer: Advanced AI/ML Architecture
- Senior Backend Engineer: Enterprise-grade Infrastructure  
- ML Engineer: Deep Learning & Data Processing
- Database Architect: High-performance Data Management
- Security Engineer: Advanced Cybersecurity & Protection
- Microservices Architect: Scalable Distributed Systems
- Audio Engineer: Professional Audio Processing
- DevOps Engineer: Cloud Infrastructure & CI/CD
- IA Prompt Engineer: Advanced Prompt Engineering & LLM Integration
"""

import logging
from typing import Dict, List, Optional, Type, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import importlib
import inspect

from .distribution_models import PlatformType, PlatformCapabilities, ContentType, ContentMetadata
from .distribution_schemas import PlatformStatusSchema


logger = logging.getLogger(__name__)


@dataclass
class PlatformAdapter:
    """Base platform adapter interface"""
    platform_type: PlatformType
    capabilities: PlatformCapabilities
    adapter_class: Type
    is_active: bool = True
    last_health_check: Optional[datetime] = None
    error_count: int = 0
    rate_limit_remaining: int = 100
    rate_limit_reset: Optional[datetime] = None


class PlatformRegistryManager:
    """Professional platform registry manager for all distribution platforms"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._adapters: Dict[PlatformType, PlatformAdapter] = {}
        self._capabilities_cache: Dict[PlatformType, PlatformCapabilities] = {}
        self._health_check_interval = timedelta(minutes=5)
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._initialize_platform_registry()
    
    def _initialize_platform_registry(self):
        """Initialize all platform adapters with their capabilities"""
        
        # YouTube Platform
        self._register_platform(
            PlatformType.YOUTUBE,
            PlatformCapabilities(
                max_file_size=256 * 1024 * 1024 * 1024,  # 256GB
                supported_formats=["mp4", "mov", "avi", "wmv", "flv", "webm", "mkv"],
                max_duration=12 * 60 * 60,  # 12 hours
                supports_scheduling=True,
                supports_monetization=True,
                supports_analytics=True,
                supports_collaboration=True,
                requires_approval=False,
                api_rate_limit=10000
            )
        )
        
        # Instagram Platform
        self._register_platform(
            PlatformType.INSTAGRAM,
            PlatformCapabilities(
                max_file_size=4 * 1024 * 1024 * 1024,  # 4GB
                supported_formats=["mp4", "mov", "jpg", "jpeg", "png", "gif"],
                max_duration=60 * 60,  # 1 hour
                supports_scheduling=True,
                supports_monetization=True,
                supports_analytics=True,
                supports_collaboration=True,
                requires_approval=False,
                api_rate_limit=200
            )
        )
        
        # TikTok Platform
        self._register_platform(
            PlatformType.TIKTOK,
            PlatformCapabilities(
                max_file_size=287 * 1024 * 1024,  # 287MB
                supported_formats=["mp4", "mov", "avi"],
                max_duration=10 * 60,  # 10 minutes
                supports_scheduling=True,
                supports_monetization=True,
                supports_analytics=True,
                supports_collaboration=True,
                requires_approval=False,
                api_rate_limit=100
            )
        )
        
        # Complete platform initialization
        self._register_additional_platforms()
    
    def _register_additional_platforms(self):
        """Register all additional platforms with their capabilities"""
        
        platforms_config = {
            PlatformType.SPOTIFY: PlatformCapabilities(
                max_file_size=650 * 1024 * 1024,  # 650MB
                supported_formats=["mp3", "wav", "flac", "ogg", "m4a"],
                supports_monetization=True,
                requires_approval=True,
                api_rate_limit=1000
            ),
            PlatformType.TWITTER: PlatformCapabilities(
                max_file_size=512 * 1024 * 1024,  # 512MB
                supported_formats=["mp4", "mov", "gif", "jpg", "jpeg", "png"],
                max_duration=2 * 60 + 20,  # 2:20
                api_rate_limit=300
            ),
            PlatformType.FACEBOOK: PlatformCapabilities(
                max_file_size=10 * 1024 * 1024 * 1024,  # 10GB
                supported_formats=["mp4", "mov", "avi", "jpg", "jpeg", "png", "gif"],
                max_duration=4 * 60 * 60,  # 4 hours
                supports_monetization=True,
                supports_collaboration=True,
                api_rate_limit=600
            ),
            PlatformType.LINKEDIN: PlatformCapabilities(
                max_file_size=5 * 1024 * 1024 * 1024,  # 5GB
                supported_formats=["mp4", "mov", "avi", "jpg", "jpeg", "png", "pdf"],
                max_duration=10 * 60,  # 10 minutes
                api_rate_limit=500
            ),
            PlatformType.PINTEREST: PlatformCapabilities(
                max_file_size=2 * 1024 * 1024 * 1024,  # 2GB
                supported_formats=["jpg", "jpeg", "png", "gif", "mp4", "mov"],
                max_duration=15 * 60,  # 15 minutes
                supports_monetization=True,
                api_rate_limit=1000
            ),
            PlatformType.TWITCH: PlatformCapabilities(
                max_file_size=10 * 1024 * 1024 * 1024,  # 10GB
                supported_formats=["mp4", "mov", "flv"],
                supports_monetization=True,
                supports_collaboration=True,
                api_rate_limit=800
            ),
            PlatformType.SOUNDCLOUD: PlatformCapabilities(
                max_file_size=4 * 1024 * 1024 * 1024,  # 4GB
                supported_formats=["mp3", "wav", "flac", "aiff", "ogg"],
                max_duration=6 * 60 * 60,  # 6 hours
                supports_monetization=True,
                supports_collaboration=True,
                api_rate_limit=15000
            )
        }
        
        for platform_type, capabilities in platforms_config.items():
            self._register_platform(platform_type, capabilities)
    
    def _register_platform(self, platform_type: PlatformType, capabilities: PlatformCapabilities):
        """Register a platform with its capabilities"""



        try:
            adapter_class = self._import_adapter_class(platform_type)
            
            adapter = PlatformAdapter(
                platform_type=platform_type,
                capabilities=capabilities,
                adapter_class=adapter_class,
                is_active=adapter_class is not None,
                last_health_check=datetime.now()
            )
            
            self._adapters[platform_type] = adapter
            self._capabilities_cache[platform_type] = capabilities
            
            self.logger.info(f"Registered platform: {platform_type.value}")
            
        except Exception as e:
            self.logger.error(f"Failed to register platform {platform_type.value}: {e}")
    
    def _import_adapter_class(self, platform_type: PlatformType) -> Optional[Type]:
        """Dynamically import adapter class for platform"""



        try:
            module_name = f".{platform_type.value}_adapter"
            class_name = f"{platform_type.value.title()}Adapter"
            
            module = importlib.import_module(module_name, package=__package__)
            adapter_class = getattr(module, class_name)
            
            return adapter_class
            
        except (ImportError, AttributeError):
            return None
    
    def get_supported_platforms(self) -> List[PlatformType]:
        """Get list of all supported platforms"""



        return list(self._adapters.keys())
    
    def get_active_platforms(self) -> List[PlatformType]:
        """Get list of active platforms"""



        return [
            platform for platform, adapter in self._adapters.items()
            if adapter.is_active and adapter.adapter_class is not None
        ]
    
    def get_platform_capabilities(self, platform: PlatformType) -> Optional[PlatformCapabilities]:
        """Get capabilities for a specific platform"""



        return self._capabilities_cache.get(platform)
    
    def is_content_supported(self, platform: PlatformType, content_metadata: ContentMetadata) -> bool:
        """Check if content is supported by platform"""
        capabilities = self.get_platform_capabilities(platform)
        if not capabilities:
            return False
        
        # Check file size
        if content_metadata.file_size > capabilities.max_file_size:
            return False
        
        # Check format
        if content_metadata.format.lower() not in [f.lower() for f in capabilities.supported_formats]:
            return False
        
        # Check duration
        if capabilities.max_duration and content_metadata.duration:
            if content_metadata.duration > capabilities.max_duration:
                return False
        
        return True
    
    def get_compatible_platforms(self, content_metadata: ContentMetadata) -> List[PlatformType]:
        """Get list of platforms compatible with content"""



        return [
            platform for platform in self.get_active_platforms()
            if self.is_content_supported(platform, content_metadata)
        ]


# Global registry instance
platform_registry = PlatformRegistryManager()

import logging
from typing import Dict, Type, List, Optional, Any
from dataclasses import dataclass

from .core.base_adapter import BasePlatformAdapter
from .youtube_adapter import YouTubeAdapter
from .instagram_adapter import InstagramAdapter
from .tiktok_adapter import TikTokAdapter
from .spotify_adapter import SpotifyAdapter
from .twitter_adapter import TwitterAdapter
from .facebook_adapter import FacebookAdapter
from .linkedin_adapter import LinkedInAdapter
from .pinterest_adapter import PinterestAdapter
from .twitch_adapter import TwitchAdapter
from .discord_adapter import DiscordAdapter

logger = logging.getLogger(__name__)

@dataclass
class PlatformConfig:
    """Configuration for a platform adapter."""
    name: str
    adapter_class: Type[BasePlatformAdapter]
    category: str
    is_active: bool = True
    supports_video: bool = False
    supports_audio: bool = False
    supports_images: bool = False
    supports_text: bool = False
    supports_live_streaming: bool = False
    monetization_available: bool = False
    analytics_available: bool = False
    api_cost_tier: str = "free"  # free, low, medium, high
    business_priority: int = 1  # 1=highest, 5=lowest

class PlatformRegistry:
    """
    Central registry for ALL platform adapters.
    Manages platform discovery, loading, and configuration.
    """
    
    def __init__(self):
        self._platforms: Dict[str, PlatformConfig] = {}
        self._initialized_adapters: Dict[str, BasePlatformAdapter] = {}
        self._register_all_platforms()
    
    def _register_all_platforms(self):
        """Register all available platform adapters."""
        
        # Social Media Platforms
        self.register_platform(PlatformConfig(
            name="youtube",
            adapter_class=YouTubeAdapter,
            category="video_social",
            supports_video=True,
            supports_images=True,
            supports_text=True,
            supports_live_streaming=True,
            monetization_available=True,
            analytics_available=True,
            api_cost_tier="medium",
            business_priority=1
        ))
        
        self.register_platform(PlatformConfig(
            name="instagram",
            adapter_class=InstagramAdapter,
            category="visual_social",
            supports_video=True,
            supports_images=True,
            supports_text=True,
            monetization_available=True,
            analytics_available=True,
            api_cost_tier="low",
            business_priority=1
        ))
        
        self.register_platform(PlatformConfig(
            name="tiktok",
            adapter_class=TikTokAdapter,
            category="video_social",
            supports_video=True,
            supports_images=True,
            supports_text=True,
            monetization_available=True,
            analytics_available=True,
            api_cost_tier="medium",
            business_priority=1
        ))
        
        self.register_platform(PlatformConfig(
            name="facebook",
            adapter_class=FacebookAdapter,
            category="social_network",
            supports_video=True,
            supports_images=True,
            supports_text=True,
            supports_live_streaming=True,
            monetization_available=True,
            analytics_available=True,
            api_cost_tier="low",
            business_priority=2
        ))
        
        self.register_platform(PlatformConfig(
            name="twitter",
            adapter_class=TwitterAdapter,
            category="microblogging",
            supports_video=True,
            supports_images=True,
            supports_text=True,
            monetization_available=True,
            analytics_available=True,
            api_cost_tier="high",
            business_priority=2
        ))
        
        # Professional Platforms
        self.register_platform(PlatformConfig(
            name="linkedin",
            adapter_class=LinkedInAdapter,
            category="professional",
            supports_video=True,
            supports_images=True,
            supports_text=True,
            monetization_available=True,
            analytics_available=True,
            api_cost_tier="medium",
            business_priority=2
        ))
        
        # Visual Platforms
        self.register_platform(PlatformConfig(
            name="pinterest",
            adapter_class=PinterestAdapter,
            category="visual_discovery",
            supports_video=True,
            supports_images=True,
            supports_text=True,
            monetization_available=True,
            analytics_available=True,
            api_cost_tier="low",
            business_priority=3
        ))
        
        # Music Platforms
        self.register_platform(PlatformConfig(
            name="spotify",
            adapter_class=SpotifyAdapter,
            category="music_streaming",
            supports_audio=True,
            supports_text=True,
            monetization_available=True,
            analytics_available=True,
            api_cost_tier="medium",
            business_priority=1
        ))
        
        # Gaming & Streaming Platforms
        self.register_platform(PlatformConfig(
            name="twitch",
            adapter_class=TwitchAdapter,
            category="live_streaming",
            supports_video=True,
            supports_text=True,
            supports_live_streaming=True,
            monetization_available=True,
            analytics_available=True,
            api_cost_tier="medium",
            business_priority=2
        ))
        
        # Community Platforms
        self.register_platform(PlatformConfig(
            name="discord",
            adapter_class=DiscordAdapter,
            category="community",
            supports_video=True,
            supports_images=True,
            supports_audio=True,
            supports_text=True,
            monetization_available=False,
            analytics_available=True,
            api_cost_tier="free",
            business_priority=3
        ))
        
        logger.info(f"Registered {len(self._platforms)} platform adapters")
    
    def register_platform(self, config: PlatformConfig):
        """Register a new platform adapter."""
        self._platforms[config.name] = config
        logger.debug(f"Registered platform: {config.name}")
    
    def get_platform_config(self, platform_name: str) -> Optional[PlatformConfig]:
        """Get platform configuration by name."""



        return self._platforms.get(platform_name)
    
    def get_all_platforms(self) -> Dict[str, PlatformConfig]:
        """Get all registered platforms."""



        return self._platforms.copy()
    
    def get_platforms_by_category(self, category: str) -> Dict[str, PlatformConfig]:
        """Get all platforms in a specific category."""



        return {
            name: config for name, config in self._platforms.items()
            if config.category == category
        }
    
    def get_platforms_by_content_type(self, content_type: str) -> Dict[str, PlatformConfig]:
        """Get platforms that support specific content type."""
        content_type_mapping = {
            "video": "supports_video",
            "audio": "supports_audio", 
            "image": "supports_images",
            "text": "supports_text"
        }
        
        attribute = content_type_mapping.get(content_type)
        if not attribute:
            return {}
        
        return {
            name: config for name, config in self._platforms.items()
            if getattr(config, attribute, False) and config.is_active
        }
    
    def get_monetization_platforms(self) -> Dict[str, PlatformConfig]:
        """Get platforms that support monetization."""



        return {
            name: config for name, config in self._platforms.items()
            if config.monetization_available and config.is_active
        }
    
    def get_high_priority_platforms(self) -> Dict[str, PlatformConfig]:
        """Get high business priority platforms."""



        return {
            name: config for name, config in self._platforms.items()
            if config.business_priority <= 2 and config.is_active
        }
    
    def get_free_tier_platforms(self) -> Dict[str, PlatformConfig]:
        """Get platforms with free API tier."""



        return {
            name: config for name, config in self._platforms.items()
            if config.api_cost_tier == "free" and config.is_active
        }
    
    def initialize_adapter(self, platform_name: str, credentials: Any) -> Optional[BasePlatformAdapter]:
        """Initialize a platform adapter with credentials."""



        try:
            config = self.get_platform_config(platform_name)
            if not config:
                logger.error(f"Platform {platform_name} not found in registry")
                return None
            
            if not config.is_active:
                logger.warning(f"Platform {platform_name} is inactive")
                return None
            
            # Check if already initialized
            if platform_name in self._initialized_adapters:
                return self._initialized_adapters[platform_name]
            
            # Initialize new adapter
            adapter = config.adapter_class(credentials)
            self._initialized_adapters[platform_name] = adapter
            
            logger.info(f"Initialized adapter for platform: {platform_name}")
            return adapter
            
        except Exception as e:
            logger.error(f"Failed to initialize adapter for {platform_name}: {e}")
            return None
    
    def get_adapter(self, platform_name: str) -> Optional[BasePlatformAdapter]:
        """Get initialized adapter instance."""



        return self._initialized_adapters.get(platform_name)
    
    def get_platform_recommendations(self, content_metadata: Any) -> List[str]:
        """Get recommended platforms based on content metadata."""
        recommendations = []
        
        # Analyze content type
        content_type = getattr(content_metadata, 'content_type', 'text').lower()
        suitable_platforms = self.get_platforms_by_content_type(content_type)
        
        # Sort by business priority and features
        sorted_platforms = sorted(
            suitable_platforms.items(),
            key=lambda x: (x[1].business_priority, -int(x[1].monetization_available))
        )
        
        # Return top recommendations
        recommendations = [name for name, _ in sorted_platforms[:5]]
        
        logger.info(f"Platform recommendations for {content_type}: {recommendations}")
        return recommendations
    
    def get_distribution_strategy(self, content_metadata: Any, budget_tier: str = "medium") -> Dict[str, Any]:
        """Get optimized distribution strategy based on content and budget."""
        strategy = {
            "primary_platforms": [],
            "secondary_platforms": [],
            "budget_allocation": {},
            "timing_recommendations": {},
            "expected_reach": 0
        }
        
        content_type = getattr(content_metadata, 'content_type', 'text').lower()
        
        # Primary platforms (high priority + content type match)
        primary_platforms = []
        for name, config in self._platforms.items():
            if (config.business_priority <= 2 and 
                config.is_active and
                getattr(config, f"supports_{content_type}", False)):
                primary_platforms.append(name)
        
        # Secondary platforms based on budget
        secondary_platforms = []
        if budget_tier in ["medium", "high"]:
            for name, config in self._platforms.items():
                if (config.business_priority <= 3 and 
                    config.is_active and
                    name not in primary_platforms and
                    getattr(config, f"supports_{content_type}", False)):
                    secondary_platforms.append(name)
        
        strategy["primary_platforms"] = primary_platforms[:3]  # Top 3
        strategy["secondary_platforms"] = secondary_platforms[:2]  # Top 2
        
        # Budget allocation (simplified)
        total_platforms = len(strategy["primary_platforms"]) + len(strategy["secondary_platforms"])
        if total_platforms > 0:
            primary_allocation = 0.7 / len(strategy["primary_platforms"]) if strategy["primary_platforms"] else 0
            secondary_allocation = 0.3 / len(strategy["secondary_platforms"]) if strategy["secondary_platforms"] else 0
            
            for platform in strategy["primary_platforms"]:
                strategy["budget_allocation"][platform] = primary_allocation
            for platform in strategy["secondary_platforms"]:
                strategy["budget_allocation"][platform] = secondary_allocation
        
        logger.info(f"Distribution strategy: {len(strategy['primary_platforms'])} primary, {len(strategy['secondary_platforms'])} secondary platforms")
        return strategy
    
    def validate_platform_compatibility(self, platform_name: str, content_metadata: Any) -> Dict[str, Any]:
        """Validate if content is compatible with platform."""
        config = self.get_platform_config(platform_name)
        if not config:
            return {"compatible": False, "reason": "Platform not found"}
        
        if not config.is_active:
            return {"compatible": False, "reason": "Platform inactive"}
        
        content_type = getattr(content_metadata, 'content_type', 'text').lower()
        
        # Check content type support
        if content_type == "video" and not config.supports_video:
            return {"compatible": False, "reason": f"Platform {platform_name} doesn't support video content"}
        elif content_type == "audio" and not config.supports_audio:
            return {"compatible": False, "reason": f"Platform {platform_name} doesn't support audio content"}
        elif content_type == "image" and not config.supports_images:
            return {"compatible": False, "reason": f"Platform {platform_name} doesn't support image content"}
        
        return {
            "compatible": True,
            "monetization_available": config.monetization_available,
            "analytics_available": config.analytics_available,
            "api_cost_tier": config.api_cost_tier,
            "business_priority": config.business_priority
        }
    
    def get_platform_statistics(self) -> Dict[str, Any]:
        """Get registry statistics."""
        stats = {
            "total_platforms": len(self._platforms),
            "active_platforms": len([p for p in self._platforms.values() if p.is_active]),
            "initialized_adapters": len(self._initialized_adapters),
            "categories": {},
            "content_support": {
                "video": len([p for p in self._platforms.values() if p.supports_video]),
                "audio": len([p for p in self._platforms.values() if p.supports_audio]),
                "images": len([p for p in self._platforms.values() if p.supports_images]),
                "text": len([p for p in self._platforms.values() if p.supports_text])
            },
            "monetization_platforms": len([p for p in self._platforms.values() if p.monetization_available]),
            "live_streaming_platforms": len([p for p in self._platforms.values() if p.supports_live_streaming])
        }
        
        # Count by category
        for config in self._platforms.values():
            category = config.category
            if category in stats["categories"]:
                stats["categories"][category] += 1
            else:
                stats["categories"][category] = 1
        
        return stats

# Global registry instance
platform_registry = PlatformRegistry()

def get_platform_registry() -> PlatformRegistry:
    """Get the global platform registry instance."""



    return platform_registry
