"""Analytics and Reporting Configuration Module for Content Protection
==================================================================

Professional analytics and reporting configuration for content protection metrics,
performance monitoring, and business intelligence for content creators and platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  COPYRIGHT WARNING:
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, modification, or distribution of this code
without explicit written permission from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
Violators will be prosecuted to the full extent of the law.

Contact: mlaiel@live.de for licensing inquiries.
"""
from typing import Dict, Any, Optional, List, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import os


class AnalyticsScope(str, Enum):
    """Scope of analytics data collection."""
    USER = "user"
    CONTENT = "content"
    PLATFORM = "platform"
    GLOBAL = "global"
    COMPARATIVE = "comparative"


class MetricType(str, Enum):
    """Types of metrics to track."""
    PROTECTION_EFFECTIVENESS = "protection_effectiveness"
    CONTENT_MONITORING = "content_monitoring"
    REVENUE_IMPACT = "revenue_impact"
    VIOLATION_TRENDS = "violation_trends"
    RESPONSE_PERFORMANCE = "response_performance"
    PLATFORM_COVERAGE = "platform_coverage"
    USER_ENGAGEMENT = "user_engagement"
    SYSTEM_PERFORMANCE = "system_performance"


class ReportType(str, Enum):
    """Types of reports to generate."""
    EXECUTIVE_SUMMARY = "executive_summary"
    TECHNICAL_DETAILED = "technical_detailed"
    COMPLIANCE_AUDIT = "compliance_audit"
    FINANCIAL_IMPACT = "financial_impact"
    PLATFORM_ANALYSIS = "platform_analysis"
    TREND_ANALYSIS = "trend_analysis"
    PERFORMANCE_BENCHMARK = "performance_benchmark"
    INCIDENT_REPORT = "incident_report"


class ReportFormat(str, Enum):
    """Available report formats."""
    PDF = "pdf"
    HTML = "html"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    POWERPOINT = "powerpoint"
    INTERACTIVE_DASHBOARD = "interactive_dashboard"


class AggregationLevel(str, Enum):
    """Data aggregation levels."""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class VisualizationType(str, Enum):
    """Types of data visualizations."""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    HEAT_MAP = "heat_map"
    SCATTER_PLOT = "scatter_plot"
    GEOGRAPHIC_MAP = "geographic_map"
    FUNNEL_CHART = "funnel_chart"
    GAUGE_CHART = "gauge_chart"


@dataclass
class MetricConfig:
    """Configuration for individual metrics."""
    metric_name: str
    metric_type: MetricType
    aggregation_levels: Set[AggregationLevel] = field(
        default_factory=lambda: {AggregationLevel.DAILY, AggregationLevel.MONTHLY}
    )
    
    # Data collection settings
    collection_enabled: bool = True
    real_time_updates: bool = True
    historical_data_retention_days: int = 1095  # 3 years
    
    # Calculation settings
    calculation_method: str = "standard"
    custom_formula: Optional[str] = None
    baseline_comparison: bool = True
    trend_analysis: bool = True
    
    # Alert thresholds
    enable_alerts: bool = False
    warning_threshold: Optional[float] = None
    critical_threshold: Optional[float] = None
    improvement_threshold: Optional[float] = None
    
    # Visualization settings
    default_visualization: VisualizationType = VisualizationType.LINE_CHART
    color_scheme: str = "professional"
    show_in_dashboard: bool = True


@dataclass
class DashboardConfig:
    """Configuration for analytics dashboards."""
    # Dashboard settings
    dashboard_name: str
    refresh_interval_seconds: int = 300
    auto_refresh: bool = True
    
    # Layout configuration
    layout_type: str = "responsive"  # responsive, fixed, grid
    max_widgets_per_row: int = 4
    default_time_range: str = "30d"  # 1h, 24h, 7d, 30d, 90d, 1y
    
    # Widget configuration
    enable_drill_down: bool = True
    enable_data_export: bool = True
    enable_real_time_updates: bool = True
    
    # User experience
    enable_dark_mode: bool = False
    enable_customization: bool = True
    enable_annotations: bool = True
    
    # Performance
    lazy_loading: bool = True
    data_caching: bool = True
    cache_ttl_minutes: int = 15


@dataclass
class ReportScheduleConfig:
    """Configuration for report scheduling."""
    # Basic scheduling
    report_name: str
    report_type: ReportType
    enabled: bool = True
    
    # Frequency settings
    frequency: str = "weekly"  # daily, weekly, monthly, quarterly, custom
    day_of_week: Optional[int] = None  # 0-6, Monday=0
    day_of_month: Optional[int] = None  # 1-31
    time_of_day: str = "09:00"
    timezone: str = "UTC"
    
    # Content settings
    include_executive_summary: bool = True
    include_charts: bool = True
    include_raw_data: bool = False
    include_recommendations: bool = True
    
    # Distribution settings
    email_recipients: List[str] = field(default_factory=list)
    webhook_urls: List[str] = field(default_factory=list)
    storage_locations: List[str] = field(default_factory=list)
    
    # Format settings
    output_formats: Set[ReportFormat] = field(
        default_factory=lambda: {ReportFormat.PDF, ReportFormat.EXCEL}
    )
    
    # Customization
    custom_branding: bool = True
    include_watermark: bool = True
    password_protect: bool = False


@dataclass
class DataSourceConfig:
    """Configuration for analytics data sources."""
    # Data source identification
    source_name: str
    source_type: str  # database, api, file, stream
    connection_string: Optional[str] = None
    
    # Connection settings
    enable_connection_pooling: bool = True
    max_connections: int = 10
    connection_timeout_seconds: int = 30
    query_timeout_seconds: int = 300
    
    # Data refresh settings
    refresh_enabled: bool = True
    refresh_interval_minutes: int = 15
    incremental_refresh: bool = True
    full_refresh_schedule: str = "weekly"
    
    # Data quality
    enable_data_validation: bool = True
    enable_data_cleansing: bool = True
    handle_missing_values: bool = True
    outlier_detection: bool = True
    
    # Security
    encrypt_connection: bool = True
    require_authentication: bool = True
    credentials_vault_path: Optional[str] = None


@dataclass
class PerformanceMetricsConfig:
    """Configuration for performance metrics tracking."""
    # System performance metrics
    track_response_times: bool = True
    track_throughput: bool = True
    track_error_rates: bool = True
    track_resource_usage: bool = True
    
    # Business performance metrics
    track_protection_success_rate: bool = True
    track_false_positive_rate: bool = True
    track_revenue_protected: bool = True
    track_takedown_success_rate: bool = True
    
    # User experience metrics
    track_user_satisfaction: bool = True
    track_feature_usage: bool = True
    track_support_tickets: bool = True
    track_user_retention: bool = True
    
    # Benchmarking
    enable_industry_benchmarking: bool = True
    enable_competitor_analysis: bool = False
    enable_historical_comparison: bool = True
    
    # Thresholds for alerts
    response_time_threshold_ms: int = 2000
    error_rate_threshold_percentage: float = 1.0
    cpu_usage_threshold_percentage: float = 80.0
    memory_usage_threshold_percentage: float = 85.0


@dataclass
class ComplianceReportingConfig:
    """Configuration for compliance and audit reporting."""
    # Regulatory compliance
    enable_gdpr_reporting: bool = True
    enable_ccpa_reporting: bool = True
    enable_sox_reporting: bool = False
    enable_hipaa_reporting: bool = False
    
    # Audit requirements
    enable_audit_trail: bool = True
    audit_retention_years: int = 7
    enable_data_lineage: bool = True
    enable_change_tracking: bool = True
    
    # Report generation
    automated_compliance_reports: bool = True
    compliance_report_frequency: str = "monthly"
    include_data_privacy_metrics: bool = True
    include_security_metrics: bool = True
    
    # Certification support
    prepare_iso_27001_reports: bool = False
    prepare_soc2_reports: bool = False
    prepare_pci_dss_reports: bool = False


@dataclass
class AdvancedAnalyticsConfig:
    """Configuration for advanced analytics features."""
    # Machine learning analytics
    enable_predictive_analytics: bool = True
    enable_anomaly_detection: bool = True
    enable_pattern_recognition: bool = True
    enable_trend_forecasting: bool = True
    
    # AI-powered insights
    enable_automated_insights: bool = True
    insight_confidence_threshold: float = 0.80
    enable_natural_language_insights: bool = True
    
    # Advanced visualizations
    enable_interactive_charts: bool = True
    enable_3d_visualizations: bool = False
    enable_real_time_streaming: bool = True
    
    # Statistical analysis
    enable_correlation_analysis: bool = True
    enable_regression_analysis: bool = True
    enable_cohort_analysis: bool = True
    enable_funnel_analysis: bool = True
    
    # External integrations
    enable_google_analytics: bool = False
    enable_adobe_analytics: bool = False
    enable_mixpanel_integration: bool = False


@dataclass
class SecurityConfig:
    """Security configuration for analytics and reporting."""
    # Access control
    require_authentication: bool = True
    enable_role_based_access: bool = True
    enable_data_masking: bool = True
    enable_row_level_security: bool = True
    
    # Data encryption
    encrypt_data_at_rest: bool = True
    encrypt_data_in_transit: bool = True
    encryption_algorithm: str = "AES-256-GCM"
    
    # Privacy protection
    enable_data_anonymization: bool = True
    anonymize_user_data: bool = True
    respect_do_not_track: bool = True
    
    # Audit and monitoring
    log_all_access: bool = True
    monitor_suspicious_activity: bool = True
    enable_intrusion_detection: bool = True
    
    # Compliance
    gdpr_compliant: bool = True
    ccpa_compliant: bool = True
    data_retention_policy_days: int = 1095


@dataclass
class AnalyticsReportingConfig:
    """Main configuration for analytics and reporting system."""
    
    # Core settings
    analytics_scope: AnalyticsScope = AnalyticsScope.GLOBAL
    default_aggregation_level: AggregationLevel = AggregationLevel.DAILY
    
    # Enabled metrics
    enabled_metrics: Set[MetricType] = field(
        default_factory=lambda: {
            MetricType.PROTECTION_EFFECTIVENESS,
            MetricType.CONTENT_MONITORING,
            MetricType.REVENUE_IMPACT,
            MetricType.VIOLATION_TRENDS
        }
    )
    
    # Component configurations
    dashboard_configs: Dict[str, DashboardConfig] = field(default_factory=dict)
    metric_configs: Dict[str, MetricConfig] = field(default_factory=dict)
    report_schedules: List[ReportScheduleConfig] = field(default_factory=list)
    data_sources: Dict[str, DataSourceConfig] = field(default_factory=dict)
    
    # Feature configurations
    performance_config: PerformanceMetricsConfig = field(default_factory=PerformanceMetricsConfig)
    compliance_config: ComplianceReportingConfig = field(default_factory=ComplianceReportingConfig)
    advanced_config: AdvancedAnalyticsConfig = field(default_factory=AdvancedAnalyticsConfig)
    security_config: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Global settings
    enable_real_time_analytics: bool = True
    enable_historical_analysis: bool = True
    enable_predictive_modeling: bool = True
    enable_automated_reporting: bool = True
    
    # Performance settings
    max_concurrent_queries: int = 50
    query_timeout_seconds: int = 300
    enable_query_caching: bool = True
    cache_ttl_minutes: int = 60
    
    def __post_init__(self):
        """Initialize default configurations."""
        if not self.dashboard_configs:
            self._create_default_dashboards()
        
        if not self.metric_configs:
            self._create_default_metrics()
        
        if not self.data_sources:
            self._create_default_data_sources()
    
    def _create_default_dashboards(self):
        """Create default dashboard configurations."""
        # Executive dashboard
        self.dashboard_configs["executive"] = DashboardConfig(
            dashboard_name="Executive Overview",
            refresh_interval_seconds=600,
            default_time_range="30d",
            enable_drill_down=False,
            enable_customization=False
        )
        
        # Technical dashboard
        self.dashboard_configs["technical"] = DashboardConfig(
            dashboard_name="Technical Monitoring",
            refresh_interval_seconds=60,
            default_time_range="24h",
            enable_real_time_updates=True,
            max_widgets_per_row=6
        )
        
        # Compliance dashboard
        self.dashboard_configs["compliance"] = DashboardConfig(
            dashboard_name="Compliance & Audit",
            refresh_interval_seconds=3600,
            default_time_range="90d",
            enable_data_export=True
        )
    
    def _create_default_metrics(self):
        """Create default metric configurations."""
        # Protection effectiveness metric
        self.metric_configs["protection_effectiveness"] = MetricConfig(
            metric_name="Protection Effectiveness",
            metric_type=MetricType.PROTECTION_EFFECTIVENESS,
            enable_alerts=True,
            warning_threshold=0.85,
            critical_threshold=0.75,
            default_visualization=VisualizationType.GAUGE_CHART
        )
        
        # Content monitoring volume
        self.metric_configs["content_monitoring_volume"] = MetricConfig(
            metric_name="Content Monitoring Volume",
            metric_type=MetricType.CONTENT_MONITORING,
            aggregation_levels={AggregationLevel.HOURLY, AggregationLevel.DAILY},
            default_visualization=VisualizationType.LINE_CHART
        )
        
        # Revenue impact
        self.metric_configs["revenue_impact"] = MetricConfig(
            metric_name="Revenue Impact",
            metric_type=MetricType.REVENUE_IMPACT,
            enable_alerts=True,
            improvement_threshold=1000.0,
            default_visualization=VisualizationType.BAR_CHART
        )
    
    def _create_default_data_sources(self):
        """Create default data source configurations."""
        # Main database
        self.data_sources["main_db"] = DataSourceConfig(
            source_name="Main Database",
            source_type="database",
            refresh_interval_minutes=5,
            enable_data_validation=True
        )
        
        # Platform APIs
        self.data_sources["platform_apis"] = DataSourceConfig(
            source_name="Platform APIs",
            source_type="api",
            refresh_interval_minutes=30,
            connection_timeout_seconds=60
        )
    
    def add_custom_metric(self, metric_name: str, metric_config: MetricConfig):
        """Add a custom metric configuration."""
        self.metric_configs[metric_name] = metric_config
    
    def add_dashboard(self, dashboard_name: str, dashboard_config: DashboardConfig):
        """Add a custom dashboard configuration."""
        self.dashboard_configs[dashboard_name] = dashboard_config
    
    def schedule_report(self, report_config: ReportScheduleConfig):
        """Schedule a new report."""
        self.report_schedules.append(report_config)
    
    def validate_config(self) -> bool:
        """Validate the analytics and reporting configuration."""
        try:
            if not self.enabled_metrics:
                raise ValueError("At least one metric must be enabled")
            
            # Validate performance settings
            if self.max_concurrent_queries <= 0:
                raise ValueError("Max concurrent queries must be positive")
            
            if self.query_timeout_seconds <= 0:
                raise ValueError("Query timeout must be positive")
            
            # Validate dashboard configurations
            for dashboard_name, dashboard_config in self.dashboard_configs.items():
                if dashboard_config.refresh_interval_seconds <= 0:
                    raise ValueError(f"Invalid refresh interval for dashboard: {dashboard_name}")
            
            # Validate metric configurations
            for metric_name, metric_config in self.metric_configs.items():
                if metric_config.historical_data_retention_days <= 0:
                    raise ValueError(f"Invalid retention period for metric: {metric_name}")
            
            return True
            
        except Exception as e:
            print(f"Analytics reporting configuration validation error: {e}")
            return False
    
    @classmethod
    def from_environment(cls) -> 'AnalyticsReportingConfig':
        """Create configuration from environment variables."""
        config = cls()
        
        # Load basic settings
        if os.getenv('ANALYTICS_SCOPE'):
            config.analytics_scope = AnalyticsScope(os.getenv('ANALYTICS_SCOPE'))
        
        if os.getenv('DEFAULT_AGGREGATION_LEVEL'):
            config.default_aggregation_level = AggregationLevel(os.getenv('DEFAULT_AGGREGATION_LEVEL'))
        
        # Load performance settings
        if os.getenv('MAX_CONCURRENT_QUERIES'):
            config.max_concurrent_queries = int(os.getenv('MAX_CONCURRENT_QUERIES'))
        
        if os.getenv('QUERY_TIMEOUT_SECONDS'):
            config.query_timeout_seconds = int(os.getenv('QUERY_TIMEOUT_SECONDS'))
        
        # Load feature flags
        if os.getenv('ENABLE_REAL_TIME_ANALYTICS'):
            config.enable_real_time_analytics = os.getenv('ENABLE_REAL_TIME_ANALYTICS').lower() == 'true'
        
        if os.getenv('ENABLE_PREDICTIVE_MODELING'):
            config.enable_predictive_modeling = os.getenv('ENABLE_PREDICTIVE_MODELING').lower() == 'true'
        
        return config


# Factory functions for different environments

def create_enterprise_analytics_config() -> AnalyticsReportingConfig:
    """Create enterprise-grade analytics configuration."""
    config = AnalyticsReportingConfig()
    
    # Enterprise features
    config.enable_real_time_analytics = True
    config.enable_historical_analysis = True
    config.enable_predictive_modeling = True
    config.enable_automated_reporting = True
    
    # Advanced analytics
    config.advanced_config.enable_predictive_analytics = True
    config.advanced_config.enable_anomaly_detection = True
    config.advanced_config.enable_pattern_recognition = True
    config.advanced_config.enable_automated_insights = True
    
    # Comprehensive compliance
    config.compliance_config.enable_gdpr_reporting = True
    config.compliance_config.enable_ccpa_reporting = True
    config.compliance_config.enable_sox_reporting = True
    config.compliance_config.automated_compliance_reports = True
    
    # High performance
    config.max_concurrent_queries = 100
    config.query_timeout_seconds = 600
    config.enable_query_caching = True
    
    return config


def create_basic_analytics_config() -> AnalyticsReportingConfig:
    """Create basic analytics configuration."""
    config = AnalyticsReportingConfig()
    
    # Basic features only
    config.enabled_metrics = {
        MetricType.PROTECTION_EFFECTIVENESS,
        MetricType.CONTENT_MONITORING
    }
    
    # Simplified dashboards
    config.dashboard_configs = {
        "main": DashboardConfig(
            dashboard_name="Main Dashboard",
            refresh_interval_seconds=300,
            enable_customization=False
        )
    }
    
    # Basic performance
    config.max_concurrent_queries = 10
    config.enable_query_caching = False
    config.advanced_config.enable_predictive_analytics = False
    
    return config


def create_compliance_focused_config() -> AnalyticsReportingConfig:
    """Create compliance-focused analytics configuration."""
    config = AnalyticsReportingConfig()
    
    # Compliance-heavy configuration
    config.compliance_config.enable_gdpr_reporting = True
    config.compliance_config.enable_ccpa_reporting = True
    config.compliance_config.enable_audit_trail = True
    config.compliance_config.audit_retention_years = 7
    config.compliance_config.enable_data_lineage = True
    
    # Security emphasis
    config.security_config.require_authentication = True
    config.security_config.enable_role_based_access = True
    config.security_config.enable_data_masking = True
    config.security_config.log_all_access = True
    
    # Audit-focused reporting
    compliance_dashboard = DashboardConfig(
        dashboard_name="Compliance Monitoring",
        refresh_interval_seconds=3600,
        enable_data_export=True,
        auto_refresh=True
    )
    config.dashboard_configs["compliance"] = compliance_dashboard
    
    return config
