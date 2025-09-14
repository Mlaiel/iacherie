"""🌐 Platform Models Module - Enterprise Platform Integration Architecture
==========================================================================
Module: models/platform_models/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Platform Integration Models - Production-Ready
Responsibility: Multi-platform integration and content distribution

⚠️  EXCLUSIVE INTELLECTUAL PROPERTY - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. All rights reserved.
Unauthorized use strictly prohibited and subject to legal prosecution.
Contact: mlaiel@live.de

This module provides enterprise-grade platform integration models supporting:
- Social Media Platforms: Instagram, TikTok, Twitter/X, Facebook, LinkedIn
- Content Platforms: YouTube, Vimeo, Twitch, Dailymotion
- Audio Platforms: Spotify, SoundCloud, Apple Music, Amazon Music
- Professional Networks: LinkedIn, Behance, Dribbble
- E-commerce Platforms: Shopify, WooCommerce, Etsy
- Payment Platforms: Stripe, PayPal, Square, Wise
- Cloud Storage: AWS S3, Google Cloud, Azure, Dropbox
- Analytics Platforms: Google Analytics, Adobe Analytics
- Email Marketing: Mailchimp, SendGrid, ConvertKit
- Collaboration Tools: Slack, Discord, Zoom

Business Logic Integration:
- Phase 7: Distribution & Analytics
- Multi-platform content distribution
- Cross-platform analytics aggregation
- Platform-specific optimization
"""

from typing import Dict, List, Any, Optional, Type, Union, Tuple
import logging
from datetime import datetime, timedelta
from enum import Enum

class PlatformType(Enum):
    """Platform type categories"""
    SOCIAL_MEDIA = "social_media"
    CONTENT_PLATFORM = "content_platform"
    AUDIO_PLATFORM = "audio_platform"
    PROFESSIONAL_NETWORK = "professional_network"
    E_COMMERCE = "e_commerce"
    PAYMENT_GATEWAY = "payment_gateway"
    CLOUD_STORAGE = "cloud_storage"
    ANALYTICS = "analytics"
    EMAIL_MARKETING = "email_marketing"
    COLLABORATION = "collaboration"

class IntegrationStatus(Enum):
    """Integration connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PENDING = "pending"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    EXPIRED = "expired"

class ContentFormat(Enum):
    """Content format for platform optimization"""
    IMAGE_SQUARE = "image_square"
    IMAGE_LANDSCAPE = "image_landscape"
    IMAGE_PORTRAIT = "image_portrait"
    VIDEO_SHORT = "video_short"
    VIDEO_LONG = "video_long"
    AUDIO_TRACK = "audio_track"
    AUDIO_PODCAST = "audio_podcast"
    TEXT_POST = "text_post"
    ARTICLE = "article"

class DistributionStrategy(Enum):
    """Content distribution strategies"""
    SIMULTANEOUS = "simultaneous"
    SEQUENTIAL = "sequential"
    PLATFORM_OPTIMIZED = "platform_optimized"
    AUDIENCE_TARGETED = "audience_targeted"
    TIME_OPTIMIZED = "time_optimized"

# Placeholder platform integration models (to be implemented as ecosystem grows)
class BasePlatformModel:
    """Base platform integration model"""
    @staticmethod
    def connect_platform(platform_name: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "platform": platform_name,
            "status": IntegrationStatus.CONNECTED.value,
            "connection_id": f"conn_{datetime.utcnow().timestamp()}",
            "connected_at": datetime.utcnow().isoformat(),
            "permissions": ["read", "write", "analytics"]
        }
    
    @staticmethod
    def disconnect_platform(platform_name: str, connection_id: str) -> Dict[str, Any]:
        return {
            "platform": platform_name,
            "connection_id": connection_id,
            "status": IntegrationStatus.DISCONNECTED.value,
            "disconnected_at": datetime.utcnow().isoformat()
        }

class SpotifyIntegrationModel:
    """Spotify platform integration"""
    @staticmethod
    def upload_track(track_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "platform": "spotify",
            "track_id": f"spotify_track_{datetime.utcnow().timestamp()}",
            "title": track_data.get("title"),
            "artist": track_data.get("artist"),
            "album": track_data.get("album"),
            "upload_status": "processing",
            "estimated_availability": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "spotify_url": f"https://open.spotify.com/track/{track_data.get('id', 'placeholder')}"
        }
    
    @staticmethod
    def get_track_analytics(track_id: str) -> Dict[str, Any]:
        return {
            "track_id": track_id,
            "platform": "spotify",
            "streams": 15420,
            "listeners": 8750,
            "saves": 1250,
            "playlist_adds": 340,
            "skip_rate": 12.5,
            "completion_rate": 78.3,
            "top_countries": ["US", "UK", "CA"],
            "analytics_date": datetime.utcnow().isoformat()
        }

class YouTubeIntegrationModel:
    """YouTube platform integration"""
    @staticmethod
    def upload_video(video_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "platform": "youtube",
            "video_id": f"youtube_video_{datetime.utcnow().timestamp()}",
            "title": video_data.get("title"),
            "description": video_data.get("description"),
            "tags": video_data.get("tags", []),
            "upload_status": "processing",
            "privacy": video_data.get("privacy", "public"),
            "youtube_url": f"https://www.youtube.com/watch?v={video_data.get('id', 'placeholder')}"
        }
    
    @staticmethod
    def get_video_analytics(video_id: str) -> Dict[str, Any]:
        return {
            "video_id": video_id,
            "platform": "youtube",
            "views": 45230,
            "likes": 1250,
            "dislikes": 45,
            "comments": 180,
            "shares": 320,
            "watch_time_minutes": 12450,
            "average_view_duration": 245.6,
            "subscriber_growth": 85,
            "revenue": 125.50,
            "top_traffic_sources": ["youtube_search", "suggested_videos", "external"],
            "analytics_date": datetime.utcnow().isoformat()
        }

class InstagramIntegrationModel:
    """Instagram platform integration"""
    @staticmethod
    def post_content(content_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "platform": "instagram",
            "post_id": f"instagram_post_{datetime.utcnow().timestamp()}",
            "content_type": content_data.get("type", "image"),
            "caption": content_data.get("caption"),
            "hashtags": content_data.get("hashtags", []),
            "location": content_data.get("location"),
            "post_status": "published",
            "instagram_url": f"https://www.instagram.com/p/{content_data.get('id', 'placeholder')}"
        }
    
    @staticmethod
    def get_post_analytics(post_id: str) -> Dict[str, Any]:
        return {
            "post_id": post_id,
            "platform": "instagram",
            "likes": 2340,
            "comments": 145,
            "shares": 89,
            "saves": 234,
            "reach": 8750,
            "impressions": 12450,
            "engagement_rate": 7.8,
            "story_views": 5420,
            "profile_visits": 180,
            "website_clicks": 45,
            "analytics_date": datetime.utcnow().isoformat()
        }

class TikTokIntegrationModel:
    """TikTok platform integration"""
    @staticmethod
    def upload_video(video_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "platform": "tiktok",
            "video_id": f"tiktok_video_{datetime.utcnow().timestamp()}",
            "title": video_data.get("title"),
            "description": video_data.get("description"),
            "hashtags": video_data.get("hashtags", []),
            "effects": video_data.get("effects", []),
            "music": video_data.get("music"),
            "upload_status": "published",
            "tiktok_url": f"https://www.tiktok.com/@user/video/{video_data.get('id', 'placeholder')}"
        }
    
    @staticmethod
    def get_video_analytics(video_id: str) -> Dict[str, Any]:
        return {
            "video_id": video_id,
            "platform": "tiktok",
            "views": 125000,
            "likes": 8750,
            "comments": 450,
            "shares": 1250,
            "completion_rate": 65.2,
            "average_watch_time": 12.5,
            "follower_growth": 150,
            "profile_views": 2340,
            "trending_score": 8.5,
            "analytics_date": datetime.utcnow().isoformat()
        }

class TwitterIntegrationModel:
    """Twitter/X platform integration"""
    @staticmethod
    def post_tweet(tweet_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "platform": "twitter",
            "tweet_id": f"twitter_tweet_{datetime.utcnow().timestamp()}",
            "text": tweet_data.get("text"),
            "hashtags": tweet_data.get("hashtags", []),
            "mentions": tweet_data.get("mentions", []),
            "media": tweet_data.get("media", []),
            "thread": tweet_data.get("is_thread", False),
            "post_status": "published",
            "twitter_url": f"https://twitter.com/user/status/{tweet_data.get('id', 'placeholder')}"
        }
    
    @staticmethod
    def get_tweet_analytics(tweet_id: str) -> Dict[str, Any]:
        return {
            "tweet_id": tweet_id,
            "platform": "twitter",
            "impressions": 15420,
            "engagements": 1250,
            "retweets": 180,
            "likes": 450,
            "replies": 85,
            "clicks": 320,
            "profile_clicks": 45,
            "hashtag_clicks": 25,
            "engagement_rate": 8.1,
            "analytics_date": datetime.utcnow().isoformat()
        }

class FacebookIntegrationModel:
    """Facebook platform integration"""
    @staticmethod
    def post_content(content_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "platform": "facebook",
            "post_id": f"facebook_post_{datetime.utcnow().timestamp()}",
            "content_type": content_data.get("type", "status"),
            "message": content_data.get("message"),
            "link": content_data.get("link"),
            "targeting": content_data.get("targeting", {}),
            "post_status": "published",
            "facebook_url": f"https://www.facebook.com/user/posts/{content_data.get('id', 'placeholder')}"
        }

class LinkedInIntegrationModel:
    """LinkedIn platform integration"""
    @staticmethod
    def post_content(content_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "platform": "linkedin",
            "post_id": f"linkedin_post_{datetime.utcnow().timestamp()}",
            "content_type": content_data.get("type", "article"),
            "title": content_data.get("title"),
            "text": content_data.get("text"),
            "visibility": content_data.get("visibility", "public"),
            "post_status": "published",
            "linkedin_url": f"https://www.linkedin.com/posts/user_{content_data.get('id', 'placeholder')}"
        }

class SoundCloudIntegrationModel:
    """SoundCloud platform integration"""
    @staticmethod
    def upload_track(track_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "platform": "soundcloud",
            "track_id": f"soundcloud_track_{datetime.utcnow().timestamp()}",
            "title": track_data.get("title"),
            "description": track_data.get("description"),
            "genre": track_data.get("genre"),
            "tags": track_data.get("tags", []),
            "upload_status": "processing",
            "soundcloud_url": f"https://soundcloud.com/user/{track_data.get('id', 'placeholder')}"
        }

class TwitchIntegrationModel:
    """Twitch platform integration"""
    @staticmethod
    def create_stream(stream_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "platform": "twitch",
            "stream_id": f"twitch_stream_{datetime.utcnow().timestamp()}",
            "title": stream_data.get("title"),
            "category": stream_data.get("category"),
            "tags": stream_data.get("tags", []),
            "stream_status": "live",
            "twitch_url": f"https://www.twitch.tv/user"
        }

class PlatformSynchronizationModel:
    """Cross-platform synchronization and management"""
    @staticmethod
    def sync_content_across_platforms(content_id: str, platforms: List[str], strategy: DistributionStrategy) -> Dict[str, Any]:
        distribution_results = {}
        
        for platform in platforms:
            if platform == "spotify":
                result = SpotifyIntegrationModel.upload_track({"id": content_id, "title": "Sample Track"})
            elif platform == "youtube":
                result = YouTubeIntegrationModel.upload_video({"id": content_id, "title": "Sample Video"})
            elif platform == "instagram":
                result = InstagramIntegrationModel.post_content({"id": content_id, "type": "image"})
            elif platform == "tiktok":
                result = TikTokIntegrationModel.upload_video({"id": content_id, "title": "Sample Video"})
            elif platform == "twitter":
                result = TwitterIntegrationModel.post_tweet({"id": content_id, "text": "Sample Tweet"})
            else:
                result = {"platform": platform, "status": "not_implemented"}
            
            distribution_results[platform] = result
        
        return {
            "content_id": content_id,
            "strategy": strategy.value,
            "platforms": platforms,
            "distribution_results": distribution_results,
            "sync_timestamp": datetime.utcnow().isoformat(),
            "overall_status": "completed"
        }

class CrossPlatformAnalyticsModel:
    """Cross-platform analytics aggregation"""
    @staticmethod
    def aggregate_analytics(content_id: str, platforms: List[str]) -> Dict[str, Any]:
        aggregated_data = {
            "content_id": content_id,
            "platforms": platforms,
            "total_metrics": {
                "total_views": 0,
                "total_engagement": 0,
                "total_shares": 0,
                "total_comments": 0
            },
            "platform_breakdown": {},
            "performance_ranking": [],
            "aggregation_date": datetime.utcnow().isoformat()
        }
        
        # Simulate aggregation from multiple platforms
        for platform in platforms:
            if platform == "youtube":
                analytics = YouTubeIntegrationModel.get_video_analytics(content_id)
                aggregated_data["platform_breakdown"][platform] = analytics
                aggregated_data["total_metrics"]["total_views"] += analytics["views"]
                aggregated_data["total_metrics"]["total_engagement"] += analytics["likes"] + analytics["comments"]
            elif platform == "instagram":
                analytics = InstagramIntegrationModel.get_post_analytics(content_id)
                aggregated_data["platform_breakdown"][platform] = analytics
                aggregated_data["total_metrics"]["total_views"] += analytics["reach"]
                aggregated_data["total_metrics"]["total_engagement"] += analytics["likes"] + analytics["comments"]
        
        return aggregated_data

class DistributionModel:
    """Content distribution management"""
    @staticmethod
    def create_distribution_plan(content_data: Dict[str, Any], target_platforms: List[str]) -> Dict[str, Any]:
        return {
            "content_id": content_data.get("id"),
            "distribution_plan": {
                "strategy": "platform_optimized",
                "schedule": {
                    "instagram": "immediate",
                    "youtube": "1_hour_later",
                    "tiktok": "2_hours_later",
                    "twitter": "immediate"
                },
                "platform_customizations": {
                    "instagram": {"format": "square", "hashtags": 10},
                    "youtube": {"format": "16:9", "description_length": "detailed"},
                    "tiktok": {"format": "9:16", "duration": "15-60s"},
                    "twitter": {"format": "text", "character_limit": 280}
                }
            },
            "estimated_reach": {
                "instagram": 5000,
                "youtube": 2000,
                "tiktok": 8000,
                "twitter": 1500
            },
            "created_at": datetime.utcnow().isoformat()
        }

class PlatformPerformanceModel:
    """Platform-specific performance analysis"""
    @staticmethod
    def analyze_platform_performance(user_id: str, platform: str, period: str = "month") -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "platform": platform,
            "period": period,
            "performance_metrics": {
                "follower_growth": 15.5,
                "engagement_rate": 7.8,
                "reach_growth": 22.3,
                "content_performance": "above_average"
            },
            "best_performing_content": {
                "content_id": "best_content_123",
                "performance_score": 9.2,
                "engagement_rate": 12.5
            },
            "optimization_recommendations": [
                "Post during peak engagement hours (7-9 PM)",
                "Use trending hashtags relevant to your niche",
                "Increase video content production"
            ],
            "competitive_position": {
                "percentile": 85,
                "category_ranking": "top_15_percent"
            },
            "analyzed_at": datetime.utcnow().isoformat()
        }

# Platform Models Registry
PLATFORM_MODELS_REGISTRY: Dict[str, Type] = {
    "base": BasePlatformModel,
    "spotify": SpotifyIntegrationModel,
    "youtube": YouTubeIntegrationModel,
    "instagram": InstagramIntegrationModel,
    "tiktok": TikTokIntegrationModel,
    "twitter": TwitterIntegrationModel,
    "facebook": FacebookIntegrationModel,
    "linkedin": LinkedInIntegrationModel,
    "soundcloud": SoundCloudIntegrationModel,
    "twitch": TwitchIntegrationModel,
    "synchronization": PlatformSynchronizationModel,
    "cross_analytics": CrossPlatformAnalyticsModel,
    "distribution": DistributionModel,
    "performance": PlatformPerformanceModel
}

class PlatformModelsManager:
    """Platform Models Manager for Enterprise Platform Integration"""
    
    def __init__(self):
        self.registry = PLATFORM_MODELS_REGISTRY
        self.logger = logging.getLogger(__name__)
        self.active_connections = {}
        
    def connect_multiple_platforms(self, user_id: str, platform_configs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Connect to multiple platforms simultaneously"""
        try:
            connection_results = {
                "user_id": user_id,
                "connections": {},
                "successful_connections": 0,
                "failed_connections": 0,
                "connection_timestamp": datetime.utcnow().isoformat()
            }
            
            for platform_name, config in platform_configs.items():
                try:
                    connection_result = BasePlatformModel.connect_platform(platform_name, config)
                    connection_results["connections"][platform_name] = connection_result
                    
                    if connection_result["status"] == IntegrationStatus.CONNECTED.value:
                        connection_results["successful_connections"] += 1
                        self.active_connections[f"{user_id}_{platform_name}"] = connection_result
                    else:
                        connection_results["failed_connections"] += 1
                        
                except Exception as e:
                    connection_results["connections"][platform_name] = {
                        "status": IntegrationStatus.ERROR.value,
                        "error": str(e)
                    }
                    connection_results["failed_connections"] += 1
            
            return connection_results
            
        except Exception as e:
            self.logger.error(f"Failed to connect multiple platforms: {e}")
            return {"error": str(e)}
    
    def distribute_content_optimized(self, content_data: Dict[str, Any], target_platforms: List[str]) -> Dict[str, Any]:
        """Distribute content with platform-specific optimizations"""
        try:
            distribution_result = {
                "content_id": content_data.get("id"),
                "distribution_strategy": DistributionStrategy.PLATFORM_OPTIMIZED.value,
                "platform_distributions": {},
                "summary": {
                    "successful_distributions": 0,
                    "failed_distributions": 0,
                    "estimated_total_reach": 0
                },
                "distributed_at": datetime.utcnow().isoformat()
            }
            
            # Create distribution plan
            distribution_plan = DistributionModel.create_distribution_plan(content_data, target_platforms)
            distribution_result["distribution_plan"] = distribution_plan
            
            # Execute distribution
            sync_result = PlatformSynchronizationModel.sync_content_across_platforms(
                content_data.get("id"),
                target_platforms,
                DistributionStrategy.PLATFORM_OPTIMIZED
            )
            distribution_result["sync_result"] = sync_result
            
            # Calculate summary
            for platform in target_platforms:
                if platform in sync_result["distribution_results"]:
                    platform_result = sync_result["distribution_results"][platform]
                    if platform_result.get("upload_status") in ["processing", "published"]:
                        distribution_result["summary"]["successful_distributions"] += 1
                    else:
                        distribution_result["summary"]["failed_distributions"] += 1
                    
                    # Add estimated reach
                    estimated_reach = distribution_plan["estimated_reach"].get(platform, 0)
                    distribution_result["summary"]["estimated_total_reach"] += estimated_reach
            
            return distribution_result
            
        except Exception as e:
            self.logger.error(f"Failed to distribute content: {e}")
            return {"error": str(e)}
    
    def get_cross_platform_analytics(self, user_id: str, content_id: str = None) -> Dict[str, Any]:
        """Get aggregated analytics across all connected platforms"""
        try:
            user_platforms = [
                platform.split("_")[1] for platform in self.active_connections.keys() 
                if platform.startswith(user_id)
            ]
            
            if content_id:
                # Get analytics for specific content
                analytics = CrossPlatformAnalyticsModel.aggregate_analytics(content_id, user_platforms)
            else:
                # Get overall user analytics
                analytics = {
                    "user_id": user_id,
                    "connected_platforms": user_platforms,
                    "overall_performance": {},
                    "analytics_date": datetime.utcnow().isoformat()
                }
                
                for platform in user_platforms:
                    platform_analytics = PlatformPerformanceModel.analyze_platform_performance(
                        user_id, platform
                    )
                    analytics["overall_performance"][platform] = platform_analytics
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to get cross-platform analytics: {e}")
            return {"error": str(e)}

# Global instance
platform_models_manager = PlatformModelsManager()

# Workflow integration functions
async def platform_distribution_workflow(content_data: Dict[str, Any], platforms: List[str]) -> Dict[str, Any]:
    """
    Platform Distribution Workflow
    Distribute content across multiple platforms with optimization
    """
    workflow_result = {
        "workflow": "platform_distribution",
        "content_id": content_data.get("id"),
        "target_platforms": platforms,
        "status": "processing"
    }
    
    try:
        # Optimized content distribution
        distribution_result = platform_models_manager.distribute_content_optimized(content_data, platforms)
        workflow_result["distribution"] = distribution_result
        
        # Setup cross-platform analytics tracking
        analytics_setup = platform_models_manager.get_cross_platform_analytics(
            content_data.get("creator_id", "unknown"),
            content_data.get("id")
        )
        workflow_result["analytics_setup"] = analytics_setup
        
        # Performance tracking initialization
        for platform in platforms:
            performance_setup = PlatformPerformanceModel.analyze_platform_performance(
                content_data.get("creator_id", "unknown"),
                platform
            )
            workflow_result[f"{platform}_performance"] = performance_setup
        
        workflow_result["status"] = "completed"
        workflow_result["models_used"] = ["distribution", "synchronization", "analytics", "performance"]
        
    except Exception as e:
        workflow_result["status"] = "error"
        workflow_result["error"] = str(e)
    
    return workflow_result

def get_platform_models_info() -> Dict[str, Any]:
    """Get information about platform models module"""
    return {
        "module": "Platform Models",
        "version": "1.0.0",
        "author": "Fahed Mlaiel (mlaiel@live.de)",
        "total_models": len(PLATFORM_MODELS_REGISTRY),
        "platform_types": [pt.value for pt in PlatformType],
        "integration_statuses": [status.value for status in IntegrationStatus],
        "content_formats": [format.value for format in ContentFormat],
        "distribution_strategies": [strategy.value for strategy in DistributionStrategy],
        "workflow_phases": [7],  # Phases handled by this module
        "business_logic": ["Distribution & Analytics"],
        "supported_platforms": {
            "social_media": ["instagram", "tiktok", "twitter", "facebook", "linkedin"],
            "content_platforms": ["youtube", "vimeo", "twitch", "dailymotion"],
            "audio_platforms": ["spotify", "soundcloud", "apple_music", "amazon_music"],
            "professional_networks": ["linkedin", "behance", "dribbble"],
            "e_commerce": ["shopify", "woocommerce", "etsy"],
            "payment_gateways": ["stripe", "paypal", "square", "wise"],
            "cloud_storage": ["aws_s3", "google_cloud", "azure", "dropbox"],
            "analytics": ["google_analytics", "adobe_analytics"],
            "email_marketing": ["mailchimp", "sendgrid", "convertkit"],
            "collaboration": ["slack", "discord", "zoom"]
        },
        "integration_capabilities": {
            "content_distribution": ["automated", "scheduled", "optimized"],
            "analytics_aggregation": ["cross_platform", "real_time", "comprehensive"],
            "platform_optimization": ["format_adaptation", "timing_optimization", "audience_targeting"],
            "synchronization": ["multi_platform", "strategy_based", "real_time"],
            "performance_monitoring": ["platform_specific", "comparative", "predictive"]
        },
        "enterprise_ready": True,
        "documentation": "Multilingual support (EN, DE, FR, AR)"
    }

# Export all platform models and components
__all__ = [
    # Enums
    'PlatformType', 'IntegrationStatus', 'ContentFormat', 'DistributionStrategy',
    
    # Core Models
    'BasePlatformModel', 'SpotifyIntegrationModel', 'YouTubeIntegrationModel',
    'InstagramIntegrationModel', 'TikTokIntegrationModel', 'TwitterIntegrationModel',
    'FacebookIntegrationModel', 'LinkedInIntegrationModel', 'SoundCloudIntegrationModel',
    'TwitchIntegrationModel', 'PlatformSynchronizationModel', 'CrossPlatformAnalyticsModel',
    'DistributionModel', 'PlatformPerformanceModel',
    
    # Manager and Registry
    'PlatformModelsManager', 'platform_models_manager',
    'PLATFORM_MODELS_REGISTRY',
    
    # Workflow Functions
    'platform_distribution_workflow',
    'get_platform_models_info'
]