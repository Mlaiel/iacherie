"""
Platform APIs Integration Usage Example
======================================

Example demonstrating how to use the Platform APIs Integration module.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from datetime import datetime, timedelta
from integrations.platforms import PlatformCoordinator


async def main():
    """Demonstrate platform integration usage"""
    
    # Initialize the platform coordinator
    async with PlatformCoordinator() as coordinator:
        
        print(" Platform APIs Integration Example")
        print("=" * 50)
        
        # 1. Configure OAuth for platforms
        print("\n1. Configuring OAuth for platforms...")
        
        # Configure YouTube
        coordinator.configure_platform_oauth(
            platform="youtube",
            client_id="your_youtube_client_id",
            client_secret="your_youtube_client_secret", 
            redirect_uri="http://localhost:8000/auth/youtube/callback"
        )
        
        # Configure Instagram
        coordinator.configure_platform_oauth(
            platform="instagram",
            client_id="your_instagram_client_id",
            client_secret="your_instagram_client_secret",
            redirect_uri="http://localhost:8000/auth/instagram/callback"
        )
        
        print(" OAuth configured for YouTube and Instagram")
        
        # 2. Generate authentication URLs
        print("\n2. Generating authentication URLs...")
        
        user_id = "user123"
        
        youtube_auth_url = await coordinator.initiate_platform_auth("youtube", user_id)
        instagram_auth_url = await coordinator.initiate_platform_auth("instagram", user_id)
        
        print(f" YouTube Auth URL: {youtube_auth_url[:80]}...")
        print(f" Instagram Auth URL: {instagram_auth_url[:80]}...")
        
        # 3. Check platform health status
        print("\n3. Checking platform health status...")
        
        status_dict = await coordinator.get_all_platform_status(user_id)
        
        for platform, status in status_dict.items():
            emoji = "" if status.is_connected else ""
            print(f"{emoji} {platform.capitalize()}: {'Connected' if status.is_connected else 'Disconnected'}")
            if status.error_message:
                print(f"   Error: {status.error_message}")
        
        # 4. Demonstrate rate limiting
        print("\n4. Testing rate limiting...")
        
        rate_status = await coordinator.rate_limiter.check_rate_limit("youtube", "search")
        print(f" YouTube search rate limit: {rate_status.remaining_requests} requests remaining")
        
        rate_status = await coordinator.rate_limiter.check_rate_limit("instagram", "media")
        print(f" Instagram media rate limit: {rate_status.remaining_requests} requests remaining")
        
        # 5. Demonstrate content protection monitoring
        print("\n5. Setting up content protection...")
        
        try:
            monitor_id = await coordinator.monitor_content_protection(
                user_id=user_id,
                content_title="My Original Song",
                content_type="audio",
                keywords=["my original song", "artist name", "album name"]
            )
            print(f" Content protection monitor created: {monitor_id}")
        except Exception as e:
            print(f" Content protection setup failed: {e}")
        
        # 6. Show supported platforms and their capabilities
        print("\n6. Supported platforms and capabilities...")
        
        supported_platforms = coordinator.oauth_manager.get_supported_platforms()
        
        platform_capabilities = {
            "youtube": ["Video upload", "Analytics", "Content ID", "Monetization"],
            "instagram": ["Photo/Video posts", "Stories", "Insights", "Business features"],
            "tiktok": ["Video upload", "Creator analytics", "Trending insights"],
            "spotify": ["Artist analytics", "Track data", "Playlists", "Following"],
            "facebook": ["Rights management", "Copyright claims", "Page insights"],
            "twitter": ["Tweets", "User management", "Analytics", "Engagement"]
        }
        
        for platform in supported_platforms:
            capabilities = platform_capabilities.get(platform, ["Basic API access"])
            print(f" {platform.capitalize()}:")
            for capability in capabilities:
                print(f"   • {capability}")
        
        # 7. Demonstrate cross-platform analytics (simulated)
        print("\n7. Cross-platform analytics example...")
        
        try:
            # This would work with real authenticated tokens
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            analytics = await coordinator.get_aggregated_analytics(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                platforms=["youtube", "instagram", "tiktok"]
            )
            
            print(f" Total views: {analytics.total_views}")
            print(f" Total engagement: {analytics.total_engagement}")
            print(f" Total followers: {analytics.total_followers}")
            print(f" Total revenue: ${analytics.total_revenue:.2f}")
            
        except Exception as e:
            print(f" Analytics demonstration failed (expected without real tokens): {e}")
            print(" Sample analytics structure:")
            print("   • Total views: 1,250,000")
            print("   • Total engagement: 85,000")
            print("   • Total followers: 45,000")
            print("   • Total revenue: $2,450.00")
        
        print("\n" + "=" * 50)
        print(" Platform APIs Integration example completed!")
        print("\nNext steps:")
        print("1. Set up OAuth credentials for each platform")
        print("2. Implement the OAuth callback endpoints in your web app")
        print("3. Store user tokens securely in your database")
        print("4. Use the coordinator to manage all platform operations")


if __name__ == "__main__":
    asyncio.run(main())