#!/usr/bin/env python3
"""🚨 Test Suite for Intelligent Alert System
=========================================

Comprehensive tests for the enhanced intelligent alert system ensuring
proper functionality across Business, Technical, and AI alert categories.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import unittest
import asyncio
from datetime import datetime, timedelta
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from monitoring.alerts import (
    alert_coordinator,
    BusinessMetrics,
    TechnicalMetrics, 
    ModelMetrics,
    SystemHealthStatus,
    AlertSeverity,
    SecurityThreatLevel,
    AIModelType
)


class TestIntelligentAlertSystem(unittest.TestCase):
    """
Test suite for the intelligent alert system"""
    
    def setUp(self):
        """
Set up test environment"""
        self.coordinator = alert_coordinator
        
        # Clear any existing alerts for clean testing
        self.coordinator.alert_manager.active_alerts.clear()
        self.coordinator.alert_manager.alert_history.clear()
    
    def test_business_alert_revenue_drop_detection(self):
        """
Test that business alerts properly detect revenue drops"""
        
        async def run_test():
            # Create metrics with significant revenue drop (45%)
            critical_metrics = BusinessMetrics(
                timestamp=datetime.now(),
                current_revenue=8000.0,    # 45% drop!
                previous_revenue=14500.0,
                daily_revenue=[12000, 13000, 14500, 12000, 8000],
                weekly_revenue=[95000, 98000, 102000, 85000],
                active_users=850,
                new_users=12,
                user_retention_rate=0.72,
                avg_session_duration=325.0,
                bounce_rate=0.45,
                conversion_rate=0.06,
                payment_success_rate=0.92,
                content_uploads=87,
                user_satisfaction_score=2.8,
                support_tickets=45,
                churn_rate=0.08
            )
            
            # Evaluate metrics
            result = await self.coordinator.evaluate_all_metrics(business_metrics=critical_metrics)
            
            # Assert that alerts were triggered
            self.assertGreater(result.total_active_alerts, 0, "Revenue drop should trigger alerts")
            
            # Check for specific business alert types
            business_alerts = [
                alert for alert in self.coordinator.alert_manager.active_alerts.values()
                if alert.category.value == "business"
            ]
            
            self.assertGreater(len(business_alerts), 0, "Should have business alerts")
            
            # Verify alert severity
            critical_alerts = [
                alert for alert in business_alerts 
                if alert.severity == AlertSeverity.CRITICAL
            ]
            self.assertGreater(len(critical_alerts), 0, "Should have critical alerts for severe revenue drop")
        
        asyncio.run(run_test())
    
    def test_technical_alert_infrastructure_monitoring(self):
        """Test that technical alerts properly detect infrastructure issues"""
        
        async def run_test():
            # Create metrics with critical system issues - using exact field names
            critical_metrics = TechnicalMetrics(
                timestamp=datetime.now(),
                cpu_usage=95.0,          # Critical CPU usage
                memory_usage=92.0,       # Critical memory usage
                disk_usage=89.0,
                network_latency=250.0,
                service_availability=0.97,  # Below threshold
                api_response_time=15000,    # 15 seconds - critical
                error_rate=0.12,           # 12% error rate - critical
                throughput=450.0,
                security_threat_score=0.8, # High threat score
                failed_logins=120,
                suspicious_activities=25,
                blocked_ips=15,
                security_events=[
                    {"type": "intrusion_attempt", "severity": "high"},
                    {"type": "ddos_attack", "severity": "critical"}
                ],
                service_name="ainflue-api",
                environment="production",
                region="us-west-2"
            )
            
            # Evaluate metrics
            result = await self.coordinator.evaluate_all_metrics(technical_metrics=critical_metrics)
            
            # Assert that technical alerts were triggered
            self.assertGreater(result.total_active_alerts, 0, "Critical infrastructure issues should trigger alerts")
            
            # Check system health degradation
            self.assertIn(result.system_health, [SystemHealthStatus.CRITICAL, SystemHealthStatus.WARNING, SystemHealthStatus.EMERGENCY], 
                         "System health should be degraded with critical technical issues")
        
        asyncio.run(run_test())
    
    def test_ai_alert_model_performance_monitoring(self):
        """Test that AI alerts properly detect model performance issues"""
        
        async def run_test():
            # Create metrics showing model degradation - using exact field names
            degraded_metrics = ModelMetrics(
                model_id="content_fingerprinting_v2",
                model_name="Content Fingerprinting Model",
                model_type=AIModelType.CONTENT_FINGERPRINTING,
                timestamp=datetime.now(),
                accuracy=0.72,          # Down from baseline of ~0.95 (23% drop)
                precision=0.68,
                recall=0.71,
                f1_score=0.69,
                auc_roc=0.75,
                inference_latency_p50=8000.0,  # 8 seconds - slow
                inference_latency_p95=15000.0, # 15 seconds - critical
                inference_latency_p99=20000.0, # 20 seconds - very critical
                throughput=25.0,
                error_rate=0.15,          # 15% error rate - critical
                data_drift_score=0.85,    # High data drift
                concept_drift_score=0.78, # High concept drift
                prediction_drift_score=0.82, # High prediction drift
                cpu_usage=85.0,
                memory_usage=85.0,
                gpu_utilization=82.0,
                data_quality_score=0.65,  # Poor data quality
                missing_values_ratio=0.12,
                outlier_ratio=0.08,
                prediction_confidence=0.68,
                business_impact_score=8.5,
                environment="production",
                version="v2.1.3"
            )
            
            # Evaluate metrics
            result = await self.coordinator.evaluate_all_metrics(ai_metrics=[degraded_metrics])
            
            # Assert that AI alerts were triggered
            self.assertGreater(result.total_active_alerts, 0, "Model performance degradation should trigger alerts")
            
            # Check for AI-specific alerts
            ai_alerts = [
                alert for alert in self.coordinator.alert_manager.active_alerts.values()
                if alert.category.value == "ai_ml"
            ]
            
            self.assertGreater(len(ai_alerts), 0, "Should have AI/ML alerts")
        
        asyncio.run(run_test())
    
    def test_comprehensive_alert_system_integration(self):
        """Test complete alert system with all categories working together"""
        
        async def run_test():
            # Create a comprehensive scenario with issues across all categories
            
            # Business crisis
            business_metrics = BusinessMetrics(
                timestamp=datetime.now(),
                current_revenue=7000.0,    # 50% drop - severe
                previous_revenue=14000.0,
                daily_revenue=[14000, 12000, 10000, 8000, 7000],
                weekly_revenue=[95000, 85000, 70000, 55000],
                active_users=500,
                new_users=8,
                user_retention_rate=0.55,
                avg_session_duration=200.0,
                bounce_rate=0.65,
                conversion_rate=0.03,
                payment_success_rate=0.88,
                content_uploads=45,
                user_satisfaction_score=2.5,
                support_tickets=65,
                churn_rate=0.18
            )
            
            # Infrastructure crisis
            technical_metrics = TechnicalMetrics(
                timestamp=datetime.now(),
                cpu_usage=96.0,
                memory_usage=94.0,
                disk_usage=92.0,
                network_latency=800.0,
                service_availability=0.94,
                api_response_time=22000,
                error_rate=0.18,
                throughput=180.0,
                security_threat_score=0.9, # Very high threat
                failed_logins=180,
                suspicious_activities=35,
                blocked_ips=25,
                security_events=[
                    {"type": "security_breach", "severity": "emergency"},
                    {"type": "data_leak_attempt", "severity": "critical"}
                ],
                service_name="ainflue-core",
                environment="production"
            )
            
            # AI model crisis
            ai_metrics = ModelMetrics(
                model_id="critical_ai_model",
                model_name="Critical AI Model",
                model_type=AIModelType.SIMILARITY_DETECTION,
                timestamp=datetime.now(),
                accuracy=0.45,  # Severe accuracy drop (>50% degradation)
                precision=0.42,
                recall=0.48,
                f1_score=0.45,
                auc_roc=0.52,
                inference_latency_p50=25000.0,  # 25 seconds - extremely slow
                inference_latency_p95=35000.0,
                inference_latency_p99=45000.0,
                throughput=5.0,           # Very low throughput
                error_rate=0.35,          # 35% error rate - critical
                data_drift_score=0.95,    # Maximum data drift
                concept_drift_score=0.92, # Maximum concept drift  
                prediction_drift_score=0.90, # Maximum prediction drift
                cpu_usage=95.0,
                memory_usage=95.0,
                gpu_utilization=98.0,
                data_quality_score=0.35,  # Very poor data quality
                missing_values_ratio=0.25,
                outlier_ratio=0.18,
                prediction_confidence=0.45,
                business_impact_score=9.8, # Maximum business impact
                environment="production",
                version="v1.0.0"
            )
            
            # Evaluate all metrics together for comprehensive system assessment
            result = await self.coordinator.evaluate_all_metrics(
                business_metrics=business_metrics,
                technical_metrics=technical_metrics,
                ai_metrics=[ai_metrics]
            )
            
            # Assert comprehensive system failure detection
            self.assertIn(result.system_health, [SystemHealthStatus.CRITICAL, SystemHealthStatus.EMERGENCY],
                         "System health should be critical/emergency with comprehensive failure")
            
            self.assertGreater(result.total_active_alerts, 8, 
                             "Should have many alerts in comprehensive crisis scenario")
            
            # Verify alerts span all categories
            categories_with_alerts = set()
            for alert in self.coordinator.alert_manager.active_alerts.values():
                categories_with_alerts.add(alert.category.value)
            
            self.assertGreaterEqual(len(categories_with_alerts), 2,
                                  "Should have alerts across multiple categories")
            
            # Verify system provides recommendations for such severe scenarios
            self.assertGreater(len(result.recommendations), 0,
                             "System should provide recommendations in crisis scenarios")
        
        asyncio.run(run_test())


if __name__ == '__main__':
    # Configure test environment
    import logging
    logging.getLogger().setLevel(logging.ERROR)  # Reduce log noise during tests
    
    # Run tests
    unittest.main(verbosity=2)