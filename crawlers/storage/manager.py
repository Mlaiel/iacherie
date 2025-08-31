"""
Storage Manager Module
======================

Professional storage management system for IA-Influencer-Agent platform.
Orchestrates multiple storage providers with intelligent routing and failover.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.

Expertise combinée:
- Lead Developer IA: Architecture intelligente et optimisations ML
- Backend Senior: Infrastructure robuste et scalabilité enterprise
- ML Engineer: Algorithmes d'apprentissage et modèles prédictifs
- DBA Expert: Gestion de données et optimisation des requêtes
- Sécurité: Protection et chiffrement des données sensibles
- Microservices: Architecture distribuée et communication inter-services
- Audio/Vidéo: Traitement multimédia et analyse de contenu
- DevOps: Déploiement, monitoring et infrastructure cloud
- IA Prompt Engineer: Optimisation des interactions et prompts
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, AsyncIterator, Tuple, Type
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from pathlib import Path
import hashlib
import time

from .interfaces import (
    BaseStorageProvider, ContentStorageProvider, ViolationStorageProvider,
    CacheStorageProvider, VectorStorageProvider, TimeSeriesStorageProvider,
    RevenueStorageProvider, CollaborationStorageProvider, FingerPrintStorageProvider,
    AnalyticsStorageProvider, DistributionStorageProvider, LicensingStorageProvider,
    StorageRouter, StorageBackendType, StorageMetadata, QueryOptions, QueryFilter,
    StorageStats, CompressionType, DataFormat, Platform, ContentType,
    ViolationSeverity, FingerPrintType, RevenueType, StorageOperation, HealthStatus,
    CrawlerData, ContentRecord, ViolationRecord, RevenueRecord, CollaborationRecord
)

logger = logging.getLogger(__name__)

class RoutingStrategy(Enum):
    """Storage routing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_LOAD = "least_load"
    FASTEST_RESPONSE = "fastest_response"
    PRIMARY_SECONDARY = "primary_secondary"
    HASH_BASED = "hash_based"

class ReplicationMode(Enum):
    """Data replication modes."""
    NONE = "none"
    SYNC = "sync"
    ASYNC = "async"
    LAZY = "lazy"

@dataclass
class ProviderConfig:
    """Storage provider configuration."""
    provider_id: str
    provider_class: str
    backend_type: StorageBackendType
    config: Dict[str, Any]
    priority: int = 100
    weight: float = 1.0
    enabled: bool = True
    read_only: bool = False
    max_connections: int = 10
    timeout_seconds: int = 30
    retry_attempts: int = 3
    health_check_interval: int = 60

@dataclass
class StoragePolicy:
    """Storage policy configuration."""
    routing_strategy: RoutingStrategy = RoutingStrategy.ROUND_ROBIN
    replication_mode: ReplicationMode = ReplicationMode.NONE
    consistency_level: str = "eventual"  # strong, eventual, weak
    compression_enabled: bool = True
    encryption_enabled: bool = True
    ttl_seconds: Optional[int] = None
    max_retries: int = 3
    batch_size: int = 1000
    enable_caching: bool = True
    cache_ttl_seconds: int = 300

@dataclass
class ProviderMetrics:
    """Provider performance metrics."""
    provider_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_error: Optional[str] = None
    last_health_check: Optional[datetime] = None
    is_healthy: bool = True
    current_load: float = 0.0
    connections_active: int = 0

class StorageManager:
    """
    Professional storage management system.
    
    Features:
    - Multi-provider routing and load balancing
    - Automatic failover and recovery
    - Data replication and consistency
    - Performance monitoring and metrics
    - Intelligent caching and compression
    - Transaction management
    - Health monitoring
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        policy: Optional[StoragePolicy] = None
    ):
        """Initialize storage manager."""
        self.policy = policy or StoragePolicy()
        
        # Provider management
        self.providers: Dict[str, BaseStorageProvider] = {}
        self.provider_configs: Dict[str, ProviderConfig] = {}
        self.provider_metrics: Dict[str, ProviderMetrics] = {}
        
        # Routing state
        self.routing_state = {
            'round_robin_index': 0,
            'last_used': {},
            'load_scores': {},
            'response_times': {}
        }
        
        # Cache for frequent operations
        self.operation_cache: Dict[str, Tuple[Any, datetime]] = {}
        
        # Health monitoring
        self.health_check_tasks: Dict[str, asyncio.Task] = {}
        
        # Performance tracking
        self.performance_history: Dict[str, List[Tuple[datetime, float]]] = {}
        
        # Load configuration if provided
        if config_path:
            self.load_configuration(config_path)
        
        logger.info("Storage manager initialized")
    
    def load_configuration(self, config_path: str) -> None:
        """Load storage configuration from file."""



        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.error(f"Configuration file not found: {config_path}")
                return
            
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Load storage policy
            if 'policy' in config_data:
                policy_data = config_data['policy']
                self.policy = StoragePolicy(
                    routing_strategy=RoutingStrategy(policy_data.get('routing_strategy', 'round_robin')),
                    replication_mode=ReplicationMode(policy_data.get('replication_mode', 'none')),
                    consistency_level=policy_data.get('consistency_level', 'eventual'),
                    compression_enabled=policy_data.get('compression_enabled', True),
                    encryption_enabled=policy_data.get('encryption_enabled', True),
                    ttl_seconds=policy_data.get('ttl_seconds'),
                    max_retries=policy_data.get('max_retries', 3),
                    batch_size=policy_data.get('batch_size', 1000),
                    enable_caching=policy_data.get('enable_caching', True),
                    cache_ttl_seconds=policy_data.get('cache_ttl_seconds', 300)
                )
            
            # Load provider configurations
            if 'providers' in config_data:
                for provider_data in config_data['providers']:
                    provider_config = ProviderConfig(
                        provider_id=provider_data['provider_id'],
                        provider_class=provider_data['provider_class'],
                        backend_type=StorageBackendType(provider_data['backend_type']),
                        config=provider_data['config'],
                        priority=provider_data.get('priority', 100),
                        weight=provider_data.get('weight', 1.0),
                        enabled=provider_data.get('enabled', True),
                        read_only=provider_data.get('read_only', False),
                        max_connections=provider_data.get('max_connections', 10),
                        timeout_seconds=provider_data.get('timeout_seconds', 30),
                        retry_attempts=provider_data.get('retry_attempts', 3),
                        health_check_interval=provider_data.get('health_check_interval', 60)
                    )
                    self.provider_configs[provider_config.provider_id] = provider_config
            
            logger.info(f"Loaded configuration from {config_path}")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    async def register_provider(
        self,
        provider: BaseStorageProvider,
        config: ProviderConfig
    ) -> bool:
        """Register a new storage provider."""



        try:
            # Store provider and configuration
            self.providers[config.provider_id] = provider
            self.provider_configs[config.provider_id] = config
            
            # Initialize metrics
            self.provider_metrics[config.provider_id] = ProviderMetrics(
                provider_id=config.provider_id
            )
            
            # Connect to provider
            if config.enabled:
                await provider.connect()
                
                # Start health monitoring
                if config.health_check_interval > 0:
                    task = asyncio.create_task(
                        self._monitor_provider_health(config.provider_id)
                    )
                    self.health_check_tasks[config.provider_id] = task
            
            logger.info(f"Registered storage provider: {config.provider_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register provider {config.provider_id}: {e}")
            return False
    
    async def unregister_provider(self, provider_id: str) -> bool:
        """Unregister a storage provider."""



        try:
            if provider_id in self.providers:
                # Stop health monitoring
                if provider_id in self.health_check_tasks:
                    self.health_check_tasks[provider_id].cancel()
                    del self.health_check_tasks[provider_id]
                
                # Disconnect provider
                provider = self.providers[provider_id]
                await provider.disconnect()
                
                # Remove from collections
                del self.providers[provider_id]
                del self.provider_configs[provider_id]
                del self.provider_metrics[provider_id]
                
                logger.info(f"Unregistered storage provider: {provider_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister provider {provider_id}: {e}")
            return False
    
    def _select_provider_for_operation(
        self,
        operation_type: str,
        backend_type: Optional[StorageBackendType] = None,
        exclude_providers: Optional[List[str]] = None
    ) -> Optional[str]:
        """Select best provider for operation based on routing strategy."""
        exclude_providers = exclude_providers or []
        
        # Filter available providers
        available_providers = []
        for provider_id, config in self.provider_configs.items():
            if (config.enabled and 
                provider_id not in exclude_providers and
                (backend_type is None or config.backend_type == backend_type) and
                (operation_type != 'write' or not config.read_only)):
                
                metrics = self.provider_metrics.get(provider_id)
                if metrics and metrics.is_healthy:
                    available_providers.append(provider_id)
        
        if not available_providers:
            logger.warning(f"No available providers for operation: {operation_type}")
            return None
        
        # Apply routing strategy
        if self.policy.routing_strategy == RoutingStrategy.ROUND_ROBIN:
            return self._round_robin_selection(available_providers)
        elif self.policy.routing_strategy == RoutingStrategy.LEAST_LOAD:
            return self._least_load_selection(available_providers)
        elif self.policy.routing_strategy == RoutingStrategy.FASTEST_RESPONSE:
            return self._fastest_response_selection(available_providers)
        elif self.policy.routing_strategy == RoutingStrategy.PRIMARY_SECONDARY:
            return self._primary_secondary_selection(available_providers)
        elif self.policy.routing_strategy == RoutingStrategy.HASH_BASED:
            return self._hash_based_selection(available_providers, operation_type)
        else:
            return available_providers[0]
    
    def _round_robin_selection(self, providers: List[str]) -> str:
        """Round-robin provider selection."""
        if not providers:
            return None
        
        index = self.routing_state['round_robin_index'] % len(providers)
        self.routing_state['round_robin_index'] = (index + 1) % len(providers)
        return providers[index]
    
    def _least_load_selection(self, providers: List[str]) -> str:
        """Least load provider selection."""
        if not providers:
            return None
        
        best_provider = providers[0]
        lowest_load = float('inf')
        
        for provider_id in providers:
            metrics = self.provider_metrics.get(provider_id)
            if metrics and metrics.current_load < lowest_load:
                lowest_load = metrics.current_load
                best_provider = provider_id
        
        return best_provider
    
    def _fastest_response_selection(self, providers: List[str]) -> str:
        """Fastest response provider selection."""
        if not providers:
            return None
        
        best_provider = providers[0]
        fastest_time = float('inf')
        
        for provider_id in providers:
            metrics = self.provider_metrics.get(provider_id)
            if metrics and metrics.average_response_time < fastest_time:
                fastest_time = metrics.average_response_time
                best_provider = provider_id
        
        return best_provider
    
    def _primary_secondary_selection(self, providers: List[str]) -> str:
        """Primary-secondary provider selection."""
        if not providers:
            return None
        
        # Sort by priority (lower number = higher priority)
        sorted_providers = sorted(
            providers,
            key=lambda p: self.provider_configs[p].priority
        )
        return sorted_providers[0]
    
    def _hash_based_selection(self, providers: List[str], key: str) -> str:
        """Hash-based provider selection."""
        if not providers:
            return None
        
        # Create hash of key and map to provider
        hash_value = hashlib.md5(key.encode()).hexdigest()
        index = int(hash_value, 16) % len(providers)
        return providers[index]
    
    async def _execute_with_fallback(
        self,
        operation_func,
        operation_type: str,
        backend_type: Optional[StorageBackendType] = None,
        max_retries: Optional[int] = None
    ) -> Any:
        """Execute operation with automatic fallback."""
        max_retries = max_retries or self.policy.max_retries
        attempted_providers = []
        last_error = None
        
        for attempt in range(max_retries + 1):
            provider_id = self._select_provider_for_operation(
                operation_type,
                backend_type,
                attempted_providers
            )
            
            if not provider_id:
                break
            
            attempted_providers.append(provider_id)
            provider = self.providers[provider_id]
            metrics = self.provider_metrics[provider_id]
            
            start_time = time.time()
            try:
                # Execute operation
                result = await operation_func(provider)
                
                # Update metrics on success
                response_time = time.time() - start_time
                metrics.total_requests += 1
                metrics.successful_requests += 1
                metrics.average_response_time = (
                    (metrics.average_response_time * (metrics.total_requests - 1) + response_time) /
                    metrics.total_requests
                )
                
                return result
                
            except Exception as e:
                # Update metrics on failure
                response_time = time.time() - start_time
                metrics.total_requests += 1
                metrics.failed_requests += 1
                metrics.last_error = str(e)
                last_error = e
                
                logger.warning(
                    f"Operation failed on provider {provider_id} (attempt {attempt + 1}): {e}"
                )
                
                # Mark provider as unhealthy if too many failures
                failure_rate = metrics.failed_requests / metrics.total_requests
                if failure_rate > 0.5:
                    metrics.is_healthy = False
                    logger.error(f"Marked provider {provider_id} as unhealthy")
        
        # All attempts failed
        if last_error:
            raise last_error
        else:
            raise RuntimeError(f"No available providers for operation: {operation_type}")
    
    async def _monitor_provider_health(self, provider_id: str) -> None:
        """Monitor provider health continuously."""
        config = self.provider_configs[provider_id]
        provider = self.providers[provider_id]
        metrics = self.provider_metrics[provider_id]
        
        while True:
            try:
                await asyncio.sleep(config.health_check_interval)
                
                # Perform health check
                is_healthy = await provider.health_check()
                metrics.is_healthy = is_healthy
                metrics.last_health_check = datetime.now()
                
                if not is_healthy:
                    logger.warning(f"Provider {provider_id} failed health check")
                else:
                    logger.debug(f"Provider {provider_id} health check passed")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error for provider {provider_id}: {e}")
                metrics.is_healthy = False
                metrics.last_error = str(e)
    
    async def store_record(
        self,
        record_id: str,
        data: Any,
        metadata: Optional[StorageMetadata] = None,
        backend_type: Optional[StorageBackendType] = None
    ) -> bool:
        """Store a record with automatic provider selection."""
        async def operation(provider):
            return await provider.store_record(record_id, data, metadata)
        
        return await self._execute_with_fallback(
            operation,
            "write",
            backend_type
        )
    
    async def retrieve_record(
        self,
        record_id: str,
        include_metadata: bool = True,
        backend_type: Optional[StorageBackendType] = None
    ) -> Optional[Tuple[Any, Optional[StorageMetadata]]]:
        """Retrieve a record with automatic provider selection."""
        # Check cache first if enabled
        if self.policy.enable_caching:
            cache_key = f"record:{record_id}"
            if cache_key in self.operation_cache:
                cached_data, cached_time = self.operation_cache[cache_key]
                if (datetime.now() - cached_time).total_seconds() < self.policy.cache_ttl_seconds:
                    return cached_data
        
        async def operation(provider):
            result = await provider.retrieve_record(record_id, include_metadata)
            
            # Cache result if enabled
            if self.policy.enable_caching and result:
                cache_key = f"record:{record_id}"
                self.operation_cache[cache_key] = (result, datetime.now())
            
            return result
        
        return await self._execute_with_fallback(
            operation,
            "read",
            backend_type
        )
    
    async def query_records(
        self,
        options: QueryOptions,
        backend_type: Optional[StorageBackendType] = None
    ) -> AsyncIterator[Tuple[str, Any, Optional[StorageMetadata]]]:
        """Query records with automatic provider selection."""
        provider_id = self._select_provider_for_operation("read", backend_type)
        if not provider_id:
            return
        
        provider = self.providers[provider_id]
        async for record in provider.query_records(options):
            yield record
    
    async def delete_record(
        self,
        record_id: str,
        backend_type: Optional[StorageBackendType] = None
    ) -> bool:
        """Delete a record with automatic provider selection."""
        # Remove from cache if exists
        if self.policy.enable_caching:
            cache_key = f"record:{record_id}"
            self.operation_cache.pop(cache_key, None)
        
        async def operation(provider):
            return await provider.delete_record(record_id)
        
        return await self._execute_with_fallback(
            operation,
            "write",
            backend_type
        )
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics."""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'policy': {
                'routing_strategy': self.policy.routing_strategy.value,
                'replication_mode': self.policy.replication_mode.value,
                'consistency_level': self.policy.consistency_level,
                'compression_enabled': self.policy.compression_enabled,
                'encryption_enabled': self.policy.encryption_enabled
            },
            'providers': {},
            'cache': {
                'enabled': self.policy.enable_caching,
                'entries': len(self.operation_cache),
                'ttl_seconds': self.policy.cache_ttl_seconds
            }
        }
        
        # Provider metrics
        for provider_id, provider_metrics in self.provider_metrics.items():
            config = self.provider_configs.get(provider_id)
            metrics['providers'][provider_id] = {
                'backend_type': config.backend_type.value if config else 'unknown',
                'enabled': config.enabled if config else False,
                'healthy': provider_metrics.is_healthy,
                'total_requests': provider_metrics.total_requests,
                'successful_requests': provider_metrics.successful_requests,
                'failed_requests': provider_metrics.failed_requests,
                'success_rate': (
                    provider_metrics.successful_requests / provider_metrics.total_requests
                    if provider_metrics.total_requests > 0 else 0.0
                ),
                'average_response_time': provider_metrics.average_response_time,
                'current_load': provider_metrics.current_load,
                'last_health_check': (
                    provider_metrics.last_health_check.isoformat()
                    if provider_metrics.last_health_check else None
                ),
                'last_error': provider_metrics.last_error
            }
        
        return metrics
    
    async def cleanup_cache(self) -> int:
        """Clean up expired cache entries."""
        if not self.policy.enable_caching:
            return 0
        
        current_time = datetime.now()
        expired_keys = []
        
        for key, (data, cached_time) in self.operation_cache.items():
            if (current_time - cached_time).total_seconds() > self.policy.cache_ttl_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.operation_cache[key]
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        return len(expired_keys)
    
    async def shutdown(self) -> None:
        """Shutdown storage manager gracefully."""
        logger.info("Shutting down storage manager...")
        
        # Cancel health check tasks
        for task in self.health_check_tasks.values():
            task.cancel()
        
        # Wait for tasks to complete
        if self.health_check_tasks:
            await asyncio.gather(
                *self.health_check_tasks.values(),
                return_exceptions=True
            )
        
        # Disconnect all providers
        for provider_id, provider in self.providers.items():
            try:
                await provider.disconnect()
                logger.info(f"Disconnected provider: {provider_id}")
            except Exception as e:
                logger.error(f"Error disconnecting provider {provider_id}: {e}")
        
        # Clear cache
        self.operation_cache.clear()
        
        logger.info("Storage manager shutdown complete")

class LoadBalancer:
    """
    Intelligent load balancer for storage operations.
    
    Implements advanced load balancing algorithms with predictive analytics.
    """
    
    def __init__(self, storage_manager: StorageManager):
        """Initialize load balancer."""
        self.storage_manager = storage_manager
        self.load_history: Dict[str, List[Tuple[datetime, float]]] = {}
        self.prediction_cache: Dict[str, Tuple[float, datetime]] = {}
        
    async def calculate_provider_load(self, provider_id: str) -> float:
        """Calculate current provider load score."""
        metrics = self.storage_manager.provider_metrics.get(provider_id)
        if not metrics:
            return 1.0
        
        # Weighted load calculation
        request_load = min(metrics.total_requests / 1000.0, 1.0)  # Normalize to 1000 requests
        response_time_load = min(metrics.average_response_time / 5.0, 1.0)  # Normalize to 5s
        connection_load = metrics.connections_active / 10.0  # Normalize to 10 connections
        
        # Failure rate penalty
        if metrics.total_requests > 0:
            failure_rate = metrics.failed_requests / metrics.total_requests
            failure_penalty = failure_rate * 2.0
        else:
            failure_penalty = 0.0
        
        total_load = (request_load * 0.3 + response_time_load * 0.4 + 
                     connection_load * 0.2 + failure_penalty * 0.1)
        
        return min(total_load, 1.0)
    
    async def predict_future_load(self, provider_id: str, minutes_ahead: int = 5) -> float:
        """Predict future load using historical data."""
        cache_key = f"{provider_id}:{minutes_ahead}"
        
        # Check prediction cache
        if cache_key in self.prediction_cache:
            prediction, cached_time = self.prediction_cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < 60:  # 1 minute cache
                return prediction
        
        # Get historical load data
        history = self.load_history.get(provider_id, [])
        if len(history) < 3:
            # Not enough data for prediction
            current_load = await self.calculate_provider_load(provider_id)
            return current_load
        
        # Simple linear regression for trend prediction
        recent_history = history[-10:]  # Last 10 data points
        if len(recent_history) >= 2:
            x_values = list(range(len(recent_history)))
            y_values = [load for _, load in recent_history]
            
            # Calculate trend
            n = len(recent_history)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
            
            # Predict future load
            future_x = n + (minutes_ahead / 5)  # Assuming 5-minute intervals
            predicted_load = slope * future_x + intercept
            predicted_load = max(0.0, min(predicted_load, 1.0))  # Clamp to [0, 1]
            
            # Cache prediction
            self.prediction_cache[cache_key] = (predicted_load, datetime.now())
            return predicted_load
        
        # Fallback to current load
        return await self.calculate_provider_load(provider_id)
    
    async def update_load_history(self) -> None:
        """Update load history for all providers."""
        current_time = datetime.now()
        
        for provider_id in self.storage_manager.providers:
            current_load = await self.calculate_provider_load(provider_id)
            
            if provider_id not in self.load_history:
                self.load_history[provider_id] = []
            
            self.load_history[provider_id].append((current_time, current_load))
            
            # Keep only last 24 hours of data
            cutoff_time = current_time - timedelta(hours=24)
            self.load_history[provider_id] = [
                (timestamp, load) for timestamp, load in self.load_history[provider_id]
                if timestamp > cutoff_time
            ]
    
    async def select_optimal_provider(
        self,
        operation_type: str,
        backend_type: Optional[StorageBackendType] = None,
        consider_future_load: bool = True
    ) -> Optional[str]:
        """Select optimal provider considering current and predicted load."""
        available_providers = []
        
        for provider_id, config in self.storage_manager.provider_configs.items():
            if (config.enabled and
                (backend_type is None or config.backend_type == backend_type) and
                (operation_type != 'write' or not config.read_only)):
                
                metrics = self.storage_manager.provider_metrics.get(provider_id)
                if metrics and metrics.is_healthy:
                    available_providers.append(provider_id)
        
        if not available_providers:
            return None
        
        # Calculate scores for each provider
        provider_scores = {}
        for provider_id in available_providers:
            current_load = await self.calculate_provider_load(provider_id)
            
            if consider_future_load:
                future_load = await self.predict_future_load(provider_id)
                combined_load = (current_load * 0.7 + future_load * 0.3)
            else:
                combined_load = current_load
            
            # Lower load = higher score
            score = 1.0 - combined_load
            
            # Apply provider weight
            config = self.storage_manager.provider_configs[provider_id]
            score *= config.weight
            
            provider_scores[provider_id] = score
        
        # Select provider with highest score
        best_provider = max(provider_scores.keys(), key=lambda p: provider_scores[p])
        return best_provider

class FailoverManager:
    """
    Advanced failover management for storage providers.
    
    Handles automatic failover, recovery, and circuit breaker patterns.
    """
    
    def __init__(self, storage_manager: StorageManager):
        """Initialize failover manager."""
        self.storage_manager = storage_manager
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        self.recovery_tasks: Dict[str, asyncio.Task] = {}
        
    def initialize_circuit_breaker(self, provider_id: str) -> None:
        """Initialize circuit breaker for provider."""
        self.circuit_breakers[provider_id] = {
            'state': 'closed',  # closed, open, half_open
            'failure_count': 0,
            'last_failure_time': None,
            'failure_threshold': 5,
            'recovery_timeout': 60,  # seconds
            'half_open_max_calls': 3,
            'half_open_calls': 0
        }
    
    async def record_success(self, provider_id: str) -> None:
        """Record successful operation."""
        if provider_id not in self.circuit_breakers:
            self.initialize_circuit_breaker(provider_id)
        
        breaker = self.circuit_breakers[provider_id]
        
        if breaker['state'] == 'half_open':
            breaker['half_open_calls'] += 1
            if breaker['half_open_calls'] >= breaker['half_open_max_calls']:
                # Recovery successful, close circuit
                breaker['state'] = 'closed'
                breaker['failure_count'] = 0
                breaker['half_open_calls'] = 0
                logger.info(f"Circuit breaker closed for provider {provider_id}")
        elif breaker['state'] == 'closed':
            # Reset failure count on success
            breaker['failure_count'] = max(0, breaker['failure_count'] - 1)
    
    async def record_failure(self, provider_id: str) -> None:
        """Record failed operation."""
        if provider_id not in self.circuit_breakers:
            self.initialize_circuit_breaker(provider_id)
        
        breaker = self.circuit_breakers[provider_id]
        breaker['failure_count'] += 1
        breaker['last_failure_time'] = datetime.now()
        
        if breaker['failure_count'] >= breaker['failure_threshold']:
            if breaker['state'] == 'closed':
                # Open circuit breaker
                breaker['state'] = 'open'
                logger.warning(f"Circuit breaker opened for provider {provider_id}")
                
                # Start recovery task
                if provider_id not in self.recovery_tasks:
                    task = asyncio.create_task(self._recovery_task(provider_id))
                    self.recovery_tasks[provider_id] = task
        elif breaker['state'] == 'half_open':
            # Failed during half-open state, go back to open
            breaker['state'] = 'open'
            breaker['half_open_calls'] = 0
            logger.warning(f"Circuit breaker reopened for provider {provider_id}")
    
    def is_provider_available(self, provider_id: str) -> bool:
        """Check if provider is available according to circuit breaker."""
        if provider_id not in self.circuit_breakers:
            return True
        
        breaker = self.circuit_breakers[provider_id]
        return breaker['state'] != 'open'
    
    async def _recovery_task(self, provider_id: str) -> None:
        """Recovery task for failed provider."""



        try:
            breaker = self.circuit_breakers[provider_id]
            
            while breaker['state'] == 'open':
                await asyncio.sleep(breaker['recovery_timeout'])
                
                # Try to recover
                try:
                    provider = self.storage_manager.providers[provider_id]
                    is_healthy = await provider.health_check()
                    
                    if is_healthy:
                        # Move to half-open state
                        breaker['state'] = 'half_open'
                        breaker['half_open_calls'] = 0
                        logger.info(f"Circuit breaker moved to half-open for provider {provider_id}")
                        break
                    else:
                        logger.debug(f"Provider {provider_id} still unhealthy during recovery")
                        
                except Exception as e:
                    logger.error(f"Recovery health check failed for provider {provider_id}: {e}")
            
        except asyncio.CancelledError:
            pass
        finally:
            # Remove from recovery tasks
            if provider_id in self.recovery_tasks:
                del self.recovery_tasks[provider_id]
    
    async def get_failover_providers(
        self,
        failed_provider_id: str,
        operation_type: str,
        backend_type: Optional[StorageBackendType] = None
    ) -> List[str]:
        """Get list of available failover providers."""
        failover_providers = []
        
        for provider_id, config in self.storage_manager.provider_configs.items():
            if (provider_id != failed_provider_id and
                config.enabled and
                (backend_type is None or config.backend_type == backend_type) and
                (operation_type != 'write' or not config.read_only) and
                self.is_provider_available(provider_id)):
                
                metrics = self.storage_manager.provider_metrics.get(provider_id)
                if metrics and metrics.is_healthy:
                    failover_providers.append(provider_id)
        
        # Sort by priority and current load
        def sort_key(provider_id):
            config = self.storage_manager.provider_configs[provider_id]
            metrics = self.storage_manager.provider_metrics[provider_id]
            return (config.priority, metrics.current_load)
        
        failover_providers.sort(key=sort_key)
        return failover_providers

class PerformanceMonitor:
    """
    Advanced performance monitoring for storage operations.
    
    Provides detailed metrics, alerting, and performance analytics.
    """
    
    def __init__(self, storage_manager: StorageManager):
        """Initialize performance monitor."""
        self.storage_manager = storage_manager
        self.operation_metrics: Dict[str, Dict[str, Any]] = {}
        self.alert_thresholds = {
            'response_time_ms': 5000,
            'error_rate_percent': 10.0,
            'availability_percent': 95.0
        }
        self.alert_callbacks: List[Callable] = []
        
    def add_alert_callback(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add alert callback function."""
        self.alert_callbacks.append(callback)
    
    async def record_operation_metrics(
        self,
        provider_id: str,
        operation_type: str,
        response_time_ms: float,
        data_size_bytes: Optional[int] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> None:
        """Record operation metrics."""
        timestamp = datetime.now()
        
        if provider_id not in self.operation_metrics:
            self.operation_metrics[provider_id] = {
                'operations': [],
                'hourly_stats': {},
                'daily_stats': {}
            }
        
        # Record operation
        operation_record = {
            'timestamp': timestamp,
            'operation_type': operation_type,
            'response_time_ms': response_time_ms,
            'data_size_bytes': data_size_bytes,
            'success': success,
            'error_message': error_message
        }
        
        self.operation_metrics[provider_id]['operations'].append(operation_record)
        
        # Update aggregated stats
        await self._update_aggregated_stats(provider_id, operation_record)
        
        # Check for alerts
        await self._check_performance_alerts(provider_id)
    
    async def _update_aggregated_stats(
        self,
        provider_id: str,
        operation_record: Dict[str, Any]
    ) -> None:
        """Update aggregated statistics."""
        timestamp = operation_record['timestamp']
        hour_key = timestamp.strftime('%Y-%m-%d-%H')
        day_key = timestamp.strftime('%Y-%m-%d')
        
        metrics = self.operation_metrics[provider_id]
        
        # Update hourly stats
        if hour_key not in metrics['hourly_stats']:
            metrics['hourly_stats'][hour_key] = {
                'total_operations': 0,
                'successful_operations': 0,
                'total_response_time_ms': 0.0,
                'total_data_bytes': 0,
                'min_response_time_ms': float('inf'),
                'max_response_time_ms': 0.0
            }
        
        hourly = metrics['hourly_stats'][hour_key]
        hourly['total_operations'] += 1
        if operation_record['success']:
            hourly['successful_operations'] += 1
        
        response_time = operation_record['response_time_ms']
        hourly['total_response_time_ms'] += response_time
        hourly['min_response_time_ms'] = min(hourly['min_response_time_ms'], response_time)
        hourly['max_response_time_ms'] = max(hourly['max_response_time_ms'], response_time)
        
        if operation_record['data_size_bytes']:
            hourly['total_data_bytes'] += operation_record['data_size_bytes']
        
        # Update daily stats (similar logic)
        if day_key not in metrics['daily_stats']:
            metrics['daily_stats'][day_key] = {
                'total_operations': 0,
                'successful_operations': 0,
                'total_response_time_ms': 0.0,
                'total_data_bytes': 0,
                'min_response_time_ms': float('inf'),
                'max_response_time_ms': 0.0
            }
        
        daily = metrics['daily_stats'][day_key]
        daily['total_operations'] += 1
        if operation_record['success']:
            daily['successful_operations'] += 1
        
        daily['total_response_time_ms'] += response_time
        daily['min_response_time_ms'] = min(daily['min_response_time_ms'], response_time)
        daily['max_response_time_ms'] = max(daily['max_response_time_ms'], response_time)
        
        if operation_record['data_size_bytes']:
            daily['total_data_bytes'] += operation_record['data_size_bytes']
    
    async def _check_performance_alerts(self, provider_id: str) -> None:
        """Check for performance alerts."""
        if not self.alert_callbacks:
            return
        
        # Get recent performance metrics
        current_metrics = await self.get_provider_performance_summary(provider_id, hours=1)
        
        alerts = []
        
        # Check response time threshold
        if current_metrics['avg_response_time_ms'] > self.alert_thresholds['response_time_ms']:
            alerts.append({
                'type': 'high_response_time',
                'provider_id': provider_id,
                'value': current_metrics['avg_response_time_ms'],
                'threshold': self.alert_thresholds['response_time_ms'],
                'message': f"High response time: {current_metrics['avg_response_time_ms']:.2f}ms"
            })
        
        # Check error rate threshold
        if current_metrics['error_rate_percent'] > self.alert_thresholds['error_rate_percent']:
            alerts.append({
                'type': 'high_error_rate',
                'provider_id': provider_id,
                'value': current_metrics['error_rate_percent'],
                'threshold': self.alert_thresholds['error_rate_percent'],
                'message': f"High error rate: {current_metrics['error_rate_percent']:.2f}%"
            })
        
        # Check availability threshold
        if current_metrics['availability_percent'] < self.alert_thresholds['availability_percent']:
            alerts.append({
                'type': 'low_availability',
                'provider_id': provider_id,
                'value': current_metrics['availability_percent'],
                'threshold': self.alert_thresholds['availability_percent'],
                'message': f"Low availability: {current_metrics['availability_percent']:.2f}%"
            })
        
        # Send alerts
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    await callback(alert['type'], alert)
                except Exception as e:
                    logger.error(f"Error in alert callback: {e}")
    
    async def get_provider_performance_summary(
        self,
        provider_id: str,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get performance summary for provider."""
        if provider_id not in self.operation_metrics:
            return {
                'total_operations': 0,
                'successful_operations': 0,
                'error_rate_percent': 0.0,
                'avg_response_time_ms': 0.0,
                'min_response_time_ms': 0.0,
                'max_response_time_ms': 0.0,
                'total_data_bytes': 0,
                'availability_percent': 100.0,
                'throughput_ops_per_hour': 0.0
            }
        
        # Filter operations by time window
        cutoff_time = datetime.now() - timedelta(hours=hours)
        operations = [
            op for op in self.operation_metrics[provider_id]['operations']
            if op['timestamp'] > cutoff_time
        ]
        
        if not operations:
            return {
                'total_operations': 0,
                'successful_operations': 0,
                'error_rate_percent': 0.0,
                'avg_response_time_ms': 0.0,
                'min_response_time_ms': 0.0,
                'max_response_time_ms': 0.0,
                'total_data_bytes': 0,
                'availability_percent': 100.0,
                'throughput_ops_per_hour': 0.0
            }
        
        # Calculate metrics
        total_operations = len(operations)
        successful_operations = sum(1 for op in operations if op['success'])
        error_rate = ((total_operations - successful_operations) / total_operations) * 100.0
        
        response_times = [op['response_time_ms'] for op in operations]
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        
        total_data_bytes = sum(op['data_size_bytes'] or 0 for op in operations)
        availability_percent = (successful_operations / total_operations) * 100.0
        throughput_ops_per_hour = total_operations / hours
        
        return {
            'total_operations': total_operations,
            'successful_operations': successful_operations,
            'error_rate_percent': error_rate,
            'avg_response_time_ms': avg_response_time,
            'min_response_time_ms': min_response_time,
            'max_response_time_ms': max_response_time,
            'total_data_bytes': total_data_bytes,
            'availability_percent': availability_percent,
            'throughput_ops_per_hour': throughput_ops_per_hour
        }
    
    async def get_system_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive system performance report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'providers': {},
            'system_totals': {
                'total_operations': 0,
                'total_successful_operations': 0,
                'overall_error_rate_percent': 0.0,
                'avg_system_response_time_ms': 0.0,
                'total_data_processed_bytes': 0
            }
        }
        
        all_operations = []
        
        for provider_id in self.storage_manager.providers:
            provider_summary = await self.get_provider_performance_summary(provider_id)
            report['providers'][provider_id] = provider_summary
            
            # Collect for system totals
            if provider_id in self.operation_metrics:
                cutoff_time = datetime.now() - timedelta(hours=24)
                provider_operations = [
                    op for op in self.operation_metrics[provider_id]['operations']
                    if op['timestamp'] > cutoff_time
                ]
                all_operations.extend(provider_operations)
        
        # Calculate system totals
        if all_operations:
            total_ops = len(all_operations)
            successful_ops = sum(1 for op in all_operations if op['success'])
            
            report['system_totals'] = {
                'total_operations': total_ops,
                'total_successful_operations': successful_ops,
                'overall_error_rate_percent': ((total_ops - successful_ops) / total_ops) * 100.0,
                'avg_system_response_time_ms': sum(op['response_time_ms'] for op in all_operations) / total_ops,
                'total_data_processed_bytes': sum(op['data_size_bytes'] or 0 for op in all_operations)
            }
        
        return report

# Export main classes
__all__ = [
    'StorageManager',
    'ProviderConfig',
    'StoragePolicy',
    'ProviderMetrics',
    'RoutingStrategy',
    'ReplicationMode',
    'LoadBalancer',
    'FailoverManager',
    'PerformanceMonitor'
]
