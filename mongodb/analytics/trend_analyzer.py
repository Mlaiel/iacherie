"""MongoDB Trend Analyzer
=======================

Trend analysis and forecasting for business metrics.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from pymongo import MongoClient
import numpy as np

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """Advanced trend analysis and forecasting."""
    
    def __init__(self, client: MongoClient, database_name: str):
        """Initialize trend analyzer."""
        self.client = client
        self.database = client[database_name]
    
    def analyze_user_growth_trend(self, days_back: int = 30) -> Dict[str, Any]:
        """Analyze user growth trend over specified period."""
        try:
            daily_data = []
            
            for i in range(days_back, 0, -1):
                date = datetime.utcnow() - timedelta(days=i)
                start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1)
                
                user_count = self.database.users.count_documents({
                    'createdAt': {
                        '$gte': start_of_day,
                        '$lt': end_of_day
                    }
                })
                
                daily_data.append({
                    'date': start_of_day.isoformat(),
                    'new_users': user_count
                })
            
            # Calculate trend direction
            if len(daily_data) >= 7:
                recent_avg = sum(d['new_users'] for d in daily_data[-7:]) / 7
                previous_avg = sum(d['new_users'] for d in daily_data[-14:-7]) / 7
                
                trend_direction = 'increasing' if recent_avg > previous_avg else 'decreasing'
                trend_strength = abs(recent_avg - previous_avg) / previous_avg if previous_avg > 0 else 0
            else:
                trend_direction = 'stable'
                trend_strength = 0
            
            return {
                'period_days': days_back,
                'daily_data': daily_data,
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'total_new_users': sum(d['new_users'] for d in daily_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze user growth trend: {e}")
            return {}
    
    def forecast_metric(self, metric_name: str, historical_data: List[float],
                       forecast_days: int = 7) -> List[float]:
        """Simple linear forecast for metric values."""
        try:
            if len(historical_data) < 3:
                return [historical_data[-1]] * forecast_days if historical_data else [0] * forecast_days
            
            # Simple linear regression
            x = np.arange(len(historical_data))
            y = np.array(historical_data)
            
            # Calculate slope and intercept
            slope = np.sum((x - np.mean(x)) * (y - np.mean(y))) / np.sum((x - np.mean(x)) ** 2)
            intercept = np.mean(y) - slope * np.mean(x)
            
            # Generate forecast
            forecast = []
            for i in range(forecast_days):
                future_x = len(historical_data) + i
                predicted_value = slope * future_x + intercept
                forecast.append(max(0, predicted_value))  # Ensure non-negative
            
            return forecast
            
        except Exception as e:
            logger.error(f"Failed to forecast metric {metric_name}: {e}")
            return [0] * forecast_days

__all__ = ['TrendAnalyzer']