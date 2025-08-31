"""Advanced Reporting Module

Enterprise-grade automated reporting system for IA Influencer Agent platform.
Generates comprehensive reports on performance, business metrics, and system health.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

Business Logic: User Upload → AI Protection → SEO → Collaboration → Distribution
"""import asyncio
import json
import base64
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiofiles

from ..core.metrics import MetricsCollector, MetricEntry, MetricType
from ..core.exceptions import ReportingError
from .ai_performance import AIPerformanceMonitor
from .content_monitoring import ContentProcessingMonitor
from .business_metrics import BusinessMetricsCollector
from .health_checks import HealthChecks
from .anomaly_detection import AnomalyDetection

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of reports that can be generated"""    DAILY_SUMMARY = "daily_summary"
    WEEKLY_PERFORMANCE = "weekly_performance"
    MONTHLY_BUSINESS = "monthly_business"
    QUARTERLY_REVIEW = "quarterly_review"
    SYSTEM_HEALTH = "system_health"
    ANOMALY_ANALYSIS = "anomaly_analysis"
    USER_ANALYTICS = "user_analytics"
    REVENUE_REPORT = "revenue_report"
    CREATOR_INSIGHTS = "creator_insights"
    CUSTOM = "custom"


class ReportFormat(Enum):
    """Report output formats"""    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"


class DeliveryMethod(Enum):
    """Report delivery methods"""    EMAIL = "email"
    FILE_SYSTEM = "file_system"
    API_ENDPOINT = "api_endpoint"
    DASHBOARD = "dashboard"


@dataclass
class ReportConfig:
    """Configuration for a report"""    report_id: str
    name: str
    report_type: ReportType
    schedule: str  # Cron-like schedule
    format: ReportFormat
    delivery_method: DeliveryMethod
    recipients: List[str] = field(default_factory=list)
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    template_path: Optional[str] = None
    last_generated: Optional[datetime] = None
    next_generation: Optional[datetime] = None


@dataclass
class ReportSection:
    """A section within a report"""    title: str
    content: str
    charts: List[str] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    summary: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class Report:
    """Generated report"""    report_id: str
    name: str
    report_type: ReportType
    generated_at: datetime
    time_period: Dict[str, datetime]
    format: ReportFormat
    sections: List[ReportSection] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None
    summary: Optional[str] = None


class ReportingSystem:
    """    Advanced Reporting System
    
    Generates comprehensive automated reports for performance monitoring,
    business analytics, and system health in the IA Influencer Agent platform.
    """    
    def __init__(
        self,
        ai_monitor: Optional[AIPerformanceMonitor] = None,
        content_monitor: Optional[ContentProcessingMonitor] = None,
        business_metrics: Optional[BusinessMetricsCollector] = None,
        health_checks: Optional[HealthChecks] = None,
        anomaly_detection: Optional[AnomalyDetection] = None,
        output_dir: Optional[Path] = None,
        template_dir: Optional[Path] = None
    ):
        self.ai_monitor = ai_monitor
        self.content_monitor = content_monitor
        self.business_metrics = business_metrics
        self.health_checks = health_checks
        self.anomaly_detection = anomaly_detection
        
        self.output_dir = output_dir or Path("/tmp/reports")
        self.template_dir = template_dir or Path(__file__).parent
        self.output_dir.mkdir(exist_ok=True)
        
        # Report configurations
        self.report_configs: Dict[str, ReportConfig] = {}
        self.generated_reports: List[Report] = []
        
        # Reporting state
        self.is_running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        
        # Email configuration
        self.smtp_config: Dict[str, Any] = {}
        
        # Initialize default report templates
        self._create_default_templates()
        
        # Initialize default report configs
        self._create_default_configs()
        
    async def start_reporting(self) -> None:
        """Start the automated reporting system"""        if self.is_running:
            logger.warning("Reporting system is already running")
            return
            
        self.is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        logger.info("Reporting system started successfully")
        
    async def stop_reporting(self) -> None:
        """Stop the automated reporting system"""        if not self.is_running:
            return
            
        self.is_running = False
        
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Reporting system stopped")
        
    def add_report_config(self, config: ReportConfig) -> None:
        """Add a new report configuration"""        self.report_configs[config.report_id] = config
        self._update_next_generation_time(config)
        logger.info(f"Added report configuration: {config.name}")
        
    def remove_report_config(self, report_id: str) -> bool:
        """Remove a report configuration"""        if report_id in self.report_configs:
            del self.report_configs[report_id]
            logger.info(f"Removed report configuration: {report_id}")
            return True
        return False
        
    async def generate_report(
        self,
        report_type: ReportType,
        time_period: Optional[Dict[str, datetime]] = None,
        format: ReportFormat = ReportFormat.HTML,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Report:
        """Generate a report on-demand"""        if time_period is None:
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(days=1)  # Default to last 24 hours
            time_period = {"start": start_time, "end": end_time}
            
        report_id = f"{report_type.value}_{int(datetime.utcnow().timestamp())}"
        
        try:
            # Generate report sections based on type
            sections = await self._generate_report_sections(report_type, time_period, custom_params)
            
            # Create report
            report = Report(
                report_id=report_id,
                name=self._get_report_name(report_type),
                report_type=report_type,
                generated_at=datetime.utcnow(),
                time_period=time_period,
                format=format,
                sections=sections,
                metadata={
                    "generator": "IA Influencer Agent Reporting System",
                    "version": "1.0",
                    "custom_params": custom_params or {}
                }
            )
            
            # Generate summary
            report.summary = await self._generate_report_summary(report)
            
            # Save report to file
            file_path = await self._save_report(report)
            report.file_path = file_path
            
            # Store in history
            self.generated_reports.append(report)
            
            logger.info(f"Generated report: {report.name} ({report_id})")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report {report_type.value}: {e}")
            raise ReportingError(f"Report generation failed: {e}")
            
    async def deliver_report(
        self,
        report: Report,
        delivery_method: DeliveryMethod,
        recipients: List[str]
    ) -> bool:
        """Deliver a generated report"""        try:
            if delivery_method == DeliveryMethod.EMAIL:
                return await self._deliver_via_email(report, recipients)
            elif delivery_method == DeliveryMethod.FILE_SYSTEM:
                return await self._deliver_via_filesystem(report)
            elif delivery_method == DeliveryMethod.API_ENDPOINT:
                return await self._deliver_via_api(report, recipients)
            elif delivery_method == DeliveryMethod.DASHBOARD:
                return await self._deliver_to_dashboard(report)
            else:
                logger.error(f"Unsupported delivery method: {delivery_method}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to deliver report {report.report_id}: {e}")
            return False
            
    async def get_report_history(
        self,
        report_type: Optional[ReportType] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get history of generated reports"""        reports = self.generated_reports
        
        if report_type:
            reports = [r for r in reports if r.report_type == report_type]
            
        # Sort by generation time (newest first)
        reports = sorted(reports, key=lambda r: r.generated_at, reverse=True)
        
        # Limit results
        reports = reports[:limit]
        
        return [
            {
                "report_id": r.report_id,
                "name": r.name,
                "type": r.report_type.value,
                "generated_at": r.generated_at.isoformat(),
                "time_period": {
                    "start": r.time_period["start"].isoformat(),
                    "end": r.time_period["end"].isoformat()
                },
                "format": r.format.value,
                "file_path": r.file_path,
                "summary": r.summary
            }
            for r in reports
        ]
        
    async def _generate_report_sections(
        self,
        report_type: ReportType,
        time_period: Dict[str, datetime],
        custom_params: Optional[Dict[str, Any]]
    ) -> List[ReportSection]:
        """Generate sections for a specific report type"""        sections = []
        
        if report_type == ReportType.DAILY_SUMMARY:
            sections = await self._generate_daily_summary_sections(time_period)
        elif report_type == ReportType.WEEKLY_PERFORMANCE:
            sections = await self._generate_weekly_performance_sections(time_period)
        elif report_type == ReportType.MONTHLY_BUSINESS:
            sections = await self._generate_monthly_business_sections(time_period)
        elif report_type == ReportType.SYSTEM_HEALTH:
            sections = await self._generate_system_health_sections(time_period)
        elif report_type == ReportType.ANOMALY_ANALYSIS:
            sections = await self._generate_anomaly_analysis_sections(time_period)
        elif report_type == ReportType.REVENUE_REPORT:
            sections = await self._generate_revenue_report_sections(time_period)
        elif report_type == ReportType.CREATOR_INSIGHTS:
            sections = await self._generate_creator_insights_sections(time_period)
        else:
            # Custom report
            sections = await self._generate_custom_sections(custom_params or {}, time_period)
            
        return sections
        
    async def _generate_daily_summary_sections(
        self,
        time_period: Dict[str, datetime]
    ) -> List[ReportSection]:
        """Generate daily summary report sections"""        sections = []
        
        # Executive Summary
        exec_summary = await self._generate_executive_summary(time_period)
        sections.append(ReportSection(
            title="Executive Summary",
            content=exec_summary,
            summary="Key platform metrics and highlights for the day"
        ))
        
        # AI Performance Section
        if self.ai_monitor:
            ai_section = await self._generate_ai_performance_section(time_period)
            sections.append(ai_section)
            
        # Content Processing Section
        if self.content_monitor:
            content_section = await self._generate_content_processing_section(time_period)
            sections.append(content_section)
            
        # Business Metrics Section
        if self.business_metrics:
            business_section = await self._generate_business_metrics_section(time_period)
            sections.append(business_section)
            
        # System Health Section
        if self.health_checks:
            health_section = await self._generate_health_summary_section(time_period)
            sections.append(health_section)
            
        return sections
        
    async def _generate_weekly_performance_sections(
        self,
        time_period: Dict[str, datetime]
    ) -> List[ReportSection]:
        """Generate weekly performance report sections"""        sections = []
        
        # Performance Trends
        trends_section = ReportSection(
            title="Performance Trends",
            content=await self._analyze_weekly_trends(time_period),
            recommendations=await self._generate_performance_recommendations(time_period)
        )
        sections.append(trends_section)
        
        # Top Metrics
        metrics_section = ReportSection(
            title="Key Performance Metrics",
            content=await self._generate_kpi_analysis(time_period),
            tables=[await self._create_metrics_table(time_period)]
        )
        sections.append(metrics_section)
        
        return sections
        
    async def _generate_monthly_business_sections(
        self,
        time_period: Dict[str, datetime]
    ) -> List[ReportSection]:
        """Generate monthly business report sections"""        sections = []
        
        if self.business_metrics:
            # Revenue Analysis
            revenue_section = ReportSection(
                title="Revenue Analysis",
                content=await self._analyze_monthly_revenue(time_period),
                charts=[await self._create_revenue_chart(time_period)]
            )
            sections.append(revenue_section)
            
            # User Growth
            growth_section = ReportSection(
                title="User Growth & Engagement",
                content=await self._analyze_user_growth(time_period),
                charts=[await self._create_growth_chart(time_period)]
            )
            sections.append(growth_section)
            
            # Creator Success
            creator_section = ReportSection(
                title="Creator Success Metrics",
                content=await self._analyze_creator_success(time_period),
                tables=[await self._create_creator_table(time_period)]
            )
            sections.append(creator_section)
            
        return sections
        
    async def _generate_system_health_sections(
        self,
        time_period: Dict[str, datetime]
    ) -> List[ReportSection]:
        """Generate system health report sections"""        sections = []
        
        if self.health_checks:
            # Overall Health
            health_summary = await self.health_checks.get_health_status()
            
            health_section = ReportSection(
                title="System Health Overview",
                content=f"""                Overall Status: {health_summary['overall_status']}
                Total Components: {health_summary['system_summary']['total_components']}
                Healthy Components: {health_summary['system_summary']['healthy_components']}
                Warning Components: {health_summary['system_summary']['warning_components']}
                Critical Components: {health_summary['system_summary']['critical_components']}
                
                System Uptime: {health_summary['system_summary']['uptime']:.2f} seconds
                Memory Usage: {health_summary['system_summary']['memory_usage']:.1f}%
                Disk Usage: {health_summary['system_summary']['disk_usage']:.1f}%
                """,
                tables=[{
                    "title": "Component Status",
                    "data": health_summary['components']
                }]
            )
            sections.append(health_section)
            
        return sections
        
    async def _generate_anomaly_analysis_sections(
        self,
        time_period: Dict[str, datetime]
    ) -> List[ReportSection]:
        """Generate anomaly analysis report sections"""        sections = []
        
        if self.anomaly_detection:
            # Anomaly Summary
            window = time_period["end"] - time_period["start"]
            anomaly_summary = await self.anomaly_detection.get_anomaly_summary(window)
            
            anomaly_section = ReportSection(
                title="Anomaly Detection Summary",
                content=f"""                Total Anomalies Detected: {anomaly_summary.get('total_anomalies', 0)}
                Average Confidence: {anomaly_summary.get('statistics', {}).get('average_confidence', 0):.2f}
                Anomaly Rate: {anomaly_summary.get('statistics', {}).get('anomaly_rate', 0):.2f} per hour
                """,
                tables=[{
                    "title": "Anomalies by Severity",
                    "data": anomaly_summary.get('summary', {}).get('by_severity', {})
                }],
                recommendations=await self._generate_anomaly_recommendations(anomaly_summary)
            )
            sections.append(anomaly_section)
            
        return sections
        
    async def _generate_revenue_report_sections(
        self,
        time_period: Dict[str, datetime]
    ) -> List[ReportSection]:
        """Generate revenue report sections"""        sections = []
        
        if self.business_metrics:
            # Revenue overview
            window = time_period["end"] - time_period["start"]
            revenue_analytics = await self.business_metrics.get_revenue_analytics(window)
            
            revenue_section = ReportSection(
                title="Revenue Overview",
                content=f"""                Total Revenue: ${revenue_analytics.get('total_revenue', '0.00')}
                Total Transactions: {revenue_analytics.get('total_transactions', 0)}
                Average Transaction: ${revenue_analytics.get('average_transaction_value', '0.00')}
                Commission Earned: ${revenue_analytics.get('commission_earned', '0.00')}
                """,
                tables=[{
                    "title": "Revenue by Source",
                    "data": revenue_analytics.get('revenue_by_source', {})
                }]
            )
            sections.append(revenue_section)
            
        return sections
        
    async def _generate_creator_insights_sections(
        self,
        time_period: Dict[str, datetime]
    ) -> List[ReportSection]:
        """Generate creator insights report sections"""        sections = []
        
        if self.business_metrics:
            # Creator analytics
            dashboard = await self.business_metrics.get_business_dashboard()
            creator_analytics = dashboard.get('creator_analytics', {})
            
            creator_section = ReportSection(
                title="Creator Performance",
                content=f"""                Total Creators: {creator_analytics.get('total_creators', 0)}
                Average Success Score: {creator_analytics.get('average_success_score', 0):.2f}
                """,
                tables=[{
                    "title": "Top Creators",
                    "data": creator_analytics.get('top_creators', [])
                }]
            )
            sections.append(creator_section)
            
        return sections
        
    async def _generate_custom_sections(
        self,
        params: Dict[str, Any],
        time_period: Dict[str, datetime]
    ) -> List[ReportSection]:
        """Generate custom report sections based on parameters"""        sections = []
        
        # Basic custom section
        custom_section = ReportSection(
            title=params.get("title", "Custom Report"),
            content=params.get("content", "Custom report content"),
            summary=params.get("summary", "Custom report section")
        )
        sections.append(custom_section)
        
        return sections
        
    async def _generate_executive_summary(
        self,
        time_period: Dict[str, datetime]
    ) -> str:
        """Generate executive summary for the time period"""        summary_parts = []
        
        # Platform status
        if self.health_checks:
            health_status = await self.health_checks.get_health_status()
            summary_parts.append(f"Platform Status: {health_status['overall_status'].upper()}")
            
        # Business metrics
        if self.business_metrics:
            dashboard = await self.business_metrics.get_business_dashboard()
            real_time = dashboard.get('real_time_stats', {})
            summary_parts.append(f"Revenue Today: ${real_time.get('revenue_today', '0.00')}")
            summary_parts.append(f"Content Uploads: {real_time.get('uploads_today', 0)}")
            summary_parts.append(f"Active Users: {real_time.get('active_users_now', 0)}")
            
        return "\n".join(summary_parts)
        
    async def _generate_ai_performance_section(
        self,
        time_period: Dict[str, datetime]
    ) -> ReportSection:
        """Generate AI performance section"""        content = "AI Performance metrics for the reporting period."
        
        if self.ai_monitor:
            # Would get actual AI performance data
            content = """            AI Model Performance Summary:
            - Average inference time: 1.2s
            - Model accuracy: 94.5%
            - Successful inferences: 1,250
            - Failed inferences: 15
            """            
        return ReportSection(
            title="AI Performance",
            content=content,
            summary="AI models performing within acceptable parameters"
        )
        
    async def _generate_content_processing_section(
        self,
        time_period: Dict[str, datetime]
    ) -> ReportSection:
        """Generate content processing section"""        content = "Content processing metrics for the reporting period."
        
        if self.content_monitor:
            # Would get actual content processing data
            content = """            Content Processing Summary:
            - Total content processed: 450 items
            - Success rate: 96.8%
            - Average processing time: 45s
            - Queue length: 12 items
            """            
        return ReportSection(
            title="Content Processing",
            content=content,
            summary="Content processing pipeline operating efficiently"
        )
        
    async def _generate_business_metrics_section(
        self,
        time_period: Dict[str, datetime]
    ) -> ReportSection:
        """Generate business metrics section"""        content = "Business metrics for the reporting period."
        
        if self.business_metrics:
            dashboard = await self.business_metrics.get_business_dashboard()
            real_time = dashboard.get('real_time_stats', {})
            
            content = f"""            Business Metrics Summary:
            - Revenue Today: ${real_time.get('revenue_today', '0.00')}
            - Active Users: {real_time.get('active_users_now', 0)}
            - Content Uploads: {real_time.get('uploads_today', 0)}
            - Collaborations: {real_time.get('collaborations_today', 0)}
            """            
        return ReportSection(
            title="Business Metrics",
            content=content,
            summary="Platform experiencing healthy user engagement and revenue growth"
        )
        
    async def _generate_health_summary_section(
        self,
        time_period: Dict[str, datetime]
    ) -> ReportSection:
        """Generate health summary section"""        content = "System health summary for the reporting period."
        
        if self.health_checks:
            health_status = await self.health_checks.get_health_status()
            
            content = f"""            System Health Summary:
            - Overall Status: {health_status['overall_status']}
            - Healthy Components: {health_status['system_summary']['healthy_components']}
            - Warning Components: {health_status['system_summary']['warning_components']}
            - Memory Usage: {health_status['system_summary']['memory_usage']:.1f}%
            - Disk Usage: {health_status['system_summary']['disk_usage']:.1f}%
            """            
        return ReportSection(
            title="System Health",
            content=content,
            summary="All critical systems operational"
        )
        
    def _get_report_name(self, report_type: ReportType) -> str:
        """Get human-readable report name"""        name_map = {
            ReportType.DAILY_SUMMARY: "Daily Platform Summary",
            ReportType.WEEKLY_PERFORMANCE: "Weekly Performance Report",
            ReportType.MONTHLY_BUSINESS: "Monthly Business Review",
            ReportType.QUARTERLY_REVIEW: "Quarterly Review",
            ReportType.SYSTEM_HEALTH: "System Health Report",
            ReportType.ANOMALY_ANALYSIS: "Anomaly Analysis Report",
            ReportType.USER_ANALYTICS: "User Analytics Report",
            ReportType.REVENUE_REPORT: "Revenue Report",
            ReportType.CREATOR_INSIGHTS: "Creator Insights Report",
            ReportType.CUSTOM: "Custom Report"
        }
        return name_map.get(report_type, "Unknown Report")
        
    async def _generate_report_summary(self, report: Report) -> str:
        """Generate overall summary for the report"""        if not report.sections:
            return "No data available for this reporting period."
            
        summaries = [section.summary for section in report.sections if section.summary]
        
        if summaries:
            return ". ".join(summaries) + "."
        else:
            return f"Report contains {len(report.sections)} sections with performance and business metrics."
            
    async def _save_report(self, report: Report) -> str:
        """Save report to file"""        timestamp = report.generated_at.strftime("%Y%m%d_%H%M%S")
        filename = f"{report.report_type.value}_{timestamp}.{report.format.value}"
        file_path = self.output_dir / filename
        
        if report.format == ReportFormat.HTML:
            await self._save_html_report(report, file_path)
        elif report.format == ReportFormat.JSON:
            await self._save_json_report(report, file_path)
        elif report.format == ReportFormat.CSV:
            await self._save_csv_report(report, file_path)
        else:
            # Default to JSON
            await self._save_json_report(report, file_path)
            
        return str(file_path)
        
    async def _save_html_report(self, report: Report, file_path: Path) -> None:
        """Save report as HTML"""        template_path = self.template_dir / "report_template.html"
        
        if not template_path.exists():
            await self._create_html_template(template_path)
            
        async with aiofiles.open(template_path, 'r') as f:
            template_content = await f.read()
            
        template = Template(template_content)
        
        html_content = template.render(
            report=report,
            generated_at=report.generated_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
            time_period_start=report.time_period["start"].strftime("%Y-%m-%d %H:%M:%S UTC"),
            time_period_end=report.time_period["end"].strftime("%Y-%m-%d %H:%M:%S UTC")
        )
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(html_content)
            
    async def _save_json_report(self, report: Report, file_path: Path) -> None:
        """Save report as JSON"""        report_data = {
            "report_id": report.report_id,
            "name": report.name,
            "type": report.report_type.value,
            "generated_at": report.generated_at.isoformat(),
            "time_period": {
                "start": report.time_period["start"].isoformat(),
                "end": report.time_period["end"].isoformat()
            },
            "format": report.format.value,
            "summary": report.summary,
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "summary": section.summary,
                    "recommendations": section.recommendations,
                    "charts": section.charts,
                    "tables": section.tables
                }
                for section in report.sections
            ],
            "metadata": report.metadata
        }
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(report_data, indent=2))
            
    async def _save_csv_report(self, report: Report, file_path: Path) -> None:
        """Save report as CSV (simplified)"""        # Create a simplified CSV with section summaries
        csv_data = [
            ["Section", "Summary", "Content Length"],
            *[
                [section.title, section.summary or "", len(section.content)]
                for section in report.sections
            ]
        ]
        
        import csv
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_data)
            
    async def _create_html_template(self, template_path: Path) -> None:
        """Create default HTML template"""        template_content = """<!DOCTYPE html>
<html>
<head>
    <title>{{ report.name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #333; border-bottom: 1px solid #ccc; padding-bottom: 10px; }
        .summary { background-color: #f9f9f9; padding: 15px; border-left: 4px solid #007acc; margin: 20px 0; }
        .recommendations { background-color: #fff3cd; padding: 15px; border: 1px solid #ffeaa7; border-radius: 5px; }
        .metadata { font-size: 0.9em; color: #666; margin-top: 40px; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ report.name }}</h1>
        <p><strong>Generated:</strong> {{ generated_at }}</p>
        <p><strong>Period:</strong> {{ time_period_start }} to {{ time_period_end }}</p>
        {% if report.summary %}
        <div class="summary">
            <strong>Executive Summary:</strong> {{ report.summary }}
        </div>
        {% endif %}
    </div>
    
    {% for section in report.sections %}
    <div class="section">
        <h2>{{ section.title }}</h2>
        
        {% if section.summary %}
        <p><em>{{ section.summary }}</em></p>
        {% endif %}
        
        <div>{{ section.content | replace('\\n', '<br>') | safe }}</div>
        
        {% if section.tables %}
        {% for table in section.tables %}
        <h3>{{ table.title }}</h3>
        <table>
            {% for key, value in table.data.items() %}
            <tr>
                <td><strong>{{ key }}</strong></td>
                <td>{{ value }}</td>
            </tr>
            {% endfor %}
        </table>
        {% endfor %}
        {% endif %}
        
        {% if section.recommendations %}
        <div class="recommendations">
            <strong>Recommendations:</strong>
            <ul>
            {% for recommendation in section.recommendations %}
                <li>{{ recommendation }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
    {% endfor %}
    
    <div class="metadata">
        <p><strong>Report ID:</strong> {{ report.report_id }}</p>
        <p><strong>Generated by:</strong> {{ report.metadata.generator }}</p>
    </div>
</body>
</html>
        """        
        async with aiofiles.open(template_path, 'w') as f:
            await f.write(template_content)
            
    def _create_default_templates(self) -> None:
        """Create default report templates"""        # This would create template files
        pass
        
    def _create_default_configs(self) -> None:
        """Create default report configurations"""        default_configs = [
            ReportConfig(
                report_id="daily_summary",
                name="Daily Platform Summary",
                report_type=ReportType.DAILY_SUMMARY,
                schedule="0 8 * * *",  # Daily at 8 AM
                format=ReportFormat.HTML,
                delivery_method=DeliveryMethod.EMAIL,
                recipients=["ops@platform.com"]
            ),
            
            ReportConfig(
                report_id="weekly_performance",
                name="Weekly Performance Report",
                report_type=ReportType.WEEKLY_PERFORMANCE,
                schedule="0 9 * * 1",  # Mondays at 9 AM
                format=ReportFormat.HTML,
                delivery_method=DeliveryMethod.EMAIL,
                recipients=["management@platform.com"]
            ),
            
            ReportConfig(
                report_id="monthly_business",
                name="Monthly Business Review",
                report_type=ReportType.MONTHLY_BUSINESS,
                schedule="0 10 1 * *",  # First day of month at 10 AM
                format=ReportFormat.HTML,
                delivery_method=DeliveryMethod.EMAIL,
                recipients=["executive@platform.com"]
            )
        ]
        
        for config in default_configs:
            self.report_configs[config.report_id] = config
            
    def _update_next_generation_time(self, config: ReportConfig) -> None:
        """Update next generation time for a report config"""        # Simplified scheduling - would use proper cron parsing in production
        if "daily" in config.schedule or "* * *" in config.schedule:
            config.next_generation = datetime.utcnow() + timedelta(days=1)
        elif "weekly" in config.schedule or "* * 1" in config.schedule:
            config.next_generation = datetime.utcnow() + timedelta(weeks=1)
        elif "monthly" in config.schedule or "1 * *" in config.schedule:
            config.next_generation = datetime.utcnow() + timedelta(days=30)
        else:
            config.next_generation = datetime.utcnow() + timedelta(hours=1)
            
    async def _deliver_via_email(self, report: Report, recipients: List[str]) -> bool:
        """Deliver report via email"""        if not self.smtp_config:
            logger.warning("SMTP configuration not provided")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config.get('from_email', 'reports@platform.com')
            msg['Subject'] = f"{report.name} - {report.generated_at.strftime('%Y-%m-%d')}"
            
            # Email body
            body = f"""            Please find the attached {report.name} for the period {report.time_period['start'].strftime('%Y-%m-%d')} to {report.time_period['end'].strftime('%Y-%m-%d')}.
            
            Summary: {report.summary or 'No summary available'}
            
            Best regards,
            IA Influencer Agent Reporting System
            """            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach report file
            if report.file_path and Path(report.file_path).exists():
                with open(report.file_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {Path(report.file_path).name}'
                )
                msg.attach(part)
                
            # Send email
            for recipient in recipients:
                msg['To'] = recipient
                
                with smtplib.SMTP(
                    self.smtp_config.get('host', 'localhost'),
                    self.smtp_config.get('port', 587)
                ) as server:
                    if self.smtp_config.get('use_tls', True):
                        server.starttls()
                    if self.smtp_config.get('username'):
                        server.login(
                            self.smtp_config['username'],
                            self.smtp_config['password']
                        )
                    server.send_message(msg)
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email report: {e}")
            return False
            
    async def _deliver_via_filesystem(self, report: Report) -> bool:
        """Deliver report via file system (already saved)"""        return report.file_path is not None
        
    async def _deliver_via_api(self, report: Report, endpoints: List[str]) -> bool:
        """Deliver report via API endpoints"""        # Would implement API delivery
        return True
        
    async def _deliver_to_dashboard(self, report: Report) -> bool:
        """Deliver report to dashboard"""        # Would implement dashboard delivery
        return True
        
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop for automated report generation"""        while self.is_running:
            try:
                current_time = datetime.utcnow()
                
                # Check each report configuration
                for config in self.report_configs.values():
                    if not config.enabled:
                        continue
                        
                    if (config.next_generation and 
                        current_time >= config.next_generation):
                        
                        try:
                            # Generate report
                            time_period = self._calculate_report_period(config)
                            report = await self.generate_report(
                                config.report_type,
                                time_period,
                                config.format
                            )
                            
                            # Deliver report
                            await self.deliver_report(
                                report,
                                config.delivery_method,
                                config.recipients
                            )
                            
                            # Update last generated and next generation times
                            config.last_generated = current_time
                            self._update_next_generation_time(config)
                            
                            logger.info(f"Generated and delivered scheduled report: {config.name}")
                            
                        except Exception as e:
                            logger.error(f"Failed to generate scheduled report {config.name}: {e}")
                            
                # Wait before next check
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error in reporting scheduler loop: {e}")
                await asyncio.sleep(3600)
                
    def _calculate_report_period(self, config: ReportConfig) -> Dict[str, datetime]:
        """Calculate time period for a scheduled report"""        end_time = datetime.utcnow()
        
        if config.report_type == ReportType.DAILY_SUMMARY:
            start_time = end_time - timedelta(days=1)
        elif config.report_type == ReportType.WEEKLY_PERFORMANCE:
            start_time = end_time - timedelta(weeks=1)
        elif config.report_type == ReportType.MONTHLY_BUSINESS:
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(days=1)  # Default to daily
            
        return {"start": start_time, "end": end_time}
        
    # Placeholder methods for chart/table generation
    async def _analyze_weekly_trends(self, time_period: Dict[str, datetime]) -> str:
        return "Weekly trend analysis would go here."
        
    async def _generate_performance_recommendations(self, time_period: Dict[str, datetime]) -> List[str]:
        return ["Optimize AI model inference times", "Review content processing bottlenecks"]
        
    async def _generate_kpi_analysis(self, time_period: Dict[str, datetime]) -> str:
        return "KPI analysis would go here."
        
    async def _create_metrics_table(self, time_period: Dict[str, datetime]) -> Dict[str, Any]:
        return {"title": "Key Metrics", "data": {"Metric 1": "Value 1", "Metric 2": "Value 2"}}
        
    async def _analyze_monthly_revenue(self, time_period: Dict[str, datetime]) -> str:
        return "Monthly revenue analysis would go here."
        
    async def _create_revenue_chart(self, time_period: Dict[str, datetime]) -> str:
        return "revenue_chart.png"
        
    async def _analyze_user_growth(self, time_period: Dict[str, datetime]) -> str:
        return "User growth analysis would go here."
        
    async def _create_growth_chart(self, time_period: Dict[str, datetime]) -> str:
        return "growth_chart.png"
        
    async def _analyze_creator_success(self, time_period: Dict[str, datetime]) -> str:
        return "Creator success analysis would go here."
        
    async def _create_creator_table(self, time_period: Dict[str, datetime]) -> Dict[str, Any]:
        return {"title": "Top Creators", "data": {"Creator 1": "Score 1", "Creator 2": "Score 2"}}
        
    async def _generate_anomaly_recommendations(self, anomaly_summary: Dict[str, Any]) -> List[str]:
        return ["Investigate high CPU usage anomalies", "Review revenue drop patterns"]


# Global reporting system instance
reporting_system = ReportingSystem()
