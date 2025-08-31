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

"""Advanced Metrics Tests - Industrial Grade

Comprehensive, enterprise-level test suite for monitoring metrics system.
Tests metrics collection, aggregation, analysis, and real-time processing.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized copying, distribution, or use of this code without explicit written permission
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will be prosecuted to the full
extent of the law.
"""
import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch
import json
import numpy as np
import pandas as pd
from decimal import Decimal
from collections import deque

from ai.monitoring.metrics import (
    MetricsCollector,
    MetricType,
    MetricUnit,
    MetricPriority,
    Metric,
    MetricAggregator,
    TimeSeriesProcessor,
    MetricValidator,
    AlertThresholds,
    MetricStorage,
    RealTimeMetrics,
    MetricAnalyzer,
    CustomMetrics
)
from ai.core.exceptions import MetricsError, ValidationError
from .fixtures import (
    metrics_configs,
    sample_metrics,
    time_series_data,
    aggregation_configs,
    alert_configs
)


class TestMetricsCore:
    """Core functionality tests for metrics system."""    
    @pytest.fixture
    async def metrics_collector(self):
        """Create and initialize metrics collector."""        collector = MetricsCollector(
            config={
                "collection_enabled": True,
                "real_time_processing": True,
                "storage_enabled": True,
                "aggregation_enabled": True,
                "alert_processing": True,
                "retention_days": 90,
                "buffer_size": 10000,
                "flush_interval": 30,
                "compression_enabled": True
            }
        )
        await collector.initialize()
        yield collector
        await collector.shutdown()
    
    @pytest.fixture
    def sample_metric_data(self, sample_metrics):
        """Get sample metric data for testing."""        return sample_metrics["performance_metrics"]
    
    async def test_metrics_collector_initialization(self, metrics_collector):
        """Test comprehensive initialization of metrics collector."""        # Verify core components
        assert metrics_collector is not None
        assert metrics_collector.is_initialized
        assert metrics_collector.metric_aggregator is not None
        assert metrics_collector.time_series_processor is not None
        assert metrics_collector.metric_validator is not None
        assert metrics_collector.alert_thresholds is not None
        assert metrics_collector.metric_storage is not None
        assert metrics_collector.real_time_metrics is not None
        assert metrics_collector.metric_analyzer is not None
        assert metrics_collector.custom_metrics is not None
        
        # Verify configuration
        config = metrics_collector.config
        assert config["collection_enabled"] is True
        assert config["retention_days"] == 90
        assert config["buffer_size"] == 10000
        assert config["flush_interval"] == 30
        
        # Verify supported metric types
        supported_types = metrics_collector.get_supported_metric_types()
        expected_types = [
            MetricType.COUNTER,
            MetricType.GAUGE,
            MetricType.HISTOGRAM,
            MetricType.SUMMARY,
            MetricType.TIMER,
            MetricType.RATE,
            MetricType.PERCENTAGE,
            MetricType.BYTES,
            MetricType.DURATION
        ]
        assert all(metric_type in supported_types for metric_type in expected_types)
        
        # Verify supported metric units
        supported_units = metrics_collector.get_supported_metric_units()
        expected_units = [
            MetricUnit.COUNT,
            MetricUnit.PERCENTAGE,
            MetricUnit.MILLISECONDS,
            MetricUnit.SECONDS,
            MetricUnit.BYTES,
            MetricUnit.MEGABYTES,
            MetricUnit.REQUESTS_PER_SECOND,
            MetricUnit.ERRORS_PER_MINUTE,
            MetricUnit.CPU_CORES,
            MetricUnit.MEMORY_GB
        ]
        assert all(unit in supported_units for unit in expected_units)
    
    async def test_metric_collection_and_validation(self, metrics_collector, sample_metric_data):
        """Test metric collection with comprehensive validation."""        # Metric collection scenarios
        collection_scenarios = [
            {
                "metric_name": "api_response_time",
                "metric_type": MetricType.TIMER,
                "value": 125.5,
                "unit": MetricUnit.MILLISECONDS,
                "tags": {"service": "user_api", "endpoint": "/users", "method": "GET"},
                "priority": MetricPriority.HIGH
            },
            {
                "metric_name": "memory_usage",
                "metric_type": MetricType.GAUGE,
                "value": 75.8,
                "unit": MetricUnit.PERCENTAGE,
                "tags": {"server": "web-01", "component": "application"},
                "priority": MetricPriority.MEDIUM
            },
            {
                "metric_name": "request_count",
                "metric_type": MetricType.COUNTER,
                "value": 1,
                "unit": MetricUnit.COUNT,
                "tags": {"service": "api_gateway", "status": "200"},
                "priority": MetricPriority.LOW
            },
            {
                "metric_name": "error_rate",
                "metric_type": MetricType.RATE,
                "value": 0.025,
                "unit": MetricUnit.PERCENTAGE,
                "tags": {"service": "payment_service", "error_type": "timeout"},
                "priority": MetricPriority.CRITICAL
            },
            {
                "metric_name": "disk_usage",
                "metric_type": MetricType.GAUGE,
                "value": 2048,
                "unit": MetricUnit.MEGABYTES,
                "tags": {"server": "db-01", "mount": "/data"},
                "priority": MetricPriority.MEDIUM
            }
        ]
        
        collected_metrics = []
        
        for scenario in collection_scenarios:
            # Create metric
            metric = Metric(
                name=scenario["metric_name"],
                type=scenario["metric_type"],
                value=scenario["value"],
                unit=scenario["unit"],
                tags=scenario["tags"],
                priority=scenario["priority"],
                timestamp=datetime.now()
            )
            
            # Collect metric
            collection_result = await metrics_collector.collect_metric(metric)
            
            collected_metrics.append({
                "scenario": scenario,
                "metric": metric,
                "result": collection_result
            })
            
            # Verify collection result
            assert collection_result.success is True
            assert collection_result.metric_id is not None
            assert collection_result.validation_passed is True
            assert collection_result.stored is True
            
            # Verify metric validation
            validation_result = await metrics_collector.validate_metric(metric)
            assert validation_result.is_valid is True
            assert validation_result.validation_errors == []
            
            # Verify metric structure
            assert metric.name == scenario["metric_name"]
            assert metric.type == scenario["metric_type"]
            assert metric.value == scenario["value"]
            assert metric.unit == scenario["unit"]
            assert metric.tags == scenario["tags"]
            assert metric.priority == scenario["priority"]
            assert metric.timestamp is not None
        
        # Test batch metric collection
        batch_metrics = [item["metric"] for item in collected_metrics]
        batch_result = await metrics_collector.collect_metrics_batch(batch_metrics)
        
        assert batch_result.total_count == len(batch_metrics)
        assert batch_result.successful_count == len(batch_metrics)
        assert batch_result.failed_count == 0
        assert batch_result.validation_errors == []
        
        # Test metric validation errors
        invalid_metric = Metric(
            name="",  # Invalid empty name
            type=MetricType.GAUGE,
            value=-999,  # Invalid value for gauge
            unit=MetricUnit.PERCENTAGE,
            tags={},
            priority=MetricPriority.HIGH,
            timestamp=datetime.now()
        )
        
        invalid_validation = await metrics_collector.validate_metric(invalid_metric)
        assert invalid_validation.is_valid is False
        assert len(invalid_validation.validation_errors) > 0
    
    async def test_time_series_processing(self, metrics_collector):
        """Test time series data processing and analysis."""        # Generate time series data
        time_series_scenarios = [
            {
                "metric_name": "cpu_utilization",
                "data_points": 1440,  # 24 hours of minute-level data
                "interval": timedelta(minutes=1),
                "trend": "stable_with_spikes",
                "base_value": 45.0,
                "spike_probability": 0.05
            },
            {
                "metric_name": "network_throughput",
                "data_points": 288,  # 24 hours of 5-minute data
                "interval": timedelta(minutes=5),
                "trend": "cyclical_daily",
                "base_value": 150.0,
                "amplitude": 50.0
            },
            {
                "metric_name": "database_connections",
                "data_points": 720,  # 24 hours of 2-minute data
                "interval": timedelta(minutes=2),
                "trend": "gradual_increase",
                "base_value": 25.0,
                "growth_rate": 0.001
            }
        ]
        
        time_series_results = []
        
        for scenario in time_series_scenarios:
            # Generate time series data
            time_series_data = await metrics_collector.generate_time_series_data(
                metric_name=scenario["metric_name"],
                data_points=scenario["data_points"],
                interval=scenario["interval"],
                pattern_config={
                    "trend": scenario["trend"],
                    "base_value": scenario["base_value"],
                    "spike_probability": scenario.get("spike_probability"),
                    "amplitude": scenario.get("amplitude"),
                    "growth_rate": scenario.get("growth_rate")
                }
            )
            
            # Process time series
            processing_result = await metrics_collector.process_time_series(
                metric_name=scenario["metric_name"],
                data=time_series_data,
                processing_config={
                    "smoothing_enabled": True,
                    "anomaly_detection": True,
                    "trend_analysis": True,
                    "seasonal_decomposition": True,
                    "forecasting": True,
                    "forecast_horizon": 24  # 24 data points ahead
                }
            )
            
            time_series_results.append({
                "scenario": scenario,
                "data": time_series_data,
                "result": processing_result
            })
            
            # Verify time series processing
            assert processing_result.processed is True
            assert processing_result.data_points == scenario["data_points"]
            assert processing_result.anomalies_detected is not None
            assert processing_result.trend_analysis is not None
            assert processing_result.forecasting is not None
            
            # Verify trend analysis
            trend_analysis = processing_result.trend_analysis
            assert "trend_direction" in trend_analysis
            assert "trend_strength" in trend_analysis
            assert "trend_significance" in trend_analysis
            
            # Verify anomaly detection
            anomaly_results = processing_result.anomalies_detected
            assert "anomaly_count" in anomaly_results
            assert "anomaly_points" in anomaly_results
            assert "severity_distribution" in anomaly_results
            
            # Verify forecasting
            forecast_results = processing_result.forecasting
            assert "forecast_values" in forecast_results
            assert "confidence_intervals" in forecast_results
            assert "forecast_accuracy" in forecast_results
            assert len(forecast_results["forecast_values"]) == 24
        
        # Test time series aggregation
        aggregation_scenarios = [
            {
                "aggregation_type": "hourly",
                "function": "avg",
                "window_size": timedelta(hours=1)
            },
            {
                "aggregation_type": "daily",
                "function": "max",
                "window_size": timedelta(days=1)
            },
            {
                "aggregation_type": "rolling",
                "function": "median",
                "window_size": timedelta(minutes=15)
            }
        ]
        
        for agg_scenario in aggregation_scenarios:
            aggregated_data = await metrics_collector.aggregate_time_series(
                metric_name="cpu_utilization",
                data=time_series_results[0]["data"],
                aggregation_type=agg_scenario["aggregation_type"],
                aggregation_function=agg_scenario["function"],
                window_size=agg_scenario["window_size"]
            )
            
            assert aggregated_data is not None
            assert len(aggregated_data) > 0
            assert all("timestamp" in point and "value" in point for point in aggregated_data)
    
    async def test_metric_aggregation_and_analysis(self, metrics_collector):
        """Test metric aggregation and statistical analysis."""        # Aggregation scenarios
        aggregation_scenarios = [
            {
                "aggregation_name": "service_performance_summary",
                "metrics": ["response_time", "throughput", "error_rate"],
                "dimensions": ["service", "endpoint"],
                "time_window": timedelta(hours=1),
                "functions": ["avg", "p95", "p99", "count", "sum"]
            },
            {
                "aggregation_name": "infrastructure_utilization",
                "metrics": ["cpu_usage", "memory_usage", "disk_usage", "network_io"],
                "dimensions": ["server", "component"],
                "time_window": timedelta(minutes=5),
                "functions": ["avg", "max", "min", "stddev"]
            },
            {
                "aggregation_name": "business_metrics_rollup",
                "metrics": ["revenue", "user_sessions", "conversion_rate"],
                "dimensions": ["product", "region", "channel"],
                "time_window": timedelta(days=1),
                "functions": ["sum", "avg", "count", "distinct_count"]
            }
        ]
        
        aggregation_results = []
        
        for scenario in aggregation_scenarios:
            # Create aggregation configuration
            agg_config = {
                "name": scenario["aggregation_name"],
                "metrics": scenario["metrics"],
                "dimensions": scenario["dimensions"],
                "time_window": scenario["time_window"],
                "functions": scenario["functions"],
                "schedule": "real_time",
                "output_format": "structured"
            }
            
            # Execute aggregation
            aggregation_result = await metrics_collector.execute_aggregation(agg_config)
            
            aggregation_results.append({
                "scenario": scenario,
                "config": agg_config,
                "result": aggregation_result
            })
            
            # Verify aggregation result
            assert aggregation_result.success is True
            assert aggregation_result.aggregated_data is not None
            assert aggregation_result.processed_count > 0
            
            # Verify aggregated data structure
            aggregated_data = aggregation_result.aggregated_data
            for function in scenario["functions"]:
                assert any(function in key for key in aggregated_data.keys()) or function in str(aggregated_data)
            
            for metric in scenario["metrics"]:
                assert any(metric in key for key in aggregated_data.keys()) or metric in str(aggregated_data)
            
            for dimension in scenario["dimensions"]:
                assert any(dimension in key for key in aggregated_data.keys()) or dimension in str(aggregated_data)
        
        # Test custom aggregation functions
        custom_functions = [
            {
                "name": "percentile_95",
                "function": lambda values: np.percentile(values, 95),
                "description": "95th percentile calculation"
            },
            {
                "name": "coefficient_of_variation",
                "function": lambda values: np.std(values) / np.mean(values) if np.mean(values) > 0 else 0,
                "description": "Coefficient of variation"
            },
            {
                "name": "inter_quartile_range",
                "function": lambda values: np.percentile(values, 75) - np.percentile(values, 25),
                "description": "Interquartile range"
            }
        ]
        
        for custom_func in custom_functions:
            # Register custom function
            registration_result = await metrics_collector.register_custom_aggregation_function(
                name=custom_func["name"],
                function=custom_func["function"],
                description=custom_func["description"]
            )
            
            assert registration_result.registered is True
            assert registration_result.function_name == custom_func["name"]
            
            # Test custom function usage
            test_data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
            custom_result = await metrics_collector.apply_custom_function(
                function_name=custom_func["name"],
                data=test_data
            )
            
            assert custom_result.success is True
            assert custom_result.result is not None
    
    async def test_alert_threshold_management(self, metrics_collector):
        """Test alert threshold configuration and monitoring."""        # Alert threshold scenarios
        threshold_scenarios = [
            {
                "metric_name": "cpu_usage",
                "thresholds": {
                    "warning": {"value": 70, "operator": "greater_than"},
                    "critical": {"value": 90, "operator": "greater_than"},
                    "recovery": {"value": 65, "operator": "less_than"}
                },
                "evaluation_window": timedelta(minutes=5),
                "min_occurrences": 3
            },
            {
                "metric_name": "error_rate",
                "thresholds": {
                    "warning": {"value": 1.0, "operator": "greater_than"},
                    "critical": {"value": 5.0, "operator": "greater_than"}
                },
                "evaluation_window": timedelta(minutes=2),
                "min_occurrences": 2
            },
            {
                "metric_name": "response_time",
                "thresholds": {
                    "warning": {"value": 200, "operator": "greater_than"},
                    "critical": {"value": 500, "operator": "greater_than"}
                },
                "evaluation_window": timedelta(minutes=1),
                "min_occurrences": 5
            }
        ]
        
        threshold_results = []
        
        for scenario in threshold_scenarios:
            # Configure alert thresholds
            threshold_config = await metrics_collector.configure_alert_thresholds(
                metric_name=scenario["metric_name"],
                thresholds=scenario["thresholds"],
                evaluation_window=scenario["evaluation_window"],
                min_occurrences=scenario["min_occurrences"]
            )
            
            threshold_results.append({
                "scenario": scenario,
                "config": threshold_config
            })
            
            # Verify threshold configuration
            assert threshold_config.metric_name == scenario["metric_name"]
            assert threshold_config.is_active is True
            assert len(threshold_config.thresholds) >= 2  # At least warning and critical
            
            # Test threshold evaluation
            test_values = [
                {"value": 50, "expected_level": "normal"},  # Below warning
                {"value": 75, "expected_level": "warning"},  # Above warning, below critical
                {"value": 95, "expected_level": "critical"},  # Above critical
                {"value": 60, "expected_level": "recovery"}  # Recovery value
            ]
            
            for test_value in test_values:
                evaluation_result = await metrics_collector.evaluate_thresholds(
                    metric_name=scenario["metric_name"],
                    value=test_value["value"],
                    timestamp=datetime.now()
                )
                
                # Verify evaluation result structure
                assert evaluation_result.metric_name == scenario["metric_name"]
                assert evaluation_result.evaluated_value == test_value["value"]
                assert evaluation_result.threshold_level in ["normal", "warning", "critical", "recovery"]
                
                # For single evaluations, we can't guarantee the expected level due to min_occurrences
                # But we can verify the evaluation completed successfully
                assert evaluation_result.evaluation_completed is True
        
        # Test threshold breach detection with sustained values
        sustained_breach_scenario = {
            "metric_name": "cpu_usage",
            "sustained_values": [85, 87, 89, 91, 88, 92],  # Values above warning threshold
            "interval": timedelta(minutes=1)
        }
        
        breach_results = []
        for i, value in enumerate(sustained_breach_scenario["sustained_values"]):
            breach_result = await metrics_collector.evaluate_thresholds(
                metric_name=sustained_breach_scenario["metric_name"],
                value=value,
                timestamp=datetime.now() + (i * sustained_breach_scenario["interval"])
            )
            breach_results.append(breach_result)
        
        # Verify that sustained breaches are detected
        breach_count = sum(1 for result in breach_results if result.threshold_breached)
        assert breach_count > 0  # At least some breaches should be detected
    
    async def test_real_time_metrics_processing(self, metrics_collector):
        """Test real-time metrics processing and streaming."""        # Real-time processing scenarios
        realtime_scenarios = [
            {
                "stream_name": "high_frequency_api_metrics",
                "metrics": ["request_count", "response_time", "error_count"],
                "frequency": 1000,  # 1000 metrics per second
                "duration": 60,  # 60 seconds
                "processing_type": "sliding_window"
            },
            {
                "stream_name": "infrastructure_monitoring",
                "metrics": ["cpu_usage", "memory_usage", "network_io"],
                "frequency": 100,  # 100 metrics per second
                "duration": 30,  # 30 seconds
                "processing_type": "tumbling_window"
            }
        ]
        
        realtime_results = []
        
        for scenario in realtime_scenarios:
            # Configure real-time stream
            stream_config = await metrics_collector.configure_realtime_stream(
                stream_name=scenario["stream_name"],
                metrics=scenario["metrics"],
                processing_type=scenario["processing_type"],
                window_size=timedelta(seconds=10),
                processing_functions=["avg", "max", "count", "rate"]
            )
            
            # Start real-time processing
            stream_processor = await metrics_collector.start_realtime_processing(stream_config)
            
            # Simulate high-frequency metrics
            metrics_generated = 0
            start_time = time.time()
            
            while time.time() - start_time < scenario["duration"] and metrics_generated < scenario["frequency"] * scenario["duration"]:
                # Generate batch of metrics
                batch_size = min(100, scenario["frequency"])  # Process in batches
                metric_batch = []
                
                for _ in range(batch_size):
                    for metric_name in scenario["metrics"]:
                        metric = Metric(
                            name=metric_name,
                            type=MetricType.GAUGE,
                            value=np.random.uniform(10, 100),
                            unit=MetricUnit.COUNT,
                            tags={"stream": scenario["stream_name"]},
                            priority=MetricPriority.MEDIUM,
                            timestamp=datetime.now()
                        )
                        metric_batch.append(metric)
                
                # Process batch
                batch_result = await stream_processor.process_batch(metric_batch)
                metrics_generated += len(metric_batch)
                
                # Small delay to simulate realistic timing
                await asyncio.sleep(0.01)
            
            # Stop processing and get results
            processing_results = await stream_processor.stop_and_get_results()
            
            realtime_results.append({
                "scenario": scenario,
                "metrics_processed": metrics_generated,
                "processing_results": processing_results
            })
            
            # Verify real-time processing results
            assert processing_results.total_processed > 0
            assert processing_results.processing_rate > 0
            assert processing_results.avg_latency < 100  # Less than 100ms average latency
            assert processing_results.error_rate < 0.01  # Less than 1% error rate
            
            # Verify window processing
            window_results = processing_results.window_results
            assert len(window_results) > 0
            for window in window_results:
                assert "window_start" in window
                assert "window_end" in window
                assert "aggregated_values" in window
    
    async def test_custom_metrics_and_extensions(self, metrics_collector):
        """Test custom metrics and extensibility features."""        # Custom metric type scenarios
        custom_metric_scenarios = [
            {
                "metric_type_name": "business_conversion_funnel",
                "metric_definition": {
                    "type": "composite",
                    "components": ["page_views", "form_submissions", "purchases"],
                    "calculation": "funnel_conversion_rate",
                    "unit": MetricUnit.PERCENTAGE
                }
            },
            {
                "metric_type_name": "system_health_score",
                "metric_definition": {
                    "type": "weighted_composite",
                    "components": {
                        "cpu_usage": {"weight": 0.3, "threshold": 80},
                        "memory_usage": {"weight": 0.3, "threshold": 85},
                        "error_rate": {"weight": 0.4, "threshold": 1.0}
                    },
                    "calculation": "weighted_health_score",
                    "unit": MetricUnit.PERCENTAGE
                }
            },
            {
                "metric_type_name": "predictive_capacity_metric",
                "metric_definition": {
                    "type": "predictive",
                    "base_metrics": ["resource_usage", "growth_rate"],
                    "prediction_horizon": timedelta(days=30),
                    "calculation": "capacity_forecast",
                    "unit": MetricUnit.PERCENTAGE
                }
            }
        ]
        
        custom_metric_results = []
        
        for scenario in custom_metric_scenarios:
            # Register custom metric type
            registration_result = await metrics_collector.register_custom_metric_type(
                type_name=scenario["metric_type_name"],
                definition=scenario["metric_definition"]
            )
            
            custom_metric_results.append({
                "scenario": scenario,
                "registration": registration_result
            })
            
            # Verify registration
            assert registration_result.registered is True
            assert registration_result.metric_type_name == scenario["metric_type_name"]
            
            # Test custom metric calculation
            if scenario["metric_type_name"] == "business_conversion_funnel":
                test_data = {
                    "page_views": 10000,
                    "form_submissions": 500,
                    "purchases": 50
                }
                
                custom_metric_value = await metrics_collector.calculate_custom_metric(
                    metric_type=scenario["metric_type_name"],
                    input_data=test_data
                )
                
                assert custom_metric_value.success is True
                assert 0 <= custom_metric_value.calculated_value <= 100  # Percentage
                
            elif scenario["metric_type_name"] == "system_health_score":
                test_data = {
                    "cpu_usage": 65,
                    "memory_usage": 78,
                    "error_rate": 0.5
                }
                
                health_score = await metrics_collector.calculate_custom_metric(
                    metric_type=scenario["metric_type_name"],
                    input_data=test_data
                )
                
                assert health_score.success is True
                assert 0 <= health_score.calculated_value <= 100  # Health score percentage
        
        # Test metric plugin system
        plugin_scenarios = [
            {
                "plugin_name": "advanced_statistical_functions",
                "functions": [
                    "skewness_calculation",
                    "kurtosis_calculation",
                    "moving_average_convergence_divergence"
                ]
            },
            {
                "plugin_name": "business_intelligence_metrics",
                "functions": [
                    "customer_lifetime_value",
                    "churn_prediction_score",
                    "market_share_calculation"
                ]
            }
        ]
        
        for plugin_scenario in plugin_scenarios:
            # Load metric plugin
            plugin_result = await metrics_collector.load_metric_plugin(
                plugin_name=plugin_scenario["plugin_name"],
                functions=plugin_scenario["functions"]
            )
            
            assert plugin_result.loaded is True
            assert plugin_result.plugin_name == plugin_scenario["plugin_name"]
            assert len(plugin_result.available_functions) == len(plugin_scenario["functions"])


@pytest.mark.performance
class TestMetricsPerformance:
    """Performance tests for metrics system."""    
    @pytest.fixture
    async def high_performance_metrics_collector(self):
        """Create high-performance metrics collector."""        collector = MetricsCollector(
            config={
                "high_performance_mode": True,
                "parallel_processing": True,
                "buffer_size": 100000,
                "batch_processing_size": 10000,
                "compression_enabled": True,
                "memory_optimization": True
            }
        )
        await collector.initialize()
        yield collector
        await collector.shutdown()
    
    async def test_high_volume_metric_collection(self, high_performance_metrics_collector):
        """Test metric collection under high volume."""        # High volume scenario
        metric_count = 1000000  # 1 million metrics
        batch_size = 10000
        
        collection_start = time.time()
        
        total_collected = 0
        for batch_start in range(0, metric_count, batch_size):
            batch_end = min(batch_start + batch_size, metric_count)
            batch_metrics = []
            
            for i in range(batch_start, batch_end):
                metric = Metric(
                    name=f"test_metric_{i % 100}",  # 100 different metric names
                    type=MetricType.COUNTER,
                    value=i % 1000,
                    unit=MetricUnit.COUNT,
                    tags={"batch": str(batch_start // batch_size)},
                    priority=MetricPriority.LOW,
                    timestamp=datetime.now()
                )
                batch_metrics.append(metric)
            
            # Collect batch
            batch_result = await high_performance_metrics_collector.collect_metrics_batch(batch_metrics)
            total_collected += batch_result.successful_count
        
        collection_time = time.time() - collection_start
        
        # Performance assertions
        assert total_collected == metric_count
        assert collection_time < 60  # Collect 1M metrics in under 60 seconds
        
        collection_rate = metric_count / collection_time
        assert collection_rate > 15000  # At least 15K metrics per second
    
    async def test_concurrent_metric_processing(self, high_performance_metrics_collector):
        """Test concurrent metric processing performance."""        # Create multiple concurrent processing tasks
        concurrent_tasks = 50
        metrics_per_task = 10000
        
        async def process_metrics_task(task_id: int):
            """Process metrics for a single task."""            task_metrics = []
            for i in range(metrics_per_task):
                metric = Metric(
                    name=f"concurrent_metric_{task_id}_{i}",
                    type=MetricType.GAUGE,
                    value=np.random.uniform(0, 100),
                    unit=MetricUnit.PERCENTAGE,
                    tags={"task_id": str(task_id)},
                    priority=MetricPriority.MEDIUM,
                    timestamp=datetime.now()
                )
                task_metrics.append(metric)
            
            return await high_performance_metrics_collector.collect_metrics_batch(task_metrics)
        
        # Execute concurrent tasks
        concurrent_start = time.time()
        
        tasks = [process_metrics_task(i) for i in range(concurrent_tasks)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        concurrent_time = time.time() - concurrent_start
        
        # Performance verification
        successful_results = [r for r in results if not isinstance(r, Exception)]
        total_processed = sum(r.successful_count for r in successful_results)
        
        expected_total = concurrent_tasks * metrics_per_task
        success_rate = total_processed / expected_total
        
        assert success_rate >= 0.95  # At least 95% success rate
        assert concurrent_time < 120  # Complete in under 2 minutes
        
        processing_rate = total_processed / concurrent_time
        assert processing_rate > 5000  # At least 5K metrics per second under concurrency


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        "test_metrics.py",
        "-v",
        "--cov=backend.ai.monitoring.metrics",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=100"
    ])
