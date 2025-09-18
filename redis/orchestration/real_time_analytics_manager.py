#!/usr/bin/env python3
"""📊 Redis Real-Time Analytics Manager - Advanced Real-Time Analytics Intelligence
==================================================================================
Expert: ML ENGINEER + DATA SCIENTIST + BACKEND SENIOR + DEVOPS
Technologies: Real-Time Analytics + Stream Processing + ML Analytics + Creator Economy Intelligence
Architecture: Level 3 - Real-Time Analytics Layer
Date: 2025-01-14

Ultra-advanced real-time analytics system with streaming data processing,
ML-powered insights, creator economy analytics and performance monitoring.
==================================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
==================================================================================
"""

from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging
import time
import numpy as np
from datetime import datetime, timedelta
import json
import math
import statistics
from collections import deque, defaultdict, Counter
import redis
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from concurrent.futures import ThreadPoolExecutor
import uuid
import hashlib

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types de métriques analytics"""
    PERFORMANCE = "performance"
    USER_ENGAGEMENT = "user_engagement"
    BUSINESS = "business"
    TECHNICAL = "technical"
    CREATOR_ECONOMY = "creator_economy"
    CONTENT = "content"
    COLLABORATION = "collaboration"
    MONETIZATION = "monetization"
    SYSTEM_HEALTH = "system_health"
    SECURITY = "security"

class AggregationType(Enum):
    """Types d'agrégation"""
    SUM = "sum"
    AVERAGE = "average"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"
    STDDEV = "stddev"
    RATE = "rate"

class TimeWindow(Enum):
    """Fenêtres temporelles"""
    REAL_TIME = "1s"
    MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "7d"
    MONTH = "30d"

class AlertSeverity(Enum):
    """Niveaux de sévérité alertes"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class DataSource(Enum):
    """Sources de données"""
    REDIS_METRICS = "redis_metrics"
    APPLICATION_LOGS = "application_logs"
    USER_INTERACTIONS = "user_interactions"
    CREATOR_ACTIVITY = "creator_activity"
    CONTENT_PERFORMANCE = "content_performance"
    COLLABORATION_DATA = "collaboration_data"
    MONETIZATION_DATA = "monetization_data"
    SYSTEM_METRICS = "system_metrics"
    EXTERNAL_APIs = "external_apis"

@dataclass
class RealTimeMetric:
    """Métrique temps réel"""
    metric_id: str = ""
    name: str = ""
    value: float = 0.0
    metric_type: MetricType = MetricType.PERFORMANCE
    unit: str = ""
    
    # Métadonnées
    source: DataSource = DataSource.REDIS_METRICS
    tags: Dict[str, str] = field(default_factory=dict)
    dimensions: Dict[str, Any] = field(default_factory=dict)
    
    # Temporel
    timestamp: datetime = field(default_factory=datetime.now)
    time_window: TimeWindow = TimeWindow.REAL_TIME
    
    # Contexte business
    creator_id: Optional[str] = None
    content_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Validation
    is_valid: bool = True
    quality_score: float = 1.0

@dataclass
class AnalyticsRule:
    """Règle d'analyse temps réel"""
    rule_id: str = ""
    name: str = ""
    description: str = ""
    
    # Conditions
    metric_filters: Dict[str, Any] = field(default_factory=dict)
    threshold_conditions: Dict[str, float] = field(default_factory=dict)
    time_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Actions
    alert_config: Dict[str, Any] = field(default_factory=dict)
    notification_config: Dict[str, Any] = field(default_factory=dict)
    auto_actions: List[str] = field(default_factory=list)
    
    # Métadonnées
    enabled: bool = True
    priority: AlertSeverity = AlertSeverity.MEDIUM
    cooldown_period: int = 300  # 5 minutes
    
    # Statistiques
    trigger_count: int = 0
    last_triggered: Optional[datetime] = None
    false_positive_rate: float = 0.0

@dataclass
class AnalyticsAlert:
    """Alerte analytics"""
    alert_id: str = ""
    rule_id: str = ""
    title: str = ""
    description: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    
    # Données déclenchement
    trigger_metric: RealTimeMetric = field(default_factory=RealTimeMetric)
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    
    # Context
    affected_resources: List[str] = field(default_factory=list)
    impact_assessment: str = ""
    recommended_actions: List[str] = field(default_factory=list)
    
    # Timestamps
    triggered_at: datetime = field(default_factory=datetime.now)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # État
    status: str = "active"  # active, acknowledged, resolved, false_positive
    assigned_to: Optional[str] = None

@dataclass
class CreatorAnalytics:
    """Analytics créateur temps réel"""
    creator_id: str = ""
    
    # Métriques d'engagement
    content_views: int = 0
    likes_received: int = 0
    comments_received: int = 0
    shares_received: int = 0
    followers_count: int = 0
    
    # Métriques collaboration
    collaborations_active: int = 0
    collaboration_invites_sent: int = 0
    collaboration_invites_received: int = 0
    
    # Métriques monétisation
    revenue_today: float = 0.0
    revenue_this_week: float = 0.0
    revenue_this_month: float = 0.0
    conversion_rate: float = 0.0
    
    # Métriques performance
    avg_content_performance: float = 0.0
    trending_score: float = 0.0
    viral_coefficient: float = 0.0
    
    # Prédictions
    predicted_growth: float = 0.0
    churn_risk: float = 0.0
    monetization_potential: float = 0.0
    
    # Timestamps
    last_updated: datetime = field(default_factory=datetime.now)
    data_freshness: float = 1.0  # 0-1, 1 = très frais

@dataclass
class SystemAnalytics:
    """Analytics système temps réel"""
    # Performance Redis
    redis_cpu_usage: float = 0.0
    redis_memory_usage: float = 0.0
    redis_operations_per_sec: int = 0
    redis_latency_avg: float = 0.0
    redis_connections_active: int = 0
    
    # Métriques application
    api_requests_per_sec: int = 0
    api_error_rate: float = 0.0
    api_response_time_avg: float = 0.0
    active_users_count: int = 0
    
    # Métriques business
    content_uploads_per_minute: int = 0
    collaborations_created_per_hour: int = 0
    revenue_per_minute: float = 0.0
    
    # Alertes actives
    active_alerts_count: int = 0
    critical_alerts_count: int = 0
    
    timestamp: datetime = field(default_factory=datetime.now)

class RedisRealTimeAnalyticsManager:
    """📊 Gestionnaire analytics temps réel Redis ultra-avancé"""
    
    def __init__(self):
        """Initialisation gestionnaire analytics"""
        self.redis_client = None
        self.is_running = False
        
        # Storage analytics
        self.real_time_metrics = defaultdict(deque)
        self.aggregated_metrics = defaultdict(dict)
        self.analytics_rules = {}
        self.active_alerts = {}
        self.creator_analytics = {}
        self.system_analytics = SystemAnalytics()
        
        # Système de traitement stream
        self.metric_streams = defaultdict(deque)
        self.processing_queues = defaultdict(deque)
        self.stream_processors = {}
        
        # ML pour analytics
        self.scaler = MinMaxScaler()
        self.anomaly_detector = None
        self.trend_predictor = None
        
        # Cache intelligent
        self.query_cache = {}
        self.aggregation_cache = {}
        self.dashboard_cache = {}
        
        # Configuration performance
        self.max_metrics_memory = 100000
        self.retention_periods = {
            TimeWindow.REAL_TIME: 3600,      # 1 heure
            TimeWindow.MINUTE: 86400,        # 1 jour
            TimeWindow.HOUR: 2592000,        # 30 jours
            TimeWindow.DAY: 31536000         # 1 an
        }
        
        # Métriques système
        self.processing_stats = {
            "metrics_processed": 0,
            "alerts_generated": 0,
            "queries_served": 0,
            "cache_hits": 0,
            "processing_time_avg": 0.0
        }
        
        # Initialiser règles par défaut
        self._initialize_default_rules()
        
        logger.info("📊 Gestionnaire analytics temps réel initialisé")

    async def start(self, redis_connection=None):
        """Démarrer le gestionnaire analytics"""
        try:
            self.redis_client = redis_connection or redis.Redis(decode_responses=True)
            self.is_running = True
            
            # Démarrer processus analytics
            analytics_tasks = [
                self._run_metric_collection(),
                self._run_stream_processing(),
                self._run_aggregation_engine(),
                self._run_alert_monitoring(),
                self._run_creator_analytics(),
                self._run_system_analytics(),
                self._run_cache_maintenance(),
                self._run_data_retention()
            ]
            
            await asyncio.gather(*analytics_tasks, return_exceptions=True)
            
            logger.info("📊 Gestionnaire analytics temps réel démarré")
            
        except Exception as e:
            logger.error(f"❌ Erreur démarrage analytics: {e}")
            raise

    async def stop(self):
        """Arrêter le gestionnaire"""
        self.is_running = False
        logger.info("📊 Gestionnaire analytics temps réel arrêté")

    async def ingest_metric(self, metric: RealTimeMetric) -> bool:
        """Ingérer une métrique temps réel"""
        try:
            # Validation métrique
            if not await self._validate_metric(metric):
                logger.warning(f"⚠️ Métrique invalide rejetée: {metric.metric_id}")
                return False
            
            # Enrichissement métrique
            metric = await self._enrich_metric(metric)
            
            # Stockage temps réel
            metric_key = f"{metric.metric_type.value}:{metric.name}"
            self.real_time_metrics[metric_key].append(metric)
            
            # Limitation mémoire
            if len(self.real_time_metrics[metric_key]) > self.max_metrics_memory:
                self.real_time_metrics[metric_key].popleft()
            
            # Ajout aux streams de traitement
            self.metric_streams[metric.metric_type].append(metric)
            
            # Déclenchement éventuel d'alertes
            await self._check_alert_conditions(metric)
            
            # Mise à jour analytics créateur si applicable
            if metric.creator_id:
                await self._update_creator_analytics(metric)
            
            # Mise à jour statistiques
            self.processing_stats["metrics_processed"] += 1
            
            logger.debug(f"📊 Métrique ingérée: {metric.name} = {metric.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur ingestion métrique: {e}")
            return False

    async def query_metrics(self, 
                          metric_type: Optional[MetricType] = None,
                          time_range: Optional[Tuple[datetime, datetime]] = None,
                          aggregation: AggregationType = AggregationType.AVERAGE,
                          time_window: TimeWindow = TimeWindow.MINUTE,
                          filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Requête métriques avec agrégation"""
        try:
            # Génération clé cache
            cache_key = self._generate_query_cache_key(
                metric_type, time_range, aggregation, time_window, filters
            )
            
            # Vérification cache
            cached_result = self.query_cache.get(cache_key)
            if cached_result and self._is_cache_valid(cached_result):
                self.processing_stats["cache_hits"] += 1
                return cached_result["data"]
            
            # Collecte métriques
            metrics = await self._collect_metrics_for_query(
                metric_type, time_range, filters
            )
            
            # Agrégation
            aggregated_data = await self._aggregate_metrics(
                metrics, aggregation, time_window
            )
            
            # Mise en cache
            self.query_cache[cache_key] = {
                "data": aggregated_data,
                "timestamp": datetime.now(),
                "ttl": 60  # 1 minute
            }
            
            self.processing_stats["queries_served"] += 1
            
            logger.info(f"📊 Requête exécutée: {len(aggregated_data)} points")
            return aggregated_data
            
        except Exception as e:
            logger.error(f"❌ Erreur requête métriques: {e}")
            return []

    async def get_creator_dashboard(self, creator_id: str) -> Dict[str, Any]:
        """Récupérer tableau de bord créateur"""
        try:
            # Vérifier cache dashboard
            cache_key = f"creator_dashboard:{creator_id}"
            cached_dashboard = self.dashboard_cache.get(cache_key)
            
            if cached_dashboard and self._is_cache_valid(cached_dashboard):
                return cached_dashboard["data"]
            
            # Analytics créateur
            creator_analytics = self.creator_analytics.get(creator_id, CreatorAnalytics(creator_id=creator_id))
            
            # Métriques temps réel
            recent_metrics = await self._get_creator_recent_metrics(creator_id)
            
            # Trends et prédictions
            engagement_trend = await self._calculate_engagement_trend(creator_id)
            revenue_forecast = await self._forecast_creator_revenue(creator_id)
            growth_insights = await self._generate_growth_insights(creator_id)
            
            # Performance contenu
            content_performance = await self._analyze_creator_content_performance(creator_id)
            
            # Opportunités
            collaboration_opportunities = await self._find_collaboration_opportunities(creator_id)
            monetization_opportunities = await self._identify_monetization_opportunities(creator_id)
            
            dashboard = {
                "creator_id": creator_id,
                "timestamp": datetime.now().isoformat(),
                
                # Métriques principales
                "key_metrics": {
                    "total_followers": creator_analytics.followers_count,
                    "engagement_rate": await self._calculate_engagement_rate(creator_id),
                    "revenue_today": creator_analytics.revenue_today,
                    "content_performance_score": creator_analytics.avg_content_performance,
                    "trending_score": creator_analytics.trending_score
                },
                
                # Données temps réel
                "real_time_data": {
                    "active_collaborations": creator_analytics.collaborations_active,
                    "views_last_hour": recent_metrics.get("views_last_hour", 0),
                    "engagement_last_hour": recent_metrics.get("engagement_last_hour", 0),
                    "revenue_last_hour": recent_metrics.get("revenue_last_hour", 0.0)
                },
                
                # Tendances
                "trends": {
                    "engagement_trend": engagement_trend,
                    "follower_growth_rate": await self._calculate_follower_growth_rate(creator_id),
                    "content_frequency_trend": await self._analyze_content_frequency_trend(creator_id)
                },
                
                # Prédictions
                "predictions": {
                    "revenue_forecast": revenue_forecast,
                    "growth_prediction": creator_analytics.predicted_growth,
                    "churn_risk": creator_analytics.churn_risk,
                    "viral_probability": await self._predict_viral_probability(creator_id)
                },
                
                # Performance contenu
                "content_analytics": content_performance,
                
                # Opportunités
                "opportunities": {
                    "collaborations": collaboration_opportunities,
                    "monetization": monetization_opportunities,
                    "content_ideas": await self._suggest_content_ideas(creator_id)
                },
                
                # Insights actionnables
                "insights": growth_insights,
                
                # Alertes
                "alerts": await self._get_creator_alerts(creator_id)
            }
            
            # Mise en cache
            self.dashboard_cache[cache_key] = {
                "data": dashboard,
                "timestamp": datetime.now(),
                "ttl": 300  # 5 minutes
            }
            
            logger.info(f"📊 Dashboard généré pour créateur {creator_id}")
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Erreur génération dashboard créateur: {e}")
            return {"error": str(e)}

    async def get_system_dashboard(self) -> Dict[str, Any]:
        """Récupérer tableau de bord système"""
        try:
            # Métriques système actuelles
            system_metrics = await self._collect_system_metrics()
            
            # Performance Redis
            redis_performance = await self._analyze_redis_performance()
            
            # Métriques business
            business_metrics = await self._collect_business_metrics()
            
            # Alertes actives
            active_alerts = list(self.active_alerts.values())
            
            # Trends système
            performance_trends = await self._analyze_system_trends()
            
            # Prédictions capacité
            capacity_forecast = await self._forecast_system_capacity()
            
            dashboard = {
                "timestamp": datetime.now().isoformat(),
                
                # Vue d'ensemble
                "overview": {
                    "system_health": await self._calculate_system_health_score(),
                    "total_users_active": system_metrics.get("active_users", 0),
                    "total_creators": await self._count_active_creators(),
                    "total_content": await self._count_total_content(),
                    "revenue_today": business_metrics.get("revenue_today", 0.0)
                },
                
                # Performance système
                "system_performance": {
                    "redis_performance": redis_performance,
                    "api_performance": {
                        "requests_per_second": system_metrics.get("api_rps", 0),
                        "average_response_time": system_metrics.get("api_avg_response", 0),
                        "error_rate": system_metrics.get("api_error_rate", 0)
                    },
                    "resource_utilization": {
                        "cpu_usage": system_metrics.get("cpu_usage", 0),
                        "memory_usage": system_metrics.get("memory_usage", 0),
                        "disk_usage": system_metrics.get("disk_usage", 0)
                    }
                },
                
                # Métriques business
                "business_metrics": {
                    "creator_activity": {
                        "content_uploads_per_hour": business_metrics.get("content_uploads_hourly", 0),
                        "collaborations_created_daily": business_metrics.get("collaborations_daily", 0),
                        "active_creators_percentage": business_metrics.get("active_creators_pct", 0)
                    },
                    "engagement": {
                        "total_interactions_per_minute": business_metrics.get("interactions_per_minute", 0),
                        "average_session_duration": business_metrics.get("avg_session_duration", 0),
                        "user_retention_rate": business_metrics.get("retention_rate", 0)
                    },
                    "monetization": {
                        "revenue_per_hour": business_metrics.get("revenue_hourly", 0),
                        "conversion_rate": business_metrics.get("conversion_rate", 0),
                        "average_transaction_value": business_metrics.get("avg_transaction", 0)
                    }
                },
                
                # Alertes
                "alerts": {
                    "active_count": len(active_alerts),
                    "critical_count": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
                    "recent_alerts": sorted(active_alerts, key=lambda x: x.triggered_at, reverse=True)[:10]
                },
                
                # Tendances
                "trends": performance_trends,
                
                # Prédictions
                "forecasts": capacity_forecast,
                
                # Recommandations
                "recommendations": await self._generate_system_recommendations()
            }
            
            logger.info("📊 Dashboard système généré")
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Erreur génération dashboard système: {e}")
            return {"error": str(e)}

    async def create_custom_alert(self, rule: AnalyticsRule) -> str:
        """Créer une alerte personnalisée"""
        try:
            rule.rule_id = rule.rule_id or str(uuid.uuid4())
            
            # Validation règle
            if not await self._validate_analytics_rule(rule):
                raise ValueError("Règle d'alerte invalide")
            
            # Sauvegarde
            self.analytics_rules[rule.rule_id] = rule
            await self._persist_analytics_rule(rule)
            
            logger.info(f"📊 Règle d'alerte créée: {rule.name}")
            return rule.rule_id
            
        except Exception as e:
            logger.error(f"❌ Erreur création alerte: {e}")
            raise

    async def get_analytics_report(self, 
                                 report_type: str = "comprehensive",
                                 time_period: str = "24h",
                                 include_predictions: bool = True) -> Dict[str, Any]:
        """Générer rapport analytics complet"""
        try:
            end_time = datetime.now()
            if time_period == "1h":
                start_time = end_time - timedelta(hours=1)
            elif time_period == "24h":
                start_time = end_time - timedelta(days=1)
            elif time_period == "7d":
                start_time = end_time - timedelta(days=7)
            elif time_period == "30d":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=1)
            
            report = {
                "report_type": report_type,
                "time_period": time_period,
                "generated_at": end_time.isoformat(),
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                }
            }
            
            if report_type in ["comprehensive", "performance"]:
                report["performance_analysis"] = await self._generate_performance_report(start_time, end_time)
            
            if report_type in ["comprehensive", "creator_economy"]:
                report["creator_economy_analysis"] = await self._generate_creator_economy_report(start_time, end_time)
            
            if report_type in ["comprehensive", "business"]:
                report["business_analysis"] = await self._generate_business_report(start_time, end_time)
            
            if report_type in ["comprehensive", "technical"]:
                report["technical_analysis"] = await self._generate_technical_report(start_time, end_time)
            
            if include_predictions:
                report["predictions"] = await self._generate_prediction_report()
            
            report["summary"] = await self._generate_report_summary(report)
            report["recommendations"] = await self._generate_report_recommendations(report)
            
            logger.info(f"📊 Rapport analytics généré: {report_type}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur génération rapport: {e}")
            return {"error": str(e)}

    # ================== MÉTHODES PRIVÉES ==================

    def _initialize_default_rules(self):
        """Initialiser règles d'alerte par défaut"""
        # Règle performance Redis
        redis_performance_rule = AnalyticsRule(
            rule_id="redis_high_cpu",
            name="Redis CPU élevé",
            description="Alerte quand CPU Redis > 80%",
            metric_filters={"metric_type": MetricType.PERFORMANCE, "name": "redis_cpu_usage"},
            threshold_conditions={"value": 80.0},
            alert_config={"severity": AlertSeverity.HIGH},
            enabled=True
        )
        self.analytics_rules["redis_high_cpu"] = redis_performance_rule
        
        # Règle engagement créateurs
        creator_engagement_rule = AnalyticsRule(
            rule_id="creator_low_engagement",
            name="Engagement créateur faible",
            description="Alerte engagement créateur < 5%",
            metric_filters={"metric_type": MetricType.USER_ENGAGEMENT},
            threshold_conditions={"engagement_rate": 0.05},
            alert_config={"severity": AlertSeverity.MEDIUM},
            enabled=True
        )
        self.analytics_rules["creator_low_engagement"] = creator_engagement_rule

    async def _run_metric_collection(self):
        """Collection métriques en continu"""
        while self.is_running:
            try:
                # Collecter métriques système
                await self._collect_system_metrics()
                
                # Collecter métriques business
                await self._collect_business_metrics()
                
                # Collecter métriques Redis
                await self._collect_redis_metrics()
                
                await asyncio.sleep(1)  # Collection toutes les secondes
            except Exception as e:
                logger.error(f"❌ Erreur collection métriques: {e}")
                await asyncio.sleep(5)

    async def _run_stream_processing(self):
        """Traitement streams métriques"""
        while self.is_running:
            try:
                for metric_type, stream in self.metric_streams.items():
                    if stream:
                        await self._process_metric_stream(metric_type, stream)
                await asyncio.sleep(0.1)  # Traitement rapide
            except Exception as e:
                logger.error(f"❌ Erreur traitement streams: {e}")
                await asyncio.sleep(1)

    async def _run_aggregation_engine(self):
        """Moteur d'agrégation"""
        while self.is_running:
            try:
                await self._run_metric_aggregations()
                await asyncio.sleep(60)  # Agrégation toutes les minutes
            except Exception as e:
                logger.error(f"❌ Erreur agrégation: {e}")
                await asyncio.sleep(60)

    async def _run_alert_monitoring(self):
        """Monitoring des alertes"""
        while self.is_running:
            try:
                await self._process_active_alerts()
                await asyncio.sleep(30)  # Check toutes les 30 secondes
            except Exception as e:
                logger.error(f"❌ Erreur monitoring alertes: {e}")
                await asyncio.sleep(60)

    async def _run_creator_analytics(self):
        """Analytics créateurs en continu"""
        while self.is_running:
            try:
                await self._update_all_creator_analytics()
                await asyncio.sleep(300)  # Toutes les 5 minutes
            except Exception as e:
                logger.error(f"❌ Erreur analytics créateurs: {e}")
                await asyncio.sleep(300)

    async def _run_system_analytics(self):
        """Analytics système en continu"""
        while self.is_running:
            try:
                self.system_analytics = await self._calculate_system_analytics()
                await asyncio.sleep(60)  # Toutes les minutes
            except Exception as e:
                logger.error(f"❌ Erreur analytics système: {e}")
                await asyncio.sleep(120)

    async def _run_cache_maintenance(self):
        """Maintenance cache"""
        while self.is_running:
            try:
                await self._clean_expired_caches()
                await asyncio.sleep(600)  # Toutes les 10 minutes
            except Exception as e:
                logger.error(f"❌ Erreur maintenance cache: {e}")
                await asyncio.sleep(300)

    async def _run_data_retention(self):
        """Gestion rétention données"""
        while self.is_running:
            try:
                await self._apply_retention_policies()
                await asyncio.sleep(3600)  # Toutes les heures
            except Exception as e:
                logger.error(f"❌ Erreur rétention données: {e}")
                await asyncio.sleep(1800)

    async def _validate_metric(self, metric: RealTimeMetric) -> bool:
        """Valider une métrique"""
        if not metric.name or not metric.metric_id:
            return False
        if math.isnan(metric.value) or math.isinf(metric.value):
            return False
        if metric.timestamp > datetime.now() + timedelta(minutes=5):
            return False
        return True

    async def _enrich_metric(self, metric: RealTimeMetric) -> RealTimeMetric:
        """Enrichir une métrique"""
        # Ajouter tags automatiques
        metric.tags["hostname"] = "redis-orchestrator"
        metric.tags["environment"] = "production"
        
        # Calculer score qualité
        quality_factors = []
        if metric.source != DataSource.EXTERNAL_APIs:
            quality_factors.append(1.0)
        else:
            quality_factors.append(0.8)
        
        metric.quality_score = np.mean(quality_factors)
        
        return metric

    def _generate_query_cache_key(self, 
                                 metric_type: Optional[MetricType],
                                 time_range: Optional[Tuple[datetime, datetime]],
                                 aggregation: AggregationType,
                                 time_window: TimeWindow,
                                 filters: Dict[str, Any]) -> str:
        """Générer clé cache requête"""
        key_parts = [
            metric_type.value if metric_type else "all",
            f"{time_range[0].isoformat()}_{time_range[1].isoformat()}" if time_range else "all_time",
            aggregation.value,
            time_window.value,
            hashlib.md5(str(filters or {}).encode()).hexdigest()[:8]
        ]
        return ":".join(key_parts)

    def _is_cache_valid(self, cached_item: Dict[str, Any]) -> bool:
        """Vérifier validité cache"""
        cache_age = (datetime.now() - cached_item["timestamp"]).total_seconds()
        return cache_age < cached_item.get("ttl", 300)

    def get_metrics(self) -> Dict[str, Any]:
        """Récupérer métriques gestionnaire"""
        return {
            "manager_type": "real_time_analytics",
            "status": "running" if self.is_running else "stopped",
            "metrics_in_memory": sum(len(stream) for stream in self.real_time_metrics.values()),
            "active_alerts": len(self.active_alerts),
            "analytics_rules": len(self.analytics_rules),
            "creator_analytics_count": len(self.creator_analytics),
            "processing_stats": self.processing_stats,
            "cache_sizes": {
                "query_cache": len(self.query_cache),
                "aggregation_cache": len(self.aggregation_cache),
                "dashboard_cache": len(self.dashboard_cache)
            }
        }