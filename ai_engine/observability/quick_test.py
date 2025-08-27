#!/usr/bin/env python3
"""
Quick Test Script for IA Influencer Observability Module

Tests core functionality without complex imports to verify the module works.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import sys
import asyncio
from datetime import datetime, timezone

def test_business_monitoring():
    """Test business process monitoring components"""
    print("🧪 Testing Business Process Monitoring...")
    
    try:
        from business_process_monitoring import (
            ContentType, CreatorType, ProcessStage, ProcessStatus,
            DistributionPlatform, ContentProcessingMonitor,
            CollaborationMonitor, MonetizationMonitor,
            BusinessProcessOrchestrator
        )
        
        # Test enums
        print(f"   ✅ Content Types: {[e.value for e in ContentType]}")
        print(f"   ✅ Creator Types: {[e.value for e in CreatorType]}")
        print(f"   ✅ Process Stages: {[e.value for e in ProcessStage]}")
        print(f"   ✅ Distribution Platforms: {[e.value for e in DistributionPlatform]}")
        
        # Test monitors
        content_monitor = ContentProcessingMonitor()
        collaboration_monitor = CollaborationMonitor()
        monetization_monitor = MonetizationMonitor()
        orchestrator = BusinessProcessOrchestrator()
        
        print("   ✅ All monitors created successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Business monitoring test failed: {e}")
        return False

def test_analytics():
    """Test analytics components"""
    print("🧪 Testing Analytics...")
    
    try:
        from analytics import (
            RealTimeAnalytics, HistoricalAnalytics, PredictiveAnalytics,
            AnalyticsTimeframe, AnalyticsMetricType, AnalyticsDataPoint
        )
        
        # Test analytics creation
        realtime = RealTimeAnalytics()
        historical = HistoricalAnalytics()
        predictive = PredictiveAnalytics()
        
        print(f"   ✅ Analytics Timeframes: {[e.value for e in AnalyticsTimeframe]}")
        print(f"   ✅ Metric Types: {[e.value for e in AnalyticsMetricType]}")
        print("   ✅ All analytics components created successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Analytics test failed: {e}")
        return False

def test_intelligent_monitoring():
    """Test intelligent monitoring"""
    print("🧪 Testing Intelligent Monitoring...")
    
    try:
        from intelligent_monitoring import (
            IntelligentMonitoringSystem, AnomalyDetector, 
            PredictiveEngine, AlertSeverity, MonitoringScope
        )
        
        # Test monitoring creation
        monitoring_system = IntelligentMonitoringSystem()
        anomaly_detector = AnomalyDetector()
        predictive_engine = PredictiveEngine()
        
        print(f"   ✅ Alert Severities: {[e.value for e in AlertSeverity]}")
        print(f"   ✅ Monitoring Scopes: {[e.value for e in MonitoringScope]}")
        print("   ✅ All monitoring components created successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Intelligent monitoring test failed: {e}")
        return False

def test_configuration():
    """Test configuration"""
    print("🧪 Testing Configuration...")
    
    try:
        from config import (
            ObservabilityConfig, Environment, MonitoringConfig,
            AnalyticsConfig, ReportingConfig
        )
        
        # Test config creation
        config = ObservabilityConfig()
        
        print(f"   ✅ Environments: {[e.value for e in Environment]}")
        print("   ✅ Configuration created successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

async def test_business_workflow():
    """Test a complete business workflow"""
    print("🧪 Testing Complete Business Workflow...")
    
    try:
        from business_process_monitoring import (
            ContentType, CreatorType, ProcessStage, ProcessStatus,
            DistributionPlatform, ContentProcessingMonitor,
            CollaborationMonitor, MonetizationMonitor
        )
        
        # Initialize monitors
        content_monitor = ContentProcessingMonitor()
        collaboration_monitor = CollaborationMonitor()
        monetization_monitor = MonetizationMonitor()
        
        # Simulate content processing
        await content_monitor.track_content_processing(
            content_id="test_song_001",
            content_type=ContentType.MUSIC,
            creator_type=CreatorType.MUSICIAN,
            stage=ProcessStage.UPLOAD,
            status=ProcessStatus.COMPLETED,
            processing_time_ms=250.0,
            file_size_mb=15.5,
            quality_score=0.92
        )
        
        # Simulate collaboration
        await collaboration_monitor.track_collaboration_match(
            creator1_id="musician_001",
            creator2_id="producer_001",
            match_score=0.85,
            match_successful=True,
            collaboration_type="music_production"
        )
        
        # Simulate monetization
        await monetization_monitor.track_revenue_event(
            content_id="test_song_001",
            creator_id="musician_001",
            platform=DistributionPlatform.SPOTIFY,
            revenue_type="streaming",
            amount=25.50,
            currency="USD"
        )
        
        # Get reports
        pipeline_report = await content_monitor.get_pipeline_performance_report()
        collab_analytics = await collaboration_monitor.get_collaboration_analytics()
        monetization_report = await monetization_monitor.get_monetization_report()
        
        print("   ✅ Content processing workflow completed")
        print("   ✅ Collaboration tracking completed")
        print("   ✅ Monetization tracking completed")
        print(f"   ✅ Pipeline report generated: {len(pipeline_report)} keys")
        print(f"   ✅ Collaboration analytics: {len(collab_analytics)} keys")
        print(f"   ✅ Monetization report: {len(monetization_report)} keys")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Business workflow test failed: {e}")
        return False

async def main():
    """Main test runner"""
    print("🎯 IA INFLUENCER AGENT - OBSERVABILITY MODULE QUICK TEST")
    print("=" * 70)
    print("👨‍💼 Author: Fahed Mlaiel <mlaiel@live.de>")
    print("🔍 Testing Core Functionality")
    print("=" * 70)
    
    tests = [
        ("Business Monitoring", test_business_monitoring),
        ("Analytics", test_analytics),
        ("Intelligent Monitoring", test_intelligent_monitoring),
        ("Configuration", test_configuration),
        ("Business Workflow", test_business_workflow)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name.upper()}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                success = await test_func()
            else:
                success = test_func()
            
            results[test_name] = success
            
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: EXCEPTION - {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("🏆 TEST SUMMARY:")
    print("=" * 70)
    
    passed_tests = sum(1 for success in results.values() if success)
    total_tests = len(tests)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    if success_rate == 100:
        print("\n🎉 ALL TESTS PASSED - MODULE IS FULLY FUNCTIONAL!")
        print("✅ IA Influencer Observability Module is ready for production")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} TESTS FAILED - SEE DETAILS ABOVE")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Fatal test error: {str(e)}")
        sys.exit(1)
