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

"""Test Suite for Intelligent Alerting System

Comprehensive test suite for the alerting system ensuring proper functionality,
performance, security, and business logic compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL STRICT / STRICT LEGAL WARNING ⚠️

PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE de Fahed Mlaiel
EXCLUSIVE INTELLECTUAL PROPERTY of Fahed Mlaiel

🚫 UTILISATION NON AUTORISÉE STRICTEMENT INTERDITE:
- Aucune copie, clonage ou réplication sans autorisation écrite explicite
- Aucune utilisation commerciale sans accord de licence
- Aucune redistribution sous quelque forme que ce soit
- Aucune rétro-ingénierie ou analyse de code

⚖️ CONSÉQUENCES LÉGALES:
Toute tentative de vol, copie ou utilisation de ce code/concept sans permission
écrite explicite de Fahed Mlaiel entraînera des poursuites judiciaires immédiates
selon le droit allemand et international, réclamation de dommages financiers,
et poursuites pénales le cas échéant.

Si vous pensez pouvoir voler ce travail - VOUS ÊTES SURVEILLÉ.
Contact: mlaiel@live.de pour les demandes de licence.

Équipe d'Experts du Projet:
✅ Lead Dev + Architecte Développeur IA: Fahed Mlaiel
✅ Développeur Backend Senior (Python/FastAPI/Django): Fahed Mlaiel  
✅ Ingénieur Machine Learning (TensorFlow/PyTorch/Hugging Face): Fahed Mlaiel
✅ DBA & Data Engineer (PostgreSQL/Redis/MongoDB): Fahed Mlaiel
✅ Spécialiste Sécurité Backend: Fahed Mlaiel
✅ Architecte Microservices: Fahed Mlaiel
✅ Développeur Audio: Fahed Mlaiel
✅ DevOps Engineer: Fahed Mlaiel
✅ IA Prompt Engineer: Fahed Mlaiel

Contact: mlaiel@live.de
"""import pytest
import sys
import os
from pathlib import Path
import asyncio
import time
import json
import threading
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock, call
from typing import Dict, List, Any, Optional
import smtplib
import requests

# Import the modules to test
from ai.observability.alerting import (
    AlertManager, ThresholdMonitor, SecurityAlerts,
    BusinessKPIAlerts, EscalationManager, NotificationHub,
    AlertRule, AlertSeverity, AlertChannel, AlertCategory,
    AlertStatus, AlertManager
)
from ai.observability.metrics import MetricPoint
from core.exceptions import ValidationError, ConfigurationError


class TestAlertRule:
    """Test cases for AlertRule dataclass"""    
    def test_alert_rule_creation(self):
        """Test AlertRule creation with all parameters"""        rule = AlertRule(
            rule_id="cpu_high",
            name="High CPU Usage",
            description="Alert when CPU usage exceeds 80%",
            category=AlertCategory.PERFORMANCE,
            severity=AlertSeverity.HIGH,
            condition="cpu_usage_percent > threshold",
            threshold=80.0,
            comparison_operator=">",
            time_window=300,
            evaluation_frequency=60,
            channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
            recipients=["admin@example.com", "#alerts"],
            suppression_duration=3600,
            auto_resolve=True,
            escalation_rules=[
                {"delay": 600, "severity": "critical", "channels": ["pager"]}
            ],
            metadata={"team": "sre", "priority": "high"}
        )
        
        assert rule.rule_id == "cpu_high"
        assert rule.name == "High CPU Usage"
        assert rule.severity == AlertSeverity.HIGH
        assert rule.threshold == 80.0
        assert len(rule.channels) == 2
        assert len(rule.recipients) == 2
        assert rule.is_enabled is True
        assert rule.created_at is not None
    
    def test_alert_rule_to_dict(self):
        """Test AlertRule serialization to dictionary"""        rule = AlertRule(
            rule_id="test_rule",
            name="Test Rule",
            description="Test alert rule",
            category=AlertCategory.SYSTEM,
            severity=AlertSeverity.MEDIUM,
            condition="metric > threshold",
            threshold=50,
            comparison_operator=">",
            time_window=300
        )
        
        rule_dict = rule.to_dict()
        
        assert isinstance(rule_dict, dict)
        assert rule_dict['rule_id'] == "test_rule"
        assert rule_dict['name'] == "Test Rule"
        assert rule_dict['category'] == "system"
        assert rule_dict['severity'] == "medium"
        assert rule_dict['threshold'] == 50
    
    def test_alert_rule_default_values(self):
        """Test AlertRule with default values"""        rule = AlertRule(
            rule_id="default_test",
            name="Default Test",
            description="Test with defaults",
            category=AlertCategory.SYSTEM,
            severity=AlertSeverity.LOW,
            condition="test_metric > threshold",
            threshold=10,
            comparison_operator=">",
            time_window=60
        )
        
        assert rule.evaluation_frequency == 60
        assert rule.channels == []
        assert rule.recipients == []
        assert rule.suppression_duration == 3600
        assert rule.auto_resolve is True
        assert rule.escalation_rules == []
        assert rule.metadata == {}
        assert rule.is_enabled is True


class TestAlertManager:
    """Test cases for AlertManager class"""    
    @pytest.fixture
    def alert_manager(self):
        """Create AlertManager instance for testing"""        return AlertManager()
    
    @pytest.fixture
    def sample_alert_rule(self):
        """Create sample alert rule for testing"""        return AlertRule(
            rule_id="test_rule",
            name="Test Alert Rule",
            description="Test alert for unit testing",
            category=AlertCategory.SYSTEM,
            severity=AlertSeverity.HIGH,
            condition="test_metric > threshold",
            threshold=75.0,
            comparison_operator=">",
            time_window=300,
            channels=[AlertChannel.EMAIL],
            recipients=["test@example.com"]
        )
    
    def test_alert_manager_initialization(self, alert_manager):
        """Test AlertManager initialization"""        assert isinstance(alert_manager.rules, dict)
        assert isinstance(alert_manager.active_alerts, dict)
        assert isinstance(alert_manager.alert_history, list)
        assert isinstance(alert_manager.suppression_cache, dict)
        assert alert_manager.is_running is False
        assert alert_manager.notification_hub is not None
    
    def test_add_alert_rule(self, alert_manager, sample_alert_rule):
        """Test adding an alert rule"""        result = alert_manager.add_rule(sample_alert_rule)
        
        assert result is True
        assert "test_rule" in alert_manager.rules
        assert alert_manager.rules["test_rule"] == sample_alert_rule
    
    def test_add_duplicate_alert_rule(self, alert_manager, sample_alert_rule):
        """Test adding duplicate alert rule"""        alert_manager.add_rule(sample_alert_rule)
        
        # Adding same rule again should return False
        result = alert_manager.add_rule(sample_alert_rule)
        assert result is False
    
    def test_remove_alert_rule(self, alert_manager, sample_alert_rule):
        """Test removing an alert rule"""        alert_manager.add_rule(sample_alert_rule)
        
        result = alert_manager.remove_rule("test_rule")
        assert result is True
        assert "test_rule" not in alert_manager.rules
    
    def test_remove_nonexistent_alert_rule(self, alert_manager):
        """Test removing non-existent alert rule"""        result = alert_manager.remove_rule("nonexistent_rule")
        assert result is False
    
    def test_update_alert_rule(self, alert_manager, sample_alert_rule):
        """Test updating an alert rule"""        alert_manager.add_rule(sample_alert_rule)
        
        # Update the rule
        updated_rule = AlertRule(
            rule_id="test_rule",
            name="Updated Test Rule",
            description="Updated description",
            category=AlertCategory.PERFORMANCE,
            severity=AlertSeverity.CRITICAL,
            condition="test_metric > threshold",
            threshold=90.0,
            comparison_operator=">",
            time_window=600
        )
        
        result = alert_manager.update_rule("test_rule", updated_rule)
        assert result is True
        
        stored_rule = alert_manager.rules["test_rule"]
        assert stored_rule.name == "Updated Test Rule"
        assert stored_rule.threshold == 90.0
        assert stored_rule.severity == AlertSeverity.CRITICAL
    
    def test_evaluate_single_rule_trigger(self, alert_manager, sample_alert_rule):
        """Test evaluating rule that should trigger"""        alert_manager.add_rule(sample_alert_rule)
        
        # Create metric that exceeds threshold
        metric = MetricPoint(
            name="test_metric",
            value=85.0,  # Above threshold of 75
            timestamp=datetime.now(timezone.utc),
            labels={"service": "test"}
        )
        
        with patch.object(alert_manager.notification_hub, 'send_alert') as mock_send:
            alerts = alert_manager.evaluate_rules([metric])
            
            assert len(alerts) == 1
            assert alerts[0]['rule_id'] == "test_rule"
            assert alerts[0]['status'] == AlertStatus.ACTIVE
            assert mock_send.called
    
    def test_evaluate_single_rule_no_trigger(self, alert_manager, sample_alert_rule):
        """Test evaluating rule that should not trigger"""        alert_manager.add_rule(sample_alert_rule)
        
        # Create metric below threshold
        metric = MetricPoint(
            name="test_metric",
            value=50.0,  # Below threshold of 75
            timestamp=datetime.now(timezone.utc),
            labels={"service": "test"}
        )
        
        alerts = alert_manager.evaluate_rules([metric])
        assert len(alerts) == 0
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, alert_manager):
        """Test starting and stopping the monitoring loop"""        assert alert_manager.is_running is False
        
        # Start monitoring
        alert_manager.start_monitoring()
        assert alert_manager.is_running is True
        assert alert_manager.monitoring_thread is not None
        
        # Wait briefly for thread to start
        await asyncio.sleep(0.1)
        
        # Stop monitoring
        alert_manager.stop_monitoring()
        assert alert_manager.is_running is False
    
    def test_suppress_alert(self, alert_manager, sample_alert_rule):
        """Test alert suppression"""        alert_manager.add_rule(sample_alert_rule)
        
        # Suppress the alert
        result = alert_manager.suppress_alert("test_rule", 1800)  # 30 minutes
        assert result is True
        assert "test_rule" in alert_manager.suppression_cache
        
        # Verify suppression time
        suppression_info = alert_manager.suppression_cache["test_rule"]
        assert suppression_info['duration'] == 1800
        assert isinstance(suppression_info['until'], datetime)
    
    def test_is_suppressed_active(self, alert_manager):
        """Test checking if alert is currently suppressed"""        # Suppress alert for 30 minutes
        alert_manager.suppress_alert("test_rule", 1800)
        
        assert alert_manager.is_suppressed("test_rule") is True
    
    def test_is_suppressed_expired(self, alert_manager):
        """Test checking if alert suppression has expired"""        # Suppress alert for very short time
        alert_manager.suppress_alert("test_rule", 0.001)
        
        # Wait for suppression to expire
        time.sleep(0.002)
        
        assert alert_manager.is_suppressed("test_rule") is False
    
    def test_get_alert_statistics(self, alert_manager, sample_alert_rule):
        """Test getting alert statistics"""        alert_manager.add_rule(sample_alert_rule)
        
        # Add some test alert history
        alert_manager.alert_history.extend([
            {"rule_id": "test_rule", "severity": AlertSeverity.HIGH, "timestamp": datetime.now(timezone.utc)},
            {"rule_id": "test_rule", "severity": AlertSeverity.HIGH, "timestamp": datetime.now(timezone.utc)},
            {"rule_id": "other_rule", "severity": AlertSeverity.LOW, "timestamp": datetime.now(timezone.utc)}
        ])
        
        stats = alert_manager.get_alert_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_rules' in stats
        assert 'active_alerts' in stats
        assert 'total_alerts_today' in stats
        assert 'alerts_by_severity' in stats
        assert 'alerts_by_category' in stats
        assert 'top_alerting_rules' in stats
        
        assert stats['total_rules'] == 1
        assert stats['total_alerts_today'] == 3


class TestThresholdMonitor:
    """Test cases for ThresholdMonitor class"""    
    @pytest.fixture
    def threshold_monitor(self):
        """Create ThresholdMonitor instance for testing"""        return ThresholdMonitor()
    
    def test_threshold_monitor_initialization(self, threshold_monitor):
        """Test ThresholdMonitor initialization"""        assert isinstance(threshold_monitor.thresholds, dict)
        assert isinstance(threshold_monitor.metric_history, dict)
        assert isinstance(threshold_monitor.breach_history, list)
    
    def test_add_threshold(self, threshold_monitor):
        """Test adding a threshold"""        result = threshold_monitor.add_threshold(
            metric_name="cpu_usage",
            threshold_value=80.0,
            comparison="greater_than",
            time_window=300,
            min_breaches=2
        )
        
        assert result is True
        assert "cpu_usage" in threshold_monitor.thresholds
        
        threshold = threshold_monitor.thresholds["cpu_usage"]
        assert threshold['value'] == 80.0
        assert threshold['comparison'] == "greater_than"
        assert threshold['time_window'] == 300
        assert threshold['min_breaches'] == 2
    
    def test_check_threshold_breach(self, threshold_monitor):
        """Test checking for threshold breach"""        threshold_monitor.add_threshold(
            metric_name="memory_usage",
            threshold_value=90.0,
            comparison="greater_than",
            time_window=300,
            min_breaches=1
        )
        
        # Record metric that breaches threshold
        breach = threshold_monitor.check_threshold(
            metric_name="memory_usage",
            value=95.0,
            timestamp=datetime.now(timezone.utc)
        )
        
        assert breach is True
        assert len(threshold_monitor.breach_history) == 1
        
        breach_record = threshold_monitor.breach_history[0]
        assert breach_record['metric_name'] == "memory_usage"
        assert breach_record['threshold_value'] == 90.0
        assert breach_record['actual_value'] == 95.0
    
    def test_check_threshold_no_breach(self, threshold_monitor):
        """Test checking threshold with no breach"""        threshold_monitor.add_threshold(
            metric_name="disk_usage",
            threshold_value=85.0,
            comparison="greater_than",
            time_window=300,
            min_breaches=1
        )
        
        # Record metric below threshold
        breach = threshold_monitor.check_threshold(
            metric_name="disk_usage",
            value=70.0,
            timestamp=datetime.now(timezone.utc)
        )
        
        assert breach is False
        assert len(threshold_monitor.breach_history) == 0
    
    def test_threshold_with_min_breaches(self, threshold_monitor):
        """Test threshold requiring multiple breaches"""        threshold_monitor.add_threshold(
            metric_name="error_rate",
            threshold_value=5.0,
            comparison="greater_than",
            time_window=300,
            min_breaches=3
        )
        
        timestamp = datetime.now(timezone.utc)
        
        # First breach - should not trigger
        breach1 = threshold_monitor.check_threshold("error_rate", 8.0, timestamp)
        assert breach1 is False
        
        # Second breach - should not trigger
        breach2 = threshold_monitor.check_threshold("error_rate", 7.0, timestamp + timedelta(seconds=30))
        assert breach2 is False
        
        # Third breach - should trigger
        breach3 = threshold_monitor.check_threshold("error_rate", 9.0, timestamp + timedelta(seconds=60))
        assert breach3 is True
    
    def test_get_breach_statistics(self, threshold_monitor):
        """Test getting breach statistics"""        threshold_monitor.add_threshold("test_metric", 50.0, "greater_than", 300, 1)
        
        # Add some breach history
        now = datetime.now(timezone.utc)
        threshold_monitor.breach_history.extend([
            {
                'metric_name': 'test_metric',
                'threshold_value': 50.0,
                'actual_value': 75.0,
                'timestamp': now,
                'comparison': 'greater_than'
            },
            {
                'metric_name': 'test_metric',
                'threshold_value': 50.0,
                'actual_value': 80.0,
                'timestamp': now - timedelta(hours=1),
                'comparison': 'greater_than'
            }
        ])
        
        stats = threshold_monitor.get_breach_statistics(hours=24)
        
        assert isinstance(stats, dict)
        assert 'total_breaches' in stats
        assert 'breaches_by_metric' in stats
        assert 'average_breach_severity' in stats
        assert 'most_breached_metrics' in stats
        
        assert stats['total_breaches'] == 2
        assert 'test_metric' in stats['breaches_by_metric']


class TestSecurityAlerts:
    """Test cases for SecurityAlerts class"""    
    @pytest.fixture
    def security_alerts(self):
        """Create SecurityAlerts instance for testing"""        return SecurityAlerts()
    
    def test_security_alerts_initialization(self, security_alerts):
        """Test SecurityAlerts initialization"""        assert isinstance(security_alerts.security_rules, dict)
        assert isinstance(security_alerts.threat_patterns, list)
        assert isinstance(security_alerts.security_incidents, list)
        assert len(security_alerts.threat_patterns) > 0  # Should have default patterns
    
    def test_add_security_rule(self, security_alerts):
        """Test adding a security rule"""        rule = {
            'rule_id': 'failed_login_attempts',
            'name': 'Multiple Failed Logins',
            'description': 'Detect multiple failed login attempts',
            'pattern': 'login_failed',
            'threshold': 5,
            'time_window': 300,
            'severity': AlertSeverity.HIGH,
            'action': 'block_ip'
        }
        
        result = security_alerts.add_security_rule(rule)
        assert result is True
        assert 'failed_login_attempts' in security_alerts.security_rules
    
    def test_detect_security_threat_basic(self, security_alerts):
        """Test basic security threat detection"""        # Add a security rule
        rule = {
            'rule_id': 'suspicious_activity',
            'name': 'Suspicious Activity',
            'description': 'Detect suspicious user activity',
            'pattern': 'suspicious_request',
            'threshold': 3,
            'time_window': 300,
            'severity': AlertSeverity.CRITICAL,
            'action': 'alert_admin'
        }
        security_alerts.add_security_rule(rule)
        
        # Simulate security events
        events = [
            {'type': 'suspicious_request', 'source_ip': '192.168.1.100', 'timestamp': datetime.now(timezone.utc)},
            {'type': 'suspicious_request', 'source_ip': '192.168.1.100', 'timestamp': datetime.now(timezone.utc)},
            {'type': 'suspicious_request', 'source_ip': '192.168.1.100', 'timestamp': datetime.now(timezone.utc)}
        ]
        
        threats = security_alerts.detect_threats(events)
        
        assert len(threats) == 1
        assert threats[0]['rule_id'] == 'suspicious_activity'
        assert threats[0]['severity'] == AlertSeverity.CRITICAL
        assert threats[0]['source_ip'] == '192.168.1.100'
    
    def test_analyze_threat_patterns(self, security_alerts):
        """Test threat pattern analysis"""        # Add security incidents
        now = datetime.now(timezone.utc)
        security_alerts.security_incidents.extend([
            {
                'incident_id': 'inc_001',
                'type': 'brute_force',
                'source_ip': '10.0.0.1',
                'timestamp': now,
                'severity': AlertSeverity.HIGH
            },
            {
                'incident_id': 'inc_002', 
                'type': 'brute_force',
                'source_ip': '10.0.0.2',
                'timestamp': now - timedelta(hours=1),
                'severity': AlertSeverity.HIGH
            },
            {
                'incident_id': 'inc_003',
                'type': 'data_exfiltration',
                'source_ip': '10.0.0.3',
                'timestamp': now - timedelta(hours=2),
                'severity': AlertSeverity.CRITICAL
            }
        ])
        
        analysis = security_alerts.analyze_threat_patterns(hours=24)
        
        assert isinstance(analysis, dict)
        assert 'total_incidents' in analysis
        assert 'incidents_by_type' in analysis
        assert 'incidents_by_severity' in analysis
        assert 'top_source_ips' in analysis
        assert 'trend_analysis' in analysis
        
        assert analysis['total_incidents'] == 3
        assert 'brute_force' in analysis['incidents_by_type']
        assert 'data_exfiltration' in analysis['incidents_by_type']
    
    def test_get_security_recommendations(self, security_alerts):
        """Test getting security recommendations"""        # Add some incidents to analyze
        now = datetime.now(timezone.utc)
        security_alerts.security_incidents.extend([
            {'type': 'sql_injection', 'severity': AlertSeverity.CRITICAL, 'timestamp': now},
            {'type': 'xss_attempt', 'severity': AlertSeverity.HIGH, 'timestamp': now},
            {'type': 'brute_force', 'severity': AlertSeverity.MEDIUM, 'timestamp': now}
        ])
        
        recommendations = security_alerts.get_security_recommendations()
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Each recommendation should have required fields
        for rec in recommendations:
            assert 'priority' in rec
            assert 'title' in rec
            assert 'description' in rec
            assert 'action_items' in rec


class TestBusinessKPIAlerts:
    """Test cases for BusinessKPIAlerts class"""    
    @pytest.fixture
    def business_alerts(self):
        """Create BusinessKPIAlerts instance for testing"""        return BusinessKPIAlerts()
    
    def test_business_alerts_initialization(self, business_alerts):
        """Test BusinessKPIAlerts initialization"""        assert isinstance(business_alerts.kpi_rules, dict)
        assert isinstance(business_alerts.kpi_history, dict)
        assert isinstance(business_alerts.business_events, list)
        assert len(business_alerts.kpi_rules) > 0  # Should have default KPI rules
    
    def test_add_kpi_rule(self, business_alerts):
        """Test adding a KPI rule"""        kpi_rule = {
            'kpi_id': 'user_engagement_rate',
            'name': 'User Engagement Rate',
            'description': 'Monitor user engagement rate',
            'metric': 'engagement_rate',
            'target_value': 0.75,
            'threshold_low': 0.60,
            'threshold_high': 0.90,
            'evaluation_period': 'daily',
            'severity': AlertSeverity.MEDIUM,
            'stakeholders': ['product_manager', 'marketing_team']
        }
        
        result = business_alerts.add_kpi_rule(kpi_rule)
        assert result is True
        assert 'user_engagement_rate' in business_alerts.kpi_rules
    
    def test_evaluate_kpi_below_threshold(self, business_alerts):
        """Test KPI evaluation below threshold"""        # Add KPI rule
        kpi_rule = {
            'kpi_id': 'conversion_rate',
            'name': 'Conversion Rate',
            'description': 'Monitor conversion rate',
            'metric': 'conversion_rate',
            'target_value': 0.15,
            'threshold_low': 0.10,
            'threshold_high': 0.20,
            'evaluation_period': 'daily',
            'severity': AlertSeverity.HIGH,
            'stakeholders': ['sales_team']
        }
        business_alerts.add_kpi_rule(kpi_rule)
        
        # Evaluate with low value
        alerts = business_alerts.evaluate_kpi('conversion_rate', 0.08, datetime.now(timezone.utc))
        
        assert len(alerts) == 1
        assert alerts[0]['kpi_id'] == 'conversion_rate'
        assert alerts[0]['alert_type'] == 'below_threshold'
        assert alerts[0]['severity'] == AlertSeverity.HIGH
    
    def test_evaluate_kpi_within_threshold(self, business_alerts):
        """Test KPI evaluation within threshold"""        # Add KPI rule
        kpi_rule = {
            'kpi_id': 'revenue_growth',
            'name': 'Revenue Growth',
            'description': 'Monitor revenue growth',
            'metric': 'revenue_growth_rate',
            'target_value': 0.20,
            'threshold_low': 0.15,
            'threshold_high': 0.25,
            'evaluation_period': 'monthly',
            'severity': AlertSeverity.MEDIUM,
            'stakeholders': ['finance_team']
        }
        business_alerts.add_kpi_rule(kpi_rule)
        
        # Evaluate with value within threshold
        alerts = business_alerts.evaluate_kpi('revenue_growth', 0.18, datetime.now(timezone.utc))
        
        assert len(alerts) == 0  # No alerts should be generated
    
    def test_generate_business_insights(self, business_alerts):
        """Test business insights generation"""        # Add some KPI history
        now = datetime.now(timezone.utc)
        business_alerts.kpi_history = {
            'user_acquisition': [
                {'value': 150, 'timestamp': now - timedelta(days=7)},
                {'value': 200, 'timestamp': now - timedelta(days=6)},
                {'value': 180, 'timestamp': now - timedelta(days=5)},
                {'value': 250, 'timestamp': now - timedelta(days=4)},
                {'value': 220, 'timestamp': now - timedelta(days=3)},
                {'value': 300, 'timestamp': now - timedelta(days=2)},
                {'value': 280, 'timestamp': now - timedelta(days=1)}
            ]
        }
        
        insights = business_alerts.generate_business_insights(days=7)
        
        assert isinstance(insights, dict)
        assert 'kpi_trends' in insights
        assert 'performance_summary' in insights
        assert 'recommendations' in insights
        assert 'growth_metrics' in insights
    
    def test_get_stakeholder_alerts(self, business_alerts):
        """Test getting alerts for specific stakeholders"""        # Add business events for different stakeholders
        now = datetime.now(timezone.utc)
        business_alerts.business_events.extend([
            {
                'event_id': 'evt_001',
                'kpi_id': 'revenue_drop',
                'stakeholders': ['ceo', 'cfo'],
                'severity': AlertSeverity.CRITICAL,
                'timestamp': now
            },
            {
                'event_id': 'evt_002',
                'kpi_id': 'user_churn',
                'stakeholders': ['product_manager', 'customer_success'],
                'severity': AlertSeverity.HIGH,
                'timestamp': now
            },
            {
                'event_id': 'evt_003',
                'kpi_id': 'server_performance',
                'stakeholders': ['sre_team', 'devops'],
                'severity': AlertSeverity.MEDIUM,
                'timestamp': now
            }
        ])
        
        ceo_alerts = business_alerts.get_stakeholder_alerts('ceo')
        product_alerts = business_alerts.get_stakeholder_alerts('product_manager')
        
        assert len(ceo_alerts) == 1
        assert ceo_alerts[0]['kpi_id'] == 'revenue_drop'
        
        assert len(product_alerts) == 1
        assert product_alerts[0]['kpi_id'] == 'user_churn'


class TestEscalationManager:
    """Test cases for EscalationManager class"""    
    @pytest.fixture
    def escalation_manager(self):
        """Create EscalationManager instance for testing"""        return EscalationManager()
    
    def test_escalation_manager_initialization(self, escalation_manager):
        """Test EscalationManager initialization"""        assert isinstance(escalation_manager.escalation_rules, dict)
        assert isinstance(escalation_manager.active_escalations, dict)
        assert isinstance(escalation_manager.escalation_history, list)
    
    def test_add_escalation_rule(self, escalation_manager):
        """Test adding an escalation rule"""        rule = {
            'rule_id': 'critical_system_alert',
            'name': 'Critical System Alert Escalation',
            'trigger_severity': AlertSeverity.CRITICAL,
            'escalation_levels': [
                {'level': 1, 'delay_minutes': 5, 'recipients': ['oncall_engineer']},
                {'level': 2, 'delay_minutes': 15, 'recipients': ['engineering_manager']},
                {'level': 3, 'delay_minutes': 30, 'recipients': ['cto', 'vp_engineering']}
            ],
            'max_escalations': 3,
            'auto_resolve': False
        }
        
        result = escalation_manager.add_escalation_rule(rule)
        assert result is True
        assert 'critical_system_alert' in escalation_manager.escalation_rules
    
    @pytest.mark.asyncio
    async def test_trigger_escalation(self, escalation_manager):
        """Test triggering an escalation"""        # Add escalation rule
        rule = {
            'rule_id': 'high_priority_alert',
            'name': 'High Priority Alert',
            'trigger_severity': AlertSeverity.HIGH,
            'escalation_levels': [
                {'level': 1, 'delay_minutes': 1, 'recipients': ['team_lead']},
                {'level': 2, 'delay_minutes': 5, 'recipients': ['manager']}
            ],
            'max_escalations': 2,
            'auto_resolve': False
        }
        escalation_manager.add_escalation_rule(rule)
        
        # Create alert
        alert = {
            'alert_id': 'alert_123',
            'rule_id': 'test_rule',
            'severity': AlertSeverity.HIGH,
            'message': 'Test alert message',
            'timestamp': datetime.now(timezone.utc)
        }
        
        with patch.object(escalation_manager, '_send_escalation_notification') as mock_send:
            result = escalation_manager.trigger_escalation(alert, 'high_priority_alert')
            
            assert result is True
            assert 'alert_123' in escalation_manager.active_escalations
            
            escalation = escalation_manager.active_escalations['alert_123']
            assert escalation['current_level'] == 0
            assert escalation['escalation_rule_id'] == 'high_priority_alert'
    
    def test_resolve_escalation(self, escalation_manager):
        """Test resolving an escalation"""        # Add active escalation
        escalation_manager.active_escalations['alert_456'] = {
            'alert_id': 'alert_456',
            'escalation_rule_id': 'test_escalation',
            'current_level': 1,
            'started_at': datetime.now(timezone.utc),
            'next_escalation_at': datetime.now(timezone.utc) + timedelta(minutes=5)
        }
        
        result = escalation_manager.resolve_escalation('alert_456')
        
        assert result is True
        assert 'alert_456' not in escalation_manager.active_escalations
        assert len(escalation_manager.escalation_history) == 1
        
        history_entry = escalation_manager.escalation_history[0]
        assert history_entry['alert_id'] == 'alert_456'
        assert history_entry['status'] == 'resolved'
    
    def test_get_escalation_statistics(self, escalation_manager):
        """Test getting escalation statistics"""        # Add escalation history
        now = datetime.now(timezone.utc)
        escalation_manager.escalation_history.extend([
            {
                'alert_id': 'alert_001',
                'escalation_rule_id': 'rule_001',
                'max_level_reached': 2,
                'total_duration_minutes': 30,
                'status': 'resolved',
                'timestamp': now
            },
            {
                'alert_id': 'alert_002',
                'escalation_rule_id': 'rule_002',
                'max_level_reached': 1,
                'total_duration_minutes': 15,
                'status': 'resolved',
                'timestamp': now - timedelta(hours=1)
            }
        ])
        
        stats = escalation_manager.get_escalation_statistics(hours=24)
        
        assert isinstance(stats, dict)
        assert 'total_escalations' in stats
        assert 'average_resolution_time' in stats
        assert 'escalations_by_rule' in stats
        assert 'escalations_by_level' in stats
        
        assert stats['total_escalations'] == 2
        assert stats['average_resolution_time'] == 22.5  # (30 + 15) / 2


class TestNotificationHub:
    """Test cases for NotificationHub class"""    
    @pytest.fixture
    def notification_hub(self):
        """Create NotificationHub instance for testing"""        return NotificationHub()
    
    def test_notification_hub_initialization(self, notification_hub):
        """Test NotificationHub initialization"""        assert isinstance(notification_hub.channels, dict)
        assert isinstance(notification_hub.notification_queue, list)
        assert isinstance(notification_hub.sent_notifications, list)
        assert notification_hub.is_running is False
    
    def test_configure_email_channel(self, notification_hub):
        """Test configuring email channel"""        email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'alerts@example.com',
            'password': 'secret_password',
            'use_tls': True
        }
        
        result = notification_hub.configure_channel(AlertChannel.EMAIL, email_config)
        assert result is True
        assert AlertChannel.EMAIL in notification_hub.channels
    
    def test_configure_slack_channel(self, notification_hub):
        """Test configuring Slack channel"""        slack_config = {
            'webhook_url': 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX',
            'default_channel': '#alerts',
            'username': 'AlertBot'
        }
        
        result = notification_hub.configure_channel(AlertChannel.SLACK, slack_config)
        assert result is True
        assert AlertChannel.SLACK in notification_hub.channels
    
    @patch('smtplib.SMTP')
    def test_send_email_notification(self, mock_smtp, notification_hub):
        """Test sending email notification"""        # Configure email channel
        email_config = {
            'smtp_server': 'smtp.example.com',
            'smtp_port': 587,
            'username': 'alerts@example.com',
            'password': 'password',
            'use_tls': True
        }
        notification_hub.configure_channel(AlertChannel.EMAIL, email_config)
        
        alert = {
            'alert_id': 'test_alert',
            'rule_id': 'test_rule',
            'severity': AlertSeverity.HIGH,
            'message': 'Test alert message',
            'timestamp': datetime.now(timezone.utc)
        }
        
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        result = notification_hub.send_notification(
            channel=AlertChannel.EMAIL,
            recipients=['admin@example.com'],
            alert=alert
        )
        
        assert result is True
        mock_smtp.assert_called_once()
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    @patch('requests.post')
    def test_send_slack_notification(self, mock_post, notification_hub):
        """Test sending Slack notification"""        # Configure Slack channel
        slack_config = {
            'webhook_url': 'https://hooks.slack.com/services/TEST/WEBHOOK/URL',
            'default_channel': '#alerts',
            'username': 'AlertBot'
        }
        notification_hub.configure_channel(AlertChannel.SLACK, slack_config)
        
        alert = {
            'alert_id': 'slack_test_alert',
            'rule_id': 'slack_test_rule', 
            'severity': AlertSeverity.CRITICAL,
            'message': 'Critical system alert',
            'timestamp': datetime.now(timezone.utc)
        }
        
        # Mock successful response
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = 'ok'
        
        result = notification_hub.send_notification(
            channel=AlertChannel.SLACK,
            recipients=['#critical-alerts'],
            alert=alert
        )
        
        assert result is True
        mock_post.assert_called_once()
        
        # Verify the payload contains expected fields
        call_args = mock_post.call_args
        payload = json.loads(call_args[1]['data'])
        assert 'text' in payload
        assert 'attachments' in payload
        assert alert['alert_id'] in payload['text']
    
    def test_queue_notification(self, notification_hub):
        """Test queuing a notification"""        alert = {
            'alert_id': 'queued_alert',
            'rule_id': 'queue_test_rule',
            'severity': AlertSeverity.MEDIUM,
            'message': 'Queued alert message',
            'timestamp': datetime.now(timezone.utc)
        }
        
        result = notification_hub.queue_notification(
            channel=AlertChannel.EMAIL,
            recipients=['test@example.com'],
            alert=alert,
            priority=1
        )
        
        assert result is True
        assert len(notification_hub.notification_queue) == 1
        
        queued_notification = notification_hub.notification_queue[0]
        assert queued_notification['channel'] == AlertChannel.EMAIL
        assert queued_notification['alert'] == alert
        assert queued_notification['priority'] == 1
    
    def test_get_notification_statistics(self, notification_hub):
        """Test getting notification statistics"""        # Add some sent notifications
        now = datetime.now(timezone.utc)
        notification_hub.sent_notifications.extend([
            {
                'channel': AlertChannel.EMAIL,
                'alert_id': 'alert_001',
                'status': 'sent',
                'timestamp': now,
                'recipients': ['admin@example.com']
            },
            {
                'channel': AlertChannel.SLACK,
                'alert_id': 'alert_002',
                'status': 'sent', 
                'timestamp': now - timedelta(minutes=30),
                'recipients': ['#alerts']
            },
            {
                'channel': AlertChannel.EMAIL,
                'alert_id': 'alert_003',
                'status': 'failed',
                'timestamp': now - timedelta(hours=1),
                'recipients': ['user@example.com']
            }
        ])
        
        stats = notification_hub.get_notification_statistics(hours=24)
        
        assert isinstance(stats, dict)
        assert 'total_notifications' in stats
        assert 'notifications_by_channel' in stats
        assert 'notifications_by_status' in stats
        assert 'success_rate' in stats
        
        assert stats['total_notifications'] == 3
        assert stats['notifications_by_channel'][AlertChannel.EMAIL.value] == 2
        assert stats['notifications_by_channel'][AlertChannel.SLACK.value] == 1
        assert stats['success_rate'] > 0.5  # 2 successful out of 3


# Integration Tests
class TestAlertingSystemIntegration:
    """Integration tests for the complete alerting system"""    
    @pytest.fixture
    def full_alerting_system(self):
        """Create complete alerting system for integration testing"""        alert_manager = AlertManager()
        
        # Configure notification hub
        notification_hub = alert_manager.notification_hub
        
        # Configure email channel
        email_config = {
            'smtp_server': 'localhost',
            'smtp_port': 1025,  # MailHog for testing
            'username': 'test@example.com',
            'password': 'test_password',
            'use_tls': False
        }
        notification_hub.configure_channel(AlertChannel.EMAIL, email_config)
        
        # Add comprehensive alert rules
        cpu_rule = AlertRule(
            rule_id="high_cpu",
            name="High CPU Usage",
            description="Alert when CPU usage exceeds 80%",
            category=AlertCategory.PERFORMANCE,
            severity=AlertSeverity.HIGH,
            condition="cpu_usage_percent > threshold",
            threshold=80.0,
            comparison_operator=">",
            time_window=300,
            channels=[AlertChannel.EMAIL],
            recipients=["sre@example.com"]
        )
        alert_manager.add_rule(cpu_rule)
        
        memory_rule = AlertRule(
            rule_id="high_memory",
            name="High Memory Usage", 
            description="Alert when memory usage exceeds 90%",
            category=AlertCategory.PERFORMANCE,
            severity=AlertSeverity.CRITICAL,
            condition="memory_usage_percent > threshold",
            threshold=90.0,
            comparison_operator=">",
            time_window=180,
            channels=[AlertChannel.EMAIL],
            recipients=["sre@example.com", "oncall@example.com"]
        )
        alert_manager.add_rule(memory_rule)
        
        return alert_manager
    
    @patch('smtplib.SMTP')
    def test_end_to_end_alert_flow(self, mock_smtp, full_alerting_system):
        """Test complete end-to-end alert flow"""        alert_manager = full_alerting_system
        
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Create metrics that trigger alerts
        high_cpu_metric = MetricPoint(
            name="cpu_usage_percent",
            value=85.0,  # Above 80% threshold
            timestamp=datetime.now(timezone.utc),
            labels={"host": "web-server-01"}
        )
        
        critical_memory_metric = MetricPoint(
            name="memory_usage_percent", 
            value=95.0,  # Above 90% threshold
            timestamp=datetime.now(timezone.utc),
            labels={"host": "db-server-01"}
        )
        
        # Evaluate rules and trigger alerts
        triggered_alerts = alert_manager.evaluate_rules([high_cpu_metric, critical_memory_metric])
        
        # Verify alerts were triggered
        assert len(triggered_alerts) == 2
        
        # Verify one high severity and one critical severity alert
        severities = [alert['severity'] for alert in triggered_alerts]
        assert AlertSeverity.HIGH in severities
        assert AlertSeverity.CRITICAL in severities
        
        # Verify notifications were sent
        assert mock_smtp.call_count >= 1  # At least one email sent
        assert mock_server.send_message.call_count >= 1
    
    def test_alert_suppression_integration(self, full_alerting_system):
        """Test alert suppression in integration scenario"""        alert_manager = full_alerting_system
        
        # Suppress high CPU alerts for 30 minutes
        alert_manager.suppress_alert("high_cpu", 1800)
        
        # Create metric that would normally trigger alert
        cpu_metric = MetricPoint(
            name="cpu_usage_percent",
            value=85.0,
            timestamp=datetime.now(timezone.utc),
            labels={"host": "web-server-02"}
        )
        
        # Evaluate rules - should not trigger suppressed alert
        triggered_alerts = alert_manager.evaluate_rules([cpu_metric])
        
        # Should not have any alerts due to suppression
        high_cpu_alerts = [a for a in triggered_alerts if a['rule_id'] == 'high_cpu']
        assert len(high_cpu_alerts) == 0
        
        # Verify suppression status
        assert alert_manager.is_suppressed("high_cpu") is True
    
    def test_multiple_metrics_single_rule(self, full_alerting_system):
        """Test multiple metrics triggering the same rule"""        alert_manager = full_alerting_system
        
        # Create multiple high CPU metrics from different hosts
        metrics = [
            MetricPoint(
                name="cpu_usage_percent",
                value=82.0,
                timestamp=datetime.now(timezone.utc),
                labels={"host": f"web-server-{i:02d}"}
            ) for i in range(1, 6)  # 5 servers with high CPU
        ]
        
        # Evaluate all metrics
        triggered_alerts = alert_manager.evaluate_rules(metrics)
        
        # Should trigger alert for each high CPU instance
        high_cpu_alerts = [a for a in triggered_alerts if a['rule_id'] == 'high_cpu']
        assert len(high_cpu_alerts) == 5
        
        # Verify each alert has different host information
        hosts = [alert['labels']['host'] for alert in high_cpu_alerts]
        assert len(set(hosts)) == 5  # All unique hosts
    
    def test_alerting_performance_under_load(self, full_alerting_system):
        """Test alerting system performance under high load"""        alert_manager = full_alerting_system
        
        # Generate large number of metrics
        start_time = time.time()
        
        metrics = []
        for i in range(1000):  # 1000 metrics
            metrics.append(MetricPoint(
                name="cpu_usage_percent",
                value=75.0 + (i % 20),  # Some will exceed threshold
                timestamp=datetime.now(timezone.utc),
                labels={"host": f"server-{i:04d}"}
            ))
        
        # Evaluate all metrics
        with patch.object(alert_manager.notification_hub, 'send_alert'):
            triggered_alerts = alert_manager.evaluate_rules(metrics)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time (under 1 second for 1000 metrics)
        assert processing_time < 1.0
        
        # Verify appropriate number of alerts triggered
        assert len(triggered_alerts) > 0
        assert len(triggered_alerts) < 1000  # Not all metrics should trigger
    
    def test_alert_history_and_statistics(self, full_alerting_system):
        """Test alert history tracking and statistics generation"""        alert_manager = full_alerting_system
        
        # Generate alerts over time
        now = datetime.now(timezone.utc)
        
        # Add historical alerts
        for i in range(10):
            alert_manager.alert_history.append({
                'alert_id': f'hist_alert_{i}',
                'rule_id': 'high_cpu' if i % 2 == 0 else 'high_memory',
                'severity': AlertSeverity.HIGH if i % 3 == 0 else AlertSeverity.MEDIUM,
                'timestamp': now - timedelta(hours=i),
                'status': AlertStatus.RESOLVED,
                'resolution_time': 300 + i * 60  # Variable resolution times
            })
        
        # Get statistics
        stats = alert_manager.get_alert_statistics()
        
        # Verify comprehensive statistics
        assert stats['total_alerts_today'] == 10
        assert 'high_cpu' in stats['top_alerting_rules']
        assert 'high_memory' in stats['top_alerting_rules']
        assert len(stats['alerts_by_severity']) >= 2
        assert 'average_resolution_time' in stats
        assert stats['average_resolution_time'] > 0


if __name__ == '__main__':
    pytest.main([str(Path(__file__)), '-v', '--tb=short'])
