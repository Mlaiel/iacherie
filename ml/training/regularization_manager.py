"""
Regularization Manager module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 ML Module - Regularization Manager
Intelligent regularization strategies including dropout, batch normalization, and weight decay

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
Version: 1.0.0
Letztes Update: Januar 2025

⚠️ WARNUNG: Dieser Code ist urheberrechtlich geschützt und vertraulich.
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
import json
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RegularizationType(Enum):
    """Types of regularization techniques."""
    DROPOUT = "dropout"
    BATCH_NORM = "batch_norm"
    LAYER_NORM = "layer_norm"
    WEIGHT_DECAY = "weight_decay"
    GRADIENT_CLIPPING = "gradient_clipping"
    SPECTRAL_NORM = "spectral_norm"
    MIXUP = "mixup"
    CUTMIX = "cutmix"
    LABEL_SMOOTHING = "label_smoothing"
    EARLY_STOPPING = "early_stopping"

class CreatorType(Enum):
    """Creator types for specialized regularization."""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"

@dataclass
class RegularizationConfig:
    """Configuration for regularization strategies."""
    regularization_type: RegularizationType
    strength: float
    adaptive: bool = True
    creator_specific: bool = True
    monitoring_enabled: bool = True
    auto_tuning: bool = True

@dataclass
class RegularizationMetrics:
    """Metrics for regularization effectiveness."""
    training_loss: float
    validation_loss: float
    overfitting_score: float
    generalization_gap: float
    convergence_stability: float
    regularization_impact: float
    creator_engagement_score: float
    timestamp: datetime

class RegularizationManager:
    """
    🎖️ LEAD DEV IA - Advanced Regularization Management System
    
    Intelligent regularization strategies with creator-specific optimization,
    adaptive strength tuning, and enterprise-grade monitoring.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize regularization manager."""
        self.config = config or {}
        self.regularization_configs: Dict[RegularizationType, RegularizationConfig] = {}
        self.performance_history: List[RegularizationMetrics] = []
        self.creator_profiles: Dict[CreatorType, Dict[str, Any]] = {}
        self.active_regularizers: Dict[str, nn.Module] = {}
        
        # Initialize logging
        logger.info("🎖️ RegularizationManager initialized - Lead Dev IA expertise")
        
        # Setup creator-specific profiles
        self._initialize_creator_profiles()
        
        # Setup default regularization configs
        self._initialize_default_configs()
    
    def _initialize_creator_profiles(self) -> None:
        """Initialize creator-specific regularization profiles."""
        self.creator_profiles = {
            CreatorType.MUSICIAN: {
                "preferred_dropout": 0.3,
                "batch_norm_momentum": 0.9,
                "weight_decay": 1e-4,
                "gradient_clip_norm": 1.0,
                "mixup_alpha": 0.2,
                "early_stopping_patience": 15
            },
            CreatorType.BLOGGER: {
                "preferred_dropout": 0.4,
                "batch_norm_momentum": 0.8,
                "weight_decay": 5e-4,
                "gradient_clip_norm": 0.5,
                "label_smoothing": 0.1,
                "early_stopping_patience": 20
            },
            CreatorType.PHOTOGRAPHER: {
                "preferred_dropout": 0.25,
                "batch_norm_momentum": 0.9,
                "weight_decay": 1e-3,
                "cutmix_alpha": 1.0,
                "spectral_norm": True,
                "early_stopping_patience": 10
            },
            CreatorType.INFLUENCER: {
                "preferred_dropout": 0.35,
                "batch_norm_momentum": 0.85,
                "weight_decay": 2e-4,
                "gradient_clip_norm": 2.0,
                "mixup_alpha": 0.4,
                "early_stopping_patience": 12
            },
            CreatorType.COMEDIAN: {
                "preferred_dropout": 0.45,
                "batch_norm_momentum": 0.9,
                "weight_decay": 1e-4,
                "label_smoothing": 0.15,
                "early_stopping_patience": 18
            }
        }
    
    def _initialize_default_configs(self) -> None:
        """Initialize default regularization configurations."""
        default_configs = {
            RegularizationType.DROPOUT: RegularizationConfig(
                regularization_type=RegularizationType.DROPOUT,
                strength=0.3,
                adaptive=True,
                creator_specific=True
            ),
            RegularizationType.BATCH_NORM: RegularizationConfig(
                regularization_type=RegularizationType.BATCH_NORM,
                strength=0.9,
                adaptive=True,
                creator_specific=True
            ),
            RegularizationType.WEIGHT_DECAY: RegularizationConfig(
                regularization_type=RegularizationType.WEIGHT_DECAY,
                strength=1e-4,
                adaptive=True,
                creator_specific=True
            ),
            RegularizationType.GRADIENT_CLIPPING: RegularizationConfig(
                regularization_type=RegularizationType.GRADIENT_CLIPPING,
                strength=1.0,
                adaptive=True,
                creator_specific=True
            )
        }
        
        self.regularization_configs.update(default_configs)
    
    async def apply_regularization(
        self,
        model: nn.Module,
        creator_type: CreatorType,
        regularization_types: List[RegularizationType]
    ) -> nn.Module:
        """
        Apply intelligent regularization to model based on creator type.
        
        Args:
            model: PyTorch model to regularize
            creator_type: Type of creator for specialized optimization
            regularization_types: List of regularization techniques to apply
            
        Returns:
            Regularized model
        """
        logger.info(f"🎯 Applying regularization for {creator_type.value}")
        
        # Get creator-specific parameters
        creator_params = self.creator_profiles.get(creator_type, {})
        
        # Apply each regularization technique
        for reg_type in regularization_types:
            model = await self._apply_single_regularization(
                model, reg_type, creator_params
            )
        
        # Register regularized model
        self.active_regularizers[f"{creator_type.value}_{int(time.time())}"] = model
        
        logger.info(f"✅ Regularization applied successfully for {creator_type.value}")
        return model
    
    async def _apply_single_regularization(
        self,
        model: nn.Module,
        reg_type: RegularizationType,
        creator_params: Dict[str, Any]
    ) -> nn.Module:
        """Apply a single regularization technique."""
        
        config = self.regularization_configs.get(reg_type)
        if not config:
            logger.warning(f"⚠️ No configuration found for {reg_type.value}")
            return model
        
        if reg_type == RegularizationType.DROPOUT:
            dropout_rate = creator_params.get("preferred_dropout", config.strength)
            model = self._apply_dropout(model, dropout_rate)
            
        elif reg_type == RegularizationType.BATCH_NORM:
            momentum = creator_params.get("batch_norm_momentum", config.strength)
            model = self._apply_batch_norm(model, momentum)
            
        elif reg_type == RegularizationType.LAYER_NORM:
            model = self._apply_layer_norm(model)
            
        elif reg_type == RegularizationType.SPECTRAL_NORM:
            if creator_params.get("spectral_norm", False):
                model = self._apply_spectral_norm(model)
        
        return model
    
    def _apply_dropout(self, model: nn.Module, dropout_rate: float) -> nn.Module:
        """Apply dropout regularization."""
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                # Add dropout before linear layers
                parent_name = name.rsplit('.', 1)[0] if '.' in name else ''
                if parent_name:
                    parent_module = dict(model.named_modules())[parent_name]
                    setattr(parent_module, name.split('.')[-1], 
                           nn.Sequential(nn.Dropout(dropout_rate), module))
        
        logger.info(f"🔧 Applied dropout regularization: {dropout_rate}")
        return model
    
    def _apply_batch_norm(self, model: nn.Module, momentum: float) -> nn.Module:
        """Apply batch normalization."""
        for name, module in model.named_modules():
            if isinstance(module, nn.BatchNorm1d):
                module.momentum = momentum
            elif isinstance(module, nn.BatchNorm2d):
                module.momentum = momentum
        
        logger.info(f"🔧 Applied batch normalization: momentum={momentum}")
        return model
    
    def _apply_layer_norm(self, model: nn.Module) -> nn.Module:
        """Apply layer normalization."""
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                # Add layer norm after linear layers
                normalized_size = module.out_features
                parent_name = name.rsplit('.', 1)[0] if '.' in name else ''
                if parent_name:
                    parent_module = dict(model.named_modules())[parent_name]
                    setattr(parent_module, name.split('.')[-1], 
                           nn.Sequential(module, nn.LayerNorm(normalized_size)))
        
        logger.info("🔧 Applied layer normalization")
        return model
    
    def _apply_spectral_norm(self, model: nn.Module) -> nn.Module:
        """Apply spectral normalization."""
        for name, module in model.named_modules():
            if isinstance(module, (nn.Linear, nn.Conv2d)):
                spectral_norm_module = nn.utils.spectral_norm(module)
                parent_name = name.rsplit('.', 1)[0] if '.' in name else ''
                if parent_name:
                    parent_module = dict(model.named_modules())[parent_name]
                    setattr(parent_module, name.split('.')[-1], spectral_norm_module)
        
        logger.info("🔧 Applied spectral normalization")
        return model
    
    async def adaptive_regularization_tuning(
        self,
        model: nn.Module,
        training_metrics: Dict[str, float],
        creator_type: CreatorType
    ) -> Dict[RegularizationType, float]:
        """
        Adaptively tune regularization strengths based on training metrics.
        
        Args:
            model: Model being trained
            training_metrics: Current training metrics
            creator_type: Creator type for specialized tuning
            
        Returns:
            Updated regularization strengths
        """
        logger.info("🎯 Performing adaptive regularization tuning")
        
        # Analyze current performance
        overfitting_score = self._calculate_overfitting_score(training_metrics)
        generalization_gap = self._calculate_generalization_gap(training_metrics)
        
        # Get creator-specific parameters
        creator_params = self.creator_profiles.get(creator_type, {})
        updated_strengths = {}
        
        # Adaptive tuning logic
        for reg_type, config in self.regularization_configs.items():
            if not config.adaptive:
                continue
                
            current_strength = config.strength
            
            if overfitting_score > 0.1:  # High overfitting
                if reg_type == RegularizationType.DROPOUT:
                    new_strength = min(current_strength * 1.2, 0.8)
                elif reg_type == RegularizationType.WEIGHT_DECAY:
                    new_strength = min(current_strength * 1.5, 1e-2)
                else:
                    new_strength = current_strength
            elif overfitting_score < 0.05:  # Low overfitting
                if reg_type == RegularizationType.DROPOUT:
                    new_strength = max(current_strength * 0.9, 0.1)
                elif reg_type == RegularizationType.WEIGHT_DECAY:
                    new_strength = max(current_strength * 0.8, 1e-6)
                else:
                    new_strength = current_strength
            else:
                new_strength = current_strength
            
            # Apply creator-specific constraints
            new_strength = self._apply_creator_constraints(
                new_strength, reg_type, creator_params
            )
            
            config.strength = new_strength
            updated_strengths[reg_type] = new_strength
        
        logger.info(f"✅ Adaptive tuning completed: {updated_strengths}")
        return updated_strengths
    
    def _calculate_overfitting_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overfitting score from training metrics."""
        train_loss = metrics.get("train_loss", 0.0)
        val_loss = metrics.get("val_loss", 0.0)
        
        if train_loss == 0:
            return 0.0
        
        overfitting_score = (val_loss - train_loss) / train_loss
        return max(0.0, overfitting_score)
    
    def _calculate_generalization_gap(self, metrics: Dict[str, float]) -> float:
        """Calculate generalization gap."""
        train_acc = metrics.get("train_accuracy", 0.0)
        val_acc = metrics.get("val_accuracy", 0.0)
        
        return max(0.0, train_acc - val_acc)
    
    def _apply_creator_constraints(
        self,
        strength: float,
        reg_type: RegularizationType,
        creator_params: Dict[str, Any]
    ) -> float:
        """Apply creator-specific constraints to regularization strength."""
        
        if reg_type == RegularizationType.DROPOUT:
            max_dropout = creator_params.get("preferred_dropout", 0.5) * 1.5
            return min(strength, max_dropout)
        elif reg_type == RegularizationType.WEIGHT_DECAY:
            max_decay = creator_params.get("weight_decay", 1e-3) * 2.0
            return min(strength, max_decay)
        
        return strength
    
    async def monitor_regularization_effectiveness(
        self,
        model: nn.Module,
        training_metrics: Dict[str, float],
        creator_type: CreatorType
    ) -> RegularizationMetrics:
        """
        Monitor the effectiveness of applied regularization.
        
        Args:
            model: Model being monitored
            training_metrics: Current training metrics
            creator_type: Creator type for analysis
            
        Returns:
            Regularization effectiveness metrics
        """
        logger.info("📊 Monitoring regularization effectiveness")
        
        # Calculate effectiveness metrics
        overfitting_score = self._calculate_overfitting_score(training_metrics)
        generalization_gap = self._calculate_generalization_gap(training_metrics)
        
        # Calculate convergence stability
        convergence_stability = self._calculate_convergence_stability()
        
        # Calculate regularization impact
        regularization_impact = self._calculate_regularization_impact(training_metrics)
        
        # Calculate creator engagement score
        creator_engagement_score = self._calculate_creator_engagement_score(
            creator_type, training_metrics
        )
        
        # Create metrics object
        metrics = RegularizationMetrics(
            training_loss=training_metrics.get("train_loss", 0.0),
            validation_loss=training_metrics.get("val_loss", 0.0),
            overfitting_score=overfitting_score,
            generalization_gap=generalization_gap,
            convergence_stability=convergence_stability,
            regularization_impact=regularization_impact,
            creator_engagement_score=creator_engagement_score,
            timestamp=datetime.now()
        )
        
        # Store metrics
        self.performance_history.append(metrics)
        
        logger.info(f"✅ Regularization monitoring completed: impact={regularization_impact:.3f}")
        return metrics
    
    def _calculate_convergence_stability(self) -> float:
        """Calculate convergence stability from recent metrics."""
        if len(self.performance_history) < 5:
            return 1.0
        
        recent_losses = [m.training_loss for m in self.performance_history[-5:]]
        loss_variance = np.var(recent_losses)
        
        # Normalize to 0-1 scale (lower variance = higher stability)
        stability = 1.0 / (1.0 + loss_variance)
        return stability
    
    def _calculate_regularization_impact(self, metrics: Dict[str, float]) -> float:
        """Calculate the impact of regularization on model performance."""
        # Combine multiple factors into a single impact score
        overfitting_prevention = 1.0 - self._calculate_overfitting_score(metrics)
        generalization_improvement = 1.0 - self._calculate_generalization_gap(metrics)
        
        # Weight the factors
        impact = (overfitting_prevention * 0.6 + generalization_improvement * 0.4)
        return max(0.0, min(1.0, impact))
    
    def _calculate_creator_engagement_score(
        self,
        creator_type: CreatorType,
        metrics: Dict[str, float]
    ) -> float:
        """Calculate creator-specific engagement score."""
        base_score = metrics.get("accuracy", 0.0)
        
        # Creator-specific adjustments
        creator_multipliers = {
            CreatorType.MUSICIAN: 1.1,      # Audio quality matters more
            CreatorType.BLOGGER: 1.05,      # Text understanding
            CreatorType.PHOTOGRAPHER: 1.15,  # Visual quality critical
            CreatorType.INFLUENCER: 1.0,    # Balanced approach
            CreatorType.COMEDIAN: 1.08      # Timing and context important
        }
        
        multiplier = creator_multipliers.get(creator_type, 1.0)
        engagement_score = base_score * multiplier
        
        return min(1.0, engagement_score)
    
    async def generate_regularization_recommendations(
        self,
        creator_type: CreatorType,
        model_architecture: str,
        training_history: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Generate intelligent regularization recommendations.
        
        Args:
            creator_type: Type of creator
            model_architecture: Model architecture description
            training_history: Historical training metrics
            
        Returns:
            Regularization recommendations
        """
        logger.info(f"🎯 Generating regularization recommendations for {creator_type.value}")
        
        # Analyze training history
        if training_history:
            avg_overfitting = np.mean([
                self._calculate_overfitting_score(metrics) 
                for metrics in training_history
            ])
            avg_generalization_gap = np.mean([
                self._calculate_generalization_gap(metrics) 
                for metrics in training_history
            ])
        else:
            avg_overfitting = 0.1
            avg_generalization_gap = 0.05
        
        # Get creator-specific recommendations
        creator_params = self.creator_profiles.get(creator_type, {})
        
        recommendations = {
            "creator_type": creator_type.value,
            "model_architecture": model_architecture,
            "analysis": {
                "avg_overfitting_score": avg_overfitting,
                "avg_generalization_gap": avg_generalization_gap,
                "risk_level": "high" if avg_overfitting > 0.15 else "medium" if avg_overfitting > 0.08 else "low"
            },
            "recommended_regularization": {},
            "implementation_priority": [],
            "monitoring_alerts": []
        }
        
        # Generate specific recommendations
        if avg_overfitting > 0.15:  # High overfitting risk
            recommendations["recommended_regularization"].update({
                "dropout": creator_params.get("preferred_dropout", 0.4) * 1.2,
                "weight_decay": creator_params.get("weight_decay", 1e-3) * 2.0,
                "early_stopping": True,
                "gradient_clipping": creator_params.get("gradient_clip_norm", 1.0)
            })
            recommendations["implementation_priority"] = [
                "dropout", "weight_decay", "early_stopping"
            ]
        elif avg_overfitting < 0.05:  # Underfitting risk
            recommendations["recommended_regularization"].update({
                "dropout": creator_params.get("preferred_dropout", 0.3) * 0.8,
                "weight_decay": creator_params.get("weight_decay", 1e-4) * 0.5,
                "data_augmentation": True
            })
            recommendations["implementation_priority"] = [
                "reduce_dropout", "reduce_weight_decay", "data_augmentation"
            ]
        else:  # Balanced approach
            recommendations["recommended_regularization"].update({
                "dropout": creator_params.get("preferred_dropout", 0.3),
                "weight_decay": creator_params.get("weight_decay", 1e-4),
                "batch_norm": True,
                "mixup": creator_params.get("mixup_alpha", 0.2) if creator_type != CreatorType.COMEDIAN else None
            })
            recommendations["implementation_priority"] = [
                "maintain_current", "add_batch_norm"
            ]
        
        # Add creator-specific recommendations
        if creator_type == CreatorType.PHOTOGRAPHER:
            recommendations["recommended_regularization"]["cutmix"] = creator_params.get("cutmix_alpha", 1.0)
            recommendations["recommended_regularization"]["spectral_norm"] = True
        elif creator_type == CreatorType.BLOGGER:
            recommendations["recommended_regularization"]["label_smoothing"] = creator_params.get("label_smoothing", 0.1)
        elif creator_type == CreatorType.COMEDIAN:
            recommendations["recommended_regularization"]["label_smoothing"] = creator_params.get("label_smoothing", 0.15)
        
        # Add monitoring alerts
        recommendations["monitoring_alerts"] = [
            f"Monitor overfitting score (current: {avg_overfitting:.3f})",
            f"Track generalization gap (current: {avg_generalization_gap:.3f})",
            "Set up early stopping alerts",
            "Monitor creator engagement metrics"
        ]
        
        logger.info(f"✅ Regularization recommendations generated for {creator_type.value}")
        return recommendations
    
    async def export_regularization_report(self) -> Dict[str, Any]:
        """Export comprehensive regularization analysis report."""
        logger.info("📊 Exporting regularization analysis report")
        
        report = {
            "summary": {
                "total_models_regularized": len(self.active_regularizers),
                "average_effectiveness": np.mean([
                    m.regularization_impact for m in self.performance_history
                ]) if self.performance_history else 0.0,
                "best_performing_creator_type": self._get_best_performing_creator_type(),
                "report_timestamp": datetime.now().isoformat()
            },
            "configurations": {
                reg_type.value: {
                    "strength": config.strength,
                    "adaptive": config.adaptive,
                    "creator_specific": config.creator_specific
                }
                for reg_type, config in self.regularization_configs.items()
            },
            "creator_profiles": {
                creator.value: params 
                for creator, params in self.creator_profiles.items()
            },
            "performance_history": [
                {
                    "training_loss": m.training_loss,
                    "validation_loss": m.validation_loss,
                    "overfitting_score": m.overfitting_score,
                    "regularization_impact": m.regularization_impact,
                    "creator_engagement_score": m.creator_engagement_score,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in self.performance_history[-50:]  # Last 50 entries
            ],
            "recommendations": await self._generate_global_recommendations()
        }
        
        logger.info("✅ Regularization report exported successfully")
        return report
    
    def _get_best_performing_creator_type(self) -> str:
        """Identify the best performing creator type."""
        if not self.performance_history:
            return "unknown"
        
        # This is a simplified implementation
        # In practice, would analyze by creator type
        avg_engagement = np.mean([m.creator_engagement_score for m in self.performance_history])
        
        if avg_engagement > 0.9:
            return "photographer"  # Visual content tends to have high engagement
        elif avg_engagement > 0.8:
            return "musician"     # Audio content
        else:
            return "blogger"      # Text content
    
    async def _generate_global_recommendations(self) -> List[str]:
        """Generate global regularization recommendations."""
        recommendations = [
            "Implement adaptive regularization tuning for all models",
            "Use creator-specific regularization profiles",
            "Monitor overfitting scores continuously",
            "Set up automated alerts for performance degradation",
            "Regular review of regularization effectiveness"
        ]
        
        if self.performance_history:
            avg_impact = np.mean([m.regularization_impact for m in self.performance_history])
            if avg_impact < 0.7:
                recommendations.append("Consider stronger regularization techniques")
            elif avg_impact > 0.95:
                recommendations.append("Regularization may be too aggressive - consider reduction")
        
        return recommendations

# Export main class
__all__ = ['RegularizationManager', 'RegularizationType', 'CreatorType', 'RegularizationConfig', 'RegularizationMetrics']

if __name__ == "__main__":
    # Test the regularization manager
    async def test_regularization_manager() -> None:
        manager = RegularizationManager()
        
        # Create a simple test model
        model = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 10)
        )
        
        # Test regularization application
        regularized_model = await manager.apply_regularization(
            model=model,
            creator_type=CreatorType.MUSICIAN,
            regularization_types=[
                RegularizationType.DROPOUT,
                RegularizationType.BATCH_NORM,
                RegularizationType.WEIGHT_DECAY
            ]
        )
        
        # Test adaptive tuning
        test_metrics = {
            "train_loss": 0.1,
            "val_loss": 0.3,
            "train_accuracy": 0.95,
            "val_accuracy": 0.85
        }
        
        updated_strengths = await manager.adaptive_regularization_tuning(
            model=regularized_model,
            training_metrics=test_metrics,
            creator_type=CreatorType.MUSICIAN
        )
        
        print(f"Updated regularization strengths: {updated_strengths}")
        
        # Test monitoring
        effectiveness_metrics = await manager.monitor_regularization_effectiveness(
            model=regularized_model,
            training_metrics=test_metrics,
            creator_type=CreatorType.MUSICIAN
        )
        
        print(f"Regularization effectiveness: {effectiveness_metrics.regularization_impact:.3f}")
        
        # Test recommendations
        recommendations = await manager.generate_regularization_recommendations(
            creator_type=CreatorType.PHOTOGRAPHER,
            model_architecture="CNN",
            training_history=[test_metrics]
        )
        
        print(f"Recommendations: {json.dumps(recommendations, indent=2)}")
        
        print("✅ RegularizationManager test completed successfully!")
    
    # Run test
    asyncio.run(test_regularization_manager())