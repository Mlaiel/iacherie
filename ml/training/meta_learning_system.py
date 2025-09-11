"""🧠 Meta-Learning System - Adaptive Learning for Creator Diversity
================================================================
Module: ml/training/meta_learning_system.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🧠 META-LEARNING SYSTEM
Advanced meta-learning for rapid adaptation to new creator types
- Model-Agnostic Meta-Learning (MAML) implementation
- Few-shot learning for new creator onboarding
- Task-specific adaptation algorithms
- Creator-type transfer learning
- Rapid personalization for diverse content types
- Meta-optimization across creator domains
"""

import asyncio
import logging
import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import uuid
import random
import math
import copy
from collections import defaultdict, deque
import pickle

logger = logging.getLogger(__name__)

class MetaLearningAlgorithm(Enum):
    """Meta-learning algorithms"""
    MAML = "maml"
    FOMAML = "fomaml"
    REPTILE = "reptile"
    PROTOTYPICAL = "prototypical"
    MATCHING_NETWORKS = "matching_networks"
    RELATION_NETWORKS = "relation_networks"
    META_SGD = "meta_sgd"
    ANIL = "anil"

class CreatorDomain(Enum):
    """Creator content domains"""
    MUSIC = "music"
    BLOG = "blog"
    PHOTOGRAPHY = "photography"
    VIDEO = "video"
    COMEDY = "comedy"
    GAMING = "gaming"
    COOKING = "cooking"
    FITNESS = "fitness"
    EDUCATION = "education"
    GENERAL = "general"

class TaskType(Enum):
    """Types of meta-learning tasks"""
    CONTENT_CLASSIFICATION = "content_classification"
    ENGAGEMENT_PREDICTION = "engagement_prediction"
    RECOMMENDATION_RANKING = "recommendation_ranking"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    TREND_PREDICTION = "trend_prediction"
    QUALITY_ASSESSMENT = "quality_assessment"
    PERSONALIZATION = "personalization"

@dataclass
class MetaTask:
    """Meta-learning task definition"""
    task_id: str
    task_type: TaskType
    creator_domain: CreatorDomain
    support_samples: int
    query_samples: int
    input_dim: int
    output_dim: int
    task_description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    difficulty_level: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class MetaLearningEpisode:
    """Meta-learning episode (support + query sets)"""
    episode_id: str
    task_id: str
    support_set: Dict[str, torch.Tensor]
    query_set: Dict[str, torch.Tensor]
    episode_metrics: Dict[str, float] = field(default_factory=dict)
    adaptation_steps: int = 5
    learning_rate: float = 0.01
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CreatorProfile:
    """Creator profile for meta-learning"""
    creator_id: str
    creator_type: CreatorDomain
    content_history: List[Dict[str, Any]]
    engagement_patterns: Dict[str, float]
    preferences: Dict[str, Any]
    adaptation_speed: float = 1.0
    personalization_level: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

class MetaLearningDataset(Dataset):
    """Dataset for meta-learning tasks"""
    
    def __init__(self, tasks: List[MetaTask], episodes_per_task: int = 100):
        self.tasks = tasks
        self.episodes_per_task = episodes_per_task
        self.episodes = self._generate_episodes()
    
    def _generate_episodes(self) -> List[MetaLearningEpisode]:
        """Generate meta-learning episodes from tasks"""
        episodes = []
        
        for task in self.tasks:
            for _ in range(self.episodes_per_task):
                episode = self._create_episode(task)
                episodes.append(episode)
        
        return episodes
    
    def _create_episode(self, task: MetaTask) -> MetaLearningEpisode:
        """Create single meta-learning episode"""
        episode_id = f"episode_{uuid.uuid4().hex[:12]}"
        
        # Generate synthetic data based on task type and domain
        support_x, support_y = self._generate_task_data(
            task, task.support_samples, is_support=True
        )
        query_x, query_y = self._generate_task_data(
            task, task.query_samples, is_support=False
        )
        
        support_set = {'x': support_x, 'y': support_y}
        query_set = {'x': query_x, 'y': query_y}
        
        return MetaLearningEpisode(
            episode_id=episode_id,
            task_id=task.task_id,
            support_set=support_set,
            query_set=query_set,
            adaptation_steps=random.randint(3, 10),
            learning_rate=random.uniform(0.001, 0.1)
        )
    
    def _generate_task_data(
        self, 
        task: MetaTask, 
        num_samples: int, 
        is_support: bool = True
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Generate synthetic task data"""
        # Generate input data
        if task.creator_domain == CreatorDomain.MUSIC:
            # Audio-like features
            x = torch.randn(num_samples, task.input_dim) * 0.5
            x[:, :20] += torch.randn(num_samples, 20) * 2  # Spectral features
        elif task.creator_domain == CreatorDomain.PHOTOGRAPHY:
            # Image-like features
            x = torch.randn(num_samples, task.input_dim)
            x = torch.clamp(x, -2, 2)  # Normalized pixel values
        elif task.creator_domain == CreatorDomain.BLOG:
            # Text-like features
            x = torch.randn(num_samples, task.input_dim) * 0.8
            x[:, :50] = torch.softmax(x[:, :50], dim=1)  # Word embeddings
        else:
            # General features
            x = torch.randn(num_samples, task.input_dim)
        
        # Generate labels based on task type
        if task.task_type == TaskType.CONTENT_CLASSIFICATION:
            y = torch.randint(0, task.output_dim, (num_samples,))
        elif task.task_type == TaskType.ENGAGEMENT_PREDICTION:
            y = torch.sigmoid(torch.randn(num_samples, task.output_dim))
        elif task.task_type == TaskType.SENTIMENT_ANALYSIS:
            y = torch.softmax(torch.randn(num_samples, task.output_dim), dim=1)
        else:
            y = torch.randn(num_samples, task.output_dim)
        
        return x, y
    
    def __len__(self) -> int:
        return len(self.episodes)
    
    def __getitem__(self, idx: int) -> MetaLearningEpisode:
        return self.episodes[idx]

class MetaNetwork(nn.Module):
    """Neural network for meta-learning"""
    
    def __init__(
        self, 
        input_dim: int, 
        output_dim: int, 
        hidden_dims: List[int] = [128, 64],
        meta_learning_rate: float = 0.001
    ):
        super().__init__()
        
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.meta_learning_rate = meta_learning_rate
        
        # Build network layers
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
        
        # Meta-learning specific parameters
        self.adaptation_lr = nn.Parameter(torch.tensor(meta_learning_rate))
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)
    
    def clone_with_params(self, params: Dict[str, torch.Tensor]) -> 'MetaNetwork':
        """Create network clone with specific parameters"""
        clone = copy.deepcopy(self)
        
        # Update parameters
        state_dict = clone.state_dict()
        for name, param in params.items():
            if name in state_dict:
                state_dict[name] = param
        
        clone.load_state_dict(state_dict)
        return clone

class MAMLLearner:
    """Model-Agnostic Meta-Learning implementation"""
    
    def __init__(
        self,
        meta_network: MetaNetwork,
        inner_lr: float = 0.01,
        outer_lr: float = 0.001,
        adaptation_steps: int = 5
    ):
        self.meta_network = meta_network
        self.inner_lr = inner_lr
        self.outer_lr = outer_lr
        self.adaptation_steps = adaptation_steps
        
        # Meta-optimizer
        self.meta_optimizer = optim.Adam(
            self.meta_network.parameters(), 
            lr=self.outer_lr
        )
        
    def adapt_to_task(
        self,
        support_set: Dict[str, torch.Tensor],
        adaptation_steps: Optional[int] = None
    ) -> Tuple[MetaNetwork, List[float]]:
        """Adapt network to specific task using support set"""
        if adaptation_steps is None:
            adaptation_steps = self.adaptation_steps
        
        # Clone meta network for adaptation
        adapted_network = copy.deepcopy(self.meta_network)
        
        # Create optimizer for adapted network
        adapted_optimizer = optim.SGD(
            adapted_network.parameters(),
            lr=self.inner_lr
        )
        
        adaptation_losses = []
        
        # Perform adaptation steps
        for step in range(adaptation_steps):
            adapted_optimizer.zero_grad()
            
            # Forward pass
            predictions = adapted_network(support_set['x'])
            
            # Calculate loss
            if len(support_set['y'].shape) == 1:  # Classification
                loss = F.cross_entropy(predictions, support_set['y'])
            else:  # Regression
                loss = F.mse_loss(predictions, support_set['y'])
            
            # Backward pass
            loss.backward()
            adapted_optimizer.step()
            
            adaptation_losses.append(loss.item())
        
        return adapted_network, adaptation_losses
    
    def meta_update(
        self,
        episodes: List[MetaLearningEpisode],
        device: torch.device = torch.device('cpu')
    ) -> Dict[str, float]:
        """Perform meta-update across multiple episodes"""
        self.meta_optimizer.zero_grad()
        
        meta_losses = []
        adaptation_accuracies = []
        
        for episode in episodes:
            # Move data to device
            support_set = {
                k: v.to(device) for k, v in episode.support_set.items()
            }
            query_set = {
                k: v.to(device) for k, v in episode.query_set.items()
            }
            
            # Adapt to task
            adapted_network, adaptation_losses = self.adapt_to_task(
                support_set, episode.adaptation_steps
            )
            
            # Evaluate on query set
            with torch.no_grad():
                query_predictions = adapted_network(query_set['x'])
                
                # Calculate accuracy for classification tasks
                if len(query_set['y'].shape) == 1:
                    accuracy = (query_predictions.argmax(dim=1) == query_set['y']).float().mean()
                    adaptation_accuracies.append(accuracy.item())
            
            # Calculate meta-loss on query set
            query_predictions = adapted_network(query_set['x'])
            
            if len(query_set['y'].shape) == 1:  # Classification
                meta_loss = F.cross_entropy(query_predictions, query_set['y'])
            else:  # Regression
                meta_loss = F.mse_loss(query_predictions, query_set['y'])
            
            meta_losses.append(meta_loss)
        
        # Average meta-loss
        avg_meta_loss = torch.stack(meta_losses).mean()
        
        # Backward pass for meta-parameters
        avg_meta_loss.backward()
        
        # Clip gradients
        torch.nn.utils.clip_grad_norm_(self.meta_network.parameters(), 1.0)
        
        # Meta-optimizer step
        self.meta_optimizer.step()
        
        return {
            'meta_loss': avg_meta_loss.item(),
            'avg_adaptation_accuracy': np.mean(adaptation_accuracies) if adaptation_accuracies else 0.0,
            'num_episodes': len(episodes)
        }

class MetaLearningSystem:
    """Advanced meta-learning system for creator platforms"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize meta-learning system"""
        self.config = config or {}
        
        # System configuration
        self.system_id = str(uuid.uuid4())
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Algorithm configuration
        self.algorithm = MetaLearningAlgorithm(
            self.config.get('algorithm', 'maml')
        )
        self.inner_lr = self.config.get('inner_lr', 0.01)
        self.outer_lr = self.config.get('outer_lr', 0.001)
        self.adaptation_steps = self.config.get('adaptation_steps', 5)
        
        # Task and creator management
        self.meta_tasks: Dict[str, MetaTask] = {}
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        self.domain_experts: Dict[CreatorDomain, MetaNetwork] = {}
        
        # Training infrastructure
        self.meta_learners: Dict[str, MAMLLearner] = {}
        self.training_history = []
        self.adaptation_metrics = defaultdict(list)
        
        # Performance tracking
        self.task_performance = defaultdict(dict)
        self.creator_adaptation_speeds = defaultdict(float)
        self.domain_transfer_matrix = defaultdict(lambda: defaultdict(float))
        
        logger.info(f"Meta-Learning System initialized: {self.system_id}")

    async def register_meta_task(
        self,
        task_type: TaskType,
        creator_domain: CreatorDomain,
        input_dim: int,
        output_dim: int,
        support_samples: int = 10,
        query_samples: int = 15,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Register new meta-learning task"""
        try:
            task_id = f"meta_task_{uuid.uuid4().hex[:12]}"
            
            meta_task = MetaTask(
                task_id=task_id,
                task_type=task_type,
                creator_domain=creator_domain,
                support_samples=support_samples,
                query_samples=query_samples,
                input_dim=input_dim,
                output_dim=output_dim,
                task_description=description,
                metadata=metadata or {}
            )
            
            self.meta_tasks[task_id] = meta_task
            
            # Initialize domain expert if not exists
            if creator_domain not in self.domain_experts:
                await self._initialize_domain_expert(creator_domain, input_dim, output_dim)
            
            logger.info(f"Meta-task registered: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"Error registering meta-task: {e}")
            raise

    async def _initialize_domain_expert(
        self,
        domain: CreatorDomain,
        input_dim: int,
        output_dim: int
    ) -> None:
        """Initialize domain-specific expert network"""
        try:
            # Create meta-network for domain
            meta_network = MetaNetwork(
                input_dim=input_dim,
                output_dim=output_dim,
                hidden_dims=self.config.get('hidden_dims', [128, 64]),
                meta_learning_rate=self.outer_lr
            ).to(self.device)
            
            self.domain_experts[domain] = meta_network
            
            # Create MAML learner
            learner_id = f"learner_{domain.value}"
            self.meta_learners[learner_id] = MAMLLearner(
                meta_network=meta_network,
                inner_lr=self.inner_lr,
                outer_lr=self.outer_lr,
                adaptation_steps=self.adaptation_steps
            )
            
            logger.info(f"Domain expert initialized: {domain.value}")
            
        except Exception as e:
            logger.error(f"Error initializing domain expert: {e}")
            raise

    async def register_creator_profile(
        self,
        creator_id: str,
        creator_type: CreatorDomain,
        content_history: List[Dict[str, Any]],
        engagement_patterns: Dict[str, float],
        preferences: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register creator profile for personalization"""
        try:
            profile = CreatorProfile(
                creator_id=creator_id,
                creator_type=creator_type,
                content_history=content_history,
                engagement_patterns=engagement_patterns,
                preferences=preferences or {},
                adaptation_speed=self._calculate_adaptation_speed(engagement_patterns),
                personalization_level=self._calculate_personalization_level(content_history)
            )
            
            self.creator_profiles[creator_id] = profile
            
            logger.info(f"Creator profile registered: {creator_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering creator profile: {e}")
            return False

    def _calculate_adaptation_speed(self, engagement_patterns: Dict[str, float]) -> float:
        """Calculate adaptation speed based on engagement patterns"""
        # Higher engagement variance indicates faster adaptation needs
        engagement_values = list(engagement_patterns.values())
        if not engagement_values:
            return 1.0
        
        variance = np.var(engagement_values)
        mean_engagement = np.mean(engagement_values)
        
        # Normalize adaptation speed
        adaptation_speed = min(2.0, max(0.5, 1.0 + variance / max(mean_engagement, 0.1)))
        return adaptation_speed

    def _calculate_personalization_level(self, content_history: List[Dict[str, Any]]) -> float:
        """Calculate required personalization level"""
        if not content_history:
            return 0.5
        
        # More diverse content requires higher personalization
        content_types = set()
        for content in content_history:
            content_types.add(content.get('type', 'unknown'))
        
        diversity_score = len(content_types) / max(len(content_history), 1)
        return min(1.0, max(0.1, diversity_score))

    async def train_meta_learner(
        self,
        task_ids: List[str],
        num_episodes: int = 1000,
        batch_size: int = 32,
        num_epochs: int = 10
    ) -> Dict[str, Any]:
        """Train meta-learner on specified tasks"""
        try:
            # Validate tasks
            tasks = []
            for task_id in task_ids:
                if task_id not in self.meta_tasks:
                    raise ValueError(f"Task not found: {task_id}")
                tasks.append(self.meta_tasks[task_id])
            
            if not tasks:
                raise ValueError("No valid tasks provided")
            
            # Group tasks by domain
            domain_tasks = defaultdict(list)
            for task in tasks:
                domain_tasks[task.creator_domain].append(task)
            
            training_results = {}
            
            # Train each domain expert
            for domain, domain_task_list in domain_tasks.items():
                logger.info(f"Training meta-learner for domain: {domain.value}")
                
                learner_id = f"learner_{domain.value}"
                if learner_id not in self.meta_learners:
                    await self._initialize_domain_expert(
                        domain, 
                        domain_task_list[0].input_dim,
                        domain_task_list[0].output_dim
                    )
                
                learner = self.meta_learners[learner_id]
                
                # Create dataset
                dataset = MetaLearningDataset(domain_task_list, num_episodes // len(domain_task_list))
                dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
                
                # Training loop
                epoch_results = []
                
                for epoch in range(num_epochs):
                    epoch_metrics = {
                        'meta_losses': [],
                        'adaptation_accuracies': [],
                        'episodes_processed': 0
                    }
                    
                    for batch in dataloader:
                        # Batch is a list of episodes
                        batch_metrics = learner.meta_update(batch, self.device)
                        
                        epoch_metrics['meta_losses'].append(batch_metrics['meta_loss'])
                        epoch_metrics['adaptation_accuracies'].append(
                            batch_metrics['avg_adaptation_accuracy']
                        )
                        epoch_metrics['episodes_processed'] += batch_metrics['num_episodes']
                    
                    # Calculate epoch averages
                    avg_meta_loss = np.mean(epoch_metrics['meta_losses'])
                    avg_adaptation_accuracy = np.mean(epoch_metrics['adaptation_accuracies'])
                    
                    epoch_result = {
                        'epoch': epoch,
                        'avg_meta_loss': avg_meta_loss,
                        'avg_adaptation_accuracy': avg_adaptation_accuracy,
                        'episodes_processed': epoch_metrics['episodes_processed']
                    }
                    
                    epoch_results.append(epoch_result)
                    
                    logger.info(
                        f"Domain {domain.value} - Epoch {epoch}: "
                        f"Loss={avg_meta_loss:.4f}, Acc={avg_adaptation_accuracy:.4f}"
                    )
                
                training_results[domain.value] = epoch_results
            
            # Store training history
            training_record = {
                'timestamp': datetime.now(),
                'task_ids': task_ids,
                'num_episodes': num_episodes,
                'num_epochs': num_epochs,
                'results': training_results
            }
            
            self.training_history.append(training_record)
            
            logger.info("Meta-learner training completed")
            return training_results
            
        except Exception as e:
            logger.error(f"Error training meta-learner: {e}")
            raise

    async def adapt_to_creator(
        self,
        creator_id: str,
        task_id: str,
        support_data: Dict[str, torch.Tensor],
        adaptation_steps: Optional[int] = None
    ) -> Tuple[MetaNetwork, Dict[str, float]]:
        """Adapt model to specific creator using few-shot learning"""
        try:
            if creator_id not in self.creator_profiles:
                raise ValueError(f"Creator profile not found: {creator_id}")
            
            if task_id not in self.meta_tasks:
                raise ValueError(f"Task not found: {task_id}")
            
            creator_profile = self.creator_profiles[creator_id]
            task = self.meta_tasks[task_id]
            
            # Get domain expert
            domain = creator_profile.creator_type
            learner_id = f"learner_{domain.value}"
            
            if learner_id not in self.meta_learners:
                raise ValueError(f"No meta-learner for domain: {domain.value}")
            
            learner = self.meta_learners[learner_id]
            
            # Adjust adaptation steps based on creator profile
            if adaptation_steps is None:
                base_steps = self.adaptation_steps
                speed_multiplier = creator_profile.adaptation_speed
                adaptation_steps = max(1, int(base_steps * speed_multiplier))
            
            # Perform adaptation
            adapted_network, adaptation_losses = learner.adapt_to_task(
                support_data, adaptation_steps
            )
            
            # Calculate adaptation metrics
            adaptation_metrics = {
                'adaptation_steps': adaptation_steps,
                'initial_loss': adaptation_losses[0] if adaptation_losses else 0.0,
                'final_loss': adaptation_losses[-1] if adaptation_losses else 0.0,
                'loss_reduction': (adaptation_losses[0] - adaptation_losses[-1]) / max(adaptation_losses[0], 1e-8) if len(adaptation_losses) > 1 else 0.0,
                'adaptation_speed': creator_profile.adaptation_speed,
                'personalization_level': creator_profile.personalization_level
            }
            
            # Update creator adaptation tracking
            self.creator_adaptation_speeds[creator_id] = adaptation_metrics['loss_reduction']
            self.adaptation_metrics[creator_id].append(adaptation_metrics)
            
            logger.info(f"Model adapted for creator {creator_id}: {adaptation_metrics['loss_reduction']:.4f} loss reduction")
            return adapted_network, adaptation_metrics
            
        except Exception as e:
            logger.error(f"Error adapting to creator: {e}")
            raise

    async def evaluate_few_shot_performance(
        self,
        task_id: str,
        test_episodes: List[MetaLearningEpisode],
        adaptation_steps: int = 5
    ) -> Dict[str, float]:
        """Evaluate few-shot learning performance"""
        try:
            if task_id not in self.meta_tasks:
                raise ValueError(f"Task not found: {task_id}")
            
            task = self.meta_tasks[task_id]
            domain = task.creator_domain
            learner_id = f"learner_{domain.value}"
            
            if learner_id not in self.meta_learners:
                raise ValueError(f"No meta-learner for domain: {domain.value}")
            
            learner = self.meta_learners[learner_id]
            
            # Evaluate each episode
            episode_accuracies = []
            episode_losses = []
            adaptation_improvements = []
            
            for episode in test_episodes:
                # Adapt to support set
                adapted_network, adaptation_losses = learner.adapt_to_task(
                    episode.support_set, adaptation_steps
                )
                
                # Evaluate on query set
                with torch.no_grad():
                    query_predictions = adapted_network(episode.query_set['x'])
                    
                    # Calculate loss
                    if len(episode.query_set['y'].shape) == 1:  # Classification
                        loss = F.cross_entropy(query_predictions, episode.query_set['y'])
                        accuracy = (query_predictions.argmax(dim=1) == episode.query_set['y']).float().mean()
                        episode_accuracies.append(accuracy.item())
                    else:  # Regression
                        loss = F.mse_loss(query_predictions, episode.query_set['y'])
                        accuracy = 1.0 / (1.0 + loss.item())  # Inverse loss as accuracy proxy
                        episode_accuracies.append(accuracy)
                    
                    episode_losses.append(loss.item())
                
                # Calculate adaptation improvement
                if len(adaptation_losses) > 1:
                    improvement = (adaptation_losses[0] - adaptation_losses[-1]) / max(adaptation_losses[0], 1e-8)
                    adaptation_improvements.append(improvement)
            
            # Calculate aggregate metrics
            evaluation_metrics = {
                'avg_accuracy': np.mean(episode_accuracies),
                'std_accuracy': np.std(episode_accuracies),
                'avg_loss': np.mean(episode_losses),
                'std_loss': np.std(episode_losses),
                'avg_adaptation_improvement': np.mean(adaptation_improvements) if adaptation_improvements else 0.0,
                'num_episodes': len(test_episodes),
                'task_id': task_id,
                'domain': domain.value
            }
            
            # Store performance metrics
            self.task_performance[task_id]['few_shot_evaluation'] = evaluation_metrics
            
            return evaluation_metrics
            
        except Exception as e:
            logger.error(f"Error evaluating few-shot performance: {e}")
            return {}

    async def transfer_across_domains(
        self,
        source_domain: CreatorDomain,
        target_domain: CreatorDomain,
        target_task_data: Dict[str, torch.Tensor],
        adaptation_steps: int = 10
    ) -> Dict[str, float]:
        """Transfer learning across creator domains"""
        try:
            source_learner_id = f"learner_{source_domain.value}"
            target_learner_id = f"learner_{target_domain.value}"
            
            if source_learner_id not in self.meta_learners:
                raise ValueError(f"No source meta-learner for domain: {source_domain.value}")
            
            source_learner = self.meta_learners[source_learner_id]
            
            # Initialize target domain if not exists
            if target_learner_id not in self.meta_learners:
                # Create target learner with source network architecture
                source_network = source_learner.meta_network
                target_network = MetaNetwork(
                    input_dim=source_network.input_dim,
                    output_dim=source_network.output_dim,
                    hidden_dims=[128, 64],  # Default architecture
                    meta_learning_rate=self.outer_lr
                ).to(self.device)
                
                # Initialize target learner
                self.meta_learners[target_learner_id] = MAMLLearner(
                    meta_network=target_network,
                    inner_lr=self.inner_lr,
                    outer_lr=self.outer_lr,
                    adaptation_steps=self.adaptation_steps
                )
                
                self.domain_experts[target_domain] = target_network
            
            target_learner = self.meta_learners[target_learner_id]
            
            # Transfer knowledge: Copy source parameters to target
            source_state_dict = source_learner.meta_network.state_dict()
            target_state_dict = target_learner.meta_network.state_dict()
            
            # Copy compatible parameters
            transferred_params = 0
            for name, param in source_state_dict.items():
                if name in target_state_dict and param.shape == target_state_dict[name].shape:
                    target_state_dict[name] = param.clone()
                    transferred_params += 1
            
            target_learner.meta_network.load_state_dict(target_state_dict)
            
            # Fine-tune on target domain data
            initial_performance = await self._evaluate_network_performance(
                target_learner.meta_network, target_task_data
            )
            
            # Adapt to target task
            adapted_network, adaptation_losses = target_learner.adapt_to_task(
                target_task_data, adaptation_steps
            )
            
            final_performance = await self._evaluate_network_performance(
                adapted_network, target_task_data
            )
            
            # Calculate transfer metrics
            transfer_metrics = {
                'source_domain': source_domain.value,
                'target_domain': target_domain.value,
                'transferred_parameters': transferred_params,
                'initial_performance': initial_performance,
                'final_performance': final_performance,
                'performance_improvement': final_performance - initial_performance,
                'adaptation_steps': adaptation_steps,
                'transfer_efficiency': (final_performance - initial_performance) / max(adaptation_steps, 1)
            }
            
            # Update domain transfer matrix
            self.domain_transfer_matrix[source_domain.value][target_domain.value] = transfer_metrics['performance_improvement']
            
            logger.info(
                f"Domain transfer completed: {source_domain.value} -> {target_domain.value}, "
                f"improvement: {transfer_metrics['performance_improvement']:.4f}"
            )
            
            return transfer_metrics
            
        except Exception as e:
            logger.error(f"Error in domain transfer: {e}")
            raise

    async def _evaluate_network_performance(
        self,
        network: MetaNetwork,
        test_data: Dict[str, torch.Tensor]
    ) -> float:
        """Evaluate network performance on test data"""
        try:
            with torch.no_grad():
                predictions = network(test_data['x'])
                
                if len(test_data['y'].shape) == 1:  # Classification
                    accuracy = (predictions.argmax(dim=1) == test_data['y']).float().mean()
                    return accuracy.item()
                else:  # Regression
                    mse = F.mse_loss(predictions, test_data['y'])
                    return 1.0 / (1.0 + mse.item())  # Inverse loss as performance proxy
                    
        except Exception as e:
            logger.error(f"Error evaluating network performance: {e}")
            return 0.0

    async def get_meta_learning_analytics(self) -> Dict[str, Any]:
        """Get comprehensive meta-learning analytics"""
        try:
            # Calculate domain statistics
            domain_stats = {}
            for domain in CreatorDomain:
                domain_creators = [
                    c for c in self.creator_profiles.values()
                    if c.creator_type == domain
                ]
                
                domain_stats[domain.value] = {
                    'num_creators': len(domain_creators),
                    'avg_adaptation_speed': np.mean([c.adaptation_speed for c in domain_creators]) if domain_creators else 0.0,
                    'avg_personalization_level': np.mean([c.personalization_level for c in domain_creators]) if domain_creators else 0.0,
                    'has_expert': domain in self.domain_experts
                }
            
            # Calculate transfer learning matrix
            transfer_matrix = {}
            for source_domain, targets in self.domain_transfer_matrix.items():
                transfer_matrix[source_domain] = dict(targets)
            
            # Calculate overall performance
            total_adaptations = sum(len(adaptations) for adaptations in self.adaptation_metrics.values())
            
            avg_adaptation_improvement = 0.0
            if total_adaptations > 0:
                all_improvements = []
                for creator_adaptations in self.adaptation_metrics.values():
                    all_improvements.extend([a['loss_reduction'] for a in creator_adaptations])
                avg_adaptation_improvement = np.mean(all_improvements)
            
            return {
                'system_id': self.system_id,
                'algorithm': self.algorithm.value,
                'total_meta_tasks': len(self.meta_tasks),
                'total_creators': len(self.creator_profiles),
                'total_domain_experts': len(self.domain_experts),
                'domain_statistics': domain_stats,
                'transfer_learning_matrix': transfer_matrix,
                'training_history_entries': len(self.training_history),
                'total_adaptations': total_adaptations,
                'avg_adaptation_improvement': avg_adaptation_improvement,
                'meta_learning_efficiency': avg_adaptation_improvement / max(self.adaptation_steps, 1),
                'supported_domains': [domain.value for domain in self.domain_experts.keys()],
                'supported_task_types': list(set([task.task_type.value for task in self.meta_tasks.values()]))
            }
            
        except Exception as e:
            logger.error(f"Error getting meta-learning analytics: {e}")
            return {}

    async def save_meta_learner(self, domain: CreatorDomain, save_path: str) -> bool:
        """Save domain-specific meta-learner"""
        try:
            if domain not in self.domain_experts:
                return False
            
            learner_id = f"learner_{domain.value}"
            if learner_id not in self.meta_learners:
                return False
            
            # Prepare save data
            save_data = {
                'domain': domain.value,
                'meta_network_state': self.domain_experts[domain].state_dict(),
                'learner_config': {
                    'inner_lr': self.meta_learners[learner_id].inner_lr,
                    'outer_lr': self.meta_learners[learner_id].outer_lr,
                    'adaptation_steps': self.meta_learners[learner_id].adaptation_steps
                },
                'system_config': self.config,
                'training_history': self.training_history,
                'timestamp': datetime.now()
            }
            
            # Save to file
            torch.save(save_data, save_path)
            
            logger.info(f"Meta-learner saved for domain {domain.value}: {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving meta-learner: {e}")
            return False

# Global meta-learning system instance
_meta_learning_system_instance = None

def get_meta_learning_system() -> MetaLearningSystem:
    """Get global meta-learning system instance"""
    global _meta_learning_system_instance
    if _meta_learning_system_instance is None:
        _meta_learning_system_instance = MetaLearningSystem()
    return _meta_learning_system_instance

# Test and validation functions
async def test_meta_learning_system():
    """Test meta-learning system functionality"""
    system = MetaLearningSystem({
        'algorithm': 'maml',
        'inner_lr': 0.01,
        'outer_lr': 0.001,
        'adaptation_steps': 5
    })
    
    # Register meta-tasks
    task_ids = []
    
    # Music classification task
    music_task_id = await system.register_meta_task(
        task_type=TaskType.CONTENT_CLASSIFICATION,
        creator_domain=CreatorDomain.MUSIC,
        input_dim=100,
        output_dim=5,
        support_samples=10,
        query_samples=15,
        description="Music genre classification"
    )
    task_ids.append(music_task_id)
    
    # Blog sentiment analysis task
    blog_task_id = await system.register_meta_task(
        task_type=TaskType.SENTIMENT_ANALYSIS,
        creator_domain=CreatorDomain.BLOG,
        input_dim=100,
        output_dim=3,
        support_samples=8,
        query_samples=12,
        description="Blog post sentiment analysis"
    )
    task_ids.append(blog_task_id)
    
    # Register creator profiles
    music_creator_success = await system.register_creator_profile(
        creator_id="musician_001",
        creator_type=CreatorDomain.MUSIC,
        content_history=[
            {'type': 'song', 'genre': 'rock', 'engagement': 0.8},
            {'type': 'song', 'genre': 'pop', 'engagement': 0.6}
        ],
        engagement_patterns={'avg_likes': 1000, 'avg_shares': 100, 'avg_comments': 50}
    )
    
    blog_creator_success = await system.register_creator_profile(
        creator_id="blogger_001",
        creator_type=CreatorDomain.BLOG,
        content_history=[
            {'type': 'article', 'topic': 'tech', 'engagement': 0.7},
            {'type': 'article', 'topic': 'lifestyle', 'engagement': 0.9}
        ],
        engagement_patterns={'avg_views': 5000, 'avg_shares': 200, 'avg_comments': 80}
    )
    
    # Train meta-learners
    training_results = await system.train_meta_learner(
        task_ids=task_ids,
        num_episodes=100,  # Reduced for testing
        batch_size=16,
        num_epochs=3
    )
    
    # Test adaptation to creator
    support_data = {
        'x': torch.randn(10, 100),
        'y': torch.randint(0, 5, (10,))
    }
    
    adapted_network, adaptation_metrics = await system.adapt_to_creator(
        creator_id="musician_001",
        task_id=music_task_id,
        support_data=support_data,
        adaptation_steps=5
    )
    
    # Test domain transfer
    target_data = {
        'x': torch.randn(15, 100),
        'y': torch.randint(0, 3, (15,))
    }
    
    transfer_metrics = await system.transfer_across_domains(
        source_domain=CreatorDomain.MUSIC,
        target_domain=CreatorDomain.PHOTOGRAPHY,
        target_task_data=target_data,
        adaptation_steps=8
    )
    
    # Get analytics
    analytics = await system.get_meta_learning_analytics()
    
    logger.info("Meta-learning system test completed successfully")
    return {
        'registered_tasks': len(task_ids),
        'registered_creators': music_creator_success and blog_creator_success,
        'training_completed': bool(training_results),
        'adaptation_loss_reduction': adaptation_metrics.get('loss_reduction', 0),
        'transfer_improvement': transfer_metrics.get('performance_improvement', 0),
        'total_domain_experts': analytics.get('total_domain_experts', 0),
        'meta_learning_efficiency': analytics.get('meta_learning_efficiency', 0)
    }

if __name__ == "__main__":
    # Run test
    asyncio.run(test_meta_learning_system())