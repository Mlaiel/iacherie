"""
ROI Calculator Engine - Comprehensive return on investment analysis
==================================================================

Advanced ROI calculation system with multi-dimensional analysis including
time investment, content performance, revenue generation, and optimization strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import redis
import asyncpg
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class ROICategory(Enum):
    """ROI calculation categories"""
    CONTENT_CREATION = "content_creation"
    ADVERTISING_SPEND = "advertising_spend"
    EQUIPMENT_INVESTMENT = "equipment_investment"
    TIME_INVESTMENT = "time_investment"
    PLATFORM_FEES = "platform_fees"
    COLLABORATION = "collaboration"

class ROITimeframe(Enum):
    """ROI calculation timeframes"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

@dataclass
class ROIData:
    """ROI calculation result data structure"""
    creator_id: str
    category: ROICategory
    timeframe: ROITimeframe
    investment_amount: float
    revenue_generated: float
    roi_percentage: float
    roi_absolute: float
    cost_per_engagement: float
    cost_per_conversion: float
    efficiency_score: float
    optimization_recommendations: List[str]

class ROICalculatorEngine:
    """
    Comprehensive ROI calculation system for content creators with
    multi-dimensional analysis and optimization recommendations.
    """
    
    def __init__(self, redis_client: redis.Redis, db_pool: asyncpg.Pool):
        self.redis = redis_client
        self.db_pool = db_pool
        
    async def initialize(self) -> None:
        """Initialize ROI calculator engine"""
        try:
            await self._setup_database_tables()
            logger.info("ROI Calculator Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize ROI Calculator Engine: {e}")
            raise

    async def _setup_database_tables(self) -> None:
        """Setup database tables for ROI tracking"""
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS roi_calculations (
                    id SERIAL PRIMARY KEY,
                    creator_id VARCHAR(255) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    timeframe VARCHAR(20) NOT NULL,
                    investment_amount DECIMAL(15,2) NOT NULL,
                    revenue_generated DECIMAL(15,2) NOT NULL,
                    roi_percentage DECIMAL(8,2) NOT NULL,
                    roi_absolute DECIMAL(15,2) NOT NULL,
                    cost_per_engagement DECIMAL(10,4),
                    cost_per_conversion DECIMAL(10,2),
                    efficiency_score DECIMAL(5,2),
                    optimization_recommendations TEXT[],
                    calculation_period_start DATE NOT NULL,
                    calculation_period_end DATE NOT NULL,
                    calculated_at TIMESTAMP DEFAULT NOW(),
                    INDEX idx_roi_creator_timeframe (creator_id, timeframe, calculated_at DESC),
                    INDEX idx_roi_category_performance (category, roi_percentage DESC)
                );
            """)

    async def calculate_comprehensive_roi(self, creator_id: str, timeframe: ROITimeframe) -> List[ROIData]:
        """Calculate comprehensive ROI across all categories"""
        try:
            roi_results = []
            
            for category in ROICategory:
                roi_data = await self._calculate_category_roi(creator_id, category, timeframe)
                if roi_data:
                    roi_results.append(roi_data)
            
            # Store calculations
            for roi in roi_results:
                await self._store_roi_calculation(roi)
            
            return roi_results
            
        except Exception as e:
            logger.error(f"Failed to calculate comprehensive ROI: {e}")
            return []

    async def _calculate_category_roi(self, creator_id: str, category: ROICategory, timeframe: ROITimeframe) -> Optional[ROIData]:
        """Calculate ROI for specific category and timeframe"""
        try:
            # Get timeframe dates
            end_date = datetime.now().date()
            start_date = self._get_timeframe_start_date(end_date, timeframe)
            
            # Get investment data
            investment_amount = await self._get_investment_amount(creator_id, category, start_date, end_date)
            if investment_amount <= 0:
                return None
            
            # Get revenue data
            revenue_generated = await self._get_revenue_generated(creator_id, category, start_date, end_date)
            
            # Get engagement metrics
            total_engagements = await self._get_total_engagements(creator_id, start_date, end_date)
            total_conversions = await self._get_total_conversions(creator_id, start_date, end_date)
            
            # Calculate ROI metrics
            roi_absolute = revenue_generated - investment_amount
            roi_percentage = (roi_absolute / investment_amount) * 100 if investment_amount > 0 else 0
            
            cost_per_engagement = investment_amount / total_engagements if total_engagements > 0 else 0
            cost_per_conversion = investment_amount / total_conversions if total_conversions > 0 else 0
            
            efficiency_score = self._calculate_efficiency_score(roi_percentage, cost_per_engagement, cost_per_conversion)
            
            # Generate optimization recommendations
            optimization_recommendations = self._generate_optimization_recommendations(
                category, roi_percentage, cost_per_engagement, cost_per_conversion, efficiency_score
            )
            
            return ROIData(
                creator_id=creator_id,
                category=category,
                timeframe=timeframe,
                investment_amount=investment_amount,
                revenue_generated=revenue_generated,
                roi_percentage=roi_percentage,
                roi_absolute=roi_absolute,
                cost_per_engagement=cost_per_engagement,
                cost_per_conversion=cost_per_conversion,
                efficiency_score=efficiency_score,
                optimization_recommendations=optimization_recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate category ROI: {e}")
            return None

    def _get_timeframe_start_date(self, end_date: datetime.date, timeframe: ROITimeframe) -> datetime.date:
        """Get start date based on timeframe"""
        if timeframe == ROITimeframe.DAILY:
            return end_date - timedelta(days=1)
        elif timeframe == ROITimeframe.WEEKLY:
            return end_date - timedelta(weeks=1)
        elif timeframe == ROITimeframe.MONTHLY:
            return end_date - timedelta(days=30)
        elif timeframe == ROITimeframe.QUARTERLY:
            return end_date - timedelta(days=90)
        elif timeframe == ROITimeframe.YEARLY:
            return end_date - timedelta(days=365)
        else:
            return end_date - timedelta(days=30)

    async def _get_investment_amount(self, creator_id: str, category: ROICategory, start_date: datetime.date, end_date: datetime.date) -> float:
        """Get investment amount for specific category and timeframe"""
        try:
            async with self.db_pool.acquire() as conn:
                if category == ROICategory.CONTENT_CREATION:
                    # Calculate content creation costs (time + resources)
                    result = await conn.fetchrow("""
                        SELECT COALESCE(SUM(creation_cost + resource_cost), 0) as total_investment
                        FROM content_metrics 
                        WHERE creator_id = $1 
                        AND DATE(created_at) BETWEEN $2 AND $3
                    """, creator_id, start_date, end_date)
                    
                elif category == ROICategory.ADVERTISING_SPEND:
                    # Get advertising spend data
                    result = await conn.fetchrow("""
                        SELECT COALESCE(SUM(ad_spend), 0) as total_investment
                        FROM advertising_campaigns 
                        WHERE creator_id = $1 
                        AND DATE(campaign_date) BETWEEN $2 AND $3
                    """, creator_id, start_date, end_date)
                    
                elif category == ROICategory.EQUIPMENT_INVESTMENT:
                    # Get equipment investment (amortized over usage period)
                    result = await conn.fetchrow("""
                        SELECT COALESCE(SUM(equipment_cost * usage_ratio), 0) as total_investment
                        FROM equipment_usage 
                        WHERE creator_id = $1 
                        AND DATE(usage_date) BETWEEN $2 AND $3
                    """, creator_id, start_date, end_date)
                    
                elif category == ROICategory.TIME_INVESTMENT:
                    # Calculate time investment costs (hours * hourly_rate)
                    result = await conn.fetchrow("""
                        SELECT COALESCE(SUM(hours_spent * hourly_rate), 0) as total_investment
                        FROM time_tracking 
                        WHERE creator_id = $1 
                        AND DATE(work_date) BETWEEN $2 AND $3
                    """, creator_id, start_date, end_date)
                    
                elif category == ROICategory.PLATFORM_FEES:
                    # Get platform fees
                    result = await conn.fetchrow("""
                        SELECT COALESCE(SUM(platform_fees), 0) as total_investment
                        FROM revenue_streams 
                        WHERE creator_id = $1 
                        AND DATE(transaction_date) BETWEEN $2 AND $3
                    """, creator_id, start_date, end_date)
                    
                elif category == ROICategory.COLLABORATION:
                    # Get collaboration costs
                    result = await conn.fetchrow("""
                        SELECT COALESCE(SUM(collaboration_cost), 0) as total_investment
                        FROM collaborations 
                        WHERE creator_id = $1 
                        AND DATE(collaboration_date) BETWEEN $2 AND $3
                    """, creator_id, start_date, end_date)
                    
                else:
                    return 0.0
                
                return float(result['total_investment']) if result else 0.0
                
        except Exception as e:
            logger.error(f"Failed to get investment amount: {e}")
            return 0.0

    async def _get_revenue_generated(self, creator_id: str, category: ROICategory, start_date: datetime.date, end_date: datetime.date) -> float:
        """Get revenue generated for specific category and timeframe"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get total revenue for the timeframe
                result = await conn.fetchrow("""
                    SELECT COALESCE(SUM(revenue_amount), 0) as total_revenue
                    FROM revenue_streams 
                    WHERE creator_id = $1 
                    AND DATE(transaction_date) BETWEEN $2 AND $3
                """, creator_id, start_date, end_date)
                
                total_revenue = float(result['total_revenue']) if result else 0.0
                
                # Apply category-specific revenue attribution
                if category == ROICategory.CONTENT_CREATION:
                    # 70% of revenue attributed to content creation
                    return total_revenue * 0.70
                elif category == ROICategory.ADVERTISING_SPEND:
                    # Get direct advertising revenue
                    ad_result = await conn.fetchrow("""
                        SELECT COALESCE(SUM(ad_revenue), 0) as ad_revenue
                        FROM advertising_campaigns 
                        WHERE creator_id = $1 
                        AND DATE(campaign_date) BETWEEN $2 AND $3
                    """, creator_id, start_date, end_date)
                    return float(ad_result['ad_revenue']) if ad_result else 0.0
                elif category == ROICategory.EQUIPMENT_INVESTMENT:
                    # 20% of revenue attributed to equipment quality
                    return total_revenue * 0.20
                elif category == ROICategory.TIME_INVESTMENT:
                    # 80% of revenue attributed to time investment
                    return total_revenue * 0.80
                elif category == ROICategory.PLATFORM_FEES:
                    # Platform fees reduce revenue, so return negative impact
                    return total_revenue * 0.90  # Assume 10% platform fee impact
                elif category == ROICategory.COLLABORATION:
                    # Get collaboration-specific revenue
                    collab_result = await conn.fetchrow("""
                        SELECT COALESCE(SUM(collaboration_revenue), 0) as collab_revenue
                        FROM collaborations 
                        WHERE creator_id = $1 
                        AND DATE(collaboration_date) BETWEEN $2 AND $3
                    """, creator_id, start_date, end_date)
                    return float(collab_result['collab_revenue']) if collab_result else 0.0
                
                return total_revenue
                
        except Exception as e:
            logger.error(f"Failed to get revenue generated: {e}")
            return 0.0

    async def _get_total_engagements(self, creator_id: str, start_date: datetime.date, end_date: datetime.date) -> int:
        """Get total engagements for timeframe"""
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT COALESCE(SUM(total_engagements), 0) as total_engagements
                    FROM content_metrics 
                    WHERE creator_id = $1 
                    AND DATE(created_at) BETWEEN $2 AND $3
                """, creator_id, start_date, end_date)
                
                return int(result['total_engagements']) if result else 0
                
        except Exception as e:
            logger.error(f"Failed to get total engagements: {e}")
            return 0

    async def _get_total_conversions(self, creator_id: str, start_date: datetime.date, end_date: datetime.date) -> int:
        """Get total conversions for timeframe"""
        try:
            async with self.db_pool.acquire() as conn:
                result = await conn.fetchrow("""
                    SELECT COALESCE(SUM(conversions), 0) as total_conversions
                    FROM content_metrics 
                    WHERE creator_id = $1 
                    AND DATE(created_at) BETWEEN $2 AND $3
                """, creator_id, start_date, end_date)
                
                return int(result['total_conversions']) if result else 0
                
        except Exception as e:
            logger.error(f"Failed to get total conversions: {e}")
            return 0

    def _calculate_efficiency_score(self, roi_percentage: float, cost_per_engagement: float, cost_per_conversion: float) -> float:
        """Calculate overall efficiency score"""
        try:
            # Normalize ROI percentage to 0-1 scale
            roi_score = min(max((roi_percentage + 100) / 200, 0), 1)  # -100% to 100% -> 0 to 1
            
            # Engagement efficiency (lower cost per engagement is better)
            engagement_score = 1 / (1 + cost_per_engagement) if cost_per_engagement > 0 else 1
            
            # Conversion efficiency (lower cost per conversion is better)
            conversion_score = 1 / (1 + cost_per_conversion / 10) if cost_per_conversion > 0 else 1
            
            # Weighted average
            efficiency_score = (roi_score * 0.5 + engagement_score * 0.3 + conversion_score * 0.2) * 100
            
            return round(efficiency_score, 2)
            
        except Exception as e:
            logger.error(f"Failed to calculate efficiency score: {e}")
            return 50.0  # Default middle score

    def _generate_optimization_recommendations(self, category: ROICategory, roi_percentage: float, 
                                             cost_per_engagement: float, cost_per_conversion: float, 
                                             efficiency_score: float) -> List[str]:
        """Generate optimization recommendations based on ROI analysis"""
        recommendations = []
        
        try:
            # ROI-based recommendations
            if roi_percentage < 0:
                recommendations.append("Negative ROI detected - review and optimize spending strategies")
            elif roi_percentage < 20:
                recommendations.append("ROI below 20% - consider cost reduction or revenue enhancement")
            elif roi_percentage > 100:
                recommendations.append("Excellent ROI - consider scaling successful strategies")
            
            # Category-specific recommendations
            if category == ROICategory.CONTENT_CREATION:
                if cost_per_engagement > 0.5:
                    recommendations.append("High cost per engagement - optimize content for better audience response")
                if efficiency_score < 60:
                    recommendations.append("Focus on content quality and audience targeting")
                recommendations.append("Test different content formats to improve engagement efficiency")
                
            elif category == ROICategory.ADVERTISING_SPEND:
                if cost_per_conversion > 50:
                    recommendations.append("High cost per conversion - refine ad targeting and messaging")
                if roi_percentage < 200:
                    recommendations.append("Ad ROI below optimal - A/B test ad creatives and audiences")
                recommendations.append("Consider reallocating budget to best-performing ad sets")
                
            elif category == ROICategory.TIME_INVESTMENT:
                if efficiency_score < 70:
                    recommendations.append("Time efficiency low - implement productivity tools and workflows")
                recommendations.append("Focus on high-impact activities that drive revenue")
                
            elif category == ROICategory.EQUIPMENT_INVESTMENT:
                if roi_percentage < 50:
                    recommendations.append("Equipment ROI low - maximize usage of existing equipment")
                recommendations.append("Consider equipment rental for occasional high-end needs")
                
            # General efficiency recommendations
            if efficiency_score < 50:
                recommendations.append("Overall efficiency below average - comprehensive strategy review needed")
            elif efficiency_score > 80:
                recommendations.append("High efficiency achieved - maintain current strategies and scale")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate optimization recommendations: {e}")
            return ["Review performance metrics and adjust strategies accordingly"]

    async def _store_roi_calculation(self, roi_data: ROIData) -> None:
        """Store ROI calculation in database"""
        try:
            # Calculate period dates
            end_date = datetime.now().date()
            start_date = self._get_timeframe_start_date(end_date, roi_data.timeframe)
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO roi_calculations 
                    (creator_id, category, timeframe, investment_amount, revenue_generated,
                     roi_percentage, roi_absolute, cost_per_engagement, cost_per_conversion,
                     efficiency_score, optimization_recommendations, calculation_period_start,
                     calculation_period_end)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """,
                roi_data.creator_id,
                roi_data.category.value,
                roi_data.timeframe.value,
                roi_data.investment_amount,
                roi_data.revenue_generated,
                roi_data.roi_percentage,
                roi_data.roi_absolute,
                roi_data.cost_per_engagement,
                roi_data.cost_per_conversion,
                roi_data.efficiency_score,
                roi_data.optimization_recommendations,
                start_date,
                end_date
                )
        except Exception as e:
            logger.error(f"Failed to store ROI calculation: {e}")

    async def get_roi_dashboard_data(self, creator_id: str) -> Dict[str, Any]:
        """Get comprehensive ROI dashboard data"""
        try:
            # Calculate current month ROI
            monthly_roi = await self.calculate_comprehensive_roi(creator_id, ROITimeframe.MONTHLY)
            
            # Get historical ROI trends
            historical_data = await self._get_historical_roi_trends(creator_id)
            
            # Calculate ROI summary
            total_investment = sum(roi.investment_amount for roi in monthly_roi)
            total_revenue = sum(roi.revenue_generated for roi in monthly_roi)
            overall_roi = ((total_revenue - total_investment) / total_investment * 100) if total_investment > 0 else 0
            
            # Get best and worst performing categories
            monthly_roi.sort(key=lambda x: x.roi_percentage, reverse=True)
            best_category = monthly_roi[0] if monthly_roi else None
            worst_category = monthly_roi[-1] if monthly_roi else None
            
            dashboard_data = {
                'roi_summary': {
                    'overall_roi_percentage': round(overall_roi, 2),
                    'total_investment': round(total_investment, 2),
                    'total_revenue': round(total_revenue, 2),
                    'net_profit': round(total_revenue - total_investment, 2)
                },
                'category_performance': [
                    {
                        'category': roi.category.value,
                        'roi_percentage': round(roi.roi_percentage, 2),
                        'investment': round(roi.investment_amount, 2),
                        'revenue': round(roi.revenue_generated, 2),
                        'efficiency_score': roi.efficiency_score,
                        'recommendations': roi.optimization_recommendations[:3]  # Top 3 recommendations
                    }
                    for roi in monthly_roi
                ],
                'performance_insights': {
                    'best_performing_category': {
                        'category': best_category.category.value if best_category else None,
                        'roi_percentage': round(best_category.roi_percentage, 2) if best_category else 0
                    },
                    'worst_performing_category': {
                        'category': worst_category.category.value if worst_category else None,
                        'roi_percentage': round(worst_category.roi_percentage, 2) if worst_category else 0
                    },
                    'avg_efficiency_score': round(np.mean([roi.efficiency_score for roi in monthly_roi]), 2) if monthly_roi else 0
                },
                'historical_trends': historical_data,
                'generated_at': datetime.now().isoformat()
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Failed to get ROI dashboard data: {e}")
            raise HTTPException(status_code=500, detail="ROI dashboard data retrieval failed")

    async def _get_historical_roi_trends(self, creator_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get historical ROI trends for the past 6 months"""
        try:
            async with self.db_pool.acquire() as conn:
                # Get monthly ROI trends for past 6 months
                monthly_trends = await conn.fetch("""
                    SELECT 
                        DATE_TRUNC('month', calculated_at) as month,
                        category,
                        AVG(roi_percentage) as avg_roi,
                        AVG(efficiency_score) as avg_efficiency
                    FROM roi_calculations 
                    WHERE creator_id = $1 
                    AND calculated_at >= NOW() - INTERVAL '6 months'
                    GROUP BY DATE_TRUNC('month', calculated_at), category
                    ORDER BY month DESC, avg_roi DESC
                """, creator_id)
                
                # Organize data by month
                trends_by_month = {}
                for trend in monthly_trends:
                    month_key = trend['month'].strftime('%Y-%m')
                    if month_key not in trends_by_month:
                        trends_by_month[month_key] = []
                    
                    trends_by_month[month_key].append({
                        'category': trend['category'],
                        'avg_roi': round(float(trend['avg_roi']), 2),
                        'avg_efficiency': round(float(trend['avg_efficiency']), 2)
                    })
                
                return trends_by_month
                
        except Exception as e:
            logger.error(f"Failed to get historical ROI trends: {e}")
            return {}
