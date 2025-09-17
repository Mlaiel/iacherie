"""
Deep Health Analyzer - Ainflue Health Checks Module
Analyseur health checks profond avec pattern analysis, anomaly detection,
trend prediction et correlation analysis.

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
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import statistics
from scipy import stats
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types d'analyse health"""
    PATTERN_RECOGNITION = "pattern_recognition"
    ANOMALY_DETECTION = "anomaly_detection"
    TREND_ANALYSIS = "trend_analysis"
    CORRELATION_ANALYSIS = "correlation_analysis"
    PREDICTIVE_ANALYSIS = "predictive_analysis"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"

class HealthTrendDirection(Enum):
    """Direction tendance santé"""
    IMPROVING = "improving"
    DEGRADING = "degrading"
    STABLE = "stable"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"

@dataclass
class HealthMetricPoint:
    """Point métrique santé"""
    timestamp: datetime
    service_name: str
    metric_name: str
    value: float
    status: str
    category: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AnalysisConfig:
    """Configuration analyseur health"""
    window_size_minutes: int = 60
    anomaly_threshold: float = 0.95
    trend_analysis_points: int = 20
    correlation_threshold: float = 0.7
    pattern_recognition_sensitivity: float = 0.8
    prediction_horizon_minutes: int = 30
    historical_data_days: int = 7

@dataclass
class HealthPattern:
    """Pattern santé détecté"""
    pattern_id: str
    pattern_type: str
    description: str
    confidence: float
    frequency: str
    services_affected: List[str]
    time_range: Tuple[datetime, datetime]
    characteristics: Dict[str, Any]

@dataclass
class HealthAnomaly:
    """Anomalie santé détectée"""
    anomaly_id: str
    service_name: str
    metric_name: str
    anomaly_score: float
    expected_value: float
    actual_value: float
    timestamp: datetime
    severity: str
    description: str
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthTrend:
    """Tendance santé"""
    service_name: str
    metric_name: str
    direction: HealthTrendDirection
    slope: float
    confidence: float
    prediction: Optional[float]
    time_range: Tuple[datetime, datetime]
    statistical_significance: float

class DeepHealthAnalyzer:
    """
    Analyseur health checks profond avec ML/IA.
    Pattern analysis + anomaly detection + trend prediction + correlation analysis.
    
    Features:
    - Advanced pattern recognition dans health metrics
    - ML-based anomaly detection avec isolation forest
    - Trend analysis et prediction avec régression
    - Service correlation analysis
    - Root cause analysis automatique
    - Predictive health forecasting
    """
    
    def __init__(self, analysis_config: AnalysisConfig):
        self.analysis_config = analysis_config
        
        # Stockage données health
        self.health_data: deque = deque(maxlen=10000)
        self.service_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Modèles ML
        self.anomaly_detectors: Dict[str, IsolationForest] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Patterns et tendances
        self.detected_patterns: List[HealthPattern] = []
        self.active_anomalies: List[HealthAnomaly] = []
        self.service_trends: Dict[str, List[HealthTrend]] = defaultdict(list)
        
        # Statistiques analyse
        self.analysis_stats = {
            'total_analyses': 0,
            'patterns_detected': 0,
            'anomalies_detected': 0,
            'predictions_made': 0,
            'accuracy_score': 0.0
        }
        
    async def ingest_health_data(self, metric_point: HealthMetricPoint):
        """Ingérer nouveau point métrique santé"""
        self.health_data.append(metric_point)
        key = f"{metric_point.service_name}:{metric_point.metric_name}"
        self.service_metrics[key].append(metric_point)
        
        # Mise à jour modèle anomaly detection si nécessaire
        await self._update_anomaly_model(key)
        
    async def analyze_comprehensive_health(self, analysis_types: List[AnalysisType] = None) -> Dict[str, Any]:
        """
        Analyse health complète multi-dimensionnelle.
        
        Args:
            analysis_types: Types d'analyse à effectuer
            
        Returns:
            Dict avec résultats analyses détaillées
        """
        if analysis_types is None:
            analysis_types = list(AnalysisType)
            
        analysis_start = datetime.now()
        results = {
            'analysis_id': f"health_analysis_{int(analysis_start.timestamp())}",
            'timestamp': analysis_start.isoformat(),
            'analysis_types': [t.value for t in analysis_types],
            'results': {}
        }
        
        try:
            # Pattern Recognition Analysis
            if AnalysisType.PATTERN_RECOGNITION in analysis_types:
                results['results']['pattern_analysis'] = await self._analyze_health_patterns()
                
            # Anomaly Detection Analysis  
            if AnalysisType.ANOMALY_DETECTION in analysis_types:
                results['results']['anomaly_analysis'] = await self._detect_health_anomalies()
                
            # Trend Analysis
            if AnalysisType.TREND_ANALYSIS in analysis_types:
                results['results']['trend_analysis'] = await self._analyze_health_trends()
                
            # Correlation Analysis
            if AnalysisType.CORRELATION_ANALYSIS in analysis_types:
                results['results']['correlation_analysis'] = await self._analyze_service_correlations()
                
            # Predictive Analysis
            if AnalysisType.PREDICTIVE_ANALYSIS in analysis_types:
                results['results']['predictive_analysis'] = await self._predict_health_evolution()
                
            # Root Cause Analysis
            if AnalysisType.ROOT_CAUSE_ANALYSIS in analysis_types:
                results['results']['root_cause_analysis'] = await self._analyze_root_causes()
                
            # Synthèse finale
            results['analysis_summary'] = await self._generate_analysis_summary(results['results'])
            results['execution_time_seconds'] = (datetime.now() - analysis_start).total_seconds()
            
            self.analysis_stats['total_analyses'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Deep health analysis failed: {e}")
            return {
                'analysis_id': results['analysis_id'],
                'timestamp': analysis_start.isoformat(),
                'status': 'error',
                'error': str(e)
            }
            
    async def _analyze_health_patterns(self) -> Dict[str, Any]:
        """Analyser patterns health récurrents"""
        patterns_found = []
        
        # Grouper données par service et métrique
        service_groups = defaultdict(list)
        for metric_point in list(self.health_data)[-1000:]:  # Derniers 1000 points
            key = f"{metric_point.service_name}:{metric_point.metric_name}"
            service_groups[key].append(metric_point)
            
        for service_metric, data_points in service_groups.items():
            if len(data_points) < 10:
                continue
                
            # Analyser patterns temporels
            temporal_patterns = await self._detect_temporal_patterns(data_points)
            patterns_found.extend(temporal_patterns)
            
            # Analyser patterns cycliques
            cyclic_patterns = await self._detect_cyclic_patterns(data_points)
            patterns_found.extend(cyclic_patterns)
            
        self.detected_patterns.extend(patterns_found)
        self.analysis_stats['patterns_detected'] += len(patterns_found)
        
        return {
            'patterns_detected': len(patterns_found),
            'pattern_details': [
                {
                    'pattern_id': p.pattern_id,
                    'type': p.pattern_type,
                    'description': p.description,
                    'confidence': p.confidence,
                    'services_affected': p.services_affected,
                    'frequency': p.frequency
                } for p in patterns_found
            ],
            'pattern_categories': self._categorize_patterns(patterns_found)
        }
        
    async def _detect_health_anomalies(self) -> Dict[str, Any]:
        """Détecter anomalies health avec ML"""
        anomalies_found = []
        
        for service_metric_key, data_points in self.service_metrics.items():
            if len(data_points) < 20:
                continue
                
            service_name, metric_name = service_metric_key.split(':', 1)
            
            # Préparer données pour détection anomalies
            values = [dp.value for dp in data_points]
            timestamps = [dp.timestamp for dp in data_points]
            
            # Détecter anomalies statistiques
            statistical_anomalies = await self._detect_statistical_anomalies(
                values, timestamps, service_name, metric_name
            )
            anomalies_found.extend(statistical_anomalies)
            
            # Détecter anomalies ML si modèle disponible
            if service_metric_key in self.anomaly_detectors:
                ml_anomalies = await self._detect_ml_anomalies(
                    values, timestamps, service_name, metric_name, service_metric_key
                )
                anomalies_found.extend(ml_anomalies)
                
        self.active_anomalies.extend(anomalies_found)
        self.analysis_stats['anomalies_detected'] += len(anomalies_found)
        
        return {
            'anomalies_detected': len(anomalies_found),
            'anomaly_details': [
                {
                    'anomaly_id': a.anomaly_id,
                    'service': a.service_name,
                    'metric': a.metric_name,
                    'severity': a.severity,
                    'anomaly_score': a.anomaly_score,
                    'expected': a.expected_value,
                    'actual': a.actual_value,
                    'timestamp': a.timestamp.isoformat(),
                    'description': a.description
                } for a in anomalies_found
            ],
            'severity_distribution': self._calculate_severity_distribution(anomalies_found)
        }
        
    async def _analyze_health_trends(self) -> Dict[str, Any]:
        """Analyser tendances health services"""
        trends_found = []
        
        for service_metric_key, data_points in self.service_metrics.items():
            if len(data_points) < self.analysis_config.trend_analysis_points:
                continue
                
            service_name, metric_name = service_metric_key.split(':', 1)
            
            # Prendre derniers points pour analyse tendance
            recent_points = list(data_points)[-self.analysis_config.trend_analysis_points:]
            values = [dp.value for dp in recent_points]
            timestamps = [(dp.timestamp - recent_points[0].timestamp).total_seconds() 
                         for dp in recent_points]
            
            # Calculer régression linéaire
            if len(values) >= 3:
                slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps, values)
                
                # Déterminer direction tendance
                direction = self._determine_trend_direction(slope, r_value)
                
                # Prédiction future
                future_time = timestamps[-1] + (self.analysis_config.prediction_horizon_minutes * 60)
                prediction = slope * future_time + intercept
                
                trend = HealthTrend(
                    service_name=service_name,
                    metric_name=metric_name,
                    direction=direction,
                    slope=slope,
                    confidence=abs(r_value),
                    prediction=prediction,
                    time_range=(recent_points[0].timestamp, recent_points[-1].timestamp),
                    statistical_significance=1 - p_value if p_value < 1 else 0
                )
                
                trends_found.append(trend)
                
        # Stocker tendances
        for trend in trends_found:
            self.service_trends[trend.service_name].append(trend)
            
        return {
            'trends_detected': len(trends_found),
            'trend_details': [
                {
                    'service': t.service_name,
                    'metric': t.metric_name,
                    'direction': t.direction.value,
                    'confidence': t.confidence,
                    'prediction': t.prediction,
                    'significance': t.statistical_significance
                } for t in trends_found
            ],
            'trend_summary': self._summarize_trends(trends_found)
        }
        
    async def _analyze_service_correlations(self) -> Dict[str, Any]:
        """Analyser corrélations entre services"""
        correlations = {}
        service_data = {}
        
        # Préparer données par service
        for service_metric_key, data_points in self.service_metrics.items():
            service_name, metric_name = service_metric_key.split(':', 1)
            if service_name not in service_data:
                service_data[service_name] = {}
            service_data[service_name][metric_name] = [dp.value for dp in data_points]
            
        # Calculer corrélations entre services
        services = list(service_data.keys())
        for i, service1 in enumerate(services):
            for j, service2 in enumerate(services[i+1:], i+1):
                correlation = await self._calculate_service_correlation(
                    service_data[service1], service_data[service2]
                )
                if abs(correlation) >= self.analysis_config.correlation_threshold:
                    correlations[f"{service1}_{service2}"] = correlation
                    
        return {
            'significant_correlations': len(correlations),
            'correlation_details': correlations,
            'correlation_matrix': await self._build_correlation_matrix(service_data),
            'correlation_insights': await self._generate_correlation_insights(correlations)
        }
        
    async def _predict_health_evolution(self) -> Dict[str, Any]:
        """Prédire évolution health services"""
        predictions = {}
        
        for service_metric_key, data_points in self.service_metrics.items():
            if len(data_points) < 30:  # Minimum données pour prédiction
                continue
                
            service_name, metric_name = service_metric_key.split(':', 1)
            
            # Préparer données temporelles
            recent_points = list(data_points)[-50:]  # 50 derniers points
            values = np.array([dp.value for dp in recent_points])
            
            # Prédiction simple avec moyenne mobile et tendance
            if len(values) >= 10:
                # Moyenne mobile
                window_size = min(10, len(values) // 3)
                moving_avg = np.convolve(values, np.ones(window_size), 'valid') / window_size
                
                # Tendance linéaire
                x = np.arange(len(moving_avg))
                slope, intercept = np.polyfit(x, moving_avg, 1)
                
                # Prédiction future
                future_steps = self.analysis_config.prediction_horizon_minutes // 5  # 5 min par step
                future_x = len(moving_avg) + future_steps
                predicted_value = slope * future_x + intercept
                
                # Calcul confidence basé sur variance récente
                recent_variance = np.var(values[-10:])
                confidence = max(0, 1 - (recent_variance / np.mean(values[-10:])))
                
                predictions[service_metric_key] = {
                    'service': service_name,
                    'metric': metric_name,
                    'current_value': float(values[-1]),
                    'predicted_value': float(predicted_value),
                    'prediction_confidence': float(confidence),
                    'trend_slope': float(slope),
                    'prediction_horizon_minutes': self.analysis_config.prediction_horizon_minutes
                }
                
        self.analysis_stats['predictions_made'] += len(predictions)
        
        return {
            'predictions_made': len(predictions),
            'prediction_details': predictions,
            'prediction_summary': await self._summarize_predictions(predictions)
        }
        
    async def _analyze_root_causes(self) -> Dict[str, Any]:
        """Analyser causes racines problems health"""
        root_causes = []
        
        # Identifier services avec problèmes
        problematic_services = []
        for service_metric_key, data_points in self.service_metrics.items():
            if not data_points:
                continue
                
            service_name, metric_name = service_metric_key.split(':', 1)
            recent_points = list(data_points)[-10:]
            
            # Vérifier si service a problèmes récents
            unhealthy_ratio = sum(1 for dp in recent_points if dp.status == 'unhealthy') / len(recent_points)
            if unhealthy_ratio > 0.3:
                problematic_services.append((service_name, metric_name, unhealthy_ratio))
                
        # Analyser causes potentielles
        for service_name, metric_name, severity in problematic_services:
            causes = await self._identify_potential_causes(service_name, metric_name, severity)
            root_causes.extend(causes)
            
        return {
            'problematic_services': len(problematic_services),
            'root_causes_identified': len(root_causes),
            'cause_analysis': root_causes,
            'priority_causes': sorted(root_causes, key=lambda x: x.get('confidence', 0), reverse=True)[:5]
        }
        
    # Méthodes utilitaires
    
    async def _update_anomaly_model(self, service_metric_key: str):
        """Mettre à jour modèle détection anomalies"""
        data_points = self.service_metrics[service_metric_key]
        
        if len(data_points) >= 100 and len(data_points) % 50 == 0:  # Update every 50 points
            values = np.array([[dp.value] for dp in data_points])
            
            # Initialiser ou mettre à jour modèle
            if service_metric_key not in self.anomaly_detectors:
                self.anomaly_detectors[service_metric_key] = IsolationForest(
                    contamination=1 - self.analysis_config.anomaly_threshold,
                    random_state=42
                )
                self.scalers[service_metric_key] = StandardScaler()
                
            # Entraîner modèle
            scaled_values = self.scalers[service_metric_key].fit_transform(values)
            self.anomaly_detectors[service_metric_key].fit(scaled_values)
            
    async def _detect_temporal_patterns(self, data_points: List[HealthMetricPoint]) -> List[HealthPattern]:
        """Détecter patterns temporels"""
        patterns = []
        
        if len(data_points) < 20:
            return patterns
            
        # Analyser patterns quotidiens/hebdomadaires
        hourly_values = defaultdict(list)
        for dp in data_points:
            hour = dp.timestamp.hour
            hourly_values[hour].append(dp.value)
            
        # Détecter patterns horaires
        if len(hourly_values) >= 12:  # Au moins 12 heures différentes
            pattern = HealthPattern(
                pattern_id=f"temporal_{data_points[0].service_name}_{int(datetime.now().timestamp())}",
                pattern_type="temporal_hourly",
                description=f"Hourly pattern detected for {data_points[0].service_name}",
                confidence=0.8,  # Placeholder
                frequency="hourly",
                services_affected=[data_points[0].service_name],
                time_range=(data_points[0].timestamp, data_points[-1].timestamp),
                characteristics={"hourly_distribution": dict(hourly_values)}
            )
            patterns.append(pattern)
            
        return patterns
        
    async def _detect_cyclic_patterns(self, data_points: List[HealthMetricPoint]) -> List[HealthPattern]:
        """Détecter patterns cycliques"""
        patterns = []
        
        if len(data_points) < 50:
            return patterns
            
        # Analyse FFT pour détecter cycles
        values = [dp.value for dp in data_points]
        if len(values) >= 8:
            try:
                fft_values = np.fft.fft(values)
                frequencies = np.fft.fftfreq(len(values))
                
                # Trouver fréquences dominantes
                dominant_freq_idx = np.argsort(np.abs(fft_values))[-3:]  # Top 3
                
                if len(dominant_freq_idx) > 0:
                    pattern = HealthPattern(
                        pattern_id=f"cyclic_{data_points[0].service_name}_{int(datetime.now().timestamp())}",
                        pattern_type="cyclic",
                        description=f"Cyclic pattern detected for {data_points[0].service_name}",
                        confidence=0.7,
                        frequency="cyclic",
                        services_affected=[data_points[0].service_name],
                        time_range=(data_points[0].timestamp, data_points[-1].timestamp),
                        characteristics={"dominant_frequencies": frequencies[dominant_freq_idx].tolist()}
                    )
                    patterns.append(pattern)
            except Exception as e:
                logger.warning(f"FFT analysis failed: {e}")
                
        return patterns
        
    async def _detect_statistical_anomalies(self, values: List[float], timestamps: List[datetime],
                                          service_name: str, metric_name: str) -> List[HealthAnomaly]:
        """Détecter anomalies statistiques"""
        anomalies = []
        
        if len(values) < 10:
            return anomalies
            
        # Calculer statistiques
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        threshold = 2.5 * std_val  # 2.5 sigma
        
        for i, (value, timestamp) in enumerate(zip(values, timestamps)):
            if abs(value - mean_val) > threshold:
                anomaly_score = abs(value - mean_val) / std_val
                
                anomaly = HealthAnomaly(
                    anomaly_id=f"stat_{service_name}_{metric_name}_{int(timestamp.timestamp())}",
                    service_name=service_name,
                    metric_name=metric_name,
                    anomaly_score=anomaly_score,
                    expected_value=mean_val,
                    actual_value=value,
                    timestamp=timestamp,
                    severity="high" if anomaly_score > 3 else "medium",
                    description=f"Statistical anomaly: {value:.2f} vs expected {mean_val:.2f}",
                    context={"method": "statistical", "threshold": threshold}
                )
                anomalies.append(anomaly)
                
        return anomalies
        
    async def _detect_ml_anomalies(self, values: List[float], timestamps: List[datetime],
                                 service_name: str, metric_name: str, 
                                 service_metric_key: str) -> List[HealthAnomaly]:
        """Détecter anomalies avec ML"""
        anomalies = []
        
        if service_metric_key not in self.anomaly_detectors:
            return anomalies
            
        try:
            # Préparer données
            recent_values = np.array([[v] for v in values[-20:]])  # 20 dernières valeurs
            recent_timestamps = timestamps[-20:]
            
            # Normaliser
            scaled_values = self.scalers[service_metric_key].transform(recent_values)
            
            # Prédire anomalies
            anomaly_predictions = self.anomaly_detectors[service_metric_key].predict(scaled_values)
            anomaly_scores = self.anomaly_detectors[service_metric_key].decision_function(scaled_values)
            
            for i, (prediction, score, value, timestamp) in enumerate(
                zip(anomaly_predictions, anomaly_scores, values[-20:], recent_timestamps)
            ):
                if prediction == -1:  # Anomalie détectée
                    anomaly = HealthAnomaly(
                        anomaly_id=f"ml_{service_name}_{metric_name}_{int(timestamp.timestamp())}",
                        service_name=service_name,
                        metric_name=metric_name,
                        anomaly_score=abs(score),
                        expected_value=statistics.mean(values),
                        actual_value=value,
                        timestamp=timestamp,
                        severity="high" if abs(score) > 0.5 else "medium",
                        description=f"ML anomaly detected: score {score:.3f}",
                        context={"method": "isolation_forest", "score": score}
                    )
                    anomalies.append(anomaly)
                    
        except Exception as e:
            logger.error(f"ML anomaly detection failed: {e}")
            
        return anomalies
        
    def _determine_trend_direction(self, slope: float, r_value: float) -> HealthTrendDirection:
        """Déterminer direction tendance"""
        if abs(r_value) < 0.3:
            return HealthTrendDirection.STABLE
        elif abs(r_value) < 0.5:
            return HealthTrendDirection.VOLATILE
        elif slope > 0:
            return HealthTrendDirection.IMPROVING
        else:
            return HealthTrendDirection.DEGRADING
            
    def _categorize_patterns(self, patterns: List[HealthPattern]) -> Dict[str, int]:
        """Catégoriser patterns détectés"""
        categories = defaultdict(int)
        for pattern in patterns:
            categories[pattern.pattern_type] += 1
        return dict(categories)
        
    def _calculate_severity_distribution(self, anomalies: List[HealthAnomaly]) -> Dict[str, int]:
        """Calculer distribution sévérité anomalies"""
        distribution = defaultdict(int)
        for anomaly in anomalies:
            distribution[anomaly.severity] += 1
        return dict(distribution)
        
    def _summarize_trends(self, trends: List[HealthTrend]) -> Dict[str, Any]:
        """Résumer tendances détectées"""
        if not trends:
            return {"message": "No trends detected"}
            
        direction_counts = defaultdict(int)
        confidence_sum = 0
        
        for trend in trends:
            direction_counts[trend.direction.value] += 1
            confidence_sum += trend.confidence
            
        return {
            "total_trends": len(trends),
            "average_confidence": confidence_sum / len(trends),
            "direction_distribution": dict(direction_counts),
            "high_confidence_trends": len([t for t in trends if t.confidence > 0.8])
        }
        
    async def _calculate_service_correlation(self, service1_data: Dict[str, List[float]], 
                                           service2_data: Dict[str, List[float]]) -> float:
        """Calculer corrélation entre services"""
        # Simplification: utiliser première métrique commune
        common_metrics = set(service1_data.keys()) & set(service2_data.keys())
        if not common_metrics:
            return 0.0
            
        metric = list(common_metrics)[0]
        values1 = service1_data[metric]
        values2 = service2_data[metric]
        
        min_len = min(len(values1), len(values2))
        if min_len < 5:
            return 0.0
            
        return float(np.corrcoef(values1[:min_len], values2[:min_len])[0, 1])
        
    async def _build_correlation_matrix(self, service_data: Dict[str, Dict[str, List[float]]]) -> Dict[str, Any]:
        """Construire matrice corrélation"""
        services = list(service_data.keys())
        matrix = {}
        
        for service in services:
            matrix[service] = {}
            for other_service in services:
                if service == other_service:
                    matrix[service][other_service] = 1.0
                else:
                    correlation = await self._calculate_service_correlation(
                        service_data[service], service_data[other_service]
                    )
                    matrix[service][other_service] = correlation
                    
        return matrix
        
    async def _generate_correlation_insights(self, correlations: Dict[str, float]) -> List[str]:
        """Générer insights corrélations"""
        insights = []
        
        high_correlations = [(k, v) for k, v in correlations.items() if abs(v) > 0.8]
        if high_correlations:
            insights.append(f"Found {len(high_correlations)} high correlation pairs")
            
        negative_correlations = [(k, v) for k, v in correlations.items() if v < -0.7]
        if negative_correlations:
            insights.append(f"Found {len(negative_correlations)} negative correlation pairs")
            
        return insights
        
    async def _summarize_predictions(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Résumer prédictions"""
        if not predictions:
            return {"message": "No predictions made"}
            
        total_confidence = sum(p['prediction_confidence'] for p in predictions.values())
        avg_confidence = total_confidence / len(predictions)
        
        improving_trends = len([p for p in predictions.values() if p['trend_slope'] > 0])
        degrading_trends = len([p for p in predictions.values() if p['trend_slope'] < 0])
        
        return {
            "total_predictions": len(predictions),
            "average_confidence": avg_confidence,
            "improving_trends": improving_trends,
            "degrading_trends": degrading_trends,
            "stable_trends": len(predictions) - improving_trends - degrading_trends
        }
        
    async def _identify_potential_causes(self, service_name: str, metric_name: str, 
                                       severity: float) -> List[Dict[str, Any]]:
        """Identifier causes potentielles problèmes"""
        causes = []
        
        # Causes génériques basées sur type métrique et sévérité
        if "response_time" in metric_name.lower():
            causes.append({
                "cause_type": "performance",
                "description": "High response time may indicate resource contention",
                "confidence": min(severity * 0.8, 1.0),
                "recommended_actions": ["Check CPU/memory usage", "Review database queries"]
            })
            
        if "error_rate" in metric_name.lower():
            causes.append({
                "cause_type": "application",
                "description": "High error rate suggests application issues",
                "confidence": min(severity * 0.9, 1.0),
                "recommended_actions": ["Check application logs", "Review recent deployments"]
            })
            
        if severity > 0.7:
            causes.append({
                "cause_type": "infrastructure",
                "description": "High severity suggests infrastructure problems",
                "confidence": severity,
                "recommended_actions": ["Check system resources", "Verify network connectivity"]
            })
            
        return causes
        
    async def _generate_analysis_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Générer synthèse analyse"""
        summary = {
            "analysis_completion": "success",
            "key_findings": [],
            "recommendations": [],
            "priority_items": []
        }
        
        # Extraire findings clés
        if 'anomaly_analysis' in results:
            anomaly_count = results['anomaly_analysis']['anomalies_detected']
            if anomaly_count > 0:
                summary["key_findings"].append(f"Detected {anomaly_count} health anomalies")
                summary["priority_items"].append("Investigate detected anomalies")
                
        if 'pattern_analysis' in results:
            pattern_count = results['pattern_analysis']['patterns_detected']
            if pattern_count > 0:
                summary["key_findings"].append(f"Identified {pattern_count} health patterns")
                
        if 'trend_analysis' in results:
            trend_summary = results['trend_analysis'].get('trend_summary', {})
            degrading_trends = trend_summary.get('direction_distribution', {}).get('degrading', 0)
            if degrading_trends > 0:
                summary["key_findings"].append(f"Found {degrading_trends} degrading trends")
                summary["priority_items"].append("Address degrading service trends")
                
        if 'root_cause_analysis' in results:
            cause_count = results['root_cause_analysis']['root_causes_identified']
            if cause_count > 0:
                summary["recommendations"].append(f"Review {cause_count} identified root causes")
                
        return summary

# Example usage et testing
if __name__ == "__main__":
    async def test_deep_analyzer():
        """Test analyseur health profond"""
        config = AnalysisConfig(
            window_size_minutes=30,
            anomaly_threshold=0.95,
            trend_analysis_points=15
        )
        
        analyzer = DeepHealthAnalyzer(config)
        
        # Simuler données health
        base_time = datetime.now()
        for i in range(100):
            # Données normales avec quelques anomalies
            value = 50 + 10 * np.sin(i * 0.1) + np.random.normal(0, 2)
            if i in [30, 60, 85]:  # Anomalies artificielles
                value += 30
                
            metric_point = HealthMetricPoint(
                timestamp=base_time + timedelta(minutes=i),
                service_name="test_service",
                metric_name="response_time_ms",
                value=value,
                status="healthy" if value < 70 else "unhealthy",
                category="performance"
            )
            
            await analyzer.ingest_health_data(metric_point)
            
        # Analyser health
        results = await analyzer.analyze_comprehensive_health()
        
        print("🔍 Deep Health Analysis Results:")
        print(f"Analysis ID: {results['analysis_id']}")
        print(f"Execution Time: {results['execution_time_seconds']:.2f}s")
        
        if 'anomaly_analysis' in results['results']:
            anomalies = results['results']['anomaly_analysis']['anomalies_detected']
            print(f"Anomalies Detected: {anomalies}")
            
        if 'pattern_analysis' in results['results']:
            patterns = results['results']['pattern_analysis']['patterns_detected']
            print(f"Patterns Detected: {patterns}")
            
        if 'trend_analysis' in results['results']:
            trends = results['results']['trend_analysis']['trends_detected']
            print(f"Trends Detected: {trends}")
            
        print(f"Key Findings: {results['analysis_summary']['key_findings']}")
        
        return results
        
    # Run test
    asyncio.run(test_deep_analyzer())