"""Revenue Performance Analyzer - IA Influencer Agent Platform
=========================================================

Advanced revenue performance analysis engine providing comprehensive
metrics, benchmarking, and optimization insights for content creators.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from enum import Enum
import statistics
import uuid

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """Revenue performance metrics."""
    TOTAL_REVENUE = "total_revenue"
    REVENUE_GROWTH_RATE = "revenue_growth_rate"
    AVERAGE_REVENUE_PER_USER = "average_revenue_per_user"
    REVENUE_PER_CONTENT = "revenue_per_content"
    CONVERSION_RATE = "conversion_rate"
    LIFETIME_VALUE = "lifetime_value"
    RETENTION_RATE = "retention_rate"
    CHURN_RATE = "churn_rate"


@dataclass
class PerformanceInsight:
    """Revenue performance insight."""
    insight_id: str
    metric: PerformanceMetric
    current_value: float
    benchmark_value: float
    performance_score: float
    trend: str
    recommendations: List[str]
    impact_potential: str


class RevenuePerformanceAnalyzer:
    """Advanced revenue performance analysis engine."""
    
    def __init__(self, creator_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize revenue performance analyzer."""
        self.creator_id = creator_id
        self.config = config or {}
        self.performance_history: List[Dict[str, Any]] = []
        self.benchmarks: Dict[str, float] = {}
        
    async def analyze_comprehensive_performance(
        self,
        revenue_data: List[Dict[str, Any]],
        timeframe_days: int = 90
    ) -> Dict[str, Any]:
        """Perform comprehensive revenue performance analysis."""
        try:
            # Calculate core performance metrics
            core_metrics = await self._calculate_core_metrics(revenue_data, timeframe_days)
            
            # Perform trend analysis
            trend_analysis = await self._analyze_revenue_trends(revenue_data)
            
            # Generate performance insights
            insights = await self._generate_performance_insights(core_metrics, trend_analysis)
            
            # Calculate performance scores
            performance_scores = await self._calculate_performance_scores(core_metrics)
            
            # Generate recommendations
            recommendations = await self._generate_optimization_recommendations(
                insights, performance_scores
            )
            
            return {
                "analysis_id": str(uuid.uuid4()),
                "creator_id": self.creator_id,
                "timeframe_days": timeframe_days,
                "core_metrics": core_metrics,
                "trend_analysis": trend_analysis,
                "performance_insights": insights,
                "performance_scores": performance_scores,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            raise
    
    async def benchmark_against_industry(
        self,
        creator_metrics: Dict[str, float],
        industry_segment: str = "content_creator"
    ) -> Dict[str, Any]:
        """Benchmark creator performance against industry standards."""
        try:
            # Get industry benchmarks
            industry_benchmarks = await self._get_industry_benchmarks(industry_segment)
            
            # Calculate performance gaps
            performance_gaps = await self._calculate_performance_gaps(
                creator_metrics, industry_benchmarks
            )
            
            # Determine performance ranking
            performance_ranking = await self._calculate_performance_ranking(
                creator_metrics, industry_benchmarks
            )
            
            # Generate competitive insights
            competitive_insights = await self._generate_competitive_insights(
                performance_gaps, performance_ranking
            )
            
            return {
                "creator_metrics": creator_metrics,
                "industry_benchmarks": industry_benchmarks,
                "performance_gaps": performance_gaps,
                "performance_ranking": performance_ranking,
                "competitive_insights": competitive_insights,
                "benchmark_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Industry benchmarking failed: {e}")
            raise
    
    async def _calculate_core_metrics(
        self,
        revenue_data: List[Dict[str, Any]],
        timeframe_days: int
    ) -> Dict[str, float]:
        """Calculate core revenue performance metrics."""
        if not revenue_data:
            return {}
        
        # Filter data by timeframe
        cutoff_date = datetime.utcnow() - timedelta(days=timeframe_days)
        filtered_data = [
            record for record in revenue_data
            if datetime.fromisoformat(record.get('date', '2024-01-01')) >= cutoff_date
        ]
        
        if not filtered_data:
            return {}
        
        # Calculate total revenue
        total_revenue = sum(float(record.get('amount', 0)) for record in filtered_data)
        
        # Calculate revenue growth rate
        growth_rate = await self._calculate_growth_rate(filtered_data)
        
        # Calculate average revenue per user
        unique_users = len(set(record.get('user_id') for record in filtered_data if record.get('user_id')))
        arpu = total_revenue / max(unique_users, 1)
        
        # Calculate revenue per content
        unique_content = len(set(record.get('content_id') for record in filtered_data if record.get('content_id')))
        revenue_per_content = total_revenue / max(unique_content, 1)
        
        # Calculate conversion rate
        conversion_rate = await self._calculate_conversion_rate(filtered_data)
        
        # Calculate customer lifetime value
        ltv = await self._calculate_lifetime_value(filtered_data)
        
        return {
            'total_revenue': total_revenue,
            'revenue_growth_rate': growth_rate,
            'average_revenue_per_user': arpu,
            'revenue_per_content': revenue_per_content,
            'conversion_rate': conversion_rate,
            'customer_lifetime_value': ltv,
            'data_points': len(filtered_data)
        }
    
    async def _calculate_growth_rate(self, revenue_data: List[Dict[str, Any]]) -> float:
        """Calculate revenue growth rate."""
        if len(revenue_data) < 2:
            return 0.0
        
        # Sort by date
        sorted_data = sorted(revenue_data, key=lambda x: x.get('date', '2024-01-01'))
        
        # Split into first and second half
        mid_point = len(sorted_data) // 2
        first_half = sorted_data[:mid_point]
        second_half = sorted_data[mid_point:]
        
        # Calculate average revenue for each half
        first_half_avg = sum(float(record.get('amount', 0)) for record in first_half) / len(first_half)
        second_half_avg = sum(float(record.get('amount', 0)) for record in second_half) / len(second_half)
        
        # Calculate growth rate
        if first_half_avg > 0:
            growth_rate = (second_half_avg - first_half_avg) / first_half_avg
        else:
            growth_rate = 0.0
        
        return growth_rate
    
    async def _calculate_conversion_rate(self, revenue_data: List[Dict[str, Any]]) -> float:
        """Calculate conversion rate from engagement to revenue."""
        # Simplified calculation - would use actual engagement data in practice
        revenue_events = len([record for record in revenue_data if float(record.get('amount', 0)) > 0])
        total_events = len(revenue_data)
        
        return revenue_events / max(total_events, 1)
    
    async def _calculate_lifetime_value(self, revenue_data: List[Dict[str, Any]]) -> float:
        """Calculate customer lifetime value."""
        # Group by user
        user_revenues = {}
        for record in revenue_data:
            user_id = record.get('user_id')
            if user_id:
                if user_id not in user_revenues:
                    user_revenues[user_id] = []
                user_revenues[user_id].append(float(record.get('amount', 0)))
        
        if not user_revenues:
            return 0.0
        
        # Calculate average total revenue per user
        user_totals = [sum(revenues) for revenues in user_revenues.values()]
        avg_user_revenue = statistics.mean(user_totals)
        
        # Estimate lifetime multiplier (simplified)
        lifetime_multiplier = 2.5  # Average user stays for 2.5x the measurement period
        
        return avg_user_revenue * lifetime_multiplier
    
    async def _analyze_revenue_trends(self, revenue_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze revenue trends over time."""
        if not revenue_data:
            return {}
        
        # Sort by date
        sorted_data = sorted(revenue_data, key=lambda x: x.get('date', '2024-01-01'))
        
        # Group by time periods
        daily_revenues = {}
        for record in sorted_data:
            date_str = record.get('date', '2024-01-01')[:10]  # YYYY-MM-DD
            if date_str not in daily_revenues:
                daily_revenues[date_str] = 0
            daily_revenues[date_str] += float(record.get('amount', 0))
        
        # Calculate trend metrics
        revenues = list(daily_revenues.values())
        
        if len(revenues) < 2:
            return {'trend_direction': 'stable', 'volatility': 0.0}
        
        # Calculate trend direction
        first_quarter = revenues[:len(revenues)//4] if len(revenues) >= 4 else revenues[:1]
        last_quarter = revenues[-len(revenues)//4:] if len(revenues) >= 4 else revenues[-1:]
        
        avg_first = statistics.mean(first_quarter)
        avg_last = statistics.mean(last_quarter)
        
        if avg_last > avg_first * 1.1:
            trend_direction = 'increasing'
        elif avg_last < avg_first * 0.9:
            trend_direction = 'decreasing'
        else:
            trend_direction = 'stable'
        
        # Calculate volatility
        volatility = statistics.stdev(revenues) / statistics.mean(revenues) if statistics.mean(revenues) > 0 else 0
        
        # Identify patterns
        patterns = await self._identify_revenue_patterns(daily_revenues)
        
        return {
            'trend_direction': trend_direction,
            'volatility': volatility,
            'daily_revenues': daily_revenues,
            'patterns': patterns,
            'revenue_momentum': await self._calculate_revenue_momentum(revenues)
        }
    
    async def _identify_revenue_patterns(self, daily_revenues: Dict[str, float]) -> Dict[str, Any]:
        """Identify patterns in revenue data."""
        patterns = {
            'seasonal_patterns': [],
            'peak_days': [],
            'low_performance_days': []
        }
        
        revenues = list(daily_revenues.values())
        dates = list(daily_revenues.keys())
        
        if len(revenues) < 7:
            return patterns
        
        # Identify peak days (top 20%)
        revenue_threshold_high = statistics.quantiles(revenues, n=5)[3]  # 80th percentile
        revenue_threshold_low = statistics.quantiles(revenues, n=5)[1]   # 20th percentile
        
        for date, revenue in daily_revenues.items():
            if revenue >= revenue_threshold_high:
                patterns['peak_days'].append({'date': date, 'revenue': revenue})
            elif revenue <= revenue_threshold_low:
                patterns['low_performance_days'].append({'date': date, 'revenue': revenue})
        
        # Weekly pattern analysis
        weekly_pattern = await self._analyze_weekly_pattern(daily_revenues)
        patterns['weekly_pattern'] = weekly_pattern
        
        return patterns
    
    async def _analyze_weekly_pattern(self, daily_revenues: Dict[str, float]) -> Dict[str, float]:
        """Analyze weekly revenue patterns."""
        weekday_revenues = {i: [] for i in range(7)}  # 0=Monday, 6=Sunday
        
        for date_str, revenue in daily_revenues.items():
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                weekday = date_obj.weekday()
                weekday_revenues[weekday].append(revenue)
            except ValueError:
                continue
        
        # Calculate average revenue by weekday
        weekday_averages = {}
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        for weekday, revenues in weekday_revenues.items():
            if revenues:
                weekday_averages[weekday_names[weekday]] = statistics.mean(revenues)
            else:
                weekday_averages[weekday_names[weekday]] = 0.0
        
        return weekday_averages
    
    async def _calculate_revenue_momentum(self, revenues: List[float]) -> Dict[str, float]:
        """Calculate revenue momentum indicators."""
        if len(revenues) < 3:
            return {'momentum_score': 0.0, 'acceleration': 0.0}
        
        # Calculate momentum as rate of change of growth rate
        recent_period = revenues[-len(revenues)//3:]  # Last third
        previous_period = revenues[-2*len(revenues)//3:-len(revenues)//3]  # Middle third
        
        if not previous_period:
            return {'momentum_score': 0.0, 'acceleration': 0.0}
        
        recent_avg = statistics.mean(recent_period)
        previous_avg = statistics.mean(previous_period)
        
        momentum_score = (recent_avg - previous_avg) / max(previous_avg, 1) if previous_avg > 0 else 0
        
        # Calculate acceleration (change in momentum)
        if len(revenues) >= 6:
            early_period = revenues[:len(revenues)//3]  # First third
            early_avg = statistics.mean(early_period)
            
            if early_avg > 0:
                early_momentum = (previous_avg - early_avg) / early_avg
                acceleration = momentum_score - early_momentum
            else:
                acceleration = 0.0
        else:
            acceleration = 0.0
        
        return {
            'momentum_score': momentum_score,
            'acceleration': acceleration
        }
    
    async def _generate_performance_insights(
        self,
        core_metrics: Dict[str, float],
        trend_analysis: Dict[str, Any]
    ) -> List[PerformanceInsight]:
        """Generate actionable performance insights."""
        insights = []
        
        # Revenue growth insight
        growth_rate = core_metrics.get('revenue_growth_rate', 0)
        insights.append(PerformanceInsight(
            insight_id=str(uuid.uuid4()),
            metric=PerformanceMetric.REVENUE_GROWTH_RATE,
            current_value=growth_rate,
            benchmark_value=0.15,  # 15% industry benchmark
            performance_score=min(100, (growth_rate / 0.15) * 100) if growth_rate >= 0 else 0,
            trend=trend_analysis.get('trend_direction', 'stable'),
            recommendations=await self._get_growth_recommendations(growth_rate),
            impact_potential='high' if growth_rate < 0.1 else 'medium'
        ))
        
        # ARPU insight
        arpu = core_metrics.get('average_revenue_per_user', 0)
        insights.append(PerformanceInsight(
            insight_id=str(uuid.uuid4()),
            metric=PerformanceMetric.AVERAGE_REVENUE_PER_USER,
            current_value=arpu,
            benchmark_value=25.0,  # $25 industry benchmark
            performance_score=min(100, (arpu / 25.0) * 100),
            trend=await self._determine_arpu_trend(core_metrics),
            recommendations=await self._get_arpu_recommendations(arpu),
            impact_potential='high' if arpu < 15 else 'medium'
        ))
        
        # Conversion rate insight
        conversion_rate = core_metrics.get('conversion_rate', 0)
        insights.append(PerformanceInsight(
            insight_id=str(uuid.uuid4()),
            metric=PerformanceMetric.CONVERSION_RATE,
            current_value=conversion_rate,
            benchmark_value=0.05,  # 5% industry benchmark
            performance_score=min(100, (conversion_rate / 0.05) * 100),
            trend=await self._determine_conversion_trend(trend_analysis),
            recommendations=await self._get_conversion_recommendations(conversion_rate),
            impact_potential='high' if conversion_rate < 0.03 else 'medium'
        ))
        
        return insights
    
    async def _calculate_performance_scores(self, core_metrics: Dict[str, float]) -> Dict[str, float]:
        """Calculate overall performance scores."""
        scores = {}
        
        # Revenue performance score (0-100)
        total_revenue = core_metrics.get('total_revenue', 0)
        revenue_score = min(100, (total_revenue / 10000) * 100)  # $10k benchmark
        scores['revenue_performance'] = revenue_score
        
        # Growth performance score
        growth_rate = core_metrics.get('revenue_growth_rate', 0)
        growth_score = min(100, max(0, (growth_rate / 0.2) * 100))  # 20% excellent growth
        scores['growth_performance'] = growth_score
        
        # Efficiency performance score
        arpu = core_metrics.get('average_revenue_per_user', 0)
        efficiency_score = min(100, (arpu / 50) * 100)  # $50 excellent ARPU
        scores['efficiency_performance'] = efficiency_score
        
        # Overall performance score (weighted average)
        overall_score = (
            revenue_score * 0.4 +
            growth_score * 0.35 +
            efficiency_score * 0.25
        )
        scores['overall_performance'] = overall_score
        
        return scores
    
    async def _generate_optimization_recommendations(
        self,
        insights: List[PerformanceInsight],
        performance_scores: Dict[str, float]
    ) -> List[str]:
        """Generate comprehensive optimization recommendations."""
        recommendations = []
        
        # Priority recommendations based on performance scores
        overall_score = performance_scores.get('overall_performance', 0)
        
        if overall_score < 50:
            recommendations.extend([
                "Critical: Overall performance is below average - implement comprehensive revenue optimization strategy",
                "Focus on high-impact areas: content quality, audience targeting, and monetization strategies"
            ])
        elif overall_score < 75:
            recommendations.extend([
                "Moderate: Performance has room for improvement - optimize key revenue drivers",
                "Implement A/B testing for content strategies and pricing models"
            ])
        
        # Specific recommendations from insights
        for insight in insights:
            if insight.performance_score < 70:
                recommendations.extend(insight.recommendations)
        
        # Growth-specific recommendations
        growth_score = performance_scores.get('growth_performance', 0)
        if growth_score < 60:
            recommendations.extend([
                "Develop and execute growth strategy focusing on audience expansion",
                "Optimize content distribution across multiple platforms",
                "Implement referral and affiliate programs"
            ])
        
        # Efficiency recommendations
        efficiency_score = performance_scores.get('efficiency_performance', 0)
        if efficiency_score < 60:
            recommendations.extend([
                "Optimize pricing strategy and value proposition",
                "Improve customer segmentation and targeting",
                "Develop premium content offerings for higher ARPU"
            ])
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    async def _get_industry_benchmarks(self, industry_segment: str) -> Dict[str, float]:
        """Get industry benchmark values."""
        # Industry benchmarks by segment
        benchmarks = {
            'content_creator': {
                'revenue_growth_rate': 0.15,      # 15% monthly growth
                'average_revenue_per_user': 25.0, # $25 ARPU
                'conversion_rate': 0.05,          # 5% conversion rate
                'customer_lifetime_value': 150.0  # $150 LTV
            },
            'influencer': {
                'revenue_growth_rate': 0.20,      # 20% monthly growth
                'average_revenue_per_user': 35.0, # $35 ARPU
                'conversion_rate': 0.07,          # 7% conversion rate
                'customer_lifetime_value': 200.0  # $200 LTV
            },
            'entertainer': {
                'revenue_growth_rate': 0.12,      # 12% monthly growth
                'average_revenue_per_user': 20.0, # $20 ARPU
                'conversion_rate': 0.04,          # 4% conversion rate
                'customer_lifetime_value': 120.0  # $120 LTV
            }
        }
        
        return benchmarks.get(industry_segment, benchmarks['content_creator'])
    
    async def _calculate_performance_gaps(
        self,
        creator_metrics: Dict[str, float],
        industry_benchmarks: Dict[str, float]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate performance gaps against benchmarks."""
        gaps = {}
        
        for metric, benchmark_value in industry_benchmarks.items():
            creator_value = creator_metrics.get(metric, 0)
            
            gap_absolute = creator_value - benchmark_value
            gap_percentage = (gap_absolute / benchmark_value * 100) if benchmark_value > 0 else 0
            
            gaps[metric] = {
                'creator_value': creator_value,
                'benchmark_value': benchmark_value,
                'gap_absolute': gap_absolute,
                'gap_percentage': gap_percentage,
                'status': 'above_benchmark' if gap_absolute >= 0 else 'below_benchmark'
            }
        
        return gaps
    
    async def _calculate_performance_ranking(
        self,
        creator_metrics: Dict[str, float],
        industry_benchmarks: Dict[str, float]
    ) -> Dict[str, Any]:
        """Calculate performance ranking against industry."""
        total_metrics = len(industry_benchmarks)
        metrics_above_benchmark = 0
        
        performance_ratios = []
        
        for metric, benchmark_value in industry_benchmarks.items():
            creator_value = creator_metrics.get(metric, 0)
            
            if creator_value >= benchmark_value:
                metrics_above_benchmark += 1
            
            if benchmark_value > 0:
                ratio = creator_value / benchmark_value
                performance_ratios.append(ratio)
        
        # Calculate overall performance ratio
        avg_performance_ratio = statistics.mean(performance_ratios) if performance_ratios else 0
        
        # Determine percentile ranking (simplified)
        if avg_performance_ratio >= 1.5:
            percentile = 90
            ranking = 'top_performer'
        elif avg_performance_ratio >= 1.2:
            percentile = 75
            ranking = 'above_average'
        elif avg_performance_ratio >= 0.8:
            percentile = 50
            ranking = 'average'
        else:
            percentile = 25
            ranking = 'below_average'
        
        return {
            'overall_performance_ratio': avg_performance_ratio,
            'metrics_above_benchmark': metrics_above_benchmark,
            'total_metrics': total_metrics,
            'percentile_ranking': percentile,
            'performance_category': ranking
        }
    
    async def _generate_competitive_insights(
        self,
        performance_gaps: Dict[str, Dict[str, float]],
        performance_ranking: Dict[str, Any]
    ) -> List[str]:
        """Generate competitive insights and recommendations."""
        insights = []
        
        # Overall performance insight
        ranking = performance_ranking['performance_category']
        percentile = performance_ranking['percentile_ranking']
        
        insights.append(
            f"Your performance ranks in the {percentile}th percentile, categorized as '{ranking}' compared to industry standards"
        )
        
        # Specific gap insights
        significant_gaps = [
            metric for metric, gap_data in performance_gaps.items()
            if gap_data['gap_percentage'] < -20  # More than 20% below benchmark
        ]
        
        if significant_gaps:
            insights.append(
                f"Critical improvement areas: {', '.join(significant_gaps)} - significantly below industry benchmarks"
            )
        
        # Strength insights
        strengths = [
            metric for metric, gap_data in performance_gaps.items()
            if gap_data['gap_percentage'] > 20  # More than 20% above benchmark
        ]
        
        if strengths:
            insights.append(
                f"Competitive advantages: {', '.join(strengths)} - significantly outperforming industry benchmarks"
            )
        
        # Strategic recommendations
        if ranking == 'below_average':
            insights.append(
                "Recommended strategy: Focus on fundamental performance improvements across all key metrics"
            )
        elif ranking == 'average':
            insights.append(
                "Recommended strategy: Identify and double down on 2-3 key differentiating factors"
            )
        else:
            insights.append(
                "Recommended strategy: Maintain competitive advantages while exploring new growth opportunities"
            )
        
        return insights
    
    # Helper methods for trend analysis
    async def _determine_arpu_trend(self, core_metrics: Dict[str, float]) -> str:
        """Determine ARPU trend direction."""
        # Simplified trend determination
        arpu = core_metrics.get('average_revenue_per_user', 0)
        if arpu > 30:
            return 'increasing'
        elif arpu < 15:
            return 'decreasing'
        else:
            return 'stable'
    
    async def _determine_conversion_trend(self, trend_analysis: Dict[str, Any]) -> str:
        """Determine conversion rate trend."""
        return trend_analysis.get('trend_direction', 'stable')
    
    async def _get_growth_recommendations(self, growth_rate: float) -> List[str]:
        """Get specific recommendations for growth rate improvement."""
        if growth_rate < 0:
            return [
                "Critical: Address negative growth with immediate revenue recovery plan",
                "Analyze customer churn and implement retention strategies"
            ]
        elif growth_rate < 0.05:
            return [
                "Low growth: Implement aggressive customer acquisition campaigns",
                "Diversify revenue streams and improve product offerings"
            ]
        elif growth_rate < 0.15:
            return [
                "Moderate growth: Optimize existing strategies and scale successful initiatives",
                "Focus on customer expansion and upselling opportunities"
            ]
        else:
            return [
                "Strong growth: Maintain momentum and prepare for scaling challenges",
                "Invest in infrastructure and team expansion"
            ]
    
    async def _get_arpu_recommendations(self, arpu: float) -> List[str]:
        """Get specific recommendations for ARPU improvement."""
        if arpu < 10:
            return [
                "Low ARPU: Implement premium pricing strategy and value-added services",
                "Develop tiered subscription models with higher-value offerings"
            ]
        elif arpu < 25:
            return [
                "Below average ARPU: Optimize pricing strategy and customer segmentation",
                "Introduce upselling and cross-selling programs"
            ]
        else:
            return [
                "Good ARPU: Focus on customer retention and lifetime value optimization",
                "Explore enterprise and premium customer segments"
            ]
    
    async def _get_conversion_recommendations(self, conversion_rate: float) -> List[str]:
        """Get specific recommendations for conversion rate improvement."""
        if conversion_rate < 0.02:
            return [
                "Low conversion: Redesign user experience and value proposition",
                "Implement comprehensive funnel optimization strategy"
            ]
        elif conversion_rate < 0.05:
            return [
                "Below average conversion: A/B test landing pages and call-to-action elements",
                "Improve targeting and lead qualification processes"
            ]
        else:
            return [
                "Good conversion rate: Fine-tune campaigns and optimize for quality leads",
                "Implement advanced personalization and recommendation systems"
            ]