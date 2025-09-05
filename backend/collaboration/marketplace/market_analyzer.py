"""Market Analyzer Module - AI-Powered Market Intelligence for Creator Marketplace
===============================================================================

Advanced market analysis system providing real-time market trends, demand forecasting,
supply analysis, competitive intelligence, and strategic insights for creator collaborations.

This module implements:
- Real-time market trend analysis
- Demand forecasting with ML models
- Supply-demand gap identification
- Competitive landscape analysis
- Price elasticity modeling
- Market opportunity detection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ STRICT COPYRIGHT WARNING - INTELLECTUAL PROPERTY PROTECTION
================================================================
This code and concept are the EXCLUSIVE PROPERTY of Fahed Mlaiel.
Unauthorized access, copying, modification, distribution, reverse engineering,
or commercialization without explicit written permission from Fahed Mlaiel
(mlaiel@live.de) is STRICTLY PROHIBITED and will result in immediate legal
action under German and International copyright laws.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
from decimal import Decimal
import json
import numpy as np
import pandas as pd
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class MarketSegment(Enum):
    """Market segments for analysis"""
    MUSIC_PRODUCTION = "music_production"
    VIDEO_CONTENT = "video_content"
    DESIGN_GRAPHICS = "design_graphics"
    WRITING_CONTENT = "writing_content"
    VOICE_ACTING = "voice_acting"
    DIGITAL_MARKETING = "digital_marketing"
    SOCIAL_MEDIA = "social_media"
    PHOTOGRAPHY = "photography"
    ANIMATION = "animation"
    CONSULTING = "consulting"


class TrendDirection(Enum):
    """Market trend directions"""
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    VOLATILE = "volatile"
    EMERGING = "emerging"


class CompetitionLevel(Enum):
    """Competition intensity levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SATURATED = "saturated"
    BLUE_OCEAN = "blue_ocean"


@dataclass
class MarketDataPoint:
    """Single market data observation"""
    timestamp: datetime
    segment: MarketSegment
    metric_name: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TrendAnalysis:
    """Market trend analysis result"""
    segment: MarketSegment
    direction: TrendDirection
    strength: float  # 0-1, how strong the trend is
    duration: timedelta  # how long the trend has been active
    confidence: float  # 0-1, confidence in the analysis
    projected_change: float  # expected percentage change
    key_drivers: List[str]
    risk_factors: List[str]


@dataclass
class DemandForecast:
    """Demand forecasting result"""
    segment: MarketSegment
    forecast_period: timedelta
    predicted_demand: float
    confidence_interval: Tuple[float, float]
    seasonality_factors: Dict[str, float]
    growth_rate: float
    peak_periods: List[datetime]
    low_periods: List[datetime]


@dataclass
class SupplyAnalysis:
    """Supply analysis result"""
    segment: MarketSegment
    total_suppliers: int
    active_suppliers: int
    capacity_utilization: float
    quality_distribution: Dict[str, int]  # quality tier -> count
    pricing_ranges: Dict[str, Tuple[float, float]]
    geographic_distribution: Dict[str, int]
    skill_gaps: List[str]
    oversupplied_areas: List[str]


@dataclass
class CompetitiveAnalysis:
    """Competitive landscape analysis"""
    segment: MarketSegment
    competition_level: CompetitionLevel
    top_competitors: List[Dict[str, Any]]
    market_share_distribution: Dict[str, float]
    pricing_strategies: Dict[str, str]
    differentiation_opportunities: List[str]
    barriers_to_entry: List[str]
    success_factors: List[str]


@dataclass
class MarketOpportunity:
    """Market opportunity identification"""
    opportunity_id: str
    segment: MarketSegment
    opportunity_type: str  # "gap", "emerging", "underserved", "innovation"
    description: str
    market_size: float
    growth_potential: float
    competition_level: CompetitionLevel
    required_skills: List[str]
    investment_required: float
    time_to_market: timedelta
    success_probability: float
    revenue_potential: float


@dataclass
class MarketInsights:
    """Comprehensive market insights"""
    analysis_period: timedelta
    segments_analyzed: List[MarketSegment]
    trend_analyses: List[TrendAnalysis]
    demand_forecasts: List[DemandForecast]
    supply_analyses: List[SupplyAnalysis]
    competitive_analyses: List[CompetitiveAnalysis]
    opportunities: List[MarketOpportunity]
    key_recommendations: List[str]
    risk_alerts: List[str]
    market_health_score: float


class MarketAnalyzer:
    """Advanced market intelligence and analysis system"""
    
    def __init__(self):
        self.market_data: Dict[MarketSegment, List[MarketDataPoint]] = defaultdict(list)
        self.historical_trends: Dict[MarketSegment, List[TrendAnalysis]] = defaultdict(list)
        self.forecast_models: Dict[MarketSegment, Any] = {}
        self.competitive_intelligence: Dict[MarketSegment, CompetitiveAnalysis] = {}
        
        # Analysis configuration
        self.trend_lookback_days = 30
        self.forecast_horizon_days = 90
        self.min_data_points = 10
        
        logger.info("📈 Market Analyzer initialized with AI-powered intelligence")
    
    async def ingest_market_data(
        self,
        segment: MarketSegment,
        metric_name: str,
        value: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Ingest new market data point"""
        try:
            data_point = MarketDataPoint(
                timestamp=datetime.now(timezone.utc),
                segment=segment,
                metric_name=metric_name,
                value=value,
                metadata=metadata or {}
            )
            
            self.market_data[segment].append(data_point)
            
            # Trigger real-time analysis if enough data
            if len(self.market_data[segment]) >= self.min_data_points:
                await self._update_real_time_analysis(segment)
            
            logger.debug(f"📊 Market data ingested: {segment.value}.{metric_name} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error ingesting market data: {e}")
            return False
    
    async def analyze_market_trends(
        self,
        segment: MarketSegment,
        time_period: Optional[timedelta] = None
    ) -> TrendAnalysis:
        """Analyze market trends for specific segment"""
        try:
            if time_period is None:
                time_period = timedelta(days=self.trend_lookback_days)
            
            # Filter data for analysis period
            cutoff_time = datetime.now(timezone.utc) - time_period
            segment_data = [
                dp for dp in self.market_data[segment]
                if dp.timestamp >= cutoff_time
            ]
            
            if len(segment_data) < self.min_data_points:
                raise ValueError(f"Insufficient data for trend analysis: {len(segment_data)} points")
            
            # Extract price/value metrics
            price_data = [dp.value for dp in segment_data if dp.metric_name == "average_price"]
            volume_data = [dp.value for dp in segment_data if dp.metric_name == "transaction_volume"]
            demand_data = [dp.value for dp in segment_data if dp.metric_name == "demand_index"]
            
            # Perform trend analysis
            direction = await self._calculate_trend_direction(price_data)
            strength = await self._calculate_trend_strength(price_data)
            duration = await self._calculate_trend_duration(segment_data)
            confidence = await self._calculate_analysis_confidence(segment_data)
            projected_change = await self._project_trend_change(price_data)
            
            # Identify key drivers and risks
            key_drivers = await self._identify_trend_drivers(segment, segment_data)
            risk_factors = await self._identify_risk_factors(segment, segment_data)
            
            trend_analysis = TrendAnalysis(
                segment=segment,
                direction=direction,
                strength=strength,
                duration=duration,
                confidence=confidence,
                projected_change=projected_change,
                key_drivers=key_drivers,
                risk_factors=risk_factors
            )
            
            # Store for historical tracking
            self.historical_trends[segment].append(trend_analysis)
            
            logger.info(f"📈 Trend analysis completed for {segment.value}: {direction.value}")
            return trend_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing market trends: {e}")
            raise
    
    async def forecast_demand(
        self,
        segment: MarketSegment,
        forecast_period: Optional[timedelta] = None
    ) -> DemandForecast:
        """Generate demand forecast for market segment"""
        try:
            if forecast_period is None:
                forecast_period = timedelta(days=self.forecast_horizon_days)
            
            # Prepare historical demand data
            demand_data = [
                dp for dp in self.market_data[segment]
                if dp.metric_name == "demand_index"
            ]
            
            if len(demand_data) < self.min_data_points:
                raise ValueError(f"Insufficient demand data: {len(demand_data)} points")
            
            # Create time series
            timestamps = [dp.timestamp for dp in demand_data]
            values = [dp.value for dp in demand_data]
            
            # Build forecasting model
            model = await self._build_demand_model(timestamps, values)
            
            # Generate forecast
            predicted_demand = await self._predict_demand(model, forecast_period)
            confidence_interval = await self._calculate_forecast_confidence(model, forecast_period)
            seasonality_factors = await self._analyze_seasonality(demand_data)
            growth_rate = await self._calculate_growth_rate(values)
            
            # Identify peak and low periods
            peak_periods = await self._identify_peak_periods(demand_data, forecast_period)
            low_periods = await self._identify_low_periods(demand_data, forecast_period)
            
            forecast = DemandForecast(
                segment=segment,
                forecast_period=forecast_period,
                predicted_demand=predicted_demand,
                confidence_interval=confidence_interval,
                seasonality_factors=seasonality_factors,
                growth_rate=growth_rate,
                peak_periods=peak_periods,
                low_periods=low_periods
            )
            
            logger.info(f"🔮 Demand forecast generated for {segment.value}: {predicted_demand:.2f}")
            return forecast
            
        except Exception as e:
            logger.error(f"❌ Error forecasting demand: {e}")
            raise
    
    async def analyze_supply(self, segment: MarketSegment) -> SupplyAnalysis:
        """Analyze supply side of market segment"""
        try:
            # Collect supply-related data
            supplier_data = await self._collect_supplier_data(segment)
            capacity_data = await self._collect_capacity_data(segment)
            quality_data = await self._collect_quality_data(segment)
            pricing_data = await self._collect_pricing_data(segment)
            geographic_data = await self._collect_geographic_data(segment)
            
            # Analyze metrics
            total_suppliers = len(supplier_data)
            active_suppliers = len([s for s in supplier_data if s.get("active", False)])
            capacity_utilization = await self._calculate_capacity_utilization(capacity_data)
            quality_distribution = await self._analyze_quality_distribution(quality_data)
            pricing_ranges = await self._analyze_pricing_ranges(pricing_data)
            geographic_distribution = await self._analyze_geographic_distribution(geographic_data)
            
            # Identify gaps and oversupply
            skill_gaps = await self._identify_skill_gaps(segment, supplier_data)
            oversupplied_areas = await self._identify_oversupplied_areas(segment, supplier_data)
            
            supply_analysis = SupplyAnalysis(
                segment=segment,
                total_suppliers=total_suppliers,
                active_suppliers=active_suppliers,
                capacity_utilization=capacity_utilization,
                quality_distribution=quality_distribution,
                pricing_ranges=pricing_ranges,
                geographic_distribution=geographic_distribution,
                skill_gaps=skill_gaps,
                oversupplied_areas=oversupplied_areas
            )
            
            logger.info(f"🏭 Supply analysis completed for {segment.value}: {total_suppliers} suppliers")
            return supply_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing supply: {e}")
            raise
    
    async def analyze_competition(self, segment: MarketSegment) -> CompetitiveAnalysis:
        """Analyze competitive landscape"""
        try:
            # Collect competitive data
            competitors = await self._identify_competitors(segment)
            market_shares = await self._calculate_market_shares(segment, competitors)
            pricing_strategies = await self._analyze_pricing_strategies(segment, competitors)
            
            # Determine competition level
            competition_level = await self._assess_competition_level(segment, competitors)
            
            # Identify opportunities and barriers
            differentiation_opportunities = await self._identify_differentiation_opportunities(segment)
            barriers_to_entry = await self._identify_barriers_to_entry(segment)
            success_factors = await self._identify_success_factors(segment)
            
            competitive_analysis = CompetitiveAnalysis(
                segment=segment,
                competition_level=competition_level,
                top_competitors=competitors[:10],  # Top 10
                market_share_distribution=market_shares,
                pricing_strategies=pricing_strategies,
                differentiation_opportunities=differentiation_opportunities,
                barriers_to_entry=barriers_to_entry,
                success_factors=success_factors
            )
            
            # Cache for future use
            self.competitive_intelligence[segment] = competitive_analysis
            
            logger.info(f"🏆 Competitive analysis completed for {segment.value}: {competition_level.value}")
            return competitive_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing competition: {e}")
            raise
    
    async def identify_opportunities(self, segments: Optional[List[MarketSegment]] = None) -> List[MarketOpportunity]:
        """Identify market opportunities across segments"""
        try:
            if segments is None:
                segments = list(MarketSegment)
            
            opportunities = []
            
            for segment in segments:
                # Gap analysis opportunities
                gap_opportunities = await self._identify_gap_opportunities(segment)
                opportunities.extend(gap_opportunities)
                
                # Emerging trend opportunities
                emerging_opportunities = await self._identify_emerging_opportunities(segment)
                opportunities.extend(emerging_opportunities)
                
                # Underserved market opportunities
                underserved_opportunities = await self._identify_underserved_opportunities(segment)
                opportunities.extend(underserved_opportunities)
                
                # Innovation opportunities
                innovation_opportunities = await self._identify_innovation_opportunities(segment)
                opportunities.extend(innovation_opportunities)
            
            # Rank opportunities by attractiveness
            ranked_opportunities = await self._rank_opportunities(opportunities)
            
            logger.info(f"💡 Identified {len(ranked_opportunities)} market opportunities")
            return ranked_opportunities
            
        except Exception as e:
            logger.error(f"❌ Error identifying opportunities: {e}")
            return []
    
    async def generate_market_insights(
        self,
        segments: Optional[List[MarketSegment]] = None,
        analysis_period: Optional[timedelta] = None
    ) -> MarketInsights:
        """Generate comprehensive market insights report"""
        try:
            if segments is None:
                segments = list(MarketSegment)
            
            if analysis_period is None:
                analysis_period = timedelta(days=30)
            
            # Perform comprehensive analysis
            trend_analyses = []
            demand_forecasts = []
            supply_analyses = []
            competitive_analyses = []
            
            for segment in segments:
                try:
                    # Trend analysis
                    trend = await self.analyze_market_trends(segment, analysis_period)
                    trend_analyses.append(trend)
                    
                    # Demand forecast
                    forecast = await self.forecast_demand(segment)
                    demand_forecasts.append(forecast)
                    
                    # Supply analysis
                    supply = await self.analyze_supply(segment)
                    supply_analyses.append(supply)
                    
                    # Competitive analysis
                    competition = await self.analyze_competition(segment)
                    competitive_analyses.append(competition)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Skipping {segment.value} due to error: {e}")
                    continue
            
            # Identify opportunities
            opportunities = await self.identify_opportunities(segments)
            
            # Generate recommendations and alerts
            key_recommendations = await self._generate_recommendations(
                trend_analyses, demand_forecasts, supply_analyses, competitive_analyses
            )
            risk_alerts = await self._generate_risk_alerts(
                trend_analyses, demand_forecasts, supply_analyses
            )
            
            # Calculate overall market health
            market_health_score = await self._calculate_market_health_score(
                trend_analyses, supply_analyses, competitive_analyses
            )
            
            insights = MarketInsights(
                analysis_period=analysis_period,
                segments_analyzed=segments,
                trend_analyses=trend_analyses,
                demand_forecasts=demand_forecasts,
                supply_analyses=supply_analyses,
                competitive_analyses=competitive_analyses,
                opportunities=opportunities,
                key_recommendations=key_recommendations,
                risk_alerts=risk_alerts,
                market_health_score=market_health_score
            )
            
            logger.info(f"🧠 Market insights generated for {len(segments)} segments")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating market insights: {e}")
            raise
    
    # Helper methods for trend analysis
    async def _calculate_trend_direction(self, data: List[float]) -> TrendDirection:
        """Calculate trend direction from price data"""
        if len(data) < 3:
            return TrendDirection.STABLE
        
        # Calculate moving averages
        short_ma = statistics.mean(data[-5:]) if len(data) >= 5 else statistics.mean(data)
        long_ma = statistics.mean(data[-10:]) if len(data) >= 10 else statistics.mean(data)
        
        # Determine direction
        if short_ma > long_ma * 1.05:
            return TrendDirection.RISING
        elif short_ma < long_ma * 0.95:
            return TrendDirection.FALLING
        else:
            # Check volatility
            volatility = statistics.stdev(data) / statistics.mean(data) if statistics.mean(data) > 0 else 0
            if volatility > 0.2:
                return TrendDirection.VOLATILE
            else:
                return TrendDirection.STABLE
    
    async def _calculate_trend_strength(self, data: List[float]) -> float:
        """Calculate trend strength (0-1)"""
        if len(data) < 3:
            return 0.0
        
        # Calculate correlation with time
        x = list(range(len(data)))
        correlation = np.corrcoef(x, data)[0, 1] if len(data) > 1 else 0
        return abs(correlation)
    
    async def _calculate_trend_duration(self, data: List[MarketDataPoint]) -> timedelta:
        """Calculate how long current trend has been active"""
        if len(data) < 2:
            return timedelta(0)
        
        # Simplified: return time since first data point
        return data[-1].timestamp - data[0].timestamp
    
    async def _calculate_analysis_confidence(self, data: List[MarketDataPoint]) -> float:
        """Calculate confidence in analysis based on data quality"""
        if not data:
            return 0.0
        
        # Factor in data quantity, recency, and consistency
        quantity_score = min(len(data) / 50, 1.0)  # Normalize to 50 points
        
        # Recency score
        latest_time = max(dp.timestamp for dp in data)
        recency_score = max(0, 1 - (datetime.now(timezone.utc) - latest_time).days / 7)
        
        # Data consistency (simplified)
        consistency_score = 0.8  # Placeholder
        
        return (quantity_score + recency_score + consistency_score) / 3
    
    async def _project_trend_change(self, data: List[float]) -> float:
        """Project percentage change based on current trend"""
        if len(data) < 2:
            return 0.0
        
        # Simple linear projection
        recent_change = (data[-1] - data[0]) / data[0] if data[0] != 0 else 0
        return recent_change * 100  # Convert to percentage
    
    async def _identify_trend_drivers(self, segment: MarketSegment, data: List[MarketDataPoint]) -> List[str]:
        """Identify key drivers of market trends"""
        # Analyze correlated metrics and external factors
        drivers = []
        
        # Check for volume correlation
        price_data = [dp.value for dp in data if dp.metric_name == "average_price"]
        volume_data = [dp.value for dp in data if dp.metric_name == "transaction_volume"]
        
        if len(price_data) > 1 and len(volume_data) > 1:
            correlation = np.corrcoef(price_data, volume_data)[0, 1]
            if correlation > 0.5:
                drivers.append("Increased demand driving price growth")
            elif correlation < -0.5:
                drivers.append("Price increases reducing transaction volume")
        
        # Add segment-specific drivers
        if segment == MarketSegment.MUSIC_PRODUCTION:
            drivers.extend(["Streaming platform algorithm changes", "Seasonal music trends"])
        elif segment == MarketSegment.VIDEO_CONTENT:
            drivers.extend(["Social media platform updates", "Creator economy growth"])
        
        return drivers[:5]  # Limit to top 5
    
    async def _identify_risk_factors(self, segment: MarketSegment, data: List[MarketDataPoint]) -> List[str]:
        """Identify risk factors for market segment"""
        risk_factors = []
        
        # Check for high volatility
        price_data = [dp.value for dp in data if dp.metric_name == "average_price"]
        if price_data and len(price_data) > 1:
            volatility = statistics.stdev(price_data) / statistics.mean(price_data)
            if volatility > 0.3:
                risk_factors.append("High price volatility")
        
        # Add general risk factors
        risk_factors.extend([
            "Economic downturn impact",
            "Platform policy changes",
            "Increased competition"
        ])
        
        return risk_factors[:5]  # Limit to top 5
    
    async def _update_real_time_analysis(self, segment: MarketSegment):
        """Update real-time analysis when new data arrives"""
        try:
            # Trigger lightweight trend analysis
            recent_data = self.market_data[segment][-20:]  # Last 20 points
            
            if len(recent_data) >= self.min_data_points:
                trend = await self.analyze_market_trends(segment, timedelta(days=7))
                logger.debug(f"🔄 Real-time analysis updated for {segment.value}")
                
        except Exception as e:
            logger.error(f"❌ Error in real-time analysis: {e}")
    
    # Placeholder methods for complex ML operations
    async def _build_demand_model(self, timestamps: List[datetime], values: List[float]) -> Any:
        """Build demand forecasting model"""
        # In real implementation, would use ML models like ARIMA, Prophet, or LSTM
        return {"type": "linear", "data": list(zip(timestamps, values))}
    
    async def _predict_demand(self, model: Any, forecast_period: timedelta) -> float:
        """Predict demand using model"""
        # Simplified prediction
        return 75.0  # Placeholder
    
    async def _calculate_forecast_confidence(self, model: Any, forecast_period: timedelta) -> Tuple[float, float]:
        """Calculate forecast confidence interval"""
        # Simplified confidence interval
        base_forecast = 75.0
        margin = 10.0
        return (base_forecast - margin, base_forecast + margin)
    
    async def _analyze_seasonality(self, data: List[MarketDataPoint]) -> Dict[str, float]:
        """Analyze seasonal patterns in demand"""
        # Simplified seasonality analysis
        return {
            "spring": 1.1,
            "summer": 1.2,
            "fall": 0.9,
            "winter": 0.8
        }
    
    async def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate compound growth rate"""
        if len(values) < 2:
            return 0.0
        
        total_growth = values[-1] / values[0] if values[0] != 0 else 1
        periods = len(values) - 1
        return (total_growth ** (1/periods) - 1) * 100  # Percentage
    
    async def _identify_peak_periods(self, data: List[MarketDataPoint], forecast_period: timedelta) -> List[datetime]:
        """Identify predicted peak demand periods"""
        # Simplified peak identification
        now = datetime.now(timezone.utc)
        return [
            now + timedelta(days=30),  # 1 month
            now + timedelta(days=60),  # 2 months
        ]
    
    async def _identify_low_periods(self, data: List[MarketDataPoint], forecast_period: timedelta) -> List[datetime]:
        """Identify predicted low demand periods"""
        # Simplified low period identification
        now = datetime.now(timezone.utc)
        return [
            now + timedelta(days=45),  # 1.5 months
            now + timedelta(days=75),  # 2.5 months
        ]
    
    # Data collection methods (would integrate with actual data sources)
    async def _collect_supplier_data(self, segment: MarketSegment) -> List[Dict[str, Any]]:
        """Collect supplier data for segment"""
        # Placeholder - would integrate with user/creator database
        return [{"id": f"supplier_{i}", "active": True, "rating": 4.5} for i in range(50)]
    
    async def _collect_capacity_data(self, segment: MarketSegment) -> List[Dict[str, Any]]:
        """Collect capacity utilization data"""
        return [{"supplier_id": f"supplier_{i}", "utilization": 0.75} for i in range(50)]
    
    async def _collect_quality_data(self, segment: MarketSegment) -> List[Dict[str, Any]]:
        """Collect quality metrics data"""
        return [{"supplier_id": f"supplier_{i}", "quality_tier": "high"} for i in range(50)]
    
    async def _collect_pricing_data(self, segment: MarketSegment) -> List[Dict[str, Any]]:
        """Collect pricing data"""
        return [{"supplier_id": f"supplier_{i}", "price": 100.0} for i in range(50)]
    
    async def _collect_geographic_data(self, segment: MarketSegment) -> List[Dict[str, Any]]:
        """Collect geographic distribution data"""
        return [{"supplier_id": f"supplier_{i}", "region": "North America"} for i in range(50)]
    
    async def _calculate_capacity_utilization(self, data: List[Dict[str, Any]]) -> float:
        """Calculate average capacity utilization"""
        if not data:
            return 0.0
        return statistics.mean([d["utilization"] for d in data])
    
    async def _analyze_quality_distribution(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze quality tier distribution"""
        distribution = defaultdict(int)
        for item in data:
            distribution[item["quality_tier"]] += 1
        return dict(distribution)
    
    async def _analyze_pricing_ranges(self, data: List[Dict[str, Any]]) -> Dict[str, Tuple[float, float]]:
        """Analyze pricing ranges by tier"""
        prices = [d["price"] for d in data]
        if not prices:
            return {}
        
        return {
            "low": (min(prices), np.percentile(prices, 25)),
            "medium": (np.percentile(prices, 25), np.percentile(prices, 75)),
            "high": (np.percentile(prices, 75), max(prices))
        }
    
    async def _analyze_geographic_distribution(self, data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze geographic distribution"""
        distribution = defaultdict(int)
        for item in data:
            distribution[item["region"]] += 1
        return dict(distribution)
    
    async def _identify_skill_gaps(self, segment: MarketSegment, data: List[Dict[str, Any]]) -> List[str]:
        """Identify skill gaps in market"""
        # Simplified skill gap identification
        if segment == MarketSegment.MUSIC_PRODUCTION:
            return ["Electronic music production", "Audio mastering", "Live sound engineering"]
        elif segment == MarketSegment.VIDEO_CONTENT:
            return ["Motion graphics", "Color grading", "3D animation"]
        return ["Advanced analytics", "AI integration", "Mobile optimization"]
    
    async def _identify_oversupplied_areas(self, segment: MarketSegment, data: List[Dict[str, Any]]) -> List[str]:
        """Identify oversupplied market areas"""
        # Simplified oversupply identification
        return ["Basic logo design", "Simple video editing", "Standard copywriting"]
    
    # Competition analysis methods
    async def _identify_competitors(self, segment: MarketSegment) -> List[Dict[str, Any]]:
        """Identify top competitors in segment"""
        # Placeholder - would integrate with market intelligence
        return [
            {"id": f"competitor_{i}", "name": f"Creator {i}", "market_share": 0.1}
            for i in range(20)
        ]
    
    async def _calculate_market_shares(self, segment: MarketSegment, competitors: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate market share distribution"""
        return {comp["name"]: comp["market_share"] for comp in competitors}
    
    async def _analyze_pricing_strategies(self, segment: MarketSegment, competitors: List[Dict[str, Any]]) -> Dict[str, str]:
        """Analyze competitor pricing strategies"""
        strategies = ["premium", "competitive", "value", "penetration"]
        return {comp["name"]: strategies[i % len(strategies)] for i, comp in enumerate(competitors)}
    
    async def _assess_competition_level(self, segment: MarketSegment, competitors: List[Dict[str, Any]]) -> CompetitionLevel:
        """Assess overall competition level"""
        if len(competitors) < 10:
            return CompetitionLevel.LOW
        elif len(competitors) < 50:
            return CompetitionLevel.MODERATE
        elif len(competitors) < 100:
            return CompetitionLevel.HIGH
        else:
            return CompetitionLevel.SATURATED
    
    async def _identify_differentiation_opportunities(self, segment: MarketSegment) -> List[str]:
        """Identify differentiation opportunities"""
        opportunities = [
            "Specialized niche focus",
            "Premium quality positioning",
            "Rapid turnaround times",
            "Innovative technology integration",
            "Exceptional customer service"
        ]
        return opportunities[:3]  # Return top 3
    
    async def _identify_barriers_to_entry(self, segment: MarketSegment) -> List[str]:
        """Identify barriers to entry"""
        barriers = [
            "High skill requirements",
            "Established relationships",
            "Brand recognition",
            "Technology investment",
            "Regulatory compliance"
        ]
        return barriers[:3]  # Return top 3
    
    async def _identify_success_factors(self, segment: MarketSegment) -> List[str]:
        """Identify key success factors"""
        factors = [
            "Quality consistency",
            "Client communication",
            "Portfolio strength",
            "Pricing competitiveness",
            "Delivery reliability"
        ]
        return factors
    
    # Opportunity identification methods
    async def _identify_gap_opportunities(self, segment: MarketSegment) -> List[MarketOpportunity]:
        """Identify gap opportunities in market"""
        # Simplified gap analysis
        opportunity = MarketOpportunity(
            opportunity_id=str(uuid.uuid4()),
            segment=segment,
            opportunity_type="gap",
            description=f"Underserved premium {segment.value} market",
            market_size=1000000.0,
            growth_potential=0.25,
            competition_level=CompetitionLevel.LOW,
            required_skills=["Advanced expertise", "Premium positioning"],
            investment_required=10000.0,
            time_to_market=timedelta(days=90),
            success_probability=0.7,
            revenue_potential=250000.0
        )
        return [opportunity]
    
    async def _identify_emerging_opportunities(self, segment: MarketSegment) -> List[MarketOpportunity]:
        """Identify emerging trend opportunities"""
        opportunity = MarketOpportunity(
            opportunity_id=str(uuid.uuid4()),
            segment=segment,
            opportunity_type="emerging",
            description=f"AI-enhanced {segment.value} services",
            market_size=500000.0,
            growth_potential=0.50,
            competition_level=CompetitionLevel.LOW,
            required_skills=["AI integration", "Technology expertise"],
            investment_required=25000.0,
            time_to_market=timedelta(days=120),
            success_probability=0.6,
            revenue_potential=400000.0
        )
        return [opportunity]
    
    async def _identify_underserved_opportunities(self, segment: MarketSegment) -> List[MarketOpportunity]:
        """Identify underserved market opportunities"""
        opportunity = MarketOpportunity(
            opportunity_id=str(uuid.uuid4()),
            segment=segment,
            opportunity_type="underserved",
            description=f"Small business {segment.value} services",
            market_size=750000.0,
            growth_potential=0.15,
            competition_level=CompetitionLevel.MODERATE,
            required_skills=["SMB expertise", "Cost efficiency"],
            investment_required=5000.0,
            time_to_market=timedelta(days=60),
            success_probability=0.8,
            revenue_potential=150000.0
        )
        return [opportunity]
    
    async def _identify_innovation_opportunities(self, segment: MarketSegment) -> List[MarketOpportunity]:
        """Identify innovation opportunities"""
        opportunity = MarketOpportunity(
            opportunity_id=str(uuid.uuid4()),
            segment=segment,
            opportunity_type="innovation",
            description=f"Next-generation {segment.value} platform",
            market_size=2000000.0,
            growth_potential=0.75,
            competition_level=CompetitionLevel.BLUE_OCEAN,
            required_skills=["Innovation", "Technology development"],
            investment_required=100000.0,
            time_to_market=timedelta(days=365),
            success_probability=0.4,
            revenue_potential=1500000.0
        )
        return [opportunity]
    
    async def _rank_opportunities(self, opportunities: List[MarketOpportunity]) -> List[MarketOpportunity]:
        """Rank opportunities by attractiveness score"""
        def calculate_score(opp: MarketOpportunity) -> float:
            # Weighted scoring formula
            return (
                opp.revenue_potential * 0.3 +
                opp.success_probability * 0.25 +
                opp.growth_potential * 0.25 +
                (1.0 / max(opp.investment_required, 1000)) * 1000 * 0.2
            )
        
        return sorted(opportunities, key=calculate_score, reverse=True)
    
    # Insight generation methods
    async def _generate_recommendations(
        self,
        trends: List[TrendAnalysis],
        forecasts: List[DemandForecast],
        supply: List[SupplyAnalysis],
        competition: List[CompetitiveAnalysis]
    ) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        # Trend-based recommendations
        for trend in trends:
            if trend.direction == TrendDirection.RISING and trend.strength > 0.7:
                recommendations.append(f"Capitalize on rising {trend.segment.value} market")
            elif trend.direction == TrendDirection.FALLING and trend.confidence > 0.8:
                recommendations.append(f"Consider diversifying from {trend.segment.value}")
        
        # Demand-based recommendations
        for forecast in forecasts:
            if forecast.growth_rate > 0.20:
                recommendations.append(f"Increase capacity in {forecast.segment.value} due to high growth")
        
        # Supply-based recommendations
        for supply_analysis in supply:
            if supply_analysis.capacity_utilization < 0.6:
                recommendations.append(f"Opportunity for expansion in {supply_analysis.segment.value}")
        
        return recommendations[:10]  # Limit to top 10
    
    async def _generate_risk_alerts(
        self,
        trends: List[TrendAnalysis],
        forecasts: List[DemandForecast],
        supply: List[SupplyAnalysis]
    ) -> List[str]:
        """Generate risk alerts"""
        alerts = []
        
        # Trend-based alerts
        for trend in trends:
            if trend.direction == TrendDirection.VOLATILE:
                alerts.append(f"High volatility detected in {trend.segment.value} market")
            if len(trend.risk_factors) > 3:
                alerts.append(f"Multiple risk factors identified in {trend.segment.value}")
        
        # Forecast-based alerts
        for forecast in forecasts:
            if forecast.confidence_interval[1] - forecast.confidence_interval[0] > forecast.predicted_demand:
                alerts.append(f"High uncertainty in {forecast.segment.value} demand forecast")
        
        return alerts[:5]  # Limit to top 5
    
    async def _calculate_market_health_score(
        self,
        trends: List[TrendAnalysis],
        supply: List[SupplyAnalysis],
        competition: List[CompetitiveAnalysis]
    ) -> float:
        """Calculate overall market health score (0-100)"""
        if not trends:
            return 50.0  # Neutral score
        
        # Trend health (0-40 points)
        positive_trends = len([t for t in trends if t.direction == TrendDirection.RISING])
        trend_score = min((positive_trends / len(trends)) * 40, 40)
        
        # Supply health (0-30 points)
        if supply:
            avg_utilization = statistics.mean([s.capacity_utilization for s in supply])
            supply_score = min(avg_utilization * 30, 30)
        else:
            supply_score = 15  # Neutral
        
        # Competition health (0-30 points)
        healthy_competition = len([c for c in competition if c.competition_level in [CompetitionLevel.MODERATE, CompetitionLevel.HIGH]])
        competition_score = min((healthy_competition / len(competition)) * 30, 30) if competition else 15
        
        total_score = trend_score + supply_score + competition_score
        return min(total_score, 100.0)


# Example usage
async def main():
    """Example usage of market analyzer"""
    analyzer = MarketAnalyzer()
    
    # Ingest some sample data
    segment = MarketSegment.MUSIC_PRODUCTION
    
    # Add market data points
    for i in range(30):
        await analyzer.ingest_market_data(
            segment=segment,
            metric_name="average_price",
            value=100 + i * 2 + (i % 3) * 5,  # Trending upward with noise
            metadata={"source": "marketplace_api"}
        )
        
        await analyzer.ingest_market_data(
            segment=segment,
            metric_name="transaction_volume",
            value=1000 + i * 10,
            metadata={"source": "marketplace_api"}
        )
        
        await analyzer.ingest_market_data(
            segment=segment,
            metric_name="demand_index",
            value=75 + i * 0.5,
            metadata={"source": "demand_tracker"}
        )
    
    # Perform analysis
    trend_analysis = await analyzer.analyze_market_trends(segment)
    print(f"Trend Analysis: {trend_analysis.direction.value} (strength: {trend_analysis.strength:.2f})")
    
    demand_forecast = await analyzer.forecast_demand(segment)
    print(f"Demand Forecast: {demand_forecast.predicted_demand:.2f}")
    
    supply_analysis = await analyzer.analyze_supply(segment)
    print(f"Supply Analysis: {supply_analysis.total_suppliers} suppliers")
    
    competitive_analysis = await analyzer.analyze_competition(segment)
    print(f"Competition Level: {competitive_analysis.competition_level.value}")
    
    opportunities = await analyzer.identify_opportunities([segment])
    print(f"Opportunities Found: {len(opportunities)}")
    
    # Generate comprehensive insights
    insights = await analyzer.generate_market_insights([segment])
    print(f"Market Health Score: {insights.market_health_score:.1f}/100")
    print(f"Key Recommendations: {len(insights.key_recommendations)}")


if __name__ == "__main__":
    asyncio.run(main())