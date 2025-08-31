"""Optimization Networks for IA-Influencer-Agent

Advanced neural networks for optimizing content performance, SEO,
monetization strategies, and overall creator success.

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

from .base_networks import BaseNeuralNetwork, NetworkConfig


class OptimizationType(Enum):
    """Types of optimization"""    SEO = "seo"
    MONETIZATION = "monetization"
    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"
    AUDIENCE_GROWTH = "audience_growth"
    CONTENT_STRATEGY = "content_strategy"


class Platform(Enum):
    """Content platforms"""    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    SPOTIFY = "spotify"
    SOUNDCLOUD = "soundcloud"
    TWITCH = "twitch"
    FACEBOOK = "facebook"


@dataclass
class OptimizationResult:
    """Result of optimization analysis"""    
    optimization_type: OptimizationType
    current_score: float
    optimized_score: float
    improvement_potential: float
    
    # SEO specific
    keywords: Optional[List[str]] = None
    seo_score: Optional[float] = None
    title_suggestions: Optional[List[str]] = None
    description_suggestions: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    
    # Monetization specific
    revenue_potential: Optional[float] = None
    pricing_strategy: Optional[Dict[str, float]] = None
    monetization_channels: Optional[List[str]] = None
    
    # Engagement specific
    engagement_score: Optional[float] = None
    optimal_posting_times: Optional[List[str]] = None
    content_adjustments: Optional[Dict[str, Any]] = None
    
    # Performance specific
    performance_metrics: Optional[Dict[str, float]] = None
    bottlenecks: Optional[List[str]] = None
    optimization_suggestions: Optional[List[str]] = None
    
    # Confidence and metadata
    confidence: float = 0.0
    platform_specific: Optional[Dict[Platform, Any]] = None


class SEOOptimizationNetwork(BaseNeuralNetwork):
    """    Network for Search Engine Optimization of content
    
    Optimizes titles, descriptions, tags, and content structure
    for maximum discoverability across platforms.
    """    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Content analyzer
        self.content_analyzer = nn.Sequential(
            nn.Linear(config.input_dim, config.hidden_dims[0]),
            nn.ReLU(),
            nn.BatchNorm1d(config.hidden_dims[0]),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1])
        )
        
        # Keyword extractor
        self.keyword_extractor = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 1000),  # Top 1000 keywords
            nn.Sigmoid()
        )
        
        # Title optimizer
        self.title_optimizer = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], config.output_dim)
        )
        
        # Description generator
        self.description_generator = nn.LSTM(
            config.hidden_dims[1],
            config.hidden_dims[0],
            num_layers=2,
            batch_first=True
        )
        
        # Tag recommender
        self.tag_recommender = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 500),  # 500 possible tags
            nn.Sigmoid()
        )
        
        # SEO score predictor
        self.seo_scorer = nn.Sequential(
            nn.Linear(config.hidden_dims[1] + 1000 + 500, config.hidden_dims[0]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
        # Platform-specific optimizers
        self.platform_optimizers = nn.ModuleDict({
            "youtube": nn.Linear(config.hidden_dims[1], config.hidden_dims[1]),
            "instagram": nn.Linear(config.hidden_dims[1], config.hidden_dims[1]),
            "tiktok": nn.Linear(config.hidden_dims[1], config.hidden_dims[1]),
            "twitter": nn.Linear(config.hidden_dims[1], config.hidden_dims[1]),
            "spotify": nn.Linear(config.hidden_dims[1], config.hidden_dims[1])
        })
        
    def forward(
        self,
        content_features: torch.Tensor,
        platform: str = "youtube"
    ) -> Dict[str, torch.Tensor]:
        
        # Analyze content
        analyzed_content = self.content_analyzer(content_features)
        
        # Apply platform-specific optimization
        if platform in self.platform_optimizers:
            platform_optimized = self.platform_optimizers[platform](analyzed_content)
        else:
            platform_optimized = analyzed_content
        
        # Extract keywords
        keywords = self.keyword_extractor(platform_optimized)
        
        # Optimize title
        title_features = self.title_optimizer(platform_optimized)
        
        # Generate description features
        description_input = platform_optimized.unsqueeze(1).repeat(1, 10, 1)  # 10 words max
        description_features, _ = self.description_generator(description_input)
        
        # Recommend tags
        tags = self.tag_recommender(platform_optimized)
        
        # Calculate SEO score
        seo_input = torch.cat([platform_optimized, keywords, tags], dim=-1)
        seo_score = self.seo_scorer(seo_input)
        
        return {
            "keywords": keywords,
            "title_features": title_features,
            "description_features": description_features.mean(dim=1),
            "tags": tags,
            "seo_score": seo_score,
            "optimized_content": platform_optimized
        }
    
    def optimize_seo(
        self,
        content_features: torch.Tensor,
        platform: Platform = Platform.YOUTUBE,
        current_metadata: Optional[Dict[str, str]] = None
    ) -> OptimizationResult:
        """Perform comprehensive SEO optimization"""        
        self.eval()
        
        with torch.no_grad():
            # Get optimization outputs
            outputs = self.forward(content_features, platform.value)
            
            # Extract top keywords
            keyword_scores = outputs["keywords"].cpu().numpy()[0]
            top_keyword_indices = np.argsort(keyword_scores)[-20:]  # Top 20
            
            # Extract top tags
            tag_scores = outputs["tags"].cpu().numpy()[0]
            top_tag_indices = np.argsort(tag_scores)[-10:]  # Top 10
            
            # Calculate current vs optimized score
            # Extract basic metrics from content features for baseline calculation
            feature_magnitude = torch.norm(content_features, dim=-1).mean().item()
            content_complexity = torch.std(content_features, dim=-1).mean().item()
            
            # Estimate current SEO score based on content characteristics
            current_score = min(0.9, max(0.1, (feature_magnitude * 0.3 + content_complexity * 0.2 + 0.3)))
            optimized_score = outputs["seo_score"].item()
            
            # Create result
            result = OptimizationResult(
                optimization_type=OptimizationType.SEO,
                current_score=current_score,
                optimized_score=optimized_score,
                improvement_potential=optimized_score - current_score,
                keywords=[f"keyword_{i}" for i in top_keyword_indices],  # Would map to actual keywords
                seo_score=optimized_score,
                tags=[f"tag_{i}" for i in top_tag_indices],  # Would map to actual tags
                confidence=optimized_score
            )
            
            return result
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        
        loss = 0.0
        
        if "seo_score" in targets:
            loss += F.mse_loss(predictions["seo_score"].squeeze(), targets["seo_score"])
        
        if "keywords" in targets:
            loss += F.binary_cross_entropy(predictions["keywords"], targets["keywords"])
        
        if "tags" in targets:
            loss += F.binary_cross_entropy(predictions["tags"], targets["tags"])
        
        return loss


class MonetizationOptimizationNetwork(BaseNeuralNetwork):
    """    Network for optimizing monetization strategies
    
    Analyzes content and audience to recommend optimal pricing,
    revenue channels, and monetization approaches.
    """    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Content value assessor
        self.value_assessor = nn.Sequential(
            nn.Linear(config.input_dim, config.hidden_dims[0]),
            nn.ReLU(),
            nn.BatchNorm1d(config.hidden_dims[0]),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2])
        )
        
        # Audience purchasing power analyzer
        self.audience_analyzer = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 1),
            nn.Sigmoid()
        )
        
        # Pricing strategy optimizer
        self.pricing_optimizer = nn.Sequential(
            nn.Linear(config.hidden_dims[2] + 1, config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 5)  # 5 pricing tiers
        )
        
        # Revenue channel recommender
        self.revenue_recommender = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 15),  # 15 revenue channels
            nn.Sigmoid()
        )
        
        # Revenue predictor
        self.revenue_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[2] + 5 + 15, config.hidden_dims[1]),
            nn.ReLU(),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 1),
            nn.ReLU()  # Positive revenue
        )
        
        # Market timing analyzer
        self.timing_analyzer = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 12),  # 12 months
            nn.Softmax(dim=-1)
        )
        
        # Competition analyzer
        self.competition_analyzer = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
    def forward(
        self,
        content_features: torch.Tensor,
        audience_features: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        
        # Assess content value
        content_value = self.value_assessor(content_features)
        
        # Analyze audience if provided
        if audience_features is not None:
            # Combine content and audience features
            combined_features = content_value + audience_features
        else:
            combined_features = content_value
        
        # Analyze audience purchasing power
        purchasing_power = self.audience_analyzer(combined_features)
        
        # Optimize pricing strategy
        pricing_input = torch.cat([combined_features, purchasing_power], dim=-1)
        pricing_strategy = self.pricing_optimizer(pricing_input)
        
        # Recommend revenue channels
        revenue_channels = self.revenue_recommender(combined_features)
        
        # Predict revenue
        revenue_input = torch.cat([combined_features, pricing_strategy, revenue_channels], dim=-1)
        predicted_revenue = self.revenue_predictor(revenue_input)
        
        # Analyze market timing
        optimal_timing = self.timing_analyzer(combined_features)
        
        # Analyze competition
        competition_level = self.competition_analyzer(combined_features)
        
        return {
            "content_value": combined_features,
            "purchasing_power": purchasing_power,
            "pricing_strategy": pricing_strategy,
            "revenue_channels": revenue_channels,
            "predicted_revenue": predicted_revenue,
            "optimal_timing": optimal_timing,
            "competition_level": competition_level
        }
    
    def optimize_monetization(
        self,
        content_features: torch.Tensor,
        audience_features: Optional[torch.Tensor] = None,
        current_revenue: float = 0.0
    ) -> OptimizationResult:
        """Optimize monetization strategy"""        
        self.eval()
        
        with torch.no_grad():
            # Get optimization outputs
            outputs = self.forward(content_features, audience_features)
            
            # Extract pricing recommendations
            pricing_probs = F.softmax(outputs["pricing_strategy"], dim=-1).cpu().numpy()[0]
            pricing_tiers = ["free", "low", "medium", "high", "premium"]
            recommended_tier = pricing_tiers[np.argmax(pricing_probs)]
            
            # Extract revenue channels
            channel_scores = outputs["revenue_channels"].cpu().numpy()[0]
            revenue_channels = ["ads", "subscriptions", "merchandise", "sponsorships", 
                             "donations", "courses", "consulting", "licensing", "affiliate",
                             "live_events", "nft", "patreon", "youtube_premium", "brand_deals", "merchandise"]
            top_channels = [revenue_channels[i] for i in np.argsort(channel_scores)[-5:]]
            
            # Calculate revenue potential
            predicted_revenue = outputs["predicted_revenue"].item()
            
            # Create result
            result = OptimizationResult(
                optimization_type=OptimizationType.MONETIZATION,
                current_score=current_revenue,
                optimized_score=predicted_revenue,
                improvement_potential=predicted_revenue - current_revenue,
                revenue_potential=predicted_revenue,
                pricing_strategy={recommended_tier: float(np.max(pricing_probs))},
                monetization_channels=top_channels,
                confidence=outputs["purchasing_power"].item()
            )
            
            return result
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        
        loss = 0.0
        
        if "revenue" in targets:
            loss += F.mse_loss(predictions["predicted_revenue"].squeeze(), targets["revenue"])
        
        if "pricing_tier" in targets:
            loss += F.cross_entropy(predictions["pricing_strategy"], targets["pricing_tier"])
        
        if "channels" in targets:
            loss += F.binary_cross_entropy(predictions["revenue_channels"], targets["channels"])
        
        return loss


class EngagementOptimizationNetwork(BaseNeuralNetwork):
    """    Network for optimizing content engagement
    
    Analyzes and optimizes content for maximum audience engagement
    across different platforms and demographics.
    """    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Content engagement analyzer
        self.engagement_analyzer = nn.Sequential(
            nn.Linear(config.input_dim, config.hidden_dims[0]),
            nn.ReLU(),
            nn.BatchNorm1d(config.hidden_dims[0]),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[0], config.hidden_dims[1])
        )
        
        # Emotional impact predictor
        self.emotion_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 7),  # 7 basic emotions
            nn.Softmax(dim=-1)
        )
        
        # Virality potential analyzer
        self.virality_analyzer = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
        # Optimal timing predictor
        self.timing_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 24 * 7)  # 24 hours × 7 days
        )
        
        # Engagement metrics predictor
        self.metrics_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 5)  # likes, shares, comments, saves, clicks
        )
        
        # Content adjustment recommender
        self.adjustment_recommender = nn.Sequential(
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[2], 20),  # 20 adjustment types
            nn.Sigmoid()
        )
        
        # Platform-specific engagement optimizers
        self.platform_engagement = nn.ModuleDict({
            "youtube": nn.Sequential(
                nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
                nn.ReLU(),
                nn.Linear(config.hidden_dims[2], config.hidden_dims[1])
            ),
            "instagram": nn.Sequential(
                nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
                nn.ReLU(),
                nn.Linear(config.hidden_dims[2], config.hidden_dims[1])
            ),
            "tiktok": nn.Sequential(
                nn.Linear(config.hidden_dims[1], config.hidden_dims[2]),
                nn.ReLU(),
                nn.Linear(config.hidden_dims[2], config.hidden_dims[1])
            )
        })
        
    def forward(
        self,
        content_features: torch.Tensor,
        platform: str = "youtube"
    ) -> Dict[str, torch.Tensor]:
        
        # Analyze engagement potential
        engagement_features = self.engagement_analyzer(content_features)
        
        # Apply platform-specific optimization
        if platform in self.platform_engagement:
            platform_features = self.platform_engagement[platform](engagement_features)
        else:
            platform_features = engagement_features
        
        # Predict emotional impact
        emotions = self.emotion_predictor(platform_features)
        
        # Analyze virality potential
        virality = self.virality_analyzer(platform_features)
        
        # Predict optimal timing
        timing = self.timing_predictor(platform_features)
        optimal_times = torch.softmax(timing, dim=-1)
        
        # Predict engagement metrics
        metrics = self.metrics_predictor(platform_features)
        
        # Recommend content adjustments
        adjustments = self.adjustment_recommender(platform_features)
        
        return {
            "engagement_features": platform_features,
            "emotional_impact": emotions,
            "virality_potential": virality,
            "optimal_timing": optimal_times,
            "predicted_metrics": metrics,
            "content_adjustments": adjustments
        }
    
    def optimize_engagement(
        self,
        content_features: torch.Tensor,
        platform: Platform = Platform.YOUTUBE,
        current_engagement: Dict[str, float] = None
    ) -> OptimizationResult:
        """Optimize content for maximum engagement"""        
        self.eval()
        
        with torch.no_grad():
            # Get optimization outputs
            outputs = self.forward(content_features, platform.value)
            
            # Extract optimal posting times
            timing_probs = outputs["optimal_timing"].cpu().numpy()[0]
            hours = list(range(24))
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            
            # Find top 3 time slots
            top_time_indices = np.argsort(timing_probs)[-3:]
            optimal_times = []
            for idx in top_time_indices:
                hour = idx % 24
                day_idx = idx // 24
                optimal_times.append(f"{days[day_idx]} {hour:02d}:00")
            
            # Extract content adjustments
            adjustment_scores = outputs["content_adjustments"].cpu().numpy()[0]
            adjustment_types = ["add_hook", "improve_thumbnail", "optimize_title", "add_music",
                              "improve_lighting", "add_captions", "shorter_intro", "call_to_action",
                              "better_pacing", "add_storytelling", "improve_audio", "add_effects",
                              "optimize_length", "add_chapters", "improve_ending", "add_polls",
                              "use_trending_sounds", "optimize_hashtags", "improve_description", "add_links"]
            
            top_adjustments = [adjustment_types[i] for i in np.argsort(adjustment_scores)[-5:]]
            
            # Calculate engagement score
            virality_score = outputs["virality_potential"].item()
            current_score = 0.5 if current_engagement is None else np.mean(list(current_engagement.values()))
            
            # Create result
            result = OptimizationResult(
                optimization_type=OptimizationType.ENGAGEMENT,
                current_score=current_score,
                optimized_score=virality_score,
                improvement_potential=virality_score - current_score,
                engagement_score=virality_score,
                optimal_posting_times=optimal_times,
                content_adjustments={"suggestions": top_adjustments},
                confidence=virality_score
            )
            
            return result
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        
        loss = 0.0
        
        if "engagement_metrics" in targets:
            loss += F.mse_loss(predictions["predicted_metrics"], targets["engagement_metrics"])
        
        if "virality" in targets:
            loss += F.binary_cross_entropy(
                predictions["virality_potential"].squeeze(),
                targets["virality"].float()
            )
        
        if "emotions" in targets:
            loss += F.cross_entropy(predictions["emotional_impact"], targets["emotions"])
        
        return loss


class PerformancePredictionNetwork(BaseNeuralNetwork):
    """    Network for predicting content performance
    
    Forecasts various performance metrics including views, engagement,
    revenue, and growth potential.
    """    
    def __init__(self, config: NetworkConfig):
        super().__init__(config)
        
        # Performance history encoder
        self.history_encoder = nn.LSTM(
            config.input_dim,
            config.hidden_dims[0],
            num_layers=2,
            batch_first=True,
            bidirectional=True
        )
        
        # Content feature analyzer
        self.content_analyzer = nn.Sequential(
            nn.Linear(config.hidden_dims[0] * 2, config.hidden_dims[1]),
            nn.ReLU(),
            nn.BatchNorm1d(config.hidden_dims[1]),
            nn.Dropout(config.dropout_rate),
            nn.Linear(config.hidden_dims[1], config.hidden_dims[2])
        )
        
        # Views predictor
        self.views_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.ReLU()  # Positive views
        )
        
        # Engagement rate predictor
        self.engagement_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
        # Revenue predictor
        self.revenue_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.ReLU()  # Positive revenue
        )
        
        # Growth trajectory predictor
        self.growth_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 30)  # 30-day trajectory
        )
        
        # Success probability predictor
        self.success_predictor = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 1),
            nn.Sigmoid()
        )
        
        # Bottleneck identifier
        self.bottleneck_identifier = nn.Sequential(
            nn.Linear(config.hidden_dims[2], config.hidden_dims[1]),
            nn.ReLU(),
            nn.Linear(config.hidden_dims[1], 15),  # 15 potential bottlenecks
            nn.Sigmoid()
        )
        
    def forward(
        self,
        performance_history: torch.Tensor,
        content_features: Optional[torch.Tensor] = None
    ) -> Dict[str, torch.Tensor]:
        
        # Encode performance history
        encoded_history, (hidden, _) = self.history_encoder(performance_history)
        history_features = encoded_history[:, -1, :]  # Last timestep
        
        # Analyze content if provided
        if content_features is not None:
            # Combine history and content features
            combined_features = self.content_analyzer(
                history_features + content_features[:, :history_features.size(-1)]
            )
        else:
            combined_features = self.content_analyzer(history_features)
        
        return {
            "predicted_views": self.views_predictor(combined_features),
            "predicted_engagement": self.engagement_predictor(combined_features),
            "predicted_revenue": self.revenue_predictor(combined_features),
            "growth_trajectory": self.growth_predictor(combined_features),
            "success_probability": self.success_predictor(combined_features),
            "bottlenecks": self.bottleneck_identifier(combined_features),
            "performance_features": combined_features
        }
    
    def predict_performance(
        self,
        performance_history: torch.Tensor,
        content_features: Optional[torch.Tensor] = None,
        time_horizon: int = 30
    ) -> OptimizationResult:
        """Predict content performance over specified time horizon"""        
        self.eval()
        
        with torch.no_grad():
            # Get predictions
            outputs = self.forward(performance_history, content_features)
            
            # Extract predictions
            predicted_views = outputs["predicted_views"].item()
            predicted_engagement = outputs["predicted_engagement"].item()
            predicted_revenue = outputs["predicted_revenue"].item()
            success_prob = outputs["success_probability"].item()
            
            # Identify bottlenecks
            bottleneck_scores = outputs["bottlenecks"].cpu().numpy()[0]
            bottleneck_types = ["low_reach", "poor_thumbnail", "weak_title", "bad_timing",
                              "audio_quality", "video_quality", "content_length", "no_hook",
                              "weak_cta", "poor_seo", "algorithm_penalty", "audience_mismatch",
                              "competition", "seasonal_decline", "platform_changes"]
            
            active_bottlenecks = [bottleneck_types[i] for i in range(len(bottleneck_scores)) 
                                if bottleneck_scores[i] > 0.6]
            
            # Performance metrics
            metrics = {
                "predicted_views": predicted_views,
                "predicted_engagement_rate": predicted_engagement,
                "predicted_revenue": predicted_revenue,
                "success_probability": success_prob
            }
            
            # Calculate current performance baseline from content features and historical patterns
            # Use content features to estimate baseline performance
            feature_quality = torch.sigmoid(content_features).mean().item()
            content_variance = torch.var(content_features, dim=-1).mean().item()
            
            # Estimate current performance score based on content characteristics
            current_score = min(0.9, max(0.1, feature_quality * 0.6 + (1.0 - min(content_variance, 1.0)) * 0.4))
            
            # Create result
            result = OptimizationResult(
                optimization_type=OptimizationType.PERFORMANCE,
                current_score=current_score,
                optimized_score=success_prob,
                improvement_potential=success_prob - current_score,
                performance_metrics=metrics,
                bottlenecks=active_bottlenecks,
                optimization_suggestions=self._generate_optimization_suggestions(active_bottlenecks),
                confidence=success_prob
            )
            
            return result
    
    def _generate_optimization_suggestions(self, bottlenecks: List[str]) -> List[str]:
        """Generate optimization suggestions based on identified bottlenecks"""        
        suggestions = []
        
        for bottleneck in bottlenecks:
            if bottleneck == "low_reach":
                suggestions.append("Improve SEO and use trending hashtags")
            elif bottleneck == "poor_thumbnail":
                suggestions.append("Create more compelling thumbnail with bright colors and clear text")
            elif bottleneck == "weak_title":
                suggestions.append("Use power words and emotional triggers in title")
            elif bottleneck == "bad_timing":
                suggestions.append("Post during optimal times for your audience")
            elif bottleneck == "audio_quality":
                suggestions.append("Improve audio recording and mixing quality")
            elif bottleneck == "video_quality":
                suggestions.append("Upgrade video resolution and stabilization")
            elif bottleneck == "content_length":
                suggestions.append("Optimize content length for platform and audience")
            elif bottleneck == "no_hook":
                suggestions.append("Add compelling hook in first 3-5 seconds")
            elif bottleneck == "weak_cta":
                suggestions.append("Include clear and compelling call-to-action")
            elif bottleneck == "poor_seo":
                suggestions.append("Optimize title, description, and tags for search")
        
        return suggestions if suggestions else ["Continue current strategy - performance looks good"]
    
    def compute_loss(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> torch.Tensor:
        
        loss = 0.0
        
        if "views" in targets:
            loss += F.mse_loss(
                torch.log1p(predictions["predicted_views"].squeeze()),
                torch.log1p(targets["views"])
            )
        
        if "engagement_rate" in targets:
            loss += F.mse_loss(
                predictions["predicted_engagement"].squeeze(),
                targets["engagement_rate"]
            )
        
        if "revenue" in targets:
            loss += F.mse_loss(
                torch.log1p(predictions["predicted_revenue"].squeeze()),
                torch.log1p(targets["revenue"])
            )
        
        if "success" in targets:
            loss += F.binary_cross_entropy(
                predictions["success_probability"].squeeze(),
                targets["success"].float()
            )
        
        return loss
