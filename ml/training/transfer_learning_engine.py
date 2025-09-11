"""
🤖 **Transfer Learning Engine - Advanced Model Fine-tuning**

Ersteller: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. Alle Rechte vorbehalten.
Version: 1.0.0

**⚠️ WARNUNG:** Dieser Code ist urheberrechtlich geschützt und vertraulich.

Enterprise transfer learning engine for domain-specific fine-tuning of pre-trained models
for creator content analysis across multiple modalities (audio, video, image, text).
"""

import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass
from pathlib import Path
import json
from datetime import datetime
import torch.optim as optim
from transformers import AutoModel, AutoTokenizer, AutoImageProcessor
import torchaudio.transforms as audio_transforms
from torch.utils.data import DataLoader, Dataset

# Ainflue ML Core Imports
try:
    from ..model_registry.mlflow_registry import MLflowRegistry
except ImportError:
    MLflowRegistry = None

try:
    from ..feature_stores.feature_store import FeatureStore
except ImportError:
    FeatureStore = None

try:
    from ..monitoring.performance_monitor import PerformanceMonitor
except ImportError:
    PerformanceMonitor = None

@dataclass
class TransferLearningConfig:
    """Configuration for transfer learning tasks."""
    source_model_path: str
    target_domain: str  # 'music', 'blog', 'photo', 'video'
    freeze_layers: List[str]
    learning_rate: float = 1e-4
    num_epochs: int = 50
    batch_size: int = 32
    gradient_accumulation_steps: int = 1
    warmup_steps: int = 1000
    weight_decay: float = 0.01
    dropout_rate: float = 0.1
    label_smoothing: float = 0.1

@dataclass
class FineTuningStrategy:
    """Fine-tuning strategy configuration."""
    strategy_type: str  # 'gradual_unfreezing', 'discriminative_lr', 'layer_wise_adaptation'
    freeze_schedule: Dict[int, List[str]]  # epoch -> layers to unfreeze
    learning_rates: Dict[str, float]  # layer_group -> learning_rate
    adaptation_method: str = 'lora'  # 'lora', 'adapter', 'full'

class CreatorSpecificDataset(Dataset):
    """Dataset wrapper for creator-specific content."""
    
    def __init__(self, data: List[Dict], content_type: str, tokenizer=None, transform=None):
        self.data = data
        self.content_type = content_type
        self.tokenizer = tokenizer
        self.transform = transform
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        if self.content_type == 'text':
            inputs = self.tokenizer(
                item['content'], 
                truncation=True, 
                padding='max_length', 
                max_length=512,
                return_tensors='pt'
            )
            return {
                'input_ids': inputs['input_ids'].squeeze(),
                'attention_mask': inputs['attention_mask'].squeeze(),
                'labels': torch.tensor(item['label'], dtype=torch.long)
            }
        elif self.content_type == 'audio':
            # Audio preprocessing for music content
            waveform = torch.tensor(item['waveform'], dtype=torch.float32)
            if self.transform:
                waveform = self.transform(waveform)
            return {
                'waveform': waveform,
                'labels': torch.tensor(item['label'], dtype=torch.long)
            }
        else:
            # Image/video preprocessing
            image = torch.tensor(item['pixels'], dtype=torch.float32)
            if self.transform:
                image = self.transform(image)
            return {
                'pixel_values': image,
                'labels': torch.tensor(item['label'], dtype=torch.long)
            }

class LoRAAdapter(nn.Module):
    """Low-Rank Adaptation module for efficient fine-tuning."""
    
    def __init__(self, in_features: int, out_features: int, rank: int = 8, alpha: float = 32.0):
        super().__init__()
        self.rank = rank
        self.alpha = alpha
        self.lora_A = nn.Linear(in_features, rank, bias=False)
        self.lora_B = nn.Linear(rank, out_features, bias=False)
        self.scaling = alpha / rank
        
        # Initialize weights
        nn.init.kaiming_uniform_(self.lora_A.weight, a=np.sqrt(5))
        nn.init.zeros_(self.lora_B.weight)
    
    def forward(self, x):
        return self.lora_B(self.lora_A(x)) * self.scaling

class TransferLearningEngine:
    """
    🎯 **Enterprise Transfer Learning Engine**
    
    Advanced transfer learning system for fine-tuning pre-trained models
    for creator-specific tasks with domain adaptation.
    """
    
    def __init__(self, config: TransferLearningConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Initialize components
        self.model_registry = MLflowRegistry() if MLflowRegistry else None
        self.feature_store = FeatureStore() if FeatureStore else None
        self.performance_monitor = PerformanceMonitor() if PerformanceMonitor else None
        
        # Model and optimizer placeholders
        self.model = None
        self.optimizer = None
        self.scheduler = None
        self.lora_adapters = {}
        
        # Training metrics
        self.training_history = {
            'train_loss': [],
            'val_loss': [],
            'train_accuracy': [],
            'val_accuracy': [],
            'learning_rates': []
        }
        
        self.logger.info(f"TransferLearningEngine initialized for domain: {config.target_domain}")
    
    async def load_pretrained_model(self, model_name: str, model_type: str = 'transformer') -> nn.Module:
        """Load pre-trained model from various sources."""
        try:
            if model_type == 'transformer':
                # Load transformer model (BERT, RoBERTa, etc.)
                model = AutoModel.from_pretrained(model_name)
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                return model, tokenizer
            elif model_type == 'vision':
                # Load vision model (ViT, ResNet, etc.)
                from transformers import AutoModelForImageClassification
                model = AutoModelForImageClassification.from_pretrained(model_name)
                processor = AutoImageProcessor.from_pretrained(model_name)
                return model, processor
            elif model_type == 'audio':
                # Load audio model (Wav2Vec2, Whisper, etc.)
                from transformers import Wav2Vec2Model, Wav2Vec2Processor
                model = Wav2Vec2Model.from_pretrained(model_name)
                processor = Wav2Vec2Processor.from_pretrained(model_name)
                return model, processor
            else:
                raise ValueError(f"Unsupported model type: {model_type}")
                
        except Exception as e:
            self.logger.error(f"Error loading pretrained model {model_name}: {e}")
            raise
    
    def apply_lora_adaptation(self, model: nn.Module, target_modules: List[str], rank: int = 8) -> nn.Module:
        """Apply LoRA adaptation to specified modules."""
        for name, module in model.named_modules():
            if any(target in name for target in target_modules):
                if isinstance(module, nn.Linear):
                    # Replace linear layer with LoRA-adapted version
                    lora_adapter = LoRAAdapter(
                        module.in_features, 
                        module.out_features, 
                        rank=rank
                    )
                    self.lora_adapters[name] = lora_adapter
                    
                    # Create new module that combines original + LoRA
                    class LoRALinear(nn.Module):
                        def __init__(self, original, lora):
                            super().__init__()
                            self.original = original
                            self.lora = lora
                            # Freeze original weights
                            for param in self.original.parameters():
                                param.requires_grad = False
                        
                        def forward(self, x):
                            return self.original(x) + self.lora(x)
                    
                    # Replace the module
                    parent_module = model
                    module_names = name.split('.')
                    for module_name in module_names[:-1]:
                        parent_module = getattr(parent_module, module_name)
                    setattr(parent_module, module_names[-1], LoRALinear(module, lora_adapter))
        
        return model
    
    def freeze_layers(self, model: nn.Module, layers_to_freeze: List[str]):
        """Freeze specified layers in the model."""
        for name, param in model.named_parameters():
            if any(layer in name for layer in layers_to_freeze):
                param.requires_grad = False
                self.logger.debug(f"Frozen layer: {name}")
    
    def setup_discriminative_learning_rates(self, model: nn.Module, base_lr: float) -> optim.Optimizer:
        """Setup discriminative learning rates for different layer groups."""
        parameter_groups = []
        
        # Group parameters by layer depth
        layer_groups = {
            'embeddings': [],
            'early_layers': [],
            'middle_layers': [],
            'late_layers': [],
            'classifier': []
        }
        
        for name, param in model.named_parameters():
            if not param.requires_grad:
                continue
                
            if 'embedding' in name:
                layer_groups['embeddings'].append(param)
            elif any(x in name for x in ['layer.0', 'layer.1', 'layer.2', 'layer.3']):
                layer_groups['early_layers'].append(param)
            elif any(x in name for x in ['layer.4', 'layer.5', 'layer.6', 'layer.7']):
                layer_groups['middle_layers'].append(param)
            elif any(x in name for x in ['layer.8', 'layer.9', 'layer.10', 'layer.11']):
                layer_groups['late_layers'].append(param)
            else:
                layer_groups['classifier'].append(param)
        
        # Assign different learning rates
        lr_multipliers = {
            'embeddings': 0.1,
            'early_layers': 0.2,
            'middle_layers': 0.5,
            'late_layers': 0.8,
            'classifier': 1.0
        }
        
        for group_name, params in layer_groups.items():
            if params:
                parameter_groups.append({
                    'params': params,
                    'lr': base_lr * lr_multipliers[group_name],
                    'group_name': group_name
                })
        
        return optim.AdamW(parameter_groups, weight_decay=self.config.weight_decay)
    
    async def gradual_unfreezing_schedule(self, model: nn.Module, epoch: int, strategy: FineTuningStrategy):
        """Implement gradual unfreezing schedule."""
        if epoch in strategy.freeze_schedule:
            layers_to_unfreeze = strategy.freeze_schedule[epoch]
            for name, param in model.named_parameters():
                if any(layer in name for layer in layers_to_unfreeze):
                    param.requires_grad = True
                    self.logger.info(f"Unfrozen layer at epoch {epoch}: {name}")
    
    def calculate_loss(self, outputs, labels, label_smoothing: float = 0.0):
        """Calculate loss with optional label smoothing."""
        if label_smoothing > 0:
            # Label smoothing cross entropy
            num_classes = outputs.size(-1)
            with torch.no_grad():
                true_dist = torch.zeros_like(outputs)
                true_dist.fill_(label_smoothing / (num_classes - 1))
                true_dist.scatter_(1, labels.data.unsqueeze(1), 1.0 - label_smoothing)
            
            return torch.mean(torch.sum(-true_dist * torch.log_softmax(outputs, dim=-1), dim=-1))
        else:
            return nn.CrossEntropyLoss()(outputs, labels)
    
    async def train_epoch(self, model: nn.Module, dataloader: DataLoader, optimizer: optim.Optimizer, epoch: int):
        """Train for one epoch."""
        model.train()
        total_loss = 0
        correct_predictions = 0
        total_samples = 0
        
        for batch_idx, batch in enumerate(dataloader):
            # Move batch to device
            for key in batch:
                if isinstance(batch[key], torch.Tensor):
                    batch[key] = batch[key].to(self.device)
            
            optimizer.zero_grad()
            
            # Forward pass
            if 'input_ids' in batch:
                # Text model
                outputs = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'])
                logits = outputs.logits if hasattr(outputs, 'logits') else outputs.last_hidden_state.mean(dim=1)
            elif 'waveform' in batch:
                # Audio model
                outputs = model(batch['waveform'])
                logits = outputs.logits if hasattr(outputs, 'logits') else outputs.last_hidden_state.mean(dim=1)
            else:
                # Image model
                outputs = model(batch['pixel_values'])
                logits = outputs.logits if hasattr(outputs, 'logits') else outputs.last_hidden_state.mean(dim=1)
            
            # Calculate loss
            loss = self.calculate_loss(logits, batch['labels'], self.config.label_smoothing)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            # Gradient accumulation
            if (batch_idx + 1) % self.config.gradient_accumulation_steps == 0:
                optimizer.step()
                if self.scheduler:
                    self.scheduler.step()
            
            # Statistics
            total_loss += loss.item()
            predictions = torch.argmax(logits, dim=-1)
            correct_predictions += (predictions == batch['labels']).sum().item()
            total_samples += batch['labels'].size(0)
            
            # Log progress
            if batch_idx % 100 == 0:
                self.logger.info(f"Epoch {epoch}, Batch {batch_idx}, Loss: {loss.item():.4f}")
        
        avg_loss = total_loss / len(dataloader)
        accuracy = correct_predictions / total_samples
        
        self.training_history['train_loss'].append(avg_loss)
        self.training_history['train_accuracy'].append(accuracy)
        
        return avg_loss, accuracy
    
    async def validate_epoch(self, model: nn.Module, dataloader: DataLoader):
        """Validate for one epoch."""
        model.eval()
        total_loss = 0
        correct_predictions = 0
        total_samples = 0
        
        with torch.no_grad():
            for batch in dataloader:
                # Move batch to device
                for key in batch:
                    if isinstance(batch[key], torch.Tensor):
                        batch[key] = batch[key].to(self.device)
                
                # Forward pass
                if 'input_ids' in batch:
                    outputs = model(input_ids=batch['input_ids'], attention_mask=batch['attention_mask'])
                    logits = outputs.logits if hasattr(outputs, 'logits') else outputs.last_hidden_state.mean(dim=1)
                elif 'waveform' in batch:
                    outputs = model(batch['waveform'])
                    logits = outputs.logits if hasattr(outputs, 'logits') else outputs.last_hidden_state.mean(dim=1)
                else:
                    outputs = model(batch['pixel_values'])
                    logits = outputs.logits if hasattr(outputs, 'logits') else outputs.last_hidden_state.mean(dim=1)
                
                # Calculate loss
                loss = self.calculate_loss(logits, batch['labels'])
                
                # Statistics
                total_loss += loss.item()
                predictions = torch.argmax(logits, dim=-1)
                correct_predictions += (predictions == batch['labels']).sum().item()
                total_samples += batch['labels'].size(0)
        
        avg_loss = total_loss / len(dataloader)
        accuracy = correct_predictions / total_samples
        
        self.training_history['val_loss'].append(avg_loss)
        self.training_history['val_accuracy'].append(accuracy)
        
        return avg_loss, accuracy
    
    async def fine_tune_model(
        self, 
        train_data: List[Dict], 
        val_data: List[Dict],
        model_name: str,
        model_type: str = 'transformer',
        strategy: Optional[FineTuningStrategy] = None
    ) -> Dict[str, Any]:
        """
        🎯 **Main Fine-tuning Pipeline**
        
        Execute complete transfer learning with domain adaptation.
        """
        try:
            start_time = datetime.now()
            
            # Load pre-trained model
            self.model, processor = await self.load_pretrained_model(model_name, model_type)
            self.model = self.model.to(self.device)
            
            # Apply adaptation strategy
            if strategy and strategy.adaptation_method == 'lora':
                target_modules = ['query', 'key', 'value', 'dense']
                self.model = self.apply_lora_adaptation(self.model, target_modules)
            
            # Freeze initial layers
            self.freeze_layers(self.model, self.config.freeze_layers)
            
            # Setup datasets
            train_dataset = CreatorSpecificDataset(train_data, self.config.target_domain, processor)
            val_dataset = CreatorSpecificDataset(val_data, self.config.target_domain, processor)
            
            train_dataloader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True)
            val_dataloader = DataLoader(val_dataset, batch_size=self.config.batch_size, shuffle=False)
            
            # Setup optimizer and scheduler
            if strategy and strategy.strategy_type == 'discriminative_lr':
                self.optimizer = self.setup_discriminative_learning_rates(self.model, self.config.learning_rate)
            else:
                self.optimizer = optim.AdamW(
                    self.model.parameters(), 
                    lr=self.config.learning_rate, 
                    weight_decay=self.config.weight_decay
                )
            
            total_steps = len(train_dataloader) * self.config.num_epochs
            self.scheduler = optim.lr_scheduler.LinearLR(
                self.optimizer,
                start_factor=0.1,
                total_iters=self.config.warmup_steps
            )
            
            # Training loop
            best_val_accuracy = 0
            for epoch in range(self.config.num_epochs):
                self.logger.info(f"Starting epoch {epoch + 1}/{self.config.num_epochs}")
                
                # Gradual unfreezing
                if strategy and strategy.strategy_type == 'gradual_unfreezing':
                    await self.gradual_unfreezing_schedule(self.model, epoch, strategy)
                
                # Train and validate
                train_loss, train_acc = await self.train_epoch(self.model, train_dataloader, self.optimizer, epoch)
                val_loss, val_acc = await self.validate_epoch(self.model, val_dataloader)
                
                # Log metrics
                current_lr = self.optimizer.param_groups[0]['lr']
                self.training_history['learning_rates'].append(current_lr)
                
                self.logger.info(
                    f"Epoch {epoch + 1}: Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, "
                    f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}, LR: {current_lr:.6f}"
                )
                
                # Save best model
                if val_acc > best_val_accuracy:
                    best_val_accuracy = val_acc
                    if self.model_registry:
                        await self.model_registry.register_model(
                            model=self.model,
                            model_name=f"{self.config.target_domain}_transfer_learned",
                            model_version=f"epoch_{epoch+1}",
                            metrics={
                                'val_accuracy': val_acc,
                                'val_loss': val_loss,
                                'train_accuracy': train_acc,
                                'train_loss': train_loss
                            }
                        )
                
                # Early stopping
                if len(self.training_history['val_loss']) > 5:
                    if val_loss > max(self.training_history['val_loss'][-5:]):
                        self.logger.info(f"Early stopping at epoch {epoch + 1}")
                        break
            
            end_time = datetime.now()
            training_duration = (end_time - start_time).total_seconds()
            
            # Final results
            results = {
                'model_id': f"{self.config.target_domain}_transfer_learned",
                'best_val_accuracy': best_val_accuracy,
                'final_train_accuracy': self.training_history['train_accuracy'][-1],
                'training_duration_seconds': training_duration,
                'total_epochs': len(self.training_history['train_loss']),
                'config': self.config.__dict__,
                'history': self.training_history
            }
            
            # Log to performance monitor
            if self.performance_monitor:
                await self.performance_monitor.log_metrics(
                    model_id=results['model_id'],
                    metrics={
                        'transfer_learning_accuracy': best_val_accuracy,
                        'training_efficiency': best_val_accuracy / training_duration * 3600  # accuracy per hour
                    }
                )
            
            self.logger.info(f"Transfer learning completed. Best validation accuracy: {best_val_accuracy:.4f}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in fine_tune_model: {e}")
            raise
    
    async def adapt_to_creator_domain(self, creator_type: str, content_samples: List[Dict]) -> Dict[str, Any]:
        """
        🎨 **Creator-Specific Domain Adaptation**
        
        Specialized adaptation for different creator types.
        """
        domain_configs = {
            'musician': {
                'model_name': 'facebook/wav2vec2-base',
                'model_type': 'audio',
                'freeze_layers': ['feature_extractor'],
                'learning_rate': 5e-5
            },
            'blogger': {
                'model_name': 'bert-base-uncased',
                'model_type': 'transformer', 
                'freeze_layers': ['embeddings'],
                'learning_rate': 2e-5
            },
            'photographer': {
                'model_name': 'google/vit-base-patch16-224',
                'model_type': 'vision',
                'freeze_layers': ['patch_embeddings'],
                'learning_rate': 1e-4
            }
        }
        
        if creator_type not in domain_configs:
            raise ValueError(f"Unsupported creator type: {creator_type}")
        
        # Update config for specific creator domain
        domain_config = domain_configs[creator_type]
        self.config.target_domain = creator_type
        self.config.freeze_layers = domain_config['freeze_layers']
        self.config.learning_rate = domain_config['learning_rate']
        
        # Split data
        split_idx = int(0.8 * len(content_samples))
        train_data = content_samples[:split_idx]
        val_data = content_samples[split_idx:]
        
        # Fine-tune with LoRA strategy
        strategy = FineTuningStrategy(
            strategy_type='gradual_unfreezing',
            freeze_schedule={5: ['encoder'], 10: ['classifier']},
            learning_rates={'encoder': 1e-5, 'classifier': 1e-4},
            adaptation_method='lora'
        )
        
        return await self.fine_tune_model(
            train_data=train_data,
            val_data=val_data,
            model_name=domain_config['model_name'],
            model_type=domain_config['model_type'],
            strategy=strategy
        )
    
    def get_training_metrics(self) -> Dict[str, Any]:
        """Get comprehensive training metrics."""
        return {
            'training_history': self.training_history,
            'model_parameters': sum(p.numel() for p in self.model.parameters() if p.requires_grad),
            'lora_adapters': len(self.lora_adapters),
            'device': str(self.device)
        }

# Usage example and factory
class TransferLearningFactory:
    """Factory for creating transfer learning engines with domain-specific configurations."""
    
    @staticmethod
    def create_for_domain(domain: str, **kwargs) -> TransferLearningEngine:
        """Create transfer learning engine optimized for specific creator domain."""
        base_config = TransferLearningConfig(
            source_model_path="",
            target_domain=domain,
            freeze_layers=[],
            **kwargs
        )
        return TransferLearningEngine(base_config)
    
    @staticmethod
    def create_multi_domain_engine(domains: List[str]) -> Dict[str, TransferLearningEngine]:
        """Create multiple engines for cross-domain transfer learning."""
        engines = {}
        for domain in domains:
            engines[domain] = TransferLearningFactory.create_for_domain(domain)
        return engines

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Example usage
    async def demo_transfer_learning():
        config = TransferLearningConfig(
            source_model_path="bert-base-uncased",
            target_domain="blogger",
            freeze_layers=["embeddings"],
            learning_rate=2e-5,
            num_epochs=10
        )
        
        engine = TransferLearningEngine(config)
        
        # Mock data for demonstration
        sample_data = [
            {"content": "This is a sample blog post about technology.", "label": 0},
            {"content": "Music review: The latest album by...", "label": 1}
        ]
        
        results = await engine.adapt_to_creator_domain("blogger", sample_data)
        print(f"Transfer learning results: {results}")
    
    # Run demo
    asyncio.run(demo_transfer_learning())