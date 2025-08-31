"""Advanced Analytics and Reporting Schemas

Comprehensive Pydantic schemas for advanced analytics, KPIs, reporting,
and business intelligence in the IA Influencer Agent platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent + Content Protection Platform
Copyright: All rights reserved. Unauthorized use prohibited.
"""from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator, HttpUrl
from pydantic.types import PositiveInt, PositiveFloat


class ReportTypeEnum(str, Enum):
    """Types of reports"""    REVENUE = "revenue"
    PROTECTION = "protection"
    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    USER_ANALYTICS = "user_analytics"
    CONTENT_ANALYTICS = "content_analytics"
    PLATFORM_ANALYTICS = "platform_analytics"
    COLLABORATION = "collaboration"
    LICENSING = "licensing"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    AUDIT = "audit"
    FORECAST = "forecast"
    CUSTOM = "custom"


class ReportFormatEnum(str, Enum):
    """Report output formats"""    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    DASHBOARD = "dashboard"
    EMAIL = "email"
    API = "api"


class AnalyticsPeriodEnum(str, Enum):
    """Analytics time periods"""    REALTIME = "realtime"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class MetricTypeEnum(str, Enum):
    """Types of metrics"""    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    RATE = "rate"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    DURATION = "duration"
    CUSTOM = "custom"


class AggregationTypeEnum(str, Enum):
    """Data aggregation types"""    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    DISTINCT_COUNT = "distinct_count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE = "percentile"
    VARIANCE = "variance"
    STANDARD_DEVIATION = "standard_deviation"


class TrendDirectionEnum(str, Enum):
    """Trend directions"""    UP = "up"
    DOWN = "down"
    STABLE = "stable"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"


class DashboardTypeEnum(str, Enum):
    """Types of dashboards"""    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    ANALYTICAL = "analytical"
    STRATEGIC = "strategic"
    REAL_TIME = "real_time"
    CUSTOM = "custom"


class VisualizationTypeEnum(str, Enum):
    """Types of data visualizations"""    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    AREA_CHART = "area_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    TABLE = "table"
    KPI_CARD = "kpi_card"
    FUNNEL = "funnel"
    SANKEY = "sankey"
    TREEMAP = "treemap"
    GAUGE = "gauge"
    MAP = "map"


class MetricDefinitionSchema(BaseModel):
    """Schema for metric definitions"""    metric_id: str = Field(..., description="Unique metric identifier")
    metric_name: str = Field(..., description="Human-readable metric name")
    metric_type: MetricTypeEnum = Field(..., description="Type of metric")
    
    # Metric calculation
    calculation_formula: str = Field(..., description="Metric calculation formula")
    aggregation_type: AggregationTypeEnum = Field(..., description="Aggregation method")
    data_sources: List[str] = Field(..., description="Required data sources")
    
    # Display configuration
    display_name: str = Field(..., description="Display name for UI")
    description: str = Field(..., description="Metric description")
    unit: Optional[str] = Field(None, description="Metric unit (%, $, seconds, etc.)")
    decimal_places: int = Field(2, description="Number of decimal places")
    
    # Thresholds and targets
    target_value: Optional[float] = Field(None, description="Target value")
    warning_threshold: Optional[float] = Field(None, description="Warning threshold")
    critical_threshold: Optional[float] = Field(None, description="Critical threshold")
    
    # Business context
    business_category: str = Field(..., description="Business category")
    importance_score: int = Field(1, ge=1, le=10, description="Importance score (1-10)")
    stakeholders: List[str] = Field(..., description="Interested stakeholders")
    
    # Technical metadata
    refresh_frequency: AnalyticsPeriodEnum = Field(..., description="Data refresh frequency")
    historical_retention: int = Field(365, description="Days to retain historical data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metric_id": "METRIC-REVENUE-001",
                "metric_name": "Monthly Recurring Revenue",
                "metric_type": "currency",
                "calculation_formula": "SUM(monthly_subscriptions)",
                "aggregation_type": "sum",
                "display_name": "MRR",
                "unit": "$",
                "target_value": 50000.0,
                "business_category": "revenue"
            }
        }


class KPISchema(BaseModel):
    """Schema for Key Performance Indicators"""    kpi_id: str = Field(..., description="Unique KPI identifier")
    kpi_name: str = Field(..., description="KPI name")
    metric_id: str = Field(..., description="Associated metric ID")
    
    # Current values
    current_value: float = Field(..., description="Current KPI value")
    previous_value: Optional[float] = Field(None, description="Previous period value")
    target_value: Optional[float] = Field(None, description="Target value")
    benchmark_value: Optional[float] = Field(None, description="Industry benchmark")
    
    # Performance analysis
    change_amount: Optional[float] = Field(None, description="Change from previous period")
    change_percentage: Optional[float] = Field(None, description="Percentage change")
    trend_direction: TrendDirectionEnum = Field(..., description="Trend direction")
    performance_status: str = Field(..., description="Performance status")
    
    # Time context
    measurement_period: AnalyticsPeriodEnum = Field(..., description="Measurement period")
    measurement_date: datetime = Field(..., description="Measurement timestamp")
    comparison_period: Optional[AnalyticsPeriodEnum] = Field(None, description="Comparison period")
    
    # Contextual data
    contributing_factors: Optional[List[str]] = Field(None, description="Contributing factors")
    action_items: Optional[List[str]] = Field(None, description="Recommended actions")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "kpi_id": "KPI-REVENUE-001",
                "kpi_name": "Monthly Revenue Growth",
                "metric_id": "METRIC-REVENUE-001",
                "current_value": 52000.0,
                "previous_value": 48000.0,
                "target_value": 50000.0,
                "change_percentage": 8.33,
                "trend_direction": "up",
                "performance_status": "exceeding_target"
            }
        }


class AnalyticsDataPointSchema(BaseModel):
    """Schema for individual analytics data points"""    timestamp: datetime = Field(..., description="Data point timestamp")
    metric_id: str = Field(..., description="Metric identifier")
    value: float = Field(..., description="Metric value")
    
    # Dimensions and context
    dimensions: Dict[str, str] = Field({}, description="Data dimensions")
    tags: Optional[List[str]] = Field(None, description="Data tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    # Data quality
    confidence_score: Optional[float] = Field(None, description="Data confidence score")
    data_source: str = Field(..., description="Data source identifier")
    collection_method: str = Field(..., description="Data collection method")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-08-24T10:30:00Z",
                "metric_id": "METRIC-ENGAGEMENT-001",
                "value": 15.7,
                "dimensions": {"platform": "youtube", "content_type": "music"},
                "data_source": "platform_api",
                "confidence_score": 0.95
            }
        }


class ReportParametersSchema(BaseModel):
    """Schema for report parameters"""    # Time range
    start_date: date = Field(..., description="Report start date")
    end_date: date = Field(..., description="Report end date")
    period_granularity: AnalyticsPeriodEnum = Field(..., description="Data granularity")
    
    # Filters and dimensions
    filters: Dict[str, Any] = Field({}, description="Report filters")
    dimensions: List[str] = Field([], description="Report dimensions")
    metrics: List[str] = Field(..., description="Metrics to include")
    
    # Grouping and sorting
    group_by: Optional[List[str]] = Field(None, description="Group by fields")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field("desc", description="Sort order (asc/desc)")
    limit: Optional[int] = Field(None, description="Result limit")
    
    # Comparison and benchmarking
    include_comparison: bool = Field(False, description="Include period comparison")
    comparison_period: Optional[AnalyticsPeriodEnum] = Field(None, description="Comparison period")
    include_benchmarks: bool = Field(False, description="Include industry benchmarks")
    
    # Output options
    include_visualizations: bool = Field(True, description="Include charts and graphs")
    include_raw_data: bool = Field(False, description="Include raw data tables")
    include_insights: bool = Field(True, description="Include AI-generated insights")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-07-01",
                "end_date": "2024-07-31",
                "period_granularity": "daily",
                "metrics": ["revenue", "engagement", "protection_events"],
                "filters": {"platform": "all", "content_type": "music"},
                "include_comparison": True,
                "comparison_period": "monthly"
            }
        }


class ReportBaseSchema(BaseModel):
    """Base schema for reports"""    report_type: ReportTypeEnum = Field(..., description="Type of report")
    title: str = Field(..., description="Report title")
    description: Optional[str] = Field(None, description="Report description")
    
    # Report metadata
    generated_by: str = Field(..., description="Report generator (user ID or system)")
    parameters: ReportParametersSchema = Field(..., description="Report parameters")
    
    # Data and content
    executive_summary: Optional[str] = Field(None, description="Executive summary")
    key_insights: List[str] = Field([], description="Key insights")
    recommendations: List[str] = Field([], description="Recommendations")
    
    # Output configuration
    output_format: ReportFormatEnum = Field(..., description="Output format")
    language: str = Field("en", description="Report language")
    branding: Optional[Dict[str, str]] = Field(None, description="Branding configuration")


class ReportCreateSchema(ReportBaseSchema):
    """Schema for creating reports"""    # Scheduling options
    scheduled: bool = Field(False, description="Whether report is scheduled")
    schedule_frequency: Optional[AnalyticsPeriodEnum] = Field(None, description="Schedule frequency")
    schedule_time: Optional[str] = Field(None, description="Schedule time (HH:MM)")
    schedule_timezone: str = Field("UTC", description="Schedule timezone")
    
    # Distribution options
    auto_distribute: bool = Field(False, description="Auto-distribute when generated")
    distribution_list: List[str] = Field([], description="Distribution email list")
    notification_settings: Optional[Dict[str, bool]] = Field(None, description="Notification settings")
    
    # Template and customization
    template_id: Optional[str] = Field(None, description="Report template ID")
    custom_styling: Optional[Dict[str, Any]] = Field(None, description="Custom styling options")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_type": "revenue",
                "title": "Monthly Revenue Report",
                "generated_by": "user_123",
                "output_format": "pdf",
                "scheduled": True,
                "schedule_frequency": "monthly",
                "auto_distribute": True,
                "distribution_list": ["manager@company.com"]
            }
        }


class ReportResponseSchema(ReportBaseSchema):
    """Schema for report responses"""    id: PositiveInt = Field(..., description="Unique report ID")
    report_reference: str = Field(..., description="Human-readable report reference")
    
    # Generation status
    status: str = Field(..., description="Report generation status")
    generation_progress: float = Field(0.0, description="Generation progress (0-1)")
    
    # Output and files
    file_url: Optional[HttpUrl] = Field(None, description="Generated report file URL")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    preview_url: Optional[HttpUrl] = Field(None, description="Report preview URL")
    
    # Data summary
    data_points_count: int = Field(0, description="Number of data points analyzed")
    metrics_count: int = Field(0, description="Number of metrics included")
    time_range_days: int = Field(0, description="Time range in days")
    
    # Performance metrics
    generation_time: Optional[float] = Field(None, description="Generation time in seconds")
    data_freshness: Optional[datetime] = Field(None, description="Data freshness timestamp")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    generated_at: Optional[datetime] = Field(None, description="Generation completion timestamp")
    expires_at: Optional[datetime] = Field(None, description="Report expiration timestamp")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")
    
    # Error handling
    error_message: Optional[str] = Field(None, description="Error message if generation failed")
    warnings: List[str] = Field([], description="Generation warnings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "report_reference": "RPT-2024-001234",
                "report_type": "revenue",
                "title": "Monthly Revenue Report - July 2024",
                "status": "completed",
                "file_url": "https://reports.example.com/rpt-12345.pdf",
                "data_points_count": 15000,
                "generation_time": 45.2,
                "created_at": "2024-08-24T10:30:00Z"
            }
        }


class DashboardWidgetSchema(BaseModel):
    """Schema for dashboard widgets"""    widget_id: str = Field(..., description="Unique widget identifier")
    widget_title: str = Field(..., description="Widget title")
    widget_type: VisualizationTypeEnum = Field(..., description="Widget visualization type")
    
    # Position and sizing
    position_x: int = Field(0, description="X position on dashboard")
    position_y: int = Field(0, description="Y position on dashboard")
    width: int = Field(1, description="Widget width in grid units")
    height: int = Field(1, description="Widget height in grid units")
    
    # Data configuration
    metric_ids: List[str] = Field(..., description="Metrics to display")
    data_filters: Dict[str, Any] = Field({}, description="Data filters")
    time_range: str = Field("last_30_days", description="Time range")
    
    # Display configuration
    display_options: Dict[str, Any] = Field({}, description="Display options")
    color_scheme: Optional[str] = Field(None, description="Color scheme")
    interactive: bool = Field(True, description="Whether widget is interactive")
    
    # Refresh and caching
    refresh_interval: int = Field(300, description="Refresh interval in seconds")
    cache_duration: int = Field(300, description="Cache duration in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "widget_id": "WIDGET-001",
                "widget_title": "Revenue Trend",
                "widget_type": "line_chart",
                "position_x": 0,
                "position_y": 0,
                "width": 2,
                "height": 1,
                "metric_ids": ["METRIC-REVENUE-001"],
                "time_range": "last_30_days"
            }
        }


class DashboardBaseSchema(BaseModel):
    """Base schema for dashboards"""    dashboard_type: DashboardTypeEnum = Field(..., description="Type of dashboard")
    title: str = Field(..., description="Dashboard title")
    description: Optional[str] = Field(None, description="Dashboard description")
    
    # Layout and configuration
    layout_type: str = Field("grid", description="Layout type")
    grid_columns: int = Field(12, description="Number of grid columns")
    widgets: List[DashboardWidgetSchema] = Field([], description="Dashboard widgets")
    
    # Access and permissions
    is_public: bool = Field(False, description="Whether dashboard is public")
    shared_with: List[str] = Field([], description="Users/groups with access")
    
    # Display options
    theme: str = Field("light", description="Dashboard theme")
    auto_refresh: bool = Field(True, description="Auto-refresh dashboard")
    refresh_interval: int = Field(300, description="Refresh interval in seconds")


class DashboardCreateSchema(DashboardBaseSchema):
    """Schema for creating dashboards"""    template_id: Optional[str] = Field(None, description="Dashboard template ID")
    clone_from: Optional[PositiveInt] = Field(None, description="Dashboard ID to clone from")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dashboard_type": "operational",
                "title": "Content Performance Dashboard",
                "description": "Real-time content performance metrics",
                "layout_type": "grid",
                "widgets": [],
                "is_public": False,
                "auto_refresh": True
            }
        }


class DashboardResponseSchema(DashboardBaseSchema):
    """Schema for dashboard responses"""    id: PositiveInt = Field(..., description="Unique dashboard ID")
    dashboard_reference: str = Field(..., description="Human-readable dashboard reference")
    
    # Usage statistics
    view_count: int = Field(0, description="Number of views")
    last_viewed: Optional[datetime] = Field(None, description="Last view timestamp")
    unique_viewers: int = Field(0, description="Number of unique viewers")
    
    # Performance metrics
    load_time: Optional[float] = Field(None, description="Average load time in seconds")
    data_freshness: Optional[datetime] = Field(None, description="Data freshness timestamp")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: str = Field(..., description="Dashboard creator")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 12345,
                "dashboard_reference": "DASH-2024-001234",
                "dashboard_type": "operational",
                "title": "Content Performance Dashboard",
                "view_count": 156,
                "unique_viewers": 23,
                "created_by": "user_123",
                "created_at": "2024-08-24T10:30:00Z"
            }
        }


class AnalyticsInsightSchema(BaseModel):
    """Schema for AI-generated analytics insights"""    insight_id: str = Field(..., description="Unique insight identifier")
    insight_type: str = Field(..., description="Type of insight")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed insight description")
    
    # Insight data
    related_metrics: List[str] = Field(..., description="Related metric IDs")
    significance_score: float = Field(..., ge=0, le=1, description="Insight significance score")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence level")
    
    # Impact and recommendations
    business_impact: str = Field(..., description="Potential business impact")
    recommended_actions: List[str] = Field([], description="Recommended actions")
    urgency_level: str = Field(..., description="Urgency level")
    
    # Context and attribution
    time_period: str = Field(..., description="Time period analyzed")
    data_sources: List[str] = Field(..., description="Data sources used")
    generated_by: str = Field(..., description="AI model or system that generated insight")
    
    # Validation and feedback
    validated: bool = Field(False, description="Whether insight has been validated")
    feedback_score: Optional[float] = Field(None, description="User feedback score")
    
    # Timestamps
    generated_at: datetime = Field(..., description="Generation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Insight expiration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "insight_id": "INS-2024-001234",
                "insight_type": "trend_analysis",
                "title": "Unusual Revenue Spike Detected",
                "description": "Revenue increased by 45% compared to last month...",
                "significance_score": 0.89,
                "confidence_level": 0.95,
                "business_impact": "high_positive",
                "urgency_level": "medium"
            }
        }


class AnalyticsExportSchema(BaseModel):
    """Schema for analytics data exports"""    export_id: str = Field(..., description="Unique export identifier")
    export_type: str = Field(..., description="Type of export")
    data_scope: Dict[str, Any] = Field(..., description="Data scope and filters")
    
    # Export configuration
    format: str = Field(..., description="Export format")
    compression: Optional[str] = Field(None, description="Compression type")
    encryption: bool = Field(False, description="Whether export is encrypted")
    
    # File information
    file_url: Optional[HttpUrl] = Field(None, description="Export file URL")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    record_count: int = Field(0, description="Number of records exported")
    
    # Status and progress
    status: str = Field(..., description="Export status")
    progress: float = Field(0.0, description="Export progress (0-1)")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    
    # Security and access
    access_token: Optional[str] = Field(None, description="Access token for download")
    expires_at: datetime = Field(..., description="Export expiration timestamp")
    download_count: int = Field(0, description="Number of downloads")
    
    # Metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    requested_by: str = Field(..., description="User who requested export")
    
    class Config:
        json_schema_extra = {
            "example": {
                "export_id": "EXP-2024-001234",
                "export_type": "revenue_data",
                "format": "csv",
                "status": "completed",
                "record_count": 10000,
                "file_size": 2048576,
                "expires_at": "2024-08-31T23:59:59Z"
            }
        }


# Export schemas
__all__ = [
    # Enums
    "ReportTypeEnum",
    "ReportFormatEnum",
    "AnalyticsPeriodEnum",
    "MetricTypeEnum",
    "AggregationTypeEnum",
    "TrendDirectionEnum",
    "DashboardTypeEnum",
    "VisualizationTypeEnum",
    
    # Complex schemas
    "MetricDefinitionSchema",
    "KPISchema",
    "AnalyticsDataPointSchema",
    "ReportParametersSchema",
    "DashboardWidgetSchema",
    "AnalyticsInsightSchema",
    "AnalyticsExportSchema",
    
    # Main schemas
    "ReportBaseSchema",
    "ReportCreateSchema",
    "ReportResponseSchema",
    "DashboardBaseSchema",
    "DashboardCreateSchema",
    "DashboardResponseSchema"
]
