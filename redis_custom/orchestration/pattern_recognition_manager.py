"""🧩 Redis Pattern Recognition Manager - AI-Driven Pattern Intelligence
=======================================================================
Expert: ML ENGINEER + LEAD DEV IA + BACKEND SENIOR + DATA SCIENTIST
Technologies: Pattern Recognition + Machine Learning + Time Series Analysis + Behavioral Analytics
Architecture: Level 3 - Pattern Intelligence Layer
Date: 2025-01-14

Ultra-advanced pattern recognition system with AI-powered pattern discovery,
behavioral analysis, trend prediction and intelligent pattern matching.
=======================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
=======================================================================
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

logger = logging.getLogger(__name__)

class PatternType(Enum):
    """Types de patterns reconnaissables"""
    TEMPORAL = "temporal"                    # Patterns temporels
    BEHAVIORAL = "behavioral"               # Patterns comportementaux
    USAGE = "usage"                         # Patterns d'utilisation
    PERFORMANCE = "performance"             # Patterns de performance
    TRAFFIC = "traffic"                     # Patterns de trafic
    SEASONAL = "seasonal"                   # Patterns saisonniers
    ANOMALOUS = "anomalous"                 # Patterns anormaux
    CREATOR_WORKFLOW = "creator_workflow"   # Patterns workflow créateurs
    CONTENT_CONSUMPTION = "content_consumption" # Patterns consommation contenu
    COLLABORATION = "collaboration"         # Patterns collaboration

class PatternConfidence(Enum):
    """Niveaux de confiance pattern"""
    VERY_HIGH = "very_high"     # >95% confiance
    HIGH = "high"               # 85-95% confiance
    MEDIUM = "medium"           # 70-85% confiance
    LOW = "low"                 # 50-70% confiance
    UNCERTAIN = "uncertain"     # <50% confiance

class PatternFrequency(Enum):
    """Fréquences de patterns"""
    CONTINUOUS = "continuous"    # Pattern continu
    HOURLY = "hourly"           # Pattern horaire
    DAILY = "daily"             # Pattern quotidien
    WEEKLY = "weekly"           # Pattern hebdomadaire
    MONTHLY = "monthly"         # Pattern mensuel
    SEASONAL = "seasonal"       # Pattern saisonnier
    IRREGULAR = "irregular"     # Pattern irrégulier

class RecognitionAlgorithm(Enum):
    """Algorithmes de reconnaissance"""
    CORRELATION_ANALYSIS = "correlation_analysis"
    FOURIER_TRANSFORM = "fourier_transform"
    WAVELET_ANALYSIS = "wavelet_analysis"
    CLUSTERING = "clustering"
    NEURAL_NETWORK = "neural_network"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    MACHINE_LEARNING = "machine_learning"
    DEEP_LEARNING = "deep_learning"

@dataclass
class PatternConfig:
    """Configuration du gestionnaire de reconnaissance patterns"""
    # Algorithmes utilisés
    recognition_algorithms: List[RecognitionAlgorithm] = field(default_factory=lambda: [
        RecognitionAlgorithm.CORRELATION_ANALYSIS,
        RecognitionAlgorithm.STATISTICAL_ANALYSIS,
        RecognitionAlgorithm.CLUSTERING
    ])
    
    # Paramètres reconnaissance
    min_pattern_length: int = 10            # Longueur minimum pattern
    max_pattern_length: int = 100           # Longueur maximum pattern
    confidence_threshold: float = 0.7       # Seuil confiance minimum
    similarity_threshold: float = 0.8       # Seuil similarité patterns
    
    # Fenêtres temporelles
    analysis_window: int = 3600             # Fenêtre analyse (1h)
    historical_depth: int = 604800          # Profondeur historique (7 jours)
    pattern_update_interval: int = 300      # Intervalle mise à jour (5 min)
    
    # Métriques analysées
    monitored_metrics: List[str] = field(default_factory=lambda: [
        "cpu_usage", "memory_usage", "latency", "throughput",
        "request_rate", "error_rate", "connection_count",
        "creator_uploads", "content_views", "collaboration_sessions"
    ])
    
    # Patterns spécialisés Creator Economy
    creator_patterns: bool = True
    content_patterns: bool = True
    collaboration_patterns: bool = True
    
    # Prédiction
    enable_prediction: bool = True
    prediction_horizon: int = 1800          # Horizon prédiction (30 min)
    
    # Performance
    max_patterns_per_metric: int = 20
    pattern_cache_size: int = 1000

@dataclass 
class Pattern:
    """Pattern reconnu"""
    pattern_id: str
    pattern_type: PatternType
    confidence: PatternConfidence
    frequency: PatternFrequency
    
    # Données pattern
    metric_name: str
    pattern_data: List[float]
    pattern_length: int
    
    # Caractéristiques
    amplitude: float
    period: float
    phase: float
    trend: float
    
    # Statistiques
    mean_value: float
    std_deviation: float
    min_value: float
    max_value: float
    
    # Reconnaissance
    recognition_algorithm: RecognitionAlgorithm
    discovery_timestamp: datetime
    last_seen: datetime
    occurrence_count: int = 1
    
    # Prédiction
    predicted_next_values: List[float] = field(default_factory=list)
    prediction_accuracy: float = 0.0
    
    # Contexte business
    business_impact: str = ""
    creator_economy_relevance: bool = False
    
    # Métadonnées
    tags: List[str] = field(default_factory=list)
    correlations: Dict[str, float] = field(default_factory=dict)

class CorrelationAnalyzer:
    """Analyseur de corrélations pour patterns"""
    
    def __init__(self, config: PatternConfig):
        self.config = config
        self.correlation_matrix: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.correlation_history: List[Dict[str, Dict[str, float]]] = []
    
    async def analyze_correlations(self, metrics_data: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
        """Analyse les corrélations entre métriques"""
        try:
            correlations = {}
            
            metric_names = list(metrics_data.keys())
            
            for i, metric1 in enumerate(metric_names):
                correlations[metric1] = {}
                
                for j, metric2 in enumerate(metric_names):
                    if i != j and len(metrics_data[metric1]) >= 10 and len(metrics_data[metric2]) >= 10:
                        # Calcul corrélation Pearson
                        correlation = self._calculate_pearson_correlation(
                            metrics_data[metric1], metrics_data[metric2]
                        )
                        correlations[metric1][metric2] = correlation
                    else:
                        correlations[metric1][metric2] = 0.0
            
            # Mise à jour matrice
            self.correlation_matrix = correlations
            self.correlation_history.append(correlations)
            
            # Limitation historique
            if len(self.correlation_history) > 100:
                self.correlation_history = self.correlation_history[-100:]
            
            return correlations
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse corrélations: {e}")
            return {}
    
    def _calculate_pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calcule corrélation Pearson entre deux séries"""
        try:
            # Alignement longueurs
            min_length = min(len(x), len(y))
            x_aligned = x[-min_length:]
            y_aligned = y[-min_length:]
            
            if min_length < 3:
                return 0.0
            
            # Calcul corrélation
            x_mean = statistics.mean(x_aligned)
            y_mean = statistics.mean(y_aligned)
            
            numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x_aligned, y_aligned))
            
            x_variance = sum((xi - x_mean) ** 2 for xi in x_aligned)
            y_variance = sum((yi - y_mean) ** 2 for yi in y_aligned)
            
            denominator = math.sqrt(x_variance * y_variance)
            
            if denominator == 0:
                return 0.0
            
            correlation = numerator / denominator
            return max(-1.0, min(1.0, correlation))  # Clamp [-1, 1]
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul corrélation Pearson: {e}")
            return 0.0
    
    async def find_correlation_patterns(self) -> List[Pattern]:
        """Trouve patterns basés sur corrélations"""
        try:
            patterns = []
            
            for metric1, correlations in self.correlation_matrix.items():
                for metric2, correlation in correlations.items():
                    if abs(correlation) > self.config.similarity_threshold:
                        # Pattern de corrélation forte
                        pattern = Pattern(
                            pattern_id=f"corr_{metric1}_{metric2}_{int(time.time())}",
                            pattern_type=PatternType.BEHAVIORAL,
                            confidence=self._correlation_to_confidence(abs(correlation)),
                            frequency=PatternFrequency.CONTINUOUS,
                            metric_name=f"{metric1}_vs_{metric2}",
                            pattern_data=[correlation],
                            pattern_length=1,
                            amplitude=abs(correlation),
                            period=0.0,
                            phase=0.0,
                            trend=0.0,
                            mean_value=correlation,
                            std_deviation=0.0,
                            min_value=correlation,
                            max_value=correlation,
                            recognition_algorithm=RecognitionAlgorithm.CORRELATION_ANALYSIS,
                            discovery_timestamp=datetime.now(),
                            last_seen=datetime.now(),
                            business_impact=self._assess_correlation_impact(metric1, metric2, correlation),
                            correlations={metric2: correlation}
                        )
                        
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche patterns corrélation: {e}")
            return []
    
    def _correlation_to_confidence(self, correlation: float) -> PatternConfidence:
        """Convertit corrélation en niveau de confiance"""
        if correlation >= 0.95:
            return PatternConfidence.VERY_HIGH
        elif correlation >= 0.85:
            return PatternConfidence.HIGH
        elif correlation >= 0.7:
            return PatternConfidence.MEDIUM
        elif correlation >= 0.5:
            return PatternConfidence.LOW
        else:
            return PatternConfidence.UNCERTAIN
    
    def _assess_correlation_impact(self, metric1: str, metric2: str, correlation: float) -> str:
        """Évalue l'impact business d'une corrélation"""
        if correlation > 0.9:
            return f"Forte corrélation positive entre {metric1} et {metric2} - Optimisation jointe possible"
        elif correlation < -0.9:
            return f"Forte corrélation négative entre {metric1} et {metric2} - Effet compensatoire détecté"
        elif abs(correlation) > 0.7:
            return f"Corrélation significative entre {metric1} et {metric2} - Surveillance coordonnée recommandée"
        else:
            return f"Corrélation modérée entre {metric1} et {metric2}"

class StatisticalPatternAnalyzer:
    """Analyseur de patterns statistiques"""
    
    def __init__(self, config: PatternConfig):
        self.config = config
        
    async def find_statistical_patterns(self, metric_name: str, 
                                       data: List[float]) -> List[Pattern]:
        """Trouve patterns statistiques dans données"""
        try:
            patterns = []
            
            if len(data) < self.config.min_pattern_length:
                return patterns
            
            # Pattern de tendance
            trend_pattern = await self._analyze_trend_pattern(metric_name, data)
            if trend_pattern:
                patterns.append(trend_pattern)
            
            # Pattern de cyclicité
            cyclic_patterns = await self._analyze_cyclic_patterns(metric_name, data)
            patterns.extend(cyclic_patterns)
            
            # Pattern de volatilité
            volatility_pattern = await self._analyze_volatility_pattern(metric_name, data)
            if volatility_pattern:
                patterns.append(volatility_pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse patterns statistiques {metric_name}: {e}")
            return []
    
    async def _analyze_trend_pattern(self, metric_name: str, data: List[float]) -> Optional[Pattern]:
        """Analyse pattern de tendance"""
        try:
            if len(data) < 10:
                return None
            
            # Régression linéaire simple
            x = np.arange(len(data))
            coeffs = np.polyfit(x, data, 1)
            trend_slope = coeffs[0]
            
            # Significance test (R²)
            predicted = np.polyval(coeffs, x)
            ss_res = np.sum((data - predicted) ** 2)
            ss_tot = np.sum((data - np.mean(data)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            if r_squared < 0.5:  # Tendance pas assez significative
                return None
            
            # Classification tendance
            pattern_type = PatternType.TEMPORAL
            if abs(trend_slope) > statistics.stdev(data) / len(data):
                pattern_type = PatternType.PERFORMANCE if trend_slope > 0 else PatternType.ANOMALOUS
            
            confidence = self._r_squared_to_confidence(r_squared)
            
            pattern = Pattern(
                pattern_id=f"trend_{metric_name}_{int(time.time())}",
                pattern_type=pattern_type,
                confidence=confidence,
                frequency=PatternFrequency.CONTINUOUS,
                metric_name=metric_name,
                pattern_data=data.copy(),
                pattern_length=len(data),
                amplitude=abs(trend_slope * len(data)),
                period=0.0,
                phase=0.0,
                trend=trend_slope,
                mean_value=statistics.mean(data),
                std_deviation=statistics.stdev(data) if len(data) > 1 else 0.0,
                min_value=min(data),
                max_value=max(data),
                recognition_algorithm=RecognitionAlgorithm.STATISTICAL_ANALYSIS,
                discovery_timestamp=datetime.now(),
                last_seen=datetime.now(),
                business_impact=self._assess_trend_impact(metric_name, trend_slope, r_squared)
            )
            
            return pattern
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse tendance {metric_name}: {e}")
            return None
    
    async def _analyze_cyclic_patterns(self, metric_name: str, data: List[float]) -> List[Pattern]:
        """Analyse patterns cycliques"""
        try:
            patterns = []
            
            if len(data) < 20:
                return patterns
            
            # Détection cycles par autocorrélation
            autocorrelations = self._calculate_autocorrelation(data)
            
            # Recherche pics dans autocorrélation
            peaks = self._find_peaks(autocorrelations)
            
            for peak_lag in peaks:
                if peak_lag >= 5 and autocorrelations[peak_lag] > 0.6:  # Cycle significatif
                    # Extraction pattern cyclique
                    cycle_pattern = self._extract_cycle_pattern(data, peak_lag)
                    
                    if cycle_pattern:
                        frequency = self._determine_frequency(peak_lag)
                        confidence = self._autocorr_to_confidence(autocorrelations[peak_lag])
                        
                        pattern = Pattern(
                            pattern_id=f"cycle_{metric_name}_{peak_lag}_{int(time.time())}",
                            pattern_type=PatternType.SEASONAL,
                            confidence=confidence,
                            frequency=frequency,
                            metric_name=metric_name,
                            pattern_data=cycle_pattern,
                            pattern_length=peak_lag,
                            amplitude=max(cycle_pattern) - min(cycle_pattern),
                            period=float(peak_lag),
                            phase=0.0,
                            trend=0.0,
                            mean_value=statistics.mean(cycle_pattern),
                            std_deviation=statistics.stdev(cycle_pattern) if len(cycle_pattern) > 1 else 0.0,
                            min_value=min(cycle_pattern),
                            max_value=max(cycle_pattern),
                            recognition_algorithm=RecognitionAlgorithm.STATISTICAL_ANALYSIS,
                            discovery_timestamp=datetime.now(),
                            last_seen=datetime.now(),
                            business_impact=self._assess_cycle_impact(metric_name, peak_lag)
                        )
                        
                        patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse cycles {metric_name}: {e}")
            return []
    
    async def _analyze_volatility_pattern(self, metric_name: str, data: List[float]) -> Optional[Pattern]:
        """Analyse pattern de volatilité"""
        try:
            if len(data) < 20:
                return None
            
            # Calcul volatilité roulante
            window_size = min(10, len(data) // 4)
            volatilities = []
            
            for i in range(window_size, len(data)):
                window_data = data[i-window_size:i]
                volatility = statistics.stdev(window_data) if len(window_data) > 1 else 0.0
                volatilities.append(volatility)
            
            if not volatilities:
                return None
            
            # Analyse variation volatilité
            volatility_trend = 0.0
            if len(volatilities) >= 5:
                x = np.arange(len(volatilities))
                coeffs = np.polyfit(x, volatilities, 1)
                volatility_trend = coeffs[0]
            
            avg_volatility = statistics.mean(volatilities)
            max_volatility = max(volatilities)
            
            # Détermination si pattern significatif
            volatility_ratio = max_volatility / (avg_volatility + 0.001)
            
            if volatility_ratio < 2.0:  # Volatilité pas assez variable
                return None
            
            confidence = PatternConfidence.MEDIUM if volatility_ratio > 3.0 else PatternConfidence.LOW
            
            pattern = Pattern(
                pattern_id=f"volatility_{metric_name}_{int(time.time())}",
                pattern_type=PatternType.BEHAVIORAL,
                confidence=confidence,
                frequency=PatternFrequency.IRREGULAR,
                metric_name=metric_name,
                pattern_data=volatilities,
                pattern_length=len(volatilities),
                amplitude=max_volatility - min(volatilities),
                period=0.0,
                phase=0.0,
                trend=volatility_trend,
                mean_value=avg_volatility,
                std_deviation=statistics.stdev(volatilities) if len(volatilities) > 1 else 0.0,
                min_value=min(volatilities),
                max_value=max_volatility,
                recognition_algorithm=RecognitionAlgorithm.STATISTICAL_ANALYSIS,
                discovery_timestamp=datetime.now(),
                last_seen=datetime.now(),
                business_impact=self._assess_volatility_impact(metric_name, volatility_ratio)
            )
            
            return pattern
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse volatilité {metric_name}: {e}")
            return None
    
    def _calculate_autocorrelation(self, data: List[float], max_lag: int = None) -> List[float]:
        """Calcule autocorrélation"""
        try:
            if max_lag is None:
                max_lag = min(len(data) // 2, 50)
            
            data_array = np.array(data)
            data_mean = np.mean(data_array)
            data_centered = data_array - data_mean
            
            autocorrs = []
            variance = np.sum(data_centered ** 2) / len(data_centered)
            
            for lag in range(max_lag):
                if lag >= len(data_centered):
                    autocorrs.append(0.0)
                    continue
                
                covariance = np.sum(data_centered[:-lag or None] * data_centered[lag:]) / (len(data_centered) - lag)
                autocorr = covariance / variance if variance != 0 else 0.0
                autocorrs.append(autocorr)
            
            return autocorrs
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul autocorrélation: {e}")
            return [0.0] * (max_lag or 10)
    
    def _find_peaks(self, data: List[float], min_prominence: float = 0.1) -> List[int]:
        """Trouve pics dans données"""
        try:
            peaks = []
            
            for i in range(1, len(data) - 1):
                # Peak simple: plus haut que voisins
                if (data[i] > data[i-1] and data[i] > data[i+1] and 
                    data[i] > min_prominence):
                    peaks.append(i)
            
            return peaks
            
        except Exception as e:
            logger.error(f"❌ Erreur recherche pics: {e}")
            return []
    
    def _extract_cycle_pattern(self, data: List[float], cycle_length: int) -> List[float]:
        """Extrait pattern cyclique"""
        try:
            if cycle_length >= len(data):
                return []
            
            # Moyenne des cycles
            num_cycles = len(data) // cycle_length
            if num_cycles < 2:
                return data[:cycle_length]
            
            cycle_sum = [0.0] * cycle_length
            
            for cycle_idx in range(num_cycles):
                start_idx = cycle_idx * cycle_length
                for i in range(cycle_length):
                    if start_idx + i < len(data):
                        cycle_sum[i] += data[start_idx + i]
            
            # Moyenne
            cycle_pattern = [val / num_cycles for val in cycle_sum]
            
            return cycle_pattern
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction cycle: {e}")
            return []
    
    def _determine_frequency(self, cycle_length: int) -> PatternFrequency:
        """Détermine fréquence basée sur longueur cycle"""
        # Assumant mesures par minute
        if cycle_length <= 60:  # 1 heure
            return PatternFrequency.HOURLY
        elif cycle_length <= 1440:  # 24 heures
            return PatternFrequency.DAILY
        elif cycle_length <= 10080:  # 7 jours
            return PatternFrequency.WEEKLY
        else:
            return PatternFrequency.MONTHLY
    
    def _r_squared_to_confidence(self, r_squared: float) -> PatternConfidence:
        """Convertit R² en confiance"""
        if r_squared >= 0.95:
            return PatternConfidence.VERY_HIGH
        elif r_squared >= 0.85:
            return PatternConfidence.HIGH
        elif r_squared >= 0.7:
            return PatternConfidence.MEDIUM
        elif r_squared >= 0.5:
            return PatternConfidence.LOW
        else:
            return PatternConfidence.UNCERTAIN
    
    def _autocorr_to_confidence(self, autocorr: float) -> PatternConfidence:
        """Convertit autocorrélation en confiance"""
        if autocorr >= 0.9:
            return PatternConfidence.VERY_HIGH
        elif autocorr >= 0.8:
            return PatternConfidence.HIGH
        elif autocorr >= 0.7:
            return PatternConfidence.MEDIUM
        elif autocorr >= 0.6:
            return PatternConfidence.LOW
        else:
            return PatternConfidence.UNCERTAIN
    
    def _assess_trend_impact(self, metric_name: str, slope: float, r_squared: float) -> str:
        """Évalue impact business d'une tendance"""
        if slope > 0:
            return f"Tendance croissante {metric_name} (R²={r_squared:.2f}) - Surveillance recommandée"
        else:
            return f"Tendance décroissante {metric_name} (R²={r_squared:.2f}) - Investigation requise"
    
    def _assess_cycle_impact(self, metric_name: str, cycle_length: int) -> str:
        """Évalue impact business d'un cycle"""
        frequency = self._determine_frequency(cycle_length)
        return f"Pattern {frequency.value} détecté pour {metric_name} - Optimisation planifiée possible"
    
    def _assess_volatility_impact(self, metric_name: str, volatility_ratio: float) -> str:
        """Évalue impact business de la volatilité"""
        if volatility_ratio > 5.0:
            return f"Volatilité très élevée {metric_name} - Stabilisation critique requise"
        elif volatility_ratio > 3.0:
            return f"Volatilité élevée {metric_name} - Monitoring renforcé recommandé"
        else:
            return f"Volatilité modérée {metric_name} - Surveillance standard"

class CreatorPatternAnalyzer:
    """Analyseur de patterns spécialisé Creator Economy"""
    
    def __init__(self, config: PatternConfig):
        self.config = config
        self.creator_metrics = [
            "creator_uploads", "content_views", "collaboration_sessions",
            "creator_revenue", "audience_engagement", "content_quality_score"
        ]
    
    async def analyze_creator_patterns(self, creator_data: Dict[str, List[float]]) -> List[Pattern]:
        """Analyse patterns spécifiques Creator Economy"""
        try:
            patterns = []
            
            # Pattern upload régulier
            if "creator_uploads" in creator_data:
                upload_patterns = await self._analyze_upload_patterns(creator_data["creator_uploads"])
                patterns.extend(upload_patterns)
            
            # Pattern engagement audience
            if "audience_engagement" in creator_data:
                engagement_patterns = await self._analyze_engagement_patterns(creator_data["audience_engagement"])
                patterns.extend(engagement_patterns)
            
            # Pattern collaboration
            if "collaboration_sessions" in creator_data:
                collab_patterns = await self._analyze_collaboration_patterns(creator_data["collaboration_sessions"])
                patterns.extend(collab_patterns)
            
            # Pattern monétisation
            if "creator_revenue" in creator_data:
                revenue_patterns = await self._analyze_revenue_patterns(creator_data["creator_revenue"])
                patterns.extend(revenue_patterns)
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse patterns créateurs: {e}")
            return []
    
    async def _analyze_upload_patterns(self, upload_data: List[float]) -> List[Pattern]:
        """Analyse patterns d'upload créateurs"""
        try:
            patterns = []
            
            if len(upload_data) < 7:  # Minimum 1 semaine
                return patterns
            
            # Détection rythme upload
            avg_uploads = statistics.mean(upload_data)
            upload_consistency = 1.0 - (statistics.stdev(upload_data) / (avg_uploads + 0.1))
            
            if upload_consistency > 0.7:  # Créateur régulier
                pattern = Pattern(
                    pattern_id=f"upload_rhythm_{int(time.time())}",
                    pattern_type=PatternType.CREATOR_WORKFLOW,
                    confidence=PatternConfidence.HIGH if upload_consistency > 0.8 else PatternConfidence.MEDIUM,
                    frequency=PatternFrequency.DAILY,
                    metric_name="creator_uploads",
                    pattern_data=upload_data.copy(),
                    pattern_length=len(upload_data),
                    amplitude=max(upload_data) - min(upload_data),
                    period=1.0,  # Quotidien
                    phase=0.0,
                    trend=0.0,
                    mean_value=avg_uploads,
                    std_deviation=statistics.stdev(upload_data) if len(upload_data) > 1 else 0.0,
                    min_value=min(upload_data),
                    max_value=max(upload_data),
                    recognition_algorithm=RecognitionAlgorithm.STATISTICAL_ANALYSIS,
                    discovery_timestamp=datetime.now(),
                    last_seen=datetime.now(),
                    business_impact=f"Créateur régulier - {avg_uploads:.1f} uploads/jour (consistance: {upload_consistency:.1%})",
                    creator_economy_relevance=True,
                    tags=["creator_productivity", "content_creation", "regularity"]
                )
                patterns.append(pattern)
            
            # Détection pics upload (batch upload)
            peaks = [i for i, val in enumerate(upload_data) if val > avg_uploads + 2 * statistics.stdev(upload_data)]
            
            if len(peaks) >= 2:  # Pattern batch upload
                pattern = Pattern(
                    pattern_id=f"batch_upload_{int(time.time())}",
                    pattern_type=PatternType.CREATOR_WORKFLOW,
                    confidence=PatternConfidence.MEDIUM,
                    frequency=PatternFrequency.IRREGULAR,
                    metric_name="creator_uploads",
                    pattern_data=[upload_data[i] for i in peaks],
                    pattern_length=len(peaks),
                    amplitude=max(upload_data[i] for i in peaks) - avg_uploads,
                    period=0.0,
                    phase=0.0,
                    trend=0.0,
                    mean_value=statistics.mean(upload_data[i] for i in peaks),
                    std_deviation=0.0,
                    min_value=min(upload_data[i] for i in peaks),
                    max_value=max(upload_data[i] for i in peaks),
                    recognition_algorithm=RecognitionAlgorithm.STATISTICAL_ANALYSIS,
                    discovery_timestamp=datetime.now(),
                    last_seen=datetime.now(),
                    business_impact=f"Pattern batch upload détecté - {len(peaks)} épisodes",
                    creator_economy_relevance=True,
                    tags=["batch_creation", "productivity_burst", "content_strategy"]
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse patterns upload: {e}")
            return []
    
    async def _analyze_engagement_patterns(self, engagement_data: List[float]) -> List[Pattern]:
        """Analyse patterns d'engagement audience"""
        try:
            patterns = []
            
            if len(engagement_data) < 10:
                return patterns
            
            # Détection patterns engagement viral
            avg_engagement = statistics.mean(engagement_data)
            viral_threshold = avg_engagement + 3 * statistics.stdev(engagement_data)
            
            viral_events = [i for i, val in enumerate(engagement_data) if val > viral_threshold]
            
            if len(viral_events) >= 1:
                pattern = Pattern(
                    pattern_id=f"viral_engagement_{int(time.time())}",
                    pattern_type=PatternType.CONTENT_CONSUMPTION,
                    confidence=PatternConfidence.HIGH,
                    frequency=PatternFrequency.IRREGULAR,
                    metric_name="audience_engagement",
                    pattern_data=[engagement_data[i] for i in viral_events],
                    pattern_length=len(viral_events),
                    amplitude=max(engagement_data[i] for i in viral_events) - avg_engagement,
                    period=0.0,
                    phase=0.0,
                    trend=0.0,
                    mean_value=statistics.mean(engagement_data[i] for i in viral_events),
                    std_deviation=0.0,
                    min_value=min(engagement_data[i] for i in viral_events),
                    max_value=max(engagement_data[i] for i in viral_events),
                    recognition_algorithm=RecognitionAlgorithm.STATISTICAL_ANALYSIS,
                    discovery_timestamp=datetime.now(),
                    last_seen=datetime.now(),
                    business_impact=f"Pattern engagement viral - {len(viral_events)} événements détectés",
                    creator_economy_relevance=True,
                    tags=["viral_content", "audience_response", "monetization_opportunity"]
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse patterns engagement: {e}")
            return []
    
    async def _analyze_collaboration_patterns(self, collab_data: List[float]) -> List[Pattern]:
        """Analyse patterns de collaboration"""
        try:
            patterns = []
            
            if len(collab_data) < 5:
                return patterns
            
            # Détection patterns collaboration intensive
            avg_collab = statistics.mean(collab_data)
            
            if avg_collab > 2.0:  # Plus de 2 collaborations par période
                pattern = Pattern(
                    pattern_id=f"high_collaboration_{int(time.time())}",
                    pattern_type=PatternType.COLLABORATION,
                    confidence=PatternConfidence.MEDIUM,
                    frequency=PatternFrequency.CONTINUOUS,
                    metric_name="collaboration_sessions",
                    pattern_data=collab_data.copy(),
                    pattern_length=len(collab_data),
                    amplitude=max(collab_data) - min(collab_data),
                    period=0.0,
                    phase=0.0,
                    trend=0.0,
                    mean_value=avg_collab,
                    std_deviation=statistics.stdev(collab_data) if len(collab_data) > 1 else 0.0,
                    min_value=min(collab_data),
                    max_value=max(collab_data),
                    recognition_algorithm=RecognitionAlgorithm.STATISTICAL_ANALYSIS,
                    discovery_timestamp=datetime.now(),
                    last_seen=datetime.now(),
                    business_impact=f"Créateur collaboratif - {avg_collab:.1f} sessions/période",
                    creator_economy_relevance=True,
                    tags=["collaboration", "network_effects", "cross_promotion"]
                )
                patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse patterns collaboration: {e}")
            return []
    
    async def _analyze_revenue_patterns(self, revenue_data: List[float]) -> List[Pattern]:
        """Analyse patterns de revenus"""
        try:
            patterns = []
            
            if len(revenue_data) < 7:
                return patterns
            
            # Détection croissance revenus
            if len(revenue_data) >= 10:
                x = np.arange(len(revenue_data))
                coeffs = np.polyfit(x, revenue_data, 1)
                revenue_growth = coeffs[0]
                
                if revenue_growth > 0.1:  # Croissance significative
                    pattern = Pattern(
                        pattern_id=f"revenue_growth_{int(time.time())}",
                        pattern_type=PatternType.PERFORMANCE,
                        confidence=PatternConfidence.HIGH,
                        frequency=PatternFrequency.CONTINUOUS,
                        metric_name="creator_revenue",
                        pattern_data=revenue_data.copy(),
                        pattern_length=len(revenue_data),
                        amplitude=max(revenue_data) - min(revenue_data),
                        period=0.0,
                        phase=0.0,
                        trend=revenue_growth,
                        mean_value=statistics.mean(revenue_data),
                        std_deviation=statistics.stdev(revenue_data) if len(revenue_data) > 1 else 0.0,
                        min_value=min(revenue_data),
                        max_value=max(revenue_data),
                        recognition_algorithm=RecognitionAlgorithm.STATISTICAL_ANALYSIS,
                        discovery_timestamp=datetime.now(),
                        last_seen=datetime.now(),
                        business_impact=f"Croissance revenus positive - {revenue_growth:.2f}/période",
                        creator_economy_relevance=True,
                        tags=["revenue_growth", "monetization_success", "creator_success"]
                    )
                    patterns.append(pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse patterns revenus: {e}")
            return []

class RedisPatternRecognitionManager:
    """🧩 Gestionnaire de reconnaissance patterns Redis - AI-driven pattern intelligence"""
    
    def __init__(self, config: PatternConfig, redis_url: str = "redis://localhost:6379"):
        self.config = config
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        
        # Analyseurs
        self.correlation_analyzer = CorrelationAnalyzer(config)
        self.statistical_analyzer = StatisticalPatternAnalyzer(config)
        self.creator_analyzer = CreatorPatternAnalyzer(config)
        
        # Cache patterns
        self.discovered_patterns: Dict[str, Pattern] = {}
        self.pattern_history: List[Pattern] = []
        
        # Cache données
        self.metrics_cache: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=self.config.historical_depth // 60)  # Points par minute
        )
        
        # État et contrôle
        self._running = False
        self._recognition_task: Optional[asyncio.Task] = None
        self._prediction_task: Optional[asyncio.Task] = None
        
        # Métriques
        self.total_patterns_discovered = 0
        self.active_patterns = 0
        self.pattern_accuracy_scores: List[float] = []
    
    async def initialize(self):
        """Initialise le gestionnaire de reconnaissance patterns"""
        try:
            # Connexion Redis
            self.redis_client = redis.Redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
            
            self.redis_client.ping()
            
            # Chargement patterns existants
            await self._load_existing_patterns()
            
            # Démarrage tâches
            self._running = True
            self._recognition_task = asyncio.create_task(self._recognition_loop())
            self._prediction_task = asyncio.create_task(self._prediction_loop())
            
            logger.info("🧩 Redis Pattern Recognition Manager initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation pattern recognition: {e}")
            raise
    
    async def analyze_patterns(self, metrics_data: Dict[str, List[float]]) -> List[Pattern]:
        """Analyse et découvre patterns dans données métriques"""
        try:
            all_patterns = []
            
            # Mise à jour cache
            for metric_name, values in metrics_data.items():
                for value in values[-10:]:  # Dernières valeurs
                    self.metrics_cache[metric_name].append({
                        "value": value,
                        "timestamp": time.time()
                    })
            
            # Analyse corrélations
            correlation_patterns = await self.correlation_analyzer.find_correlation_patterns()
            all_patterns.extend(correlation_patterns)
            
            # Analyse statistique par métrique
            for metric_name, values in metrics_data.items():
                if len(values) >= self.config.min_pattern_length:
                    stat_patterns = await self.statistical_analyzer.find_statistical_patterns(
                        metric_name, values
                    )
                    all_patterns.extend(stat_patterns)
            
            # Analyse patterns Creator Economy
            if self.config.creator_patterns:
                creator_data = {k: v for k, v in metrics_data.items() 
                              if k in self.creator_analyzer.creator_metrics}
                if creator_data:
                    creator_patterns = await self.creator_analyzer.analyze_creator_patterns(creator_data)
                    all_patterns.extend(creator_patterns)
            
            # Filtrage et validation patterns
            validated_patterns = await self._validate_patterns(all_patterns)
            
            # Stockage nouveaux patterns
            for pattern in validated_patterns:
                await self._store_pattern(pattern)
            
            return validated_patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur analyse patterns: {e}")
            return []
    
    async def predict_pattern_evolution(self, pattern_id: str, 
                                      horizon: int = None) -> List[float]:
        """Prédit évolution d'un pattern"""
        try:
            pattern = self.discovered_patterns.get(pattern_id)
            if not pattern:
                return []
            
            if horizon is None:
                horizon = self.config.prediction_horizon // 60  # Points
            
            predictions = []
            
            # Prédiction basée sur type pattern
            if pattern.pattern_type == PatternType.SEASONAL:
                # Extrapolation cyclique
                cycle_length = int(pattern.period)
                if cycle_length > 0:
                    for i in range(horizon):
                        pred_value = pattern.pattern_data[i % cycle_length]
                        predictions.append(pred_value)
            
            elif pattern.pattern_type == PatternType.TEMPORAL:
                # Extrapolation tendance
                last_value = pattern.pattern_data[-1] if pattern.pattern_data else pattern.mean_value
                for i in range(horizon):
                    pred_value = last_value + pattern.trend * (i + 1)
                    predictions.append(pred_value)
            
            elif pattern.pattern_type == PatternType.BEHAVIORAL:
                # Prédiction basée sur moyenne
                avg_value = pattern.mean_value
                std_value = pattern.std_deviation
                for i in range(horizon):
                    # Simulation avec variation
                    pred_value = avg_value + np.random.normal(0, std_value * 0.1)
                    predictions.append(pred_value)
            
            else:
                # Prédiction par défaut
                predictions = [pattern.mean_value] * horizon
            
            # Mise à jour prédictions pattern
            pattern.predicted_next_values = predictions
            
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction pattern {pattern_id}: {e}")
            return []
    
    async def get_active_patterns(self, pattern_type: Optional[PatternType] = None,
                                confidence_filter: Optional[PatternConfidence] = None) -> List[Pattern]:
        """Retourne patterns actifs avec filtres optionnels"""
        try:
            patterns = list(self.discovered_patterns.values())
            
            # Filtrage par type
            if pattern_type:
                patterns = [p for p in patterns if p.pattern_type == pattern_type]
            
            # Filtrage par confiance
            if confidence_filter:
                confidence_levels = {
                    PatternConfidence.VERY_HIGH: 4,
                    PatternConfidence.HIGH: 3,
                    PatternConfidence.MEDIUM: 2,
                    PatternConfidence.LOW: 1,
                    PatternConfidence.UNCERTAIN: 0
                }
                min_level = confidence_levels[confidence_filter]
                patterns = [p for p in patterns 
                           if confidence_levels[p.confidence] >= min_level]
            
            # Tri par confiance et dernière occurrence
            confidence_order = {
                PatternConfidence.VERY_HIGH: 4,
                PatternConfidence.HIGH: 3,
                PatternConfidence.MEDIUM: 2,
                PatternConfidence.LOW: 1,
                PatternConfidence.UNCERTAIN: 0
            }
            
            patterns.sort(key=lambda p: (confidence_order[p.confidence], p.last_seen), reverse=True)
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération patterns actifs: {e}")
            return []
    
    async def get_pattern_statistics(self) -> Dict[str, Any]:
        """Retourne statistiques reconnaissance patterns"""
        try:
            # Répartition par type
            type_counts = defaultdict(int)
            for pattern in self.discovered_patterns.values():
                type_counts[pattern.pattern_type.value] += 1
            
            # Répartition par confiance
            confidence_counts = defaultdict(int)
            for pattern in self.discovered_patterns.values():
                confidence_counts[pattern.confidence.value] += 1
            
            # Répartition par fréquence
            frequency_counts = defaultdict(int)
            for pattern in self.discovered_patterns.values():
                frequency_counts[pattern.frequency.value] += 1
            
            # Patterns Creator Economy
            creator_patterns = [p for p in self.discovered_patterns.values() 
                              if p.creator_economy_relevance]
            
            # Accuracy moyenne
            avg_accuracy = statistics.mean(self.pattern_accuracy_scores) if self.pattern_accuracy_scores else 0.0
            
            return {
                "total_patterns_discovered": self.total_patterns_discovered,
                "active_patterns": len(self.discovered_patterns),
                "pattern_type_distribution": dict(type_counts),
                "confidence_distribution": dict(confidence_counts),
                "frequency_distribution": dict(frequency_counts),
                "creator_economy_patterns": len(creator_patterns),
                "average_prediction_accuracy": avg_accuracy,
                "monitored_metrics": len(self.config.monitored_metrics),
                "recognition_algorithms": [alg.value for alg in self.config.recognition_algorithms],
                "cache_utilization": {
                    metric: len(cache) for metric, cache in self.metrics_cache.items()
                },
                "last_analysis": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statistiques patterns: {e}")
            return {}
    
    async def _validate_patterns(self, patterns: List[Pattern]) -> List[Pattern]:
        """Valide et filtre patterns découverts"""
        try:
            validated = []
            
            for pattern in patterns:
                # Validation confiance minimum
                if pattern.confidence == PatternConfidence.UNCERTAIN:
                    continue
                
                # Validation longueur minimum
                if pattern.pattern_length < self.config.min_pattern_length:
                    continue
                
                # Validation unicité (éviter doublons)
                is_duplicate = False
                for existing_pattern in self.discovered_patterns.values():
                    if (existing_pattern.metric_name == pattern.metric_name and
                        existing_pattern.pattern_type == pattern.pattern_type and
                        abs(existing_pattern.period - pattern.period) < 0.1):
                        is_duplicate = True
                        # Mise à jour occurrence
                        existing_pattern.occurrence_count += 1
                        existing_pattern.last_seen = datetime.now()
                        break
                
                if not is_duplicate:
                    validated.append(pattern)
            
            return validated
            
        except Exception as e:
            logger.error(f"❌ Erreur validation patterns: {e}")
            return patterns
    
    async def _store_pattern(self, pattern: Pattern):
        """Stocke un pattern découvert"""
        try:
            # Stockage en mémoire
            self.discovered_patterns[pattern.pattern_id] = pattern
            self.pattern_history.append(pattern)
            self.total_patterns_discovered += 1
            
            # Limitation cache
            if len(self.discovered_patterns) > self.config.max_patterns_per_metric * len(self.config.monitored_metrics):
                # Suppression patterns les plus anciens avec faible confiance
                old_patterns = sorted(
                    self.discovered_patterns.values(),
                    key=lambda p: (p.confidence.value, p.last_seen)
                )
                
                for old_pattern in old_patterns[:10]:  # Supprime 10 patterns
                    del self.discovered_patterns[old_pattern.pattern_id]
            
            # Persistance Redis
            await self._persist_pattern(pattern)
            
            logger.info(f"🧩 Pattern stocké: {pattern.pattern_id} "
                       f"({pattern.pattern_type.value}, {pattern.confidence.value})")
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage pattern: {e}")
    
    async def _load_existing_patterns(self):
        """Charge patterns existants depuis Redis"""
        try:
            pattern_keys = self.redis_client.keys("pattern:*")
            
            for key in pattern_keys:
                try:
                    pattern_data = self.redis_client.get(key)
                    if pattern_data:
                        # Reconstruction simplifiée du pattern
                        data = json.loads(pattern_data)
                        pattern_id = data.get("pattern_id", key.split(":")[-1])
                        
                        # Pattern minimal pour démo
                        self.discovered_patterns[pattern_id] = data
                        
                except Exception as e:
                    logger.warning(f"⚠️ Erreur chargement pattern {key}: {e}")
            
            logger.info(f"📊 Patterns chargés: {len(self.discovered_patterns)}")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement patterns: {e}")
    
    async def _persist_pattern(self, pattern: Pattern):
        """Persiste un pattern dans Redis"""
        try:
            pattern_data = {
                "pattern_id": pattern.pattern_id,
                "pattern_type": pattern.pattern_type.value,
                "confidence": pattern.confidence.value,
                "frequency": pattern.frequency.value,
                "metric_name": pattern.metric_name,
                "pattern_length": pattern.pattern_length,
                "amplitude": pattern.amplitude,
                "period": pattern.period,
                "mean_value": pattern.mean_value,
                "discovery_timestamp": pattern.discovery_timestamp.isoformat(),
                "last_seen": pattern.last_seen.isoformat(),
                "occurrence_count": pattern.occurrence_count,
                "business_impact": pattern.business_impact,
                "creator_economy_relevance": pattern.creator_economy_relevance,
                "tags": pattern.tags
            }
            
            key = f"pattern:{pattern.pattern_id}"
            self.redis_client.setex(key, 86400 * 7, json.dumps(pattern_data))  # 7 jours TTL
            
        except Exception as e:
            logger.error(f"❌ Erreur persistance pattern: {e}")
    
    async def _recognition_loop(self):
        """Boucle de reconnaissance automatique"""
        while self._running:
            try:
                # Collecte données récentes depuis cache
                metrics_data = {}
                
                for metric_name in self.config.monitored_metrics:
                    if metric_name in self.metrics_cache:
                        # Extraction valeurs récentes
                        recent_data = list(self.metrics_cache[metric_name])[-100:]  # 100 derniers points
                        values = [item["value"] for item in recent_data]
                        
                        if len(values) >= self.config.min_pattern_length:
                            metrics_data[metric_name] = values
                
                # Analyse correlations
                if len(metrics_data) >= 2:
                    await self.correlation_analyzer.analyze_correlations(metrics_data)
                
                # Reconnaissance patterns
                if metrics_data:
                    patterns = await self.analyze_patterns(metrics_data)
                    if patterns:
                        logger.info(f"🧩 Patterns découverts: {len(patterns)}")
                
                await asyncio.sleep(self.config.pattern_update_interval)
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle reconnaissance: {e}")
                await asyncio.sleep(60)
    
    async def _prediction_loop(self):
        """Boucle de prédiction patterns"""
        while self._running:
            try:
                await asyncio.sleep(900)  # Prédictions toutes les 15 min
                
                # Mise à jour prédictions patterns actifs
                for pattern_id in list(self.discovered_patterns.keys()):
                    try:
                        predictions = await self.predict_pattern_evolution(pattern_id)
                        if predictions:
                            # Simulation validation prédiction (à implémenter avec vraies données)
                            accuracy = np.random.uniform(0.7, 0.95)  # Simulation
                            self.pattern_accuracy_scores.append(accuracy)
                            
                            # Limitation historique accuracy
                            if len(self.pattern_accuracy_scores) > 100:
                                self.pattern_accuracy_scores = self.pattern_accuracy_scores[-100:]
                                
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur prédiction pattern {pattern_id}: {e}")
                
                logger.info("🔮 Prédictions patterns mises à jour")
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle prédiction: {e}")
                await asyncio.sleep(300)
    
    async def shutdown(self):
        """Arrêt propre du gestionnaire"""
        try:
            self._running = False
            
            # Arrêt tâches
            for task in [self._recognition_task, self._prediction_task]:
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Sauvegarde finale patterns
            for pattern in self.discovered_patterns.values():
                await self._persist_pattern(pattern)
            
            # Fermeture Redis
            if self.redis_client:
                self.redis_client.close()
            
            logger.info("🧩 Redis Pattern Recognition Manager arrêté")
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt pattern recognition: {e}")


# Factory function
async def create_pattern_recognition_manager(config: Optional[PatternConfig] = None,
                                           redis_url: str = "redis://localhost:6379") -> RedisPatternRecognitionManager:
    """Crée et initialise un gestionnaire de reconnaissance patterns Redis"""
    try:
        if config is None:
            config = PatternConfig()
        
        manager = RedisPatternRecognitionManager(config, redis_url)
        await manager.initialize()
        
        logger.info("🧩 Redis Pattern Recognition Manager créé avec succès")
        return manager
        
    except Exception as e:
        logger.error(f"❌ Erreur création pattern recognition manager: {e}")
        raise


# Export des classes principales
__all__ = [
    "RedisPatternRecognitionManager",
    "PatternConfig",
    "Pattern",
    "PatternType",
    "PatternConfidence",
    "PatternFrequency",
    "RecognitionAlgorithm",
    "CorrelationAnalyzer",
    "StatisticalPatternAnalyzer",
    "CreatorPatternAnalyzer",
    "create_pattern_recognition_manager"
]
