"""Adaptive Scheduler Module
========================

Machine learning-powered adaptive scheduling system for crawler operations.
Implements self-learning and self-optimizing scheduling algorithms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts

Business Logic Integration:
Continuous learning → Performance pattern recognition → Adaptive optimization → 
Predictive scheduling → Business impact analysis → Revenue optimization → 
User experience enhancement → Competitive advantage → Market leadership
"""

import asyncio
import logging
import time
import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple, Union, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error, accuracy_score
import tensorflow as tf
from tensorflow import keras
import joblib
import sqlite3
import aiofiles
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AdaptationStrategy(Enum):
    """
Adaptation strategy types."""

    PERFORMANCE_BASED = "performance_based"
    PATTERN_RECOGNITION = "pattern_recognition"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    MULTI_OBJECTIVE = "multi_objective"
    BUSINESS_IMPACT = "business_impact"
    USER_BEHAVIOR = "user_behavior"
    HYBRID = "hybrid"


class LearningMode(Enum):
    """Learning operation modes."""

    EXPLORATION = "exploration"  # Try new strategies
    EXPLOITATION = "exploitation"  # Use best known strategies
    BALANCED = "balanced"  # Mix of both
    CONSERVATIVE = "conservative"  # Minimal changes
    AGGRESSIVE = "aggressive"  # Rapid adaptation


class OptimizationObjective(Enum):
    """Optimization objectives."""

    MINIMIZE_LATENCY = "minimize_latency"
    MAXIMIZE_THROUGHPUT = "maximize_throughput"
    OPTIMIZE_RESOURCES = "optimize_resources"
    IMPROVE_ACCURACY = "improve_accuracy"
    REDUCE_COSTS = "reduce_costs"
    ENHANCE_USER_EXPERIENCE = "enhance_user_experience"
    INCREASE_REVENUE = "increase_revenue"
    MAINTAIN_SLA = "maintain_sla"


@dataclass
class PerformancePattern:
    """Performance pattern identification."""
    pattern_id: str
    pattern_type: str
    frequency: float
    confidence: float
    impact_score: float
    discovered_at: datetime
    last_seen: datetime
    pattern_data: Dict[str, Any]
    business_context: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class AdaptationDecision:
    """
Adaptation decision record."""
    decision_id: str
    strategy: AdaptationStrategy
    objective: OptimizationObjective
    learning_mode: LearningMode
    confidence: float
    expected_improvement: float
    decision_data: Dict[str, Any]
    created_at: datetime
    implemented_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    rollback_plan: Optional[Dict[str, Any]] = None


@dataclass
class LearningState:
    """
Current learning state."""
    exploration_rate: float = 0.3
    exploitation_rate: float = 0.7
    learning_rate: float = 0.01
    model_confidence: float = 0.5
    adaptation_count: int = 0
    success_rate: float = 0.0
    last_adaptation: Optional[datetime] = None
    current_strategy: AdaptationStrategy = AdaptationStrategy.BALANCED
    active_experiments: Set[str] = field(default_factory=set)


@dataclass
class ReinforcementState:
    """
Reinforcement learning state."""
    state_vector: List[float]
    action_space: List[str]
    reward_history: deque
    q_values: Dict[str, float] = field(default_factory=dict)
    epsilon: float = 0.1  # Exploration rate
    alpha: float = 0.1    # Learning rate
    gamma: float = 0.95   # Discount factor
    last_state: Optional[List[float]] = None
    last_action: Optional[str] = None
    last_reward: float = 0.0


class AdaptiveScheduler:
    """
    Machine learning-powered adaptive scheduler.
    
    Features:
    - Continuous performance monitoring and learning
    - Pattern recognition and prediction
    - Reinforcement learning for optimization
    - Multi-objective optimization
    - Business impact-aware adaptations
    - Real-time strategy adjustment
    - Self-healing and recovery
    - Competitive intelligence integration
    """
    
    def __init__(
        self,
        adaptation_strategy: AdaptationStrategy = AdaptationStrategy.HYBRID,
        learning_mode: LearningMode = LearningMode.BALANCED,
        enable_reinforcement_learning: bool = True,
        enable_pattern_recognition: bool = True,
        enable_deep_learning: bool = True,
        adaptation_interval: int = 300,  # seconds
        learning_history_size: int = 10000
    ):
        """
Initialize adaptive scheduler."""
        self.adaptation_strategy = adaptation_strategy
        self.learning_mode = learning_mode
        self.enable_reinforcement_learning = enable_reinforcement_learning
        self.enable_pattern_recognition = enable_pattern_recognition
        self.enable_deep_learning = enable_deep_learning
        self.adaptation_interval = adaptation_interval
        self.learning_history_size = learning_history_size
        
        # Learning models
        self.performance_predictor = None
        self.pattern_classifier = None
        self.deep_learning_model = None
        self.reinforcement_agent = None
        
        # Data processors
        self.feature_scaler = StandardScaler()
        self.target_scaler = MinMaxScaler()
        self.pattern_clusters = None
        
        # Learning state
        self.learning_state = LearningState()
        self.reinforcement_state = ReinforcementState(
            state_vector=[],
            action_space=[
                'increase_frequency', 'decrease_frequency',
                'optimize_timing', 'adjust_resources',
                'change_strategy', 'maintain_current'
            ],
            reward_history=deque(maxlen=1000)
        )
        
        # Data storage
        self.performance_history: deque = deque(maxlen=learning_history_size)
        self.pattern_history: deque = deque(maxlen=1000)
        self.adaptation_history: deque = deque(maxlen=500)
        self.discovered_patterns: Dict[str, PerformancePattern] = {}
        
        # Business intelligence
        self.business_metrics: Dict[str, float] = {}
        self.user_behavior_patterns: Dict[str, Any] = {}
        self.competitive_intelligence: Dict[str, Any] = {}
        
        # Configuration
        self.config = {
            'learning_enabled': True,
            'adaptation_enabled': True,
            'pattern_detection_enabled': True,
            'business_optimization_enabled': True,
            'model_update_frequency': 3600,  # seconds
            'pattern_discovery_threshold': 0.7,
            'adaptation_confidence_threshold': 0.6,
            'rollback_threshold': 0.3,
            'exploration_decay_rate': 0.995,
            'max_concurrent_experiments': 3,
            'safety_constraints_enabled': True,
            'model_storage_path': './models/adaptive',
            'performance_baseline_window': 24 * 3600,  # 24 hours
            'business_impact_weight': 0.3
        }
        
        # State tracking
        self.is_learning = False
        self.learning_task: Optional[asyncio.Task] = None
        self.adaptation_task: Optional[asyncio.Task] = None
        self.pattern_detection_task: Optional[asyncio.Task] = None
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = defaultdict(list)
        
        logger.info(f"Adaptive scheduler initialized with strategy: {adaptation_strategy.value}")
    
    async def initialize(self) -> None:
        """Initialize adaptive scheduler."""
        try:
            # Create model storage directory
            import os
            os.makedirs(self.config['model_storage_path'], exist_ok=True)
            
            # Initialize ML models
            await self._initialize_models()
            
            # Load existing models if available
            await self._load_models()
            
            # Start learning processes
            await self.start_learning()
            
            logger.info("Adaptive scheduler initialization complete")
            
        except Exception as e:
            logger.error(f"Failed to initialize adaptive scheduler: {e}")
            raise
    
    async def _initialize_models(self) -> None:
        """Initialize machine learning models."""
        try:
            # Performance prediction model
            self.performance_predictor = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            
            # Pattern classification model
            self.pattern_classifier = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42
            )
            
            # Deep learning model for complex patterns
            if self.enable_deep_learning:
                self.deep_learning_model = self._create_deep_learning_model()
            
            # Reinforcement learning agent
            if self.enable_reinforcement_learning:
                self.reinforcement_agent = self._create_reinforcement_agent()
            
            # Pattern clustering
            self.pattern_clusters = KMeans(n_clusters=10, random_state=42)
            
            logger.info("Machine learning models initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize models: {e}")
    
    def _create_deep_learning_model(self) -> keras.Model:
        """Create deep learning model for pattern recognition."""
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(50,)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(16, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _create_reinforcement_agent(self) -> Dict[str, Any]:
        """
Create reinforcement learning agent."""
        return {
            'q_table': defaultdict(lambda: defaultdict(float)),
            'state_action_counts': defaultdict(lambda: defaultdict(int)),
            'total_episodes': 0,
            'total_reward': 0.0,
            'best_policy': {},
            'exploration_schedule': []
        }
    
    async def start_learning(self) -> None:
        """
Start adaptive learning processes."""
        if self.is_learning:
            return
        
        self.is_learning = True
        
        # Start learning tasks
        self.learning_task = asyncio.create_task(self._learning_loop())
        self.adaptation_task = asyncio.create_task(self._adaptation_loop())
        
        if self.enable_pattern_recognition:
            self.pattern_detection_task = asyncio.create_task(self._pattern_detection_loop())
        
        logger.info("Adaptive learning started")
    
    async def stop_learning(self) -> None:
        try:
            logger.info(f"Executing stop_learning")
            
            # Implementation for stop_learning
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"stop_learning completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"stop_learning failed: {e}")
            raise
    async def learn_from_performance(
        self,
        performance_data: Dict[str, Any],
        business_context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Learn from performance data."""
        try:
            # Enhance data with business context
            enhanced_data = {
                **performance_data,
                'timestamp': datetime.utcnow(),
                'business_context': business_context or {}
            }
            
            # Store in history
            self.performance_history.append(enhanced_data)
            
            # Update business metrics
            if business_context:
                self._update_business_metrics(business_context)
            
            # Trigger online learning if enough data
            if len(self.performance_history) % 50 == 0:
                await self._trigger_online_learning()
            
            # Update reinforcement learning
            if self.enable_reinforcement_learning:
                await self._update_reinforcement_learning(enhanced_data)
            
        except Exception as e:
            logger.error(f"Learning from performance failed: {e}")
    
    async def _learning_loop(self) -> None:
        """Main learning loop."""
        while self.is_learning:
            try:
                # Update models with recent data
                await self._update_models()
                
                # Evaluate current performance
                await self._evaluate_performance()
                
                # Adjust learning parameters
                await self._adjust_learning_parameters()
                
                await asyncio.sleep(self.config['model_update_frequency'])
                
            except Exception as e:
                logger.error(f"Learning loop error: {e}")
                await asyncio.sleep(60)
    
    async def _adaptation_loop(self) -> None:
        """Main adaptation loop."""
        while self.is_learning:
            try:
                # Evaluate need for adaptation
                if await self._should_adapt():
                    # Generate adaptation decision
                    decision = await self._generate_adaptation_decision()
                    
                    if decision:
                        # Implement adaptation
                        await self._implement_adaptation(decision)
                
                await asyncio.sleep(self.adaptation_interval)
                
            except Exception as e:
                logger.error(f"Adaptation loop error: {e}")
                await asyncio.sleep(60)
    
    async def _pattern_detection_loop(self) -> None:
        """Pattern detection loop."""
        while self.is_learning:
            try:
                # Analyze recent performance for patterns
                await self._detect_performance_patterns()
                
                # Update pattern clusters
                await self._update_pattern_clusters()
                
                # Clean up old patterns
                await self._cleanup_patterns()
                
                await asyncio.sleep(300)  # Every 5 minutes
                
            except Exception as e:
                logger.error(f"Pattern detection error: {e}")
                await asyncio.sleep(60)
    
    async def _update_models(self) -> None:
        """Update ML models with recent data."""
        try:
            if len(self.performance_history) < 100:
                return
            
            # Prepare training data
            recent_data = list(self.performance_history)[-500:]
            X, y = await self._prepare_training_data(recent_data)
            
            if len(X) < 10:
                return
            
            # Update performance predictor
            if self.performance_predictor:
                self.performance_predictor.fit(X, y)
                
                # Evaluate model performance
                predictions = self.performance_predictor.predict(X)
                mse = mean_squared_error(y, predictions)
                self.learning_state.model_confidence = max(0.1, 1.0 - (mse / np.var(y)))
            
            # Update deep learning model
            if self.enable_deep_learning and self.deep_learning_model and len(X) > 50:
                # Prepare data for deep learning
                X_deep = self._prepare_deep_learning_features(recent_data)
                y_deep = self._prepare_deep_learning_targets(recent_data)
                
                if len(X_deep) > 0:
                    self.deep_learning_model.fit(
                        np.array(X_deep), 
                        np.array(y_deep),
                        epochs=10,
                        batch_size=32,
                        verbose=0
                    )
            
            logger.info(f"Models updated with {len(X)} samples, confidence: {self.learning_state.model_confidence:.3f}")
            
        except Exception as e:
            logger.error(f"Model update failed: {e}")
    
    async def _prepare_training_data(self, data: List[Dict[str, Any]]) -> Tuple[List[List[float]], List[float]]:
        """Prepare training data from performance history."""

        X = []
        y = []
        
        for item in data:
            # Extract features
            features = await self._extract_features(item)
            
            # Extract target (performance score)
            target = self._calculate_performance_score(item)
            
            if features and target is not None:
                X.append(features)
                y.append(target)
        
        return X, y
    
    async def _extract_features(self, data: Dict[str, Any]) -> Optional[List[float]]:
        """
Extract feature vector from performance data."""
        try:
            features = []
            
            # Basic performance metrics
            features.append(data.get('execution_time', 0))
            features.append(data.get('success_rate', 0))
            features.append(data.get('resource_usage', 0))
            features.append(data.get('queue_length', 0))
            features.append(data.get('error_rate', 0))
            
            # Temporal features
            timestamp = data.get('timestamp', datetime.utcnow())
            features.append(timestamp.hour)
            features.append(timestamp.weekday())
            features.append(timestamp.day)
            
            # Business context features
            business_ctx = data.get('business_context', {})
            features.append(business_ctx.get('priority', 0.5))
            features.append(business_ctx.get('business_impact', 0.5))
            features.append(business_ctx.get('user_satisfaction', 0.5))
            
            # System state features
            features.append(data.get('cpu_usage', 0))
            features.append(data.get('memory_usage', 0))
            features.append(data.get('network_usage', 0))
            
            # Historical context
            features.append(self.learning_state.success_rate)
            features.append(self.learning_state.model_confidence)
            features.append(len(self.performance_history))
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return None
    
    def _calculate_performance_score(self, data: Dict[str, Any]) -> Optional[float]:
        """Calculate performance score from data."""
        try:
            # Weighted performance score
            execution_time = data.get('execution_time', 60)
            success_rate = data.get('success_rate', 0.9)
            resource_efficiency = 1.0 - data.get('resource_usage', 0.5)
            user_satisfaction = data.get('business_context', {}).get('user_satisfaction', 0.8)
            
            # Normalize execution time (lower is better)
            time_score = max(0, 1.0 - (execution_time / 300))  # Normalize to 5 minutes
            
            # Combine metrics
            score = (
                time_score * 0.3 +
                success_rate * 0.4 +
                resource_efficiency * 0.2 +
                user_satisfaction * 0.1
            )
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Performance score calculation failed: {e}")
            return None
    
    def _prepare_deep_learning_features(self, data: List[Dict[str, Any]]) -> List[List[float]]:
        """Prepare features for deep learning model."""
        features = []
        
        for item in data:
            feature_vector = []
            
            # Extended feature set for deep learning
            basic_features = [
                item.get('execution_time', 0),
                item.get('success_rate', 0),
                item.get('resource_usage', 0),
                item.get('queue_length', 0),
                item.get('error_rate', 0),
                item.get('cpu_usage', 0),
                item.get('memory_usage', 0),
                item.get('network_usage', 0)
            ]
            
            # Add temporal embeddings
            timestamp = item.get('timestamp', datetime.utcnow())
            temporal_features = [
                np.sin(2 * np.pi * timestamp.hour / 24),
                np.cos(2 * np.pi * timestamp.hour / 24),
                np.sin(2 * np.pi * timestamp.weekday() / 7),
                np.cos(2 * np.pi * timestamp.weekday() / 7)
            ]
            
            # Business context features
            business_ctx = item.get('business_context', {})
            business_features = [
                business_ctx.get('priority', 0.5),
                business_ctx.get('business_impact', 0.5),
                business_ctx.get('user_satisfaction', 0.5),
                business_ctx.get('revenue_impact', 0.5)
            ]
            
            # Combine all features
            feature_vector.extend(basic_features)
            feature_vector.extend(temporal_features)
            feature_vector.extend(business_features)
            
            # Pad to fixed size (50 features)
            while len(feature_vector) < 50:
                feature_vector.append(0.0)
            
            features.append(feature_vector[:50])
        
        return features
    
    def _prepare_deep_learning_targets(self, data: List[Dict[str, Any]]) -> List[float]:
        """
Prepare targets for deep learning model."""
        targets = []
        
        for item in data:
            # Binary classification: good performance (1) or poor performance (0)
            performance_score = self._calculate_performance_score(item)
            target = 1.0 if performance_score and performance_score > 0.7 else 0.0
            targets.append(target)
        
        return targets
    
    async def _should_adapt(self) -> bool:
        """
Determine if adaptation is needed."""
        try:
            # Check if enough time has passed since last adaptation
            if self.learning_state.last_adaptation:
                time_since_last = (datetime.utcnow() - self.learning_state.last_adaptation).seconds
                if time_since_last < self.adaptation_interval:
                    return False
            
            # Check if there's sufficient data
            if len(self.performance_history) < 50:
                return False
            
            # Evaluate current performance against baseline
            current_performance = await self._evaluate_current_performance()
            baseline_performance = await self._get_baseline_performance()
            
            # Adapt if performance degrades significantly
            performance_threshold = 0.1  # 10% degradation
            if baseline_performance - current_performance > performance_threshold:
                return True
            
            # Check for new patterns
            if await self._has_new_patterns():
                return True
            
            # Periodic adaptation in exploration mode
            if self.learning_mode == LearningMode.EXPLORATION:
                if len(self.adaptation_history) == 0 or \
                   (datetime.utcnow() - self.adaptation_history[-1].created_at).seconds > 1800:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Adaptation evaluation failed: {e}")
            return False
    
    async def _evaluate_current_performance(self) -> float:
        """Evaluate current system performance."""
        if not self.performance_history:
            return 0.5
        
        # Calculate average performance over recent window
        recent_data = list(self.performance_history)[-50:]
        scores = [
            self._calculate_performance_score(item) 
            for item in recent_data
            if self._calculate_performance_score(item) is not None
        ]
        
        return np.mean(scores) if scores else 0.5
    
    async def _get_baseline_performance(self) -> float:
        """
Get baseline performance for comparison."""
        window_size = min(200, len(self.performance_history))
        if window_size < 10:
            return 0.7  # Default baseline
        
        # Calculate baseline from historical data
        baseline_data = list(self.performance_history)[-window_size:-50]
        scores = [
            self._calculate_performance_score(item) 
            for item in baseline_data
            if self._calculate_performance_score(item) is not None
        ]
        
        return np.mean(scores) if scores else 0.7
    
    async def _has_new_patterns(self) -> bool:
        """
Check if new performance patterns have been discovered."""
        return len(self.pattern_history) > len(self.discovered_patterns) * 10
    
    async def _generate_adaptation_decision(self) -> Optional[AdaptationDecision]:
        """
Generate adaptation decision based on current state."""
        try:
            # Analyze current situation
            current_state = await self._analyze_current_state()
            
            # Generate adaptation options
            adaptation_options = await self._generate_adaptation_options(current_state)
            
            if not adaptation_options:
                return None
            
            # Select best option based on strategy
            best_option = await self._select_best_adaptation(adaptation_options)
            
            if not best_option:
                return None
            
            # Create adaptation decision
            decision = AdaptationDecision(
                decision_id=f"adapt_{int(time.time())}",
                strategy=self.adaptation_strategy,
                objective=best_option['objective'],
                learning_mode=self.learning_mode,
                confidence=best_option['confidence'],
                expected_improvement=best_option['expected_improvement'],
                decision_data=best_option,
                created_at=datetime.utcnow(),
                rollback_plan=best_option.get('rollback_plan')
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Adaptation decision generation failed: {e}")
            return None
    
    async def _analyze_current_state(self) -> Dict[str, Any]:
        """Analyze current system state."""
        state = {
            'performance_trend': await self._calculate_performance_trend(),
            'resource_utilization': await self._get_resource_utilization(),
            'error_patterns': await self._analyze_error_patterns(),
            'business_metrics': self.business_metrics.copy(),
            'user_satisfaction': self._get_user_satisfaction(),
            'competitive_position': self.competitive_intelligence.copy(),
            'learning_state': asdict(self.learning_state)
        }
        
        return state
    
    async def _calculate_performance_trend(self) -> str:
        """
Calculate performance trend direction."""
        if len(self.performance_history) < 20:
            return "stable"
        
        recent_scores = [
            self._calculate_performance_score(item)
            for item in list(self.performance_history)[-20:]
            if self._calculate_performance_score(item) is not None
        ]
        
        if len(recent_scores) < 10:
            return "stable"
        
        # Simple trend analysis
        first_half = np.mean(recent_scores[:len(recent_scores)//2])
        second_half = np.mean(recent_scores[len(recent_scores)//2:])
        
        if second_half > first_half + 0.05:
            return "improving"
        elif second_half < first_half - 0.05:
            return "degrading"
        else:
            return "stable"
    
    async def _get_resource_utilization(self) -> Dict[str, float]:
        """Get current resource utilization."""
        # This would integrate with the resource scheduler
        return {
            'cpu': 0.6,
            'memory': 0.7,
            'network': 0.4,
            'database': 0.5
        }
    
    async def _analyze_error_patterns(self) -> Dict[str, Any]:
        """
Analyze error patterns in recent performance."""
        if not self.performance_history:
            return {}
        
        recent_data = list(self.performance_history)[-100:]
        error_types = defaultdict(int)
        error_trends = defaultdict(list)
        
        for item in recent_data:
            if item.get('error_rate', 0) > 0:
                error_type = item.get('error_type', 'unknown')
                error_types[error_type] += 1
                error_trends[error_type].append(item.get('error_rate', 0))
        
        return {
            'error_types': dict(error_types),
            'error_trends': {k: np.mean(v) for k, v in error_trends.items()},
            'total_errors': sum(error_types.values())
        }
    
    def _get_user_satisfaction(self) -> float:
        """
Get current user satisfaction score."""
        if not self.business_metrics:
            return 0.8
        
        return self.business_metrics.get('user_satisfaction', 0.8)
    
    async def _generate_adaptation_options(self, current_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
Generate adaptation options based on current state."""
        options = []
        
        # Performance-based adaptations
        if current_state['performance_trend'] == 'degrading':
            options.extend([
                {
                    'type': 'increase_resources',
                    'objective': OptimizationObjective.MINIMIZE_LATENCY,
                    'confidence': 0.7,
                    'expected_improvement': 0.15,
                    'implementation': {'action': 'scale_up', 'factor': 1.5}
                },
                {
                    'type': 'optimize_scheduling',
                    'objective': OptimizationObjective.MAXIMIZE_THROUGHPUT,
                    'confidence': 0.6,
                    'expected_improvement': 0.1,
                    'implementation': {'action': 'adjust_priority', 'strategy': 'performance_based'}
                }
            ])
        
        # Resource-based adaptations
        resource_util = current_state['resource_utilization']
        if max(resource_util.values()) > 0.8:
            options.append({
                'type': 'resource_optimization',
                'objective': OptimizationObjective.OPTIMIZE_RESOURCES,
                'confidence': 0.8,
                'expected_improvement': 0.2,
                'implementation': {'action': 'redistribute_load', 'target_utilization': 0.7}
            })
        
        # Business-based adaptations
        if current_state.get('user_satisfaction', 0.8) < 0.7:
            options.append({
                'type': 'user_experience_optimization',
                'objective': OptimizationObjective.ENHANCE_USER_EXPERIENCE,
                'confidence': 0.9,
                'expected_improvement': 0.25,
                'implementation': {'action': 'prioritize_user_tasks', 'weight': 1.5}
            })
        
        # Learning-based adaptations
        if self.learning_state.model_confidence < 0.5:
            options.append({
                'type': 'increase_exploration',
                'objective': OptimizationObjective.IMPROVE_ACCURACY,
                'confidence': 0.5,
                'expected_improvement': 0.1,
                'implementation': {'action': 'increase_exploration_rate', 'rate': 0.5}
            })
        
        return options
    
    async def _select_best_adaptation(self, options: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
Select best adaptation option."""
        if not options:
            return None
        
        # Score options based on multiple criteria
        scored_options = []
        
        for option in options:
            score = 0.0
            
            # Confidence weight
            score += option['confidence'] * 0.4
            
            # Expected improvement weight
            score += option['expected_improvement'] * 0.3
            
            # Strategy alignment weight
            if self._aligns_with_strategy(option):
                score += 0.2
            
            # Business impact weight
            if option['objective'] in [
                OptimizationObjective.ENHANCE_USER_EXPERIENCE,
                OptimizationObjective.INCREASE_REVENUE
            ]:
                score += 0.1
            
            scored_options.append((score, option))
        
        # Select highest scoring option
        best_option = max(scored_options, key=lambda x: x[0])[1]
        
        # Check minimum confidence threshold
        if best_option['confidence'] < self.config['adaptation_confidence_threshold']:
            return None
        
        return best_option
    
    def _aligns_with_strategy(self, option: Dict[str, Any]) -> bool:
        """
Check if option aligns with current adaptation strategy."""
        if self.adaptation_strategy == AdaptationStrategy.PERFORMANCE_BASED:
            return option['objective'] in [
                OptimizationObjective.MINIMIZE_LATENCY,
                OptimizationObjective.MAXIMIZE_THROUGHPUT
            ]
        elif self.adaptation_strategy == AdaptationStrategy.BUSINESS_IMPACT:
            return option['objective'] in [
                OptimizationObjective.ENHANCE_USER_EXPERIENCE,
                OptimizationObjective.INCREASE_REVENUE
            ]
        else:
            return True  # Hybrid strategy accepts all
    
    async def _implement_adaptation(self, decision: AdaptationDecision) -> None:
        """
Implement adaptation decision."""
        try:
            implementation = decision.decision_data.get('implementation', {})
            action = implementation.get('action')
            
            if action == 'scale_up':
                await self._scale_up_resources(implementation.get('factor', 1.5))
            elif action == 'adjust_priority':
                await self._adjust_priority_strategy(implementation.get('strategy'))
            elif action == 'redistribute_load':
                await self._redistribute_load(implementation.get('target_utilization', 0.7))
            elif action == 'prioritize_user_tasks':
                await self._prioritize_user_tasks(implementation.get('weight', 1.5))
            elif action == 'increase_exploration_rate':
                await self._increase_exploration_rate(implementation.get('rate', 0.5))
            
            # Mark as implemented
            decision.implemented_at = datetime.utcnow()
            
            # Update learning state
            self.learning_state.adaptation_count += 1
            self.learning_state.last_adaptation = datetime.utcnow()
            
            # Store decision
            self.adaptation_history.append(decision)
            
            # Call adaptation callbacks
            await self._call_callbacks('adaptation_implemented', decision)
            
            logger.info(f"Adaptation implemented: {decision.decision_id}")
            
        except Exception as e:
            logger.error(f"Adaptation implementation failed: {e}")
            decision.result = {'success': False, 'error': str(e)}
    
    async def _scale_up_resources(self, factor: float) -> None:
        """Scale up resources by given factor."""
        # This would integrate with the resource scheduler
        logger.info(f"Scaling up resources by factor {factor}")
    
    async def _adjust_priority_strategy(self, strategy: str) -> None:
        """Adjust priority scheduling strategy."""
        # This would integrate with the priority scheduler
        logger.info(f"Adjusting priority strategy to {strategy}")
    
    async def _redistribute_load(self, target_utilization: float) -> None:
        """Redistribute load to achieve target utilization."""
        # This would integrate with the load balancer
        logger.info(f"Redistributing load to achieve {target_utilization:.1%} utilization")
    
    async def _prioritize_user_tasks(self, weight: float) -> None:
        """Increase priority weight for user tasks."""
        # This would integrate with the task prioritization system
        logger.info(f"Increasing user task priority weight to {weight}")
    
    async def _increase_exploration_rate(self, rate: float) -> None:
        """Increase exploration rate for learning."""
        self.learning_state.exploration_rate = min(1.0, rate)
        self.learning_state.exploitation_rate = 1.0 - self.learning_state.exploration_rate
        logger.info(f"Increased exploration rate to {rate:.1%}")
    
    async def _update_reinforcement_learning(self, performance_data: Dict[str, Any]) -> None:
        """Update reinforcement learning agent."""
        if not self.enable_reinforcement_learning or not self.reinforcement_agent:
            return
        
        try:
            # Calculate reward based on performance
            reward = self._calculate_reward(performance_data)
            
            # Update Q-values if we have previous state-action
            if (self.reinforcement_state.last_state is not None and 
                self.reinforcement_state.last_action is not None):
                
                self._update_q_values(
                    self.reinforcement_state.last_state,
                    self.reinforcement_state.last_action,
                    reward,
                    self.reinforcement_state.state_vector
                )
            
            # Store current state and reward
            self.reinforcement_state.last_state = self.reinforcement_state.state_vector.copy()
            self.reinforcement_state.last_reward = reward
            self.reinforcement_state.reward_history.append(reward)
            
            # Update state vector with current performance
            self.reinforcement_state.state_vector = await self._extract_rl_state(performance_data)
            
        except Exception as e:
            logger.error(f"Reinforcement learning update failed: {e}")
    
    def _calculate_reward(self, performance_data: Dict[str, Any]) -> float:
        """Calculate reward for reinforcement learning."""
        # Multi-objective reward function
        performance_score = self._calculate_performance_score(performance_data) or 0.5
        
        # Business impact component
        business_ctx = performance_data.get('business_context', {})
        business_reward = business_ctx.get('revenue_impact', 0.5) * 0.3
        
        # User satisfaction component
        user_reward = business_ctx.get('user_satisfaction', 0.5) * 0.2
        
        # Efficiency component
        efficiency = 1.0 - performance_data.get('resource_usage', 0.5)
        efficiency_reward = efficiency * 0.2
        
        # Combine rewards
        total_reward = (
            performance_score * 0.3 +
            business_reward +
            user_reward +
            efficiency_reward
        )
        
        return min(1.0, max(-1.0, total_reward))
    
    def _update_q_values(self, state: List[float], action: str, reward: float, next_state: List[float]) -> None:
        """
Update Q-values using Q-learning algorithm."""
        # Convert state to hashable representation
        state_key = tuple(round(x, 2) for x in state)
        next_state_key = tuple(round(x, 2) for x in next_state)
        
        # Current Q-value
        current_q = self.reinforcement_state.q_values.get((state_key, action), 0.0)
        
        # Best next action value
        next_q_values = [
            self.reinforcement_state.q_values.get((next_state_key, a), 0.0)
            for a in self.reinforcement_state.action_space
        ]
        max_next_q = max(next_q_values) if next_q_values else 0.0
        
        # Q-learning update
        alpha = self.reinforcement_state.alpha
        gamma = self.reinforcement_state.gamma
        
        new_q = current_q + alpha * (reward + gamma * max_next_q - current_q)
        self.reinforcement_state.q_values[(state_key, action)] = new_q
    
    async def _extract_rl_state(self, performance_data: Dict[str, Any]) -> List[float]:
        """
Extract state vector for reinforcement learning."""
        state = []
        
        # Performance metrics
        state.append(performance_data.get('execution_time', 60) / 300)  # Normalized
        state.append(performance_data.get('success_rate', 0.9))
        state.append(performance_data.get('resource_usage', 0.5))
        state.append(performance_data.get('error_rate', 0.1))
        
        # System state
        state.append(len(self.performance_history) / self.learning_history_size)
        state.append(self.learning_state.model_confidence)
        state.append(self.learning_state.success_rate)
        
        # Business context
        business_ctx = performance_data.get('business_context', {})
        state.append(business_ctx.get('priority', 0.5))
        state.append(business_ctx.get('business_impact', 0.5))
        state.append(business_ctx.get('user_satisfaction', 0.8))
        
        return state
    
    async def _detect_performance_patterns(self) -> None:
        """
Detect patterns in performance data."""
        if not self.enable_pattern_recognition or len(self.performance_history) < 50:
            return
        
        try:
            # Analyze recent performance data
            recent_data = list(self.performance_history)[-200:]
            
            # Extract temporal patterns
            temporal_patterns = await self._detect_temporal_patterns(recent_data)
            
            # Extract performance patterns
            performance_patterns = await self._detect_performance_patterns_ml(recent_data)
            
            # Store discovered patterns
            for pattern in temporal_patterns + performance_patterns:
                if pattern.confidence > self.config['pattern_discovery_threshold']:
                    self.discovered_patterns[pattern.pattern_id] = pattern
                    self.pattern_history.append(pattern)
            
        except Exception as e:
            logger.error(f"Pattern detection failed: {e}")
    
    async def _detect_temporal_patterns(self, data: List[Dict[str, Any]]) -> List[PerformancePattern]:
        """Detect temporal patterns in performance."""
        patterns = []
        
        # Group by hour of day
        hourly_performance = defaultdict(list)
        for item in data:
            timestamp = item.get('timestamp', datetime.utcnow())
            hour = timestamp.hour
            score = self._calculate_performance_score(item)
            if score is not None:
                hourly_performance[hour].append(score)
        
        # Analyze hourly patterns
        for hour, scores in hourly_performance.items():
            if len(scores) >= 5:
                avg_score = np.mean(scores)
                std_score = np.std(scores)
                
                # Detect peak hours
                if avg_score > 0.8 and std_score < 0.1:
                    pattern = PerformancePattern(
                        pattern_id=f"peak_hour_{hour}",
                        pattern_type="temporal_peak",
                        frequency=len(scores) / len(data),
                        confidence=min(1.0, avg_score + (1.0 - std_score)),
                        impact_score=avg_score,
                        discovered_at=datetime.utcnow(),
                        last_seen=datetime.utcnow(),
                        pattern_data={'hour': hour, 'performance': avg_score},
                        recommendations=[f"Schedule important tasks at {hour}:00"]
                    )
                    patterns.append(pattern)
        
        return patterns
    
    async def _detect_performance_patterns_ml(self, data: List[Dict[str, Any]]) -> List[PerformancePattern]:
        """Detect patterns using machine learning."""
        patterns = []
        
        try:
            # Prepare feature matrix
            features = []
            for item in data:
                feature_vector = await self._extract_features(item)
                if feature_vector:
                    features.append(feature_vector)
            
            if len(features) < 10:
                return patterns
            
            # Use clustering to find patterns
            if self.pattern_clusters:
                clusters = self.pattern_clusters.fit_predict(features)
                
                # Analyze each cluster
                for cluster_id in set(clusters):
                    cluster_indices = [i for i, c in enumerate(clusters) if c == cluster_id]
                    
                    if len(cluster_indices) >= 5:  # Minimum cluster size
                        cluster_data = [data[i] for i in cluster_indices]
                        cluster_performance = [
                            self._calculate_performance_score(item)
                            for item in cluster_data
                            if self._calculate_performance_score(item) is not None
                        ]
                        
                        if cluster_performance:
                            avg_performance = np.mean(cluster_performance)
                            
                            pattern = PerformancePattern(
                                pattern_id=f"cluster_{cluster_id}_{int(time.time())}",
                                pattern_type="performance_cluster",
                                frequency=len(cluster_indices) / len(data),
                                confidence=min(1.0, len(cluster_indices) / 20),
                                impact_score=avg_performance,
                                discovered_at=datetime.utcnow(),
                                last_seen=datetime.utcnow(),
                                pattern_data={
                                    'cluster_id': cluster_id,
                                    'size': len(cluster_indices),
                                    'performance': avg_performance
                                }
                            )
                            patterns.append(pattern)
        
        except Exception as e:
            logger.error(f"ML pattern detection failed: {e}")
        
        return patterns
    
    def _update_business_metrics(self, business_context: Dict[str, Any]) -> None:
        """Update business metrics from context data."""
        for key, value in business_context.items():
            if isinstance(value, (int, float)):
                # Use exponential moving average
                alpha = 0.1
                current_value = self.business_metrics.get(key, value)
                self.business_metrics[key] = alpha * value + (1 - alpha) * current_value
    
    async def _save_models(self) -> None:
        """
Save ML models to storage."""
        try:
            storage_path = self.config['model_storage_path']
            
            # Save sklearn models
            if self.performance_predictor:
                joblib.dump(self.performance_predictor, f"{storage_path}/performance_predictor.joblib")
            
            if self.pattern_classifier:
                joblib.dump(self.pattern_classifier, f"{storage_path}/pattern_classifier.joblib")
            
            if self.pattern_clusters:
                joblib.dump(self.pattern_clusters, f"{storage_path}/pattern_clusters.joblib")
            
            # Save deep learning model
            if self.enable_deep_learning and self.deep_learning_model:
                self.deep_learning_model.save(f"{storage_path}/deep_learning_model.h5")
            
            # Save reinforcement learning data
            if self.enable_reinforcement_learning and self.reinforcement_agent:
                with open(f"{storage_path}/reinforcement_agent.json", 'w') as f:
                    json.dump({
                        'q_values': {str(k): v for k, v in self.reinforcement_state.q_values.items()},
                        'total_episodes': self.reinforcement_agent['total_episodes'],
                        'total_reward': self.reinforcement_agent['total_reward']
                    }, f)
            
            # Save learning state
            with open(f"{storage_path}/learning_state.json", 'w') as f:
                json.dump(asdict(self.learning_state), f, default=str)
            
            logger.info("Adaptive scheduler models saved")
            
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
    
    async def _load_models(self) -> None:
        """Load existing ML models."""
        try:
            storage_path = self.config['model_storage_path']
            
            # Load sklearn models
            try:
                self.performance_predictor = joblib.load(f"{storage_path}/performance_predictor.joblib")
                logger.info("Loaded performance predictor model")
            except FileNotFoundError:
                pass
            
            try:
                self.pattern_classifier = joblib.load(f"{storage_path}/pattern_classifier.joblib")
                logger.info("Loaded pattern classifier model")
            except FileNotFoundError:
                pass
            
            try:
                self.pattern_clusters = joblib.load(f"{storage_path}/pattern_clusters.joblib")
                logger.info("Loaded pattern clusters model")
            except FileNotFoundError:
                pass
            
            # Load deep learning model
            try:
                if self.enable_deep_learning:
                    self.deep_learning_model = keras.models.load_model(f"{storage_path}/deep_learning_model.h5")
                    logger.info("Loaded deep learning model")
            except FileNotFoundError:
                pass
            
            # Load reinforcement learning data
            try:
                with open(f"{storage_path}/reinforcement_agent.json", 'r') as f:
                    rl_data = json.load(f)
                    
                    # Convert string keys back to tuples
                    q_values = {}
                    for k, v in rl_data.get('q_values', {}).items():
                        try:
                            key = eval(k)  # Convert string back to tuple
                            q_values[key] = v
                        except:
                            pass
                    
                    self.reinforcement_state.q_values = q_values
                    self.reinforcement_agent['total_episodes'] = rl_data.get('total_episodes', 0)
                    self.reinforcement_agent['total_reward'] = rl_data.get('total_reward', 0.0)
                    
                logger.info("Loaded reinforcement learning data")
            except FileNotFoundError:
                pass
            
            # Load learning state
            try:
                with open(f"{storage_path}/learning_state.json", 'r') as f:
                    state_data = json.load(f)
                    
                    # Update learning state
                    for key, value in state_data.items():
                        if hasattr(self.learning_state, key):
                            setattr(self.learning_state, key, value)
                    
                logger.info("Loaded learning state")
            except FileNotFoundError:
                pass
                
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
    
    async def get_adaptation_status(self) -> Dict[str, Any]:
        """Get comprehensive adaptation status."""
        return {
            'learning_enabled': self.is_learning,
            'adaptation_strategy': self.adaptation_strategy.value,
            'learning_mode': self.learning_mode.value,
            'learning_state': asdict(self.learning_state),
            'reinforcement_learning_enabled': self.enable_reinforcement_learning,
            'pattern_recognition_enabled': self.enable_pattern_recognition,
            'deep_learning_enabled': self.enable_deep_learning,
            'performance_history_size': len(self.performance_history),
            'discovered_patterns': len(self.discovered_patterns),
            'adaptation_history_size': len(self.adaptation_history),
            'recent_adaptations': [
                {
                    'decision_id': decision.decision_id,
                    'strategy': decision.strategy.value,
                    'objective': decision.objective.value,
                    'confidence': decision.confidence,
                    'implemented': decision.implemented_at is not None
                }
                for decision in list(self.adaptation_history)[-5:]
            ],
            'business_metrics': self.business_metrics,
            'current_performance': await self._evaluate_current_performance(),
            'model_confidence': self.learning_state.model_confidence,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def add_callback(self, event_type: str, callback: Callable) -> None:
        """
Add event callback."""
        self.event_callbacks[event_type].append(callback)
    
    async def _call_callbacks(self, event_type: str, *args) -> None:
        """
Call registered callbacks for an event."""
        for callback in self.event_callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args)
                else:
                    callback(*args)
            except Exception as e:
                logger.error(f"Callback error for {event_type}: {e}")


# Export main classes
__all__ = [
    'AdaptiveScheduler',
    'AdaptationStrategy',
    'LearningMode',
    'OptimizationObjective',
    'PerformancePattern',
    'AdaptationDecision',
    'LearningState',
    'ReinforcementState'
]
