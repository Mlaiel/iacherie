"""Test Main Platform Crawlers
===========================

Test script to verify that all 10 main platform crawlers work correctly.
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
        # Import the crawlers
        from crawlers.main_platform_crawlers import CrawlerOrchestrator
        
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
        
        # Test copyright monitoring (briefly)
        print(f"\n🛡️ Testing copyright monitoring...")
        async def mock_callback(violation):
            print(f"    🚨 Mock violation detected: {violation['type']}")
        
        # Run a brief test of monitoring (for 5 seconds)
        monitoring_task = asyncio.create_task(
            youtube_crawler.monitor_copyright_violations(["test song"], mock_callback)
        )
        
        # Wait a bit then cancel
        await asyncio.sleep(2)
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            print(f"  ✅ Copyright monitoring test completed")
        
        print(f"\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_crawlers())
    sys.exit(0 if success else 1)