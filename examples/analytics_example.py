"""Example usage of the consolidated analytics module

This example demonstrates how to use the analytics consolidation module
to perform various types of analytics operations.
"""

import asyncio
import json
from datetime import datetime, timedelta

# Add project root to path for imports
import sys
import os
sys.path.insert(0, '/home/runner/work/Ainflue/Ainflue')

from backend.ai.analytics import (
    AnalyticsHub,
    AnalyticsRequest,
    analyze_trends,
    predict_engagement,
    analyze_audience,
    monitor_competitors,
    comprehensive_analytics
)

async def main():
    """Example usage of the analytics consolidation module"""
    
    print("🎯 Analytics Consolidation Module - Usage Examples")
    print("=" * 60)
    
    # Sample data for demonstrations
    sample_data = {
        'content_type': 'video',
        'platform': 'youtube',
        'metrics': ['views', 'likes', 'comments', 'shares'],
        'historical_data': {
            'last_week': {'views': 5000, 'likes': 250, 'comments': 45},
            'last_month': {'views': 20000, 'likes': 1000, 'comments': 180}
        },
        'target_audience': {
            'age_group': '18-35',
            'interests': ['technology', 'gaming', 'lifestyle'],
            'location': 'global'
        },
        'competitors': ['competitor1', 'competitor2', 'competitor3'],
        'scheduling': {
            'preferred_times': ['18:00', '20:00'],
            'frequency': 'daily'
        }
    }
    
    date_range = {
        'start': (datetime.now() - timedelta(days=30)).isoformat(),
        'end': datetime.now().isoformat()
    }
    
    print("\n1. 📈 Trend Analysis")
    print("-" * 30)
    trend_result = await analyze_trends(sample_data)
    print(f"Success: {trend_result.success}")
    print(f"Insights: {json.dumps(trend_result.insights, indent=2)}")
    print(f"Metrics: {json.dumps(trend_result.metrics, indent=2)}")
    
    print("\n2. 💫 Engagement Prediction")
    print("-" * 30)
    engagement_result = await predict_engagement(sample_data)
    print(f"Success: {engagement_result.success}")
    print(f"Insights: {json.dumps(engagement_result.insights, indent=2)}")
    print(f"Metrics: {json.dumps(engagement_result.metrics, indent=2)}")
    
    print("\n3. 👥 Audience Analysis")
    print("-" * 30)
    audience_result = await analyze_audience(sample_data)
    print(f"Success: {audience_result.success}")
    print(f"Insights: {json.dumps(audience_result.insights, indent=2)}")
    print(f"Metrics: {json.dumps(audience_result.metrics, indent=2)}")
    
    print("\n4. 🔍 Competitor Monitoring")
    print("-" * 30)
    competitor_result = await monitor_competitors(sample_data)
    print(f"Success: {competitor_result.success}")
    print(f"Insights: {json.dumps(competitor_result.insights, indent=2)}")
    print(f"Metrics: {json.dumps(competitor_result.metrics, indent=2)}")
    
    print("\n5. 🌟 Comprehensive Analytics")
    print("-" * 30)
    comprehensive_result = await comprehensive_analytics(sample_data)
    print(f"Success: {comprehensive_result.success}")
    print(f"Analysis Types: {list(comprehensive_result.results.keys()) if comprehensive_result.results else 'None'}")
    print(f"Total Insights: {len(comprehensive_result.insights) if comprehensive_result.insights else 0}")
    print(f"Processing Time: {comprehensive_result.processing_time:.2f}s")
    
    print("\n6. 🏗️ Using AnalyticsHub Directly")
    print("-" * 30)
    
    # Initialize analytics hub
    hub = AnalyticsHub()
    
    # Get system status
    status = await hub.get_system_status()
    print(f"System Status: {json.dumps(status, indent=2)}")
    
    # Create custom request
    custom_request = AnalyticsRequest(
        request_id="example_request_001",
        analysis_type="trend",
        data=sample_data,
        user_id="user_123",
        platform="youtube",
        date_range=date_range,
        filters={'category': 'tech'},
        options={'depth': 'detailed', 'include_forecasts': True}
    )
    
    # Process custom request
    custom_result = await hub.process_analytics_request(custom_request)
    print(f"\nCustom Request Result:")
    print(f"  Request ID: {custom_result.request_id}")
    print(f"  Success: {custom_result.success}")
    print(f"  Analysis Type: {custom_result.analysis_type}")
    print(f"  Processing Time: {custom_result.processing_time:.2f}s")
    
    print("\n7. 📊 Consolidated Results Summary")
    print("-" * 30)
    
    all_results = [
        ("Trend Analysis", trend_result),
        ("Engagement Prediction", engagement_result),
        ("Audience Analysis", audience_result),
        ("Competitor Monitoring", competitor_result),
        ("Comprehensive Analytics", comprehensive_result)
    ]
    
    print(f"{'Analysis Type':<25} {'Success':<10} {'Insights':<10} {'Processing Time':<15}")
    print("-" * 65)
    
    for name, result in all_results:
        insights_count = len(result.insights) if result.insights else 0
        processing_time = f"{result.processing_time:.2f}s" if result.processing_time else "N/A"
        print(f"{name:<25} {'✓' if result.success else '✗':<10} {insights_count:<10} {processing_time:<15}")
    
    print("\n🎉 Analytics Consolidation Examples Completed Successfully!")
    print("\nKey Features Demonstrated:")
    print("- ✓ Trend analysis with pattern recognition")
    print("- ✓ Engagement prediction with optimization suggestions")
    print("- ✓ Audience segmentation and behavior analysis") 
    print("- ✓ Competitor monitoring and market intelligence")
    print("- ✓ Comprehensive multi-dimensional analytics")
    print("- ✓ Unified API with consistent response structure")
    print("- ✓ Fallback implementations for development/testing")
    print("- ✓ Async support for high-performance operations")

if __name__ == "__main__":
    asyncio.run(main())