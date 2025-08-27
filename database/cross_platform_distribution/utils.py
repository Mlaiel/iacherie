"""
Utilities and Examples for Cross-Platform Distribution System

Provides utility functions, example implementations, and helper methods
for the cross-platform distribution system.

Author: Fahed Mlaiel (mlaiel@live.de)
Development Team: Lead AI Developer, Senior Backend Engineer, ML Engineer, DBA, Security Expert
Architecture: Enterprise-grade, microservices-ready, production-optimized

⚠️ INTELLECTUAL PROPERTY WARNING ⚠️
This code is the exclusive property of Fahed Mlaiel (mlaiel@live.de).
Any unauthorized use, copying, or distribution is STRICTLY PROHIBITED.
Violations will be prosecuted under international copyright law.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .index import CrossPlatformDistributionSystem, create_distribution_system
from .config import get_config, Environment
from .platform_adapters import PlatformCredentials, AuthenticationType
from .content_optimizer import OptimizationType, ContentType
from .scheduling_engine import SchedulingStrategy, AudienceSegment

logger = logging.getLogger(__name__)

class DistributionSystemExamples:
    """
    Example implementations and utility functions for the distribution system
    """
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.system = create_distribution_system(db_session)
        self.config = get_config()
        self.logger = logging.getLogger(__name__)
    
    async def example_music_release_campaign(
        self,
        user_id: int,
        track_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Example: Complete music release campaign
        
        Args:
            user_id: User identifier
            track_data: Track information
            
        Returns:
            Campaign results
        """
        
        self.logger.info("Creating example music release campaign")
        
        # Configure campaign for music release
        campaign_config = {
            "name": f"Release Campaign: {track_data.get('title', 'Unknown Track')}",
            "platforms": ["spotify", "youtube", "instagram", "tiktok"],
            "content_format": "audio",
            "content_type": "music_track",
            "title": track_data.get("title", ""),
            "description": track_data.get("description", ""),
            "optimization_goals": [
                OptimizationType.SEO_KEYWORDS,
                OptimizationType.HASHTAGS,
                OptimizationType.ENGAGEMENT_PREDICTION,
                OptimizationType.PLATFORM_ADAPTATION
            ],
            "scheduling_strategy": SchedulingStrategy.MAXIMUM_ENGAGEMENT,
            "target_audience": "global",
            "auto_optimize": True,
            "enable_scheduling": True,
            "date_range": (
                datetime.utcnow() + timedelta(hours=1),
                datetime.utcnow() + timedelta(days=7)
            )
        }
        
        try:
            # Create and execute campaign
            result = await self.system.create_distribution_campaign(
                user_id=user_id,
                content_id=track_data.get("id", 1),
                campaign_config=campaign_config
            )
            
            # Wait a moment and check status
            await asyncio.sleep(2)
            
            if result.get("success"):
                status = await self.system.get_campaign_status(
                    result["campaign_id"]
                )
                result["status_check"] = status
            
            return result
            
        except Exception as e:
            self.logger.error(f"Music release campaign failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def example_social_media_post(
        self,
        user_id: int,
        post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Example: Social media post distribution
        
        Args:
            user_id: User identifier
            post_data: Post content data
            
        Returns:
            Distribution results
        """
        
        self.logger.info("Creating example social media post campaign")
        
        campaign_config = {
            "name": f"Social Post: {post_data.get('title', 'Social Content')}",
            "platforms": ["instagram", "twitter", "facebook", "linkedin"],
            "content_format": "image",
            "content_type": "social_post",
            "title": post_data.get("title", ""),
            "description": post_data.get("caption", ""),
            "optimization_goals": [
                OptimizationType.HASHTAGS,
                OptimizationType.ENGAGEMENT_PREDICTION,
                OptimizationType.TIMING_OPTIMIZATION
            ],
            "scheduling_strategy": SchedulingStrategy.MAXIMUM_REACH,
            "target_audience": post_data.get("target_audience", "global"),
            "auto_optimize": True
        }
        
        try:
            return await self.system.create_distribution_campaign(
                user_id=user_id,
                content_id=post_data.get("id", 2),
                campaign_config=campaign_config
            )
            
        except Exception as e:
            self.logger.error(f"Social media campaign failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def example_video_content_distribution(
        self,
        user_id: int,
        video_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Example: Video content distribution
        
        Args:
            user_id: User identifier
            video_data: Video content data
            
        Returns:
            Distribution results
        """
        
        self.logger.info("Creating example video distribution campaign")
        
        campaign_config = {
            "name": f"Video Campaign: {video_data.get('title', 'Video Content')}",
            "platforms": ["youtube", "tiktok", "instagram_reels", "twitch"],
            "content_format": "video",
            "content_type": "video_content",
            "title": video_data.get("title", ""),
            "description": video_data.get("description", ""),
            "optimization_goals": [
                OptimizationType.SEO_KEYWORDS,
                OptimizationType.TITLE_OPTIMIZATION,
                OptimizationType.DESCRIPTION_OPTIMIZATION,
                OptimizationType.THUMBNAIL_OPTIMIZATION
            ],
            "scheduling_strategy": SchedulingStrategy.BALANCED_DISTRIBUTION,
            "target_audience": video_data.get("target_audience", "global"),
            "auto_optimize": True
        }
        
        try:
            return await self.system.create_distribution_campaign(
                user_id=user_id,
                content_id=video_data.get("id", 3),
                campaign_config=campaign_config
            )
            
        except Exception as e:
            self.logger.error(f"Video distribution campaign failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def example_podcast_episode_distribution(
        self,
        user_id: int,
        episode_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Example: Podcast episode distribution
        
        Args:
            user_id: User identifier
            episode_data: Episode data
            
        Returns:
            Distribution results
        """
        
        self.logger.info("Creating example podcast distribution campaign")
        
        campaign_config = {
            "name": f"Podcast Episode: {episode_data.get('title', 'Episode')}",
            "platforms": ["spotify", "youtube", "apple_music", "soundcloud"],
            "content_format": "audio",
            "content_type": "podcast_episode",
            "title": episode_data.get("title", ""),
            "description": episode_data.get("description", ""),
            "optimization_goals": [
                OptimizationType.SEO_KEYWORDS,
                OptimizationType.DESCRIPTION_OPTIMIZATION,
                OptimizationType.AUDIENCE_TARGETING
            ],
            "scheduling_strategy": SchedulingStrategy.TIMEZONE_OPTIMIZATION,
            "target_audience": episode_data.get("target_audience", "global"),
            "auto_optimize": True
        }
        
        try:
            return await self.system.create_distribution_campaign(
                user_id=user_id,
                content_id=episode_data.get("id", 4),
                campaign_config=campaign_config
            )
            
        except Exception as e:
            self.logger.error(f"Podcast distribution campaign failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def create_example_platform_credentials(self) -> Dict[str, PlatformCredentials]:
        """
        Create example platform credentials for testing
        
        Returns:
            Dictionary of platform credentials
        """
        
        credentials = {}
        
        # YouTube credentials example
        credentials["youtube"] = PlatformCredentials(
            platform_name="youtube",
            auth_type=AuthenticationType.OAUTH2,
            client_id="example_youtube_client_id",
            client_secret="example_youtube_client_secret",
            access_token="example_youtube_access_token"
        )
        
        # Spotify credentials example
        credentials["spotify"] = PlatformCredentials(
            platform_name="spotify",
            auth_type=AuthenticationType.OAUTH2,
            client_id="example_spotify_client_id",
            client_secret="example_spotify_client_secret"
        )
        
        # Instagram credentials example
        credentials["instagram"] = PlatformCredentials(
            platform_name="instagram",
            auth_type=AuthenticationType.ACCESS_TOKEN,
            access_token="example_instagram_access_token"
        )
        
        # Twitter credentials example
        credentials["twitter"] = PlatformCredentials(
            platform_name="twitter",
            auth_type=AuthenticationType.OAUTH2,
            client_id="example_twitter_api_key",
            client_secret="example_twitter_api_secret",
            access_token="example_twitter_access_token"
        )
        
        return credentials
    
    async def test_platform_connectivity(self) -> Dict[str, Any]:
        """
        Test connectivity to all configured platforms
        
        Returns:
            Platform connectivity test results
        """
        
        self.logger.info("Testing platform connectivity")
        
        results = {
            "total_platforms": 0,
            "connected": 0,
            "failed": 0,
            "platform_status": {},
            "test_timestamp": datetime.utcnow().isoformat()
        }
        
        # Get example credentials
        credentials = self.create_example_platform_credentials()
        
        for platform_name, creds in credentials.items():
            results["total_platforms"] += 1
            
            try:
                # Test platform connection
                is_valid = await self.system.validate_platform_credentials(
                    platform_name, 
                    creds
                )
                
                if is_valid:
                    results["connected"] += 1
                    results["platform_status"][platform_name] = "connected"
                else:
                    results["failed"] += 1
                    results["platform_status"][platform_name] = "authentication_failed"
                    
            except Exception as e:
                results["failed"] += 1
                results["platform_status"][platform_name] = f"error: {str(e)}"
        
        return results
    
    def get_example_content_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Get example content data for different content types
        
        Returns:
            Dictionary of example content data
        """
        
        return {
            "music_track": {
                "id": 1,
                "title": "New Summer Hit 2025",
                "description": "An amazing new track perfect for summer vibes. Features upbeat melody and catchy lyrics.",
                "genre": "Pop",
                "duration": 210,  # seconds
                "artist": "Example Artist",
                "album": "Summer Collection",
                "tags": ["summer", "pop", "upbeat", "new music"],
                "target_audience": "global"
            },
            "video_content": {
                "id": 2,
                "title": "Behind the Scenes: Recording Studio",
                "description": "Take a look behind the scenes as we record our latest album in the studio.",
                "duration": 600,  # seconds
                "category": "Music",
                "tags": ["behind the scenes", "studio", "recording", "music"],
                "target_audience": "north_america"
            },
            "social_post": {
                "id": 3,
                "title": "New Music Announcement",
                "caption": "Excited to announce our new single dropping next week! 🎵 #NewMusic #ComingSoon",
                "image_url": "https://example.com/announcement.jpg",
                "tags": ["announcement", "new music", "single"],
                "target_audience": "global"
            },
            "podcast_episode": {
                "id": 4,
                "title": "The Creative Process: Episode 15",
                "description": "In this episode, we dive deep into the creative process behind songwriting and music production.",
                "duration": 2700,  # seconds (45 minutes)
                "episode_number": 15,
                "season": 1,
                "tags": ["creativity", "songwriting", "music production", "interview"],
                "target_audience": "global"
            }
        }
    
    async def run_comprehensive_example(self) -> Dict[str, Any]:
        """
        Run comprehensive example showcasing all system capabilities
        
        Returns:
            Comprehensive test results
        """
        
        self.logger.info("Running comprehensive distribution system example")
        
        results = {
            "system_health": self.system.get_system_health(),
            "platform_tests": await self.test_platform_connectivity(),
            "campaigns": {},
            "analytics": {},
            "optimization_examples": {},
            "execution_time": None
        }
        
        start_time = datetime.utcnow()
        
        try:
            # Get example content
            content_examples = self.get_example_content_data()
            
            # Test different campaign types
            for content_type, content_data in content_examples.items():
                campaign_name = f"{content_type}_campaign"
                
                if content_type == "music_track":
                    campaign_result = await self.example_music_release_campaign(1, content_data)
                elif content_type == "video_content":
                    campaign_result = await self.example_video_content_distribution(1, content_data)
                elif content_type == "social_post":
                    campaign_result = await self.example_social_media_post(1, content_data)
                elif content_type == "podcast_episode":
                    campaign_result = await self.example_podcast_episode_distribution(1, content_data)
                else:
                    continue
                
                results["campaigns"][campaign_name] = campaign_result
                
                # Generate analytics report if campaign was successful
                if campaign_result.get("success"):
                    try:
                        analytics_report = await self.system.generate_performance_report(
                            str(content_data["id"]),
                            ["youtube", "instagram", "spotify"],
                            "daily"
                        )
                        
                        results["analytics"][campaign_name] = {
                            "report_id": analytics_report.report_id,
                            "platforms": analytics_report.platforms,
                            "summary": analytics_report.summary_statistics,
                            "insights": analytics_report.performance_insights[:3],  # Top 3 insights
                            "recommendations": analytics_report.recommendations[:3]  # Top 3 recommendations
                        }
                    except Exception as e:
                        results["analytics"][campaign_name] = {"error": str(e)}
                
                # Test content optimization
                try:
                    optimization_result = await self.system.optimize_content_for_platforms(
                        content_data,
                        ["youtube", "instagram", "tiktok"]
                    )
                    
                    results["optimization_examples"][campaign_name] = {
                        "success": optimization_result.success,
                        "seo_score": optimization_result.seo_score,
                        "platform_count": len(optimization_result.platform_optimizations),
                        "engagement_predictions": optimization_result.engagement_prediction,
                        "recommendations_count": len(optimization_result.recommendations)
                    }
                except Exception as e:
                    results["optimization_examples"][campaign_name] = {"error": str(e)}
            
            # Calculate execution time
            end_time = datetime.utcnow()
            results["execution_time"] = (end_time - start_time).total_seconds()
            
            self.logger.info("Comprehensive example completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Comprehensive example failed: {str(e)}")
            results["error"] = str(e)
            return results

# Utility functions for quick testing
async def quick_test_distribution_system(db_session=None) -> Dict[str, Any]:
    """
    Quick test of the distribution system
    
    Args:
        db_session: Database session
        
    Returns:
        Test results
    """
    
    examples = DistributionSystemExamples(db_session)
    
    # Run a simple music release campaign test
    test_track = {
        "id": 999,
        "title": "Quick Test Track",
        "description": "A test track for system validation",
        "genre": "Electronic",
        "artist": "Test Artist"
    }
    
    return await examples.example_music_release_campaign(1, test_track)

async def test_content_optimization(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test content optimization for given content
    
    Args:
        content_data: Content to optimize
        
    Returns:
        Optimization results
    """
    
    system = create_distribution_system()
    
    return await system.optimize_content_for_platforms(
        content_data,
        ["youtube", "instagram", "tiktok", "spotify"]
    )

def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information
    
    Returns:
        System information and capabilities
    """
    
    system = create_distribution_system()
    config = get_config()
    
    return {
        "system_health": system.get_system_health(),
        "configuration": config.to_dict(),
        "supported_platforms": system.get_supported_platforms(),
        "version": "1.0.0",
        "author": "Fahed Mlaiel (mlaiel@live.de)",
        "capabilities": {
            "content_optimization": True,
            "intelligent_scheduling": True,
            "multi_platform_distribution": True,
            "real_time_analytics": True,
            "ai_powered_insights": True,
            "automated_workflows": True
        }
    }

# Export all utility functions and classes
__all__ = [
    "DistributionSystemExamples",
    "quick_test_distribution_system",
    "test_content_optimization",
    "get_system_info"
]
