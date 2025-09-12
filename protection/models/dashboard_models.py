"""
Dashboard Models - Protection System
===================================

Dashboard and UI data models for the protection system.

🧠 Lead Dev IA: Advanced dashboard intelligence and interactive analytics
🏗️ Backend Senior: Scalable dashboard data architecture with real-time updates
🤖 ML Engineer: Predictive dashboard insights and behavioral analytics
🗄️ DBA: Optimized dashboard queries and efficient data aggregation
🔒 Sécurité: Secure dashboard data access and permission-based views
🌐 Microservices: Distributed dashboard services with real-time synchronization
🎵 Audio Engineer: Audio analytics dashboards and acoustic metrics visualization
⚙️ DevOps: Dashboard performance monitoring and auto-scaling infrastructure
💡 IA Prompt Engineer: AI-generated dashboard insights and intelligent recommendations

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚖️ LEGAL NOTICE: This code is proprietary and protected by copyright law.
Unauthorized use, reproduction, or distribution is strictly prohibited.
Contact mlaiel@live.de for licensing inquiries.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from .base_models import BaseModel

class WidgetType(Enum):
    """Dashboard widget types"""
    CHART = "chart"
    METRIC = "metric"
    TABLE = "table"
    MAP = "map"
    ALERT = "alert"
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"

class ChartType(Enum):
    """Chart widget subtypes"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    RADAR = "radar"

class MetricType(Enum):
    """Metric display types"""
    NUMBER = "number"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"
    DURATION = "duration"
    BYTES = "bytes"

@dataclass
class TimeSeriesData:
    """Time series data point for charts"""
    # Required fields first
    timestamp: datetime
    value: Union[int, float]
    
    # Base model fields with defaults
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Optional fields with defaults
    label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChartConfiguration:
    """Chart display configuration"""
    chart_type: ChartType
    x_axis_label: str
    y_axis_label: str
    title: str
    colors: List[str] = field(default_factory=list)
    show_legend: bool = True
    show_grid: bool = True
    interactive: bool = True

@dataclass
class MetricConfiguration:
    """Metric display configuration"""
    metric_type: MetricType
    unit: Optional[str] = None
    format_string: Optional[str] = None
    threshold_low: Optional[float] = None
    threshold_high: Optional[float] = None
    color_good: str = "#28a745"
    color_warning: str = "#ffc107"
    color_danger: str = "#dc3545"

@dataclass
class DashboardWidget:
    """Individual dashboard widget"""
    # Required fields first
    title: str
    widget_type: WidgetType
    position_x: int
    position_y: int
    data_source: str
    
    # Base model fields with defaults
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Optional fields with defaults
    width: int = 4
    height: int = 3
    
    # Configuration based on widget type
    chart_config: Optional[ChartConfiguration] = None
    metric_config: Optional[MetricConfiguration] = None
    
    # Data source configuration
    data_source: str
    query_params: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: int = 30  # seconds
    
    # Display settings
    background_color: Optional[str] = None
    border_color: Optional[str] = None
    text_color: Optional[str] = None
    
    # Permissions
    required_permissions: List[str] = field(default_factory=list)
    visible_roles: List[str] = field(default_factory=list)

@dataclass
class DashboardLayout:
    """Dashboard layout configuration"""
    # Required fields
    name: str
    owner_id: str
    
    # Base model fields with defaults  
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Optional fields with defaults
    description: Optional[str] = None
    widgets: List[DashboardWidget] = field(default_factory=list)
    
    # Layout settings
    grid_columns: int = 12
    grid_row_height: int = 100
    margin: int = 10
    
    # Theme settings
    theme: str = "default"
    background_color: str = "#ffffff"
    
    # Access control
    owner_id: str
    shared_with: List[str] = field(default_factory=list)
    is_public: bool = False
    
    # Auto-refresh settings
    auto_refresh: bool = True
    refresh_interval: int = 60  # seconds

@dataclass
class UserPreferences:
    """User dashboard preferences"""
    user_id: str
    default_layout_id: Optional[str] = None
    
    # Display preferences
    theme: str = "default"
    timezone: str = "UTC"
    date_format: str = "YYYY-MM-DD"
    time_format: str = "24h"
    
    # Notification preferences
    email_notifications: bool = True
    desktop_notifications: bool = True
    mobile_notifications: bool = True
    
    # Feature preferences
    auto_refresh: bool = True
    show_tooltips: bool = True
    compact_mode: bool = False
    
    # Language and localization
    language: str = "en"
    currency: str = "USD"

@dataclass
class AlertMetrics:
    """Alert-related metrics for dashboard"""
    total_alerts: int = 0
    critical_alerts: int = 0
    high_alerts: int = 0
    medium_alerts: int = 0
    low_alerts: int = 0
    resolved_alerts: int = 0
    pending_alerts: int = 0
    
    # Time-based metrics
    alerts_last_hour: int = 0
    alerts_last_24h: int = 0
    alerts_last_week: int = 0
    
    # Performance metrics
    avg_resolution_time: Optional[float] = None  # minutes
    false_positive_rate: Optional[float] = None
    escalation_rate: Optional[float] = None

@dataclass
class PlatformMetrics:
    """Platform-wide metrics for dashboard"""
    
    # Content metrics
    total_content_items: int = 0
    protected_items: int = 0
    monitored_platforms: int = 0
    
    # Detection metrics
    violations_detected: int = 0
    takedowns_successful: int = 0
    revenue_protected: float = 0.0
    
    # Performance metrics
    processing_speed: float = 0.0  # items per hour
    system_uptime: float = 0.0  # percentage
    api_response_time: float = 0.0  # milliseconds
    
    # Financial metrics
    revenue_generated: float = 0.0
    costs_saved: float = 0.0
    roi_percentage: float = 0.0

@dataclass
class DashboardMetrics:
    """Combined dashboard metrics"""
    alert_metrics: AlertMetrics = field(default_factory=AlertMetrics)
    platform_metrics: PlatformMetrics = field(default_factory=PlatformMetrics)
    
    # Additional KPIs
    user_satisfaction: Optional[float] = None
    system_efficiency: Optional[float] = None
    threat_level: str = "normal"
    
    # Temporal data
    historical_data: List[TimeSeriesData] = field(default_factory=list)
    trend_direction: str = "stable"  # up, down, stable
    
    def get_overall_health_score(self) -> float:
        """Calculate overall system health score (0-100)"""
        # 🧠 Lead Dev IA: Intelligent health scoring algorithm
        score = 100.0
        
        # Reduce score based on alert severity
        if self.alert_metrics.critical_alerts > 0:
            score -= min(self.alert_metrics.critical_alerts * 10, 30)
        if self.alert_metrics.high_alerts > 0:
            score -= min(self.alert_metrics.high_alerts * 5, 20)
        
        # Adjust for system performance
        if self.platform_metrics.system_uptime < 99.0:
            score -= (99.0 - self.platform_metrics.system_uptime) * 2
        
        # Adjust for response time
        if self.platform_metrics.api_response_time > 1000:  # > 1 second
            score -= min((self.platform_metrics.api_response_time - 1000) / 100, 15)
        
        return max(0.0, min(100.0, score))

@dataclass
class DashboardState:
    """Current dashboard state and cached data"""
    layout_id: str
    user_id: str
    
    # Cached widget data
    widget_data: Dict[str, Any] = field(default_factory=dict)
    last_refresh: Dict[str, datetime] = field(default_factory=dict)
    
    # Real-time state
    active_filters: Dict[str, Any] = field(default_factory=dict)
    selected_time_range: str = "1h"
    auto_refresh_enabled: bool = True
    
    # Performance tracking
    load_times: Dict[str, float] = field(default_factory=dict)
    error_count: int = 0
    last_error: Optional[str] = None

# 🛡️ Enterprise Dashboard Security Model
@dataclass
class DashboardSecurity:
    """Dashboard security and access control"""
    dashboard_id: str
    
    # Access permissions
    read_permissions: List[str] = field(default_factory=list)
    write_permissions: List[str] = field(default_factory=list)
    admin_permissions: List[str] = field(default_factory=list)
    
    # Data sensitivity levels
    data_classification: str = "internal"  # public, internal, confidential, restricted
    pii_present: bool = False
    financial_data: bool = False
    
    # Audit trail
    access_log: List[Dict[str, Any]] = field(default_factory=list)
    modification_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # Security settings
    session_timeout: int = 3600  # seconds
    require_mfa: bool = False
    ip_whitelist: List[str] = field(default_factory=list)