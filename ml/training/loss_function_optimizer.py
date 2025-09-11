"""Loss Function Optimizer for Ainflue ML Platform

Custom loss functions optimized for creator-specific objectives and content quality
with advanced optimization techniques for multi-modal content analysis.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
import math
from abc import ABC, abstractmethod
from enum import Enum

logger = logging.getLogger(__name__)


class CreatorType(Enum):
    """Creator type enumeration."""
    MUSICIAN = "musician"
    PHOTOGRAPHER = "photographer"
    BLOGGER = "blogger"
    INFLUENCER = "influencer"
    GENERAL = "general"


class ContentType(Enum):
    """Content type enumeration."""
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"
    MULTIMODAL = "multimodal"


@dataclass
class LossConfig:
    """Configuration for loss function optimization."""
    # Basic loss weights
    primary_loss_weight: float = 1.0
    auxiliary_loss_weight: float = 0.3
    regularization_weight: float = 0.01
    
    # Creator-specific weights
    engagement_weight: float = 0.5
    quality_weight: float = 0.7
    authenticity_weight: float = 0.4
    virality_weight: float = 0.3
    
    # Content-specific weights
    aesthetic_weight: float = 0.6  # For visual content
    audio_quality_weight: float = 0.8  # For audio content
    readability_weight: float = 0.5  # For text content
    temporal_coherence_weight: float = 0.4  # For video content
    
    # Advanced loss components
    contrastive_learning: bool = True
    focal_loss_gamma: float = 2.0
    label_smoothing: float = 0.1
    confidence_penalty: float = 0.1
    
    # Adaptive weighting
    dynamic_weighting: bool = True
    weight_adaptation_rate: float = 0.01
    performance_threshold: float = 0.8


@dataclass
class CreatorObjectives:
    """Creator-specific objectives and constraints."""
    creator_type: CreatorType
    content_type: ContentType
    primary_goal: str  # engagement, quality, reach, monetization
    target_audience: str  # demographics
    brand_consistency: float = 0.8
    growth_priority: float = 0.6
    monetization_focus: float = 0.4
    creative_freedom: float = 0.7


class BaseLossFunction(ABC):
    """Abstract base class for custom loss functions."""
    
    def __init__(self, config: LossConfig):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
    @abstractmethod
    async def compute_loss(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        **kwargs
    ) -> torch.Tensor:
        """Compute the loss value."""
        pass
    
    @abstractmethod
    def get_loss_components(self) -> Dict[str, float]:
        """Get breakdown of loss components."""
        pass


class FocalLoss(BaseLossFunction):
    """Focal Loss for handling class imbalance in creator content."""
    
    def __init__(self, config: LossConfig, alpha: float = 1.0, gamma: float = 2.0):
        super().__init__(config)
        self.alpha = alpha
        self.gamma = gamma
    
    async def compute_loss(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor,
        **kwargs
    ) -> torch.Tensor:
        """Compute focal loss."""
        ce_loss = F.cross_entropy(predictions, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        
        return focal_loss.mean()
    
    def get_loss_components(self) -> Dict[str, float]:
        """Get focal loss components."""
        return {
            'focal_loss': 1.0,
            'alpha': self.alpha,
            'gamma': self.gamma
        }


class ContrastiveLoss(BaseLossFunction):
    """Contrastive loss for learning creator-specific representations."""
    
    def __init__(self, config: LossConfig, margin: float = 1.0, temperature: float = 0.07):
        super().__init__(config)
        self.margin = margin
        self.temperature = temperature
    
    async def compute_loss(
        self,
        anchor: torch.Tensor,
        positive: torch.Tensor,
        negative: torch.Tensor,
        **kwargs
    ) -> torch.Tensor:
        """Compute contrastive loss."""
        # Normalize embeddings
        anchor = F.normalize(anchor, dim=1)
        positive = F.normalize(positive, dim=1)
        negative = F.normalize(negative, dim=1)
        
        # Compute similarities
        pos_sim = torch.sum(anchor * positive, dim=1) / self.temperature
        neg_sim = torch.sum(anchor * negative, dim=1) / self.temperature
        
        # Contrastive loss
        loss = -torch.log(torch.exp(pos_sim) / (torch.exp(pos_sim) + torch.exp(neg_sim)))
        
        return loss.mean()
    
    def get_loss_components(self) -> Dict[str, float]:
        """Get contrastive loss components."""
        return {
            'contrastive_loss': 1.0,
            'margin': self.margin,
            'temperature': self.temperature
        }


class EngagementLoss(BaseLossFunction):
    """Loss function optimized for creator engagement metrics."""
    
    def __init__(self, config: LossConfig):
        super().__init__(config)
        self.engagement_factors = {
            'likes': 0.3,
            'comments': 0.4,
            'shares': 0.5,
            'saves': 0.6,
            'view_time': 0.7
        }
    
    async def compute_loss(
        self,
        predictions: torch.Tensor,
        engagement_targets: torch.Tensor,
        content_features: torch.Tensor,
        **kwargs
    ) -> torch.Tensor:
        """Compute engagement-optimized loss."""
        # Base prediction loss
        base_loss = F.mse_loss(predictions, engagement_targets)
        
        # Engagement-weighted loss
        engagement_weights = self._compute_engagement_weights(content_features)
        weighted_loss = base_loss * engagement_weights.mean()
        
        # Add virality bonus
        virality_bonus = self._compute_virality_bonus(predictions, engagement_targets)
        
        total_loss = weighted_loss - self.config.virality_weight * virality_bonus
        
        return total_loss
    
    def _compute_engagement_weights(self, content_features: torch.Tensor) -> torch.Tensor:
        """Compute engagement weights based on content features."""
        # Simple heuristic based on content complexity and appeal
        feature_variance = torch.var(content_features, dim=1)
        weights = torch.sigmoid(feature_variance)
        
        return weights
    
    def _compute_virality_bonus(
        self,
        predictions: torch.Tensor,
        targets: torch.Tensor
    ) -> torch.Tensor:
        """Compute virality potential bonus."""
        # Reward predictions that exceed engagement thresholds
        threshold = targets.mean() + targets.std()
        virality_mask = predictions > threshold
        
        bonus = torch.where(virality_mask, predictions - threshold, torch.zeros_like(predictions))
        
        return bonus.mean()
    
    def get_loss_components(self) -> Dict[str, float]:
        """Get engagement loss components."""
        return {
            'base_loss': 1.0,
            'engagement_weighting': self.config.engagement_weight,
            'virality_bonus': self.config.virality_weight,
            'engagement_factors': self.engagement_factors
        }


class QualityLoss(BaseLossFunction):
    """Loss function for content quality assessment."""
    
    def __init__(self, config: LossConfig, content_type: ContentType):
        super().__init__(config)
        self.content_type = content_type
        
    async def compute_loss(
        self,
        predictions: torch.Tensor,
        quality_targets: torch.Tensor,
        content_features: torch.Tensor,
        **kwargs
    ) -> torch.Tensor:
        """Compute quality-optimized loss."""
        # Base quality loss
        base_loss = F.smooth_l1_loss(predictions, quality_targets)
        
        # Content-type specific quality metrics
        if self.content_type == ContentType.IMAGE:
            aesthetic_loss = self._compute_aesthetic_loss(content_features)
            base_loss += self.config.aesthetic_weight * aesthetic_loss
        
        elif self.content_type == ContentType.AUDIO:
            audio_quality_loss = self._compute_audio_quality_loss(content_features)
            base_loss += self.config.audio_quality_weight * audio_quality_loss
        
        elif self.content_type == ContentType.TEXT:
            readability_loss = self._compute_readability_loss(content_features)
            base_loss += self.config.readability_weight * readability_loss
        
        elif self.content_type == ContentType.VIDEO:
            temporal_loss = self._compute_temporal_coherence_loss(content_features)
            base_loss += self.config.temporal_coherence_weight * temporal_loss
        
        return base_loss
    
    def _compute_aesthetic_loss(self, image_features: torch.Tensor) -> torch.Tensor:
        """Compute aesthetic quality loss for images."""
        # Rule of thirds, color harmony, contrast, etc.
        # Simplified implementation
        feature_std = torch.std(image_features, dim=1)
        aesthetic_score = torch.sigmoid(feature_std)
        aesthetic_loss = 1.0 - aesthetic_score
        
        return aesthetic_loss.mean()
    
    def _compute_audio_quality_loss(self, audio_features: torch.Tensor) -> torch.Tensor:
        """Compute audio quality loss."""
        # SNR, dynamic range, frequency balance
        # Simplified implementation
        dynamic_range = torch.max(audio_features, dim=1)[0] - torch.min(audio_features, dim=1)[0]
        quality_score = torch.sigmoid(dynamic_range)
        quality_loss = 1.0 - quality_score
        
        return quality_loss.mean()
    
    def _compute_readability_loss(self, text_features: torch.Tensor) -> torch.Tensor:
        """Compute text readability loss."""
        # Complexity, coherence, flow
        # Simplified implementation
        coherence_score = torch.mean(torch.abs(text_features), dim=1)
        readability_score = torch.sigmoid(coherence_score)
        readability_loss = 1.0 - readability_score
        
        return readability_loss.mean()
    
    def _compute_temporal_coherence_loss(self, video_features: torch.Tensor) -> torch.Tensor:
        """Compute temporal coherence loss for videos."""
        # Frame-to-frame consistency, motion smoothness
        # Simplified implementation
        if video_features.dim() > 2:
            frame_diff = torch.diff(video_features, dim=1)
            coherence_score = 1.0 / (1.0 + torch.mean(torch.abs(frame_diff), dim=(1, 2)))
            coherence_loss = 1.0 - coherence_score
            
            return coherence_loss.mean()
        
        return torch.tensor(0.0, device=self.device)
    
    def get_loss_components(self) -> Dict[str, float]:
        """Get quality loss components."""
        components = {
            'base_quality_loss': 1.0,
            'content_type': self.content_type.value
        }
        
        if self.content_type == ContentType.IMAGE:
            components['aesthetic_weight'] = self.config.aesthetic_weight
        elif self.content_type == ContentType.AUDIO:
            components['audio_quality_weight'] = self.config.audio_quality_weight
        elif self.content_type == ContentType.TEXT:
            components['readability_weight'] = self.config.readability_weight
        elif self.content_type == ContentType.VIDEO:
            components['temporal_coherence_weight'] = self.config.temporal_coherence_weight
        
        return components


class AuthenticityLoss(BaseLossFunction):
    """Loss function for maintaining creator authenticity."""
    
    def __init__(self, config: LossConfig, creator_style_embedding: torch.Tensor):
        super().__init__(config)
        self.creator_style_embedding = creator_style_embedding.to(self.device)
    
    async def compute_loss(
        self,
        content_embedding: torch.Tensor,
        style_consistency_target: torch.Tensor,
        **kwargs
    ) -> torch.Tensor:
        """Compute authenticity loss."""
        # Style consistency loss
        style_similarity = F.cosine_similarity(
            content_embedding,
            self.creator_style_embedding.expand_as(content_embedding),
            dim=1
        )
        
        style_loss = 1.0 - style_similarity
        
        # Authenticity regularization
        authenticity_reg = F.mse_loss(style_similarity, style_consistency_target)
        
        total_loss = style_loss.mean() + self.config.authenticity_weight * authenticity_reg
        
        return total_loss
    
    def get_loss_components(self) -> Dict[str, float]:
        """Get authenticity loss components."""
        return {
            'style_consistency_loss': 1.0,
            'authenticity_regularization': self.config.authenticity_weight
        }


class MultiModalLoss(BaseLossFunction):
    """Loss function for multi-modal content analysis."""
    
    def __init__(self, config: LossConfig):
        super().__init__(config)
        self.modality_weights = {
            'audio': 0.3,
            'visual': 0.4,
            'text': 0.3
        }
    
    async def compute_loss(
        self,
        audio_pred: torch.Tensor,
        visual_pred: torch.Tensor,
        text_pred: torch.Tensor,
        targets: torch.Tensor,
        **kwargs
    ) -> torch.Tensor:
        """Compute multi-modal loss."""
        # Individual modality losses
        audio_loss = F.mse_loss(audio_pred, targets) if audio_pred is not None else 0
        visual_loss = F.mse_loss(visual_pred, targets) if visual_pred is not None else 0
        text_loss = F.mse_loss(text_pred, targets) if text_pred is not None else 0
        
        # Weighted combination
        total_loss = (
            self.modality_weights['audio'] * audio_loss +
            self.modality_weights['visual'] * visual_loss +
            self.modality_weights['text'] * text_loss
        )
        
        # Cross-modal consistency loss
        if audio_pred is not None and visual_pred is not None:
            consistency_loss = F.mse_loss(audio_pred, visual_pred)
            total_loss += 0.1 * consistency_loss
        
        return total_loss
    
    def get_loss_components(self) -> Dict[str, float]:
        """Get multi-modal loss components."""
        return {
            'modality_weights': self.modality_weights,
            'cross_modal_consistency': 0.1
        }


class AdaptiveLossWeightOptimizer:
    """Optimizer for adaptive loss weight adjustment."""
    
    def __init__(self, config: LossConfig):
        self.config = config
        self.weight_history = []
        self.performance_history = []
        
    async def update_weights(
        self,
        current_weights: Dict[str, float],
        performance_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """Update loss weights based on performance."""
        if not self.config.dynamic_weighting:
            return current_weights
        
        # Store history
        self.weight_history.append(current_weights.copy())
        self.performance_history.append(performance_metrics.copy())
        
        # Adaptive weight adjustment
        updated_weights = current_weights.copy()
        
        for weight_name, current_weight in current_weights.items():
            if weight_name in performance_metrics:
                performance = performance_metrics[weight_name]
                
                # Increase weight if performance is below threshold
                if performance < self.config.performance_threshold:
                    weight_adjustment = self.config.weight_adaptation_rate
                else:
                    weight_adjustment = -self.config.weight_adaptation_rate * 0.5
                
                updated_weights[weight_name] = max(
                    0.1, min(2.0, current_weight + weight_adjustment)
                )
        
        return updated_weights
    
    def get_weight_trends(self) -> Dict[str, List[float]]:
        """Get weight adaptation trends."""
        if not self.weight_history:
            return {}
        
        trends = {}
        for weight_name in self.weight_history[0].keys():
            trends[weight_name] = [w[weight_name] for w in self.weight_history]
        
        return trends


class CreatorSpecificLossFunction(BaseLossFunction):
    """Comprehensive creator-specific loss function."""
    
    def __init__(
        self,
        config: LossConfig,
        creator_objectives: CreatorObjectives,
        creator_style_embedding: Optional[torch.Tensor] = None
    ):
        super().__init__(config)
        self.creator_objectives = creator_objectives
        
        # Initialize component loss functions
        self.focal_loss = FocalLoss(config, gamma=config.focal_loss_gamma)
        self.engagement_loss = EngagementLoss(config)
        self.quality_loss = QualityLoss(config, creator_objectives.content_type)
        
        if creator_style_embedding is not None:
            self.authenticity_loss = AuthenticityLoss(config, creator_style_embedding)
        else:
            self.authenticity_loss = None
        
        if creator_objectives.content_type == ContentType.MULTIMODAL:
            self.multimodal_loss = MultiModalLoss(config)
        else:
            self.multimodal_loss = None
        
        # Adaptive weight optimizer
        self.weight_optimizer = AdaptiveLossWeightOptimizer(config)
        
        # Current loss weights
        self.current_weights = self._initialize_weights()
        
    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize loss weights based on creator objectives."""
        weights = {
            'focal': self.config.primary_loss_weight,
            'engagement': self.config.engagement_weight,
            'quality': self.config.quality_weight,
            'authenticity': self.config.authenticity_weight,
            'regularization': self.config.regularization_weight
        }
        
        # Adjust weights based on creator priorities
        if self.creator_objectives.primary_goal == "engagement":
            weights['engagement'] *= 1.5
        elif self.creator_objectives.primary_goal == "quality":
            weights['quality'] *= 1.5
        elif self.creator_objectives.primary_goal == "reach":
            weights['focal'] *= 1.3
        elif self.creator_objectives.primary_goal == "monetization":
            weights['engagement'] *= 1.2
            weights['quality'] *= 1.2
        
        # Creator type adjustments
        if self.creator_objectives.creator_type == CreatorType.MUSICIAN:
            weights['quality'] *= 1.2  # Audio quality is crucial
        elif self.creator_objectives.creator_type == CreatorType.PHOTOGRAPHER:
            weights['quality'] *= 1.3  # Visual quality is paramount
        elif self.creator_objectives.creator_type == CreatorType.BLOGGER:
            weights['authenticity'] *= 1.2  # Authenticity matters for bloggers
        elif self.creator_objectives.creator_type == CreatorType.INFLUENCER:
            weights['engagement'] *= 1.3  # Engagement is key for influencers
        
        return weights
    
    async def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor],
        features: Dict[str, torch.Tensor],
        **kwargs
    ) -> torch.Tensor:
        """Compute comprehensive creator-specific loss."""
        total_loss = torch.tensor(0.0, device=self.device)
        loss_components = {}
        
        # Focal loss (primary classification/regression)
        if 'classification' in predictions and 'classification' in targets:
            focal_loss = await self.focal_loss.compute_loss(
                predictions['classification'],
                targets['classification']
            )
            total_loss += self.current_weights['focal'] * focal_loss
            loss_components['focal'] = focal_loss.item()
        
        # Engagement loss
        if 'engagement' in predictions and 'engagement' in targets:
            engagement_loss = await self.engagement_loss.compute_loss(
                predictions['engagement'],
                targets['engagement'],
                features.get('content', torch.empty(0, device=self.device))
            )
            total_loss += self.current_weights['engagement'] * engagement_loss
            loss_components['engagement'] = engagement_loss.item()
        
        # Quality loss
        if 'quality' in predictions and 'quality' in targets:
            quality_loss = await self.quality_loss.compute_loss(
                predictions['quality'],
                targets['quality'],
                features.get('content', torch.empty(0, device=self.device))
            )
            total_loss += self.current_weights['quality'] * quality_loss
            loss_components['quality'] = quality_loss.item()
        
        # Authenticity loss
        if (self.authenticity_loss and 
            'content_embedding' in features and 
            'style_consistency' in targets):
            auth_loss = await self.authenticity_loss.compute_loss(
                features['content_embedding'],
                targets['style_consistency']
            )
            total_loss += self.current_weights['authenticity'] * auth_loss
            loss_components['authenticity'] = auth_loss.item()
        
        # Multi-modal loss
        if self.multimodal_loss and self.creator_objectives.content_type == ContentType.MULTIMODAL:
            mm_loss = await self.multimodal_loss.compute_loss(
                predictions.get('audio'),
                predictions.get('visual'),
                predictions.get('text'),
                targets.get('multimodal', targets.get('classification'))
            )
            total_loss += 0.3 * mm_loss
            loss_components['multimodal'] = mm_loss.item()
        
        # Regularization
        reg_loss = self._compute_regularization(predictions)
        total_loss += self.current_weights['regularization'] * reg_loss
        loss_components['regularization'] = reg_loss.item()
        
        # Store loss components for analysis
        self.last_loss_components = loss_components
        
        return total_loss
    
    def _compute_regularization(self, predictions: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Compute regularization loss."""
        reg_loss = torch.tensor(0.0, device=self.device)
        
        for pred in predictions.values():
            if pred is not None:
                # L2 regularization on predictions
                reg_loss += torch.mean(pred ** 2)
        
        return reg_loss
    
    async def update_weights(self, performance_metrics: Dict[str, float]):
        """Update loss weights based on performance."""
        self.current_weights = await self.weight_optimizer.update_weights(
            self.current_weights,
            performance_metrics
        )
    
    def get_loss_components(self) -> Dict[str, float]:
        """Get breakdown of all loss components."""
        components = {
            'current_weights': self.current_weights,
            'creator_objectives': {
                'type': self.creator_objectives.creator_type.value,
                'content_type': self.creator_objectives.content_type.value,
                'primary_goal': self.creator_objectives.primary_goal
            }
        }
        
        if hasattr(self, 'last_loss_components'):
            components['last_computed_losses'] = self.last_loss_components
        
        return components
    
    def get_optimization_suggestions(self) -> Dict[str, str]:
        """Get suggestions for loss function optimization."""
        suggestions = {}
        
        if hasattr(self, 'last_loss_components'):
            losses = self.last_loss_components
            
            # Identify dominant loss components
            max_loss_component = max(losses, key=losses.get)
            suggestions['dominant_loss'] = f"Focus on optimizing {max_loss_component}"
            
            # Check balance
            loss_values = list(losses.values())
            if max(loss_values) / min(loss_values) > 10:
                suggestions['balance'] = "Consider rebalancing loss weights"
            
            # Creator-specific suggestions
            if self.creator_objectives.creator_type == CreatorType.MUSICIAN:
                if losses.get('quality', 0) > 0.5:
                    suggestions['music_quality'] = "Focus on audio quality improvements"
            
            elif self.creator_objectives.creator_type == CreatorType.PHOTOGRAPHER:
                if losses.get('quality', 0) > 0.5:
                    suggestions['photo_quality'] = "Focus on aesthetic and visual quality"
            
            elif self.creator_objectives.creator_type == CreatorType.INFLUENCER:
                if losses.get('engagement', 0) > 0.5:
                    suggestions['engagement'] = "Focus on engagement optimization strategies"
        
        return suggestions


class LossFunctionOptimizer:
    """Main optimizer for creator-specific loss functions."""
    
    def __init__(self):
        self.loss_functions: Dict[str, CreatorSpecificLossFunction] = {}
        self.performance_tracker = {}
        
    async def create_loss_function(
        self,
        creator_id: str,
        creator_objectives: CreatorObjectives,
        config: Optional[LossConfig] = None,
        creator_style_embedding: Optional[torch.Tensor] = None
    ) -> CreatorSpecificLossFunction:
        """Create customized loss function for creator."""
        if config is None:
            config = LossConfig()
        
        loss_function = CreatorSpecificLossFunction(
            config,
            creator_objectives,
            creator_style_embedding
        )
        
        self.loss_functions[creator_id] = loss_function
        self.performance_tracker[creator_id] = []
        
        logger.info(f"Created loss function for creator {creator_id} "
                   f"({creator_objectives.creator_type.value})")
        
        return loss_function
    
    async def optimize_for_creator(
        self,
        creator_id: str,
        performance_metrics: Dict[str, float]
    ):
        """Optimize loss function for specific creator."""
        if creator_id not in self.loss_functions:
            logger.warning(f"No loss function found for creator {creator_id}")
            return
        
        loss_function = self.loss_functions[creator_id]
        await loss_function.update_weights(performance_metrics)
        
        # Track performance
        self.performance_tracker[creator_id].append({
            'timestamp': datetime.now(),
            'metrics': performance_metrics,
            'weights': loss_function.current_weights.copy()
        })
        
        logger.info(f"Optimized loss function for creator {creator_id}")
    
    def get_creator_analytics(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive analytics for creator's loss function."""
        if creator_id not in self.loss_functions:
            return {}
        
        loss_function = self.loss_functions[creator_id]
        performance_history = self.performance_tracker.get(creator_id, [])
        
        analytics = {
            'creator_id': creator_id,
            'loss_components': loss_function.get_loss_components(),
            'optimization_suggestions': loss_function.get_optimization_suggestions(),
            'performance_history_length': len(performance_history),
            'weight_trends': loss_function.weight_optimizer.get_weight_trends()
        }
        
        if performance_history:
            recent_performance = performance_history[-1]['metrics']
            analytics['recent_performance'] = recent_performance
            
            # Calculate performance trends
            if len(performance_history) > 1:
                analytics['performance_trend'] = self._calculate_trend(performance_history)
        
        return analytics
    
    def _calculate_trend(self, history: List[Dict]) -> Dict[str, str]:
        """Calculate performance trends."""
        if len(history) < 2:
            return {}
        
        recent = history[-1]['metrics']
        previous = history[-2]['metrics']
        
        trends = {}
        for metric, value in recent.items():
            if metric in previous:
                change = value - previous[metric]
                if change > 0.05:
                    trends[metric] = "improving"
                elif change < -0.05:
                    trends[metric] = "declining"
                else:
                    trends[metric] = "stable"
        
        return trends
    
    def get_global_insights(self) -> Dict[str, Any]:
        """Get insights across all creators."""
        insights = {
            'total_creators': len(self.loss_functions),
            'creator_types': {},
            'average_performance': {},
            'best_practices': []
        }
        
        # Analyze by creator type
        for creator_id, loss_func in self.loss_functions.items():
            creator_type = loss_func.creator_objectives.creator_type.value
            insights['creator_types'][creator_type] = insights['creator_types'].get(creator_type, 0) + 1
        
        # Calculate average performance
        all_metrics = []
        for history in self.performance_tracker.values():
            if history:
                all_metrics.extend([h['metrics'] for h in history])
        
        if all_metrics:
            avg_metrics = {}
            for metric in all_metrics[0].keys():
                values = [m[metric] for m in all_metrics if metric in m]
                avg_metrics[metric] = np.mean(values)
            insights['average_performance'] = avg_metrics
        
        return insights


# Factory functions for easy instantiation
def create_loss_optimizer() -> LossFunctionOptimizer:
    """Factory function to create loss function optimizer."""
    return LossFunctionOptimizer()


def create_creator_objectives(
    creator_type: str,
    content_type: str,
    primary_goal: str = "engagement",
    **kwargs
) -> CreatorObjectives:
    """Factory function to create creator objectives."""
    return CreatorObjectives(
        creator_type=CreatorType(creator_type),
        content_type=ContentType(content_type),
        primary_goal=primary_goal,
        target_audience=kwargs.get('target_audience', 'general'),
        **{k: v for k, v in kwargs.items() if k != 'target_audience'}
    )


# Example usage for Ainflue creators
async def example_loss_optimization():
    """Example of loss function optimization for creators."""
    
    # Create loss optimizer
    optimizer = create_loss_optimizer()
    
    # Create objectives for different creators
    musician_objectives = create_creator_objectives(
        creator_type="musician",
        content_type="audio",
        primary_goal="quality",
        target_audience="music_lovers",
        brand_consistency=0.9,
        monetization_focus=0.6
    )
    
    photographer_objectives = create_creator_objectives(
        creator_type="photographer",
        content_type="image",
        primary_goal="engagement",
        target_audience="visual_arts",
        brand_consistency=0.8,
        creative_freedom=0.9
    )
    
    # Create loss functions
    musician_loss = await optimizer.create_loss_function(
        creator_id="musician_123",
        creator_objectives=musician_objectives
    )
    
    photographer_loss = await optimizer.create_loss_function(
        creator_id="photographer_456",
        creator_objectives=photographer_objectives
    )
    
    logger.info("Loss function optimizer ready with creator-specific optimizations")
    
    return optimizer


if __name__ == "__main__":
    # Run example
    asyncio.run(example_loss_optimization())