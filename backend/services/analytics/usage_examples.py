"""Analytics & SEO Engine Usage Examples

Comprehensive examples demonstrating how to use the Analytics & SEO Engine services.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.append('/home/runner/work/Ainflue/Ainflue')

# Import Analytics & SEO Engine services
from backend.services.analytics.seo.content_optimizer import ContentOptimizer, OptimizationRequest, OptimizationLevel
from backend.services.analytics.seo.meta_generator import MetaGenerator, MetaGenerationRequest
from backend.services.analytics.seo.sitemap_builder import SitemapBuilder, SitemapUrl, ChangeFrequency
from backend.services.analytics.tracking.user_behavior import UserBehaviorTracker, UserAction
from backend.services.analytics.tracking.content_performance import ContentPerformanceTracker
from backend.services.analytics.tracking.engagement_metrics import EngagementMetrics, EngagementEvent, EngagementType
from backend.services.analytics.reporting.report_generator import ReportGenerator, ReportConfiguration, ReportType, ReportFormat
from backend.services.analytics.reporting.export_manager import ExportManager, ExportRequest, DataSource, ExportFormat, ExportDestination


async def seo_optimization_example():
    """Example: SEO Content Optimization"""
    print("🔍 SEO Content Optimization Example")
    print("=" * 50)
    
    # Initialize content optimizer
    optimizer = ContentOptimizer({
        'language': 'en',
        'optimization_level': 'advanced'
    })
    
    # Prepare content for optimization
    content = """
    # The Future of Artificial Intelligence in Content Creation
    
    Artificial Intelligence is revolutionizing how we create and optimize content.
    Machine learning algorithms can now generate, optimize, and personalize content
    at scale, helping creators reach their audience more effectively.
    
    ## Key Benefits of AI in Content Creation
    - Automated content generation
    - SEO optimization recommendations
    - Personalized content delivery
    - Performance analytics and insights
    """
    
    # Create optimization request
    request = OptimizationRequest(
        content=content,
        target_keywords=["artificial intelligence", "content creation", "AI content", "machine learning"],
        optimization_level=OptimizationLevel.ADVANCED
    )
    
    # Optimize content
    result = await optimizer.optimize_content(request)
    
    print(f"Original content length: {len(content)} characters")
    print(f"Optimized content length: {len(result.optimized_content.optimized_content)} characters")
    print(f"Optimization score: {result.optimization_score:.1f}/100")
    print(f"Recommendations: {len(result.recommendations)}")
    for rec in result.recommendations[:3]:
        print(f"  • {rec}")
    
    return result


async def meta_tags_generation_example():
    """Example: Meta Tags Generation"""
    print("\n🏷️ Meta Tags Generation Example")
    print("=" * 50)
    
    # Initialize meta generator
    meta_gen = MetaGenerator({
        'base_url': 'https://ainflue.com',
        'default_author': 'Ainflue Team'
    })
    
    # Generate meta tags
    request = MetaGenerationRequest(
        content="A comprehensive guide to AI-powered content creation and optimization for modern creators.",
        target_keywords=["AI content creation", "content optimization", "creator tools"],
        title="AI Content Creation Guide",
        description="Learn how to leverage AI for creating and optimizing content that engages your audience",
        url_path="/guides/ai-content-creation",
        images=["https://ainflue.com/images/ai-guide-featured.jpg"]
    )
    
    result = await meta_gen.generate_meta_tags(request)
    
    print(f"Generated Title: {result.meta_tags.title}")
    print(f"Meta Description: {result.meta_tags.description}")
    print(f"Keywords: {', '.join(result.meta_tags.keywords[:5])}")
    print(f"Open Graph Title: {result.open_graph.title if result.open_graph else 'Not generated'}")
    
    return result


async def sitemap_generation_example():
    """Example: Dynamic Sitemap Generation"""
    print("\n🗺️ Sitemap Generation Example")
    print("=" * 50)
    
    # Initialize sitemap builder
    sitemap = SitemapBuilder()
    
    # Define URLs for sitemap
    urls = [
        SitemapUrl(
            loc="https://ainflue.com/",
            priority=1.0,
            changefreq=ChangeFrequency.WEEKLY,
            lastmod=datetime.now()
        ),
        SitemapUrl(
            loc="https://ainflue.com/about",
            priority=0.8,
            changefreq=ChangeFrequency.MONTHLY,
            lastmod=datetime.now() - timedelta(days=30)
        ),
        SitemapUrl(
            loc="https://ainflue.com/guides/ai-content-creation",
            priority=0.9,
            changefreq=ChangeFrequency.WEEKLY,
            lastmod=datetime.now() - timedelta(days=5)
        ),
        SitemapUrl(
            loc="https://ainflue.com/blog",
            priority=0.7,
            changefreq=ChangeFrequency.DAILY,
            lastmod=datetime.now() - timedelta(days=1)
        )
    ]
    
    # Generate sitemap
    result = await sitemap.build_sitemap(urls)
    
    print(f"Generated sitemap with {result.url_count} URLs")
    print(f"File size: {result.file_size} bytes")
    print(f"Generated at: {result.timestamp}")
    
    # Show sample XML output
    lines = result.xml_content.split('\n')
    print("\nSample XML output:")
    for line in lines[:10]:
        print(f"  {line}")
    if len(lines) > 10:
        print("  ...")
    
    return result


async def user_behavior_tracking_example():
    """Example: User Behavior Tracking"""
    print("\n👤 User Behavior Tracking Example")
    print("=" * 50)
    
    # Initialize behavior tracker
    tracker = UserBehaviorTracker()
    
    # Simulate user session
    user_id = "user_12345"
    session = await tracker.start_session(user_id, {
        'device': 'desktop',
        'browser': 'Chrome',
        'platform': 'Windows'
    })
    
    print(f"Started session: {session.session_id}")
    
    # Track user actions
    actions = [
        UserAction(
            action_id="action_1",
            user_id=user_id,
            session_id=session.session_id,
            action_type="page_view",
            target="/home",
            timestamp=datetime.now()
        ),
        UserAction(
            action_id="action_2",
            user_id=user_id,
            session_id=session.session_id,
            action_type="click",
            target="/guides/ai-content-creation",
            timestamp=datetime.now() + timedelta(minutes=2)
        ),
        UserAction(
            action_id="action_3",
            user_id=user_id,
            session_id=session.session_id,
            action_type="share",
            target="/guides/ai-content-creation",
            timestamp=datetime.now() + timedelta(minutes=5)
        )
    ]
    
    for action in actions:
        await tracker.track_user_action(action)
        session.actions_count += 1
    
    # End session
    session = await tracker.end_session(session)
    duration = (session.end_time - session.start_time).total_seconds()
    
    print(f"Session ended - Duration: {duration:.0f} seconds")
    print(f"Actions tracked: {session.actions_count}")
    
    # Analyze behavior
    analysis = await tracker.analyze_user_behavior(user_id, days=30)
    print(f"User segment: {analysis.segment.value}")
    print(f"Recommendations: {len(analysis.recommendations)}")
    
    return analysis


async def engagement_tracking_example():
    """Example: Engagement Metrics Tracking"""
    print("\n💝 Engagement Metrics Example")
    print("=" * 50)
    
    # Initialize engagement metrics
    engagement = EngagementMetrics()
    
    # Track engagement events
    content_id = "content_ai_guide"
    events = [
        EngagementEvent(
            event_id="eng_1",
            user_id="user_001",
            content_id=content_id,
            engagement_type=EngagementType.VIEW,
            timestamp=datetime.now() - timedelta(hours=2)
        ),
        EngagementEvent(
            event_id="eng_2",
            user_id="user_002",
            content_id=content_id,
            engagement_type=EngagementType.LIKE,
            timestamp=datetime.now() - timedelta(hours=1)
        ),
        EngagementEvent(
            event_id="eng_3",
            user_id="user_003",
            content_id=content_id,
            engagement_type=EngagementType.SHARE,
            timestamp=datetime.now() - timedelta(minutes=30)
        )
    ]
    
    for event in events:
        await engagement.track_engagement(event)
    
    # Get engagement analytics
    analytics = await engagement.get_content_engagement_analytics(content_id, days=7)
    
    print(f"Total engagements: {analytics.total_engagements}")
    print(f"Engagement rate: {analytics.engagement_rate:.1f}%")
    print(f"Engagement velocity: {analytics.engagement_velocity:.1f} per hour")
    print(f"Viral coefficient: {analytics.viral_coefficient:.2f}")
    
    return analytics


async def reporting_example():
    """Example: Analytics Report Generation"""
    print("\n📊 Analytics Reporting Example")
    print("=" * 50)
    
    # Initialize report generator
    reporter = ReportGenerator()
    
    # Generate comprehensive report
    config = ReportConfiguration(
        report_type=ReportType.COMPREHENSIVE,
        format=ReportFormat.JSON,
        period_days=30,
        include_charts=True,
        include_recommendations=True
    )
    
    report = await reporter.generate_report(config, user_id="user_12345")
    
    print(f"Report ID: {report.report_id}")
    print(f"Report Type: {report.report_type.value}")
    print(f"Sections: {len(report.sections)}")
    print(f"Period: {report.period['start_date'].date()} to {report.period['end_date'].date()}")
    
    # Show sections
    for section in report.sections:
        print(f"\n📋 {section.title}:")
        print(f"  Insights: {len(section.insights)}")
        print(f"  Recommendations: {len(section.recommendations)}")
        if section.insights:
            print(f"  • {section.insights[0]}")
    
    # Show executive summary
    print(f"\n📈 Executive Summary:")
    print(report.executive_summary[:200] + "..." if len(report.executive_summary) > 200 else report.executive_summary)
    
    return report


async def data_export_example():
    """Example: Data Export Management"""
    print("\n📤 Data Export Example")
    print("=" * 50)
    
    # Initialize export manager
    exporter = ExportManager({
        'export_directory': '/tmp/exports'
    })
    
    # Create export request
    request = ExportRequest(
        export_id="export_user_behavior_" + str(int(datetime.now().timestamp())),
        data_source=DataSource.USER_BEHAVIOR,
        format=ExportFormat.CSV,
        destination=ExportDestination.LOCAL_FILE,
        date_range={
            'start_date': datetime.now() - timedelta(days=7),
            'end_date': datetime.now()
        },
        filters={'platform': 'web'}
    )
    
    # Execute export
    result = await exporter.export_data(request)
    
    print(f"Export ID: {result.export_id}")
    print(f"Success: {result.success}")
    print(f"Records exported: {result.record_count}")
    print(f"File size: {result.file_size} bytes")
    print(f"File path: {result.file_path}")
    
    return result


async def main():
    """Run all examples"""
    print("🚀 Analytics & SEO Engine Usage Examples")
    print("=" * 60)
    
    try:
        # SEO Examples
        await seo_optimization_example()
        await meta_tags_generation_example()
        await sitemap_generation_example()
        
        # Tracking Examples
        await user_behavior_tracking_example()
        await engagement_tracking_example()
        
        # Reporting Examples
        await reporting_example()
        await data_export_example()
        
        print("\n✅ All examples completed successfully!")
        print("\n💡 Tips:")
        print("  • Integrate these services into your application's workflow")
        print("  • Use scheduled exports for regular data backups")
        print("  • Monitor engagement metrics to optimize content strategy")
        print("  • Generate regular reports for stakeholders")
        
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())