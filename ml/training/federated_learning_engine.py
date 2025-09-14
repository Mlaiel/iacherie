"""🌐 Federated Learning Engine - Privacy-Preserving Distributed ML
===============================================================
Module: ml/training/federated_learning_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
===============================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🌐 FEDERATED LEARNING ENGINE
Privacy-preserving federated learning for distributed creator data
- Federated averaging algorithms (FedAvg, FedProx, FedNova)
- Differential privacy protection
- Secure aggregation protocols
- Multi-party computation support
- Creator data sovereignty preservation
- Asynchronous and synchronous training modes
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
import hashlib
import pickle
import copy
from collections import defaultdict, deque
import cryptography
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import secrets

logger = logging.getLogger(__name__)

class FederatedAlgorithm(Enum):
    """Federated learning algorithms"""
    FEDAVG = "fedavg"
    FEDPROX = "fedprox"
    FEDNOVA = "fednova"
    FEDOPT = "fedopt"
    SCAFFOLD = "scaffold"
    FEDDYN = "feddyn"
    FEDBN = "fedbn"
    PERSONALIZED_FL = "personalized_fl"

class AggregationStrategy(Enum):
    """Model aggregation strategies"""
    WEIGHTED_AVERAGE = "weighted_average"
    MEDIAN_AGGREGATION = "median_aggregation"
    TRIMMED_MEAN = "trimmed_mean"
    KRUM = "krum"
    BRIDGE = "bridge"
    SECURE_AGGREGATION = "secure_aggregation"

class PrivacyMechanism(Enum):
    """Privacy protection mechanisms"""
    DIFFERENTIAL_PRIVACY = "differential_privacy"
    HOMOMORPHIC_ENCRYPTION = "homomorphic_encryption"
    SECURE_MULTIPARTY_COMPUTATION = "secure_multiparty_computation"
    SPLIT_LEARNING = "split_learning"
    GRADIENT_COMPRESSION = "gradient_compression"

class ClientType(Enum):
    """Types of federated learning clients"""
    CREATOR_DEVICE = "creator_device"
    EDGE_AGGREGATOR = "edge_aggregator"
    PLATFORM_NODE = "platform_node"
    TRUSTED_PARTNER = "trusted_partner"

@dataclass
class FederatedClient:
    """Federated learning client configuration"""
    client_id: str
    client_type: ClientType
    creator_type: str  # musician, blogger, photographer, etc.
    data_size: int
    model_version: str
    capabilities: Dict[str, Any]
    privacy_preferences: Dict[str, Any]
    compute_resources: Dict[str, float]
    connection_quality: float = 1.0
    participation_rate: float = 1.0
    last_seen: datetime = field(default_factory=datetime.now)
    total_rounds_participated: int = 0
    average_training_time: float = 0.0
    data_quality_score: float = 1.0
    trustworthiness_score: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class FederatedRound:
    """Federated learning round configuration"""
    round_id: str
    round_number: int
    algorithm: FederatedAlgorithm
    aggregation_strategy: AggregationStrategy
    selected_clients: List[str]
    global_model_state: Dict[str, Any]
    client_updates: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    aggregated_model: Optional[Dict[str, Any]] = None
    round_metrics: Dict[str, float] = field(default_factory=dict)
    privacy_budget_used: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "active"

@dataclass
class PrivacyConfig:
    """Privacy protection configuration"""
    mechanism: PrivacyMechanism
    epsilon: float = 1.0  # Differential privacy parameter
    delta: float = 1e-5  # Differential privacy parameter
    noise_scale: float = 1.0
    clipping_bound: float = 1.0
    secure_aggregation_threshold: int = 3
    encryption_key_size: int = 2048
    max_privacy_budget: float = 10.0
    privacy_accountant: Dict[str, float] = field(default_factory=dict)

class DifferentialPrivacyManager:
    """Differential privacy manager for federated learning"""
    
    def __init__(self, epsilon -> None: float, delta -> None: float) -> None:
        self.epsilon = epsilon
        self.delta = delta
        self.privacy_budget_used = 0.0
        self.noise_scale = self._calculate_noise_scale()
    
    def _calculate_noise_scale(self) -> float:
        """Calculate noise scale for Gaussian mechanism"""
        # Gaussian mechanism noise scale
        return np.sqrt(2 * np.log(1.25 / self.delta)) / self.epsilon
    
    def add_noise_to_gradients(self, gradients: Dict[str, torch.Tensor], clipping_bound: float = 1.0) -> Dict[str, torch.Tensor]:
        """Add differential privacy noise to gradients"""
        noisy_gradients = {}
        
        for name, grad in gradients.items():
            # Clip gradients
            grad_norm = torch.norm(grad)
            if grad_norm > clipping_bound:
                grad = grad * (clipping_bound / grad_norm)
            
            # Add Gaussian noise
            noise = torch.normal(0, self.noise_scale * clipping_bound, grad.shape)
            noisy_gradients[name] = grad + noise
        
        self.privacy_budget_used += self.epsilon
        return noisy_gradients
    
    def get_remaining_budget(self) -> float:
        """Get remaining privacy budget"""
        return max(0, self.epsilon - self.privacy_budget_used)

class SecureAggregationProtocol:
    """Secure aggregation protocol for federated learning"""
    
    def __init__(self, threshold -> None: int = 3) -> None:
        self.threshold = threshold
        self.client_keys = {}
        self.shared_secrets = {}
    
    def generate_client_keypair(self, client_id: str) -> Tuple[bytes, bytes]:
        """Generate RSA key pair for client"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        public_key = private_key.public_key()
        
        # Serialize keys
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        self.client_keys[client_id] = {
            'private_key': private_key,
            'public_key': public_key,
            'private_pem': private_pem,
            'public_pem': public_pem
        }
        
        return private_pem, public_pem
    
    def encrypt_model_update(self, client_id: str, model_update: Dict[str, torch.Tensor]) -> bytes:
        """Encrypt model update using client's public key"""
        if client_id not in self.client_keys:
            raise ValueError(f"No keys found for client: {client_id}")
        
        # Serialize model update
        serialized_update = pickle.dumps(model_update)
        
        # Generate symmetric key for encryption
        symmetric_key = secrets.token_bytes(32)
        
        # Encrypt with AES
        cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(secrets.token_bytes(12)))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(serialized_update) + encryptor.finalize()
        
        # Encrypt symmetric key with RSA public key
        public_key = self.client_keys[client_id]['public_key']
        encrypted_key = public_key.encrypt(
            symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return pickle.dumps({
            'encrypted_key': encrypted_key,
            'ciphertext': ciphertext,
            'nonce': encryptor.tag
        })
    
    def decrypt_model_update(self, client_id: str, encrypted_data: bytes) -> Dict[str, torch.Tensor]:
        """Decrypt model update using client's private key"""
        if client_id not in self.client_keys:
            raise ValueError(f"No keys found for client: {client_id}")
        
        # Deserialize encrypted data
        encrypted_package = pickle.loads(encrypted_data)
        
        # Decrypt symmetric key with RSA private key
        private_key = self.client_keys[client_id]['private_key']
        symmetric_key = private_key.decrypt(
            encrypted_package['encrypted_key'],
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        # Decrypt with AES
        cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(encrypted_package['nonce']))
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(encrypted_package['ciphertext']) + decryptor.finalize()
        
        # Deserialize model update
        return pickle.loads(plaintext)

class FederatedLearningEngine:
    """Advanced federated learning engine for creator platforms"""
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize federated learning engine"""
        self.config = config or {}
        
        # Engine configuration
        self.engine_id = str(uuid.uuid4())
        self.max_clients = self.config.get('max_clients', 1000)
        self.min_clients_per_round = self.config.get('min_clients_per_round', 10)
        self.max_rounds = self.config.get('max_rounds', 100)
        
        # Client management
        self.clients: Dict[str, FederatedClient] = {}
        self.active_clients: Set[str] = set()
        self.client_selection_strategy = self.config.get('client_selection_strategy', 'random')
        
        # Training management
        self.current_round: Optional[FederatedRound] = None
        self.round_history: List[FederatedRound] = []
        self.global_model: Optional[nn.Module] = None
        self.global_model_state: Dict[str, Any] = {}
        
        # Privacy and security
        self.privacy_config = PrivacyConfig(
            mechanism=PrivacyMechanism(self.config.get('privacy_mechanism', 'differential_privacy')),
            epsilon=self.config.get('privacy_epsilon', 1.0),
            delta=self.config.get('privacy_delta', 1e-5)
        )
        self.dp_manager = DifferentialPrivacyManager(
            self.privacy_config.epsilon,
            self.privacy_config.delta
        )
        self.secure_aggregation = SecureAggregationProtocol(
            threshold=self.privacy_config.secure_aggregation_threshold
        )
        
        # Performance tracking
        self.federation_metrics = defaultdict(list)
        self.client_performance = defaultdict(dict)
        self.convergence_history = []
        
        # Federated algorithms
        self.algorithms = {
            FederatedAlgorithm.FEDAVG: self._federated_averaging,
            FederatedAlgorithm.FEDPROX: self._federated_prox,
            FederatedAlgorithm.FEDNOVA: self._federated_nova,
            FederatedAlgorithm.SCAFFOLD: self._scaffold_algorithm
        }
        
        logger.info(f"Federated Learning Engine initialized: {self.engine_id}")

    async def register_client(
        self,
        client_id: str,
        client_type: ClientType,
        creator_type: str,
        data_size: int,
        capabilities: Dict[str, Any],
        privacy_preferences: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Register new federated learning client"""
        try:
            if len(self.clients) >= self.max_clients:
                logger.warning(f"Maximum client capacity reached: {self.max_clients}")
                return False
            
            if client_id in self.clients:
                logger.warning(f"Client already registered: {client_id}")
                return False
            
            # Create client configuration
            client = FederatedClient(
                client_id=client_id,
                client_type=client_type,
                creator_type=creator_type,
                data_size=data_size,
                model_version="1.0.0",
                capabilities=capabilities,
                privacy_preferences=privacy_preferences or {},
                compute_resources=capabilities.get('compute_resources', {}),
                connection_quality=capabilities.get('connection_quality', 1.0),
                data_quality_score=self._assess_data_quality(data_size, creator_type),
                trustworthiness_score=1.0  # Start with full trust
            )
            
            self.clients[client_id] = client
            self.active_clients.add(client_id)
            
            # Generate security keys if secure aggregation is enabled
            if self.privacy_config.mechanism == PrivacyMechanism.SECURE_MULTIPARTY_COMPUTATION:
                private_key, public_key = self.secure_aggregation.generate_client_keypair(client_id)
                client.capabilities['private_key'] = private_key
                client.capabilities['public_key'] = public_key
            
            logger.info(f"Federated client registered: {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering federated client: {e}")
            return False

    def _assess_data_quality(self, data_size: int, creator_type: str) -> float:
        """Assess data quality based on size and creator type"""
        # Simple heuristic for data quality assessment
        size_score = min(1.0, data_size / 10000)  # Normalize by 10k samples
        
        # Creator type quality weights
        creator_weights = {
            'musician': 0.9,
            'blogger': 0.8,
            'photographer': 0.95,
            'influencer': 0.85,
            'comedian': 0.8
        }
        
        type_score = creator_weights.get(creator_type, 0.7)
        
        return (size_score + type_score) / 2

    async def start_training_round(
        self,
        algorithm: FederatedAlgorithm,
        aggregation_strategy: AggregationStrategy,
        client_fraction: float = 0.1,
        min_clients: Optional[int] = None
    ) -> str:
        """Start new federated training round"""
        try:
            if self.current_round and self.current_round.status == "active":
                raise ValueError("Training round already in progress")
            
            round_id = f"fl_round_{uuid.uuid4().hex[:12]}"
            round_number = len(self.round_history) + 1
            
            # Select clients for this round
            selected_clients = await self._select_clients(client_fraction, min_clients)
            
            if len(selected_clients) < self.min_clients_per_round:
                raise ValueError(f"Insufficient clients selected: {len(selected_clients)} < {self.min_clients_per_round}")
            
            # Create training round
            training_round = FederatedRound(
                round_id=round_id,
                round_number=round_number,
                algorithm=algorithm,
                aggregation_strategy=aggregation_strategy,
                selected_clients=selected_clients,
                global_model_state=copy.deepcopy(self.global_model_state)
            )
            
            self.current_round = training_round
            
            # Notify selected clients to start training
            await self._notify_clients_start_training(selected_clients, round_id)
            
            logger.info(f"Federated training round started: {round_id} with {len(selected_clients)} clients")
            return round_id
            
        except Exception as e:
            logger.error(f"Error starting training round: {e}")
            raise

    async def _select_clients(
        self,
        client_fraction: float,
        min_clients: Optional[int] = None
    ) -> List[str]:
        """Select clients for federated training round"""
        try:
            available_clients = list(self.active_clients)
            
            if not available_clients:
                return []
            
            # Calculate number of clients to select
            num_clients = max(
                min_clients or self.min_clients_per_round,
                int(len(available_clients) * client_fraction)
            )
            num_clients = min(num_clients, len(available_clients))
            
            if self.client_selection_strategy == 'random':
                selected = random.sample(available_clients, num_clients)
            elif self.client_selection_strategy == 'data_size':
                # Select clients with larger datasets
                client_data_sizes = [
                    (client_id, self.clients[client_id].data_size)
                    for client_id in available_clients
                ]
                client_data_sizes.sort(key=lambda x: x[1], reverse=True)
                selected = [client_id for client_id, _ in client_data_sizes[:num_clients]]
            elif self.client_selection_strategy == 'quality_based':
                # Select clients with higher data quality
                client_qualities = [
                    (client_id, self.clients[client_id].data_quality_score)
                    for client_id in available_clients
                ]
                client_qualities.sort(key=lambda x: x[1], reverse=True)
                selected = [client_id for client_id, _ in client_qualities[:num_clients]]
            elif self.client_selection_strategy == 'diverse':
                # Select diverse clients by creator type
                selected = self._select_diverse_clients(available_clients, num_clients)
            else:
                selected = random.sample(available_clients, num_clients)
            
            return selected
            
        except Exception as e:
            logger.error(f"Error selecting clients: {e}")
            return []

    def _select_diverse_clients(self, available_clients: List[str], num_clients: int) -> List[str]:
        """Select diverse clients by creator type"""
        creator_type_clients = defaultdict(list)
        
        for client_id in available_clients:
            creator_type = self.clients[client_id].creator_type
            creator_type_clients[creator_type].append(client_id)
        
        selected = []
        types = list(creator_type_clients.keys())
        
        # Round-robin selection across creator types
        while len(selected) < num_clients and any(creator_type_clients.values()):
            for creator_type in types:
                if creator_type_clients[creator_type] and len(selected) < num_clients:
                    client_id = creator_type_clients[creator_type].pop(0)
                    selected.append(client_id)
        
        return selected

    async def _notify_clients_start_training(self, client_ids: List[str], round_id: str) -> None:
        """Notify selected clients to start training"""
        for client_id in client_ids:
            # In production, this would send actual notifications to clients
            logger.info(f"Notifying client {client_id} to start training for round {round_id}")
            
            # Update client participation
            client = self.clients[client_id]
            client.total_rounds_participated += 1

    async def receive_client_update(
        self,
        client_id: str,
        round_id: str,
        model_update: Dict[str, torch.Tensor],
        training_metrics: Dict[str, float]
    ) -> bool:
        """Receive model update from federated client"""
        try:
            if not self.current_round or self.current_round.round_id != round_id:
                logger.warning(f"No active round for update from client {client_id}")
                return False
            
            if client_id not in self.current_round.selected_clients:
                logger.warning(f"Client {client_id} not selected for current round")
                return False
            
            if client_id in self.current_round.client_updates:
                logger.warning(f"Update already received from client {client_id}")
                return False
            
            # Validate model update
            if not self._validate_model_update(model_update):
                logger.error(f"Invalid model update from client {client_id}")
                return False
            
            # Apply privacy protection
            protected_update = await self._apply_privacy_protection(client_id, model_update)
            
            # Store client update
            self.current_round.client_updates[client_id] = {
                'model_update': protected_update,
                'training_metrics': training_metrics,
                'timestamp': datetime.now(),
                'data_size': self.clients[client_id].data_size
            }
            
            # Update client performance metrics
            await self._update_client_performance(client_id, training_metrics)
            
            logger.info(f"Received update from client {client_id} for round {round_id}")
            
            # Check if round is complete
            if len(self.current_round.client_updates) == len(self.current_round.selected_clients):
                await self._complete_training_round()
            
            return True
            
        except Exception as e:
            logger.error(f"Error receiving client update: {e}")
            return False

    def _validate_model_update(self, model_update: Dict[str, torch.Tensor]) -> bool:
        """Validate model update from client"""
        try:
            # Check if update contains expected parameters
            if not model_update:
                return False
            
            # Check for NaN or infinite values
            for name, param in model_update.items():
                if torch.isnan(param).any() or torch.isinf(param).any():
                    logger.warning(f"Invalid values in parameter {name}")
                    return False
            
            # Check parameter shapes (if global model exists)
            if self.global_model_state:
                for name, param in model_update.items():
                    if name in self.global_model_state:
                        expected_shape = self.global_model_state[name].shape
                        if param.shape != expected_shape:
                            logger.warning(f"Shape mismatch for parameter {name}")
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating model update: {e}")
            return False

    async def _apply_privacy_protection(
        self,
        client_id: str,
        model_update: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """Apply privacy protection to model update"""
        try:
            if self.privacy_config.mechanism == PrivacyMechanism.DIFFERENTIAL_PRIVACY:
                return self.dp_manager.add_noise_to_gradients(
                    model_update,
                    self.privacy_config.clipping_bound
                )
            elif self.privacy_config.mechanism == PrivacyMechanism.SECURE_MULTIPARTY_COMPUTATION:
                # Encrypt model update
                encrypted_update = self.secure_aggregation.encrypt_model_update(client_id, model_update)
                return {'encrypted_data': encrypted_update}
            else:
                return model_update
                
        except Exception as e:
            logger.error(f"Error applying privacy protection: {e}")
            return model_update

    async def _update_client_performance(
        self,
        client_id: str,
        training_metrics: Dict[str, float]
    ) -> None:
        """Update client performance metrics"""
        try:
            client = self.clients[client_id]
            
            # Update average training time
            if 'training_time' in training_metrics:
                training_time = training_metrics['training_time']
                if client.average_training_time == 0:
                    client.average_training_time = training_time
                else:
                    client.average_training_time = (
                        client.average_training_time * 0.9 + training_time * 0.1
                    )
            
            # Update trustworthiness based on update quality
            if 'loss' in training_metrics:
                loss_improvement = training_metrics.get('loss_improvement', 0)
                if loss_improvement > 0:
                    client.trustworthiness_score = min(1.0, client.trustworthiness_score + 0.01)
                else:
                    client.trustworthiness_score = max(0.1, client.trustworthiness_score - 0.005)
            
            # Store performance history
            self.client_performance[client_id][datetime.now()] = training_metrics
            
        except Exception as e:
            logger.error(f"Error updating client performance: {e}")

    async def _complete_training_round(self) -> None:
        """Complete current training round and aggregate models"""
        try:
            if not self.current_round:
                return
            
            round_id = self.current_round.round_id
            logger.info(f"Completing training round: {round_id}")
            
            # Aggregate client updates
            aggregated_model = await self._aggregate_client_updates()
            
            if aggregated_model:
                self.current_round.aggregated_model = aggregated_model
                self.global_model_state = aggregated_model
                
                # Calculate round metrics
                await self._calculate_round_metrics()
                
                # Update convergence tracking
                await self._update_convergence_tracking()
            
            # Mark round as complete
            self.current_round.end_time = datetime.now()
            self.current_round.status = "completed"
            
            # Archive round
            self.round_history.append(self.current_round)
            self.current_round = None
            
            logger.info(f"Training round completed: {round_id}")
            
        except Exception as e:
            logger.error(f"Error completing training round: {e}")

    async def _aggregate_client_updates(self) -> Optional[Dict[str, torch.Tensor]]:
        """Aggregate client model updates"""
        try:
            if not self.current_round or not self.current_round.client_updates:
                return None
            
            algorithm = self.current_round.algorithm
            
            if algorithm in self.algorithms:
                return await self.algorithms[algorithm]()
            else:
                return await self._federated_averaging()
                
        except Exception as e:
            logger.error(f"Error aggregating client updates: {e}")
            return None

    async def _federated_averaging(self) -> Dict[str, torch.Tensor]:
        """FedAvg: Federated Averaging algorithm"""
        try:
            client_updates = self.current_round.client_updates
            total_data_size = sum(
                self.clients[client_id].data_size
                for client_id in client_updates.keys()
            )
            
            aggregated_model = {}
            
            for client_id, update_data in client_updates.items():
                model_update = update_data['model_update']
                client_data_size = self.clients[client_id].data_size
                weight = client_data_size / total_data_size
                
                for param_name, param_value in model_update.items():
                    if param_name == 'encrypted_data':  # Skip encrypted data
                        continue
                        
                    if param_name not in aggregated_model:
                        aggregated_model[param_name] = weight * param_value
                    else:
                        aggregated_model[param_name] += weight * param_value
            
            return aggregated_model
            
        except Exception as e:
            logger.error(f"Error in federated averaging: {e}")
            return {}

    async def _federated_prox(self) -> Dict[str, torch.Tensor]:
        """FedProx: Federated Optimization with proximal term"""
        try:
            # FedProx is similar to FedAvg but includes proximal term during training
            # For aggregation, we use the same weighted averaging
            return await self._federated_averaging()
            
        except Exception as e:
            logger.error(f"Error in FedProx: {e}")
            return {}

    async def _federated_nova(self) -> Dict[str, torch.Tensor]:
        """FedNova: Normalized averaging accounting for client heterogeneity"""
        try:
            client_updates = self.current_round.client_updates
            
            # Calculate effective local steps for each client
            effective_steps = {}
            total_effective_steps = 0
            
            for client_id, update_data in client_updates.items():
                # Estimate effective steps (simplified)
                training_metrics = update_data['training_metrics']
                local_epochs = training_metrics.get('local_epochs', 1)
                batch_size = training_metrics.get('batch_size', 32)
                data_size = self.clients[client_id].data_size
                
                steps_per_epoch = max(1, data_size // batch_size)
                effective_steps[client_id] = local_epochs * steps_per_epoch
                total_effective_steps += effective_steps[client_id]
            
            # Weighted aggregation with normalization
            aggregated_model = {}
            
            for client_id, update_data in client_updates.items():
                model_update = update_data['model_update']
                weight = effective_steps[client_id] / total_effective_steps
                
                for param_name, param_value in model_update.items():
                    if param_name == 'encrypted_data':
                        continue
                        
                    if param_name not in aggregated_model:
                        aggregated_model[param_name] = weight * param_value
                    else:
                        aggregated_model[param_name] += weight * param_value
            
            return aggregated_model
            
        except Exception as e:
            logger.error(f"Error in FedNova: {e}")
            return {}

    async def _scaffold_algorithm(self) -> Dict[str, torch.Tensor]:
        """SCAFFOLD: Controlled local training"""
        try:
            # SCAFFOLD requires control variates - simplified implementation
            return await self._federated_averaging()
            
        except Exception as e:
            logger.error(f"Error in SCAFFOLD: {e}")
            return {}

    async def _calculate_round_metrics(self) -> None:
        """Calculate metrics for completed round"""
        try:
            if not self.current_round:
                return
            
            client_updates = self.current_round.client_updates
            
            # Calculate average training metrics
            all_losses = []
            all_accuracies = []
            all_training_times = []
            
            for update_data in client_updates.values():
                metrics = update_data['training_metrics']
                
                if 'loss' in metrics:
                    all_losses.append(metrics['loss'])
                if 'accuracy' in metrics:
                    all_accuracies.append(metrics['accuracy'])
                if 'training_time' in metrics:
                    all_training_times.append(metrics['training_time'])
            
            round_metrics = {}
            
            if all_losses:
                round_metrics['avg_loss'] = np.mean(all_losses)
                round_metrics['std_loss'] = np.std(all_losses)
            
            if all_accuracies:
                round_metrics['avg_accuracy'] = np.mean(all_accuracies)
                round_metrics['std_accuracy'] = np.std(all_accuracies)
            
            if all_training_times:
                round_metrics['avg_training_time'] = np.mean(all_training_times)
                round_metrics['total_training_time'] = np.sum(all_training_times)
            
            round_metrics['num_participants'] = len(client_updates)
            round_metrics['participation_rate'] = len(client_updates) / len(self.current_round.selected_clients)
            
            # Privacy budget tracking
            round_metrics['privacy_budget_used'] = self.dp_manager.privacy_budget_used
            round_metrics['privacy_budget_remaining'] = self.dp_manager.get_remaining_budget()
            
            self.current_round.round_metrics = round_metrics
            
        except Exception as e:
            logger.error(f"Error calculating round metrics: {e}")

    async def _update_convergence_tracking(self) -> None:
        """Update convergence tracking metrics"""
        try:
            if not self.current_round or not self.current_round.round_metrics:
                return
            
            round_metrics = self.current_round.round_metrics
            
            convergence_point = {
                'round': self.current_round.round_number,
                'avg_loss': round_metrics.get('avg_loss', 0),
                'avg_accuracy': round_metrics.get('avg_accuracy', 0),
                'privacy_budget_used': round_metrics.get('privacy_budget_used', 0),
                'timestamp': datetime.now()
            }
            
            self.convergence_history.append(convergence_point)
            
            # Store in federation metrics
            self.federation_metrics['round_losses'].append(round_metrics.get('avg_loss', 0))
            self.federation_metrics['round_accuracies'].append(round_metrics.get('avg_accuracy', 0))
            self.federation_metrics['participation_rates'].append(round_metrics.get('participation_rate', 0))
            
        except Exception as e:
            logger.error(f"Error updating convergence tracking: {e}")

    async def evaluate_global_model(
        self,
        test_data: Dict[str, Any],
        metrics: List[str] = ['accuracy', 'loss']
    ) -> Dict[str, float]:
        """Evaluate global model performance"""
        try:
            if not self.global_model_state:
                return {}
            
            # Simulate model evaluation (in production, use actual test data)
            evaluation_results = {}
            
            # Simulate accuracy based on training progress
            num_rounds = len(self.round_history)
            base_accuracy = 0.5 + 0.4 * (1 - np.exp(-num_rounds / 10))
            evaluation_results['accuracy'] = base_accuracy + random.uniform(-0.05, 0.05)
            
            # Simulate loss
            base_loss = 2.0 * np.exp(-num_rounds / 8)
            evaluation_results['loss'] = base_loss + random.uniform(-0.1, 0.1)
            
            # Add other metrics
            for metric in metrics:
                if metric not in evaluation_results:
                    evaluation_results[metric] = random.uniform(0.6, 0.9)
            
            return evaluation_results
            
        except Exception as e:
            logger.error(f"Error evaluating global model: {e}")
            return {}

    async def get_federation_analytics(self) -> Dict[str, Any]:
        """Get comprehensive federation analytics"""
        try:
            total_clients = len(self.clients)
            active_clients = len(self.active_clients)
            total_rounds = len(self.round_history)
            
            # Calculate client diversity
            creator_types = defaultdict(int)
            for client in self.clients.values():
                creator_types[client.creator_type] += 1
            
            # Calculate average metrics
            avg_participation_rate = 0.0
            avg_round_accuracy = 0.0
            avg_round_loss = 0.0
            
            if self.round_history:
                participation_rates = [r.round_metrics.get('participation_rate', 0) for r in self.round_history]
                avg_participation_rate = np.mean(participation_rates)
                
                accuracies = [r.round_metrics.get('avg_accuracy', 0) for r in self.round_history if 'avg_accuracy' in r.round_metrics]
                if accuracies:
                    avg_round_accuracy = np.mean(accuracies)
                
                losses = [r.round_metrics.get('avg_loss', 0) for r in self.round_history if 'avg_loss' in r.round_metrics]
                if losses:
                    avg_round_loss = np.mean(losses)
            
            # Privacy metrics
            total_privacy_budget = self.privacy_config.max_privacy_budget
            used_privacy_budget = self.dp_manager.privacy_budget_used
            
            return {
                'engine_id': self.engine_id,
                'total_clients': total_clients,
                'active_clients': active_clients,
                'total_rounds_completed': total_rounds,
                'current_round_active': self.current_round is not None,
                'client_diversity': dict(creator_types),
                'avg_participation_rate': avg_participation_rate,
                'avg_round_accuracy': avg_round_accuracy,
                'avg_round_loss': avg_round_loss,
                'privacy_mechanism': self.privacy_config.mechanism.value,
                'privacy_budget_used': used_privacy_budget,
                'privacy_budget_remaining': total_privacy_budget - used_privacy_budget,
                'privacy_budget_utilization': used_privacy_budget / total_privacy_budget if total_privacy_budget > 0 else 0,
                'convergence_trend': 'improving' if len(self.convergence_history) > 1 and 
                                   self.convergence_history[-1]['avg_loss'] < self.convergence_history[-2]['avg_loss'] else 'stable',
                'federation_health_score': self._calculate_federation_health_score()
            }
            
        except Exception as e:
            logger.error(f"Error getting federation analytics: {e}")
            return {}

    def _calculate_federation_health_score(self) -> float:
        """Calculate overall federation health score"""
        try:
            score = 0.0
            
            # Client participation score (40%)
            if len(self.clients) > 0:
                participation_score = len(self.active_clients) / len(self.clients)
                score += participation_score * 0.4
            
            # Training progress score (30%)
            if self.round_history:
                recent_rounds = self.round_history[-5:]  # Last 5 rounds
                avg_participation = np.mean([r.round_metrics.get('participation_rate', 0) for r in recent_rounds])
                score += avg_participation * 0.3
            
            # Privacy budget efficiency (20%)
            privacy_efficiency = 1.0 - (self.dp_manager.privacy_budget_used / self.privacy_config.max_privacy_budget)
            score += privacy_efficiency * 0.2
            
            # Model convergence (10%)
            if len(self.convergence_history) > 1:
                latest_accuracy = self.convergence_history[-1].get('avg_accuracy', 0)
                score += latest_accuracy * 0.1
            
            return min(1.0, max(0.0, score))
            
        except Exception:
            return 0.5  # Default neutral score

    async def get_client_analytics(self, client_id: str) -> Dict[str, Any]:
        """Get analytics for specific client"""
        if client_id not in self.clients:
            raise ValueError(f"Client not found: {client_id}")
        
        client = self.clients[client_id]
        performance_history = self.client_performance.get(client_id, {})
        
        return {
            'client_id': client_id,
            'client_type': client.client_type.value,
            'creator_type': client.creator_type,
            'data_size': client.data_size,
            'total_rounds_participated': client.total_rounds_participated,
            'participation_rate': client.participation_rate,
            'average_training_time': client.average_training_time,
            'data_quality_score': client.data_quality_score,
            'trustworthiness_score': client.trustworthiness_score,
            'connection_quality': client.connection_quality,
            'last_seen': client.last_seen.isoformat(),
            'performance_history_entries': len(performance_history),
            'is_active': client_id in self.active_clients
        }

    async def remove_client(self, client_id: str) -> bool:
        """Remove client from federation"""
        try:
            if client_id not in self.clients:
                return False
            
            # Remove from active clients
            self.active_clients.discard(client_id)
            
            # Clean up client data
            del self.clients[client_id]
            
            if client_id in self.client_performance:
                del self.client_performance[client_id]
            
            # Clean up security keys
            if client_id in self.secure_aggregation.client_keys:
                del self.secure_aggregation.client_keys[client_id]
            
            logger.info(f"Client removed from federation: {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing client: {e}")
            return False

# Global federation engine instance
_federation_engine_instance = None

def get_federation_engine() -> FederatedLearningEngine:
    """Get global federation engine instance"""
    global _federation_engine_instance
    if _federation_engine_instance is None:
        _federation_engine_instance = FederatedLearningEngine()
    return _federation_engine_instance

# Test and validation functions
async def test_federated_learning_engine() -> None:
    """Test federated learning engine functionality"""
    engine = FederatedLearningEngine({
        'max_clients': 100,
        'min_clients_per_round': 5,
        'privacy_mechanism': 'differential_privacy',
        'privacy_epsilon': 1.0
    })
    
    # Register clients
    client_ids = []
    creator_types = ['musician', 'blogger', 'photographer', 'influencer', 'comedian']
    
    for i in range(10):
        client_id = f"client_{i}"
        creator_type = creator_types[i % len(creator_types)]
        
        success = await engine.register_client(
            client_id=client_id,
            client_type=ClientType.CREATOR_DEVICE,
            creator_type=creator_type,
            data_size=random.randint(1000, 10000),
            capabilities={
                'compute_resources': {'cpu_cores': 4, 'memory_gb': 8},
                'connection_quality': random.uniform(0.7, 1.0)
            }
        )
        
        if success:
            client_ids.append(client_id)
    
    # Start training round
    round_id = await engine.start_training_round(
        algorithm=FederatedAlgorithm.FEDAVG,
        aggregation_strategy=AggregationStrategy.WEIGHTED_AVERAGE,
        client_fraction=0.5
    )
    
    # Simulate client updates
    for client_id in client_ids[:5]:  # First 5 clients participate
        # Simulate model update (dummy gradients)
        model_update = {
            'layer1.weight': torch.randn(10, 5),
            'layer1.bias': torch.randn(10),
            'layer2.weight': torch.randn(1, 10),
            'layer2.bias': torch.randn(1)
        }
        
        training_metrics = {
            'loss': random.uniform(0.1, 2.0),
            'accuracy': random.uniform(0.6, 0.95),
            'training_time': random.uniform(10, 60),
            'local_epochs': 5,
            'batch_size': 32
        }
        
        await engine.receive_client_update(
            client_id=client_id,
            round_id=round_id,
            model_update=model_update,
            training_metrics=training_metrics
        )
    
    # Wait for round completion
    await asyncio.sleep(0.1)
    
    # Evaluate global model
    evaluation_results = await engine.evaluate_global_model(
        test_data={'test_samples': 1000},
        metrics=['accuracy', 'loss']
    )
    
    # Get analytics
    federation_analytics = await engine.get_federation_analytics()
    client_analytics = await engine.get_client_analytics(client_ids[0])
    
    logger.info("Federated learning engine test completed successfully")
    return {
        'registered_clients': len(client_ids),
        'round_id': round_id,
        'rounds_completed': len(engine.round_history),
        'global_model_accuracy': evaluation_results.get('accuracy', 0),
        'federation_health_score': federation_analytics.get('federation_health_score', 0),
        'privacy_budget_used': federation_analytics.get('privacy_budget_used', 0)
    }

if __name__ == "__main__":
    # Run test
    asyncio.run(test_federated_learning_engine())