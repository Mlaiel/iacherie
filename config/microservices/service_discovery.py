"""Service Discovery Configuration for IA-Influencer Agent Platform
==============================================================

Professional service discovery configuration management for distributed microservices.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import consul
import etcd3
import redis
from pydantic import BaseSettings, Field, validator


class ServiceDiscoveryType(str, Enum):
    """Service discovery backend types."""    CONSUL = "consul"
    ETCD = "etcd"
    REDIS = "redis"
    KUBERNETES = "kubernetes"
    EUREKA = "eureka"


class HealthCheckType(str, Enum):
    """Health check types for service registration."""    HTTP = "http"
    TCP = "tcp"
    GRPC = "grpc"
    SCRIPT = "script"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""    host: str
    port: int
    protocol: str = "http"
    weight: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthCheckConfig:
    """Health check configuration for services."""    type: HealthCheckType
    endpoint: str
    interval: int = 30  # seconds
    timeout: int = 10   # seconds
    retries: int = 3
    deregister_critical_service_after: int = 300  # seconds


@dataclass
class ServiceRegistration:
    """Service registration configuration."""    service_id: str
    service_name: str
    version: str
    endpoints: List[ServiceEndpoint]
    health_check: HealthCheckConfig
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ServiceDiscoveryConfig(BaseSettings):
    """    Centralized service discovery configuration for microservices architecture.
    Supports multiple backends: Consul, etcd, Redis, Kubernetes.
    """    
    # Service discovery backend
    discovery_type: ServiceDiscoveryType = ServiceDiscoveryType.CONSUL
    
    # Consul configuration
    consul_host: str = Field("localhost", env="CONSUL_HOST")
    consul_port: int = Field(8500, env="CONSUL_PORT")
    consul_token: Optional[str] = Field(None, env="CONSUL_TOKEN")
    consul_datacenter: str = Field("dc1", env="CONSUL_DATACENTER")
    consul_scheme: str = Field("http", env="CONSUL_SCHEME")
    
    # etcd configuration
    etcd_host: str = Field("localhost", env="ETCD_HOST")
    etcd_port: int = Field(2379, env="ETCD_PORT")
    etcd_user: Optional[str] = Field(None, env="ETCD_USER")
    etcd_password: Optional[str] = Field(None, env="ETCD_PASSWORD")
    etcd_ca_cert: Optional[str] = Field(None, env="ETCD_CA_CERT")
    etcd_cert_key: Optional[str] = Field(None, env="ETCD_CERT_KEY")
    etcd_cert_cert: Optional[str] = Field(None, env="ETCD_CERT_CERT")
    
    # Redis configuration
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    redis_db: int = Field(0, env="REDIS_DB")
    
    # Kubernetes configuration
    kubernetes_namespace: str = Field("default", env="KUBERNETES_NAMESPACE")
    kubernetes_config_path: Optional[str] = Field(None, env="KUBECONFIG")
    
    # Service registration settings
    service_name: str = Field("ia-influencer-agent", env="SERVICE_NAME")
    service_version: str = Field("1.0.0", env="SERVICE_VERSION")
    service_host: str = Field("localhost", env="SERVICE_HOST")
    service_port: int = Field(8000, env="SERVICE_PORT")
    service_protocol: str = Field("http", env="SERVICE_PROTOCOL")
    
    # Health check settings
    health_check_enabled: bool = Field(True, env="HEALTH_CHECK_ENABLED")
    health_check_endpoint: str = Field("/health", env="HEALTH_CHECK_ENDPOINT")
    health_check_interval: int = Field(30, env="HEALTH_CHECK_INTERVAL")
    health_check_timeout: int = Field(10, env="HEALTH_CHECK_TIMEOUT")
    health_check_retries: int = Field(3, env="HEALTH_CHECK_RETRIES")
    
    # Service discovery settings
    discovery_refresh_interval: int = Field(60, env="DISCOVERY_REFRESH_INTERVAL")
    service_cache_ttl: int = Field(300, env="SERVICE_CACHE_TTL")
    enable_service_cache: bool = Field(True, env="ENABLE_SERVICE_CACHE")
    
    # Load balancing settings
    load_balancing_strategy: str = Field("round_robin", env="LOAD_BALANCING_STRATEGY")
    max_retries: int = Field(3, env="MAX_RETRIES")
    retry_backoff: float = Field(1.0, env="RETRY_BACKOFF")
    
    class Config:
        env_prefix = "SERVICE_DISCOVERY_"
        case_sensitive = False
        
    @validator("discovery_type")
    def validate_discovery_type(cls, v):
        if v not in ServiceDiscoveryType:
            raise ValueError(f"Invalid discovery type: {v}")
        return v
    
    def get_consul_client(self) -> consul.Consul:
        """Get configured Consul client."""        return consul.Consul(
            host=self.consul_host,
            port=self.consul_port,
            token=self.consul_token,
            dc=self.consul_datacenter,
            scheme=self.consul_scheme
        )
    
    def get_etcd_client(self) -> etcd3.Etcd3Client:
        """Get configured etcd client."""        return etcd3.client(
            host=self.etcd_host,
            port=self.etcd_port,
            user=self.etcd_user,
            password=self.etcd_password,
            ca_cert=self.etcd_ca_cert,
            cert_key=self.etcd_cert_key,
            cert_cert=self.etcd_cert_cert
        )
    
    def get_redis_client(self) -> redis.Redis:
        """Get configured Redis client."""        return redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            password=self.redis_password,
            db=self.redis_db,
            decode_responses=True
        )
    
    def get_service_config(self) -> Dict[str, Any]:
        """Get complete service configuration."""        return {
            "discovery": {
                "type": self.discovery_type,
                "consul": {
                    "host": self.consul_host,
                    "port": self.consul_port,
                    "datacenter": self.consul_datacenter,
                    "scheme": self.consul_scheme
                },
                "etcd": {
                    "host": self.etcd_host,
                    "port": self.etcd_port
                },
                "redis": {
                    "host": self.redis_host,
                    "port": self.redis_port,
                    "db": self.redis_db
                },
                "kubernetes": {
                    "namespace": self.kubernetes_namespace
                }
            },
            "service": {
                "name": self.service_name,
                "version": self.service_version,
                "host": self.service_host,
                "port": self.service_port,
                "protocol": self.service_protocol
            },
            "health_check": {
                "enabled": self.health_check_enabled,
                "endpoint": self.health_check_endpoint,
                "interval": self.health_check_interval,
                "timeout": self.health_check_timeout,
                "retries": self.health_check_retries
            },
            "settings": {
                "refresh_interval": self.discovery_refresh_interval,
                "cache_ttl": self.service_cache_ttl,
                "enable_cache": self.enable_service_cache,
                "load_balancing": self.load_balancing_strategy,
                "max_retries": self.max_retries,
                "retry_backoff": self.retry_backoff
            }
        }


class ServiceRegistry:
    """Service registry for managing service registrations."""    
    def __init__(self, config: ServiceDiscoveryConfig):
        self.config = config
        self._services: Dict[str, List[ServiceRegistration]] = {}
        
    def register_service(self, registration: ServiceRegistration):
        """Register a service."""        if registration.service_name not in self._services:
            self._services[registration.service_name] = []
        self._services[registration.service_name].append(registration)
    
    def deregister_service(self, service_name: str, service_id: str):
        """Deregister a service."""        if service_name in self._services:
            self._services[service_name] = [
                s for s in self._services[service_name] 
                if s.service_id != service_id
            ]
    
    def get_service_instances(self, service_name: str) -> List[ServiceRegistration]:
        """Get all instances of a service."""        return self._services.get(service_name, [])
    
    def get_healthy_instances(self, service_name: str) -> List[ServiceRegistration]:
        """Get healthy instances of a service."""        # Implementation would include health checking logic
        return self.get_service_instances(service_name)


# Pre-configured service registrations for IA-Influencer Agent microservices
MICROSERVICE_REGISTRATIONS = {
    "api-gateway": ServiceRegistration(
        service_id="api-gateway-1",
        service_name="api-gateway",
        version="1.0.0",
        endpoints=[ServiceEndpoint("localhost", 8000)],
        health_check=HealthCheckConfig(
            type=HealthCheckType.HTTP,
            endpoint="/health"
        ),
        tags=["gateway", "api", "authentication"]
    ),
    "spotify-agent": ServiceRegistration(
        service_id="spotify-agent-1",
        service_name="spotify-agent",
        version="1.0.0",
        endpoints=[ServiceEndpoint("localhost", 8001)],
        health_check=HealthCheckConfig(
            type=HealthCheckType.HTTP,
            endpoint="/health"
        ),
        tags=["ai", "spotify", "analytics", "recommendations"]
    ),
    "content-protection": ServiceRegistration(
        service_id="content-protection-1",
        service_name="content-protection",
        version="1.0.0",
        endpoints=[ServiceEndpoint("localhost", 8002)],
        health_check=HealthCheckConfig(
            type=HealthCheckType.HTTP,
            endpoint="/health"
        ),
        tags=["protection", "fingerprinting", "ai", "monitoring"]
    ),
    "fingerprinting-engine": ServiceRegistration(
        service_id="fingerprinting-engine-1",
        service_name="fingerprinting-engine",
        version="1.0.0",
        endpoints=[ServiceEndpoint("localhost", 8003)],
        health_check=HealthCheckConfig(
            type=HealthCheckType.HTTP,
            endpoint="/health"
        ),
        tags=["fingerprinting", "ai", "audio", "video", "image"]
    ),
    "web-crawler": ServiceRegistration(
        service_id="web-crawler-1",
        service_name="web-crawler",
        version="1.0.0",
        endpoints=[ServiceEndpoint("localhost", 8004)],
        health_check=HealthCheckConfig(
            type=HealthCheckType.HTTP,
            endpoint="/health"
        ),
        tags=["crawler", "monitoring", "surveillance", "scraping"]
    ),
    "monetization-engine": ServiceRegistration(
        service_id="monetization-engine-1",
        service_name="monetization-engine",
        version="1.0.0",
        endpoints=[ServiceEndpoint("localhost", 8005)],
        health_check=HealthCheckConfig(
            type=HealthCheckType.HTTP,
            endpoint="/health"
        ),
        tags=["monetization", "revenue", "payments", "licensing"]
    ),
    "notification-service": ServiceRegistration(
        service_id="notification-service-1",
        service_name="notification-service",
        version="1.0.0",
        endpoints=[ServiceEndpoint("localhost", 8006)],
        health_check=HealthCheckConfig(
            type=HealthCheckType.HTTP,
            endpoint="/health"
        ),
        tags=["notifications", "alerts", "messaging", "websocket"]
    ),
    "analytics-engine": ServiceRegistration(
        service_id="analytics-engine-1",
        service_name="analytics-engine",
        version="1.0.0",
        endpoints=[ServiceEndpoint("localhost", 8007)],
        health_check=HealthCheckConfig(
            type=HealthCheckType.HTTP,
            endpoint="/health"
        ),
        tags=["analytics", "ml", "insights", "reporting"]
    )
}


# Export configuration instance
service_discovery_config = ServiceDiscoveryConfig()
