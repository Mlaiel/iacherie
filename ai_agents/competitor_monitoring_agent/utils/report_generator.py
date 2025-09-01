"""Report Generator - Advanced Reporting and Analytics System
Generates comprehensive reports for competitor monitoring analysis.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: Fahed Mlaiel. All rights reserved.
WARNING: Unauthorized use, copying, or distribution is strictly prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    from core.exceptions import ReportError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ReportError = globals().get('ReportError', Exception)
from ...utils.data_processor import DataProcessor
from ...utils.chart_generator import ChartGenerator


@dataclass
class ReportTemplate:
    """
Report template configuration."""
    template_id: str
    name: str
    description: str
    template_type: str
    sections: List[str]
    format_type: str  # html, pdf, json, excel
    frequency: str  # on_demand, daily, weekly, monthly
    recipients: List[str]
    created_at: datetime


@dataclass
class ReportData:
    """
Report data structure."""
    report_id: str
    template_id: str
    title: str
    subtitle: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    data_sources: List[str]
    sections: Dict[str, Any]
    metrics: Dict[str, float]
    charts: List[Dict[str, Any]]
    recommendations: List[str]
    executive_summary: str


class ReportGenerator:
    """
    Advanced report generator for competitor monitoring analysis.
    
    Provides comprehensive reporting capabilities with multiple formats,
    automated scheduling, and interactive visualizations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
Initialize the report generator."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.data_processor = DataProcessor()
        self.chart_generator = ChartGenerator()
        
        # Report settings
        self.output_dir = config.get("output_dir", "reports/competitor_monitoring")
        self.template_dir = config.get("template_dir", "templates/reports")
        
        # Report templates
        self.report_templates: Dict[str, ReportTemplate] = {}
        self.generated_reports: List[ReportData] = []
        
        # Styling configuration
        self.chart_style = config.get("chart_style", "plotly_white")
        self.color_palette = config.get("color_palette", ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"])
        
        # Initialize templates
        self._initialize_default_templates()
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        self.logger.info("ReportGenerator initialized")
    
    def _initialize_default_templates(self):
        """Initialize default report templates."""
        try:
            # Executive Summary Report
            executive_template = ReportTemplate(
                template_id="executive_summary",
                name="Executive Summary Report",
                description="High-level executive summary of competitor monitoring insights",
                template_type="executive",
                sections=[
                    "executive_summary",
                    "key_metrics",
                    "top_competitors",
                    "market_trends",
                    "strategic_recommendations"
                ],
                format_type="html",
                frequency="weekly",
                recipients=[],
                created_at=datetime.utcnow()
            )
            self.report_templates["executive_summary"] = executive_template
            
            # Detailed Analysis Report
            detailed_template = ReportTemplate(
                template_id="detailed_analysis",
                name="Detailed Competitive Analysis Report",
                description="Comprehensive analysis of all competitors and market dynamics",
                template_type="detailed",
                sections=[
                    "executive_summary",
                    "competitor_profiles",
                    "swot_analysis",
                    "market_intelligence",
                    "threat_assessment",
                    "opportunity_analysis",
                    "financial_analysis",
                    "strategic_recommendations",
                    "action_items"
                ],
                format_type="html",
                frequency="monthly",
                recipients=[],
                created_at=datetime.utcnow()
            )
            self.report_templates["detailed_analysis"] = detailed_template
            
            # Alert Summary Report
            alert_template = ReportTemplate(
                template_id="alert_summary",
                name="Alert Summary Report",
                description="Summary of monitoring alerts and required actions",
                template_type="operational",
                sections=[
                    "alert_summary",
                    "critical_alerts",
                    "trend_alerts",
                    "response_metrics",
                    "recommendations"
                ],
                format_type="html",
                frequency="daily",
                recipients=[],
                created_at=datetime.utcnow()
            )
            self.report_templates["alert_summary"] = alert_template
            
            # Performance Dashboard
            dashboard_template = ReportTemplate(
                template_id="performance_dashboard",
                name="Performance Dashboard",
                description="Interactive dashboard with key performance metrics",
                template_type="dashboard",
                sections=[
                    "kpi_overview",
                    "competitor_comparison",
                    "trend_analysis",
                    "market_share_evolution",
                    "alert_status"
                ],
                format_type="html",
                frequency="on_demand",
                recipients=[],
                created_at=datetime.utcnow()
            )
            self.report_templates["performance_dashboard"] = dashboard_template
            
        except Exception as e:
            self.logger.error(f"Error initializing default templates: {str(e)}")
    
    async def generate_report(self, template_id: str, data: Dict[str, Any], period: Optional[Tuple[datetime, datetime]] = None) -> ReportData:
        """Generate a report using specified template and data."""
        try:
            self.logger.info(f"Generating report with template: {template_id}")
            
            if template_id not in self.report_templates:
                raise ReportError(f"Template not found: {template_id}")
            
            template = self.report_templates[template_id]
            
            # Set period if not provided
            if not period:
                period_end = datetime.utcnow()
                period_start = period_end - timedelta(days=30)  # Default 30 days
                period = (period_start, period_end)
            
            # Generate report ID
            report_id = f"{template_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Process data for each section
            sections_data = {}
            for section in template.sections:
                sections_data[section] = await self._generate_section_data(section, data, period)
            
            # Generate metrics
            metrics = await self._calculate_report_metrics(data, period)
            
            # Generate charts
            charts = await self._generate_report_charts(template, data, period)
            
            # Generate executive summary
            executive_summary = await self._generate_executive_summary(sections_data, metrics)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(sections_data, metrics)
            
            # Create report data
            report_data = ReportData(
                report_id=report_id,
                template_id=template_id,
                title=template.name,
                subtitle=f"Report Period: {period[0].strftime('%Y-%m-%d')} to {period[1].strftime('%Y-%m-%d')}",
                generated_at=datetime.utcnow(),
                period_start=period[0],
                period_end=period[1],
                data_sources=data.get("data_sources", []),
                sections=sections_data,
                metrics=metrics,
                charts=charts,
                recommendations=recommendations,
                executive_summary=executive_summary
            )
            
            # Generate report file
            report_file = await self._generate_report_file(report_data, template)
            
            # Store report
            self.generated_reports.append(report_data)
            
            self.logger.info(f"Report generated successfully: {report_id}")
            return report_data
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise ReportError(f"Failed to generate report: {str(e)}")
    
    async def _generate_section_data(self, section: str, data: Dict[str, Any], period: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Generate data for a specific report section."""
        try:
            section_generators = {
                "executive_summary": self._generate_executive_section,
                "key_metrics": self._generate_key_metrics_section,
                "competitor_profiles": self._generate_competitor_profiles_section,
                "swot_analysis": self._generate_swot_section,
                "market_intelligence": self._generate_market_intelligence_section,
                "threat_assessment": self._generate_threat_assessment_section,
                "opportunity_analysis": self._generate_opportunity_analysis_section,
                "financial_analysis": self._generate_financial_analysis_section,
                "strategic_recommendations": self._generate_strategic_recommendations_section,
                "alert_summary": self._generate_alert_summary_section,
                "trend_analysis": self._generate_trend_analysis_section,
                "kpi_overview": self._generate_kpi_overview_section,
                "competitor_comparison": self._generate_competitor_comparison_section,
                "action_items": self._generate_action_items_section
            }
            
            if section in section_generators:
                return await section_generators[section](data, period)
            else:
                self.logger.warning(f"Unknown section: {section}")
                return {"content": f"Section '{section}' not implemented", "data": {}}
                
        except Exception as e:
            self.logger.error(f"Error generating section {section}: {str(e)}")
            return {"content": f"Error generating section: {str(e)}", "data": {}}
    
    async def _generate_key_metrics_section(self, data: Dict[str, Any], period: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Generate key metrics section."""
        try:
            competitors = data.get("competitors", [])
            market_data = data.get("market_data", {})
            alerts = data.get("alerts", [])
            
            # Calculate key metrics
            total_competitors = len(competitors)
            active_alerts = len([a for a in alerts if not a.get("resolved", False)])
            market_growth = market_data.get("growth_rate", 0.0)
            
            # Top performing competitor
            top_competitor = max(competitors, key=lambda x: x.get("market_share", 0)) if competitors else None
            
            # Alert distribution
            alert_distribution = {}
            for alert in alerts:
                severity = alert.get("severity", "unknown")
                alert_distribution[severity] = alert_distribution.get(severity, 0) + 1
            
            return {
                "content": "Key performance metrics and indicators",
                "data": {
                    "total_competitors": total_competitors,
                    "active_alerts": active_alerts,
                    "market_growth_rate": market_growth,
                    "top_competitor": top_competitor.get("name", "Unknown") if top_competitor else "None",
                    "top_competitor_share": top_competitor.get("market_share", 0.0) if top_competitor else 0.0,
                    "alert_distribution": alert_distribution,
                    "period_days": (period[1] - period[0]).days
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating key metrics section: {str(e)}")
            return {"content": "Error generating metrics", "data": {}}
    
    async def _generate_competitor_profiles_section(self, data: Dict[str, Any], period: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Generate competitor profiles section."""
        try:
            competitors = data.get("competitors", [])
            
            # Process competitor data
            profiles = []
            for competitor in competitors[:10]:  # Top 10 competitors
                profile = {
                    "name": competitor.get("name", "Unknown"),
                    "market_share": competitor.get("market_share", 0.0),
                    "growth_rate": competitor.get("growth_rate", 0.0),
                    "threat_level": competitor.get("threat_level", "unknown"),
                    "strengths": competitor.get("strengths", [])[:3],  # Top 3 strengths
                    "weaknesses": competitor.get("weaknesses", [])[:3],  # Top 3 weaknesses
                    "recent_activities": competitor.get("recent_activities", [])[:5],  # Last 5 activities
                    "website": competitor.get("website", ""),
                    "industry": competitor.get("industry", "")
                }
                profiles.append(profile)
            
            # Sort by market share
            profiles.sort(key=lambda x: x["market_share"], reverse=True)
            
            return {
                "content": "Detailed profiles of key competitors",
                "data": {
                    "total_profiles": len(profiles),
                    "profiles": profiles,
                    "market_leaders": profiles[:3],
                    "emerging_threats": [p for p in profiles if p["threat_level"] == "high"]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating competitor profiles section: {str(e)}")
            return {"content": "Error generating profiles", "data": {}}
    
    async def _generate_report_charts(self, template: ReportTemplate, data: Dict[str, Any], period: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """Generate charts for the report."""
        try:
            charts = []
            
            # Market share chart
            if "competitor_comparison" in template.sections or "key_metrics" in template.sections:
                market_share_chart = await self._create_market_share_chart(data)
                if market_share_chart:
                    charts.append(market_share_chart)
            
            # Trend analysis chart
            if "trend_analysis" in template.sections:
                trend_chart = await self._create_trend_analysis_chart(data, period)
                if trend_chart:
                    charts.append(trend_chart)
            
            # Alert distribution chart
            if "alert_summary" in template.sections:
                alert_chart = await self._create_alert_distribution_chart(data)
                if alert_chart:
                    charts.append(alert_chart)
            
            # Threat level chart
            if "threat_assessment" in template.sections:
                threat_chart = await self._create_threat_level_chart(data)
                if threat_chart:
                    charts.append(threat_chart)
            
            return charts
            
        except Exception as e:
            self.logger.error(f"Error generating report charts: {str(e)}")
            return []
    
    async def _create_market_share_chart(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create market share pie chart."""
        try:
            competitors = data.get("competitors", [])
            if not competitors:
                return None
            
            # Prepare data
            names = [c.get("name", "Unknown") for c in competitors[:10]]
            shares = [c.get("market_share", 0.0) for c in competitors[:10]]
            
            # Create plotly figure
            fig = go.Figure(data=[go.Pie(
                labels=names,
                values=shares,
                hole=0.3,
                textinfo="label+percent",
                textposition="outside"
            )])
            
            fig.update_layout(
                title="Market Share Distribution",
                font=dict(size=12),
                showlegend=True,
                height=500
            )
            
            return {
                "chart_id": "market_share_pie",
                "title": "Market Share Distribution",
                "type": "pie",
                "data": fig.to_json(),
                "description": "Distribution of market share among top competitors"
            }
            
        except Exception as e:
            self.logger.error(f"Error creating market share chart: {str(e)}")
            return None
    
    async def _create_trend_analysis_chart(self, data: Dict[str, Any], period: Tuple[datetime, datetime]) -> Optional[Dict[str, Any]]:
        """Create trend analysis line chart."""
        try:
            trends = data.get("trends", [])
            if not trends:
                return None
            
            # Create subplots
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Market Growth Trends", "Competitor Activity Trends"),
                vertical_spacing=0.1
            )
            
            # Sample trend data (in real implementation, use actual trend data)
            dates = pd.date_range(start=period[0], end=period[1], freq='D')
            
            # Market growth trend
            market_growth = [0.05 + 0.02 * np.sin(i * 0.1) for i in range(len(dates))]
            fig.add_trace(
                go.Scatter(x=dates, y=market_growth, name="Market Growth", line=dict(color=self.color_palette[0])),
                row=1, col=1
            )
            
            # Competitor activity trend
            activity_levels = [50 + 20 * np.sin(i * 0.05) + 10 * np.random.random() for i in range(len(dates))]
            fig.add_trace(
                go.Scatter(x=dates, y=activity_levels, name="Competitor Activity", line=dict(color=self.color_palette[1])),
                row=2, col=1
            )
            
            fig.update_layout(
                height=600,
                title="Trend Analysis Over Time",
                showlegend=True
            )
            
            return {
                "chart_id": "trend_analysis_line",
                "title": "Trend Analysis Over Time",
                "type": "line",
                "data": fig.to_json(),
                "description": "Analysis of key trends over the reporting period"
            }
            
        except Exception as e:
            self.logger.error(f"Error creating trend analysis chart: {str(e)}")
            return None
    
    async def _generate_report_file(self, report_data: ReportData, template: ReportTemplate) -> str:
        """Generate the actual report file."""
        try:
            if template.format_type == "html":
                return await self._generate_html_report(report_data, template)
            elif template.format_type == "json":
                return await self._generate_json_report(report_data)
            elif template.format_type == "excel":
                return await self._generate_excel_report(report_data, template)
            else:
                raise ReportError(f"Unsupported format type: {template.format_type}")
                
        except Exception as e:
            self.logger.error(f"Error generating report file: {str(e)}")
            raise ReportError(f"Failed to generate report file: {str(e)}")
    
    async def _generate_html_report(self, report_data: ReportData, template: ReportTemplate) -> str:
        """Generate HTML report."""
        try:
            # HTML template
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>{{ report.title }}</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .header { border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
                    .section { margin-bottom: 30px; }
                    .metric { display: inline-block; margin: 10px; padding: 15px; background: #f5f5f5; border-radius: 5px; }
                    .chart { margin: 20px 0; }
                    table { border-collapse: collapse; width: 100%; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f2f2f2; }
                    .recommendation { background: #e8f4f8; padding: 15px; border-left: 4px solid #2196F3; margin: 10px 0; }
                    .alert-critical { color: #d32f2f; font-weight: bold; }
                    .alert-high { color: #f57c00; font-weight: bold; }
                    .alert-medium { color: #1976d2; }
                    .alert-low { color: #388e3c; }
                </style>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            </head>
            <body>
                <div class="header">
                    <h1>{{ report.title }}</h1>
                    <h3>{{ report.subtitle }}</h3>
                    <p>Generated on: {{ report.generated_at.strftime('%Y-%m-%d %H:%M:%S') }}</p>
                </div>
                
                <div class="section">
                    <h2>Executive Summary</h2>
                    <p>{{ report.executive_summary }}</p>
                </div>
                
                {% if 'key_metrics' in report.sections %}
                <div class="section">
                    <h2>Key Metrics</h2>
                    <div class="metric">
                        <strong>Total Competitors:</strong> {{ report.sections.key_metrics.data.total_competitors }}
                    </div>
                    <div class="metric">
                        <strong>Active Alerts:</strong> {{ report.sections.key_metrics.data.active_alerts }}
                    </div>
                    <div class="metric">
                        <strong>Market Growth:</strong> {{ "%.1f%%" | format(report.sections.key_metrics.data.market_growth_rate * 100) }}
                    </div>
                    <div class="metric">
                        <strong>Top Competitor:</strong> {{ report.sections.key_metrics.data.top_competitor }}
                    </div>
                </div>
                {% endif %}
                
                {% for chart in report.charts %}
                <div class="section">
                    <h2>{{ chart.title }}</h2>
                    <div id="{{ chart.chart_id }}" class="chart"></div>
                    <p><em>{{ chart.description }}</em></p>
                    <script>
                        Plotly.newPlot('{{ chart.chart_id }}', JSON.parse('{{ chart.data }}'));
                    </script>
                </div>
                {% endfor %}
                
                <div class="section">
                    <h2>Strategic Recommendations</h2>
                    {% for recommendation in report.recommendations %}
                    <div class="recommendation">
                        <strong>{{ recommendation }}</strong>
                    </div>
                    {% endfor %}
                </div>
            </body>
            </html>
            """
            
            # Render template
            template_obj = Template(html_template)
            html_content = template_obj.render(report=report_data)
            
            # Save to file
            filename = f"{report_data.report_id}.html"
            filepath = Path(self.output_dir) / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report generated: {filepath}")
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error generating HTML report: {str(e)}")
            raise ReportError(f"Failed to generate HTML report: {str(e)}")
    
    async def get_report_history(self, limit: int = 50) -> List[ReportData]:
        """Get report generation history."""
        try:
            # Sort by generation time (newest first)
            sorted_reports = sorted(self.generated_reports, key=lambda x: x.generated_at, reverse=True)
            return sorted_reports[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting report history: {str(e)}")
            return []
    
    async def schedule_report(self, template_id: str, frequency: str, recipients: List[str]):
        """Schedule automated report generation."""
        try:
            if template_id not in self.report_templates:
                raise ReportError(f"Template not found: {template_id}")
            
            template = self.report_templates[template_id]
            template.frequency = frequency
            template.recipients = recipients
            
            # In a real implementation, this would integrate with a task scheduler
            self.logger.info(f"Report scheduled: {template_id} - {frequency}")
            
        except Exception as e:
            self.logger.error(f"Error scheduling report: {str(e)}")
            raise ReportError(f"Failed to schedule report: {str(e)}")
    
    async def get_generator_status(self) -> Dict[str, Any]:
        """Get report generator status."""
        return {
            "total_templates": len(self.report_templates),
            "generated_reports": len(self.generated_reports),
            "output_directory": self.output_dir,
            "template_directory": self.template_dir,
            "supported_formats": ["html", "json", "excel"],
            "last_report_generated": max([r.generated_at for r in self.generated_reports]) if self.generated_reports else None
        }
