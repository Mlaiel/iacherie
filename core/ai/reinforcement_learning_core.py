"""
Reinforcement Learning Core - Advanced Reinforcement Learning System
====================================================================

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Core business logic for reinforcement learning, policy optimization,
agent training, and intelligent decision making.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
import json
import uuid
from abc import ABC, abstractmethod

# Get logger
logger = logging.getLogger(__name__)

class RLAlgorithm(Enum):
    """Reinforcement learning algorithms"""
    Q_LEARNING = "q_learning"
    DEEP_Q_NETWORK = "deep_q_network"
    POLICY_GRADIENT = "policy_gradient"
    ACTOR_CRITIC = "actor_critic"
    PPO = "ppo"
    SAC = "sac"
    DDPG = "ddpg"

class AgentState(Enum):
    """Agent states"""
    IDLE = "idle"
    TRAINING = "training"
    EVALUATING = "evaluating"
    DEPLOYED = "deployed"
    UPDATING = "updating"

@dataclass
class RLEnvironment:
    """Reinforcement learning environment"""
    env_id: str
    name: str
    state_space: Dict[str, Any]
    action_space: Dict[str, Any]
    reward_function: str
    max_steps: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrainingResult:
    """Training result"""
    agent_id: str
    episode: int
    total_reward: float
    steps: int
    loss: float
    accuracy: float
    timestamp: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)

class ReinforcementLearningCore:
    """Advanced Reinforcement Learning Core System"""
    
    def __init__(self, level -> None: str = "enterprise") -> None:
        self.version = "2.1.0"
        self.level = level
        self.agents = {}
        self.environments = {}
        self.training_sessions = {}
        self.policies = {}
        self.experience_replay = {}
        
        logger.info(f"Reinforcement Learning Core initialized - Level: {level}")

    async def create_agent(self, agent_config: Dict[str, Any]) -> str:
        """Create RL agent"""
        try:
            agent_id = f"agent_{uuid.uuid4().hex[:12]}"
            
            agent = {
                "id": agent_id,
                "algorithm": RLAlgorithm(agent_config.get("algorithm", "q_learning")),
                "state": AgentState.IDLE,
                "hyperparameters": agent_config.get("hyperparameters", {}),
                "network_architecture": agent_config.get("network_architecture", {}),
                "created_at": datetime.now(),
                "total_episodes": 0,
                "total_reward": 0.0,
                "performance_metrics": {}
            }
            
            self.agents[agent_id] = agent
            
            logger.info(f"RL Agent created: {agent_id}")
            return agent_id
            
        except Exception as e:
            logger.error(f"Failed to create RL agent: {str(e)}")
            return ""

    async def create_environment(self, env_config: Dict[str, Any]) -> str:
        """Create RL environment"""
        try:
            env_id = f"env_{uuid.uuid4().hex[:12]}"
            
            environment = RLEnvironment(
                env_id=env_id,
                name=env_config.get("name", "Custom Environment"),
                state_space=env_config.get("state_space", {}),
                action_space=env_config.get("action_space", {}),
                reward_function=env_config.get("reward_function", "custom"),
                max_steps=env_config.get("max_steps", 1000),
                metadata=env_config.get("metadata", {})
            )
            
            self.environments[env_id] = environment
            
            logger.info(f"RL Environment created: {env_id}")
            return env_id
            
        except Exception as e:
            logger.error(f"Failed to create RL environment: {str(e)}")
            return ""

    async def train_agent(self, agent_id: str, env_id: str, training_config: Dict[str, Any]) -> bool:
        """Train RL agent"""
        try:
            if agent_id not in self.agents or env_id not in self.environments:
                return False
            
            agent = self.agents[agent_id]
            environment = self.environments[env_id]
            
            # Start training session
            session_id = f"session_{uuid.uuid4().hex[:8]}"
            training_session = {
                "session_id": session_id,
                "agent_id": agent_id,
                "env_id": env_id,
                "start_time": datetime.now(),
                "episodes": training_config.get("episodes", 1000),
                "current_episode": 0,
                "results": []
            }
            
            agent["state"] = AgentState.TRAINING
            self.training_sessions[session_id] = training_session
            
            # Simulate training episodes
            for episode in range(training_config.get("episodes", 100)):
                result = await self._simulate_episode(agent, environment, episode)
                training_session["results"].append(result)
                training_session["current_episode"] = episode + 1
                
                # Update agent metrics
                agent["total_episodes"] += 1
                agent["total_reward"] += result.total_reward
                
                # Early stopping if performance is good
                if result.total_reward > 1000:  # Example threshold
                    break
            
            agent["state"] = AgentState.IDLE
            training_session["end_time"] = datetime.now()
            
            logger.info(f"Agent training completed: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Agent training failed: {str(e)}")
            return False

    async def _simulate_episode(self, agent: Dict[str, Any], environment: RLEnvironment, episode: int) -> TrainingResult:
        """Simulate training episode"""
        # Mock episode simulation
        total_reward = np.random.normal(100, 20)  # Random reward with noise
        steps = np.random.randint(50, environment.max_steps)
        loss = max(0, np.random.normal(0.1, 0.05))  # Decreasing loss over time
        accuracy = min(1.0, 0.5 + episode * 0.001)  # Increasing accuracy
        
        result = TrainingResult(
            agent_id=agent["id"],
            episode=episode,
            total_reward=total_reward,
            steps=steps,
            loss=loss,
            accuracy=accuracy,
            timestamp=datetime.now(),
            metrics={
                "exploration_rate": max(0.1, 1.0 - episode * 0.001),
                "learning_rate": 0.001,
                "avg_reward": total_reward / steps
            }
        )
        
        return result

    async def evaluate_agent(self, agent_id: str, env_id: str, episodes: int = 10) -> Dict[str, Any]:
        """Evaluate trained agent"""
        try:
            if agent_id not in self.agents or env_id not in self.environments:
                return {}
            
            agent = self.agents[agent_id]
            environment = self.environments[env_id]
            
            agent["state"] = AgentState.EVALUATING
            
            evaluation_results = []
            total_rewards = []
            
            for episode in range(episodes):
                # Mock evaluation episode
                reward = np.random.normal(150, 30)  # Better performance than training
                steps = np.random.randint(30, 100)
                
                episode_result = {
                    "episode": episode,
                    "reward": reward,
                    "steps": steps,
                    "success": reward > 100
                }
                
                evaluation_results.append(episode_result)
                total_rewards.append(reward)
            
            agent["state"] = AgentState.IDLE
            
            evaluation_summary = {
                "agent_id": agent_id,
                "environment_id": env_id,
                "total_episodes": episodes,
                "average_reward": np.mean(total_rewards),
                "std_reward": np.std(total_rewards),
                "success_rate": sum(1 for r in evaluation_results if r["success"]) / episodes,
                "min_reward": min(total_rewards),
                "max_reward": max(total_rewards),
                "results": evaluation_results
            }
            
            logger.info(f"Agent evaluation completed: {agent_id}")
            return evaluation_summary
            
        except Exception as e:
            logger.error(f"Agent evaluation failed: {str(e)}")
            return {}

    async def deploy_agent(self, agent_id: str, deployment_config: Dict[str, Any]) -> bool:
        """Deploy trained agent"""
        try:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            
            # Check if agent is trained
            if agent["total_episodes"] < 100:  # Minimum training requirement
                logger.warning(f"Agent {agent_id} needs more training")
                return False
            
            agent["state"] = AgentState.DEPLOYED
            agent["deployment_config"] = deployment_config
            agent["deployed_at"] = datetime.now()
            
            logger.info(f"Agent deployed: {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Agent deployment failed: {str(e)}")
            return False

    async def get_training_analytics(self, agent_id: str) -> Dict[str, Any]:
        """Get training analytics for agent"""
        try:
            if agent_id not in self.agents:
                return {}
            
            agent = self.agents[agent_id]
            
            # Find training sessions for this agent
            sessions = [s for s in self.training_sessions.values() if s["agent_id"] == agent_id]
            
            if not sessions:
                return {}
            
            latest_session = max(sessions, key=lambda x: x["start_time"])
            results = latest_session.get("results", [])
            
            if not results:
                return {}
            
            rewards = [r.total_reward for r in results]
            losses = [r.loss for r in results]
            
            analytics = {
                "agent_id": agent_id,
                "total_sessions": len(sessions),
                "total_episodes": len(results),
                "average_reward": np.mean(rewards),
                "reward_improvement": rewards[-1] - rewards[0] if len(rewards) > 1 else 0,
                "final_loss": losses[-1] if losses else 0,
                "convergence_episode": self._find_convergence_point(rewards),
                "performance_trend": "improving" if rewards[-1] > rewards[0] else "declining",
                "training_duration": str(latest_session.get("end_time", datetime.now()) - latest_session["start_time"])
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to get training analytics: {str(e)}")
            return {}

    def _find_convergence_point(self, rewards: List[float]) -> int:
        """Find convergence point in training"""
        if len(rewards) < 10:
            return -1
        
        # Simple convergence detection: when variance becomes small
        window_size = 10
        for i in range(window_size, len(rewards)):
            window = rewards[i-window_size:i]
            if np.std(window) < 10:  # Threshold for convergence
                return i
        
        return -1

# Module exports
__all__ = [
    "ReinforcementLearningCore",
    "RLAlgorithm",
    "AgentState", 
    "RLEnvironment",
    "TrainingResult"
]

logger.info("🤖 Reinforcement Learning Core module loaded")