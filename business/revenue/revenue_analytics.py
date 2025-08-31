"""
 Revenue Analytics - Ultra-Advanced Revenue Analytics & Insights Engine
========================================================================

Industrial-grade revenue analytics system providing comprehensive insights,
predictive analytics, performance benchmarking, and advanced reporting
for content creators across all platforms.

Created by: Fahed Mlaiel <mlaiel@live.de>
© 2025 Fahed Mlaiel. All rights reserved.

Team Specialists:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

 STRICT COPYRIGHT WARNING - UNAUTHORIZED USE PROHIBITED 
Contact mlaiel@live.de for licensing inquiries.

Business Logic: Multi-Format Upload → AI Protection → SEO → Collaboration → Revenue Analytics
==========================================================================================
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import json
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from ...core.database import DatabaseManager
from ...core.security import SecurityManager
from ...core.monitoring import MetricsCollector
from ...ai.engines.analytics_engine import AnalyticsEngine
from ...ai.models.revenue_prediction import RevenuePredictionModel
from ...integrations.visualization.chart_generator import ChartGenerator

logger = logging.getLogger(__name__)


class AnalyticsTimeframe(Enum):
    """Analytics timeframe options"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class MetricType(Enum):
    """Revenue metric types"""
    GROSS_REVENUE = "gross_revenue"
    NET_REVENUE = "net_revenue"
    PLATFORM_FEES = "platform_fees"
    TAX_WITHHOLDINGS = "tax_withholdings"
    COMMISSION = "commission"
    GROWTH_RATE = "growth_rate"
    CONVERSION_RATE = "conversion_rate"
    AVERAGE_REVENUE_PER_USER = "arpu"
    LIFETIME_VALUE = "ltv"


class ComparisonType(Enum):
    """Comparison analysis types"""
    PERIOD_OVER_PERIOD = "period_over_period"
    YEAR_OVER_YEAR = "year_over_year"
    PLATFORM_COMPARISON = "platform_comparison"
    PEER_BENCHMARKING = "peer_benchmarking"
    INDUSTRY_BENCHMARKING = "industry_benchmarking"


@dataclass
class RevenueMetrics:
    """Revenue metrics data structure"""
    creator_id: str
    timeframe: AnalyticsTimeframe
    period_start: datetime
    period_end: datetime
    gross_revenue: Decimal
    net_revenue: Decimal
    platform_breakdown: Dict[str, Decimal]
    growth_rate: float
    transaction_count: int
    average_transaction: Decimal
    top_revenue_sources: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalyticsInsight:
    """Analytics insight data structure"""
    insight_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    insight_type: str = ""
    title: str = ""
    description: str = ""
    impact_score: float = 0.0
    confidence_level: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    data_points: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


class RevenueAnalytics:
    """
    Ultra-advanced revenue analytics system for content creators
    
    Features:
    - Real-time revenue analytics and KPI tracking
    - Predictive revenue modeling with ML
    - Multi-platform performance comparison
    - Automated insights and recommendations
    - Advanced statistical analysis and forecasting
    - Industry benchmarking and peer comparison
    - Custom dashboard generation
    - Anomaly detection and trend analysis
    """
    
    def __init__(self,
                 db_manager: DatabaseManager,
                 security_manager: SecurityManager,
                 metrics_collector: MetricsCollector):
        self.db = db_manager
        self.security = security_manager
        self.metrics = metrics_collector
        self.analytics_engine = AnalyticsEngine()
        self.prediction_model = RevenuePredictionModel()
        self.chart_generator = ChartGenerator()
        
        # Analytics configuration
        self._analytics_config = {}
        self._cached_metrics = {}
        self._benchmark_data = {}
        
        # ML models and processors
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)  # Retain 95% variance
        
    async def initialize(self):
        """Initialize the revenue analytics system"""



        try:
            # Initialize analytics engine
            await self.analytics_engine.initialize()
            
            # Load prediction models
            await self.prediction_model.load_models()
            
            # Initialize chart generator
            await self.chart_generator.initialize()
            
            # Load analytics configuration
            await self._load_analytics_configuration()
            
            # Load benchmark data
            await self._load_benchmark_data()
            
            logger.info("Revenue analytics initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize revenue analytics: {e}")
            raise

    async def generate_revenue_report(self,
                                    creator_id: str,
                                    timeframe: AnalyticsTimeframe,
                                    date_range: Optional[Tuple[datetime, datetime]] = None,
                                    include_predictions: bool = True,
                                    include_benchmarks: bool = True) -> Dict[str, Any]:
        """
        Generate comprehensive revenue analytics report
        
        Args:
            creator_id: Creator ID
            timeframe: Analytics timeframe
            date_range: Custom date range (optional)
            include_predictions: Include revenue predictions
            include_benchmarks: Include benchmark comparisons
            
        Returns:
            Comprehensive revenue analytics report
        """



        try:
            # Determine date range based on timeframe
            if not date_range:
                date_range = self._get_timeframe_date_range(timeframe)
            
            # Calculate core revenue metrics
            revenue_metrics = await self._calculate_revenue_metrics(
                creator_id, timeframe, date_range
            )
            
            # Generate performance insights
            insights = await self._generate_performance_insights(
                creator_id, revenue_metrics, timeframe
            )
            
            # Platform performance analysis
            platform_analysis = await self._analyze_platform_performance(
                creator_id, date_range
            )
            
            # Trend analysis
            trend_analysis = await self._perform_trend_analysis(
                creator_id, timeframe, date_range
            )
            
            # Revenue forecasting (if requested)
            predictions = {}
            if include_predictions:
                predictions = await self._generate_revenue_predictions(
                    creator_id, timeframe
                )
            
            # Benchmark comparison (if requested)
            benchmarks = {}
            if include_benchmarks:
                benchmarks = await self._perform_benchmark_analysis(
                    creator_id, revenue_metrics
                )
            
            # Generate visualizations
            charts = await self._generate_revenue_charts(
                creator_id, revenue_metrics, platform_analysis
            )
            
            # Compile comprehensive report
            report = {
                'report_id': str(uuid.uuid4()),
                'creator_id': creator_id,
                'timeframe': timeframe.value,
                'date_range': {
                    'start': date_range[0].isoformat(),
                    'end': date_range[1].isoformat()
                },
                'generated_at': datetime.utcnow().isoformat(),
                'metrics': {
                    'gross_revenue': float(revenue_metrics.gross_revenue),
                    'net_revenue': float(revenue_metrics.net_revenue),
                    'growth_rate': revenue_metrics.growth_rate,
                    'transaction_count': revenue_metrics.transaction_count,
                    'average_transaction': float(revenue_metrics.average_transaction),
                    'platform_breakdown': {k: float(v) for k, v in revenue_metrics.platform_breakdown.items()},
                    'top_revenue_sources': revenue_metrics.top_revenue_sources
                },
                'insights': [
                    {
                        'type': insight.insight_type,
                        'title': insight.title,
                        'description': insight.description,
                        'impact_score': insight.impact_score,
                        'confidence': insight.confidence_level,
                        'recommendations': insight.recommendations
                    }
                    for insight in insights
                ],
                'platform_analysis': platform_analysis,
                'trend_analysis': trend_analysis,
                'predictions': predictions,
                'benchmarks': benchmarks,
                'charts': charts
            }
            
            # Store report for future reference
            await self._store_analytics_report(report)
            
            # Update metrics
            await self.metrics.record_analytics_report_generation(report)
            
            logger.info(f"Revenue analytics report generated for creator {creator_id}")
            return report
            
        except Exception as e:
            logger.error(f"Revenue report generation failed: {e}")
            raise

    async def _calculate_revenue_metrics(self,
                                       creator_id: str,
                                       timeframe: AnalyticsTimeframe,
                                       date_range: Tuple[datetime, datetime]) -> RevenueMetrics:
        """Calculate comprehensive revenue metrics"""



        try:
            # Query revenue data for the period
            revenue_query = """
                SELECT 
                    platform,
                    revenue_type,
                    SUM(gross_amount) as gross_revenue,
                    SUM(net_amount) as net_revenue,
                    SUM(platform_fee + taxes + commission) as total_deductions,
                    COUNT(*) as transaction_count,
                    AVG(net_amount) as avg_transaction
                FROM revenue_calculations 
                WHERE creator_id = %s 
                AND calculation_date BETWEEN %s AND %s
                GROUP BY platform, revenue_type
                ORDER BY gross_revenue DESC
            """
            
            revenue_data = await self.db.fetch_all(revenue_query, (
                creator_id, date_range[0], date_range[1]
            ))
            
            # Calculate aggregate metrics
            total_gross = sum(Decimal(str(row['gross_revenue'])) for row in revenue_data)
            total_net = sum(Decimal(str(row['net_revenue'])) for row in revenue_data)
            total_transactions = sum(row['transaction_count'] for row in revenue_data)
            
            # Platform breakdown
            platform_breakdown = {}
            for row in revenue_data:
                platform = row['platform']
                if platform not in platform_breakdown:
                    platform_breakdown[platform] = Decimal('0')
                platform_breakdown[platform] += Decimal(str(row['net_revenue']))
            
            # Calculate growth rate
            growth_rate = await self._calculate_growth_rate(
                creator_id, date_range, timeframe
            )
            
            # Top revenue sources
            top_sources = await self._identify_top_revenue_sources(
                creator_id, date_range
            )
            
            # Average transaction value
            avg_transaction = total_net / total_transactions if total_transactions > 0 else Decimal('0')
            
            return RevenueMetrics(
                creator_id=creator_id,
                timeframe=timeframe,
                period_start=date_range[0],
                period_end=date_range[1],
                gross_revenue=total_gross,
                net_revenue=total_net,
                platform_breakdown=platform_breakdown,
                growth_rate=growth_rate,
                transaction_count=total_transactions,
                average_transaction=avg_transaction,
                top_revenue_sources=top_sources
            )
            
        except Exception as e:
            logger.error(f"Revenue metrics calculation failed: {e}")
            raise

    async def _generate_performance_insights(self,
                                           creator_id: str,
                                           metrics: RevenueMetrics,
                                           timeframe: AnalyticsTimeframe) -> List[AnalyticsInsight]:
        """Generate AI-powered performance insights"""



        try:
            insights = []
            
            # Revenue growth insight
            if abs(metrics.growth_rate) > 10:  # Significant growth/decline
                growth_insight = AnalyticsInsight(
                    creator_id=creator_id,
                    insight_type="revenue_growth",
                    title=f"{'Strong Growth' if metrics.growth_rate > 0 else 'Revenue Decline'} Detected",
                    description=f"Your revenue has {'grown' if metrics.growth_rate > 0 else 'declined'} by {abs(metrics.growth_rate):.1f}% in the last {timeframe.value}.",
                    impact_score=min(abs(metrics.growth_rate) / 10, 10.0),
                    confidence_level=0.85,
                    recommendations=await self._generate_growth_recommendations(metrics.growth_rate, metrics)
                )
                insights.append(growth_insight)
            
            # Platform performance insight
            if metrics.platform_breakdown:
                top_platform = max(metrics.platform_breakdown, key=metrics.platform_breakdown.get)
                top_platform_revenue = metrics.platform_breakdown[top_platform]
                platform_percentage = (top_platform_revenue / metrics.net_revenue) * 100
                
                if platform_percentage > 60:  # High platform concentration
                    platform_insight = AnalyticsInsight(
                        creator_id=creator_id,
                        insight_type="platform_concentration",
                        title="High Platform Concentration Risk",
                        description=f"{top_platform.title()} accounts for {platform_percentage:.1f}% of your revenue, creating concentration risk.",
                        impact_score=platform_percentage / 10,
                        confidence_level=0.9,
                        recommendations=[
                            f"Diversify revenue streams across other platforms",
                            f"Explore additional monetization options on {top_platform}",
                            "Consider building direct-to-fan revenue channels"
                        ]
                    )
                    insights.append(platform_insight)
            
            # Transaction size analysis
            if metrics.average_transaction < Decimal('10'):
                transaction_insight = AnalyticsInsight(
                    creator_id=creator_id,
                    insight_type="transaction_optimization",
                    title="Low Average Transaction Value",
                    description=f"Your average transaction value is ${metrics.average_transaction:.2f}, which may indicate opportunities for optimization.",
                    impact_score=5.0,
                    confidence_level=0.75,
                    recommendations=[
                        "Explore premium content offerings",
                        "Bundle multiple products/services together",
                        "Implement tiered pricing strategies"
                    ]
                )
                insights.append(transaction_insight)
            
            # Seasonal pattern insights
            seasonal_insights = await self._analyze_seasonal_patterns(creator_id, timeframe)
            insights.extend(seasonal_insights)
            
            # Anomaly detection insights
            anomaly_insights = await self._detect_revenue_anomalies(creator_id, metrics)
            insights.extend(anomaly_insights)
            
            return insights
            
        except Exception as e:
            logger.error(f"Performance insights generation failed: {e}")
            return []

    async def _analyze_platform_performance(self,
                                          creator_id: str,
                                          date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Analyze performance across different platforms"""



        try:
            # Get platform-specific metrics
            platform_query = """
                SELECT 
                    platform,
                    SUM(gross_amount) as gross_revenue,
                    SUM(net_amount) as net_revenue,
                    SUM(platform_fee) as platform_fees,
                    COUNT(*) as transaction_count,
                    AVG(net_amount) as avg_transaction,
                    MIN(calculation_date) as first_transaction,
                    MAX(calculation_date) as last_transaction
                FROM revenue_calculations 
                WHERE creator_id = %s 
                AND calculation_date BETWEEN %s AND %s
                GROUP BY platform
                ORDER BY net_revenue DESC
            """
            
            platform_data = await self.db.fetch_all(platform_query, (
                creator_id, date_range[0], date_range[1]
            ))
            
            analysis = {
                'total_platforms': len(platform_data),
                'platforms': [],
                'top_performer': None,
                'most_efficient': None,
                'growth_leaders': [],
                'recommendations': []
            }
            
            total_revenue = sum(Decimal(str(row['net_revenue'])) for row in platform_data)
            
            for row in platform_data:
                platform_name = row['platform']
                net_revenue = Decimal(str(row['net_revenue']))
                gross_revenue = Decimal(str(row['gross_revenue']))
                platform_fees = Decimal(str(row['platform_fees']))
                
                # Calculate efficiency (net revenue / gross revenue)
                efficiency = (net_revenue / gross_revenue * 100) if gross_revenue > 0 else 0
                
                # Calculate market share
                market_share = (net_revenue / total_revenue * 100) if total_revenue > 0 else 0
                
                # Get growth rate for this platform
                platform_growth = await self._calculate_platform_growth_rate(
                    creator_id, platform_name, date_range
                )
                
                platform_info = {
                    'platform': platform_name,
                    'gross_revenue': float(gross_revenue),
                    'net_revenue': float(net_revenue),
                    'platform_fees': float(platform_fees),
                    'efficiency_percentage': float(efficiency),
                    'market_share_percentage': float(market_share),
                    'transaction_count': row['transaction_count'],
                    'average_transaction': float(row['avg_transaction']),
                    'growth_rate': platform_growth,
                    'days_active': (row['last_transaction'] - row['first_transaction']).days + 1
                }
                
                analysis['platforms'].append(platform_info)
            
            # Identify top performer (highest revenue)
            if analysis['platforms']:
                analysis['top_performer'] = max(analysis['platforms'], key=lambda x: x['net_revenue'])
                
                # Identify most efficient platform
                analysis['most_efficient'] = max(analysis['platforms'], key=lambda x: x['efficiency_percentage'])
                
                # Identify growth leaders (positive growth > 15%)
                analysis['growth_leaders'] = [
                    p for p in analysis['platforms'] 
                    if p['growth_rate'] > 15
                ]
                
                # Generate platform-specific recommendations
                analysis['recommendations'] = await self._generate_platform_recommendations(
                    analysis['platforms']
                )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Platform performance analysis failed: {e}")
            return {}

    async def _perform_trend_analysis(self,
                                    creator_id: str,
                                    timeframe: AnalyticsTimeframe,
                                    date_range: Tuple[datetime, datetime]) -> Dict[str, Any]:
        """Perform comprehensive trend analysis"""



        try:
            # Get time-series revenue data
            if timeframe == AnalyticsTimeframe.DAILY:
                date_trunc = "day"
                interval = "1 day"
            elif timeframe == AnalyticsTimeframe.WEEKLY:
                date_trunc = "week"
                interval = "1 week"
            elif timeframe == AnalyticsTimeframe.MONTHLY:
                date_trunc = "month"
                interval = "1 month"
            else:
                date_trunc = "day"
                interval = "1 day"
            
            trend_query = f"""
                SELECT 
                    DATE_TRUNC('{date_trunc}', calculation_date) as period,
                    SUM(net_amount) as revenue,
                    COUNT(*) as transactions,
                    AVG(net_amount) as avg_transaction
                FROM revenue_calculations 
                WHERE creator_id = %s 
                AND calculation_date BETWEEN %s AND %s
                GROUP BY DATE_TRUNC('{date_trunc}', calculation_date)
                ORDER BY period ASC
            """
            
            trend_data = await self.db.fetch_all(trend_query, (
                creator_id, date_range[0], date_range[1]
            ))
            
            if len(trend_data) < 3:
                return {'error': 'Insufficient data for trend analysis'}
            
            # Prepare data for analysis
            revenues = [float(row['revenue']) for row in trend_data]
            transactions = [row['transactions'] for row in trend_data]
            periods = [row['period'] for row in trend_data]
            
            # Statistical trend analysis
            x = np.arange(len(revenues))
            
            # Linear regression for trend
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, revenues)
            
            # Moving averages
            ma_7 = self._calculate_moving_average(revenues, 7)
            ma_30 = self._calculate_moving_average(revenues, 30) if len(revenues) >= 30 else []
            
            # Volatility analysis
            revenue_std = np.std(revenues)
            revenue_mean = np.mean(revenues)
            volatility = (revenue_std / revenue_mean * 100) if revenue_mean > 0 else 0
            
            # Trend classification
            trend_direction = "upward" if slope > 0 else "downward" if slope < 0 else "flat"
            trend_strength = "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.3 else "weak"
            
            # Seasonal analysis
            seasonal_analysis = await self._analyze_seasonality(revenues, periods)
            
            # Cycle detection
            cycles = await self._detect_revenue_cycles(revenues, periods)
            
            return {
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'slope': slope,
                'r_squared': r_value ** 2,
                'p_value': p_value,
                'volatility_percentage': volatility,
                'moving_averages': {
                    '7_period': ma_7[-1] if ma_7 else None,
                    '30_period': ma_30[-1] if ma_30 else None
                },
                'seasonal_patterns': seasonal_analysis,
                'detected_cycles': cycles,
                'data_points': len(trend_data),
                'analysis_confidence': self._calculate_trend_confidence(len(trend_data), abs(r_value))
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {}

    async def _generate_revenue_predictions(self,
                                          creator_id: str,
                                          timeframe: AnalyticsTimeframe) -> Dict[str, Any]:
        """Generate AI-powered revenue predictions"""



        try:
            # Get historical data for prediction model
            historical_data = await self._get_historical_revenue_data(creator_id, 90)  # Last 90 days
            
            if len(historical_data) < 10:
                return {'error': 'Insufficient historical data for predictions'}
            
            # Prepare features for prediction model
            features = await self._prepare_prediction_features(creator_id, historical_data)
            
            # Generate predictions using ML model
            predictions = await self.prediction_model.predict_revenue(
                creator_id, features, timeframe
            )
            
            # Calculate prediction intervals
            prediction_intervals = await self._calculate_prediction_intervals(
                historical_data, predictions
            )
            
            # Generate scenario analysis
            scenarios = await self._generate_revenue_scenarios(creator_id, predictions)
            
            return {
                'predictions': predictions,
                'prediction_intervals': prediction_intervals,
                'scenarios': scenarios,
                'model_accuracy': await self.prediction_model.get_model_accuracy(creator_id),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Revenue predictions generation failed: {e}")
            return {}

    async def _perform_benchmark_analysis(self,
                                        creator_id: str,
                                        metrics: RevenueMetrics) -> Dict[str, Any]:
        """Perform benchmark analysis against peers and industry"""



        try:
            # Get creator category and tier for benchmarking
            creator_info = await self.db.fetch_one("""
                SELECT category, tier, follower_count, content_type 
                FROM creators 
                WHERE id = %s
            """, (creator_id,))
            
            if not creator_info:
                return {'error': 'Creator information not found'}
            
            # Get peer benchmarks (similar creators)
            peer_benchmarks = await self._get_peer_benchmarks(
                creator_info['category'],
                creator_info['tier'],
                creator_info['follower_count']
            )
            
            # Get industry benchmarks
            industry_benchmarks = await self._get_industry_benchmarks(
                creator_info['category'],
                creator_info['content_type']
            )
            
            # Calculate percentile rankings
            peer_percentile = await self._calculate_percentile_ranking(
                float(metrics.net_revenue), peer_benchmarks
            )
            
            industry_percentile = await self._calculate_percentile_ranking(
                float(metrics.net_revenue), industry_benchmarks
            )
            
            return {
                'peer_comparison': {
                    'your_revenue': float(metrics.net_revenue),
                    'peer_average': peer_benchmarks.get('average', 0),
                    'peer_median': peer_benchmarks.get('median', 0),
                    'peer_percentile': peer_percentile,
                    'peer_count': peer_benchmarks.get('count', 0)
                },
                'industry_comparison': {
                    'industry_average': industry_benchmarks.get('average', 0),
                    'industry_median': industry_benchmarks.get('median', 0),
                    'industry_percentile': industry_percentile,
                    'top_10_percent_threshold': industry_benchmarks.get('top_10_percent', 0)
                },
                'performance_rating': await self._calculate_performance_rating(
                    peer_percentile, industry_percentile
                )
            }
            
        except Exception as e:
            logger.error(f"Benchmark analysis failed: {e}")
            return {}

    def _get_timeframe_date_range(self, timeframe: AnalyticsTimeframe) -> Tuple[datetime, datetime]:
        """Get date range based on timeframe"""
        end_date = datetime.utcnow()
        
        if timeframe == AnalyticsTimeframe.DAILY:
            start_date = end_date - timedelta(days=1)
        elif timeframe == AnalyticsTimeframe.WEEKLY:
            start_date = end_date - timedelta(weeks=1)
        elif timeframe == AnalyticsTimeframe.MONTHLY:
            start_date = end_date - timedelta(days=30)
        elif timeframe == AnalyticsTimeframe.QUARTERLY:
            start_date = end_date - timedelta(days=90)
        elif timeframe == AnalyticsTimeframe.YEARLY:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)  # Default to monthly
        
        return start_date, end_date

    def _calculate_moving_average(self, data: List[float], window: int) -> List[float]:
        """Calculate moving average for data series"""
        if len(data) < window:
            return []
        
        moving_averages = []
        for i in range(window - 1, len(data)):
            window_data = data[i - window + 1:i + 1]
            moving_averages.append(sum(window_data) / window)
        
        return moving_averages

    async def cleanup(self):
        """Cleanup analytics resources"""



        try:
            # Cleanup analytics engine
            await self.analytics_engine.cleanup()
            
            # Cleanup prediction model
            await self.prediction_model.cleanup()
            
            # Cleanup chart generator
            await self.chart_generator.cleanup()
            
            logger.info("Revenue analytics cleanup completed")
            
        except Exception as e:
            logger.error(f"Revenue analytics cleanup failed: {e}")
