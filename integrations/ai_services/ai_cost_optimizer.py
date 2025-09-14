"""AI Cost Optimizer - AI Service Cost Optimization and Management System
=========================================================================

Advanced cost optimization system for AI services that tracks spending,
optimizes costs, predicts usage, and manages budgets across providers.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Optional, Any, Union, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import statistics
import hashlib

import aioredis
import aiofiles
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)


class CostMetric(Enum):
    """Cost tracking metrics."""
    REQUEST_COUNT = "request_count"
    TOKEN_COUNT = "token_count"
    PROCESSING_TIME = "processing_time"
    TOTAL_COST = "total_cost"
    AVERAGE_COST = "average_cost"
    COST_PER_TOKEN = "cost_per_token"
    COST_EFFICIENCY = "cost_efficiency"


class BudgetPeriod(Enum):
    """Budget tracking periods."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class CostOptimizationStrategy(Enum):
    """Cost optimization strategies."""
    MINIMIZE_COST = "minimize_cost"
    MAXIMIZE_QUALITY = "maximize_quality"
    BALANCED = "balanced"
    BUDGET_CONSTRAINED = "budget_constrained"
    PERFORMANCE_OPTIMIZED = "performance_optimized"


class AlertLevel(Enum):
    """Cost alert levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    BUDGET_EXCEEDED = "budget_exceeded"


@dataclass
class CostRecord:
    """Individual cost record."""
    timestamp: datetime
    provider: str
    model: str
    service_type: str
    request_id: str
    user_id: Optional[str]
    input_tokens: int
    output_tokens: int
    total_tokens: int
    processing_time_ms: float
    base_cost: float
    additional_costs: Dict[str, float]
    total_cost: float
    quality_score: float
    cost_efficiency: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BudgetLimit:
    """Budget limit configuration."""
    name: str
    period: BudgetPeriod
    limit_amount: float
    current_usage: float
    alert_thresholds: List[float]  # e.g., [0.5, 0.8, 0.9]
    scope: Dict[str, Any]  # e.g., {"user_id": "123", "provider": "openai"}
    auto_disable: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CostPrediction:
    """Cost prediction result."""
    period: BudgetPeriod
    predicted_cost: float
    confidence_interval: Tuple[float, float]
    prediction_accuracy: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    factors: Dict[str, float]
    recommendations: List[str]


@dataclass
class OptimizationRecommendation:
    """Cost optimization recommendation."""
    type: str
    description: str
    potential_savings: float
    impact_score: float
    implementation_effort: str  # "low", "medium", "high"
    provider_changes: Dict[str, str]
    configuration_changes: Dict[str, Any]


class CostTracker:
    """Cost tracking and monitoring system."""
    
    def __init__(self, redis_url -> None: str = None) -> None:
        self.cost_records: deque = deque(maxlen=10000)
        self.budget_limits: Dict[str, BudgetLimit] = {}
        self.redis_client = None
        self.redis_url = redis_url
        
        # Metrics
        self.cost_counter = Counter('ai_costs_total', 'Total AI costs', ['provider', 'model'])
        self.request_counter = Counter('ai_requests_total', 'Total AI requests', ['provider', 'model'])
        self.token_counter = Counter('ai_tokens_total', 'Total AI tokens', ['provider', 'model', 'type'])
        self.cost_gauge = Gauge('ai_cost_current', 'Current AI costs', ['provider', 'period'])
        self.budget_gauge = Gauge('ai_budget_usage', 'Budget usage percentage', ['budget_name'])
        
        # Cost tracking by period
        self.period_costs: Dict[BudgetPeriod, Dict[str, float]] = {
            period: defaultdict(float) for period in BudgetPeriod
        }
        
        # Cost optimization cache
        self.optimization_cache: Dict[str, Any] = {}
        self.last_optimization = {}
    
    async def initialize(self) -> None:
        """Initialize the cost tracker."""
        try:
            if self.redis_url:
                self.redis_client = await aioredis.create_redis_pool(self.redis_url)
                await self._load_budget_limits()
            
            # Start monitoring tasks
            asyncio.create_task(self._periodic_budget_check())
            asyncio.create_task(self._cost_aggregation_task())
            
            logger.info("Cost tracker initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize cost tracker: {str(e)}")
            raise
    
    async def record_cost(self, 
                         provider: str,
                         model: str,
                         service_type: str,
                         request_id: str,
                         input_tokens: int,
                         output_tokens: int,
                         processing_time_ms: float,
                         base_cost: float,
                         quality_score: float = 1.0,
                         user_id: Optional[str] = None,
                         additional_costs: Optional[Dict[str, float]] = None) -> CostRecord:
        """Record a cost entry."""
        try:
            additional_costs = additional_costs or {}
            total_cost = base_cost + sum(additional_costs.values())
            total_tokens = input_tokens + output_tokens
            
            # Calculate cost efficiency (quality per dollar)
            cost_efficiency = quality_score / total_cost if total_cost > 0 else 0
            
            cost_record = CostRecord(
                timestamp=datetime.utcnow(),
                provider=provider,
                model=model,
                service_type=service_type,
                request_id=request_id,
                user_id=user_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                processing_time_ms=processing_time_ms,
                base_cost=base_cost,
                additional_costs=additional_costs,
                total_cost=total_cost,
                quality_score=quality_score,
                cost_efficiency=cost_efficiency
            )
            
            # Store record
            self.cost_records.append(cost_record)
            
            # Update metrics
            self.cost_counter.labels(provider=provider, model=model).inc(total_cost)
            self.request_counter.labels(provider=provider, model=model).inc()
            self.token_counter.labels(provider=provider, model=model, type='input').inc(input_tokens)
            self.token_counter.labels(provider=provider, model=model, type='output').inc(output_tokens)
            
            # Update period costs
            await self._update_period_costs(cost_record)
            
            # Check budgets
            await self._check_budget_limits(cost_record)
            
            # Store in Redis for persistence
            if self.redis_client:
                await self._store_cost_record(cost_record)
            
            return cost_record
            
        except Exception as e:
            logger.error(f"Failed to record cost: {str(e)}")
            raise
    
    async def _update_period_costs(self, cost_record -> None: CostRecord) -> None:
        """Update cost tracking for different periods."""
        timestamp = cost_record.timestamp
        provider_key = f"{cost_record.provider}_{cost_record.model}"
        
        # Update hourly
        hour_key = timestamp.strftime("%Y-%m-%d-%H")
        self.period_costs[BudgetPeriod.HOURLY][f"{provider_key}_{hour_key}"] += cost_record.total_cost
        
        # Update daily
        day_key = timestamp.strftime("%Y-%m-%d")
        self.period_costs[BudgetPeriod.DAILY][f"{provider_key}_{day_key}"] += cost_record.total_cost
        
        # Update weekly
        week_key = f"{timestamp.year}-W{timestamp.isocalendar()[1]}"
        self.period_costs[BudgetPeriod.WEEKLY][f"{provider_key}_{week_key}"] += cost_record.total_cost
        
        # Update monthly
        month_key = timestamp.strftime("%Y-%m")
        self.period_costs[BudgetPeriod.MONTHLY][f"{provider_key}_{month_key}"] += cost_record.total_cost
        
        # Update yearly
        year_key = str(timestamp.year)
        self.period_costs[BudgetPeriod.YEARLY][f"{provider_key}_{year_key}"] += cost_record.total_cost
    
    async def create_budget_limit(self, 
                                name: str,
                                period: BudgetPeriod,
                                limit_amount: float,
                                alert_thresholds: List[float],
                                scope: Optional[Dict[str, Any]] = None,
                                auto_disable: bool = False) -> str:
        """Create a new budget limit."""
        try:
            budget_id = hashlib.md5(f"{name}_{period.value}_{time.time()}".encode()).hexdigest()
            
            budget_limit = BudgetLimit(
                name=name,
                period=period,
                limit_amount=limit_amount,
                current_usage=0.0,
                alert_thresholds=sorted(alert_thresholds),
                scope=scope or {},
                auto_disable=auto_disable
            )
            
            self.budget_limits[budget_id] = budget_limit
            
            # Store in Redis
            if self.redis_client:
                await self.redis_client.hset(
                    "budget_limits",
                    budget_id,
                    json.dumps(asdict(budget_limit), default=str)
                )
            
            logger.info(f"Created budget limit: {name} - ${limit_amount}/{period.value}")
            return budget_id
            
        except Exception as e:
            logger.error(f"Failed to create budget limit: {str(e)}")
            raise
    
    async def _check_budget_limits(self, cost_record -> None: CostRecord) -> None:
        """Check if cost record violates any budget limits."""
        for budget_id, budget in self.budget_limits.items():
            try:
                # Check if cost record matches budget scope
                if not self._matches_budget_scope(cost_record, budget.scope):
                    continue
                
                # Calculate current usage for the period
                current_usage = await self._calculate_budget_usage(budget)
                budget.current_usage = current_usage
                
                # Check alert thresholds
                usage_percentage = current_usage / budget.limit_amount if budget.limit_amount > 0 else 0
                
                for threshold in budget.alert_thresholds:
                    if usage_percentage >= threshold:
                        await self._send_budget_alert(budget, usage_percentage, threshold)
                
                # Check if budget exceeded
                if current_usage >= budget.limit_amount:
                    await self._handle_budget_exceeded(budget, cost_record)
                
                # Update metrics
                self.budget_gauge.labels(budget_name=budget.name).set(usage_percentage)
                
            except Exception as e:
                logger.error(f"Budget check failed for {budget_id}: {str(e)}")
    
    def _matches_budget_scope(self, cost_record: CostRecord, scope: Dict[str, Any]) -> bool:
        """Check if cost record matches budget scope."""
        if not scope:
            return True
        
        for key, value in scope.items():
            if key == "provider" and cost_record.provider != value:
                return False
            elif key == "model" and cost_record.model != value:
                return False
            elif key == "service_type" and cost_record.service_type != value:
                return False
            elif key == "user_id" and cost_record.user_id != value:
                return False
        
        return True
    
    async def _calculate_budget_usage(self, budget: BudgetLimit) -> float:
        """Calculate current budget usage for the period."""
        now = datetime.utcnow()
        
        # Determine period start
        if budget.period == BudgetPeriod.HOURLY:
            period_start = now.replace(minute=0, second=0, microsecond=0)
        elif budget.period == BudgetPeriod.DAILY:
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif budget.period == BudgetPeriod.WEEKLY:
            days_since_monday = now.weekday()
            period_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif budget.period == BudgetPeriod.MONTHLY:
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif budget.period == BudgetPeriod.YEARLY:
            period_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate usage
        total_usage = 0.0
        for record in self.cost_records:
            if record.timestamp >= period_start and self._matches_budget_scope(record, budget.scope):
                total_usage += record.total_cost
        
        return total_usage
    
    async def _send_budget_alert(self, budget -> None: BudgetLimit, usage_percentage -> None: float, threshold -> None: float) -> None:
        """Send budget alert notification."""
        alert_data = {
            "budget_name": budget.name,
            "period": budget.period.value,
            "usage_percentage": usage_percentage,
            "threshold": threshold,
            "current_usage": budget.current_usage,
            "limit_amount": budget.limit_amount,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.warning(f"Budget alert: {budget.name} - {usage_percentage:.1%} usage (threshold: {threshold:.1%})")
        
        # Store alert for external processing
        if self.redis_client:
            await self.redis_client.lpush("budget_alerts", json.dumps(alert_data))
    
    async def _handle_budget_exceeded(self, budget -> None: BudgetLimit, cost_record -> None: CostRecord) -> None:
        """Handle budget exceeded scenario."""
        logger.critical(f"Budget exceeded: {budget.name} - ${budget.current_usage:.2f} / ${budget.limit_amount:.2f}")
        
        if budget.auto_disable:
            # Disable further requests for this scope
            await self._disable_scope(budget.scope)
        
        # Send critical alert
        alert_data = {
            "budget_name": budget.name,
            "period": budget.period.value,
            "usage": budget.current_usage,
            "limit": budget.limit_amount,
            "auto_disabled": budget.auto_disable,
            "timestamp": datetime.utcnow().isoformat(),
            "cost_record": asdict(cost_record)
        }
        
        if self.redis_client:
            await self.redis_client.lpush("budget_exceeded", json.dumps(alert_data, default=str))


class CostOptimizer:
    """AI cost optimization system."""
    
    def __init__(self, cost_tracker -> None: CostTracker) -> None:
        self.cost_tracker = cost_tracker
        self.optimization_rules = {
            'provider_switching': self._optimize_provider_switching,
            'model_selection': self._optimize_model_selection,
            'batch_processing': self._optimize_batch_processing,
            'caching_strategy': self._optimize_caching_strategy,
            'request_throttling': self._optimize_request_throttling
        }
        
        # Cost prediction models (simple moving averages for now)
        self.prediction_window = 30  # days
        self.prediction_cache = {}
    
    async def optimize_costs(self, strategy: CostOptimizationStrategy = CostOptimizationStrategy.BALANCED) -> List[OptimizationRecommendation]:
        """Generate cost optimization recommendations."""
        recommendations = []
        
        try:
            # Analyze cost patterns
            cost_analysis = await self._analyze_cost_patterns()
            
            # Generate recommendations based on strategy
            for rule_name, rule_func in self.optimization_rules.items():
                try:
                    rule_recommendations = await rule_func(cost_analysis, strategy)
                    recommendations.extend(rule_recommendations)
                    
                except Exception as e:
                    logger.warning(f"Optimization rule {rule_name} failed: {str(e)}")
            
            # Sort by impact score
            recommendations.sort(key=lambda x: x.impact_score, reverse=True)
            
            return recommendations[:10]  # Top 10 recommendations
            
        except Exception as e:
            logger.error(f"Cost optimization failed: {str(e)}")
            return []
    
    async def _analyze_cost_patterns(self) -> Dict[str, Any]:
        """Analyze cost patterns and trends."""
        analysis = {
            'provider_costs': defaultdict(float),
            'model_costs': defaultdict(float),
            'service_costs': defaultdict(float),
            'hourly_patterns': defaultdict(list),
            'cost_efficiency': defaultdict(list),
            'total_cost': 0.0,
            'total_requests': 0,
            'average_cost_per_request': 0.0,
            'cost_trend': 'stable'
        }
        
        # Analyze recent cost records
        recent_records = [r for r in self.cost_tracker.cost_records if r.timestamp > datetime.utcnow() - timedelta(days=7)]
        
        for record in recent_records:
            analysis['provider_costs'][record.provider] += record.total_cost
            analysis['model_costs'][f"{record.provider}_{record.model}"] += record.total_cost
            analysis['service_costs'][record.service_type] += record.total_cost
            analysis['total_cost'] += record.total_cost
            analysis['total_requests'] += 1
            
            # Hourly patterns
            hour = record.timestamp.hour
            analysis['hourly_patterns'][hour].append(record.total_cost)
            
            # Cost efficiency
            analysis['cost_efficiency'][f"{record.provider}_{record.model}"].append(record.cost_efficiency)
        
        # Calculate averages
        if analysis['total_requests'] > 0:
            analysis['average_cost_per_request'] = analysis['total_cost'] / analysis['total_requests']
        
        # Determine cost trend
        if len(recent_records) >= 2:
            first_half = recent_records[:len(recent_records)//2]
            second_half = recent_records[len(recent_records)//2:]
            
            first_avg = sum(r.total_cost for r in first_half) / len(first_half)
            second_avg = sum(r.total_cost for r in second_half) / len(second_half)
            
            if second_avg > first_avg * 1.1:
                analysis['cost_trend'] = 'increasing'
            elif second_avg < first_avg * 0.9:
                analysis['cost_trend'] = 'decreasing'
        
        return analysis
    
    async def _optimize_provider_switching(self, analysis: Dict[str, Any], strategy: CostOptimizationStrategy) -> List[OptimizationRecommendation]:
        """Generate provider switching recommendations."""
        recommendations = []
        
        # Find expensive providers
        provider_costs = analysis['provider_costs']
        if len(provider_costs) > 1:
            sorted_providers = sorted(provider_costs.items(), key=lambda x: x[1], reverse=True)
            most_expensive = sorted_providers[0]
            least_expensive = sorted_providers[-1]
            
            if most_expensive[1] > least_expensive[1] * 2:  # More than 2x difference
                potential_savings = most_expensive[1] - least_expensive[1]
                
                recommendations.append(OptimizationRecommendation(
                    type="provider_switching",
                    description=f"Switch from {most_expensive[0]} to {least_expensive[0]} for cost savings",
                    potential_savings=potential_savings,
                    impact_score=min(potential_savings / analysis['total_cost'], 1.0),
                    implementation_effort="medium",
                    provider_changes={most_expensive[0]: least_expensive[0]},
                    configuration_changes={"primary_provider": least_expensive[0]}
                ))
        
        return recommendations
    
    async def _optimize_model_selection(self, analysis: Dict[str, Any], strategy: CostOptimizationStrategy) -> List[OptimizationRecommendation]:
        """Generate model selection recommendations."""
        recommendations = []
        
        # Analyze cost efficiency by model
        model_efficiency = {}
        for model, efficiency_scores in analysis['cost_efficiency'].items():
            if efficiency_scores:
                model_efficiency[model] = statistics.mean(efficiency_scores)
        
        if len(model_efficiency) > 1:
            best_model = max(model_efficiency.items(), key=lambda x: x[1])
            worst_model = min(model_efficiency.items(), key=lambda x: x[1])
            
            if best_model[1] > worst_model[1] * 1.5:  # 50% better efficiency
                model_cost = analysis['model_costs'].get(worst_model[0], 0)
                potential_savings = model_cost * 0.3  # Estimate 30% savings
                
                recommendations.append(OptimizationRecommendation(
                    type="model_selection",
                    description=f"Switch from {worst_model[0]} to {best_model[0]} for better cost efficiency",
                    potential_savings=potential_savings,
                    impact_score=potential_savings / analysis['total_cost'] if analysis['total_cost'] > 0 else 0,
                    implementation_effort="low",
                    provider_changes={},
                    configuration_changes={"preferred_model": best_model[0]}
                ))
        
        return recommendations
    
    async def _optimize_batch_processing(self, analysis: Dict[str, Any], strategy: CostOptimizationStrategy) -> List[OptimizationRecommendation]:
        """Generate batch processing recommendations."""
        recommendations = []
        
        # Check if many small requests could be batched
        small_requests = [r for r in self.cost_tracker.cost_records if r.total_tokens < 100]
        
        if len(small_requests) > analysis['total_requests'] * 0.3:  # More than 30% are small
            potential_savings = sum(r.total_cost for r in small_requests) * 0.2  # 20% savings
            
            recommendations.append(OptimizationRecommendation(
                type="batch_processing",
                description="Implement batch processing for small requests to reduce API overhead",
                potential_savings=potential_savings,
                impact_score=potential_savings / analysis['total_cost'] if analysis['total_cost'] > 0 else 0,
                implementation_effort="high",
                provider_changes={},
                configuration_changes={"enable_batching": True, "batch_size": 10}
            ))
        
        return recommendations
    
    async def _optimize_caching_strategy(self, analysis: Dict[str, Any], strategy: CostOptimizationStrategy) -> List[OptimizationRecommendation]:
        """Generate caching strategy recommendations."""
        recommendations = []
        
        # Analyze request patterns for potential caching
        # This is a simplified analysis - in practice, you'd need more sophisticated duplicate detection
        total_cost = analysis['total_cost']
        
        if total_cost > 0:
            # Estimate potential cache hit rate based on request patterns
            estimated_cache_savings = total_cost * 0.15  # Conservative 15% estimate
            
            recommendations.append(OptimizationRecommendation(
                type="caching_strategy",
                description="Implement intelligent response caching to reduce redundant API calls",
                potential_savings=estimated_cache_savings,
                impact_score=0.15,  # 15% impact
                implementation_effort="medium",
                provider_changes={},
                configuration_changes={
                    "enable_caching": True,
                    "cache_ttl": 3600,
                    "cache_similarity_threshold": 0.9
                }
            ))
        
        return recommendations
    
    async def _optimize_request_throttling(self, analysis: Dict[str, Any], strategy: CostOptimizationStrategy) -> List[OptimizationRecommendation]:
        """Generate request throttling recommendations."""
        recommendations = []
        
        # Analyze hourly patterns for peak usage
        hourly_costs = {}
        for hour, costs in analysis['hourly_patterns'].items():
            if costs:
                hourly_costs[hour] = sum(costs)
        
        if hourly_costs:
            max_hour_cost = max(hourly_costs.values())
            avg_hour_cost = sum(hourly_costs.values()) / len(hourly_costs)
            
            if max_hour_cost > avg_hour_cost * 3:  # Peak is 3x average
                potential_savings = (max_hour_cost - avg_hour_cost) * 0.5  # 50% peak reduction
                
                recommendations.append(OptimizationRecommendation(
                    type="request_throttling",
                    description="Implement request throttling during peak hours to control costs",
                    potential_savings=potential_savings,
                    impact_score=potential_savings / analysis['total_cost'] if analysis['total_cost'] > 0 else 0,
                    implementation_effort="medium",
                    provider_changes={},
                    configuration_changes={
                        "enable_throttling": True,
                        "peak_hours": [h for h, c in hourly_costs.items() if c > avg_hour_cost * 2],
                        "throttle_rate": 0.7
                    }
                ))
        
        return recommendations
    
    async def predict_costs(self, period: BudgetPeriod, horizon_days: int = 30) -> CostPrediction:
        """Predict future costs based on historical patterns."""
        try:
            # Get historical data
            lookback_days = max(30, horizon_days * 2)
            cutoff_date = datetime.utcnow() - timedelta(days=lookback_days)
            historical_records = [r for r in self.cost_tracker.cost_records if r.timestamp > cutoff_date]
            
            if not historical_records:
                return CostPrediction(
                    period=period,
                    predicted_cost=0.0,
                    confidence_interval=(0.0, 0.0),
                    prediction_accuracy=0.0,
                    trend_direction="stable",
                    factors={},
                    recommendations=["Insufficient data for prediction"]
                )
            
            # Calculate daily costs
            daily_costs = defaultdict(float)
            for record in historical_records:
                day_key = record.timestamp.strftime("%Y-%m-%d")
                daily_costs[day_key] += record.total_cost
            
            # Simple linear trend prediction
            costs = list(daily_costs.values())
            if len(costs) >= 7:  # Need at least a week of data
                # Calculate trend
                x = list(range(len(costs)))
                n = len(costs)
                sum_x = sum(x)
                sum_y = sum(costs)
                sum_xy = sum(x[i] * costs[i] for i in range(n))
                sum_x2 = sum(x[i] ** 2 for i in range(n))
                
                # Linear regression slope
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
                intercept = (sum_y - slope * sum_x) / n
                
                # Predict daily cost at horizon
                future_daily_cost = intercept + slope * (len(costs) + horizon_days // 2)
                
                # Adjust for period
                if period == BudgetPeriod.DAILY:
                    predicted_cost = future_daily_cost
                elif period == BudgetPeriod.WEEKLY:
                    predicted_cost = future_daily_cost * 7
                elif period == BudgetPeriod.MONTHLY:
                    predicted_cost = future_daily_cost * 30
                elif period == BudgetPeriod.YEARLY:
                    predicted_cost = future_daily_cost * 365
                else:  # HOURLY
                    predicted_cost = future_daily_cost / 24
                
                # Calculate confidence interval (simplified)
                std_dev = statistics.stdev(costs) if len(costs) > 1 else 0
                confidence_interval = (
                    max(0, predicted_cost - std_dev * 2),
                    predicted_cost + std_dev * 2
                )
                
                # Determine trend direction
                if slope > 0.1:
                    trend_direction = "increasing"
                elif slope < -0.1:
                    trend_direction = "decreasing"
                else:
                    trend_direction = "stable"
                
                # Calculate prediction accuracy (based on recent predictions)
                prediction_accuracy = 0.8  # Placeholder - would calculate based on historical accuracy
                
                # Generate factors and recommendations
                factors = {
                    "historical_average": statistics.mean(costs),
                    "trend_slope": slope,
                    "volatility": std_dev,
                    "data_points": len(costs)
                }
                
                recommendations = []
                if trend_direction == "increasing":
                    recommendations.append("Consider cost optimization strategies")
                    recommendations.append("Review high-cost providers and models")
                elif predicted_cost > statistics.mean(costs) * 1.5:
                    recommendations.append("Predicted costs are significantly higher than average")
                    recommendations.append("Implement budget alerts and monitoring")
                
                return CostPrediction(
                    period=period,
                    predicted_cost=predicted_cost,
                    confidence_interval=confidence_interval,
                    prediction_accuracy=prediction_accuracy,
                    trend_direction=trend_direction,
                    factors=factors,
                    recommendations=recommendations
                )
            
            else:
                # Insufficient data for trend analysis, use simple average
                avg_daily_cost = statistics.mean(costs)
                
                if period == BudgetPeriod.DAILY:
                    predicted_cost = avg_daily_cost
                elif period == BudgetPeriod.WEEKLY:
                    predicted_cost = avg_daily_cost * 7
                elif period == BudgetPeriod.MONTHLY:
                    predicted_cost = avg_daily_cost * 30
                elif period == BudgetPeriod.YEARLY:
                    predicted_cost = avg_daily_cost * 365
                else:  # HOURLY
                    predicted_cost = avg_daily_cost / 24
                
                return CostPrediction(
                    period=period,
                    predicted_cost=predicted_cost,
                    confidence_interval=(predicted_cost * 0.5, predicted_cost * 1.5),
                    prediction_accuracy=0.6,
                    trend_direction="stable",
                    factors={"historical_average": avg_daily_cost, "data_points": len(costs)},
                    recommendations=["Collect more data for better predictions"]
                )
        
        except Exception as e:
            logger.error(f"Cost prediction failed: {str(e)}")
            return CostPrediction(
                period=period,
                predicted_cost=0.0,
                confidence_interval=(0.0, 0.0),
                prediction_accuracy=0.0,
                trend_direction="unknown",
                factors={},
                recommendations=[f"Prediction error: {str(e)}"]
            )


class AICostOptimizer:
    """Main AI cost optimization system."""
    
    def __init__(self, redis_url -> None: str = None) -> None:
        self.cost_tracker = CostTracker(redis_url)
        self.cost_optimizer = CostOptimizer(self.cost_tracker)
        
        # Optimization metrics
        self.optimization_counter = Counter('ai_cost_optimizations_total', 'Total cost optimizations', ['type'])
        self.savings_gauge = Gauge('ai_cost_savings_total', 'Total cost savings', ['period'])
    
    async def initialize(self) -> None:
        """Initialize the cost optimization system."""
        await self.cost_tracker.initialize()
        logger.info("AI cost optimizer initialized successfully")
    
    async def record_ai_usage(self, **kwargs) -> CostRecord:
        """Record AI usage and cost."""
        return await self.cost_tracker.record_cost(**kwargs)
    
    async def optimize_costs(self, strategy: CostOptimizationStrategy = CostOptimizationStrategy.BALANCED) -> List[OptimizationRecommendation]:
        """Generate cost optimization recommendations."""
        recommendations = await self.cost_optimizer.optimize_costs(strategy)
        
        # Update metrics
        for rec in recommendations:
            self.optimization_counter.labels(type=rec.type).inc()
        
        return recommendations
    
    async def predict_costs(self, period: BudgetPeriod, horizon_days: int = 30) -> CostPrediction:
        """Predict future costs."""
        return await self.cost_optimizer.predict_costs(period, horizon_days)
    
    async def create_budget(self, **kwargs) -> str:
        """Create a budget limit."""
        return await self.cost_tracker.create_budget_limit(**kwargs)
    
    async def get_cost_summary(self, period: BudgetPeriod = BudgetPeriod.DAILY) -> Dict[str, Any]:
        """Get comprehensive cost summary."""
        now = datetime.utcnow()
        
        # Calculate period start
        if period == BudgetPeriod.DAILY:
            period_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == BudgetPeriod.WEEKLY:
            days_since_monday = now.weekday()
            period_start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == BudgetPeriod.MONTHLY:
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            period_start = now - timedelta(hours=1)
        
        # Filter records for period
        period_records = [r for r in self.cost_tracker.cost_records if r.timestamp >= period_start]
        
        if not period_records:
            return {
                "period": period.value,
                "total_cost": 0.0,
                "total_requests": 0,
                "total_tokens": 0,
                "average_cost_per_request": 0.0,
                "cost_by_provider": {},
                "cost_by_model": {},
                "cost_efficiency": 0.0,
                "budget_status": {}
            }
        
        # Calculate summary
        total_cost = sum(r.total_cost for r in period_records)
        total_requests = len(period_records)
        total_tokens = sum(r.total_tokens for r in period_records)
        avg_cost_per_request = total_cost / total_requests if total_requests > 0 else 0
        avg_cost_efficiency = statistics.mean(r.cost_efficiency for r in period_records)
        
        # Group by provider and model
        cost_by_provider = defaultdict(float)
        cost_by_model = defaultdict(float)
        
        for record in period_records:
            cost_by_provider[record.provider] += record.total_cost
            cost_by_model[f"{record.provider}_{record.model}"] += record.total_cost
        
        # Budget status
        budget_status = {}
        for budget_id, budget in self.cost_tracker.budget_limits.items():
            if budget.period == period:
                usage_percentage = budget.current_usage / budget.limit_amount if budget.limit_amount > 0 else 0
                budget_status[budget.name] = {
                    "current_usage": budget.current_usage,
                    "limit_amount": budget.limit_amount,
                    "usage_percentage": usage_percentage,
                    "status": "exceeded" if usage_percentage >= 1.0 else "warning" if usage_percentage >= 0.8 else "ok"
                }
        
        return {
            "period": period.value,
            "period_start": period_start.isoformat(),
            "total_cost": total_cost,
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "average_cost_per_request": avg_cost_per_request,
            "cost_by_provider": dict(cost_by_provider),
            "cost_by_model": dict(cost_by_model),
            "cost_efficiency": avg_cost_efficiency,
            "budget_status": budget_status
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.cost_tracker.redis_client:
            self.cost_tracker.redis_client.close()
            await self.cost_tracker.redis_client.wait_closed()


# Global cost optimizer instance
cost_optimizer = AICostOptimizer()


async def record_ai_cost(**kwargs) -> CostRecord:
    """Record AI cost using global optimizer."""
    return await cost_optimizer.record_ai_usage(**kwargs)


async def get_cost_optimization_recommendations(strategy: CostOptimizationStrategy = CostOptimizationStrategy.BALANCED) -> List[OptimizationRecommendation]:
    """Get cost optimization recommendations."""
    return await cost_optimizer.optimize_costs(strategy)


# Example usage
async def main() -> None:
    """Example usage of AI cost optimizer."""
    await cost_optimizer.initialize()
    
    # Record some example costs
    await cost_optimizer.record_ai_usage(
        provider="openai",
        model="gpt-4",
        service_type="text_generation",
        request_id="test-1",
        input_tokens=100,
        output_tokens=200,
        processing_time_ms=2000,
        base_cost=0.006,
        quality_score=0.95
    )
    
    # Create a budget
    budget_id = await cost_optimizer.create_budget(
        name="OpenAI Monthly Budget",
        period=BudgetPeriod.MONTHLY,
        limit_amount=100.0,
        alert_thresholds=[0.5, 0.8, 0.9],
        scope={"provider": "openai"}
    )
    
    # Get cost summary
    summary = await cost_optimizer.get_cost_summary(BudgetPeriod.DAILY)
    print(f"Daily cost summary: ${summary['total_cost']:.2f}")
    
    # Get optimization recommendations
    recommendations = await cost_optimizer.optimize_costs(CostOptimizationStrategy.COST_OPTIMIZED)
    for rec in recommendations:
        print(f"Recommendation: {rec.description} - Potential savings: ${rec.potential_savings:.2f}")
    
    # Predict costs
    prediction = await cost_optimizer.predict_costs(BudgetPeriod.MONTHLY)
    print(f"Predicted monthly cost: ${prediction.predicted_cost:.2f}")


if __name__ == "__main__":
    asyncio.run(main())