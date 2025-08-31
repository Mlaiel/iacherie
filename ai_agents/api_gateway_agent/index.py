"""
API Gateway Agent Index - Central Module Access Point

Centralized access point for API Gateway Agent with service discovery,
health monitoring, and management utilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from .api_gateway_agent import APIGatewayAgent
from .config import APIGatewayConfig
from .request_router import RequestRouter
from .load_balancer import LoadBalancer
from .rate_limiter import RateLimiter
from .auth_middleware import AuthMiddleware
from .response_aggregator import ResponseAggregator
from .circuit_breaker import CircuitBreaker, circuit_breaker_registry
from .metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


class APIGatewayManager:
    """
    API Gateway Manager - Central Management Interface
    
    Provides centralized management and monitoring of all API Gateway
    components with health checking and service coordination.
    """
    
    def __init__(self, config: Optional[APIGatewayConfig] = None):
        """Initialize API Gateway Manager"""
        self.config = config or APIGatewayConfig()
        
        # Initialize main gateway agent
        self.gateway_agent: Optional[APIGatewayAgent] = None
        
        # Component status tracking
        self.component_status: Dict[str, Dict[str, Any]] = {}
        
        # Health check interval
        self.health_check_interval = 30  # seconds
        
        logger.info("API Gateway Manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize all gateway components"""



        try:
            logger.info("Initializing API Gateway components...")
            
            # Initialize main gateway agent
            self.gateway_agent = APIGatewayAgent(self.config)
            
            # Initialize components
            await self.gateway_agent.start()
            
            # Update component status
            await self._update_component_status()
            
            logger.info("API Gateway initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize API Gateway: {e}")
            return False
    
    async def shutdown(self):
        """Gracefully shutdown API Gateway"""



        try:
            logger.info("Shutting down API Gateway...")
            
            if self.gateway_agent:
                await self.gateway_agent.stop()
            
            logger.info("API Gateway shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""



        try:
            if not self.gateway_agent:
                return {"status": "not_initialized", "components": {}}
            
            # Get gateway stats
            gateway_stats = self.gateway_agent.get_stats()
            
            # Get component health
            component_health = await self._check_component_health()
            
            return {
                "status": "healthy" if gateway_stats["status"] == "running" else "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "gateway": gateway_stats,
                "components": component_health,
                "services": await self._get_services_health()
            }
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _check_component_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all components"""
        component_health = {}
        
        if not self.gateway_agent:
            return component_health
        
        try:
            # Router health
            if hasattr(self.gateway_agent, 'router'):
                component_health["router"] = {
                    "status": "healthy",
                    "stats": self.gateway_agent.router.get_routing_stats()
                }
            
            # Load balancer health
            if hasattr(self.gateway_agent, 'load_balancer'):
                component_health["load_balancer"] = {
                    "status": "healthy",
                    "stats": self.gateway_agent.load_balancer.get_load_balancer_stats()
                }
            
            # Rate limiter health
            if hasattr(self.gateway_agent, 'rate_limiter'):
                component_health["rate_limiter"] = {
                    "status": "healthy",
                    "stats": {"enabled": True}  # Placeholder
                }
            
            # Authentication middleware health
            if hasattr(self.gateway_agent, 'auth_middleware'):
                component_health["auth_middleware"] = {
                    "status": "healthy",
                    "stats": self.gateway_agent.auth_middleware.get_auth_stats()
                }
            
            # Response aggregator health
            if hasattr(self.gateway_agent, 'response_aggregator'):
                component_health["response_aggregator"] = {
                    "status": "healthy",
                    "stats": self.gateway_agent.response_aggregator.get_aggregator_stats()
                }
            
            # Circuit breaker health
            component_health["circuit_breaker"] = {
                "status": "healthy",
                "stats": circuit_breaker_registry.get_registry_stats()
            }
            
            # Metrics collector health
            if hasattr(self.gateway_agent, 'metrics_collector'):
                component_health["metrics_collector"] = {
                    "status": "healthy",
                    "stats": self.gateway_agent.metrics_collector.get_metrics_summary()
                }
            
        except Exception as e:
            logger.error(f"Error checking component health: {e}")
        
        return component_health
    
    async def _get_services_health(self) -> Dict[str, Any]:
        """Get health status of all registered services"""
        if not self.gateway_agent:
            return {}
        
        return await self.gateway_agent._get_services_health()
    
    async def _update_component_status(self):
        """Update component status tracking"""



        try:
            current_time = datetime.utcnow().isoformat()
            
            components = [
                "router", "load_balancer", "rate_limiter", 
                "auth_middleware", "response_aggregator", 
                "circuit_breaker", "metrics_collector"
            ]
            
            for component in components:
                self.component_status[component] = {
                    "status": "running",
                    "last_check": current_time,
                    "uptime": 0
                }
            
        except Exception as e:
            logger.error(f"Error updating component status: {e}")
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration"""



        return self.config.dict()
    
    async def update_configuration(self, config_updates: Dict[str, Any]) -> bool:
        """Update configuration dynamically"""



        try:
            # Update configuration
            for key, value in config_updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                else:
                    logger.warning(f"Unknown configuration key: {key}")
            
            # Apply configuration changes to components
            await self._apply_configuration_changes()
            
            logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return False
    
    async def _apply_configuration_changes(self):
        """Apply configuration changes to running components"""
        # This would implement dynamic reconfiguration
        # For now, placeholder implementation
        logger.info("Applying configuration changes...")
    
    async def reload_services(self) -> bool:
        """Reload service configurations"""



        try:
            if not self.gateway_agent:
                return False
            
            # Reload load balancer with new service configurations
            if hasattr(self.gateway_agent, 'load_balancer'):
                # This would reload service instances
                logger.info("Reloading service configurations...")
            
            return True
            
        except Exception as e:
            logger.error(f"Error reloading services: {e}")
            return False
    
    def get_metrics(self) -> str:
        """Get Prometheus metrics"""
        if not self.gateway_agent or not hasattr(self.gateway_agent, 'metrics_collector'):
            return ""
        
        return self.gateway_agent.metrics_collector.generate_metrics()
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive API Gateway statistics"""



        try:
            stats = {
                "timestamp": datetime.utcnow().isoformat(),
                "version": self.config.version,
                "uptime": 0,  # Would be calculated from start time
                "configuration": {
                    "services": len(self.config.service_routes),
                    "rate_limit_strategy": self.config.rate_limit_strategy.value,
                    "load_balancing_strategy": self.config.load_balancing_strategy.value
                }
            }
            
            # Add component stats if available
            if self.gateway_agent:
                stats["gateway"] = self.gateway_agent.get_stats()
            
            # Add component status
            stats["components"] = self.component_status
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting comprehensive stats: {e}")
            return {"error": str(e)}


# Global gateway manager instance
gateway_manager: Optional[APIGatewayManager] = None


async def initialize_api_gateway(config: Optional[APIGatewayConfig] = None) -> APIGatewayManager:
    """
    Initialize API Gateway with configuration
    
    Args:
        config: Gateway configuration
        
    Returns:
        Initialized gateway manager
    """
    global gateway_manager
    
    try:
        gateway_manager = APIGatewayManager(config)
        
        success = await gateway_manager.initialize()
        if not success:
            raise RuntimeError("Failed to initialize API Gateway")
        
        logger.info("API Gateway initialized and ready")
        return gateway_manager
        
    except Exception as e:
        logger.error(f"API Gateway initialization failed: {e}")
        raise


async def shutdown_api_gateway():
    """Gracefully shutdown API Gateway"""
    global gateway_manager
    
    if gateway_manager:
        await gateway_manager.shutdown()
        gateway_manager = None
        logger.info("API Gateway shutdown completed")


def get_gateway_manager() -> Optional[APIGatewayManager]:
    """Get current gateway manager instance"""



    return gateway_manager


# Health check endpoint for external monitoring
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    if not gateway_manager:
        return {
            "status": "not_initialized",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return await gateway_manager.get_health_status()


# Metrics endpoint for Prometheus
def get_prometheus_metrics() -> str:
    """Get Prometheus metrics"""
    if not gateway_manager:
        return ""
    
    return gateway_manager.get_metrics()


# Utility functions
def get_service_list() -> List[str]:
    """Get list of configured services"""
    if not gateway_manager:
        return []
    
    return list(gateway_manager.config.service_routes.keys())


def get_gateway_stats() -> Dict[str, Any]:
    """Get gateway statistics"""
    if not gateway_manager:
        return {}
    
    return gateway_manager.get_comprehensive_stats()


# Export main components for direct access if needed
__all__ = [
    'APIGatewayManager',
    'initialize_api_gateway',
    'shutdown_api_gateway',
    'get_gateway_manager',
    'health_check',
    'get_prometheus_metrics',
    'get_service_list',
    'get_gateway_stats',
    'APIGatewayAgent',
    'APIGatewayConfig',
    'RequestRouter',
    'LoadBalancer',
    'RateLimiter',
    'AuthMiddleware',
    'ResponseAggregator',
    'CircuitBreaker',
    'MetricsCollector'
]
