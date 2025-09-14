"""
Federated Learning Module - Privacy-Preserving Machine Learning

Advanced federated learning orchestration system with privacy-preserving capabilities,
secure aggregation, and distributed training coordination.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import numpy as np
import hashlib
import secrets
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
import threading
from collections import defaultdict, deque
import weakref

logger = logging.getLogger(__name__)


class PrivacyLevel(Enum):
    """Privacy protection levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class AggregationStrategy(Enum):
    """Federated aggregation strategies"""
    FEDAVG = "federated_averaging"
    WEIGHTED_AVERAGE = "weighted_average"
    MEDIAN_AGGREGATION = "median_aggregation"
    BYZANTINE_ROBUST = "byzantine_robust"
    SECURE_AGGREGATION = "secure_aggregation"
    DIFFERENTIAL_PRIVATE = "differential_private"


class ClientStatus(Enum):
    """Federated client status"""
    ONLINE = "online"
    OFFLINE = "offline"
    TRAINING = "training"
    SYNCING = "syncing"
    ERROR = "error"
    SUSPENDED = "suspended"


@dataclass
class PrivacyConfig:
    """Privacy configuration for federated learning"""
    privacy_level: PrivacyLevel = PrivacyLevel.MEDIUM
    differential_privacy: bool = True
    epsilon: float = 1.0  # Privacy budget
    delta: float = 1e-5  # Privacy parameter
    noise_multiplier: float = 1.0
    max_grad_norm: float = 1.0
    secure_aggregation: bool = True
    client_sampling_rate: float = 0.1
    min_clients_for_update: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "privacy_level": self.privacy_level.value,
            "differential_privacy": self.differential_privacy,
            "epsilon": self.epsilon,
            "delta": self.delta,
            "noise_multiplier": self.noise_multiplier,
            "max_grad_norm": self.max_grad_norm,
            "secure_aggregation": self.secure_aggregation,
            "client_sampling_rate": self.client_sampling_rate,
            "min_clients_for_update": self.min_clients_for_update
        }


@dataclass
class FederatedMetrics:
    """Federated learning metrics"""
    round_number: int = 0
    participating_clients: int = 0
    global_accuracy: float = 0.0
    convergence_rate: float = 0.0
    privacy_cost: float = 0.0
    communication_overhead_mb: float = 0.0
    training_time_seconds: float = 0.0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "round_number": self.round_number,
            "participating_clients": self.participating_clients,
            "global_accuracy": self.global_accuracy,
            "convergence_rate": self.convergence_rate,
            "privacy_cost": self.privacy_cost,
            "communication_overhead_mb": self.communication_overhead_mb,
            "training_time_seconds": self.training_time_seconds,
            "last_updated": self.last_updated.isoformat()
        }


class FederatedClient:
    """Federated learning client"""
    
    def __init__(self, client_id -> None: str, data_size -> None: int = 1000) -> None:
        self.client_id = client_id
        self.data_size = data_size
        self.status = ClientStatus.OFFLINE
        self.local_model_weights: Optional[Dict[str, np.ndarray]] = None
        self.local_metrics = {
            'accuracy': 0.0,
            'loss': float('inf'),
            'data_samples': data_size,
            'last_update': datetime.utcnow()
        }
        self.privacy_budget_used = 0.0
        self.total_rounds_participated = 0
        self.last_communication = datetime.utcnow()
        
        logger.info(f"FederatedClient {client_id} initialized with {data_size} data samples")
    
    async def local_training(self, global_weights: Dict[str, np.ndarray], 
                           epochs: int = 1) -> Dict[str, Any]:
        """Perform local training"""
        self.status = ClientStatus.TRAINING
        start_time = time.time()
        
        try:
            # Simulate local training
            await asyncio.sleep(np.random.uniform(0.1, 0.5))  # Simulate training time
            
            # Create updated weights (simulate training)
            updated_weights = {}
            for layer_name, weights in global_weights.items():
                # Add noise to simulate training updates
                noise = np.random.normal(0, 0.01, weights.shape)
                updated_weights[layer_name] = weights + noise
            
            # Simulate metrics improvement
            accuracy_improvement = np.random.uniform(0.001, 0.01)
            self.local_metrics['accuracy'] = min(1.0, self.local_metrics['accuracy'] + accuracy_improvement)
            self.local_metrics['loss'] = max(0.01, self.local_metrics['loss'] * 0.99)
            self.local_metrics['last_update'] = datetime.utcnow()
            
            training_time = time.time() - start_time
            self.total_rounds_participated += 1
            
            self.status = ClientStatus.ONLINE
            
            return {
                'client_id': self.client_id,
                'updated_weights': updated_weights,
                'local_metrics': self.local_metrics.copy(),
                'training_time': training_time,
                'data_samples': self.data_size
            }
        
        except Exception as e:
            self.status = ClientStatus.ERROR
            logger.error(f"Local training failed for client {self.client_id}: {e}")
            raise
    
    async def apply_differential_privacy(self, weights: Dict[str, np.ndarray], 
                                       privacy_config: PrivacyConfig) -> Dict[str, np.ndarray]:
        """Apply differential privacy to model weights"""
        if not privacy_config.differential_privacy:
            return weights
        
        # Calculate sensitivity and noise scale
        sensitivity = privacy_config.max_grad_norm
        noise_scale = sensitivity * privacy_config.noise_multiplier
        
        # Add noise to weights
        private_weights = {}
        total_privacy_cost = 0
        
        for layer_name, layer_weights in weights.items():
            # Add Gaussian noise
            noise = np.random.normal(0, noise_scale, layer_weights.shape)
            private_weights[layer_name] = layer_weights + noise
            
            # Update privacy cost
            total_privacy_cost += privacy_config.epsilon / len(weights)
        
        self.privacy_budget_used += total_privacy_cost
        
        logger.debug(f"Applied differential privacy to client {self.client_id}, "
                    f"privacy cost: {total_privacy_cost:.6f}")
        
        return private_weights
    
    def get_client_info(self) -> Dict[str, Any]:
        """Get client information"""
        return {
            'client_id': self.client_id,
            'status': self.status.value,
            'data_size': self.data_size,
            'local_metrics': self.local_metrics.copy(),
            'privacy_budget_used': self.privacy_budget_used,
            'total_rounds_participated': self.total_rounds_participated,
            'last_communication': self.last_communication.isoformat()
        }


class FederatedServer:
    """Federated learning server"""
    
    def __init__(self, server_id -> None: str, privacy_config -> None: PrivacyConfig) -> None:
        self.server_id = server_id
        self.privacy_config = privacy_config
        self.global_model_weights: Dict[str, np.ndarray] = {}
        self.round_number = 0
        self.clients: Dict[str, FederatedClient] = {}
        self.aggregation_history: List[Dict[str, Any]] = []
        self.is_training = False
        self._lock = threading.RLock()
        
        # Initialize global model
        self._initialize_global_model()
        
        logger.info(f"FederatedServer {server_id} initialized")
    
    def _initialize_global_model(self) -> None:
        """Initialize global model weights"""
        # Simulate a simple neural network structure
        self.global_model_weights = {
            'layer1_weights': np.random.normal(0, 0.1, (784, 128)),
            'layer1_bias': np.zeros(128),
            'layer2_weights': np.random.normal(0, 0.1, (128, 64)),
            'layer2_bias': np.zeros(64),
            'output_weights': np.random.normal(0, 0.1, (64, 10)),
            'output_bias': np.zeros(10)
        }
        
        logger.info("Global model initialized")
    
    def register_client(self, client: FederatedClient) -> bool:
        """Register a federated client"""
        with self._lock:
            if client.client_id in self.clients:
                logger.warning(f"Client {client.client_id} already registered")
                return False
            
            self.clients[client.client_id] = client
            client.status = ClientStatus.ONLINE
            client.last_communication = datetime.utcnow()
            
            logger.info(f"Registered client {client.client_id} "
                       f"(total clients: {len(self.clients)})")
            return True
    
    def unregister_client(self, client_id: str) -> bool:
        """Unregister a federated client"""
        with self._lock:
            if client_id not in self.clients:
                return False
            
            del self.clients[client_id]
            logger.info(f"Unregistered client {client_id} "
                       f"(remaining clients: {len(self.clients)})")
            return True
    
    async def federated_round(self, strategy: AggregationStrategy = AggregationStrategy.FEDAVG) -> FederatedMetrics:
        """Execute one round of federated learning"""
        if self.is_training:
            raise RuntimeError("Federated round already in progress")
        
        self.is_training = True
        start_time = time.time()
        
        try:
            # Select clients for this round
            selected_clients = await self._select_clients()
            
            if len(selected_clients) < self.privacy_config.min_clients_for_update:
                raise RuntimeError(f"Not enough clients for update. "
                                 f"Need {self.privacy_config.min_clients_for_update}, "
                                 f"got {len(selected_clients)}")
            
            # Send global model to selected clients
            logger.info(f"Starting federated round {self.round_number + 1} "
                       f"with {len(selected_clients)} clients")
            
            # Collect client updates
            client_updates = await self._collect_client_updates(selected_clients)
            
            # Aggregate updates
            aggregated_weights = await self._aggregate_updates(client_updates, strategy)
            
            # Update global model
            self.global_model_weights = aggregated_weights
            self.round_number += 1
            
            # Calculate metrics
            metrics = await self._calculate_round_metrics(client_updates, start_time)
            
            # Store aggregation history
            self.aggregation_history.append({
                'round': self.round_number,
                'clients': len(selected_clients),
                'strategy': strategy.value,
                'metrics': metrics.to_dict(),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            logger.info(f"Federated round {self.round_number} completed. "
                       f"Global accuracy: {metrics.global_accuracy:.4f}")
            
            return metrics
        
        finally:
            self.is_training = False
    
    async def _select_clients(self) -> List[str]:
        """Select clients for federated round"""
        with self._lock:
            online_clients = [
                client_id for client_id, client in self.clients.items()
                if client.status == ClientStatus.ONLINE
            ]
        
        # Random sampling based on sampling rate
        num_selected = max(
            self.privacy_config.min_clients_for_update,
            int(len(online_clients) * self.privacy_config.client_sampling_rate)
        )
        
        if len(online_clients) < num_selected:
            selected = online_clients
        else:
            selected = np.random.choice(
                online_clients, 
                size=num_selected, 
                replace=False
            ).tolist()
        
        logger.debug(f"Selected {len(selected)} clients from {len(online_clients)} online clients")
        return selected
    
    async def _collect_client_updates(self, selected_clients: List[str]) -> List[Dict[str, Any]]:
        """Collect updates from selected clients"""
        update_tasks = []
        
        for client_id in selected_clients:
            client = self.clients[client_id]
            task = asyncio.create_task(
                client.local_training(self.global_model_weights)
            )
            update_tasks.append((client_id, task))
        
        client_updates = []
        for client_id, task in update_tasks:
            try:
                update = await task
                
                # Apply differential privacy if enabled
                if self.privacy_config.differential_privacy:
                    client = self.clients[client_id]
                    update['updated_weights'] = await client.apply_differential_privacy(
                        update['updated_weights'], 
                        self.privacy_config
                    )
                
                client_updates.append(update)
                
            except Exception as e:
                logger.error(f"Failed to collect update from client {client_id}: {e}")
                # Mark client as error state
                if client_id in self.clients:
                    self.clients[client_id].status = ClientStatus.ERROR
        
        return client_updates
    
    async def _aggregate_updates(self, client_updates: List[Dict[str, Any]], 
                               strategy: AggregationStrategy) -> Dict[str, np.ndarray]:
        """Aggregate client updates"""
        if not client_updates:
            return self.global_model_weights
        
        if strategy == AggregationStrategy.FEDAVG:
            return await self._federated_averaging(client_updates)
        elif strategy == AggregationStrategy.WEIGHTED_AVERAGE:
            return await self._weighted_averaging(client_updates)
        elif strategy == AggregationStrategy.MEDIAN_AGGREGATION:
            return await self._median_aggregation(client_updates)
        elif strategy == AggregationStrategy.BYZANTINE_ROBUST:
            return await self._byzantine_robust_aggregation(client_updates)
        else:
            # Default to FedAvg
            return await self._federated_averaging(client_updates)
    
    async def _federated_averaging(self, client_updates: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """Standard federated averaging (FedAvg)"""
        if not client_updates:
            return self.global_model_weights
        
        # Calculate total samples
        total_samples = sum(update['data_samples'] for update in client_updates)
        
        # Initialize aggregated weights
        aggregated_weights = {}
        
        for layer_name in self.global_model_weights.keys():
            weighted_sum = np.zeros_like(self.global_model_weights[layer_name])
            
            for update in client_updates:
                weight = update['data_samples'] / total_samples
                layer_weights = update['updated_weights'][layer_name]
                weighted_sum += weight * layer_weights
            
            aggregated_weights[layer_name] = weighted_sum
        
        return aggregated_weights
    
    async def _weighted_averaging(self, client_updates: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """Weighted averaging based on client performance"""
        if not client_updates:
            return self.global_model_weights
        
        # Calculate weights based on local accuracy
        total_weight = 0
        weights = []
        
        for update in client_updates:
            accuracy = update['local_metrics']['accuracy']
            data_samples = update['data_samples']
            # Weight by accuracy and data size
            weight = accuracy * np.sqrt(data_samples)
            weights.append(weight)
            total_weight += weight
        
        # Normalize weights
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(client_updates)] * len(client_updates)
        
        # Aggregate with normalized weights
        aggregated_weights = {}
        
        for layer_name in self.global_model_weights.keys():
            weighted_sum = np.zeros_like(self.global_model_weights[layer_name])
            
            for update, weight in zip(client_updates, weights):
                layer_weights = update['updated_weights'][layer_name]
                weighted_sum += weight * layer_weights
            
            aggregated_weights[layer_name] = weighted_sum
        
        return aggregated_weights
    
    async def _median_aggregation(self, client_updates: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """Median-based aggregation for robustness"""
        if not client_updates:
            return self.global_model_weights
        
        aggregated_weights = {}
        
        for layer_name in self.global_model_weights.keys():
            # Collect all weights for this layer
            layer_weights_list = []
            for update in client_updates:
                layer_weights_list.append(update['updated_weights'][layer_name])
            
            # Stack weights and compute median
            stacked_weights = np.stack(layer_weights_list, axis=0)
            median_weights = np.median(stacked_weights, axis=0)
            
            aggregated_weights[layer_name] = median_weights
        
        return aggregated_weights
    
    async def _byzantine_robust_aggregation(self, client_updates: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """Byzantine-robust aggregation"""
        # For simplicity, use trimmed mean (remove outliers)
        if len(client_updates) < 3:
            return await self._federated_averaging(client_updates)
        
        aggregated_weights = {}
        trim_fraction = 0.2  # Remove 20% of outliers
        
        for layer_name in self.global_model_weights.keys():
            layer_weights_list = []
            for update in client_updates:
                layer_weights_list.append(update['updated_weights'][layer_name])
            
            # Stack weights
            stacked_weights = np.stack(layer_weights_list, axis=0)
            
            # Calculate trimmed mean
            trim_count = int(len(client_updates) * trim_fraction)
            if trim_count > 0:
                # Sort along client axis and trim outliers
                sorted_weights = np.sort(stacked_weights, axis=0)
                trimmed_weights = sorted_weights[trim_count:-trim_count] if trim_count < len(client_updates)//2 else sorted_weights
                aggregated_weights[layer_name] = np.mean(trimmed_weights, axis=0)
            else:
                aggregated_weights[layer_name] = np.mean(stacked_weights, axis=0)
        
        return aggregated_weights
    
    async def _calculate_round_metrics(self, client_updates: List[Dict[str, Any]], 
                                     start_time: float) -> FederatedMetrics:
        """Calculate metrics for the federated round"""
        training_time = time.time() - start_time
        
        # Calculate weighted average accuracy
        total_samples = sum(update['data_samples'] for update in client_updates)
        weighted_accuracy = 0
        
        if total_samples > 0:
            for update in client_updates:
                weight = update['data_samples'] / total_samples
                accuracy = update['local_metrics']['accuracy']
                weighted_accuracy += weight * accuracy
        
        # Calculate convergence rate (simplified)
        convergence_rate = 0.0
        if len(self.aggregation_history) > 1:
            prev_accuracy = self.aggregation_history[-1]['metrics']['global_accuracy']
            convergence_rate = abs(weighted_accuracy - prev_accuracy)
        
        # Calculate privacy cost
        privacy_cost = 0.0
        if self.privacy_config.differential_privacy:
            privacy_cost = self.privacy_config.epsilon * len(client_updates)
        
        # Calculate communication overhead (simplified)
        communication_overhead = len(client_updates) * 10.0  # MB per client
        
        return FederatedMetrics(
            round_number=self.round_number + 1,
            participating_clients=len(client_updates),
            global_accuracy=weighted_accuracy,
            convergence_rate=convergence_rate,
            privacy_cost=privacy_cost,
            communication_overhead_mb=communication_overhead,
            training_time_seconds=training_time
        )
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get comprehensive server statistics"""
        with self._lock:
            client_status_counts = defaultdict(int)
            total_data_samples = 0
            
            for client in self.clients.values():
                client_status_counts[client.status.value] += 1
                total_data_samples += client.data_size
        
        return {
            'server_id': self.server_id,
            'round_number': self.round_number,
            'total_clients': len(self.clients),
            'client_status_distribution': dict(client_status_counts),
            'total_data_samples': total_data_samples,
            'is_training': self.is_training,
            'privacy_config': self.privacy_config.to_dict(),
            'aggregation_history_length': len(self.aggregation_history)
        }


class PrivacyPreservingLearning:
    """Advanced privacy-preserving learning mechanisms"""
    
    def __init__(self, privacy_config -> None: PrivacyConfig) -> None:
        self.privacy_config = privacy_config
        self.privacy_accountant = {
            'total_epsilon_used': 0.0,
            'total_delta_used': 0.0,
            'queries_count': 0
        }
    
    async def apply_differential_privacy(self, data: np.ndarray, 
                                       sensitivity: float = 1.0) -> np.ndarray:
        """Apply differential privacy to data"""
        if not self.privacy_config.differential_privacy:
            return data
        
        # Calculate noise scale
        noise_scale = sensitivity / self.privacy_config.epsilon
        
        # Add Laplace noise
        noise = np.random.laplace(0, noise_scale, data.shape)
        private_data = data + noise
        
        # Update privacy accountant
        self.privacy_accountant['total_epsilon_used'] += self.privacy_config.epsilon
        self.privacy_accountant['total_delta_used'] += self.privacy_config.delta
        self.privacy_accountant['queries_count'] += 1
        
        return private_data
    
    async def secure_aggregation(self, client_updates: List[Dict[str, np.ndarray]]) -> Dict[str, np.ndarray]:
        """Perform secure aggregation"""
        if len(client_updates) < 2:
            raise ValueError("Need at least 2 clients for secure aggregation")
        
        # Simulate secure aggregation protocol
        # In practice, this would use cryptographic techniques
        
        aggregated = {}
        for layer_name in client_updates[0].keys():
            layer_sum = np.zeros_like(client_updates[0][layer_name])
            
            for update in client_updates:
                # Add noise for security
                noise = np.random.normal(0, 0.001, update[layer_name].shape)
                layer_sum += update[layer_name] + noise
            
            # Average
            aggregated[layer_name] = layer_sum / len(client_updates)
        
        return aggregated
    
    def get_privacy_budget_status(self) -> Dict[str, Any]:
        """Get privacy budget status"""
        return {
            'privacy_config': self.privacy_config.to_dict(),
            'privacy_accountant': self.privacy_accountant.copy(),
            'budget_remaining': {
                'epsilon': max(0, 10.0 - self.privacy_accountant['total_epsilon_used']),  # Assume budget of 10
                'delta': max(0, 1e-3 - self.privacy_accountant['total_delta_used'])  # Assume budget of 1e-3
            }
        }


class FederatedOrchestrator:
    """Main orchestrator for federated learning"""
    
    def __init__(self, privacy_config -> None: PrivacyConfig) -> None:
        self.privacy_config = privacy_config
        self.servers: Dict[str, FederatedServer] = {}
        self.privacy_engine = PrivacyPreservingLearning(privacy_config)
        self.global_stats = {
            'total_servers': 0,
            'total_clients': 0,
            'total_rounds_completed': 0,
            'global_privacy_budget_used': 0.0
        }
        
        logger.info("FederatedOrchestrator initialized")
    
    async def create_server(self, server_id: str, 
                          privacy_config: Optional[PrivacyConfig] = None) -> FederatedServer:
        """Create federated server"""
        if server_id in self.servers:
            raise ValueError(f"Server {server_id} already exists")
        
        config = privacy_config or self.privacy_config
        server = FederatedServer(server_id, config)
        self.servers[server_id] = server
        
        self.global_stats['total_servers'] = len(self.servers)
        
        logger.info(f"Created federated server {server_id}")
        return server
    
    async def remove_server(self, server_id: str) -> bool:
        """Remove federated server"""
        if server_id not in self.servers:
            return False
        
        del self.servers[server_id]
        self.global_stats['total_servers'] = len(self.servers)
        
        logger.info(f"Removed federated server {server_id}")
        return True
    
    async def orchestrate_federated_learning(self, server_id: str, 
                                           rounds: int = 10,
                                           strategy: AggregationStrategy = AggregationStrategy.FEDAVG) -> List[FederatedMetrics]:
        """Orchestrate complete federated learning process"""
        if server_id not in self.servers:
            raise ValueError(f"Server {server_id} not found")
        
        server = self.servers[server_id]
        metrics_history = []
        
        logger.info(f"Starting federated learning orchestration for {rounds} rounds")
        
        for round_num in range(rounds):
            try:
                metrics = await server.federated_round(strategy)
                metrics_history.append(metrics)
                
                self.global_stats['total_rounds_completed'] += 1
                self.global_stats['global_privacy_budget_used'] += metrics.privacy_cost
                
                logger.info(f"Round {round_num + 1}/{rounds} completed. "
                           f"Accuracy: {metrics.global_accuracy:.4f}")
                
                # Check convergence
                if len(metrics_history) > 5 and self._check_convergence(metrics_history[-5:]):
                    logger.info("Convergence detected, stopping early")
                    break
                
            except Exception as e:
                logger.error(f"Round {round_num + 1} failed: {e}")
                break
        
        logger.info(f"Federated learning orchestration completed. "
                   f"Final accuracy: {metrics_history[-1].global_accuracy:.4f}")
        
        return metrics_history
    
    def _check_convergence(self, recent_metrics: List[FederatedMetrics]) -> bool:
        """Check if the model has converged"""
        if len(recent_metrics) < 3:
            return False
        
        # Check if accuracy improvement is minimal
        accuracies = [m.global_accuracy for m in recent_metrics]
        improvement = max(accuracies) - min(accuracies)
        
        return improvement < 0.001  # 0.1% threshold
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global orchestration statistics"""
        total_clients = sum(len(server.clients) for server in self.servers.values())
        self.global_stats['total_clients'] = total_clients
        
        return {
            **self.global_stats,
            'privacy_budget_status': self.privacy_engine.get_privacy_budget_status(),
            'active_servers': [server_id for server_id in self.servers.keys()],
            'server_details': {
                server_id: server.get_server_stats() 
                for server_id, server in self.servers.items()
            }
        }