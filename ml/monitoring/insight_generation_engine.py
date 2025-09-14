"""
🧠 Insight Generation Engine - AI-Powered Business Intelligence System

🤖 IA PROMPT ENGINEER + 🔬 ML ENGINEER + 💼 BUSINESS ANALYST EXPERTISE

Advanced AI-powered insight generation system that analyzes ML model performance,
business metrics, and creator data to generate actionable intelligence and
strategic recommendations for platform optimization and growth.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Version: 1.0.0

🧠 INSIGHT GENERATION PLATFORM
- AI-powered pattern recognition and analysis
- Business intelligence and strategic insights
- Creator-specific optimization recommendations
- Predictive analytics and trend forecasting
- Automated report generation and alerting
"""

import asyncio
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid
import yaml
from collections import defaultdict, Counter
import re
import math

logger = logging.getLogger(__name__)

class InsightType(Enum):
    """Types of insights generated"""
    PERFORMANCE_INSIGHT = "performance_insight"
    BUSINESS_INSIGHT = "business_insight"
    OPTIMIZATION_INSIGHT = "optimization_insight"
    PREDICTIVE_INSIGHT = "predictive_insight"
    ANOMALY_INSIGHT = "anomaly_insight"
    TREND_INSIGHT = "trend_insight"
    CREATOR_INSIGHT = "creator_insight"
    COMPETITIVE_INSIGHT = "competitive_insight"

class InsightPriority(Enum):
    """Priority levels for insights"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

class CreatorType(Enum):
    """Creator types for specialized insights"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERAL = "general"

class DataSource(Enum):
    """Data sources for insight generation"""
    MODEL_METRICS = "model_metrics"
    BUSINESS_METRICS = "business_metrics"
    USER_BEHAVIOR = "user_behavior"
    CONTENT_ANALYTICS = "content_analytics"
    PERFORMANCE_DATA = "performance_data"
    FINANCIAL_DATA = "financial_data"
    EXTERNAL_DATA = "external_data"

@dataclass
class Insight:
    """Individual insight with metadata"""
    insight_id: str
    insight_type: InsightType
    priority: InsightPriority
    title: str
    description: str
    key_findings: List[str]
    recommendations: List[str]
    data_sources: List[DataSource]
    confidence_score: float
    impact_score: float
    creator_type: Optional[CreatorType] = None
    model_id: Optional[str] = None
    supporting_data: Dict[str, Any] = field(default_factory=dict)
    visualizations: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    action_items: List[str] = field(default_factory=list)

@dataclass
class InsightReport:
    """Comprehensive insight report"""
    report_id: str
    report_title: str
    executive_summary: str
    insights: List[Insight]
    key_metrics: Dict[str, float]
    trend_analysis: Dict[str, Any]
    strategic_recommendations: List[str]
    risk_alerts: List[str]
    opportunity_highlights: List[str]
    generated_timestamp: datetime = field(default_factory=datetime.now)
    report_period: Tuple[datetime, datetime] = field(default_factory=lambda: (datetime.now() - timedelta(days=7), datetime.now()))

class PatternRecognitionEngine:
    """🔬 ML ENGINEER - Advanced pattern recognition and analysis"""
    
    def __init__(self) -> None:
        self.pattern_library = {}
        self.anomaly_thresholds = {}
        self.trend_algorithms = {
            "linear": self._linear_trend_analysis,
            "polynomial": self._polynomial_trend_analysis,
            "seasonal": self._seasonal_trend_analysis,
            "exponential": self._exponential_trend_analysis
        }
        
    async def analyze_performance_patterns(self, metrics_data: Dict[str, List[float]],
                                         timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Analyze performance patterns in metrics data"""
        patterns = []
        
        for metric_name, values in metrics_data.items():
            if len(values) < 3:
                continue
                
            # Detect trends
            trend_analysis = await self._analyze_metric_trends(metric_name, values, timestamps)
            if trend_analysis["significance"] > 0.7:
                patterns.append(trend_analysis)
            
            # Detect anomalies
            anomalies = await self._detect_metric_anomalies(metric_name, values, timestamps)
            patterns.extend(anomalies)
            
            # Detect cycles/seasonality
            cycles = await self._detect_metric_cycles(metric_name, values, timestamps)
            if cycles:
                patterns.append(cycles)
        
        return patterns
    
    async def _analyze_metric_trends(self, metric_name: str, values: List[float],
                                   timestamps: List[datetime]) -> Dict[str, Any]:
        """Analyze trends in metric values"""
        if len(values) < 3:
            return {"significance": 0}
        
        # Convert to numeric indices for trend analysis
        x = np.arange(len(values))
        y = np.array(values)
        
        # Linear trend analysis
        slope, intercept = np.polyfit(x, y, 1)
        correlation = np.corrcoef(x, y)[0, 1]
        
        # Determine trend strength and direction
        trend_strength = abs(correlation)
        trend_direction = "increasing" if slope > 0 else "decreasing"
        
        # Calculate significance
        significance = trend_strength * min(1.0, len(values) / 10.0)
        
        return {
            "pattern_type": "trend",
            "metric_name": metric_name,
            "trend_direction": trend_direction,
            "slope": slope,
            "correlation": correlation,
            "significance": significance,
            "trend_strength": trend_strength,
            "start_value": values[0],
            "end_value": values[-1],
            "change_percentage": ((values[-1] - values[0]) / abs(values[0])) * 100 if values[0] != 0 else 0
        }
    
    async def _detect_metric_anomalies(self, metric_name: str, values: List[float],
                                     timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Detect anomalies in metric values"""
        if len(values) < 5:
            return []
        
        anomalies = []
        
        # Calculate statistical thresholds
        mean_val = np.mean(values)
        std_val = np.std(values)
        threshold = 2.5 * std_val  # 2.5 sigma threshold
        
        for i, (value, timestamp) in enumerate(zip(values, timestamps)):
            deviation = abs(value - mean_val)
            if deviation > threshold:
                anomaly_score = deviation / std_val
                
                anomalies.append({
                    "pattern_type": "anomaly",
                    "metric_name": metric_name,
                    "timestamp": timestamp,
                    "value": value,
                    "expected_value": mean_val,
                    "deviation": deviation,
                    "anomaly_score": anomaly_score,
                    "severity": "high" if anomaly_score > 3 else "medium",
                    "significance": min(1.0, anomaly_score / 3.0)
                })
        
        return anomalies
    
    async def _detect_metric_cycles(self, metric_name: str, values: List[float],
                                  timestamps: List[datetime]) -> Optional[Dict[str, Any]]:
        """Detect cyclical patterns in metrics"""
        if len(values) < 12:  # Need sufficient data for cycle detection
            return None
        
        # Simple cycle detection using autocorrelation
        autocorr = np.correlate(values, values, mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        
        # Find peaks that might indicate cycles
        if len(autocorr) > 3:
            peak_indices = []
            for i in range(1, len(autocorr) - 1):
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                    peak_indices.append(i)
            
            if peak_indices and max(autocorr[peak_indices]) > 0.5:
                strongest_peak = peak_indices[np.argmax(autocorr[peak_indices])]
                cycle_length = strongest_peak
                cycle_strength = autocorr[strongest_peak]
                
                return {
                    "pattern_type": "cycle",
                    "metric_name": metric_name,
                    "cycle_length": cycle_length,
                    "cycle_strength": cycle_strength,
                    "significance": cycle_strength
                }
        
        return None
    
    def _linear_trend_analysis(self, values: List[float]) -> Dict[str, float]:
        """Linear trend analysis"""
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        return {"slope": slope, "intercept": intercept, "type": "linear"}
    
    def _polynomial_trend_analysis(self, values: List[float]) -> Dict[str, float]:
        """Polynomial trend analysis"""
        if len(values) < 4:
            return self._linear_trend_analysis(values)
        
        x = np.arange(len(values))
        coeffs = np.polyfit(x, values, min(3, len(values) - 1))
        return {"coefficients": coeffs.tolist(), "type": "polynomial"}
    
    def _seasonal_trend_analysis(self, values: List[float]) -> Dict[str, Any]:
        """Seasonal trend analysis"""
        # Simplified seasonal decomposition
        if len(values) < 12:
            return {"type": "seasonal", "insufficient_data": True}
        
        # Simple moving average for trend
        window_size = min(7, len(values) // 3)
        trend = np.convolve(values, np.ones(window_size)/window_size, mode='valid')
        
        return {
            "type": "seasonal",
            "trend": trend.tolist(),
            "seasonality_detected": len(trend) > 0
        }
    
    def _exponential_trend_analysis(self, values: List[float]) -> Dict[str, float]:
        """Exponential trend analysis"""
        if any(v <= 0 for v in values):
            return self._linear_trend_analysis(values)
        
        log_values = np.log(values)
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, log_values, 1)
        
        return {
            "growth_rate": np.exp(slope) - 1,
            "base": np.exp(intercept),
            "type": "exponential"
        }

class BusinessIntelligenceEngine:
    """💼 BUSINESS ANALYST - Business intelligence and strategic analysis"""
    
    def __init__(self) -> None:
        self.business_rules = {}
        self.kpi_definitions = {}
        self.benchmarks = {}
        
    async def analyze_business_performance(self, business_data: Dict[str, Any]) -> List[Insight]:
        """Analyze business performance and generate insights"""
        insights = []
        
        # Revenue analysis
        if "revenue_data" in business_data:
            revenue_insights = await self._analyze_revenue_performance(business_data["revenue_data"])
            insights.extend(revenue_insights)
        
        # Cost analysis
        if "cost_data" in business_data:
            cost_insights = await self._analyze_cost_efficiency(business_data["cost_data"])
            insights.extend(cost_insights)
        
        # Creator performance analysis
        if "creator_data" in business_data:
            creator_insights = await self._analyze_creator_performance(business_data["creator_data"])
            insights.extend(creator_insights)
        
        # Market opportunity analysis
        if "market_data" in business_data:
            market_insights = await self._analyze_market_opportunities(business_data["market_data"])
            insights.extend(market_insights)
        
        return insights
    
    async def _analyze_revenue_performance(self, revenue_data: Dict[str, Any]) -> List[Insight]:
        """Analyze revenue performance and trends"""
        insights = []
        
        # Revenue growth analysis
        if "historical_revenue" in revenue_data:
            historical = revenue_data["historical_revenue"]
            
            if len(historical) >= 2:
                latest_revenue = historical[-1]
                previous_revenue = historical[-2]
                growth_rate = ((latest_revenue - previous_revenue) / previous_revenue) * 100
                
                if growth_rate > 20:
                    insights.append(Insight(
                        insight_id=str(uuid.uuid4()),
                        insight_type=InsightType.BUSINESS_INSIGHT,
                        priority=InsightPriority.HIGH,
                        title="Strong Revenue Growth Detected",
                        description=f"Revenue has grown by {growth_rate:.1f}% in the latest period, indicating strong business momentum.",
                        key_findings=[
                            f"Current revenue: ${latest_revenue:,.2f}",
                            f"Growth rate: {growth_rate:.1f}%",
                            "Growth exceeds industry benchmarks"
                        ],
                        recommendations=[
                            "Scale successful initiatives that are driving growth",
                            "Invest in marketing and creator acquisition",
                            "Optimize high-performing creator segments"
                        ],
                        data_sources=[DataSource.FINANCIAL_DATA],
                        confidence_score=0.9,
                        impact_score=0.8,
                        supporting_data={"growth_rate": growth_rate, "revenue_trend": historical}
                    ))
                elif growth_rate < -10:
                    insights.append(Insight(
                        insight_id=str(uuid.uuid4()),
                        insight_type=InsightType.BUSINESS_INSIGHT,
                        priority=InsightPriority.CRITICAL,
                        title="Revenue Decline Alert",
                        description=f"Revenue has declined by {abs(growth_rate):.1f}% in the latest period, requiring immediate attention.",
                        key_findings=[
                            f"Current revenue: ${latest_revenue:,.2f}",
                            f"Decline rate: {abs(growth_rate):.1f}%",
                            "Performance below industry expectations"
                        ],
                        recommendations=[
                            "Conduct immediate root cause analysis",
                            "Review and optimize underperforming segments",
                            "Implement revenue recovery strategies",
                            "Analyze competitor activities and market changes"
                        ],
                        data_sources=[DataSource.FINANCIAL_DATA],
                        confidence_score=0.95,
                        impact_score=0.9,
                        supporting_data={"decline_rate": abs(growth_rate), "revenue_trend": historical}
                    ))
        
        # Revenue stream analysis
        if "revenue_streams" in revenue_data:
            streams = revenue_data["revenue_streams"]
            total_revenue = sum(streams.values())
            
            # Identify dominant revenue stream
            if streams:
                dominant_stream = max(streams.items(), key=lambda x: x[1])
                concentration = (dominant_stream[1] / total_revenue) * 100
                
                if concentration > 70:
                    insights.append(Insight(
                        insight_id=str(uuid.uuid4()),
                        insight_type=InsightType.BUSINESS_INSIGHT,
                        priority=InsightPriority.MEDIUM,
                        title="High Revenue Concentration Risk",
                        description=f"{dominant_stream[0]} accounts for {concentration:.1f}% of total revenue, creating concentration risk.",
                        key_findings=[
                            f"Dominant stream: {dominant_stream[0]} ({concentration:.1f}%)",
                            f"Revenue concentration above 70% threshold",
                            "Business vulnerable to single stream disruption"
                        ],
                        recommendations=[
                            "Diversify revenue streams to reduce risk",
                            "Develop alternative monetization strategies",
                            "Invest in underutilized revenue channels",
                            "Create contingency plans for main revenue stream"
                        ],
                        data_sources=[DataSource.FINANCIAL_DATA],
                        confidence_score=0.85,
                        impact_score=0.7,
                        supporting_data={"concentration": concentration, "streams": streams}
                    ))
        
        return insights
    
    async def _analyze_cost_efficiency(self, cost_data: Dict[str, Any]) -> List[Insight]:
        """Analyze cost efficiency and optimization opportunities"""
        insights = []
        
        # Cost trend analysis
        if "historical_costs" in cost_data:
            historical = cost_data["historical_costs"]
            
            if len(historical) >= 3:
                # Calculate cost trend
                recent_avg = np.mean(historical[-3:])
                earlier_avg = np.mean(historical[:-3]) if len(historical) > 3 else historical[0]
                cost_change = ((recent_avg - earlier_avg) / earlier_avg) * 100
                
                if cost_change > 15:
                    insights.append(Insight(
                        insight_id=str(uuid.uuid4()),
                        insight_type=InsightType.OPTIMIZATION_INSIGHT,
                        priority=InsightPriority.HIGH,
                        title="Rising Cost Trend Detected",
                        description=f"Costs have increased by {cost_change:.1f}% recently, impacting profitability.",
                        key_findings=[
                            f"Recent average cost: ${recent_avg:,.2f}",
                            f"Cost increase: {cost_change:.1f}%",
                            "Cost inflation exceeding revenue growth"
                        ],
                        recommendations=[
                            "Conduct comprehensive cost audit",
                            "Identify and eliminate inefficiencies",
                            "Negotiate better vendor contracts",
                            "Implement cost monitoring and controls"
                        ],
                        data_sources=[DataSource.FINANCIAL_DATA],
                        confidence_score=0.88,
                        impact_score=0.75,
                        supporting_data={"cost_trend": historical, "increase_rate": cost_change}
                    ))
        
        # Cost category analysis
        if "cost_categories" in cost_data:
            categories = cost_data["cost_categories"]
            total_costs = sum(categories.values())
            
            # Identify highest cost category
            if categories:
                highest_cost = max(categories.items(), key=lambda x: x[1])
                percentage = (highest_cost[1] / total_costs) * 100
                
                insights.append(Insight(
                    insight_id=str(uuid.uuid4()),
                    insight_type=InsightType.OPTIMIZATION_INSIGHT,
                    priority=InsightPriority.MEDIUM,
                    title="Cost Optimization Opportunity",
                    description=f"{highest_cost[0]} represents {percentage:.1f}% of total costs, offering optimization potential.",
                    key_findings=[
                        f"Highest cost category: {highest_cost[0]}",
                        f"Cost amount: ${highest_cost[1]:,.2f} ({percentage:.1f}%)",
                        "Optimization could significantly impact bottom line"
                    ],
                    recommendations=[
                        f"Deep dive analysis of {highest_cost[0]} costs",
                        "Benchmark against industry standards",
                        "Explore cost reduction strategies",
                        "Consider alternative solutions or vendors"
                    ],
                    data_sources=[DataSource.FINANCIAL_DATA],
                    confidence_score=0.8,
                    impact_score=0.6,
                    supporting_data={"categories": categories, "focus_category": highest_cost[0]}
                ))
        
        return insights
    
    async def _analyze_creator_performance(self, creator_data: Dict[str, Any]) -> List[Insight]:
        """Analyze creator performance and identify opportunities"""
        insights = []
        
        # Creator type performance analysis
        if "creator_metrics" in creator_data:
            metrics = creator_data["creator_metrics"]
            
            for creator_type, data in metrics.items():
                if "revenue" in data and "engagement" in data:
                    revenue = data["revenue"]
                    engagement = data["engagement"]
                    
                    # Calculate revenue per engagement
                    rpe = revenue / max(engagement, 1)
                    
                    # Determine if this creator type is high-performing
                    if rpe > 0.05:  # $0.05 per engagement
                        insights.append(Insight(
                            insight_id=str(uuid.uuid4()),
                            insight_type=InsightType.CREATOR_INSIGHT,
                            priority=InsightPriority.HIGH,
                            title=f"High-Performing Creator Segment: {creator_type.title()}",
                            description=f"{creator_type.title()} creators show exceptional revenue per engagement ratio.",
                            key_findings=[
                                f"Revenue per engagement: ${rpe:.3f}",
                                f"Total revenue: ${revenue:,.2f}",
                                f"Total engagement: {engagement:,.0f}",
                                "Performance exceeds platform average"
                            ],
                            recommendations=[
                                f"Increase marketing to attract more {creator_type} creators",
                                f"Develop {creator_type}-specific features and tools",
                                f"Create premium tiers for {creator_type} creators",
                                "Analyze success factors for replication"
                            ],
                            data_sources=[DataSource.BUSINESS_METRICS, DataSource.USER_BEHAVIOR],
                            confidence_score=0.85,
                            impact_score=0.8,
                            creator_type=CreatorType(creator_type),
                            supporting_data={"rpe": rpe, "metrics": data}
                        ))
        
        return insights
    
    async def _analyze_market_opportunities(self, market_data: Dict[str, Any]) -> List[Insight]:
        """Analyze market opportunities and competitive landscape"""
        insights = []
        
        # Market growth analysis
        if "market_size" in market_data and "market_growth" in market_data:
            market_size = market_data["market_size"]
            growth_rate = market_data["market_growth"]
            
            if growth_rate > 10:
                insights.append(Insight(
                    insight_id=str(uuid.uuid4()),
                    insight_type=InsightType.COMPETITIVE_INSIGHT,
                    priority=InsightPriority.HIGH,
                    title="Strong Market Growth Opportunity",
                    description=f"The market is growing at {growth_rate:.1f}% annually, presenting significant expansion opportunities.",
                    key_findings=[
                        f"Market size: ${market_size:,.0f}",
                        f"Annual growth rate: {growth_rate:.1f}%",
                        "Growth rate above industry average"
                    ],
                    recommendations=[
                        "Accelerate market expansion initiatives",
                        "Increase investment in product development",
                        "Expand marketing and user acquisition",
                        "Consider strategic partnerships or acquisitions"
                    ],
                    data_sources=[DataSource.EXTERNAL_DATA],
                    confidence_score=0.75,
                    impact_score=0.85,
                    supporting_data={"market_data": market_data}
                ))
        
        return insights

class PredictiveAnalyticsEngine:
    """🤖 IA PROMPT ENGINEER - AI-powered predictive analytics and forecasting"""
    
    def __init__(self) -> None:
        self.prediction_models = {}
        self.forecast_algorithms = {
            "linear": self._linear_forecast,
            "exponential": self._exponential_forecast,
            "seasonal": self._seasonal_forecast,
            "ml_ensemble": self._ml_ensemble_forecast
        }
        
    async def generate_predictive_insights(self, historical_data: Dict[str, List[float]],
                                         forecast_horizon: int = 30) -> List[Insight]:
        """Generate predictive insights and forecasts"""
        insights = []
        
        for metric_name, values in historical_data.items():
            if len(values) < 5:
                continue
            
            # Generate forecast
            forecast = await self._generate_forecast(metric_name, values, forecast_horizon)
            
            if forecast["confidence"] > 0.6:
                insight = await self._create_predictive_insight(metric_name, values, forecast)
                if insight:
                    insights.append(insight)
        
        return insights
    
    async def _generate_forecast(self, metric_name: str, historical_values: List[float],
                               horizon: int) -> Dict[str, Any]:
        """Generate forecast for specific metric"""
        
        # Choose best forecasting algorithm based on data characteristics
        algorithm = self._select_forecast_algorithm(historical_values)
        forecast_func = self.forecast_algorithms[algorithm]
        
        # Generate forecast
        forecast_values = forecast_func(historical_values, horizon)
        
        # Calculate confidence based on historical accuracy
        confidence = self._calculate_forecast_confidence(historical_values, algorithm)
        
        return {
            "forecast_values": forecast_values,
            "algorithm": algorithm,
            "confidence": confidence,
            "horizon": horizon
        }
    
    def _select_forecast_algorithm(self, values: List[float]) -> str:
        """Select best forecasting algorithm based on data characteristics"""
        
        if len(values) < 12:
            return "linear"
        
        # Check for seasonality
        if self._has_seasonality(values):
            return "seasonal"
        
        # Check for exponential growth
        if self._has_exponential_trend(values):
            return "exponential"
        
        # Default to linear for stable trends
        return "linear"
    
    def _has_seasonality(self, values: List[float]) -> bool:
        """Check if data shows seasonal patterns"""
        if len(values) < 12:
            return False
        
        # Simple seasonality detection using autocorrelation
        autocorr = np.correlate(values, values, mode='full')
        autocorr = autocorr[autocorr.size // 2:]
        
        # Look for peaks that might indicate seasonal cycles
        seasonal_lags = [7, 30, 90, 365]  # Weekly, monthly, quarterly, yearly
        
        for lag in seasonal_lags:
            if lag < len(autocorr) and autocorr[lag] > 0.5:
                return True
        
        return False
    
    def _has_exponential_trend(self, values: List[float]) -> bool:
        """Check if data shows exponential growth pattern"""
        if any(v <= 0 for v in values):
            return False
        
        log_values = np.log(values)
        x = np.arange(len(values))
        
        # Check correlation of log values with time
        correlation = np.corrcoef(x, log_values)[0, 1]
        
        return abs(correlation) > 0.8
    
    def _linear_forecast(self, values: List[float], horizon: int) -> List[float]:
        """Linear forecasting"""
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        forecast_x = np.arange(len(values), len(values) + horizon)
        forecast = slope * forecast_x + intercept
        
        return forecast.tolist()
    
    def _exponential_forecast(self, values: List[float], horizon: int) -> List[float]:
        """Exponential growth forecasting"""
        if any(v <= 0 for v in values):
            return self._linear_forecast(values, horizon)
        
        log_values = np.log(values)
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, log_values, 1)
        
        forecast_x = np.arange(len(values), len(values) + horizon)
        log_forecast = slope * forecast_x + intercept
        forecast = np.exp(log_forecast)
        
        return forecast.tolist()
    
    def _seasonal_forecast(self, values: List[float], horizon: int) -> List[float]:
        """Seasonal forecasting with trend and seasonality"""
        # Simplified seasonal decomposition
        season_length = 7  # Weekly seasonality
        
        if len(values) < season_length * 2:
            return self._linear_forecast(values, horizon)
        
        # Extract trend using moving average
        trend = []
        for i in range(len(values)):
            start_idx = max(0, i - season_length // 2)
            end_idx = min(len(values), i + season_length // 2 + 1)
            trend.append(np.mean(values[start_idx:end_idx]))
        
        # Extract seasonal pattern
        seasonal = []
        for i in range(season_length):
            season_values = [values[j] - trend[j] for j in range(i, len(values), season_length)]
            seasonal.append(np.mean(season_values))
        
        # Forecast trend
        trend_forecast = self._linear_forecast(trend, horizon)
        
        # Apply seasonal pattern to forecast
        forecast = []
        for i in range(horizon):
            seasonal_component = seasonal[i % season_length]
            forecast.append(trend_forecast[i] + seasonal_component)
        
        return forecast
    
    def _ml_ensemble_forecast(self, values: List[float], horizon: int) -> List[float]:
        """Ensemble of multiple forecasting methods"""
        linear_forecast = self._linear_forecast(values, horizon)
        exponential_forecast = self._exponential_forecast(values, horizon)
        
        # Weighted ensemble (simplified)
        weights = [0.6, 0.4]  # Favor linear for stability
        
        ensemble_forecast = []
        for i in range(horizon):
            weighted_value = (weights[0] * linear_forecast[i] + 
                            weights[1] * exponential_forecast[i])
            ensemble_forecast.append(weighted_value)
        
        return ensemble_forecast
    
    def _calculate_forecast_confidence(self, historical_values: List[float],
                                     algorithm: str) -> float:
        """Calculate confidence score for forecast"""
        
        if len(historical_values) < 4:
            return 0.5
        
        # Cross-validation approach: use part of data to predict rest
        split_point = len(historical_values) // 2
        train_data = historical_values[:split_point]
        test_data = historical_values[split_point:]
        
        # Generate forecast for test period
        forecast_func = self.forecast_algorithms[algorithm]
        predicted = forecast_func(train_data, len(test_data))
        
        # Calculate accuracy
        mape = np.mean([abs((actual - pred) / max(abs(actual), 0.001)) 
                       for actual, pred in zip(test_data, predicted)])
        
        # Convert MAPE to confidence (lower MAPE = higher confidence)
        confidence = max(0.1, 1.0 - min(1.0, mape))
        
        return confidence
    
    async def _create_predictive_insight(self, metric_name: str, historical_values: List[float],
                                       forecast: Dict[str, Any]) -> Optional[Insight]:
        """Create predictive insight from forecast results"""
        
        current_value = historical_values[-1]
        forecast_values = forecast["forecast_values"]
        
        if not forecast_values:
            return None
        
        # Analyze forecast trend
        forecast_end = forecast_values[-1]
        change_percentage = ((forecast_end - current_value) / abs(current_value)) * 100
        
        if abs(change_percentage) < 5:  # Less than 5% change
            return None  # Not significant enough for insight
        
        trend_direction = "increase" if change_percentage > 0 else "decrease"
        
        # Determine priority based on magnitude of change
        if abs(change_percentage) > 50:
            priority = InsightPriority.CRITICAL
        elif abs(change_percentage) > 25:
            priority = InsightPriority.HIGH
        else:
            priority = InsightPriority.MEDIUM
        
        return Insight(
            insight_id=str(uuid.uuid4()),
            insight_type=InsightType.PREDICTIVE_INSIGHT,
            priority=priority,
            title=f"Predicted {trend_direction.title()} in {metric_name}",
            description=f"Predictive analysis indicates {metric_name} will {trend_direction} by {abs(change_percentage):.1f}% over the forecast period.",
            key_findings=[
                f"Current value: {current_value:.2f}",
                f"Predicted value: {forecast_end:.2f}",
                f"Expected change: {change_percentage:+.1f}%",
                f"Forecast confidence: {forecast['confidence']*100:.1f}%"
            ],
            recommendations=[
                f"Monitor {metric_name} closely for early indicators",
                "Prepare contingency plans for predicted changes",
                "Adjust resource allocation based on forecast",
                "Update strategic planning to account for predicted trends"
            ],
            data_sources=[DataSource.MODEL_METRICS, DataSource.PERFORMANCE_DATA],
            confidence_score=forecast["confidence"],
            impact_score=min(1.0, abs(change_percentage) / 50.0),
            supporting_data={
                "historical_values": historical_values,
                "forecast": forecast_values,
                "algorithm": forecast["algorithm"]
            }
        )

class InsightGenerationEngine:
    """
    🧠 🤖 IA PROMPT ENGINEER + 🔬 ML ENGINEER + 💼 BUSINESS ANALYST - MASTER CLASS
    
    Enterprise-grade insight generation engine that combines AI-powered analysis,
    pattern recognition, and business intelligence to generate actionable insights.
    """
    
    def __init__(self, config_path -> None: Optional[str] = None) -> None:
        self.config = self._load_config(config_path)
        self.pattern_engine = PatternRecognitionEngine()
        self.business_engine = BusinessIntelligenceEngine()
        self.predictive_engine = PredictiveAnalyticsEngine()
        
        # Insight management
        self.generated_insights: List[Insight] = []
        self.insight_reports: List[InsightReport] = []
        self.insight_templates = {}
        
        logger.info("🧠 Insight Generation Engine initialized")
    
    async def generate_comprehensive_insights(self, data_sources: Dict[str, Any],
                                            analysis_period_days: int = 30) -> InsightReport:
        """Generate comprehensive insights from multiple data sources"""
        
        report_id = str(uuid.uuid4())
        end_date = datetime.now()
        start_date = end_date - timedelta(days=analysis_period_days)
        
        logger.info(f"🔍 Generating comprehensive insights for period {start_date.date()} to {end_date.date()}")
        
        all_insights = []
        
        # Pattern recognition insights
        if "metrics_data" in data_sources:
            logger.debug("Analyzing performance patterns...")
            patterns = await self.pattern_engine.analyze_performance_patterns(
                data_sources["metrics_data"].get("values", {}),
                data_sources["metrics_data"].get("timestamps", [])
            )
            pattern_insights = await self._convert_patterns_to_insights(patterns)
            all_insights.extend(pattern_insights)
        
        # Business intelligence insights
        if "business_data" in data_sources:
            logger.debug("Analyzing business performance...")
            business_insights = await self.business_engine.analyze_business_performance(
                data_sources["business_data"]
            )
            all_insights.extend(business_insights)
        
        # Predictive analytics insights
        if "historical_data" in data_sources:
            logger.debug("Generating predictive insights...")
            predictive_insights = await self.predictive_engine.generate_predictive_insights(
                data_sources["historical_data"]
            )
            all_insights.extend(predictive_insights)
        
        # Score and rank insights
        ranked_insights = await self._rank_insights(all_insights)
        
        # Generate executive summary
        executive_summary = await self._generate_executive_summary(ranked_insights)
        
        # Extract key metrics
        key_metrics = await self._extract_key_metrics(data_sources)
        
        # Generate strategic recommendations
        strategic_recommendations = await self._generate_strategic_recommendations(ranked_insights)
        
        # Identify risks and opportunities
        risk_alerts = await self._identify_risk_alerts(ranked_insights)
        opportunity_highlights = await self._identify_opportunities(ranked_insights)
        
        # Trend analysis
        trend_analysis = await self._perform_trend_analysis(data_sources)
        
        # Create comprehensive report
        report = InsightReport(
            report_id=report_id,
            report_title=f"AI-Powered Business Intelligence Report - {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            executive_summary=executive_summary,
            insights=ranked_insights,
            key_metrics=key_metrics,
            trend_analysis=trend_analysis,
            strategic_recommendations=strategic_recommendations,
            risk_alerts=risk_alerts,
            opportunity_highlights=opportunity_highlights,
            report_period=(start_date, end_date)
        )
        
        # Store report
        self.insight_reports.append(report)
        self.generated_insights.extend(ranked_insights)
        
        logger.info(f"✅ Generated {len(ranked_insights)} insights in comprehensive report")
        return report
    
    async def _convert_patterns_to_insights(self, patterns: List[Dict[str, Any]]) -> List[Insight]:
        """Convert detected patterns to actionable insights"""
        insights = []
        
        for pattern in patterns:
            if pattern["significance"] < 0.5:
                continue
            
            pattern_type = pattern["pattern_type"]
            
            if pattern_type == "trend":
                insight = await self._create_trend_insight(pattern)
            elif pattern_type == "anomaly":
                insight = await self._create_anomaly_insight(pattern)
            elif pattern_type == "cycle":
                insight = await self._create_cycle_insight(pattern)
            else:
                continue
            
            if insight:
                insights.append(insight)
        
        return insights
    
    async def _create_trend_insight(self, pattern: Dict[str, Any]) -> Insight:
        """Create insight from trend pattern"""
        metric_name = pattern["metric_name"]
        trend_direction = pattern["trend_direction"]
        change_percentage = pattern["change_percentage"]
        significance = pattern["significance"]
        
        # Determine priority based on trend strength and metric importance
        if significance > 0.9 and abs(change_percentage) > 20:
            priority = InsightPriority.HIGH
        elif significance > 0.7:
            priority = InsightPriority.MEDIUM
        else:
            priority = InsightPriority.LOW
        
        return Insight(
            insight_id=str(uuid.uuid4()),
            insight_type=InsightType.TREND_INSIGHT,
            priority=priority,
            title=f"{trend_direction.title()} Trend in {metric_name}",
            description=f"Strong {trend_direction} trend detected in {metric_name} with {abs(change_percentage):.1f}% change.",
            key_findings=[
                f"Trend direction: {trend_direction}",
                f"Change magnitude: {change_percentage:+.1f}%",
                f"Trend strength: {significance*100:.1f}%",
                f"Statistical correlation: {pattern['correlation']:.3f}"
            ],
            recommendations=self._generate_trend_recommendations(trend_direction, metric_name, change_percentage),
            data_sources=[DataSource.PERFORMANCE_DATA],
            confidence_score=significance,
            impact_score=min(1.0, abs(change_percentage) / 50.0),
            supporting_data=pattern
        )
    
    async def _create_anomaly_insight(self, pattern: Dict[str, Any]) -> Insight:
        """Create insight from anomaly pattern"""
        metric_name = pattern["metric_name"]
        anomaly_score = pattern["anomaly_score"]
        severity = pattern["severity"]
        
        priority = InsightPriority.HIGH if severity == "high" else InsightPriority.MEDIUM
        
        return Insight(
            insight_id=str(uuid.uuid4()),
            insight_type=InsightType.ANOMALY_INSIGHT,
            priority=priority,
            title=f"Anomaly Detected in {metric_name}",
            description=f"Unusual {severity} anomaly detected in {metric_name} requiring investigation.",
            key_findings=[
                f"Anomaly severity: {severity}",
                f"Anomaly score: {anomaly_score:.2f}",
                f"Observed value: {pattern['value']:.2f}",
                f"Expected value: {pattern['expected_value']:.2f}"
            ],
            recommendations=[
                f"Investigate root cause of {metric_name} anomaly",
                "Check for system issues or data quality problems",
                "Review recent changes that might explain the anomaly",
                "Implement monitoring to detect similar future anomalies"
            ],
            data_sources=[DataSource.PERFORMANCE_DATA],
            confidence_score=min(1.0, anomaly_score / 3.0),
            impact_score=0.8 if severity == "high" else 0.6,
            supporting_data=pattern
        )
    
    async def _create_cycle_insight(self, pattern: Dict[str, Any]) -> Insight:
        """Create insight from cyclical pattern"""
        metric_name = pattern["metric_name"]
        cycle_length = pattern["cycle_length"]
        cycle_strength = pattern["cycle_strength"]
        
        return Insight(
            insight_id=str(uuid.uuid4()),
            insight_type=InsightType.TREND_INSIGHT,
            priority=InsightPriority.MEDIUM,
            title=f"Cyclical Pattern in {metric_name}",
            description=f"Regular cycle detected in {metric_name} with {cycle_length}-period frequency.",
            key_findings=[
                f"Cycle length: {cycle_length} periods",
                f"Cycle strength: {cycle_strength:.3f}",
                "Predictable pattern can be leveraged for planning"
            ],
            recommendations=[
                f"Plan activities around {metric_name} cycles",
                "Optimize resource allocation based on cyclical patterns",
                "Use cycle information for capacity planning",
                "Monitor for cycle disruptions or changes"
            ],
            data_sources=[DataSource.PERFORMANCE_DATA],
            confidence_score=cycle_strength,
            impact_score=0.6,
            supporting_data=pattern
        )
    
    def _generate_trend_recommendations(self, trend_direction: str, metric_name: str,
                                      change_percentage: float) -> List[str]:
        """Generate recommendations based on trend analysis"""
        recommendations = []
        
        if trend_direction == "increasing":
            if "revenue" in metric_name.lower():
                recommendations.extend([
                    "Scale successful initiatives driving revenue growth",
                    "Invest in high-performing channels and segments",
                    "Optimize pricing strategies to maximize growth"
                ])
            elif "cost" in metric_name.lower():
                recommendations.extend([
                    "Investigate drivers of cost increases",
                    "Implement cost control measures",
                    "Review vendor contracts and optimize spending"
                ])
            else:
                recommendations.extend([
                    f"Leverage positive {metric_name} trend",
                    "Scale successful strategies",
                    "Monitor for sustainability"
                ])
        else:  # decreasing
            if "revenue" in metric_name.lower():
                recommendations.extend([
                    "Immediate investigation of revenue decline",
                    "Implement revenue recovery strategies",
                    "Review and optimize underperforming segments"
                ])
            elif "performance" in metric_name.lower():
                recommendations.extend([
                    f"Address declining {metric_name}",
                    "Optimize system performance",
                    "Review recent changes and their impact"
                ])
            else:
                recommendations.extend([
                    f"Address declining {metric_name} trend",
                    "Implement corrective measures",
                    "Monitor closely for further decline"
                ])
        
        return recommendations
    
    async def _rank_insights(self, insights: List[Insight]) -> List[Insight]:
        """Rank insights by priority and impact"""
        
        def insight_score(insight: Insight) -> float:
            priority_weights = {
                InsightPriority.CRITICAL: 5.0,
                InsightPriority.HIGH: 4.0,
                InsightPriority.MEDIUM: 3.0,
                InsightPriority.LOW: 2.0,
                InsightPriority.INFORMATIONAL: 1.0
            }
            
            priority_score = priority_weights.get(insight.priority, 1.0)
            confidence_score = insight.confidence_score
            impact_score = insight.impact_score
            
            return priority_score * confidence_score * impact_score
        
        return sorted(insights, key=insight_score, reverse=True)
    
    async def _generate_executive_summary(self, insights: List[Insight]) -> str:
        """Generate executive summary from insights"""
        if not insights:
            return "No significant insights generated for this period."
        
        critical_insights = [i for i in insights if i.priority == InsightPriority.CRITICAL]
        high_insights = [i for i in insights if i.priority == InsightPriority.HIGH]
        
        summary_parts = []
        
        # Overall summary
        summary_parts.append(f"Analysis of {len(insights)} insights reveals key trends and opportunities.")
        
        # Critical issues
        if critical_insights:
            summary_parts.append(f"🔴 {len(critical_insights)} critical issues require immediate attention:")
            for insight in critical_insights[:3]:  # Top 3 critical
                summary_parts.append(f"   • {insight.title}")
        
        # High-priority opportunities
        if high_insights:
            summary_parts.append(f"🟡 {len(high_insights)} high-priority opportunities identified:")
            for insight in high_insights[:3]:  # Top 3 high-priority
                summary_parts.append(f"   • {insight.title}")
        
        # Key trends
        trend_insights = [i for i in insights if i.insight_type == InsightType.TREND_INSIGHT]
        if trend_insights:
            summary_parts.append(f"📈 Key trends: {len(trend_insights)} significant patterns detected")
        
        return "\n".join(summary_parts)
    
    async def _extract_key_metrics(self, data_sources: Dict[str, Any]) -> Dict[str, float]:
        """Extract key metrics from data sources"""
        key_metrics = {}
        
        # Extract from business data
        if "business_data" in data_sources:
            business_data = data_sources["business_data"]
            
            if "revenue_data" in business_data:
                revenue_data = business_data["revenue_data"]
                if "historical_revenue" in revenue_data and revenue_data["historical_revenue"]:
                    key_metrics["current_revenue"] = revenue_data["historical_revenue"][-1]
                    if len(revenue_data["historical_revenue"]) >= 2:
                        prev_revenue = revenue_data["historical_revenue"][-2]
                        curr_revenue = revenue_data["historical_revenue"][-1]
                        key_metrics["revenue_growth_rate"] = ((curr_revenue - prev_revenue) / prev_revenue) * 100
            
            if "cost_data" in business_data:
                cost_data = business_data["cost_data"]
                if "historical_costs" in cost_data and cost_data["historical_costs"]:
                    key_metrics["current_costs"] = cost_data["historical_costs"][-1]
        
        # Extract from metrics data
        if "metrics_data" in data_sources:
            metrics_data = data_sources["metrics_data"]
            if "values" in metrics_data:
                for metric_name, values in metrics_data["values"].items():
                    if values:
                        key_metrics[f"current_{metric_name}"] = values[-1]
        
        return key_metrics
    
    async def _generate_strategic_recommendations(self, insights: List[Insight]) -> List[str]:
        """Generate strategic recommendations from insights"""
        recommendations = set()
        
        # Collect recommendations from top insights
        for insight in insights[:10]:  # Top 10 insights
            recommendations.update(insight.recommendations)
        
        # Add strategic recommendations based on insight patterns
        critical_count = len([i for i in insights if i.priority == InsightPriority.CRITICAL])
        if critical_count > 2:
            recommendations.add("Establish crisis management protocol for multiple critical issues")
        
        trend_insights = [i for i in insights if i.insight_type == InsightType.TREND_INSIGHT]
        if len(trend_insights) > 3:
            recommendations.add("Develop comprehensive trend monitoring and response system")
        
        return list(recommendations)
    
    async def _identify_risk_alerts(self, insights: List[Insight]) -> List[str]:
        """Identify risk alerts from insights"""
        risk_alerts = []
        
        critical_insights = [i for i in insights if i.priority == InsightPriority.CRITICAL]
        for insight in critical_insights:
            risk_alerts.append(f"🔴 CRITICAL: {insight.title}")
        
        # Look for specific risk patterns
        revenue_decline = any("decline" in i.title.lower() and "revenue" in i.title.lower() for i in insights)
        if revenue_decline:
            risk_alerts.append("🔴 Revenue decline detected - financial stability at risk")
        
        anomaly_count = len([i for i in insights if i.insight_type == InsightType.ANOMALY_INSIGHT])
        if anomaly_count > 3:
            risk_alerts.append("🟡 Multiple anomalies detected - system stability may be compromised")
        
        return risk_alerts
    
    async def _identify_opportunities(self, insights: List[Insight]) -> List[str]:
        """Identify opportunity highlights from insights"""
        opportunities = []
        
        # Growth opportunities
        growth_insights = [i for i in insights if "growth" in i.title.lower() or "increase" in i.title.lower()]
        for insight in growth_insights[:3]:
            opportunities.append(f"🟢 GROWTH: {insight.title}")
        
        # Optimization opportunities
        optimization_insights = [i for i in insights if i.insight_type == InsightType.OPTIMIZATION_INSIGHT]
        for insight in optimization_insights[:2]:
            opportunities.append(f"⚡ OPTIMIZATION: {insight.title}")
        
        return opportunities
    
    async def _perform_trend_analysis(self, data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive trend analysis"""
        trend_analysis = {}
        
        if "historical_data" in data_sources:
            for metric_name, values in data_sources["historical_data"].items():
                if len(values) >= 3:
                    # Calculate trend direction and strength
                    x = np.arange(len(values))
                    slope, _ = np.polyfit(x, values, 1)
                    correlation = np.corrcoef(x, values)[0, 1]
                    
                    trend_analysis[metric_name] = {
                        "trend_direction": "increasing" if slope > 0 else "decreasing",
                        "trend_strength": abs(correlation),
                        "slope": slope,
                        "recent_change": ((values[-1] - values[0]) / abs(values[0])) * 100 if values[0] != 0 else 0
                    }
        
        return trend_analysis
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load insight generation configuration"""
        default_config = {
            "min_confidence_threshold": 0.6,
            "max_insights_per_report": 50,
            "enable_predictive_analytics": True,
            "forecast_horizon_days": 30,
            "anomaly_sensitivity": 2.5
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                custom_config = yaml.safe_load(f)
            default_config.update(custom_config)
        
        return default_config
    
    def export_insights_report(self, report: InsightReport, format: str = "json") -> str:
        """Export insights report in specified format"""
        
        if format == "json":
            # Convert to JSON-serializable format
            report_data = {
                "report_id": report.report_id,
                "report_title": report.report_title,
                "generated_timestamp": report.generated_timestamp.isoformat(),
                "report_period": [
                    report.report_period[0].isoformat(),
                    report.report_period[1].isoformat()
                ],
                "executive_summary": report.executive_summary,
                "key_metrics": report.key_metrics,
                "trend_analysis": report.trend_analysis,
                "strategic_recommendations": report.strategic_recommendations,
                "risk_alerts": report.risk_alerts,
                "opportunity_highlights": report.opportunity_highlights,
                "insights": [
                    {
                        "insight_id": insight.insight_id,
                        "type": insight.insight_type.value,
                        "priority": insight.priority.value,
                        "title": insight.title,
                        "description": insight.description,
                        "key_findings": insight.key_findings,
                        "recommendations": insight.recommendations,
                        "confidence_score": insight.confidence_score,
                        "impact_score": insight.impact_score,
                        "timestamp": insight.timestamp.isoformat()
                    }
                    for insight in report.insights
                ]
            }
            
            return json.dumps(report_data, indent=2)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Example usage and testing
if __name__ == "__main__":
    async def test_insight_generation() -> None:
        """Test insight generation engine"""
        
        # Initialize insight generation engine
        engine = InsightGenerationEngine()
        
        print("🧠 Testing Insight Generation Engine...")
        
        # Prepare sample data sources
        data_sources = {
            "metrics_data": {
                "values": {
                    "response_time": [45, 48, 52, 47, 49, 51, 55, 58, 62, 67],
                    "throughput": [1200, 1180, 1220, 1250, 1190, 1210, 1280, 1300, 1350, 1400],
                    "error_rate": [0.2, 0.3, 0.1, 0.2, 0.4, 0.6, 0.3, 0.2, 0.1, 0.2],
                    "user_engagement": [85, 87, 89, 91, 88, 90, 92, 95, 97, 100]
                },
                "timestamps": [datetime.now() - timedelta(days=i) for i in range(9, -1, -1)]
            },
            "business_data": {
                "revenue_data": {
                    "historical_revenue": [45000, 48000, 52000, 47000, 49000, 51000, 55000, 58000, 62000, 67000],
                    "revenue_streams": {
                        "platform_fees": 30000,
                        "premium_subscriptions": 20000,
                        "advertising": 15000,
                        "partnerships": 2000
                    }
                },
                "cost_data": {
                    "historical_costs": [25000, 26000, 27000, 28000, 29000, 30000, 31000, 32000, 33000, 34000],
                    "cost_categories": {
                        "infrastructure": 18000,
                        "development": 8000,
                        "marketing": 5000,
                        "operations": 3000
                    }
                },
                "creator_data": {
                    "creator_metrics": {
                        "musician": {"revenue": 25000, "engagement": 450000},
                        "photographer": {"revenue": 20000, "engagement": 380000},
                        "blogger": {"revenue": 15000, "engagement": 520000},
                        "influencer": {"revenue": 7000, "engagement": 280000}
                    }
                }
            },
            "historical_data": {
                "monthly_revenue": [40000, 42000, 45000, 48000, 52000, 55000, 58000, 62000, 65000, 67000],
                "monthly_users": [12000, 12500, 13000, 13800, 14200, 14800, 15400, 16000, 16800, 17500],
                "monthly_engagement": [75, 78, 82, 85, 88, 90, 92, 95, 97, 100]
            }
        }
        
        # Generate comprehensive insights
        print("🔍 Generating comprehensive insights...")
        
        report = await engine.generate_comprehensive_insights(data_sources, analysis_period_days=30)
        
        print(f"\n📋 Insight Generation Results:")
        print(f"   Report ID: {report.report_id}")
        print(f"   Report Title: {report.report_title}")
        print(f"   Generated: {report.generated_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Total Insights: {len(report.insights)}")
        
        print(f"\n📊 Executive Summary:")
        print(f"   {report.executive_summary}")
        
        print(f"\n📈 Key Metrics:")
        for metric, value in report.key_metrics.items():
            print(f"   {metric}: {value:.2f}")
        
        print(f"\n🎯 Top Insights:")
        for i, insight in enumerate(report.insights[:5], 1):
            print(f"   {i}. [{insight.priority.value.upper()}] {insight.title}")
            print(f"      Confidence: {insight.confidence_score:.2f}, Impact: {insight.impact_score:.2f}")
            print(f"      {insight.description}")
        
        print(f"\n📋 Strategic Recommendations:")
        for rec in report.strategic_recommendations[:5]:
            print(f"   • {rec}")
        
        print(f"\n⚠️ Risk Alerts:")
        for alert in report.risk_alerts:
            print(f"   {alert}")
        
        print(f"\n🚀 Opportunities:")
        for opp in report.opportunity_highlights:
            print(f"   {opp}")
        
        print(f"\n📊 Trend Analysis:")
        for metric, analysis in report.trend_analysis.items():
            direction = analysis.get("trend_direction", "unknown")
            strength = analysis.get("trend_strength", 0)
            change = analysis.get("recent_change", 0)
            print(f"   {metric}: {direction} trend (strength: {strength:.2f}, change: {change:+.1f}%)")
        
        # Export report
        print(f"\n📄 Exporting insights report...")
        report_json = engine.export_insights_report(report, "json")
        
        # Save to file
        report_path = "/tmp/insights_report.json"
        with open(report_path, 'w') as f:
            f.write(report_json)
        
        print(f"   Report exported to: {report_path}")
        print(f"   Report size: {len(report_json):,} characters")
        
        print(f"\n✅ Insight generation engine test completed")
    
    # Run test
    asyncio.run(test_insight_generation())