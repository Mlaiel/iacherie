"""💰 Cost Optimization Metrics - Financial Efficiency & ROI Analytics System
===========================================================================

Advanced cost optimization and financial efficiency metrics system for the Ainflue platform.
Provides comprehensive cost analysis, ROI optimization, resource utilization tracking,
and intelligent recommendations for cost reduction and efficiency improvements.

Enhanced Features:
- Real-time cost tracking and budget monitoring
- ROI analysis and optimization recommendations
- Resource utilization efficiency measurement
- Automated cost alerts and threshold management
- Cost per creator acquisition and retention analytics
- Infrastructure cost optimization with ML predictions
- Financial forecasting and budget planning tools
- Multi-dimensional cost attribution and analysis

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
import json
from collections import defaultdict, deque
import statistics
import uuid
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading
import math

logger = logging.getLogger(__name__)


class CostCategory(Enum):
    """Categories of costs for optimization analysis."""
    INFRASTRUCTURE = "infrastructure"
    MARKETING = "marketing"
    CONTENT_CREATION = "content_creation"
    CREATOR_PAYMENTS = "creator_payments"
    PLATFORM_FEES = "platform_fees"
    STORAGE = "storage"
    BANDWIDTH = "bandwidth"
    COMPUTING = "computing"
    SUPPORT = "support"
    OPERATIONS = "operations"
    COMPLIANCE = "compliance"
    SECURITY = "security"


class CostType(Enum):
    """Types of costs."""
    FIXED = "fixed"
    VARIABLE = "variable"
    SEMI_VARIABLE = "semi_variable"
    ONE_TIME = "one_time"
    RECURRING = "recurring"


class OptimizationPriority(Enum):
    """Priority levels for cost optimization."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResourceType(Enum):
    """Types of resources for utilization tracking."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    DATABASE = "database"
    CACHE = "cache"
    CDN = "cdn"


@dataclass
class CostRecord:
    """Individual cost record for tracking expenses."""
    cost_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: CostCategory = CostCategory.INFRASTRUCTURE
    cost_type: CostType = CostType.VARIABLE
    description: str = ""
    amount: Decimal = field(default_factory=lambda: Decimal('0.00'))
    currency: str = "USD"
    date: datetime = field(default_factory=datetime.utcnow)
    billing_period: str = "monthly"  # daily, weekly, monthly, quarterly, yearly
    resource_id: Optional[str] = None
    creator_id: Optional[str] = None
    campaign_id: Optional[str] = None
    vendor: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_recurring: bool = True
    optimization_potential: float = 0.0  # 0-100 percentage


@dataclass
class ROIAnalysis:
    """Return on Investment analysis data."""
    analysis_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    investment_category: CostCategory = CostCategory.MARKETING
    investment_amount: Decimal = field(default_factory=lambda: Decimal('0.00'))
    revenue_generated: Decimal = field(default_factory=lambda: Decimal('0.00'))
    roi_percentage: float = 0.0
    payback_period_days: Optional[int] = None
    net_present_value: Decimal = field(default_factory=lambda: Decimal('0.00'))
    analysis_period: timedelta = field(default_factory=lambda: timedelta(days=30))
    confidence_score: float = 0.0  # 0-1
    attribution_model: str = "last_touch"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ResourceUtilization:
    """Resource utilization tracking data."""
    resource_id: str = ""
    resource_type: ResourceType = ResourceType.CPU
    utilization_percentage: float = 0.0  # 0-100
    capacity_total: float = 0.0
    capacity_used: float = 0.0
    cost_per_unit: Decimal = field(default_factory=lambda: Decimal('0.00'))
    efficiency_score: float = 0.0  # 0-100
    waste_percentage: float = 0.0  # 0-100
    optimization_recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CostOptimizationRecommendation:
    """Cost optimization recommendation."""
    recommendation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: CostCategory = CostCategory.INFRASTRUCTURE
    priority: OptimizationPriority = OptimizationPriority.MEDIUM
    title: str = ""
    description: str = ""
    current_cost: Decimal = field(default_factory=lambda: Decimal('0.00'))
    potential_savings: Decimal = field(default_factory=lambda: Decimal('0.00'))
    savings_percentage: float = 0.0
    implementation_cost: Decimal = field(default_factory=lambda: Decimal('0.00'))
    implementation_time: timedelta = field(default_factory=lambda: timedelta(days=7))
    risk_level: str = "low"  # low, medium, high
    impact_level: str = "medium"  # low, medium, high
    specific_actions: List[str] = field(default_factory=list)
    expected_roi: float = 0.0
    confidence: float = 0.0  # 0-1
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


@dataclass
class BudgetAlert:
    """Budget monitoring alert."""
    alert_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: CostCategory = CostCategory.INFRASTRUCTURE
    budget_limit: Decimal = field(default_factory=lambda: Decimal('0.00'))
    current_spend: Decimal = field(default_factory=lambda: Decimal('0.00'))
    utilization_percentage: float = 0.0  # 0-100
    threshold_type: str = "warning"  # info, warning, critical
    forecast_overspend: Decimal = field(default_factory=lambda: Decimal('0.00'))
    days_remaining: int = 0
    burn_rate: Decimal = field(default_factory=lambda: Decimal('0.00'))  # per day
    recommended_actions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CostForecast:
    """Cost forecasting data."""
    forecast_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: CostCategory = CostCategory.INFRASTRUCTURE
    forecast_period: timedelta = field(default_factory=lambda: timedelta(days=30))
    predicted_cost: Decimal = field(default_factory=lambda: Decimal('0.00'))
    confidence_interval: Tuple[Decimal, Decimal] = field(default_factory=lambda: (Decimal('0'), Decimal('0')))
    forecast_accuracy: float = 0.0  # 0-100
    trend_direction: str = "stable"  # increasing, decreasing, stable
    growth_rate: float = 0.0  # monthly percentage
    seasonal_factors: Dict[str, float] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class CostOptimizationMetrics:
    """Advanced cost optimization and financial efficiency analytics system."""
    
    def __init__(self):
        """Initialize the cost optimization metrics system."""
        self.cost_records: Dict[str, CostRecord] = {}
        self.roi_analyses: Dict[str, ROIAnalysis] = {}
        self.resource_utilization: Dict[str, ResourceUtilization] = {}
        self.optimization_recommendations: Dict[str, CostOptimizationRecommendation] = {}
        self.budget_alerts: Dict[str, BudgetAlert] = {}
        self.cost_forecasts: Dict[str, CostForecast] = {}
        
        # Time-series cost data
        self.cost_history: Dict[CostCategory, deque] = {
            category: deque(maxlen=10000) for category in CostCategory
        }
        
        # Budget tracking
        self.budgets: Dict[CostCategory, Dict[str, Decimal]] = defaultdict(dict)
        self.budget_periods: Dict[CostCategory, str] = {}
        
        # Optimization settings
        self.optimization_thresholds = {
            "utilization_warning": 80.0,
            "utilization_critical": 95.0,
            "cost_increase_warning": 20.0,  # 20% increase
            "roi_minimum": 10.0  # 10% minimum ROI
        }
        
        # Threading and processing
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=6)
        
        # ML models for cost prediction (placeholders)
        self.cost_predictor = None
        self.optimization_engine = None
        self.anomaly_detector = None
        
        # Exchange rates cache (for multi-currency support)
        self.exchange_rates = {"USD": 1.0, "EUR": 0.85, "GBP": 0.73}
        
        logger.info("CostOptimizationMetrics initialized successfully")
    
    async def record_cost(self, cost_record: CostRecord) -> bool:
        """Record a cost entry and update analytics."""
        try:
            with self.lock:
                # Store cost record
                self.cost_records[cost_record.cost_id] = cost_record
                
                # Add to time-series data
                self.cost_history[cost_record.category].append(cost_record)
                
                # Update budget tracking
                await self._update_budget_tracking(cost_record)
                
                # Check for alerts
                await self._check_cost_alerts(cost_record)
                
                # Update optimization recommendations
                await self._update_optimization_recommendations(cost_record)
            
            logger.debug(f"Recorded cost: {cost_record.description} - {cost_record.amount} {cost_record.currency}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording cost: {e}")
            return False
    
    async def analyze_roi(
        self, 
        investment_category: CostCategory,
        investment_amount: Decimal,
        analysis_period: timedelta = timedelta(days=30),
        attribution_model: str = "last_touch"
    ) -> ROIAnalysis:
        """Analyze return on investment for a specific category."""
        try:
            # Calculate investment period
            end_date = datetime.utcnow()
            start_date = end_date - analysis_period
            
            # Get investment costs
            investment_costs = await self._get_category_costs(
                investment_category, start_date, end_date
            )
            
            # Calculate revenue attribution
            revenue_generated = await self._calculate_attributed_revenue(
                investment_category, start_date, end_date, attribution_model
            )
            
            # Calculate ROI metrics
            total_investment = sum(cost.amount for cost in investment_costs) + investment_amount
            roi_percentage = 0.0
            
            if total_investment > 0:
                roi_percentage = float((revenue_generated - total_investment) / total_investment * 100)
            
            # Calculate payback period
            payback_period = await self._calculate_payback_period(
                total_investment, revenue_generated, analysis_period
            )
            
            # Calculate NPV (simplified)
            discount_rate = 0.1  # 10% annual discount rate
            npv = await self._calculate_npv(
                total_investment, revenue_generated, analysis_period, discount_rate
            )
            
            # Calculate confidence score
            confidence = await self._calculate_roi_confidence(
                investment_costs, revenue_generated, attribution_model
            )
            
            analysis = ROIAnalysis(
                investment_category=investment_category,
                investment_amount=total_investment,
                revenue_generated=revenue_generated,
                roi_percentage=roi_percentage,
                payback_period_days=payback_period,
                net_present_value=npv,
                analysis_period=analysis_period,
                confidence_score=confidence,
                attribution_model=attribution_model
            )
            
            # Store analysis
            self.roi_analyses[analysis.analysis_id] = analysis
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing ROI: {e}")
            return ROIAnalysis(investment_category=investment_category)
    
    async def track_resource_utilization(
        self, 
        resource_id: str,
        resource_type: ResourceType,
        capacity_total: float,
        capacity_used: float,
        cost_per_unit: Decimal
    ) -> ResourceUtilization:
        """Track resource utilization and efficiency."""
        try:
            # Calculate utilization metrics
            utilization_percentage = (capacity_used / capacity_total * 100) if capacity_total > 0 else 0
            waste_percentage = max(0, 100 - utilization_percentage)
            
            # Calculate efficiency score
            efficiency_score = await self._calculate_efficiency_score(
                utilization_percentage, resource_type
            )
            
            # Generate optimization recommendations
            optimization_recs = await self._generate_resource_optimization_recommendations(
                resource_type, utilization_percentage, efficiency_score
            )
            
            utilization = ResourceUtilization(
                resource_id=resource_id,
                resource_type=resource_type,
                utilization_percentage=utilization_percentage,
                capacity_total=capacity_total,
                capacity_used=capacity_used,
                cost_per_unit=cost_per_unit,
                efficiency_score=efficiency_score,
                waste_percentage=waste_percentage,
                optimization_recommendations=optimization_recs
            )
            
            # Store utilization data
            self.resource_utilization[resource_id] = utilization
            
            # Check for utilization alerts
            await self._check_utilization_alerts(utilization)
            
            return utilization
            
        except Exception as e:
            logger.error(f"Error tracking resource utilization: {e}")
            return ResourceUtilization(resource_id=resource_id, resource_type=resource_type)
    
    async def generate_cost_optimization_recommendations(
        self, 
        categories: Optional[List[CostCategory]] = None,
        min_savings_threshold: Decimal = Decimal('100.00')
    ) -> List[CostOptimizationRecommendation]:
        """Generate comprehensive cost optimization recommendations."""
        try:
            if not categories:
                categories = list(CostCategory)
            
            recommendations = []
            
            for category in categories:
                # Analyze category costs
                category_recs = await self._analyze_category_optimization(
                    category, min_savings_threshold
                )
                recommendations.extend(category_recs)
            
            # Resource-specific optimizations
            resource_recs = await self._generate_resource_based_recommendations(
                min_savings_threshold
            )
            recommendations.extend(resource_recs)
            
            # Contract and vendor optimizations
            contract_recs = await self._analyze_contract_optimizations(
                min_savings_threshold
            )
            recommendations.extend(contract_recs)
            
            # Usage pattern optimizations
            usage_recs = await self._analyze_usage_pattern_optimizations(
                min_savings_threshold
            )
            recommendations.extend(usage_recs)
            
            # Sort by potential savings and priority
            recommendations.sort(
                key=lambda r: (r.priority.value, float(r.potential_savings)), 
                reverse=True
            )
            
            # Store top recommendations
            for rec in recommendations[:20]:  # Store top 20
                self.optimization_recommendations[rec.recommendation_id] = rec
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating cost optimization recommendations: {e}")
            return []
    
    async def forecast_costs(
        self, 
        category: CostCategory,
        forecast_period: timedelta = timedelta(days=90)
    ) -> CostForecast:
        """Forecast future costs using historical data and trends."""
        try:
            # Get historical cost data
            historical_costs = list(self.cost_history[category])
            
            if len(historical_costs) < 10:
                logger.warning(f"Insufficient historical data for forecasting {category.value}")
                return CostForecast(category=category, forecast_period=forecast_period)
            
            # Calculate trend analysis
            trend_analysis = await self._analyze_cost_trends(historical_costs)
            
            # Apply seasonal adjustments
            seasonal_factors = await self._calculate_seasonal_factors(historical_costs)
            
            # Generate base forecast
            base_forecast = await self._generate_base_forecast(
                historical_costs, forecast_period
            )
            
            # Apply trend and seasonal adjustments
            adjusted_forecast = await self._apply_forecast_adjustments(
                base_forecast, trend_analysis, seasonal_factors
            )
            
            # Calculate confidence intervals
            confidence_interval = await self._calculate_forecast_confidence_interval(
                historical_costs, adjusted_forecast
            )
            
            # Assess forecast accuracy based on historical performance
            forecast_accuracy = await self._assess_forecast_accuracy(category)
            
            forecast = CostForecast(
                category=category,
                forecast_period=forecast_period,
                predicted_cost=adjusted_forecast,
                confidence_interval=confidence_interval,
                forecast_accuracy=forecast_accuracy,
                trend_direction=trend_analysis["direction"],
                growth_rate=trend_analysis["growth_rate"],
                seasonal_factors=seasonal_factors,
                assumptions=await self._get_forecast_assumptions(category, trend_analysis)
            )
            
            # Store forecast
            self.cost_forecasts[forecast.forecast_id] = forecast
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error forecasting costs for {category.value}: {e}")
            return CostForecast(category=category, forecast_period=forecast_period)
    
    async def set_budget(
        self, 
        category: CostCategory,
        amount: Decimal,
        period: str = "monthly",
        alert_thresholds: Optional[Dict[str, float]] = None
    ) -> bool:
        """Set budget for a cost category with alert thresholds."""
        try:
            # Store budget
            self.budgets[category]["amount"] = amount
            self.budgets[category]["period"] = period
            self.budget_periods[category] = period
            
            # Set default alert thresholds if not provided
            if not alert_thresholds:
                alert_thresholds = {
                    "warning": 80.0,    # 80% of budget
                    "critical": 95.0    # 95% of budget
                }
            
            self.budgets[category]["alert_thresholds"] = alert_thresholds
            
            # Check current budget status
            await self._check_budget_status(category)
            
            logger.info(f"Set budget for {category.value}: {amount} {period}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting budget: {e}")
            return False
    
    async def get_cost_analytics(
        self, 
        categories: Optional[List[CostCategory]] = None,
        timeframe: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Get comprehensive cost analytics."""
        try:
            if not categories:
                categories = list(CostCategory)
            
            end_date = datetime.utcnow()
            start_date = end_date - timeframe
            
            analytics = {
                "timeframe_days": timeframe.days,
                "analysis_timestamp": end_date.isoformat(),
                "total_costs": Decimal('0.00'),
                "category_breakdown": {},
                "cost_trends": {},
                "efficiency_metrics": {},
                "optimization_summary": {},
                "budget_status": {},
                "roi_summary": {}
            }
            
            # Calculate cost breakdown by category
            total_costs = Decimal('0.00')
            for category in categories:
                category_costs = await self._get_category_costs(category, start_date, end_date)
                category_total = sum(cost.amount for cost in category_costs)
                total_costs += category_total
                
                analytics["category_breakdown"][category.value] = {
                    "total_amount": float(category_total),
                    "transaction_count": len(category_costs),
                    "average_cost": float(category_total / max(len(category_costs), 1)),
                    "cost_percentage": 0.0  # Will be calculated after total
                }
            
            # Calculate percentages
            analytics["total_costs"] = float(total_costs)
            for category in categories:
                if total_costs > 0:
                    category_total = Decimal(str(analytics["category_breakdown"][category.value]["total_amount"]))
                    analytics["category_breakdown"][category.value]["cost_percentage"] = float(
                        category_total / total_costs * 100
                    )
            
            # Cost trend analysis
            for category in categories:
                trend_data = await self._get_category_trend_analysis(category, timeframe)
                analytics["cost_trends"][category.value] = trend_data
            
            # Efficiency metrics
            analytics["efficiency_metrics"] = await self._calculate_efficiency_metrics()
            
            # Optimization summary
            active_recommendations = [
                rec for rec in self.optimization_recommendations.values()
                if not rec.expires_at or rec.expires_at > datetime.utcnow()
            ]
            
            total_potential_savings = sum(rec.potential_savings for rec in active_recommendations)
            analytics["optimization_summary"] = {
                "total_recommendations": len(active_recommendations),
                "total_potential_savings": float(total_potential_savings),
                "high_priority_count": len([r for r in active_recommendations if r.priority == OptimizationPriority.HIGH]),
                "critical_priority_count": len([r for r in active_recommendations if r.priority == OptimizationPriority.CRITICAL])
            }
            
            # Budget status
            for category in categories:
                if category in self.budgets:
                    budget_status = await self._get_budget_status(category, start_date, end_date)
                    analytics["budget_status"][category.value] = budget_status
            
            # ROI summary
            recent_roi_analyses = [
                roi for roi in self.roi_analyses.values()
                if roi.created_at >= start_date
            ]
            
            if recent_roi_analyses:
                avg_roi = statistics.mean([roi.roi_percentage for roi in recent_roi_analyses])
                analytics["roi_summary"] = {
                    "analysis_count": len(recent_roi_analyses),
                    "average_roi": round(avg_roi, 2),
                    "positive_roi_count": len([roi for roi in recent_roi_analyses if roi.roi_percentage > 0]),
                    "best_performing_category": max(
                        recent_roi_analyses, 
                        key=lambda r: r.roi_percentage
                    ).investment_category.value if recent_roi_analyses else None
                }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting cost analytics: {e}")
            return {"error": str(e)}
    
    async def get_optimization_dashboard(self) -> Dict[str, Any]:
        """Get cost optimization dashboard data."""
        try:
            current_time = datetime.utcnow()
            
            # Active recommendations by priority
            active_recs = [
                rec for rec in self.optimization_recommendations.values()
                if not rec.expires_at or rec.expires_at > current_time
            ]
            
            recs_by_priority = defaultdict(list)
            for rec in active_recs:
                recs_by_priority[rec.priority.value].append(rec)
            
            # Resource utilization summary
            utilization_summary = {}
            for resource_type in ResourceType:
                type_resources = [
                    util for util in self.resource_utilization.values()
                    if util.resource_type == resource_type
                ]
                
                if type_resources:
                    avg_utilization = statistics.mean([r.utilization_percentage for r in type_resources])
                    avg_efficiency = statistics.mean([r.efficiency_score for r in type_resources])
                    
                    utilization_summary[resource_type.value] = {
                        "average_utilization": round(avg_utilization, 2),
                        "average_efficiency": round(avg_efficiency, 2),
                        "resource_count": len(type_resources),
                        "underutilized_count": len([r for r in type_resources if r.utilization_percentage < 50])
                    }
            
            # Budget alerts summary
            active_alerts = [
                alert for alert in self.budget_alerts.values()
                if alert.created_at >= current_time - timedelta(days=7)
            ]
            
            alerts_by_severity = defaultdict(int)
            for alert in active_alerts:
                alerts_by_severity[alert.threshold_type] += 1
            
            # Cost savings potential
            total_potential_savings = sum(rec.potential_savings for rec in active_recs)
            
            # Implementation quick wins (low effort, high impact)
            quick_wins = [
                rec for rec in active_recs
                if (rec.implementation_time <= timedelta(days=7) and 
                    rec.potential_savings >= Decimal('500.00') and
                    rec.risk_level == "low")
            ]
            
            return {
                "timestamp": current_time.isoformat(),
                "optimization_overview": {
                    "total_recommendations": len(active_recs),
                    "total_potential_savings": float(total_potential_savings),
                    "quick_wins_available": len(quick_wins),
                    "recommendations_by_priority": {
                        priority: len(recs) for priority, recs in recs_by_priority.items()
                    }
                },
                "resource_utilization": utilization_summary,
                "budget_alerts": {
                    "total_active_alerts": len(active_alerts),
                    "alerts_by_severity": dict(alerts_by_severity),
                    "categories_over_budget": len([
                        alert for alert in active_alerts 
                        if alert.utilization_percentage > 100
                    ])
                },
                "top_recommendations": [
                    {
                        "title": rec.title,
                        "category": rec.category.value,
                        "potential_savings": float(rec.potential_savings),
                        "priority": rec.priority.value,
                        "implementation_time_days": rec.implementation_time.days
                    }
                    for rec in sorted(active_recs, key=lambda r: r.potential_savings, reverse=True)[:5]
                ],
                "quick_wins": [
                    {
                        "title": rec.title,
                        "savings": float(rec.potential_savings),
                        "implementation_days": rec.implementation_time.days
                    }
                    for rec in quick_wins[:3]
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting optimization dashboard: {e}")
            return {"error": str(e)}
    
    # Private helper methods
    
    async def _update_budget_tracking(self, cost_record: CostRecord):
        """Update budget tracking with new cost record."""
        category = cost_record.category
        if category not in self.budgets:
            return
        
        # Calculate current period spend
        period_start = await self._get_period_start_date(
            self.budget_periods.get(category, "monthly")
        )
        
        period_costs = await self._get_category_costs(
            category, period_start, datetime.utcnow()
        )
        
        current_spend = sum(cost.amount for cost in period_costs)
        budget_amount = self.budgets[category].get("amount", Decimal('0.00'))
        
        # Check if budget alert is needed
        if budget_amount > 0:
            utilization_percentage = float(current_spend / budget_amount * 100)
            alert_thresholds = self.budgets[category].get("alert_thresholds", {})
            
            # Create alert if threshold exceeded
            for threshold_name, threshold_value in alert_thresholds.items():
                if utilization_percentage >= threshold_value:
                    await self._create_budget_alert(
                        category, budget_amount, current_spend, 
                        utilization_percentage, threshold_name
                    )
    
    async def _check_cost_alerts(self, cost_record: CostRecord):
        """Check if cost record triggers any alerts."""
        # Check for anomalous costs
        category_history = list(self.cost_history[cost_record.category])
        
        if len(category_history) >= 10:
            recent_amounts = [
                float(cost.amount) for cost in category_history[-10:]
                if cost.amount > 0
            ]
            
            if recent_amounts:
                avg_amount = statistics.mean(recent_amounts)
                std_dev = statistics.stdev(recent_amounts) if len(recent_amounts) > 1 else 0
                
                # Alert if cost is significantly higher than average
                if float(cost_record.amount) > avg_amount + (2 * std_dev):
                    await self._create_anomaly_alert(cost_record, avg_amount)
    
    async def _create_budget_alert(
        self, 
        category: CostCategory,
        budget_amount: Decimal,
        current_spend: Decimal,
        utilization_percentage: float,
        threshold_type: str
    ):
        """Create a budget alert."""
        # Calculate burn rate and forecast
        period_start = await self._get_period_start_date(
            self.budget_periods.get(category, "monthly")
        )
        
        days_elapsed = (datetime.utcnow() - period_start).days
        burn_rate = current_spend / max(days_elapsed, 1) if days_elapsed > 0 else current_spend
        
        # Calculate days remaining in period
        period_end = await self._get_period_end_date(
            self.budget_periods.get(category, "monthly")
        )
        days_remaining = (period_end - datetime.utcnow()).days
        
        # Forecast overspend
        forecast_spend = current_spend + (burn_rate * days_remaining)
        forecast_overspend = max(Decimal('0.00'), forecast_spend - budget_amount)
        
        # Generate recommendations
        recommendations = []
        if forecast_overspend > 0:
            recommendations.append(f"Reduce spending by ${forecast_overspend:.2f} to stay within budget")
        if burn_rate > budget_amount / 30:  # Assuming monthly budget
            recommendations.append("Consider implementing cost controls to reduce burn rate")
        
        alert = BudgetAlert(
            category=category,
            budget_limit=budget_amount,
            current_spend=current_spend,
            utilization_percentage=utilization_percentage,
            threshold_type=threshold_type,
            forecast_overspend=forecast_overspend,
            days_remaining=days_remaining,
            burn_rate=burn_rate,
            recommended_actions=recommendations
        )
        
        self.budget_alerts[alert.alert_id] = alert
        
        logger.warning(
            f"Budget alert for {category.value}: {utilization_percentage:.1f}% utilized "
            f"({threshold_type} threshold)"
        )
    
    async def _get_category_costs(
        self, 
        category: CostCategory, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[CostRecord]:
        """Get cost records for a category within date range."""
        return [
            cost for cost in self.cost_records.values()
            if (cost.category == category and 
                start_date <= cost.date <= end_date)
        ]
    
    async def _calculate_attributed_revenue(
        self, 
        investment_category: CostCategory,
        start_date: datetime,
        end_date: datetime,
        attribution_model: str
    ) -> Decimal:
        """Calculate revenue attributed to investment category."""
        # Simplified revenue attribution - would use actual revenue tracking in production
        
        base_revenue = Decimal('10000.00')  # Mock base revenue
        
        # Apply attribution multipliers based on category
        attribution_multipliers = {
            CostCategory.MARKETING: 2.5,
            CostCategory.CONTENT_CREATION: 1.8,
            CostCategory.CREATOR_PAYMENTS: 3.0,
            CostCategory.INFRASTRUCTURE: 0.8,
            CostCategory.PLATFORM_FEES: 0.5
        }
        
        multiplier = attribution_multipliers.get(investment_category, 1.0)
        attributed_revenue = base_revenue * Decimal(str(multiplier))
        
        # Apply time-based decay for attribution model
        if attribution_model == "time_decay":
            days_elapsed = (end_date - start_date).days
            decay_factor = max(0.5, 1.0 - (days_elapsed / 365))  # Decay over a year
            attributed_revenue *= Decimal(str(decay_factor))
        
        return attributed_revenue
    
    async def _calculate_payback_period(
        self, 
        investment: Decimal,
        revenue: Decimal,
        analysis_period: timedelta
    ) -> Optional[int]:
        """Calculate payback period in days."""
        if revenue <= investment:
            return None  # No payback achieved
        
        daily_net_return = (revenue - investment) / Decimal(str(analysis_period.days))
        
        if daily_net_return <= 0:
            return None
        
        payback_days = int(investment / daily_net_return)
        return payback_days if payback_days > 0 else None
    
    async def _calculate_npv(
        self, 
        investment: Decimal,
        revenue: Decimal,
        period: timedelta,
        discount_rate: float
    ) -> Decimal:
        """Calculate Net Present Value."""
        net_cash_flow = revenue - investment
        periods = period.days / 365  # Convert to years
        
        # Simple NPV calculation
        npv = net_cash_flow / (1 + discount_rate) ** periods
        return npv
    
    async def _calculate_roi_confidence(
        self, 
        investment_costs: List[CostRecord],
        revenue: Decimal,
        attribution_model: str
    ) -> float:
        """Calculate confidence score for ROI analysis."""
        confidence_factors = []
        
        # Data completeness factor
        data_completeness = min(1.0, len(investment_costs) / 10)  # Ideal: 10+ data points
        confidence_factors.append(data_completeness)
        
        # Attribution model confidence
        attribution_confidence = {
            "last_touch": 0.6,
            "first_touch": 0.5,
            "linear": 0.7,
            "time_decay": 0.8,
            "position_based": 0.75
        }
        confidence_factors.append(attribution_confidence.get(attribution_model, 0.5))
        
        # Revenue variability factor
        if revenue > 0:
            confidence_factors.append(0.8)  # Simplified - would analyze revenue stability
        else:
            confidence_factors.append(0.3)
        
        return statistics.mean(confidence_factors)
    
    async def _calculate_efficiency_score(
        self, 
        utilization_percentage: float, 
        resource_type: ResourceType
    ) -> float:
        """Calculate efficiency score for resource utilization."""
        # Optimal utilization ranges by resource type
        optimal_ranges = {
            ResourceType.CPU: (70, 85),
            ResourceType.MEMORY: (60, 80),
            ResourceType.STORAGE: (50, 75),
            ResourceType.NETWORK: (40, 70),
            ResourceType.GPU: (80, 95),
            ResourceType.DATABASE: (60, 80),
            ResourceType.CACHE: (70, 90),
            ResourceType.CDN: (50, 70)
        }
        
        optimal_min, optimal_max = optimal_ranges.get(resource_type, (60, 80))
        
        if optimal_min <= utilization_percentage <= optimal_max:
            # Maximum efficiency in optimal range
            return 100.0
        elif utilization_percentage < optimal_min:
            # Underutilized - efficiency decreases linearly
            return max(0, utilization_percentage / optimal_min * 100)
        else:
            # Overutilized - efficiency decreases after optimal range
            excess = utilization_percentage - optimal_max
            penalty = min(50, excess)  # Max 50% penalty for overutilization
            return max(0, 100 - penalty)
    
    async def _generate_resource_optimization_recommendations(
        self, 
        resource_type: ResourceType,
        utilization_percentage: float,
        efficiency_score: float
    ) -> List[str]:
        """Generate optimization recommendations for resource utilization."""
        recommendations = []
        
        if utilization_percentage < 30:
            recommendations.append(f"Consider downsizing {resource_type.value} capacity - currently underutilized")
            recommendations.append("Evaluate if this resource is necessary for current workload")
        elif utilization_percentage < 50:
            recommendations.append(f"Optimize {resource_type.value} allocation to improve cost efficiency")
            recommendations.append("Consider consolidating workloads to reduce waste")
        elif utilization_percentage > 90:
            recommendations.append(f"Scale up {resource_type.value} capacity to prevent performance bottlenecks")
            recommendations.append("Implement auto-scaling if not already configured")
        elif utilization_percentage > 95:
            recommendations.append(f"URGENT: {resource_type.value} is critically overutilized")
            recommendations.append("Immediate capacity increase required to maintain service quality")
        
        if efficiency_score < 60:
            recommendations.append("Review resource configuration for optimization opportunities")
            recommendations.append("Consider implementing resource monitoring and alerting")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    async def _check_utilization_alerts(self, utilization: ResourceUtilization):
        """Check resource utilization for alert conditions."""
        if utilization.utilization_percentage > self.optimization_thresholds["utilization_critical"]:
            # Create critical utilization alert
            logger.critical(
                f"Critical resource utilization: {utilization.resource_id} at "
                f"{utilization.utilization_percentage:.1f}%"
            )
        elif utilization.utilization_percentage > self.optimization_thresholds["utilization_warning"]:
            # Create warning alert
            logger.warning(
                f"High resource utilization: {utilization.resource_id} at "
                f"{utilization.utilization_percentage:.1f}%"
            )
    
    async def _get_period_start_date(self, period: str) -> datetime:
        """Get the start date for a budget period."""
        now = datetime.utcnow()
        
        if period == "daily":
            return now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "weekly":
            days_since_monday = now.weekday()
            return (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "monthly":
            return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "quarterly":
            quarter_start_month = ((now.month - 1) // 3) * 3 + 1
            return now.replace(month=quarter_start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif period == "yearly":
            return now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return now - timedelta(days=30)  # Default to 30 days
    
    async def _get_period_end_date(self, period: str) -> datetime:
        """Get the end date for a budget period."""
        start_date = await self._get_period_start_date(period)
        
        if period == "daily":
            return start_date + timedelta(days=1) - timedelta(microseconds=1)
        elif period == "weekly":
            return start_date + timedelta(days=7) - timedelta(microseconds=1)
        elif period == "monthly":
            if start_date.month == 12:
                next_month = start_date.replace(year=start_date.year + 1, month=1)
            else:
                next_month = start_date.replace(month=start_date.month + 1)
            return next_month - timedelta(microseconds=1)
        elif period == "quarterly":
            return start_date + timedelta(days=90) - timedelta(microseconds=1)
        elif period == "yearly":
            return start_date.replace(year=start_date.year + 1) - timedelta(microseconds=1)
        else:
            return start_date + timedelta(days=30) - timedelta(microseconds=1)


# Export the main class
__all__ = [
    "CostOptimizationMetrics", 
    "CostRecord", 
    "ROIAnalysis", 
    "ResourceUtilization",
    "CostOptimizationRecommendation",
    "BudgetAlert",
    "CostForecast"
]