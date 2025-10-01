"""
AI Model Metrics Exporter Module
Exporteur métriques modèles IA spécialisé - IA Chéries Platform

⚠️ CONFIDENTIEL - IA Chéries Creator Platform ⚠️
🔒 PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - Fahed Mlaiel (mlaiel@live.de)

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS
"""

import time
import psutil
import threading
import numpy as np
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, Summary
import logging
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class ModelMetrics:
    """Métriques d'un modèle IA"""
    model_name: str
    model_version: str
    inference_count: int
    total_inference_time: float
    accuracy: float
    gpu_utilization: float
    memory_usage: float
    error_count: int

class AIModelMetricsExporter:
    """
    Exporteur métriques modèles IA spécialisé
    
    Fonctionnalités:
    - ML model performance metrics
    - Inference latency tracking
    - Model accuracy monitoring
    - GPU utilization metrics
    - Training pipeline metrics
    """
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self.model_metrics = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        self._initialize_metrics()
        
    def _initialize_metrics(self):
        """Initialise les métriques Prometheus pour l'IA"""
        
        # Métriques de performance des modèles
        self.model_inference_latency = Histogram(
            'ainflue_ai_model_inference_latency_seconds',
            'Model inference latency in seconds',
            labelnames=['model_name', 'model_version', 'input_type'],
            registry=self.registry
        )
        
        self.model_inference_total = Counter(
            'ainflue_ai_model_inference_total',
            'Total number of model inferences',
            labelnames=['model_name', 'model_version', 'status'],
            registry=self.registry
        )
        
        self.model_accuracy = Gauge(
            'ainflue_ai_model_accuracy',
            'Model prediction accuracy',
            labelnames=['model_name', 'model_version', 'dataset'],
            registry=self.registry
        )
        
        self.model_memory_usage = Gauge(
            'ainflue_ai_model_memory_usage_bytes',
            'Model memory usage in bytes',
            labelnames=['model_name', 'model_version', 'memory_type'],
            registry=self.registry
        )
        
        # Métriques GPU
        self.gpu_utilization = Gauge(
            'ainflue_ai_gpu_utilization_percent',
            'GPU utilization percentage',
            labelnames=['gpu_id', 'gpu_name'],
            registry=self.registry
        )
        
        self.gpu_memory_usage = Gauge(
            'ainflue_ai_gpu_memory_usage_bytes',
            'GPU memory usage in bytes',
            labelnames=['gpu_id', 'gpu_name', 'memory_type'],
            registry=self.registry
        )
        
        self.gpu_temperature = Gauge(
            'ainflue_ai_gpu_temperature_celsius',
            'GPU temperature in Celsius',
            labelnames=['gpu_id', 'gpu_name'],
            registry=self.registry
        )
        
        # Métriques de pipeline d'entraînement
        self.training_loss = Gauge(
            'ainflue_ai_training_loss',
            'Model training loss',
            labelnames=['model_name', 'epoch', 'loss_type'],
            registry=self.registry
        )
        
        self.training_time = Histogram(
            'ainflue_ai_training_time_seconds',
            'Model training time per epoch in seconds',
            labelnames=['model_name', 'model_version'],
            registry=self.registry
        )
        
        self.data_processing_time = Histogram(
            'ainflue_ai_data_processing_time_seconds',
            'Data preprocessing time in seconds',
            labelnames=['preprocessing_stage', 'data_type'],
            registry=self.registry
        )
        
        # Métriques business spécifiques Creator Economy
        self.content_enhancement_success_rate = Gauge(
            'ainflue_ai_content_enhancement_success_rate',
            'Content enhancement success rate',
            labelnames=['enhancement_type', 'content_format'],
            registry=self.registry
        )
        
        self.ai_protection_detection_rate = Gauge(
            'ainflue_ai_protection_detection_rate',
            'AI-powered protection detection rate',
            labelnames=['protection_type', 'threat_category'],
            registry=self.registry
        )
        
        self.recommendation_accuracy = Gauge(
            'ainflue_ai_recommendation_accuracy',
            'AI recommendation system accuracy',
            labelnames=['recommendation_type', 'creator_segment'],
            registry=self.registry
        )
        
        logger.info("AI Model metrics initialized")
    
    def start_monitoring(self, interval: int = 30):
        """Démarre le monitoring automatique des métriques"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
            
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitoring_thread.start()
        logger.info(f"Started AI metrics monitoring with {interval}s interval")
    
    def stop_monitoring(self):
        """Arrête le monitoring automatique"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Stopped AI metrics monitoring")
    
    def _monitoring_loop(self, interval: int):
        """Boucle de monitoring principal"""
        while self.monitoring_active:
            try:
                self._collect_system_metrics()
                self._collect_gpu_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
    
    def _collect_system_metrics(self):
        """Collecte les métriques système"""
        try:
            # Utilisation mémoire système
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()
            
            # Ces métriques peuvent être utilisées pour corréler avec les performances IA
            logger.debug(f"System metrics - Memory: {memory.percent}%, CPU: {cpu_percent}%")
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_gpu_metrics(self):
        """Collecte les métriques GPU"""
        try:
            # Simulation de collecte GPU (à remplacer par nvidia-ml-py ou équivalent)
            # Dans un environnement réel, utiliser pynvml pour NVIDIA GPUs
            self._simulate_gpu_metrics()
            
        except Exception as e:
            logger.error(f"Error collecting GPU metrics: {e}")
    
    def _simulate_gpu_metrics(self):
        """Simule les métriques GPU pour démonstration"""
        # Dans un environnement de production, remplacer par de vraies métriques GPU
        import random
        
        gpu_id = "0"
        gpu_name = "Tesla_V100"
        
        # Simulation des métriques
        utilization = random.uniform(20, 95)
        memory_used = random.uniform(1000000000, 8000000000)  # 1-8GB
        memory_total = 16000000000  # 16GB
        temperature = random.uniform(40, 85)
        
        self.gpu_utilization.labels(gpu_id=gpu_id, gpu_name=gpu_name).set(utilization)
        self.gpu_memory_usage.labels(
            gpu_id=gpu_id, 
            gpu_name=gpu_name, 
            memory_type="used"
        ).set(memory_used)
        self.gpu_memory_usage.labels(
            gpu_id=gpu_id, 
            gpu_name=gpu_name, 
            memory_type="total"
        ).set(memory_total)
        self.gpu_temperature.labels(gpu_id=gpu_id, gpu_name=gpu_name).set(temperature)
    
    def record_inference(self, 
                        model_name: str, 
                        model_version: str,
                        latency: float,
                        input_type: str = "unknown",
                        success: bool = True):
        """Enregistre une inférence de modèle"""
        try:
            # Latence d'inférence
            self.model_inference_latency.labels(
                model_name=model_name,
                model_version=model_version,
                input_type=input_type
            ).observe(latency)
            
            # Compteur d'inférences
            status = "success" if success else "error"
            self.model_inference_total.labels(
                model_name=model_name,
                model_version=model_version,
                status=status
            ).inc()
            
            logger.debug(f"Recorded inference for {model_name} v{model_version}: {latency:.3f}s")
            
        except Exception as e:
            logger.error(f"Error recording inference: {e}")
    
    def update_model_accuracy(self, 
                             model_name: str, 
                             model_version: str,
                             accuracy: float,
                             dataset: str = "test"):
        """Met à jour la précision du modèle"""
        try:
            self.model_accuracy.labels(
                model_name=model_name,
                model_version=model_version,
                dataset=dataset
            ).set(accuracy)
            
            logger.debug(f"Updated accuracy for {model_name} v{model_version}: {accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"Error updating model accuracy: {e}")
    
    def record_training_metrics(self,
                               model_name: str,
                               model_version: str,
                               epoch: int,
                               training_time: float,
                               train_loss: float,
                               val_loss: Optional[float] = None):
        """Enregistre les métriques d'entraînement"""
        try:
            # Temps d'entraînement
            self.training_time.labels(
                model_name=model_name,
                model_version=model_version
            ).observe(training_time)
            
            # Loss d'entraînement
            self.training_loss.labels(
                model_name=model_name,
                epoch=str(epoch),
                loss_type="train"
            ).set(train_loss)
            
            # Loss de validation si disponible
            if val_loss is not None:
                self.training_loss.labels(
                    model_name=model_name,
                    epoch=str(epoch),
                    loss_type="validation"
                ).set(val_loss)
            
            logger.debug(f"Recorded training metrics for {model_name} epoch {epoch}")
            
        except Exception as e:
            logger.error(f"Error recording training metrics: {e}")
    
    def record_memory_usage(self,
                           model_name: str,
                           model_version: str,
                           memory_bytes: int,
                           memory_type: str = "allocated"):
        """Enregistre l'utilisation mémoire du modèle"""
        try:
            self.model_memory_usage.labels(
                model_name=model_name,
                model_version=model_version,
                memory_type=memory_type
            ).set(memory_bytes)
            
            logger.debug(f"Recorded memory usage for {model_name}: {memory_bytes} bytes")
            
        except Exception as e:
            logger.error(f"Error recording memory usage: {e}")
    
    def record_data_processing(self,
                              processing_stage: str,
                              data_type: str,
                              processing_time: float):
        """Enregistre les métriques de traitement de données"""
        try:
            self.data_processing_time.labels(
                preprocessing_stage=processing_stage,
                data_type=data_type
            ).observe(processing_time)
            
            logger.debug(f"Recorded data processing: {processing_stage} took {processing_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Error recording data processing metrics: {e}")
    
    # Métriques spécifiques Creator Economy
    
    def update_content_enhancement_success_rate(self,
                                               enhancement_type: str,
                                               content_format: str,
                                               success_rate: float):
        """Met à jour le taux de succès d'amélioration de contenu"""
        try:
            self.content_enhancement_success_rate.labels(
                enhancement_type=enhancement_type,
                content_format=content_format
            ).set(success_rate)
            
            logger.debug(f"Updated content enhancement success rate: {success_rate:.3f}")
            
        except Exception as e:
            logger.error(f"Error updating content enhancement metrics: {e}")
    
    def update_ai_protection_detection_rate(self,
                                          protection_type: str,
                                          threat_category: str,
                                          detection_rate: float):
        """Met à jour le taux de détection de protection IA"""
        try:
            self.ai_protection_detection_rate.labels(
                protection_type=protection_type,
                threat_category=threat_category
            ).set(detection_rate)
            
            logger.debug(f"Updated AI protection detection rate: {detection_rate:.3f}")
            
        except Exception as e:
            logger.error(f"Error updating AI protection metrics: {e}")
    
    def update_recommendation_accuracy(self,
                                      recommendation_type: str,
                                      creator_segment: str,
                                      accuracy: float):
        """Met à jour la précision du système de recommandation"""
        try:
            self.recommendation_accuracy.labels(
                recommendation_type=recommendation_type,
                creator_segment=creator_segment
            ).set(accuracy)
            
            logger.debug(f"Updated recommendation accuracy: {accuracy:.3f}")
            
        except Exception as e:
            logger.error(f"Error updating recommendation metrics: {e}")
    
    def create_model_performance_decorator(self, 
                                         model_name: str, 
                                         model_version: str,
                                         input_type: str = "unknown"):
        """Crée un décorateur pour mesurer automatiquement les performances d'inférence"""
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):
                start_time = time.time()
                success = True
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    success = False
                    raise e
                finally:
                    latency = time.time() - start_time
                    self.record_inference(model_name, model_version, latency, input_type, success)
            return wrapper
        return decorator
    
    async def async_record_inference(self,
                                   model_name: str,
                                   model_version: str,
                                   latency: float,
                                   input_type: str = "unknown",
                                   success: bool = True):
        """Version asynchrone de l'enregistrement d'inférence"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, 
            self.record_inference,
            model_name, model_version, latency, input_type, success
        )
    
    def get_model_statistics(self, model_name: str) -> Dict[str, Any]:
        """Récupère les statistiques d'un modèle"""
        stats = {
            'model_name': model_name,
            'total_inferences': 0,
            'success_rate': 0.0,
            'average_latency': 0.0,
            'current_accuracy': 0.0
        }
        
        # Dans un environnement réel, ces statistiques seraient calculées
        # à partir des métriques Prometheus stockées
        logger.debug(f"Retrieved statistics for model: {model_name}")
        
        return stats
    
    def export_registry(self) -> CollectorRegistry:
        """Exporte le registry Prometheus"""
        return self.registry