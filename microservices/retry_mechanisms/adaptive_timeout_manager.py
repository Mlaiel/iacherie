"""
Adaptive Timeout Manager - IA Chérie
=================================
Manager timeout adaptatif avec ML predictions.
Dynamic timeout adjustment + latency prediction + service profiling.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Retry Mechanisms
Version: 1.0 Production

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture retry mechanisms et tous ses algorithmes sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import time
import statistics
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class TimeoutStrategy(Enum):
    """Stratégies de timeout disponibles"""
    FIXED = "fixed"
    PERCENTILE_BASED = "percentile_based"
    ML_PREDICTED = "ml_predicted"
    ADAPTIVE_HYBRID = "adaptive_hybrid"
    LOAD_AWARE = "load_aware"

class TimeOfDayPeriod(Enum):
    """Périodes du jour pour adaptation"""
    NIGHT = "night"          # 00:00-06:00
    MORNING = "morning"      # 06:00-12:00
    AFTERNOON = "afternoon"  # 12:00-18:00
    EVENING = "evening"      # 18:00-24:00

@dataclass
class TimeoutConfig:
    """Configuration timeout adaptatif"""
    # Basic timeout settings
    base_timeout: float = 30.0
    min_timeout: float = 1.0
    max_timeout: float = 300.0
    strategy: TimeoutStrategy = TimeoutStrategy.ADAPTIVE_HYBRID
    
    # Percentile settings
    target_percentile: float = 95.0  # P95
    percentile_buffer: float = 1.5   # 50% buffer
    
    # ML prediction settings
    prediction_enabled: bool = True
    learning_rate: float = 0.01
    confidence_threshold: float = 0.7
    
    # Adaptive settings
    load_adjustment_factor: float = 0.3
    time_of_day_adjustment: bool = True
    seasonal_adjustment: bool = True
    
    # Historical data
    history_window_size: int = 1000
    min_samples_for_ml: int = 50

@dataclass
class OperationContext:
    """Contexte d'opération pour timeout calculation"""
    operation_id: str
    operation_type: str
    service_name: str
    priority: int = 1
    data_size: Optional[int] = None
    complexity_score: float = 1.0
    retry_attempt: int = 0
    user_context: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)

@dataclass
class LatencyPrediction:
    """Prédiction latence ML"""
    predicted_latency: float
    confidence_score: float
    prediction_method: str
    features_used: List[str]
    timestamp: float = field(default_factory=time.time)

@dataclass
class TimeoutDecision:
    """Décision timeout finale"""
    recommended_timeout: float
    strategy_used: TimeoutStrategy
    confidence: float
    factors: Dict
    reasoning: str
    adaptive_adjustments: Dict = field(default_factory=dict)

class LatencyPredictionEngine:
    """Moteur prédiction latence avec ML time series"""
    
    def __init__(self, config: TimeoutConfig):
        self.config = config
        self.latency_history = defaultdict(lambda: deque(maxlen=config.history_window_size))
        self.prediction_models = defaultdict(dict)  # service -> model_weights
        self.feature_extractors = {}
        
        # Time series patterns
        self.seasonal_patterns = defaultdict(dict)  # service -> {hour: avg_latency}
        self.trend_data = defaultdict(lambda: deque(maxlen=100))
        
    async def predict_latency(self, context: OperationContext) -> LatencyPrediction:
        """Prédiction latence opération avec ML time series"""
        
        service_name = context.service_name
        operation_type = context.operation_type
        
        # Extraction features
        features = await self._extract_features(context)
        
        # Prédiction basée sur historique si disponible
        historical_latencies = self.latency_history[f"{service_name}:{operation_type}"]
        
        if len(historical_latencies) < self.config.min_samples_for_ml:
            # Pas assez de données pour ML - utilisation baseline
            predicted_latency = self._baseline_prediction(context, features)
            confidence = 0.3
            method = "baseline_heuristic"
        else:
            # Prédiction ML basée sur features et historique
            predicted_latency = await self._ml_predict_latency(context, features, historical_latencies)
            confidence = self._calculate_prediction_confidence(features, historical_latencies)
            method = "ml_time_series"
        
        return LatencyPrediction(
            predicted_latency=predicted_latency,
            confidence_score=confidence,
            prediction_method=method,
            features_used=list(features.keys())
        )
    
    async def _extract_features(self, context: OperationContext) -> Dict[str, float]:
        """Extraction features pour prédiction ML"""
        
        current_time = time.time()
        hour_of_day = (current_time % 86400) / 3600  # 0-24
        day_of_week = ((current_time // 86400) % 7)  # 0-6
        
        features = {
            # Temporal features
            'hour_of_day_sin': math.sin(2 * math.pi * hour_of_day / 24),
            'hour_of_day_cos': math.cos(2 * math.pi * hour_of_day / 24),
            'day_of_week_sin': math.sin(2 * math.pi * day_of_week / 7),
            'day_of_week_cos': math.cos(2 * math.pi * day_of_week / 7),
            
            # Operation features
            'priority_normalized': context.priority / 5.0,
            'complexity_score': context.complexity_score,
            'retry_attempt': min(context.retry_attempt / 5.0, 1.0),
            
            # Data size features
            'data_size_log': math.log10(max(context.data_size or 1, 1)),
            'data_size_normalized': min((context.data_size or 0) / 1000000, 1.0),
            
            # Context features
            'is_peak_hour': 1.0 if 9 <= hour_of_day <= 17 else 0.0,
            'is_weekend': 1.0 if day_of_week >= 5 else 0.0,
        }
        
        # Service-specific features
        service_key = f"{context.service_name}:{context.operation_type}"
        recent_latencies = list(self.latency_history[service_key])[-10:]
        
        if recent_latencies:
            features['recent_avg_latency'] = statistics.mean(recent_latencies)
            features['recent_latency_trend'] = self._calculate_trend(recent_latencies)
            features['latency_volatility'] = statistics.stdev(recent_latencies) if len(recent_latencies) > 1 else 0.0
        else:
            features['recent_avg_latency'] = 1.0
            features['recent_latency_trend'] = 0.0
            features['latency_volatility'] = 0.0
        
        return features
    
    def _baseline_prediction(self, context: OperationContext, features: Dict) -> float:
        """Prédiction baseline basée sur heuristiques"""
        
        base_latency = 1.0  # 1 second baseline
        
        # Ajustement par type d'opération
        operation_multipliers = {
            'content_processing': 5.0,
            'ai_processing': 10.0,
            'monetization': 2.0,
            'collaboration': 3.0,
            'distribution': 4.0,
            'protection': 2.5
        }
        
        base_latency *= operation_multipliers.get(context.operation_type, 2.0)
        
        # Ajustement par taille données
        if context.data_size:
            data_factor = max(1.0, math.log10(context.data_size / 1000))
            base_latency *= data_factor
        
        # Ajustement par complexité
        base_latency *= context.complexity_score
        
        # Ajustement par retry attempt
        if context.retry_attempt > 0:
            base_latency *= (1.2 ** context.retry_attempt)  # Exponential degradation
        
        return base_latency
    
    async def _ml_predict_latency(self, context: OperationContext, features: Dict, historical_data: deque) -> float:
        """Prédiction ML basée sur features et données historiques"""
        
        service_key = f"{context.service_name}:{context.operation_type}"
        model_weights = self.prediction_models[service_key]
        
        # Simple linear prediction si pas de modèle entraîné
        if not model_weights:
            model_weights = {feature: 0.1 for feature in features.keys()}
            self.prediction_models[service_key] = model_weights
        
        # Prédiction linéaire
        prediction = 1.0  # Baseline
        for feature, value in features.items():
            weight = model_weights.get(feature, 0.0)
            prediction += weight * value
        
        # Ajustement basé sur tendance récente
        recent_avg = statistics.mean(list(historical_data)[-20:])
        prediction = (prediction + recent_avg) / 2  # Blend with recent average
        
        return max(0.1, prediction)
    
    def _calculate_prediction_confidence(self, features: Dict, historical_data: deque) -> float:
        """Calcul confidence score pour prédiction"""
        
        confidence = 0.5  # Base confidence
        
        # Plus de données historiques = plus de confidence
        data_factor = min(1.0, len(historical_data) / self.config.history_window_size)
        confidence += data_factor * 0.3
        
        # Stabilité des données récentes
        if len(historical_data) > 10:
            recent_data = list(historical_data)[-20:]
            volatility = statistics.stdev(recent_data) / statistics.mean(recent_data)
            stability_factor = max(0.0, 1.0 - volatility)
            confidence += stability_factor * 0.2
        
        return min(1.0, confidence)
    
    def _calculate_trend(self, data_points: List[float]) -> float:
        """Calcul tendance des données récentes"""
        if len(data_points) < 2:
            return 0.0
        
        # Simple linear regression slope
        n = len(data_points)
        x_sum = sum(range(n))
        y_sum = sum(data_points)
        xy_sum = sum(i * y for i, y in enumerate(data_points))
        x2_sum = sum(i * i for i in range(n))
        
        denominator = n * x2_sum - x_sum * x_sum
        if denominator == 0:
            return 0.0
        
        slope = (n * xy_sum - x_sum * y_sum) / denominator
        return slope
    
    async def update_model(self, context: OperationContext, actual_latency: float):
        """Mise à jour modèle ML avec latence réelle"""
        
        service_key = f"{context.service_name}:{context.operation_type}"
        
        # Ajout à l'historique
        self.latency_history[service_key].append(actual_latency)
        
        # Mise à jour patterns saisonniers
        hour = int((time.time() % 86400) / 3600)
        if service_key not in self.seasonal_patterns:
            self.seasonal_patterns[service_key] = {}
        
        current_avg = self.seasonal_patterns[service_key].get(hour, actual_latency)
        # Exponential moving average
        self.seasonal_patterns[service_key][hour] = current_avg * 0.9 + actual_latency * 0.1
        
        # Mise à jour modèle si assez de données
        if len(self.latency_history[service_key]) >= self.config.min_samples_for_ml:
            await self._retrain_model(service_key, context)
    
    async def _retrain_model(self, service_key: str, context: OperationContext):
        """Re-entraînement modèle ML"""
        
        # Entraînement simple avec gradient descent
        learning_rate = self.config.learning_rate
        model_weights = self.prediction_models[service_key]
        
        # Récupération données récentes pour entraînement
        recent_data = list(self.latency_history[service_key])[-100:]
        
        if len(recent_data) < 10:
            return
        
        # Simple mise à jour weights basée sur erreur récente
        features = await self._extract_features(context)
        predicted = sum(model_weights.get(f, 0.0) * v for f, v in features.items())
        actual = recent_data[-1]  # Last actual latency
        
        error = actual - predicted
        
        # Gradient descent update
        for feature, value in features.items():
            if feature not in model_weights:
                model_weights[feature] = 0.0
            model_weights[feature] += learning_rate * error * value

class ServiceLatencyProfiler:
    """Profiler latence services pour timeout optimization"""
    
    def __init__(self, config: TimeoutConfig):
        self.config = config
        self.service_profiles = defaultdict(lambda: {
            'latency_percentiles': {},
            'load_patterns': defaultdict(list),
            'error_correlations': {},
            'capacity_metrics': {}
        })
        
        self.profiling_active = True
        self.profile_history = defaultdict(lambda: deque(maxlen=500))
    
    async def profile_service(self, service_id: str, sampling_period: int = 300) -> Dict:
        """Profiling latence service pour timeout optimization"""
        
        if not self.profiling_active:
            return {'status': 'profiling_disabled'}
        
        profile_data = self.service_profiles[service_id]
        
        # Calcul percentiles récents
        recent_latencies = [
            record['latency'] for record in self.profile_history[service_id]
            if time.time() - record['timestamp'] <= sampling_period
        ]
        
        if recent_latencies:
            percentiles = self._calculate_percentiles(recent_latencies)
            profile_data['latency_percentiles'] = percentiles
            
            # Analyse patterns de charge
            load_analysis = await self._analyze_load_patterns(service_id, sampling_period)
            profile_data['load_patterns'] = load_analysis
            
            # Corrélation erreurs/latence
            error_correlation = await self._analyze_error_correlation(service_id)
            profile_data['error_correlations'] = error_correlation
        
        return {
            'service_id': service_id,
            'sampling_period': sampling_period,
            'profile_data': profile_data,
            'samples_count': len(recent_latencies),
            'profiling_timestamp': time.time()
        }
    
    def _calculate_percentiles(self, latencies: List[float]) -> Dict:
        """Calcul percentiles latence"""
        if not latencies:
            return {}
        
        sorted_latencies = sorted(latencies)
        
        percentiles = {}
        for p in [50, 75, 90, 95, 99]:
            index = int((p / 100.0) * len(sorted_latencies))
            index = min(index, len(sorted_latencies) - 1)
            percentiles[f'p{p}'] = sorted_latencies[index]
        
        percentiles['mean'] = statistics.mean(latencies)
        percentiles['median'] = statistics.median(latencies)
        percentiles['std_dev'] = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
        
        return percentiles
    
    async def _analyze_load_patterns(self, service_id: str, sampling_period: int) -> Dict:
        """Analyse patterns de charge service"""
        
        current_time = time.time()
        recent_records = [
            record for record in self.profile_history[service_id]
            if current_time - record['timestamp'] <= sampling_period
        ]
        
        if not recent_records:
            return {}
        
        # Groupement par période temporelle
        hourly_loads = defaultdict(list)
        for record in recent_records:
            hour = int((record['timestamp'] % 86400) / 3600)
            hourly_loads[hour].append(record['latency'])
        
        # Calcul moyennes par heure
        hourly_averages = {}
        for hour, latencies in hourly_loads.items():
            hourly_averages[hour] = statistics.mean(latencies)
        
        # Détection pics de charge
        if hourly_averages:
            avg_latency = statistics.mean(hourly_averages.values())
            peak_hours = [
                hour for hour, latency in hourly_averages.items()
                if latency > avg_latency * 1.5
            ]
        else:
            peak_hours = []
        
        return {
            'hourly_averages': hourly_averages,
            'peak_hours': peak_hours,
            'load_variability': statistics.stdev(list(hourly_averages.values())) if len(hourly_averages) > 1 else 0.0
        }
    
    async def _analyze_error_correlation(self, service_id: str) -> Dict:
        """Analyse corrélation erreurs/latence"""
        
        records = list(self.profile_history[service_id])
        
        if len(records) < 10:
            return {'correlation': 0.0, 'sample_size': len(records)}
        
        # Séparation succès/échecs
        success_latencies = [r['latency'] for r in records if r.get('success', True)]
        error_latencies = [r['latency'] for r in records if not r.get('success', True)]
        
        correlation_data = {
            'success_avg_latency': statistics.mean(success_latencies) if success_latencies else 0.0,
            'error_avg_latency': statistics.mean(error_latencies) if error_latencies else 0.0,
            'success_count': len(success_latencies),
            'error_count': len(error_latencies)
        }
        
        # Calcul corrélation simple
        if success_latencies and error_latencies:
            correlation_data['latency_difference'] = correlation_data['error_avg_latency'] - correlation_data['success_avg_latency']
            correlation_data['error_impact_factor'] = correlation_data['error_avg_latency'] / correlation_data['success_avg_latency']
        
        return correlation_data
    
    async def record_operation(self, service_id: str, latency: float, success: bool = True, metadata: Dict = None):
        """Enregistrement opération pour profiling"""
        
        record = {
            'timestamp': time.time(),
            'latency': latency,
            'success': success,
            'metadata': metadata or {}
        }
        
        self.profile_history[service_id].append(record)

class TimeoutOptimizer:
    """Optimiseur timeout basé sur performance metrics"""
    
    def __init__(self, config: TimeoutConfig):
        self.config = config 
        self.optimization_history = deque(maxlen=200)
        self.current_optimizations = {}
    
    async def optimize_timeout_strategy(self, performance_data: Dict) -> Dict:
        """Optimization stratégie timeout basée sur performance metrics"""
        
        service_id = performance_data.get('service_id', 'unknown')
        current_timeout = performance_data.get('current_timeout', self.config.base_timeout)
        
        # Métriques performance
        success_rate = performance_data.get('success_rate', 0.5)
        avg_latency = performance_data.get('avg_latency', 1.0)
        timeout_rate = performance_data.get('timeout_rate', 0.0)
        p95_latency = performance_data.get('p95_latency', avg_latency * 2)
        
        optimization = {
            'service_id': service_id,
            'current_timeout': current_timeout,
            'recommended_timeout': current_timeout,
            'optimization_reason': [],
            'confidence': 0.5,
            'expected_improvement': 0.0
        }
        
        # Optimisation si taux timeout élevé
        if timeout_rate > 0.1:  # Plus de 10% de timeouts
            new_timeout = max(p95_latency * self.config.percentile_buffer, current_timeout * 1.2)
            optimization['recommended_timeout'] = min(new_timeout, self.config.max_timeout)
            optimization['optimization_reason'].append(f"High timeout rate ({timeout_rate:.1%})")
            optimization['confidence'] += 0.2
        
        # Optimisation si timeout trop conservatif
        elif timeout_rate < 0.01 and current_timeout > p95_latency * 2:
            new_timeout = max(p95_latency * self.config.percentile_buffer, self.config.min_timeout)
            optimization['recommended_timeout'] = new_timeout
            optimization['optimization_reason'].append("Conservative timeout - can be reduced")
            optimization['confidence'] += 0.15
        
        # Ajustement basé sur success rate
        if success_rate < 0.8:
            optimization['recommended_timeout'] *= 1.3
            optimization['optimization_reason'].append(f"Low success rate ({success_rate:.1%})")
        
        # Calcul amélioration attendue
        timeout_difference = abs(optimization['recommended_timeout'] - current_timeout)
        optimization['expected_improvement'] = min(timeout_difference / current_timeout, 0.5)
        
        # Stockage historique
        self.optimization_history.append(optimization.copy())
        self.current_optimizations[service_id] = optimization
        
        return optimization

class AdaptiveTimeoutManager:
    """
    Manager timeout adaptatif avec ML predictions.
    Dynamic timeout adjustment + latency prediction + service profiling.
    """
    
    def __init__(self, timeout_config: TimeoutConfig = None):
        self.timeout_config = timeout_config or TimeoutConfig()
        self.latency_predictor = LatencyPredictionEngine(self.timeout_config)
        self.service_profiler = ServiceLatencyProfiler(self.timeout_config)
        self.timeout_optimizer = TimeoutOptimizer(self.timeout_config)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Cache timeout decisions
        self.timeout_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Métriques manager
        self.manager_metrics = {
            'timeout_calculations': 0,
            'cache_hits': 0,
            'ml_predictions': 0,
            'optimizations_applied': 0,
            'services_profiled': 0
        }
    
    async def calculate_adaptive_timeout(self, operation_context: OperationContext) -> TimeoutDecision:
        """
        Calcul timeout adaptatif basé sur ML predictions.
        
        Adaptive Features:
        - ML-based latency prediction pour timeout optimization
        - Service-specific timeout profiling
        - Time-of-day adaptive timeouts
        - Load-based timeout adjustment
        - Network condition aware timeouts
        - Historical performance timeout tuning
        - Percentile-based timeout calculation (P95, P99)
        """
        
        self.manager_metrics['timeout_calculations'] += 1
        
        try:
            # Vérification cache
            cache_key = self._generate_cache_key(operation_context)
            cached_decision = self._get_cached_decision(cache_key)
            
            if cached_decision:
                self.manager_metrics['cache_hits'] += 1
                return cached_decision
            
            # 1. Prédiction latence ML
            latency_prediction = await self.predict_operation_latency(
                operation_context.operation_type, 
                operation_context.__dict__
            )
            
            # 2. Profiling service
            service_profile = await self.profile_service_latency(
                operation_context.service_name,
                sampling_period=300
            )
            
            # 3. Calcul timeout basé sur stratégie
            base_timeout = await self._calculate_base_timeout(
                operation_context, 
                latency_prediction,
                service_profile
            )
            
            # 4. Ajustements adaptatifs
            adjusted_timeout = await self._apply_adaptive_adjustments(
                base_timeout,
                operation_context,
                latency_prediction
            )
            
            # 5. Validation et finalisation
            final_timeout = self._validate_timeout_bounds(adjusted_timeout)
            
            # Création décision
            decision = TimeoutDecision(
                recommended_timeout=final_timeout,
                strategy_used=self.timeout_config.strategy,
                confidence=latency_prediction.confidence_score,
                factors={
                    'predicted_latency': latency_prediction.predicted_latency,
                    'base_timeout': base_timeout,
                    'adjustments_applied': adjusted_timeout - base_timeout,
                    'service_profile': service_profile.get('profile_data', {}),
                    'time_of_day_factor': self._get_time_of_day_factor(),
                    'load_factor': await self._estimate_current_load()
                },
                reasoning=self._generate_timeout_reasoning(latency_prediction, operation_context)
            )
            
            # Cache décision
            self._cache_decision(cache_key, decision)
            
            self.logger.info(f"Calculated adaptive timeout for {operation_context.operation_type}: {final_timeout:.2f}s")
            return decision
            
        except Exception as e:
            self.logger.error(f"Error calculating adaptive timeout: {str(e)}")
            # Fallback timeout
            return TimeoutDecision(
                recommended_timeout=self.timeout_config.base_timeout,
                strategy_used=TimeoutStrategy.FIXED,
                confidence=0.1,
                factors={'error': str(e)},
                reasoning="Fallback due to calculation error"
            )
    
    async def predict_operation_latency(self, operation_type: str, context: Dict) -> LatencyPrediction:
        """Prédiction latence opération avec ML time series."""
        
        self.manager_metrics['ml_predictions'] += 1
        
        # Création contexte d'opération
        operation_context = OperationContext(
            operation_id=context.get('operation_id', 'unknown'),
            operation_type=operation_type,
            service_name=context.get('service_name', 'unknown'),
            priority=context.get('priority', 1),
            data_size=context.get('data_size'),
            complexity_score=context.get('complexity_score', 1.0),
            retry_attempt=context.get('retry_attempt', 0)
        )
        
        return await self.latency_predictor.predict_latency(operation_context)
    
    async def profile_service_latency(self, service_id: str, sampling_period: int) -> Dict:
        """Profiling latence service pour timeout optimization."""
        
        self.manager_metrics['services_profiled'] += 1
        return await self.service_profiler.profile_service(service_id, sampling_period)
    
    async def optimize_timeout_strategy(self, performance_metrics: Dict) -> Dict:
        """Optimization stratégie timeout basée sur performance metrics."""
        
        self.manager_metrics['optimizations_applied'] += 1
        return await self.timeout_optimizer.optimize_timeout_strategy(performance_metrics)
    
    async def adjust_timeout_dynamically(self, real_time_metrics: Dict) -> Dict:
        """Ajustement timeout dynamique basé sur conditions courantes."""
        
        service_id = real_time_metrics.get('service_id', 'unknown')
        current_timeout = real_time_metrics.get('current_timeout', self.timeout_config.base_timeout)
        
        # Facteurs d'ajustement
        load_factor = real_time_metrics.get('load_factor', 1.0)
        error_rate = real_time_metrics.get('error_rate', 0.0)
        network_quality = real_time_metrics.get('network_quality', 1.0)
        
        # Calcul ajustement
        adjustment_factor = 1.0
        
        # Ajustement charge
        if load_factor > 0.8:
            adjustment_factor *= 1.3
        elif load_factor < 0.3:
            adjustment_factor *= 0.8
        
        # Ajustement taux d'erreur
        if error_rate > 0.1:
            adjustment_factor *= 1.2
        
        # Ajustement qualité réseau
        adjustment_factor *= (2.0 - network_quality)  # Worse network = higher timeout
        
        new_timeout = current_timeout * adjustment_factor
        new_timeout = self._validate_timeout_bounds(new_timeout)
        
        return {
            'service_id': service_id,
            'previous_timeout': current_timeout,
            'new_timeout': new_timeout,
            'adjustment_factor': adjustment_factor,
            'factors': {
                'load_factor': load_factor,
                'error_rate': error_rate,
                'network_quality': network_quality
            },
            'adjustment_timestamp': time.time()
        }
    
    async def _calculate_base_timeout(self, context: OperationContext, prediction: LatencyPrediction, profile: Dict) -> float:
        """Calcul timeout de base selon stratégie"""
        
        if self.timeout_config.strategy == TimeoutStrategy.FIXED:
            return self.timeout_config.base_timeout
        
        elif self.timeout_config.strategy == TimeoutStrategy.ML_PREDICTED:
            return prediction.predicted_latency * self.timeout_config.percentile_buffer
        
        elif self.timeout_config.strategy == TimeoutStrategy.PERCENTILE_BASED:
            profile_data = profile.get('profile_data', {})
            percentiles = profile_data.get('latency_percentiles', {})
            p95 = percentiles.get('p95', prediction.predicted_latency)
            return p95 * self.timeout_config.percentile_buffer
        
        elif self.timeout_config.strategy == TimeoutStrategy.ADAPTIVE_HYBRID:
            # Combinaison ML + percentiles
            ml_timeout = prediction.predicted_latency * self.timeout_config.percentile_buffer
            
            profile_data = profile.get('profile_data', {})
            percentiles = profile_data.get('latency_percentiles', {})
            percentile_timeout = percentiles.get('p95', prediction.predicted_latency) * self.timeout_config.percentile_buffer
            
            # Pondération par confidence
            confidence = prediction.confidence_score
            hybrid_timeout = (ml_timeout * confidence + percentile_timeout * (1 - confidence))
            
            return hybrid_timeout
        
        else:
            return self.timeout_config.base_timeout
    
    async def _apply_adaptive_adjustments(self, base_timeout: float, context: OperationContext, prediction: LatencyPrediction) -> float:
        """Application ajustements adaptatifs"""
        
        adjusted_timeout = base_timeout
        
        # Ajustement priorité
        priority_factor = 1.0 + (context.priority - 1) * 0.2  # Higher priority = higher timeout
        adjusted_timeout *= priority_factor
        
        # Ajustement retry
        if context.retry_attempt > 0:
            retry_factor = 1.0 + context.retry_attempt * 0.3
            adjusted_timeout *= retry_factor
        
        # Ajustement time-of-day
        if self.timeout_config.time_of_day_adjustment:
            time_factor = self._get_time_of_day_factor()
            adjusted_timeout *= time_factor
        
        # Ajustement charge système
        load_factor = await self._estimate_current_load()
        load_adjustment = 1.0 + (load_factor - 0.5) * self.timeout_config.load_adjustment_factor
        adjusted_timeout *= load_adjustment
        
        return adjusted_timeout
    
    def _get_time_of_day_factor(self) -> float:
        """Facteur ajustement basé sur heure du jour"""
        
        hour = int((time.time() % 86400) / 3600)
        
        # Heures de pointe (9h-17h) - plus de timeout
        if 9 <= hour <= 17:
            return 1.2
        # Heures creuses (0h-6h) - moins de timeout
        elif 0 <= hour <= 6:
            return 0.8
        else:
            return 1.0
    
    async def _estimate_current_load(self) -> float:
        """Estimation charge système actuelle"""
        # En production, intégrerait avec monitoring système
        # Simulation basique
        hour = int((time.time() % 86400) / 3600)
        base_load = 0.3 + 0.4 * math.sin(2 * math.pi * (hour - 6) / 24)  # Peak at ~14h
        return max(0.1, min(1.0, base_load))
    
    def _validate_timeout_bounds(self, timeout: float) -> float:
        """Validation limites timeout"""
        return max(self.timeout_config.min_timeout, 
                  min(timeout, self.timeout_config.max_timeout))
    
    def _generate_cache_key(self, context: OperationContext) -> str:
        """Génération clé cache pour timeout decision"""
        key_components = [
            context.service_name,
            context.operation_type,
            str(context.priority),
            str(context.retry_attempt),
            str(int(time.time() / self.cache_ttl))  # Time bucket for cache invalidation
        ]
        return ":".join(key_components)
    
    def _get_cached_decision(self, cache_key: str) -> Optional[TimeoutDecision]:
        """Récupération décision cachée"""
        if cache_key in self.timeout_cache:
            cached_entry = self.timeout_cache[cache_key]
            if time.time() - cached_entry['timestamp'] < self.cache_ttl:
                return cached_entry['decision']
            else:
                del self.timeout_cache[cache_key]
        return None
    
    def _cache_decision(self, cache_key: str, decision: TimeoutDecision):
        """Mise en cache décision"""
        self.timeout_cache[cache_key] = {
            'decision': decision,
            'timestamp': time.time()
        }
    
    def _generate_timeout_reasoning(self, prediction: LatencyPrediction, context: OperationContext) -> str:
        """Génération explication décision timeout"""
        
        reasoning_parts = [
            f"Based on {prediction.prediction_method}",
            f"Predicted latency: {prediction.predicted_latency:.2f}s",
            f"Confidence: {prediction.confidence_score:.2f}",
            f"Operation type: {context.operation_type}",
            f"Priority: {context.priority}"
        ]
        
        if context.retry_attempt > 0:
            reasoning_parts.append(f"Retry attempt: {context.retry_attempt}")
        
        return " | ".join(reasoning_parts)
    
    async def record_operation_result(self, context: OperationContext, actual_latency: float, success: bool):
        """Enregistrement résultat opération pour amélioration ML"""
        
        # Mise à jour modèle ML
        await self.latency_predictor.update_model(context, actual_latency)
        
        # Enregistrement pour profiling
        await self.service_profiler.record_operation(
            context.service_name,
            actual_latency,
            success,
            {'operation_type': context.operation_type, 'priority': context.priority}
        )
    
    async def get_manager_metrics(self) -> Dict:
        """Métriques manager timeout"""
        
        return {
            **self.manager_metrics,
            'cache_size': len(self.timeout_cache),
            'services_tracked': len(self.latency_predictor.latency_history),
            'ml_models_trained': len(self.latency_predictor.prediction_models),
            'config': {
                'strategy': self.timeout_config.strategy.value,
                'base_timeout': self.timeout_config.base_timeout,
                'min_timeout': self.timeout_config.min_timeout,
                'max_timeout': self.timeout_config.max_timeout,
                'target_percentile': self.timeout_config.target_percentile
            }
        }

# Factory functions
def create_adaptive_timeout_manager(
    base_timeout: float = 30.0,
    strategy: TimeoutStrategy = TimeoutStrategy.ADAPTIVE_HYBRID,
    ml_enabled: bool = True
) -> AdaptiveTimeoutManager:
    """Factory pour création manager timeout adaptatif"""
    
    config = TimeoutConfig(
        base_timeout=base_timeout,
        strategy=strategy,
        prediction_enabled=ml_enabled
    )
    
    return AdaptiveTimeoutManager(config)

# Configurations prédéfinies pour IA Chérie
IACHERIE_TIMEOUT_CONFIGS = {
    'content_processing': TimeoutConfig(
        base_timeout=120.0,
        max_timeout=600.0,
        strategy=TimeoutStrategy.PERCENTILE_BASED,
        target_percentile=95.0
    ),
    'ai_processing': TimeoutConfig(
        base_timeout=300.0,
        max_timeout=1800.0,
        strategy=TimeoutStrategy.ML_PREDICTED,
        prediction_enabled=True
    ),
    'monetization': TimeoutConfig(
        base_timeout=30.0,
        max_timeout=120.0,
        strategy=TimeoutStrategy.FIXED,
        time_of_day_adjustment=False
    ),
    'distribution': TimeoutConfig(
        base_timeout=60.0,
        max_timeout=900.0,
        strategy=TimeoutStrategy.ADAPTIVE_HYBRID,
        load_adjustment_factor=0.5
    )
}

__all__ = [
    'AdaptiveTimeoutManager',
    'TimeoutConfig',
    'OperationContext',
    'TimeoutDecision',
    'LatencyPrediction',
    'TimeoutStrategy',
    'TimeOfDayPeriod',
    'LatencyPredictionEngine',
    'ServiceLatencyProfiler',
    'TimeoutOptimizer',
    'create_adaptive_timeout_manager',
    'IACHERIE_TIMEOUT_CONFIGS'
]