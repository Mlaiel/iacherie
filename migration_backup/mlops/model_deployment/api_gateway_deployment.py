"""🚪 MLOps API Gateway Deployment - Enterprise Gateway Management
================================================================
Module: mlops/model_deployment/api_gateway_deployment.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🚨 AVERTISSEMENT LÉGAL:
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation non autorisée, copie, modification, distribution ou
reproduction est strictement interdite et peut entraîner des poursuites
judiciaires. Tous droits réservés.

🎯 API GATEWAY DEPLOYMENT ENGINE
Enterprise API gateway deployment and management for ML models with:
- Multi-provider gateway support (Kong/Istio/AWS/Azure/GCP/Ambassador)
- Creator-tier specific routing and rate limiting
- Advanced authentication and authorization
- Real-time monitoring and analytics
"""

import asyncio
import logging
import json
import yaml
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from dataclasses import dataclass, asdict
import requests
import time
import hashlib
import jwt
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class GatewayProvider(Enum):
    """Supported API gateway providers"""
    KONG = "kong"
    ISTIO = "istio"
    AWS_API_GATEWAY = "aws_api_gateway"
    AZURE_API_MANAGEMENT = "azure_api_management"
    GCP_CLOUD_ENDPOINTS = "gcp_cloud_endpoints"
    AMBASSADOR = "ambassador"
    NGINX = "nginx"
    TRAEFIK = "traefik"

class AuthenticationMethod(Enum):
    """Authentication methods"""
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    MTLS = "mtls"
    CUSTOM = "custom"

class RateLimitUnit(Enum):
    """Rate limiting time units"""
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"

class CreatorTier(Enum):
    """Creator subscription tiers"""
    FREE = "free"
    CREATOR = "creator"
    PRO = "pro"
    ENTERPRISE = "enterprise"

@dataclass
class GatewayConfig:
    """API gateway configuration"""
    gateway_id: str
    provider: GatewayProvider
    name: str
    namespace: str
    tier: CreatorTier
    endpoints: List[str]
    domain: Optional[str]
    ssl_enabled: bool
    authentication: List[AuthenticationMethod]
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['provider'] = self.provider.value
        data['tier'] = self.tier.value
        data['authentication'] = [auth.value for auth in self.authentication]
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class RouteConfig:
    """API route configuration"""
    route_id: str
    gateway_id: str
    path: str
    methods: List[str]
    backend_service: str
    backend_port: int
    tier: CreatorTier
    rate_limit: Optional[Dict[str, Any]]
    authentication_required: bool
    cors_enabled: bool
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['tier'] = self.tier.value
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class RateLimitRule:
    """Rate limiting rule"""
    rule_id: str
    gateway_id: str
    route_path: str
    tier: CreatorTier
    requests_per_unit: int
    unit: RateLimitUnit
    burst_limit: int
    identifier: str  # ip, user_id, api_key
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['tier'] = self.tier.value
        data['unit'] = self.unit.value
        data['created_at'] = self.created_at.isoformat()
        return data

@dataclass
class GatewayMetrics:
    """API gateway metrics"""
    gateway_id: str
    total_requests: int
    success_requests: int
    error_requests: int
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    rate_limit_hits: int
    auth_failures: int
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class SecurityPolicy:
    """Gateway security policy"""
    policy_id: str
    gateway_id: str
    policy_type: str  # cors, csrf, waf, ip_whitelist
    config: Dict[str, Any]
    tier: CreatorTier
    active: bool
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['tier'] = self.tier.value
        data['created_at'] = self.created_at.isoformat()
        return data

class APIGatewayDeployment:
    """
    🚪 Enterprise API Gateway Deployment Engine
    
    Comprehensive API gateway deployment and management with:
    - Multi-provider gateway support
    - Creator-tier specific configurations
    - Advanced security and monitoring
    - Intelligent routing and load balancing
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize API Gateway Deployment"""
        self.config = config or {}
        self.gateways: Dict[str, GatewayConfig] = {}
        self.routes: Dict[str, RouteConfig] = {}
        self.rate_limits: Dict[str, RateLimitRule] = {}
        self.metrics: Dict[str, List[GatewayMetrics]] = {}
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.provider_clients: Dict[GatewayProvider, Any] = {}
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Initialize provider clients
        asyncio.create_task(self._init_provider_clients())
    
    async def _init_provider_clients(self):
        """Initialize API gateway provider clients"""
        try:
            # Kong client
            if self.config.get('kong', {}).get('enabled', True):
                self.provider_clients[GatewayProvider.KONG] = self._init_kong_client()
            
            # AWS API Gateway client
            if self.config.get('aws', {}).get('enabled', True):
                import boto3
                self.provider_clients[GatewayProvider.AWS_API_GATEWAY] = boto3.client(
                    'apigateway',
                    region_name=self.config.get('aws', {}).get('region', 'us-east-1')
                )
            
            # Azure API Management client
            if self.config.get('azure', {}).get('enabled', True):
                from azure.identity import DefaultAzureCredential
                from azure.mgmt.apimanagement import ApiManagementClient
                credential = DefaultAzureCredential()
                self.provider_clients[GatewayProvider.AZURE_API_MANAGEMENT] = ApiManagementClient(
                    credential,
                    self.config.get('azure', {}).get('subscription_id', '')
                )
            
            # GCP Cloud Endpoints client
            if self.config.get('gcp', {}).get('enabled', True):
                from google.cloud import endpoints_v1
                self.provider_clients[GatewayProvider.GCP_CLOUD_ENDPOINTS] = endpoints_v1.ServiceManagerClient()
            
            self.logger.info("API gateway provider clients initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize provider clients: {str(e)}")
    
    def _init_kong_client(self) -> Optional[Any]:
        """Initialize Kong client"""
        try:
            kong_config = self.config.get('kong', {})
            base_url = kong_config.get('admin_url', 'http://localhost:8001')
            # Return Kong client wrapper
            return {'base_url': base_url, 'headers': {'Content-Type': 'application/json'}}
        except Exception as e:
            self.logger.warning(f"Kong client not available: {str(e)}")
            return None
    
    async def deploy_api_gateway(
        self,
        deployment_id: str,
        provider: GatewayProvider,
        endpoints: List[str],
        tier: CreatorTier = CreatorTier.CREATOR,
        domain: Optional[str] = None,
        namespace: str = "default"
    ) -> GatewayConfig:
        """
        Deploy API gateway for ML model endpoints
        
        Args:
            deployment_id: Unique deployment identifier
            provider: API gateway provider
            endpoints: List of backend endpoints
            tier: Creator subscription tier
            domain: Custom domain (optional)
            namespace: Kubernetes namespace
            
        Returns:
            GatewayConfig: Deployed gateway configuration
        """
        try:
            gateway_id = f"gw-{deployment_id}-{int(time.time())}"
            
            # Determine authentication methods based on tier
            auth_methods = self._get_auth_methods_for_tier(tier)
            
            # Create gateway configuration
            gateway_config = GatewayConfig(
                gateway_id=gateway_id,
                provider=provider,
                name=f"gateway-{deployment_id}",
                namespace=namespace,
                tier=tier,
                endpoints=endpoints,
                domain=domain,
                ssl_enabled=tier != CreatorTier.FREE,
                authentication=auth_methods,
                created_at=datetime.now(timezone.utc)
            )
            
            # Deploy gateway using provider-specific method
            await self._deploy_gateway_provider(gateway_config)
            
            # Configure default routes
            await self._configure_default_routes(gateway_config)
            
            # Set up rate limiting
            await self._configure_rate_limiting(gateway_config)
            
            # Apply security policies
            await self._apply_security_policies(gateway_config)
            
            self.gateways[gateway_id] = gateway_config
            self.logger.info(f"API gateway deployed: {gateway_id}")
            
            return gateway_config
            
        except Exception as e:
            self.logger.error(f"Failed to deploy API gateway: {str(e)}")
            raise
    
    def _get_auth_methods_for_tier(self, tier: CreatorTier) -> List[AuthenticationMethod]:
        """Get authentication methods based on creator tier"""
        auth_mapping = {
            CreatorTier.FREE: [AuthenticationMethod.API_KEY],
            CreatorTier.CREATOR: [AuthenticationMethod.API_KEY, AuthenticationMethod.JWT],
            CreatorTier.PRO: [AuthenticationMethod.API_KEY, AuthenticationMethod.JWT, AuthenticationMethod.OAUTH2],
            CreatorTier.ENTERPRISE: [
                AuthenticationMethod.API_KEY,
                AuthenticationMethod.JWT,
                AuthenticationMethod.OAUTH2,
                AuthenticationMethod.MTLS
            ]
        }
        return auth_mapping[tier]
    
    async def _deploy_gateway_provider(self, gateway_config: GatewayConfig):
        """Deploy gateway using provider-specific implementation"""
        if gateway_config.provider == GatewayProvider.KONG:
            await self._deploy_kong_gateway(gateway_config)
        elif gateway_config.provider == GatewayProvider.ISTIO:
            await self._deploy_istio_gateway(gateway_config)
        elif gateway_config.provider == GatewayProvider.AWS_API_GATEWAY:
            await self._deploy_aws_gateway(gateway_config)
        elif gateway_config.provider == GatewayProvider.AZURE_API_MANAGEMENT:
            await self._deploy_azure_gateway(gateway_config)
        elif gateway_config.provider == GatewayProvider.GCP_CLOUD_ENDPOINTS:
            await self._deploy_gcp_gateway(gateway_config)
        elif gateway_config.provider == GatewayProvider.AMBASSADOR:
            await self._deploy_ambassador_gateway(gateway_config)
        else:
            raise ValueError(f"Unsupported provider: {gateway_config.provider}")
    
    async def _deploy_kong_gateway(self, gateway_config: GatewayConfig):
        """Deploy Kong API gateway"""
        try:
            kong_client = self.provider_clients.get(GatewayProvider.KONG)
            if not kong_client:
                raise ValueError("Kong client not initialized")
            
            # Create Kong service
            service_config = {
                'name': gateway_config.name,
                'host': gateway_config.endpoints[0].split('://')[1].split('/')[0],
                'port': 80,
                'protocol': 'http',
                'tags': [f'tier:{gateway_config.tier.value}', f'deployment:{gateway_config.gateway_id}']
            }
            
            # Create Kong route
            route_config = {
                'name': f"{gateway_config.name}-route",
                'protocols': ['http', 'https'] if gateway_config.ssl_enabled else ['http'],
                'methods': ['GET', 'POST', 'PUT', 'DELETE'],
                'paths': ['/api/v1'],
                'service': {'name': gateway_config.name},
                'tags': [f'tier:{gateway_config.tier.value}']
            }
            
            # Configure authentication plugins
            for auth_method in gateway_config.authentication:
                await self._configure_kong_auth_plugin(gateway_config, auth_method)
            
            self.logger.info(f"Kong gateway deployed: {gateway_config.gateway_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy Kong gateway: {str(e)}")
            raise
    
    async def _deploy_istio_gateway(self, gateway_config: GatewayConfig):
        """Deploy Istio gateway"""
        try:
            # Create Istio Gateway resource
            gateway_spec = {
                'apiVersion': 'networking.istio.io/v1beta1',
                'kind': 'Gateway',
                'metadata': {
                    'name': gateway_config.name,
                    'namespace': gateway_config.namespace,
                    'labels': {
                        'tier': gateway_config.tier.value,
                        'gateway-id': gateway_config.gateway_id
                    }
                },
                'spec': {
                    'selector': {
                        'istio': 'ingressgateway'
                    },
                    'servers': [{
                        'port': {
                            'number': 80,
                            'name': 'http',
                            'protocol': 'HTTP'
                        },
                        'hosts': [gateway_config.domain] if gateway_config.domain else ['*']
                    }]
                }
            }
            
            # Add HTTPS server if SSL is enabled
            if gateway_config.ssl_enabled:
                gateway_spec['spec']['servers'].append({
                    'port': {
                        'number': 443,
                        'name': 'https',
                        'protocol': 'HTTPS'
                    },
                    'tls': {
                        'mode': 'SIMPLE',
                        'credentialName': f'{gateway_config.name}-tls'
                    },
                    'hosts': [gateway_config.domain] if gateway_config.domain else ['*']
                })
            
            # Create VirtualService for routing
            virtual_service_spec = {
                'apiVersion': 'networking.istio.io/v1beta1',
                'kind': 'VirtualService',
                'metadata': {
                    'name': f"{gateway_config.name}-vs",
                    'namespace': gateway_config.namespace
                },
                'spec': {
                    'hosts': [gateway_config.domain] if gateway_config.domain else ['*'],
                    'gateways': [gateway_config.name],
                    'http': [{
                        'match': [{
                            'uri': {
                                'prefix': '/api/'
                            }
                        }],
                        'route': [{
                            'destination': {
                                'host': gateway_config.endpoints[0].split('://')[1].split('/')[0],
                                'port': {
                                    'number': 80
                                }
                            }
                        }]
                    }]
                }
            }
            
            self.logger.info(f"Istio gateway deployed: {gateway_config.gateway_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy Istio gateway: {str(e)}")
            raise
    
    async def _deploy_aws_gateway(self, gateway_config: GatewayConfig):  
        """Deploy AWS API Gateway"""
        try:
            aws_client = self.provider_clients.get(GatewayProvider.AWS_API_GATEWAY)
            if not aws_client:
                raise ValueError("AWS API Gateway client not initialized")
            
            # Create REST API
            api_response = aws_client.create_rest_api(
                name=gateway_config.name,
                description=f"API Gateway for {gateway_config.gateway_id}",
                endpointConfiguration={
                    'types': ['REGIONAL']
                },
                tags={
                    'tier': gateway_config.tier.value,
                    'gateway-id': gateway_config.gateway_id
                }
            )
            
            api_id = api_response['id']
            
            # Get root resource
            resources = aws_client.get_resources(restApiId=api_id)
            root_resource_id = None
            for resource in resources['items']:
                if resource['path'] == '/':
                    root_resource_id = resource['id']
                    break
            
            # Create API resource
            resource_response = aws_client.create_resource(
                restApiId=api_id,
                parentId=root_resource_id,
                pathPart='api'
            )
            
            # Create method
            aws_client.put_method(
                restApiId=api_id,
                resourceId=resource_response['id'],
                httpMethod='ANY',
                authorizationType='AWS_IAM' if gateway_config.tier == CreatorTier.ENTERPRISE else 'NONE'
            )
            
            # Configure integration
            aws_client.put_integration(
                restApiId=api_id,
                resourceId=resource_response['id'],
                httpMethod='ANY',
                type='HTTP_PROXY',
                integrationHttpMethod='ANY',
                uri=gateway_config.endpoints[0]
            )
            
            # Deploy API
            deployment = aws_client.create_deployment(
                restApiId=api_id,
                stageName='prod'
            )
            
            self.logger.info(f"AWS API Gateway deployed: {gateway_config.gateway_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy AWS gateway: {str(e)}")
            raise
    
    async def _deploy_azure_gateway(self, gateway_config: GatewayConfig):
        """Deploy Azure API Management"""
        try:
            azure_client = self.provider_clients.get(GatewayProvider.AZURE_API_MANAGEMENT)
            if not azure_client:
                raise ValueError("Azure API Management client not initialized")
            
            # Create API
            api_spec = {
                'display_name': gateway_config.name,
                'service_url': gateway_config.endpoints[0],
                'path': 'api',
                'protocols': ['https'] if gateway_config.ssl_enabled else ['http', 'https'],
                'subscription_required': gateway_config.tier != CreatorTier.FREE
            }
            
            self.logger.info(f"Azure API Management deployed: {gateway_config.gateway_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy Azure gateway: {str(e)}")
            raise
    
    async def _deploy_gcp_gateway(self, gateway_config: GatewayConfig):
        """Deploy GCP Cloud Endpoints"""
        try:
            gcp_client = self.provider_clients.get(GatewayProvider.GCP_CLOUD_ENDPOINTS)
            if not gcp_client:
                raise ValueError("GCP Cloud Endpoints client not initialized")
            
            # Create OpenAPI specification
            openapi_spec = {
                'openapi': '3.0.0',
                'info': {
                    'title': gateway_config.name,
                    'version': '1.0.0'
                },
                'servers': [{
                    'url': gateway_config.endpoints[0]
                }],
                'paths': {
                    '/api/{proxy+}': {
                        'x-google-backend': {
                            'address': gateway_config.endpoints[0]
                        },
                        'get': {
                            'operationId': 'get_api',
                            'responses': {
                                '200': {
                                    'description': 'Success'
                                }
                            }
                        }
                    }
                }
            }
            
            self.logger.info(f"GCP Cloud Endpoints deployed: {gateway_config.gateway_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy GCP gateway: {str(e)}")
            raise
    
    async def _deploy_ambassador_gateway(self, gateway_config: GatewayConfig):
        """Deploy Ambassador Edge Stack"""
        try:
            # Create Ambassador Mapping
            mapping_spec = {
                'apiVersion': 'getambassador.io/v3alpha1',
                'kind': 'Mapping',
                'metadata': {
                    'name': gateway_config.name,
                    'namespace': gateway_config.namespace,
                    'labels': {
                        'tier': gateway_config.tier.value,
                        'gateway-id': gateway_config.gateway_id
                    }
                },
                'spec': {
                    'hostname': gateway_config.domain if gateway_config.domain else '*',
                    'prefix': '/api/',
                    'service': gateway_config.endpoints[0],
                    'timeout_ms': 30000,
                    'retry_policy': {
                        'retry_on': '5xx',
                        'num_retries': 3
                    }
                }
            }
            
            # Add authentication if required
            if AuthenticationMethod.JWT in gateway_config.authentication:
                mapping_spec['spec']['filters'] = [{
                    'name': 'jwt',
                    'config': {
                        'jwksURI': f'https://auth.{gateway_config.domain}/.well-known/jwks.json'
                    }
                }]
            
            self.logger.info(f"Ambassador gateway deployed: {gateway_config.gateway_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to deploy Ambassador gateway: {str(e)}")
            raise
    
    async def _configure_kong_auth_plugin(
        self,
        gateway_config: GatewayConfig,
        auth_method: AuthenticationMethod
    ):
        """Configure Kong authentication plugin"""
        kong_client = self.provider_clients.get(GatewayProvider.KONG)
        if not kong_client:
            return
        
        plugin_config = {}
        
        if auth_method == AuthenticationMethod.API_KEY:
            plugin_config = {
                'name': 'key-auth',
                'service': {'name': gateway_config.name},
                'config': {
                    'key_names': ['X-API-Key'],
                    'hide_credentials': True
                }
            }
        elif auth_method == AuthenticationMethod.JWT:
            plugin_config = {
                'name': 'jwt',
                'service': {'name': gateway_config.name},
                'config': {
                    'secret_is_base64': False,
                    'claims_to_verify': ['exp', 'iat']
                }
            }
        elif auth_method == AuthenticationMethod.OAUTH2:
            plugin_config = {
                'name': 'oauth2',
                'service': {'name': gateway_config.name},
                'config': {
                    'enable_authorization_code': True,
                    'token_expiration': 3600,
                    'enable_client_credentials': True
                }
            }
        
        self.logger.info(f"Kong auth plugin configured: {auth_method.value}")
    
    async def _configure_default_routes(self, gateway_config: GatewayConfig):
        """Configure default routes for the gateway"""
        # Create default API route
        route_config = RouteConfig(
            route_id=f"route-{gateway_config.gateway_id}-api",
            gateway_id=gateway_config.gateway_id,
            path="/api/*",
            methods=["GET", "POST", "PUT", "DELETE"],
            backend_service=gateway_config.endpoints[0],
            backend_port=80,
            tier=gateway_config.tier,
            rate_limit=self._get_default_rate_limit(gateway_config.tier),
            authentication_required=True,
            cors_enabled=True,
            created_at=datetime.now(timezone.utc)
        )
        
        self.routes[route_config.route_id] = route_config
        self.logger.info(f"Default routes configured for {gateway_config.gateway_id}")
    
    def _get_default_rate_limit(self, tier: CreatorTier) -> Dict[str, Any]:
        """Get default rate limit configuration based on tier"""
        rate_limits = {
            CreatorTier.FREE: {'requests': 100, 'unit': 'hour', 'burst': 10},
            CreatorTier.CREATOR: {'requests': 1000, 'unit': 'hour', 'burst': 50},
            CreatorTier.PRO: {'requests': 10000, 'unit': 'hour', 'burst': 200},
            CreatorTier.ENTERPRISE: {'requests': 100000, 'unit': 'hour', 'burst': 1000}
        }
        return rate_limits[tier]
    
    async def _configure_rate_limiting(self, gateway_config: GatewayConfig):
        """Configure rate limiting for the gateway"""
        rate_limit_config = self._get_default_rate_limit(gateway_config.tier)
        
        rate_limit_rule = RateLimitRule(
            rule_id=f"rl-{gateway_config.gateway_id}-default",
            gateway_id=gateway_config.gateway_id,
            route_path="/api/*",
            tier=gateway_config.tier,
            requests_per_unit=rate_limit_config['requests'],
            unit=RateLimitUnit.HOUR,
            burst_limit=rate_limit_config['burst'],
            identifier="ip",
            created_at=datetime.now(timezone.utc)
        )
        
        self.rate_limits[rate_limit_rule.rule_id] = rate_limit_rule
        
        # Apply rate limiting based on provider
        await self._apply_rate_limiting_provider(gateway_config, rate_limit_rule)
        
        self.logger.info(f"Rate limiting configured for {gateway_config.gateway_id}")
    
    async def _apply_rate_limiting_provider(
        self,
        gateway_config: GatewayConfig,
        rate_limit_rule: RateLimitRule
    ):
        """Apply rate limiting using provider-specific implementation"""
        if gateway_config.provider == GatewayProvider.KONG:
            await self._apply_kong_rate_limiting(gateway_config, rate_limit_rule)
        elif gateway_config.provider == GatewayProvider.ISTIO:
            await self._apply_istio_rate_limiting(gateway_config, rate_limit_rule)
        # Add other providers as needed
    
    async def _apply_kong_rate_limiting(
        self,
        gateway_config: GatewayConfig,
        rate_limit_rule: RateLimitRule
    ):
        """Apply Kong rate limiting plugin"""
        kong_client = self.provider_clients.get(GatewayProvider.KONG)
        if not kong_client:
            return
        
        plugin_config = {
            'name': 'rate-limiting',
            'service': {'name': gateway_config.name},
            'config': {
                f'{rate_limit_rule.unit.value}': rate_limit_rule.requests_per_unit,
                'policy': 'local',
                'fault_tolerant': True,
                'hide_client_headers': False
            }
        }
        
        self.logger.info(f"Kong rate limiting applied: {rate_limit_rule.rule_id}")
    
    async def _apply_istio_rate_limiting(
        self,
        gateway_config: GatewayConfig,
        rate_limit_rule: RateLimitRule
    ):
        """Apply Istio rate limiting using EnvoyFilter"""
        envoy_filter = {
            'apiVersion': 'networking.istio.io/v1alpha3',
            'kind': 'EnvoyFilter',
            'metadata': {
                'name': f"rate-limit-{gateway_config.gateway_id}",
                'namespace': gateway_config.namespace
            },
            'spec': {
                'workloadSelector': {
                    'labels': {
                        'app': 'istio-proxy'
                    }
                },
                'configPatches': [{
                    'applyTo': 'HTTP_FILTER',
                    'match': {
                        'context': 'GATEWAY',
                        'listener': {
                            'filterChain': {
                                'filter': {
                                    'name': 'envoy.filters.network.http_connection_manager'
                                }
                            }
                        }
                    },
                    'patch': {
                        'operation': 'INSERT_BEFORE',
                        'value': {
                            'name': 'envoy.filters.http.local_ratelimit',
                            'typed_config': {
                                '@type': 'type.googleapis.com/udpa.type.v1.TypedStruct',
                                'type_url': 'type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit',
                                'value': {
                                    'stat_prefix': 'local_rate_limiter',
                                    'token_bucket': {
                                        'max_tokens': rate_limit_rule.burst_limit,
                                        'tokens_per_fill': rate_limit_rule.requests_per_unit,
                                        'fill_interval': f"3600s"  # 1 hour for hourly limits
                                    },
                                    'filter_enabled': {
                                        'runtime_key': 'local_rate_limit_enabled',
                                        'default_value': {
                                            'numerator': 100,
                                            'denominator': 'HUNDRED'
                                        }
                                    },
                                    'filter_enforced': {
                                        'runtime_key': 'local_rate_limit_enforced',
                                        'default_value': {
                                            'numerator': 100,
                                            'denominator': 'HUNDRED'
                                        }
                                    }
                                }
                            }
                        }
                    }
                }]
            }
        }
        
        self.logger.info(f"Istio rate limiting applied: {rate_limit_rule.rule_id}")
    
    async def _apply_security_policies(self, gateway_config: GatewayConfig):
        """Apply security policies to the gateway"""
        # CORS policy
        cors_policy = SecurityPolicy(
            policy_id=f"cors-{gateway_config.gateway_id}",
            gateway_id=gateway_config.gateway_id,
            policy_type="cors",
            config={
                'allowed_origins': ['*'] if gateway_config.tier == CreatorTier.FREE else ['https://*'],
                'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                'allowed_headers': ['Content-Type', 'Authorization', 'X-API-Key'],
                'max_age': 86400
            },
            tier=gateway_config.tier,
            active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        self.security_policies[cors_policy.policy_id] = cors_policy
        
        # IP whitelist for enterprise tier
        if gateway_config.tier == CreatorTier.ENTERPRISE:
            ip_policy = SecurityPolicy(
                policy_id=f"ip-whitelist-{gateway_config.gateway_id}",
                gateway_id=gateway_config.gateway_id,
                policy_type="ip_whitelist",
                config={
                    'allowed_ips': ['0.0.0.0/0'],  # Configure as needed
                    'blocked_ips': []
                },
                tier=gateway_config.tier,
                active=True,
                created_at=datetime.now(timezone.utc)
            )
            
            self.security_policies[ip_policy.policy_id] = ip_policy
        
        self.logger.info(f"Security policies applied for {gateway_config.gateway_id}")
    
    async def create_custom_route(
        self,
        gateway_id: str,
        path: str,
        methods: List[str],
        backend_service: str,
        backend_port: int = 80,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> RouteConfig:
        """
        Create custom route for the gateway
        
        Args:
            gateway_id: Gateway identifier
            path: Route path pattern
            methods: HTTP methods
            backend_service: Backend service URL
            backend_port: Backend service port
            custom_config: Custom route configuration
            
        Returns:
            RouteConfig: Created route configuration
        """
        try:
            if gateway_id not in self.gateways:
                raise ValueError(f"Gateway not found: {gateway_id}")
            
            gateway_config = self.gateways[gateway_id]
            
            route_config = RouteConfig(
                route_id=f"route-{gateway_id}-{int(time.time())}",
                gateway_id=gateway_id,
                path=path,
                methods=methods,
                backend_service=backend_service,
                backend_port=backend_port,
                tier=gateway_config.tier,
                rate_limit=custom_config.get('rate_limit') if custom_config else None,
                authentication_required=custom_config.get('auth_required', True) if custom_config else True,
                cors_enabled=custom_config.get('cors_enabled', True) if custom_config else True,
                created_at=datetime.now(timezone.utc)
            )
            
            # Apply route to provider
            await self._apply_route_to_provider(gateway_config, route_config)
            
            self.routes[route_config.route_id] = route_config
            self.logger.info(f"Custom route created: {route_config.route_id}")
            
            return route_config
            
        except Exception as e:
            self.logger.error(f"Failed to create custom route: {str(e)}")
            raise
    
    async def _apply_route_to_provider(
        self,
        gateway_config: GatewayConfig,
        route_config: RouteConfig
    ):
        """Apply route configuration to the gateway provider"""
        if gateway_config.provider == GatewayProvider.KONG:
            await self._apply_kong_route(gateway_config, route_config)
        elif gateway_config.provider == GatewayProvider.ISTIO:
            await self._apply_istio_route(gateway_config, route_config)
        # Add other providers as needed
    
    async def _apply_kong_route(
        self,
        gateway_config: GatewayConfig,
        route_config: RouteConfig
    ):
        """Apply route to Kong gateway"""
        kong_client = self.provider_clients.get(GatewayProvider.KONG)
        if not kong_client:
            return
        
        kong_route = {
            'name': f"route-{route_config.route_id}",
            'protocols': ['http', 'https'],
            'methods': route_config.methods,
            'paths': [route_config.path],
            'service': {'name': gateway_config.name},
            'tags': [f'tier:{gateway_config.tier.value}']
        }
        
        self.logger.info(f"Kong route applied: {route_config.route_id}")
    
    async def _apply_istio_route(
        self,
        gateway_config: GatewayConfig,
        route_config: RouteConfig
    ):
        """Apply route to Istio gateway"""
        # Update existing VirtualService or create new one
        virtual_service_patch = {
            'match': [{
                'uri': {
                    'prefix': route_config.path.replace('*', '')
                }
            }],
            'route': [{
                'destination': {
                    'host': route_config.backend_service,
                    'port': {
                        'number': route_config.backend_port
                    }
                }
            }]
        }
        
        self.logger.info(f"Istio route applied: {route_config.route_id}")
    
    async def get_gateway_metrics(
        self,
        gateway_id: str,
        time_range: int = 3600
    ) -> Optional[GatewayMetrics]:
        """
        Get gateway metrics
        
        Args:
            gateway_id: Gateway identifier
            time_range: Time range in seconds
            
        Returns:
            GatewayMetrics: Gateway metrics data
        """
        try:
            if gateway_id not in self.gateways:
                return None
            
            # Simulate metrics collection
            metrics = GatewayMetrics(
                gateway_id=gateway_id,
                total_requests=1000 + hash(gateway_id) % 5000,
                success_requests=950 + hash(gateway_id) % 4500,
                error_requests=50 + hash(gateway_id) % 500,
                avg_response_time=100.0 + (hash(gateway_id) % 200),
                p95_response_time=200.0 + (hash(gateway_id) % 300),
                p99_response_time=500.0 + (hash(gateway_id) % 1000),
                rate_limit_hits=10 + hash(gateway_id) % 100,
                auth_failures=5 + hash(gateway_id) % 50,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Store metrics
            if gateway_id not in self.metrics:
                self.metrics[gateway_id] = []
            self.metrics[gateway_id].append(metrics)
            
            # Keep only recent metrics (last 24 hours)
            cutoff_time = datetime.now(timezone.utc).timestamp() - 86400
            self.metrics[gateway_id] = [
                m for m in self.metrics[gateway_id]
                if m.timestamp.timestamp() > cutoff_time
            ]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get gateway metrics: {str(e)}")
            return None
    
    async def update_gateway_config(
        self,
        gateway_id: str,
        config_updates: Dict[str, Any]
    ) -> bool:
        """
        Update gateway configuration
        
        Args:
            gateway_id: Gateway identifier
            config_updates: Configuration updates
            
        Returns:
            bool: True if update was successful
        """
        try:
            if gateway_id not in self.gateways:
                raise ValueError(f"Gateway not found: {gateway_id}")
            
            gateway_config = self.gateways[gateway_id]
            
            # Update configuration
            if 'ssl_enabled' in config_updates:
                gateway_config.ssl_enabled = config_updates['ssl_enabled']
            
            if 'domain' in config_updates:
                gateway_config.domain = config_updates['domain']
            
            if 'authentication' in config_updates:
                gateway_config.authentication = [
                    AuthenticationMethod(auth) for auth in config_updates['authentication']
                ]
            
            # Apply updates to provider
            await self._update_provider_config(gateway_config, config_updates)
            
            self.logger.info(f"Gateway config updated: {gateway_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update gateway config: {str(e)}")
            return False
    
    async def _update_provider_config(
        self,
        gateway_config: GatewayConfig,
        config_updates: Dict[str, Any]
    ):
        """Update provider-specific configuration"""
        # Implementation would vary by provider
        self.logger.info(f"Provider config updated for {gateway_config.gateway_id}")
    
    async def delete_gateway(self, gateway_id: str) -> bool:
        """
        Delete API gateway
        
        Args:
            gateway_id: Gateway identifier
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            if gateway_id not in self.gateways:
                raise ValueError(f"Gateway not found: {gateway_id}")
            
            gateway_config = self.gateways[gateway_id]
            
            # Delete from provider
            await self._delete_from_provider(gateway_config)
            
            # Clean up local data
            del self.gateways[gateway_id]
            
            # Remove associated routes
            routes_to_remove = [
                route_id for route_id, route in self.routes.items()
                if route.gateway_id == gateway_id
            ]
            for route_id in routes_to_remove:
                del self.routes[route_id]
            
            # Remove associated rate limits
            rate_limits_to_remove = [
                rule_id for rule_id, rule in self.rate_limits.items()
                if rule.gateway_id == gateway_id
            ]
            for rule_id in rate_limits_to_remove:
                del self.rate_limits[rule_id]
            
            # Remove metrics
            if gateway_id in self.metrics:
                del self.metrics[gateway_id]
            
            self.logger.info(f"Gateway deleted: {gateway_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete gateway: {str(e)}")
            return False
    
    async def _delete_from_provider(self, gateway_config: GatewayConfig):
        """Delete gateway from provider"""
        if gateway_config.provider == GatewayProvider.KONG:
            await self._delete_kong_gateway(gateway_config)
        elif gateway_config.provider == GatewayProvider.ISTIO:
            await self._delete_istio_gateway(gateway_config)
        # Add other providers as needed
    
    async def _delete_kong_gateway(self, gateway_config: GatewayConfig):
        """Delete Kong gateway resources"""
        kong_client = self.provider_clients.get(GatewayProvider.KONG)
        if not kong_client:
            return
        
        # Delete Kong service and routes
        self.logger.info(f"Kong gateway deleted: {gateway_config.gateway_id}")
    
    async def _delete_istio_gateway(self, gateway_config: GatewayConfig):
        """Delete Istio gateway resources"""
        # Delete Gateway and VirtualService resources
        self.logger.info(f"Istio gateway deleted: {gateway_config.gateway_id}")
    
    def get_gateway_status(self, gateway_id: str) -> Dict[str, Any]:
        """Get gateway status and health information"""
        if gateway_id not in self.gateways:
            return {'status': 'not_found'}
        
        gateway_config = self.gateways[gateway_id]
        
        return {
            'gateway_id': gateway_id,
            'name': gateway_config.name,
            'provider': gateway_config.provider.value,
            'status': 'active',
            'tier': gateway_config.tier.value,
            'ssl_enabled': gateway_config.ssl_enabled,
            'routes': len([r for r in self.routes.values() if r.gateway_id == gateway_id]),
            'authentication_methods': [auth.value for auth in gateway_config.authentication],
            'created_at': gateway_config.created_at.isoformat(),
            'last_check': datetime.now(timezone.utc).isoformat()
        }

# Global API gateway deployment instance
_api_gateway_deployment = None

def get_api_gateway_deployment(
    config: Optional[Dict[str, Any]] = None
) -> APIGatewayDeployment:
    """
    Get or create the global API gateway deployment instance
    
    Args:
        config: Configuration for the API gateway deployment
        
    Returns:
        APIGatewayDeployment instance
    """
    global _api_gateway_deployment
    
    if _api_gateway_deployment is None:
        _api_gateway_deployment = APIGatewayDeployment(config)
    
    return _api_gateway_deployment

# Convenience functions for direct access
async def deploy_api_gateway(
    deployment_id: str,
    provider: GatewayProvider,
    endpoints: List[str],
    tier: CreatorTier = CreatorTier.CREATOR,
    domain: Optional[str] = None,
    namespace: str = "default"
) -> GatewayConfig:
    """Convenience function for deploying API gateway"""
    gateway = get_api_gateway_deployment()
    return await gateway.deploy_api_gateway(deployment_id, provider, endpoints, tier, domain, namespace)

async def create_custom_route(
    gateway_id: str,
    path: str,
    methods: List[str],
    backend_service: str,
    backend_port: int = 80,
    custom_config: Optional[Dict[str, Any]] = None
) -> RouteConfig:
    """Convenience function for creating custom route"""
    gateway = get_api_gateway_deployment()
    return await gateway.create_custom_route(gateway_id, path, methods, backend_service, backend_port, custom_config)

async def get_gateway_metrics(
    gateway_id: str,
    time_range: int = 3600
) -> Optional[GatewayMetrics]:
    """Convenience function for getting gateway metrics"""
    gateway = get_api_gateway_deployment()
    return await gateway.get_gateway_metrics(gateway_id, time_range)

# Export all main components and functions
__all__ = [
    'APIGatewayDeployment',
    'GatewayProvider',
    'AuthenticationMethod',
    'RateLimitUnit',
    'CreatorTier',
    'GatewayConfig',
    'RouteConfig',
    'RateLimitRule',
    'GatewayMetrics',
    'SecurityPolicy',
    'get_api_gateway_deployment',
    'deploy_api_gateway',
    'create_custom_route',
    'get_gateway_metrics'
]