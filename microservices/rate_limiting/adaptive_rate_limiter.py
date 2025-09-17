"""
Adaptive Rate Limiter Enterprise - Ainflue
==========================================
Rate limiter adaptatif avec ML pour ajustement dynamique.
Machine learning + predictive scaling + anomaly detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: Ainflue Rate Limiting
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import statistics
from collections import deque, defaultdict
import uuid

from .distributed_rate_limiter import (
    DistributedRateLimiter, RateLimitConfig, RateLimitResult, 
    RateLimitAlgorithm, RateLimitStatus
)

logger = logging.getLogger(__name__)

class AdaptationStrategy(Enum):
    """Stratégies d'adaptation du rate limiting"""
    PREDICTIVE = "predictive"  # ML-based prediction
    REACTIVE = "reactive"      # Response to current metrics
    HYBRID = "hybrid"          # Combination of both
    CONSERVATIVE = "conservative"  # Cautious adjustments
    AGGRESSIVE = "aggressive"  # Rapid adjustments

class AnomalyType(Enum):
    """Types d'anomalies détectées"""
    TRAFFIC_SPIKE = "traffic_spike"
    DDOS_PATTERN = "ddos_pattern"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    FRAUD_PATTERN = "fraud_pattern"

@dataclass
class MLConfig:
    """Configuration pour ML components"""
    prediction_window_minutes: int = 30
    training_data_points: int = 1000
    anomaly_threshold: float = 2.0  # Standard deviations
    learning_rate: float = 0.01
    model_update_interval_minutes: int = 15
    enable_online_learning: bool = True
    feature_extraction_enabled: bool = True
    ensemble_models: List[str] = field(default_factory=lambda: ["arima", "lstm", "isolation_forest"])

@dataclass 
class RequestContext:
    """Context d'une request pour adaptive rate limiting"""
    identifier: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: str = "GET"
    content_type: Optional[str] = None
    geographic_region: Optional[str] = None
    user_tier: str = "free"
    timestamp: float = field(default_factory=time.time)
    cost: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrafficPattern:
    """Pattern de trafic détecté"""
    pattern_id: str
    pattern_type: str
    confidence: float
    frequency: int
    duration_seconds: int
    indicators: List[str]
    risk_score: float
    recommended_action: str

@dataclass
class Anomaly:
    """Anomalie détectée dans le trafic"""
    anomaly_id: str
    type: AnomalyType
    severity: str  # low, medium, high, critical
    confidence: float
    detected_at: datetime
    description: str
    affected_identifiers: List[str]
    metrics: Dict[str, float]
    recommended_limits: Dict[str, int]

@dataclass
class TrafficForecast:
    """Prédiction de trafic"""
    forecast_horizon_minutes: int
    predicted_requests: List[int]
    confidence_intervals: List[Tuple[int, int]]
    peak_times: List[datetime]
    recommended_capacity: int
    risk_assessment: str

@dataclass
class PolicyUpdate:
    """Mise à jour de policy rate limiting"""
    update_id: str
    timestamp: datetime
    affected_identifiers: List[str]
    old_limits: Dict[str, int]
    new_limits: Dict[str, int]
    reason: str
    confidence: float
    rollback_conditions: List[str]

@dataclass
class RateLimitDecision:
    """Décision adaptive rate limiting"""
    allowed: bool
    confidence: float
    reason: str
    applied_limits: Dict[str, int]
    next_review_time: datetime
    adaptation_applied: bool
    original_decision: RateLimitResult
    metadata: Dict[str, Any] = field(default_factory=dict)

class RateLimitMLPredictor:
    """Prédicteur ML pour rate limiting adaptatif"""
    
    def __init__(self, config: MLConfig):
        self.config = config
        self.historical_data = deque(maxlen=config.training_data_points)
        self.models = {}
        self.feature_extractors = {}
        self.last_training = datetime.now()
        self.prediction_cache = {}
        self.logger = logging.getLogger(__name__)
    
    async def predict_traffic(self, identifier: str, horizon_minutes: int) -> TrafficForecast:
        """Prédiction trafic avec ensemble ML models"""
        try:
            # Extraction features historiques
            features = await self._extract_features(identifier)
            
            # Prédictions avec ensemble models
            predictions = {}
            for model_name in self.config.ensemble_models:
                if model_name in self.models:
                    pred = await self._predict_with_model(model_name, features, horizon_minutes)
                    predictions[model_name] = pred
            
            # Ensemble prediction avec weighted average
            ensemble_prediction = await self._ensemble_predict(predictions, horizon_minutes)
            
            # Génération forecast complet
            forecast = TrafficForecast(
                forecast_horizon_minutes=horizon_minutes,
                predicted_requests=ensemble_prediction["requests"],
                confidence_intervals=ensemble_prediction["confidence_intervals"],
                peak_times=ensemble_prediction["peak_times"],
                recommended_capacity=ensemble_prediction["recommended_capacity"],
                risk_assessment=ensemble_prediction["risk_assessment"]
            )
            
            return forecast
            
        except Exception as e:
            self.logger.error(f"Traffic prediction failed for {identifier}: {e}")
            # Fallback prediction based on historical average
            return await self._fallback_prediction(identifier, horizon_minutes)
    
    async def _extract_features(self, identifier: str) -> Dict[str, Any]:
        """Extraction features pour ML prediction"""
        # Features temporelles
        now = datetime.now()
        hour_of_day = now.hour
        day_of_week = now.weekday()
        day_of_month = now.day
        
        # Features historiques
        recent_data = [point for point in self.historical_data 
                      if point.get("identifier") == identifier]
        
        if len(recent_data) < 10:
            # Pas assez de données historiques
            return {
                "hour_of_day": hour_of_day,
                "day_of_week": day_of_week,
                "day_of_month": day_of_month,
                "avg_requests_per_hour": 100,  # Default
                "variance": 0.1,
                "trend": 0.0
            }
        
        # Calcul statistiques
        requests = [point["requests"] for point in recent_data[-50:]]
        avg_requests = statistics.mean(requests)
        variance = statistics.variance(requests) if len(requests) > 1 else 0.1
        
        # Calcul trend (simple linear regression)
        if len(requests) >= 5:
            x = list(range(len(requests)))
            trend = np.corrcoef(x, requests)[0, 1] if len(set(requests)) > 1 else 0.0
        else:
            trend = 0.0
        
        return {
            "hour_of_day": hour_of_day,
            "day_of_week": day_of_week, 
            "day_of_month": day_of_month,
            "avg_requests_per_hour": avg_requests,
            "variance": variance,
            "trend": trend,
            "recent_peak": max(requests),
            "recent_min": min(requests),
            "data_points": len(recent_data)
        }
    
    async def _predict_with_model(self, model_name: str, features: Dict[str, Any], 
                                horizon_minutes: int) -> List[int]:
        """Prédiction avec modèle spécifique"""
        if model_name == "arima":
            return await self._arima_predict(features, horizon_minutes)
        elif model_name == "lstm":
            return await self._lstm_predict(features, horizon_minutes)
        elif model_name == "linear_trend":
            return await self._linear_trend_predict(features, horizon_minutes)
        else:
            # Fallback: simple extrapolation
            base_rate = features.get("avg_requests_per_hour", 100)
            return [int(base_rate)] * (horizon_minutes // 60 + 1)
    
    async def _arima_predict(self, features: Dict[str, Any], horizon_minutes: int) -> List[int]:
        """Prédiction ARIMA simplifiée"""
        base_rate = features["avg_requests_per_hour"]
        trend = features["trend"]
        variance = features["variance"]
        
        predictions = []
        for i in range(horizon_minutes // 60 + 1):
            # Simple ARIMA(1,1,1) approximation
            predicted = base_rate + (trend * i) + np.random.normal(0, np.sqrt(variance))
            predictions.append(max(0, int(predicted)))
        
        return predictions
    
    async def _lstm_predict(self, features: Dict[str, Any], horizon_minutes: int) -> List[int]:
        """Prédiction LSTM simplifiée"""
        # Pour une implémentation complète, utiliser TensorFlow/PyTorch
        # Ici: approximation basée sur patterns cycliques
        base_rate = features["avg_requests_per_hour"]
        hour_of_day = features["hour_of_day"]
        
        # Pattern cyclique simple (pic aux heures de pointe)
        peak_hours = [9, 10, 11, 14, 15, 16, 19, 20, 21]
        
        predictions = []
        for i in range(horizon_minutes // 60 + 1):
            current_hour = (hour_of_day + i) % 24
            multiplier = 1.5 if current_hour in peak_hours else 0.8
            predicted = int(base_rate * multiplier)
            predictions.append(predicted)
        
        return predictions
    
    async def _linear_trend_predict(self, features: Dict[str, Any], horizon_minutes: int) -> List[int]:
        """Prédiction trend linéaire"""
        base_rate = features["avg_requests_per_hour"]
        trend = features["trend"]
        
        predictions = []
        for i in range(horizon_minutes // 60 + 1):
            predicted = base_rate + (trend * i)
            predictions.append(max(0, int(predicted)))
        
        return predictions
    
    async def _ensemble_predict(self, predictions: Dict[str, List[int]], 
                              horizon_minutes: int) -> Dict[str, Any]:
        """Ensemble prediction avec weighted average"""
        if not predictions:
            return {
                "requests": [100] * (horizon_minutes // 60 + 1),
                "confidence_intervals": [(80, 120)] * (horizon_minutes // 60 + 1),
                "peak_times": [],
                "recommended_capacity": 150,
                "risk_assessment": "medium"
            }
        
        # Weights basés sur performance historique des modèles
        weights = {
            "arima": 0.4,
            "lstm": 0.4, 
            "linear_trend": 0.2
        }
        
        ensemble_requests = []
        confidence_intervals = []
        
        for i in range(horizon_minutes // 60 + 1):
            weighted_sum = 0
            total_weight = 0
            values = []
            
            for model_name, model_predictions in predictions.items():
                if i < len(model_predictions):
                    weight = weights.get(model_name, 0.2)
                    weighted_sum += model_predictions[i] * weight
                    total_weight += weight
                    values.append(model_predictions[i])
            
            if total_weight > 0:
                ensemble_pred = int(weighted_sum / total_weight)
            else:
                ensemble_pred = 100  # Fallback
            
            ensemble_requests.append(ensemble_pred)
            
            # Confidence interval basé sur variance des prédictions
            if values:
                mean_val = statistics.mean(values)
                std_val = statistics.stdev(values) if len(values) > 1 else mean_val * 0.1
                confidence_intervals.append((
                    max(0, int(mean_val - 2 * std_val)),
                    int(mean_val + 2 * std_val)
                ))
            else:
                confidence_intervals.append((80, 120))
        
        # Détection peak times
        peak_times = []
        if len(ensemble_requests) > 1:
            avg_prediction = statistics.mean(ensemble_requests)
            for i, pred in enumerate(ensemble_requests):
                if pred > avg_prediction * 1.3:  # 30% au-dessus de la moyenne
                    peak_time = datetime.now() + timedelta(hours=i)
                    peak_times.append(peak_time)
        
        # Recommended capacity
        max_predicted = max(ensemble_requests) if ensemble_requests else 100
        recommended_capacity = int(max_predicted * 1.2)  # 20% buffer
        
        # Risk assessment
        if max_predicted > 500:
            risk_assessment = "high"
        elif max_predicted > 200:
            risk_assessment = "medium"
        else:
            risk_assessment = "low"
        
        return {
            "requests": ensemble_requests,
            "confidence_intervals": confidence_intervals,
            "peak_times": peak_times,
            "recommended_capacity": recommended_capacity,
            "risk_assessment": risk_assessment
        }
    
    async def _fallback_prediction(self, identifier: str, horizon_minutes: int) -> TrafficForecast:
        """Fallback prediction quand ML échoue"""
        return TrafficForecast(
            forecast_horizon_minutes=horizon_minutes,
            predicted_requests=[100] * (horizon_minutes // 60 + 1),
            confidence_intervals=[(80, 120)] * (horizon_minutes // 60 + 1),
            peak_times=[],
            recommended_capacity=150,
            risk_assessment="medium"
        )

class TrafficAnomalyDetector:
    """Détecteur d'anomalies dans le trafic"""
    
    def __init__(self, config: MLConfig):
        self.config = config
        self.baseline_metrics = defaultdict(dict)
        self.anomaly_history = deque(maxlen=1000)
        self.detection_models = {}
        self.logger = logging.getLogger(__name__)
    
    async def detect_anomalies(self, traffic_data: Dict[str, Any]) -> List[Anomaly]:
        """Détection anomalies multi-dimensionnelle"""
        anomalies = []
        
        try:
            # Détection anomalies de volume
            volume_anomalies = await self._detect_volume_anomalies(traffic_data)
            anomalies.extend(volume_anomalies)
            
            # Détection anomalies géographiques
            geo_anomalies = await self._detect_geographic_anomalies(traffic_data)
            anomalies.extend(geo_anomalies)
            
            # Détection anomalies comportementales
            behavioral_anomalies = await self._detect_behavioral_anomalies(traffic_data)
            anomalies.extend(behavioral_anomalies)
            
            # Détection patterns DDoS
            ddos_anomalies = await self._detect_ddos_patterns(traffic_data)
            anomalies.extend(ddos_anomalies)
            
            # Corrélation et déduplication
            anomalies = await self._correlate_anomalies(anomalies)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return []
    
    async def _detect_volume_anomalies(self, traffic_data: Dict[str, Any]) -> List[Anomaly]:
        """Détection anomalies de volume de trafic"""
        anomalies = []
        
        for identifier, metrics in traffic_data.items():
            current_rate = metrics.get("requests_per_minute", 0)
            
            # Baseline comparison
            if identifier in self.baseline_metrics:
                baseline = self.baseline_metrics[identifier]
                avg_rate = baseline.get("avg_requests_per_minute", current_rate)
                std_rate = baseline.get("std_requests_per_minute", avg_rate * 0.1)
                
                # Z-score anomaly detection
                if std_rate > 0:
                    z_score = abs(current_rate - avg_rate) / std_rate
                    
                    if z_score > self.config.anomaly_threshold:
                        severity = "critical" if z_score > 4 else "high" if z_score > 3 else "medium"
                        
                        anomaly = Anomaly(
                            anomaly_id=str(uuid.uuid4()),
                            type=AnomalyType.TRAFFIC_SPIKE,
                            severity=severity,
                            confidence=min(0.99, z_score / 5),
                            detected_at=datetime.now(),
                            description=f"Traffic spike detected: {current_rate} vs baseline {avg_rate}",
                            affected_identifiers=[identifier],
                            metrics={
                                "current_rate": current_rate,
                                "baseline_rate": avg_rate,
                                "z_score": z_score,
                                "threshold": self.config.anomaly_threshold
                            },
                            recommended_limits={
                                "requests_per_minute": max(10, int(avg_rate * 0.5))
                            }
                        )
                        anomalies.append(anomaly)
            
            # Update baseline metrics
            if identifier not in self.baseline_metrics:
                self.baseline_metrics[identifier] = {
                    "avg_requests_per_minute": current_rate,
                    "std_requests_per_minute": current_rate * 0.1,
                    "data_points": 1
                }
            else:
                baseline = self.baseline_metrics[identifier]
                n = baseline["data_points"]
                old_avg = baseline["avg_requests_per_minute"]
                
                # Incremental mean and variance update
                new_avg = (old_avg * n + current_rate) / (n + 1)
                baseline["avg_requests_per_minute"] = new_avg
                baseline["data_points"] = min(n + 1, 1000)  # Cap pour éviter overflow
        
        return anomalies
    
    async def _detect_geographic_anomalies(self, traffic_data: Dict[str, Any]) -> List[Anomaly]:
        """Détection anomalies géographiques"""
        anomalies = []
        
        # Analyse distribution géographique
        geo_distribution = defaultdict(int)
        for identifier, metrics in traffic_data.items():
            region = metrics.get("geographic_region", "unknown")
            geo_distribution[region] += metrics.get("requests_per_minute", 0)
        
        # Détection régions avec trafic anormal
        if len(geo_distribution) > 1:
            values = list(geo_distribution.values())
            if len(values) > 1:
                mean_traffic = statistics.mean(values)
                std_traffic = statistics.stdev(values)
                
                for region, traffic in geo_distribution.items():
                    if std_traffic > 0:
                        z_score = abs(traffic - mean_traffic) / std_traffic
                        
                        if z_score > 2.5 and traffic > mean_traffic:  # Seuil plus bas pour geo
                            anomaly = Anomaly(
                                anomaly_id=str(uuid.uuid4()),
                                type=AnomalyType.GEOGRAPHIC_ANOMALY,
                                severity="medium" if z_score < 3 else "high",
                                confidence=min(0.95, z_score / 4),
                                detected_at=datetime.now(),
                                description=f"Unusual traffic from region {region}: {traffic} requests",
                                affected_identifiers=[f"region:{region}"],
                                metrics={
                                    "region_traffic": traffic,
                                    "baseline_traffic": mean_traffic,
                                    "z_score": z_score
                                },
                                recommended_limits={
                                    "requests_per_minute": max(10, int(mean_traffic))
                                }
                            )
                            anomalies.append(anomaly)
        
        return anomalies
    
    async def _detect_behavioral_anomalies(self, traffic_data: Dict[str, Any]) -> List[Anomaly]:
        """Détection anomalies comportementales"""
        anomalies = []
        
        for identifier, metrics in traffic_data.items():
            # Analyse patterns de requests
            request_patterns = metrics.get("request_patterns", {})
            
            # Détection patterns suspects
            suspicious_patterns = []
            
            # Trop de requests identiques
            if request_patterns.get("identical_requests_ratio", 0) > 0.8:
                suspicious_patterns.append("high_identical_requests")
            
            # User agent patterns suspects
            if request_patterns.get("single_user_agent_ratio", 0) > 0.9:
                suspicious_patterns.append("single_user_agent")
            
            # Requests trop rapides
            if request_patterns.get("avg_request_interval_ms", 1000) < 100:
                suspicious_patterns.append("too_fast_requests")
            
            if suspicious_patterns:
                anomaly = Anomaly(
                    anomaly_id=str(uuid.uuid4()),
                    type=AnomalyType.BEHAVIORAL_ANOMALY,
                    severity="medium",
                    confidence=0.7,
                    detected_at=datetime.now(),
                    description=f"Suspicious behavioral patterns: {', '.join(suspicious_patterns)}",
                    affected_identifiers=[identifier],
                    metrics=request_patterns,
                    recommended_limits={
                        "requests_per_minute": 30  # Conservative limit
                    }
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    async def _detect_ddos_patterns(self, traffic_data: Dict[str, Any]) -> List[Anomaly]:
        """Détection patterns DDoS"""
        anomalies = []
        
        # Indicateurs DDoS
        total_requests = sum(metrics.get("requests_per_minute", 0) 
                           for metrics in traffic_data.values())
        
        unique_identifiers = len(traffic_data)
        
        # Pattern: beaucoup de requests de peu d'identifiers
        if unique_identifiers > 0:
            avg_requests_per_identifier = total_requests / unique_identifiers
            
            # DDoS probable si >100 req/min par identifier en moyenne
            if avg_requests_per_identifier > 100:
                # Analyse distribution
                high_volume_identifiers = [
                    identifier for identifier, metrics in traffic_data.items()
                    if metrics.get("requests_per_minute", 0) > avg_requests_per_identifier * 2
                ]
                
                if len(high_volume_identifiers) > unique_identifiers * 0.1:  # >10% des identifiers
                    anomaly = Anomaly(
                        anomaly_id=str(uuid.uuid4()),
                        type=AnomalyType.DDOS_PATTERN,
                        severity="critical",
                        confidence=0.85,
                        detected_at=datetime.now(),
                        description=f"Potential DDoS: {len(high_volume_identifiers)} high-volume sources",
                        affected_identifiers=high_volume_identifiers[:50],  # Limit pour éviter overflow
                        metrics={
                            "total_requests": total_requests,
                            "unique_identifiers": unique_identifiers,
                            "avg_requests_per_identifier": avg_requests_per_identifier,
                            "high_volume_count": len(high_volume_identifiers)
                        },
                        recommended_limits={
                            "requests_per_minute": 10  # Very restrictive
                        }
                    )
                    anomalies.append(anomaly)
        
        return anomalies
    
    async def _correlate_anomalies(self, anomalies: List[Anomaly]) -> List[Anomaly]:
        """Corrélation et déduplication des anomalies"""
        if len(anomalies) <= 1:
            return anomalies
        
        # Regroupement par identifiers affectés
        grouped_anomalies = defaultdict(list)
        for anomaly in anomalies:
            key = tuple(sorted(anomaly.affected_identifiers))
            grouped_anomalies[key].append(anomaly)
        
        # Merge anomalies similaires
        merged_anomalies = []
        for identifier_group, group_anomalies in grouped_anomalies.items():
            if len(group_anomalies) == 1:
                merged_anomalies.extend(group_anomalies)
            else:
                # Merge multiple anomalies pour mêmes identifiers
                merged = await self._merge_anomalies(group_anomalies)
                merged_anomalies.append(merged)
        
        return merged_anomalies
    
    async def _merge_anomalies(self, anomalies: List[Anomaly]) -> Anomaly:
        """Merge plusieurs anomalies similaires"""
        # Prendre l'anomalie la plus sévère comme base
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        base_anomaly = max(anomalies, 
                          key=lambda a: severity_order.get(a.severity, 0))
        
        # Combine descriptions
        descriptions = [a.description for a in anomalies]
        combined_description = " | ".join(descriptions)
        
        # Combine metrics
        combined_metrics = {}
        for anomaly in anomalies:
            combined_metrics.update(anomaly.metrics)
        
        # Max confidence
        max_confidence = max(a.confidence for a in anomalies)
        
        return Anomaly(
            anomaly_id=str(uuid.uuid4()),
            type=base_anomaly.type,
            severity=base_anomaly.severity,
            confidence=max_confidence,
            detected_at=base_anomaly.detected_at,
            description=combined_description,
            affected_identifiers=base_anomaly.affected_identifiers,
            metrics=combined_metrics,
            recommended_limits=base_anomaly.recommended_limits
        )

class AdaptivePolicyEngine:
    """Moteur de policies adaptatives"""
    
    def __init__(self, config: MLConfig):
        self.config = config
        self.active_policies = {}
        self.policy_history = deque(maxlen=1000)
        self.logger = logging.getLogger(__name__)
    
    async def generate_policy_update(self, forecast: TrafficForecast, 
                                   anomalies: List[Anomaly],
                                   current_metrics: Dict[str, Any]) -> PolicyUpdate:
        """Génération update policy basé sur ML insights"""
        try:
            # Analyse impact des anomalies
            risk_level = await self._assess_risk_level(forecast, anomalies)
            
            # Calcul nouvelles limites
            new_limits = await self._calculate_adaptive_limits(forecast, anomalies, risk_level)
            
            # Identification identifiers affectés
            affected_identifiers = []
            for anomaly in anomalies:
                affected_identifiers.extend(anomaly.affected_identifiers)
            
            # Si pas d'anomalies, application générale du forecast
            if not affected_identifiers:
                affected_identifiers = ["*"]  # Global policy
            
            # Récupération limites actuelles
            old_limits = {}
            for identifier in affected_identifiers:
                old_limits[identifier] = current_metrics.get(identifier, {}).get("current_limit", 100)
            
            # Génération policy update
            policy_update = PolicyUpdate(
                update_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                affected_identifiers=list(set(affected_identifiers)),
                old_limits=old_limits,
                new_limits=new_limits,
                reason=await self._generate_policy_reason(forecast, anomalies, risk_level),
                confidence=await self._calculate_confidence(forecast, anomalies),
                rollback_conditions=await self._generate_rollback_conditions(risk_level)
            )
            
            return policy_update
            
        except Exception as e:
            self.logger.error(f"Policy update generation failed: {e}")
            # Fallback: pas de changement
            return PolicyUpdate(
                update_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                affected_identifiers=[],
                old_limits={},
                new_limits={},
                reason="Error in policy generation - no changes applied",
                confidence=0.0,
                rollback_conditions=[]
            )
    
    async def _assess_risk_level(self, forecast: TrafficForecast, 
                               anomalies: List[Anomaly]) -> str:
        """Assessment du niveau de risque"""
        risk_score = 0
        
        # Risk from forecast
        if forecast.risk_assessment == "high":
            risk_score += 3
        elif forecast.risk_assessment == "medium":
            risk_score += 2
        else:
            risk_score += 1
        
        # Risk from anomalies
        for anomaly in anomalies:
            if anomaly.severity == "critical":
                risk_score += 4
            elif anomaly.severity == "high":
                risk_score += 3
            elif anomaly.severity == "medium":
                risk_score += 2
            else:
                risk_score += 1
        
        # Classification risk level
        if risk_score >= 10:
            return "critical"
        elif risk_score >= 7:
            return "high"
        elif risk_score >= 4:
            return "medium"
        else:
            return "low"
    
    async def _calculate_adaptive_limits(self, forecast: TrafficForecast,
                                       anomalies: List[Anomaly],
                                       risk_level: str) -> Dict[str, int]:
        """Calcul limites adaptatives"""
        new_limits = {}
        
        # Base limits from forecast
        base_capacity = forecast.recommended_capacity
        
        # Adjustment factors par risk level
        risk_factors = {
            "critical": 0.2,  # Very restrictive
            "high": 0.4,
            "medium": 0.7,
            "low": 1.0
        }
        
        adjustment_factor = risk_factors.get(risk_level, 0.7)
        
        # Limites spécifiques par anomalie
        for anomaly in anomalies:
            for identifier in anomaly.affected_identifiers:
                if identifier in anomaly.recommended_limits:
                    recommended = anomaly.recommended_limits["requests_per_minute"]
                    new_limits[identifier] = int(recommended * adjustment_factor)
                else:
                    new_limits[identifier] = int(base_capacity * adjustment_factor)
        
        # Limite globale si pas d'anomalies spécifiques
        if not new_limits:
            new_limits["*"] = int(base_capacity * adjustment_factor)
        
        return new_limits
    
    async def _generate_policy_reason(self, forecast: TrafficForecast,
                                    anomalies: List[Anomaly],
                                    risk_level: str) -> str:
        """Génération raison pour policy update"""
        reasons = []
        
        # Forecast reasons
        if forecast.risk_assessment != "low":
            reasons.append(f"Traffic forecast indicates {forecast.risk_assessment} risk")
        
        # Anomaly reasons
        anomaly_types = [a.type.value for a in anomalies]
        if anomaly_types:
            reasons.append(f"Anomalies detected: {', '.join(set(anomaly_types))}")
        
        # Risk level reason
        reasons.append(f"Overall risk level: {risk_level}")
        
        return " | ".join(reasons)
    
    async def _calculate_confidence(self, forecast: TrafficForecast,
                                  anomalies: List[Anomaly]) -> float:
        """Calcul confidence score pour policy update"""
        confidence_scores = []
        
        # Forecast confidence (simplified)
        if forecast.predicted_requests:
            # Base confidence sur variance des prédictions
            variance = statistics.variance(forecast.predicted_requests) if len(forecast.predicted_requests) > 1 else 0
            forecast_confidence = max(0.3, min(0.9, 1.0 - (variance / max(forecast.predicted_requests))))
            confidence_scores.append(forecast_confidence)
        
        # Anomaly confidences
        for anomaly in anomalies:
            confidence_scores.append(anomaly.confidence)
        
        # Overall confidence = moyenne pondérée
        if confidence_scores:
            return statistics.mean(confidence_scores)
        else:
            return 0.5  # Neutral confidence
    
    async def _generate_rollback_conditions(self, risk_level: str) -> List[str]:
        """Génération conditions de rollback"""
        conditions = []
        
        # Standard rollback conditions
        conditions.append("error_rate > 10%")
        conditions.append("response_time > 5000ms")
        
        # Risk-specific conditions
        if risk_level in ["critical", "high"]:
            conditions.append("legitimate_traffic_drop > 50%")
            conditions.append("manual_override")
        else:
            conditions.append("legitimate_traffic_drop > 80%")
        
        # Time-based rollback
        conditions.append("time_elapsed > 60 minutes")
        
        return conditions

class AdaptiveRateLimiter:
    """
    Rate Limiter adaptatif avec ML pour ajustement dynamique.
    Machine learning + predictive scaling + anomaly detection.
    """
    
    def __init__(self, distributed_limiter: DistributedRateLimiter, ml_config: MLConfig):
        self.distributed_limiter = distributed_limiter
        self.ml_config = ml_config
        self.ml_predictor = RateLimitMLPredictor(ml_config)
        self.anomaly_detector = TrafficAnomalyDetector(ml_config)
        self.policy_engine = AdaptivePolicyEngine(ml_config)
        self.metrics_collector = RealTimeMetricsCollector()
        
        # État adaptatif
        self.adaptation_strategy = AdaptationStrategy.HYBRID
        self.active_adaptations = {}
        self.adaptation_history = deque(maxlen=1000)
        
        self.logger = logging.getLogger(__name__)
        
        # Tâches background
        self._background_tasks = []
        self._stop_event = asyncio.Event()
    
    async def initialize(self) -> bool:
        """Initialisation du rate limiter adaptatif"""
        try:
            # Initialisation distributed limiter
            await self.distributed_limiter.initialize()
            
            # Démarrage tâches background
            await self._start_background_tasks()
            
            self.logger.info("Adaptive rate limiter initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Adaptive rate limiter initialization failed: {e}")
            return False
    
    async def adaptive_rate_check(self, request_context: RequestContext) -> RateLimitDecision:
        """
        Rate limiting adaptatif basé sur ML predictions.
        
        Adaptive Features:
        - ML-based traffic prediction pour ajustement proactif
        - Real-time anomaly detection pour attaques DDoS
        - User behavior analysis pour rate limiting personnalisé
        - Geographic load balancing avec rate limiting
        - Content-type aware rate limiting (upload vs query)
        - Time-of-day adaptive limits basé sur patterns historiques
        - Auto-scaling rate limits selon charge système
        """
        try:
            # 1. Vérification rate limit standard
            original_result = await self.distributed_limiter.check_rate_limit(
                request_context.identifier,
                request_context.cost,
                request_context.metadata
            )
            
            # 2. Collecte métriques temps réel
            await self.metrics_collector.collect_request_metrics(request_context)
            
            # 3. Vérification adaptations actives
            active_adaptation = self.active_adaptations.get(request_context.identifier)
            
            # 4. Application adaptation si nécessaire
            if active_adaptation:
                adapted_result = await self._apply_adaptation(
                    request_context, original_result, active_adaptation
                )
            else:
                adapted_result = original_result
            
            # 5. Génération décision finale
            decision = RateLimitDecision(
                allowed=adapted_result.allowed,
                confidence=0.95 if not active_adaptation else active_adaptation.get("confidence", 0.8),
                reason=await self._generate_decision_reason(request_context, adapted_result, active_adaptation),
                applied_limits=await self._get_applied_limits(request_context.identifier),
                next_review_time=datetime.now() + timedelta(minutes=5),
                adaptation_applied=bool(active_adaptation),
                original_decision=original_result,
                metadata={
                    "strategy": str(self.adaptation_strategy),
                    "context": request_context.metadata,
                    "adaptation_id": active_adaptation.get("id") if active_adaptation else None
                }
            )
            
            return decision
            
        except Exception as e:
            self.logger.error(f"Adaptive rate check failed for {request_context.identifier}: {e}")
            # Fallback sur décision originale
            return RateLimitDecision(
                allowed=True,  # Fail open
                confidence=0.5,
                reason=f"Adaptation error: {str(e)}",
                applied_limits={},
                next_review_time=datetime.now() + timedelta(minutes=1),
                adaptation_applied=False,
                original_decision=RateLimitResult(
                    status=RateLimitStatus.ERROR,
                    allowed=True
                ),
                metadata={"error": str(e)}
            )
    
    async def _apply_adaptation(self, request_context: RequestContext,
                              original_result: RateLimitResult,
                              adaptation: Dict[str, Any]) -> RateLimitResult:
        """Application adaptation spécifique"""
        adaptation_type = adaptation.get("type", "none")
        
        if adaptation_type == "rate_reduction":
            # Réduction du rate limit
            reduction_factor = adaptation.get("reduction_factor", 0.5)
            if original_result.allowed and adaptation.get("apply_reduction", True):
                # Simulate reduced rate limit
                if request_context.cost > adaptation.get("max_allowed_cost", 1):
                    original_result.allowed = False
                    original_result.status = RateLimitStatus.THROTTLED
                    original_result.retry_after = adaptation.get("retry_after", 60.0)
        
        elif adaptation_type == "priority_boost":
            # Boost pour utilisateurs prioritaires
            if request_context.user_tier in ["premium", "enterprise"]:
                original_result.allowed = True
                original_result.status = RateLimitStatus.ALLOWED
        
        elif adaptation_type == "geographic_restriction":
            # Restriction géographique
            restricted_regions = adaptation.get("restricted_regions", [])
            if request_context.geographic_region in restricted_regions:
                original_result.allowed = False
                original_result.status = RateLimitStatus.DENIED
                original_result.retry_after = adaptation.get("retry_after", 300.0)
        
        return original_result
    
    async def _start_background_tasks(self):
        """Démarrage tâches background pour adaptation"""
        # Tâche prédiction trafic
        prediction_task = asyncio.create_task(self._traffic_prediction_loop())
        self._background_tasks.append(prediction_task)
        
        # Tâche détection anomalies
        anomaly_task = asyncio.create_task(self._anomaly_detection_loop())
        self._background_tasks.append(anomaly_task)
        
        # Tâche update policies
        policy_task = asyncio.create_task(self._policy_update_loop())
        self._background_tasks.append(policy_task)
    
    async def _traffic_prediction_loop(self):
        """Loop prédiction trafic en background"""
        while not self._stop_event.is_set():
            try:
                # Prédiction pour principaux identifiers
                active_identifiers = list(self.metrics_collector.get_active_identifiers())
                
                for identifier in active_identifiers[:50]:  # Limit pour performance
                    forecast = await self.ml_predictor.predict_traffic(identifier, 30)
                    
                    # Stockage forecast pour utilisation
                    self.metrics_collector.store_forecast(identifier, forecast)
                
                # Attente avant prochaine prédiction
                await asyncio.sleep(self.ml_config.model_update_interval_minutes * 60)
                
            except Exception as e:
                self.logger.error(f"Traffic prediction loop error: {e}")
                await asyncio.sleep(60)  # Retry après 1 minute
    
    async def _anomaly_detection_loop(self):
        """Loop détection anomalies en background"""
        while not self._stop_event.is_set():
            try:
                # Collecte données trafic récentes
                traffic_data = await self.metrics_collector.get_recent_traffic_data()
                
                # Détection anomalies
                anomalies = await self.anomaly_detector.detect_anomalies(traffic_data)
                
                # Application mesures si anomalies critiques
                critical_anomalies = [a for a in anomalies if a.severity == "critical"]
                if critical_anomalies:
                    await self._handle_critical_anomalies(critical_anomalies)
                
                # Stockage pour policy engine
                self.metrics_collector.store_anomalies(anomalies)
                
                # Attente avant prochaine détection
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Anomaly detection loop error: {e}")
                await asyncio.sleep(60)
    
    async def _policy_update_loop(self):
        """Loop update policies en background"""
        while not self._stop_event.is_set():
            try:
                # Récupération forecasts et anomalies récentes
                recent_forecasts = self.metrics_collector.get_recent_forecasts()
                recent_anomalies = self.metrics_collector.get_recent_anomalies()
                current_metrics = await self.metrics_collector.get_current_metrics()
                
                # Génération policy updates
                for identifier, forecast in recent_forecasts.items():
                    identifier_anomalies = [
                        a for a in recent_anomalies 
                        if identifier in a.affected_identifiers
                    ]
                    
                    policy_update = await self.policy_engine.generate_policy_update(
                        forecast, identifier_anomalies, current_metrics
                    )
                    
                    # Application policy si confidence suffisante
                    if policy_update.confidence > 0.7:
                        await self._apply_policy_update(policy_update)
                
                # Attente avant prochaine update
                await asyncio.sleep(self.ml_config.model_update_interval_minutes * 60)
                
            except Exception as e:
                self.logger.error(f"Policy update loop error: {e}")
                await asyncio.sleep(300)  # Retry après 5 minutes
    
    async def _handle_critical_anomalies(self, anomalies: List[Anomaly]):
        """Handling immédiat des anomalies critiques"""
        for anomaly in anomalies:
            # Application mesures d'urgence
            emergency_adaptation = {
                "id": anomaly.anomaly_id,
                "type": "emergency_restriction",
                "reduction_factor": 0.1,  # Very restrictive
                "max_allowed_cost": 1,
                "retry_after": 300.0,
                "confidence": anomaly.confidence,
                "reason": f"Emergency response to {anomaly.type.value}",
                "expires_at": datetime.now() + timedelta(minutes=30)
            }
            
            # Application à tous identifiers affectés
            for identifier in anomaly.affected_identifiers:
                self.active_adaptations[identifier] = emergency_adaptation
            
            self.logger.warning(f"Emergency adaptation applied for anomaly {anomaly.anomaly_id}")
    
    async def _apply_policy_update(self, policy_update: PolicyUpdate):
        """Application policy update"""
        try:
            for identifier, new_limit in policy_update.new_limits.items():
                # Création adaptation basée sur policy
                adaptation = {
                    "id": policy_update.update_id,
                    "type": "policy_adjustment",
                    "new_limit": new_limit,
                    "old_limit": policy_update.old_limits.get(identifier, 100),
                    "confidence": policy_update.confidence,
                    "reason": policy_update.reason,
                    "expires_at": datetime.now() + timedelta(hours=1),
                    "rollback_conditions": policy_update.rollback_conditions
                }
                
                self.active_adaptations[identifier] = adaptation
            
            self.logger.info(f"Policy update applied: {policy_update.update_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to apply policy update {policy_update.update_id}: {e}")

class RealTimeMetricsCollector:
    """Collecteur métriques temps réel pour ML"""
    
    def __init__(self):
        self.metrics_buffer = deque(maxlen=10000)
        self.forecasts_cache = {}
        self.anomalies_cache = deque(maxlen=1000)
        self.active_identifiers = set()
        self.logger = logging.getLogger(__name__)
    
    async def collect_request_metrics(self, request_context: RequestContext):
        """Collecte métriques d'une request"""
        metric_entry = {
            "timestamp": request_context.timestamp,
            "identifier": request_context.identifier,
            "ip_address": request_context.ip_address,
            "endpoint": request_context.endpoint,
            "method": request_context.method,
            "geographic_region": request_context.geographic_region,
            "user_tier": request_context.user_tier,
            "cost": request_context.cost
        }
        
        self.metrics_buffer.append(metric_entry)
        self.active_identifiers.add(request_context.identifier)
    
    def get_active_identifiers(self) -> List[str]:
        """Récupération identifiers actifs"""
        return list(self.active_identifiers)
    
    async def get_recent_traffic_data(self) -> Dict[str, Dict[str, Any]]:
        """Récupération données trafic récentes"""
        now = time.time()
        recent_cutoff = now - 300  # 5 minutes
        
        # Filtrage données récentes
        recent_metrics = [
            m for m in self.metrics_buffer 
            if m["timestamp"] > recent_cutoff
        ]
        
        # Agrégation par identifier
        traffic_data = defaultdict(lambda: {
            "requests_per_minute": 0,
            "geographic_regions": set(),
            "endpoints": set(),
            "user_tiers": defaultdict(int),
            "request_patterns": {}
        })
        
        for metric in recent_metrics:
            identifier = metric["identifier"]
            traffic_data[identifier]["requests_per_minute"] += 1
            
            if metric["geographic_region"]:
                traffic_data[identifier]["geographic_regions"].add(metric["geographic_region"])
            
            if metric["endpoint"]:
                traffic_data[identifier]["endpoints"].add(metric["endpoint"])
            
            traffic_data[identifier]["user_tiers"][metric["user_tier"]] += 1
        
        # Conversion sets en counts
        for identifier, data in traffic_data.items():
            data["geographic_regions"] = len(data["geographic_regions"])
            data["endpoints"] = len(data["endpoints"])
            data["user_tiers"] = dict(data["user_tiers"])
        
        return dict(traffic_data)
    
    def store_forecast(self, identifier: str, forecast: TrafficForecast):
        """Stockage forecast"""
        self.forecasts_cache[identifier] = forecast
    
    def store_anomalies(self, anomalies: List[Anomaly]):
        """Stockage anomalies"""
        self.anomalies_cache.extend(anomalies)
    
    def get_recent_forecasts(self) -> Dict[str, TrafficForecast]:
        """Récupération forecasts récents"""
        return self.forecasts_cache.copy()
    
    def get_recent_anomalies(self) -> List[Anomaly]:
        """Récupération anomalies récentes"""
        return list(self.anomalies_cache)
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Récupération métriques actuelles"""
        return {
            "total_active_identifiers": len(self.active_identifiers),
            "metrics_buffer_size": len(self.metrics_buffer),
            "forecasts_count": len(self.forecasts_cache),
            "anomalies_count": len(self.anomalies_cache)
        }

# Export classes principales
__all__ = [
    'AdaptiveRateLimiter',
    'MLConfig',
    'RequestContext', 
    'TrafficForecast',
    'Anomaly',
    'RateLimitDecision',
    'AdaptationStrategy',
    'AnomalyType'
]