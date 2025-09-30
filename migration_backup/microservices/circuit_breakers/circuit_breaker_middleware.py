"""
Circuit Breaker Middleware - Ainflue Platform
============================================

Middleware circuit breaker pour intégration frameworks.
FastAPI + Django + Flask + gRPC + message brokers integration.

Author: Fahed Mlaiel (mlaiel@live.de)
Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture circuit breakers et tous ses patterns sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, distribution 
ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est STRICTEMENT INTERDITE.

Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, Callable, Union, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
import json
import inspect

# Framework imports with graceful degradation
try:
    from fastapi import Request, Response, HTTPException
    from fastapi.responses import JSONResponse
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    Request = Response = HTTPException = JSONResponse = None

try:
    from flask import Flask, request as flask_request, jsonify
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    Flask = flask_request = jsonify = None

try:
    import grpc
    from grpc import ServicerContext
    HAS_GRPC = True
except ImportError:
    HAS_GRPC = False
    grpc = ServicerContext = None

# Import our circuit breaker components
from .enterprise_circuit_breaker import EnterpriseCircuitBreaker, EnterpriseCircuitConfig, CircuitState

logger = logging.getLogger(__name__)

class FrameworkType(Enum):
    """Supported framework types"""
    FASTAPI = "FASTAPI"
    FLASK = "FLASK"
    DJANGO = "DJANGO"
    GRPC = "GRPC"
    GENERIC = "GENERIC"

class RequestCriticality(Enum):
    """Request criticality levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class EndpointConfig:
    """Configuration for specific endpoint"""
    path: str
    method: str = "GET"
    criticality: RequestCriticality = RequestCriticality.MEDIUM
    circuit_config: Optional[EnterpriseCircuitConfig] = None
    custom_fallback: Optional[Callable] = None
    enable_metrics: bool = True
    timeout_override: Optional[float] = None

@dataclass
class FrameworkConfig:
    """Framework-specific configuration"""
    framework_type: FrameworkType
    service_name: str
    endpoints: List[EndpointConfig] = field(default_factory=list)
    global_circuit_config: Optional[EnterpriseCircuitConfig] = None
    enable_auto_registration: bool = True
    enable_request_classification: bool = True
    enable_response_analysis: bool = True
    metrics_collection: bool = True

class RequestClassifier:
    """Classify requests by criticality and characteristics"""
    
    def __init__(self):
        self.classification_rules = {}
        self.learned_patterns = {}
    
    async def classify_request(self, request_info: Dict[str, Any]) -> RequestCriticality:
        """Classify request criticality"""
        try:
            # Extract request characteristics
            path = request_info.get('path', '/')
            method = request_info.get('method', 'GET')
            headers = request_info.get('headers', {})
            
            # Rule-based classification
            if self._is_critical_endpoint(path, method):
                return RequestCriticality.CRITICAL
            elif self._is_high_priority_request(headers):
                return RequestCriticality.HIGH
            elif method in ['POST', 'PUT', 'DELETE']:
                return RequestCriticality.MEDIUM
            else:
                return RequestCriticality.LOW
                
        except Exception as e:
            logger.debug(f"Request classification failed: {str(e)}")
            return RequestCriticality.MEDIUM
    
    def _is_critical_endpoint(self, path: str, method: str) -> bool:
        """Check if endpoint is critical"""
        critical_patterns = [
            '/api/auth/',
            '/api/payment/',
            '/api/emergency/',
            '/health',
            '/metrics'
        ]
        
        return any(pattern in path for pattern in critical_patterns)
    
    def _is_high_priority_request(self, headers: Dict[str, Any]) -> bool:
        """Check if request has high priority indicators"""
        priority_headers = headers.get('x-priority', '').lower()
        user_type = headers.get('x-user-type', '').lower()
        
        return (priority_headers in ['high', 'urgent'] or 
                user_type in ['premium', 'admin', 'vip'])
    
    async def learn_from_feedback(self, request_info: Dict[str, Any], 
                                 actual_criticality: RequestCriticality):
        """Learn from classification feedback"""
        # Store learning data for future improvements
        key = f"{request_info.get('path', '')}_{request_info.get('method', '')}"
        self.learned_patterns[key] = actual_criticality

class ResponseAnalyzer:
    """Analyze responses to determine success/failure patterns"""
    
    def __init__(self):
        self.response_patterns = {}
        self.error_patterns = {}
    
    async def analyze_response(self, response_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze response for circuit breaker decisions"""
        try:
            status_code = response_info.get('status_code', 200)
            response_time = response_info.get('response_time', 0.0)
            content_length = response_info.get('content_length', 0)
            
            analysis = {
                'is_success': self._is_successful_response(status_code),
                'is_timeout': response_time > 30000,  # 30 seconds
                'is_server_error': 500 <= status_code < 600,
                'is_client_error': 400 <= status_code < 500,
                'response_time': response_time,
                'failure_type': self._classify_failure_type(status_code, response_time)
            }
            
            return analysis
            
        except Exception as e:
            logger.debug(f"Response analysis failed: {str(e)}")
            return {'is_success': False, 'failure_type': 'analysis_error'}
    
    def _is_successful_response(self, status_code: int) -> bool:
        """Check if response indicates success"""
        return 200 <= status_code < 400
    
    def _classify_failure_type(self, status_code: int, response_time: float) -> str:
        """Classify the type of failure"""
        if response_time > 30000:
            return 'timeout'
        elif status_code == 503:
            return 'service_unavailable'
        elif status_code == 502:
            return 'bad_gateway'
        elif status_code == 500:
            return 'internal_server_error'
        elif status_code == 429:
            return 'rate_limited'
        elif 400 <= status_code < 500:
            return 'client_error'
        else:
            return 'unknown'

class CircuitRegistry:
    """Registry for managing circuit breakers per endpoint"""
    
    def __init__(self):
        self.circuits: Dict[str, EnterpriseCircuitBreaker] = {}
        self.endpoint_configs: Dict[str, EndpointConfig] = {}
        self.registry_lock = asyncio.Lock()
    
    async def get_or_create_circuit(self, endpoint_key: str, 
                                   config: Optional[EnterpriseCircuitConfig] = None) -> EnterpriseCircuitBreaker:
        """Get existing circuit or create new one"""
        async with self.registry_lock:
            if endpoint_key not in self.circuits:
                circuit_config = config or EnterpriseCircuitConfig()
                self.circuits[endpoint_key] = EnterpriseCircuitBreaker(
                    service_name=endpoint_key,
                    config=circuit_config
                )
                logger.info(f"Created new circuit breaker for endpoint: {endpoint_key}")
            
            return self.circuits[endpoint_key]
    
    async def register_endpoint(self, endpoint_config: EndpointConfig):
        """Register endpoint configuration"""
        endpoint_key = f"{endpoint_config.method}:{endpoint_config.path}"
        self.endpoint_configs[endpoint_key] = endpoint_config
        
        # Pre-create circuit if needed
        await self.get_or_create_circuit(endpoint_key, endpoint_config.circuit_config)
    
    async def get_circuit_status(self) -> Dict[str, Any]:
        """Get status of all registered circuits"""
        circuit_status = {}
        
        for endpoint_key, circuit in self.circuits.items():
            circuit_status[endpoint_key] = await circuit.get_metrics()
        
        return circuit_status
    
    async def reset_circuit(self, endpoint_key: str, reason: str = "Manual reset"):
        """Reset specific circuit"""
        if endpoint_key in self.circuits:
            await self.circuits[endpoint_key].reset(reason)

class CircuitBreakerMiddleware:
    """
    Middleware circuit breaker pour intégration frameworks.
    FastAPI + Django + Flask + gRPC + message brokers integration.
    """
    
    def __init__(self, framework_config: FrameworkConfig):
        self.framework_config = framework_config
        self.circuit_registry = CircuitRegistry()
        self.request_classifier = RequestClassifier() if framework_config.enable_request_classification else None
        self.response_analyzer = ResponseAnalyzer() if framework_config.enable_response_analysis else None
        
        # Metrics collection
        self.request_metrics = {}
        self.performance_metrics = {}
        
        logger.info(f"Circuit breaker middleware initialized for {framework_config.framework_type.value}")
    
    async def initialize(self):
        """Initialize middleware with endpoint configurations"""
        for endpoint_config in self.framework_config.endpoints:
            await self.circuit_registry.register_endpoint(endpoint_config)
    
    # FastAPI Integration
    async def fastapi_middleware(self, request: Request, call_next: Callable) -> Response:
        """
        Middleware FastAPI avec circuit breaker protection.
        
        Features:
        - Automatic endpoint registration
        - Request classification par criticité
        - Response analysis pour failure detection
        - Graceful degradation responses
        - Custom error handling per endpoint
        """
        if not HAS_FASTAPI:
            logger.error("FastAPI not available")
            return JSONResponse(
                status_code=500,
                content={"error": "FastAPI not available"}
            )
        
        start_time = time.time()
        endpoint_key = f"{request.method}:{request.url.path}"
        
        try:
            # Get or create circuit breaker
            circuit = await self.circuit_registry.get_or_create_circuit(endpoint_key)
            
            # Extract request info
            request_info = {
                'path': request.url.path,
                'method': request.method,
                'headers': dict(request.headers),
                'query_params': dict(request.query_params)
            }
            
            # Classify request if enabled
            criticality = RequestCriticality.MEDIUM
            if self.request_classifier:
                criticality = await self.request_classifier.classify_request(request_info)
            
            # Execute with circuit breaker protection
            context = {
                'criticality': criticality.value,
                'endpoint': endpoint_key,
                'framework': 'fastapi'
            }
            
            async def protected_call():
                return await call_next(request)
            
            response = await circuit.execute_with_protection(
                protected_call,
                context
            )
            
            # Analyze response if it's a real Response object
            if hasattr(response, 'status_code'):
                response_time = (time.time() - start_time) * 1000
                
                response_info = {
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'content_length': len(getattr(response, 'body', b''))
                }
                
                if self.response_analyzer:
                    analysis = await self.response_analyzer.analyze_response(response_info)
                    
                    # Record metrics
                    await self._record_request_metrics(endpoint_key, analysis, response_time)
            
            return response
            
        except Exception as e:
            # Handle circuit breaker exceptions
            response_time = (time.time() - start_time) * 1000
            
            if "Circuit breaker" in str(e):
                return await self._create_fastapi_fallback_response(endpoint_key, str(e))
            
            # Record failure
            await self._record_request_metrics(endpoint_key, {'is_success': False}, response_time)
            
            # Re-raise for FastAPI to handle
            raise e
    
    async def _create_fastapi_fallback_response(self, endpoint_key: str, error_message: str) -> JSONResponse:
        """Create fallback response for FastAPI"""
        # Get endpoint configuration for custom fallback
        endpoint_config = self.circuit_registry.endpoint_configs.get(endpoint_key)
        
        if endpoint_config and endpoint_config.custom_fallback:
            try:
                return await endpoint_config.custom_fallback()
            except Exception as e:
                logger.error(f"Custom fallback failed: {str(e)}")
        
        # Default fallback response
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service temporarily unavailable",
                "message": error_message,
                "fallback": True,
                "endpoint": endpoint_key
            }
        )
    
    # Flask Integration
    def flask_middleware(self, app: Flask):
        """Flask middleware integration"""
        if not HAS_FLASK:
            logger.error("Flask not available")
            return
        
        @app.before_request
        async def before_request():
            flask_request.start_time = time.time()
            flask_request.endpoint_key = f"{flask_request.method}:{flask_request.path}"
        
        @app.after_request
        async def after_request(response):
            if hasattr(flask_request, 'start_time') and hasattr(flask_request, 'endpoint_key'):
                response_time = (time.time() - flask_request.start_time) * 1000
                
                response_info = {
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'content_length': response.content_length or 0
                }
                
                if self.response_analyzer:
                    analysis = await self.response_analyzer.analyze_response(response_info)
                    await self._record_request_metrics(flask_request.endpoint_key, analysis, response_time)
            
            return response
        
        def circuit_breaker_decorator(f):
            """Decorator for Flask routes"""
            async def wrapper(*args, **kwargs):
                endpoint_key = f"{flask_request.method}:{flask_request.path}"
                circuit = await self.circuit_registry.get_or_create_circuit(endpoint_key)
                
                context = {
                    'endpoint': endpoint_key,
                    'framework': 'flask'
                }
                
                try:
                    return await circuit.execute_with_protection(
                        lambda: f(*args, **kwargs),
                        context
                    )
                except Exception as e:
                    if "Circuit breaker" in str(e):
                        return jsonify({
                            "error": "Service temporarily unavailable",
                            "message": str(e),
                            "fallback": True
                        }), 503
                    raise e
            
            return wrapper
        
        app.circuit_breaker = circuit_breaker_decorator
    
    # gRPC Integration
    async def grpc_interceptor(self, method: str, request: Any, context: ServicerContext) -> Any:
        """Interceptor gRPC avec circuit breaker"""
        if not HAS_GRPC:
            logger.error("gRPC not available")
            context.abort(grpc.StatusCode.UNAVAILABLE, "gRPC not available")
            return
        
        endpoint_key = f"GRPC:{method}"
        circuit = await self.circuit_registry.get_or_create_circuit(endpoint_key)
        
        grpc_context = {
            'method': method,
            'framework': 'grpc'
        }
        
        try:
            async def grpc_call():
                # This would be the actual gRPC service method call
                # Implementation depends on specific gRPC setup
                return await self._execute_grpc_method(method, request, context)
            
            return await circuit.execute_with_protection(grpc_call, grpc_context)
            
        except Exception as e:
            if "Circuit breaker" in str(e):
                context.abort(grpc.StatusCode.UNAVAILABLE, f"Circuit breaker open: {str(e)}")
            else:
                context.abort(grpc.StatusCode.INTERNAL, f"Internal error: {str(e)}")
    
    async def _execute_grpc_method(self, method: str, request: Any, context: ServicerContext) -> Any:
        """Execute gRPC method (placeholder for actual implementation)"""
        # This would contain the actual gRPC service logic
        # For now, return a placeholder response
        return {"status": "success", "method": method}
    
    # Message Broker Integration
    async def message_broker_wrapper(self, message: Dict[str, Any], handler: Callable) -> Any:
        """Wrapper message broker avec protection circuit"""
        message_type = message.get('type', 'unknown')
        endpoint_key = f"MESSAGE:{message_type}"
        
        circuit = await self.circuit_registry.get_or_create_circuit(endpoint_key)
        
        broker_context = {
            'message_type': message_type,
            'framework': 'message_broker'
        }
        
        try:
            async def message_handler():
                return await handler(message)
            
            return await circuit.execute_with_protection(message_handler, broker_context)
            
        except Exception as e:
            if "Circuit breaker" in str(e):
                # Handle circuit breaker failure for message processing
                await self._handle_message_circuit_failure(message, str(e))
                return {"status": "circuit_open", "message": str(e)}
            raise e
    
    async def _handle_message_circuit_failure(self, message: Dict[str, Any], error: str):
        """Handle circuit breaker failure for message processing"""
        # Could implement dead letter queue, retry logic, etc.
        logger.warning(f"Message processing failed due to circuit breaker: {error}")
    
    # Database Connection Wrapper
    async def database_connection_wrapper(self, query: str, params: Dict[str, Any]) -> Any:
        """Wrapper connexions DB avec circuit breaker"""
        endpoint_key = f"DATABASE:{self._extract_table_name(query)}"
        circuit = await self.circuit_registry.get_or_create_circuit(endpoint_key)
        
        db_context = {
            'query_type': self._classify_query_type(query),
            'table': self._extract_table_name(query),
            'framework': 'database'
        }
        
        try:
            async def db_operation():
                # This would execute the actual database operation
                return await self._execute_database_query(query, params)
            
            return await circuit.execute_with_protection(db_operation, db_context)
            
        except Exception as e:
            if "Circuit breaker" in str(e):
                # Handle database circuit breaker failure
                return await self._handle_database_circuit_failure(query, params, str(e))
            raise e
    
    def _extract_table_name(self, query: str) -> str:
        """Extract table name from SQL query"""
        query_lower = query.lower().strip()
        
        # Simple table name extraction
        if query_lower.startswith('select'):
            # Find FROM clause
            from_idx = query_lower.find('from')
            if from_idx != -1:
                after_from = query[from_idx + 4:].strip()
                table_name = after_from.split()[0]
                return table_name
        elif query_lower.startswith(('insert', 'update', 'delete')):
            # Find table name after INSERT INTO, UPDATE, DELETE FROM
            words = query.split()
            if len(words) >= 3:
                return words[2] if query_lower.startswith('insert') else words[1]
        
        return 'unknown'
    
    def _classify_query_type(self, query: str) -> str:
        """Classify database query type"""
        query_lower = query.lower().strip()
        
        if query_lower.startswith('select'):
            return 'read'
        elif query_lower.startswith(('insert', 'update', 'delete')):
            return 'write'
        elif query_lower.startswith(('create', 'alter', 'drop')):
            return 'ddl'
        else:
            return 'unknown'
    
    async def _execute_database_query(self, query: str, params: Dict[str, Any]) -> Any:
        """Execute database query (placeholder)"""
        # This would contain actual database execution logic
        return {"query": query, "params": params, "status": "executed"}
    
    async def _handle_database_circuit_failure(self, query: str, params: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Handle database circuit breaker failure"""
        return {
            "status": "circuit_open",
            "error": error,
            "fallback": True,
            "query_type": self._classify_query_type(query)
        }
    
    # Metrics and Monitoring
    async def _record_request_metrics(self, endpoint_key: str, analysis: Dict[str, Any], response_time: float):
        """Record request metrics"""
        if not self.framework_config.metrics_collection:
            return
        
        current_time = datetime.now()
        
        if endpoint_key not in self.request_metrics:
            self.request_metrics[endpoint_key] = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'average_response_time': 0.0,
                'last_updated': current_time
            }
        
        metrics = self.request_metrics[endpoint_key]
        metrics['total_requests'] += 1
        
        if analysis.get('is_success', False):
            metrics['successful_requests'] += 1
        else:
            metrics['failed_requests'] += 1
        
        # Update average response time
        total_time = metrics['average_response_time'] * (metrics['total_requests'] - 1)
        metrics['average_response_time'] = (total_time + response_time) / metrics['total_requests']
        metrics['last_updated'] = current_time
    
    async def get_middleware_metrics(self) -> Dict[str, Any]:
        """Get comprehensive middleware metrics"""
        circuit_status = await self.circuit_registry.get_circuit_status()
        
        return {
            'framework': self.framework_config.framework_type.value,
            'service_name': self.framework_config.service_name,
            'registered_endpoints': len(self.circuit_registry.endpoint_configs),
            'active_circuits': len(self.circuit_registry.circuits),
            'request_metrics': self.request_metrics,
            'circuit_status': circuit_status,
            'configuration': {
                'auto_registration': self.framework_config.enable_auto_registration,
                'request_classification': self.framework_config.enable_request_classification,
                'response_analysis': self.framework_config.enable_response_analysis,
                'metrics_collection': self.framework_config.metrics_collection
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for middleware"""
        healthy_circuits = 0
        total_circuits = len(self.circuit_registry.circuits)
        
        for circuit in self.circuit_registry.circuits.values():
            circuit_metrics = await circuit.get_metrics()
            if circuit_metrics['state'] != CircuitState.OPEN.value:
                healthy_circuits += 1
        
        health_percentage = (healthy_circuits / total_circuits * 100) if total_circuits > 0 else 100
        
        return {
            'status': 'healthy' if health_percentage > 50 else 'degraded',
            'health_percentage': health_percentage,
            'healthy_circuits': healthy_circuits,
            'total_circuits': total_circuits,
            'framework': self.framework_config.framework_type.value,
            'timestamp': datetime.now().isoformat()
        }

# Helper functions for framework integration
def create_fastapi_middleware(service_name: str, endpoints: List[EndpointConfig] = None) -> CircuitBreakerMiddleware:
    """Create FastAPI middleware"""
    config = FrameworkConfig(
        framework_type=FrameworkType.FASTAPI,
        service_name=service_name,
        endpoints=endpoints or []
    )
    return CircuitBreakerMiddleware(config)

def create_flask_middleware(app: Flask, service_name: str) -> CircuitBreakerMiddleware:
    """Create Flask middleware"""
    config = FrameworkConfig(
        framework_type=FrameworkType.FLASK,
        service_name=service_name
    )
    middleware = CircuitBreakerMiddleware(config)
    middleware.flask_middleware(app)
    return middleware

def create_grpc_interceptor(service_name: str) -> CircuitBreakerMiddleware:
    """Create gRPC interceptor"""
    config = FrameworkConfig(
        framework_type=FrameworkType.GRPC,
        service_name=service_name
    )
    return CircuitBreakerMiddleware(config)

# Export main classes
__all__ = [
    'CircuitBreakerMiddleware',
    'FrameworkConfig',
    'EndpointConfig',
    'FrameworkType',
    'RequestCriticality',
    'RequestClassifier',
    'ResponseAnalyzer',
    'CircuitRegistry',
    'create_fastapi_middleware',
    'create_flask_middleware',
    'create_grpc_interceptor'
]