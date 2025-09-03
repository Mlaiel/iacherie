"""Content Optimizer - SEO Content Optimization Service

Advanced content optimization service that leverages the existing SEO engine
for comprehensive content optimization with AI-driven recommendations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

# Import from existing SEO engine
from ....seo_engine.content_optimizer import (
    ContentOptimizer as BaseContentOptimizer,
    OptimizedContent,
    ContentType,
    OptimizationLevel
)

logger = logging.getLogger(__name__)


@dataclass
class OptimizationRequest:
    """Request for content optimization"""
    content: str
    target_keywords: List[str]
    content_type: ContentType = ContentType.BLOG_POST
    optimization_level: OptimizationLevel = OptimizationLevel.ADVANCED
    existing_meta: Optional[Dict[str, str]] = None


@dataclass
class OptimizationResult:
    """Result of content optimization"""
    optimized_content: OptimizedContent
    optimization_score: float
    recommendations: List[str]
    performance_prediction: Dict[str, float]
    timestamp: datetime


class ContentOptimizer:
    """Analytics-integrated content optimization service"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.base_optimizer = BaseContentOptimizer(config)
        logger.info("Analytics ContentOptimizer service initialized")
    
    async def optimize_content(self, request: OptimizationRequest) -> OptimizationResult:
        """
        Optimize content with analytics integration
        
        Args:
            request: Optimization request parameters
            
        Returns:
            OptimizationResult: Comprehensive optimization result
        """
        try:
            # Use existing SEO engine for optimization
            optimized_content = await self.base_optimizer.optimize_content(
                content=request.content,
                target_keywords=request.target_keywords,
                content_type=request.content_type,
                existing_meta=request.existing_meta
            )
            
            # Calculate overall optimization score
            optimization_score = optimized_content.optimization_score
            
            # Generate recommendations
            recommendations = [
                rec.description for rec in optimized_content.recommendations
            ]
            
            # Performance prediction
            performance_prediction = {
                'traffic_increase': optimized_content.performance_prediction.get('traffic_increase', 0),
                'ranking_improvement': optimized_content.performance_prediction.get('ranking_improvement', 0),
                'engagement_boost': optimized_content.performance_prediction.get('engagement_boost', 0)
            }
            
            result = OptimizationResult(
                optimized_content=optimized_content,
                optimization_score=optimization_score,
                recommendations=recommendations,
                performance_prediction=performance_prediction,
                timestamp=datetime.now()
            )
            
            logger.info(f"Content optimization completed with score: {optimization_score}")
            return result
            
        except Exception as e:
            logger.error(f"Content optimization failed: {str(e)}")
            raise
    
    async def batch_optimize(self, requests: List[OptimizationRequest]) -> List[OptimizationResult]:
        """
        Optimize multiple content pieces in batch
        
        Args:
            requests: List of optimization requests
            
        Returns:
            List[OptimizationResult]: Batch optimization results
        """
        results = []
        for request in requests:
            try:
                result = await self.optimize_content(request)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch optimization failed for request: {str(e)}")
                continue
        
        logger.info(f"Batch optimization completed: {len(results)}/{len(requests)} successful")
        return results
    
    async def get_optimization_suggestions(self, content: str) -> List[str]:
        """
        Get quick optimization suggestions for content
        
        Args:
            content: Content to analyze
            
        Returns:
            List[str]: Optimization suggestions
        """
        try:
            # Quick analysis using base optimizer
            suggestions = []
            
            # Basic content analysis
            word_count = len(content.split())
            if word_count < 300:
                suggestions.append("Content is too short. Aim for at least 300 words.")
            elif word_count > 3000:
                suggestions.append("Content is very long. Consider breaking into sections.")
            
            # Check for headings
            if '<h1>' not in content and '<h2>' not in content:
                suggestions.append("Add headings (H1, H2) to improve structure.")
            
            # Check for meta description length
            if len(content) > 0:
                suggestions.append("Ensure meta description is 120-155 characters.")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to get optimization suggestions: {str(e)}")
            return []