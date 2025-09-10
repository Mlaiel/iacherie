"""
Comprehensive Integration Tests - Distribution Module
===================================================

Enterprise-grade integration tests for the Ainflue Distribution Module.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2024 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Any
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
from dataclasses import dataclass

# Test configuration
@dataclass
class TestConfig:
    """Test configuration"""
    test_timeout: int = 30
    mock_api_responses: bool = True
    performance_test_enabled: bool = True
    load_test_duration: int = 60
    stress_test_enabled: bool = False

@pytest.fixture
def test_config():
    """Test configuration fixture"""
    return TestConfig()

@pytest.fixture
async def mock_platform_apis():
    """Mock platform API responses"""
    with patch('aiohttp.ClientSession') as mock_session:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "success": True,
            "id": "post_123",
            "url": "https://platform.com/post/123"
        }
        
        mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
        mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
        
        yield mock_session

@pytest.fixture
async def mock_redis():
    """Mock Redis client"""
    with patch('aioredis.from_url') as mock_redis:
        mock_client = AsyncMock()
        mock_client.ping.return_value = True
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        mock_client.setex.return_value = True
        mock_redis.return_value = mock_client
        yield mock_client

class TestViralOptimizationIntegration:
    """Integration tests for viral optimization module"""
    
    @pytest.mark.asyncio
    async def test_viral_prediction_pipeline(self, test_config, mock_platform_apis):
        """Test complete viral prediction pipeline"""
        try:
            # Import viral optimization module
            from distribution.viral_optimization import viral_predictor
            
            # Test data
            content_data = {
                "content_id": "test_content_123",
                "content_type": "video",
                "title": "Test Video Content",
                "description": "This is a test video for viral prediction",
                "tags": ["test", "video", "viral"],
                "duration": 60,
                "file_size": 1024000,
                "metadata": {
                    "resolution": "1080p",
                    "fps": 30,
                    "format": "mp4"
                }
            }
            
            # Initialize predictor
            predictor = viral_predictor.ViralPredictor()
            await predictor.initialize()
            
            # Test viral prediction
            prediction_result = await predictor.predict_viral_potential(content_data)
            
            # Assertions
            assert prediction_result is not None
            assert "viral_score" in prediction_result
            assert "confidence" in prediction_result
            assert "factors" in prediction_result
            assert 0 <= prediction_result["viral_score"] <= 1
            assert 0 <= prediction_result["confidence"] <= 1
            
            # Test optimization suggestions
            optimization_result = await predictor.get_optimization_suggestions(content_data, prediction_result)
            
            assert optimization_result is not None
            assert "suggestions" in optimization_result
            assert isinstance(optimization_result["suggestions"], list)
            
        except ImportError:
            pytest.skip("Viral optimization module not available")
    
    @pytest.mark.asyncio
    async def test_trend_analysis_integration(self, test_config):
        """Test trend analysis integration"""
        try:
            from distribution.viral_optimization import trend_analyzer
            
            analyzer = trend_analyzer.TrendAnalyzer()
            await analyzer.initialize()
            
            # Test trend detection
            trends = await analyzer.detect_current_trends(categories=["technology", "entertainment"])
            
            assert trends is not None
            assert isinstance(trends, list)
            
            # Test trend scoring
            content_data = {
                "title": "AI Technology Breakthrough",
                "tags": ["ai", "technology", "innovation"],
                "description": "Latest AI development"
            }
            
            trend_score = await analyzer.calculate_trend_alignment(content_data, trends)
            
            assert 0 <= trend_score <= 1
            
        except ImportError:
            pytest.skip("Trend analyzer module not available")

class TestAudienceIntelligenceIntegration:
    """Integration tests for audience intelligence module"""
    
    @pytest.mark.asyncio
    async def test_audience_profiling_pipeline(self, test_config, mock_redis):
        """Test complete audience profiling pipeline"""
        try:
            from distribution.audience_intelligence import audience_profiler
            
            profiler = audience_profiler.AudienceProfiler()
            await profiler.initialize()
            
            # Test user data
            user_data = {
                "user_id": "user_123",
                "engagement_history": [
                    {"content_type": "video", "engagement_type": "like", "timestamp": "2024-01-01T10:00:00Z"},
                    {"content_type": "image", "engagement_type": "share", "timestamp": "2024-01-01T11:00:00Z"}
                ],
                "demographic_data": {
                    "age": 25,
                    "location": "US",
                    "interests": ["technology", "music", "travel"]
                }
            }
            
            # Test audience profiling
            profile = await profiler.create_audience_profile(user_data)
            
            assert profile is not None
            assert "demographics" in profile
            assert "psychographics" in profile
            assert "preferences" in profile
            assert "engagement_patterns" in profile
            
            # Test behavior prediction
            content_data = {
                "content_type": "video",
                "topic": "technology",
                "duration": 120
            }
            
            prediction = await profiler.predict_engagement(user_data["user_id"], content_data)
            
            assert prediction is not None
            assert "engagement_probability" in prediction
            assert 0 <= prediction["engagement_probability"] <= 1
            
        except ImportError:
            pytest.skip("Audience profiler module not available")

class TestContentAmplificationIntegration:
    """Integration tests for content amplification module"""
    
    @pytest.mark.asyncio
    async def test_amplification_strategy_pipeline(self, test_config, mock_platform_apis):
        """Test complete amplification strategy pipeline"""
        try:
            from distribution.content_amplification import amplification_engine
            
            engine = amplification_engine.AmplificationEngine()
            await engine.initialize()
            
            # Test content data
            content_data = {
                "content_id": "content_456",
                "content_type": "video",
                "target_audience": {
                    "age_range": [18, 35],
                    "interests": ["music", "entertainment"],
                    "locations": ["US", "UK", "CA"]
                },
                "budget": 500.0,
                "goals": {
                    "target_reach": 100000,
                    "target_engagement_rate": 0.12
                }
            }
            
            # Test strategy generation
            strategy = await engine.generate_amplification_strategy(content_data)
            
            assert strategy is not None
            assert "channels" in strategy
            assert "estimated_reach" in strategy
            assert "estimated_cost" in strategy
            assert "timeline" in strategy
            
            # Test strategy execution
            execution_result = await engine.execute_strategy(strategy)
            
            assert execution_result is not None
            assert "execution_id" in execution_result
            assert "status" in execution_result
            
        except ImportError:
            pytest.skip("Amplification engine module not available")

class TestPlatformOptimizationIntegration:
    """Integration tests for platform optimization module"""
    
    @pytest.mark.asyncio
    async def test_multi_platform_optimization(self, test_config, mock_platform_apis):
        """Test multi-platform optimization pipeline"""
        try:
            from distribution.platform_optimization import platform_analyzer
            
            analyzer = platform_analyzer.PlatformAnalyzer()
            await analyzer.initialize()
            
            platforms = ["instagram", "tiktok", "youtube", "facebook"]
            content_data = {
                "content_type": "video",
                "duration": 30,
                "aspect_ratio": "16:9",
                "title": "Test Content",
                "description": "Test description"
            }
            
            # Test platform analysis
            for platform in platforms:
                analysis = await analyzer.analyze_platform_requirements(platform)
                
                assert analysis is not None
                assert "algorithm_factors" in analysis
                assert "content_requirements" in analysis
                assert "best_practices" in analysis
                
                # Test content optimization for platform
                optimization = await analyzer.optimize_content_for_platform(content_data, platform)
                
                assert optimization is not None
                assert "optimized_content" in optimization
                assert "recommendations" in optimization
            
        except ImportError:
            pytest.skip("Platform analyzer module not available")

class TestRealTimeOptimizationIntegration:
    """Integration tests for real-time optimization module"""
    
    @pytest.mark.asyncio
    async def test_real_time_monitoring_pipeline(self, test_config, mock_redis):
        """Test real-time monitoring and optimization pipeline"""
        try:
            from distribution.real_time_optimization import live_performance_monitor
            
            monitor = live_performance_monitor.LivePerformanceMonitor()
            await monitor.initialize()
            
            content_id = "content_789"
            
            # Test live monitoring setup
            monitoring_config = {
                "content_id": content_id,
                "platforms": ["instagram", "tiktok"],
                "metrics": ["views", "likes", "shares", "comments"],
                "update_interval": 10
            }
            
            await monitor.start_monitoring(monitoring_config)
            
            # Simulate some metrics
            test_metrics = {
                "views": 1500,
                "likes": 120,
                "shares": 25,
                "comments": 8,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            await monitor.update_metrics(content_id, test_metrics)
            
            # Test performance analysis
            analysis = await monitor.analyze_performance(content_id)
            
            assert analysis is not None
            assert "current_metrics" in analysis
            assert "performance_trend" in analysis
            assert "optimization_suggestions" in analysis
            
            # Test adaptive optimization
            optimization = await monitor.get_optimization_recommendations(content_id)
            
            assert optimization is not None
            assert isinstance(optimization, list)
            
        except ImportError:
            pytest.skip("Live performance monitor module not available")

class TestCreatorCollaborationIntegration:
    """Integration tests for creator collaboration module"""
    
    @pytest.mark.asyncio
    async def test_collaboration_matching_pipeline(self, test_config, mock_redis):
        """Test creator collaboration matching pipeline"""
        try:
            from distribution.creator_collaboration_hub import collaboration_matcher
            
            matcher = collaboration_matcher.CollaborationMatcher()
            await matcher.initialize()
            
            # Test creator data
            creator_data = {
                "creator_id": "creator_123",
                "profile": {
                    "follower_count": 50000,
                    "engagement_rate": 0.08,
                    "content_categories": ["music", "lifestyle"],
                    "target_audience": {
                        "age_range": [18, 30],
                        "gender_split": {"male": 0.4, "female": 0.6},
                        "top_locations": ["US", "UK"]
                    }
                },
                "collaboration_preferences": {
                    "types": ["duet", "cross_promotion"],
                    "budget_range": [0, 1000],
                    "audience_overlap_preference": [0.2, 0.6]
                }
            }
            
            # Test creator matching
            matches = await matcher.find_collaboration_matches(creator_data)
            
            assert matches is not None
            assert isinstance(matches, list)
            
            if matches:
                match = matches[0]
                assert "creator_id" in match
                assert "compatibility_score" in match
                assert "collaboration_potential" in match
                assert 0 <= match["compatibility_score"] <= 1
            
            # Test collaboration campaign creation
            if matches:
                campaign_data = {
                    "campaign_name": "Test Collaboration",
                    "creators": [creator_data["creator_id"], matches[0]["creator_id"]],
                    "campaign_type": "cross_promotion",
                    "timeline": {
                        "start_date": "2024-01-15T00:00:00Z",
                        "end_date": "2024-01-22T23:59:59Z"
                    }
                }
                
                campaign = await matcher.create_collaboration_campaign(campaign_data)
                
                assert campaign is not None
                assert "campaign_id" in campaign
                assert "status" in campaign
                
        except ImportError:
            pytest.skip("Collaboration matcher module not available")

class TestCrisisManagementIntegration:
    """Integration tests for crisis management module"""
    
    @pytest.mark.asyncio
    async def test_crisis_detection_pipeline(self, test_config, mock_platform_apis):
        """Test crisis detection and response pipeline"""
        try:
            from distribution.crisis_management import crisis_detector
            
            detector = crisis_detector.CrisisDetector()
            await detector.initialize()
            
            content_id = "content_crisis_test"
            
            # Test normal content monitoring
            normal_metrics = {
                "comments": [
                    {"text": "Great content!", "sentiment": 0.8},
                    {"text": "Love this!", "sentiment": 0.9},
                    {"text": "Amazing work", "sentiment": 0.7}
                ],
                "engagement_rate": 0.12,
                "reach": 10000,
                "negative_feedback_ratio": 0.05
            }
            
            normal_analysis = await detector.analyze_content_risk(content_id, normal_metrics)
            
            assert normal_analysis is not None
            assert "risk_level" in normal_analysis
            assert normal_analysis["risk_level"] in ["low", "medium", "high", "critical"]
            assert normal_analysis["risk_level"] == "low"
            
            # Test crisis scenario
            crisis_metrics = {
                "comments": [
                    {"text": "This is terrible!", "sentiment": 0.1},
                    {"text": "I hate this", "sentiment": 0.1},
                    {"text": "Worst content ever", "sentiment": 0.05}
                ],
                "engagement_rate": 0.02,
                "reach": 50000,
                "negative_feedback_ratio": 0.85,
                "reports_count": 25,
                "share_velocity": -0.5
            }
            
            crisis_analysis = await detector.analyze_content_risk(content_id, crisis_metrics)
            
            assert crisis_analysis is not None
            assert crisis_analysis["risk_level"] in ["high", "critical"]
            
            # Test crisis response
            if crisis_analysis["risk_level"] == "critical":
                response = await detector.initiate_crisis_response(content_id, crisis_analysis)
                
                assert response is not None
                assert "response_plan" in response
                assert "actions_taken" in response
                assert "estimated_impact_reduction" in response
            
        except ImportError:
            pytest.skip("Crisis detector module not available")

class TestSecurityIntegration:
    """Integration tests for security modules"""
    
    @pytest.mark.asyncio
    async def test_security_pipeline(self, test_config):
        """Test complete security pipeline"""
        try:
            from distribution.security import threat_detector, audit_logger
            
            # Test threat detection
            detector = threat_detector.ThreatDetector()
            await detector.initialize()
            
            # Test normal request
            normal_request = {
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0 (compatible browser)",
                "request_path": "/api/v1/distribution/viral/predict",
                "request_method": "POST",
                "request_size": 1024,
                "headers": {"Content-Type": "application/json"}
            }
            
            threat_analysis = await detector.analyze_request(normal_request)
            
            assert threat_analysis is not None
            assert "threat_level" in threat_analysis
            assert threat_analysis["threat_level"] == "low"
            
            # Test suspicious request
            suspicious_request = {
                "ip_address": "10.0.0.1",
                "user_agent": "sqlmap/1.0",
                "request_path": "/api/v1/distribution/../../../etc/passwd",
                "request_method": "GET",
                "request_size": 10240,
                "headers": {"X-Injection": "'; DROP TABLE users; --"}
            }
            
            suspicious_analysis = await detector.analyze_request(suspicious_request)
            
            assert suspicious_analysis is not None
            assert suspicious_analysis["threat_level"] in ["high", "critical"]
            
            # Test audit logging
            logger_instance = audit_logger.AuditLogger(audit_logger.AuditLogConfig())
            await logger_instance.start()
            
            # Test logging security event
            await audit_logger.log_security_violation(
                logger_instance,
                user_id="test_user",
                violation_type="sql_injection_attempt",
                ip_address=suspicious_request["ip_address"],
                details=suspicious_analysis
            )
            
            await logger_instance.stop()
            
        except ImportError:
            pytest.skip("Security modules not available")

class TestPerformanceIntegration:
    """Performance integration tests"""
    
    @pytest.mark.asyncio
    async def test_performance_monitoring(self, test_config):
        """Test performance monitoring integration"""
        if not test_config.performance_test_enabled:
            pytest.skip("Performance tests disabled")
        
        try:
            from distribution.monitoring import performance_tracker
            
            tracker = performance_tracker.PerformanceTracker()
            await tracker.start()
            
            # Simulate various operations
            async with performance_tracker.PerformanceTimer(tracker, "test_operation"):
                await asyncio.sleep(0.1)  # Simulate work
            
            # Test metrics recording
            await tracker.record_metric(
                "test_metric",
                100.0,
                performance_tracker.MetricType.GAUGE,
                unit="requests"
            )
            
            # Track some requests
            await tracker.track_request(duration_ms=50.0, success=True)
            await tracker.track_request(duration_ms=120.0, success=True)
            await tracker.track_request(duration_ms=200.0, success=False)
            
            # Get performance summary
            summary = await tracker.get_metrics_summary(hours=1)
            
            assert summary is not None
            assert "system_metrics" in summary or "application_metrics" in summary or "custom_metrics" in summary
            
            await tracker.stop()
            
        except ImportError:
            pytest.skip("Performance tracker module not available")

@pytest.mark.asyncio
async def test_end_to_end_distribution_pipeline(test_config, mock_platform_apis, mock_redis):
    """Complete end-to-end distribution pipeline test"""
    
    # Test content creation and distribution
    content_data = {
        "content_id": "e2e_test_content",
        "content_type": "video",
        "title": "End-to-End Test Video",
        "description": "Testing complete distribution pipeline",
        "tags": ["test", "automation", "distribution"],
        "target_platforms": ["instagram", "tiktok", "youtube"],
        "target_audience": {
            "age_range": [18, 35],
            "interests": ["technology", "entertainment"]
        },
        "budget": 1000.0
    }
    
    results = {}
    
    # Step 1: Viral prediction
    try:
        from distribution.viral_optimization import viral_predictor
        predictor = viral_predictor.ViralPredictor()
        await predictor.initialize()
        viral_result = await predictor.predict_viral_potential(content_data)
        results["viral_prediction"] = viral_result
    except ImportError:
        results["viral_prediction"] = {"skipped": "Module not available"}
    
    # Step 2: Audience analysis
    try:
        from distribution.audience_intelligence import audience_profiler
        profiler = audience_profiler.AudienceProfiler()
        await profiler.initialize()
        audience_result = await profiler.analyze_target_audience(content_data["target_audience"])
        results["audience_analysis"] = audience_result
    except ImportError:
        results["audience_analysis"] = {"skipped": "Module not available"}
    
    # Step 3: Platform optimization
    try:
        from distribution.platform_optimization import platform_analyzer
        analyzer = platform_analyzer.PlatformAnalyzer()
        await analyzer.initialize()
        
        platform_results = {}
        for platform in content_data["target_platforms"]:
            optimization = await analyzer.optimize_content_for_platform(content_data, platform)
            platform_results[platform] = optimization
        
        results["platform_optimization"] = platform_results
    except ImportError:
        results["platform_optimization"] = {"skipped": "Module not available"}
    
    # Step 4: Content amplification
    try:
        from distribution.content_amplification import amplification_engine
        engine = amplification_engine.AmplificationEngine()
        await engine.initialize()
        amplification_result = await engine.generate_amplification_strategy(content_data)
        results["amplification_strategy"] = amplification_result
    except ImportError:
        results["amplification_strategy"] = {"skipped": "Module not available"}
    
    # Verify end-to-end pipeline completion
    assert len(results) > 0
    
    # Check that at least some modules were available
    available_modules = [k for k, v in results.items() if not isinstance(v, dict) or "skipped" not in v]
    assert len(available_modules) > 0, "No distribution modules were available for testing"
    
    print(f"E2E Pipeline Results: {json.dumps(results, indent=2, default=str)}")

if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=distribution",
        "--cov-report=html",
        "--cov-report=term-missing"
    ])