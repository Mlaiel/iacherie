"""
💰 ROI Calculator - ML Model Business Impact Analysis Engine

💼 BUSINESS ANALYST + 🗄️ DBA + 🔬 ML ENGINEER EXPERTISE

Advanced ROI calculation system for measuring and analyzing the business impact
of ML models across all creator types, with comprehensive financial metrics,
cost tracking, and value attribution for enterprise decision making.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
Version: 1.0.0

💰 ROI CALCULATION PLATFORM
- Comprehensive financial impact analysis
- Creator-specific revenue attribution
- ML model cost tracking and optimization
- Business value measurement and reporting
- Enterprise-grade financial analytics
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
from collections import defaultdict

logger = logging.getLogger(__name__)

class CostCategory(Enum):
    """ML cost categories"""
    INFRASTRUCTURE = "infrastructure"
    COMPUTE = "compute" 
    STORAGE = "storage"
    DATA_PROCESSING = "data_processing"
    MODEL_TRAINING = "model_training"
    MODEL_SERVING = "model_serving"
    DEVELOPMENT = "development"
    MAINTENANCE = "maintenance"
    MONITORING = "monitoring"
    COMPLIANCE = "compliance"

class RevenueStream(Enum):
    """Revenue stream types"""
    CONTENT_MONETIZATION = "content_monetization"
    PLATFORM_FEES = "platform_fees"
    PREMIUM_FEATURES = "premium_features"
    ADVERTISING = "advertising"
    COLLABORATIONS = "collaborations"
    SUBSCRIPTIONS = "subscriptions"
    LICENSING = "licensing"
    ANALYTICS_INSIGHTS = "analytics_insights"

class CreatorType(Enum):
    """Creator types for specialized ROI analysis"""
    MUSICIAN = "musician"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    INFLUENCER = "influencer"
    COMEDIAN = "comedian"
    GENERAL = "general"

class TimeHorizon(Enum):
    """Time horizons for ROI analysis"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    LIFETIME = "lifetime"

@dataclass
class CostItem:
    """Individual cost item"""
    cost_id: str
    category: CostCategory
    amount: float
    currency: str = "USD"
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    model_id: Optional[str] = None
    creator_type: Optional[CreatorType] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RevenueItem:
    """Individual revenue item"""
    revenue_id: str
    stream: RevenueStream
    amount: float
    currency: str = "USD"
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    model_attribution: float = 0.0  # Percentage attributed to ML models
    creator_id: Optional[str] = None
    creator_type: Optional[CreatorType] = None
    model_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ROIMetrics:
    """ROI calculation results"""
    period_start: datetime
    period_end: datetime
    total_revenue: float
    total_costs: float
    net_profit: float
    roi_percentage: float
    revenue_attribution: float  # Revenue directly attributed to ML
    cost_breakdown: Dict[str, float]
    revenue_breakdown: Dict[str, float]
    creator_breakdown: Dict[str, Dict[str, float]]
    model_performance: Dict[str, Dict[str, float]]
    efficiency_metrics: Dict[str, float]
    currency: str = "USD"

@dataclass
class BusinessImpactAnalysis:
    """Comprehensive business impact analysis"""
    analysis_id: str
    time_horizon: TimeHorizon
    roi_metrics: ROIMetrics
    trend_analysis: Dict[str, List[float]]
    predictive_insights: Dict[str, Any]
    recommendations: List[str]
    risk_assessment: Dict[str, float]
    opportunity_analysis: Dict[str, Any]
    competitive_benchmarks: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

class CostTracker:
    """🗄️ DBA - Comprehensive cost tracking system"""
    
    def __init__(self):
        self.cost_items: List[CostItem] = []
        self.cost_categories = defaultdict(float)
        self.model_costs = defaultdict(float)
        self.creator_costs = defaultdict(float)
        
    def add_cost(self, cost_item: CostItem) -> str:
        """Add cost item to tracking system"""
        self.cost_items.append(cost_item)
        
        # Update category totals
        self.cost_categories[cost_item.category.value] += cost_item.amount
        
        # Update model costs
        if cost_item.model_id:
            self.model_costs[cost_item.model_id] += cost_item.amount
        
        # Update creator type costs
        if cost_item.creator_type:
            self.creator_costs[cost_item.creator_type.value] += cost_item.amount
        
        logger.debug(f"Added cost: {cost_item.cost_id} - ${cost_item.amount:.2f}")
        return cost_item.cost_id
    
    def get_costs_by_period(self, start_date: datetime, end_date: datetime) -> List[CostItem]:
        """Get costs for specific time period"""
        return [
            cost for cost in self.cost_items
            if start_date <= cost.timestamp <= end_date
        ]
    
    def get_costs_by_category(self, category: CostCategory, 
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> List[CostItem]:
        """Get costs by category"""
        costs = [cost for cost in self.cost_items if cost.category == category]
        
        if start_date and end_date:
            costs = [cost for cost in costs if start_date <= cost.timestamp <= end_date]
        
        return costs
    
    def get_costs_by_model(self, model_id: str,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[CostItem]:
        """Get costs for specific model"""
        costs = [cost for cost in self.cost_items if cost.model_id == model_id]
        
        if start_date and end_date:
            costs = [cost for cost in costs if start_date <= cost.timestamp <= end_date]
        
        return costs
    
    def calculate_total_costs(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate total costs for period"""
        period_costs = self.get_costs_by_period(start_date, end_date)
        return sum(cost.amount for cost in period_costs)
    
    def get_cost_breakdown(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Get detailed cost breakdown"""
        period_costs = self.get_costs_by_period(start_date, end_date)
        
        breakdown = defaultdict(float)
        for cost in period_costs:
            breakdown[cost.category.value] += cost.amount
        
        return dict(breakdown)
    
    def estimate_infrastructure_costs(self, model_id: str, usage_metrics: Dict[str, float]) -> float:
        """Estimate infrastructure costs based on usage"""
        # Cloud compute costs (simplified pricing model)
        compute_hours = usage_metrics.get("compute_hours", 0)
        gpu_hours = usage_metrics.get("gpu_hours", 0)
        storage_gb_month = usage_metrics.get("storage_gb_month", 0)
        api_calls = usage_metrics.get("api_calls", 0)
        
        # Pricing (example rates)
        compute_cost = compute_hours * 0.10  # $0.10/hour
        gpu_cost = gpu_hours * 2.50  # $2.50/hour for GPU
        storage_cost = storage_gb_month * 0.023  # $0.023/GB/month
        api_cost = api_calls * 0.001  # $0.001/call
        
        total_cost = compute_cost + gpu_cost + storage_cost + api_cost
        
        # Add infrastructure cost
        infrastructure_cost = CostItem(
            cost_id=str(uuid.uuid4()),
            category=CostCategory.INFRASTRUCTURE,
            amount=total_cost,
            description=f"Estimated infrastructure costs for model {model_id}",
            model_id=model_id,
            metadata={
                "compute_hours": compute_hours,
                "gpu_hours": gpu_hours,
                "storage_gb_month": storage_gb_month,
                "api_calls": api_calls
            }
        )
        
        self.add_cost(infrastructure_cost)
        return total_cost

class RevenueTracker:
    """💼 BUSINESS ANALYST - Revenue tracking and attribution system"""
    
    def __init__(self):
        self.revenue_items: List[RevenueItem] = []
        self.revenue_streams = defaultdict(float)
        self.model_revenue = defaultdict(float)
        self.creator_revenue = defaultdict(float)
        
    def add_revenue(self, revenue_item: RevenueItem) -> str:
        """Add revenue item to tracking system"""
        self.revenue_items.append(revenue_item)
        
        # Update stream totals
        self.revenue_streams[revenue_item.stream.value] += revenue_item.amount
        
        # Update model revenue attribution
        if revenue_item.model_id and revenue_item.model_attribution > 0:
            attributed_amount = revenue_item.amount * (revenue_item.model_attribution / 100.0)
            self.model_revenue[revenue_item.model_id] += attributed_amount
        
        # Update creator revenue
        if revenue_item.creator_type:
            self.creator_revenue[revenue_item.creator_type.value] += revenue_item.amount
        
        logger.debug(f"Added revenue: {revenue_item.revenue_id} - ${revenue_item.amount:.2f}")
        return revenue_item.revenue_id
    
    def get_revenue_by_period(self, start_date: datetime, end_date: datetime) -> List[RevenueItem]:
        """Get revenue for specific time period"""
        return [
            revenue for revenue in self.revenue_items
            if start_date <= revenue.timestamp <= end_date
        ]
    
    def get_revenue_by_stream(self, stream: RevenueStream,
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> List[RevenueItem]:
        """Get revenue by stream type"""
        revenue = [item for item in self.revenue_items if item.stream == stream]
        
        if start_date and end_date:
            revenue = [item for item in revenue if start_date <= item.timestamp <= end_date]
        
        return revenue
    
    def calculate_total_revenue(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate total revenue for period"""
        period_revenue = self.get_revenue_by_period(start_date, end_date)
        return sum(item.amount for item in period_revenue)
    
    def calculate_attributed_revenue(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate ML-attributed revenue for period"""
        period_revenue = self.get_revenue_by_period(start_date, end_date)
        
        attributed_revenue = 0.0
        for item in period_revenue:
            if item.model_attribution > 0:
                attributed_revenue += item.amount * (item.model_attribution / 100.0)
        
        return attributed_revenue
    
    def get_revenue_breakdown(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Get detailed revenue breakdown"""
        period_revenue = self.get_revenue_by_period(start_date, end_date)
        
        breakdown = defaultdict(float)
        for item in period_revenue:
            breakdown[item.stream.value] += item.amount
        
        return dict(breakdown)
    
    def analyze_creator_revenue_impact(self, creator_type: CreatorType,
                                     start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Analyze revenue impact for specific creator type"""
        creator_revenue = [
            item for item in self.revenue_items
            if (item.creator_type == creator_type and 
                start_date <= item.timestamp <= end_date)
        ]
        
        total_revenue = sum(item.amount for item in creator_revenue)
        attributed_revenue = sum(
            item.amount * (item.model_attribution / 100.0) 
            for item in creator_revenue if item.model_attribution > 0
        )
        
        return {
            "total_revenue": total_revenue,
            "ml_attributed_revenue": attributed_revenue,
            "attribution_percentage": (attributed_revenue / total_revenue * 100) if total_revenue > 0 else 0,
            "average_attribution": np.mean([item.model_attribution for item in creator_revenue if item.model_attribution > 0]) if creator_revenue else 0
        }

class ROIAnalyzer:
    """🔬 ML ENGINEER - Advanced ROI analysis and calculation engine"""
    
    def __init__(self):
        self.cost_tracker = CostTracker()
        self.revenue_tracker = RevenueTracker()
        self.analysis_history: List[BusinessImpactAnalysis] = []
        
    async def calculate_roi(self, start_date: datetime, end_date: datetime) -> ROIMetrics:
        """Calculate comprehensive ROI metrics"""
        
        # Calculate totals
        total_revenue = self.revenue_tracker.calculate_total_revenue(start_date, end_date)
        total_costs = self.cost_tracker.calculate_total_costs(start_date, end_date)
        revenue_attribution = self.revenue_tracker.calculate_attributed_revenue(start_date, end_date)
        
        # Calculate ROI
        net_profit = total_revenue - total_costs
        roi_percentage = (net_profit / total_costs * 100) if total_costs > 0 else 0
        
        # Get breakdowns
        cost_breakdown = self.cost_tracker.get_cost_breakdown(start_date, end_date)
        revenue_breakdown = self.revenue_tracker.get_revenue_breakdown(start_date, end_date)
        
        # Calculate creator-specific metrics
        creator_breakdown = await self._calculate_creator_breakdown(start_date, end_date)
        
        # Calculate model performance metrics
        model_performance = await self._calculate_model_performance(start_date, end_date)
        
        # Calculate efficiency metrics
        efficiency_metrics = await self._calculate_efficiency_metrics(
            total_revenue, total_costs, revenue_attribution
        )
        
        return ROIMetrics(
            period_start=start_date,
            period_end=end_date,
            total_revenue=total_revenue,
            total_costs=total_costs,
            net_profit=net_profit,
            roi_percentage=roi_percentage,
            revenue_attribution=revenue_attribution,
            cost_breakdown=cost_breakdown,
            revenue_breakdown=revenue_breakdown,
            creator_breakdown=creator_breakdown,
            model_performance=model_performance,
            efficiency_metrics=efficiency_metrics
        )
    
    async def analyze_business_impact(self, time_horizon: TimeHorizon,
                                    analysis_period_days: int = 30) -> BusinessImpactAnalysis:
        """Comprehensive business impact analysis"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=analysis_period_days)
        
        # Calculate ROI metrics
        roi_metrics = await self.calculate_roi(start_date, end_date)
        
        # Trend analysis
        trend_analysis = await self._analyze_trends(time_horizon, analysis_period_days)
        
        # Predictive insights
        predictive_insights = await self._generate_predictive_insights(roi_metrics, trend_analysis)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(roi_metrics, trend_analysis)
        
        # Risk assessment
        risk_assessment = await self._assess_risks(roi_metrics, trend_analysis)
        
        # Opportunity analysis
        opportunity_analysis = await self._analyze_opportunities(roi_metrics)
        
        # Competitive benchmarks
        competitive_benchmarks = await self._calculate_competitive_benchmarks()
        
        analysis = BusinessImpactAnalysis(
            analysis_id=str(uuid.uuid4()),
            time_horizon=time_horizon,
            roi_metrics=roi_metrics,
            trend_analysis=trend_analysis,
            predictive_insights=predictive_insights,
            recommendations=recommendations,
            risk_assessment=risk_assessment,
            opportunity_analysis=opportunity_analysis,
            competitive_benchmarks=competitive_benchmarks
        )
        
        self.analysis_history.append(analysis)
        return analysis
    
    async def _calculate_creator_breakdown(self, start_date: datetime, 
                                         end_date: datetime) -> Dict[str, Dict[str, float]]:
        """Calculate creator-specific ROI breakdown"""
        creator_breakdown = {}
        
        for creator_type in CreatorType:
            revenue_analysis = self.revenue_tracker.analyze_creator_revenue_impact(
                creator_type, start_date, end_date
            )
            
            # Get creator-specific costs
            creator_costs = [
                cost for cost in self.cost_tracker.get_costs_by_period(start_date, end_date)
                if cost.creator_type == creator_type
            ]
            total_creator_costs = sum(cost.amount for cost in creator_costs)
            
            # Calculate creator ROI
            creator_revenue = revenue_analysis["total_revenue"]
            creator_profit = creator_revenue - total_creator_costs
            creator_roi = (creator_profit / total_creator_costs * 100) if total_creator_costs > 0 else 0
            
            creator_breakdown[creator_type.value] = {
                "revenue": creator_revenue,
                "costs": total_creator_costs,
                "profit": creator_profit,
                "roi_percentage": creator_roi,
                "ml_attribution": revenue_analysis["ml_attributed_revenue"],
                "attribution_percentage": revenue_analysis["attribution_percentage"]
            }
        
        return creator_breakdown
    
    async def _calculate_model_performance(self, start_date: datetime,
                                         end_date: datetime) -> Dict[str, Dict[str, float]]:
        """Calculate model-specific performance metrics"""
        model_performance = {}
        
        # Get all models that had costs or revenue in the period
        models_with_costs = set()
        models_with_revenue = set()
        
        for cost in self.cost_tracker.get_costs_by_period(start_date, end_date):
            if cost.model_id:
                models_with_costs.add(cost.model_id)
        
        for revenue in self.revenue_tracker.get_revenue_by_period(start_date, end_date):
            if revenue.model_id:
                models_with_revenue.add(revenue.model_id)
        
        all_models = models_with_costs.union(models_with_revenue)
        
        for model_id in all_models:
            # Calculate model costs
            model_costs = self.cost_tracker.get_costs_by_model(model_id, start_date, end_date)
            total_model_costs = sum(cost.amount for cost in model_costs)
            
            # Calculate model revenue
            model_revenue_items = [
                item for item in self.revenue_tracker.get_revenue_by_period(start_date, end_date)
                if item.model_id == model_id
            ]
            
            model_revenue = sum(
                item.amount * (item.model_attribution / 100.0)
                for item in model_revenue_items if item.model_attribution > 0
            )
            
            # Calculate model ROI
            model_profit = model_revenue - total_model_costs
            model_roi = (model_profit / total_model_costs * 100) if total_model_costs > 0 else 0
            
            # Calculate efficiency metrics
            cost_per_inference = total_model_costs / max(1, len(model_revenue_items))
            revenue_per_inference = model_revenue / max(1, len(model_revenue_items))
            
            model_performance[model_id] = {
                "revenue": model_revenue,
                "costs": total_model_costs,
                "profit": model_profit,
                "roi_percentage": model_roi,
                "inferences": len(model_revenue_items),
                "cost_per_inference": cost_per_inference,
                "revenue_per_inference": revenue_per_inference,
                "efficiency_score": revenue_per_inference / max(0.001, cost_per_inference)
            }
        
        return model_performance
    
    async def _calculate_efficiency_metrics(self, total_revenue: float, total_costs: float,
                                          revenue_attribution: float) -> Dict[str, float]:
        """Calculate various efficiency metrics"""
        return {
            "cost_efficiency": total_revenue / max(0.001, total_costs),
            "attribution_efficiency": revenue_attribution / max(0.001, total_costs),
            "profit_margin": ((total_revenue - total_costs) / max(0.001, total_revenue)) * 100,
            "attribution_rate": (revenue_attribution / max(0.001, total_revenue)) * 100,
            "cost_recovery_rate": (revenue_attribution / max(0.001, total_costs)) * 100
        }
    
    async def _analyze_trends(self, time_horizon: TimeHorizon, 
                            period_days: int) -> Dict[str, List[float]]:
        """Analyze ROI trends over time"""
        trends = {
            "roi_trend": [],
            "revenue_trend": [],
            "cost_trend": [],
            "attribution_trend": []
        }
        
        # Calculate trends based on time horizon
        if time_horizon == TimeHorizon.WEEKLY:
            periods = 8  # 8 weeks
            period_length = 7
        elif time_horizon == TimeHorizon.MONTHLY:
            periods = 6  # 6 months
            period_length = 30
        else:
            periods = period_days  # Daily
            period_length = 1
        
        end_date = datetime.now()
        
        for i in range(periods):
            period_end = end_date - timedelta(days=i * period_length)
            period_start = period_end - timedelta(days=period_length)
            
            period_roi = await self.calculate_roi(period_start, period_end)
            
            trends["roi_trend"].insert(0, period_roi.roi_percentage)
            trends["revenue_trend"].insert(0, period_roi.total_revenue)
            trends["cost_trend"].insert(0, period_roi.total_costs)
            trends["attribution_trend"].insert(0, period_roi.revenue_attribution)
        
        return trends
    
    async def _generate_predictive_insights(self, roi_metrics: ROIMetrics,
                                          trend_analysis: Dict[str, List[float]]) -> Dict[str, Any]:
        """Generate predictive insights based on trends"""
        
        # Simple trend analysis (in production, would use more sophisticated ML models)
        roi_trend = trend_analysis["roi_trend"]
        revenue_trend = trend_analysis["revenue_trend"]
        
        if len(roi_trend) >= 3:
            roi_slope = np.polyfit(range(len(roi_trend)), roi_trend, 1)[0]
            revenue_slope = np.polyfit(range(len(revenue_trend)), revenue_trend, 1)[0]
            
            # Predict next period
            next_roi = roi_trend[-1] + roi_slope
            next_revenue = revenue_trend[-1] + revenue_slope
            
            return {
                "predicted_next_roi": next_roi,
                "predicted_next_revenue": next_revenue,
                "roi_trend_direction": "increasing" if roi_slope > 0 else "decreasing",
                "revenue_trend_direction": "increasing" if revenue_slope > 0 else "decreasing",
                "trend_confidence": min(0.95, abs(roi_slope) * 10),  # Simplified confidence
                "risk_level": "high" if next_roi < 0 else "medium" if next_roi < 10 else "low"
            }
        
        return {"insufficient_data": True}
    
    async def _generate_recommendations(self, roi_metrics: ROIMetrics,
                                      trend_analysis: Dict[str, List[float]]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # ROI-based recommendations
        if roi_metrics.roi_percentage < 0:
            recommendations.append("CRITICAL: Negative ROI detected. Immediate cost reduction or revenue optimization needed.")
        elif roi_metrics.roi_percentage < 10:
            recommendations.append("LOW ROI: Consider optimizing model efficiency or increasing revenue attribution.")
        
        # Cost optimization recommendations
        cost_breakdown = roi_metrics.cost_breakdown
        max_cost_category = max(cost_breakdown.items(), key=lambda x: x[1])[0]
        recommendations.append(f"COST OPTIMIZATION: Focus on reducing {max_cost_category} costs (${cost_breakdown[max_cost_category]:.2f})")
        
        # Revenue optimization recommendations
        if roi_metrics.revenue_attribution / roi_metrics.total_revenue < 0.3:
            recommendations.append("ATTRIBUTION: Low ML attribution rate. Improve model impact tracking or enhance model capabilities.")
        
        # Creator-specific recommendations
        creator_breakdown = roi_metrics.creator_breakdown
        best_creator_roi = max(creator_breakdown.items(), key=lambda x: x[1]["roi_percentage"])
        recommendations.append(f"SCALING: {best_creator_roi[0]} shows highest ROI ({best_creator_roi[1]['roi_percentage']:.1f}%). Consider scaling this creator type.")
        
        # Model performance recommendations
        model_performance = roi_metrics.model_performance
        if model_performance:
            best_model = max(model_performance.items(), key=lambda x: x[1]["efficiency_score"])
            recommendations.append(f"MODEL OPTIMIZATION: Model {best_model[0]} shows best efficiency. Consider applying similar optimizations to other models.")
        
        return recommendations
    
    async def _assess_risks(self, roi_metrics: ROIMetrics,
                          trend_analysis: Dict[str, List[float]]) -> Dict[str, float]:
        """Assess business risks"""
        risks = {}
        
        # ROI volatility risk
        roi_trend = trend_analysis["roi_trend"]
        if len(roi_trend) > 1:
            roi_volatility = np.std(roi_trend)
            risks["roi_volatility"] = min(1.0, roi_volatility / 50.0)  # Normalize to 0-1
        
        # Revenue concentration risk
        revenue_breakdown = roi_metrics.revenue_breakdown
        if revenue_breakdown:
            max_revenue_stream = max(revenue_breakdown.values())
            total_revenue = sum(revenue_breakdown.values())
            concentration = max_revenue_stream / total_revenue if total_revenue > 0 else 0
            risks["revenue_concentration"] = concentration
        
        # Cost escalation risk
        cost_trend = trend_analysis["cost_trend"]
        if len(cost_trend) >= 3:
            cost_slope = np.polyfit(range(len(cost_trend)), cost_trend, 1)[0]
            risks["cost_escalation"] = max(0, min(1.0, cost_slope / 1000))  # Normalize
        
        # Model dependency risk
        model_performance = roi_metrics.model_performance
        if model_performance:
            model_revenues = [perf["revenue"] for perf in model_performance.values()]
            if model_revenues:
                max_model_revenue = max(model_revenues)
                total_ml_revenue = sum(model_revenues)
                dependency = max_model_revenue / total_ml_revenue if total_ml_revenue > 0 else 0
                risks["model_dependency"] = dependency
        
        return risks
    
    async def _analyze_opportunities(self, roi_metrics: ROIMetrics) -> Dict[str, Any]:
        """Analyze growth opportunities"""
        opportunities = {}
        
        # Creator type expansion opportunities
        creator_breakdown = roi_metrics.creator_breakdown
        if creator_breakdown:
            # Find creator types with high ROI but low volume
            high_roi_creators = [
                (creator, metrics) for creator, metrics in creator_breakdown.items()
                if metrics["roi_percentage"] > 20 and metrics["revenue"] < 10000
            ]
            
            opportunities["creator_expansion"] = [
                {
                    "creator_type": creator,
                    "current_roi": metrics["roi_percentage"],
                    "current_revenue": metrics["revenue"],
                    "expansion_potential": "high"
                }
                for creator, metrics in high_roi_creators
            ]
        
        # Model optimization opportunities
        model_performance = roi_metrics.model_performance
        if model_performance:
            underperforming_models = [
                (model_id, metrics) for model_id, metrics in model_performance.items()
                if metrics["efficiency_score"] < 1.0
            ]
            
            opportunities["model_optimization"] = [
                {
                    "model_id": model_id,
                    "current_efficiency": metrics["efficiency_score"],
                    "cost_per_inference": metrics["cost_per_inference"],
                    "optimization_potential": "medium" if metrics["efficiency_score"] > 0.5 else "high"
                }
                for model_id, metrics in underperforming_models
            ]
        
        # Revenue stream opportunities
        revenue_breakdown = roi_metrics.revenue_breakdown
        if revenue_breakdown:
            # Identify underutilized revenue streams
            total_revenue = sum(revenue_breakdown.values())
            underutilized_streams = [
                stream for stream, amount in revenue_breakdown.items()
                if amount / total_revenue < 0.1  # Less than 10% of total revenue
            ]
            
            opportunities["revenue_diversification"] = underutilized_streams
        
        return opportunities
    
    async def _calculate_competitive_benchmarks(self) -> Dict[str, float]:
        """Calculate competitive benchmarks (simplified)"""
        # In production, would integrate with industry benchmark data
        return {
            "industry_average_roi": 15.0,
            "industry_average_attribution": 35.0,
            "industry_average_cost_efficiency": 2.5,
            "top_quartile_roi": 25.0,
            "median_roi": 12.0
        }
    
    def export_analysis_report(self, analysis: BusinessImpactAnalysis,
                              format: str = "json") -> str:
        """Export analysis report in specified format"""
        
        if format == "json":
            # Convert to JSON-serializable format
            report_data = {
                "analysis_id": analysis.analysis_id,
                "timestamp": analysis.timestamp.isoformat(),
                "time_horizon": analysis.time_horizon.value,
                "roi_metrics": {
                    "period_start": analysis.roi_metrics.period_start.isoformat(),
                    "period_end": analysis.roi_metrics.period_end.isoformat(),
                    "total_revenue": analysis.roi_metrics.total_revenue,
                    "total_costs": analysis.roi_metrics.total_costs,
                    "net_profit": analysis.roi_metrics.net_profit,
                    "roi_percentage": analysis.roi_metrics.roi_percentage,
                    "revenue_attribution": analysis.roi_metrics.revenue_attribution,
                    "cost_breakdown": analysis.roi_metrics.cost_breakdown,
                    "revenue_breakdown": analysis.roi_metrics.revenue_breakdown,
                    "creator_breakdown": analysis.roi_metrics.creator_breakdown,
                    "model_performance": analysis.roi_metrics.model_performance,
                    "efficiency_metrics": analysis.roi_metrics.efficiency_metrics
                },
                "trend_analysis": analysis.trend_analysis,
                "predictive_insights": analysis.predictive_insights,
                "recommendations": analysis.recommendations,
                "risk_assessment": analysis.risk_assessment,
                "opportunity_analysis": analysis.opportunity_analysis,
                "competitive_benchmarks": analysis.competitive_benchmarks
            }
            
            return json.dumps(report_data, indent=2)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")

# Example usage and testing
if __name__ == "__main__":
    async def test_roi_calculator():
        """Test ROI calculator"""
        
        # Initialize ROI analyzer
        analyzer = ROIAnalyzer()
        
        # Add sample cost data
        print("💰 Adding sample cost data...")
        
        base_date = datetime.now() - timedelta(days=30)
        
        # Infrastructure costs
        for i in range(10):
            cost = CostItem(
                cost_id=f"infra_cost_{i}",
                category=CostCategory.INFRASTRUCTURE,
                amount=np.random.uniform(500, 2000),
                timestamp=base_date + timedelta(days=i*3),
                model_id=f"model_{i%3}",
                creator_type=CreatorType.MUSICIAN if i%2 == 0 else CreatorType.PHOTOGRAPHER
            )
            analyzer.cost_tracker.add_cost(cost)
        
        # Development costs
        for i in range(5):
            cost = CostItem(
                cost_id=f"dev_cost_{i}",
                category=CostCategory.DEVELOPMENT,
                amount=np.random.uniform(2000, 5000),
                timestamp=base_date + timedelta(days=i*6),
                model_id=f"model_{i%3}"
            )
            analyzer.cost_tracker.add_cost(cost)
        
        print("💰 Adding sample revenue data...")
        
        # Add sample revenue data
        for i in range(20):
            revenue = RevenueItem(
                revenue_id=f"revenue_{i}",
                stream=RevenueStream.CONTENT_MONETIZATION if i%3 == 0 else RevenueStream.PLATFORM_FEES,
                amount=np.random.uniform(1000, 8000),
                timestamp=base_date + timedelta(days=i*1.5),
                model_attribution=np.random.uniform(20, 80),
                creator_type=CreatorType.MUSICIAN if i%2 == 0 else CreatorType.PHOTOGRAPHER,
                model_id=f"model_{i%3}",
                creator_id=f"creator_{i%5}"
            )
            analyzer.revenue_tracker.add_revenue(revenue)
        
        # Calculate ROI for the past 30 days
        print("📊 Calculating ROI metrics...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        roi_metrics = await analyzer.calculate_roi(start_date, end_date)
        
        print(f"\n💰 ROI Analysis Results:")
        print(f"   Period: {roi_metrics.period_start.strftime('%Y-%m-%d')} to {roi_metrics.period_end.strftime('%Y-%m-%d')}")
        print(f"   Total Revenue: ${roi_metrics.total_revenue:,.2f}")
        print(f"   Total Costs: ${roi_metrics.total_costs:,.2f}")
        print(f"   Net Profit: ${roi_metrics.net_profit:,.2f}")
        print(f"   ROI Percentage: {roi_metrics.roi_percentage:.2f}%")
        print(f"   ML Attribution: ${roi_metrics.revenue_attribution:,.2f} ({roi_metrics.revenue_attribution/roi_metrics.total_revenue*100:.1f}%)")
        
        print(f"\n💼 Cost Breakdown:")
        for category, amount in roi_metrics.cost_breakdown.items():
            print(f"   {category}: ${amount:,.2f}")
        
        print(f"\n💰 Revenue Breakdown:")
        for stream, amount in roi_metrics.revenue_breakdown.items():
            print(f"   {stream}: ${amount:,.2f}")
        
        print(f"\n🎨 Creator Breakdown:")
        for creator, metrics in roi_metrics.creator_breakdown.items():
            if metrics["revenue"] > 0:
                print(f"   {creator}:")
                print(f"      Revenue: ${metrics['revenue']:,.2f}")
                print(f"      ROI: {metrics['roi_percentage']:.1f}%")
                print(f"      ML Attribution: {metrics['attribution_percentage']:.1f}%")
        
        print(f"\n📈 Efficiency Metrics:")
        for metric, value in roi_metrics.efficiency_metrics.items():
            print(f"   {metric}: {value:.2f}")
        
        # Comprehensive business impact analysis
        print(f"\n🔍 Running comprehensive business impact analysis...")
        
        business_analysis = await analyzer.analyze_business_impact(TimeHorizon.MONTHLY)
        
        print(f"\n🎯 Business Impact Analysis:")
        print(f"   Analysis ID: {business_analysis.analysis_id}")
        print(f"   Time Horizon: {business_analysis.time_horizon.value}")
        
        if business_analysis.predictive_insights.get("insufficient_data"):
            print(f"   Predictive Insights: Insufficient data for predictions")
        else:
            insights = business_analysis.predictive_insights
            print(f"   Predicted Next ROI: {insights.get('predicted_next_roi', 0):.2f}%")
            print(f"   ROI Trend: {insights.get('roi_trend_direction', 'unknown')}")
            print(f"   Risk Level: {insights.get('risk_level', 'unknown')}")
        
        print(f"\n📋 Recommendations:")
        for rec in business_analysis.recommendations[:5]:  # Show top 5
            print(f"   • {rec}")
        
        print(f"\n⚠️ Risk Assessment:")
        for risk, level in business_analysis.risk_assessment.items():
            print(f"   {risk}: {level:.2f}")
        
        print(f"\n🚀 Growth Opportunities:")
        opportunities = business_analysis.opportunity_analysis
        if "creator_expansion" in opportunities:
            print(f"   Creator Expansion: {len(opportunities['creator_expansion'])} opportunities")
        if "model_optimization" in opportunities:
            print(f"   Model Optimization: {len(opportunities['model_optimization'])} opportunities")
        
        # Export analysis report
        print(f"\n📄 Exporting analysis report...")
        report_json = analyzer.export_analysis_report(business_analysis, "json")
        
        # Save to file
        report_path = "/tmp/roi_analysis_report.json"
        with open(report_path, 'w') as f:
            f.write(report_json)
        
        print(f"   Report exported to: {report_path}")
        print(f"   Report size: {len(report_json):,} characters")
        
        print(f"\n✅ ROI calculator test completed")
    
    # Run test
    asyncio.run(test_roi_calculator())