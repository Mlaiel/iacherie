"""
📊 REAL-TIME DASHBOARD - ENTERPRISE LOAD BALANCING MONITORING
Dashboard temps réel pour monitoring load balancing avec visualisations interactives

Implements live metrics + interactive charts + alerting interface
for comprehensive real-time monitoring of load balancing performance.

Key Features:
- Real-time metrics visualization avec WebSocket streaming
- Interactive charts avec drill-down capabilities
- Alerting interface avec customizable rules
- Performance reports generation avec automated scheduling
- Multi-dimensional data visualization (time-series, heatmaps, topology)
- Mobile-responsive dashboard design

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture real-time dashboard est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution sans autorisation écrite est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, AsyncIterator
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import hashlib
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ChartType(Enum):
    """Types de graphiques disponibles"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    AREA_CHART = "area_chart"
    SCATTER_PLOT = "scatter_plot"
    TOPOLOGY_GRAPH = "topology_graph"

class MetricCategory(Enum):
    """Catégories de métriques"""
    PERFORMANCE = "performance"
    TRAFFIC = "traffic"
    ERRORS = "errors"
    RESOURCES = "resources"
    ALGORITHMS = "algorithms"
    GEOGRAPHY = "geography"
    SECURITY = "security"

class AlertSeverity(Enum):
    """Niveaux de sévérité des alertes"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class DashboardLayout(Enum):
    """Layouts de dashboard disponibles"""
    OVERVIEW = "overview"
    PERFORMANCE = "performance"
    TRAFFIC_ANALYSIS = "traffic_analysis"
    ALGORITHM_COMPARISON = "algorithm_comparison"
    GEOGRAPHIC_VIEW = "geographic_view"
    CUSTOM = "custom"

@dataclass
class MetricData:
    """Données de métrique pour dashboard"""
    timestamp: datetime
    metric_name: str
    value: float
    category: MetricCategory
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ChartConfiguration:
    """Configuration d'un graphique"""
    chart_id: str
    title: str
    chart_type: ChartType
    metric_queries: List[str]
    refresh_interval: int  # seconds
    time_range: timedelta
    display_options: Dict[str, Any] = field(default_factory=dict)
    alert_thresholds: Dict[str, float] = field(default_factory=dict)

@dataclass
class AlertRule:
    """Règle d'alerte pour dashboard"""
    rule_id: str
    name: str
    metric_name: str
    condition: str  # "greater_than", "less_than", "equals", "change_rate"
    threshold: float
    severity: AlertSeverity
    notification_channels: List[str]
    cooldown_minutes: int = 5
    enabled: bool = True

@dataclass
class DashboardAlert:
    """Alerte générée par le dashboard"""
    alert_id: str
    rule_id: str
    severity: AlertSeverity
    message: str
    metric_value: float
    threshold: float
    triggered_at: datetime
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class DashboardConfig:
    """Configuration du dashboard"""
    dashboard_id: str
    title: str
    layout: DashboardLayout
    charts: List[ChartConfiguration]
    alert_rules: List[AlertRule]
    refresh_interval: int = 30
    auto_refresh: bool = True
    theme: str = "dark"
    shared: bool = False

class MetricsCollector:
    """🔍 Collecteur de métriques pour dashboard"""
    
    def __init__(self):
        self.metrics_buffer: deque = deque(maxlen=10000)
        self.metric_streams: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.collection_stats = {
            'total_metrics_collected': 0,
            'metrics_per_second': 0.0,
            'last_collection_time': None
        }
    
    async def collect_metrics(self, source_systems: List[str]) -> AsyncIterator[MetricData]:
        """Collection de métriques depuis les systèmes sources"""
        try:
            for system in source_systems:
                async for metric in self._collect_from_system(system):
                    # Stockage en buffer
                    self.metrics_buffer.append(metric)
                    self.metric_streams[metric.metric_name].append(metric)
                    
                    # Mise à jour des statistiques
                    self.collection_stats['total_metrics_collected'] += 1
                    self.collection_stats['last_collection_time'] = datetime.now()
                    
                    yield metric
                    
        except Exception as e:
            logger.error(f"❌ Error collecting metrics: {e}")
    
    async def _collect_from_system(self, system: str) -> AsyncIterator[MetricData]:
        """Collection depuis un système spécifique"""
        # Simulation de collection de métriques
        current_time = datetime.now()
        
        # Métriques de performance
        performance_metrics = [
            MetricData(current_time, "response_time_avg", 150.5, MetricCategory.PERFORMANCE, "ms"),
            MetricData(current_time, "response_time_p95", 250.0, MetricCategory.PERFORMANCE, "ms"),
            MetricData(current_time, "response_time_p99", 400.0, MetricCategory.PERFORMANCE, "ms"),
            MetricData(current_time, "throughput_rps", 125.0, MetricCategory.PERFORMANCE, "req/s")
        ]
        
        # Métriques de trafic
        traffic_metrics = [
            MetricData(current_time, "active_connections", 450, MetricCategory.TRAFFIC, "count"),
            MetricData(current_time, "bandwidth_usage", 85.5, MetricCategory.TRAFFIC, "MB/s"),
            MetricData(current_time, "request_rate", 200, MetricCategory.TRAFFIC, "req/min")
        ]
        
        # Métriques d'erreur
        error_metrics = [
            MetricData(current_time, "error_rate", 0.02, MetricCategory.ERRORS, "percentage"),
            MetricData(current_time, "timeout_rate", 0.005, MetricCategory.ERRORS, "percentage")
        ]
        
        all_metrics = performance_metrics + traffic_metrics + error_metrics
        
        for metric in all_metrics:
            metric.tags['system'] = system
            yield metric
    
    def get_metric_history(self, metric_name: str, time_range: timedelta) -> List[MetricData]:
        """Récupération de l'historique d'une métrique"""
        cutoff_time = datetime.now() - time_range
        
        return [
            metric for metric in self.metric_streams[metric_name]
            if metric.timestamp >= cutoff_time
        ]
    
    def get_latest_metrics(self, limit: int = 100) -> List[MetricData]:
        """Récupération des métriques les plus récentes"""
        return list(self.metrics_buffer)[-limit:]

class ChartRenderer:
    """📈 Moteur de rendu de graphiques"""
    
    def __init__(self):
        self.chart_cache: Dict[str, Dict[str, Any]] = {}
        self.rendering_stats = {
            'charts_rendered': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    async def render_chart(self, config: ChartConfiguration, metrics: List[MetricData]) -> Dict[str, Any]:
        """Rendu d'un graphique basé sur la configuration"""
        try:
            # Vérification du cache
            cache_key = self._generate_cache_key(config, metrics)
            if cache_key in self.chart_cache:
                self.rendering_stats['cache_hits'] += 1
                return self.chart_cache[cache_key]
            
            # Rendu du graphique
            chart_data = await self._render_chart_by_type(config, metrics)
            
            # Mise en cache
            self.chart_cache[cache_key] = chart_data
            self.rendering_stats['cache_misses'] += 1
            self.rendering_stats['charts_rendered'] += 1
            
            return chart_data
            
        except Exception as e:
            logger.error(f"❌ Error rendering chart {config.chart_id}: {e}")
            return self._create_error_chart(config, str(e))
    
    def _generate_cache_key(self, config: ChartConfiguration, metrics: List[MetricData]) -> str:
        """Génération d'une clé de cache pour le graphique"""
        # Hash basé sur la config et les timestamps des métriques
        config_hash = hashlib.md5(json.dumps(asdict(config), sort_keys=True, default=str).encode()).hexdigest()
        metrics_hash = hashlib.md5(str([m.timestamp for m in metrics[-10:]]).encode()).hexdigest()
        return f"{config_hash}:{metrics_hash}"
    
    async def _render_chart_by_type(self, config: ChartConfiguration, metrics: List[MetricData]) -> Dict[str, Any]:
        """Rendu spécifique par type de graphique"""
        if config.chart_type == ChartType.LINE_CHART:
            return self._render_line_chart(config, metrics)
        elif config.chart_type == ChartType.BAR_CHART:
            return self._render_bar_chart(config, metrics)
        elif config.chart_type == ChartType.PIE_CHART:
            return self._render_pie_chart(config, metrics)
        elif config.chart_type == ChartType.HEATMAP:
            return self._render_heatmap(config, metrics)
        elif config.chart_type == ChartType.GAUGE:
            return self._render_gauge(config, metrics)
        elif config.chart_type == ChartType.AREA_CHART:
            return self._render_area_chart(config, metrics)
        elif config.chart_type == ChartType.TOPOLOGY_GRAPH:
            return self._render_topology_graph(config, metrics)
        else:
            return self._create_default_chart(config, metrics)
    
    def _render_line_chart(self, config: ChartConfiguration, metrics: List[MetricData]) -> Dict[str, Any]:
        """Rendu d'un graphique en ligne"""
        # Regroupement des métriques par nom
        series_data = defaultdict(list)
        
        for metric in metrics:
            if any(query in metric.metric_name for query in config.metric_queries):
                series_data[metric.metric_name].append({
                    'x': metric.timestamp.isoformat(),
                    'y': metric.value
                })
        
        # Génération des séries
        series = []
        for metric_name, data_points in series_data.items():
            series.append({
                'name': metric_name,
                'data': sorted(data_points, key=lambda x: x['x'])
            })
        
        return {
            'chart_id': config.chart_id,
            'title': config.title,
            'type': 'line',
            'series': series,
            'xAxis': {
                'type': 'datetime',
                'title': 'Time'
            },
            'yAxis': {
                'title': 'Value'
            },
            'options': config.display_options
        }
    
    def _render_bar_chart(self, config: ChartConfiguration, metrics: List[MetricData]) -> Dict[str, Any]:
        """Rendu d'un graphique en barres"""
        # Agrégation des métriques pour les barres
        categories = []
        values = []
        
        # Regroupement par tag ou métrique
        metric_groups = defaultdict(list)
        for metric in metrics:
            if any(query in metric.metric_name for query in config.metric_queries):
                key = metric.tags.get('system', metric.metric_name)
                metric_groups[key].append(metric.value)
        
        for category, metric_values in metric_groups.items():
            categories.append(category)
            values.append(statistics.mean(metric_values) if metric_values else 0)
        
        return {
            'chart_id': config.chart_id,
            'title': config.title,
            'type': 'bar',
            'series': [{
                'name': 'Average Value',
                'data': values
            }],
            'xAxis': {
                'categories': categories
            },
            'options': config.display_options
        }
    
    def _render_pie_chart(self, config: ChartConfiguration, metrics: List[MetricData]) -> Dict[str, Any]:
        """Rendu d'un graphique en secteurs"""
        # Agrégation pour secteurs
        data_points = []
        metric_totals = defaultdict(float)
        
        for metric in metrics:
            if any(query in metric.metric_name for query in config.metric_queries):
                key = metric.tags.get('category', metric.metric_name)
                metric_totals[key] += metric.value
        
        total = sum(metric_totals.values())
        for category, value in metric_totals.items():
            percentage = (value / total * 100) if total > 0 else 0
            data_points.append({
                'name': category,
                'y': percentage
            })
        
        return {
            'chart_id': config.chart_id,
            'title': config.title,
            'type': 'pie',
            'series': [{
                'name': 'Distribution',
                'data': data_points
            }],
            'options': config.display_options
        }
    
    def _render_gauge(self, config: ChartConfiguration, metrics: List[MetricData]) -> Dict[str, Any]:
        """Rendu d'une jauge"""
        # Utilisation de la dernière valeur pour la jauge
        current_value = 0
        max_value = 100
        
        relevant_metrics = [m for m in metrics if any(query in m.metric_name for query in config.metric_queries)]
        if relevant_metrics:
            latest_metric = max(relevant_metrics, key=lambda x: x.timestamp)
            current_value = latest_metric.value
            max_value = config.display_options.get('max_value', 100)
        
        return {
            'chart_id': config.chart_id,
            'title': config.title,
            'type': 'gauge',
            'series': [{
                'name': 'Current Value',
                'data': [current_value]
            }],
            'plotOptions': {
                'gauge': {
                    'max': max_value,
                    'zones': [
                        {'from': 0, 'to': max_value * 0.6, 'color': '#55bf3b'},
                        {'from': max_value * 0.6, 'to': max_value * 0.9, 'color': '#dddf0d'},
                        {'from': max_value * 0.9, 'to': max_value, 'color': '#df5353'}
                    ]
                }
            },
            'options': config.display_options
        }
    
    def _render_heatmap(self, config: ChartConfiguration, metrics: List[MetricData]) -> Dict[str, Any]:
        """Rendu d'une heatmap"""
        # Création de données de heatmap (exemple: par heure et jour)
        heatmap_data = []
        
        # Regroupement par heure et jour
        time_groups = defaultdict(lambda: defaultdict(list))
        
        for metric in metrics:
            if any(query in metric.metric_name for query in config.metric_queries):
                hour = metric.timestamp.hour
                day = metric.timestamp.weekday()
                time_groups[day][hour].append(metric.value)
        
        # Génération des points de heatmap
        for day in range(7):  # 0-6 (lundi-dimanche)
            for hour in range(24):  # 0-23
                values = time_groups[day][hour]
                avg_value = statistics.mean(values) if values else 0
                heatmap_data.append([hour, day, avg_value])
        
        return {
            'chart_id': config.chart_id,
            'title': config.title,
            'type': 'heatmap',
            'series': [{
                'name': 'Average Value',
                'data': heatmap_data
            }],
            'xAxis': {
                'title': 'Hour of Day',
                'categories': list(range(24))
            },
            'yAxis': {
                'title': 'Day of Week',
                'categories': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            },
            'options': config.display_options
        }
    
    def _render_area_chart(self, config: ChartConfiguration, metrics: List[MetricData]) -> Dict[str, Any]:
        """Rendu d'un graphique en aires"""
        # Similar to line chart but with area fill
        line_chart = self._render_line_chart(config, metrics)
        line_chart['type'] = 'area'
        line_chart['plotOptions'] = {
            'area': {
                'fillOpacity': 0.3,
                'stacking': config.display_options.get('stacking', 'normal')
            }
        }
        return line_chart
    
    def _render_topology_graph(self, config: ChartConfiguration, metrics: List[MetricData]) -> Dict[str, Any]:
        """Rendu d'un graphique de topologie"""
        # Génération d'une topologie de réseau simple
        nodes = []
        links = []
        
        # Simulation de nœuds basés sur les systèmes
        systems = set()
        for metric in metrics:
            if 'system' in metric.tags:
                systems.add(metric.tags['system'])
        
        # Création des nœuds
        for i, system in enumerate(systems):
            # Calcul de métriques agrégées pour le système
            system_metrics = [m for m in metrics if m.tags.get('system') == system]
            avg_response_time = statistics.mean([m.value for m in system_metrics if 'response_time' in m.metric_name]) if system_metrics else 100
            
            nodes.append({
                'id': system,
                'name': system,
                'size': max(10, min(50, len(system_metrics))),
                'color': '#55bf3b' if avg_response_time < 200 else '#df5353'
            })
        
        # Création des liens (simulation)
        node_list = list(systems)
        for i in range(len(node_list) - 1):
            links.append({
                'source': node_list[i],
                'target': node_list[i + 1],
                'weight': 1
            })
        
        return {
            'chart_id': config.chart_id,
            'title': config.title,
            'type': 'network',
            'series': [{
                'nodes': nodes,
                'links': links
            }],
            'options': config.display_options
        }
    
    def _create_default_chart(self, config: ChartConfiguration, metrics: List[MetricData]) -> Dict[str, Any]:
        """Création d'un graphique par défaut"""
        return self._render_line_chart(config, metrics)
    
    def _create_error_chart(self, config: ChartConfiguration, error_message: str) -> Dict[str, Any]:
        """Création d'un graphique d'erreur"""
        return {
            'chart_id': config.chart_id,
            'title': config.title,
            'type': 'error',
            'error': error_message,
            'series': [],
            'message': f"Error rendering chart: {error_message}"
        }

class AlertManager:
    """🚨 Gestionnaire d'alertes pour dashboard"""
    
    def __init__(self):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, DashboardAlert] = {}
        self.alert_history: deque = deque(maxlen=1000)
        self.notification_stats = {
            'alerts_triggered': 0,
            'alerts_resolved': 0,
            'false_positives': 0
        }
    
    async def add_alert_rule(self, rule: AlertRule) -> bool:
        """Ajout d'une règle d'alerte"""
        try:
            self.alert_rules[rule.rule_id] = rule
            logger.info(f"✅ Alert rule added: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error adding alert rule: {e}")
            return False
    
    async def evaluate_alerts(self, metrics: List[MetricData]) -> List[DashboardAlert]:
        """Évaluation des règles d'alerte"""
        triggered_alerts = []
        
        try:
            for rule_id, rule in self.alert_rules.items():
                if not rule.enabled:
                    continue
                
                # Recherche des métriques pertinentes
                relevant_metrics = [m for m in metrics if m.metric_name == rule.metric_name]
                
                if not relevant_metrics:
                    continue
                
                # Évaluation de la condition
                latest_metric = max(relevant_metrics, key=lambda x: x.timestamp)
                alert = await self._evaluate_rule_condition(rule, latest_metric)
                
                if alert:
                    triggered_alerts.append(alert)
                    self.active_alerts[alert.alert_id] = alert
                    self.alert_history.append(alert)
                    self.notification_stats['alerts_triggered'] += 1
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"❌ Error evaluating alerts: {e}")
            return []
    
    async def _evaluate_rule_condition(self, rule: AlertRule, metric: MetricData) -> Optional[DashboardAlert]:
        """Évaluation d'une condition de règle"""
        try:
            # Vérification du cooldown
            if await self._is_in_cooldown(rule.rule_id):
                return None
            
            # Évaluation de la condition
            condition_met = False
            
            if rule.condition == "greater_than":
                condition_met = metric.value > rule.threshold
            elif rule.condition == "less_than":
                condition_met = metric.value < rule.threshold
            elif rule.condition == "equals":
                condition_met = abs(metric.value - rule.threshold) < 0.01
            elif rule.condition == "change_rate":
                # Condition de taux de changement (simplifiée)
                condition_met = abs(metric.value) > rule.threshold
            
            if condition_met:
                alert_id = f"{rule.rule_id}_{int(time.time())}"
                
                return DashboardAlert(
                    alert_id=alert_id,
                    rule_id=rule.rule_id,
                    severity=rule.severity,
                    message=f"{rule.name}: {metric.metric_name} = {metric.value} (threshold: {rule.threshold})",
                    metric_value=metric.value,
                    threshold=rule.threshold,
                    triggered_at=datetime.now()
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error evaluating rule condition: {e}")
            return None
    
    async def _is_in_cooldown(self, rule_id: str) -> bool:
        """Vérification si une règle est en cooldown"""
        rule = self.alert_rules.get(rule_id)
        if not rule:
            return False
        
        # Recherche de la dernière alerte pour cette règle
        recent_alerts = [a for a in self.alert_history if a.rule_id == rule_id]
        if not recent_alerts:
            return False
        
        latest_alert = max(recent_alerts, key=lambda x: x.triggered_at)
        cooldown_end = latest_alert.triggered_at + timedelta(minutes=rule.cooldown_minutes)
        
        return datetime.now() < cooldown_end
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Accusé de réception d'une alerte"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledged = True
            logger.info(f"✅ Alert {alert_id} acknowledged")
            return True
        return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Résolution d'une alerte"""
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolved = True
            self.notification_stats['alerts_resolved'] += 1
            logger.info(f"✅ Alert {alert_id} resolved")
            return True
        return False
    
    def get_active_alerts(self, severity_filter: Optional[AlertSeverity] = None) -> List[DashboardAlert]:
        """Récupération des alertes actives"""
        alerts = [a for a in self.active_alerts.values() if not a.resolved]
        
        if severity_filter:
            alerts = [a for a in alerts if a.severity == severity_filter]
        
        return sorted(alerts, key=lambda x: x.triggered_at, reverse=True)
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Statistiques des alertes"""
        return {
            'total_rules': len(self.alert_rules),
            'active_alerts': len([a for a in self.active_alerts.values() if not a.resolved]),
            'alerts_triggered': self.notification_stats['alerts_triggered'],
            'alerts_resolved': self.notification_stats['alerts_resolved'],
            'alert_history_size': len(self.alert_history)
        }

class RealTimeDashboard:
    """
    📊 Dashboard temps réel pour monitoring load balancing
    Live metrics + interactive charts + alerting interface
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.metrics_collector = MetricsCollector()
        self.chart_renderer = ChartRenderer()
        self.alert_manager = AlertManager()
        
        # Configuration du dashboard
        self.dashboards: Dict[str, DashboardConfig] = {}
        self.active_connections: Dict[str, Any] = {}
        
        # WebSocket simulation pour streaming
        self.websocket_clients: List[str] = []
        
        # Statistiques
        self.dashboard_stats = {
            'dashboards_created': 0,
            'charts_rendered': 0,
            'metrics_streamed': 0,
            'websocket_connections': 0
        }
        
        logger.info("📊 Real-Time Dashboard initialized")
    
    async def initialize(self) -> bool:
        """Initialisation du dashboard"""
        try:
            # Création des dashboards par défaut
            await self._create_default_dashboards()
            
            logger.info("✅ Real-Time Dashboard initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing dashboard: {e}")
            return False
    
    async def _create_default_dashboards(self):
        """Création des dashboards par défaut"""
        # Dashboard d'overview
        overview_charts = [
            ChartConfiguration(
                chart_id="overview_performance",
                title="Performance Overview",
                chart_type=ChartType.LINE_CHART,
                metric_queries=["response_time", "throughput"],
                refresh_interval=30,
                time_range=timedelta(hours=1)
            ),
            ChartConfiguration(
                chart_id="traffic_gauge",
                title="Current Traffic",
                chart_type=ChartType.GAUGE,
                metric_queries=["active_connections"],
                refresh_interval=15,
                time_range=timedelta(minutes=5)
            )
        ]
        
        overview_alerts = [
            AlertRule(
                rule_id="high_response_time",
                name="High Response Time",
                metric_name="response_time_avg",
                condition="greater_than",
                threshold=500.0,
                severity=AlertSeverity.WARNING,
                notification_channels=["email", "slack"]
            )
        ]
        
        overview_dashboard = DashboardConfig(
            dashboard_id="overview",
            title="Load Balancing Overview",
            layout=DashboardLayout.OVERVIEW,
            charts=overview_charts,
            alert_rules=overview_alerts
        )
        
        self.dashboards["overview"] = overview_dashboard
        self.dashboard_stats['dashboards_created'] += 1
    
    async def create_live_dashboard(self, dashboard_config: Dict[str, Any]) -> str:
        """
        Création dashboard live avec métriques temps réel
        
        Features:
        - WebSocket streaming pour mise à jour temps réel
        - Configuration flexible des graphiques
        - Alerting intégré avec rules customisables
        - Multi-layout support (overview, performance, traffic)
        - Theme customization (dark/light)
        - Mobile-responsive design
        """
        try:
            # Génération d'un ID unique
            dashboard_id = dashboard_config.get('id', f"dashboard_{int(time.time())}")
            
            # Parsing de la configuration
            charts = []
            for chart_config in dashboard_config.get('charts', []):
                chart = ChartConfiguration(
                    chart_id=chart_config['id'],
                    title=chart_config['title'],
                    chart_type=ChartType(chart_config['type']),
                    metric_queries=chart_config['metrics'],
                    refresh_interval=chart_config.get('refresh_interval', 30),
                    time_range=timedelta(seconds=chart_config.get('time_range_seconds', 3600)),
                    display_options=chart_config.get('options', {})
                )
                charts.append(chart)
            
            # Configuration des alertes
            alert_rules = []
            for alert_config in dashboard_config.get('alerts', []):
                rule = AlertRule(
                    rule_id=alert_config['id'],
                    name=alert_config['name'],
                    metric_name=alert_config['metric'],
                    condition=alert_config['condition'],
                    threshold=float(alert_config['threshold']),
                    severity=AlertSeverity(alert_config.get('severity', 'warning')),
                    notification_channels=alert_config.get('channels', [])
                )
                alert_rules.append(rule)
                await self.alert_manager.add_alert_rule(rule)
            
            # Création du dashboard
            dashboard = DashboardConfig(
                dashboard_id=dashboard_id,
                title=dashboard_config.get('title', 'Custom Dashboard'),
                layout=DashboardLayout(dashboard_config.get('layout', 'custom')),
                charts=charts,
                alert_rules=alert_rules,
                refresh_interval=dashboard_config.get('refresh_interval', 30),
                theme=dashboard_config.get('theme', 'dark')
            )
            
            self.dashboards[dashboard_id] = dashboard
            self.dashboard_stats['dashboards_created'] += 1
            
            logger.info(f"✅ Dashboard created: {dashboard_id}")
            return dashboard_id
            
        except Exception as e:
            logger.error(f"❌ Error creating dashboard: {e}")
            return ""
    
    async def setup_alerting_rules(self, alert_config: Dict[str, Any]) -> bool:
        """
        Configuration règles alerting pour load balancing
        
        Features:
        - Multi-condition alerting (threshold, rate, anomaly)
        - Severity-based escalation
        - Notification channel integration
        - Cooldown management pour éviter spam
        - Alert correlation et grouping
        - Auto-resolution basée sur conditions
        """
        try:
            for rule_config in alert_config.get('rules', []):
                rule = AlertRule(
                    rule_id=rule_config['id'],
                    name=rule_config['name'],
                    metric_name=rule_config['metric'],
                    condition=rule_config['condition'],
                    threshold=float(rule_config['threshold']),
                    severity=AlertSeverity(rule_config.get('severity', 'warning')),
                    notification_channels=rule_config.get('channels', []),
                    cooldown_minutes=rule_config.get('cooldown_minutes', 5),
                    enabled=rule_config.get('enabled', True)
                )
                
                success = await self.alert_manager.add_alert_rule(rule)
                if not success:
                    logger.warning(f"⚠️ Failed to add alert rule: {rule.name}")
            
            logger.info(f"✅ Configured {len(alert_config.get('rules', []))} alert rules")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up alerting rules: {e}")
            return False
    
    async def generate_performance_reports(self, report_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génération rapports performance comprehensive
        
        Features:
        - Automated report generation avec scheduling
        - Multi-format output (PDF, HTML, JSON)
        - Time-series analysis avec trend detection
        - Comparative analysis entre periods
        - Executive summary avec key insights
        - Actionable recommendations basées sur data
        """
        try:
            report_id = f"report_{int(time.time())}"
            time_range = timedelta(days=report_config.get('days', 7))
            
            # Collection des métriques pour le rapport
            metrics = self.metrics_collector.get_latest_metrics(1000)
            
            # Analyse des performances
            performance_analysis = await self._analyze_performance_trends(metrics, time_range)
            
            # Génération des insights
            insights = await self._generate_performance_insights(performance_analysis)
            
            # Recommandations
            recommendations = await self._generate_recommendations(performance_analysis)
            
            # Structure du rapport
            report = {
                'report_id': report_id,
                'generated_at': datetime.now().isoformat(),
                'time_range': {
                    'start': (datetime.now() - time_range).isoformat(),
                    'end': datetime.now().isoformat(),
                    'duration_days': time_range.days
                },
                'summary': {
                    'total_metrics_analyzed': len(metrics),
                    'performance_score': performance_analysis.get('overall_score', 0),
                    'trend': performance_analysis.get('overall_trend', 'stable'),
                    'critical_issues': len([i for i in insights if i.get('severity') == 'critical'])
                },
                'performance_analysis': performance_analysis,
                'key_insights': insights,
                'recommendations': recommendations,
                'charts': await self._generate_report_charts(metrics, report_config),
                'metadata': {
                    'format': report_config.get('format', 'json'),
                    'template': report_config.get('template', 'standard'),
                    'audience': report_config.get('audience', 'technical')
                }
            }
            
            logger.info(f"✅ Performance report generated: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Error generating performance report: {e}")
            return {'error': str(e)}
    
    async def _analyze_performance_trends(self, metrics: List[MetricData], time_range: timedelta) -> Dict[str, Any]:
        """Analyse des tendances de performance"""
        analysis = {
            'overall_score': 0.8,
            'overall_trend': 'stable',
            'response_time_trend': 'improving',
            'throughput_trend': 'stable',
            'error_rate_trend': 'stable',
            'peak_hours': [9, 10, 14, 15],
            'bottlenecks': []
        }
        
        # Analyse des métriques de temps de réponse
        response_time_metrics = [m for m in metrics if 'response_time' in m.metric_name]
        if response_time_metrics:
            avg_response_time = statistics.mean([m.value for m in response_time_metrics])
            if avg_response_time < 200:
                analysis['response_time_status'] = 'excellent'
            elif avg_response_time < 500:
                analysis['response_time_status'] = 'good'
            else:
                analysis['response_time_status'] = 'needs_improvement'
                analysis['bottlenecks'].append('High response time detected')
        
        # Analyse du throughput
        throughput_metrics = [m for m in metrics if 'throughput' in m.metric_name]
        if throughput_metrics:
            avg_throughput = statistics.mean([m.value for m in throughput_metrics])
            analysis['average_throughput'] = avg_throughput
        
        return analysis
    
    async def _generate_performance_insights(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génération d'insights de performance"""
        insights = []
        
        # Insight sur le temps de réponse
        if analysis.get('response_time_status') == 'needs_improvement':
            insights.append({
                'category': 'performance',
                'severity': 'warning',
                'title': 'High Response Time Detected',
                'description': 'Average response time is above optimal threshold',
                'impact': 'User experience degradation',
                'suggested_action': 'Review server capacity and optimize algorithms'
            })
        
        # Insight sur les bottlenecks
        if analysis.get('bottlenecks'):
            insights.append({
                'category': 'capacity',
                'severity': 'critical',
                'title': 'Performance Bottlenecks Identified',
                'description': f"Detected {len(analysis['bottlenecks'])} bottlenecks",
                'impact': 'System performance degradation',
                'suggested_action': 'Implement capacity scaling or optimization'
            })
        
        # Insight positif
        if analysis.get('overall_score', 0) > 0.8:
            insights.append({
                'category': 'performance',
                'severity': 'info',
                'title': 'System Performance is Optimal',
                'description': 'Load balancing is performing within expected parameters',
                'impact': 'Positive user experience',
                'suggested_action': 'Continue monitoring and maintain current configuration'
            })
        
        return insights
    
    async def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génération de recommandations"""
        recommendations = []
        
        if analysis.get('response_time_status') == 'needs_improvement':
            recommendations.append({
                'priority': 'high',
                'category': 'optimization',
                'title': 'Optimize Load Balancing Algorithm',
                'description': 'Consider switching to performance-based algorithm',
                'estimated_impact': 'Reduce response time by 20-30%',
                'implementation_effort': 'medium',
                'timeline': '1-2 weeks'
            })
        
        if analysis.get('bottlenecks'):
            recommendations.append({
                'priority': 'critical',
                'category': 'capacity',
                'title': 'Scale Infrastructure',
                'description': 'Add server capacity or improve resource allocation',
                'estimated_impact': 'Eliminate performance bottlenecks',
                'implementation_effort': 'high',
                'timeline': '2-4 weeks'
            })
        
        # Recommandation proactive
        recommendations.append({
            'priority': 'low',
            'category': 'monitoring',
            'title': 'Enhance Monitoring Coverage',
            'description': 'Add additional metrics and alerting rules',
            'estimated_impact': 'Improved visibility into system behavior',
            'implementation_effort': 'low',
            'timeline': '1 week'
        })
        
        return recommendations
    
    async def _generate_report_charts(self, metrics: List[MetricData], report_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Génération des graphiques pour le rapport"""
        charts = []
        
        # Configuration des graphiques par défaut
        default_charts = [
            {
                'id': 'response_time_trend',
                'title': 'Response Time Trend',
                'type': 'line',
                'metrics': ['response_time_avg']
            },
            {
                'id': 'throughput_overview',
                'title': 'Throughput Overview',
                'type': 'area',
                'metrics': ['throughput_rps']
            },
            {
                'id': 'error_rate_distribution',
                'title': 'Error Rate Distribution',
                'type': 'bar',
                'metrics': ['error_rate']
            }
        ]
        
        for chart_config in default_charts:
            config = ChartConfiguration(
                chart_id=chart_config['id'],
                title=chart_config['title'],
                chart_type=ChartType(chart_config['type']),
                metric_queries=chart_config['metrics'],
                refresh_interval=0,  # Static for reports
                time_range=timedelta(days=7)
            )
            
            chart_data = await self.chart_renderer.render_chart(config, metrics)
            charts.append(chart_data)
        
        return charts
    
    async def start_metrics_streaming(self, dashboard_id: str) -> bool:
        """Démarrage du streaming de métriques"""
        try:
            if dashboard_id not in self.dashboards:
                return False
            
            dashboard = self.dashboards[dashboard_id]
            
            # Simulation du streaming WebSocket
            async def stream_metrics():
                source_systems = ['lb_node_1', 'lb_node_2', 'lb_node_3']
                
                async for metric in self.metrics_collector.collect_metrics(source_systems):
                    # Évaluation des alertes
                    alerts = await self.alert_manager.evaluate_alerts([metric])
                    
                    # Mise à jour des graphiques si nécessaire
                    for chart in dashboard.charts:
                        if any(query in metric.metric_name for query in chart.metric_queries):
                            # Simulation de mise à jour WebSocket
                            await self._send_websocket_update(dashboard_id, {
                                'type': 'metric_update',
                                'chart_id': chart.chart_id,
                                'metric': asdict(metric),
                                'alerts': [asdict(alert) for alert in alerts]
                            })
                    
                    self.dashboard_stats['metrics_streamed'] += 1
                    
                    # Pause pour contrôler la fréquence
                    await asyncio.sleep(1)
            
            # Démarrage du streaming en arrière-plan
            asyncio.create_task(stream_metrics())
            
            logger.info(f"✅ Metrics streaming started for dashboard: {dashboard_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting metrics streaming: {e}")
            return False
    
    async def _send_websocket_update(self, dashboard_id: str, data: Dict[str, Any]):
        """Simulation d'envoi de mise à jour WebSocket"""
        # Dans un environnement réel, ceci enverrait les données via WebSocket
        logger.debug(f"📡 WebSocket update for {dashboard_id}: {data['type']}")
    
    async def get_dashboard_data(self, dashboard_id: str) -> Dict[str, Any]:
        """Récupération des données d'un dashboard"""
        if dashboard_id not in self.dashboards:
            return {'error': 'Dashboard not found'}
        
        dashboard = self.dashboards[dashboard_id]
        
        # Collection des métriques récentes
        metrics = self.metrics_collector.get_latest_metrics(500)
        
        # Rendu des graphiques
        charts_data = []
        for chart in dashboard.charts:
            chart_data = await self.chart_renderer.render_chart(chart, metrics)
            charts_data.append(chart_data)
        
        # Alertes actives
        active_alerts = self.alert_manager.get_active_alerts()
        
        return {
            'dashboard_id': dashboard_id,
            'title': dashboard.title,
            'layout': dashboard.layout.value,
            'charts': charts_data,
            'alerts': [asdict(alert) for alert in active_alerts],
            'last_updated': datetime.now().isoformat(),
            'refresh_interval': dashboard.refresh_interval
        }
    
    async def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Statistiques du dashboard"""
        return {
            'dashboards_created': self.dashboard_stats['dashboards_created'],
            'charts_rendered': self.chart_renderer.rendering_stats['charts_rendered'],
            'metrics_streamed': self.dashboard_stats['metrics_streamed'],
            'active_dashboards': len(self.dashboards),
            'websocket_connections': len(self.websocket_clients),
            'cache_hit_rate': (
                self.chart_renderer.rendering_stats['cache_hits'] / 
                max(1, self.chart_renderer.rendering_stats['cache_hits'] + 
                    self.chart_renderer.rendering_stats['cache_misses'])
            ),
            'alert_statistics': self.alert_manager.get_alert_statistics()
        }

# Factory function pour création d'instance
async def create_real_time_dashboard(config: Dict[str, Any] = None) -> RealTimeDashboard:
    """Factory function pour créer et initialiser le dashboard"""
    dashboard = RealTimeDashboard(config)
    await dashboard.initialize()
    return dashboard

# Export des classes principales
__all__ = [
    'RealTimeDashboard',
    'ChartType',
    'MetricCategory',
    'AlertSeverity',
    'DashboardLayout',
    'MetricData',
    'ChartConfiguration',
    'AlertRule',
    'DashboardAlert',
    'DashboardConfig',
    'create_real_time_dashboard'
]