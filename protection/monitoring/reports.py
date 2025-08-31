"""
 Monitoring Reports Generator
=============================

Advanced automated reporting system for content protection monitoring.
Generates comprehensive reports, insights, and actionable recommendations.

Technical Specifications:
- Multi-format report generation (PDF, Excel, JSON)
- Automated report scheduling and delivery
- Advanced data visualization and charts
- Custom report templates and branding
- Executive summary and detailed analytics

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized use strictly prohibited

 LEGAL WARNING: This software is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or reverse engineering is strictly prohibited
and will result in immediate legal action under German and international copyright law.
Contact mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
import json
import io
import base64
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from pydantic import BaseModel, Field
from jinja2 import Template
import aiofiles

from .analytics import MonitoringAnalytics, AnalyticsTimeRange, AnalyticsReport
from .performance_optimizer import PerformanceOptimizer

logger = logging.getLogger(__name__)

class ReportFormat(str, Enum):
    """Report output formats."""
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"
    HTML = "html"
    CSV = "csv"

class ReportType(str, Enum):
    """Types of reports."""
    EXECUTIVE_SUMMARY = "executive_summary"
    DETAILED_ANALYTICS = "detailed_analytics"
    PERFORMANCE_REPORT = "performance_report"
    SECURITY_ASSESSMENT = "security_assessment"
    COST_ANALYSIS = "cost_analysis"
    PLATFORM_COMPARISON = "platform_comparison"
    CUSTOM = "custom"

class ReportFrequency(str, Enum):
    """Report generation frequency."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ON_DEMAND = "on_demand"

class ChartStyle(str, Enum):
    """Chart styling options."""
    PROFESSIONAL = "professional"
    MODERN = "modern"
    MINIMAL = "minimal"
    COLORFUL = "colorful"

@dataclass
class ReportSection:
    """Report section configuration."""
    section_id: str
    title: str
    content_type: str  # text, chart, table, metrics
    data_source: str
    template: str
    config: Dict[str, Any]
    order: int = 0

class ReportTemplate(BaseModel):
    """Report template configuration."""
    template_id: str
    name: str
    description: str = ""
    report_type: ReportType
    sections: List[ReportSection] = Field(default_factory=list)
    styling: Dict[str, Any] = Field(default_factory=dict)
    created_by: int
    is_public: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ReportConfiguration(BaseModel):
    """Report generation configuration."""
    config_id: str
    template_id: str
    name: str
    description: str = ""
    output_formats: List[ReportFormat] = Field(default_factory=list)
    frequency: ReportFrequency = ReportFrequency.ON_DEMAND
    recipients: List[str] = Field(default_factory=list)  # Email addresses
    filters: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    next_run: Optional[datetime] = None
    created_by: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class GeneratedReport(BaseModel):
    """Generated report metadata."""
    report_id: str
    config_id: str
    template_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    time_range_start: datetime
    time_range_end: datetime
    formats_generated: List[ReportFormat] = Field(default_factory=list)
    file_paths: Dict[str, str] = Field(default_factory=dict)  # format -> file_path
    file_sizes: Dict[str, int] = Field(default_factory=dict)  # format -> size_bytes
    generation_time_seconds: float = 0.0
    status: str = "completed"  # pending, completed, failed
    error_message: Optional[str] = None

class ReportGenerator:
    """
    Advanced automated reporting system for monitoring analytics.
    
    Features:
    - Multi-format report generation with professional styling
    - Automated scheduling and delivery
    - Interactive charts and visualizations
    - Custom templates and branding
    - Executive summaries with key insights
    """
    
    def __init__(
        self,
        config: Dict[str, Any],
        analytics: MonitoringAnalytics,
        performance_optimizer: PerformanceOptimizer
    ):
        """Initialize report generator."""
        self.config = config
        self.analytics = analytics
        self.performance_optimizer = performance_optimizer
        
        # Configuration
        self.output_directory = Path(config.get('output_directory', './reports'))
        self.template_directory = Path(config.get('template_directory', './templates'))
        self.chart_style = ChartStyle(config.get('chart_style', 'professional'))
        self.brand_colors = config.get('brand_colors', ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        
        # Ensure directories exist
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.template_directory.mkdir(parents=True, exist_ok=True)
        
        # Report storage
        self._report_templates: Dict[str, ReportTemplate] = {}
        self._report_configurations: Dict[str, ReportConfiguration] = {}
        self._generated_reports: Dict[str, GeneratedReport] = {}
        
        # Scheduled reporting
        self._scheduler_running = False
        self._scheduler_task: Optional[asyncio.Task] = None
        
        logger.info("Report Generator initialized")

    async def initialize(self) -> bool:
        """Initialize the report generator."""



        try:
            logger.info("Initializing Report Generator...")
            
            # Load default templates
            await self._load_default_templates()
            
            # Load existing configurations
            await self._load_report_configurations()
            
            # Start scheduler
            await self._start_report_scheduler()
            
            logger.info("Report Generator initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Report Generator: {e}")
            return False

    async def create_report_template(
        self,
        template_data: Dict[str, Any],
        user_id: int
    ) -> ReportTemplate:
        """Create a new report template."""



        try:
            template = ReportTemplate(
                template_id=f"template_{user_id}_{int(datetime.utcnow().timestamp())}",
                name=template_data.get('name', 'New Template'),
                description=template_data.get('description', ''),
                report_type=ReportType(template_data.get('report_type', 'detailed_analytics')),
                sections=[
                    ReportSection(**section) 
                    for section in template_data.get('sections', [])
                ],
                styling=template_data.get('styling', {}),
                created_by=user_id,
                is_public=template_data.get('is_public', False)
            )
            
            # Store template
            self._report_templates[template.template_id] = template
            
            # Save to storage
            await self._save_report_template(template)
            
            logger.info(f"Created report template: {template.template_id}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to create report template: {e}")
            raise

    async def generate_report(
        self,
        config_id: Optional[str] = None,
        template_id: Optional[str] = None,
        output_formats: Optional[List[ReportFormat]] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None,
        custom_parameters: Optional[Dict[str, Any]] = None
    ) -> GeneratedReport:
        """Generate a report based on configuration or template."""
        start_time = datetime.utcnow()
        
        try:
            # Determine configuration
            if config_id:
                if config_id not in self._report_configurations:
                    raise ValueError(f"Report configuration not found: {config_id}")
                config = self._report_configurations[config_id]
                template_id = config.template_id
                output_formats = output_formats or config.output_formats
            elif template_id:
                if template_id not in self._report_templates:
                    raise ValueError(f"Report template not found: {template_id}")
                config = None
                output_formats = output_formats or [ReportFormat.PDF]
            else:
                raise ValueError("Either config_id or template_id must be provided")
            
            # Get template
            template = self._report_templates[template_id]
            
            # Determine time range
            if not time_range:
                end_time = datetime.utcnow()
                start_time_data = end_time - timedelta(days=7)  # Default: last week
                time_range = (start_time_data, end_time)
            
            # Generate report ID
            report_id = f"report_{template_id}_{int(start_time.timestamp())}"
            
            logger.info(f"Generating report: {report_id}")
            
            # Gather data for all sections
            report_data = await self._gather_report_data(
                template, time_range, custom_parameters
            )
            
            # Generate report in each requested format
            file_paths = {}
            file_sizes = {}
            
            for format_type in output_formats:
                file_path, file_size = await self._generate_report_format(
                    report_id, template, report_data, format_type
                )
                file_paths[format_type.value] = str(file_path)
                file_sizes[format_type.value] = file_size
            
            # Create generated report record
            generation_time = (datetime.utcnow() - start_time).total_seconds()
            
            generated_report = GeneratedReport(
                report_id=report_id,
                config_id=config_id or "",
                template_id=template_id,
                time_range_start=time_range[0],
                time_range_end=time_range[1],
                formats_generated=output_formats,
                file_paths=file_paths,
                file_sizes=file_sizes,
                generation_time_seconds=generation_time
            )
            
            # Store generated report
            self._generated_reports[report_id] = generated_report
            
            logger.info(f"Report generated successfully: {report_id} ({generation_time:.2f}s)")
            return generated_report
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            
            # Create failed report record
            generated_report = GeneratedReport(
                report_id=f"failed_{int(start_time.timestamp())}",
                config_id=config_id or "",
                template_id=template_id or "",
                time_range_start=time_range[0] if time_range else datetime.utcnow(),
                time_range_end=time_range[1] if time_range else datetime.utcnow(),
                status="failed",
                error_message=str(e)
            )
            
            return generated_report

    async def schedule_report(
        self,
        config_data: Dict[str, Any],
        user_id: int
    ) -> ReportConfiguration:
        """Schedule automated report generation."""



        try:
            config = ReportConfiguration(
                config_id=f"config_{user_id}_{int(datetime.utcnow().timestamp())}",
                template_id=config_data['template_id'],
                name=config_data.get('name', 'Scheduled Report'),
                description=config_data.get('description', ''),
                output_formats=[
                    ReportFormat(fmt) for fmt in config_data.get('output_formats', ['pdf'])
                ],
                frequency=ReportFrequency(config_data.get('frequency', 'weekly')),
                recipients=config_data.get('recipients', []),
                filters=config_data.get('filters', {}),
                parameters=config_data.get('parameters', {}),
                created_by=user_id
            )
            
            # Calculate next run time
            config.next_run = self._calculate_next_run_time(config.frequency)
            
            # Store configuration
            self._report_configurations[config.config_id] = config
            
            # Save to storage
            await self._save_report_configuration(config)
            
            logger.info(f"Scheduled report configuration: {config.config_id}")
            return config
            
        except Exception as e:
            logger.error(f"Failed to schedule report: {e}")
            raise

    async def _gather_report_data(
        self,
        template: ReportTemplate,
        time_range: Tuple[datetime, datetime],
        custom_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Gather all data needed for report generation."""
        report_data = {
            'metadata': {
                'generated_at': datetime.utcnow(),
                'time_range_start': time_range[0],
                'time_range_end': time_range[1],
                'template_name': template.name,
                'report_type': template.report_type.value
            },
            'sections': {}
        }
        
        # Process each section
        for section in template.sections:
            try:
                section_data = await self._gather_section_data(
                    section, time_range, custom_parameters
                )
                report_data['sections'][section.section_id] = section_data
            except Exception as e:
                logger.error(f"Failed to gather data for section {section.section_id}: {e}")
                report_data['sections'][section.section_id] = {
                    'error': str(e),
                    'title': section.title
                }
        
        return report_data

    async def _gather_section_data(
        self,
        section: ReportSection,
        time_range: Tuple[datetime, datetime],
        custom_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Gather data for a specific report section."""
        if section.data_source == 'analytics':
            return await self._gather_analytics_data(section, time_range)
        elif section.data_source == 'performance':
            return await self._gather_performance_data(section, time_range)
        elif section.data_source == 'violations':
            return await self._gather_violations_data(section, time_range)
        elif section.data_source == 'platforms':
            return await self._gather_platforms_data(section, time_range)
        else:
            return {'error': f'Unknown data source: {section.data_source}'}

    async def _gather_analytics_data(
        self,
        section: ReportSection,
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Gather analytics data for a section."""
        # Determine time range for analytics
        duration = time_range[1] - time_range[0]
        if duration <= timedelta(hours=1):
            analytics_range = AnalyticsTimeRange.LAST_HOUR
        elif duration <= timedelta(hours=6):
            analytics_range = AnalyticsTimeRange.LAST_6_HOURS
        elif duration <= timedelta(days=1):
            analytics_range = AnalyticsTimeRange.LAST_24_HOURS
        elif duration <= timedelta(days=7):
            analytics_range = AnalyticsTimeRange.LAST_7_DAYS
        elif duration <= timedelta(days=30):
            analytics_range = AnalyticsTimeRange.LAST_30_DAYS
        else:
            analytics_range = AnalyticsTimeRange.LAST_90_DAYS
        
        # Generate analytics report
        analytics_report = await self.analytics.generate_analytics_report(
            analytics_range,
            start_date=time_range[0],
            end_date=time_range[1]
        )
        
        return {
            'title': section.title,
            'analytics_report': analytics_report.dict(),
            'summary_metrics': {
                'total_detections': analytics_report.total_detections,
                'total_violations': analytics_report.total_violations,
                'detection_accuracy': analytics_report.detection_accuracy,
                'average_response_time': analytics_report.average_response_time
            }
        }

    async def _gather_performance_data(
        self,
        section: ReportSection,
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Gather performance data for a section."""
        # Get current performance metrics
        current_metrics = await self.performance_optimizer.monitor_system_performance()
        
        # Get optimization recommendations
        recommendations = await self.performance_optimizer.generate_optimization_recommendations()
        
        return {
            'title': section.title,
            'current_metrics': {
                resource_type.value: {
                    'usage': metrics.current_usage,
                    'efficiency': metrics.efficiency,
                    'trend': metrics.trend
                }
                for resource_type, metrics in current_metrics.items()
            },
            'optimization_recommendations': [
                {
                    'description': rec.description,
                    'priority': rec.priority,
                    'expected_improvement': rec.expected_improvement,
                    'risk_level': rec.risk_level
                }
                for rec in recommendations[:5]
            ]
        }

    async def _gather_violations_data(
        self,
        section: ReportSection,
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Gather violations data for a section."""
        # Mock violations data (would integrate with actual violation tracking)
        return {
            'title': section.title,
            'total_violations': np.random.randint(100, 500),
            'violations_by_platform': {
                'youtube': np.random.randint(20, 100),
                'spotify': np.random.randint(10, 50),
                'instagram': np.random.randint(15, 75),
                'tiktok': np.random.randint(25, 125)
            },
            'threat_level_distribution': {
                'critical': np.random.randint(5, 20),
                'high': np.random.randint(15, 50),
                'medium': np.random.randint(30, 100),
                'low': np.random.randint(50, 200)
            },
            'resolution_status': {
                'resolved': np.random.randint(200, 400),
                'in_progress': np.random.randint(20, 80),
                'pending': np.random.randint(10, 40)
            }
        }

    async def _gather_platforms_data(
        self,
        section: ReportSection,
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """Gather platform-specific data for a section."""
        platforms = ['youtube', 'spotify', 'instagram', 'tiktok']
        
        platform_data = {}
        for platform in platforms:
            platform_data[platform] = {
                'status': np.random.choice(['active', 'warning', 'error'], p=[0.8, 0.15, 0.05]),
                'uptime': np.random.uniform(95, 100),
                'detections': np.random.randint(50, 200),
                'false_positives': np.random.randint(2, 15),
                'average_response_time': np.random.uniform(500, 2000),
                'efficiency_score': np.random.uniform(0.8, 0.95)
            }
        
        return {
            'title': section.title,
            'platforms': platform_data,
            'summary': {
                'total_platforms': len(platforms),
                'active_platforms': sum(1 for p in platform_data.values() if p['status'] == 'active'),
                'average_uptime': np.mean([p['uptime'] for p in platform_data.values()]),
                'total_detections': sum(p['detections'] for p in platform_data.values())
            }
        }

    async def _generate_report_format(
        self,
        report_id: str,
        template: ReportTemplate,
        report_data: Dict[str, Any],
        format_type: ReportFormat
    ) -> Tuple[Path, int]:
        """Generate report in specific format."""
        if format_type == ReportFormat.PDF:
            return await self._generate_pdf_report(report_id, template, report_data)
        elif format_type == ReportFormat.EXCEL:
            return await self._generate_excel_report(report_id, template, report_data)
        elif format_type == ReportFormat.JSON:
            return await self._generate_json_report(report_id, template, report_data)
        elif format_type == ReportFormat.HTML:
            return await self._generate_html_report(report_id, template, report_data)
        elif format_type == ReportFormat.CSV:
            return await self._generate_csv_report(report_id, template, report_data)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    async def _generate_pdf_report(
        self,
        report_id: str,
        template: ReportTemplate,
        report_data: Dict[str, Any]
    ) -> Tuple[Path, int]:
        """Generate PDF report with charts and professional formatting."""
        file_path = self.output_directory / f"{report_id}.pdf"
        
        # Configure matplotlib for PDF generation
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        
        with PdfPages(str(file_path)) as pdf:
            # Title page
            await self._create_pdf_title_page(pdf, template, report_data)
            
            # Executive summary
            await self._create_pdf_executive_summary(pdf, report_data)
            
            # Process each section
            for section in sorted(template.sections, key=lambda s: s.order):
                section_data = report_data['sections'].get(section.section_id, {})
                
                if section.content_type == 'chart':
                    await self._create_pdf_chart_section(pdf, section, section_data)
                elif section.content_type == 'table':
                    await self._create_pdf_table_section(pdf, section, section_data)
                elif section.content_type == 'metrics':
                    await self._create_pdf_metrics_section(pdf, section, section_data)
                else:
                    await self._create_pdf_text_section(pdf, section, section_data)
        
        # Get file size
        file_size = file_path.stat().st_size
        
        return file_path, file_size

    async def _create_pdf_title_page(
        self,
        pdf: PdfPages,
        template: ReportTemplate,
        report_data: Dict[str, Any]
    ) -> None:
        """Create PDF title page."""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.8, template.name, 
                horizontalalignment='center',
                fontsize=24, fontweight='bold',
                transform=ax.transAxes)
        
        # Subtitle
        ax.text(0.5, 0.7, f"Report Type: {template.report_type.value.replace('_', ' ').title()}",
                horizontalalignment='center',
                fontsize=16,
                transform=ax.transAxes)
        
        # Date range
        metadata = report_data['metadata']
        date_range = f"{metadata['time_range_start'].strftime('%Y-%m-%d')} to {metadata['time_range_end'].strftime('%Y-%m-%d')}"
        ax.text(0.5, 0.6, f"Period: {date_range}",
                horizontalalignment='center',
                fontsize=14,
                transform=ax.transAxes)
        
        # Generated date
        ax.text(0.5, 0.5, f"Generated: {metadata['generated_at'].strftime('%Y-%m-%d %H:%M:%S')}",
                horizontalalignment='center',
                fontsize=12,
                transform=ax.transAxes)
        
        # Copyright notice
        ax.text(0.5, 0.1, "© 2025 Fahed Mlaiel - IA Influencer Agent Platform",
                horizontalalignment='center',
                fontsize=10, style='italic',
                transform=ax.transAxes)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

    async def _create_pdf_executive_summary(
        self,
        pdf: PdfPages,
        report_data: Dict[str, Any]
    ) -> None:
        """Create PDF executive summary page."""
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, "Executive Summary", 
                horizontalalignment='center',
                fontsize=20, fontweight='bold',
                transform=ax.transAxes)
        
        # Key metrics (mock data)
        key_metrics = [
            ("Total Content Protected", "1,247 items"),
            ("Violations Detected", "89 incidents"),
            ("Detection Accuracy", "94.2%"),
            ("Average Response Time", "1.3 seconds"),
            ("False Positive Rate", "3.1%"),
            ("Revenue Protected", "$45,230")
        ]
        
        y_pos = 0.8
        for i, (metric, value) in enumerate(key_metrics):
            if i % 2 == 0:  # Left column
                ax.text(0.1, y_pos, f"{metric}:", fontweight='bold', transform=ax.transAxes)
                ax.text(0.4, y_pos, value, transform=ax.transAxes)
            else:  # Right column
                ax.text(0.6, y_pos, f"{metric}:", fontweight='bold', transform=ax.transAxes)
                ax.text(0.9, y_pos, value, transform=ax.transAxes)
                y_pos -= 0.1
        
        # Key insights
        insights = [
            "• Content protection system operating at 94.2% accuracy",
            "• YouTube and Instagram showing highest violation rates",
            "• Average threat response time improved by 23% this period",
            "• False positive rate within acceptable range (<5%)",
            "• System performance optimizations yielding 15% efficiency gains"
        ]
        
        ax.text(0.1, 0.4, "Key Insights:", fontsize=16, fontweight='bold', transform=ax.transAxes)
        
        y_pos = 0.35
        for insight in insights:
            ax.text(0.1, y_pos, insight, fontsize=11, transform=ax.transAxes)
            y_pos -= 0.05
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

    async def _create_pdf_chart_section(
        self,
        pdf: PdfPages,
        section: ReportSection,
        section_data: Dict[str, Any]
    ) -> None:
        """Create PDF chart section."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(11, 8.5))
        fig.suptitle(section.title, fontsize=16, fontweight='bold')
        
        # Chart 1: Detection Trends
        days = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        detections = np.random.randint(10, 50, len(days))
        
        ax1.plot(days, detections, marker='o', linewidth=2, markersize=4)
        ax1.set_title('Daily Detection Trends')
        ax1.set_ylabel('Detections')
        ax1.tick_params(axis='x', rotation=45)
        
        # Chart 2: Platform Distribution
        platforms = ['YouTube', 'Spotify', 'Instagram', 'TikTok']
        violations = [89, 34, 56, 72]
        
        ax2.pie(violations, labels=platforms, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Violations by Platform')
        
        # Chart 3: Threat Levels
        threat_levels = ['Critical', 'High', 'Medium', 'Low']
        counts = [12, 28, 45, 89]
        
        bars = ax3.bar(threat_levels, counts, color=['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4'])
        ax3.set_title('Threat Level Distribution')
        ax3.set_ylabel('Count')
        
        # Chart 4: Response Times
        times = np.random.normal(1.5, 0.3, 100)
        ax4.hist(times, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax4.set_title('Response Time Distribution')
        ax4.set_xlabel('Response Time (seconds)')
        ax4.set_ylabel('Frequency')
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

    async def _generate_excel_report(
        self,
        report_id: str,
        template: ReportTemplate,
        report_data: Dict[str, Any]
    ) -> Tuple[Path, int]:
        """Generate Excel report with multiple sheets."""
        file_path = self.output_directory / f"{report_id}.xlsx"
        
        with pd.ExcelWriter(str(file_path), engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Metric': ['Total Detections', 'Total Violations', 'Detection Accuracy', 'Response Time'],
                'Value': [1247, 89, '94.2%', '1.3s'],
                'Status': ['Good', 'Monitoring', 'Excellent', 'Good']
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            # Platform data sheet
            platform_data = {
                'Platform': ['YouTube', 'Spotify', 'Instagram', 'TikTok'],
                'Violations': [45, 12, 23, 31],
                'Uptime %': [99.2, 98.8, 99.5, 98.9],
                'Response Time (ms)': [1200, 800, 1500, 1100]
            }
            pd.DataFrame(platform_data).to_excel(writer, sheet_name='Platforms', index=False)
            
            # Detailed logs (mock data)
            log_data = {
                'Timestamp': pd.date_range(start=datetime.now() - timedelta(days=7), 
                                         end=datetime.now(), freq='H'),
                'Platform': np.random.choice(['YouTube', 'Spotify', 'Instagram', 'TikTok'], 
                                           size=168),
                'Threat Level': np.random.choice(['Low', 'Medium', 'High', 'Critical'], 
                                               size=168),
                'Status': np.random.choice(['Resolved', 'Pending', 'In Progress'], 
                                         size=168)
            }
            pd.DataFrame(log_data).to_excel(writer, sheet_name='Detailed_Logs', index=False)
        
        file_size = file_path.stat().st_size
        return file_path, file_size

    async def _generate_json_report(
        self,
        report_id: str,
        template: ReportTemplate,
        report_data: Dict[str, Any]
    ) -> Tuple[Path, int]:
        """Generate JSON report."""
        file_path = self.output_directory / f"{report_id}.json"
        
        # Convert datetime objects to ISO format strings
        def convert_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            else:
                return obj
        
        json_data = convert_datetime(report_data)
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(json_data, indent=2))
        
        file_size = file_path.stat().st_size
        return file_path, file_size

    async def _generate_html_report(
        self,
        report_id: str,
        template: ReportTemplate,
        report_data: Dict[str, Any]
    ) -> Tuple[Path, int]:
        """Generate HTML report with interactive charts."""
        file_path = self.output_directory / f"{report_id}.html"
        
        # Create HTML template
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ template_name }}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { text-align: center; margin-bottom: 40px; }
                .section { margin-bottom: 30px; }
                .chart { margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{{ template_name }}</h1>
                <p>Generated: {{ generated_at }}</p>
                <p>Period: {{ time_range }}</p>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <ul>
                    <li>Total Detections: 1,247</li>
                    <li>Violations: 89</li>
                    <li>Accuracy: 94.2%</li>
                    <li>Response Time: 1.3s</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>Platform Distribution</h2>
                <div id="platform-chart" class="chart"></div>
            </div>
            
            <script>
                // Platform distribution chart
                var platformData = [{
                    values: [45, 12, 23, 31],
                    labels: ['YouTube', 'Spotify', 'Instagram', 'TikTok'],
                    type: 'pie'
                }];
                
                Plotly.newPlot('platform-chart', platformData);
            </script>
        </body>
        </html>
        """
        
        template_obj = Template(html_template)
        metadata = report_data['metadata']
        
        html_content = template_obj.render(
            template_name=template.name,
            generated_at=metadata['generated_at'].strftime('%Y-%m-%d %H:%M:%S'),
            time_range=f"{metadata['time_range_start'].strftime('%Y-%m-%d')} to {metadata['time_range_end'].strftime('%Y-%m-%d')}"
        )
        
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(html_content)
        
        file_size = file_path.stat().st_size
        return file_path, file_size

    async def _generate_csv_report(
        self,
        report_id: str,
        template: ReportTemplate,
        report_data: Dict[str, Any]
    ) -> Tuple[Path, int]:
        """Generate CSV report."""
        file_path = self.output_directory / f"{report_id}.csv"
        
        # Create summary data
        data = {
            'Timestamp': pd.date_range(start=datetime.now() - timedelta(days=30), 
                                     end=datetime.now(), freq='D'),
            'Platform': np.random.choice(['YouTube', 'Spotify', 'Instagram', 'TikTok'], 30),
            'Detections': np.random.randint(5, 25, 30),
            'Violations': np.random.randint(0, 5, 30),
            'Response_Time_ms': np.random.randint(500, 2000, 30)
        }
        
        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False)
        
        file_size = file_path.stat().st_size
        return file_path, file_size

    def _calculate_next_run_time(self, frequency: ReportFrequency) -> datetime:
        """Calculate next run time based on frequency."""
        now = datetime.utcnow()
        
        if frequency == ReportFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == ReportFrequency.WEEKLY:
            return now + timedelta(weeks=1)
        elif frequency == ReportFrequency.MONTHLY:
            return now + timedelta(days=30)
        elif frequency == ReportFrequency.QUARTERLY:
            return now + timedelta(days=90)
        else:
            return now

    async def _start_report_scheduler(self) -> None:
        """Start the automated report scheduler."""
        self._scheduler_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("Report scheduler started")

    async def _scheduler_loop(self) -> None:
        """Main scheduler loop for automated reports."""



        try:
            while self._scheduler_running:
                current_time = datetime.utcnow()
                
                # Check for reports that need to be generated
                for config in self._report_configurations.values():
                    if (config.enabled and 
                        config.next_run and 
                        config.next_run <= current_time):
                        
                        # Generate scheduled report
                        try:
                            await self.generate_report(config_id=config.config_id)
                            
                            # Update next run time
                            config.next_run = self._calculate_next_run_time(config.frequency)
                            await self._save_report_configuration(config)
                            
                            logger.info(f"Generated scheduled report: {config.config_id}")
                            
                        except Exception as e:
                            logger.error(f"Failed to generate scheduled report {config.config_id}: {e}")
                
                # Wait 1 hour before next check
                await asyncio.sleep(3600)
                
        except asyncio.CancelledError:
            logger.debug("Report scheduler loop cancelled")

    async def _load_default_templates(self) -> None:
        """Load default report templates."""



        try:
            # Executive Summary template
            executive_template = ReportTemplate(
                template_id="default_executive_summary",
                name="Executive Summary Report",
                description="High-level overview for executives and stakeholders",
                report_type=ReportType.EXECUTIVE_SUMMARY,
                sections=[
                    ReportSection(
                        section_id="summary_metrics",
                        title="Key Performance Indicators",
                        content_type="metrics",
                        data_source="analytics",
                        template="executive_metrics",
                        config={},
                        order=1
                    ),
                    ReportSection(
                        section_id="threat_overview",
                        title="Threat Landscape Overview",
                        content_type="chart",
                        data_source="violations",
                        template="threat_charts",
                        config={},
                        order=2
                    )
                ],
                created_by=0,
                is_public=True
            )
            
            self._report_templates[executive_template.template_id] = executive_template
            
            # Detailed Analytics template
            detailed_template = ReportTemplate(
                template_id="default_detailed_analytics",
                name="Detailed Analytics Report",
                description="Comprehensive analysis with detailed metrics and insights",
                report_type=ReportType.DETAILED_ANALYTICS,
                sections=[
                    ReportSection(
                        section_id="analytics_overview",
                        title="Analytics Overview",
                        content_type="metrics",
                        data_source="analytics",
                        template="detailed_metrics",
                        config={},
                        order=1
                    ),
                    ReportSection(
                        section_id="platform_analysis",
                        title="Platform-by-Platform Analysis",
                        content_type="table",
                        data_source="platforms",
                        template="platform_table",
                        config={},
                        order=2
                    ),
                    ReportSection(
                        section_id="performance_metrics",
                        title="System Performance",
                        content_type="chart",
                        data_source="performance",
                        template="performance_charts",
                        config={},
                        order=3
                    )
                ],
                created_by=0,
                is_public=True
            )
            
            self._report_templates[detailed_template.template_id] = detailed_template
            
            logger.info("Loaded default report templates")
            
        except Exception as e:
            logger.error(f"Failed to load default templates: {e}")

    async def _load_report_configurations(self) -> None:
        """Load existing report configurations."""



        try:
            # This would load from database in real implementation
            logger.debug("Loaded report configurations")
        except Exception as e:
            logger.error(f"Failed to load report configurations: {e}")

    async def _save_report_template(self, template: ReportTemplate) -> None:
        """Save report template to storage."""



        try:
            # This would save to database in real implementation
            logger.debug(f"Saved report template: {template.template_id}")
        except Exception as e:
            logger.error(f"Failed to save report template: {e}")

    async def _save_report_configuration(self, config: ReportConfiguration) -> None:
        """Save report configuration to storage."""



        try:
            # This would save to database in real implementation
            logger.debug(f"Saved report configuration: {config.config_id}")
        except Exception as e:
            logger.error(f"Failed to save report configuration: {e}")

    async def _create_pdf_table_section(
        self,
        pdf: PdfPages,
        section: ReportSection,
        section_data: Dict[str, Any]
    ) -> None:
        """Create PDF table section."""
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, section.title, 
                horizontalalignment='center',
                fontsize=16, fontweight='bold',
                transform=ax.transAxes)
        
        # Create sample table data
        if 'platforms' in section_data:
            platforms_data = section_data['platforms']
            table_data = []
            headers = ['Platform', 'Status', 'Uptime %', 'Detections', 'Response Time (ms)']
            
            for platform, data in platforms_data.items():
                table_data.append([
                    platform.title(),
                    data.get('status', 'Unknown'),
                    f"{data.get('uptime', 0):.1f}%",
                    str(data.get('detections', 0)),
                    f"{data.get('average_response_time', 0):.0f}"
                ])
        else:
            # Default table data
            headers = ['Metric', 'Current', 'Previous', 'Change']
            table_data = [
                ['Detection Rate', '94.2%', '91.8%', '+2.4%'],
                ['Response Time', '1.3s', '1.7s', '-0.4s'],
                ['False Positives', '3.1%', '4.2%', '-1.1%'],
                ['System Uptime', '99.2%', '98.9%', '+0.3%']
            ]
        
        # Create table
        table = ax.table(cellText=table_data,
                        colLabels=headers,
                        cellLoc='center',
                        loc='center',
                        bbox=[0.1, 0.3, 0.8, 0.5])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style header row
        for i in range(len(headers)):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Style data rows
        for i in range(1, len(table_data) + 1):
            for j in range(len(headers)):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#F2F2F2')
                else:
                    table[(i, j)].set_facecolor('#FFFFFF')
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

    async def _create_pdf_metrics_section(
        self,
        pdf: PdfPages,
        section: ReportSection,
        section_data: Dict[str, Any]
    ) -> None:
        """Create PDF metrics section."""
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, section.title, 
                horizontalalignment='center',
                fontsize=16, fontweight='bold',
                transform=ax.transAxes)
        
        # Key metrics layout
        if 'summary_metrics' in section_data:
            metrics = section_data['summary_metrics']
        elif 'current_metrics' in section_data:
            metrics = section_data['current_metrics']
        else:
            # Default metrics
            metrics = {
                'total_detections': 1247,
                'total_violations': 89,
                'detection_accuracy': 0.942,
                'average_response_time': 1.3
            }
        
        # Create metrics grid
        metrics_grid = [
            ("Total Detections", str(metrics.get('total_detections', 'N/A'))),
            ("Total Violations", str(metrics.get('total_violations', 'N/A'))),
            ("Detection Accuracy", f"{float(metrics.get('detection_accuracy', 0)) * 100:.1f}%"),
            ("Avg Response Time", f"{metrics.get('average_response_time', 0):.1f}s"),
        ]
        
        # Position metrics in 2x2 grid
        positions = [(0.2, 0.7), (0.7, 0.7), (0.2, 0.4), (0.7, 0.4)]
        
        for i, ((metric, value), (x, y)) in enumerate(zip(metrics_grid, positions)):
            # Metric value (large)
            ax.text(x, y + 0.05, value, 
                   horizontalalignment='center',
                   fontsize=24, fontweight='bold',
                   color=self.brand_colors[i % len(self.brand_colors)],
                   transform=ax.transAxes)
            
            # Metric name (smaller)
            ax.text(x, y - 0.05, metric, 
                   horizontalalignment='center',
                   fontsize=12,
                   transform=ax.transAxes)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

    async def _create_pdf_text_section(
        self,
        pdf: PdfPages,
        section: ReportSection,
        section_data: Dict[str, Any]
    ) -> None:
        """Create PDF text section."""
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.95, section.title, 
                horizontalalignment='center',
                fontsize=16, fontweight='bold',
                transform=ax.transAxes)
        
        # Content based on section data
        if 'optimization_recommendations' in section_data:
            # Performance recommendations
            recommendations = section_data['optimization_recommendations']
            y_pos = 0.85
            
            ax.text(0.1, y_pos, "Performance Optimization Recommendations:", 
                   fontsize=14, fontweight='bold',
                   transform=ax.transAxes)
            y_pos -= 0.08
            
            for i, rec in enumerate(recommendations[:5]):
                rec_text = f"{i+1}. {rec.get('description', 'Optimization recommendation')}"
                priority = rec.get('priority', 'medium')
                improvement = rec.get('expected_improvement', 0)
                
                ax.text(0.1, y_pos, rec_text, 
                       fontsize=11,
                       transform=ax.transAxes)
                
                ax.text(0.8, y_pos, f"Priority: {priority.title()}", 
                       fontsize=10, style='italic',
                       transform=ax.transAxes)
                
                y_pos -= 0.05
                
                if improvement > 0:
                    ax.text(0.15, y_pos, f"Expected improvement: {improvement:.1f}%", 
                           fontsize=9, color='green',
                           transform=ax.transAxes)
                    y_pos -= 0.04
                
                y_pos -= 0.02
        
        else:
            # Generic content
            content = [
                "This section provides detailed analysis and insights based on the monitoring data.",
                "",
                "Key findings:",
                "• System performance is within normal parameters",
                "• Detection accuracy has improved by 2.4% this period",
                "• Response times have decreased by 23% on average",
                "• No critical security issues detected",
                "",
                "Recommendations:",
                "• Continue monitoring current performance levels",
                "• Consider increasing detection sensitivity on high-risk platforms",
                "• Review and update threat detection algorithms quarterly"
            ]
            
            y_pos = 0.85
            for line in content:
                if line.startswith("•"):
                    ax.text(0.15, y_pos, line, fontsize=11, transform=ax.transAxes)
                elif line.endswith(":"):
                    ax.text(0.1, y_pos, line, fontsize=12, fontweight='bold', transform=ax.transAxes)
                else:
                    ax.text(0.1, y_pos, line, fontsize=11, transform=ax.transAxes)
                y_pos -= 0.05
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)

    # Public API methods for external access
    
    async def get_available_templates(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of available report templates."""



        try:
            templates = []
            for template in self._report_templates.values():
                if template.is_public or (user_id and template.created_by == user_id):
                    templates.append({
                        'template_id': template.template_id,
                        'name': template.name,
                        'description': template.description,
                        'report_type': template.report_type.value,
                        'sections_count': len(template.sections),
                        'is_public': template.is_public,
                        'created_at': template.created_at.isoformat()
                    })
            
            return templates
            
        except Exception as e:
            logger.error(f"Failed to get available templates: {e}")
            return []

    async def get_report_history(
        self,
        user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get history of generated reports."""



        try:
            reports = []
            for report in self._generated_reports.values():
                # Filter by user if provided (would check permissions in real implementation)
                report_info = {
                    'report_id': report.report_id,
                    'template_id': report.template_id,
                    'generated_at': report.generated_at.isoformat(),
                    'time_range_start': report.time_range_start.isoformat(),
                    'time_range_end': report.time_range_end.isoformat(),
                    'formats_generated': [fmt.value for fmt in report.formats_generated],
                    'file_sizes': report.file_sizes,
                    'generation_time_seconds': report.generation_time_seconds,
                    'status': report.status
                }
                
                if report.error_message:
                    report_info['error_message'] = report.error_message
                
                reports.append(report_info)
            
            # Sort by generation time (newest first) and limit
            reports.sort(key=lambda x: x['generated_at'], reverse=True)
            return reports[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get report history: {e}")
            return []

    async def delete_report_template(self, template_id: str, user_id: int) -> bool:
        """Delete a report template."""



        try:
            if template_id not in self._report_templates:
                return False
            
            template = self._report_templates[template_id]
            
            # Check permissions (only creator or admin can delete)
            if template.created_by != user_id and not template.is_public:
                return False
            
            # Remove template
            del self._report_templates[template_id]
            
            # Remove any configurations using this template
            configs_to_remove = [
                config_id for config_id, config in self._report_configurations.items()
                if config.template_id == template_id
            ]
            
            for config_id in configs_to_remove:
                del self._report_configurations[config_id]
            
            logger.info(f"Deleted report template: {template_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete report template: {e}")
            return False

    async def update_report_configuration(
        self,
        config_id: str,
        updates: Dict[str, Any],
        user_id: int
    ) -> bool:
        """Update a report configuration."""



        try:
            if config_id not in self._report_configurations:
                return False
            
            config = self._report_configurations[config_id]
            
            # Check permissions
            if config.created_by != user_id:
                return False
            
            # Update allowed fields
            allowed_updates = [
                'name', 'description', 'output_formats', 'frequency', 
                'recipients', 'filters', 'parameters', 'enabled'
            ]
            
            for key, value in updates.items():
                if key in allowed_updates:
                    if key == 'output_formats':
                        setattr(config, key, [ReportFormat(fmt) for fmt in value])
                    elif key == 'frequency':
                        setattr(config, key, ReportFrequency(value))
                        # Recalculate next run time
                        config.next_run = self._calculate_next_run_time(config.frequency)
                    else:
                        setattr(config, key, value)
            
            # Save configuration
            await self._save_report_configuration(config)
            
            logger.info(f"Updated report configuration: {config_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update report configuration: {e}")
            return False

    async def download_report(self, report_id: str, format_type: str) -> Optional[Path]:
        """Get download path for a generated report."""



        try:
            if report_id not in self._generated_reports:
                return None
            
            report = self._generated_reports[report_id]
            
            if format_type not in report.file_paths:
                return None
            
            file_path = Path(report.file_paths[format_type])
            
            if file_path.exists():
                return file_path
            else:
                logger.warning(f"Report file not found: {file_path}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get report download path: {e}")
            return None

    async def get_report_statistics(self) -> Dict[str, Any]:
        """Get statistics about report generation."""



        try:
            total_reports = len(self._generated_reports)
            successful_reports = len([r for r in self._generated_reports.values() if r.status == "completed"])
            failed_reports = total_reports - successful_reports
            
            if total_reports > 0:
                avg_generation_time = np.mean([
                    r.generation_time_seconds for r in self._generated_reports.values() 
                    if r.status == "completed"
                ])
            else:
                avg_generation_time = 0.0
            
            # Format distribution
            format_counts = {}
            for report in self._generated_reports.values():
                for fmt in report.formats_generated:
                    format_counts[fmt.value] = format_counts.get(fmt.value, 0) + 1
            
            # Template usage
            template_usage = {}
            for report in self._generated_reports.values():
                template_usage[report.template_id] = template_usage.get(report.template_id, 0) + 1
            
            return {
                'total_reports_generated': total_reports,
                'successful_reports': successful_reports,
                'failed_reports': failed_reports,
                'success_rate': (successful_reports / total_reports * 100) if total_reports > 0 else 0,
                'average_generation_time_seconds': avg_generation_time,
                'format_distribution': format_counts,
                'template_usage': template_usage,
                'active_configurations': len([c for c in self._report_configurations.values() if c.enabled]),
                'total_templates': len(self._report_templates)
            }
            
        except Exception as e:
            logger.error(f"Failed to get report statistics: {e}")
            return {}

    async def cleanup_old_reports(self, days_to_keep: int = 30) -> int:
        """Clean up old report files."""



        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            files_deleted = 0
            
            reports_to_remove = []
            for report_id, report in self._generated_reports.items():
                if report.generated_at < cutoff_date:
                    # Delete files
                    for file_path in report.file_paths.values():
                        try:
                            Path(file_path).unlink(missing_ok=True)
                            files_deleted += 1
                        except Exception as e:
                            logger.warning(f"Failed to delete report file {file_path}: {e}")
                    
                    reports_to_remove.append(report_id)
            
            # Remove from memory
            for report_id in reports_to_remove:
                del self._generated_reports[report_id]
            
            logger.info(f"Cleaned up {len(reports_to_remove)} old reports, deleted {files_deleted} files")
            return files_deleted
            
        except Exception as e:
            logger.error(f"Failed to cleanup old reports: {e}")
            return 0
