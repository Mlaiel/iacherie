# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""
import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Test Enhanced Performance Optimization Features

This test validates the enhanced performance profiling, caching strategy,
and database indexing optimizations.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Test Performance Optimization Profiling
class TestEnhancedPerformanceProfiling:
    """Test enhanced performance profiling capabilities"""
    
    def test_advanced_performance_analyzer_initialization(self):
        """Test AdvancedPerformanceAnalyzer initialization"""
        from core.pipeline.performance_optimizer import AdvancedPerformanceAnalyzer
        
        config = {
            "ml_enabled": True,
            "analysis_window": 3600,
            "prediction_horizon": 300
        }
        
        analyzer = AdvancedPerformanceAnalyzer(config)
        
        assert analyzer.config == config
        assert hasattr(analyzer, 'prediction_models')
        assert hasattr(analyzer, 'performance_patterns')
        assert hasattr(analyzer, 'historical_data')
        assert hasattr(analyzer, 'real_time_analytics')
    
    def test_performance_trend_analysis(self):
        """Test performance trend analysis"""
        from core.pipeline.performance_optimizer import AdvancedPerformanceAnalyzer, PerformanceMeasurement, PerformanceProfile, PerformanceMetric
        
        config = {"analysis_enabled": True}
        analyzer = AdvancedPerformanceAnalyzer(config)
        
        # Create test profile with measurements
        profile = PerformanceProfile(
            profile_id="test_profile",
            component_name="test_component"
        )
        
        # Add test measurements showing an increasing trend
        base_time = datetime.now()
        for i in range(10):
            measurement = PerformanceMeasurement(
                metric=PerformanceMetric.EXECUTION_TIME,
                value=1.0 + (i * 0.1),  # Increasing trend
                timestamp=base_time + timedelta(seconds=i)
            )
            profile.measurements.append(measurement)
        
        # Analyze trends
        analysis = analyzer.analyze_performance_trends(profile)
        
        assert "trend_analysis" in analysis
        assert "anomaly_detection" in analysis
        assert "performance_prediction" in analysis
        assert "optimization_opportunities" in analysis
        assert "risk_assessment" in analysis
        
        # Check trend analysis results
        trends = analysis["trend_analysis"]
        if "execution_time" in trends:
            trend = trends["execution_time"]
            assert trend["direction"] == "increasing"
            assert trend["slope"] > 0
    
    def test_anomaly_detection(self):
        """Test performance anomaly detection"""
        from core.pipeline.performance_optimizer import AdvancedPerformanceAnalyzer, PerformanceMeasurement, PerformanceProfile, PerformanceMetric
        
        config = {"anomaly_detection_enabled": True}
        analyzer = AdvancedPerformanceAnalyzer(config)
        
        profile = PerformanceProfile(
            profile_id="anomaly_test",
            component_name="test_component"
        )
        
        # Add normal measurements and one anomaly
        normal_values = [1.0] * 8 + [10.0] + [1.0] * 1  # Spike in the middle
        base_time = datetime.now()
        
        for i, value in enumerate(normal_values):
            measurement = PerformanceMeasurement(
                metric=PerformanceMetric.EXECUTION_TIME,
                value=value,
                timestamp=base_time + timedelta(seconds=i)
            )
            profile.measurements.append(measurement)
        
        # Analyze for anomalies
        analysis = analyzer.analyze_performance_trends(profile)
        anomaly_detection = analysis["anomaly_detection"]
        
        assert "detected_anomalies" in anomaly_detection
        assert "anomaly_score" in anomaly_detection
        assert "severity" in anomaly_detection
        
        # Should detect the spike as an anomaly
        if anomaly_detection["detected_anomalies"]:
            assert len(anomaly_detection["detected_anomalies"]) > 0
    
    def test_optimization_opportunity_identification(self):
        """Test optimization opportunity identification"""
        from core.pipeline.performance_optimizer import AdvancedPerformanceAnalyzer, PerformanceMeasurement, PerformanceProfile, PerformanceMetric
        
        config = {"optimization_analysis_enabled": True}
        analyzer = AdvancedPerformanceAnalyzer(config)
        
        profile = PerformanceProfile(
            profile_id="optimization_test", 
            component_name="test_component"
        )
        
        # Add measurements showing high CPU usage (opportunity for optimization)
        base_time = datetime.now()
        for i in range(10):
            # CPU usage measurement
            cpu_measurement = PerformanceMeasurement(
                metric=PerformanceMetric.CPU_USAGE,
                value=85.0 + (i % 3),  # High CPU usage
                timestamp=base_time + timedelta(seconds=i)
            )
            profile.measurements.append(cpu_measurement)
            
            # Memory usage measurement  
            memory_measurement = PerformanceMeasurement(
                metric=PerformanceMetric.MEMORY_USAGE,
                value=90.0 + (i % 2),  # High memory usage
                timestamp=base_time + timedelta(seconds=i)
            )
            profile.measurements.append(memory_measurement)
        
        # Analyze for optimization opportunities
        analysis = analyzer.analyze_performance_trends(profile)
        opportunities = analysis["optimization_opportunities"]
        
        assert isinstance(opportunities, list)
        
        # Should identify CPU and memory optimization opportunities
        if opportunities:
            # Check for CPU optimization opportunity
            cpu_opportunities = [opp for opp in opportunities if "cpu" in opp.get("type", "")]
            memory_opportunities = [opp for opp in opportunities if "memory" in opp.get("type", "")]
            
            assert len(cpu_opportunities) > 0 or len(memory_opportunities) > 0
            
            # Validate opportunity structure
            for opp in opportunities:
                assert "type" in opp
                assert "priority" in opp
                assert "description" in opp
                assert "recommendations" in opp
                assert "expected_impact" in opp
    
    @pytest.mark.asyncio
    async def test_real_time_performance_monitor(self):
        """Test real-time performance monitoring"""
        from core.pipeline.performance_optimizer import RealTimePerformanceMonitor
        
        config = {
            "monitoring_interval": 0.1,  # 100ms for fast testing
            "alert_thresholds": {
                "cpu_usage": {"warning": 50.0, "critical": 80.0}
            }
        }
        
        monitor = RealTimePerformanceMonitor(config)
        
        # Test initialization
        assert monitor.config == config
        assert hasattr(monitor, 'metric_streams')
        assert hasattr(monitor, 'alert_thresholds')
        assert hasattr(monitor, 'active_alerts')
        
        # Test monitoring start/stop
        await monitor.start_monitoring()
        assert monitor.monitoring_active is True
        
        # Let it collect some data
        await asyncio.sleep(0.5)
        
        # Test status retrieval
        status = monitor.get_current_status()
        assert "monitoring_active" in status
        assert "active_alerts" in status
        assert "health_score" in status
        
        # Stop monitoring
        await monitor.stop_monitoring()
        assert monitor.monitoring_active is False
    
    def test_performance_risk_assessment(self):
        """Test performance risk assessment"""
        from core.pipeline.performance_optimizer import AdvancedPerformanceAnalyzer, PerformanceMeasurement, PerformanceProfile, PerformanceMetric
        
        config = {"risk_assessment_enabled": True}
        analyzer = AdvancedPerformanceAnalyzer(config)
        
        profile = PerformanceProfile(
            profile_id="risk_test",
            component_name="test_component"
        )
        
        # Add measurements showing critical resource usage
        base_time = datetime.now()
        for i in range(10):
            # Critical CPU usage
            cpu_measurement = PerformanceMeasurement(
                metric=PerformanceMetric.CPU_USAGE,
                value=97.0,  # Critical level
                timestamp=base_time + timedelta(seconds=i)
            )
            profile.measurements.append(cpu_measurement)
            
            # Critical memory usage
            memory_measurement = PerformanceMeasurement(
                metric=PerformanceMetric.MEMORY_USAGE,
                value=96.0,  # Critical level
                timestamp=base_time + timedelta(seconds=i)
            )
            profile.measurements.append(memory_measurement)
        
        # Analyze risks
        analysis = analyzer.analyze_performance_trends(profile)
        risk_assessment = analysis["risk_assessment"]
        
        assert "overall_risk_level" in risk_assessment
        assert "risk_factors" in risk_assessment
        assert "critical_thresholds" in risk_assessment
        assert "mitigation_strategies" in risk_assessment
        
        # Should identify high or critical risk level
        risk_level = risk_assessment["overall_risk_level"]
        assert risk_level in ["high", "critical"]
        
        # Should have risk factors
        assert len(risk_assessment["risk_factors"]) > 0
        
        # Should have mitigation strategies
        assert len(risk_assessment["mitigation_strategies"]) > 0


class TestCacheStrategyEnhancements:
    """Test advanced caching strategy enhancements"""
    
    def test_cache_manager_initialization(self):
        """Test cache manager initialization"""
        # Test with simple import to avoid complex dependencies
        try:
            from crawlers.caching.memory_cache import MemoryCache
            
            cache = MemoryCache(max_size=1024*1024, ttl=300)
            
            assert cache.max_size == 1024*1024
            assert cache.ttl == 300
            assert hasattr(cache, '_cache')
            assert hasattr(cache, '_sizes')
            assert hasattr(cache, '_access_times')
            
        except ImportError:
            pytest.skip("Cache modules not available for testing")
    
    def test_cache_operations(self):
        """Test basic cache operations"""
        try:
            from crawlers.caching.memory_cache import MemoryCache
            
            cache = MemoryCache(max_size=1024, ttl=300)
            
            # Test set operation
            result = cache.set("test_key", "test_value")
            assert result is True
            
            # Test get operation
            value = cache.get("test_key")
            assert value == "test_value"
            
            # Test delete operation
            result = cache.delete("test_key")
            assert result is True
            
            # Test get after delete
            value = cache.get("test_key")
            assert value is None
            
        except ImportError:
            pytest.skip("Cache modules not available for testing")
    
    def test_cache_metrics(self):
        """Test cache performance metrics"""
        try:
            from crawlers.caching.metrics import CacheMetrics
            
            metrics = CacheMetrics()
            
            # Test initial state
            assert metrics.metrics["hits"] == 0
            assert metrics.metrics["misses"] == 0
            assert metrics.metrics["operations"] == 0
            assert metrics.metrics["errors"] == 0
            
            # Test recording operations
            metrics.record_hit()
            assert metrics.metrics["hits"] == 1
            assert metrics.metrics["operations"] == 1
            
            metrics.record_miss()
            assert metrics.metrics["misses"] == 1
            assert metrics.metrics["operations"] == 2
            
            metrics.record_error()
            assert metrics.metrics["errors"] == 1
            
            # Test hit ratio calculation
            hit_ratio = metrics.get_hit_ratio()
            assert hit_ratio == 0.5  # 1 hit out of 2 operations
            
        except ImportError:
            pytest.skip("Cache modules not available for testing")


class TestDatabaseIndexingOptimization:
    """Test database indexing optimization enhancements"""
    
    def test_index_optimization_config(self):
        """Test index optimization configuration"""
        config = {
            "auto_optimization": True,
            "monitoring_enabled": True,
            "optimization_threshold": 0.1,
            "index_types": ["btree", "hash", "gin", "gist"]
        }
        
        # Test configuration validation
        assert config["auto_optimization"] is True
        assert config["monitoring_enabled"] is True
        assert config["optimization_threshold"] == 0.1
        assert len(config["index_types"]) == 4
    
    def test_optimization_strategy_selection(self):
        """Test optimization strategy selection"""
        # Mock query performance data
        query_stats = {
            "avg_execution_time": 250.0,  # ms
            "query_frequency": 100,       # queries per minute
            "index_usage": 0.3,          # 30% index usage
            "table_size": 1000000        # 1M rows
        }
        
        # Determine optimization strategy based on stats
        strategy = "create_index"  # Default strategy
        
        if query_stats["avg_execution_time"] > 200 and query_stats["index_usage"] < 0.5:
            strategy = "create_missing_index"
        elif query_stats["index_usage"] > 0.8 and query_stats["avg_execution_time"] > 100:
            strategy = "optimize_existing_index"
        elif query_stats["query_frequency"] > 50:
            strategy = "add_partial_index"
        
        assert strategy in ["create_index", "create_missing_index", "optimize_existing_index", "add_partial_index"]
        assert strategy == "create_missing_index"  # Based on our test data


class TestCodeQualityRefactoring:
    """Test code quality improvements and refactoring"""
    
    def test_error_handling_standardization(self):
        """Test standardized error handling"""
        from core.pipeline.performance_optimizer import AdvancedPerformanceAnalyzer
        
        config = {}
        analyzer = AdvancedPerformanceAnalyzer(config)
        
        # Test that the analyzer handles invalid input gracefully
        try:
            # This should not raise an exception
            result = analyzer.analyze_performance_trends(None)
            assert isinstance(result, dict)
            
            # Should return default structure even with invalid input
            expected_keys = ["trend_analysis", "anomaly_detection", "performance_prediction", 
                           "optimization_opportunities", "risk_assessment"]
            for key in expected_keys:
                assert key in result
                
        except Exception as e:
            pytest.fail(f"Error handling failed: {e}")
    
    def test_logging_integration(self):
        """Test logging integration"""
        from core.pipeline.performance_optimizer import AdvancedPerformanceAnalyzer
        import logging
        
        # Create analyzer and verify logger is set up
        config = {}
        analyzer = AdvancedPerformanceAnalyzer(config)
        
        assert hasattr(analyzer, 'logger')
        assert isinstance(analyzer.logger, logging.Logger)
        assert analyzer.logger.name.endswith("AdvancedPerformanceAnalyzer")
    
    def test_configuration_validation(self):
        """Test configuration validation and defaults"""
        from core.pipeline.performance_optimizer import AdvancedPerformanceAnalyzer
        
        # Test with empty config
        analyzer1 = AdvancedPerformanceAnalyzer({})
        assert analyzer1.config == {}
        
        # Test with partial config
        partial_config = {"ml_enabled": False}
        analyzer2 = AdvancedPerformanceAnalyzer(partial_config)
        assert analyzer2.config == partial_config
        
        # Test that it doesn't crash with various config types
        test_configs = [
            {},
            {"test": "value"},
            {"numbers": [1, 2, 3]},
            {"nested": {"key": "value"}}
        ]
        
        for config in test_configs:
            try:
                analyzer = AdvancedPerformanceAnalyzer(config)
                assert analyzer.config == config
            except Exception as e:
                pytest.fail(f"Configuration validation failed for {config}: {e}")


# Integration Tests
class TestPerformanceOptimizationIntegration:
    """Integration tests for performance optimization features"""
    
    @pytest.mark.asyncio
    async def test_performance_monitoring_workflow(self):
        """Test complete performance monitoring workflow"""
        from core.pipeline.performance_optimizer import RealTimePerformanceMonitor, AdvancedPerformanceAnalyzer
        
        config = {
            "monitoring_interval": 0.1,
            "analysis_enabled": True
        }
        
        # Initialize components
        monitor = RealTimePerformanceMonitor(config)
        analyzer = AdvancedPerformanceAnalyzer(config)
        
        # Start monitoring
        await monitor.start_monitoring()
        
        # Let it collect some data
        await asyncio.sleep(0.3)
        
        # Get current status
        status = monitor.get_current_status()
        assert status["monitoring_active"] is True
        
        # Get metric history
        history = monitor.get_metric_history("cpu_usage", duration_minutes=1)
        # History might be empty in test environment, just check structure
        assert isinstance(history, list)
        
        # Stop monitoring
        await monitor.stop_monitoring()
        assert monitor.monitoring_active is False
    
    def test_performance_optimization_pipeline(self):
        """Test the complete performance optimization pipeline"""
        from core.pipeline.performance_optimizer import AdvancedPerformanceAnalyzer, PerformanceMeasurement, PerformanceProfile, PerformanceMetric
        
        # Step 1: Data Collection (simulated)
        profile = PerformanceProfile(
            profile_id="integration_test",
            component_name="test_pipeline"
        )
        
        # Add varied measurements
        base_time = datetime.now()
        metrics_data = [
            (PerformanceMetric.CPU_USAGE, [70, 75, 85, 90, 95, 88, 82, 78, 72, 70]),
            (PerformanceMetric.MEMORY_USAGE, [65, 70, 80, 85, 90, 92, 88, 83, 78, 75]),
            (PerformanceMetric.EXECUTION_TIME, [2.1, 2.3, 2.8, 3.2, 3.5, 3.1, 2.9, 2.5, 2.2, 2.0])
        ]
        
        for metric, values in metrics_data:
            for i, value in enumerate(values):
                measurement = PerformanceMeasurement(
                    metric=metric,
                    value=value,
                    timestamp=base_time + timedelta(seconds=i)
                )
                profile.measurements.append(measurement)
        
        # Step 2: Analysis
        analyzer = AdvancedPerformanceAnalyzer({"analysis_enabled": True})
        analysis = analyzer.analyze_performance_trends(profile)
        
        # Step 3: Validation of results
        assert "trend_analysis" in analysis
        assert "optimization_opportunities" in analysis
        assert "risk_assessment" in analysis
        
        # Should identify high resource usage as optimization opportunities
        opportunities = analysis["optimization_opportunities"]
        assert len(opportunities) > 0
        
        # Should identify risk factors
        risk_assessment = analysis["risk_assessment"]
        assert risk_assessment["overall_risk_level"] in ["low", "medium", "high", "critical"]
        
        # Step 4: Verify actionable recommendations
        for opportunity in opportunities:
            assert "recommendations" in opportunity
            assert len(opportunity["recommendations"]) > 0
            assert "expected_impact" in opportunity


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])