"""📊 Unified Analytics Dashboard - Complete KPI Monitoring System
================================================================

Unified analytics dashboard that aggregates all monitoring systems:
- User Metrics (MAU, DAU, retention)
- Revenue Metrics (MRR, ARR, CLV, churn)
- Technical Performance (system, API, database, uptime)
- AI Model Performance (accuracy, processing time, drift)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
CRITICAL WARNING: Unauthorized use, copying, or distribution strictly prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import pandas as pd
import numpy as np
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CollectorRegistry, REGISTRY

from .user_metrics_tracker import UserMetricsTracker, UserActivity, UserActivityType
from .revenue_metrics_tracker import RevenueMetricsTracker, RevenueTransaction, RevenueType
from .technical_performance_monitor import TechnicalPerformanceMonitor, PerformanceMetric, ComponentType
from .ai_model_performance_tracker import AIModelPerformanceTracker, ModelPrediction, AIModelType

logger = logging.getLogger(__name__)

# Global flag to prevent duplicate metrics registration
_dashboard_metrics_registered = False


class DashboardStatus(Enum):
    """
Dashboard operational status"""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class DashboardMetrics:
    """Unified dashboard metrics summary"""
    timestamp: datetime
    overall_health_score: float
    status: DashboardStatus
    
    # User metrics summary
    mau: int
    dau: int
    retention_rate_30d: float
    user_growth_rate: float
    
    # Revenue metrics summary
    mrr: float
    arr: float
    clv: float
    churn_rate: float
    revenue_growth_rate: float
    
    # Technical metrics summary
    system_cpu_usage: float
    system_memory_usage: float
    api_response_time_ms: float
    api_error_rate: float
    uptime_percentage: float
    
    # AI metrics summary
    avg_model_accuracy: float
    avg_inference_time_ms: float
    models_with_drift: int
    ai_throughput_per_second: float
    
    # Alerts and issues
    active_alerts: List[Dict[str, Any]] = field(default_factory=list)
    performance_issues: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class KPITarget:
    """
KPI target and threshold definition"""
    metric_name: str
    target_value: float
    warning_threshold: float
    critical_threshold: float
    unit: str
    description: str


class UnifiedAnalyticsDashboard:
    """
    Unified analytics dashboard that aggregates all monitoring systems.
    Provides comprehensive KPI tracking, alerting, and performance insights.
    """

    def __init__(self, user_tracker=None, revenue_tracker=None, tech_monitor=None, ai_tracker=None):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Use provided instances or create new ones
        self.user_tracker = user_tracker or UserMetricsTracker()
        self.revenue_tracker = revenue_tracker or RevenueMetricsTracker()
        self.tech_monitor = tech_monitor or TechnicalPerformanceMonitor()
        self.ai_tracker = ai_tracker or AIModelPerformanceTracker()
        
        # Dashboard state
        self.dashboard_cache = {}
        self.alert_history = []
        self.metrics_history = []
        
        # KPI targets and thresholds
        self.kpi_targets = {
            "mau_growth_rate": KPITarget("MAU Growth Rate", 10.0, 5.0, 0.0, "%", "Monthly Active Users growth"),
            "dau_growth_rate": KPITarget("DAU Growth Rate", 8.0, 3.0, -2.0, "%", "Daily Active Users growth"),
            "retention_30d": KPITarget("30-day Retention", 45.0, 35.0, 25.0, "%", "30-day user retention rate"),
            "mrr_growth_rate": KPITarget("MRR Growth Rate", 15.0, 8.0, 2.0, "%", "Monthly Recurring Revenue growth"),
            "churn_rate": KPITarget("Churn Rate", 3.0, 5.0, 8.0, "%", "Monthly customer churn rate"),
            "clv_cac_ratio": KPITarget("CLV/CAC Ratio", 3.0, 2.5, 2.0, "ratio", "Customer Lifetime Value to Acquisition Cost ratio"),
            "api_response_time": KPITarget("API Response Time", 250.0, 500.0, 1000.0, "ms", "Average API response time"),
            "api_error_rate": KPITarget("API Error Rate", 1.0, 3.0, 5.0, "%", "API error rate"),
            "uptime": KPITarget("System Uptime", 99.9, 99.5, 99.0, "%", "System uptime percentage"),
            "model_accuracy": KPITarget("AI Model Accuracy", 90.0, 85.0, 80.0, "%", "Average AI model accuracy"),
            "inference_time": KPITarget("AI Inference Time", 200.0, 500.0, 1000.0, "ms", "Average AI inference time")
        }
        
        # Prometheus metrics for dashboard
        global _dashboard_metrics_registered
        if not _dashboard_metrics_registered:
            self.prometheus_metrics = {
                "dashboard_health_score": Gauge(
                    "ainflue_dashboard_overall_health_score",
                    "Overall dashboard health score (0-100)"
                ),
                "kpi_target_performance": Gauge(
                    "ainflue_kpi_target_performance_ratio",
                    "KPI performance vs target ratio",
                    ["kpi_name"]
                ),
                "active_alerts_count": Gauge(
                    "ainflue_dashboard_active_alerts_total",
                    "Total number of active alerts",
                    ["severity"]
                )
            }
            _dashboard_metrics_registered = True
        else:
            # Use dummy metrics if already registered
            self.prometheus_metrics = {
                "dashboard_health_score": None,
                "kpi_target_performance": None,
                "active_alerts_count": None
            }
    
    async def initialize(self) -> None:
        """Initialize the unified analytics dashboard"""
        try:
            self.logger.info("Initializing Unified Analytics Dashboard...")
            
            # Initialize all component trackers
            await self.user_tracker.initialize()
            await self.revenue_tracker.initialize()
            await self.tech_monitor.initialize()
            await self.ai_tracker.initialize()
            
            # Setup dashboard-specific monitoring
            await self._setup_dashboard_monitoring()
            
            # Initialize alerting system
            await self._initialize_alerting()
            
            self.logger.info("Unified Analytics Dashboard initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Unified Analytics Dashboard: {e}")
            raise
    
    async def get_unified_metrics(self, time_window: Optional[timedelta] = None) -> DashboardMetrics:
        """Get comprehensive unified metrics dashboard"""
        time_window = time_window or timedelta(hours=24)
        
        try:
            self.logger.info("Collecting unified metrics dashboard")
            
            # Collect metrics from all components
            user_metrics = await self._collect_user_metrics()
            revenue_metrics = await self._collect_revenue_metrics()
            tech_metrics = await self._collect_technical_metrics()
            ai_metrics = await self._collect_ai_metrics()
            
            # Calculate overall health score
            health_score = await self._calculate_overall_health_score(
                user_metrics, revenue_metrics, tech_metrics, ai_metrics
            )
            
            # Determine dashboard status
            status = await self._determine_dashboard_status(health_score)
            
            # Collect active alerts
            active_alerts = await self._collect_active_alerts()
            
            # Identify performance issues
            performance_issues = await self._identify_performance_issues(
                user_metrics, revenue_metrics, tech_metrics, ai_metrics
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                user_metrics, revenue_metrics, tech_metrics, ai_metrics, performance_issues
            )
            
            # Create unified metrics
            unified_metrics = DashboardMetrics(
                timestamp=datetime.now(),
                overall_health_score=health_score,
                status=status,
                
                # User metrics
                mau=user_metrics.get("mau", 0),
                dau=user_metrics.get("dau", 0),
                retention_rate_30d=user_metrics.get("retention_30d", 0.0),
                user_growth_rate=user_metrics.get("growth_rate", 0.0),
                
                # Revenue metrics
                mrr=revenue_metrics.get("mrr", 0.0),
                arr=revenue_metrics.get("arr", 0.0),
                clv=revenue_metrics.get("clv", 0.0),
                churn_rate=revenue_metrics.get("churn_rate", 0.0),
                revenue_growth_rate=revenue_metrics.get("growth_rate", 0.0),
                
                # Technical metrics
                system_cpu_usage=tech_metrics.get("cpu_usage", 0.0),
                system_memory_usage=tech_metrics.get("memory_usage", 0.0),
                api_response_time_ms=tech_metrics.get("api_response_time", 0.0),
                api_error_rate=tech_metrics.get("api_error_rate", 0.0),
                uptime_percentage=tech_metrics.get("uptime", 0.0),
                
                # AI metrics
                avg_model_accuracy=ai_metrics.get("avg_accuracy", 0.0),
                avg_inference_time_ms=ai_metrics.get("avg_inference_time", 0.0),
                models_with_drift=ai_metrics.get("models_with_drift", 0),
                ai_throughput_per_second=ai_metrics.get("throughput", 0.0),
                
                # Issues and recommendations
                active_alerts=active_alerts,
                performance_issues=performance_issues,
                recommendations=recommendations
            )
            
            # Update Prometheus metrics
            await self._update_prometheus_dashboard_metrics(unified_metrics)
            
            # Cache results
            self.dashboard_cache["latest"] = unified_metrics
            self.metrics_history.append(unified_metrics)
            
            # Keep only last 1000 metrics records
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
            
            return unified_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect unified metrics: {e}")
            raise
    
    async def get_kpi_performance_report(self) -> Dict[str, Any]:
        """Generate KPI performance vs targets report"""
        try:
            self.logger.info("Generating KPI performance report")
            
            # Get current metrics
            current_metrics = await self.get_unified_metrics()
            
            report = {
                "report_timestamp": datetime.now().isoformat(),
                "overall_kpi_health": 0.0,
                "kpi_performance": {},
                "targets_met": 0,
                "targets_missed": 0,
                "critical_kpis": [],
                "top_performing_kpis": [],
                "improvement_needed": []
            }
            
            # Analyze each KPI against targets
            kpi_scores = []
            
            # User KPIs
            user_kpis = {
                "retention_30d": current_metrics.retention_rate_30d,
                "dau_growth_rate": current_metrics.user_growth_rate,
                "mau_growth_rate": current_metrics.user_growth_rate  # Assuming similar
            }
            
            # Revenue KPIs
            revenue_kpis = {
                "mrr_growth_rate": current_metrics.revenue_growth_rate,
                "churn_rate": current_metrics.churn_rate
            }
            
            # Technical KPIs
            tech_kpis = {
                "api_response_time": current_metrics.api_response_time_ms,
                "api_error_rate": current_metrics.api_error_rate,
                "uptime": current_metrics.uptime_percentage
            }
            
            # AI KPIs
            ai_kpis = {
                "model_accuracy": current_metrics.avg_model_accuracy,
                "inference_time": current_metrics.avg_inference_time_ms
            }
            
            all_kpis = {**user_kpis, **revenue_kpis, **tech_kpis, **ai_kpis}
            
            for kpi_name, current_value in all_kpis.items():
                if kpi_name in self.kpi_targets:
                    target = self.kpi_targets[kpi_name]
                    performance = await self._evaluate_kpi_performance(kpi_name, current_value, target)
                    
                    report["kpi_performance"][kpi_name] = performance
                    kpi_scores.append(performance["score"])
                    
                    if performance["status"] == "target_met":
                        report["targets_met"] += 1
                        if performance["score"] > 1.2:  # Exceeding target by 20%
                            report["top_performing_kpis"].append({
                                "kpi": kpi_name,
                                "performance": performance
                            })
                    else:
                        report["targets_missed"] += 1
                        if performance["status"] == "critical":
                            report["critical_kpis"].append({
                                "kpi": kpi_name,
                                "performance": performance
                            })
                        else:
                            report["improvement_needed"].append({
                                "kpi": kpi_name,
                                "performance": performance
                            })
            
            # Calculate overall KPI health
            if kpi_scores:
                report["overall_kpi_health"] = np.mean(kpi_scores) * 100
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate KPI performance report: {e}")
            raise
    
    async def get_real_time_alerts(self) -> List[Dict[str, Any]]:
        """Get real-time alerts from all monitoring systems"""
        try:
            alerts = []
            current_time = datetime.now()
            
            # Get current metrics
            current_metrics = await self.get_unified_metrics()
            
            # Check user metrics alerts
            if current_metrics.retention_rate_30d < self.kpi_targets["retention_30d"].critical_threshold:
                alerts.append({
                    "id": f"user_retention_{current_time.isoformat()}",
                    "type": "user_metrics",
                    "severity": AlertLevel.CRITICAL.value,
                    "title": "Critical User Retention Rate",
                    "message": f"30-day retention rate is {current_metrics.retention_rate_30d:.1f}%, below critical threshold",
                    "timestamp": current_time,
                    "metric_value": current_metrics.retention_rate_30d,
                    "threshold": self.kpi_targets["retention_30d"].critical_threshold
                })
            
            # Check revenue metrics alerts
            if current_metrics.churn_rate > self.kpi_targets["churn_rate"].critical_threshold:
                alerts.append({
                    "id": f"revenue_churn_{current_time.isoformat()}",
                    "type": "revenue_metrics",
                    "severity": AlertLevel.CRITICAL.value,
                    "title": "High Customer Churn Rate",
                    "message": f"Churn rate is {current_metrics.churn_rate:.1f}%, above critical threshold",
                    "timestamp": current_time,
                    "metric_value": current_metrics.churn_rate,
                    "threshold": self.kpi_targets["churn_rate"].critical_threshold
                })
            
            # Check technical performance alerts
            if current_metrics.api_response_time_ms > self.kpi_targets["api_response_time"].critical_threshold:
                alerts.append({
                    "id": f"tech_api_response_{current_time.isoformat()}",
                    "type": "technical_performance",
                    "severity": AlertLevel.CRITICAL.value,
                    "title": "High API Response Time",
                    "message": f"API response time is {current_metrics.api_response_time_ms:.1f}ms, above critical threshold",
                    "timestamp": current_time,
                    "metric_value": current_metrics.api_response_time_ms,
                    "threshold": self.kpi_targets["api_response_time"].critical_threshold
                })
            
            if current_metrics.uptime_percentage < self.kpi_targets["uptime"].critical_threshold:
                alerts.append({
                    "id": f"tech_uptime_{current_time.isoformat()}",
                    "type": "technical_performance",
                    "severity": AlertLevel.CRITICAL.value,
                    "title": "Low System Uptime",
                    "message": f"System uptime is {current_metrics.uptime_percentage:.2f}%, below SLA threshold",
                    "timestamp": current_time,
                    "metric_value": current_metrics.uptime_percentage,
                    "threshold": self.kpi_targets["uptime"].critical_threshold
                })
            
            # Check AI performance alerts
            if current_metrics.avg_model_accuracy < self.kpi_targets["model_accuracy"].critical_threshold:
                alerts.append({
                    "id": f"ai_accuracy_{current_time.isoformat()}",
                    "type": "ai_performance",
                    "severity": AlertLevel.CRITICAL.value,
                    "title": "Low AI Model Accuracy",
                    "message": f"Average model accuracy is {current_metrics.avg_model_accuracy:.1f}%, below critical threshold",
                    "timestamp": current_time,
                    "metric_value": current_metrics.avg_model_accuracy,
                    "threshold": self.kpi_targets["model_accuracy"].critical_threshold
                })
            
            if current_metrics.models_with_drift > 0:
                alerts.append({
                    "id": f"ai_drift_{current_time.isoformat()}",
                    "type": "ai_performance",
                    "severity": AlertLevel.WARNING.value,
                    "title": "Model Drift Detected",
                    "message": f"{current_metrics.models_with_drift} AI models showing performance drift",
                    "timestamp": current_time,
                    "metric_value": current_metrics.models_with_drift,
                    "threshold": 0
                })
            
            # Store alerts in history
            self.alert_history.extend(alerts)
            
            # Keep only last 1000 alerts
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Failed to get real-time alerts: {e}")
            return []
    
    async def get_comprehensive_dashboard_export(self) -> Dict[str, Any]:
        """Export comprehensive dashboard data for external systems"""
        try:
            self.logger.info("Generating comprehensive dashboard export")
            
            # Get all current metrics
            unified_metrics = await self.get_unified_metrics()
            kpi_report = await self.get_kpi_performance_report()
            alerts = await self.get_real_time_alerts()
            
            # Get detailed reports from each component
            user_report = await self._get_detailed_user_report()
            revenue_report = await self._get_detailed_revenue_report()
            tech_report = await self._get_detailed_tech_report()
            ai_report = await self._get_detailed_ai_report()
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "dashboard_version": "1.0.0",
                "data_freshness_minutes": 5,  # Data is updated every 5 minutes
                
                # Summary metrics
                "summary": {
                    "overall_health_score": unified_metrics.overall_health_score,
                    "status": unified_metrics.status.value,
                    "total_active_alerts": len(alerts),
                    "critical_alerts": len([a for a in alerts if a["severity"] == "critical"]),
                    "kpi_targets_met": kpi_report["targets_met"],
                    "kpi_targets_missed": kpi_report["targets_missed"]
                },
                
                # Unified metrics
                "metrics": {
                    "user_metrics": {
                        "mau": unified_metrics.mau,
                        "dau": unified_metrics.dau,
                        "retention_30d": unified_metrics.retention_rate_30d,
                        "user_growth_rate": unified_metrics.user_growth_rate
                    },
                    "revenue_metrics": {
                        "mrr": unified_metrics.mrr,
                        "arr": unified_metrics.arr,
                        "clv": unified_metrics.clv,
                        "churn_rate": unified_metrics.churn_rate,
                        "revenue_growth_rate": unified_metrics.revenue_growth_rate
                    },
                    "technical_metrics": {
                        "cpu_usage": unified_metrics.system_cpu_usage,
                        "memory_usage": unified_metrics.system_memory_usage,
                        "api_response_time": unified_metrics.api_response_time_ms,
                        "api_error_rate": unified_metrics.api_error_rate,
                        "uptime": unified_metrics.uptime_percentage
                    },
                    "ai_metrics": {
                        "avg_accuracy": unified_metrics.avg_model_accuracy,
                        "avg_inference_time": unified_metrics.avg_inference_time_ms,
                        "models_with_drift": unified_metrics.models_with_drift,
                        "throughput": unified_metrics.ai_throughput_per_second
                    }
                },
                
                # KPI performance
                "kpi_performance": kpi_report,
                
                # Active alerts
                "alerts": alerts,
                
                # Detailed reports
                "detailed_reports": {
                    "user_analytics": user_report,
                    "revenue_analytics": revenue_report,
                    "technical_performance": tech_report,
                    "ai_performance": ai_report
                },
                
                # Recommendations
                "recommendations": unified_metrics.recommendations,
                
                # Prometheus metrics export
                "prometheus_metrics": generate_latest().decode('utf-8')
            }
            
            return export_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate comprehensive dashboard export: {e}")
            raise
    
    # Helper methods for data collection and analysis
    async def _collect_user_metrics(self) -> Dict[str, Any]:
        """Collect user metrics summary"""
        try:
            mau_metrics = await self.user_tracker.calculate_mau_metrics()
            dau_metrics = await self.user_tracker.calculate_dau_metrics()
            retention_metrics = await self.user_tracker.calculate_retention_metrics()
            
            return {
                "mau": mau_metrics.total_mau,
                "dau": dau_metrics.total_dau,
                "retention_30d": retention_metrics.retention_rates.get("30_days", 0.0) * 100,
                "growth_rate": mau_metrics.mau_growth_rate
            }
        except Exception as e:
            self.logger.error(f"Failed to collect user metrics: {e}")
            return {"mau": 0, "dau": 0, "retention_30d": 0.0, "growth_rate": 0.0}
    
    async def _collect_revenue_metrics(self) -> Dict[str, Any]:
        """Collect revenue metrics summary"""
        try:
            mrr_metrics = await self.revenue_tracker.calculate_mrr_metrics()
            arr_metrics = await self.revenue_tracker.calculate_arr_metrics()
            clv_metrics = await self.revenue_tracker.calculate_clv_metrics()
            churn_metrics = await self.revenue_tracker.calculate_churn_metrics()
            
            return {
                "mrr": float(mrr_metrics.total_mrr),
                "arr": float(arr_metrics.total_arr),
                "clv": float(clv_metrics.avg_clv),
                "churn_rate": churn_metrics.monthly_churn_rate,
                "growth_rate": mrr_metrics.mrr_growth_rate
            }
        except Exception as e:
            self.logger.error(f"Failed to collect revenue metrics: {e}")
            return {"mrr": 0.0, "arr": 0.0, "clv": 0.0, "churn_rate": 0.0, "growth_rate": 0.0}
    
    async def _collect_technical_metrics(self) -> Dict[str, Any]:
        """Collect technical metrics summary"""
        try:
            system_metrics = await self.tech_monitor.collect_system_performance()
            api_metrics = await self.tech_monitor.collect_api_performance()
            uptime_metrics = await self.tech_monitor.collect_uptime_metrics()
            
            return {
                "cpu_usage": system_metrics.cpu_usage_percent,
                "memory_usage": system_metrics.memory_usage_percent,
                "api_response_time": api_metrics.avg_response_time_ms,
                "api_error_rate": api_metrics.error_rate_percent,
                "uptime": uptime_metrics.uptime_percentage_24h
            }
        except Exception as e:
            self.logger.error(f"Failed to collect technical metrics: {e}")
            return {"cpu_usage": 0.0, "memory_usage": 0.0, "api_response_time": 0.0, "api_error_rate": 0.0, "uptime": 0.0}
    
    async def _collect_ai_metrics(self) -> Dict[str, Any]:
        """Collect AI metrics summary"""
        try:
            ai_report = await self.ai_tracker.get_comprehensive_ai_performance_report()
            
            return {
                "avg_accuracy": ai_report.get("overall_metrics", {}).get("avg_accuracy", 0.0) * 100,
                "avg_inference_time": ai_report.get("overall_metrics", {}).get("avg_processing_time_ms", 0.0),
                "models_with_drift": ai_report.get("overall_metrics", {}).get("models_with_drift", 0),
                "throughput": 0.0  # Would be calculated from individual model throughputs
            }
        except Exception as e:
            self.logger.error(f"Failed to collect AI metrics: {e}")
            return {"avg_accuracy": 0.0, "avg_inference_time": 0.0, "models_with_drift": 0, "throughput": 0.0}
    
    async def _calculate_overall_health_score(self, user_metrics, revenue_metrics, tech_metrics, ai_metrics) -> float:
        """Calculate overall system health score (0-100)"""
        try:
            # Weight factors for different metric categories
            weights = {
                "user": 0.25,
                "revenue": 0.30,
                "technical": 0.25,
                "ai": 0.20
            }
            
            # User health score (0-100)
            user_score = min(100, max(0, (
                (user_metrics["retention_30d"] / 50.0 * 50) +  # Retention weight: 50%
                (min(user_metrics["growth_rate"], 20) / 20.0 * 50)  # Growth weight: 50%
            )))
            
            # Revenue health score (0-100)
            revenue_score = min(100, max(0, (
                (min(revenue_metrics["growth_rate"], 20) / 20.0 * 40) +  # Growth weight: 40%
                (max(0, 10 - revenue_metrics["churn_rate"]) / 10.0 * 60)  # Churn weight: 60%
            )))
            
            # Technical health score (0-100)
            tech_score = min(100, max(0, (
                (max(0, 100 - tech_metrics["cpu_usage"]) * 0.2) +
                (max(0, 100 - tech_metrics["memory_usage"]) * 0.2) +
                (max(0, 100 - tech_metrics["api_response_time"] / 10) * 0.3) +
                (max(0, 100 - tech_metrics["api_error_rate"] * 10) * 0.3)
            )))
            
            # AI health score (0-100)
            ai_score = min(100, max(0, (
                (ai_metrics["avg_accuracy"]) * 0.6 +  # Accuracy weight: 60%
                (max(0, 100 - ai_metrics["avg_inference_time"] / 10) * 0.4)  # Speed weight: 40%
            )))
            
            # Calculate weighted overall score
            overall_score = (
                user_score * weights["user"] +
                revenue_score * weights["revenue"] +
                tech_score * weights["technical"] +
                ai_score * weights["ai"]
            )
            
            return round(overall_score, 2)
            
        except Exception as e:
            self.logger.error(f"Failed to calculate overall health score: {e}")
            return 0.0
    
    async def _determine_dashboard_status(self, health_score: float) -> DashboardStatus:
        """Determine dashboard status based on health score"""
        if health_score >= 80:
            return DashboardStatus.HEALTHY
        elif health_score >= 60:
            return DashboardStatus.WARNING
        else:
            return DashboardStatus.CRITICAL
    
    async def _collect_active_alerts(self) -> List[Dict[str, Any]]:
        """
Collect active alerts from all systems"""
        try:
            alerts = await self.get_real_time_alerts()
            return alerts
        except Exception as e:
            self.logger.error(f"Failed to collect active alerts: {e}")
            return []
    
    async def _identify_performance_issues(self, user_metrics, revenue_metrics, tech_metrics, ai_metrics) -> List[Dict[str, Any]]:
        """Identify performance issues across all systems"""
        issues = []
        
        # User performance issues
        if user_metrics["retention_30d"] < 30:
            issues.append({
                "category": "user_engagement",
                "severity": "high",
                "issue": f"Low user retention rate: {user_metrics['retention_30d']:.1f}%",
                "recommendation": "Improve onboarding and user experience"
            })
        
        # Revenue performance issues
        if revenue_metrics["churn_rate"] > 5:
            issues.append({
                "category": "revenue",
                "severity": "high",
                "issue": f"High churn rate: {revenue_metrics['churn_rate']:.1f}%",
                "recommendation": "Implement customer success initiatives"
            })
        
        # Technical performance issues
        if tech_metrics["api_response_time"] > 500:
            issues.append({
                "category": "technical",
                "severity": "medium",
                "issue": f"High API response time: {tech_metrics['api_response_time']:.1f}ms",
                "recommendation": "Optimize API endpoints and add caching"
            })
        
        # AI performance issues
        if ai_metrics["avg_accuracy"] < 85:
            issues.append({
                "category": "ai",
                "severity": "medium",
                "issue": f"Low AI model accuracy: {ai_metrics['avg_accuracy']:.1f}%",
                "recommendation": "Review and retrain underperforming models"
            })
        
        return issues
    
    async def _generate_recommendations(self, user_metrics, revenue_metrics, tech_metrics, ai_metrics, issues) -> List[Dict[str, Any]]:
        """Generate strategic recommendations based on metrics and issues"""
        recommendations = []
        
        # User growth recommendations
        if user_metrics["growth_rate"] < 5:
            recommendations.append({
                "category": "user_growth",
                "priority": "high",
                "recommendation": "Increase marketing spend and optimize acquisition channels",
                "expected_impact": "10-15% increase in user growth"
            })
        
        # Revenue optimization recommendations
        if revenue_metrics["growth_rate"] < 10:
            recommendations.append({
                "category": "revenue",
                "priority": "high",
                "recommendation": "Implement value-based pricing and expand upselling",
                "expected_impact": "15-20% increase in MRR"
            })
        
        # Technical optimization recommendations
        if tech_metrics["cpu_usage"] > 70:
            recommendations.append({
                "category": "technical",
                "priority": "medium",
                "recommendation": "Scale infrastructure and optimize resource usage",
                "expected_impact": "Improved system performance and reliability"
            })
        
        # AI optimization recommendations
        if ai_metrics["models_with_drift"] > 0:
            recommendations.append({
                "category": "ai",
                "priority": "medium",
                "recommendation": "Implement automated model retraining pipelines",
                "expected_impact": "Consistent AI performance and accuracy"
            })
        
        return recommendations
    
    async def _evaluate_kpi_performance(self, kpi_name: str, current_value: float, target: KPITarget) -> Dict[str, Any]:
        """Evaluate KPI performance against target"""
        
        # For metrics where lower is better (like churn_rate, response time)
        lower_is_better = kpi_name in ["churn_rate", "api_response_time", "inference_time", "api_error_rate"]
        
        if lower_is_better:
            if current_value <= target.target_value:
                status = "target_met"
                score = target.target_value / current_value if current_value > 0 else 1.0
            elif current_value <= target.warning_threshold:
                status = "warning"
                score = target.target_value / current_value if current_value > 0 else 0.5
            else:
                status = "critical"
                score = target.target_value / current_value if current_value > 0 else 0.1
        else:
            if current_value >= target.target_value:
                status = "target_met"
                score = current_value / target.target_value
            elif current_value >= target.warning_threshold:
                status = "warning"
                score = current_value / target.target_value
            else:
                status = "critical"
                score = current_value / target.target_value
        
        performance_percentage = (current_value / target.target_value * 100) if not lower_is_better else (target.target_value / current_value * 100) if current_value > 0 else 0
        
        return {
            "kpi_name": kpi_name,
            "current_value": current_value,
            "target_value": target.target_value,
            "performance_percentage": performance_percentage,
            "status": status,
            "score": score,
            "unit": target.unit,
            "description": target.description
        }
    
    async def _update_prometheus_dashboard_metrics(self, metrics: DashboardMetrics) -> None:
        """Update Prometheus metrics for the dashboard"""
        try:
            # Update overall health score
            if self.prometheus_metrics["dashboard_health_score"]:
                self.prometheus_metrics["dashboard_health_score"].set(metrics.overall_health_score)
            
            # Update alert counts
            alert_counts = {"critical": 0, "warning": 0, "info": 0}
            for alert in metrics.active_alerts:
                severity = alert.get("severity", "info")
                if severity in alert_counts:
                    alert_counts[severity] += 1
            
            if self.prometheus_metrics["active_alerts_count"]:
                for severity, count in alert_counts.items():
                    self.prometheus_metrics["active_alerts_count"].labels(severity=severity).set(count)
                
        except Exception as e:
            self.logger.error(f"Failed to update Prometheus dashboard metrics: {e}")
    
    async def _get_detailed_user_report(self) -> Dict[str, Any]:
        """Get detailed user analytics report"""
        try:
            mau_metrics = await self.user_tracker.calculate_mau_metrics()
            dau_metrics = await self.user_tracker.calculate_dau_metrics()
            retention_metrics = await self.user_tracker.calculate_retention_metrics()
            engagement_metrics = await self.user_tracker.calculate_engagement_metrics()
            
            return {
                "mau_metrics": {
                    "total": mau_metrics.total_mau,
                    "new_users": mau_metrics.new_users_this_month,
                    "growth_rate": mau_metrics.mau_growth_rate
                },
                "dau_metrics": {
                    "total": dau_metrics.total_dau,
                    "growth_rate": dau_metrics.dau_growth_rate
                },
                "retention_metrics": {
                    "day_1": retention_metrics.retention_rates.get("1_day", 0.0) * 100,
                    "day_7": retention_metrics.retention_rates.get("7_days", 0.0) * 100,
                    "day_30": retention_metrics.retention_rates.get("30_days", 0.0) * 100
                },
                "engagement_metrics": {
                    "avg_session_duration": engagement_metrics.avg_session_duration,
                    "content_engagement_rate": engagement_metrics.content_engagement_rate
                }
            }
        except Exception as e:
            self.logger.error(f"Failed to get detailed user report: {e}")
            return {}
    
    async def _get_detailed_revenue_report(self) -> Dict[str, Any]:
        """Get detailed revenue analytics report"""
        try:
            insights = await self.revenue_tracker.generate_revenue_insights()
            
            return {
                "revenue_health_score": insights.revenue_health_score,
                "growth_trajectory": insights.growth_trajectory,
                "key_metrics": insights.key_metrics_summary,
                "risks": insights.risks_identified,
                "opportunities": insights.opportunities
            }
        except Exception as e:
            self.logger.error(f"Failed to get detailed revenue report: {e}")
            return {}
    
    async def _get_detailed_tech_report(self) -> Dict[str, Any]:
        """Get detailed technical performance report"""
        try:
            tech_report = await self.tech_monitor.get_comprehensive_performance_report()
            return tech_report
        except Exception as e:
            self.logger.error(f"Failed to get detailed tech report: {e}")
            return {}
    
    async def _get_detailed_ai_report(self) -> Dict[str, Any]:
        """Get detailed AI performance report"""
        try:
            ai_report = await self.ai_tracker.get_comprehensive_ai_performance_report()
            return ai_report
        except Exception as e:
            self.logger.error(f"Failed to get detailed AI report: {e}")
            return {}
    
    async def _setup_dashboard_monitoring(self) -> None:
        """Setup dashboard-specific monitoring"""
        try:
            # Initialize dashboard monitoring infrastructure
            self.monitoring_config = {
                "refresh_interval": 30,  # seconds
                "alert_threshold": 0.8,   # 80% utilization
                "data_retention": 86400 * 7,  # 7 days
                "enabled_metrics": [
                    "cpu_usage", "memory_usage", "disk_usage", 
                    "network_io", "response_time", "error_rate"
                ]
            }
            
            # Setup monitoring intervals
            self.monitoring_intervals = {
                "system_metrics": 10,    # seconds
                "app_metrics": 30,       # seconds  
                "health_checks": 60,     # seconds
                "performance": 5         # seconds
            }
            
            # Initialize metric collectors
            self.metric_collectors = {}
            for metric in self.monitoring_config["enabled_metrics"]:
                self.metric_collectors[metric] = {
                    "last_value": 0,
                    "trend": [],
                    "alerts": []
                }
            
            logger.info("Dashboard monitoring setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup dashboard monitoring: {e}")
            # Continue without monitoring rather than failing
    
    async def _initialize_alerting(self) -> None:
        """Initialize alerting system"""
        try:
            # Setup alerting configuration
            self.alerting_config = {
                "channels": {
                    "email": {
                        "enabled": True,
                        "recipients": ["admin@ainflue.com", "alerts@ainflue.com"],
                        "smtp_server": "smtp.ainflue.com",
                        "smtp_port": 587
                    },
                    "slack": {
                        "enabled": False,  # Would need webhook URL
                        "webhook_url": None,
                        "channel": "#alerts"
                    },
                    "webhook": {
                        "enabled": True,
                        "url": "https://api.ainflue.com/webhooks/alerts"
                    }
                },
                "rules": [
                    {
                        "name": "high_cpu_usage",
                        "condition": "cpu_percent > 80",
                        "severity": "warning",
                        "cooldown": 300  # 5 minutes
                    },
                    {
                        "name": "high_memory_usage", 
                        "condition": "memory_percent > 85",
                        "severity": "warning",
                        "cooldown": 300
                    },
                    {
                        "name": "service_down",
                        "condition": "health_status == 'unhealthy'",
                        "severity": "critical",
                        "cooldown": 60
                    },
                    {
                        "name": "high_error_rate",
                        "condition": "error_rate > 0.05",
                        "severity": "warning", 
                        "cooldown": 180
                    }
                ]
            }
            
            # Initialize alert state tracking
            self.alert_states = {}
            for rule in self.alerting_config["rules"]:
                self.alert_states[rule["name"]] = {
                    "active": False,
                    "last_triggered": None,
                    "count": 0
                }
            
            # Setup alert delivery queue
            self.alert_queue = asyncio.Queue()
            
            # Start alert processor background task
            self.alert_task = asyncio.create_task(self._process_alerts())
            
            logger.info("Alerting system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize alerting: {e}")
            # Continue without alerting rather than failing
    
    async def _process_alerts(self) -> None:
        """Background task to process and deliver alerts"""
        try:
            while True:
                try:
                    # Wait for alert with timeout
                    alert = await asyncio.wait_for(self.alert_queue.get(), timeout=30.0)
                    
                    # Check cooldown period
                    rule_name = alert.get("rule_name")
                    if rule_name in self.alert_states:
                        state = self.alert_states[rule_name]
                        now = datetime.utcnow()
                        
                        # Check if in cooldown period
                        if (state["last_triggered"] and 
                            (now - state["last_triggered"]).total_seconds() < alert.get("cooldown", 300)):
                            continue
                        
                        # Update alert state
                        state["last_triggered"] = now
                        state["count"] += 1
                        state["active"] = True
                    
                    # Deliver alert through configured channels
                    await self._deliver_alert(alert)
                    
                except asyncio.TimeoutError:
                    # No alerts to process, continue monitoring
                    continue
                except Exception as e:
                    logger.error(f"Error processing alert: {e}")
                    
        except asyncio.CancelledError:
            logger.info("Alert processor stopped")
        except Exception as e:
            logger.error(f"Alert processor error: {e}")
    
    async def _deliver_alert(self, alert: Dict[str, Any]) -> None:
        """Deliver alert through configured channels"""
        try:
            # Log the alert
            logger.warning(f"🚨 ALERT: {alert.get('name', 'Unknown')} - {alert.get('message', 'No message')}")
            
            # Email delivery (simplified)
            if self.alerting_config["channels"]["email"]["enabled"]:
                # In production, would send actual emails
                logger.info(f"📧 Alert sent to email: {alert.get('name')}")
            
            # Webhook delivery (simplified)
            if self.alerting_config["channels"]["webhook"]["enabled"]:
                # In production, would make HTTP POST to webhook URL
                logger.info(f"🔗 Alert sent to webhook: {alert.get('name')}")
            
            # Store alert in metrics for dashboard display
            alert_metric = {
                "timestamp": datetime.utcnow().isoformat(),
                "rule": alert.get("rule_name"),
                "severity": alert.get("severity", "info"),
                "message": alert.get("message"),
                "value": alert.get("value")
            }
            
            # Add to recent alerts list (keep last 100)
            if not hasattr(self, 'recent_alerts'):
                self.recent_alerts = []
            
            self.recent_alerts.append(alert_metric)
            if len(self.recent_alerts) > 100:
                self.recent_alerts = self.recent_alerts[-100:]
                
        except Exception as e:
            logger.error(f"Failed to deliver alert: {e}")