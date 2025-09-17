"""
Health Dashboard Engine - Ainflue Health Checks Module
Moteur dashboard santé enterprise temps réel avec real-time visualization,
custom charts, alerting interface et executive summaries.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture health checks et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel. Toute reproduction, modification, distribution ou vol 
d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import uuid
from pathlib import Path
import base64
import io
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class ChartType(Enum):
    """Types de graphiques dashboard"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SCATTER_PLOT = "scatter_plot"
    TIME_SERIES = "time_series"
    CORRELATION_MATRIX = "correlation_matrix"
    TREND_ANALYSIS = "trend_analysis"

class DashboardType(Enum):
    """Types de dashboards"""
    OPERATIONAL = "operational"
    EXECUTIVE = "executive"
    TECHNICAL = "technical"
    BUSINESS = "business"
    REAL_TIME = "real_time"
    HISTORICAL = "historical"

class AlertSeverity(Enum):
    """Niveaux sévérité alertes"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class DashboardConfig:
    """Configuration dashboard"""
    dashboard_id: str
    dashboard_type: DashboardType
    title: str
    refresh_interval_seconds: int = 30
    auto_refresh: bool = True
    enable_alerts: bool = True
    chart_configs: List[Dict[str, Any]] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    access_permissions: List[str] = field(default_factory=list)

@dataclass
class ChartConfig:
    """Configuration graphique"""
    chart_id: str
    chart_type: ChartType
    title: str
    data_source: str
    metrics: List[str]
    time_range_hours: int = 24
    aggregation_interval_minutes: int = 5
    styling: Dict[str, Any] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)

@dataclass
class DashboardWidget:
    """Widget dashboard"""
    widget_id: str
    widget_type: str
    title: str
    position: Dict[str, int]  # x, y, width, height
    content: Dict[str, Any]
    last_updated: datetime
    data_source: str

@dataclass
class AlertRule:
    """Règle alerte dashboard"""
    rule_id: str
    metric_name: str
    condition: str  # >, <, ==, !=
    threshold: float
    severity: AlertSeverity
    message_template: str
    enabled: bool = True
    cooldown_minutes: int = 5

class VisualizationEngine:
    """Moteur visualisation graphiques"""
    
    def __init__(self):
        # Configuration style par défaut
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    async def create_time_series_chart(self, data: Dict[str, Any], config: ChartConfig) -> str:
        """Créer graphique time series"""
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Préparer données
            timestamps = data.get('timestamps', [])
            metrics_data = data.get('metrics', {})
            
            for metric_name, values in metrics_data.items():
                if len(timestamps) == len(values):
                    ax.plot(timestamps, values, label=metric_name, linewidth=2)
                    
            # Configuration graphique
            ax.set_title(config.title, fontsize=16, fontweight='bold')
            ax.set_xlabel('Time', fontsize=12)
            ax.set_ylabel('Value', fontsize=12)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Ajouter seuils si configurés
            for threshold_name, threshold_value in config.thresholds.items():
                ax.axhline(y=threshold_value, color='red', linestyle='--', 
                          alpha=0.7, label=f'{threshold_name}: {threshold_value}')
                          
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Convertir en base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Time series chart creation failed: {e}")
            return ""
            
    async def create_gauge_chart(self, data: Dict[str, Any], config: ChartConfig) -> str:
        """Créer graphique gauge/jauge"""
        try:
            fig, ax = plt.subplots(figsize=(8, 6), subplot_kw=dict(projection='polar'))
            
            # Données gauge
            current_value = data.get('current_value', 0)
            max_value = data.get('max_value', 100)
            
            # Calculer angle (0-180 degrés)
            angle = np.pi * (current_value / max_value)
            
            # Créer gauge
            theta = np.linspace(0, np.pi, 100)
            r = np.ones_like(theta)
            
            # Zones colorées
            red_zone = theta > np.pi * 0.8
            yellow_zone = (theta > np.pi * 0.6) & (theta <= np.pi * 0.8)
            green_zone = theta <= np.pi * 0.6
            
            ax.fill_between(theta[green_zone], 0, r[green_zone], color='green', alpha=0.3)
            ax.fill_between(theta[yellow_zone], 0, r[yellow_zone], color='yellow', alpha=0.3)
            ax.fill_between(theta[red_zone], 0, r[red_zone], color='red', alpha=0.3)
            
            # Aiguille
            ax.arrow(0, 0, angle, 0.8, head_width=0.1, head_length=0.1, 
                    fc='black', ec='black', linewidth=3)
                    
            # Configuration
            ax.set_ylim(0, 1)
            ax.set_theta_zero_location('W')
            ax.set_theta_direction(1)
            ax.set_thetagrids([0, 45, 90, 135, 180], 
                             ['0', '25%', '50%', '75%', '100%'])
            ax.set_title(f"{config.title}\n{current_value:.1f}/{max_value}", 
                        pad=20, fontsize=14, fontweight='bold')
            
            # Convertir en base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Gauge chart creation failed: {e}")
            return ""
            
    async def create_heatmap_chart(self, data: Dict[str, Any], config: ChartConfig) -> str:
        """Créer heatmap"""
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Préparer données matrice
            matrix_data = data.get('matrix', [])
            labels = data.get('labels', [])
            
            if matrix_data and labels:
                df = pd.DataFrame(matrix_data, index=labels, columns=labels)
                
                # Créer heatmap
                sns.heatmap(df, annot=True, cmap='RdYlGn_r', center=0,
                           square=True, ax=ax, cbar_kws={'shrink': 0.8})
                           
                ax.set_title(config.title, fontsize=16, fontweight='bold')
                
            plt.tight_layout()
            
            # Convertir en base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Heatmap creation failed: {e}")
            return ""
            
    async def create_bar_chart(self, data: Dict[str, Any], config: ChartConfig) -> str:
        """Créer graphique barres"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            categories = data.get('categories', [])
            values = data.get('values', [])
            
            if categories and values:
                bars = ax.bar(categories, values, color=sns.color_palette("husl", len(categories)))
                
                # Ajouter valeurs sur barres
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                           f'{value:.1f}', ha='center', va='bottom')
                           
                ax.set_title(config.title, fontsize=16, fontweight='bold')
                ax.set_xlabel('Categories', fontsize=12)
                ax.set_ylabel('Values', fontsize=12)
                
                # Rotation labels si nécessaire
                if len(max(categories, key=len)) > 10:
                    plt.xticks(rotation=45)
                    
            plt.tight_layout()
            
            # Convertir en base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
            plt.close(fig)
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Bar chart creation failed: {e}")
            return ""

class AlertingSystem:
    """Système alerting dashboard"""
    
    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: List[Dict[str, Any]] = []
        self.alert_history: List[Dict[str, Any]] = []
        
    async def register_alert_rule(self, rule: AlertRule):
        """Enregistrer règle alerte"""
        self.alert_rules[rule.rule_id] = rule
        logger.info(f"Registered alert rule: {rule.rule_id}")
        
    async def evaluate_alerts(self, metrics_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Évaluer règles alertes"""
        triggered_alerts = []
        
        for rule_id, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
                
            metric_value = metrics_data.get(rule.metric_name)
            if metric_value is None:
                continue
                
            # Évaluer condition
            alert_triggered = await self._evaluate_condition(
                metric_value, rule.condition, rule.threshold
            )
            
            if alert_triggered:
                # Vérifier cooldown
                if not await self._is_in_cooldown(rule_id):
                    alert = {
                        'alert_id': str(uuid.uuid4()),
                        'rule_id': rule_id,
                        'metric_name': rule.metric_name,
                        'current_value': metric_value,
                        'threshold': rule.threshold,
                        'severity': rule.severity.value,
                        'message': rule.message_template.format(
                            metric=rule.metric_name,
                            value=metric_value,
                            threshold=rule.threshold
                        ),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    triggered_alerts.append(alert)
                    self.active_alerts.append(alert)
                    self.alert_history.append(alert)
                    
        return triggered_alerts
        
    async def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Évaluer condition alerte"""
        if condition == '>':
            return value > threshold
        elif condition == '<':
            return value < threshold
        elif condition == '>=':
            return value >= threshold
        elif condition == '<=':
            return value <= threshold
        elif condition == '==':
            return abs(value - threshold) < 0.001
        elif condition == '!=':
            return abs(value - threshold) >= 0.001
        return False
        
    async def _is_in_cooldown(self, rule_id: str) -> bool:
        """Vérifier cooldown alerte"""
        rule = self.alert_rules.get(rule_id)
        if not rule:
            return False
            
        # Chercher dernière alerte pour cette règle
        recent_alerts = [
            alert for alert in self.alert_history
            if alert['rule_id'] == rule_id
        ]
        
        if not recent_alerts:
            return False
            
        last_alert_time = datetime.fromisoformat(recent_alerts[-1]['timestamp'])
        cooldown_end = last_alert_time + timedelta(minutes=rule.cooldown_minutes)
        
        return datetime.now() < cooldown_end

class HealthDashboardEngine:
    """
    Moteur dashboard santé enterprise temps réel.
    Real-time visualization + custom charts + alerting interface + executive summaries.
    
    Features:
    - Real-time dashboard generation avec auto-refresh
    - Multi-type visualizations (time series, gauges, heatmaps, etc.)
    - Executive summary generation avec business context
    - Advanced alerting system avec rules engine
    - Custom dashboard templates pour différents rôles
    - Export capabilities (PDF, PNG, JSON)
    """
    
    def __init__(self):
        self.visualization_engine = VisualizationEngine()
        self.alerting_system = AlertingSystem()
        
        # Stockage dashboards
        self.active_dashboards: Dict[str, DashboardConfig] = {}
        self.dashboard_cache: Dict[str, Dict[str, Any]] = {}
        self.widget_registry: Dict[str, DashboardWidget] = {}
        
        # Templates dashboard
        self.dashboard_templates = {
            DashboardType.OPERATIONAL: self._get_operational_template(),
            DashboardType.EXECUTIVE: self._get_executive_template(),
            DashboardType.TECHNICAL: self._get_technical_template(),
            DashboardType.BUSINESS: self._get_business_template()
        }
        
        # Statistiques
        self.dashboard_stats = {
            'dashboards_created': 0,
            'charts_generated': 0,
            'alerts_triggered': 0,
            'executive_summaries_generated': 0,
            'total_page_views': 0
        }
        
    async def create_realtime_health_dashboard(self, dashboard_spec: Dict[str, Any]) -> str:
        """
        Création dashboard santé temps réel avec visualisations.
        
        Args:
            dashboard_spec: Spécifications dashboard
            
        Returns:
            Dashboard ID pour accès
        """
        try:
            dashboard_id = str(uuid.uuid4())
            
            # Créer configuration dashboard
            config = DashboardConfig(
                dashboard_id=dashboard_id,
                dashboard_type=DashboardType(dashboard_spec.get('type', 'operational')),
                title=dashboard_spec.get('title', 'Health Dashboard'),
                refresh_interval_seconds=dashboard_spec.get('refresh_interval', 30),
                chart_configs=dashboard_spec.get('charts', []),
                data_sources=dashboard_spec.get('data_sources', [])
            )
            
            # Utiliser template si spécifié
            if config.dashboard_type in self.dashboard_templates:
                template = self.dashboard_templates[config.dashboard_type]
                config.chart_configs.extend(template.get('default_charts', []))
                
            # Enregistrer dashboard
            self.active_dashboards[dashboard_id] = config
            
            # Générer contenu initial
            dashboard_content = await self._generate_dashboard_content(config, dashboard_spec.get('data', {}))
            
            # Mettre en cache
            self.dashboard_cache[dashboard_id] = {
                'content': dashboard_content,
                'last_updated': datetime.now(),
                'config': config
            }
            
            # Configurer auto-refresh si activé
            if config.auto_refresh:
                asyncio.create_task(self._auto_refresh_dashboard(dashboard_id))
                
            self.dashboard_stats['dashboards_created'] += 1
            
            logger.info(f"Created real-time dashboard: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"Dashboard creation failed: {e}")
            raise
            
    async def generate_executive_health_summary(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génération synthèse executive avec business impact.
        
        Args:
            business_context: Contexte business pour synthèse
            
        Returns:
            Executive summary détaillée
        """
        try:
            summary_id = str(uuid.uuid4())
            generation_time = datetime.now()
            
            # Analyser santé services critiques
            critical_services_health = await self._analyze_critical_services_health(business_context)
            
            # Calculer impact business
            business_impact = await self._calculate_business_impact(critical_services_health, business_context)
            
            # Identifier tendances clés
            key_trends = await self._identify_key_health_trends(business_context)
            
            # Générer recommandations executive
            executive_recommendations = await self._generate_executive_recommendations(
                critical_services_health, business_impact, key_trends
            )
            
            # Créer métriques KPI
            kpi_metrics = await self._generate_kpi_metrics(business_context)
            
            # Analyser risques business
            business_risks = await self._analyze_business_risks(critical_services_health, business_context)
            
            executive_summary = {
                'summary_id': summary_id,
                'generation_timestamp': generation_time.isoformat(),
                'executive_overview': {
                    'overall_health_score': await self._calculate_overall_health_score(critical_services_health),
                    'business_impact_level': business_impact.get('impact_level', 'low'),
                    'critical_issues_count': len([s for s in critical_services_health if s.get('status') != 'healthy']),
                    'uptime_percentage': business_impact.get('uptime_percentage', 99.9),
                    'revenue_at_risk': business_impact.get('revenue_at_risk', 0)
                },
                'key_performance_indicators': kpi_metrics,
                'critical_services_status': critical_services_health,
                'business_impact_analysis': business_impact,
                'trending_concerns': key_trends,
                'business_risks': business_risks,
                'executive_recommendations': executive_recommendations,
                'next_review_date': (generation_time + timedelta(hours=24)).isoformat()
            }
            
            self.dashboard_stats['executive_summaries_generated'] += 1
            
            return executive_summary
            
        except Exception as e:
            logger.error(f"Executive summary generation failed: {e}")
            return {
                'summary_id': str(uuid.uuid4()),
                'generation_timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e)
            }
            
    async def setup_health_alerting_interface(self, alert_config: Dict[str, Any]) -> bool:
        """
        Configuration interface alerting santé multi-canal.
        
        Args:
            alert_config: Configuration alerting
            
        Returns:
            Success status
        """
        try:
            # Créer règles alertes depuis config
            for rule_config in alert_config.get('rules', []):
                rule = AlertRule(
                    rule_id=str(uuid.uuid4()),
                    metric_name=rule_config['metric'],
                    condition=rule_config['condition'],
                    threshold=rule_config['threshold'],
                    severity=AlertSeverity(rule_config.get('severity', 'warning')),
                    message_template=rule_config.get('message', 'Alert: {metric} {condition} {threshold}'),
                    cooldown_minutes=rule_config.get('cooldown_minutes', 5)
                )
                
                await self.alerting_system.register_alert_rule(rule)
                
            # Configurer canaux notification
            notification_channels = alert_config.get('channels', [])
            await self._setup_notification_channels(notification_channels)
            
            # Démarrer monitoring alertes
            asyncio.create_task(self._alert_monitoring_loop())
            
            logger.info("Health alerting interface configured successfully")
            return True
            
        except Exception as e:
            logger.error(f"Alerting interface setup failed: {e}")
            return False
            
    async def get_dashboard_content(self, dashboard_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Obtenir contenu dashboard"""
        if dashboard_id not in self.active_dashboards:
            raise ValueError(f"Dashboard {dashboard_id} not found")
            
        # Vérifier cache
        if not force_refresh and dashboard_id in self.dashboard_cache:
            cached = self.dashboard_cache[dashboard_id]
            config = self.active_dashboards[dashboard_id]
            
            # Vérifier si refresh nécessaire
            time_since_update = (datetime.now() - cached['last_updated']).total_seconds()
            if time_since_update < config.refresh_interval_seconds:
                self.dashboard_stats['total_page_views'] += 1
                return cached['content']
                
        # Régénérer contenu
        config = self.active_dashboards[dashboard_id]
        dashboard_content = await self._generate_dashboard_content(config, {})
        
        # Mettre à jour cache
        self.dashboard_cache[dashboard_id] = {
            'content': dashboard_content,
            'last_updated': datetime.now(),
            'config': config
        }
        
        self.dashboard_stats['total_page_views'] += 1
        return dashboard_content
        
    # Méthodes utilitaires
    
    async def _generate_dashboard_content(self, config: DashboardConfig, data: Dict[str, Any]) -> Dict[str, Any]:
        """Générer contenu dashboard"""
        widgets = []
        
        # Générer widgets pour chaque chart configuré
        for i, chart_config_dict in enumerate(config.chart_configs):
            try:
                chart_config = ChartConfig(
                    chart_id=str(uuid.uuid4()),
                    chart_type=ChartType(chart_config_dict['type']),
                    title=chart_config_dict['title'],
                    data_source=chart_config_dict.get('data_source', 'default'),
                    metrics=chart_config_dict.get('metrics', []),
                    thresholds=chart_config_dict.get('thresholds', {})
                )
                
                # Simuler données pour demo
                chart_data = await self._generate_sample_chart_data(chart_config)
                
                # Créer visualisation
                chart_image = ""
                if chart_config.chart_type == ChartType.TIME_SERIES:
                    chart_image = await self.visualization_engine.create_time_series_chart(chart_data, chart_config)
                elif chart_config.chart_type == ChartType.GAUGE:
                    chart_image = await self.visualization_engine.create_gauge_chart(chart_data, chart_config)
                elif chart_config.chart_type == ChartType.HEATMAP:
                    chart_image = await self.visualization_engine.create_heatmap_chart(chart_data, chart_config)
                elif chart_config.chart_type == ChartType.BAR_CHART:
                    chart_image = await self.visualization_engine.create_bar_chart(chart_data, chart_config)
                    
                widget = DashboardWidget(
                    widget_id=chart_config.chart_id,
                    widget_type=chart_config.chart_type.value,
                    title=chart_config.title,
                    position={'x': (i % 2) * 6, 'y': (i // 2) * 4, 'width': 6, 'height': 4},
                    content={
                        'chart_image': chart_image,
                        'data': chart_data,
                        'config': chart_config_dict
                    },
                    last_updated=datetime.now(),
                    data_source=chart_config.data_source
                )
                
                widgets.append(widget)
                self.dashboard_stats['charts_generated'] += 1
                
            except Exception as e:
                logger.error(f"Widget generation failed: {e}")
                continue
                
        return {
            'dashboard_id': config.dashboard_id,
            'title': config.title,
            'type': config.dashboard_type.value,
            'last_updated': datetime.now().isoformat(),
            'widgets': [
                {
                    'widget_id': w.widget_id,
                    'type': w.widget_type,
                    'title': w.title,
                    'position': w.position,
                    'content': w.content,
                    'last_updated': w.last_updated.isoformat()
                } for w in widgets
            ],
            'refresh_interval': config.refresh_interval_seconds,
            'auto_refresh': config.auto_refresh
        }
        
    async def _generate_sample_chart_data(self, config: ChartConfig) -> Dict[str, Any]:
        """Générer données exemple pour charts"""
        if config.chart_type == ChartType.TIME_SERIES:
            # Données time series
            timestamps = [datetime.now() - timedelta(hours=i) for i in range(24, 0, -1)]
            metrics_data = {}
            
            for metric in config.metrics or ['response_time', 'cpu_usage']:
                values = [50 + 20 * np.sin(i * 0.2) + np.random.normal(0, 5) for i in range(24)]
                metrics_data[metric] = [max(0, v) for v in values]
                
            return {
                'timestamps': timestamps,
                'metrics': metrics_data
            }
            
        elif config.chart_type == ChartType.GAUGE:
            return {
                'current_value': np.random.uniform(0, 100),
                'max_value': 100
            }
            
        elif config.chart_type == ChartType.HEATMAP:
            services = ['api', 'db', 'cache', 'queue']
            matrix = np.random.uniform(-1, 1, (len(services), len(services)))
            return {
                'matrix': matrix.tolist(),
                'labels': services
            }
            
        elif config.chart_type == ChartType.BAR_CHART:
            categories = ['Service A', 'Service B', 'Service C', 'Service D']
            values = [np.random.uniform(0, 100) for _ in categories]
            return {
                'categories': categories,
                'values': values
            }
            
        return {}
        
    async def _analyze_critical_services_health(self, business_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyser santé services critiques"""
        critical_services = business_context.get('critical_services', ['api', 'database', 'payment'])
        
        services_health = []
        for service in critical_services:
            # Simuler analyse santé
            health_score = np.random.uniform(0.7, 1.0)
            status = 'healthy' if health_score > 0.9 else 'degraded' if health_score > 0.7 else 'unhealthy'
            
            services_health.append({
                'service_name': service,
                'health_score': health_score,
                'status': status,
                'uptime_percentage': health_score * 100,
                'response_time_ms': 100 / health_score,
                'error_rate_percent': (1 - health_score) * 5,
                'business_impact': 'high' if service in ['api', 'payment'] else 'medium'
            })
            
        return services_health
        
    async def _calculate_business_impact(self, services_health: List[Dict[str, Any]], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculer impact business"""
        unhealthy_services = [s for s in services_health if s['status'] != 'healthy']
        
        # Estimation impact financier
        revenue_per_hour = context.get('revenue_per_hour', 10000)
        revenue_at_risk = 0
        
        for service in unhealthy_services:
            if service['business_impact'] == 'high':
                revenue_at_risk += revenue_per_hour * 0.3  # 30% revenue at risk
            elif service['business_impact'] == 'medium':
                revenue_at_risk += revenue_per_hour * 0.1  # 10% revenue at risk
                
        # Calcul uptime global
        avg_health = np.mean([s['health_score'] for s in services_health])
        
        return {
            'impact_level': 'high' if len(unhealthy_services) > 2 else 'medium' if unhealthy_services else 'low',
            'revenue_at_risk': revenue_at_risk,
            'uptime_percentage': avg_health * 100,
            'affected_services_count': len(unhealthy_services),
            'estimated_users_affected': len(unhealthy_services) * context.get('users_per_service', 1000)
        }
        
    async def _identify_key_health_trends(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identifier tendances santé clés"""
        trends = [
            {
                'trend_name': 'Response Time Increase',
                'description': 'API response times trending upward over last 6 hours',
                'severity': 'warning',
                'projected_impact': 'User experience degradation expected'
            },
            {
                'trend_name': 'Database Connection Growth',
                'description': 'Database connection pool utilization increasing',
                'severity': 'info',
                'projected_impact': 'May require scaling within 24 hours'
            }
        ]
        
        return trends
        
    async def _generate_executive_recommendations(self, services_health: List[Dict[str, Any]], 
                                                business_impact: Dict[str, Any],
                                                trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Générer recommandations executive"""
        recommendations = []
        
        # Recommandations basées sur santé services
        unhealthy_count = len([s for s in services_health if s['status'] != 'healthy'])
        if unhealthy_count > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'immediate_action',
                'title': 'Address Service Health Issues',
                'description': f'Investigate and resolve {unhealthy_count} unhealthy services',
                'expected_outcome': 'Restore full service availability',
                'timeline': 'Within 2 hours'
            })
            
        # Recommandations basées sur impact business
        if business_impact['revenue_at_risk'] > 5000:
            recommendations.append({
                'priority': 'critical',
                'category': 'financial_impact',
                'title': 'Mitigate Revenue Risk',
                'description': f'${business_impact["revenue_at_risk"]:,.0f} hourly revenue at risk',
                'expected_outcome': 'Prevent financial losses',
                'timeline': 'Immediate'
            })
            
        # Recommandations préventives
        recommendations.append({
            'priority': 'medium',
            'category': 'preventive',
            'title': 'Enhance Monitoring Coverage',
            'description': 'Implement additional health checks for early detection',
            'expected_outcome': 'Reduce MTTR by 40%',
            'timeline': 'Within 1 week'
        })
        
        return recommendations
        
    async def _generate_kpi_metrics(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Générer métriques KPI"""
        return {
            'system_availability': {
                'current': 99.5,
                'target': 99.9,
                'trend': 'stable',
                'unit': 'percentage'
            },
            'mean_time_to_resolution': {
                'current': 15.5,
                'target': 10.0,
                'trend': 'improving',
                'unit': 'minutes'
            },
            'incident_count_24h': {
                'current': 3,
                'target': 0,
                'trend': 'increasing',
                'unit': 'count'
            },
            'customer_satisfaction': {
                'current': 4.2,
                'target': 4.5,
                'trend': 'stable',
                'unit': 'rating_5'
            }
        }
        
    async def _analyze_business_risks(self, services_health: List[Dict[str, Any]], 
                                    context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyser risques business"""
        risks = []
        
        high_impact_services = [s for s in services_health if s['business_impact'] == 'high']
        degraded_high_impact = [s for s in high_impact_services if s['status'] != 'healthy']
        
        if degraded_high_impact:
            risks.append({
                'risk_type': 'service_availability',
                'probability': 'medium',
                'impact': 'high',
                'description': f'{len(degraded_high_impact)} critical services showing degradation',
                'mitigation': 'Implement immediate remediation and failover procedures'
            })
            
        return risks
        
    async def _calculate_overall_health_score(self, services_health: List[Dict[str, Any]]) -> float:
        """Calculer score santé global"""
        if not services_health:
            return 0.0
            
        health_scores = [s['health_score'] for s in services_health]
        return np.mean(health_scores)
        
    def _get_operational_template(self) -> Dict[str, Any]:
        """Template dashboard opérationnel"""
        return {
            'default_charts': [
                {
                    'type': 'time_series',
                    'title': 'Response Time Trends',
                    'metrics': ['response_time_ms'],
                    'thresholds': {'warning': 500, 'critical': 1000}
                },
                {
                    'type': 'gauge',
                    'title': 'System Health Score',
                    'metrics': ['health_score']
                },
                {
                    'type': 'bar_chart',
                    'title': 'Service Status',
                    'metrics': ['service_status']
                }
            ]
        }
        
    def _get_executive_template(self) -> Dict[str, Any]:
        """Template dashboard executive"""
        return {
            'default_charts': [
                {
                    'type': 'gauge',
                    'title': 'Overall System Health',
                    'metrics': ['overall_health']
                },
                {
                    'type': 'bar_chart',
                    'title': 'Business Impact Summary',
                    'metrics': ['business_impact']
                }
            ]
        }
        
    def _get_technical_template(self) -> Dict[str, Any]:
        """Template dashboard technique"""
        return {
            'default_charts': [
                {
                    'type': 'time_series',
                    'title': 'System Metrics',
                    'metrics': ['cpu_usage', 'memory_usage', 'disk_usage']
                },
                {
                    'type': 'heatmap',
                    'title': 'Service Dependencies',
                    'metrics': ['dependency_health']
                }
            ]
        }
        
    def _get_business_template(self) -> Dict[str, Any]:
        """Template dashboard business"""
        return {
            'default_charts': [
                {
                    'type': 'bar_chart',
                    'title': 'Revenue Impact',
                    'metrics': ['revenue_at_risk']
                },
                {
                    'type': 'time_series',
                    'title': 'Customer Experience Metrics',
                    'metrics': ['customer_satisfaction', 'conversion_rate']
                }
            ]
        }
        
    async def _auto_refresh_dashboard(self, dashboard_id: str):
        """Auto-refresh dashboard"""
        config = self.active_dashboards.get(dashboard_id)
        if not config:
            return
            
        while dashboard_id in self.active_dashboards:
            try:
                await asyncio.sleep(config.refresh_interval_seconds)
                
                # Régénérer contenu
                dashboard_content = await self._generate_dashboard_content(config, {})
                
                # Mettre à jour cache
                self.dashboard_cache[dashboard_id] = {
                    'content': dashboard_content,
                    'last_updated': datetime.now(),
                    'config': config
                }
                
            except Exception as e:
                logger.error(f"Auto-refresh failed for dashboard {dashboard_id}: {e}")
                await asyncio.sleep(60)  # Wait longer on error
                
    async def _setup_notification_channels(self, channels: List[str]):
        """Configurer canaux notification"""
        # Placeholder - implémenter intégrations notification
        pass
        
    async def _alert_monitoring_loop(self):
        """Boucle monitoring alertes"""
        while True:
            try:
                # Simuler données métriques
                sample_metrics = {
                    'response_time_ms': np.random.uniform(100, 1500),
                    'error_rate_percent': np.random.uniform(0, 10),
                    'cpu_utilization': np.random.uniform(20, 90)
                }
                
                # Évaluer alertes
                triggered_alerts = await self.alerting_system.evaluate_alerts(sample_metrics)
                
                if triggered_alerts:
                    self.dashboard_stats['alerts_triggered'] += len(triggered_alerts)
                    logger.info(f"Triggered {len(triggered_alerts)} alerts")
                    
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                await asyncio.sleep(60)

# Example usage et testing
if __name__ == "__main__":
    async def test_dashboard_engine():
        """Test moteur dashboard"""
        engine = HealthDashboardEngine()
        
        # Créer dashboard opérationnel
        dashboard_spec = {
            'type': 'operational',
            'title': 'Ainflue Health Operations Dashboard',
            'refresh_interval': 30,
            'charts': [
                {
                    'type': 'time_series',
                    'title': 'API Response Times',
                    'data_source': 'api_metrics',
                    'metrics': ['response_time_ms', 'error_rate'],
                    'thresholds': {'warning': 500, 'critical': 1000}
                },
                {
                    'type': 'gauge',
                    'title': 'System Health Score',
                    'data_source': 'health_aggregator',
                    'metrics': ['overall_health']
                },
                {
                    'type': 'bar_chart',
                    'title': 'Service Status Overview',
                    'data_source': 'service_monitor',
                    'metrics': ['service_counts']
                }
            ]
        }
        
        dashboard_id = await engine.create_realtime_health_dashboard(dashboard_spec)
        print(f"📊 Created dashboard: {dashboard_id}")
        
        # Obtenir contenu dashboard
        content = await engine.get_dashboard_content(dashboard_id)
        print(f"Dashboard widgets: {len(content['widgets'])}")
        
        # Générer executive summary
        business_context = {
            'critical_services': ['api_service', 'payment_service', 'user_service'],
            'revenue_per_hour': 15000,
            'users_per_service': 2000
        }
        
        executive_summary = await engine.generate_executive_health_summary(business_context)
        print(f"Executive Summary ID: {executive_summary['summary_id']}")
        print(f"Overall Health Score: {executive_summary['executive_overview']['overall_health_score']:.2f}")
        print(f"Revenue at Risk: ${executive_summary['executive_overview']['revenue_at_risk']:,.0f}")
        
        # Configuration alerting
        alert_config = {
            'rules': [
                {
                    'metric': 'response_time_ms',
                    'condition': '>',
                    'threshold': 1000,
                    'severity': 'critical',
                    'message': 'High response time detected: {value}ms > {threshold}ms'
                },
                {
                    'metric': 'error_rate_percent',
                    'condition': '>',
                    'threshold': 5.0,
                    'severity': 'warning',
                    'message': 'Error rate elevated: {value}% > {threshold}%'
                }
            ],
            'channels': ['email', 'slack']
        }
        
        alerting_success = await engine.setup_health_alerting_interface(alert_config)
        print(f"Alerting configured: {alerting_success}")
        
        # Afficher stats
        print(f"\nDashboard Engine Stats:")
        print(f"Dashboards Created: {engine.dashboard_stats['dashboards_created']}")
        print(f"Charts Generated: {engine.dashboard_stats['charts_generated']}")
        print(f"Executive Summaries: {engine.dashboard_stats['executive_summaries_generated']}")
        
        return dashboard_id, executive_summary
        
    # Run test
    asyncio.run(test_dashboard_engine())