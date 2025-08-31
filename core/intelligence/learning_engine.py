"""Learning Engine - Adaptive Intelligence for Content Optimization

Implements sophisticated machine learning algorithms for continuous learning,
model adaptation, and intelligent content optimization. Provides adaptive
algorithms that learn from user behavior, content performance, and market trends.

Features:
- Online learning algorithms
- Reinforcement learning for content strategy
- Transfer learning capabilities
- Meta-learning and few-shot learning
- Adaptive model selection
- Continuous optimization

Author: Fahed Mlaiel <mlaiel@live.de>
"""import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass
from enum import Enum
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from collections import deque, defaultdict

# Machine Learning
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import SGDRegressor, PassiveAggressiveRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler
import joblib

# Advanced ML
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# Reinforcement Learning
import gym
from stable_baselines3 import PPO, A2C, DQN
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.vec_env import DummyVecEnv

# Optimization
from scipy.optimize import minimize, differential_evolution
from hyperopt import fmin, tpe, hp, Trials

# Core Dependencies
from ..adapters.learning_adapter import LearningAdapter
from ..engines.optimization_engine import OptimizationEngine
from ..processors.model_processor import ModelProcessor
from ..storage.learning_storage import LearningStorage


class LearningType(Enum):
    """Learning algorithm types"""    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    SEMI_SUPERVISED = "semi_supervised"
    TRANSFER = "transfer"
    META = "meta"
    ONLINE = "online"
    FEDERATED = "federated"


class OptimizationObjective(Enum):
    """Optimization objectives"""    ENGAGEMENT = "engagement"
    REVENUE = "revenue"
    REACH = "reach"
    QUALITY = "quality"
    EFFICIENCY = "efficiency"
    MULTI_OBJECTIVE = "multi_objective"


@dataclass
class LearningConfig:
    """Learning algorithm configuration"""    learning_type: LearningType
    algorithm: str
    hyperparameters: Dict[str, Any]
    optimization_objective: OptimizationObjective
    update_frequency: str
    memory_size: int
    exploration_rate: float
    learning_rate: float


@dataclass
class LearningResult:
    """Learning process result"""    algorithm_id: str
    performance_score: float
    improvement_rate: float
    convergence_time: float
    model_parameters: Dict[str, Any]
    confidence_score: float
    metadata: Dict[str, Any]


class OnlineLearner:
    """Online learning algorithm for continuous adaptation"""    
    def __init__(self, input_dim: int, output_dim: int, learning_rate: float = 0.01):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.learning_rate = learning_rate
        
        # Initialize model
        self.model = SGDRegressor(
            learning_rate='adaptive',
            eta0=learning_rate,
            random_state=42
        )
        
        # Memory for recent samples
        self.memory_size = 1000
        self.memory_x = deque(maxlen=self.memory_size)
        self.memory_y = deque(maxlen=self.memory_size)
        
        # Performance tracking
        self.performance_history = []
        self.is_fitted = False
        
    def update(self, x: np.ndarray, y: np.ndarray) -> float:
        """Update model with new data"""        try:
            # Add to memory
            self.memory_x.append(x)
            self.memory_y.append(y)
            
            if not self.is_fitted and len(self.memory_x) >= 10:
                # Initial fitting
                X_init = np.array(list(self.memory_x))
                y_init = np.array(list(self.memory_y))
                self.model.fit(X_init, y_init)
                self.is_fitted = True
            
            elif self.is_fitted:
                # Online update
                self.model.partial_fit(x.reshape(1, -1), [y])
            
            # Calculate performance on recent data
            if len(self.memory_x) >= 5:
                recent_x = np.array(list(self.memory_x)[-5:])
                recent_y = np.array(list(self.memory_y)[-5:])
                predictions = self.model.predict(recent_x)
                performance = r2_score(recent_y, predictions)
                self.performance_history.append(performance)
                return performance
            
            return 0.0
            
        except Exception as e:
            logging.error(f"Online learning update failed: {e}")
            return 0.0
    
    def predict(self, x: np.ndarray) -> np.ndarray:
        """Make prediction"""        if self.is_fitted:
            return self.model.predict(x.reshape(1, -1) if x.ndim == 1 else x)
        else:
            return np.zeros(self.output_dim)
    
    def get_performance(self) -> float:
        """Get recent performance score"""        if self.performance_history:
            return np.mean(self.performance_history[-10:])
        return 0.0


class ReinforcementLearner:
    """Reinforcement learning for content strategy optimization"""    
    def __init__(self, state_dim: int, action_dim: int, algorithm: str = "ppo"):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.algorithm = algorithm
        
        # Create environment
        self.env = self._create_environment()
        
        # Initialize RL agent
        if algorithm.lower() == "ppo":
            self.agent = PPO("MlpPolicy", self.env, verbose=0)
        elif algorithm.lower() == "a2c":
            self.agent = A2C("MlpPolicy", self.env, verbose=0)
        elif algorithm.lower() == "dqn":
            self.agent = DQN("MlpPolicy", self.env, verbose=0)
        else:
            self.agent = PPO("MlpPolicy", self.env, verbose=0)
        
        # Learning tracking
        self.episode_rewards = []
        self.training_steps = 0
        
    def _create_environment(self):
        """Create custom environment for content optimization"""        # This would be a custom gym environment
        # For now, use a simple mock environment
        return gym.make('CartPole-v1')  # Placeholder
    
    def train(self, total_timesteps: int = 10000) -> float:
        """Train the RL agent"""        try:
            self.agent.learn(total_timesteps=total_timesteps)
            self.training_steps += total_timesteps
            
            # Evaluate performance
            obs = self.env.reset()
            total_reward = 0
            done = False
            
            while not done:
                action, _ = self.agent.predict(obs, deterministic=True)
                obs, reward, done, _ = self.env.step(action)
                total_reward += reward
            
            self.episode_rewards.append(total_reward)
            return total_reward
            
        except Exception as e:
            logging.error(f"RL training failed: {e}")
            return 0.0
    
    def get_action(self, state: np.ndarray) -> np.ndarray:
        """Get action for given state"""        try:
            action, _ = self.agent.predict(state, deterministic=True)
            return action
        except Exception as e:
            logging.error(f"RL action prediction failed: {e}")
            return np.random.rand(self.action_dim)
    
    def update_reward(self, state: np.ndarray, action: np.ndarray, reward: float) -> None:
        """Update with reward feedback"""        # This would update the agent with new experience
        # Implementation depends on the specific RL algorithm
        pass


class MetaLearner:
    """Meta-learning for few-shot adaptation"""    
    def __init__(self, input_dim: int, output_dim: int, meta_lr: float = 0.001):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.meta_lr = meta_lr
        
        # Meta-model (MAML-inspired)
        self.meta_model = self._create_meta_model()
        self.optimizer = optim.Adam(self.meta_model.parameters(), lr=meta_lr)
        
        # Task memory
        self.task_memory = {}
        self.adaptation_history = []
        
    def _create_meta_model(self) -> nn.Module:
        """Create meta-learning model"""        return nn.Sequential(
            nn.Linear(self.input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, self.output_dim)
        )
    
    def meta_train(self, tasks: List[Dict[str, np.ndarray]], steps: int = 100) -> float:
        """Meta-training on multiple tasks"""        total_loss = 0.0
        
        for step in range(steps):
            # Sample batch of tasks
            batch_tasks = np.random.choice(tasks, size=min(4, len(tasks)), replace=False)
            
            meta_loss = 0.0
            
            for task in batch_tasks:
                # Fast adaptation on support set
                support_x = torch.FloatTensor(task['support_x'])
                support_y = torch.FloatTensor(task['support_y'])
                
                # Clone model for fast adaptation
                fast_model = type(self.meta_model)(self.input_dim, self.output_dim)
                fast_model.load_state_dict(self.meta_model.state_dict())
                fast_optimizer = optim.SGD(fast_model.parameters(), lr=0.01)
                
                # Fast adaptation steps
                for _ in range(5):
                    pred = fast_model(support_x)
                    loss = nn.MSELoss()(pred, support_y)
                    fast_optimizer.zero_grad()
                    loss.backward()
                    fast_optimizer.step()
                
                # Evaluate on query set
                query_x = torch.FloatTensor(task['query_x'])
                query_y = torch.FloatTensor(task['query_y'])
                
                query_pred = fast_model(query_x)
                meta_loss += nn.MSELoss()(query_pred, query_y)
            
            # Meta-update
            self.optimizer.zero_grad()
            meta_loss.backward()
            self.optimizer.step()
            
            total_loss += meta_loss.item()
        
        avg_loss = total_loss / steps
        return avg_loss
    
    def adapt_to_task(
        self,
        task_data: Dict[str, np.ndarray],
        adaptation_steps: int = 10
    ) -> float:
        """Quickly adapt to new task"""        try:
            # Clone meta-model
            adapted_model = type(self.meta_model)(self.input_dim, self.output_dim)
            adapted_model.load_state_dict(self.meta_model.state_dict())
            
            # Fast adaptation
            optimizer = optim.SGD(adapted_model.parameters(), lr=0.01)
            
            x = torch.FloatTensor(task_data['x'])
            y = torch.FloatTensor(task_data['y'])
            
            for step in range(adaptation_steps):
                pred = adapted_model(x)
                loss = nn.MSELoss()(pred, y)
                
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            
            # Store adapted model
            task_id = f"task_{len(self.task_memory)}"
            self.task_memory[task_id] = adapted_model.state_dict()
            
            # Track adaptation performance
            final_loss = loss.item()
            self.adaptation_history.append(final_loss)
            
            return final_loss
            
        except Exception as e:
            logging.error(f"Meta-learning adaptation failed: {e}")
            return float('inf')


class AdaptiveModelSelector:
    """Adaptive model selection and ensemble"""    
    def __init__(self, models: List[Any], selection_strategy: str = "performance"):
        self.models = models
        self.selection_strategy = selection_strategy
        
        # Performance tracking
        self.model_performances = defaultdict(list)
        self.model_weights = np.ones(len(models)) / len(models)
        
        # Selection parameters
        self.window_size = 100
        self.exploration_rate = 0.1
        
    def select_model(self, context: Optional[Dict[str, Any]] = None) -> int:
        """Select best model based on strategy"""        if self.selection_strategy == "performance":
            return self._select_by_performance()
        elif self.selection_strategy == "context":
            return self._select_by_context(context)
        elif self.selection_strategy == "ensemble":
            return -1  # Use ensemble
        else:
            return np.random.choice(len(self.models))
    
    def _select_by_performance(self) -> int:
        """Select model based on recent performance"""        if np.random.random() < self.exploration_rate:
            # Exploration: random selection
            return np.random.choice(len(self.models))
        
        # Exploitation: select best performing model
        recent_performances = []
        for i in range(len(self.models)):
            if self.model_performances[i]:
                recent_perf = np.mean(self.model_performances[i][-self.window_size:])
                recent_performances.append(recent_perf)
            else:
                recent_performances.append(0.0)
        
        return np.argmax(recent_performances)
    
    def _select_by_context(self, context: Dict[str, Any]) -> int:
        """Select model based on context"""        # Context-based selection (simplified)
        if context and 'content_type' in context:
            content_type = context['content_type']
            if content_type == 'audio':
                return 0  # Assume first model is best for audio
            elif content_type == 'video':
                return 1  # Assume second model is best for video
            else:
                return self._select_by_performance()
        else:
            return self._select_by_performance()
    
    def update_performance(self, model_id: int, performance: float) -> None:
        """Update model performance"""        self.model_performances[model_id].append(performance)
        
        # Update ensemble weights
        self._update_weights()
    
    def _update_weights(self) -> None:
        """Update ensemble weights based on performance"""        performances = []
        for i in range(len(self.models)):
            if self.model_performances[i]:
                avg_perf = np.mean(self.model_performances[i][-self.window_size:])
                performances.append(max(avg_perf, 0.01))  # Avoid zero weights
            else:
                performances.append(0.01)
        
        # Softmax normalization
        performances = np.array(performances)
        exp_performances = np.exp(performances - np.max(performances))
        self.model_weights = exp_performances / np.sum(exp_performances)
    
    def predict_ensemble(self, x: np.ndarray) -> np.ndarray:
        """Make ensemble prediction"""        predictions = []
        
        for model in self.models:
            try:
                pred = model.predict(x.reshape(1, -1) if x.ndim == 1 else x)
                predictions.append(pred)
            except:
                predictions.append(np.zeros(1))  # Fallback
        
        # Weighted ensemble
        ensemble_pred = np.zeros_like(predictions[0])
        for i, pred in enumerate(predictions):
            ensemble_pred += self.model_weights[i] * pred
        
        return ensemble_pred


class LearningEngine:
    """    Adaptive learning engine for content intelligence optimization
    """    
    def __init__(self, config: Dict[str, Any]):
        """        Initialize learning engine
        
        Args:
            config: Configuration dictionary
        """        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._initialize_learners()
        self._initialize_optimizers()
        self._initialize_storage()
        
        # Learning tracking
        self.learning_history = {}
        self.active_experiments = {}
        self.performance_metrics = {
            "total_learning_sessions": 0,
            "average_improvement_rate": 0.0,
            "active_learners": 0,
            "best_performance": 0.0,
            "convergence_rate": 0.0
        }
        
        # Adaptive parameters
        self.adaptation_frequency = config.get("adaptation_frequency", "hourly")
        self.exploration_rate = config.get("exploration_rate", 0.1)
        self.memory_retention = config.get("memory_retention", 0.95)
    
    def _initialize_learners(self) -> None:
        """Initialize learning algorithms"""        try:
            # Online learners
            self.online_learner = OnlineLearner(
                input_dim=self.config.get("input_dim", 100),
                output_dim=self.config.get("output_dim", 1),
                learning_rate=self.config.get("learning_rate", 0.01)
            )
            
            # Reinforcement learner
            self.rl_learner = ReinforcementLearner(
                state_dim=self.config.get("state_dim", 50),
                action_dim=self.config.get("action_dim", 10),
                algorithm=self.config.get("rl_algorithm", "ppo")
            )
            
            # Meta learner
            self.meta_learner = MetaLearner(
                input_dim=self.config.get("input_dim", 100),
                output_dim=self.config.get("output_dim", 1),
                meta_lr=self.config.get("meta_lr", 0.001)
            )
            
            # Traditional models for ensemble
            traditional_models = [
                RandomForestRegressor(n_estimators=100, random_state=42),
                GradientBoostingRegressor(n_estimators=100, random_state=42),
                MLPRegressor(hidden_layer_sizes=(100, 50), random_state=42)
            ]
            
            # Adaptive model selector
            self.model_selector = AdaptiveModelSelector(
                models=traditional_models,
                selection_strategy=self.config.get("selection_strategy", "performance")
            )
            
            self.logger.info("Learning algorithms initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize learners: {e}")
            raise
    
    def _initialize_optimizers(self) -> None:
        """Initialize optimization engines"""        self.learning_adapter = LearningAdapter(self.config)
        self.optimization_engine = OptimizationEngine(self.config)
        self.model_processor = ModelProcessor(self.config)
    
    def _initialize_storage(self) -> None:
        """Initialize learning storage"""        self.learning_storage = LearningStorage(self.config)
    
    async def learn_from_feedback(
        self,
        content_features: np.ndarray,
        performance_feedback: Dict[str, float],
        learning_type: LearningType = LearningType.ONLINE
    ) -> LearningResult:
        """        Learn from performance feedback
        
        Args:
            content_features: Content feature vector
            performance_feedback: Performance metrics (engagement, revenue, etc.)
            learning_type: Type of learning to apply
            
        Returns:
            LearningResult: Learning outcome and metrics
        """        start_time = datetime.now()
        
        try:
            # Prepare target value from feedback
            target = self._aggregate_feedback(performance_feedback)
            
            # Apply appropriate learning algorithm
            if learning_type == LearningType.ONLINE:
                performance = self.online_learner.update(content_features, target)
                algorithm_id = "online_sgd"
                
            elif learning_type == LearningType.REINFORCEMENT:
                # Convert feedback to reward signal
                reward = self._feedback_to_reward(performance_feedback)
                action = self.rl_learner.get_action(content_features)
                self.rl_learner.update_reward(content_features, action, reward)
                performance = reward
                algorithm_id = f"rl_{self.rl_learner.algorithm}"
                
            elif learning_type == LearningType.META:
                # Create task from current data
                task_data = {
                    'x': content_features,
                    'y': target
                }
                performance = 1.0 / (1.0 + self.meta_learner.adapt_to_task(task_data))
                algorithm_id = "meta_maml"
                
            else:
                # Use adaptive model selector
                model_id = self.model_selector.select_model()
                if model_id >= 0:
                    model = self.model_selector.models[model_id]
                    
                    # Fit model if not already fitted
                    if not hasattr(model, 'fitted_') or not model.fitted_:
                        model.fit(content_features.reshape(1, -1), [target])
                        model.fitted_ = True
                    
                    # Make prediction and calculate performance
                    prediction = model.predict(content_features.reshape(1, -1))
                    performance = 1.0 / (1.0 + abs(prediction[0] - target))
                    
                    # Update model selector
                    self.model_selector.update_performance(model_id, performance)
                    
                    algorithm_id = f"adaptive_{model_id}"
                else:
                    # Ensemble prediction
                    prediction = self.model_selector.predict_ensemble(content_features)
                    performance = 1.0 / (1.0 + abs(prediction[0] - target))
                    algorithm_id = "ensemble"
            
            # Calculate improvement rate
            improvement_rate = self._calculate_improvement_rate(algorithm_id, performance)
            
            # Calculate convergence time
            convergence_time = (datetime.now() - start_time).total_seconds()
            
            # Create learning result
            result = LearningResult(
                algorithm_id=algorithm_id,
                performance_score=performance,
                improvement_rate=improvement_rate,
                convergence_time=convergence_time,
                model_parameters=self._get_model_parameters(algorithm_id),
                confidence_score=self._calculate_confidence(performance, algorithm_id),
                metadata={
                    'learning_type': learning_type.value,
                    'feedback_keys': list(performance_feedback.keys()),
                    'target_value': target,
                    'feature_dimension': len(content_features)
                }
            )
            
            # Store learning history
            self.learning_history[algorithm_id] = result
            
            # Update performance metrics
            self._update_learning_metrics(result)
            
            self.logger.info(f"Learning completed with {algorithm_id}: performance={performance:.4f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Learning from feedback failed: {e}")
            raise
    
    def _aggregate_feedback(self, feedback: Dict[str, float]) -> float:
        """Aggregate multiple feedback metrics into single target"""        weights = {
            'engagement': 0.3,
            'revenue': 0.4,
            'quality': 0.2,
            'reach': 0.1
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric, value in feedback.items():
            weight = weights.get(metric, 0.1)
            total_score += weight * value
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.5
    
    def _feedback_to_reward(self, feedback: Dict[str, float]) -> float:
        """Convert feedback to reward signal for RL"""        # Normalize feedback values to [0, 1] and aggregate
        normalized_feedback = {}
        for key, value in feedback.items():
            normalized_feedback[key] = max(0.0, min(1.0, value))
        
        return self._aggregate_feedback(normalized_feedback)
    
    def _calculate_improvement_rate(self, algorithm_id: str, current_performance: float) -> float:
        """Calculate improvement rate compared to previous performance"""        if algorithm_id in self.learning_history:
            previous_performance = self.learning_history[algorithm_id].performance_score
            if previous_performance > 0:
                return (current_performance - previous_performance) / previous_performance
        
        return 0.0
    
    def _get_model_parameters(self, algorithm_id: str) -> Dict[str, Any]:
        """Get model parameters for given algorithm"""        try:
            if algorithm_id == "online_sgd":
                if hasattr(self.online_learner.model, 'coef_'):
                    return {
                        'coefficients': self.online_learner.model.coef_.tolist(),
                        'intercept': float(self.online_learner.model.intercept_),
                        'learning_rate': self.online_learner.learning_rate
                    }
            
            elif algorithm_id.startswith("rl_"):
                return {
                    'training_steps': self.rl_learner.training_steps,
                    'episode_rewards': self.rl_learner.episode_rewards[-10:],
                    'algorithm': self.rl_learner.algorithm
                }
            
            elif algorithm_id == "meta_maml":
                return {
                    'meta_lr': self.meta_learner.meta_lr,
                    'adaptation_history': self.meta_learner.adaptation_history[-10:],
                    'tasks_learned': len(self.meta_learner.task_memory)
                }
            
            return {}
            
        except Exception:
            return {}
    
    def _calculate_confidence(self, performance: float, algorithm_id: str) -> float:
        """Calculate confidence score for learning result"""        # Base confidence from performance
        base_confidence = min(performance, 1.0)
        
        # Adjust based on algorithm history
        if algorithm_id in self.learning_history:
            # More stable algorithms get higher confidence
            prev_result = self.learning_history[algorithm_id]
            stability = 1.0 - abs(performance - prev_result.performance_score)
            base_confidence = 0.7 * base_confidence + 0.3 * stability
        
        return max(0.0, min(1.0, base_confidence))
    
    def _update_learning_metrics(self, result: LearningResult) -> None:
        """Update learning performance metrics"""        self.performance_metrics["total_learning_sessions"] += 1
        
        # Update average improvement rate
        current_avg = self.performance_metrics["average_improvement_rate"]
        total_sessions = self.performance_metrics["total_learning_sessions"]
        
        self.performance_metrics["average_improvement_rate"] = (
            (current_avg * (total_sessions - 1) + result.improvement_rate) / total_sessions
        )
        
        # Update best performance
        if result.performance_score > self.performance_metrics["best_performance"]:
            self.performance_metrics["best_performance"] = result.performance_score
        
        # Update convergence rate
        if result.convergence_time > 0:
            self.performance_metrics["convergence_rate"] = (
                self.performance_metrics["convergence_rate"] * 0.9 + 
                (1.0 / result.convergence_time) * 0.1
            )
        
        self.performance_metrics["active_learners"] = len(set(
            result.algorithm_id for result in self.learning_history.values()
        ))
    
    async def optimize_strategy(
        self,
        content_data: Dict[str, Any],
        optimization_objective: OptimizationObjective,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """        Optimize content strategy using learned models
        
        Args:
            content_data: Content data for optimization
            optimization_objective: Optimization goal
            constraints: Optional constraints
            
        Returns:
            Optimized strategy recommendations
        """        try:
            # Extract features from content data
            features = await self._extract_optimization_features(content_data)
            
            # Get predictions from all learners
            predictions = {}
            
            # Online learner prediction
            online_pred = self.online_learner.predict(features)
            predictions['online'] = float(online_pred[0]) if online_pred.size > 0 else 0.0
            
            # RL agent action
            rl_action = self.rl_learner.get_action(features)
            predictions['rl_action'] = rl_action.tolist() if hasattr(rl_action, 'tolist') else [float(rl_action)]
            
            # Ensemble prediction
            ensemble_pred = self.model_selector.predict_ensemble(features)
            predictions['ensemble'] = float(ensemble_pred[0]) if ensemble_pred.size > 0 else 0.0
            
            # Strategy optimization
            if optimization_objective == OptimizationObjective.ENGAGEMENT:
                strategy = self._optimize_for_engagement(predictions, constraints)
            elif optimization_objective == OptimizationObjective.REVENUE:
                strategy = self._optimize_for_revenue(predictions, constraints)
            elif optimization_objective == OptimizationObjective.REACH:
                strategy = self._optimize_for_reach(predictions, constraints)
            else:
                strategy = self._optimize_multi_objective(predictions, constraints)
            
            return {
                'optimized_strategy': strategy,
                'predictions': predictions,
                'objective': optimization_objective.value,
                'confidence': np.mean([
                    self._calculate_confidence(pred, 'strategy') 
                    for pred in predictions.values() if isinstance(pred, (int, float))
                ])
            }
            
        except Exception as e:
            self.logger.error(f"Strategy optimization failed: {e}")
            return {'optimized_strategy': {}, 'predictions': {}, 'confidence': 0.0}
    
    async def _extract_optimization_features(self, content_data: Dict[str, Any]) -> np.ndarray:
        """Extract features for optimization"""        # Simplified feature extraction
        features = []
        
        # Content type
        content_type = content_data.get('type', 'unknown')
        type_encoding = {'audio': 1, 'video': 2, 'image': 3, 'text': 4, 'unknown': 0}
        features.append(type_encoding.get(content_type, 0))
        
        # Duration
        features.append(content_data.get('duration', 0) / 3600)  # Normalize to hours
        
        # Quality score
        features.append(content_data.get('quality_score', 0.5))
        
        # Engagement metrics
        features.append(content_data.get('likes', 0) / 1000)  # Normalize
        features.append(content_data.get('views', 0) / 10000)  # Normalize
        
        # Pad or truncate to expected dimension
        target_dim = self.config.get("input_dim", 100)
        while len(features) < target_dim:
            features.append(0.0)
        
        return np.array(features[:target_dim])
    
    def _optimize_for_engagement(self, predictions: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize strategy for engagement"""        strategy = {
            'posting_time': 'peak_hours',
            'content_length': 'medium',
            'interaction_encouragement': True,
            'hashtag_strategy': 'trending_relevant'
        }
        
        # Adjust based on predictions
        ensemble_score = predictions.get('ensemble', 0.5)
        if ensemble_score > 0.7:
            strategy['posting_frequency'] = 'high'
        elif ensemble_score > 0.4:
            strategy['posting_frequency'] = 'medium'
        else:
            strategy['posting_frequency'] = 'low'
        
        return strategy
    
    def _optimize_for_revenue(self, predictions: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize strategy for revenue"""        strategy = {
            'monetization_focus': True,
            'premium_content_ratio': 0.3,
            'collaboration_opportunities': True,
            'brand_partnerships': True
        }
        
        # Adjust based on predictions
        online_score = predictions.get('online', 0.5)
        if online_score > 0.6:
            strategy['premium_content_ratio'] = 0.5
            strategy['pricing_strategy'] = 'premium'
        else:
            strategy['pricing_strategy'] = 'competitive'
        
        return strategy
    
    def _optimize_for_reach(self, predictions: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize strategy for reach"""        strategy = {
            'cross_platform_posting': True,
            'viral_content_focus': True,
            'influencer_collaborations': True,
            'trending_topic_alignment': True
        }
        
        return strategy
    
    def _optimize_multi_objective(self, predictions: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Multi-objective optimization"""        # Combine strategies with weights
        engagement_strategy = self._optimize_for_engagement(predictions, constraints)
        revenue_strategy = self._optimize_for_revenue(predictions, constraints)
        reach_strategy = self._optimize_for_reach(predictions, constraints)
        
        # Weighted combination
        combined_strategy = {
            'balanced_approach': True,
            'engagement_weight': 0.4,
            'revenue_weight': 0.4,
            'reach_weight': 0.2
        }
        
        # Merge specific recommendations
        combined_strategy.update({
            'posting_strategy': engagement_strategy.get('posting_frequency', 'medium'),
            'monetization_enabled': revenue_strategy.get('monetization_focus', False),
            'cross_platform': reach_strategy.get('cross_platform_posting', False)
        })
        
        return combined_strategy
    
    async def start_experiment(
        self,
        experiment_name: str,
        experiment_config: Dict[str, Any]
    ) -> str:
        """Start a learning experiment"""        experiment_id = f"exp_{int(datetime.now().timestamp())}"
        
        self.active_experiments[experiment_id] = {
            'name': experiment_name,
            'config': experiment_config,
            'start_time': datetime.now(),
            'results': []
        }
        
        self.logger.info(f"Started learning experiment: {experiment_name} ({experiment_id})")
        return experiment_id
    
    async def get_learning_metrics(self) -> Dict[str, Any]:
        """Get learning engine performance metrics"""        return self.performance_metrics.copy()
    
    async def get_model_recommendations(
        self,
        content_features: np.ndarray,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Get top model recommendations for content"""        try:
            recommendations = []
            
            # Get predictions from all models
            for i, model in enumerate(self.model_selector.models):
                try:
                    if hasattr(model, 'predict'):
                        prediction = model.predict(content_features.reshape(1, -1))
                        confidence = self.model_selector.model_weights[i]
                        
                        recommendations.append({
                            'model_id': i,
                            'model_type': type(model).__name__,
                            'prediction': float(prediction[0]),
                            'confidence': float(confidence),
                            'performance_history': self.model_selector.model_performances[i][-10:]
                        })
                except Exception as e:
                    self.logger.warning(f"Model {i} prediction failed: {e}")
                    continue
            
            # Sort by confidence and return top k
            recommendations.sort(key=lambda x: x['confidence'], reverse=True)
            return recommendations[:top_k]
            
        except Exception as e:
            self.logger.error(f"Model recommendations failed: {e}")
            return []
    
    def reset_learner(self, learner_type: str) -> bool:
        """Reset a specific learner"""        try:
            if learner_type == "online":
                self.online_learner = OnlineLearner(
                    input_dim=self.config.get("input_dim", 100),
                    output_dim=self.config.get("output_dim", 1),
                    learning_rate=self.config.get("learning_rate", 0.01)
                )
            elif learner_type == "rl":
                self.rl_learner = ReinforcementLearner(
                    state_dim=self.config.get("state_dim", 50),
                    action_dim=self.config.get("action_dim", 10),
                    algorithm=self.config.get("rl_algorithm", "ppo")
                )
            elif learner_type == "meta":
                self.meta_learner = MetaLearner(
                    input_dim=self.config.get("input_dim", 100),
                    output_dim=self.config.get("output_dim", 1),
                    meta_lr=self.config.get("meta_lr", 0.001)
                )
            else:
                return False
            
            self.logger.info(f"Reset {learner_type} learner successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset {learner_type} learner: {e}")
            return False
