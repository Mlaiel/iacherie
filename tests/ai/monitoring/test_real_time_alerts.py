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

"""Advanced Real-Time Alerts Tests - Industrial Grade

Comprehensive, enterprise-level test suite for real-time alerting system.
Tests alert generation, notification delivery, escalation chains, and alert management.

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
import uuid

from ai.monitoring.real_time_alerts import (
    RealTimeAlerts,
    AlertSeverity,
    AlertStatus,
    AlertType,
    NotificationChannel,
    Alert,
    AlertRule,
    EscalationPolicy,
    AlertManager,
    NotificationDelivery,
    AlertAggregator,
    AlertCorrelator,
    AlertThrottler
)
from ai.core.metrics import MetricType, MetricPriority
from ai.core.exceptions import AlertingError, NotificationError
from .fixtures import (
    alert_scenarios,
    notification_configs,
    escalation_policies,
    alert_rules,
    threshold_configs
)


class TestRealTimeAlertsCore:
    """Core functionality tests for real-time alerting system."""    
    @pytest.fixture
    async def alerts_system(self):
        """Create and initialize real-time alerts system."""        system = RealTimeAlerts(
            config={
                "alert_processing_enabled": True,
                "notification_delivery_enabled": True,
                "escalation_enabled": True,
                "correlation_enabled": True,
                "throttling_enabled": True,
                "max_alerts_per_minute": 100,
                "default_notification_channels": ["email", "slack"],
                "alert_retention_days": 30
            }
        )
        await system.initialize()
        yield system
        await system.shutdown()
    
    @pytest.fixture
    def sample_alert_rules(self, alert_rules):
        """Get sample alert rules for testing."""        return alert_rules["production_rules"]
    
    async def test_alerts_system_initialization(self, alerts_system):
        """Test comprehensive initialization of alerting system."""        # Verify core components
        assert alerts_system is not None
        assert alerts_system.is_initialized
        assert alerts_system.alert_manager is not None
        assert alerts_system.notification_delivery is not None
        assert alerts_system.alert_aggregator is not None
        assert alerts_system.alert_correlator is not None
        assert alerts_system.alert_throttler is not None
        
        # Verify configuration
        config = alerts_system.config
        assert config["alert_processing_enabled"] is True
        assert config["max_alerts_per_minute"] == 100
        assert config["default_notification_channels"] == ["email", "slack"]
        
        # Verify supported alert types
        supported_types = alerts_system.get_supported_alert_types()
        expected_types = [
            AlertType.SYSTEM_ERROR,
            AlertType.PERFORMANCE_DEGRADATION,
            AlertType.RESOURCE_EXHAUSTION,
            AlertType.SECURITY_INCIDENT,
            AlertType.SERVICE_UNAVAILABLE,
            AlertType.DATA_ANOMALY,
            AlertType.BUSINESS_METRIC_THRESHOLD
        ]
        assert all(alert_type in supported_types for alert_type in expected_types)
        
        # Verify notification channels
        available_channels = alerts_system.get_available_notification_channels()
        expected_channels = [
            NotificationChannel.EMAIL,
            NotificationChannel.SLACK,
            NotificationChannel.PAGERDUTY,
            NotificationChannel.SMS,
            NotificationChannel.WEBHOOK,
            NotificationChannel.TEAMS
        ]
        assert all(channel in available_channels for channel in expected_channels)
    
    async def test_alert_rule_management(self, alerts_system, sample_alert_rules):
        """Test alert rule creation, management, and validation."""        # Test alert rule creation
        rule_creation_scenarios = [
            {
                "rule_name": "high_cpu_usage",
                "rule_type": AlertType.PERFORMANCE_DEGRADATION,
                "condition": "cpu_usage > 80",
                "severity": AlertSeverity.WARNING,
                "notification_channels": [NotificationChannel.EMAIL, NotificationChannel.SLACK],
                "escalation_delay_minutes": 15,
                "auto_resolve": True
            },
            {
                "rule_name": "database_connection_failure",
                "rule_type": AlertType.SYSTEM_ERROR,
                "condition": "database_connections == 0",
                "severity": AlertSeverity.CRITICAL,
                "notification_channels": [NotificationChannel.PAGERDUTY, NotificationChannel.SMS],
                "escalation_delay_minutes": 5,
                "auto_resolve": False
            },
            {
                "rule_name": "memory_exhaustion",
                "rule_type": AlertType.RESOURCE_EXHAUSTION,
                "condition": "memory_usage > 95",
                "severity": AlertSeverity.CRITICAL,
                "notification_channels": [NotificationChannel.PAGERDUTY],
                "escalation_delay_minutes": 10,
                "auto_resolve": True
            }
        ]
        
        created_rules = []
        
        for scenario in rule_creation_scenarios:
            # Create alert rule
            rule = await alerts_system.create_alert_rule(
                rule_name=scenario["rule_name"],
                alert_type=scenario["rule_type"],
                condition=scenario["condition"],
                severity=scenario["severity"],
                notification_channels=scenario["notification_channels"],
                escalation_config={
                    "delay_minutes": scenario["escalation_delay_minutes"],
                    "auto_resolve": scenario["auto_resolve"]
                }
            )
            
            created_rules.append(rule)
            
            # Verify rule creation
            assert rule.rule_id is not None
            assert rule.rule_name == scenario["rule_name"]
            assert rule.alert_type == scenario["rule_type"]
            assert rule.severity == scenario["severity"]
            assert rule.is_active is True
            assert rule.created_at is not None
            
            # Verify rule validation
            validation_result = await alerts_system.validate_alert_rule(rule.rule_id)
            assert validation_result["is_valid"] is True
            assert "condition_syntax" in validation_result
            assert "notification_channels_valid" in validation_result
        
        # Test rule listing and filtering
        all_rules = await alerts_system.list_alert_rules()
        assert len(all_rules) >= len(rule_creation_scenarios)
        
        # Test rule filtering by severity
        critical_rules = await alerts_system.list_alert_rules(
            filter_criteria={"severity": AlertSeverity.CRITICAL}
        )
        expected_critical_count = sum(
            1 for scenario in rule_creation_scenarios 
            if scenario["severity"] == AlertSeverity.CRITICAL
        )
        assert len(critical_rules) >= expected_critical_count
        
        # Test rule modification
        rule_to_modify = created_rules[0]
        updated_rule = await alerts_system.update_alert_rule(
            rule_id=rule_to_modify.rule_id,
            updates={
                "severity": AlertSeverity.CRITICAL,
                "notification_channels": [NotificationChannel.PAGERDUTY],
                "condition": "cpu_usage > 90"
            }
        )
        
        assert updated_rule.severity == AlertSeverity.CRITICAL
        assert NotificationChannel.PAGERDUTY in updated_rule.notification_channels
        
        # Test rule deletion
        rule_to_delete = created_rules[-1]
        deletion_result = await alerts_system.delete_alert_rule(rule_to_delete.rule_id)
        assert deletion_result["deleted"] is True
        
        # Verify rule is no longer active
        deleted_rule = await alerts_system.get_alert_rule(rule_to_delete.rule_id)
        assert deleted_rule is None or deleted_rule.is_active is False
    
    async def test_alert_generation_and_processing(self, alerts_system):
        """Test alert generation, processing, and lifecycle management."""        # Create test alert rules
        test_rules = [
            {
                "rule_name": "test_performance_alert",
                "condition": "response_time > 1000",
                "severity": AlertSeverity.WARNING,
                "alert_type": AlertType.PERFORMANCE_DEGRADATION
            },
            {
                "rule_name": "test_error_alert",
                "condition": "error_rate > 0.05",
                "severity": AlertSeverity.CRITICAL,
                "alert_type": AlertType.SYSTEM_ERROR
            }
        ]
        
        created_rules = []
        for rule_config in test_rules:
            rule = await alerts_system.create_alert_rule(
                rule_name=rule_config["rule_name"],
                alert_type=rule_config["alert_type"],
                condition=rule_config["condition"],
                severity=rule_config["severity"],
                notification_channels=[NotificationChannel.EMAIL]
            )
            created_rules.append(rule)
        
        # Test alert triggering scenarios
        alert_scenarios = [
            {
                "metric_name": "response_time",
                "metric_value": 1500,  # Exceeds threshold
                "service_name": "api_gateway",
                "expected_alerts": ["test_performance_alert"]
            },
            {
                "metric_name": "error_rate",
                "metric_value": 0.08,  # Exceeds threshold
                "service_name": "user_service",
                "expected_alerts": ["test_error_alert"]
            },
            {
                "metric_name": "response_time",
                "metric_value": 2000,  # Multiple thresholds
                "service_name": "content_service",
                "expected_alerts": ["test_performance_alert"]
            }
        ]
        
        triggered_alerts = []
        
        for scenario in alert_scenarios:
            # Submit metric that should trigger alert
            alert_trigger_result = await alerts_system.process_metric_update(
                metric_name=scenario["metric_name"],
                metric_value=scenario["metric_value"],
                service_name=scenario["service_name"],
                timestamp=datetime.utcnow()
            )
            
            # Check if alerts were triggered
            if alert_trigger_result["alerts_triggered"]:
                new_alerts = alert_trigger_result["triggered_alerts"]
                triggered_alerts.extend(new_alerts)
                
                # Verify expected alerts were triggered
                triggered_rule_names = [alert.rule_name for alert in new_alerts]
                for expected_alert in scenario["expected_alerts"]:
                    assert expected_alert in triggered_rule_names
        
        # Verify alert properties
        assert len(triggered_alerts) > 0
        
        for alert in triggered_alerts:
            assert alert.alert_id is not None
            assert alert.alert_type in [AlertType.PERFORMANCE_DEGRADATION, AlertType.SYSTEM_ERROR]
            assert alert.severity in [AlertSeverity.WARNING, AlertSeverity.CRITICAL]
            assert alert.status == AlertStatus.TRIGGERED
            assert alert.triggered_at is not None
            assert alert.source_service is not None
            
        # Test alert lifecycle operations
        test_alert = triggered_alerts[0]
        
        # Acknowledge alert
        ack_result = await alerts_system.acknowledge_alert(
            alert_id=test_alert.alert_id,
            acknowledged_by="test_user"
        )
        assert ack_result["acknowledged"] is True
        
        updated_alert = await alerts_system.get_alert(test_alert.alert_id)
        assert updated_alert.status == AlertStatus.ACKNOWLEDGED
        assert updated_alert.acknowledged_by == "test_user"
        assert updated_alert.acknowledged_at is not None
        
        # Resolve alert
        resolve_result = await alerts_system.resolve_alert(
            alert_id=test_alert.alert_id,
            resolved_by="test_user",
            resolution_notes="Issue resolved by restarting service"
        )
        assert resolve_result["resolved"] is True
        
        resolved_alert = await alerts_system.get_alert(test_alert.alert_id)
        assert resolved_alert.status == AlertStatus.RESOLVED
        assert resolved_alert.resolved_by == "test_user"
        assert resolved_alert.resolved_at is not None
        assert resolved_alert.resolution_notes == "Issue resolved by restarting service"


@pytest.mark.performance
class TestAlertingPerformance:
    """Performance tests for real-time alerting system."""    
    @pytest.fixture
    async def performance_alerts_system(self):
        """Create high-performance alerting system."""        system = RealTimeAlerts(
            config={
                "high_performance_mode": True,
                "parallel_processing": True,
                "batch_processing_size": 100,
                "async_notification_delivery": True,
                "max_concurrent_notifications": 50
            }
        )
        await system.initialize()
        yield system
        await system.shutdown()
    
    async def test_high_volume_alert_processing(self, performance_alerts_system):
        """Test alert processing under high volume conditions."""        # Generate large number of alerts
        alert_count = 1000
        alerts = []
        
        for i in range(alert_count):
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                rule_name=f"load_test_alert_{i}",
                alert_type=AlertType.PERFORMANCE_DEGRADATION,
                severity=AlertSeverity.WARNING,
                status=AlertStatus.TRIGGERED,
                message=f"Load test alert {i}",
                source_service=f"service_{i % 10}",  # 10 different services
                triggered_at=datetime.utcnow()
            )
            alerts.append(alert)
        
        # Measure processing performance
        start_time = time.time()
        
        # Process alerts in batches
        batch_size = 100
        processing_results = []
        
        for i in range(0, alert_count, batch_size):
            batch = alerts[i:i + batch_size]
            batch_result = await performance_alerts_system.process_alert_batch(batch)
            processing_results.append(batch_result)
        
        processing_time = time.time() - start_time
        
        # Performance assertions
        assert processing_time < 30  # Process 1000 alerts in under 30 seconds
        
        # Verify processing throughput
        throughput = alert_count / processing_time
        assert throughput >= 50  # At least 50 alerts per second
        
        # Verify all batches processed successfully
        total_processed = sum(result["processed_count"] for result in processing_results)
        assert total_processed == alert_count
        
        # Verify processing success rate
        total_successful = sum(result["successful_count"] for result in processing_results)
        success_rate = total_successful / alert_count
        assert success_rate >= 0.95  # At least 95% success rate


if __name__ == "__main__":
    # Run tests with coverage
    pytest.main([
        "test_real_time_alerts.py",
        "-v",
        "--cov=backend.ai.monitoring.real_time_alerts",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-fail-under=100"
    ])

import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, patch
import json
import smtplib

from ai.monitoring.real_time_alerts import (
    RealTimeAlerts,
    AlertSeverity,
    AlertCategory,
    AlertRule,
    AlertNotification,
    AlertEscalation,
    NotificationChannel,
    AlertSuppression
)
from .utils import TestDataGenerator, PerformanceValidator

class TestRealTimeAlerts:
    """Test suite for Real-Time Alerts system."""    
    @pytest.fixture
    async def alert_system(self):
        """Create Real-Time Alerts instance."""        alerts = RealTimeAlerts()
        await alerts.initialize()
        yield alerts
        await alerts.shutdown()
    
    @pytest.fixture
    def alert_test_config(self):
        """Alert system configuration for testing."""        return {
            "notification_channels": {
                "email": {
                    "smtp_server": "smtp.test.com",
                    "smtp_port": 587,
                    "username": "alerts@test.com",
                    "password": "test_password",
                    "from_address": "alerts@test.com",
                    "recipients": ["admin@test.com", "ops@test.com"]
                },
                "slack": {
                    "webhook_url": "https://hooks.slack.com/test/webhook",
                    "channel": "#alerts",
                    "username": "AlertBot"
                },
                "webhook": {
                    "url": "https://api.test.com/alerts",
                    "method": "POST",
                    "headers": {"Authorization": "Bearer test_token"}
                },
                "sms": {
                    "provider": "twilio",
                    "account_sid": "test_sid",
                    "auth_token": "test_token",
                    "from_number": "+1234567890",
                    "recipients": ["+1987654321"]
                }
            },
            "alert_rules": [
                {
                    "name": "high_cpu_usage",
                    "category": AlertCategory.PERFORMANCE,
                    "severity": AlertSeverity.WARNING,
                    "condition": "cpu_usage > 85",
                    "threshold": 85.0,
                    "duration": 300,  # 5 minutes
                    "channels": ["email", "slack"]
                },
                {
                    "name": "database_connection_failure",
                    "category": AlertCategory.INFRASTRUCTURE,
                    "severity": AlertSeverity.CRITICAL,
                    "condition": "database_status == 'unhealthy'",
                    "duration": 0,  # Immediate
                    "channels": ["email", "slack", "sms"]
                },
                {
                    "name": "ai_model_error_rate",
                    "category": AlertCategory.AI_PERFORMANCE,
                    "severity": AlertSeverity.ERROR,
                    "condition": "error_rate > 0.05",
                    "threshold": 0.05,
                    "duration": 180,  # 3 minutes
                    "channels": ["email", "webhook"]
                }
            ],
            "escalation_rules": [
                {
                    "severity": AlertSeverity.CRITICAL,
                    "escalation_time": 300,  # 5 minutes
                    "escalation_channels": ["sms"],
                    "escalation_recipients": ["manager@test.com"]
                },
                {
                    "severity": AlertSeverity.ERROR,
                    "escalation_time": 900,  # 15 minutes
                    "escalation_channels": ["email"],
                    "escalation_recipients": ["lead@test.com"]
                }
            ],
            "suppression_rules": [
                {
                    "name": "maintenance_window",
                    "schedule": "0 2 * * 0",  # Sunday 2 AM
                    "duration": 7200,  # 2 hours
                    "suppress_categories": [AlertCategory.INFRASTRUCTURE]
                }
            ]
        }
    
    async def test_alert_system_initialization(self, alert_system):
        """Test proper initialization of alert system."""        assert alert_system is not None
        assert alert_system.is_initialized
        assert alert_system.rule_engine is not None
        assert alert_system.notification_manager is not None
        assert alert_system.escalation_manager is not None
        assert alert_system.suppression_manager is not None
    
    async def test_alert_rule_configuration(self, alert_system, alert_test_config):
        """Test alert rule configuration and validation."""        # Configure alert rules
        for rule_config in alert_test_config["alert_rules"]:
            rule = AlertRule(
                name=rule_config["name"],
                category=rule_config["category"],
                severity=rule_config["severity"],
                condition=rule_config["condition"],
                threshold=rule_config.get("threshold"),
                duration=rule_config["duration"],
                notification_channels=rule_config["channels"]
            )
            
            await alert_system.add_alert_rule(rule)
        
        # Verify rules were added
        rules = await alert_system.get_alert_rules()
        assert len(rules) == 3
        
        # Verify rule details
        rule_names = [rule.name for rule in rules]
        assert "high_cpu_usage" in rule_names
        assert "database_connection_failure" in rule_names
        assert "ai_model_error_rate" in rule_names
        
        # Test rule validation
        valid_rule = AlertRule(
            name="test_valid_rule",
            category=AlertCategory.PERFORMANCE,
            severity=AlertSeverity.WARNING,
            condition="metric_value > threshold",
            threshold=100.0,
            duration=300,
            notification_channels=["email"]
        )
        
        validation_result = await alert_system.validate_alert_rule(valid_rule)
        assert validation_result["valid"] == True
        
        # Test invalid rule
        invalid_rule = AlertRule(
            name="test_invalid_rule",
            category=AlertCategory.PERFORMANCE,
            severity=AlertSeverity.WARNING,
            condition="invalid condition syntax",
            threshold=None,  # Missing required threshold
            duration=-100,   # Invalid duration
            notification_channels=[]  # No channels
        )
        
        validation_result = await alert_system.validate_alert_rule(invalid_rule)
        assert validation_result["valid"] == False
        assert len(validation_result["errors"]) > 0
    
    async def test_alert_triggering_and_evaluation(self, alert_system, alert_test_config):
        """Test alert triggering based on metric evaluation."""        # Configure alert rules
        await alert_system.configure_alert_rules(alert_test_config["alert_rules"])
        
        # Track triggered alerts
        triggered_alerts = []
        
        async def alert_callback(alert):
            triggered_alerts.append(alert)
        
        alert_system.add_alert_callback(alert_callback)
        
        # Test CPU usage alert
        cpu_metrics = [
            {"timestamp": datetime.utcnow(), "cpu_usage": 70.0},  # Normal
            {"timestamp": datetime.utcnow(), "cpu_usage": 88.0},  # Above threshold
            {"timestamp": datetime.utcnow(), "cpu_usage": 90.0},  # Still above
            {"timestamp": datetime.utcnow(), "cpu_usage": 92.0},  # Still above
        ]
        
        for metric in cpu_metrics:
            await alert_system.evaluate_metrics(
                metric_name="cpu_usage",
                metric_value=metric["cpu_usage"],
                timestamp=metric["timestamp"]
            )
            await asyncio.sleep(0.01)  # Small delay for processing
        
        # Test database failure alert (immediate)
        await alert_system.evaluate_metrics(
            metric_name="database_status",
            metric_value="unhealthy",
            timestamp=datetime.utcnow()
        )
        
        # Test AI model error rate alert
        error_rate_metrics = [
            {"timestamp": datetime.utcnow(), "error_rate": 0.02},  # Normal
            {"timestamp": datetime.utcnow(), "error_rate": 0.08},  # Above threshold
            {"timestamp": datetime.utcnow(), "error_rate": 0.10},  # Still above
        ]
        
        for metric in error_rate_metrics:
            await alert_system.evaluate_metrics(
                metric_name="error_rate",
                metric_value=metric["error_rate"],
                timestamp=metric["timestamp"]
            )
            await asyncio.sleep(0.01)
        
        # Allow time for alert processing
        await asyncio.sleep(0.5)
        
        # Verify alerts were triggered
        assert len(triggered_alerts) >= 2  # Database and error rate alerts
        
        # Verify alert details
        alert_names = [alert.rule_name for alert in triggered_alerts]
        assert "database_connection_failure" in alert_names
        assert "ai_model_error_rate" in alert_names
        
        # Verify alert severities
        critical_alerts = [alert for alert in triggered_alerts if alert.severity == AlertSeverity.CRITICAL]
        assert len(critical_alerts) >= 1  # Database failure
        
        error_alerts = [alert for alert in triggered_alerts if alert.severity == AlertSeverity.ERROR]
        assert len(error_alerts) >= 1  # AI model error rate
    
    async def test_notification_delivery(self, alert_system, alert_test_config):
        """Test alert notification delivery through various channels."""        # Configure notification channels
        await alert_system.configure_notification_channels(
            alert_test_config["notification_channels"]
        )
        
        # Track sent notifications
        sent_notifications = []
        
        async def notification_callback(notification):
            sent_notifications.append(notification)
        
        alert_system.add_notification_callback(notification_callback)
        
        # Test email notification
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            mock_server.send_message.return_value = {}
            
            alert = AlertNotification(
                id="test_alert_001",
                rule_name="database_connection_failure",
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.INFRASTRUCTURE,
                message="Database connection failed",
                timestamp=datetime.utcnow(),
                channels=["email"]
            )
            
            result = await alert_system.send_notification(alert)
            
            assert result["email"]["success"] == True
            assert mock_server.send_message.called
        
        # Test Slack notification
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.text.return_value = "ok"
            mock_post.return_value.__aenter__.return_value = mock_response
            
            alert = AlertNotification(
                id="test_alert_002",
                rule_name="high_cpu_usage",
                severity=AlertSeverity.WARNING,
                category=AlertCategory.PERFORMANCE,
                message="CPU usage is above 85%",
                timestamp=datetime.utcnow(),
                channels=["slack"]
            )
            
            result = await alert_system.send_notification(alert)
            
            assert result["slack"]["success"] == True
            assert mock_post.called
        
        # Test webhook notification
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"status": "received"}
            mock_post.return_value.__aenter__.return_value = mock_response
            
            alert = AlertNotification(
                id="test_alert_003",
                rule_name="ai_model_error_rate",
                severity=AlertSeverity.ERROR,
                category=AlertCategory.AI_PERFORMANCE,
                message="AI model error rate exceeded threshold",
                timestamp=datetime.utcnow(),
                channels=["webhook"]
            )
            
            result = await alert_system.send_notification(alert)
            
            assert result["webhook"]["success"] == True
            assert mock_post.called
        
        # Test notification failure handling
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            alert = AlertNotification(
                id="test_alert_004",
                rule_name="test_rule",
                severity=AlertSeverity.ERROR,
                category=AlertCategory.SYSTEM,
                message="Test notification failure",
                timestamp=datetime.utcnow(),
                channels=["webhook"]
            )
            
            result = await alert_system.send_notification(alert)
            
            assert result["webhook"]["success"] == False
            assert "error" in result["webhook"]
        
        # Verify notifications were tracked
        assert len(sent_notifications) >= 3
    
    async def test_alert_escalation(self, alert_system, alert_test_config):
        """Test alert escalation procedures."""        # Configure escalation rules
        await alert_system.configure_escalation_rules(
            alert_test_config["escalation_rules"]
        )
        
        # Track escalated alerts
        escalated_alerts = []
        
        async def escalation_callback(escalation):
            escalated_alerts.append(escalation)
        
        alert_system.add_escalation_callback(escalation_callback)
        
        # Create critical alert that should escalate
        critical_alert = AlertNotification(
            id="critical_alert_001",
            rule_name="database_connection_failure",
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.INFRASTRUCTURE,
            message="Database connection failed - critical system down",
            timestamp=datetime.utcnow(),
            channels=["email", "slack"]
        )
        
        # Send initial alert
        await alert_system.send_notification(critical_alert)
        
        # Simulate time passing without acknowledgment
        # In real scenario, this would be timer-based
        await alert_system.check_escalation_needed(critical_alert.id)
        
        # Simulate escalation trigger (normally time-based)
        escalation = AlertEscalation(
            original_alert_id=critical_alert.id,
            escalation_level=1,
            escalation_reason="No acknowledgment after 5 minutes",
            escalation_channels=["sms"],
            escalation_recipients=["manager@test.com"],
            escalation_timestamp=datetime.utcnow()
        )
        
        await alert_system.trigger_escalation(escalation)
        
        # Verify escalation was triggered
        assert len(escalated_alerts) >= 1
        
        # Test escalation chain
        error_alert = AlertNotification(
            id="error_alert_001",
            rule_name="ai_model_error_rate",
            severity=AlertSeverity.ERROR,
            category=AlertCategory.AI_PERFORMANCE,
            message="AI model error rate exceeded 5%",
            timestamp=datetime.utcnow(),
            channels=["email"]
        )
        
        await alert_system.send_notification(error_alert)
        
        # Simulate longer escalation time for ERROR alerts
        escalation_2 = AlertEscalation(
            original_alert_id=error_alert.id,
            escalation_level=1,
            escalation_reason="No resolution after 15 minutes",
            escalation_channels=["email"],
            escalation_recipients=["lead@test.com"],
            escalation_timestamp=datetime.utcnow()
        )
        
        await alert_system.trigger_escalation(escalation_2)
        
        # Test escalation prevention (alert acknowledgment)
        warning_alert = AlertNotification(
            id="warning_alert_001",
            rule_name="high_cpu_usage",
            severity=AlertSeverity.WARNING,
            category=AlertCategory.PERFORMANCE,
            message="CPU usage above 85%",
            timestamp=datetime.utcnow(),
            channels=["email"]
        )
        
        await alert_system.send_notification(warning_alert)
        
        # Acknowledge alert before escalation
        await alert_system.acknowledge_alert(
            alert_id=warning_alert.id,
            acknowledged_by="ops_team",
            acknowledgment_message="Investigating high CPU usage"
        )
        
        # Check that escalation is prevented
        escalation_needed = await alert_system.check_escalation_needed(warning_alert.id)
        assert escalation_needed == False  # Should not escalate acknowledged alerts
    
    async def test_alert_suppression_and_filtering(self, alert_system, alert_test_config):
        """Test alert suppression and intelligent filtering."""        # Configure suppression rules
        await alert_system.configure_suppression_rules(
            alert_test_config["suppression_rules"]
        )
        
        # Test maintenance window suppression
        maintenance_start = datetime.utcnow()
        maintenance_end = maintenance_start + timedelta(hours=2)
        
        await alert_system.activate_maintenance_window(
            start_time=maintenance_start,
            end_time=maintenance_end,
            suppress_categories=[AlertCategory.INFRASTRUCTURE],
            reason="Scheduled database maintenance"
        )
        
        # Try to trigger infrastructure alert during maintenance
        infrastructure_alert = AlertNotification(
            id="maintenance_alert_001",
            rule_name="database_connection_failure",
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.INFRASTRUCTURE,
            message="Database connection failed",
            timestamp=datetime.utcnow(),
            channels=["email"]
        )
        
        suppression_result = await alert_system.check_alert_suppression(infrastructure_alert)
        assert suppression_result["suppressed"] == True
        assert "maintenance_window" in suppression_result["reason"]
        
        # Test that non-infrastructure alerts are not suppressed
        performance_alert = AlertNotification(
            id="maintenance_alert_002",
            rule_name="high_cpu_usage",
            severity=AlertSeverity.WARNING,
            category=AlertCategory.PERFORMANCE,
            message="High CPU usage",
            timestamp=datetime.utcnow(),
            channels=["email"]
        )
        
        suppression_result = await alert_system.check_alert_suppression(performance_alert)
        assert suppression_result["suppressed"] == False
        
        # Test alert deduplication
        duplicate_alerts = []
        for i in range(5):
            duplicate_alert = AlertNotification(
                id=f"duplicate_alert_{i:03d}",
                rule_name="high_cpu_usage",
                severity=AlertSeverity.WARNING,
                category=AlertCategory.PERFORMANCE,
                message="CPU usage above 85%",
                timestamp=datetime.utcnow(),
                channels=["email"]
            )
            duplicate_alerts.append(duplicate_alert)
        
        # Send duplicate alerts
        sent_count = 0
        for alert in duplicate_alerts:
            dedup_result = await alert_system.check_alert_deduplication(alert)
            if not dedup_result["duplicate"]:
                await alert_system.send_notification(alert)
                sent_count += 1
        
        # Should only send first alert, suppress duplicates
        assert sent_count == 1
        
        # Test alert frequency limiting
        frequency_alerts = []
        for i in range(10):
            freq_alert = AlertNotification(
                id=f"frequency_alert_{i:03d}",
                rule_name="api_response_time",
                severity=AlertSeverity.WARNING,
                category=AlertCategory.PERFORMANCE,
                message=f"API response time high: {2.5 + i * 0.1}s",
                timestamp=datetime.utcnow() + timedelta(seconds=i),
                channels=["email"]
            )
            frequency_alerts.append(freq_alert)
        
        # Configure frequency limit: max 3 alerts per 5 minutes for same rule
        await alert_system.configure_frequency_limits({
            "api_response_time": {"max_alerts": 3, "time_window": 300}
        })
        
        sent_frequency_count = 0
        for alert in frequency_alerts:
            frequency_result = await alert_system.check_frequency_limits(alert)
            if not frequency_result["rate_limited"]:
                await alert_system.send_notification(alert)
                sent_frequency_count += 1
        
        # Should respect frequency limit
        assert sent_frequency_count <= 3
    
    async def test_intelligent_alert_correlation(self, alert_system):
        """Test intelligent alert correlation and root cause analysis."""        # Configure correlation rules
        correlation_config = {
            "correlation_rules": [
                {
                    "name": "infrastructure_cascade",
                    "primary_alert": "database_connection_failure",
                    "related_alerts": ["api_response_time", "user_session_errors"],
                    "correlation_window": 300,  # 5 minutes
                    "confidence_threshold": 0.8
                },
                {
                    "name": "performance_degradation",
                    "primary_alert": "high_cpu_usage",
                    "related_alerts": ["high_memory_usage", "slow_response_time"],
                    "correlation_window": 180,  # 3 minutes
                    "confidence_threshold": 0.7
                }
            ]
        }
        
        await alert_system.configure_alert_correlation(correlation_config)
        
        # Simulate correlated alerts
        base_time = datetime.utcnow()
        
        # Primary alert: database failure
        primary_alert = AlertNotification(
            id="primary_alert_001",
            rule_name="database_connection_failure",
            severity=AlertSeverity.CRITICAL,
            category=AlertCategory.INFRASTRUCTURE,
            message="Database connection failed",
            timestamp=base_time,
            channels=["email"]
        )
        
        await alert_system.send_notification(primary_alert)
        
        # Related alerts that should correlate
        related_alerts = [
            AlertNotification(
                id="related_alert_001",
                rule_name="api_response_time",
                severity=AlertSeverity.WARNING,
                category=AlertCategory.PERFORMANCE,
                message="API response time increased",
                timestamp=base_time + timedelta(seconds=30),
                channels=["email"]
            ),
            AlertNotification(
                id="related_alert_002",
                rule_name="user_session_errors",
                severity=AlertSeverity.ERROR,
                category=AlertCategory.BUSINESS,
                message="Increased user session errors",
                timestamp=base_time + timedelta(seconds=60),
                channels=["email"]
            )
        ]
        
        for alert in related_alerts:
            await alert_system.send_notification(alert)
        
        # Analyze alert correlations
        correlation_analysis = await alert_system.analyze_alert_correlations(
            time_range=timedelta(minutes=10)
        )
        
        assert correlation_analysis is not None
        assert "correlations" in correlation_analysis
        assert "root_cause_candidates" in correlation_analysis
        
        # Verify correlation detection
        correlations = correlation_analysis["correlations"]
        assert len(correlations) >= 1
        
        # Check if infrastructure cascade was detected
        infrastructure_correlation = next(
            (c for c in correlations if c["correlation_type"] == "infrastructure_cascade"),
            None
        )
        assert infrastructure_correlation is not None
        assert infrastructure_correlation["confidence"] >= 0.8
        
        # Verify root cause identification
        root_causes = correlation_analysis["root_cause_candidates"]
        primary_root_cause = root_causes[0] if root_causes else None
        
        assert primary_root_cause is not None
        assert primary_root_cause["alert_id"] == "primary_alert_001"
        assert primary_root_cause["rule_name"] == "database_connection_failure"
    
    async def test_alert_analytics_and_reporting(self, alert_system):
        """Test alert analytics and reporting capabilities."""        # Generate historical alert data
        historical_alerts = TestDataGenerator.generate_alert_scenarios()
        
        # Record historical alerts
        for alert_scenario in historical_alerts:
            alert = AlertNotification(
                id=alert_scenario["id"],
                rule_name=alert_scenario["condition"],
                severity=AlertSeverity(alert_scenario["severity"]),
                category=AlertCategory(alert_scenario["category"]),
                message=alert_scenario["message"],
                timestamp=alert_scenario["timestamp"],
                channels=["email"]
            )
            
            await alert_system.record_alert_history(alert)
        
        # Generate alert analytics
        analytics = await alert_system.generate_alert_analytics(
            time_range=timedelta(days=7),
            include_trends=True,
            include_patterns=True
        )
        
        assert analytics is not None
        assert "summary" in analytics
        assert "trends" in analytics
        assert "patterns" in analytics
        assert "recommendations" in analytics
        
        # Verify summary statistics
        summary = analytics["summary"]
        assert "total_alerts" in summary
        assert "alerts_by_severity" in summary
        assert "alerts_by_category" in summary
        assert "avg_resolution_time" in summary
        
        # Verify trend analysis
        trends = analytics["trends"]
        assert "alert_frequency" in trends
        assert "severity_distribution" in trends
        assert "category_distribution" in trends
        
        # Verify pattern recognition
        patterns = analytics["patterns"]
        assert "recurring_alerts" in patterns
        assert "time_based_patterns" in patterns
        assert "correlation_patterns" in patterns
        
        # Generate alert report
        report = await alert_system.generate_alert_report(
            report_type="weekly_summary",
            time_range=timedelta(days=7),
            include_charts=True,
            format="json"
        )
        
        assert report is not None
        assert "report_metadata" in report
        assert "alert_summary" in report
        assert "detailed_analysis" in report
        assert "charts" in report
        assert "recommendations" in report
    
    async def test_alert_system_performance(self, alert_system):
        """Test alert system performance and scalability."""        # Performance test with high alert volume
        start_time = datetime.utcnow()
        
        # Generate high volume of alerts
        alert_count = 1000
        alert_tasks = []
        
        for i in range(alert_count):
            alert = AlertNotification(
                id=f"perf_test_alert_{i:06d}",
                rule_name="performance_test_rule",
                severity=AlertSeverity.WARNING,
                category=AlertCategory.PERFORMANCE,
                message=f"Performance test alert {i}",
                timestamp=datetime.utcnow(),
                channels=["email"]
            )
            
            # Create task for alert processing
            task = alert_system.process_alert(alert)
            alert_tasks.append(task)
        
        # Process alerts concurrently
        results = await asyncio.gather(*alert_tasks, return_exceptions=True)
        
        end_time = datetime.utcnow()
        processing_duration = (end_time - start_time).total_seconds()
        
        # Verify performance requirements
        alerts_per_second = alert_count / processing_duration
        assert alerts_per_second >= 100  # Should process at least 100 alerts/second
        
        # Verify processing success rate
        successful_results = [r for r in results if not isinstance(r, Exception)]
        success_rate = len(successful_results) / alert_count
        assert success_rate >= 0.95  # 95% success rate minimum
        
        # Test notification delivery performance
        notification_start = datetime.utcnow()
        
        # Mock notification delivery for performance testing
        with patch.multiple(
            alert_system,
            send_email_notification=AsyncMock(return_value={"success": True}),
            send_slack_notification=AsyncMock(return_value={"success": True}),
            send_webhook_notification=AsyncMock(return_value={"success": True})
        ):
            notification_tasks = []
            
            for i in range(500):  # 500 notifications
                alert = AlertNotification(
                    id=f"notification_test_{i:06d}",
                    rule_name="notification_test_rule",
                    severity=AlertSeverity.INFO,
                    category=AlertCategory.SYSTEM,
                    message=f"Notification test {i}",
                    timestamp=datetime.utcnow(),
                    channels=["email", "slack", "webhook"]
                )
                
                task = alert_system.send_notification(alert)
                notification_tasks.append(task)
            
            # Send notifications concurrently
            notification_results = await asyncio.gather(*notification_tasks)
            
            notification_end = datetime.utcnow()
            notification_duration = (notification_end - notification_start).total_seconds()
            
            notifications_per_second = 500 / notification_duration
            assert notifications_per_second >= 50  # 50 notifications/second minimum
        
        # Test memory usage during high load
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        
        # Memory usage should be reasonable even with high alert volume
        assert memory_usage < 500  # Less than 500MB
