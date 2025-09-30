"""Gradient Optimization Engine for Ainflue ML Platform

Advanced gradient optimization algorithms including Adam, RMSprop, custom optimizers,
and creator-specific optimization strategies for optimal learning.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.optimizer import Optimizer
import math
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
from enum import Enum
import json

logger = logging.getLogger(__name__)


class OptimizerType(Enum):
    """Optimizer type enumeration."""
    ADAM = "adam"
    ADAMW = "adamw"
    RMSPROP = "rmsprop"
    SGD = "sgd"
    ADAGRAD = "adagrad"
    CREATOR_ADAPTIVE = "creator_adaptive"
    MOMENTUM_SCHEDULE = "momentum_schedule"
    LOOKAHEAD = "lookahead"
    RANGER = "ranger"
    LION = "lion"


@dataclass
class OptimizationConfig:
    """Configuration for gradient optimization."""
    # Basic optimizer settings
    optimizer_type: OptimizerType = OptimizerType.ADAM
    learning_rate: float = 0.001
    weight_decay: float = 0.01
    momentum: float = 0.9
    
    # Adam-specific parameters
    beta1: float = 0.9
    beta2: float = 0.999
    epsilon: float = 1e-8
    amsgrad: bool = False
    
    # Learning rate scheduling
    use_scheduler: bool = True
    scheduler_type: str = "cosine_annealing"  # cosine_annealing, step, exponential, plateau
    warmup_epochs: int = 10
    max_epochs: int = 100
    min_lr: float = 1e-6
    
    # Gradient clipping
    gradient_clipping: bool = True
    max_grad_norm: float = 1.0
    
    # Advanced features
    use_lookahead: bool = False
    lookahead_k: int = 5
    lookahead_alpha: float = 0.5
    
    # Creator-specific adaptations
    creator_adaptive: bool = True
    content_type_adjustment: bool = True
    engagement_based_lr: bool = True
    
    # Convergence settings
    early_stopping: bool = True
    patience: int = 20
    min_delta: float = 1e-4


@dataclass
class CreatorOptimizationProfile:
    """Creator-specific optimization profile."""
    creator_id: str
    creator_type: str  # musician, photographer, blogger, influencer
    content_complexity: float = 0.5  # 0-1 scale
    learning_stability: float = 0.7  # how stable the learning should be
    convergence_speed: float = 0.6  # how fast to converge
    exploration_factor: float = 0.3  # how much to explore vs exploit
    engagement_sensitivity: float = 0.5  # how much engagement affects learning


class LookaheadOptimizer(Optimizer):
    """Lookahead optimizer wrapper."""
    
    def __init__(self, base_optimizer: Optimizer, k: int = 5, alpha: float = 0.5):
        self.base_optimizer = base_optimizer
        self.k = k
        self.alpha = alpha
        self.step_count = 0
        
        # Store slow weights
        self.slow_weights = {}
        for group in base_optimizer.param_groups:
            for p in group['params']:
                self.slow_weights[p] = p.data.clone()
    
    def step(self, closure=None):
        """Perform optimization step."""
        loss = self.base_optimizer.step(closure)
        self.step_count += 1
        
        if self.step_count % self.k == 0:
            # Update slow weights
            for group in self.base_optimizer.param_groups:
                for p in group['params']:
                    if p in self.slow_weights:
                        self.slow_weights[p] += self.alpha * (p.data - self.slow_weights[p])
                        p.data.copy_(self.slow_weights[p])
        
        return loss
    
    def zero_grad(self):
        """Zero gradients."""
        self.base_optimizer.zero_grad()
    
    @property
    def param_groups(self):
        """Get parameter groups."""
        return self.base_optimizer.param_groups
    
    @property
    def state(self):
        """Get optimizer state."""
        return self.base_optimizer.state


class LionOptimizer(Optimizer):
    """Lion optimizer implementation."""
    
    def __init__(self, params, lr=1e-4, betas=(0.9, 0.99), weight_decay=0.0):
        defaults = dict(lr=lr, betas=betas, weight_decay=weight_decay)
        super().__init__(params, defaults)
    
    def step(self, closure=None):
        """Perform optimization step."""
        loss = None
        if closure is not None:
            loss = closure()
        
        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue
                
                grad = p.grad.data
                if group['weight_decay'] != 0:
                    grad = grad.add(p.data, alpha=group['weight_decay'])
                
                state = self.state[p]
                
                # State initialization
                if len(state) == 0:
                    state['step'] = 0
                    state['exp_avg'] = torch.zeros_like(p.data)
                
                exp_avg = state['exp_avg']
                beta1, beta2 = group['betas']
                
                state['step'] += 1
                
                # Update momentum
                update = exp_avg * beta1 + grad * (1 - beta1)
                
                # Apply update
                p.data.add_(torch.sign(update), alpha=-group['lr'])
                
                # Update exponential moving average
                exp_avg.mul_(beta2).add_(grad, alpha=1 - beta2)
        
        return loss


class CreatorAdaptiveOptimizer(Optimizer):
    """Creator-specific adaptive optimizer."""
    
    def __init__(
        self,
        params,
        creator_profile: CreatorOptimizationProfile,
        base_lr: float = 0.001,
        betas: Tuple[float, float] = (0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0.01
    ):
        self.creator_profile = creator_profile
        
        # Adjust parameters based on creator profile
        adjusted_lr = self._adjust_learning_rate(base_lr)
        adjusted_betas = self._adjust_betas(betas)
        
        defaults = dict(
            lr=adjusted_lr,
            betas=adjusted_betas,
            eps=eps,
            weight_decay=weight_decay
        )
        super().__init__(params, defaults)
    
    def _adjust_learning_rate(self, base_lr: float) -> float:
        """Adjust learning rate based on creator profile."""
        # Content complexity affects learning rate
        complexity_factor = 1.0 - 0.3 * self.creator_profile.content_complexity
        
        # Learning stability affects learning rate
        stability_factor = 0.5 + 0.5 * self.creator_profile.learning_stability
        
        # Convergence speed affects learning rate
        speed_factor = 0.7 + 0.6 * self.creator_profile.convergence_speed
        
        adjusted_lr = base_lr * complexity_factor * stability_factor * speed_factor
        
        return max(adjusted_lr, 1e-6)  # Minimum learning rate
    
    def _adjust_betas(self, base_betas: Tuple[float, float]) -> Tuple[float, float]:
        """Adjust momentum parameters based on creator profile."""
        beta1, beta2 = base_betas
        
        # Exploration factor affects beta1 (first moment)
        exploration_adjustment = 0.05 * (self.creator_profile.exploration_factor - 0.5)
        adjusted_beta1 = max(0.5, min(0.99, beta1 + exploration_adjustment))
        
        # Learning stability affects beta2 (second moment)
        stability_adjustment = 0.1 * (self.creator_profile.learning_stability - 0.5)
        adjusted_beta2 = max(0.9, min(0.999, beta2 + stability_adjustment))
        
        return (adjusted_beta1, adjusted_beta2)
    
    def step(self, closure=None):
        """Perform optimization step."""
        loss = None
        if closure is not None:
            loss = closure()
        
        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue
                
                grad = p.grad.data
                if group['weight_decay'] != 0:
                    grad = grad.add(p.data, alpha=group['weight_decay'])
                
                state = self.state[p]
                
                # State initialization
                if len(state) == 0:
                    state['step'] = 0
                    state['exp_avg'] = torch.zeros_like(p.data)
                    state['exp_avg_sq'] = torch.zeros_like(p.data)
                
                exp_avg, exp_avg_sq = state['exp_avg'], state['exp_avg_sq']
                beta1, beta2 = group['betas']
                
                state['step'] += 1
                
                # Exponential moving average of gradient values
                exp_avg.mul_(beta1).add_(grad, alpha=1 - beta1)
                
                # Exponential moving average of squared gradient values
                exp_avg_sq.mul_(beta2).addcmul_(grad, grad, value=1 - beta2)
                
                # Bias correction
                bias_correction1 = 1 - beta1 ** state['step']
                bias_correction2 = 1 - beta2 ** state['step']
                
                step_size = group['lr'] / bias_correction1
                bias_correction2_sqrt = math.sqrt(bias_correction2)
                
                # Apply update
                denom = (exp_avg_sq.sqrt() / bias_correction2_sqrt).add_(group['eps'])
                p.data.addcdiv_(exp_avg, denom, value=-step_size)
        
        return loss


class GradientClipper:
    """Advanced gradient clipping utilities."""
    
    def __init__(self, max_norm: float = 1.0, norm_type: float = 2.0):
        self.max_norm = max_norm
        self.norm_type = norm_type
        self.gradient_history = []
    
    def clip_gradients(self, parameters) -> float:
        """Clip gradients and return gradient norm."""
        if isinstance(parameters, torch.Tensor):
            parameters = [parameters]
        
        parameters = list(filter(lambda p: p.grad is not None, parameters))
        
        if len(parameters) == 0:
            return 0.0
        
        # Calculate gradient norm
        total_norm = torch.norm(
            torch.stack([torch.norm(p.grad.detach(), self.norm_type) for p in parameters]),
            self.norm_type
        )
        
        # Store gradient history
        self.gradient_history.append(total_norm.item())
        if len(self.gradient_history) > 1000:
            self.gradient_history.pop(0)
        
        # Apply clipping
        clip_coef = self.max_norm / (total_norm + 1e-6)
        if clip_coef < 1:
            for p in parameters:
                p.grad.detach().mul_(clip_coef)
        
        return total_norm.item()
    
    def adaptive_clip(self, parameters, percentile: float = 95.0) -> float:
        """Adaptive gradient clipping based on gradient history."""
        if len(self.gradient_history) < 10:
            return self.clip_gradients(parameters)
        
        # Calculate adaptive threshold
        threshold = np.percentile(self.gradient_history, percentile)
        original_max_norm = self.max_norm
        self.max_norm = min(threshold, original_max_norm * 2)
        
        grad_norm = self.clip_gradients(parameters)
        
        # Restore original max norm
        self.max_norm = original_max_norm
        
        return grad_norm
    
    def get_gradient_stats(self) -> Dict[str, float]:
        """Get gradient statistics."""
        if not self.gradient_history:
            return {}
        
        return {
            'mean_grad_norm': np.mean(self.gradient_history),
            'std_grad_norm': np.std(self.gradient_history),
            'max_grad_norm': np.max(self.gradient_history),
            'min_grad_norm': np.min(self.gradient_history),
            'recent_grad_norm': self.gradient_history[-1] if self.gradient_history else 0.0
        }


class LearningRateScheduler:
    """Advanced learning rate scheduling."""
    
    def __init__(
        self,
        optimizer: Optimizer,
        config: OptimizationConfig,
        creator_profile: Optional[CreatorOptimizationProfile] = None
    ):
        self.optimizer = optimizer
        self.config = config
        self.creator_profile = creator_profile
        self.step_count = 0
        self.best_metric = None
        self.patience_counter = 0
        
        # Initialize scheduler
        self.scheduler = self._create_scheduler()
    
    def _create_scheduler(self):
        """Create appropriate scheduler based on configuration."""
        if self.config.scheduler_type == "cosine_annealing":
            return optim.lr_scheduler.CosineAnnealingLR(
                self.optimizer,
                T_max=self.config.max_epochs,
                eta_min=self.config.min_lr
            )
        elif self.config.scheduler_type == "step":
            return optim.lr_scheduler.StepLR(
                self.optimizer,
                step_size=self.config.max_epochs // 3,
                gamma=0.1
            )
        elif self.config.scheduler_type == "exponential":
            return optim.lr_scheduler.ExponentialLR(
                self.optimizer,
                gamma=0.95
            )
        elif self.config.scheduler_type == "plateau":
            return optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode='min',
                patience=self.config.patience // 2,
                factor=0.5,
                min_lr=self.config.min_lr
            )
        else:
            return None
    
    def step(self, metric: Optional[float] = None):
        """Step the learning rate scheduler."""
        self.step_count += 1
        
        # Apply warmup
        if self.step_count <= self.config.warmup_epochs:
            self._apply_warmup()
        else:
            # Use regular scheduler
            if self.config.scheduler_type == "plateau" and metric is not None:
                self.scheduler.step(metric)
            elif self.scheduler:
                self.scheduler.step()
        
        # Creator-specific adjustments
        if self.creator_profile and self.config.creator_adaptive:
            self._apply_creator_adjustments(metric)
    
    def _apply_warmup(self):
        """Apply learning rate warmup."""
        warmup_lr = self.config.learning_rate * (self.step_count / self.config.warmup_epochs)
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = warmup_lr
    
    def _apply_creator_adjustments(self, metric: Optional[float]):
        """Apply creator-specific learning rate adjustments."""
        if metric is None:
            return
        
        # Engagement-based adjustment
        if self.config.engagement_based_lr:
            engagement_factor = self.creator_profile.engagement_sensitivity
            
            # Increase LR if performance is good and we want faster convergence
            if metric > 0.8 and self.creator_profile.convergence_speed > 0.7:
                lr_multiplier = 1.1
            # Decrease LR if performance is poor and we want stability
            elif metric < 0.6 and self.creator_profile.learning_stability > 0.7:
                lr_multiplier = 0.95
            else:
                lr_multiplier = 1.0
            
            for param_group in self.optimizer.param_groups:
                param_group['lr'] *= lr_multiplier
    
    def get_current_lr(self) -> float:
        """Get current learning rate."""
        return self.optimizer.param_groups[0]['lr']


class GradientOptimizationEngine:
    """Comprehensive gradient optimization engine."""
    
    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.optimizers: Dict[str, Optimizer] = {}
        self.schedulers: Dict[str, LearningRateScheduler] = {}
        self.clippers: Dict[str, GradientClipper] = {}
        self.optimization_history: Dict[str, List[Dict]] = {}
        
        logger.info(f"Initialized GradientOptimizationEngine with {config.optimizer_type.value}")
    
    async def create_optimizer(
        self,
        model: nn.Module,
        optimizer_id: str,
        creator_profile: Optional[CreatorOptimizationProfile] = None
    ) -> Optimizer:
        """Create optimized optimizer for specific model and creator."""
        parameters = model.parameters()
        
        # Choose optimizer based on configuration
        if self.config.optimizer_type == OptimizerType.ADAM:
            optimizer = optim.Adam(
                parameters,
                lr=self.config.learning_rate,
                betas=(self.config.beta1, self.config.beta2),
                eps=self.config.epsilon,
                weight_decay=self.config.weight_decay,
                amsgrad=self.config.amsgrad
            )
        
        elif self.config.optimizer_type == OptimizerType.ADAMW:
            optimizer = optim.AdamW(
                parameters,
                lr=self.config.learning_rate,
                betas=(self.config.beta1, self.config.beta2),
                eps=self.config.epsilon,
                weight_decay=self.config.weight_decay,
                amsgrad=self.config.amsgrad
            )
        
        elif self.config.optimizer_type == OptimizerType.RMSPROP:
            optimizer = optim.RMSprop(
                parameters,
                lr=self.config.learning_rate,
                momentum=self.config.momentum,
                weight_decay=self.config.weight_decay,
                eps=self.config.epsilon
            )
        
        elif self.config.optimizer_type == OptimizerType.SGD:
            optimizer = optim.SGD(
                parameters,
                lr=self.config.learning_rate,
                momentum=self.config.momentum,
                weight_decay=self.config.weight_decay
            )
        
        elif self.config.optimizer_type == OptimizerType.ADAGRAD:
            optimizer = optim.Adagrad(
                parameters,
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay,
                eps=self.config.epsilon
            )
        
        elif self.config.optimizer_type == OptimizerType.CREATOR_ADAPTIVE:
            if creator_profile is None:
                raise ValueError("Creator profile required for creator adaptive optimizer")
            optimizer = CreatorAdaptiveOptimizer(
                parameters,
                creator_profile,
                base_lr=self.config.learning_rate,
                betas=(self.config.beta1, self.config.beta2),
                eps=self.config.epsilon,
                weight_decay=self.config.weight_decay
            )
        
        elif self.config.optimizer_type == OptimizerType.LION:
            optimizer = LionOptimizer(
                parameters,
                lr=self.config.learning_rate,
                betas=(self.config.beta1, self.config.beta2),
                weight_decay=self.config.weight_decay
            )
        
        else:
            # Default to Adam
            optimizer = optim.Adam(
                parameters,
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )
        
        # Apply Lookahead wrapper if configured
        if self.config.use_lookahead:
            optimizer = LookaheadOptimizer(
                optimizer,
                k=self.config.lookahead_k,
                alpha=self.config.lookahead_alpha
            )
        
        # Store optimizer and create associated components
        self.optimizers[optimizer_id] = optimizer
        
        # Create scheduler
        if self.config.use_scheduler:
            self.schedulers[optimizer_id] = LearningRateScheduler(
                optimizer, self.config, creator_profile
            )
        
        # Create gradient clipper
        if self.config.gradient_clipping:
            self.clippers[optimizer_id] = GradientClipper(
                max_norm=self.config.max_grad_norm
            )
        
        # Initialize optimization history
        self.optimization_history[optimizer_id] = []
        
        logger.info(f"Created optimizer {optimizer_id} with type {self.config.optimizer_type.value}")
        
        return optimizer
    
    async def optimization_step(
        self,
        optimizer_id: str,
        model: nn.Module,
        loss: torch.Tensor,
        performance_metric: Optional[float] = None
    ) -> Dict[str, float]:
        """Perform complete optimization step with monitoring."""
        if optimizer_id not in self.optimizers:
            raise ValueError(f"Optimizer {optimizer_id} not found")
        
        optimizer = self.optimizers[optimizer_id]
        step_metrics = {}
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Backward pass
        loss.backward()
        
        # Gradient clipping
        if optimizer_id in self.clippers:
            grad_norm = self.clippers[optimizer_id].clip_gradients(model.parameters())
            step_metrics['grad_norm'] = grad_norm
            
            # Get gradient statistics
            grad_stats = self.clippers[optimizer_id].get_gradient_stats()
            step_metrics.update(grad_stats)
        
        # Optimizer step
        optimizer.step()
        
        # Learning rate scheduling
        if optimizer_id in self.schedulers:
            self.schedulers[optimizer_id].step(performance_metric)
            step_metrics['learning_rate'] = self.schedulers[optimizer_id].get_current_lr()
        
        # Record optimization step
        step_record = {
            'timestamp': datetime.now(),
            'loss': loss.item(),
            'metrics': step_metrics,
            'performance_metric': performance_metric
        }
        
        self.optimization_history[optimizer_id].append(step_record)
        
        # Limit history size
        if len(self.optimization_history[optimizer_id]) > 10000:
            self.optimization_history[optimizer_id] = self.optimization_history[optimizer_id][-5000:]
        
        return step_metrics
    
    async def analyze_optimization_health(self, optimizer_id: str) -> Dict[str, Any]:
        """Analyze optimization health and suggest improvements."""
        if optimizer_id not in self.optimization_history:
            return {}
        
        history = self.optimization_history[optimizer_id]
        if len(history) < 10:
            return {'status': 'insufficient_data'}
        
        # Analyze recent performance
        recent_history = history[-100:]  # Last 100 steps
        
        losses = [h['loss'] for h in recent_history]
        grad_norms = [h['metrics'].get('grad_norm', 0) for h in recent_history]
        learning_rates = [h['metrics'].get('learning_rate', 0) for h in recent_history]
        
        analysis = {
            'status': 'healthy',
            'loss_trend': self._analyze_trend(losses),
            'gradient_health': self._analyze_gradient_health(grad_norms),
            'learning_rate_info': {
                'current_lr': learning_rates[-1] if learning_rates else 0,
                'lr_stability': np.std(learning_rates) if learning_rates else 0
            },
            'suggestions': []
        }
        
        # Generate suggestions
        if analysis['loss_trend'] == 'increasing':
            analysis['suggestions'].append("Consider reducing learning rate")
            analysis['status'] = 'warning'
        
        if analysis['gradient_health']['exploding_gradients']:
            analysis['suggestions'].append("Reduce learning rate or increase gradient clipping")
            analysis['status'] = 'critical'
        
        if analysis['gradient_health']['vanishing_gradients']:
            analysis['suggestions'].append("Consider increasing learning rate or using different optimizer")
            analysis['status'] = 'warning'
        
        if len(analysis['suggestions']) == 0:
            analysis['suggestions'].append("Optimization appears healthy")
        
        return analysis
    
    def _analyze_trend(self, values: List[float]) -> str:
        """Analyze trend in values."""
        if len(values) < 5:
            return 'unknown'
        
        # Simple linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.01:
            return 'increasing'
        elif slope < -0.01:
            return 'decreasing'
        else:
            return 'stable'
    
    def _analyze_gradient_health(self, grad_norms: List[float]) -> Dict[str, Any]:
        """Analyze gradient health."""
        if not grad_norms:
            return {'exploding_gradients': False, 'vanishing_gradients': False}
        
        mean_grad = np.mean(grad_norms)
        max_grad = np.max(grad_norms)
        min_grad = np.min(grad_norms)
        
        return {
            'mean_gradient_norm': mean_grad,
            'max_gradient_norm': max_grad,
            'min_gradient_norm': min_grad,
            'exploding_gradients': max_grad > 10.0,
            'vanishing_gradients': mean_grad < 1e-6,
            'gradient_variance': np.var(grad_norms)
        }
    
    async def optimize_for_creator(
        self,
        optimizer_id: str,
        creator_profile: CreatorOptimizationProfile,
        performance_history: List[float]
    ):
        """Optimize optimization strategy for specific creator."""
        if optimizer_id not in self.optimizers:
            return
        
        # Analyze performance trends
        if len(performance_history) > 10:
            performance_trend = self._analyze_trend(performance_history)
            
            # Adjust learning rate based on performance
            if performance_trend == 'decreasing' and creator_profile.convergence_speed > 0.7:
                # Increase learning rate for faster convergence
                for param_group in self.optimizers[optimizer_id].param_groups:
                    param_group['lr'] *= 1.1
            
            elif performance_trend == 'increasing' and creator_profile.learning_stability > 0.7:
                # Decrease learning rate for stability
                for param_group in self.optimizers[optimizer_id].param_groups:
                    param_group['lr'] *= 0.95
    
    def get_optimization_statistics(self, optimizer_id: str) -> Dict[str, Any]:
        """Get comprehensive optimization statistics."""
        if optimizer_id not in self.optimization_history:
            return {}
        
        history = self.optimization_history[optimizer_id]
        
        if not history:
            return {'total_steps': 0}
        
        losses = [h['loss'] for h in history]
        grad_norms = [h['metrics'].get('grad_norm', 0) for h in history if 'grad_norm' in h['metrics']]
        
        stats = {
            'total_steps': len(history),
            'loss_statistics': {
                'current_loss': losses[-1],
                'min_loss': min(losses),
                'max_loss': max(losses),
                'mean_loss': np.mean(losses),
                'loss_reduction': losses[0] - losses[-1] if len(losses) > 1 else 0
            },
            'gradient_statistics': {},
            'optimizer_type': self.config.optimizer_type.value,
            'current_config': self.config.__dict__
        }
        
        if grad_norms:
            stats['gradient_statistics'] = {
                'mean_grad_norm': np.mean(grad_norms),
                'max_grad_norm': max(grad_norms),
                'min_grad_norm': min(grad_norms),
                'grad_norm_std': np.std(grad_norms)
            }
        
        return stats
    
    def export_optimization_report(self, optimizer_id: str) -> Dict[str, Any]:
        """Export comprehensive optimization report."""
        stats = self.get_optimization_statistics(optimizer_id)
        health = asyncio.run(self.analyze_optimization_health(optimizer_id))
        
        report = {
            'optimizer_id': optimizer_id,
            'statistics': stats,
            'health_analysis': health,
            'configuration': self.config.__dict__,
            'timestamp': datetime.now().isoformat()
        }
        
        return report


# Factory functions for easy instantiation
def create_optimization_engine(
    optimizer_type: str = "adam",
    learning_rate: float = 0.001,
    **kwargs
) -> GradientOptimizationEngine:
    """Factory function to create gradient optimization engine."""
    config = OptimizationConfig(
        optimizer_type=OptimizerType(optimizer_type),
        learning_rate=learning_rate,
        **kwargs
    )
    return GradientOptimizationEngine(config)


def create_creator_profile(
    creator_id: str,
    creator_type: str,
    content_complexity: float = 0.5,
    learning_stability: float = 0.7,
    convergence_speed: float = 0.6,
    **kwargs
) -> CreatorOptimizationProfile:
    """Factory function to create creator optimization profile."""
    return CreatorOptimizationProfile(
        creator_id=creator_id,
        creator_type=creator_type,
        content_complexity=content_complexity,
        learning_stability=learning_stability,
        convergence_speed=convergence_speed,
        **kwargs
    )


# Example usage for Ainflue creators
async def example_gradient_optimization():
    """Example of gradient optimization for creator models."""
    
    # Create optimization engine
    engine = create_optimization_engine(
        optimizer_type="creator_adaptive",
        learning_rate=0.001,
        use_scheduler=True,
        gradient_clipping=True,
        creator_adaptive=True
    )
    
    # Create creator profiles
    musician_profile = create_creator_profile(
        creator_id="musician_123",
        creator_type="musician",
        content_complexity=0.7,  # Music is complex
        learning_stability=0.8,  # Need stable learning for audio quality
        convergence_speed=0.6,   # Moderate convergence speed
        engagement_sensitivity=0.7
    )
    
    photographer_profile = create_creator_profile(
        creator_id="photographer_456",
        creator_type="photographer",
        content_complexity=0.6,  # Visual content complexity
        learning_stability=0.7,  # Balance stability and adaptability
        convergence_speed=0.8,   # Faster convergence for visual feedback
        engagement_sensitivity=0.9
    )
    
    logger.info("Gradient optimization engine ready with creator-specific optimization")
    
    return engine


if __name__ == "__main__":
    # Run example
    asyncio.run(example_gradient_optimization())