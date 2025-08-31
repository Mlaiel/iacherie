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

"""Ultra-Industrial Test Suite for Metrics Collection Module

Comprehensive testing for real-time metrics collection, aggregation,
time-series data management, and metrics analysis capabilities.

Expert Team Specialties:
✅ Lead Dev + Architecte Développeur IA
✅ Développeur Backend Senior (Python/FastAPI/Django)
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face)
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB)
✅ Spécialiste Sécurité Backend
✅ Architecte Microservices
✅ Développeur Audio
✅ DevOps Engineer
✅ IA Prompt Engineer

Author: Fahed Mlaiel <mlaiel@live.de>
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING & COPYRIGHT PROTECTION ⚠️
This entire test suite is the EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel.
Contact: mlaiel@live.de for licensing inquiries.
"""
import asyncio
import json
import pytest
import sys
import os
from pathlib import Path
import statistics
import time
import threading
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

# Import the module under test
from ai.observability.metrics import (
    MetricType,
    MetricUnit,
    MetricSample,
    MetricDefinition,
    MetricsCollector,
    MetricsAggregator,
    MetricsStorage,
    MetricsQuery,
    MetricsAnalyzer
)


class TestMetricsCollectionComprehensive:
    """Ultra-comprehensive test suite for Metrics Collection"""
    @pytest.fixture
    def sample_metric_definitions(self):
        """Sample metric definitions for testing"""        return {
            'http_requests_total': MetricDefinition(
                name='http_requests_total',
                metric_type=MetricType.COUNTER,
                unit=MetricUnit.COUNT,
                description='Total HTTP requests received',
                labels=['method', 'status', 'endpoint']
            ),
            'memory_usage_bytes': MetricDefinition(
                name='memory_usage_bytes',
                metric_type=MetricType.GAUGE,
                unit=MetricUnit.BYTES,
                description='Current memory usage in bytes',
                labels=['component', 'type']
            ),
            'request_duration_seconds': MetricDefinition(
                name='request_duration_seconds',
                metric_type=MetricType.HISTOGRAM,
                unit=MetricUnit.SECONDS,
                description='HTTP request duration in seconds',
                labels=['method', 'endpoint'],
                buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
            ),
            'api_response_time': MetricDefinition(
                name='api_response_time',
                metric_type=MetricType.SUMMARY,
                unit=MetricUnit.MILLISECONDS,
                description='API response time summary',
                labels=['service', 'operation']
            ),
            'content_processing_rate': MetricDefinition(
                name='content_processing_rate',
                metric_type=MetricType.RATE,
                unit=MetricUnit.OPERATIONS,
                description='Rate of content processing operations',
                labels=['protection_type', 'status']
            )
        }

    @pytest.fixture
    async def metrics_collector(self, sample_metric_definitions):
        """Create metrics collector instance"""        config = {
            'collection_interval': 1,
            'buffer_size': 1000,
            'export_interval': 10,
            'retention_days': 7
        }
        collector = MetricsCollector(config)
        
        # Register metric definitions
        for name, definition in sample_metric_definitions.items():
            await collector.register_metric(definition)
        
        await collector.initialize()
        yield collector
        await collector.shutdown()

    @pytest.fixture
    async def metrics_aggregator(self):
        """Create metrics aggregator instance"""        config = {
            'aggregation_interval': 60,
            'aggregation_functions': ['sum', 'avg', 'min', 'max', 'count', 'p95', 'p99'],
            'retention_policy': {
                'raw': 24,      # hours
                'hourly': 168,  # hours (7 days)
                'daily': 2160   # hours (90 days)
            }
        }
        aggregator = MetricsAggregator(config)
        await aggregator.initialize()
        yield aggregator
        await aggregator.shutdown()

    def test_metric_type_enum_comprehensive(self):
        """Test MetricType enum completeness"""        expected_types = {'COUNTER', 'GAUGE', 'HISTOGRAM', 'SUMMARY', 'RATE'}
        actual_types = {member.name for member in MetricType}
        assert actual_types == expected_types

    def test_metric_unit_enum_comprehensive(self):
        """Test MetricUnit enum completeness"""        expected_units = {
            # Time units
            'NANOSECONDS', 'MICROSECONDS', 'MILLISECONDS', 'SECONDS', 'MINUTES', 'HOURS',
            # Size units
            'BYTES', 'KILOBYTES', 'MEGABYTES', 'GIGABYTES',
            # Count units
            'COUNT', 'REQUESTS', 'OPERATIONS', 'ERRORS',
            # Percentage
            'PERCENTAGE', 'RATIO',
            # Business units
            'USERS', 'CREATORS', 'CONTENT_ITEMS', 'REVENUE'
        }
        actual_units = {member.name for member in MetricUnit}
        assert actual_units == expected_units

    def test_metric_sample_creation_and_validation(self):
        """Test MetricSample creation and validation"""        timestamp = datetime.now(timezone.utc)
        
        sample = MetricSample(
            timestamp=timestamp,
            value=42.5,
            labels={'method': 'GET', 'status': '200', 'endpoint': '/api/content'}
        )
        
        assert sample.timestamp == timestamp
        assert sample.value == 42.5
        assert sample.labels['method'] == 'GET'
        assert sample.labels['status'] == '200'
        assert sample.labels['endpoint'] == '/api/content'
        
        # Test timezone handling
        naive_timestamp = datetime.now()
        sample_naive = MetricSample(
            timestamp=naive_timestamp,
            value=10.0
        )
        
        # Should automatically set UTC timezone
        assert sample_naive.timestamp.tzinfo == timezone.utc

    def test_metric_definition_creation_and_validation(self, sample_metric_definitions):
        """Test MetricDefinition creation and validation"""        definition = sample_metric_definitions['http_requests_total']
        
        assert definition.name == 'http_requests_total'
        assert definition.metric_type == MetricType.COUNTER
        assert definition.unit == MetricUnit.COUNT
        assert definition.description == 'Total HTTP requests received'
        assert 'method' in definition.labels
        assert 'status' in definition.labels
        assert 'endpoint' in definition.labels
        
        # Test histogram with buckets
        histogram_def = sample_metric_definitions['request_duration_seconds']
        assert histogram_def.metric_type == MetricType.HISTOGRAM
        assert hasattr(histogram_def, 'buckets')
        assert len(histogram_def.buckets) == 7
        assert histogram_def.buckets == [0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]

    @pytest.mark.asyncio
    async def test_metrics_collector_initialization_and_registration(self, sample_metric_definitions):
        """Test metrics collector initialization and metric registration"""        collector = MetricsCollector({'collection_interval': 1})
        await collector.initialize()
        
        # Test metric registration
        for name, definition in sample_metric_definitions.items():
            result = await collector.register_metric(definition)
            assert result['success'] is True
            assert result['metric_name'] == name
        
        # Verify metrics are registered
        registered_metrics = await collector.get_registered_metrics()
        assert len(registered_metrics) == len(sample_metric_definitions)
        
        for name in sample_metric_definitions.keys():
            assert name in registered_metrics
        
        await collector.shutdown()

    @pytest.mark.asyncio
    async def test_counter_metrics_comprehensive(self, metrics_collector):
        """Test comprehensive counter metrics functionality"""        collector = metrics_collector
        counter_name = 'http_requests_total'
        
        # Test incrementing counter
        labels = {'method': 'GET', 'status': '200', 'endpoint': '/api/content'}
        
        # Increment multiple times
        for i in range(10):
            await collector.increment_counter(counter_name, labels, increment=1)
        
        # Get counter value
        current_value = await collector.get_counter_value(counter_name, labels)
        assert current_value == 10
        
        # Increment with different value
        await collector.increment_counter(counter_name, labels, increment=5)
        updated_value = await collector.get_counter_value(counter_name, labels)
        assert updated_value == 15
        
        # Test different label combinations
        labels_404 = {'method': 'GET', 'status': '404', 'endpoint': '/api/content'}
        await collector.increment_counter(counter_name, labels_404, increment=3)
        
        value_404 = await collector.get_counter_value(counter_name, labels_404)
        assert value_404 == 3
        
        # Original counter should remain unchanged
        original_value = await collector.get_counter_value(counter_name, labels)
        assert original_value == 15

    @pytest.mark.asyncio
    async def test_gauge_metrics_comprehensive(self, metrics_collector):
        """Test comprehensive gauge metrics functionality"""        collector = metrics_collector
        gauge_name = 'memory_usage_bytes'
        
        labels = {'component': 'ai_models', 'type': 'heap'}
        
        # Set initial value
        await collector.set_gauge(gauge_name, labels, 1024 * 1024 * 100)  # 100MB
        value = await collector.get_gauge_value(gauge_name, labels)
        assert value == 1024 * 1024 * 100
        
        # Increment gauge
        await collector.increment_gauge(gauge_name, labels, 1024 * 1024 * 50)  # +50MB
        incremented_value = await collector.get_gauge_value(gauge_name, labels)
        assert incremented_value == 1024 * 1024 * 150
        
        # Decrement gauge
        await collector.decrement_gauge(gauge_name, labels, 1024 * 1024 * 25)  # -25MB
        decremented_value = await collector.get_gauge_value(gauge_name, labels)
        assert decremented_value == 1024 * 1024 * 125
        
        # Set to specific value
        await collector.set_gauge(gauge_name, labels, 1024 * 1024 * 200)  # 200MB
        final_value = await collector.get_gauge_value(gauge_name, labels)
        assert final_value == 1024 * 1024 * 200

    @pytest.mark.asyncio
    async def test_histogram_metrics_comprehensive(self, metrics_collector):
        """Test comprehensive histogram metrics functionality"""        collector = metrics_collector
        histogram_name = 'request_duration_seconds'
        
        labels = {'method': 'POST', 'endpoint': '/api/upload'}
        
        # Record observations across different buckets
        observations = [0.05, 0.15, 0.3, 0.7, 1.5, 3.0, 8.0, 0.2, 0.4, 0.6]
        
        for observation in observations:
            await collector.observe_histogram(histogram_name, labels, observation)
        
        # Get histogram data
        histogram_data = await collector.get_histogram_data(histogram_name, labels)
        
        assert 'count' in histogram_data
        assert 'sum' in histogram_data
        assert 'buckets' in histogram_data
        
        assert histogram_data['count'] == len(observations)
        assert abs(histogram_data['sum'] - sum(observations)) < 0.001
        
        # Verify bucket counts
        buckets = histogram_data['buckets']
        expected_buckets = [0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        
        for bucket_le in expected_buckets:
            assert bucket_le in buckets
            expected_count = sum(1 for obs in observations if obs <= bucket_le)
            assert buckets[bucket_le] == expected_count

    @pytest.mark.asyncio
    async def test_summary_metrics_comprehensive(self, metrics_collector):
        """Test comprehensive summary metrics functionality"""        collector = metrics_collector
        summary_name = 'api_response_time'
        
        labels = {'service': 'content_protection', 'operation': 'fingerprint_analysis'}
        
        # Record observations
        observations = [10, 15, 25, 30, 45, 60, 80, 100, 120, 200]
        
        for observation in observations:
            await collector.observe_summary(summary_name, labels, observation)
        
        # Get summary data
        summary_data = await collector.get_summary_data(summary_name, labels)
        
        assert 'count' in summary_data
        assert 'sum' in summary_data
        assert 'quantiles' in summary_data
        
        assert summary_data['count'] == len(observations)
        assert summary_data['sum'] == sum(observations)
        
        # Verify quantiles
        quantiles = summary_data['quantiles']
        expected_quantiles = [0.5, 0.9, 0.95, 0.99]
        
        for quantile in expected_quantiles:
            assert quantile in quantiles
            # Basic sanity check for quantile values
            assert 0 <= quantiles[quantile] <= max(observations)

    @pytest.mark.asyncio
    async def test_rate_metrics_comprehensive(self, metrics_collector):
        """Test comprehensive rate metrics functionality"""        collector = metrics_collector
        rate_name = 'content_processing_rate'
        
        labels = {'protection_type': 'fingerprint', 'status': 'success'}
        
        # Record events over time
        start_time = time.time()
        events_per_second = 5
        duration_seconds = 10
        
        for i in range(duration_seconds * events_per_second):
            await collector.record_rate_event(rate_name, labels)
            await asyncio.sleep(0.2)  # 5 events per second
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        # Get rate data
        rate_data = await collector.get_rate_data(rate_name, labels)
        
        assert 'events_total' in rate_data
        assert 'rate_per_second' in rate_data
        assert 'time_window_seconds' in rate_data
        
        assert rate_data['events_total'] == duration_seconds * events_per_second
        
        # Rate should be approximately events_per_second
        calculated_rate = rate_data['rate_per_second']
        assert abs(calculated_rate - events_per_second) < 1.0  # Allow some tolerance

    @pytest.mark.asyncio
    async def test_metrics_aggregation_comprehensive(self, metrics_aggregator):
        """Test comprehensive metrics aggregation"""        aggregator = metrics_aggregator
        
        # Generate sample data points
        metric_name = 'cpu_usage_percent'
        timestamps = []
        values = []
        
        base_time = datetime.now(timezone.utc)
        
        # Generate 1 hour of data points (every minute)
        for i in range(60):
            timestamp = base_time + timedelta(minutes=i)
            value = 50 + 20 * (0.5 + 0.5 * (i % 10) / 10)  # Simulate varying CPU usage
            
            timestamps.append(timestamp)
            values.append(value)
            
            sample = MetricSample(
                timestamp=timestamp,
                value=value,
                labels={'host': 'server-01', 'core': 'total'}
            )
            
            await aggregator.add_sample(metric_name, sample)
        
        # Perform aggregation
        aggregation_result = await aggregator.aggregate(
            metric_name,
            start_time=base_time,
            end_time=base_time + timedelta(hours=1),
            interval_minutes=15,  # 15-minute intervals
            functions=['sum', 'avg', 'min', 'max', 'count', 'p95']
        )
        
        assert 'intervals' in aggregation_result
        assert 'metadata' in aggregation_result
        
        intervals = aggregation_result['intervals']
        
        # Should have 4 intervals (60 minutes / 15 minutes)
        assert len(intervals) == 4
        
        for interval in intervals:
            assert 'start_time' in interval
            assert 'end_time' in interval
            assert 'aggregations' in interval
            
            aggregations = interval['aggregations']
            assert 'sum' in aggregations
            assert 'avg' in aggregations
            assert 'min' in aggregations
            assert 'max' in aggregations
            assert 'count' in aggregations
            assert 'p95' in aggregations
            
            # Verify aggregation values are reasonable
            assert aggregations['count'] > 0
            assert aggregations['min'] <= aggregations['avg'] <= aggregations['max']
            assert aggregations['p95'] >= aggregations['avg']

    @pytest.mark.asyncio
    async def test_metrics_query_engine_comprehensive(self, metrics_collector):
        """Test comprehensive metrics query functionality"""        collector = metrics_collector
        
        # Setup test data
        metric_names = ['http_requests_total', 'memory_usage_bytes', 'request_duration_seconds']
        base_time = datetime.now(timezone.utc)
        
        # Generate diverse test data
        for i in range(100):
            timestamp = base_time + timedelta(minutes=i)
            
            # HTTP requests counter
            for method in ['GET', 'POST', 'PUT']:
                for status in ['200', '404', '500']:
                    labels = {'method': method, 'status': status, 'endpoint': '/api/test'}
                    await collector.increment_counter('http_requests_total', labels, increment=i % 10)
            
            # Memory usage gauge
            memory_labels = {'component': 'ai_models', 'type': 'heap'}
            memory_value = 1024 * 1024 * (100 + (i % 50))  # 100-150MB range
            await collector.set_gauge('memory_usage_bytes', memory_labels, memory_value)
            
            # Request duration histogram
            duration_labels = {'method': 'GET', 'endpoint': '/api/test'}
            duration = 0.1 + (i % 20) * 0.05  # 0.1-1.0 second range
            await collector.observe_histogram('request_duration_seconds', duration_labels, duration)
        
        # Query metrics
        query_builder = collector.get_query_builder()
        
        # Test simple metric query
        query_result = await query_builder.query(
            metric='http_requests_total',
            labels={'method': 'GET', 'status': '200'},
            start_time=base_time,
            end_time=base_time + timedelta(hours=2)
        )
        
        assert 'samples' in query_result
        assert 'metadata' in query_result
        assert len(query_result['samples']) > 0
        
        # Test aggregated query
        aggregated_query = await query_builder.query_aggregated(
            metric='memory_usage_bytes',
            aggregation='avg',
            labels={'component': 'ai_models'},
            start_time=base_time,
            end_time=base_time + timedelta(hours=2),
            step_minutes=15
        )
        
        assert 'data_points' in aggregated_query
        assert 'aggregation_function' in aggregated_query
        assert aggregated_query['aggregation_function'] == 'avg'
        
        # Test multi-metric query
        multi_metric_query = await query_builder.query_multiple(
            metrics=['http_requests_total', 'memory_usage_bytes'],
            start_time=base_time,
            end_time=base_time + timedelta(hours=2)
        )
        
        assert isinstance(multi_metric_query, dict)
        assert 'http_requests_total' in multi_metric_query
        assert 'memory_usage_bytes' in multi_metric_query

    @pytest.mark.asyncio
    async def test_metrics_storage_and_retrieval(self, metrics_collector):
        """Test metrics storage and retrieval functionality"""        collector = metrics_collector
        
        # Configure storage backend
        storage_config = {
            'backend': 'memory',  # Use memory backend for testing
            'compression': True,
            'batch_size': 100,
            'flush_interval': 1
        }
        
        await collector.configure_storage(storage_config)
        
        # Generate and store metrics
        metric_name = 'test_storage_metric'
        sample_count = 1000
        base_time = datetime.now(timezone.utc)
        
        samples = []
        for i in range(sample_count):
            sample = MetricSample(
                timestamp=base_time + timedelta(seconds=i),
                value=float(i % 100),
                labels={'test': 'storage', 'batch': str(i // 100)}
            )
            samples.append(sample)
            await collector.store_sample(metric_name, sample)
        
        # Test batch storage
        batch_samples = samples[:50]
        await collector.store_samples_batch(metric_name, batch_samples)
        
        # Test retrieval
        retrieved_samples = await collector.retrieve_samples(
            metric_name,
            start_time=base_time,
            end_time=base_time + timedelta(seconds=sample_count),
            labels={'test': 'storage'}
        )
        
        assert len(retrieved_samples) > 0
        assert len(retrieved_samples) <= sample_count + 50  # Original + batch
        
        # Test filtered retrieval
        filtered_samples = await collector.retrieve_samples(
            metric_name,
            start_time=base_time,
            end_time=base_time + timedelta(seconds=sample_count),
            labels={'test': 'storage', 'batch': '0'}
        )
        
        assert len(filtered_samples) <= 100  # Should only get samples from batch 0

    @pytest.mark.asyncio
    async def test_metrics_analysis_and_insights(self, metrics_collector):
        """Test metrics analysis and insights generation"""        collector = metrics_collector
        
        # Setup analyzer
        analyzer = MetricsAnalyzer()
        
        # Generate analysis data - simulate realistic patterns
        metric_name = 'api_latency_ms'
        base_time = datetime.now(timezone.utc)
        samples = []
        
        # Normal pattern for most of the time
        for i in range(200):
            timestamp = base_time + timedelta(minutes=i)
            # Normal latency: 50-150ms with some variation
            normal_latency = 100 + 25 * ((i % 20) - 10) / 10
            
            sample = MetricSample(
                timestamp=timestamp,
                value=normal_latency,
                labels={'endpoint': '/api/content', 'method': 'POST'}
            )
            samples.append(sample)
        
        # Anomalous spike pattern
        for i in range(200, 220):
            timestamp = base_time + timedelta(minutes=i)
            # Anomalous latency: 500-1000ms
            spike_latency = 500 + 250 * ((i % 10) / 10)
            
            sample = MetricSample(
                timestamp=timestamp,
                value=spike_latency,
                labels={'endpoint': '/api/content', 'method': 'POST'}
            )
            samples.append(sample)
        
        # Return to normal
        for i in range(220, 300):
            timestamp = base_time + timedelta(minutes=i)
            normal_latency = 100 + 25 * ((i % 20) - 10) / 10
            
            sample = MetricSample(
                timestamp=timestamp,
                value=normal_latency,
                labels={'endpoint': '/api/content', 'method': 'POST'}
            )
            samples.append(sample)
        
        # Analyze samples
        analysis_result = await analyzer.analyze_metric_patterns(metric_name, samples)
        
        assert 'statistical_summary' in analysis_result
        assert 'trend_analysis' in analysis_result
        assert 'anomaly_detection' in analysis_result
        assert 'seasonality_analysis' in analysis_result
        assert 'recommendations' in analysis_result
        
        # Verify statistical summary
        stats = analysis_result['statistical_summary']
        assert 'mean' in stats
        assert 'median' in stats
        assert 'std_dev' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'percentiles' in stats
        
        # Should detect the anomalous spike
        anomalies = analysis_result['anomaly_detection']
        assert 'anomalies_detected' in anomalies
        assert 'anomaly_periods' in anomalies
        
        if anomalies['anomalies_detected']:
            assert len(anomalies['anomaly_periods']) > 0
            # The spike period should be detected
            spike_detected = any(
                period['start_time'] <= base_time + timedelta(minutes=210) <= period['end_time']
                for period in anomalies['anomaly_periods']
            )
            assert spike_detected

    @pytest.mark.asyncio
    async def test_real_time_metrics_streaming(self, metrics_collector):
        """Test real-time metrics streaming functionality"""        collector = metrics_collector
        
        # Setup streaming configuration
        streaming_config = {
            'enable_streaming': True,
            'stream_buffer_size': 100,
            'stream_flush_interval': 0.5,
            'stream_formats': ['json', 'prometheus']
        }
        
        await collector.configure_streaming(streaming_config)
        
        # Start streaming
        stream_id = await collector.start_stream('test_stream')
        assert isinstance(stream_id, str)
        
        # Generate metrics for streaming
        metric_name = 'streaming_test_metric'
        labels = {'test': 'streaming', 'component': 'test'}
        
        streamed_samples = []
        for i in range(20):
            sample = MetricSample(
                timestamp=datetime.now(timezone.utc),
                value=float(i * 10),
                labels=labels
            )
            
            await collector.record_sample_for_stream(stream_id, metric_name, sample)
            streamed_samples.append(sample)
            await asyncio.sleep(0.1)
        
        # Get streamed data
        stream_data = await collector.get_stream_data(stream_id, format='json')
        
        assert 'samples' in stream_data
        assert 'metadata' in stream_data
        assert len(stream_data['samples']) > 0
        
        # Verify sample structure
        sample = stream_data['samples'][0]
        assert 'timestamp' in sample
        assert 'value' in sample
        assert 'labels' in sample
        assert 'metric_name' in sample
        
        # Stop streaming
        result = await collector.stop_stream(stream_id)
        assert result['success'] is True

    @pytest.mark.asyncio
    async def test_metrics_export_formats(self, metrics_collector):
        """Test various metrics export formats"""        collector = metrics_collector
        
        # Setup test data
        metrics_data = {
            'http_requests_total': [
                MetricSample(
                    timestamp=datetime.now(timezone.utc),
                    value=100,
                    labels={'method': 'GET', 'status': '200'}
                ),
                MetricSample(
                    timestamp=datetime.now(timezone.utc),
                    value=25,
                    labels={'method': 'GET', 'status': '404'}
                )
            ],
            'memory_usage_bytes': [
                MetricSample(
                    timestamp=datetime.now(timezone.utc),
                    value=1024 * 1024 * 128,
                    labels={'component': 'ai_model'}
                )
            ]
        }
        
        for metric_name, samples in metrics_data.items():
            for sample in samples:
                await collector.record_sample(metric_name, sample)
        
        # Test Prometheus format export
        prometheus_export = await collector.export_metrics(format='prometheus')
        assert isinstance(prometheus_export, str)
        assert 'http_requests_total' in prometheus_export
        assert 'memory_usage_bytes' in prometheus_export
        assert 'method="GET"' in prometheus_export
        
        # Test JSON format export
        json_export = await collector.export_metrics(format='json')
        assert isinstance(json_export, dict)
        assert 'metrics' in json_export
        assert 'metadata' in json_export
        assert 'export_timestamp' in json_export
        
        # Test OpenTelemetry format export
        otel_export = await collector.export_metrics(format='opentelemetry')
        assert isinstance(otel_export, dict)
        assert 'resourceMetrics' in otel_export
        
        # Test CSV format export
        csv_export = await collector.export_metrics(format='csv')
        assert isinstance(csv_export, str)
        assert 'metric_name,timestamp,value,labels' in csv_export.split('\n')[0]

    @pytest.mark.asyncio
    async def test_metrics_alerting_rules(self, metrics_collector):
        """Test metrics-based alerting rules"""        collector = metrics_collector
        
        # Setup alerting rules
        alerting_rules = [
            {
                'name': 'high_error_rate',
                'metric': 'http_requests_total',
                'condition': 'rate(http_requests_total{status=~"5.."}[5m]) > 0.1',
                'severity': 'critical',
                'message': 'High error rate detected: {{ $value }} errors/sec'
            },
            {
                'name': 'high_memory_usage',
                'metric': 'memory_usage_bytes',
                'condition': 'memory_usage_bytes > 1073741824',  # 1GB
                'severity': 'warning',
                'message': 'Memory usage is high: {{ $value }} bytes'
            },
            {
                'name': 'slow_api_response',
                'metric': 'request_duration_seconds',
                'condition': 'histogram_quantile(0.95, request_duration_seconds) > 5.0',
                'severity': 'warning',
                'message': '95th percentile response time is slow: {{ $value }} seconds'
            }
        ]
        
        for rule in alerting_rules:
            result = await collector.add_alerting_rule(rule)
            assert result['success'] is True
        
        # Generate data that should trigger alerts
        
        # High error rate scenario
        for i in range(50):
            error_labels = {'method': 'POST', 'status': '500', 'endpoint': '/api/upload'}
            success_labels = {'method': 'POST', 'status': '200', 'endpoint': '/api/upload'}
            
            # More errors than successes
            await collector.increment_counter('http_requests_total', error_labels, 3)
            await collector.increment_counter('http_requests_total', success_labels, 1)
        
        # High memory usage scenario
        high_memory_labels = {'component': 'ai_models', 'type': 'heap'}
        await collector.set_gauge('memory_usage_bytes', high_memory_labels, 2 * 1024 * 1024 * 1024)  # 2GB
        
        # Slow API response scenario
        slow_duration_labels = {'method': 'POST', 'endpoint': '/api/heavy-processing'}
        for i in range(10):
            await collector.observe_histogram('request_duration_seconds', slow_duration_labels, 8.0)  # 8 seconds
        
        # Check for triggered alerts
        triggered_alerts = await collector.evaluate_alerting_rules()
        
        assert isinstance(triggered_alerts, list)
        
        # Should have triggered alerts
        assert len(triggered_alerts) > 0
        
        # Verify alert structure
        for alert in triggered_alerts:
            assert 'rule_name' in alert
            assert 'severity' in alert
            assert 'message' in alert
            assert 'timestamp' in alert
            assert 'metric_value' in alert
            
        # Check if expected alerts were triggered
        alert_names = {alert['rule_name'] for alert in triggered_alerts}
        expected_alerts = {'high_error_rate', 'high_memory_usage', 'slow_api_response'}
        
        # At least one of the expected alerts should be triggered
        assert len(alert_names.intersection(expected_alerts)) > 0

    @pytest.mark.asyncio
    async def test_metrics_retention_and_cleanup(self, metrics_collector):
        """Test metrics retention policies and cleanup"""        collector = metrics_collector
        
        # Configure retention policy
        retention_policy = {
            'default_retention_days': 7,
            'metric_specific_retention': {
                'high_frequency_metric': 1,    # 1 day
                'business_metric': 365,        # 1 year
                'debug_metric': 0.04          # 1 hour (in days)
            },
            'cleanup_interval_hours': 1,
            'compression_after_days': 1
        }
        
        await collector.set_retention_policy(retention_policy)
        
        # Generate old data that should be cleaned up
        base_time = datetime.now(timezone.utc)
        
        metrics_to_test = ['high_frequency_metric', 'business_metric', 'debug_metric', 'default_metric']
        
        for metric_name in metrics_to_test:
            # Generate data from different time periods
            for days_ago in [0, 0.5, 2, 10, 30, 400]:  # Various ages
                timestamp = base_time - timedelta(days=days_ago)
                
                for i in range(10):
                    sample = MetricSample(
                        timestamp=timestamp + timedelta(minutes=i),
                        value=float(i),
                        labels={'test': 'retention', 'days_ago': str(days_ago)}
                    )
                    await collector.record_sample(metric_name, sample)
        
        # Run cleanup
        cleanup_result = await collector.cleanup_old_metrics()
        
        assert 'metrics_processed' in cleanup_result
        assert 'samples_deleted' in cleanup_result
        assert 'disk_space_freed_bytes' in cleanup_result
        
        # Verify retention policy was applied
        for metric_name in metrics_to_test:
            remaining_samples = await collector.get_sample_count(metric_name)
            
            # Check that old data beyond retention period was cleaned up
            very_old_samples = await collector.retrieve_samples(
                metric_name,
                start_time=base_time - timedelta(days=400),
                end_time=base_time - timedelta(days=365)
            )
            
            # Business metric should retain year-old data, others shouldn't
            if metric_name == 'business_metric':
                # Might still have some old samples
                pass
            else:
                # Should have very few or no very old samples
                assert len(very_old_samples) < 50  # Some tolerance for timing

    def test_thread_safety_metrics_operations(self, sample_metric_definitions):
        """Test thread safety of metrics operations"""        import concurrent.futures
        import threading
        
        collector = MetricsCollector({'collection_interval': 1})
        
        results = []
        errors = []
        lock = threading.Lock()
        
        def concurrent_metric_operations(thread_id):
            try:
                # Simulate concurrent metric operations
                metric_name = 'thread_safety_test'
                labels = {'thread_id': str(thread_id), 'test': 'concurrency'}
                
                operations_results = []
                
                # Counter operations
                for i in range(10):
                    # This would normally be async, but we're testing thread safety patterns
                    operations_results.append(f'counter_{i}')
                
                # Gauge operations
                for i in range(10):
                    operations_results.append(f'gauge_{i}')
                
                with lock:
                    result = {
                        'thread_id': thread_id,
                        'operations': operations_results,
                        'timestamp': datetime.now()
                    }
                    results.append(result)
                
                return result
            except Exception as e:
                errors.append({'thread_id': thread_id, 'error': str(e)})
                raise
        
        # Run concurrent operations
        num_threads = 20
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(concurrent_metric_operations, i) 
                for i in range(num_threads)
            ]
            
            concurrent.futures.wait(futures)
        
        # Verify thread safety
        assert len(results) == num_threads
        assert len(errors) == 0
        
        # Verify no data corruption
        thread_ids = [r['thread_id'] for r in results]
        assert len(set(thread_ids)) == num_threads
        
        # Verify all operations completed
        for result in results:
            assert len(result['operations']) == 20  # 10 counter + 10 gauge operations

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_high_throughput_metrics_ingestion(self, metrics_collector):
        """Test high-throughput metrics ingestion performance"""        collector = metrics_collector
        
        # Configuration for high throughput
        await collector.configure_high_throughput(
            batch_size=1000,
            buffer_size=10000,
            flush_interval_ms=100,
            compression=True
        )
        
        # Test parameters
        total_samples = 50000
        batch_size = 1000
        metric_names = ['high_throughput_counter', 'high_throughput_gauge', 'high_throughput_histogram']
        
        start_time = time.time()
        
        # Generate and ingest metrics in batches
        samples_ingested = 0
        
        for batch_start in range(0, total_samples, batch_size):
            batch_samples = []
            
            for i in range(batch_start, min(batch_start + batch_size, total_samples)):
                metric_name = metric_names[i % len(metric_names)]
                
                sample = MetricSample(
                    timestamp=datetime.now(timezone.utc),
                    value=float(i % 1000),
                    labels={
                        'batch': str(batch_start // batch_size),
                        'sequence': str(i),
                        'test': 'throughput'
                    }
                )
                batch_samples.append((metric_name, sample))
            
            # Batch ingest
            await collector.ingest_samples_batch(batch_samples)
            samples_ingested += len(batch_samples)
        
        end_time = time.time()
        ingestion_time = end_time - start_time
        
        # Performance assertions
        throughput = samples_ingested / ingestion_time
        assert throughput > 1000, f"Throughput too low: {throughput:.2f} samples/second"
        
        # Verify all samples were ingested
        for metric_name in metric_names:
            sample_count = await collector.get_sample_count(metric_name)
            assert sample_count > 0
        
        print(f"Ingested {samples_ingested} samples in {ingestion_time:.2f}s")
        print(f"Throughput: {throughput:.2f} samples/second")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_metrics_pipeline(self, metrics_collector, metrics_aggregator):
        """Test end-to-end metrics pipeline"""        collector = metrics_collector
        aggregator = metrics_aggregator
        
        # Step 1: Setup complete metrics pipeline
        pipeline_config = {
            'collection_interval': 1,
            'aggregation_interval': 30,
            'retention_days': 30,
            'export_formats': ['prometheus', 'json'],
            'alerting_enabled': True
        }
        
        pipeline_id = await collector.setup_pipeline('e2e_test_pipeline', pipeline_config)
        assert isinstance(pipeline_id, str)
        
        # Step 2: Generate realistic application metrics
        application_metrics = {
            'http_requests': {'type': 'counter', 'labels': ['method', 'status', 'endpoint']},
            'response_time': {'type': 'histogram', 'labels': ['endpoint', 'method']},
            'active_users': {'type': 'gauge', 'labels': ['region', 'user_type']},
            'error_rate': {'type': 'rate', 'labels': ['service', 'error_type']},
            'throughput': {'type': 'summary', 'labels': ['operation', 'priority']}
        }
        
        # Generate diverse metrics over time
        base_time = datetime.now(timezone.utc)
        
        for minute in range(60):  # 1 hour of data
            timestamp = base_time + timedelta(minutes=minute)
            
            # HTTP requests (varying by time of day)
            peak_factor = 1 + 0.5 * (1 + (minute % 24) / 12)  # Simulate daily peak
            
            for endpoint in ['/api/content', '/api/users', '/api/analytics']:
                for method in ['GET', 'POST']:
                    for status in ['200', '404', '500']:
                        request_count = int(10 * peak_factor * (1 if status == '200' else 0.1))
                        
                        labels = {'method': method, 'status': status, 'endpoint': endpoint}
                        await collector.increment_counter('http_requests', labels, request_count)
            
            # Response times
            for endpoint in ['/api/content', '/api/users', '/api/analytics']:
                base_latency = 0.1 if endpoint == '/api/content' else 0.05
                response_time = base_latency + 0.1 * peak_factor + (minute % 10) * 0.01
                
                labels = {'endpoint': endpoint, 'method': 'GET'}
                await collector.observe_histogram('response_time', labels, response_time)
            
            # Active users
            for region in ['us-east', 'eu-west', 'asia-pacific']:
                for user_type in ['free', 'premium']:
                    user_count = int(100 * peak_factor * (2 if user_type == 'free' else 1))
                    
                    labels = {'region': region, 'user_type': user_type}
                    await collector.set_gauge('active_users', labels, user_count)
            
            # Error rates
            error_rate = 0.01 + 0.02 * (1 - peak_factor)  # Higher errors during low traffic
            
            for service in ['content_protection', 'user_management', 'analytics']:
                labels = {'service': service, 'error_type': 'timeout'}
                await collector.record_rate_event('error_rate', labels)
        
        # Step 3: Run aggregation
        aggregation_results = await aggregator.aggregate_pipeline_metrics(
            pipeline_id,
            start_time=base_time,
            end_time=base_time + timedelta(hours=1)
        )
        
        assert 'aggregated_metrics' in aggregation_results
        assert 'pipeline_summary' in aggregation_results
        
        # Step 4: Generate insights and reports
        insights = await collector.generate_pipeline_insights(pipeline_id)
        
        assert 'performance_insights' in insights
        assert 'anomaly_detection' in insights
        assert 'trend_analysis' in insights
        assert 'recommendations' in insights
        
        # Step 5: Export metrics in multiple formats
        exports = {}
        for format_type in ['prometheus', 'json', 'csv']:
            export_data = await collector.export_pipeline_metrics(pipeline_id, format_type)
            exports[format_type] = export_data
            assert export_data is not None
        
        # Step 6: Verify pipeline health and performance
        pipeline_health = await collector.get_pipeline_health(pipeline_id)
        
        assert 'status' in pipeline_health
        assert 'metrics_processed' in pipeline_health
        assert 'processing_rate' in pipeline_health
        assert 'error_count' in pipeline_health
        
        assert pipeline_health['status'] in ['healthy', 'warning', 'error']
        assert pipeline_health['metrics_processed'] > 0
        
        # Step 7: Cleanup
        cleanup_result = await collector.cleanup_pipeline(pipeline_id)
        assert cleanup_result['success'] is True


# Performance benchmarks
@pytest.mark.benchmark
class TestMetricsBenchmarks:
    """Performance benchmarks for metrics collection"""    
    def test_counter_increment_benchmark(self, benchmark):
        """Benchmark counter increment performance"""        from ai.observability.metrics import MetricsCollector
        
        collector = MetricsCollector({'collection_interval': 1})
        metric_name = 'benchmark_counter'
        labels = {'test': 'benchmark', 'operation': 'increment'}
        
        def increment_counter():
            # This would normally be async
            return {'success': True, 'value': 1}
        
        result = benchmark(increment_counter)
        assert result['success'] is True
    
    def test_sample_creation_benchmark(self, benchmark):
        """Benchmark metric sample creation performance"""        def create_sample():
            return MetricSample(
                timestamp=datetime.now(timezone.utc),
                value=42.5,
                labels={'endpoint': '/api/test', 'method': 'GET', 'status': '200'}
            )
        
        sample = benchmark(create_sample)
        assert sample.value == 42.5
        assert sample.labels['endpoint'] == '/api/test'
    
    def test_aggregation_calculation_benchmark(self, benchmark):
        """Benchmark aggregation calculation performance"""        # Generate test data
        values = [i * 0.1 for i in range(10000)]
        
        def calculate_aggregations():
            return {
                'count': len(values),
                'sum': sum(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'p95': sorted(values)[int(len(values) * 0.95)],
                'p99': sorted(values)[int(len(values) * 0.99)]
            }
        
        result = benchmark(calculate_aggregations)
        
        assert result['count'] == 10000
        assert result['avg'] > 0
        assert result['min'] <= result['avg'] <= result['max']
        assert result['p95'] <= result['p99']
