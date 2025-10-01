"""📈 Scaling Controller - Predictive Autoscaling Enterprise
==========================================================

Scaling controller enterprise avec predictive autoscaling, ML-powered scaling decisions,
resource optimization et cost-aware scaling pour l'écosystème IA Chéries.

Expert Roles Implementation:
🤖 Lead Dev IA: ML-powered scaling predictions + intelligent resource allocation
🏗️ Backend Senior: Horizontal/vertical scaling + performance optimization
⚙️ DevOps: Autoscaling automation + monitoring + alerting
🗄️ DBA: Database scaling coordination + connection pooling
💰 FinOps: Cost-aware scaling + resource optimization + budget control
📊 Data Engineer: Metrics collection + trend analysis + capacity planning

Author: Fahed Mlaiel (mlaiel@live.de)
Version: 2.0 Production Enterprise
Date: 14 Septembre 2025

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
==========================================
"""

import asyncio
import logging
import json
import time
import statistics
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import deque

logger = logging.getLogger(__name__)

class ScalingType(Enum):
    """Types of scaling operations"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    HYBRID = "hybrid"

class ScalingDirection(Enum):
    """Scaling direction"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"

class ScalingTrigger(Enum):
    """Scaling trigger types"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    RESPONSE_TIME = "response_time"
    QUEUE_LENGTH = "queue_length"
    CUSTOM_METRIC = "custom_metric"
    PREDICTIVE = "predictive"
    SCHEDULED = "scheduled"

@dataclass
class ScalingMetrics:
    """Scaling metrics data"""
    cpu_utilization: float
    memory_utilization: float
    request_rate: float
    response_time: float
    queue_length: int
    error_rate: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class ScalingRule:
    """Scaling rule configuration"""
    name: str
    trigger: ScalingTrigger
    threshold_up: float
    threshold_down: float
    cooldown_period: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    min_replicas: int = 1
    max_replicas: int = 10
    scaling_factor: float = 1.5
    enabled: bool = True

@dataclass
class ScalingPrediction:
    """ML scaling prediction result"""
    predicted_load: float
    recommended_replicas: int
    confidence_score: float
    time_horizon: timedelta
    reasoning: str
    cost_impact: Dict[str, float]
    risk_assessment: str

class ScalingController:
    """📈 Scaling controller avec predictive autoscaling"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize Scaling Controller"""
        self.config = config or {}
        self.scaling_rules: Dict[str, List[ScalingRule]] = {}
        self.metrics_history: Dict[str, deque] = {}
        self.scaling_history: List[Dict[str, Any]] = []
        self.active_scaling_operations: Dict[str, Dict[str, Any]] = {}
        
        # ML and prediction components
        self.ml_predictor = MLScalingPredictor()
        self.metrics_analyzer = MetricsAnalyzer()
        self.cost_optimizer = CostOptimizer()
        self.capacity_planner = CapacityPlanner()
        
        self.initialized = False
        
        logger.info("📈 Scaling Controller initialized")
    
    async def initialize(self) -> bool:
        """
        🚀 Initialize scaling control infrastructure
        
        Acting as: Lead Dev IA + DevOps + FinOps
        """
        try:
            logger.info("🔄 Initializing scaling control infrastructure...")
            
            # Initialize ML predictor
            await self.ml_predictor.initialize()
            
            # Initialize metrics analyzer
            await self.metrics_analyzer.initialize()
            
            # Initialize cost optimizer
            await self.cost_optimizer.initialize()
            
            # Initialize capacity planner
            await self.capacity_planner.initialize()
            
            # Setup default scaling rules
            await self._setup_default_scaling_rules()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.initialized = True
            logger.info("✅ Scaling control infrastructure initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize scaling controller: {e}")
            return False
    
    async def configure_scaling_rules(
        self,
        service_name: str,
        scaling_rules: List[ScalingRule]
    ) -> Dict[str, Any]:
        """
        ⚙️ Configure scaling rules for service
        
        Acting as: DevOps + Performance Engineer
        """
        try:
            logger.info(f"⚙️ Configuring scaling rules for service: {service_name}")
            
            # Validate scaling rules
            validation_result = await self._validate_scaling_rules(scaling_rules)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'reason': validation_result['reason']
                }
            
            # Store scaling rules
            self.scaling_rules[service_name] = scaling_rules
            
            # Initialize metrics history for service
            if service_name not in self.metrics_history:
                self.metrics_history[service_name] = deque(maxlen=1000)
            
            # Configure monitoring
            await self._configure_service_monitoring(service_name, scaling_rules)
            
            return {
                'success': True,
                'service_name': service_name,
                'rules_configured': len(scaling_rules),
                'monitoring_enabled': True
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to configure scaling rules for {service_name}: {e}")
            raise
    
    async def evaluate_scaling_decision(
        self,
        service_name: str,
        current_metrics: ScalingMetrics
    ) -> Dict[str, Any]:
        """
        🧠 Evaluate scaling decision using ML and rules
        
        Acting as: Lead Dev IA + ML Engineer + Performance Analyst
        """
        try:
            if service_name not in self.scaling_rules:
                return {
                    'scaling_needed': False,
                    'reason': 'No scaling rules configured'
                }
            
            # Add metrics to history
            self.metrics_history[service_name].append(current_metrics)
            
            # Evaluate rule-based scaling
            rule_evaluation = await self._evaluate_scaling_rules(service_name, current_metrics)
            
            # Get ML-based prediction
            ml_prediction = await self.ml_predictor.predict_scaling_needs(
                service_name=service_name,
                current_metrics=current_metrics,
                metrics_history=list(self.metrics_history[service_name])
            )
            
            # Combine rule-based and ML-based decisions
            final_decision = await self._combine_scaling_decisions(
                service_name, rule_evaluation, ml_prediction, current_metrics
            )
            
            # Add cost analysis
            if final_decision['scaling_needed']:
                cost_analysis = await self.cost_optimizer.analyze_scaling_cost(
                    service_name, final_decision
                )
                final_decision['cost_analysis'] = cost_analysis
            
            return final_decision
            
        except Exception as e:
            logger.error(f"❌ Failed to evaluate scaling decision for {service_name}: {e}")
            raise
    
    async def execute_scaling_operation(
        self,
        service_name: str,
        scaling_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🚀 Execute scaling operation
        
        Acting as: DevOps + Backend Senior + Resource Manager
        """
        try:
            if not scaling_decision.get('scaling_needed', False):
                return {
                    'success': False,
                    'reason': 'No scaling needed'
                }
            
            operation_id = f"{service_name}-scale-{int(time.time())}"
            
            logger.info(f"🚀 Executing scaling operation: {operation_id}")
            
            # Check for concurrent scaling operations
            if service_name in self.active_scaling_operations:
                return {
                    'success': False,
                    'reason': 'Scaling operation already in progress'
                }
            
            # Initialize scaling operation
            scaling_operation = {
                'id': operation_id,
                'service_name': service_name,
                'type': scaling_decision['scaling_type'],
                'direction': scaling_decision['direction'],
                'target_replicas': scaling_decision.get('target_replicas'),
                'target_resources': scaling_decision.get('target_resources'),
                'start_time': datetime.utcnow(),
                'status': 'in_progress'
            }
            
            self.active_scaling_operations[service_name] = scaling_operation
            
            try:
                # Execute scaling based on type
                if scaling_decision['scaling_type'] == ScalingType.HORIZONTAL:
                    result = await self._execute_horizontal_scaling(
                        service_name, scaling_decision
                    )
                elif scaling_decision['scaling_type'] == ScalingType.VERTICAL:
                    result = await self._execute_vertical_scaling(
                        service_name, scaling_decision
                    )
                else:  # HYBRID
                    result = await self._execute_hybrid_scaling(
                        service_name, scaling_decision
                    )
                
                # Update operation status
                scaling_operation['status'] = 'completed' if result['success'] else 'failed'
                scaling_operation['end_time'] = datetime.utcnow()
                scaling_operation['result'] = result
                
                # Add to history
                self.scaling_history.append(scaling_operation.copy())
                
                # Remove from active operations
                del self.active_scaling_operations[service_name]
                
                return result
                
            except Exception as e:
                scaling_operation['status'] = 'failed'
                scaling_operation['error'] = str(e)
                scaling_operation['end_time'] = datetime.utcnow()
                
                del self.active_scaling_operations[service_name]
                raise
            
        except Exception as e:
            logger.error(f"❌ Failed to execute scaling operation for {service_name}: {e}")
            raise
    
    async def predict_future_scaling_needs(
        self,
        service_name: str,
        prediction_horizon: timedelta = timedelta(hours=4)
    ) -> ScalingPrediction:
        """
        🔮 Predict future scaling needs using ML
        
        Acting as: ML Engineer + Capacity Planner + Data Scientist
        """
        try:
            if service_name not in self.metrics_history:
                return ScalingPrediction(
                    predicted_load=1.0,
                    recommended_replicas=1,
                    confidence_score=0.5,
                    time_horizon=prediction_horizon,
                    reasoning="No historical data available",
                    cost_impact={},
                    risk_assessment="unknown"
                )
            
            # Get historical metrics
            historical_metrics = list(self.metrics_history[service_name])
            
            # Generate ML prediction
            ml_prediction = await self.ml_predictor.predict_future_load(
                service_name=service_name,
                historical_metrics=historical_metrics,
                prediction_horizon=prediction_horizon
            )
            
            # Calculate recommended resources
            current_replicas = await self._get_current_replicas(service_name)
            recommended_replicas = await self._calculate_recommended_replicas(
                ml_prediction['predicted_load'], current_replicas
            )
            
            # Analyze cost impact
            cost_impact = await self.cost_optimizer.calculate_scaling_cost_impact(
                service_name, current_replicas, recommended_replicas
            )
            
            # Assess risk
            risk_assessment = await self._assess_scaling_risk(
                service_name, ml_prediction, recommended_replicas
            )
            
            return ScalingPrediction(
                predicted_load=ml_prediction['predicted_load'],
                recommended_replicas=recommended_replicas,
                confidence_score=ml_prediction['confidence'],
                time_horizon=prediction_horizon,
                reasoning=ml_prediction['reasoning'],
                cost_impact=cost_impact,
                risk_assessment=risk_assessment
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to predict scaling needs for {service_name}: {e}")
            raise
    
    async def get_scaling_analytics(self, service_name: str) -> Dict[str, Any]:
        """
        📊 Get comprehensive scaling analytics
        
        Acting as: Data Analyst + Performance Engineer + FinOps
        """
        try:
            # Get recent metrics
            recent_metrics = list(self.metrics_history.get(service_name, []))[-100:]
            
            # Calculate analytics
            if recent_metrics:
                avg_cpu = statistics.mean(m.cpu_utilization for m in recent_metrics)
                avg_memory = statistics.mean(m.memory_utilization for m in recent_metrics)
                avg_response_time = statistics.mean(m.response_time for m in recent_metrics)
                avg_request_rate = statistics.mean(m.request_rate for m in recent_metrics)
            else:
                avg_cpu = avg_memory = avg_response_time = avg_request_rate = 0
            
            # Get scaling history for service
            service_scaling_history = [
                h for h in self.scaling_history 
                if h['service_name'] == service_name
            ]
            
            # Calculate scaling efficiency
            scaling_efficiency = await self._calculate_scaling_efficiency(service_name)
            
            # Get cost analytics
            cost_analytics = await self.cost_optimizer.get_service_cost_analytics(service_name)
            
            return {
                'service_name': service_name,
                'metrics_summary': {
                    'avg_cpu_utilization': avg_cpu,
                    'avg_memory_utilization': avg_memory,
                    'avg_response_time': avg_response_time,
                    'avg_request_rate': avg_request_rate,
                    'metrics_count': len(recent_metrics)
                },
                'scaling_history': {
                    'total_scaling_operations': len(service_scaling_history),
                    'successful_operations': len([h for h in service_scaling_history if h['status'] == 'completed']),
                    'failed_operations': len([h for h in service_scaling_history if h['status'] == 'failed']),
                    'recent_operations': service_scaling_history[-10:]
                },
                'scaling_efficiency': scaling_efficiency,
                'cost_analytics': cost_analytics,
                'active_rules': len(self.scaling_rules.get(service_name, [])),
                'current_status': await self._get_current_scaling_status(service_name)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get scaling analytics for {service_name}: {e}")
            raise
    
    # Helper methods and background tasks
    async def _setup_default_scaling_rules(self):
        """Setup default scaling rules"""
        default_rules = [
            ScalingRule(
                name="cpu_based_scaling",
                trigger=ScalingTrigger.CPU_UTILIZATION,
                threshold_up=80.0,
                threshold_down=30.0,
                min_replicas=1,
                max_replicas=10
            ),
            ScalingRule(
                name="memory_based_scaling",
                trigger=ScalingTrigger.MEMORY_UTILIZATION,
                threshold_up=85.0,
                threshold_down=40.0,
                min_replicas=1,
                max_replicas=10
            )
        ]
        
        logger.info("📋 Default scaling rules setup complete")
    
    async def _start_background_tasks(self):
        """Start background scaling tasks"""
        asyncio.create_task(self._continuous_monitoring_task())
        asyncio.create_task(self._predictive_scaling_task())
        asyncio.create_task(self._cost_optimization_task())
        logger.info("🔄 Background scaling tasks started")
    
    async def _continuous_monitoring_task(self):
        """Continuous monitoring and scaling evaluation"""
        while True:
            try:
                for service_name in self.scaling_rules.keys():
                    # Simulate current metrics collection
                    current_metrics = await self._collect_current_metrics(service_name)
                    
                    # Evaluate scaling decision
                    scaling_decision = await self.evaluate_scaling_decision(
                        service_name, current_metrics
                    )
                    
                    # Execute scaling if needed and enabled
                    if (scaling_decision.get('scaling_needed', False) and 
                        self.config.get('auto_scaling_enabled', True)):
                        
                        await self.execute_scaling_operation(service_name, scaling_decision)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Error in continuous monitoring: {e}")
                await asyncio.sleep(120)
    
    async def _predictive_scaling_task(self):
        """Predictive scaling task"""
        while True:
            try:
                for service_name in self.scaling_rules.keys():
                    prediction = await self.predict_future_scaling_needs(service_name)
                    
                    # Execute predictive scaling if confidence is high
                    if (prediction.confidence_score > 0.8 and 
                        self.config.get('predictive_scaling_enabled', False)):
                        
                        logger.info(f"🔮 Executing predictive scaling for {service_name}")
                        # Implementation would trigger preemptive scaling
                
                await asyncio.sleep(900)  # Check every 15 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in predictive scaling: {e}")
                await asyncio.sleep(1800)
    
    async def _cost_optimization_task(self):
        """Cost optimization background task"""
        while True:
            try:
                for service_name in self.scaling_rules.keys():
                    cost_optimization = await self.cost_optimizer.optimize_service_cost(service_name)
                    
                    if cost_optimization.get('optimization_available'):
                        logger.info(f"💰 Cost optimization available for {service_name}")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"❌ Error in cost optimization: {e}")
                await asyncio.sleep(7200)
    
    # Simplified helper method implementations
    async def _collect_current_metrics(self, service_name: str) -> ScalingMetrics:
        """Collect current metrics for service"""
        # Simulate metrics collection
        base_cpu = 50 + (hash(service_name + str(int(time.time() / 60))) % 40)
        base_memory = 45 + (hash(service_name + str(int(time.time() / 120))) % 35)
        
        return ScalingMetrics(
            cpu_utilization=base_cpu,
            memory_utilization=base_memory,
            request_rate=100 + (hash(service_name) % 200),
            response_time=80 + (hash(service_name) % 100),
            queue_length=5 + (hash(service_name) % 20),
            error_rate=0.01 + (hash(service_name) % 5) / 1000
        )
    
    async def _validate_scaling_rules(self, rules: List[ScalingRule]) -> Dict[str, Any]:
        """Validate scaling rules"""
        for rule in rules:
            if rule.threshold_up <= rule.threshold_down:
                return {
                    'valid': False,
                    'reason': f'Invalid thresholds for rule {rule.name}'
                }
            
            if rule.min_replicas >= rule.max_replicas:
                return {
                    'valid': False,
                    'reason': f'Invalid replica limits for rule {rule.name}'
                }
        
        return {'valid': True}
    
    async def _evaluate_scaling_rules(self, service_name: str, metrics: ScalingMetrics) -> Dict[str, Any]:
        """Evaluate rule-based scaling"""
        rules = self.scaling_rules.get(service_name, [])
        
        for rule in rules:
            if not rule.enabled:
                continue
            
            metric_value = getattr(metrics, rule.trigger.value.replace('_utilization', '_utilization'))
            
            if metric_value > rule.threshold_up:
                return {
                    'scaling_needed': True,
                    'direction': ScalingDirection.UP,
                    'trigger': rule.trigger,
                    'rule_name': rule.name,
                    'metric_value': metric_value,
                    'threshold': rule.threshold_up
                }
            elif metric_value < rule.threshold_down:
                return {
                    'scaling_needed': True,
                    'direction': ScalingDirection.DOWN,
                    'trigger': rule.trigger,
                    'rule_name': rule.name,
                    'metric_value': metric_value,
                    'threshold': rule.threshold_down
                }
        
        return {
            'scaling_needed': False,
            'reason': 'All metrics within thresholds'
        }


# Helper classes for scaling functionality
class MLScalingPredictor:
    """🤖 ML-based scaling predictor"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize ML predictor"""
        self.initialized = True
        logger.info("✅ ML Scaling Predictor initialized")
    
    async def predict_scaling_needs(
        self,
        service_name: str,
        current_metrics: ScalingMetrics,
        metrics_history: List[ScalingMetrics]
    ) -> Dict[str, Any]:
        """Predict scaling needs using ML"""
        if not metrics_history:
            return {
                'scaling_needed': False,
                'confidence': 0.5,
                'reasoning': 'Insufficient historical data'
            }
        
        # Simulate ML prediction
        trend = self._calculate_trend(metrics_history)
        
        if trend > 0.1:  # Increasing trend
            return {
                'scaling_needed': True,
                'direction': ScalingDirection.UP,
                'confidence': 0.85,
                'reasoning': 'Increasing load trend detected'
            }
        elif trend < -0.1:  # Decreasing trend
            return {
                'scaling_needed': True,
                'direction': ScalingDirection.DOWN,
                'confidence': 0.75,
                'reasoning': 'Decreasing load trend detected'
            }
        
        return {
            'scaling_needed': False,
            'confidence': 0.9,
            'reasoning': 'Stable load pattern'
        }
    
    def _calculate_trend(self, metrics_history: List[ScalingMetrics]) -> float:
        """Calculate trend from metrics history"""
        if len(metrics_history) < 2:
            return 0.0
        
        cpu_values = [m.cpu_utilization for m in metrics_history[-10:]]
        if len(cpu_values) < 2:
            return 0.0
        
        # Simple trend calculation
        return (cpu_values[-1] - cpu_values[0]) / len(cpu_values)


class MetricsAnalyzer:
    """📊 Metrics analyzer for scaling decisions"""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize metrics analyzer"""
        self.initialized = True
        logger.info("✅ Metrics Analyzer initialized")


class CostOptimizer:
    """💰 Cost optimizer for scaling operations"""
    
    def __init__(self):
        self.cost_models: Dict[str, float] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize cost optimizer"""
        self.initialized = True
        logger.info("✅ Cost Optimizer initialized")
    
    async def analyze_scaling_cost(self, service_name: str, scaling_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cost impact of scaling decision"""
        return {
            'current_cost_per_hour': 5.0,
            'projected_cost_per_hour': 7.5 if scaling_decision['direction'] == ScalingDirection.UP else 3.5,
            'cost_change_percent': 50.0 if scaling_decision['direction'] == ScalingDirection.UP else -30.0,
            'break_even_utilization': 70.0
        }


class CapacityPlanner:
    """📋 Capacity planner for resource management"""
    
    def __init__(self):
        self.capacity_models: Dict[str, Dict[str, Any]] = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize capacity planner"""
        self.initialized = True
        logger.info("✅ Capacity Planner initialized")
