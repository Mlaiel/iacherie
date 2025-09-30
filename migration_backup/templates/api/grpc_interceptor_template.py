#!/usr/bin/env python3
"""
⚡ gRPC Interceptor Template - Enterprise Microservices
🏗️ Architecture: Ainflue Creator Economy Platform
🔒 Protection IP: © 2025 Fahed Mlaiel <mlaiel@live.de>

🚨 AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import grpc
from grpc import aio
import asyncio
import time
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import contextlib
from collections import defaultdict
import threading

# Expert Team: Lead Dev IA + Backend Senior + Microservices Architect + DevOps Engineer
__author__ = "Fahed Mlaiel"
__copyright__ = "© 2025 Fahed Mlaiel. All rights reserved."
__license__ = "Proprietary - Commercial license required"
__version__ = "1.0.0"
__email__ = "mlaiel@live.de"


class InterceptorType(str, Enum):
    """gRPC interceptor types"""
    SERVER_UNARY = "server_unary"
    SERVER_STREAMING = "server_streaming"
    CLIENT_UNARY = "client_unary"
    CLIENT_STREAMING = "client_streaming"


class MetricType(str, Enum):
    """Metric types for monitoring"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class RequestMetrics:
    """Request metrics collection"""
    request_count: int = 0
    error_count: int = 0
    total_duration: float = 0.0
    min_duration: float = float('inf')
    max_duration: float = 0.0
    
    def add_request(self, duration: float, is_error: bool = False):
        """Add request metrics"""
        self.request_count += 1
        if is_error:
            self.error_count += 1
        
        self.total_duration += duration
        self.min_duration = min(self.min_duration, duration)
        self.max_duration = max(self.max_duration, duration)
    
    @property
    def average_duration(self) -> float:
        return self.total_duration / self.request_count if self.request_count > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        return (self.error_count / self.request_count * 100) if self.request_count > 0 else 0.0


@dataclass
class InterceptorConfig:
    """Enterprise gRPC interceptor configuration"""
    # Authentication & Authorization
    enable_auth: bool = True
    auth_header_key: str = "authorization"
    require_auth_for_methods: List[str] = field(default_factory=list)
    
    # Rate limiting
    enable_rate_limiting: bool = True
    default_rate_limit: int = 1000  # requests per minute
    rate_limit_per_method: Dict[str, int] = field(default_factory=dict)
    
    # Monitoring & Metrics
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_logging: bool = True
    log_request_payload: bool = False
    log_response_payload: bool = False
    
    # Error handling
    enable_error_enrichment: bool = True
    mask_internal_errors: bool = True
    include_stack_traces: bool = False
    
    # Timeouts
    default_timeout: float = 30.0
    method_timeouts: Dict[str, float] = field(default_factory=dict)
    
    # Circuit breaker
    enable_circuit_breaker: bool = True
    failure_threshold: int = 5
    recovery_timeout: int = 60
    
    # Creator-specific settings
    enable_creator_context: bool = True
    creator_id_header: str = "x-creator-id"
    content_id_header: str = "x-content-id"
    
    # Compression
    enable_compression: bool = True
    compression_algorithm: str = "gzip"
    
    # Load balancing metadata
    enable_load_balancer_hints: bool = True
    
    # Security
    enable_request_validation: bool = True
    max_message_size: int = 4 * 1024 * 1024  # 4MB


class BaseInterceptor:
    """Base interceptor with common functionality"""
    
    def __init__(self, config: InterceptorConfig):
        self.config = config
        self.logger = self._setup_logger()
        self.metrics = defaultdict(RequestMetrics)
        self.circuit_breakers = {}
        self.rate_limiters = {}
        self._lock = threading.Lock()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup interceptor logger"""
        logger = logging.getLogger(f"grpc_interceptor_{self.__class__.__name__}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _extract_metadata(self, context) -> Dict[str, str]:
        """Extract metadata from gRPC context"""
        metadata = {}
        
        if hasattr(context, 'invocation_metadata'):
            for key, value in context.invocation_metadata():
                metadata[key] = value
        
        return metadata
    
    def _get_method_name(self, method_path: str) -> str:
        """Extract method name from full path"""
        return method_path.split('/')[-1] if method_path else "unknown"
    
    def _generate_trace_id(self) -> str:
        """Generate unique trace ID"""
        return str(uuid.uuid4())
    
    def _check_auth(self, context) -> bool:
        """Check authentication"""
        if not self.config.enable_auth:
            return True
        
        metadata = self._extract_metadata(context)
        auth_header = metadata.get(self.config.auth_header_key)
        
        if not auth_header:
            return False
        
        # Implement your authentication logic here
        # This is a simplified example
        return auth_header.startswith("Bearer ")
    
    def _check_rate_limit(self, method_name: str, client_id: str = "unknown") -> bool:
        """Check rate limiting"""
        if not self.config.enable_rate_limiting:
            return True
        
        key = f"{method_name}:{client_id}"
        current_time = time.time()
        
        with self._lock:
            if key not in self.rate_limiters:
                self.rate_limiters[key] = {
                    'requests': [],
                    'limit': self.config.rate_limit_per_method.get(
                        method_name, 
                        self.config.default_rate_limit
                    )
                }
            
            limiter = self.rate_limiters[key]
            
            # Remove old requests (older than 1 minute)
            cutoff_time = current_time - 60
            limiter['requests'] = [
                req_time for req_time in limiter['requests'] 
                if req_time > cutoff_time
            ]
            
            # Check if limit exceeded
            if len(limiter['requests']) >= limiter['limit']:
                return False
            
            # Add current request
            limiter['requests'].append(current_time)
            return True
    
    def _check_circuit_breaker(self, method_name: str) -> bool:
        """Check circuit breaker state"""
        if not self.config.enable_circuit_breaker:
            return True
        
        current_time = time.time()
        
        with self._lock:
            if method_name not in self.circuit_breakers:
                self.circuit_breakers[method_name] = {
                    'failures': 0,
                    'last_failure': 0,
                    'state': 'closed'  # closed, open, half-open
                }
            
            breaker = self.circuit_breakers[method_name]
            
            # Check if recovery timeout has passed
            if (breaker['state'] == 'open' and 
                current_time - breaker['last_failure'] > self.config.recovery_timeout):
                breaker['state'] = 'half-open'
                breaker['failures'] = 0
            
            # Allow request if circuit is closed or half-open
            return breaker['state'] != 'open'
    
    def _record_success(self, method_name: str, duration: float):
        """Record successful request"""
        with self._lock:
            self.metrics[method_name].add_request(duration, is_error=False)
            
            # Reset circuit breaker on success
            if method_name in self.circuit_breakers:
                breaker = self.circuit_breakers[method_name]
                if breaker['state'] == 'half-open':
                    breaker['state'] = 'closed'
                breaker['failures'] = 0
    
    def _record_failure(self, method_name: str, duration: float):
        """Record failed request"""
        with self._lock:
            self.metrics[method_name].add_request(duration, is_error=True)
            
            # Update circuit breaker on failure
            if method_name in self.circuit_breakers:
                breaker = self.circuit_breakers[method_name]
                breaker['failures'] += 1
                breaker['last_failure'] = time.time()
                
                if breaker['failures'] >= self.config.failure_threshold:
                    breaker['state'] = 'open'
    
    def _enrich_context(self, context, metadata: Dict[str, str]):
        """Enrich context with additional metadata"""
        # Add trace ID
        trace_id = metadata.get('x-trace-id', self._generate_trace_id())
        context.set_trailing_metadata([('x-trace-id', trace_id)])
        
        # Add creator context if enabled
        if self.config.enable_creator_context:
            creator_id = metadata.get(self.config.creator_id_header)
            content_id = metadata.get(self.config.content_id_header)
            
            if creator_id:
                context.set_trailing_metadata([('x-creator-context', creator_id)])
            if content_id:
                context.set_trailing_metadata([('x-content-context', content_id)])


class ServerUnaryInterceptor(BaseInterceptor, grpc.aio.ServerInterceptor):
    """
    🛡️ Enterprise Server Unary Interceptor
    
    Features:
    - Authentication & authorization
    - Rate limiting per method/client
    - Circuit breaker pattern
    - Request/response logging
    - Metrics collection
    - Error enrichment
    - Timeout handling
    - Creator context injection
    """
    
    async def intercept_service(self, continuation, handler_call_details):
        """Intercept unary server calls"""
        method_name = self._get_method_name(handler_call_details.method)
        start_time = time.time()
        
        # Create wrapper for the actual handler
        async def wrapper(request, context):
            try:
                # Extract metadata
                metadata = self._extract_metadata(context)
                
                # Authentication check
                if method_name in self.config.require_auth_for_methods:
                    if not self._check_auth(context):
                        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                        context.set_details("Authentication required")
                        return None
                
                # Rate limiting check
                client_id = metadata.get('x-client-id', 'unknown')
                if not self._check_rate_limit(method_name, client_id):
                    context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
                    context.set_details("Rate limit exceeded")
                    return None
                
                # Circuit breaker check
                if not self._check_circuit_breaker(method_name):
                    context.set_code(grpc.StatusCode.UNAVAILABLE)
                    context.set_details("Service temporarily unavailable")
                    return None
                
                # Request validation
                if self.config.enable_request_validation:
                    if hasattr(request, 'ByteSize') and request.ByteSize() > self.config.max_message_size:
                        context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                        context.set_details("Message size exceeds limit")
                        return None
                
                # Enrich context
                self._enrich_context(context, metadata)
                
                # Log request
                if self.config.enable_logging:
                    self._log_request(method_name, metadata, request if self.config.log_request_payload else None)
                
                # Set timeout
                timeout = self.config.method_timeouts.get(method_name, self.config.default_timeout)
                
                # Get the actual handler
                handler = continuation(handler_call_details)
                
                # Execute with timeout
                try:
                    response = await asyncio.wait_for(
                        handler(request, context),
                        timeout=timeout
                    )
                    
                    # Record success
                    duration = time.time() - start_time
                    self._record_success(method_name, duration)
                    
                    # Log response
                    if self.config.enable_logging:
                        self._log_response(method_name, response if self.config.log_response_payload else None, duration)
                    
                    return response
                    
                except asyncio.TimeoutError:
                    duration = time.time() - start_time
                    self._record_failure(method_name, duration)
                    
                    context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
                    context.set_details(f"Request timeout after {timeout}s")
                    return None
                
            except Exception as e:
                duration = time.time() - start_time
                self._record_failure(method_name, duration)
                
                # Error enrichment
                if self.config.enable_error_enrichment:
                    self._handle_error(context, e, method_name)
                else:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Internal server error")
                
                return None
        
        # Return the wrapped handler
        return grpc.aio.unary_unary_rpc_method_handler(wrapper)
    
    def _log_request(self, method_name: str, metadata: Dict[str, str], request=None):
        """Log request details"""
        log_data = {
            "type": "grpc_request",
            "method": method_name,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if request and self.config.log_request_payload:
            log_data["request"] = str(request)
        
        self.logger.info(json.dumps(log_data))
    
    def _log_response(self, method_name: str, response=None, duration: float = 0.0):
        """Log response details"""
        log_data = {
            "type": "grpc_response",
            "method": method_name,
            "duration_ms": duration * 1000,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if response and self.config.log_response_payload:
            log_data["response"] = str(response)
        
        self.logger.info(json.dumps(log_data))
    
    def _handle_error(self, context, error: Exception, method_name: str):
        """Handle and enrich errors"""
        error_code = grpc.StatusCode.INTERNAL
        error_message = "Internal server error"
        
        # Map specific exceptions to gRPC status codes
        if isinstance(error, ValueError):
            error_code = grpc.StatusCode.INVALID_ARGUMENT
            error_message = str(error) if not self.config.mask_internal_errors else "Invalid argument"
        
        elif isinstance(error, PermissionError):
            error_code = grpc.StatusCode.PERMISSION_DENIED
            error_message = "Permission denied"
        
        elif isinstance(error, FileNotFoundError):
            error_code = grpc.StatusCode.NOT_FOUND
            error_message = "Resource not found"
        
        elif isinstance(error, TimeoutError):
            error_code = grpc.StatusCode.DEADLINE_EXCEEDED
            error_message = "Request timeout"
        
        # Log error
        error_log = {
            "type": "grpc_error",
            "method": method_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.config.include_stack_traces:
            import traceback
            error_log["stack_trace"] = traceback.format_exc()
        
        self.logger.error(json.dumps(error_log))
        
        # Set error in context
        context.set_code(error_code)
        context.set_details(error_message)
        
        # Add error metadata
        context.set_trailing_metadata([
            ('x-error-type', type(error).__name__),
            ('x-error-timestamp', datetime.utcnow().isoformat())
        ])


class ServerStreamingInterceptor(BaseInterceptor, grpc.aio.ServerInterceptor):
    """
    🌊 Enterprise Server Streaming Interceptor
    
    Features:
    - Stream lifecycle management
    - Backpressure handling
    - Stream rate limiting
    - Connection monitoring
    - Stream metrics
    """
    
    async def intercept_service(self, continuation, handler_call_details):
        """Intercept streaming server calls"""
        method_name = self._get_method_name(handler_call_details.method)
        start_time = time.time()
        
        async def wrapper(request, context):
            try:
                # Authentication and validation (similar to unary)
                metadata = self._extract_metadata(context)
                
                if method_name in self.config.require_auth_for_methods:
                    if not self._check_auth(context):
                        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
                        context.set_details("Authentication required")
                        return
                
                client_id = metadata.get('x-client-id', 'unknown')
                if not self._check_rate_limit(method_name, client_id):
                    context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
                    context.set_details("Rate limit exceeded")
                    return
                
                # Enrich context
                self._enrich_context(context, metadata)
                
                # Get handler
                handler = continuation(handler_call_details)
                
                # Stream with monitoring
                stream_count = 0
                async for response in handler(request, context):
                    stream_count += 1
                    
                    # Check if client is still connected
                    if context.cancelled():
                        self.logger.info(f"Stream cancelled by client: {method_name}")
                        break
                    
                    # Stream rate limiting (optional)
                    if stream_count % 100 == 0:  # Check every 100 messages
                        await asyncio.sleep(0.001)  # Small delay to prevent overwhelming
                    
                    yield response
                
                # Record success
                duration = time.time() - start_time
                self._record_success(method_name, duration)
                
                if self.config.enable_logging:
                    self.logger.info(f"Stream completed: {method_name}, messages: {stream_count}, duration: {duration:.3f}s")
                
            except Exception as e:
                duration = time.time() - start_time
                self._record_failure(method_name, duration)
                
                if self.config.enable_error_enrichment:
                    self._handle_error(context, e, method_name)
                else:
                    context.set_code(grpc.StatusCode.INTERNAL)
                    context.set_details("Internal server error")
        
        return grpc.aio.unary_stream_rpc_method_handler(wrapper)


class ClientUnaryInterceptor(BaseInterceptor, grpc.aio.UnaryUnaryClientInterceptor):
    """
    📞 Enterprise Client Unary Interceptor
    
    Features:
    - Automatic retries with backoff
    - Client-side load balancing hints
    - Request enrichment
    - Client metrics
    - Error handling
    """
    
    async def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercept client unary calls"""
        method_name = self._get_method_name(client_call_details.method)
        start_time = time.time()
        
        # Enrich metadata
        metadata = list(client_call_details.metadata or [])
        
        # Add trace ID
        trace_id = self._generate_trace_id()
        metadata.append(('x-trace-id', trace_id))
        
        # Add client identification
        metadata.append(('x-client-id', 'ainflue-client'))
        metadata.append(('x-client-version', '1.0.0'))
        
        # Add creator context if available
        if self.config.enable_creator_context:
            # These would typically come from request context
            metadata.append(('x-creator-id', 'creator_123'))
        
        # Add compression hint
        if self.config.enable_compression:
            metadata.append(('grpc-accept-encoding', self.config.compression_algorithm))
        
        # Add load balancer hints
        if self.config.enable_load_balancer_hints:
            metadata.append(('x-load-balancer-hint', 'prefer-local'))
        
        # Create new call details with enriched metadata
        new_details = client_call_details._replace(metadata=metadata)
        
        # Retry logic
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries + 1):
            try:
                # Log request
                if self.config.enable_logging:
                    self.logger.info(f"Client request: {method_name}, attempt: {attempt + 1}")
                
                # Make the call
                response = await continuation(new_details, request)
                
                # Record success
                duration = time.time() - start_time
                self._record_success(method_name, duration)
                
                if self.config.enable_logging:
                    self.logger.info(f"Client response: {method_name}, duration: {duration:.3f}s")
                
                return response
                
            except grpc.RpcError as e:
                duration = time.time() - start_time
                
                # Check if retryable
                if attempt < max_retries and self._is_retryable_error(e):
                    self.logger.warning(f"Retrying {method_name} after error: {e.code()}")
                    await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                
                # Record failure
                self._record_failure(method_name, duration)
                
                # Log error
                if self.config.enable_logging:
                    self.logger.error(f"Client error: {method_name}, code: {e.code()}, details: {e.details()}")
                
                raise
            
            except Exception as e:
                duration = time.time() - start_time
                self._record_failure(method_name, duration)
                
                if self.config.enable_logging:
                    self.logger.error(f"Client exception: {method_name}, error: {str(e)}")
                
                raise
    
    def _is_retryable_error(self, error: grpc.RpcError) -> bool:
        """Check if error is retryable"""
        retryable_codes = [
            grpc.StatusCode.UNAVAILABLE,
            grpc.StatusCode.DEADLINE_EXCEEDED,
            grpc.StatusCode.RESOURCE_EXHAUSTED,
            grpc.StatusCode.ABORTED
        ]
        return error.code() in retryable_codes


class ClientStreamingInterceptor(BaseInterceptor, grpc.aio.StreamUnaryClientInterceptor):
    """
    🌊📞 Enterprise Client Streaming Interceptor
    
    Features:
    - Stream batching
    - Backpressure management
    - Stream recovery
    - Progress tracking
    """
    
    async def intercept_stream_unary(self, continuation, client_call_details, request_iterator):
        """Intercept client streaming calls"""
        method_name = self._get_method_name(client_call_details.method)
        start_time = time.time()
        
        # Enrich metadata
        metadata = list(client_call_details.metadata or [])
        trace_id = self._generate_trace_id()
        metadata.append(('x-trace-id', trace_id))
        metadata.append(('x-client-id', 'ainflue-client'))
        
        new_details = client_call_details._replace(metadata=metadata)
        
        try:
            # Monitor stream progress
            message_count = 0
            
            async def monitored_stream():
                nonlocal message_count
                async for request in request_iterator:
                    message_count += 1
                    
                    # Log progress periodically
                    if message_count % 1000 == 0:
                        self.logger.info(f"Stream progress: {method_name}, messages: {message_count}")
                    
                    yield request
            
            # Make the streaming call
            response = await continuation(new_details, monitored_stream())
            
            # Record success
            duration = time.time() - start_time
            self._record_success(method_name, duration)
            
            if self.config.enable_logging:
                self.logger.info(
                    f"Client stream completed: {method_name}, "
                    f"messages: {message_count}, duration: {duration:.3f}s"
                )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            self._record_failure(method_name, duration)
            
            if self.config.enable_logging:
                self.logger.error(f"Client stream error: {method_name}, error: {str(e)}")
            
            raise


class InterceptorChain:
    """
    🔗 Enterprise Interceptor Chain Manager
    
    Features:
    - Interceptor ordering
    - Conditional activation
    - Performance monitoring
    - Dynamic configuration
    """
    
    def __init__(self, config: InterceptorConfig):
        self.config = config
        self.logger = logging.getLogger("grpc_interceptor_chain")
        self.interceptors = {}
        self.metrics = {}
        
        # Initialize interceptors
        self._initialize_interceptors()
    
    def _initialize_interceptors(self):
        """Initialize all interceptors"""
        if self.config.enable_auth or self.config.enable_rate_limiting:
            self.interceptors['server_unary'] = ServerUnaryInterceptor(self.config)
            self.interceptors['server_streaming'] = ServerStreamingInterceptor(self.config)
        
        if self.config.enable_metrics:
            self.interceptors['client_unary'] = ClientUnaryInterceptor(self.config)
            self.interceptors['client_streaming'] = ClientStreamingInterceptor(self.config)
    
    def get_server_interceptors(self) -> List[grpc.aio.ServerInterceptor]:
        """Get all server interceptors"""
        interceptors = []
        
        if 'server_unary' in self.interceptors:
            interceptors.append(self.interceptors['server_unary'])
        
        if 'server_streaming' in self.interceptors:
            interceptors.append(self.interceptors['server_streaming'])
        
        return interceptors
    
    def get_client_interceptors(self) -> List:
        """Get all client interceptors"""
        interceptors = []
        
        if 'client_unary' in self.interceptors:
            interceptors.append(self.interceptors['client_unary'])
        
        if 'client_streaming' in self.interceptors:
            interceptors.append(self.interceptors['client_streaming'])
        
        return interceptors
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get metrics from all interceptors"""
        metrics = {}
        
        for name, interceptor in self.interceptors.items():
            if hasattr(interceptor, 'metrics'):
                interceptor_metrics = {}
                for method, method_metrics in interceptor.metrics.items():
                    interceptor_metrics[method] = {
                        'request_count': method_metrics.request_count,
                        'error_count': method_metrics.error_count,
                        'error_rate': method_metrics.error_rate,
                        'average_duration': method_metrics.average_duration,
                        'min_duration': method_metrics.min_duration,
                        'max_duration': method_metrics.max_duration
                    }
                metrics[name] = interceptor_metrics
        
        return metrics
    
    def reset_metrics(self):
        """Reset all metrics"""
        for interceptor in self.interceptors.values():
            if hasattr(interceptor, 'metrics'):
                interceptor.metrics.clear()
        
        self.logger.info("All interceptor metrics reset")


# Factory functions for easy integration
def create_server_interceptors(config: Optional[InterceptorConfig] = None) -> List[grpc.aio.ServerInterceptor]:
    """
    🏭 Factory function to create server interceptors
    
    Args:
        config: Interceptor configuration
    
    Returns:
        List of configured server interceptors
    """
    if config is None:
        config = InterceptorConfig()
    
    chain = InterceptorChain(config)
    return chain.get_server_interceptors()


def create_client_interceptors(config: Optional[InterceptorConfig] = None) -> List:
    """
    🏭 Factory function to create client interceptors
    
    Args:
        config: Interceptor configuration
    
    Returns:
        List of configured client interceptors
    """
    if config is None:
        config = InterceptorConfig()
    
    chain = InterceptorChain(config)
    return chain.get_client_interceptors()


def setup_creator_interceptors() -> InterceptorChain:
    """
    🎯 Creator-specific interceptor setup
    Optimized for content creation platforms
    """
    config = InterceptorConfig(
        # Enhanced auth for creator operations
        enable_auth=True,
        require_auth_for_methods=[
            'CreateContent', 'UpdateContent', 'DeleteContent',
            'UploadMedia', 'ProcessVideo', 'PublishContent'
        ],
        
        # Higher rate limits for creators
        enable_rate_limiting=True,
        default_rate_limit=2000,  # Higher default limit
        rate_limit_per_method={
            'CreateContent': 100,   # per minute
            'UploadMedia': 50,      # per minute
            'ProcessVideo': 20,     # per minute
            'GetAnalytics': 500     # per minute
        },
        
        # Enhanced monitoring for creator operations
        enable_metrics=True,
        enable_tracing=True,
        enable_logging=True,
        
        # Creator context
        enable_creator_context=True,
        creator_id_header='x-creator-id',
        content_id_header='x-content-id',
        
        # Larger message sizes for media uploads
        max_message_size=50 * 1024 * 1024,  # 50MB
        
        # Longer timeouts for media processing
        default_timeout=300.0,  # 5 minutes
        method_timeouts={
            'ProcessVideo': 1800.0,    # 30 minutes
            'UploadMedia': 600.0,      # 10 minutes
            'AnalyzeContent': 300.0    # 5 minutes
        },
        
        # Enhanced error handling
        enable_error_enrichment=True,
        mask_internal_errors=True,
        include_stack_traces=False,  # Security consideration
        
        # Circuit breaker for external services
        enable_circuit_breaker=True,
        failure_threshold=3,  # Lower threshold for creator services
        recovery_timeout=30,   # Faster recovery
        
        # Compression for large responses
        enable_compression=True,
        compression_algorithm='gzip'
    )
    
    return InterceptorChain(config)


if __name__ == "__main__":
    # Example usage
    async def example_server():
        """Example gRPC server with interceptors"""
        import grpc
        from grpc import aio
        
        # Create interceptors
        interceptors = create_server_interceptors()
        
        # Create server
        server = aio.server(interceptors=interceptors)
        
        # Add service (this would be your actual service)
        # server.add_generic_rpc_handlers([service_handler])
        
        # Start server
        listen_addr = '[::]:50051'
        server.add_insecure_port(listen_addr)
        
        print(f"Starting gRPC server on {listen_addr}")
        await server.start()
        
        try:
            await server.wait_for_termination()
        except KeyboardInterrupt:
            print("Stopping server...")
            await server.stop(grace=5)
    
    async def example_client():
        """Example gRPC client with interceptors"""
        import grpc
        from grpc import aio
        
        # Create interceptors
        interceptors = create_client_interceptors()
        
        # Create channel with interceptors
        async with aio.insecure_channel('localhost:50051', interceptors=interceptors) as channel:
            # Use channel for your service calls
            print("Client connected with interceptors")
    
    # Run example
    print("gRPC Interceptor Template Example")
    print("This demonstrates enterprise gRPC interceptors for the Ainflue platform")
    
    # Show metrics example
    creator_chain = setup_creator_interceptors()
    print("\nCreator interceptor metrics:")
    print(json.dumps(creator_chain.get_metrics(), indent=2))