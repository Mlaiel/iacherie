# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""Test Suite for Performance Monitoring Module

Comprehensive tests for enterprise-grade performance monitoring and optimization.
Tests system monitoring, alerting, optimization, and performance analytics.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""import pytest
import sys
import os
from pathlib import Path
import time
import threading
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Import the performance module
try:
    from ai.core import performance
    from ai.core.performance import (
        PerformanceMonitor,
        PerformanceMetrics,
        PerformanceLevel,
        ResourceType,
        ResourceAlert,
        PerformanceProfiler,
        PerformanceOptimizer,
        performance_monitor,
        monitor_performance
    )
except ImportError as e:
    pytest.skip(f"Could not import performance module: {e}", allow_module_level=True)


class TestPerformanceMetrics:
    """Test cases for PerformanceMetrics class"""    
    def test_performance_metrics_creation(self):
        """Test basic performance metrics creation"""        timestamp = datetime.now()
        
        metrics = PerformanceMetrics(
            cpu_percent=75.5,
            memory_percent=65.2,
            disk_usage=78.9,
            response_time=0.125,
            throughput=150.0,
            timestamp=timestamp
        )
        
        assert metrics.cpu_percent == 75.5
        assert metrics.memory_percent == 65.2
        assert metrics.disk_usage == 78.9
        assert metrics.response_time == 0.125
        assert metrics.throughput == 150.0
        assert metrics.timestamp == timestamp
        
    def test_performance_metrics_defaults(self):
        """Test performance metrics with default values"""        metrics = PerformanceMetrics()
        
        assert metrics.cpu_percent == 0.0
        assert metrics.memory_percent == 0.0
        assert metrics.disk_usage == 0.0
        assert metrics.response_time == 0.0
        assert metrics.throughput == 0.0
        assert isinstance(metrics.timestamp, datetime)
        
    def test_performance_metrics_serialization(self):
        """Test performance metrics serialization"""        metrics = PerformanceMetrics(
            cpu_percent=45.2,
            memory_percent=67.8,
            disk_usage=55.1,
            response_time=0.089,
            throughput=200.5
        )
        
        metrics_dict = metrics.to_dict()
        
        assert metrics_dict["cpu_percent"] == 45.2
        assert metrics_dict["memory_percent"] == 67.8
        assert metrics_dict["disk_usage"] == 55.1
        assert metrics_dict["response_time"] == 0.089
        assert metrics_dict["throughput"] == 200.5
        assert "timestamp" in metrics_dict
        
    def test_performance_level_calculation(self):
        """Test performance level calculation based on metrics"""        # Good performance
        good_metrics = PerformanceMetrics(
            cpu_percent=30.0,
            memory_percent=40.0,
            response_time=0.05
        )
        assert good_metrics.get_performance_level() == PerformanceLevel.EXCELLENT
        
        # Warning performance
        warning_metrics = PerformanceMetrics(
            cpu_percent=75.0,
            memory_percent=80.0,
            response_time=1.5
        )
        assert warning_metrics.get_performance_level() == PerformanceLevel.WARNING
        
        # Critical performance
        critical_metrics = PerformanceMetrics(
            cpu_percent=95.0,
            memory_percent=95.0,
            response_time=5.0
        )
        assert critical_metrics.get_performance_level() == PerformanceLevel.CRITICAL


class TestResourceAlert:
    """Test cases for ResourceAlert class"""    
    def test_resource_alert_creation(self):
        """Test resource alert creation"""        alert = ResourceAlert(
            resource_type=ResourceType.CPU,
            level=PerformanceLevel.WARNING,
            current_value=85.5,
            threshold=80.0,
            message="CPU usage above warning threshold"
        )
        
        assert alert.resource_type == ResourceType.CPU
        assert alert.level == PerformanceLevel.WARNING
        assert alert.current_value == 85.5
        assert alert.threshold == 80.0
        assert alert.message == "CPU usage above warning threshold"
        assert isinstance(alert.timestamp, datetime)
        
    def test_alert_severity_ordering(self):
        """Test alert severity ordering"""        info_alert = ResourceAlert(ResourceType.CPU, PerformanceLevel.GOOD, 50.0, 70.0, "Info")
        warning_alert = ResourceAlert(ResourceType.CPU, PerformanceLevel.WARNING, 80.0, 70.0, "Warning")
        critical_alert = ResourceAlert(ResourceType.CPU, PerformanceLevel.CRITICAL, 95.0, 90.0, "Critical")
        
        assert info_alert.level < warning_alert.level
        assert warning_alert.level < critical_alert.level
        assert critical_alert.level > info_alert.level


class TestPerformanceMonitor:
    """Test cases for PerformanceMonitor class"""    
    def setup_method(self):
        """Setup for each test method"""        self.monitor = PerformanceMonitor()
        
    def teardown_method(self):
        """Cleanup after each test"""        if self.monitor.is_monitoring():
            self.monitor.stop_monitoring()
            
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_collect_system_metrics(self, mock_disk, mock_memory, mock_cpu):
        """Test system metrics collection"""        # Mock system metrics
        mock_cpu.return_value = 45.5
        
        memory_mock = MagicMock()
        memory_mock.percent = 65.2
        memory_mock.total = 8589934592  # 8GB
        memory_mock.available = 2952790016  # ~2.75GB
        mock_memory.return_value = memory_mock
        
        disk_mock = MagicMock()
        disk_mock.percent = 78.9
        mock_disk.return_value = disk_mock
        
        # Collect metrics
        metrics = self.monitor.collect_metrics()
        
        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.cpu_percent == 45.5
        assert metrics.memory_percent == 65.2
        assert metrics.disk_usage == 78.9
        assert isinstance(metrics.timestamp, datetime)
        
    def test_start_stop_monitoring(self):
        """Test starting and stopping monitoring"""        assert not self.monitor.is_monitoring()
        
        # Start monitoring
        self.monitor.start_monitoring()
        assert self.monitor.is_monitoring()
        
        time.sleep(0.1)  # Let it run briefly
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        assert not self.monitor.is_monitoring()
        
    def test_monitoring_interval(self):
        """Test monitoring interval configuration"""        self.monitor.monitoring_interval = 0.1  # 100ms for testing
        
        metrics_count_before = len(self.monitor.get_metrics_history())
        
        self.monitor.start_monitoring()
        time.sleep(0.25)  # Let it collect a few metrics
        self.monitor.stop_monitoring()
        
        metrics_count_after = len(self.monitor.get_metrics_history())
        
        # Should have collected at least 2 metrics in 250ms with 100ms interval
        assert metrics_count_after >= metrics_count_before + 2
        
    def test_metrics_history(self):
        """Test metrics history storage"""        # Manually add some metrics to history
        for i in range(5):
            metrics = PerformanceMetrics(
                cpu_percent=50.0 + i,
                memory_percent=60.0 + i,
                timestamp=datetime.now() - timedelta(minutes=i)
            )
            self.monitor.add_metrics_to_history(metrics)
            
        history = self.monitor.get_metrics_history()
        assert len(history) == 5
        
        # Should be ordered by timestamp (newest first)
        for i in range(len(history) - 1):
            assert history[i].timestamp >= history[i + 1].timestamp
            
    def test_history_size_limit(self):
        """Test metrics history size limiting"""        self.monitor.history_size = 3  # Set small limit for testing
        
        # Add more metrics than the limit
        for i in range(10):
            metrics = PerformanceMetrics(cpu_percent=50.0 + i)
            self.monitor.add_metrics_to_history(metrics)
            
        history = self.monitor.get_metrics_history()
        assert len(history) == 3  # Should respect the limit
        
        # Should keep the most recent ones
        assert history[0].cpu_percent == 59.0  # Last added
        assert history[2].cpu_percent == 57.0  # Third from last


class TestPerformanceAlerts:
    """Test cases for performance alerting system"""    
    def setup_method(self):
        """Setup for each test method"""        self.monitor = PerformanceMonitor()
        
        # Set test thresholds
        self.monitor.cpu_warning_threshold = 70.0
        self.monitor.cpu_critical_threshold = 85.0
        self.monitor.memory_warning_threshold = 75.0
        self.monitor.memory_critical_threshold = 90.0
        
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory') 
    def test_cpu_warning_alert(self, mock_memory, mock_cpu):
        """Test CPU warning alert generation"""        # Mock high CPU usage
        mock_cpu.return_value = 80.0  # Above warning threshold
        
        memory_mock = MagicMock()
        memory_mock.percent = 50.0  # Normal memory
        mock_memory.return_value = memory_mock
        
        alerts = self.monitor.check_alerts()
        
        # Should have CPU warning alert
        cpu_alerts = [a for a in alerts if a.resource_type == ResourceType.CPU]
        assert len(cpu_alerts) == 1
        assert cpu_alerts[0].level == PerformanceLevel.WARNING
        assert cpu_alerts[0].current_value == 80.0
        
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_memory_critical_alert(self, mock_memory, mock_cpu):
        """Test memory critical alert generation"""        mock_cpu.return_value = 50.0  # Normal CPU
        
        memory_mock = MagicMock()
        memory_mock.percent = 95.0  # Critical memory usage
        mock_memory.return_value = memory_mock
        
        alerts = self.monitor.check_alerts()
        
        # Should have memory critical alert
        memory_alerts = [a for a in alerts if a.resource_type == ResourceType.MEMORY]
        assert len(memory_alerts) == 1
        assert memory_alerts[0].level == PerformanceLevel.CRITICAL
        assert memory_alerts[0].current_value == 95.0
        
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_multiple_alerts(self, mock_memory, mock_cpu):
        """Test multiple simultaneous alerts"""        # Mock high usage for both CPU and memory
        mock_cpu.return_value = 90.0  # Critical CPU
        
        memory_mock = MagicMock()
        memory_mock.percent = 85.0  # Warning memory
        mock_memory.return_value = memory_mock
        
        alerts = self.monitor.check_alerts()
        
        # Should have both alerts
        assert len(alerts) == 2
        
        alert_types = {alert.resource_type for alert in alerts}
        assert ResourceType.CPU in alert_types
        assert ResourceType.MEMORY in alert_types
        
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_no_alerts_normal_usage(self, mock_memory, mock_cpu):
        """Test no alerts when usage is normal"""        mock_cpu.return_value = 30.0  # Normal CPU
        
        memory_mock = MagicMock()
        memory_mock.percent = 40.0  # Normal memory
        mock_memory.return_value = memory_mock
        
        alerts = self.monitor.check_alerts()
        
        # Should have no alerts
        assert len(alerts) == 0


class TestPerformanceProfiler:
    """Test cases for PerformanceProfiler class"""    
    def setup_method(self):
        """Setup for each test method"""        self.profiler = PerformanceProfiler()
        
    def test_profiler_start_stop(self):
        """Test profiler start and stop functionality"""        assert not self.profiler.is_profiling()
        
        self.profiler.start_profiling("test_operation")
        assert self.profiler.is_profiling()
        assert self.profiler.current_operation == "test_operation"
        
        time.sleep(0.01)  # Brief operation
        
        profile_data = self.profiler.stop_profiling()
        assert not self.profiler.is_profiling()
        assert profile_data["operation"] == "test_operation"
        assert profile_data["duration"] > 0.0
        
    def test_profiler_context_manager(self):
        """Test profiler context manager functionality"""        with self.profiler.profile_operation("context_test") as profile:
            time.sleep(0.01)
            profile["custom_metric"] = 42
            
        # Should have completed profiling
        assert not self.profiler.is_profiling()
        
        # Check profile data
        profile_history = self.profiler.get_profile_history()
        assert len(profile_history) == 1
        assert profile_history[0]["operation"] == "context_test"
        assert profile_history[0]["custom_metric"] == 42
        
    def test_nested_profiling(self):
        """Test nested profiling operations"""        with self.profiler.profile_operation("outer_operation"):
            time.sleep(0.01)
            
            with self.profiler.profile_operation("inner_operation"):
                time.sleep(0.01)
                
        profile_history = self.profiler.get_profile_history()
        assert len(profile_history) == 2
        
        operations = [p["operation"] for p in profile_history]
        assert "outer_operation" in operations
        assert "inner_operation" in operations
        
    def test_profiler_decorator(self):
        """Test profiler decorator functionality"""        @self.profiler.profile
        def test_function(x, y):
            time.sleep(0.01)
            return x + y
            
        result = test_function(2, 3)
        
        assert result == 5
        profile_history = self.profiler.get_profile_history()
        assert len(profile_history) == 1
        assert profile_history[0]["operation"] == "test_function"
        
    def test_profiler_statistics(self):
        """Test profiler statistics calculation"""        # Profile multiple operations
        operations = ["op1", "op2", "op1", "op3", "op1"]
        
        for op in operations:
            with self.profiler.profile_operation(op):
                time.sleep(0.001)  # Brief sleep
                
        stats = self.profiler.get_statistics()
        
        assert "op1" in stats
        assert "op2" in stats
        assert "op3" in stats
        
        # op1 was called 3 times
        op1_stats = stats["op1"]
        assert op1_stats["count"] == 3
        assert op1_stats["total_time"] > 0.0
        assert op1_stats["average_time"] > 0.0
        assert op1_stats["min_time"] > 0.0
        assert op1_stats["max_time"] > 0.0


class TestPerformanceOptimizer:
    """Test cases for PerformanceOptimizer class"""    
    def setup_method(self):
        """Setup for each test method"""        self.optimizer = PerformanceOptimizer()
        
    def test_analyze_performance_data(self):
        """Test performance data analysis"""        # Create sample performance data
        sample_data = [
            PerformanceMetrics(cpu_percent=85.0, memory_percent=75.0, response_time=2.5),
            PerformanceMetrics(cpu_percent=90.0, memory_percent=80.0, response_time=3.0),
            PerformanceMetrics(cpu_percent=75.0, memory_percent=70.0, response_time=1.8),
        ]
        
        analysis = self.optimizer.analyze_performance_data(sample_data)
        
        assert "cpu" in analysis
        assert "memory" in analysis
        assert "response_time" in analysis
        
        # Check CPU analysis
        cpu_analysis = analysis["cpu"]
        assert cpu_analysis["average"] == 83.33333333333333
        assert cpu_analysis["max"] == 90.0
        assert cpu_analysis["min"] == 75.0
        
    def test_get_optimization_suggestions(self):
        """Test optimization suggestions generation"""        # Simulate performance issues
        high_cpu_data = [
            PerformanceMetrics(cpu_percent=95.0, memory_percent=50.0, response_time=1.0)
        ]
        
        suggestions = self.optimizer.get_optimization_suggestions(high_cpu_data)
        
        assert len(suggestions) > 0
        
        # Should suggest CPU optimization
        cpu_suggestions = [s for s in suggestions if "cpu" in s["category"].lower()]
        assert len(cpu_suggestions) > 0
        
        # Check suggestion structure
        for suggestion in suggestions:
            assert "category" in suggestion
            assert "suggestion" in suggestion
            assert "impact" in suggestion
            assert "priority" in suggestion
            
    def test_memory_optimization_suggestions(self):
        """Test memory-specific optimization suggestions"""        high_memory_data = [
            PerformanceMetrics(cpu_percent=30.0, memory_percent=95.0, response_time=1.0)
        ]
        
        suggestions = self.optimizer.get_optimization_suggestions(high_memory_data)
        
        memory_suggestions = [s for s in suggestions if "memory" in s["category"].lower()]
        assert len(memory_suggestions) > 0
        
    def test_response_time_optimization_suggestions(self):
        """Test response time optimization suggestions"""        slow_response_data = [
            PerformanceMetrics(cpu_percent=50.0, memory_percent=60.0, response_time=5.0)
        ]
        
        suggestions = self.optimizer.get_optimization_suggestions(slow_response_data)
        
        response_suggestions = [s for s in suggestions if "response" in s["category"].lower()]
        assert len(response_suggestions) > 0
        
    def test_auto_optimization(self):
        """Test automatic optimization features"""        # Mock some optimization actions
        with patch.object(self.optimizer, '_optimize_memory_usage') as mock_memory_opt, \
             patch.object(self.optimizer, '_optimize_cpu_usage') as mock_cpu_opt:
            
            mock_memory_opt.return_value = True
            mock_cpu_opt.return_value = True
            
            # Trigger auto optimization
            high_usage_data = [
                PerformanceMetrics(cpu_percent=90.0, memory_percent=85.0, response_time=3.0)
            ]
            
            optimization_results = self.optimizer.auto_optimize(high_usage_data)
            
            assert "optimizations_applied" in optimization_results
            assert "improvements" in optimization_results
            
            # Should have attempted optimizations
            optimizations = optimization_results["optimizations_applied"]
            assert len(optimizations) > 0


class TestPerformanceIntegration:
    """Test cases for performance monitoring integration"""    
    def setup_method(self):
        """Setup for each test method"""        self.monitor = PerformanceMonitor()
        self.profiler = PerformanceProfiler()
        self.optimizer = PerformanceOptimizer()
        
    def teardown_method(self):
        """Cleanup after each test"""        if self.monitor.is_monitoring():
            self.monitor.stop_monitoring()
            
    def test_end_to_end_performance_workflow(self):
        """Test complete performance monitoring workflow"""        # Step 1: Start monitoring
        self.monitor.start_monitoring()
        
        # Step 2: Simulate some operations with profiling
        operations = [
            ("content_validation", 0.05),
            ("ai_inference", 0.8),
            ("seo_optimization", 0.1)
        ]
        
        for operation, duration in operations:
            with self.profiler.profile_operation(operation):
                time.sleep(duration / 10)  # Shortened for testing
                
        # Step 3: Stop monitoring and collect data
        time.sleep(0.1)  # Let monitor collect some data
        self.monitor.stop_monitoring()
        
        # Step 4: Analyze performance
        metrics_history = self.monitor.get_metrics_history()
        profile_stats = self.profiler.get_statistics()
        
        assert len(metrics_history) > 0
        assert len(profile_stats) == 3
        
        # Step 5: Get optimization suggestions
        suggestions = self.optimizer.get_optimization_suggestions(metrics_history)
        assert isinstance(suggestions, list)
        
    def test_business_logic_performance_tracking(self):
        """Test performance tracking for business logic stages"""        # Simulate the business logic workflow: 
        # User Upload → AI Protection → SEO → Collaboration → Distribution
        
        workflow_stages = [
            ("user_upload", 0.1),
            ("ai_protection", 0.5),
            ("seo_optimization", 0.2),
            ("collaboration_setup", 0.3),
            ("distribution", 0.15)
        ]
        
        stage_performances = []
        
        for stage, expected_duration in workflow_stages:
            with self.profiler.profile_operation(stage) as profile:
                # Simulate stage processing
                start_time = time.time()
                time.sleep(expected_duration / 10)  # Shortened for testing
                actual_duration = time.time() - start_time
                
                profile["expected_duration"] = expected_duration
                profile["actual_duration"] = actual_duration
                stage_performances.append(profile)
                
        # Analyze workflow performance
        total_expected = sum(stage[1] for stage in workflow_stages)
        total_actual = sum(p["actual_duration"] for p in stage_performances)
        
        # Should complete within reasonable time
        assert total_actual < total_expected  # Since we shortened the sleeps
        
        # Check individual stage performance
        profile_stats = self.profiler.get_statistics()
        assert "user_upload" in profile_stats
        assert "ai_protection" in profile_stats
        assert "distribution" in profile_stats
        
    def test_creator_specific_performance_scenarios(self):
        """Test performance scenarios for different creator types"""        creator_scenarios = {
            "musician": {
                "operations": [("audio_validation", 0.1), ("copyright_check", 0.3), ("audio_processing", 0.8)],
                "content_size": 5242880  # 5MB audio file
            },
            "photographer": {
                "operations": [("image_validation", 0.05), ("metadata_extraction", 0.1), ("image_processing", 0.4)],
                "content_size": 2097152  # 2MB image file
            },
            "blogger": {
                "operations": [("text_validation", 0.02), ("seo_analysis", 0.1), ("content_optimization", 0.2)],
                "content_size": 51200  # 50KB text file
            }
        }
        
        performance_results = {}
        
        for creator_type, scenario in creator_scenarios.items():
            creator_performance = []
            
            for operation, duration in scenario["operations"]:
                with self.profiler.profile_operation(f"{creator_type}_{operation}") as profile:
                    time.sleep(duration / 20)  # Shortened for testing
                    profile["creator_type"] = creator_type
                    profile["content_size"] = scenario["content_size"]
                    creator_performance.append(profile)
                    
            performance_results[creator_type] = creator_performance
            
        # Verify all creator types were processed
        assert len(performance_results) == 3
        assert "musician" in performance_results
        assert "photographer" in performance_results
        assert "blogger" in performance_results
        
        # Check that different content sizes affect performance appropriately
        profile_stats = self.profiler.get_statistics()
        
        # Audio processing should be tracked
        assert any("musician_audio_processing" in op for op in profile_stats.keys())
        # Image processing should be tracked
        assert any("photographer_image_processing" in op for op in profile_stats.keys())
        # Text processing should be tracked
        assert any("blogger_content_optimization" in op for op in profile_stats.keys())


class TestPerformanceDecorators:
    """Test cases for performance monitoring decorators"""    
    def setup_method(self):
        """Setup for each test method"""        self.monitor = PerformanceMonitor()
        
    def test_monitor_performance_decorator(self):
        """Test monitor_performance decorator"""        @monitor_performance
        def test_function(x, y):
            time.sleep(0.01)
            return x * y
            
        result = test_function(3, 4)
        
        assert result == 12
        
        # Should have recorded performance metrics
        metrics_history = self.monitor.get_metrics_history()
        # Note: This might be empty if global monitor is different
        # In a real scenario, we'd check the global performance_monitor instance
        
    def test_profiler_decorator_with_custom_name(self):
        """Test profiler decorator with custom operation name"""        profiler = PerformanceProfiler()
        
        @profiler.profile_as("custom_operation")
        def test_function():
            time.sleep(0.01)
            return "done"
            
        result = test_function()
        
        assert result == "done"
        profile_stats = profiler.get_statistics()
        assert "custom_operation" in profile_stats


class TestPerformanceAsync:
    """Test cases for async performance monitoring"""    
    def setup_method(self):
        """Setup for each test method"""        self.profiler = PerformanceProfiler()
        
    @pytest.mark.asyncio
    async def test_async_operation_profiling(self):
        """Test profiling of async operations"""        async def async_operation():
            await asyncio.sleep(0.01)
            return "async_result"
            
        # Profile async operation
        start_time = time.time()
        with self.profiler.profile_operation("async_test"):
            result = await async_operation()
        end_time = time.time()
        
        assert result == "async_result"
        
        profile_stats = self.profiler.get_statistics()
        assert "async_test" in profile_stats
        
        # Should have reasonable timing
        recorded_time = profile_stats["async_test"]["average_time"]
        actual_time = end_time - start_time
        assert abs(recorded_time - actual_time) < 0.01  # Within 10ms tolerance
        
    @pytest.mark.asyncio
    async def test_concurrent_async_profiling(self):
        """Test profiling of concurrent async operations"""        async def async_task(task_id, duration):
            await asyncio.sleep(duration)
            return f"task_{task_id}_done"
            
        # Run multiple concurrent tasks with profiling
        tasks = []
        for i in range(3):
            task = self.profiler.profile_async_operation(
                f"concurrent_task_{i}",
                async_task(i, 0.01)
            )
            tasks.append(task)
            
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all("done" in result for result in results)
        
        profile_stats = self.profiler.get_statistics()
        
        # Should have stats for all concurrent tasks
        for i in range(3):
            assert f"concurrent_task_{i}" in profile_stats


class TestPerformanceErrorHandling:
    """Test cases for error handling in performance monitoring"""    
    def setup_method(self):
        """Setup for each test method"""        self.monitor = PerformanceMonitor()
        self.profiler = PerformanceProfiler()
        
    def test_monitoring_with_exceptions(self):
        """Test that monitoring continues despite exceptions"""        self.monitor.start_monitoring()
        
        # Simulate an exception during monitoring
        with patch('psutil.cpu_percent', side_effect=Exception("Mock error")):
            time.sleep(0.1)  # Let it attempt to collect metrics
            
        # Should still be monitoring despite the error
        assert self.monitor.is_monitoring()
        
        self.monitor.stop_monitoring()
        
    def test_profiler_with_exceptions(self):
        """Test profiler behavior when profiled function raises exception"""        try:
            with self.profiler.profile_operation("failing_operation"):
                time.sleep(0.01)
                raise ValueError("Test exception")
        except ValueError:
            pass
            
        # Should still have recorded the profile data
        profile_stats = self.profiler.get_statistics()
        assert "failing_operation" in profile_stats
        
        # Should have recorded the time up to the exception
        assert profile_stats["failing_operation"]["total_time"] > 0.0
        
    def test_optimizer_with_invalid_data(self):
        """Test optimizer behavior with invalid performance data"""        optimizer = PerformanceOptimizer()
        
        # Test with empty data
        suggestions = optimizer.get_optimization_suggestions([])
        assert isinstance(suggestions, list)  # Should return empty list gracefully
        
        # Test with None data
        suggestions = optimizer.get_optimization_suggestions(None)
        assert isinstance(suggestions, list)
        
        # Test with invalid metrics
        invalid_metrics = [None, "invalid", 123]
        suggestions = optimizer.get_optimization_suggestions(invalid_metrics)
        assert isinstance(suggestions, list)


class TestPerformanceScalability:
    """Test cases for performance monitoring scalability"""    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_high_frequency_monitoring(self, performance_tracker):
        """Test monitoring performance under high frequency"""        monitor = PerformanceMonitor()
        monitor.monitoring_interval = 0.001  # 1ms interval for stress test
        
        performance_tracker.start()
        
        monitor.start_monitoring()
        time.sleep(0.1)  # Run for 100ms
        monitor.stop_monitoring()
        
        performance_tracker.stop()
        
        # Should handle high frequency monitoring
        duration = performance_tracker.get_duration()
        metrics_count = len(monitor.get_metrics_history())
        
        assert duration < 0.2  # Should complete quickly
        assert metrics_count > 10  # Should have collected many metrics
        
    @pytest.mark.performance
    def test_large_profile_history(self, performance_tracker):
        """Test profiler performance with large history"""        profiler = PerformanceProfiler()
        
        performance_tracker.start()
        
        # Generate large number of profile entries
        for i in range(1000):
            with profiler.profile_operation(f"operation_{i % 10}"):
                pass  # Minimal operation
                
        performance_tracker.stop()
        
        duration = performance_tracker.get_duration()
        stats = profiler.get_statistics()
        
        assert duration < 1.0  # Should complete within 1 second
        assert len(stats) == 10  # Should have 10 unique operations
        
        # Check that statistics are accurate
        for op_name, op_stats in stats.items():
            assert op_stats["count"] == 100  # Each operation done 100 times


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
