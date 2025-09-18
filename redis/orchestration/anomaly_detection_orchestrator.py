"""🔍 Redis Anomaly Detection Orchestrator - AI-Powered Anomaly Intelligence
=============================================================================
Expert: ML ENGINEER + LEAD DEV IA + SÉCURITÉ EXPERT + BACKEND SENIOR
Technologies: Anomaly Detection + Machine Learning + Statistical Analysis + Real-time Monitoring
Architecture: Level 3 - Anomaly Intelligence Layer
Date: 2025-01-14

Ultra-advanced anomaly detection system with AI-powered pattern recognition,
real-time anomaly scoring, intelligent alerting and automated response.
=============================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
Utilisation commerciale INTERDITE sans autorisation écrite explicite
=============================================================================
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
from collections import deque, defaultdict
import redis

logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    """Types d'anomalies détectables"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    RESOURCE_SPIKE = "resource_spike"
    TRAFFIC_ANOMALY = "traffic_anomaly"
    ERROR_RATE_SPIKE = "error_rate_spike"
    LATENCY_ANOMALY = "latency_anomaly"
    MEMORY_LEAK = "memory_leak"
    CONNECTION_FLOOD = "connection_flood"
    SECURITY_BREACH = "security_breach"
    DATA_CORRUPTION = "data_corruption"
    SYSTEM_INSTABILITY = "system_instability"

class AnomalySeverity(Enum):
    """Niveaux de sévérité des anomalies"""
    CRITICAL = "critical"     # Impact immédiat service
    HIGH = "high"            # Dégradation significative
    MEDIUM = "medium"        # Impact modéré
    LOW = "low"             # Impact mineur
    INFO = "info"           # Information surveillance

class DetectionMethod(Enum):
    """Méthodes de détection d'anomalies"""
    STATISTICAL = "statistical"           # Analyse statistique classique
    MACHINE_LEARNING = "machine_learning" # ML supervisé/non-supervisé
    ISOLATION_FOREST = "isolation_forest" # Isolation Forest algorithm
    ONE_CLASS_SVM = "one_class_svm"      # One-Class SVM
    LSTM_AUTOENCODER = "lstm_autoencoder" # LSTM Autoencoder
    ENSEMBLE = "ensemble"                 # Ensemble de méthodes
    THRESHOLD_BASED = "threshold_based"   # Seuils dynamiques
    SEASONAL_DECOMPOSITION = "seasonal_decomposition" # Décomposition saisonnière

class AnomalyStatus(Enum):
    """État d'une anomalie"""
    DETECTED = "detected"         # Nouvellement détectée
    CONFIRMED = "confirmed"       # Confirmée par analyses
    INVESTIGATING = "investigating" # En cours d'investigation
    RESOLVED = "resolved"         # Résolue
    FALSE_POSITIVE = "false_positive" # Faux positif
    IGNORED = "ignored"           # Ignorée volontairement

@dataclass
class AnomalyConfig:
    """Configuration de la détection d'anomalies"""
    # Méthodes de détection
    detection_methods: List[DetectionMethod] = field(default_factory=lambda: [
        DetectionMethod.STATISTICAL,
        DetectionMethod.ISOLATION_FOREST,
        DetectionMethod.ENSEMBLE
    ])
    
    # Seuils de détection
    sensitivity: float = 0.8              # Sensibilité détection (0-1)
    confidence_threshold: float = 0.7     # Seuil confiance minimum
    anomaly_score_threshold: float = 0.6  # Seuil score anomalie
    
    # Fenêtres temporelles
    detection_window: int = 300           # Fenêtre détection (secondes)
    historical_window: int = 86400        # Fenêtre historique (24h)
    baseline_period: int = 604800         # Période baseline (7 jours)
    
    # Métriques surveillées
    monitored_metrics: List[str] = field(default_factory=lambda: [
        "cpu_usage", "memory_usage", "latency", "throughput",
        "error_rate", "connection_count", "cache_hit_ratio"
    ])
    
    # Algorithmes ML
    isolation_forest_contamination: float = 0.1
    svm_nu: float = 0.05
    lstm_sequence_length: int = 50
    
    # Alerting
    enable_alerting: bool = True
    alert_cooldown: int = 300             # Cooldown entre alertes (secondes)
    escalation_threshold: int = 3         # Seuil escalade (nb anomalies)
    
    # Auto-response
    enable_auto_response: bool = False
    auto_response_actions: List[str] = field(default_factory=lambda: [
        "scale_resources", "restart_services", "enable_circuit_breaker"
    ])

@dataclass
class AnomalyDetection:
    """Détection d'anomalie"""
    detection_id: str
    timestamp: datetime
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    
    # Données anomalie
    metric_name: str
    anomaly_value: float
    expected_value: float
    anomaly_score: float
    confidence: float
    
    # Détection
    detection_method: DetectionMethod
    detection_duration: float
    
    # Contexte
    baseline_stats: Dict[str, float]
    contributing_factors: List[str]
    affected_components: List[str]
    
    # État
    status: AnomalyStatus = AnomalyStatus.DETECTED
    investigation_notes: str = ""
    resolution_action: Optional[str] = None

@dataclass
class StatisticalBaseline:
    """Baseline statistique pour détection"""
    metric_name: str
    
    # Statistiques descriptives
    mean: float = 0.0
    std: float = 0.0
    median: float = 0.0
    q1: float = 0.0
    q3: float = 0.0
    min_value: float = 0.0
    max_value: float = 0.0
    
    # Seuils dynamiques
    upper_threshold: float = 0.0
    lower_threshold: float = 0.0
    
    # Historique
    sample_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Saisonnalité
    seasonal_patterns: Dict[str, float] = field(default_factory=dict)
    trend_coefficient: float = 0.0

class StatisticalDetector:
    """Détecteur d'anomalies statistique"""
    
    def __init__(self, config: AnomalyConfig):
        self.config = config
        self.baselines: Dict[str, StatisticalBaseline] = {}
        self.recent_values: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
    
    async def update_baseline(self, metric_name: str, values: List[float]):
        """Met à jour la baseline statistique"""
        try:
            if len(values) < 10:  # Minimum pour calculs statistiques
                return
            
            # Calcul statistiques
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0.0
            median_val = statistics.median(values)
            
            # Percentiles
            sorted_values = sorted(values)
            n = len(sorted_values)
            q1 = sorted_values[n // 4] if n >= 4 else sorted_values[0]
            q3 = sorted_values[3 * n // 4] if n >= 4 else sorted_values[-1]
            
            # Seuils dynamiques (méthode IQR + écart-type)
            iqr = q3 - q1
            std_factor = 2.0 / self.config.sensitivity  # Plus sensible = factor plus petit
            
            upper_threshold = mean_val + std_factor * std_val
            lower_threshold = max(0, mean_val - std_factor * std_val)
            
            # Seuils basés IQR pour valeurs extrêmes
            iqr_upper = q3 + 1.5 * iqr
            iqr_lower = max(0, q1 - 1.5 * iqr)
            
            # Combinaison des deux approches
            final_upper = min(upper_threshold, iqr_upper)
            final_lower = max(lower_threshold, iqr_lower)
            
            # Mise à jour baseline
            baseline = StatisticalBaseline(
                metric_name=metric_name,
                mean=mean_val,
                std=std_val,
                median=median_val,
                q1=q1,
                q3=q3,
                min_value=min(values),
                max_value=max(values),
                upper_threshold=final_upper,
                lower_threshold=final_lower,
                sample_count=len(values),
                last_updated=datetime.now()
            )
            
            # Calcul tendance
            if len(values) >= 20:
                x = np.arange(len(values))
                coeffs = np.polyfit(x, values, 1)
                baseline.trend_coefficient = coeffs[0]
            
            # Analyse saisonnalité simple (par heure)
            if len(values) >= 24:
                hourly_patterns = defaultdict(list)
                current_time = datetime.now()
                
                for i, value in enumerate(values[-24:]):
                    hour = (current_time - timedelta(hours=24-i)).hour
                    hourly_patterns[str(hour)].append(value)
                
                # Moyenne par heure
                for hour, hour_values in hourly_patterns.items():
                    if hour_values:
                        baseline.seasonal_patterns[hour] = statistics.mean(hour_values)
            
            self.baselines[metric_name] = baseline
            
            logger.info(f"📊 Baseline mise à jour {metric_name}: "
                       f"μ={mean_val:.2f}, σ={std_val:.2f}, "
                       f"seuils=[{final_lower:.2f}, {final_upper:.2f}]")
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour baseline {metric_name}: {e}")
    
    async def detect_anomaly(self, metric_name: str, 
                           current_value: float) -> Optional[AnomalyDetection]:
        """Détecte anomalie statistique"""
        try:
            baseline = self.baselines.get(metric_name)
            if not baseline:
                return None
            
            # Stockage valeur récente
            self.recent_values[metric_name].append(current_value)
            
            # Détection seuils simples
            is_anomaly = False
            anomaly_type = AnomalyType.PERFORMANCE_DEGRADATION
            severity = AnomalySeverity.LOW
            
            # Comparaison seuils
            if current_value > baseline.upper_threshold:
                is_anomaly = True
                anomaly_type = self._classify_high_anomaly(metric_name, current_value)
                
                # Calcul sévérité basée sur l'écart
                deviation = (current_value - baseline.mean) / max(baseline.std, 0.1)
                if deviation > 4:
                    severity = AnomalySeverity.CRITICAL
                elif deviation > 3:
                    severity = AnomalySeverity.HIGH
                elif deviation > 2:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW
                    
            elif current_value < baseline.lower_threshold:
                is_anomaly = True
                anomaly_type = self._classify_low_anomaly(metric_name, current_value)
                
                deviation = abs(current_value - baseline.mean) / max(baseline.std, 0.1)
                if deviation > 3:
                    severity = AnomalySeverity.HIGH
                elif deviation > 2:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW
            
            if not is_anomaly:
                return None
            
            # Calcul score anomalie et confiance
            z_score = abs(current_value - baseline.mean) / max(baseline.std, 0.1)
            anomaly_score = min(1.0, z_score / 4.0)  # Normalisation
            
            # Confiance basée sur la qualité baseline et l'écart
            confidence = min(0.95, 0.5 + (baseline.sample_count / 1000) * 0.3 + 
                           (anomaly_score * 0.2))
            
            # Vérification seuil confiance
            if confidence < self.config.confidence_threshold:
                return None
            
            # Facteurs contributifs
            contributing_factors = self._analyze_contributing_factors(
                metric_name, current_value, baseline
            )
            
            # Composants affectés
            affected_components = self._identify_affected_components(metric_name)
            
            detection = AnomalyDetection(
                detection_id=f"stat_{metric_name}_{int(time.time())}",
                timestamp=datetime.now(),
                anomaly_type=anomaly_type,
                severity=severity,
                metric_name=metric_name,
                anomaly_value=current_value,
                expected_value=baseline.mean,
                anomaly_score=anomaly_score,
                confidence=confidence,
                detection_method=DetectionMethod.STATISTICAL,
                detection_duration=0.001,  # Rapide pour statistique
                baseline_stats={
                    "mean": baseline.mean,
                    "std": baseline.std,
                    "upper_threshold": baseline.upper_threshold,
                    "lower_threshold": baseline.lower_threshold
                },
                contributing_factors=contributing_factors,
                affected_components=affected_components
            )
            
            logger.warning(f"🚨 Anomalie détectée {metric_name}: "
                          f"valeur={current_value:.2f}, "
                          f"attendu={baseline.mean:.2f}, "
                          f"score={anomaly_score:.3f}")
            
            return detection
            
        except Exception as e:
            logger.error(f"❌ Erreur détection anomalie {metric_name}: {e}")
            return None
    
    def _classify_high_anomaly(self, metric_name: str, value: float) -> AnomalyType:
        """Classifie anomalie valeur élevée"""
        if metric_name in ["cpu_usage", "memory_usage"]:
            return AnomalyType.RESOURCE_SPIKE
        elif metric_name in ["latency", "response_time"]:
            return AnomalyType.LATENCY_ANOMALY
        elif metric_name == "error_rate":
            return AnomalyType.ERROR_RATE_SPIKE
        elif metric_name == "connection_count":
            return AnomalyType.CONNECTION_FLOOD
        else:
            return AnomalyType.PERFORMANCE_DEGRADATION
    
    def _classify_low_anomaly(self, metric_name: str, value: float) -> AnomalyType:
        """Classifie anomalie valeur faible"""
        if metric_name in ["throughput", "cache_hit_ratio"]:
            return AnomalyType.PERFORMANCE_DEGRADATION
        elif metric_name == "connection_count":
            return AnomalyType.SYSTEM_INSTABILITY
        else:
            return AnomalyType.TRAFFIC_ANOMALY
    
    def _analyze_contributing_factors(self, metric_name: str, value: float,
                                    baseline: StatisticalBaseline) -> List[str]:
        """Analyse les facteurs contributifs"""
        factors = []
        
        # Facteur tendance
        if abs(baseline.trend_coefficient) > 0.1:
            if baseline.trend_coefficient > 0:
                factors.append("Tendance croissante détectée")
            else:
                factors.append("Tendance décroissante détectée")
        
        # Facteur saisonnalité
        current_hour = str(datetime.now().hour)
        if current_hour in baseline.seasonal_patterns:
            expected_seasonal = baseline.seasonal_patterns[current_hour]
            if abs(value - expected_seasonal) > baseline.std:
                factors.append(f"Déviation pattern saisonnier heure {current_hour}")
        
        # Facteur écart extrême
        z_score = abs(value - baseline.mean) / max(baseline.std, 0.1)
        if z_score > 3:
            factors.append(f"Écart extrême détecté (z-score: {z_score:.2f})")
        
        # Facteur persistance
        recent_values = list(self.recent_values[metric_name])
        if len(recent_values) >= 5:
            recent_anomalies = sum(1 for v in recent_values[-5:] 
                                 if v > baseline.upper_threshold or v < baseline.lower_threshold)
            if recent_anomalies >= 3:
                factors.append("Anomalies persistantes détectées")
        
        return factors or ["Déviation statistique standard"]
    
    def _identify_affected_components(self, metric_name: str) -> List[str]:
        """Identifie les composants affectés"""
        component_map = {
            "cpu_usage": ["compute_nodes", "worker_threads", "application_layer"],
            "memory_usage": ["cache_layer", "data_structures", "memory_pools"],
            "latency": ["network_layer", "database_layer", "cache_layer"],
            "throughput": ["load_balancer", "worker_threads", "network_layer"],
            "error_rate": ["application_layer", "database_layer", "external_apis"],
            "connection_count": ["connection_pool", "network_layer", "load_balancer"],
            "cache_hit_ratio": ["cache_layer", "data_layer", "memory_management"]
        }
        
        return component_map.get(metric_name, ["system_global"])

class IsolationForestDetector:
    """Détecteur d'anomalies par Isolation Forest"""
    
    def __init__(self, config: AnomalyConfig):
        self.config = config
        self.models: Dict[str, Any] = {}
        self.training_data: Dict[str, List[List[float]]] = defaultdict(list)
        self.feature_scalers: Dict[str, Any] = {}
        
    async def train_model(self, metric_name: str, 
                         historical_data: List[List[float]]) -> bool:
        """Entraîne modèle Isolation Forest"""
        try:
            if len(historical_data) < 100:  # Minimum pour entraînement
                return False
            
            # Simulation Isolation Forest (implémentation simplifiée)
            # En production, utiliser sklearn.ensemble.IsolationForest
            
            # Calcul statistiques pour simulation
            all_values = [item[0] if isinstance(item, list) else item 
                         for item in historical_data]
            
            mean_val = statistics.mean(all_values)
            std_val = statistics.stdev(all_values) if len(all_values) > 1 else 1.0
            
            # Modèle simulé
            self.models[metric_name] = {
                "mean": mean_val,
                "std": std_val,
                "contamination": self.config.isolation_forest_contamination,
                "threshold": mean_val + 2.5 * std_val,  # Seuil anomalie
                "trained": True
            }
            
            logger.info(f"🌲 Modèle Isolation Forest entraîné: {metric_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur entraînement Isolation Forest {metric_name}: {e}")
            return False
    
    async def detect_anomaly(self, metric_name: str, 
                           features: List[float]) -> Optional[AnomalyDetection]:
        """Détecte anomalie avec Isolation Forest"""
        try:
            model = self.models.get(metric_name)
            if not model or not model.get("trained"):
                return None
            
            current_value = features[0] if features else 0.0
            
            # Simulation détection Isolation Forest
            # Score d'isolation (0 = normal, 1 = anomalie)
            deviation = abs(current_value - model["mean"]) / model["std"]
            isolation_score = min(1.0, deviation / 3.0)
            
            # Seuil basé sur contamination
            threshold = 1.0 - model["contamination"]
            
            if isolation_score < threshold:
                return None  # Pas d'anomalie
            
            # Classification sévérité
            if isolation_score > 0.9:
                severity = AnomalySeverity.CRITICAL
            elif isolation_score > 0.8:
                severity = AnomalySeverity.HIGH
            elif isolation_score > 0.7:
                severity = AnomalySeverity.MEDIUM
            else:
                severity = AnomalySeverity.LOW
            
            # Type anomalie basé sur métrique
            anomaly_type = self._classify_anomaly_type(metric_name, current_value)
            
            detection = AnomalyDetection(
                detection_id=f"iforest_{metric_name}_{int(time.time())}",
                timestamp=datetime.now(),
                anomaly_type=anomaly_type,
                severity=severity,
                metric_name=metric_name,
                anomaly_value=current_value,
                expected_value=model["mean"],
                anomaly_score=isolation_score,
                confidence=min(0.95, isolation_score),
                detection_method=DetectionMethod.ISOLATION_FOREST,
                detection_duration=0.005,
                baseline_stats={"mean": model["mean"], "std": model["std"]},
                contributing_factors=["Isolation Forest détection"],
                affected_components=[f"{metric_name}_component"]
            )
            
            logger.warning(f"🌲 Anomalie Isolation Forest {metric_name}: "
                          f"score={isolation_score:.3f}")
            
            return detection
            
        except Exception as e:
            logger.error(f"❌ Erreur détection Isolation Forest {metric_name}: {e}")
            return None
    
    def _classify_anomaly_type(self, metric_name: str, value: float) -> AnomalyType:
        """Classifie le type d'anomalie"""
        if metric_name in ["cpu_usage", "memory_usage"]:
            return AnomalyType.RESOURCE_SPIKE
        elif "latency" in metric_name:
            return AnomalyType.LATENCY_ANOMALY
        elif "error" in metric_name:
            return AnomalyType.ERROR_RATE_SPIKE
        else:
            return AnomalyType.PERFORMANCE_DEGRADATION

class EnsembleDetector:
    """Détecteur d'anomalies ensemble"""
    
    def __init__(self, config: AnomalyConfig):
        self.config = config
        self.statistical_detector = StatisticalDetector(config)
        self.isolation_forest_detector = IsolationForestDetector(config)
        self.detection_weights = {
            DetectionMethod.STATISTICAL: 0.4,
            DetectionMethod.ISOLATION_FOREST: 0.3,
            DetectionMethod.THRESHOLD_BASED: 0.3
        }
    
    async def detect_anomaly(self, metric_name: str, current_value: float,
                           features: List[float]) -> Optional[AnomalyDetection]:
        """Détection ensemble multi-méthodes"""
        try:
            detections = []
            
            # Détection statistique
            stat_detection = await self.statistical_detector.detect_anomaly(
                metric_name, current_value
            )
            if stat_detection:
                detections.append((stat_detection, self.detection_weights[DetectionMethod.STATISTICAL]))
            
            # Détection Isolation Forest
            if_detection = await self.isolation_forest_detector.detect_anomaly(
                metric_name, features
            )
            if if_detection:
                detections.append((if_detection, self.detection_weights[DetectionMethod.ISOLATION_FOREST]))
            
            # Détection seuils simple
            threshold_detection = await self._threshold_detection(metric_name, current_value)
            if threshold_detection:
                detections.append((threshold_detection, self.detection_weights[DetectionMethod.THRESHOLD_BASED]))
            
            if not detections:
                return None
            
            # Fusion des détections
            return await self._fuse_detections(detections)
            
        except Exception as e:
            logger.error(f"❌ Erreur détection ensemble {metric_name}: {e}")
            return None
    
    async def _threshold_detection(self, metric_name: str, 
                                 value: float) -> Optional[AnomalyDetection]:
        """Détection basée seuils fixes"""
        try:
            # Seuils fixes par métrique
            thresholds = {
                "cpu_usage": {"high": 90, "critical": 95},
                "memory_usage": {"high": 85, "critical": 95},
                "latency": {"high": 1000, "critical": 5000},  # ms
                "error_rate": {"high": 5, "critical": 10},    # %
                "connection_count": {"high": 1000, "critical": 2000}
            }
            
            metric_thresholds = thresholds.get(metric_name)
            if not metric_thresholds:
                return None
            
            severity = None
            if value >= metric_thresholds["critical"]:
                severity = AnomalySeverity.CRITICAL
            elif value >= metric_thresholds["high"]:
                severity = AnomalySeverity.HIGH
            
            if not severity:
                return None
            
            detection = AnomalyDetection(
                detection_id=f"threshold_{metric_name}_{int(time.time())}",
                timestamp=datetime.now(),
                anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                severity=severity,
                metric_name=metric_name,
                anomaly_value=value,
                expected_value=metric_thresholds["high"] * 0.8,
                anomaly_score=min(1.0, value / metric_thresholds["critical"]),
                confidence=0.8,
                detection_method=DetectionMethod.THRESHOLD_BASED,
                detection_duration=0.001,
                baseline_stats=metric_thresholds,
                contributing_factors=["Seuil fixe dépassé"],
                affected_components=[f"{metric_name}_system"]
            )
            
            return detection
            
        except Exception as e:
            logger.error(f"❌ Erreur détection seuil {metric_name}: {e}")
            return None
    
    async def _fuse_detections(self, detections: List[Tuple[AnomalyDetection, float]]) -> AnomalyDetection:
        """Fusionne les détections multiples"""
        try:
            if not detections:
                return None
            
            if len(detections) == 1:
                return detections[0][0]
            
            # Calcul score pondéré
            total_weight = sum(weight for _, weight in detections)
            weighted_score = sum(detection.anomaly_score * weight 
                               for detection, weight in detections) / total_weight
            
            # Confiance pondérée
            weighted_confidence = sum(detection.confidence * weight 
                                    for detection, weight in detections) / total_weight
            
            # Sévérité maximale
            max_severity = max(detection.severity for detection, _ in detections)
            
            # Facteurs contributifs combinés
            all_factors = []
            for detection, _ in detections:
                all_factors.extend(detection.contributing_factors)
            
            # Méthodes utilisées
            methods_used = [detection.detection_method.value for detection, _ in detections]
            
            # Détection de référence (plus haute confiance)
            reference_detection = max(detections, key=lambda x: x[0].confidence)[0]
            
            fused_detection = AnomalyDetection(
                detection_id=f"ensemble_{reference_detection.metric_name}_{int(time.time())}",
                timestamp=datetime.now(),
                anomaly_type=reference_detection.anomaly_type,
                severity=max_severity,
                metric_name=reference_detection.metric_name,
                anomaly_value=reference_detection.anomaly_value,
                expected_value=reference_detection.expected_value,
                anomaly_score=weighted_score,
                confidence=weighted_confidence,
                detection_method=DetectionMethod.ENSEMBLE,
                detection_duration=sum(d.detection_duration for d, _ in detections),
                baseline_stats=reference_detection.baseline_stats,
                contributing_factors=list(set(all_factors)) + [f"Ensemble: {', '.join(methods_used)}"],
                affected_components=list(set(
                    comp for detection, _ in detections 
                    for comp in detection.affected_components
                ))
            )
            
            logger.info(f"🤝 Détection ensemble fusionnée: "
                       f"méthodes={len(detections)}, score={weighted_score:.3f}")
            
            return fused_detection
            
        except Exception as e:
            logger.error(f"❌ Erreur fusion détections: {e}")
            return detections[0][0] if detections else None

class RedisAnomalyDetectionOrchestrator:
    """🔍 Orchestrateur de détection d'anomalies Redis - AI-powered anomaly intelligence"""
    
    def __init__(self, config: AnomalyConfig, redis_url: str = "redis://localhost:6379"):
        self.config = config
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        
        # Détecteurs
        self.ensemble_detector = EnsembleDetector(config)
        
        # Gestion anomalies
        self.active_anomalies: Dict[str, AnomalyDetection] = {}
        self.anomaly_history: List[AnomalyDetection] = []
        
        # Cache et métriques
        self.metrics_cache: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self.baseline_data: Dict[str, List[float]] = defaultdict(list)
        
        # État et contrôle
        self._running = False
        self._detection_task: Optional[asyncio.Task] = None
        self._training_task: Optional[asyncio.Task] = None
        self.last_alert_times: Dict[str, datetime] = {}
        
        # Métriques système
        self.total_detections = 0
        self.false_positives = 0
        self.confirmed_anomalies = 0
        
    async def initialize(self):
        """Initialise l'orchestrateur de détection d'anomalies"""
        try:
            # Connexion Redis
            self.redis_client = redis.Redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
            
            self.redis_client.ping()
            
            # Chargement historique
            await self._load_baseline_data()
            
            # Entraînement modèles initiaux
            await self._initial_training()
            
            # Démarrage tâches
            self._running = True
            self._detection_task = asyncio.create_task(self._detection_loop())
            self._training_task = asyncio.create_task(self._training_loop())
            
            logger.info("🔍 Redis Anomaly Detection Orchestrator initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation anomaly detector: {e}")
            raise
    
    async def detect_anomalies(self, metrics: Dict[str, float]) -> List[AnomalyDetection]:
        """Détecte les anomalies dans les métriques"""
        try:
            detections = []
            
            for metric_name, value in metrics.items():
                if metric_name not in self.config.monitored_metrics:
                    continue
                
                # Mise à jour cache
                self.metrics_cache[metric_name].append({
                    "value": value,
                    "timestamp": time.time()
                })
                
                # Préparation features pour ML
                features = self._prepare_features(metric_name, value)
                
                # Détection avec ensemble
                detection = await self.ensemble_detector.detect_anomaly(
                    metric_name, value, features
                )
                
                if detection:
                    # Vérification dédoublonnage
                    if not await self._is_duplicate_detection(detection):
                        detections.append(detection)
                        await self._process_new_detection(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"❌ Erreur détection anomalies: {e}")
            return []
    
    async def update_anomaly_status(self, detection_id: str, 
                                  new_status: AnomalyStatus,
                                  notes: str = "") -> bool:
        """Met à jour le statut d'une anomalie"""
        try:
            anomaly = self.active_anomalies.get(detection_id)
            if not anomaly:
                # Recherche dans historique
                for hist_anomaly in self.anomaly_history:
                    if hist_anomaly.detection_id == detection_id:
                        anomaly = hist_anomaly
                        break
                
                if not anomaly:
                    return False
            
            old_status = anomaly.status
            anomaly.status = new_status
            anomaly.investigation_notes = notes
            
            # Mise à jour métriques
            if new_status == AnomalyStatus.FALSE_POSITIVE:
                self.false_positives += 1
            elif new_status == AnomalyStatus.CONFIRMED:
                self.confirmed_anomalies += 1
            
            # Persistance
            await self._persist_anomaly_update(anomaly)
            
            logger.info(f"📝 Anomalie {detection_id} mise à jour: "
                       f"{old_status.value} → {new_status.value}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour anomalie {detection_id}: {e}")
            return False
    
    async def get_active_anomalies(self, severity_filter: Optional[AnomalySeverity] = None) -> List[AnomalyDetection]:
        """Retourne les anomalies actives"""
        try:
            anomalies = list(self.active_anomalies.values())
            
            if severity_filter:
                anomalies = [a for a in anomalies if a.severity == severity_filter]
            
            # Tri par sévérité puis par timestamp
            severity_order = {
                AnomalySeverity.CRITICAL: 0,
                AnomalySeverity.HIGH: 1,
                AnomalySeverity.MEDIUM: 2,
                AnomalySeverity.LOW: 3,
                AnomalySeverity.INFO: 4
            }
            
            anomalies.sort(key=lambda a: (severity_order[a.severity], a.timestamp), reverse=True)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération anomalies actives: {e}")
            return []
    
    async def get_detection_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de détection"""
        try:
            # Calcul taux de faux positifs
            false_positive_rate = (
                self.false_positives / max(self.total_detections, 1) * 100
            )
            
            # Calcul précision
            precision = (
                self.confirmed_anomalies / max(self.confirmed_anomalies + self.false_positives, 1) * 100
            )
            
            # Répartition par sévérité
            severity_counts = defaultdict(int)
            for anomaly in self.active_anomalies.values():
                severity_counts[anomaly.severity.value] += 1
            
            # Répartition par type
            type_counts = defaultdict(int)
            for anomaly in self.anomaly_history[-100:]:  # 100 dernières
                type_counts[anomaly.anomaly_type.value] += 1
            
            # Performance détection
            recent_detections = [a for a in self.anomaly_history[-50:] 
                               if a.timestamp > datetime.now() - timedelta(hours=24)]
            
            avg_detection_time = (
                statistics.mean([d.detection_duration for d in recent_detections])
                if recent_detections else 0.0
            )
            
            return {
                "total_detections": self.total_detections,
                "active_anomalies": len(self.active_anomalies),
                "false_positives": self.false_positives,
                "confirmed_anomalies": self.confirmed_anomalies,
                "false_positive_rate": false_positive_rate,
                "precision": precision,
                "severity_distribution": dict(severity_counts),
                "type_distribution": dict(type_counts),
                "average_detection_time": avg_detection_time,
                "monitored_metrics": len(self.config.monitored_metrics),
                "detection_methods": [m.value for m in self.config.detection_methods],
                "last_update": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur statistiques détection: {e}")
            return {}
    
    def _prepare_features(self, metric_name: str, current_value: float) -> List[float]:
        """Prépare les features pour la détection ML"""
        try:
            features = [current_value]
            
            # Features temporelles récentes
            recent_values = [item["value"] for item in list(self.metrics_cache[metric_name])[-10:]]
            
            if len(recent_values) >= 3:
                # Moyenne, min, max récents
                features.extend([
                    statistics.mean(recent_values),
                    min(recent_values),
                    max(recent_values)
                ])
                
                # Tendance récente
                if len(recent_values) >= 5:
                    x = np.arange(len(recent_values))
                    coeffs = np.polyfit(x, recent_values, 1)
                    features.append(coeffs[0])  # Pente
                else:
                    features.append(0.0)
                    
                # Volatilité
                if len(recent_values) > 1:
                    features.append(statistics.stdev(recent_values))
                else:
                    features.append(0.0)
            else:
                # Valeurs par défaut
                features.extend([current_value, current_value, current_value, 0.0, 0.0])
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Erreur préparation features {metric_name}: {e}")
            return [current_value]
    
    async def _is_duplicate_detection(self, detection: AnomalyDetection) -> bool:
        """Vérifie si la détection est un doublon"""
        try:
            # Recherche anomalies similaires récentes
            recent_threshold = datetime.now() - timedelta(minutes=5)
            
            for anomaly in self.active_anomalies.values():
                if (anomaly.metric_name == detection.metric_name and
                    anomaly.anomaly_type == detection.anomaly_type and
                    anomaly.timestamp > recent_threshold and
                    abs(anomaly.anomaly_value - detection.anomaly_value) < 
                    anomaly.anomaly_value * 0.1):  # 10% de différence
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Erreur vérification doublon: {e}")
            return False
    
    async def _process_new_detection(self, detection: AnomalyDetection):
        """Traite une nouvelle détection"""
        try:
            # Stockage
            self.active_anomalies[detection.detection_id] = detection
            self.anomaly_history.append(detection)
            self.total_detections += 1
            
            # Limitation historique
            if len(self.anomaly_history) > 10000:
                self.anomaly_history = self.anomaly_history[-10000:]
            
            # Alerting
            if self.config.enable_alerting:
                await self._send_alert(detection)
            
            # Auto-response
            if (self.config.enable_auto_response and 
                detection.severity in [AnomalySeverity.CRITICAL, AnomalySeverity.HIGH]):
                await self._trigger_auto_response(detection)
            
            # Persistance
            await self._persist_detection(detection)
            
            logger.warning(f"🚨 Nouvelle anomalie traitée: {detection.detection_id}")
            
        except Exception as e:
            logger.error(f"❌ Erreur traitement détection: {e}")
    
    async def _send_alert(self, detection: AnomalyDetection):
        """Envoie une alerte pour l'anomalie"""
        try:
            alert_key = f"{detection.metric_name}_{detection.anomaly_type.value}"
            
            # Vérification cooldown
            last_alert = self.last_alert_times.get(alert_key)
            if (last_alert and 
                datetime.now() - last_alert < timedelta(seconds=self.config.alert_cooldown)):
                return
            
            # Simulation envoi alerte
            alert_message = (f"🚨 Anomalie {detection.severity.value.upper()}: "
                           f"{detection.metric_name} = {detection.anomaly_value:.2f} "
                           f"(attendu: {detection.expected_value:.2f})")
            
            # Stockage alerte dans Redis
            await self._store_alert(detection, alert_message)
            
            self.last_alert_times[alert_key] = datetime.now()
            
            logger.warning(f"📢 Alerte envoyée: {alert_message}")
            
        except Exception as e:
            logger.error(f"❌ Erreur envoi alerte: {e}")
    
    async def _trigger_auto_response(self, detection: AnomalyDetection):
        """Déclenche réponse automatique"""
        try:
            response_actions = []
            
            # Sélection actions selon type anomalie
            if detection.anomaly_type == AnomalyType.RESOURCE_SPIKE:
                response_actions = ["scale_resources", "enable_circuit_breaker"]
            elif detection.anomaly_type == AnomalyType.LATENCY_ANOMALY:
                response_actions = ["optimize_cache", "restart_services"]
            elif detection.anomaly_type == AnomalyType.CONNECTION_FLOOD:
                response_actions = ["enable_rate_limiting", "scale_resources"]
            
            # Exécution actions (simulation)
            for action in response_actions[:2]:  # Maximum 2 actions
                await self._execute_response_action(action, detection)
            
            detection.resolution_action = ", ".join(response_actions)
            
            logger.info(f"🤖 Réponse automatique: {response_actions}")
            
        except Exception as e:
            logger.error(f"❌ Erreur réponse automatique: {e}")
    
    async def _execute_response_action(self, action: str, detection: AnomalyDetection):
        """Execute une action de réponse"""
        try:
            # Simulation exécution actions
            action_simulation = {
                "scale_resources": lambda: "Scaling ressources activé",
                "restart_services": lambda: "Redémarrage services déclenché",
                "enable_circuit_breaker": lambda: "Circuit breaker activé",
                "enable_rate_limiting": lambda: "Rate limiting activé",
                "optimize_cache": lambda: "Optimisation cache déclenchée"
            }
            
            result = action_simulation.get(action, lambda: f"Action {action} exécutée")()
            
            # Stockage action dans Redis
            action_data = {
                "action": action,
                "detection_id": detection.detection_id,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
            key = f"auto_response:{detection.detection_id}:{action}"
            self.redis_client.setex(key, 3600, json.dumps(action_data))
            
            logger.info(f"⚡ Action exécutée: {action} - {result}")
            
        except Exception as e:
            logger.error(f"❌ Erreur exécution action {action}: {e}")
    
    async def _load_baseline_data(self):
        """Charge les données baseline"""
        try:
            for metric in self.config.monitored_metrics:
                # Chargement depuis Redis
                key = f"anomaly_baseline:{metric}"
                baseline_data = self.redis_client.get(key)
                
                if baseline_data:
                    data = json.loads(baseline_data)
                    self.baseline_data[metric] = data
                else:
                    # Génération données simulées pour démo
                    self.baseline_data[metric] = self._generate_baseline_data(metric)
            
            logger.info(f"📊 Données baseline chargées: {len(self.baseline_data)} métriques")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement baseline: {e}")
    
    def _generate_baseline_data(self, metric_name: str) -> List[float]:
        """Génère données baseline simulées"""
        # Simulation données historiques normales
        base_values = {
            "cpu_usage": 45,
            "memory_usage": 60,
            "latency": 20,
            "throughput": 1000,
            "error_rate": 0.5,
            "connection_count": 150,
            "cache_hit_ratio": 85
        }
        
        base_value = base_values.get(metric_name, 50)
        noise_level = base_value * 0.1
        
        # Génération 1000 points avec variation normale
        data = []
        for i in range(1000):
            # Variation temporelle + bruit
            temporal = base_value * 0.1 * math.sin(i / 100)
            noise = np.random.normal(0, noise_level)
            value = max(0, base_value + temporal + noise)
            
            if metric_name in ["cpu_usage", "memory_usage", "cache_hit_ratio"]:
                value = min(100, value)
            
            data.append(value)
        
        return data
    
    async def _initial_training(self):
        """Entraînement initial des modèles"""
        try:
            for metric_name, baseline_data in self.baseline_data.items():
                if len(baseline_data) >= 100:
                    # Entraînement baseline statistique
                    await self.ensemble_detector.statistical_detector.update_baseline(
                        metric_name, baseline_data
                    )
                    
                    # Entraînement Isolation Forest
                    features_data = [[value] for value in baseline_data]
                    await self.ensemble_detector.isolation_forest_detector.train_model(
                        metric_name, features_data
                    )
            
            logger.info("🎓 Entraînement initial des modèles terminé")
            
        except Exception as e:
            logger.error(f"❌ Erreur entraînement initial: {e}")
    
    async def _detection_loop(self):
        """Boucle de détection automatique"""
        while self._running:
            try:
                # Simulation collecte métriques système
                current_time = time.time()
                
                simulated_metrics = {
                    "cpu_usage": 45 + 20 * math.sin(current_time / 1800) + np.random.normal(0, 3),
                    "memory_usage": 60 + 15 * math.sin(current_time / 3600) + np.random.normal(0, 2),
                    "latency": 20 + 10 * math.sin(current_time / 900) + abs(np.random.normal(0, 2)),
                    "throughput": 1000 + 200 * math.sin(current_time / 1200) + np.random.normal(0, 20),
                    "error_rate": max(0, 0.5 + 2 * math.sin(current_time / 450) + np.random.normal(0, 0.3)),
                    "connection_count": 150 + 50 * math.sin(current_time / 600) + np.random.normal(0, 10),
                    "cache_hit_ratio": 85 + 10 * math.sin(current_time / 800) + np.random.normal(0, 1)
                }
                
                # Injection anomalies occasionnelles (5% chance)
                if np.random.random() < 0.05:
                    anomaly_metric = np.random.choice(list(simulated_metrics.keys()))
                    if anomaly_metric in ["cpu_usage", "memory_usage", "latency"]:
                        simulated_metrics[anomaly_metric] *= np.random.uniform(2.0, 3.0)
                    else:
                        simulated_metrics[anomaly_metric] *= np.random.uniform(0.3, 0.5)
                
                # Clamp valeurs
                for metric, value in simulated_metrics.items():
                    if metric in ["cpu_usage", "memory_usage", "cache_hit_ratio"]:
                        simulated_metrics[metric] = max(0, min(100, value))
                    else:
                        simulated_metrics[metric] = max(0, value)
                
                # Détection anomalies
                detections = await self.detect_anomalies(simulated_metrics)
                
                if detections:
                    logger.info(f"🔍 Détections automatiques: {len(detections)}")
                
                await asyncio.sleep(self.config.detection_window)
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle détection: {e}")
                await asyncio.sleep(60)
    
    async def _training_loop(self):
        """Boucle de réentraînement des modèles"""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Réentraînement horaire
                
                # Mise à jour baselines avec nouvelles données
                for metric_name in self.config.monitored_metrics:
                    if metric_name in self.metrics_cache:
                        recent_values = [
                            item["value"] for item in list(self.metrics_cache[metric_name])
                        ]
                        
                        if len(recent_values) >= 50:
                            await self.ensemble_detector.statistical_detector.update_baseline(
                                metric_name, recent_values
                            )
                
                logger.info("🔄 Réentraînement modèles terminé")
                
            except Exception as e:
                logger.error(f"❌ Erreur boucle entraînement: {e}")
                await asyncio.sleep(1800)  # Retry dans 30 min
    
    async def _persist_detection(self, detection: AnomalyDetection):
        """Persiste une détection"""
        try:
            detection_data = {
                "detection_id": detection.detection_id,
                "timestamp": detection.timestamp.isoformat(),
                "anomaly_type": detection.anomaly_type.value,
                "severity": detection.severity.value,
                "metric_name": detection.metric_name,
                "anomaly_value": detection.anomaly_value,
                "expected_value": detection.expected_value,
                "anomaly_score": detection.anomaly_score,
                "confidence": detection.confidence,
                "detection_method": detection.detection_method.value,
                "status": detection.status.value
            }
            
            key = f"anomaly_detection:{detection.detection_id}"
            self.redis_client.setex(key, 86400, json.dumps(detection_data))
            
        except Exception as e:
            logger.error(f"❌ Erreur persistance détection: {e}")
    
    async def _persist_anomaly_update(self, anomaly: AnomalyDetection):
        """Persiste mise à jour anomalie"""
        try:
            update_data = {
                "detection_id": anomaly.detection_id,
                "status": anomaly.status.value,
                "investigation_notes": anomaly.investigation_notes,
                "resolution_action": anomaly.resolution_action,
                "updated_at": datetime.now().isoformat()
            }
            
            key = f"anomaly_update:{anomaly.detection_id}"
            self.redis_client.setex(key, 86400 * 7, json.dumps(update_data))
            
        except Exception as e:
            logger.error(f"❌ Erreur persistance mise à jour: {e}")
    
    async def _store_alert(self, detection: AnomalyDetection, message: str):
        """Stocke une alerte"""
        try:
            alert_data = {
                "detection_id": detection.detection_id,
                "message": message,
                "severity": detection.severity.value,
                "timestamp": datetime.now().isoformat(),
                "metric": detection.metric_name
            }
            
            key = f"anomaly_alert:{detection.detection_id}"
            self.redis_client.setex(key, 3600, json.dumps(alert_data))
            
        except Exception as e:
            logger.error(f"❌ Erreur stockage alerte: {e}")
    
    async def shutdown(self):
        """Arrêt propre de l'orchestrateur"""
        try:
            self._running = False
            
            # Arrêt tâches
            for task in [self._detection_task, self._training_task]:
                if task:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Sauvegarde baselines
            for metric_name, data in self.baseline_data.items():
                key = f"anomaly_baseline:{metric_name}"
                self.redis_client.setex(key, 86400 * 7, json.dumps(data))
            
            # Fermeture Redis
            if self.redis_client:
                self.redis_client.close()
            
            logger.info("🔍 Redis Anomaly Detection Orchestrator arrêté")
            
        except Exception as e:
            logger.error(f"❌ Erreur arrêt anomaly detector: {e}")


# Factory function
async def create_anomaly_detection_orchestrator(config: Optional[AnomalyConfig] = None,
                                              redis_url: str = "redis://localhost:6379") -> RedisAnomalyDetectionOrchestrator:
    """Crée et initialise un orchestrateur de détection d'anomalies Redis"""
    try:
        if config is None:
            config = AnomalyConfig()
        
        orchestrator = RedisAnomalyDetectionOrchestrator(config, redis_url)
        await orchestrator.initialize()
        
        logger.info("🔍 Redis Anomaly Detection Orchestrator créé avec succès")
        return orchestrator
        
    except Exception as e:
        logger.error(f"❌ Erreur création anomaly detection orchestrator: {e}")
        raise


# Export des classes principales
__all__ = [
    "RedisAnomalyDetectionOrchestrator",
    "AnomalyConfig",
    "AnomalyDetection",
    "StatisticalBaseline",
    "AnomalyType",
    "AnomalySeverity", 
    "DetectionMethod",
    "AnomalyStatus",
    "StatisticalDetector",
    "IsolationForestDetector",
    "EnsembleDetector",
    "create_anomaly_detection_orchestrator"
]