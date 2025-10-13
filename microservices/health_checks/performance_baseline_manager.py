"""
Performance Baseline Manager - IA Chérie Health Checks Module
Gestionnaire baselines performance avec adaptive thresholds, trend analysis,
performance regression detection et optimization recommendations.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture health checks et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel. Toute reproduction, modification, distribution ou vol 
d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import json
import uuid
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

logger = logging.getLogger(__name__)

class BaselineType(Enum):
    """Types de baselines performance"""
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    CUSTOM_METRIC = "custom_metric"

class BaselineStatus(Enum):
    """Statuts baseline"""
    ACTIVE = "active"
    LEARNING = "learning"
    STALE = "stale"
    INVALID = "invalid"

class PerformanceRegression(Enum):
    """Types régression performance"""
    MINOR = "minor"          # 5-15% dégradation
    MODERATE = "moderate"    # 15-30% dégradation
    MAJOR = "major"          # 30-50% dégradation
    SEVERE = "severe"        # >50% dégradation

@dataclass
class PerformanceBaseline:
    """Baseline performance"""
    baseline_id: str
    service_name: str
    metric_name: str
    baseline_type: BaselineType
    baseline_value: float
    confidence_interval: Tuple[float, float]
    sample_size: int
    created_timestamp: datetime
    last_updated: datetime
    status: BaselineStatus
    learning_period_days: int = 7
    adaptation_rate: float = 0.1  # Rate of adaptation to new data
    seasonal_pattern: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PerformanceBenchmark:
    """Benchmark performance"""
    benchmark_id: str
    service_name: str
    benchmark_timestamp: datetime
    metrics: Dict[str, float]
    environment_context: Dict[str, Any]
    load_characteristics: Dict[str, Any]
    performance_score: float
    baseline_comparison: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RegressionDetection:
    """Détection régression performance"""
    detection_id: str
    service_name: str
    metric_name: str
    regression_type: PerformanceRegression
    current_value: float
    baseline_value: float
    degradation_percentage: float
    detection_timestamp: datetime
    confidence_score: float
    potential_causes: List[str] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)

@dataclass
class BaselineConfig:
    """Configuration baseline manager"""
    learning_period_days: int = 7
    min_samples_for_baseline: int = 100
    confidence_level: float = 0.95
    outlier_threshold_sigma: float = 3.0
    regression_threshold_percentage: float = 15.0
    adaptation_enabled: bool = True
    seasonal_analysis_enabled: bool = True
    auto_threshold_adjustment: bool = True

class StatisticalAnalyzer:
    """Analyseur statistique pour baselines"""
    
    @staticmethod
    async def calculate_baseline_statistics(values: List[float], 
                                          confidence_level: float = 0.95) -> Dict[str, Any]:
        """Calculer statistiques baseline"""
        if len(values) < 2:
            return {'error': 'Insufficient data points'}
            
        # Statistiques de base
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values)
        median_value = statistics.median(values)
        
        # Intervalle confiance
        confidence_interval = stats.t.interval(
            confidence_level, 
            len(values) - 1,
            loc=mean_value, 
            scale=stats.sem(values)
        )
        
        # Percentiles
        percentiles = {
            'p50': np.percentile(values, 50),
            'p75': np.percentile(values, 75),
            'p90': np.percentile(values, 90),
            'p95': np.percentile(values, 95),
            'p99': np.percentile(values, 99)
        }
        
        # Test normalité
        try:
            normality_test = stats.shapiro(values[:5000])  # Limite à 5000 points
            is_normal = normality_test.pvalue > 0.05
        except:
            is_normal = False
            
        return {
            'mean': mean_value,
            'median': median_value,
            'std_dev': std_dev,
            'min': min(values),
            'max': max(values),
            'confidence_interval': confidence_interval,
            'percentiles': percentiles,
            'sample_size': len(values),
            'is_normal_distribution': is_normal,
            'coefficient_of_variation': std_dev / mean_value if mean_value != 0 else 0
        }
        
    @staticmethod
    async def detect_outliers(values: List[float], 
                            method: str = 'zscore',
                            threshold: float = 3.0) -> List[int]:
        """Détecter outliers"""
        if len(values) < 4:
            return []
            
        outlier_indices = []
        
        if method == 'zscore':
            z_scores = np.abs(stats.zscore(values))
            outlier_indices = [i for i, z in enumerate(z_scores) if z > threshold]
            
        elif method == 'iqr':
            q1 = np.percentile(values, 25)
            q3 = np.percentile(values, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outlier_indices = [
                i for i, value in enumerate(values) 
                if value < lower_bound or value > upper_bound
            ]
            
        return outlier_indices
        
    @staticmethod
    async def analyze_trend(values: List[float], timestamps: List[datetime]) -> Dict[str, Any]:
        """Analyser tendance temporelle"""
        if len(values) != len(timestamps) or len(values) < 3:
            return {'trend': 'insufficient_data'}
            
        # Convertir timestamps en secondes
        time_seconds = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
        
        # Régression linéaire
        slope, intercept, r_value, p_value, std_err = stats.linregress(time_seconds, values)
        
        # Classification tendance
        if abs(r_value) < 0.1:
            trend_direction = 'stable'
        elif slope > 0:
            trend_direction = 'increasing'
        else:
            trend_direction = 'decreasing'
            
        # Force tendance
        if abs(r_value) > 0.7:
            trend_strength = 'strong'
        elif abs(r_value) > 0.3:
            trend_strength = 'moderate'
        else:
            trend_strength = 'weak'
            
        return {
            'trend': trend_direction,
            'strength': trend_strength,
            'slope': slope,
            'correlation_coefficient': r_value,
            'p_value': p_value,
            'statistical_significance': p_value < 0.05,
            'trend_equation': f'y = {slope:.4f}x + {intercept:.4f}'
        }

class SeasonalityAnalyzer:
    """Analyseur saisonnalité patterns"""
    
    @staticmethod
    async def detect_seasonal_patterns(values: List[float], 
                                     timestamps: List[datetime],
                                     period_hours: int = 24) -> Dict[str, Any]:
        """Détecter patterns saisonniers"""
        if len(values) < period_hours * 2:  # Au moins 2 cycles
            return {'seasonal_pattern': None}
            
        # Extraire composants temporels
        hours = [ts.hour for ts in timestamps]
        days_of_week = [ts.weekday() for ts in timestamps]
        
        # Analyser pattern horaire
        hourly_pattern = await SeasonalityAnalyzer._analyze_hourly_pattern(values, hours)
        
        # Analyser pattern hebdomadaire
        weekly_pattern = await SeasonalityAnalyzer._analyze_weekly_pattern(values, days_of_week)
        
        # Décomposition saisonnière simple
        seasonal_strength = await SeasonalityAnalyzer._calculate_seasonal_strength(
            values, timestamps, period_hours
        )
        
        return {
            'seasonal_pattern': {
                'hourly': hourly_pattern,
                'weekly': weekly_pattern,
                'seasonal_strength': seasonal_strength
            }
        }
        
    @staticmethod
    async def _analyze_hourly_pattern(values: List[float], hours: List[int]) -> Dict[str, Any]:
        """Analyser pattern horaire"""
        hourly_values = defaultdict(list)
        
        for value, hour in zip(values, hours):
            hourly_values[hour].append(value)
            
        hourly_stats = {}
        for hour in range(24):
            if hour in hourly_values and len(hourly_values[hour]) > 1:
                hourly_stats[hour] = {
                    'mean': statistics.mean(hourly_values[hour]),
                    'std': statistics.stdev(hourly_values[hour]),
                    'count': len(hourly_values[hour])
                }
                
        return hourly_stats
        
    @staticmethod
    async def _analyze_weekly_pattern(values: List[float], days: List[int]) -> Dict[str, Any]:
        """Analyser pattern hebdomadaire"""
        daily_values = defaultdict(list)
        
        for value, day in zip(values, days):
            daily_values[day].append(value)
            
        daily_stats = {}
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for day in range(7):
            if day in daily_values and len(daily_values[day]) > 1:
                daily_stats[day_names[day]] = {
                    'mean': statistics.mean(daily_values[day]),
                    'std': statistics.stdev(daily_values[day]),
                    'count': len(daily_values[day])
                }
                
        return daily_stats
        
    @staticmethod
    async def _calculate_seasonal_strength(values: List[float], 
                                         timestamps: List[datetime],
                                         period_hours: int) -> float:
        """Calculer force saisonnalité"""
        if len(values) < period_hours * 2:
            return 0.0
            
        # Grouper par période
        period_groups = defaultdict(list)
        
        for value, timestamp in zip(values, timestamps):
            period_key = timestamp.hour  # Simplification: utiliser heure
            period_groups[period_key].append(value)
            
        # Calculer variance inter vs intra groupes
        overall_variance = np.var(values)
        
        period_means = []
        for period_values in period_groups.values():
            if len(period_values) > 1:
                period_means.append(statistics.mean(period_values))
                
        if len(period_means) < 2:
            return 0.0
            
        between_group_variance = np.var(period_means)
        
        # Force saisonnalité = variance entre groupes / variance totale
        seasonal_strength = between_group_variance / overall_variance if overall_variance > 0 else 0
        
        return min(1.0, seasonal_strength)

class PerformanceBaselineManager:
    """
    Gestionnaire baselines performance avec adaptive thresholds.
    Trend analysis + performance regression detection + optimization recommendations.
    
    Features:
    - Adaptive baseline learning avec statistical analysis
    - Seasonal pattern detection et adjustment
    - Performance regression detection multi-level
    - Confidence interval calculation avec outlier handling
    - Auto-adjusting thresholds basé sur performance trends
    - Benchmark comparison et performance scoring
    """
    
    def __init__(self, baseline_config: BaselineConfig):
        self.baseline_config = baseline_config
        self.statistical_analyzer = StatisticalAnalyzer()
        self.seasonality_analyzer = SeasonalityAnalyzer()
        
        # Stockage baselines
        self.performance_baselines: Dict[str, PerformanceBaseline] = {}
        self.baseline_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # Benchmarks et comparaisons
        self.performance_benchmarks: List[PerformanceBenchmark] = []
        self.regression_detections: List[RegressionDetection] = []
        
        # Monitoring continu
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Statistiques
        self.baseline_stats = {
            'total_baselines': 0,
            'active_baselines': 0,
            'learning_baselines': 0,
            'regressions_detected': 0,
            'baselines_updated': 0,
            'average_confidence_score': 0.0
        }
        
    async def ingest_performance_data(self, service_name: str, metric_name: str, 
                                    value: float, timestamp: datetime = None):
        """Ingérer données performance"""
        if timestamp is None:
            timestamp = datetime.now()
            
        data_point = {
            'value': value,
            'timestamp': timestamp,
            'service_name': service_name,
            'metric_name': metric_name
        }
        
        baseline_key = f"{service_name}:{metric_name}"
        self.baseline_data[baseline_key].append(data_point)
        
        # Déclencher mise à jour baseline si suffisamment de données
        if len(self.baseline_data[baseline_key]) >= self.baseline_config.min_samples_for_baseline:
            await self._trigger_baseline_update(service_name, metric_name)
            
    async def create_performance_baseline(self, service_name: str, metric_name: str,
                                        baseline_type: BaselineType,
                                        force_recreate: bool = False) -> Optional[PerformanceBaseline]:
        """
        Créer baseline performance pour service/métrique.
        
        Args:
            service_name: Nom du service
            metric_name: Nom de la métrique
            baseline_type: Type de baseline
            force_recreate: Forcer recréation si existe
            
        Returns:
            Baseline créée ou None si échec
        """
        baseline_key = f"{service_name}:{metric_name}"
        
        # Vérifier si baseline existe déjà
        if baseline_key in self.performance_baselines and not force_recreate:
            return self.performance_baselines[baseline_key]
            
        # Récupérer données historiques
        if baseline_key not in self.baseline_data:
            logger.warning(f"No historical data for baseline: {baseline_key}")
            return None
            
        data_points = list(self.baseline_data[baseline_key])
        
        if len(data_points) < self.baseline_config.min_samples_for_baseline:
            logger.warning(f"Insufficient data points for baseline: {len(data_points)} < {self.baseline_config.min_samples_for_baseline}")
            return None
            
        try:
            # Extraire valeurs et timestamps
            values = [dp['value'] for dp in data_points]
            timestamps = [dp['timestamp'] for dp in data_points]
            
            # Supprimer outliers
            outlier_indices = await self.statistical_analyzer.detect_outliers(
                values, threshold=self.baseline_config.outlier_threshold_sigma
            )
            
            clean_values = [v for i, v in enumerate(values) if i not in outlier_indices]
            clean_timestamps = [t for i, t in enumerate(timestamps) if i not in outlier_indices]
            
            if len(clean_values) < self.baseline_config.min_samples_for_baseline:
                logger.warning(f"Too many outliers removed, insufficient clean data: {len(clean_values)}")
                return None
                
            # Calculer statistiques baseline
            stats = await self.statistical_analyzer.calculate_baseline_statistics(
                clean_values, self.baseline_config.confidence_level
            )
            
            if 'error' in stats:
                logger.error(f"Baseline statistics calculation failed: {stats['error']}")
                return None
                
            # Analyser saisonnalité si activée
            seasonal_pattern = None
            if self.baseline_config.seasonal_analysis_enabled:
                seasonality_result = await self.seasonality_analyzer.detect_seasonal_patterns(
                    clean_values, clean_timestamps
                )
                seasonal_pattern = seasonality_result.get('seasonal_pattern')
                
            # Créer baseline
            baseline = PerformanceBaseline(
                baseline_id=str(uuid.uuid4()),
                service_name=service_name,
                metric_name=metric_name,
                baseline_type=baseline_type,
                baseline_value=stats['mean'],
                confidence_interval=stats['confidence_interval'],
                sample_size=len(clean_values),
                created_timestamp=datetime.now(),
                last_updated=datetime.now(),
                status=BaselineStatus.ACTIVE,
                learning_period_days=self.baseline_config.learning_period_days,
                seasonal_pattern=seasonal_pattern,
                metadata={
                    'statistics': stats,
                    'outliers_removed': len(outlier_indices),
                    'data_quality_score': len(clean_values) / len(values)
                }
            )
            
            # Stocker baseline
            self.performance_baselines[baseline_key] = baseline
            self.baseline_stats['total_baselines'] += 1
            self.baseline_stats['active_baselines'] += 1
            
            logger.info(f"Created performance baseline: {baseline_key} (value: {baseline.baseline_value:.2f})")
            return baseline
            
        except Exception as e:
            logger.error(f"Baseline creation failed for {baseline_key}: {e}")
            return None
            
    async def detect_performance_regressions(self, service_name: str = None,
                                           lookback_hours: int = 24) -> List[RegressionDetection]:
        """
        Détecter régressions performance.
        
        Args:
            service_name: Service spécifique ou None pour tous
            lookback_hours: Période analyse
            
        Returns:
            Liste régressions détectées
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=lookback_hours)
        
        regressions = []
        
        # Filtrer baselines à analyser
        baselines_to_check = []
        for baseline_key, baseline in self.performance_baselines.items():
            if service_name is None or baseline.service_name == service_name:
                if baseline.status == BaselineStatus.ACTIVE:
                    baselines_to_check.append((baseline_key, baseline))
                    
        # Analyser chaque baseline
        for baseline_key, baseline in baselines_to_check:
            try:
                # Récupérer données récentes
                recent_data = [
                    dp for dp in self.baseline_data[baseline_key]
                    if start_time <= dp['timestamp'] <= end_time
                ]
                
                if len(recent_data) < 10:  # Minimum data points
                    continue
                    
                recent_values = [dp['value'] for dp in recent_data]
                current_mean = statistics.mean(recent_values)
                
                # Calculer dégradation
                degradation_pct = await self._calculate_performance_degradation(
                    current_mean, baseline.baseline_value, baseline.baseline_type
                )
                
                # Détecter régression selon seuil
                if abs(degradation_pct) >= self.baseline_config.regression_threshold_percentage:
                    regression_type = await self._classify_regression_severity(degradation_pct)
                    
                    # Calculer confidence score
                    confidence_score = await self._calculate_regression_confidence(
                        recent_values, baseline
                    )
                    
                    # Identifier causes potentielles
                    potential_causes = await self._identify_regression_causes(
                        baseline, recent_data, degradation_pct
                    )
                    
                    # Générer recommandations
                    recommendations = await self._generate_regression_recommendations(
                        baseline, regression_type, potential_causes
                    )
                    
                    regression = RegressionDetection(
                        detection_id=str(uuid.uuid4()),
                        service_name=baseline.service_name,
                        metric_name=baseline.metric_name,
                        regression_type=regression_type,
                        current_value=current_mean,
                        baseline_value=baseline.baseline_value,
                        degradation_percentage=degradation_pct,
                        detection_timestamp=datetime.now(),
                        confidence_score=confidence_score,
                        potential_causes=potential_causes,
                        recommended_actions=recommendations
                    )
                    
                    regressions.append(regression)
                    self.regression_detections.append(regression)
                    
                    logger.warning(f"Performance regression detected: {baseline_key} ({degradation_pct:.1f}% degradation)")
                    
            except Exception as e:
                logger.error(f"Regression detection failed for {baseline_key}: {e}")
                continue
                
        self.baseline_stats['regressions_detected'] += len(regressions)
        return regressions
        
    async def update_adaptive_baseline(self, service_name: str, metric_name: str) -> bool:
        """Mettre à jour baseline adaptive"""
        baseline_key = f"{service_name}:{metric_name}"
        
        if baseline_key not in self.performance_baselines:
            return False
            
        baseline = self.performance_baselines[baseline_key]
        
        if not self.baseline_config.adaptation_enabled:
            return False
            
        try:
            # Récupérer données récentes
            recent_cutoff = datetime.now() - timedelta(days=1)  # Dernières 24h
            recent_data = [
                dp for dp in self.baseline_data[baseline_key]
                if dp['timestamp'] >= recent_cutoff
            ]
            
            if len(recent_data) < 20:  # Minimum pour adaptation
                return False
                
            recent_values = [dp['value'] for dp in recent_data]
            
            # Supprimer outliers
            outlier_indices = await self.statistical_analyzer.detect_outliers(recent_values)
            clean_recent_values = [v for i, v in enumerate(recent_values) if i not in outlier_indices]
            
            if len(clean_recent_values) < 10:
                return False
                
            # Calculer nouvelle valeur adaptée
            recent_mean = statistics.mean(clean_recent_values)
            adaptation_rate = baseline.adaptation_rate
            
            # Mise à jour adaptive: nouvelle_valeur = ancienne * (1-rate) + récente * rate
            new_baseline_value = (
                baseline.baseline_value * (1 - adaptation_rate) + 
                recent_mean * adaptation_rate
            )
            
            # Recalculer intervalle confiance
            new_stats = await self.statistical_analyzer.calculate_baseline_statistics(
                clean_recent_values, self.baseline_config.confidence_level
            )
            
            # Mettre à jour baseline
            baseline.baseline_value = new_baseline_value
            baseline.confidence_interval = new_stats['confidence_interval']
            baseline.last_updated = datetime.now()
            baseline.sample_size += len(clean_recent_values)
            
            self.baseline_stats['baselines_updated'] += 1
            
            logger.info(f"Updated adaptive baseline: {baseline_key} ({baseline.baseline_value:.2f})")
            return True
            
        except Exception as e:
            logger.error(f"Adaptive baseline update failed for {baseline_key}: {e}")
            return False
            
    async def create_performance_benchmark(self, service_name: str, 
                                         metrics: Dict[str, float],
                                         environment_context: Dict[str, Any] = None,
                                         load_characteristics: Dict[str, Any] = None) -> PerformanceBenchmark:
        """Créer benchmark performance"""
        benchmark_id = str(uuid.uuid4())
        
        # Calculer score performance global
        performance_score = await self._calculate_performance_score(service_name, metrics)
        
        # Comparer avec baselines existantes
        baseline_comparison = await self._compare_with_baselines(service_name, metrics)
        
        benchmark = PerformanceBenchmark(
            benchmark_id=benchmark_id,
            service_name=service_name,
            benchmark_timestamp=datetime.now(),
            metrics=metrics.copy(),
            environment_context=environment_context or {},
            load_characteristics=load_characteristics or {},
            performance_score=performance_score,
            baseline_comparison=baseline_comparison
        )
        
        self.performance_benchmarks.append(benchmark)
        
        logger.info(f"Created performance benchmark: {benchmark_id} for {service_name} (score: {performance_score:.2f})")
        return benchmark
        
    async def get_baseline_summary(self, service_name: str = None) -> Dict[str, Any]:
        """Obtenir synthèse baselines"""
        # Filtrer baselines
        if service_name:
            baselines = [b for b in self.performance_baselines.values() if b.service_name == service_name]
        else:
            baselines = list(self.performance_baselines.values())
            
        if not baselines:
            return {'message': 'No baselines found'}
            
        # Calculer statistiques
        active_baselines = [b for b in baselines if b.status == BaselineStatus.ACTIVE]
        learning_baselines = [b for b in baselines if b.status == BaselineStatus.LEARNING]
        
        # Confidence scores
        confidence_scores = []
        for baseline in baselines:
            if baseline.metadata and 'statistics' in baseline.metadata:
                stats = baseline.metadata['statistics']
                cv = stats.get('coefficient_of_variation', 0)
                confidence = max(0, 1 - cv)  # Simple confidence metric
                confidence_scores.append(confidence)
                
        avg_confidence = statistics.mean(confidence_scores) if confidence_scores else 0
        
        return {
            'total_baselines': len(baselines),
            'active_baselines': len(active_baselines),
            'learning_baselines': len(learning_baselines),
            'average_confidence_score': avg_confidence,
            'baselines_by_type': {
                baseline_type.value: len([b for b in baselines if b.baseline_type == baseline_type])
                for baseline_type in BaselineType
            },
            'recent_regressions': len([r for r in self.regression_detections 
                                     if r.detection_timestamp >= datetime.now() - timedelta(hours=24)]),
            'baseline_stats': self.baseline_stats.copy()
        }
        
    # Méthodes utilitaires
    
    async def _trigger_baseline_update(self, service_name: str, metric_name: str):
        """Déclencher mise à jour baseline"""
        baseline_key = f"{service_name}:{metric_name}"
        
        if baseline_key in self.performance_baselines:
            # Mise à jour adaptive
            await self.update_adaptive_baseline(service_name, metric_name)
        else:
            # Créer nouvelle baseline
            baseline_type = await self._infer_baseline_type(metric_name)
            await self.create_performance_baseline(service_name, metric_name, baseline_type)
            
    async def _infer_baseline_type(self, metric_name: str) -> BaselineType:
        """Inférer type baseline depuis nom métrique"""
        metric_lower = metric_name.lower()
        
        if 'response_time' in metric_lower or 'latency' in metric_lower:
            return BaselineType.RESPONSE_TIME
        elif 'throughput' in metric_lower or 'rps' in metric_lower:
            return BaselineType.THROUGHPUT
        elif 'error_rate' in metric_lower or 'error' in metric_lower:
            return BaselineType.ERROR_RATE
        elif 'cpu' in metric_lower:
            return BaselineType.CPU_UTILIZATION
        elif 'memory' in metric_lower:
            return BaselineType.MEMORY_UTILIZATION
        elif 'disk' in metric_lower:
            return BaselineType.DISK_IO
        elif 'network' in metric_lower:
            return BaselineType.NETWORK_IO
        else:
            return BaselineType.CUSTOM_METRIC
            
    async def _calculate_performance_degradation(self, current_value: float, 
                                               baseline_value: float,
                                               baseline_type: BaselineType) -> float:
        """Calculer dégradation performance"""
        if baseline_value == 0:
            return 0.0
            
        # Pour certaines métriques, plus élevé = meilleur
        if baseline_type in [BaselineType.THROUGHPUT]:
            # Throughput: dégradation si diminution
            degradation = ((baseline_value - current_value) / baseline_value) * 100
        else:
            # Response time, error rate, etc.: dégradation si augmentation
            degradation = ((current_value - baseline_value) / baseline_value) * 100
            
        return degradation
        
    async def _classify_regression_severity(self, degradation_pct: float) -> PerformanceRegression:
        """Classifier sévérité régression"""
        abs_degradation = abs(degradation_pct)
        
        if abs_degradation >= 50:
            return PerformanceRegression.SEVERE
        elif abs_degradation >= 30:
            return PerformanceRegression.MAJOR
        elif abs_degradation >= 15:
            return PerformanceRegression.MODERATE
        else:
            return PerformanceRegression.MINOR
            
    async def _calculate_regression_confidence(self, recent_values: List[float], 
                                             baseline: PerformanceBaseline) -> float:
        """Calculer confidence score régression"""
        if len(recent_values) < 5:
            return 0.0
            
        # Facteurs confidence:
        # 1. Taille échantillon
        sample_factor = min(1.0, len(recent_values) / 30)
        
        # 2. Consistance dégradation
        recent_mean = statistics.mean(recent_values)
        degraded_points = sum(1 for v in recent_values 
                            if abs(v - recent_mean) < abs(v - baseline.baseline_value))
        consistency_factor = degraded_points / len(recent_values)
        
        # 3. Distance du baseline
        distance_factor = min(1.0, abs(recent_mean - baseline.baseline_value) / baseline.baseline_value)
        
        confidence = (sample_factor * 0.3 + consistency_factor * 0.4 + distance_factor * 0.3)
        return confidence
        
    async def _identify_regression_causes(self, baseline: PerformanceBaseline,
                                        recent_data: List[Dict[str, Any]],
                                        degradation_pct: float) -> List[str]:
        """Identifier causes potentielles régression"""
        causes = []
        
        # Analyse temporelle
        if len(recent_data) >= 10:
            timestamps = [dp['timestamp'] for dp in recent_data]
            values = [dp['value'] for dp in recent_data]
            
            trend_analysis = await self.statistical_analyzer.analyze_trend(values, timestamps)
            
            if trend_analysis.get('trend') == 'increasing' and baseline.baseline_type in [
                BaselineType.RESPONSE_TIME, BaselineType.ERROR_RATE
            ]:
                causes.append("Gradual performance degradation trend detected")
            elif trend_analysis.get('trend') == 'decreasing' and baseline.baseline_type == BaselineType.THROUGHPUT:
                causes.append("Throughput decline trend detected")
                
        # Analyse saisonnalité
        if baseline.seasonal_pattern:
            current_hour = datetime.now().hour
            if baseline.seasonal_pattern.get('hourly', {}).get(str(current_hour)):
                causes.append("Performance issue coincides with known seasonal pattern")
                
        # Sévérité-based causes
        if abs(degradation_pct) > 30:
            causes.extend([
                "Possible infrastructure issue",
                "Recent deployment impact",
                "Resource exhaustion"
            ])
        elif abs(degradation_pct) > 15:
            causes.extend([
                "Configuration change impact",
                "Increased load without scaling",
                "Dependency performance issue"
            ])
            
        return causes[:5]  # Limiter à 5 causes
        
    async def _generate_regression_recommendations(self, baseline: PerformanceBaseline,
                                                 regression_type: PerformanceRegression,
                                                 potential_causes: List[str]) -> List[str]:
        """Générer recommandations régression"""
        recommendations = []
        
        # Recommandations par sévérité
        if regression_type == PerformanceRegression.SEVERE:
            recommendations.extend([
                "Immediate investigation required",
                "Consider emergency rollback if recent deployment",
                "Activate incident response procedures"
            ])
        elif regression_type == PerformanceRegression.MAJOR:
            recommendations.extend([
                "Priority investigation needed",
                "Check recent changes and deployments",
                "Monitor resource utilization"
            ])
        else:
            recommendations.extend([
                "Monitor trend continuation",
                "Review performance optimization opportunities"
            ])
            
        # Recommandations par type métrique
        if baseline.baseline_type == BaselineType.RESPONSE_TIME:
            recommendations.extend([
                "Check database query performance",
                "Review API endpoint optimization",
                "Consider caching improvements"
            ])
        elif baseline.baseline_type == BaselineType.THROUGHPUT:
            recommendations.extend([
                "Consider horizontal scaling",
                "Review load balancing configuration",
                "Check for bottlenecks in processing pipeline"
            ])
        elif baseline.baseline_type == BaselineType.ERROR_RATE:
            recommendations.extend([
                "Review application logs for error patterns",
                "Check dependency health",
                "Verify configuration correctness"
            ])
            
        return recommendations[:5]  # Limiter à 5 recommandations
        
    async def _calculate_performance_score(self, service_name: str, metrics: Dict[str, float]) -> float:
        """Calculer score performance global"""
        scores = []
        
        for metric_name, value in metrics.items():
            baseline_key = f"{service_name}:{metric_name}"
            
            if baseline_key in self.performance_baselines:
                baseline = self.performance_baselines[baseline_key]
                
                # Score basé sur distance du baseline
                if baseline.baseline_type in [BaselineType.RESPONSE_TIME, BaselineType.ERROR_RATE]:
                    # Plus bas = meilleur
                    score = max(0, 100 - ((value - baseline.baseline_value) / baseline.baseline_value * 100))
                else:
                    # Plus haut = meilleur
                    score = max(0, 100 + ((value - baseline.baseline_value) / baseline.baseline_value * 100))
                    
                scores.append(min(100, max(0, score)))
                
        return statistics.mean(scores) if scores else 50.0  # Score neutre si pas de baseline
        
    async def _compare_with_baselines(self, service_name: str, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Comparer métriques avec baselines"""
        comparisons = {}
        
        for metric_name, value in metrics.items():
            baseline_key = f"{service_name}:{metric_name}"
            
            if baseline_key in self.performance_baselines:
                baseline = self.performance_baselines[baseline_key]
                
                degradation_pct = await self._calculate_performance_degradation(
                    value, baseline.baseline_value, baseline.baseline_type
                )
                
                comparisons[metric_name] = {
                    'current_value': value,
                    'baseline_value': baseline.baseline_value,
                    'degradation_percentage': degradation_pct,
                    'within_confidence_interval': (
                        baseline.confidence_interval[0] <= value <= baseline.confidence_interval[1]
                    )
                }
                
        return comparisons

# Example usage et testing
if __name__ == "__main__":
    async def test_performance_baseline_manager():
        """Test gestionnaire baselines performance"""
        config = BaselineConfig(
            learning_period_days=1,  # Plus court pour test
            min_samples_for_baseline=20,
            regression_threshold_percentage=10.0,
            adaptation_enabled=True
        )
        
        manager = PerformanceBaselineManager(config)
        
        # Simuler ingestion données historiques
        base_time = datetime.now() - timedelta(hours=48)
        
        # Générer données normales puis dégradées
        for i in range(100):
            timestamp = base_time + timedelta(minutes=i * 30)
            
            # Response time normal: 200-400ms avec pattern horaire
            base_response_time = 300 + 50 * np.sin(i * 0.2)  # Pattern cyclique
            noise = np.random.normal(0, 30)
            response_time = max(50, base_response_time + noise)
            
            # Throughput normal: 100-200 RPS
            base_throughput = 150 + 30 * np.sin(i * 0.15)
            throughput = max(0, base_throughput + np.random.normal(0, 10))
            
            await manager.ingest_performance_data('api_service', 'response_time_ms', response_time, timestamp)
            await manager.ingest_performance_data('api_service', 'throughput_rps', throughput, timestamp)
            
        # Créer baselines
        response_time_baseline = await manager.create_performance_baseline(
            'api_service', 'response_time_ms', BaselineType.RESPONSE_TIME
        )
        
        throughput_baseline = await manager.create_performance_baseline(
            'api_service', 'throughput_rps', BaselineType.THROUGHPUT
        )
        
        print("📊 Performance Baseline Manager Results:")
        
        if response_time_baseline:
            print(f"Response Time Baseline: {response_time_baseline.baseline_value:.2f}ms")
            print(f"  Confidence Interval: {response_time_baseline.confidence_interval}")
            print(f"  Sample Size: {response_time_baseline.sample_size}")
            
        if throughput_baseline:
            print(f"Throughput Baseline: {throughput_baseline.baseline_value:.2f} RPS")
            print(f"  Confidence Interval: {throughput_baseline.confidence_interval}")
            
        # Simuler dégradation performance
        print("\n🔻 Simulating Performance Degradation...")
        
        recent_time = datetime.now() - timedelta(hours=2)
        for i in range(20):
            timestamp = recent_time + timedelta(minutes=i * 5)
            
            # Dégradation: response time +40%, throughput -25%
            degraded_response_time = 300 * 1.4 + np.random.normal(0, 20)
            degraded_throughput = 150 * 0.75 + np.random.normal(0, 5)
            
            await manager.ingest_performance_data('api_service', 'response_time_ms', degraded_response_time, timestamp)
            await manager.ingest_performance_data('api_service', 'throughput_rps', degraded_throughput, timestamp)
            
        # Détecter régressions
        regressions = await manager.detect_performance_regressions('api_service', 4)
        
        print(f"\nRegressions Detected: {len(regressions)}")
        for regression in regressions:
            print(f"  {regression.metric_name}: {regression.regression_type.value}")
            print(f"    Degradation: {regression.degradation_percentage:.1f}%")
            print(f"    Confidence: {regression.confidence_score:.2f}")
            print(f"    Causes: {regression.potential_causes[:2]}")
            
        # Créer benchmark
        current_metrics = {
            'response_time_ms': 420.0,
            'throughput_rps': 112.0,
            'error_rate_percent': 1.2
        }
        
        benchmark = await manager.create_performance_benchmark(
            'api_service', 
            current_metrics,
            environment_context={'version': '1.2.3', 'load': 'normal'},
            load_characteristics={'concurrent_users': 100, 'duration_minutes': 60}
        )
        
        print(f"\nBenchmark Created: {benchmark.benchmark_id}")
        print(f"  Performance Score: {benchmark.performance_score:.2f}/100")
        print(f"  Baseline Comparison: {len(benchmark.baseline_comparison)} metrics compared")
        
        # Synthèse baselines
        summary = await manager.get_baseline_summary('api_service')
        print(f"\nBaseline Summary:")
        print(f"  Total Baselines: {summary['total_baselines']}")
        print(f"  Active Baselines: {summary['active_baselines']}")
        print(f"  Average Confidence: {summary['average_confidence_score']:.2f}")
        print(f"  Recent Regressions: {summary['recent_regressions']}")
        
        return manager, regressions, benchmark
        
    # Run test
    asyncio.run(test_performance_baseline_manager())