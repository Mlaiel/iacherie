"""Master Integration Orchestration System
===========================================

Centralized management for all platform integrations in the Ainflue ecosystem.
Handles initialization, coordination, and lifecycle management of integrations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import json
import time
from datetime import datetime, timedelta

from .oauth_manager import OAuthManager
from .rate_limiter import RateLimiter
from .webhook_manager import WebhookManager
from .error_handler import IntegrationErrorHandler
from .monitoring_integration import IntegrationMonitor
from .circuit_breaker import CircuitBreaker
from .cache_manager import IntegrationCacheManager


class IntegrationStatus(Enum):
    """Integration status enumeration"""
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    RATE_LIMITED = "rate_limited"


@dataclass
class IntegrationConfig:
    """Configuration for integration instances"""
    name: str
    provider: str
    enabled: bool = True
    rate_limit: Optional[int] = None
    retry_attempts: int = 3
    timeout: int = 30
    circuit_breaker_threshold: int = 5
    cache_ttl: int = 300
    priority: int = 1


class IntegrationManager:
    """Master orchestrator for all platform integrations"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize integration manager
        
        Args:
            config_path: Path to integration configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.integrations: Dict[str, Any] = {}
        self.configs: Dict[str, IntegrationConfig] = {}
        self.status: Dict[str, IntegrationStatus] = {}
        
        # Core managers
        self.oauth_manager = OAuthManager()
        self.rate_limiter = RateLimiter()
        self.webhook_manager = WebhookManager()
        self.error_handler = IntegrationErrorHandler()
        self.monitor = IntegrationMonitor()
        self.circuit_breaker = CircuitBreaker()
        self.cache_manager = IntegrationCacheManager()
        
        # Load configuration
        if config_path:
            self._load_config(config_path)
            
        # Integration registry
        self._integration_registry = {}
        self._startup_time = datetime.utcnow()
    
    def register_integration(self, name: str, integration_class: type, config: IntegrationConfig):
        """Register a new integration
        
        Args:
            name: Unique integration name
            integration_class: Integration implementation class
            config: Integration configuration
        """
        try:
            self.configs[name] = config
            self._integration_registry[name] = integration_class
            self.status[name] = IntegrationStatus.INACTIVE
            
            self.logger.info(f"Registered integration: {name}")
            
        except Exception as e:
            self.logger.error(f"Failed to register integration {name}: {e}")
            raise
    
    async def initialize_integration(self, name: str, **kwargs) -> bool:
        """Initialize a specific integration
        
        Args:
            name: Integration name to initialize
            **kwargs: Additional initialization parameters
            
        Returns:
            bool: Success status
        """
        if name not in self._integration_registry:
            self.logger.error(f"Integration {name} not registered")
            return False
            
        try:
            self.status[name] = IntegrationStatus.INITIALIZING
            
            # Get integration class and config
            integration_class = self._integration_registry[name]
            config = self.configs[name]
            
            # Initialize integration instance
            integration = integration_class(
                oauth_manager=self.oauth_manager,
                rate_limiter=self.rate_limiter,
                cache_manager=self.cache_manager,
                config=config,
                **kwargs
            )
            
            # Perform initialization
            await integration.initialize()
            
            # Store instance
            self.integrations[name] = integration
            self.status[name] = IntegrationStatus.ACTIVE
            
            # Setup monitoring
            await self.monitor.register_integration(name, integration)
            
            self.logger.info(f"Successfully initialized integration: {name}")
            return True
            
        except Exception as e:
            self.status[name] = IntegrationStatus.ERROR
            await self.error_handler.handle_error(name, e)
            self.logger.error(f"Failed to initialize integration {name}: {e}")
            return False
    
    async def initialize_all(self, priority_order: bool = True) -> Dict[str, bool]:
        """Initialize all registered integrations
        
        Args:
            priority_order: Whether to initialize by priority
            
        Returns:
            Dict[str, bool]: Results for each integration
        """
        results = {}
        
        # Get initialization order
        integrations = list(self.configs.keys())
        if priority_order:
            integrations.sort(key=lambda x: self.configs[x].priority, reverse=True)
        
        # Initialize each integration
        for name in integrations:
            if self.configs[name].enabled:
                results[name] = await self.initialize_integration(name)
            else:
                results[name] = False
                self.logger.info(f"Skipping disabled integration: {name}")
        
        self.logger.info(f"Initialization complete. Success: {sum(results.values())}/{len(results)}")
        return results
    
    async def get_integration(self, name: str) -> Optional[Any]:
        """Get active integration instance
        
        Args:
            name: Integration name
            
        Returns:
            Integration instance or None
        """
        if name not in self.integrations:
            self.logger.warning(f"Integration {name} not found")
            return None
            
        if self.status[name] != IntegrationStatus.ACTIVE:
            self.logger.warning(f"Integration {name} not active (status: {self.status[name]})")
            return None
            
        return self.integrations[name]
    
    async def call_integration(self, name: str, method: str, *args, **kwargs) -> Any:
        """Call method on integration with error handling
        
        Args:
            name: Integration name
            method: Method name to call
            *args: Method arguments
            **kwargs: Method keyword arguments
            
        Returns:
            Method result
        """
        integration = await self.get_integration(name)
        if not integration:
            raise ValueError(f"Integration {name} not available")
        
        try:
            # Check circuit breaker
            if not await self.circuit_breaker.call_allowed(name):
                raise Exception(f"Circuit breaker open for {name}")
            
            # Check rate limits
            if not await self.rate_limiter.allow_request(name):
                self.status[name] = IntegrationStatus.RATE_LIMITED
                raise Exception(f"Rate limit exceeded for {name}")
            
            # Make the call
            if hasattr(integration, method):
                result = await getattr(integration, method)(*args, **kwargs)
                
                # Record success
                await self.circuit_breaker.record_success(name)
                await self.monitor.record_call(name, method, success=True)
                
                return result
            else:
                raise AttributeError(f"Method {method} not found on integration {name}")
                
        except Exception as e:
            # Record failure
            await self.circuit_breaker.record_failure(name)
            await self.monitor.record_call(name, method, success=False, error=str(e))
            await self.error_handler.handle_error(name, e)
            raise
    
    async def get_integration_status(self, name: Optional[str] = None) -> Union[Dict[str, IntegrationStatus], IntegrationStatus]:
        """Get integration status
        
        Args:
            name: Specific integration name or None for all
            
        Returns:
            Status or status dictionary
        """
        if name:
            return self.status.get(name, IntegrationStatus.INACTIVE)
        return self.status.copy()
    
    async def get_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report
        
        Returns:
            Health report dictionary
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self._startup_time).total_seconds(),
            "total_integrations": len(self._integration_registry),
            "active_integrations": sum(1 for s in self.status.values() if s == IntegrationStatus.ACTIVE),
            "integrations": {}
        }
        
        for name in self._integration_registry:
            integration_health = await self.monitor.get_integration_health(name)
            report["integrations"][name] = {
                "status": self.status.get(name, IntegrationStatus.INACTIVE).value,
                "config": self.configs[name].__dict__ if name in self.configs else {},
                "health": integration_health
            }
        
        return report
    
    async def restart_integration(self, name: str) -> bool:
        """Restart a specific integration
        
        Args:
            name: Integration name
            
        Returns:
            bool: Success status
        """
        try:
            # Shutdown existing
            if name in self.integrations:
                await self.shutdown_integration(name)
            
            # Reinitialize
            return await self.initialize_integration(name)
            
        except Exception as e:
            self.logger.error(f"Failed to restart integration {name}: {e}")
            return False
    
    async def shutdown_integration(self, name: str) -> bool:
        """Shutdown a specific integration
        
        Args:
            name: Integration name
            
        Returns:
            bool: Success status
        """
        try:
            if name in self.integrations:
                integration = self.integrations[name]
                if hasattr(integration, 'shutdown'):
                    await integration.shutdown()
                
                del self.integrations[name]
            
            self.status[name] = IntegrationStatus.INACTIVE
            await self.monitor.unregister_integration(name)
            
            self.logger.info(f"Successfully shutdown integration: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to shutdown integration {name}: {e}")
            return False
    
    async def shutdown_all(self) -> Dict[str, bool]:
        """Shutdown all active integrations
        
        Returns:
            Dict[str, bool]: Results for each integration
        """
        results = {}
        
        for name in list(self.integrations.keys()):
            results[name] = await self.shutdown_integration(name)
        
        # Shutdown core managers
        await self.webhook_manager.shutdown()
        await self.monitor.shutdown()
        
        self.logger.info("Integration manager shutdown complete")
        return results
    
    def _load_config(self, config_path: str):
        """Load configuration from file
        
        Args:
            config_path: Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            for name, config in config_data.get('integrations', {}).items():
                self.configs[name] = IntegrationConfig(
                    name=name,
                    **config
                )
            
            self.logger.info(f"Loaded configuration for {len(self.configs)} integrations")
            
        except Exception as e:
            self.logger.error(f"Failed to load config from {config_path}: {e}")
            raise


# Global integration manager instance
integration_manager = IntegrationManager()


async def get_integration_manager() -> IntegrationManager:
    """Get global integration manager instance
    
    Returns:
        IntegrationManager: Global instance
    """
    return integration_manager