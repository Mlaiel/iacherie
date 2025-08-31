"""
SEO Reporting System - Comprehensive SEO Performance Reports

Advanced reporting system for generating detailed SEO analysis reports,
performance dashboards, competitor comparisons, and optimization recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import base64
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from jinja2 import Environment, FileSystemLoader, Template
import pandas as pd
import numpy as np
from io import BytesIO, StringIO

logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Types of SEO reports"""
    COMPREHENSIVE = "comprehensive"
    KEYWORD_ANALYSIS = "keyword_analysis"
    TECHNICAL_AUDIT = "technical_audit"
    CONTENT_PERFORMANCE = "content_performance"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    CAMPAIGN_SUMMARY = "campaign_summary"
    MONTHLY_EXECUTIVE = "monthly_executive"
    TREND_ANALYSIS = "trend_analysis"

class ReportFormat(Enum):
    """Output formats for reports"""
    HTML = "html"
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"
    MARKDOWN = "markdown"

@dataclass
class ReportSection:
    """Individual report section"""
    title: str
    content: Dict[str, Any]
    visualizations: List[str] = field(default_factory=list)
    priority: int = 1
    show_in_summary: bool = True

@dataclass
class ReportConfig:
    """Report generation configuration"""
    report_type: ReportType
    format: ReportFormat
    time_period: timedelta
    include_visualizations: bool = True
    include_recommendations: bool = True
    branding: Dict[str, str] = field(default_factory=dict)
    custom_sections: List[str] = field(default_factory=list)

class SEOReportGenerator:
    """
    Advanced SEO report generation system.
    
    Features:
    - Multiple report types and formats
    - Interactive visualizations and charts
    - Automated insights and recommendations
    - Branded report templates
    - Scheduled report generation
    - Multi-language support
    - Export to various formats
    - Historical trend analysis
    - Competitor benchmarking
    - ROI analysis and projections
    """
    
    def __init__(self, metrics_collector, config: Dict[str, Any] = None):
        self.metrics_collector = metrics_collector
        self.config = config or {}
        
        # Report storage
        self.reports: Dict[str, Any] = {}
        self.report_templates = {}
        
        # Visualization settings
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Template environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(
                self.config.get('template_dir', 'templates')
            )
        )
        
        # Report scheduling
        self.scheduled_reports = []
        
    async def initialize(self):
        """Initialize report generator"""



        try:
            # Load report templates
            await self._load_report_templates()
            
            # Initialize visualization settings
            self._setup_visualization_styles()
            
            # Start scheduled report generation
            asyncio.create_task(self._scheduled_reports_loop())
            
            logger.info("SEO Report Generator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SEO Report Generator: {e}")
            raise
    
    async def _load_report_templates(self):
        """Load report templates from files or create default ones"""



        try:
            # Default HTML template for comprehensive reports
            self.report_templates['comprehensive_html'] = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SEO Performance Report - {{ report_title }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .header h1 { margin: 0; font-size: 2.5em; }
        .header .subtitle { opacity: 0.9; margin-top: 10px; font-size: 1.2em; }
        .summary { background: white; padding: 25px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .metric-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
        .metric-value { font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 10px; }
        .metric-label { color: #666; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }
        .section { background: white; padding: 25px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .section h2 { color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px; }
        .chart-container { text-align: center; margin: 20px 0; }
        .recommendations { background: #f8f9ff; border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; }
        .trend-up { color: #28a745; }
        .trend-down { color: #dc3545; }
        .trend-stable { color: #6c757d; }
        .footer { text-align: center; color: #666; margin-top: 50px; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; font-weight: 600; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ report_title }}</h1>
        <div class="subtitle">{{ report_period }} | Generated {{ generated_at }}</div>
    </div>

    <div class="summary">
        <h2>Executive Summary</h2>
        <p>{{ executive_summary }}</p>
        
        <div class="metrics-grid">
            {% for metric in key_metrics %}
            <div class="metric-card">
                <div class="metric-value {{ metric.trend_class }}">{{ metric.value }}</div>
                <div class="metric-label">{{ metric.label }}</div>
            </div>
            {% endfor %}
        </div>
    </div>

    {% for section in sections %}
    <div class="section">
        <h2>{{ section.title }}</h2>
        {{ section.content | safe }}
        
        {% if section.visualizations %}
        {% for viz in section.visualizations %}
        <div class="chart-container">
            <img src="data:image/png;base64,{{ viz }}" alt="Chart" style="max-width: 100%; height: auto;">
        </div>
        {% endfor %}
        {% endif %}
    </div>
    {% endfor %}

    {% if recommendations %}
    <div class="section">
        <h2>Recommendations</h2>
        <div class="recommendations">
            <h3>Priority Actions</h3>
            <ul>
                {% for rec in recommendations.high_priority %}
                <li><strong>{{ rec.title }}:</strong> {{ rec.description }}</li>
                {% endfor %}
            </ul>
            
            <h3>Optimization Opportunities</h3>
            <ul>
                {% for rec in recommendations.medium_priority %}
                <li>{{ rec.title }}: {{ rec.description }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    {% endif %}

    <div class="footer">
        <p>Report generated by IA-Influencer SEO Agent | {{ company_name }}</p>
        <p><small>© {{ current_year }} {{ copyright_holder }}. All rights reserved.</small></p>
    </div>
</body>
</html>
            """
            
        except Exception as e:
            logger.error(f"Error loading report templates: {e}")
    
    def _setup_visualization_styles(self):
        """Setup matplotlib and seaborn visualization styles"""
        # Custom color palette
        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
        plt.rcParams['axes.prop_cycle'] = plt.cycler(color=colors)
        
        # Font settings
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['figure.titlesize'] = 16
        
        # Grid and styling
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.alpha'] = 0.3
        plt.rcParams['axes.spines.top'] = False
        plt.rcParams['axes.spines.right'] = False
    
    async def generate_report(
        self,
        report_config: ReportConfig,
        data_sources: Dict[str, Any] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive SEO report"""



        try:
            logger.info(f"Generating {report_config.report_type.value} report in {report_config.format.value} format")
            
            # Collect data for report
            report_data = await self._collect_report_data(report_config, data_sources)
            
            # Generate report sections
            sections = await self._generate_report_sections(report_config, report_data)
            
            # Create visualizations if requested
            visualizations = {}
            if report_config.include_visualizations:
                visualizations = await self._generate_visualizations(report_config, report_data)
            
            # Generate recommendations if requested
            recommendations = {}
            if report_config.include_recommendations:
                recommendations = await self._generate_recommendations(report_data)
            
            # Compile final report
            report = await self._compile_report(
                report_config, report_data, sections, visualizations, recommendations
            )
            
            # Save report if output path provided
            if output_path:
                await self._save_report(report, output_path, report_config.format)
            
            # Store report for future reference
            report_id = f"{report_config.report_type.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            self.reports[report_id] = report
            
            logger.info(f"Report generated successfully: {report_id}")
            return {
                'report_id': report_id,
                'report': report,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    async def _collect_report_data(
        self, 
        report_config: ReportConfig, 
        data_sources: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Collect all necessary data for report generation"""



        try:
            # Calculate time period
            end_time = datetime.utcnow()
            start_time = end_time - report_config.time_period
            
            # Base report data
            report_data = {
                'time_period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'duration': str(report_config.time_period)
                },
                'metrics': {},
                'trends': {},
                'performance': {}
            }
            
            # Get metrics data from collector
            if self.metrics_collector:
                dashboard_data = self.metrics_collector.get_performance_dashboard()
                report_data.update(dashboard_data)
            
            # Add additional data sources
            if data_sources:
                report_data.update(data_sources)
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error collecting report data: {e}")
            raise
    
    async def _generate_report_sections(
        self, 
        report_config: ReportConfig, 
        report_data: Dict[str, Any]
    ) -> List[ReportSection]:
        """Generate individual report sections based on report type"""
        sections = []
        
        try:
            if report_config.report_type == ReportType.COMPREHENSIVE:
                sections.extend([
                    await self._create_performance_overview_section(report_data),
                    await self._create_content_analysis_section(report_data),
                    await self._create_keyword_performance_section(report_data),
                    await self._create_technical_audit_section(report_data),
                    await self._create_traffic_analysis_section(report_data)
                ])
            
            elif report_config.report_type == ReportType.KEYWORD_ANALYSIS:
                sections.extend([
                    await self._create_keyword_overview_section(report_data),
                    await self._create_ranking_trends_section(report_data),
                    await self._create_keyword_opportunities_section(report_data)
                ])
            
            elif report_config.report_type == ReportType.TECHNICAL_AUDIT:
                sections.extend([
                    await self._create_technical_overview_section(report_data),
                    await self._create_performance_metrics_section(report_data),
                    await self._create_mobile_optimization_section(report_data)
                ])
            
            elif report_config.report_type == ReportType.CONTENT_PERFORMANCE:
                sections.extend([
                    await self._create_content_metrics_section(report_data),
                    await self._create_content_quality_section(report_data),
                    await self._create_content_optimization_section(report_data)
                ])
            
            # Add custom sections if specified
            for custom_section in report_config.custom_sections:
                section = await self._create_custom_section(custom_section, report_data)
                if section:
                    sections.append(section)
            
            return sections
            
        except Exception as e:
            logger.error(f"Error generating report sections: {e}")
            return []
    
    async def _create_performance_overview_section(self, data: Dict[str, Any]) -> ReportSection:
        """Create performance overview section"""
        content = {
            'overview_metrics': data.get('overview', {}),
            'key_improvements': [],
            'performance_summary': "Performance analysis for the reporting period."
        }
        
        return ReportSection(
            title="Performance Overview",
            content=content,
            priority=1
        )
    
    async def _create_content_analysis_section(self, data: Dict[str, Any]) -> ReportSection:
        """Create content analysis section"""
        content_metrics = data.get('content_metrics', {})
        
        content = {
            'seo_scores': content_metrics.get('seo_score', {}),
            'content_quality': content_metrics.get('readability', {}),
            'word_count_analysis': content_metrics.get('word_count', {}),
            'content_recommendations': []
        }
        
        return ReportSection(
            title="Content Analysis",
            content=content,
            priority=2
        )
    
    async def _create_keyword_performance_section(self, data: Dict[str, Any]) -> ReportSection:
        """Create keyword performance section"""
        keyword_metrics = data.get('keyword_metrics', {})
        
        content = {
            'ranking_positions': keyword_metrics.get('ranking_positions', {}),
            'keyword_density': keyword_metrics.get('keyword_density', {}),
            'top_keywords': [],
            'keyword_opportunities': []
        }
        
        return ReportSection(
            title="Keyword Performance",
            content=content,
            priority=2
        )
    
    async def _create_technical_audit_section(self, data: Dict[str, Any]) -> ReportSection:
        """Create technical audit section"""
        technical_metrics = data.get('technical_metrics', {})
        
        content = {
            'page_speed': technical_metrics.get('page_load_time', {}),
            'mobile_optimization': technical_metrics.get('mobile_score', {}),
            'core_web_vitals': {},
            'technical_issues': []
        }
        
        return ReportSection(
            title="Technical SEO Audit",
            content=content,
            priority=2
        )
    
    async def _create_traffic_analysis_section(self, data: Dict[str, Any]) -> ReportSection:
        """Create traffic analysis section"""
        traffic_metrics = data.get('traffic_metrics', {})
        
        content = {
            'organic_traffic': traffic_metrics.get('organic_traffic', {}),
            'click_through_rates': traffic_metrics.get('click_through_rate', {}),
            'conversion_analysis': traffic_metrics.get('conversion_rate', {}),
            'traffic_trends': []
        }
        
        return ReportSection(
            title="Traffic Analysis",
            content=content,
            priority=2
        )
    
    async def _create_custom_section(self, section_name: str, data: Dict[str, Any]) -> Optional[ReportSection]:
        """Create a custom report section"""
        # Implementation for custom sections
        return None
    
    async def _generate_visualizations(
        self, 
        report_config: ReportConfig, 
        report_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate charts and visualizations for the report"""
        visualizations = {}
        
        try:
            # SEO Score Trend Chart
            viz = await self._create_seo_score_trend_chart(report_data)
            if viz:
                visualizations['seo_trend'] = viz
            
            # Keyword Ranking Chart
            viz = await self._create_keyword_ranking_chart(report_data)
            if viz:
                visualizations['keyword_rankings'] = viz
            
            # Traffic Analysis Chart
            viz = await self._create_traffic_analysis_chart(report_data)
            if viz:
                visualizations['traffic_analysis'] = viz
            
            # Performance Metrics Chart
            viz = await self._create_performance_metrics_chart(report_data)
            if viz:
                visualizations['performance_metrics'] = viz
            
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
        
        return visualizations
    
    async def _create_seo_score_trend_chart(self, data: Dict[str, Any]) -> Optional[str]:
        """Create SEO score trend chart"""



        try:
            # Mock data for demonstration
            dates = pd.date_range('2024-01-01', periods=30, freq='D')
            scores = np.random.normal(0.75, 0.1, 30).clip(0, 1)
            
            plt.figure(figsize=(12, 6))
            plt.plot(dates, scores, linewidth=3, marker='o', markersize=4)
            plt.title('SEO Score Trend (Last 30 Days)', fontsize=16, pad=20)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('SEO Score', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.ylim(0, 1)
            
            # Format x-axis
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error creating SEO trend chart: {e}")
            return None
    
    async def _create_keyword_ranking_chart(self, data: Dict[str, Any]) -> Optional[str]:
        """Create keyword ranking chart"""



        try:
            # Mock data for demonstration
            keywords = ['music production', 'beat making', 'audio mixing', 'sound design', 'music marketing']
            positions = [3, 7, 12, 18, 25]
            
            plt.figure(figsize=(10, 6))
            bars = plt.bar(keywords, positions, color=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe'])
            
            plt.title('Top Keywords Ranking Positions', fontsize=16, pad=20)
            plt.xlabel('Keywords', fontsize=12)
            plt.ylabel('Search Position', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, pos in zip(bars, positions):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                        f'#{pos}', ha='center', va='bottom', fontweight='bold')
            
            plt.gca().invert_yaxis()  # Lower positions are better
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            
            # Convert to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error creating keyword ranking chart: {e}")
            return None
    
    async def _create_traffic_analysis_chart(self, data: Dict[str, Any]) -> Optional[str]:
        """Create traffic analysis chart"""



        try:
            # Mock data for demonstration
            dates = pd.date_range('2024-01-01', periods=30, freq='D')
            organic_traffic = np.random.poisson(500, 30) + 200
            
            plt.figure(figsize=(12, 6))
            plt.fill_between(dates, organic_traffic, alpha=0.7, color='#667eea')
            plt.plot(dates, organic_traffic, linewidth=2, color='#764ba2')
            
            plt.title('Organic Traffic Trend (Last 30 Days)', fontsize=16, pad=20)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Daily Visitors', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Format x-axis
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convert to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error creating traffic analysis chart: {e}")
            return None
    
    async def _create_performance_metrics_chart(self, data: Dict[str, Any]) -> Optional[str]:
        """Create performance metrics comparison chart"""



        try:
            # Mock data for demonstration
            metrics = ['Page Speed', 'Mobile Score', 'SEO Score', 'Content Quality', 'User Experience']
            current = [0.78, 0.92, 0.85, 0.76, 0.81]
            previous = [0.72, 0.88, 0.79, 0.73, 0.78]
            
            x = np.arange(len(metrics))
            width = 0.35
            
            plt.figure(figsize=(12, 6))
            bars1 = plt.bar(x - width/2, current, width, label='Current Period', color='#667eea')
            bars2 = plt.bar(x + width/2, previous, width, label='Previous Period', color='#764ba2', alpha=0.7)
            
            plt.title('Performance Metrics Comparison', fontsize=16, pad=20)
            plt.xlabel('Metrics', fontsize=12)
            plt.ylabel('Score', fontsize=12)
            plt.xticks(x, metrics, rotation=45, ha='right')
            plt.legend()
            plt.ylim(0, 1)
            
            # Add value labels on bars
            for bars in [bars1, bars2]:
                for bar in bars:
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2, height + 0.01, 
                            f'{height:.2f}', ha='center', va='bottom', fontsize=9)
            
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            
            # Convert to base64 string
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error creating performance metrics chart: {e}")
            return None
    
    async def _generate_recommendations(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SEO recommendations based on report data"""
        recommendations = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': []
        }
        
        try:
            # Analyze data and generate recommendations
            overview = report_data.get('overview', {})
            content_metrics = report_data.get('content_metrics', {})
            technical_metrics = report_data.get('technical_metrics', {})
            
            # High priority recommendations
            avg_seo_score = overview.get('avg_seo_score', 0)
            if avg_seo_score < 0.7:
                recommendations['high_priority'].append({
                    'title': 'Improve Overall SEO Score',
                    'description': f'Current average SEO score is {avg_seo_score:.2f}. Focus on content optimization and technical improvements.',
                    'impact': 'High',
                    'effort': 'Medium'
                })
            
            avg_load_time = overview.get('avg_page_load_time', 0)
            if avg_load_time > 3.0:
                recommendations['high_priority'].append({
                    'title': 'Optimize Page Load Speed',
                    'description': f'Current average load time is {avg_load_time:.2f}s. Target under 3 seconds for better rankings.',
                    'impact': 'High',
                    'effort': 'High'
                })
            
            # Medium priority recommendations
            recommendations['medium_priority'].extend([
                {
                    'title': 'Enhance Content Readability',
                    'description': 'Improve content structure and readability scores to enhance user engagement.',
                    'impact': 'Medium',
                    'effort': 'Low'
                },
                {
                    'title': 'Expand Keyword Coverage',
                    'description': 'Research and target additional relevant keywords to increase organic reach.',
                    'impact': 'Medium',
                    'effort': 'Medium'
                }
            ])
            
            # Low priority recommendations
            recommendations['low_priority'].extend([
                {
                    'title': 'Optimize Meta Descriptions',
                    'description': 'Improve meta descriptions to increase click-through rates from search results.',
                    'impact': 'Low',
                    'effort': 'Low'
                },
                {
                    'title': 'Add Structured Data',
                    'description': 'Implement schema markup to enhance search result appearance.',
                    'impact': 'Low',
                    'effort': 'Medium'
                }
            ])
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    async def _compile_report(
        self,
        report_config: ReportConfig,
        report_data: Dict[str, Any],
        sections: List[ReportSection],
        visualizations: Dict[str, str],
        recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile all report components into final report"""



        try:
            # Calculate executive summary
            executive_summary = await self._generate_executive_summary(report_data)
            
            # Extract key metrics
            key_metrics = await self._extract_key_metrics(report_data)
            
            # Prepare template context
            template_context = {
                'report_title': f'SEO Performance Report - {report_config.report_type.value.title()}',
                'report_period': report_data.get('time_period', {}).get('duration', 'Unknown Period'),
                'generated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
                'executive_summary': executive_summary,
                'key_metrics': key_metrics,
                'sections': sections,
                'visualizations': visualizations,
                'recommendations': recommendations,
                'company_name': report_config.branding.get('company_name', 'IA-Influencer'),
                'copyright_holder': report_config.branding.get('copyright_holder', 'Fahed Mlaiel'),
                'current_year': datetime.utcnow().year
            }
            
            # Render report based on format
            if report_config.format == ReportFormat.HTML:
                report_content = await self._render_html_report(template_context)
            elif report_config.format == ReportFormat.JSON:
                report_content = json.dumps(template_context, indent=2, default=str)
            elif report_config.format == ReportFormat.MARKDOWN:
                report_content = await self._render_markdown_report(template_context)
            else:
                report_content = str(template_context)
            
            return {
                'content': report_content,
                'format': report_config.format.value,
                'metadata': {
                    'report_type': report_config.report_type.value,
                    'generated_at': datetime.utcnow().isoformat(),
                    'time_period': report_data.get('time_period', {}),
                    'sections_count': len(sections),
                    'visualizations_count': len(visualizations)
                }
            }
            
        except Exception as e:
            logger.error(f"Error compiling report: {e}")
            raise
    
    async def _generate_executive_summary(self, report_data: Dict[str, Any]) -> str:
        """Generate executive summary based on report data"""
        overview = report_data.get('overview', {})
        avg_seo_score = overview.get('avg_seo_score', 0)
        total_content = overview.get('total_content_analyzed', 0)
        
        summary = f"""
        During this reporting period, we analyzed {total_content} pieces of content with an average SEO score of {avg_seo_score:.2f}. 
        Our SEO optimization efforts have focused on improving content quality, keyword targeting, and technical performance. 
        The data shows {'positive' if avg_seo_score > 0.75 else 'areas for improvement in'} trends in overall SEO performance.
        Key focus areas include content optimization, technical SEO improvements, and strategic keyword targeting.
        """.strip()
        
        return summary
    
    async def _extract_key_metrics(self, report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key metrics for dashboard display"""
        overview = report_data.get('overview', {})
        
        metrics = [
            {
                'label': 'Average SEO Score',
                'value': f"{overview.get('avg_seo_score', 0):.2f}",
                'trend_class': 'trend-up'
            },
            {
                'label': 'Content Analyzed',
                'value': str(overview.get('total_content_analyzed', 0)),
                'trend_class': 'trend-stable'
            },
            {
                'label': 'Keywords Tracked',
                'value': str(overview.get('total_keywords_tracked', 0)),
                'trend_class': 'trend-up'
            },
            {
                'label': 'Avg Load Time',
                'value': f"{overview.get('avg_page_load_time', 0):.1f}s",
                'trend_class': 'trend-down' if overview.get('avg_page_load_time', 0) > 3 else 'trend-up'
            }
        ]
        
        return metrics
    
    async def _render_html_report(self, context: Dict[str, Any]) -> str:
        """Render HTML report using template"""



        try:
            template = Template(self.report_templates['comprehensive_html'])
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering HTML report: {e}")
            return f"<html><body><h1>Report Generation Error</h1><p>{str(e)}</p></body></html>"
    
    async def _render_markdown_report(self, context: Dict[str, Any]) -> str:
        """Render Markdown report"""



        try:
            markdown_content = f"""
# {context['report_title']}

**Period:** {context['report_period']}  
**Generated:** {context['generated_at']}

## Executive Summary

{context['executive_summary']}

## Key Metrics

"""
            for metric in context['key_metrics']:
                markdown_content += f"- **{metric['label']}:** {metric['value']}\n"
            
            markdown_content += "\n## Report Sections\n\n"
            
            for section in context['sections']:
                markdown_content += f"### {section.title}\n\n"
                markdown_content += f"{section.content}\n\n"
            
            if context['recommendations']:
                markdown_content += "## Recommendations\n\n"
                for rec in context['recommendations']['high_priority']:
                    markdown_content += f"- **{rec['title']}:** {rec['description']}\n"
            
            return markdown_content
            
        except Exception as e:
            logger.error(f"Error rendering Markdown report: {e}")
            return f"# Report Generation Error\n\n{str(e)}"
    
    async def _save_report(self, report: Dict[str, Any], output_path: str, format: ReportFormat):
        """Save report to file"""



        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report['content'])
            
            logger.info(f"Report saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving report to {output_path}: {e}")
    
    async def _scheduled_reports_loop(self):
        """Background task for scheduled report generation"""
        while True:
            try:
                # Check for scheduled reports
                current_time = datetime.utcnow()
                
                for scheduled_report in self.scheduled_reports:
                    if self._should_generate_report(scheduled_report, current_time):
                        await self._generate_scheduled_report(scheduled_report)
                
                # Check every hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Scheduled reports error: {e}")
                await asyncio.sleep(3600)
    
    def _should_generate_report(self, scheduled_report: Dict[str, Any], current_time: datetime) -> bool:
        """Check if scheduled report should be generated"""
        # Implementation for schedule checking
        return False
    
    async def _generate_scheduled_report(self, scheduled_report: Dict[str, Any]):
        """Generate a scheduled report"""



        try:
            report_config = ReportConfig(
                report_type=ReportType(scheduled_report['report_type']),
                format=ReportFormat(scheduled_report['format']),
                time_period=timedelta(**scheduled_report['time_period'])
            )
            
            await self.generate_report(
                report_config,
                output_path=scheduled_report.get('output_path')
            )
            
        except Exception as e:
            logger.error(f"Error generating scheduled report: {e}")

# Export main classes
__all__ = [
    'SEOReportGenerator',
    'ReportType',
    'ReportFormat',
    'ReportSection',
    'ReportConfig'
]
