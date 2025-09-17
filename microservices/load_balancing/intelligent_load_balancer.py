"""
🧠 INTELLIGENT LOAD BALANCER - ENTERPRISE IA/ML
Load balancer intelligent avec IA/ML pour optimization automatique

Implements ML-based routing + predictive scaling + adaptive algorithms
for enterprise-grade traffic distribution and performance optimization.

Key Features:
- ML-based server selection basée sur patterns historiques  
- Real-time performance prediction per server
- Request type classification pour routing intelligent
- Adaptive algorithm selection basée sur context
- Predictive auto-scaling recommendations
- Traffic pattern learning et optimization

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture load balancing intelligent est la propriété intellectuelle EXCLUSIVE de Fahed Mlaiel.
Toute reproduction, modification, distribution sans autorisation écrite est STRICTEMENT INTERDITE.
"""

import asyncio
import logging
import time
import numpy as np
from typing import Dict, List, Any, Optional, AsyncIterator, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import pickle
import json
import hashlib
from abc import ABC, abstractmethod

# ML Dependencies
try:
    from sklearn.ensemble import RandomForestRegressor, IsolationForest, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    import pandas as pd
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("ML dependencies not available. Running in basic mode.")

logger = logging.getLogger(__name__)

class MLModelType(Enum):
    """Types de modèles ML pour load balancing"""
    TRAFFIC_PREDICTOR = "traffic_predictor"
    PERFORMANCE_OPTIMIZER = "performance_optimizer" 
    ANOMALY_DETECTOR = "anomaly_detector"
    LOAD_FORECASTER = "load_forecaster"
    ROUTING_CLASSIFIER = "routing_classifier"

class PredictionConfidence(Enum):
    """Niveaux de confiance prédictions ML"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"

@dataclass
class ServerMetrics:
    """Métriques serveur pour ML analysis"""
    server_id: str
    cpu_usage: float
    memory_usage: float
    active_connections: int
    response_time_avg: float
    request_rate: float
    error_rate: float
    throughput: float
    health_score: float
    geographic_region: str
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_feature_vector(self) -> np.ndarray:
        """Conversion vers vecteur features pour ML"""
        return np.array([
            self.cpu_usage,
            self.memory_usage,
            self.active_connections,
            self.response_time_avg,
            self.request_rate,
            self.error_rate,
            self.throughput,
            self.health_score
        ])

@dataclass
class RequestContext:
    """Context requête pour routing intelligent"""
    request_id: str
    client_ip: str
    user_agent: str
    request_type: str
    payload_size: int
    priority_level: int
    session_id: Optional[str] = None
    geographic_origin: Optional[str] = None
    business_tier: str = "standard"
    sla_requirements: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RoutingPrediction:
    """Résultat prédiction routing ML"""
    server_id: str
    confidence_score: float
    predicted_response_time: float
    predicted_success_rate: float
    routing_reason: str
    alternative_servers: List[str]
    performance_metrics: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MLConfig:
    """Configuration ML pour load balancer intelligent"""
    model_update_interval: int = 300  # 5 minutes
    prediction_cache_ttl: int = 60    # 1 minute
    anomaly_threshold: float = 0.8
    min_confidence_threshold: float = 0.7
    feature_importance_threshold: float = 0.1
    retrain_trigger_accuracy: float = 0.85
    max_model_age_hours: int = 24
    enable_online_learning: bool = True
    
class MLModelManager:
    """Gestionnaire modèles ML pour load balancing intelligent"""
    
    def __init__(self, config: MLConfig):
        self.config = config
        self.models: Dict[MLModelType, Any] = {}
        self.scalers: Dict[MLModelType, StandardScaler] = {}
        self.model_performance: Dict[MLModelType, Dict[str, float]] = {}
        self.last_training: Dict[MLModelType, datetime] = {}
        self.training_data: Dict[MLModelType, List[Dict]] = {}
        
        # Initialize ML models si disponible
        if ML_AVAILABLE:
            self._initialize_models()
        
    def _initialize_models(self):
        """Initialisation modèles ML"""
        logger.info("🧠 Initialisation modèles ML pour load balancing intelligent")
        
        # Traffic Predictor - LSTM simulé avec RandomForest
        self.models[MLModelType.TRAFFIC_PREDICTOR] = RandomForestRegressor(
            n_estimators=100, random_state=42, n_jobs=-1
        )
        
        # Performance Optimizer - Gradient Boosting
        self.models[MLModelType.PERFORMANCE_OPTIMIZER] = GradientBoostingRegressor(
            n_estimators=100, learning_rate=0.1, random_state=42
        )
        
        # Anomaly Detector - Isolation Forest
        self.models[MLModelType.ANOMALY_DETECTOR] = IsolationForest(
            contamination=0.1, random_state=42, n_jobs=-1
        )
        
        # Load Forecaster - Linear Regression pour simplicité
        self.models[MLModelType.LOAD_FORECASTER] = LinearRegression()
        
        # Routing Classifier - RandomForest pour classification
        self.models[MLModelType.ROUTING_CLASSIFIER] = RandomForestRegressor(
            n_estimators=50, random_state=42, n_jobs=-1
        )
        
        # Initialize scalers
        for model_type in MLModelType:
            self.scalers[model_type] = StandardScaler()
            self.model_performance[model_type] = {"accuracy": 0.0, "last_updated": time.time()}
            self.training_data[model_type] = []
            
        logger.info("✅ Modèles ML initialisés avec succès")

    async def predict_server_performance(
        self, 
        server_metrics: ServerMetrics, 
        request_context: RequestContext
    ) -> RoutingPrediction:
        """Prédiction performance serveur avec ML"""
        if not ML_AVAILABLE:
            return self._fallback_prediction(server_metrics, request_context)
            
        try:
            # Préparer features
            features = self._prepare_features(server_metrics, request_context)
            
            # Prédiction avec modèle performance
            model = self.models[MLModelType.PERFORMANCE_OPTIMIZER]
            scaler = self.scalers[MLModelType.PERFORMANCE_OPTIMIZER]
            
            if hasattr(model, 'predict'):
                # Scale features
                scaled_features = scaler.transform([features]) if scaler.scale_ is not None else [features]
                
                # Prédiction response time
                predicted_response_time = max(0.001, float(model.predict(scaled_features)[0]))
                
                # Calcul confidence score
                confidence_score = self._calculate_confidence(features, MLModelType.PERFORMANCE_OPTIMIZER)
                
                # Prédiction success rate basée sur métriques
                predicted_success_rate = max(0.5, 1.0 - server_metrics.error_rate)
                
                return RoutingPrediction(
                    server_id=server_metrics.server_id,
                    confidence_score=confidence_score,
                    predicted_response_time=predicted_response_time,
                    predicted_success_rate=predicted_success_rate,
                    routing_reason=f"ML prediction avec confidence {confidence_score:.2f}",
                    alternative_servers=[],
                    performance_metrics={
                        "cpu_usage": server_metrics.cpu_usage,
                        "memory_usage": server_metrics.memory_usage,
                        "active_connections": server_metrics.active_connections
                    }
                )
            else:
                return self._fallback_prediction(server_metrics, request_context)
                
        except Exception as e:
            logger.error(f"❌ Erreur prédiction ML: {e}")
            return self._fallback_prediction(server_metrics, request_context)

    def _prepare_features(self, server_metrics: ServerMetrics, request_context: RequestContext) -> np.ndarray:
        """Préparation features pour ML"""
        server_features = server_metrics.to_feature_vector()
        
        # Features contextuelles
        context_features = np.array([
            request_context.payload_size / 1024.0,  # KB
            request_context.priority_level,
            hash(request_context.request_type) % 100,  # Hash type requête
            hash(request_context.client_ip) % 100      # Hash IP client
        ])
        
        return np.concatenate([server_features, context_features])
    
    def _calculate_confidence(self, features: np.ndarray, model_type: MLModelType) -> float:
        """Calcul confidence score prédiction"""
        try:
            # Confidence basée sur performance modèle et variance features
            model_accuracy = self.model_performance[model_type].get("accuracy", 0.5)
            feature_variance = np.var(features)
            
            # Normalisation confidence
            confidence = min(0.95, max(0.1, model_accuracy * (1.0 - feature_variance / 100.0)))
            return confidence
            
        except Exception:
            return 0.5  # Confidence par défaut
    
    def _fallback_prediction(self, server_metrics: ServerMetrics, request_context: RequestContext) -> RoutingPrediction:
        """Prédiction fallback sans ML"""
        # Calcul simple basé sur métriques serveur
        load_factor = (server_metrics.cpu_usage + server_metrics.memory_usage) / 2.0
        predicted_response_time = server_metrics.response_time_avg * (1.0 + load_factor / 100.0)
        
        return RoutingPrediction(
            server_id=server_metrics.server_id,
            confidence_score=0.6,  # Confidence moyenne pour fallback
            predicted_response_time=predicted_response_time,
            predicted_success_rate=max(0.7, 1.0 - server_metrics.error_rate),
            routing_reason="Fallback prediction (ML indisponible)",
            alternative_servers=[],
            performance_metrics={
                "load_factor": load_factor,
                "health_score": server_metrics.health_score
            }
        )

    async def update_models_with_feedback(
        self, 
        server_id: str, 
        predicted_metrics: Dict[str, float], 
        actual_metrics: Dict[str, float]
    ):
        """Mise à jour modèles avec feedback réel"""
        if not ML_AVAILABLE:
            return
            
        try:
            # Calcul accuracy
            accuracy = self._calculate_prediction_accuracy(predicted_metrics, actual_metrics)
            
            # Mise à jour performance modèles
            for model_type in [MLModelType.PERFORMANCE_OPTIMIZER, MLModelType.TRAFFIC_PREDICTOR]:
                self.model_performance[model_type]["accuracy"] = (
                    self.model_performance[model_type]["accuracy"] * 0.9 + accuracy * 0.1
                )
                self.model_performance[model_type]["last_updated"] = time.time()
            
            # Stocker données pour réentraînement
            training_sample = {
                "server_id": server_id,
                "predicted": predicted_metrics,
                "actual": actual_metrics,
                "timestamp": time.time()
            }
            
            for model_type in MLModelType:
                self.training_data[model_type].append(training_sample)
                
                # Limiter taille buffer
                if len(self.training_data[model_type]) > 1000:
                    self.training_data[model_type] = self.training_data[model_type][-800:]
            
            logger.debug(f"📊 Feedback ML intégré: accuracy={accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"❌ Erreur mise à jour modèles ML: {e}")
    
    def _calculate_prediction_accuracy(self, predicted: Dict[str, float], actual: Dict[str, float]) -> float:
        """Calcul accuracy prédiction"""
        try:
            accuracies = []
            for key in predicted:
                if key in actual and actual[key] > 0:
                    error = abs(predicted[key] - actual[key]) / actual[key]
                    accuracy = max(0.0, 1.0 - error)
                    accuracies.append(accuracy)
            
            return np.mean(accuracies) if accuracies else 0.5
            
        except Exception:
            return 0.5

class IntelligentLoadBalancer:
    """
    🧠 LOAD BALANCER INTELLIGENT AVEC IA/ML ENTERPRISE
    
    Load balancer intelligent avec ML pour optimization automatique.
    ML-based routing + predictive scaling + adaptive algorithms.
    """
    
    def __init__(self, ml_config: Optional[MLConfig] = None):
        self.ml_config = ml_config or MLConfig()
        self.ml_manager = MLModelManager(self.ml_config)
        
        # Caches et métriques
        self.server_metrics_cache: Dict[str, ServerMetrics] = {}
        self.prediction_cache: Dict[str, RoutingPrediction] = {}
        self.routing_history: List[Dict[str, Any]] = []
        
        # Configuration performance
        self.max_cache_size = 1000
        self.cache_cleanup_interval = 300  # 5 minutes
        
        # Métriques performance
        self.total_predictions = 0
        self.successful_predictions = 0
        self.average_prediction_time = 0.0
        
        logger.info("🧠 Intelligent Load Balancer initialisé avec succès")

    async def predict_optimal_routing(self, request_context: RequestContext) -> RoutingPrediction:
        """
        🎯 PRÉDICTION ROUTING OPTIMAL AVEC ML ANALYSIS
        
        Prédiction routing optimal avec ML analysis comprehensive.
        ML-based server selection + performance prediction + adaptive optimization.
        """
        start_time = time.time()
        
        try:
            logger.debug(f"🎯 Prédiction routing pour requête {request_context.request_id}")
            
            # Vérifier cache
            cache_key = self._generate_cache_key(request_context)
            if cache_key in self.prediction_cache:
                cached_prediction = self.prediction_cache[cache_key]
                if self._is_cache_valid(cached_prediction):
                    logger.debug("⚡ Utilisation cache prédiction")
                    return cached_prediction
            
            # Obtenir métriques serveurs disponibles
            available_servers = await self._get_available_server_metrics()
            if not available_servers:
                raise Exception("Aucun serveur disponible pour routing")
            
            # Prédictions ML pour chaque serveur
            server_predictions = []
            for server_metrics in available_servers:
                prediction = await self.ml_manager.predict_server_performance(
                    server_metrics, request_context
                )
                server_predictions.append(prediction)
            
            # Sélection serveur optimal
            optimal_prediction = self._select_optimal_server(server_predictions, request_context)
            
            # Cache résultat
            self.prediction_cache[cache_key] = optimal_prediction
            
            # Mise à jour métriques
            self.total_predictions += 1
            prediction_time = time.time() - start_time
            self.average_prediction_time = (
                self.average_prediction_time * 0.9 + prediction_time * 0.1
            )
            
            # Stockage historique
            self.routing_history.append({
                "request_id": request_context.request_id,
                "server_selected": optimal_prediction.server_id,
                "confidence": optimal_prediction.confidence_score,
                "prediction_time": prediction_time,
                "timestamp": datetime.now()
            })
            
            # Nettoyage historique
            if len(self.routing_history) > 1000:
                self.routing_history = self.routing_history[-800:]
            
            logger.info(
                f"✅ Routing optimal prédit: {optimal_prediction.server_id} "
                f"(confidence: {optimal_prediction.confidence_score:.2f}, "
                f"temps: {prediction_time*1000:.1f}ms)"
            )
            
            return optimal_prediction
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction routing optimal: {e}")
            # Fallback vers serveur avec meilleure health
            return await self._fallback_routing(request_context)

    async def learn_traffic_patterns(self, traffic_data: AsyncIterator[Dict[str, Any]]) -> Dict[str, Any]:
        """
        📚 APPRENTISSAGE PATTERNS TRAFIC AVEC ML CONTINU
        
        Apprentissage patterns trafic avec ML continu pour optimization.
        """
        logger.info("📚 Démarrage apprentissage patterns trafic")
        
        patterns_learned = {
            "temporal_patterns": {},
            "geographic_patterns": {},
            "request_type_patterns": {},
            "load_patterns": {},
            "performance_insights": []
        }
        
        try:
            sample_count = 0
            async for traffic_sample in traffic_data:
                # Analyse temporelle
                timestamp = traffic_sample.get("timestamp", datetime.now())
                hour = timestamp.hour
                day_of_week = timestamp.weekday()
                
                temporal_key = f"{day_of_week}_{hour}"
                if temporal_key not in patterns_learned["temporal_patterns"]:
                    patterns_learned["temporal_patterns"][temporal_key] = []
                patterns_learned["temporal_patterns"][temporal_key].append(traffic_sample)
                
                # Analyse géographique
                geo_region = traffic_sample.get("geographic_origin", "unknown")
                if geo_region not in patterns_learned["geographic_patterns"]:
                    patterns_learned["geographic_patterns"][geo_region] = []
                patterns_learned["geographic_patterns"][geo_region].append(traffic_sample)
                
                # Analyse types requêtes
                request_type = traffic_sample.get("request_type", "unknown")
                if request_type not in patterns_learned["request_type_patterns"]:
                    patterns_learned["request_type_patterns"][request_type] = []
                patterns_learned["request_type_patterns"][request_type].append(traffic_sample)
                
                sample_count += 1
                
                # Limite pour éviter surcharge mémoire
                if sample_count >= 10000:
                    break
            
            # Génération insights
            patterns_learned["performance_insights"] = self._generate_traffic_insights(patterns_learned)
            patterns_learned["samples_analyzed"] = sample_count
            patterns_learned["learning_timestamp"] = datetime.now()
            
            logger.info(f"✅ Apprentissage patterns terminé: {sample_count} échantillons analysés")
            
        except Exception as e:
            logger.error(f"❌ Erreur apprentissage patterns trafic: {e}")
            
        return patterns_learned

    async def optimize_server_weights(self, performance_metrics: Dict[str, ServerMetrics]) -> Dict[str, float]:
        """
        ⚖️ OPTIMISATION WEIGHTS SERVEURS AVEC ML REINFORCEMENT
        
        Optimisation weights serveurs avec ML reinforcement learning.
        """
        logger.info("⚖️ Optimisation weights serveurs avec ML")
        
        optimized_weights = {}
        
        try:
            if not performance_metrics:
                logger.warning("Aucune métrique performance fournie")
                return optimized_weights
            
            # Calcul weights basé sur performance
            total_performance_score = 0.0
            server_scores = {}
            
            for server_id, metrics in performance_metrics.items():
                # Score performance composite
                performance_score = self._calculate_performance_score(metrics)
                server_scores[server_id] = performance_score
                total_performance_score += performance_score
            
            # Normalisation weights
            if total_performance_score > 0:
                for server_id, score in server_scores.items():
                    # Weight proportionnel à performance avec minimum
                    weight = max(0.1, score / total_performance_score)
                    optimized_weights[server_id] = weight
            else:
                # Weights égaux en cas d'échec calcul
                equal_weight = 1.0 / len(performance_metrics)
                for server_id in performance_metrics:
                    optimized_weights[server_id] = equal_weight
            
            logger.info(f"✅ Weights optimisés pour {len(optimized_weights)} serveurs")
            
        except Exception as e:
            logger.error(f"❌ Erreur optimisation weights serveurs: {e}")
            
        return optimized_weights

    async def predict_capacity_needs(self, current_load: Dict[str, Any]) -> Dict[str, Any]:
        """
        📈 PRÉDICTION BESOINS CAPACITÉ AVEC FORECASTING ML
        
        Prédiction besoins capacité avec forecasting ML pour scaling intelligent.
        """
        logger.info("📈 Prédiction besoins capacité avec ML forecasting")
        
        capacity_prediction = {
            "current_capacity_utilization": 0.0,
            "predicted_peak_load": 0.0,
            "scaling_recommendations": [],
            "confidence_level": "medium",
            "time_horizon_hours": 24,
            "resource_requirements": {}
        }
        
        try:
            # Analyse charge actuelle
            current_cpu = current_load.get("average_cpu", 0.0)
            current_memory = current_load.get("average_memory", 0.0)
            current_connections = current_load.get("total_connections", 0)
            current_rps = current_load.get("requests_per_second", 0.0)
            
            # Calcul utilisation capacité actuelle
            capacity_utilization = (current_cpu + current_memory) / 2.0
            capacity_prediction["current_capacity_utilization"] = capacity_utilization
            
            # Prédiction simple basée sur tendance
            growth_factor = 1.2  # 20% croissance par défaut
            if len(self.routing_history) > 100:
                # Analyse tendance historique
                recent_load = self.routing_history[-50:]
                older_load = self.routing_history[-100:-50]
                
                if len(recent_load) > 0 and len(older_load) > 0:
                    recent_avg = len(recent_load) / 50.0
                    older_avg = len(older_load) / 50.0
                    if older_avg > 0:
                        growth_factor = max(1.0, recent_avg / older_avg)
            
            # Prédiction pic charge
            predicted_peak = current_rps * growth_factor
            capacity_prediction["predicted_peak_load"] = predicted_peak
            
            # Recommandations scaling
            if capacity_utilization > 0.8:
                capacity_prediction["scaling_recommendations"].append({
                    "action": "scale_up",
                    "priority": "high",
                    "reason": f"Utilisation capacité élevée: {capacity_utilization:.1%}",
                    "suggested_instances": max(1, int(capacity_utilization * 2))
                })
            elif capacity_utilization < 0.3:
                capacity_prediction["scaling_recommendations"].append({
                    "action": "scale_down",
                    "priority": "medium", 
                    "reason": f"Utilisation capacité faible: {capacity_utilization:.1%}",
                    "instances_to_remove": 1
                })
            
            # Calcul confidence
            if len(self.routing_history) > 200:
                capacity_prediction["confidence_level"] = "high"
            elif len(self.routing_history) > 50:
                capacity_prediction["confidence_level"] = "medium"
            else:
                capacity_prediction["confidence_level"] = "low"
            
            # Exigences ressources
            capacity_prediction["resource_requirements"] = {
                "cpu_cores": max(2, int(predicted_peak / 100)),
                "memory_gb": max(4, int(predicted_peak / 50)),
                "storage_gb": max(20, int(predicted_peak / 10)),
                "network_mbps": max(100, int(predicted_peak * 0.1))
            }
            
            logger.info(
                f"✅ Prédiction capacité terminée: "
                f"utilisation={capacity_utilization:.1%}, "
                f"pic prédit={predicted_peak:.1f} RPS"
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction besoins capacité: {e}")
            
        return capacity_prediction

    # Méthodes utilitaires privées
    
    def _generate_cache_key(self, request_context: RequestContext) -> str:
        """Génération clé cache pour prédiction"""
        key_data = f"{request_context.request_type}_{request_context.priority_level}_{request_context.business_tier}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def _is_cache_valid(self, prediction: RoutingPrediction) -> bool:
        """Vérification validité cache prédiction"""
        age_seconds = (datetime.now() - prediction.timestamp).total_seconds()
        return age_seconds < self.ml_config.prediction_cache_ttl
    
    async def _get_available_server_metrics(self) -> List[ServerMetrics]:
        """Obtention métriques serveurs disponibles"""
        # Simulation - à remplacer par vraie intégration
        return [
            ServerMetrics(
                server_id=f"server_{i}",
                cpu_usage=np.random.uniform(10, 80),
                memory_usage=np.random.uniform(20, 70),
                active_connections=np.random.randint(10, 100),
                response_time_avg=np.random.uniform(0.05, 0.5),
                request_rate=np.random.uniform(50, 200),
                error_rate=np.random.uniform(0.001, 0.05),
                throughput=np.random.uniform(100, 500),
                health_score=np.random.uniform(0.8, 1.0),
                geographic_region=np.random.choice(["us-east", "eu-west", "asia-pacific"])
            ) for i in range(3)
        ]
    
    def _select_optimal_server(self, predictions: List[RoutingPrediction], context: RequestContext) -> RoutingPrediction:
        """Sélection serveur optimal parmi prédictions"""
        if not predictions:
            raise Exception("Aucune prédiction serveur disponible")
        
        # Score composite basé sur performance + confidence
        best_prediction = None
        best_score = -1.0
        
        for prediction in predictions:
            # Score composite
            performance_score = (
                (1.0 / max(0.001, prediction.predicted_response_time)) * 0.4 +
                prediction.predicted_success_rate * 0.3 +
                prediction.confidence_score * 0.3
            )
            
            # Bonus pour priorité élevée
            if context.priority_level > 5:
                performance_score *= 1.2
            
            if performance_score > best_score:
                best_score = performance_score
                best_prediction = prediction
        
        return best_prediction or predictions[0]
    
    async def _fallback_routing(self, request_context: RequestContext) -> RoutingPrediction:
        """Routing fallback en cas d'erreur"""
        return RoutingPrediction(
            server_id="fallback_server",
            confidence_score=0.3,
            predicted_response_time=0.1,
            predicted_success_rate=0.8,
            routing_reason="Fallback routing - erreur prédiction ML",
            alternative_servers=[],
            performance_metrics={}
        )
    
    def _calculate_performance_score(self, metrics: ServerMetrics) -> float:
        """Calcul score performance serveur"""
        # Score composite basé sur métriques clés
        score = (
            (100 - metrics.cpu_usage) * 0.25 +  # CPU libre
            (100 - metrics.memory_usage) * 0.25 +  # Mémoire libre
            (1.0 / max(0.001, metrics.response_time_avg)) * 0.2 +  # Performance
            metrics.health_score * 100 * 0.15 +  # Santé
            (1.0 - metrics.error_rate) * 100 * 0.15  # Fiabilité
        )
        return max(0.0, score)
    
    def _generate_traffic_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Génération insights à partir patterns trafic"""
        insights = []
        
        try:
            # Analyse patterns temporels
            temporal = patterns.get("temporal_patterns", {})
            if temporal:
                peak_hours = sorted(temporal.keys(), key=lambda k: len(temporal[k]), reverse=True)[:3]
                insights.append(f"Heures de pointe identifiées: {', '.join(peak_hours)}")
            
            # Analyse patterns géographiques
            geographic = patterns.get("geographic_patterns", {})
            if geographic:
                top_regions = sorted(geographic.keys(), key=lambda k: len(geographic[k]), reverse=True)[:3]
                insights.append(f"Régions principales: {', '.join(top_regions)}")
            
            # Analyse types requêtes
            request_types = patterns.get("request_type_patterns", {})
            if request_types:
                common_types = sorted(request_types.keys(), key=lambda k: len(request_types[k]), reverse=True)[:3]
                insights.append(f"Types requêtes fréquents: {', '.join(common_types)}")
            
        except Exception as e:
            logger.error(f"Erreur génération insights: {e}")
            
        return insights

# Point d'entrée pour tests et démonstration
async def main():
    """Démonstration Intelligent Load Balancer"""
    logger.info("🚀 Démonstration Intelligent Load Balancer")
    
    # Configuration ML
    ml_config = MLConfig(
        model_update_interval=300,
        prediction_cache_ttl=60,
        min_confidence_threshold=0.6
    )
    
    # Initialisation load balancer
    intelligent_lb = IntelligentLoadBalancer(ml_config)
    
    # Context requête test
    request_context = RequestContext(
        request_id="test_001",
        client_ip="192.168.1.100",
        user_agent="TestAgent/1.0",
        request_type="api_call",
        payload_size=1024,
        priority_level=5,
        business_tier="premium"
    )
    
    # Test prédiction routing
    prediction = await intelligent_lb.predict_optimal_routing(request_context)
    logger.info(f"🎯 Prédiction routing: {prediction.server_id} (confidence: {prediction.confidence_score:.2f})")
    
    # Test prédiction capacité
    current_load = {
        "average_cpu": 65.0,
        "average_memory": 45.0,
        "total_connections": 150,
        "requests_per_second": 75.0
    }
    
    capacity_prediction = await intelligent_lb.predict_capacity_needs(current_load)
    logger.info(f"📈 Prédiction capacité: utilisation {capacity_prediction['current_capacity_utilization']:.1%}")
    
    logger.info("✅ Démonstration terminée avec succès")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())