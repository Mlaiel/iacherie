#!/usr/bin/env python3
"""
📊 REPORTING SERVICE
===================

Advanced automated reporting and document generation service for the Ainflue platform.
Handles business reports, analytics dashboards, compliance reports, and data exports.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code is proprietary and confidential. Unauthorized use, reproduction,
distribution, or modification is strictly prohibited and will be prosecuted
to the full extent of the law.
"""

import asyncio
import logging
import time
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import redis.asyncio as redis
from jinja2 import Template
import base64
from io import BytesIO
import plotly.graph_objs as go
import plotly.express as px

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Report type enumeration"""
    ANALYTICS_DASHBOARD = "analytics_dashboard"
    PERFORMANCE_SUMMARY = "performance_summary"
    REVENUE_REPORT = "revenue_report"
    ENGAGEMENT_ANALYSIS = "engagement_analysis"
    COMPLIANCE_REPORT = "compliance_report"
    CREATOR_INSIGHTS = "creator_insights"
    PLATFORM_COMPARISON = "platform_comparison"
    GROWTH_ANALYSIS = "growth_analysis"
    CUSTOM_REPORT = "custom_report"

class ReportFormat(Enum):
    """Report output format"""
    PDF = "pdf"
    HTML = "html"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    DASHBOARD = "dashboard"

class ReportSchedule(Enum):
    """Report generation schedule"""
    ON_DEMAND = "on_demand"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class ReportRequest:
    """Report generation request"""
    id: str
    report_type: ReportType
    format: ReportFormat
    title: str
    description: str
    creator_id: Optional[str] = None
    date_range: Dict[str, str] = None
    filters: Dict[str, Any] = None
    template_id: Optional[str] = None
    schedule: ReportSchedule = ReportSchedule.ON_DEMAND
    recipients: List[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.date_range is None:
            self.date_range = {
                "start": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "end": datetime.utcnow().isoformat()
            }
        if self.filters is None:
            self.filters = {}
        if self.recipients is None:
            self.recipients = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class GeneratedReport:
    """Generated report result"""
    id: str
    request_id: str
    report_type: ReportType
    format: ReportFormat
    title: str
    file_path: Optional[str] = None
    content: Optional[str] = None
    size_bytes: int = 0
    generation_time: float = 0.0
    charts: List[Dict[str, Any]] = None
    summary: Dict[str, Any] = None
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.charts is None:
            self.charts = []
        if self.summary is None:
            self.summary = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.expires_at is None:
            self.expires_at = datetime.utcnow() + timedelta(days=30)

@dataclass
class ReportTemplate:
    """Report template definition"""
    id: str
    name: str
    description: str
    report_type: ReportType
    template_content: str
    variables: List[str]
    chart_configs: List[Dict[str, Any]]
    created_by: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class ReportingMetrics:
    """Reporting service metrics"""
    total_reports: int = 0
    reports_by_type: Dict[str, int] = None
    reports_by_format: Dict[str, int] = None
    avg_generation_time: float = 0.0
    scheduled_reports: int = 0
    active_templates: int = 0
    
    def __post_init__(self):
        if self.reports_by_type is None:
            self.reports_by_type = {}
        if self.reports_by_format is None:
            self.reports_by_format = {}

class ReportingService:
    """Enterprise reporting service"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.reports: Dict[str, GeneratedReport] = {}
        self.templates: Dict[str, ReportTemplate] = {}
        self.scheduled_reports: Dict[str, ReportRequest] = {}
        self.metrics = ReportingMetrics()
        self.running = False
        self.redis_client = None
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize default templates
        self._init_default_templates()
    
    async def start(self) -> None:
        """Start the reporting service"""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            await self.redis_client.ping()
            
            self.running = True
            self.logger.info("🚀 Reporting Service started")
            
            # Start background tasks
            asyncio.create_task(self._scheduled_report_generator())
            asyncio.create_task(self._metrics_collector())
            asyncio.create_task(self._cleanup_expired_reports())
            
        except Exception as e:
            self.logger.error(f"❌ Error starting reporting service: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the reporting service"""
        try:
            self.running = False
            if self.redis_client:
                await self.redis_client.close()
            
            self.logger.info("🛑 Reporting Service stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping reporting service: {e}")
    
    def _init_default_templates(self) -> None:
        """Initialize default report templates"""
        # Analytics Dashboard Template
        analytics_template = ReportTemplate(
            id="analytics_dashboard",
            name="Analytics Dashboard",
            description="Comprehensive analytics dashboard with key metrics",
            report_type=ReportType.ANALYTICS_DASHBOARD,
            template_content="""
            <html>
            <head><title>{{title}}</title></head>
            <body>
                <h1>{{title}}</h1>
                <h2>Summary</h2>
                <p>Total Revenue: ${{summary.total_revenue}}</p>
                <p>Total Views: {{summary.total_views}}</p>
                <p>Engagement Rate: {{summary.engagement_rate}}%</p>
                
                <h2>Charts</h2>
                {% for chart in charts %}
                <div class="chart">
                    <h3>{{chart.title}}</h3>
                    <img src="data:image/png;base64,{{chart.image}}" />
                </div>
                {% endfor %}
            </body>
            </html>
            """,
            variables=["title", "summary", "charts"],
            chart_configs=[
                {"type": "line", "title": "Revenue Trend", "x": "date", "y": "revenue"},
                {"type": "bar", "title": "Platform Performance", "x": "platform", "y": "views"}
            ],
            created_by="system"
        )
        
        self.templates[analytics_template.id] = analytics_template
        
        # Performance Summary Template
        performance_template = ReportTemplate(
            id="performance_summary",
            name="Performance Summary",
            description="Weekly/Monthly performance summary report",
            report_type=ReportType.PERFORMANCE_SUMMARY,
            template_content="""
            # Performance Summary Report
            
            ## Executive Summary
            - **Total Revenue**: ${{summary.total_revenue}}
            - **Growth Rate**: {{summary.growth_rate}}%
            - **Top Platform**: {{summary.top_platform}}
            
            ## Key Metrics
            {% for metric in metrics %}
            - {{metric.name}}: {{metric.value}}
            {% endfor %}
            
            ## Recommendations
            {% for recommendation in recommendations %}
            - {{recommendation}}
            {% endfor %}
            """,
            variables=["summary", "metrics", "recommendations"],
            chart_configs=[
                {"type": "pie", "title": "Revenue by Platform", "values": "revenue", "labels": "platform"}
            ],
            created_by="system"
        )
        
        self.templates[performance_template.id] = performance_template
    
    async def generate_report(
        self,
        report_type: ReportType,
        format: ReportFormat,
        title: str,
        description: str = "",
        creator_id: Optional[str] = None,
        date_range: Optional[Dict[str, str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        template_id: Optional[str] = None
    ) -> str:
        """Generate a new report"""
        try:
            request_id = str(uuid.uuid4())
            
            request = ReportRequest(
                id=request_id,
                report_type=report_type,
                format=format,
                title=title,
                description=description,
                creator_id=creator_id,
                date_range=date_range,
                filters=filters,
                template_id=template_id
            )
            
            # Generate report
            start_time = time.time()
            report = await self._process_report_generation(request)
            generation_time = time.time() - start_time
            
            report.generation_time = generation_time
            self.reports[report.id] = report
            
            # Update metrics
            self.metrics.total_reports += 1
            if report_type.value not in self.metrics.reports_by_type:
                self.metrics.reports_by_type[report_type.value] = 0
            self.metrics.reports_by_type[report_type.value] += 1
            
            if format.value not in self.metrics.reports_by_format:
                self.metrics.reports_by_format[format.value] = 0
            self.metrics.reports_by_format[format.value] += 1
            
            # Cache in Redis
            if self.redis_client:
                await self.redis_client.setex(
                    f"report:{report.id}",
                    86400,  # 24 hours
                    json.dumps(asdict(report), default=str)
                )
            
            self.logger.info(f"✅ Generated report {report.id} in {generation_time:.2f}s")
            return report.id
            
        except Exception as e:
            self.logger.error(f"❌ Error generating report: {e}")
            raise
    
    async def _process_report_generation(self, request: ReportRequest) -> GeneratedReport:
        """Process report generation"""
        try:
            report_id = str(uuid.uuid4())
            
            # Get data for report
            data = await self._fetch_report_data(request)
            
            # Generate charts
            charts = await self._generate_charts(request, data)
            
            # Generate summary
            summary = await self._generate_summary(request, data)
            
            # Generate content based on format
            content = await self._generate_content(request, data, charts, summary)
            
            report = GeneratedReport(
                id=report_id,
                request_id=request.id,
                report_type=request.report_type,
                format=request.format,
                title=request.title,
                content=content,
                size_bytes=len(content.encode('utf-8')) if content else 0,
                charts=charts,
                summary=summary
            )
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error processing report generation: {e}")
            raise
    
    async def _fetch_report_data(self, request: ReportRequest) -> Dict[str, Any]:
        """Fetch data for report generation"""
        # Simulate data fetching - in real implementation, this would query databases
        
        if request.report_type == ReportType.ANALYTICS_DASHBOARD:
            return {
                "revenue_data": [
                    {"date": "2024-01-01", "revenue": 1500, "platform": "YouTube"},
                    {"date": "2024-01-02", "revenue": 2000, "platform": "Instagram"},
                    {"date": "2024-01-03", "revenue": 1800, "platform": "TikTok"},
                ],
                "engagement_data": [
                    {"platform": "YouTube", "views": 50000, "likes": 2500, "comments": 150},
                    {"platform": "Instagram", "views": 35000, "likes": 3200, "comments": 180},
                    {"platform": "TikTok", "views": 85000, "likes": 5500, "comments": 320},
                ]
            }
        
        elif request.report_type == ReportType.PERFORMANCE_SUMMARY:
            return {
                "metrics": [
                    {"name": "Total Revenue", "value": "$15,750", "change": "+12%"},
                    {"name": "Total Views", "value": "1.2M", "change": "+8%"},
                    {"name": "Engagement Rate", "value": "4.2%", "change": "+0.3%"},
                ],
                "platform_performance": [
                    {"platform": "YouTube", "revenue": 8500, "views": 450000},
                    {"platform": "Instagram", "revenue": 4200, "views": 280000},
                    {"platform": "TikTok", "revenue": 3050, "views": 470000},
                ]
            }
        
        return {"default": "No data available"}
    
    async def _generate_charts(self, request: ReportRequest, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate charts for report"""
        charts = []
        
        try:
            if request.report_type == ReportType.ANALYTICS_DASHBOARD:
                # Revenue trend chart
                if "revenue_data" in data:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    revenue_df = pd.DataFrame(data["revenue_data"])
                    
                    ax.plot(pd.to_datetime(revenue_df["date"]), revenue_df["revenue"], marker='o')
                    ax.set_title("Revenue Trend")
                    ax.set_xlabel("Date")
                    ax.set_ylabel("Revenue ($)")
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    
                    # Convert to base64
                    buffer = BytesIO()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    chart_image = base64.b64encode(buffer.getvalue()).decode()
                    plt.close()
                    
                    charts.append({
                        "title": "Revenue Trend",
                        "type": "line",
                        "image": chart_image
                    })
                
                # Platform performance chart
                if "engagement_data" in data:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    engagement_df = pd.DataFrame(data["engagement_data"])
                    
                    ax.bar(engagement_df["platform"], engagement_df["views"])
                    ax.set_title("Platform Performance")
                    ax.set_xlabel("Platform")
                    ax.set_ylabel("Views")
                    plt.tight_layout()
                    
                    buffer = BytesIO()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    chart_image = base64.b64encode(buffer.getvalue()).decode()
                    plt.close()
                    
                    charts.append({
                        "title": "Platform Performance",
                        "type": "bar",
                        "image": chart_image
                    })
            
            elif request.report_type == ReportType.PERFORMANCE_SUMMARY:
                # Platform revenue pie chart
                if "platform_performance" in data:
                    fig, ax = plt.subplots(figsize=(8, 8))
                    platform_df = pd.DataFrame(data["platform_performance"])
                    
                    ax.pie(platform_df["revenue"], labels=platform_df["platform"], autopct='%1.1f%%')
                    ax.set_title("Revenue by Platform")
                    
                    buffer = BytesIO()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    chart_image = base64.b64encode(buffer.getvalue()).decode()
                    plt.close()
                    
                    charts.append({
                        "title": "Revenue by Platform",
                        "type": "pie",
                        "image": chart_image
                    })
            
        except Exception as e:
            self.logger.error(f"❌ Error generating charts: {e}")
        
        return charts
    
    async def _generate_summary(self, request: ReportRequest, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report summary"""
        summary = {}
        
        try:
            if request.report_type == ReportType.ANALYTICS_DASHBOARD:
                if "revenue_data" in data:
                    revenue_df = pd.DataFrame(data["revenue_data"])
                    summary["total_revenue"] = revenue_df["revenue"].sum()
                
                if "engagement_data" in data:
                    engagement_df = pd.DataFrame(data["engagement_data"])
                    summary["total_views"] = engagement_df["views"].sum()
                    summary["total_likes"] = engagement_df["likes"].sum()
                    summary["engagement_rate"] = round(
                        (engagement_df["likes"].sum() / engagement_df["views"].sum()) * 100, 2
                    )
            
            elif request.report_type == ReportType.PERFORMANCE_SUMMARY:
                if "platform_performance" in data:
                    platform_df = pd.DataFrame(data["platform_performance"])
                    summary["total_revenue"] = platform_df["revenue"].sum()
                    summary["top_platform"] = platform_df.loc[platform_df["revenue"].idxmax(), "platform"]
                    summary["growth_rate"] = 12.5  # Simulated growth rate
            
        except Exception as e:
            self.logger.error(f"❌ Error generating summary: {e}")
        
        return summary
    
    async def _generate_content(
        self,
        request: ReportRequest,
        data: Dict[str, Any],
        charts: List[Dict[str, Any]],
        summary: Dict[str, Any]
    ) -> str:
        """Generate report content"""
        try:
            if request.format == ReportFormat.JSON:
                return json.dumps({
                    "title": request.title,
                    "summary": summary,
                    "charts": charts,
                    "data": data,
                    "generated_at": datetime.utcnow().isoformat()
                }, indent=2)
            
            elif request.format == ReportFormat.CSV:
                # Convert data to CSV format
                if request.report_type == ReportType.ANALYTICS_DASHBOARD and "revenue_data" in data:
                    df = pd.DataFrame(data["revenue_data"])
                    return df.to_csv(index=False)
            
            elif request.format == ReportFormat.HTML:
                # Use template if available
                template_id = request.template_id or request.report_type.value
                template = self.templates.get(template_id)
                
                if template:
                    jinja_template = Template(template.template_content)
                    return jinja_template.render(
                        title=request.title,
                        summary=summary,
                        charts=charts,
                        data=data
                    )
                else:
                    # Default HTML format
                    html_content = f"""
                    <html>
                    <head><title>{request.title}</title></head>
                    <body>
                        <h1>{request.title}</h1>
                        <h2>Summary</h2>
                        <pre>{json.dumps(summary, indent=2)}</pre>
                        <h2>Data</h2>
                        <pre>{json.dumps(data, indent=2)}</pre>
                    </body>
                    </html>
                    """
                    return html_content
            
            # Default: return JSON
            return json.dumps({
                "title": request.title,
                "summary": summary,
                "data": data
            }, indent=2)
            
        except Exception as e:
            self.logger.error(f"❌ Error generating content: {e}")
            return f"Error generating report content: {e}"
    
    async def schedule_report(
        self,
        report_type: ReportType,
        format: ReportFormat,
        title: str,
        schedule: ReportSchedule,
        recipients: List[str],
        creator_id: Optional[str] = None,
        template_id: Optional[str] = None
    ) -> str:
        """Schedule recurring report generation"""
        try:
            schedule_id = str(uuid.uuid4())
            
            request = ReportRequest(
                id=schedule_id,
                report_type=report_type,
                format=format,
                title=title,
                description=f"Scheduled {schedule.value} report",
                creator_id=creator_id,
                template_id=template_id,
                schedule=schedule,
                recipients=recipients
            )
            
            self.scheduled_reports[schedule_id] = request
            self.metrics.scheduled_reports += 1
            
            self.logger.info(f"✅ Scheduled {schedule.value} report {schedule_id}")
            return schedule_id
            
        except Exception as e:
            self.logger.error(f"❌ Error scheduling report: {e}")
            raise
    
    async def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get generated report"""
        try:
            report = self.reports.get(report_id)
            if report:
                return asdict(report)
            
            # Try Redis cache
            if self.redis_client:
                cached = await self.redis_client.get(f"report:{report_id}")
                if cached:
                    return json.loads(cached)
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Error getting report: {e}")
            return None
    
    async def _scheduled_report_generator(self) -> None:
        """Generate scheduled reports"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                
                for schedule_id, request in self.scheduled_reports.items():
                    if await self._should_generate_report(request, current_time):
                        # Generate report
                        report_id = await self.generate_report(
                            request.report_type,
                            request.format,
                            f"{request.title} - {current_time.strftime('%Y-%m-%d')}",
                            request.description,
                            request.creator_id,
                            template_id=request.template_id
                        )
                        
                        self.logger.info(f"📊 Generated scheduled report {report_id}")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"❌ Error in scheduled report generation: {e}")
                await asyncio.sleep(300)
    
    async def _should_generate_report(self, request: ReportRequest, current_time: datetime) -> bool:
        """Check if scheduled report should be generated"""
        # Simplified logic - in real implementation, track last generation times
        if request.schedule == ReportSchedule.DAILY:
            return current_time.hour == 9  # Generate at 9 AM
        elif request.schedule == ReportSchedule.WEEKLY:
            return current_time.weekday() == 0 and current_time.hour == 9  # Monday at 9 AM
        elif request.schedule == ReportSchedule.MONTHLY:
            return current_time.day == 1 and current_time.hour == 9  # 1st of month at 9 AM
        
        return False
    
    async def _metrics_collector(self) -> None:
        """Collect reporting metrics"""
        while self.running:
            try:
                # Update metrics
                self.metrics.active_templates = len(self.templates)
                
                if self.reports:
                    generation_times = [r.generation_time for r in self.reports.values() if r.generation_time > 0]
                    if generation_times:
                        self.metrics.avg_generation_time = sum(generation_times) / len(generation_times)
                
                # Store in Redis
                if self.redis_client:
                    await self.redis_client.setex(
                        "reporting:metrics",
                        300,  # 5 minutes
                        json.dumps(asdict(self.metrics), default=str)
                    )
                
                await asyncio.sleep(300)  # Update every 5 minutes
                
            except Exception as e:
                self.logger.error(f"❌ Error collecting metrics: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired_reports(self) -> None:
        """Clean up expired reports"""
        while self.running:
            try:
                current_time = datetime.utcnow()
                expired_reports = []
                
                for report_id, report in self.reports.items():
                    if report.expires_at and report.expires_at <= current_time:
                        expired_reports.append(report_id)
                
                for report_id in expired_reports:
                    del self.reports[report_id]
                
                if expired_reports:
                    self.logger.info(f"🧹 Cleaned up {len(expired_reports)} expired reports")
                
                await asyncio.sleep(3600)  # Clean every hour
                
            except Exception as e:
                self.logger.error(f"❌ Error in report cleanup: {e}")
                await asyncio.sleep(300)
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get reporting service metrics"""
        return asdict(self.metrics)
    
    async def create_template(
        self,
        name: str,
        description: str,
        report_type: ReportType,
        template_content: str,
        created_by: str
    ) -> str:
        """Create a new report template"""
        try:
            template_id = str(uuid.uuid4())
            
            template = ReportTemplate(
                id=template_id,
                name=name,
                description=description,
                report_type=report_type,
                template_content=template_content,
                variables=[],  # Extract from template content
                chart_configs=[],
                created_by=created_by
            )
            
            self.templates[template_id] = template
            
            self.logger.info(f"✅ Created report template {template_id}")
            return template_id
            
        except Exception as e:
            self.logger.error(f"❌ Error creating template: {e}")
            raise


# Example usage and testing
async def main():
    """Test the reporting service"""
    service = ReportingService()
    
    try:
        await service.start()
        
        # Generate analytics dashboard
        dashboard_id = await service.generate_report(
            ReportType.ANALYTICS_DASHBOARD,
            ReportFormat.HTML,
            "Weekly Analytics Dashboard",
            "Comprehensive weekly performance analysis",
            "creator_123"
        )
        
        # Generate performance summary
        summary_id = await service.generate_report(
            ReportType.PERFORMANCE_SUMMARY,
            ReportFormat.JSON,
            "Monthly Performance Summary",
            "Monthly performance metrics and insights"
        )
        
        # Schedule weekly report
        schedule_id = await service.schedule_report(
            ReportType.ANALYTICS_DASHBOARD,
            ReportFormat.HTML,
            "Weekly Automated Report",
            ReportSchedule.WEEKLY,
            ["manager@company.com", "creator@company.com"]
        )
        
        # Get reports
        dashboard = await service.get_report(dashboard_id)
        summary = await service.get_report(summary_id)
        
        print(f"Dashboard Report: {len(dashboard['content'])} characters")
        print(f"Summary Report: {len(summary['content'])} characters")
        
        # Get metrics
        metrics = await service.get_metrics()
        print(f"Service Metrics: {metrics}")
        
    finally:
        await service.stop()


if __name__ == "__main__":
    asyncio.run(main())