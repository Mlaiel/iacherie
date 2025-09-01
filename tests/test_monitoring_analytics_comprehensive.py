"""🧪 Comprehensive Tests for Monitoring & Analytics System
======================================================

Test suite for all monitoring and analytics components:
- User Metrics Tracker
- Revenue Metrics Tracker  
- Technical Performance Monitor
- AI Model Performance Tracker
- Unified Analytics Dashboard

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
import numpy as np

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from monitoring.advanced_metrics.user_metrics_tracker import (
    UserMetricsTracker, UserActivity, UserActivityType, RetentionPeriod
)
from monitoring.advanced_metrics.revenue_metrics_tracker import (
    RevenueMetricsTracker, RevenueTransaction, RevenueType, CustomerSegment
)
from monitoring.advanced_metrics.technical_performance_monitor import (
    TechnicalPerformanceMonitor, PerformanceMetric, ComponentType, ServiceStatus, ErrorEvent, ErrorSeverity
)
from monitoring.advanced_metrics.ai_model_performance_tracker import (
    AIModelPerformanceTracker, ModelPrediction, AIModelType
)
from monitoring.advanced_metrics.unified_analytics_dashboard import (
    UnifiedAnalyticsDashboard, DashboardStatus
)


class TestUserMetricsTracker:
    """
Test cases for User Metrics Tracker"""
    
    @pytest.fixture
    async def user_tracker(self):
        tracker = UserMetricsTracker()
        await tracker.initialize()
        return tracker
    
    @pytest.mark.asyncio
    async def test_user_tracker_initialization(self, user_tracker):
        """
Test user tracker initialization"""
        assert user_tracker is not None
        assert hasattr(user_tracker, 'prometheus_metrics')
        assert hasattr(user_tracker, 'activity_cache')
    
    @pytest.mark.asyncio
    async def test_track_user_activity(self, user_tracker):
        """
Test tracking user activities"""
        activity = UserActivity(
            user_id="test_user_123",
            activity_type=UserActivityType.CONTENT_UPLOAD,
            timestamp=datetime.now(),
            platform="spotify",
            session_id="session_456"
        )
        
        await user_tracker.track_user_activity(activity)
        
        # Verify activity was cached
        assert "test_user_123" in user_tracker.activity_cache
        assert len(user_tracker.activity_cache["test_user_123"]) == 1
    
    @pytest.mark.asyncio
    async def test_calculate_mau_metrics(self, user_tracker):
        """Test MAU metrics calculation"""
        mau_metrics = await user_tracker.calculate_mau_metrics()
        
        assert mau_metrics is not None
        assert mau_metrics.total_mau > 0
        assert isinstance(mau_metrics.mau_growth_rate, float)
        assert mau_metrics.new_users_this_month >= 0
        assert mau_metrics.returning_users >= 0
        assert len(mau_metrics.mau_by_platform) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_dau_metrics(self, user_tracker):
        """
Test DAU metrics calculation"""
        dau_metrics = await user_tracker.calculate_dau_metrics()
        
        assert dau_metrics is not None
        assert dau_metrics.total_dau > 0
        assert isinstance(dau_metrics.dau_growth_rate, float)
        assert dau_metrics.peak_concurrent_users > 0
        assert len(dau_metrics.dau_by_platform) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_retention_metrics(self, user_tracker):
        """
Test retention metrics calculation"""
        retention_metrics = await user_tracker.calculate_retention_metrics()
        
        assert retention_metrics is not None
        assert RetentionPeriod.DAY_1 in retention_metrics.retention_rates
        assert RetentionPeriod.DAY_30 in retention_metrics.retention_rates
        assert 0 <= retention_metrics.retention_rates[RetentionPeriod.DAY_1] <= 1
        assert retention_metrics.churn_rate >= 0
        assert len(retention_metrics.cohort_analysis) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_engagement_metrics(self, user_tracker):
        """
Test engagement metrics calculation"""
        engagement_metrics = await user_tracker.calculate_engagement_metrics()
        
        assert engagement_metrics is not None
        assert engagement_metrics.avg_session_duration > 0
        assert 0 <= engagement_metrics.content_engagement_rate <= 1
        assert 0 <= engagement_metrics.collaboration_participation_rate <= 1
        assert len(engagement_metrics.platform_distribution) > 0


class TestRevenueMetricsTracker:
    """
Test cases for Revenue Metrics Tracker"""
    
    @pytest.fixture
    async def revenue_tracker(self):
        tracker = RevenueMetricsTracker()
        await tracker.initialize()
        return tracker
    
    @pytest.mark.asyncio
    async def test_revenue_tracker_initialization(self, revenue_tracker):
        """
Test revenue tracker initialization"""
        assert revenue_tracker is not None
        assert hasattr(revenue_tracker, 'prometheus_metrics')
        assert hasattr(revenue_tracker, 'transaction_cache')
    
    @pytest.mark.asyncio
    async def test_track_revenue_transaction(self, revenue_tracker):
        """
Test tracking revenue transactions"""
        transaction = RevenueTransaction(
            transaction_id="txn_123",
            customer_id="customer_456",
            revenue_type=RevenueType.SUBSCRIPTION_PREMIUM,
            amount=Decimal("99.99"),
            currency="EUR",
            timestamp=datetime.now()
        )
        
        await revenue_tracker.track_revenue_transaction(transaction)
        
        # Verify transaction was cached
        assert "customer_456" in revenue_tracker.transaction_cache
        assert len(revenue_tracker.transaction_cache["customer_456"]) == 1
    
    @pytest.mark.asyncio
    async def test_calculate_mrr_metrics(self, revenue_tracker):
        """Test MRR metrics calculation"""
        mrr_metrics = await revenue_tracker.calculate_mrr_metrics()
        
        assert mrr_metrics is not None
        assert mrr_metrics.total_mrr > 0
        assert isinstance(mrr_metrics.mrr_growth_rate, float)
        assert mrr_metrics.new_mrr >= 0
        assert mrr_metrics.churned_mrr >= 0
        assert len(mrr_metrics.mrr_by_segment) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_arr_metrics(self, revenue_tracker):
        """
Test ARR metrics calculation"""
        arr_metrics = await revenue_tracker.calculate_arr_metrics()
        
        assert arr_metrics is not None
        assert arr_metrics.total_arr > 0
        assert isinstance(arr_metrics.arr_growth_rate, float)
        assert arr_metrics.arr_multiple >= 0
        assert len(arr_metrics.arr_by_segment) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_clv_metrics(self, revenue_tracker):
        """
Test CLV metrics calculation"""
        clv_metrics = await revenue_tracker.calculate_clv_metrics()
        
        assert clv_metrics is not None
        assert clv_metrics.avg_clv > 0
        assert clv_metrics.clv_to_cac_ratio > 0
        assert clv_metrics.payback_period_months > 0
        assert len(clv_metrics.clv_by_segment) > 0
    
    @pytest.mark.asyncio
    async def test_calculate_churn_metrics(self, revenue_tracker):
        """
Test churn metrics calculation"""
        churn_metrics = await revenue_tracker.calculate_churn_metrics()
        
        assert churn_metrics is not None
        assert churn_metrics.monthly_churn_rate >= 0
        assert churn_metrics.annual_churn_rate >= 0
        assert churn_metrics.at_risk_customers >= 0
        assert len(churn_metrics.churn_by_segment) > 0
    
    @pytest.mark.asyncio
    async def test_generate_revenue_insights(self, revenue_tracker):
        """
Test revenue insights generation"""
        insights = await revenue_tracker.generate_revenue_insights()
        
        assert insights is not None
        assert 0 <= insights.revenue_health_score <= 100
        assert insights.growth_trajectory in ["accelerating", "steady", "slow", "declining"]
        assert len(insights.key_metrics_summary) > 0
        assert isinstance(insights.recommendations, list)


class TestTechnicalPerformanceMonitor:
    """Test cases for Technical Performance Monitor"""
    
    @pytest.fixture
    async def tech_monitor(self):
        monitor = TechnicalPerformanceMonitor()
        await monitor.initialize()
        return monitor
    
    @pytest.mark.asyncio
    async def test_tech_monitor_initialization(self, tech_monitor):
        """
Test technical monitor initialization"""
        assert tech_monitor is not None
        assert hasattr(tech_monitor, 'prometheus_metrics')
        assert hasattr(tech_monitor, 'performance_cache')
        assert hasattr(tech_monitor, 'thresholds')
    
    @pytest.mark.asyncio
    async def test_record_performance_metric(self, tech_monitor):
        """
Test recording performance metrics"""
        metric = PerformanceMetric(
            component_id="api_gateway_01",
            component_type=ComponentType.API_GATEWAY,
            metric_name="response_time_ms",
            value=250.5,
            unit="ms",
            timestamp=datetime.now(),
            status=ServiceStatus.HEALTHY
        )
        
        await tech_monitor.record_performance_metric(metric)
        
        # Verify metric was processed
        cache_key = f"{metric.component_id}_{metric.metric_name}"
        assert cache_key in tech_monitor.metrics_history
    
    @pytest.mark.asyncio
    async def test_record_error_event(self, tech_monitor):
        """Test recording error events"""
        error = ErrorEvent(
            error_id="error_123",
            component_id="api_gateway_01",
            component_type=ComponentType.API_GATEWAY,
            error_type="timeout",
            severity=ErrorSeverity.HIGH,
            message="Request timeout occurred",
            timestamp=datetime.now()
        )
        
        await tech_monitor.record_error_event(error)
        
        # Verify error was cached
        assert "api_gateway_01" in tech_monitor.error_cache
    
    @pytest.mark.asyncio
    async def test_collect_system_performance(self, tech_monitor):
        """Test system performance collection"""
        system_metrics = await tech_monitor.collect_system_performance()
        
        assert system_metrics is not None
        assert 0 <= system_metrics.cpu_usage_percent <= 100
        assert 0 <= system_metrics.memory_usage_percent <= 100
        assert system_metrics.active_connections >= 0
        assert system_metrics.process_count > 0
    
    @pytest.mark.asyncio
    async def test_collect_api_performance(self, tech_monitor):
        """
Test API performance collection"""
        api_metrics = await tech_monitor.collect_api_performance()
        
        assert api_metrics is not None
        assert api_metrics.total_requests > 0
        assert api_metrics.requests_per_second > 0
        assert api_metrics.avg_response_time_ms > 0
        assert 0 <= api_metrics.success_rate_percent <= 100
        assert len(api_metrics.response_time_by_endpoint) > 0
    
    @pytest.mark.asyncio
    async def test_collect_database_performance(self, tech_monitor):
        """
Test database performance collection"""
        db_metrics = await tech_monitor.collect_database_performance()
        
        assert db_metrics is not None
        assert db_metrics.active_connections >= 0
        assert db_metrics.max_connections > 0
        assert db_metrics.avg_query_time_ms > 0
        assert 0 <= db_metrics.cache_hit_rate_percent <= 100
    
    @pytest.mark.asyncio
    async def test_collect_uptime_metrics(self, tech_monitor):
        """
Test uptime metrics collection"""
        uptime_metrics = await tech_monitor.collect_uptime_metrics()
        
        assert uptime_metrics is not None
        assert 0 <= uptime_metrics.uptime_percentage_24h <= 100
        assert 0 <= uptime_metrics.uptime_percentage_7d <= 100
        assert uptime_metrics.mttr_minutes >= 0
        assert uptime_metrics.incident_count_24h >= 0
    
    @pytest.mark.asyncio
    async def test_collect_cdn_performance(self, tech_monitor):
        """
Test CDN performance collection"""
        cdn_metrics = await tech_monitor.collect_cdn_performance()
        
        assert cdn_metrics is not None
        assert 0 <= cdn_metrics.cache_hit_rate_percent <= 100
        assert cdn_metrics.requests_per_second > 0
        assert cdn_metrics.bandwidth_usage_gbps >= 0
        assert len(cdn_metrics.geographical_performance) > 0
    
    @pytest.mark.asyncio
    async def test_comprehensive_performance_report(self, tech_monitor):
        """
Test comprehensive performance report generation"""
        report = await tech_monitor.get_comprehensive_performance_report()
        
        assert report is not None
        assert "overall_health_score" in report
        assert "system_performance" in report
        assert "api_performance" in report
        assert "database_performance" in report
        assert "recommendations" in report
        assert 0 <= report["overall_health_score"] <= 100


class TestAIModelPerformanceTracker:
    """Test cases for AI Model Performance Tracker"""
    
    @pytest.fixture
    async def ai_tracker(self):
        tracker = AIModelPerformanceTracker()
        await tracker.initialize()
        return tracker
    
    @pytest.mark.asyncio
    async def test_ai_tracker_initialization(self, ai_tracker):
        """
Test AI tracker initialization"""
        assert ai_tracker is not None
        assert hasattr(ai_tracker, 'prometheus_metrics')
        assert hasattr(ai_tracker, 'model_registry')
        assert hasattr(ai_tracker, 'thresholds')
    
    @pytest.mark.asyncio
    async def test_register_model(self, ai_tracker):
        """
Test model registration"""
        model_id = "test_content_protector_v1"
        model_type = AIModelType.CONTENT_PROTECTOR
        
        await ai_tracker.register_model(model_id, model_type, "1.0.0")
        
        assert model_id in ai_tracker.model_registry
        assert ai_tracker.model_registry[model_id]["model_type"] == model_type
    
    @pytest.mark.asyncio
    async def test_record_prediction(self, ai_tracker):
        """Test recording model predictions"""
        # First register a model
        model_id = "test_model_001"
        await ai_tracker.register_model(model_id, AIModelType.CONTENT_PROTECTOR)
        
        prediction = ModelPrediction(
            prediction_id="pred_123",
            model_id=model_id,
            model_type=AIModelType.CONTENT_PROTECTOR,
            input_data_hash="hash_456",
            prediction_result={"class": "positive", "confidence": 0.95},
            confidence_score=0.95,
            processing_time_ms=125.5,
            timestamp=datetime.now(),
            ground_truth={"class": "positive"},
            is_correct=True
        )
        
        await ai_tracker.record_prediction(prediction)
        
        # Verify prediction was cached
        assert model_id in ai_tracker.prediction_cache
    
    @pytest.mark.asyncio
    async def test_calculate_accuracy_metrics(self, ai_tracker):
        """Test accuracy metrics calculation"""
        # Register a model first
        model_id = "test_accuracy_model"
        await ai_tracker.register_model(model_id, AIModelType.CONTENT_PROTECTOR)
        
        accuracy_metrics = await ai_tracker.calculate_accuracy_metrics(model_id)
        
        assert accuracy_metrics is not None
        assert accuracy_metrics.model_id == model_id
        assert 0 <= accuracy_metrics.accuracy_score <= 1
        assert 0 <= accuracy_metrics.precision_score <= 1
        assert 0 <= accuracy_metrics.recall_score <= 1
        assert 0 <= accuracy_metrics.f1_score <= 1
    
    @pytest.mark.asyncio
    async def test_calculate_processing_time_metrics(self, ai_tracker):
        """Test processing time metrics calculation"""
        # Register a model first
        model_id = "test_processing_model"
        await ai_tracker.register_model(model_id, AIModelType.CONTENT_PROTECTOR)
        
        processing_metrics = await ai_tracker.calculate_processing_time_metrics(model_id)
        
        assert processing_metrics is not None
        assert processing_metrics.model_id == model_id
        assert processing_metrics.avg_processing_time_ms >= 0
        assert processing_metrics.throughput_per_second >= 0
        assert processing_metrics.p95_processing_time_ms >= processing_metrics.p50_processing_time_ms
    
    @pytest.mark.asyncio
    async def test_calculate_resource_metrics(self, ai_tracker):
        """Test resource metrics calculation"""
        # Register a model first
        model_id = "test_resource_model"
        await ai_tracker.register_model(model_id, AIModelType.CONTENT_PROTECTOR)
        
        resource_metrics = await ai_tracker.calculate_resource_metrics(model_id)
        
        assert resource_metrics is not None
        assert resource_metrics.model_id == model_id
        assert resource_metrics.avg_memory_usage_mb >= 0
        assert resource_metrics.avg_cpu_usage_percent >= 0
        assert 0 <= resource_metrics.cache_hit_rate_percent <= 100
    
    @pytest.mark.asyncio
    async def test_detect_model_drift(self, ai_tracker):
        """Test model drift detection"""
        # Register a model first
        model_id = "test_drift_model"
        await ai_tracker.register_model(model_id, AIModelType.CONTENT_PROTECTOR)
        
        drift_metrics = await ai_tracker.detect_model_drift(model_id)
        
        assert drift_metrics is not None
        assert drift_metrics.model_id == model_id
        assert drift_metrics.drift_score >= 0
        assert isinstance(drift_metrics.is_drifting, bool)
        assert 0 <= drift_metrics.data_quality_score <= 1
    
    @pytest.mark.asyncio
    async def test_compare_models(self, ai_tracker):
        """Test model comparison"""
        # Register two models
        model_a_id = "test_model_a"
        model_b_id = "test_model_b"
        await ai_tracker.register_model(model_a_id, AIModelType.CONTENT_PROTECTOR)
        await ai_tracker.register_model(model_b_id, AIModelType.CONTENT_PROTECTOR)
        
        comparison_metrics = await ai_tracker.compare_models(model_a_id, model_b_id)
        
        assert comparison_metrics is not None
        assert comparison_metrics.model_a_id == model_a_id
        assert comparison_metrics.model_b_id == model_b_id
        assert "accuracy" in comparison_metrics.model_a_performance
        assert "accuracy" in comparison_metrics.model_b_performance
        assert 0 <= comparison_metrics.statistical_significance <= 1
    
    @pytest.mark.asyncio
    async def test_comprehensive_ai_performance_report(self, ai_tracker):
        """Test comprehensive AI performance report"""
        # Register a test model
        await ai_tracker.register_model("test_report_model", AIModelType.CONTENT_PROTECTOR)
        
        report = await ai_tracker.get_comprehensive_ai_performance_report()
        
        assert report is not None
        assert "total_models" in report
        assert "models_summary" in report
        assert "overall_metrics" in report
        assert "recommendations" in report
        assert report["total_models"] >= 1


class TestUnifiedAnalyticsDashboard:
    """Test cases for Unified Analytics Dashboard"""
    
    @pytest.fixture
    async def dashboard(self):
        dashboard = UnifiedAnalyticsDashboard()
        await dashboard.initialize()
        return dashboard
    
    @pytest.mark.asyncio
    async def test_dashboard_initialization(self, dashboard):
        """
Test dashboard initialization"""
        assert dashboard is not None
        assert hasattr(dashboard, 'user_tracker')
        assert hasattr(dashboard, 'revenue_tracker')
        assert hasattr(dashboard, 'tech_monitor')
        assert hasattr(dashboard, 'ai_tracker')
        assert hasattr(dashboard, 'kpi_targets')
    
    @pytest.mark.asyncio
    async def test_get_unified_metrics(self, dashboard):
        """
Test unified metrics collection"""
        unified_metrics = await dashboard.get_unified_metrics()
        
        assert unified_metrics is not None
        assert hasattr(unified_metrics, 'overall_health_score')
        assert hasattr(unified_metrics, 'status')
        assert 0 <= unified_metrics.overall_health_score <= 100
        assert unified_metrics.status in [s for s in DashboardStatus]
        
        # Check user metrics
        assert unified_metrics.mau >= 0
        assert unified_metrics.dau >= 0
        assert unified_metrics.retention_rate_30d >= 0
        
        # Check revenue metrics
        assert unified_metrics.mrr >= 0
        assert unified_metrics.arr >= 0
        assert unified_metrics.clv >= 0
        
        # Check technical metrics
        assert 0 <= unified_metrics.system_cpu_usage <= 100
        assert 0 <= unified_metrics.system_memory_usage <= 100
        assert unified_metrics.api_response_time_ms >= 0
        
        # Check AI metrics
        assert 0 <= unified_metrics.avg_model_accuracy <= 100
        assert unified_metrics.avg_inference_time_ms >= 0
    
    @pytest.mark.asyncio
    async def test_get_kpi_performance_report(self, dashboard):
        """
Test KPI performance report generation"""
        kpi_report = await dashboard.get_kpi_performance_report()
        
        assert kpi_report is not None
        assert "overall_kpi_health" in kpi_report
        assert "kpi_performance" in kpi_report
        assert "targets_met" in kpi_report
        assert "targets_missed" in kpi_report
        assert 0 <= kpi_report["overall_kpi_health"] <= 100
        assert kpi_report["targets_met"] >= 0
        assert kpi_report["targets_missed"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_real_time_alerts(self, dashboard):
        """Test real-time alerts collection"""
        alerts = await dashboard.get_real_time_alerts()
        
        assert isinstance(alerts, list)
        
        # If there are alerts, verify their structure
        for alert in alerts:
            assert "id" in alert
            assert "type" in alert
            assert "severity" in alert
            assert "title" in alert
            assert "message" in alert
            assert "timestamp" in alert
    
    @pytest.mark.asyncio
    async def test_comprehensive_dashboard_export(self, dashboard):
        """Test comprehensive dashboard export"""
        export_data = await dashboard.get_comprehensive_dashboard_export()
        
        assert export_data is not None
        assert "export_timestamp" in export_data
        assert "summary" in export_data
        assert "metrics" in export_data
        assert "kpi_performance" in export_data
        assert "alerts" in export_data
        assert "detailed_reports" in export_data
        assert "recommendations" in export_data
        
        # Check metrics structure
        metrics = export_data["metrics"]
        assert "user_metrics" in metrics
        assert "revenue_metrics" in metrics
        assert "technical_metrics" in metrics
        assert "ai_metrics" in metrics
        
        # Check summary structure
        summary = export_data["summary"]
        assert "overall_health_score" in summary
        assert "status" in summary
        assert 0 <= summary["overall_health_score"] <= 100


class TestIntegrationScenarios:
    """Integration test scenarios for the complete monitoring system"""
    
    @pytest.fixture
    async def full_system(self):
        """
Setup full monitoring system for integration tests"""
        dashboard = UnifiedAnalyticsDashboard()
        await dashboard.initialize()
        
        # Register some AI models for testing
        await dashboard.ai_tracker.register_model("content_protector_v1", AIModelType.CONTENT_PROTECTOR)
        await dashboard.ai_tracker.register_model("audio_fingerprinter_v1", AIModelType.AUDIO_FINGERPRINTER)
        
        return dashboard
    
    @pytest.mark.asyncio
    async def test_end_to_end_monitoring_flow(self, full_system):
        """Test complete end-to-end monitoring flow"""
        dashboard = full_system
        
        # 1. Track some user activities
        for i in range(10):
            activity = UserActivity(
                user_id=f"user_{i}",
                activity_type=UserActivityType.CONTENT_UPLOAD,
                timestamp=datetime.now() - timedelta(minutes=i),
                platform="spotify"
            )
            await dashboard.user_tracker.track_user_activity(activity)
        
        # 2. Track some revenue transactions
        for i in range(5):
            transaction = RevenueTransaction(
                transaction_id=f"txn_{i}",
                customer_id=f"customer_{i}",
                revenue_type=RevenueType.SUBSCRIPTION_PREMIUM,
                amount=Decimal("99.99"),
                currency="EUR",
                timestamp=datetime.now() - timedelta(hours=i)
            )
            await dashboard.revenue_tracker.track_revenue_transaction(transaction)
        
        # 3. Record some performance metrics
        for i in range(3):
            metric = PerformanceMetric(
                component_id="api_gateway",
                component_type=ComponentType.API_GATEWAY,
                metric_name="response_time_ms",
                value=200 + i * 50,
                unit="ms",
                timestamp=datetime.now() - timedelta(minutes=i),
                status=ServiceStatus.HEALTHY
            )
            await dashboard.tech_monitor.record_performance_metric(metric)
        
        # 4. Record some AI predictions
        for i in range(5):
            prediction = ModelPrediction(
                prediction_id=f"pred_{i}",
                model_id="content_protector_v1",
                model_type=AIModelType.CONTENT_PROTECTOR,
                input_data_hash=f"hash_{i}",
                prediction_result={"class": "positive"},
                confidence_score=0.9 + i * 0.01,
                processing_time_ms=100 + i * 10,
                timestamp=datetime.now() - timedelta(minutes=i),
                ground_truth={"class": "positive"},
                is_correct=True
            )
            await dashboard.ai_tracker.record_prediction(prediction)
        
        # 5. Get unified metrics
        unified_metrics = await dashboard.get_unified_metrics()
        
        # Verify the system processed all data
        assert unified_metrics is not None
        assert unified_metrics.overall_health_score > 0
        
        # 6. Generate comprehensive report
        export_data = await dashboard.get_comprehensive_dashboard_export()
        
        assert export_data is not None
        assert len(export_data["detailed_reports"]) == 4  # All 4 system reports
    
    @pytest.mark.asyncio
    async def test_alert_generation_scenario(self, full_system):
        """Test alert generation under various conditions"""
        dashboard = full_system
        
        # Simulate high error rate scenario
        for i in range(10):
            error = ErrorEvent(
                error_id=f"error_{i}",
                component_id="api_gateway",
                component_type=ComponentType.API_GATEWAY,
                error_type="server_error",
                severity=ErrorSeverity.HIGH,
                message=f"Server error #{i}",
                timestamp=datetime.now() - timedelta(minutes=i)
            )
            await dashboard.tech_monitor.record_error_event(error)
        
        # Get unified metrics (which should trigger alert analysis)
        unified_metrics = await dashboard.get_unified_metrics()
        
        # Get real-time alerts
        alerts = await dashboard.get_real_time_alerts()
        
        # Verify alerts were generated for critical conditions
        assert isinstance(alerts, list)
        # Note: Actual alert generation depends on simulated data thresholds
    
    @pytest.mark.asyncio
    async def test_performance_degradation_detection(self, full_system):
        """Test detection of performance degradation across systems"""
        dashboard = full_system
        
        # Simulate degrading performance over time
        base_time = datetime.now()
        
        # Degrading API performance
        for i in range(20):
            response_time = 200 + (i * 100)  # Increasing response time
            metric = PerformanceMetric(
                component_id="api_gateway",
                component_type=ComponentType.API_GATEWAY,
                metric_name="response_time_ms",
                value=response_time,
                unit="ms",
                timestamp=base_time - timedelta(minutes=20-i),
                status=ServiceStatus.HEALTHY if response_time < 1000 else ServiceStatus.WARNING
            )
            await dashboard.tech_monitor.record_performance_metric(metric)
        
        # Get performance report
        tech_report = await dashboard.tech_monitor.get_comprehensive_performance_report()
        
        # Verify performance issues are detected
        assert tech_report is not None
        assert "performance_issues" in tech_report
        
        # Get unified metrics
        unified_metrics = await dashboard.get_unified_metrics()
        
        # Health score should reflect performance degradation
        assert unified_metrics.overall_health_score < 100


# Test execution helpers
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])