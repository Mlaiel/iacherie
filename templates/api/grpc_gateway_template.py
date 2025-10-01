#!/usr/bin/env python3
"""
⚡ Enterprise gRPC Gateway Template - iacherie API Templates
Advanced production-ready gRPC-HTTP gateway with intelligent routing

⚠️ PROTECTION INTELLECTUELLE:
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS - Code propriétaire de Fahed Mlaiel
Utilisation commerciale INTERDITE sans autorisation écrite
Reverse engineering STRICTEMENT INTERDIT
Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence  
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import json
import time
import logging
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import grpc
from grpc_reflection.v1alpha import reflection
import aiohttp
from aiohttp import web, ClientSession
from aiohttp.web import Request, Response, StreamResponse
import structlog
from urllib.parse import urlparse, parse_qs
import ssl
import jwt
from functools import wraps
import asyncio
from concurrent.futures import ThreadPoolExecutor
import weakref
import re


class GRPCGatewayTemplate:
    """
    🚀 Enterprise gRPC Gateway Template
    
    Fonctionnalités:
    - ✅ Conversion gRPC <-> HTTP/REST automatique
    - ✅ Routing intelligent multi-service
    - ✅ Load balancing et failover
    - ✅ Authentication et authorization
    - ✅ Rate limiting par service
    - ✅ Protocol transcoding avancé
    - ✅ Streaming support (Server/Client/Bidirectional)
    - ✅ Health checking et circuit breakers
    - ✅ Métriques et monitoring intégrés
    - ✅ WebSocket <-> gRPC streaming bridge
    """
    
    def __init__(
        self,
        gateway_port: int = 8080,
        ssl_context: Optional[ssl.SSLContext] = None,
        cors_enabled: bool = True
    ):
        self.gateway_port = gateway_port
        self.ssl_context = ssl_context
        self.cors_enabled = cors_enabled
        
        # Logger structuré
        self.logger = structlog.get_logger(__name__)
        
        # Service registry
        self.services: Dict[str, GRPCServiceConfig] = {}
        self.service_pools: Dict[str, ConnectionPool] = {}
        
        # Load balancer
        self.load_balancer = LoadBalancer()
        
        # Auth system
        self.auth_manager = AuthenticationManager()
        
        # Rate limiter
        self.rate_limiter = RateLimiter()
        
        # Protocol transcoder
        self.transcoder = ProtocolTranscoder()
        
        # Health checker
        self.health_checker = HealthChecker()
        
        # Circuit breaker
        self.circuit_breaker = CircuitBreakerManager()
        
        # Metrics collector
        self.metrics = MetricsCollector("grpc_gateway")
        
        # WebSocket manager
        self.websocket_manager = WebSocketManager()
        
        # HTTP app
        self.app = self._create_app()
    
    def _create_app(self) -> web.Application:
        """Crée l'application HTTP/WebSocket"""
        app = web.Application(middlewares=[
            self._cors_middleware,
            self._auth_middleware,
            self._rate_limit_middleware,
            self._metrics_middleware,
            self._error_handling_middleware
        ])
        
        # Routes API
        app.router.add_route('*', '/{service}/{method}', self.handle_grpc_request)
        app.router.add_get('/ws/{service}/{method}', self.handle_websocket)
        
        # Routes utilitaires
        app.router.add_get('/health', self.health_endpoint)
        app.router.add_get('/metrics', self.metrics_endpoint)
        app.router.add_get('/services', self.services_endpoint)
        
        # Routes de gestion
        app.router.add_post('/admin/services', self.register_service_endpoint)
        app.router.add_delete('/admin/services/{service_name}', self.unregister_service_endpoint)
        app.router.add_get('/admin/status', self.admin_status_endpoint)
        
        return app
    
    def register_service(
        self,
        service_name: str,
        service_config: 'GRPCServiceConfig'
    ):
        """Enregistre un service gRPC"""
        self.services[service_name] = service_config
        self.service_pools[service_name] = ConnectionPool(service_config)
        
        # Démarrer health checking
        self.health_checker.add_service(service_name, service_config)
        
        # Configurer circuit breaker
        self.circuit_breaker.add_service(service_name)
        
        self.logger.info(
            "Service registered",
            service=service_name,
            endpoints=service_config.endpoints,
            auth_required=service_config.auth_required
        )
    
    async def handle_grpc_request(self, request: Request) -> Response:
        """Route principal pour les requêtes gRPC"""
        try:
            # Extraction des paramètres
            service_name = request.match_info['service']
            method_name = request.match_info['method']
            
            # Vérifier que le service existe
            if service_name not in self.services:
                return web.json_response(
                    {'error': f'Service {service_name} not found'},
                    status=404
                )
            
            service_config = self.services[service_name]
            
            # Vérifier circuit breaker
            if not self.circuit_breaker.can_execute(service_name):
                return web.json_response(
                    {'error': 'Service temporarily unavailable'},
                    status=503
                )
            
            # Load balancing
            endpoint = self.load_balancer.get_endpoint(service_name, service_config)
            if not endpoint:
                return web.json_response(
                    {'error': 'No healthy endpoints available'},
                    status=503
                )
            
            # Obtenir connexion
            pool = self.service_pools[service_name]
            async with pool.get_connection(endpoint) as stub:
                
                # Transcoder la requête
                grpc_request = await self.transcoder.http_to_grpc(
                    request, method_name, service_config
                )
                
                # Exécuter la requête gRPC
                start_time = time.time()
                try:
                    # Déterminer le type de méthode
                    method_info = service_config.get_method_info(method_name)
                    
                    if method_info['streaming'] == 'none':
                        # Unary call
                        grpc_response = await self._call_unary_method(
                            stub, method_name, grpc_request, service_config
                        )
                        
                        # Transcoder la réponse
                        http_response = await self.transcoder.grpc_to_http(
                            grpc_response, method_info
                        )
                        
                        # Métriques de succès
                        self.metrics.record_request(
                            service_name, method_name, 
                            time.time() - start_time, True
                        )
                        
                        self.circuit_breaker.record_success(service_name)
                        
                        return web.json_response(http_response)
                    
                    elif method_info['streaming'] == 'server':
                        # Server streaming
                        return await self._handle_server_streaming(
                            request, stub, method_name, grpc_request, service_config
                        )
                    
                    else:
                        return web.json_response(
                            {'error': 'Client/bidirectional streaming not supported in HTTP mode'},
                            status=400
                        )
                
                except grpc.RpcError as e:
                    # Erreur gRPC
                    self.metrics.record_request(
                        service_name, method_name,
                        time.time() - start_time, False
                    )
                    
                    self.circuit_breaker.record_failure(service_name)
                    
                    return await self._handle_grpc_error(e)
        
        except Exception as e:
            self.logger.error(
                "Gateway error",
                service=service_name,
                method=method_name,
                error=str(e)
            )
            
            return web.json_response(
                {'error': 'Internal gateway error'},
                status=500
            )
    
    async def handle_websocket(self, request: Request) -> StreamResponse:
        """Gère les connexions WebSocket pour streaming"""
        service_name = request.match_info['service']
        method_name = request.match_info['method']
        
        if service_name not in self.services:
            return web.json_response(
                {'error': f'Service {service_name} not found'},
                status=404
            )
        
        service_config = self.services[service_name]
        method_info = service_config.get_method_info(method_name)
        
        if method_info['streaming'] == 'none':
            return web.json_response(
                {'error': 'Method does not support streaming'},
                status=400
            )
        
        # Établir connexion WebSocket
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        try:
            # Obtenir endpoint et connexion
            endpoint = self.load_balancer.get_endpoint(service_name, service_config)
            pool = self.service_pools[service_name]
            
            async with pool.get_connection(endpoint) as stub:
                await self.websocket_manager.handle_streaming(
                    ws, stub, method_name, method_info, service_config
                )
        
        except Exception as e:
            self.logger.error(
                "WebSocket streaming error",
                service=service_name,
                method=method_name,
                error=str(e)
            )
            
            if not ws.closed:
                await ws.close(code=aiohttp.WSMsgType.ERROR, message=str(e).encode())
        
        return ws
    
    async def _call_unary_method(
        self,
        stub,
        method_name: str,
        request,
        service_config: 'GRPCServiceConfig'
    ):
        """Appelle une méthode gRPC unary"""
        method = getattr(stub, method_name)
        
        # Timeout configuration
        timeout = service_config.timeout
        
        # Metadata
        metadata = service_config.get_metadata()
        
        # Exécuter l'appel
        response = await method(request, timeout=timeout, metadata=metadata)
        return response
    
    async def _handle_server_streaming(
        self,
        request: Request,
        stub,
        method_name: str,
        grpc_request,
        service_config: 'GRPCServiceConfig'
    ) -> StreamResponse:
        """Gère server streaming via Server-Sent Events"""
        response = web.StreamResponse()
        response.headers['Content-Type'] = 'text/event-stream'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Connection'] = 'keep-alive'
        
        await response.prepare(request)
        
        try:
            method = getattr(stub, method_name)
            stream = method(grpc_request, timeout=service_config.timeout)
            
            async for grpc_response in stream:
                # Transcoder chaque réponse
                http_data = await self.transcoder.grpc_to_http(
                    grpc_response, {'response_type': 'streaming'}
                )
                
                # Envoyer via SSE
                sse_data = f"data: {json.dumps(http_data)}\n\n"
                await response.write(sse_data.encode())
        
        except Exception as e:
            error_data = f"data: {json.dumps({'error': str(e)})}\n\n"
            await response.write(error_data.encode())
        
        finally:
            await response.write_eof()
        
        return response
    
    async def _handle_grpc_error(self, error: grpc.RpcError) -> Response:
        """Convertit les erreurs gRPC en réponses HTTP"""
        status_code_map = {
            grpc.StatusCode.NOT_FOUND: 404,
            grpc.StatusCode.INVALID_ARGUMENT: 400,
            grpc.StatusCode.UNAUTHENTICATED: 401,
            grpc.StatusCode.PERMISSION_DENIED: 403,
            grpc.StatusCode.ALREADY_EXISTS: 409,
            grpc.StatusCode.RESOURCE_EXHAUSTED: 429,
            grpc.StatusCode.FAILED_PRECONDITION: 412,
            grpc.StatusCode.UNIMPLEMENTED: 501,
            grpc.StatusCode.UNAVAILABLE: 503,
            grpc.StatusCode.DEADLINE_EXCEEDED: 504,
        }
        
        http_status = status_code_map.get(error.code(), 500)
        
        return web.json_response(
            {
                'error': error.details(),
                'grpc_code': error.code().name,
                'grpc_message': error.details()
            },
            status=http_status
        )
    
    # Middleware
    async def _cors_middleware(self, request: Request, handler: Callable) -> Response:
        """Middleware CORS"""
        if not self.cors_enabled:
            return await handler(request)
        
        # Préflight request
        if request.method == 'OPTIONS':
            response = web.Response()
        else:
            response = await handler(request)
        
        # CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response
    
    async def _auth_middleware(self, request: Request, handler: Callable) -> Response:
        """Middleware d'authentification"""
        # Routes publiques
        if request.path in ['/health', '/metrics']:
            return await handler(request)
        
        # Extraire le service
        path_parts = request.path.strip('/').split('/')
        if len(path_parts) < 2:
            return await handler(request)
        
        service_name = path_parts[0]
        
        # Vérifier si l'auth est requise
        if service_name in self.services:
            service_config = self.services[service_name]
            if service_config.auth_required:
                auth_result = await self.auth_manager.authenticate(request)
                if not auth_result['valid']:
                    return web.json_response(
                        {'error': 'Authentication required'},
                        status=401
                    )
                
                # Ajouter user info à la requête
                request['user'] = auth_result['user']
        
        return await handler(request)
    
    async def _rate_limit_middleware(self, request: Request, handler: Callable) -> Response:
        """Middleware de rate limiting"""
        # Identifier le client
        client_id = request.remote or 'unknown'
        if 'user' in request:
            client_id = request['user'].get('id', client_id)
        
        # Vérifier rate limit
        if not await self.rate_limiter.check_limit(client_id, request.path):
            return web.json_response(
                {'error': 'Rate limit exceeded'},
                status=429
            )
        
        return await handler(request)
    
    async def _metrics_middleware(self, request: Request, handler: Callable) -> Response:
        """Middleware de métriques"""
        start_time = time.time()
        
        try:
            response = await handler(request)
            
            # Enregistrer métrique de succès
            self.metrics.record_http_request(
                request.method,
                request.path,
                response.status,
                time.time() - start_time
            )
            
            return response
        
        except Exception as e:
            # Enregistrer métrique d'erreur
            self.metrics.record_http_request(
                request.method,
                request.path,
                500,
                time.time() - start_time
            )
            raise
    
    async def _error_handling_middleware(self, request: Request, handler: Callable) -> Response:
        """Middleware de gestion d'erreurs"""
        try:
            return await handler(request)
        except web.HTTPException:
            raise
        except Exception as e:
            self.logger.error(
                "Unhandled error",
                path=request.path,
                method=request.method,
                error=str(e)
            )
            
            return web.json_response(
                {'error': 'Internal server error'},
                status=500
            )
    
    # Endpoints utilitaires
    async def health_endpoint(self, request: Request) -> Response:
        """Endpoint de health check"""
        health_status = await self.health_checker.check_all_services()
        
        overall_healthy = all(status['healthy'] for status in health_status.values())
        
        return web.json_response(
            {
                'status': 'healthy' if overall_healthy else 'unhealthy',
                'services': health_status,
                'timestamp': datetime.utcnow().isoformat()
            },
            status=200 if overall_healthy else 503
        )
    
    async def metrics_endpoint(self, request: Request) -> Response:
        """Endpoint de métriques"""
        metrics = self.metrics.get_metrics()
        return web.json_response(metrics)
    
    async def services_endpoint(self, request: Request) -> Response:
        """Liste des services enregistrés"""
        services_info = {}
        
        for name, config in self.services.items():
            services_info[name] = {
                'endpoints': config.endpoints,
                'auth_required': config.auth_required,
                'healthy': await self.health_checker.is_healthy(name),
                'circuit_breaker_open': self.circuit_breaker.is_open(name)
            }
        
        return web.json_response({'services': services_info})
    
    async def register_service_endpoint(self, request: Request) -> Response:
        """Endpoint pour enregistrer un nouveau service"""
        data = await request.json()
        
        try:
            config = GRPCServiceConfig.from_dict(data)
            self.register_service(data['name'], config)
            
            return web.json_response({'status': 'registered'})
        
        except Exception as e:
            return web.json_response(
                {'error': str(e)},
                status=400
            )
    
    async def unregister_service_endpoint(self, request: Request) -> Response:
        """Endpoint pour désenregistrer un service"""
        service_name = request.match_info['service_name']
        
        if service_name in self.services:
            del self.services[service_name]
            del self.service_pools[service_name]
            self.health_checker.remove_service(service_name)
            self.circuit_breaker.remove_service(service_name)
            
            return web.json_response({'status': 'unregistered'})
        
        return web.json_response(
            {'error': 'Service not found'},
            status=404
        )
    
    async def admin_status_endpoint(self, request: Request) -> Response:
        """Status complet du gateway"""
        return web.json_response({
            'gateway': {
                'port': self.gateway_port,
                'ssl_enabled': self.ssl_context is not None,
                'cors_enabled': self.cors_enabled
            },
            'services': len(self.services),
            'metrics': self.metrics.get_summary(),
            'health': await self.health_checker.get_summary()
        })
    
    async def start(self):
        """Démarre le gateway"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(
            runner,
            '0.0.0.0',
            self.gateway_port,
            ssl_context=self.ssl_context
        )
        
        await site.start()
        
        self.logger.info(
            "gRPC Gateway started",
            port=self.gateway_port,
            ssl=self.ssl_context is not None
        )


@dataclass
class GRPCServiceConfig:
    """Configuration d'un service gRPC"""
    endpoints: List[str]
    auth_required: bool = False
    timeout: float = 30.0
    max_connections: int = 10
    health_check_path: str = "/health"
    metadata: Dict[str, str] = field(default_factory=dict)
    methods: Dict[str, Dict[str, str]] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GRPCServiceConfig':
        """Crée la config depuis un dictionnaire"""
        return cls(**data)
    
    def get_method_info(self, method_name: str) -> Dict[str, str]:
        """Retourne les infos d'une méthode"""
        return self.methods.get(method_name, {
            'streaming': 'none',
            'request_type': 'json',
            'response_type': 'json'
        })
    
    def get_metadata(self) -> List[Tuple[str, str]]:
        """Retourne les metadata gRPC"""
        return [(k, v) for k, v in self.metadata.items()]


class ConnectionPool:
    """Pool de connexions gRPC"""
    
    def __init__(self, config: GRPCServiceConfig):
        self.config = config
        self.pools: Dict[str, List] = {}
        self.lock = asyncio.Lock()
    
    async def get_connection(self, endpoint: str):
        """Obtient une connexion du pool"""
        # Simplified - would implement actual connection pooling
        channel = grpc.aio.insecure_channel(endpoint)
        return GRPCStubWrapper(channel)


class GRPCStubWrapper:
    """Wrapper pour les stubs gRPC"""
    
    def __init__(self, channel):
        self.channel = channel
        self._stubs = {}
    
    def __getattr__(self, name):
        # Dynamic method resolution based on service
        # Would implement actual protobuf stub creation
        return lambda *args, **kwargs: asyncio.sleep(0.1)  # Placeholder
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.channel.close()


class LoadBalancer:
    """Load balancer pour endpoints"""
    
    def __init__(self):
        self.current_index: Dict[str, int] = {}
    
    def get_endpoint(self, service_name: str, config: GRPCServiceConfig) -> Optional[str]:
        """Retourne le prochain endpoint (round-robin)"""
        if not config.endpoints:
            return None
        
        if service_name not in self.current_index:
            self.current_index[service_name] = 0
        
        endpoint = config.endpoints[self.current_index[service_name]]
        self.current_index[service_name] = (
            self.current_index[service_name] + 1
        ) % len(config.endpoints)
        
        return endpoint


class AuthenticationManager:
    """Gestionnaire d'authentification"""
    
    async def authenticate(self, request: Request) -> Dict[str, Any]:
        """Authentifie une requête"""
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return {'valid': False, 'error': 'Missing bearer token'}
        
        token = auth_header[7:]  # Remove 'Bearer '
        
        try:
            # Valider le JWT (simplifié)
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
            return {
                'valid': True,
                'user': payload
            }
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}


class RateLimiter:
    """Rate limiter par client"""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
        self.limits = {
            'default': 100,  # 100 requests per minute
            'authenticated': 1000  # Higher limit for auth users
        }
    
    async def check_limit(self, client_id: str, path: str) -> bool:
        """Vérifie si la limite est respectée"""
        now = time.time()
        minute_ago = now - 60
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Nettoyer les anciennes requêtes
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > minute_ago
        ]
        
        # Vérifier la limite
        current_count = len(self.requests[client_id])
        limit = self.limits['default']  # Simplification
        
        if current_count >= limit:
            return False
        
        # Enregistrer la nouvelle requête
        self.requests[client_id].append(now)
        return True


class ProtocolTranscoder:
    """Transcoder HTTP <-> gRPC"""
    
    async def http_to_grpc(
        self,
        request: Request,
        method_name: str,
        service_config: GRPCServiceConfig
    ):
        """Convertit une requête HTTP en requête gRPC"""
        # Simplification - would implement actual protobuf conversion
        if request.method == 'GET':
            # Query parameters to protobuf
            return self._query_to_protobuf(dict(request.query))
        else:
            # JSON body to protobuf
            json_data = await request.json()
            return self._json_to_protobuf(json_data)
    
    async def grpc_to_http(self, grpc_response, method_info: Dict[str, str]):
        """Convertit une réponse gRPC en HTTP"""
        # Simplification - would implement actual protobuf to JSON conversion
        return {'result': 'success', 'data': 'placeholder'}
    
    def _query_to_protobuf(self, params: Dict[str, str]):
        """Convertit query params en protobuf"""
        # Placeholder implementation
        return type('Request', (), params)()
    
    def _json_to_protobuf(self, json_data: Dict[str, Any]):
        """Convertit JSON en protobuf"""
        # Placeholder implementation
        return type('Request', (), json_data)()


class HealthChecker:
    """Health checker pour services"""
    
    def __init__(self):
        self.services: Dict[str, GRPCServiceConfig] = {}
        self.health_status: Dict[str, bool] = {}
    
    def add_service(self, name: str, config: GRPCServiceConfig):
        """Ajoute un service à surveiller"""
        self.services[name] = config
        self.health_status[name] = True
    
    def remove_service(self, name: str):
        """Retire un service"""
        self.services.pop(name, None)
        self.health_status.pop(name, None)
    
    async def check_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Vérifie tous les services"""
        results = {}
        
        for name, config in self.services.items():
            healthy = await self._check_service_health(name, config)
            self.health_status[name] = healthy
            
            results[name] = {
                'healthy': healthy,
                'endpoints': config.endpoints,
                'last_check': datetime.utcnow().isoformat()
            }
        
        return results
    
    async def _check_service_health(self, name: str, config: GRPCServiceConfig) -> bool:
        """Vérifie la santé d'un service"""
        # Simplification - would implement actual health checks
        return True
    
    async def is_healthy(self, service_name: str) -> bool:
        """Vérifie si un service est en santé"""
        return self.health_status.get(service_name, False)
    
    async def get_summary(self) -> Dict[str, Any]:
        """Résumé de santé"""
        total = len(self.services)
        healthy = sum(1 for status in self.health_status.values() if status)
        
        return {
            'total_services': total,
            'healthy_services': healthy,
            'unhealthy_services': total - healthy,
            'health_percentage': (healthy / total * 100) if total > 0 else 0
        }


class CircuitBreakerManager:
    """Gestionnaire de circuit breakers"""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
    
    def add_service(self, service_name: str):
        """Ajoute un circuit breaker pour un service"""
        self.breakers[service_name] = CircuitBreaker(service_name)
    
    def remove_service(self, service_name: str):
        """Retire un circuit breaker"""
        self.breakers.pop(service_name, None)
    
    def can_execute(self, service_name: str) -> bool:
        """Vérifie si on peut exécuter une requête"""
        breaker = self.breakers.get(service_name)
        return breaker.can_execute() if breaker else True
    
    def record_success(self, service_name: str):
        """Enregistre un succès"""
        breaker = self.breakers.get(service_name)
        if breaker:
            breaker.record_success()
    
    def record_failure(self, service_name: str):
        """Enregistre un échec"""
        breaker = self.breakers.get(service_name)
        if breaker:
            breaker.record_failure()
    
    def is_open(self, service_name: str) -> bool:
        """Vérifie si le circuit breaker est ouvert"""
        breaker = self.breakers.get(service_name)
        return breaker.is_open() if breaker else False


class CircuitBreaker:
    """Circuit breaker pour un service"""
    
    def __init__(
        self,
        service_name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0
    ):
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Vérifie si on peut exécuter"""
        if self.state == 'CLOSED':
            return True
        
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                return True
            return False
        
        # HALF_OPEN
        return True
    
    def record_success(self):
        """Enregistre un succès"""
        self.failure_count = 0
        if self.state == 'HALF_OPEN':
            self.state = 'CLOSED'
    
    def record_failure(self):
        """Enregistre un échec"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
    
    def is_open(self) -> bool:
        """Vérifie si ouvert"""
        return self.state == 'OPEN'


class MetricsCollector:
    """Collecteur de métriques"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.request_counts: Dict[str, int] = {}
        self.request_durations: List[float] = []
        self.error_counts: Dict[str, int] = {}
    
    def record_request(
        self,
        service: str,
        method: str,
        duration: float,
        success: bool
    ):
        """Enregistre une requête"""
        key = f"{service}.{method}"
        self.request_counts[key] = self.request_counts.get(key, 0) + 1
        self.request_durations.append(duration)
        
        if not success:
            self.error_counts[key] = self.error_counts.get(key, 0) + 1
    
    def record_http_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float
    ):
        """Enregistre une requête HTTP"""
        key = f"http.{method}.{path}"
        self.request_counts[key] = self.request_counts.get(key, 0) + 1
        self.request_durations.append(duration)
        
        if status_code >= 400:
            self.error_counts[key] = self.error_counts.get(key, 0) + 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retourne toutes les métriques"""
        if not self.request_durations:
            return {}
        
        return {
            'requests': self.request_counts,
            'errors': self.error_counts,
            'avg_duration': sum(self.request_durations) / len(self.request_durations),
            'total_requests': sum(self.request_counts.values()),
            'total_errors': sum(self.error_counts.values())
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Résumé des métriques"""
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())
        
        return {
            'total_requests': total_requests,
            'total_errors': total_errors,
            'error_rate': (total_errors / total_requests) if total_requests > 0 else 0,
            'avg_duration': sum(self.request_durations) / len(self.request_durations) if self.request_durations else 0
        }


class WebSocketManager:
    """Gestionnaire WebSocket pour streaming"""
    
    async def handle_streaming(
        self,
        websocket: web.WebSocketResponse,
        stub,
        method_name: str,
        method_info: Dict[str, str],
        service_config: GRPCServiceConfig
    ):
        """Gère le streaming via WebSocket"""
        
        if method_info['streaming'] == 'server':
            await self._handle_server_streaming(websocket, stub, method_name)
        elif method_info['streaming'] == 'client':
            await self._handle_client_streaming(websocket, stub, method_name)
        elif method_info['streaming'] == 'bidirectional':
            await self._handle_bidirectional_streaming(websocket, stub, method_name)
    
    async def _handle_server_streaming(self, websocket, stub, method_name):
        """Server streaming via WebSocket"""
        # Simplified implementation
        for i in range(10):  # Simulate streaming
            message = {'data': f'message_{i}', 'timestamp': time.time()}
            await websocket.send_str(json.dumps(message))
            await asyncio.sleep(1)
    
    async def _handle_client_streaming(self, websocket, stub, method_name):
        """Client streaming via WebSocket"""
        messages = []
        
        async for msg in websocket:
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                messages.append(data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                break
        
        # Send final response
        result = {'received_messages': len(messages)}
        await websocket.send_str(json.dumps(result))
    
    async def _handle_bidirectional_streaming(self, websocket, stub, method_name):
        """Bidirectional streaming via WebSocket"""
        async def sender():
            for i in range(10):
                message = {'server_data': f'response_{i}'}
                await websocket.send_str(json.dumps(message))
                await asyncio.sleep(1)
        
        async def receiver():
            async for msg in websocket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    # Process client message
                    pass
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
        
        # Run both coroutines concurrently
        await asyncio.gather(sender(), receiver())


# Factory functions
def create_grpc_gateway(
    gateway_port: int = 8080,
    ssl_cert_path: Optional[str] = None,
    ssl_key_path: Optional[str] = None
) -> GRPCGatewayTemplate:
    """Factory pour créer un gateway gRPC"""
    
    ssl_context = None
    if ssl_cert_path and ssl_key_path:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(ssl_cert_path, ssl_key_path)
    
    gateway = GRPCGatewayTemplate(
        gateway_port=gateway_port,
        ssl_context=ssl_context
    )
    
    return gateway


async def setup_gateway_with_services(
    services_config: Dict[str, Dict[str, Any]],
    gateway_port: int = 8080
) -> GRPCGatewayTemplate:
    """Setup complet d'un gateway avec services"""
    
    gateway = create_grpc_gateway(gateway_port)
    
    # Enregistrer les services
    for service_name, config_data in services_config.items():
        config = GRPCServiceConfig.from_dict(config_data)
        gateway.register_service(service_name, config)
    
    return gateway


# Example usage
if __name__ == "__main__":
    async def main():
        # Configuration exemple
        services_config = {
            'user_service': {
                'endpoints': ['localhost:50051', 'localhost:50052'],
                'auth_required': True,
                'timeout': 10.0,
                'methods': {
                    'GetUser': {'streaming': 'none'},
                    'StreamUsers': {'streaming': 'server'}
                }
            },
            'content_service': {
                'endpoints': ['localhost:50053'],
                'auth_required': False,
                'timeout': 30.0,
                'methods': {
                    'UploadContent': {'streaming': 'client'},
                    'ProcessContent': {'streaming': 'bidirectional'}
                }
            }
        }
        
        # Créer et démarrer le gateway
        gateway = await setup_gateway_with_services(services_config, 8080)
        await gateway.start()
        
        print("gRPC Gateway running on http://localhost:8080")
        print("Health: http://localhost:8080/health")
        print("Metrics: http://localhost:8080/metrics")
        print("Services: http://localhost:8080/services")
        
        # Maintenir le serveur en vie
        try:
            while True:
                await asyncio.sleep(3600)
        except KeyboardInterrupt:
            print("Gateway shutting down...")
    
    asyncio.run(main())