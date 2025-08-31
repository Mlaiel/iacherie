"""Service Deployer - Deployment Automation

Advanced service deployment engine for the IA Influencer Agent platform,
handling deployment of AI services, content protection, monetization,
and microservices with intelligent rollout strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import json
import yaml
from pathlib import Path
import hashlib

from ..core.base import BaseComponent
from ..kubernetes.deployment_manager import DeploymentManager
from ..containers.image_manager import ImageManager
from ..config.service_config import ServiceConfigManager
from ..monitoring.health_checker import HealthChecker
from ..security.security_scanner import SecurityScanner


class ServiceType(Enum):
    """Service types in the IA Influencer Agent platform"""
    AI_AGENT = "ai_agent"
    CONTENT_PROTECTION = "content_protection"
    FINGERPRINTING = "fingerprinting"
    MONETIZATION = "monetization"
    CRAWLER = "crawler"
    API_GATEWAY = "api_gateway"
    DATABASE = "database"
    CACHE = "cache"
    MESSAGE_QUEUE = "message_queue"
    MONITORING = "monitoring"
    STORAGE = "storage"


class DeploymentStatus(Enum):
    """Deployment status types"""
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    RUNNING = "running"
    UPDATING = "updating"
    SCALING = "scaling"
    FAILED = "failed"
    STOPPED = "stopped"
    TERMINATING = "terminating"


@dataclass
class ServiceSpec:
    """Service deployment specification"""
    name: str
    service_type: ServiceType
    image: str
    version: str
    replicas: int = 3
    cpu_request: str = "100m"
    cpu_limit: str = "500m"
    memory_request: str = "256Mi"
    memory_limit: str = "512Mi"
    gpu_request: Optional[str] = None
    environment_variables: Dict[str, str] = field(default_factory=dict)
    secrets: List[str] = field(default_factory=list)
    config_maps: List[str] = field(default_factory=list)
    volumes: List[Dict[str, Any]] = field(default_factory=list)
    ports: List[Dict[str, Any]] = field(default_factory=list)
    health_check: Optional[Dict[str, Any]] = None
    autoscaling: Optional[Dict[str, Any]] = None
    service_mesh: bool = True
    security_context: Optional[Dict[str, Any]] = None
    annotations: Dict[str, str] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class DeploymentContext:
    """Deployment execution context"""
    deployment_id: str
    environment: str
    namespace: str
    strategy: str = "rolling"
    max_unavailable: str = "25%"
    max_surge: str = "25%"
    rollback_on_failure: bool = True
    timeout: int = 600
    pre_deployment_hooks: List[str] = field(default_factory=list)
    post_deployment_hooks: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    notification_channels: List[str] = field(default_factory=list)


class ServiceDeployer(BaseComponent):
    """
    Enterprise-grade service deployment engine.
    
    Handles deployment of microservices across the IA Influencer Agent platform
    with support for multiple deployment strategies, health validation, and
    automated rollbacks.
    """
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core managers
        self.deployment_manager = DeploymentManager(config.get('kubernetes', {}))
        self.image_manager = ImageManager(config.get('images', {}))
        self.config_manager = ServiceConfigManager(config.get('service_config', {}))
        self.health_checker = HealthChecker(config.get('health_checks', {}))
        self.security_scanner = SecurityScanner(config.get('security', {}))
        
        # Deployment state
        self.active_deployments: Dict[str, Dict[str, Any]] = {}
        self.service_registry: Dict[str, ServiceSpec] = {}
        
        # Service templates
        self.service_templates = self._load_service_templates()
        
        # Deployment strategies
        self.deployment_strategies = {
            'rolling': self._rolling_deployment,
            'blue_green': self._blue_green_deployment,
            'canary': self._canary_deployment,
            'recreate': self._recreate_deployment
        }

    def _load_service_templates(self) -> Dict[str, ServiceSpec]:
        """Load service deployment templates"""
        templates = {}
        
        # AI Agent Service Template
        templates['ai_agent'] = ServiceSpec(
            name="ia-influencer-ai-agent",
            service_type=ServiceType.AI_AGENT,
            image="ia-influencer/ai-agent",
            version="2.0.0",
            replicas=3,
            cpu_request="500m",
            cpu_limit="2000m",
            memory_request="1Gi",
            memory_limit="4Gi",
            gpu_request="1",
            environment_variables={
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "info",
                "AI_MODEL_PATH": "/models",
                "REDIS_URL": "redis://redis-service:6379",
                "DATABASE_URL": "postgresql://postgres:5432/ia_influencer_agent"
            },
            secrets=["ai-agent-secrets", "database-credentials"],
            config_maps=["ai-agent-config"],
            volumes=[
                {
                    "name": "model-storage",
                    "mountPath": "/models",
                    "type": "persistentVolumeClaim",
                    "claimName": "ai-models-pvc"
                },
                {
                    "name": "temp-storage",
                    "mountPath": "/tmp",
                    "type": "emptyDir"
                }
            ],
            ports=[
                {"name": "http", "containerPort": 8000, "protocol": "TCP"},
                {"name": "grpc", "containerPort": 9000, "protocol": "TCP"},
                {"name": "metrics", "containerPort": 9090, "protocol": "TCP"}
            ],
            health_check={
                "livenessProbe": {
                    "httpGet": {"path": "/health", "port": 8000},
                    "initialDelaySeconds": 30,
                    "periodSeconds": 10
                },
                "readinessProbe": {
                    "httpGet": {"path": "/ready", "port": 8000},
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5
                }
            },
            autoscaling={
                "minReplicas": 2,
                "maxReplicas": 20,
                "targetCPUUtilizationPercentage": 70,
                "targetMemoryUtilizationPercentage": 80
            },
            labels={
                "app": "ia-influencer-ai-agent",
                "component": "ai-processing",
                "tier": "backend"
            }
        )
        
        # Content Protection Service Template
        templates['content_protection'] = ServiceSpec(
            name="ia-influencer-content-protection",
            service_type=ServiceType.CONTENT_PROTECTION,
            image="ia-influencer/content-protection",
            version="2.0.0",
            replicas=3,
            cpu_request="1000m",
            cpu_limit="3000m",
            memory_request="2Gi",
            memory_limit="8Gi",
            environment_variables={
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "info",
                "FINGERPRINT_ENGINE": "advanced",
                "VECTOR_DB_URL": "faiss://vector-db:8080",
                "REDIS_URL": "redis://redis-service:6379"
            },
            secrets=["content-protection-secrets"],
            config_maps=["content-protection-config"],
            volumes=[
                {
                    "name": "fingerprint-cache",
                    "mountPath": "/cache",
                    "type": "persistentVolumeClaim",
                    "claimName": "fingerprint-cache-pvc"
                }
            ],
            ports=[
                {"name": "http", "containerPort": 8001, "protocol": "TCP"},
                {"name": "metrics", "containerPort": 9091, "protocol": "TCP"}
            ],
            health_check={
                "livenessProbe": {
                    "httpGet": {"path": "/health", "port": 8001},
                    "initialDelaySeconds": 45,
                    "periodSeconds": 15
                },
                "readinessProbe": {
                    "httpGet": {"path": "/ready", "port": 8001},
                    "initialDelaySeconds": 10,
                    "periodSeconds": 5
                }
            },
            autoscaling={
                "minReplicas": 2,
                "maxReplicas": 15,
                "targetCPUUtilizationPercentage": 75
            },
            labels={
                "app": "ia-influencer-content-protection",
                "component": "content-protection",
                "tier": "backend"
            }
        )
        
        # Fingerprinting Service Template
        templates['fingerprinting'] = ServiceSpec(
            name="ia-influencer-fingerprinting",
            service_type=ServiceType.FINGERPRINTING,
            image="ia-influencer/fingerprinting",
            version="2.0.0",
            replicas=5,
            cpu_request="2000m",
            cpu_limit="4000m",
            memory_request="4Gi",
            memory_limit="16Gi",
            gpu_request="1",
            environment_variables={
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "info",
                "AUDIO_ENGINE": "chromaprint",
                "VIDEO_ENGINE": "opencv",
                "IMAGE_ENGINE": "clip",
                "TEXT_ENGINE": "bert"
            },
            secrets=["fingerprinting-secrets"],
            config_maps=["fingerprinting-config"],
            volumes=[
                {
                    "name": "temp-processing",
                    "mountPath": "/tmp/processing",
                    "type": "emptyDir",
                    "sizeLimit": "50Gi"
                }
            ],
            ports=[
                {"name": "http", "containerPort": 8002, "protocol": "TCP"},
                {"name": "metrics", "containerPort": 9092, "protocol": "TCP"}
            ],
            health_check={
                "livenessProbe": {
                    "httpGet": {"path": "/health", "port": 8002},
                    "initialDelaySeconds": 60,
                    "periodSeconds": 20
                },
                "readinessProbe": {
                    "httpGet": {"path": "/ready", "port": 8002},
                    "initialDelaySeconds": 15,
                    "periodSeconds": 10
                }
            },
            autoscaling={
                "minReplicas": 3,
                "maxReplicas": 25,
                "targetCPUUtilizationPercentage": 80,
                "targetMemoryUtilizationPercentage": 85
            },
            labels={
                "app": "ia-influencer-fingerprinting",
                "component": "fingerprinting",
                "tier": "processing"
            }
        )
        
        # Monetization Service Template
        templates['monetization'] = ServiceSpec(
            name="ia-influencer-monetization",
            service_type=ServiceType.MONETIZATION,
            image="ia-influencer/monetization",
            version="2.0.0",
            replicas=3,
            cpu_request="500m",
            cpu_limit="1500m",
            memory_request="1Gi",
            memory_limit="3Gi",
            environment_variables={
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "info",
                "PAYMENT_GATEWAY": "stripe",
                "BLOCKCHAIN_NETWORK": "ethereum",
                "ANALYTICS_ENGINE": "advanced"
            },
            secrets=["monetization-secrets", "payment-credentials"],
            config_maps=["monetization-config"],
            ports=[
                {"name": "http", "containerPort": 8003, "protocol": "TCP"},
                {"name": "metrics", "containerPort": 9093, "protocol": "TCP"}
            ],
            health_check={
                "livenessProbe": {
                    "httpGet": {"path": "/health", "port": 8003},
                    "initialDelaySeconds": 30,
                    "periodSeconds": 10
                },
                "readinessProbe": {
                    "httpGet": {"path": "/ready", "port": 8003},
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5
                }
            },
            autoscaling={
                "minReplicas": 2,
                "maxReplicas": 12,
                "targetCPUUtilizationPercentage": 70
            },
            labels={
                "app": "ia-influencer-monetization",
                "component": "monetization",
                "tier": "backend"
            }
        )
        
        # Crawler Service Template
        templates['crawler'] = ServiceSpec(
            name="ia-influencer-crawler",
            service_type=ServiceType.CRAWLER,
            image="ia-influencer/crawler",
            version="2.0.0",
            replicas=4,
            cpu_request="1000m",
            cpu_limit="2500m",
            memory_request="2Gi",
            memory_limit="6Gi",
            environment_variables={
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "info",
                "CRAWLER_MODE": "distributed",
                "RATE_LIMIT": "1000",
                "USER_AGENT_ROTATION": "true"
            },
            secrets=["crawler-secrets", "api-credentials"],
            config_maps=["crawler-config"],
            volumes=[
                {
                    "name": "crawler-cache",
                    "mountPath": "/cache",
                    "type": "persistentVolumeClaim",
                    "claimName": "crawler-cache-pvc"
                }
            ],
            ports=[
                {"name": "http", "containerPort": 8004, "protocol": "TCP"},
                {"name": "metrics", "containerPort": 9094, "protocol": "TCP"}
            ],
            health_check={
                "livenessProbe": {
                    "httpGet": {"path": "/health", "port": 8004},
                    "initialDelaySeconds": 40,
                    "periodSeconds": 15
                },
                "readinessProbe": {
                    "httpGet": {"path": "/ready", "port": 8004},
                    "initialDelaySeconds": 10,
                    "periodSeconds": 10
                }
            },
            autoscaling={
                "minReplicas": 2,
                "maxReplicas": 18,
                "targetCPUUtilizationPercentage": 75
            },
            labels={
                "app": "ia-influencer-crawler",
                "component": "crawler",
                "tier": "processing"
            }
        )
        
        # API Gateway Template
        templates['api_gateway'] = ServiceSpec(
            name="ia-influencer-api-gateway",
            service_type=ServiceType.API_GATEWAY,
            image="ia-influencer/api-gateway",
            version="2.0.0",
            replicas=3,
            cpu_request="500m",
            cpu_limit="2000m",
            memory_request="512Mi",
            memory_limit="2Gi",
            environment_variables={
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "info",
                "RATE_LIMITING": "true",
                "CORS_ENABLED": "true",
                "JWT_VALIDATION": "true"
            },
            secrets=["api-gateway-secrets", "jwt-secrets"],
            config_maps=["api-gateway-config"],
            ports=[
                {"name": "http", "containerPort": 8080, "protocol": "TCP"},
                {"name": "https", "containerPort": 8443, "protocol": "TCP"},
                {"name": "metrics", "containerPort": 9095, "protocol": "TCP"}
            ],
            health_check={
                "livenessProbe": {
                    "httpGet": {"path": "/health", "port": 8080},
                    "initialDelaySeconds": 20,
                    "periodSeconds": 10
                },
                "readinessProbe": {
                    "httpGet": {"path": "/ready", "port": 8080},
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5
                }
            },
            autoscaling={
                "minReplicas": 3,
                "maxReplicas": 15,
                "targetCPUUtilizationPercentage": 70
            },
            labels={
                "app": "ia-influencer-api-gateway",
                "component": "api-gateway",
                "tier": "frontend"
            }
        )
        
        # Audio Processing Service Template
        templates['audio_processing'] = ServiceSpec(
            name="ia-influencer-audio-processing",
            service_type=ServiceType.AI_AGENT,
            image="ia-influencer/audio-processing",
            version="2.0.0",
            replicas=4,
            cpu_request="2000m",
            cpu_limit="6000m",
            memory_request="4Gi",
            memory_limit="12Gi",
            gpu_request="1",
            environment_variables={
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "info",
                "AUDIO_SAMPLE_RATE": "44100",
                "GPU_ACCELERATION": "true",
                "MODEL_CACHE_SIZE": "10Gi",
                "PROCESSING_QUEUE": "redis"
            },
            secrets=["audio-processing-secrets", "model-api-keys"],
            config_maps=["audio-processing-config"],
            volumes=[
                {
                    "name": "audio-models",
                    "mountPath": "/models/audio",
                    "type": "persistentVolumeClaim",
                    "claimName": "audio-models-pvc"
                },
                {
                    "name": "audio-temp",
                    "mountPath": "/tmp/audio",
                    "type": "emptyDir",
                    "sizeLimit": "100Gi"
                }
            ],
            ports=[
                {"name": "http", "containerPort": 8005, "protocol": "TCP"},
                {"name": "grpc", "containerPort": 9005, "protocol": "TCP"},
                {"name": "metrics", "containerPort": 9096, "protocol": "TCP"}
            ],
            health_check={
                "livenessProbe": {
                    "httpGet": {"path": "/health", "port": 8005},
                    "initialDelaySeconds": 90,
                    "periodSeconds": 30
                },
                "readinessProbe": {
                    "httpGet": {"path": "/ready", "port": 8005},
                    "initialDelaySeconds": 30,
                    "periodSeconds": 15
                }
            },
            autoscaling={
                "minReplicas": 2,
                "maxReplicas": 20,
                "targetCPUUtilizationPercentage": 80,
                "targetMemoryUtilizationPercentage": 85
            },
            labels={
                "app": "ia-influencer-audio-processing",
                "component": "audio-processing",
                "tier": "ai-processing"
            }
        )

        # Collaboration Matching Service Template
        templates['collaboration_matching'] = ServiceSpec(
            name="ia-influencer-collaboration-matching",
            service_type=ServiceType.AI_AGENT,
            image="ia-influencer/collaboration-matching",
            version="2.0.0",
            replicas=3,
            cpu_request="1000m",
            cpu_limit="3000m",
            memory_request="2Gi",
            memory_limit="6Gi",
            environment_variables={
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "info",
                "MATCHING_ALGORITHM": "neural_collaborative_filtering",
                "RECOMMENDATION_ENGINE": "transformer",
                "SIMILARITY_THRESHOLD": "0.75"
            },
            secrets=["collaboration-secrets", "recommendation-api-keys"],
            config_maps=["collaboration-config"],
            volumes=[
                {
                    "name": "matching-models",
                    "mountPath": "/models/matching",
                    "type": "persistentVolumeClaim",
                    "claimName": "matching-models-pvc"
                }
            ],
            ports=[
                {"name": "http", "containerPort": 8006, "protocol": "TCP"},
                {"name": "metrics", "containerPort": 9097, "protocol": "TCP"}
            ],
            health_check={
                "livenessProbe": {
                    "httpGet": {"path": "/health", "port": 8006},
                    "initialDelaySeconds": 45,
                    "periodSeconds": 20
                },
                "readinessProbe": {
                    "httpGet": {"path": "/ready", "port": 8006},
                    "initialDelaySeconds": 10,
                    "periodSeconds": 10
                }
            },
            autoscaling={
                "minReplicas": 2,
                "maxReplicas": 12,
                "targetCPUUtilizationPercentage": 75
            },
            labels={
                "app": "ia-influencer-collaboration-matching",
                "component": "collaboration-matching",
                "tier": "ai-processing"
            }
        )

        # Revenue Analytics Service Template  
        templates['revenue_analytics'] = ServiceSpec(
            name="ia-influencer-revenue-analytics",
            service_type=ServiceType.MONETIZATION,
            image="ia-influencer/revenue-analytics",
            version="2.0.0",
            replicas=3,
            cpu_request="1000m",
            cpu_limit="2500m",
            memory_request="2Gi",
            memory_limit="5Gi",
            environment_variables={
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "info",
                "ANALYTICS_ENGINE": "spark",
                "REAL_TIME_PROCESSING": "true",
                "PREDICTION_MODEL": "lstm_forecasting"
            },
            secrets=["revenue-analytics-secrets", "platform-api-keys"],
            config_maps=["revenue-analytics-config"],
            volumes=[
                {
                    "name": "analytics-cache",
                    "mountPath": "/cache/analytics",
                    "type": "persistentVolumeClaim",
                    "claimName": "analytics-cache-pvc"
                }
            ],
            ports=[
                {"name": "http", "containerPort": 8007, "protocol": "TCP"},
                {"name": "metrics", "containerPort": 9098, "protocol": "TCP"}
            ],
            health_check={
                "livenessProbe": {
                    "httpGet": {"path": "/health", "port": 8007},
                    "initialDelaySeconds": 60,
                    "periodSeconds": 25
                },
                "readinessProbe": {
                    "httpGet": {"path": "/ready", "port": 8007},
                    "initialDelaySeconds": 15,
                    "periodSeconds": 10
                }
            },
            autoscaling={
                "minReplicas": 2,
                "maxReplicas": 15,
                "targetCPUUtilizationPercentage": 80
            },
            labels={
                "app": "ia-influencer-revenue-analytics",
                "component": "revenue-analytics",
                "tier": "analytics"
            }
        )

        # SEO Optimization Service Template
        templates['seo_optimization'] = ServiceSpec(
            name="ia-influencer-seo-optimization",
            service_type=ServiceType.AI_AGENT,
            image="ia-influencer/seo-optimization",
            version="2.0.0",
            replicas=2,
            cpu_request="500m",
            cpu_limit="1500m",
            memory_request="1Gi",
            memory_limit="3Gi",
            environment_variables={
                "ENVIRONMENT": "production",
                "LOG_LEVEL": "info",
                "SEO_ENGINE": "advanced_nlp",
                "KEYWORD_RESEARCH": "true",
                "CONTENT_OPTIMIZATION": "true"
            },
            secrets=["seo-secrets", "keyword-api-keys"],
            config_maps=["seo-config"],
            ports=[
                {"name": "http", "containerPort": 8008, "protocol": "TCP"},
                {"name": "metrics", "containerPort": 9099, "protocol": "TCP"}
            ],
            health_check={
                "livenessProbe": {
                    "httpGet": {"path": "/health", "port": 8008},
                    "initialDelaySeconds": 30,
                    "periodSeconds": 15
                },
                "readinessProbe": {
                    "httpGet": {"path": "/ready", "port": 8008},
                    "initialDelaySeconds": 5,
                    "periodSeconds": 5
                }
            },
            autoscaling={
                "minReplicas": 1,
                "maxReplicas": 8,
                "targetCPUUtilizationPercentage": 70
            },
            labels={
                "app": "ia-influencer-seo-optimization",
                "component": "seo-optimization",
                "tier": "content-processing"
            }
        )

        return templates

    async def deploy_services(
        self,
        services: List[str],
        environment: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deploy multiple services to the specified environment.
        
        Args:
            services: List of service names to deploy
            environment: Target environment
            context: Deployment context and configuration
            
        Returns:
            Deployment results for all services
        """
        deployment_id = context.get('deployment_id', f"deploy-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}")
        
        self.logger.info(f"Starting deployment of {len(services)} services to {environment}")
        
        deployment_context = DeploymentContext(
            deployment_id=deployment_id,
            environment=environment,
            namespace=context.get('namespace', f"ia-influencer-{environment}"),
            strategy=context.get('strategy', 'rolling'),
            **context.get('deployment_options', {})
        )
        
        # Initialize deployment state
        deployment_state = {
            'deployment_id': deployment_id,
            'environment': environment,
            'services': services,
            'status': DeploymentStatus.PENDING,
            'start_time': datetime.utcnow(),
            'context': deployment_context,
            'service_results': {},
            'errors': []
        }
        
        self.active_deployments[deployment_id] = deployment_state
        
        try:
            # Pre-deployment validation
            await self._validate_deployment_prerequisites(services, deployment_context)
            
            # Build and push container images
            deployment_state['status'] = DeploymentStatus.BUILDING
            image_results = await self._build_and_push_images(services, deployment_context)
            deployment_state['image_results'] = image_results
            
            # Execute pre-deployment hooks
            await self._execute_pre_deployment_hooks(deployment_context)
            
            # Deploy services based on strategy
            deployment_state['status'] = DeploymentStatus.DEPLOYING
            strategy_handler = self.deployment_strategies.get(deployment_context.strategy)
            
            if not strategy_handler:
                raise ValueError(f"Unsupported deployment strategy: {deployment_context.strategy}")
            
            service_results = await strategy_handler(services, deployment_context)
            deployment_state['service_results'] = service_results
            
            # Validate deployment health
            health_results = await self._validate_deployment_health(services, deployment_context)
            deployment_state['health_results'] = health_results
            
            # Execute post-deployment hooks
            await self._execute_post_deployment_hooks(deployment_context)
            
            deployment_state['status'] = DeploymentStatus.RUNNING
            deployment_state['end_time'] = datetime.utcnow()
            
            self.logger.info(f"Deployment completed successfully: {deployment_id}")
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {deployment_id}", exc_info=True)
            deployment_state['status'] = DeploymentStatus.FAILED
            deployment_state['errors'].append(str(e))
            deployment_state['end_time'] = datetime.utcnow()
            
            # Attempt rollback if enabled
            if deployment_context.rollback_on_failure:
                await self._rollback_deployment(deployment_id, str(e))
            
            raise
        
        return deployment_state

    async def _validate_deployment_prerequisites(
        self,
        services: List[str],
        context: DeploymentContext
    ) -> None:
        """Validate deployment prerequisites"""
        
        # Validate namespace exists
        namespace_exists = await self.deployment_manager.namespace_exists(context.namespace)
        if not namespace_exists:
            await self.deployment_manager.create_namespace(context.namespace)
        
        # Validate service specifications
        for service_name in services:
            if service_name not in self.service_templates:
                raise ValueError(f"No template found for service: {service_name}")
        
        # Validate cluster resources
        resource_check = await self.deployment_manager.check_cluster_resources(
            services, context.namespace
        )
        if not resource_check['sufficient']:
            raise Exception(f"Insufficient cluster resources: {resource_check['missing']}")
        
        # Security validation
        security_check = await self.security_scanner.validate_deployment_security(
            services, context
        )
        if not security_check['secure']:
            raise Exception(f"Security validation failed: {security_check['issues']}")

    async def _build_and_push_images(
        self,
        services: List[str],
        context: DeploymentContext
    ) -> Dict[str, Any]:
        """Build and push container images for services"""
        
        image_results = {}
        
        for service_name in services:
            service_spec = self.service_templates[service_name]
            
            # Check if image already exists
            image_exists = await self.image_manager.image_exists(
                service_spec.image, service_spec.version
            )
            
            if not image_exists:
                # Build image
                build_result = await self.image_manager.build_image(
                    service_name,
                    service_spec.image,
                    service_spec.version,
                    context.environment
                )
                
                # Security scan
                scan_result = await self.security_scanner.scan_image(
                    service_spec.image, service_spec.version
                )
                
                if scan_result['critical_vulnerabilities'] > 0:
                    raise Exception(f"Critical vulnerabilities found in {service_name} image")
                
                # Push image
                push_result = await self.image_manager.push_image(
                    service_spec.image, service_spec.version
                )
                
                image_results[service_name] = {
                    'build': build_result,
                    'scan': scan_result,
                    'push': push_result
                }
            else:
                image_results[service_name] = {
                    'message': 'Image already exists, skipping build'
                }
        
        return image_results

    async def _rolling_deployment(
        self,
        services: List[str],
        context: DeploymentContext
    ) -> Dict[str, Any]:
        """Execute rolling deployment strategy"""
        
        results = {}
        
        for service_name in services:
            service_spec = self.service_templates[service_name]
            
            # Create or update deployment
            deployment_result = await self.deployment_manager.create_or_update_deployment(
                service_spec, context.namespace, context
            )
            
            # Create or update service
            service_result = await self.deployment_manager.create_or_update_service(
                service_spec, context.namespace
            )
            
            # Create or update ingress if needed
            ingress_result = None
            if service_spec.service_type in [ServiceType.API_GATEWAY, ServiceType.AI_AGENT]:
                ingress_result = await self.deployment_manager.create_or_update_ingress(
                    service_spec, context.namespace, context.environment
                )
            
            # Wait for rollout to complete
            rollout_status = await self.deployment_manager.wait_for_rollout(
                service_spec.name, context.namespace, timeout=context.timeout
            )
            
            results[service_name] = {
                'deployment': deployment_result,
                'service': service_result,
                'ingress': ingress_result,
                'rollout': rollout_status
            }
        
        return results

    async def _blue_green_deployment(
        self,
        services: List[str],
        context: DeploymentContext
    ) -> Dict[str, Any]:
        """Execute blue-green deployment strategy"""
        
        results = {}
        green_namespace = f"{context.namespace}-green"
        
        # Create green namespace
        await self.deployment_manager.create_namespace(green_namespace)
        
        try:
            # Deploy to green environment
            for service_name in services:
                service_spec = self.service_templates[service_name]
                
                # Deploy to green
                green_deployment = await self.deployment_manager.create_or_update_deployment(
                    service_spec, green_namespace, context
                )
                
                green_service = await self.deployment_manager.create_or_update_service(
                    service_spec, green_namespace
                )
                
                # Wait for green deployment to be ready
                await self.deployment_manager.wait_for_rollout(
                    service_spec.name, green_namespace, timeout=context.timeout
                )
                
                results[service_name] = {
                    'green_deployment': green_deployment,
                    'green_service': green_service
                }
            
            # Validate green environment
            green_health = await self._validate_deployment_health(services, context, green_namespace)
            
            if green_health['healthy']:
                # Switch traffic to green
                for service_name in services:
                    await self.deployment_manager.switch_service_traffic(
                        service_name, context.namespace, green_namespace
                    )
                
                # Clean up blue environment after successful switch
                await asyncio.sleep(300)  # Wait 5 minutes before cleanup
                await self.deployment_manager.delete_namespace(context.namespace)
                await self.deployment_manager.rename_namespace(green_namespace, context.namespace)
                
            else:
                raise Exception(f"Green environment health check failed: {green_health['errors']}")
                
        except Exception as e:
            # Cleanup green environment on failure
            await self.deployment_manager.delete_namespace(green_namespace)
            raise
        
        return results

    async def _canary_deployment(
        self,
        services: List[str],
        context: DeploymentContext
    ) -> Dict[str, Any]:
        """Execute canary deployment strategy"""
        
        results = {}
        canary_percentage = context.context.get('canary_percentage', 10)
        
        for service_name in services:
            service_spec = self.service_templates[service_name]
            
            # Deploy canary version
            canary_spec = service_spec.copy()
            canary_spec.name = f"{service_spec.name}-canary"
            canary_spec.replicas = max(1, int(service_spec.replicas * canary_percentage / 100))
            
            canary_deployment = await self.deployment_manager.create_or_update_deployment(
                canary_spec, context.namespace, context
            )
            
            # Configure traffic splitting
            traffic_split = await self.deployment_manager.configure_traffic_split(
                service_spec.name, context.namespace, canary_percentage
            )
            
            # Monitor canary metrics
            canary_metrics = await self._monitor_canary_metrics(
                service_name, context, duration=300  # 5 minutes
            )
            
            # Analyze canary performance
            canary_analysis = await self._analyze_canary_performance(canary_metrics)
            
            if canary_analysis['successful']:
                # Promote canary to full deployment
                full_deployment = await self.deployment_manager.promote_canary_to_full(
                    service_spec, canary_spec, context.namespace
                )
                
                results[service_name] = {
                    'canary_deployment': canary_deployment,
                    'traffic_split': traffic_split,
                    'metrics': canary_metrics,
                    'analysis': canary_analysis,
                    'promotion': full_deployment
                }
            else:
                # Rollback canary
                await self.deployment_manager.delete_deployment(
                    canary_spec.name, context.namespace
                )
                
                raise Exception(f"Canary analysis failed for {service_name}: {canary_analysis['issues']}")
        
        return results

    async def _recreate_deployment(
        self,
        services: List[str],
        context: DeploymentContext
    ) -> Dict[str, Any]:
        """Execute recreate deployment strategy"""
        
        results = {}
        
        for service_name in services:
            service_spec = self.service_templates[service_name]
            
            # Delete existing deployment
            await self.deployment_manager.delete_deployment(
                service_spec.name, context.namespace
            )
            
            # Wait for termination
            await self.deployment_manager.wait_for_termination(
                service_spec.name, context.namespace
            )
            
            # Create new deployment
            new_deployment = await self.deployment_manager.create_or_update_deployment(
                service_spec, context.namespace, context
            )
            
            # Create or update service
            service_result = await self.deployment_manager.create_or_update_service(
                service_spec, context.namespace
            )
            
            # Wait for rollout
            rollout_status = await self.deployment_manager.wait_for_rollout(
                service_spec.name, context.namespace, timeout=context.timeout
            )
            
            results[service_name] = {
                'deployment': new_deployment,
                'service': service_result,
                'rollout': rollout_status
            }
        
        return results

    async def _validate_deployment_health(
        self,
        services: List[str],
        context: DeploymentContext,
        namespace: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate deployment health across all services"""
        
        target_namespace = namespace or context.namespace
        health_results = {
            'healthy': True,
            'services': {},
            'errors': []
        }
        
        for service_name in services:
            service_spec = self.service_templates[service_name]
            
            # Pod health check
            pod_health = await self.health_checker.check_pod_health(
                service_spec.name, target_namespace
            )
            
            # Service endpoint health check
            endpoint_health = await self.health_checker.check_service_endpoints(
                service_spec.name, target_namespace
            )
            
            # Application health check
            app_health = await self.health_checker.check_application_health(
                service_spec.name, target_namespace, service_spec.health_check
            )
            
            service_healthy = (
                pod_health['healthy'] and
                endpoint_health['healthy'] and
                app_health['healthy']
            )
            
            if not service_healthy:
                health_results['healthy'] = False
                health_results['errors'].extend([
                    *pod_health.get('errors', []),
                    *endpoint_health.get('errors', []),
                    *app_health.get('errors', [])
                ])
            
            health_results['services'][service_name] = {
                'healthy': service_healthy,
                'pods': pod_health,
                'endpoints': endpoint_health,
                'application': app_health
            }
        
        return health_results

    async def _execute_pre_deployment_hooks(self, context: DeploymentContext) -> None:
        """Execute pre-deployment hooks"""
        
        for hook in context.pre_deployment_hooks:
            try:
                await self._execute_hook(hook, context, "pre-deployment")
            except Exception as e:
                self.logger.error(f"Pre-deployment hook failed: {hook}", exc_info=True)
                raise

    async def _execute_post_deployment_hooks(self, context: DeploymentContext) -> None:
        """Execute post-deployment hooks"""
        
        for hook in context.post_deployment_hooks:
            try:
                await self._execute_hook(hook, context, "post-deployment")
            except Exception as e:
                self.logger.error(f"Post-deployment hook failed: {hook}", exc_info=True)
                # Post-deployment hook failures are non-fatal

    async def _execute_hook(self, hook: str, context: DeploymentContext, hook_type: str) -> None:
        """Execute a deployment hook"""
        
        # Hook execution logic would be implemented based on hook type
        # This could include database migrations, cache warming, notifications, etc.
        self.logger.info(f"Executing {hook_type} hook: {hook}")

    async def _monitor_canary_metrics(
        self,
        service_name: str,
        context: DeploymentContext,
        duration: int
    ) -> Dict[str, Any]:
        """Monitor canary deployment metrics"""
        
        # Implement canary metrics collection
        # This would integrate with monitoring systems like Prometheus
        return {
            'error_rate': 0.01,
            'response_time': 150,
            'cpu_usage': 0.6,
            'memory_usage': 0.7,
            'request_rate': 100
        }

    async def _analyze_canary_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze canary deployment performance"""
        
        analysis = {
            'successful': True,
            'issues': []
        }
        
        # Check error rate
        if metrics.get('error_rate', 0) > 0.05:
            analysis['successful'] = False
            analysis['issues'].append(f"High error rate: {metrics['error_rate']}")
        
        # Check response time
        if metrics.get('response_time', 0) > 500:
            analysis['successful'] = False
            analysis['issues'].append(f"High response time: {metrics['response_time']}ms")
        
        # Check resource usage
        if metrics.get('cpu_usage', 0) > 0.9:
            analysis['successful'] = False
            analysis['issues'].append(f"High CPU usage: {metrics['cpu_usage']}")
        
        if metrics.get('memory_usage', 0) > 0.9:
            analysis['successful'] = False
            analysis['issues'].append(f"High memory usage: {metrics['memory_usage']}")
        
        return analysis

    async def _rollback_deployment(self, deployment_id: str, reason: str) -> None:
        """Rollback a failed deployment"""
        
        if deployment_id not in self.active_deployments:
            return
        
        deployment_state = self.active_deployments[deployment_id]
        self.logger.info(f"Rolling back deployment {deployment_id}: {reason}")
        
        try:
            # Get previous revision
            previous_revision = await self.deployment_manager.get_previous_revision(
                deployment_state['services'], deployment_state['context'].namespace
            )
            
            # Rollback each service
            for service_name in deployment_state['services']:
                await self.deployment_manager.rollback_deployment(
                    service_name, deployment_state['context'].namespace, previous_revision
                )
            
            deployment_state['rollback_completed'] = True
            deployment_state['rollback_reason'] = reason
            
        except Exception as e:
            self.logger.error(f"Rollback failed for deployment {deployment_id}", exc_info=True)
            deployment_state['rollback_failed'] = True
            deployment_state['rollback_error'] = str(e)

    async def deploy_service_batch(
        self,
        batch: List[str],
        environment: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy a batch of service instances (for rolling deployments)"""
        
        return await self.deploy_services(batch, environment, context)

    async def deploy_canary_services(
        self,
        services: List[str],
        environment: str,
        canary_percentage: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy canary versions of services"""
        
        context['canary_percentage'] = canary_percentage
        context['strategy'] = 'canary'
        
        return await self.deploy_services(services, environment, context)

    async def promote_canary_to_full(
        self,
        services: List[str],
        environment: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Promote canary deployment to full deployment"""
        
        results = {}
        
        for service_name in services:
            promotion_result = await self.deployment_manager.promote_canary_to_full(
                self.service_templates[service_name],
                None,  # canary_spec will be derived
                context.get('namespace', f"ia-influencer-{environment}")
            )
            
            results[service_name] = promotion_result
        
        return results

    async def stop_services(
        self,
        services: List[str],
        environment: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stop services in the specified environment"""
        
        results = {}
        namespace = context.get('namespace', f"ia-influencer-{environment}")
        
        for service_name in services:
            service_spec = self.service_templates[service_name]
            
            # Scale down to 0 replicas
            scale_result = await self.deployment_manager.scale_deployment(
                service_spec.name, namespace, 0
            )
            
            results[service_name] = scale_result
        
        return results

    async def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status"""
        return self.active_deployments.get(deployment_id)

    async def list_active_deployments(self) -> List[Dict[str, Any]]:
        """List all active deployments"""
        return [
            {
                'deployment_id': deployment_id,
                'environment': state['environment'],
                'services': state['services'],
                'status': state['status'].value,
                'start_time': state['start_time']
            }
            for deployment_id, state in self.active_deployments.items()
        ]

    async def cleanup_completed_deployments(self, max_age_hours: int = 24) -> int:
        """Cleanup old completed deployment states"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        deployments_to_remove = []
        for deployment_id, state in self.active_deployments.items():
            if (state['status'] in [DeploymentStatus.RUNNING, DeploymentStatus.FAILED] and
                state.get('end_time', datetime.utcnow()) < cutoff_time):
                deployments_to_remove.append(deployment_id)
        
        for deployment_id in deployments_to_remove:
            del self.active_deployments[deployment_id]
            cleaned_count += 1
            
        return cleaned_count
