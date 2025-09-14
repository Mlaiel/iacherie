"""Business Monitoring Configuration
from datetime import datetime

==================================

Configuration settings for the comprehensive business monitoring system.
Defines dashboards, alerts, KPIs, and monitoring parameters for business metrics.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import timedelta

try:
    from .business_monitoring import BusinessAlertType, BusinessMetricType
except ImportError:
    # Mock enums for testing
    from enum import Enum
    class BusinessAlertType(Enum):
    """BusinessAlertType class implementation"""
        REVENUE_DROP = "revenue_drop"
        CHURN_SPIKE = "churn_spike"
        CONVERSION_DROP = "conversion_drop"
    class BusinessMetricType(Enum):
    """BusinessMetricType class implementation"""
        MONTHLY_RECURRING_REVENUE = "mrr"
        CHURN_RATE = "churn_rate"
        CONVERSION_RATE = "conversion_rate"
        CUSTOMER_ACQUISITION_COST = "cac"
        LIFETIME_VALUE = "ltv"
        RETENTION_RATE = "retention_rate"


class MonitoringFrequency(Enum):
    """Monitoring frequency options"""
    REAL_TIME = "real_time"  # Every second
    HIGH = "high"            # Every 5 seconds
    MEDIUM = "medium"        # Every 30 seconds
    LOW = "low"             # Every 5 minutes
    BATCH = "batch"         # Hourly/Daily


class NotificationChannel(Enum):
    """Notification channels for alerts"""
    EMAIL = "email"
    SLACK = "slack"
    SMS = "sms"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"
    MOBILE_PUSH = "mobile_push"


@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    dashboard_id: str
    name: str
    description: str
    auto_refresh: bool = True
    refresh_interval_seconds: int = 30
    access_roles: List[str] = field(default_factory=lambda: ["admin", "manager"])
    layout_config: Dict[str, Any] = field(default_factory=dict)
    theme: str = "business"
    export_enabled: bool = True


@dataclass
class AlertConfig:
    """Alert configuration"""
    alert_id: str
    metric_type: BusinessMetricType
    alert_type: BusinessAlertType
    threshold_value: float
    comparison_operator: str
    severity: str
    notification_channels: List[NotificationChannel]
    escalation_enabled: bool = False
    escalation_delay: timedelta = field(default_factory=lambda: timedelta(minutes=30))
    auto_resolution: bool = True
    cooldown_period: timedelta = field(default_factory=lambda: timedelta(minutes=15))


@dataclass
class KPIConfig:
    """KPI monitoring configuration"""
    kpi_id: str
    name: str
    metric_type: BusinessMetricType
    calculation_method: str
    target_value: Optional[float] = None
    monitoring_frequency: MonitoringFrequency = MonitoringFrequency.MEDIUM
    historical_retention_days: int = 365
    trend_analysis_enabled: bool = True
    forecasting_enabled: bool = True


@dataclass
class FunnelConfig:
    """Funnel analysis configuration"""
    funnel_id: str
    name: str
    stages: List[str]
    conversion_goals: Dict[str, float]
    analysis_frequency: MonitoringFrequency = MonitoringFrequency.LOW
    optimization_alerts: bool = True
    segment_analysis: bool = True


@dataclass
class CohortConfig:
    """Cohort analysis configuration"""
    cohort_id: str
    cohort_type: str  # acquisition, behavior, revenue
    period_type: str  # daily, weekly, monthly
    retention_periods: List[int]  # periods to track (e.g., [1, 7, 30, 90])
    revenue_tracking: bool = True
    engagement_tracking: bool = True
    auto_segmentation: bool = True


@dataclass
class ChurnPredictionConfig:
    """Churn prediction configuration"""
    model_type: str = "random_forest"
    prediction_horizon_days: int = 30
    feature_importance_analysis: bool = True
    risk_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "low": 0.3,
        "medium": 0.5,
        "high": 0.7,
        "critical": 0.85
    })
    preventive_actions_enabled: bool = True
    prediction_frequency: MonitoringFrequency = MonitoringFrequency.LOW


@dataclass
class CompetitiveIntelligenceConfig:
    """Competitive intelligence configuration"""
    competitors: List[str]
    monitoring_sources: List[str] = field(default_factory=lambda: [
        "social_media", "news", "pricing", "features", "reviews"
    ])
    analysis_frequency: MonitoringFrequency = MonitoringFrequency.LOW
    threat_detection: bool = True
    opportunity_identification: bool = True
    market_share_tracking: bool = True


@dataclass
class RevenueMonitoringConfig:
    """Revenue monitoring configuration"""
    real_time_tracking: bool = True
    prediction_models: List[str] = field(default_factory=lambda: [
        "linear_regression", "prophet", "arima"
    ])
    forecast_horizon_months: int = 6
    anomaly_detection: bool = True
    revenue_streams: List[str] = field(default_factory=lambda: [
        "subscriptions", "licensing", "commissions", "partnerships"
    ])
    currency: str = "USD"
    target_accuracy: float = 0.85


@dataclass
class ABTestingConfig:
    """A/B Testing integration configuration"""
    auto_analytics_integration: bool = True
    statistical_significance_threshold: float = 0.95
    minimum_sample_size: int = 1000
    maximum_test_duration_days: int = 30
    auto_winner_selection: bool = False
    conversion_metrics: List[str] = field(default_factory=lambda: [
        "signup_rate", "retention_rate", "revenue_per_user", "engagement_score"
    ])


@dataclass
class ReportingConfig:
    """Automated reporting configuration"""
    stakeholder_reports: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "daily": {
            "enabled": True,
            "recipients": ["operations@company.com"],
            "delivery_time": "09:00",
            "include_sections": ["kpis", "alerts", "trends"]
        },
        "weekly": {
            "enabled": True,
            "recipients": ["management@company.com", "investors@company.com"],
            "delivery_time": "monday_09:00",
            "include_sections": ["executive_summary", "revenue", "growth", "competitive"]
        },
        "monthly": {
            "enabled": True,
            "recipients": ["board@company.com", "investors@company.com"],
            "delivery_time": "first_monday_09:00",
            "include_sections": ["comprehensive"]
        }
    })
    export_formats: List[str] = field(default_factory=lambda: ["pdf", "excel", "json"])
    custom_branding: bool = True


class BusinessMonitoringConfig:
    """Main business monitoring configuration class"""
    
    def __init__(self) -> None:
        self.dashboards = self._get_default_dashboards()
        self.alerts = self._get_default_alerts()
        self.kpis = self._get_default_kpis()
        self.funnels = self._get_default_funnels()
        self.cohorts = self._get_default_cohorts()
        self.churn_prediction = self._get_default_churn_prediction()
        self.competitive_intelligence = self._get_default_competitive_intelligence()
        self.revenue_monitoring = self._get_default_revenue_monitoring()
        self.ab_testing = self._get_default_ab_testing()
        self.reporting = self._get_default_reporting()
    
    def _get_default_dashboards(self) -> List[DashboardConfig]:
        """Get default dashboard configurations"""
        return [
            DashboardConfig(
                dashboard_id="executive_overview",
                name="Executive Overview",
                description="High-level business metrics for executives",
                refresh_interval_seconds=60,
                access_roles=["exec", "admin"],
                theme="executive"
            ),
            DashboardConfig(
                dashboard_id="revenue_dashboard",
                name="Revenue Analytics",
                description="Comprehensive revenue tracking and forecasting",
                refresh_interval_seconds=30,
                access_roles=["finance", "admin", "manager"]
            ),
            DashboardConfig(
                dashboard_id="user_analytics",
                name="User Analytics",
                description="User behavior, retention, and engagement metrics",
                access_roles=["product", "admin", "manager"]
            ),
            DashboardConfig(
                dashboard_id="competitive_intelligence",
                name="Competitive Intelligence",
                description="Market position and competitive analysis",
                refresh_interval_seconds=300,
                access_roles=["strategy", "admin", "exec"]
            )
        ]
    
    def _get_default_alerts(self) -> List[AlertConfig]:
        """Get default alert configurations"""
        return [
            AlertConfig(
                alert_id="revenue_drop_critical",
                metric_type=BusinessMetricType.MONTHLY_RECURRING_REVENUE,
                alert_type=BusinessAlertType.REVENUE_DROP,
                threshold_value=-0.05,  # 5% drop
                comparison_operator="<",
                severity="critical",
                notification_channels=[
                    NotificationChannel.EMAIL,
                    NotificationChannel.SLACK,
                    NotificationChannel.SMS
                ],
                escalation_enabled=True,
                escalation_delay=timedelta(minutes=15)
            ),
            AlertConfig(
                alert_id="churn_rate_warning",
                metric_type=BusinessMetricType.CHURN_RATE,
                alert_type=BusinessAlertType.CHURN_SPIKE,
                threshold_value=0.08,  # 8% churn rate
                comparison_operator=">",
                severity="warning",
                notification_channels=[
                    NotificationChannel.EMAIL,
                    NotificationChannel.DASHBOARD
                ],
                escalation_enabled=False
            ),
            AlertConfig(
                alert_id="conversion_drop_warning",
                metric_type=BusinessMetricType.CONVERSION_RATE,
                alert_type=BusinessAlertType.CONVERSION_DROP,
                threshold_value=0.02,  # 2% conversion rate
                comparison_operator="<",
                severity="warning",
                notification_channels=[
                    NotificationChannel.EMAIL,
                    NotificationChannel.SLACK
                ]
            ),
            AlertConfig(
                alert_id="acquisition_cost_critical",
                metric_type=BusinessMetricType.CUSTOMER_ACQUISITION_COST,
                alert_type=BusinessAlertType.CONVERSION_DROP,  # Use available enum value
                threshold_value=200.0,  # $200 CAC
                comparison_operator=">",
                severity="critical",
                notification_channels=[
                    NotificationChannel.EMAIL,
                    NotificationChannel.SLACK
                ],
                escalation_enabled=True
            )
        ]
    
    def _get_default_kpis(self) -> List[KPIConfig]:
        """Get default KPI configurations"""
        return [
            KPIConfig(
                kpi_id="mrr",
                name="Monthly Recurring Revenue",
                metric_type=BusinessMetricType.MONTHLY_RECURRING_REVENUE,
                calculation_method="sum",
                target_value=100000.0,
                monitoring_frequency=MonitoringFrequency.HIGH,
                forecasting_enabled=True
            ),
            KPIConfig(
                kpi_id="arr",
                name="Annual Recurring Revenue",
                metric_type=BusinessMetricType.MONTHLY_RECURRING_REVENUE,  # Use available enum value
                calculation_method="multiplication",
                target_value=1200000.0,
                monitoring_frequency=MonitoringFrequency.MEDIUM
            ),
            KPIConfig(
                kpi_id="ltv_cac_ratio",
                name="LTV/CAC Ratio",
                metric_type=BusinessMetricType.LIFETIME_VALUE,
                calculation_method="ratio",
                target_value=3.0,
                monitoring_frequency=MonitoringFrequency.LOW
            ),
            KPIConfig(
                kpi_id="retention_rate",
                name="User Retention Rate",
                metric_type=BusinessMetricType.RETENTION_RATE,
                calculation_method="percentage",
                target_value=0.85,
                monitoring_frequency=MonitoringFrequency.MEDIUM
            ),
            KPIConfig(
                kpi_id="churn_rate",
                name="User Churn Rate",
                metric_type=BusinessMetricType.CHURN_RATE,
                calculation_method="percentage",
                target_value=0.05,
                monitoring_frequency=MonitoringFrequency.MEDIUM
            )
        ]
    
    def _get_default_funnels(self) -> List[FunnelConfig]:
        """Get default funnel configurations"""
        return [
            FunnelConfig(
                funnel_id="user_acquisition",
                name="User Acquisition Funnel",
                stages=[
                    "landing_page_visit",
                    "signup_start",
                    "email_verification",
                    "profile_completion",
                    "first_content_upload",
                    "active_user"
                ],
                conversion_goals={
                    "signup_start": 0.15,
                    "email_verification": 0.8,
                    "profile_completion": 0.9,
                    "first_content_upload": 0.7,
                    "active_user": 0.6
                }
            ),
            FunnelConfig(
                funnel_id="monetization",
                name="Monetization Funnel",
                stages=[
                    "free_user",
                    "content_created",
                    "monetization_enabled",
                    "first_revenue",
                    "premium_upgrade"
                ],
                conversion_goals={
                    "content_created": 0.8,
                    "monetization_enabled": 0.4,
                    "first_revenue": 0.6,
                    "premium_upgrade": 0.2
                }
            )
        ]
    
    def _get_default_cohorts(self) -> List[CohortConfig]:
        """Get default cohort configurations"""
        return [
            CohortConfig(
                cohort_id="weekly_acquisition",
                cohort_type="acquisition",
                period_type="weekly",
                retention_periods=[1, 2, 4, 8, 12, 24, 52],  # weeks
                revenue_tracking=True,
                engagement_tracking=True
            ),
            CohortConfig(
                cohort_id="monthly_revenue",
                cohort_type="revenue",
                period_type="monthly",
                retention_periods=[1, 3, 6, 12],  # months
                revenue_tracking=True,
                engagement_tracking=False
            )
        ]
    
    def _get_default_churn_prediction(self) -> ChurnPredictionConfig:
        """Get default churn prediction configuration"""
        return ChurnPredictionConfig(
            model_type="random_forest",
            prediction_horizon_days=30,
            feature_importance_analysis=True,
            preventive_actions_enabled=True,
            prediction_frequency=MonitoringFrequency.LOW
        )
    
    def _get_default_competitive_intelligence(self) -> CompetitiveIntelligenceConfig:
        """Get default competitive intelligence configuration"""
        return CompetitiveIntelligenceConfig(
            competitors=[
                "competitor_a",
                "competitor_b", 
                "competitor_c"
            ],
            analysis_frequency=MonitoringFrequency.LOW,
            threat_detection=True,
            opportunity_identification=True
        )
    
    def _get_default_revenue_monitoring(self) -> RevenueMonitoringConfig:
        """Get default revenue monitoring configuration"""
        return RevenueMonitoringConfig(
            real_time_tracking=True,
            forecast_horizon_months=6,
            anomaly_detection=True,
            target_accuracy=0.85
        )
    
    def _get_default_ab_testing(self) -> ABTestingConfig:
        """Get default A/B testing configuration"""
        return ABTestingConfig(
            auto_analytics_integration=True,
            statistical_significance_threshold=0.95,
            minimum_sample_size=1000,
            maximum_test_duration_days=30
        )
    
    def _get_default_reporting(self) -> ReportingConfig:
        """Get default reporting configuration"""
        return ReportingConfig(
            export_formats=["pdf", "excel", "json"],
            custom_branding=True
        )

    def get_config_dict(self) -> Dict[str, Any]:
        """Get complete configuration as dictionary"""
        return {
            "dashboards": [dashboard.__dict__ for dashboard in self.dashboards],
            "alerts": [alert.__dict__ for alert in self.alerts],
            "kpis": [kpi.__dict__ for kpi in self.kpis],
            "funnels": [funnel.__dict__ for funnel in self.funnels],
            "cohorts": [cohort.__dict__ for cohort in self.cohorts],
            "churn_prediction": self.churn_prediction.__dict__,
            "competitive_intelligence": self.competitive_intelligence.__dict__,
            "revenue_monitoring": self.revenue_monitoring.__dict__,
            "ab_testing": self.ab_testing.__dict__,
            "reporting": self.reporting.__dict__
        }

    def validate_config(self) -> List[str]:
        """Validate configuration and return any errors"""
        errors = []
        
        # Validate dashboards
        dashboard_ids = [d.dashboard_id for d in self.dashboards]
        if len(dashboard_ids) != len(set(dashboard_ids)):
            errors.append("Duplicate dashboard IDs found")
        
        # Validate alerts
        alert_ids = [a.alert_id for a in self.alerts]
        if len(alert_ids) != len(set(alert_ids)):
            errors.append("Duplicate alert IDs found")
        
        # Validate KPIs
        kpi_ids = [k.kpi_id for k in self.kpis]
        if len(kpi_ids) != len(set(kpi_ids)):
            errors.append("Duplicate KPI IDs found")
        
        # Validate funnel stages
        for funnel in self.funnels:
            if len(funnel.stages) < 2:
                errors.append(f"Funnel '{funnel.funnel_id}' must have at least 2 stages")
        
        # Validate cohort retention periods
        for cohort in self.cohorts:
            if not cohort.retention_periods:
                errors.append(f"Cohort '{cohort.cohort_id}' must have retention periods defined")
        
        return errors


# Global configuration instance
business_monitoring_config = BusinessMonitoringConfig()