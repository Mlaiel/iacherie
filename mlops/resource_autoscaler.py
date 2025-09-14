"""
Resource Autoscaler module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
🚀 Resource Auto-Scaler - Enterprise MLOps Platform
Backend Senior Expertise: Auto-scaler intelligent basé sur métriques ML et charge prédictive

Créateur: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Tous droits réservés.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import threading
import time
import psutil
import docker

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResourceType(Enum):
    """Types de ressources gérées"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"
    CUSTOM = "custom"

class ScalingDirection(Enum):
    """Direction du scaling"""
    UP = "up"
    DOWN = "down"
    NONE = "none"

class ScalingTrigger(Enum):
    """Déclencheurs de scaling"""
    METRIC_THRESHOLD = "metric_threshold"
    PREDICTIVE = "predictive"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    EVENT_DRIVEN = "event_driven"

class ScalingStrategy(Enum):
    """Stratégies de scaling"""
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    HYBRID = "hybrid"
    ML_OPTIMIZED = "ml_optimized"

@dataclass
class ResourceMetric:
    """Métrique de ressource"""
    resource_type: ResourceType
    current_value: float
    target_value: float
    threshold_min: float
    threshold_max: float
    unit: str
    timestamp: datetime
    source: str

@dataclass
class ScalingRule:
    """Règle de scaling"""
    rule_id: str
    resource_type: ResourceType
    metric_name: str
    threshold_up: float
    threshold_down: float
    scale_up_by: int
    scale_down_by: int
    cooldown_period: timedelta
    min_instances: int
    max_instances: int
    enabled: bool = True
    weight: float = 1.0

@dataclass
class PredictionModel:
    """Modèle de prédiction pour le scaling"""
    model_type: str
    model: Any
    scaler: StandardScaler
    features: List[str]
    last_trained: datetime
    accuracy_score: float
    training_data_size: int

@dataclass
class ScalingAction:
    """Action de scaling"""
    action_id: str
    timestamp: datetime
    direction: ScalingDirection
    trigger: ScalingTrigger
    resource_type: ResourceType
    current_instances: int
    target_instances: int
    actual_instances: int
    reason: str
    execution_time: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class AutoScalerConfig:
    """Configuration de l'auto-scaler"""
    strategy: ScalingStrategy
    prediction_window: timedelta
    metrics_retention: timedelta
    model_retrain_interval: timedelta
    cooldown_global: timedelta
    enable_predictive: bool = True
    enable_reactive: bool = True
    enable_cost_optimization: bool = True
    max_scaling_rate: int = 5  # instances par minute
    min_confidence_threshold: float = 0.8

class MetricsCollector:
    """Collecteur de métriques système et ML"""
    
    def __init__(self) -> None:
        self.docker_client = docker.from_env()
        self.metrics_buffer: List[Dict[str, Any]] = []
        self.is_collecting = False
        
    async def start_collection(self) -> None:
        """Démarre la collecte de métriques"""
        self.is_collecting = True
        asyncio.create_task(self._collect_system_metrics())
        asyncio.create_task(self._collect_container_metrics())
        asyncio.create_task(self._collect_ml_metrics())
        
    async def stop_collection(self) -> None:
        """Arrête la collecte de métriques"""
        self.is_collecting = False
        
    async def _collect_system_metrics(self) -> None:
        """Collecte les métriques système"""
        while self.is_collecting:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                metrics = {
                    'timestamp': datetime.now(),
                    'type': 'system',
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_percent': disk.percent,
                    'network_bytes_sent': network.bytes_sent,
                    'network_bytes_recv': network.bytes_recv
                }
                
                self.metrics_buffer.append(metrics)
                
                # Nettoyage du buffer
                if len(self.metrics_buffer) > 10000:
                    self.metrics_buffer = self.metrics_buffer[-5000:]
                
                await asyncio.sleep(10)  # Collecte toutes les 10 secondes
                
            except Exception as e:
                logger.error(f"Erreur collecte métriques système: {e}")
                await asyncio.sleep(10)
    
    async def _collect_container_metrics(self) -> None:
        """Collecte les métriques des containers"""
        while self.is_collecting:
            try:
                containers = self.docker_client.containers.list()
                
                for container in containers:
                    if 'mlops' in container.name:
                        stats = container.stats(stream=False)
                        
                        # Calcul du CPU
                        cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                                   stats['precpu_stats']['cpu_usage']['total_usage']
                        system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                                      stats['precpu_stats']['system_cpu_usage']
                        cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
                        
                        # Calcul de la mémoire
                        memory_usage = stats['memory_stats']['usage']
                        memory_limit = stats['memory_stats']['limit']
                        memory_percent = (memory_usage / memory_limit) * 100.0
                        
                        metrics = {
                            'timestamp': datetime.now(),
                            'type': 'container',
                            'container_id': container.id[:12],
                            'container_name': container.name,
                            'cpu_percent': cpu_percent,
                            'memory_percent': memory_percent,
                            'memory_usage_mb': memory_usage / (1024**2),
                            'memory_limit_mb': memory_limit / (1024**2)
                        }
                        
                        self.metrics_buffer.append(metrics)
                
                await asyncio.sleep(15)  # Collecte toutes les 15 secondes
                
            except Exception as e:
                logger.error(f"Erreur collecte métriques containers: {e}")
                await asyncio.sleep(15)
    
    async def _collect_ml_metrics(self) -> None:
        """Collecte les métriques ML spécifiques"""
        while self.is_collecting:
            try:
                # Simulation de métriques ML
                # En production, ceci collecterait les vraies métriques des modèles
                
                ml_metrics = {
                    'timestamp': datetime.now(),
                    'type': 'ml',
                    'inference_requests_per_second': np.random.uniform(10, 100),
                    'average_inference_time_ms': np.random.uniform(50, 200),
                    'model_accuracy': np.random.uniform(0.85, 0.95),
                    'queue_length': np.random.randint(0, 50),
                    'error_rate_percent': np.random.uniform(0.1, 5.0),
                    'gpu_utilization_percent': np.random.uniform(20, 90)
                }
                
                self.metrics_buffer.append(ml_metrics)
                
                await asyncio.sleep(5)  # Collecte toutes les 5 secondes
                
            except Exception as e:
                logger.error(f"Erreur collecte métriques ML: {e}")
                await asyncio.sleep(5)
    
    def get_recent_metrics(self, duration: timedelta) -> List[Dict[str, Any]]:
        """Récupère les métriques récentes"""
        cutoff_time = datetime.now() - duration
        return [
            metric for metric in self.metrics_buffer
            if metric['timestamp'] >= cutoff_time
        ]
    
    def get_metrics_by_type(self, metric_type: str, duration: timedelta) -> List[Dict[str, Any]]:
        """Récupère les métriques par type"""
        recent_metrics = self.get_recent_metrics(duration)
        return [
            metric for metric in recent_metrics
            if metric.get('type') == metric_type
        ]

class PredictiveEngine:
    """Engine de prédiction pour l'auto-scaling"""
    
    def __init__(self) -> None:
        self.models: Dict[str, PredictionModel] = {}
        self.feature_columns = [
            'cpu_percent', 'memory_percent', 'inference_rps', 
            'avg_inference_time', 'queue_length', 'hour_of_day', 
            'day_of_week', 'is_weekend'
        ]
        
    def prepare_features(self, metrics: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prépare les features pour l'entraînement/prédiction"""
        try:
            # Conversion en DataFrame
            df = pd.DataFrame(metrics)
            
            if df.empty:
                return pd.DataFrame(columns=self.feature_columns)
            
            # Agrégation par période de 5 minutes
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Regroupement des métriques par type
            system_metrics = df[df['type'] == 'system'].resample('5T').mean()
            ml_metrics = df[df['type'] == 'ml'].resample('5T').mean()
            
            # Fusion des métriques
            combined = pd.concat([system_metrics, ml_metrics], axis=1, suffixes=('_sys', '_ml'))
            
            # Features temporelles
            combined['hour_of_day'] = combined.index.hour
            combined['day_of_week'] = combined.index.dayofweek
            combined['is_weekend'] = (combined.index.dayofweek >= 5).astype(int)
            
            # Renommage et sélection des colonnes
            feature_mapping = {
                'cpu_percent': 'cpu_percent',
                'memory_percent': 'memory_percent',
                'inference_requests_per_second': 'inference_rps',
                'average_inference_time_ms': 'avg_inference_time',
                'queue_length': 'queue_length'
            }
            
            for old_name, new_name in feature_mapping.items():
                if old_name in combined.columns:
                    combined[new_name] = combined[old_name]
            
            # Sélection des features finales
            available_features = [col for col in self.feature_columns if col in combined.columns]
            result = combined[available_features].fillna(0)
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur préparation features: {e}")
            return pd.DataFrame(columns=self.feature_columns)
    
    async def train_model(self, metrics: List[Dict[str, Any]], target_metric: str) -> bool:
        """Entraîne un modèle de prédiction"""
        try:
            # Préparation des données
            features_df = self.prepare_features(metrics)
            
            if len(features_df) < 50:  # Minimum de données pour l'entraînement
                logger.warning("Pas assez de données pour l'entraînement")
                return False
            
            # Création de la variable cible (prédiction de la charge future)
            target = features_df['cpu_percent'].shift(-6)  # Prédiction 30 minutes en avance
            target = target.fillna(method='bfill')
            
            # Division des données
            train_size = int(len(features_df) * 0.8)
            X_train = features_df[:train_size]
            y_train = target[:train_size]
            X_test = features_df[train_size:]
            y_test = target[train_size:]
            
            # Normalisation
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Entraînement du modèle
            model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_train_scaled, y_train)
            
            # Évaluation
            accuracy = model.score(X_test_scaled, y_test)
            
            # Sauvegarde du modèle
            prediction_model = PredictionModel(
                model_type="RandomForest",
                model=model,
                scaler=scaler,
                features=list(features_df.columns),
                last_trained=datetime.now(),
                accuracy_score=accuracy,
                training_data_size=len(features_df)
            )
            
            self.models[target_metric] = prediction_model
            
            logger.info(f"Modèle {target_metric} entraîné avec précision: {accuracy:.3f}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur entraînement modèle: {e}")
            return False
    
    async def predict_load(
        self, 
        current_metrics: List[Dict[str, Any]], 
        prediction_horizon: timedelta
    ) -> Dict[str, float]:
        """Prédit la charge future"""
        try:
            predictions = {}
            
            # Préparation des features actuelles
            features_df = self.prepare_features(current_metrics)
            
            if features_df.empty:
                return predictions
            
            # Prédiction pour chaque modèle
            for metric_name, model_info in self.models.items():
                try:
                    # Dernières features
                    latest_features = features_df.iloc[-1:][model_info.features]
                    
                    # Normalisation
                    features_scaled = model_info.scaler.transform(latest_features)
                    
                    # Prédiction
                    prediction = model_info.model.predict(features_scaled)[0]
                    predictions[metric_name] = float(prediction)
                    
                except Exception as e:
                    logger.error(f"Erreur prédiction {metric_name}: {e}")
            
            return predictions
            
        except Exception as e:
            logger.error(f"Erreur prédiction charge: {e}")
            return {}
    
    def get_model_info(self) -> Dict[str, Dict[str, Any]]:
        """Récupère les informations des modèles"""
        return {
            model_name: {
                'model_type': model.model_type,
                'features': model.features,
                'last_trained': model.last_trained.isoformat(),
                'accuracy_score': model.accuracy_score,
                'training_data_size': model.training_data_size
            }
            for model_name, model in self.models.items()
        }

class CostOptimizer:
    """Optimiseur de coûts pour le scaling"""
    
    def __init__(self) -> None:
        self.cost_matrix = {
            'cpu_small': 0.05,    # $/heure
            'cpu_medium': 0.10,
            'cpu_large': 0.20,
            'gpu_small': 0.50,
            'gpu_medium': 1.00,
            'gpu_large': 2.00
        }
        
    def calculate_cost_impact(
        self, 
        current_instances: int, 
        target_instances: int, 
        instance_type: str
    ) -> Dict[str, float]:
        """Calcule l'impact sur les coûts d'un scaling"""
        
        base_cost = self.cost_matrix.get(instance_type, 0.10)
        
        current_cost_per_hour = current_instances * base_cost
        target_cost_per_hour = target_instances * base_cost
        
        cost_diff_per_hour = target_cost_per_hour - current_cost_per_hour
        cost_diff_per_day = cost_diff_per_hour * 24
        cost_diff_per_month = cost_diff_per_day * 30
        
        return {
            'current_cost_per_hour': current_cost_per_hour,
            'target_cost_per_hour': target_cost_per_hour,
            'cost_diff_per_hour': cost_diff_per_hour,
            'cost_diff_per_day': cost_diff_per_day,
            'cost_diff_per_month': cost_diff_per_month,
            'cost_efficiency_ratio': target_instances / current_instances if current_instances > 0 else 1.0
        }
    
    def recommend_instance_mix(
        self, 
        workload_requirements: Dict[str, float],
        budget_constraint: Optional[float] = None
    ) -> Dict[str, int]:
        """Recommande un mix optimal d'instances"""
        
        # Algorithme simple de répartition optimale
        # En production, ceci utiliserait des algorithmes d'optimisation plus sophistiqués
        
        recommendations = {}
        total_cost = 0.0
        
        # Priorisation par coût-efficacité
        sorted_instances = sorted(
            self.cost_matrix.items(), 
            key=lambda x: x[1]  # Tri par coût croissant
        )
        
        remaining_workload = workload_requirements.get('total_capacity', 100)
        
        for instance_type, cost_per_hour in sorted_instances:
            if budget_constraint and total_cost >= budget_constraint:
                break
            
            # Capacité par instance (simulée)
            capacity_per_instance = {
                'cpu_small': 10,
                'cpu_medium': 25,
                'cpu_large': 50,
                'gpu_small': 15,
                'gpu_medium': 35,
                'gpu_large': 70
            }.get(instance_type, 20)
            
            # Calcul du nombre d'instances nécessaires
            needed_instances = min(
                int(remaining_workload / capacity_per_instance) + 1,
                10  # Maximum par type
            )
            
            if budget_constraint:
                max_affordable = int((budget_constraint - total_cost) / cost_per_hour)
                needed_instances = min(needed_instances, max_affordable)
            
            if needed_instances > 0:
                recommendations[instance_type] = needed_instances
                total_cost += needed_instances * cost_per_hour
                remaining_workload -= needed_instances * capacity_per_instance
            
            if remaining_workload <= 0:
                break
        
        return recommendations

class ResourceAutoScaler:
    """Auto-scaler intelligent basé sur métriques ML et charge prédictive"""
    
    def __init__(self, config -> None: AutoScalerConfig) -> None:
        self.config = config
        self.scaling_rules: Dict[str, ScalingRule] = {}
        self.metrics_collector = MetricsCollector()
        self.predictive_engine = PredictiveEngine()
        self.cost_optimizer = CostOptimizer()
        self.scaling_history: List[ScalingAction] = []
        self.current_instances: Dict[str, int] = {}
        self.last_scaling_action = datetime.now() - config.cooldown_global
        self.is_running = False
        
    async def start(self) -> None:
        """Démarre l'auto-scaler"""
        try:
            logger.info("Démarrage de l'auto-scaler intelligent")
            
            # Démarrage de la collecte de métriques
            await self.metrics_collector.start_collection()
            
            # Démarrage des tâches de fond
            self.is_running = True
            asyncio.create_task(self._scaling_monitor())
            asyncio.create_task(self._model_trainer())
            asyncio.create_task(self._metrics_analyzer())
            
            logger.info("Auto-scaler démarré avec succès")
            
        except Exception as e:
            logger.error(f"Erreur démarrage auto-scaler: {e}")
            raise
    
    async def stop(self) -> None:
        """Arrête l'auto-scaler"""
        logger.info("Arrêt de l'auto-scaler")
        self.is_running = False
        await self.metrics_collector.stop_collection()
    
    def add_scaling_rule(self, rule -> None: ScalingRule) -> None:
        """Ajoute une règle de scaling"""
        self.scaling_rules[rule.rule_id] = rule
        logger.info(f"Règle de scaling ajoutée: {rule.rule_id}")
    
    def remove_scaling_rule(self, rule_id -> None: str) -> None:
        """Supprime une règle de scaling"""
        if rule_id in self.scaling_rules:
            del self.scaling_rules[rule_id]
            logger.info(f"Règle de scaling supprimée: {rule_id}")
    
    async def _scaling_monitor(self) -> None:
        """Monitor principal de scaling"""
        while self.is_running:
            try:
                # Vérification du cooldown global
                time_since_last_action = datetime.now() - self.last_scaling_action
                if time_since_last_action < self.config.cooldown_global:
                    await asyncio.sleep(30)
                    continue
                
                # Collecte des métriques récentes
                recent_metrics = self.metrics_collector.get_recent_metrics(timedelta(minutes=10))
                
                if not recent_metrics:
                    await asyncio.sleep(30)
                    continue
                
                # Analyse réactive
                if self.config.enable_reactive:
                    await self._reactive_scaling_analysis(recent_metrics)
                
                # Analyse prédictive
                if self.config.enable_predictive:
                    await self._predictive_scaling_analysis(recent_metrics)
                
                await asyncio.sleep(60)  # Analyse toutes les minutes
                
            except Exception as e:
                logger.error(f"Erreur monitor scaling: {e}")
                await asyncio.sleep(60)
    
    async def _reactive_scaling_analysis(self, metrics -> None: List[Dict[str, Any]]) -> None:
        """Analyse de scaling réactive basée sur les seuils"""
        try:
            # Calcul des métriques moyennes récentes
            recent_system_metrics = [m for m in metrics if m.get('type') == 'system']
            recent_ml_metrics = [m for m in metrics if m.get('type') == 'ml']
            
            if not recent_system_metrics or not recent_ml_metrics:
                return
            
            # Moyennes des métriques clés
            avg_cpu = np.mean([m['cpu_percent'] for m in recent_system_metrics])
            avg_memory = np.mean([m['memory_percent'] for m in recent_system_metrics])
            avg_inference_rps = np.mean([m['inference_requests_per_second'] for m in recent_ml_metrics])
            avg_queue_length = np.mean([m['queue_length'] for m in recent_ml_metrics])
            
            # Évaluation des règles de scaling
            for rule in self.scaling_rules.values():
                if not rule.enabled:
                    continue
                
                current_instances = self.current_instances.get(rule.resource_type.value, 1)
                
                # Détermination de la métrique à analyser
                metric_value = self._get_metric_value(rule.metric_name, {
                    'cpu_percent': avg_cpu,
                    'memory_percent': avg_memory,
                    'inference_rps': avg_inference_rps,
                    'queue_length': avg_queue_length
                })
                
                if metric_value is None:
                    continue
                
                # Évaluation scale-up
                if (metric_value > rule.threshold_up and 
                    current_instances < rule.max_instances):
                    
                    target_instances = min(
                        current_instances + rule.scale_up_by,
                        rule.max_instances
                    )
                    
                    await self._execute_scaling_action(
                        rule=rule,
                        direction=ScalingDirection.UP,
                        current_instances=current_instances,
                        target_instances=target_instances,
                        trigger=ScalingTrigger.METRIC_THRESHOLD,
                        reason=f"{rule.metric_name} = {metric_value:.2f} > {rule.threshold_up}"
                    )
                
                # Évaluation scale-down
                elif (metric_value < rule.threshold_down and 
                      current_instances > rule.min_instances):
                    
                    target_instances = max(
                        current_instances - rule.scale_down_by,
                        rule.min_instances
                    )
                    
                    await self._execute_scaling_action(
                        rule=rule,
                        direction=ScalingDirection.DOWN,
                        current_instances=current_instances,
                        target_instances=target_instances,
                        trigger=ScalingTrigger.METRIC_THRESHOLD,
                        reason=f"{rule.metric_name} = {metric_value:.2f} < {rule.threshold_down}"
                    )
            
        except Exception as e:
            logger.error(f"Erreur analyse réactive: {e}")
    
    async def _predictive_scaling_analysis(self, metrics -> None: List[Dict[str, Any]]) -> None:
        """Analyse de scaling prédictive basée sur ML"""
        try:
            # Prédiction de la charge future
            predictions = await self.predictive_engine.predict_load(
                current_metrics=metrics,
                prediction_horizon=self.config.prediction_window
            )
            
            if not predictions:
                return
            
            # Analyse des prédictions pour chaque règle
            for rule in self.scaling_rules.values():
                if not rule.enabled:
                    continue
                
                predicted_value = predictions.get('cpu_percent')  # Principale métrique prédite
                if predicted_value is None:
                    continue
                
                current_instances = self.current_instances.get(rule.resource_type.value, 1)
                
                # Seuils prédictifs (plus conservateurs)
                predictive_threshold_up = rule.threshold_up * 0.8
                predictive_threshold_down = rule.threshold_down * 1.2
                
                # Évaluation scale-up prédictif
                if (predicted_value > predictive_threshold_up and 
                    current_instances < rule.max_instances):
                    
                    target_instances = min(
                        current_instances + rule.scale_up_by,
                        rule.max_instances
                    )
                    
                    await self._execute_scaling_action(
                        rule=rule,
                        direction=ScalingDirection.UP,
                        current_instances=current_instances,
                        target_instances=target_instances,
                        trigger=ScalingTrigger.PREDICTIVE,
                        reason=f"Prédiction: {rule.metric_name} = {predicted_value:.2f} > {predictive_threshold_up}"
                    )
                
                # Évaluation scale-down prédictif
                elif (predicted_value < predictive_threshold_down and 
                      current_instances > rule.min_instances):
                    
                    target_instances = max(
                        current_instances - rule.scale_down_by,
                        rule.min_instances
                    )
                    
                    await self._execute_scaling_action(
                        rule=rule,
                        direction=ScalingDirection.DOWN,
                        current_instances=current_instances,
                        target_instances=target_instances,
                        trigger=ScalingTrigger.PREDICTIVE,
                        reason=f"Prédiction: {rule.metric_name} = {predicted_value:.2f} < {predictive_threshold_down}"
                    )
            
        except Exception as e:
            logger.error(f"Erreur analyse prédictive: {e}")
    
    def _get_metric_value(self, metric_name: str, metrics_dict: Dict[str, float]) -> Optional[float]:
        """Récupère la valeur d'une métrique"""
        return metrics_dict.get(metric_name)
    
    async def _execute_scaling_action(
        self,
        rule: ScalingRule,
        direction: ScalingDirection,
        current_instances: int,
        target_instances: int,
        trigger: ScalingTrigger,
        reason: str
    ) -> ScalingAction:
        """Exécute une action de scaling"""
        
        action_id = f"scale-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        start_time = time.time()
        
        try:
            # Vérification du taux de scaling
            if not self._check_scaling_rate_limit():
                logger.warning("Taux de scaling limite atteint")
                return self._create_failed_action(action_id, rule, direction, current_instances, 
                                                target_instances, trigger, reason, "Rate limit exceeded")
            
            # Optimisation des coûts
            if self.config.enable_cost_optimization:
                cost_impact = self.cost_optimizer.calculate_cost_impact(
                    current_instances, target_instances, "cpu_medium"  # Type par défaut
                )
                
                # Vérification de l'impact sur les coûts
                if cost_impact['cost_diff_per_month'] > 1000:  # Seuil de 1000$/mois
                    logger.warning(f"Impact coût élevé détecté: {cost_impact['cost_diff_per_month']:.2f}$/mois")
            
            # Simulation de l'exécution du scaling
            # En production, ceci interagirait avec l'orchestrateur (Kubernetes, Docker Swarm, etc.)
            await self._simulate_scaling_execution(rule.resource_type, target_instances)
            
            # Mise à jour de l'état
            self.current_instances[rule.resource_type.value] = target_instances
            self.last_scaling_action = datetime.now()
            
            execution_time = time.time() - start_time
            
            # Création de l'action réussie
            action = ScalingAction(
                action_id=action_id,
                timestamp=datetime.now(),
                direction=direction,
                trigger=trigger,
                resource_type=rule.resource_type,
                current_instances=current_instances,
                target_instances=target_instances,
                actual_instances=target_instances,
                reason=reason,
                execution_time=execution_time,
                success=True
            )
            
            self.scaling_history.append(action)
            
            logger.info(f"Scaling exécuté: {action_id} - {current_instances} -> {target_instances} instances")
            return action
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_message = str(e)
            
            logger.error(f"Erreur exécution scaling {action_id}: {error_message}")
            
            return self._create_failed_action(action_id, rule, direction, current_instances,
                                            target_instances, trigger, reason, error_message)
    
    def _create_failed_action(self, action_id: str, rule: ScalingRule, direction: ScalingDirection,
                            current_instances: int, target_instances: int, trigger: ScalingTrigger,
                            reason: str, error_message: str) -> ScalingAction:
        """Crée une action de scaling échouée"""
        action = ScalingAction(
            action_id=action_id,
            timestamp=datetime.now(),
            direction=direction,
            trigger=trigger,
            resource_type=rule.resource_type,
            current_instances=current_instances,
            target_instances=target_instances,
            actual_instances=current_instances,  # Pas de changement
            reason=reason,
            execution_time=0.0,
            success=False,
            error_message=error_message
        )
        
        self.scaling_history.append(action)
        return action
    
    def _check_scaling_rate_limit(self) -> bool:
        """Vérifie le taux limite de scaling"""
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_actions = [
            action for action in self.scaling_history
            if action.timestamp >= one_minute_ago and action.success
        ]
        
        return len(recent_actions) < self.config.max_scaling_rate
    
    async def _simulate_scaling_execution(self, resource_type -> None: ResourceType, target_instances -> None: int) -> None:
        """Simule l'exécution du scaling"""
        # Simulation du temps d'exécution
        await asyncio.sleep(np.random.uniform(2, 5))
        
        # En production, ceci exécuterait les vraies commandes de scaling:
        # - kubectl scale deployment
        # - docker service scale
        # - AWS Auto Scaling API
        # - Azure Scale Sets
        # - GCP Instance Groups
        
        logger.info(f"Scaling simulé: {resource_type.value} -> {target_instances} instances")
    
    async def _model_trainer(self) -> None:
        """Entraîne périodiquement les modèles de prédiction"""
        while self.is_running:
            try:
                # Récupération des données d'entraînement
                training_data = self.metrics_collector.get_recent_metrics(
                    self.config.metrics_retention
                )
                
                if len(training_data) > 100:  # Minimum de données
                    # Entraînement du modèle principal
                    await self.predictive_engine.train_model(training_data, "cpu_percent")
                    
                    logger.info("Modèles de prédiction ré-entraînés")
                
                # Attente avant le prochain entraînement
                await asyncio.sleep(self.config.model_retrain_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"Erreur entraînement modèles: {e}")
                await asyncio.sleep(3600)  # Retry dans 1 heure
    
    async def _metrics_analyzer(self) -> None:
        """Analyse continue des métriques pour optimisations"""
        while self.is_running:
            try:
                # Analyse des patterns de charge
                recent_metrics = self.metrics_collector.get_recent_metrics(timedelta(hours=24))
                
                if recent_metrics:
                    await self._analyze_usage_patterns(recent_metrics)
                    await self._optimize_scaling_rules(recent_metrics)
                
                await asyncio.sleep(1800)  # Analyse toutes les 30 minutes
                
            except Exception as e:
                logger.error(f"Erreur analyse métriques: {e}")
                await asyncio.sleep(1800)
    
    async def _analyze_usage_patterns(self, metrics -> None: List[Dict[str, Any]]) -> None:
        """Analyse les patterns d'utilisation"""
        try:
            # Conversion en DataFrame pour analyse
            df = pd.DataFrame(metrics)
            
            if df.empty:
                return
            
            # Analyse des patterns temporels
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            # Patterns de charge par heure
            system_metrics = df[df['type'] == 'system']
            if not system_metrics.empty:
                hourly_cpu = system_metrics.groupby('hour')['cpu_percent'].mean()
                peak_hours = hourly_cpu[hourly_cpu > hourly_cpu.mean() + hourly_cpu.std()].index.tolist()
                
                logger.info(f"Heures de pointe détectées: {peak_hours}")
            
        except Exception as e:
            logger.error(f"Erreur analyse patterns: {e}")
    
    async def _optimize_scaling_rules(self, metrics -> None: List[Dict[str, Any]]) -> None:
        """Optimise automatiquement les règles de scaling"""
        try:
            # Analyse de l'efficacité des scaling actions
            successful_actions = [a for a in self.scaling_history if a.success]
            
            if len(successful_actions) < 10:
                return
            
            # Calcul de métriques d'efficacité
            avg_execution_time = np.mean([a.execution_time for a in successful_actions])
            scale_up_actions = [a for a in successful_actions if a.direction == ScalingDirection.UP]
            scale_down_actions = [a for a in successful_actions if a.direction == ScalingDirection.DOWN]
            
            # Optimisation des seuils basée sur l'historique
            for rule_id, rule in self.scaling_rules.items():
                rule_actions = [a for a in successful_actions if a.resource_type == rule.resource_type]
                
                if len(rule_actions) >= 5:
                    # Ajustement conservateur des seuils
                    if len([a for a in rule_actions if a.direction == ScalingDirection.UP]) > len(scale_down_actions):
                        # Trop de scale-ups, augmenter le seuil
                        rule.threshold_up *= 1.05
                        logger.info(f"Seuil scale-up ajusté pour {rule_id}: {rule.threshold_up:.2f}")
            
        except Exception as e:
            logger.error(f"Erreur optimisation règles: {e}")
    
    async def manual_scale(
        self, 
        resource_type: ResourceType, 
        target_instances: int,
        reason: str = "Manual scaling"
    ) -> ScalingAction:
        """Exécute un scaling manuel"""
        current_instances = self.current_instances.get(resource_type.value, 1)
        
        direction = ScalingDirection.UP if target_instances > current_instances else ScalingDirection.DOWN
        
        # Création d'une règle temporaire pour l'exécution
        temp_rule = ScalingRule(
            rule_id="manual",
            resource_type=resource_type,
            metric_name="manual",
            threshold_up=0,
            threshold_down=0,
            scale_up_by=1,
            scale_down_by=1,
            cooldown_period=timedelta(0),
            min_instances=0,
            max_instances=100
        )
        
        return await self._execute_scaling_action(
            rule=temp_rule,
            direction=direction,
            current_instances=current_instances,
            target_instances=target_instances,
            trigger=ScalingTrigger.MANUAL,
            reason=reason
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Récupère le statut de l'auto-scaler"""
        recent_actions = [
            action for action in self.scaling_history
            if action.timestamp >= datetime.now() - timedelta(hours=24)
        ]
        
        successful_actions = [a for a in recent_actions if a.success]
        failed_actions = [a for a in recent_actions if not a.success]
        
        return {
            'is_running': self.is_running,
            'strategy': self.config.strategy.value,
            'total_scaling_rules': len(self.scaling_rules),
            'active_rules': len([r for r in self.scaling_rules.values() if r.enabled]),
            'current_instances': self.current_instances.copy(),
            'last_scaling_action': self.last_scaling_action.isoformat() if self.last_scaling_action else None,
            'scaling_stats_24h': {
                'total_actions': len(recent_actions),
                'successful_actions': len(successful_actions),
                'failed_actions': len(failed_actions),
                'success_rate': (len(successful_actions) / len(recent_actions) * 100) if recent_actions else 0
            },
            'predictive_models': self.predictive_engine.get_model_info(),
            'config': {
                'strategy': self.config.strategy.value,
                'prediction_window': str(self.config.prediction_window),
                'cooldown_global': str(self.config.cooldown_global),
                'max_scaling_rate': self.config.max_scaling_rate,
                'enable_predictive': self.config.enable_predictive,
                'enable_cost_optimization': self.config.enable_cost_optimization
            }
        }
    
    def get_scaling_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Récupère l'historique de scaling"""
        recent_actions = sorted(
            self.scaling_history, 
            key=lambda x: x.timestamp, 
            reverse=True
        )[:limit]
        
        return [
            {
                'action_id': action.action_id,
                'timestamp': action.timestamp.isoformat(),
                'direction': action.direction.value,
                'trigger': action.trigger.value,
                'resource_type': action.resource_type.value,
                'current_instances': action.current_instances,
                'target_instances': action.target_instances,
                'actual_instances': action.actual_instances,
                'reason': action.reason,
                'execution_time': action.execution_time,
                'success': action.success,
                'error_message': action.error_message
            }
            for action in recent_actions
        ]

# Factory pour la création de l'auto-scaler
def create_resource_auto_scaler(config: Dict[str, Any]) -> ResourceAutoScaler:
    """Factory pour créer un auto-scaler configuré"""
    
    auto_scaler_config = AutoScalerConfig(
        strategy=ScalingStrategy(config.get('strategy', 'ml_optimized')),
        prediction_window=timedelta(minutes=config.get('prediction_window_minutes', 30)),
        metrics_retention=timedelta(hours=config.get('metrics_retention_hours', 72)),
        model_retrain_interval=timedelta(hours=config.get('model_retrain_interval_hours', 6)),
        cooldown_global=timedelta(minutes=config.get('cooldown_global_minutes', 5)),
        enable_predictive=config.get('enable_predictive', True),
        enable_reactive=config.get('enable_reactive', True),
        enable_cost_optimization=config.get('enable_cost_optimization', True),
        max_scaling_rate=config.get('max_scaling_rate', 5),
        min_confidence_threshold=config.get('min_confidence_threshold', 0.8)
    )
    
    return ResourceAutoScaler(auto_scaler_config)

# Exemple d'utilisation
async def main() -> None:
    """Exemple d'utilisation de l'auto-scaler intelligent"""
    
    # Configuration
    config = {
        'strategy': 'ml_optimized',
        'prediction_window_minutes': 30,
        'metrics_retention_hours': 72,
        'model_retrain_interval_hours': 6,
        'cooldown_global_minutes': 5,
        'enable_predictive': True,
        'enable_reactive': True,
        'enable_cost_optimization': True,
        'max_scaling_rate': 5,
        'min_confidence_threshold': 0.8
    }
    
    # Création de l'auto-scaler
    auto_scaler = create_resource_auto_scaler(config)
    
    try:
        # Démarrage
        await auto_scaler.start()
        
        # Ajout de règles de scaling
        cpu_rule = ScalingRule(
            rule_id="cpu_scaling",
            resource_type=ResourceType.CPU,
            metric_name="cpu_percent",
            threshold_up=75.0,
            threshold_down=25.0,
            scale_up_by=2,
            scale_down_by=1,
            cooldown_period=timedelta(minutes=5),
            min_instances=2,
            max_instances=20
        )
        
        memory_rule = ScalingRule(
            rule_id="memory_scaling",
            resource_type=ResourceType.MEMORY,
            metric_name="memory_percent",
            threshold_up=80.0,
            threshold_down=30.0,
            scale_up_by=1,
            scale_down_by=1,
            cooldown_period=timedelta(minutes=3),
            min_instances=1,
            max_instances=15
        )
        
        auto_scaler.add_scaling_rule(cpu_rule)
        auto_scaler.add_scaling_rule(memory_rule)
        
        # Simulation de scaling manuel
        await auto_scaler.manual_scale(
            resource_type=ResourceType.CPU,
            target_instances=5,
            reason="Test initial"
        )
        
        # Attente pour observer le comportement
        await asyncio.sleep(60)
        
        # Affichage du statut
        status = auto_scaler.get_status()
        print(f"Statut auto-scaler: {json.dumps(status, indent=2)}")
        
        # Historique de scaling
        history = auto_scaler.get_scaling_history(10)
        print(f"Historique scaling: {json.dumps(history, indent=2)}")
        
    finally:
        # Arrêt
        await auto_scaler.stop()

if __name__ == "__main__":
    asyncio.run(main())