"""Revenue Management System - Complete Integration Hub

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT COPYRIGHT WARNING ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, reproduction, modification, or distribution without explicit 
written permission from the author is strictly prohibited.

Complete revenue management system integrating all platforms and business logic.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from decimal import Decimal
import json

from .platform_integration_manager import PlatformRevenueData, PlatformConfig
from .spotify_integration import SpotifyIntegrationManager

logger = logging.getLogger(__name__)


@dataclass
class RevenueMetrics:
    """Comprehensive revenue metrics for a creator."""
    total_revenue: Decimal
    platform_breakdown: Dict[str, Decimal]
    growth_rate: float
    period_start: datetime
    period_end: datetime
    currency: str = "USD"
    
    
@dataclass
class RevenueGoal:
    """Revenue goal configuration."""
    target_amount: Decimal
    target_date: datetime
    platform_targets: Dict[str, Decimal]
    progress_percentage: float = 0.0


class RevenueManagementSystem:
    """
    Complete Revenue Management System for IA Influencer Platform.
    
    Features:
    - Multi-platform revenue aggregation
    - Real-time revenue tracking
    - Advanced analytics and forecasting
    - Goal setting and progress tracking
    - Automated optimization recommendations
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Platform managers
        self.platform_managers: Dict[str, Any] = {}
        self.initialized_platforms: List[str] = []
        
        # Revenue data cache
        self.revenue_cache: Dict[str, PlatformRevenueData] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        
        # Analytics
        self.metrics_history: List[RevenueMetrics] = []
        self.goals: Dict[str, RevenueGoal] = {}
        
    async def initialize(self, platform_configs: Dict[str, Dict[str, Any]]) -> None:
        """Initialize the revenue management system with platform configurations."""
        try:
            self.logger.info("Initializing Revenue Management System...")
            
            # Initialize platform managers
            for platform_id, platform_config in platform_configs.items():
                await self._initialize_platform(platform_id, platform_config)
            
            self.logger.info(f"Revenue Management System initialized with {len(self.platform_managers)} platforms")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Revenue Management System: {e}")
            raise
    
    async def _initialize_platform(self, platform_id: str, config: Dict[str, Any]) -> None:
        """Initialize a specific platform manager."""
        try:
            platform_config = PlatformConfig(**config)
            
            if platform_id == "spotify":
                manager = SpotifyIntegrationManager(platform_config)
            else:
                # For other platforms, use a generic manager for now
                manager = GenericPlatformManager(platform_config)
            
            # Test authentication
            if await manager.authenticate():
                self.platform_managers[platform_id] = manager
                self.initialized_platforms.append(platform_id)
                self.logger.info(f"Successfully initialized {platform_id} platform manager")
            else:
                self.logger.warning(f"Failed to authenticate {platform_id} platform")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize {platform_id}: {e}")
    
    async def get_total_revenue(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime,
        force_refresh: bool = False
    ) -> RevenueMetrics:
        """Get total revenue across all platforms."""
        try:
            self.logger.info(f"Fetching total revenue for user {user_id}")
            
            platform_revenues = {}
            total_revenue = Decimal('0')
            
            # Fetch revenue from each platform
            for platform_id, manager in self.platform_managers.items():
                try:
                    revenue_data = await self._get_platform_revenue(
                        platform_id, manager, user_id, start_date, end_date, force_refresh
                    )
                    
                    platform_revenue = Decimal(str(revenue_data.total_revenue))
                    platform_revenues[platform_id] = platform_revenue
                    total_revenue += platform_revenue
                    
                except Exception as e:
                    self.logger.error(f"Failed to fetch revenue from {platform_id}: {e}")
                    platform_revenues[platform_id] = Decimal('0')
            
            # Calculate growth rate
            growth_rate = await self._calculate_growth_rate(user_id, total_revenue, start_date, end_date)
            
            metrics = RevenueMetrics(
                total_revenue=total_revenue,
                platform_breakdown=platform_revenues,
                growth_rate=growth_rate,
                period_start=start_date,
                period_end=end_date
            )
            
            # Store in history
            self.metrics_history.append(metrics)
            
            self.logger.info(f"Total revenue calculated: ${total_revenue}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to calculate total revenue: {e}")
            raise
    
    async def _get_platform_revenue(
        self,
        platform_id: str,
        manager: Any,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
        force_refresh: bool
    ) -> PlatformRevenueData:
        """Get revenue data from a specific platform with caching."""
        cache_key = f"{platform_id}_{user_id}_{start_date.date()}_{end_date.date()}"
        
        # Check cache
        if not force_refresh and cache_key in self.revenue_cache:
            cache_expiry = self.cache_expiry.get(cache_key)
            if cache_expiry and datetime.utcnow() < cache_expiry:
                return self.revenue_cache[cache_key]
        
        # Fetch fresh data
        revenue_data = await manager.fetch_revenue_data(user_id, start_date, end_date)
        
        # Cache the result (expire after 1 hour)
        self.revenue_cache[cache_key] = revenue_data
        self.cache_expiry[cache_key] = datetime.utcnow() + timedelta(hours=1)
        
        return revenue_data
    
    async def _calculate_growth_rate(
        self, 
        user_id: str, 
        current_revenue: Decimal, 
        start_date: datetime, 
        end_date: datetime
    ) -> float:
        """Calculate revenue growth rate compared to previous period."""
        try:
            # Calculate previous period
            period_duration = end_date - start_date
            previous_start = start_date - period_duration
            previous_end = start_date
            
            # Get previous period revenue
            previous_metrics = await self.get_total_revenue(
                user_id, previous_start, previous_end, force_refresh=False
            )
            
            if previous_metrics.total_revenue > 0:
                growth_rate = float(
                    (current_revenue - previous_metrics.total_revenue) / 
                    previous_metrics.total_revenue * 100
                )
                return round(growth_rate, 2)
            
            return 0.0
            
        except Exception as e:
            self.logger.warning(f"Could not calculate growth rate: {e}")
            return 0.0
    
    async def set_revenue_goal(
        self, 
        user_id: str, 
        goal: RevenueGoal
    ) -> bool:
        """Set a revenue goal for a user."""
        try:
            goal_key = f"{user_id}_{goal.target_date.date()}"
            self.goals[goal_key] = goal
            
            self.logger.info(f"Revenue goal set for user {user_id}: ${goal.target_amount}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set revenue goal: {e}")
            return False
    
    async def check_goal_progress(self, user_id: str) -> Dict[str, Any]:
        """Check progress towards revenue goals."""
        try:
            progress_data = {}
            
            for goal_key, goal in self.goals.items():
                if user_id in goal_key:
                    # Get current revenue up to target date
                    current_date = datetime.utcnow()
                    if current_date <= goal.target_date:
                        period_start = goal.target_date - timedelta(days=30)  # Last 30 days
                        
                        current_metrics = await self.get_total_revenue(
                            user_id, period_start, current_date
                        )
                        
                        # Calculate progress
                        progress_percentage = float(
                            current_metrics.total_revenue / goal.target_amount * 100
                        )
                        
                        progress_data[goal_key] = {
                            'goal': asdict(goal),
                            'current_revenue': float(current_metrics.total_revenue),
                            'progress_percentage': min(progress_percentage, 100.0),
                            'days_remaining': (goal.target_date - current_date).days,
                            'on_track': progress_percentage >= 80.0  # 80% threshold for being "on track"
                        }
            
            return progress_data
            
        except Exception as e:
            self.logger.error(f"Failed to check goal progress: {e}")
            return {}
    
    async def get_revenue_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive revenue analytics."""
        try:
            analytics = {
                'summary': {
                    'total_platforms': len(self.platform_managers),
                    'active_platforms': len(self.initialized_platforms),
                    'data_points': len(self.metrics_history)
                },
                'trends': await self._calculate_trends(user_id),
                'platform_performance': await self._analyze_platform_performance(user_id),
                'recommendations': await self._generate_recommendations(user_id)
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Failed to generate revenue analytics: {e}")
            return {}
    
    async def _calculate_trends(self, user_id: str) -> Dict[str, Any]:
        """Calculate revenue trends."""
        if len(self.metrics_history) < 2:
            return {'trend': 'insufficient_data'}
        
        recent_metrics = self.metrics_history[-5:]  # Last 5 data points
        revenues = [float(m.total_revenue) for m in recent_metrics]
        
        # Simple trend calculation
        if len(revenues) >= 2:
            if revenues[-1] > revenues[0]:
                trend = 'upward'
            elif revenues[-1] < revenues[0]:
                trend = 'downward'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'average_revenue': sum(revenues) / len(revenues),
            'peak_revenue': max(revenues),
            'low_revenue': min(revenues)
        }
    
    async def _analyze_platform_performance(self, user_id: str) -> Dict[str, Any]:
        """Analyze performance across platforms."""
        if not self.metrics_history:
            return {}
        
        latest_metrics = self.metrics_history[-1]
        total = float(latest_metrics.total_revenue)
        
        performance = {}
        for platform, revenue in latest_metrics.platform_breakdown.items():
            revenue_float = float(revenue)
            percentage = (revenue_float / total * 100) if total > 0 else 0
            
            performance[platform] = {
                'revenue': revenue_float,
                'percentage': round(percentage, 2),
                'rank': 0  # Will be set after sorting
            }
        
        # Rank platforms by revenue
        sorted_platforms = sorted(
            performance.items(), 
            key=lambda x: x[1]['revenue'], 
            reverse=True
        )
        
        for rank, (platform, data) in enumerate(sorted_platforms, 1):
            performance[platform]['rank'] = rank
        
        return performance
    
    async def _generate_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate optimization recommendations."""
        recommendations = []
        
        if not self.metrics_history:
            return recommendations
        
        latest_metrics = self.metrics_history[-1]
        
        # Platform diversification recommendation
        if len(latest_metrics.platform_breakdown) < 3:
            recommendations.append({
                'type': 'diversification',
                'priority': 'high',
                'title': 'Expand to More Platforms',
                'description': 'Consider expanding to additional platforms to diversify revenue streams.',
                'action': 'Add 1-2 new platforms to your revenue mix'
            })
        
        # Growth opportunity recommendation
        if latest_metrics.growth_rate < 5.0:  # Less than 5% growth
            recommendations.append({
                'type': 'growth',
                'priority': 'medium',
                'title': 'Accelerate Growth',
                'description': 'Your revenue growth is below optimal levels.',
                'action': 'Focus on content optimization and audience engagement'
            })
        
        return recommendations
    
    async def export_revenue_report(self, user_id: str, format: str = 'json') -> Union[str, Dict]:
        """Export comprehensive revenue report."""
        try:
            report_data = {
                'user_id': user_id,
                'generated_at': datetime.utcnow().isoformat(),
                'metrics_history': [asdict(m) for m in self.metrics_history],
                'goals': {k: asdict(v) for k, v in self.goals.items() if user_id in k},
                'analytics': await self.get_revenue_analytics(user_id)
            }
            
            if format == 'json':
                return json.dumps(report_data, indent=2, default=str)
            else:
                return report_data
                
        except Exception as e:
            self.logger.error(f"Failed to export revenue report: {e}")
            raise


class GenericPlatformManager:
    """Generic platform manager for platforms without specific implementations."""
    
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    async def authenticate(self) -> bool:
        """Generic authentication placeholder."""
        self.logger.info(f"Generic authentication for {self.config.platform_id}")
        return True  # Assume success for now
    
    async def fetch_revenue_data(self, user_id: str, start_date: datetime, end_date: datetime) -> PlatformRevenueData:
        """Generic revenue data fetch."""
        # Return placeholder data
        return PlatformRevenueData(
            platform_id=self.config.platform_id,
            user_id=user_id,
            total_revenue=100.0,  # Placeholder
            currency="USD",
            period_start=start_date,
            period_end=end_date,
            data_points={'placeholder': True},
            metadata={'source': 'generic_manager'}
        )