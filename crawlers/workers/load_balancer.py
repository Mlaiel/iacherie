"""Load Balancer - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/load_balancer.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Load Balancer - Intelligent Traffic Distribution
Responsibility: Optimal worker selection and load distribution
Technologies: ML-based Load Balancing, Real-time Analytics, Performance Optimization
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Task analysis → Worker evaluation → Performance prediction → 
Optimal selection → Load distribution → Real-time monitoring → Adaptive optimization
"""
from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple
import logging
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import time
import statistics
import math
from collections import defaultdict, deque

from .crawler_worker import CrawlerTask, WorkerType
from .worker_scheduler import LoadBalancingStrategy
from ...ai.ml.prediction_engine import PredictionEngine
from ...monitoring.performance_monitor import PerformanceMonitor
from ...utils.math_utils import MathUtils

logger = logging.getLogger(__name__)


class LoadMetric(Enum):
    """Load balancing metrics"""    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    NETWORK_USAGE = "network_usage"
    TASK_COUNT = "task_count"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    EFFICIENCY = "efficiency"


@dataclass
class WorkerLoad:
    """Worker load information"""    worker_id: str
    cpu_load: float = 0.0
    memory_load: float = 0.0
    network_load: float = 0.0
    active_tasks: int = 0
    max_tasks: int = 5
    average_response_time: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    efficiency_score: float = 1.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    specializations: List[str] = field(default_factory=list)
    health_status: str = "healthy"


@dataclass
class SelectionCriteria:
    """Worker selection criteria"""    preferred_worker_types: List[WorkerType] = field(default_factory=list)
    min_efficiency: float = 0.5
    max_load_threshold: float = 0.8
    required_specializations: List[str] = field(default_factory=list)
    avoid_workers: List[str] = field(default_factory=list)
    geographic_preference: Optional[str] = None
    sticky_session: Optional[str] = None


@dataclass
class LoadBalancingResult:
    """Load balancing decision result"""    selected_worker: Optional[str]
    confidence_score: float
    selection_reason: str
    alternative_workers: List[str] = field(default_factory=list)
    estimated_wait_time: float = 0.0
    load_distribution: Dict[str, float] = field(default_factory=dict)


class WorkerLoadBalancer:
    """    Intelligent load balancer for optimal worker selection
    
    Features:
    - Multiple balancing algorithms
    - ML-based performance prediction
    - Real-time load monitoring
    - Adaptive weight adjustment
    - Sticky sessions support
    - Geographic optimization
    """
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.INTELLIGENT):
        self.strategy = strategy
        
        # Worker tracking
        self.worker_loads: Dict[str, WorkerLoad] = {}
        self.worker_performance_history: Dict[str, Dict[str, deque]] = defaultdict(lambda: defaultdict(deque))
        self.worker_affinities: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Load balancing state
        self.round_robin_index = 0
        self.weighted_round_robin_weights: Dict[str, float] = {}
        self.sticky_sessions: Dict[str, str] = {}
        
        # Components
        self.prediction_engine = PredictionEngine()
        self.performance_monitor = PerformanceMonitor()
        self.math_utils = MathUtils()
        
        # Balancing weights
        self.metric_weights = {
            LoadMetric.CPU_USAGE: 0.25,
            LoadMetric.MEMORY_USAGE: 0.20,
            LoadMetric.TASK_COUNT: 0.20,
            LoadMetric.RESPONSE_TIME: 0.15,
            LoadMetric.ERROR_RATE: 0.10,
            LoadMetric.EFFICIENCY: 0.10
        }
        
        # Adaptive parameters
        self.adaptation_enabled = True
        self.adaptation_window = 100  # Number of decisions to consider
        self.decision_history: deque = deque(maxlen=1000)
        
        # Performance tracking
        self.balancing_stats = {
            'total_selections': 0,
            'successful_selections': 0,
            'failed_selections': 0,
            'average_confidence': 0.0,
            'strategy_performance': defaultdict(lambda: {'count': 0, 'success': 0})
        }

    async def initialize(self) -> None:
        """Initialize the load balancer"""        try:
            logger.info("🚀 Initializing load balancer")
            
            # Initialize prediction engine
            await self.prediction_engine.initialize()
            
            logger.info("✅ Load balancer initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize load balancer: {e}")
            raise

    async def select_worker(
        self,
        task: CrawlerTask,
        available_workers: List[str],
        worker_health: Dict[str, Dict[str, Any]],
        criteria: Optional[SelectionCriteria] = None
    ) -> Optional[str]:
        """Select optimal worker for task"""        try:
            if not available_workers:
                return None
            
            # Filter healthy workers
            healthy_workers = await self._filter_healthy_workers(available_workers, worker_health)
            if not healthy_workers:
                return None
            
            # Apply selection criteria
            if criteria:
                healthy_workers = await self._apply_selection_criteria(healthy_workers, criteria)
                if not healthy_workers:
                    return None
            
            # Select based on strategy
            result = await self._select_by_strategy(task, healthy_workers, criteria)
            
            # Record decision
            await self._record_selection_decision(task, result)
            
            # Update statistics
            self.balancing_stats['total_selections'] += 1
            if result.selected_worker:
                self.balancing_stats['successful_selections'] += 1
            else:
                self.balancing_stats['failed_selections'] += 1
            
            logger.info(f"🎯 Worker selected: {result.selected_worker} (confidence: {result.confidence_score:.2f}, reason: {result.selection_reason})")
            
            return result.selected_worker
            
        except Exception as e:
            logger.error(f"❌ Failed to select worker: {e}")
            return None

    async def update_worker_load(self, worker_id: str, load_data: Dict[str, Any]) -> None:
        """Update worker load information"""        try:
            # Create or update worker load
            if worker_id not in self.worker_loads:
                self.worker_loads[worker_id] = WorkerLoad(worker_id=worker_id)
            
            load = self.worker_loads[worker_id]
            
            # Update load metrics
            load.cpu_load = load_data.get('cpu_usage_percent', 0) / 100.0
            load.memory_load = load_data.get('memory_usage_percent', 0) / 100.0
            load.network_load = load_data.get('network_usage_percent', 0) / 100.0
            load.active_tasks = load_data.get('active_tasks', 0)
            load.max_tasks = load_data.get('max_tasks', 5)
            load.average_response_time = load_data.get('avg_response_time', 0)
            load.error_rate = load_data.get('error_rate', 0) / 100.0
            load.throughput = load_data.get('throughput_per_hour', 0)
            load.efficiency_score = load_data.get('efficiency_score', 1.0)
            load.specializations = load_data.get('specializations', [])
            load.health_status = load_data.get('health_status', 'healthy')
            load.last_updated = datetime.utcnow()
            
            # Update performance history
            history = self.worker_performance_history[worker_id]
            history['cpu_load'].append(load.cpu_load)
            history['memory_load'].append(load.memory_load)
            history['response_time'].append(load.average_response_time)
            history['error_rate'].append(load.error_rate)
            history['throughput'].append(load.throughput)
            history['efficiency'].append(load.efficiency_score)
            
            # Keep limited history
            for metric_history in history.values():
                if len(metric_history) > 100:
                    metric_history.popleft()
            
            # Update weighted round robin weights
            await self._update_worker_weights(worker_id)
            
        except Exception as e:
            logger.error(f"❌ Failed to update worker load for {worker_id}: {e}")

    async def get_load_distribution(self) -> Dict[str, Any]:
        """Get current load distribution across workers"""        try:
            if not self.worker_loads:
                return {}
            
            distribution = {
                'workers': {},
                'global_metrics': {},
                'balancing_stats': self.balancing_stats.copy()
            }
            
            total_workers = len(self.worker_loads)
            total_cpu = sum(load.cpu_load for load in self.worker_loads.values())
            total_memory = sum(load.memory_load for load in self.worker_loads.values())
            total_tasks = sum(load.active_tasks for load in self.worker_loads.values())
            
            # Worker-specific metrics
            for worker_id, load in self.worker_loads.items():
                distribution['workers'][worker_id] = {
                    'load_score': await self._calculate_load_score(worker_id),
                    'cpu_load': load.cpu_load,
                    'memory_load': load.memory_load,
                    'task_load': load.active_tasks / load.max_tasks,
                    'efficiency': load.efficiency_score,
                    'health': load.health_status,
                    'last_updated': load.last_updated.isoformat()
                }
            
            # Global metrics
            distribution['global_metrics'] = {
                'average_cpu_load': total_cpu / total_workers,
                'average_memory_load': total_memory / total_workers,
                'total_active_tasks': total_tasks,
                'load_variance': await self._calculate_load_variance(),
                'strategy': self.strategy.value,
                'balanced': await self._is_load_balanced()
            }
            
            return distribution
            
        except Exception as e:
            logger.error(f"❌ Failed to get load distribution: {e}")
            return {}

    async def _filter_healthy_workers(
        self, 
        workers: List[str], 
        worker_health: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Filter out unhealthy workers"""        try:
            healthy_workers = []
            
            for worker_id in workers:
                # Check health status
                health_info = worker_health.get(worker_id, {})
                if health_info.get('status') == 'healthy':
                    # Check load information availability
                    if worker_id in self.worker_loads:
                        load = self.worker_loads[worker_id]
                        if load.health_status == 'healthy':
                            healthy_workers.append(worker_id)
                    else:
                        # Worker without load data, assume healthy
                        healthy_workers.append(worker_id)
            
            return healthy_workers
            
        except Exception as e:
            logger.error(f"❌ Failed to filter healthy workers: {e}")
            return workers

    async def _apply_selection_criteria(
        self, 
        workers: List[str], 
        criteria: SelectionCriteria
    ) -> List[str]:
        """Apply selection criteria to filter workers"""        try:
            filtered_workers = []
            
            for worker_id in workers:
                load = self.worker_loads.get(worker_id)
                
                # Skip if no load data
                if not load:
                    continue
                
                # Check avoid list
                if worker_id in criteria.avoid_workers:
                    continue
                
                # Check efficiency threshold
                if load.efficiency_score < criteria.min_efficiency:
                    continue
                
                # Check load threshold
                load_score = await self._calculate_load_score(worker_id)
                if load_score > criteria.max_load_threshold:
                    continue
                
                # Check specializations
                if criteria.required_specializations:
                    if not any(spec in load.specializations for spec in criteria.required_specializations):
                        continue
                
                filtered_workers.append(worker_id)
            
            return filtered_workers
            
        except Exception as e:
            logger.error(f"❌ Failed to apply selection criteria: {e}")
            return workers

    async def _select_by_strategy(
        self,
        task: CrawlerTask,
        workers: List[str],
        criteria: Optional[SelectionCriteria]
    ) -> LoadBalancingResult:
        """Select worker based on strategy"""        try:
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return await self._round_robin_selection(workers)
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return await self._least_connections_selection(workers)
            elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                return await self._weighted_round_robin_selection(workers)
            elif self.strategy == LoadBalancingStrategy.RESPONSE_TIME:
                return await self._response_time_selection(workers)
            elif self.strategy == LoadBalancingStrategy.RESOURCE_BASED:
                return await self._resource_based_selection(workers, task)
            elif self.strategy == LoadBalancingStrategy.INTELLIGENT:
                return await self._intelligent_selection(workers, task, criteria)
            else:
                # Default to round robin
                return await self._round_robin_selection(workers)
                
        except Exception as e:
            logger.error(f"❌ Failed to select by strategy: {e}")
            return LoadBalancingResult(
                selected_worker=None,
                confidence_score=0.0,
                selection_reason=f"Selection failed: {e}"
            )

    async def _round_robin_selection(self, workers: List[str]) -> LoadBalancingResult:
        """Round robin worker selection"""        try:
            if not workers:
                return LoadBalancingResult(
                    selected_worker=None,
                    confidence_score=0.0,
                    selection_reason="No available workers"
                )
            
            selected_worker = workers[self.round_robin_index % len(workers)]
            self.round_robin_index += 1
            
            return LoadBalancingResult(
                selected_worker=selected_worker,
                confidence_score=0.8,
                selection_reason="Round robin selection",
                alternative_workers=workers[:3]
            )
            
        except Exception as e:
            logger.error(f"❌ Round robin selection failed: {e}")
            return LoadBalancingResult(
                selected_worker=None,
                confidence_score=0.0,
                selection_reason=f"Round robin failed: {e}"
            )

    async def _least_connections_selection(self, workers: List[str]) -> LoadBalancingResult:
        """Least connections worker selection"""        try:
            if not workers:
                return LoadBalancingResult(
                    selected_worker=None,
                    confidence_score=0.0,
                    selection_reason="No available workers"
                )
            
            # Find worker with least active tasks
            best_worker = None
            min_tasks = float('inf')
            
            for worker_id in workers:
                load = self.worker_loads.get(worker_id)
                if load:
                    if load.active_tasks < min_tasks:
                        min_tasks = load.active_tasks
                        best_worker = worker_id
                else:
                    # Worker without load data, assume 0 tasks
                    best_worker = worker_id
                    break
            
            confidence = 0.9 if best_worker else 0.0
            
            return LoadBalancingResult(
                selected_worker=best_worker,
                confidence_score=confidence,
                selection_reason=f"Least connections ({min_tasks} tasks)",
                alternative_workers=[w for w in workers if w != best_worker][:3]
            )
            
        except Exception as e:
            logger.error(f"❌ Least connections selection failed: {e}")
            return LoadBalancingResult(
                selected_worker=None,
                confidence_score=0.0,
                selection_reason=f"Least connections failed: {e}"
            )

    async def _weighted_round_robin_selection(self, workers: List[str]) -> LoadBalancingResult:
        """Weighted round robin worker selection"""        try:
            if not workers:
                return LoadBalancingResult(
                    selected_worker=None,
                    confidence_score=0.0,
                    selection_reason="No available workers"
                )
            
            # Calculate selection probabilities based on weights
            worker_weights = []
            total_weight = 0.0
            
            for worker_id in workers:
                weight = self.weighted_round_robin_weights.get(worker_id, 1.0)
                worker_weights.append(weight)
                total_weight += weight
            
            if total_weight == 0:
                # Fallback to round robin
                return await self._round_robin_selection(workers)
            
            # Normalize weights and select
            import random
            rand_value = random.random() * total_weight
            cumulative_weight = 0.0
            
            for i, worker_id in enumerate(workers):
                cumulative_weight += worker_weights[i]
                if rand_value <= cumulative_weight:
                    return LoadBalancingResult(
                        selected_worker=worker_id,
                        confidence_score=0.85,
                        selection_reason=f"Weighted round robin (weight: {worker_weights[i]:.2f})",
                        alternative_workers=[w for w in workers if w != worker_id][:3]
                    )
            
            # Fallback to last worker
            return LoadBalancingResult(
                selected_worker=workers[-1],
                confidence_score=0.7,
                selection_reason="Weighted round robin fallback"
            )
            
        except Exception as e:
            logger.error(f"❌ Weighted round robin selection failed: {e}")
            return LoadBalancingResult(
                selected_worker=None,
                confidence_score=0.0,
                selection_reason=f"Weighted round robin failed: {e}"
            )

    async def _response_time_selection(self, workers: List[str]) -> LoadBalancingResult:
        """Response time based worker selection"""        try:
            if not workers:
                return LoadBalancingResult(
                    selected_worker=None,
                    confidence_score=0.0,
                    selection_reason="No available workers"
                )
            
            # Find worker with best response time
            best_worker = None
            best_response_time = float('inf')
            
            for worker_id in workers:
                load = self.worker_loads.get(worker_id)
                if load:
                    if load.average_response_time < best_response_time:
                        best_response_time = load.average_response_time
                        best_worker = worker_id
                else:
                    # Worker without load data, assume good response time
                    best_worker = worker_id
                    best_response_time = 0.0
                    break
            
            confidence = 0.8 if best_worker else 0.0
            
            return LoadBalancingResult(
                selected_worker=best_worker,
                confidence_score=confidence,
                selection_reason=f"Best response time ({best_response_time:.2f}s)",
                alternative_workers=[w for w in workers if w != best_worker][:3]
            )
            
        except Exception as e:
            logger.error(f"❌ Response time selection failed: {e}")
            return LoadBalancingResult(
                selected_worker=None,
                confidence_score=0.0,
                selection_reason=f"Response time selection failed: {e}"
            )

    async def _resource_based_selection(self, workers: List[str], task: CrawlerTask) -> LoadBalancingResult:
        """Resource-based worker selection"""        try:
            if not workers:
                return LoadBalancingResult(
                    selected_worker=None,
                    confidence_score=0.0,
                    selection_reason="No available workers"
                )
            
            # Calculate resource scores for each worker
            worker_scores = []
            
            for worker_id in workers:
                load = self.worker_loads.get(worker_id)
                if load:
                    # Calculate composite resource score
                    cpu_score = 1.0 - load.cpu_load
                    memory_score = 1.0 - load.memory_load
                    task_score = 1.0 - (load.active_tasks / load.max_tasks)
                    
                    # Weighted composite score
                    composite_score = (
                        cpu_score * 0.4 +
                        memory_score * 0.3 +
                        task_score * 0.3
                    )
                    
                    worker_scores.append((worker_id, composite_score))
                else:
                    # Worker without load data, assume good resources
                    worker_scores.append((worker_id, 1.0))
            
            # Sort by score and select best
            worker_scores.sort(key=lambda x: x[1], reverse=True)
            best_worker, best_score = worker_scores[0]
            
            return LoadBalancingResult(
                selected_worker=best_worker,
                confidence_score=min(0.95, best_score),
                selection_reason=f"Best resource availability (score: {best_score:.2f})",
                alternative_workers=[w[0] for w in worker_scores[1:4]]
            )
            
        except Exception as e:
            logger.error(f"❌ Resource-based selection failed: {e}")
            return LoadBalancingResult(
                selected_worker=None,
                confidence_score=0.0,
                selection_reason=f"Resource-based selection failed: {e}"
            )

    async def _intelligent_selection(
        self, 
        workers: List[str], 
        task: CrawlerTask,
        criteria: Optional[SelectionCriteria]
    ) -> LoadBalancingResult:
        """Intelligent ML-based worker selection"""        try:
            if not workers:
                return LoadBalancingResult(
                    selected_worker=None,
                    confidence_score=0.0,
                    selection_reason="No available workers"
                )
            
            # Calculate intelligent scores for each worker
            worker_scores = []
            
            for worker_id in workers:
                score = await self._calculate_intelligent_score(worker_id, task, criteria)
                worker_scores.append((worker_id, score))
            
            # Sort by score and select best
            worker_scores.sort(key=lambda x: x[1], reverse=True)
            
            if worker_scores:
                best_worker, best_score = worker_scores[0]
                
                # Predict performance
                estimated_wait_time = await self._predict_wait_time(best_worker, task)
                
                return LoadBalancingResult(
                    selected_worker=best_worker,
                    confidence_score=min(0.98, best_score),
                    selection_reason=f"Intelligent ML-based selection (score: {best_score:.3f})",
                    alternative_workers=[w[0] for w in worker_scores[1:4]],
                    estimated_wait_time=estimated_wait_time,
                    load_distribution={w[0]: w[1] for w in worker_scores}
                )
            
            return LoadBalancingResult(
                selected_worker=None,
                confidence_score=0.0,
                selection_reason="No suitable workers found"
            )
            
        except Exception as e:
            logger.error(f"❌ Intelligent selection failed: {e}")
            return LoadBalancingResult(
                selected_worker=None,
                confidence_score=0.0,
                selection_reason=f"Intelligent selection failed: {e}"
            )

    async def _calculate_intelligent_score(
        self, 
        worker_id: str, 
        task: CrawlerTask,
        criteria: Optional[SelectionCriteria]
    ) -> float:
        """Calculate intelligent score for worker"""        try:
            load = self.worker_loads.get(worker_id)
            if not load:
                return 0.5  # Default score for workers without load data
            
            # Base metrics
            cpu_score = 1.0 - load.cpu_load
            memory_score = 1.0 - load.memory_load
            task_score = 1.0 - (load.active_tasks / load.max_tasks)
            response_score = max(0.0, 1.0 - (load.average_response_time / 300.0))  # Normalize to 5 minutes
            error_score = 1.0 - load.error_rate
            efficiency_score = load.efficiency_score
            
            # Calculate weighted base score
            base_score = (
                cpu_score * self.metric_weights[LoadMetric.CPU_USAGE] +
                memory_score * self.metric_weights[LoadMetric.MEMORY_USAGE] +
                task_score * self.metric_weights[LoadMetric.TASK_COUNT] +
                response_score * self.metric_weights[LoadMetric.RESPONSE_TIME] +
                error_score * self.metric_weights[LoadMetric.ERROR_RATE] +
                efficiency_score * self.metric_weights[LoadMetric.EFFICIENCY]
            )
            
            # Specialization bonus
            specialization_bonus = 0.0
            if load.specializations:
                if task.platform in load.specializations or 'all' in load.specializations:
                    specialization_bonus = 0.2
            
            # Historical performance bonus
            performance_bonus = await self._calculate_performance_bonus(worker_id)
            
            # Affinity bonus
            affinity_bonus = await self._calculate_affinity_bonus(worker_id, task)
            
            # Combine scores
            final_score = base_score + specialization_bonus + performance_bonus + affinity_bonus
            
            # Apply criteria adjustments
            if criteria:
                if criteria.sticky_session and criteria.sticky_session == worker_id:
                    final_score += 0.3  # Sticky session bonus
            
            return min(1.0, max(0.0, final_score))
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate intelligent score for {worker_id}: {e}")
            return 0.0

    async def _calculate_performance_bonus(self, worker_id: str) -> float:
        """Calculate performance bonus based on historical data"""        try:
            history = self.worker_performance_history.get(worker_id)
            if not history or not history['efficiency']:
                return 0.0
            
            recent_efficiency = list(history['efficiency'])[-10:]  # Last 10 data points
            if len(recent_efficiency) < 5:
                return 0.0
            
            avg_efficiency = statistics.mean(recent_efficiency)
            efficiency_trend = recent_efficiency[-1] - recent_efficiency[0] if len(recent_efficiency) > 1 else 0
            
            # Bonus for high efficiency and positive trend
            bonus = (avg_efficiency - 0.8) * 0.5 + efficiency_trend * 0.3
            
            return max(0.0, min(0.2, bonus))
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate performance bonus: {e}")
            return 0.0

    async def _calculate_affinity_bonus(self, worker_id: str, task: CrawlerTask) -> float:
        """Calculate worker-task affinity bonus"""        try:
            if worker_id not in self.worker_affinities:
                return 0.0
            
            affinities = self.worker_affinities[worker_id]
            
            # Platform affinity
            platform_affinity = affinities.get(f"platform_{task.platform}", 0.0)
            
            # Content type affinity
            content_affinity = 0.0
            for content_type in task.content_types:
                content_affinity += affinities.get(f"content_{content_type}", 0.0)
            content_affinity /= max(1, len(task.content_types))
            
            # User affinity
            user_affinity = affinities.get(f"user_{task.user_id}", 0.0)
            
            # Combined affinity bonus
            total_affinity = (platform_affinity + content_affinity + user_affinity) / 3
            
            return max(0.0, min(0.15, total_affinity))
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate affinity bonus: {e}")
            return 0.0

    async def _predict_wait_time(self, worker_id: str, task: CrawlerTask) -> float:
        """Predict wait time for task on worker"""        try:
            load = self.worker_loads.get(worker_id)
            if not load:
                return 60.0  # Default 1 minute
            
            # Estimate based on current load and average response time
            queue_time = load.active_tasks * load.average_response_time
            processing_time = load.average_response_time or 300.0  # Default 5 minutes
            
            return queue_time + processing_time
            
        except Exception as e:
            logger.error(f"❌ Failed to predict wait time: {e}")
            return 300.0

    async def _calculate_load_score(self, worker_id: str) -> float:
        """Calculate overall load score for worker"""        try:
            load = self.worker_loads.get(worker_id)
            if not load:
                return 0.0
            
            cpu_load = load.cpu_load
            memory_load = load.memory_load
            task_load = load.active_tasks / load.max_tasks
            
            # Weighted average
            return (cpu_load * 0.4 + memory_load * 0.3 + task_load * 0.3)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate load score: {e}")
            return 1.0

    async def _calculate_load_variance(self) -> float:
        """Calculate load variance across all workers"""        try:
            if len(self.worker_loads) < 2:
                return 0.0
            
            load_scores = [await self._calculate_load_score(worker_id) for worker_id in self.worker_loads]
            return statistics.variance(load_scores)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate load variance: {e}")
            return 0.0

    async def _is_load_balanced(self) -> bool:
        """Check if load is well balanced"""        try:
            variance = await self._calculate_load_variance()
            return variance < 0.1  # Low variance indicates good balance
            
        except Exception as e:
            logger.error(f"❌ Failed to check load balance: {e}")
            return False

    async def _update_worker_weights(self, worker_id: str) -> None:
        """Update weighted round robin weights based on performance"""        try:
            load = self.worker_loads.get(worker_id)
            if not load:
                return
            
            # Calculate weight based on efficiency and current load
            efficiency_factor = load.efficiency_score
            load_factor = 1.0 - await self._calculate_load_score(worker_id)
            
            # Combined weight
            weight = (efficiency_factor + load_factor) / 2
            self.weighted_round_robin_weights[worker_id] = weight
            
        except Exception as e:
            logger.error(f"❌ Failed to update worker weights: {e}")

    async def _record_selection_decision(self, task: CrawlerTask, result: LoadBalancingResult) -> None:
        """Record selection decision for analysis"""        try:
            decision = {
                'timestamp': datetime.utcnow().isoformat(),
                'task_id': task.task_id,
                'task_platform': task.platform,
                'selected_worker': result.selected_worker,
                'confidence': result.confidence_score,
                'reason': result.selection_reason,
                'strategy': self.strategy.value
            }
            
            self.decision_history.append(decision)
            
            # Update strategy performance
            strategy_stats = self.balancing_stats['strategy_performance'][self.strategy.value]
            strategy_stats['count'] += 1
            if result.selected_worker:
                strategy_stats['success'] += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to record selection decision: {e}")
