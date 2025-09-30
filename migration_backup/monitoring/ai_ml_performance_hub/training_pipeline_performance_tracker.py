"""
🚀 Training Pipeline Performance Tracker - Enterprise AI/ML Training Monitoring
============================================================================

Tracking performance des pipelines d'entraînement IA/ML pour Creator Economy.
Monitoring durée entraînement, convergence, utilisation ressources et efficacité.

⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Architecture: monitoring/ai_ml_performance_hub/training_pipeline_performance_tracker.py
Responsabilité: Tracking performance pipelines entraînement Creator Economy
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Audio + DevOps
"""

import asyncio
import logging
import time
import statistics
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
import uuid
import numpy as np
import pandas as pd
from pathlib import Path


class TrainingPhase(Enum):
    """Phases d'entraînement"""
    INITIALIZATION = "initialization"
    DATA_LOADING = "data_loading"
    MODEL_SETUP = "model_setup"
    TRAINING = "training"
    VALIDATION = "validation"
    EVALUATION = "evaluation"
    COMPLETION = "completion"


class ModelFramework(Enum):
    """Frameworks ML supportés"""
    TENSORFLOW = "tensorflow"
    PYTORCH = "pytorch"
    SCIKIT_LEARN = "scikit-learn"
    XGBOOST = "xgboost"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"


class TrainingType(Enum):
    """Types d'entraînement"""
    FULL_TRAINING = "full_training"
    FINE_TUNING = "fine_tuning"
    TRANSFER_LEARNING = "transfer_learning"
    INCREMENTAL_LEARNING = "incremental_learning"
    DISTRIBUTED_TRAINING = "distributed_training"


class CreatorContentType(Enum):
    """Type de contenu créateur"""
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    MIXED_MEDIA = "mixed_media"


@dataclass
class TrainingMetrics:
    """Métriques performance entraînement"""
    training_id: str
    model_name: str
    framework: ModelFramework
    training_type: TrainingType
    content_type: CreatorContentType
    
    # Performance metrics
    epoch: int
    total_epochs: int
    train_loss: float
    validation_loss: float
    train_accuracy: float
    validation_accuracy: float
    learning_rate: float
    
    # Time metrics
    epoch_duration: float  # seconds
    estimated_completion_time: float  # seconds
    total_training_time: float  # seconds
    
    # Resource metrics
    gpu_utilization: float  # percentage
    gpu_memory_usage: float  # MB
    cpu_utilization: float  # percentage
    ram_usage: float  # MB
    disk_io: float  # MB/s
    
    # Creator-specific metrics
    creator_tier: str
    data_size: int  # number of samples
    model_complexity: float  # parameters count
    
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConvergenceAnalysis:
    """Analyse convergence modèle"""
    training_id: str
    is_converged: bool
    convergence_epoch: Optional[int]
    convergence_score: float
    overfitting_detected: bool
    early_stopping_triggered: bool
    plateau_detected: bool
    recommended_epochs: int
    confidence_level: float


@dataclass
class ResourceEfficiencyMetrics:
    """Métriques efficacité ressources"""
    training_id: str
    gpu_efficiency: float  # utilization vs. time
    memory_efficiency: float
    compute_efficiency: float
    cost_per_epoch: float
    energy_consumption: float
    carbon_footprint: float
    resource_optimization_score: float


@dataclass
class TrainingComparison:
    """Comparaison performance entre entraînements"""
    baseline_training_id: str
    current_training_id: str
    performance_improvement: float
    training_time_reduction: float
    resource_efficiency_gain: float
    accuracy_delta: float
    recommendation: str


class TrainingPipelinePerformanceTracker:
    """Tracker performance pipeline entraînement enterprise"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Training tracking
        self.active_trainings: Dict[str, Dict[str, Any]] = {}
        self.training_history: Dict[str, List[TrainingMetrics]] = {}
        self.convergence_analyses: Dict[str, ConvergenceAnalysis] = {}
        self.resource_metrics: Dict[str, ResourceEfficiencyMetrics] = {}
        
        # Performance thresholds
        self.performance_thresholds = {
            'max_epoch_duration': 3600,  # 1 hour
            'min_gpu_utilization': 70,   # %
            'max_memory_usage': 32000,   # MB
            'convergence_patience': 10,   # epochs
            'overfitting_threshold': 0.1  # validation loss increase
        }
        
        # Creator tier configurations
        self.creator_tier_configs = {
            'free': {'max_training_time': 1800, 'max_epochs': 50},
            'premium': {'max_training_time': 7200, 'max_epochs': 200},
            'enterprise': {'max_training_time': 86400, 'max_epochs': 1000}
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Configuration logging"""
        logger = logging.getLogger("training_pipeline_tracker")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def start_training_tracking(self, 
                                    training_id: str,
                                    model_name: str,
                                    framework: ModelFramework,
                                    training_type: TrainingType,
                                    content_type: CreatorContentType,
                                    creator_tier: str = "free",
                                    total_epochs: int = 100,
                                    data_size: int = 1000) -> bool:
        """Démarrage tracking entraînement"""
        try:
            training_config = {
                'training_id': training_id,
                'model_name': model_name,
                'framework': framework,
                'training_type': training_type,
                'content_type': content_type,
                'creator_tier': creator_tier,
                'total_epochs': total_epochs,
                'data_size': data_size,
                'start_time': datetime.utcnow(),
                'status': 'active',
                'current_epoch': 0
            }
            
            self.active_trainings[training_id] = training_config
            self.training_history[training_id] = []
            
            self.logger.info(f"🚀 Started tracking training {training_id} for {model_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting training tracking: {e}")
            return False
    
    async def update_training_metrics(self, 
                                    training_id: str,
                                    epoch: int,
                                    metrics_data: Dict[str, Any]) -> bool:
        """Mise à jour métriques entraînement"""
        try:
            if training_id not in self.active_trainings:
                self.logger.warning(f"Training {training_id} not found")
                return False
            
            training_config = self.active_trainings[training_id]
            
            # Calculate timing metrics
            current_time = time.time()
            if hasattr(self, '_last_epoch_time') and training_id in self._last_epoch_time:
                epoch_duration = current_time - self._last_epoch_time[training_id]
            else:
                epoch_duration = 0
                if not hasattr(self, '_last_epoch_time'):
                    self._last_epoch_time = {}
            
            self._last_epoch_time[training_id] = current_time
            
            # Calculate estimated completion time
            if epoch > 0:
                avg_epoch_time = (current_time - training_config['start_time'].timestamp()) / epoch
                remaining_epochs = training_config['total_epochs'] - epoch
                estimated_completion = remaining_epochs * avg_epoch_time
            else:
                estimated_completion = 0
            
            # Create training metrics
            training_metrics = TrainingMetrics(
                training_id=training_id,
                model_name=training_config['model_name'],
                framework=training_config['framework'],
                training_type=training_config['training_type'],
                content_type=training_config['content_type'],
                epoch=epoch,
                total_epochs=training_config['total_epochs'],
                train_loss=metrics_data.get('train_loss', 0.0),
                validation_loss=metrics_data.get('validation_loss', 0.0),
                train_accuracy=metrics_data.get('train_accuracy', 0.0),
                validation_accuracy=metrics_data.get('validation_accuracy', 0.0),
                learning_rate=metrics_data.get('learning_rate', 0.001),
                epoch_duration=epoch_duration,
                estimated_completion_time=estimated_completion,
                total_training_time=current_time - training_config['start_time'].timestamp(),
                gpu_utilization=metrics_data.get('gpu_utilization', 0.0),
                gpu_memory_usage=metrics_data.get('gpu_memory_usage', 0.0),
                cpu_utilization=metrics_data.get('cpu_utilization', 0.0),
                ram_usage=metrics_data.get('ram_usage', 0.0),
                disk_io=metrics_data.get('disk_io', 0.0),
                creator_tier=training_config['creator_tier'],
                data_size=training_config['data_size'],
                model_complexity=metrics_data.get('model_complexity', 1000000)
            )
            
            # Store metrics
            self.training_history[training_id].append(training_metrics)
            training_config['current_epoch'] = epoch
            
            # Analyze convergence
            await self._analyze_convergence(training_id)
            
            # Check resource efficiency
            await self._analyze_resource_efficiency(training_id)
            
            # Check for alerts
            await self._check_training_alerts(training_metrics)
            
            self.logger.debug(f"Updated metrics for {training_id} epoch {epoch}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating training metrics: {e}")
            return False
    
    async def _analyze_convergence(self, training_id: str):
        """Analyse convergence entraînement"""
        try:
            if training_id not in self.training_history:
                return
            
            metrics_history = self.training_history[training_id]
            if len(metrics_history) < 5:  # Need minimum data points
                return
            
            # Get recent validation losses
            recent_losses = [m.validation_loss for m in metrics_history[-10:]]
            recent_accuracies = [m.validation_accuracy for m in metrics_history[-10:]]
            
            # Check for convergence
            loss_std = np.std(recent_losses) if recent_losses else 0
            is_converged = loss_std < 0.001  # Very stable loss
            
            # Find convergence epoch
            convergence_epoch = None
            if is_converged and len(metrics_history) >= 10:
                # Look for when loss stabilized
                for i in range(10, len(metrics_history)):
                    window_losses = [m.validation_loss for m in metrics_history[i-10:i]]
                    if np.std(window_losses) < 0.001:
                        convergence_epoch = metrics_history[i].epoch
                        break
            
            # Check for overfitting
            if len(recent_losses) >= 5:
                recent_trend = np.polyfit(range(len(recent_losses)), recent_losses, 1)[0]
                overfitting_detected = recent_trend > self.performance_thresholds['overfitting_threshold']
            else:
                overfitting_detected = False
            
            # Check for plateau
            plateau_detected = False
            if len(recent_accuracies) >= 5:
                accuracy_improvement = max(recent_accuracies) - min(recent_accuracies)
                plateau_detected = accuracy_improvement < 0.01  # Less than 1% improvement
            
            # Calculate convergence score
            if len(metrics_history) > 1:
                loss_improvement = metrics_history[0].validation_loss - metrics_history[-1].validation_loss
                convergence_score = min(1.0, max(0.0, loss_improvement))
            else:
                convergence_score = 0.0
            
            # Recommend optimal epochs
            if convergence_epoch:
                recommended_epochs = convergence_epoch + 5  # Add buffer
            else:
                recommended_epochs = len(metrics_history) + 10
            
            convergence_analysis = ConvergenceAnalysis(
                training_id=training_id,
                is_converged=is_converged,
                convergence_epoch=convergence_epoch,
                convergence_score=convergence_score,
                overfitting_detected=overfitting_detected,
                early_stopping_triggered=False,  # Would be set by training framework
                plateau_detected=plateau_detected,
                recommended_epochs=recommended_epochs,
                confidence_level=0.8 if is_converged else 0.5
            )
            
            self.convergence_analyses[training_id] = convergence_analysis
            
            if overfitting_detected:
                self.logger.warning(f"🚨 Overfitting detected for training {training_id}")
            elif is_converged:
                self.logger.info(f"✅ Convergence achieved for training {training_id}")
            
        except Exception as e:
            self.logger.error(f"Error analyzing convergence: {e}")
    
    async def _analyze_resource_efficiency(self, training_id: str):
        """Analyse efficacité ressources"""
        try:
            if training_id not in self.training_history:
                return
            
            metrics_history = self.training_history[training_id]
            if not metrics_history:
                return
            
            latest_metrics = metrics_history[-1]
            
            # Calculate efficiency scores
            gpu_efficiency = min(1.0, latest_metrics.gpu_utilization / 100.0)
            memory_efficiency = 1.0 - min(1.0, latest_metrics.gpu_memory_usage / 32000)  # Assuming 32GB GPU
            
            # Compute efficiency based on training speed vs resource usage
            if latest_metrics.epoch_duration > 0:
                compute_efficiency = min(1.0, 3600 / latest_metrics.epoch_duration)  # 1 hour baseline
            else:
                compute_efficiency = 0.0
            
            # Estimate cost (simplified)
            gpu_cost_per_hour = 2.5  # USD
            training_hours = latest_metrics.total_training_time / 3600
            cost_per_epoch = (gpu_cost_per_hour * training_hours) / max(1, latest_metrics.epoch)
            
            # Estimate energy consumption (simplified)
            gpu_power_watts = 250  # Typical GPU power
            energy_consumption = (gpu_power_watts * training_hours) / 1000  # kWh
            
            # Carbon footprint (simplified - assuming avg grid mix)
            carbon_intensity = 0.5  # kg CO2/kWh
            carbon_footprint = energy_consumption * carbon_intensity
            
            # Overall resource optimization score
            resource_optimization_score = np.mean([gpu_efficiency, memory_efficiency, compute_efficiency])
            
            resource_metrics = ResourceEfficiencyMetrics(
                training_id=training_id,
                gpu_efficiency=gpu_efficiency,
                memory_efficiency=memory_efficiency,
                compute_efficiency=compute_efficiency,
                cost_per_epoch=cost_per_epoch,
                energy_consumption=energy_consumption,
                carbon_footprint=carbon_footprint,
                resource_optimization_score=resource_optimization_score
            )
            
            self.resource_metrics[training_id] = resource_metrics
            
            if resource_optimization_score < 0.6:
                self.logger.warning(f"⚠️ Low resource efficiency for training {training_id}: {resource_optimization_score:.2f}")
            
        except Exception as e:
            self.logger.error(f"Error analyzing resource efficiency: {e}")
    
    async def _check_training_alerts(self, metrics: TrainingMetrics):
        """Vérification alertes entraînement"""
        alerts = []
        
        # Long epoch duration alert
        if metrics.epoch_duration > self.performance_thresholds['max_epoch_duration']:
            alerts.append(f"Epoch duration exceeded: {metrics.epoch_duration:.1f}s")
        
        # Low GPU utilization alert
        if metrics.gpu_utilization < self.performance_thresholds['min_gpu_utilization']:
            alerts.append(f"Low GPU utilization: {metrics.gpu_utilization:.1f}%")
        
        # High memory usage alert
        if metrics.gpu_memory_usage > self.performance_thresholds['max_memory_usage']:
            alerts.append(f"High GPU memory usage: {metrics.gpu_memory_usage:.1f}MB")
        
        # Creator tier limit alerts
        tier_config = self.creator_tier_configs.get(metrics.creator_tier, {})
        if 'max_training_time' in tier_config and metrics.total_training_time > tier_config['max_training_time']:
            alerts.append(f"Training time limit exceeded for {metrics.creator_tier} tier")
        
        for alert in alerts:
            self.logger.warning(f"🚨 Training Alert {metrics.training_id}: {alert}")
    
    async def complete_training(self, training_id: str) -> Dict[str, Any]:
        """Finalisation entraînement"""
        try:
            if training_id not in self.active_trainings:
                return {'success': False, 'message': 'Training not found'}
            
            training_config = self.active_trainings[training_id]
            training_config['status'] = 'completed'
            training_config['end_time'] = datetime.utcnow()
            
            # Generate final report
            report = await self.generate_training_report(training_id)
            
            # Move from active to completed
            del self.active_trainings[training_id]
            
            self.logger.info(f"✅ Training {training_id} completed successfully")
            return {'success': True, 'report': report}
            
        except Exception as e:
            self.logger.error(f"Error completing training: {e}")
            return {'success': False, 'message': str(e)}
    
    async def generate_training_report(self, training_id: str) -> Dict[str, Any]:
        """Génération rapport entraînement"""
        try:
            if training_id not in self.training_history:
                return {}
            
            metrics_history = self.training_history[training_id]
            if not metrics_history:
                return {}
            
            # Basic statistics
            final_metrics = metrics_history[-1]
            total_epochs = len(metrics_history)
            total_time = final_metrics.total_training_time
            
            # Performance summary
            best_accuracy = max(m.validation_accuracy for m in metrics_history)
            final_accuracy = final_metrics.validation_accuracy
            best_loss = min(m.validation_loss for m in metrics_history)
            final_loss = final_metrics.validation_loss
            
            # Efficiency metrics
            avg_epoch_time = statistics.mean([m.epoch_duration for m in metrics_history if m.epoch_duration > 0])
            avg_gpu_utilization = statistics.mean([m.gpu_utilization for m in metrics_history])
            
            # Convergence info
            convergence_info = self.convergence_analyses.get(training_id, {})
            
            # Resource efficiency
            resource_info = self.resource_metrics.get(training_id, {})
            
            report = {
                'training_summary': {
                    'training_id': training_id,
                    'model_name': final_metrics.model_name,
                    'framework': final_metrics.framework.value,
                    'total_epochs': total_epochs,
                    'total_time_hours': total_time / 3600,
                    'creator_tier': final_metrics.creator_tier
                },
                'performance_metrics': {
                    'final_accuracy': final_accuracy,
                    'best_accuracy': best_accuracy,
                    'final_loss': final_loss,
                    'best_loss': best_loss,
                    'accuracy_improvement': final_accuracy - metrics_history[0].validation_accuracy
                },
                'efficiency_metrics': {
                    'average_epoch_time': avg_epoch_time,
                    'average_gpu_utilization': avg_gpu_utilization,
                    'resource_optimization_score': getattr(resource_info, 'resource_optimization_score', 0.0)
                },
                'convergence_analysis': {
                    'converged': getattr(convergence_info, 'is_converged', False),
                    'convergence_epoch': getattr(convergence_info, 'convergence_epoch', None),
                    'overfitting_detected': getattr(convergence_info, 'overfitting_detected', False)
                },
                'recommendations': await self._generate_recommendations(training_id)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating training report: {e}")
            return {}
    
    async def _generate_recommendations(self, training_id: str) -> List[str]:
        """Génération recommandations"""
        recommendations = []
        
        try:
            if training_id not in self.training_history:
                return recommendations
            
            metrics_history = self.training_history[training_id]
            convergence_info = self.convergence_analyses.get(training_id)
            resource_info = self.resource_metrics.get(training_id)
            
            if not metrics_history:
                return recommendations
            
            latest_metrics = metrics_history[-1]
            
            # GPU utilization recommendations
            if latest_metrics.gpu_utilization < 50:
                recommendations.append("Consider increasing batch size to improve GPU utilization")
            
            # Convergence recommendations
            if convergence_info and convergence_info.overfitting_detected:
                recommendations.append("Add regularization techniques to prevent overfitting")
            
            if convergence_info and convergence_info.plateau_detected:
                recommendations.append("Consider learning rate scheduling or early stopping")
            
            # Resource efficiency recommendations
            if resource_info and resource_info.resource_optimization_score < 0.6:
                recommendations.append("Optimize resource usage through model quantization or pruning")
            
            # Creator tier recommendations
            if latest_metrics.creator_tier == "free" and latest_metrics.total_training_time > 1800:
                recommendations.append("Consider upgrading to premium tier for longer training times")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}")
            return recommendations
    
    async def compare_trainings(self, 
                              baseline_training_id: str, 
                              current_training_id: str) -> TrainingComparison:
        """Comparaison entre entraînements"""
        try:
            baseline_metrics = self.training_history.get(baseline_training_id, [])
            current_metrics = self.training_history.get(current_training_id, [])
            
            if not baseline_metrics or not current_metrics:
                return TrainingComparison(
                    baseline_training_id=baseline_training_id,
                    current_training_id=current_training_id,
                    performance_improvement=0.0,
                    training_time_reduction=0.0,
                    resource_efficiency_gain=0.0,
                    accuracy_delta=0.0,
                    recommendation="Insufficient data for comparison"
                )
            
            baseline_final = baseline_metrics[-1]
            current_final = current_metrics[-1]
            
            # Calculate improvements
            accuracy_delta = current_final.validation_accuracy - baseline_final.validation_accuracy
            performance_improvement = (accuracy_delta / baseline_final.validation_accuracy) * 100
            
            time_reduction = ((baseline_final.total_training_time - current_final.total_training_time) / 
                            baseline_final.total_training_time) * 100
            
            # Resource efficiency comparison
            baseline_resource = self.resource_metrics.get(baseline_training_id)
            current_resource = self.resource_metrics.get(current_training_id)
            
            if baseline_resource and current_resource:
                efficiency_gain = ((current_resource.resource_optimization_score - 
                                  baseline_resource.resource_optimization_score) / 
                                 baseline_resource.resource_optimization_score) * 100
            else:
                efficiency_gain = 0.0
            
            # Generate recommendation
            if performance_improvement > 5 and time_reduction > 10:
                recommendation = "Excellent improvement in both accuracy and training time"
            elif performance_improvement > 0 and efficiency_gain > 0:
                recommendation = "Good overall improvement"
            elif performance_improvement < -5:
                recommendation = "Performance regression detected - review training configuration"
            else:
                recommendation = "Marginal improvement - consider further optimization"
            
            return TrainingComparison(
                baseline_training_id=baseline_training_id,
                current_training_id=current_training_id,
                performance_improvement=performance_improvement,
                training_time_reduction=time_reduction,
                resource_efficiency_gain=efficiency_gain,
                accuracy_delta=accuracy_delta,
                recommendation=recommendation
            )
            
        except Exception as e:
            self.logger.error(f"Error comparing trainings: {e}")
            return TrainingComparison(
                baseline_training_id=baseline_training_id,
                current_training_id=current_training_id,
                performance_improvement=0.0,
                training_time_reduction=0.0,
                resource_efficiency_gain=0.0,
                accuracy_delta=0.0,
                recommendation=f"Error during comparison: {str(e)}"
            )
    
    async def get_creator_training_analytics(self, creator_tier: str) -> Dict[str, Any]:
        """Analytics entraînement par tier créateur"""
        try:
            # Filter trainings by creator tier
            tier_trainings = []
            for training_id, metrics_list in self.training_history.items():
                if metrics_list and metrics_list[0].creator_tier == creator_tier:
                    tier_trainings.extend(metrics_list)
            
            if not tier_trainings:
                return {'creator_tier': creator_tier, 'total_trainings': 0}
            
            # Calculate statistics
            total_trainings = len(set(m.training_id for m in tier_trainings))
            avg_accuracy = statistics.mean([m.validation_accuracy for m in tier_trainings])
            avg_training_time = statistics.mean([m.total_training_time for m in tier_trainings])
            avg_gpu_utilization = statistics.mean([m.gpu_utilization for m in tier_trainings])
            
            # Content type distribution
            content_types = {}
            for metrics in tier_trainings:
                content_type = metrics.content_type.value
                content_types[content_type] = content_types.get(content_type, 0) + 1
            
            return {
                'creator_tier': creator_tier,
                'total_trainings': total_trainings,
                'average_accuracy': avg_accuracy,
                'average_training_time_hours': avg_training_time / 3600,
                'average_gpu_utilization': avg_gpu_utilization,
                'content_type_distribution': content_types,
                'tier_limits': self.creator_tier_configs.get(creator_tier, {})
            }
            
        except Exception as e:
            self.logger.error(f"Error getting creator analytics: {e}")
            return {'creator_tier': creator_tier, 'error': str(e)}
    
    async def get_active_trainings(self) -> Dict[str, Any]:
        """Récupération entraînements actifs"""
        return {
            'total_active': len(self.active_trainings),
            'trainings': {
                training_id: {
                    'model_name': config['model_name'],
                    'current_epoch': config['current_epoch'],
                    'total_epochs': config['total_epochs'],
                    'progress': (config['current_epoch'] / config['total_epochs']) * 100,
                    'creator_tier': config['creator_tier'],
                    'start_time': config['start_time'].isoformat()
                }
                for training_id, config in self.active_trainings.items()
            }
        }
    
    async def shutdown(self):
        """Arrêt propre du tracker"""
        self.logger.info("⏹️ Arrêt Training Pipeline Performance Tracker...")
        
        # Save any pending data (if persistent storage implemented)
        # self._save_training_data()
        
        # Clear data
        self.active_trainings.clear()
        self.training_history.clear()
        self.convergence_analyses.clear()
        self.resource_metrics.clear()
        
        self.logger.info("✅ Training Pipeline Performance Tracker arrêté proprement")


# Point d'entrée pour tests
if __name__ == "__main__":
    async def test_training_tracker():
        config = {
            'debug': True,
            'storage_path': '/tmp/training_data'
        }
        
        tracker = TrainingPipelinePerformanceTracker(config)
        
        # Test training start
        success = await tracker.start_training_tracking(
            training_id="test_training_001",
            model_name="creator_content_classifier",
            framework=ModelFramework.PYTORCH,
            training_type=TrainingType.FINE_TUNING,
            content_type=CreatorContentType.MIXED_MEDIA,
            creator_tier="premium",
            total_epochs=50,
            data_size=10000
        )
        
        print(f"Training started: {success}")
        
        # Simulate training epochs
        for epoch in range(1, 11):
            await tracker.update_training_metrics("test_training_001", epoch, {
                'train_loss': 0.5 - (epoch * 0.02),
                'validation_loss': 0.6 - (epoch * 0.015),
                'train_accuracy': 0.7 + (epoch * 0.02),
                'validation_accuracy': 0.65 + (epoch * 0.015),
                'learning_rate': 0.001,
                'gpu_utilization': 75 + (epoch * 2),
                'gpu_memory_usage': 8000 + (epoch * 100),
                'cpu_utilization': 40 + (epoch * 1),
                'ram_usage': 16000 + (epoch * 200),
                'model_complexity': 1500000
            })
            
            await asyncio.sleep(0.1)  # Simulate epoch duration
        
        # Complete training
        result = await tracker.complete_training("test_training_001")
        print(f"Training completed: {result['success']}")
        
        # Get analytics
        analytics = await tracker.get_creator_training_analytics("premium")
        print(f"Premium tier analytics: {analytics}")
        
        print('✅ Training Pipeline Performance Tracker test passed')
        await tracker.shutdown()
    
    asyncio.run(test_training_tracker())