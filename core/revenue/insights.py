"""
Revenue Insights Engine - Advanced AI-powered revenue intelligence and insights system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

  STRICT COPYRIGHT WARNING 
This code is the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, reproduction, modification, or distribution without explicit 
written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.


REVENUE INSIGHTS ENGINE - ENTERPRISE EDITION


Developed by Expert Team:
 Lead Dev IA: Fahed Mlaiel (Advanced AI/ML Architecture)
  Backend Senior: System Architecture & Performance Optimization  
🤖 ML Engineer: Revenue Forecasting & Optimization Algorithms
  DBA: Advanced Data Management & Analytics
 Security Expert: Enterprise-Grade Security & Encryption
 Microservices: Scalable Distributed Architecture
 Audio Expert: Audio Revenue Stream Optimization
  DevOps: Production Infrastructure & Monitoring
🧠 IA Prompt Engineer: AI-Powered Decision Making
"""

import asyncio
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
import uuid
import statistics

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.decomposition import PCA
import networkx as nx

logger = logging.getLogger(__name__)


class InsightType(Enum):
    """Types of revenue insights"""
    TREND_ANALYSIS = "trend_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    PATTERN_RECOGNITION = "pattern_recognition"
    PREDICTIVE_INSIGHT = "predictive_insight"
    OPTIMIZATION_OPPORTUNITY = "optimization_opportunity"
    RISK_ASSESSMENT = "risk_assessment"
    MARKET_INTELLIGENCE = "market_intelligence"
    CUSTOMER_BEHAVIOR = "customer_behavior"
    SEASONAL_PATTERN = "seasonal_pattern"
    PERFORMANCE_BENCHMARK = "performance_benchmark"


class InsightPriority(Enum):
    """Priority levels for insights"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class InsightCategory(Enum):
    """Categories of insights"""
    REVENUE_OPTIMIZATION = "revenue_optimization"
    COST_MANAGEMENT = "cost_management"
    MARKET_OPPORTUNITY = "market_opportunity"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    CUSTOMER_INSIGHTS = "customer_insights"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    STRATEGIC_PLANNING = "strategic_planning"
    RISK_MITIGATION = "risk_mitigation"


@dataclass
class ActionableInsight:
    """Actionable revenue insight"""
    insight_id: str
    type: InsightType
    category: InsightCategory
    priority: InsightPriority
    title: str
    description: str
    key_findings: List[str]
    recommended_actions: List[str]
    potential_impact: Decimal
    confidence_score: float
    time_sensitivity: str  # immediate, short_term, medium_term, long_term
    data_sources: List[str]
    supporting_evidence: Dict[str, Any]
    related_insights: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    @property
    def age_hours(self) -> int:
        """Get age of insight in hours"""



        return int((datetime.utcnow() - self.created_at).total_seconds() / 3600)
    
    @property
    def is_expired(self) -> bool:
        """Check if insight has expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


@dataclass
class InsightCluster:
    """Cluster of related insights"""
    cluster_id: str
    theme: str
    insights: List[ActionableInsight]
    combined_impact: Decimal
    priority: InsightPriority
    recommended_approach: str
    synergy_score: float
    
    @property
    def insight_count(self) -> int:
        """Get number of insights in cluster"""



        return len(self.insights)


@dataclass
class InsightTrend:
    """Trend analysis for insights"""
    trend_id: str
    metric_name: str
    time_period: str
    trend_direction: str  # increasing, decreasing, stable, volatile
    trend_strength: float  # 0-1
    statistical_significance: float
    trend_equation: str
    forecast_values: List[Decimal]
    turning_points: List[datetime]
    seasonality_detected: bool


class RevenueInsightsEngine:
    """Advanced AI-powered revenue insights and intelligence engine"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.insights_database = []
        self.ml_models = {}
        self.pattern_library = {}
        self.insight_clusters = []
        self.scaler = StandardScaler()
        
        # Analysis parameters
        self.anomaly_threshold = self.config.get('anomaly_threshold', 0.05)
        self.trend_window = self.config.get('trend_window', 30)  # days
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        
    async def initialize(self) -> None:
        """Initialize insights engine"""



        try:
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Load pattern library
            await self._load_pattern_library()
            
            # Setup insight templates
            await self._setup_insight_templates()
            
            logger.info("Revenue insights engine initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing insights engine: {e}")
            raise
    
    async def _initialize_ml_models(self) -> None:
        """Initialize machine learning models"""
        # Anomaly detection model
        self.ml_models['anomaly_detector'] = IsolationForest(
            contamination=self.anomaly_threshold,
            random_state=42
        )
        
        # Clustering model for pattern recognition
        self.ml_models['pattern_clusterer'] = KMeans(
            n_clusters=8,
            random_state=42
        )
        
        # Trend detection model
        self.ml_models['trend_detector'] = DBSCAN(
            eps=0.5,
            min_samples=3
        )
        
        # Dimensionality reduction for insights
        self.ml_models['dimension_reducer'] = PCA(
            n_components=0.95,  # Retain 95% of variance
            random_state=42
        )
    
    async def _load_pattern_library(self) -> None:
        """Load revenue pattern library"""
        # Revenue patterns for different scenarios
        self.pattern_library = {
            'seasonal_patterns': {
                'holiday_boost': {
                    'description': 'Revenue increase during holiday periods',
                    'multiplier': 1.3,
                    'duration_days': 7,
                    'certainty': 0.9
                },
                'summer_dip': {
                    'description': 'Revenue decrease during summer months',
                    'multiplier': 0.85,
                    'duration_days': 60,
                    'certainty': 0.7
                },
                'back_to_school': {
                    'description': 'Revenue boost in September',
                    'multiplier': 1.15,
                    'duration_days': 14,
                    'certainty': 0.8
                }
            },
            'growth_patterns': {
                'viral_growth': {
                    'description': 'Exponential growth from viral content',
                    'growth_rate': 2.5,
                    'sustainability': 0.3,
                    'indicators': ['sudden_spike', 'social_mentions', 'share_rate']
                },
                'organic_growth': {
                    'description': 'Steady organic growth',
                    'growth_rate': 0.05,
                    'sustainability': 0.9,
                    'indicators': ['consistent_increase', 'retention_growth']
                }
            },
            'risk_patterns': {
                'platform_dependency': {
                    'description': 'High dependency on single platform',
                    'risk_level': 0.8,
                    'indicators': ['single_platform_dominance', 'concentration_ratio']
                },
                'revenue_volatility': {
                    'description': 'High revenue volatility',
                    'risk_level': 0.7,
                    'indicators': ['high_variance', 'irregular_patterns']
                }
            }
        }
    
    async def _setup_insight_templates(self) -> None:
        """Setup insight generation templates"""
        self.insight_templates = {
            InsightType.TREND_ANALYSIS: self._generate_trend_insight,
            InsightType.ANOMALY_DETECTION: self._generate_anomaly_insight,
            InsightType.PATTERN_RECOGNITION: self._generate_pattern_insight,
            InsightType.PREDICTIVE_INSIGHT: self._generate_predictive_insight,
            InsightType.OPTIMIZATION_OPPORTUNITY: self._generate_optimization_insight,
            InsightType.RISK_ASSESSMENT: self._generate_risk_insight,
            InsightType.MARKET_INTELLIGENCE: self._generate_market_insight,
            InsightType.CUSTOMER_BEHAVIOR: self._generate_customer_insight,
            InsightType.SEASONAL_PATTERN: self._generate_seasonal_insight,
            InsightType.PERFORMANCE_BENCHMARK: self._generate_benchmark_insight
        }
    
    async def generate_comprehensive_insights(
        self,
        revenue_data: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ActionableInsight]:
        """Generate comprehensive revenue insights"""



        try:
            insights = []
            context = context or {}
            
            # Prepare data for analysis
            processed_data = await self._prepare_data_for_analysis(
                revenue_data, historical_data
            )
            
            # Generate insights for each type
            for insight_type in InsightType:
                try:
                    insight_generator = self.insight_templates.get(insight_type)
                    if insight_generator:
                        type_insights = await insight_generator(
                            processed_data, context
                        )
                        insights.extend(type_insights)
                except Exception as e:
                    logger.warning(f"Error generating {insight_type.value} insights: {e}")
            
            # Filter and rank insights
            filtered_insights = await self._filter_and_rank_insights(insights)
            
            # Identify related insights
            clustered_insights = await self._cluster_related_insights(filtered_insights)
            
            # Store in database
            self.insights_database.extend(clustered_insights)
            
            return clustered_insights
            
        except Exception as e:
            logger.error(f"Error generating comprehensive insights: {e}")
            raise
    
    async def _prepare_data_for_analysis(
        self,
        revenue_data: Dict[str, Any],
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Prepare data for insight analysis"""
        processed_data = {
            'current_revenue': Decimal(str(revenue_data.get('monthly_revenue', 0))),
            'revenue_streams': revenue_data.get('revenue_streams', {}),
            'platform_data': revenue_data.get('platform_data', {}),
            'engagement_metrics': revenue_data.get('engagement_metrics', {}),
            'growth_metrics': revenue_data.get('growth_metrics', {}),
            'historical_series': [],
            'derived_metrics': {}
        }
        
        # Process historical data
        if historical_data:
            processed_data['historical_series'] = [
                {
                    'date': datetime.fromisoformat(item['date']) if isinstance(item['date'], str) else item['date'],
                    'revenue': Decimal(str(item.get('revenue', 0))),
                    'metrics': item.get('metrics', {})
                }
                for item in historical_data
            ]
            
            # Calculate derived metrics
            processed_data['derived_metrics'] = await self._calculate_derived_metrics(
                processed_data['historical_series']
            )
        
        return processed_data
    
    async def _calculate_derived_metrics(
        self,
        historical_series: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate derived metrics from historical data"""
        if not historical_series:
            return {}
        
        revenues = [float(item['revenue']) for item in historical_series]
        dates = [item['date'] for item in historical_series]
        
        derived = {}
        
        # Growth rate calculation
        if len(revenues) > 1:
            growth_rates = [
                (revenues[i] - revenues[i-1]) / revenues[i-1] * 100
                for i in range(1, len(revenues))
                if revenues[i-1] > 0
            ]
            
            if growth_rates:
                derived['avg_growth_rate'] = statistics.mean(growth_rates)
                derived['growth_rate_variance'] = statistics.variance(growth_rates) if len(growth_rates) > 1 else 0
                derived['growth_trend'] = 'increasing' if derived['avg_growth_rate'] > 0 else 'decreasing'
        
        # Volatility metrics
        if len(revenues) > 2:
            derived['revenue_volatility'] = statistics.stdev(revenues) / statistics.mean(revenues)
            derived['coefficient_of_variation'] = derived['revenue_volatility']
        
        # Trend strength
        if len(revenues) > 3:
            x_values = list(range(len(revenues)))
            correlation, p_value = stats.pearsonr(x_values, revenues)
            derived['trend_strength'] = abs(correlation)
            derived['trend_significance'] = p_value
        
        # Seasonality detection
        if len(revenues) >= 12:  # Need at least 12 data points
            derived['seasonality_score'] = await self._detect_seasonality(revenues, dates)
        
        return derived
    
    async def _detect_seasonality(
        self,
        revenues: List[float],
        dates: List[datetime]
    ) -> float:
        """Detect seasonality in revenue data"""
        # Simple seasonality detection based on month-over-month patterns
        if len(revenues) < 12:
            return 0.0
        
        monthly_revenues = {}
        for revenue, date in zip(revenues, dates):
            month = date.month
            if month not in monthly_revenues:
                monthly_revenues[month] = []
            monthly_revenues[month].append(revenue)
        
        # Calculate monthly averages
        monthly_averages = {}
        for month, month_revenues in monthly_revenues.items():
            monthly_averages[month] = statistics.mean(month_revenues)
        
        if len(monthly_averages) < 6:  # Need at least 6 months
            return 0.0
        
        # Calculate variation across months
        avg_values = list(monthly_averages.values())
        overall_mean = statistics.mean(avg_values)
        variation = statistics.stdev(avg_values) / overall_mean if overall_mean > 0 else 0
        
        # Seasonality score (0-1)
        seasonality_score = min(variation * 2, 1.0)  # Scale to 0-1
        
        return seasonality_score
    
    async def _generate_trend_insight(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[ActionableInsight]:
        """Generate trend analysis insights"""
        insights = []
        
        derived_metrics = data.get('derived_metrics', {})
        
        # Growth trend insight
        growth_rate = derived_metrics.get('avg_growth_rate', 0)
        trend_strength = derived_metrics.get('trend_strength', 0)
        
        if abs(growth_rate) > 5 and trend_strength > 0.7:  # Strong trend
            if growth_rate > 0:
                insight = ActionableInsight(
                    insight_id=str(uuid.uuid4()),
                    type=InsightType.TREND_ANALYSIS,
                    category=InsightCategory.REVENUE_OPTIMIZATION,
                    priority=InsightPriority.HIGH,
                    title="Strong Positive Revenue Trend Detected",
                    description=f"Revenue showing strong upward trend with {growth_rate:.1f}% average growth rate",
                    key_findings=[
                        f"Average growth rate: {growth_rate:.1f}%",
                        f"Trend strength: {trend_strength:.2f}",
                        "Consistent upward trajectory observed"
                    ],
                    recommended_actions=[
                        "Capitalize on current momentum with increased investment",
                        "Analyze successful strategies for replication",
                        "Prepare for scaling operations"
                    ],
                    potential_impact=data['current_revenue'] * Decimal(str(growth_rate / 100)),
                    confidence_score=trend_strength,
                    time_sensitivity="immediate",
                    data_sources=["historical_revenue", "growth_metrics"],
                    supporting_evidence={
                        'growth_rate': growth_rate,
                        'trend_strength': trend_strength,
                        'data_points': len(data.get('historical_series', []))
                    }
                )
            else:
                insight = ActionableInsight(
                    insight_id=str(uuid.uuid4()),
                    type=InsightType.TREND_ANALYSIS,
                    category=InsightCategory.RISK_MITIGATION,
                    priority=InsightPriority.CRITICAL,
                    title="Concerning Downward Revenue Trend",
                    description=f"Revenue showing strong downward trend with {abs(growth_rate):.1f}% average decline",
                    key_findings=[
                        f"Average decline rate: {abs(growth_rate):.1f}%",
                        f"Trend strength: {trend_strength:.2f}",
                        "Sustained downward trajectory requires immediate attention"
                    ],
                    recommended_actions=[
                        "Implement immediate revenue recovery strategies",
                        "Analyze root causes of decline",
                        "Consider emergency cost reduction measures"
                    ],
                    potential_impact=data['current_revenue'] * Decimal(str(abs(growth_rate) / 100)),
                    confidence_score=trend_strength,
                    time_sensitivity="immediate",
                    data_sources=["historical_revenue", "growth_metrics"],
                    supporting_evidence={
                        'decline_rate': abs(growth_rate),
                        'trend_strength': trend_strength,
                        'urgency_level': 'critical'
                    }
                )
            
            insights.append(insight)
        
        return insights
    
    async def _generate_anomaly_insight(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[ActionableInsight]:
        """Generate anomaly detection insights"""
        insights = []
        
        historical_series = data.get('historical_series', [])
        
        if len(historical_series) < 10:  # Need sufficient data
            return insights
        
        # Prepare data for anomaly detection
        revenues = np.array([[float(item['revenue'])] for item in historical_series])
        
        # Fit anomaly detection model
        anomaly_detector = self.ml_models['anomaly_detector']
        anomaly_detector.fit(revenues)
        
        # Detect anomalies
        anomaly_scores = anomaly_detector.decision_function(revenues)
        is_anomaly = anomaly_detector.predict(revenues)
        
        # Find recent anomalies
        recent_anomalies = []
        for i, (score, is_anom) in enumerate(zip(anomaly_scores, is_anomaly)):
            if is_anom == -1 and i >= len(historical_series) - 7:  # Last 7 data points
                recent_anomalies.append({
                    'index': i,
                    'date': historical_series[i]['date'],
                    'revenue': historical_series[i]['revenue'],
                    'anomaly_score': score
                })
        
        if recent_anomalies:
            # Most significant recent anomaly
            most_significant = min(recent_anomalies, key=lambda x: x['anomaly_score'])
            
            # Determine if positive or negative anomaly
            recent_revenues = [float(item['revenue']) for item in historical_series[-10:]]
            avg_recent = statistics.mean(recent_revenues)
            
            is_positive_anomaly = float(most_significant['revenue']) > avg_recent
            
            insight = ActionableInsight(
                insight_id=str(uuid.uuid4()),
                type=InsightType.ANOMALY_DETECTION,
                category=InsightCategory.REVENUE_OPTIMIZATION if is_positive_anomaly else InsightCategory.RISK_MITIGATION,
                priority=InsightPriority.HIGH,
                title=f"{'Positive' if is_positive_anomaly else 'Negative'} Revenue Anomaly Detected",
                description=f"Unusual revenue pattern detected on {most_significant['date'].strftime('%Y-%m-%d')}",
                key_findings=[
                    f"Anomaly severity: {abs(most_significant['anomaly_score']):.2f}",
                    f"Revenue value: €{most_significant['revenue']}",
                    f"Deviation from recent average: {(float(most_significant['revenue']) - avg_recent) / avg_recent * 100:.1f}%"
                ],
                recommended_actions=[
                    "Investigate the specific factors that caused this anomaly",
                    "Document the conditions for future reference",
                    "Consider if this represents a new normal or one-time event"
                ] if is_positive_anomaly else [
                    "Immediately investigate the cause of revenue drop",
                    "Implement corrective measures",
                    "Monitor closely for recurrence"
                ],
                potential_impact=abs(Decimal(str(float(most_significant['revenue']) - avg_recent))),
                confidence_score=min(abs(most_significant['anomaly_score']) / 2, 1.0),
                time_sensitivity="immediate",
                data_sources=["historical_revenue", "anomaly_detection"],
                supporting_evidence={
                    'anomaly_date': most_significant['date'].isoformat(),
                    'anomaly_score': most_significant['anomaly_score'],
                    'recent_average': avg_recent,
                    'anomaly_count': len(recent_anomalies)
                }
            )
            
            insights.append(insight)
        
        return insights
    
    async def _generate_pattern_insight(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[ActionableInsight]:
        """Generate pattern recognition insights"""
        insights = []
        
        revenue_streams = data.get('revenue_streams', {})
        
        # Platform concentration analysis
        if revenue_streams:
            total_revenue = sum(Decimal(str(revenue)) for revenue in revenue_streams.values())
            
            if total_revenue > 0:
                # Calculate concentration ratio
                sorted_streams = sorted(revenue_streams.items(), key=lambda x: Decimal(str(x[1])), reverse=True)
                top_stream_ratio = Decimal(str(sorted_streams[0][1])) / total_revenue
                
                if top_stream_ratio > Decimal('0.7'):  # >70% concentration
                    insight = ActionableInsight(
                        insight_id=str(uuid.uuid4()),
                        type=InsightType.PATTERN_RECOGNITION,
                        category=InsightCategory.RISK_MITIGATION,
                        priority=InsightPriority.HIGH,
                        title="High Revenue Concentration Risk",
                        description=f"Over {float(top_stream_ratio * 100):.1f}% of revenue concentrated in single stream: {sorted_streams[0][0]}",
                        key_findings=[
                            f"Primary revenue source: {sorted_streams[0][0]}",
                            f"Concentration ratio: {float(top_stream_ratio * 100):.1f}%",
                            "High dependency creates vulnerability to platform changes"
                        ],
                        recommended_actions=[
                            "Diversify revenue streams across multiple platforms",
                            "Develop alternative revenue sources",
                            "Reduce dependency on single platform"
                        ],
                        potential_impact=Decimal(str(sorted_streams[0][1])) * Decimal('0.5'),  # Potential loss
                        confidence_score=0.9,
                        time_sensitivity="medium_term",
                        data_sources=["revenue_streams"],
                        supporting_evidence={
                            'primary_stream': sorted_streams[0][0],
                            'concentration_ratio': float(top_stream_ratio),
                            'diversification_index': 1 - float(top_stream_ratio)
                        }
                    )
                    
                    insights.append(insight)
        
        return insights
    
    async def _generate_predictive_insight(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[ActionableInsight]:
        """Generate predictive insights"""
        insights = []
        
        derived_metrics = data.get('derived_metrics', {})
        current_revenue = data.get('current_revenue', Decimal('0'))
        
        # Revenue forecasting based on trend
        growth_rate = derived_metrics.get('avg_growth_rate', 0)
        trend_strength = derived_metrics.get('trend_strength', 0)
        
        if trend_strength > 0.6:  # Strong enough trend for prediction
            # 3-month forecast
            months_ahead = 3
            if growth_rate > 0:
                forecasted_revenue = current_revenue * (Decimal(str(1 + growth_rate / 100)) ** months_ahead)
                revenue_increase = forecasted_revenue - current_revenue
                
                insight = ActionableInsight(
                    insight_id=str(uuid.uuid4()),
                    type=InsightType.PREDICTIVE_INSIGHT,
                    category=InsightCategory.STRATEGIC_PLANNING,
                    priority=InsightPriority.MEDIUM,
                    title="Positive Revenue Growth Forecast",
                    description=f"Based on current trends, revenue projected to reach €{forecasted_revenue:.0f} in {months_ahead} months",
                    key_findings=[
                        f"Current monthly revenue: €{current_revenue}",
                        f"Forecasted revenue ({months_ahead} months): €{forecasted_revenue:.0f}",
                        f"Expected increase: €{revenue_increase:.0f} ({float(revenue_increase / current_revenue * 100):.1f}%)"
                    ],
                    recommended_actions=[
                        "Prepare infrastructure for expected growth",
                        "Plan resource allocation for scaling",
                        "Set realistic targets based on projections"
                    ],
                    potential_impact=revenue_increase,
                    confidence_score=trend_strength,
                    time_sensitivity="long_term",
                    data_sources=["trend_analysis", "historical_revenue"],
                    supporting_evidence={
                        'growth_rate': growth_rate,
                        'trend_strength': trend_strength,
                        'forecast_period': months_ahead,
                        'methodology': 'compound_growth_projection'
                    }
                )
                
                insights.append(insight)
        
        return insights
    
    async def _generate_optimization_insight(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[ActionableInsight]:
        """Generate optimization opportunity insights"""
        insights = []
        
        revenue_streams = data.get('revenue_streams', {})
        engagement_metrics = data.get('engagement_metrics', {})
        
        # Revenue per engagement optimization
        if revenue_streams and engagement_metrics:
            engagement_rate = engagement_metrics.get('engagement_rate', 0)
            total_revenue = sum(Decimal(str(revenue)) for revenue in revenue_streams.values())
            
            if engagement_rate > 0:
                revenue_per_engagement = total_revenue / Decimal(str(engagement_rate))
                
                # Compare to benchmarks (simplified)
                benchmark_ratio = 50  # €50 per engagement point benchmark
                
                if float(revenue_per_engagement) < benchmark_ratio * 0.8:  # Below 80% of benchmark
                    optimization_potential = Decimal(str(benchmark_ratio)) - revenue_per_engagement
                    
                    insight = ActionableInsight(
                        insight_id=str(uuid.uuid4()),
                        type=InsightType.OPTIMIZATION_OPPORTUNITY,
                        category=InsightCategory.REVENUE_OPTIMIZATION,
                        priority=InsightPriority.MEDIUM,
                        title="Revenue Per Engagement Optimization Opportunity",
                        description=f"Current revenue per engagement (€{revenue_per_engagement:.0f}) below market benchmark",
                        key_findings=[
                            f"Current revenue per engagement: €{revenue_per_engagement:.0f}",
                            f"Market benchmark: €{benchmark_ratio}",
                            f"Optimization potential: €{optimization_potential:.0f} per engagement point"
                        ],
                        recommended_actions=[
                            "Implement monetization improvements",
                            "Optimize content for higher-value engagement",
                            "Explore premium content offerings"
                        ],
                        potential_impact=optimization_potential * Decimal(str(engagement_rate)),
                        confidence_score=0.7,
                        time_sensitivity="medium_term",
                        data_sources=["revenue_streams", "engagement_metrics"],
                        supporting_evidence={
                            'current_ratio': float(revenue_per_engagement),
                            'benchmark_ratio': benchmark_ratio,
                            'engagement_rate': engagement_rate,
                            'optimization_potential': float(optimization_potential)
                        }
                    )
                    
                    insights.append(insight)
        
        return insights
    
    async def _generate_risk_insight(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[ActionableInsight]:
        """Generate risk assessment insights"""
        insights = []
        
        derived_metrics = data.get('derived_metrics', {})
        
        # Revenue volatility risk
        volatility = derived_metrics.get('revenue_volatility', 0)
        
        if volatility > 0.3:  # High volatility threshold
            insight = ActionableInsight(
                insight_id=str(uuid.uuid4()),
                type=InsightType.RISK_ASSESSMENT,
                category=InsightCategory.RISK_MITIGATION,
                priority=InsightPriority.HIGH,
                title="High Revenue Volatility Detected",
                description=f"Revenue volatility of {volatility:.2f} indicates unstable income patterns",
                key_findings=[
                    f"Revenue volatility coefficient: {volatility:.2f}",
                    "Income unpredictability affects planning",
                    "High volatility may indicate external dependencies"
                ],
                recommended_actions=[
                    "Implement revenue smoothing strategies",
                    "Build financial reserves for volatile periods",
                    "Diversify revenue sources to reduce volatility"
                ],
                potential_impact=data['current_revenue'] * Decimal(str(volatility)),
                confidence_score=0.8,
                time_sensitivity="medium_term",
                data_sources=["historical_revenue", "volatility_analysis"],
                supporting_evidence={
                    'volatility_coefficient': volatility,
                    'risk_level': 'high' if volatility > 0.5 else 'medium',
                    'stability_score': 1 - volatility
                }
            )
            
            insights.append(insight)
        
        return insights
    
    async def _generate_market_insight(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[ActionableInsight]:
        """Generate market intelligence insights"""
        insights = []
        
        # Platform performance comparison
        platform_data = data.get('platform_data', {})
        
        if platform_data:
            # Find best and worst performing platforms
            platform_performance = {}
            for platform, metrics in platform_data.items():
                revenue = Decimal(str(metrics.get('revenue', 0)))
                engagement = metrics.get('engagement_rate', 0)
                
                # Calculate performance score
                performance_score = float(revenue) * engagement
                platform_performance[platform] = {
                    'revenue': revenue,
                    'engagement': engagement,
                    'score': performance_score
                }
            
            if len(platform_performance) > 1:
                sorted_platforms = sorted(
                    platform_performance.items(),
                    key=lambda x: x[1]['score'],
                    reverse=True
                )
                
                best_platform = sorted_platforms[0]
                worst_platform = sorted_platforms[-1]
                
                performance_gap = best_platform[1]['score'] - worst_platform[1]['score']
                
                if performance_gap > best_platform[1]['score'] * 0.5:  # Significant gap
                    insight = ActionableInsight(
                        insight_id=str(uuid.uuid4()),
                        type=InsightType.MARKET_INTELLIGENCE,
                        category=InsightCategory.MARKET_OPPORTUNITY,
                        priority=InsightPriority.MEDIUM,
                        title="Significant Platform Performance Gap",
                        description=f"Large performance difference between {best_platform[0]} and {worst_platform[0]}",
                        key_findings=[
                            f"Best performing platform: {best_platform[0]}",
                            f"Worst performing platform: {worst_platform[0]}",
                            f"Performance gap: {performance_gap:.0f} points"
                        ],
                        recommended_actions=[
                            f"Analyze success factors on {best_platform[0]}",
                            f"Apply successful strategies to {worst_platform[0]}",
                            "Consider reallocating resources to top-performing platforms"
                        ],
                        potential_impact=Decimal(str(performance_gap / 10)),  # Estimated impact
                        confidence_score=0.6,
                        time_sensitivity="medium_term",
                        data_sources=["platform_data"],
                        supporting_evidence={
                            'best_platform': best_platform[0],
                            'worst_platform': worst_platform[0],
                            'performance_gap': performance_gap,
                            'platforms_analyzed': len(platform_performance)
                        }
                    )
                    
                    insights.append(insight)
        
        return insights
    
    async def _generate_customer_insight(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[ActionableInsight]:
        """Generate customer behavior insights"""
        insights = []
        
        engagement_metrics = data.get('engagement_metrics', {})
        
        # Engagement pattern analysis
        engagement_rate = engagement_metrics.get('engagement_rate', 0)
        follower_count = engagement_metrics.get('follower_count', 0)
        
        if engagement_rate > 0 and follower_count > 0:
            # Calculate engagement efficiency
            engagement_efficiency = engagement_rate / (follower_count / 1000)  # Per 1K followers
            
            # Benchmark comparison (simplified)
            benchmark_efficiency = 5.0  # 5% engagement per 1K followers
            
            if engagement_efficiency > benchmark_efficiency * 1.2:  # 20% above benchmark
                insight = ActionableInsight(
                    insight_id=str(uuid.uuid4()),
                    type=InsightType.CUSTOMER_BEHAVIOR,
                    category=InsightCategory.CUSTOMER_INSIGHTS,
                    priority=InsightPriority.MEDIUM,
                    title="Exceptional Audience Engagement Quality",
                    description=f"Engagement efficiency of {engagement_efficiency:.2f} significantly exceeds benchmarks",
                    key_findings=[
                        f"Engagement efficiency: {engagement_efficiency:.2f}",
                        f"Market benchmark: {benchmark_efficiency:.2f}",
                        "Highly engaged, quality audience base"
                    ],
                    recommended_actions=[
                        "Leverage high engagement for premium offerings",
                        "Document successful engagement strategies",
                        "Maintain content quality to preserve engagement"
                    ],
                    potential_impact=data['current_revenue'] * Decimal('0.2'),  # 20% premium potential
                    confidence_score=0.7,
                    time_sensitivity="short_term",
                    data_sources=["engagement_metrics"],
                    supporting_evidence={
                        'engagement_efficiency': engagement_efficiency,
                        'benchmark_efficiency': benchmark_efficiency,
                        'follower_count': follower_count,
                        'engagement_rate': engagement_rate
                    }
                )
                
                insights.append(insight)
        
        return insights
    
    async def _generate_seasonal_insight(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[ActionableInsight]:
        """Generate seasonal pattern insights"""
        insights = []
        
        derived_metrics = data.get('derived_metrics', {})
        seasonality_score = derived_metrics.get('seasonality_score', 0)
        
        if seasonality_score > 0.3:  # Significant seasonality
            current_month = datetime.utcnow().month
            
            # Predict seasonal impact based on current month
            seasonal_patterns = self.pattern_library['seasonal_patterns']
            
            relevant_pattern = None
            for pattern_name, pattern_data in seasonal_patterns.items():
                # Simplified pattern matching
                if 'holiday' in pattern_name and current_month in [11, 12]:
                    relevant_pattern = (pattern_name, pattern_data)
                elif 'summer' in pattern_name and current_month in [6, 7, 8]:
                    relevant_pattern = (pattern_name, pattern_data)
                elif 'school' in pattern_name and current_month == 9:
                    relevant_pattern = (pattern_name, pattern_data)
            
            if relevant_pattern:
                pattern_name, pattern_data = relevant_pattern
                expected_multiplier = pattern_data['multiplier']
                
                expected_impact = (Decimal(str(expected_multiplier)) - 1) * data['current_revenue']
                
                insight = ActionableInsight(
                    insight_id=str(uuid.uuid4()),
                    type=InsightType.SEASONAL_PATTERN,
                    category=InsightCategory.STRATEGIC_PLANNING,
                    priority=InsightPriority.MEDIUM,
                    title=f"Seasonal Pattern Detected: {pattern_data['description']}",
                    description=f"Historical data shows {seasonality_score:.1f} seasonality score, expecting {pattern_data['description'].lower()}",
                    key_findings=[
                        f"Seasonality strength: {seasonality_score:.2f}",
                        f"Expected revenue multiplier: {expected_multiplier}x",
                        f"Pattern duration: {pattern_data['duration_days']} days"
                    ],
                    recommended_actions=[
                        "Prepare for seasonal revenue changes",
                        "Adjust marketing and content strategy accordingly",
                        "Plan resource allocation for seasonal peaks/troughs"
                    ],
                    potential_impact=abs(expected_impact),
                    confidence_score=pattern_data['certainty'] * seasonality_score,
                    time_sensitivity="short_term",
                    data_sources=["historical_revenue", "seasonal_analysis"],
                    supporting_evidence={
                        'seasonality_score': seasonality_score,
                        'pattern_name': pattern_name,
                        'expected_multiplier': expected_multiplier,
                        'current_month': current_month
                    }
                )
                
                insights.append(insight)
        
        return insights
    
    async def _generate_benchmark_insight(
        self,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[ActionableInsight]:
        """Generate performance benchmark insights"""
        insights = []
        
        current_revenue = data.get('current_revenue', Decimal('0'))
        
        # Simple benchmark comparison (in production, use real benchmark data)
        industry_benchmarks = {
            'content_creator_monthly_revenue': {
                'beginner': Decimal('500'),
                'intermediate': Decimal('2000'),
                'advanced': Decimal('5000'),
                'professional': Decimal('10000')
            }
        }
        
        benchmarks = industry_benchmarks['content_creator_monthly_revenue']
        
        # Determine tier
        user_tier = 'beginner'
        next_tier = 'intermediate'
        next_target = benchmarks['intermediate']
        
        for tier, threshold in benchmarks.items():
            if current_revenue >= threshold:
                user_tier = tier
                
                # Find next tier
                tier_order = ['beginner', 'intermediate', 'advanced', 'professional']
                current_tier_index = tier_order.index(tier)
                if current_tier_index < len(tier_order) - 1:
                    next_tier = tier_order[current_tier_index + 1]
                    next_target = benchmarks[next_tier]
                else:
                    next_tier = None
                    next_target = None
        
        if next_target:
            gap_to_next = next_target - current_revenue
            
            insight = ActionableInsight(
                insight_id=str(uuid.uuid4()),
                type=InsightType.PERFORMANCE_BENCHMARK,
                category=InsightCategory.STRATEGIC_PLANNING,
                priority=InsightPriority.LOW,
                title=f"Currently in {user_tier.title()} Tier",
                description=f"Revenue of €{current_revenue} places you in {user_tier} tier. Next milestone: {next_tier} tier at €{next_target}",
                key_findings=[
                    f"Current tier: {user_tier.title()}",
                    f"Current revenue: €{current_revenue}",
                    f"Next tier target: €{next_target} ({next_tier})",
                    f"Gap to next tier: €{gap_to_next}"
                ],
                recommended_actions=[
                    f"Focus on strategies to reach {next_tier} tier",
                    "Analyze success factors of higher-tier creators",
                    "Set milestone targets for tier progression"
                ],
                potential_impact=gap_to_next,
                confidence_score=0.8,
                time_sensitivity="long_term",
                data_sources=["industry_benchmarks"],
                supporting_evidence={
                    'current_tier': user_tier,
                    'next_tier': next_tier,
                    'gap_amount': float(gap_to_next),
                    'tier_thresholds': {k: float(v) for k, v in benchmarks.items()}
                }
            )
            
            insights.append(insight)
        
        return insights
    
    async def _filter_and_rank_insights(
        self,
        insights: List[ActionableInsight]
    ) -> List[ActionableInsight]:
        """Filter and rank insights by relevance and priority"""
        # Filter out low-confidence insights
        filtered_insights = [
            insight for insight in insights
            if insight.confidence_score >= self.confidence_threshold
        ]
        
        # Remove expired insights
        filtered_insights = [
            insight for insight in filtered_insights
            if not insight.is_expired
        ]
        
        # Rank by priority and impact
        priority_weights = {
            InsightPriority.CRITICAL: 5,
            InsightPriority.HIGH: 4,
            InsightPriority.MEDIUM: 3,
            InsightPriority.LOW: 2,
            InsightPriority.INFORMATIONAL: 1
        }
        
        def ranking_score(insight: ActionableInsight) -> float:
            priority_score = priority_weights.get(insight.priority, 1)
            impact_score = min(float(insight.potential_impact) / 1000, 10)  # Normalize impact
            confidence_score = insight.confidence_score
            
            return priority_score * 2 + impact_score + confidence_score
        
        filtered_insights.sort(key=ranking_score, reverse=True)
        
        return filtered_insights
    
    async def _cluster_related_insights(
        self,
        insights: List[ActionableInsight]
    ) -> List[ActionableInsight]:
        """Identify and cluster related insights"""
        if len(insights) < 2:
            return insights
        
        # Simple clustering based on categories and types
        clusters = {}
        
        for insight in insights:
            cluster_key = f"{insight.category.value}_{insight.type.value}"
            
            if cluster_key not in clusters:
                clusters[cluster_key] = []
            
            clusters[cluster_key].append(insight)
        
        # Update related insights
        for cluster_insights in clusters.values():
            if len(cluster_insights) > 1:
                insight_ids = [insight.insight_id for insight in cluster_insights]
                
                for insight in cluster_insights:
                    insight.related_insights = [
                        insight_id for insight_id in insight_ids
                        if insight_id != insight.insight_id
                    ]
        
        return insights
    
    async def get_insights_summary(
        self,
        time_period: int = 7  # days
    ) -> Dict[str, Any]:
        """Get summary of insights from specified time period"""



        try:
            cutoff_date = datetime.utcnow() - timedelta(days=time_period)
            
            recent_insights = [
                insight for insight in self.insights_database
                if insight.created_at >= cutoff_date and not insight.is_expired
            ]
            
            # Categorize insights
            by_priority = {}
            by_category = {}
            by_type = {}
            
            for insight in recent_insights:
                # By priority
                priority = insight.priority.value
                if priority not in by_priority:
                    by_priority[priority] = []
                by_priority[priority].append(insight)
                
                # By category
                category = insight.category.value
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(insight)
                
                # By type
                insight_type = insight.type.value
                if insight_type not in by_type:
                    by_type[insight_type] = []
                by_type[insight_type].append(insight)
            
            # Calculate total potential impact
            total_impact = sum(insight.potential_impact for insight in recent_insights)
            
            # Top insights by priority
            top_insights = sorted(
                recent_insights,
                key=lambda x: (
                    {'critical': 5, 'high': 4, 'medium': 3, 'low': 2, 'informational': 1}.get(x.priority.value, 0),
                    x.potential_impact
                ),
                reverse=True
            )[:5]
            
            return {
                'summary_period_days': time_period,
                'total_insights': len(recent_insights),
                'total_potential_impact': str(total_impact),
                'insights_by_priority': {
                    priority: len(insights) for priority, insights in by_priority.items()
                },
                'insights_by_category': {
                    category: len(insights) for category, insights in by_category.items()
                },
                'insights_by_type': {
                    insight_type: len(insights) for insight_type, insights in by_type.items()
                },
                'top_insights': [
                    {
                        'id': insight.insight_id,
                        'title': insight.title,
                        'priority': insight.priority.value,
                        'potential_impact': str(insight.potential_impact),
                        'confidence_score': insight.confidence_score,
                        'time_sensitivity': insight.time_sensitivity
                    }
                    for insight in top_insights
                ],
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating insights summary: {e}")
            raise
    
    async def export_insights_report(
        self,
        insights: List[ActionableInsight],
        include_details: bool = True
    ) -> Dict[str, Any]:
        """Export comprehensive insights report"""



        try:
            report = {
                'report_info': {
                    'total_insights': len(insights),
                    'generated_at': datetime.utcnow().isoformat(),
                    'confidence_threshold': self.confidence_threshold
                },
                'executive_summary': await self._generate_executive_summary(insights),
                'insights_overview': {
                    'by_priority': self._group_insights_by_priority(insights),
                    'by_category': self._group_insights_by_category(insights),
                    'by_time_sensitivity': self._group_insights_by_time_sensitivity(insights)
                },
                'key_insights': [
                    await self._format_insight_for_report(insight, include_details)
                    for insight in insights[:10]  # Top 10 insights
                ],
                'action_priorities': await self._generate_action_priorities(insights),
                'impact_analysis': await self._calculate_impact_analysis(insights)
            }
            
            if include_details:
                report['detailed_insights'] = [
                    await self._format_insight_for_report(insight, True)
                    for insight in insights
                ]
            
            return report
            
        except Exception as e:
            logger.error(f"Error exporting insights report: {e}")
            raise
    
    async def _generate_executive_summary(self, insights: List[ActionableInsight]) -> Dict[str, Any]:
        """Generate executive summary of insights"""
        if not insights:
            return {'message': 'No insights available for summary'}
        
        # Count critical and high priority insights
        critical_count = len([i for i in insights if i.priority == InsightPriority.CRITICAL])
        high_count = len([i for i in insights if i.priority == InsightPriority.HIGH])
        
        # Calculate total potential impact
        total_impact = sum(insight.potential_impact for insight in insights)
        
        # Find most impactful insight
        most_impactful = max(insights, key=lambda x: x.potential_impact)
        
        # Immediate action items
        immediate_actions = [
            insight for insight in insights
            if insight.time_sensitivity == "immediate" and insight.priority in [InsightPriority.CRITICAL, InsightPriority.HIGH]
        ]
        
        return {
            'total_insights': len(insights),
            'critical_issues': critical_count,
            'high_priority_items': high_count,
            'total_potential_impact': str(total_impact),
            'most_impactful_insight': most_impactful.title,
            'immediate_actions_required': len(immediate_actions),
            'key_recommendation': most_impactful.recommended_actions[0] if most_impactful.recommended_actions else "No specific recommendations available"
        }
    
    def _group_insights_by_priority(self, insights: List[ActionableInsight]) -> Dict[str, int]:
        """Group insights by priority"""
        groups = {}
        for insight in insights:
            priority = insight.priority.value
            groups[priority] = groups.get(priority, 0) + 1
        return groups
    
    def _group_insights_by_category(self, insights: List[ActionableInsight]) -> Dict[str, int]:
        """Group insights by category"""
        groups = {}
        for insight in insights:
            category = insight.category.value
            groups[category] = groups.get(category, 0) + 1
        return groups
    
    def _group_insights_by_time_sensitivity(self, insights: List[ActionableInsight]) -> Dict[str, int]:
        """Group insights by time sensitivity"""
        groups = {}
        for insight in insights:
            time_sensitivity = insight.time_sensitivity
            groups[time_sensitivity] = groups.get(time_sensitivity, 0) + 1
        return groups
    
    async def _format_insight_for_report(
        self,
        insight: ActionableInsight,
        include_details: bool
    ) -> Dict[str, Any]:
        """Format insight for report"""
        formatted = {
            'id': insight.insight_id,
            'title': insight.title,
            'type': insight.type.value,
            'category': insight.category.value,
            'priority': insight.priority.value,
            'description': insight.description,
            'potential_impact': str(insight.potential_impact),
            'confidence_score': insight.confidence_score,
            'time_sensitivity': insight.time_sensitivity,
            'created_at': insight.created_at.isoformat(),
            'age_hours': insight.age_hours
        }
        
        if include_details:
            formatted.update({
                'key_findings': insight.key_findings,
                'recommended_actions': insight.recommended_actions,
                'data_sources': insight.data_sources,
                'supporting_evidence': insight.supporting_evidence,
                'related_insights': insight.related_insights
            })
        
        return formatted
    
    async def _generate_action_priorities(self, insights: List[ActionableInsight]) -> List[Dict[str, Any]]:
        """Generate prioritized action items"""
        action_items = []
        
        # Extract all recommended actions with context
        for insight in insights:
            for action in insight.recommended_actions:
                action_items.append({
                    'action': action,
                    'insight_id': insight.insight_id,
                    'insight_title': insight.title,
                    'priority': insight.priority.value,
                    'time_sensitivity': insight.time_sensitivity,
                    'potential_impact': insight.potential_impact,
                    'confidence_score': insight.confidence_score
                })
        
        # Sort by priority and impact
        priority_weights = {
            'critical': 5, 'high': 4, 'medium': 3, 'low': 2, 'informational': 1
        }
        
        action_items.sort(
            key=lambda x: (
                priority_weights.get(x['priority'], 0),
                x['potential_impact'],
                x['confidence_score']
            ),
            reverse=True
        )
        
        return action_items[:15]  # Top 15 actions
    
    async def _calculate_impact_analysis(self, insights: List[ActionableInsight]) -> Dict[str, Any]:
        """Calculate overall impact analysis"""
        if not insights:
            return {}
        
        total_impact = sum(insight.potential_impact for insight in insights)
        
        # Impact by category
        category_impact = {}
        for insight in insights:
            category = insight.category.value
            if category not in category_impact:
                category_impact[category] = Decimal('0')
            category_impact[category] += insight.potential_impact
        
        # Risk vs opportunity analysis
        risk_insights = [i for i in insights if i.category == InsightCategory.RISK_MITIGATION]
        opportunity_insights = [i for i in insights if i.category == InsightCategory.REVENUE_OPTIMIZATION]
        
        risk_impact = sum(i.potential_impact for i in risk_insights)
        opportunity_impact = sum(i.potential_impact for i in opportunity_insights)
        
        return {
            'total_potential_impact': str(total_impact),
            'impact_by_category': {k: str(v) for k, v in category_impact.items()},
            'risk_vs_opportunity': {
                'risk_impact': str(risk_impact),
                'opportunity_impact': str(opportunity_impact),
                'net_opportunity': str(opportunity_impact - risk_impact)
            },
            'average_confidence': statistics.mean([i.confidence_score for i in insights]),
            'high_confidence_insights': len([i for i in insights if i.confidence_score > 0.8])
        }


async def create_revenue_insights_engine(config: Optional[Dict[str, Any]] = None) -> RevenueInsightsEngine:
    """Factory function to create and initialize revenue insights engine"""
    engine = RevenueInsightsEngine(config)
    await engine.initialize()
    return engine
