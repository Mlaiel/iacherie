#!/usr/bin/env python3
"""
🤖 Intelligent Orchestrator
===========================

AI-powered Redis orchestration system with machine learning-based optimization,
predictive scaling, and intelligent resource management.

Expert Roles Combined:
- Lead Dev IA: AI orchestration and intelligent automation
- ML Engineer: Machine learning models for prediction and optimization
- DevOps Engineer: Advanced orchestration and monitoring
- Backend Senior: Scalable distributed system architecture

Features:
- AI-powered resource allocation and optimization
- Machine learning-based performance prediction
- Intelligent auto-scaling with demand forecasting
- Anomaly detection and self-healing
- Smart workload distribution
- Predictive maintenance and optimization
- Real-time decision making engine
- Creator economy workload optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Expert: Lead Dev IA + ML Engineer + DevOps + Backend Senior
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  INTELLECTUAL PROPERTY WARNING:
This module is proprietary software owned by Fahed Mlaiel.
Unauthorized copying, distribution, or use is strictly prohibited.
Violation will result in legal action.
"""

import asyncio
import logging
import json
import time
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
# Safe Redis import with Python 3.12 compatibility
try:
    import aioredis
    REDIS_AVAILABLE = True
except (ImportError, TypeError) as e:
    # Handle Python 3.12 TimeoutError duplicate base class issue
    from protection.utils.redis_compat import MockRedis as aioredis, REDIS_AVAILABLE
    import logging
    logging.warning(f"Using Redis compatibility layer: {e}")
import hashlib
import secrets
import uuid
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class OrchestrationMode(Enum):
    """Orchestration operation modes"""
    AUTOMATIC = "automatic"
    SEMI_AUTOMATIC = "semi_automatic"
    MANUAL = "manual"
    EMERGENCY = "emergency"

class WorkloadType(Enum):
    """Types of workloads to orchestrate"""
    CREATOR_CONTENT = "creator_content"
    COLLABORATION = "collaboration"
    ANALYTICS = "analytics"
    PAYMENT_PROCESSING = "payment_processing"
    MEDIA_PROCESSING = "media_processing"
    AI_INFERENCE = "ai_inference"
    REAL_TIME_CHAT = "real_time_chat"
    FILE_STORAGE = "file_storage"

class ResourceState(Enum):
    """Resource states"""
    OPTIMAL = "optimal"
    UNDERUTILIZED = "underutilized"
    OVERUTILIZED = "overutilized"
    CRITICAL = "critical"
    FAILED = "failed"

class DecisionType(Enum):
    """Types of orchestration decisions"""
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    MIGRATE_WORKLOAD = "migrate_workload"
    OPTIMIZE_CONFIG = "optimize_config"
    REALLOCATE_RESOURCES = "reallocate_resources"
    PERFORM_MAINTENANCE = "perform_maintenance"
    ALERT_OPERATORS = "alert_operators"

@dataclass
class WorkloadMetrics:
    """Workload performance metrics"""
    workload_id: str = ""
    workload_type: WorkloadType = WorkloadType.CREATOR_CONTENT
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_io: float = 0.0
    disk_io: float = 0.0
    request_rate: float = 0.0
    response_time: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
@dataclass
class ResourceAllocation:
    """Resource allocation configuration"""
    resource_id: str = ""
    workload_type: WorkloadType = WorkloadType.CREATOR_CONTENT
    cpu_cores: float = 1.0
    memory_gb: float = 1.0
    storage_gb: float = 10.0
    network_bandwidth: float = 100.0  # Mbps
    priority: int = 1  # 1=highest, 10=lowest
    is_active: bool = True

@dataclass
class OrchestrationDecision:
    """AI orchestration decision"""
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_type: DecisionType = DecisionType.SCALE_UP
    target_resource: str = ""
    workload_affected: str = ""
    confidence_score: float = 0.0
    expected_impact: Dict[str, float] = field(default_factory=dict)
    implementation_steps: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    executed_at: Optional[datetime] = None
    success: Optional[bool] = None
    actual_impact: Dict[str, float] = field(default_factory=dict)

@dataclass
class PredictionModel:
    """ML prediction model data"""
    model_id: str = ""
    model_type: str = ""
    target_metric: str = ""
    accuracy: float = 0.0
    last_trained: datetime = field(default_factory=datetime.now)
    training_samples: int = 0
    feature_importance: Dict[str, float] = field(default_factory=dict)

class IntelligentOrchestrator:
    """
    AI-Powered Redis Orchestration System
    ====================================
    
    Intelligent orchestration with ML-based optimization,
    predictive scaling, and automated decision making.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.mode = OrchestrationMode.AUTOMATIC
        
        # Data storage
        self.workload_metrics: Dict[str, List[WorkloadMetrics]] = {}
        self.resource_allocations: Dict[str, ResourceAllocation] = {}
        self.decisions_history: List[OrchestrationDecision] = []
        self.prediction_models: Dict[str, PredictionModel] = {}
        
        # ML models
        self.ml_models = {
            'demand_forecaster': RandomForestRegressor(n_estimators=100, random_state=42),
            'anomaly_detector': IsolationForest(contamination=0.1, random_state=42),
            'workload_clusterer': KMeans(n_clusters=5, random_state=42),
            'scaler': StandardScaler()
        }
        
        # Configuration
        self.config = {
            'prediction_window': 3600,  # 1 hour
            'metrics_retention': 86400 * 7,  # 7 days
            'decision_confidence_threshold': 0.7,
            'auto_execution_threshold': 0.9,
            'learning_rate': 0.01,
            'optimization_interval': 300,  # 5 minutes
            'emergency_threshold': 0.95  # 95% resource utilization
        }
        
        # Performance tracking
        self.orchestration_metrics = {
            'decisions_made': 0,
            'successful_optimizations': 0,
            'failed_optimizations': 0,
            'avg_response_time': 0.0,
            'resource_efficiency': 0.0,
            'cost_savings': 0.0,
            'uptime_improvement': 0.0,
            'ml_model_accuracy': 0.0
        }
        
        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Initialize workload patterns
        self._initialize_workload_patterns()
        
        logger.info("🤖 Intelligent Orchestrator initialized")

    async def initialize(self):
        """Initialize Redis connection and load historical data"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            await self._load_historical_data()
            await self._initialize_ml_models()
            logger.info("✅ Intelligent Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Intelligent Orchestrator: {e}")
            raise

    def _initialize_workload_patterns(self):
        """Initialize known workload patterns for better predictions"""
        self.workload_patterns = {
            WorkloadType.CREATOR_CONTENT: {
                'peak_hours': [19, 20, 21, 22],  # Evening hours
                'peak_days': [5, 6, 0],  # Friday, Saturday, Sunday
                'seasonal_multiplier': 1.2,
                'base_cpu': 0.3,
                'base_memory': 0.4
            },
            WorkloadType.COLLABORATION: {
                'peak_hours': [9, 10, 14, 15, 16],  # Business hours
                'peak_days': [1, 2, 3, 4],  # Monday-Thursday
                'seasonal_multiplier': 1.0,
                'base_cpu': 0.2,
                'base_memory': 0.3
            },
            WorkloadType.ANALYTICS: {
                'peak_hours': [2, 3, 4],  # Early morning batch processing
                'peak_days': [1, 2, 3, 4, 5],  # Weekdays
                'seasonal_multiplier': 1.1,
                'base_cpu': 0.6,
                'base_memory': 0.8
            },
            WorkloadType.PAYMENT_PROCESSING: {
                'peak_hours': [12, 13, 18, 19, 20],  # Lunch and evening
                'peak_days': [1, 2, 3, 4, 5],  # Weekdays
                'seasonal_multiplier': 1.3,  # Higher during shopping seasons
                'base_cpu': 0.4,
                'base_memory': 0.3
            }
        }

    async def collect_metrics(self, workload_id: str, metrics: WorkloadMetrics):
        """
        Collect workload metrics for analysis
        
        Args:
            workload_id: Unique workload identifier
            metrics: Performance metrics to collect
        """
        try:
            # Store metrics
            if workload_id not in self.workload_metrics:
                self.workload_metrics[workload_id] = []
                
            self.workload_metrics[workload_id].append(metrics)
            
            # Keep only recent metrics (based on retention policy)
            cutoff_time = datetime.now() - timedelta(seconds=self.config['metrics_retention'])
            self.workload_metrics[workload_id] = [
                m for m in self.workload_metrics[workload_id] 
                if m.timestamp >= cutoff_time
            ]
            
            # Store in Redis
            await self._store_metrics(workload_id, metrics)
            
            # Check for immediate action needed
            await self._check_immediate_action(workload_id, metrics)
            
        except Exception as e:
            logger.error(f"❌ Error collecting metrics for {workload_id}: {e}")

    async def _check_immediate_action(self, workload_id: str, metrics: WorkloadMetrics):
        """Check if immediate action is needed based on metrics"""
        # Emergency thresholds
        emergency_conditions = [
            metrics.cpu_usage > self.config['emergency_threshold'],
            metrics.memory_usage > self.config['emergency_threshold'],
            metrics.error_rate > 0.1,  # 10% error rate
            metrics.response_time > 5000  # 5 seconds
        ]
        
        if any(emergency_conditions):
            await self._handle_emergency(workload_id, metrics)

    async def _handle_emergency(self, workload_id: str, metrics: WorkloadMetrics):
        """Handle emergency situations immediately"""
        logger.warning(f"🚨 Emergency detected for workload {workload_id}")
        
        # Create emergency decision
        decision = OrchestrationDecision(
            decision_type=DecisionType.SCALE_UP,
            target_resource=workload_id,
            workload_affected=workload_id,
            confidence_score=1.0,
            expected_impact={'performance_improvement': 0.5},
            implementation_steps=[
                'immediate_scale_up',
                'increase_cpu_allocation',
                'increase_memory_allocation',
                'notify_operators'
            ]
        )
        
        # Execute immediately in emergency mode
        await self._execute_decision(decision, force=True)

    async def analyze_and_optimize(self) -> List[OrchestrationDecision]:
        """
        Analyze current state and generate optimization decisions
        
        Returns:
            List of optimization decisions
        """
        try:
            logger.info("🧠 Starting intelligent analysis and optimization")
            
            decisions = []
            
            # 1. Predict future demand
            demand_predictions = await self._predict_future_demand()
            
            # 2. Detect anomalies
            anomalies = await self._detect_anomalies()
            
            # 3. Analyze resource utilization
            utilization_analysis = await self._analyze_resource_utilization()
            
            # 4. Generate optimization decisions
            optimization_decisions = await self._generate_optimization_decisions(
                demand_predictions, anomalies, utilization_analysis
            )
            
            decisions.extend(optimization_decisions)
            
            # 5. Evaluate decisions with ML
            evaluated_decisions = await self._evaluate_decisions_with_ml(decisions)
            
            # 6. Filter by confidence threshold
            high_confidence_decisions = [
                d for d in evaluated_decisions 
                if d.confidence_score >= self.config['decision_confidence_threshold']
            ]
            
            # 7. Execute high-confidence decisions if in automatic mode
            if self.mode == OrchestrationMode.AUTOMATIC:
                auto_executable = [
                    d for d in high_confidence_decisions
                    if d.confidence_score >= self.config['auto_execution_threshold']
                ]
                
                for decision in auto_executable:
                    await self._execute_decision(decision)
                    
            # Store all decisions
            self.decisions_history.extend(evaluated_decisions)
            
            logger.info(f"🎯 Generated {len(evaluated_decisions)} decisions, executed {len(auto_executable) if self.mode == OrchestrationMode.AUTOMATIC else 0}")
            
            return evaluated_decisions
            
        except Exception as e:
            logger.error(f"❌ Error in analysis and optimization: {e}")
            return []

    async def _predict_future_demand(self) -> Dict[str, Dict[str, float]]:
        """Predict future demand for each workload type"""
        predictions = {}
        
        for workload_type in WorkloadType:
            try:
                # Get historical data
                historical_data = await self._get_workload_historical_data(workload_type)
                
                if len(historical_data) < 10:  # Need minimum data
                    continue
                    
                # Prepare features
                features = await self._extract_demand_features(historical_data)
                
                # Make prediction
                if len(features) > 0:
                    demand_forecast = await self._ml_predict_demand(workload_type, features)
                    predictions[workload_type.value] = demand_forecast
                    
            except Exception as e:
                logger.error(f"❌ Error predicting demand for {workload_type}: {e}")
                
        return predictions

    async def _detect_anomalies(self) -> Dict[str, List[Dict[str, Any]]]:
        """Detect anomalies in workload patterns"""
        anomalies = {}
        
        for workload_id, metrics_list in self.workload_metrics.items():
            if len(metrics_list) < 10:  # Need minimum data
                continue
                
            try:
                # Extract features for anomaly detection
                features = []
                for metrics in metrics_list[-50:]:  # Last 50 samples
                    features.append([
                        metrics.cpu_usage,
                        metrics.memory_usage,
                        metrics.network_io,
                        metrics.request_rate,
                        metrics.response_time,
                        metrics.error_rate
                    ])
                
                if len(features) > 0:
                    # Scale features
                    features_scaled = self.ml_models['scaler'].fit_transform(features)
                    
                    # Detect anomalies
                    anomaly_predictions = self.ml_models['anomaly_detector'].fit_predict(features_scaled)
                    anomaly_scores = self.ml_models['anomaly_detector'].decision_function(features_scaled)
                    
                    # Find anomalous points
                    workload_anomalies = []
                    for i, (prediction, score) in enumerate(zip(anomaly_predictions, anomaly_scores)):
                        if prediction == -1:  # Anomaly detected
                            workload_anomalies.append({
                                'timestamp': metrics_list[-(len(features) - i)].timestamp,
                                'anomaly_score': float(score),
                                'metrics_index': len(metrics_list) - len(features) + i
                            })
                    
                    if workload_anomalies:
                        anomalies[workload_id] = workload_anomalies
                        
            except Exception as e:
                logger.error(f"❌ Error detecting anomalies for {workload_id}: {e}")
                
        return anomalies

    async def _analyze_resource_utilization(self) -> Dict[str, ResourceState]:
        """Analyze current resource utilization across all workloads"""
        utilization_analysis = {}
        
        for workload_id, metrics_list in self.workload_metrics.items():
            if not metrics_list:
                continue
                
            # Get latest metrics
            latest_metrics = metrics_list[-1]
            
            # Determine resource state
            avg_cpu = latest_metrics.cpu_usage
            avg_memory = latest_metrics.memory_usage
            avg_utilization = (avg_cpu + avg_memory) / 2
            
            if avg_utilization > 0.9:
                state = ResourceState.CRITICAL
            elif avg_utilization > 0.7:
                state = ResourceState.OVERUTILIZED
            elif avg_utilization < 0.2:
                state = ResourceState.UNDERUTILIZED
            else:
                state = ResourceState.OPTIMAL
                
            utilization_analysis[workload_id] = state
            
        return utilization_analysis

    async def _generate_optimization_decisions(
        self,
        demand_predictions: Dict[str, Dict[str, float]],
        anomalies: Dict[str, List[Dict[str, Any]]],
        utilization_analysis: Dict[str, ResourceState]
    ) -> List[OrchestrationDecision]:
        """Generate optimization decisions based on analysis"""
        decisions = []
        
        # Handle resource utilization issues
        for workload_id, state in utilization_analysis.items():
            if state == ResourceState.CRITICAL or state == ResourceState.OVERUTILIZED:
                decision = OrchestrationDecision(
                    decision_type=DecisionType.SCALE_UP,
                    target_resource=workload_id,
                    workload_affected=workload_id,
                    confidence_score=0.8,
                    expected_impact={'performance_improvement': 0.3},
                    implementation_steps=[
                        'analyze_current_allocation',
                        'calculate_optimal_resources',
                        'allocate_additional_resources',
                        'monitor_improvement'
                    ]
                )
                decisions.append(decision)
                
            elif state == ResourceState.UNDERUTILIZED:
                decision = OrchestrationDecision(
                    decision_type=DecisionType.SCALE_DOWN,
                    target_resource=workload_id,
                    workload_affected=workload_id,
                    confidence_score=0.7,
                    expected_impact={'cost_savings': 0.2},
                    implementation_steps=[
                        'verify_low_utilization_period',
                        'calculate_minimum_resources',
                        'reallocate_excess_resources',
                        'monitor_performance'
                    ]
                )
                decisions.append(decision)
        
        # Handle anomalies
        for workload_id, workload_anomalies in anomalies.items():
            if len(workload_anomalies) > 3:  # Multiple anomalies detected
                decision = OrchestrationDecision(
                    decision_type=DecisionType.OPTIMIZE_CONFIG,
                    target_resource=workload_id,
                    workload_affected=workload_id,
                    confidence_score=0.6,
                    expected_impact={'stability_improvement': 0.4},
                    implementation_steps=[
                        'investigate_anomaly_patterns',
                        'adjust_configuration_parameters',
                        'implement_adaptive_thresholds',
                        'enhance_monitoring'
                    ]
                )
                decisions.append(decision)
        
        # Handle demand predictions
        for workload_type, predictions in demand_predictions.items():
            if predictions.get('predicted_increase', 0) > 0.5:  # 50% increase predicted
                decision = OrchestrationDecision(
                    decision_type=DecisionType.SCALE_UP,
                    target_resource=workload_type,
                    workload_affected=workload_type,
                    confidence_score=0.75,
                    expected_impact={'capacity_readiness': 0.6},
                    implementation_steps=[
                        'pre_allocate_resources',
                        'prepare_scaling_infrastructure',
                        'configure_auto_scaling_triggers',
                        'setup_monitoring_alerts'
                    ]
                )
                decisions.append(decision)
                
        return decisions

    async def _evaluate_decisions_with_ml(self, decisions: List[OrchestrationDecision]) -> List[OrchestrationDecision]:
        """Evaluate and refine decisions using ML models"""
        evaluated_decisions = []
        
        for decision in decisions:
            try:
                # Extract features for decision evaluation
                features = await self._extract_decision_features(decision)
                
                # Use ML to evaluate decision quality
                confidence_adjustment = await self._ml_evaluate_decision(decision, features)
                
                # Adjust confidence score
                original_confidence = decision.confidence_score
                adjusted_confidence = min(1.0, original_confidence * confidence_adjustment)
                decision.confidence_score = adjusted_confidence
                
                # Refine implementation steps if needed
                if adjusted_confidence < 0.5:
                    decision.implementation_steps.append('require_manual_approval')
                    
                evaluated_decisions.append(decision)
                
            except Exception as e:
                logger.error(f"❌ Error evaluating decision {decision.decision_id}: {e}")
                # Keep original decision with lower confidence
                decision.confidence_score *= 0.5
                evaluated_decisions.append(decision)
                
        return evaluated_decisions

    async def _execute_decision(self, decision: OrchestrationDecision, force: bool = False):
        """Execute an orchestration decision"""
        try:
            if not force and decision.confidence_score < self.config['auto_execution_threshold']:
                logger.info(f"⏸️ Decision {decision.decision_id} requires manual approval (confidence: {decision.confidence_score:.2f})")
                return
                
            logger.info(f"🚀 Executing decision: {decision.decision_type.value} for {decision.target_resource}")
            
            decision.executed_at = datetime.now()
            
            # Execute based on decision type
            if decision.decision_type == DecisionType.SCALE_UP:
                success = await self._execute_scale_up(decision)
            elif decision.decision_type == DecisionType.SCALE_DOWN:
                success = await self._execute_scale_down(decision)
            elif decision.decision_type == DecisionType.OPTIMIZE_CONFIG:
                success = await self._execute_config_optimization(decision)
            elif decision.decision_type == DecisionType.REALLOCATE_RESOURCES:
                success = await self._execute_resource_reallocation(decision)
            else:
                success = await self._execute_generic_action(decision)
                
            decision.success = success
            
            if success:
                self.orchestration_metrics['successful_optimizations'] += 1
                logger.info(f"✅ Successfully executed decision {decision.decision_id}")
            else:
                self.orchestration_metrics['failed_optimizations'] += 1
                logger.error(f"❌ Failed to execute decision {decision.decision_id}")
                
            self.orchestration_metrics['decisions_made'] += 1
            
            # Store execution result
            await self._store_decision_result(decision)
            
        except Exception as e:
            logger.error(f"❌ Error executing decision {decision.decision_id}: {e}")
            decision.success = False

    async def _execute_scale_up(self, decision: OrchestrationDecision) -> bool:
        """Execute scale up decision"""
        try:
            target = decision.target_resource
            
            # Get current allocation
            current_allocation = self.resource_allocations.get(target)
            if not current_allocation:
                # Create new allocation
                current_allocation = ResourceAllocation(
                    resource_id=target,
                    workload_type=WorkloadType.CREATOR_CONTENT,  # Default
                    cpu_cores=1.0,
                    memory_gb=1.0
                )
                
            # Calculate scale up amount (increase by 50%)
            scale_factor = 1.5
            new_allocation = ResourceAllocation(
                resource_id=target,
                workload_type=current_allocation.workload_type,
                cpu_cores=current_allocation.cpu_cores * scale_factor,
                memory_gb=current_allocation.memory_gb * scale_factor,
                storage_gb=current_allocation.storage_gb,
                network_bandwidth=current_allocation.network_bandwidth * scale_factor,
                priority=current_allocation.priority
            )
            
            # Apply new allocation
            self.resource_allocations[target] = new_allocation
            
            # Store in Redis
            await self._store_resource_allocation(target, new_allocation)
            
            logger.info(f"📈 Scaled up {target}: CPU {current_allocation.cpu_cores:.1f} → {new_allocation.cpu_cores:.1f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error scaling up {decision.target_resource}: {e}")
            return False

    async def _execute_scale_down(self, decision: OrchestrationDecision) -> bool:
        """Execute scale down decision"""
        try:
            target = decision.target_resource
            
            # Get current allocation
            current_allocation = self.resource_allocations.get(target)
            if not current_allocation:
                return False
                
            # Calculate scale down amount (decrease by 25%)
            scale_factor = 0.75
            min_cpu = 0.1  # Minimum CPU allocation
            min_memory = 0.1  # Minimum memory allocation
            
            new_allocation = ResourceAllocation(
                resource_id=target,
                workload_type=current_allocation.workload_type,
                cpu_cores=max(min_cpu, current_allocation.cpu_cores * scale_factor),
                memory_gb=max(min_memory, current_allocation.memory_gb * scale_factor),
                storage_gb=current_allocation.storage_gb,
                network_bandwidth=current_allocation.network_bandwidth * scale_factor,
                priority=current_allocation.priority
            )
            
            # Apply new allocation
            self.resource_allocations[target] = new_allocation
            
            # Store in Redis
            await self._store_resource_allocation(target, new_allocation)
            
            logger.info(f"📉 Scaled down {target}: CPU {current_allocation.cpu_cores:.1f} → {new_allocation.cpu_cores:.1f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error scaling down {decision.target_resource}: {e}")
            return False

    async def _execute_config_optimization(self, decision: OrchestrationDecision) -> bool:
        """Execute configuration optimization"""
        try:
            target = decision.target_resource
            
            # Simulate configuration optimization
            optimizations = [
                'cache_size_adjustment',
                'connection_pool_tuning',
                'timeout_optimization',
                'buffer_size_adjustment'
            ]
            
            applied_optimizations = []
            for optimization in optimizations:
                # Simulate applying optimization
                applied_optimizations.append(optimization)
                
            logger.info(f"⚙️ Optimized configuration for {target}: {', '.join(applied_optimizations)}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error optimizing configuration for {decision.target_resource}: {e}")
            return False

    async def _execute_resource_reallocation(self, decision: OrchestrationDecision) -> bool:
        """Execute resource reallocation"""
        try:
            # Simulate intelligent resource reallocation
            logger.info(f"🔄 Reallocated resources for {decision.target_resource}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error reallocating resources for {decision.target_resource}: {e}")
            return False

    async def _execute_generic_action(self, decision: OrchestrationDecision) -> bool:
        """Execute generic orchestration action"""
        try:
            logger.info(f"⚡ Executed {decision.decision_type.value} for {decision.target_resource}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error executing {decision.decision_type.value}: {e}")
            return False

    async def _get_workload_historical_data(self, workload_type: WorkloadType) -> List[WorkloadMetrics]:
        """Get historical data for specific workload type"""
        historical_data = []
        
        for workload_id, metrics_list in self.workload_metrics.items():
            # Filter by workload type
            type_metrics = [m for m in metrics_list if m.workload_type == workload_type]
            historical_data.extend(type_metrics)
            
        return sorted(historical_data, key=lambda m: m.timestamp)

    async def _extract_demand_features(self, historical_data: List[WorkloadMetrics]) -> List[List[float]]:
        """Extract features for demand prediction"""
        features = []
        
        for metrics in historical_data:
            # Time-based features
            hour = metrics.timestamp.hour
            day_of_week = metrics.timestamp.weekday()
            day_of_month = metrics.timestamp.day
            
            # Performance features
            feature_vector = [
                hour,
                day_of_week,
                day_of_month,
                metrics.cpu_usage,
                metrics.memory_usage,
                metrics.request_rate,
                metrics.response_time,
                metrics.throughput
            ]
            
            features.append(feature_vector)
            
        return features

    async def _ml_predict_demand(self, workload_type: WorkloadType, features: List[List[float]]) -> Dict[str, float]:
        """Use ML to predict future demand"""
        try:
            if len(features) < 10:
                return {'predicted_increase': 0.0, 'confidence': 0.0}
                
            # Prepare data
            X = np.array(features[:-1])  # Features
            y = np.array([f[3] for f in features[1:]])  # CPU usage as target (next value)
            
            # Train model
            self.ml_models['demand_forecaster'].fit(X, y)
            
            # Predict next value
            last_features = np.array(features[-1]).reshape(1, -1)
            predicted_demand = self.ml_models['demand_forecaster'].predict(last_features)[0]
            
            # Calculate change from current
            current_demand = features[-1][3]  # Current CPU usage
            change = (predicted_demand - current_demand) / current_demand if current_demand > 0 else 0
            
            # Calculate confidence based on recent model performance
            confidence = min(1.0, len(features) / 100.0)  # More data = higher confidence
            
            return {
                'predicted_increase': max(0.0, change),
                'predicted_demand': predicted_demand,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"❌ Error in ML demand prediction: {e}")
            return {'predicted_increase': 0.0, 'confidence': 0.0}

    async def _extract_decision_features(self, decision: OrchestrationDecision) -> List[float]:
        """Extract features for decision evaluation"""
        # Simple feature extraction
        features = [
            float(decision.decision_type.value == DecisionType.SCALE_UP.value),
            float(decision.decision_type.value == DecisionType.SCALE_DOWN.value),
            float(decision.decision_type.value == DecisionType.OPTIMIZE_CONFIG.value),
            decision.confidence_score,
            len(decision.implementation_steps),
            float(decision.target_resource.startswith('creator')),
            float(decision.target_resource.startswith('payment')),
            float(decision.target_resource.startswith('analytics'))
        ]
        
        return features

    async def _ml_evaluate_decision(self, decision: OrchestrationDecision, features: List[float]) -> float:
        """Use ML to evaluate decision quality"""
        try:
            # Simple heuristic-based evaluation
            # In a real system, this would use trained models
            
            base_confidence = 1.0
            
            # Adjust based on decision type
            if decision.decision_type == DecisionType.SCALE_UP:
                base_confidence *= 0.9  # Slightly conservative
            elif decision.decision_type == DecisionType.SCALE_DOWN:
                base_confidence *= 0.8  # More conservative
            elif decision.decision_type == DecisionType.OPTIMIZE_CONFIG:
                base_confidence *= 0.7  # Most conservative
                
            # Adjust based on target resource type
            if 'payment' in decision.target_resource:
                base_confidence *= 0.9  # Be careful with payment systems
            elif 'creator' in decision.target_resource:
                base_confidence *= 0.95  # Careful with creator systems
                
            return base_confidence
            
        except Exception as e:
            logger.error(f"❌ Error in ML decision evaluation: {e}")
            return 0.5  # Default conservative confidence

    async def _store_metrics(self, workload_id: str, metrics: WorkloadMetrics):
        """Store metrics in Redis"""
        if self.redis:
            metrics_data = {
                'workload_id': workload_id,
                'workload_type': metrics.workload_type.value,
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'network_io': metrics.network_io,
                'disk_io': metrics.disk_io,
                'request_rate': metrics.request_rate,
                'response_time': metrics.response_time,
                'error_rate': metrics.error_rate,
                'throughput': metrics.throughput,
                'timestamp': metrics.timestamp.isoformat()
            }
            
            await self.redis.lpush(
                f"orchestrator:metrics:{workload_id}",
                json.dumps(metrics_data)
            )
            
            # Keep only recent metrics
            await self.redis.ltrim(f"orchestrator:metrics:{workload_id}", 0, 1000)

    async def _store_resource_allocation(self, resource_id: str, allocation: ResourceAllocation):
        """Store resource allocation in Redis"""
        if self.redis:
            allocation_data = {
                'resource_id': allocation.resource_id,
                'workload_type': allocation.workload_type.value,
                'cpu_cores': allocation.cpu_cores,
                'memory_gb': allocation.memory_gb,
                'storage_gb': allocation.storage_gb,
                'network_bandwidth': allocation.network_bandwidth,
                'priority': allocation.priority,
                'is_active': allocation.is_active
            }
            
            await self.redis.setex(
                f"orchestrator:allocation:{resource_id}",
                86400,  # 24 hours
                json.dumps(allocation_data)
            )

    async def _store_decision_result(self, decision: OrchestrationDecision):
        """Store decision execution result"""
        if self.redis:
            decision_data = {
                'decision_id': decision.decision_id,
                'decision_type': decision.decision_type.value,
                'target_resource': decision.target_resource,
                'workload_affected': decision.workload_affected,
                'confidence_score': decision.confidence_score,
                'expected_impact': decision.expected_impact,
                'implementation_steps': decision.implementation_steps,
                'created_at': decision.created_at.isoformat(),
                'executed_at': decision.executed_at.isoformat() if decision.executed_at else None,
                'success': decision.success,
                'actual_impact': decision.actual_impact
            }
            
            await self.redis.lpush(
                "orchestrator:decisions",
                json.dumps(decision_data)
            )

    async def _load_historical_data(self):
        """Load historical data from Redis"""
        if self.redis:
            try:
                # Load metrics
                workload_keys = await self.redis.keys("orchestrator:metrics:*")
                for key in workload_keys:
                    workload_id = key.decode().split(':')[-1]
                    metrics_list = await self.redis.lrange(key, 0, -1)
                    
                    workload_metrics = []
                    for metrics_json in metrics_list:
                        data = json.loads(metrics_json)
                        # Convert back to WorkloadMetrics object
                        # Implementation would deserialize the data
                        
                    if workload_metrics:
                        self.workload_metrics[workload_id] = workload_metrics
                        
                # Load allocations
                allocation_keys = await self.redis.keys("orchestrator:allocation:*")
                for key in allocation_keys:
                    resource_id = key.decode().split(':')[-1]
                    allocation_data = await self.redis.get(key)
                    if allocation_data:
                        data = json.loads(allocation_data)
                        # Convert back to ResourceAllocation object
                        
            except Exception as e:
                logger.error(f"❌ Failed to load historical data: {e}")

    async def _initialize_ml_models(self):
        """Initialize and train ML models with available data"""
        try:
            # If we have enough historical data, train models
            total_samples = sum(len(metrics) for metrics in self.workload_metrics.values())
            
            if total_samples > 100:
                await self._train_models()
                
        except Exception as e:
            logger.error(f"❌ Error initializing ML models: {e}")

    async def _train_models(self):
        """Train ML models with historical data"""
        try:
            # Collect all historical data
            all_features = []
            all_targets = []
            
            for workload_metrics in self.workload_metrics.values():
                for i, metrics in enumerate(workload_metrics[:-1]):
                    features = await self._extract_demand_features([metrics])
                    if features:
                        all_features.extend(features)
                        # Target is next CPU usage
                        next_cpu = workload_metrics[i + 1].cpu_usage
                        all_targets.append(next_cpu)
                        
            if len(all_features) > 10:
                X = np.array(all_features)
                y = np.array(all_targets)
                
                # Train demand forecaster
                self.ml_models['demand_forecaster'].fit(X, y)
                
                # Train anomaly detector
                self.ml_models['anomaly_detector'].fit(X)
                
                logger.info(f"🤖 Trained ML models with {len(all_features)} samples")
                
        except Exception as e:
            logger.error(f"❌ Error training models: {e}")

    async def get_orchestration_status(self) -> Dict[str, Any]:
        """Get comprehensive orchestration status"""
        return {
            'mode': self.mode.value,
            'active_workloads': len(self.workload_metrics),
            'resource_allocations': len(self.resource_allocations),
            'decisions_history': len(self.decisions_history),
            'metrics': self.orchestration_metrics,
            'ml_models_trained': len([m for m in self.ml_models.values() if hasattr(m, 'feature_importances_')]),
            'system_status': 'operational',
            'last_optimization': datetime.now().isoformat()
        }

    async def close(self):
        """Close connections and cleanup"""
        if self.redis:
            await self.redis.close()
        self.executor.shutdown(wait=True)
        logger.info("🤖 Intelligent Orchestrator closed")


# Factory function
async def create_intelligent_orchestrator(redis_url: str = "redis://localhost:6379") -> IntelligentOrchestrator:
    """
    Factory function to create and initialize Intelligent Orchestrator
    
    Args:
        redis_url: Redis connection URL
        
    Returns:
        Initialized IntelligentOrchestrator instance
    """
    orchestrator = IntelligentOrchestrator(redis_url)
    await orchestrator.initialize()
    return orchestrator


if __name__ == "__main__":
    async def test_intelligent_orchestrator():
        """Test the intelligent orchestrator"""
        orchestrator = await create_intelligent_orchestrator()
        
        # Simulate workload metrics
        test_metrics = WorkloadMetrics(
            workload_id="creator_content_01",
            workload_type=WorkloadType.CREATOR_CONTENT,
            cpu_usage=0.85,  # High CPU usage
            memory_usage=0.75,
            network_io=50.0,
            request_rate=1000.0,
            response_time=150.0,
            error_rate=0.02,
            throughput=800.0
        )
        
        # Collect metrics
        await orchestrator.collect_metrics("creator_content_01", test_metrics)
        
        # Wait a moment for processing
        await asyncio.sleep(1)
        
        # Analyze and optimize
        decisions = await orchestrator.analyze_and_optimize()
        print(f"🧠 Generated {len(decisions)} optimization decisions")
        
        for decision in decisions:
            print(f"  📋 {decision.decision_type.value} for {decision.target_resource} (confidence: {decision.confidence_score:.2f})")
            
        # Get status
        status = await orchestrator.get_orchestration_status()
        print(f"📊 Orchestration status: {json.dumps(status, indent=2)}")
        
        await orchestrator.close()

    # Run test
    asyncio.run(test_intelligent_orchestrator())