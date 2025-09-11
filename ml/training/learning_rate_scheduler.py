"""🚀 Learning Rate Scheduler - IA Influencer Agent Platform Enterprise
================================================================
Module: backend/ml/training/learning_rate_scheduler.py
Author: Fahed Mlaiel (mlaiel@live.de) - DevOps Expert
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 LEARNING RATE SCHEDULER AVANCÉ
Gestion intelligente des taux d'apprentissage
- Adaptive scheduling avec warm-up, decay, cyclical
- Creator-specific optimization profiles
- Multi-strategy scheduling automation
- Performance-based dynamic adjustment
"""

import asyncio
import logging
import time
import uuid
import math
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
from pathlib import Path

# Configuration
logger = logging.getLogger(__name__)

class SchedulerType(Enum):
    """Types de schedulers de learning rate"""
    STEP_LR = "step_lr"
    EXPONENTIAL_LR = "exponential_lr"
    COSINE_ANNEALING = "cosine_annealing"
    REDUCE_ON_PLATEAU = "reduce_on_plateau"
    CYCLIC_LR = "cyclic_lr"
    ONE_CYCLE_LR = "one_cycle_lr"
    WARM_UP_COSINE = "warm_up_cosine"
    CREATOR_ADAPTIVE = "creator_adaptive"

class CreatorType(Enum):
    """Types de créateurs pour optimisation spécialisée"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

@dataclass
class SchedulerConfig:
    """Configuration du scheduler de learning rate"""
    scheduler_type: SchedulerType
    base_lr: float = 0.001
    max_lr: float = 0.01
    min_lr: float = 1e-7
    warmup_epochs: int = 10
    total_epochs: int = 100
    step_size: int = 30
    gamma: float = 0.1
    T_max: int = 50
    eta_min: float = 0.0
    patience: int = 10
    factor: float = 0.5
    threshold: float = 1e-4
    cycle_momentum: bool = True
    base_momentum: float = 0.85
    max_momentum: float = 0.95
    div_factor: float = 25.0
    final_div_factor: float = 1e4
    pct_start: float = 0.3
    creator_type: Optional[CreatorType] = None
    creator_specific_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SchedulerState:
    """État du scheduler"""
    current_lr: float
    current_epoch: int = 0
    current_step: int = 0
    best_metric: Optional[float] = None
    plateau_count: int = 0
    warmup_completed: bool = False
    cycle_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
@dataclass
class SchedulerMetrics:
    """Métriques du scheduler"""
    lr_history: List[float] = field(default_factory=list)
    metric_history: List[float] = field(default_factory=list)
    epoch_history: List[int] = field(default_factory=list)
    adjustment_count: int = 0
    warmup_duration: float = 0.0
    convergence_epoch: Optional[int] = None
    optimal_lr: Optional[float] = None

class LearningRateScheduler:
    """🔧 Gestionnaire de scheduling de learning rate"""
    
    def __init__(self, config: SchedulerConfig):
        self.config = config
        self.state = SchedulerState(current_lr=config.base_lr)
        self.metrics = SchedulerMetrics()
        self.scheduler_id = str(uuid.uuid4())
        self._initialize_creator_specific_config()
        
        logger.info(f"Learning Rate Scheduler initialized: {self.scheduler_id}")
    
    def _initialize_creator_specific_config(self):
        """Initialise la configuration spécifique au créateur"""
        if not self.config.creator_type:
            return
            
        creator_configs = {
            CreatorType.MUSICIAN: {
                "warmup_epochs": 15,
                "cycle_length": 40,
                "lr_decay_factor": 0.8,
                "adaptive_threshold": 0.02
            },
            CreatorType.BLOGGER: {
                "warmup_epochs": 8,
                "cycle_length": 25,
                "lr_decay_factor": 0.9,
                "adaptive_threshold": 0.01
            },
            CreatorType.PHOTOGRAPHER: {
                "warmup_epochs": 12,
                "cycle_length": 35,
                "lr_decay_factor": 0.85,
                "adaptive_threshold": 0.015
            },
            CreatorType.INFLUENCER: {
                "warmup_epochs": 10,
                "cycle_length": 30,
                "lr_decay_factor": 0.88,
                "adaptive_threshold": 0.012
            },
            CreatorType.COMEDIAN: {
                "warmup_epochs": 6,
                "cycle_length": 20,
                "lr_decay_factor": 0.92,
                "adaptive_threshold": 0.008
            }
        }
        
        creator_config = creator_configs.get(self.config.creator_type, {})
        self.config.creator_specific_params.update(creator_config)
    
    async def get_learning_rate(self, epoch: int, step: int, metric: Optional[float] = None) -> float:
        """Calcule le learning rate pour l'époque/étape courante"""
        try:
            self.state.current_epoch = epoch
            self.state.current_step = step
            
            # Enregistrer la métrique
            if metric is not None:
                self.metrics.metric_history.append(metric)
                self.metrics.epoch_history.append(epoch)
            
            # Calculer le learning rate selon le type de scheduler
            if self.config.scheduler_type == SchedulerType.STEP_LR:
                lr = await self._step_lr(epoch)
            elif self.config.scheduler_type == SchedulerType.EXPONENTIAL_LR:
                lr = await self._exponential_lr(epoch)
            elif self.config.scheduler_type == SchedulerType.COSINE_ANNEALING:
                lr = await self._cosine_annealing(epoch)
            elif self.config.scheduler_type == SchedulerType.REDUCE_ON_PLATEAU:
                lr = await self._reduce_on_plateau(metric)
            elif self.config.scheduler_type == SchedulerType.CYCLIC_LR:
                lr = await self._cyclic_lr(step)
            elif self.config.scheduler_type == SchedulerType.ONE_CYCLE_LR:
                lr = await self._one_cycle_lr(step)
            elif self.config.scheduler_type == SchedulerType.WARM_UP_COSINE:
                lr = await self._warm_up_cosine(epoch)
            elif self.config.scheduler_type == SchedulerType.CREATOR_ADAPTIVE:
                lr = await self._creator_adaptive_lr(epoch, metric)
            else:
                lr = self.config.base_lr
            
            # Appliquer les limites
            lr = max(self.config.min_lr, min(self.config.max_lr, lr))
            
            self.state.current_lr = lr
            self.metrics.lr_history.append(lr)
            self.state.last_updated = datetime.now()
            
            return lr
            
        except Exception as e:
            logger.error(f"Error calculating learning rate: {e}")
            return self.config.base_lr
    
    async def _step_lr(self, epoch: int) -> float:
        """Step learning rate decay"""
        decay_count = epoch // self.config.step_size
        return self.config.base_lr * (self.config.gamma ** decay_count)
    
    async def _exponential_lr(self, epoch: int) -> float:
        """Exponential learning rate decay"""
        return self.config.base_lr * (self.config.gamma ** epoch)
    
    async def _cosine_annealing(self, epoch: int) -> float:
        """Cosine annealing scheduler"""
        return self.config.eta_min + (self.config.base_lr - self.config.eta_min) * \
               (1 + math.cos(math.pi * epoch / self.config.T_max)) / 2
    
    async def _reduce_on_plateau(self, metric: Optional[float]) -> float:
        """Reduce learning rate on plateau"""
        if metric is None:
            return self.state.current_lr
        
        if self.state.best_metric is None:
            self.state.best_metric = metric
            return self.state.current_lr
        
        # Vérifier si amélioration
        if metric <= self.state.best_metric - self.config.threshold:
            self.state.best_metric = metric
            self.state.plateau_count = 0
        else:
            self.state.plateau_count += 1
        
        # Réduire le LR si plateau détecté
        if self.state.plateau_count >= self.config.patience:
            self.state.plateau_count = 0
            self.metrics.adjustment_count += 1
            return self.state.current_lr * self.config.factor
        
        return self.state.current_lr
    
    async def _cyclic_lr(self, step: int) -> float:
        """Cyclical learning rate"""
        cycle = math.floor(1 + step / (2 * self.config.step_size))
        x = abs(step / self.config.step_size - 2 * cycle + 1)
        lr = self.config.base_lr + (self.config.max_lr - self.config.base_lr) * \
             max(0, (1 - x))
        return lr
    
    async def _one_cycle_lr(self, step: int) -> float:
        """One cycle learning rate policy"""
        total_steps = self.config.total_epochs * 100  # Approximation
        pct = step / total_steps
        
        if pct <= self.config.pct_start:
            # Montée du LR
            return self.config.base_lr + (self.config.max_lr - self.config.base_lr) * \
                   (pct / self.config.pct_start)
        else:
            # Descente du LR
            return self.config.max_lr - (self.config.max_lr - self.config.base_lr / self.config.final_div_factor) * \
                   ((pct - self.config.pct_start) / (1 - self.config.pct_start))
    
    async def _warm_up_cosine(self, epoch: int) -> float:
        """Warm-up followed by cosine annealing"""
        if epoch < self.config.warmup_epochs:
            # Phase de warm-up
            self.state.warmup_completed = False
            return self.config.base_lr * (epoch + 1) / self.config.warmup_epochs
        else:
            # Phase de cosine annealing
            if not self.state.warmup_completed:
                self.state.warmup_completed = True
                self.metrics.warmup_duration = epoch
            
            cosine_epoch = epoch - self.config.warmup_epochs
            cosine_total = self.config.total_epochs - self.config.warmup_epochs
            return self.config.eta_min + (self.config.base_lr - self.config.eta_min) * \
                   (1 + math.cos(math.pi * cosine_epoch / cosine_total)) / 2
    
    async def _creator_adaptive_lr(self, epoch: int, metric: Optional[float]) -> float:
        """Learning rate adaptatif spécifique au créateur"""
        base_lr = await self._warm_up_cosine(epoch)
        
        if metric is None or not self.config.creator_specific_params:
            return base_lr
        
        # Paramètres spécifiques au créateur
        adaptive_threshold = self.config.creator_specific_params.get('adaptive_threshold', 0.01)
        lr_decay_factor = self.config.creator_specific_params.get('lr_decay_factor', 0.9)
        
        # Adaptation basée sur la performance
        if len(self.metrics.metric_history) >= 3:
            recent_metrics = self.metrics.metric_history[-3:]
            metric_trend = np.polyfit(range(len(recent_metrics)), recent_metrics, 1)[0]
            
            if abs(metric_trend) < adaptive_threshold:
                # Plateau détecté, réduire le LR
                return base_lr * lr_decay_factor
            elif metric_trend > 0:
                # Performance dégradée, réduire plus agressivement
                return base_lr * (lr_decay_factor ** 2)
        
        return base_lr
    
    async def should_stop_training(self) -> bool:
        """Détermine si l'entraînement doit s'arrêter"""
        if self.state.current_lr <= self.config.min_lr:
            logger.info("Learning rate reached minimum, suggesting early stopping")
            return True
        
        # Early stopping basé sur la convergence
        if len(self.metrics.metric_history) >= 20:
            recent_variance = np.var(self.metrics.metric_history[-10:])
            if recent_variance < 1e-6:
                self.metrics.convergence_epoch = self.state.current_epoch
                logger.info(f"Convergence detected at epoch {self.state.current_epoch}")
                return True
        
        return False
    
    async def get_scheduler_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques du scheduler"""
        try:
            optimal_lr = None
            if self.metrics.metric_history and self.metrics.lr_history:
                # Trouver le LR optimal (celui qui donne la meilleure métrique)
                best_idx = np.argmin(self.metrics.metric_history)
                optimal_lr = self.metrics.lr_history[best_idx]
                self.metrics.optimal_lr = optimal_lr
            
            return {
                'scheduler_id': self.scheduler_id,
                'scheduler_type': self.config.scheduler_type.value,
                'creator_type': self.config.creator_type.value if self.config.creator_type else None,
                'current_lr': self.state.current_lr,
                'current_epoch': self.state.current_epoch,
                'adjustment_count': self.metrics.adjustment_count,
                'warmup_completed': self.state.warmup_completed,
                'warmup_duration': self.metrics.warmup_duration,
                'convergence_epoch': self.metrics.convergence_epoch,
                'optimal_lr': optimal_lr,
                'lr_range': {
                    'min': min(self.metrics.lr_history) if self.metrics.lr_history else self.config.min_lr,
                    'max': max(self.metrics.lr_history) if self.metrics.lr_history else self.config.max_lr,
                    'current': self.state.current_lr
                },
                'performance_trend': self._calculate_performance_trend(),
                'last_updated': self.state.last_updated.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting scheduler metrics: {e}")
            return {}
    
    def _calculate_performance_trend(self) -> Optional[str]:
        """Calcule la tendance de performance"""
        if len(self.metrics.metric_history) < 5:
            return None
        
        recent_metrics = self.metrics.metric_history[-5:]
        trend = np.polyfit(range(len(recent_metrics)), recent_metrics, 1)[0]
        
        if trend < -0.001:
            return "improving"
        elif trend > 0.001:
            return "degrading"
        else:
            return "stable"
    
    async def save_scheduler_state(self, filepath: str):
        """Sauvegarde l'état du scheduler"""
        try:
            state_data = {
                'config': {
                    'scheduler_type': self.config.scheduler_type.value,
                    'base_lr': self.config.base_lr,
                    'max_lr': self.config.max_lr,
                    'min_lr': self.config.min_lr,
                    'creator_type': self.config.creator_type.value if self.config.creator_type else None,
                    'creator_specific_params': self.config.creator_specific_params
                },
                'state': {
                    'current_lr': self.state.current_lr,
                    'current_epoch': self.state.current_epoch,
                    'best_metric': self.state.best_metric,
                    'plateau_count': self.state.plateau_count,
                    'warmup_completed': self.state.warmup_completed
                },
                'metrics': {
                    'lr_history': self.metrics.lr_history,
                    'metric_history': self.metrics.metric_history,
                    'adjustment_count': self.metrics.adjustment_count,
                    'optimal_lr': self.metrics.optimal_lr
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            logger.info(f"Scheduler state saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving scheduler state: {e}")
            raise

# Factory functions
def create_learning_rate_scheduler(
    scheduler_type: SchedulerType,
    creator_type: Optional[CreatorType] = None,
    **kwargs
) -> LearningRateScheduler:
    """Factory pour créer un scheduler de learning rate"""
    config = SchedulerConfig(
        scheduler_type=scheduler_type,
        creator_type=creator_type,
        **kwargs
    )
    return LearningRateScheduler(config)

def create_creator_optimized_scheduler(
    creator_type: CreatorType,
    base_lr: float = 0.001,
    total_epochs: int = 100
) -> LearningRateScheduler:
    """Crée un scheduler optimisé pour un type de créateur"""
    return create_learning_rate_scheduler(
        scheduler_type=SchedulerType.CREATOR_ADAPTIVE,
        creator_type=creator_type,
        base_lr=base_lr,
        total_epochs=total_epochs
    )

async def demo_learning_rate_scheduler():
    """Démo du scheduler de learning rate"""
    # Créer un scheduler pour musicien
    scheduler = create_creator_optimized_scheduler(
        creator_type=CreatorType.MUSICIAN,
        base_lr=0.001,
        total_epochs=50
    )
    
    print("📊 Learning Rate Scheduler Demo")
    
    # Simuler l'entraînement
    for epoch in range(10):
        # Simuler une métrique (loss qui diminue)
        metric = 1.0 - (epoch * 0.08) + np.random.normal(0, 0.02)
        
        lr = await scheduler.get_learning_rate(epoch, epoch * 100, metric)
        print(f"Epoch {epoch}: LR = {lr:.6f}, Metric = {metric:.4f}")
    
    # Métriques du scheduler
    metrics = await scheduler.get_scheduler_metrics()
    print(f"\n📈 Scheduler Metrics:")
    print(f"Optimal LR: {metrics.get('optimal_lr', 'N/A')}")
    print(f"Performance Trend: {metrics.get('performance_trend', 'N/A')}")
    print(f"Adjustments: {metrics.get('adjustment_count', 0)}")

if __name__ == "__main__":
    # Configurer le logging
    logging.basicConfig(level=logging.INFO)
    
    # Lancer la démo
    asyncio.run(demo_learning_rate_scheduler())