"""
API Quota Manager Implementation
===============================

Advanced API quota management system for monitoring and controlling API usage.
Implements intelligent throttling, cost optimization, and usage analytics.

Team Expertise: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + 
Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

  CRITICAL WARNING 
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

Unauthorized copying or theft of this concept, code, or methodology 
will be prosecuted to the FULL EXTENT OF THE LAW under German and 
International Copyright Laws.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque
import time


class QuotaStatus(Enum):
    """API quota status levels"""
    AVAILABLE = "available"
    WARNING = "warning"
    CRITICAL = "critical"
    EXHAUSTED = "exhausted"
    SUSPENDED = "suspended"


class QuotaPeriod(Enum):
    """Quota reset periods"""
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"


@dataclass
class PlatformQuotas:
    """Quota configuration for a platform"""
    platform_name: str
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    requests_per_month: int
    cost_per_request: float = 0.0
    burst_allowance: int = 0
    priority_reserves: int = 0  # Reserved quota for high priority requests
    current_usage: Dict[str, int] = field(default_factory=lambda: {
        'minute': 0, 'hour': 0, 'day': 0, 'month': 0
    })
    reset_times: Dict[str, datetime] = field(default_factory=dict)
    is_active: bool = True


@dataclass
class QuotaAlert:
    """Alert for quota threshold breach"""
    alert_id: str
    platform: str
    quota_type: str  # requests, cost
    threshold_percentage: float
    current_usage: int
    limit: int
    timestamp: datetime
    severity: str  # info, warning, critical
    message: str


@dataclass
class UsageMetrics:
    """Usage metrics for analytics"""
    platform: str
    time_period: str
    requests_made: int
    requests_failed: int
    requests_throttled: int
    average_response_time: float
    cost_incurred: float
    efficiency_score: float
    timestamp: datetime


class APIQuotaManager:
    """
    Advanced API quota management system for monitoring and controlling API usage.
    
    Features:
    - Real-time quota monitoring
    - Intelligent request throttling
    - Cost tracking and optimization
    - Multi-platform quota management
    - Priority-based request handling
    - Predictive quota planning
    - Alert system for threshold breaches
    - Usage analytics and reporting
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Platform quota configurations
        self.platform_quotas: Dict[str, PlatformQuotas] = {}
        
        # Usage tracking
        self.usage_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.request_timestamps: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # Alert system
        self.quota_alerts: List[QuotaAlert] = []
        self.alert_thresholds = {
            'warning': 75.0,    # 75% of quota
            'critical': 90.0,   # 90% of quota
            'exhausted': 100.0  # 100% of quota
        }
        
        # Cost tracking
        self.cost_tracking = {
            'daily_costs': defaultdict(float),
            'monthly_costs': defaultdict(float),
            'cost_alerts': []
        }
        
        # Request queue for throttling
        self.request_queues: Dict[str, asyncio.Queue] = {}
        self.throttling_active: Dict[str, bool] = defaultdict(bool)
        
        # Analytics
        self.usage_metrics: List[UsageMetrics] = []
        self.performance_stats = defaultdict(lambda: {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'throttled_requests': 0,
            'average_response_time': 0.0,
            'total_cost': 0.0
        })
        
        # Predictive planning
        self.usage_predictions: Dict[str, Dict[str, float]] = {}
        
        # Initialize background tasks
        asyncio.create_task(self._quota_monitor_loop())
        asyncio.create_task(self._reset_quotas_loop())
    
    def register_platform(self, platform_name: str, 
                         quotas: Dict[str, int],
                         cost_per_request: float = 0.0,
                         burst_allowance: int = 0,
                         priority_reserves: int = 0):
        """
        Register a platform with its quota configuration.
        
        Args:
            platform_name: Name of the platform
            quotas: Dictionary with quota limits (per_minute, per_hour, per_day, per_month)
            cost_per_request: Cost per API request
            burst_allowance: Additional requests allowed in burst
            priority_reserves: Reserved quota for high priority requests
        """



        try:
            platform_quota = PlatformQuotas(
                platform_name=platform_name,
                requests_per_minute=quotas.get('per_minute', 60),
                requests_per_hour=quotas.get('per_hour', 3600),
                requests_per_day=quotas.get('per_day', 86400),
                requests_per_month=quotas.get('per_month', 2592000),
                cost_per_request=cost_per_request,
                burst_allowance=burst_allowance,
                priority_reserves=priority_reserves
            )
            
            # Initialize reset times
            now = datetime.utcnow()
            platform_quota.reset_times = {
                'minute': now + timedelta(minutes=1),
                'hour': now + timedelta(hours=1),
                'day': now + timedelta(days=1),
                'month': now + timedelta(days=30)
            }
            
            self.platform_quotas[platform_name] = platform_quota
            self.request_queues[platform_name] = asyncio.Queue()
            
            self.logger.info(f"Registered platform {platform_name} with quotas: {quotas}")
            
        except Exception as e:
            self.logger.error(f"Error registering platform {platform_name}: {str(e)}")
            raise
    
    async def request_quota(self, platform: str, 
                          requests_needed: int = 1,
                          priority: str = "normal") -> Tuple[bool, Optional[float]]:
        """
        Request quota for API calls with intelligent throttling.
        
        Args:
            platform: Platform name
            requests_needed: Number of requests needed
            priority: Request priority (low, normal, high, critical)
            
        Returns:
            Tuple of (allowed, suggested_delay_seconds)
        """



        try:
            if platform not in self.platform_quotas:
                self.logger.warning(f"Platform {platform} not registered")
                return False, None
            
            quota_config = self.platform_quotas[platform]
            
            if not quota_config.is_active:
                return False, None
            
            # Check if we have enough quota
            quota_available = await self._check_quota_availability(platform, requests_needed, priority)
            
            if quota_available:
                # Reserve the quota
                await self._consume_quota(platform, requests_needed)
                return True, None
            else:
                # Calculate suggested delay
                suggested_delay = await self._calculate_suggested_delay(platform, requests_needed)
                
                # Add to throttling queue if delay is reasonable
                if suggested_delay < 300:  # Less than 5 minutes
                    if not self.throttling_active[platform]:
                        asyncio.create_task(self._process_throttled_requests(platform))
                    
                    await self.request_queues[platform].put((requests_needed, priority, time.time()))
                    return False, suggested_delay
                else:
                    return False, None
                    
        except Exception as e:
            self.logger.error(f"Error requesting quota for {platform}: {str(e)}")
            return False, None
    
    async def check_quota_status(self, platform: str) -> Dict[str, Any]:
        """
        Check current quota status for a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Quota status information
        """



        try:
            if platform not in self.platform_quotas:
                return {'status': 'unknown', 'message': 'Platform not registered'}
            
            quota_config = self.platform_quotas[platform]
            current_time = datetime.utcnow()
            
            status_info = {
                'platform': platform,
                'status': QuotaStatus.AVAILABLE.value,
                'current_usage': quota_config.current_usage.copy(),
                'limits': {
                    'per_minute': quota_config.requests_per_minute,
                    'per_hour': quota_config.requests_per_hour,
                    'per_day': quota_config.requests_per_day,
                    'per_month': quota_config.requests_per_month
                },
                'remaining': {},
                'reset_times': {},
                'cost_incurred': 0.0,
                'efficiency_score': 0.0
            }
            
            # Calculate remaining quotas
            status_info['remaining'] = {
                'per_minute': max(0, quota_config.requests_per_minute - quota_config.current_usage['minute']),
                'per_hour': max(0, quota_config.requests_per_hour - quota_config.current_usage['hour']),
                'per_day': max(0, quota_config.requests_per_day - quota_config.current_usage['day']),
                'per_month': max(0, quota_config.requests_per_month - quota_config.current_usage['month'])
            }
            
            # Format reset times
            for period, reset_time in quota_config.reset_times.items():
                time_until_reset = (reset_time - current_time).total_seconds()
                status_info['reset_times'][period] = max(0, time_until_reset)
            
            # Determine overall status
            min_remaining_percentage = min(
                status_info['remaining']['per_minute'] / quota_config.requests_per_minute * 100,
                status_info['remaining']['per_hour'] / quota_config.requests_per_hour * 100,
                status_info['remaining']['per_day'] / quota_config.requests_per_day * 100,
                status_info['remaining']['per_month'] / quota_config.requests_per_month * 100
            )
            
            if min_remaining_percentage <= 0:
                status_info['status'] = QuotaStatus.EXHAUSTED.value
            elif min_remaining_percentage <= 10:
                status_info['status'] = QuotaStatus.CRITICAL.value
            elif min_remaining_percentage <= 25:
                status_info['status'] = QuotaStatus.WARNING.value
            
            # Calculate cost and efficiency
            total_requests = sum(quota_config.current_usage.values())
            status_info['cost_incurred'] = total_requests * quota_config.cost_per_request
            
            # Get efficiency score from performance stats
            platform_stats = self.performance_stats.get(platform, {})
            if platform_stats.get('total_requests', 0) > 0:
                status_info['efficiency_score'] = (
                    platform_stats['successful_requests'] / platform_stats['total_requests'] * 100
                )
            
            return status_info
            
        except Exception as e:
            self.logger.error(f"Error checking quota status for {platform}: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_usage_analytics(self, platform: str = None, 
                                time_range_hours: int = 24) -> Dict[str, Any]:
        """
        Get usage analytics for platforms.
        
        Args:
            platform: Specific platform or None for all platforms
            time_range_hours: Time range for analytics
            
        Returns:
            Analytics data
        """



        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_range_hours)
            
            analytics = {
                'time_range_hours': time_range_hours,
                'platforms': {},
                'total_requests': 0,
                'total_cost': 0.0,
                'average_efficiency': 0.0,
                'alerts_generated': 0
            }
            
            platforms_to_analyze = [platform] if platform else list(self.platform_quotas.keys())
            
            for platform_name in platforms_to_analyze:
                if platform_name not in self.platform_quotas:
                    continue
                
                platform_analytics = await self._analyze_platform_usage(platform_name, cutoff_time)
                analytics['platforms'][platform_name] = platform_analytics
                
                analytics['total_requests'] += platform_analytics.get('total_requests', 0)
                analytics['total_cost'] += platform_analytics.get('total_cost', 0.0)
            
            # Calculate average efficiency
            if analytics['platforms']:
                efficiency_scores = [
                    data.get('efficiency_score', 0) 
                    for data in analytics['platforms'].values()
                ]
                analytics['average_efficiency'] = sum(efficiency_scores) / len(efficiency_scores)
            
            # Count recent alerts
            analytics['alerts_generated'] = len([
                alert for alert in self.quota_alerts
                if alert.timestamp >= cutoff_time
            ])
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting usage analytics: {str(e)}")
            return {}
    
    async def predict_quota_usage(self, platform: str, 
                                hours_ahead: int = 24) -> Dict[str, Any]:
        """
        Predict quota usage for planning purposes.
        
        Args:
            platform: Platform name
            hours_ahead: Hours to predict ahead
            
        Returns:
            Usage predictions
        """



        try:
            if platform not in self.platform_quotas:
                return {}
            
            # Analyze historical usage patterns
            historical_data = await self._get_historical_usage_pattern(platform)
            
            # Simple linear prediction based on recent trends
            recent_hourly_average = historical_data.get('recent_hourly_average', 0)
            daily_trend = historical_data.get('daily_trend', 1.0)
            
            predictions = {
                'platform': platform,
                'prediction_horizon_hours': hours_ahead,
                'predicted_requests': recent_hourly_average * hours_ahead * daily_trend,
                'predicted_cost': 0.0,
                'quota_sufficiency': {},
                'recommendations': []
            }
            
            quota_config = self.platform_quotas[platform]
            predicted_requests = predictions['predicted_requests']
            
            # Calculate predicted cost
            predictions['predicted_cost'] = predicted_requests * quota_config.cost_per_request
            
            # Check quota sufficiency
            current_usage = quota_config.current_usage
            predictions['quota_sufficiency'] = {
                'hourly': (current_usage['hour'] + predicted_requests) <= quota_config.requests_per_hour,
                'daily': (current_usage['day'] + predicted_requests) <= quota_config.requests_per_day,
                'monthly': (current_usage['month'] + predicted_requests) <= quota_config.requests_per_month
            }
            
            # Generate recommendations
            if not all(predictions['quota_sufficiency'].values()):
                predictions['recommendations'].append('Consider reducing request rate or increasing quotas')
            
            if predictions['predicted_cost'] > 100:  # Arbitrary threshold
                predictions['recommendations'].append('High cost predicted - optimize request efficiency')
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error predicting quota usage for {platform}: {str(e)}")
            return {}
    
    async def optimize_quota_distribution(self) -> Dict[str, Any]:
        """
        Optimize quota distribution across platforms based on usage patterns.
        
        Returns:
            Optimization recommendations
        """



        try:
            optimization = {
                'total_platforms': len(self.platform_quotas),
                'recommendations': [],
                'efficiency_improvements': {},
                'cost_savings_potential': 0.0
            }
            
            for platform_name, quota_config in self.platform_quotas.items():
                platform_stats = self.performance_stats.get(platform_name, {})
                
                if platform_stats.get('total_requests', 0) == 0:
                    continue
                
                # Calculate efficiency metrics
                success_rate = (platform_stats['successful_requests'] / 
                              platform_stats['total_requests'] * 100)
                
                utilization_rate = (sum(quota_config.current_usage.values()) / 
                                  sum([quota_config.requests_per_hour, 
                                       quota_config.requests_per_day, 
                                       quota_config.requests_per_month]) * 100)
                
                # Generate recommendations
                if success_rate < 80:
                    optimization['recommendations'].append(
                        f"{platform_name}: Low success rate ({success_rate:.1f}%) - investigate API issues"
                    )
                
                if utilization_rate < 20:
                    optimization['recommendations'].append(
                        f"{platform_name}: Low utilization ({utilization_rate:.1f}%) - consider reducing quotas"
                    )
                elif utilization_rate > 80:
                    optimization['recommendations'].append(
                        f"{platform_name}: High utilization ({utilization_rate:.1f}%) - consider increasing quotas"
                    )
                
                optimization['efficiency_improvements'][platform_name] = {
                    'success_rate': success_rate,
                    'utilization_rate': utilization_rate,
                    'cost_efficiency': platform_stats['successful_requests'] / max(1, platform_stats['total_cost'])
                }
            
            return optimization
            
        except Exception as e:
            self.logger.error(f"Error optimizing quota distribution: {str(e)}")
            return {}
    
    # Private helper methods
    
    async def _check_quota_availability(self, platform: str, 
                                      requests_needed: int, 
                                      priority: str) -> bool:
        """Check if quota is available for requests"""



        try:
            quota_config = self.platform_quotas[platform]
            
            # Check all time periods
            periods_to_check = ['minute', 'hour', 'day', 'month']
            limits = {
                'minute': quota_config.requests_per_minute,
                'hour': quota_config.requests_per_hour,
                'day': quota_config.requests_per_day,
                'month': quota_config.requests_per_month
            }
            
            for period in periods_to_check:
                current_usage = quota_config.current_usage[period]
                limit = limits[period]
                
                # Apply priority reserves
                if priority in ['high', 'critical']:
                    effective_limit = limit
                else:
                    effective_limit = limit - quota_config.priority_reserves
                
                # Check if request would exceed limit
                if current_usage + requests_needed > effective_limit:
                    # Check if burst allowance can cover it
                    if current_usage + requests_needed > limit + quota_config.burst_allowance:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking quota availability: {str(e)}")
            return False
    
    async def _consume_quota(self, platform: str, requests_count: int):
        """Consume quota for successful requests"""



        try:
            quota_config = self.platform_quotas[platform]
            
            # Update usage counters
            for period in ['minute', 'hour', 'day', 'month']:
                quota_config.current_usage[period] += requests_count
            
            # Record timestamp for rate limiting
            current_time = time.time()
            for _ in range(requests_count):
                self.request_timestamps[platform].append(current_time)
            
            # Update performance stats
            self.performance_stats[platform]['total_requests'] += requests_count
            self.performance_stats[platform]['successful_requests'] += requests_count
            self.performance_stats[platform]['total_cost'] += requests_count * quota_config.cost_per_request
            
            # Record usage metrics
            self._record_usage_metrics(platform, requests_count, success=True)
            
        except Exception as e:
            self.logger.error(f"Error consuming quota for {platform}: {str(e)}")
    
    async def _calculate_suggested_delay(self, platform: str, requests_needed: int) -> float:
        """Calculate suggested delay for throttled requests"""



        try:
            quota_config = self.platform_quotas[platform]
            
            # Find the most restrictive period
            min_reset_time = float('inf')
            
            for period, reset_time in quota_config.reset_times.items():
                time_until_reset = (reset_time - datetime.utcnow()).total_seconds()
                min_reset_time = min(min_reset_time, time_until_reset)
            
            # Add some buffer time
            suggested_delay = max(1.0, min_reset_time + 5.0)
            
            return min(suggested_delay, 300.0)  # Cap at 5 minutes
            
        except Exception as e:
            self.logger.error(f"Error calculating suggested delay: {str(e)}")
            return 60.0  # Default 1 minute
    
    async def _process_throttled_requests(self, platform: str):
        """Process throttled requests when quota becomes available"""



        try:
            self.throttling_active[platform] = True
            queue = self.request_queues[platform]
            
            while not queue.empty():
                try:
                    requests_needed, priority, timestamp = await asyncio.wait_for(
                        queue.get(), timeout=1.0
                    )
                    
                    # Check if request is still valid (not too old)
                    if time.time() - timestamp > 300:  # 5 minutes
                        continue
                    
                    # Check if quota is now available
                    if await self._check_quota_availability(platform, requests_needed, priority):
                        await self._consume_quota(platform, requests_needed)
                        # Notify waiting request (would need callback mechanism)
                        
                except asyncio.TimeoutError:
                    break
                except Exception as e:
                    self.logger.error(f"Error processing throttled request: {str(e)}")
                    break
            
            self.throttling_active[platform] = False
            
        except Exception as e:
            self.logger.error(f"Error processing throttled requests for {platform}: {str(e)}")
            self.throttling_active[platform] = False
    
    async def _quota_monitor_loop(self):
        """Background loop for quota monitoring and alerting"""



        try:
            while True:
                for platform_name, quota_config in self.platform_quotas.items():
                    await self._check_quota_thresholds(platform_name, quota_config)
                
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            self.logger.error(f"Error in quota monitor loop: {str(e)}")
    
    async def _reset_quotas_loop(self):
        """Background loop for resetting quotas"""



        try:
            while True:
                current_time = datetime.utcnow()
                
                for platform_name, quota_config in self.platform_quotas.items():
                    for period, reset_time in quota_config.reset_times.items():
                        if current_time >= reset_time:
                            # Reset quota for this period
                            quota_config.current_usage[period] = 0
                            
                            # Set next reset time
                            if period == 'minute':
                                quota_config.reset_times[period] = current_time + timedelta(minutes=1)
                            elif period == 'hour':
                                quota_config.reset_times[period] = current_time + timedelta(hours=1)
                            elif period == 'day':
                                quota_config.reset_times[period] = current_time + timedelta(days=1)
                            elif period == 'month':
                                quota_config.reset_times[period] = current_time + timedelta(days=30)
                            
                            self.logger.debug(f"Reset {period} quota for {platform_name}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            self.logger.error(f"Error in quota reset loop: {str(e)}")
    
    async def _check_quota_thresholds(self, platform_name: str, quota_config: PlatformQuotas):
        """Check quota thresholds and generate alerts"""



        try:
            for period in ['minute', 'hour', 'day', 'month']:
                current_usage = quota_config.current_usage[period]
                limit = getattr(quota_config, f'requests_per_{period}')
                
                usage_percentage = (current_usage / limit) * 100 if limit > 0 else 0
                
                # Check alert thresholds
                for severity, threshold in self.alert_thresholds.items():
                    if usage_percentage >= threshold:
                        await self._generate_quota_alert(
                            platform_name, period, usage_percentage, 
                            current_usage, limit, severity
                        )
                        break
                        
        except Exception as e:
            self.logger.error(f"Error checking quota thresholds: {str(e)}")
    
    async def _generate_quota_alert(self, platform: str, period: str, 
                                  usage_percentage: float, current_usage: int, 
                                  limit: int, severity: str):
        """Generate quota alert"""



        try:
            alert_id = f"quota_alert_{platform}_{period}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            alert = QuotaAlert(
                alert_id=alert_id,
                platform=platform,
                quota_type='requests',
                threshold_percentage=usage_percentage,
                current_usage=current_usage,
                limit=limit,
                timestamp=datetime.utcnow(),
                severity=severity,
                message=f"{platform} {period} quota at {usage_percentage:.1f}% ({current_usage}/{limit})"
            )
            
            self.quota_alerts.append(alert)
            
            # Log alert
            self.logger.warning(f"Quota alert: {alert.message}")
            
            # Keep only recent alerts
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.quota_alerts = [
                alert for alert in self.quota_alerts 
                if alert.timestamp >= cutoff_time
            ]
            
        except Exception as e:
            self.logger.error(f"Error generating quota alert: {str(e)}")
    
    def _record_usage_metrics(self, platform: str, requests_count: int, 
                            success: bool, response_time: float = 0.0):
        """Record usage metrics for analytics"""



        try:
            current_time = datetime.utcnow()
            
            # Update performance stats
            stats = self.performance_stats[platform]
            if success:
                stats['successful_requests'] += requests_count
            else:
                stats['failed_requests'] += requests_count
            
            if response_time > 0:
                # Calculate running average
                total_requests = stats['total_requests']
                if total_requests > 0:
                    stats['average_response_time'] = (
                        (stats['average_response_time'] * total_requests + response_time) / 
                        (total_requests + requests_count)
                    )
                else:
                    stats['average_response_time'] = response_time
            
            # Create usage metric entry
            metric = UsageMetrics(
                platform=platform,
                time_period='hour',
                requests_made=requests_count,
                requests_failed=0 if success else requests_count,
                requests_throttled=0,
                average_response_time=response_time,
                cost_incurred=requests_count * self.platform_quotas[platform].cost_per_request,
                efficiency_score=100.0 if success else 0.0,
                timestamp=current_time
            )
            
            self.usage_metrics.append(metric)
            
            # Keep only recent metrics
            cutoff_time = current_time - timedelta(days=7)
            self.usage_metrics = [
                metric for metric in self.usage_metrics 
                if metric.timestamp >= cutoff_time
            ]
            
        except Exception as e:
            self.logger.error(f"Error recording usage metrics: {str(e)}")
    
    async def _analyze_platform_usage(self, platform: str, since_time: datetime) -> Dict[str, Any]:
        """Analyze usage for a specific platform"""



        try:
            relevant_metrics = [
                metric for metric in self.usage_metrics
                if metric.platform == platform and metric.timestamp >= since_time
            ]
            
            if not relevant_metrics:
                return {'total_requests': 0, 'efficiency_score': 0, 'total_cost': 0.0}
            
            total_requests = sum(metric.requests_made for metric in relevant_metrics)
            total_failed = sum(metric.requests_failed for metric in relevant_metrics)
            total_cost = sum(metric.cost_incurred for metric in relevant_metrics)
            
            efficiency_score = 0.0
            if total_requests > 0:
                efficiency_score = ((total_requests - total_failed) / total_requests) * 100
            
            average_response_time = 0.0
            if relevant_metrics:
                response_times = [m.average_response_time for m in relevant_metrics if m.average_response_time > 0]
                if response_times:
                    average_response_time = sum(response_times) / len(response_times)
            
            return {
                'total_requests': total_requests,
                'successful_requests': total_requests - total_failed,
                'failed_requests': total_failed,
                'efficiency_score': efficiency_score,
                'total_cost': total_cost,
                'average_response_time': average_response_time
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing platform usage: {str(e)}")
            return {}
    
    async def _get_historical_usage_pattern(self, platform: str) -> Dict[str, float]:
        """Get historical usage pattern for predictions"""



        try:
            # Get timestamps for the platform
            timestamps = list(self.request_timestamps.get(platform, []))
            
            if len(timestamps) < 10:  # Not enough data
                return {'recent_hourly_average': 10, 'daily_trend': 1.0}
            
            # Calculate recent hourly average
            current_time = time.time()
            recent_timestamps = [ts for ts in timestamps if current_time - ts < 3600]  # Last hour
            recent_hourly_average = len(recent_timestamps)
            
            # Simple trend calculation (compare last 24h vs previous 24h)
            day_ago = current_time - 86400
            two_days_ago = current_time - 172800
            
            recent_day = [ts for ts in timestamps if day_ago <= ts <= current_time]
            previous_day = [ts for ts in timestamps if two_days_ago <= ts <= day_ago]
            
            daily_trend = 1.0
            if len(previous_day) > 0:
                daily_trend = len(recent_day) / len(previous_day)
            
            return {
                'recent_hourly_average': max(1, recent_hourly_average),
                'daily_trend': max(0.1, min(10.0, daily_trend))  # Bound the trend
            }
            
        except Exception as e:
            self.logger.error(f"Error getting historical usage pattern: {str(e)}")
            return {'recent_hourly_average': 10, 'daily_trend': 1.0}
    
    def get_quota_statistics(self) -> Dict[str, Any]:
        """Get comprehensive quota management statistics"""



        try:
            stats = {
                'total_platforms': len(self.platform_quotas),
                'active_platforms': len([q for q in self.platform_quotas.values() if q.is_active]),
                'total_alerts': len(self.quota_alerts),
                'platforms_throttling': len([p for p in self.throttling_active if self.throttling_active[p]]),
                'platform_details': {},
                'global_metrics': {
                    'total_requests_all_platforms': 0,
                    'total_cost_all_platforms': 0.0,
                    'average_efficiency_all_platforms': 0.0
                }
            }
            
            # Platform-specific details
            total_requests = 0
            total_cost = 0.0
            efficiency_scores = []
            
            for platform_name, quota_config in self.platform_quotas.items():
                platform_stats = self.performance_stats.get(platform_name, {})
                
                platform_detail = {
                    'quota_status': 'available',
                    'current_usage': quota_config.current_usage.copy(),
                    'limits': {
                        'per_minute': quota_config.requests_per_minute,
                        'per_hour': quota_config.requests_per_hour,
                        'per_day': quota_config.requests_per_day,
                        'per_month': quota_config.requests_per_month
                    },
                    'performance': platform_stats,
                    'is_throttling': self.throttling_active.get(platform_name, False)
                }
                
                stats['platform_details'][platform_name] = platform_detail
                
                # Aggregate global metrics
                total_requests += platform_stats.get('total_requests', 0)
                total_cost += platform_stats.get('total_cost', 0.0)
                
                if platform_stats.get('total_requests', 0) > 0:
                    efficiency = (platform_stats['successful_requests'] / 
                                platform_stats['total_requests'] * 100)
                    efficiency_scores.append(efficiency)
            
            # Update global metrics
            stats['global_metrics']['total_requests_all_platforms'] = total_requests
            stats['global_metrics']['total_cost_all_platforms'] = total_cost
            if efficiency_scores:
                stats['global_metrics']['average_efficiency_all_platforms'] = (
                    sum(efficiency_scores) / len(efficiency_scores)
                )
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting quota statistics: {str(e)}")
            return {}
