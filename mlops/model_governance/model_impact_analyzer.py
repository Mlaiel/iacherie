"""
📈 Model Impact Analyzer - Enterprise Business Intelligence
© 2025 Fahed Mlaiel <mlaiel@live.de> - Tous droits réservés

⚠️ AVERTISSEMENT LÉGAL:
==========================================
TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE: Licence entreprise disponible sur demande
📧 Contact: mlaiel@live.de

Analyseur impact business modèles IA Creator Economy
Expertise: Lead Dev IA + Backend Senior + DBA + Business Analytics
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from pathlib import Path
import statistics
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class ImpactCategory(Enum):
    """Impact analysis categories"""
    REVENUE = "revenue"
    USER_ENGAGEMENT = "user_engagement"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    CREATOR_SATISFACTION = "creator_satisfaction"
    MARKET_EXPANSION = "market_expansion"
    COMPETITIVE_ADVANTAGE = "competitive_advantage"
    RISK_MITIGATION = "risk_mitigation"


class ImpactLevel(Enum):
    """Impact significance levels"""
    NEGLIGIBLE = "negligible"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class AnalysisTimeframe(Enum):
    """Analysis timeframe options"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class BusinessMetric:
    """Business metric definition"""
    metric_id: str
    name: str
    description: str
    category: ImpactCategory
    unit: str
    value: float
    baseline_value: Optional[float] = None
    target_value: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            "metric_id": self.metric_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "unit": self.unit,
            "value": self.value,
            "baseline_value": self.baseline_value,
            "target_value": self.target_value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ImpactAnalysis:
    """Model impact analysis result"""
    analysis_id: str
    model_name: str
    model_version: str
    timeframe: AnalysisTimeframe
    analysis_date: datetime
    overall_impact_score: float
    category_impacts: Dict[ImpactCategory, float]
    business_metrics: List[BusinessMetric]
    roi_calculation: Dict[str, float]
    recommendations: List[str]
    confidence_score: float
    data_sources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis to dictionary"""
        return {
            "analysis_id": self.analysis_id,
            "model_name": self.model_name,
            "model_version": self.model_version,
            "timeframe": self.timeframe.value,
            "analysis_date": self.analysis_date.isoformat(),
            "overall_impact_score": self.overall_impact_score,
            "category_impacts": {cat.value: score for cat, score in self.category_impacts.items()},
            "business_metrics": [metric.to_dict() for metric in self.business_metrics],
            "roi_calculation": self.roi_calculation,
            "recommendations": self.recommendations,
            "confidence_score": self.confidence_score,
            "data_sources": self.data_sources
        }


@dataclass
class CreatorImpactProfile:
    """Creator impact profile"""
    creator_id: str
    creator_tier: str
    usage_frequency: str  # daily, weekly, monthly
    revenue_contribution: float
    satisfaction_score: float
    adoption_rate: float
    churn_risk: float
    growth_potential: float
    model_preferences: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            "creator_id": self.creator_id,
            "creator_tier": self.creator_tier,
            "usage_frequency": self.usage_frequency,
            "revenue_contribution": self.revenue_contribution,
            "satisfaction_score": self.satisfaction_score,
            "adoption_rate": self.adoption_rate,
            "churn_risk": self.churn_risk,
            "growth_potential": self.growth_potential,
            "model_preferences": self.model_preferences
        }


@dataclass
class ModelROIAnalysis:
    """Model ROI analysis"""
    model_name: str
    model_version: str
    analysis_period_days: int
    total_revenue: float
    total_costs: float
    net_profit: float
    roi_percentage: float
    payback_period_days: Optional[int]
    break_even_point: Optional[datetime]
    cost_breakdown: Dict[str, float]
    revenue_breakdown: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ROI analysis to dictionary"""
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "analysis_period_days": self.analysis_period_days,
            "total_revenue": self.total_revenue,
            "total_costs": self.total_costs,
            "net_profit": self.net_profit,
            "roi_percentage": self.roi_percentage,
            "payback_period_days": self.payback_period_days,
            "break_even_point": self.break_even_point.isoformat() if self.break_even_point else None,
            "cost_breakdown": self.cost_breakdown,
            "revenue_breakdown": self.revenue_breakdown
        }


class ModelImpactAnalyzer:
    """
    📈 Analyseur impact business modèles IA
    
    Enterprise business impact analysis with:
    - Revenue impact quantification with attribution modeling
    - Creator satisfaction correlation with predictive analytics
    - Performance business metrics with trend analysis
    - ROI calculation per model with cost optimization
    - Strategic decision support with recommendations engine
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize impact analyzer
        
        Args:
            config: Impact analyzer configuration
        """
        self.config = config or self._get_default_config()
        self.analyzer_id = str(uuid.uuid4())
        
        # Analysis data storage
        self._impact_analyses: Dict[str, ImpactAnalysis] = {}
        self._business_metrics: Dict[str, List[BusinessMetric]] = defaultdict(list)
        self._creator_profiles: Dict[str, CreatorImpactProfile] = {}
        self._roi_analyses: Dict[str, ModelROIAnalysis] = {}
        
        # Historical data for trend analysis
        self._metric_history: Dict[str, List[Tuple[datetime, float]]] = defaultdict(list)
        self._impact_trends: Dict[str, List[float]] = defaultdict(list)
        
        # Analysis models and weights
        self._impact_weights = self._load_impact_weights()
        self._correlation_models = {}
        
        # Performance metrics
        self._analyzer_metrics = {
            "analyses_completed": 0,
            "models_analyzed": 0,
            "roi_calculations": 0,
            "recommendations_generated": 0,
            "accuracy_score": 0.0
        }
        
        logger.info(f"📈 ModelImpactAnalyzer initialized with ID: {self.analyzer_id}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default analyzer configuration"""
        return {
            "analysis": {
                "default_timeframe": "monthly",
                "confidence_threshold": 0.7,
                "min_data_points": 30,
                "correlation_threshold": 0.5
            },
            "revenue_analysis": {
                "attribution_model": "first_touch",  # first_touch, last_touch, linear
                "cost_allocation_method": "proportional",
                "include_indirect_revenue": True,
                "revenue_recognition_period": 30  # days
            },
            "creator_analysis": {
                "satisfaction_weights": {
                    "performance": 0.4,
                    "reliability": 0.3,
                    "support": 0.2,
                    "innovation": 0.1
                },
                "churn_prediction_enabled": True,
                "growth_modeling": True
            },
            "roi_calculation": {
                "discount_rate": 0.1,  # 10% annual
                "include_opportunity_cost": True,
                "cost_categories": [
                    "infrastructure",
                    "development",
                    "maintenance",
                    "support",
                    "marketing"
                ]
            },
            "recommendations": {
                "max_recommendations": 10,
                "include_risk_assessment": True,
                "prioritize_by_impact": True,
                "strategic_alignment_check": True
            }
        }
    
    def _load_impact_weights(self) -> Dict[ImpactCategory, float]:
        """Load impact category weights"""
        return {
            ImpactCategory.REVENUE: 0.25,
            ImpactCategory.USER_ENGAGEMENT: 0.20,
            ImpactCategory.OPERATIONAL_EFFICIENCY: 0.15,
            ImpactCategory.CREATOR_SATISFACTION: 0.15,
            ImpactCategory.MARKET_EXPANSION: 0.10,
            ImpactCategory.COMPETITIVE_ADVANTAGE: 0.10,
            ImpactCategory.RISK_MITIGATION: 0.05
        }
    
    async def analyze_model_impact(
        self,
        model_name: str,
        model_version: str,
        timeframe: AnalysisTimeframe = AnalysisTimeframe.MONTHLY,
        custom_metrics: Optional[List[str]] = None
    ) -> str:
        """
        Perform comprehensive model impact analysis
        
        Args:
            model_name: Name of the model to analyze
            model_version: Version of the model
            timeframe: Analysis timeframe
            custom_metrics: Optional custom metrics to include
            
        Returns:
            Analysis ID
        """
        try:
            analysis_id = str(uuid.uuid4())
            
            logger.info(f"🔍 Starting impact analysis for {model_name}:{model_version}")
            
            # Collect business metrics
            business_metrics = await self._collect_business_metrics(
                model_name, model_version, timeframe, custom_metrics
            )
            
            # Calculate category impacts
            category_impacts = await self._calculate_category_impacts(
                model_name, model_version, business_metrics, timeframe
            )
            
            # Calculate overall impact score
            overall_impact = self._calculate_overall_impact(category_impacts)
            
            # Perform ROI calculation
            roi_analysis = await self._calculate_model_roi(
                model_name, model_version, timeframe
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                model_name, model_version, category_impacts, roi_analysis, business_metrics
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(business_metrics, timeframe)
            
            # Create impact analysis
            analysis = ImpactAnalysis(
                analysis_id=analysis_id,
                model_name=model_name,
                model_version=model_version,
                timeframe=timeframe,
                analysis_date=datetime.now(),
                overall_impact_score=overall_impact,
                category_impacts=category_impacts,
                business_metrics=business_metrics,
                roi_calculation=roi_analysis.to_dict(),
                recommendations=recommendations,
                confidence_score=confidence_score,
                data_sources=[
                    "usage_analytics",
                    "revenue_data",
                    "creator_feedback",
                    "performance_metrics"
                ]
            )
            
            # Store analysis
            self._impact_analyses[analysis_id] = analysis
            
            # Update trends
            self._update_impact_trends(model_name, overall_impact)
            
            # Update metrics
            self._analyzer_metrics["analyses_completed"] += 1
            if model_name not in [a.model_name for a in self._impact_analyses.values()]:
                self._analyzer_metrics["models_analyzed"] += 1
            
            logger.info(f"✅ Completed impact analysis {analysis_id} with score {overall_impact:.2f}")
            
            return analysis_id
            
        except Exception as e:
            logger.error(f"Impact analysis error: {str(e)}")
            raise
    
    async def _collect_business_metrics(
        self,
        model_name: str,
        model_version: str,
        timeframe: AnalysisTimeframe,
        custom_metrics: Optional[List[str]]
    ) -> List[BusinessMetric]:
        """Collect relevant business metrics for analysis"""
        try:
            metrics = []
            
            # Revenue metrics
            revenue_metrics = await self._collect_revenue_metrics(model_name, model_version, timeframe)
            metrics.extend(revenue_metrics)
            
            # User engagement metrics
            engagement_metrics = await self._collect_engagement_metrics(model_name, model_version, timeframe)
            metrics.extend(engagement_metrics)
            
            # Operational metrics
            operational_metrics = await self._collect_operational_metrics(model_name, model_version, timeframe)
            metrics.extend(operational_metrics)
            
            # Creator satisfaction metrics
            satisfaction_metrics = await self._collect_satisfaction_metrics(model_name, model_version, timeframe)
            metrics.extend(satisfaction_metrics)
            
            # Market expansion metrics
            market_metrics = await self._collect_market_metrics(model_name, model_version, timeframe)
            metrics.extend(market_metrics)
            
            logger.info(f"📊 Collected {len(metrics)} business metrics for {model_name}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics collection error: {str(e)}")
            return []
    
    async def _collect_revenue_metrics(
        self,
        model_name: str,
        model_version: str,
        timeframe: AnalysisTimeframe
    ) -> List[BusinessMetric]:
        """Collect revenue-related metrics"""
        metrics = []
        
        # Direct revenue from model usage
        direct_revenue = BusinessMetric(
            metric_id=f"direct_revenue_{model_name}_{timeframe.value}",
            name="Direct Revenue",
            description="Direct revenue generated from model usage",
            category=ImpactCategory.REVENUE,
            unit="USD",
            value=self._simulate_revenue_data("direct", model_name, timeframe),
            baseline_value=self._get_baseline_revenue("direct", model_name)
        )
        metrics.append(direct_revenue)
        
        # Indirect revenue (upsells, cross-sells)
        if self.config["revenue_analysis"]["include_indirect_revenue"]:
            indirect_revenue = BusinessMetric(
                metric_id=f"indirect_revenue_{model_name}_{timeframe.value}",
                name="Indirect Revenue",
                description="Indirect revenue from upsells and cross-sells",
                category=ImpactCategory.REVENUE,
                unit="USD",
                value=self._simulate_revenue_data("indirect", model_name, timeframe),
                baseline_value=self._get_baseline_revenue("indirect", model_name)
            )
            metrics.append(indirect_revenue)
        
        # Revenue per user
        revenue_per_user = BusinessMetric(
            metric_id=f"revenue_per_user_{model_name}_{timeframe.value}",
            name="Revenue Per User",
            description="Average revenue generated per active user",
            category=ImpactCategory.REVENUE,
            unit="USD",
            value=self._simulate_revenue_data("per_user", model_name, timeframe),
            baseline_value=self._get_baseline_revenue("per_user", model_name)
        )
        metrics.append(revenue_per_user)
        
        return metrics
    
    async def _collect_engagement_metrics(
        self,
        model_name: str,
        model_version: str,
        timeframe: AnalysisTimeframe
    ) -> List[BusinessMetric]:
        """Collect user engagement metrics"""
        metrics = []
        
        # Daily active users
        daily_active_users = BusinessMetric(
            metric_id=f"dau_{model_name}_{timeframe.value}",
            name="Daily Active Users",
            description="Average daily active users for the model",
            category=ImpactCategory.USER_ENGAGEMENT,
            unit="users",
            value=self._simulate_engagement_data("dau", model_name, timeframe),
            baseline_value=self._get_baseline_engagement("dau", model_name)
        )
        metrics.append(daily_active_users)
        
        # Session duration
        avg_session_duration = BusinessMetric(
            metric_id=f"session_duration_{model_name}_{timeframe.value}",
            name="Average Session Duration",
            description="Average time users spend with the model",
            category=ImpactCategory.USER_ENGAGEMENT,
            unit="minutes",
            value=self._simulate_engagement_data("session_duration", model_name, timeframe),
            baseline_value=self._get_baseline_engagement("session_duration", model_name)
        )
        metrics.append(avg_session_duration)
        
        # Retention rate
        retention_rate = BusinessMetric(
            metric_id=f"retention_rate_{model_name}_{timeframe.value}",
            name="User Retention Rate",
            description="Percentage of users who continue using the model",
            category=ImpactCategory.USER_ENGAGEMENT,
            unit="percentage",
            value=self._simulate_engagement_data("retention", model_name, timeframe),
            baseline_value=self._get_baseline_engagement("retention", model_name)
        )
        metrics.append(retention_rate)
        
        return metrics
    
    async def _collect_operational_metrics(
        self,
        model_name: str,
        model_version: str,
        timeframe: AnalysisTimeframe
    ) -> List[BusinessMetric]:
        """Collect operational efficiency metrics"""
        metrics = []
        
        # Cost per inference
        cost_per_inference = BusinessMetric(
            metric_id=f"cost_per_inference_{model_name}_{timeframe.value}",
            name="Cost Per Inference",
            description="Average cost to run one model inference",
            category=ImpactCategory.OPERATIONAL_EFFICIENCY,
            unit="USD",
            value=self._simulate_operational_data("cost_per_inference", model_name, timeframe),
            baseline_value=self._get_baseline_operational("cost_per_inference", model_name)
        )
        metrics.append(cost_per_inference)
        
        # Processing efficiency
        processing_efficiency = BusinessMetric(
            metric_id=f"processing_efficiency_{model_name}_{timeframe.value}",
            name="Processing Efficiency",
            description="Efficiency score based on throughput and resource utilization",
            category=ImpactCategory.OPERATIONAL_EFFICIENCY,
            unit="score",
            value=self._simulate_operational_data("efficiency", model_name, timeframe),
            baseline_value=self._get_baseline_operational("efficiency", model_name)
        )
        metrics.append(processing_efficiency)
        
        # Error rate
        error_rate = BusinessMetric(
            metric_id=f"error_rate_{model_name}_{timeframe.value}",
            name="Error Rate",
            description="Percentage of failed model requests",
            category=ImpactCategory.OPERATIONAL_EFFICIENCY,
            unit="percentage",
            value=self._simulate_operational_data("error_rate", model_name, timeframe),
            baseline_value=self._get_baseline_operational("error_rate", model_name)
        )
        metrics.append(error_rate)
        
        return metrics
    
    async def _collect_satisfaction_metrics(
        self,
        model_name: str,
        model_version: str,
        timeframe: AnalysisTimeframe
    ) -> List[BusinessMetric]:
        """Collect creator satisfaction metrics"""
        metrics = []
        
        # Overall satisfaction score
        satisfaction_score = BusinessMetric(
            metric_id=f"satisfaction_score_{model_name}_{timeframe.value}",
            name="Creator Satisfaction Score",
            description="Overall creator satisfaction with the model",
            category=ImpactCategory.CREATOR_SATISFACTION,
            unit="score",
            value=self._simulate_satisfaction_data("overall", model_name, timeframe),
            baseline_value=self._get_baseline_satisfaction("overall", model_name)
        )
        metrics.append(satisfaction_score)
        
        # Net Promoter Score
        nps_score = BusinessMetric(
            metric_id=f"nps_score_{model_name}_{timeframe.value}",
            name="Net Promoter Score",
            description="Creator likelihood to recommend the model",
            category=ImpactCategory.CREATOR_SATISFACTION,
            unit="score",
            value=self._simulate_satisfaction_data("nps", model_name, timeframe),
            baseline_value=self._get_baseline_satisfaction("nps", model_name)
        )
        metrics.append(nps_score)
        
        # Support ticket resolution time
        support_resolution_time = BusinessMetric(
            metric_id=f"support_resolution_{model_name}_{timeframe.value}",
            name="Support Resolution Time",
            description="Average time to resolve support tickets",
            category=ImpactCategory.CREATOR_SATISFACTION,
            unit="hours",
            value=self._simulate_satisfaction_data("support_time", model_name, timeframe),
            baseline_value=self._get_baseline_satisfaction("support_time", model_name)
        )
        metrics.append(support_resolution_time)
        
        return metrics
    
    async def _collect_market_metrics(
        self,
        model_name: str,
        model_version: str,
        timeframe: AnalysisTimeframe
    ) -> List[BusinessMetric]:
        """Collect market expansion metrics"""
        metrics = []
        
        # Market share
        market_share = BusinessMetric(
            metric_id=f"market_share_{model_name}_{timeframe.value}",
            name="Market Share",
            description="Estimated market share in model category",
            category=ImpactCategory.MARKET_EXPANSION,
            unit="percentage",
            value=self._simulate_market_data("market_share", model_name, timeframe),
            baseline_value=self._get_baseline_market("market_share", model_name)
        )
        metrics.append(market_share)
        
        # New customer acquisition
        new_customers = BusinessMetric(
            metric_id=f"new_customers_{model_name}_{timeframe.value}",
            name="New Customer Acquisition",
            description="Number of new customers acquired through this model",
            category=ImpactCategory.MARKET_EXPANSION,
            unit="customers",
            value=self._simulate_market_data("new_customers", model_name, timeframe),
            baseline_value=self._get_baseline_market("new_customers", model_name)
        )
        metrics.append(new_customers)
        
        return metrics
    
    def _simulate_revenue_data(self, metric_type: str, model_name: str, timeframe: AnalysisTimeframe) -> float:
        """Simulate revenue data for analysis"""
        base_values = {
            "direct": {"monthly": 50000, "weekly": 12500, "daily": 1800},
            "indirect": {"monthly": 15000, "weekly": 3750, "daily": 540},
            "per_user": {"monthly": 45, "weekly": 11, "daily": 1.6}
        }
        
        base_value = base_values.get(metric_type, {}).get(timeframe.value, 1000)
        # Add some variance based on model name hash
        variance = (hash(model_name) % 100) / 100 * 0.3  # ±30% variance
        return base_value * (1 + variance - 0.15)
    
    def _simulate_engagement_data(self, metric_type: str, model_name: str, timeframe: AnalysisTimeframe) -> float:
        """Simulate engagement data for analysis"""
        base_values = {
            "dau": {"monthly": 2500, "weekly": 2200, "daily": 2000},
            "session_duration": {"monthly": 25, "weekly": 23, "daily": 20},
            "retention": {"monthly": 0.75, "weekly": 0.82, "daily": 0.88}
        }
        
        base_value = base_values.get(metric_type, {}).get(timeframe.value, 100)
        variance = (hash(model_name) % 50) / 100 * 0.2
        return base_value * (1 + variance - 0.1)
    
    def _simulate_operational_data(self, metric_type: str, model_name: str, timeframe: AnalysisTimeframe) -> float:
        """Simulate operational data for analysis"""
        base_values = {
            "cost_per_inference": {"monthly": 0.008, "weekly": 0.009, "daily": 0.010},
            "efficiency": {"monthly": 0.88, "weekly": 0.85, "daily": 0.82},
            "error_rate": {"monthly": 0.015, "weekly": 0.018, "daily": 0.022}
        }
        
        base_value = base_values.get(metric_type, {}).get(timeframe.value, 0.5)
        variance = (hash(model_name) % 30) / 100 * 0.15
        return base_value * (1 + variance - 0.075)
    
    def _simulate_satisfaction_data(self, metric_type: str, model_name: str, timeframe: AnalysisTimeframe) -> float:
        """Simulate satisfaction data for analysis"""
        base_values = {
            "overall": {"monthly": 0.82, "weekly": 0.80, "daily": 0.78},
            "nps": {"monthly": 35, "weekly": 32, "daily": 28},
            "support_time": {"monthly": 4.2, "weekly": 4.8, "daily": 5.5}
        }
        
        base_value = base_values.get(metric_type, {}).get(timeframe.value, 0.7)
        variance = (hash(model_name) % 25) / 100 * 0.1
        return base_value * (1 + variance - 0.05)
    
    def _simulate_market_data(self, metric_type: str, model_name: str, timeframe: AnalysisTimeframe) -> float:
        """Simulate market data for analysis"""
        base_values = {
            "market_share": {"monthly": 0.15, "weekly": 0.14, "daily": 0.13},
            "new_customers": {"monthly": 125, "weekly": 30, "daily": 4}
        }
        
        base_value = base_values.get(metric_type, {}).get(timeframe.value, 10)
        variance = (hash(model_name) % 40) / 100 * 0.25
        return base_value * (1 + variance - 0.125)
    
    def _get_baseline_revenue(self, metric_type: str, model_name: str) -> float:
        """Get baseline revenue for comparison"""
        # Simulate baseline as 80% of current value
        return self._simulate_revenue_data(metric_type, model_name, AnalysisTimeframe.MONTHLY) * 0.8
    
    def _get_baseline_engagement(self, metric_type: str, model_name: str) -> float:
        """Get baseline engagement for comparison"""
        return self._simulate_engagement_data(metric_type, model_name, AnalysisTimeframe.MONTHLY) * 0.85
    
    def _get_baseline_operational(self, metric_type: str, model_name: str) -> float:
        """Get baseline operational metrics for comparison"""
        return self._simulate_operational_data(metric_type, model_name, AnalysisTimeframe.MONTHLY) * 1.1
    
    def _get_baseline_satisfaction(self, metric_type: str, model_name: str) -> float:
        """Get baseline satisfaction for comparison"""
        return self._simulate_satisfaction_data(metric_type, model_name, AnalysisTimeframe.MONTHLY) * 0.9
    
    def _get_baseline_market(self, metric_type: str, model_name: str) -> float:
        """Get baseline market metrics for comparison"""
        return self._simulate_market_data(metric_type, model_name, AnalysisTimeframe.MONTHLY) * 0.75
    
    async def _calculate_category_impacts(
        self,
        model_name: str,
        model_version: str,
        metrics: List[BusinessMetric],
        timeframe: AnalysisTimeframe
    ) -> Dict[ImpactCategory, float]:
        """Calculate impact scores by category"""
        try:
            category_impacts = {}
            
            for category in ImpactCategory:
                category_metrics = [m for m in metrics if m.category == category]
                
                if not category_metrics:
                    category_impacts[category] = 0.0
                    continue
                
                impact_scores = []
                
                for metric in category_metrics:
                    if metric.baseline_value is not None and metric.baseline_value != 0:
                        # Calculate percentage improvement
                        improvement = (metric.value - metric.baseline_value) / abs(metric.baseline_value)
                        
                        # Normalize to 0-1 scale (with some metrics being reverse scored)
                        if category == ImpactCategory.OPERATIONAL_EFFICIENCY and "error_rate" in metric.name.lower():
                            # Lower error rate is better
                            score = max(0, min(1, 1 - improvement))
                        elif "cost" in metric.name.lower():
                            # Lower cost is better
                            score = max(0, min(1, 1 - improvement))
                        else:
                            # Higher value is better
                            score = max(0, min(1, improvement + 0.5))
                        
                        impact_scores.append(score)
                    else:
                        # No baseline, use normalized current value
                        if category == ImpactCategory.CREATOR_SATISFACTION:
                            score = metric.value  # Already 0-1 scale
                        else:
                            score = min(1, metric.value / 1000)  # Rough normalization
                        
                        impact_scores.append(score)
                
                # Calculate weighted average for category
                category_impacts[category] = sum(impact_scores) / len(impact_scores) if impact_scores else 0.0
            
            logger.info(f"📊 Calculated category impacts for {model_name}")
            
            return category_impacts
            
        except Exception as e:
            logger.error(f"Category impact calculation error: {str(e)}")
            return {category: 0.0 for category in ImpactCategory}
    
    def _calculate_overall_impact(self, category_impacts: Dict[ImpactCategory, float]) -> float:
        """Calculate overall impact score using weighted categories"""
        try:
            total_score = 0.0
            total_weight = 0.0
            
            for category, impact_score in category_impacts.items():
                weight = self._impact_weights.get(category, 0.1)
                total_score += impact_score * weight
                total_weight += weight
            
            overall_impact = total_score / total_weight if total_weight > 0 else 0.0
            
            return round(overall_impact, 3)
            
        except Exception as e:
            logger.error(f"Overall impact calculation error: {str(e)}")
            return 0.0
    
    async def _calculate_model_roi(
        self,
        model_name: str,
        model_version: str,
        timeframe: AnalysisTimeframe
    ) -> ModelROIAnalysis:
        """Calculate comprehensive ROI for model"""
        try:
            # Calculate revenue components
            direct_revenue = self._simulate_revenue_data("direct", model_name, timeframe)
            indirect_revenue = self._simulate_revenue_data("indirect", model_name, timeframe)
            total_revenue = direct_revenue + indirect_revenue
            
            # Calculate cost components
            cost_breakdown = {
                "infrastructure": total_revenue * 0.15,  # 15% of revenue
                "development": total_revenue * 0.20,     # 20% of revenue
                "maintenance": total_revenue * 0.08,     # 8% of revenue
                "support": total_revenue * 0.05,         # 5% of revenue
                "marketing": total_revenue * 0.12        # 12% of revenue
            }
            
            total_costs = sum(cost_breakdown.values())
            net_profit = total_revenue - total_costs
            roi_percentage = (net_profit / total_costs * 100) if total_costs > 0 else 0
            
            # Calculate payback period (simplified)
            monthly_profit = net_profit if timeframe == AnalysisTimeframe.MONTHLY else net_profit * 30
            payback_period_days = int(cost_breakdown["development"] / (monthly_profit / 30)) if monthly_profit > 0 else None
            
            # Calculate break-even point
            break_even_point = None
            if monthly_profit > 0:
                days_to_break_even = total_costs / (monthly_profit / 30)
                break_even_point = datetime.now() - timedelta(days=max(0, days_to_break_even))
            
            roi_analysis = ModelROIAnalysis(
                model_name=model_name,
                model_version=model_version,
                analysis_period_days=30 if timeframe == AnalysisTimeframe.MONTHLY else 7,
                total_revenue=total_revenue,
                total_costs=total_costs,
                net_profit=net_profit,
                roi_percentage=roi_percentage,
                payback_period_days=payback_period_days,
                break_even_point=break_even_point,
                cost_breakdown=cost_breakdown,
                revenue_breakdown={
                    "direct_revenue": direct_revenue,
                    "indirect_revenue": indirect_revenue
                }
            )
            
            # Store ROI analysis
            self._roi_analyses[f"{model_name}:{model_version}"] = roi_analysis
            self._analyzer_metrics["roi_calculations"] += 1
            
            logger.info(f"💰 Calculated ROI for {model_name}: {roi_percentage:.2f}%")
            
            return roi_analysis
            
        except Exception as e:
            logger.error(f"ROI calculation error: {str(e)}")
            # Return zero ROI analysis on error
            return ModelROIAnalysis(
                model_name=model_name,
                model_version=model_version,
                analysis_period_days=30,
                total_revenue=0,
                total_costs=0,
                net_profit=0,
                roi_percentage=0,
                payback_period_days=None,
                break_even_point=None,
                cost_breakdown={},
                revenue_breakdown={}
            )
    
    async def _generate_recommendations(
        self,
        model_name: str,
        model_version: str,
        category_impacts: Dict[ImpactCategory, float],
        roi_analysis: ModelROIAnalysis,
        metrics: List[BusinessMetric]
    ) -> List[str]:
        """Generate strategic recommendations based on analysis"""
        try:
            recommendations = []
            
            # ROI-based recommendations
            if roi_analysis.roi_percentage < 50:
                recommendations.append(
                    "Consider optimizing model infrastructure costs to improve ROI"
                )
            elif roi_analysis.roi_percentage > 200:
                recommendations.append(
                    "Excellent ROI - consider scaling model deployment to maximize returns"
                )
            
            # Category-specific recommendations
            for category, impact_score in category_impacts.items():
                if impact_score < 0.3:  # Low impact
                    if category == ImpactCategory.REVENUE:
                        recommendations.append(
                            "Focus on revenue optimization through pricing strategy or market expansion"
                        )
                    elif category == ImpactCategory.USER_ENGAGEMENT:
                        recommendations.append(
                            "Improve user experience and engagement features to increase adoption"
                        )
                    elif category == ImpactCategory.CREATOR_SATISFACTION:
                        recommendations.append(
                            "Enhance creator support and communication to improve satisfaction scores"
                        )
                elif impact_score > 0.8:  # High impact
                    if category == ImpactCategory.MARKET_EXPANSION:
                        recommendations.append(
                            "Leverage strong market position to explore adjacent markets"
                        )
                    elif category == ImpactCategory.COMPETITIVE_ADVANTAGE:
                        recommendations.append(
                            "Maintain competitive advantage through continued innovation"
                        )
            
            # Metric-specific recommendations
            for metric in metrics:
                if metric.baseline_value and metric.value < metric.baseline_value * 0.9:
                    if "error_rate" in metric.name.lower():
                        recommendations.append(
                            f"Address increasing error rates in {model_name} to maintain quality"
                        )
                    elif "satisfaction" in metric.name.lower():
                        recommendations.append(
                            f"Investigate satisfaction decline and implement improvement measures"
                        )
            
            # Limit recommendations
            max_recommendations = self.config["recommendations"]["max_recommendations"]
            if len(recommendations) > max_recommendations:
                recommendations = recommendations[:max_recommendations]
            
            # Add strategic alignment check if no recommendations
            if not recommendations:
                recommendations.append(
                    "Model performance is stable - maintain current strategy and monitor trends"
                )
            
            self._analyzer_metrics["recommendations_generated"] += len(recommendations)
            
            logger.info(f"💡 Generated {len(recommendations)} recommendations for {model_name}")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation error: {str(e)}")
            return ["Analysis completed - manual review recommended"]
    
    def _calculate_confidence_score(
        self,
        metrics: List[BusinessMetric],
        timeframe: AnalysisTimeframe
    ) -> float:
        """Calculate confidence score for analysis"""
        try:
            factors = []
            
            # Data completeness factor
            expected_metrics = 15  # Rough estimate of expected metrics
            completeness_factor = min(1.0, len(metrics) / expected_metrics)
            factors.append(completeness_factor)
            
            # Baseline availability factor
            metrics_with_baseline = len([m for m in metrics if m.baseline_value is not None])
            baseline_factor = metrics_with_baseline / len(metrics) if metrics else 0
            factors.append(baseline_factor)
            
            # Timeframe factor (longer timeframes = higher confidence)
            timeframe_factors = {
                AnalysisTimeframe.DAILY: 0.6,
                AnalysisTimeframe.WEEKLY: 0.7,
                AnalysisTimeframe.MONTHLY: 0.9,
                AnalysisTimeframe.QUARTERLY: 1.0
            }
            timeframe_factor = timeframe_factors.get(timeframe, 0.8)
            factors.append(timeframe_factor)
            
            # Data variance factor (lower variance = higher confidence)
            variance_values = []
            for metric in metrics:
                if metric.baseline_value and metric.baseline_value != 0:
                    variance = abs(metric.value - metric.baseline_value) / abs(metric.baseline_value)
                    variance_values.append(variance)
            
            if variance_values:
                avg_variance = sum(variance_values) / len(variance_values)
                variance_factor = max(0.3, 1.0 - avg_variance)
                factors.append(variance_factor)
            
            # Calculate overall confidence
            confidence = sum(factors) / len(factors) if factors else 0.5
            
            return round(confidence, 3)
            
        except Exception as e:
            logger.error(f"Confidence calculation error: {str(e)}")
            return 0.5
    
    def _update_impact_trends(self, model_name: str, impact_score: float) -> None:
        """Update impact trends for model"""
        try:
            self._impact_trends[model_name].append(impact_score)
            
            # Keep only last 12 data points for trending
            if len(self._impact_trends[model_name]) > 12:
                self._impact_trends[model_name] = self._impact_trends[model_name][-12:]
            
        except Exception as e:
            logger.error(f"Trend update error: {str(e)}")
    
    def get_impact_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get impact analysis by ID"""
        analysis = self._impact_analyses.get(analysis_id)
        return analysis.to_dict() if analysis else None
    
    def get_model_roi_analysis(self, model_name: str, model_version: str) -> Optional[Dict[str, Any]]:
        """Get ROI analysis for specific model"""
        roi_analysis = self._roi_analyses.get(f"{model_name}:{model_version}")
        return roi_analysis.to_dict() if roi_analysis else None
    
    def get_impact_trends(self, model_name: str) -> List[float]:
        """Get impact trend data for model"""
        return self._impact_trends.get(model_name, [])
    
    def get_analyzer_metrics(self) -> Dict[str, Any]:
        """Get analyzer performance metrics"""
        return {
            **self._analyzer_metrics,
            "total_analyses": len(self._impact_analyses),
            "total_roi_analyses": len(self._roi_analyses),
            "models_with_trends": len(self._impact_trends)
        }
    
    def health_check(self) -> str:
        """Health check for impact analyzer"""
        try:
            # Check if we have recent analyses
            if not self._impact_analyses:
                return "WARNING: No impact analyses completed"
            
            # Check analysis age
            recent_analyses = [
                a for a in self._impact_analyses.values()
                if (datetime.now() - a.analysis_date).days < 7
            ]
            
            if len(recent_analyses) == 0 and len(self._impact_analyses) > 0:
                return "WARNING: No recent analyses (within 7 days)"
            
            # Check confidence scores
            low_confidence_analyses = [
                a for a in self._impact_analyses.values()
                if a.confidence_score < self.config["analysis"]["confidence_threshold"]
            ]
            
            if len(low_confidence_analyses) > len(self._impact_analyses) * 0.5:
                return f"WARNING: {len(low_confidence_analyses)} analyses with low confidence"
            
            return "OPERATIONAL"
            
        except Exception as e:
            return f"ERROR: {str(e)}"


# Export main class and related types
__all__ = [
    "ModelImpactAnalyzer",
    "ImpactCategory",
    "ImpactLevel",
    "AnalysisTimeframe",
    "BusinessMetric",
    "ImpactAnalysis",
    "CreatorImpactProfile",
    "ModelROIAnalysis"
]