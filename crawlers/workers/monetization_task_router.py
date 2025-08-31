"""Monetization Task Router - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/monetization_task_router.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial Monetization Task Router - Intelligent Revenue Optimization
Responsibility: Advanced task routing for revenue optimization and platform analytics
Technologies: ML-based Routing, Revenue Prediction, Platform Analytics, Performance Optimization
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Revenue task → Platform analysis → ML routing decision → 
Optimal worker selection → Performance tracking → Revenue optimization
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
import numpy as np
from collections import defaultdict, deque

from .revenue_analytics_worker import RevenueAnalyticsWorker, Platform, RevenueType, AnalyticsType
from .ml_task_router import MLTaskRouter, TaskCategory, RoutingStrategy, WorkerCapability
from ...ai.ml.revenue_predictor import RevenuePredictor
from ...ai.ml.performance_optimizer import PerformanceOptimizer
from ...monitoring.revenue_monitor import RevenueMonitor
from ...utils.financial_utils import FinancialUtils

logger = logging.getLogger(__name__)


class MonetizationTaskType(Enum):
    """Monetization task types"""    REVENUE_TRACKING = "revenue_tracking"
    ANALYTICS_GENERATION = "analytics_generation"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    PAYMENT_PROCESSING = "payment_processing"
    PLATFORM_SYNC = "platform_sync"
    REVENUE_PREDICTION = "revenue_prediction"
    TAX_CALCULATION = "tax_calculation"
    ROYALTY_DISTRIBUTION = "royalty_distribution"


class PlatformPriority(Enum):
    """Platform priority levels"""    CRITICAL = "critical"  # Spotify, YouTube
    HIGH = "high"         # Instagram, TikTok
    MEDIUM = "medium"     # SoundCloud, Bandcamp
    LOW = "low"           # Other platforms


class RevenueUrgency(Enum):
    """Revenue task urgency"""    IMMEDIATE = "immediate"    # Payment processing
    URGENT = "urgent"         # End of month analytics
    NORMAL = "normal"         # Regular tracking
    BATCH = "batch"           # Background optimization


@dataclass
class MonetizationTask:
    """Monetization task definition"""    task_id: str
    task_type: MonetizationTaskType
    user_id: str
    platform: Platform
    revenue_type: RevenueType
    priority: PlatformPriority
    urgency: RevenueUrgency
    amount_involved: float = 0.0
    currency: str = "EUR"
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    estimated_processing_time: float = 0.0
    complexity_score: float = 1.0


@dataclass
class MonetizationWorkerProfile:
    """Monetization worker profile and capabilities"""    worker_id: str
    supported_platforms: List[Platform]
    supported_task_types: List[MonetizationTaskType]
    specializations: List[str]
    performance_metrics: Dict[str, float]
    current_load: float = 0.0
    max_concurrent_tasks: int = 5
    revenue_processed_total: float = 0.0
    accuracy_score: float = 0.95
    average_processing_time: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoutingDecision:
    """Monetization routing decision result"""    selected_worker: Optional[str]
    confidence_score: float
    reasoning: str
    estimated_completion_time: datetime
    revenue_impact_score: float
    alternative_workers: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)


class MonetizationTaskRouter:
    """    Advanced monetization task router for revenue optimization
    
    Features:
    - ML-powered revenue task routing
    - Platform-specific optimization
    - Real-time performance tracking
    - Revenue impact prediction
    - Intelligent load balancing
    - Multi-currency support
    - Tax and compliance optimization
    """
    def __init__(self, router_id: str = None):
        self.router_id = router_id or f"monetization_router_{uuid.uuid4().hex[:8]}"
        
        # Core components
        self.revenue_analytics_worker = None
        self.ml_task_router = MLTaskRouter()
        self.revenue_predictor = RevenuePredictor()
        self.performance_optimizer = PerformanceOptimizer()
        self.revenue_monitor = RevenueMonitor()
        self.financial_utils = FinancialUtils()
        
        # Worker management
        self.worker_profiles: Dict[str, MonetizationWorkerProfile] = {}
        self.task_history: Dict[str, List[MonetizationTask]] = defaultdict(list)
        self.performance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Routing configuration
        self.config = {
            'revenue_weight': 0.35,      # Weight for revenue impact
            'performance_weight': 0.25,  # Weight for worker performance
            'urgency_weight': 0.20,      # Weight for task urgency
            'platform_weight': 0.15,     # Weight for platform expertise
            'load_weight': 0.05,         # Weight for current load
            'min_confidence_threshold': 0.7,
            'max_routing_time': 5.0,     # Max time for routing decision
        }
        
        # Platform-specific configuration
        self.platform_config = {
            Platform.SPOTIFY: {
                'priority_multiplier': 1.5,
                'revenue_importance': 0.9,
                'api_rate_limit': 100,
                'preferred_workers': []
            },
            Platform.YOUTUBE: {
                'priority_multiplier': 1.4,
                'revenue_importance': 0.85,
                'api_rate_limit': 200,
                'preferred_workers': []
            },
            Platform.INSTAGRAM: {
                'priority_multiplier': 1.2,
                'revenue_importance': 0.7,
                'api_rate_limit': 150,
                'preferred_workers': []
            },
            Platform.TIKTOK: {
                'priority_multiplier': 1.1,
                'revenue_importance': 0.65,
                'api_rate_limit': 100,
                'preferred_workers': []
            }
        }
        
        # Performance tracking
        self.routing_stats = {
            'total_tasks_routed': 0,
            'successful_routes': 0,
            'failed_routes': 0,
            'average_routing_time': 0.0,
            'revenue_optimized': 0.0,
            'platform_performance': defaultdict(dict)
        }
        
        self.initialized = False

    async def initialize(self) -> bool:
        """Initialize the monetization task router"""        try:
            logger.info(f"🚀 Initializing Monetization Task Router {self.router_id}")
            
            # Initialize revenue analytics worker
            self.revenue_analytics_worker = RevenueAnalyticsWorker()
            await self.revenue_analytics_worker.initialize()
            
            # Initialize ML components
            await self.ml_task_router.initialize()
            await self.revenue_predictor.initialize()
            await self.performance_optimizer.initialize()
            await self.revenue_monitor.initialize()
            await self.financial_utils.initialize()
            
            # Load worker profiles
            await self._load_worker_profiles()
            
            # Start monitoring loops
            asyncio.create_task(self._performance_monitor_loop())
            asyncio.create_task(self._optimization_loop())
            
            self.initialized = True
            logger.info(f"✅ Monetization Task Router {self.router_id} initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize monetization task router: {e}")
            return False

    async def route_task(self, task: MonetizationTask) -> RoutingDecision:
        """Route monetization task to optimal worker"""        try:
            logger.info(f"🎯 Routing monetization task: {task.task_id} ({task.task_type.value})")
            routing_start = time.time()
            
            # Validate task
            if not await self._validate_task(task):
                return RoutingDecision(
                    selected_worker=None,
                    confidence_score=0.0,
                    reasoning="Task validation failed",
                    estimated_completion_time=datetime.utcnow(),
                    revenue_impact_score=0.0
                )
            
            # Get eligible workers
            eligible_workers = await self._get_eligible_workers(task)
            if not eligible_workers:
                return RoutingDecision(
                    selected_worker=None,
                    confidence_score=0.0,
                    reasoning="No eligible workers available",
                    estimated_completion_time=datetime.utcnow(),
                    revenue_impact_score=0.0
                )
            
            # Calculate worker scores
            worker_scores = await self._calculate_worker_scores(task, eligible_workers)
            
            # Select best worker
            best_worker, confidence = await self._select_best_worker(worker_scores, task)
            
            # Calculate revenue impact
            revenue_impact = await self._calculate_revenue_impact(task, best_worker)
            
            # Estimate completion time
            completion_time = await self._estimate_completion_time(task, best_worker)
            
            # Generate optimization suggestions
            optimization_suggestions = await self._generate_optimization_suggestions(task, worker_scores)
            
            # Create routing decision
            decision = RoutingDecision(
                selected_worker=best_worker,
                confidence_score=confidence,
                reasoning=f"Selected based on revenue optimization score: {worker_scores.get(best_worker, 0):.3f}",
                estimated_completion_time=completion_time,
                revenue_impact_score=revenue_impact,
                alternative_workers=list(worker_scores.keys())[:3],
                optimization_suggestions=optimization_suggestions
            )
            
            # Record routing decision
            await self._record_routing_decision(task, decision)
            
            # Update statistics
            routing_time = time.time() - routing_start
            self.routing_stats['total_tasks_routed'] += 1
            if best_worker:
                self.routing_stats['successful_routes'] += 1
            else:
                self.routing_stats['failed_routes'] += 1
            
            self.routing_stats['average_routing_time'] = (
                (self.routing_stats['average_routing_time'] * (self.routing_stats['total_tasks_routed'] - 1) + routing_time) /
                self.routing_stats['total_tasks_routed']
            )
            
            logger.info(f"✅ Task routed: {task.task_id} → {best_worker} (confidence: {confidence:.3f}, revenue impact: {revenue_impact:.3f})")
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ Failed to route monetization task {task.task_id}: {e}")
            return RoutingDecision(
                selected_worker=None,
                confidence_score=0.0,
                reasoning=f"Routing failed: {e}",
                estimated_completion_time=datetime.utcnow(),
                revenue_impact_score=0.0
            )

    async def register_worker(self, profile: MonetizationWorkerProfile) -> bool:
        """Register a new monetization worker"""        try:
            logger.info(f"📝 Registering monetization worker: {profile.worker_id}")
            
            # Validate profile
            if not await self._validate_worker_profile(profile):
                logger.error(f"❌ Invalid worker profile: {profile.worker_id}")
                return False
            
            # Store profile
            self.worker_profiles[profile.worker_id] = profile
            
            # Initialize performance tracking
            self.performance_history[profile.worker_id] = deque(maxlen=1000)
            
            logger.info(f"✅ Monetization worker registered: {profile.worker_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to register worker: {e}")
            return False

    async def update_worker_performance(
        self, 
        worker_id: str, 
        task_id: str, 
        performance_data: Dict[str, Any]
    ) -> None:
        """Update worker performance metrics"""        try:
            if worker_id not in self.worker_profiles:
                logger.warning(f"⚠️ Worker not found: {worker_id}")
                return
            
            profile = self.worker_profiles[worker_id]
            
            # Update performance metrics
            processing_time = performance_data.get('processing_time', 0.0)
            success = performance_data.get('success', True)
            revenue_amount = performance_data.get('revenue_amount', 0.0)
            accuracy = performance_data.get('accuracy', 1.0)
            
            # Update profile metrics
            profile.revenue_processed_total += revenue_amount
            
            # Update average processing time
            if processing_time > 0:
                if profile.average_processing_time == 0:
                    profile.average_processing_time = processing_time
                else:
                    profile.average_processing_time = (
                        profile.average_processing_time * 0.9 + processing_time * 0.1
                    )
            
            # Update accuracy score
            profile.accuracy_score = profile.accuracy_score * 0.95 + accuracy * 0.05
            
            # Record performance history
            performance_record = {
                'timestamp': datetime.utcnow().isoformat(),
                'task_id': task_id,
                'processing_time': processing_time,
                'success': success,
                'revenue_amount': revenue_amount,
                'accuracy': accuracy
            }
            
            self.performance_history[worker_id].append(performance_record)
            
            profile.last_updated = datetime.utcnow()
            
            logger.debug(f"📊 Worker performance updated: {worker_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update worker performance: {e}")

    async def get_routing_analytics(
        self, 
        time_range: timedelta = timedelta(days=7)
    ) -> Dict[str, Any]:
        """Get comprehensive routing analytics"""        try:
            end_time = datetime.utcnow()
            start_time = end_time - time_range
            
            analytics = {
                'overview': {
                    'total_tasks_routed': self.routing_stats['total_tasks_routed'],
                    'success_rate': (
                        self.routing_stats['successful_routes'] / 
                        max(1, self.routing_stats['total_tasks_routed'])
                    ),
                    'average_routing_time': self.routing_stats['average_routing_time'],
                    'total_revenue_optimized': self.routing_stats['revenue_optimized']
                },
                'platform_performance': {},
                'worker_performance': {},
                'task_distribution': {},
                'revenue_insights': {}
            }
            
            # Platform performance analysis
            for platform in Platform:
                platform_stats = self.routing_stats['platform_performance'].get(platform.value, {})
                analytics['platform_performance'][platform.value] = {
                    'tasks_processed': platform_stats.get('tasks', 0),
                    'average_revenue': platform_stats.get('avg_revenue', 0.0),
                    'success_rate': platform_stats.get('success_rate', 0.0),
                    'priority_score': self.platform_config.get(platform, {}).get('priority_multiplier', 1.0)
                }
            
            # Worker performance analysis
            for worker_id, profile in self.worker_profiles.items():
                recent_performance = [
                    record for record in self.performance_history[worker_id]
                    if datetime.fromisoformat(record['timestamp']) >= start_time
                ]
                
                analytics['worker_performance'][worker_id] = {
                    'tasks_completed': len(recent_performance),
                    'success_rate': sum(1 for r in recent_performance if r['success']) / max(1, len(recent_performance)),
                    'average_processing_time': profile.average_processing_time,
                    'accuracy_score': profile.accuracy_score,
                    'revenue_processed': profile.revenue_processed_total,
                    'specializations': profile.specializations
                }
            
            # Task distribution analysis
            task_types = defaultdict(int)
            urgency_distribution = defaultdict(int)
            
            for worker_tasks in self.task_history.values():
                for task in worker_tasks:
                    if task.created_at >= start_time:
                        task_types[task.task_type.value] += 1
                        urgency_distribution[task.urgency.value] += 1
            
            analytics['task_distribution'] = {
                'by_type': dict(task_types),
                'by_urgency': dict(urgency_distribution)
            }
            
            # Revenue insights
            analytics['revenue_insights'] = await self._generate_revenue_insights(start_time, end_time)
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Failed to get routing analytics: {e}")
            return {}

    async def _get_eligible_workers(self, task: MonetizationTask) -> List[str]:
        """Get workers eligible for the task"""        try:
            eligible_workers = []
            
            for worker_id, profile in self.worker_profiles.items():
                # Check platform support
                if task.platform not in profile.supported_platforms:
                    continue
                
                # Check task type support
                if task.task_type not in profile.supported_task_types:
                    continue
                
                # Check current load
                if profile.current_load >= profile.max_concurrent_tasks:
                    continue
                
                # Check deadline feasibility
                if task.deadline:
                    estimated_time = profile.average_processing_time * task.complexity_score
                    if datetime.utcnow() + timedelta(seconds=estimated_time) > task.deadline:
                        continue
                
                eligible_workers.append(worker_id)
            
            return eligible_workers
            
        except Exception as e:
            logger.error(f"❌ Failed to get eligible workers: {e}")
            return []

    async def _calculate_worker_scores(
        self, 
        task: MonetizationTask, 
        eligible_workers: List[str]
    ) -> Dict[str, float]:
        """Calculate optimization scores for eligible workers"""        try:
            worker_scores = {}
            
            for worker_id in eligible_workers:
                profile = self.worker_profiles[worker_id]
                
                # Performance score (0-1)
                performance_score = min(1.0, profile.accuracy_score * (1.0 - profile.current_load / profile.max_concurrent_tasks))
                
                # Platform expertise score (0-1)
                platform_config = self.platform_config.get(task.platform, {})
                platform_score = platform_config.get('priority_multiplier', 1.0) / 1.5  # Normalize
                
                # Revenue impact score (0-1)
                revenue_score = await self._calculate_revenue_potential(task, profile)
                
                # Urgency alignment score (0-1)
                urgency_score = await self._calculate_urgency_alignment(task, profile)
                
                # Load balancing score (0-1)
                load_score = 1.0 - (profile.current_load / profile.max_concurrent_tasks)
                
                # Weighted composite score
                composite_score = (
                    performance_score * self.config['performance_weight'] +
                    platform_score * self.config['platform_weight'] +
                    revenue_score * self.config['revenue_weight'] +
                    urgency_score * self.config['urgency_weight'] +
                    load_score * self.config['load_weight']
                )
                
                worker_scores[worker_id] = composite_score
            
            return worker_scores
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate worker scores: {e}")
            return {}

    async def _select_best_worker(
        self, 
        worker_scores: Dict[str, float], 
        task: MonetizationTask
    ) -> Tuple[Optional[str], float]:
        """Select the best worker based on scores"""        try:
            if not worker_scores:
                return None, 0.0
            
            # Sort workers by score
            sorted_workers = sorted(worker_scores.items(), key=lambda x: x[1], reverse=True)
            
            best_worker, best_score = sorted_workers[0]
            
            # Check minimum confidence threshold
            if best_score < self.config['min_confidence_threshold']:
                logger.warning(f"⚠️ Best worker score ({best_score:.3f}) below threshold ({self.config['min_confidence_threshold']})")
                return None, best_score
            
            return best_worker, best_score
            
        except Exception as e:
            logger.error(f"❌ Failed to select best worker: {e}")
            return None, 0.0

    async def _calculate_revenue_potential(
        self, 
        task: MonetizationTask, 
        profile: MonetizationWorkerProfile
    ) -> float:
        """Calculate revenue optimization potential"""        try:
            # Base revenue potential based on task amount
            if task.amount_involved > 0:
                revenue_potential = min(1.0, task.amount_involved / 10000.0)  # Normalize to 10K
            else:
                revenue_potential = 0.5  # Default for non-monetary tasks
            
            # Worker specialization bonus
            specialization_bonus = 0.0
            for specialization in profile.specializations:
                if specialization.lower() in task.task_type.value.lower():
                    specialization_bonus += 0.2
                if specialization.lower() in task.platform.value.lower():
                    specialization_bonus += 0.1
            
            # Historical performance bonus
            performance_bonus = min(0.3, profile.accuracy_score - 0.8)  # Bonus for >80% accuracy
            
            total_potential = min(1.0, revenue_potential + specialization_bonus + performance_bonus)
            
            return total_potential
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate revenue potential: {e}")
            return 0.5

    async def _calculate_urgency_alignment(
        self, 
        task: MonetizationTask, 
        profile: MonetizationWorkerProfile
    ) -> float:
        """Calculate urgency alignment score"""        try:
            # Base urgency score
            urgency_scores = {
                RevenueUrgency.IMMEDIATE: 1.0,
                RevenueUrgency.URGENT: 0.8,
                RevenueUrgency.NORMAL: 0.6,
                RevenueUrgency.BATCH: 0.4
            }
            
            base_score = urgency_scores.get(task.urgency, 0.5)
            
            # Adjust based on worker availability
            availability_factor = 1.0 - (profile.current_load / profile.max_concurrent_tasks)
            
            # Adjust based on processing speed
            speed_factor = min(1.0, 300.0 / max(1.0, profile.average_processing_time))  # 5 minutes baseline
            
            alignment_score = base_score * availability_factor * speed_factor
            
            return min(1.0, alignment_score)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate urgency alignment: {e}")
            return 0.5

    async def _calculate_revenue_impact(self, task: MonetizationTask, worker_id: str) -> float:
        """Calculate potential revenue impact of routing decision"""        try:
            if not worker_id or worker_id not in self.worker_profiles:
                return 0.0
            
            profile = self.worker_profiles[worker_id]
            
            # Base impact from task amount
            base_impact = task.amount_involved * 0.01  # 1% of amount as base impact
            
            # Worker efficiency multiplier
            efficiency_multiplier = profile.accuracy_score
            
            # Platform importance multiplier
            platform_config = self.platform_config.get(task.platform, {})
            platform_multiplier = platform_config.get('revenue_importance', 0.5)
            
            total_impact = base_impact * efficiency_multiplier * platform_multiplier
            
            return min(10.0, total_impact)  # Cap at 10.0
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate revenue impact: {e}")
            return 0.0

    async def _estimate_completion_time(self, task: MonetizationTask, worker_id: str) -> datetime:
        """Estimate task completion time"""        try:
            if not worker_id or worker_id not in self.worker_profiles:
                return datetime.utcnow() + timedelta(hours=1)  # Default 1 hour
            
            profile = self.worker_profiles[worker_id]
            
            # Base processing time
            base_time = profile.average_processing_time or 300.0  # 5 minutes default
            
            # Complexity adjustment
            complexity_factor = task.complexity_score
            
            # Load adjustment
            load_factor = 1.0 + (profile.current_load / profile.max_concurrent_tasks)
            
            # Urgency adjustment
            urgency_factors = {
                RevenueUrgency.IMMEDIATE: 0.8,  # Faster processing
                RevenueUrgency.URGENT: 0.9,
                RevenueUrgency.NORMAL: 1.0,
                RevenueUrgency.BATCH: 1.2       # Slower processing
            }
            
            urgency_factor = urgency_factors.get(task.urgency, 1.0)
            
            estimated_seconds = base_time * complexity_factor * load_factor * urgency_factor
            
            return datetime.utcnow() + timedelta(seconds=estimated_seconds)
            
        except Exception as e:
            logger.error(f"❌ Failed to estimate completion time: {e}")
            return datetime.utcnow() + timedelta(hours=1)

    async def _generate_optimization_suggestions(
        self, 
        task: MonetizationTask, 
        worker_scores: Dict[str, float]
    ) -> List[str]:
        """Generate optimization suggestions for task routing"""        try:
            suggestions = []
            
            # Analyze worker score distribution
            if worker_scores:
                scores = list(worker_scores.values())
                avg_score = statistics.mean(scores)
                max_score = max(scores)
                
                if max_score < 0.8:
                    suggestions.append("Consider worker training or adding specialized workers for this task type")
                
                if len(scores) < 3:
                    suggestions.append("Limited worker pool - consider scaling up for better redundancy")
                
                score_variance = statistics.variance(scores) if len(scores) > 1 else 0
                if score_variance > 0.1:
                    suggestions.append("High variance in worker capabilities - consider load balancing optimization")
            
            # Platform-specific suggestions
            platform_config = self.platform_config.get(task.platform, {})
            if platform_config.get('revenue_importance', 0) > 0.8:
                suggestions.append(f"High-value platform ({task.platform.value}) - ensure priority handling")
            
            # Urgency-based suggestions
            if task.urgency == RevenueUrgency.IMMEDIATE and task.deadline:
                time_to_deadline = (task.deadline - datetime.utcnow()).total_seconds()
                if time_to_deadline < 3600:  # Less than 1 hour
                    suggestions.append("Critical deadline - consider manual intervention if needed")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"❌ Failed to generate optimization suggestions: {e}")
            return []

    async def _generate_revenue_insights(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate revenue insights for analytics"""        try:
            insights = {
                'top_performing_platforms': {},
                'revenue_trends': {},
                'optimization_opportunities': [],
                'performance_bottlenecks': []
            }
            
            # Analyze platform performance
            platform_revenues = defaultdict(float)
            platform_tasks = defaultdict(int)
            
            for worker_tasks in self.task_history.values():
                for task in worker_tasks:
                    if start_time <= task.created_at <= end_time:
                        platform_revenues[task.platform.value] += task.amount_involved
                        platform_tasks[task.platform.value] += 1
            
            # Top performing platforms
            for platform, revenue in sorted(platform_revenues.items(), key=lambda x: x[1], reverse=True):
                insights['top_performing_platforms'][platform] = {
                    'total_revenue': revenue,
                    'task_count': platform_tasks[platform],
                    'average_per_task': revenue / max(1, platform_tasks[platform])
                }
            
            # Revenue trends (simplified)
            insights['revenue_trends'] = {
                'total_period_revenue': sum(platform_revenues.values()),
                'average_daily_revenue': sum(platform_revenues.values()) / max(1, (end_time - start_time).days),
                'growth_indicators': 'stable'  # Would be calculated from historical data
            }
            
            # Optimization opportunities
            if platform_revenues:
                max_revenue_platform = max(platform_revenues.items(), key=lambda x: x[1])
                insights['optimization_opportunities'].append(
                    f"Focus on {max_revenue_platform[0]} - highest revenue generator"
                )
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Failed to generate revenue insights: {e}")
            return {}

    async def _validate_task(self, task: MonetizationTask) -> bool:
        """Validate monetization task"""        try:
            # Check required fields
            if not all([task.task_id, task.user_id, task.task_type, task.platform]):
                return False
            
            # Check valid enums
            if task.task_type not in MonetizationTaskType:
                return False
            
            if task.platform not in Platform:
                return False
            
            # Check deadline validity
            if task.deadline and task.deadline <= datetime.utcnow():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to validate task: {e}")
            return False

    async def _validate_worker_profile(self, profile: MonetizationWorkerProfile) -> bool:
        """Validate worker profile"""        try:
            # Check required fields
            if not all([profile.worker_id, profile.supported_platforms, profile.supported_task_types]):
                return False
            
            # Check valid platforms and task types
            for platform in profile.supported_platforms:
                if platform not in Platform:
                    return False
            
            for task_type in profile.supported_task_types:
                if task_type not in MonetizationTaskType:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to validate worker profile: {e}")
            return False

    async def _record_routing_decision(self, task: MonetizationTask, decision: RoutingDecision) -> None:
        """Record routing decision for analysis"""        try:
            # Add to task history
            if decision.selected_worker:
                self.task_history[decision.selected_worker].append(task)
            
            # Update routing statistics
            self.routing_stats['revenue_optimized'] += decision.revenue_impact_score
            
            # Update platform statistics
            platform_stats = self.routing_stats['platform_performance'].setdefault(task.platform.value, {})
            platform_stats['tasks'] = platform_stats.get('tasks', 0) + 1
            platform_stats['total_revenue'] = platform_stats.get('total_revenue', 0.0) + task.amount_involved
            platform_stats['avg_revenue'] = platform_stats['total_revenue'] / platform_stats['tasks']
            
        except Exception as e:
            logger.error(f"❌ Failed to record routing decision: {e}")

    async def _load_worker_profiles(self) -> None:
        """Load worker profiles from storage"""        try:
            # This would load from database in production
            # For now, we'll start with empty profiles
            self.worker_profiles = {}
            logger.info("💼 Worker profiles loaded")
            
        except Exception as e:
            logger.error(f"❌ Failed to load worker profiles: {e}")

    async def _performance_monitor_loop(self) -> None:
        """Performance monitoring loop"""        try:
            while True:
                try:
                    # Monitor worker performance and adjust routing parameters
                    await self._analyze_worker_performance()
                    await asyncio.sleep(300)  # Every 5 minutes
                    
                except Exception as e:
                    logger.error(f"❌ Error in performance monitor loop: {e}")
                    await asyncio.sleep(60)
                    
        except asyncio.CancelledError:
            logger.info("🛑 Performance monitor loop cancelled")

    async def _optimization_loop(self) -> None:
        """Optimization loop for continuous improvement"""        try:
            while True:
                try:
                    # Perform routing optimization
                    await self._optimize_routing_parameters()
                    await asyncio.sleep(3600)  # Every hour
                    
                except Exception as e:
                    logger.error(f"❌ Error in optimization loop: {e}")
                    await asyncio.sleep(300)
                    
        except asyncio.CancelledError:
            logger.info("🛑 Optimization loop cancelled")

    async def _analyze_worker_performance(self) -> None:
        """Analyze worker performance and update profiles"""        try:
            for worker_id, profile in self.worker_profiles.items():
                # Analyze recent performance
                recent_records = list(self.performance_history[worker_id])[-50:]  # Last 50 records
                
                if recent_records:
                    # Calculate performance metrics
                    success_rate = sum(1 for r in recent_records if r['success']) / len(recent_records)
                    avg_processing_time = statistics.mean([r['processing_time'] for r in recent_records if r['processing_time'] > 0])
                    
                    # Update profile if significant change
                    if abs(success_rate - profile.accuracy_score) > 0.05:
                        profile.accuracy_score = profile.accuracy_score * 0.8 + success_rate * 0.2
                    
                    if avg_processing_time > 0 and abs(avg_processing_time - profile.average_processing_time) > 30:
                        profile.average_processing_time = profile.average_processing_time * 0.9 + avg_processing_time * 0.1
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze worker performance: {e}")

    async def _optimize_routing_parameters(self) -> None:
        """Optimize routing parameters based on performance"""        try:
            # Analyze routing success rates and adjust weights
            recent_decisions = []  # Would be loaded from decision history
            
            # This would implement ML-based parameter optimization
            # For now, we'll do basic adjustments
            
            success_rate = self.routing_stats['successful_routes'] / max(1, self.routing_stats['total_tasks_routed'])
            
            if success_rate < 0.9:
                # Increase performance weight if success rate is low
                self.config['performance_weight'] = min(0.5, self.config['performance_weight'] * 1.1)
                self.config['revenue_weight'] = max(0.2, self.config['revenue_weight'] * 0.95)
            
            logger.debug("🎛️ Routing parameters optimized")
            
        except Exception as e:
            logger.error(f"❌ Failed to optimize routing parameters: {e}")

    async def get_router_stats(self) -> Dict[str, Any]:
        """Get comprehensive router statistics"""        try:
            return {
                'router_id': self.router_id,
                'status': 'active' if self.initialized else 'inactive',
                'registered_workers': len(self.worker_profiles),
                'routing_stats': self.routing_stats.copy(),
                'config': self.config.copy(),
                'platform_config': {
                    k.value if hasattr(k, 'value') else k: v 
                    for k, v in self.platform_config.items()
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get router stats: {e}")
            return {}

    async def shutdown(self) -> bool:
        """Gracefully shutdown the router"""        try:
            logger.info(f"🛑 Shutting down Monetization Task Router {self.router_id}")
            
            # Save state if necessary
            # Clean up resources
            
            self.initialized = False
            logger.info(f"✅ Monetization Task Router {self.router_id} shutdown complete")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to shutdown router: {e}")
            return False


# Factory functions and global instances
_monetization_task_router: Optional[MonetizationTaskRouter] = None


async def get_monetization_task_router() -> Optional[MonetizationTaskRouter]:
    """Get global monetization task router instance"""    global _monetization_task_router
    return _monetization_task_router


async def initialize_monetization_task_router(router_id: str = None) -> bool:
    """Initialize global monetization task router"""    global _monetization_task_router
    try:
        if _monetization_task_router is None:
            _monetization_task_router = MonetizationTaskRouter(router_id)
            return await _monetization_task_router.initialize()
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize monetization task router: {e}")
        return False


async def shutdown_monetization_task_router() -> bool:
    """Shutdown global monetization task router"""    global _monetization_task_router
    try:
        if _monetization_task_router:
            result = await _monetization_task_router.shutdown()
            _monetization_task_router = None
            return result
        return True
    except Exception as e:
        logger.error(f"❌ Failed to shutdown monetization task router: {e}")
        return False
