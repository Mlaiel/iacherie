"""
Recommendation Networks for IA-Influencer-Agent

Advanced recommendation systems for content creators, including collaboration
matching, audience targeting, and content optimization recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union, Any
import numpy as np
from dataclasses import dataclass
from enum import Enum
import math

from .base_networks import BaseNeuralNetwork, NetworkConfig


class RecommendationType(Enum):
    """Types of recommendations"""
    COLLABORATION = "collaboration"
    CONTENT_OPTIMIZATION = "content_optimization"
    AUDIENCE_TARGETING = "audience_targeting"
    TREND_ALIGNMENT = "trend_alignment"
    MONETIZATION = "monetization"
    CROSS_PROMOTION = "cross_promotion"


class CollaborationType(Enum):
    """Types of collaborations"""
    MUSICAL_COLLAB = "musical_collaboration"
    VIDEO_COLLAB = "video_collaboration"
    PODCAST_GUEST = "podcast_guest"
    CROSS_PROMOTION = "cross_promotion"
    REMIX_PERMISSION = "remix_permission"
    JOINT_PROJECT = "joint_project"
    MENTORSHIP = "mentorship"


@dataclass
class RecommendationResult:
    """Result of a recommendation query"""
    
    recommendation_type: RecommendationType
    score: float
    confidence: float
    
    # Collaboration specific
    target_creator_id: Optional[str] = None
    collaboration_type: Optional[CollaborationType] = None
    compatibility_score: Optional[float] = None
    
    # Content specific
    suggested_content_types: Optional[List[str]] = None
    optimization_suggestions: Optional[Dict[str, Any]] = None
    
    # Audience specific
    target_demographics: Optional[Dict[str, float]] = None
    engagement_prediction: Optional[float] = None
    
    # Monetization specific
    revenue_potential: Optional[float] = None
    pricing_suggestions: Optional[Dict[str, float]] = None
    
    # Supporting data
    explanation: Optional[str] = None
    alternative_options: Optional[List['RecommendationResult']] = None
    
    def __post_init__(self):
        """Ensure score and confidence are in valid ranges"""
        self.score = max(0.0, min(1.0, self.score))
        self.confidence = max(0.0, min(1.0, self.confidence))


class CollaborationRecommendationNetwork(BaseNeuralNetwork):
    """
    Network for recommending creator collaborations
    
    Matches creators based on complementary skills, audience overlap,
    and collaboration potential.
    """
    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Creator profile encoder
        self.creator_encoder = nn.Sequential(
            nn.Linear(config.input_dim, config.hidden_dims[0]),
            nn.ReLU(),
            nn.BatchNorm1d(config.hidden_dims[0]),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1])
        )
        
        # Content style encoder
        self.style_encoder = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2])
        )
        
        # Audience compatibility analyzer
        self.audience_analyzer = nn.Sequential(
            nn.Linear(config.hidden_dims[1] * 2, config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 1),
            nn.Sigmoid()
        )
        
        # Skill complementarity analyzer
        self.skill_analyzer = nn.MultiheadAttention(
            config.hidden_dims[1], 8, batch_first=True
        )
        
        # Collaboration type predictor
        self.collab_type_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[1] * 2, config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], len(CollaborationType)),
            nn.Softmax(dim=-1)
        )
        
        # Success probability predictor
        self.success_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[1] * 2 + len(CollaborationType), config.hidden_dims[2]),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[2], config.hidden_dims[2] // 2),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2] // 2, 1),
            nn.Sigmoid()
        )
        
        # Mutual benefit analyzer
        self.benefit_analyzer = nn.Sequential(
            nn.Linear(config.hidden_dims[1] * 2, config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 2)  # Benefit for each creator
        )
        
    def forward(
        self,
        creator1_features: torch.Tensor,
        creator2_features: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        
        # Encode creator profiles
        creator1_encoded = self.creator_encoder(creator1_features)
        creator2_encoded = self.creator_encoder(creator2_features)
        
        # Encode styles
        style1 = self.style_encoder(creator1_encoded)
        style2 = self.style_encoder(creator2_encoded)
        
        # Analyze audience compatibility
        combined_features = torch.cat([creator1_encoded, creator2_encoded], dim=-1)
        audience_compatibility = self.audience_analyzer(combined_features)
        
        # Analyze skill complementarity using attention
        stacked_creators = torch.stack([creator1_encoded, creator2_encoded], dim=1)
        skill_attention, _ = self.skill_analyzer(
            stacked_creators, stacked_creators, stacked_creators
        )
        skill_complementarity = skill_attention.mean(dim=1)
        
        # Predict collaboration type
        collab_type_probs = self.collab_type_predictor(combined_features)
        
        # Predict success probability
        success_input = torch.cat([combined_features, collab_type_probs], dim=-1)
        success_prob = self.success_predictor(success_input)
        
        # Analyze mutual benefits
        mutual_benefits = self.benefit_analyzer(combined_features)
        
        return {
            "audience_compatibility": audience_compatibility,
            "skill_complementarity": skill_complementarity.mean(dim=-1, keepdim=True),
            "collaboration_type": collab_type_probs,
            "success_probability": success_prob,
            "mutual_benefits": torch.softmax(mutual_benefits, dim=-1),
            "creator1_embedding": creator1_encoded,
            "creator2_embedding": creator2_encoded
        }
    
    def recommend_collaborations(
        self,
        creator_features: torch.Tensor,
        candidate_creators: torch.Tensor,
        top_k: int = 10
    ) -> List[RecommendationResult]:
        """
        Recommend top collaborations for a creator
        """
        
        self.eval()
        recommendations = []
        
        with torch.no_grad():
            for i, candidate_features in enumerate(candidate_creators):
                # Compute collaboration metrics
                outputs = self.forward(
                    creator_features.unsqueeze(0),
                    candidate_features.unsqueeze(0)
                )
                
                # Calculate overall compatibility score
                audience_score = outputs["audience_compatibility"].item()
                skill_score = outputs["skill_complementarity"].item()
                success_score = outputs["success_probability"].item()
                
                overall_score = (audience_score + skill_score + success_score) / 3.0
                
                # Get best collaboration type
                collab_probs = outputs["collaboration_type"][0]
                best_collab_idx = torch.argmax(collab_probs).item()
                best_collab_type = list(CollaborationType)[best_collab_idx]
                
                # Create recommendation
                recommendation = RecommendationResult(
                    recommendation_type=RecommendationType.COLLABORATION,
                    score=overall_score,
                    confidence=success_score,
                    target_creator_id=str(i),
                    collaboration_type=best_collab_type,
                    compatibility_score=audience_score
                )
                
                recommendations.append(recommendation)
        
        # Sort by score and return top k
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:top_k]
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        
        loss = 0.0
        
        if "audience_compatibility" in targets:
            loss += F.binary_cross_entropy(
                predictions["audience_compatibility"].squeeze(),
                targets["audience_compatibility"]
            )
        
        if "collaboration_success" in targets:
            loss += F.binary_cross_entropy(
                predictions["success_probability"].squeeze(),
                targets["collaboration_success"]
            )
        
        if "collaboration_type" in targets:
            loss += F.cross_entropy(
                predictions["collaboration_type"],
                targets["collaboration_type"]
            )
        
        return loss


class ContentRecommendationNetwork(BaseNeuralNetwork):
    """
    Network for recommending content optimization strategies
    
    Suggests content types, timing, and optimization strategies.
    """
    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Content history encoder
        self.history_encoder = nn.LSTM(
            config.input_dim,
            config.hidden_dims[0],
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )
        
        # Trend analyzer
        self.trend_analyzer = nn.Sequential(
            nn.Linear(config.hidden_dims[0] * 2, config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2])
        )
        
        # Content type recommender
        self.content_type_recommender = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 20),  # 20 content types
            nn.Softmax(dim=-1)
        )
        
        # Timing optimizer
        self.timing_optimizer = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 24)  # 24 hours
        )
        
        # Engagement predictor
        self.engagement_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
        # Performance optimizer
        self.performance_optimizer = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 10),  # 10 optimization aspects
            nn.Sigmoid()
        )
        
    def forward(
        self,
        content_history: torch.Tensor,
        current_trends: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        
        # Encode content history
        history_encoded, (hidden, _) = self.history_encoder(content_history)
        history_features = history_encoded[:, -1, :]  # Last timestep
        
        # Analyze trends
        trend_features = self.trend_analyzer(history_features)
        
        return {
            "content_type_recommendations": self.content_type_recommender(trend_features),
            "optimal_timing": torch.softmax(self.timing_optimizer(trend_features), dim=-1),
            "engagement_prediction": self.engagement_predictor(trend_features),
            "performance_optimizations": self.performance_optimizer(trend_features),
            "trend_features": trend_features
        }
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        
        loss = 0.0
        
        if "content_type" in targets:
            loss += F.cross_entropy(
                predictions["content_type_recommendations"],
                targets["content_type"]
            )
        
        if "optimal_timing" in targets:
            loss += F.cross_entropy(
                predictions["optimal_timing"],
                targets["optimal_timing"]
            )
        
        if "engagement" in targets:
            loss += F.mse_loss(
                predictions["engagement_prediction"].squeeze(),
                targets["engagement"]
            )
        
        return loss


class AudienceTargetingNetwork(BaseNeuralNetwork):
    """
    Network for audience analysis and targeting recommendations
    
    Analyzes audience demographics and suggests targeting strategies.
    """
    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Audience profile encoder
        self.audience_encoder = nn.Sequential(
            nn.Linear(config.input_dim, config.hidden_dims[0]),
            nn.ReLU(),
            nn.BatchNorm1d(config.hidden_dims[0]),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1])
        )
        
        # Demographics analyzer
        self.demographics_analyzer = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 50)  # 50 demographic segments
        )
        
        # Interest profiler
        self.interest_profiler = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 100),  # 100 interest categories
            nn.Sigmoid()
        )
        
        # Behavior predictor
        self.behavior_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 20),  # 20 behavior patterns
            nn.Softmax(dim=-1)
        )
        
        # Engagement optimizer
        self.engagement_optimizer = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
        # Growth predictor
        self.growth_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 1),
            nn.Sigmoid()
        )
        
    def forward(self, audience_data: torch.Tensor) -> Dict[str, torch.Tensor]:
        
        # Encode audience profile
        audience_encoded = self.audience_encoder(audience_data)
        
        return {
            "demographics": torch.softmax(self.demographics_analyzer(audience_encoded), dim=-1),
            "interests": self.interest_profiler(audience_encoded),
            "behavior_patterns": self.behavior_predictor(audience_encoded),
            "engagement_potential": self.engagement_optimizer(audience_encoded),
            "growth_potential": self.growth_predictor(audience_encoded),
            "audience_embedding": audience_encoded
        }
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        
        loss = 0.0
        
        if "demographics" in targets:
            loss += F.cross_entropy(predictions["demographics"], targets["demographics"])
        
        if "interests" in targets:
            loss += F.binary_cross_entropy(predictions["interests"], targets["interests"])
        
        if "behavior_patterns" in targets:
            loss += F.cross_entropy(predictions["behavior_patterns"], targets["behavior_patterns"])
        
        if "engagement" in targets:
            loss += F.mse_loss(
                predictions["engagement_potential"].squeeze(),
                targets["engagement"]
            )
        
        return loss


class TrendPredictionNetwork(BaseNeuralNetwork):
    """
    Network for predicting trends and viral potential
    
    Analyzes current trends and predicts future content opportunities.
    """
    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Trend history encoder
        self.trend_encoder = nn.LSTM(
            config.input_dim,
            config.hidden_dims[0],
            num_layers=3,
            batch_first=True,
            bidirectional=True
        )
        
        # Seasonal pattern analyzer
        self.seasonal_analyzer = nn.Sequential(
            nn.Linear(config.hidden_dims[0] * 2, config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 12)  # 12 months
        )
        
        # Viral potential predictor
        self.viral_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[0] * 2, config.hidden_dims[1]),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 1),
            nn.Sigmoid()
        )
        
        # Trend category classifier
        self.trend_classifier = nn.Sequential(
            nn.Linear(config.hidden_dims[0] * 2, config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 30),  # 30 trend categories
            nn.Softmax(dim=-1)
        )
        
        # Duration predictor
        self.duration_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[0] * 2, config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.ReLU()  # Positive duration
        )
        
        # Geographic spread predictor
        self.geographic_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[0] * 2, config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 50),  # 50 regions
            nn.Sigmoid()
        )
        
    def forward(self, trend_history: torch.Tensor) -> Dict[str, torch.Tensor]:
        
        # Encode trend history
        trend_encoded, (hidden, _) = self.trend_encoder(trend_history)
        trend_features = trend_encoded[:, -1, :]  # Use last timestep
        
        return {
            "seasonal_patterns": torch.softmax(self.seasonal_analyzer(trend_features), dim=-1),
            "viral_potential": self.viral_predictor(trend_features),
            "trend_category": self.trend_classifier(trend_features),
            "predicted_duration": self.duration_predictor(trend_features),
            "geographic_spread": self.geographic_predictor(trend_features),
            "trend_embedding": trend_features
        }
    
    def predict_trends(
        self,
        historical_data: torch.Tensor,
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """
        Predict future trends for the specified number of days
        """
        
        self.eval()
        
        with torch.no_grad():
            # Get current trend state
            outputs = self.forward(historical_data)
            
            # Generate predictions
            predictions = {
                "viral_potential": outputs["viral_potential"].cpu().numpy(),
                "trend_categories": outputs["trend_category"].cpu().numpy(),
                "seasonal_influence": outputs["seasonal_patterns"].cpu().numpy(),
                "predicted_duration": outputs["predicted_duration"].cpu().numpy(),
                "geographic_potential": outputs["geographic_spread"].cpu().numpy()
            }
            
            # Add confidence scores
            predictions["confidence"] = float(torch.mean(outputs["viral_potential"]).item())
            
        return predictions
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        
        loss = 0.0
        
        if "viral_potential" in targets:
            loss += F.binary_cross_entropy(
                predictions["viral_potential"].squeeze(),
                targets["viral_potential"]
            )
        
        if "trend_category" in targets:
            loss += F.cross_entropy(predictions["trend_category"], targets["trend_category"])
        
        if "duration" in targets:
            loss += F.mse_loss(
                predictions["predicted_duration"].squeeze(),
                targets["duration"]
            )
        
        if "geographic_spread" in targets:
            loss += F.binary_cross_entropy(
                predictions["geographic_spread"],
                targets["geographic_spread"]
            )
        
        return loss
