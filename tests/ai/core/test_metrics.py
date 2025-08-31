# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Test Suite for Metrics Collection Module

Comprehensive tests for enterprise-grade metrics collection and business intelligence.
Tests metrics gathering, aggregation, and business analytics for all creator types.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

# Import the metrics module
try:
    from ai.core import metrics
    from ai.core.metrics import (
        MetricsCollector,
        MetricEntry,
        MetricType,
        MetricPriority,
        AggregationType,
        TimerContext,
        MetricsAggregator,
        BusinessMetricsTracker,
        metrics_collector,
        track_execution_time,
        track_business_metric,
        capture_errors
    )
except ImportError as e:
    pytest.skip(f"Could not import metrics module: {e}", allow_module_level=True)


class TestMetricEntry:
    """Test cases for MetricEntry class"""
    
    def test_metric_entry_creation(self):
        """Test basic metric entry creation"""
        timestamp = datetime.now()
        tags = {"user_type": "musician", "operation": "upload"}
        
        entry = MetricEntry(
            name="response_time",
            value=0.125,
            timestamp=timestamp,
            metric_type=MetricType.PERFORMANCE,
            priority=MetricPriority.HIGH,
            tags=tags,
            unit="seconds"
        )
        
        assert entry.name == "response_time"
        assert entry.value == 0.125
        assert entry.timestamp == timestamp
        assert entry.metric_type == MetricType.PERFORMANCE
        assert entry.priority == MetricPriority.HIGH
        assert entry.tags == tags
        assert entry.unit == "seconds"
        
    def test_metric_entry_defaults(self):
        """Test metric entry creation with default values"""
        entry = MetricEntry("test_metric", 42.0)
        
        assert entry.name == "test_metric"
        assert entry.value == 42.0
        assert isinstance(entry.timestamp, datetime)
        assert entry.metric_type == MetricType.COUNTER
        assert entry.priority == MetricPriority.MEDIUM
        assert entry.tags == {}
        assert entry.unit is None
        
    def test_metric_entry_serialization(self):
        """Test metric entry serialization to dictionary"""
        entry = MetricEntry(
            "cpu_usage",
            75.5,
            metric_type=MetricType.GAUGE,
            tags={"server": "web-01"},
            unit="percent"
        )
        
        entry_dict = entry.to_dict()
        
        assert entry_dict["name"] == "cpu_usage"
        assert entry_dict["value"] == 75.5
        assert entry_dict["metric_type"] == "gauge"
        assert entry_dict["priority"] == "medium"
        assert entry_dict["tags"] == {"server": "web-01"}
        assert entry_dict["unit"] == "percent"
        assert "timestamp" in entry_dict


class TestMetricsCollector:
    """Test cases for MetricsCollector class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.collector = MetricsCollector()
        
    def test_collector_initialization(self):
        """Test metrics collector initialization"""
        assert isinstance(self.collector.metrics, list)
        assert len(self.collector.metrics) == 0
        assert self.collector.max_entries == 10000
        assert self.collector.auto_flush_interval == 300
        
    def test_record_simple_metric(self):
        """Test recording a simple metric"""
        self.collector.record_metric("test_counter", 1)
        
        assert len(self.collector.metrics) == 1
        metric = self.collector.metrics[0]
        assert metric.name == "test_counter"
        assert metric.value == 1
        assert metric.metric_type == MetricType.COUNTER
        
    def test_record_metric_with_tags(self):
        """Test recording metric with tags and metadata"""
        tags = {"creator_type": "musician", "content_type": "audio"}
        
        self.collector.record_metric(
            "content_upload",
            1,
            tags=tags,
            metric_type=MetricType.COUNTER,
            priority=MetricPriority.HIGH
        )
        
        assert len(self.collector.metrics) == 1
        metric = self.collector.metrics[0]
        assert metric.tags == tags
        assert metric.metric_type == MetricType.COUNTER
        assert metric.priority == MetricPriority.HIGH
        
    def test_record_performance_metric(self):
        """Test recording performance metrics"""
        self.collector.record_performance_metric("response_time", 0.125)
        
        metric = self.collector.metrics[0]
        assert metric.name == "response_time"
        assert metric.value == 0.125
        assert metric.metric_type == MetricType.PERFORMANCE
        
    def test_record_business_metric(self):
        """Test recording business metrics"""
        self.collector.record_business_metric(
            "revenue_generated",
            250.00,
            {"creator_id": "musician_123", "content_id": "track_456"}
        )
        
        metric = self.collector.metrics[0]
        assert metric.name == "revenue_generated"
        assert metric.value == 250.00
        assert metric.metric_type == MetricType.BUSINESS
        assert metric.tags["creator_id"] == "musician_123"
        
    def test_get_metrics(self):
        """Test retrieving recorded metrics"""
        # Record multiple metrics
        self.collector.record_metric("metric1", 10)
        self.collector.record_metric("metric2", 20)
        self.collector.record_metric("metric3", 30)
        
        metrics = self.collector.get_metrics()
        assert len(metrics) == 3
        assert all(isinstance(m, MetricEntry) for m in metrics)
        
    def test_get_metrics_by_name(self):
        """Test retrieving metrics by name"""
        self.collector.record_metric("cpu_usage", 50.0)
        self.collector.record_metric("memory_usage", 75.0)
        self.collector.record_metric("cpu_usage", 60.0)
        
        cpu_metrics = self.collector.get_metrics_by_name("cpu_usage")
        assert len(cpu_metrics) == 2
        assert all(m.name == "cpu_usage" for m in cpu_metrics)
        
    def test_get_metrics_by_type(self):
        """Test retrieving metrics by type"""
        self.collector.record_metric("counter1", 1, metric_type=MetricType.COUNTER)
        self.collector.record_metric("gauge1", 50.0, metric_type=MetricType.GAUGE)
        self.collector.record_metric("counter2", 2, metric_type=MetricType.COUNTER)
        
        counter_metrics = self.collector.get_metrics_by_type(MetricType.COUNTER)
        assert len(counter_metrics) == 2
        assert all(m.metric_type == MetricType.COUNTER for m in counter_metrics)
        
    def test_get_metrics_by_tags(self):
        """Test retrieving metrics by tags"""
        tags1 = {"creator_type": "musician"}
        tags2 = {"creator_type": "photographer"}
        tags3 = {"creator_type": "musician", "content_type": "audio"}
        
        self.collector.record_metric("metric1", 1, tags=tags1)
        self.collector.record_metric("metric2", 2, tags=tags2)
        self.collector.record_metric("metric3", 3, tags=tags3)
        
        musician_metrics = self.collector.get_metrics_by_tags({"creator_type": "musician"})
        assert len(musician_metrics) == 2
        
    def test_clear_metrics(self):
        """Test clearing recorded metrics"""
        self.collector.record_metric("test1", 1)
        self.collector.record_metric("test2", 2)
        
        assert len(self.collector.metrics) == 2
        
        self.collector.clear_metrics()
        assert len(self.collector.metrics) == 0
        
    def test_max_entries_limit(self):
        """Test that metrics collection respects max entries limit"""
        # Set a small limit for testing
        self.collector.max_entries = 5
        
        # Add more metrics than the limit
        for i in range(10):
            self.collector.record_metric(f"metric_{i}", i)
            
        # Should only keep the most recent entries
        assert len(self.collector.metrics) == 5
        
        # Check that we have the latest metrics
        metric_names = [m.name for m in self.collector.metrics]
        assert "metric_9" in metric_names
        assert "metric_0" not in metric_names


class TestTimerContext:
    """Test cases for TimerContext class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.collector = MetricsCollector()
        
    def test_timer_context_basic(self):
        """Test basic timer context functionality"""
        with TimerContext(self.collector, "test_operation"):
            time.sleep(0.01)  # Sleep for 10ms
            
        metrics = self.collector.get_metrics()
        assert len(metrics) == 1
        
        timer_metric = metrics[0]
        assert timer_metric.name == "test_operation"
        assert timer_metric.value > 0.01  # Should be at least 10ms
        assert timer_metric.metric_type == MetricType.PERFORMANCE
        
    def test_timer_context_with_tags(self):
        """Test timer context with tags"""
        tags = {"operation_type": "content_validation", "creator": "musician"}
        
        with TimerContext(self.collector, "validation_time", tags=tags):
            time.sleep(0.01)
            
        timer_metric = self.collector.get_metrics()[0]
        assert timer_metric.tags == tags
        
    def test_timer_context_exception_handling(self):
        """Test timer context when exception occurs"""
        try:
            with TimerContext(self.collector, "failed_operation"):
                time.sleep(0.01)
                raise ValueError("Test exception")
        except ValueError:
            pass
            
        # Timer should still record the time even when exception occurs
        metrics = self.collector.get_metrics()
        assert len(metrics) == 1
        assert metrics[0].name == "failed_operation"
        
    def test_timer_decorator(self):
        """Test timer decorator functionality"""
        @track_execution_time(self.collector, "decorated_function")
        def test_function():
            time.sleep(0.01)
            return "result"
            
        result = test_function()
        
        assert result == "result"
        metrics = self.collector.get_metrics()
        assert len(metrics) == 1
        assert metrics[0].name == "decorated_function"


class TestMetricsAggregator:
    """Test cases for MetricsAggregator class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.collector = MetricsCollector()
        self.aggregator = MetricsAggregator(self.collector)
        
        # Add test data
        for i in range(10):
            self.collector.record_metric("response_time", i * 0.1)
            self.collector.record_metric("cpu_usage", 50 + i)
            
    def test_aggregator_initialization(self):
        """Test aggregator initialization"""
        assert self.aggregator.collector == self.collector
        
    def test_aggregate_by_name(self):
        """Test aggregating metrics by name"""
        result = self.aggregator.aggregate_by_name("response_time", AggregationType.AVERAGE)
        
        # Should be average of 0.0, 0.1, 0.2, ..., 0.9 = 0.45
        expected_avg = sum(i * 0.1 for i in range(10)) / 10
        assert abs(result - expected_avg) < 0.001
        
    def test_aggregate_sum(self):
        """Test sum aggregation"""
        result = self.aggregator.aggregate_by_name("cpu_usage", AggregationType.SUM)
        
        # Should be sum of 50, 51, 52, ..., 59
        expected_sum = sum(50 + i for i in range(10))
        assert result == expected_sum
        
    def test_aggregate_min_max(self):
        """Test min and max aggregation"""
        min_result = self.aggregator.aggregate_by_name("cpu_usage", AggregationType.MIN)
        max_result = self.aggregator.aggregate_by_name("cpu_usage", AggregationType.MAX)
        
        assert min_result == 50
        assert max_result == 59
        
    def test_aggregate_count(self):
        """Test count aggregation"""
        result = self.aggregator.aggregate_by_name("response_time", AggregationType.COUNT)
        assert result == 10
        
    def test_get_aggregated_metrics(self):
        """Test getting aggregated metrics summary"""
        summary = self.aggregator.get_aggregated_metrics()
        
        assert "response_time" in summary
        assert "cpu_usage" in summary
        
        response_stats = summary["response_time"]
        assert "count" in response_stats
        assert "average" in response_stats
        assert "min" in response_stats
        assert "max" in response_stats
        assert "sum" in response_stats
        
        assert response_stats["count"] == 10
        
    def test_aggregate_by_time_window(self):
        """Test aggregating metrics by time window"""
        # Clear existing metrics and add time-specific ones
        self.collector.clear_metrics()
        
        now = datetime.now()
        for i in range(5):
            timestamp = now - timedelta(minutes=i)
            entry = MetricEntry("requests", 1, timestamp=timestamp)
            self.collector.metrics.append(entry)
            
        # Aggregate last 3 minutes
        recent_count = self.aggregator.aggregate_by_time_window(
            "requests", 
            now - timedelta(minutes=2), 
            now,
            AggregationType.COUNT
        )
        
        assert recent_count == 3  # Should include entries from 0, 1, 2 minutes ago


class TestBusinessMetricsTracker:
    """Test cases for BusinessMetricsTracker class"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tracker = BusinessMetricsTracker()
        
    def test_track_user_upload(self):
        """Test tracking user upload events"""
        self.tracker.track_user_upload("audio", 5242880, "musician")
        
        summary = self.tracker.get_business_summary()
        
        assert summary["uploads"]["total_count"] == 1
        assert summary["uploads"]["total_size_mb"] == 5.0
        assert summary["content_types"]["audio"]["count"] == 1
        assert summary["creator_types"]["musician"]["count"] == 1
        
    def test_track_multiple_uploads(self):
        """Test tracking multiple upload events"""
        # Simulate different creator uploads
        uploads = [
            ("audio", 5242880, "musician"),      # 5MB audio by musician
            ("image", 2097152, "photographer"),  # 2MB image by photographer
            ("text", 51200, "blogger"),          # 50KB text by blogger
            ("video", 52428800, "influencer"),   # 50MB video by influencer
            ("audio", 7340032, "musician")       # 7MB audio by musician
        ]
        
        for content_type, size, creator_type in uploads:
            self.tracker.track_user_upload(content_type, size, creator_type)
            
        summary = self.tracker.get_business_summary()
        
        # Check totals
        assert summary["uploads"]["total_count"] == 5
        expected_total_mb = (5 + 2 + 0.05 + 50 + 7)  # Convert to MB
        assert abs(summary["uploads"]["total_size_mb"] - expected_total_mb) < 0.1
        
        # Check content type breakdown
        assert summary["content_types"]["audio"]["count"] == 2
        assert summary["content_types"]["image"]["count"] == 1
        assert summary["content_types"]["text"]["count"] == 1
        assert summary["content_types"]["video"]["count"] == 1
        
        # Check creator type breakdown
        assert summary["creator_types"]["musician"]["count"] == 2
        assert summary["creator_types"]["photographer"]["count"] == 1
        assert summary["creator_types"]["blogger"]["count"] == 1
        assert summary["creator_types"]["influencer"]["count"] == 1
        
    def test_track_content_processing(self):
        """Test tracking content processing stages"""
        content_id = "audio_123"
        
        # Track processing through business logic stages
        stages = [
            "upload",
            "ai_protection", 
            "seo_optimization",
            "collaboration_setup",
            "distribution"
        ]
        
        for stage in stages:
            self.tracker.track_content_processing(content_id, stage, "completed", 0.5)
            
        processing_stats = self.tracker.get_processing_statistics()
        
        assert processing_stats["total_stages_processed"] == 5
        assert processing_stats["average_stage_time"] == 0.5
        assert processing_stats["stages_completed"]["upload"] == 1
        assert processing_stats["stages_completed"]["distribution"] == 1
        
    def test_track_revenue_events(self):
        """Test tracking revenue-related events"""
        # Track revenue for different creators
        revenue_events = [
            ("musician_123", "audio_456", 15.99, "premium"),
            ("photographer_456", "image_789", 5.99, "standard"),
            ("musician_123", "audio_789", 25.99, "premium"),
            ("blogger_789", "article_123", 2.99, "basic")
        ]
        
        for creator_id, content_id, amount, tier in revenue_events:
            self.tracker.track_revenue_event(creator_id, content_id, amount, tier)
            
        revenue_stats = self.tracker.get_revenue_statistics()
        
        assert revenue_stats["total_revenue"] == 50.96
        assert revenue_stats["total_transactions"] == 4
        assert abs(revenue_stats["average_transaction"] - 12.74) < 0.01
        
        # Check tier breakdown
        assert revenue_stats["revenue_by_tier"]["premium"] == 41.98
        assert revenue_stats["revenue_by_tier"]["standard"] == 5.99
        assert revenue_stats["revenue_by_tier"]["basic"] == 2.99
        
    def test_track_collaboration_events(self):
        """Test tracking collaboration events"""
        collaboration_data = {
            "primary_creator": "musician_123",
            "collaborators": ["producer_456", "vocalist_789"],
            "content_id": "track_123",
            "collaboration_type": "music_production"
        }
        
        self.tracker.track_collaboration_event(
            collaboration_data["primary_creator"],
            collaboration_data["collaborators"],
            collaboration_data["content_id"],
            collaboration_data["collaboration_type"]
        )
        
        collab_stats = self.tracker.get_collaboration_statistics()
        
        assert collab_stats["total_collaborations"] == 1
        assert collab_stats["unique_collaborators"] == 2
        assert collab_stats["collaboration_types"]["music_production"] == 1
        
    def test_get_creator_analytics(self):
        """Test getting analytics for specific creator types"""
        # Add data for different creator types
        self.tracker.track_user_upload("audio", 5242880, "musician")
        self.tracker.track_user_upload("audio", 7340032, "musician")
        self.tracker.track_user_upload("image", 2097152, "photographer")
        
        self.tracker.track_revenue_event("musician_123", "audio_1", 15.99, "premium")
        self.tracker.track_revenue_event("musician_456", "audio_2", 25.99, "premium")
        
        musician_analytics = self.tracker.get_creator_analytics("musician")
        
        assert musician_analytics["upload_count"] == 2
        assert musician_analytics["total_content_size_mb"] == 12.0
        assert musician_analytics["revenue_generated"] == 41.98
        
        photographer_analytics = self.tracker.get_creator_analytics("photographer")
        
        assert photographer_analytics["upload_count"] == 1
        assert photographer_analytics["total_content_size_mb"] == 2.0
        assert photographer_analytics["revenue_generated"] == 0.0


class TestMetricsIntegration:
    """Test cases for metrics integration scenarios"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.collector = MetricsCollector()
        self.business_tracker = BusinessMetricsTracker()
        
    def test_end_to_end_workflow_tracking(self):
        """Test complete workflow tracking from upload to distribution"""
        # Simulate musician uploading an audio track
        creator_type = "musician"
        content_type = "audio"
        file_size = 5242880  # 5MB
        content_id = "audio_track_123"
        
        # Stage 1: Upload
        with TimerContext(self.collector, "upload_processing"):
            self.business_tracker.track_user_upload(content_type, file_size, creator_type)
            self.collector.record_business_metric("content_uploaded", 1, {
                "content_type": content_type,
                "creator_type": creator_type
            })
            
        # Stage 2: AI Protection
        with TimerContext(self.collector, "ai_protection"):
            self.business_tracker.track_content_processing(content_id, "ai_protection", "completed", 1.2)
            self.collector.record_metric("ai_protection_score", 95.5, {
                "content_id": content_id
            })
            
        # Stage 3: SEO Optimization
        with TimerContext(self.collector, "seo_optimization"):
            self.business_tracker.track_content_processing(content_id, "seo_optimization", "completed", 0.8)
            self.collector.record_metric("seo_score", 88.0, {
                "content_id": content_id
            })
            
        # Stage 4: Collaboration
        with TimerContext(self.collector, "collaboration_setup"):
            self.business_tracker.track_collaboration_event(
                "musician_123", ["producer_456"], content_id, "music_production"
            )
            
        # Stage 5: Distribution
        with TimerContext(self.collector, "distribution"):
            self.business_tracker.track_content_processing(content_id, "distribution", "completed", 0.5)
            self.collector.record_metric("platforms_distributed", 3, {
                "content_id": content_id,
                "platforms": "spotify,youtube,instagram"
            })
            
        # Verify all metrics were recorded
        metrics = self.collector.get_metrics()
        assert len(metrics) >= 8  # At least 8 metrics should be recorded
        
        # Verify business summary
        business_summary = self.business_tracker.get_business_summary()
        assert business_summary["uploads"]["total_count"] == 1
        assert business_summary["creator_types"]["musician"]["count"] == 1
        
        # Verify processing stats
        processing_stats = self.business_tracker.get_processing_statistics()
        assert processing_stats["total_stages_processed"] == 4
        
    def test_performance_monitoring_integration(self):
        """Test integration with performance monitoring"""
        # Simulate high-load scenario
        operations = [
            ("content_validation", 0.05),
            ("ai_inference", 0.8),
            ("image_processing", 0.3),
            ("seo_analysis", 0.1),
            ("database_write", 0.02)
        ]
        
        for operation, duration in operations:
            # Simulate operation timing
            start_time = time.time()
            time.sleep(duration / 10)  # Sleep for a fraction to simulate work
            actual_duration = time.time() - start_time
            
            self.collector.record_performance_metric(f"{operation}_time", actual_duration)
            self.collector.record_metric(f"{operation}_completed", 1)
            
        # Check performance metrics
        performance_metrics = self.collector.get_metrics_by_type(MetricType.PERFORMANCE)
        assert len(performance_metrics) == 5
        
        # Verify all operations completed
        completion_metrics = [m for m in self.collector.get_metrics() if m.name.endswith("_completed")]
        assert len(completion_metrics) == 5
        
    def test_error_tracking_integration(self):
        """Test error tracking with metrics"""
        # Simulate various error scenarios
        error_scenarios = [
            ("validation_error", "ContentValidationError", "format_mismatch"),
            ("ai_engine_error", "ModelConnectionError", "timeout"),
            ("security_error", "SecurityValidationError", "malicious_content"),
            ("performance_error", "PerformanceError", "memory_limit")
        ]
        
        for error_type, error_class, error_reason in error_scenarios:
            # Track error occurrence
            self.collector.record_metric("error_occurred", 1, {
                "error_type": error_type,
                "error_class": error_class,
                "error_reason": error_reason
            })
            
            # Track error recovery
            self.collector.record_metric("error_recovery_time", 0.5, {
                "error_type": error_type
            })
            
        # Verify error metrics
        error_metrics = self.collector.get_metrics_by_name("error_occurred")
        assert len(error_metrics) == 4
        
        recovery_metrics = self.collector.get_metrics_by_name("error_recovery_time")
        assert len(recovery_metrics) == 4


class TestMetricsExport:
    """Test cases for metrics export functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.collector = MetricsCollector()
        
        # Add sample data
        sample_metrics = [
            ("cpu_usage", 75.5, MetricType.GAUGE),
            ("memory_usage", 65.2, MetricType.GAUGE),
            ("requests_count", 150, MetricType.COUNTER),
            ("response_time", 0.125, MetricType.PERFORMANCE),
            ("revenue", 99.99, MetricType.BUSINESS)
        ]
        
        for name, value, metric_type in sample_metrics:
            self.collector.record_metric(name, value, metric_type=metric_type)
            
    def test_export_to_json(self):
        """Test exporting metrics to JSON format"""
        json_data = self.collector.export_metrics("json")
        
        # Should be valid JSON
        parsed_data = json.loads(json_data)
        assert isinstance(parsed_data, list)
        assert len(parsed_data) == 5
        
        # Check first metric structure
        first_metric = parsed_data[0]
        assert "name" in first_metric
        assert "value" in first_metric
        assert "timestamp" in first_metric
        assert "metric_type" in first_metric
        
    def test_export_to_csv(self):
        """Test exporting metrics to CSV format"""
        csv_data = self.collector.export_metrics("csv")
        
        lines = csv_data.strip().split('\n')
        assert len(lines) == 6  # Header + 5 data rows
        
        # Check header
        header = lines[0]
        assert "name" in header
        assert "value" in header
        assert "timestamp" in header
        
    def test_export_prometheus_format(self):
        """Test exporting metrics in Prometheus format"""
        prometheus_data = self.collector.export_metrics("prometheus")
        
        # Should contain metric declarations
        assert "cpu_usage" in prometheus_data
        assert "memory_usage" in prometheus_data
        assert "requests_count" in prometheus_data
        
        # Should contain values
        assert "75.5" in prometheus_data
        assert "65.2" in prometheus_data
        assert "150" in prometheus_data


class TestMetricsPerformance:
    """Test cases for metrics performance and scalability"""
    
    @pytest.mark.performance
    def test_high_volume_metric_collection(self, performance_tracker):
        """Test performance with high volume of metrics"""
        collector = MetricsCollector()
        
        performance_tracker.start()
        
        # Record large number of metrics
        for i in range(10000):
            collector.record_metric(f"metric_{i % 100}", i, {
                "batch": i // 1000,
                "creator_type": ["musician", "photographer", "blogger"][i % 3]
            })
            
        performance_tracker.stop()
        
        duration = performance_tracker.get_duration()
        memory_delta = performance_tracker.get_memory_delta()
        
        # Should handle 10k metrics efficiently
        assert duration < 2.0  # Under 2 seconds
        assert len(collector.metrics) == 10000
        
        # Memory usage should be reasonable
        if memory_delta is not None:
            assert memory_delta < 10  # Under 10% memory increase
            
    @pytest.mark.performance
    def test_aggregation_performance(self, performance_tracker):
        """Test performance of metrics aggregation"""
        collector = MetricsCollector()
        aggregator = MetricsAggregator(collector)
        
        # Add many metrics
        for i in range(5000):
            collector.record_metric("response_time", i * 0.001)
            
        performance_tracker.start()
        
        # Perform multiple aggregations
        for _ in range(100):
            avg = aggregator.aggregate_by_name("response_time", AggregationType.AVERAGE)
            sum_val = aggregator.aggregate_by_name("response_time", AggregationType.SUM)
            count = aggregator.aggregate_by_name("response_time", AggregationType.COUNT)
            
        performance_tracker.stop()
        
        duration = performance_tracker.get_duration()
        assert duration < 1.0  # Should complete aggregations quickly
        
    @pytest.mark.performance
    def test_export_performance(self, performance_tracker):
        """Test performance of metrics export"""
        collector = MetricsCollector()
        
        # Add substantial amount of data
        for i in range(1000):
            collector.record_metric(f"metric_{i}", i, {
                "tag1": f"value_{i}",
                "tag2": f"category_{i % 10}"
            })
            
        performance_tracker.start()
        
        # Export in different formats
        json_export = collector.export_metrics("json")
        csv_export = collector.export_metrics("csv")
        prometheus_export = collector.export_metrics("prometheus")
        
        performance_tracker.stop()
        
        duration = performance_tracker.get_duration()
        assert duration < 0.5  # Should export quickly
        
        # Verify exports are non-empty
        assert len(json_export) > 1000
        assert len(csv_export) > 1000
        assert len(prometheus_export) > 1000


class TestMetricsThreadSafety:
    """Test cases for metrics thread safety"""
    
    @pytest.mark.slow
    def test_concurrent_metric_recording(self):
        """Test thread safety of concurrent metric recording"""
        import threading
        
        collector = MetricsCollector()
        
        def record_metrics(thread_id, count):
            for i in range(count):
                collector.record_metric(f"thread_{thread_id}_metric", i, {
                    "thread_id": thread_id,
                    "iteration": i
                })
                
        # Create multiple threads
        threads = []
        metrics_per_thread = 100
        thread_count = 10
        
        for thread_id in range(thread_count):
            thread = threading.Thread(
                target=record_metrics,
                args=(thread_id, metrics_per_thread)
            )
            threads.append(thread)
            
        # Start all threads
        for thread in threads:
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Verify all metrics were recorded
        total_expected = thread_count * metrics_per_thread
        assert len(collector.metrics) == total_expected
        
        # Verify no data corruption
        thread_counts = {}
        for metric in collector.metrics:
            if "thread_id" in metric.tags:
                thread_id = metric.tags["thread_id"]
                thread_counts[thread_id] = thread_counts.get(thread_id, 0) + 1
                
        for thread_id in range(thread_count):
            assert thread_counts.get(thread_id, 0) == metrics_per_thread


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v"])
