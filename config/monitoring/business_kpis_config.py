"""Business KPIs Configuration and Metrics Collection for Ainflue Platform
==========================================================================

Custom business metrics configuration for monitoring key performance indicators
that directly impact business operations and revenue generation.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
"""

import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import time
import logging
from prometheus_client import Counter, Histogram, Gauge, Info, CollectorRegistry


class MetricType(Enum):
    """Supported metric types for business KPIs"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    INFO = "info"


class BusinessDomain(Enum):
    """Business domains for metric categorization"""
    REVENUE = "revenue"
    USER_ENGAGEMENT = "user_engagement"
    CONTENT_CREATION = "content_creation"
    CONTENT_PROTECTION = "content_protection"
    AI_PERFORMANCE = "ai_performance"
    PLATFORM_ADOPTION = "platform_adoption"
    CUSTOMER_SUCCESS = "customer_success"
    MONETIZATION = "monetization"


@dataclass
class BusinessKPI:
    """Business KPI metric definition"""
    name: str
    description: str
    metric_type: MetricType
    domain: BusinessDomain
    labels: List[str] = field(default_factory=list)
    thresholds: Dict[str, float] = field(default_factory=dict)
    unit: Optional[str] = None
    business_impact: str = "medium"  # low, medium, high, critical


class BusinessKPIConfig:
    """
    Configuration for business KPIs and custom metrics
    """
    
    def __init__(self):
        self.enabled = os.getenv("BUSINESS_METRICS_ENABLED", "true").lower() == "true"
        self.collection_interval = int(os.getenv("BUSINESS_METRICS_INTERVAL", "60"))
        self.registry = CollectorRegistry()
        self.logger = logging.getLogger(__name__)
        
        # Initialize metric collectors
        self.metric_collectors = {}
        self._initialize_kpis()
    
    def _initialize_kpis(self):
        """Initialize all business KPI metric collectors"""
        kpis = self.get_business_kpis()
        
        for kpi in kpis:
            if kpi.metric_type == MetricType.COUNTER:
                collector = Counter(
                    kpi.name,
                    kpi.description,
                    labelnames=kpi.labels,
                    registry=self.registry
                )
            elif kpi.metric_type == MetricType.GAUGE:
                collector = Gauge(
                    kpi.name,
                    kpi.description,
                    labelnames=kpi.labels,
                    registry=self.registry
                )
            elif kpi.metric_type == MetricType.HISTOGRAM:
                collector = Histogram(
                    kpi.name,
                    kpi.description,
                    labelnames=kpi.labels,
                    registry=self.registry
                )
            elif kpi.metric_type == MetricType.INFO:
                collector = Info(
                    kpi.name,
                    kpi.description,
                    labelnames=kpi.labels,
                    registry=self.registry
                )
            
            self.metric_collectors[kpi.name] = collector
    
    def get_business_kpis(self) -> List[BusinessKPI]:
        """Get all defined business KPIs"""
        return [
            # Revenue Metrics
            BusinessKPI(
                name="revenue_generated_total",
                description="Total revenue generated in USD",
                metric_type=MetricType.COUNTER,
                domain=BusinessDomain.REVENUE,
                labels=["platform", "revenue_type", "currency"],
                thresholds={"hourly_min": 1000, "daily_min": 24000},
                unit="USD",
                business_impact="critical"
            ),
            
            BusinessKPI(
                name="revenue_per_user",
                description="Average revenue per user",
                metric_type=MetricType.GAUGE,
                domain=BusinessDomain.REVENUE,
                labels=["user_tier", "subscription_type"],
                thresholds={"min_arpu": 50},
                unit="USD",
                business_impact="high"
            ),
            
            BusinessKPI(
                name="revenue_detection_accuracy",
                description="Accuracy of revenue detection algorithms",
                metric_type=MetricType.GAUGE,
                domain=BusinessDomain.REVENUE,
                labels=["detection_method", "content_type"],
                thresholds={"min_accuracy": 0.90},
                unit="percentage",
                business_impact="critical"
            ),
            
            # User Engagement Metrics
            BusinessKPI(
                name="active_users_total",
                description="Number of active users",
                metric_type=MetricType.GAUGE,
                domain=BusinessDomain.USER_ENGAGEMENT,
                labels=["time_period", "user_type"],
                thresholds={"min_daily_active": 100, "min_monthly_active": 2000},
                business_impact="high"
            ),
            
            BusinessKPI(
                name="user_session_duration_seconds",
                description="User session duration in seconds",
                metric_type=MetricType.HISTOGRAM,
                domain=BusinessDomain.USER_ENGAGEMENT,
                labels=["user_type", "feature_used"],
                thresholds={"min_avg_session": 300},
                unit="seconds",
                business_impact="medium"
            ),
            
            BusinessKPI(
                name="user_retention_rate",
                description="User retention rate percentage",
                metric_type=MetricType.GAUGE,
                domain=BusinessDomain.USER_ENGAGEMENT,
                labels=["cohort", "time_period"],
                thresholds={"min_7day_retention": 0.70, "min_30day_retention": 0.40},
                unit="percentage",
                business_impact="high"
            ),
            
            # Content Creation Metrics
            BusinessKPI(
                name="content_uploads_total",
                description="Total number of content uploads",
                metric_type=MetricType.COUNTER,
                domain=BusinessDomain.CONTENT_CREATION,
                labels=["content_type", "platform", "quality_tier"],
                thresholds={"hourly_min": 50, "daily_min": 1000},
                business_impact="medium"
            ),
            
            BusinessKPI(
                name="content_processing_duration_seconds",
                description="Time taken to process uploaded content",
                metric_type=MetricType.HISTOGRAM,
                domain=BusinessDomain.CONTENT_CREATION,
                labels=["content_type", "processing_stage"],
                thresholds={"p95_max": 60},
                unit="seconds",
                business_impact="high"
            ),
            
            BusinessKPI(
                name="content_quality_score",
                description="Quality score of processed content",
                metric_type=MetricType.GAUGE,
                domain=BusinessDomain.CONTENT_CREATION,
                labels=["content_type", "ai_model"],
                thresholds={"min_quality": 0.85},
                unit="score",
                business_impact="medium"
            ),
            
            # Content Protection Metrics
            BusinessKPI(
                name="content_protection_detections_total",
                description="Total number of content protection detections",
                metric_type=MetricType.COUNTER,
                domain=BusinessDomain.CONTENT_PROTECTION,
                labels=["detection_type", "platform", "confidence_level"],
                business_impact="high"
            ),
            
            BusinessKPI(
                name="content_protection_false_positives_total",
                description="Number of false positive detections",
                metric_type=MetricType.COUNTER,
                domain=BusinessDomain.CONTENT_PROTECTION,
                labels=["detection_type", "reason"],
                thresholds={"max_false_positive_rate": 0.05},
                business_impact="medium"
            ),
            
            BusinessKPI(
                name="takedown_success_rate",
                description="Success rate of content takedown requests",
                metric_type=MetricType.GAUGE,
                domain=BusinessDomain.CONTENT_PROTECTION,
                labels=["platform", "content_type"],
                thresholds={"min_success_rate": 0.80},
                unit="percentage",
                business_impact="high"
            ),
            
            # AI Performance Metrics
            BusinessKPI(
                name="ai_inference_requests_total",
                description="Total AI inference requests",
                metric_type=MetricType.COUNTER,
                domain=BusinessDomain.AI_PERFORMANCE,
                labels=["model_name", "model_version", "request_type"],
                business_impact="medium"
            ),
            
            BusinessKPI(
                name="ai_inference_duration_seconds",
                description="AI model inference duration",
                metric_type=MetricType.HISTOGRAM,
                domain=BusinessDomain.AI_PERFORMANCE,
                labels=["model_name", "model_version", "input_size"],
                thresholds={"p95_max": 2.0},
                unit="seconds",
                business_impact="high"
            ),
            
            BusinessKPI(
                name="ai_model_accuracy",
                description="AI model accuracy score",
                metric_type=MetricType.GAUGE,
                domain=BusinessDomain.AI_PERFORMANCE,
                labels=["model_name", "model_version", "evaluation_dataset"],
                thresholds={"min_accuracy": 0.92},
                unit="score",
                business_impact="critical"
            ),
            
            # Platform Adoption Metrics
            BusinessKPI(
                name="feature_adoption_rate",
                description="Feature adoption rate by users",
                metric_type=MetricType.GAUGE,
                domain=BusinessDomain.PLATFORM_ADOPTION,
                labels=["feature_name", "user_segment"],
                thresholds={"min_adoption_rate": 0.30},
                unit="percentage",
                business_impact="medium"
            ),
            
            BusinessKPI(
                name="api_usage_total",
                description="Total API endpoint usage",
                metric_type=MetricType.COUNTER,
                domain=BusinessDomain.PLATFORM_ADOPTION,
                labels=["endpoint", "user_tier", "integration_type"],
                business_impact="medium"
            ),
            
            # Customer Success Metrics
            BusinessKPI(
                name="customer_satisfaction_score",
                description="Customer satisfaction score (CSAT)",
                metric_type=MetricType.GAUGE,
                domain=BusinessDomain.CUSTOMER_SUCCESS,
                labels=["survey_type", "user_segment"],
                thresholds={"min_csat": 4.0},
                unit="score",
                business_impact="high"
            ),
            
            BusinessKPI(
                name="support_ticket_resolution_time_seconds",
                description="Support ticket resolution time",
                metric_type=MetricType.HISTOGRAM,
                domain=BusinessDomain.CUSTOMER_SUCCESS,
                labels=["priority", "category"],
                thresholds={"p95_max": 86400},  # 24 hours
                unit="seconds",
                business_impact="medium"
            ),
            
            # Monetization Metrics
            BusinessKPI(
                name="subscription_conversions_total",
                description="Total subscription conversions",
                metric_type=MetricType.COUNTER,
                domain=BusinessDomain.MONETIZATION,
                labels=["plan_type", "conversion_source"],
                business_impact="high"
            ),
            
            BusinessKPI(
                name="payment_processing_success_rate",
                description="Payment processing success rate",
                metric_type=MetricType.GAUGE,
                domain=BusinessDomain.MONETIZATION,
                labels=["payment_method", "currency"],
                thresholds={"min_success_rate": 0.99},
                unit="percentage",
                business_impact="critical"
            ),
            
            BusinessKPI(
                name="churn_rate",
                description="Customer churn rate",
                metric_type=MetricType.GAUGE,
                domain=BusinessDomain.MONETIZATION,
                labels=["plan_type", "churn_reason"],
                thresholds={"max_monthly_churn": 0.05},
                unit="percentage",
                business_impact="critical"
            )
        ]
    
    def get_metrics_by_domain(self, domain: BusinessDomain) -> List[BusinessKPI]:
        """Get metrics by business domain"""
        return [kpi for kpi in self.get_business_kpis() if kpi.domain == domain]
    
    def get_critical_metrics(self) -> List[BusinessKPI]:
        """Get metrics with critical business impact"""
        return [kpi for kpi in self.get_business_kpis() if kpi.business_impact == "critical"]
    
    def get_sla_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get SLA thresholds for all metrics"""
        thresholds = {}
        for kpi in self.get_business_kpis():
            if kpi.thresholds:
                thresholds[kpi.name] = kpi.thresholds
        return thresholds
    
    def record_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Record a metric value"""
        if not self.enabled:
            return
        
        if metric_name not in self.metric_collectors:
            self.logger.warning(f"Metric {metric_name} not found in collectors")
            return
        
        collector = self.metric_collectors[metric_name]
        labels = labels or {}
        
        try:
            if isinstance(collector, Counter):
                collector.labels(**labels).inc(value)
            elif isinstance(collector, Gauge):
                collector.labels(**labels).set(value)
            elif isinstance(collector, Histogram):
                collector.labels(**labels).observe(value)
            elif isinstance(collector, Info):
                collector.labels(**labels).info(labels)
        except Exception as e:
            self.logger.error(f"Error recording metric {metric_name}: {e}")
    
    def get_metric_value(self, metric_name: str, labels: Dict[str, str] = None) -> float:
        """Get current metric value"""
        if metric_name not in self.metric_collectors:
            return 0.0
        
        collector = self.metric_collectors[metric_name]
        labels = labels or {}
        
        try:
            if isinstance(collector, (Counter, Gauge)):
                return collector.labels(**labels)._value._value
            elif isinstance(collector, Histogram):
                return collector.labels(**labels)._sum._value
        except Exception as e:
            self.logger.error(f"Error getting metric value {metric_name}: {e}")
            return 0.0
    
    def check_sla_compliance(self) -> Dict[str, bool]:
        """Check SLA compliance for all metrics with thresholds"""
        compliance = {}
        
        for kpi in self.get_business_kpis():
            if not kpi.thresholds:
                continue
            
            try:
                current_value = self.get_metric_value(kpi.name)
                
                for threshold_name, threshold_value in kpi.thresholds.items():
                    if threshold_name.startswith("min_"):
                        compliance[f"{kpi.name}_{threshold_name}"] = current_value >= threshold_value
                    elif threshold_name.startswith("max_"):
                        compliance[f"{kpi.name}_{threshold_name}"] = current_value <= threshold_value
                    elif threshold_name.endswith("_max"):
                        compliance[f"{kpi.name}_{threshold_name}"] = current_value <= threshold_value
                    elif threshold_name.endswith("_min"):
                        compliance[f"{kpi.name}_{threshold_name}"] = current_value >= threshold_value
                        
            except Exception as e:
                self.logger.error(f"Error checking SLA compliance for {kpi.name}: {e}")
                compliance[f"{kpi.name}_error"] = False
        
        return compliance
    
    def get_business_dashboard_config(self) -> Dict[str, Any]:
        """Get configuration for business metrics dashboard"""
        return {
            "dashboard_title": "Ainflue Business KPIs",
            "refresh_interval": "30s",
            "time_range": "24h",
            "panels": [
                {
                    "title": "Revenue Metrics",
                    "metrics": [kpi.name for kpi in self.get_metrics_by_domain(BusinessDomain.REVENUE)],
                    "type": "stat",
                    "thresholds": True
                },
                {
                    "title": "User Engagement",
                    "metrics": [kpi.name for kpi in self.get_metrics_by_domain(BusinessDomain.USER_ENGAGEMENT)],
                    "type": "graph",
                    "thresholds": True
                },
                {
                    "title": "Content Performance",
                    "metrics": [kpi.name for kpi in self.get_metrics_by_domain(BusinessDomain.CONTENT_CREATION)],
                    "type": "graph",
                    "thresholds": True
                },
                {
                    "title": "AI Model Performance",
                    "metrics": [kpi.name for kpi in self.get_metrics_by_domain(BusinessDomain.AI_PERFORMANCE)],
                    "type": "graph",
                    "thresholds": True
                },
                {
                    "title": "Content Protection",
                    "metrics": [kpi.name for kpi in self.get_metrics_by_domain(BusinessDomain.CONTENT_PROTECTION)],
                    "type": "stat",
                    "thresholds": True
                },
                {
                    "title": "Monetization",
                    "metrics": [kpi.name for kpi in self.get_metrics_by_domain(BusinessDomain.MONETIZATION)],
                    "type": "stat",
                    "thresholds": True
                }
            ]
        }
    
    def export_prometheus_config(self) -> str:
        """Export Prometheus configuration for business metrics"""
        config_lines = [
            "# Business KPIs Custom Metrics Configuration",
            "# Auto-generated by BusinessKPIConfig",
            "",
            "# Recording rules for business metrics",
            "groups:",
            "  - name: business_kpis",
            "    interval: 60s",
            "    rules:"
        ]
        
        for kpi in self.get_business_kpis():
            if kpi.metric_type == MetricType.GAUGE and kpi.thresholds:
                for threshold_name, threshold_value in kpi.thresholds.items():
                    config_lines.extend([
                        f"      - record: business:sla:{kpi.name}:{threshold_name}",
                        f"        expr: {kpi.name} {'>' if 'min_' in threshold_name else '<'} {threshold_value}",
                        ""
                    ])
        
        return "\n".join(config_lines)


# Factory function to get configured business KPI instance
def get_business_kpi_config() -> BusinessKPIConfig:
    """Get configured BusinessKPIConfig instance"""
    return BusinessKPIConfig()