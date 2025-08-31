"""Task Distribution Engine - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/queues/task_distribution_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Task Distribution & Load Balancing Engine
Responsibility: Intelligent task distribution with ML-powered load balancing
Technologies: ML-based distribution, Predictive analytics, Resource optimization
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Task analysis → Resource prediction → Agent selection → Load balancing → 
Performance monitoring → Optimization → Analytics → Predictive scaling
"""from typing import Any, Dict, List, Optional, Union, Set, Tuple, Callable
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import json
import uuid
import numpy as np
from collections import defaultdict, deque
import time
import hashlib
import heapq

from backend.core.managers.queue_manager import (
    IntelligentQueueManager, 
    TaskDefinition, 
    QueueType, 
    TaskPriority
)

logger = logging.getLogger(__name__)


class DistributionStrategy(Enum):
    """Task distribution strategies"""    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    RESOURCE_OPTIMIZED = "resource_optimized"
    PERFORMANCE_BASED = "performance_based"
    ML_PREDICTED = "ml_predicted"
    PLATFORM_SPECIALIZED = "platform_specialized"
    GEOGRAPHIC_OPTIMIZED = "geographic_optimized"


class TaskComplexity(Enum):
    """Task complexity classification"""    MINIMAL = "minimal"          # Simple URL checks
    STANDARD = "standard"        # Regular crawling
    COMPLEX = "complex"          # Deep analysis
    INTENSIVE = "intensive"      # Heavy processing
    ENTERPRISE = "enterprise"    # Multi-platform operations


class ResourceType(Enum):
    """Resource types for distribution"""    CPU_INTENSIVE = "cpu_intensive"
    MEMORY_INTENSIVE = "memory_intensive"
    NETWORK_INTENSIVE = "network_intensive"
    IO_INTENSIVE = "io_intensive"
    MIXED_WORKLOAD = "mixed_workload"


@dataclass
class AgentCapability:
    """Agent capability specification"""    agent_id: str
    platform_specialties: List[str] = field(default_factory=list)
    max_concurrent_tasks: int = 10
    cpu_capacity: float = 100.0
    memory_capacity_mb: int = 1024
    network_bandwidth_mbps: float = 100.0
    geographic_region: str = "global"
    success_rate: float = 0.95
    average_response_time_ms: float = 500.0
    supported_task_types: List[TaskComplexity] = field(default_factory=list)
    current_load: float = 0.0
    health_score: float = 1.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TaskResource:
    """Task resource requirements"""    task_id: str
    complexity: TaskComplexity
    resource_type: ResourceType
    estimated_cpu_usage: float = 10.0
    estimated_memory_mb: int = 128
    estimated_duration_seconds: float = 30.0
    network_requirement_mbps: float = 1.0
    platform_requirement: Optional[str] = None
    geographic_preference: Optional[str] = None
    deadline: Optional[datetime] = None
    priority_multiplier: float = 1.0


@dataclass
class DistributionResult:
    """Distribution decision result"""    task_id: str
    assigned_agent_id: Optional[str]
    distribution_strategy: DistributionStrategy
    confidence_score: float
    estimated_completion_time: Optional[datetime]
    resource_efficiency_score: float
    reason: str
    alternative_agents: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)


@dataclass
class LoadBalancingMetrics:
    """Load balancing performance metrics"""    total_distributions: int = 0
    successful_distributions: int = 0
    failed_distributions: int = 0
    average_distribution_time_ms: float = 0.0
    resource_utilization_efficiency: float = 0.0
    load_balance_score: float = 0.0
    agent_health_average: float = 1.0
    prediction_accuracy: float = 0.95
    last_updated: datetime = field(default_factory=datetime.utcnow)


class MLDistributionPredictor:
    """Machine learning-based distribution predictor"""    
    def __init__(self):
        self.historical_data: List[Dict] = []
        self.prediction_model = None
        self.feature_weights = {
            'agent_load': 0.3,
            'success_rate': 0.25,
            'response_time': 0.2,
            'resource_match': 0.15,
            'geographic_match': 0.1
        }
        
    async def predict_best_agent(self, 
                                task: TaskResource, 
                                available_agents: List[AgentCapability]) -> Tuple[str, float]:
        """Predict best agent using ML algorithms"""        
        if not available_agents:
            return None, 0.0
            
        agent_scores = []
        
        for agent in available_agents:
            score = await self._calculate_agent_score(task, agent)
            agent_scores.append((agent.agent_id, score))
        
        # Sort by score (highest first)
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        best_agent_id, best_score = agent_scores[0]
        
        # Store prediction for learning
        await self._store_prediction(task, best_agent_id, best_score)
        
        return best_agent_id, best_score
    
    async def _calculate_agent_score(self, 
                                   task: TaskResource, 
                                   agent: AgentCapability) -> float:
        """Calculate agent suitability score"""        
        score = 0.0
        
        # Load-based scoring (inverse relationship)
        load_score = max(0, (1.0 - agent.current_load)) * self.feature_weights['agent_load']
        score += load_score
        
        # Success rate scoring
        success_score = agent.success_rate * self.feature_weights['success_rate']
        score += success_score
        
        # Response time scoring (inverse relationship)
        response_score = max(0, (1000 - agent.average_response_time_ms) / 1000) * self.feature_weights['response_time']
        score += response_score
        
        # Resource matching scoring
        resource_score = await self._calculate_resource_match(task, agent) * self.feature_weights['resource_match']
        score += resource_score
        
        # Geographic matching scoring
        geo_score = await self._calculate_geographic_match(task, agent) * self.feature_weights['geographic_match']
        score += geo_score
        
        # Health penalty
        score *= agent.health_score
        
        return min(1.0, max(0.0, score))
    
    async def _calculate_resource_match(self, 
                                      task: TaskResource, 
                                      agent: AgentCapability) -> float:
        """Calculate resource compatibility score"""        
        # Check CPU capacity
        cpu_match = 1.0 if agent.cpu_capacity >= task.estimated_cpu_usage else 0.5
        
        # Check memory capacity
        memory_match = 1.0 if agent.memory_capacity_mb >= task.estimated_memory_mb else 0.5
        
        # Check network capacity
        network_match = 1.0 if agent.network_bandwidth_mbps >= task.network_requirement_mbps else 0.5
        
        # Check task complexity support
        complexity_match = 1.0 if task.complexity in agent.supported_task_types else 0.3
        
        # Check platform specialty
        platform_match = 1.0
        if task.platform_requirement:
            platform_match = 1.0 if task.platform_requirement in agent.platform_specialties else 0.6
        
        return (cpu_match + memory_match + network_match + complexity_match + platform_match) / 5.0
    
    async def _calculate_geographic_match(self, 
                                        task: TaskResource, 
                                        agent: AgentCapability) -> float:
        """Calculate geographic proximity score"""        
        if not task.geographic_preference:
            return 1.0
        
        if agent.geographic_region == task.geographic_preference:
            return 1.0
        elif agent.geographic_region == "global":
            return 0.8
        else:
            return 0.4
    
    async def _store_prediction(self, 
                              task: TaskResource, 
                              predicted_agent: str, 
                              confidence: float):
        """Store prediction for future learning"""        
        prediction_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'task_id': task.task_id,
            'complexity': task.complexity.value,
            'resource_type': task.resource_type.value,
            'predicted_agent': predicted_agent,
            'confidence': confidence,
            'platform': task.platform_requirement,
            'geographic_preference': task.geographic_preference
        }
        
        self.historical_data.append(prediction_data)
        
        # Limit historical data size
        if len(self.historical_data) > 10000:
            self.historical_data = self.historical_data[-5000:]
    
    async def update_prediction_accuracy(self, 
                                       task_id: str, 
                                       actual_performance: Dict):
        """Update prediction model with actual performance"""        
        # Find prediction
        prediction = None
        for data in reversed(self.historical_data):
            if data['task_id'] == task_id:
                prediction = data
                break
        
        if prediction:
            # Calculate accuracy
            success = actual_performance.get('success', False)
            completion_time = actual_performance.get('completion_time_seconds', 0)
            
            prediction['actual_success'] = success
            prediction['actual_completion_time'] = completion_time
            
            # Update feature weights based on performance
            await self._adjust_feature_weights(prediction, actual_performance)
    
    async def _adjust_feature_weights(self, 
                                    prediction: Dict, 
                                    actual_performance: Dict):
        """Adjust feature weights based on prediction accuracy"""        
        # Simple adjustment mechanism
        if actual_performance.get('success', False):
            # Successful prediction - slightly increase confidence in features
            adjustment = 0.001
            for feature in self.feature_weights:
                self.feature_weights[feature] = min(1.0, self.feature_weights[feature] + adjustment)
        else:
            # Failed prediction - slightly decrease confidence
            adjustment = -0.001
            for feature in self.feature_weights:
                self.feature_weights[feature] = max(0.0, self.feature_weights[feature] + adjustment)
        
        # Normalize weights
        total_weight = sum(self.feature_weights.values())
        if total_weight > 0:
            for feature in self.feature_weights:
                self.feature_weights[feature] /= total_weight


class TaskDistributionEngine:
    """Advanced task distribution engine with ML capabilities"""    
    def __init__(self, 
                 default_strategy: DistributionStrategy = DistributionStrategy.ML_PREDICTED,
                 enable_prediction: bool = True):
        self.default_strategy = default_strategy
        self.enable_prediction = enable_prediction
        
        # Components
        self.ml_predictor = MLDistributionPredictor() if enable_prediction else None
        
        # Agent registry
        self.registered_agents: Dict[str, AgentCapability] = {}
        
        # Distribution history
        self.distribution_history: deque = deque(maxlen=10000)
        
        # Performance metrics
        self.metrics = LoadBalancingMetrics()
        
        # Strategy implementations
        self.strategy_handlers = {
            DistributionStrategy.ROUND_ROBIN: self._round_robin_distribution,
            DistributionStrategy.LEAST_LOADED: self._least_loaded_distribution,
            DistributionStrategy.RESOURCE_OPTIMIZED: self._resource_optimized_distribution,
            DistributionStrategy.PERFORMANCE_BASED: self._performance_based_distribution,
            DistributionStrategy.ML_PREDICTED: self._ml_predicted_distribution,
            DistributionStrategy.PLATFORM_SPECIALIZED: self._platform_specialized_distribution,
            DistributionStrategy.GEOGRAPHIC_OPTIMIZED: self._geographic_optimized_distribution
        }
        
        # Round-robin counter
        self._round_robin_index = 0
        
        # Distribution lock
        self._distribution_lock = asyncio.Lock()
        
        logger.info(f"Task Distribution Engine initialized with strategy: {default_strategy.value}")
    
    async def register_agent(self, agent_capability: AgentCapability):
        """Register agent with capabilities"""        
        async with self._distribution_lock:
            self.registered_agents[agent_capability.agent_id] = agent_capability
            
        logger.info(f"Agent registered: {agent_capability.agent_id}")
    
    async def unregister_agent(self, agent_id: str):
        """Unregister agent"""        
        async with self._distribution_lock:
            if agent_id in self.registered_agents:
                del self.registered_agents[agent_id]
                
        logger.info(f"Agent unregistered: {agent_id}")
    
    async def update_agent_status(self, 
                                agent_id: str, 
                                status_update: Dict):
        """Update agent status and metrics"""        
        if agent_id not in self.registered_agents:
            logger.warning(f"Attempt to update unknown agent: {agent_id}")
            return
        
        agent = self.registered_agents[agent_id]
        
        # Update agent properties
        if 'current_load' in status_update:
            agent.current_load = status_update['current_load']
        
        if 'success_rate' in status_update:
            agent.success_rate = status_update['success_rate']
        
        if 'average_response_time_ms' in status_update:
            agent.average_response_time_ms = status_update['average_response_time_ms']
        
        if 'health_score' in status_update:
            agent.health_score = status_update['health_score']
        
        agent.last_updated = datetime.utcnow()
        
        logger.debug(f"Agent status updated: {agent_id}")
    
    async def distribute_task(self, 
                            task: TaskResource, 
                            strategy: Optional[DistributionStrategy] = None) -> DistributionResult:
        """Distribute task to best available agent"""        
        distribution_start = time.time()
        
        strategy = strategy or self.default_strategy
        
        try:
            async with self._distribution_lock:
                # Get available agents
                available_agents = [
                    agent for agent in self.registered_agents.values()
                    if agent.health_score > 0.5 and agent.current_load < 0.9
                ]
                
                if not available_agents:
                    result = DistributionResult(
                        task_id=task.task_id,
                        assigned_agent_id=None,
                        distribution_strategy=strategy,
                        confidence_score=0.0,
                        estimated_completion_time=None,
                        resource_efficiency_score=0.0,
                        reason="No available agents"
                    )
                    await self._record_distribution(result, distribution_start, False)
                    return result
                
                # Apply distribution strategy
                handler = self.strategy_handlers.get(strategy, self._least_loaded_distribution)
                result = await handler(task, available_agents)
                
                # Update agent load if assignment successful
                if result.assigned_agent_id:
                    agent = self.registered_agents[result.assigned_agent_id]
                    await self._update_agent_load(agent, task, increment=True)
                
                await self._record_distribution(result, distribution_start, result.assigned_agent_id is not None)
                
                return result
                
        except Exception as e:
            logger.error(f"Task distribution error: {e}")
            result = DistributionResult(
                task_id=task.task_id,
                assigned_agent_id=None,
                distribution_strategy=strategy,
                confidence_score=0.0,
                estimated_completion_time=None,
                resource_efficiency_score=0.0,
                reason=f"Distribution error: {str(e)}"
            )
            await self._record_distribution(result, distribution_start, False)
            return result
    
    async def _round_robin_distribution(self, 
                                      task: TaskResource, 
                                      available_agents: List[AgentCapability]) -> DistributionResult:
        """Round-robin distribution strategy"""        
        if not available_agents:
            return DistributionResult(
                task_id=task.task_id,
                assigned_agent_id=None,
                distribution_strategy=DistributionStrategy.ROUND_ROBIN,
                confidence_score=0.0,
                estimated_completion_time=None,
                resource_efficiency_score=0.0,
                reason="No available agents"
            )
        
        # Select agent using round-robin
        selected_agent = available_agents[self._round_robin_index % len(available_agents)]
        self._round_robin_index += 1
        
        # Calculate estimated completion time
        estimated_completion = datetime.utcnow() + timedelta(seconds=task.estimated_duration_seconds)
        
        return DistributionResult(
            task_id=task.task_id,
            assigned_agent_id=selected_agent.agent_id,
            distribution_strategy=DistributionStrategy.ROUND_ROBIN,
            confidence_score=0.7,
            estimated_completion_time=estimated_completion,
            resource_efficiency_score=0.6,
            reason="Round-robin selection",
            alternative_agents=[a.agent_id for a in available_agents if a.agent_id != selected_agent.agent_id][:3]
        )
    
    async def _least_loaded_distribution(self, 
                                       task: TaskResource, 
                                       available_agents: List[AgentCapability]) -> DistributionResult:
        """Least loaded distribution strategy"""        
        # Sort agents by current load (ascending)
        sorted_agents = sorted(available_agents, key=lambda a: a.current_load)
        selected_agent = sorted_agents[0]
        
        estimated_completion = datetime.utcnow() + timedelta(
            seconds=task.estimated_duration_seconds * (1 + selected_agent.current_load)
        )
        
        return DistributionResult(
            task_id=task.task_id,
            assigned_agent_id=selected_agent.agent_id,
            distribution_strategy=DistributionStrategy.LEAST_LOADED,
            confidence_score=0.8,
            estimated_completion_time=estimated_completion,
            resource_efficiency_score=1.0 - selected_agent.current_load,
            reason=f"Least loaded agent (load: {selected_agent.current_load:.2f})",
            alternative_agents=[a.agent_id for a in sorted_agents[1:4]]
        )
    
    async def _resource_optimized_distribution(self, 
                                             task: TaskResource, 
                                             available_agents: List[AgentCapability]) -> DistributionResult:
        """Resource-optimized distribution strategy"""        
        best_agent = None
        best_score = 0.0
        agent_scores = []
        
        for agent in available_agents:
            score = await self._calculate_resource_compatibility(task, agent)
            agent_scores.append((agent, score))
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        if not best_agent:
            return DistributionResult(
                task_id=task.task_id,
                assigned_agent_id=None,
                distribution_strategy=DistributionStrategy.RESOURCE_OPTIMIZED,
                confidence_score=0.0,
                estimated_completion_time=None,
                resource_efficiency_score=0.0,
                reason="No compatible agents found"
            )
        
        estimated_completion = datetime.utcnow() + timedelta(
            seconds=task.estimated_duration_seconds / max(0.1, best_score)
        )
        
        # Sort alternatives by score
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        alternatives = [agent.agent_id for agent, _ in agent_scores[1:4]]
        
        return DistributionResult(
            task_id=task.task_id,
            assigned_agent_id=best_agent.agent_id,
            distribution_strategy=DistributionStrategy.RESOURCE_OPTIMIZED,
            confidence_score=best_score,
            estimated_completion_time=estimated_completion,
            resource_efficiency_score=best_score,
            reason=f"Best resource match (score: {best_score:.2f})",
            alternative_agents=alternatives
        )
    
    async def _performance_based_distribution(self, 
                                            task: TaskResource, 
                                            available_agents: List[AgentCapability]) -> DistributionResult:
        """Performance-based distribution strategy"""        
        # Calculate performance scores
        agent_scores = []
        for agent in available_agents:
            # Performance score based on success rate and response time
            performance_score = (
                agent.success_rate * 0.6 + 
                (1000 - min(1000, agent.average_response_time_ms)) / 1000 * 0.4
            ) * agent.health_score
            
            agent_scores.append((agent, performance_score))
        
        # Sort by performance score
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        best_agent, best_score = agent_scores[0]
        
        estimated_completion = datetime.utcnow() + timedelta(
            seconds=task.estimated_duration_seconds * (2.0 - best_score)
        )
        
        alternatives = [agent.agent_id for agent, _ in agent_scores[1:4]]
        
        return DistributionResult(
            task_id=task.task_id,
            assigned_agent_id=best_agent.agent_id,
            distribution_strategy=DistributionStrategy.PERFORMANCE_BASED,
            confidence_score=best_score,
            estimated_completion_time=estimated_completion,
            resource_efficiency_score=best_score,
            reason=f"Best performance agent (score: {best_score:.2f})",
            alternative_agents=alternatives
        )
    
    async def _ml_predicted_distribution(self, 
                                       task: TaskResource, 
                                       available_agents: List[AgentCapability]) -> DistributionResult:
        """ML-predicted distribution strategy"""        
        if not self.ml_predictor:
            # Fallback to resource-optimized
            return await self._resource_optimized_distribution(task, available_agents)
        
        best_agent_id, confidence = await self.ml_predictor.predict_best_agent(task, available_agents)
        
        if not best_agent_id:
            return DistributionResult(
                task_id=task.task_id,
                assigned_agent_id=None,
                distribution_strategy=DistributionStrategy.ML_PREDICTED,
                confidence_score=0.0,
                estimated_completion_time=None,
                resource_efficiency_score=0.0,
                reason="ML prediction failed"
            )
        
        best_agent = next(a for a in available_agents if a.agent_id == best_agent_id)
        
        estimated_completion = datetime.utcnow() + timedelta(
            seconds=task.estimated_duration_seconds * (2.0 - confidence)
        )
        
        alternatives = [a.agent_id for a in available_agents if a.agent_id != best_agent_id][:3]
        
        return DistributionResult(
            task_id=task.task_id,
            assigned_agent_id=best_agent_id,
            distribution_strategy=DistributionStrategy.ML_PREDICTED,
            confidence_score=confidence,
            estimated_completion_time=estimated_completion,
            resource_efficiency_score=confidence,
            reason=f"ML prediction (confidence: {confidence:.2f})",
            alternative_agents=alternatives
        )
    
    async def _platform_specialized_distribution(self, 
                                               task: TaskResource, 
                                               available_agents: List[AgentCapability]) -> DistributionResult:
        """Platform-specialized distribution strategy"""        
        if not task.platform_requirement:
            # Fallback to least loaded if no platform requirement
            return await self._least_loaded_distribution(task, available_agents)
        
        # Filter agents by platform specialty
        specialized_agents = [
            agent for agent in available_agents
            if task.platform_requirement in agent.platform_specialties
        ]
        
        if not specialized_agents:
            # No specialized agents, use general agents
            specialized_agents = available_agents
        
        # Among specialized agents, choose least loaded
        selected_agent = min(specialized_agents, key=lambda a: a.current_load)
        
        estimated_completion = datetime.utcnow() + timedelta(
            seconds=task.estimated_duration_seconds * (0.8 if task.platform_requirement in selected_agent.platform_specialties else 1.2)
        )
        
        alternatives = [a.agent_id for a in specialized_agents if a.agent_id != selected_agent.agent_id][:3]
        
        return DistributionResult(
            task_id=task.task_id,
            assigned_agent_id=selected_agent.agent_id,
            distribution_strategy=DistributionStrategy.PLATFORM_SPECIALIZED,
            confidence_score=0.9 if task.platform_requirement in selected_agent.platform_specialties else 0.6,
            estimated_completion_time=estimated_completion,
            resource_efficiency_score=0.8,
            reason=f"Platform specialist for {task.platform_requirement}",
            alternative_agents=alternatives
        )
    
    async def _geographic_optimized_distribution(self, 
                                               task: TaskResource, 
                                               available_agents: List[AgentCapability]) -> DistributionResult:
        """Geographic-optimized distribution strategy"""        
        if not task.geographic_preference:
            # Fallback to least loaded if no geographic preference
            return await self._least_loaded_distribution(task, available_agents)
        
        # Score agents by geographic proximity and load
        agent_scores = []
        for agent in available_agents:
            geo_score = 1.0 if agent.geographic_region == task.geographic_preference else 0.5
            load_score = 1.0 - agent.current_load
            combined_score = geo_score * 0.6 + load_score * 0.4
            
            agent_scores.append((agent, combined_score))
        
        # Sort by combined score
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        selected_agent, score = agent_scores[0]
        
        estimated_completion = datetime.utcnow() + timedelta(
            seconds=task.estimated_duration_seconds * (2.0 - score)
        )
        
        alternatives = [agent.agent_id for agent, _ in agent_scores[1:4]]
        
        return DistributionResult(
            task_id=task.task_id,
            assigned_agent_id=selected_agent.agent_id,
            distribution_strategy=DistributionStrategy.GEOGRAPHIC_OPTIMIZED,
            confidence_score=score,
            estimated_completion_time=estimated_completion,
            resource_efficiency_score=score,
            reason=f"Geographic optimization for {task.geographic_preference}",
            alternative_agents=alternatives
        )
    
    async def _calculate_resource_compatibility(self, 
                                              task: TaskResource, 
                                              agent: AgentCapability) -> float:
        """Calculate resource compatibility score"""        
        # CPU compatibility
        cpu_score = min(1.0, agent.cpu_capacity / max(1.0, task.estimated_cpu_usage))
        
        # Memory compatibility
        memory_score = min(1.0, agent.memory_capacity_mb / max(1.0, task.estimated_memory_mb))
        
        # Network compatibility
        network_score = min(1.0, agent.network_bandwidth_mbps / max(1.0, task.network_requirement_mbps))
        
        # Load penalty
        load_penalty = 1.0 - agent.current_load
        
        # Platform match bonus
        platform_bonus = 1.2 if (task.platform_requirement and 
                               task.platform_requirement in agent.platform_specialties) else 1.0
        
        # Complexity compatibility
        complexity_score = 1.0 if task.complexity in agent.supported_task_types else 0.5
        
        # Combined score
        resource_score = (cpu_score + memory_score + network_score + complexity_score) / 4.0
        final_score = resource_score * load_penalty * platform_bonus * agent.health_score
        
        return min(1.0, final_score)
    
    async def _update_agent_load(self, 
                               agent: AgentCapability, 
                               task: TaskResource, 
                               increment: bool = True):
        """Update agent load based on task assignment"""        
        load_change = task.estimated_cpu_usage / agent.cpu_capacity
        
        if increment:
            agent.current_load = min(1.0, agent.current_load + load_change)
        else:
            agent.current_load = max(0.0, agent.current_load - load_change)
        
        agent.last_updated = datetime.utcnow()
    
    async def _record_distribution(self, 
                                 result: DistributionResult, 
                                 start_time: float, 
                                 success: bool):
        """Record distribution result for metrics"""        
        distribution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Update metrics
        self.metrics.total_distributions += 1
        if success:
            self.metrics.successful_distributions += 1
        else:
            self.metrics.failed_distributions += 1
        
        # Update average distribution time
        current_avg = self.metrics.average_distribution_time_ms
        total = self.metrics.total_distributions
        self.metrics.average_distribution_time_ms = ((current_avg * (total - 1)) + distribution_time) / total
        
        # Store in history
        distribution_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'task_id': result.task_id,
            'assigned_agent': result.assigned_agent_id,
            'strategy': result.distribution_strategy.value,
            'confidence': result.confidence_score,
            'success': success,
            'distribution_time_ms': distribution_time
        }
        
        self.distribution_history.append(distribution_record)
        
        self.metrics.last_updated = datetime.utcnow()
    
    async def task_completed(self, 
                           task_id: str, 
                           agent_id: str, 
                           performance_data: Dict):
        """Handle task completion and update agent metrics"""        
        if agent_id in self.registered_agents:
            agent = self.registered_agents[agent_id]
            
            # Update agent metrics based on performance
            success = performance_data.get('success', False)
            completion_time = performance_data.get('completion_time_seconds', 0)
            
            # Update success rate (exponential moving average)
            alpha = 0.1  # Learning rate
            new_success_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * agent.success_rate
            agent.success_rate = max(0.0, min(1.0, new_success_rate))
            
            # Update response time (exponential moving average)
            if completion_time > 0:
                new_response_time = alpha * (completion_time * 1000) + (1 - alpha) * agent.average_response_time_ms
                agent.average_response_time_ms = max(0.0, new_response_time)
            
            # Calculate and decrease load (task completed)
            # This should match the task that was assigned
            estimated_load_decrease = 0.1  # Default assumption
            agent.current_load = max(0.0, agent.current_load - estimated_load_decrease)
            
            agent.last_updated = datetime.utcnow()
            
            # Update ML predictor if enabled
            if self.ml_predictor:
                await self.ml_predictor.update_prediction_accuracy(task_id, performance_data)
        
        logger.debug(f"Task completed: {task_id} by agent {agent_id}")
    
    async def get_distribution_metrics(self) -> LoadBalancingMetrics:
        """Get current distribution metrics"""        
        # Calculate current resource utilization efficiency
        if self.registered_agents:
            total_efficiency = sum(
                (1.0 - agent.current_load) * agent.health_score 
                for agent in self.registered_agents.values()
            )
            self.metrics.resource_utilization_efficiency = total_efficiency / len(self.registered_agents)
            
            # Calculate load balance score (inverse of standard deviation of loads)
            loads = [agent.current_load for agent in self.registered_agents.values()]
            if len(loads) > 1:
                load_std = np.std(loads)
                self.metrics.load_balance_score = max(0.0, 1.0 - load_std)
            else:
                self.metrics.load_balance_score = 1.0
            
            # Calculate average agent health
            self.metrics.agent_health_average = sum(
                agent.health_score for agent in self.registered_agents.values()
            ) / len(self.registered_agents)
        
        return self.metrics
    
    async def get_agent_status(self) -> Dict[str, Dict]:
        """Get status of all registered agents"""        
        agent_status = {}
        for agent_id, agent in self.registered_agents.items():
            agent_status[agent_id] = {
                'agent_id': agent_id,
                'current_load': agent.current_load,
                'health_score': agent.health_score,
                'success_rate': agent.success_rate,
                'average_response_time_ms': agent.average_response_time_ms,
                'platform_specialties': agent.platform_specialties,
                'geographic_region': agent.geographic_region,
                'max_concurrent_tasks': agent.max_concurrent_tasks,
                'last_updated': agent.last_updated.isoformat()
            }
        
        return agent_status
    
    async def optimize_distribution_strategy(self) -> Dict[str, Any]:
        """Analyze performance and suggest optimization strategies"""        
        optimization_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'current_strategy': self.default_strategy.value,
            'metrics': await self.get_distribution_metrics(),
            'recommendations': [],
            'agent_analysis': {}
        }
        
        # Analyze recent distribution performance
        recent_distributions = list(self.distribution_history)[-100:]  # Last 100 distributions
        
        if recent_distributions:
            success_rate = sum(1 for d in recent_distributions if d['success']) / len(recent_distributions)
            avg_time = sum(d['distribution_time_ms'] for d in recent_distributions) / len(recent_distributions)
            
            # Strategy-specific analysis
            strategy_performance = defaultdict(list)
            for dist in recent_distributions:
                strategy_performance[dist['strategy']].append(dist['success'])
            
            best_strategy = None
            best_performance = 0.0
            
            for strategy, results in strategy_performance.items():
                if results:
                    performance = sum(results) / len(results)
                    if performance > best_performance:
                        best_performance = performance
                        best_strategy = strategy
            
            # Generate recommendations
            if success_rate < 0.9:
                optimization_report['recommendations'].append({
                    'priority': 'high',
                    'issue': 'Low distribution success rate',
                    'current_rate': success_rate,
                    'suggestion': 'Consider using resource-optimized or ML-predicted strategy'
                })
            
            if avg_time > 100:  # 100ms threshold
                optimization_report['recommendations'].append({
                    'priority': 'medium',
                    'issue': 'High distribution latency',
                    'current_latency_ms': avg_time,
                    'suggestion': 'Optimize agent selection algorithms or increase agent pool'
                })
            
            if best_strategy and best_strategy != self.default_strategy.value:
                optimization_report['recommendations'].append({
                    'priority': 'medium',
                    'issue': 'Suboptimal distribution strategy',
                    'current_strategy': self.default_strategy.value,
                    'suggested_strategy': best_strategy,
                    'expected_improvement': f"{(best_performance - success_rate) * 100:.1f}%"
                })
        
        # Analyze agent performance
        for agent_id, agent in self.registered_agents.items():
            agent_analysis = {
                'health_status': 'healthy' if agent.health_score > 0.8 else 'degraded' if agent.health_score > 0.5 else 'critical',
                'load_status': 'underutilized' if agent.current_load < 0.3 else 'optimal' if agent.current_load < 0.8 else 'overloaded',
                'performance_status': 'excellent' if agent.success_rate > 0.95 else 'good' if agent.success_rate > 0.85 else 'poor'
            }
            
            optimization_report['agent_analysis'][agent_id] = agent_analysis
            
            # Agent-specific recommendations
            if agent.health_score < 0.5:
                optimization_report['recommendations'].append({
                    'priority': 'high',
                    'issue': f'Agent {agent_id} health critical',
                    'suggestion': 'Investigate agent health issues and consider restart'
                })
            
            if agent.current_load > 0.9:
                optimization_report['recommendations'].append({
                    'priority': 'medium',
                    'issue': f'Agent {agent_id} overloaded',
                    'suggestion': 'Redistribute tasks or scale up agent capacity'
                })
        
        return optimization_report


# Factory function
def create_task_distribution_engine(
    strategy: DistributionStrategy = DistributionStrategy.ML_PREDICTED,
    enable_prediction: bool = True
) -> TaskDistributionEngine:
    """Create and configure task distribution engine"""    
    return TaskDistributionEngine(
        default_strategy=strategy,
        enable_prediction=enable_prediction
    )


# Export classes and functions
__all__ = [
    'TaskDistributionEngine',
    'MLDistributionPredictor',
    'DistributionStrategy',
    'TaskComplexity',
    'ResourceType',
    'AgentCapability',
    'TaskResource',
    'DistributionResult',
    'LoadBalancingMetrics',
    'create_task_distribution_engine'
]
