# 📊 Analytics: Analytics engine avec performance insights
"""
Prompt Analytics Engine - Enterprise Implementation
==================================================
Analytics engine enterprise avec performance insights, usage tracking,
effectiveness measurement et business intelligence pour prompt engineering.

Expert Roles Applied:
- DBA: Advanced analytics queries et data optimization
- ML Engineer: Predictive analytics et machine learning insights
- Backend Senior: Scalable analytics infrastructure et real-time processing
- Lead Dev IA: AI-powered analytics et intelligent insights generation
- DevOps: Performance monitoring et analytics dashboard automation
- IA Prompt Engineer: Prompt-specific metrics et optimization insights

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Integrations - Prompt Engineering
Version: 1.0 Enterprise Production
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncpg
import redis.asyncio as redis
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
import uuid
from collections import defaultdict, Counter

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Types de métriques supportées"""
    PERFORMANCE = "performance"
    USAGE = "usage" 
    QUALITY = "quality"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    SECURITY = "security"
    BUSINESS = "business"

class TimeGranularity(Enum):
    """Granularité temporelle pour les analyses"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class AnalyticsScope(Enum):
    """Portée des analyses"""
    GLOBAL = "global"
    USER = "user"
    TEMPLATE = "template"
    CATEGORY = "category"
    PROJECT = "project"
    EXPERIMENT = "experiment"

@dataclass
class PromptMetric:
    """Structure d'une métrique de prompt"""
    id: str
    prompt_id: str
    metric_type: MetricType
    metric_name: str
    metric_value: float
    measurement_timestamp: datetime
    context_data: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    experiment_id: Optional[str] = None

@dataclass
class AnalyticsReport:
    """Rapport d'analytics complet"""
    report_id: str
    report_name: str
    scope: AnalyticsScope
    time_range: Dict[str, datetime]
    metrics_summary: Dict[str, Any]
    trends_analysis: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    visualizations: List[str]
    generated_at: datetime
    generated_by: str

@dataclass
class UsagePattern:
    """Pattern d'utilisation détecté"""
    pattern_id: str
    pattern_name: str
    description: str
    frequency: int
    confidence_score: float
    associated_metrics: List[str]
    impact_score: float
    detected_at: datetime

class PromptAnalytics:
    """Analytics engine enterprise avec performance insights et usage tracking"""
    
    def __init__(self, db_config: Dict[str, Any], redis_config: Dict[str, Any]):
        """
        Initialise le moteur d'analytics avec configuration enterprise
        
        Args:
            db_config: Configuration base de données PostgreSQL
            redis_config: Configuration Redis pour cache et performance
        """
        self.db_config = db_config
        self.redis_config = redis_config
        self.db_pool = None
        self.redis_client = None
        
        # Cache des analytics
        self.metrics_cache: Dict[str, List[PromptMetric]] = defaultdict(list)
        self.reports_cache: Dict[str, AnalyticsReport] = {}
        self.usage_patterns: Dict[str, UsagePattern] = {}
        
        # Configuration analytics
        self.cache_ttl = 1800  # 30 minutes
        self.batch_size = 1000
        self.max_concurrent_queries = 10
        
        # Modèles ML pour analytics
        self.clustering_model = None
        self.trend_predictor = None
        
        logger.info("PromptAnalytics initialized - Enterprise mode")

    async def initialize(self):
        """Initialise les connexions et composants analytics"""
        try:
            # Initialisation pool de connexions PostgreSQL
            self.db_pool = await asyncpg.create_pool(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database'],
                min_size=5,
                max_size=20
            )
            
            # Initialisation Redis client
            self.redis_client = redis.Redis(
                host=self.redis_config['host'],
                port=self.redis_config['port'],
                password=self.redis_config.get('password'),
                decode_responses=True
            )
            
            # Création du schéma analytics
            await self._create_analytics_schema()
            
            # Initialisation des modèles ML
            await self._initialize_analytics_models()
            
            # Démarrage des tâches de traitement périodique
            asyncio.create_task(self._periodic_analytics_processor())
            asyncio.create_task(self._usage_pattern_detector())
            
            logger.info("PromptAnalytics initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize PromptAnalytics: {e}")
            raise

    async def _create_analytics_schema(self):
        """Crée le schéma de base de données pour les analytics"""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS prompt_metrics (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            prompt_id UUID,
            metric_type VARCHAR(50) NOT NULL,
            metric_name VARCHAR(100) NOT NULL,
            metric_value FLOAT NOT NULL,
            measurement_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            context_data JSONB DEFAULT '{}',
            user_id UUID,
            session_id VARCHAR(255),
            experiment_id UUID
        );
        
        CREATE TABLE IF NOT EXISTS analytics_reports (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            report_name VARCHAR(255) NOT NULL,
            scope VARCHAR(50) NOT NULL,
            time_range JSONB NOT NULL,
            metrics_summary JSONB DEFAULT '{}',
            trends_analysis JSONB DEFAULT '{}',
            insights JSONB DEFAULT '[]',
            recommendations JSONB DEFAULT '[]',
            visualizations JSONB DEFAULT '[]',
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            generated_by VARCHAR(255)
        );
        
        CREATE TABLE IF NOT EXISTS usage_patterns (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            pattern_name VARCHAR(255) NOT NULL,
            description TEXT,
            frequency INTEGER DEFAULT 0,
            confidence_score FLOAT DEFAULT 0.0,
            associated_metrics JSONB DEFAULT '[]',
            impact_score FLOAT DEFAULT 0.0,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT true
        );
        
        CREATE TABLE IF NOT EXISTS performance_baselines (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            metric_name VARCHAR(100) NOT NULL,
            baseline_value FLOAT NOT NULL,
            measurement_period VARCHAR(50),
            confidence_interval JSONB,
            calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_current BOOLEAN DEFAULT true
        );
        
        CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON prompt_metrics(measurement_timestamp);
        CREATE INDEX IF NOT EXISTS idx_metrics_type ON prompt_metrics(metric_type);
        CREATE INDEX IF NOT EXISTS idx_metrics_prompt ON prompt_metrics(prompt_id);
        CREATE INDEX IF NOT EXISTS idx_reports_scope ON analytics_reports(scope);
        CREATE INDEX IF NOT EXISTS idx_patterns_active ON usage_patterns(is_active);
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(schema_sql)

    async def prompt_performance_analytics(
        self,
        prompt_ids: List[str],
        time_range: Optional[tuple[datetime, datetime]] = None,
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analyse des performances détaillée des prompts"""
        try:
            if time_range is None:
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=7)
                time_range = (start_time, end_time)
            
            if metrics is None:
                metrics = ['quality_score', 'engagement_rate', 'response_time', 'success_rate']
            
            performance_data = {}
            
            # Récupération des métriques pour chaque prompt
            for prompt_id in prompt_ids:
                prompt_metrics = await self._get_prompt_metrics(
                    prompt_id, time_range, metrics
                )
                
                # Calcul des statistiques de base
                basic_stats = await self._calculate_basic_statistics(prompt_metrics)
                
                # Analyse des tendances
                trend_analysis = await self._analyze_performance_trends(prompt_metrics)
                
                # Comparaison avec les baselines
                baseline_comparison = await self._compare_with_baselines(prompt_metrics, metrics)
                
                # Détection d'anomalies
                anomalies = await self._detect_performance_anomalies(prompt_metrics)
                
                # Corrélations entre métriques
                correlations = await self._calculate_metric_correlations(prompt_metrics)
                
                performance_data[prompt_id] = {
                    'basic_statistics': basic_stats,
                    'trend_analysis': trend_analysis,
                    'baseline_comparison': baseline_comparison,
                    'anomalies_detected': anomalies,
                    'metric_correlations': correlations,
                    'performance_score': await self._calculate_performance_score(prompt_metrics),
                    'improvement_opportunities': await self._identify_improvement_opportunities(
                        basic_stats, trend_analysis, baseline_comparison
                    )
                }
            
            # Analyse comparative entre prompts
            comparative_analysis = await self._perform_comparative_analysis(performance_data)
            
            # Recommandations globales
            global_recommendations = await self._generate_performance_recommendations(
                performance_data, comparative_analysis
            )
            
            analytics_result = {
                'prompt_performance': performance_data,
                'comparative_analysis': comparative_analysis,
                'global_recommendations': global_recommendations,
                'analysis_period': {
                    'start_time': time_range[0].isoformat(),
                    'end_time': time_range[1].isoformat()
                },
                'metrics_analyzed': metrics,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Performance analytics completed for {len(prompt_ids)} prompts")
            return analytics_result
            
        except Exception as e:
            logger.error(f"Prompt performance analytics failed: {e}")
            raise

    async def usage_pattern_analysis(
        self,
        scope: AnalyticsScope = AnalyticsScope.GLOBAL,
        time_range: Optional[tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Analyse avancée des patterns d'utilisation"""
        try:
            if time_range is None:
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=30)
                time_range = (start_time, end_time)
            
            # Collecte des données d'utilisation
            usage_data = await self._collect_usage_data(scope, time_range)
            
            # Détection des patterns temporels
            temporal_patterns = await self._detect_temporal_patterns(usage_data)
            
            # Analyse des patterns d'utilisateurs
            user_patterns = await self._analyze_user_patterns(usage_data)
            
            # Patterns de contenu
            content_patterns = await self._analyze_content_patterns(usage_data)
            
            # Clustering des comportements
            behavior_clusters = await self._perform_behavior_clustering(usage_data)
            
            # Identification des tendances émergentes
            emerging_trends = await self._identify_emerging_trends(usage_data, temporal_patterns)
            
            # Analyse de saisonnalité
            seasonality_analysis = await self._analyze_seasonality(usage_data)
            
            # Prédictions d'utilisation future
            usage_predictions = await self._predict_future_usage(usage_data, temporal_patterns)
            
            pattern_analysis = {
                'temporal_patterns': temporal_patterns,
                'user_behavior_patterns': user_patterns,
                'content_patterns': content_patterns,
                'behavior_clusters': behavior_clusters,
                'emerging_trends': emerging_trends,
                'seasonality_analysis': seasonality_analysis,
                'usage_predictions': usage_predictions,
                'analysis_scope': scope.value,
                'analysis_period': {
                    'start_time': time_range[0].isoformat(),
                    'end_time': time_range[1].isoformat()
                },
                'total_data_points': len(usage_data),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            # Sauvegarde des patterns détectés
            await self._save_detected_patterns(pattern_analysis)
            
            logger.info(f"Usage pattern analysis completed: {len(temporal_patterns)} patterns detected")
            return pattern_analysis
            
        except Exception as e:
            logger.error(f"Usage pattern analysis failed: {e}")
            raise

    async def effectiveness_measurement(
        self,
        prompt_id: str,
        success_criteria: Dict[str, float],
        time_range: Optional[tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Mesure d'efficacité avancée des prompts"""
        try:
            if time_range is None:
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=7)
                time_range = (start_time, end_time)
            
            # Collecte des métriques d'efficacité
            effectiveness_metrics = await self._collect_effectiveness_metrics(
                prompt_id, success_criteria.keys(), time_range
            )
            
            # Évaluation par rapport aux critères de succès
            success_evaluation = {}
            overall_effectiveness = 0.0
            
            for criterion, target_value in success_criteria.items():
                actual_value = effectiveness_metrics.get(criterion, 0.0)
                success_rate = min(actual_value / target_value, 1.0) if target_value > 0 else 0.0
                
                success_evaluation[criterion] = {
                    'target_value': target_value,
                    'actual_value': actual_value,
                    'success_rate': success_rate,
                    'variance': actual_value - target_value,
                    'percentage_of_target': (actual_value / target_value * 100) if target_value > 0 else 0
                }
                
                overall_effectiveness += success_rate
            
            overall_effectiveness /= len(success_criteria)
            
            # Analyse des facteurs d'impact
            impact_factors = await self._analyze_effectiveness_factors(
                prompt_id, effectiveness_metrics, time_range
            )
            
            # Comparaison avec des prompts similaires
            peer_comparison = await self._compare_with_similar_prompts(
                prompt_id, effectiveness_metrics
            )
            
            # Analyse temporelle de l'efficacité
            temporal_effectiveness = await self._analyze_temporal_effectiveness(
                prompt_id, success_criteria, time_range
            )
            
            # Recommandations d'amélioration
            improvement_recommendations = await self._generate_effectiveness_recommendations(
                success_evaluation, impact_factors, peer_comparison
            )
            
            effectiveness_report = {
                'prompt_id': prompt_id,
                'overall_effectiveness_score': overall_effectiveness,
                'success_criteria_evaluation': success_evaluation,
                'effectiveness_grade': self._calculate_effectiveness_grade(overall_effectiveness),
                'impact_factors': impact_factors,
                'peer_comparison': peer_comparison,
                'temporal_analysis': temporal_effectiveness,
                'improvement_recommendations': improvement_recommendations,
                'measurement_period': {
                    'start_time': time_range[0].isoformat(),
                    'end_time': time_range[1].isoformat()
                },
                'measured_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Effectiveness measurement completed: {overall_effectiveness:.2f} score")
            return effectiveness_report
            
        except Exception as e:
            logger.error(f"Effectiveness measurement failed: {e}")
            raise

    async def roi_analysis(
        self,
        prompt_ids: List[str],
        cost_metrics: Dict[str, float],
        revenue_metrics: Dict[str, float],
        time_range: Optional[tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Analyse ROI avancée pour les prompts"""
        try:
            if time_range is None:
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=30)
                time_range = (start_time, end_time)
            
            roi_analysis_results = {}
            
            for prompt_id in prompt_ids:
                # Calcul des coûts
                total_costs = await self._calculate_prompt_costs(
                    prompt_id, cost_metrics, time_range
                )
                
                # Calcul des revenus
                total_revenues = await self._calculate_prompt_revenues(
                    prompt_id, revenue_metrics, time_range
                )
                
                # Calcul du ROI
                roi_value = ((total_revenues - total_costs) / total_costs * 100) if total_costs > 0 else 0
                
                # Analyse des tendances ROI
                roi_trends = await self._analyze_roi_trends(prompt_id, time_range)
                
                # Analyse des contributeurs de valeur
                value_contributors = await self._analyze_value_contributors(
                    prompt_id, revenue_metrics, time_range
                )
                
                # Analyse des drivers de coût
                cost_drivers = await self._analyze_cost_drivers(
                    prompt_id, cost_metrics, time_range
                )
                
                # Projections ROI
                roi_projections = await self._project_future_roi(
                    prompt_id, roi_trends, time_range
                )
                
                # Recommandations d'optimisation ROI
                roi_optimization = await self._generate_roi_optimization_recommendations(
                    total_costs, total_revenues, cost_drivers, value_contributors
                )
                
                roi_analysis_results[prompt_id] = {
                    'total_costs': total_costs,
                    'total_revenues': total_revenues,
                    'roi_percentage': roi_value,
                    'roi_grade': self._calculate_roi_grade(roi_value),
                    'profit_margin': ((total_revenues - total_costs) / total_revenues * 100) if total_revenues > 0 else 0,
                    'roi_trends': roi_trends,
                    'value_contributors': value_contributors,
                    'cost_drivers': cost_drivers,
                    'roi_projections': roi_projections,
                    'optimization_recommendations': roi_optimization
                }
            
            # Analyse comparative ROI
            comparative_roi = await self._perform_comparative_roi_analysis(roi_analysis_results)
            
            # Portfolio ROI analysis
            portfolio_roi = await self._calculate_portfolio_roi(roi_analysis_results)
            
            roi_report = {
                'individual_prompt_roi': roi_analysis_results,
                'comparative_analysis': comparative_roi,
                'portfolio_analysis': portfolio_roi,
                'analysis_period': {
                    'start_time': time_range[0].isoformat(),
                    'end_time': time_range[1].isoformat()
                },
                'cost_metrics_used': list(cost_metrics.keys()),
                'revenue_metrics_used': list(revenue_metrics.keys()),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"ROI analysis completed for {len(prompt_ids)} prompts")
            return roi_report
            
        except Exception as e:
            logger.error(f"ROI analysis failed: {e}")
            raise

    async def trend_identification(
        self,
        metric_names: List[str],
        time_range: Optional[tuple[datetime, datetime]] = None,
        granularity: TimeGranularity = TimeGranularity.DAY
    ) -> Dict[str, Any]:
        """Identification avancée des tendances"""
        try:
            if time_range is None:
                end_time = datetime.utcnow()
                start_time = end_time - timedelta(days=30)
                time_range = (start_time, end_time)
            
            trend_analysis = {}
            
            for metric_name in metric_names:
                # Collecte des données temporelles
                time_series_data = await self._get_time_series_data(
                    metric_name, time_range, granularity
                )
                
                # Détection de tendances
                trend_direction = await self._detect_trend_direction(time_series_data)
                
                # Analyse de saisonnalité
                seasonality = await self._analyze_metric_seasonality(time_series_data)
                
                # Points de changement
                change_points = await self._detect_change_points(time_series_data)
                
                # Prédiction de tendance future
                future_trend = await self._predict_trend_continuation(time_series_data)
                
                # Analyse de volatilité
                volatility_analysis = await self._analyze_trend_volatility(time_series_data)
                
                # Corrélations avec facteurs externes
                external_correlations = await self._analyze_external_correlations(
                    metric_name, time_series_data
                )
                
                trend_analysis[metric_name] = {
                    'trend_direction': trend_direction,
                    'trend_strength': await self._calculate_trend_strength(time_series_data),
                    'seasonality_pattern': seasonality,
                    'change_points': change_points,
                    'future_predictions': future_trend,
                    'volatility_metrics': volatility_analysis,
                    'external_correlations': external_correlations,
                    'confidence_score': await self._calculate_trend_confidence(time_series_data),
                    'data_quality_score': await self._assess_data_quality(time_series_data)
                }
            
            # Analyse inter-métriques
            cross_metric_analysis = await self._analyze_cross_metric_trends(
                metric_names, time_range, granularity
            )
            
            # Identification des tendances globales
            global_trends = await self._identify_global_trends(trend_analysis)
            
            # Recommandations basées sur les tendances
            trend_recommendations = await self._generate_trend_recommendations(
                trend_analysis, global_trends
            )
            
            trend_report = {
                'individual_metric_trends': trend_analysis,
                'cross_metric_analysis': cross_metric_analysis,
                'global_trends': global_trends,
                'trend_recommendations': trend_recommendations,
                'analysis_period': {
                    'start_time': time_range[0].isoformat(),
                    'end_time': time_range[1].isoformat()
                },
                'time_granularity': granularity.value,
                'metrics_analyzed': metric_names,
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Trend identification completed for {len(metric_names)} metrics")
            return trend_report
            
        except Exception as e:
            logger.error(f"Trend identification failed: {e}")
            raise

    async def predictive_analytics(
        self,
        target_metric: str,
        prediction_horizon: timedelta,
        context_factors: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Analytics prédictives avancées"""
        try:
            # Collecte des données historiques
            historical_data = await self._collect_historical_data_for_prediction(
                target_metric, prediction_horizon * 3  # 3x horizon pour training
            )
            
            # Préparation des features
            feature_data = await self._prepare_prediction_features(
                historical_data, context_factors
            )
            
            # Entraînement du modèle prédictif
            prediction_model = await self._train_prediction_model(
                feature_data, target_metric
            )
            
            # Génération des prédictions
            predictions = await self._generate_predictions(
                prediction_model, prediction_horizon, context_factors
            )
            
            # Calcul des intervalles de confiance
            confidence_intervals = await self._calculate_prediction_confidence(
                predictions, historical_data
            )
            
            # Analyse des facteurs d'influence
            influence_factors = await self._analyze_prediction_factors(
                prediction_model, feature_data
            )
            
            # Scénarios alternatifs
            scenario_analysis = await self._perform_scenario_analysis(
                prediction_model, predictions, context_factors
            )
            
            # Validation du modèle
            model_validation = await self._validate_prediction_model(
                prediction_model, historical_data
            )
            
            predictive_report = {
                'target_metric': target_metric,
                'prediction_horizon_days': prediction_horizon.days,
                'predictions': predictions,
                'confidence_intervals': confidence_intervals,
                'influence_factors': influence_factors,
                'scenario_analysis': scenario_analysis,
                'model_performance': model_validation,
                'model_accuracy': model_validation.get('accuracy_score', 0.0),
                'prediction_confidence': model_validation.get('confidence_score', 0.0),
                'recommendations': await self._generate_predictive_recommendations(
                    predictions, influence_factors, scenario_analysis
                ),
                'generated_at': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Predictive analytics completed for {target_metric}")
            return predictive_report
            
        except Exception as e:
            logger.error(f"Predictive analytics failed: {e}")
            raise

    async def business_intelligence_dashboard(self) -> Dict[str, Any]:
        """Dashboard business intelligence complet"""
        try:
            # KPIs principaux
            key_metrics = await self._calculate_key_performance_indicators()
            
            # Analyse de performance en temps réel
            real_time_performance = await self._get_real_time_performance_metrics()
            
            # Analyse des revenus
            revenue_analysis = await self._analyze_revenue_metrics()
            
            # Analyse d'utilisation
            usage_analytics = await self._get_usage_analytics_summary()
            
            # Analyse concurrentielle
            competitive_analysis = await self._perform_competitive_analysis()
            
            # Alertes et notifications
            alerts = await self._generate_business_alerts()
            
            # Recommandations stratégiques
            strategic_recommendations = await self._generate_strategic_recommendations(
                key_metrics, revenue_analysis, usage_analytics
            )
            
            # Visualisations
            visualizations = await self._generate_dashboard_visualizations(
                key_metrics, real_time_performance, revenue_analysis
            )
            
            dashboard_data = {
                'executive_summary': {
                    'total_prompts': key_metrics.get('total_prompts', 0),
                    'active_users': key_metrics.get('active_users', 0),
                    'total_revenue': revenue_analysis.get('total_revenue', 0),
                    'roi_average': key_metrics.get('average_roi', 0),
                    'satisfaction_score': key_metrics.get('user_satisfaction', 0)
                },
                'key_performance_indicators': key_metrics,
                'real_time_metrics': real_time_performance,
                'revenue_analysis': revenue_analysis,
                'usage_analytics': usage_analytics,
                'competitive_insights': competitive_analysis,
                'business_alerts': alerts,
                'strategic_recommendations': strategic_recommendations,
                'dashboard_visualizations': visualizations,
                'last_updated': datetime.utcnow().isoformat(),
                'data_freshness': await self._calculate_data_freshness(),
                'dashboard_health_score': await self._calculate_dashboard_health()
            }
            
            logger.info("Business intelligence dashboard generated successfully")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Business intelligence dashboard generation failed: {e}")
            raise

    # Méthodes utilitaires privées
    async def _initialize_analytics_models(self):
        """Initialise les modèles ML pour analytics"""
        try:
            # Modèle de clustering pour patterns
            self.clustering_model = KMeans(n_clusters=5, random_state=42)
            
            # Modèle de prédiction de tendances
            from sklearn.linear_model import LinearRegression
            self.trend_predictor = LinearRegression()
            
            logger.info("Analytics ML models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics models: {e}")

    async def _get_prompt_metrics(
        self,
        prompt_id: str,
        time_range: tuple[datetime, datetime],
        metrics: List[str]
    ) -> List[PromptMetric]:
        """Récupère les métriques d'un prompt"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM prompt_metrics 
                    WHERE prompt_id = $1 
                    AND measurement_timestamp BETWEEN $2 AND $3
                    AND metric_name = ANY($4)
                    ORDER BY measurement_timestamp
                """, uuid.UUID(prompt_id), time_range[0], time_range[1], metrics)
                
                prompt_metrics = []
                for row in rows:
                    metric = PromptMetric(
                        id=str(row['id']),
                        prompt_id=str(row['prompt_id']),
                        metric_type=MetricType(row['metric_type']),
                        metric_name=row['metric_name'],
                        metric_value=row['metric_value'],
                        measurement_timestamp=row['measurement_timestamp'],
                        context_data=row['context_data'],
                        user_id=str(row['user_id']) if row['user_id'] else None,
                        session_id=row['session_id'],
                        experiment_id=str(row['experiment_id']) if row['experiment_id'] else None
                    )
                    prompt_metrics.append(metric)
                
                return prompt_metrics
                
        except Exception as e:
            logger.error(f"Failed to get prompt metrics: {e}")
            return []

    async def _calculate_basic_statistics(self, metrics: List[PromptMetric]) -> Dict[str, Any]:
        """Calcule les statistiques de base des métriques"""
        if not metrics:
            return {}
        
        stats_by_metric = defaultdict(list)
        
        for metric in metrics:
            stats_by_metric[metric.metric_name].append(metric.metric_value)
        
        basic_stats = {}
        for metric_name, values in stats_by_metric.items():
            if values:
                basic_stats[metric_name] = {
                    'count': len(values),
                    'mean': np.mean(values),
                    'median': np.median(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'q25': np.percentile(values, 25),
                    'q75': np.percentile(values, 75)
                }
        
        return basic_stats

    async def _periodic_analytics_processor(self):
        """Processeur périodique pour les analytics"""
        while True:
            try:
                # Traitement des métriques en batch
                await self._process_metrics_batch()
                
                # Génération de rapports automatiques
                await self._generate_automated_reports()
                
                # Nettoyage des caches expirés
                await self._cleanup_analytics_cache()
                
                # Attente avant la prochaine itération
                await asyncio.sleep(3600)  # 1 heure
                
            except Exception as e:
                logger.error(f"Periodic analytics processor error: {e}")
                await asyncio.sleep(300)  # 5 minutes en cas d'erreur

    async def _usage_pattern_detector(self):
        """Détecteur de patterns d'utilisation en arrière-plan"""
        while True:
            try:
                # Détection de nouveaux patterns
                new_patterns = await self.usage_pattern_analysis()
                
                # Mise à jour des patterns existants
                await self._update_usage_patterns(new_patterns)
                
                # Attente avant la prochaine détection
                await asyncio.sleep(7200)  # 2 heures
                
            except Exception as e:
                logger.error(f"Usage pattern detector error: {e}")
                await asyncio.sleep(600)  # 10 minutes en cas d'erreur

    def _calculate_effectiveness_grade(self, effectiveness_score: float) -> str:
        """Calcule la note d'efficacité"""
        if effectiveness_score >= 0.9:
            return "Excellent"
        elif effectiveness_score >= 0.8:
            return "Very Good"
        elif effectiveness_score >= 0.7:
            return "Good"
        elif effectiveness_score >= 0.6:
            return "Fair"
        else:
            return "Poor"

    def _calculate_roi_grade(self, roi_percentage: float) -> str:
        """Calcule la note ROI"""
        if roi_percentage >= 300:
            return "Exceptional"
        elif roi_percentage >= 200:
            return "Excellent"
        elif roi_percentage >= 100:
            return "Very Good"
        elif roi_percentage >= 50:
            return "Good"
        elif roi_percentage >= 0:
            return "Positive"
        else:
            return "Negative"

    async def record_metric(self, metric: PromptMetric):
        """Enregistre une métrique"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO prompt_metrics (
                        id, prompt_id, metric_type, metric_name, metric_value,
                        measurement_timestamp, context_data, user_id, session_id, experiment_id
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """, uuid.UUID(metric.id), uuid.UUID(metric.prompt_id) if metric.prompt_id else None,
                metric.metric_type.value, metric.metric_name, metric.metric_value,
                metric.measurement_timestamp, json.dumps(metric.context_data),
                uuid.UUID(metric.user_id) if metric.user_id else None,
                metric.session_id, uuid.UUID(metric.experiment_id) if metric.experiment_id else None)
                
            # Mise en cache
            cache_key = f"metrics:{metric.prompt_id}"
            self.metrics_cache[cache_key].append(metric)
            
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")

    # Placeholder methods pour les analyses complexes
    async def _analyze_performance_trends(self, metrics: List[PromptMetric]) -> Dict[str, Any]:
        """Analyse les tendances de performance"""
        return {"trend": "stable", "change_rate": 0.0}

    async def _compare_with_baselines(self, metrics: List[PromptMetric], metric_names: List[str]) -> Dict[str, Any]:
        """Compare avec les baselines établies"""
        return {"baseline_comparison": "above_baseline"}

    async def _detect_performance_anomalies(self, metrics: List[PromptMetric]) -> List[Dict[str, Any]]:
        """Détecte les anomalies de performance"""
        return []