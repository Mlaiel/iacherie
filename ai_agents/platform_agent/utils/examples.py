"""
Platform Agent Usage Examples - Comprehensive Implementation Guide

Example implementations showing how to use all Platform Agent components
with real-world scenarios and enterprise patterns.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Import Platform Agent components
from . import (
    PlatformAgent,
    PlatformAgentManager,
    PlatformType,
    ContentType,
    OptimizationLevel,
    get_config,
    get_platform_credentials
)


class PlatformAgentExamples:
    """Comprehensive examples for Platform Agent usage"""
    
    def __init__(self):
        self.platform_agent = None
        self.manager = None
    
    async def example_1_basic_setup(self):
        """Example 1: Basic Platform Agent setup and initialization"""
        
        print("=== Example 1: Basic Setup ===")
        
        # Initialize Platform Agent Manager
        self.manager = PlatformAgentManager()
        
        # Initialize Platform Agent with multiple platforms
        platforms = [
            PlatformType.SPOTIFY,
            PlatformType.YOUTUBE,
            PlatformType.INSTAGRAM,
            PlatformType.TIKTOK
        ]
        
        self.platform_agent = await self.manager.create_agent(
            agent_id="influencer_001",
            platforms=platforms,
            config={
                "enable_ai_optimization": True,
                "enable_real_time_sync": True,
                "optimization_level": OptimizationLevel.ADVANCED
            }
        )
        
        print(f"✅ Platform Agent created with {len(platforms)} platforms")
        
        # Check platform connections
        for platform in platforms:
            health = await self.platform_agent.check_platform_health(platform)
            print(f"📊 {platform.value}: {health.status} ({health.response_time}ms)")
    
    async def example_2_content_upload(self):
        """Example 2: Upload and distribute content across platforms"""
        
        print("\n=== Example 2: Content Upload & Distribution ===")
        
        # Content metadata
        content_metadata = {
            "title": "Amazing AI-Generated Music Track",
            "description": "A beautiful composition created with advanced AI algorithms",
            "tags": ["ai", "music", "electronic", "instrumental"],
            "category": "Music",
            "privacy": "public",
            "language": "en",
            "location": "Berlin, Germany",
            "copyright_notice": "© 2025 AI Music Lab"
        }
        
        # Example file path (would be real file in production)
        file_path = "/path/to/music_track.mp3"
        
        try:
            # Distribute content across all connected platforms
            results = await self.platform_agent.distribute_content(
                file_path=file_path,
                content_type=ContentType.AUDIO,
                metadata=content_metadata,
                platforms=[PlatformType.SPOTIFY, PlatformType.YOUTUBE],
                optimization_level=OptimizationLevel.ADVANCED,
                schedule_time=None  # Publish immediately
            )
            
            # Process results
            for platform, result in results.items():
                if result.success:
                    print(f"✅ {platform}: Published successfully - {result.platform_url}")
                else:
                    print(f"❌ {platform}: Failed - {result.error_message}")
                    
        except Exception as e:
            print(f"❌ Distribution failed: {str(e)}")
    
    async def example_3_ai_optimization(self):
        """Example 3: AI-powered content optimization"""
        
        print("\n=== Example 3: AI Content Optimization ===")
        
        file_path = "/path/to/raw_video.mp4"
        
        try:
            # Optimize content for different platforms
            optimization_results = await self.platform_agent.optimize_content(
                file_path=file_path,
                content_type=ContentType.VIDEO,
                target_platforms=[
                    PlatformType.YOUTUBE,
                    PlatformType.INSTAGRAM,
                    PlatformType.TIKTOK
                ],
                optimization_settings={
                    "enhance_quality": True,
                    "auto_crop": True,
                    "noise_reduction": True,
                    "color_correction": True,
                    "compression_level": "optimal"
                }
            )
            
            for platform, result in optimization_results.items():
                print(f"🎨 {platform}:")
                print(f"   Quality Score: {result.quality_score}")
                print(f"   File Size: {result.optimized_size_mb:.1f} MB")
                print(f"   Processing Time: {result.processing_time:.2f}s")
                
        except Exception as e:
            print(f"❌ Optimization failed: {str(e)}")
    
    async def example_4_real_time_sync(self):
        """Example 4: Real-time synchronization across platforms"""
        
        print("\n=== Example 4: Real-time Synchronization ===")
        
        # Enable real-time sync for specific content
        content_id = "content_12345"
        
        try:
            # Start synchronization
            sync_result = await self.platform_agent.start_real_time_sync(
                content_id=content_id,
                platforms=[
                    PlatformType.INSTAGRAM,
                    PlatformType.FACEBOOK,
                    PlatformType.TWITTER
                ],
                sync_settings={
                    "sync_metrics": True,
                    "sync_comments": True,
                    "sync_engagement": True,
                    "conflict_resolution": "latest_wins"
                }
            )
            
            print(f"🔄 Sync started for {len(sync_result.platforms)} platforms")
            
            # Monitor sync status
            for i in range(5):  # Monitor for 5 cycles
                await asyncio.sleep(10)  # Wait 10 seconds
                
                status = await self.platform_agent.get_sync_status(content_id)
                print(f"📊 Sync Status #{i+1}:")
                for platform, platform_status in status.platforms.items():
                    print(f"   {platform}: {platform_status.status} - {platform_status.last_sync}")
                    
        except Exception as e:
            print(f"❌ Sync failed: {str(e)}")
    
    async def example_5_collaboration_matching(self):
        """Example 5: AI-powered collaboration matching"""
        
        print("\n=== Example 5: Collaboration Matching ===")
        
        try:
            # Find collaboration opportunities
            matches = await self.platform_agent.find_collaboration_matches(
                criteria={
                    "genre": ["electronic", "ambient", "experimental"],
                    "follower_range": (10000, 100000),
                    "engagement_rate_min": 3.0,
                    "location": ["Europe", "North America"],
                    "collaboration_types": ["remix", "feature", "co-production"]
                },
                limit=10
            )
            
            print(f"🤝 Found {len(matches)} potential collaborations:")
            
            for match in matches[:3]:  # Show top 3
                print(f"   👤 {match.artist_name} ({match.platform})")
                print(f"      Followers: {match.follower_count:,}")
                print(f"      Compatibility: {match.compatibility_score:.1f}%")
                print(f"      Suggested Type: {match.collaboration_type}")
                print()
                
        except Exception as e:
            print(f"❌ Collaboration matching failed: {str(e)}")
    
    async def example_6_analytics_and_insights(self):
        """Example 6: Advanced analytics and insights"""
        
        print("\n=== Example 6: Analytics & Insights ===")
        
        try:
            # Get comprehensive analytics
            analytics = await self.platform_agent.get_analytics(
                time_range="last_30_days",
                platforms=[PlatformType.SPOTIFY, PlatformType.YOUTUBE, PlatformType.INSTAGRAM],
                metrics=[
                    "views", "likes", "shares", "comments",
                    "engagement_rate", "reach", "revenue"
                ]
            )
            
            print("📊 Platform Performance:")
            for platform, metrics in analytics.platform_metrics.items():
                print(f"   {platform}:")
                print(f"      Views: {metrics.views:,}")
                print(f"      Engagement Rate: {metrics.engagement_rate:.2f}%")
                print(f"      Revenue: ${metrics.revenue:.2f}")
            
            # AI Insights
            insights = await self.platform_agent.get_ai_insights(analytics)
            print(f"\n🧠 AI Insights:")
            for insight in insights[:3]:  # Top 3 insights
                print(f"   • {insight.title}")
                print(f"     {insight.description}")
                print(f"     Confidence: {insight.confidence:.1f}%")
                
        except Exception as e:
            print(f"❌ Analytics failed: {str(e)}")
    
    async def example_7_automated_workflow(self):
        """Example 7: Automated content workflow"""
        
        print("\n=== Example 7: Automated Workflow ===")
        
        try:
            # Create automated workflow
            workflow_config = {
                "name": "Daily Music Upload",
                "schedule": "0 9 * * *",  # Daily at 9 AM
                "steps": [
                    {
                        "type": "content_scan",
                        "source_folder": "/content/ready_to_publish/"
                    },
                    {
                        "type": "ai_optimization",
                        "settings": {
                            "enhancement_level": "high",
                            "target_platforms": ["spotify", "youtube"]
                        }
                    },
                    {
                        "type": "metadata_generation",
                        "ai_generated": True,
                        "include_seo": True
                    },
                    {
                        "type": "distribution",
                        "platforms": ["spotify", "youtube", "instagram"],
                        "stagger_timing": 300  # 5 minutes between platforms
                    },
                    {
                        "type": "monitoring",
                        "duration": 24 * 3600,  # 24 hours
                        "alert_thresholds": {
                            "low_engagement": 1.0,
                            "error_rate": 5.0
                        }
                    }
                ]
            }
            
            workflow_id = await self.platform_agent.create_workflow(workflow_config)
            print(f"⚡ Automated workflow created: {workflow_id}")
            
            # Monitor workflow execution
            status = await self.platform_agent.get_workflow_status(workflow_id)
            print(f"📋 Workflow Status: {status.state}")
            print(f"📅 Next Run: {status.next_execution}")
            
        except Exception as e:
            print(f"❌ Workflow creation failed: {str(e)}")
    
    async def example_8_error_handling(self):
        """Example 8: Comprehensive error handling"""
        
        print("\n=== Example 8: Error Handling ===")
        
        from .exceptions import (
            PlatformConnectionException,
            ContentValidationException,
            RateLimitException
        )
        
        try:
            # Simulate operation that might fail
            result = await self.platform_agent.distribute_content(
                file_path="/nonexistent/file.mp3",
                content_type=ContentType.AUDIO,
                metadata={"title": "Test"},
                platforms=[PlatformType.SPOTIFY]
            )
            
        except PlatformConnectionException as e:
            print(f"🔌 Connection Error: {e.user_message}")
            print(f"   Platform: {e.platform}")
            print(f"   Retry after: {e.retry_after}s")
            
        except ContentValidationException as e:
            print(f"📝 Validation Error: {e.user_message}")
            print(f"   Errors: {', '.join(e.validation_errors)}")
            
        except RateLimitException as e:
            print(f"⏰ Rate Limit: {e.user_message}")
            print(f"   Platform: {e.platform}")
            print(f"   Retry after: {e.retry_after}s")
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
    
    async def example_9_configuration_management(self):
        """Example 9: Configuration management"""
        
        print("\n=== Example 9: Configuration Management ===")
        
        # Get current configuration
        config = get_config()
        
        print(f"🔧 Current Environment: {config.environment.value}")
        print(f"🔧 Debug Mode: {config.debug}")
        print(f"🔧 AI Optimization: {config.ai.enable_ai_optimization}")
        print(f"🔧 Max Concurrent Uploads: {config.max_concurrent_uploads}")
        
        # Validate configuration
        from .config import config_manager
        
        validation_errors = config_manager.validate_config()
        
        if validation_errors['critical']:
            print("🚨 Critical Configuration Issues:")
            for error in validation_errors['critical']:
                print(f"   • {error}")
        
        if validation_errors['warning']:
            print("⚠️  Configuration Warnings:")
            for warning in validation_errors['warning']:
                print(f"   • {warning}")
        
        if not validation_errors['critical'] and not validation_errors['warning']:
            print("✅ Configuration is valid")
    
    async def example_10_monitoring_and_alerts(self):
        """Example 10: Monitoring and alerting"""
        
        print("\n=== Example 10: Monitoring & Alerts ===")
        
        try:
            # Set up monitoring
            monitoring_config = {
                "metrics": [
                    "upload_success_rate",
                    "api_response_time",
                    "engagement_rate",
                    "error_rate"
                ],
                "thresholds": {
                    "upload_success_rate_min": 95.0,
                    "api_response_time_max": 2000,  # ms
                    "error_rate_max": 5.0
                },
                "notification_channels": [
                    "email", "slack", "webhook"
                ],
                "check_interval": 300  # 5 minutes
            }
            
            monitor_id = await self.platform_agent.setup_monitoring(monitoring_config)
            print(f"📊 Monitoring setup complete: {monitor_id}")
            
            # Get current metrics
            metrics = await self.platform_agent.get_current_metrics()
            
            print("📈 Current Metrics:")
            print(f"   Upload Success Rate: {metrics.upload_success_rate:.1f}%")
            print(f"   Avg Response Time: {metrics.avg_response_time:.0f}ms")
            print(f"   Error Rate: {metrics.error_rate:.2f}%")
            print(f"   Active Connections: {metrics.active_connections}")
            
        except Exception as e:
            print(f"❌ Monitoring setup failed: {str(e)}")


# Main execution function
async def run_all_examples():
    """Run all platform agent examples"""
    
    print("🚀 Platform Agent Examples - Comprehensive Demo")
    print("=" * 60)
    
    examples = PlatformAgentExamples()
    
    # List of all examples
    example_methods = [
        examples.example_1_basic_setup,
        examples.example_2_content_upload,
        examples.example_3_ai_optimization,
        examples.example_4_real_time_sync,
        examples.example_5_collaboration_matching,
        examples.example_6_analytics_and_insights,
        examples.example_7_automated_workflow,
        examples.example_8_error_handling,
        examples.example_9_configuration_management,
        examples.example_10_monitoring_and_alerts
    ]
    
    # Run examples with error handling
    for i, example_method in enumerate(example_methods, 1):
        try:
            await example_method()
            print(f"\n✅ Example {i} completed successfully")
        except Exception as e:
            print(f"\n❌ Example {i} failed: {str(e)}")
        
        if i < len(example_methods):
            print("\n" + "-" * 40)
            await asyncio.sleep(1)  # Brief pause between examples
    
    print("\n🎉 All examples completed!")
    print("📚 For more information, check the documentation in README files")


# Quick start function
async def quick_start_example():
    """Quick start example for new users"""
    
    print("🚀 Platform Agent - Quick Start")
    print("=" * 40)
    
    try:
        # 1. Initialize manager
        manager = PlatformAgentManager()
        
        # 2. Create agent
        agent = await manager.create_agent(
            agent_id="quickstart_demo",
            platforms=[PlatformType.SPOTIFY, PlatformType.YOUTUBE]
        )
        
        print("✅ Platform Agent initialized")
        
        # 3. Check platform health
        for platform in [PlatformType.SPOTIFY, PlatformType.YOUTUBE]:
            health = await agent.check_platform_health(platform)
            print(f"📊 {platform.value}: {health.status}")
        
        # 4. Show available features
        features = await agent.get_available_features()
        print(f"🎯 Available Features: {len(features)} total")
        for feature in features[:5]:  # Show first 5
            print(f"   • {feature}")
        
        print("\n🎉 Quick start completed successfully!")
        print("💡 Run run_all_examples() for comprehensive demonstrations")
        
    except Exception as e:
        print(f"❌ Quick start failed: {str(e)}")
        print("💡 Check your configuration and platform credentials")


if __name__ == "__main__":
    # Choose which example to run
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        asyncio.run(quick_start_example())
    else:
        asyncio.run(run_all_examples())
