"""Tests for Industrialization Success Metrics System
===================================================

Comprehensive tests for the industrialization success metrics implementation.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import unittest
import asyncio
import sys
import os
from unittest.mock import patch, AsyncMock

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from monitoring.industrialization_success_metrics import (
    IndustrializationSuccessMetrics, 
    IndustrializationKPI, 
    KPIType
)
from monitoring.industrialization_dashboard import IndustrializationDashboard
from monitoring.industrialization_metrics_integration import IndustrializationMetricsIntegration


class TestIndustrializationSuccessMetrics(unittest.TestCase):
    """Test the core metrics system"""
    
    def setUp(self):
        """Set up test environment"""
        self.metrics = IndustrializationSuccessMetrics()
    
    def test_kpi_initialization(self):
        """Test that all required KPIs are initialized"""
        # Technical KPIs
        technical_kpis = [
            "uptime_sla", "response_time_api", "error_rate", "mttr",
            "deployment_frequency", "security_score", "code_coverage", "technical_debt_ratio"
        ]
        
        for kpi_name in technical_kpis:
            self.assertIn(kpi_name, self.metrics.kpis)
            self.assertEqual(self.metrics.kpis[kpi_name].kpi_type, KPIType.TECHNICAL)
        
        # Business KPIs
        business_kpis = [
            "time_to_market", "customer_satisfaction", "cost_per_transaction",
            "revenue_growth", "user_retention", "support_ticket_volume"
        ]
        
        for kpi_name in business_kpis:
            self.assertIn(kpi_name, self.metrics.kpis)
            self.assertEqual(self.metrics.kpis[kpi_name].kpi_type, KPIType.BUSINESS)
    
    def test_kpi_objectives(self):
        """Test that KPI objectives match problem statement requirements"""
        expected_objectives = {
            "uptime_sla": "99.9%",
            "response_time_api": "<200ms P95",
            "error_rate": "<0.1%",
            "mttr": "<15 minutes",
            "deployment_frequency": ">10/jour",
            "security_score": "A+ (95%+)",
            "code_coverage": ">90%",
            "technical_debt_ratio": "<5%",
            "time_to_market": "<1 jour",
            "customer_satisfaction": ">4.5/5",
            "cost_per_transaction": "<€0.10",
            "revenue_growth": "+20% MoM",
            "user_retention": ">85%",
            "support_ticket_volume": "<100/jour"
        }
        
        for kpi_name, expected_objective in expected_objectives.items():
            self.assertEqual(self.metrics.kpis[kpi_name].objective, expected_objective)
    
    async def test_kpi_update(self):
        """Test KPI value updates"""
        # Test updating a technical KPI
        result = await self.metrics.update_kpi_value("uptime_sla", 99.95)
        self.assertTrue(result)
        self.assertEqual(self.metrics.kpis["uptime_sla"].current_value, 99.95)
        
        # Test updating a business KPI
        result = await self.metrics.update_kpi_value("customer_satisfaction", 4.7)
        self.assertTrue(result)
        self.assertEqual(self.metrics.kpis["customer_satisfaction"].current_value, 4.7)
        
        # Test invalid KPI
        result = await self.metrics.update_kpi_value("invalid_kpi", 100.0)
        self.assertFalse(result)
    
    async def test_kpi_alerts(self):
        """Test KPI alerting system"""
        # Set a value that should trigger an alert
        await self.metrics.update_kpi_value("uptime_sla", 98.0)  # Below 99.9% target
        
        alerts = await self.metrics.check_kpi_alerts()
        uptime_alerts = [a for a in alerts if a["kpi_name"] == "uptime_sla"]
        self.assertTrue(len(uptime_alerts) > 0)
        self.assertEqual(uptime_alerts[0]["severity"], "critical")
    
    async def test_kpi_summary(self):
        """Test KPI summary generation"""
        # Update some KPIs
        await self.metrics.update_kpi_value("uptime_sla", 99.95)
        await self.metrics.update_kpi_value("customer_satisfaction", 4.6)
        
        summary = await self.metrics.get_kpi_summary()
        
        self.assertIn("technical_kpis_stats", summary)
        self.assertIn("business_kpis_stats", summary)
        self.assertIn("overall_industrialization_score", summary)
        self.assertIsInstance(summary["overall_industrialization_score"], float)


class TestIndustrializationDashboard(unittest.TestCase):
    """Test the dashboard system"""
    
    def setUp(self):
        """Set up test environment"""
        self.dashboard = IndustrializationDashboard()
    
    async def test_dashboard_data_generation(self):
        """Test dashboard data generation"""
        # Update some metrics first
        await self.dashboard.metrics.update_kpi_value("uptime_sla", 99.95)
        await self.dashboard.metrics.update_kpi_value("response_time_api", 150.0)
        
        dashboard_data = await self.dashboard.get_dashboard_data()
        
        self.assertIn("title", dashboard_data)
        self.assertIn("sections", dashboard_data)
        self.assertIn("technical", dashboard_data["sections"])
        self.assertIn("business", dashboard_data["sections"])
        self.assertEqual(dashboard_data["title"], "📊 MÉTRIQUES DE SUCCÈS INDUSTRIALISATION")
    
    async def test_html_dashboard_generation(self):
        """Test HTML dashboard generation"""
        html = await self.dashboard.generate_html_dashboard()
        
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("MÉTRIQUES DE SUCCÈS INDUSTRIALISATION", html)
        self.assertIn("KPIs TECHNIQUES", html)
        self.assertIn("KPIs BUSINESS", html)
        self.assertTrue(len(html) > 1000)  # Should be substantial HTML


class TestIndustrializationMetricsIntegration(unittest.TestCase):
    """Test the integration system"""
    
    def setUp(self):
        """Set up test environment"""
        self.integration = IndustrializationMetricsIntegration()
    
    async def test_metrics_collection(self):
        """Test metrics collection from simulated sources"""
        await self.integration.collect_and_update_metrics()
        
        # Check that technical KPIs were updated
        technical_kpis = await self.integration.metrics.get_technical_kpis()
        self.assertGreater(len(technical_kpis), 0)
        
        # Check that business KPIs were updated
        business_kpis = await self.integration.metrics.get_business_kpis()
        self.assertGreater(len(business_kpis), 0)
    
    async def test_full_report_generation(self):
        """Test full report generation"""
        report = await self.integration.generate_full_report()
        
        self.assertIn("report_type", report)
        self.assertIn("technical_kpis", report)
        self.assertIn("business_kpis", report)
        self.assertIn("summary", report)
        self.assertIn("integration_info", report)
        self.assertEqual(report["report_type"], "Industrialization Success Metrics")
    
    async def test_status_summary(self):
        """Test KPI status summary"""
        summary = await self.integration.get_kpi_status_summary()
        
        self.assertIn("overall_score", summary)
        self.assertIn("technical_score", summary)
        self.assertIn("business_score", summary)
        self.assertIn("total_kpis", summary)
        self.assertIn("kpis_on_target", summary)
        self.assertIsInstance(summary["overall_score"], float)


class TestEndToEndFunctionality(unittest.TestCase):
    """End-to-end tests for the complete system"""
    
    def setUp(self):
        """Set up test environment"""
        self.integration = IndustrializationMetricsIntegration()
    
    async def test_complete_workflow(self):
        """Test the complete metrics workflow"""
        # 1. Collect metrics
        await self.integration.collect_and_update_metrics()
        
        # 2. Generate dashboard
        dashboard_data = await self.integration.dashboard.get_dashboard_data()
        self.assertIsInstance(dashboard_data, dict)
        
        # 3. Generate HTML dashboard
        html = await self.integration.dashboard.generate_html_dashboard()
        self.assertIn("<!DOCTYPE html>", html)
        
        # 4. Generate full report
        report = await self.integration.generate_full_report()
        self.assertIn("report_type", report)
        
        # 5. Check status summary
        summary = await self.integration.get_kpi_status_summary()
        self.assertIn("overall_score", summary)
    
    async def test_metrics_format_compliance(self):
        """Test that metrics match the exact format from problem statement"""
        # Export metrics table
        metrics_table = await self.integration.dashboard.export_metrics_table()
        
        # Should contain the exact headings from problem statement
        self.assertIn("📊 MÉTRIQUES DE SUCCÈS INDUSTRIALISATION", metrics_table)
        self.assertIn("🎯 KPIs TECHNIQUES", metrics_table)
        self.assertIn("💼 KPIs BUSINESS", metrics_table)
        self.assertIn("Métrique\tObjectif\tMesure", metrics_table)
        
        # Should contain all required metrics
        required_technical = ["Uptime SLA", "Response Time API", "Error Rate", 
                            "MTTR (Mean Time to Repair)", "Deployment Frequency",
                            "Security Score", "Code Coverage", "Technical Debt Ratio"]
        
        required_business = ["Time to Market", "Customer Satisfaction", 
                           "Cost per Transaction", "Revenue Growth", 
                           "User Retention", "Support Ticket Volume"]
        
        for metric in required_technical + required_business:
            self.assertIn(metric, metrics_table)


async def run_async_test(test_method):
    """Helper to run async test methods"""
    await test_method()


def suite():
    """Create test suite"""
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(TestIndustrializationSuccessMetrics('test_kpi_initialization'))
    suite.addTest(TestIndustrializationSuccessMetrics('test_kpi_objectives'))
    
    return suite


if __name__ == '__main__':
    # Run async tests
    async def run_all_tests():
        print("🧪 Running Industrialization Metrics Tests...")
        print("=" * 50)
        
        # Test 1: KPI Initialization
        print("Testing KPI initialization...")
        test_metrics = TestIndustrializationSuccessMetrics()
        test_metrics.setUp()
        test_metrics.test_kpi_initialization()
        test_metrics.test_kpi_objectives()
        print("✅ KPI initialization tests passed")
        
        # Test 2: KPI Updates
        print("Testing KPI updates...")
        await test_metrics.test_kpi_update()
        await test_metrics.test_kpi_alerts()
        await test_metrics.test_kpi_summary()
        print("✅ KPI update tests passed")
        
        # Test 3: Dashboard
        print("Testing dashboard generation...")
        test_dashboard = TestIndustrializationDashboard()
        test_dashboard.setUp()
        await test_dashboard.test_dashboard_data_generation()
        await test_dashboard.test_html_dashboard_generation()
        print("✅ Dashboard tests passed")
        
        # Test 4: Integration
        print("Testing integration system...")
        test_integration = TestIndustrializationMetricsIntegration()
        test_integration.setUp()
        await test_integration.test_metrics_collection()
        await test_integration.test_full_report_generation()
        await test_integration.test_status_summary()
        print("✅ Integration tests passed")
        
        # Test 5: End-to-end
        print("Testing end-to-end functionality...")
        test_e2e = TestEndToEndFunctionality()
        test_e2e.setUp()
        await test_e2e.test_complete_workflow()
        await test_e2e.test_metrics_format_compliance()
        print("✅ End-to-end tests passed")
        
        print("=" * 50)
        print("🎉 All tests passed successfully!")
    
    # Run the tests
    asyncio.run(run_all_tests())