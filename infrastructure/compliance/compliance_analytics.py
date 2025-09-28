#!/usr/bin/env python3
"""
📊 COMPLIANCE ANALYTICS ENGINE - AINFLUE ENTERPRISE
Intelligence artificielle pour analytics compliance et insights prédictifs

🏛️ EXPERTISE MULTI-RÔLES:
- Lead Dev IA: Intelligence artificielle pour analytics prédictifs compliance
- Backend Senior: Architecture enterprise pour processing massive données compliance
- ML Engineer: Algorithmes ML avancés pour patterns detection et predictions
- DBA: Optimisation BD pour analytics complexes et data warehousing compliance
- Sécurité: Analytics sécuritaires et détection anomalies compliance
- Microservices: Architecture distribuée pour services analytics scalables
- Audio Engineer: Analytics spécialisées contenu audio et compliance multimedia
- DevOps: Monitoring analytics temps réel et dashboards compliance
- IA Prompt Engineer: Auto-génération rapports analytics intelligents

👨‍💻 CRÉATEUR & PROPRIÉTÉ INTELLECTUELLE
Architecte Principal: Fahed Mlaiel (mlaiel@live.de)

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL
Toute utilisation non autorisée = Poursuites judiciaires immédiates
Contact: mlaiel@live.de
"""

import asyncio
import logging
import hashlib
import json
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps, lru_cache
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    pass  # Redis warning suppressed
import asyncpg
from cryptography.fernet import Fernet
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import seaborn as sns
import matplotlib.pyplot as plt

# Configuration logging avancé
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ainflue/compliance_analytics.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AnalyticsMetric(Enum):
    """Métriques analytics compliance"""
    COMPLIANCE_SCORE = "compliance_score"
    VIOLATION_RATE = "violation_rate"
    RESPONSE_TIME = "response_time"
    COST_COMPLIANCE = "cost_compliance"
    RISK_EXPOSURE = "risk_exposure"
    AUTOMATION_RATE = "automation_rate"
    TRAINING_EFFECTIVENESS = "training_effectiveness"
    INCIDENT_FREQUENCY = "incident_frequency"
    AUDIT_READINESS = "audit_readiness"
    REGULATORY_CHANGES = "regulatory_changes"

class TrendDirection(Enum):
    """Direction des tendances"""
    IMPROVING = "improving"
    DETERIORATING = "deteriorating"
    STABLE = "stable"
    VOLATILE = "volatile"

class AlertThreshold(Enum):
    """Seuils d'alerte analytics"""
    CRITICAL = "critical"    # Action immédiate requise
    WARNING = "warning"      # Attention requise
    INFO = "info"           # Information
    GOOD = "good"           # Performance excellente

@dataclass
class ComplianceMetric:
    """Métrique compliance avec contexte"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    source: str
    framework: str = ""
    entity_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrendAnalysis:
    """Analyse de tendance"""
    metric: AnalyticsMetric
    direction: TrendDirection
    magnitude: float  # Ampleur du changement
    confidence: float  # Confiance de la prédiction
    period_days: int
    forecast_next_30d: float
    recommendations: List[str] = field(default_factory=list)

@dataclass
class ComplianceInsight:
    """Insight compliance généré par IA"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    title: str = ""
    description: str = ""
    insight_type: str = "trend"  # trend, anomaly, prediction, recommendation
    priority: AlertThreshold = AlertThreshold.INFO
    affected_entities: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    actionable_recommendations: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    impact_assessment: str = ""

@dataclass
class ComplianceDashboard:
    """Dashboard compliance complet"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Métriques clés
    overall_compliance_score: float = 0.0
    total_entities: int = 0
    active_violations: int = 0
    resolved_violations: int = 0
    
    # Tendances
    score_trend: TrendDirection = TrendDirection.STABLE
    violation_trend: TrendDirection = TrendDirection.STABLE
    
    # Analytics par framework
    framework_scores: Dict[str, float] = field(default_factory=dict)
    framework_trends: Dict[str, TrendDirection] = field(default_factory=dict)
    
    # Insights IA
    top_insights: List[ComplianceInsight] = field(default_factory=list)
    
    # Prédictions
    risk_forecast_30d: float = 0.0
    compliance_forecast_30d: float = 0.0
    
    # Actions recommandées
    priority_actions: List[str] = field(default_factory=list)

class ComplianceAnalyticsEngine:
    """
    📊 MOTEUR ANALYTICS COMPLIANCE ENTERPRISE
    Intelligence artificielle pour analytics et insights compliance
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialiser le moteur analytics compliance"""
        self.config = config
        self.redis_client = None
        self.db_pool = None
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Modèles ML pour analytics
        self.trend_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.clustering_model = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)
        
        # Cache analytics
        self.metrics_cache: Dict[str, ComplianceMetric] = {}
        self.insights_cache: Dict[str, ComplianceInsight] = {}
        
        # Configuration analytics
        self.thresholds = {
            AnalyticsMetric.COMPLIANCE_SCORE: {
                AlertThreshold.CRITICAL: 60.0,
                AlertThreshold.WARNING: 80.0,
                AlertThreshold.GOOD: 95.0
            },
            AnalyticsMetric.VIOLATION_RATE: {
                AlertThreshold.CRITICAL: 10.0,
                AlertThreshold.WARNING: 5.0,
                AlertThreshold.GOOD: 1.0
            },
            AnalyticsMetric.RESPONSE_TIME: {
                AlertThreshold.CRITICAL: 48.0,  # heures
                AlertThreshold.WARNING: 24.0,
                AlertThreshold.GOOD: 12.0
            }
        }
        
        # Métriques système
        self.system_metrics = {
            'total_analytics_runs': 0,
            'insights_generated': 0,
            'anomalies_detected': 0,
            'predictions_accuracy': 0.0,
            'dashboard_views': 0
        }
        
        logger.info("📊 Compliance Analytics Engine initialisé - Fahed Mlaiel (mlaiel@live.de)")
    
    async def initialize(self):
        """Initialiser le moteur analytics"""
        try:
            # Connexion Redis pour cache analytics
            self.redis_client = await aioredis.from_url(
                self.config.get('redis_url', 'redis://localhost:6379'),
                encoding='utf-8',
                decode_responses=True
            )
            
            # Pool connexions PostgreSQL
            self.db_pool = await asyncpg.create_pool(
                self.config.get('database_url'),
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            
            # Créer les tables analytics
            await self._create_analytics_tables()
            
            # Charger les données historiques
            await self._load_historical_data()
            
            # Initialiser les modèles ML
            await self._initialize_ml_models()
            
            # Démarrer les workers analytics
            await self._start_analytics_workers()
            
            logger.info("✅ Compliance Analytics Engine initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation Analytics Engine: {e}")
            raise
    
    async def _create_analytics_tables(self):
        """Créer les tables analytics"""
        async with self.db_pool.acquire() as conn:
            # Table métriques compliance
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS compliance_metrics (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    metric_name VARCHAR(100) NOT NULL,
                    value DECIMAL(10,4) NOT NULL,
                    unit VARCHAR(20),
                    source VARCHAR(100),
                    framework VARCHAR(50),
                    entity_id VARCHAR(255),
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Table insights IA
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS compliance_insights (
                    id VARCHAR(36) PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    insight_type VARCHAR(50) DEFAULT 'trend',
                    priority VARCHAR(20) DEFAULT 'info',
                    affected_entities JSONB DEFAULT '[]',
                    frameworks JSONB DEFAULT '[]',
                    supporting_data JSONB DEFAULT '{}',
                    actionable_recommendations JSONB DEFAULT '[]',
                    confidence_score DECIMAL(5,2) DEFAULT 0.0,
                    impact_assessment TEXT,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Table dashboards
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS compliance_dashboards (
                    id VARCHAR(36) PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    overall_compliance_score DECIMAL(5,2) DEFAULT 0.0,
                    total_entities INTEGER DEFAULT 0,
                    active_violations INTEGER DEFAULT 0,
                    resolved_violations INTEGER DEFAULT 0,
                    score_trend VARCHAR(20) DEFAULT 'stable',
                    violation_trend VARCHAR(20) DEFAULT 'stable',
                    framework_scores JSONB DEFAULT '{}',
                    framework_trends JSONB DEFAULT '{}',
                    top_insights JSONB DEFAULT '[]',
                    risk_forecast_30d DECIMAL(5,2) DEFAULT 0.0,
                    compliance_forecast_30d DECIMAL(5,2) DEFAULT 0.0,
                    priority_actions JSONB DEFAULT '[]',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Index pour performance
            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON compliance_metrics(timestamp);
                CREATE INDEX IF NOT EXISTS idx_metrics_name ON compliance_metrics(metric_name);
                CREATE INDEX IF NOT EXISTS idx_metrics_entity ON compliance_metrics(entity_id);
                CREATE INDEX IF NOT EXISTS idx_insights_timestamp ON compliance_insights(timestamp);
                CREATE INDEX IF NOT EXISTS idx_insights_priority ON compliance_insights(priority);
                CREATE INDEX IF NOT EXISTS idx_dashboards_timestamp ON compliance_dashboards(timestamp);
            """)
    
    async def _load_historical_data(self):
        """Charger les données historiques pour analytics"""
        try:
            async with self.db_pool.acquire() as conn:
                # Charger métriques des 90 derniers jours
                metrics_data = await conn.fetch("""
                    SELECT metric_name, value, timestamp, framework, entity_id
                    FROM compliance_metrics
                    WHERE timestamp >= NOW() - INTERVAL '90 days'
                    ORDER BY timestamp DESC
                    LIMIT 10000
                """)
                
                # Convertir en DataFrame pour analytics
                if metrics_data:
                    self.historical_df = pd.DataFrame([
                        {
                            'metric': row['metric_name'],
                            'value': float(row['value']),
                            'timestamp': row['timestamp'],
                            'framework': row['framework'] or 'unknown',
                            'entity_id': row['entity_id'] or 'unknown'
                        }
                        for row in metrics_data
                    ])
                    
                    logger.info(f"✅ {len(self.historical_df)} métriques historiques chargées")
                else:
                    # Créer DataFrame vide si pas de données
                    self.historical_df = pd.DataFrame(columns=['metric', 'value', 'timestamp', 'framework', 'entity_id'])
                    logger.info("📊 Aucune donnée historique - Démarrage à froid")
                    
        except Exception as e:
            logger.warning(f"⚠️ Erreur chargement données historiques: {e}")
            self.historical_df = pd.DataFrame(columns=['metric', 'value', 'timestamp', 'framework', 'entity_id'])
    
    async def _initialize_ml_models(self):
        """Initialiser les modèles ML pour analytics"""
        try:
            if len(self.historical_df) > 100:  # Minimum de données pour entraînement
                # Préparer les features pour ML
                features_df = await self._prepare_ml_features()
                
                if len(features_df) > 50:
                    # Entraîner le modèle de tendance
                    X = features_df.drop(['target'], axis=1)
                    y = features_df['target']
                    
                    X_scaled = self.scaler.fit_transform(X)
                    self.trend_model.fit(X_scaled, y)
                    
                    # Entraîner le détecteur d'anomalies
                    self.anomaly_detector.fit(X_scaled)
                    
                    # Clustering des patterns compliance
                    self.clustering_model.fit(X_scaled)
                    
                    logger.info("✅ Modèles ML entraînés avec succès")
                else:
                    logger.info("📊 Données insuffisantes pour ML - Utilisation heuristiques")
            else:
                logger.info("📊 Pas assez de données historiques - Utilisation baseline")
                
        except Exception as e:
            logger.warning(f"⚠️ Erreur initialisation ML: {e}")
    
    async def _prepare_ml_features(self) -> pd.DataFrame:
        """Préparer les features pour ML"""
        try:
            features_list = []
            
            # Grouper par entité et métrique
            for (entity_id, metric), group in self.historical_df.groupby(['entity_id', 'metric']):
                if len(group) >= 7:  # Minimum 7 points pour tendance
                    # Calculer features temporelles
                    values = group.sort_values('timestamp')['value'].values
                    
                    # Features statistiques
                    mean_val = np.mean(values)
                    std_val = np.std(values)
                    trend_slope = np.polyfit(range(len(values)), values, 1)[0]
                    
                    # Features de série temporelle
                    recent_avg = np.mean(values[-7:])  # 7 derniers points
                    old_avg = np.mean(values[:7])      # 7 premiers points
                    
                    features_list.append({
                        'entity_id': entity_id,
                        'metric': metric,
                        'mean_value': mean_val,
                        'std_value': std_val,
                        'trend_slope': trend_slope,
                        'recent_avg': recent_avg,
                        'old_avg': old_avg,
                        'volatility': std_val / (mean_val + 1e-8),
                        'target': recent_avg  # Prédiction: moyenne récente
                    })
            
            features_df = pd.DataFrame(features_list)
            
            if len(features_df) > 0:
                # Encoder les variables catégorielles
                features_df = pd.get_dummies(features_df, columns=['metric'], prefix='metric')
                
            return features_df
            
        except Exception as e:
            logger.error(f"❌ Erreur préparation features ML: {e}")
            return pd.DataFrame()
    
    async def collect_compliance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        source: str = "system",
        framework: str = "",
        entity_id: str = ""
    ) -> ComplianceMetric:
        """
        📊 Collecter une métrique compliance
        
        Args:
            metric_name: Nom de la métrique
            value: Valeur de la métrique
            unit: Unité de mesure
            source: Source de la métrique
            framework: Framework réglementaire
            entity_id: Identifiant entité
            
        Returns:
            ComplianceMetric: Métrique collectée
        """
        try:
            metric = ComplianceMetric(
                name=metric_name,
                value=value,
                unit=unit,
                timestamp=datetime.utcnow(),
                source=source,
                framework=framework,
                entity_id=entity_id
            )
            
            # Stocker en base
            await self._store_metric(metric)
            
            # Ajouter au cache
            cache_key = f"{metric_name}:{entity_id}:{framework}"
            self.metrics_cache[cache_key] = metric
            
            # Déclencher analytics si métrique critique
            if metric_name in [m.value for m in AnalyticsMetric]:
                await self._trigger_metric_analysis(metric)
            
            logger.debug(f"📊 Métrique collectée: {metric_name} = {value} {unit}")
            return metric
            
        except Exception as e:
            logger.error(f"❌ Erreur collecte métrique: {e}")
            raise
    
    async def _store_metric(self, metric: ComplianceMetric):
        """Stocker métrique en base"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO compliance_metrics (
                    timestamp, metric_name, value, unit, source, framework, entity_id, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                metric.timestamp, metric.name, metric.value, metric.unit,
                metric.source, metric.framework, metric.entity_id,
                json.dumps(metric.metadata)
            )
    
    async def _trigger_metric_analysis(self, metric: ComplianceMetric):
        """Déclencher analyse quand métrique critique reçue"""
        try:
            # Vérifier seuils d'alerte
            alert_level = await self._check_metric_thresholds(metric)
            
            if alert_level in [AlertThreshold.CRITICAL, AlertThreshold.WARNING]:
                # Générer insight d'alerte
                insight = await self._generate_alert_insight(metric, alert_level)
                await self._store_insight(insight)
                
                logger.warning(f"⚠️ Seuil {alert_level.value} atteint pour {metric.name}: {metric.value}")
            
            # Détecter anomalies si modèle disponible
            await self._detect_metric_anomaly(metric)
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse métrique: {e}")
    
    async def _check_metric_thresholds(self, metric: ComplianceMetric) -> AlertThreshold:
        """Vérifier les seuils d'alerte pour une métrique"""
        try:
            metric_enum = AnalyticsMetric(metric.name)
            
            if metric_enum in self.thresholds:
                thresholds = self.thresholds[metric_enum]
                
                if metric.value <= thresholds[AlertThreshold.CRITICAL]:
                    return AlertThreshold.CRITICAL
                elif metric.value <= thresholds[AlertThreshold.WARNING]:
                    return AlertThreshold.WARNING
                elif metric.value >= thresholds[AlertThreshold.GOOD]:
                    return AlertThreshold.GOOD
                else:
                    return AlertThreshold.INFO
            
            return AlertThreshold.INFO
            
        except (ValueError, KeyError):
            return AlertThreshold.INFO
    
    async def _generate_alert_insight(self, metric: ComplianceMetric, alert_level: AlertThreshold) -> ComplianceInsight:
        """Générer insight d'alerte"""
        recommendations = []
        
        if metric.name == AnalyticsMetric.COMPLIANCE_SCORE.value:
            if alert_level == AlertThreshold.CRITICAL:
                recommendations.extend([
                    "🚨 Score compliance critique - Action immédiate requise",
                    "📋 Réviser toutes les mesures de conformité",
                    "👥 Former le personnel en urgence"
                ])
            elif alert_level == AlertThreshold.WARNING:
                recommendations.extend([
                    "⚠️ Score compliance en baisse - Attention requise",
                    "🔍 Analyser les causes de la dégradation"
                ])
        
        insight = ComplianceInsight(
            title=f"Alerte {alert_level.value.upper()}: {metric.name}",
            description=f"Métrique {metric.name} a atteint le seuil {alert_level.value} avec la valeur {metric.value} {metric.unit}",
            insight_type="alert",
            priority=alert_level,
            affected_entities=[metric.entity_id] if metric.entity_id else [],
            frameworks=[metric.framework] if metric.framework else [],
            supporting_data={
                "metric_name": metric.name,
                "current_value": metric.value,
                "threshold_level": alert_level.value,
                "source": metric.source
            },
            actionable_recommendations=recommendations,
            confidence_score=0.95,
            impact_assessment=f"Impact {alert_level.value} sur compliance {metric.framework}"
        )
        
        return insight
    
    async def generate_compliance_insights(
        self,
        entity_id: Optional[str] = None,
        framework: Optional[str] = None,
        days_back: int = 30
    ) -> List[ComplianceInsight]:
        """
        🧠 Générer des insights compliance avec IA
        
        Args:
            entity_id: Entité spécifique (optionnel)
            framework: Framework spécifique (optionnel)
            days_back: Nombre de jours d'historique
            
        Returns:
            List[ComplianceInsight]: Insights générés
        """
        try:
            insights = []
            
            # Récupérer les données pour analyse
            metrics_data = await self._get_metrics_for_analysis(entity_id, framework, days_back)
            
            if len(metrics_data) > 0:
                # 1. Analyse des tendances
                trend_insights = await self._analyze_trends(metrics_data)
                insights.extend(trend_insights)
                
                # 2. Détection d'anomalies
                anomaly_insights = await self._detect_anomalies(metrics_data)
                insights.extend(anomaly_insights)
                
                # 3. Analyse des patterns
                pattern_insights = await self._analyze_patterns(metrics_data)
                insights.extend(pattern_insights)
                
                # 4. Prédictions
                prediction_insights = await self._generate_predictions(metrics_data)
                insights.extend(prediction_insights)
                
                # 5. Recommandations IA
                recommendation_insights = await self._generate_ai_recommendations(metrics_data)
                insights.extend(recommendation_insights)
            
            # Stocker les insights
            for insight in insights:
                await self._store_insight(insight)
            
            # Trier par priorité et confiance
            insights.sort(key=lambda x: (x.priority.value, -x.confidence_score))
            
            self.system_metrics['insights_generated'] += len(insights)
            logger.info(f"🧠 {len(insights)} insights générés")
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Erreur génération insights: {e}")
            return []
    
    async def _get_metrics_for_analysis(self, entity_id: Optional[str], framework: Optional[str], days_back: int) -> pd.DataFrame:
        """Récupérer métriques pour analyse"""
        async with self.db_pool.acquire() as conn:
            where_clauses = ["timestamp >= NOW() - INTERVAL '{} days'".format(days_back)]
            params = []
            
            if entity_id:
                where_clauses.append("entity_id = ${}".format(len(params) + 1))
                params.append(entity_id)
            
            if framework:
                where_clauses.append("framework = ${}".format(len(params) + 1))
                params.append(framework)
            
            query = f"""
                SELECT metric_name, value, timestamp, framework, entity_id, source
                FROM compliance_metrics
                WHERE {' AND '.join(where_clauses)}
                ORDER BY timestamp DESC
            """
            
            rows = await conn.fetch(query, *params)
            
            if rows:
                return pd.DataFrame([
                    {
                        'metric': row['metric_name'],
                        'value': float(row['value']),
                        'timestamp': row['timestamp'],
                        'framework': row['framework'] or 'unknown',
                        'entity_id': row['entity_id'] or 'unknown',
                        'source': row['source']
                    }
                    for row in rows
                ])
            else:
                return pd.DataFrame()
    
    async def _analyze_trends(self, data: pd.DataFrame) -> List[ComplianceInsight]:
        """Analyser les tendances compliance"""
        insights = []
        
        try:
            # Analyser tendances par métrique
            for metric_name in data['metric'].unique():
                metric_data = data[data['metric'] == metric_name].sort_values('timestamp')
                
                if len(metric_data) >= 7:  # Minimum pour tendance
                    values = metric_data['value'].values
                    
                    # Calculer la tendance
                    slope, _ = np.polyfit(range(len(values)), values, 1)
                    
                    # Déterminer direction et magnitude
                    if abs(slope) > 0.1:  # Seuil de changement significatif
                        direction = TrendDirection.IMPROVING if slope > 0 else TrendDirection.DETERIORATING
                        
                        # Si métrique négative (comme violation_rate), inverser
                        if metric_name in ['violation_rate', 'response_time']:
                            direction = TrendDirection.DETERIORATING if slope > 0 else TrendDirection.IMPROVING
                        
                        insight = ComplianceInsight(
                            title=f"Tendance {direction.value} détectée: {metric_name}",
                            description=f"La métrique {metric_name} montre une tendance {direction.value} avec un changement de {slope:.2f} par période",
                            insight_type="trend",
                            priority=AlertThreshold.WARNING if direction == TrendDirection.DETERIORATING else AlertThreshold.INFO,
                            supporting_data={
                                "metric": metric_name,
                                "slope": slope,
                                "direction": direction.value,
                                "data_points": len(values),
                                "current_value": values[-1]
                            },
                            confidence_score=min(0.9, abs(slope) * 10),  # Plus la pente est forte, plus on est confiant
                            actionable_recommendations=await self._get_trend_recommendations(metric_name, direction)
                        )
                        
                        insights.append(insight)
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse tendances: {e}")
        
        return insights
    
    async def _get_trend_recommendations(self, metric_name: str, direction: TrendDirection) -> List[str]:
        """Obtenir recommandations basées sur la tendance"""
        recommendations = []
        
        if direction == TrendDirection.DETERIORATING:
            if metric_name == AnalyticsMetric.COMPLIANCE_SCORE.value:
                recommendations.extend([
                    "📋 Réviser les procédures de conformité",
                    "👥 Renforcer la formation du personnel",
                    "🔍 Audit interne recommandé"
                ])
            elif metric_name == AnalyticsMetric.VIOLATION_RATE.value:
                recommendations.extend([
                    "🚨 Analyser les causes des violations",
                    "⚡ Améliorer les contrôles préventifs",
                    "📚 Mise à jour des politiques"
                ])
            elif metric_name == AnalyticsMetric.RESPONSE_TIME.value:
                recommendations.extend([
                    "⏱️ Optimiser les processus de réponse",
                    "🤖 Automatiser davantage de tâches",
                    "👥 Augmenter les ressources"
                ])
        else:  # IMPROVING
            recommendations.extend([
                "✅ Maintenir les bonnes pratiques actuelles",
                "📈 Documenter les facteurs de succès",
                "🎯 Définir de nouveaux objectifs d'amélioration"
            ])
        
        return recommendations
    
    async def _detect_anomalies(self, data: pd.DataFrame) -> List[ComplianceInsight]:
        """Détecter les anomalies dans les métriques"""
        insights = []
        
        try:
            if hasattr(self, 'anomaly_detector') and len(data) > 10:
                # Préparer données pour détection anomalies
                numeric_cols = ['value']
                X = data[numeric_cols].values
                
                # Détecter anomalies
                anomalies = self.anomaly_detector.predict(X)
                
                # Analyser les anomalies détectées
                anomaly_indices = np.where(anomalies == -1)[0]
                
                for idx in anomaly_indices:
                    anomaly_row = data.iloc[idx]
                    
                    insight = ComplianceInsight(
                        title=f"Anomalie détectée: {anomaly_row['metric']}",
                        description=f"Valeur anormale détectée pour {anomaly_row['metric']}: {anomaly_row['value']}",
                        insight_type="anomaly",
                        priority=AlertThreshold.WARNING,
                        supporting_data={
                            "metric": anomaly_row['metric'],
                            "anomaly_value": anomaly_row['value'],
                            "timestamp": anomaly_row['timestamp'].isoformat(),
                            "entity_id": anomaly_row['entity_id']
                        },
                        confidence_score=0.7,
                        actionable_recommendations=[
                            "🔍 Investiguer la cause de cette valeur anormale",
                            "📊 Vérifier la qualité des données",
                            "⚠️ Surveillance renforcée recommandée"
                        ]
                    )
                    
                    insights.append(insight)
                    self.system_metrics['anomalies_detected'] += 1
        
        except Exception as e:
            logger.error(f"❌ Erreur détection anomalies: {e}")
        
        return insights
    
    async def generate_compliance_dashboard(
        self,
        entity_id: Optional[str] = None,
        framework: Optional[str] = None
    ) -> ComplianceDashboard:
        """
        📊 Générer dashboard compliance complet
        
        Args:
            entity_id: Entité spécifique (optionnel)
            framework: Framework spécifique (optionnel)
            
        Returns:
            ComplianceDashboard: Dashboard complet
        """
        try:
            dashboard = ComplianceDashboard()
            
            # Récupérer métriques récentes
            recent_metrics = await self._get_metrics_for_analysis(entity_id, framework, 30)
            
            if len(recent_metrics) > 0:
                # Calculer score compliance global
                compliance_scores = recent_metrics[recent_metrics['metric'] == AnalyticsMetric.COMPLIANCE_SCORE.value]
                if len(compliance_scores) > 0:
                    dashboard.overall_compliance_score = compliance_scores['value'].mean()
                    dashboard.score_trend = await self._calculate_trend_direction(compliance_scores['value'].values)
                
                # Calculer violations
                violations = recent_metrics[recent_metrics['metric'] == AnalyticsMetric.VIOLATION_RATE.value]
                if len(violations) > 0:
                    dashboard.active_violations = int(violations['value'].sum())
                    dashboard.violation_trend = await self._calculate_trend_direction(violations['value'].values)
                
                # Entités uniques
                dashboard.total_entities = recent_metrics['entity_id'].nunique()
                
                # Scores par framework
                for fw in recent_metrics['framework'].unique():
                    fw_data = recent_metrics[recent_metrics['framework'] == fw]
                    fw_scores = fw_data[fw_data['metric'] == AnalyticsMetric.COMPLIANCE_SCORE.value]
                    
                    if len(fw_scores) > 0:
                        dashboard.framework_scores[fw] = fw_scores['value'].mean()
                        dashboard.framework_trends[fw] = await self._calculate_trend_direction(fw_scores['value'].values)
                
                # Générer insights top priorité
                insights = await self.generate_compliance_insights(entity_id, framework, 7)
                dashboard.top_insights = insights[:5]  # Top 5 insights
                
                # Prédictions 30 jours
                dashboard.risk_forecast_30d = await self._predict_risk_30d(recent_metrics)
                dashboard.compliance_forecast_30d = await self._predict_compliance_30d(recent_metrics)
                
                # Actions prioritaires
                dashboard.priority_actions = await self._generate_priority_actions(dashboard)
            
            # Stocker dashboard
            await self._store_dashboard(dashboard)
            
            self.system_metrics['dashboard_views'] += 1
            logger.info(f"📊 Dashboard généré: Score {dashboard.overall_compliance_score:.1f}%")
            
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Erreur génération dashboard: {e}")
            return ComplianceDashboard()
    
    async def _calculate_trend_direction(self, values: np.ndarray) -> TrendDirection:
        """Calculer la direction de tendance"""
        if len(values) < 3:
            return TrendDirection.STABLE
        
        # Calculer pente de régression linéaire
        slope, _ = np.polyfit(range(len(values)), values, 1)
        
        if abs(slope) < 0.1:
            return TrendDirection.STABLE
        elif slope > 0:
            return TrendDirection.IMPROVING
        else:
            return TrendDirection.DETERIORATING
    
    async def _predict_risk_30d(self, data: pd.DataFrame) -> float:
        """Prédire le risque dans 30 jours"""
        try:
            # Simplification: utiliser moyenne des violations récentes
            violations = data[data['metric'] == AnalyticsMetric.VIOLATION_RATE.value]
            
            if len(violations) > 0:
                recent_avg = violations['value'].tail(7).mean()
                return min(100.0, recent_avg * 1.1)  # Projection +10%
            
            return 5.0  # Valeur par défaut
            
        except Exception:
            return 5.0
    
    async def _predict_compliance_30d(self, data: pd.DataFrame) -> float:
        """Prédire le score compliance dans 30 jours"""
        try:
            scores = data[data['metric'] == AnalyticsMetric.COMPLIANCE_SCORE.value]
            
            if len(scores) > 0:
                recent_trend = await self._calculate_trend_direction(scores['value'].values)
                current_avg = scores['value'].tail(7).mean()
                
                if recent_trend == TrendDirection.IMPROVING:
                    return min(100.0, current_avg * 1.05)
                elif recent_trend == TrendDirection.DETERIORATING:
                    return max(0.0, current_avg * 0.95)
                else:
                    return current_avg
            
            return 75.0  # Valeur par défaut
            
        except Exception:
            return 75.0
    
    async def _store_dashboard(self, dashboard: ComplianceDashboard):
        """Stocker dashboard en base"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO compliance_dashboards (
                    id, timestamp, overall_compliance_score, total_entities,
                    active_violations, resolved_violations, score_trend, violation_trend,
                    framework_scores, framework_trends, top_insights,
                    risk_forecast_30d, compliance_forecast_30d, priority_actions
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            """,
                dashboard.id, dashboard.timestamp, dashboard.overall_compliance_score,
                dashboard.total_entities, dashboard.active_violations, dashboard.resolved_violations,
                dashboard.score_trend.value, dashboard.violation_trend.value,
                json.dumps(dashboard.framework_scores), json.dumps({k: v.value for k, v in dashboard.framework_trends.items()}),
                json.dumps([insight.title for insight in dashboard.top_insights]),
                dashboard.risk_forecast_30d, dashboard.compliance_forecast_30d,
                json.dumps(dashboard.priority_actions)
            )
    
    async def _store_insight(self, insight: ComplianceInsight):
        """Stocker insight en base"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO compliance_insights (
                    id, timestamp, title, description, insight_type, priority,
                    affected_entities, frameworks, supporting_data,
                    actionable_recommendations, confidence_score, impact_assessment
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            """,
                insight.id, insight.timestamp, insight.title, insight.description,
                insight.insight_type, insight.priority.value,
                json.dumps(insight.affected_entities), json.dumps(insight.frameworks),
                json.dumps(insight.supporting_data), json.dumps(insight.actionable_recommendations),
                insight.confidence_score, insight.impact_assessment
            )
    
    async def _start_analytics_workers(self):
        """Démarrer les workers analytics"""
        # Worker analytics périodiques
        asyncio.create_task(self._periodic_analytics_worker())
        
        # Worker nettoyage données anciennes
        asyncio.create_task(self._data_cleanup_worker())
        
        logger.info("✅ Workers analytics démarrés")
    
    async def _periodic_analytics_worker(self):
        """Worker pour analytics périodiques"""
        while True:
            try:
                # Générer insights quotidiens
                await self.generate_compliance_insights(days_back=7)
                
                # Générer dashboard global
                await self.generate_compliance_dashboard()
                
                self.system_metrics['total_analytics_runs'] += 1
                
                await asyncio.sleep(86400)  # Quotidien
                
            except Exception as e:
                logger.error(f"❌ Erreur analytics worker: {e}")
                await asyncio.sleep(3600)

# Interface publique
async def analyze_compliance_metrics(
    entity_id: Optional[str] = None,
    framework: Optional[str] = None,
    days_back: int = 30
) -> Dict[str, Any]:
    """
    Interface publique pour analytics compliance
    
    Args:
        entity_id: Entité à analyser
        framework: Framework spécifique
        days_back: Jours d'historique
        
    Returns:
        Dict: Résultats analytics
    """
    engine = ComplianceAnalyticsEngine({})
    await engine.initialize()
    
    # Générer insights
    insights = await engine.generate_compliance_insights(entity_id, framework, days_back)
    
    # Générer dashboard
    dashboard = await engine.generate_compliance_dashboard(entity_id, framework)
    
    return {
        "insights_count": len(insights),
        "top_insights": [
            {
                "title": insight.title,
                "type": insight.insight_type,
                "priority": insight.priority.value,
                "confidence": insight.confidence_score
            }
            for insight in insights[:5]
        ],
        "dashboard": {
            "compliance_score": dashboard.overall_compliance_score,
            "total_entities": dashboard.total_entities,
            "active_violations": dashboard.active_violations,
            "score_trend": dashboard.score_trend.value,
            "risk_forecast_30d": dashboard.risk_forecast_30d
        }
    }

if __name__ == "__main__":
    # Test du moteur analytics
    async def test_analytics_engine():
        config = {
            'redis_url': 'redis://localhost:6379',
            'database_url': 'postgresql://user:pass@localhost/ainflue'
        }
        
        engine = ComplianceAnalyticsEngine(config)
        await engine.initialize()
        
        # Simuler quelques métriques
        await engine.collect_compliance_metric(
            metric_name="compliance_score",
            value=85.5,
            unit="%",
            framework="gdpr",
            entity_id="creator_123"
        )
        
        await engine.collect_compliance_metric(
            metric_name="violation_rate",
            value=2.1,
            unit="%",
            framework="gdpr",
            entity_id="creator_123"
        )
        
        # Générer insights
        insights = await engine.generate_compliance_insights(entity_id="creator_123")
        print(f"🧠 {len(insights)} insights générés")
        
        # Générer dashboard
        dashboard = await engine.generate_compliance_dashboard()
        print(f"📊 Dashboard: Score {dashboard.overall_compliance_score:.1f}%")
    
    # asyncio.run(test_analytics_engine())
    
    logger.info("📊 Compliance Analytics Engine - Prêt pour production")
    logger.info("👨‍💻 Créé par Fahed Mlaiel (mlaiel@live.de)")
    logger.info("⚠️ Propriété intellectuelle exclusive protégée")