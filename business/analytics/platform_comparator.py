"""
Platform Performance Comparator - Cross-platform performance analysis
=====================================================================

Advanced platform comparison system with competitive analysis, performance benchmarking,
and cross-platform optimization recommendations for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import redis
import asyncpg
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported platform types"""
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    SPOTIFY = "spotify"
    TWITCH = "twitch"

@dataclass
class PlatformMetrics:
    """Platform-specific performance metrics"""
    platform: PlatformType
    followers: int
    engagement_rate: float
    reach: int
    impressions: int
    content_count: int
    avg_performance_score: float
    top_performing_format: str
    growth_rate: float

class PlatformPerformanceComparator:
    """
    Cross-platform performance analysis system with competitive benchmarking
    and optimization recommendations for multi-platform content creators.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        
    async def initialize(self) -> None:
        """Initialize platform comparator"""
        try:
            await self._setup_database_tables()
            logger.info("Platform Performance Comparator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Platform Performance Comparator: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for platform comparison"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS platform_metrics (
                    id SERIAL PRIMARY KEY,
                    creator_id VARCHAR(255) NOT NULL,
                    platform VARCHAR(50) NOT NULL,
                    followers INTEGER DEFAULT 0,
                    engagement_rate FLOAT DEFAULT 0,
                    reach INTEGER DEFAULT 0,
                    impressions INTEGER DEFAULT 0,
                    content_count INTEGER DEFAULT 0,
                    avg_performance_score FLOAT DEFAULT 0,
                    top_performing_format VARCHAR(50),
                    growth_rate FLOAT DEFAULT 0,
                    recorded_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_creator_platform (creator_id, platform, recorded_at)
                );
            """)

    async def compare_platform_performance(self, creator_id: str) -> Dict[str, Any]:
        """Compare performance across all creator's platforms"""
        try:
            # Get latest metrics for all platforms
            platform_data = await self._get_platform_metrics(creator_id)
            
            if not platform_data:
                return {'error': 'No platform data available'}
            
            # Calculate comparative metrics
            comparison_results = {
                'platform_rankings': self._rank_platforms(platform_data),
                'engagement_analysis': self._analyze_engagement_patterns(platform_data),
                'growth_analysis': self._analyze_growth_patterns(platform_data),
                'content_format_analysis': self._analyze_content_formats(platform_data),
                'optimization_recommendations': self._generate_optimization_recommendations(platform_data),
                'cross_platform_strategy': self._suggest_cross_platform_strategy(platform_data),
                'generated_at': datetime.now().isoformat()
            }
            
            return comparison_results
            
        except Exception as e:
            logger.error(f"Failed to compare platform performance: {e}")
            raise HTTPException(status_code=500, detail="Platform comparison failed")

    async def _get_platform_metrics(self, creator_id: str) -> List[PlatformMetrics]:
        """Get latest platform metrics for creator"""
        try:
            async with self.db_pool.acquire() as conn:
                records = await conn.fetch("""
                    SELECT DISTINCT ON (platform) platform, followers, engagement_rate, reach, impressions,
                           content_count, avg_performance_score, top_performing_format, growth_rate
                    FROM platform_metrics 
                    WHERE creator_id = $1 
                    ORDER BY platform, recorded_at DESC
                """, creator_id)
                
                metrics = []
                for record in records:
                    metrics.append(PlatformMetrics(
                        platform=PlatformType(record['platform']),
                        followers=record['followers'],
                        engagement_rate=record['engagement_rate'],
                        reach=record['reach'],
                        impressions=record['impressions'],
                        content_count=record['content_count'],
                        avg_performance_score=record['avg_performance_score'],
                        top_performing_format=record['top_performing_format'],
                        growth_rate=record['growth_rate']
                    ))
                
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to get platform metrics: {e}")
            return []

    def _rank_platforms(self, platform_data: List[PlatformMetrics]) -> Dict[str, Any]:
        """Rank platforms by various performance metrics"""
        try:
            rankings = {
                'by_followers': sorted(platform_data, key=lambda x: x.followers, reverse=True),
                'by_engagement': sorted(platform_data, key=lambda x: x.engagement_rate, reverse=True),
                'by_reach': sorted(platform_data, key=lambda x: x.reach, reverse=True),
                'by_growth': sorted(platform_data, key=lambda x: x.growth_rate, reverse=True),
                'overall_performance': sorted(platform_data, key=lambda x: x.avg_performance_score, reverse=True)
            }
            
            # Format for JSON response
            formatted_rankings = {}
            for category, platforms in rankings.items():
                formatted_rankings[category] = [
                    {
                        'platform': p.platform.value,
                        'score': getattr(p, category.split('_')[-1]) if hasattr(p, category.split('_')[-1]) else p.avg_performance_score,
                        'rank': idx + 1
                    }
                    for idx, p in enumerate(platforms)
                ]
            
            return formatted_rankings
            
        except Exception as e:
            logger.error(f"Failed to rank platforms: {e}")
            return {}

    def _analyze_engagement_patterns(self, platform_data: List[PlatformMetrics]) -> Dict[str, Any]:
        """Analyze engagement patterns across platforms"""
        try:
            if not platform_data:
                return {}
            
            engagement_rates = [p.engagement_rate for p in platform_data]
            avg_engagement = np.mean(engagement_rates)
            
            # Find platforms above/below average
            above_average = [p for p in platform_data if p.engagement_rate > avg_engagement]
            below_average = [p for p in platform_data if p.engagement_rate <= avg_engagement]
            
            return {
                'average_engagement_rate': avg_engagement,
                'highest_engagement': {
                    'platform': max(platform_data, key=lambda x: x.engagement_rate).platform.value,
                    'rate': max(engagement_rates)
                },
                'lowest_engagement': {
                    'platform': min(platform_data, key=lambda x: x.engagement_rate).platform.value,
                    'rate': min(engagement_rates)
                },
                'above_average_platforms': [p.platform.value for p in above_average],
                'below_average_platforms': [p.platform.value for p in below_average],
                'engagement_variance': np.var(engagement_rates)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze engagement patterns: {e}")
            return {}

    def _analyze_growth_patterns(self, platform_data: List[PlatformMetrics]) -> Dict[str, Any]:
        """Analyze growth patterns across platforms"""
        try:
            growth_rates = [p.growth_rate for p in platform_data]
            
            if not growth_rates:
                return {}
            
            return {
                'average_growth_rate': np.mean(growth_rates),
                'fastest_growing': {
                    'platform': max(platform_data, key=lambda x: x.growth_rate).platform.value,
                    'rate': max(growth_rates)
                },
                'slowest_growing': {
                    'platform': min(platform_data, key=lambda x: x.growth_rate).platform.value,
                    'rate': min(growth_rates)
                },
                'growth_opportunities': [
                    p.platform.value for p in platform_data 
                    if p.growth_rate < np.mean(growth_rates) * 0.5
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze growth patterns: {e}")
            return {}

    def _analyze_content_formats(self, platform_data: List[PlatformMetrics]) -> Dict[str, Any]:
        """Analyze top performing content formats by platform"""
        try:
            format_analysis = {}
            
            for platform_metric in platform_data:
                format_analysis[platform_metric.platform.value] = {
                    'top_format': platform_metric.top_performing_format,
                    'performance_score': platform_metric.avg_performance_score
                }
            
            # Find most successful formats overall
            format_counter = {}
            for platform_metric in platform_data:
                format_name = platform_metric.top_performing_format
                if format_name:
                    if format_name not in format_counter:
                        format_counter[format_name] = []
                    format_counter[format_name].append(platform_metric.avg_performance_score)
            
            # Calculate average performance by format
            format_performance = {}
            for format_name, scores in format_counter.items():
                format_performance[format_name] = np.mean(scores)
            
            return {
                'by_platform': format_analysis,
                'overall_format_performance': format_performance,
                'recommended_formats': sorted(format_performance.keys(), 
                                            key=lambda x: format_performance[x], reverse=True)[:3]
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze content formats: {e}")
            return {}

    def _generate_optimization_recommendations(self, platform_data: List[PlatformMetrics]) -> List[Dict[str, Any]]:
        """Generate platform-specific optimization recommendations"""
        recommendations = []
        
        try:
            # Calculate benchmarks
            avg_engagement = np.mean([p.engagement_rate for p in platform_data])
            avg_growth = np.mean([p.growth_rate for p in platform_data])
            
            for platform_metric in platform_data:
                platform_recs = {
                    'platform': platform_metric.platform.value,
                    'recommendations': []
                }
                
                # Engagement recommendations
                if platform_metric.engagement_rate < avg_engagement * 0.7:
                    platform_recs['recommendations'].append({
                        'type': 'engagement_improvement',
                        'priority': 'high',
                        'suggestion': f"Focus on improving engagement rate on {platform_metric.platform.value}",
                        'current_rate': platform_metric.engagement_rate,
                        'target_rate': avg_engagement
                    })
                
                # Growth recommendations
                if platform_metric.growth_rate < avg_growth * 0.5:
                    platform_recs['recommendations'].append({
                        'type': 'growth_acceleration',
                        'priority': 'medium',
                        'suggestion': f"Implement growth strategies for {platform_metric.platform.value}",
                        'current_rate': platform_metric.growth_rate,
                        'target_rate': avg_growth
                    })
                
                # Content recommendations
                if platform_metric.avg_performance_score < 60:
                    platform_recs['recommendations'].append({
                        'type': 'content_optimization',
                        'priority': 'high',
                        'suggestion': f"Optimize content strategy for {platform_metric.platform.value}",
                        'current_score': platform_metric.avg_performance_score,
                        'target_score': 75
                    })
                
                if platform_recs['recommendations']:
                    recommendations.append(platform_recs)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate optimization recommendations: {e}")
            return []

    def _suggest_cross_platform_strategy(self, platform_data: List[PlatformMetrics]) -> Dict[str, Any]:
        """Suggest cross-platform content and growth strategy"""
        try:
            # Identify strongest and weakest platforms
            strongest_platform = max(platform_data, key=lambda x: x.avg_performance_score)
            weakest_platform = min(platform_data, key=lambda x: x.avg_performance_score)
            
            # Calculate resource allocation suggestions
            total_followers = sum(p.followers for p in platform_data)
            
            allocation_suggestions = {}
            for platform_metric in platform_data:
                # Base allocation on performance and audience size
                performance_weight = platform_metric.avg_performance_score / 100
                audience_weight = platform_metric.followers / total_followers if total_followers > 0 else 0
                
                suggested_allocation = (performance_weight * 0.7 + audience_weight * 0.3) * 100
                allocation_suggestions[platform_metric.platform.value] = min(suggested_allocation, 100)
            
            # Normalize allocations to sum to 100%
            total_allocation = sum(allocation_suggestions.values())
            if total_allocation > 0:
                allocation_suggestions = {
                    k: (v / total_allocation) * 100 
                    for k, v in allocation_suggestions.items()
                }
            
            return {
                'primary_platform': strongest_platform.platform.value,
                'growth_opportunity_platform': weakest_platform.platform.value,
                'resource_allocation': allocation_suggestions,
                'cross_promotion_strategy': {
                    'source_platform': strongest_platform.platform.value,
                    'target_platforms': [p.platform.value for p in platform_data 
                                       if p.avg_performance_score < strongest_platform.avg_performance_score * 0.8],
                    'strategy': 'Leverage high-performing content from primary platform across weaker platforms'
                },
                'content_repurposing': {
                    'high_value_formats': [p.top_performing_format for p in platform_data 
                                         if p.avg_performance_score > 70],
                    'adaptation_priority': 'Adapt top-performing formats to underperforming platforms'
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to suggest cross-platform strategy: {e}")
            return {}

    async def get_competitive_analysis(self, creator_id: str, competitor_ids: List[str]) -> Dict[str, Any]:
        """Get competitive analysis against other creators"""
        try:
            # Get creator's metrics
            creator_metrics = await self._get_platform_metrics(creator_id)
            
            # Get competitors' metrics
            competitor_data = {}
            for competitor_id in competitor_ids:
                competitor_metrics = await self._get_platform_metrics(competitor_id)
                competitor_data[competitor_id] = competitor_metrics
            
            # Perform comparative analysis
            competitive_analysis = {
                'creator_performance': {
                    platform.platform.value: {
                        'engagement_rate': platform.engagement_rate,
                        'followers': platform.followers,
                        'growth_rate': platform.growth_rate,
                        'performance_score': platform.avg_performance_score
                    }
                    for platform in creator_metrics
                },
                'competitive_benchmarks': self._calculate_competitive_benchmarks(creator_metrics, competitor_data),
                'opportunities': self._identify_competitive_opportunities(creator_metrics, competitor_data),
                'generated_at': datetime.now().isoformat()
            }
            
            return competitive_analysis
            
        except Exception as e:
            logger.error(f"Failed to get competitive analysis: {e}")
            raise HTTPException(status_code=500, detail="Competitive analysis failed")

    def _calculate_competitive_benchmarks(self, creator_metrics: List[PlatformMetrics], 
                                        competitor_data: Dict[str, List[PlatformMetrics]]) -> Dict[str, Any]:
        """Calculate competitive benchmarks"""
        try:
            benchmarks = {}
            
            for platform_metric in creator_metrics:
                platform_name = platform_metric.platform.value
                
                # Collect competitor metrics for same platform
                competitor_metrics = []
                for competitor_id, metrics_list in competitor_data.items():
                    for metric in metrics_list:
                        if metric.platform.value == platform_name:
                            competitor_metrics.append(metric)
                
                if competitor_metrics:
                    benchmarks[platform_name] = {
                        'creator_vs_avg': {
                            'engagement_rate': platform_metric.engagement_rate / np.mean([m.engagement_rate for m in competitor_metrics]),
                            'followers': platform_metric.followers / np.mean([m.followers for m in competitor_metrics]),
                            'growth_rate': platform_metric.growth_rate / np.mean([m.growth_rate for m in competitor_metrics])
                        },
                        'percentile_ranking': {
                            'engagement_rate': self._calculate_percentile(platform_metric.engagement_rate, [m.engagement_rate for m in competitor_metrics]),
                            'followers': self._calculate_percentile(platform_metric.followers, [m.followers for m in competitor_metrics]),
                            'growth_rate': self._calculate_percentile(platform_metric.growth_rate, [m.growth_rate for m in competitor_metrics])
                        }
                    }
            
            return benchmarks
            
        except Exception as e:
            logger.error(f"Failed to calculate competitive benchmarks: {e}")
            return {}

    def _calculate_percentile(self, value: float, competitor_values: List[float]) -> float:
        """Calculate percentile ranking against competitors"""
        if not competitor_values:
            return 50.0  # Default to median
        
        competitor_values.append(value)
        sorted_values = sorted(competitor_values)
        position = sorted_values.index(value)
        
        return (position / (len(sorted_values) - 1)) * 100

    def _identify_competitive_opportunities(self, creator_metrics: List[PlatformMetrics], 
                                          competitor_data: Dict[str, List[PlatformMetrics]]) -> List[Dict[str, Any]]:
        """Identify opportunities based on competitive analysis"""
        opportunities = []
        
        try:
            for platform_metric in creator_metrics:
                platform_name = platform_metric.platform.value
                
                # Find top competitor on this platform
                competitor_metrics = []
                for competitor_id, metrics_list in competitor_data.items():
                    for metric in metrics_list:
                        if metric.platform.value == platform_name:
                            competitor_metrics.append((competitor_id, metric))
                
                if competitor_metrics:
                    top_competitor = max(competitor_metrics, key=lambda x: x[1].avg_performance_score)
                    
                    # Check for significant performance gaps
                    performance_gap = top_competitor[1].avg_performance_score - platform_metric.avg_performance_score
                    
                    if performance_gap > 20:  # Significant gap
                        opportunities.append({
                            'platform': platform_name,
                            'opportunity_type': 'performance_gap',
                            'description': f'Significant performance gap with top competitor on {platform_name}',
                            'gap_size': performance_gap,
                            'top_competitor_id': top_competitor[0],
                            'recommendation': f'Analyze top competitor content strategy on {platform_name}'
                        })
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to identify competitive opportunities: {e}")
            return []
