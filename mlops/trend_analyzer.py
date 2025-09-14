"""
Enterprise Trend Analyzer for ML Performance and Business Metrics
ML Engineer + Business Analyst implementation with predictive analytics
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import statistics
import math

logger = logging.getLogger(__name__)


class TrendType(Enum):
    """Types of trends to analyze"""
    PERFORMANCE = "performance"
    BUSINESS = "business"
    USAGE = "usage"
    QUALITY = "quality"
    SEASONAL = "seasonal"
    ANOMALY = "anomaly"


class TrendDirection(Enum):
    """Trend direction"""
    INCREASING = "increasing"
    DECREASING = "decreasing"
    STABLE = "stable"
    VOLATILE = "volatile"
    CYCLICAL = "cyclical"


class TrendSignificance(Enum):
    """Trend significance levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TimeHorizon(Enum):
    """Time horizons for trend analysis"""
    SHORT_TERM = "short_term"  # 1-7 days
    MEDIUM_TERM = "medium_term"  # 1-4 weeks
    LONG_TERM = "long_term"  # 1-12 months
    VERY_LONG_TERM = "very_long_term"  # 1+ years


@dataclass
class TrendPoint:
    """Individual data point for trend analysis"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Trend analysis result"""
    trend_id: str
    metric_name: str
    time_horizon: TimeHorizon
    direction: TrendDirection
    significance: TrendSignificance
    slope: float
    correlation: float
    confidence: float
    data_points: List[TrendPoint]
    predictions: List[TrendPoint] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SeasonalPattern:
    """Seasonal pattern identification"""
    pattern_id: str
    metric_name: str
    pattern_type: str  # daily, weekly, monthly, yearly
    peak_periods: List[str]
    trough_periods: List[str]
    amplitude: float
    confidence: float
    next_peak: Optional[datetime] = None
    next_trough: Optional[datetime] = None


@dataclass
class TrendAlert:
    """Trend-based alert"""
    alert_id: str
    metric_name: str
    alert_type: str
    message: str
    severity: str
    trend_analysis: TrendAnalysis
    created_at: datetime = field(default_factory=datetime.utcnow)
    creator_impact: str = "unknown"


class TrendAnalyzer:
    """Enterprise trend analyzer for ML performance and business metrics"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        self.config = config or {}
        self.metric_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.trend_analyses: Dict[str, TrendAnalysis] = {}
        self.seasonal_patterns: Dict[str, SeasonalPattern] = {}
        self.alerts: List[TrendAlert] = []
        self.alert_handlers: List[Callable] = []
        
        # Creator-specific trend monitoring
        self.creator_trend_metrics = {
            'musicians': {
                'performance_metrics': [
                    'audio_quality_score', 'streaming_revenue', 'listener_engagement',
                    'collaboration_frequency', 'fan_growth_rate', 'song_completion_rate'
                ],
                'business_metrics': [
                    'monthly_revenue', 'booking_requests', 'brand_partnerships',
                    'merchandise_sales', 'licensing_deals', 'live_performance_revenue'
                ],
                'engagement_metrics': [
                    'social_media_reach', 'playlist_additions', 'user_generated_content',
                    'concert_attendance', 'fan_club_growth', 'streaming_hours'
                ]
            },
            'photographers': {
                'performance_metrics': [
                    'image_quality_score', 'portfolio_views', 'client_satisfaction',
                    'booking_conversion_rate', 'editing_efficiency', 'style_consistency'
                ],
                'business_metrics': [
                    'session_bookings', 'average_project_value', 'client_retention',
                    'print_sales', 'licensing_revenue', 'workshop_income'
                ],
                'market_metrics': [
                    'market_demand', 'pricing_competitiveness', 'niche_popularity',
                    'seasonal_booking_trends', 'geographic_reach', 'brand_recognition'
                ]
            },
            'bloggers': {
                'content_metrics': [
                    'content_quality_score', 'page_views', 'time_on_page',
                    'social_shares', 'comment_engagement', 'subscriber_growth'
                ],
                'seo_metrics': [
                    'search_rankings', 'organic_traffic', 'keyword_performance',
                    'backlink_acquisition', 'domain_authority', 'click_through_rate'
                ],
                'monetization_metrics': [
                    'ad_revenue', 'affiliate_commissions', 'sponsored_content_value',
                    'course_sales', 'book_sales', 'speaking_engagement_fees'
                ]
            },
            'influencers': {
                'reach_metrics': [
                    'follower_growth', 'reach_per_post', 'engagement_rate',
                    'story_completion_rate', 'live_stream_viewers', 'cross_platform_reach'
                ],
                'engagement_metrics': [
                    'likes_per_post', 'comments_per_post', 'shares_per_post',
                    'save_rate', 'direct_messages', 'user_generated_content'
                ],
                'business_metrics': [
                    'brand_deal_value', 'product_launch_success', 'conversion_rates',
                    'affiliate_earnings', 'merchandise_sales', 'event_hosting_revenue'
                ]
            },
            'comedians': {
                'performance_metrics': [
                    'audience_response_score', 'joke_success_rate', 'timing_accuracy',
                    'stage_presence_rating', 'material_originality', 'crowd_energy'
                ],
                'booking_metrics': [
                    'venue_bookings', 'ticket_sales', 'audience_size_growth',
                    'repeat_bookings', 'venue_rating', 'geographic_expansion'
                ],
                'content_metrics': [
                    'video_views', 'viral_content_rate', 'social_media_engagement',
                    'podcast_appearances', 'tv_show_bookings', 'streaming_special_views'
                ]
            }
        }
        
        # Trend detection thresholds
        self.trend_thresholds = {
            'significance_slope': 0.1,  # Minimum slope for significant trend
            'correlation_threshold': 0.7,  # Minimum correlation for reliable trend
            'confidence_threshold': 0.8,  # Minimum confidence level
            'volatility_threshold': 0.3,  # Maximum volatility for stable trend
            'seasonal_strength': 0.6  # Minimum strength for seasonal pattern
        }
        
    async def initialize(self) -> bool:
        """Initialize trend analyzer"""
        try:
            logger.info("Initializing Trend Analyzer...")
            
            # Setup trend monitoring
            await self._setup_trend_monitoring()
            
            # Initialize seasonal pattern detection
            await self._setup_seasonal_detection()
            
            # Setup alert system
            await self._setup_alert_system()
            
            logger.info("Trend Analyzer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Trend Analyzer: {e}")
            return False
    
    async def add_data_point(self, 
                           metric_name: str,
                           value: float,
                           timestamp: Optional[datetime] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add data point for trend analysis"""
        try:
            timestamp = timestamp or datetime.utcnow()
            metadata = metadata or {}
            
            data_point = TrendPoint(
                timestamp=timestamp,
                value=value,
                metadata=metadata
            )
            
            self.metric_data[metric_name].append(data_point)
            
            # Trigger real-time trend analysis if enough data
            if len(self.metric_data[metric_name]) >= 10:
                await self._analyze_real_time_trend(metric_name)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add data point: {e}")
            return False
    
    async def analyze_trend(self, 
                          metric_name: str,
                          time_horizon: TimeHorizon = TimeHorizon.MEDIUM_TERM,
                          include_predictions: bool = True) -> Optional[TrendAnalysis]:
        """Analyze trend for specific metric"""
        try:
            if metric_name not in self.metric_data:
                logger.error(f"No data found for metric: {metric_name}")
                return None
            
            data_points = list(self.metric_data[metric_name])
            
            # Filter data based on time horizon
            filtered_data = self._filter_data_by_horizon(data_points, time_horizon)
            
            if len(filtered_data) < 5:
                logger.warning(f"Insufficient data for trend analysis: {len(filtered_data)} points")
                return None
            
            # Perform trend analysis
            analysis = await self._perform_trend_analysis(
                metric_name, filtered_data, time_horizon, include_predictions
            )
            
            # Store analysis
            if analysis:
                self.trend_analyses[f"{metric_name}_{time_horizon.value}"] = analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze trend: {e}")
            return None
    
    async def detect_seasonal_patterns(self, 
                                     metric_name: str,
                                     min_periods: int = 3) -> List[SeasonalPattern]:
        """Detect seasonal patterns in metric data"""
        try:
            if metric_name not in self.metric_data:
                return []
            
            data_points = list(self.metric_data[metric_name])
            
            if len(data_points) < 30:  # Need at least 30 points for seasonal analysis
                return []
            
            patterns = []
            
            # Detect different seasonal patterns
            daily_pattern = await self._detect_daily_pattern(metric_name, data_points)
            if daily_pattern:
                patterns.append(daily_pattern)
            
            weekly_pattern = await self._detect_weekly_pattern(metric_name, data_points)
            if weekly_pattern:
                patterns.append(weekly_pattern)
            
            monthly_pattern = await self._detect_monthly_pattern(metric_name, data_points)
            if monthly_pattern:
                patterns.append(monthly_pattern)
            
            # Store patterns
            for pattern in patterns:
                self.seasonal_patterns[pattern.pattern_id] = pattern
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to detect seasonal patterns: {e}")
            return []
    
    async def predict_future_values(self, 
                                  metric_name: str,
                                  prediction_horizon: timedelta = timedelta(days=30),
                                  confidence_interval: bool = True) -> List[TrendPoint]:
        """Predict future values for metric"""
        try:
            if metric_name not in self.metric_data:
                return []
            
            data_points = list(self.metric_data[metric_name])
            
            if len(data_points) < 10:
                return []
            
            # Use different prediction methods
            predictions = []
            
            # Linear trend prediction
            linear_predictions = await self._predict_linear_trend(
                data_points, prediction_horizon
            )
            
            # Seasonal prediction if pattern exists
            seasonal_predictions = await self._predict_seasonal_trend(
                metric_name, data_points, prediction_horizon
            )
            
            # Combine predictions (weighted average)
            if seasonal_predictions:
                predictions = await self._combine_predictions(
                    linear_predictions, seasonal_predictions
                )
            else:
                predictions = linear_predictions
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to predict future values: {e}")
            return []
    
    async def get_creator_trends(self, 
                               creator_type: str,
                               time_horizon: TimeHorizon = TimeHorizon.MEDIUM_TERM) -> Dict[str, List[TrendAnalysis]]:
        """Get trend analysis for all creator metrics"""
        try:
            if creator_type not in self.creator_trend_metrics:
                logger.error(f"Creator type {creator_type} not supported")
                return {}
            
            creator_metrics = self.creator_trend_metrics[creator_type]
            trends_by_category = {}
            
            for category, metrics in creator_metrics.items():
                category_trends = []
                
                for metric in metrics:
                    trend_analysis = await self.analyze_trend(metric, time_horizon)
                    if trend_analysis:
                        category_trends.append(trend_analysis)
                
                trends_by_category[category] = category_trends
            
            return trends_by_category
            
        except Exception as e:
            logger.error(f"Failed to get creator trends: {e}")
            return {}
    
    async def generate_insights(self, 
                              metric_name: str,
                              time_horizon: TimeHorizon = TimeHorizon.MEDIUM_TERM) -> List[str]:
        """Generate insights from trend analysis"""
        try:
            trend_key = f"{metric_name}_{time_horizon.value}"
            
            if trend_key not in self.trend_analyses:
                trend_analysis = await self.analyze_trend(metric_name, time_horizon)
                if not trend_analysis:
                    return []
            else:
                trend_analysis = self.trend_analyses[trend_key]
            
            insights = []
            
            # Direction insights
            if trend_analysis.direction == TrendDirection.INCREASING:
                if trend_analysis.significance == TrendSignificance.HIGH:
                    insights.append(f"{metric_name} shows strong upward trend with {trend_analysis.slope:.2f} slope")
                else:
                    insights.append(f"{metric_name} shows modest improvement")
            elif trend_analysis.direction == TrendDirection.DECREASING:
                if trend_analysis.significance == TrendSignificance.HIGH:
                    insights.append(f"{metric_name} shows concerning downward trend")
                else:
                    insights.append(f"{metric_name} shows slight decline")
            elif trend_analysis.direction == TrendDirection.STABLE:
                insights.append(f"{metric_name} remains stable with minimal variation")
            elif trend_analysis.direction == TrendDirection.VOLATILE:
                insights.append(f"{metric_name} shows high volatility - investigation recommended")
            
            # Confidence insights
            if trend_analysis.confidence < 0.7:
                insights.append(f"Trend analysis has low confidence ({trend_analysis.confidence:.2f}) - more data needed")
            elif trend_analysis.confidence > 0.9:
                insights.append(f"Trend analysis is highly reliable ({trend_analysis.confidence:.2f})")
            
            # Seasonal insights
            seasonal_patterns = await self.detect_seasonal_patterns(metric_name)
            if seasonal_patterns:
                insights.append(f"Seasonal patterns detected in {metric_name}")
                for pattern in seasonal_patterns:
                    insights.append(f"Peak periods: {', '.join(pattern.peak_periods)}")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate insights: {e}")
            return []
    
    async def generate_recommendations(self, 
                                     metric_name: str,
                                     creator_type: Optional[str] = None) -> List[str]:
        """Generate actionable recommendations based on trends"""
        try:
            recommendations = []
            
            # Get recent trend analysis
            trend_analysis = await self.analyze_trend(metric_name, TimeHorizon.SHORT_TERM)
            
            if not trend_analysis:
                return ["Insufficient data for recommendations"]
            
            # General recommendations based on trend direction
            if trend_analysis.direction == TrendDirection.DECREASING:
                if trend_analysis.significance == TrendSignificance.HIGH:
                    recommendations.append(f"Immediate action required: {metric_name} declining rapidly")
                    recommendations.append("Investigate root causes and implement corrective measures")
                else:
                    recommendations.append(f"Monitor {metric_name} closely for continued decline")
            
            elif trend_analysis.direction == TrendDirection.INCREASING:
                recommendations.append(f"Continue current strategies - {metric_name} improving")
                recommendations.append("Identify success factors for replication")
            
            elif trend_analysis.direction == TrendDirection.VOLATILE:
                recommendations.append(f"Stabilize {metric_name} through process improvements")
                recommendations.append("Implement monitoring and control mechanisms")
            
            # Creator-specific recommendations
            if creator_type:
                creator_recommendations = await self._generate_creator_specific_recommendations(
                    metric_name, creator_type, trend_analysis
                )
                recommendations.extend(creator_recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            return []
    
    async def get_trend_alerts(self, 
                             severity_filter: Optional[str] = None,
                             time_period: Optional[timedelta] = None) -> List[TrendAlert]:
        """Get trend-based alerts"""
        try:
            alerts = self.alerts.copy()
            
            # Filter by time period
            if time_period:
                cutoff_time = datetime.utcnow() - time_period
                alerts = [a for a in alerts if a.created_at >= cutoff_time]
            
            # Filter by severity
            if severity_filter:
                alerts = [a for a in alerts if a.severity == severity_filter]
            
            return alerts
            
        except Exception as e:
            logger.error(f"Failed to get trend alerts: {e}")
            return []
    
    async def _setup_trend_monitoring(self) -> None:
        """Setup continuous trend monitoring"""
        asyncio.create_task(self._continuous_trend_monitoring())
    
    async def _setup_seasonal_detection(self) -> None:
        """Setup seasonal pattern detection"""
        asyncio.create_task(self._continuous_seasonal_detection())
    
    async def _setup_alert_system(self) -> None:
        """Setup trend alert system"""
        async def default_alert_handler(alert -> None: TrendAlert) -> None:
            logger.warning(f"Trend Alert: {alert.message} (Severity: {alert.severity})")
        
        self.alert_handlers.append(default_alert_handler)
    
    def _filter_data_by_horizon(self, 
                              data_points: List[TrendPoint],
                              horizon: TimeHorizon) -> List[TrendPoint]:
        """Filter data points by time horizon"""
        now = datetime.utcnow()
        
        if horizon == TimeHorizon.SHORT_TERM:
            cutoff = now - timedelta(days=7)
        elif horizon == TimeHorizon.MEDIUM_TERM:
            cutoff = now - timedelta(days=30)
        elif horizon == TimeHorizon.LONG_TERM:
            cutoff = now - timedelta(days=365)
        else:  # VERY_LONG_TERM
            cutoff = now - timedelta(days=365*2)
        
        return [dp for dp in data_points if dp.timestamp >= cutoff]
    
    async def _perform_trend_analysis(self, 
                                    metric_name: str,
                                    data_points: List[TrendPoint],
                                    time_horizon: TimeHorizon,
                                    include_predictions: bool) -> TrendAnalysis:
        """Perform comprehensive trend analysis"""
        try:
            # Extract values and timestamps
            values = [dp.value for dp in data_points]
            timestamps = [dp.timestamp for dp in data_points]
            
            # Convert timestamps to numeric values for analysis
            epoch_times = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
            
            # Calculate trend metrics
            slope = self._calculate_slope(epoch_times, values)
            correlation = self._calculate_correlation(epoch_times, values)
            volatility = self._calculate_volatility(values)
            
            # Determine trend direction
            direction = self._determine_trend_direction(slope, volatility)
            
            # Determine significance
            significance = self._determine_significance(slope, correlation, volatility)
            
            # Calculate confidence
            confidence = self._calculate_confidence(correlation, len(values), volatility)
            
            # Generate predictions if requested
            predictions = []
            if include_predictions:
                predictions = await self.predict_future_values(metric_name)
            
            # Generate insights
            insights = await self.generate_insights(metric_name, time_horizon)
            
            # Generate recommendations
            recommendations = await self.generate_recommendations(metric_name)
            
            analysis = TrendAnalysis(
                trend_id=str(uuid.uuid4()),
                metric_name=metric_name,
                time_horizon=time_horizon,
                direction=direction,
                significance=significance,
                slope=slope,
                correlation=correlation,
                confidence=confidence,
                data_points=data_points,
                predictions=predictions,
                insights=insights,
                recommendations=recommendations
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Trend analysis error: {e}")
            raise
    
    def _calculate_slope(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate trend slope using linear regression"""
        try:
            n = len(x_values)
            if n < 2:
                return 0.0
            
            x_mean = statistics.mean(x_values)
            y_mean = statistics.mean(y_values)
            
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
            denominator = sum((x - x_mean) ** 2 for x in x_values)
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
            
        except Exception:
            return 0.0
    
    def _calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate correlation coefficient"""
        try:
            if len(x_values) < 2:
                return 0.0
            
            # Use numpy for correlation calculation
            correlation_matrix = np.corrcoef(x_values, y_values)
            return correlation_matrix[0, 1] if not np.isnan(correlation_matrix[0, 1]) else 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_volatility(self, values: List[float]) -> float:
        """Calculate volatility (coefficient of variation)"""
        try:
            if len(values) < 2:
                return 0.0
            
            mean_val = statistics.mean(values)
            std_val = statistics.stdev(values)
            
            if mean_val == 0:
                return 0.0
            
            return std_val / abs(mean_val)
            
        except Exception:
            return 0.0
    
    def _determine_trend_direction(self, slope: float, volatility: float) -> TrendDirection:
        """Determine trend direction"""
        if volatility > self.trend_thresholds['volatility_threshold']:
            return TrendDirection.VOLATILE
        elif abs(slope) < self.trend_thresholds['significance_slope']:
            return TrendDirection.STABLE
        elif slope > 0:
            return TrendDirection.INCREASING
        else:
            return TrendDirection.DECREASING
    
    def _determine_significance(self, slope: float, correlation: float, volatility: float) -> TrendSignificance:
        """Determine trend significance"""
        score = 0
        
        # Slope contribution
        if abs(slope) > 0.5:
            score += 3
        elif abs(slope) > 0.2:
            score += 2
        elif abs(slope) > 0.1:
            score += 1
        
        # Correlation contribution
        if abs(correlation) > 0.9:
            score += 3
        elif abs(correlation) > 0.7:
            score += 2
        elif abs(correlation) > 0.5:
            score += 1
        
        # Volatility contribution (inverse)
        if volatility < 0.1:
            score += 2
        elif volatility < 0.3:
            score += 1
        
        if score >= 6:
            return TrendSignificance.CRITICAL
        elif score >= 4:
            return TrendSignificance.HIGH
        elif score >= 2:
            return TrendSignificance.MEDIUM
        else:
            return TrendSignificance.LOW
    
    def _calculate_confidence(self, correlation: float, sample_size: int, volatility: float) -> float:
        """Calculate confidence in trend analysis"""
        try:
            # Base confidence from correlation
            confidence = abs(correlation)
            
            # Adjust for sample size
            if sample_size > 100:
                confidence *= 1.1
            elif sample_size > 50:
                confidence *= 1.05
            elif sample_size < 10:
                confidence *= 0.8
            
            # Adjust for volatility
            confidence *= (1 - volatility)
            
            return min(max(confidence, 0.0), 1.0)
            
        except Exception:
            return 0.5
    
    async def _detect_daily_pattern(self, 
                                  metric_name: str,
                                  data_points: List[TrendPoint]) -> Optional[SeasonalPattern]:
        """Detect daily seasonal patterns"""
        try:
            # Group data by hour of day
            hourly_data = defaultdict(list)
            
            for dp in data_points:
                hour = dp.timestamp.hour
                hourly_data[hour].append(dp.value)
            
            if len(hourly_data) < 12:  # Need at least half-day coverage
                return None
            
            # Calculate average values for each hour
            hourly_averages = {}
            for hour, values in hourly_data.items():
                hourly_averages[hour] = statistics.mean(values)
            
            # Find peaks and troughs
            peak_hours = []
            trough_hours = []
            
            max_val = max(hourly_averages.values())
            min_val = min(hourly_averages.values())
            threshold = (max_val - min_val) * 0.8  # Top 20% are peaks, bottom 20% are troughs
            
            for hour, avg_val in hourly_averages.items():
                if avg_val >= max_val - threshold * 0.2:
                    peak_hours.append(f"{hour:02d}:00")
                elif avg_val <= min_val + threshold * 0.2:
                    trough_hours.append(f"{hour:02d}:00")
            
            amplitude = (max_val - min_val) / statistics.mean(hourly_averages.values())
            
            # Only return pattern if it's significant
            if amplitude > 0.2:  # 20% variation
                return SeasonalPattern(
                    pattern_id=f"{metric_name}_daily",
                    metric_name=metric_name,
                    pattern_type="daily",
                    peak_periods=peak_hours,
                    trough_periods=trough_hours,
                    amplitude=amplitude,
                    confidence=min(amplitude * 2, 1.0)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Daily pattern detection error: {e}")
            return None
    
    async def _detect_weekly_pattern(self, 
                                   metric_name: str,
                                   data_points: List[TrendPoint]) -> Optional[SeasonalPattern]:
        """Detect weekly seasonal patterns"""
        try:
            # Group data by day of week
            daily_data = defaultdict(list)
            
            for dp in data_points:
                day_of_week = dp.timestamp.strftime('%A')
                daily_data[day_of_week].append(dp.value)
            
            if len(daily_data) < 5:  # Need at least 5 days coverage
                return None
            
            # Calculate average values for each day
            daily_averages = {}
            for day, values in daily_data.items():
                daily_averages[day] = statistics.mean(values)
            
            # Find peaks and troughs
            peak_days = []
            trough_days = []
            
            max_val = max(daily_averages.values())
            min_val = min(daily_averages.values())
            
            for day, avg_val in daily_averages.items():
                if avg_val >= max_val * 0.9:  # Top 10%
                    peak_days.append(day)
                elif avg_val <= min_val * 1.1:  # Bottom 10%
                    trough_days.append(day)
            
            amplitude = (max_val - min_val) / statistics.mean(daily_averages.values())
            
            if amplitude > 0.15:  # 15% variation
                return SeasonalPattern(
                    pattern_id=f"{metric_name}_weekly",
                    metric_name=metric_name,
                    pattern_type="weekly",
                    peak_periods=peak_days,
                    trough_periods=trough_days,
                    amplitude=amplitude,
                    confidence=min(amplitude * 3, 1.0)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Weekly pattern detection error: {e}")
            return None
    
    async def _detect_monthly_pattern(self, 
                                    metric_name: str,
                                    data_points: List[TrendPoint]) -> Optional[SeasonalPattern]:
        """Detect monthly seasonal patterns"""
        try:
            # Group data by month
            monthly_data = defaultdict(list)
            
            for dp in data_points:
                month = dp.timestamp.strftime('%B')
                monthly_data[month].append(dp.value)
            
            if len(monthly_data) < 6:  # Need at least 6 months coverage
                return None
            
            # Calculate average values for each month
            monthly_averages = {}
            for month, values in monthly_data.items():
                monthly_averages[month] = statistics.mean(values)
            
            # Find peaks and troughs
            peak_months = []
            trough_months = []
            
            max_val = max(monthly_averages.values())
            min_val = min(monthly_averages.values())
            
            for month, avg_val in monthly_averages.items():
                if avg_val >= max_val * 0.85:  # Top 15%
                    peak_months.append(month)
                elif avg_val <= min_val * 1.15:  # Bottom 15%
                    trough_months.append(month)
            
            amplitude = (max_val - min_val) / statistics.mean(monthly_averages.values())
            
            if amplitude > 0.2:  # 20% variation
                return SeasonalPattern(
                    pattern_id=f"{metric_name}_monthly",
                    metric_name=metric_name,
                    pattern_type="monthly",
                    peak_periods=peak_months,
                    trough_periods=trough_months,
                    amplitude=amplitude,
                    confidence=min(amplitude * 2.5, 1.0)
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Monthly pattern detection error: {e}")
            return None
    
    async def _predict_linear_trend(self, 
                                  data_points: List[TrendPoint],
                                  horizon: timedelta) -> List[TrendPoint]:
        """Predict future values using linear trend"""
        try:
            if len(data_points) < 3:
                return []
            
            # Extract values and timestamps
            values = [dp.value for dp in data_points]
            timestamps = [dp.timestamp for dp in data_points]
            
            # Convert to epoch times
            epoch_times = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
            
            # Calculate linear trend
            slope = self._calculate_slope(epoch_times, values)
            intercept = statistics.mean(values) - slope * statistics.mean(epoch_times)
            
            # Generate predictions
            predictions = []
            last_time = timestamps[-1]
            prediction_seconds = horizon.total_seconds()
            num_predictions = min(int(prediction_seconds / 3600), 168)  # Max 1 week of hourly predictions
            
            for i in range(1, num_predictions + 1):
                pred_time = last_time + timedelta(hours=i)
                pred_epoch = (pred_time - timestamps[0]).total_seconds()
                pred_value = slope * pred_epoch + intercept
                
                predictions.append(TrendPoint(
                    timestamp=pred_time,
                    value=max(0, pred_value),  # Ensure non-negative values
                    metadata={'prediction_type': 'linear', 'confidence': 0.7}
                ))
            
            return predictions
            
        except Exception as e:
            logger.error(f"Linear prediction error: {e}")
            return []
    
    async def _predict_seasonal_trend(self, 
                                    metric_name: str,
                                    data_points: List[TrendPoint],
                                    horizon: timedelta) -> List[TrendPoint]:
        """Predict future values using seasonal patterns"""
        try:
            # Check if seasonal patterns exist
            patterns = await self.detect_seasonal_patterns(metric_name)
            if not patterns:
                return []
            
            # Use the strongest pattern
            strongest_pattern = max(patterns, key=lambda p: p.confidence)
            
            # For simplicity, apply seasonal adjustment to linear prediction
            linear_predictions = await self._predict_linear_trend(data_points, horizon)
            
            seasonal_predictions = []
            for pred in linear_predictions:
                # Apply seasonal adjustment based on pattern
                seasonal_factor = self._get_seasonal_factor(pred.timestamp, strongest_pattern)
                adjusted_value = pred.value * seasonal_factor
                
                seasonal_predictions.append(TrendPoint(
                    timestamp=pred.timestamp,
                    value=max(0, adjusted_value),
                    metadata={'prediction_type': 'seasonal', 'confidence': strongest_pattern.confidence}
                ))
            
            return seasonal_predictions
            
        except Exception as e:
            logger.error(f"Seasonal prediction error: {e}")
            return []
    
    def _get_seasonal_factor(self, timestamp: datetime, pattern: SeasonalPattern) -> float:
        """Get seasonal adjustment factor for timestamp"""
        try:
            if pattern.pattern_type == "daily":
                hour = timestamp.strftime("%H:00")
                if hour in pattern.peak_periods:
                    return 1.0 + pattern.amplitude * 0.5
                elif hour in pattern.trough_periods:
                    return 1.0 - pattern.amplitude * 0.5
                else:
                    return 1.0
            elif pattern.pattern_type == "weekly":
                day = timestamp.strftime("%A")
                if day in pattern.peak_periods:
                    return 1.0 + pattern.amplitude * 0.3
                elif day in pattern.trough_periods:
                    return 1.0 - pattern.amplitude * 0.3
                else:
                    return 1.0
            elif pattern.pattern_type == "monthly":
                month = timestamp.strftime("%B")
                if month in pattern.peak_periods:
                    return 1.0 + pattern.amplitude * 0.4
                elif month in pattern.trough_periods:
                    return 1.0 - pattern.amplitude * 0.4
                else:
                    return 1.0
            
            return 1.0
            
        except Exception:
            return 1.0
    
    async def _combine_predictions(self, 
                                 linear_preds: List[TrendPoint],
                                 seasonal_preds: List[TrendPoint]) -> List[TrendPoint]:
        """Combine linear and seasonal predictions"""
        try:
            combined = []
            
            for lin_pred, seas_pred in zip(linear_preds, seasonal_preds):
                # Weighted average based on confidence
                lin_weight = lin_pred.metadata.get('confidence', 0.5)
                seas_weight = seas_pred.metadata.get('confidence', 0.5)
                
                total_weight = lin_weight + seas_weight
                if total_weight > 0:
                    combined_value = (
                        (lin_pred.value * lin_weight + seas_pred.value * seas_weight) / total_weight
                    )
                else:
                    combined_value = (lin_pred.value + seas_pred.value) / 2
                
                combined.append(TrendPoint(
                    timestamp=lin_pred.timestamp,
                    value=max(0, combined_value),
                    metadata={
                        'prediction_type': 'combined',
                        'confidence': min(lin_weight + seas_weight, 1.0)
                    }
                ))
            
            return combined
            
        except Exception as e:
            logger.error(f"Prediction combination error: {e}")
            return linear_preds
    
    async def _analyze_real_time_trend(self, metric_name -> None: str) -> None:
        """Analyze trend in real-time as new data arrives"""
        try:
            # Quick trend analysis on recent data
            recent_analysis = await self.analyze_trend(metric_name, TimeHorizon.SHORT_TERM)
            
            if recent_analysis:
                # Check for alert conditions
                await self._check_trend_alerts(recent_analysis)
            
        except Exception as e:
            logger.error(f"Real-time trend analysis error: {e}")
    
    async def _check_trend_alerts(self, analysis -> None: TrendAnalysis) -> None:
        """Check if trend analysis should trigger alerts"""
        try:
            alerts_to_create = []
            
            # Critical declining trend
            if (analysis.direction == TrendDirection.DECREASING and 
                analysis.significance == TrendSignificance.CRITICAL):
                alerts_to_create.append({
                    'type': 'critical_decline',
                    'message': f"Critical decline detected in {analysis.metric_name}",
                    'severity': 'critical'
                })
            
            # High volatility
            elif analysis.direction == TrendDirection.VOLATILE:
                alerts_to_create.append({
                    'type': 'high_volatility',
                    'message': f"High volatility detected in {analysis.metric_name}",
                    'severity': 'medium'
                })
            
            # Low confidence warning
            if analysis.confidence < 0.6:
                alerts_to_create.append({
                    'type': 'low_confidence',
                    'message': f"Low confidence in trend analysis for {analysis.metric_name}",
                    'severity': 'low'
                })
            
            # Create alerts
            for alert_config in alerts_to_create:
                alert = TrendAlert(
                    alert_id=str(uuid.uuid4()),
                    metric_name=analysis.metric_name,
                    alert_type=alert_config['type'],
                    message=alert_config['message'],
                    severity=alert_config['severity'],
                    trend_analysis=analysis
                )
                
                self.alerts.append(alert)
                
                # Trigger alert handlers
                for handler in self.alert_handlers:
                    asyncio.create_task(handler(alert))
            
            # Keep only recent alerts (last 30 days)
            cutoff = datetime.utcnow() - timedelta(days=30)
            self.alerts = [a for a in self.alerts if a.created_at >= cutoff]
            
        except Exception as e:
            logger.error(f"Trend alert check error: {e}")
    
    async def _generate_creator_specific_recommendations(self, 
                                                       metric_name: str,
                                                       creator_type: str,
                                                       analysis: TrendAnalysis) -> List[str]:
        """Generate creator-specific recommendations"""
        try:
            recommendations = []
            
            if creator_type == 'musicians':
                if 'revenue' in metric_name.lower() and analysis.direction == TrendDirection.DECREASING:
                    recommendations.extend([
                        "Consider diversifying revenue streams (streaming, live performances, merchandising)",
                        "Analyze audience engagement patterns to optimize release timing",
                        "Explore collaboration opportunities with trending artists"
                    ])
                elif 'engagement' in metric_name.lower() and analysis.direction == TrendDirection.INCREASING:
                    recommendations.extend([
                        "Capitalize on increased engagement with more frequent releases",
                        "Consider launching fan community initiatives"
                    ])
            
            elif creator_type == 'photographers':
                if 'booking' in metric_name.lower() and analysis.direction == TrendDirection.VOLATILE:
                    recommendations.extend([
                        "Stabilize booking flow with retainer packages",
                        "Develop seasonal marketing strategies",
                        "Build referral network with wedding planners and event coordinators"
                    ])
            
            elif creator_type == 'influencers':
                if 'reach' in metric_name.lower() and analysis.direction == TrendDirection.STABLE:
                    recommendations.extend([
                        "Experiment with new content formats to boost reach",
                        "Analyze peak engagement times for optimal posting",
                        "Consider cross-platform content strategies"
                    ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Creator-specific recommendations error: {e}")
            return []
    
    async def _continuous_trend_monitoring(self) -> None:
        """Continuous background trend monitoring"""
        while True:
            try:
                # Monitor trends every 10 minutes
                await asyncio.sleep(600)
                
                for metric_name in list(self.metric_data.keys()):
                    if len(self.metric_data[metric_name]) >= 20:
                        await self._analyze_real_time_trend(metric_name)
                
            except Exception as e:
                logger.error(f"Continuous trend monitoring error: {e}")
    
    async def _continuous_seasonal_detection(self) -> None:
        """Continuous seasonal pattern detection"""
        while True:
            try:
                # Check for seasonal patterns every hour
                await asyncio.sleep(3600)
                
                for metric_name in list(self.metric_data.keys()):
                    if len(self.metric_data[metric_name]) >= 50:
                        await self.detect_seasonal_patterns(metric_name)
                
            except Exception as e:
                logger.error(f"Continuous seasonal detection error: {e}")


# Example usage and testing
async def main() -> None:
    """Example usage of Trend Analyzer"""
    analyzer = TrendAnalyzer()
    
    # Initialize
    await analyzer.initialize()
    
    # Add sample data points
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for i in range(720):  # 30 days of hourly data
        timestamp = base_time + timedelta(hours=i)
        # Simulate trending data with noise and seasonal pattern
        base_value = 100 + i * 0.1  # Slight upward trend
        seasonal = 20 * math.sin(2 * math.pi * i / 24)  # Daily seasonality
        noise = np.random.normal(0, 5)  # Random noise
        value = max(0, base_value + seasonal + noise)
        
        await analyzer.add_data_point("user_engagement", value, timestamp)
    
    # Analyze trends
    trend_analysis = await analyzer.analyze_trend("user_engagement", TimeHorizon.MEDIUM_TERM)
    print(f"Trend Analysis: {trend_analysis}")
    
    # Detect seasonal patterns
    patterns = await analyzer.detect_seasonal_patterns("user_engagement")
    print(f"Seasonal Patterns: {patterns}")
    
    # Generate insights
    insights = await analyzer.generate_insights("user_engagement")
    print(f"Insights: {insights}")


if __name__ == "__main__":
    asyncio.run(main())