"""Base Neural Network Infrastructure

Core infrastructure for all neural networks in the IA-Influencer-Agent platform.
Provides standardized architecture, training, and deployment capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import json
import pickle
from datetime import datetime

logger = logging.getLogger(__name__)


class NetworkType(Enum):
    """Neural network architecture types"""
    TRANSFORMER = "transformer"
    CNN = "convolutional"
    RNN = "recurrent"  
    GAN = "generative_adversarial"
    VAE = "variational_autoencoder"
    DIFFUSION = "diffusion_model"
    HYBRID = "hybrid_architecture"


class DeviceType(Enum):
    """Supported computation devices"""
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"  # Apple Silicon


@dataclass
class NetworkConfig:
    """Neural network configuration"""
    
    # Architecture parameters
    input_dim: int
    hidden_dims: List[int]
    output_dim: int
    network_type: NetworkType
    
    # Training parameters
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    dropout_rate: float = 0.1
    weight_decay: float = 1e-5
    
    # Device and optimization
    device: DeviceType = DeviceType.CUDA
    mixed_precision: bool = True
    gradient_clipping: float = 1.0
    
    # Model specific
    attention_heads: Optional[int] = None
    num_layers: int = 6
    activation: str = "relu"
    normalization: str = "layer_norm"
    
    # Regularization
    use_dropout: bool = True
    use_batch_norm: bool = True
    l1_regularization: float = 0.0
    l2_regularization: float = 0.01


@dataclass  
class TrainingConfig:
    """Training process configuration"""
    
    # Data parameters
    train_split: float = 0.8
    validation_split: float = 0.1
    test_split: float = 0.1
    
    # Training strategy
    optimizer: str = "adamw"
    scheduler: str = "cosine_annealing"
    early_stopping_patience: int = 10
    early_stopping_delta: float = 1e-6
    
    # Monitoring
    log_interval: int = 100
    validation_interval: int = 500
    checkpoint_interval: int = 1000
    
    # Augmentation
    use_data_augmentation: bool = True
    augmentation_probability: float = 0.5
    
    # Advanced training
    use_gradient_accumulation: bool = False
    gradient_accumulation_steps: int = 1
    use_amp: bool = True  # Automatic Mixed Precision
    
    # Distributed training
    use_distributed: bool = False
    world_size: int = 1
    rank: int = 0


class BaseNeuralNetwork(nn.Module, ABC):
    """
    Base class for all neural networks in the platform.
    
    Provides standardized architecture, training, and inference capabilities.
    """
    
    def __init__(
        self,
        config: NetworkConfig,
        name: str = "BaseNetwork"
    ):
        super().__init__()
        self.config = config
        self.name = name
        self.device = self._get_device()
        
        # Training state
        self.training_history = []
        self.best_validation_loss = float('inf')
        self.training_step = 0
        
        # Model registry
        self.model_version = "1.0.0"
        self.created_at = datetime.now()
        
        # Initialize metrics tracking
        self.metrics = {
            'loss': [],
            'accuracy': [],
            'validation_loss': [],
            'validation_accuracy': [],
            'learning_rate': [],
            'gradient_norm': []
        }
        
        logger.info(f"Initialized {self.name} on device: {self.device}")
    
    def _get_device(self) -> torch.device:
        """Determine and return the appropriate device"""
        if self.config.device == DeviceType.CUDA and torch.cuda.is_available():
            return torch.device("cuda")
        elif self.config.device == DeviceType.MPS and torch.backends.mps.is_available():
            return torch.device("mps")
        else:
            return torch.device("cpu")
    
    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network"""
        pass
    
    @abstractmethod
    def compute_loss(
        self, 
        predictions: torch.Tensor, 
        targets: torch.Tensor
    ) -> torch.Tensor:
        """Compute loss for the specific network type"""
        pass
    
    def configure_optimizer(self) -> optim.Optimizer:
        """Configure optimizer for training"""
        if hasattr(self.config, 'optimizer_type'):
            optimizer_type = self.config.optimizer_type
        else:
            optimizer_type = "adamw"
            
        if optimizer_type.lower() == "adamw":
            return optim.AdamW(
                self.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )
        elif optimizer_type.lower() == "adam":
            return optim.Adam(
                self.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )
        elif optimizer_type.lower() == "sgd":
            return optim.SGD(
                self.parameters(),
                lr=self.config.learning_rate,
                momentum=0.9,
                weight_decay=self.config.weight_decay
            )
        else:
            raise ValueError(f"Unsupported optimizer: {optimizer_type}")
    
    def configure_scheduler(
        self, 
        optimizer: optim.Optimizer,
        num_training_steps: int
    ) -> Optional[optim.lr_scheduler._LRScheduler]:
        """Configure learning rate scheduler"""
        if hasattr(self.config, 'scheduler_type'):
            scheduler_type = self.config.scheduler_type
        else:
            scheduler_type = "cosine_annealing"
            
        if scheduler_type.lower() == "cosine_annealing":
            return optim.lr_scheduler.CosineAnnealingLR(
                optimizer, T_max=num_training_steps
            )
        elif scheduler_type.lower() == "step":
            return optim.lr_scheduler.StepLR(
                optimizer, step_size=num_training_steps // 3, gamma=0.1
            )
        elif scheduler_type.lower() == "exponential":
            return optim.lr_scheduler.ExponentialLR(
                optimizer, gamma=0.95
            )
        return None
    
    def train_epoch(
        self, 
        dataloader: DataLoader,
        optimizer: optim.Optimizer,
        scheduler: Optional[optim.lr_scheduler._LRScheduler] = None
    ) -> Dict[str, float]:
        """Train for one epoch"""
        self.train()
        epoch_loss = 0.0
        epoch_accuracy = 0.0
        num_batches = 0
        
        for batch_idx, batch in enumerate(dataloader):
            # Move batch to device
            if isinstance(batch, (list, tuple)):
                batch = [item.to(self.device) if hasattr(item, 'to') else item 
                        for item in batch]
                inputs, targets = batch[0], batch[1]
            else:
                inputs = batch.to(self.device)
                targets = None
            
            # Forward pass
            optimizer.zero_grad()
            outputs = self.forward(inputs)
            
            # Compute loss
            if targets is not None:
                loss = self.compute_loss(outputs, targets)
            else:
                # For unsupervised learning
                loss = self.compute_unsupervised_loss(outputs, inputs)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            if self.config.gradient_clipping > 0:
                torch.nn.utils.clip_grad_norm_(
                    self.parameters(), self.config.gradient_clipping
                )
            
            optimizer.step()
            if scheduler:
                scheduler.step()
            
            # Update metrics
            epoch_loss += loss.item()
            if targets is not None:
                accuracy = self.compute_accuracy(outputs, targets)
                epoch_accuracy += accuracy
            
            num_batches += 1
            self.training_step += 1
            
            # Log progress
            if batch_idx % 100 == 0:
                logger.debug(
                    f"Batch {batch_idx}/{len(dataloader)}: "
                    f"Loss = {loss.item():.6f}"
                )
        
        return {
            'loss': epoch_loss / num_batches,
            'accuracy': epoch_accuracy / num_batches if targets is not None else 0.0,
            'learning_rate': optimizer.param_groups[0]['lr']
        }
    
    def compute_accuracy(
        self, 
        predictions: torch.Tensor, 
        targets: torch.Tensor
    ) -> float:
        """Compute accuracy metric"""
        if len(predictions.shape) > 1 and predictions.shape[1] > 1:
            # Classification
            predicted = torch.argmax(predictions, dim=1)
            correct = (predicted == targets).float().mean()
            return correct.item()
        else:
            # Regression - use R² score
            ss_res = torch.sum((targets - predictions) ** 2)
            ss_tot = torch.sum((targets - torch.mean(targets)) ** 2)
            r_squared = 1 - (ss_res / ss_tot)
            return r_squared.item()
    
    def compute_unsupervised_loss(
        self, 
        outputs: torch.Tensor, 
        inputs: torch.Tensor
    ) -> torch.Tensor:
        """Compute unsupervised loss (reconstruction, etc.)"""
        return nn.MSELoss()(outputs, inputs)
    
    def validate(
        self, 
        dataloader: DataLoader
    ) -> Dict[str, float]:
        """Validate the model"""
        self.eval()
        total_loss = 0.0
        total_accuracy = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch in dataloader:
                if isinstance(batch, (list, tuple)):
                    batch = [item.to(self.device) if hasattr(item, 'to') else item 
                            for item in batch]
                    inputs, targets = batch[0], batch[1]
                else:
                    inputs = batch.to(self.device)
                    targets = None
                
                outputs = self.forward(inputs)
                
                if targets is not None:
                    loss = self.compute_loss(outputs, targets)
                    accuracy = self.compute_accuracy(outputs, targets)
                else:
                    loss = self.compute_unsupervised_loss(outputs, inputs)
                    accuracy = 0.0
                
                total_loss += loss.item()
                total_accuracy += accuracy
                num_batches += 1
        
        return {
            'validation_loss': total_loss / num_batches,
            'validation_accuracy': total_accuracy / num_batches
        }
    
    def save_model(self, path: Union[str, Path]) -> None:
        """Save model checkpoint"""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            'model_state_dict': self.state_dict(),
            'config': self.config,
            'metrics': self.metrics,
            'training_history': self.training_history,
            'model_version': self.model_version,
            'created_at': self.created_at,
            'training_step': self.training_step
        }
        
        torch.save(checkpoint, path / 'model.pt')
        
        # Save config separately as JSON
        config_dict = {
            'network_type': self.config.network_type.value,
            'input_dim': self.config.input_dim,
            'hidden_dims': self.config.hidden_dims,
            'output_dim': self.config.output_dim,
            'learning_rate': self.config.learning_rate,
            'batch_size': self.config.batch_size
        }
        
        with open(path / 'config.json', 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Model saved to {path}")
    
    @classmethod
    def load_model(cls, path: Union[str, Path]) -> 'BaseNeuralNetwork':
        """Load model from checkpoint"""
        path = Path(path)
        checkpoint = torch.load(path / 'model.pt', map_location='cpu')
        
        # Create instance with saved config
        instance = cls(checkpoint['config'])
        instance.load_state_dict(checkpoint['model_state_dict'])
        instance.metrics = checkpoint.get('metrics', {})
        instance.training_history = checkpoint.get('training_history', [])
        instance.model_version = checkpoint.get('model_version', '1.0.0')
        instance.training_step = checkpoint.get('training_step', 0)
        
        logger.info(f"Model loaded from {path}")
        return instance


class ModelRegistry:
    """Registry for managing trained models"""
    
    def __init__(self, registry_path: Union[str, Path]):
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.registry_path / 'models.json'
        self.models = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Any]:
        """Load model registry from disk"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_registry(self) -> None:
        """Save model registry to disk"""
        with open(self.registry_file, 'w') as f:
            json.dump(self.models, f, indent=2, default=str)
    
    def register_model(
        self,
        name: str,
        model: BaseNeuralNetwork,
        description: str = "",
        tags: List[str] = None
    ) -> None:
        """Register a trained model"""
        model_info = {
            'name': name,
            'description': description,
            'tags': tags or [],
            'model_version': model.model_version,
            'created_at': model.created_at,
            'config': {
                'network_type': model.config.network_type.value,
                'input_dim': model.config.input_dim,
                'output_dim': model.config.output_dim
            },
            'metrics': model.metrics,
            'training_step': model.training_step
        }
        
        self.models[name] = model_info
        self._save_registry()
        
        # Save model
        model_path = self.registry_path / name
        model.save_model(model_path)
        
        logger.info(f"Registered model: {name}")
    
    def get_model(self, name: str) -> Optional[Dict[str, Any]]:
        """Get model information"""
        return self.models.get(name)
    
    def list_models(self, tag: str = None) -> List[str]:
        """List available models, optionally filtered by tag"""
        if tag:
            return [
                name for name, info in self.models.items()
                if tag in info.get('tags', [])
            ]
        return list(self.models.keys())
    
    def remove_model(self, name: str) -> None:
        """Remove model from registry"""
        if name in self.models:
            del self.models[name]
            self._save_registry()
            
            # Remove model files
            model_path = self.registry_path / name
            if model_path.exists():
                import shutil
                shutil.rmtree(model_path)
            
            logger.info(f"Removed model: {name}")


class InferenceEngine:
    """High-performance inference engine for deployed models"""
    
    def __init__(
        self,
        model: BaseNeuralNetwork,
        batch_size: int = 1,
        use_jit: bool = True
    ):
        self.model = model
        self.batch_size = batch_size
        self.device = model.device
        
        # Optimize for inference
        self.model.eval()
        
        # JIT compilation for better performance
        if use_jit:
            try:
                # Create sample input for tracing
                sample_input = torch.randn(
                    1, model.config.input_dim, 
                    device=self.device
                )
                self.model = torch.jit.trace(self.model, sample_input)
                logger.info("Model compiled with TorchScript JIT")
            except Exception as e:
                logger.warning(f"JIT compilation failed: {e}")
        
        # Warm up
        self._warmup()
    
    def _warmup(self) -> None:
        """Warm up the model for consistent inference timing"""
        with torch.no_grad():
            dummy_input = torch.randn(
                self.batch_size, 
                self.model.config.input_dim,
                device=self.device
            )
            
            # Run a few forward passes
            for _ in range(5):
                _ = self.model(dummy_input)
        
        logger.info("Inference engine warmed up")
    
    def predict(
        self, 
        inputs: Union[torch.Tensor, np.ndarray],
        return_numpy: bool = True
    ) -> Union[torch.Tensor, np.ndarray]:
        """Run inference on input data"""
        
        # Convert to tensor if needed
        if isinstance(inputs, np.ndarray):
            inputs = torch.from_numpy(inputs).float()
        
        # Move to device
        inputs = inputs.to(self.device)
        
        # Ensure batch dimension
        if len(inputs.shape) == 1:
            inputs = inputs.unsqueeze(0)
        
        # Run inference
        with torch.no_grad():
            outputs = self.model(inputs)
        
        # Convert to numpy if requested
        if return_numpy:
            return outputs.cpu().numpy()
        
        return outputs
    
    def batch_predict(
        self,
        inputs: Union[torch.Tensor, np.ndarray],
        batch_size: Optional[int] = None
    ) -> np.ndarray:
        """Run batch inference on large inputs"""
        
        if batch_size is None:
            batch_size = self.batch_size
        
        # Convert to tensor
        if isinstance(inputs, np.ndarray):
            inputs = torch.from_numpy(inputs).float()
        
        results = []
        
        for i in range(0, len(inputs), batch_size):
            batch = inputs[i:i + batch_size].to(self.device)
            
            with torch.no_grad():
                batch_outputs = self.model(batch)
            
            results.append(batch_outputs.cpu().numpy())
        
        return np.concatenate(results, axis=0)
