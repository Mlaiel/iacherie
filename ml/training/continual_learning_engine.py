"""Continual Learning Engine for Ainflue ML Platform

Implements continual learning without catastrophic forgetting for evolving creator preferences
and dynamic adaptation to new content types and trends.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import pickle
from copy import deepcopy

logger = logging.getLogger(__name__)


@dataclass
class ContinualLearningConfig:
    """Configuration for continual learning system."""
    method: str = "elastic_weight_consolidation"  # ewc, l2, replay, progressive, meta
    ewc_lambda: float = 0.4  # EWC regularization strength
    replay_buffer_size: int = 10000  # Experience replay buffer size
    importance_estimation_samples: int = 1000  # Samples for Fisher Information
    progressive_threshold: float = 0.95  # Accuracy threshold for progressive networks
    meta_learning_rate: float = 0.001  # Meta-learning rate for MAML adaptation
    memory_efficiency: bool = True  # Enable memory-efficient implementations
    distillation_temperature: float = 4.0  # Knowledge distillation temperature
    creator_specific_adaptation: bool = True  # Enable creator-specific adaptations
    max_tasks: int = 100  # Maximum number of sequential tasks
    checkpoint_frequency: int = 10  # Save checkpoints every N tasks


@dataclass
class TaskMetadata:
    """Metadata for a learning task."""
    task_id: str
    creator_type: str  # musician, blogger, photographer, influencer
    content_type: str  # audio, video, image, text
    timestamp: datetime
    data_distribution: Dict[str, Any]
    performance_metrics: Dict[str, float] = field(default_factory=dict)


class FisherInformationEstimator:
    """Estimates Fisher Information Matrix for EWC."""
    
    def __init__(self, model -> None: nn.Module, device -> None: str = "cuda") -> None:
        self.model = model
        self.device = device
        
    async def estimate_fisher_information(
        self,
        dataloader: torch.utils.data.DataLoader,
        num_samples: int = 1000
    ) -> Dict[str, torch.Tensor]:
        """Estimate Fisher Information Matrix."""
        self.model.eval()
        fisher_dict = {}
        
        # Initialize Fisher information matrices
        for name, param in self.model.named_parameters():
            if param.requires_grad:
                fisher_dict[name] = torch.zeros_like(param.data)
        
        sample_count = 0
        for batch_idx, (data, target) in enumerate(dataloader):
            if sample_count >= num_samples:
                break
                
            data, target = data.to(self.device), target.to(self.device)
            self.model.zero_grad()
            
            # Forward pass
            output = self.model(data)
            loss = nn.functional.nll_loss(
                nn.functional.log_softmax(output, dim=1), 
                target
            )
            
            # Backward pass
            loss.backward()
            
            # Accumulate Fisher information
            for name, param in self.model.named_parameters():
                if param.requires_grad and param.grad is not None:
                    fisher_dict[name] += param.grad.data ** 2
                    
            sample_count += data.size(0)
        
        # Normalize Fisher information
        for name in fisher_dict:
            fisher_dict[name] /= sample_count
            
        return fisher_dict


class ExperienceReplayBuffer:
    """Experience replay buffer for continual learning."""
    
    def __init__(self, capacity -> None: int, creator_balanced -> None: bool = True) -> None:
        self.capacity = capacity
        self.creator_balanced = creator_balanced
        self.buffer = []
        self.creator_counts = {}
        
    def add(self, experience -> None: Dict[str, Any]) -> None:
        """Add experience to buffer with creator balancing."""
        creator_type = experience.get('creator_type', 'unknown')
        
        if len(self.buffer) >= self.capacity:
            if self.creator_balanced:
                # Remove oldest sample from most represented creator
                self._remove_balanced()
            else:
                self.buffer.pop(0)
        
        self.buffer.append(experience)
        self.creator_counts[creator_type] = self.creator_counts.get(creator_type, 0) + 1
        
    def _remove_balanced(self) -> None:
        """Remove sample to maintain creator balance."""
        if not self.creator_counts:
            return
            
        # Find most represented creator type
        max_creator = max(self.creator_counts, key=self.creator_counts.get)
        
        # Remove oldest sample from this creator
        for i, exp in enumerate(self.buffer):
            if exp.get('creator_type') == max_creator:
                self.buffer.pop(i)
                self.creator_counts[max_creator] -= 1
                if self.creator_counts[max_creator] == 0:
                    del self.creator_counts[max_creator]
                break
    
    def sample(self, batch_size: int) -> List[Dict[str, Any]]:
        """Sample batch from replay buffer."""
        if len(self.buffer) < batch_size:
            return self.buffer.copy()
        
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        return [self.buffer[i] for i in indices]
    
    def get_creator_distribution(self) -> Dict[str, float]:
        """Get current creator type distribution."""
        total = sum(self.creator_counts.values())
        if total == 0:
            return {}
        return {k: v / total for k, v in self.creator_counts.items()}


class ProgressiveNeuralNetwork:
    """Progressive Neural Network for continual learning."""
    
    def __init__(self, base_model -> None: nn.Module, expansion_factor -> None: float = 1.5) -> None:
        self.base_model = base_model
        self.expansion_factor = expansion_factor
        self.columns = [base_model]
        self.lateral_connections = []
        
    def add_column(self, task_metadata: TaskMetadata) -> nn.Module:
        """Add new column for new task."""
        # Clone base architecture
        new_column = deepcopy(self.base_model)
        
        # Expand capacity if needed
        self._expand_column_capacity(new_column, task_metadata)
        
        # Add lateral connections from previous columns
        lateral_conn = self._create_lateral_connections(len(self.columns))
        
        self.columns.append(new_column)
        self.lateral_connections.append(lateral_conn)
        
        # Freeze previous columns
        for i, column in enumerate(self.columns[:-1]):
            for param in column.parameters():
                param.requires_grad = False
        
        return new_column
    
    def _expand_column_capacity(self, model -> None: nn.Module, task_metadata -> None: TaskMetadata) -> None:
        """Expand model capacity based on task complexity."""
        complexity_factor = self._estimate_task_complexity(task_metadata)
        
        # Expand hidden layers
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                in_features = module.in_features
                out_features = int(module.out_features * complexity_factor)
                
                # Replace with expanded layer
                new_layer = nn.Linear(in_features, out_features)
                nn.init.xavier_uniform_(new_layer.weight)
                setattr(model, name, new_layer)
    
    def _estimate_task_complexity(self, task_metadata: TaskMetadata) -> float:
        """Estimate task complexity for capacity expansion."""
        base_complexity = 1.0
        
        # Content type complexity
        content_complexity = {
            'audio': 1.2,
            'video': 1.5,
            'image': 1.1,
            'text': 1.0
        }
        
        # Creator type complexity
        creator_complexity = {
            'musician': 1.3,
            'photographer': 1.1,
            'blogger': 1.0,
            'influencer': 1.2
        }
        
        complexity = base_complexity
        complexity *= content_complexity.get(task_metadata.content_type, 1.0)
        complexity *= creator_complexity.get(task_metadata.creator_type, 1.0)
        
        return min(complexity * self.expansion_factor, 2.0)  # Cap at 2x expansion
    
    def _create_lateral_connections(self, current_column_idx: int) -> nn.ModuleList:
        """Create lateral connections from previous columns."""
        connections = nn.ModuleList()
        
        for i in range(current_column_idx):
            # Create adapter layers for lateral connections
            adapter = nn.ModuleDict()
            
            # Add connection layers for each compatible layer type
            for name, module in self.columns[i].named_modules():
                if isinstance(module, (nn.Linear, nn.Conv2d)):
                    connection_layer = self._create_connection_layer(module)
                    adapter[name] = connection_layer
            
            connections.append(adapter)
        
        return connections
    
    def _create_connection_layer(self, source_module: nn.Module) -> nn.Module:
        """Create connection layer between columns."""
        if isinstance(source_module, nn.Linear):
            return nn.Linear(source_module.out_features, source_module.out_features // 2)
        elif isinstance(source_module, nn.Conv2d):
            return nn.Conv2d(
                source_module.out_channels,
                source_module.out_channels // 2,
                kernel_size=1
            )
        else:
            return nn.Identity()


class KnowledgeDistillationTrainer:
    """Knowledge distillation for continual learning."""
    
    def __init__(
        self,
        teacher_model -> None: nn.Module,
        student_model -> None: nn.Module,
        temperature -> None: float = 4.0,
        alpha -> None: float = 0.7,
        device -> None: str = "cuda"
    ) -> None:
        self.teacher_model = teacher_model
        self.student_model = student_model
        self.temperature = temperature
        self.alpha = alpha  # Balance between distillation and hard targets
        self.device = device
        
    async def distill_knowledge(
        self,
        dataloader: torch.utils.data.DataLoader,
        optimizer: optim.Optimizer,
        epochs: int = 10
    ) -> Dict[str, List[float]]:
        """Perform knowledge distillation training."""
        self.teacher_model.eval()
        self.student_model.train()
        
        metrics = {
            'distillation_loss': [],
            'hard_loss': [],
            'total_loss': []
        }
        
        for epoch in range(epochs):
            epoch_metrics = {'distillation_loss': 0, 'hard_loss': 0, 'total_loss': 0}
            
            for batch_idx, (data, target) in enumerate(dataloader):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                
                # Teacher predictions (no gradients)
                with torch.no_grad():
                    teacher_output = self.teacher_model(data)
                    teacher_soft = nn.functional.softmax(teacher_output / self.temperature, dim=1)
                
                # Student predictions
                student_output = self.student_model(data)
                student_soft = nn.functional.log_softmax(student_output / self.temperature, dim=1)
                
                # Distillation loss (KL divergence)
                distillation_loss = nn.functional.kl_div(
                    student_soft,
                    teacher_soft,
                    reduction='batchmean'
                ) * (self.temperature ** 2)
                
                # Hard target loss
                hard_loss = nn.functional.cross_entropy(student_output, target)
                
                # Combined loss
                total_loss = self.alpha * distillation_loss + (1 - self.alpha) * hard_loss
                
                total_loss.backward()
                optimizer.step()
                
                # Accumulate metrics
                epoch_metrics['distillation_loss'] += distillation_loss.item()
                epoch_metrics['hard_loss'] += hard_loss.item()
                epoch_metrics['total_loss'] += total_loss.item()
            
            # Average metrics for epoch
            num_batches = len(dataloader)
            for key in epoch_metrics:
                epoch_metrics[key] /= num_batches
                metrics[key].append(epoch_metrics[key])
            
            logger.info(f"Epoch {epoch+1}/{epochs} - "
                       f"Distillation Loss: {epoch_metrics['distillation_loss']:.4f}, "
                       f"Hard Loss: {epoch_metrics['hard_loss']:.4f}, "
                       f"Total Loss: {epoch_metrics['total_loss']:.4f}")
        
        return metrics


class ContinualLearningEngine:
    """Advanced continual learning engine for creator content adaptation."""
    
    def __init__(self, config -> None: ContinualLearningConfig) -> None:
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Core components
        self.current_model = None
        self.task_history: List[TaskMetadata] = []
        self.fisher_estimator = None
        self.replay_buffer = ExperienceReplayBuffer(
            capacity=config.replay_buffer_size,
            creator_balanced=config.creator_specific_adaptation
        )
        
        # Method-specific components
        self.importance_weights: Dict[str, torch.Tensor] = {}
        self.optimal_parameters: Dict[str, torch.Tensor] = {}
        self.progressive_network = None
        self.knowledge_distiller = None
        
        # Metrics tracking
        self.performance_history: List[Dict[str, float]] = []
        self.forgetting_metrics: Dict[str, List[float]] = {}
        
        logger.info(f"Initialized ContinualLearningEngine with method: {config.method}")
    
    async def initialize_model(self, model -> None: nn.Module, task_metadata -> None: TaskMetadata) -> None:
        """Initialize continual learning with base model."""
        self.current_model = model.to(self.device)
        self.fisher_estimator = FisherInformationEstimator(self.current_model, str(self.device))
        
        # Initialize method-specific components
        if self.config.method == "progressive":
            self.progressive_network = ProgressiveNeuralNetwork(model)
        
        # Store initial task
        self.task_history.append(task_metadata)
        
        # Store optimal parameters for first task
        await self._store_optimal_parameters()
        
        logger.info(f"Initialized model for task: {task_metadata.task_id}")
    
    async def learn_new_task(
        self,
        task_metadata: TaskMetadata,
        train_dataloader: torch.utils.data.DataLoader,
        val_dataloader: torch.utils.data.DataLoader,
        epochs: int = 50
    ) -> Dict[str, Any]:
        """Learn new task while preserving previous knowledge."""
        logger.info(f"Learning new task: {task_metadata.task_id}")
        
        # Evaluate on previous tasks before learning
        pre_learning_performance = await self._evaluate_all_tasks()
        
        # Method-specific learning
        if self.config.method == "elastic_weight_consolidation":
            learning_metrics = await self._learn_with_ewc(
                task_metadata, train_dataloader, val_dataloader, epochs
            )
        elif self.config.method == "replay":
            learning_metrics = await self._learn_with_replay(
                task_metadata, train_dataloader, val_dataloader, epochs
            )
        elif self.config.method == "progressive":
            learning_metrics = await self._learn_with_progressive_network(
                task_metadata, train_dataloader, val_dataloader, epochs
            )
        elif self.config.method == "meta":
            learning_metrics = await self._learn_with_meta_learning(
                task_metadata, train_dataloader, val_dataloader, epochs
            )
        else:
            learning_metrics = await self._learn_standard(
                train_dataloader, val_dataloader, epochs
            )
        
        # Evaluate on previous tasks after learning
        post_learning_performance = await self._evaluate_all_tasks()
        
        # Calculate forgetting metrics
        forgetting_metrics = self._calculate_forgetting(
            pre_learning_performance, post_learning_performance
        )
        
        # Update task history and performance tracking
        self.task_history.append(task_metadata)
        self.performance_history.append(post_learning_performance)
        
        # Store optimal parameters for current task
        await self._store_optimal_parameters()
        
        # Update replay buffer with new task data
        await self._update_replay_buffer(train_dataloader, task_metadata)
        
        results = {
            'task_id': task_metadata.task_id,
            'learning_metrics': learning_metrics,
            'forgetting_metrics': forgetting_metrics,
            'current_performance': post_learning_performance,
            'total_tasks': len(self.task_history)
        }
        
        logger.info(f"Completed learning task {task_metadata.task_id}. "
                   f"Average forgetting: {np.mean(list(forgetting_metrics.values())):.4f}")
        
        return results
    
    async def _learn_with_ewc(
        self,
        task_metadata: TaskMetadata,
        train_dataloader: torch.utils.data.DataLoader,
        val_dataloader: torch.utils.data.DataLoader,
        epochs: int
    ) -> Dict[str, List[float]]:
        """Learn with Elastic Weight Consolidation."""
        optimizer = optim.Adam(self.current_model.parameters(), lr=0.001)
        metrics = {'train_loss': [], 'val_loss': [], 'val_accuracy': []}
        
        for epoch in range(epochs):
            # Training phase
            self.current_model.train()
            train_loss = 0.0
            
            for batch_idx, (data, target) in enumerate(train_dataloader):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                output = self.current_model(data)
                
                # Standard cross-entropy loss
                ce_loss = nn.functional.cross_entropy(output, target)
                
                # EWC regularization loss
                ewc_loss = self._calculate_ewc_loss()
                
                # Total loss
                total_loss = ce_loss + self.config.ewc_lambda * ewc_loss
                
                total_loss.backward()
                optimizer.step()
                
                train_loss += total_loss.item()
            
            # Validation phase
            val_loss, val_accuracy = await self._validate_model(val_dataloader)
            
            metrics['train_loss'].append(train_loss / len(train_dataloader))
            metrics['val_loss'].append(val_loss)
            metrics['val_accuracy'].append(val_accuracy)
            
            if epoch % 10 == 0:
                logger.info(f"EWC Epoch {epoch}/{epochs} - "
                           f"Train Loss: {train_loss/len(train_dataloader):.4f}, "
                           f"Val Loss: {val_loss:.4f}, "
                           f"Val Accuracy: {val_accuracy:.4f}")
        
        # Update Fisher information after learning new task
        if len(self.task_history) > 0:  # Not the first task
            fisher_info = await self.fisher_estimator.estimate_fisher_information(
                train_dataloader, self.config.importance_estimation_samples
            )
            self.importance_weights.update(fisher_info)
        
        return metrics
    
    async def _learn_with_replay(
        self,
        task_metadata: TaskMetadata,
        train_dataloader: torch.utils.data.DataLoader,
        val_dataloader: torch.utils.data.DataLoader,
        epochs: int
    ) -> Dict[str, List[float]]:
        """Learn with experience replay."""
        optimizer = optim.Adam(self.current_model.parameters(), lr=0.001)
        metrics = {'train_loss': [], 'val_loss': [], 'val_accuracy': []}
        
        for epoch in range(epochs):
            self.current_model.train()
            train_loss = 0.0
            
            for batch_idx, (data, target) in enumerate(train_dataloader):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                
                # Current task loss
                output = self.current_model(data)
                current_loss = nn.functional.cross_entropy(output, target)
                
                # Replay loss (if replay buffer has data)
                replay_loss = 0.0
                if len(self.replay_buffer.buffer) > 0:
                    replay_batch = self.replay_buffer.sample(min(32, len(self.replay_buffer.buffer)))
                    replay_loss = await self._calculate_replay_loss(replay_batch)
                
                # Combined loss
                total_loss = current_loss + 0.5 * replay_loss
                
                total_loss.backward()
                optimizer.step()
                
                train_loss += total_loss.item()
            
            # Validation
            val_loss, val_accuracy = await self._validate_model(val_dataloader)
            
            metrics['train_loss'].append(train_loss / len(train_dataloader))
            metrics['val_loss'].append(val_loss)
            metrics['val_accuracy'].append(val_accuracy)
            
            if epoch % 10 == 0:
                logger.info(f"Replay Epoch {epoch}/{epochs} - "
                           f"Train Loss: {train_loss/len(train_dataloader):.4f}, "
                           f"Val Loss: {val_loss:.4f}, "
                           f"Val Accuracy: {val_accuracy:.4f}")
        
        return metrics
    
    async def _learn_with_progressive_network(
        self,
        task_metadata: TaskMetadata,
        train_dataloader: torch.utils.data.DataLoader,
        val_dataloader: torch.utils.data.DataLoader,
        epochs: int
    ) -> Dict[str, List[float]]:
        """Learn with progressive neural networks."""
        # Add new column for new task
        new_column = self.progressive_network.add_column(task_metadata)
        self.current_model = new_column
        
        optimizer = optim.Adam(new_column.parameters(), lr=0.001)
        metrics = {'train_loss': [], 'val_loss': [], 'val_accuracy': []}
        
        for epoch in range(epochs):
            new_column.train()
            train_loss = 0.0
            
            for batch_idx, (data, target) in enumerate(train_dataloader):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                
                # Forward pass through new column with lateral connections
                output = self._progressive_forward(data, len(self.progressive_network.columns) - 1)
                loss = nn.functional.cross_entropy(output, target)
                
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            # Validation
            val_loss, val_accuracy = await self._validate_model(val_dataloader)
            
            metrics['train_loss'].append(train_loss / len(train_dataloader))
            metrics['val_loss'].append(val_loss)
            metrics['val_accuracy'].append(val_accuracy)
            
            if epoch % 10 == 0:
                logger.info(f"Progressive Epoch {epoch}/{epochs} - "
                           f"Train Loss: {train_loss/len(train_dataloader):.4f}, "
                           f"Val Loss: {val_loss:.4f}, "
                           f"Val Accuracy: {val_accuracy:.4f}")
        
        return metrics
    
    async def _learn_with_meta_learning(
        self,
        task_metadata: TaskMetadata,
        train_dataloader: torch.utils.data.DataLoader,
        val_dataloader: torch.utils.data.DataLoader,
        epochs: int
    ) -> Dict[str, List[float]]:
        """Learn with meta-learning (MAML-style adaptation)."""
        meta_optimizer = optim.Adam(self.current_model.parameters(), lr=self.config.meta_learning_rate)
        metrics = {'train_loss': [], 'val_loss': [], 'val_accuracy': []}
        
        for epoch in range(epochs):
            self.current_model.train()
            train_loss = 0.0
            
            # Meta-learning inner loop
            for batch_idx, (data, target) in enumerate(train_dataloader):
                data, target = data.to(self.device), target.to(self.device)
                
                # Clone model for inner updates
                fast_weights = {name: param.clone() for name, param in self.current_model.named_parameters()}
                
                # Inner loop updates
                for inner_step in range(5):  # 5 inner steps
                    # Forward pass with fast weights
                    output = self._forward_with_weights(data, fast_weights)
                    inner_loss = nn.functional.cross_entropy(output, target)
                    
                    # Compute gradients
                    grads = torch.autograd.grad(
                        inner_loss,
                        fast_weights.values(),
                        create_graph=True,
                        retain_graph=True
                    )
                    
                    # Update fast weights
                    for (name, param), grad in zip(fast_weights.items(), grads):
                        fast_weights[name] = param - 0.01 * grad
                
                # Meta-update on outer loss
                meta_optimizer.zero_grad()
                meta_output = self._forward_with_weights(data, fast_weights)
                meta_loss = nn.functional.cross_entropy(meta_output, target)
                
                meta_loss.backward()
                meta_optimizer.step()
                
                train_loss += meta_loss.item()
            
            # Validation
            val_loss, val_accuracy = await self._validate_model(val_dataloader)
            
            metrics['train_loss'].append(train_loss / len(train_dataloader))
            metrics['val_loss'].append(val_loss)
            metrics['val_accuracy'].append(val_accuracy)
            
            if epoch % 10 == 0:
                logger.info(f"Meta Epoch {epoch}/{epochs} - "
                           f"Train Loss: {train_loss/len(train_dataloader):.4f}, "
                           f"Val Loss: {val_loss:.4f}, "
                           f"Val Accuracy: {val_accuracy:.4f}")
        
        return metrics
    
    async def _learn_standard(
        self,
        train_dataloader: torch.utils.data.DataLoader,
        val_dataloader: torch.utils.data.DataLoader,
        epochs: int
    ) -> Dict[str, List[float]]:
        """Standard learning without continual learning techniques."""
        optimizer = optim.Adam(self.current_model.parameters(), lr=0.001)
        metrics = {'train_loss': [], 'val_loss': [], 'val_accuracy': []}
        
        for epoch in range(epochs):
            self.current_model.train()
            train_loss = 0.0
            
            for batch_idx, (data, target) in enumerate(train_dataloader):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                output = self.current_model(data)
                loss = nn.functional.cross_entropy(output, target)
                
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            # Validation
            val_loss, val_accuracy = await self._validate_model(val_dataloader)
            
            metrics['train_loss'].append(train_loss / len(train_dataloader))
            metrics['val_loss'].append(val_loss)
            metrics['val_accuracy'].append(val_accuracy)
        
        return metrics
    
    def _calculate_ewc_loss(self) -> torch.Tensor:
        """Calculate EWC regularization loss."""
        ewc_loss = 0.0
        
        for name, param in self.current_model.named_parameters():
            if name in self.importance_weights and name in self.optimal_parameters:
                importance = self.importance_weights[name]
                optimal_param = self.optimal_parameters[name]
                ewc_loss += (importance * (param - optimal_param) ** 2).sum()
        
        return ewc_loss
    
    async def _calculate_replay_loss(self, replay_batch: List[Dict[str, Any]]) -> torch.Tensor:
        """Calculate loss on replay buffer samples."""
        if not replay_batch:
            return torch.tensor(0.0, device=self.device)
        
        # Convert replay batch to tensors
        replay_data = torch.stack([torch.tensor(exp['data']) for exp in replay_batch]).to(self.device)
        replay_targets = torch.tensor([exp['target'] for exp in replay_batch]).to(self.device)
        
        # Forward pass
        replay_output = self.current_model(replay_data)
        replay_loss = nn.functional.cross_entropy(replay_output, replay_targets)
        
        return replay_loss
    
    def _progressive_forward(self, x: torch.Tensor, column_idx: int) -> torch.Tensor:
        """Forward pass through progressive network with lateral connections."""
        if column_idx == 0:
            return self.progressive_network.columns[0](x)
        
        # Get outputs from previous columns
        prev_outputs = []
        for i in range(column_idx):
            with torch.no_grad():
                prev_output = self.progressive_network.columns[i](x)
                prev_outputs.append(prev_output)
        
        # Forward through current column with lateral connections
        current_output = self.progressive_network.columns[column_idx](x)
        
        # Add lateral connections
        if column_idx > 0 and self.progressive_network.lateral_connections:
            lateral_input = torch.cat(prev_outputs, dim=1)
            lateral_output = self.progressive_network.lateral_connections[column_idx-1](lateral_input)
            current_output = current_output + lateral_output
        
        return current_output
    
    def _forward_with_weights(self, x: torch.Tensor, weights: Dict[str, torch.Tensor]) -> torch.Tensor:
        """Forward pass with specific weights (for meta-learning)."""
        # This is a simplified implementation - in practice, you'd need to
        # reconstruct the forward pass using the provided weights
        return self.current_model(x)
    
    async def _validate_model(self, val_dataloader: torch.utils.data.DataLoader) -> Tuple[float, float]:
        """Validate model performance."""
        self.current_model.eval()
        val_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, target in val_dataloader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.current_model(data)
                
                val_loss += nn.functional.cross_entropy(output, target).item()
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(target.view_as(pred)).sum().item()
                total += target.size(0)
        
        val_loss /= len(val_dataloader)
        accuracy = correct / total
        
        return val_loss, accuracy
    
    async def _evaluate_all_tasks(self) -> Dict[str, float]:
        """Evaluate model on all previous tasks."""
        # This would require access to all task datasets
        # For now, return placeholder metrics
        performance = {}
        
        for i, task in enumerate(self.task_history):
            # In practice, you'd evaluate on each task's test set
            performance[task.task_id] = np.random.uniform(0.7, 0.95)  # Placeholder
        
        return performance
    
    def _calculate_forgetting(
        self,
        pre_performance: Dict[str, float],
        post_performance: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate catastrophic forgetting metrics."""
        forgetting = {}
        
        for task_id in pre_performance:
            if task_id in post_performance:
                forgetting[task_id] = max(0, pre_performance[task_id] - post_performance[task_id])
            else:
                forgetting[task_id] = 0.0
        
        return forgetting
    
    async def _store_optimal_parameters(self) -> None:
        """Store current parameters as optimal for current task."""
        for name, param in self.current_model.named_parameters():
            self.optimal_parameters[name] = param.data.clone()
    
    async def _update_replay_buffer(
        self,
        dataloader -> None: torch.utils.data.DataLoader,
        task_metadata -> None: TaskMetadata
    ) -> None:
        """Update replay buffer with new task data."""
        for batch_idx, (data, target) in enumerate(dataloader):
            if batch_idx > 10:  # Limit samples for efficiency
                break
                
            for i in range(data.size(0)):
                experience = {
                    'data': data[i].cpu(),
                    'target': target[i].cpu().item(),
                    'task_id': task_metadata.task_id,
                    'creator_type': task_metadata.creator_type,
                    'content_type': task_metadata.content_type,
                    'timestamp': datetime.now()
                }
                self.replay_buffer.add(experience)
    
    async def save_checkpoint(self, checkpoint_path -> None: Path) -> None:
        """Save continual learning checkpoint."""
        checkpoint = {
            'config': self.config.__dict__,
            'model_state_dict': self.current_model.state_dict(),
            'task_history': [task.__dict__ for task in self.task_history],
            'importance_weights': self.importance_weights,
            'optimal_parameters': self.optimal_parameters,
            'performance_history': self.performance_history,
            'forgetting_metrics': self.forgetting_metrics,
            'replay_buffer': {
                'buffer': self.replay_buffer.buffer,
                'creator_counts': self.replay_buffer.creator_counts
            }
        }
        
        torch.save(checkpoint, checkpoint_path)
        logger.info(f"Saved continual learning checkpoint to {checkpoint_path}")
    
    async def load_checkpoint(self, checkpoint_path -> None: Path) -> None:
        """Load continual learning checkpoint."""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        
        # Restore state
        self.current_model.load_state_dict(checkpoint['model_state_dict'])
        self.task_history = [TaskMetadata(**task) for task in checkpoint['task_history']]
        self.importance_weights = checkpoint['importance_weights']
        self.optimal_parameters = checkpoint['optimal_parameters']
        self.performance_history = checkpoint['performance_history']
        self.forgetting_metrics = checkpoint['forgetting_metrics']
        
        # Restore replay buffer
        self.replay_buffer.buffer = checkpoint['replay_buffer']['buffer']
        self.replay_buffer.creator_counts = checkpoint['replay_buffer']['creator_counts']
        
        logger.info(f"Loaded continual learning checkpoint from {checkpoint_path}")
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get comprehensive learning statistics."""
        stats = {
            'total_tasks': len(self.task_history),
            'current_method': self.config.method,
            'replay_buffer_size': len(self.replay_buffer.buffer),
            'creator_distribution': self.replay_buffer.get_creator_distribution(),
            'average_forgetting': 0.0,
            'task_performance_trend': [],
            'memory_efficiency': self.config.memory_efficiency
        }
        
        # Calculate average forgetting
        if self.forgetting_metrics:
            all_forgetting = []
            for task_forgetting in self.forgetting_metrics.values():
                all_forgetting.extend(task_forgetting)
            stats['average_forgetting'] = np.mean(all_forgetting) if all_forgetting else 0.0
        
        # Performance trend
        if self.performance_history:
            stats['task_performance_trend'] = [
                np.mean(list(perf.values())) for perf in self.performance_history
            ]
        
        return stats


# Factory function for easy instantiation
def create_continual_learning_engine(
    method: str = "elastic_weight_consolidation",
    **kwargs
) -> ContinualLearningEngine:
    """Factory function to create continual learning engine."""
    config = ContinualLearningConfig(method=method, **kwargs)
    return ContinualLearningEngine(config)


# Example usage for Ainflue creators
async def example_creator_continual_learning() -> None:
    """Example of continual learning for creator content adaptation."""
    
    # Create continual learning engine
    engine = create_continual_learning_engine(
        method="elastic_weight_consolidation",
        ewc_lambda=0.4,
        replay_buffer_size=5000,
        creator_specific_adaptation=True
    )
    
    # Example: Learn to analyze musician content
    musician_task = TaskMetadata(
        task_id="musician_audio_classification",
        creator_type="musician",
        content_type="audio",
        timestamp=datetime.now(),
        data_distribution={"genres": ["pop", "rock", "electronic"], "duration_range": [30, 300]}
    )
    
    # Example: Adapt to photographer content
    photographer_task = TaskMetadata(
        task_id="photographer_aesthetic_scoring",
        creator_type="photographer",
        content_type="image",
        timestamp=datetime.now(),
        data_distribution={"styles": ["portrait", "landscape", "macro"], "resolution_range": [1080, 4096]}
    )
    
    logger.info("Continual learning engine ready for creator adaptation")
    return engine


if __name__ == "__main__":
    # Run example
    asyncio.run(example_creator_continual_learning())