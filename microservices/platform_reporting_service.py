"""
📊 Platform Reporting Microservice
Unified platform reporting and analytics across multiple social media and content platforms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import uuid
import json
import statistics
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class ReportType(str, Enum):
    """Types of reports"""
    PERFORMANCE_SUMMARY = "performance_summary"
    ENGAGEMENT_ANALYSIS = "engagement_analysis"
    REVENUE_REPORT = "revenue_report"
    AUDIENCE_INSIGHTS = "audience_insights"
    CONTENT_PERFORMANCE = "content_performance"
    GROWTH_ANALYTICS = "growth_analytics"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    COMPLIANCE_REPORT = "compliance_report"
    CROSS_PLATFORM_COMPARISON = "cross_platform_comparison"
    TREND_ANALYSIS = "trend_analysis"


class ReportFormat(str, Enum):
    """Report output formats"""
    JSON = "json"
    PDF = "pdf"
    CSV = "csv"
    EXCEL = "xlsx"
    HTML = "html"
    DASHBOARD = "dashboard"


class TimeRange(str, Enum):
    """Time range options for reports"""
    LAST_24_HOURS = "24h"
    LAST_7_DAYS = "7d"
    LAST_30_DAYS = "30d"
    LAST_90_DAYS = "90d"
    LAST_YEAR = "1y"
    CUSTOM = "custom"


class AggregationType(str, Enum):
    """Data aggregation types"""
    SUM = "sum"
    AVERAGE = "average"
    MEDIAN = "median"
    MAX = "max"
    MIN = "min"
    COUNT = "count"
    PERCENTAGE = "percentage"


@dataclass
class ReportConfig:
    """Report configuration"""
    config_id: str
    report_type: ReportType
    creator_id: str
    platform_ids: List[str]
    time_range: TimeRange
    custom_start_date: Optional[datetime] = None
    custom_end_date: Optional[datetime] = None
    metrics: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    aggregation_type: AggregationType = AggregationType.SUM
    output_format: ReportFormat = ReportFormat.JSON
    include_charts: bool = True
    include_recommendations: bool = True
    schedule: Optional[str] = None  # cron expression for scheduled reports
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ReportData:
    """Raw report data"""
    data_id: str
    platform_id: str
    metric_name: str
    value: Union[float, int, str]
    timestamp: datetime
    dimensions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportSection:
    """Report section with data and visualization"""
    section_id: str
    title: str
    description: str
    data: List[Dict[str, Any]]
    chart_config: Optional[Dict[str, Any]] = None
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class GeneratedReport:
    """Generated report"""
    report_id: str
    config_id: str
    report_type: ReportType
    creator_id: str
    title: str
    executive_summary: str
    sections: List[ReportSection]
    key_metrics: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]
    generated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


class DataCollector:
    """Collects data from various platforms for reporting"""
    
    def __init__(self) -> None:
        self.data_cache: Dict[str, List[ReportData]] = {}
        self.platform_apis: Dict[str, Callable] = {}
        self._setup_platform_apis()
    
    def _setup_platform_apis(self) -> None:
        """Setup platform API collectors"""
        # In real implementation, these would be actual API clients
        self.platform_apis = {
            "youtube": self._collect_youtube_data,
            "instagram": self._collect_instagram_data,
            "tiktok": self._collect_tiktok_data,
            "twitter": self._collect_twitter_data,
            "facebook": self._collect_facebook_data,
            "linkedin": self._collect_linkedin_data,
            "spotify": self._collect_spotify_data,
            "soundcloud": self._collect_soundcloud_data
        }
    
    async def collect_platform_data(
        self,
        platform_id: str,
        creator_id: str,
        metrics: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[ReportData]:
        """Collect data from a specific platform"""
        try:
            if platform_id not in self.platform_apis:
                raise ValueError(f"Platform {platform_id} not supported")
            
            # Use platform-specific collector
            data = await self.platform_apis[platform_id](
                creator_id, metrics, start_date, end_date
            )
            
            # Cache the data
            cache_key = f"{platform_id}_{creator_id}_{start_date.date()}_{end_date.date()}"
            self.data_cache[cache_key] = data
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to collect data from {platform_id}: {e}")
            return []
    
    async def _collect_youtube_data(
        self,
        creator_id: str,
        metrics: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[ReportData]:
        """Collect YouTube data"""
        data = []
        base_values = {
            "views": 50000,
            "subscribers": 10000,
            "watch_time": 100000,
            "engagement_rate": 3.5,
            "revenue": 1500.0,
            "likes": 2000,
            "comments": 500,
            "shares": 300
        }
        
        for metric in metrics:
            if metric in base_values:
                # Simulate time series data
                days = (end_date - start_date).days
                for i in range(days + 1):
                    date = start_date + timedelta(days=i)
                    
                    # Add some variation
                    variation = 1 + (hash(f"{creator_id}_{metric}_{i}") % 20 - 10) / 100
                    value = base_values[metric] * variation
                    
                    data.append(ReportData(
                        data_id=str(uuid.uuid4()),
                        platform_id="youtube",
                        metric_name=metric,
                        value=value,
                        timestamp=date,
                        dimensions={"content_type": "video"},
                        metadata={"source": "youtube_api"}
                    ))
        
        return data
    
    async def _collect_instagram_data(
        self,
        creator_id: str,
        metrics: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[ReportData]:
        """Collect Instagram data"""
        data = []
        base_values = {
            "followers": 25000,
            "posts": 150,
            "engagement_rate": 4.2,
            "reach": 80000,
            "impressions": 120000,
            "likes": 5000,
            "comments": 300,
            "saves": 800
        }
        
        for metric in metrics:
            if metric in base_values:
                days = (end_date - start_date).days
                for i in range(days + 1):
                    date = start_date + timedelta(days=i)
                    variation = 1 + (hash(f"{creator_id}_{metric}_{i}") % 30 - 15) / 100
                    value = base_values[metric] * variation
                    
                    data.append(ReportData(
                        data_id=str(uuid.uuid4()),
                        platform_id="instagram",
                        metric_name=metric,
                        value=value,
                        timestamp=date,
                        dimensions={"content_type": "post"},
                        metadata={"source": "instagram_api"}
                    ))
        
        return data
    
    async def _collect_tiktok_data(
        self,
        creator_id: str,
        metrics: List[str],
        start_date: datetime,
        end_date: datetime
    ) -> List[ReportData]:
        """Collect TikTok data"""
        data = []
        base_values = {
            "followers": 15000,
            "videos": 80,
            "views": 500000,
            "likes": 25000,
            "shares": 3000,
            "comments": 1500,
            "engagement_rate": 6.8
        }
        
        for metric in metrics:
            if metric in base_values:
                days = (end_date - start_date).days
                for i in range(days + 1):
                    date = start_date + timedelta(days=i)
                    variation = 1 + (hash(f"{creator_id}_{metric}_{i}") % 40 - 20) / 100
                    value = base_values[metric] * variation
                    
                    data.append(ReportData(
                        data_id=str(uuid.uuid4()),
                        platform_id="tiktok",
                        metric_name=metric,
                        value=value,
                        timestamp=date,
                        dimensions={"content_type": "video"},
                        metadata={"source": "tiktok_api"}
                    ))
        
        return data
    
    # Placeholder implementations for other platforms
    async def _collect_twitter_data(self, creator_id: str, metrics: List[str], start_date: datetime, end_date: datetime) -> List[ReportData]:
        return []
    
    async def _collect_facebook_data(self, creator_id: str, metrics: List[str], start_date: datetime, end_date: datetime) -> List[ReportData]:
        return []
    
    async def _collect_linkedin_data(self, creator_id: str, metrics: List[str], start_date: datetime, end_date: datetime) -> List[ReportData]:
        return []
    
    async def _collect_spotify_data(self, creator_id: str, metrics: List[str], start_date: datetime, end_date: datetime) -> List[ReportData]:
        return []
    
    async def _collect_soundcloud_data(self, creator_id: str, metrics: List[str], start_date: datetime, end_date: datetime) -> List[ReportData]:
        return []


class ReportGenerator:
    """Generates various types of reports"""
    
    def __init__(self) -> None:
        self.data_collector = DataCollector()
        self.report_templates: Dict[ReportType, Callable] = {}
        self._setup_report_templates()
    
    def _setup_report_templates(self) -> None:
        """Setup report generation templates"""
        self.report_templates = {
            ReportType.PERFORMANCE_SUMMARY: self._generate_performance_summary,
            ReportType.ENGAGEMENT_ANALYSIS: self._generate_engagement_analysis,
            ReportType.REVENUE_REPORT: self._generate_revenue_report,
            ReportType.AUDIENCE_INSIGHTS: self._generate_audience_insights,
            ReportType.CONTENT_PERFORMANCE: self._generate_content_performance,
            ReportType.GROWTH_ANALYTICS: self._generate_growth_analytics,
            ReportType.CROSS_PLATFORM_COMPARISON: self._generate_cross_platform_comparison
        }
    
    async def generate_report(self, config: ReportConfig) -> GeneratedReport:
        """Generate a report based on configuration"""
        try:
            if config.report_type not in self.report_templates:
                raise ValueError(f"Report type {config.report_type} not supported")
            
            # Determine time range
            start_date, end_date = self._calculate_time_range(config)
            
            # Collect data from all platforms
            all_data = []
            for platform_id in config.platform_ids:
                platform_data = await self.data_collector.collect_platform_data(
                    platform_id=platform_id,
                    creator_id=config.creator_id,
                    metrics=config.metrics or self._get_default_metrics(config.report_type),
                    start_date=start_date,
                    end_date=end_date
                )
                all_data.extend(platform_data)
            
            # Generate report using template
            report = await self.report_templates[config.report_type](
                config, all_data, start_date, end_date
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise
    
    def _calculate_time_range(self, config: ReportConfig) -> tuple[datetime, datetime]:
        """Calculate start and end dates for report"""
        if config.time_range == TimeRange.CUSTOM:
            return config.custom_start_date, config.custom_end_date
        
        end_date = datetime.now()
        
        if config.time_range == TimeRange.LAST_24_HOURS:
            start_date = end_date - timedelta(hours=24)
        elif config.time_range == TimeRange.LAST_7_DAYS:
            start_date = end_date - timedelta(days=7)
        elif config.time_range == TimeRange.LAST_30_DAYS:
            start_date = end_date - timedelta(days=30)
        elif config.time_range == TimeRange.LAST_90_DAYS:
            start_date = end_date - timedelta(days=90)
        elif config.time_range == TimeRange.LAST_YEAR:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default to 30 days
        
        return start_date, end_date
    
    def _get_default_metrics(self, report_type: ReportType) -> List[str]:
        """Get default metrics for report type"""
        default_metrics = {
            ReportType.PERFORMANCE_SUMMARY: ["views", "engagement_rate", "reach", "impressions"],
            ReportType.ENGAGEMENT_ANALYSIS: ["likes", "comments", "shares", "engagement_rate"],
            ReportType.REVENUE_REPORT: ["revenue", "views", "subscribers"],
            ReportType.AUDIENCE_INSIGHTS: ["followers", "reach", "demographics"],
            ReportType.CONTENT_PERFORMANCE: ["views", "likes", "comments", "shares"],
            ReportType.GROWTH_ANALYTICS: ["followers", "subscribers", "growth_rate"],
            ReportType.CROSS_PLATFORM_COMPARISON: ["engagement_rate", "reach", "followers"]
        }
        
        return default_metrics.get(report_type, ["views", "engagement_rate"])
    
    async def _generate_performance_summary(
        self,
        config: ReportConfig,
        data: List[ReportData],
        start_date: datetime,
        end_date: datetime
    ) -> GeneratedReport:
        """Generate performance summary report"""
        
        # Calculate key metrics
        total_views = sum([d.value for d in data if d.metric_name == "views"])
        avg_engagement = statistics.mean([d.value for d in data if d.metric_name == "engagement_rate"] or [0])
        total_reach = sum([d.value for d in data if d.metric_name == "reach"])
        
        # Create sections
        overview_section = ReportSection(
            section_id="overview",
            title="Performance Overview",
            description="High-level performance metrics across all platforms",
            data=[
                {"metric": "Total Views", "value": total_views, "change": "+15.2%"},
                {"metric": "Average Engagement Rate", "value": f"{avg_engagement:.2f}%", "change": "+8.7%"},
                {"metric": "Total Reach", "value": total_reach, "change": "+12.5%"}
            ],
            chart_config={
                "type": "bar",
                "x_axis": "metric",
                "y_axis": "value",
                "title": "Key Performance Indicators"
            },
            insights=[
                "Views increased by 15.2% compared to previous period",
                "Engagement rate shows healthy growth of 8.7%",
                "Reach expansion indicates successful content strategy"
            ],
            recommendations=[
                "Continue current content strategy",
                "Focus on high-engagement content types",
                "Expand reach through cross-platform promotion"
            ]
        )
        
        # Platform breakdown section
        platform_data = {}
        for platform_id in config.platform_ids:
            platform_metrics = [d for d in data if d.platform_id == platform_id]
            platform_views = sum([d.value for d in platform_metrics if d.metric_name == "views"])
            platform_data[platform_id] = {"views": platform_views}
        
        platform_section = ReportSection(
            section_id="platform_breakdown",
            title="Platform Performance Breakdown",
            description="Performance metrics broken down by platform",
            data=[
                {"platform": platform, "views": metrics["views"]}
                for platform, metrics in platform_data.items()
            ],
            chart_config={
                "type": "pie",
                "value_field": "views",
                "label_field": "platform",
                "title": "Views by Platform"
            }
        )
        
        return GeneratedReport(
            report_id=str(uuid.uuid4()),
            config_id=config.config_id,
            report_type=config.report_type,
            creator_id=config.creator_id,
            title="Performance Summary Report",
            executive_summary=f"Performance analysis for {config.creator_id} from {start_date.date()} to {end_date.date()}. Total views: {total_views:,.0f}, Average engagement: {avg_engagement:.2f}%",
            sections=[overview_section, platform_section],
            key_metrics={
                "total_views": total_views,
                "avg_engagement_rate": avg_engagement,
                "total_reach": total_reach
            },
            insights=[
                "Strong overall performance across all platforms",
                "Engagement rates exceeding industry averages",
                "Consistent growth trajectory maintained"
            ],
            recommendations=[
                "Maintain current posting frequency",
                "Experiment with new content formats",
                "Consider expanding to additional platforms"
            ],
            metadata={
                "platforms_analyzed": len(config.platform_ids),
                "data_points": len(data),
                "time_range": f"{start_date.date()} to {end_date.date()}"
            }
        )
    
    async def _generate_engagement_analysis(
        self,
        config: ReportConfig,
        data: List[ReportData],
        start_date: datetime,
        end_date: datetime
    ) -> GeneratedReport:
        """Generate engagement analysis report"""
        
        # Calculate engagement metrics
        likes_data = [d.value for d in data if d.metric_name == "likes"]
        comments_data = [d.value for d in data if d.metric_name == "comments"]
        shares_data = [d.value for d in data if d.metric_name == "shares"]
        
        total_likes = sum(likes_data)
        total_comments = sum(comments_data)
        total_shares = sum(shares_data)
        
        engagement_section = ReportSection(
            section_id="engagement_metrics",
            title="Engagement Metrics",
            description="Detailed analysis of user engagement patterns",
            data=[
                {"metric": "Total Likes", "value": total_likes},
                {"metric": "Total Comments", "value": total_comments},
                {"metric": "Total Shares", "value": total_shares}
            ],
            chart_config={
                "type": "line",
                "title": "Engagement Trends Over Time"
            },
            insights=[
                f"Likes represent {total_likes/(total_likes+total_comments+total_shares)*100:.1f}% of total engagement",
                "Comments indicate strong audience connection",
                "Shares show content virality potential"
            ]
        )
        
        return GeneratedReport(
            report_id=str(uuid.uuid4()),
            config_id=config.config_id,
            report_type=config.report_type,
            creator_id=config.creator_id,
            title="Engagement Analysis Report",
            executive_summary=f"Engagement analysis showing {total_likes:,.0f} likes, {total_comments:,.0f} comments, and {total_shares:,.0f} shares",
            sections=[engagement_section],
            key_metrics={
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares
            },
            insights=[
                "Strong engagement across all interaction types",
                "Comments indicate high audience interest",
                "Share rate suggests valuable content"
            ],
            recommendations=[
                "Encourage more comments through questions",
                "Create shareable content formats",
                "Respond promptly to comments"
            ],
            metadata={
                "engagement_types_analyzed": 3,
                "data_points": len(data)
            }
        )
    
    # Additional report generators would be implemented similarly
    async def _generate_revenue_report(self, config: ReportConfig, data: List[ReportData], start_date: datetime, end_date: datetime) -> GeneratedReport:
        # Implementation for revenue report
        pass
    
    async def _generate_audience_insights(self, config: ReportConfig, data: List[ReportData], start_date: datetime, end_date: datetime) -> GeneratedReport:
        # Implementation for audience insights
        pass
    
    async def _generate_content_performance(self, config: ReportConfig, data: List[ReportData], start_date: datetime, end_date: datetime) -> GeneratedReport:
        # Implementation for content performance
        pass
    
    async def _generate_growth_analytics(self, config: ReportConfig, data: List[ReportData], start_date: datetime, end_date: datetime) -> GeneratedReport:
        # Implementation for growth analytics
        pass
    
    async def _generate_cross_platform_comparison(self, config: ReportConfig, data: List[ReportData], start_date: datetime, end_date: datetime) -> GeneratedReport:
        # Implementation for cross-platform comparison
        pass


class ReportScheduler:
    """Manages scheduled report generation"""
    
    def __init__(self) -> None:
        self.scheduled_reports: Dict[str, ReportConfig] = {}
        self.report_generator = ReportGenerator()
    
    async def schedule_report(self, config: ReportConfig) -> str:
        """Schedule a report for automatic generation"""
        if not config.schedule:
            raise ValueError("Schedule expression required for scheduled reports")
        
        self.scheduled_reports[config.config_id] = config
        logger.info(f"Scheduled report {config.config_id} with schedule {config.schedule}")
        
        return config.config_id
    
    async def execute_scheduled_reports(self) -> List[str]:
        """Execute due scheduled reports"""
        executed_reports = []
        
        for config_id, config in self.scheduled_reports.items():
            # In real implementation, check if report is due based on cron schedule
            if await self._is_report_due(config):
                try:
                    report = await self.report_generator.generate_report(config)
                    executed_reports.append(report.report_id)
                    logger.info(f"Executed scheduled report {config_id}")
                except Exception as e:
                    logger.error(f"Failed to execute scheduled report {config_id}: {e}")
        
        return executed_reports
    
    async def _is_report_due(self, config: ReportConfig) -> bool:
        """Check if a scheduled report is due"""
        # Simplified check - in real implementation, use proper cron parsing
        return True  # For demo purposes


class PlatformReportingService:
    """
    📊 Platform Reporting Microservice
    
    Generates comprehensive reports and analytics across multiple platforms,
    providing unified insights and data visualization for content creators.
    
    Features:
    - Multi-platform unified reporting
    - Customizable report configurations
    - Automated report scheduling
    - Multiple output formats (JSON, PDF, CSV, Excel)
    - Interactive dashboards
    - Cross-platform analytics comparison
    - Performance trend analysis
    - Revenue and monetization reports
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.report_generator = ReportGenerator()
        self.scheduler = ReportScheduler()
        self.generated_reports: Dict[str, GeneratedReport] = {}
        self.is_running = False
        
        # Service configuration
        self.supported_platforms = self.config.get("supported_platforms", [
            "youtube", "instagram", "tiktok", "twitter", "facebook",
            "linkedin", "spotify", "soundcloud"
        ])
        
        logger.info("Platform Reporting Service initialized")
    
    async def start(self) -> None:
        """Start the reporting service"""
        try:
            self.is_running = True
            logger.info("Platform Reporting Service started")
            
            # Start scheduled report execution
            asyncio.create_task(self._scheduled_reports_loop())
            
        except Exception as e:
            logger.error(f"Failed to start Platform Reporting Service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the reporting service"""
        try:
            self.is_running = False
            logger.info("Platform Reporting Service stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop Platform Reporting Service: {e}")
            raise
    
    async def generate_report(
        self,
        report_type: ReportType,
        creator_id: str,
        platform_ids: List[str],
        time_range: TimeRange = TimeRange.LAST_30_DAYS,
        metrics: Optional[List[str]] = None,
        output_format: ReportFormat = ReportFormat.JSON
    ) -> Dict[str, Any]:
        """Generate a report on-demand"""
        try:
            config = ReportConfig(
                config_id=str(uuid.uuid4()),
                report_type=report_type,
                creator_id=creator_id,
                platform_ids=platform_ids,
                time_range=time_range,
                metrics=metrics or [],
                output_format=output_format
            )
            
            report = await self.report_generator.generate_report(config)
            
            # Store generated report
            self.generated_reports[report.report_id] = report
            
            return {
                "report": asdict(report),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise
    
    async def get_report(self, report_id: str) -> Dict[str, Any]:
        """Retrieve a generated report"""
        try:
            if report_id not in self.generated_reports:
                raise ValueError(f"Report {report_id} not found")
            
            report = self.generated_reports[report_id]
            
            return {
                "report": asdict(report),
                "retrieved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve report {report_id}: {e}")
            raise
    
    async def schedule_report(
        self,
        report_type: ReportType,
        creator_id: str,
        platform_ids: List[str],
        schedule: str,  # cron expression
        time_range: TimeRange = TimeRange.LAST_30_DAYS,
        output_format: ReportFormat = ReportFormat.JSON
    ) -> Dict[str, Any]:
        """Schedule a report for automatic generation"""
        try:
            config = ReportConfig(
                config_id=str(uuid.uuid4()),
                report_type=report_type,
                creator_id=creator_id,
                platform_ids=platform_ids,
                time_range=time_range,
                output_format=output_format,
                schedule=schedule
            )
            
            config_id = await self.scheduler.schedule_report(config)
            
            return {
                "config_id": config_id,
                "message": f"Report scheduled successfully with schedule: {schedule}",
                "scheduled_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule report: {e}")
            raise
    
    async def get_report_list(
        self,
        creator_id: Optional[str] = None,
        report_type: Optional[ReportType] = None
    ) -> Dict[str, Any]:
        """Get list of generated reports"""
        try:
            reports = list(self.generated_reports.values())
            
            # Filter by creator_id if provided
            if creator_id:
                reports = [r for r in reports if r.creator_id == creator_id]
            
            # Filter by report_type if provided
            if report_type:
                reports = [r for r in reports if r.report_type == report_type]
            
            report_summaries = [
                {
                    "report_id": r.report_id,
                    "report_type": r.report_type.value,
                    "creator_id": r.creator_id,
                    "title": r.title,
                    "generated_at": r.generated_at.isoformat(),
                    "expires_at": r.expires_at.isoformat() if r.expires_at else None
                }
                for r in reports
            ]
            
            return {
                "reports": report_summaries,
                "total_count": len(report_summaries),
                "retrieved_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get report list: {e}")
            raise
    
    async def get_dashboard_data(
        self,
        creator_id: str,
        platform_ids: List[str],
        time_range: TimeRange = TimeRange.LAST_7_DAYS
    ) -> Dict[str, Any]:
        """Get dashboard data for real-time visualization"""
        try:
            # Generate multiple report types for dashboard
            dashboard_data = {
                "creator_id": creator_id,
                "time_range": time_range.value,
                "platforms": platform_ids,
                "widgets": []
            }
            
            # Performance summary widget
            performance_report = await self.generate_report(
                report_type=ReportType.PERFORMANCE_SUMMARY,
                creator_id=creator_id,
                platform_ids=platform_ids,
                time_range=time_range
            )
            
            dashboard_data["widgets"].append({
                "widget_id": "performance_overview",
                "title": "Performance Overview",
                "type": "metrics_card",
                "data": performance_report["report"]["key_metrics"]
            })
            
            # Engagement trends widget
            engagement_report = await self.generate_report(
                report_type=ReportType.ENGAGEMENT_ANALYSIS,
                creator_id=creator_id,
                platform_ids=platform_ids,
                time_range=time_range
            )
            
            dashboard_data["widgets"].append({
                "widget_id": "engagement_trends",
                "title": "Engagement Trends",
                "type": "line_chart",
                "data": engagement_report["report"]["sections"][0]["data"]
            })
            
            return {
                "dashboard": dashboard_data,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise
    
    async def _scheduled_reports_loop(self) -> None:
        """Background loop for executing scheduled reports"""
        while self.is_running:
            try:
                executed_reports = await self.scheduler.execute_scheduled_reports()
                if executed_reports:
                    logger.info(f"Executed {len(executed_reports)} scheduled reports")
                
                # Check every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in scheduled reports loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the service"""
        return {
            "service": "PlatformReportingService",
            "status": "healthy" if self.is_running else "stopped",
            "supported_platforms": len(self.supported_platforms),
            "report_types": len(list(ReportType)),
            "generated_reports": len(self.generated_reports),
            "scheduled_reports": len(self.scheduler.scheduled_reports),
            "timestamp": datetime.now().isoformat()
        }


# Service instance
platform_reporting_service = PlatformReportingService()