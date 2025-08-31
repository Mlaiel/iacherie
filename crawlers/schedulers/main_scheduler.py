"""Main Scheduler Module
====================

Central coordination module for all crawler scheduling systems.
Provides unified interface and orchestration for all scheduler types.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et orchestration
- Backend Senior: Infrastructure robuste et coordination des services
- ML Engineer: Algorithmes intelligents et optimisation prédictive
- DBA Expert: Gestion optimisée des données et requêtes
- Sécurité: Protection et contrôle d'accès sécurisé
- Microservices: Architecture distribuée et communication
- Audio/Vidéo: Traitement et analyse de contenu multimédia
- DevOps: Déploiement et monitoring des systèmes
- IA Prompt Engineer: Optimisation des interactions

Business Logic Integration:
Creator content upload → Multi-scheduler coordination → AI processing → 
Protection layer → Intelligent scheduling → Platform distribution → 
Performance monitoring → Revenue optimization → User satisfaction → 
Business growth → Market leadership
"""import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Union, Callable, Type
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
from abc import ABC, abstractmethod
import uuid

# Import all scheduler types
from .priority_scheduler import PriorityScheduler, ScheduledTask
from .intelligent_scheduler import IntelligentScheduler
from .time_scheduler import TimeBasedScheduler, TimedTask
from .resource_scheduler import ResourceScheduler
from .adaptive_scheduler import AdaptiveScheduler, AdaptationStrategy

logger = logging.getLogger(__name__)


class SchedulerType(Enum):
    """Types of available schedulers."""    PRIORITY = "priority"
    INTELLIGENT = "intelligent"
    TIME_BASED = "time_based"
    RESOURCE_AWARE = "resource_aware"
    ADAPTIVE = "adaptive"
    BATCH = "batch"
    EVENT_DRIVEN = "event_driven"
    CAMPAIGN = "campaign"


class SchedulingStrategy(Enum):
    """Overall scheduling strategies."""    PERFORMANCE_OPTIMIZED = "performance_optimized"
    RESOURCE_OPTIMIZED = "resource_optimized"
    TIME_OPTIMIZED = "time_optimized"
    COST_OPTIMIZED = "cost_optimized"
    BUSINESS_OPTIMIZED = "business_optimized"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"


class TaskState(Enum):
    """Task execution states."""    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"
    PAUSED = "paused"


@dataclass
class SchedulerConfiguration:
    """Configuration for scheduler system."""    enabled_schedulers: Set[SchedulerType] = field(default_factory=lambda: {
        SchedulerType.PRIORITY,
        SchedulerType.INTELLIGENT,
        SchedulerType.TIME_BASED,
        SchedulerType.RESOURCE_AWARE,
        SchedulerType.ADAPTIVE
    })
    primary_strategy: SchedulingStrategy = SchedulingStrategy.BALANCED
    fallback_strategy: SchedulingStrategy = SchedulingStrategy.PERFORMANCE_OPTIMIZED
    coordination_interval: int = 60  # seconds
    health_check_interval: int = 30
    task_timeout: int = 3600  # 1 hour
    max_concurrent_tasks: int = 100
    enable_cross_scheduler_optimization: bool = True
    enable_predictive_scaling: bool = True
    enable_business_intelligence: bool = True
    performance_monitoring_enabled: bool = True
    auto_recovery_enabled: bool = True
    scheduler_weights: Dict[SchedulerType, float] = field(default_factory=lambda: {
        SchedulerType.PRIORITY: 0.3,
        SchedulerType.INTELLIGENT: 0.25,
        SchedulerType.TIME_BASED: 0.2,
        SchedulerType.RESOURCE_AWARE: 0.15,
        SchedulerType.ADAPTIVE: 0.1
    })


@dataclass
class TaskRequest:
    """Unified task request structure."""    task_id: str
    task_type: str
    priority: float = 0.5
    data: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    required_resources: Dict[str, float] = field(default_factory=dict)
    deadline: Optional[datetime] = None
    max_retries: int = 3
    retry_count: int = 0
    business_context: Dict[str, Any] = field(default_factory=dict)
    scheduling_constraints: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    estimated_duration: Optional[int] = None  # seconds
    callback_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchedulingDecision:
    """Scheduling decision from coordinaton process."""    task_id: str
    selected_scheduler: SchedulerType
    scheduling_time: datetime
    priority_score: float
    confidence: float
    decision_factors: Dict[str, Any]
    alternative_schedulers: List[SchedulerType] = field(default_factory=list)
    estimated_completion: Optional[datetime] = None
    resource_allocation: Dict[str, float] = field(default_factory=dict)
    business_impact_score: float = 0.5
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SchedulerMetrics:
    """Metrics for individual scheduler."""    scheduler_type: SchedulerType
    tasks_processed: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    average_completion_time: float = 0.0
    success_rate: float = 1.0
    resource_efficiency: float = 1.0
    last_activity: Optional[datetime] = None
    health_score: float = 1.0
    throughput: float = 0.0  # tasks per minute
    error_rate: float = 0.0
    business_impact: float = 0.5
    user_satisfaction: float = 0.8


@dataclass
class SystemMetrics:
    """Overall system metrics."""    total_tasks_processed: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    average_scheduling_time: float = 0.0
    system_throughput: float = 0.0
    overall_success_rate: float = 1.0
    resource_utilization: Dict[str, float] = field(default_factory=dict)
    scheduler_distribution: Dict[SchedulerType, float] = field(default_factory=dict)
    business_revenue_impact: float = 0.0
    user_satisfaction_score: float = 0.8
    cost_efficiency: float = 1.0
    competitive_advantage_score: float = 0.7
    last_updated: datetime = field(default_factory=datetime.utcnow)


class BaseSchedulerInterface(ABC):
    """Base interface for all schedulers."""    
    @abstractmethod
    async def schedule_task(self, task: TaskRequest) -> bool:
        """Schedule a task."""        pass
    
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get scheduler metrics."""        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check scheduler health."""        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop scheduler."""        pass


class MainScheduler:
    """    Main scheduler coordination system.
    
    Features:
    - Multi-scheduler coordination and orchestration
    - Intelligent task routing and load balancing
    - Performance monitoring and optimization
    - Business intelligence integration
    - Real-time adaptation and scaling
    - Comprehensive metrics and analytics
    - Cross-scheduler learning and optimization
    - Predictive capacity planning
    - Auto-recovery and fault tolerance
    - Revenue and business impact optimization
    """    
    def __init__(self, configuration: Optional[SchedulerConfiguration] = None):
        """Initialize main scheduler."""        self.config = configuration or SchedulerConfiguration()
        
        # Scheduler instances
        self.schedulers: Dict[SchedulerType, BaseSchedulerInterface] = {}
        self.scheduler_metrics: Dict[SchedulerType, SchedulerMetrics] = {}
        
        # Task management
        self.pending_tasks: Dict[str, TaskRequest] = {}
        self.active_tasks: Dict[str, TaskRequest] = {}
        self.completed_tasks: deque = deque(maxlen=10000)
        self.failed_tasks: deque = deque(maxlen=1000)
        
        # Scheduling state
        self.scheduling_decisions: deque = deque(maxlen=1000)
        self.task_assignments: Dict[str, SchedulerType] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        
        # Performance tracking
        self.system_metrics = SystemMetrics()
        self.performance_history: deque = deque(maxlen=10000)
        self.business_intelligence: Dict[str, Any] = {}
        
        # Coordination state
        self.is_running = False
        self.coordination_task: Optional[asyncio.Task] = None
        self.health_monitor_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        # Configuration
        self.routing_config = {
            'load_balancing_enabled': True,
            'intelligent_routing_enabled': True,
            'cross_scheduler_optimization': True,
            'predictive_scaling_enabled': True,
            'business_priority_weighting': 0.3,
            'performance_priority_weighting': 0.4,
            'resource_priority_weighting': 0.3,
            'adaptive_threshold': 0.1,
            'fallback_timeout': 30,
            'health_check_timeout': 10
        }
        
        logger.info("Main scheduler initialized")
    
    async def initialize(self) -> None:
        """Initialize all scheduler systems."""        try:
            # Initialize enabled schedulers
            await self._initialize_schedulers()
            
            # Start coordination processes
            await self._start_coordination()
            
            # Initialize business intelligence
            await self._initialize_business_intelligence()
            
            self.is_running = True
            logger.info("Main scheduler system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize main scheduler: {e}")
            raise
    
    async def _initialize_schedulers(self) -> None:
        """Initialize all enabled scheduler types."""        try:
            # Priority Scheduler
            if SchedulerType.PRIORITY in self.config.enabled_schedulers:
                self.schedulers[SchedulerType.PRIORITY] = PriorityScheduler()
                await self.schedulers[SchedulerType.PRIORITY].initialize()
                self.scheduler_metrics[SchedulerType.PRIORITY] = SchedulerMetrics(
                    scheduler_type=SchedulerType.PRIORITY
                )
            
            # Intelligent Scheduler
            if SchedulerType.INTELLIGENT in self.config.enabled_schedulers:
                self.schedulers[SchedulerType.INTELLIGENT] = IntelligentScheduler()
                await self.schedulers[SchedulerType.INTELLIGENT].initialize()
                self.scheduler_metrics[SchedulerType.INTELLIGENT] = SchedulerMetrics(
                    scheduler_type=SchedulerType.INTELLIGENT
                )
            
            # Time-Based Scheduler
            if SchedulerType.TIME_BASED in self.config.enabled_schedulers:
                self.schedulers[SchedulerType.TIME_BASED] = TimeBasedScheduler()
                await self.schedulers[SchedulerType.TIME_BASED].initialize()
                self.scheduler_metrics[SchedulerType.TIME_BASED] = SchedulerMetrics(
                    scheduler_type=SchedulerType.TIME_BASED
                )
            
            # Resource-Aware Scheduler
            if SchedulerType.RESOURCE_AWARE in self.config.enabled_schedulers:
                self.schedulers[SchedulerType.RESOURCE_AWARE] = ResourceScheduler()
                await self.schedulers[SchedulerType.RESOURCE_AWARE].initialize()
                self.scheduler_metrics[SchedulerType.RESOURCE_AWARE] = SchedulerMetrics(
                    scheduler_type=SchedulerType.RESOURCE_AWARE
                )
            
            # Adaptive Scheduler
            if SchedulerType.ADAPTIVE in self.config.enabled_schedulers:
                self.schedulers[SchedulerType.ADAPTIVE] = AdaptiveScheduler()
                await self.schedulers[SchedulerType.ADAPTIVE].initialize()
                self.scheduler_metrics[SchedulerType.ADAPTIVE] = SchedulerMetrics(
                    scheduler_type=SchedulerType.ADAPTIVE
                )
            
            logger.info(f"Initialized {len(self.schedulers)} schedulers")
            
        except Exception as e:
            logger.error(f"Scheduler initialization failed: {e}")
            raise
    
    async def _start_coordination(self) -> None:
        """Start coordination processes."""        self.coordination_task = asyncio.create_task(self._coordination_loop())
        self.health_monitor_task = asyncio.create_task(self._health_monitor_loop())
        self.metrics_task = asyncio.create_task(self._metrics_loop())
        
        logger.info("Coordination processes started")
    
    async def _initialize_business_intelligence(self) -> None:
        """Initialize business intelligence system."""        self.business_intelligence = {
            'revenue_targets': {},
            'user_behavior_patterns': {},
            'competitive_analysis': {},
            'market_trends': {},
            'performance_benchmarks': {},
            'cost_optimization_targets': {},
            'customer_satisfaction_metrics': {},
            'business_impact_weights': {
                'revenue': 0.4,
                'user_satisfaction': 0.3,
                'cost_efficiency': 0.2,
                'competitive_advantage': 0.1
            }
        }
    
    async def schedule_task(
        self,
        task: TaskRequest,
        preferred_scheduler: Optional[SchedulerType] = None
    ) -> SchedulingDecision:
        """        Schedule a task through the coordination system.
        
        Args:
            task: Task request to schedule
            preferred_scheduler: Optional preferred scheduler type
            
        Returns:
            Scheduling decision with selected scheduler and metadata
        """        try:
            # Validate task
            if not await self._validate_task(task):
                raise ValueError(f"Invalid task: {task.task_id}")
            
            # Store pending task
            self.pending_tasks[task.task_id] = task
            
            # Build dependency graph
            await self._update_dependency_graph(task)
            
            # Generate scheduling decision
            decision = await self._make_scheduling_decision(task, preferred_scheduler)
            
            # Execute scheduling decision
            success = await self._execute_scheduling_decision(task, decision)
            
            if success:
                # Move to active tasks
                self.active_tasks[task.task_id] = task
                self.task_assignments[task.task_id] = decision.selected_scheduler
                
                # Store decision
                self.scheduling_decisions.append(decision)
                
                # Update metrics
                await self._update_scheduling_metrics(decision)
                
                # Call callbacks
                await self._call_callbacks('task_scheduled', task, decision)
                
                logger.info(f"Task {task.task_id} scheduled to {decision.selected_scheduler.value}")
                
            else:
                # Handle scheduling failure
                await self._handle_scheduling_failure(task, decision)
            
            return decision
            
        except Exception as e:
            logger.error(f"Task scheduling failed for {task.task_id}: {e}")
            
            # Create failure decision
            failure_decision = SchedulingDecision(
                task_id=task.task_id,
                selected_scheduler=SchedulerType.PRIORITY,  # Fallback
                scheduling_time=datetime.utcnow(),
                priority_score=0.0,
                confidence=0.0,
                decision_factors={'error': str(e)}
            )
            
            return failure_decision
    
    async def _validate_task(self, task: TaskRequest) -> bool:
        """Validate task request."""        # Check required fields
        if not task.task_id or not task.task_type:
            return False
        
        # Check for duplicate task ID
        if task.task_id in self.active_tasks or task.task_id in self.pending_tasks:
            return False
        
        # Validate priority range
        if not 0 <= task.priority <= 1:
            return False
        
        # Check resource requirements
        if task.required_resources:
            for resource, amount in task.required_resources.items():
                if amount < 0:
                    return False
        
        # Check deadline
        if task.deadline and task.deadline <= datetime.utcnow():
            return False
        
        return True
    
    async def _update_dependency_graph(self, task: TaskRequest) -> None:
        """Update task dependency graph."""        if task.dependencies:
            for dep_id in task.dependencies:
                self.dependency_graph[task.task_id].add(dep_id)
    
    async def _make_scheduling_decision(
        self,
        task: TaskRequest,
        preferred_scheduler: Optional[SchedulerType] = None
    ) -> SchedulingDecision:
        """Make intelligent scheduling decision."""        try:
            # Calculate scheduler suitability scores
            scheduler_scores = await self._calculate_scheduler_suitability(task)
            
            # Apply preferences
            if preferred_scheduler and preferred_scheduler in scheduler_scores:
                scheduler_scores[preferred_scheduler] *= 1.5
            
            # Apply business intelligence
            scheduler_scores = await self._apply_business_intelligence(task, scheduler_scores)
            
            # Apply load balancing
            scheduler_scores = await self._apply_load_balancing(scheduler_scores)
            
            # Select best scheduler
            best_scheduler = max(scheduler_scores.items(), key=lambda x: x[1])
            selected_scheduler = best_scheduler[0]
            confidence = best_scheduler[1]
            
            # Calculate additional decision factors
            decision_factors = await self._calculate_decision_factors(task, scheduler_scores)
            
            # Estimate completion time
            estimated_completion = await self._estimate_completion_time(task, selected_scheduler)
            
            # Calculate business impact
            business_impact = await self._calculate_business_impact(task)
            
            # Create scheduling decision
            decision = SchedulingDecision(
                task_id=task.task_id,
                selected_scheduler=selected_scheduler,
                scheduling_time=datetime.utcnow(),
                priority_score=task.priority,
                confidence=confidence,
                decision_factors=decision_factors,
                alternative_schedulers=sorted(
                    [s for s, score in scheduler_scores.items() if s != selected_scheduler],
                    key=lambda s: scheduler_scores[s],
                    reverse=True
                )[:3],
                estimated_completion=estimated_completion,
                business_impact_score=business_impact
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Scheduling decision failed: {e}")
            raise
    
    async def _calculate_scheduler_suitability(self, task: TaskRequest) -> Dict[SchedulerType, float]:
        """Calculate suitability scores for each scheduler."""        scores = {}
        
        for scheduler_type in self.schedulers.keys():
            score = 0.0
            
            # Base suitability based on scheduler type and task characteristics
            if scheduler_type == SchedulerType.PRIORITY:
                # Good for high-priority tasks
                score += task.priority * 0.5
                score += 0.3 if task.business_context.get('urgent', False) else 0.0
            
            elif scheduler_type == SchedulerType.INTELLIGENT:
                # Good for complex tasks with learning potential
                score += 0.4 if task.task_type in ['ai_processing', 'ml_training'] else 0.2
                score += 0.3 if len(task.data) > 10 else 0.1
            
            elif scheduler_type == SchedulerType.TIME_BASED:
                # Good for time-sensitive tasks
                score += 0.5 if task.deadline else 0.1
                score += 0.3 if task.scheduling_constraints.get('time_sensitive', False) else 0.0
            
            elif scheduler_type == SchedulerType.RESOURCE_AWARE:
                # Good for resource-intensive tasks
                resource_intensity = sum(task.required_resources.values()) if task.required_resources else 0
                score += min(0.5, resource_intensity / 10)
                score += 0.3 if resource_intensity > 5 else 0.0
            
            elif scheduler_type == SchedulerType.ADAPTIVE:
                # Good for experimental or variable tasks
                score += 0.4 if task.task_type == 'experimental' else 0.2
                score += 0.3 if task.business_context.get('adaptive', False) else 0.0
            
            # Apply scheduler health and performance
            metrics = self.scheduler_metrics.get(scheduler_type)
            if metrics:
                score *= metrics.health_score
                score *= (1.0 + metrics.success_rate) / 2.0
            
            # Apply configuration weights
            weight = self.config.scheduler_weights.get(scheduler_type, 1.0)
            score *= weight
            
            scores[scheduler_type] = max(0.0, min(1.0, score))
        
        return scores
    
    async def _apply_business_intelligence(
        self,
        task: TaskRequest,
        scores: Dict[SchedulerType, float]
    ) -> Dict[SchedulerType, float]:
        """Apply business intelligence to scheduling scores."""        if not self.config.enable_business_intelligence:
            return scores
        
        # Get business context
        business_impact = task.business_context.get('business_impact', 0.5)
        revenue_potential = task.business_context.get('revenue_potential', 0.5)
        user_impact = task.business_context.get('user_impact', 0.5)
        
        # Calculate business multiplier
        business_multiplier = (
            business_impact * 0.4 +
            revenue_potential * 0.4 +
            user_impact * 0.2
        )
        
        # Apply multiplier to high-performing schedulers
        adjusted_scores = {}
        for scheduler_type, score in scores.items():
            metrics = self.scheduler_metrics.get(scheduler_type)
            if metrics and metrics.business_impact > 0.7:
                adjusted_scores[scheduler_type] = score * (1.0 + business_multiplier * 0.3)
            else:
                adjusted_scores[scheduler_type] = score
        
        return adjusted_scores
    
    async def _apply_load_balancing(self, scores: Dict[SchedulerType, float]) -> Dict[SchedulerType, float]:
        """Apply load balancing to scheduler selection."""        if not self.routing_config['load_balancing_enabled']:
            return scores
        
        # Calculate current loads
        scheduler_loads = {}
        for scheduler_type in scores.keys():
            # Count active tasks for each scheduler
            active_count = sum(
                1 for assigned_scheduler in self.task_assignments.values()
                if assigned_scheduler == scheduler_type
            )
            scheduler_loads[scheduler_type] = active_count
        
        # Apply load balancing penalty
        max_load = max(scheduler_loads.values()) if scheduler_loads.values() else 0
        if max_load > 0:
            balanced_scores = {}
            for scheduler_type, score in scores.items():
                load = scheduler_loads.get(scheduler_type, 0)
                load_factor = 1.0 - (load / (max_load + 1)) * 0.3  # Reduce by up to 30%
                balanced_scores[scheduler_type] = score * load_factor
            return balanced_scores
        
        return scores
    
    async def _calculate_decision_factors(
        self,
        task: TaskRequest,
        scheduler_scores: Dict[SchedulerType, float]
    ) -> Dict[str, Any]:
        """Calculate factors that influenced the scheduling decision."""        return {
            'task_priority': task.priority,
            'task_type': task.task_type,
            'has_deadline': task.deadline is not None,
            'resource_requirements': sum(task.required_resources.values()) if task.required_resources else 0,
            'dependency_count': len(task.dependencies),
            'business_impact': task.business_context.get('business_impact', 0.5),
            'scheduler_scores': {k.value: v for k, v in scheduler_scores.items()},
            'system_load': len(self.active_tasks),
            'strategy': self.config.primary_strategy.value
        }
    
    async def _estimate_completion_time(
        self,
        task: TaskRequest,
        scheduler_type: SchedulerType
    ) -> Optional[datetime]:
        """Estimate task completion time."""        if task.estimated_duration:
            base_duration = task.estimated_duration
        else:
            # Default estimates based on task type
            duration_estimates = {
                'content_analysis': 300,    # 5 minutes
                'ai_processing': 1800,      # 30 minutes
                'crawling': 600,            # 10 minutes
                'data_processing': 900,     # 15 minutes
                'ml_training': 3600,        # 1 hour
                'default': 1200             # 20 minutes
            }
            base_duration = duration_estimates.get(task.task_type, duration_estimates['default'])
        
        # Apply scheduler-specific factors
        scheduler_factors = {
            SchedulerType.PRIORITY: 0.9,        # Faster due to priority
            SchedulerType.INTELLIGENT: 1.1,     # Slightly slower but smarter
            SchedulerType.TIME_BASED: 1.0,      # Average
            SchedulerType.RESOURCE_AWARE: 0.95, # Efficient resource usage
            SchedulerType.ADAPTIVE: 1.2         # Learning overhead
        }
        
        factor = scheduler_factors.get(scheduler_type, 1.0)
        estimated_seconds = int(base_duration * factor)
        
        return datetime.utcnow() + timedelta(seconds=estimated_seconds)
    
    async def _calculate_business_impact(self, task: TaskRequest) -> float:
        """Calculate business impact score for the task."""        business_ctx = task.business_context
        
        # Base business impact
        base_impact = business_ctx.get('business_impact', 0.5)
        
        # Revenue impact
        revenue_impact = business_ctx.get('revenue_potential', 0.5) * 0.3
        
        # User satisfaction impact
        user_impact = business_ctx.get('user_impact', 0.5) * 0.3
        
        # Competitive advantage impact
        competitive_impact = business_ctx.get('competitive_advantage', 0.5) * 0.2
        
        # Cost efficiency impact
        cost_impact = business_ctx.get('cost_efficiency', 0.5) * 0.2
        
        total_impact = base_impact + revenue_impact + user_impact + competitive_impact + cost_impact
        
        return min(1.0, max(0.0, total_impact))
    
    async def _execute_scheduling_decision(
        self,
        task: TaskRequest,
        decision: SchedulingDecision
    ) -> bool:
        """Execute the scheduling decision."""        try:
            scheduler = self.schedulers.get(decision.selected_scheduler)
            if not scheduler:
                logger.error(f"Scheduler {decision.selected_scheduler.value} not available")
                return False
            
            # Check scheduler health
            if not await scheduler.health_check():
                logger.warning(f"Scheduler {decision.selected_scheduler.value} health check failed")
                # Try fallback scheduler
                return await self._try_fallback_scheduling(task, decision)
            
            # Schedule the task
            success = await scheduler.schedule_task(task)
            
            if success:
                # Remove from pending
                self.pending_tasks.pop(task.task_id, None)
                return True
            else:
                # Try fallback
                return await self._try_fallback_scheduling(task, decision)
                
        except Exception as e:
            logger.error(f"Scheduling execution failed: {e}")
            return await self._try_fallback_scheduling(task, decision)
    
    async def _try_fallback_scheduling(
        self,
        task: TaskRequest,
        original_decision: SchedulingDecision
    ) -> bool:
        """Try fallback scheduling options."""        # Try alternative schedulers from decision
        for alt_scheduler in original_decision.alternative_schedulers:
            scheduler = self.schedulers.get(alt_scheduler)
            if scheduler and await scheduler.health_check():
                try:
                    success = await scheduler.schedule_task(task)
                    if success:
                        # Update decision
                        original_decision.selected_scheduler = alt_scheduler
                        original_decision.decision_factors['fallback_used'] = True
                        logger.info(f"Fallback scheduling successful: {alt_scheduler.value}")
                        return True
                except Exception as e:
                    logger.warning(f"Fallback scheduler {alt_scheduler.value} failed: {e}")
                    continue
        
        # Final fallback to priority scheduler
        priority_scheduler = self.schedulers.get(SchedulerType.PRIORITY)
        if priority_scheduler and await priority_scheduler.health_check():
            try:
                success = await priority_scheduler.schedule_task(task)
                if success:
                    original_decision.selected_scheduler = SchedulerType.PRIORITY
                    original_decision.decision_factors['final_fallback'] = True
                    logger.info("Final fallback to priority scheduler successful")
                    return True
            except Exception as e:
                logger.error(f"Final fallback failed: {e}")
        
        return False
    
    async def _handle_scheduling_failure(
        self,
        task: TaskRequest,
        decision: SchedulingDecision
    ) -> None:
        """Handle scheduling failure."""        # Move task to failed
        self.failed_tasks.append({
            'task': task,
            'decision': decision,
            'failure_time': datetime.utcnow(),
            'retry_count': task.retry_count
        })
        
        # Remove from pending
        self.pending_tasks.pop(task.task_id, None)
        
        # Consider retry
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            # Schedule retry with delay
            asyncio.create_task(self._schedule_retry(task, delay=60))
        
        # Call failure callbacks
        await self._call_callbacks('task_failed', task, decision)
        
        logger.error(f"Task {task.task_id} scheduling failed permanently")
    
    async def _schedule_retry(self, task: TaskRequest, delay: int) -> None:
        """Schedule task retry after delay."""        await asyncio.sleep(delay)
        try:
            await self.schedule_task(task)
        except Exception as e:
            logger.error(f"Task retry failed for {task.task_id}: {e}")
    
    async def _coordination_loop(self) -> None:
        """Main coordination loop."""        while self.is_running:
            try:
                # Optimize cross-scheduler performance
                if self.config.enable_cross_scheduler_optimization:
                    await self._optimize_cross_scheduler_performance()
                
                # Check for dependency resolutions
                await self._check_dependency_resolutions()
                
                # Rebalance if needed
                await self._rebalance_if_needed()
                
                # Update business intelligence
                await self._update_business_intelligence()
                
                await asyncio.sleep(self.config.coordination_interval)
                
            except Exception as e:
                logger.error(f"Coordination loop error: {e}")
                await asyncio.sleep(10)
    
    async def _health_monitor_loop(self) -> None:
        """Health monitoring loop."""        while self.is_running:
            try:
                # Check scheduler health
                for scheduler_type, scheduler in self.schedulers.items():
                    try:
                        health = await asyncio.wait_for(
                            scheduler.health_check(),
                            timeout=self.routing_config['health_check_timeout']
                        )
                        
                        metrics = self.scheduler_metrics.get(scheduler_type)
                        if metrics:
                            metrics.health_score = 1.0 if health else 0.0
                            metrics.last_activity = datetime.utcnow()
                            
                    except asyncio.TimeoutError:
                        logger.warning(f"Health check timeout for {scheduler_type.value}")
                        metrics = self.scheduler_metrics.get(scheduler_type)
                        if metrics:
                            metrics.health_score = 0.5
                    except Exception as e:
                        logger.error(f"Health check failed for {scheduler_type.value}: {e}")
                        metrics = self.scheduler_metrics.get(scheduler_type)
                        if metrics:
                            metrics.health_score = 0.0
                
                await asyncio.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(10)
    
    async def _metrics_loop(self) -> None:
        """Metrics collection loop."""        while self.is_running:
            try:
                # Collect metrics from all schedulers
                for scheduler_type, scheduler in self.schedulers.items():
                    try:
                        scheduler_metrics = await scheduler.get_metrics()
                        await self._update_scheduler_metrics(scheduler_type, scheduler_metrics)
                    except Exception as e:
                        logger.error(f"Metrics collection failed for {scheduler_type.value}: {e}")
                
                # Update system metrics
                await self._update_system_metrics()
                
                # Store performance snapshot
                self.performance_history.append({
                    'timestamp': datetime.utcnow(),
                    'system_metrics': asdict(self.system_metrics),
                    'scheduler_metrics': {
                        k.value: asdict(v) for k, v in self.scheduler_metrics.items()
                    }
                })
                
                await asyncio.sleep(60)  # Every minute
                
            except Exception as e:
                logger.error(f"Metrics loop error: {e}")
                await asyncio.sleep(10)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""        return {
            'is_running': self.is_running,
            'configuration': asdict(self.config),
            'enabled_schedulers': [s.value for s in self.config.enabled_schedulers],
            'active_schedulers': [s.value for s in self.schedulers.keys()],
            'system_metrics': asdict(self.system_metrics),
            'scheduler_metrics': {
                k.value: asdict(v) for k, v in self.scheduler_metrics.items()
            },
            'task_counts': {
                'pending': len(self.pending_tasks),
                'active': len(self.active_tasks),
                'completed': len(self.completed_tasks),
                'failed': len(self.failed_tasks)
            },
            'recent_decisions': [
                {
                    'task_id': d.task_id,
                    'scheduler': d.selected_scheduler.value,
                    'confidence': d.confidence,
                    'business_impact': d.business_impact_score
                }
                for d in list(self.scheduling_decisions)[-10:]
            ],
            'business_intelligence': self.business_intelligence,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def stop(self) -> None:
        """Stop the main scheduler system."""        logger.info("Stopping main scheduler system...")
        
        self.is_running = False
        
        # Cancel coordination tasks
        for task in [self.coordination_task, self.health_monitor_task, self.metrics_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Stop all schedulers
        for scheduler_type, scheduler in self.schedulers.items():
            try:
                await scheduler.stop()
                logger.info(f"Stopped {scheduler_type.value} scheduler")
            except Exception as e:
                logger.error(f"Error stopping {scheduler_type.value}: {e}")
        
        logger.info("Main scheduler system stopped")
    
    def add_callback(self, event_type: str, callback: Callable) -> None:
        """Add event callback."""        self.event_callbacks[event_type].append(callback)
    
    async def _call_callbacks(self, event_type: str, *args) -> None:
        """Call registered callbacks for an event."""        for callback in self.event_callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args)
                else:
                    callback(*args)
            except Exception as e:
                logger.error(f"Callback error for {event_type}: {e}")


# Export main classes
__all__ = [
    'MainScheduler',
    'SchedulerType',
    'SchedulingStrategy',
    'TaskState',
    'SchedulerConfiguration',
    'TaskRequest',
    'SchedulingDecision',
    'SchedulerMetrics',
    'SystemMetrics',
    'BaseSchedulerInterface'
]
