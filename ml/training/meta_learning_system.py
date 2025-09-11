"""
🧠 **Meta-Learning System - Rapid Model Adaptation**

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
Version: 1.0.0

**⚠️ WARNUNG:** Dieser Code ist urheberrechtlich geschützt und vertraulich.

Enterprise meta-learning system for rapid adaptation to new creator types and content formats
using Model-Agnostic Meta-Learning (MAML) and advanced few-shot learning techniques.
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime
import torch.optim as optim
from collections import defaultdict, deque
import copy
import random

# Ainflue ML Core Imports
from ..model_registry.mlflow_registry import MLflowRegistry
from ..feature_stores.feature_store import FeatureStore
from ..monitoring.performance_monitor import PerformanceMonitor

@dataclass
class MetaLearningConfig:
    """Configuration for meta-learning system."""
    meta_lr: float = 1e-3  # Meta-learning rate
    inner_lr: float = 1e-2  # Inner loop learning rate
    inner_steps: int = 5   # Number of inner gradient steps
    meta_batch_size: int = 16  # Number of tasks per meta-batch
    support_shots: int = 5  # Number of support examples per task
    query_shots: int = 15   # Number of query examples per task
    num_classes_per_task: int = 5  # Classes per task (N-way)
    max_meta_iterations: int = 10000
    adaptation_method: str = 'maml'  # 'maml', 'reptile', 'fomaml'
    second_order: bool = True  # Use second-order gradients
    creator_types: List[str] = None

@dataclass  
class Task:
    """Represents a single meta-learning task."""
    task_id: str
    creator_type: str
    content_type: str  # 'audio', 'text', 'image', 'video'
    support_set: List[Dict]
    query_set: List[Dict]
    task_difficulty: float = 1.0
    metadata: Dict[str, Any] = None

class CreatorTaskGenerator:
    """Generates diverse creator-specific tasks for meta-learning."""
    
    def __init__(self, creator_types: List[str]):
        self.creator_types = creator_types
        self.task_templates = {
            'musician': {
                'genre_classification': ['rock', 'jazz', 'classical', 'electronic', 'pop'],
                'mood_detection': ['happy', 'sad', 'energetic', 'calm', 'aggressive'],
                'instrument_recognition': ['guitar', 'piano', 'drums', 'violin', 'saxophone']
            },
            'blogger': {
                'topic_classification': ['tech', 'lifestyle', 'travel', 'food', 'business'],
                'sentiment_analysis': ['positive', 'negative', 'neutral', 'mixed'],
                'writing_style': ['formal', 'casual', 'academic', 'creative', 'technical']
            },
            'photographer': {
                'style_classification': ['portrait', 'landscape', 'street', 'macro', 'abstract'],
                'color_analysis': ['warm', 'cool', 'monochrome', 'vibrant', 'muted'],
                'composition_quality': ['excellent', 'good', 'average', 'poor', 'artistic']
            },
            'influencer': {
                'engagement_prediction': ['high', 'medium', 'low', 'viral_potential'],
                'content_category': ['lifestyle', 'fashion', 'fitness', 'travel', 'food'],
                'audience_reaction': ['positive', 'negative', 'controversial', 'inspiring']
            }
        }
    
    def generate_task(self, creator_type: str, task_type: str = None) -> Task:
        """Generate a single task for meta-learning."""
        if creator_type not in self.task_templates:
            raise ValueError(f"Unknown creator type: {creator_type}")
        
        templates = self.task_templates[creator_type]
        if task_type is None:
            task_type = random.choice(list(templates.keys()))
        
        classes = templates[task_type]
        selected_classes = random.sample(classes, min(len(classes), 5))
        
        # Generate synthetic task data (in real scenario, this would be actual data)
        support_set = []
        query_set = []
        
        for class_idx, class_name in enumerate(selected_classes):
            # Support examples
            for _ in range(5):  # 5-shot learning
                support_set.append({
                    'content': self._generate_synthetic_content(creator_type, class_name),
                    'label': class_idx,
                    'class_name': class_name,
                    'creator_type': creator_type
                })
            
            # Query examples
            for _ in range(15):
                query_set.append({
                    'content': self._generate_synthetic_content(creator_type, class_name),
                    'label': class_idx,
                    'class_name': class_name,
                    'creator_type': creator_type
                })
        
        return Task(
            task_id=f"{creator_type}_{task_type}_{datetime.now().timestamp()}",
            creator_type=creator_type,
            content_type=self._get_content_type(creator_type),
            support_set=support_set,
            query_set=query_set,
            task_difficulty=random.uniform(0.5, 1.5),
            metadata={'task_type': task_type, 'num_classes': len(selected_classes)}
        )
    
    def _generate_synthetic_content(self, creator_type: str, class_name: str) -> Dict:
        """Generate synthetic content for demonstration."""
        if creator_type == 'musician':
            return {
                'features': torch.randn(128),  # Audio features
                'duration': random.uniform(30, 300),
                'tempo': random.randint(60, 180)
            }
        elif creator_type == 'blogger':
            return {
                'text_features': torch.randn(768),  # Text embeddings
                'word_count': random.randint(100, 2000),
                'readability_score': random.uniform(0, 100)
            }
        elif creator_type == 'photographer':
            return {
                'image_features': torch.randn(2048),  # Image features
                'dimensions': (random.randint(800, 4000), random.randint(600, 3000)),
                'color_channels': 3
            }
        else:
            return {
                'multimodal_features': torch.randn(512),
                'engagement_score': random.uniform(0, 1)
            }
    
    def _get_content_type(self, creator_type: str) -> str:
        """Map creator type to content type."""
        mapping = {
            'musician': 'audio',
            'blogger': 'text', 
            'photographer': 'image',
            'influencer': 'multimodal'
        }
        return mapping.get(creator_type, 'multimodal')
    
    def generate_task_batch(self, batch_size: int) -> List[Task]:
        """Generate a batch of diverse tasks."""
        tasks = []
        for _ in range(batch_size):
            creator_type = random.choice(self.creator_types)
            task = self.generate_task(creator_type)
            tasks.append(task)
        return tasks

class MetaNetwork(nn.Module):
    """Meta-network that can quickly adapt to new tasks."""
    
    def __init__(self, input_dim: int, hidden_dim: int = 256, num_classes: int = 5):
        super().__init__()
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1)
        )
        
        self.classifier = nn.Linear(hidden_dim, num_classes)
        
        # Meta-parameters for rapid adaptation
        self.adaptation_layers = nn.ModuleDict({
            'feature_adapter': nn.Linear(hidden_dim, hidden_dim),
            'task_embedding': nn.Embedding(10, hidden_dim),  # For different creator types
            'attention': nn.MultiheadAttention(hidden_dim, num_heads=8)
        })
    
    def forward(self, x, task_embedding=None, support_features=None):
        """Forward pass with optional task-specific adaptation."""
        features = self.feature_extractor(x)
        
        if task_embedding is not None:
            # Apply task-specific adaptation
            task_embed = self.adaptation_layers['task_embedding'](task_embedding)
            features = features + task_embed.unsqueeze(0)
        
        if support_features is not None:
            # Use attention mechanism with support set
            features, _ = self.adaptation_layers['attention'](
                features.unsqueeze(1), 
                support_features, 
                support_features
            )
            features = features.squeeze(1)
        
        # Apply feature adaptation
        features = self.adaptation_layers['feature_adapter'](features)
        
        logits = self.classifier(features)
        return logits, features
    
    def clone_parameters(self):
        """Create a deep copy of parameters for MAML inner loop."""
        return {name: param.clone() for name, param in self.named_parameters()}
    
    def set_parameters(self, parameters):
        """Set parameters from dictionary."""
        for name, param in self.named_parameters():
            param.data = parameters[name].data

class MAMLOptimizer:
    """Model-Agnostic Meta-Learning optimizer."""
    
    def __init__(self, model: nn.Module, config: MetaLearningConfig):
        self.model = model
        self.config = config
        self.meta_optimizer = optim.Adam(model.parameters(), lr=config.meta_lr)
        self.logger = logging.getLogger(__name__)
    
    def inner_loop_update(self, task: Task, fast_weights=None) -> Tuple[Dict, float]:
        """Perform inner loop adaptation for a single task."""
        if fast_weights is None:
            fast_weights = self.model.clone_parameters()
        
        # Prepare support set
        support_x = torch.stack([torch.tensor(item['content']['features'], dtype=torch.float32) 
                                for item in task.support_set])
        support_y = torch.tensor([item['label'] for item in task.support_set], dtype=torch.long)
        
        # Inner loop optimization
        inner_loss_history = []
        for step in range(self.config.inner_steps):
            # Forward pass with fast weights
            self.model.set_parameters(fast_weights)
            logits, _ = self.model(support_x)
            
            inner_loss = F.cross_entropy(logits, support_y)
            inner_loss_history.append(inner_loss.item())
            
            # Compute gradients
            grads = torch.autograd.grad(
                inner_loss,
                self.model.parameters(),
                create_graph=self.config.second_order,
                retain_graph=True
            )
            
            # Update fast weights
            for (name, param), grad in zip(self.model.named_parameters(), grads):
                fast_weights[name] = param - self.config.inner_lr * grad
        
        return fast_weights, np.mean(inner_loss_history)
    
    def compute_meta_loss(self, tasks: List[Task]) -> Tuple[torch.Tensor, Dict[str, float]]:
        """Compute meta-loss across a batch of tasks."""
        meta_losses = []
        metrics = defaultdict(list)
        
        for task in tasks:
            # Inner loop adaptation
            fast_weights, inner_loss = self.inner_loop_update(task)
            
            # Prepare query set
            query_x = torch.stack([torch.tensor(item['content']['features'], dtype=torch.float32)
                                  for item in task.query_set])
            query_y = torch.tensor([item['label'] for item in task.query_set], dtype=torch.long)
            
            # Forward pass with adapted weights
            self.model.set_parameters(fast_weights)
            query_logits, _ = self.model(query_x)
            
            # Meta-loss (query loss after adaptation)
            meta_loss = F.cross_entropy(query_logits, query_y)
            meta_losses.append(meta_loss)
            
            # Compute accuracy
            predictions = torch.argmax(query_logits, dim=1)
            accuracy = (predictions == query_y).float().mean().item()
            
            metrics['inner_loss'].append(inner_loss)
            metrics['meta_loss'].append(meta_loss.item())
            metrics['accuracy'].append(accuracy)
            metrics['task_difficulty'].append(task.task_difficulty)
        
        # Average meta-loss
        total_meta_loss = torch.stack(meta_losses).mean()
        
        # Aggregate metrics
        aggregated_metrics = {
            key: np.mean(values) for key, values in metrics.items()
        }
        
        return total_meta_loss, aggregated_metrics
    
    def meta_update(self, tasks: List[Task]) -> Dict[str, float]:
        """Perform one meta-update step."""
        # Reset meta-optimizer
        self.meta_optimizer.zero_grad()
        
        # Compute meta-loss
        meta_loss, metrics = self.compute_meta_loss(tasks)
        
        # Meta-gradient step
        meta_loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        
        self.meta_optimizer.step()
        
        return metrics

class ReptileOptimizer:
    """Reptile meta-learning optimizer (first-order approximation)."""
    
    def __init__(self, model: nn.Module, config: MetaLearningConfig):
        self.model = model
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def reptile_update(self, tasks: List[Task]) -> Dict[str, float]:
        """Perform Reptile meta-update."""
        initial_weights = self.model.clone_parameters()
        aggregated_weights = {name: torch.zeros_like(param) 
                             for name, param in self.model.named_parameters()}
        
        metrics = defaultdict(list)
        
        for task in tasks:
            # Reset to initial weights
            self.model.set_parameters(initial_weights)
            
            # Task-specific optimization
            task_optimizer = optim.SGD(self.model.parameters(), lr=self.config.inner_lr)
            
            # Prepare data
            support_x = torch.stack([torch.tensor(item['content']['features'], dtype=torch.float32)
                                    for item in task.support_set])
            support_y = torch.tensor([item['label'] for item in task.support_set], dtype=torch.long)
            
            # Inner loop
            for step in range(self.config.inner_steps):
                task_optimizer.zero_grad()
                logits, _ = self.model(support_x)
                loss = F.cross_entropy(logits, support_y)
                loss.backward()
                task_optimizer.step()
                
                metrics['inner_loss'].append(loss.item())
            
            # Accumulate task-adapted weights
            for name, param in self.model.named_parameters():
                aggregated_weights[name] += param.data
        
        # Average the adapted weights
        for name in aggregated_weights:
            aggregated_weights[name] /= len(tasks)
        
        # Reptile update: move towards average of adapted weights
        for name, param in self.model.named_parameters():
            param.data += self.config.meta_lr * (aggregated_weights[name] - param.data)
        
        return {key: np.mean(values) for key, values in metrics.items()}

class MetaLearningSystem:
    """
    🧠 **Enterprise Meta-Learning System**
    
    Advanced meta-learning system for rapid adaptation to new creator types
    and content formats using MAML, Reptile, and custom algorithms.
    """
    
    def __init__(self, config: MetaLearningConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize components
        self.model_registry = MLflowRegistry()
        self.feature_store = FeatureStore()
        self.performance_monitor = PerformanceMonitor()
        
        # Initialize creator types
        if config.creator_types is None:
            config.creator_types = ['musician', 'blogger', 'photographer', 'influencer']
        
        # Task generator
        self.task_generator = CreatorTaskGenerator(config.creator_types)
        
        # Meta-network
        self.meta_network = MetaNetwork(
            input_dim=512,  # Configurable based on content type
            hidden_dim=256,
            num_classes=config.num_classes_per_task
        ).to(self.device)
        
        # Optimizer
        if config.adaptation_method == 'maml':
            self.optimizer = MAMLOptimizer(self.meta_network, config)
        elif config.adaptation_method == 'reptile':
            self.optimizer = ReptileOptimizer(self.meta_network, config)
        else:
            raise ValueError(f"Unknown adaptation method: {config.adaptation_method}")
        
        # Training metrics
        self.training_history = {
            'meta_loss': [],
            'inner_loss': [],
            'accuracy': [],
            'adaptation_speed': [],
            'creator_type_performance': defaultdict(list)
        }
        
        self.logger.info(f"MetaLearningSystem initialized with {config.adaptation_method}")
    
    async def meta_train(self, num_iterations: int = None) -> Dict[str, Any]:
        """
        🎯 **Main Meta-Training Loop**
        
        Execute meta-learning across diverse creator tasks.
        """
        if num_iterations is None:
            num_iterations = self.config.max_meta_iterations
        
        start_time = datetime.now()
        best_performance = 0
        
        try:
            for iteration in range(num_iterations):
                # Generate task batch
                tasks = self.task_generator.generate_task_batch(self.config.meta_batch_size)
                
                # Meta-update
                if self.config.adaptation_method == 'maml':
                    metrics = self.optimizer.meta_update(tasks)
                else:  # reptile
                    metrics = self.optimizer.reptile_update(tasks)
                
                # Record metrics
                self.training_history['meta_loss'].append(metrics.get('meta_loss', 0))
                self.training_history['inner_loss'].append(metrics.get('inner_loss', 0))
                self.training_history['accuracy'].append(metrics.get('accuracy', 0))
                
                # Track per-creator performance
                for task in tasks:
                    creator_type = task.creator_type
                    self.training_history['creator_type_performance'][creator_type].append(
                        metrics.get('accuracy', 0)
                    )
                
                # Log progress
                if iteration % 100 == 0:
                    avg_accuracy = np.mean(self.training_history['accuracy'][-100:])
                    self.logger.info(
                        f"Meta-iteration {iteration}: Avg Accuracy: {avg_accuracy:.4f}, "
                        f"Meta Loss: {metrics.get('meta_loss', 0):.4f}"
                    )
                
                # Save best model
                current_performance = metrics.get('accuracy', 0)
                if current_performance > best_performance:
                    best_performance = current_performance
                    await self.model_registry.register_model(
                        model=self.meta_network,
                        model_name="meta_learning_network",
                        model_version=f"iteration_{iteration}",
                        metrics=metrics
                    )
                
                # Early stopping check
                if iteration > 1000 and len(self.training_history['accuracy']) > 500:
                    recent_performance = np.mean(self.training_history['accuracy'][-500:])
                    older_performance = np.mean(self.training_history['accuracy'][-1000:-500])
                    
                    if recent_performance <= older_performance:
                        self.logger.info(f"Early stopping at iteration {iteration}")
                        break
            
            end_time = datetime.now()
            training_duration = (end_time - start_time).total_seconds()
            
            # Final results
            results = {
                'meta_learning_method': self.config.adaptation_method,
                'total_iterations': iteration + 1,
                'best_accuracy': best_performance,
                'final_accuracy': self.training_history['accuracy'][-1] if self.training_history['accuracy'] else 0,
                'training_duration_seconds': training_duration,
                'creator_type_performances': {
                    creator: np.mean(performances) 
                    for creator, performances in self.training_history['creator_type_performance'].items()
                },
                'adaptation_speed': self.calculate_adaptation_speed(),
                'config': self.config.__dict__
            }
            
            # Log to performance monitor
            await self.performance_monitor.log_metrics(
                model_id="meta_learning_network",
                metrics={
                    'meta_learning_accuracy': best_performance,
                    'adaptation_speed': results['adaptation_speed'],
                    'training_efficiency': best_performance / training_duration * 3600
                }
            )
            
            self.logger.info(f"Meta-training completed. Best accuracy: {best_performance:.4f}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in meta_train: {e}")
            raise
    
    async def rapid_adapt(self, new_creator_data: List[Dict], creator_type: str, num_adaptation_steps: int = 5) -> Dict[str, Any]:
        """
        ⚡ **Rapid Adaptation to New Creator**
        
        Quickly adapt meta-learned model to new creator with minimal examples.
        """
        try:
            start_time = datetime.now()
            
            # Create adaptation task
            adaptation_task = Task(
                task_id=f"adaptation_{creator_type}_{datetime.now().timestamp()}",
                creator_type=creator_type,
                content_type=self._infer_content_type(new_creator_data),
                support_set=new_creator_data[:self.config.support_shots],
                query_set=new_creator_data[self.config.support_shots:],
                metadata={'adaptation': True}
            )
            
            # Store original weights
            original_weights = self.meta_network.clone_parameters()
            
            # Rapid adaptation using inner loop
            adapted_weights, adaptation_loss = self.optimizer.inner_loop_update(
                adaptation_task, 
                fast_weights=original_weights
            )
            
            # Test adaptation quality
            self.meta_network.set_parameters(adapted_weights)
            
            if adaptation_task.query_set:
                query_x = torch.stack([
                    torch.tensor(item['content']['features'], dtype=torch.float32)
                    for item in adaptation_task.query_set
                ])
                query_y = torch.tensor([item['label'] for item in adaptation_task.query_set], dtype=torch.long)
                
                with torch.no_grad():
                    query_logits, _ = self.meta_network(query_x)
                    predictions = torch.argmax(query_logits, dim=1)
                    adaptation_accuracy = (predictions == query_y).float().mean().item()
            else:
                adaptation_accuracy = 0.0
            
            end_time = datetime.now()
            adaptation_time = (end_time - start_time).total_seconds()
            
            # Results
            results = {
                'creator_type': creator_type,
                'adaptation_accuracy': adaptation_accuracy,
                'adaptation_loss': adaptation_loss,
                'adaptation_time_seconds': adaptation_time,
                'num_support_examples': len(adaptation_task.support_set),
                'num_query_examples': len(adaptation_task.query_set),
                'adaptation_speed': adaptation_accuracy / adaptation_time if adaptation_time > 0 else 0
            }
            
            # Restore original weights
            self.meta_network.set_parameters(original_weights)
            
            self.logger.info(
                f"Rapid adaptation completed for {creator_type}: "
                f"Accuracy: {adaptation_accuracy:.4f}, Time: {adaptation_time:.2f}s"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in rapid_adapt: {e}")
            raise
    
    def calculate_adaptation_speed(self) -> float:
        """Calculate average adaptation speed metric."""
        if not self.training_history['accuracy']:
            return 0.0
        
        # Measure how quickly accuracy improves in early iterations
        early_iterations = min(100, len(self.training_history['accuracy']))
        if early_iterations < 10:
            return 0.0
        
        early_accuracies = self.training_history['accuracy'][:early_iterations]
        improvement_rate = np.polyfit(range(early_iterations), early_accuracies, 1)[0]
        
        return max(0, improvement_rate * 1000)  # Scale for interpretability
    
    def _infer_content_type(self, data: List[Dict]) -> str:
        """Infer content type from data structure."""
        if not data:
            return 'unknown'
        
        sample = data[0]['content']
        if 'text_features' in sample:
            return 'text'
        elif 'image_features' in sample:
            return 'image'
        elif 'features' in sample and len(sample['features']) == 128:
            return 'audio'
        else:
            return 'multimodal'
    
    async def evaluate_generalization(self, test_creators: List[str]) -> Dict[str, Any]:
        """
        📊 **Evaluate Meta-Learning Generalization**
        
        Test generalization to completely new creator types.
        """
        results = {}
        
        for creator_type in test_creators:
            # Generate test tasks
            test_tasks = [
                self.task_generator.generate_task(creator_type) 
                for _ in range(10)
            ]
            
            accuracies = []
            adaptation_times = []
            
            for task in test_tasks:
                # Test rapid adaptation
                creator_data = task.support_set + task.query_set
                adaptation_result = await self.rapid_adapt(creator_data, creator_type)
                
                accuracies.append(adaptation_result['adaptation_accuracy'])
                adaptation_times.append(adaptation_result['adaptation_time_seconds'])
            
            results[creator_type] = {
                'mean_accuracy': np.mean(accuracies),
                'std_accuracy': np.std(accuracies),
                'mean_adaptation_time': np.mean(adaptation_times),
                'generalization_score': np.mean(accuracies) / (1 + np.std(accuracies))
            }
        
        overall_generalization = np.mean([r['generalization_score'] for r in results.values()])
        results['overall_generalization'] = overall_generalization
        
        return results
    
    def get_training_insights(self) -> Dict[str, Any]:
        """Get detailed training insights and visualizations."""
        return {
            'training_history': self.training_history,
            'model_parameters': sum(p.numel() for p in self.meta_network.parameters()),
            'device': str(self.device),
            'supported_creators': list(self.training_history['creator_type_performance'].keys()),
            'adaptation_method': self.config.adaptation_method
        }

# Factory for creating meta-learning systems
class MetaLearningFactory:
    """Factory for creating optimized meta-learning systems."""
    
    @staticmethod
    def create_for_creators(creator_types: List[str], **config_overrides) -> MetaLearningSystem:
        """Create meta-learning system optimized for specific creator types."""
        config = MetaLearningConfig(
            creator_types=creator_types,
            **config_overrides
        )
        return MetaLearningSystem(config)
    
    @staticmethod
    def create_fast_adaptation_system() -> MetaLearningSystem:
        """Create system optimized for fast adaptation."""
        config = MetaLearningConfig(
            meta_lr=5e-4,
            inner_lr=1e-1,
            inner_steps=3,
            adaptation_method='reptile',  # Faster than MAML
            second_order=False
        )
        return MetaLearningSystem(config)
    
    @staticmethod
    def create_high_accuracy_system() -> MetaLearningSystem:
        """Create system optimized for high accuracy."""
        config = MetaLearningConfig(
            meta_lr=1e-4,
            inner_lr=1e-2,
            inner_steps=10,
            adaptation_method='maml',
            second_order=True,
            meta_batch_size=32
        )
        return MetaLearningSystem(config)

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Example usage
    async def demo_meta_learning():
        config = MetaLearningConfig(
            creator_types=['musician', 'blogger', 'photographer'],
            meta_lr=1e-3,
            inner_steps=5,
            max_meta_iterations=1000
        )
        
        system = MetaLearningSystem(config)
        
        # Meta-training
        results = await system.meta_train(num_iterations=100)
        print(f"Meta-training results: {results}")
        
        # Test rapid adaptation
        new_creator_data = [
            {"content": {"features": torch.randn(512)}, "label": 0}
            for _ in range(20)
        ]
        
        adaptation_results = await system.rapid_adapt(new_creator_data, "new_creator_type")
        print(f"Adaptation results: {adaptation_results}")
    
    # Run demo
    asyncio.run(demo_meta_learning())