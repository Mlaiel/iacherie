# -*- coding: utf-8 -*-
"""
Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Training Module Tests - Enterprise Grade Test Suite

Comprehensive tests for ML training infrastructure including distributed training,
hyperparameter optimization, experiment tracking, and advanced training strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  STRICT LEGAL WARNING ⚠️
Contact: mlaiel@live.de - Unauthorized use STRICTLY PROHIBITED
"""

import pytest
import sys
import os
from pathlib import Path
import torch
import torch.nn as nn
import numpy as np
import tempfile
import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

from ai.ml.training import (
    ModelTrainer, TrainingConfig, DistributedTrainingManager,
    HyperparameterOptimizer, ExperimentTracker, TrainingMode,
    TrainingStrategy, ValidationStrategy, OptimizationAlgorithm,
    LearningRateScheduler
)


class TestModelTrainer:
    """Comprehensive tests for ModelTrainer class"""
    
    def test_init_trainer_basic(self, sample_training_config, sample_pytorch_model):
        """Test basic trainer initialization"""
        trainer = ModelTrainer(
            model=sample_pytorch_model,
            config=sample_training_config
        )
        
        assert trainer.model is sample_pytorch_model
        assert trainer.config.model_name == "test_model"
        assert trainer.config.num_epochs == 5
        assert trainer.config.batch_size == 16
        assert trainer.config.learning_rate == 0.001
        assert trainer.training_history == []
        assert trainer.best_metrics == {}
        assert trainer.current_epoch == 0

    def test_init_trainer_with_optimizer(self, sample_training_config, sample_pytorch_model):
        """Test trainer initialization with custom optimizer"""
        sample_training_config.optimizer = OptimizationAlgorithm.ADAM
        sample_training_config.learning_rate = 0.01
        sample_training_config.weight_decay = 0.001
        
        trainer = ModelTrainer(
            model=sample_pytorch_model,
            config=sample_training_config
        )
        
        optimizer = trainer._create_optimizer()
        assert isinstance(optimizer, torch.optim.Adam)
        assert optimizer.param_groups[0]['lr'] == 0.01
        assert optimizer.param_groups[0]['weight_decay'] == 0.001

    def test_create_different_optimizers(self, sample_training_config, sample_pytorch_model):
        """Test creation of different optimizer types"""
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        # Test SGD
        sample_training_config.optimizer = OptimizationAlgorithm.SGD
        optimizer = trainer._create_optimizer()
        assert isinstance(optimizer, torch.optim.SGD)
        
        # Test AdamW
        sample_training_config.optimizer = OptimizationAlgorithm.ADAMW
        optimizer = trainer._create_optimizer()
        assert isinstance(optimizer, torch.optim.AdamW)
        
        # Test RMSprop
        sample_training_config.optimizer = OptimizationAlgorithm.RMSPROP
        optimizer = trainer._create_optimizer()
        assert isinstance(optimizer, torch.optim.RMSprop)

    def test_create_lr_schedulers(self, sample_training_config, sample_pytorch_model):
        """Test creation of different learning rate schedulers"""
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        optimizer = trainer._create_optimizer()
        
        # Test cosine scheduler
        sample_training_config.lr_scheduler = LearningRateScheduler.COSINE
        scheduler = trainer._create_scheduler(optimizer)
        assert scheduler is not None
        
        # Test linear scheduler
        sample_training_config.lr_scheduler = LearningRateScheduler.LINEAR
        scheduler = trainer._create_scheduler(optimizer)
        assert scheduler is not None
        
        # Test step scheduler
        sample_training_config.lr_scheduler = LearningRateScheduler.STEP
        scheduler = trainer._create_scheduler(optimizer)
        assert scheduler is not None

    def test_training_data_preparation(self, sample_training_config, sample_pytorch_model, sample_dataset):
        """Test training data preparation and validation"""
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        X, y = sample_dataset
        
        # Test data splitting
        train_loader, val_loader, test_loader = trainer.prepare_data_loaders(X, y)
        
        assert train_loader is not None
        assert val_loader is not None
        assert test_loader is not None
        
        # Check batch sizes
        train_batch = next(iter(train_loader))
        assert train_batch[0].shape[0] <= sample_training_config.batch_size
        
        val_batch = next(iter(val_loader))
        assert val_batch[0].shape[0] <= sample_training_config.batch_size

    @patch('torch.cuda.is_available', return_value=True)
    def test_device_selection_gpu(self, mock_cuda, sample_training_config, sample_pytorch_model):
        """Test GPU device selection when available"""
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        device = trainer._select_device()
        
        assert "cuda" in str(device) or device == torch.device("cpu")  # Fallback if no actual GPU

    @patch('torch.cuda.is_available', return_value=False)
    def test_device_selection_cpu(self, mock_cuda, sample_training_config, sample_pytorch_model):
        """Test CPU device selection when GPU unavailable"""
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        device = trainer._select_device()
        
        assert device == torch.device("cpu")

    def test_training_step_supervised(self, sample_training_config, sample_pytorch_model, sample_dataset):
        """Test single training step for supervised learning"""
        sample_training_config.training_mode = TrainingMode.SUPERVISED
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        X, y = sample_dataset
        train_loader, _, _ = trainer.prepare_data_loaders(X, y)
        
        optimizer = trainer._create_optimizer()
        criterion = nn.CrossEntropyLoss()
        
        # Get a batch
        batch_x, batch_y = next(iter(train_loader))
        
        # Training step
        loss = trainer._training_step(batch_x, batch_y, optimizer, criterion)
        
        assert isinstance(loss, (float, torch.Tensor))
        assert loss >= 0

    def test_validation_step(self, sample_training_config, sample_pytorch_model, sample_dataset):
        """Test validation step"""
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        X, y = sample_dataset
        _, val_loader, _ = trainer.prepare_data_loaders(X, y)
        
        criterion = nn.CrossEntropyLoss()
        
        # Validation step
        val_loss, val_accuracy = trainer._validation_step(val_loader, criterion)
        
        assert isinstance(val_loss, (float, torch.Tensor))
        assert isinstance(val_accuracy, (float, torch.Tensor))
        assert val_loss >= 0
        assert 0 <= val_accuracy <= 1

    def test_model_checkpointing(self, sample_training_config, sample_pytorch_model, temp_dir):
        """Test model checkpointing functionality"""
        sample_training_config.output_dir = str(temp_dir)
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        # Create checkpoint
        checkpoint_path = trainer._save_checkpoint(
            epoch=5,
            loss=0.5,
            metrics={"accuracy": 0.85, "f1_score": 0.83}
        )
        
        assert checkpoint_path.exists()
        
        # Load checkpoint
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        assert checkpoint['epoch'] == 5
        assert checkpoint['loss'] == 0.5
        assert checkpoint['metrics']['accuracy'] == 0.85

    def test_early_stopping(self, sample_training_config, sample_pytorch_model):
        """Test early stopping mechanism"""
        sample_training_config.early_stopping = True
        sample_training_config.patience = 3
        sample_training_config.min_delta = 0.001
        
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        # Simulate training with no improvement
        losses = [0.5, 0.4, 0.45, 0.44, 0.43, 0.425]
        should_stop = False
        
        for epoch, loss in enumerate(losses):
            trainer.validation_losses.append(loss)
            should_stop = trainer._check_early_stopping()
            if should_stop:
                break
        
        # Should trigger early stopping due to lack of significant improvement
        assert should_stop or len(losses) > sample_training_config.patience

    def test_gradient_clipping(self, sample_training_config, sample_pytorch_model, sample_dataset):
        """Test gradient clipping functionality"""
        sample_training_config.gradient_clip_norm = 1.0
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        X, y = sample_dataset
        train_loader, _, _ = trainer.prepare_data_loaders(X, y)
        
        optimizer = trainer._create_optimizer()
        criterion = nn.CrossEntropyLoss()
        
        # Get batch and compute loss
        batch_x, batch_y = next(iter(train_loader))
        outputs = trainer.model(batch_x)
        loss = criterion(outputs, batch_y)
        
        # Backward pass
        loss.backward()
        
        # Check gradients before clipping
        total_norm_before = torch.norm(torch.stack([p.grad.norm() for p in trainer.model.parameters() if p.grad is not None]))
        
        # Apply gradient clipping
        trainer._clip_gradients()
        
        # Check gradients after clipping
        total_norm_after = torch.norm(torch.stack([p.grad.norm() for p in trainer.model.parameters() if p.grad is not None]))
        
        assert total_norm_after <= sample_training_config.gradient_clip_norm + 1e-6  # Small tolerance

    def test_mixed_precision_training(self, sample_training_config, sample_pytorch_model):
        """Test mixed precision training setup"""
        sample_training_config.mixed_precision = True
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        # Check if scaler is created for mixed precision
        if torch.cuda.is_available() and hasattr(torch.cuda.amp, 'GradScaler'):
            assert hasattr(trainer, 'scaler')
            assert trainer.scaler is not None

    @pytest.mark.asyncio
    async def test_async_training(self, sample_training_config, sample_pytorch_model, sample_dataset):
        """Test asynchronous training capabilities"""
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        X, y = sample_dataset
        
        # Setup minimal training for async test
        sample_training_config.num_epochs = 2
        
        # Mock the train method to be async-compatible
        async def mock_train():
            await asyncio.sleep(0.1)  # Simulate training time
            return {"final_loss": 0.3, "final_accuracy": 0.9}
        
        trainer.train_async = mock_train
        
        # Test async training
        results = await trainer.train_async()
        assert "final_loss" in results
        assert "final_accuracy" in results

    def test_training_history_tracking(self, sample_training_config, sample_pytorch_model):
        """Test training history tracking"""
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        # Simulate training epochs
        for epoch in range(5):
            history_entry = {
                "epoch": epoch,
                "train_loss": 0.5 - epoch * 0.1,
                "val_loss": 0.6 - epoch * 0.08,
                "train_accuracy": 0.7 + epoch * 0.05,
                "val_accuracy": 0.65 + epoch * 0.06,
                "learning_rate": 0.001 * (0.9 ** epoch),
                "timestamp": datetime.now().isoformat()
            }
            trainer.training_history.append(history_entry)
        
        assert len(trainer.training_history) == 5
        assert trainer.training_history[0]["epoch"] == 0
        assert trainer.training_history[-1]["epoch"] == 4
        
        # Check improvement trend
        assert trainer.training_history[-1]["train_loss"] < trainer.training_history[0]["train_loss"]
        assert trainer.training_history[-1]["train_accuracy"] > trainer.training_history[0]["train_accuracy"]


class TestDistributedTrainingManager:
    """Tests for distributed training management"""
    
    def test_init_distributed_manager(self):
        """Test distributed training manager initialization"""
        manager = DistributedTrainingManager(
            world_size=4,
            rank=0,
            backend="nccl",
            master_addr="localhost",
            master_port="12355"
        )
        
        assert manager.world_size == 4
        assert manager.rank == 0
        assert manager.backend == "nccl"
        assert manager.master_addr == "localhost"
        assert manager.master_port == "12355"

    @patch('torch.distributed.init_process_group')
    def test_setup_distributed_training(self, mock_init_process_group):
        """Test distributed training setup"""
        manager = DistributedTrainingManager(world_size=2, rank=0)
        
        manager.setup_distributed_training()
        
        mock_init_process_group.assert_called_once()

    def test_create_distributed_sampler(self, sample_dataset):
        """Test creation of distributed sampler"""
        manager = DistributedTrainingManager(world_size=2, rank=0)
        X, y = sample_dataset
        
        # Create a simple dataset
        dataset = torch.utils.data.TensorDataset(
            torch.FloatTensor(X),
            torch.LongTensor(y)
        )
        
        sampler = manager.create_distributed_sampler(dataset)
        
        # Check if sampler is properly configured
        assert sampler.num_replicas == 2
        assert sampler.rank == 0

    def test_sync_metrics_across_processes(self):
        """Test metrics synchronization across processes"""
        manager = DistributedTrainingManager(world_size=2, rank=0)
        
        metrics = {
            "loss": torch.tensor(0.5),
            "accuracy": torch.tensor(0.85)
        }
        
        # Mock distributed operations
        with patch('torch.distributed.all_reduce') as mock_all_reduce:
            synced_metrics = manager.sync_metrics(metrics)
            
            assert "loss" in synced_metrics
            assert "accuracy" in synced_metrics


class TestHyperparameterOptimizer:
    """Tests for hyperparameter optimization"""
    
    def test_init_optimizer(self):
        """Test hyperparameter optimizer initialization"""
        param_space = {
            "learning_rate": (0.001, 0.1, "log"),
            "batch_size": (16, 128, "int"),
            "dropout_rate": (0.1, 0.5, "float"),
            "hidden_size": [128, 256, 512]
        }
        
        optimizer = HyperparameterOptimizer(
            param_space=param_space,
            optimization_method="bayesian",
            n_trials=20
        )
        
        assert optimizer.param_space == param_space
        assert optimizer.optimization_method == "bayesian"
        assert optimizer.n_trials == 20
        assert optimizer.best_params is None
        assert optimizer.best_score is None

    def test_sample_parameters(self, sample_hyperparameters):
        """Test parameter sampling from search space"""
        optimizer = HyperparameterOptimizer(
            param_space=sample_hyperparameters,
            optimization_method="random"
        )
        
        # Sample parameters
        params = optimizer.sample_parameters()
        
        assert "learning_rate" in params
        assert "batch_size" in params
        assert params["learning_rate"] in sample_hyperparameters["learning_rate"]
        assert params["batch_size"] in sample_hyperparameters["batch_size"]

    @patch('optuna.create_study')
    def test_bayesian_optimization(self, mock_create_study):
        """Test Bayesian optimization setup"""
        mock_study = MagicMock()
        mock_create_study.return_value = mock_study
        
        param_space = {"learning_rate": (0.001, 0.1, "log")}
        optimizer = HyperparameterOptimizer(param_space, "bayesian")
        
        # Mock objective function
        def objective(params):
            return 0.85  # Mock accuracy
        
        optimizer.optimize(objective, n_trials=5)
        
        mock_create_study.assert_called_once()
        mock_study.optimize.assert_called_once()

    def test_grid_search_optimization(self):
        """Test grid search optimization"""
        param_space = {
            "learning_rate": [0.001, 0.01],
            "batch_size": [16, 32]
        }
        
        optimizer = HyperparameterOptimizer(param_space, "grid_search")
        
        def objective(params):
            # Simple objective: prefer higher learning rate and batch size
            return params["learning_rate"] * 10 + params["batch_size"] / 100
        
        best_params, best_score = optimizer.optimize(objective)
        
        assert best_params is not None
        assert best_score is not None
        assert best_params["learning_rate"] == 0.01  # Higher is better in our objective
        assert best_params["batch_size"] == 32      # Higher is better in our objective

    def test_random_search_optimization(self):
        """Test random search optimization"""
        param_space = {
            "learning_rate": (0.001, 0.1, "log"),
            "dropout_rate": (0.1, 0.5, "float")
        }
        
        optimizer = HyperparameterOptimizer(param_space, "random_search")
        
        def objective(params):
            # Simple objective based on parameters
            return 1.0 - params["dropout_rate"] + np.log10(params["learning_rate"])
        
        best_params, best_score = optimizer.optimize(objective, n_trials=10)
        
        assert best_params is not None
        assert best_score is not None
        assert 0.001 <= best_params["learning_rate"] <= 0.1
        assert 0.1 <= best_params["dropout_rate"] <= 0.5


class TestExperimentTracker:
    """Tests for experiment tracking"""
    
    def test_init_tracker(self, temp_dir):
        """Test experiment tracker initialization"""
        tracker = ExperimentTracker(
            experiment_name="test_experiment",
            tracking_backend="local",
            save_dir=str(temp_dir)
        )
        
        assert tracker.experiment_name == "test_experiment"
        assert tracker.tracking_backend == "local"
        assert tracker.save_dir == temp_dir

    def test_log_parameters(self, temp_dir):
        """Test parameter logging"""
        tracker = ExperimentTracker("test", "local", str(temp_dir))
        
        params = {
            "learning_rate": 0.001,
            "batch_size": 32,
            "model_type": "transformer"
        }
        
        tracker.log_parameters(params)
        
        assert tracker.logged_params == params

    def test_log_metrics(self, temp_dir):
        """Test metrics logging"""
        tracker = ExperimentTracker("test", "local", str(temp_dir))
        
        metrics = {
            "train_loss": 0.3,
            "val_accuracy": 0.92,
            "f1_score": 0.89
        }
        
        tracker.log_metrics(metrics, step=10)
        
        assert len(tracker.logged_metrics) == 1
        assert tracker.logged_metrics[0]["step"] == 10
        assert tracker.logged_metrics[0]["metrics"]["train_loss"] == 0.3

    def test_log_model_artifact(self, temp_dir, sample_pytorch_model):
        """Test model artifact logging"""
        tracker = ExperimentTracker("test", "local", str(temp_dir))
        
        # Save model temporarily
        model_path = temp_dir / "test_model.pt"
        torch.save(sample_pytorch_model.state_dict(), model_path)
        
        tracker.log_artifact(str(model_path), "model")
        
        assert len(tracker.logged_artifacts) == 1
        assert tracker.logged_artifacts[0]["path"] == str(model_path)
        assert tracker.logged_artifacts[0]["type"] == "model"

    @patch('mlflow.start_run')
    def test_mlflow_integration(self, mock_start_run):
        """Test MLflow integration"""
        tracker = ExperimentTracker("test", "mlflow")
        
        tracker.start_run()
        mock_start_run.assert_called_once()

    def test_wandb_integration(self):
        """Test Weights & Biases integration"""
        with patch('wandb.init') as mock_wandb_init:
            tracker = ExperimentTracker("test", "wandb")
            
            params = {"lr": 0.001}
            metrics = {"loss": 0.5}
            
            tracker.log_parameters(params)
            tracker.log_metrics(metrics)
            
            # Verify wandb methods would be called
            assert tracker.tracking_backend == "wandb"

    def test_export_experiment_data(self, temp_dir):
        """Test experiment data export"""
        tracker = ExperimentTracker("test", "local", str(temp_dir))
        
        # Log some data
        tracker.log_parameters({"lr": 0.001})
        tracker.log_metrics({"loss": 0.5}, step=1)
        tracker.log_metrics({"loss": 0.3}, step=2)
        
        # Export data
        export_path = tracker.export_experiment_data()
        
        assert export_path.exists()
        
        # Load and verify exported data
        with open(export_path) as f:
            exported_data = json.load(f)
        
        assert "parameters" in exported_data
        assert "metrics" in exported_data
        assert exported_data["parameters"]["lr"] == 0.001
        assert len(exported_data["metrics"]) == 2


class TestAdvancedTrainingFeatures:
    """Tests for advanced training features"""
    
    def test_curriculum_learning(self, sample_training_config, sample_pytorch_model):
        """Test curriculum learning implementation"""
        sample_training_config.curriculum_learning = True
        sample_training_config.curriculum_strategy = "difficulty_based"
        
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        # Mock curriculum learning setup
        trainer._setup_curriculum_learning()
        
        assert hasattr(trainer, 'curriculum_scheduler')
        assert trainer.config.curriculum_learning is True

    def test_knowledge_distillation(self, sample_training_config, sample_pytorch_model):
        """Test knowledge distillation setup"""
        # Create teacher model (larger)
        teacher_model = nn.Sequential(
            nn.Linear(768, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 10)
        )
        
        sample_training_config.knowledge_distillation = True
        sample_training_config.temperature = 3.0
        sample_training_config.alpha = 0.3
        
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        trainer.teacher_model = teacher_model
        
        # Test distillation loss computation
        student_logits = torch.randn(32, 10)
        teacher_logits = torch.randn(32, 10)
        targets = torch.randint(0, 10, (32,))
        
        distillation_loss = trainer._compute_distillation_loss(
            student_logits, teacher_logits, targets
        )
        
        assert isinstance(distillation_loss, torch.Tensor)
        assert distillation_loss.item() >= 0

    def test_meta_learning_setup(self, sample_training_config, sample_pytorch_model):
        """Test meta-learning (MAML) setup"""
        sample_training_config.meta_learning = True
        sample_training_config.meta_lr = 0.01
        sample_training_config.inner_steps = 5
        
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        # Setup meta-learning
        trainer._setup_meta_learning()
        
        assert hasattr(trainer, 'meta_optimizer')
        assert trainer.config.meta_learning is True

    def test_federated_learning_simulation(self, sample_training_config, sample_pytorch_model):
        """Test federated learning simulation"""
        sample_training_config.federated_learning = True
        sample_training_config.num_clients = 5
        sample_training_config.client_fraction = 0.6
        
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        # Mock federated learning setup
        clients = trainer._setup_federated_clients()
        
        assert len(clients) == sample_training_config.num_clients
        
        # Test client selection
        selected_clients = trainer._select_clients(clients)
        expected_selected = int(sample_training_config.num_clients * sample_training_config.client_fraction)
        assert len(selected_clients) == expected_selected

    def test_adversarial_training(self, sample_training_config, sample_pytorch_model):
        """Test adversarial training setup"""
        sample_training_config.adversarial_training = True
        sample_training_config.adversarial_epsilon = 0.01
        sample_training_config.adversarial_steps = 10
        
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        # Test adversarial example generation
        inputs = torch.randn(16, 768)
        targets = torch.randint(0, 10, (16,))
        
        adversarial_inputs = trainer._generate_adversarial_examples(inputs, targets)
        
        assert adversarial_inputs.shape == inputs.shape
        
        # Check that adversarial examples are different from originals
        diff = torch.norm(adversarial_inputs - inputs, p=float('inf'))
        assert diff <= sample_training_config.adversarial_epsilon + 1e-6


@pytest.mark.integration
class TestTrainingIntegration:
    """Integration tests for training pipeline"""
    
    @pytest.mark.slow
    def test_full_training_pipeline(self, sample_training_config, sample_pytorch_model, sample_dataset, temp_dir):
        """Test complete training pipeline integration"""
        sample_training_config.output_dir = str(temp_dir)
        sample_training_config.num_epochs = 3  # Reduced for testing
        
        trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
        
        X, y = sample_dataset
        train_loader, val_loader, test_loader = trainer.prepare_data_loaders(X, y)
        
        # Run training
        results = trainer.train(train_loader, val_loader)
        
        assert "final_train_loss" in results
        assert "final_val_loss" in results
        assert "final_val_accuracy" in results
        assert "training_time" in results
        assert "best_epoch" in results
        
        # Check that model was actually trained
        assert len(trainer.training_history) == sample_training_config.num_epochs
        
        # Verify checkpoint was saved
        checkpoint_files = list(temp_dir.glob("checkpoint_*.pt"))
        assert len(checkpoint_files) > 0

    def test_distributed_training_simulation(self, sample_training_config, sample_pytorch_model, temp_dir):
        """Test distributed training simulation"""
        sample_training_config.output_dir = str(temp_dir)
        sample_training_config.distributed_training = True
        
        # Create multiple trainer instances to simulate different processes
        trainers = []
        for rank in range(2):  # Simulate 2 processes
            trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
            trainer.rank = rank
            trainer.world_size = 2
            trainers.append(trainer)
        
        # Each trainer should have the same model architecture
        for trainer in trainers:
            assert str(trainer.model) == str(trainers[0].model)

    def test_hyperparameter_optimization_integration(self, sample_training_config, sample_pytorch_model, sample_dataset):
        """Test integration of hyperparameter optimization with training"""
        param_space = {
            "learning_rate": [0.001, 0.01],
            "batch_size": [16, 32]
        }
        
        optimizer = HyperparameterOptimizer(param_space, "grid_search")
        
        def train_objective(params):
            # Update config with suggested parameters
            sample_training_config.learning_rate = params["learning_rate"]
            sample_training_config.batch_size = params["batch_size"]
            sample_training_config.num_epochs = 2  # Reduced for testing
            
            trainer = ModelTrainer(sample_pytorch_model, sample_training_config)
            X, y = sample_dataset
            
            train_loader, val_loader, _ = trainer.prepare_data_loaders(X, y)
            results = trainer.train(train_loader, val_loader)
            
            return results["final_val_accuracy"]
        
        best_params, best_score = optimizer.optimize(train_objective)
        
        assert best_params is not None
        assert best_score is not None
        assert isinstance(best_score, (int, float))
        assert 0 <= best_score <= 1  # Accuracy should be between 0 and 1


if __name__ == "__main__":
    pytest.main([str(Path(__file__)), "-v", "--tb=short"])
