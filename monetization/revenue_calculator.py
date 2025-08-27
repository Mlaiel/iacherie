"""
Revenue Calculator
Automated revenue calculation for different platforms.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class RevenueData:
    """Revenue data structure"""
    platform: str
    content_id: str
    views: int
    engagement_rate: float
    revenue: float
    currency: str = "EUR"
    period_start: datetime = None
    period_end: datetime = None


class RevenueCalculator:
    """Automated revenue calculation engine"""
    
    # Platform-specific CPM and conversion rates
    PLATFORM_RATES = {
        "youtube": {
            "cpm_min": 0.25,
            "cpm_max": 4.0,
            "engagement_multiplier": 1.5,
            "monetization_threshold": 1000  # subscribers
        },
        "instagram": {
            "cpm_min": 0.50,
            "cpm_max": 6.0, 
            "engagement_multiplier": 2.0,
            "monetization_threshold": 1000  # followers
        },
        "tiktok": {
            "cpm_min": 0.02,
            "cpm_max": 0.04,
            "creator_fund_rate": 0.02,
            "monetization_threshold": 10000  # followers
        },
        "spotify": {
            "per_stream": 0.003,
            "premium_multiplier": 1.5,
            "royalty_rate": 0.70
        },
        "twitter": {
            "cpm_min": 0.38,
            "cpm_max": 2.0,
            "super_follows_rate": 0.97
        }
    }
    
    def __init__(self):
        self.cache = {}
        
    async def calculate_youtube_revenue(
        self, 
        views: int, 
        watch_time_hours: float,
        engagement_rate: float,
        subscriber_count: int,
        country: str = "US"
    ) -> float:
        """Calculate YouTube revenue based on views and engagement"""
        try:
            if subscriber_count < self.PLATFORM_RATES["youtube"]["monetization_threshold"]:
                return 0.0
                
            # Base CPM calculation
            country_multiplier = self._get_country_cpm_multiplier(country)
            base_cpm = self.PLATFORM_RATES["youtube"]["cpm_min"] * country_multiplier
            
            # Engagement bonus
            if engagement_rate > 0.05:  # 5% engagement rate
                base_cpm *= self.PLATFORM_RATES["youtube"]["engagement_multiplier"]
                
            # Watch time bonus
            if watch_time_hours > 4000:  # 4000 hours threshold
                base_cpm *= 1.2
                
            revenue = (views / 1000) * base_cpm
            logger.info(f"YouTube revenue calculated: {revenue:.2f} EUR for {views} views")
            return revenue
            
        except Exception as e:
            logger.error(f"Error calculating YouTube revenue: {str(e)}")
            return 0.0
    
    async def calculate_instagram_revenue(
        self,
        impressions: int,
        reach: int, 
        engagement_rate: float,
        story_views: int,
        follower_count: int
    ) -> float:
        """Calculate Instagram revenue from impressions and engagement"""
        try:
            if follower_count < self.PLATFORM_RATES["instagram"]["monetization_threshold"]:
                return 0.0
                
            # Calculate effective CPM based on engagement
            base_cpm = self.PLATFORM_RATES["instagram"]["cpm_min"]
            
            if engagement_rate > 0.03:  # 3% engagement rate
                base_cpm *= self.PLATFORM_RATES["instagram"]["engagement_multiplier"]
                
            # Story bonus
            if story_views > reach * 0.1:  # 10% story view rate
                base_cpm *= 1.1
                
            revenue = (impressions / 1000) * base_cpm
            logger.info(f"Instagram revenue calculated: {revenue:.2f} EUR for {impressions} impressions")
            return revenue
            
        except Exception as e:
            logger.error(f"Error calculating Instagram revenue: {str(e)}")
            return 0.0
    
    async def calculate_tiktok_revenue(
        self,
        views: int,
        shares: int,
        likes: int,
        follower_count: int,
        in_creator_fund: bool = True
    ) -> float:
        """Calculate TikTok revenue from Creator Fund and engagement"""
        try:
            if follower_count < self.PLATFORM_RATES["tiktok"]["monetization_threshold"]:
                return 0.0
                
            revenue = 0.0
            
            if in_creator_fund:
                # Creator Fund revenue (very low rate)
                fund_revenue = views * self.PLATFORM_RATES["tiktok"]["creator_fund_rate"]
                revenue += fund_revenue
                
            # Engagement bonus (for brand partnerships estimation)
            engagement_rate = (likes + shares) / max(views, 1)
            if engagement_rate > 0.05:  # 5% engagement
                bonus = views * 0.001  # Estimated brand partnership value
                revenue += bonus
                
            logger.info(f"TikTok revenue calculated: {revenue:.2f} EUR for {views} views")
            return revenue
            
        except Exception as e:
            logger.error(f"Error calculating TikTok revenue: {str(e)}")
            return 0.0
    
    async def calculate_spotify_revenue(
        self,
        streams: int,
        premium_streams: int,
        country_distribution: Dict[str, int]
    ) -> float:
        """Calculate Spotify revenue from streams"""
        try:
            base_rate = self.PLATFORM_RATES["spotify"]["per_stream"]
            
            # Premium streams earn more
            premium_revenue = premium_streams * base_rate * self.PLATFORM_RATES["spotify"]["premium_multiplier"]
            free_revenue = (streams - premium_streams) * base_rate
            
            # Country-based adjustments
            total_revenue = premium_revenue + free_revenue
            
            # Apply royalty rate (artist gets ~70%)
            artist_revenue = total_revenue * self.PLATFORM_RATES["spotify"]["royalty_rate"]
            
            logger.info(f"Spotify revenue calculated: {artist_revenue:.2f} EUR for {streams} streams")
            return artist_revenue
            
        except Exception as e:
            logger.error(f"Error calculating Spotify revenue: {str(e)}")
            return 0.0
    
    async def predict_revenue_ml(
        self,
        platform: str,
        historical_data: List[RevenueData],
        forecast_days: int = 30
    ) -> List[float]:
        """ML-based revenue prediction (simplified implementation)"""
        try:
            if not historical_data:
                return [0.0] * forecast_days
                
            # Simple trend analysis
            recent_revenues = [data.revenue for data in historical_data[-30:]]
            
            if len(recent_revenues) < 7:
                # Not enough data, return average
                avg_revenue = sum(recent_revenues) / len(recent_revenues)
                return [avg_revenue] * forecast_days
                
            # Calculate trend
            mid_point = len(recent_revenues) // 2
            early_avg = sum(recent_revenues[:mid_point]) / mid_point
            late_avg = sum(recent_revenues[mid_point:]) / (len(recent_revenues) - mid_point)
            
            trend = (late_avg - early_avg) / mid_point
            
            # Project forward
            last_revenue = recent_revenues[-1]
            predictions = []
            
            for day in range(forecast_days):
                predicted = last_revenue + (trend * day)
                predicted = max(0, predicted)  # Revenue can't be negative
                predictions.append(predicted)
                
            logger.info(f"Revenue prediction generated for {platform}: {len(predictions)} days")
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting revenue: {str(e)}")
            return [0.0] * forecast_days
    
    async def calculate_total_revenue(
        self,
        content_id: str,
        platform_data: Dict[str, Dict]
    ) -> Dict[str, float]:
        """Calculate total revenue across all platforms"""
        try:
            revenues = {}
            
            for platform, data in platform_data.items():
                if platform == "youtube":
                    revenue = await self.calculate_youtube_revenue(
                        data.get("views", 0),
                        data.get("watch_time_hours", 0),
                        data.get("engagement_rate", 0),
                        data.get("subscriber_count", 0),
                        data.get("country", "US")
                    )
                elif platform == "instagram":
                    revenue = await self.calculate_instagram_revenue(
                        data.get("impressions", 0),
                        data.get("reach", 0),
                        data.get("engagement_rate", 0),
                        data.get("story_views", 0),
                        data.get("follower_count", 0)
                    )
                elif platform == "tiktok":
                    revenue = await self.calculate_tiktok_revenue(
                        data.get("views", 0),
                        data.get("shares", 0),
                        data.get("likes", 0),
                        data.get("follower_count", 0),
                        data.get("in_creator_fund", True)
                    )
                elif platform == "spotify":
                    revenue = await self.calculate_spotify_revenue(
                        data.get("streams", 0),
                        data.get("premium_streams", 0),
                        data.get("country_distribution", {})
                    )
                else:
                    revenue = 0.0
                    
                revenues[platform] = revenue
                
            total = sum(revenues.values())
            revenues["total"] = total
            
            logger.info(f"Total revenue calculated for content {content_id}: {total:.2f} EUR")
            return revenues
            
        except Exception as e:
            logger.error(f"Error calculating total revenue: {str(e)}")
            return {"total": 0.0}
    
    def _get_country_cpm_multiplier(self, country: str) -> float:
        """Get CPM multiplier based on country"""
        multipliers = {
            "US": 1.0,
            "CA": 0.9,
            "GB": 0.8,
            "DE": 0.7,
            "FR": 0.7,
            "AU": 0.8,
            "JP": 0.6,
            "BR": 0.3,
            "IN": 0.1,
            "default": 0.5
        }
        return multipliers.get(country, multipliers["default"])
    
    async def get_real_time_revenue(self, content_id: str) -> Dict[str, float]:
        """Get real-time revenue estimates"""
        try:
            # This would integrate with platform APIs for real-time data
            # For now, return cached/estimated values
            
            cache_key = f"revenue_{content_id}_{datetime.now().strftime('%Y%m%d%H')}"
            
            if cache_key in self.cache:
                return self.cache[cache_key]
                
            # Simulate real-time calculation
            # In production, this would call platform APIs
            estimated_revenue = {
                "youtube": 12.45,
                "instagram": 8.30,
                "tiktok": 2.15,
                "spotify": 15.60,
                "total": 38.50
            }
            
            self.cache[cache_key] = estimated_revenue
            return estimated_revenue
            
        except Exception as e:
            logger.error(f"Error getting real-time revenue: {str(e)}")
            return {"total": 0.0}