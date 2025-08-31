"""Revenue Analytics Configuration Module
=====================================

Professional revenue analytics and business intelligence configuration.
Advanced metrics, reporting, and predictive analytics for monetization optimization.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + Data Scientist

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""
import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta


class MetricType(str, Enum):
    """Types of revenue and business metrics."""    # Core Revenue Metrics
    TOTAL_REVENUE = "total_revenue"
    MONTHLY_RECURRING_REVENUE = "monthly_recurring_revenue"
    ANNUAL_RECURRING_REVENUE = "annual_recurring_revenue"
    AVERAGE_REVENUE_PER_USER = "average_revenue_per_user"
    LIFETIME_VALUE = "lifetime_value"
    
    # Growth Metrics
    REVENUE_GROWTH_RATE = "revenue_growth_rate"
    USER_GROWTH_RATE = "user_growth_rate"
    CHURN_RATE = "churn_rate"
    RETENTION_RATE = "retention_rate"
    EXPANSION_REVENUE = "expansion_revenue"
    
    # Conversion Metrics
    CONVERSION_RATE = "conversion_rate"
    TRIAL_CONVERSION_RATE = "trial_conversion_rate"
    FREEMIUM_CONVERSION_RATE = "freemium_conversion_rate"
    UPGRADE_RATE = "upgrade_rate"
    DOWNGRADE_RATE = "downgrade_rate"
    
    # Customer Acquisition
    CUSTOMER_ACQUISITION_COST = "customer_acquisition_cost"
    PAYBACK_PERIOD = "payback_period"
    LTV_CAC_RATIO = "ltv_cac_ratio"
    
    # Platform-Specific
    STREAMING_REVENUE = "streaming_revenue"
    PROTECTION_REVENUE = "protection_revenue"
    LICENSING_REVENUE = "licensing_revenue"
    COMMISSION_REVENUE = "commission_revenue"
    
    # Financial Health
    GROSS_MARGIN = "gross_margin"
    NET_MARGIN = "net_margin"
    BURN_RATE = "burn_rate"
    RUNWAY_MONTHS = "runway_months"
    
    # Engagement Metrics
    DAILY_ACTIVE_USERS = "daily_active_users"
    MONTHLY_ACTIVE_USERS = "monthly_active_users"
    SESSION_DURATION = "session_duration"
    FEATURE_ADOPTION = "feature_adoption"


class TimeGranularity(str, Enum):
    """Time granularity for analytics aggregation."""    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    REAL_TIME = "real_time"


class ReportType(str, Enum):
    """Types of analytical reports."""    EXECUTIVE_DASHBOARD = "executive_dashboard"
    REVENUE_REPORT = "revenue_report"
    USER_ANALYTICS = "user_analytics"
    CHURN_ANALYSIS = "churn_analysis"
    COHORT_ANALYSIS = "cohort_analysis"
    SUBSCRIPTION_METRICS = "subscription_metrics"
    CONVERSION_FUNNEL = "conversion_funnel"
    RETENTION_ANALYSIS = "retention_analysis"
    PLATFORM_PERFORMANCE = "platform_performance"
    FINANCIAL_SUMMARY = "financial_summary"
    PREDICTIVE_FORECAST = "predictive_forecast"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    CUSTOM_REPORT = "custom_report"


class AlertType(str, Enum):
    """Types of revenue and business alerts."""    REVENUE_DROP = "revenue_drop"
    CHURN_SPIKE = "churn_spike"
    CONVERSION_DROP = "conversion_drop"
    HIGH_VALUE_CUSTOMER_CHURN = "high_value_customer_churn"
    PAYMENT_FAILURE_SPIKE = "payment_failure_spike"
    NEGATIVE_GROWTH = "negative_growth"
    BUDGET_THRESHOLD = "budget_threshold"
    ANOMALY_DETECTION = "anomaly_detection"
    FORECAST_DEVIATION = "forecast_deviation"


@dataclass
class MetricConfiguration:
    """Configuration for individual metrics."""    metric_type: MetricType
    enabled: bool = True
    
    # Data collection
    collection_frequency: TimeGranularity = TimeGranularity.DAILY
    retention_days: int = 365
    
    # Calculation settings
    calculation_method: str = "standard"  # standard, weighted, custom
    aggregation_method: str = "sum"  # sum, avg, median, max, min
    
    # Thresholds and benchmarks
    target_value: Optional[Decimal] = None
    warning_threshold: Optional[Decimal] = None
    critical_threshold: Optional[Decimal] = None
    
    # Segmentation
    segment_by_tier: bool = True
    segment_by_region: bool = True
    segment_by_cohort: bool = True
    
    # Advanced features
    enable_forecasting: bool = False
    enable_anomaly_detection: bool = False
    enable_benchmarking: bool = False


@dataclass
class DashboardWidget:
    """Configuration for dashboard widgets."""    widget_id: str
    widget_type: str  # chart, table, kpi, gauge, funnel
    title: str
    description: Optional[str] = None
    
    # Data configuration
    metrics: List[MetricType] = field(default_factory=list)
    time_range: str = "last_30_days"
    granularity: TimeGranularity = TimeGranularity.DAILY
    
    # Visualization
    chart_type: str = "line"  # line, bar, pie, area, scatter
    color_scheme: str = "default"
    height: int = 300
    width: int = 12  # Bootstrap grid columns
    
    # Interactivity
    drill_down_enabled: bool = True
    export_enabled: bool = True
    real_time_updates: bool = False
    
    # Permissions
    required_roles: List[str] = field(default_factory=list)
    visible_to_customers: bool = False


@dataclass
class CohortAnalysisConfig:
    """Configuration for cohort analysis."""    enabled: bool = True
    
    # Cohort definition
    cohort_type: str = "acquisition"  # acquisition, behavior, revenue
    cohort_period: TimeGranularity = TimeGranularity.MONTHLY
    analysis_period: int = 12  # months to analyze
    
    # Metrics to track
    tracked_metrics: List[MetricType] = field(default_factory=lambda: [
        MetricType.RETENTION_RATE,
        MetricType.AVERAGE_REVENUE_PER_USER,
        MetricType.CHURN_RATE
    ])
    
    # Segmentation
    segment_by_tier: bool = True
    segment_by_source: bool = True
    segment_by_geography: bool = False
    
    # Visualization
    heatmap_enabled: bool = True
    trend_analysis: bool = True
    statistical_significance: bool = True


@dataclass
class ForecastingConfig:
    """Configuration for predictive analytics and forecasting."""    enabled: bool = True
    
    # Forecasting models
    models: List[str] = field(default_factory=lambda: [
        "linear_regression", "arima", "prophet", "lstm"
    ])
    model_selection: str = "auto"  # auto, manual, ensemble
    
    # Forecasting parameters
    forecast_horizon_months: int = 12
    confidence_intervals: List[float] = field(default_factory=lambda: [0.8, 0.95])
    seasonality_detection: bool = True
    trend_detection: bool = True
    
    # Data requirements
    minimum_data_points: int = 30
    training_data_months: int = 24
    validation_split: float = 0.2
    
    # Model performance
    accuracy_threshold: float = 0.85
    retrain_frequency_days: int = 7
    performance_monitoring: bool = True
    
    # Forecast applications
    revenue_forecasting: bool = True
    churn_prediction: bool = True
    demand_forecasting: bool = True
    capacity_planning: bool = True


@dataclass
class AlertConfiguration:
    """Configuration for automated alerts and notifications."""    alert_type: AlertType
    enabled: bool = True
    
    # Trigger conditions
    threshold_value: Optional[Decimal] = None
    threshold_operator: str = "less_than"  # less_than, greater_than, equal_to
    lookback_period: str = "24_hours"
    
    # Alert sensitivity
    sensitivity: str = "medium"  # low, medium, high
    minimum_sample_size: int = 100
    statistical_significance: float = 0.95
    
    # Notification settings
    notification_channels: List[str] = field(default_factory=lambda: ["email", "slack"])
    recipient_groups: List[str] = field(default_factory=lambda: ["executives", "product"])
    escalation_enabled: bool = True
    escalation_delay_hours: int = 4
    
    # Response actions
    auto_response_enabled: bool = False
    response_actions: List[str] = field(default_factory=list)
    
    # Alert management
    cooldown_period_hours: int = 4
    alert_priority: str = "medium"  # low, medium, high, critical
    suppress_during_maintenance: bool = True


@dataclass
class ExportConfiguration:
    """Configuration for data export and API access."""    enabled: bool = True
    
    # Export formats
    supported_formats: List[str] = field(default_factory=lambda: [
        "csv", "excel", "json", "pdf", "html"
    ])
    default_format: str = "csv"
    
    # Data access
    max_records_per_export: int = 100000
    rate_limit_per_hour: int = 100
    data_freshness_minutes: int = 15
    
    # Scheduling
    scheduled_exports_enabled: bool = True
    max_scheduled_exports: int = 10
    supported_frequencies: List[str] = field(default_factory=lambda: [
        "daily", "weekly", "monthly", "quarterly"
    ])
    
    # Security
    encryption_enabled: bool = True
    access_log_enabled: bool = True
    ip_whitelisting: bool = False
    api_key_required: bool = True


@dataclass
class RevenueAnalyticsConfig:
    """Professional revenue analytics configuration."""    
    # Global Analytics Settings
    ENABLE_ANALYTICS: bool = True
    DEFAULT_CURRENCY: str = "EUR"
    DEFAULT_TIME_ZONE: str = "Europe/Berlin"
    
    # Data Collection
    REAL_TIME_PROCESSING: bool = True
    DATA_RETENTION_DAYS: int = 2555  # 7 years for compliance
    BATCH_PROCESSING_INTERVAL_MINUTES: int = 15
    
    # Core Metrics Configuration
    METRICS: Dict[MetricType, MetricConfiguration] = field(
        default_factory=lambda: {
            MetricType.MONTHLY_RECURRING_REVENUE: MetricConfiguration(
                metric_type=MetricType.MONTHLY_RECURRING_REVENUE,
                collection_frequency=TimeGranularity.DAILY,
                retention_days=1095,  # 3 years
                calculation_method="standard",
                target_value=Decimal("50000.00"),
                warning_threshold=Decimal("40000.00"),
                enable_forecasting=True,
                enable_anomaly_detection=True
            ),
            MetricType.CHURN_RATE: MetricConfiguration(
                metric_type=MetricType.CHURN_RATE,
                collection_frequency=TimeGranularity.DAILY,
                aggregation_method="avg",
                target_value=Decimal("5.0"),  # 5% monthly churn
                critical_threshold=Decimal("10.0"),
                enable_forecasting=True,
                enable_anomaly_detection=True
            ),
            MetricType.CUSTOMER_ACQUISITION_COST: MetricConfiguration(
                metric_type=MetricType.CUSTOMER_ACQUISITION_COST,
                collection_frequency=TimeGranularity.WEEKLY,
                target_value=Decimal("50.00"),
                warning_threshold=Decimal("75.00"),
                critical_threshold=Decimal("100.00"),
                enable_benchmarking=True
            ),
            MetricType.LIFETIME_VALUE: MetricConfiguration(
                metric_type=MetricType.LIFETIME_VALUE,
                collection_frequency=TimeGranularity.WEEKLY,
                calculation_method="predictive",
                target_value=Decimal("500.00"),
                enable_forecasting=True,
                segment_by_tier=True,
                segment_by_cohort=True
            ),
            MetricType.CONVERSION_RATE: MetricConfiguration(
                metric_type=MetricType.CONVERSION_RATE,
                collection_frequency=TimeGranularity.DAILY,
                aggregation_method="avg",
                target_value=Decimal("15.0"),  # 15% conversion
                warning_threshold=Decimal("12.0"),
                enable_anomaly_detection=True
            )
        }
    )
    
    # Dashboard Configurations
    EXECUTIVE_DASHBOARD: List[DashboardWidget] = field(
        default_factory=lambda: [
            DashboardWidget(
                widget_id="mrr_trend",
                widget_type="chart",
                title="Monthly Recurring Revenue",
                metrics=[MetricType.MONTHLY_RECURRING_REVENUE],
                chart_type="line",
                time_range="last_12_months",
                granularity=TimeGranularity.MONTHLY,
                height=400,
                width=12
            ),
            DashboardWidget(
                widget_id="key_metrics",
                widget_type="kpi",
                title="Key Metrics",
                metrics=[
                    MetricType.TOTAL_REVENUE,
                    MetricType.CHURN_RATE,
                    MetricType.CONVERSION_RATE,
                    MetricType.CUSTOMER_ACQUISITION_COST
                ],
                time_range="last_30_days",
                height=200,
                width=12
            ),
            DashboardWidget(
                widget_id="revenue_by_tier",
                widget_type="chart",
                title="Revenue by Subscription Tier",
                metrics=[MetricType.TOTAL_REVENUE],
                chart_type="pie",
                time_range="last_30_days",
                height=300,
                width=6
            ),
            DashboardWidget(
                widget_id="user_growth",
                widget_type="chart",
                title="User Growth",
                metrics=[MetricType.USER_GROWTH_RATE],
                chart_type="area",
                time_range="last_6_months",
                granularity=TimeGranularity.WEEKLY,
                height=300,
                width=6
            ),
            DashboardWidget(
                widget_id="conversion_funnel",
                widget_type="funnel",
                title="Conversion Funnel",
                metrics=[MetricType.CONVERSION_RATE],
                time_range="last_30_days",
                height=350,
                width=8
            ),
            DashboardWidget(
                widget_id="ltv_cac",
                widget_type="gauge",
                title="LTV:CAC Ratio",
                metrics=[MetricType.LTV_CAC_RATIO],
                time_range="current_month",
                height=200,
                width=4
            )
        ]
    )
    
    # Cohort Analysis
    COHORT_ANALYSIS: CohortAnalysisConfig = CohortAnalysisConfig()
    
    # Forecasting and Predictions
    FORECASTING: ForecastingConfig = ForecastingConfig()
    
    # Alert Configurations
    ALERTS: List[AlertConfiguration] = field(
        default_factory=lambda: [
            AlertConfiguration(
                alert_type=AlertType.REVENUE_DROP,
                threshold_value=Decimal("10.0"),  # 10% drop
                threshold_operator="less_than",
                lookback_period="24_hours",
                notification_channels=["email", "slack"],
                alert_priority="high"
            ),
            AlertConfiguration(
                alert_type=AlertType.CHURN_SPIKE,
                threshold_value=Decimal("8.0"),  # 8% churn rate
                threshold_operator="greater_than",
                lookback_period="7_days",
                sensitivity="high",
                escalation_enabled=True,
                alert_priority="critical"
            ),
            AlertConfiguration(
                alert_type=AlertType.CONVERSION_DROP,
                threshold_value=Decimal("20.0"),  # 20% drop in conversion
                lookback_period="48_hours",
                notification_channels=["email"],
                alert_priority="medium"
            ),
            AlertConfiguration(
                alert_type=AlertType.HIGH_VALUE_CUSTOMER_CHURN,
                threshold_value=Decimal("1000.00"),  # Customers with LTV > €1000
                notification_channels=["email", "slack", "teams"],
                alert_priority="critical",
                auto_response_enabled=True,
                response_actions=["create_retention_campaign"]
            )
        ]
    )
    
    # Segmentation Configuration
    SEGMENTATION: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "dimensions": [
            "subscription_tier",
            "geography",
            "acquisition_channel",
            "user_cohort",
            "usage_level",
            "revenue_tier",
            "platform_type"
        ],
        "custom_segments_enabled": True,
        "max_custom_segments": 50,
        "segment_refresh_frequency": "daily"
    })
    
    # Performance and Scalability
    PERFORMANCE_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "query_cache_enabled": True,
        "cache_ttl_minutes": 15,
        "max_concurrent_queries": 100,
        "query_timeout_seconds": 300,
        "result_pagination_enabled": True,
        "max_results_per_page": 10000,
        
        # Data processing
        "parallel_processing": True,
        "max_worker_threads": 10,
        "batch_size": 10000,
        "memory_limit_gb": 8,
        
        # Storage optimization
        "data_compression": True,
        "partitioning_enabled": True,
        "indexing_strategy": "optimized"
    })
    
    # Export and API
    EXPORT_CONFIG: ExportConfiguration = ExportConfiguration()
    
    # Integration Settings
    INTEGRATIONS: Dict[str, Any] = field(default_factory=lambda: {
        "google_analytics": {
            "enabled": False,
            "tracking_id": None,
            "custom_dimensions": True
        },
        "mixpanel": {
            "enabled": False,
            "project_token": None,
            "track_revenue": True
        },
        "segment": {
            "enabled": False,
            "write_key": None,
            "destinations": []
        },
        "amplitude": {
            "enabled": False,
            "api_key": None,
            "track_events": True
        },
        "custom_webhook": {
            "enabled": True,
            "webhook_url": None,
            "events": ["revenue_milestone", "churn_alert"]
        }
    })
    
    # Privacy and Compliance
    PRIVACY_SETTINGS: Dict[str, Any] = field(default_factory=lambda: {
        "gdpr_compliant": True,
        "data_anonymization": True,
        "right_to_be_forgotten": True,
        "data_export_enabled": True,
        "audit_logging": True,
        "consent_tracking": True,
        
        # Data sharing
        "third_party_sharing": False,
        "anonymized_benchmarking": True,
        "opt_out_enabled": True
    })
    
    # Custom Business Logic
    BUSINESS_RULES: Dict[str, Any] = field(default_factory=lambda: {
        # Revenue calculation rules
        "exclude_refunds_from_revenue": True,
        "exclude_chargebacks": True,
        "include_pending_payments": False,
        "revenue_recognition_method": "accrual",
        
        # Churn calculation
        "churn_grace_period_days": 7,
        "voluntary_churn_only": False,
        "exclude_paused_subscriptions": True,
        
        # Customer lifecycle
        "trial_users_count_as_customers": False,
        "freemium_users_count": True,
        "minimum_payment_for_customer": Decimal("1.00"),
        
        # Time-based calculations
        "business_hours_only": False,
        "exclude_weekends": False,
        "fiscal_year_start_month": 1  # January
    })
    
    def get_metric_config(self, metric_type: MetricType) -> Optional[MetricConfiguration]:
        """Get configuration for a specific metric."""        return self.METRICS.get(metric_type)
    
    def get_enabled_metrics(self) -> List[MetricType]:
        """Get list of enabled metrics."""        return [
            metric_type for metric_type, config in self.METRICS.items()
            if config.enabled
        ]
    
    def get_dashboard_widgets(self, dashboard_type: str = "executive") -> List[DashboardWidget]:
        """Get widgets for a specific dashboard."""        if dashboard_type == "executive":
            return self.EXECUTIVE_DASHBOARD
        return []
    
    def get_alert_config(self, alert_type: AlertType) -> Optional[AlertConfiguration]:
        """Get configuration for a specific alert type."""        for alert in self.ALERTS:
            if alert.alert_type == alert_type:
                return alert
        return None
    
    def calculate_ltv_cac_ratio(self, ltv: Decimal, cac: Decimal) -> Optional[Decimal]:
        """Calculate LTV:CAC ratio with proper error handling."""        if cac == Decimal("0.00"):
            return None
        return (ltv / cac).quantize(Decimal("0.01"))
    
    def get_recommended_metrics_for_tier(self, subscription_tier: str) -> List[MetricType]:
        """Get recommended metrics based on subscription tier."""        tier_metrics = {
            "freemium": [
                MetricType.CONVERSION_RATE,
                MetricType.FREEMIUM_CONVERSION_RATE,
                MetricType.DAILY_ACTIVE_USERS
            ],
            "starter": [
                MetricType.MONTHLY_RECURRING_REVENUE,
                MetricType.CHURN_RATE,
                MetricType.CUSTOMER_ACQUISITION_COST
            ],
            "professional": [
                MetricType.LIFETIME_VALUE,
                MetricType.EXPANSION_REVENUE,
                MetricType.NET_MARGIN
            ],
            "enterprise": [
                MetricType.ANNUAL_RECURRING_REVENUE,
                MetricType.GROSS_MARGIN,
                MetricType.RETENTION_RATE
            ]
        }
        return tier_metrics.get(subscription_tier.lower(), [])


# Global configuration instance
analytics_config = RevenueAnalyticsConfig()import os
from decimal import Decimal
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum


class AnalyticsMetric(str, Enum):
    """Available analytics metrics."""    TOTAL_REVENUE = "total_revenue"
    RECURRING_REVENUE = "recurring_revenue"
    MONTHLY_RECURRING_REVENUE = "monthly_recurring_revenue"
    ANNUAL_RECURRING_REVENUE = "annual_recurring_revenue"
    AVERAGE_REVENUE_PER_USER = "average_revenue_per_user"
    CUSTOMER_LIFETIME_VALUE = "customer_lifetime_value"
    CHURN_RATE = "churn_rate"
    RETENTION_RATE = "retention_rate"
    CONVERSION_RATE = "conversion_rate"
    REVENUE_GROWTH_RATE = "revenue_growth_rate"
    REVENUE_PER_PLATFORM = "revenue_per_platform"
    REVENUE_PER_CONTENT_TYPE = "revenue_per_content_type"
    GROSS_MARGIN = "gross_margin"
    NET_MARGIN = "net_margin"
    REVENUE_CONCENTRATION = "revenue_concentration"


class ReportType(str, Enum):
    """Types of revenue reports."""    DAILY_SUMMARY = "daily_summary"
    WEEKLY_REPORT = "weekly_report"
    MONTHLY_REPORT = "monthly_report"
    QUARTERLY_REPORT = "quarterly_report"
    ANNUAL_REPORT = "annual_report"
    REAL_TIME_DASHBOARD = "real_time_dashboard"
    COHORT_ANALYSIS = "cohort_analysis"
    PLATFORM_BREAKDOWN = "platform_breakdown"
    GEOGRAPHIC_ANALYSIS = "geographic_analysis"
    CONTENT_PERFORMANCE = "content_performance"
    CREATOR_EARNINGS = "creator_earnings"
    PREDICTIVE_FORECAST = "predictive_forecast"


class AggregationPeriod(str, Enum):
    """Data aggregation periods."""    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"
    ALL_TIME = "all_time"


class ChartType(str, Enum):
    """Chart types for visualization."""    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    AREA_CHART = "area_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    FUNNEL_CHART = "funnel_chart"
    WATERFALL_CHART = "waterfall_chart"
    GAUGE_CHART = "gauge_chart"
    TREEMAP = "treemap"


@dataclass
class MetricConfiguration:
    """Configuration for individual metrics."""    metric: AnalyticsMetric
    name: str
    description: str
    unit: str
    format_type: str  # currency, percentage, number, etc.
    decimal_places: int
    chart_types: List[ChartType]
    aggregation_methods: List[str]  # sum, avg, max, min, count
    benchmark_enabled: bool = False
    target_value: Optional[Decimal] = None
    alert_thresholds: Dict[str, Decimal] = field(default_factory=dict)


@dataclass
class ReportConfiguration:
    """Configuration for analytics reports."""    report_type: ReportType
    name: str
    description: str
    metrics: List[AnalyticsMetric]
    default_period: AggregationPeriod
    refresh_interval_minutes: int
    auto_generate: bool
    export_formats: List[str]
    recipients: List[str] = field(default_factory=list)
    template_file: Optional[str] = None
    custom_sql: Optional[str] = None


@dataclass
class DashboardConfiguration:
    """Dashboard configuration."""    dashboard_id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]]
    layout: Dict[str, Any]
    refresh_interval_seconds: int
    real_time_enabled: bool
    export_enabled: bool = True
    sharing_enabled: bool = True
    drill_down_enabled: bool = True


@dataclass
class RevenueAnalyticsConfig:
    """Main revenue analytics configuration class."""    
    # Database Configuration
    ANALYTICS_DB_URL: str = os.getenv(
        "ANALYTICS_DB_URL", 
        "postgresql://user:pass@localhost:5432/analytics_db"
    )
    
    WAREHOUSE_DB_URL: str = os.getenv(
        "WAREHOUSE_DB_URL", 
        "postgresql://user:pass@localhost:5432/warehouse_db"
    )
    
    # Data Processing Configuration
    DATA_PROCESSING_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "batch_size": 10000,
        "processing_interval_minutes": 15,
        "real_time_processing": True,
        "data_retention_days": 2555,  # 7 years
        "aggregation_delay_minutes": 5,
        "outlier_detection_enabled": True,
        "data_quality_checks": True,
        "automated_cleanup": True,
        "backup_frequency": "daily"
    })
    
    # Metrics Configuration
    METRICS_CONFIG: Dict[AnalyticsMetric, MetricConfiguration] = field(
        default_factory=lambda: {
            AnalyticsMetric.TOTAL_REVENUE: MetricConfiguration(
                metric=AnalyticsMetric.TOTAL_REVENUE,
                name="Total Revenue",
                description="Sum of all revenue streams",
                unit="currency",
                format_type="currency",
                decimal_places=2,
                chart_types=[ChartType.LINE_CHART, ChartType.BAR_CHART, ChartType.AREA_CHART],
                aggregation_methods=["sum"],
                benchmark_enabled=True,
                target_value=Decimal("100000.00"),
                alert_thresholds={
                    "low": Decimal("50000.00"),
                    "high": Decimal("500000.00")
                }
            ),
            AnalyticsMetric.MONTHLY_RECURRING_REVENUE: MetricConfiguration(
                metric=AnalyticsMetric.MONTHLY_RECURRING_REVENUE,
                name="Monthly Recurring Revenue (MRR)",
                description="Predictable monthly revenue from subscriptions",
                unit="currency",
                format_type="currency",
                decimal_places=2,
                chart_types=[ChartType.LINE_CHART, ChartType.AREA_CHART],
                aggregation_methods=["sum", "avg"],
                benchmark_enabled=True,
                target_value=Decimal("50000.00"),
                alert_thresholds={
                    "low": Decimal("25000.00"),
                    "high": Decimal("200000.00")
                }
            ),
            AnalyticsMetric.AVERAGE_REVENUE_PER_USER: MetricConfiguration(
                metric=AnalyticsMetric.AVERAGE_REVENUE_PER_USER,
                name="Average Revenue Per User (ARPU)",
                description="Average revenue generated per user",
                unit="currency",
                format_type="currency",
                decimal_places=2,
                chart_types=[ChartType.LINE_CHART, ChartType.BAR_CHART],
                aggregation_methods=["avg"],
                benchmark_enabled=True,
                target_value=Decimal("50.00"),
                alert_thresholds={
                    "low": Decimal("20.00"),
                    "high": Decimal("200.00")
                }
            ),
            AnalyticsMetric.CUSTOMER_LIFETIME_VALUE: MetricConfiguration(
                metric=AnalyticsMetric.CUSTOMER_LIFETIME_VALUE,
                name="Customer Lifetime Value (CLV)",
                description="Predicted total revenue from a customer",
                unit="currency",
                format_type="currency",
                decimal_places=2,
                chart_types=[ChartType.LINE_CHART, ChartType.BAR_CHART, ChartType.SCATTER_PLOT],
                aggregation_methods=["avg", "median"],
                benchmark_enabled=True,
                target_value=Decimal("500.00"),
                alert_thresholds={
                    "low": Decimal("200.00"),
                    "high": Decimal("2000.00")
                }
            ),
            AnalyticsMetric.CHURN_RATE: MetricConfiguration(
                metric=AnalyticsMetric.CHURN_RATE,
                name="Churn Rate",
                description="Percentage of customers who cancel",
                unit="percentage",
                format_type="percentage",
                decimal_places=1,
                chart_types=[ChartType.LINE_CHART, ChartType.GAUGE_CHART],
                aggregation_methods=["avg"],
                benchmark_enabled=True,
                target_value=Decimal("5.0"),
                alert_thresholds={
                    "low": Decimal("2.0"),
                    "high": Decimal("15.0")
                }
            ),
            AnalyticsMetric.CONVERSION_RATE: MetricConfiguration(
                metric=AnalyticsMetric.CONVERSION_RATE,
                name="Conversion Rate",
                description="Percentage of visitors who become customers",
                unit="percentage",
                format_type="percentage",
                decimal_places=1,
                chart_types=[ChartType.LINE_CHART, ChartType.FUNNEL_CHART, ChartType.GAUGE_CHART],
                aggregation_methods=["avg"],
                benchmark_enabled=True,
                target_value=Decimal("5.0"),
                alert_thresholds={
                    "low": Decimal("2.0"),
                    "high": Decimal("15.0")
                }
            ),
            AnalyticsMetric.REVENUE_GROWTH_RATE: MetricConfiguration(
                metric=AnalyticsMetric.REVENUE_GROWTH_RATE,
                name="Revenue Growth Rate",
                description="Month-over-month revenue growth percentage",
                unit="percentage",
                format_type="percentage",
                decimal_places=1,
                chart_types=[ChartType.LINE_CHART, ChartType.WATERFALL_CHART],
                aggregation_methods=["avg"],
                benchmark_enabled=True,
                target_value=Decimal("10.0"),
                alert_thresholds={
                    "low": Decimal("0.0"),
                    "high": Decimal("50.0")
                }
            )
        }
    )
    
    # Report Configurations
    REPORT_CONFIGS: Dict[ReportType, ReportConfiguration] = field(
        default_factory=lambda: {
            ReportType.DAILY_SUMMARY: ReportConfiguration(
                report_type=ReportType.DAILY_SUMMARY,
                name="Daily Revenue Summary",
                description="Daily overview of revenue performance",
                metrics=[
                    AnalyticsMetric.TOTAL_REVENUE,
                    AnalyticsMetric.RECURRING_REVENUE,
                    AnalyticsMetric.CONVERSION_RATE
                ],
                default_period=AggregationPeriod.DAY,
                refresh_interval_minutes=60,
                auto_generate=True,
                export_formats=["PDF", "CSV", "JSON"],
                recipients=["admin@ia-influencer.de"],
                template_file="templates/reports/daily_summary.html"
            ),
            ReportType.MONTHLY_REPORT: ReportConfiguration(
                report_type=ReportType.MONTHLY_REPORT,
                name="Monthly Revenue Report",
                description="Comprehensive monthly revenue analysis",
                metrics=[
                    AnalyticsMetric.TOTAL_REVENUE,
                    AnalyticsMetric.MONTHLY_RECURRING_REVENUE,
                    AnalyticsMetric.AVERAGE_REVENUE_PER_USER,
                    AnalyticsMetric.CUSTOMER_LIFETIME_VALUE,
                    AnalyticsMetric.CHURN_RATE,
                    AnalyticsMetric.REVENUE_GROWTH_RATE
                ],
                default_period=AggregationPeriod.MONTH,
                refresh_interval_minutes=1440,  # Daily
                auto_generate=True,
                export_formats=["PDF", "Excel", "PowerPoint"],
                recipients=["management@ia-influencer.de", "finance@ia-influencer.de"],
                template_file="templates/reports/monthly_report.html"
            ),
            ReportType.PLATFORM_BREAKDOWN: ReportConfiguration(
                report_type=ReportType.PLATFORM_BREAKDOWN,
                name="Platform Revenue Breakdown",
                description="Revenue performance by platform",
                metrics=[
                    AnalyticsMetric.REVENUE_PER_PLATFORM,
                    AnalyticsMetric.TOTAL_REVENUE
                ],
                default_period=AggregationPeriod.MONTH,
                refresh_interval_minutes=720,  # 12 hours
                auto_generate=True,
                export_formats=["PDF", "CSV"],
                template_file="templates/reports/platform_breakdown.html"
            ),
            ReportType.COHORT_ANALYSIS: ReportConfiguration(
                report_type=ReportType.COHORT_ANALYSIS,
                name="Customer Cohort Analysis",
                description="Customer retention and revenue cohort analysis",
                metrics=[
                    AnalyticsMetric.CUSTOMER_LIFETIME_VALUE,
                    AnalyticsMetric.RETENTION_RATE,
                    AnalyticsMetric.CHURN_RATE
                ],
                default_period=AggregationPeriod.MONTH,
                refresh_interval_minutes=1440,  # Daily
                auto_generate=True,
                export_formats=["PDF", "CSV", "JSON"],
                template_file="templates/reports/cohort_analysis.html"
            ),
            ReportType.PREDICTIVE_FORECAST: ReportConfiguration(
                report_type=ReportType.PREDICTIVE_FORECAST,
                name="Revenue Forecast",
                description="Predictive revenue forecasting and trends",
                metrics=[
                    AnalyticsMetric.TOTAL_REVENUE,
                    AnalyticsMetric.MONTHLY_RECURRING_REVENUE,
                    AnalyticsMetric.REVENUE_GROWTH_RATE
                ],
                default_period=AggregationPeriod.MONTH,
                refresh_interval_minutes=1440,  # Daily
                auto_generate=True,
                export_formats=["PDF", "Excel"],
                template_file="templates/reports/forecast.html"
            )
        }
    )
    
    # Dashboard Configurations
    DASHBOARD_CONFIGS: Dict[str, DashboardConfiguration] = field(
        default_factory=lambda: {
            "executive": DashboardConfiguration(
                dashboard_id="executive",
                name="Executive Revenue Dashboard",
                description="High-level revenue metrics for executives",
                widgets=[
                    {
                        "id": "total_revenue",
                        "type": "metric_card",
                        "metric": AnalyticsMetric.TOTAL_REVENUE,
                        "size": "large",
                        "position": {"row": 1, "col": 1, "width": 2, "height": 1}
                    },
                    {
                        "id": "mrr_chart",
                        "type": "line_chart",
                        "metric": AnalyticsMetric.MONTHLY_RECURRING_REVENUE,
                        "period": AggregationPeriod.MONTH,
                        "size": "large",
                        "position": {"row": 1, "col": 3, "width": 4, "height": 2}
                    },
                    {
                        "id": "churn_gauge",
                        "type": "gauge_chart",
                        "metric": AnalyticsMetric.CHURN_RATE,
                        "size": "medium",
                        "position": {"row": 2, "col": 1, "width": 2, "height": 1}
                    }
                ],
                layout={"columns": 6, "rows": 4},
                refresh_interval_seconds=300,  # 5 minutes
                real_time_enabled=True
            ),
            "operational": DashboardConfiguration(
                dashboard_id="operational",
                name="Operational Revenue Dashboard",
                description="Detailed operational revenue metrics",
                widgets=[
                    {
                        "id": "revenue_breakdown",
                        "type": "pie_chart",
                        "metric": AnalyticsMetric.REVENUE_PER_PLATFORM,
                        "size": "medium",
                        "position": {"row": 1, "col": 1, "width": 2, "height": 2}
                    },
                    {
                        "id": "growth_trend",
                        "type": "area_chart",
                        "metric": AnalyticsMetric.REVENUE_GROWTH_RATE,
                        "period": AggregationPeriod.MONTH,
                        "size": "large",
                        "position": {"row": 1, "col": 3, "width": 4, "height": 2}
                    },
                    {
                        "id": "conversion_funnel",
                        "type": "funnel_chart",
                        "metric": AnalyticsMetric.CONVERSION_RATE,
                        "size": "medium",
                        "position": {"row": 3, "col": 1, "width": 3, "height": 2}
                    }
                ],
                layout={"columns": 6, "rows": 5},
                refresh_interval_seconds=60,  # 1 minute
                real_time_enabled=True
            ),
            "creator": DashboardConfiguration(
                dashboard_id="creator",
                name="Creator Revenue Dashboard",
                description="Revenue dashboard for content creators",
                widgets=[
                    {
                        "id": "creator_earnings",
                        "type": "metric_card",
                        "metric": AnalyticsMetric.TOTAL_REVENUE,
                        "size": "large",
                        "position": {"row": 1, "col": 1, "width": 2, "height": 1}
                    },
                    {
                        "id": "platform_performance",
                        "type": "bar_chart",
                        "metric": AnalyticsMetric.REVENUE_PER_PLATFORM,
                        "size": "medium",
                        "position": {"row": 1, "col": 3, "width": 2, "height": 2}
                    },
                    {
                        "id": "content_performance",
                        "type": "treemap",
                        "metric": AnalyticsMetric.REVENUE_PER_CONTENT_TYPE,
                        "size": "large",
                        "position": {"row": 2, "col": 1, "width": 4, "height": 2}
                    }
                ],
                layout={"columns": 4, "rows": 4},
                refresh_interval_seconds=300,  # 5 minutes
                real_time_enabled=True
            )
        }
    )
    
    # Alert Configuration
    ALERT_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "channels": ["email", "slack", "webhook"],
        "alert_types": [
            "threshold_breach",
            "anomaly_detection",
            "forecast_deviation",
            "data_quality_issue",
            "processing_failure"
        ],
        "severity_levels": ["low", "medium", "high", "critical"],
        "notification_settings": {
            "email": {
                "recipients": ["alerts@ia-influencer.de"],
                "template": "templates/alerts/email.html"
            },
            "slack": {
                "webhook_url": os.getenv("SLACK_WEBHOOK_URL", ""),
                "channel": "#revenue-alerts"
            },
            "webhook": {
                "endpoints": ["/api/v1/alerts/revenue"],
                "retry_attempts": 3
            }
        },
        "escalation_rules": {
            "high": {"delay_minutes": 15, "escalate_to": ["manager@ia-influencer.de"]},
            "critical": {"delay_minutes": 5, "escalate_to": ["ceo@ia-influencer.de"]}
        }
    })
    
    # Export Configuration
    EXPORT_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "supported_formats": ["PDF", "CSV", "Excel", "JSON", "XML", "PowerPoint"],
        "default_format": "PDF",
        "max_export_size": 100000,  # Max rows
        "compression_enabled": True,
        "encryption_enabled": True,
        "watermark_enabled": True,
        "custom_branding": True,
        "scheduled_exports": True,
        "export_retention_days": 30,
        "cloud_storage_integration": ["AWS S3", "Google Drive", "Dropbox"]
    })
    
    # Machine Learning Configuration
    ML_CONFIG: Dict[str, Any] = field(default_factory=lambda: {
        "forecasting_enabled": True,
        "anomaly_detection_enabled": True,
        "customer_segmentation_enabled": True,
        "churn_prediction_enabled": True,
        "revenue_optimization_enabled": True,
        "models": {
            "forecasting": {
                "algorithm": "ARIMA",
                "training_data_months": 12,
                "forecast_horizon_months": 6,
                "confidence_interval": 0.95
            },
            "anomaly_detection": {
                "algorithm": "Isolation Forest",
                "sensitivity": 0.1,
                "lookback_days": 30
            },
            "churn_prediction": {
                "algorithm": "Random Forest",
                "features": ["usage", "engagement", "billing_history"],
                "prediction_horizon_days": 30
            }
        },
        "model_refresh_frequency": "weekly",
        "performance_monitoring": True,
        "automated_retraining": True
    })
    
    def get_metric_config(self, metric: AnalyticsMetric) -> Optional[MetricConfiguration]:
        """Get configuration for a specific metric."""        return self.METRICS_CONFIG.get(metric)
    
    def get_report_config(self, report_type: ReportType) -> Optional[ReportConfiguration]:
        """Get configuration for a specific report type."""        return self.REPORT_CONFIGS.get(report_type)
    
    def get_dashboard_config(self, dashboard_id: str) -> Optional[DashboardConfiguration]:
        """Get configuration for a specific dashboard."""        return self.DASHBOARD_CONFIGS.get(dashboard_id)
    
    def get_available_metrics(self) -> List[AnalyticsMetric]:
        """Get list of available metrics."""        return list(self.METRICS_CONFIG.keys())
    
    def get_available_reports(self) -> List[ReportType]:
        """Get list of available report types."""        return list(self.REPORT_CONFIGS.keys())
    
    def get_available_dashboards(self) -> List[str]:
        """Get list of available dashboard IDs."""        return list(self.DASHBOARD_CONFIGS.keys())


# Global configuration instance
analytics_config = RevenueAnalyticsConfig()
