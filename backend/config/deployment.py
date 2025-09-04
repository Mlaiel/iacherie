"""Deployment Configuration Module - Consolidated Deployment Configs
==================================================================

Consolidates all deployment-related configurations from:
- config/deployment/ (31 files)
- config/environments/ (8 files)

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum

# ===== ENVIRONMENT CONFIGURATION =====

class Environment(str, Enum):
    """Deployment environments"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class DeploymentStrategy(str, Enum):
    """Deployment strategies"""
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    RECREATE = "recreate"

@dataclass
class EnvironmentConfig:
    """Environment configuration"""
    name: Environment
    description: str = ""
    debug: bool = False
    log_level: str = "INFO"
    allowed_hosts: List[str] = field(default_factory=lambda: ["*"])
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    secret_key: Optional[str] = None
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    custom_settings: Dict[str, Any] = field(default_factory=dict)

# ===== DOCKER CONFIGURATION =====

@dataclass
class DockerConfig:
    """Docker configuration"""
    enabled: bool = True
    registry: str = "docker.io"
    namespace: str = "ia-influencer"
    image_name: str = "ia-influencer-agent"
    tag: str = "latest"
    build_args: Dict[str, str] = field(default_factory=dict)
    ports: List[str] = field(default_factory=lambda: ["8000:8000"])
    volumes: List[str] = field(default_factory=list)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    health_check: bool = True
    restart_policy: str = "unless-stopped"

# ===== KUBERNETES CONFIGURATION =====

@dataclass
class KubernetesResourceLimits:
    """Kubernetes resource limits"""
    cpu: str = "500m"
    memory: str = "512Mi"

@dataclass
class KubernetesResourceRequests:
    """Kubernetes resource requests"""
    cpu: str = "100m"
    memory: str = "128Mi"

@dataclass
class KubernetesConfig:
    """Kubernetes configuration"""
    enabled: bool = False
    namespace: str = "ia-influencer"
    replicas: int = 3
    deployment_strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    service_type: str = "ClusterIP"
    service_port: int = 80
    target_port: int = 8000
    ingress_enabled: bool = True
    ingress_host: str = "api.ia-influencer.com"
    ingress_tls: bool = True
    resource_limits: KubernetesResourceLimits = field(default_factory=KubernetesResourceLimits)
    resource_requests: KubernetesResourceRequests = field(default_factory=KubernetesResourceRequests)
    horizontal_pod_autoscaler: bool = True
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_utilization: int = 70

# ===== CI/CD CONFIGURATION =====

class CIPlatform(str, Enum):
    """CI/CD platforms"""
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    JENKINS = "jenkins"
    AZURE_DEVOPS = "azure_devops"
    CIRCLECI = "circleci"
    TRAVIS_CI = "travis_ci"

@dataclass
class CICDConfig:
    """CI/CD configuration"""
    platform: CIPlatform = CIPlatform.GITHUB_ACTIONS
    enabled: bool = True
    build_on_push: bool = True
    build_on_pr: bool = True
    auto_deploy_staging: bool = True
    auto_deploy_production: bool = False
    run_tests: bool = True
    run_security_scan: bool = True
    run_quality_gate: bool = True
    artifacts_retention_days: int = 30
    notification_channels: List[str] = field(default_factory=list)

# ===== LOAD BALANCER CONFIGURATION =====

class LoadBalancerType(str, Enum):
    """Load balancer types"""
    NGINX = "nginx"
    HAPROXY = "haproxy"
    TRAEFIK = "traefik"
    AWS_ALB = "aws_alb"
    CLOUDFLARE = "cloudflare"

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""
    type: LoadBalancerType = LoadBalancerType.NGINX
    enabled: bool = True
    algorithm: str = "round_robin"  # round_robin, least_conn, ip_hash
    health_check_path: str = "/health"
    health_check_interval: int = 30
    health_check_timeout: int = 5
    ssl_enabled: bool = True
    ssl_redirect: bool = True
    rate_limiting: bool = True
    rate_limit_rpm: int = 1000

# ===== DATABASE DEPLOYMENT =====

@dataclass
class DatabaseDeploymentConfig:
    """Database deployment configuration"""
    type: str = "postgresql"  # postgresql, mysql, mongodb
    version: str = "14"
    high_availability: bool = False
    replication_enabled: bool = False
    backup_enabled: bool = True
    backup_schedule: str = "0 2 * * *"  # Daily at 2 AM
    monitoring_enabled: bool = True
    persistent_storage: bool = True
    storage_size: str = "10Gi"
    connection_pooling: bool = True
    max_connections: int = 100

# ===== CACHE DEPLOYMENT =====

@dataclass
class CacheDeploymentConfig:
    """Cache deployment configuration"""
    type: str = "redis"  # redis, memcached
    version: str = "7"
    cluster_enabled: bool = False
    persistence_enabled: bool = True
    memory_limit: str = "1Gi"
    eviction_policy: str = "allkeys-lru"
    monitoring_enabled: bool = True
    sentinel_enabled: bool = False
    backup_enabled: bool = False

# ===== SECURITY DEPLOYMENT =====

@dataclass
class SecurityDeploymentConfig:
    """Security deployment configuration"""
    network_policies_enabled: bool = True
    pod_security_policies_enabled: bool = True
    rbac_enabled: bool = True
    secrets_encryption: bool = True
    vulnerability_scanning: bool = True
    compliance_scanning: bool = True
    mtls_enabled: bool = False
    service_mesh_enabled: bool = False

# ===== MONITORING DEPLOYMENT =====

@dataclass
class MonitoringDeploymentConfig:
    """Monitoring deployment configuration"""
    prometheus_enabled: bool = True
    grafana_enabled: bool = True
    alertmanager_enabled: bool = True
    jaeger_enabled: bool = False
    elk_stack_enabled: bool = False
    log_aggregation: bool = True
    metrics_retention_days: int = 30
    log_retention_days: int = 7

# ===== SCALING CONFIGURATION =====

@dataclass
class AutoScalingConfig:
    """Auto-scaling configuration"""
    enabled: bool = True
    min_instances: int = 2
    max_instances: int = 10
    target_cpu_utilization: int = 70
    target_memory_utilization: int = 80
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 300  # seconds
    custom_metrics: List[str] = field(default_factory=list)

# ===== MAIN DEPLOYMENT CONFIGURATION =====

@dataclass
class DeploymentConfig:
    """Main deployment configuration"""
    environment: EnvironmentConfig
    docker: DockerConfig = field(default_factory=DockerConfig)
    kubernetes: KubernetesConfig = field(default_factory=KubernetesConfig)
    cicd: CICDConfig = field(default_factory=CICDConfig)
    load_balancer: LoadBalancerConfig = field(default_factory=LoadBalancerConfig)
    database: DatabaseDeploymentConfig = field(default_factory=DatabaseDeploymentConfig)
    cache: CacheDeploymentConfig = field(default_factory=CacheDeploymentConfig)
    security: SecurityDeploymentConfig = field(default_factory=SecurityDeploymentConfig)
    monitoring: MonitoringDeploymentConfig = field(default_factory=MonitoringDeploymentConfig)
    auto_scaling: AutoScalingConfig = field(default_factory=AutoScalingConfig)
    deployment_timeout: int = 600  # 10 minutes
    rollback_enabled: bool = True

# ===== ENVIRONMENT-SPECIFIC CONFIGURATIONS =====

def get_development_deployment_config() -> DeploymentConfig:
    """Get development deployment configuration"""
    return DeploymentConfig(
        environment=EnvironmentConfig(
            name=Environment.DEVELOPMENT,
            debug=True,
            log_level="DEBUG",
            allowed_hosts=["localhost", "127.0.0.1", "0.0.0.0"]
        ),
        docker=DockerConfig(
            tag="dev",
            health_check=False
        ),
        kubernetes=KubernetesConfig(
            enabled=False
        ),
        cicd=CICDConfig(
            auto_deploy_staging=False,
            auto_deploy_production=False
        ),
        database=DatabaseDeploymentConfig(
            high_availability=False,
            backup_enabled=False,
            storage_size="1Gi"
        ),
        cache=CacheDeploymentConfig(
            cluster_enabled=False,
            persistence_enabled=False
        ),
        auto_scaling=AutoScalingConfig(
            enabled=False
        )
    )

def get_production_deployment_config() -> DeploymentConfig:
    """Get production deployment configuration"""
    return DeploymentConfig(
        environment=EnvironmentConfig(
            name=Environment.PRODUCTION,
            debug=False,
            log_level="INFO",
            allowed_hosts=["api.ia-influencer.com", "www.ia-influencer.com"]
        ),
        docker=DockerConfig(
            tag="latest",
            registry="your-registry.com"
        ),
        kubernetes=KubernetesConfig(
            enabled=True,
            replicas=5,
            deployment_strategy=DeploymentStrategy.BLUE_GREEN,
            ingress_host="api.ia-influencer.com"
        ),
        cicd=CICDConfig(
            auto_deploy_production=False,  # Manual approval required
            run_security_scan=True
        ),
        database=DatabaseDeploymentConfig(
            high_availability=True,
            replication_enabled=True,
            storage_size="100Gi"
        ),
        cache=CacheDeploymentConfig(
            cluster_enabled=True,
            sentinel_enabled=True
        ),
        security=SecurityDeploymentConfig(
            network_policies_enabled=True,
            vulnerability_scanning=True,
            compliance_scanning=True
        ),
        auto_scaling=AutoScalingConfig(
            enabled=True,
            min_instances=3,
            max_instances=20
        )
    )

def get_testing_deployment_config() -> DeploymentConfig:
    """Get testing deployment configuration"""
    return DeploymentConfig(
        environment=EnvironmentConfig(
            name=Environment.TESTING,
            debug=False,
            log_level="WARNING"
        ),
        docker=DockerConfig(
            tag="test",
            health_check=False
        ),
        kubernetes=KubernetesConfig(
            enabled=False
        ),
        cicd=CICDConfig(
            auto_deploy_staging=False,
            auto_deploy_production=False,
            notification_channels=[]
        ),
        database=DatabaseDeploymentConfig(
            backup_enabled=False,
            storage_size="1Gi"
        ),
        cache=CacheDeploymentConfig(
            persistence_enabled=False
        ),
        auto_scaling=AutoScalingConfig(
            enabled=False
        )
    )

# ===== DEPLOYMENT CONFIGURATION FACTORY =====

class DeploymentConfigurationFactory:
    """Factory for creating deployment configurations"""
    
    @staticmethod
    def create_config(environment: str = "development") -> DeploymentConfig:
        """Create deployment configuration for environment"""
        if environment.lower() == "production":
            return get_production_deployment_config()
        elif environment.lower() == "testing":
            return get_testing_deployment_config()
        else:
            return get_development_deployment_config()

# Export all deployment configurations
__all__ = [
    # Enums
    "Environment",
    "DeploymentStrategy",
    "CIPlatform",
    "LoadBalancerType",
    
    # Configuration Classes
    "EnvironmentConfig",
    "DockerConfig",
    "KubernetesResourceLimits",
    "KubernetesResourceRequests",
    "KubernetesConfig",
    "CICDConfig",
    "LoadBalancerConfig",
    "DatabaseDeploymentConfig",
    "CacheDeploymentConfig",
    "SecurityDeploymentConfig",
    "MonitoringDeploymentConfig",
    "AutoScalingConfig",
    "DeploymentConfig",
    
    # Factory and Functions
    "DeploymentConfigurationFactory",
    "get_development_deployment_config",
    "get_production_deployment_config",
    "get_testing_deployment_config"
]