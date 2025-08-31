"""
Revenue Tracker
Advanced revenue tracking and analytics system.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import logging
import statistics

logger = logging.getLogger(__name__)


@dataclass
class RevenueMetrics:
    """Revenue metrics data structure"""
    period_start: datetime
    period_end: datetime
    total_revenue: float
    platform_breakdown: Dict[str, float]
    content_breakdown: Dict[str, float]
    growth_rate: float
    average_per_day: float
    currency: str = "EUR"


class RevenueTracker:
    """Advanced revenue tracking and monitoring system"""
    
    def __init__(self):
        self.revenue_data = {}
        self.alerts = {}
        self.benchmarks = {}
        
    async def track_real_time_revenue(
        self,
        content_id: str,
        platform: str,
        revenue: float,
        currency: str = "EUR",
        metadata: Optional[Dict] = None
    ) -> bool:
        """Track real-time revenue updates"""



        try:
            timestamp = datetime.now()
            
            # Create revenue record
            revenue_record = {
                "content_id": content_id,
                "platform": platform,
                "revenue": revenue,
                "currency": currency,
                "timestamp": timestamp,
                "metadata": metadata or {}
            }
            
            # Store in time-series format
            date_key = timestamp.strftime("%Y-%m-%d")
            hour_key = timestamp.strftime("%H")
            
            if content_id not in self.revenue_data:
                self.revenue_data[content_id] = {}
                
            if date_key not in self.revenue_data[content_id]:
                self.revenue_data[content_id][date_key] = {}
                
            if hour_key not in self.revenue_data[content_id][date_key]:
                self.revenue_data[content_id][date_key][hour_key] = []
                
            self.revenue_data[content_id][date_key][hour_key].append(revenue_record)
            
            logger.info(f"Revenue tracked: {content_id} - {platform}: {revenue} {currency}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking revenue: {str(e)}")
            return False
    
    async def get_cross_platform_correlation(
        self,
        content_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Analyze revenue correlation across platforms"""



        try:
            platform_revenues = {}
            
            # Get revenue data for each platform
            content_data = self.revenue_data.get(content_id, {})
            
            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.strftime("%Y-%m-%d")
                daily_data = content_data.get(date_key, {})
                
                for hour_data in daily_data.values():
                    for record in hour_data:
                        platform = record["platform"]
                        revenue = record["revenue"]
                        
                        if platform not in platform_revenues:
                            platform_revenues[platform] = []
                        platform_revenues[platform].append(revenue)
                
                current_date += timedelta(days=1)
            
            # Calculate total revenue by platform
            platform_totals = {
                platform: sum(revenues)
                for platform, revenues in platform_revenues.items()
            }
            
            analysis = {
                "content_id": content_id,
                "period_start": start_date.isoformat(),
                "period_end": end_date.isoformat(),
                "platform_totals": platform_totals,
                "dominant_platform": max(platform_totals.items(), key=lambda x: x[1])[0] if platform_totals else None,
                "revenue_distribution": {
                    platform: total / sum(platform_totals.values()) if sum(platform_totals.values()) > 0 else 0
                    for platform, total in platform_totals.items()
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing cross-platform correlation: {str(e)}")
            return {}
    
    async def calculate_roi_per_content(
        self,
        content_id: str,
        production_cost: float,
        marketing_cost: float = 0.0,
        time_period_days: int = 30
    ) -> Dict[str, Any]:
        """Calculate ROI for specific content"""



        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=time_period_days)
            
            # Get total revenue for the period
            total_revenue = await self._get_content_revenue_sum(content_id, start_date, end_date)
            
            # Calculate costs
            total_costs = production_cost + marketing_cost
            
            # Calculate ROI
            if total_costs > 0:
                roi = ((total_revenue - total_costs) / total_costs) * 100
            else:
                roi = 0.0
            
            # Calculate daily averages
            daily_revenue = total_revenue / time_period_days if time_period_days > 0 else 0
            
            roi_analysis = {
                "content_id": content_id,
                "analysis_period_days": time_period_days,
                "total_revenue": total_revenue,
                "production_cost": production_cost,
                "marketing_cost": marketing_cost,
                "total_costs": total_costs,
                "net_profit": total_revenue - total_costs,
                "roi_percentage": roi,
                "daily_average_revenue": daily_revenue,
                "break_even_point_days": total_costs / daily_revenue if daily_revenue > 0 else float('inf'),
                "calculated_at": datetime.now().isoformat()
            }
            
            return roi_analysis
            
        except Exception as e:
            logger.error(f"Error calculating ROI: {str(e)}")
            return {}
    
    async def forecast_revenue_ml(
        self,
        content_id: str,
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """ML-based revenue forecasting"""



        try:
            # Get historical revenue data
            historical_data = await self._get_historical_revenue_data(content_id, days=90)
            
            if len(historical_data) < 7:
                return {"error": "Insufficient historical data for forecasting"}
            
            # Simple trend-based forecasting
            daily_revenues = [day["total"] for day in historical_data]
            
            # Calculate trend
            trend = self._calculate_linear_trend(daily_revenues)
            
            # Generate forecast
            last_revenue = daily_revenues[-1]
            forecast_data = []
            
            for day in range(1, forecast_days + 1):
                forecast = last_revenue + (trend * day)
                forecast_data.append({
                    "day": day,
                    "date": (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d"),
                    "forecast": max(0, forecast)  # Revenue can't be negative
                })
            
            total_forecast = sum(f["forecast"] for f in forecast_data)
            
            forecast_result = {
                "content_id": content_id,
                "forecast_period_days": forecast_days,
                "total_forecasted_revenue": total_forecast,
                "daily_forecasts": forecast_data,
                "trend_direction": "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable",
                "generated_at": datetime.now().isoformat()
            }
            
            return forecast_result
            
        except Exception as e:
            logger.error(f"Error forecasting revenue: {str(e)}")
            return {"error": str(e)}
    
    async def _get_content_revenue_sum(
        self,
        content_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> float:
        """Get total revenue sum for content in date range"""



        try:
            total = 0.0
            content_data = self.revenue_data.get(content_id, {})
            
            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.strftime("%Y-%m-%d")
                daily_data = content_data.get(date_key, {})
                
                for hour_data in daily_data.values():
                    for record in hour_data:
                        total += record["revenue"]
                
                current_date += timedelta(days=1)
            
            return total
            
        except Exception as e:
            logger.error(f"Error getting content revenue sum: {str(e)}")
            return 0.0
    
    async def _get_historical_revenue_data(
        self,
        content_id: str,
        days: int = 90
    ) -> List[Dict]:
        """Get historical daily revenue data"""



        try:
            daily_data = []
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            current_date = start_date
            while current_date <= end_date:
                date_key = current_date.strftime("%Y-%m-%d")
                daily_total = 0.0
                
                content_data = self.revenue_data.get(content_id, {})
                daily_records = content_data.get(date_key, {})
                
                for hour_data in daily_records.values():
                    for record in hour_data:
                        daily_total += record["revenue"]
                
                daily_data.append({
                    "date": date_key,
                    "total": daily_total
                })
                
                current_date += timedelta(days=1)
            
            return daily_data
            
        except Exception as e:
            logger.error(f"Error getting historical data: {str(e)}")
            return []
    
    def _calculate_linear_trend(self, data: List[float]) -> float:
        """Calculate linear trend from data"""



        try:
            if len(data) < 2:
                return 0.0
                
            n = len(data)
            x_sum = sum(range(n))
            y_sum = sum(data)
            xy_sum = sum(i * y for i, y in enumerate(data))
            x2_sum = sum(i ** 2 for i in range(n))
            
            slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum ** 2)
            return slope
            
        except Exception as e:
            logger.error(f"Error calculating trend: {str(e)}")
            return 0.0