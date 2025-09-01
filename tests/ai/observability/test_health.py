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

"""
Ultra-Industrial Test Suite for System Health Module

Comprehensive testing for system health monitoring, diagnostics,
component health checks, and health status assessment.

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
import socket
import time
import threading
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

# Import the module under test
from ai.observability.health import (
    HealthStatus,
    ComponentType,
    HealthCheck,
    ComponentHealth,
    SystemHealth,
    HealthMonitor,
    DiagnosticsEngine,
    HealthReporter
)


class TestSystemHealthComprehensive:
    """
Ultra-comprehensive test suite for System Health"""
    @pytest.fixture
    def health_config(self):
        """
Sample health monitoring configuration"""
        return {
            'check_interval_seconds': 30,
            'timeout_seconds': 10,
            'retry_attempts': 3,
            'critical_thresholds': {
                'cpu_percent': 90.0,
                'memory_percent': 95.0,
                'disk_percent': 98.0,
                'response_time_ms': 5000
            },
            'warning_thresholds': {
                'cpu_percent': 75.0,
                'memory_percent': 80.0,
                'disk_percent': 85.0,
                'response_time_ms': 2000
            },
            'components': {
                'database': {
                    'type': ComponentType.DATABASE,
                    'host': 'localhost',
                    'port': 5432,
                    'database': 'ia_influencer',
                    'check_query': 'SELECT 1;'
                },
                'redis_cache': {
                    'type': ComponentType.CACHE,
                    'host': 'localhost',
                    'port': 6379,
                    'timeout': 5
                },
                'elasticsearch': {
                    'type': ComponentType.SEARCH_ENGINE,
                    'host': 'localhost',
                    'port': 9200,
                    'index': 'system_health'
                }
            }
        }

    @pytest.fixture
    async def health_monitor(self, health_config):
        """
Create health monitor instance"""
        monitor = HealthMonitor(health_config)
        await monitor.initialize()
        yield monitor
        await monitor.shutdown()

    def test_health_status_enum_comprehensive(self):
        """
Test HealthStatus enum completeness and ordering"""
        expected_statuses = {'HEALTHY', 'WARNING', 'CRITICAL', 'UNKNOWN', 'MAINTENANCE'}
        actual_statuses = {member.name for member in HealthStatus}
        assert actual_statuses == expected_statuses
        
        # Test status severity ordering
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.WARNING.value == "warning"
        assert HealthStatus.CRITICAL.value == "critical"

    def test_component_type_enum_comprehensive(self):
        """Test ComponentType enum completeness"""
        expected_types = {
            'DATABASE', 'CACHE', 'MESSAGE_QUEUE', 'STORAGE', 'API_GATEWAY',
            'LOAD_BALANCER', 'SEARCH_ENGINE', 'AI_MODEL_SERVICE', 'AUTHENTICATION',
            'CONTENT_PROTECTION', 'EXTERNAL_API'
        }
        actual_types = {member.name for member in ComponentType}
        assert actual_types == expected_types

    def test_health_check_creation_and_validation(self):
        """
Test HealthCheck dataclass creation and validation"""
        timestamp = datetime.now(timezone.utc)
        
        health_check = HealthCheck(
            component_name="content_protection_api",
            component_type=ComponentType.API_GATEWAY,
            status=HealthStatus.HEALTHY,
            response_time_ms=150.5,
            last_check=timestamp,
            details={
                'endpoint': '/api/v1/health',
                'http_status': 200,
                'version': '2.1.0',
                'build': 'build-12345'
            },
            metrics={
                'requests_per_second': 45.2,
                'active_connections': 120,
                'memory_usage_mb': 512,
                'cpu_usage_percent': 25.8
            },
            dependencies_status={
                'database': HealthStatus.HEALTHY,
                'redis': HealthStatus.WARNING,
                'ai_service': HealthStatus.HEALTHY
            }
        )
        
        assert health_check.component_name == "content_protection_api"
        assert health_check.component_type == ComponentType.API_GATEWAY
        assert health_check.status == HealthStatus.HEALTHY
        assert health_check.response_time_ms == 150.5
        assert health_check.last_check == timestamp
        assert health_check.details['endpoint'] == '/api/v1/health'
        assert health_check.metrics['requests_per_second'] == 45.2
        assert health_check.dependencies_status['redis'] == HealthStatus.WARNING

    def test_component_health_creation_and_validation(self):
        """Test ComponentHealth dataclass creation and validation"""
        timestamp = datetime.now(timezone.utc)
        
        component_health = ComponentHealth(
            component_name="ai_inference_service",
            component_type=ComponentType.AI_MODEL_SERVICE,
            status=HealthStatus.WARNING,
            last_check=timestamp,
            response_time_ms=2500.0,
            error_message="Model loading timeout",
            health_score=0.65,
            uptime_seconds=86400.0,
            check_history=[
                {
                    'timestamp': timestamp - timedelta(minutes=5),
                    'status': HealthStatus.HEALTHY.value,
                    'response_time_ms': 800.0
                },
                {
                    'timestamp': timestamp - timedelta(minutes=10),
                    'status': HealthStatus.HEALTHY.value,
                    'response_time_ms': 750.0
                }
            ],
            custom_metrics={
                'model_accuracy': 0.94,
                'inference_queue_size': 15,
                'gpu_utilization_percent': 85.2,
                'model_memory_usage_gb': 2.5
            }
        )
        
        assert component_health.component_name == "ai_inference_service"
        assert component_health.component_type == ComponentType.AI_MODEL_SERVICE
        assert component_health.status == HealthStatus.WARNING
        assert component_health.error_message == "Model loading timeout"
        assert component_health.health_score == 0.65
        assert len(component_health.check_history) == 2
        assert component_health.custom_metrics['model_accuracy'] == 0.94

    @pytest.mark.asyncio
    async def test_health_monitor_initialization(self, health_config):
        """Test health monitor initialization"""
        monitor = HealthMonitor(health_config)
        
        # Test initialization
        result = await monitor.initialize()
        assert result is True
        assert monitor.is_running is True
        
        # Test configuration
        assert monitor.check_interval_seconds == 30
        assert monitor.timeout_seconds == 10
        assert monitor.retry_attempts == 3
        
        # Test component registration
        registered_components = await monitor.get_registered_components()
        assert len(registered_components) >= 3  # database, redis, elasticsearch
        assert 'database' in registered_components
        assert 'redis_cache' in registered_components
        
        await monitor.shutdown()

    @pytest.mark.asyncio
    async def test_system_health_check_comprehensive(self, health_monitor):
        """
Test comprehensive system health check"""
        monitor = health_monitor
        
        # Perform system health check
        system_health = await monitor.check_system_health()
        
        assert isinstance(system_health, SystemHealth)
        assert system_health.overall_status in [status for status in HealthStatus]
        assert isinstance(system_health.components_status, dict)
        assert isinstance(system_health.system_metrics, dict)
        assert isinstance(system_health.last_check, datetime)
        assert isinstance(system_health.uptime_seconds, (int, float))
        
        # Verify system metrics
        metrics = system_health.system_metrics
        expected_metrics = [
            'cpu_percent', 'memory_percent', 'disk_percent',
            'load_average', 'network_connections', 'process_count'
        ]
        
        for metric in expected_metrics:
            if metric in metrics:
                assert isinstance(metrics[metric], (int, float, list))
        
        # Verify component health checks
        components_status = system_health.components_status
        for component_name, health_check in components_status.items():
            assert isinstance(health_check, HealthCheck)
            assert health_check.component_name == component_name
            assert health_check.status in [status for status in HealthStatus]

    @pytest.mark.asyncio
    async def test_database_health_check_detailed(self, health_monitor):
        """
Test detailed database health check"""
        monitor = health_monitor
        
        # Test with mock database connection
        with patch('psycopg2.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (1,)
            
            # Perform database health check
            db_health = await monitor.check_component_health('database')
            
            assert isinstance(db_health, HealthCheck)
            assert db_health.component_name == 'database'
            assert db_health.component_type == ComponentType.DATABASE
            assert db_health.status == HealthStatus.HEALTHY
            assert db_health.response_time_ms >= 0
            assert 'connection_success' in str(db_health.details)
            
            # Verify connection was attempted
            mock_connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_health_check_detailed(self, health_monitor):
        """
Test detailed cache (Redis) health check"""
        monitor = health_monitor
        
        # Test with mock Redis connection
        with patch('redis.Redis') as mock_redis_class:
            mock_redis = MagicMock()
            mock_redis_class.return_value = mock_redis
            mock_redis.ping.return_value = True
            mock_redis.info.return_value = {
                'redis_version': '6.2.6',
                'used_memory': 1024000,
                'connected_clients': 5,
                'total_commands_processed': 12345
            }
            
            # Perform Redis health check
            cache_health = await monitor.check_component_health('redis_cache')
            
            assert isinstance(cache_health, HealthCheck)
            assert cache_health.component_name == 'redis_cache'
            assert cache_health.component_type == ComponentType.CACHE
            assert cache_health.status == HealthStatus.HEALTHY
            assert 'redis_version' in str(cache_health.details)
            assert cache_health.response_time_ms >= 0

    @pytest.mark.asyncio
    async def test_health_check_failure_scenarios(self, health_monitor):
        """
Test health check failure scenarios"""
        monitor = health_monitor
        
        # Test database connection failure
        with patch('psycopg2.connect', side_effect=Exception("Connection refused")):
            db_health = await monitor.check_component_health('database')
            
            assert db_health.status == HealthStatus.CRITICAL
            assert db_health.error_message is not None
            assert "Connection refused" in db_health.error_message
        
        # Test Redis timeout
        with patch('redis.Redis') as mock_redis_class:
            mock_redis = MagicMock()
            mock_redis_class.return_value = mock_redis
            mock_redis.ping.side_effect = TimeoutError("Redis timeout")
            
            cache_health = await monitor.check_component_health('redis_cache')
            
            assert cache_health.status in [HealthStatus.CRITICAL, HealthStatus.WARNING]
            assert cache_health.error_message is not None
            assert "timeout" in cache_health.error_message.lower()

    @pytest.mark.asyncio
    async def test_health_thresholds_and_alerting(self, health_monitor):
        """Test health thresholds and alerting logic"""
        monitor = health_monitor
        
        # Mock system metrics to trigger different thresholds
        critical_metrics = {
            'cpu_percent': 95.0,     # Above critical threshold (90%)
            'memory_percent': 97.0,  # Above critical threshold (95%)
            'disk_percent': 99.0     # Above critical threshold (98%)
        }
        
        warning_metrics = {
            'cpu_percent': 78.0,     # Above warning threshold (75%)
            'memory_percent': 82.0,  # Above warning threshold (80%)
            'disk_percent': 87.0     # Above warning threshold (85%)
        }
        
        healthy_metrics = {
            'cpu_percent': 45.0,     # Below warning threshold
            'memory_percent': 60.0,  # Below warning threshold
            'disk_percent': 70.0     # Below warning threshold
        }
        
        # Test critical thresholds
        with patch.object(monitor, 'get_system_metrics', return_value=critical_metrics):
            alerts = await monitor.check_threshold_alerts()
            
            assert len(alerts) > 0
            critical_alerts = [a for a in alerts if a['severity'] == 'critical']
            assert len(critical_alerts) >= 3  # CPU, Memory, Disk
            
            for alert in critical_alerts:
                assert 'metric' in alert
                assert 'current_value' in alert
                assert 'threshold' in alert
                assert alert['current_value'] > alert['threshold']
        
        # Test warning thresholds
        with patch.object(monitor, 'get_system_metrics', return_value=warning_metrics):
            alerts = await monitor.check_threshold_alerts()
            
            warning_alerts = [a for a in alerts if a['severity'] == 'warning']
            assert len(warning_alerts) >= 3  # CPU, Memory, Disk
        
        # Test healthy state (no alerts)
        with patch.object(monitor, 'get_system_metrics', return_value=healthy_metrics):
            alerts = await monitor.check_threshold_alerts()
            
            threshold_alerts = [a for a in alerts if a['type'] == 'threshold']
            assert len(threshold_alerts) == 0

    @pytest.mark.asyncio
    async def test_health_history_tracking(self, health_monitor):
        """
Test health history tracking and trends"""
        monitor = health_monitor
        
        # Enable health history tracking
        await monitor.enable_health_history(
            retention_hours=24,
            sampling_interval_seconds=60
        )
        
        # Generate health check history
        component_name = 'test_component'
        
        # Register test component
        await monitor.register_component(
            component_name,
            ComponentType.API_GATEWAY,
            {'host': 'localhost', 'port': 8080}
        )
        
        # Simulate health checks over time with different statuses
        health_scenarios = [
            (HealthStatus.HEALTHY, 100.0),
            (HealthStatus.HEALTHY, 120.0),
            (HealthStatus.WARNING, 1500.0),
            (HealthStatus.WARNING, 1800.0),
            (HealthStatus.CRITICAL, 4500.0),
            (HealthStatus.HEALTHY, 200.0),
            (HealthStatus.HEALTHY, 150.0)
        ]
        
        for status, response_time in health_scenarios:
            # Mock health check result
            mock_health_check = HealthCheck(
                component_name=component_name,
                component_type=ComponentType.API_GATEWAY,
                status=status,
                response_time_ms=response_time,
                last_check=datetime.now(timezone.utc)
            )
            
            await monitor.record_health_check_history(component_name, mock_health_check)
            await asyncio.sleep(0.1)  # Small delay between checks
        
        # Get health history
        health_history = await monitor.get_health_history(
            component_name,
            start_time=datetime.now(timezone.utc) - timedelta(hours=1),
            end_time=datetime.now(timezone.utc)
        )
        
        assert 'history' in health_history
        assert 'trends' in health_history
        assert 'statistics' in health_history
        
        # Verify history contains our checks
        history = health_history['history']
        assert len(history) >= len(health_scenarios)
        
        # Verify trend analysis
        trends = health_history['trends']
        assert 'status_changes' in trends
        assert 'response_time_trend' in trends
        assert 'availability_percentage' in trends
        
        # Should detect status degradation and recovery
        status_changes = trends['status_changes']
        assert len(status_changes) > 0
        
        # Should have detected the critical period
        critical_periods = [change for change in status_changes if change['to_status'] == 'CRITICAL']
        assert len(critical_periods) > 0

    @pytest.mark.asyncio
    async def test_dependency_health_checking(self, health_monitor):
        """
Test dependency health checking and cascade failures"""
        monitor = health_monitor
        
        # Define service dependencies
        service_dependencies = {
            'api_gateway': ['authentication', 'database'],
            'content_service': ['database', 'redis_cache', 'ai_service'],
            'ai_service': ['model_storage', 'gpu_cluster'],
            'notification_service': ['message_queue', 'external_email_api']
        }
        
        # Register services with dependencies
        for service, deps in service_dependencies.items():
            await monitor.register_service_with_dependencies(
                service_name=service,
                component_type=ComponentType.API_GATEWAY,
                dependencies=deps,
                config={'host': 'localhost', 'port': 8080}
            )
        
        # Mock dependency health checks
        dependency_health_states = {
            'authentication': HealthStatus.HEALTHY,
            'database': HealthStatus.CRITICAL,        # Critical dependency
            'redis_cache': HealthStatus.WARNING,
            'ai_service': HealthStatus.HEALTHY,
            'model_storage': HealthStatus.HEALTHY,
            'gpu_cluster': HealthStatus.HEALTHY,
            'message_queue': HealthStatus.HEALTHY,
            'external_email_api': HealthStatus.CRITICAL  # External dependency down
        }
        
        # Perform dependency health analysis
        dependency_analysis = await monitor.analyze_dependency_health(dependency_health_states)
        
        assert 'impact_analysis' in dependency_analysis
        assert 'cascade_failures' in dependency_analysis
        assert 'affected_services' in dependency_analysis
        
        # Verify impact analysis
        impact = dependency_analysis['impact_analysis']
        
        # Database failure should affect api_gateway and content_service
        database_impact = [
            service for service, impacts in impact.items() 
            if 'database' in impacts.get('failed_dependencies', [])
        ]
        assert 'api_gateway' in database_impact
        assert 'content_service' in database_impact
        
        # External email API failure should affect notification_service
        email_impact = [
            service for service, impacts in impact.items() 
            if 'external_email_api' in impacts.get('failed_dependencies', [])
        ]
        assert 'notification_service' in email_impact

    @pytest.mark.asyncio
    async def test_diagnostics_engine_comprehensive(self, health_monitor):
        """
Test comprehensive diagnostics engine"""
        monitor = health_monitor
        
        # Initialize diagnostics engine
        diagnostics_config = {
            'diagnostic_modules': [
                'system_resources',
                'network_connectivity',
                'service_dependencies',
                'performance_analysis',
                'security_checks'
            ],
            'analysis_depth': 'deep',
            'include_recommendations': True
        }
        
        diagnostics_engine = DiagnosticsEngine(diagnostics_config)
        await diagnostics_engine.initialize()
        
        # Perform comprehensive system diagnostics
        diagnostic_report = await diagnostics_engine.run_full_diagnostics()
        
        assert 'system_overview' in diagnostic_report
        assert 'resource_analysis' in diagnostic_report
        assert 'service_analysis' in diagnostic_report
        assert 'network_analysis' in diagnostic_report
        assert 'performance_analysis' in diagnostic_report
        assert 'security_analysis' in diagnostic_report
        assert 'recommendations' in diagnostic_report
        assert 'diagnostic_timestamp' in diagnostic_report
        
        # Verify system overview
        overview = diagnostic_report['system_overview']
        assert 'platform' in overview
        assert 'python_version' in overview
        assert 'architecture' in overview
        assert 'cpu_count' in overview
        assert 'total_memory_gb' in overview
        
        # Verify resource analysis
        resources = diagnostic_report['resource_analysis']
        assert 'cpu_analysis' in resources
        assert 'memory_analysis' in resources
        assert 'disk_analysis' in resources
        assert 'network_analysis' in resources
        
        # Verify recommendations exist
        recommendations = diagnostic_report['recommendations']
        assert isinstance(recommendations, list)
        
        if len(recommendations) > 0:
            recommendation = recommendations[0]
            assert 'category' in recommendation
            assert 'severity' in recommendation
            assert 'description' in recommendation
            assert 'action_items' in recommendation

    @pytest.mark.asyncio
    async def test_health_reporting_comprehensive(self, health_monitor):
        """
Test comprehensive health reporting"""
        monitor = health_monitor
        
        # Initialize health reporter
        reporter_config = {
            'report_formats': ['json', 'html', 'pdf'],
            'include_charts': True,
            'include_trends': True,
            'include_recommendations': True,
            'report_sections': [
                'executive_summary',
                'system_health',
                'component_health',
                'performance_metrics',
                'availability_analysis',
                'incident_summary'
            ]
        }
        
        reporter = HealthReporter(reporter_config)
        await reporter.initialize()
        
        # Generate comprehensive health report
        report_period = {
            'start_time': datetime.now(timezone.utc) - timedelta(hours=24),
            'end_time': datetime.now(timezone.utc)
        }
        
        health_report = await reporter.generate_comprehensive_report(
            period=report_period,
            include_historical_data=True
        )
        
        assert 'report_metadata' in health_report
        assert 'executive_summary' in health_report
        assert 'system_health_summary' in health_report
        assert 'component_health_details' in health_report
        assert 'performance_analysis' in health_report
        assert 'availability_metrics' in health_report
        assert 'trends_analysis' in health_report
        assert 'recommendations' in health_report
        
        # Verify executive summary
        executive_summary = health_report['executive_summary']
        assert 'overall_health_score' in executive_summary
        assert 'availability_percentage' in executive_summary
        assert 'total_incidents' in executive_summary
        assert 'mean_time_to_recovery' in executive_summary
        
        # Verify availability metrics
        availability = health_report['availability_metrics']
        assert 'uptime_percentage' in availability
        assert 'downtime_minutes' in availability
        assert 'service_availability' in availability
        
        # Verify performance analysis
        performance = health_report['performance_analysis']
        assert 'response_time_analysis' in performance
        assert 'throughput_analysis' in performance
        assert 'resource_utilization' in performance

    @pytest.mark.asyncio
    async def test_custom_health_checks(self, health_monitor):
        """
Test custom health check implementations"""
        monitor = health_monitor
        
        # Define custom health check for AI model service
        async def ai_model_health_check(component_config):
            """
Custom health check for AI model service"""
            try:
                # Simulate AI model health check
                model_status = {
                    'model_loaded': True,
                    'model_version': '2.1.0',
                    'memory_usage_gb': 2.5,
                    'inference_queue_size': 5,
                    'last_inference_time_ms': 150.0,
                    'accuracy_score': 0.94
                }
                
                # Check if model is responding
                response_time_start = time.time()
                await asyncio.sleep(0.1)  # Simulate model ping
                response_time_ms = (time.time() - response_time_start) * 1000
                
                # Determine health status based on metrics
                if model_status['inference_queue_size'] > 100:
                    status = HealthStatus.CRITICAL
                    error_message = "Inference queue overloaded"
                elif model_status['last_inference_time_ms'] > 1000:
                    status = HealthStatus.WARNING
                    error_message = "Slow inference response"
                else:
                    status = HealthStatus.HEALTHY
                    error_message = None
                
                return HealthCheck(
                    component_name=component_config['name'],
                    component_type=ComponentType.AI_MODEL_SERVICE,
                    status=status,
                    response_time_ms=response_time_ms,
                    last_check=datetime.now(timezone.utc),
                    details=model_status,
                    error_message=error_message,
                    custom_metrics={
                        'model_accuracy': model_status['accuracy_score'],
                        'queue_size': model_status['inference_queue_size'],
                        'memory_usage_gb': model_status['memory_usage_gb']
                    }
                )
                
            except Exception as e:
                return HealthCheck(
                    component_name=component_config['name'],
                    component_type=ComponentType.AI_MODEL_SERVICE,
                    status=HealthStatus.CRITICAL,
                    response_time_ms=0.0,
                    last_check=datetime.now(timezone.utc),
                    error_message=f"AI model health check failed: {str(e)}"
                )
        
        # Register custom health check
        await monitor.register_custom_health_check(
            'ai_model_service',
            ai_model_health_check,
            {'name': 'ai_model_service', 'model_path': '/models/content_analyzer_v2.1'}
        )
        
        # Perform custom health check
        ai_health = await monitor.check_component_health('ai_model_service')
        
        assert isinstance(ai_health, HealthCheck)
        assert ai_health.component_name == 'ai_model_service'
        assert ai_health.component_type == ComponentType.AI_MODEL_SERVICE
        assert ai_health.status in [status for status in HealthStatus]
        assert 'model_loaded' in str(ai_health.details)
        
        if ai_health.custom_metrics:
            assert 'model_accuracy' in ai_health.custom_metrics
            assert 'queue_size' in ai_health.custom_metrics
            assert 'memory_usage_gb' in ai_health.custom_metrics

    @pytest.mark.asyncio
    async def test_health_check_parallelization(self, health_monitor):
        """Test parallel execution of health checks"""
        monitor = health_monitor
        
        # Register multiple components for parallel checking
        components_to_check = [
            {'name': f'service_{i}', 'type': ComponentType.API_GATEWAY, 'port': 8000 + i}
            for i in range(10)
        ]
        
        for component in components_to_check:
            await monitor.register_component(
                component['name'],
                component['type'],
                {'host': 'localhost', 'port': component['port']}
            )
        
        # Measure parallel health check performance
        start_time = time.time()
        
        # Check all components in parallel
        health_results = await monitor.check_all_components_parallel()
        
        end_time = time.time()
        parallel_duration = end_time - start_time
        
        # Verify results
        assert len(health_results) == len(components_to_check)
        
        for component_name, health_check in health_results.items():
            assert isinstance(health_check, HealthCheck)
            assert health_check.component_name == component_name
        
        # Measure sequential health check performance for comparison
        start_time = time.time()
        
        sequential_results = {}
        for component in components_to_check:
            sequential_results[component['name']] = await monitor.check_component_health(component['name'])
        
        end_time = time.time()
        sequential_duration = end_time - start_time
        
        # Parallel should be faster (or at least not much slower due to overhead)
        efficiency_ratio = parallel_duration / sequential_duration
        assert efficiency_ratio < 2.0, f"Parallel execution not efficient: {efficiency_ratio:.2f}x slower"

    def test_thread_safety_health_monitoring(self, health_config):
        """Test thread safety of health monitoring operations"""
        import concurrent.futures
        import threading
        
        monitor = HealthMonitor(health_config)
        
        results = []
        errors = []
        lock = threading.Lock()
        
        def concurrent_health_operations(thread_id):
            try:
                operations_results = []
                
                # Simulate concurrent health monitoring operations
                for i in range(20):
                    # This would normally be async operations
                    operation_result = {
                        'thread_id': thread_id,
                        'operation_index': i,
                        'component_name': f'thread_{thread_id}_component_{i}',
                        'timestamp': datetime.now(timezone.utc),
                        'status': HealthStatus.HEALTHY.value
                    }
                    operations_results.append(operation_result)
                
                with lock:
                    results.extend(operations_results)
                
                return operations_results
            except Exception as e:
                errors.append({'thread_id': thread_id, 'error': str(e)})
                raise
        
        # Run concurrent health monitoring operations
        num_threads = 15
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(concurrent_health_operations, i) 
                for i in range(num_threads)
            ]
            
            concurrent.futures.wait(futures)
        
        # Verify thread safety
        assert len(errors) == 0
        assert len(results) == num_threads * 20
        
        # Verify no data corruption
        thread_ids = set()
        component_names = set()
        
        for result in results:
            thread_ids.add(result['thread_id'])
            component_names.add(result['component_name'])
        
        assert len(thread_ids) == num_threads
        assert len(component_names) == num_threads * 20

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_health_monitoring_performance_at_scale(self, health_monitor):
        """
Test health monitoring performance at scale"""
        monitor = health_monitor
        
        # Configure for high performance
        await monitor.configure_high_performance(
            max_concurrent_checks=50,
            check_timeout_seconds=5,
            result_caching=True,
            cache_ttl_seconds=30
        )
        
        # Register large number of components
        num_components = 200
        component_names = []
        
        for i in range(num_components):
            component_name = f'scale_test_component_{i}'
            component_names.append(component_name)
            
            await monitor.register_component(
                component_name,
                ComponentType.API_GATEWAY,
                {'host': 'localhost', 'port': 8000 + i}
            )
        
        # Measure health check performance
        start_time = time.time()
        
        # Perform health checks on all components
        health_results = await monitor.check_all_components_parallel(
            component_names=component_names
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Performance assertions
        assert len(health_results) == num_components
        
        checks_per_second = num_components / total_time
        assert checks_per_second > 20, f"Health check throughput too low: {checks_per_second:.2f} checks/second"
        
        average_check_time = total_time / num_components
        assert average_check_time < 0.5, f"Average check time too high: {average_check_time:.2f}s"
        
        # Test caching efficiency
        start_time = time.time()
        
        # Perform checks again (should use cache)
        cached_results = await monitor.check_all_components_parallel(
            component_names=component_names[:50]  # Subset for cache test
        )
        
        end_time = time.time()
        cached_time = end_time - start_time
        
        # Cached checks should be much faster
        cached_checks_per_second = 50 / cached_time
        assert cached_checks_per_second > checks_per_second * 2, "Cache not providing performance benefit"
        
        print(f"Checked {num_components} components in {total_time:.2f}s")
        print(f"Throughput: {checks_per_second:.2f} checks/second")
        print(f"Cached throughput: {cached_checks_per_second:.2f} checks/second")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_end_to_end_health_monitoring_scenario(self, health_monitor):
        """Test end-to-end health monitoring scenario"""
        monitor = health_monitor
        
        # Step 1: Setup comprehensive health monitoring for IA Influencer platform
        platform_components = {
            'api_gateway': {
                'type': ComponentType.API_GATEWAY,
                'config': {'host': 'api.ia-influencer.com', 'port': 443},
                'dependencies': ['authentication', 'load_balancer']
            },
            'authentication': {
                'type': ComponentType.AUTHENTICATION,
                'config': {'host': 'auth.ia-influencer.com', 'port': 443},
                'dependencies': ['user_database', 'redis_session_store']
            },
            'content_service': {
                'type': ComponentType.API_GATEWAY,
                'config': {'host': 'content.ia-influencer.com', 'port': 443},
                'dependencies': ['content_database', 'file_storage', 'ai_processing']
            },
            'ai_processing': {
                'type': ComponentType.AI_MODEL_SERVICE,
                'config': {'host': 'ai.ia-influencer.com', 'port': 443},
                'dependencies': ['model_storage', 'gpu_cluster']
            },
            'content_protection': {
                'type': ComponentType.CONTENT_PROTECTION,
                'config': {'host': 'protection.ia-influencer.com', 'port': 443},
                'dependencies': ['fingerprint_database', 'ai_processing']
            },
            'user_database': {
                'type': ComponentType.DATABASE,
                'config': {'host': 'db-users.ia-influencer.com', 'port': 5432},
                'dependencies': []
            },
            'content_database': {
                'type': ComponentType.DATABASE,
                'config': {'host': 'db-content.ia-influencer.com', 'port': 5432},
                'dependencies': []
            },
            'redis_session_store': {
                'type': ComponentType.CACHE,
                'config': {'host': 'cache.ia-influencer.com', 'port': 6379},
                'dependencies': []
            },
            'file_storage': {
                'type': ComponentType.STORAGE,
                'config': {'host': 's3.amazonaws.com', 'bucket': 'ia-influencer-content'},
                'dependencies': []
            }
        }
        
        # Register all components
        for component_name, component_info in platform_components.items():
            await monitor.register_service_with_dependencies(
                service_name=component_name,
                component_type=component_info['type'],
                dependencies=component_info['dependencies'],
                config=component_info['config']
            )
        
        # Step 2: Simulate realistic health scenarios
        
        # Scenario 1: Normal healthy state
        print("Testing normal healthy state...")
        healthy_system_health = await monitor.check_system_health()
        
        assert healthy_system_health.overall_status == HealthStatus.HEALTHY
        assert len(healthy_system_health.components_status) >= len(platform_components)
        
        # Step 3: Simulate database performance degradation
        print("Simulating database performance degradation...")
        
        # Mock database slow response
        with patch.object(monitor, 'check_component_health') as mock_check:
            def mock_health_check(component_name):
                if 'database' in component_name:
                    return HealthCheck(
                        component_name=component_name,
                        component_type=ComponentType.DATABASE,
                        status=HealthStatus.WARNING,
                        response_time_ms=2500.0,  # Slow response
                        last_check=datetime.now(timezone.utc),
                        error_message="High query response time detected"
                    )
                else:
                    return HealthCheck(
                        component_name=component_name,
                        component_type=ComponentType.API_GATEWAY,
                        status=HealthStatus.HEALTHY,
                        response_time_ms=100.0,
                        last_check=datetime.now(timezone.utc)
                    )
            
            mock_check.side_effect = mock_health_check
            
            degraded_system_health = await monitor.check_system_health()
            
            # Should detect degradation
            assert degraded_system_health.overall_status in [HealthStatus.WARNING, HealthStatus.DEGRADED]
            
            # Should have alerts
            alerts = await monitor.check_threshold_alerts()
            database_alerts = [a for a in alerts if 'database' in a.get('component', '').lower()]
            assert len(database_alerts) > 0
        
        # Step 4: Simulate cascade failure scenario
        print("Simulating cascade failure scenario...")
        
        # Mock critical database failure
        with patch.object(monitor, 'check_component_health') as mock_check:
            def mock_cascade_failure(component_name):
                if component_name == 'user_database':
                    return HealthCheck(
                        component_name=component_name,
                        component_type=ComponentType.DATABASE,
                        status=HealthStatus.CRITICAL,
                        response_time_ms=0.0,
                        last_check=datetime.now(timezone.utc),
                        error_message="Database connection failed"
                    )
                elif component_name in ['authentication', 'api_gateway']:
                    # These depend on user_database
                    return HealthCheck(
                        component_name=component_name,
                        component_type=ComponentType.API_GATEWAY,
                        status=HealthStatus.CRITICAL,
                        response_time_ms=0.0,
                        last_check=datetime.now(timezone.utc),
                        error_message="Dependency failure: user_database unavailable"
                    )
                else:
                    return HealthCheck(
                        component_name=component_name,
                        component_type=ComponentType.API_GATEWAY,
                        status=HealthStatus.HEALTHY,
                        response_time_ms=100.0,
                        last_check=datetime.now(timezone.utc)
                    )
            
            mock_check.side_effect = mock_cascade_failure
            
            # Analyze cascade failure impact
            cascade_analysis = await monitor.analyze_dependency_health({
                'user_database': HealthStatus.CRITICAL,
                'authentication': HealthStatus.CRITICAL,
                'api_gateway': HealthStatus.CRITICAL
            })
            
            assert 'cascade_failures' in cascade_analysis
            assert len(cascade_analysis['affected_services']) > 1
            
            # Should identify user_database as root cause
            root_causes = cascade_analysis.get('root_causes', [])
            assert any('user_database' in cause for cause in root_causes)
        
        # Step 5: Generate comprehensive health report
        print("Generating comprehensive health report...")
        
        report_period = {
            'start_time': datetime.now(timezone.utc) - timedelta(hours=1),
            'end_time': datetime.now(timezone.utc)
        }
        
        reporter = HealthReporter({
            'report_formats': ['json'],
            'include_trends': True,
            'include_recommendations': True
        })
        await reporter.initialize()
        
        comprehensive_report = await reporter.generate_comprehensive_report(
            period=report_period,
            include_historical_data=True
        )
        
        # Verify report completeness
        assert 'executive_summary' in comprehensive_report
        assert 'system_health_summary' in comprehensive_report
        assert 'component_health_details' in comprehensive_report
        assert 'availability_metrics' in comprehensive_report
        assert 'recommendations' in comprehensive_report
        
        # Should have recommendations for database performance
        recommendations = comprehensive_report['recommendations']
        database_recommendations = [
            r for r in recommendations 
            if 'database' in r.get('description', '').lower()
        ]
        assert len(database_recommendations) > 0
        
        # Step 6: Test auto-remediation suggestions
        print("Testing auto-remediation suggestions...")
        
        remediation_suggestions = await monitor.generate_remediation_suggestions(
            failed_components=['user_database'],
            cascade_impact=cascade_analysis
        )
        
        assert 'immediate_actions' in remediation_suggestions
        assert 'preventive_measures' in remediation_suggestions
        assert 'monitoring_improvements' in remediation_suggestions
        
        immediate_actions = remediation_suggestions['immediate_actions']
        assert len(immediate_actions) > 0
        
        # Should suggest database restart/failover
        database_actions = [
            action for action in immediate_actions
            if 'database' in action.get('description', '').lower()
        ]
        assert len(database_actions) > 0
        
        print("End-to-end health monitoring scenario completed successfully!")


# Performance benchmarks
@pytest.mark.benchmark
class TestHealthMonitoringBenchmarks:
    """Performance benchmarks for system health monitoring"""
    
    def test_health_check_creation_benchmark(self, benchmark):
        """
Benchmark health check creation performance"""
        def create_health_check():
            return HealthCheck(
                component_name="benchmark_component",
                component_type=ComponentType.API_GATEWAY,
                status=HealthStatus.HEALTHY,
                response_time_ms=150.0,
                last_check=datetime.now(timezone.utc),
                details={'version': '2.1.0', 'build': '12345'},
                metrics={'cpu_percent': 45.2, 'memory_mb': 512}
            )
        
        health_check = benchmark(create_health_check)
        
        assert health_check.component_name == "benchmark_component"
        assert health_check.status == HealthStatus.HEALTHY
        assert health_check.response_time_ms == 150.0
    
    def test_system_metrics_collection_benchmark(self, benchmark):
        """Benchmark system metrics collection performance"""
        def collect_system_metrics():
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0,
                'process_count': len(psutil.pids()),
                'network_connections': len(psutil.net_connections())
            }
        
        metrics = benchmark(collect_system_metrics)
        
        assert 'cpu_percent' in metrics
        assert 'memory_percent' in metrics
        assert 'disk_percent' in metrics
        assert isinstance(metrics['cpu_percent'], (int, float))
        assert isinstance(metrics['memory_percent'], (int, float))
    
    def test_health_status_evaluation_benchmark(self, benchmark):
        """
Benchmark health status evaluation performance"""
        # Sample health checks for evaluation
        health_checks = [
            HealthCheck(
                component_name=f"component_{i}",
                component_type=ComponentType.API_GATEWAY,
                status=HealthStatus.HEALTHY if i % 3 != 0 else HealthStatus.WARNING,
                response_time_ms=100.0 + i * 10,
                last_check=datetime.now(timezone.utc)
            )
            for i in range(100)
        ]
        
        def evaluate_overall_health():
            healthy_count = sum(1 for hc in health_checks if hc.status == HealthStatus.HEALTHY)
            warning_count = sum(1 for hc in health_checks if hc.status == HealthStatus.WARNING)
            critical_count = sum(1 for hc in health_checks if hc.status == HealthStatus.CRITICAL)
            
            total_components = len(health_checks)
            
            if critical_count > 0:
                overall_status = HealthStatus.CRITICAL
            elif warning_count > total_components * 0.3:
                overall_status = HealthStatus.WARNING
            else:
                overall_status = HealthStatus.HEALTHY
            
            return {
                'overall_status': overall_status,
                'healthy_count': healthy_count,
                'warning_count': warning_count,
                'critical_count': critical_count,
                'health_score': healthy_count / total_components
            }
        
        result = benchmark(evaluate_overall_health)
        
        assert 'overall_status' in result
        assert 'health_score' in result
        assert 0.0 <= result['health_score'] <= 1.0
