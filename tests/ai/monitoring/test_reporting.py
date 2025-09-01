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
Advanced Reporting Tests - Industrial Grade

Comprehensive, enterprise-level test suite for monitoring reporting system.
Tests report generation, data visualization, analytics, and business intelligence.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

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
import pandas as pd
import numpy as np
from decimal import Decimal

from ai.monitoring.reporting import (
    Reporting,
    ReportType,
    ReportFormat,
    ReportFrequency,
    Report,
    ReportGenerator,
    DataAggregator,
    MetricsAnalyzer,
    ChartGenerator,
    DashboardBuilder,
    BusinessIntelligence,
    ReportScheduler,
    ExportManager
)
from ai.core.metrics import MetricType, MetricPriority
from ai.core.exceptions import ReportingError, DataProcessingError
from .fixtures import (
    reporting_configs,
    metric_datasets,
    report_templates,
    visualization_configs,
    business_metrics
)


class TestReportingCore:
    """
Core functionality tests for reporting system."""
    
    @pytest.fixture
    async def reporting_system(self):
        """
Create and initialize reporting system."""
        system = Reporting(
            config={
                "report_generation_enabled": True,
                "data_aggregation_enabled": True,
                "visualization_enabled": True,
                "export_enabled": True,
                "scheduling_enabled": True,
                "business_intelligence_enabled": True,
                "data_retention_days": 365,
                "export_formats": ["pdf", "excel", "json", "csv"],
                "chart_libraries": ["plotly", "matplotlib", "chartjs"]
            }
        )
        await system.initialize()
        yield engine
        await engine.shutdown()
    
    @pytest.fixture
    def report_test_config(self):
        """Reporting system configuration for testing."""
        return {
            "data_sources": {
                "performance_metrics": {
                    "type": "database",
                    "connection": "postgresql://test:test@localhost/metrics",
                    "tables": ["ai_performance", "system_metrics", "user_metrics"]
                },
                "business_metrics": {
                    "type": "api",
                    "endpoint": "https://api.test.com/business-metrics",
                    "authentication": {"type": "bearer", "token": "test_token"}
                },
                "alert_logs": {
                    "type": "file",
                    "path": "/var/log/alerts",
                    "format": "json"
                }
            },
            "report_templates": [
                {
                    "name": "daily_performance_summary",
                    "type": ReportType.PERFORMANCE,
                    "schedule": {"frequency": "daily", "time": "09:00"},
                    "metrics": [
                        "cpu_usage", "memory_usage", "response_time",
                        "throughput", "error_rate"
                    ],
                    "visualizations": ["line_chart", "heatmap", "gauge"],
                    "recipients": ["ops@test.com", "dev@test.com"]
                },
                {
                    "name": "weekly_business_report",
                    "type": ReportType.BUSINESS,
                    "schedule": {"frequency": "weekly", "day": "monday", "time": "08:00"},
                    "metrics": [
                        "revenue", "user_acquisition", "retention_rate",
                        "conversion_rate", "churn_rate"
                    ],
                    "visualizations": ["bar_chart", "pie_chart", "trend_line"],
                    "recipients": ["business@test.com", "management@test.com"]
                },
                {
                    "name": "monthly_ai_analytics",
                    "type": ReportType.AI_ANALYTICS,
                    "schedule": {"frequency": "monthly", "day": 1, "time": "10:00"},
                    "metrics": [
                        "model_accuracy", "inference_latency", "training_metrics",
                        "data_quality", "model_drift"
                    ],
                    "visualizations": ["scatter_plot", "box_plot", "correlation_matrix"],
                    "recipients": ["ai-team@test.com", "data-science@test.com"]
                }
            ],
            "visualization_config": {
                "theme": "professional",
                "color_palette": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
                "font_family": "Arial",
                "dpi": 300,
                "figure_size": [12, 8]
            },
            "output_formats": ["pdf", "html", "excel", "json"],
            "storage_config": {
                "local_path": "/tmp/reports",
                "cloud_storage": {
                    "provider": "s3",
                    "bucket": "test-reports-bucket",
                    "region": "us-east-1"
                }
            }
        }
    
    async def test_reporting_engine_initialization(self, reporting_engine):
        """Test proper initialization of reporting engine."""
        assert reporting_engine is not None
        assert reporting_engine.is_initialized
        assert reporting_engine.data_aggregator is not None
        assert reporting_engine.visualization_engine is not None
        assert reporting_engine.template_manager is not None
        assert reporting_engine.scheduler is not None
    
    async def test_data_aggregation_and_collection(self, reporting_engine, report_test_config):
        """
Test data aggregation from multiple sources."""
        # Configure data sources
        await reporting_engine.configure_data_sources(report_test_config["data_sources"])
        
        # Mock data from different sources
        performance_data = TestDataGenerator.generate_performance_metrics(
            duration=timedelta(days=7),
            interval=timedelta(hours=1)
        )
        
        business_data = TestDataGenerator.generate_business_metrics(
            duration=timedelta(days=30),
            interval=timedelta(days=1)
        )
        
        alert_data = TestDataGenerator.generate_alert_scenarios()
        
        # Test performance data aggregation
        aggregated_performance = await reporting_engine.aggregate_data(
            source="performance_metrics",
            time_range=timedelta(days=7),
            aggregation_functions=["mean", "max", "min", "percentile_95"],
            group_by=["hour", "day"]
        )
        
        assert aggregated_performance is not None
        assert "cpu_usage" in aggregated_performance
        assert "memory_usage" in aggregated_performance
        assert "response_time" in aggregated_performance
        
        # Verify aggregation statistics
        cpu_stats = aggregated_performance["cpu_usage"]
        assert "mean" in cpu_stats
        assert "max" in cpu_stats
        assert "min" in cpu_stats
        assert "percentile_95" in cpu_stats
        
        # Test business data aggregation
        aggregated_business = await reporting_engine.aggregate_data(
            source="business_metrics",
            time_range=timedelta(days=30),
            aggregation_functions=["sum", "mean", "count"],
            group_by=["day", "week"]
        )
        
        assert aggregated_business is not None
        assert "revenue" in aggregated_business
        assert "user_acquisition" in aggregated_business
        assert "conversion_rate" in aggregated_business
        
        # Test data quality validation
        data_quality = await reporting_engine.validate_data_quality(
            data=aggregated_performance,
            validation_rules={
                "completeness": {"threshold": 0.95},
                "accuracy": {"threshold": 0.99},
                "consistency": {"threshold": 0.98}
            }
        )
        
        assert data_quality["completeness"] >= 0.95
        assert data_quality["accuracy"] >= 0.99
        assert data_quality["overall_score"] >= 0.95
        
        # Test real-time data streaming
        streaming_data = []
        
        async def data_callback(data_batch):
            streaming_data.append(data_batch)
        
        await reporting_engine.start_real_time_aggregation(
            source="performance_metrics",
            callback=data_callback,
            batch_size=100,
            interval=timedelta(seconds=30)
        )
        
        # Simulate real-time data flow
        for i in range(10):
            await reporting_engine.ingest_real_time_data({
                "timestamp": datetime.utcnow(),
                "cpu_usage": 50 + i * 2,
                "memory_usage": 60 + i * 1.5,
                "response_time": 200 + i * 10
            })
            await asyncio.sleep(0.01)
        
        # Wait for batch processing
        await asyncio.sleep(0.1)
        
        # Verify streaming data collection
        assert len(streaming_data) > 0
        
        await reporting_engine.stop_real_time_aggregation()
    
    async def test_report_template_management(self, reporting_engine, report_test_config):
        """Test report template creation and management."""
        # Create report templates
        for template_config in report_test_config["report_templates"]:
            template = ReportTemplate(
                name=template_config["name"],
                report_type=template_config["type"],
                metrics=template_config["metrics"],
                visualizations=template_config["visualizations"],
                schedule=ReportSchedule(**template_config["schedule"]),
                recipients=template_config["recipients"]
            )
            
            await reporting_engine.add_report_template(template)
        
        # Verify templates were added
        templates = await reporting_engine.get_report_templates()
        assert len(templates) == 3
        
        template_names = [t.name for t in templates]
        assert "daily_performance_summary" in template_names
        assert "weekly_business_report" in template_names
        assert "monthly_ai_analytics" in template_names
        
        # Test template validation
        valid_template = ReportTemplate(
            name="test_valid_template",
            report_type=ReportType.PERFORMANCE,
            metrics=["cpu_usage", "memory_usage"],
            visualizations=["line_chart"],
            schedule=ReportSchedule(frequency="daily", time="09:00"),
            recipients=["test@example.com"]
        )
        
        validation_result = await reporting_engine.validate_template(valid_template)
        assert validation_result["valid"] == True
        
        # Test invalid template
        invalid_template = ReportTemplate(
            name="test_invalid_template",
            report_type=ReportType.PERFORMANCE,
            metrics=[],  # No metrics
            visualizations=["invalid_chart_type"],  # Invalid visualization
            schedule=ReportSchedule(frequency="invalid"),  # Invalid frequency
            recipients=[]  # No recipients
        )
        
        validation_result = await reporting_engine.validate_template(invalid_template)
        assert validation_result["valid"] == False
        assert len(validation_result["errors"]) > 0
        
        # Test template customization
        customized_template = await reporting_engine.customize_template(
            base_template="daily_performance_summary",
            customizations={
                "metrics": ["cpu_usage", "memory_usage", "disk_usage"],
                "visualizations": ["line_chart", "gauge"],
                "schedule": {"frequency": "hourly"},
                "filters": {"service": "api-gateway"}
            }
        )
        
        assert customized_template is not None
        assert "disk_usage" in customized_template.metrics
        assert customized_template.schedule.frequency == "hourly"
    
    async def test_data_visualization_generation(self, reporting_engine, report_test_config):
        """Test data visualization generation and rendering."""
        # Configure visualization settings
        await reporting_engine.configure_visualizations(
            report_test_config["visualization_config"]
        )
        
        # Generate test data for visualizations
        time_series_data = TestDataGenerator.generate_time_series_data(
            metrics=["cpu_usage", "memory_usage", "response_time"],
            duration=timedelta(days=7),
            interval=timedelta(hours=1)
        )
        
        distribution_data = TestDataGenerator.generate_distribution_data(
            metric="response_time",
            sample_size=10000
        )
        
        correlation_data = TestDataGenerator.generate_correlation_data(
            metrics=["cpu_usage", "memory_usage", "response_time", "throughput"],
            sample_size=1000
        )
        
        # Test line chart generation
        line_chart = await reporting_engine.create_visualization(
            chart_type="line_chart",
            data=time_series_data,
            config={
                "title": "Performance Metrics Over Time",
                "x_axis": "timestamp",
                "y_axis": ["cpu_usage", "memory_usage"],
                "colors": ["#1f77b4", "#ff7f0e"],
                "show_legend": True,
                "grid": True
            }
        )
        
        assert line_chart is not None
        assert line_chart["chart_type"] == "line_chart"
        assert "image_data" in line_chart
        assert "metadata" in line_chart
        
        # Test bar chart generation
        bar_chart = await reporting_engine.create_visualization(
            chart_type="bar_chart",
            data={"categories": ["API", "Database", "Cache", "AI Models"],
                  "values": [85.2, 92.1, 78.5, 89.7]},
            config={
                "title": "Service Performance Scores",
                "x_axis": "Service",
                "y_axis": "Performance Score",
                "color": "#2ca02c"
            }
        )
        
        assert bar_chart is not None
        assert bar_chart["chart_type"] == "bar_chart"
        
        # Test heatmap generation
        heatmap = await reporting_engine.create_visualization(
            chart_type="heatmap",
            data=correlation_data,
            config={
                "title": "Metrics Correlation Matrix",
                "colormap": "coolwarm",
                "annotations": True,
                "center": 0
            }
        )
        
        assert heatmap is not None
        assert heatmap["chart_type"] == "heatmap"
        
        # Test gauge chart generation
        gauge = await reporting_engine.create_visualization(
            chart_type="gauge",
            data={"value": 87.5, "min": 0, "max": 100},
            config={
                "title": "System Health Score",
                "color_ranges": [
                    {"min": 0, "max": 50, "color": "#d62728"},
                    {"min": 50, "max": 80, "color": "#ff7f0e"},
                    {"min": 80, "max": 100, "color": "#2ca02c"}
                ]
            }
        )
        
        assert gauge is not None
        assert gauge["chart_type"] == "gauge"
        
        # Test scatter plot generation
        scatter_plot = await reporting_engine.create_visualization(
            chart_type="scatter_plot",
            data={
                "x": [i for i in range(100)],
                "y": [i * 2 + np.random.normal(0, 10) for i in range(100)]
            },
            config={
                "title": "Performance Correlation",
                "x_axis": "CPU Usage (%)",
                "y_axis": "Response Time (ms)",
                "color": "#1f77b4",
                "alpha": 0.6
            }
        )
        
        assert scatter_plot is not None
        assert scatter_plot["chart_type"] == "scatter_plot"
        
        # Test dashboard creation with multiple visualizations
        dashboard = await reporting_engine.create_dashboard(
            title="Performance Dashboard",
            visualizations=[line_chart, bar_chart, heatmap, gauge],
            layout="2x2",
            config={
                "background_color": "#ffffff",
                "title_font_size": 16,
                "spacing": 0.05
            }
        )
        
        assert dashboard is not None
        assert "dashboard_image" in dashboard
        assert "individual_charts" in dashboard
        assert len(dashboard["individual_charts"]) == 4
    
    async def test_report_generation_and_formatting(self, reporting_engine, report_test_config):
        """Test complete report generation in multiple formats."""
        # Configure report templates
        await reporting_engine.configure_templates(report_test_config["report_templates"])
        
        # Generate daily performance report
        performance_report = await reporting_engine.generate_report(
            template_name="daily_performance_summary",
            time_range=timedelta(days=1),
            format=ReportFormat.HTML,
            include_raw_data=True
        )
        
        assert performance_report is not None
        assert performance_report["format"] == "html"
        assert "content" in performance_report
        assert "metadata" in performance_report
        assert "visualizations" in performance_report
        
        # Verify report content structure
        report_content = performance_report["content"]
        assert "executive_summary" in report_content
        assert "detailed_analysis" in report_content
        assert "recommendations" in report_content
        assert "appendix" in report_content
        
        # Test PDF report generation
        pdf_report = await reporting_engine.generate_report(
            template_name="weekly_business_report",
            time_range=timedelta(days=7),
            format=ReportFormat.PDF,
            include_charts=True
        )
        
        assert pdf_report is not None
        assert pdf_report["format"] == "pdf"
        assert "pdf_data" in pdf_report
        assert len(pdf_report["pdf_data"]) > 0  # PDF content exists
        
        # Test Excel report generation
        excel_report = await reporting_engine.generate_report(
            template_name="monthly_ai_analytics",
            time_range=timedelta(days=30),
            format=ReportFormat.EXCEL,
            include_raw_data=True
        )
        
        assert excel_report is not None
        assert excel_report["format"] == "excel"
        assert "excel_data" in excel_report
        
        # Verify Excel structure
        excel_metadata = excel_report["metadata"]["excel_structure"]
        assert "worksheets" in excel_metadata
        assert len(excel_metadata["worksheets"]) >= 3  # Summary, Charts, Data
        
        # Test JSON report generation
        json_report = await reporting_engine.generate_report(
            template_name="daily_performance_summary",
            time_range=timedelta(days=1),
            format=ReportFormat.JSON,
            include_raw_data=True
        )
        
        assert json_report is not None
        assert json_report["format"] == "json"
        assert "json_data" in json_report
        
        # Verify JSON structure
        json_data = json.loads(json_report["json_data"])
        assert "report_metadata" in json_data
        assert "summary_statistics" in json_data
        assert "time_series_data" in json_data
        assert "visualizations" in json_data
        
        # Test custom report generation
        custom_report = await reporting_engine.generate_custom_report(
            title="Custom Performance Analysis",
            metrics=["cpu_usage", "memory_usage", "response_time"],
            time_range=timedelta(days=3),
            visualizations=["line_chart", "heatmap"],
            format=ReportFormat.HTML,
            filters={
                "service": ["api-gateway", "user-service"],
                "severity": ["warning", "error", "critical"]
            },
            comparison_period=timedelta(days=7)  # Compare with previous week
        )
        
        assert custom_report is not None
        assert "comparison_analysis" in custom_report["content"]
        assert "filtered_data" in custom_report["metadata"]
    
    async def test_automated_reporting_scheduler(self, reporting_engine, report_test_config):
        """Test automated report scheduling and delivery."""
        # Configure automated reporting
        await reporting_engine.configure_automated_reporting(
            report_test_config["report_templates"]
        )
        
        # Track scheduled reports
        scheduled_reports = []
        delivered_reports = []
        
        async def schedule_callback(report_info):
            scheduled_reports.append(report_info)
        
        async def delivery_callback(delivery_info):
            delivered_reports.append(delivery_info)
        
        reporting_engine.add_schedule_callback(schedule_callback)
        reporting_engine.add_delivery_callback(delivery_callback)
        
        # Test daily report scheduling
        await reporting_engine.schedule_report(
            template_name="daily_performance_summary",
            schedule=ReportSchedule(frequency="daily", time="09:00"),
            next_run=datetime.utcnow() + timedelta(seconds=1)  # Run soon for testing
        )
        
        # Wait for scheduled execution
        await asyncio.sleep(2)
        
        # Verify report was scheduled and executed
        assert len(scheduled_reports) >= 1
        
        daily_schedule = next(
            (s for s in scheduled_reports if s["template"] == "daily_performance_summary"),
            None
        )
        assert daily_schedule is not None
        assert daily_schedule["status"] == "executed"
        
        # Test weekly report scheduling
        next_monday = datetime.utcnow() + timedelta(days=(7 - datetime.utcnow().weekday()))
        
        await reporting_engine.schedule_report(
            template_name="weekly_business_report",
            schedule=ReportSchedule(frequency="weekly", day="monday", time="08:00"),
            next_run=next_monday
        )
        
        # Verify weekly schedule was created
        weekly_schedules = await reporting_engine.get_scheduled_reports(
            filter_by={"frequency": "weekly"}
        )
        
        assert len(weekly_schedules) >= 1
        
        weekly_schedule = next(
            (s for s in weekly_schedules if s["template"] == "weekly_business_report"),
            None
        )
        assert weekly_schedule is not None
        assert weekly_schedule["next_run"] >= next_monday
        
        # Test report delivery
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = MagicMock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            delivery_result = await reporting_engine.deliver_report(
                report_data={"content": "Test report content", "format": "html"},
                recipients=["test@example.com"],
                delivery_method="email",
                subject="Test Report Delivery"
            )
            
            assert delivery_result["success"] == True
            assert mock_server.send_message.called
        
        # Test delivery failure handling
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = Exception("SMTP error")
            
            delivery_result = await reporting_engine.deliver_report(
                report_data={"content": "Test report content", "format": "html"},
                recipients=["test@example.com"],
                delivery_method="email",
                subject="Test Report Delivery"
            )
            
            assert delivery_result["success"] == False
            assert "error" in delivery_result
        
        # Test retry mechanism
        retry_count = 0
        
        async def failing_delivery():
            nonlocal retry_count
            retry_count += 1
            if retry_count < 3:
                raise Exception("Temporary delivery failure")
            return {"success": True, "delivery_id": "retry_success"}
        
        with patch.object(reporting_engine, '_deliver_report', side_effect=failing_delivery):
            delivery_result = await reporting_engine.deliver_report_with_retry(
                report_data={"content": "Test retry content"},
                recipients=["test@example.com"],
                delivery_method="email",
                max_retries=3,
                retry_delay=0.1
            )
            
            assert delivery_result["success"] == True
            assert retry_count == 3  # Failed twice, succeeded on third try
    
    async def test_business_intelligence_and_insights(self, reporting_engine):
        """Test business intelligence and automated insights generation."""
        # Configure BI engine
        bi_config = {
            "insight_models": [
                {
                    "name": "performance_trends",
                    "model_type": "trend_analysis",
                    "metrics": ["cpu_usage", "memory_usage", "response_time"],
                    "analysis_window": timedelta(days=30),
                    "sensitivity": 0.05
                },
                {
                    "name": "anomaly_detection",
                    "model_type": "statistical_anomaly",
                    "metrics": ["error_rate", "throughput"],
                    "threshold": 2.0,  # 2 standard deviations
                    "min_samples": 100
                },
                {
                    "name": "capacity_forecasting",
                    "model_type": "time_series_forecast",
                    "metrics": ["cpu_usage", "memory_usage"],
                    "forecast_horizon": timedelta(days=7),
                    "confidence_interval": 0.95
                }
            ],
            "insight_triggers": [
                {
                    "trigger_type": "threshold_breach",
                    "condition": "cpu_usage > 90",
                    "action": "generate_capacity_insight"
                },
                {
                    "trigger_type": "trend_change",
                    "condition": "response_time_trend > 0.1",
                    "action": "generate_performance_insight"
                }
            ]
        }
        
        await reporting_engine.configure_business_intelligence(bi_config)
        
        # Generate historical data for analysis
        historical_data = TestDataGenerator.generate_business_intelligence_data(
            duration=timedelta(days=60),
            include_trends=True,
            include_anomalies=True
        )
        
        # Test trend analysis
        trend_insights = await reporting_engine.analyze_trends(
            data=historical_data,
            metrics=["cpu_usage", "memory_usage", "response_time"],
            analysis_period=timedelta(days=30)
        )
        
        assert trend_insights is not None
        assert "trend_analysis" in trend_insights
        assert "trend_strength" in trend_insights
        assert "trend_direction" in trend_insights
        assert "trend_significance" in trend_insights
        
        # Verify trend detection
        cpu_trend = trend_insights["trend_analysis"]["cpu_usage"]
        assert "slope" in cpu_trend
        assert "r_squared" in cpu_trend
        assert "p_value" in cpu_trend
        
        # Test anomaly detection insights
        anomaly_insights = await reporting_engine.detect_anomalies(
            data=historical_data,
            metrics=["error_rate", "throughput"],
            detection_method="statistical"
        )
        
        assert anomaly_insights is not None
        assert "anomalies_detected" in anomaly_insights
        assert "anomaly_score" in anomaly_insights
        assert "affected_metrics" in anomaly_insights
        
        # Test capacity forecasting
        capacity_forecast = await reporting_engine.forecast_capacity(
            data=historical_data,
            metrics=["cpu_usage", "memory_usage"],
            forecast_horizon=timedelta(days=7),
            include_confidence_intervals=True
        )
        
        assert capacity_forecast is not None
        assert "forecast_data" in capacity_forecast
        assert "confidence_intervals" in capacity_forecast
        assert "capacity_recommendations" in capacity_forecast
        
        # Verify forecast quality
        forecast_quality = capacity_forecast["forecast_quality"]
        assert "mape" in forecast_quality  # Mean Absolute Percentage Error
        assert "rmse" in forecast_quality  # Root Mean Square Error
        assert forecast_quality["mape"] < 0.2  # Less than 20% error
        
        # Test automated insight generation
        automated_insights = await reporting_engine.generate_automated_insights(
            data=historical_data,
            insight_types=["trends", "anomalies", "correlations", "forecasts"],
            priority_threshold=0.7
        )
        
        assert automated_insights is not None
        assert "insights" in automated_insights
        assert "priority_insights" in automated_insights
        assert "recommendations" in automated_insights
        
        # Verify insight quality
        high_priority_insights = automated_insights["priority_insights"]
        assert len(high_priority_insights) > 0
        
        for insight in high_priority_insights:
            assert "type" in insight
            assert "confidence" in insight
            assert "impact" in insight
            assert "recommendation" in insight
            assert insight["confidence"] >= 0.7
        
        # Test correlation analysis
        correlation_insights = await reporting_engine.analyze_correlations(
            data=historical_data,
            metrics=["cpu_usage", "memory_usage", "response_time", "error_rate"],
            correlation_threshold=0.5
        )
        
        assert correlation_insights is not None
        assert "correlation_matrix" in correlation_insights
        assert "significant_correlations" in correlation_insights
        assert "correlation_insights" in correlation_insights
        
        # Test root cause analysis
        root_cause_analysis = await reporting_engine.analyze_root_causes(
            problem_metric="response_time",
            problem_threshold=1000,  # Response time > 1000ms
            candidate_causes=["cpu_usage", "memory_usage", "database_latency"],
            analysis_window=timedelta(hours=2)
        )
        
        assert root_cause_analysis is not None
        assert "potential_causes" in root_cause_analysis
        assert "causal_strength" in root_cause_analysis
        assert "recommendations" in root_cause_analysis
    
    async def test_report_storage_and_archiving(self, reporting_engine, report_test_config):
        """Test report storage, retrieval, and archiving."""
        # Configure storage
        await reporting_engine.configure_storage(report_test_config["storage_config"])
        
        # Generate test reports
        test_reports = []
        
        for i in range(5):
            report = await reporting_engine.generate_report(
                template_name="daily_performance_summary",
                time_range=timedelta(days=1),
                format=ReportFormat.HTML,
                metadata={
                    "generated_at": datetime.utcnow(),
                    "report_id": f"test_report_{i:03d}",
                    "version": "1.0"
                }
            )
            test_reports.append(report)
        
        # Test report storage
        storage_results = []
        
        for report in test_reports:
            storage_result = await reporting_engine.store_report(
                report=report,
                storage_location="local",
                metadata=report["metadata"]
            )
            storage_results.append(storage_result)
        
        # Verify all reports were stored
        assert len(storage_results) == 5
        
        for result in storage_results:
            assert result["success"] == True
            assert "file_path" in result
            assert "storage_id" in result
        
        # Test report retrieval
        first_report_id = storage_results[0]["storage_id"]
        retrieved_report = await reporting_engine.retrieve_report(
            report_id=first_report_id,
            storage_location="local"
        )
        
        assert retrieved_report is not None
        assert retrieved_report["metadata"]["report_id"] == test_reports[0]["metadata"]["report_id"]
        
        # Test report search and filtering
        search_results = await reporting_engine.search_reports(
            filters={
                "template_name": "daily_performance_summary",
                "date_range": {
                    "start": datetime.utcnow() - timedelta(days=1),
                    "end": datetime.utcnow()
                }
            },
            sort_by="generated_at",
            limit=10
        )
        
        assert search_results is not None
        assert "reports" in search_results
        assert len(search_results["reports"]) >= 5
        
        # Test report archiving
        old_report_date = datetime.utcnow() - timedelta(days=365)  # 1 year old
        
        # Create old report for archiving test
        old_report = await reporting_engine.generate_report(
            template_name="daily_performance_summary",
            time_range=timedelta(days=1),
            format=ReportFormat.HTML,
            metadata={
                "generated_at": old_report_date,
                "report_id": "old_report_001",
                "version": "1.0"
            }
        )
        
        await reporting_engine.store_report(old_report, "local")
        
        # Configure archiving policy
        archiving_policy = {
            "archive_after": timedelta(days=90),
            "delete_after": timedelta(days=1095),  # 3 years
            "compression": True,
            "archive_location": "cloud"
        }
        
        await reporting_engine.configure_archiving_policy(archiving_policy)
        
        # Test archiving process
        archiving_result = await reporting_engine.archive_old_reports(
            dry_run=False,
            force_archive=True
        )
        
        assert archiving_result is not None
        assert "archived_count" in archiving_result
        assert "errors" in archiving_result
        assert archiving_result["archived_count"] >= 1  # Old report should be archived
        
        # Test report deletion
        deletion_result = await reporting_engine.delete_report(
            report_id=first_report_id,
            permanent=True
        )
        
        assert deletion_result["success"] == True
        assert deletion_result["deleted"] == True
        
        # Verify report was deleted
        try:
            deleted_report = await reporting_engine.retrieve_report(first_report_id)
            assert deleted_report is None  # Should not exist
        except Exception as e:
            assert "not found" in str(e).lower()
    
    async def test_reporting_system_performance(self, reporting_engine):
        """Test reporting system performance and scalability."""
        # Performance test with large dataset
        large_dataset = TestDataGenerator.generate_large_dataset(
            metrics=["cpu_usage", "memory_usage", "response_time", "throughput"],
            sample_count=100000,  # 100K data points
            time_range=timedelta(days=30)
        )
        
        # Test data aggregation performance
        start_time = datetime.utcnow()
        
        aggregation_result = await reporting_engine.aggregate_large_dataset(
            data=large_dataset,
            aggregation_functions=["mean", "max", "min", "std", "percentile_95"],
            group_by=["hour", "day"],
            parallel_processing=True
        )
        
        end_time = datetime.utcnow()
        aggregation_duration = (end_time - start_time).total_seconds()
        
        # Should process 100K points in reasonable time
        assert aggregation_duration < 10.0  # Less than 10 seconds
        assert aggregation_result is not None
        
        # Test concurrent report generation
        concurrent_reports = []
        
        async def generate_concurrent_report(report_id):
            return await reporting_engine.generate_report(
                template_name="daily_performance_summary",
                time_range=timedelta(days=1),
                format=ReportFormat.JSON,
                metadata={"concurrent_id": report_id}
            )
        
        # Generate 10 reports concurrently
        start_time = datetime.utcnow()
        
        tasks = [generate_concurrent_report(i) for i in range(10)]
        concurrent_results = await asyncio.gather(*tasks)
        
        end_time = datetime.utcnow()
        concurrent_duration = (end_time - start_time).total_seconds()
        
        # Verify all reports generated successfully
        assert len(concurrent_results) == 10
        
        for result in concurrent_results:
            assert result is not None
            assert result["format"] == "json"
        
        # Should handle concurrent generation efficiently
        assert concurrent_duration < 30.0  # Less than 30 seconds for 10 reports
        
        # Test memory usage during large report generation
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate large report with many visualizations
        large_report = await reporting_engine.generate_report(
            template_name="monthly_ai_analytics",
            time_range=timedelta(days=30),
            format=ReportFormat.PDF,
            include_raw_data=True,
            visualization_count=20  # Many charts
        )
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Memory usage should be reasonable
        assert memory_increase < 200  # Less than 200MB increase
        assert large_report is not None
        
        # Test caching performance
        cached_start = datetime.utcnow()
        
        # Generate same report again (should use cache)
        cached_report = await reporting_engine.generate_report(
            template_name="daily_performance_summary",
            time_range=timedelta(days=1),
            format=ReportFormat.JSON,
            use_cache=True
        )
        
        cached_end = datetime.utcnow()
        cached_duration = (cached_end - cached_start).total_seconds()
        
        # Cached generation should be much faster
        assert cached_duration < 1.0  # Less than 1 second with cache
        assert cached_report is not None
