#!/usr/bin/env python3
"""💡 Insight Generation Manager - Advanced AI-Powered Insights Platform
================================================================
Expert: DATA SCIENTIST + ML ENGINEER + BUSINESS ANALYST + BACKEND SENIOR
Technologies: AI Insights + Pattern Discovery + Natural Language Generation + Automated Analysis
Architecture: Level 3 - Insight Intelligence Layer
Date: 2025-01-25

Ultra-advanced insight generation system with AI-powered pattern discovery,
natural language generation, automated analysis and intelligent recommendations.
================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
================================================================
"""

import asyncio
import logging
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import redis
from abc import ABC, abstractmethod
import statistics
import math
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict, deque
import re
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx

logger = logging.getLogger(__name__)

class InsightType(Enum):
    """Types d'insights"""
    PERFORMANCE = "performance"
    ANOMALY = "anomaly"
    TREND = "trend"
    CORRELATION = "correlation"
    PATTERN = "pattern"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    RECOMMENDATION = "recommendation"
    PREDICTION = "prediction"
    CAUSATION = "causation"
    OPTIMIZATION = "optimization"
    CREATOR_BEHAVIOR = "creator_behavior"

class InsightCategory(Enum):
    """Catégories d'insights"""
    BUSINESS = "business"
    TECHNICAL = "technical"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"
    CREATOR_ECONOMY = "creator_economy"
    USER_EXPERIENCE = "user_experience"
    SECURITY = "security"

class InsightPriority(Enum):
    """Priorités d'insights"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class InsightConfidence(Enum):
    """Niveaux de confiance"""
    VERY_HIGH = "very_high"  # > 0.9
    HIGH = "high"            # 0.8 - 0.9
    MEDIUM = "medium"        # 0.6 - 0.8
    LOW = "low"              # 0.4 - 0.6
    VERY_LOW = "very_low"    # < 0.4

class AnalysisMethod(Enum):
    """Méthodes d'analyse"""
    STATISTICAL = "statistical"
    MACHINE_LEARNING = "machine_learning"
    PATTERN_MATCHING = "pattern_matching"
    CORRELATION_ANALYSIS = "correlation_analysis"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"
    NETWORK_ANALYSIS = "network_analysis"
    TEXT_MINING = "text_mining"

@dataclass
class DataPoint:
    """Point de données pour l'analyse"""
    id: str
    value: Any
    timestamp: datetime
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

@dataclass
class Pattern:
    """Motif découvert"""
    id: str
    name: str
    description: str
    type: str
    confidence: float
    support: float  # Fréquence du motif
    data_points: List[DataPoint] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Correlation:
    """Corrélation entre variables"""
    id: str
    variable_1: str
    variable_2: str
    correlation_coefficient: float
    p_value: float
    significance_level: float
    relationship_type: str  # positive, negative, non-linear
    strength: str  # weak, moderate, strong
    confidence: float

@dataclass
class Insight:
    """Insight généré"""
    id: str
    title: str
    description: str
    type: InsightType
    category: InsightCategory
    priority: InsightPriority
    confidence: float
    impact_score: float
    actionable: bool
    evidence: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)
    patterns: List[Pattern] = field(default_factory=list)
    correlations: List[Correlation] = field(default_factory=list)
    analysis_method: AnalysisMethod = AnalysisMethod.STATISTICAL
    keywords: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class InsightRule:
    """Règle de génération d'insights"""
    id: str
    name: str
    description: str
    condition: str  # Expression à évaluer
    insight_template: Dict[str, Any]
    enabled: bool = True
    priority: int = 1
    confidence_threshold: float = 0.6
    frequency_limit: Optional[int] = None  # Max fois par période
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class InsightGenerationConfig:
    """Configuration du générateur d'insights"""
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 9
    analysis_interval: int = 300  # 5 minutes
    min_data_points: int = 10
    max_insights_per_cycle: int = 50
    confidence_threshold: float = 0.6
    enable_ml_analysis: bool = True
    enable_pattern_discovery: bool = True
    enable_correlation_analysis: bool = True
    enable_nlp_insights: bool = True
    data_retention_days: int = 30
    parallel_processors: int = 4
    creator_economy_focus: bool = True
    custom_rules: List[InsightRule] = field(default_factory=list)

class InsightProcessor(ABC):
    """Processeur d'insights abstrait"""
    
    @abstractmethod
    async def process(self, data: List[DataPoint]) -> List[Insight]:
        """Traite les données et génère des insights"""
        pass
    
    @abstractmethod
    def get_processor_type(self) -> str:
        """Retourne le type de processeur"""
        pass

class StatisticalInsightProcessor(InsightProcessor):
    """Processeur d'insights statistiques"""
    
    def __init__(self):
        self.name = "Statistical Insight Processor"
    
    async def process(self, data: List[DataPoint]) -> List[Insight]:
        """Traite les données avec des méthodes statistiques"""
        insights = []
        
        try:
            # Grouper les données par source
            data_by_source = defaultdict(list)
            for point in data:
                data_by_source[point.source].append(point)
            
            # Analyse statistique pour chaque source
            for source, points in data_by_source.items():
                if len(points) >= 5:
                    source_insights = await self._analyze_source_data(source, points)
                    insights.extend(source_insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Erreur dans le processeur statistique: {e}")
            return []
    
    async def _analyze_source_data(self, source: str, points: List[DataPoint]) -> List[Insight]:
        """Analyse les données d'une source"""
        insights = []
        
        try:
            # Extraction des valeurs numériques
            numeric_values = []
            for point in points:
                if isinstance(point.value, (int, float)):
                    numeric_values.append(point.value)
            
            if len(numeric_values) >= 5:
                # Analyse des tendances
                trend_insight = await self._analyze_trend(source, numeric_values, points)
                if trend_insight:
                    insights.append(trend_insight)
                
                # Analyse des anomalies
                anomaly_insights = await self._detect_anomalies(source, numeric_values, points)
                insights.extend(anomaly_insights)
                
                # Analyse de la variabilité
                variability_insight = await self._analyze_variability(source, numeric_values, points)
                if variability_insight:
                    insights.append(variability_insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Erreur dans l'analyse des données de source {source}: {e}")
            return []
    
    async def _analyze_trend(self, source: str, values: List[float], points: List[DataPoint]) -> Optional[Insight]:
        """Analyse les tendances"""
        try:
            if len(values) < 5:
                return None
            
            # Calcul de la tendance (régression linéaire simple)
            x = np.arange(len(values))
            y = np.array(values)
            
            slope, intercept = np.polyfit(x, y, 1)
            
            # Seuil de significativité
            if abs(slope) < np.std(values) * 0.1:
                return None
            
            trend_direction = "croissante" if slope > 0 else "décroissante"
            trend_strength = "forte" if abs(slope) > np.std(values) * 0.5 else "modérée"
            
            confidence = min(0.95, abs(slope) / np.std(values))
            impact_score = min(10.0, abs(slope) * 2)
            
            return Insight(
                id=f"trend_{source}_{int(time.time())}",
                title=f"Tendance {trend_direction} détectée dans {source}",
                description=f"Une tendance {trend_direction} {trend_strength} a été identifiée dans les données de {source}. "
                           f"Pente: {slope:.4f}, Variation moyenne: {np.std(values):.2f}",
                type=InsightType.TREND,
                category=InsightCategory.OPERATIONAL,
                priority=InsightPriority.MEDIUM if trend_strength == "modérée" else InsightPriority.HIGH,
                confidence=confidence,
                impact_score=impact_score,
                actionable=True,
                evidence=[
                    f"Pente de régression: {slope:.4f}",
                    f"Nombre de points analysés: {len(values)}",
                    f"Écart-type: {np.std(values):.2f}"
                ],
                recommendations=[
                    f"Surveiller l'évolution de {source}",
                    "Investiguer les causes de cette tendance",
                    "Planifier des actions préventives si nécessaire"
                ],
                data_sources=[source],
                analysis_method=AnalysisMethod.STATISTICAL,
                keywords=["tendance", trend_direction, source]
            )
            
        except Exception as e:
            logger.error(f"Erreur dans l'analyse de tendance: {e}")
            return None
    
    async def _detect_anomalies(self, source: str, values: List[float], points: List[DataPoint]) -> List[Insight]:
        """Détecte les anomalies statistiques"""
        insights = []
        
        try:
            if len(values) < 10:
                return insights
            
            # Calcul des statistiques
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            # Détection d'anomalies (règle 3-sigma)
            threshold = 3 * std_val
            anomalies = []
            
            for i, value in enumerate(values):
                if abs(value - mean_val) > threshold:
                    anomalies.append((i, value, points[i]))
            
            # Génération d'insights pour les anomalies
            for i, (index, value, point) in enumerate(anomalies[:5]):  # Max 5 anomalies
                severity = "critique" if abs(value - mean_val) > 4 * std_val else "majeure"
                
                insights.append(Insight(
                    id=f"anomaly_{source}_{index}_{int(time.time())}",
                    title=f"Anomalie {severity} détectée dans {source}",
                    description=f"Valeur anormale détectée: {value:.2f} (écart de {abs(value - mean_val):.2f} "
                               f"par rapport à la moyenne {mean_val:.2f})",
                    type=InsightType.ANOMALY,
                    category=InsightCategory.OPERATIONAL,
                    priority=InsightPriority.CRITICAL if severity == "critique" else InsightPriority.HIGH,
                    confidence=min(0.95, abs(value - mean_val) / (4 * std_val)),
                    impact_score=min(10.0, abs(value - mean_val) / std_val),
                    actionable=True,
                    evidence=[
                        f"Valeur: {value:.2f}",
                        f"Moyenne: {mean_val:.2f}",
                        f"Écart-type: {std_val:.2f}",
                        f"Écart en sigmas: {abs(value - mean_val) / std_val:.2f}"
                    ],
                    recommendations=[
                        f"Investiguer immédiatement la cause de cette anomalie",
                        "Vérifier l'intégrité des données",
                        "Mettre en place des alertes préventives"
                    ],
                    data_sources=[source],
                    analysis_method=AnalysisMethod.STATISTICAL,
                    keywords=["anomalie", severity, source]
                ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Erreur dans la détection d'anomalies: {e}")
            return []
    
    async def _analyze_variability(self, source: str, values: List[float], points: List[DataPoint]) -> Optional[Insight]:
        """Analyse la variabilité des données"""
        try:
            if len(values) < 10:
                return None
            
            coefficient_variation = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
            
            # Seuils de variabilité
            if coefficient_variation < 0.1:
                variability_level = "très faible"
                priority = InsightPriority.LOW
            elif coefficient_variation < 0.3:
                variability_level = "faible"
                priority = InsightPriority.LOW
            elif coefficient_variation < 0.6:
                variability_level = "modérée"
                priority = InsightPriority.MEDIUM
            elif coefficient_variation < 1.0:
                variability_level = "élevée"
                priority = InsightPriority.HIGH
            else:
                variability_level = "très élevée"
                priority = InsightPriority.CRITICAL
            
            # Génération d'insight uniquement si la variabilité est notable
            if coefficient_variation > 0.3:
                return Insight(
                    id=f"variability_{source}_{int(time.time())}",
                    title=f"Variabilité {variability_level} dans {source}",
                    description=f"Les données de {source} présentent une variabilité {variability_level} "
                               f"(coefficient de variation: {coefficient_variation:.3f})",
                    type=InsightType.PATTERN,
                    category=InsightCategory.OPERATIONAL,
                    priority=priority,
                    confidence=0.8,
                    impact_score=coefficient_variation * 5,
                    actionable=True,
                    evidence=[
                        f"Coefficient de variation: {coefficient_variation:.3f}",
                        f"Écart-type: {np.std(values):.2f}",
                        f"Moyenne: {np.mean(values):.2f}"
                    ],
                    recommendations=[
                        "Analyser les causes de cette variabilité",
                        "Considérer la stabilisation des processus",
                        "Surveiller les tendances de variabilité"
                    ],
                    data_sources=[source],
                    analysis_method=AnalysisMethod.STATISTICAL,
                    keywords=["variabilité", variability_level, source]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur dans l'analyse de variabilité: {e}")
            return None
    
    def get_processor_type(self) -> str:
        return "statistical"

class MachineLearningInsightProcessor(InsightProcessor):
    """Processeur d'insights basé sur l'apprentissage automatique"""
    
    def __init__(self):
        self.name = "ML Insight Processor"
        self.clusterer = None
        self.scaler = StandardScaler()
    
    async def process(self, data: List[DataPoint]) -> List[Insight]:
        """Traite les données avec des méthodes ML"""
        insights = []
        
        try:
            # Préparation des données pour le ML
            feature_matrix, data_mapping = await self._prepare_features(data)
            
            if len(feature_matrix) >= 10:
                # Clustering insights
                clustering_insights = await self._perform_clustering(feature_matrix, data_mapping)
                insights.extend(clustering_insights)
                
                # Analyse des composantes principales
                pca_insights = await self._perform_pca_analysis(feature_matrix, data_mapping)
                insights.extend(pca_insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Erreur dans le processeur ML: {e}")
            return []
    
    async def _prepare_features(self, data: List[DataPoint]) -> Tuple[np.ndarray, List[DataPoint]]:
        """Prépare les features pour l'analyse ML"""
        try:
            features = []
            valid_data = []
            
            for point in data:
                if isinstance(point.value, (int, float)):
                    # Features simples pour l'exemple
                    feature_vector = [
                        float(point.value),
                        float(point.timestamp.hour),
                        float(point.timestamp.weekday()),
                        len(point.tags),
                        len(point.metadata)
                    ]
                    features.append(feature_vector)
                    valid_data.append(point)
            
            if features:
                feature_matrix = np.array(features)
                # Normalisation
                feature_matrix = self.scaler.fit_transform(feature_matrix)
                return feature_matrix, valid_data
            
            return np.array([]), []
            
        except Exception as e:
            logger.error(f"Erreur dans la préparation des features: {e}")
            return np.array([]), []
    
    async def _perform_clustering(self, features: np.ndarray, data: List[DataPoint]) -> List[Insight]:
        """Effectue un clustering et génère des insights"""
        insights = []
        
        try:
            if len(features) < 10:
                return insights
            
            # Clustering K-means
            n_clusters = min(5, len(features) // 3)
            if n_clusters >= 2:
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                cluster_labels = kmeans.fit_predict(features)
                
                # Analyse des clusters
                cluster_analysis = defaultdict(list)
                for i, label in enumerate(cluster_labels):
                    cluster_analysis[label].append(data[i])
                
                # Génération d'insights pour les clusters
                for cluster_id, cluster_data in cluster_analysis.items():
                    if len(cluster_data) >= 3:
                        insight = await self._analyze_cluster(cluster_id, cluster_data, n_clusters)
                        if insight:
                            insights.append(insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Erreur dans le clustering: {e}")
            return []
    
    async def _analyze_cluster(self, cluster_id: int, cluster_data: List[DataPoint], total_clusters: int) -> Optional[Insight]:
        """Analyse un cluster spécifique"""
        try:
            # Calcul des statistiques du cluster
            values = [point.value for point in cluster_data if isinstance(point.value, (int, float))]
            
            if not values:
                return None
            
            cluster_mean = np.mean(values)
            cluster_size = len(cluster_data)
            cluster_percentage = (cluster_size / sum(len(cluster_data) for cluster_data in [cluster_data])) * 100
            
            # Sources dominantes dans le cluster
            sources = [point.source for point in cluster_data]
            dominant_source = max(set(sources), key=sources.count)
            
            return Insight(
                id=f"cluster_{cluster_id}_{int(time.time())}",
                title=f"Groupe de données identifié (Cluster {cluster_id + 1})",
                description=f"Un groupe distinct de {cluster_size} points de données a été identifié, "
                           f"représentant {cluster_percentage:.1f}% des données. "
                           f"Valeur moyenne: {cluster_mean:.2f}, Source dominante: {dominant_source}",
                type=InsightType.PATTERN,
                category=InsightCategory.TECHNICAL,
                priority=InsightPriority.MEDIUM,
                confidence=0.75,
                impact_score=cluster_percentage / 10,
                actionable=True,
                evidence=[
                    f"Taille du cluster: {cluster_size}",
                    f"Pourcentage des données: {cluster_percentage:.1f}%",
                    f"Valeur moyenne: {cluster_mean:.2f}",
                    f"Source dominante: {dominant_source}"
                ],
                recommendations=[
                    f"Analyser les caractéristiques spécifiques du groupe {cluster_id + 1}",
                    "Identifier les facteurs communs dans ce groupe",
                    "Exploiter les patterns identifiés pour l'optimisation"
                ],
                data_sources=[dominant_source],
                analysis_method=AnalysisMethod.MACHINE_LEARNING,
                keywords=["clustering", "pattern", "groupe", dominant_source]
            )
            
        except Exception as e:
            logger.error(f"Erreur dans l'analyse du cluster {cluster_id}: {e}")
            return None
    
    async def _perform_pca_analysis(self, features: np.ndarray, data: List[DataPoint]) -> List[Insight]:
        """Effectue une analyse PCA"""
        insights = []
        
        try:
            if len(features) < 5 or features.shape[1] < 3:
                return insights
            
            # PCA
            pca = PCA(n_components=min(3, features.shape[1]))
            pca_features = pca.fit_transform(features)
            
            # Analyse de la variance expliquée
            explained_variance_ratio = pca.explained_variance_ratio_
            
            # Insight sur la dimensionnalité
            if explained_variance_ratio[0] > 0.7:
                insights.append(Insight(
                    id=f"pca_dimensionality_{int(time.time())}",
                    title="Dimensionnalité réduite détectée",
                    description=f"La première composante principale explique {explained_variance_ratio[0]:.1%} "
                               f"de la variance, suggérant une structure sous-jacente simple dans les données.",
                    type=InsightType.PATTERN,
                    category=InsightCategory.TECHNICAL,
                    priority=InsightPriority.MEDIUM,
                    confidence=0.8,
                    impact_score=explained_variance_ratio[0] * 5,
                    actionable=True,
                    evidence=[
                        f"Variance expliquée PC1: {explained_variance_ratio[0]:.1%}",
                        f"Variance expliquée PC2: {explained_variance_ratio[1]:.1%}" if len(explained_variance_ratio) > 1 else "PC2: N/A",
                        f"Nombre de features originales: {features.shape[1]}"
                    ],
                    recommendations=[
                        "Explorer la simplification du modèle de données",
                        "Identifier les variables redondantes",
                        "Optimiser la collecte de données"
                    ],
                    analysis_method=AnalysisMethod.MACHINE_LEARNING,
                    keywords=["PCA", "dimensionnalité", "structure"]
                ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Erreur dans l'analyse PCA: {e}")
            return []
    
    def get_processor_type(self) -> str:
        return "machine_learning"

class CorrelationInsightProcessor(InsightProcessor):
    """Processeur d'insights de corrélation"""
    
    def __init__(self):
        self.name = "Correlation Insight Processor"
    
    async def process(self, data: List[DataPoint]) -> List[Insight]:
        """Traite les corrélations entre variables"""
        insights = []
        
        try:
            # Groupement des données par source
            data_by_source = defaultdict(list)
            for point in data:
                if isinstance(point.value, (int, float)):
                    data_by_source[point.source].append(point.value)
            
            # Calcul des corrélations entre sources
            sources = list(data_by_source.keys())
            
            for i, source1 in enumerate(sources):
                for source2 in sources[i+1:]:
                    if len(data_by_source[source1]) >= 5 and len(data_by_source[source2]) >= 5:
                        correlation_insight = await self._analyze_correlation(
                            source1, data_by_source[source1],
                            source2, data_by_source[source2]
                        )
                        if correlation_insight:
                            insights.append(correlation_insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Erreur dans le processeur de corrélation: {e}")
            return []
    
    async def _analyze_correlation(self, source1: str, values1: List[float], 
                                 source2: str, values2: List[float]) -> Optional[Insight]:
        """Analyse la corrélation entre deux sources"""
        try:
            # Alignement des données (même longueur)
            min_length = min(len(values1), len(values2))
            if min_length < 5:
                return None
            
            aligned_values1 = values1[-min_length:]
            aligned_values2 = values2[-min_length:]
            
            # Calcul de la corrélation de Pearson
            correlation_matrix = np.corrcoef(aligned_values1, aligned_values2)
            correlation_coeff = correlation_matrix[0, 1]
            
            # Seuil de significativité
            if abs(correlation_coeff) < 0.3:
                return None
            
            # Détermination de la force de la corrélation
            abs_corr = abs(correlation_coeff)
            if abs_corr >= 0.8:
                strength = "très forte"
                priority = InsightPriority.HIGH
            elif abs_corr >= 0.6:
                strength = "forte"
                priority = InsightPriority.MEDIUM
            elif abs_corr >= 0.4:
                strength = "modérée"
                priority = InsightPriority.MEDIUM
            else:
                strength = "faible"
                priority = InsightPriority.LOW
            
            direction = "positive" if correlation_coeff > 0 else "négative"
            
            return Insight(
                id=f"correlation_{source1}_{source2}_{int(time.time())}",
                title=f"Corrélation {strength} entre {source1} et {source2}",
                description=f"Une corrélation {direction} {strength} a été détectée entre {source1} et {source2} "
                           f"(coefficient: {correlation_coeff:.3f})",
                type=InsightType.CORRELATION,
                category=InsightCategory.TECHNICAL,
                priority=priority,
                confidence=min(0.95, abs_corr),
                impact_score=abs_corr * 5,
                actionable=True,
                evidence=[
                    f"Coefficient de corrélation: {correlation_coeff:.3f}",
                    f"Nombre de points analysés: {min_length}",
                    f"Force de la corrélation: {strength}",
                    f"Direction: {direction}"
                ],
                recommendations=[
                    f"Investiguer la relation causale entre {source1} et {source2}",
                    "Exploiter cette corrélation pour la prédiction",
                    "Surveiller l'évolution de cette relation"
                ],
                data_sources=[source1, source2],
                analysis_method=AnalysisMethod.CORRELATION_ANALYSIS,
                keywords=["corrélation", direction, strength, source1, source2]
            )
            
        except Exception as e:
            logger.error(f"Erreur dans l'analyse de corrélation: {e}")
            return None
    
    def get_processor_type(self) -> str:
        return "correlation"

class InsightGenerationManager:
    """Gestionnaire de génération d'insights ultra-avancé"""
    
    def __init__(self, config: InsightGenerationConfig):
        self.config = config
        self.redis_client = None
        self.is_running = False
        self.processors: Dict[str, InsightProcessor] = {}
        self.data_cache: deque = deque(maxlen=10000)
        self.insights_cache: Dict[str, Insight] = {}
        self.patterns_cache: Dict[str, Pattern] = {}
        self.rules_engine = None
        self.executor = ThreadPoolExecutor(max_workers=config.parallel_processors)
        self.insight_history = defaultdict(list)
        self.generation_stats = {
            'total_insights': 0,
            'insights_by_type': defaultdict(int),
            'insights_by_processor': defaultdict(int),
            'processing_time': []
        }
        
    async def initialize(self):
        """Initialise le gestionnaire d'insights"""
        try:
            self.redis_client = redis.from_url(
                self.config.redis_url,
                db=self.config.redis_db,
                decode_responses=True
            )
            
            # Test de connexion
            await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.ping
            )
            
            # Initialisation des processeurs
            await self._initialize_processors()
            
            # Chargement des règles personnalisées
            await self._load_custom_rules()
            
            # Chargement des données historiques
            await self._load_historical_data()
            
            self.is_running = True
            logger.info("Insight Generation Manager initialisé avec succès")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du gestionnaire d'insights: {e}")
            raise
    
    async def _initialize_processors(self):
        """Initialise les processeurs d'insights"""
        try:
            # Processeur statistique (toujours activé)
            self.processors['statistical'] = StatisticalInsightProcessor()
            
            # Processeur ML (si activé)
            if self.config.enable_ml_analysis:
                self.processors['machine_learning'] = MachineLearningInsightProcessor()
            
            # Processeur de corrélation (si activé)
            if self.config.enable_correlation_analysis:
                self.processors['correlation'] = CorrelationInsightProcessor()
            
            logger.info(f"Processeurs initialisés: {list(self.processors.keys())}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des processeurs: {e}")
            raise
    
    async def _load_custom_rules(self):
        """Charge les règles personnalisées"""
        try:
            # Implémentation des règles personnalisées
            for rule in self.config.custom_rules:
                if rule.enabled:
                    logger.info(f"Règle personnalisée chargée: {rule.name}")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des règles: {e}")
    
    async def _load_historical_data(self):
        """Charge les données historiques"""
        try:
            # Chargement des insights historiques depuis Redis
            historical_keys = await asyncio.get_event_loop().run_in_executor(
                None, self.redis_client.keys, "insight:*"
            )
            
            for key in historical_keys[-100:]:  # Derniers 100 insights
                try:
                    insight_data = await asyncio.get_event_loop().run_in_executor(
                        None, self.redis_client.get, key
                    )
                    
                    if insight_data:
                        insight_dict = json.loads(insight_data)
                        # Reconstruction de l'insight (simplifié)
                        self.insight_history[insight_dict.get('type', 'unknown')].append(insight_dict)
                        
                except Exception as e:
                    logger.warning(f"Erreur lors du chargement de l'insight {key}: {e}")
            
            logger.info(f"Données historiques chargées: {len(historical_keys)} insights")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données historiques: {e}")
    
    async def start_generation(self):
        """Démarre la génération d'insights"""
        if not self.is_running:
            await self.initialize()
        
        logger.info("Démarrage de la génération d'insights")
        
        # Démarrage des tâches
        tasks = [
            asyncio.create_task(self._data_collection_loop()),
            asyncio.create_task(self._insight_generation_loop()),
            asyncio.create_task(self._pattern_discovery_loop()),
            asyncio.create_task(self._cleanup_loop())
        ]
        
        await asyncio.gather(*tasks)
    
    async def _data_collection_loop(self):
        """Boucle de collecte de données"""
        while self.is_running:
            try:
                # Collecte de données depuis Redis
                new_data = await self._collect_data_from_redis()
                
                # Ajout au cache
                self.data_cache.extend(new_data)
                
                await asyncio.sleep(30)  # Collecte toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"Erreur dans la collecte de données: {e}")
                await asyncio.sleep(60)
    
    async def _insight_generation_loop(self):
        """Boucle principale de génération d'insights"""
        while self.is_running:
            try:
                start_time = time.time()
                
                # Vérification du minimum de données
                if len(self.data_cache) >= self.config.min_data_points:
                    # Génération d'insights avec tous les processeurs
                    new_insights = await self._generate_insights_batch()
                    
                    # Filtrage et stockage
                    filtered_insights = await self._filter_and_validate_insights(new_insights)
                    await self._store_insights(filtered_insights)
                    
                    # Mise à jour des statistiques
                    processing_time = time.time() - start_time
                    self.generation_stats['processing_time'].append(processing_time)
                    
                    if filtered_insights:
                        logger.info(f"Génération terminée: {len(filtered_insights)} insights en {processing_time:.2f}s")
                
                await asyncio.sleep(self.config.analysis_interval)
                
            except Exception as e:
                logger.error(f"Erreur dans la génération d'insights: {e}")
                await asyncio.sleep(60)
    
    async def _pattern_discovery_loop(self):
        """Boucle de découverte de patterns"""
        while self.is_running and self.config.enable_pattern_discovery:
            try:
                # Découverte de nouveaux patterns
                new_patterns = await self._discover_patterns()
                
                # Stockage des patterns
                for pattern in new_patterns:
                    self.patterns_cache[pattern.id] = pattern
                
                await asyncio.sleep(self.config.analysis_interval * 2)
                
            except Exception as e:
                logger.error(f"Erreur dans la découverte de patterns: {e}")
                await asyncio.sleep(120)
    
    async def _cleanup_loop(self):
        """Boucle de nettoyage"""
        while self.is_running:
            try:
                # Nettoyage des insights expirés
                await self._cleanup_expired_insights()
                
                # Nettoyage des patterns anciens
                await self._cleanup_old_patterns()
                
                # Nettoyage des statistiques
                await self._cleanup_statistics()
                
                await asyncio.sleep(3600)  # Nettoyage toutes les heures
                
            except Exception as e:
                logger.error(f"Erreur dans le nettoyage: {e}")
                await asyncio.sleep(1800)
    
    async def _collect_data_from_redis(self) -> List[DataPoint]:
        """Collecte les données depuis Redis"""
        try:
            data_points = []
            
            # Collecte depuis différentes sources Redis
            redis_sources = [
                "metrics:*",
                "analytics:*",
                "performance:*",
                "creator:*"
            ]
            
            for pattern in redis_sources:
                keys = await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.keys, pattern
                )
                
                for key in keys[-10:]:  # Dernières 10 clés par pattern
                    try:
                        value = await asyncio.get_event_loop().run_in_executor(
                            None, self.redis_client.get, key
                        )
                        
                        if value:
                            # Tentative de parsing JSON
                            try:
                                parsed_value = json.loads(value)
                                if isinstance(parsed_value, dict) and 'value' in parsed_value:
                                    data_points.append(DataPoint(
                                        id=f"{key}_{int(time.time())}",
                                        value=parsed_value['value'],
                                        timestamp=datetime.utcnow(),
                                        source=key.split(':')[0],
                                        metadata=parsed_value.get('metadata', {}),
                                        tags=parsed_value.get('tags', [])
                                    ))
                            except json.JSONDecodeError:
                                # Valeur simple
                                try:
                                    numeric_value = float(value)
                                    data_points.append(DataPoint(
                                        id=f"{key}_{int(time.time())}",
                                        value=numeric_value,
                                        timestamp=datetime.utcnow(),
                                        source=key.split(':')[0]
                                    ))
                                except ValueError:
                                    pass  # Ignorer les valeurs non-numériques
                                    
                    except Exception as e:
                        logger.warning(f"Erreur lors de la collecte de {key}: {e}")
            
            return data_points
            
        except Exception as e:
            logger.error(f"Erreur dans la collecte de données Redis: {e}")
            return []
    
    async def _generate_insights_batch(self) -> List[Insight]:
        """Génère un batch d'insights"""
        try:
            all_insights = []
            
            # Conversion du cache en liste pour le traitement
            data_list = list(self.data_cache)
            
            # Traitement avec chaque processeur
            tasks = []
            for processor_name, processor in self.processors.items():
                task = asyncio.create_task(self._process_with_processor(processor, data_list))
                tasks.append((processor_name, task))
            
            # Collecte des résultats
            for processor_name, task in tasks:
                try:
                    insights = await task
                    all_insights.extend(insights)
                    
                    # Mise à jour des statistiques
                    self.generation_stats['insights_by_processor'][processor_name] += len(insights)
                    
                except Exception as e:
                    logger.error(f"Erreur dans le processeur {processor_name}: {e}")
            
            return all_insights
            
        except Exception as e:
            logger.error(f"Erreur dans la génération du batch d'insights: {e}")
            return []
    
    async def _process_with_processor(self, processor: InsightProcessor, data: List[DataPoint]) -> List[Insight]:
        """Traite les données avec un processeur spécifique"""
        try:
            return await processor.process(data)
        except Exception as e:
            logger.error(f"Erreur dans le processeur {processor.get_processor_type()}: {e}")
            return []
    
    async def _filter_and_validate_insights(self, insights: List[Insight]) -> List[Insight]:
        """Filtre et valide les insights"""
        try:
            filtered_insights = []
            
            for insight in insights:
                # Filtrage par confiance
                if insight.confidence < self.config.confidence_threshold:
                    continue
                
                # Vérification des doublons
                if await self._is_duplicate_insight(insight):
                    continue
                
                # Validation de la structure
                if not await self._validate_insight_structure(insight):
                    continue
                
                filtered_insights.append(insight)
                
                # Limite par cycle
                if len(filtered_insights) >= self.config.max_insights_per_cycle:
                    break
            
            return filtered_insights
            
        except Exception as e:
            logger.error(f"Erreur dans le filtrage des insights: {e}")
            return []
    
    async def _is_duplicate_insight(self, insight: Insight) -> bool:
        """Vérifie si l'insight est un doublon"""
        try:
            # Vérification simple basée sur le type et les sources
            for existing_insight in self.insights_cache.values():
                if (existing_insight.type == insight.type and
                    existing_insight.data_sources == insight.data_sources and
                    abs((existing_insight.created_at - insight.created_at).total_seconds()) < 3600):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Erreur dans la vérification de doublon: {e}")
            return False
    
    async def _validate_insight_structure(self, insight: Insight) -> bool:
        """Valide la structure d'un insight"""
        try:
            # Vérifications basiques
            if not insight.title or not insight.description:
                return False
            
            if insight.confidence < 0 or insight.confidence > 1:
                return False
            
            if insight.impact_score < 0:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur dans la validation de structure: {e}")
            return False
    
    async def _store_insights(self, insights: List[Insight]):
        """Stocke les insights"""
        try:
            for insight in insights:
                # Stockage en cache
                self.insights_cache[insight.id] = insight
                
                # Stockage dans Redis
                insight_data = {
                    'id': insight.id,
                    'title': insight.title,
                    'description': insight.description,
                    'type': insight.type.value,
                    'category': insight.category.value,
                    'priority': insight.priority.value,
                    'confidence': insight.confidence,
                    'impact_score': insight.impact_score,
                    'actionable': insight.actionable,
                    'evidence': insight.evidence,
                    'recommendations': insight.recommendations,
                    'data_sources': insight.data_sources,
                    'analysis_method': insight.analysis_method.value,
                    'keywords': insight.keywords,
                    'created_at': insight.created_at.isoformat()
                }
                
                insight_key = f"insight:{insight.id}"
                ttl = 86400 * self.config.data_retention_days  # TTL en secondes
                
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.redis_client.setex,
                    insight_key,
                    ttl,
                    json.dumps(insight_data)
                )
                
                # Mise à jour des statistiques
                self.generation_stats['total_insights'] += 1
                self.generation_stats['insights_by_type'][insight.type.value] += 1
                
                logger.debug(f"Insight stocké: {insight.id}")
            
        except Exception as e:
            logger.error(f"Erreur lors du stockage des insights: {e}")
    
    async def _discover_patterns(self) -> List[Pattern]:
        """Découvre de nouveaux patterns"""
        try:
            patterns = []
            
            if len(self.data_cache) < 20:
                return patterns
            
            # Analyse des patterns temporels
            temporal_patterns = await self._discover_temporal_patterns()
            patterns.extend(temporal_patterns)
            
            # Analyse des patterns de valeurs
            value_patterns = await self._discover_value_patterns()
            patterns.extend(value_patterns)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Erreur dans la découverte de patterns: {e}")
            return []
    
    async def _discover_temporal_patterns(self) -> List[Pattern]:
        """Découvre les patterns temporels"""
        try:
            patterns = []
            
            # Groupement par heure
            hourly_data = defaultdict(list)
            for point in self.data_cache:
                hour = point.timestamp.hour
                if isinstance(point.value, (int, float)):
                    hourly_data[hour].append(point.value)
            
            # Recherche de patterns d'activité
            for hour, values in hourly_data.items():
                if len(values) >= 5:
                    avg_value = np.mean(values)
                    
                    # Pattern d'activité élevée
                    if avg_value > np.mean([np.mean(v) for v in hourly_data.values() if v]) * 1.5:
                        patterns.append(Pattern(
                            id=f"high_activity_h{hour}_{int(time.time())}",
                            name=f"Activité élevée à {hour}h",
                            description=f"Pattern d'activité élevée détecté à {hour}h (moyenne: {avg_value:.2f})",
                            type="temporal_high_activity",
                            confidence=0.8,
                            support=len(values) / len(self.data_cache),
                            parameters={
                                'hour': hour,
                                'average_value': avg_value,
                                'sample_count': len(values)
                            }
                        ))
            
            return patterns
            
        except Exception as e:
            logger.error(f"Erreur dans la découverte de patterns temporels: {e}")
            return []
    
    async def _discover_value_patterns(self) -> List[Pattern]:
        """Découvre les patterns de valeurs"""
        try:
            patterns = []
            
            # Groupement par source
            source_data = defaultdict(list)
            for point in self.data_cache:
                if isinstance(point.value, (int, float)):
                    source_data[point.source].append(point.value)
            
            # Recherche de patterns de stabilité
            for source, values in source_data.items():
                if len(values) >= 10:
                    coefficient_variation = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
                    
                    # Pattern de stabilité
                    if coefficient_variation < 0.1:
                        patterns.append(Pattern(
                            id=f"stability_{source}_{int(time.time())}",
                            name=f"Stabilité dans {source}",
                            description=f"Pattern de stabilité détecté dans {source} (CV: {coefficient_variation:.3f})",
                            type="value_stability",
                            confidence=0.9,
                            support=len(values) / len(self.data_cache),
                            parameters={
                                'source': source,
                                'coefficient_variation': coefficient_variation,
                                'mean_value': np.mean(values),
                                'sample_count': len(values)
                            }
                        ))
            
            return patterns
            
        except Exception as e:
            logger.error(f"Erreur dans la découverte de patterns de valeurs: {e}")
            return []
    
    async def _cleanup_expired_insights(self):
        """Nettoie les insights expirés"""
        try:
            current_time = datetime.utcnow()
            expired_insights = []
            
            for insight_id, insight in self.insights_cache.items():
                if insight.expires_at and insight.expires_at < current_time:
                    expired_insights.append(insight_id)
            
            for insight_id in expired_insights:
                del self.insights_cache[insight_id]
                
                # Suppression de Redis
                await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.delete, f"insight:{insight_id}"
                )
            
            if expired_insights:
                logger.info(f"Nettoyage: {len(expired_insights)} insights expirés supprimés")
            
        except Exception as e:
            logger.error(f"Erreur dans le nettoyage des insights expirés: {e}")
    
    async def _cleanup_old_patterns(self):
        """Nettoie les anciens patterns"""
        try:
            current_time = datetime.utcnow()
            old_patterns = []
            
            for pattern_id, pattern in self.patterns_cache.items():
                age = current_time - pattern.discovered_at
                if age > timedelta(days=7):  # Patterns plus anciens que 7 jours
                    old_patterns.append(pattern_id)
            
            for pattern_id in old_patterns:
                del self.patterns_cache[pattern_id]
            
            if old_patterns:
                logger.info(f"Nettoyage: {len(old_patterns)} anciens patterns supprimés")
            
        except Exception as e:
            logger.error(f"Erreur dans le nettoyage des patterns: {e}")
    
    async def _cleanup_statistics(self):
        """Nettoie les statistiques anciennes"""
        try:
            # Garde seulement les 1000 derniers temps de traitement
            if len(self.generation_stats['processing_time']) > 1000:
                self.generation_stats['processing_time'] = self.generation_stats['processing_time'][-1000:]
            
        except Exception as e:
            logger.error(f"Erreur dans le nettoyage des statistiques: {e}")
    
    async def get_insights(self, 
                          insight_type: Optional[InsightType] = None,
                          category: Optional[InsightCategory] = None,
                          priority: Optional[InsightPriority] = None,
                          limit: int = 100) -> List[Insight]:
        """Récupère les insights avec filtres"""
        try:
            insights = list(self.insights_cache.values())
            
            # Filtrage
            if insight_type:
                insights = [i for i in insights if i.type == insight_type]
            
            if category:
                insights = [i for i in insights if i.category == category]
            
            if priority:
                insights = [i for i in insights if i.priority == priority]
            
            # Tri par timestamp décroissant
            insights.sort(key=lambda x: x.created_at, reverse=True)
            
            return insights[:limit]
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des insights: {e}")
            return []
    
    async def get_patterns(self, pattern_type: Optional[str] = None) -> List[Pattern]:
        """Récupère les patterns découverts"""
        try:
            patterns = list(self.patterns_cache.values())
            
            if pattern_type:
                patterns = [p for p in patterns if p.type == pattern_type]
            
            # Tri par confiance décroissante
            patterns.sort(key=lambda x: x.confidence, reverse=True)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des patterns: {e}")
            return []
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Récupère les statistiques de génération"""
        try:
            stats = dict(self.generation_stats)
            
            # Ajout de statistiques calculées
            if stats['processing_time']:
                stats['avg_processing_time'] = np.mean(stats['processing_time'])
                stats['max_processing_time'] = max(stats['processing_time'])
                stats['min_processing_time'] = min(stats['processing_time'])
            
            stats['active_insights'] = len(self.insights_cache)
            stats['active_patterns'] = len(self.patterns_cache)
            stats['data_cache_size'] = len(self.data_cache)
            stats['active_processors'] = list(self.processors.keys())
            
            return stats
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques: {e}")
            return {}
    
    async def generate_custom_insight(self, data: List[DataPoint], 
                                    processor_type: str = "statistical") -> List[Insight]:
        """Génère des insights personnalisés"""
        try:
            if processor_type in self.processors:
                processor = self.processors[processor_type]
                return await processor.process(data)
            else:
                logger.warning(f"Processeur {processor_type} non disponible")
                return []
            
        except Exception as e:
            logger.error(f"Erreur dans la génération d'insight personnalisé: {e}")
            return []
    
    async def add_data_point(self, data_point: DataPoint):
        """Ajoute un point de données"""
        try:
            self.data_cache.append(data_point)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du point de données: {e}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Récupère le statut de santé du gestionnaire"""
        try:
            return {
                'status': 'healthy' if self.is_running else 'stopped',
                'redis_connected': self.redis_client is not None,
                'active_processors': len(self.processors),
                'data_cache_size': len(self.data_cache),
                'insights_count': len(self.insights_cache),
                'patterns_count': len(self.patterns_cache),
                'total_insights_generated': self.generation_stats['total_insights'],
                'last_processing_time': self.generation_stats['processing_time'][-1] if self.generation_stats['processing_time'] else 0,
                'last_update': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut de santé: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def stop(self):
        """Arrête le gestionnaire d'insights"""
        try:
            self.is_running = False
            
            if self.executor:
                self.executor.shutdown(wait=True)
            
            if self.redis_client:
                self.redis_client.close()
            
            logger.info("Insight Generation Manager arrêté")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt du gestionnaire: {e}")

# Factory function pour créer le gestionnaire d'insights
def create_insight_generation_manager(config: Optional[InsightGenerationConfig] = None) -> InsightGenerationManager:
    """Crée une instance du gestionnaire de génération d'insights"""
    if config is None:
        config = InsightGenerationConfig()
    
    return InsightGenerationManager(config)

# Export des classes principales
__all__ = [
    'InsightGenerationManager',
    'InsightGenerationConfig',
    'Insight',
    'Pattern',
    'Correlation',
    'DataPoint',
    'InsightRule',
    'InsightProcessor',
    'StatisticalInsightProcessor',
    'MachineLearningInsightProcessor',
    'CorrelationInsightProcessor',
    'InsightType',
    'InsightCategory',
    'InsightPriority',
    'InsightConfidence',
    'AnalysisMethod',
    'create_insight_generation_manager'
]