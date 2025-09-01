"""ML Task Router - IA-Influencer-Agent
================================================================================
Module: backend/crawlers/workers/ml_task_router.py
Author: Fahed Mlaiel (mlaiel@live.de)
Type: Industrial ML Task Router - Intelligent Task Distribution Engine
Responsibility: ML-powered task routing, optimization, and load balancing
Technologies: Deep Learning, Reinforcement Learning, Real-time Analytics, Predictive Routing
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

LOGIQUE MÉTIER:
Task analysis → ML classification → Performance prediction → 
Optimal worker selection → Real-time routing → Performance feedback → Model adaptation
"""
from typing import Any, Dict, List, Optional, Union, Callable, Set, Tuple, AsyncGenerator
import logging
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import defaultdict, deque
import heapq
import threading
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib

from .crawler_worker import CrawlerTask, TaskPriority, TaskStatus
from .worker_pool import WorkerPool, WorkerMetrics
from ...ai.ml.feature_extractor import FeatureExtractor
from ...ai.ml.performance_predictor import PerformancePredictor
from ...ai.ml.routing_optimizer import RoutingOptimizer
from ...monitoring.performance_monitor import PerformanceMonitor
from ...utils.math_utils import MathUtils
from ...core.managers.queue_manager import QueueManager

logger = logging.getLogger(__name__)


class TaskCategory(Enum):
    """Task categories for ML classification"""
    CONTENT_CRAWLING = "content_crawling"
    DATA_EXTRACTION = "data_extraction"
    MEDIA_PROCESSING = "media_processing"
    FINGERPRINTING = "fingerprinting"
    ANALYTICS = "analytics"
    PROTECTION = "protection"
    MONITORING = "monitoring"
    NOTIFICATION = "notification"


class RoutingStrategy(Enum):
    """Routing strategies"""
    LOAD_BALANCED = "load_balanced"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    COST_OPTIMIZED = "cost_optimized"
    DEADLINE_AWARE = "deadline_aware"
    ML_PREDICTED = "ml_predicted"
    REINFORCEMENT_LEARNED = "reinforcement_learned"


class WorkerCapability(Enum):
    """Worker capability types"""
    CPU_INTENSIVE = "cpu_intensive"
    MEMORY_INTENSIVE = "memory_intensive"
    IO_INTENSIVE = "io_intensive"
    GPU_ACCELERATED = "gpu_accelerated"
    NETWORK_HEAVY = "network_heavy"
    SPECIALIZED_AI = "specialized_ai"


@dataclass
class TaskFeatures:
    """Task feature vector for ML analysis"""
    task_id: str
    category: TaskCategory
    complexity_score: float
    estimated_duration: float
    resource_requirements: Dict[str, float]
    priority_score: float
    data_size: int
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    platform_specific: bool = False
    requires_gpu: bool = False
    feature_vector: Optional[np.ndarray] = None


@dataclass
class WorkerProfile:
    """Worker capability and performance profile"""
    worker_id: str
    capabilities: Set[WorkerCapability]
    performance_metrics: Dict[str, float]
    current_load: float
    success_rate: float
    average_completion_time: float
    specializations: List[TaskCategory]
    resource_limits: Dict[str, float]
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoutingDecision:
    """ML routing decision with explanation"""
    task_id: str
    selected_worker_id: str
    confidence_score: float
    predicted_completion_time: float
    predicted_success_probability: float
    routing_strategy: RoutingStrategy
    reasoning: Dict[str, Any]
    alternatives: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class TaskClassifierNN(nn.Module):
    """Neural network for task classification"""
    
    def __init__(self, input_size: int, hidden_size: int = 128, num_classes: int = 8):
        super(TaskClassifierNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, num_classes)
        self.dropout = nn.Dropout(0.2)
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        return self.softmax(x)


class PerformancePredictorNN(nn.Module):
    """Neural network for performance prediction"""
    
    def __init__(self, input_size: int, hidden_size: int = 64):
        super(PerformancePredictorNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, 2)  # completion_time, success_probability
        self.dropout = nn.Dropout(0.1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        outputs = self.fc3(x)
        # completion_time (positive), success_probability (0-1)
        return torch.cat([
            torch.abs(outputs[:, 0:1]),  # Ensure positive completion time
            self.sigmoid(outputs[:, 1:2])  # Success probability 0-1
        ], dim=1)


class MLTaskRouter:
    """Advanced ML-powered task router with intelligent optimization"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.router_id = str(uuid.uuid4())
        self.is_running = False
        
        # ML Models
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.task_classifier = None
        self.performance_predictor = None
        self.rf_classifier = None
        self.gb_regressor = None
        
        # Feature processing
        self.feature_extractor = FeatureExtractor(self.config.get("feature_config", {}))
        self.feature_scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Worker management
        self.worker_profiles: Dict[str, WorkerProfile] = {}
        self.worker_pool = None
        
        # Performance tracking
        self.routing_history = deque(maxlen=10000)
        self.performance_feedback = {}
        self.model_metrics = {
            "task_classification_accuracy": 0.0,
            "performance_prediction_mse": 0.0,
            "routing_success_rate": 0.0,
            "average_prediction_error": 0.0
        }
        
        # Real-time routing queue
        self.routing_queue = asyncio.Queue()
        self.routing_results: Dict[str, RoutingDecision] = {}
        
        # Training data collection
        self.training_data = {
            "features": [],
            "labels": [],
            "performance_data": []
        }
        
        # Reinforcement learning components
        self.rl_agent = None
        self.rl_enabled = self.config.get("enable_reinforcement_learning", False)
        
        logger.info(f"🧠 MLTaskRouter {self.router_id} initialized on device: {self.device}")
    
    async def start(self) -> bool:
        """Start the ML task router"""
        try:
            if self.is_running:
                logger.warning("MLTaskRouter is already running")
                return True
            
            self.is_running = True
            self._start_time = time.time()
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Start processing loops
            asyncio.create_task(self._routing_processing_loop())
            asyncio.create_task(self._performance_monitoring_loop())
            asyncio.create_task(self._model_training_loop())
            asyncio.create_task(self._worker_profile_update_loop())
            
            logger.info(f"🚀 MLTaskRouter {self.router_id} started")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start MLTaskRouter: {e}")
            self.is_running = False
            return False
    
    async def stop(self) -> bool:
        """Stop the ML task router"""
        try:
            self.is_running = False
            
            # Save trained models
            await self._save_models()
            
            logger.info(f"🛑 MLTaskRouter {self.router_id} stopped")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to stop MLTaskRouter: {e}")
            return False
    
    async def route_task(self, task: CrawlerTask, available_workers: List[str], strategy: RoutingStrategy = RoutingStrategy.ML_PREDICTED) -> Optional[RoutingDecision]:
        """Route a task to the optimal worker using ML"""
        try:
            if not self.is_running:
                logger.error("MLTaskRouter is not running")
                return None
            
            # Extract task features
            task_features = await self._extract_task_features(task)
            
            # Get worker profiles
            worker_profiles = {
                worker_id: self.worker_profiles.get(worker_id)
                for worker_id in available_workers
                if worker_id in self.worker_profiles
            }
            
            if not worker_profiles:
                logger.warning("No worker profiles available for routing")
                return await self._fallback_routing(task, available_workers)
            
            # Apply routing strategy
            if strategy == RoutingStrategy.ML_PREDICTED:
                decision = await self._ml_routing(task_features, worker_profiles)
            elif strategy == RoutingStrategy.PERFORMANCE_OPTIMIZED:
                decision = await self._performance_optimized_routing(task_features, worker_profiles)
            elif strategy == RoutingStrategy.LOAD_BALANCED:
                decision = await self._load_balanced_routing(task_features, worker_profiles)
            elif strategy == RoutingStrategy.DEADLINE_AWARE:
                decision = await self._deadline_aware_routing(task_features, worker_profiles)
            elif strategy == RoutingStrategy.REINFORCEMENT_LEARNED and self.rl_enabled:
                decision = await self._rl_routing(task_features, worker_profiles)
            else:
                decision = await self._ml_routing(task_features, worker_profiles)
            
            if decision:
                # Store routing decision
                self.routing_results[task.task_id] = decision
                self.routing_history.append(decision)
                
                logger.info(f"🎯 Task {task.task_id} routed to worker {decision.selected_worker_id} (confidence: {decision.confidence_score:.3f})")
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ Failed to route task {task.task_id}: {e}")
            return await self._fallback_routing(task, available_workers)
    
    async def _extract_task_features(self, task: CrawlerTask) -> TaskFeatures:
        """Extract comprehensive features from a task"""
        try:
            # Basic task analysis
            complexity_score = await self._calculate_task_complexity(task)
            estimated_duration = await self._estimate_task_duration(task)
            priority_score = self._map_priority_to_score(task.priority)
            
            # Resource requirements estimation
            resource_requirements = await self._estimate_resource_requirements(task)
            
            # Task categorization
            category = await self._categorize_task(task)
            
            # Platform and data analysis
            data_size = len(str(task.task_data).encode('utf-8'))
            platform_specific = task.platform_type != "generic"
            requires_gpu = await self._requires_gpu_processing(task)
            
            # Create feature object
            task_features = TaskFeatures(
                task_id=task.task_id,
                category=category,
                complexity_score=complexity_score,
                estimated_duration=estimated_duration,
                resource_requirements=resource_requirements,
                priority_score=priority_score,
                data_size=data_size,
                deadline=getattr(task, 'deadline', None),
                dependencies=getattr(task, 'dependencies', []),
                platform_specific=platform_specific,
                requires_gpu=requires_gpu
            )
            
            # Generate feature vector
            task_features.feature_vector = await self._generate_feature_vector(task_features)
            
            return task_features
            
        except Exception as e:
            logger.error(f"❌ Failed to extract task features: {e}")
            raise
    
    async def _ml_routing(self, task_features: TaskFeatures, worker_profiles: Dict[str, WorkerProfile]) -> Optional[RoutingDecision]:
        """Perform ML-based intelligent routing"""
        try:
            best_worker = None
            best_score = float('-inf')
            predictions = {}
            
            for worker_id, profile in worker_profiles.items():
                if profile is None:
                    continue
                
                # Create combined feature vector (task + worker)
                combined_features = await self._create_combined_features(task_features, profile)
                
                # Predict performance
                completion_time, success_prob = await self._predict_performance(combined_features)
                
                # Calculate routing score
                score = await self._calculate_routing_score(
                    task_features, profile, completion_time, success_prob
                )
                
                predictions[worker_id] = {
                    "completion_time": completion_time,
                    "success_probability": success_prob,
                    "routing_score": score
                }
                
                if score > best_score:
                    best_score = score
                    best_worker = worker_id
            
            if best_worker is None:
                return None
            
            # Create routing decision
            best_prediction = predictions[best_worker]
            
            decision = RoutingDecision(
                task_id=task_features.task_id,
                selected_worker_id=best_worker,
                confidence_score=min(best_prediction["success_probability"], 1.0),
                predicted_completion_time=best_prediction["completion_time"],
                predicted_success_probability=best_prediction["success_probability"],
                routing_strategy=RoutingStrategy.ML_PREDICTED,
                reasoning={
                    "routing_score": best_score,
                    "task_category": task_features.category.value,
                    "worker_specializations": list(worker_profiles[best_worker].specializations),
                    "load_factor": worker_profiles[best_worker].current_load,
                    "model_version": "v1.0"
                },
                alternatives=[
                    {
                        "worker_id": wid,
                        "score": pred["routing_score"],
                        "completion_time": pred["completion_time"],
                        "success_probability": pred["success_probability"]
                    }
                    for wid, pred in sorted(predictions.items(), key=lambda x: x[1]["routing_score"], reverse=True)[1:4]
                ]
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"❌ Failed ML routing: {e}")
            return None
    
    async def _performance_optimized_routing(self, task_features: TaskFeatures, worker_profiles: Dict[str, WorkerProfile]) -> Optional[RoutingDecision]:
        """Route based on performance optimization"""
        try:
            best_worker = None
            best_performance = float('-inf')
            
            for worker_id, profile in worker_profiles.items():
                if profile is None:
                    continue
                
                # Calculate performance score
                performance_score = (
                    profile.success_rate * 0.4 +
                    (1.0 / max(profile.average_completion_time, 0.1)) * 0.3 +
                    (1.0 - profile.current_load) * 0.3
                )
                
                # Adjust for task category specialization
                if task_features.category in profile.specializations:
                    performance_score *= 1.2
                
                if performance_score > best_performance:
                    best_performance = performance_score
                    best_worker = worker_id
            
            if best_worker is None:
                return None
            
            return RoutingDecision(
                task_id=task_features.task_id,
                selected_worker_id=best_worker,
                confidence_score=min(best_performance, 1.0),
                predicted_completion_time=worker_profiles[best_worker].average_completion_time,
                predicted_success_probability=worker_profiles[best_worker].success_rate,
                routing_strategy=RoutingStrategy.PERFORMANCE_OPTIMIZED,
                reasoning={
                    "performance_score": best_performance,
                    "worker_success_rate": worker_profiles[best_worker].success_rate,
                    "worker_load": worker_profiles[best_worker].current_load
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed performance optimized routing: {e}")
            return None
    
    async def _load_balanced_routing(self, task_features: TaskFeatures, worker_profiles: Dict[str, WorkerProfile]) -> Optional[RoutingDecision]:
        """Route based on load balancing"""
        try:
            # Sort workers by current load (ascending)
            sorted_workers = sorted(
                worker_profiles.items(),
                key=lambda x: x[1].current_load if x[1] else float('inf')
            )
            
            # Select the least loaded capable worker
            for worker_id, profile in sorted_workers:
                if profile is None:
                    continue
                
                # Check basic capability match
                if await self._worker_can_handle_task(profile, task_features):
                    return RoutingDecision(
                        task_id=task_features.task_id,
                        selected_worker_id=worker_id,
                        confidence_score=0.8,  # Fixed confidence for load balancing
                        predicted_completion_time=profile.average_completion_time,
                        predicted_success_probability=profile.success_rate,
                        routing_strategy=RoutingStrategy.LOAD_BALANCED,
                        reasoning={
                            "load_balancing": True,
                            "worker_load": profile.current_load,
                            "load_rank": sorted_workers.index((worker_id, profile)) + 1
                        }
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed load balanced routing: {e}")
            return None
    
    async def _deadline_aware_routing(self, task_features: TaskFeatures, worker_profiles: Dict[str, WorkerProfile]) -> Optional[RoutingDecision]:
        """Route with deadline awareness"""
        try:
            if task_features.deadline is None:
                # Fall back to performance optimized routing
                return await self._performance_optimized_routing(task_features, worker_profiles)
            
            time_remaining = (task_features.deadline - datetime.utcnow()).total_seconds()
            
            if time_remaining <= 0:
                logger.warning(f"Task {task_features.task_id} deadline already passed")
                return None
            
            # Find workers that can meet the deadline
            capable_workers = []
            
            for worker_id, profile in worker_profiles.items():
                if profile is None:
                    continue
                
                # Estimate if worker can complete task before deadline
                estimated_completion = profile.average_completion_time * (1 + profile.current_load)
                
                if estimated_completion < time_remaining:
                    capable_workers.append((worker_id, profile, estimated_completion))
            
            if not capable_workers:
                logger.warning(f"No workers can meet deadline for task {task_features.task_id}")
                return None
            
            # Select the most reliable among capable workers
            best_worker = max(
                capable_workers,
                key=lambda x: x[1].success_rate
            )
            
            worker_id, profile, estimated_time = best_worker
            
            return RoutingDecision(
                task_id=task_features.task_id,
                selected_worker_id=worker_id,
                confidence_score=profile.success_rate,
                predicted_completion_time=estimated_time,
                predicted_success_probability=profile.success_rate,
                routing_strategy=RoutingStrategy.DEADLINE_AWARE,
                reasoning={
                    "deadline_aware": True,
                    "time_remaining": time_remaining,
                    "estimated_completion": estimated_time,
                    "deadline_margin": time_remaining - estimated_time
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed deadline aware routing: {e}")
            return None
    
    async def _rl_routing(self, task_features: TaskFeatures, worker_profiles: Dict[str, WorkerProfile]) -> Optional[RoutingDecision]:
        """Reinforcement learning based routing"""
        try:
            # This would implement RL-based routing in a full implementation
            # For now, fall back to ML routing
            logger.info("RL routing not fully implemented, falling back to ML routing")
            return await self._ml_routing(task_features, worker_profiles)
            
        except Exception as e:
            logger.error(f"❌ Failed RL routing: {e}")
            return None
    
    async def _fallback_routing(self, task: CrawlerTask, available_workers: List[str]) -> Optional[RoutingDecision]:
        """Simple fallback routing when ML routing fails"""
        try:
            if not available_workers:
                return None
            
            # Simple round-robin selection
            selected_worker = available_workers[hash(task.task_id) % len(available_workers)]
            
            return RoutingDecision(
                task_id=task.task_id,
                selected_worker_id=selected_worker,
                confidence_score=0.5,  # Low confidence for fallback
                predicted_completion_time=300.0,  # Default 5 minutes
                predicted_success_probability=0.8,  # Optimistic default
                routing_strategy=RoutingStrategy.LOAD_BALANCED,
                reasoning={
                    "fallback_routing": True,
                    "method": "round_robin",
                    "available_workers": len(available_workers)
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed fallback routing: {e}")
            return None
    
    async def update_worker_profile(self, worker_id: str, metrics: Dict[str, Any]):
        """Update worker profile with new metrics"""
        try:
            if worker_id not in self.worker_profiles:
                # Create new profile
                self.worker_profiles[worker_id] = WorkerProfile(
                    worker_id=worker_id,
                    capabilities=set(),
                    performance_metrics={},
                    current_load=0.0,
                    success_rate=1.0,
                    average_completion_time=300.0,
                    specializations=[],
                    resource_limits={}
                )
            
            profile = self.worker_profiles[worker_id]
            
            # Update metrics
            profile.performance_metrics.update(metrics.get("performance_metrics", {}))
            profile.current_load = metrics.get("current_load", profile.current_load)
            profile.success_rate = metrics.get("success_rate", profile.success_rate)
            profile.average_completion_time = metrics.get("average_completion_time", profile.average_completion_time)
            profile.last_updated = datetime.utcnow()
            
            # Update capabilities if provided
            if "capabilities" in metrics:
                profile.capabilities = set(metrics["capabilities"])
            
            # Update specializations if provided
            if "specializations" in metrics:
                profile.specializations = metrics["specializations"]
            
            logger.debug(f"📊 Updated worker profile: {worker_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to update worker profile {worker_id}: {e}")
    
    async def report_task_completion(self, task_id: str, success: bool, completion_time: float, worker_id: str):
        """Report task completion for model learning"""
        try:
            if task_id in self.routing_results:
                decision = self.routing_results[task_id]
                
                # Store performance feedback
                self.performance_feedback[task_id] = {
                    "success": success,
                    "actual_completion_time": completion_time,
                    "predicted_completion_time": decision.predicted_completion_time,
                    "predicted_success": decision.predicted_success_probability,
                    "worker_id": worker_id,
                    "routing_strategy": decision.routing_strategy.value,
                    "reported_at": datetime.utcnow()
                }
                
                # Update model metrics
                await self._update_model_metrics()
                
                # Collect training data
                await self._collect_training_data(decision, success, completion_time)
                
                logger.debug(f"📈 Reported completion for task {task_id}: success={success}, time={completion_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to report task completion: {e}")
    
    async def _initialize_ml_models(self):
        """Initialize and load ML models"""
        try:
            # Initialize neural networks
            feature_size = 20  # Adjustable based on feature engineering
            
            self.task_classifier = TaskClassifierNN(feature_size, 128, len(TaskCategory))
            self.performance_predictor = PerformancePredictorNN(feature_size * 2)  # task + worker features
            
            # Move to appropriate device
            self.task_classifier.to(self.device)
            self.performance_predictor.to(self.device)
            
            # Initialize traditional ML models
            self.rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.gb_regressor = GradientBoostingRegressor(n_estimators=100, random_state=42)
            
            # Try to load pre-trained models
            await self._load_models()
            
            logger.info("✅ ML models initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML models: {e}")
    
    async def _routing_processing_loop(self):
        """Process routing requests"""
        while self.is_running:
            try:
                # Process any pending routing requests
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Error in routing processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _performance_monitoring_loop(self):
        """Monitor routing performance"""
        while self.is_running:
            try:
                # Calculate performance metrics
                await self._calculate_performance_metrics()
                
                # Sleep for 60 seconds
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Error in performance monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _model_training_loop(self):
        """Periodic model retraining"""
        while self.is_running:
            try:
                # Check if we have enough data for retraining
                if len(self.training_data["features"]) >= 100:
                    await self._retrain_models()
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"❌ Error in model training loop: {e}")
                await asyncio.sleep(300)
    
    async def _worker_profile_update_loop(self):
        """Update worker profiles periodically"""
        while self.is_running:
            try:
                # Update worker profiles from worker pool
                if self.worker_pool:
                    await self._sync_worker_profiles()
                
                # Sleep for 30 seconds
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Error in worker profile update loop: {e}")
                await asyncio.sleep(10)
    
    def _map_priority_to_score(self, priority: TaskPriority) -> float:
        """Map task priority to numerical score"""
        priority_mapping = {
            TaskPriority.LOW: 0.2,
            TaskPriority.NORMAL: 0.5,
            TaskPriority.HIGH: 0.8,
            TaskPriority.URGENT: 1.0
        }
        return priority_mapping.get(priority, 0.5)
    
    async def get_router_status(self) -> Dict[str, Any]:
        """Get current router status"""
        return {
            "router_id": self.router_id,
            "is_running": self.is_running,
            "device": str(self.device),
            "worker_profiles_count": len(self.worker_profiles),
            "routing_history_size": len(self.routing_history),
            "pending_routes": self.routing_queue.qsize(),
            "model_metrics": self.model_metrics.copy(),
            "training_data_size": len(self.training_data["features"]),
            "uptime": time.time() - getattr(self, '_start_time', time.time())
        }
    
    # Placeholder methods that would be fully implemented in production
    async def _calculate_task_complexity(self, task: CrawlerTask) -> float:
        """Calculate task complexity score"""
        # Simplified implementation
        base_complexity = 0.5
        if hasattr(task, 'target_urls') and len(task.target_urls) > 10:
            base_complexity += 0.3
        if hasattr(task, 'extract_media') and task.extract_media:
            base_complexity += 0.2
        return min(base_complexity, 1.0)
    
    async def _estimate_task_duration(self, task: CrawlerTask) -> float:
        """Estimate task duration in seconds"""
        # Simplified implementation
        base_duration = 120.0  # 2 minutes base
        if hasattr(task, 'target_urls'):
            base_duration += len(task.target_urls) * 10
        return base_duration
    
    async def _estimate_resource_requirements(self, task: CrawlerTask) -> Dict[str, float]:
        """Estimate resource requirements"""
        return {
            "cpu": 0.5,
            "memory": 512.0,  # MB
            "network": 1.0,
            "storage": 100.0  # MB
        }
    
    async def _categorize_task(self, task: CrawlerTask) -> TaskCategory:
        """Categorize task using ML or heuristics"""
        # Simplified implementation
        if hasattr(task, 'extract_media') and task.extract_media:
            return TaskCategory.MEDIA_PROCESSING
        elif hasattr(task, 'generate_fingerprint') and task.generate_fingerprint:
            return TaskCategory.FINGERPRINTING
        else:
            return TaskCategory.CONTENT_CRAWLING
    
    async def _requires_gpu_processing(self, task: CrawlerTask) -> bool:
        """Check if task requires GPU processing"""
        # Simplified implementation
        return hasattr(task, 'ai_processing') and task.ai_processing
    
    async def _generate_feature_vector(self, task_features: TaskFeatures) -> np.ndarray:
        """Generate numerical feature vector from task features"""
        # Simplified implementation
        feature_vector = np.array([
            task_features.complexity_score,
            task_features.estimated_duration / 1000.0,  # Normalize
            task_features.priority_score,
            task_features.data_size / 1000000.0,  # Normalize to MB
            1.0 if task_features.platform_specific else 0.0,
            1.0 if task_features.requires_gpu else 0.0,
            len(task_features.dependencies),
            # Add more features as needed
        ])
        
        # Pad or truncate to fixed size
        target_size = 20
        if len(feature_vector) < target_size:
            feature_vector = np.pad(feature_vector, (0, target_size - len(feature_vector)))
        elif len(feature_vector) > target_size:
            feature_vector = feature_vector[:target_size]
        
        return feature_vector
    
    async def _create_combined_features(self, task_features: TaskFeatures, worker_profile: WorkerProfile) -> np.ndarray:
        """Create combined feature vector for task and worker"""
        task_vector = task_features.feature_vector
        
        # Worker feature vector
        worker_vector = np.array([
            worker_profile.current_load,
            worker_profile.success_rate,
            worker_profile.average_completion_time / 1000.0,  # Normalize
            len(worker_profile.capabilities),
            len(worker_profile.specializations),
            1.0 if task_features.category in worker_profile.specializations else 0.0,
            # Add more worker features
        ])
        
        # Pad worker vector to match task vector size
        target_size = len(task_vector)
        if len(worker_vector) < target_size:
            worker_vector = np.pad(worker_vector, (0, target_size - len(worker_vector)))
        elif len(worker_vector) > target_size:
            worker_vector = worker_vector[:target_size]
        
        return np.concatenate([task_vector, worker_vector])
    
    async def _predict_performance(self, combined_features: np.ndarray) -> Tuple[float, float]:
        """Predict task completion time and success probability"""
        try:
            if self.performance_predictor is None:
                # Fallback prediction
                return 300.0, 0.8
            
            # Convert to tensor
            feature_tensor = torch.FloatTensor(combined_features).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                prediction = self.performance_predictor(feature_tensor)
                completion_time = prediction[0, 0].item() * 1000.0  # Denormalize
                success_prob = prediction[0, 1].item()
            
            return completion_time, success_prob
            
        except Exception as e:
            logger.error(f"❌ Failed to predict performance: {e}")
            return 300.0, 0.8
    
    async def _calculate_routing_score(self, task_features: TaskFeatures, worker_profile: WorkerProfile, completion_time: float, success_prob: float) -> float:
        """Calculate overall routing score"""
        # Weighted scoring
        time_score = 1.0 / max(completion_time / 1000.0, 0.1)  # Prefer faster completion
        success_score = success_prob  # Prefer higher success probability
        load_score = 1.0 - worker_profile.current_load  # Prefer lower load
        specialization_score = 1.2 if task_features.category in worker_profile.specializations else 1.0
        
        overall_score = (
            time_score * 0.3 +
            success_score * 0.4 +
            load_score * 0.2 +
            (specialization_score - 1.0) * 0.1
        )
        
        return overall_score
    
    async def _worker_can_handle_task(self, worker_profile: WorkerProfile, task_features: TaskFeatures) -> bool:
        """Check if worker can handle the task"""
        # Basic capability checking
        if task_features.requires_gpu and WorkerCapability.GPU_ACCELERATED not in worker_profile.capabilities:
            return False
        
        # Check resource limits
        cpu_requirement = task_features.resource_requirements.get("cpu", 0.5)
        if cpu_requirement > worker_profile.resource_limits.get("cpu", 1.0):
            return False
        
        return True
    
    # Placeholder methods for model training and management
    async def _load_models(self):
        """Load pre-trained models"""
        try:
            # Try to load saved models
            pass
        except Exception as e:
            logger.debug(f"No pre-trained models found: {e}")
    
    async def _save_models(self):
        """Save trained models"""
        try:
            # Save models to disk
            pass
        except Exception as e:
            logger.error(f"❌ Failed to save models: {e}")
    
    async def _retrain_models(self):
        """Retrain models with new data"""
        try:
            logger.info("🔄 Retraining ML models...")
            # Implement model retraining
        except Exception as e:
            logger.error(f"❌ Failed to retrain models: {e}")
    
    async def _update_model_metrics(self):
        """Update model performance metrics"""
        try:
            # Calculate metrics based on performance feedback
            pass
        except Exception as e:
            logger.error(f"❌ Failed to update model metrics: {e}")
    
    async def _collect_training_data(self, decision: RoutingDecision, success: bool, completion_time: float):
        """Collect data for model training"""
        try:
            # Store training examples
            pass
        except Exception as e:
            logger.error(f"❌ Failed to collect training data: {e}")
    
    async def _calculate_performance_metrics(self):
        """Calculate routing performance metrics"""
        try:
            # Calculate various performance metrics
            pass
        except Exception as e:
            logger.error(f"❌ Failed to calculate performance metrics: {e}")
    
    async def _sync_worker_profiles(self):
        """Sync worker profiles from worker pool"""
        try:
            # Sync with worker pool
            pass
        except Exception as e:
            logger.error(f"❌ Failed to sync worker profiles: {e}")


# Global router instance
_ml_task_router: Optional[MLTaskRouter] = None


async def get_ml_task_router() -> Optional[MLTaskRouter]:
    """Get the global ML task router instance"""
    return _ml_task_router


async def initialize_ml_task_router(config: Dict[str, Any] = None) -> bool:
    """Initialize the ML task router"""
    global _ml_task_router
    
    try:
        if _ml_task_router is not None:
            logger.warning("MLTaskRouter already initialized")
            return True
        
        _ml_task_router = MLTaskRouter(config)
        success = await _ml_task_router.start()
        
        if success:
            logger.info("✅ MLTaskRouter initialized successfully")
        else:
            logger.error("❌ Failed to initialize MLTaskRouter")
            _ml_task_router = None
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize MLTaskRouter: {e}")
        _ml_task_router = None
        return False


async def shutdown_ml_task_router() -> bool:
    """Shutdown the ML task router"""
    global _ml_task_router
    
    try:
        if _ml_task_router is None:
            logger.warning("MLTaskRouter not initialized")
            return True
        
        success = await _ml_task_router.stop()
        _ml_task_router = None
        
        if success:
            logger.info("✅ MLTaskRouter shutdown successfully")
        else:
            logger.error("❌ Failed to shutdown MLTaskRouter")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Failed to shutdown MLTaskRouter: {e}")
        return False


# Export classes and functions
__all__ = [
    "MLTaskRouter",
    "TaskCategory",
    "RoutingStrategy",
    "WorkerCapability",
    "TaskFeatures",
    "WorkerProfile",
    "RoutingDecision",
    "TaskClassifierNN",
    "PerformancePredictorNN",
    "get_ml_task_router",
    "initialize_ml_task_router",
    "shutdown_ml_task_router"
]
