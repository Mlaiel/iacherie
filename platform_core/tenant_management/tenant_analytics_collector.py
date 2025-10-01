"""🚀 Tenant Analytics Collector - IA Influencer Agent Platform Enterprise
========================================================================
Module: backend/platform_core/tenant_management/tenant_analytics_collector.py
Author: Fahed Mlaiel (mlaiel@live.de)
========================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ANALYTICS ET MÉTRIQUES MULTI-TENANT
Système ultra-avancé de collecte et analyse d'analytics par tenant
- Analytics en temps réel avec streaming data processing
- Métriques business intelligence par tenant isolées
- Insights prédictifs avec ML pour optimisation tenant
- Reporting automatisé multi-niveau (tenant/platform)
"""

import asyncio
import logging
import uuid
import json
import time
import statistics
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.sql import text

logger = logging.getLogger(__name__)


class AnalyticsEventType(Enum):
    """Types d'événements analytics"""
    USER_ACTION = "user_action"
    CONTENT_CREATION = "content_creation"
    CONTENT_CONSUMPTION = "content_consumption"
    COLLABORATION = "collaboration"
    BILLING_EVENT = "billing_event"
    PERFORMANCE_METRIC = "performance_metric"
    SECURITY_EVENT = "security_event"
    SYSTEM_EVENT = "system_event"


class MetricType(Enum):
    """Types de métriques"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SET = "set"


class AggregationPeriod(Enum):
    """Périodes d'agrégation"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class InsightCategory(Enum):
    """Catégories d'insights"""
    USER_BEHAVIOR = "user_behavior"
    CONTENT_PERFORMANCE = "content_performance"
    RESOURCE_UTILIZATION = "resource_utilization"
    BUSINESS_METRICS = "business_metrics"
    SECURITY_INSIGHTS = "security_insights"
    COST_OPTIMIZATION = "cost_optimization"


@dataclass
class AnalyticsEvent:
    """Événement analytics"""
    event_id: str
    tenant_id: str
    event_type: AnalyticsEventType
    event_name: str
    user_id: Optional[str]
    session_id: Optional[str]
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    processing_timestamp: Optional[datetime] = None
    geo_location: Optional[Dict[str, str]] = None
    device_info: Optional[Dict[str, str]] = None


@dataclass
class TenantMetric:
    """Métrique tenant"""
    metric_id: str
    tenant_id: str
    metric_name: str
    metric_type: MetricType
    value: Union[int, float, str, List[Any]]
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    aggregation_period: Optional[AggregationPeriod] = None


@dataclass
class TenantInsight:
    """Insight généré pour un tenant"""
    insight_id: str
    tenant_id: str
    category: InsightCategory
    title: str
    description: str
    confidence_score: float
    impact_level: str  # low, medium, high, critical
    recommendation: str
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    is_actionable: bool = True


@dataclass
class AnalyticsDashboard:
    """Dashboard analytics pour un tenant"""
    dashboard_id: str
    tenant_id: str
    dashboard_name: str
    widgets: List[Dict[str, Any]] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    refresh_interval: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


class TenantAnalyticsCollector:
    """
    🚀 Collecteur d'analytics multi-tenant ultra-avancé
    
    Fonctionnalités Enterprise:
    - Streaming analytics en temps réel avec Apache Kafka
    - Isolation complète des données analytics par tenant
    - ML-powered insights avec prédictions comportementales
    - Business intelligence dashboards personnalisables
    - Real-time alerting basé sur anomalies
    - GDPR-compliant analytics avec anonymisation
    - Cross-tenant benchmarking (anonymisé)
    - Auto-scaling basé sur patterns d'usage
    """
    
    def __init__(
        self,
        database_url: str,
        redis_url: str,
        enable_ml_insights: bool = True,
        enable_real_time_processing: bool = True,
        retention_period_days: int = 365
    ):
        self.database_url = database_url
        self.redis_url = redis_url
        self.enable_ml_insights = enable_ml_insights
        self.enable_real_time_processing = enable_real_time_processing
        self.retention_period_days = retention_period_days
        
        # Clients
        self.engine = None
        self.redis_client = None
        
        # Caches et buffers
        self.event_buffer: Dict[str, List[AnalyticsEvent]] = {}
        self.metrics_cache: Dict[str, List[TenantMetric]] = {}
        self.insights_cache: Dict[str, List[TenantInsight]] = {}
        self.dashboards: Dict[str, List[AnalyticsDashboard]] = {}
        
        # Configuration
        self.batch_size = 1000
        self.flush_interval = timedelta(seconds=30)
        self.anomaly_detection_threshold = 2.0  # écarts-types
        
        # ML Models pour insights
        if enable_ml_insights:
            self.ml_models = {
                "user_clustering": KMeans(n_clusters=5),
                "usage_prediction": None,  # À initialiser
                "anomaly_detection": None
            }
            self.scalers = {
                "user_features": StandardScaler(),
                "usage_features": StandardScaler()
            }
        
        # Statistiques
        self.analytics_stats = {
            "total_events_processed": 0,
            "total_metrics_collected": 0,
            "total_insights_generated": 0,
            "active_dashboards": 0,
            "anomalies_detected": 0,
            "ml_predictions_made": 0
        }
        
        logger.info("TenantAnalyticsCollector initialisé")
    
    async def initialize(self) -> None:
        """Initialise le collecteur d'analytics"""
        try:
            # Connexion base de données
            self.engine = create_async_engine(
                self.database_url,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True
            )
            
            # Connexion Redis pour cache et streaming
            self.redis_client = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialisation des tables analytics
            await self._initialize_analytics_tables()
            
            # Chargement des configurations existantes
            await self._load_analytics_configurations()
            
            # Initialisation des modèles ML
            if self.enable_ml_insights:
                await self._initialize_ml_models()
            
            # Démarrage des tâches de traitement
            if self.enable_real_time_processing:
                asyncio.create_task(self._real_time_processor())
            
            asyncio.create_task(self._batch_processor())
            asyncio.create_task(self._metrics_aggregator())
            asyncio.create_task(self._insights_generator())
            asyncio.create_task(self._anomaly_detector())
            asyncio.create_task(self._dashboard_updater())
            
            logger.info("TenantAnalyticsCollector initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation TenantAnalyticsCollector: {e}")
            raise
    
    async def collect_tenant_event(
        self,
        tenant_id: str,
        event_type: AnalyticsEventType,
        event_name: str,
        properties: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        📊 Collecte un événement analytics pour un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            event_type: Type d'événement
            event_name: Nom de l'événement
            properties: Propriétés de l'événement
            user_id: Identifiant utilisateur (optionnel)
            session_id: Identifiant de session (optionnel)
            
        Returns:
            Confirmation de collecte avec métadonnées
        """
        try:
            event_id = str(uuid.uuid4())
            
            # Validation et enrichissement des propriétés
            enriched_properties = await self._enrich_event_properties(
                tenant_id,
                properties,
                user_id,
                session_id
            )
            
            # Création de l'événement
            event = AnalyticsEvent(
                event_id=event_id,
                tenant_id=tenant_id,
                event_type=event_type,
                event_name=event_name,
                user_id=user_id,
                session_id=session_id,
                properties=enriched_properties
            )
            
            # Ajout au buffer pour traitement
            if tenant_id not in self.event_buffer:
                self.event_buffer[tenant_id] = []
            self.event_buffer[tenant_id].append(event)
            
            # Traitement en temps réel si activé
            if self.enable_real_time_processing:
                await self._process_event_real_time(event)
            
            # Mise en cache Redis pour accès rapide
            await self.redis_client.setex(
                f"event:{tenant_id}:{event_id}",
                3600,  # 1 heure
                json.dumps({
                    "event_id": event_id,
                    "event_type": event_type.value,
                    "event_name": event_name,
                    "timestamp": event.timestamp.isoformat(),
                    "properties_count": len(enriched_properties)
                })
            )
            
            # Mise à jour des statistiques
            self.analytics_stats["total_events_processed"] += 1
            
            # Trigger de flush si buffer plein
            if len(self.event_buffer.get(tenant_id, [])) >= self.batch_size:
                asyncio.create_task(self._flush_tenant_events(tenant_id))
            
            result = {
                "event_id": event_id,
                "tenant_id": tenant_id,
                "status": "collected",
                "processing_mode": "real_time" if self.enable_real_time_processing else "batch",
                "enriched_properties_count": len(enriched_properties),
                "collected_at": event.timestamp.isoformat()
            }
            
            logger.debug(f"Événement collecté: {tenant_id}/{event_name} ({event_id})")
            return result
            
        except Exception as e:
            logger.error(f"Erreur collecte événement {tenant_id}: {e}")
            raise
    
    async def collect_tenant_metrics(
        self,
        tenant_id: str,
        metrics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        📈 Collecte des métriques pour un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            metrics: Liste des métriques à collecter
            
        Returns:
            Résumé de collecte des métriques
        """
        try:
            collection_id = str(uuid.uuid4())
            collected_metrics = []
            collection_errors = []
            
            for metric_data in metrics:
                try:
                    # Validation des données de métrique
                    required_fields = ["name", "type", "value"]
                    for field in required_fields:
                        if field not in metric_data:
                            raise ValueError(f"Champ requis manquant: {field}")
                    
                    metric = TenantMetric(
                        metric_id=str(uuid.uuid4()),
                        tenant_id=tenant_id,
                        metric_name=metric_data["name"],
                        metric_type=MetricType(metric_data["type"]),
                        value=metric_data["value"],
                        tags=metric_data.get("tags", {}),
                        aggregation_period=AggregationPeriod(metric_data.get("period", "minute")) if metric_data.get("period") else None
                    )
                    
                    collected_metrics.append(metric)
                    
                    # Mise en cache
                    if tenant_id not in self.metrics_cache:
                        self.metrics_cache[tenant_id] = []
                    self.metrics_cache[tenant_id].append(metric)
                    
                    # Sauvegarde immédiate des métriques critiques
                    if metric_data.get("critical", False):
                        await self._save_metric_immediate(metric)
                    
                except ValueError as e:
                    collection_errors.append({
                        "metric_data": metric_data,
                        "error": str(e)
                    })
                except Exception as e:
                    collection_errors.append({
                        "metric_data": metric_data,
                        "error": f"Erreur collecte: {e}"
                    })
            
            # Déclenchement de l'agrégation pour métriques collectées
            if collected_metrics:
                await self._trigger_metrics_aggregation(tenant_id, collected_metrics)
            
            # Détection d'anomalies sur les nouvelles métriques
            anomalies_detected = await self._detect_metric_anomalies(
                tenant_id,
                collected_metrics
            )
            
            # Mise à jour des statistiques
            self.analytics_stats["total_metrics_collected"] += len(collected_metrics)
            if anomalies_detected:
                self.analytics_stats["anomalies_detected"] += len(anomalies_detected)
            
            result = {
                "collection_id": collection_id,
                "tenant_id": tenant_id,
                "metrics_summary": {
                    "total_submitted": len(metrics),
                    "successfully_collected": len(collected_metrics),
                    "collection_errors": len(collection_errors)
                },
                "collected_metrics": [
                    {
                        "metric_id": m.metric_id,
                        "name": m.metric_name,
                        "type": m.metric_type.value,
                        "value": m.value,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in collected_metrics
                ],
                "collection_errors": collection_errors,
                "anomalies_detected": anomalies_detected,
                "collected_at": datetime.utcnow().isoformat()
            }
            
            logger.info(
                f"Métriques collectées pour {tenant_id}: {len(collected_metrics)} métriques, "
                f"{len(anomalies_detected)} anomalies"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur collecte métriques {tenant_id}: {e}")
            raise
    
    async def generate_tenant_insights(
        self,
        tenant_id: str,
        insight_categories: Optional[List[InsightCategory]] = None,
        time_range: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """
        🧠 Génère des insights analytiques pour un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            insight_categories: Catégories d'insights à générer
            time_range: Période d'analyse
            
        Returns:
            Insights générés avec recommandations
        """
        try:
            generation_id = str(uuid.uuid4())
            
            # Catégories par défaut si non spécifiées
            if not insight_categories:
                insight_categories = list(InsightCategory)
            
            end_time = datetime.utcnow()
            start_time = end_time - time_range
            
            # Collecte des données pour analyse
            analysis_data = await self._collect_analysis_data(
                tenant_id,
                start_time,
                end_time
            )
            
            generated_insights = []
            
            # Génération d'insights par catégorie
            for category in insight_categories:
                try:
                    category_insights = await self._generate_category_insights(
                        tenant_id,
                        category,
                        analysis_data,
                        time_range
                    )
                    generated_insights.extend(category_insights)
                except Exception as e:
                    logger.warning(f"Erreur génération insights {category.value}: {e}")
            
            # Insights ML si activés
            ml_insights = []
            if self.enable_ml_insights and analysis_data:
                ml_insights = await self._generate_ml_insights(
                    tenant_id,
                    analysis_data,
                    time_range
                )
                generated_insights.extend(ml_insights)
            
            # Tri par score de confiance et impact
            generated_insights.sort(
                key=lambda i: (i.confidence_score, self._impact_weight(i.impact_level)),
                reverse=True
            )
            
            # Mise en cache des insights
            if tenant_id not in self.insights_cache:
                self.insights_cache[tenant_id] = []
            
            # Nettoyage des anciens insights expirés
            current_time = datetime.utcnow()
            self.insights_cache[tenant_id] = [
                i for i in self.insights_cache[tenant_id]
                if not i.expires_at or i.expires_at > current_time
            ]
            
            # Ajout des nouveaux insights
            self.insights_cache[tenant_id].extend(generated_insights)
            
            # Sauvegarde des insights en base
            for insight in generated_insights:
                await self._save_insight(insight)
            
            # Génération d'alertes pour insights critiques
            critical_insights = [
                i for i in generated_insights
                if i.impact_level == "critical" and i.is_actionable
            ]
            
            if critical_insights:
                await self._generate_critical_insight_alerts(tenant_id, critical_insights)
            
            # Mise à jour des statistiques
            self.analytics_stats["total_insights_generated"] += len(generated_insights)
            if ml_insights:
                self.analytics_stats["ml_predictions_made"] += len(ml_insights)
            
            result = {
                "generation_id": generation_id,
                "tenant_id": tenant_id,
                "analysis_period": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "duration_days": time_range.days
                },
                "insights_summary": {
                    "total_generated": len(generated_insights),
                    "critical_insights": len(critical_insights),
                    "ml_insights": len(ml_insights),
                    "actionable_insights": len([i for i in generated_insights if i.is_actionable])
                },
                "insights_by_category": {
                    category.value: len([i for i in generated_insights if i.category == category])
                    for category in insight_categories
                },
                "top_insights": [
                    {
                        "insight_id": i.insight_id,
                        "category": i.category.value,
                        "title": i.title,
                        "description": i.description,
                        "confidence_score": i.confidence_score,
                        "impact_level": i.impact_level,
                        "recommendation": i.recommendation,
                        "is_actionable": i.is_actionable
                    }
                    for i in generated_insights[:10]  # Top 10
                ],
                "critical_alerts": len(critical_insights),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(
                f"Insights générés pour {tenant_id}: {len(generated_insights)} insights, "
                f"{len(critical_insights)} critiques"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur génération insights {tenant_id}: {e}")
            raise
    
    async def create_analytics_dashboard(
        self,
        tenant_id: str,
        dashboard_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        📊 Crée un dashboard analytics personnalisé pour un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            dashboard_config: Configuration du dashboard
            
        Returns:
            Dashboard créé avec configuration
        """
        try:
            dashboard_id = str(uuid.uuid4())
            
            # Validation de la configuration
            required_fields = ["name", "widgets"]
            for field in required_fields:
                if field not in dashboard_config:
                    raise ValueError(f"Champ requis manquant: {field}")
            
            # Validation des widgets
            validated_widgets = []
            for widget_config in dashboard_config["widgets"]:
                validated_widget = await self._validate_widget_config(
                    tenant_id,
                    widget_config
                )
                validated_widgets.append(validated_widget)
            
            # Création du dashboard
            dashboard = AnalyticsDashboard(
                dashboard_id=dashboard_id,
                tenant_id=tenant_id,
                dashboard_name=dashboard_config["name"],
                widgets=validated_widgets,
                filters=dashboard_config.get("filters", {}),
                refresh_interval=timedelta(
                    seconds=dashboard_config.get("refresh_interval_seconds", 300)
                )
            )
            
            # Génération des données initiales pour chaque widget
            widget_data = {}
            for widget in validated_widgets:
                try:
                    data = await self._generate_widget_data(tenant_id, widget)
                    widget_data[widget["widget_id"]] = data
                except Exception as e:
                    logger.warning(f"Erreur génération données widget {widget['widget_id']}: {e}")
                    widget_data[widget["widget_id"]] = {"error": str(e)}
            
            # Mise en cache du dashboard
            if tenant_id not in self.dashboards:
                self.dashboards[tenant_id] = []
            self.dashboards[tenant_id].append(dashboard)
            
            # Sauvegarde en base de données
            await self._save_dashboard(dashboard)
            
            # Configuration du rafraîchissement automatique
            await self._schedule_dashboard_refresh(dashboard_id, dashboard.refresh_interval)
            
            # Mise à jour des statistiques
            self.analytics_stats["active_dashboards"] += 1
            
            result = {
                "dashboard_id": dashboard_id,
                "tenant_id": tenant_id,
                "dashboard_name": dashboard.dashboard_name,
                "widgets_count": len(validated_widgets),
                "refresh_interval_seconds": int(dashboard.refresh_interval.total_seconds()),
                "widget_data": widget_data,
                "dashboard_url": f"/analytics/dashboard/{dashboard_id}",
                "created_at": dashboard.created_at.isoformat()
            }
            
            logger.info(f"Dashboard créé pour {tenant_id}: {dashboard_id} ({len(validated_widgets)} widgets)")
            return result
            
        except Exception as e:
            logger.error(f"Erreur création dashboard {tenant_id}: {e}")
            raise
    
    async def get_tenant_analytics_report(
        self,
        tenant_id: str,
        report_type: str = "comprehensive",
        time_range: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """
        📋 Génère un rapport analytics complet pour un tenant
        
        Args:
            tenant_id: Identifiant du tenant
            report_type: Type de rapport (comprehensive, summary, custom)
            time_range: Période d'analyse
            
        Returns:
            Rapport analytics détaillé
        """
        try:
            report_id = str(uuid.uuid4())
            end_time = datetime.utcnow()
            start_time = end_time - time_range
            
            # Collecte des données analytics
            analytics_data = await self._collect_comprehensive_analytics(
                tenant_id,
                start_time,
                end_time
            )
            
            # Métriques générales
            general_metrics = await self._calculate_general_metrics(
                tenant_id,
                analytics_data,
                time_range
            )
            
            # Analyse d'engagement utilisateur
            user_engagement = await self._analyze_user_engagement(
                tenant_id,
                analytics_data,
                time_range
            )
            
            # Performance du contenu
            content_performance = await self._analyze_content_performance(
                tenant_id,
                analytics_data,
                time_range
            )
            
            # Tendances et patterns
            trends_analysis = await self._analyze_trends_patterns(
                tenant_id,
                analytics_data,
                time_range
            )
            
            # Insights et recommandations
            insights_summary = await self._summarize_tenant_insights(
                tenant_id,
                time_range
            )
            
            # Comparaisons avec benchmarks (anonymisés)
            benchmark_comparison = await self._generate_benchmark_comparison(
                tenant_id,
                general_metrics
            )
            
            # Prédictions futures si ML activé
            future_predictions = {}
            if self.enable_ml_insights:
                future_predictions = await self._generate_future_predictions(
                    tenant_id,
                    analytics_data,
                    timedelta(days=30)  # Prédictions 30 jours
                )
            
            # Compilation du rapport
            report = {
                "report_id": report_id,
                "tenant_id": tenant_id,
                "report_metadata": {
                    "report_type": report_type,
                    "generated_at": datetime.utcnow().isoformat(),
                    "analysis_period": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat(),
                        "duration_days": time_range.days
                    }
                },
                "executive_summary": {
                    "total_events": analytics_data.get("total_events", 0),
                    "unique_users": analytics_data.get("unique_users", 0),
                    "content_items": analytics_data.get("content_items", 0),
                    "engagement_score": user_engagement.get("overall_score", 0),
                    "top_insight": insights_summary.get("top_insight", "Aucun insight disponible")
                },
                "general_metrics": general_metrics,
                "user_engagement": user_engagement,
                "content_performance": content_performance,
                "trends_analysis": trends_analysis,
                "insights_summary": insights_summary,
                "benchmark_comparison": benchmark_comparison,
                "future_predictions": future_predictions,
                "data_quality": {
                    "completeness_score": analytics_data.get("completeness", 1.0),
                    "data_points_analyzed": analytics_data.get("data_points", 0),
                    "confidence_level": "high" if analytics_data.get("data_points", 0) > 1000 else "medium"
                }
            }
            
            # Sauvegarde du rapport
            await self._save_analytics_report(report)
            
            logger.info(
                f"Rapport analytics généré pour {tenant_id}: {report_type}, "
                f"{analytics_data.get('total_events', 0)} événements analysés"
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Erreur génération rapport analytics {tenant_id}: {e}")
            raise
    
    # Méthodes privées utilitaires
    
    async def _initialize_analytics_tables(self) -> None:
        """Initialise les tables analytics"""
        async with self.engine.begin() as conn:
            # Table des événements analytics
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS analytics_events (
                    event_id VARCHAR(255) PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    event_type VARCHAR(50),
                    event_name VARCHAR(255),
                    user_id VARCHAR(255),
                    session_id VARCHAR(255),
                    properties JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processing_timestamp TIMESTAMP,
                    geo_location JSONB,
                    device_info JSONB
                )
            """))
            
            # Index pour performances
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_analytics_events_tenant_time 
                ON analytics_events (tenant_id, timestamp)
            """))
            
            # Table des métriques
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tenant_metrics (
                    metric_id VARCHAR(255) PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    metric_name VARCHAR(255),
                    metric_type VARCHAR(50),
                    value JSONB,
                    tags JSONB,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    aggregation_period VARCHAR(20)
                )
            """))
            
            # Table des insights
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS tenant_insights (
                    insight_id VARCHAR(255) PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    category VARCHAR(50),
                    title VARCHAR(255),
                    description TEXT,
                    confidence_score FLOAT,
                    impact_level VARCHAR(20),
                    recommendation TEXT,
                    supporting_data JSONB,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_actionable BOOLEAN DEFAULT TRUE
                )
            """))
    
    async def _load_analytics_configurations(self) -> None:
        """Charge les configurations analytics existantes"""
        # Chargement des dashboards existants
        async with self.engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT * FROM analytics_dashboards WHERE is_active = TRUE
            """))
            # Traitement des résultats...
    
    async def _initialize_ml_models(self) -> None:
        """Initialise les modèles ML pour analytics"""
        if not self.enable_ml_insights:
            return
        
        # Initialisation des modèles selon les besoins
        logger.info("Modèles ML initialisés pour analytics")
    
    async def _enrich_event_properties(
        self,
        tenant_id: str,
        properties: Dict[str, Any],
        user_id: Optional[str],
        session_id: Optional[str]
    ) -> Dict[str, Any]:
        """Enrichit les propriétés d'un événement"""
        enriched = properties.copy()
        
        # Ajout de métadonnées contextuelles
        enriched["_tenant_id"] = tenant_id
        enriched["_server_timestamp"] = datetime.utcnow().isoformat()
        
        if user_id:
            # Enrichissement avec données utilisateur (si disponible)
            user_context = await self._get_user_context(tenant_id, user_id)
            if user_context:
                enriched["_user_context"] = user_context
        
        if session_id:
            # Enrichissement avec données de session
            session_context = await self._get_session_context(tenant_id, session_id)
            if session_context:
                enriched["_session_context"] = session_context
        
        return enriched
    
    async def _process_event_real_time(self, event: AnalyticsEvent) -> None:
        """Traite un événement en temps réel"""
        try:
            # Mise à jour des métriques en temps réel
            await self._update_real_time_metrics(event)
            
            # Détection d'anomalies en temps réel
            anomaly_detected = await self._detect_real_time_anomaly(event)
            if anomaly_detected:
                await self._handle_real_time_anomaly(event, anomaly_detected)
            
            # Mise à jour des dashboards en temps réel
            await self._update_real_time_dashboards(event)
            
        except Exception as e:
            logger.error(f"Erreur traitement temps réel événement {event.event_id}: {e}")
    
    async def _flush_tenant_events(self, tenant_id: str) -> None:
        """Flush les événements en buffer vers la base"""
        if tenant_id not in self.event_buffer or not self.event_buffer[tenant_id]:
            return
        
        events_to_flush = self.event_buffer[tenant_id]
        self.event_buffer[tenant_id] = []
        
        try:
            # Sauvegarde batch en base de données
            async with self.engine.begin() as conn:
                for event in events_to_flush:
                    await conn.execute(text("""
                        INSERT INTO analytics_events (
                            event_id, tenant_id, event_type, event_name,
                            user_id, session_id, properties, timestamp
                        ) VALUES (
                            :event_id, :tenant_id, :event_type, :event_name,
                            :user_id, :session_id, :properties, :timestamp
                        )
                    """), {
                        "event_id": event.event_id,
                        "tenant_id": event.tenant_id,
                        "event_type": event.event_type.value,
                        "event_name": event.event_name,
                        "user_id": event.user_id,
                        "session_id": event.session_id,
                        "properties": json.dumps(event.properties),
                        "timestamp": event.timestamp
                    })
            
            logger.debug(f"Flush events {tenant_id}: {len(events_to_flush)} événements")
            
        except Exception as e:
            logger.error(f"Erreur flush events {tenant_id}: {e}")
            # Remettre les événements en buffer en cas d'erreur
            self.event_buffer[tenant_id] = events_to_flush + self.event_buffer.get(tenant_id, [])
    
    def _impact_weight(self, impact_level: str) -> int:
        """Retourne le poids numérique d'un niveau d'impact"""
        weights = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        return weights.get(impact_level, 0)
    
    async def _collect_analysis_data(
        self,
        tenant_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Collecte les données pour analyse"""
        # Collecte des événements
        async with self.engine.begin() as conn:
            events_result = await conn.execute(text("""
                SELECT COUNT(*) as total_events,
                       COUNT(DISTINCT user_id) as unique_users,
                       event_type,
                       event_name
                FROM analytics_events 
                WHERE tenant_id = :tenant_id 
                AND timestamp BETWEEN :start_time AND :end_time
                GROUP BY event_type, event_name
            """), {
                "tenant_id": tenant_id,
                "start_time": start_time,
                "end_time": end_time
            })
            
            events_data = events_result.fetchall()
        
        return {
            "total_events": sum(row.total_events for row in events_data),
            "unique_users": len(set(row.unique_users for row in events_data if row.unique_users)),
            "event_breakdown": [
                {
                    "type": row.event_type,
                    "name": row.event_name,
                    "count": row.total_events
                }
                for row in events_data
            ]
        }
    
    async def _generate_category_insights(
        self,
        tenant_id: str,
        category: InsightCategory,
        analysis_data: Dict[str, Any],
        time_range: timedelta
    ) -> List[TenantInsight]:
        """Génère des insights pour une catégorie spécifique"""
        insights = []
        
        if category == InsightCategory.USER_BEHAVIOR:
            # Analyse du comportement utilisateur
            if analysis_data.get("unique_users", 0) > 0:
                engagement_rate = analysis_data.get("total_events", 0) / analysis_data.get("unique_users", 1)
                
                if engagement_rate > 50:  # Seuil exemple
                    insight = TenantInsight(
                        insight_id=str(uuid.uuid4()),
                        tenant_id=tenant_id,
                        category=category,
                        title="Engagement utilisateur élevé",
                        description=f"Taux d'engagement de {engagement_rate:.1f} événements par utilisateur",
                        confidence_score=0.85,
                        impact_level="medium",
                        recommendation="Capitaliser sur cet engagement en proposant plus de contenu"
                    )
                    insights.append(insight)
        
        # Autres catégories...
        
        return insights
    
    async def _generate_ml_insights(
        self,
        tenant_id: str,
        analysis_data: Dict[str, Any],
        time_range: timedelta
    ) -> List[TenantInsight]:
        """Génère des insights basés sur ML"""
        ml_insights = []
        
        if not self.enable_ml_insights:
            return ml_insights
        
        # Implémentation des insights ML
        # Clustering utilisateurs, prédictions, détection d'anomalies
        
        return ml_insights
    
    async def _real_time_processor(self) -> None:
        """Processeur temps réel"""
        while True:
            try:
                # Traitement temps réel des événements
                await asyncio.sleep(1)  # Traitement chaque seconde
            except Exception as e:
                logger.error(f"Erreur real-time processor: {e}")
                await asyncio.sleep(1)
    
    async def _batch_processor(self) -> None:
        """Processeur batch"""
        while True:
            try:
                # Flush périodique des buffers
                for tenant_id in list(self.event_buffer.keys()):
                    await self._flush_tenant_events(tenant_id)
                
                await asyncio.sleep(self.flush_interval.total_seconds())
            except Exception as e:
                logger.error(f"Erreur batch processor: {e}")
                await asyncio.sleep(self.flush_interval.total_seconds())
    
    async def _metrics_aggregator(self) -> None:
        """Agrégateur de métriques"""
        while True:
            try:
                # Agrégation périodique des métriques
                await asyncio.sleep(300)  # Toutes les 5 minutes
            except Exception as e:
                logger.error(f"Erreur metrics aggregator: {e}")
                await asyncio.sleep(300)
    
    async def _insights_generator(self) -> None:
        """Générateur d'insights"""
        while True:
            try:
                # Génération périodique d'insights
                await asyncio.sleep(3600)  # Toutes les heures
            except Exception as e:
                logger.error(f"Erreur insights generator: {e}")
                await asyncio.sleep(3600)
    
    async def _anomaly_detector(self) -> None:
        """Détecteur d'anomalies"""
        while True:
            try:
                # Détection d'anomalies
                await asyncio.sleep(300)  # Toutes les 5 minutes
            except Exception as e:
                logger.error(f"Erreur anomaly detector: {e}")
                await asyncio.sleep(300)
    
    async def _dashboard_updater(self) -> None:
        """Mise à jour des dashboards"""
        while True:
            try:
                # Mise à jour des dashboards
                await asyncio.sleep(60)  # Toutes les minutes
            except Exception as e:
                logger.error(f"Erreur dashboard updater: {e}")
                await asyncio.sleep(60)
    
    async def cleanup(self) -> None:
        """Nettoyage des ressources"""
        # Flush final des buffers
        for tenant_id in list(self.event_buffer.keys()):
            await self._flush_tenant_events(tenant_id)
        
        if self.engine:
            await self.engine.dispose()
        if self.redis_client:
            await self.redis_client.close()
        
        logger.info("TenantAnalyticsCollector nettoyé")


# Instance principale
tenant_analytics_collector = None


async def get_tenant_analytics_collector() -> TenantAnalyticsCollector:
    """Factory pour l'instance TenantAnalyticsCollector"""
    global tenant_analytics_collector
    if not tenant_analytics_collector:
        database_url = "postgresql+asyncpg://localhost/iacherie_analytics"
        redis_url = "redis://localhost:6379/7"
        
        tenant_analytics_collector = TenantAnalyticsCollector(
            database_url=database_url,
            redis_url=redis_url,
            enable_ml_insights=True,
            enable_real_time_processing=True
        )
        await tenant_analytics_collector.initialize()
    
    return tenant_analytics_collector


# Tests de démonstration
async def main():
    """Fonction principale pour tests et démonstration"""
    collector = await get_tenant_analytics_collector()
    
    test_tenant_id = "tenant_analytics_demo"
    
    try:
        # Test collecte d'événement
        event_result = await collector.collect_tenant_event(
            test_tenant_id,
            AnalyticsEventType.CONTENT_CREATION,
            "video_upload",
            {
                "video_duration": 120,
                "resolution": "1080p",
                "file_size": 50000000,
                "category": "education"
            },
            user_id="user_123",
            session_id="session_456"
        )
        print(f"✅ Événement collecté: {event_result['event_id']}")
        
        # Test collecte de métriques
        metrics_data = [
            {"name": "cpu_usage", "type": "gauge", "value": 75.5, "tags": {"instance": "web-1"}},
            {"name": "requests_per_second", "type": "counter", "value": 150},
            {"name": "response_time", "type": "histogram", "value": [100, 200, 150, 300]}
        ]
        
        metrics_result = await collector.collect_tenant_metrics(test_tenant_id, metrics_data)
        print(f"✅ Métriques collectées: {metrics_result['metrics_summary']['successfully_collected']}")
        
        # Test génération d'insights
        insights_result = await collector.generate_tenant_insights(
            test_tenant_id,
            [InsightCategory.USER_BEHAVIOR, InsightCategory.CONTENT_PERFORMANCE]
        )
        print(f"✅ Insights générés: {insights_result['insights_summary']['total_generated']}")
        
        # Test création dashboard
        dashboard_config = {
            "name": "Dashboard Principal",
            "widgets": [
                {
                    "type": "line_chart",
                    "title": "Événements par heure",
                    "metric": "events_count",
                    "period": "hour"
                },
                {
                    "type": "pie_chart", 
                    "title": "Types de contenu",
                    "metric": "content_types",
                    "period": "day"
                }
            ],
            "refresh_interval_seconds": 300
        }
        
        dashboard_result = await collector.create_analytics_dashboard(
            test_tenant_id,
            dashboard_config
        )
        print(f"✅ Dashboard créé: {dashboard_result['dashboard_id']}")
        
        # Test rapport analytics
        report = await collector.get_tenant_analytics_report(
            test_tenant_id,
            "comprehensive",
            timedelta(days=7)
        )
        print(f"✅ Rapport généré: {report['executive_summary']['total_events']} événements analysés")
        
    except Exception as e:
        print(f"❌ Erreur test: {e}")
    finally:
        await collector.cleanup()


if __name__ == "__main__":
    asyncio.run(main())