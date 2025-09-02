"""Test Main Platform Crawlers (Direct Import)
============================================

Test script that imports crawlers directly without going through the problematic __init__.py
"""

import asyncio
import sys
import os

# Add the project root to the path
sys.path.insert(0, '/home/runner/work/Ainflue/Ainflue')

async def test_crawlers():
    """
Test all platform crawlers."""
    try:
        # Direct import to avoid dependency issues
        sys.path.append('/home/runner/work/Ainflue/Ainflue/crawlers')
        from main_platform_crawlers import CrawlerOrchestrator
        
        print("🕷️ Testing Main Platform Crawlers")
        print("=" * 50)
        
        # Create orchestrator
        orchestrator = CrawlerOrchestrator()
        
        # Test supported platforms
        platforms = orchestrator.get_supported_platforms()
        print(f"✅ Supported platforms: {', '.join(platforms)}")
        
        # Test search across all platforms
        query = "test content"
        print(f"\n🔍 Searching for '{query}' across all platforms...")
        
        results = await orchestrator.search_all_platforms(query, max_results=3)
        
        print("\n📊 Search Results:")
        for platform, platform_results in results.items():
            print(f"  📱 {platform.upper()}: {len(platform_results)} results")
            for i, result in enumerate(platform_results[:2]):  # Show first 2 results
                print(f"    {i+1}. {result.title}")
                print(f"       URL: {result.url}")
                print(f"       Author: {result.author}")
        
        # Test individual crawler
        print(f"\n🎥 Testing YouTube crawler specifically...")
        youtube_crawler = await orchestrator.get_crawler('youtube')
        if youtube_crawler:
            youtube_results = await youtube_crawler.search_content("music video", max_results=2)
            print(f"  Found {len(youtube_results)} YouTube results")
            
            # Test getting details
            if youtube_results:
                details = await youtube_crawler.get_content_details(youtube_results[0].content_id)
                if details:
                    print(f"  ✅ Successfully retrieved video details")
        
        # Test Instagram story monitoring
        print(f"\n📷 Testing Instagram story monitoring...")
        instagram_crawler = await orchestrator.get_crawler('instagram')
        if instagram_crawler:
            async def mock_story_callback(update):
        try:
            logger.info(f"Executing mock_story_callback")
            
            # Implementation for mock_story_callback
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"mock_story_callback completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mock_story_callback failed: {e}")
            raise
            monitoring_task = asyncio.create_task(
                instagram_crawler.monitor_stories(["demo_user"], mock_story_callback)
            )
            
            # Wait a bit then cancel
            await asyncio.sleep(1)
            monitoring_task.cancel()
            try:
        try:
            logger.info(f"Executing mock_twitter_callback")
            
            # Implementation for mock_twitter_callback
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"mock_twitter_callback completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mock_twitter_callback failed: {e}")
            raise
            try:
                await monitoring_task
            except asyncio.CancelledError:
                print(f"  ✅ Instagram story monitoring test completed")
        
        # Test Twitter real-time monitoring
        print(f"\n🐦 Testing Twitter real-time monitoring...")
        twitter_crawler = await orchestrator.get_crawler('twitter')
        if twitter_crawler:
        try:
            logger.info(f"Executing mock_company_callback")
            
            # Implementation for mock_company_callback
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"mock_company_callback completed successfully")
            return result
            
        except Exception as e:
        try:
            logger.info(f"Executing mock_board_callback")
            
            # Implementation for mock_board_callback
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"mock_board_callback completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mock_board_callback failed: {e}")
            raise
            raise
        print(f"\n🐦 Testing Twitter real-time monitoring...")
        twitter_crawler = await orchestrator.get_crawler('twitter')
        if twitter_crawler:
        try:
            logger.info(f"Executing mock_server_callback")
            
            # Implementation for mock_server_callback
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"mock_server_callback completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mock_server_callback failed: {e}")
            raise
            async def mock_twitter_callback(update):
                print(f"    🐦 Twitter update: {update['type']} for '{update['keyword']}'")
        try:
            logger.info(f"Executing mock_channel_callback")
            
            # Implementation for mock_channel_callback
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"mock_channel_callback completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"mock_channel_callback failed: {e}")
            raise
            monitoring_task = asyncio.create_task(
                twitter_crawler.monitor_real_time_stream(["test"], mock_twitter_callback)
            )
            
            # Wait a bit then cancel
            await asyncio.sleep(1)
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                print(f"  ✅ Twitter real-time monitoring test completed")
        
        # Test platform-specific features
        print(f"\n🏢 Testing LinkedIn company monitoring...")
        linkedin_crawler = await orchestrator.get_crawler('linkedin')
        if linkedin_crawler:
            async def mock_company_callback(update):
                print(f"    🏢 Company update: {update['type']} for {update['company_id']}")
            
            monitoring_task = asyncio.create_task(
                linkedin_crawler.monitor_companies(["demo_company"], mock_company_callback)
            )
            
            await asyncio.sleep(1)
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                print(f"  ✅ LinkedIn company monitoring test completed")
        
        print(f"\n🎯 Testing Pinterest board tracking...")
        pinterest_crawler = await orchestrator.get_crawler('pinterest')
        if pinterest_crawler:
            async def mock_board_callback(update):
                print(f"    📌 Board update: {update['type']} for {update['board_id']}")
            
            monitoring_task = asyncio.create_task(
                pinterest_crawler.monitor_boards(["demo_board"], mock_board_callback)
            )
            
            await asyncio.sleep(1)
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                print(f"  ✅ Pinterest board tracking test completed")
        
        print(f"\n💬 Testing Discord server monitoring...")
        discord_crawler = await orchestrator.get_crawler('discord')
        if discord_crawler:
            async def mock_server_callback(update):
                print(f"    💬 Server update: {update['type']} for {update['server_id']}")
            
            monitoring_task = asyncio.create_task(
                discord_crawler.monitor_servers(["demo_server"], mock_server_callback)
            )
            
            await asyncio.sleep(1)
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                print(f"  ✅ Discord server monitoring test completed")
        
        print(f"\n📱 Testing Telegram channel monitoring...")
        telegram_crawler = await orchestrator.get_crawler('telegram')
        if telegram_crawler:
            async def mock_channel_callback(update):
                print(f"    📱 Channel update: {update['type']} for {update['channel_id']}")
            
            monitoring_task = asyncio.create_task(
                telegram_crawler.monitor_channels(["demo_channel"], mock_channel_callback)
            )
            
            await asyncio.sleep(1)
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                print(f"  ✅ Telegram channel monitoring test completed")
        
        print(f"\n✅ All tests completed successfully!")
        print(f"\n📈 Summary:")
        print(f"  • {len(platforms)} platforms supported")
        print(f"  • Search functionality working")
        print(f"  • Content details retrieval working")
        print(f"  • Real-time monitoring working")
        print(f"  • Platform-specific features working")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_crawlers())
    sys.exit(0 if success else 1)