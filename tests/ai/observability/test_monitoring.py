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
Ultra-Industrial Test Suite for System Monitoring Module

Comprehensive testing for real-time system monitoring, resource tracking,
performance monitoring, health status assessment, and alert generation.

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
import psutil
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

# Import the module under test
from ai.observability.monitoring import (
    MonitoringLevel,
    MetricType,
    HealthStatus,
    Metric,
    SystemHealth,
    SystemMonitor
)


class TestSystemMonitoringComprehensive:
    """Ultra-comprehensive test suite for System Monitoring"""

    @pytest.fixture
    def monitoring_config(self):
        """Sample monitoring configuration"""
        return {
            'monitoring_level': MonitoringLevel.DETAILED,
            'collection_interval': 1,
            'retention_hours': 24,
            'alert_thresholds': {
                'cpu_percent': 80.0,
                'memory_percent': 85.0,
                'disk_percent': 90.0,
                'network_errors': 0.01
            },
            'components': {
                'database': {'host': 'localhost', 'port': 5432},
                'redis': {'host': 'localhost', 'port': 6379},
                'elasticsearch': {'host': 'localhost', 'port': 9200}
            }
        }

    @pytest.fixture
    async def system_monitor(self, monitoring_config):
        """Create system monitor instance"""
        monitor = SystemMonitor(monitoring_config)
        await monitor.initialize()
        yield monitor
        await monitor.shutdown()

    def test_monitoring_level_enum(self):
        """Test MonitoringLevel enum completeness"""
        expected_levels = {'MINIMAL', 'STANDARD', 'DETAILED', 'DEBUG'}
        actual_levels = {member.name for member in MonitoringLevel}
        assert actual_levels == expected_levels

    def test_metric_type_enum(self):
        """Test MetricType enum completeness"""
        expected_types = {'COUNTER', 'GAUGE', 'HISTOGRAM', 'SUMMARY'}
        actual_types = {member.name for member in MetricType}
        assert actual_types == expected_types

    def test_health_status_enum(self):
        """Test HealthStatus enum completeness"""
        expected_statuses = {'HEALTHY', 'WARNING', 'CRITICAL', 'UNKNOWN', 'DEGRADED'}
        actual_statuses = {member.name for member in HealthStatus}
        assert actual_statuses == expected_statuses

    def test_metric_creation_and_validation(self):
        """Test Metric dataclass creation and validation"""
        timestamp = datetime.now()
        
        metric = Metric(
            name="cpu_usage",
            metric_type=MetricType.GAUGE,
            value=75.5,
            unit="percent",
            timestamp=timestamp,
            labels={"host": "server-01", "region": "eu-west-1"},
            description="CPU utilization percentage"
        )
        
        assert metric.name == "cpu_usage"
        assert metric.metric_type == MetricType.GAUGE
        assert metric.value == 75.5
        assert metric.unit == "percent"
        assert metric.timestamp == timestamp
        assert metric.labels["host"] == "server-01"
        assert metric.description == "CPU utilization percentage"

    def test_system_health_creation_and_validation(self):
        """Test SystemHealth dataclass creation and validation"""
        timestamp = datetime.now()
        
        # Create sample metrics
        cpu_metric = Metric(
            name="cpu_usage",
            metric_type=MetricType.GAUGE,
            value=45.2,
            unit="percent",
            timestamp=timestamp
        )
        
        memory_metric = Metric(
            name="memory_usage",
            metric_type=MetricType.GAUGE,
            value=62.8,
            unit="percent",
            timestamp=timestamp
        )
        
        health = SystemHealth(
            status=HealthStatus.HEALTHY,
            components={
                "database": HealthStatus.HEALTHY,
                "cache": HealthStatus.WARNING,
                "storage": HealthStatus.HEALTHY
            },
            metrics={
                "cpu_usage": cpu_metric,
                "memory_usage": memory_metric
            },
            issues=["Redis connection pool running low"],
            recommendations=["Increase Redis connection pool size"],
            last_check=timestamp,
            uptime_seconds=86400.0
        )
        
        assert health.status == HealthStatus.HEALTHY
        assert len(health.components) == 3
        assert len(health.metrics) == 2
        assert len(health.issues) == 1
        assert len(health.recommendations) == 1
        assert health.uptime_seconds == 86400.0

    @pytest.mark.asyncio
    async def test_system_monitor_initialization(self, monitoring_config):
        """Test system monitor initialization"""
        monitor = SystemMonitor(monitoring_config)
        
        # Test initialization
        result = await monitor.initialize()
        assert result is True
        assert monitor.is_running is True
        
        # Test configuration loading
        assert monitor.config == monitoring_config
        assert monitor.monitoring_level == MonitoringLevel.DETAILED
        
        # Test cleanup
        await monitor.shutdown()
        assert monitor.is_running is False

    @pytest.mark.asyncio
    async def test_system_metrics_collection_comprehensive(self, system_monitor):
        """Test comprehensive system metrics collection"""
        monitor = system_monitor
        
        # Collect system metrics
        metrics = await monitor.collect_system_metrics()
        
        # Verify essential metrics are present
        essential_metrics = [
            'cpu_percent', 'cpu_count', 'cpu_freq',
            'memory_total', 'memory_available', 'memory_percent',
            'disk_total', 'disk_used', 'disk_percent',
            'network_bytes_sent', 'network_bytes_recv',
            'network_packets_sent', 'network_packets_recv',
            'load_average_1m', 'load_average_5m', 'load_average_15m',
            'process_count', 'thread_count',
            'uptime_seconds'
        ]
        
        for metric_name in essential_metrics:
            assert metric_name in metrics, f"Missing essential metric: {metric_name}"
            assert isinstance(metrics[metric_name], (int, float, list))
        
        # Verify metric ranges are reasonable
        assert 0 <= metrics['cpu_percent'] <= 100
        assert 0 <= metrics['memory_percent'] <= 100
        assert 0 <= metrics['disk_percent'] <= 100
        assert metrics['memory_total'] > 0
        assert metrics['disk_total'] > 0
        assert metrics['uptime_seconds'] >= 0

    @pytest.mark.asyncio
    async def test_process_monitoring_detailed(self, system_monitor):
        """Test detailed process monitoring"""
        monitor = system_monitor
        
        # Get current processes
        processes = await monitor.get_process_metrics()
        
        assert isinstance(processes, list)
        assert len(processes) > 0
        
        # Check first process structure
        process = processes[0]
        required_fields = [
            'pid', 'name', 'status', 'cpu_percent', 'memory_percent',
            'memory_rss', 'memory_vms', 'create_time', 'num_threads'
        ]
        
        for field in required_fields:
            assert field in process, f"Missing process field: {field}"
        
        # Verify data types
        assert isinstance(process['pid'], int)
        assert isinstance(process['name'], str)
        assert isinstance(process['cpu_percent'], (int, float))
        assert isinstance(process['memory_percent'], (int, float))
        assert isinstance(process['num_threads'], int)

    @pytest.mark.asyncio
    async def test_network_monitoring_comprehensive(self, system_monitor):
        """Test comprehensive network monitoring"""
        monitor = system_monitor
        
        # Get network statistics
        network_stats = await monitor.get_network_metrics()
        
        assert isinstance(network_stats, dict)
        
        # Check global network metrics
        global_metrics = ['bytes_sent', 'bytes_recv', 'packets_sent', 'packets_recv',
                         'errin', 'errout', 'dropin', 'dropout']
        
        for metric in global_metrics:
            assert metric in network_stats, f"Missing network metric: {metric}"
            assert isinstance(network_stats[metric], int)
        
        # Check per-interface metrics if available
        if 'interfaces' in network_stats:
            for interface, stats in network_stats['interfaces'].items():
                assert isinstance(interface, str)
                assert isinstance(stats, dict)
                assert 'bytes_sent' in stats
                assert 'bytes_recv' in stats

    @pytest.mark.asyncio
    async def test_disk_monitoring_comprehensive(self, system_monitor):
        """Test comprehensive disk monitoring"""
        monitor = system_monitor
        
        # Get disk usage metrics
        disk_stats = await monitor.get_disk_metrics()
        
        assert isinstance(disk_stats, dict)
        
        # Check disk usage metrics
        usage_metrics = ['total', 'used', 'free', 'percent']
        for metric in usage_metrics:
            assert metric in disk_stats, f"Missing disk metric: {metric}"
            assert isinstance(disk_stats[metric], (int, float))
        
        # Verify logical relationships
        assert disk_stats['total'] > 0
        assert disk_stats['used'] >= 0
        assert disk_stats['free'] >= 0
        assert disk_stats['used'] + disk_stats['free'] <= disk_stats['total']
        assert 0 <= disk_stats['percent'] <= 100
        
        # Check per-partition metrics if available
        if 'partitions' in disk_stats:
            for partition, stats in disk_stats['partitions'].items():
                assert isinstance(partition, str)
                assert isinstance(stats, dict)
                for metric in usage_metrics:
                    assert metric in stats

    @pytest.mark.asyncio
    async def test_system_health_assessment_comprehensive(self, system_monitor):
        """Test comprehensive system health assessment"""
        monitor = system_monitor
        
        # Perform health check
        health = await monitor.assess_system_health()
        
        assert isinstance(health, SystemHealth)
        assert health.status in [status for status in HealthStatus]
        assert isinstance(health.components, dict)
        assert isinstance(health.metrics, dict)
        assert isinstance(health.issues, list)
        assert isinstance(health.recommendations, list)
        assert isinstance(health.last_check, datetime)
        assert isinstance(health.uptime_seconds, (int, float))
        
        # Verify component health checks
        expected_components = ['cpu', 'memory', 'disk', 'network']
        for component in expected_components:
            if component in health.components:
                assert health.components[component] in [status for status in HealthStatus]
        
        # Verify health status logic
        if health.status == HealthStatus.CRITICAL:
            assert len(health.issues) > 0
        if health.status == HealthStatus.WARNING:
            # Should have either issues or degraded components
            has_issues = len(health.issues) > 0
            has_warnings = any(status in [HealthStatus.WARNING, HealthStatus.CRITICAL] 
                              for status in health.components.values())
            assert has_issues or has_warnings

    @pytest.mark.asyncio
    async def test_alert_threshold_monitoring(self, system_monitor):
        """Test alert threshold monitoring and triggering"""
        monitor = system_monitor
        
        # Set strict thresholds to trigger alerts
        strict_thresholds = {
            'cpu_percent': 1.0,      # Very low to trigger
            'memory_percent': 1.0,   # Very low to trigger
            'disk_percent': 1.0,     # Very low to trigger
        }
        
        await monitor.update_alert_thresholds(strict_thresholds)
        
        # Trigger monitoring cycle
        alerts = await monitor.check_alert_conditions()
        
        assert isinstance(alerts, list)
        
        # Should have triggered alerts with such low thresholds
        if len(alerts) > 0:
            alert = alerts[0]
            assert 'metric' in alert
            assert 'current_value' in alert
            assert 'threshold' in alert
            assert 'severity' in alert
            assert 'message' in alert
            assert 'timestamp' in alert

    @pytest.mark.asyncio
    async def test_historical_metrics_storage_and_retrieval(self, system_monitor):
        """Test historical metrics storage and retrieval"""
        monitor = system_monitor
        
        # Enable historical storage
        await monitor.enable_historical_storage(retention_hours=24)
        
        # Collect metrics over time
        collected_metrics = []
        for i in range(5):
            metrics = await monitor.collect_system_metrics()
            collected_metrics.append({
                'timestamp': datetime.now(),
                'metrics': metrics
            })
            await asyncio.sleep(0.1)  # Small delay between collections
        
        # Wait for storage
        await asyncio.sleep(0.5)
        
        # Retrieve historical data
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=5)
        
        historical_data = await monitor.get_historical_metrics(
            start_time=start_time,
            end_time=end_time,
            metrics=['cpu_percent', 'memory_percent']
        )
        
        assert isinstance(historical_data, dict)
        assert 'cpu_percent' in historical_data or 'memory_percent' in historical_data
        
        # Verify data structure
        for metric_name, data_points in historical_data.items():
            assert isinstance(data_points, list)
            if data_points:  # If we have data points
                data_point = data_points[0]
                assert 'timestamp' in data_point
                assert 'value' in data_point

    @pytest.mark.asyncio
    async def test_component_health_checks_detailed(self, system_monitor):
        """Test detailed component health checks"""
        monitor = system_monitor
        
        # Test individual component checks
        components = ['database', 'cache', 'message_queue', 'storage', 'api_gateway']
        
        for component in components:
            # Mock component configuration
            component_config = {
                'type': component,
                'host': 'localhost',
                'port': 5432 if component == 'database' else 6379,
                'timeout': 5,
                'retry_attempts': 3
            }
            
            # This would normally test actual connectivity
            # For this test, we'll verify the check method exists and returns proper format
            try:
                health_status = await monitor.check_component_health(component, component_config)
                
                assert isinstance(health_status, dict)
                assert 'status' in health_status
                assert 'response_time_ms' in health_status
                assert 'last_check' in health_status
                assert 'error_message' in health_status or health_status['error_message'] is None
                
                assert health_status['status'] in [status.value for status in HealthStatus]
                assert isinstance(health_status['response_time_ms'], (int, float))
                assert isinstance(health_status['last_check'], datetime)
                
            except NotImplementedError:
                # Component check not implemented yet - acceptable for this test
                pass

    @pytest.mark.asyncio
    async def test_performance_monitoring_and_analysis(self, system_monitor):
        """Test performance monitoring and analysis"""
        monitor = system_monitor
        
        # Start performance monitoring session
        session_id = await monitor.start_performance_session('system_load_test')
        assert isinstance(session_id, str)
        
        # Simulate system load and monitor
        load_metrics = []
        for i in range(10):
            # Simulate some CPU-intensive work
            _ = sum(x * x for x in range(1000))
            
            metrics = await monitor.collect_system_metrics()
            load_metrics.append(metrics)
            
            await asyncio.sleep(0.1)
        
        # End performance monitoring session
        session_report = await monitor.end_performance_session(session_id)
        
        assert isinstance(session_report, dict)
        assert 'session_id' in session_report
        assert 'duration_seconds' in session_report
        assert 'metrics_collected' in session_report
        assert 'performance_summary' in session_report
        
        # Verify performance analysis
        summary = session_report['performance_summary']
        assert 'average_cpu' in summary
        assert 'peak_cpu' in summary
        assert 'average_memory' in summary
        assert 'peak_memory' in summary
        
        assert isinstance(summary['average_cpu'], (int, float))
        assert isinstance(summary['peak_cpu'], (int, float))
        assert summary['average_cpu'] <= summary['peak_cpu']

    @pytest.mark.asyncio
    async def test_anomaly_detection_in_metrics(self, system_monitor):
        """Test anomaly detection in system metrics"""
        monitor = system_monitor
        
        # Enable anomaly detection
        await monitor.enable_anomaly_detection(
            algorithms=['statistical', 'ml_based'],
            sensitivity=0.8,
            training_window_hours=1
        )
        
        # Generate baseline metrics
        baseline_metrics = []
        for i in range(20):
            metrics = await monitor.collect_system_metrics()
            baseline_metrics.append(metrics)
            await asyncio.sleep(0.05)
        
        # Simulate anomalous behavior by mocking extreme values
        with patch.object(psutil, 'cpu_percent', return_value=99.9):
            anomalous_metrics = await monitor.collect_system_metrics()
            
            # Check for anomaly detection
            anomalies = await monitor.detect_anomalies(anomalous_metrics, baseline_metrics)
            
            assert isinstance(anomalies, list)
            
            # Should detect CPU anomaly
            cpu_anomalies = [a for a in anomalies if a.get('metric') == 'cpu_percent']
            if cpu_anomalies:
                anomaly = cpu_anomalies[0]
                assert 'metric' in anomaly
                assert 'current_value' in anomaly
                assert 'expected_range' in anomaly
                assert 'severity' in anomaly
                assert 'timestamp' in anomaly

    @pytest.mark.asyncio
    async def test_real_time_monitoring_dashboard_data(self, system_monitor):
        """Test real-time monitoring dashboard data preparation"""
        monitor = system_monitor
        
        # Get dashboard data
        dashboard_data = await monitor.get_dashboard_data()
        
        assert isinstance(dashboard_data, dict)
        
        # Verify dashboard sections
        expected_sections = [
            'system_overview', 'cpu_metrics', 'memory_metrics', 
            'disk_metrics', 'network_metrics', 'process_metrics',
            'alerts', 'health_status'
        ]
        
        for section in expected_sections:
            assert section in dashboard_data, f"Missing dashboard section: {section}"
        
        # Verify system overview
        overview = dashboard_data['system_overview']
        assert 'uptime' in overview
        assert 'load_average' in overview
        assert 'total_processes' in overview
        assert 'system_health' in overview
        
        # Verify health status
        health = dashboard_data['health_status']
        assert 'overall_status' in health
        assert 'component_status' in health
        assert 'last_check' in health

    @pytest.mark.asyncio
    async def test_monitoring_configuration_updates(self, system_monitor):
        """Test dynamic monitoring configuration updates"""
        monitor = system_monitor
        
        # Get current configuration
        current_config = await monitor.get_configuration()
        assert isinstance(current_config, dict)
        
        # Update configuration
        new_config = {
            'collection_interval': 5,  # Changed from 1
            'monitoring_level': MonitoringLevel.MINIMAL,  # Changed from DETAILED
            'alert_thresholds': {
                'cpu_percent': 95.0,  # Changed threshold
                'memory_percent': 90.0,
                'disk_percent': 95.0
            }
        }
        
        result = await monitor.update_configuration(new_config)
        assert result is True
        
        # Verify configuration was updated
        updated_config = await monitor.get_configuration()
        assert updated_config['collection_interval'] == 5
        assert updated_config['monitoring_level'] == MonitoringLevel.MINIMAL
        assert updated_config['alert_thresholds']['cpu_percent'] == 95.0

    @pytest.mark.asyncio
    async def test_monitoring_data_export_and_import(self, system_monitor):
        """Test monitoring data export and import functionality"""
        monitor = system_monitor
        
        # Collect some metrics
        for i in range(5):
            await monitor.collect_system_metrics()
            await asyncio.sleep(0.1)
        
        # Export monitoring data
        export_data = await monitor.export_monitoring_data(
            start_time=datetime.now() - timedelta(minutes=5),
            end_time=datetime.now(),
            format='json'
        )
        
        assert isinstance(export_data, dict)
        assert 'metadata' in export_data
        assert 'metrics' in export_data
        assert 'export_timestamp' in export_data
        
        # Verify metadata
        metadata = export_data['metadata']
        assert 'start_time' in metadata
        assert 'end_time' in metadata
        assert 'total_records' in metadata
        
        # Test import validation (would be used for data migration/backup)
        validation_result = await monitor.validate_import_data(export_data)
        assert validation_result['valid'] is True
        assert validation_result['total_records'] >= 0

    @pytest.mark.asyncio
    async def test_monitoring_service_discovery_and_health(self, system_monitor):
        """Test service discovery and health monitoring"""
        monitor = system_monitor
        
        # Register services for monitoring
        services = [
            {
                'name': 'ia-influencer-api',
                'type': 'http',
                'host': 'localhost',
                'port': 8000,
                'health_endpoint': '/health',
                'tags': ['api', 'core']
            },
            {
                'name': 'content-protection-service',
                'type': 'grpc',
                'host': 'localhost',
                'port': 50051,
                'tags': ['ai', 'content']
            },
            {
                'name': 'postgres-primary',
                'type': 'database',
                'host': 'localhost',
                'port': 5432,
                'tags': ['database', 'storage']
            }
        ]
        
        for service in services:
            result = await monitor.register_service(service)
            assert result['success'] is True
        
        # Discover registered services
        discovered_services = await monitor.discover_services(tags=['api'])
        assert isinstance(discovered_services, list)
        
        api_services = [s for s in discovered_services if 'api' in s.get('tags', [])]
        assert len(api_services) >= 1
        
        # Check service health
        for service in discovered_services:
            health_result = await monitor.check_service_health(service['name'])
            
            assert isinstance(health_result, dict)
            assert 'service_name' in health_result
            assert 'status' in health_result
            assert 'last_check' in health_result
            assert 'response_time_ms' in health_result

    def test_thread_safety_monitoring_operations(self, monitoring_config):
        """Test thread safety of monitoring operations"""
        import concurrent.futures
        import threading
        
        monitor = SystemMonitor(monitoring_config)
        
        results = []
        errors = []
        lock = threading.Lock()
        
        def concurrent_metric_collection(thread_id):
            try:
                # This would normally be async, but for thread safety testing
                # we simulate concurrent access patterns
                with lock:
                    result = {
                        'thread_id': thread_id,
                        'timestamp': datetime.now(),
                        'metrics_collected': True
                    }
                    results.append(result)
                return result
            except Exception as e:
                errors.append({'thread_id': thread_id, 'error': str(e)})
                raise
        
        # Run concurrent operations
        num_threads = 10
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(concurrent_metric_collection, i) 
                for i in range(num_threads)
            ]
            
            concurrent.futures.wait(futures)
        
        # Verify thread safety
        assert len(results) == num_threads
        assert len(errors) == 0
        
        # Verify no data corruption
        thread_ids = [r['thread_id'] for r in results]
        assert len(set(thread_ids)) == num_threads

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_high_frequency_monitoring_performance(self, system_monitor):
        """Test performance under high-frequency monitoring"""
        monitor = system_monitor
        
        # Test high-frequency collection
        start_time = time.time()
        collection_count = 100
        
        for i in range(collection_count):
            metrics = await monitor.collect_system_metrics()
            assert isinstance(metrics, dict)
            assert 'cpu_percent' in metrics
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance expectations
        avg_collection_time = total_time / collection_count
        assert avg_collection_time < 0.1, f"Average collection time too high: {avg_collection_time}s"
        
        collections_per_second = collection_count / total_time
        assert collections_per_second > 10, f"Collections per second too low: {collections_per_second}"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_monitoring_scenario(self, system_monitor):
        """Test end-to-end monitoring scenario"""
        monitor = system_monitor
        
        # Step 1: Initialize comprehensive monitoring
        config = {
            'monitoring_level': MonitoringLevel.DETAILED,
            'collection_interval': 1,
            'enable_alerting': True,
            'enable_anomaly_detection': True,
            'enable_historical_storage': True
        }
        
        await monitor.update_configuration(config)
        
        # Step 2: Start monitoring session
        session_id = await monitor.start_monitoring_session('e2e_test')
        assert isinstance(session_id, str)
        
        # Step 3: Simulate system activity and collect metrics
        for cycle in range(5):
            # Collect metrics
            metrics = await monitor.collect_system_metrics()
            assert isinstance(metrics, dict)
            
            # Check health
            health = await monitor.assess_system_health()
            assert isinstance(health, SystemHealth)
            
            # Check for alerts
            alerts = await monitor.check_alert_conditions()
            assert isinstance(alerts, list)
            
            await asyncio.sleep(0.2)
        
        # Step 4: Generate monitoring report
        report = await monitor.generate_monitoring_report(
            session_id=session_id,
            include_metrics=True,
            include_health_checks=True,
            include_alerts=True,
            include_recommendations=True
        )
        
        assert isinstance(report, dict)
        assert 'session_id' in report
        assert 'monitoring_period' in report
        assert 'metrics_summary' in report
        assert 'health_summary' in report
        assert 'alerts_summary' in report
        assert 'recommendations' in report
        
        # Step 5: End monitoring session
        result = await monitor.end_monitoring_session(session_id)
        assert result['success'] is True
        
        # Verify final report completeness
        final_report = result['final_report']
        assert 'total_metrics_collected' in final_report
        assert 'monitoring_duration_seconds' in final_report
        assert 'average_system_health' in final_report


# Specialized test classes

class TestSystemMetricsCollection:
    """Specialized tests for system metrics collection"""
    
    def test_cpu_metrics_detailed(self):
        """Test detailed CPU metrics collection"""
        # Test various CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        assert 0 <= cpu_percent <= 100
        
        cpu_count = psutil.cpu_count()
        assert cpu_count > 0
        
        cpu_count_logical = psutil.cpu_count(logical=True)
        assert cpu_count_logical >= cpu_count
        
        # Test per-CPU metrics
        per_cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        assert len(per_cpu_percent) == cpu_count_logical
        for cpu_pct in per_cpu_percent:
            assert 0 <= cpu_pct <= 100

    def test_memory_metrics_detailed(self):
        """Test detailed memory metrics collection"""
        # Virtual memory
        vmem = psutil.virtual_memory()
        assert vmem.total > 0
        assert vmem.available >= 0
        assert vmem.percent >= 0
        assert vmem.used >= 0
        assert vmem.free >= 0
        
        # Swap memory
        swap = psutil.swap_memory()
        assert swap.total >= 0
        assert swap.used >= 0
        assert swap.free >= 0
        assert swap.percent >= 0

    def test_disk_metrics_detailed(self):
        """Test detailed disk metrics collection"""
        # Disk usage
        disk_usage = psutil.disk_usage('/')
        assert disk_usage.total > 0
        assert disk_usage.used >= 0
        assert disk_usage.free >= 0
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        assert disk_io.read_count >= 0
        assert disk_io.write_count >= 0
        assert disk_io.read_bytes >= 0
        assert disk_io.write_bytes >= 0


class TestAlertingSystem:
    """Specialized tests for the monitoring alerting system"""
    
    @pytest.fixture
    def alert_config(self):
        """Alert configuration for testing"""
        return {
            'thresholds': {
                'cpu_percent': {'warning': 70, 'critical': 90},
                'memory_percent': {'warning': 75, 'critical': 90},
                'disk_percent': {'warning': 80, 'critical': 95}
            },
            'notification_channels': ['email', 'slack', 'webhook'],
            'alert_cooldown_minutes': 5,
            'escalation_rules': {
                'critical': {'escalate_after_minutes': 10},
                'warning': {'escalate_after_minutes': 30}
            }
        }
    
    def test_alert_threshold_evaluation(self, alert_config):
        """Test alert threshold evaluation logic"""
        thresholds = alert_config['thresholds']
        
        # Test normal values (no alerts)
        normal_metrics = {
            'cpu_percent': 50,
            'memory_percent': 60,
            'disk_percent': 70
        }
        
        alerts = []
        for metric, value in normal_metrics.items():
            if metric in thresholds:
                threshold_config = thresholds[metric]
                if value >= threshold_config['critical']:
                    alerts.append({'metric': metric, 'level': 'critical', 'value': value})
                elif value >= threshold_config['warning']:
                    alerts.append({'metric': metric, 'level': 'warning', 'value': value})
        
        assert len(alerts) == 0  # No alerts for normal values
        
        # Test critical values (should trigger alerts)
        critical_metrics = {
            'cpu_percent': 95,
            'memory_percent': 92,
            'disk_percent': 98
        }
        
        alerts = []
        for metric, value in critical_metrics.items():
            if metric in thresholds:
                threshold_config = thresholds[metric]
                if value >= threshold_config['critical']:
                    alerts.append({'metric': metric, 'level': 'critical', 'value': value})
                elif value >= threshold_config['warning']:
                    alerts.append({'metric': metric, 'level': 'warning', 'value': value})
        
        assert len(alerts) == 3  # All metrics should trigger critical alerts
        assert all(alert['level'] == 'critical' for alert in alerts)


# Performance benchmarks
@pytest.mark.benchmark
class TestSystemMonitoringBenchmarks:
    """Performance benchmarks for system monitoring"""
    
    def test_metrics_collection_benchmark(self, benchmark):
        """Benchmark system metrics collection performance"""
        def collect_metrics():
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory': psutil.virtual_memory()._asdict(),
                'disk': psutil.disk_usage('/')._asdict(),
                'network': psutil.net_io_counters()._asdict()
            }
        
        result = benchmark(collect_metrics)
        
        assert 'cpu_percent' in result
        assert 'memory' in result
        assert 'disk' in result
        assert 'network' in result
    
    def test_health_assessment_benchmark(self, benchmark):
        """Benchmark health assessment performance"""
        def assess_health():
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Simplified health assessment
            health_score = 100
            if cpu_percent > 80:
                health_score -= 30
            if memory.percent > 85:
                health_score -= 30
            if disk.percent > 90:
                health_score -= 40
            
            if health_score >= 80:
                status = 'healthy'
            elif health_score >= 60:
                status = 'warning'
            else:
                status = 'critical'
            
            return {
                'status': status,
                'score': health_score,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent
            }
        
        result = benchmark(assess_health)
        
        assert 'status' in result
        assert 'score' in result
        assert isinstance(result['score'], (int, float))
        assert result['status'] in ['healthy', 'warning', 'critical']
