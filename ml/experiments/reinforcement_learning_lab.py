"""🎯 Reinforcement Learning Lab - Advanced RL Research Platform
===============================================================
Module: ml/experiments/reinforcement_learning_lab.py
Author: Fahed Mlaiel (mlaiel@live.de)
===============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 REINFORCEMENT LEARNING LABORATORY
Advanced RL research platform for creator content optimization
- Multi-agent RL for creator collaboration
- Content recommendation optimization
- Revenue maximization through RL
- Real-time A/B testing with RL
- Meta-learning for rapid adaptation
- Safe RL for content moderation
"""

import asyncio
import logging
import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid
import random
import math
from collections import defaultdict, deque, namedtuple
import pickle
import gym
import gymnasium

logger = logging.getLogger(__name__)

class RLAlgorithm(Enum):
    """Reinforcement learning algorithms"""
    DQN = "dqn"
    DDPG = "ddpg"
    A3C = "a3c"
    PPO = "ppo"
    SAC = "sac"
    TD3 = "td3"
    RAINBOW = "rainbow"
    IMPALA = "impala"
    APEX = "apex"
    MULTI_AGENT = "multi_agent"

class EnvironmentType(Enum):
    """RL environment types for creator platform"""
    CONTENT_RECOMMENDATION = "content_recommendation"
    REVENUE_OPTIMIZATION = "revenue_optimization"
    CREATOR_MATCHING = "creator_matching"
    CONTENT_SCHEDULING = "content_scheduling"
    ENGAGEMENT_MAXIMIZATION = "engagement_maximization"
    RESOURCE_ALLOCATION = "resource_allocation"
    A_B_TESTING = "a_b_testing"
    CONTENT_MODERATION = "content_moderation"

class ExplorationStrategy(Enum):
    """Exploration strategies"""
    EPSILON_GREEDY = "epsilon_greedy"
    UCB = "ucb"
    THOMPSON_SAMPLING = "thompson_sampling"
    NOISE_BASED = "noise_based"
    CURIOSITY_DRIVEN = "curiosity_driven"
    INFO_GAIN = "info_gain"

# Define experience tuple
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])

@dataclass
class RLExperiment:
    """RL experiment configuration"""
    experiment_id: str
    name: str
    algorithm: RLAlgorithm
    environment_type: EnvironmentType
    hyperparameters: Dict[str, Any]
    network_architecture: Dict[str, Any]
    training_config: Dict[str, Any]
    evaluation_metrics: List[str]
    status: str = "initialized"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    best_reward: float = float('-inf')
    total_episodes: int = 0
    total_steps: int = 0
    convergence_threshold: float = 0.01
    early_stopping: bool = True
    checkpointing_frequency: int = 1000
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class MultiAgentConfig:
    """Multi-agent RL configuration"""
    num_agents: int
    agent_types: List[str]
    communication_enabled: bool
    shared_reward: bool
    competition_mode: bool
    cooperation_reward_weight: float = 0.3
    communication_bandwidth: int = 32
    agent_specializations: Dict[str, List[str]] = field(default_factory=dict)

class DQNNetwork(nn.Module):
    """Deep Q-Network for value-based RL"""
    
    def __init__(self, input_dim: int, output_dim: int, hidden_dims: List[int] = [256, 256]):
        super().__init__()
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, output_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Dueling DQN components
        self.value_head = nn.Linear(hidden_dims[-1], 1)
        self.advantage_head = nn.Linear(hidden_dims[-1], output_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.network[:-1](x)  # All layers except last
        
        # Dueling DQN: V(s) + A(s,a) - mean(A(s,a))
        value = self.value_head(features)
        advantage = self.advantage_head(features)
        
        q_values = value + advantage - advantage.mean(dim=1, keepdim=True)
        return q_values

class ActorCriticNetwork(nn.Module):
    """Actor-Critic network for policy-based RL"""
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [256, 256]):
        super().__init__()
        
        # Shared feature extractor
        self.shared_layers = nn.Sequential(
            nn.Linear(state_dim, hidden_dims[0]),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
        # Actor network (policy)
        actor_layers = []
        prev_dim = hidden_dims[0]
        for hidden_dim in hidden_dims[1:]:
            actor_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            prev_dim = hidden_dim
        
        actor_layers.append(nn.Linear(prev_dim, action_dim))
        actor_layers.append(nn.Tanh())  # For continuous actions
        
        self.actor = nn.Sequential(*actor_layers)
        
        # Critic network (value function)
        critic_layers = []
        prev_dim = hidden_dims[0]
        for hidden_dim in hidden_dims[1:]:
            critic_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            prev_dim = hidden_dim
        
        critic_layers.append(nn.Linear(prev_dim, 1))
        
        self.critic = nn.Sequential(*critic_layers)
        
    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        features = self.shared_layers(state)
        action = self.actor(features)
        value = self.critic(features)
        return action, value

class CreatorEnvironment:
    """Creator platform RL environment"""
    
    def __init__(self, env_type: EnvironmentType, config: Dict[str, Any]):
        self.env_type = env_type
        self.config = config
        
        # Environment dimensions
        self.state_dim = config.get('state_dim', 100)
        self.action_dim = config.get('action_dim', 10)
        self.max_steps = config.get('max_steps', 1000)
        
        # Current state
        self.current_state = None
        self.step_count = 0
        self.episode_reward = 0.0
        
        # Creator-specific parameters
        self.creator_profiles = self._initialize_creator_profiles()
        self.content_library = self._initialize_content_library()
        self.engagement_models = self._initialize_engagement_models()
        
        # Simulation parameters
        self.noise_level = config.get('noise_level', 0.1)
        self.reward_scaling = config.get('reward_scaling', 1.0)
        
    def reset(self) -> np.ndarray:
        """Reset environment to initial state"""
        self.step_count = 0
        self.episode_reward = 0.0
        
        if self.env_type == EnvironmentType.CONTENT_RECOMMENDATION:
            self.current_state = self._reset_recommendation_env()
        elif self.env_type == EnvironmentType.REVENUE_OPTIMIZATION:
            self.current_state = self._reset_revenue_env()
        elif self.env_type == EnvironmentType.CREATOR_MATCHING:
            self.current_state = self._reset_matching_env()
        else:
            self.current_state = np.random.normal(0, 1, self.state_dim)
        
        return self.current_state
    
    def step(self, action: Union[int, np.ndarray]) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Execute action and return next state, reward, done, info"""
        self.step_count += 1
        
        # Execute action based on environment type
        if self.env_type == EnvironmentType.CONTENT_RECOMMENDATION:
            next_state, reward, done, info = self._step_recommendation(action)
        elif self.env_type == EnvironmentType.REVENUE_OPTIMIZATION:
            next_state, reward, done, info = self._step_revenue_optimization(action)
        elif self.env_type == EnvironmentType.CREATOR_MATCHING:
            next_state, reward, done, info = self._step_creator_matching(action)
        else:
            next_state, reward, done, info = self._step_generic(action)
        
        self.current_state = next_state
        self.episode_reward += reward
        
        # Check termination conditions
        done = done or self.step_count >= self.max_steps
        
        return next_state, reward, done, info
    
    def _reset_recommendation_env(self) -> np.ndarray:
        """Reset content recommendation environment"""
        # State: [user_preferences, content_features, context, history]
        user_prefs = np.random.normal(0, 1, 20)
        content_features = np.random.normal(0, 1, 30)
        context = np.random.normal(0, 1, 25)
        history = np.random.normal(0, 1, 25)
        
        return np.concatenate([user_prefs, content_features, context, history])
    
    def _step_recommendation(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Step in content recommendation environment"""
        # Action: content_id to recommend
        content_id = action
        
        # Simulate user engagement based on action
        engagement_score = self._simulate_engagement(content_id)
        
        # Reward based on engagement and diversity
        reward = engagement_score * self.reward_scaling
        
        # Add exploration bonus
        if content_id not in getattr(self, '_recommended_recently', set()):
            reward += 0.1  # Diversity bonus
        
        # Update state
        next_state = self._update_recommendation_state(content_id, engagement_score)
        
        # Track recommendations
        if not hasattr(self, '_recommended_recently'):
            self._recommended_recently = set()
        self._recommended_recently.add(content_id)
        
        # Keep only recent recommendations
        if len(self._recommended_recently) > 10:
            self._recommended_recently.pop()
        
        info = {
            'engagement_score': engagement_score,
            'content_id': content_id,
            'diversity_bonus': 0.1 if content_id not in self._recommended_recently else 0.0
        }
        
        done = False
        return next_state, reward, done, info
    
    def _simulate_engagement(self, content_id: int) -> float:
        """Simulate user engagement with content"""
        # Simple engagement simulation
        base_engagement = np.random.beta(2, 5)  # Skewed towards lower engagement
        
        # Add noise
        noise = np.random.normal(0, self.noise_level)
        engagement = np.clip(base_engagement + noise, 0, 1)
        
        return engagement
    
    def _update_recommendation_state(self, content_id: int, engagement: float) -> np.ndarray:
        """Update state after recommendation"""
        # Update user preferences based on engagement
        preference_update = engagement * 0.1 * np.random.normal(0, 1, 20)
        
        # Update content features
        new_content_features = np.random.normal(0, 1, 30)
        
        # Update context (time, season, etc.)
        context_update = np.random.normal(0, 0.1, 25)
        
        # Update history
        history_update = np.roll(self.current_state[-25:], 1)
        history_update[0] = engagement
        
        updated_prefs = self.current_state[:20] + preference_update
        updated_context = self.current_state[50:75] + context_update
        
        return np.concatenate([updated_prefs, new_content_features, updated_context, history_update])
    
    def _initialize_creator_profiles(self) -> Dict[str, Any]:
        """Initialize creator profiles for simulation"""
        return {
            'musicians': {'count': 1000, 'avg_engagement': 0.6},
            'bloggers': {'count': 800, 'avg_engagement': 0.4},
            'photographers': {'count': 600, 'avg_engagement': 0.7},
            'influencers': {'count': 400, 'avg_engagement': 0.8},
            'comedians': {'count': 200, 'avg_engagement': 0.5}
        }
    
    def _initialize_content_library(self) -> Dict[str, Any]:
        """Initialize content library for simulation"""
        return {
            'total_content': 100000,
            'categories': ['music', 'blog', 'photo', 'video', 'comedy'],
            'quality_distribution': np.random.beta(2, 5, 100000)
        }
    
    def _initialize_engagement_models(self) -> Dict[str, Any]:
        """Initialize engagement prediction models"""
        return {
            'time_decay': 0.95,
            'quality_weight': 0.4,
            'freshness_weight': 0.3,
            'personalization_weight': 0.3
        }
    
    def _reset_revenue_env(self) -> np.ndarray:
        """Reset revenue optimization environment"""
        return np.random.normal(0, 1, self.state_dim)
    
    def _step_revenue_optimization(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Step in revenue optimization environment"""
        # Simulate revenue optimization
        revenue_change = np.sum(action * np.random.normal(1, 0.1, len(action)))
        reward = revenue_change
        
        next_state = self.current_state + np.random.normal(0, 0.1, self.state_dim)
        info = {'revenue_change': revenue_change}
        
        return next_state, reward, False, info
    
    def _reset_matching_env(self) -> np.ndarray:
        """Reset creator matching environment"""
        return np.random.normal(0, 1, self.state_dim)
    
    def _step_creator_matching(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Step in creator matching environment"""
        # Simulate creator collaboration matching
        match_quality = np.random.beta(3, 2)  # Better matches on average
        reward = match_quality
        
        next_state = self.current_state + np.random.normal(0, 0.05, self.state_dim)
        info = {'match_quality': match_quality}
        
        return next_state, reward, False, info
    
    def _step_generic(self, action: Union[int, np.ndarray]) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Generic step function"""
        reward = np.random.normal(0, 1)
        next_state = self.current_state + np.random.normal(0, 0.1, self.state_dim)
        info = {}
        
        return next_state, reward, False, info

class ReinforcementLearningLab:
    """Advanced reinforcement learning research laboratory"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize RL laboratory"""
        self.config = config or {}
        
        # Lab configuration
        self.lab_id = str(uuid.uuid4())
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Experiment management
        self.experiments: Dict[str, RLExperiment] = {}
        self.active_agents: Dict[str, Any] = {}
        self.environments: Dict[str, CreatorEnvironment] = {}
        
        # Training infrastructure
        self.replay_buffers: Dict[str, deque] = {}
        self.training_metrics: Dict[str, List[float]] = defaultdict(list)
        self.evaluation_results: Dict[str, Dict[str, Any]] = {}
        
        # Multi-agent coordination
        self.multi_agent_configs: Dict[str, MultiAgentConfig] = {}
        self.agent_communication_channels: Dict[str, Any] = {}
        
        # Research tracking
        self.research_log = deque(maxlen=10000)
        self.hyperparameter_search_results = []
        
        logger.info(f"Reinforcement Learning Lab initialized: {self.lab_id}")

    async def create_rl_experiment(
        self,
        name: str,
        algorithm: RLAlgorithm,
        environment_type: EnvironmentType,
        hyperparameters: Dict[str, Any],
        network_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create new RL experiment"""
        try:
            experiment_id = f"rl_exp_{uuid.uuid4().hex[:12]}"
            
            # Default network configuration
            if network_config is None:
                network_config = {
                    'hidden_dims': [256, 256],
                    'activation': 'relu',
                    'dropout': 0.1
                }
            
            # Default training configuration
            training_config = {
                'max_episodes': hyperparameters.get('max_episodes', 1000),
                'max_steps_per_episode': hyperparameters.get('max_steps_per_episode', 1000),
                'learning_rate': hyperparameters.get('learning_rate', 0.001),
                'batch_size': hyperparameters.get('batch_size', 32),
                'replay_buffer_size': hyperparameters.get('replay_buffer_size', 100000),
                'target_update_frequency': hyperparameters.get('target_update_frequency', 100),
                'evaluation_frequency': hyperparameters.get('evaluation_frequency', 100)
            }
            
            # Create experiment
            experiment = RLExperiment(
                experiment_id=experiment_id,
                name=name,
                algorithm=algorithm,
                environment_type=environment_type,
                hyperparameters=hyperparameters,
                network_architecture=network_config,
                training_config=training_config,
                evaluation_metrics=['episode_reward', 'episode_length', 'loss', 'q_values']
            )
            
            self.experiments[experiment_id] = experiment
            
            # Initialize environment
            env_config = {
                'state_dim': hyperparameters.get('state_dim', 100),
                'action_dim': hyperparameters.get('action_dim', 10),
                'max_steps': training_config['max_steps_per_episode']
            }
            
            self.environments[experiment_id] = CreatorEnvironment(environment_type, env_config)
            
            # Initialize replay buffer
            self.replay_buffers[experiment_id] = deque(maxlen=training_config['replay_buffer_size'])
            
            # Initialize agent
            await self._initialize_agent(experiment_id, algorithm, network_config, hyperparameters)
            
            logger.info(f"RL experiment created: {experiment_id}")
            return experiment_id
            
        except Exception as e:
            logger.error(f"Error creating RL experiment: {e}")
            raise

    async def _initialize_agent(
        self,
        experiment_id: str,
        algorithm: RLAlgorithm,
        network_config: Dict[str, Any],
        hyperparameters: Dict[str, Any]
    ) -> None:
        """Initialize RL agent based on algorithm"""
        try:
            env = self.environments[experiment_id]
            
            if algorithm == RLAlgorithm.DQN:
                agent = self._create_dqn_agent(env, network_config, hyperparameters)
            elif algorithm == RLAlgorithm.PPO:
                agent = self._create_ppo_agent(env, network_config, hyperparameters)
            elif algorithm == RLAlgorithm.SAC:
                agent = self._create_sac_agent(env, network_config, hyperparameters)
            else:
                # Default to DQN
                agent = self._create_dqn_agent(env, network_config, hyperparameters)
            
            self.active_agents[experiment_id] = agent
            
        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            raise

    def _create_dqn_agent(
        self,
        env: CreatorEnvironment,
        network_config: Dict[str, Any],
        hyperparameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create DQN agent"""
        # Create Q-networks
        q_network = DQNNetwork(
            input_dim=env.state_dim,
            output_dim=env.action_dim,
            hidden_dims=network_config['hidden_dims']
        ).to(self.device)
        
        target_network = DQNNetwork(
            input_dim=env.state_dim,
            output_dim=env.action_dim,
            hidden_dims=network_config['hidden_dims']
        ).to(self.device)
        
        # Copy weights to target network
        target_network.load_state_dict(q_network.state_dict())
        
        # Create optimizer
        optimizer = torch.optim.Adam(
            q_network.parameters(),
            lr=hyperparameters.get('learning_rate', 0.001)
        )
        
        agent = {
            'type': 'dqn',
            'q_network': q_network,
            'target_network': target_network,
            'optimizer': optimizer,
            'epsilon': hyperparameters.get('epsilon_start', 1.0),
            'epsilon_decay': hyperparameters.get('epsilon_decay', 0.995),
            'epsilon_min': hyperparameters.get('epsilon_min', 0.01),
            'gamma': hyperparameters.get('gamma', 0.99),
            'tau': hyperparameters.get('tau', 0.005)
        }
        
        return agent

    def _create_ppo_agent(
        self,
        env: CreatorEnvironment,
        network_config: Dict[str, Any],
        hyperparameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create PPO agent"""
        # Create actor-critic network
        actor_critic = ActorCriticNetwork(
            state_dim=env.state_dim,
            action_dim=env.action_dim,
            hidden_dims=network_config['hidden_dims']
        ).to(self.device)
        
        optimizer = torch.optim.Adam(
            actor_critic.parameters(),
            lr=hyperparameters.get('learning_rate', 0.0003)
        )
        
        agent = {
            'type': 'ppo',
            'actor_critic': actor_critic,
            'optimizer': optimizer,
            'gamma': hyperparameters.get('gamma', 0.99),
            'gae_lambda': hyperparameters.get('gae_lambda', 0.95),
            'clip_epsilon': hyperparameters.get('clip_epsilon', 0.2),
            'entropy_coef': hyperparameters.get('entropy_coef', 0.01),
            'value_loss_coef': hyperparameters.get('value_loss_coef', 0.5)
        }
        
        return agent

    def _create_sac_agent(
        self,
        env: CreatorEnvironment,
        network_config: Dict[str, Any],
        hyperparameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create SAC agent (placeholder)"""
        # Simplified SAC implementation
        return self._create_ppo_agent(env, network_config, hyperparameters)

    async def train_agent(
        self,
        experiment_id: str,
        num_episodes: Optional[int] = None
    ) -> Dict[str, Any]:
        """Train RL agent"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment not found: {experiment_id}")
            
            experiment = self.experiments[experiment_id]
            agent = self.active_agents[experiment_id]
            env = self.environments[experiment_id]
            
            if num_episodes is None:
                num_episodes = experiment.training_config['max_episodes']
            
            experiment.status = "training"
            experiment.start_time = datetime.now()
            
            training_results = {
                'episode_rewards': [],
                'episode_lengths': [],
                'losses': [],
                'evaluation_scores': []
            }
            
            for episode in range(num_episodes):
                episode_reward = 0
                episode_length = 0
                state = env.reset()
                done = False
                
                while not done:
                    # Select action
                    action = self._select_action(agent, state, training=True)
                    
                    # Execute action
                    next_state, reward, done, info = env.step(action)
                    
                    # Store experience
                    experience = Experience(state, action, reward, next_state, done)
                    self.replay_buffers[experiment_id].append(experience)
                    
                    # Update agent
                    if len(self.replay_buffers[experiment_id]) > experiment.training_config['batch_size']:
                        loss = await self._update_agent(experiment_id)
                        if loss is not None:
                            training_results['losses'].append(loss)
                    
                    state = next_state
                    episode_reward += reward
                    episode_length += 1
                
                training_results['episode_rewards'].append(episode_reward)
                training_results['episode_lengths'].append(episode_length)
                
                # Update experiment metrics
                experiment.total_episodes += 1
                experiment.total_steps += episode_length
                experiment.best_reward = max(experiment.best_reward, episode_reward)
                
                # Periodic evaluation
                if episode % experiment.training_config['evaluation_frequency'] == 0:
                    eval_score = await self._evaluate_agent(experiment_id)
                    training_results['evaluation_scores'].append(eval_score)
                    
                    logger.info(f"Episode {episode}: Reward={episode_reward:.2f}, Eval={eval_score:.2f}")
                
                # Early stopping check
                if self._check_convergence(training_results['episode_rewards']):
                    logger.info(f"Training converged at episode {episode}")
                    break
            
            experiment.status = "completed"
            experiment.end_time = datetime.now()
            
            # Store training results
            self.training_metrics[experiment_id] = training_results
            
            logger.info(f"Training completed for experiment: {experiment_id}")
            return training_results
            
        except Exception as e:
            logger.error(f"Error training agent: {e}")
            experiment.status = "failed"
            raise

    def _select_action(self, agent: Dict[str, Any], state: np.ndarray, training: bool = True) -> Union[int, np.ndarray]:
        """Select action based on agent type and policy"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        if agent['type'] == 'dqn':
            if training and random.random() < agent['epsilon']:
                # Epsilon-greedy exploration
                return random.randint(0, agent['q_network'].network[-1].out_features - 1)
            else:
                # Greedy action
                with torch.no_grad():
                    q_values = agent['q_network'](state_tensor)
                    return q_values.argmax().item()
        
        elif agent['type'] in ['ppo', 'sac']:
            with torch.no_grad():
                action, _ = agent['actor_critic'](state_tensor)
                if training:
                    # Add exploration noise
                    noise = torch.randn_like(action) * 0.1
                    action = action + noise
                return action.cpu().numpy().flatten()
        
        return 0  # Default action

    async def _update_agent(self, experiment_id: str) -> Optional[float]:
        """Update agent using experiences from replay buffer"""
        try:
            agent = self.active_agents[experiment_id]
            experiment = self.experiments[experiment_id]
            replay_buffer = self.replay_buffers[experiment_id]
            
            if len(replay_buffer) < experiment.training_config['batch_size']:
                return None
            
            # Sample batch
            batch = random.sample(replay_buffer, experiment.training_config['batch_size'])
            
            if agent['type'] == 'dqn':
                return await self._update_dqn(agent, batch)
            elif agent['type'] == 'ppo':
                return await self._update_ppo(agent, batch)
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating agent: {e}")
            return None

    async def _update_dqn(self, agent: Dict[str, Any], batch: List[Experience]) -> float:
        """Update DQN agent"""
        states = torch.FloatTensor([e.state for e in batch]).to(self.device)
        actions = torch.LongTensor([e.action for e in batch]).to(self.device)
        rewards = torch.FloatTensor([e.reward for e in batch]).to(self.device)
        next_states = torch.FloatTensor([e.next_state for e in batch]).to(self.device)
        dones = torch.BoolTensor([e.done for e in batch]).to(self.device)
        
        # Current Q-values
        current_q_values = agent['q_network'](states).gather(1, actions.unsqueeze(1))
        
        # Target Q-values
        with torch.no_grad():
            next_q_values = agent['target_network'](next_states).max(1)[0]
            target_q_values = rewards + (agent['gamma'] * next_q_values * ~dones)
        
        # Compute loss
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        # Update network
        agent['optimizer'].zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(agent['q_network'].parameters(), 1.0)
        agent['optimizer'].step()
        
        # Update target network
        self._soft_update(agent['q_network'], agent['target_network'], agent['tau'])
        
        # Update epsilon
        agent['epsilon'] = max(agent['epsilon_min'], agent['epsilon'] * agent['epsilon_decay'])
        
        return loss.item()

    async def _update_ppo(self, agent: Dict[str, Any], batch: List[Experience]) -> float:
        """Update PPO agent (simplified)"""
        states = torch.FloatTensor([e.state for e in batch]).to(self.device)
        actions = torch.FloatTensor([e.action for e in batch]).to(self.device)
        rewards = torch.FloatTensor([e.reward for e in batch]).to(self.device)
        
        # Forward pass
        predicted_actions, values = agent['actor_critic'](states)
        
        # Compute losses (simplified)
        value_loss = F.mse_loss(values.squeeze(), rewards)
        action_loss = F.mse_loss(predicted_actions, actions)
        
        total_loss = value_loss + action_loss
        
        # Update network
        agent['optimizer'].zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(agent['actor_critic'].parameters(), 0.5)
        agent['optimizer'].step()
        
        return total_loss.item()

    def _soft_update(self, source: nn.Module, target: nn.Module, tau: float) -> None:
        """Soft update target network"""
        for target_param, source_param in zip(target.parameters(), source.parameters()):
            target_param.data.copy_(tau * source_param.data + (1.0 - tau) * target_param.data)

    async def _evaluate_agent(self, experiment_id: str, num_episodes: int = 5) -> float:
        """Evaluate agent performance"""
        try:
            agent = self.active_agents[experiment_id]
            env = self.environments[experiment_id]
            
            total_reward = 0
            
            for _ in range(num_episodes):
                state = env.reset()
                episode_reward = 0
                done = False
                
                while not done:
                    action = self._select_action(agent, state, training=False)
                    state, reward, done, _ = env.step(action)
                    episode_reward += reward
                
                total_reward += episode_reward
            
            return total_reward / num_episodes
            
        except Exception as e:
            logger.error(f"Error evaluating agent: {e}")
            return 0.0

    def _check_convergence(self, rewards: List[float], window: int = 100) -> bool:
        """Check if training has converged"""
        if len(rewards) < window * 2:
            return False
        
        recent_rewards = rewards[-window:]
        previous_rewards = rewards[-window*2:-window]
        
        recent_mean = np.mean(recent_rewards)
        previous_mean = np.mean(previous_rewards)
        
        # Check if improvement is below threshold
        improvement = (recent_mean - previous_mean) / abs(previous_mean) if previous_mean != 0 else 0
        return improvement < 0.01  # 1% improvement threshold

    async def create_multi_agent_experiment(
        self,
        name: str,
        num_agents: int,
        agent_types: List[str],
        environment_type: EnvironmentType,
        cooperation_mode: bool = True
    ) -> str:
        """Create multi-agent RL experiment"""
        try:
            experiment_id = f"multi_agent_{uuid.uuid4().hex[:12]}"
            
            # Configure multi-agent setup
            multi_agent_config = MultiAgentConfig(
                num_agents=num_agents,
                agent_types=agent_types,
                communication_enabled=True,
                shared_reward=cooperation_mode,
                competition_mode=not cooperation_mode
            )
            
            self.multi_agent_configs[experiment_id] = multi_agent_config
            
            # Create individual agent experiments
            agent_experiment_ids = []
            for i, agent_type in enumerate(agent_types):
                agent_exp_id = await self.create_rl_experiment(
                    name=f"{name}_agent_{i}",
                    algorithm=RLAlgorithm.PPO,  # Default for multi-agent
                    environment_type=environment_type,
                    hyperparameters={
                        'learning_rate': 0.0003,
                        'gamma': 0.99,
                        'max_episodes': 1000
                    }
                )
                agent_experiment_ids.append(agent_exp_id)
            
            # Store multi-agent experiment mapping
            self.multi_agent_configs[experiment_id].agent_ids = agent_experiment_ids
            
            logger.info(f"Multi-agent experiment created: {experiment_id}")
            return experiment_id
            
        except Exception as e:
            logger.error(f"Error creating multi-agent experiment: {e}")
            raise

    async def hyperparameter_search(
        self,
        base_experiment_id: str,
        search_space: Dict[str, List[Any]],
        search_strategy: str = "random",
        max_trials: int = 20
    ) -> Dict[str, Any]:
        """Automated hyperparameter search"""
        try:
            if base_experiment_id not in self.experiments:
                raise ValueError(f"Base experiment not found: {base_experiment_id}")
            
            base_experiment = self.experiments[base_experiment_id]
            search_results = []
            
            for trial in range(max_trials):
                # Sample hyperparameters
                if search_strategy == "random":
                    trial_hyperparameters = self._sample_random_hyperparameters(search_space)
                else:
                    trial_hyperparameters = self._sample_random_hyperparameters(search_space)  # Default to random
                
                # Create trial experiment
                trial_experiment_id = await self.create_rl_experiment(
                    name=f"{base_experiment.name}_trial_{trial}",
                    algorithm=base_experiment.algorithm,
                    environment_type=base_experiment.environment_type,
                    hyperparameters=trial_hyperparameters,
                    network_config=base_experiment.network_architecture
                )
                
                # Train for shorter duration
                trial_results = await self.train_agent(
                    trial_experiment_id,
                    num_episodes=100  # Shorter training for search
                )
                
                # Evaluate performance
                final_performance = np.mean(trial_results['episode_rewards'][-10:])
                
                search_results.append({
                    'trial': trial,
                    'hyperparameters': trial_hyperparameters,
                    'performance': final_performance,
                    'experiment_id': trial_experiment_id
                })
                
                logger.info(f"Trial {trial}: Performance={final_performance:.2f}")
            
            # Find best hyperparameters
            best_trial = max(search_results, key=lambda x: x['performance'])
            
            search_summary = {
                'best_hyperparameters': best_trial['hyperparameters'],
                'best_performance': best_trial['performance'],
                'best_experiment_id': best_trial['experiment_id'],
                'all_trials': search_results
            }
            
            self.hyperparameter_search_results.append(search_summary)
            
            logger.info(f"Hyperparameter search completed. Best performance: {best_trial['performance']:.2f}")
            return search_summary
            
        except Exception as e:
            logger.error(f"Error in hyperparameter search: {e}")
            raise

    def _sample_random_hyperparameters(self, search_space: Dict[str, List[Any]]) -> Dict[str, Any]:
        """Sample random hyperparameters from search space"""
        sampled_params = {}
        for param, values in search_space.items():
            sampled_params[param] = random.choice(values)
        return sampled_params

    async def get_experiment_results(self, experiment_id: str) -> Dict[str, Any]:
        """Get comprehensive experiment results"""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        experiment = self.experiments[experiment_id]
        training_metrics = self.training_metrics.get(experiment_id, {})
        
        return {
            'experiment_info': {
                'id': experiment_id,
                'name': experiment.name,
                'algorithm': experiment.algorithm.value,
                'environment_type': experiment.environment_type.value,
                'status': experiment.status,
                'duration_minutes': (
                    (experiment.end_time - experiment.start_time).total_seconds() / 60
                    if experiment.end_time and experiment.start_time else 0
                ),
                'total_episodes': experiment.total_episodes,
                'total_steps': experiment.total_steps,
                'best_reward': experiment.best_reward
            },
            'training_metrics': training_metrics,
            'hyperparameters': experiment.hyperparameters,
            'network_architecture': experiment.network_architecture
        }

    async def save_experiment(self, experiment_id: str, save_path: str) -> bool:
        """Save experiment artifacts"""
        try:
            if experiment_id not in self.experiments:
                raise ValueError(f"Experiment not found: {experiment_id}")
            
            save_data = {
                'experiment': self.experiments[experiment_id],
                'agent': self.active_agents.get(experiment_id),
                'training_metrics': self.training_metrics.get(experiment_id, {}),
                'environment_config': self.environments[experiment_id].config if experiment_id in self.environments else {}
            }
            
            # Save to file
            with open(save_path, 'wb') as f:
                pickle.dump(save_data, f)
            
            logger.info(f"Experiment saved: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving experiment: {e}")
            return False

    async def get_lab_analytics(self) -> Dict[str, Any]:
        """Get comprehensive lab analytics"""
        return {
            'total_experiments': len(self.experiments),
            'active_experiments': len([e for e in self.experiments.values() if e.status == 'training']),
            'completed_experiments': len([e for e in self.experiments.values() if e.status == 'completed']),
            'total_training_time': sum([
                (e.end_time - e.start_time).total_seconds()
                for e in self.experiments.values()
                if e.end_time and e.start_time
            ]) / 3600,  # in hours
            'algorithms_used': list(set([e.algorithm.value for e in self.experiments.values()])),
            'environment_types': list(set([e.environment_type.value for e in self.experiments.values()])),
            'average_performance': np.mean([e.best_reward for e in self.experiments.values()]) if self.experiments else 0.0,
            'hyperparameter_searches': len(self.hyperparameter_search_results)
        }

# Global lab instance
_lab_instance = None

def get_rl_lab() -> ReinforcementLearningLab:
    """Get global RL lab instance"""
    global _lab_instance
    if _lab_instance is None:
        _lab_instance = ReinforcementLearningLab()
    return _lab_instance

# Test function
async def test_rl_lab():
    """Test RL lab functionality"""
    lab = ReinforcementLearningLab()
    
    # Create experiment
    experiment_id = await lab.create_rl_experiment(
        name="Content Recommendation RL",
        algorithm=RLAlgorithm.DQN,
        environment_type=EnvironmentType.CONTENT_RECOMMENDATION,
        hyperparameters={
            'learning_rate': 0.001,
            'epsilon_start': 1.0,
            'epsilon_decay': 0.995,
            'max_episodes': 100
        }
    )
    
    # Train agent
    results = await lab.train_agent(experiment_id, num_episodes=10)
    
    # Get results
    experiment_results = await lab.get_experiment_results(experiment_id)
    
    # Get analytics
    analytics = await lab.get_lab_analytics()
    
    logger.info("RL lab test completed successfully")
    return {
        'experiment_id': experiment_id,
        'final_reward': results['episode_rewards'][-1] if results['episode_rewards'] else 0,
        'episodes_trained': len(results['episode_rewards']),
        'lab_analytics': analytics
    }

if __name__ == "__main__":
    # Run test
    asyncio.run(test_rl_lab())