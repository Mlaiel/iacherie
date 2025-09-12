"""Viral Detection Workflow - Advanced Viral Content Detection for Ainflue Platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Ainflue Platform. All rights reserved.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)


class ViralityStage(Enum):
    """Stages of virality."""
    EMERGING = "emerging"
    TRENDING = "trending"
    VIRAL = "viral"
    PEAK_VIRAL = "peak_viral"
    DECLINING = "declining"


@dataclass
class ViralMetrics:
    """Viral detection metrics."""
    content_id: str
    timestamp: datetime
    virality_score: float
    growth_rate: float
    velocity: float  # engagement per minute
    reach_expansion: float
    social_mentions: int
    cross_platform_spread: int
    virality_stage: ViralityStage
    viral_triggers: List[str]


@dataclass
class ViralityScore:
    """Comprehensive virality scoring."""
    content_id: str
    overall_score: float
    viral_potential: float
    current_stage: ViralityStage
    viral_metrics: ViralMetrics
    predictions: Dict[str, Any]
    recommendations: List[str]


class ViralDetectionWorkflow:
    """Advanced viral content detection and analysis workflow."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize viral detection workflow."""
        self.config = config or {}
        self.viral_threshold = self.config.get('viral_threshold', 80.0)
        self.trending_threshold = self.config.get('trending_threshold', 60.0)

    async def detect_viral_content(
        self,
        content_id: str,
        timeframe_hours: int = 24
    ) -> ViralityScore:
        """Detect and analyze viral potential of content."""
        try:
            logger.info(f"Analyzing viral potential for content: {content_id}")
            
            # Collect viral metrics
            viral_metrics = await self._collect_viral_metrics(content_id, timeframe_hours)
            
            # Calculate overall virality score
            overall_score = self._calculate_virality_score(viral_metrics)
            
            # Determine virality stage
            stage = self._determine_virality_stage(overall_score, viral_metrics)
            
            # Calculate viral potential
            viral_potential = await self._calculate_viral_potential(content_id, viral_metrics)
            
            # Generate predictions
            predictions = await self._generate_viral_predictions(viral_metrics)
            
            # Generate recommendations
            recommendations = self._generate_viral_recommendations(viral_metrics, stage)
            
            score = ViralityScore(
                content_id=content_id,
                overall_score=overall_score,
                viral_potential=viral_potential,
                current_stage=stage,
                viral_metrics=viral_metrics,
                predictions=predictions,
                recommendations=recommendations
            )
            
            logger.info(f"Viral analysis completed for content: {content_id}")
            return score
            
        except Exception as e:
            logger.error(f"Error detecting viral content: {str(e)}")
            raise

    async def _collect_viral_metrics(self, content_id: str, timeframe_hours: int) -> ViralMetrics:
        """Collect metrics for viral detection."""
        import random
        
        # Mock viral metrics collection
        viral_triggers = random.sample([
            'celebrity_interaction', 'trending_hashtag', 'current_event',
            'emotional_content', 'humor', 'controversial_topic',
            'user_generated_content', 'challenge_participation'
        ], random.randint(1, 3))
        
        return ViralMetrics(
            content_id=content_id,
            timestamp=datetime.now(),
            virality_score=random.uniform(30, 95),
            growth_rate=random.uniform(-10, 200),  # percentage
            velocity=random.uniform(10, 1000),  # engagements per minute
            reach_expansion=random.uniform(1.0, 10.0),  # multiplier
            social_mentions=random.randint(0, 5000),
            cross_platform_spread=random.randint(1, 5),
            virality_stage=ViralityStage.EMERGING,  # Will be updated
            viral_triggers=viral_triggers
        )

    def _calculate_virality_score(self, metrics: ViralMetrics) -> float:
        """Calculate overall virality score."""
        score_components = {
            'growth_rate': min(metrics.growth_rate / 100 * 30, 30),  # Max 30 points
            'velocity': min(metrics.velocity / 100 * 25, 25),  # Max 25 points
            'reach_expansion': min(metrics.reach_expansion * 10, 20),  # Max 20 points
            'social_mentions': min(metrics.social_mentions / 100, 15),  # Max 15 points
            'cross_platform': metrics.cross_platform_spread * 2  # Max 10 points
        }
        
        return round(sum(score_components.values()), 2)

    def _determine_virality_stage(self, score: float, metrics: ViralMetrics) -> ViralityStage:
        """Determine current virality stage."""
        if score >= 85:
            return ViralityStage.PEAK_VIRAL
        elif score >= self.viral_threshold:
            return ViralityStage.VIRAL
        elif score >= self.trending_threshold:
            return ViralityStage.TRENDING
        elif metrics.growth_rate > 50:
            return ViralityStage.EMERGING
        else:
            return ViralityStage.DECLINING

    async def _calculate_viral_potential(self, content_id: str, metrics: ViralMetrics) -> float:
        """Calculate viral potential based on various factors."""
        import random
        
        # Mock calculation - in production, use ML models
        potential_factors = {
            'content_quality': random.uniform(0.6, 1.0),
            'timing': random.uniform(0.5, 1.0),
            'audience_alignment': random.uniform(0.7, 1.0),
            'platform_algorithm': random.uniform(0.6, 0.9),
            'creator_influence': random.uniform(0.5, 1.0)
        }
        
        base_potential = sum(potential_factors.values()) / len(potential_factors)
        
        # Adjust based on current metrics
        if metrics.growth_rate > 100:
            base_potential *= 1.2
        if len(metrics.viral_triggers) > 2:
            base_potential *= 1.1
        
        return round(min(base_potential * 100, 100), 2)

    async def _generate_viral_predictions(self, metrics: ViralMetrics) -> Dict[str, Any]:
        """Generate viral content predictions."""
        import random
        
        return {
            'peak_reach_prediction': random.randint(10000, 1000000),
            'peak_time_hours': random.randint(6, 72),
            'total_engagement_prediction': random.randint(5000, 500000),
            'cross_platform_spread_prediction': random.randint(2, 8),
            'viral_lifespan_hours': random.randint(24, 168)
        }

    def _generate_viral_recommendations(self, metrics: ViralMetrics, stage: ViralityStage) -> List[str]:
        """Generate recommendations for viral content optimization."""
        recommendations = []
        
        if stage == ViralityStage.EMERGING:
            recommendations.extend([
                "Boost content with paid promotion to accelerate viral growth",
                "Engage with early commenters to increase engagement velocity",
                "Cross-post to other platforms immediately"
            ])
        elif stage == ViralityStage.TRENDING:
            recommendations.extend([
                "Create follow-up content to capitalize on momentum",
                "Collaborate with other creators to expand reach",
                "Optimize posting times for maximum visibility"
            ])
        elif stage == ViralityStage.VIRAL:
            recommendations.extend([
                "Prepare content series to maintain audience attention",
                "Monitor for brand partnership opportunities",
                "Document viral strategies for future replication"
            ])
        
        if 'trending_hashtag' in metrics.viral_triggers:
            recommendations.append("Continue leveraging trending hashtags while relevant")
        
        if metrics.cross_platform_spread < 3:
            recommendations.append("Expand content to additional platforms for maximum viral reach")
        
        return recommendations