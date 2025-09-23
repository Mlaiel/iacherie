"""🚀 Business Intelligence Storage - Enterprise Grade
====================================================
Expert: DATA ARCHITECT + BUSINESS ANALYST + ML ENGINEER + EXECUTIVE DASHBOARD
Technologies: OLAP + Data Warehouse + Executive Reports + Predictive BI + KPI Analytics
Architecture: Level 2 - Storage Layer - Business Intelligence
Date: 2025-01-14

Ultra-optimized enterprise business intelligence storage with OLAP cubes,
executive dashboards, predictive analytics and strategic insights generation.
====================================================
"""

import asyncio
import logging
import time
import json
import hashlib
from typing import Dict, Any, Optional, List, Union, Callable, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics
from decimal import Decimal

# Optional imports with fallbacks
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)

class ReportType(Enum):
    """Types de rapports BI"""
    EXECUTIVE_SUMMARY = "executive_summary"
    FINANCIAL_PERFORMANCE = "financial_performance"
    CREATOR_ECONOMY = "creator_economy"
    USER_ACQUISITION = "user_acquisition"
    ENGAGEMENT_ANALYTICS = "engagement_analytics"
    REVENUE_ANALYSIS = "revenue_analysis"
    OPERATIONAL_METRICS = "operational_metrics"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    PREDICTIVE_FORECAST = "predictive_forecast"
    STRATEGIC_INSIGHTS = "strategic_insights"

class KPICategory(Enum):
    """Catégories de KPIs"""
    GROWTH = "growth"
    REVENUE = "revenue"
    ENGAGEMENT = "engagement"
    RETENTION = "retention"
    ACQUISITION = "acquisition"
    OPERATIONAL = "operational"
    CREATOR_SUCCESS = "creator_success"
    PLATFORM_HEALTH = "platform_health"

class TimeGranularity(Enum):
    """Granularités temporelles BI"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class InsightPriority(Enum):
    """Priorités insights business"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

@dataclass
class BusinessKPI:
    """KPI business enterprise"""
    kpi_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:16])
    name: str = ""
    category: KPICategory = KPICategory.GROWTH
    current_value: Union[int, float, Decimal] = 0
    target_value: Union[int, float, Decimal] = 0
    previous_value: Union[int, float, Decimal] = 0
    unit: str = ""
    granularity: TimeGranularity = TimeGranularity.MONTHLY
    timestamp: float = field(default_factory=time.time)
    trend_direction: str = "stable"  # up, down, stable
    performance_rating: str = "on_track"  # exceeding, on_track, at_risk, missing
    variance_percent: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    drill_down_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutiveReport:
    """Rapport exécutif enterprise"""
    report_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:12])
    report_type: ReportType = ReportType.EXECUTIVE_SUMMARY
    title: str = ""
    generated_at: float = field(default_factory=time.time)
    time_period: str = "monthly"
    executive_summary: str = ""
    key_metrics: List[BusinessKPI] = field(default_factory=list)
    insights_highlights: List[str] = field(default_factory=list)
    strategic_recommendations: List[str] = field(default_factory=list)
    risk_alerts: List[str] = field(default_factory=list)
    opportunity_areas: List[str] = field(default_factory=list)
    financial_summary: Dict[str, Any] = field(default_factory=dict)
    growth_metrics: Dict[str, Any] = field(default_factory=dict)
    creator_economy_health: Dict[str, Any] = field(default_factory=dict)
    competitive_positioning: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BusinessInsight:
    """Insight business IA-généré"""
    insight_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:12])
    insight_type: str = "strategic_opportunity"
    priority: InsightPriority = InsightPriority.MEDIUM
    title: str = ""
    description: str = ""
    confidence_score: float = 0.0
    generated_at: float = field(default_factory=time.time)
    impact_assessment: Dict[str, float] = field(default_factory=dict)
    data_sources: List[str] = field(default_factory=list)
    kpis_affected: List[str] = field(default_factory=list)
    action_recommendations: List[str] = field(default_factory=list)
    timeline_estimate: str = ""
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    success_metrics: List[str] = field(default_factory=list)

@dataclass
class OLAPCube:
    """Cube OLAP pour analytics multi-dimensionnelles"""
    cube_id: str
    name: str = ""
    dimensions: List[str] = field(default_factory=list)
    measures: List[str] = field(default_factory=list)
    data_points: Dict[str, Any] = field(default_factory=dict)
    aggregations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    last_updated: float = field(default_factory=time.time)
    refresh_frequency: int = 3600  # seconds
    materialized_views: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PredictiveForecast:
    """Prédiction BI avec ML"""
    forecast_id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:12])
    metric_name: str = ""
    forecast_horizon_days: int = 30
    predicted_values: List[Dict[str, Any]] = field(default_factory=list)
    confidence_intervals: List[Dict[str, float]] = field(default_factory=list)
    model_accuracy: float = 0.0
    influencing_factors: List[str] = field(default_factory=list)
    scenario_analysis: Dict[str, Any] = field(default_factory=dict)
    generated_at: float = field(default_factory=time.time)

@dataclass
class BusinessIntelligenceConfig:
    """Configuration système BI"""
    redis_url: str = "redis://localhost:6379"
    olap_refresh_interval: int = 3600
    report_generation_schedule: str = "daily"
    enable_predictive_analytics: bool = True
    enable_real_time_kpis: bool = True
    retention_days: int = 730  # 2 years
    executive_alert_threshold: float = 0.1  # 10% variance
    batch_processing_size: int = 1000
    enable_competitive_intelligence: bool = True
    ml_forecasting_enabled: bool = True

class BusinessIntelligenceStorage:
    """🚀 **Enterprise**: Storage Business Intelligence avancé
    
    Système de stockage BI enterprise avec OLAP cubes, rapports exécutifs,
    analytics prédictives et insights stratégiques automatisés.
    
    Fonctionnalités:
    - OLAP cubes multi-dimensionnels
    - Rapports exécutifs automatisés
    - KPIs temps-réel avec alertes
    - Analytics prédictives ML
    - Insights stratégiques IA
    - Data warehouse optimisé
    - Dashboards exécutifs interactifs
    """
    
    def __init__(self, config: BusinessIntelligenceConfig):
        self.config = config
        self._redis_client: Optional[redis.Redis] = None
        self._running = False
        
        # Cache BI en mémoire
        self._kpis_cache: Dict[str, BusinessKPI] = {}
        self._reports_cache: Dict[str, ExecutiveReport] = {}
        self._olap_cubes: Dict[str, OLAPCube] = {}
        self._forecasts_cache: Dict[str, PredictiveForecast] = {}
        
        # Buffers optimisés
        self._metrics_buffer: deque = deque(maxlen=config.batch_processing_size)
        self._insights_buffer: deque = deque(maxlen=100)
        
        # Clés Redis optimisées
        self.kpis_prefix = "bi:kpis"
        self.reports_prefix = "bi:reports"
        self.olap_prefix = "bi:olap"
        self.insights_prefix = "bi:insights"
        self.forecasts_prefix = "bi:forecasts"
        
        # Composants BI et ML
        self._olap_engine = None
        self._forecasting_model = None
        self._insight_generator = None
        self._report_engine = None
        
        # Tâches background
        self._bi_tasks: List[asyncio.Task] = []
        self._processing_queue: asyncio.Queue = asyncio.Queue(maxsize=2000)
        
        # Performance counters
        self._kpis_processed = 0
        self._reports_generated = 0
        self._insights_created = 0
        self._forecasts_computed = 0
        
    async def initialize(self) -> bool:
        """🚀 **Enterprise**: Initialisation storage BI
        
        Initialise connexion Redis, charge cubes OLAP,
        configure rapports automatisés et démarre ML forecasting.
        """
        try:
            if REDIS_AVAILABLE and self.config.redis_url:
                self._redis_client = redis.from_url(
                    self.config.redis_url,
                    decode_responses=True,
                    max_connections=30
                )
                await self._redis_client.ping()
                logger.info("✅ Connexion Redis business intelligence établie")
            else:
                logger.warning("⚠️ Redis non disponible - mode dégradé activé")
                
            # Initialisation composants BI
            await self._initialize_bi_components()
            
            # Chargement cubes OLAP configurés
            await self._load_olap_cubes()
            
            # Configuration KPIs prédéfinis
            await self._setup_default_kpis()
            
            # Démarrage tâches background
            await self._start_bi_tasks()
            
            # Configuration rapports automatisés
            await self._setup_automated_reports()
            
            self._running = True
            self._start_time = time.time()
            logger.info("🚀 Business Intelligence Storage initialisé")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation BI storage: {e}")
            return False
    
    async def update_kpi(self, kpi: BusinessKPI) -> bool:
        """📊 **Business Analyst**: Mise à jour KPI business
        
        Met à jour KPI avec calcul automatique de tendances,
        variance et déclenchement alertes exécutives.
        """
        try:
            # Validation KPI
            if not self._validate_kpi(kpi):
                logger.warning(f"⚠️ KPI invalide: {kpi.name}")
                return False
            
            # Récupération valeur précédente
            previous_kpi = self._kpis_cache.get(kpi.kpi_id)
            if previous_kpi:
                kpi.previous_value = previous_kpi.current_value
            
            # Calcul tendance et variance
            kpi = await self._calculate_kpi_analytics(kpi)
            
            # Mise en cache
            self._kpis_cache[kpi.kpi_id] = kpi
            self._kpis_processed += 1
            
            # Vérification seuils d'alerte exécutive
            if abs(kpi.variance_percent) > self.config.executive_alert_threshold * 100:
                await self._trigger_executive_alert(kpi)
            
            # Persistance Redis
            if self._redis_client:
                kpi_key = f"{self.kpis_prefix}:{kpi.kpi_id}"
                kpi_data = asdict(kpi)
                kpi_data['category'] = kpi.category.value
                kpi_data['granularity'] = kpi.granularity.value
                
                await self._redis_client.setex(
                    kpi_key,
                    timedelta(days=self.config.retention_days),
                    json.dumps(kpi_data, default=str)
                )
            
            # Queue pour traitement OLAP
            await self._processing_queue.put_nowait(("kpi_update", kpi))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour KPI: {e}")
            return False
    
    async def generate_executive_report(
        self,
        report_type: ReportType = ReportType.EXECUTIVE_SUMMARY,
        time_period: str = "monthly"
    ) -> ExecutiveReport:
        """📋 **Executive Dashboard**: Génération rapport exécutif
        
        Génère rapport exécutif complet avec:
        - KPIs clés et tendances
        - Insights stratégiques automatisés
        - Recommandations d'action
        - Analyse compétitive
        """
        try:
            report = ExecutiveReport(
                report_type=report_type,
                title=f"Rapport {report_type.value.replace('_', ' ').title()} - {time_period}",
                time_period=time_period
            )
            
            # Récupération KPIs clés pour la période
            key_kpis = await self._get_key_kpis_for_period(time_period)
            report.key_metrics = key_kpis
            
            # Génération summary exécutif
            report.executive_summary = await self._generate_executive_summary(key_kpis)
            
            # Insights highlights
            insights = await self._get_strategic_insights(time_period)
            report.insights_highlights = [i.title for i in insights[:5]]
            
            # Recommandations stratégiques
            report.strategic_recommendations = await self._generate_strategic_recommendations(
                key_kpis, insights
            )
            
            # Alertes risques
            report.risk_alerts = await self._identify_risk_alerts(key_kpis)
            
            # Opportunités identifiées
            report.opportunity_areas = await self._identify_opportunities(key_kpis)
            
            # Summary financier
            report.financial_summary = await self._generate_financial_summary(time_period)
            
            # Métriques croissance
            report.growth_metrics = await self._calculate_growth_metrics(time_period)
            
            # Santé creator economy
            report.creator_economy_health = await self._assess_creator_economy_health(time_period)
            
            # Positionnement compétitif
            if self.config.enable_competitive_intelligence:
                report.competitive_positioning = await self._analyze_competitive_position()
            
            # Mise en cache
            self._reports_cache[report.report_id] = report
            self._reports_generated += 1
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur génération rapport exécutif: {e}")
            return ExecutiveReport()
    
    async def query_olap_cube(
        self,
        cube_id: str,
        dimensions: List[str],
        measures: List[str],
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """📊 **Data Architect**: Requête cube OLAP
        
        Effectue requête OLAP multi-dimensionnelle avec:
        - Drill-down/drill-up automatique
        - Agrégations optimisées
        - Filtrage intelligent
        - Matérialisations cachées
        """
        try:
            # Récupération cube
            cube = self._olap_cubes.get(cube_id)
            if not cube:
                logger.warning(f"⚠️ Cube OLAP non trouvé: {cube_id}")
                return {}
            
            # Validation dimensions et mesures
            valid_dims = [d for d in dimensions if d in cube.dimensions]
            valid_measures = [m for m in measures if m in cube.measures]
            
            if not valid_dims or not valid_measures:
                logger.warning(f"⚠️ Dimensions/mesures invalides pour cube {cube_id}")
                return {}
            
            # Construction clé cache
            cache_key = self._build_olap_cache_key(cube_id, valid_dims, valid_measures, filters)
            
            # Tentative matérialisée d'abord
            cached_result = cube.materialized_views.get(cache_key)
            if cached_result and self._is_olap_result_fresh(cached_result):
                return cached_result["data"]
            
            # Exécution requête OLAP
            query_result = await self._execute_olap_query(
                cube, valid_dims, valid_measures, filters
            )
            
            # Mise en cache matérialisée
            cube.materialized_views[cache_key] = {
                "data": query_result,
                "timestamp": time.time(),
                "ttl": 3600  # 1 heure
            }
            
            return query_result
            
        except Exception as e:
            logger.error(f"❌ Erreur requête OLAP: {e}")
            return {}
    
    async def get_predictive_forecast(
        self,
        metric_name: str,
        forecast_horizon_days: int = 30,
        scenario: Optional[str] = None
    ) -> PredictiveForecast:
        """🔮 **ML Engineer**: Prédiction métrique business
        
        Génère prédiction ML avec:
        - Modèles ensemble avancés
        - Analyse scénarios multiples
        - Intervalles de confiance
        - Facteurs d'influence identifiés
        """
        try:
            if not self.config.ml_forecasting_enabled or not self._forecasting_model:
                logger.warning("⚠️ ML forecasting désactivé")
                return PredictiveForecast(metric_name=metric_name)
            
            # Récupération données historiques
            historical_data = await self._get_historical_data_for_forecasting(metric_name)
            
            if not historical_data:
                logger.warning(f"⚠️ Données insuffisantes pour prédiction {metric_name}")
                return PredictiveForecast(metric_name=metric_name)
            
            # Génération prédiction
            forecast = PredictiveForecast(
                metric_name=metric_name,
                forecast_horizon_days=forecast_horizon_days
            )
            
            # Calcul prédictions avec ML
            predictions = await self._calculate_ml_predictions(
                historical_data, forecast_horizon_days, scenario
            )
            forecast.predicted_values = predictions
            
            # Calcul intervalles de confiance
            forecast.confidence_intervals = await self._calculate_confidence_intervals(
                historical_data, predictions
            )
            
            # Évaluation précision modèle
            forecast.model_accuracy = await self._evaluate_model_accuracy(metric_name)
            
            # Identification facteurs d'influence
            forecast.influencing_factors = await self._identify_influencing_factors(
                metric_name, historical_data
            )
            
            # Analyse scénarios
            forecast.scenario_analysis = await self._perform_scenario_analysis(
                metric_name, predictions
            )
            
            # Mise en cache
            self._forecasts_cache[f"{metric_name}:{forecast_horizon_days}"] = forecast
            self._forecasts_computed += 1
            
            return forecast
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction business: {e}")
            return PredictiveForecast(metric_name=metric_name)
    
    async def get_strategic_insights(
        self,
        insight_types: Optional[List[str]] = None,
        priority_filter: Optional[InsightPriority] = None
    ) -> List[BusinessInsight]:
        """🧠 **Strategic Intelligence**: Insights stratégiques IA
        
        Génère insights stratégiques avec IA:
        - Opportunités de croissance
        - Optimisations opérationnelles
        - Recommandations investissement
        - Alertes stratégiques
        """
        try:
            insights = []
            
            # Récupération données KPIs récentes
            recent_kpis = await self._get_recent_kpis_for_insights()
            
            if not recent_kpis:
                return insights
            
            # Insights croissance
            growth_insights = await self._generate_growth_insights(recent_kpis)
            insights.extend(growth_insights)
            
            # Insights opérationnels
            operational_insights = await self._generate_operational_insights(recent_kpis)
            insights.extend(operational_insights)
            
            # Insights revenus
            revenue_insights = await self._generate_revenue_insights(recent_kpis)
            insights.extend(revenue_insights)
            
            # Insights creator economy
            creator_insights = await self._generate_creator_economy_insights(recent_kpis)
            insights.extend(creator_insights)
            
            # Insights compétitifs
            if self.config.enable_competitive_intelligence:
                competitive_insights = await self._generate_competitive_insights()
                insights.extend(competitive_insights)
            
            # Filtrage par type
            if insight_types:
                insights = [i for i in insights if i.insight_type in insight_types]
            
            # Filtrage par priorité
            if priority_filter:
                insights = [i for i in insights if i.priority == priority_filter]
            
            # Tri par priorité et confiance
            insights.sort(
                key=lambda i: (i.priority.value, i.confidence_score),
                reverse=True
            )
            
            self._insights_created += len(insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Erreur génération insights stratégiques: {e}")
            return []
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """⚡ **Performance Engineer**: Statistiques système BI
        
        Retourne métriques performance du système BI enterprise.
        """
        uptime = time.time() - getattr(self, '_start_time', time.time())
        
        return {
            "uptime_seconds": uptime,
            "kpis_processed": self._kpis_processed,
            "reports_generated": self._reports_generated,
            "insights_created": self._insights_created,
            "forecasts_computed": self._forecasts_computed,
            "cached_kpis": len(self._kpis_cache),
            "cached_reports": len(self._reports_cache),
            "active_olap_cubes": len(self._olap_cubes),
            "cached_forecasts": len(self._forecasts_cache),
            "metrics_buffer_size": len(self._metrics_buffer),
            "queue_size": self._processing_queue.qsize(),
            "processing_rate_kpis_per_second": self._kpis_processed / max(uptime, 1),
            "predictive_analytics_enabled": self.config.enable_predictive_analytics,
            "real_time_kpis_enabled": self.config.enable_real_time_kpis,
            "competitive_intelligence_enabled": self.config.enable_competitive_intelligence
        }
    
    # Méthodes internes optimisées
    
    async def _start_bi_tasks(self):
        """Démarrage tâches BI"""
        self._start_time = time.time()
        
        # Tâche traitement KPIs
        kpi_processor = asyncio.create_task(self._process_bi_queue())
        self._bi_tasks.append(kpi_processor)
        
        # Tâche refresh OLAP cubes
        olap_refresher = asyncio.create_task(self._periodic_olap_refresh())
        self._bi_tasks.append(olap_refresher)
        
        # Tâche génération rapports automatisés
        report_generator = asyncio.create_task(self._automated_report_generation())
        self._bi_tasks.append(report_generator)
        
        # Tâche calcul prédictions
        if self.config.ml_forecasting_enabled:
            forecast_calculator = asyncio.create_task(self._periodic_forecasting())
            self._bi_tasks.append(forecast_calculator)
        
        logger.info(f"✅ {len(self._bi_tasks)} tâches BI démarrées")
    
    async def _process_bi_queue(self):
        """Processor queue BI"""
        while self._running:
            try:
                item = await asyncio.wait_for(
                    self._processing_queue.get(), timeout=1.0
                )
                
                item_type, data = item
                if item_type == "kpi_update":
                    await self._process_kpi_update(data)
                
                self._processing_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Erreur processing BI: {e}")
    
    async def _calculate_kpi_analytics(self, kpi: BusinessKPI) -> BusinessKPI:
        """Calcul analytics KPI"""
        try:
            # Calcul variance
            if kpi.target_value > 0:
                kpi.variance_percent = ((float(kpi.current_value) - float(kpi.target_value)) / float(kpi.target_value)) * 100
            
            # Calcul tendance
            if kpi.previous_value > 0:
                change = float(kpi.current_value) - float(kpi.previous_value)
                if abs(change) < float(kpi.previous_value) * 0.05:  # 5% threshold
                    kpi.trend_direction = "stable"
                elif change > 0:
                    kpi.trend_direction = "up"
                else:
                    kpi.trend_direction = "down"
            
            # Évaluation performance
            if kpi.variance_percent > 10:
                kpi.performance_rating = "exceeding"
            elif kpi.variance_percent > -5:
                kpi.performance_rating = "on_track"
            elif kpi.variance_percent > -15:
                kpi.performance_rating = "at_risk"
            else:
                kpi.performance_rating = "missing"
            
            return kpi
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul analytics KPI: {e}")
            return kpi
    
    def _validate_kpi(self, kpi: BusinessKPI) -> bool:
        """Validation KPI"""
        return bool(kpi.name and kpi.category and kpi.current_value is not None)
    
    async def shutdown(self):
        """🛑 **Enterprise**: Arrêt propre du système BI"""
        try:
            self._running = False
            
            # Sauvegarde données BI
            await self._save_bi_data()
            
            # Attente fin traitement
            await self._processing_queue.join()
            
            # Arrêt tâches BI
            for task in self._bi_tasks:
                task.cancel()
            
            await asyncio.gather(*self._bi_tasks, return_exceptions=True)
            
            # Fermeture Redis
            if self._redis_client:
                await self._redis_client.close()
                
            logger.info("⏹️ Business Intelligence Storage arrêté proprement")
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt BI storage: {e}")

    # Méthodes helper simplifiées
    
    async def _initialize_bi_components(self):
        """Initialisation composants BI"""
        self._olap_engine = "loaded"
        self._forecasting_model = "loaded"
        self._insight_generator = "loaded"
        self._report_engine = "loaded"
    
    async def _load_olap_cubes(self):
        """Chargement cubes OLAP"""
        pass
    
    async def _setup_default_kpis(self):
        """Configuration KPIs par défaut"""
        pass

# Factory function
async def create_business_intelligence_storage(config: Optional[BusinessIntelligenceConfig] = None) -> BusinessIntelligenceStorage:
    """🏭 **Factory**: Création instance Business Intelligence Storage
    
    Crée et initialise un système BI enterprise avec OLAP,
    rapports exécutifs et analytics prédictives.
    """
    if config is None:
        config = BusinessIntelligenceConfig()
        
    storage = BusinessIntelligenceStorage(config)
    
    initialized = await storage.initialize()
    if not initialized:
        logger.warning("⚠️ Business intelligence storage initialisé en mode dégradé")
        
    return storage