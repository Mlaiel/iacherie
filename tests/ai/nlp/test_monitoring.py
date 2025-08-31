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
Comprehensive Tests for NLP Monitoring Module

Industrial-grade tests for AdvancedMonitoringSystem covering performance monitoring,
quality tracking, and system observability with real implementations.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - Unauthorized use prohibited ⚠️
This software is proprietary and confidential. Contact: mlaiel@live.de
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from typing import Dict, List, Any, Optional
import logging

from ai.nlp.monitoring import (
    AdvancedNLPMonitor, TrendAnalyzer, AnomalyDetector, ReportGenerator,
    MonitoringAlert, MetricSnapshot, TrendAnalysis, PerformanceReport,
    AlertLevel, MetricType
)
try:
    from ai.nlp.utils import Platform, Language
except ImportError:
    Platform = type('Platform', (), {'INSTAGRAM': 'instagram', 'TIKTOK': 'tiktok', 'TWITTER': 'twitter'})
    Language = type('Language', (), {'EN': 'en', 'DE': 'de', 'FR': 'fr'})

logger = logging.getLogger(__name__)

class TestAdvancedMonitoringSystem:
    """Comprehensive tests for AdvancedMonitoringSystem"""
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, monitoring_system):
        """Test monitoring system initialization"""
        assert monitoring_system is not None
        assert hasattr(monitoring_system, 'config')
        assert hasattr(monitoring_system, 'performance_monitor')
        assert hasattr(monitoring_system, 'quality_tracker')
        assert hasattr(monitoring_system, 'system_observer')
        
        # Test configuration
        config = monitoring_system.config
        assert 'monitoring_interval' in config
        assert 'metrics_collection' in config
        assert 'alert_thresholds' in config

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, monitoring_system):
        """Test system performance monitoring"""
        # Start performance monitoring
        monitoring_session = await monitoring_system.start_performance_monitoring(
            session_id='test_performance_001',
            monitoring_config={
                'cpu_monitoring': True,
                'memory_monitoring': True,
                'response_time_tracking': True,
                'throughput_measurement': True,
                'error_rate_tracking': True
            }
        )
        
        assert monitoring_session is not None
        assert 'session_id' in monitoring_session
        assert 'monitoring_start_time' in monitoring_session
        assert 'metrics_collection_interval' in monitoring_session
        
        # Simulate some NLP operations to monitor
        operations = [
            {'operation': 'sentiment_analysis', 'duration': 0.5, 'success': True},
            {'operation': 'content_generation', 'duration': 1.2, 'success': True},
            {'operation': 'translation', 'duration': 0.8, 'success': False},
            {'operation': 'classification', 'duration': 0.3, 'success': True},
            {'operation': 'extraction', 'duration': 0.7, 'success': True}
        ]
        
        for operation in operations:
            await monitoring_system.record_operation(
                session_id='test_performance_001',
                operation_type=operation['operation'],
                duration=operation['duration'],
                success=operation['success'],
                metadata={
                    'timestamp': time.time(),
                    'operation_details': f"Test {operation['operation']}"
                }
            )
        
        # Get performance metrics
        performance_metrics = await monitoring_system.get_performance_metrics(
            session_id='test_performance_001',
            options={
                'detailed_breakdown': True,
                'trend_analysis': True,
                'comparison_metrics': True
            }
        )
        
        assert performance_metrics is not None
        assert 'session_metrics' in performance_metrics
        assert 'operation_statistics' in performance_metrics
        assert 'performance_trends' in performance_metrics
        
        session_metrics = performance_metrics['session_metrics']
        operation_stats = performance_metrics['operation_statistics']
        
        # Verify metrics collection
        assert 'total_operations' in session_metrics
        assert 'success_rate' in session_metrics
        assert 'average_response_time' in session_metrics
        assert 'throughput' in session_metrics
        
        # Should have recorded all operations
        assert session_metrics['total_operations'] == len(operations)
        
        # Success rate should reflect our test data (4/5 = 80%)
        expected_success_rate = 4 / 5
        actual_success_rate = session_metrics['success_rate']
        assert abs(actual_success_rate - expected_success_rate) < 0.1

    @pytest.mark.asyncio
    async def test_quality_tracking(self, monitoring_system):
        """Test content quality tracking"""
        # Define quality test cases
        quality_test_cases = [
            {
                'content': "This is high-quality, well-structured content with proper grammar and engaging style.",
                'expected_quality': 'high',
                'operation': 'content_generation'
            },
            {
                'content': "this is ok content but could be better maybe",
                'expected_quality': 'medium',
                'operation': 'content_generation'
            },
            {
                'content': "bad content poor quality errors everywhere...",
                'expected_quality': 'low',
                'operation': 'content_generation'
            },
            {
                'content': "I love this amazing product! It's fantastic and wonderful!",
                'expected_quality': 'high',
                'operation': 'sentiment_analysis'
            }
        ]
        
        # Start quality tracking session
        quality_session = await monitoring_system.start_quality_tracking(
            session_id='test_quality_001',
            tracking_config={
                'content_quality_scoring': True,
                'accuracy_measurement': True,
                'consistency_tracking': True,
                'user_satisfaction_tracking': True
            }
        )
        
        assert quality_session is not None
        assert 'session_id' in quality_session
        
        # Record quality metrics for each test case
        for i, case in enumerate(quality_test_cases):
            quality_score = await monitoring_system.track_content_quality(
                session_id='test_quality_001',
                content=case['content'],
                operation_type=case['operation'],
                expected_quality=case['expected_quality'],
                options={
                    'detailed_analysis': True,
                    'quality_factors': True
                }
            )
            
            assert quality_score is not None
            assert 'quality_score' in quality_score
            assert 'quality_factors' in quality_score
            assert 'quality_category' in quality_score
            
            score = quality_score['quality_score']
            category = quality_score['quality_category']
            
            # Verify quality scoring
            assert 0.0 <= score <= 1.0
            assert category in ['low', 'medium', 'high', 'excellent']
            
            # Should generally match expected quality
            if case['expected_quality'] == 'high':
                assert score > 0.6 or category in ['high', 'excellent']
            elif case['expected_quality'] == 'low':
                assert score < 0.5 or category in ['low', 'medium']
        
        # Get quality report
        quality_report = await monitoring_system.get_quality_report(
            session_id='test_quality_001',
            options={
                'quality_trends': True,
                'improvement_suggestions': True,
                'benchmark_comparison': True
            }
        )
        
        assert quality_report is not None
        assert 'overall_quality_score' in quality_report
        assert 'quality_distribution' in quality_report
        assert 'improvement_areas' in quality_report

    @pytest.mark.asyncio
    async def test_system_health_monitoring(self, monitoring_system):
        """Test system health and observability"""
        # Start system health monitoring
        health_monitoring = await monitoring_system.start_system_health_monitoring(
            monitoring_config={
                'resource_usage': True,
                'error_tracking': True,
                'service_availability': True,
                'dependency_health': True,
                'alert_conditions': {
                    'cpu_threshold': 80.0,
                    'memory_threshold': 85.0,
                    'error_rate_threshold': 5.0
                }
            }
        )
        
        assert health_monitoring is not None
        assert 'monitoring_id' in health_monitoring
        assert 'health_check_interval' in health_monitoring
        
        # Simulate system health data
        health_data = [
            {'cpu_usage': 45.2, 'memory_usage': 62.8, 'error_rate': 1.2, 'status': 'healthy'},
            {'cpu_usage': 67.5, 'memory_usage': 78.3, 'error_rate': 2.1, 'status': 'healthy'},
            {'cpu_usage': 89.1, 'memory_usage': 91.2, 'error_rate': 7.3, 'status': 'warning'},  # High usage
            {'cpu_usage': 52.3, 'memory_usage': 68.7, 'error_rate': 1.8, 'status': 'healthy'}
        ]
        
        for i, health_point in enumerate(health_data):
            await monitoring_system.record_health_metrics(
                monitoring_id=health_monitoring['monitoring_id'],
                metrics=health_point,
                timestamp=time.time() + i * 60  # 1 minute intervals
            )
        
        # Get system health status
        health_status = await monitoring_system.get_system_health(
            monitoring_id=health_monitoring['monitoring_id'],
            options={
                'current_status': True,
                'health_trends': True,
                'alert_analysis': True,
                'performance_insights': True
            }
        )
        
        assert health_status is not None
        assert 'current_health' in health_status
        assert 'health_score' in health_status
        assert 'alerts' in health_status
        assert 'recommendations' in health_status
        
        current_health = health_status['current_health']
        health_score = health_status['health_score']
        alerts = health_status['alerts']
        
        # Verify health monitoring
        assert 'cpu_usage' in current_health
        assert 'memory_usage' in current_health
        assert 'error_rate' in current_health
        assert 0.0 <= health_score <= 1.0
        
        # Should have detected the high usage alert
        assert len(alerts) > 0  # Should have alerts for high usage

    @pytest.mark.asyncio
    async def test_real_time_monitoring(self, monitoring_system):
        """Test real-time monitoring capabilities"""
        # Start real-time monitoring
        realtime_session = await monitoring_system.start_realtime_monitoring(
            session_id='test_realtime_001',
            monitoring_config={
                'live_metrics': True,
                'real_time_alerts': True,
                'streaming_analytics': True,
                'dashboard_updates': True
            }
        )
        
        assert realtime_session is not None
        assert 'session_id' in realtime_session
        assert 'streaming_endpoint' in realtime_session
        
        # Simulate real-time events
        realtime_events = [
            {'event_type': 'content_processed', 'processing_time': 0.8, 'quality_score': 0.92},
            {'event_type': 'error_occurred', 'error_type': 'timeout', 'severity': 'medium'},
            {'event_type': 'content_processed', 'processing_time': 1.2, 'quality_score': 0.87},
            {'event_type': 'performance_spike', 'cpu_usage': 85.5, 'memory_usage': 78.2},
            {'event_type': 'content_processed', 'processing_time': 0.6, 'quality_score': 0.95}
        ]
        
        for event in realtime_events:
            await monitoring_system.stream_event(
                session_id='test_realtime_001',
                event=event,
                timestamp=time.time()
            )
        
        # Get real-time analytics
        realtime_analytics = await monitoring_system.get_realtime_analytics(
            session_id='test_realtime_001',
            options={
                'live_dashboard_data': True,
                'event_aggregation': True,
                'trend_detection': True
            }
        )
        
        assert realtime_analytics is not None
        assert 'live_metrics' in realtime_analytics
        assert 'event_summary' in realtime_analytics
        assert 'real_time_trends' in realtime_analytics
        
        event_summary = realtime_analytics['event_summary']
        
        # Should have processed all events
        total_events = sum(event_summary.values()) if isinstance(event_summary, dict) else len(realtime_events)
        assert total_events >= len(realtime_events)

    @pytest.mark.asyncio
    async def test_anomaly_detection(self, monitoring_system):
        """Test anomaly detection in monitoring"""
        # Create baseline normal behavior
        normal_data = [
            {'response_time': 0.5, 'cpu_usage': 45.0, 'memory_usage': 60.0, 'error_rate': 1.0},
            {'response_time': 0.6, 'cpu_usage': 48.0, 'memory_usage': 62.0, 'error_rate': 1.2},
            {'response_time': 0.4, 'cpu_usage': 42.0, 'memory_usage': 58.0, 'error_rate': 0.8},
            {'response_time': 0.7, 'cpu_usage': 50.0, 'memory_usage': 65.0, 'error_rate': 1.5}
        ]
        
        # Create anomalous data
        anomalous_data = [
            {'response_time': 5.2, 'cpu_usage': 95.0, 'memory_usage': 92.0, 'error_rate': 15.0},  # Severe anomaly
            {'response_time': 2.1, 'cpu_usage': 78.0, 'memory_usage': 85.0, 'error_rate': 8.0},   # Moderate anomaly
            {'response_time': 0.5, 'cpu_usage': 46.0, 'memory_usage': 61.0, 'error_rate': 1.1}    # Normal
        ]
        
        # Start anomaly detection
        anomaly_detection = await monitoring_system.start_anomaly_detection(
            detection_config={
                'baseline_learning': True,
                'statistical_analysis': True,
                'machine_learning_detection': True,
                'sensitivity_level': 'medium'
            }
        )
        
        assert anomaly_detection is not None
        assert 'detection_id' in anomaly_detection
        
        # Feed normal data to establish baseline
        for data_point in normal_data:
            await monitoring_system.feed_baseline_data(
                detection_id=anomaly_detection['detection_id'],
                data_point=data_point
            )
        
        # Test anomaly detection on new data
        anomaly_results = []
        for data_point in anomalous_data:
            anomaly_result = await monitoring_system.detect_anomaly(
                detection_id=anomaly_detection['detection_id'],
                data_point=data_point,
                options={
                    'anomaly_scoring': True,
                    'explanation': True,
                    'severity_assessment': True
                }
            )
            
            anomaly_results.append(anomaly_result)
            
            assert anomaly_result is not None
            assert 'is_anomaly' in anomaly_result
            assert 'anomaly_score' in anomaly_result
            assert 'severity' in anomaly_result
        
        # Verify anomaly detection
        assert anomaly_results[0]['is_anomaly'] is True  # Severe anomaly
        assert anomaly_results[1]['is_anomaly'] is True  # Moderate anomaly
        assert anomaly_results[2]['is_anomaly'] is False  # Normal data
        
        # Severe anomaly should have higher score
        assert anomaly_results[0]['anomaly_score'] > anomaly_results[1]['anomaly_score']

    @pytest.mark.asyncio
    async def test_monitoring_alerts(self, monitoring_system):
        """Test monitoring alert system"""
        # Configure alert rules
        alert_rules = {
            'high_response_time': {
                'metric': 'response_time',
                'threshold': 2.0,
                'condition': 'greater_than',
                'severity': 'warning'
            },
            'critical_error_rate': {
                'metric': 'error_rate',
                'threshold': 10.0,
                'condition': 'greater_than',
                'severity': 'critical'
            },
            'low_quality_score': {
                'metric': 'quality_score',
                'threshold': 0.5,
                'condition': 'less_than',
                'severity': 'warning'
            }
        }
        
        # Start alert monitoring
        alert_system = await monitoring_system.setup_alert_system(
            alert_rules=alert_rules,
            notification_config={
                'email_alerts': False,  # Skip for tests
                'webhook_alerts': False,
                'log_alerts': True,
                'dashboard_alerts': True
            }
        )
        
        assert alert_system is not None
        assert 'alert_system_id' in alert_system
        
        # Test alert triggering
        test_metrics = [
            {'response_time': 3.5, 'error_rate': 2.0, 'quality_score': 0.8},  # Should trigger response_time alert
            {'response_time': 1.0, 'error_rate': 15.0, 'quality_score': 0.9},  # Should trigger error_rate alert
            {'response_time': 0.8, 'error_rate': 1.0, 'quality_score': 0.3},  # Should trigger quality_score alert
            {'response_time': 1.2, 'error_rate': 2.5, 'quality_score': 0.85}  # No alerts
        ]
        
        alerts_triggered = []
        for metrics in test_metrics:
            alert_result = await monitoring_system.process_metrics_for_alerts(
                alert_system_id=alert_system['alert_system_id'],
                metrics=metrics,
                timestamp=time.time()
            )
            
            if alert_result and 'alerts' in alert_result:
                alerts_triggered.extend(alert_result['alerts'])
        
        # Verify alerts were triggered
        assert len(alerts_triggered) >= 3  # Should have triggered at least 3 alerts
        
        # Check alert details
        alert_types = [alert['rule_name'] for alert in alerts_triggered]
        assert 'high_response_time' in alert_types
        assert 'critical_error_rate' in alert_types
        assert 'low_quality_score' in alert_types

    @pytest.mark.asyncio
    async def test_monitoring_dashboard(self, monitoring_system):
        """Test monitoring dashboard data generation"""
        # Generate dashboard data
        dashboard_data = await monitoring_system.generate_dashboard_data(
            time_range='24h',
            metrics=[
                'response_time', 'throughput', 'error_rate',
                'quality_score', 'system_health'
            ],
            options={
                'real_time_updates': True,
                'historical_trends': True,
                'comparative_analysis': True,
                'drill_down_data': True
            }
        )
        
        assert dashboard_data is not None
        assert 'metrics_summary' in dashboard_data
        assert 'time_series_data' in dashboard_data
        assert 'system_overview' in dashboard_data
        assert 'performance_insights' in dashboard_data
        
        metrics_summary = dashboard_data['metrics_summary']
        time_series_data = dashboard_data['time_series_data']
        
        # Verify dashboard data structure
        assert 'current_values' in metrics_summary
        assert 'trends' in metrics_summary
        assert 'comparisons' in metrics_summary
        
        # Should have time series data for each metric
        for metric in ['response_time', 'throughput', 'error_rate', 'quality_score']:
            assert metric in time_series_data

    @pytest.mark.asyncio
    async def test_monitoring_reports(self, monitoring_system):
        """Test monitoring report generation"""
        # Generate comprehensive monitoring report
        monitoring_report = await monitoring_system.generate_monitoring_report(
            report_type='comprehensive',
            time_period='1_week',
            report_config={
                'performance_analysis': True,
                'quality_assessment': True,
                'system_health_review': True,
                'trend_analysis': True,
                'recommendations': True
            }
        )
        
        assert monitoring_report is not None
        assert 'report_summary' in monitoring_report
        assert 'performance_section' in monitoring_report
        assert 'quality_section' in monitoring_report
        assert 'health_section' in monitoring_report
        assert 'recommendations' in monitoring_report
        
        report_summary = monitoring_report['report_summary']
        recommendations = monitoring_report['recommendations']
        
        # Verify report structure
        assert 'report_period' in report_summary
        assert 'key_metrics' in report_summary
        assert 'overall_score' in report_summary
        
        # Should have actionable recommendations
        assert isinstance(recommendations, list)
        if len(recommendations) > 0:
            for recommendation in recommendations:
                assert 'category' in recommendation
                assert 'description' in recommendation
                assert 'priority' in recommendation

    @pytest.mark.asyncio
    async def test_batch_monitoring_analysis(self, monitoring_system, performance_test_data):
        """Test batch monitoring analysis"""
        # Simulate batch operation monitoring
        batch_operations = performance_test_data['small_batch'][:5]
        
        start_time = time.time()
        batch_monitoring = await monitoring_system.monitor_batch_operations(
            operations=batch_operations,
            monitoring_config={
                'individual_tracking': True,
                'aggregate_metrics': True,
                'performance_analysis': True,
                'quality_assessment': True
            }
        )
        monitoring_time = time.time() - start_time
        
        assert batch_monitoring is not None
        assert 'batch_metrics' in batch_monitoring
        assert 'individual_results' in batch_monitoring
        assert 'aggregate_statistics' in batch_monitoring
        
        batch_metrics = batch_monitoring['batch_metrics']
        individual_results = batch_monitoring['individual_results']
        
        # Verify batch monitoring
        assert 'total_operations' in batch_metrics
        assert 'average_processing_time' in batch_metrics
        assert 'success_rate' in batch_metrics
        
        assert len(individual_results) == len(batch_operations)
        
        # Should monitor efficiently
        avg_monitoring_time = monitoring_time / len(batch_operations)
        assert avg_monitoring_time < 0.5  # Should monitor quickly

    @pytest.mark.asyncio
    async def test_performance_benchmarks(self, monitoring_system, benchmark_config):
        """Test monitoring system performance benchmarks"""
        # Test monitoring overhead
        operations_to_monitor = 100
        
        start_time = time.time()
        for i in range(operations_to_monitor):
            await monitoring_system.record_operation(
                session_id='benchmark_test',
                operation_type='test_operation',
                duration=0.1,
                success=True
            )
        monitoring_overhead = time.time() - start_time
        
        # Monitoring overhead should be minimal
        overhead_per_operation = monitoring_overhead / operations_to_monitor
        max_overhead = benchmark_config.get('max_monitoring_overhead', 0.01)
        
        assert overhead_per_operation < max_overhead, f"Monitoring overhead {overhead_per_operation:.4f}s, max: {max_overhead}s"

    @pytest.mark.asyncio
    async def test_error_handling(self, monitoring_system):
        """Test monitoring error handling"""
        # Test invalid session ID
        result = await monitoring_system.get_performance_metrics(
            session_id='non_existent_session',
            options={'handle_missing': True}
        )
        assert result is not None  # Should handle gracefully
        
        # Test invalid metrics
        result = await monitoring_system.record_operation(
            session_id='test_session',
            operation_type='test',
            duration=-1.0,  # Invalid duration
            success=True,
            options={'validate_input': True}
        )
        assert result is not None  # Should handle gracefully
        
        # Test system health with missing data
        result = await monitoring_system.get_system_health(
            monitoring_id='non_existent_monitoring',
            options={'handle_missing': True}
        )
        assert result is not None

class TestPerformanceMonitor:
    """Test performance monitor component"""
    
    @pytest.mark.asyncio
    async def test_performance_monitor_initialization(self):
        """Test performance monitor initialization"""
        monitor = PerformanceMonitor()
        assert monitor is not None
        assert hasattr(monitor, 'monitor_performance')

class TestQualityTracker:
    """Test quality tracker component"""
    
    @pytest.mark.asyncio
    async def test_quality_tracker_initialization(self):
        """Test quality tracker initialization"""
        tracker = QualityTracker()
        assert tracker is not None
        assert hasattr(tracker, 'track_quality')

class TestSystemObserver:
    """Test system observer component"""
    
    @pytest.mark.asyncio
    async def test_system_observer_initialization(self):
        """Test system observer initialization"""
        observer = SystemObserver()
        assert observer is not None
        assert hasattr(observer, 'observe_system')

class TestMonitoringConfig:
    """Test monitoring configuration"""
    
    def test_config_creation(self):
        """Test monitoring configuration creation"""
        config = MonitoringConfig(
            monitoring_interval=60,
            metrics_collection=['performance', 'quality', 'health'],
            alert_thresholds={'response_time': 2.0, 'error_rate': 5.0}
        )
        
        assert config.monitoring_interval == 60
        assert 'performance' in config.metrics_collection
        assert config.alert_thresholds['response_time'] == 2.0
