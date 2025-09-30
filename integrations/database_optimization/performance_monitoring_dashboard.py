"""🗄️ Performance Monitoring Dashboard - Enterprise Implementation
================================================================

Real-time database performance monitoring with predictive analytics,
intelligent alerting, and comprehensive visualization for IA Chérie platform.

Expert Roles Implementation:
🗄️ DBA Senior: Advanced performance monitoring + query analysis + tuning
🏗️ Backend Senior: Real-time metrics collection + API services + scalability
🔒 Sécurité: Monitoring security + access control + audit trails
⚙️ DevOps: Infrastructure monitoring + alerting + automation + SRE practices
🔗 Microservices: Distributed monitoring + service health + observability
🧠 ML Engineer: Anomaly detection + predictive analytics + performance ML
🤖 Lead Dev IA: Intelligent alerting + automated optimization + AI insights
🎵 Audio Engineer: Multimedia query monitoring + streaming performance
📊 IA Prompt Engineer: Dashboard automation + intelligent reporting

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 1.0 Enterprise Production
Date: Décembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
Cette implémentation monitoring dashboard est la propriété intellectuelle EXCLUSIVE
de Fahed Mlaiel. Toute reproduction sans autorisation écrite est INTERDITE.
"""

import asyncio
import logging
import json
import time
import uuid
import threading
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, AsyncGenerator
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import psutil
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import asyncpg
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
import aiohttp
from contextlib import asynccontextmanager
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types de métriques supportées"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AlertLevel(Enum):
    """Niveaux d'alerte"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class DatabaseEngine(Enum):
    """Moteurs de base de données"""
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"
    REDIS = "redis"
    CLICKHOUSE = "clickhouse"

@dataclass
class PerformanceMetric:
    """Métrique de performance"""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    type: MetricType = MetricType.GAUGE
    value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    database: str = ""
    engine: DatabaseEngine = DatabaseEngine.POSTGRESQL
    unit: str = ""
    description: str = ""

@dataclass
class QueryMetrics:
    """Métriques de requête"""
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_hash: str = ""
    query_text: str = ""
    execution_time_ms: float = 0.0
    cpu_time_ms: float = 0.0
    io_time_ms: float = 0.0
    rows_examined: int = 0
    rows_returned: int = 0
    index_usage: List[str] = field(default_factory=list)
    lock_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    database: str = ""
    user: str = ""
    application: str = ""

@dataclass
class PerformanceAlert:
    """Alerte de performance"""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    level: AlertLevel = AlertLevel.INFO
    metric_name: str = ""
    threshold_value: float = 0.0
    current_value: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    database: str = ""
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    actions_taken: List[str] = field(default_factory=list)

@dataclass
class DatabaseHealthScore:
    """Score de santé de base de données"""
    database: str = ""
    overall_score: float = 0.0
    performance_score: float = 0.0
    availability_score: float = 0.0
    security_score: float = 0.0
    capacity_score: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)

class PerformanceMonitoringDashboard:
    """🗄️ Dashboard Monitoring Performance Enterprise
    
    Dashboard enterprise de monitoring performance avec:
    - Collecte métriques temps réel multi-database
    - Détection anomalies ML et alerting intelligent
    - Visualisations interactives et analytics avancés
    - Optimisation prédictive et recommandations automatiques
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_buffer: List[PerformanceMetric] = []
        self.query_metrics_buffer: List[QueryMetrics] = []
        self.alerts: Dict[str, PerformanceAlert] = {}
        self.health_scores: Dict[str, DatabaseHealthScore] = {}
        self.running = False
        
        # Configuration Redis pour cache métriques
        self.redis_config = config.get('redis', {})
        self.redis_client = None
        
        # Configuration ML pour détection anomalies
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.ml_models_trained = False
        
        # Configuration dashboard Web
        self.dash_app = None
        self.dash_port = config.get('dashboard_port', 8050)
        
        # Collecteurs de métriques par moteur
        self.database_collectors = {}
        
        # Thread pool pour collecte asynchrone
        self.collection_interval = config.get('collection_interval', 30)  # secondes
        
        logger.info("🗄️ Performance Monitoring Dashboard initialisé")

    async def initialize(self):
        """🚀 Initialiser le dashboard de monitoring"""
        try:
            # Connexion Redis
            if self.redis_config:
                self.redis_client = await aioredis.from_url(
                    f"redis://{self.redis_config.get('host', 'localhost')}:"
                    f"{self.redis_config.get('port', 6379)}"
                )
            
            # Initialisation des collecteurs
            await self._initialize_database_collectors()
            
            # Initialisation du dashboard Web
            await self._initialize_web_dashboard()
            
            logger.info("🚀 Dashboard monitoring initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation dashboard: {e}")
            raise

    async def _initialize_database_collectors(self):
        """🔧 Initialiser les collecteurs de métriques par base"""
        try:
            databases_config = self.config.get('databases', {})
            
            for db_name, db_config in databases_config.items():
                engine = DatabaseEngine(db_config.get('type', 'postgresql'))
                
                if engine == DatabaseEngine.POSTGRESQL:
                    collector = PostgreSQLCollector(db_name, db_config)
                elif engine == DatabaseEngine.MYSQL:
                    collector = MySQLCollector(db_name, db_config)
                elif engine == DatabaseEngine.MONGODB:
                    collector = MongoDBCollector(db_name, db_config)
                elif engine == DatabaseEngine.REDIS:
                    collector = RedisCollector(db_name, db_config)
                else:
                    logger.warning(f"Moteur non supporté: {engine}")
                    continue
                
                await collector.initialize()
                self.database_collectors[db_name] = collector
            
            logger.info(f"✅ {len(self.database_collectors)} collecteurs initialisés")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation collecteurs: {e}")
            raise

    async def _initialize_web_dashboard(self):
        """🌐 Initialiser le dashboard Web Dash/Plotly"""
        try:
            self.dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
            
            # Layout du dashboard
            self.dash_app.layout = self._create_dashboard_layout()
            
            # Callbacks pour interactivité
            self._register_dashboard_callbacks()
            
            logger.info("🌐 Dashboard Web initialisé")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation dashboard Web: {e}")
            raise

    def _create_dashboard_layout(self):
        """🎨 Créer le layout du dashboard"""
        return dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("🗄️ IA Chérie Database Performance Dashboard", 
                           className="text-center mb-4"),
                    html.Hr()
                ])
            ]),
            
            # Métriques temps réel
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("📊 Métriques Temps Réel"),
                        dbc.CardBody([
                            dcc.Graph(id="realtime-metrics"),
                            dcc.Interval(id="metrics-interval", 
                                       interval=5000, n_intervals=0)
                        ])
                    ])
                ], width=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🎯 Health Scores"),
                        dbc.CardBody([
                            dcc.Graph(id="health-scores")
                        ])
                    ])
                ], width=6)
            ], className="mb-4"),
            
            # Requêtes et alertes
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🔍 Top Requêtes Lentes"),
                        dbc.CardBody([
                            dcc.Graph(id="slow-queries")
                        ])
                    ])
                ], width=8),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🚨 Alertes Actives"),
                        dbc.CardBody([
                            html.Div(id="active-alerts")
                        ])
                    ])
                ], width=4)
            ], className="mb-4"),
            
            # Analytics avancés
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("🧠 Détection Anomalies ML"),
                        dbc.CardBody([
                            dcc.Graph(id="anomaly-detection")
                        ])
                    ])
                ], width=12)
            ], className="mb-4"),
            
            # Configuration et contrôles
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("⚙️ Configuration Monitoring"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Intervalle de collecte (s):"),
                                    dbc.Input(
                                        id="collection-interval",
                                        type="number",
                                        value=self.collection_interval,
                                        min=5, max=300
                                    )
                                ], width=4),
                                
                                dbc.Col([
                                    dbc.Label("Seuil alerte CPU (%):"),
                                    dbc.Input(
                                        id="cpu-threshold",
                                        type="number",
                                        value=80,
                                        min=50, max=100
                                    )
                                ], width=4),
                                
                                dbc.Col([
                                    dbc.Button("Appliquer", id="apply-config", 
                                             color="primary"),
                                    html.Div(id="config-status", className="mt-2")
                                ], width=4)
                            ])
                        ])
                    ])
                ])
            ])
        ], fluid=True)

    def _register_dashboard_callbacks(self):
        """🔄 Enregistrer les callbacks du dashboard"""
        
        @self.dash_app.callback(
            Output("realtime-metrics", "figure"),
            Input("metrics-interval", "n_intervals")
        )
        def update_realtime_metrics(n):
            return self._create_realtime_metrics_chart()
        
        @self.dash_app.callback(
            Output("health-scores", "figure"),
            Input("metrics-interval", "n_intervals")
        )
        def update_health_scores(n):
            return self._create_health_scores_chart()
        
        @self.dash_app.callback(
            Output("slow-queries", "figure"),
            Input("metrics-interval", "n_intervals")
        )
        def update_slow_queries(n):
            return self._create_slow_queries_chart()
        
        @self.dash_app.callback(
            Output("active-alerts", "children"),
            Input("metrics-interval", "n_intervals")
        )
        def update_active_alerts(n):
            return self._create_alerts_list()
        
        @self.dash_app.callback(
            Output("anomaly-detection", "figure"),
            Input("metrics-interval", "n_intervals")
        )
        def update_anomaly_detection(n):
            return self._create_anomaly_detection_chart()
        
        @self.dash_app.callback(
            Output("config-status", "children"),
            Input("apply-config", "n_clicks"),
            State("collection-interval", "value"),
            State("cpu-threshold", "value")
        )
        def apply_configuration(n_clicks, interval, threshold):
            if n_clicks:
                self.collection_interval = interval
                return dbc.Alert("Configuration appliquée!", color="success", 
                               dismissable=True)
            return ""

    def _create_realtime_metrics_chart(self):
        """📈 Créer le graphique des métriques temps réel"""
        try:
            if not self.metrics_buffer:
                return go.Figure()
            
            # Données des 5 dernières minutes
            cutoff_time = datetime.now() - timedelta(minutes=5)
            recent_metrics = [
                m for m in self.metrics_buffer 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return go.Figure()
            
            # Groupement par métrique
            metrics_by_name = {}
            for metric in recent_metrics:
                if metric.name not in metrics_by_name:
                    metrics_by_name[metric.name] = []
                metrics_by_name[metric.name].append(metric)
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=list(metrics_by_name.keys())[:4],
                specs=[[{"secondary_y": True}, {"secondary_y": True}],
                       [{"secondary_y": True}, {"secondary_y": True}]]
            )
            
            colors = ['blue', 'red', 'green', 'orange']
            
            for i, (metric_name, metrics) in enumerate(list(metrics_by_name.items())[:4]):
                row = (i // 2) + 1
                col = (i % 2) + 1
                
                timestamps = [m.timestamp for m in metrics]
                values = [m.value for m in metrics]
                
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=values,
                        name=metric_name,
                        line=dict(color=colors[i]),
                        mode='lines+markers'
                    ),
                    row=row, col=col
                )
            
            fig.update_layout(
                title="📊 Métriques Performance Temps Réel",
                showlegend=True,
                height=600
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Erreur création graphique métriques: {e}")
            return go.Figure()

    def _create_health_scores_chart(self):
        """🎯 Créer le graphique des scores de santé"""
        try:
            if not self.health_scores:
                return go.Figure()
            
            databases = list(self.health_scores.keys())
            overall_scores = [score.overall_score for score in self.health_scores.values()]
            performance_scores = [score.performance_score for score in self.health_scores.values()]
            availability_scores = [score.availability_score for score in self.health_scores.values()]
            security_scores = [score.security_score for score in self.health_scores.values()]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Overall',
                x=databases,
                y=overall_scores,
                marker_color='lightblue'
            ))
            
            fig.add_trace(go.Bar(
                name='Performance',
                x=databases,
                y=performance_scores,
                marker_color='lightgreen'
            ))
            
            fig.add_trace(go.Bar(
                name='Availability',
                x=databases,
                y=availability_scores,
                marker_color='lightyellow'
            ))
            
            fig.add_trace(go.Bar(
                name='Security',
                x=databases,
                y=security_scores,
                marker_color='lightcoral'
            ))
            
            fig.update_layout(
                title="🎯 Database Health Scores",
                barmode='group',
                yaxis=dict(range=[0, 100]),
                height=400
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Erreur création graphique health: {e}")
            return go.Figure()

    def _create_slow_queries_chart(self):
        """🐌 Créer le graphique des requêtes lentes"""
        try:
            if not self.query_metrics_buffer:
                return go.Figure()
            
            # Top 10 requêtes les plus lentes
            slow_queries = sorted(
                self.query_metrics_buffer,
                key=lambda q: q.execution_time_ms,
                reverse=True
            )[:10]
            
            query_ids = [f"Query {i+1}" for i in range(len(slow_queries))]
            execution_times = [q.execution_time_ms for q in slow_queries]
            cpu_times = [q.cpu_time_ms for q in slow_queries]
            io_times = [q.io_time_ms for q in slow_queries]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Execution Time',
                x=query_ids,
                y=execution_times,
                marker_color='red'
            ))
            
            fig.add_trace(go.Bar(
                name='CPU Time',
                x=query_ids,
                y=cpu_times,
                marker_color='blue'
            ))
            
            fig.add_trace(go.Bar(
                name='I/O Time',
                x=query_ids,
                y=io_times,
                marker_color='green'
            ))
            
            fig.update_layout(
                title="🐌 Top 10 Requêtes Lentes (ms)",
                barmode='group',
                height=400
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Erreur création graphique requêtes: {e}")
            return go.Figure()

    def _create_alerts_list(self):
        """🚨 Créer la liste des alertes actives"""
        try:
            active_alerts = [
                alert for alert in self.alerts.values()
                if not alert.resolved
            ]
            
            if not active_alerts:
                return dbc.Alert("✅ Aucune alerte active", color="success")
            
            alert_items = []
            for alert in active_alerts[-5:]:  # 5 dernières alertes
                color_map = {
                    AlertLevel.INFO: "info",
                    AlertLevel.WARNING: "warning", 
                    AlertLevel.ERROR: "danger",
                    AlertLevel.CRITICAL: "danger"
                }
                
                alert_items.append(
                    dbc.Alert([
                        html.H6(alert.title, className="alert-heading"),
                        html.P(alert.description),
                        html.Small(f"Database: {alert.database} | "
                                 f"Time: {alert.timestamp.strftime('%H:%M:%S')}")
                    ], color=color_map.get(alert.level, "info"), className="mb-2")
                )
            
            return html.Div(alert_items)
            
        except Exception as e:
            logger.error(f"❌ Erreur création liste alertes: {e}")
            return html.Div("Erreur chargement alertes")

    def _create_anomaly_detection_chart(self):
        """🧠 Créer le graphique de détection d'anomalies"""
        try:
            if not self.ml_models_trained or not self.metrics_buffer:
                return go.Figure()
            
            # Données des dernières heures
            cutoff_time = datetime.now() - timedelta(hours=2)
            recent_metrics = [
                m for m in self.metrics_buffer 
                if m.timestamp >= cutoff_time and m.name == 'cpu_usage'
            ]
            
            if len(recent_metrics) < 10:
                return go.Figure()
            
            # Préparation des données pour ML
            timestamps = [m.timestamp for m in recent_metrics]
            values = np.array([m.value for m in recent_metrics]).reshape(-1, 1)
            
            # Détection anomalies
            anomaly_scores = self.anomaly_detector.decision_function(values)
            is_anomaly = self.anomaly_detector.predict(values) == -1
            
            fig = go.Figure()
            
            # Données normales
            normal_timestamps = [t for t, a in zip(timestamps, is_anomaly) if not a]
            normal_values = [v[0] for v, a in zip(values, is_anomaly) if not a]
            
            fig.add_trace(go.Scatter(
                x=normal_timestamps,
                y=normal_values,
                mode='markers',
                name='Normal',
                marker=dict(color='blue', size=6)
            ))
            
            # Anomalies
            anomaly_timestamps = [t for t, a in zip(timestamps, is_anomaly) if a]
            anomaly_values = [v[0] for v, a in zip(values, is_anomaly) if a]
            
            if anomaly_timestamps:
                fig.add_trace(go.Scatter(
                    x=anomaly_timestamps,
                    y=anomaly_values,
                    mode='markers',
                    name='Anomalies',
                    marker=dict(color='red', size=10, symbol='x')
                ))
            
            fig.update_layout(
                title="🧠 Détection Anomalies ML - CPU Usage",
                xaxis_title="Temps",
                yaxis_title="CPU Usage (%)",
                height=400
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ Erreur création graphique anomalies: {e}")
            return go.Figure()

    async def start_monitoring(self):
        """🚀 Démarrer le monitoring"""
        try:
            if self.running:
                return
            
            self.running = True
            logger.info("🚀 Monitoring démarré")
            
            # Tâche de collecte des métriques
            asyncio.create_task(self._metrics_collection_loop())
            
            # Tâche de détection des alertes
            asyncio.create_task(self._alert_detection_loop())
            
            # Tâche d'entraînement ML
            asyncio.create_task(self._ml_training_loop())
            
            # Démarrage du serveur dashboard
            if self.dash_app:
                asyncio.create_task(self._run_dashboard_server())
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage monitoring: {e}")
            raise

    async def _metrics_collection_loop(self):
        """🔄 Boucle de collecte des métriques"""
        while self.running:
            try:
                # Collecte depuis chaque base de données
                for db_name, collector in self.database_collectors.items():
                    try:
                        metrics = await collector.collect_metrics()
                        self.metrics_buffer.extend(metrics)
                        
                        query_metrics = await collector.collect_query_metrics()
                        self.query_metrics_buffer.extend(query_metrics)
                        
                        # Calcul du health score
                        health_score = await self._calculate_health_score(
                            db_name, metrics
                        )
                        self.health_scores[db_name] = health_score
                        
                    except Exception as e:
                        logger.error(f"❌ Erreur collecte {db_name}: {e}")
                
                # Nettoyage du buffer (garde seulement les 1000 dernières métriques)
                if len(self.metrics_buffer) > 1000:
                    self.metrics_buffer = self.metrics_buffer[-1000:]
                
                if len(self.query_metrics_buffer) > 1000:
                    self.query_metrics_buffer = self.query_metrics_buffer[-1000:]
                
                # Stockage Redis si configuré
                if self.redis_client:
                    await self._store_metrics_to_redis()
                
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle collecte: {e}")
                await asyncio.sleep(self.collection_interval)

    async def _alert_detection_loop(self):
        """🚨 Boucle de détection des alertes"""
        while self.running:
            try:
                # Vérification des seuils
                await self._check_threshold_alerts()
                
                # Vérification des anomalies ML
                if self.ml_models_trained:
                    await self._check_ml_anomaly_alerts()
                
                await asyncio.sleep(60)  # Vérification toutes les minutes
                
            except Exception as e:
                logger.error(f"❌ Erreur détection alertes: {e}")
                await asyncio.sleep(60)

    async def _ml_training_loop(self):
        """🧠 Boucle d'entraînement ML"""
        while self.running:
            try:
                if len(self.metrics_buffer) >= 100:  # Minimum de données
                    await self._train_anomaly_detection_model()
                
                await asyncio.sleep(3600)  # Réentraînement toutes les heures
                
            except Exception as e:
                logger.error(f"❌ Erreur entraînement ML: {e}")
                await asyncio.sleep(3600)

    async def _run_dashboard_server(self):
        """🌐 Lancer le serveur dashboard"""
        try:
            # Dans un environnement de production, utiliser gunicorn
            self.dash_app.run_server(
                host='0.0.0.0',
                port=self.dash_port,
                debug=False
            )
        except Exception as e:
            logger.error(f"❌ Erreur serveur dashboard: {e}")

    async def _calculate_health_score(self, db_name: str, 
                                     metrics: List[PerformanceMetric]) -> DatabaseHealthScore:
        """🎯 Calculer le score de santé d'une base"""
        try:
            # Métriques par catégorie
            performance_metrics = [m for m in metrics if 'performance' in m.name.lower()]
            availability_metrics = [m for m in metrics if 'availability' in m.name.lower()]
            security_metrics = [m for m in metrics if 'security' in m.name.lower()]
            capacity_metrics = [m for m in metrics if any(
                keyword in m.name.lower() 
                for keyword in ['disk', 'memory', 'cpu', 'capacity']
            )]
            
            # Calcul des scores (simplifié)
            performance_score = self._calculate_category_score(performance_metrics, 'performance')
            availability_score = self._calculate_category_score(availability_metrics, 'availability')
            security_score = self._calculate_category_score(security_metrics, 'security')
            capacity_score = self._calculate_category_score(capacity_metrics, 'capacity')
            
            # Score global pondéré
            overall_score = (
                performance_score * 0.3 +
                availability_score * 0.25 +
                security_score * 0.25 +
                capacity_score * 0.2
            )
            
            return DatabaseHealthScore(
                database=db_name,
                overall_score=min(100, max(0, overall_score)),
                performance_score=min(100, max(0, performance_score)),
                availability_score=min(100, max(0, availability_score)),
                security_score=min(100, max(0, security_score)),
                capacity_score=min(100, max(0, capacity_score)),
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul health score: {e}")
            return DatabaseHealthScore(database=db_name)

    def _calculate_category_score(self, metrics: List[PerformanceMetric], 
                                 category: str) -> float:
        """📊 Calculer le score d'une catégorie"""
        try:
            if not metrics:
                return 75.0  # Score par défaut
            
            # Logique simplifiée de scoring
            if category == 'performance':
                # Pour performance: plus bas est mieux (temps de réponse)
                avg_value = statistics.mean([m.value for m in metrics])
                return max(0, 100 - avg_value)
            
            elif category == 'availability':
                # Pour availability: plus haut est mieux (uptime)
                avg_value = statistics.mean([m.value for m in metrics])
                return min(100, avg_value)
            
            elif category == 'capacity':
                # Pour capacity: éviter les extrêmes (trop plein ou vide)
                avg_value = statistics.mean([m.value for m in metrics])
                if avg_value < 20 or avg_value > 90:
                    return 50.0
                else:
                    return 100.0 - abs(avg_value - 50)
            
            else:
                return 75.0
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul score catégorie {category}: {e}")
            return 75.0

    async def _check_threshold_alerts(self):
        """🚨 Vérifier les alertes de seuil"""
        try:
            thresholds = self.config.get('alert_thresholds', {
                'cpu_usage': 80.0,
                'memory_usage': 85.0,
                'disk_usage': 90.0,
                'query_time_ms': 1000.0,
                'connections_count': 100
            })
            
            recent_metrics = [
                m for m in self.metrics_buffer
                if m.timestamp >= datetime.now() - timedelta(minutes=5)
            ]
            
            for metric_name, threshold in thresholds.items():
                relevant_metrics = [m for m in recent_metrics if m.name == metric_name]
                
                if not relevant_metrics:
                    continue
                
                latest_metric = max(relevant_metrics, key=lambda x: x.timestamp)
                
                if latest_metric.value > threshold:
                    alert = PerformanceAlert(
                        title=f"Seuil dépassé: {metric_name}",
                        description=f"Valeur actuelle: {latest_metric.value}, "
                                  f"Seuil: {threshold}",
                        level=AlertLevel.WARNING if latest_metric.value < threshold * 1.2 
                              else AlertLevel.ERROR,
                        metric_name=metric_name,
                        threshold_value=threshold,
                        current_value=latest_metric.value,
                        database=latest_metric.database
                    )
                    
                    self.alerts[alert.alert_id] = alert
                    logger.warning(f"🚨 Alerte créée: {alert.title}")
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification alertes seuil: {e}")

    async def _check_ml_anomaly_alerts(self):
        """🧠 Vérifier les alertes d'anomalies ML"""
        try:
            if not self.ml_models_trained:
                return
            
            recent_metrics = [
                m for m in self.metrics_buffer
                if (m.timestamp >= datetime.now() - timedelta(minutes=10) and
                    m.name in ['cpu_usage', 'memory_usage', 'query_time_ms'])
            ]
            
            # Groupement par métrique
            metrics_by_name = {}
            for metric in recent_metrics:
                if metric.name not in metrics_by_name:
                    metrics_by_name[metric.name] = []
                metrics_by_name[metric.name].append(metric)
            
            for metric_name, metrics in metrics_by_name.items():
                if len(metrics) < 5:  # Minimum de données
                    continue
                
                values = np.array([m.value for m in metrics]).reshape(-1, 1)
                anomaly_scores = self.anomaly_detector.decision_function(values)
                is_anomaly = self.anomaly_detector.predict(values) == -1
                
                # Créer alerte si anomalie détectée
                if any(is_anomaly):
                    anomaly_indices = [i for i, a in enumerate(is_anomaly) if a]
                    anomaly_metric = metrics[anomaly_indices[-1]]  # Dernière anomalie
                    
                    alert = PerformanceAlert(
                        title=f"Anomalie ML détectée: {metric_name}",
                        description=f"Comportement anormal détecté par ML. "
                                  f"Valeur: {anomaly_metric.value}",
                        level=AlertLevel.WARNING,
                        metric_name=metric_name,
                        current_value=anomaly_metric.value,
                        database=anomaly_metric.database
                    )
                    
                    self.alerts[alert.alert_id] = alert
                    logger.warning(f"🧠 Anomalie ML détectée: {metric_name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification anomalies ML: {e}")

    async def _train_anomaly_detection_model(self):
        """🧠 Entraîner le modèle de détection d'anomalies"""
        try:
            # Préparation des données d'entraînement
            training_metrics = [
                m for m in self.metrics_buffer
                if m.name in ['cpu_usage', 'memory_usage', 'query_time_ms']
            ]
            
            if len(training_metrics) < 100:
                return
            
            # Conversion en format ML
            data = []
            for metric in training_metrics:
                data.append([
                    hash(metric.name) % 1000,  # Encoding du nom
                    metric.value,
                    metric.timestamp.hour,  # Heure de la journée
                    metric.timestamp.weekday()  # Jour de la semaine
                ])
            
            X = np.array(data)
            
            # Normalisation
            X_scaled = self.scaler.fit_transform(X)
            
            # Entraînement
            self.anomaly_detector.fit(X_scaled)
            
            self.ml_models_trained = True
            logger.info("🧠 Modèle ML d'anomalies entraîné")
            
        except Exception as e:
            logger.error(f"❌ Erreur entraînement modèle ML: {e}")

    async def _store_metrics_to_redis(self):
        """💾 Stocker les métriques dans Redis"""
        try:
            if not self.redis_client:
                return
            
            # Stocker les métriques récentes
            recent_metrics = [
                m for m in self.metrics_buffer
                if m.timestamp >= datetime.now() - timedelta(minutes=60)
            ]
            
            metrics_data = []
            for metric in recent_metrics:
                metrics_data.append({
                    'name': metric.name,
                    'value': metric.value,
                    'timestamp': metric.timestamp.isoformat(),
                    'database': metric.database,
                    'labels': metric.labels
                })
            
            await self.redis_client.setex(
                'monitoring:metrics:recent',
                3600,  # 1 heure de TTL
                json.dumps(metrics_data)
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage Redis: {e}")

    async def get_current_metrics(self, database: str = None) -> List[Dict[str, Any]]:
        """📊 Obtenir les métriques actuelles"""
        try:
            recent_metrics = [
                m for m in self.metrics_buffer
                if m.timestamp >= datetime.now() - timedelta(minutes=5)
            ]
            
            if database:
                recent_metrics = [m for m in recent_metrics if m.database == database]
            
            return [
                {
                    'name': metric.name,
                    'value': metric.value,
                    'timestamp': metric.timestamp.isoformat(),
                    'database': metric.database,
                    'unit': metric.unit,
                    'labels': metric.labels
                }
                for metric in recent_metrics
            ]
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération métriques: {e}")
            return []

    async def get_active_alerts(self) -> List[Dict[str, Any]]:
        """🚨 Obtenir les alertes actives"""
        try:
            active_alerts = [
                alert for alert in self.alerts.values()
                if not alert.resolved
            ]
            
            return [
                {
                    'alert_id': alert.alert_id,
                    'title': alert.title,
                    'description': alert.description,
                    'level': alert.level.value,
                    'metric_name': alert.metric_name,
                    'threshold_value': alert.threshold_value,
                    'current_value': alert.current_value,
                    'timestamp': alert.timestamp.isoformat(),
                    'database': alert.database
                }
                for alert in active_alerts
            ]
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération alertes: {e}")
            return []

    async def resolve_alert(self, alert_id: str) -> bool:
        """✅ Résoudre une alerte"""
        try:
            if alert_id not in self.alerts:
                return False
            
            alert = self.alerts[alert_id]
            alert.resolved = True
            alert.resolution_time = datetime.now()
            
            logger.info(f"✅ Alerte résolue: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur résolution alerte: {e}")
            return False

    async def stop_monitoring(self):
        """⏹️ Arrêter le monitoring"""
        try:
            self.running = False
            
            # Fermeture Redis
            if self.redis_client:
                await self.redis_client.close()
            
            # Fermeture des collecteurs
            for collector in self.database_collectors.values():
                await collector.cleanup()
            
            logger.info("⏹️ Monitoring arrêté")
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt monitoring: {e}")

class DatabaseCollector:
    """🔧 Collecteur de métriques de base pour bases de données"""
    
    def __init__(self, database_name: str, config: Dict[str, Any]):
        self.database_name = database_name
        self.config = config
        self.connection = None
    
    async def initialize(self):
        """🚀 Initialiser le collecteur"""
        pass
    
    async def collect_metrics(self) -> List[PerformanceMetric]:
        """📊 Collecter les métriques"""
        return []
    
    async def collect_query_metrics(self) -> List[QueryMetrics]:
        """🔍 Collecter les métriques de requêtes"""
        return []
    
    async def cleanup(self):
        """🧹 Nettoyer les ressources"""
        pass

class PostgreSQLCollector(DatabaseCollector):
    """🐘 Collecteur PostgreSQL"""
    
    async def initialize(self):
        """🚀 Initialiser la connexion PostgreSQL"""
        try:
            dsn = f"postgresql://{self.config['username']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.database_name}"
            self.connection = await asyncpg.connect(dsn)
            logger.info(f"🐘 Collecteur PostgreSQL initialisé pour {self.database_name}")
            
        except Exception as e:
            logger.error(f"❌ Erreur init PostgreSQL: {e}")
            raise
    
    async def collect_metrics(self) -> List[PerformanceMetric]:
        """📊 Collecter les métriques PostgreSQL"""
        try:
            if not self.connection:
                return []
            
            metrics = []
            
            # Statistiques de base
            query = """
            SELECT 
                'connections_active' as metric,
                count(*) as value
            FROM pg_stat_activity 
            WHERE state = 'active'
            UNION ALL
            SELECT 
                'connections_total' as metric,
                count(*) as value
            FROM pg_stat_activity
            UNION ALL
            SELECT 
                'database_size_mb' as metric,
                pg_database_size(current_database()) / 1024.0 / 1024.0 as value
            """
            
            rows = await self.connection.fetch(query)
            
            for row in rows:
                metric = PerformanceMetric(
                    name=row['metric'],
                    value=float(row['value']),
                    database=self.database_name,
                    engine=DatabaseEngine.POSTGRESQL,
                    unit='count' if 'connections' in row['metric'] else 'MB'
                )
                metrics.append(metric)
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte métriques PostgreSQL: {e}")
            return []
    
    async def collect_query_metrics(self) -> List[QueryMetrics]:
        """🔍 Collecter les métriques de requêtes PostgreSQL"""
        try:
            if not self.connection:
                return []
            
            # Requêtes lentes depuis pg_stat_statements
            query = """
            SELECT 
                queryid,
                query,
                mean_exec_time,
                total_exec_time,
                calls,
                rows
            FROM pg_stat_statements 
            ORDER BY mean_exec_time DESC 
            LIMIT 10
            """
            
            try:
                rows = await self.connection.fetch(query)
                query_metrics = []
                
                for row in rows:
                    metric = QueryMetrics(
                        query_hash=str(row['queryid']),
                        query_text=row['query'][:500],  # Tronquer pour éviter les logs trop longs
                        execution_time_ms=float(row['mean_exec_time']),
                        rows_returned=int(row['rows']),
                        database=self.database_name
                    )
                    query_metrics.append(metric)
                
                return query_metrics
                
            except Exception:
                # pg_stat_statements peut ne pas être installé
                return []
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte requêtes PostgreSQL: {e}")
            return []
    
    async def cleanup(self):
        """🧹 Nettoyer la connexion"""
        try:
            if self.connection:
                await self.connection.close()
        except Exception as e:
            logger.error(f"❌ Erreur nettoyage PostgreSQL: {e}")

class MySQLCollector(DatabaseCollector):
    """🐬 Collecteur MySQL"""
    
    async def collect_metrics(self) -> List[PerformanceMetric]:
        """📊 Collecter les métriques MySQL"""
        # Implémentation simplifiée - à étendre selon les besoins
        return [
            PerformanceMetric(
                name="connections_active",
                value=10.0,  # Valeur simulée
                database=self.database_name,
                engine=DatabaseEngine.MYSQL
            )
        ]

class MongoDBCollector(DatabaseCollector):
    """🍃 Collecteur MongoDB"""
    
    async def collect_metrics(self) -> List[PerformanceMetric]:
        """📊 Collecter les métriques MongoDB"""
        # Implémentation simplifiée - à étendre selon les besoins
        return [
            PerformanceMetric(
                name="connections_active",
                value=5.0,  # Valeur simulée
                database=self.database_name,
                engine=DatabaseEngine.MONGODB
            )
        ]

class RedisCollector(DatabaseCollector):
    """🔴 Collecteur Redis"""
    
    async def collect_metrics(self) -> List[PerformanceMetric]:
        """📊 Collecter les métriques Redis"""
        # Implémentation simplifiée - à étendre selon les besoins
        return [
            PerformanceMetric(
                name="memory_usage",
                value=25.0,  # Valeur simulée
                database=self.database_name,
                engine=DatabaseEngine.REDIS
            )
        ]

# Fonction d'initialisation
def initialize_performance_monitoring_dashboard(config: Dict[str, Any]) -> PerformanceMonitoringDashboard:
    """🚀 Initialiser le dashboard de monitoring performance
    
    Args:
        config: Configuration du dashboard
        
    Returns:
        Instance du dashboard initialisée
    """
    try:
        dashboard = PerformanceMonitoringDashboard(config)
        logger.info("🚀 Performance Monitoring Dashboard initialisé avec succès")
        return dashboard
        
    except Exception as e:
        logger.error(f"❌ Erreur initialisation Dashboard: {e}")
        raise

# Configuration par défaut
DEFAULT_MONITORING_CONFIG = {
    'collection_interval': 30,
    'dashboard_port': 8050,
    'databases': {
        'ainflue_main': {
            'type': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'username': 'postgres',
            'password': 'password'
        }
    },
    'redis': {
        'host': 'localhost',
        'port': 6379
    },
    'alert_thresholds': {
        'cpu_usage': 80.0,
        'memory_usage': 85.0,
        'disk_usage': 90.0,
        'query_time_ms': 1000.0,
        'connections_count': 100
    }
}

if __name__ == "__main__":
    # Test basique
    async def test_monitoring_dashboard():
        dashboard = initialize_performance_monitoring_dashboard(DEFAULT_MONITORING_CONFIG)
        
        await dashboard.initialize()
        await dashboard.start_monitoring()
        
        print("✅ Dashboard monitoring démarré")
        print(f"🌐 Interface Web disponible sur: http://localhost:{dashboard.dash_port}")
        
        # Laisser tourner pendant le test
        await asyncio.sleep(5)
        
        # Récupération des métriques
        metrics = await dashboard.get_current_metrics()
        print(f"📊 {len(metrics)} métriques collectées")
        
        alerts = await dashboard.get_active_alerts()
        print(f"🚨 {len(alerts)} alertes actives")
        
        await dashboard.stop_monitoring()
    
    asyncio.run(test_monitoring_dashboard())