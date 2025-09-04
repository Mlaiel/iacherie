#!/usr/bin/env python3
"""
Example usage of the Consolidated Content AI Agents

This script demonstrates how to use the various content agents
for creating, optimizing, and scheduling social media content.
"""

import asyncio
from datetime import datetime, timezone, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.ai import (
    create_content_agent,
    ContentRequest,
    ContentType,
    Platform,
    ContentStyle,
    ScheduleRequest
)

async def content_creation_example():
    """Example of complete content creation workflow"""
    print("🎯 Content Creation Example")
    print("=" * 50)
    
    # Create the agent
    agent = create_content_agent()
    
    # 1. Create optimized caption for Instagram
    print("📝 1. Creating Instagram Caption...")
    caption_request = ContentRequest(
        content_type=ContentType.CAPTION,
        platform=Platform.INSTAGRAM,
        style=ContentStyle.CASUAL,
        target_audience="tech enthusiasts",
        topic="AI and creativity"
    )
    
    caption_result = await agent.process_content_request(caption_request)
    print(f"   Generated: {caption_result.content}")
    print(f"   Quality Score: {caption_result.quality_score:.2f}")
    print(f"   Hashtags: {', '.join(caption_result.hashtags[:5])}")
    
    # 2. Create a story for the same topic
    print("\n📚 2. Creating Engaging Story...")
    story_result = await agent.story_teller.create_story(
        "AI and creativity", "before_after", "tech enthusiasts"
    )
    print(f"   Story Structure: {story_result['structure']}")
    print(f"   Word Count: {story_result['analysis']['word_count']}")
    print(f"   Engagement Score: {story_result['analysis']['engagement_score']:.2f}")
    
    # 3. Predict viral potential
    print("\n🚀 3. Analyzing Viral Potential...")
    viral_analysis = await agent.viral_predictor.predict_viral_potential(
        caption_result.content, Platform.INSTAGRAM
    )
    print(f"   Viral Score: {viral_analysis['viral_score']:.2f}")
    print(f"   Viral Level: {viral_analysis['viral_level']}")
    print(f"   Recommendations: {viral_analysis['recommendations'][:2]}")
    
    # 4. Schedule content
    print("\n📅 4. Scheduling Content...")
    schedule_time = datetime.now(timezone.utc) + timedelta(hours=6)
    schedule_request = ScheduleRequest(
        content=caption_result.content,
        platform=Platform.INSTAGRAM,
        scheduled_time=schedule_time
    )
    
    schedule_result = await agent.scheduler.schedule_content(schedule_request)
    print(f"   Scheduled ID: {schedule_result['schedule_id']}")
    print(f"   Optimized Time: {schedule_result['optimized_time']}")
    
    # 5. Generate sample replies
    print("\n💬 5. Sample Reply Generation...")
    sample_comments = [
        "This is so cool! Tell me more!",
        "I don't really understand this...",
        "Amazing work! Keep it up!"
    ]
    
    for comment in sample_comments:
        reply = await agent.reply_generator.generate_reply(
            caption_result.content, comment, "friendly", Platform.INSTAGRAM
        )
        print(f"   Comment: '{comment}'")
        print(f"   Reply: '{reply}'\n")

async def multi_platform_example():
    """Example of creating content for multiple platforms"""
    print("\n🌐 Multi-Platform Content Example")
    print("=" * 50)
    
    agent = create_content_agent()
    topic = "sustainable living"
    
    platforms = [Platform.INSTAGRAM, Platform.TWITTER, Platform.LINKEDIN]
    
    for platform in platforms:
        print(f"\n📱 Creating content for {platform.value.upper()}...")
        
        # Adapt style based on platform
        if platform == Platform.LINKEDIN:
            style = ContentStyle.PROFESSIONAL
        elif platform == Platform.TWITTER:
            style = ContentStyle.CASUAL
        else:
            style = ContentStyle.EDUCATIONAL
        
        # Create optimized content
        package = await agent.create_complete_content_package(
            topic, platform, style
        )
        
        main_content = package['package']['main_content']
        print(f"   Content: {main_content.content[:80]}...")
        print(f"   Quality: {main_content.quality_score:.2f}")
        print(f"   Hashtags: {', '.join(main_content.hashtags[:3])}")

async def optimization_workflow_example():
    """Example of content optimization workflow"""
    print("\n⚡ Content Optimization Workflow")
    print("=" * 50)
    
    agent = create_content_agent()
    
    # Original content (not optimized)
    original_content = "I think technology is pretty interesting and people should learn about it"
    
    print(f"📝 Original: {original_content}")
    
    # Optimize for different platforms
    for platform in [Platform.INSTAGRAM, Platform.TIKTOK, Platform.YOUTUBE]:
        print(f"\n🔧 Optimizing for {platform.value.upper()}:")
        
        optimization = await agent.optimizer.optimize_content(
            original_content, platform
        )
        
        print(f"   Optimized: {optimization['optimized_content']}")
        print(f"   Changes: {optimization['changes']}")
        print(f"   Score: {optimization['optimization_score']:.2f}")
        print(f"   Improvement: {optimization['predicted_improvement']}")

if __name__ == "__main__":
    print("🤖 Consolidated Content AI Agents - Example Usage")
    print("=" * 60)
    
    # Run all examples
    asyncio.run(content_creation_example())
    asyncio.run(multi_platform_example())
    asyncio.run(optimization_workflow_example())
    
    print("\n✅ All examples completed successfully!")
    print("🎉 The Consolidated Content AI Agents are ready to use!")