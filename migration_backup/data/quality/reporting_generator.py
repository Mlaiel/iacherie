"""
📊 REPORTING GENERATOR - DASHBOARDS & AUTOMATED REPORTS
Data Quality Module - Phase 2 Implementation

🚨 PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel - TOUS DROITS RÉSERVÉS
Toute utilisation non autorisée sera poursuivie en justice.

Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from pathlib import Path
import base64
from io import BytesIO

# Visualisation et rapports
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio

# Export formats
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

# Templates
from jinja2 import Template
import weasyprint


class ReportType(str, Enum):
    """Types de rapports"""
    QUALITY_SUMMARY = "quality_summary"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    BUSINESS_INTELLIGENCE = "business_intelligence"
    SECURITY_AUDIT = "security_audit"
    COMPLIANCE_REPORT = "compliance_report"
    EXECUTIVE_SUMMARY = "executive_summary"
    TECHNICAL_DEEP_DIVE = "technical_deep_dive"


class ReportFormat(str, Enum):
    """Formats de rapport"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    EXCEL = "xlsx"
    DASHBOARD = "dashboard"


class ReportFrequency(str, Enum):
    """Fréquences de génération"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass
class ReportConfig:
    """Configuration de rapport"""
    report_type: ReportType
    format: ReportFormat
    frequency: ReportFrequency
    recipients: List[str] = field(default_factory=list)
    include_charts: bool = True
    include_raw_data: bool = False
    custom_filters: Dict[str, Any] = field(default_factory=dict)
    template_path: Optional[str] = None


@dataclass
class ReportSection:
    """Section de rapport"""
    title: str
    content: Union[str, Dict[str, Any]]
    charts: List[Dict[str, Any]] = field(default_factory=list)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    order: int = 0


@dataclass
class GeneratedReport:
    """Rapport généré"""
    report_id: str
    report_type: ReportType
    format: ReportFormat
    title: str
    generated_at: datetime
    data_period: Dict[str, datetime]
    sections: List[ReportSection]
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class QualityReportGenerator:
    """Générateur de rapports qualité"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_quality_summary(self, quality_data: List[Dict[str, Any]], 
                                period_days: int = 7) -> ReportSection:
        """Génération résumé qualité"""
        try:
            df = pd.DataFrame(quality_data)
            
            if df.empty:
                return ReportSection(
                    title="Résumé Qualité",
                    content="Aucune donnée de qualité disponible",
                    order=1
                )
            
            # Calculs statistiques
            avg_quality = df['quality_score'].mean() if 'quality_score' in df.columns else 0
            min_quality = df['quality_score'].min() if 'quality_score' in df.columns else 0
            max_quality = df['quality_score'].max() if 'quality_score' in df.columns else 0
            std_quality = df['quality_score'].std() if 'quality_score' in df.columns else 0
            
            # Insights
            insights = []
            if avg_quality > 0.9:
                insights.append("🎉 Excellente qualité moyenne maintenue")
            elif avg_quality > 0.8:
                insights.append("✅ Bonne qualité moyenne")
            else:
                insights.append("⚠️ Qualité moyenne nécessite amélioration")
            
            if std_quality > 0.2:
                insights.append("📊 Forte variabilité dans la qualité - standardisation recommandée")
            
            # Graphique évolution qualité
            fig_evolution = go.Figure()
            fig_evolution.add_trace(go.Scatter(
                x=df.index if 'timestamp' not in df.columns else pd.to_datetime(df['timestamp']),
                y=df['quality_score'] if 'quality_score' in df.columns else [avg_quality] * len(df),
                mode='lines+markers',
                name='Score de Qualité',
                line=dict(color='blue', width=2)
            ))
            
            fig_evolution.add_hline(y=0.8, line_dash="dash", line_color="green", 
                                  annotation_text="Seuil Acceptable")
            fig_evolution.add_hline(y=0.6, line_dash="dash", line_color="red", 
                                  annotation_text="Seuil Critique")
            
            fig_evolution.update_layout(
                title='Évolution du Score de Qualité',
                xaxis_title='Temps',
                yaxis_title='Score de Qualité',
                yaxis=dict(range=[0, 1])
            )
            
            # Distribution qualité
            fig_distribution = go.Figure()
            fig_distribution.add_trace(go.Histogram(
                x=df['quality_score'] if 'quality_score' in df.columns else [avg_quality],
                nbinsx=20,
                name='Distribution Qualité'
            ))
            
            fig_distribution.update_layout(
                title='Distribution des Scores de Qualité',
                xaxis_title='Score de Qualité',
                yaxis_title='Fréquence'
            )
            
            content = {
                "period_days": period_days,
                "total_items": len(df),
                "statistics": {
                    "average": round(avg_quality, 3),
                    "minimum": round(min_quality, 3),
                    "maximum": round(max_quality, 3),
                    "standard_deviation": round(std_quality, 3)
                },
                "quality_distribution": {
                    "excellent": len(df[df['quality_score'] > 0.9]) if 'quality_score' in df.columns else 0,
                    "good": len(df[(df['quality_score'] > 0.8) & (df['quality_score'] <= 0.9)]) if 'quality_score' in df.columns else 0,
                    "acceptable": len(df[(df['quality_score'] > 0.6) & (df['quality_score'] <= 0.8)]) if 'quality_score' in df.columns else 0,
                    "poor": len(df[df['quality_score'] <= 0.6]) if 'quality_score' in df.columns else 0
                }
            }
            
            return ReportSection(
                title="Résumé Qualité",
                content=content,
                charts=[
                    {"name": "evolution", "figure": fig_evolution.to_json()},
                    {"name": "distribution", "figure": fig_distribution.to_json()}
                ],
                insights=insights,
                order=1
            )
            
        except Exception as e:
            self.logger.error(f"Error generating quality summary: {e}")
            return ReportSection(
                title="Résumé Qualité",
                content=f"Erreur lors de la génération: {str(e)}",
                order=1
            )


class PerformanceReportGenerator:
    """Générateur de rapports performance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_performance_analysis(self, performance_data: List[Dict[str, Any]]) -> ReportSection:
        """Génération analyse performance"""
        try:
            df = pd.DataFrame(performance_data)
            
            if df.empty:
                return ReportSection(
                    title="Analyse Performance",
                    content="Aucune donnée de performance disponible",
                    order=2
                )
            
            # Métriques performance
            metrics = {}
            for metric in ['cpu_usage', 'memory_usage', 'disk_usage', 'response_time']:
                if metric in df.columns:
                    metrics[metric] = {
                        "average": round(df[metric].mean(), 2),
                        "max": round(df[metric].max(), 2),
                        "min": round(df[metric].min(), 2),
                        "current": round(df[metric].iloc[-1], 2) if len(df) > 0 else 0
                    }
            
            # Insights performance
            insights = []
            if 'cpu_usage' in metrics and metrics['cpu_usage']['average'] > 80:
                insights.append("🔥 CPU usage élevé - optimisation requise")
            if 'memory_usage' in metrics and metrics['memory_usage']['average'] > 85:
                insights.append("💾 Consommation mémoire élevée")
            if 'response_time' in metrics and metrics['response_time']['average'] > 1000:
                insights.append("⏱️ Temps de réponse dégradé")
            
            # Graphique métriques système
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('CPU Usage (%)', 'Memory Usage (%)', 'Disk Usage (%)', 'Response Time (ms)'),
                vertical_spacing=0.12
            )
            
            # Ajout des traces
            for i, metric in enumerate(['cpu_usage', 'memory_usage', 'disk_usage', 'response_time']):
                if metric in df.columns:
                    row = (i // 2) + 1
                    col = (i % 2) + 1
                    
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df[metric],
                        name=metric.replace('_', ' ').title(),
                        mode='lines+markers'
                    ), row=row, col=col)
            
            fig.update_layout(
                title='Métriques de Performance Système',
                height=600,
                showlegend=False
            )
            
            content = {
                "metrics_summary": metrics,
                "data_points": len(df),
                "analysis_period": "Dernières mesures disponibles"
            }
            
            return ReportSection(
                title="Analyse Performance",
                content=content,
                charts=[{"name": "system_metrics", "figure": fig.to_json()}],
                insights=insights,
                order=2
            )
            
        except Exception as e:
            self.logger.error(f"Error generating performance analysis: {e}")
            return ReportSection(
                title="Analyse Performance",
                content=f"Erreur lors de la génération: {str(e)}",
                order=2
            )


class BusinessReportGenerator:
    """Générateur de rapports business"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_business_intelligence(self, business_data: Dict[str, Any]) -> ReportSection:
        """Génération rapport business intelligence"""
        try:
            # KPIs principaux
            kpis = {
                "total_content": business_data.get('total_content', 0),
                "average_quality": business_data.get('average_quality', 0),
                "engagement_rate": business_data.get('engagement_rate', 0),
                "revenue_trend": business_data.get('revenue_trend', 'stable')
            }
            
            # Insights business
            insights = []
            if kpis['average_quality'] > 0.85:
                insights.append("📈 Qualité content excellente - opportunité de premium pricing")
            if kpis['engagement_rate'] > 0.75:
                insights.append("🎯 Engagement élevé - audience fidèle établie")
            if kpis['total_content'] > 1000:
                insights.append("📚 Volume de contenu significatif - diversification possible")
            
            # Graphique KPIs
            fig_kpis = go.Figure()
            
            # Jauge qualité
            fig_kpis.add_trace(go.Indicator(
                mode="gauge+number+delta",
                value=kpis['average_quality'] * 100,
                domain={'x': [0, 0.5], 'y': [0.5, 1]},
                title={'text': "Qualité Moyenne (%)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            # Jauge engagement
            fig_kpis.add_trace(go.Indicator(
                mode="gauge+number",
                value=kpis['engagement_rate'] * 100,
                domain={'x': [0.5, 1], 'y': [0.5, 1]},
                title={'text': "Engagement (%)"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 75], 'color': "yellow"},
                        {'range': [75, 100], 'color': "green"}
                    ]
                }
            ))
            
            fig_kpis.update_layout(
                title='KPIs Business Intelligence',
                height=400
            )
            
            content = {
                "kpis": kpis,
                "business_health": "excellent" if kpis['average_quality'] > 0.85 and kpis['engagement_rate'] > 0.75 else "good",
                "recommendations": [
                    "Maintenir la qualité élevée",
                    "Capitaliser sur l'engagement",
                    "Explorer nouveaux formats de contenu"
                ]
            }
            
            return ReportSection(
                title="Business Intelligence",
                content=content,
                charts=[{"name": "kpis", "figure": fig_kpis.to_json()}],
                insights=insights,
                order=3
            )
            
        except Exception as e:
            self.logger.error(f"Error generating business intelligence: {e}")
            return ReportSection(
                title="Business Intelligence",
                content=f"Erreur lors de la génération: {str(e)}",
                order=3
            )


class DashboardGenerator:
    """Générateur de dashboards interactifs"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def create_executive_dashboard(self, data_sources: Dict[str, Any]) -> str:
        """Création dashboard exécutif"""
        try:
            # Template HTML pour dashboard
            dashboard_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Ainflue - Executive Dashboard</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .dashboard-header { text-align: center; margin-bottom: 30px; }
                    .kpi-container { display: flex; justify-content: space-around; margin-bottom: 30px; }
                    .kpi-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
                    .chart-container { margin-bottom: 30px; }
                    .insights { background: #e3f2fd; padding: 15px; border-radius: 8px; }
                </style>
            </head>
            <body>
                <div class="dashboard-header">
                    <h1>🚀 Ainflue Platform - Executive Dashboard</h1>
                    <p>Généré le {{ timestamp }}</p>
                </div>
                
                <div class="kpi-container">
                    <div class="kpi-card">
                        <h3>Qualité Moyenne</h3>
                        <h2 style="color: {{ quality_color }};">{{ quality_score }}%</h2>
                    </div>
                    <div class="kpi-card">
                        <h3>Total Contenu</h3>
                        <h2>{{ total_content }}</h2>
                    </div>
                    <div class="kpi-card">
                        <h3>Performance</h3>
                        <h2 style="color: {{ performance_color }};">{{ performance_status }}</h2>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div id="quality-chart"></div>
                </div>
                
                <div class="chart-container">
                    <div id="performance-chart"></div>
                </div>
                
                <div class="insights">
                    <h3>💡 Insights Clés</h3>
                    <ul>
                        {% for insight in insights %}
                        <li>{{ insight }}</li>
                        {% endfor %}
                    </ul>
                </div>
                
                <script>
                    // Graphique qualité
                    var qualityData = {{ quality_chart_data }};
                    Plotly.newPlot('quality-chart', qualityData.data, qualityData.layout);
                    
                    // Graphique performance
                    var performanceData = {{ performance_chart_data }};
                    Plotly.newPlot('performance-chart', performanceData.data, performanceData.layout);
                    
                    // Auto-refresh toutes les 30 secondes
                    setInterval(function() {
                        location.reload();
                    }, 30000);
                </script>
            </body>
            </html>
            """
            
            # Préparation des données
            quality_score = data_sources.get('quality_score', 0.85) * 100
            total_content = data_sources.get('total_content', 0)
            performance_status = data_sources.get('performance_status', 'Excellent')
            
            # Couleurs conditionnelles
            quality_color = "green" if quality_score > 80 else "orange" if quality_score > 60 else "red"
            performance_color = "green" if performance_status == "Excellent" else "orange"
            
            # Données graphiques
            quality_chart_data = {
                "data": [{
                    "x": data_sources.get('quality_timeline', []),
                    "y": data_sources.get('quality_values', []),
                    "type": "scatter",
                    "mode": "lines+markers",
                    "name": "Qualité"
                }],
                "layout": {
                    "title": "Évolution Qualité",
                    "xaxis": {"title": "Temps"},
                    "yaxis": {"title": "Score"}
                }
            }
            
            performance_chart_data = {
                "data": [{
                    "x": ["CPU", "Mémoire", "Disque"],
                    "y": data_sources.get('system_metrics', [45, 60, 30]),
                    "type": "bar",
                    "marker": {"color": ["blue", "green", "orange"]}
                }],
                "layout": {
                    "title": "Métriques Système",
                    "yaxis": {"title": "Utilisation (%)"}
                }
            }
            
            # Rendu template
            template = Template(dashboard_template)
            html_content = template.render(
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                quality_score=round(quality_score, 1),
                quality_color=quality_color,
                total_content=total_content,
                performance_status=performance_status,
                performance_color=performance_color,
                insights=data_sources.get('insights', ["Dashboard généré avec succès"]),
                quality_chart_data=json.dumps(quality_chart_data),
                performance_chart_data=json.dumps(performance_chart_data)
            )
            
            return html_content
            
        except Exception as e:
            self.logger.error(f"Error creating executive dashboard: {e}")
            return f"<html><body><h1>Erreur Dashboard</h1><p>{str(e)}</p></body></html>"


class ReportExporter:
    """Exporteur de rapports vers différents formats"""
    
    def __init__(self, output_dir: str = "/tmp/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def export_to_pdf(self, report: GeneratedReport) -> str:
        """Export vers PDF"""
        try:
            filename = f"{report.report_id}_{report.report_type.value}.pdf"
            filepath = self.output_dir / filename
            
            # Création PDF avec ReportLab
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                textColor=colors.darkblue
            )
            story.append(Paragraph(report.title, title_style))
            story.append(Spacer(1, 12))
            
            # Métadonnées
            story.append(Paragraph(f"Généré le: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Paragraph(f"Type: {report.report_type.value}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Sections
            for section in sorted(report.sections, key=lambda x: x.order):
                # Titre section
                story.append(Paragraph(section.title, styles['Heading2']))
                
                # Contenu
                if isinstance(section.content, str):
                    story.append(Paragraph(section.content, styles['Normal']))
                elif isinstance(section.content, dict):
                    content_text = json.dumps(section.content, indent=2, ensure_ascii=False)
                    story.append(Paragraph(f"<pre>{content_text}</pre>", styles['Code']))
                
                # Insights
                if section.insights:
                    story.append(Paragraph("Insights:", styles['Heading3']))
                    for insight in section.insights:
                        story.append(Paragraph(f"• {insight}", styles['Normal']))
                
                story.append(Spacer(1, 20))
            
            # Construction PDF
            doc.build(story)
            
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error exporting to PDF: {e}")
            raise
    
    def export_to_html(self, report: GeneratedReport) -> str:
        """Export vers HTML"""
        try:
            filename = f"{report.report_id}_{report.report_type.value}.html"
            filepath = self.output_dir / filename
            
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>{{ title }}</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                    h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
                    h2 { color: #34495e; margin-top: 30px; }
                    .metadata { background: #ecf0f1; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
                    .section { margin-bottom: 30px; }
                    .insights { background: #e8f6f3; padding: 15px; border-left: 4px solid #1abc9c; }
                    .content { background: #f8f9fa; padding: 15px; border-radius: 5px; }
                    pre { background: #2c3e50; color: white; padding: 15px; border-radius: 5px; overflow-x: auto; }
                </style>
            </head>
            <body>
                <h1>{{ title }}</h1>
                
                <div class="metadata">
                    <strong>Généré le:</strong> {{ generated_at }}<br>
                    <strong>Type:</strong> {{ report_type }}<br>
                    <strong>Format:</strong> {{ format }}
                </div>
                
                {% for section in sections %}
                <div class="section">
                    <h2>{{ section.title }}</h2>
                    
                    {% if section.content %}
                    <div class="content">
                        {% if section.content is string %}
                            <p>{{ section.content }}</p>
                        {% else %}
                            <pre>{{ section.content | tojson(indent=2) }}</pre>
                        {% endif %}
                    </div>
                    {% endif %}
                    
                    {% if section.insights %}
                    <div class="insights">
                        <h3>💡 Insights</h3>
                        <ul>
                        {% for insight in section.insights %}
                            <li>{{ insight }}</li>
                        {% endfor %}
                        </ul>
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
                
                <hr>
                <p><em>Rapport généré par Ainflue Analytics Engine</em></p>
            </body>
            </html>
            """
            
            template = Template(html_template)
            html_content = template.render(
                title=report.title,
                generated_at=report.generated_at.strftime('%Y-%m-%d %H:%M:%S'),
                report_type=report.report_type.value,
                format=report.format.value,
                sections=sorted(report.sections, key=lambda x: x.order)
            )
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error exporting to HTML: {e}")
            raise
    
    def export_to_json(self, report: GeneratedReport) -> str:
        """Export vers JSON"""
        try:
            filename = f"{report.report_id}_{report.report_type.value}.json"
            filepath = self.output_dir / filename
            
            # Sérialisation du rapport
            report_dict = {
                "report_id": report.report_id,
                "report_type": report.report_type.value,
                "format": report.format.value,
                "title": report.title,
                "generated_at": report.generated_at.isoformat(),
                "data_period": {
                    k: v.isoformat() if isinstance(v, datetime) else v
                    for k, v in report.data_period.items()
                },
                "sections": [
                    {
                        "title": section.title,
                        "content": section.content,
                        "charts": section.charts,
                        "tables": section.tables,
                        "insights": section.insights,
                        "order": section.order
                    }
                    for section in report.sections
                ],
                "metadata": report.metadata
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, indent=2, ensure_ascii=False)
            
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error exporting to JSON: {e}")
            raise


class AdvancedReportingEngine:
    """Moteur de reporting avancé enterprise"""
    
    def __init__(self, output_dir: str = "/tmp/reports"):
        self.quality_generator = QualityReportGenerator()
        self.performance_generator = PerformanceReportGenerator()
        self.business_generator = BusinessReportGenerator()
        self.dashboard_generator = DashboardGenerator()
        self.exporter = ReportExporter(output_dir)
        
        # Planificateur de rapports
        self.scheduled_reports: Dict[str, ReportConfig] = {}
        
        self.logger = logging.getLogger(__name__)
    
    async def generate_report(self, report_config: ReportConfig, 
                            data_sources: Dict[str, Any]) -> GeneratedReport:
        """Génération rapport complet"""
        try:
            report_id = f"report_{int(datetime.utcnow().timestamp())}"
            sections = []
            
            # Génération sections selon type de rapport
            if report_config.report_type == ReportType.QUALITY_SUMMARY:
                if 'quality_data' in data_sources:
                    quality_section = self.quality_generator.generate_quality_summary(
                        data_sources['quality_data']
                    )
                    sections.append(quality_section)
            
            elif report_config.report_type == ReportType.PERFORMANCE_ANALYSIS:
                if 'performance_data' in data_sources:
                    perf_section = self.performance_generator.generate_performance_analysis(
                        data_sources['performance_data']
                    )
                    sections.append(perf_section)
            
            elif report_config.report_type == ReportType.BUSINESS_INTELLIGENCE:
                if 'business_data' in data_sources:
                    bi_section = self.business_generator.generate_business_intelligence(
                        data_sources['business_data']
                    )
                    sections.append(bi_section)
            
            elif report_config.report_type == ReportType.EXECUTIVE_SUMMARY:
                # Rapport exécutif combiné
                for data_key, generator_method in [
                    ('quality_data', self.quality_generator.generate_quality_summary),
                    ('performance_data', self.performance_generator.generate_performance_analysis),
                    ('business_data', self.business_generator.generate_business_intelligence)
                ]:
                    if data_key in data_sources:
                        section = generator_method(data_sources[data_key])
                        sections.append(section)
            
            # Création rapport
            report = GeneratedReport(
                report_id=report_id,
                report_type=report_config.report_type,
                format=report_config.format,
                title=f"Rapport {report_config.report_type.value.replace('_', ' ').title()}",
                generated_at=datetime.utcnow(),
                data_period={
                    "start": datetime.utcnow() - timedelta(days=7),
                    "end": datetime.utcnow()
                },
                sections=sections,
                metadata={
                    "config": report_config.__dict__,
                    "data_sources": list(data_sources.keys())
                }
            )
            
            # Export selon format
            if report_config.format == ReportFormat.PDF:
                filepath = self.exporter.export_to_pdf(report)
                report.file_path = filepath
            elif report_config.format == ReportFormat.HTML:
                filepath = self.exporter.export_to_html(report)
                report.file_path = filepath
            elif report_config.format == ReportFormat.JSON:
                filepath = self.exporter.export_to_json(report)
                report.file_path = filepath
            elif report_config.format == ReportFormat.DASHBOARD:
                dashboard_html = self.dashboard_generator.create_executive_dashboard(data_sources)
                dashboard_path = self.exporter.output_dir / f"{report_id}_dashboard.html"
                with open(dashboard_path, 'w', encoding='utf-8') as f:
                    f.write(dashboard_html)
                report.file_path = str(dashboard_path)
            
            self.logger.info(f"Report generated: {report_id} - {report_config.report_type.value}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            raise
    
    async def generate_real_time_dashboard(self, data_sources: Dict[str, Any]) -> str:
        """Génération dashboard temps réel"""
        try:
            return self.dashboard_generator.create_executive_dashboard(data_sources)
        except Exception as e:
            self.logger.error(f"Error generating real-time dashboard: {e}")
            raise
    
    def schedule_report(self, report_id: str, config: ReportConfig):
        """Planification rapport automatique"""
        self.scheduled_reports[report_id] = config
        self.logger.info(f"Report scheduled: {report_id} - {config.frequency.value}")
    
    def get_scheduled_reports(self) -> Dict[str, ReportConfig]:
        """Récupération rapports planifiés"""
        return self.scheduled_reports.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérification santé du moteur de reporting"""
        try:
            return {
                "status": "healthy",
                "output_directory": str(self.exporter.output_dir),
                "directory_exists": self.exporter.output_dir.exists(),
                "scheduled_reports": len(self.scheduled_reports),
                "supported_formats": [f.value for f in ReportFormat],
                "supported_types": [t.value for t in ReportType],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Service singleton
reporting_engine = AdvancedReportingEngine()


async def get_reporting_engine() -> AdvancedReportingEngine:
    """Factory function pour moteur de reporting"""
    return reporting_engine


# Export des classes principales
__all__ = [
    'AdvancedReportingEngine',
    'QualityReportGenerator',
    'PerformanceReportGenerator',
    'BusinessReportGenerator',
    'DashboardGenerator',
    'ReportExporter',
    'ReportType',
    'ReportFormat',
    'ReportFrequency',
    'ReportConfig',
    'ReportSection',
    'GeneratedReport',
    'reporting_engine',
    'get_reporting_engine'
]


# Exemple d'utilisation
if __name__ == "__main__":
    async def main():
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        
        # Initialisation moteur
        engine = AdvancedReportingEngine()
        
        # Configuration rapport
        config = ReportConfig(
            report_type=ReportType.EXECUTIVE_SUMMARY,
            format=ReportFormat.HTML,
            frequency=ReportFrequency.DAILY,
            recipients=["admin@ainflue.com"],
            include_charts=True
        )
        
        # Données de test
        test_data = {
            "quality_data": [
                {"quality_score": 0.85, "timestamp": datetime.utcnow() - timedelta(hours=i)}
                for i in range(24)
            ],
            "performance_data": [
                {
                    "cpu_usage": 45 + (i % 20),
                    "memory_usage": 60 + (i % 15),
                    "disk_usage": 30 + (i % 10),
                    "response_time": 100 + (i % 50),
                    "timestamp": datetime.utcnow() - timedelta(hours=i)
                }
                for i in range(24)
            ],
            "business_data": {
                "total_content": 1500,
                "average_quality": 0.87,
                "engagement_rate": 0.78,
                "revenue_trend": "increasing"
            }
        }
        
        try:
            # Génération rapport
            report = await engine.generate_report(config, test_data)
            print(f"Report generated: {report.report_id}")
            print(f"File path: {report.file_path}")
            
            # Dashboard temps réel
            dashboard_html = await engine.generate_real_time_dashboard(test_data)
            print("Real-time dashboard generated")
            
            # Vérification santé
            health = await engine.health_check()
            print(f"Engine health: {health['status']}")
            
        except Exception as e:
            print(f"Error in reporting test: {e}")
    
    # Exécution test
    asyncio.run(main())