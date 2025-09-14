"""
🏗️ Ainflue Infrastructure - Cloud Cost Optimizer
Cross-cloud cost optimization and intelligent resource management.

Created by: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Contact mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import statistics
from enum import Enum
import numpy as np

from ..cloud.aws_provider import AWSProvider
from ..cloud.gcp_provider import GCPProvider
from ..cloud.azure_provider import AzureProvider


class OptimizationStrategy(Enum):
    """Cost optimization strategies."""
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    CUSTOM = "custom"


class ResourceType(Enum):
    """Types of cloud resources."""
    COMPUTE = "compute"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE = "database"
    AI_ML = "ai_ml"
    CONTAINERS = "containers"


@dataclass
class CostThreshold:
    """Cost threshold configuration."""
    resource_type: ResourceType
    daily_limit: float
    monthly_limit: float
    alert_percentage: float = 80.0
    auto_scale_down: bool = False


@dataclass
class OptimizationRule:
    """Cost optimization rule."""
    name: str
    resource_type: ResourceType
    condition: str
    action: str
    savings_estimate: float
    risk_level: str  # low, medium, high


@dataclass
class CostReport:
    """Cost analysis report."""
    period: str
    total_cost: float
    cost_by_cloud: Dict[str, float]
    cost_by_service: Dict[str, float]
    cost_trends: Dict[str, List[float]]
    optimization_opportunities: List[Dict[str, Any]]
    savings_potential: float


class CloudCostOptimizer:
    """
    Enterprise cloud cost optimization system.
    
    Provides intelligent cost monitoring, analysis, and optimization
    across multiple cloud providers for the Ainflue platform.
    """

    def __init__(self, optimization_strategy -> None: OptimizationStrategy = OptimizationStrategy.BALANCED) -> None:
        """Initialize cloud cost optimizer."""
        self.strategy = optimization_strategy
        self.logger = logging.getLogger(__name__)
        
        # Cloud providers
        self.providers = {
            'aws': AWSProvider(),
            'gcp': GCPProvider(),
            'azure': AzureProvider()
        }
        
        # Cost tracking
        self.cost_data: Dict[str, Dict[str, Any]] = {}
        self.thresholds: Dict[str, CostThreshold] = {}
        self.optimization_rules: List[OptimizationRule] = []
        
        # Performance tracking
        self.optimization_history: List[Dict[str, Any]] = []
        self.savings_achieved: Dict[str, float] = {}
        
        # Initialize default rules and thresholds
        self._initialize_default_rules()
        self._initialize_default_thresholds()
        
        self.logger.info("CloudCostOptimizer initialized successfully")

    def _initialize_default_rules(self) -> None:
        """Initialize default optimization rules."""
        try:
            default_rules = [
                OptimizationRule(
                    name="idle_compute_instances",
                    resource_type=ResourceType.COMPUTE,
                    condition="cpu_utilization < 5% for 24 hours",
                    action="stop_or_downsize",
                    savings_estimate=0.7,
                    risk_level="low"
                ),
                OptimizationRule(
                    name="oversized_instances",
                    resource_type=ResourceType.COMPUTE,
                    condition="cpu_utilization < 20% and memory_utilization < 30%",
                    action="downsize_instance",
                    savings_estimate=0.4,
                    risk_level="medium"
                ),
                OptimizationRule(
                    name="unattached_storage",
                    resource_type=ResourceType.STORAGE,
                    condition="storage_attached = false for 7 days",
                    action="delete_volume",
                    savings_estimate=1.0,
                    risk_level="low"
                ),
                OptimizationRule(
                    name="reserved_instance_opportunity",
                    resource_type=ResourceType.COMPUTE,
                    condition="consistent_usage > 75% for 30 days",
                    action="purchase_reserved_instance",
                    savings_estimate=0.3,
                    risk_level="low"
                ),
                OptimizationRule(
                    name="spot_instance_opportunity",
                    resource_type=ResourceType.COMPUTE,
                    condition="workload_interruption_tolerant = true",
                    action="migrate_to_spot",
                    savings_estimate=0.6,
                    risk_level="medium"
                )
            ]
            
            self.optimization_rules.extend(default_rules)
            self.logger.info(f"Initialized {len(default_rules)} default optimization rules")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize default rules: {e}")

    def _initialize_default_thresholds(self) -> None:
        """Initialize default cost thresholds."""
        try:
            default_thresholds = {
                'compute': CostThreshold(
                    resource_type=ResourceType.COMPUTE,
                    daily_limit=1000.0,
                    monthly_limit=25000.0,
                    alert_percentage=80.0,
                    auto_scale_down=True
                ),
                'storage': CostThreshold(
                    resource_type=ResourceType.STORAGE,
                    daily_limit=200.0,
                    monthly_limit=5000.0,
                    alert_percentage=85.0
                ),
                'network': CostThreshold(
                    resource_type=ResourceType.NETWORK,
                    daily_limit=150.0,
                    monthly_limit=3000.0,
                    alert_percentage=90.0
                ),
                'ai_ml': CostThreshold(
                    resource_type=ResourceType.AI_ML,
                    daily_limit=500.0,
                    monthly_limit=12000.0,
                    alert_percentage=75.0,
                    auto_scale_down=True
                )
            }
            
            self.thresholds.update(default_thresholds)
            self.logger.info(f"Initialized {len(default_thresholds)} default cost thresholds")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize default thresholds: {e}")

    async def analyze_costs(self, time_period: str = "30d") -> CostReport:
        """Perform comprehensive cost analysis across all clouds."""
        try:
            self.logger.info(f"Starting cost analysis for period: {time_period}")
            
            # Collect cost data from all providers
            cost_data = await self._collect_cost_data(time_period)
            
            # Analyze cost trends
            cost_trends = await self._analyze_cost_trends(cost_data, time_period)
            
            # Identify optimization opportunities
            opportunities = await self._identify_optimization_opportunities(cost_data)
            
            # Calculate savings potential
            savings_potential = sum(opp['estimated_savings'] for opp in opportunities)
            
            # Generate cost report
            report = CostReport(
                period=time_period,
                total_cost=sum(cost_data.values()),
                cost_by_cloud=cost_data,
                cost_by_service=await self._analyze_cost_by_service(cost_data),
                cost_trends=cost_trends,
                optimization_opportunities=opportunities,
                savings_potential=savings_potential
            )
            
            self.logger.info(f"Cost analysis completed. Total cost: ${report.total_cost:.2f}")
            return report
            
        except Exception as e:
            self.logger.error(f"Cost analysis failed: {e}")
            raise

    async def optimize_costs(self, auto_apply: bool = False) -> Dict[str, Any]:
        """Execute cost optimization based on identified opportunities."""
        try:
            self.logger.info("Starting cost optimization process")
            
            # Get current cost analysis
            report = await self.analyze_costs()
            
            # Filter opportunities based on strategy and risk tolerance
            filtered_opportunities = await self._filter_opportunities_by_strategy(
                report.optimization_opportunities
            )
            
            # Create optimization plan
            optimization_plan = await self._create_optimization_plan(filtered_opportunities)
            
            # Execute optimizations
            optimization_results = {}
            total_savings = 0.0
            
            for opportunity in optimization_plan:
                try:
                    if auto_apply or opportunity['risk_level'] == 'low':
                        result = await self._execute_optimization(opportunity)
                        optimization_results[opportunity['id']] = {
                            'status': 'applied',
                            'action': opportunity['action'],
                            'estimated_savings': opportunity['estimated_savings'],
                            'actual_savings': result.get('actual_savings', 0),
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        total_savings += result.get('actual_savings', 0)
                    else:
                        optimization_results[opportunity['id']] = {
                            'status': 'pending_approval',
                            'action': opportunity['action'],
                            'estimated_savings': opportunity['estimated_savings'],
                            'risk_level': opportunity['risk_level']
                        }
                except Exception as e:
                    optimization_results[opportunity['id']] = {
                        'status': 'failed',
                        'error': str(e),
                        'action': opportunity['action']
                    }
                    self.logger.error(f"Optimization failed for {opportunity['id']}: {e}")
            
            # Record optimization history
            self._record_optimization_history(optimization_results, total_savings)
            
            return {
                'total_opportunities': len(report.optimization_opportunities),
                'applied_optimizations': len([r for r in optimization_results.values() 
                                            if r['status'] == 'applied']),
                'total_savings': total_savings,
                'pending_approvals': len([r for r in optimization_results.values() 
                                        if r['status'] == 'pending_approval']),
                'failed_optimizations': len([r for r in optimization_results.values() 
                                           if r['status'] == 'failed']),
                'details': optimization_results
            }
            
        except Exception as e:
            self.logger.error(f"Cost optimization failed: {e}")
            raise

    async def monitor_cost_thresholds(self) -> Dict[str, Any]:
        """Monitor cost thresholds and trigger alerts/actions."""
        try:
            self.logger.info("Monitoring cost thresholds")
            
            threshold_status = {}
            alerts = []
            actions_taken = []
            
            # Get current costs
            current_costs = await self._get_current_costs()
            
            # Check each threshold
            for threshold_name, threshold in self.thresholds.items():
                try:
                    # Calculate current usage percentage
                    current_cost = current_costs.get(threshold_name, 0)
                    daily_percentage = (current_cost / threshold.daily_limit) * 100
                    
                    # Get monthly costs
                    monthly_cost = await self._get_monthly_cost(threshold_name)
                    monthly_percentage = (monthly_cost / threshold.monthly_limit) * 100
                    
                    threshold_status[threshold_name] = {
                        'daily_usage': daily_percentage,
                        'monthly_usage': monthly_percentage,
                        'current_daily_cost': current_cost,
                        'current_monthly_cost': monthly_cost,
                        'status': 'normal'
                    }
                    
                    # Check for threshold breaches
                    if daily_percentage >= threshold.alert_percentage:
                        alert = {
                            'type': 'daily_threshold_alert',
                            'resource_type': threshold_name,
                            'percentage': daily_percentage,
                            'threshold': threshold.alert_percentage,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        alerts.append(alert)
                        threshold_status[threshold_name]['status'] = 'alert'
                        
                        # Auto-scale if enabled
                        if threshold.auto_scale_down and daily_percentage >= 95:
                            action_result = await self._auto_scale_down(threshold_name)
                            actions_taken.append(action_result)
                    
                    elif monthly_percentage >= threshold.alert_percentage:
                        alert = {
                            'type': 'monthly_threshold_alert',
                            'resource_type': threshold_name,
                            'percentage': monthly_percentage,
                            'threshold': threshold.alert_percentage,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        alerts.append(alert)
                        threshold_status[threshold_name]['status'] = 'warning'
                
                except Exception as e:
                    self.logger.error(f"Threshold monitoring failed for {threshold_name}: {e}")
                    threshold_status[threshold_name] = {'status': 'error', 'error': str(e)}
            
            return {
                'threshold_status': threshold_status,
                'alerts': alerts,
                'actions_taken': actions_taken,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Threshold monitoring failed: {e}")
            raise

    async def predict_costs(self, prediction_period: str = "30d") -> Dict[str, Any]:
        """Predict future costs based on historical data and trends."""
        try:
            self.logger.info(f"Predicting costs for period: {prediction_period}")
            
            # Collect historical data
            historical_data = await self._collect_historical_cost_data()
            
            # Analyze trends
            trends = await self._analyze_cost_trends(historical_data, "90d")
            
            # Generate predictions using trend analysis
            predictions = {}
            
            for cloud, cost_history in historical_data.items():
                try:
                    # Simple linear regression for trend prediction
                    prediction = self._predict_cost_trend(cost_history, prediction_period)
                    predictions[cloud] = {
                        'predicted_cost': prediction['predicted_cost'],
                        'confidence_interval': prediction['confidence_interval'],
                        'trend_direction': prediction['trend_direction'],
                        'monthly_growth_rate': prediction['growth_rate']
                    }
                except Exception as e:
                    self.logger.error(f"Prediction failed for {cloud}: {e}")
                    predictions[cloud] = {'error': str(e)}
            
            # Calculate total predicted cost
            total_predicted = sum(
                pred.get('predicted_cost', 0) for pred in predictions.values()
            )
            
            # Identify cost drivers
            cost_drivers = await self._identify_cost_drivers(historical_data)
            
            # Generate recommendations
            recommendations = await self._generate_cost_recommendations(predictions, cost_drivers)
            
            return {
                'prediction_period': prediction_period,
                'total_predicted_cost': total_predicted,
                'predictions_by_cloud': predictions,
                'cost_drivers': cost_drivers,
                'recommendations': recommendations,
                'confidence_score': self._calculate_prediction_confidence(predictions),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Cost prediction failed: {e}")
            raise

    async def get_cost_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive cost dashboard data."""
        try:
            # Get current costs
            current_costs = await self._get_current_costs()
            
            # Get cost analysis
            cost_report = await self.analyze_costs("30d")
            
            # Get threshold status
            threshold_status = await self.monitor_cost_thresholds()
            
            # Get predictions
            predictions = await self.predict_costs("30d")
            
            # Calculate savings metrics
            savings_metrics = await self._calculate_savings_metrics()
            
            dashboard = {
                'summary': {
                    'current_daily_cost': sum(current_costs.values()),
                    'monthly_cost': cost_report.total_cost,
                    'predicted_next_month': predictions['total_predicted_cost'],
                    'total_savings_achieved': sum(self.savings_achieved.values()),
                    'optimization_opportunities': len(cost_report.optimization_opportunities)
                },
                'cost_breakdown': {
                    'by_cloud': cost_report.cost_by_cloud,
                    'by_service': cost_report.cost_by_service,
                    'trends': cost_report.cost_trends
                },
                'thresholds': threshold_status,
                'optimization': {
                    'opportunities': cost_report.optimization_opportunities[:10],  # Top 10
                    'potential_savings': cost_report.savings_potential,
                    'recent_optimizations': self.optimization_history[-5:]  # Last 5
                },
                'predictions': predictions,
                'savings_metrics': savings_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Dashboard generation failed: {e}")
            raise

    # Private helper methods

    async def _collect_cost_data(self, time_period: str) -> Dict[str, float]:
        """Collect cost data from all cloud providers."""
        try:
            cost_data = {}
            
            for cloud_name, provider in self.providers.items():
                try:
                    cost = await self._get_provider_cost(provider, cloud_name, time_period)
                    cost_data[cloud_name] = cost
                except Exception as e:
                    self.logger.error(f"Failed to get cost data from {cloud_name}: {e}")
                    cost_data[cloud_name] = 0.0
            
            return cost_data
            
        except Exception as e:
            self.logger.error(f"Cost data collection failed: {e}")
            return {}

    async def _get_provider_cost(self, provider, cloud_name: str, time_period: str) -> float:
        """Get cost data from specific provider."""
        # Placeholder implementation - would integrate with actual cloud billing APIs
        # AWS: Cost Explorer API
        # GCP: Cloud Billing API
        # Azure: Consumption API
        
        base_costs = {
            'aws': 5000.0,
            'gcp': 3000.0,
            'azure': 2500.0
        }
        
        # Simulate some variance
        import random
        variance = random.uniform(0.8, 1.2)
        return base_costs.get(cloud_name, 1000.0) * variance

    async def _analyze_cost_trends(self, cost_data: Dict[str, float], 
                                 time_period: str) -> Dict[str, List[float]]:
        """Analyze cost trends over time."""
        try:
            trends = {}
            
            # Simulate historical trend data
            for cloud, current_cost in cost_data.items():
                # Generate 30 days of trend data
                trend_data = []
                base_cost = current_cost
                
                for day in range(30):
                    # Simulate daily variance with slight upward trend
                    daily_cost = base_cost * (0.98 + (day * 0.001)) * (0.9 + random.random() * 0.2)
                    trend_data.append(round(daily_cost, 2))
                
                trends[cloud] = trend_data
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            return {}

    async def _identify_optimization_opportunities(self, 
                                                 cost_data: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify cost optimization opportunities."""
        try:
            opportunities = []
            
            # Simulate resource analysis for each cloud
            for cloud, cost in cost_data.items():
                # Idle instances opportunity
                opportunities.append({
                    'id': f"{cloud}_idle_instances",
                    'type': 'idle_resources',
                    'cloud': cloud,
                    'resource_type': 'compute',
                    'description': f"Idle compute instances in {cloud}",
                    'estimated_savings': cost * 0.15,
                    'risk_level': 'low',
                    'action': 'terminate_idle_instances',
                    'confidence': 0.9
                })
                
                # Oversized instances opportunity
                opportunities.append({
                    'id': f"{cloud}_oversized_instances",
                    'type': 'rightsizing',
                    'cloud': cloud,
                    'resource_type': 'compute',
                    'description': f"Oversized instances in {cloud}",
                    'estimated_savings': cost * 0.08,
                    'risk_level': 'medium',
                    'action': 'rightsize_instances',
                    'confidence': 0.7
                })
                
                # Reserved instance opportunity
                if cost > 1000:  # Only for significant costs
                    opportunities.append({
                        'id': f"{cloud}_reserved_instances",
                        'type': 'reservation',
                        'cloud': cloud,
                        'resource_type': 'compute',
                        'description': f"Reserved instance opportunity in {cloud}",
                        'estimated_savings': cost * 0.25,
                        'risk_level': 'low',
                        'action': 'purchase_reserved_instances',
                        'confidence': 0.8
                    })
            
            # Sort by estimated savings
            opportunities.sort(key=lambda x: x['estimated_savings'], reverse=True)
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Opportunity identification failed: {e}")
            return []

    async def _analyze_cost_by_service(self, cost_data: Dict[str, float]) -> Dict[str, float]:
        """Analyze costs by service type."""
        try:
            # Simulate service breakdown
            service_costs = {}
            total_cost = sum(cost_data.values())
            
            # Typical service distribution for a platform like Ainflue
            service_distribution = {
                'compute': 0.40,
                'storage': 0.20,
                'database': 0.15,
                'networking': 0.10,
                'ai_ml': 0.10,
                'other': 0.05
            }
            
            for service, percentage in service_distribution.items():
                service_costs[service] = total_cost * percentage
            
            return service_costs
            
        except Exception as e:
            self.logger.error(f"Service cost analysis failed: {e}")
            return {}

    async def _filter_opportunities_by_strategy(self, 
                                              opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter opportunities based on optimization strategy."""
        try:
            if self.strategy == OptimizationStrategy.AGGRESSIVE:
                # Accept all opportunities
                return opportunities
            elif self.strategy == OptimizationStrategy.CONSERVATIVE:
                # Only low-risk opportunities
                return [opp for opp in opportunities if opp['risk_level'] == 'low']
            elif self.strategy == OptimizationStrategy.BALANCED:
                # Low and medium risk with high confidence
                return [opp for opp in opportunities 
                       if opp['risk_level'] in ['low', 'medium'] and opp['confidence'] > 0.7]
            else:
                # Custom strategy - implement based on specific requirements
                return opportunities
                
        except Exception as e:
            self.logger.error(f"Opportunity filtering failed: {e}")
            return []

    async def _create_optimization_plan(self, 
                                      opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create detailed optimization execution plan."""
        try:
            plan = []
            
            for opportunity in opportunities:
                plan_item = {
                    'id': opportunity['id'],
                    'action': opportunity['action'],
                    'cloud': opportunity['cloud'],
                    'resource_type': opportunity['resource_type'],
                    'estimated_savings': opportunity['estimated_savings'],
                    'risk_level': opportunity['risk_level'],
                    'execution_steps': self._get_execution_steps(opportunity),
                    'rollback_plan': self._get_rollback_plan(opportunity),
                    'estimated_duration': self._estimate_execution_duration(opportunity)
                }
                plan.append(plan_item)
            
            return plan
            
        except Exception as e:
            self.logger.error(f"Optimization planning failed: {e}")
            return []

    def _get_execution_steps(self, opportunity: Dict[str, Any]) -> List[str]:
        """Get execution steps for optimization opportunity."""
        action = opportunity['action']
        
        steps_map = {
            'terminate_idle_instances': [
                'Identify idle instances',
                'Verify no critical workloads',
                'Create instance snapshots',
                'Terminate instances',
                'Verify termination success'
            ],
            'rightsize_instances': [
                'Analyze instance utilization',
                'Identify optimal instance sizes',
                'Schedule maintenance window',
                'Resize instances',
                'Monitor performance post-resize'
            ],
            'purchase_reserved_instances': [
                'Analyze usage patterns',
                'Calculate optimal reservation mix',
                'Purchase reserved instances',
                'Apply reservations to instances',
                'Monitor savings realization'
            ]
        }
        
        return steps_map.get(action, ['Execute optimization action'])

    def _get_rollback_plan(self, opportunity: Dict[str, Any]) -> List[str]:
        """Get rollback plan for optimization opportunity."""
        action = opportunity['action']
        
        rollback_map = {
            'terminate_idle_instances': [
                'Restore from snapshots if needed',
                'Restart instances if required'
            ],
            'rightsize_instances': [
                'Resize back to original instance type',
                'Verify application performance'
            ],
            'purchase_reserved_instances': [
                'Reserved instances cannot be rolled back',
                'Consider selling on marketplace if needed'
            ]
        }
        
        return rollback_map.get(action, ['Contact support for rollback assistance'])

    def _estimate_execution_duration(self, opportunity: Dict[str, Any]) -> str:
        """Estimate execution duration for optimization."""
        action = opportunity['action']
        
        duration_map = {
            'terminate_idle_instances': '15 minutes',
            'rightsize_instances': '30 minutes',
            'purchase_reserved_instances': '5 minutes'
        }
        
        return duration_map.get(action, '20 minutes')

    async def _execute_optimization(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specific optimization opportunity."""
        try:
            self.logger.info(f"Executing optimization: {opportunity['id']}")
            
            # Simulate optimization execution
            # In real implementation, this would call specific cloud provider APIs
            
            result = {
                'opportunity_id': opportunity['id'],
                'action_taken': opportunity['action'],
                'estimated_savings': opportunity['estimated_savings'],
                'actual_savings': opportunity['estimated_savings'] * 0.85,  # 85% realization
                'execution_time': datetime.utcnow().isoformat(),
                'status': 'completed',
                'resources_affected': self._simulate_affected_resources(opportunity)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Optimization execution failed: {e}")
            return {'status': 'failed', 'error': str(e)}

    def _simulate_affected_resources(self, opportunity: Dict[str, Any]) -> List[str]:
        """Simulate list of affected resources."""
        cloud = opportunity['cloud']
        action = opportunity['action']
        
        if 'instances' in action:
            return [f"{cloud}-instance-{i}" for i in range(1, 4)]
        elif 'storage' in action:
            return [f"{cloud}-volume-{i}" for i in range(1, 3)]
        else:
            return [f"{cloud}-resource-1"]

    def _record_optimization_history(self, results -> None: Dict[str, Any], total_savings -> None: float) -> None:
        """Record optimization history."""
        try:
            history_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'total_savings': total_savings,
                'optimizations_applied': len([r for r in results.values() if r['status'] == 'applied']),
                'strategy': self.strategy.value,
                'details': results
            }
            
            self.optimization_history.append(history_entry)
            
            # Keep only last 100 entries
            if len(self.optimization_history) > 100:
                self.optimization_history = self.optimization_history[-100:]
                
        except Exception as e:
            self.logger.error(f"Failed to record optimization history: {e}")

    async def _get_current_costs(self) -> Dict[str, float]:
        """Get current daily costs by resource type."""
        try:
            # Simulate current costs
            current_costs = {
                'compute': 850.0,
                'storage': 120.0,
                'network': 80.0,
                'database': 200.0,
                'ai_ml': 300.0
            }
            
            return current_costs
            
        except Exception as e:
            self.logger.error(f"Failed to get current costs: {e}")
            return {}

    async def _get_monthly_cost(self, resource_type: str) -> float:
        """Get monthly cost for specific resource type."""
        daily_costs = await self._get_current_costs()
        return daily_costs.get(resource_type, 0) * 30

    async def _auto_scale_down(self, resource_type: str) -> Dict[str, Any]:
        """Automatically scale down resources to reduce costs."""
        try:
            self.logger.info(f"Auto-scaling down {resource_type} resources")
            
            # Simulate auto-scaling action
            action_result = {
                'action': 'auto_scale_down',
                'resource_type': resource_type,
                'timestamp': datetime.utcnow().isoformat(),
                'resources_affected': 3,
                'estimated_savings': 200.0,
                'status': 'completed'
            }
            
            return action_result
            
        except Exception as e:
            self.logger.error(f"Auto-scaling failed for {resource_type}: {e}")
            return {'status': 'failed', 'error': str(e)}

    async def _collect_historical_cost_data(self) -> Dict[str, List[float]]:
        """Collect historical cost data for trend analysis."""
        try:
            # Simulate 90 days of historical data
            historical_data = {}
            
            for cloud in self.providers.keys():
                daily_costs = []
                base_cost = random.uniform(1000, 5000)
                
                for day in range(90):
                    # Simulate gradual cost increase with daily variance
                    daily_cost = base_cost * (1 + day * 0.001) * random.uniform(0.9, 1.1)
                    daily_costs.append(daily_cost)
                
                historical_data[cloud] = daily_costs
            
            return historical_data
            
        except Exception as e:
            self.logger.error(f"Historical data collection failed: {e}")
            return {}

    def _predict_cost_trend(self, cost_history: List[float], 
                          prediction_period: str) -> Dict[str, Any]:
        """Predict cost trend using historical data."""
        try:
            # Simple linear regression
            x = np.arange(len(cost_history))
            y = np.array(cost_history)
            
            # Calculate trend
            slope, intercept = np.polyfit(x, y, 1)
            
            # Predict future costs
            days_to_predict = 30  # Default to 30 days
            if prediction_period == "7d":
                days_to_predict = 7
            elif prediction_period == "60d":
                days_to_predict = 60
            elif prediction_period == "90d":
                days_to_predict = 90
            
            future_x = len(cost_history) + days_to_predict
            predicted_cost = slope * future_x + intercept
            
            # Calculate confidence interval (simplified)
            residuals = y - (slope * x + intercept)
            std_error = np.std(residuals)
            confidence_interval = [predicted_cost - 2*std_error, predicted_cost + 2*std_error]
            
            # Determine trend direction
            trend_direction = "increasing" if slope > 0 else "decreasing"
            
            # Calculate monthly growth rate
            monthly_growth_rate = (slope * 30 / np.mean(y)) * 100
            
            return {
                'predicted_cost': max(predicted_cost, 0),  # Cost can't be negative
                'confidence_interval': [max(ci, 0) for ci in confidence_interval],
                'trend_direction': trend_direction,
                'growth_rate': monthly_growth_rate
            }
            
        except Exception as e:
            self.logger.error(f"Cost prediction failed: {e}")
            return {
                'predicted_cost': np.mean(cost_history) if cost_history else 0,
                'confidence_interval': [0, 0],
                'trend_direction': 'unknown',
                'growth_rate': 0
            }

    async def _identify_cost_drivers(self, historical_data: Dict[str, List[float]]) -> List[Dict[str, Any]]:
        """Identify major cost drivers."""
        try:
            cost_drivers = []
            
            for cloud, costs in historical_data.items():
                if costs:
                    avg_cost = np.mean(costs)
                    cost_variance = np.var(costs)
                    
                    cost_drivers.append({
                        'cloud': cloud,
                        'average_cost': avg_cost,
                        'cost_variance': cost_variance,
                        'cost_stability': 'stable' if cost_variance < avg_cost * 0.1 else 'variable',
                        'contribution_percentage': avg_cost / sum(np.mean(c) for c in historical_data.values()) * 100
                    })
            
            # Sort by contribution percentage
            cost_drivers.sort(key=lambda x: x['contribution_percentage'], reverse=True)
            
            return cost_drivers
            
        except Exception as e:
            self.logger.error(f"Cost driver identification failed: {e}")
            return []

    async def _generate_cost_recommendations(self, predictions: Dict[str, Any], 
                                           cost_drivers: List[Dict[str, Any]]) -> List[str]:
        """Generate cost optimization recommendations."""
        try:
            recommendations = []
            
            # Analyze predictions for recommendations
            for cloud, prediction in predictions.items():
                if isinstance(prediction, dict) and 'growth_rate' in prediction:
                    growth_rate = prediction['growth_rate']
                    
                    if growth_rate > 10:  # More than 10% monthly growth
                        recommendations.append(
                            f"Consider implementing cost controls for {cloud} - "
                            f"projected {growth_rate:.1f}% monthly growth"
                        )
                    elif growth_rate > 20:  # Very high growth
                        recommendations.append(
                            f"URGENT: Review {cloud} resource usage - "
                            f"unsustainable {growth_rate:.1f}% monthly growth rate"
                        )
            
            # Analyze cost drivers for recommendations
            for driver in cost_drivers[:3]:  # Top 3 cost drivers
                if driver['cost_stability'] == 'variable':
                    recommendations.append(
                        f"Investigate cost variability in {driver['cloud']} - "
                        f"represents {driver['contribution_percentage']:.1f}% of total costs"
                    )
            
            # General recommendations
            total_predicted = sum(
                pred.get('predicted_cost', 0) for pred in predictions.values()
                if isinstance(pred, dict)
            )
            
            if total_predicted > 50000:  # High cost threshold
                recommendations.append(
                    "Consider reserved instances and enterprise discounts for high-volume usage"
                )
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Recommendation generation failed: {e}")
            return ["Unable to generate recommendations due to data analysis error"]

    def _calculate_prediction_confidence(self, predictions: Dict[str, Any]) -> float:
        """Calculate overall confidence score for predictions."""
        try:
            confidence_scores = []
            
            for prediction in predictions.values():
                if isinstance(prediction, dict) and 'confidence_interval' in prediction:
                    # Calculate confidence based on interval width
                    interval = prediction['confidence_interval']
                    predicted = prediction['predicted_cost']
                    
                    if predicted > 0:
                        interval_width = abs(interval[1] - interval[0])
                        confidence = max(0, 1 - (interval_width / predicted / 2))
                        confidence_scores.append(confidence)
            
            return np.mean(confidence_scores) if confidence_scores else 0.5
            
        except Exception as e:
            self.logger.error(f"Confidence calculation failed: {e}")
            return 0.5

    async def _calculate_savings_metrics(self) -> Dict[str, Any]:
        """Calculate savings achievement metrics."""
        try:
            total_savings = sum(self.savings_achieved.values())
            
            # Calculate savings trend
            recent_optimizations = self.optimization_history[-10:]  # Last 10 optimizations
            recent_savings = sum(opt.get('total_savings', 0) for opt in recent_optimizations)
            
            # Calculate average savings per optimization
            avg_savings = (total_savings / len(self.optimization_history) 
                          if self.optimization_history else 0)
            
            return {
                'total_lifetime_savings': total_savings,
                'recent_savings': recent_savings,
                'average_savings_per_optimization': avg_savings,
                'total_optimizations': len(self.optimization_history),
                'savings_trend': 'increasing' if recent_savings > avg_savings * 5 else 'stable'
            }
            
        except Exception as e:
            self.logger.error(f"Savings metrics calculation failed: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    async def main() -> None:
        # Initialize optimizer
        optimizer = CloudCostOptimizer(OptimizationStrategy.BALANCED)
        
        # Perform cost analysis
        report = await optimizer.analyze_costs("30d")
        print("Cost Analysis Report:")
        print(f"Total Cost: ${report.total_cost:.2f}")
        print(f"Savings Potential: ${report.savings_potential:.2f}")
        
        # Run optimization
        optimization_result = await optimizer.optimize_costs(auto_apply=False)
        print("\nOptimization Result:")
        print(f"Total Opportunities: {optimization_result['total_opportunities']}")
        print(f"Applied Optimizations: {optimization_result['applied_optimizations']}")
        
        # Get dashboard
        dashboard = await optimizer.get_cost_dashboard()
        print("\nCost Dashboard Summary:")
        print(f"Current Daily Cost: ${dashboard['summary']['current_daily_cost']:.2f}")
        print(f"Monthly Cost: ${dashboard['summary']['monthly_cost']:.2f}")

    asyncio.run(main())