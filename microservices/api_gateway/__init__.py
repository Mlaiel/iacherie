"""
🔗 API Gateway Module - Enterprise API Gateway Services
=======================================================

Provides enterprise API gateway functionality including authentication, 
rate limiting, routing, monitoring, and security for the Ainflue platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

__all__ = [
    'APIGateway',
    'APIManagement', 
    'GatewayAuthentication',
    'GatewayAuthorization',
    'GatewayRateLimiting',
    'GatewayLoadBalancer',
    'GatewayMonitoring',
    'GatewaySecurity',
    'api_gateway_module'
]

class APIGatewayModule:
    """
    🔗 Enterprise API Gateway Module
    
    Central module for all API gateway services including:
    - API Gateway Service (routing and proxy)
    - API Management Service (lifecycle management)
    - Gateway Authentication (OAuth2, JWT, multi-tenant)
    - Gateway Authorization (RBAC, policies)
    - Gateway Rate Limiting (intelligent rate limiting)
    - Gateway Load Balancer (intelligent load balancing)
    - Gateway Monitoring (metrics and observability)
    - Gateway Security (threat detection, WAF)
    """
    
    def __init__(self):
        """Initialize the API Gateway module."""
        self.services = {}
        self.routes = {}
        self.middleware = []
        self.is_initialized = False
        
        logger.info("🔗 API Gateway Module initialized")
    
    async def initialize(self):
        """Initialize all gateway services."""
        try:
            # Import and initialize services
            from .api_gateway_service import APIGatewayService
            from .api_management_service import APIManagementService
            from .gateway_authentication import GatewayAuthentication
            from .gateway_authorization import GatewayAuthorization
            from .gateway_rate_limiting import GatewayRateLimiting
            from .gateway_load_balancer import GatewayLoadBalancer, LoadBalancerConfig
            from .gateway_monitoring import GatewayMonitoring
            from .gateway_security import GatewaySecurity
            
            # Initialize services
            self.api_gateway = APIGatewayService()
            self.api_management = APIManagementService()
            self.authentication = GatewayAuthentication()
            self.authorization = GatewayAuthorization()
            self.rate_limiting = GatewayRateLimiting()
            self.load_balancer = GatewayLoadBalancer(LoadBalancerConfig())
            self.monitoring = GatewayMonitoring()
            self.security = GatewaySecurity()
            
            self.is_initialized = True
            logger.info("✅ API Gateway Module fully initialized")
            return True
            
        except ImportError as e:
            logger.warning(f"⚠️ Some gateway services not available: {e}")
            return False
    
    async def start_services(self):
        """Start all gateway services."""
        if not self.is_initialized:
            await self.initialize()
        
        services_to_start = [
            ('load_balancer', self.load_balancer),
            ('monitoring', self.monitoring),
            ('security', self.security),
            ('rate_limiting', self.rate_limiting),
            ('authentication', self.authentication),
            ('authorization', self.authorization)
        ]
        
        started_count = 0
        for service_name, service in services_to_start:
            try:
                if hasattr(service, 'start'):
                    await service.start()
                    started_count += 1
                    logger.info(f"✅ Started {service_name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to start {service_name}: {e}")
        
        logger.info(f"🚀 API Gateway services started: {started_count}/{len(services_to_start)}")
        return started_count > 0
    
    def get_services(self) -> List[str]:
        """Get list of available services."""
        return [
            'api_gateway_service',
            'api_management_service', 
            'gateway_authentication',
            'gateway_authorization',
            'gateway_rate_limiting',
            'gateway_load_balancer',
            'gateway_monitoring',
            'gateway_security'
        ]


# Global module instance
api_gateway_module = APIGatewayModule()

# Legacy compatibility classes
class APIGateway:
    """Main API Gateway service (legacy compatibility)"""
    
    def __init__(self):
        self.services = {}
        self.routes = {}
        self.middleware = []
        
    def register_service(self, name: str, service_config: Dict[str, Any]):
        """Register a backend service"""
        self.services[name] = service_config
        logger.info(f"Registered service: {name}")
        
    def add_route(self, path: str, service: str, methods: List[str] = None):
        """Add a route to a backend service"""
        if methods is None:
            methods = ['GET']
        
        self.routes[path] = {
            'service': service,
            'methods': methods
        }
        logger.info(f"Added route: {path} -> {service}")
        
    def add_middleware(self, middleware_func):
        """Add middleware to the gateway"""
        self.middleware.append(middleware_func)
        logger.info("Added middleware")

# Import gateway services
try:
    from .api_gateway_service import *
    from .api_management_service import *
    from .gateway_authentication import *
    from .gateway_authorization import *
    from .gateway_rate_limiting import *
    from .gateway_load_balancer import *
    from .gateway_monitoring import *
    from .gateway_security import *
except ImportError as e:
    logger.warning(f"Some gateway services not available: {e}")