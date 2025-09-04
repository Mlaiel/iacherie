"""Performance Optimization - IA Influencer Agent Platform
========================================================

Consolidated performance optimization for revenue, content delivery, 
system performance, and business process efficiency.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
import statistics
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from collections import defaultdict

# Optional import for advanced optimization calculations
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of optimization."""
    REVENUE_OPTIMIZATION = "revenue_optimization"
    CONTENT_OPTIMIZATION = "content_optimization"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    PROCESS_OPTIMIZATION = "process_optimization"
    RESOURCE_OPTIMIZATION = "resource_optimization"
    USER_EXPERIENCE = "user_experience"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"
    COST_OPTIMIZATION = "cost_optimization"


class OptimizationStatus(Enum):
    """Optimization status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OptimizationPriority(Enum):
    """Optimization priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class OptimizationMetric:
    """Optimization metric definition."""
    metric_id: str
    name: str
    current_value: float
    target_value: float
    unit: str
    improvement_percentage: float = 0.0
    baseline_value: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationStrategy:
    """Optimization strategy definition."""
    strategy_id: str
    name: str
    optimization_type: OptimizationType
    description: str
    target_metrics: List[str]
    actions: List[Dict[str, Any]]
    expected_improvement: float
    implementation_cost: float
    priority: OptimizationPriority
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationJob:
    """Optimization job execution record."""
    job_id: str
    strategy_id: str
    status: OptimizationStatus
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    results: Dict[str, Any] = field(default_factory=dict)
    metrics_before: Dict[str, float] = field(default_factory=dict)
    metrics_after: Dict[str, float] = field(default_factory=dict)
    error_details: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceOptimizer:
    """
    Consolidated performance optimization engine for the IA Influencer platform.
    
    Provides optimization for revenue, content delivery, system performance,
    business processes, and overall platform efficiency.
    """
    
    def __init__(self):
        """Initialize the performance optimizer."""
        self.optimization_strategies: Dict[str, OptimizationStrategy] = {}
        self.optimization_jobs: Dict[str, OptimizationJob] = {}
        self.metrics: Dict[str, OptimizationMetric] = {}
        self.optimization_history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(__name__)
        self._load_default_strategies()
        self._initialize_metrics()
    
    def _load_default_strategies(self):
        """Load default optimization strategies."""
        default_strategies = [
            # Revenue Optimization
            OptimizationStrategy(
                strategy_id="revenue_pricing_optimization",
                name="Revenue Pricing Optimization",
                optimization_type=OptimizationType.REVENUE_OPTIMIZATION,
                description="Optimize pricing strategies to maximize revenue",
                target_metrics=["revenue_per_user", "conversion_rate"],
                actions=[
                    {"type": "dynamic_pricing", "parameters": {"algorithm": "demand_based"}},
                    {"type": "a_b_testing", "parameters": {"variants": ["current", "premium_10%", "discount_5%"]}},
                    {"type": "personalized_pricing", "parameters": {"segmentation": "user_behavior"}}
                ],
                expected_improvement=15.0,
                implementation_cost=5000.0,
                priority=OptimizationPriority.HIGH
            ),
            
            # Content Optimization
            OptimizationStrategy(
                strategy_id="content_delivery_optimization",
                name="Content Delivery Optimization",
                optimization_type=OptimizationType.CONTENT_OPTIMIZATION,
                description="Optimize content delivery and caching strategies",
                target_metrics=["content_load_time", "cache_hit_ratio"],
                actions=[
                    {"type": "cdn_optimization", "parameters": {"regions": "global"}},
                    {"type": "caching_strategy", "parameters": {"ttl": "adaptive"}},
                    {"type": "compression", "parameters": {"algorithm": "brotli"}}
                ],
                expected_improvement=25.0,
                implementation_cost=3000.0,
                priority=OptimizationPriority.HIGH
            ),
            
            # Performance Optimization
            OptimizationStrategy(
                strategy_id="database_optimization",
                name="Database Performance Optimization",
                optimization_type=OptimizationType.PERFORMANCE_OPTIMIZATION,
                description="Optimize database queries and indexing",
                target_metrics=["query_response_time", "database_cpu_usage"],
                actions=[
                    {"type": "index_optimization", "parameters": {"analyze_slow_queries": True}},
                    {"type": "query_optimization", "parameters": {"enable_hints": True}},
                    {"type": "connection_pooling", "parameters": {"pool_size": "adaptive"}}
                ],
                expected_improvement=30.0,
                implementation_cost=2000.0,
                priority=OptimizationPriority.CRITICAL
            ),
            
            # Process Optimization
            OptimizationStrategy(
                strategy_id="workflow_automation_optimization",
                name="Workflow Automation Optimization",
                optimization_type=OptimizationType.PROCESS_OPTIMIZATION,
                description="Optimize business process automation",
                target_metrics=["process_completion_time", "automation_success_rate"],
                actions=[
                    {"type": "workflow_analysis", "parameters": {"identify_bottlenecks": True}},
                    {"type": "automation_enhancement", "parameters": {"ai_assistance": True}},
                    {"type": "parallel_processing", "parameters": {"concurrent_tasks": 5}}
                ],
                expected_improvement=20.0,
                implementation_cost=4000.0,
                priority=OptimizationPriority.MEDIUM
            ),
            
            # User Experience Optimization
            OptimizationStrategy(
                strategy_id="ux_optimization",
                name="User Experience Optimization",
                optimization_type=OptimizationType.USER_EXPERIENCE,
                description="Optimize user interface and experience",
                target_metrics=["user_engagement_rate", "session_duration"],
                actions=[
                    {"type": "ui_optimization", "parameters": {"responsive_design": True}},
                    {"type": "personalization", "parameters": {"recommendation_engine": "collaborative_filtering"}},
                    {"type": "performance_tuning", "parameters": {"lazy_loading": True}}
                ],
                expected_improvement=18.0,
                implementation_cost=6000.0,
                priority=OptimizationPriority.MEDIUM
            ),
            
            # Cost Optimization
            OptimizationStrategy(
                strategy_id="cost_optimization",
                name="Infrastructure Cost Optimization",
                optimization_type=OptimizationType.COST_OPTIMIZATION,
                description="Optimize infrastructure and operational costs",
                target_metrics=["cost_per_user", "infrastructure_efficiency"],
                actions=[
                    {"type": "resource_scaling", "parameters": {"auto_scaling": True}},
                    {"type": "cost_analysis", "parameters": {"unused_resources": "cleanup"}},
                    {"type": "vendor_optimization", "parameters": {"negotiate_rates": True}}
                ],
                expected_improvement=12.0,
                implementation_cost=1500.0,
                priority=OptimizationPriority.HIGH
            )
        ]
        
        for strategy in default_strategies:
            self.add_optimization_strategy(strategy)
    
    def _initialize_metrics(self):
        """Initialize optimization metrics."""
        metrics = [
            OptimizationMetric(
                metric_id="revenue_per_user",
                name="Revenue per User",
                current_value=45.0,
                target_value=60.0,
                unit="USD",
                baseline_value=40.0
            ),
            OptimizationMetric(
                metric_id="conversion_rate",
                name="Conversion Rate",
                current_value=0.12,
                target_value=0.18,
                unit="percentage",
                baseline_value=0.10
            ),
            OptimizationMetric(
                metric_id="content_load_time",
                name="Content Load Time",
                current_value=2.5,
                target_value=1.5,
                unit="seconds",
                baseline_value=3.0
            ),
            OptimizationMetric(
                metric_id="cache_hit_ratio",
                name="Cache Hit Ratio",
                current_value=0.75,
                target_value=0.90,
                unit="percentage",
                baseline_value=0.70
            ),
            OptimizationMetric(
                metric_id="query_response_time",
                name="Database Query Response Time",
                current_value=150.0,
                target_value=80.0,
                unit="milliseconds",
                baseline_value=200.0
            ),
            OptimizationMetric(
                metric_id="database_cpu_usage",
                name="Database CPU Usage",
                current_value=0.65,
                target_value=0.45,
                unit="percentage",
                baseline_value=0.75
            ),
            OptimizationMetric(
                metric_id="process_completion_time",
                name="Process Completion Time",
                current_value=300.0,
                target_value=180.0,
                unit="seconds",
                baseline_value=360.0
            ),
            OptimizationMetric(
                metric_id="automation_success_rate",
                name="Automation Success Rate",
                current_value=0.88,
                target_value=0.95,
                unit="percentage",
                baseline_value=0.85
            ),
            OptimizationMetric(
                metric_id="user_engagement_rate",
                name="User Engagement Rate",
                current_value=0.16,
                target_value=0.25,
                unit="percentage",
                baseline_value=0.14
            ),
            OptimizationMetric(
                metric_id="session_duration",
                name="Average Session Duration",
                current_value=420.0,
                target_value=600.0,
                unit="seconds",
                baseline_value=380.0
            ),
            OptimizationMetric(
                metric_id="cost_per_user",
                name="Cost per User",
                current_value=12.0,
                target_value=8.0,
                unit="USD",
                baseline_value=15.0
            ),
            OptimizationMetric(
                metric_id="infrastructure_efficiency",
                name="Infrastructure Efficiency",
                current_value=0.72,
                target_value=0.85,
                unit="percentage",
                baseline_value=0.68
            )
        ]
        
        for metric in metrics:
            self.metrics[metric.metric_id] = metric
    
    def add_optimization_strategy(self, strategy: OptimizationStrategy) -> str:
        """Add an optimization strategy."""
        try:
            self.optimization_strategies[strategy.strategy_id] = strategy
            self.logger.info(f"Added optimization strategy: {strategy.name} ({strategy.strategy_id})")
            return strategy.strategy_id
        except Exception as e:
            self.logger.error(f"Failed to add optimization strategy {strategy.strategy_id}: {str(e)}")
            raise
    
    async def start_optimization(self, strategy_id: str, custom_parameters: Optional[Dict[str, Any]] = None) -> str:
        """Start an optimization job."""
        try:
            if strategy_id not in self.optimization_strategies:
                raise ValueError(f"Optimization strategy {strategy_id} not found")
            
            strategy = self.optimization_strategies[strategy_id]
            
            # Create optimization job
            job = OptimizationJob(
                job_id=str(uuid.uuid4()),
                strategy_id=strategy_id,
                status=OptimizationStatus.PENDING
            )
            
            # Record baseline metrics
            for metric_id in strategy.target_metrics:
                if metric_id in self.metrics:
                    job.metrics_before[metric_id] = self.metrics[metric_id].current_value
            
            self.optimization_jobs[job.job_id] = job
            
            # Start optimization asynchronously
            asyncio.create_task(self._run_optimization_job(job.job_id, custom_parameters))
            
            self.logger.info(f"Started optimization job: {strategy.name} ({job.job_id})")
            return job.job_id
            
        except Exception as e:
            self.logger.error(f"Error starting optimization {strategy_id}: {str(e)}")
            raise
    
    async def _run_optimization_job(self, job_id: str, custom_parameters: Optional[Dict[str, Any]] = None) -> None:
        """Run an optimization job."""
        try:
            job = self.optimization_jobs[job_id]
            strategy = self.optimization_strategies[job.strategy_id]
            
            job.status = OptimizationStatus.RUNNING
            
            # Execute optimization actions
            total_actions = len(strategy.actions)
            
            for i, action in enumerate(strategy.actions):
                job.progress = (i / total_actions) * 100
                
                result = await self._execute_optimization_action(action, custom_parameters)
                job.results[f"action_{i}"] = result
                
                # Simulate some processing time
                await asyncio.sleep(0.5)
            
            # Simulate optimization completion and metric updates
            await self._apply_optimization_results(job, strategy)
            
            job.status = OptimizationStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.progress = 100.0
            
            # Record final metrics
            for metric_id in strategy.target_metrics:
                if metric_id in self.metrics:
                    job.metrics_after[metric_id] = self.metrics[metric_id].current_value
            
            # Add to history
            self.optimization_history.append({
                "job_id": job_id,
                "strategy_id": strategy.strategy_id,
                "strategy_name": strategy.name,
                "optimization_type": strategy.optimization_type.value,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "improvement_achieved": self._calculate_improvement(job, strategy),
                "success": True
            })
            
            self.logger.info(f"Completed optimization job: {job_id}")
            
        except Exception as e:
            job.status = OptimizationStatus.FAILED
            job.error_details = str(e)
            job.completed_at = datetime.utcnow()
            
            self.optimization_history.append({
                "job_id": job_id,
                "strategy_id": strategy.strategy_id if 'strategy' in locals() else None,
                "completed_at": job.completed_at.isoformat(),
                "success": False,
                "error": str(e)
            })
            
            self.logger.error(f"Optimization job failed: {job_id} - {str(e)}")
    
    async def _execute_optimization_action(self, action: Dict[str, Any], custom_parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a specific optimization action."""
        try:
            action_type = action.get("type")
            parameters = action.get("parameters", {})
            
            if custom_parameters:
                parameters.update(custom_parameters)
            
            self.logger.info(f"Executing optimization action: {action_type}")
            
            # Simulate action execution
            if action_type == "dynamic_pricing":
                return {
                    "action": action_type,
                    "algorithm": parameters.get("algorithm", "demand_based"),
                    "pricing_model_updated": True,
                    "estimated_revenue_increase": 8.5
                }
            
            elif action_type == "cdn_optimization":
                return {
                    "action": action_type,
                    "regions_optimized": parameters.get("regions", "global"),
                    "cache_policies_updated": True,
                    "estimated_speed_improvement": 35.0
                }
            
            elif action_type == "index_optimization":
                return {
                    "action": action_type,
                    "indexes_created": 5,
                    "slow_queries_optimized": 12,
                    "estimated_performance_gain": 40.0
                }
            
            elif action_type == "workflow_analysis":
                return {
                    "action": action_type,
                    "bottlenecks_identified": 3,
                    "optimization_opportunities": 7,
                    "estimated_time_savings": 25.0
                }
            
            elif action_type == "ui_optimization":
                return {
                    "action": action_type,
                    "components_optimized": 15,
                    "performance_score_improvement": 22.0,
                    "user_experience_rating": 4.2
                }
            
            elif action_type == "resource_scaling":
                return {
                    "action": action_type,
                    "auto_scaling_enabled": True,
                    "cost_savings": 15.0,
                    "efficiency_improvement": 18.0
                }
            
            else:
                return {
                    "action": action_type,
                    "status": "completed",
                    "parameters": parameters
                }
                
        except Exception as e:
            self.logger.error(f"Error executing optimization action {action_type}: {str(e)}")
            return {
                "action": action_type,
                "status": "failed",
                "error": str(e)
            }
    
    async def _apply_optimization_results(self, job: OptimizationJob, strategy: OptimizationStrategy) -> None:
        """Apply optimization results to metrics."""
        try:
            # Simulate metric improvements based on strategy expectations
            improvement_factor = strategy.expected_improvement / 100.0
            
            for metric_id in strategy.target_metrics:
                if metric_id in self.metrics:
                    metric = self.metrics[metric_id]
                    
                    # Calculate improvement based on strategy type
                    import random
                    if strategy.optimization_type == OptimizationType.REVENUE_OPTIMIZATION:
                        if "revenue" in metric_id or "conversion" in metric_id:
                            # For revenue metrics, increase is good
                            improvement = metric.current_value * improvement_factor * random.uniform(0.7, 1.3)
                            metric.current_value = min(metric.target_value, metric.current_value + improvement)
                    
                    elif strategy.optimization_type == OptimizationType.PERFORMANCE_OPTIMIZATION:
                        if "time" in metric_id or "usage" in metric_id:
                            # For time/usage metrics, decrease is good
                            improvement = metric.current_value * improvement_factor * random.uniform(0.7, 1.3)
                            metric.current_value = max(metric.target_value, metric.current_value - improvement)
                        else:
                            # For ratio/rate metrics, increase is good
                            improvement = metric.current_value * improvement_factor * random.uniform(0.7, 1.3)
                            metric.current_value = min(metric.target_value, metric.current_value + improvement)
                    
                    elif strategy.optimization_type == OptimizationType.COST_OPTIMIZATION:
                        if "cost" in metric_id:
                            # For cost metrics, decrease is good
                            improvement = metric.current_value * improvement_factor * random.uniform(0.7, 1.3)
                            metric.current_value = max(metric.target_value, metric.current_value - improvement)
                        else:
                            # For efficiency metrics, increase is good
                            improvement = metric.current_value * improvement_factor * random.uniform(0.7, 1.3)
                            metric.current_value = min(metric.target_value, metric.current_value + improvement)
                    
                    else:
                        # Default: assume increase is good
                        improvement = metric.current_value * improvement_factor * random.uniform(0.7, 1.3)
                        metric.current_value = min(metric.target_value, metric.current_value + improvement)
                    
                    # Calculate improvement percentage
                    if metric.baseline_value and metric.baseline_value != 0:
                        metric.improvement_percentage = ((metric.current_value - metric.baseline_value) / metric.baseline_value) * 100
            
        except Exception as e:
            self.logger.error(f"Error applying optimization results: {str(e)}")
    
    def _calculate_improvement(self, job: OptimizationJob, strategy: OptimizationStrategy) -> Dict[str, float]:
        """Calculate improvement achieved by optimization."""
        improvements = {}
        
        for metric_id in strategy.target_metrics:
            if metric_id in job.metrics_before and metric_id in job.metrics_after:
                before = job.metrics_before[metric_id]
                after = job.metrics_after[metric_id]
                
                if before != 0:
                    improvement_pct = ((after - before) / before) * 100
                    improvements[metric_id] = round(improvement_pct, 2)
        
        return improvements
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations based on current metrics."""
        try:
            recommendations = []
            
            for metric_id, metric in self.metrics.items():
                if metric.current_value < metric.target_value * 0.8:  # If current is less than 80% of target
                    # Find strategies that target this metric
                    relevant_strategies = [
                        s for s in self.optimization_strategies.values()
                        if metric_id in s.target_metrics
                    ]
                    
                    if relevant_strategies:
                        # Recommend the highest priority strategy
                        best_strategy = min(relevant_strategies, key=lambda s: s.priority.value)
                        
                        recommendations.append({
                            "metric_id": metric_id,
                            "metric_name": metric.name,
                            "current_value": metric.current_value,
                            "target_value": metric.target_value,
                            "gap_percentage": ((metric.target_value - metric.current_value) / metric.target_value) * 100,
                            "recommended_strategy": {
                                "strategy_id": best_strategy.strategy_id,
                                "name": best_strategy.name,
                                "expected_improvement": best_strategy.expected_improvement,
                                "implementation_cost": best_strategy.implementation_cost,
                                "priority": best_strategy.priority.value
                            }
                        })
            
            # Sort by gap percentage (highest gaps first)
            recommendations.sort(key=lambda r: r["gap_percentage"], reverse=True)
            
            return recommendations[:10]  # Return top 10 recommendations
            
        except Exception as e:
            self.logger.error(f"Error getting optimization recommendations: {str(e)}")
            return []
    
    async def get_optimization_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive optimization dashboard."""
        try:
            # Calculate overall performance score
            total_score = 0
            scored_metrics = 0
            
            for metric in self.metrics.values():
                if metric.target_value != 0:
                    score = min(100, (metric.current_value / metric.target_value) * 100)
                    total_score += score
                    scored_metrics += 1
            
            overall_score = total_score / scored_metrics if scored_metrics > 0 else 0
            
            # Get recent optimization jobs
            recent_jobs = sorted(
                [job for job in self.optimization_jobs.values() if job.completed_at],
                key=lambda j: j.completed_at,
                reverse=True
            )[:5]
            
            # Calculate optimization impact
            total_improvement = 0
            successful_optimizations = 0
            
            for history_item in self.optimization_history:
                if history_item.get("success") and "improvement_achieved" in history_item:
                    improvements = history_item["improvement_achieved"]
                    if improvements:
                        avg_improvement = sum(improvements.values()) / len(improvements)
                        total_improvement += avg_improvement
                        successful_optimizations += 1
            
            avg_improvement = total_improvement / successful_optimizations if successful_optimizations > 0 else 0
            
            return {
                "overall_performance_score": round(overall_score, 1),
                "metrics_summary": {
                    "total_metrics": len(self.metrics),
                    "metrics_on_target": len([m for m in self.metrics.values() if m.current_value >= m.target_value * 0.95]),
                    "metrics_needing_attention": len([m for m in self.metrics.values() if m.current_value < m.target_value * 0.8])
                },
                "optimization_activity": {
                    "total_strategies": len(self.optimization_strategies),
                    "completed_optimizations": len([j for j in self.optimization_jobs.values() if j.status == OptimizationStatus.COMPLETED]),
                    "running_optimizations": len([j for j in self.optimization_jobs.values() if j.status == OptimizationStatus.RUNNING]),
                    "average_improvement": round(avg_improvement, 2)
                },
                "key_metrics": [
                    {
                        "metric_id": metric.metric_id,
                        "name": metric.name,
                        "current_value": metric.current_value,
                        "target_value": metric.target_value,
                        "progress_percentage": min(100, (metric.current_value / metric.target_value) * 100) if metric.target_value != 0 else 0,
                        "improvement_percentage": metric.improvement_percentage
                    } for metric in list(self.metrics.values())[:6]
                ],
                "recent_optimizations": [
                    {
                        "job_id": job.job_id,
                        "strategy_name": self.optimization_strategies[job.strategy_id].name,
                        "status": job.status.value,
                        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                        "improvement": self._calculate_improvement(job, self.optimization_strategies[job.strategy_id])
                    } for job in recent_jobs
                ],
                "recommendations": await self.get_optimization_recommendations(),
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting optimization dashboard: {str(e)}")
            return {"error": str(e)}
    
    async def get_optimization_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific optimization job."""
        try:
            if job_id not in self.optimization_jobs:
                return None
            
            job = self.optimization_jobs[job_id]
            strategy = self.optimization_strategies[job.strategy_id]
            
            return {
                "job_id": job_id,
                "strategy_name": strategy.name,
                "optimization_type": strategy.optimization_type.value,
                "status": job.status.value,
                "progress": job.progress,
                "started_at": job.started_at.isoformat(),
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "target_metrics": strategy.target_metrics,
                "metrics_before": job.metrics_before,
                "metrics_after": job.metrics_after,
                "improvement": self._calculate_improvement(job, strategy) if job.status == OptimizationStatus.COMPLETED else {},
                "error_details": job.error_details
            }
            
        except Exception as e:
            self.logger.error(f"Error getting optimization status: {str(e)}")
            return None
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of optimization system."""
        try:
            return {
                "total_strategies": len(self.optimization_strategies),
                "total_metrics": len(self.metrics),
                "total_jobs": len(self.optimization_jobs),
                "optimization_types": [ot.value for ot in OptimizationType],
                "priority_levels": [op.value for op in OptimizationPriority],
                "strategies_by_type": {
                    ot.value: len([s for s in self.optimization_strategies.values() if s.optimization_type == ot])
                    for ot in OptimizationType
                },
                "jobs_by_status": {
                    status.value: len([j for j in self.optimization_jobs.values() if j.status == status])
                    for status in OptimizationStatus
                },
                "total_optimization_history": len(self.optimization_history),
                "successful_optimizations": len([h for h in self.optimization_history if h.get("success")])
            }
        except Exception as e:
            self.logger.error(f"Error getting optimization summary: {str(e)}")
            return {}