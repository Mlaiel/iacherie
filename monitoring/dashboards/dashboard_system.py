"""
Ainflue Platform - Enterprise Dashboard System
==============================================

Real-time enterprise dashboards with interactive visualizations for
audio processing, content protection, monetization, collaboration,
and comprehensive business intelligence monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class DashboardType(Enum):
    """Types of enterprise dashboards."""
    EXECUTIVE_OVERVIEW = "executive_overview"
    AUDIO_PROCESSING = "audio_processing"
    CONTENT_PROTECTION = "content_protection"
    MONETIZATION = "monetization"
    COLLABORATION = "collaboration"
    GAMIFICATION = "gamification"
    SEO_OPTIMIZATION = "seo_optimization"
    DISTRIBUTION = "distribution"
    ANALYTICS = "analytics"
    REAL_TIME_OPERATIONS = "real_time_operations"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    # === CREATOR ECONOMY DASHBOARD TYPES ===
    CREATOR_ECONOMY_OVERVIEW = "creator_economy_overview"
    CREATOR_ANALYTICS = "creator_analytics"
    CREATOR_COLLABORATION = "creator_collaboration"
    CREATOR_MONETIZATION = "creator_monetization" 
    CREATOR_TIER_PROGRESSION = "creator_tier_progression"
    MULTI_FORMAT_CONTENT = "multi_format_content"
    GAMIFICATION_ENGAGEMENT = "gamification_engagement"
    CROSS_PLATFORM_DISTRIBUTION = "cross_platform_distribution"
    CREATOR_PERFORMANCE_INTELLIGENCE = "creator_performance_intelligence"

class VisualizationType(Enum):
    """Types of visualizations available."""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    KPI_CARD = "kpi_card"
    TABLE = "table"
    TREEMAP = "treemap"
    SANKEY = "sankey"
    GEOGRAPHIC_MAP = "geographic_map"
    REAL_TIME_STREAM = "real_time_stream"

class UpdateFrequency(Enum):
    """Dashboard update frequencies."""
    REAL_TIME = "real_time"        # 1-5 seconds
    HIGH_FREQUENCY = "high_frequency"  # 30 seconds
    MEDIUM_FREQUENCY = "medium_frequency"  # 5 minutes
    LOW_FREQUENCY = "low_frequency"    # 30 minutes
    HOURLY = "hourly"              # 1 hour
    DAILY = "daily"                # 24 hours

@dataclass
class DashboardWidget:
    """Individual dashboard widget configuration."""
    widget_id: str
    title: str
    visualization_type: VisualizationType
    data_source: str
    query: str
    update_frequency: UpdateFrequency
    position: Dict[str, int]  # x, y, width, height
    configuration: Dict[str, Any]
    filters: List[Dict[str, Any]] = field(default_factory=list)
    alerts_enabled: bool = True
    cache_duration_seconds: int = 300

@dataclass
class Dashboard:
    """Enterprise dashboard configuration."""
    dashboard_id: str
    name: str
    description: str
    dashboard_type: DashboardType
    owner: str
    role_permissions: List[str]
    widgets: List[DashboardWidget]
    layout_config: Dict[str, Any]
    theme_config: Dict[str, Any]
    auto_refresh: bool
    refresh_interval_seconds: int
    is_public: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed: Optional[datetime] = None

@dataclass
class DashboardMetrics:
    """Dashboard performance and usage metrics."""
    dashboard_id: str
    load_time_ms: float
    user_sessions: int
    unique_viewers: int
    total_views: int
    average_session_duration_minutes: float
    bounce_rate: float
    widget_interaction_count: int
    error_count: int
    timestamp: datetime = field(default_factory=datetime.utcnow)

class EnterpriseDashboardSystem:
    """
    Enterprise dashboard system for Ainflue platform monitoring.
    
    Features:
    - Real-time interactive dashboards for all monitoring aspects
    - Role-based access control and personalization
    - Advanced visualizations with drill-down capabilities
    - Automated alert integration and notification
    - Performance optimization and caching
    - Mobile-responsive design and offline capability
    - Export and sharing functionality
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.dashboards: Dict[str, Dashboard] = {}
        self.dashboard_metrics: deque = deque(maxlen=100000)
        self.data_sources = self._initialize_data_sources()
        self.theme_templates = self._initialize_theme_templates()
        self.widget_templates = self._initialize_widget_templates()
        self._create_default_dashboards()
        
        logger.info("Enterprise Dashboard System initialized")
    
    def _initialize_data_sources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize available data sources for dashboard widgets."""
        return {
            'audio_processing_metrics': {
                'endpoint': '/monitoring/audio_processing/statistics',
                'cache_duration': 60,
                'fields': ['processing_time', 'quality_score', 'throughput', 'error_rate']
            },
            'content_protection_alerts': {
                'endpoint': '/monitoring/content_protection/statistics',
                'cache_duration': 30,
                'fields': ['copyright_matches', 'piracy_incidents', 'takedown_requests']
            },
            'monetization_revenue': {
                'endpoint': '/monitoring/monetization/statistics',
                'cache_duration': 300,
                'fields': ['revenue', 'transactions', 'conversion_rate', 'arpu']
            },
            'collaboration_activity': {
                'endpoint': '/monitoring/collaboration/statistics',
                'cache_duration': 120,
                'fields': ['active_collaborations', 'match_success_rate', 'user_engagement']
            },
            'system_performance': {
                'endpoint': '/monitoring/performance/statistics',
                'cache_duration': 30,
                'fields': ['cpu_usage', 'memory_usage', 'response_time', 'uptime']
            },
            'user_analytics': {
                'endpoint': '/monitoring/analytics/user_behavior',
                'cache_duration': 180,
                'fields': ['active_users', 'session_duration', 'feature_usage', 'retention']
            },
            'business_kpis': {
                'endpoint': '/monitoring/business/kpis',
                'cache_duration': 600,
                'fields': ['total_revenue', 'user_growth', 'content_processed', 'platform_health']
            },
            # === CREATOR ECONOMY DASHBOARD ENHANCEMENTS ===
            'creator_economy_metrics': {
                'endpoint': '/monitoring/creator_economy/metrics',
                'cache_duration': 120,
                'fields': ['active_creators', 'creator_tier_distribution', 'average_creator_revenue', 'creator_growth_rate', 'collaboration_success_rate']
            },
            'creator_performance_analytics': {
                'endpoint': '/monitoring/creator_economy/performance',
                'cache_duration': 180,
                'fields': ['content_quality_score', 'engagement_rates', 'cross_platform_reach', 'monetization_efficiency']
            },
            'creator_collaboration_insights': {
                'endpoint': '/monitoring/creator_economy/collaboration',
                'cache_duration': 300,
                'fields': ['collaboration_matches', 'partnership_success_rate', 'creator_network_density', 'collaboration_revenue']
            },
            'creator_tier_progression': {
                'endpoint': '/monitoring/creator_economy/tiers',
                'cache_duration': 600,
                'fields': ['tier_distributions', 'progression_rates', 'tier_benefits_usage', 'upgrade_patterns']
            },
            'multi_format_content_analytics': {
                'endpoint': '/monitoring/creator_economy/content',
                'cache_duration': 240,
                'fields': ['content_type_performance', 'format_optimization_scores', 'cross_format_engagement', 'ai_enhancement_usage']
            },
            'gamification_engagement_metrics': {
                'endpoint': '/monitoring/creator_economy/gamification',
                'cache_duration': 150,
                'fields': ['achievement_completion_rates', 'leaderboard_activity', 'challenge_participation', 'reward_redemption']
            },
            'cross_platform_distribution_analytics': {
                'endpoint': '/monitoring/creator_economy/distribution',
                'cache_duration': 200,
                'fields': ['platform_performance', 'cross_platform_synergy', 'distribution_optimization', 'audience_correlation']
            }
        }
    
    def _initialize_theme_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize dashboard theme templates."""
        return {
            'ainflue_dark': {
                'primary_color': '#1a1a2e',
                'secondary_color': '#16213e',
                'accent_color': '#0f3460',
                'text_color': '#ffffff',
                'success_color': '#00ff88',
                'warning_color': '#ff6b35',
                'error_color': '#ff0040',
                'font_family': 'Inter, sans-serif'
            },
            'ainflue_light': {
                'primary_color': '#ffffff',
                'secondary_color': '#f8f9fa',
                'accent_color': '#007bff',
                'text_color': '#333333',
                'success_color': '#28a745',
                'warning_color': '#ffc107',
                'error_color': '#dc3545',
                'font_family': 'Inter, sans-serif'
            },
            'professional': {
                'primary_color': '#2c3e50',
                'secondary_color': '#34495e',
                'accent_color': '#3498db',
                'text_color': '#ecf0f1',
                'success_color': '#2ecc71',
                'warning_color': '#f39c12',
                'error_color': '#e74c3c',
                'font_family': 'Roboto, sans-serif'
            }
        }
    
    def _initialize_widget_templates(self) -> Dict[str, DashboardWidget]:
        """Initialize common widget templates."""
        templates = {}
        
        # Audio Processing KPI Card
        templates['audio_processing_kpi'] = DashboardWidget(
            widget_id='template_audio_kpi',
            title='Audio Processing Performance',
            visualization_type=VisualizationType.KPI_CARD,
            data_source='audio_processing_metrics',
            query='SELECT AVG(processing_time) as avg_time, SUM(files_processed) as total_files FROM audio_metrics WHERE timestamp >= NOW() - INTERVAL 1 HOUR',
            update_frequency=UpdateFrequency.HIGH_FREQUENCY,
            position={'x': 0, 'y': 0, 'width': 4, 'height': 2},
            configuration={
                'metrics': [
                    {'name': 'Average Processing Time', 'field': 'avg_time', 'unit': 'ms', 'format': '0.2f'},
                    {'name': 'Files Processed', 'field': 'total_files', 'unit': '', 'format': '0,0'}
                ],
                'thresholds': {'warning': 5000, 'critical': 10000}
            }
        )
        
        # === CREATOR ECONOMY DASHBOARD WIDGET TEMPLATES ===
        
        # Creator Economy Overview KPI
        templates['creator_economy_overview_kpi'] = DashboardWidget(
            widget_id='template_creator_economy_kpi',
            title='Creator Economy Overview',
            visualization_type=VisualizationType.KPI_CARD,
            data_source='creator_economy_metrics',
            query='SELECT COUNT(*) as active_creators, AVG(revenue) as avg_revenue, SUM(content_created) as total_content FROM creator_metrics WHERE timestamp >= NOW() - INTERVAL 24 HOUR',
            update_frequency=UpdateFrequency.MEDIUM_FREQUENCY,
            position={'x': 0, 'y': 0, 'width': 6, 'height': 3},
            configuration={
                'metrics': [
                    {'name': 'Active Creators', 'field': 'active_creators', 'unit': '', 'format': '0,0'},
                    {'name': 'Average Creator Revenue', 'field': 'avg_revenue', 'unit': '$', 'format': '0,0.00'},
                    {'name': 'Content Created Today', 'field': 'total_content', 'unit': '', 'format': '0,0'}
                ],
                'thresholds': {'revenue_warning': 100, 'revenue_excellent': 1000}
            }
        )
        
        # Creator Tier Distribution Chart
        templates['creator_tier_distribution'] = DashboardWidget(
            widget_id='template_tier_distribution',
            title='Creator Tier Distribution',
            visualization_type=VisualizationType.PIE_CHART,
            data_source='creator_tier_progression',
            query='SELECT tier, COUNT(*) as count FROM creator_tiers GROUP BY tier',
            update_frequency=UpdateFrequency.HOURLY,
            position={'x': 6, 'y': 0, 'width': 6, 'height': 4},
            configuration={
                'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'],
                'show_labels': True,
                'show_legend': True,
                'animate': True
            }
        )
        
        # Real-time Creator Analytics
        templates['real_time_creator_analytics'] = DashboardWidget(
            widget_id='template_realtime_creator',
            title='Real-time Creator Activity',
            visualization_type=VisualizationType.REAL_TIME_STREAM,
            data_source='creator_performance_analytics',
            query='SELECT timestamp, creator_id, engagement_rate, content_views FROM creator_activity WHERE timestamp >= NOW() - INTERVAL 1 HOUR ORDER BY timestamp DESC',
            update_frequency=UpdateFrequency.REAL_TIME,
            position={'x': 0, 'y': 3, 'width': 12, 'height': 4},
            configuration={
                'max_items': 100,
                'auto_scroll': True,
                'highlight_anomalies': True,
                'stream_type': 'creator_activity'
            }
        )
        
        # Multi-format Content Performance
        templates['multi_format_content_chart'] = DashboardWidget(
            widget_id='template_content_format',
            title='Multi-format Content Performance',
            visualization_type=VisualizationType.BAR_CHART,
            data_source='multi_format_content_analytics',
            query='SELECT content_type, AVG(engagement_rate) as avg_engagement, SUM(views) as total_views FROM content_analytics GROUP BY content_type',
            update_frequency=UpdateFrequency.MEDIUM_FREQUENCY,
            position={'x': 0, 'y': 7, 'width': 8, 'height': 5},
            configuration={
                'x_axis': 'content_type',
                'y_axis': 'avg_engagement',
                'color_scheme': 'creator_economy',
                'show_grid': True,
                'animate_bars': True
            }
        )
        
        # Collaboration Network Heatmap
        templates['collaboration_heatmap'] = DashboardWidget(
            widget_id='template_collaboration_heatmap',
            title='Creator Collaboration Network',
            visualization_type=VisualizationType.HEATMAP,
            data_source='creator_collaboration_insights',
            query='SELECT creator_a, creator_b, collaboration_strength FROM collaboration_matrix WHERE timestamp >= NOW() - INTERVAL 7 DAY',
            update_frequency=UpdateFrequency.HOURLY,
            position={'x': 8, 'y': 7, 'width': 4, 'height': 5},
            configuration={
                'color_scale': 'viridis',
                'show_values': True,
                'cluster_similar': True
            }
        )
        
        # Gamification Engagement Gauge
        templates['gamification_gauge'] = DashboardWidget(
            widget_id='template_gamification_gauge',
            title='Platform Engagement Score',
            visualization_type=VisualizationType.GAUGE,
            data_source='gamification_engagement_metrics',
            query='SELECT AVG(engagement_score) as score FROM gamification_metrics WHERE timestamp >= NOW() - INTERVAL 1 HOUR',
            update_frequency=UpdateFrequency.HIGH_FREQUENCY,
            position={'x': 0, 'y': 12, 'width': 4, 'height': 4},
            configuration={
                'min_value': 0,
                'max_value': 100,
                'thresholds': [
                    {'value': 30, 'color': '#FF4444', 'label': 'Low'},
                    {'value': 70, 'color': '#FFA500', 'label': 'Medium'},
                    {'value': 100, 'color': '#00FF00', 'label': 'High'}
                ],
                'show_needle': True,
                'animate': True
            }
        )
        
        # Cross-platform Distribution Analytics
        templates['cross_platform_analytics'] = DashboardWidget(
            widget_id='template_cross_platform',
            title='Cross-platform Performance',
            visualization_type=VisualizationType.LINE_CHART,
            data_source='cross_platform_distribution_analytics',
            query='SELECT DATE(timestamp) as date, platform, SUM(reach) as total_reach FROM distribution_analytics WHERE timestamp >= NOW() - INTERVAL 30 DAY GROUP BY DATE(timestamp), platform',
            update_frequency=UpdateFrequency.HOURLY,
            position={'x': 4, 'y': 12, 'width': 8, 'height': 4},
            configuration={
                'x_axis': 'date',
                'y_axis': 'total_reach',
                'group_by': 'platform',
                'show_points': True,
                'smooth_lines': True,
                'fill_area': False
            }
        )
        
        return templates
    
    def _create_default_dashboards(self):
        """Create default enterprise dashboards."""
        # Executive Overview Dashboard
        exec_dashboard = self._create_executive_dashboard()
        self.dashboards[exec_dashboard.dashboard_id] = exec_dashboard
        
        # Audio Processing Dashboard
        audio_dashboard = self._create_audio_processing_dashboard()
        self.dashboards[audio_dashboard.dashboard_id] = audio_dashboard
        
        # === CREATOR ECONOMY DASHBOARDS ===
        
        # Creator Economy Overview Dashboard
        creator_overview_dashboard = self._create_creator_economy_overview_dashboard()
        self.dashboards[creator_overview_dashboard.dashboard_id] = creator_overview_dashboard
        
        # Creator Analytics Dashboard  
        creator_analytics_dashboard = self._create_creator_analytics_dashboard()
        self.dashboards[creator_analytics_dashboard.dashboard_id] = creator_analytics_dashboard
        
        # Multi-format Content Dashboard
        content_dashboard = self._create_multi_format_content_dashboard()
        self.dashboards[content_dashboard.dashboard_id] = content_dashboard
    
    def _create_executive_dashboard(self) -> Dashboard:
        """Create executive overview dashboard."""
        widgets = []
        
        # Revenue KPI
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            title='Total Revenue (24h)',
            visualization_type=VisualizationType.KPI_CARD,
            data_source='business_kpis',
            query='SELECT SUM(revenue) as total_revenue FROM revenue_metrics WHERE timestamp >= NOW() - INTERVAL 24 HOURS',
            update_frequency=UpdateFrequency.MEDIUM_FREQUENCY,
            position={'x': 0, 'y': 0, 'width': 3, 'height': 2},
            configuration={
                'primary_metric': 'total_revenue',
                'format': '$0,0.00',
                'trend_comparison': 'previous_day',
                'color_scheme': 'success'
            }
        ))
        
        return Dashboard(
            dashboard_id=str(uuid.uuid4()),
            name='Executive Overview',
            description='High-level business metrics and KPIs for executive decision making',
            dashboard_type=DashboardType.EXECUTIVE_OVERVIEW,
            owner='system',
            role_permissions=['executive', 'admin', 'manager'],
            widgets=widgets,
            layout_config={'columns': 12, 'row_height': 60},
            theme_config=self.theme_templates['ainflue_dark'],
            auto_refresh=True,
            refresh_interval_seconds=300
        )
    
    def _create_audio_processing_dashboard(self) -> Dashboard:
        """Create audio processing monitoring dashboard."""
        widgets = []
        
        # Processing Queue Status
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            title='Processing Queue Status',
            visualization_type=VisualizationType.KPI_CARD,
            data_source='audio_processing_metrics',
            query='SELECT COUNT(*) as queue_length, AVG(wait_time) as avg_wait FROM processing_queue WHERE status = \'pending\'',
            update_frequency=UpdateFrequency.REAL_TIME,
            position={'x': 0, 'y': 0, 'width': 3, 'height': 2},
            configuration={
                'metrics': [
                    {'name': 'Queue Length', 'field': 'queue_length', 'format': '0,0'},
                    {'name': 'Avg Wait Time', 'field': 'avg_wait', 'unit': 'sec', 'format': '0.1f'}
                ]
            }
        ))
        
        return Dashboard(
            dashboard_id=str(uuid.uuid4()),
            name='Audio Processing Monitor',
            description='Real-time monitoring of audio processing workflows and performance',
            dashboard_type=DashboardType.AUDIO_PROCESSING,
            owner='system',
            role_permissions=['engineer', 'admin', 'operator'],
            widgets=widgets,
            layout_config={'columns': 12, 'row_height': 60},
            theme_config=self.theme_templates['professional'],
            auto_refresh=True,
            refresh_interval_seconds=30
        )
    
    def get_dashboard_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get dashboard usage analytics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_metrics = [
            metrics for metrics in self.dashboard_metrics
            if metrics.timestamp >= cutoff_time
        ]
        
        if not recent_metrics:
            return {"message": f"No dashboard usage data in last {hours} hours"}
        
        return {
            'period_hours': hours,
            'total_dashboard_views': sum(m.total_views for m in recent_metrics),
            'active_dashboards': len(self.dashboards),
            'avg_load_time_ms': statistics.mean([m.load_time_ms for m in recent_metrics]) if recent_metrics else 0
        }
    
    # === CREATOR ECONOMY DASHBOARD CREATION METHODS ===
    
    def _create_creator_economy_overview_dashboard(self) -> Dashboard:
        """Create Creator Economy overview dashboard."""
        widgets = []
        
        # Creator Economy KPI Card
        widgets.append(self.widget_templates['creator_economy_overview_kpi'])
        
        # Creator Tier Distribution
        widgets.append(self.widget_templates['creator_tier_distribution'])
        
        # Gamification Engagement Gauge
        widgets.append(self.widget_templates['gamification_gauge'])
        
        return Dashboard(
            dashboard_id=str(uuid.uuid4()),
            name='Creator Economy Overview',
            description='Comprehensive overview of Creator Economy metrics, tier distributions, and engagement analytics',
            dashboard_type=DashboardType.CREATOR_ECONOMY_OVERVIEW,
            owner='system',
            role_permissions=['creator', 'admin', 'manager', 'analyst'],
            widgets=widgets,
            layout_config={'columns': 12, 'row_height': 60},
            theme_config=self.theme_templates['ainflue_dark'],
            auto_refresh=True,
            refresh_interval_seconds=120
        )
    
    def _create_creator_analytics_dashboard(self) -> Dashboard:
        """Create Creator Analytics dashboard."""
        widgets = []
        
        # Real-time Creator Analytics Stream
        widgets.append(self.widget_templates['real_time_creator_analytics'])
        
        # Cross-platform Analytics
        widgets.append(self.widget_templates['cross_platform_analytics'])
        
        # Collaboration Network Heatmap
        widgets.append(self.widget_templates['collaboration_heatmap'])
        
        return Dashboard(
            dashboard_id=str(uuid.uuid4()),
            name='Creator Analytics Dashboard',
            description='Real-time creator performance analytics with cross-platform insights and collaboration network analysis',
            dashboard_type=DashboardType.CREATOR_ANALYTICS,
            owner='system',
            role_permissions=['creator', 'admin', 'analyst', 'data_scientist'],
            widgets=widgets,
            layout_config={'columns': 12, 'row_height': 60},
            theme_config=self.theme_templates['professional'],
            auto_refresh=True,
            refresh_interval_seconds=60
        )
    
    def _create_multi_format_content_dashboard(self) -> Dashboard:
        """Create Multi-format Content dashboard."""
        widgets = []
        
        # Multi-format Content Performance Chart
        widgets.append(self.widget_templates['multi_format_content_chart'])
        
        # Content Quality KPI
        widgets.append(DashboardWidget(
            widget_id=str(uuid.uuid4()),
            title='Content Quality Metrics',
            visualization_type=VisualizationType.KPI_CARD,
            data_source='multi_format_content_analytics',
            query='SELECT AVG(quality_score) as avg_quality, COUNT(*) as total_content, AVG(ai_enhancement_score) as ai_score FROM content_quality WHERE timestamp >= NOW() - INTERVAL 24 HOUR',
            update_frequency=UpdateFrequency.MEDIUM_FREQUENCY,
            position={'x': 8, 'y': 0, 'width': 4, 'height': 5},
            configuration={
                'metrics': [
                    {'name': 'Average Quality Score', 'field': 'avg_quality', 'unit': '/100', 'format': '0.1f'},
                    {'name': 'Content Processed', 'field': 'total_content', 'unit': '', 'format': '0,0'},
                    {'name': 'AI Enhancement Score', 'field': 'ai_score', 'unit': '/100', 'format': '0.1f'}
                ],
                'thresholds': {'quality_excellent': 85, 'quality_good': 70}
            }
        ))
        
        return Dashboard(
            dashboard_id=str(uuid.uuid4()),
            name='Multi-format Content Dashboard',
            description='AI-powered multi-format content analysis with quality metrics and optimization insights',
            dashboard_type=DashboardType.MULTI_FORMAT_CONTENT,
            owner='system',
            role_permissions=['creator', 'content_manager', 'admin', 'quality_analyst'],
            widgets=widgets,
            layout_config={'columns': 12, 'row_height': 60},
            theme_config=self.theme_templates['ainflue_light'],
            auto_refresh=True,
            refresh_interval_seconds=180
        )

# Global enterprise dashboard system instance
enterprise_dashboard_system = EnterpriseDashboardSystem()

# Export main components
__all__ = [
    'EnterpriseDashboardSystem',
    'Dashboard',
    'DashboardWidget',
    'DashboardMetrics',
    'DashboardType',
    'VisualizationType',
    'UpdateFrequency',
    'enterprise_dashboard_system'
]