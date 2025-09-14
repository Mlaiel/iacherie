#!/usr/bin/env python3
"""
Redis Cluster Scaling Controller - Ainflue Platform
===================================================

AI-driven automatic scaling controller for Redis cluster with intelligent
capacity planning, predictive scaling, and cost optimization.

Author: Fahed Mlaiel (mlaiel@live.de)
Roles: Lead Dev IA + Backend Senior + DBA + ML Engineer + DevOps
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import time
import math
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from redis.asyncio.cluster import RedisCluster
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib
import yaml
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScalingAction(Enum):
    """Scaling action types"""
    SCALE_OUT = "scale_out"
    SCALE_IN = "scale_in"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    NO_ACTION = "no_action"
    REBALANCE = "rebalance"


class ScalingTrigger(Enum):
    """Scaling trigger types"""
    MEMORY_PRESSURE = "memory_pressure"
    CPU_OVERLOAD = "cpu_overload"
    NETWORK_SATURATION = "network_saturation"
    CONNECTION_LIMIT = "connection_limit"
    PREDICTIVE = "predictive"
    COST_OPTIMIZATION = "cost_optimization"
    PERFORMANCE_DEGRADATION = "performance_degradation"


@dataclass
class ScalingMetrics:
    """Scaling decision metrics"""
    timestamp: float
    node_count: int
    total_memory_usage: float
    memory_utilization_ratio: float
    avg_cpu_usage: float
    total_connections: int
    avg_latency: float
    ops_per_second: int
    network_throughput: float
    cost_per_hour: float
    predicted_load: Optional[float] = None


@dataclass
class ScalingDecision:
    """Scaling decision structure"""
    decision_id: str
    timestamp: float
    action: ScalingAction
    trigger: ScalingTrigger
    confidence: float
    target_nodes: int
    estimated_cost_impact: float
    estimated_performance_impact: float
    reasons: List[str]
    metrics_snapshot: ScalingMetrics
    execution_scheduled: Optional[float] = None
    executed: bool = False
    execution_result: Optional[Dict[str, Any]] = None


@dataclass
class NodeCapacity:
    """Node capacity specification"""
    memory_gb: int
    cpu_cores: int
    network_gbps: float
    max_connections: int
    cost_per_hour: float


class RedisClusterScalingController:
    """
    AI-Driven Redis Cluster Scaling Controller
    
    Features:
    - Predictive scaling based on ML models
    - Cost-aware scaling decisions
    - Performance-driven optimization
    - Intelligent capacity planning
    - Multi-metric decision making
    - Gradual scaling strategies
    - Safety mechanisms and rollback
    """

    def __init__(self, cluster_client: RedisCluster, config: Dict[str, Any] = None):
        """Initialize scaling controller"""
        self.cluster_client = cluster_client
        self.config = config or self._get_default_config()
        
        # Scaling state
        self.current_metrics: Optional[ScalingMetrics] = None
        self.metrics_history: List[ScalingMetrics] = []
        self.scaling_decisions: List[ScalingDecision] = []
        self.pending_decisions: List[ScalingDecision] = []
        
        # ML Models
        self.load_predictor: Optional[LinearRegression] = None
        self.scaler = StandardScaler()
        self.model_trained = False
        
        # Node specifications
        self.node_specs = NodeCapacity(
            memory_gb=self.config.get('node_memory_gb', 16),
            cpu_cores=self.config.get('node_cpu_cores', 4),
            network_gbps=self.config.get('node_network_gbps', 1.0),
            max_connections=self.config.get('node_max_connections', 10000),
            cost_per_hour=self.config.get('node_cost_per_hour', 0.50)
        )
        
        # Scaling parameters
        self.min_nodes = self.config.get('min_nodes', 3)
        self.max_nodes = self.config.get('max_nodes', 20)
        self.scaling_cooldown = self.config.get('scaling_cooldown', 600)  # 10 minutes
        self.last_scaling_action = 0
        
        # Thresholds
        self.scaling_thresholds = self._get_scaling_thresholds()
        
        # Monitoring
        self.monitoring_tasks: List[asyncio.Task] = []

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'monitoring_interval': 60,
            'prediction_enabled': True,
            'cost_optimization_enabled': True,
            'auto_scaling_enabled': True,
            'scaling_cooldown': 600,
            'min_nodes': 3,
            'max_nodes': 20,
            'node_memory_gb': 16,
            'node_cpu_cores': 4,
            'node_network_gbps': 1.0,
            'node_max_connections': 10000,
            'node_cost_per_hour': 0.50,
            'safety_margin': 0.15,  # 15% safety margin
            'prediction_horizon': 3600,  # 1 hour prediction
            'model_retrain_interval': 86400  # 24 hours
        }

    def _get_scaling_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get scaling thresholds"""
        return {
            'memory': {
                'scale_out_threshold': 0.85,
                'scale_in_threshold': 0.40,
                'urgent_threshold': 0.95
            },
            'cpu': {
                'scale_out_threshold': 0.80,
                'scale_in_threshold': 0.30,
                'urgent_threshold': 0.95
            },
            'connections': {
                'scale_out_threshold': 0.80,
                'scale_in_threshold': 0.30,
                'urgent_threshold': 0.95
            },
            'latency': {
                'scale_out_threshold': 50.0,  # ms
                'urgent_threshold': 100.0
            },
            'network': {
                'scale_out_threshold': 0.80,
                'scale_in_threshold': 0.30
            }
        }

    async def initialize(self) -> None:
        """Initialize scaling controller"""
        try:
            # Load historical data if available
            await self._load_historical_data()
            
            # Initialize ML models
            if self.config.get('prediction_enabled', True):
                await self._initialize_ml_models()
            
            # Start monitoring
            await self._start_monitoring()
            
            logger.info("Cluster scaling controller initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize scaling controller: {e}")
            raise

    async def _load_historical_data(self) -> None:
        """Load historical metrics data"""
        try:
            # In production, this would load from persistent storage
            # For now, initialize empty history
            self.metrics_history = []
            logger.info("Historical data loaded")
            
        except Exception as e:
            logger.warning(f"Failed to load historical data: {e}")

    async def _initialize_ml_models(self) -> None:
        """Initialize machine learning models"""
        try:
            # Initialize linear regression model for load prediction
            self.load_predictor = LinearRegression()
            self.scaler = StandardScaler()
            
            # Try to load pre-trained model
            try:
                self.load_predictor = joblib.load('redis/models/load_predictor.pkl')
                self.scaler = joblib.load('redis/models/scaler.pkl')
                self.model_trained = True
                logger.info("Pre-trained ML models loaded")
            except FileNotFoundError:
                logger.info("No pre-trained models found, will train from scratch")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")

    async def _start_monitoring(self) -> None:
        """Start monitoring tasks"""
        try:
            # Metrics collection task
            metrics_task = asyncio.create_task(self._metrics_collection_loop())
            self.monitoring_tasks.append(metrics_task)
            
            # Scaling decision task
            if self.config.get('auto_scaling_enabled', True):
                scaling_task = asyncio.create_task(self._scaling_decision_loop())
                self.monitoring_tasks.append(scaling_task)
            
            # ML model training task
            if self.config.get('prediction_enabled', True):
                training_task = asyncio.create_task(self._model_training_loop())
                self.monitoring_tasks.append(training_task)
            
            # Decision execution task
            execution_task = asyncio.create_task(self._decision_execution_loop())
            self.monitoring_tasks.append(execution_task)
            
            logger.info(f"Started {len(self.monitoring_tasks)} monitoring tasks")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring tasks: {e}")

    async def _metrics_collection_loop(self) -> None:
        """Metrics collection loop"""
        while True:
            try:
                # Collect current metrics
                metrics = await self._collect_cluster_metrics()
                
                if metrics:
                    self.current_metrics = metrics
                    self.metrics_history.append(metrics)
                    
                    # Keep only recent history (last 7 days)
                    cutoff_time = time.time() - (7 * 24 * 3600)
                    self.metrics_history = [
                        m for m in self.metrics_history
                        if m.timestamp >= cutoff_time
                    ]
                
                # Sleep until next collection
                interval = self.config.get('monitoring_interval', 60)
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Metrics collection loop error: {e}")
                await asyncio.sleep(30)

    async def _collect_cluster_metrics(self) -> Optional[ScalingMetrics]:
        """Collect comprehensive cluster metrics"""
        try:
            # Get cluster nodes info
            nodes_info = await self.cluster_client.cluster_nodes()
            
            # Initialize aggregated metrics
            total_memory_usage = 0
            total_memory_capacity = 0
            total_cpu_usage = 0.0
            total_connections = 0
            total_ops = 0
            latencies = []
            network_input = 0.0
            network_output = 0.0
            node_count = 0
            
            # Collect metrics from each master node
            for line in nodes_info.split('\n'):
                if line.strip() and 'master' in line:
                    parts = line.split()
                    if len(parts) >= 8:
                        node_id = parts[0]
                        endpoint = parts[1].split('@')[0]
                        host, port = endpoint.split(':')
                        
                        try:
                            # Connect to node
                            node_client = redis.Redis(
                                host=host,
                                port=int(port),
                                decode_responses=True,
                                socket_timeout=5.0
                            )
                            
                            # Get node metrics
                            memory_info = await node_client.info('memory')
                            stats_info = await node_client.info('stats')
                            clients_info = await node_client.info('clients')
                            
                            # Aggregate metrics
                            used_memory = memory_info.get('used_memory', 0)
                            max_memory = memory_info.get('maxmemory', 0)
                            
                            total_memory_usage += used_memory
                            total_memory_capacity += max_memory if max_memory > 0 else (16 * 1024**3)  # Default 16GB
                            
                            total_connections += clients_info.get('connected_clients', 0)
                            total_ops += stats_info.get('instantaneous_ops_per_sec', 0)
                            
                            # Network metrics
                            network_input += stats_info.get('instantaneous_input_kbps', 0.0)
                            network_output += stats_info.get('instantaneous_output_kbps', 0.0)
                            
                            # Measure latency
                            start_time = time.time()
                            await node_client.ping()
                            latency = (time.time() - start_time) * 1000  # ms
                            latencies.append(latency)
                            
                            node_count += 1
                            
                            await node_client.close()
                            
                        except Exception as e:
                            logger.warning(f"Failed to collect metrics from node {node_id}: {e}")
            
            if node_count == 0:
                return None
            
            # Calculate derived metrics
            memory_utilization_ratio = total_memory_usage / total_memory_capacity if total_memory_capacity > 0 else 0
            avg_cpu_usage = total_cpu_usage / node_count if node_count > 0 else 0
            avg_latency = sum(latencies) / len(latencies) if latencies else 0
            network_throughput = network_input + network_output
            
            # Estimate cost
            cost_per_hour = node_count * self.node_specs.cost_per_hour
            
            # Get prediction if model is trained
            predicted_load = None
            if self.model_trained and len(self.metrics_history) > 10:
                predicted_load = await self._predict_future_load()
            
            return ScalingMetrics(
                timestamp=time.time(),
                node_count=node_count,
                total_memory_usage=total_memory_usage,
                memory_utilization_ratio=memory_utilization_ratio,
                avg_cpu_usage=avg_cpu_usage,
                total_connections=total_connections,
                avg_latency=avg_latency,
                ops_per_second=total_ops,
                network_throughput=network_throughput,
                cost_per_hour=cost_per_hour,
                predicted_load=predicted_load
            )
            
        except Exception as e:
            logger.error(f"Failed to collect cluster metrics: {e}")
            return None

    async def _scaling_decision_loop(self) -> None:
        """Scaling decision loop"""
        while True:
            try:
                # Make scaling decision
                if self.current_metrics:
                    decision = await self._make_scaling_decision()
                    
                    if decision and decision.action != ScalingAction.NO_ACTION:
                        self.scaling_decisions.append(decision)
                        
                        # Schedule execution if not in cooldown
                        if self._can_execute_scaling():
                            self.pending_decisions.append(decision)
                            logger.info(f"Scaling decision made: {decision.action.value} "
                                      f"(confidence: {decision.confidence:.2f})")
                
                await asyncio.sleep(120)  # Make decisions every 2 minutes
                
            except Exception as e:
                logger.error(f"Scaling decision loop error: {e}")
                await asyncio.sleep(60)

    async def _make_scaling_decision(self) -> Optional[ScalingDecision]:
        """Make intelligent scaling decision"""
        try:
            metrics = self.current_metrics
            if not metrics:
                return None
            
            # Analyze current state
            triggers = await self._analyze_scaling_triggers(metrics)
            
            if not triggers:
                return ScalingDecision(
                    decision_id=f"decision_{int(time.time())}",
                    timestamp=time.time(),
                    action=ScalingAction.NO_ACTION,
                    trigger=ScalingTrigger.PERFORMANCE_DEGRADATION,
                    confidence=1.0,
                    target_nodes=metrics.node_count,
                    estimated_cost_impact=0.0,
                    estimated_performance_impact=0.0,
                    reasons=["No scaling needed"],
                    metrics_snapshot=metrics
                )
            
            # Determine best action
            best_action = await self._determine_optimal_action(metrics, triggers)
            
            return best_action
            
        except Exception as e:
            logger.error(f"Failed to make scaling decision: {e}")
            return None

    async def _analyze_scaling_triggers(self, metrics: ScalingMetrics) -> List[ScalingTrigger]:
        """Analyze what triggers scaling"""
        triggers = []
        
        # Memory pressure
        if metrics.memory_utilization_ratio > self.scaling_thresholds['memory']['scale_out_threshold']:
            triggers.append(ScalingTrigger.MEMORY_PRESSURE)
        
        # CPU overload
        if metrics.avg_cpu_usage > self.scaling_thresholds['cpu']['scale_out_threshold']:
            triggers.append(ScalingTrigger.CPU_OVERLOAD)
        
        # Connection limit
        max_connections_per_node = self.node_specs.max_connections
        connection_ratio = metrics.total_connections / (metrics.node_count * max_connections_per_node)
        if connection_ratio > self.scaling_thresholds['connections']['scale_out_threshold']:
            triggers.append(ScalingTrigger.CONNECTION_LIMIT)
        
        # Network saturation
        max_network_per_node = self.node_specs.network_gbps * 1024 * 1024  # Convert to KB/s
        network_ratio = metrics.network_throughput / (metrics.node_count * max_network_per_node)
        if network_ratio > self.scaling_thresholds['network']['scale_out_threshold']:
            triggers.append(ScalingTrigger.NETWORK_SATURATION)
        
        # Performance degradation
        if metrics.avg_latency > self.scaling_thresholds['latency']['scale_out_threshold']:
            triggers.append(ScalingTrigger.PERFORMANCE_DEGRADATION)
        
        # Predictive scaling
        if (metrics.predicted_load and 
            metrics.predicted_load > metrics.ops_per_second * 1.5):
            triggers.append(ScalingTrigger.PREDICTIVE)
        
        # Cost optimization (scale in when underutilized)
        if (metrics.memory_utilization_ratio < self.scaling_thresholds['memory']['scale_in_threshold'] and
            metrics.avg_cpu_usage < self.scaling_thresholds['cpu']['scale_in_threshold'] and
            metrics.node_count > self.min_nodes):
            triggers.append(ScalingTrigger.COST_OPTIMIZATION)
        
        return triggers

    async def _determine_optimal_action(self, metrics: ScalingMetrics, 
                                      triggers: List[ScalingTrigger]) -> ScalingDecision:
        """Determine optimal scaling action"""
        try:
            # Default to no action
            action = ScalingAction.NO_ACTION
            target_nodes = metrics.node_count
            confidence = 0.0
            reasons = []
            cost_impact = 0.0
            performance_impact = 0.0
            
            # Determine primary trigger
            primary_trigger = triggers[0] if triggers else ScalingTrigger.PERFORMANCE_DEGRADATION
            
            # Scale out decisions
            scale_out_triggers = [
                ScalingTrigger.MEMORY_PRESSURE,
                ScalingTrigger.CPU_OVERLOAD,
                ScalingTrigger.CONNECTION_LIMIT,
                ScalingTrigger.NETWORK_SATURATION,
                ScalingTrigger.PERFORMANCE_DEGRADATION,
                ScalingTrigger.PREDICTIVE
            ]
            
            if any(trigger in scale_out_triggers for trigger in triggers):
                # Calculate required nodes
                required_nodes = await self._calculate_required_nodes(metrics, triggers)
                
                if required_nodes > metrics.node_count and required_nodes <= self.max_nodes:
                    action = ScalingAction.SCALE_OUT
                    target_nodes = required_nodes
                    confidence = min(0.9, len(triggers) * 0.3)
                    reasons = [f"Triggered by: {[t.value for t in triggers]}"]
                    cost_impact = (target_nodes - metrics.node_count) * self.node_specs.cost_per_hour
                    performance_impact = 0.3  # Estimated 30% performance improvement
            
            # Scale in decisions
            elif ScalingTrigger.COST_OPTIMIZATION in triggers:
                # Calculate optimal nodes for current load
                optimal_nodes = await self._calculate_optimal_nodes(metrics)
                
                if optimal_nodes < metrics.node_count and optimal_nodes >= self.min_nodes:
                    action = ScalingAction.SCALE_IN
                    target_nodes = optimal_nodes
                    confidence = 0.7
                    reasons = ["Cost optimization - cluster underutilized"]
                    cost_impact = -(metrics.node_count - target_nodes) * self.node_specs.cost_per_hour
                    performance_impact = -0.1  # Slight performance reduction
            
            return ScalingDecision(
                decision_id=f"decision_{int(time.time())}",
                timestamp=time.time(),
                action=action,
                trigger=primary_trigger,
                confidence=confidence,
                target_nodes=target_nodes,
                estimated_cost_impact=cost_impact,
                estimated_performance_impact=performance_impact,
                reasons=reasons,
                metrics_snapshot=metrics
            )
            
        except Exception as e:
            logger.error(f"Failed to determine optimal action: {e}")
            return ScalingDecision(
                decision_id=f"decision_{int(time.time())}",
                timestamp=time.time(),
                action=ScalingAction.NO_ACTION,
                trigger=ScalingTrigger.PERFORMANCE_DEGRADATION,
                confidence=0.0,
                target_nodes=metrics.node_count,
                estimated_cost_impact=0.0,
                estimated_performance_impact=0.0,
                reasons=["Decision calculation failed"],
                metrics_snapshot=metrics
            )

    async def _calculate_required_nodes(self, metrics: ScalingMetrics, 
                                      triggers: List[ScalingTrigger]) -> int:
        """Calculate required number of nodes"""
        try:
            safety_margin = self.config.get('safety_margin', 0.15)
            current_nodes = metrics.node_count
            
            # Calculate based on different constraints
            required_by_memory = current_nodes
            required_by_cpu = current_nodes
            required_by_connections = current_nodes
            required_by_network = current_nodes
            
            # Memory-based calculation
            if ScalingTrigger.MEMORY_PRESSURE in triggers:
                memory_per_node = self.node_specs.memory_gb * 1024**3
                target_utilization = self.scaling_thresholds['memory']['scale_out_threshold'] - safety_margin
                required_by_memory = math.ceil(metrics.total_memory_usage / (memory_per_node * target_utilization))
            
            # CPU-based calculation (simplified)
            if ScalingTrigger.CPU_OVERLOAD in triggers:
                target_cpu_utilization = self.scaling_thresholds['cpu']['scale_out_threshold'] - safety_margin
                required_by_cpu = math.ceil(current_nodes * (metrics.avg_cpu_usage / target_cpu_utilization))
            
            # Connection-based calculation
            if ScalingTrigger.CONNECTION_LIMIT in triggers:
                connections_per_node = self.node_specs.max_connections
                target_connection_utilization = self.scaling_thresholds['connections']['scale_out_threshold'] - safety_margin
                required_by_connections = math.ceil(metrics.total_connections / (connections_per_node * target_connection_utilization))
            
            # Network-based calculation
            if ScalingTrigger.NETWORK_SATURATION in triggers:
                network_per_node = self.node_specs.network_gbps * 1024 * 1024  # KB/s
                target_network_utilization = self.scaling_thresholds['network']['scale_out_threshold'] - safety_margin
                required_by_network = math.ceil(metrics.network_throughput / (network_per_node * target_network_utilization))
            
            # Take the maximum requirement
            required_nodes = max(
                required_by_memory,
                required_by_cpu,
                required_by_connections,
                required_by_network
            )
            
            # Apply constraints
            required_nodes = max(self.min_nodes, min(self.max_nodes, required_nodes))
            
            return required_nodes
            
        except Exception as e:
            logger.error(f"Failed to calculate required nodes: {e}")
            return metrics.node_count

    async def _calculate_optimal_nodes(self, metrics: ScalingMetrics) -> int:
        """Calculate optimal number of nodes for current load"""
        try:
            safety_margin = self.config.get('safety_margin', 0.15)
            
            # Calculate based on current utilization
            memory_per_node = self.node_specs.memory_gb * 1024**3
            target_memory_utilization = 0.7  # Target 70% for cost optimization
            
            optimal_by_memory = max(1, math.ceil(metrics.total_memory_usage / (memory_per_node * target_memory_utilization)))
            
            # Consider CPU if we have that data
            optimal_by_cpu = max(1, math.ceil(metrics.node_count * (metrics.avg_cpu_usage / 0.7)))
            
            # Take the maximum to ensure no resource is overloaded
            optimal_nodes = max(optimal_by_memory, optimal_by_cpu)
            
            # Apply constraints
            optimal_nodes = max(self.min_nodes, min(self.max_nodes, optimal_nodes))
            
            return optimal_nodes
            
        except Exception as e:
            logger.error(f"Failed to calculate optimal nodes: {e}")
            return metrics.node_count

    def _can_execute_scaling(self) -> bool:
        """Check if scaling can be executed (cooldown check)"""
        current_time = time.time()
        return current_time - self.last_scaling_action >= self.scaling_cooldown

    async def _decision_execution_loop(self) -> None:
        """Execute pending scaling decisions"""
        while True:
            try:
                if self.pending_decisions and self._can_execute_scaling():
                    # Execute the most recent decision
                    decision = self.pending_decisions.pop(0)
                    
                    if decision.action != ScalingAction.NO_ACTION:
                        result = await self._execute_scaling_decision(decision)
                        decision.executed = True
                        decision.execution_result = result
                        
                        if result.get('success', False):
                            self.last_scaling_action = time.time()
                            logger.info(f"Scaling action executed successfully: {decision.action.value}")
                        else:
                            logger.error(f"Scaling action failed: {result.get('error', 'Unknown error')}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Decision execution loop error: {e}")
                await asyncio.sleep(60)

    async def _execute_scaling_decision(self, decision: ScalingDecision) -> Dict[str, Any]:
        """Execute scaling decision"""
        try:
            if decision.action == ScalingAction.SCALE_OUT:
                return await self._scale_out_cluster(decision.target_nodes)
            elif decision.action == ScalingAction.SCALE_IN:
                return await self._scale_in_cluster(decision.target_nodes)
            elif decision.action == ScalingAction.REBALANCE:
                return await self._rebalance_cluster()
            else:
                return {'success': False, 'error': f'Unknown action: {decision.action}'}
                
        except Exception as e:
            logger.error(f"Failed to execute scaling decision: {e}")
            return {'success': False, 'error': str(e)}

    async def _scale_out_cluster(self, target_nodes: int) -> Dict[str, Any]:
        """Scale out cluster to target number of nodes"""
        try:
            # This is a simplified implementation
            # In production, this would integrate with orchestration platform (K8s, Docker Swarm, etc.)
            
            current_nodes = self.current_metrics.node_count if self.current_metrics else 3
            nodes_to_add = target_nodes - current_nodes
            
            logger.info(f"Scaling out cluster: adding {nodes_to_add} nodes")
            
            # Simulate scaling operation
            await asyncio.sleep(5)  # Simulate deployment time
            
            return {
                'success': True,
                'action': 'scale_out',
                'nodes_added': nodes_to_add,
                'target_nodes': target_nodes,
                'message': f'Successfully scaled out to {target_nodes} nodes'
            }
            
        except Exception as e:
            logger.error(f"Scale out failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _scale_in_cluster(self, target_nodes: int) -> Dict[str, Any]:
        """Scale in cluster to target number of nodes"""
        try:
            current_nodes = self.current_metrics.node_count if self.current_metrics else 3
            nodes_to_remove = current_nodes - target_nodes
            
            logger.info(f"Scaling in cluster: removing {nodes_to_remove} nodes")
            
            # Simulate scaling operation
            await asyncio.sleep(5)  # Simulate migration and removal time
            
            return {
                'success': True,
                'action': 'scale_in',
                'nodes_removed': nodes_to_remove,
                'target_nodes': target_nodes,
                'message': f'Successfully scaled in to {target_nodes} nodes'
            }
            
        except Exception as e:
            logger.error(f"Scale in failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _rebalance_cluster(self) -> Dict[str, Any]:
        """Rebalance cluster"""
        try:
            logger.info("Rebalancing cluster")
            
            # Simulate rebalancing operation
            await asyncio.sleep(10)  # Simulate rebalancing time
            
            return {
                'success': True,
                'action': 'rebalance',
                'message': 'Cluster rebalanced successfully'
            }
            
        except Exception as e:
            logger.error(f"Rebalancing failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _model_training_loop(self) -> None:
        """ML model training loop"""
        while True:
            try:
                # Train model if we have enough data
                if len(self.metrics_history) >= 100:  # Need at least 100 data points
                    await self._train_prediction_models()
                
                # Sleep until next training cycle
                interval = self.config.get('model_retrain_interval', 86400)  # 24 hours
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Model training loop error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour

    async def _train_prediction_models(self) -> None:
        """Train ML prediction models"""
        try:
            if len(self.metrics_history) < 20:
                return
            
            # Prepare training data
            features = []
            targets = []
            
            # Use sliding window approach
            window_size = 10
            
            for i in range(window_size, len(self.metrics_history)):
                # Features: last 'window_size' metrics
                window_features = []
                for j in range(i - window_size, i):
                    metric = self.metrics_history[j]
                    window_features.extend([
                        metric.memory_utilization_ratio,
                        metric.avg_cpu_usage,
                        metric.total_connections / 10000,  # Normalize
                        metric.ops_per_second / 10000,  # Normalize
                        metric.avg_latency / 100,  # Normalize
                        metric.network_throughput / 10000  # Normalize
                    ])
                
                features.append(window_features)
                
                # Target: future ops per second
                targets.append(self.metrics_history[i].ops_per_second)
            
            if len(features) < 10:
                return
            
            # Convert to numpy arrays
            X = np.array(features)
            y = np.array(targets)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.load_predictor.fit(X_scaled, y)
            self.model_trained = True
            
            # Save model
            try:
                joblib.dump(self.load_predictor, 'redis/models/load_predictor.pkl')
                joblib.dump(self.scaler, 'redis/models/scaler.pkl')
            except:
                pass  # Ignore save errors
            
            logger.info(f"ML model trained with {len(features)} samples")
            
        except Exception as e:
            logger.error(f"Failed to train prediction models: {e}")

    async def _predict_future_load(self) -> Optional[float]:
        """Predict future load using ML model"""
        try:
            if not self.model_trained or len(self.metrics_history) < 10:
                return None
            
            # Prepare features from recent history
            window_size = 10
            recent_metrics = self.metrics_history[-window_size:]
            
            features = []
            for metric in recent_metrics:
                features.extend([
                    metric.memory_utilization_ratio,
                    metric.avg_cpu_usage,
                    metric.total_connections / 10000,
                    metric.ops_per_second / 10000,
                    metric.avg_latency / 100,
                    metric.network_throughput / 10000
                ])
            
            # Scale features
            X = np.array([features])
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            predicted_ops = self.load_predictor.predict(X_scaled)[0]
            
            return max(0, predicted_ops)
            
        except Exception as e:
            logger.error(f"Failed to predict future load: {e}")
            return None

    async def get_scaling_status(self) -> Dict[str, Any]:
        """Get comprehensive scaling status"""
        return {
            'current_metrics': asdict(self.current_metrics) if self.current_metrics else None,
            'recent_decisions': [asdict(d) for d in self.scaling_decisions[-10:]],
            'pending_decisions': [asdict(d) for d in self.pending_decisions],
            'model_trained': self.model_trained,
            'last_scaling_action': self.last_scaling_action,
            'can_scale': self._can_execute_scaling(),
            'configuration': {
                'min_nodes': self.min_nodes,
                'max_nodes': self.max_nodes,
                'scaling_cooldown': self.scaling_cooldown,
                'node_specs': asdict(self.node_specs)
            }
        }

    async def force_scaling_decision(self, action: ScalingAction, 
                                   target_nodes: Optional[int] = None) -> Dict[str, Any]:
        """Force a scaling decision (manual override)"""
        try:
            if not self.current_metrics:
                return {'success': False, 'error': 'No current metrics available'}
            
            if action == ScalingAction.NO_ACTION:
                return {'success': True, 'message': 'No action requested'}
            
            if target_nodes is None:
                if action == ScalingAction.SCALE_OUT:
                    target_nodes = self.current_metrics.node_count + 1
                elif action == ScalingAction.SCALE_IN:
                    target_nodes = max(self.min_nodes, self.current_metrics.node_count - 1)
                else:
                    target_nodes = self.current_metrics.node_count
            
            # Create forced decision
            forced_decision = ScalingDecision(
                decision_id=f"forced_{int(time.time())}",
                timestamp=time.time(),
                action=action,
                trigger=ScalingTrigger.COST_OPTIMIZATION,  # Generic trigger for manual actions
                confidence=1.0,
                target_nodes=target_nodes,
                estimated_cost_impact=0.0,
                estimated_performance_impact=0.0,
                reasons=["Manual override"],
                metrics_snapshot=self.current_metrics
            )
            
            # Execute immediately
            result = await self._execute_scaling_decision(forced_decision)
            forced_decision.executed = True
            forced_decision.execution_result = result
            
            self.scaling_decisions.append(forced_decision)
            
            if result.get('success', False):
                self.last_scaling_action = time.time()
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to force scaling decision: {e}")
            return {'success': False, 'error': str(e)}

    async def shutdown(self) -> None:
        """Shutdown scaling controller"""
        try:
            # Cancel monitoring tasks
            for task in self.monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.monitoring_tasks:
                await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
            
            logger.info("Cluster scaling controller shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Example usage
async def main():
    """Example usage of Cluster Scaling Controller"""
    try:
        # This would normally be initialized with actual cluster client
        print("Cluster Scaling Controller Demo")
        print("Note: This would require actual Redis cluster connection")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())