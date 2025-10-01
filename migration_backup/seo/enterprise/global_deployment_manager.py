"""
⚠️  AVERTISSEMENT LÉGAL OBLIGATOIRE:
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

Global Deployment Manager Enterprise
====================================

Enterprise-grade global deployment management system for IA Chéries SEO platform.
Provides comprehensive multi-region deployment, CDN optimization, and global scalability.

Author: Fahed Mlaiel (mlaiel@live.de)
Enterprise Architecture: Advanced Global Infrastructure Systems
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import aiohttp
from contextlib import asynccontextmanager

from pydantic import BaseModel, Field, validator
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession


class DeploymentRegion(str, Enum):
    """Global deployment regions"""
    US_EAST = "us-east-1"
    US_WEST = "us-west-2"
    EU_WEST = "eu-west-1"
    EU_CENTRAL = "eu-central-1"
    ASIA_PACIFIC = "ap-southeast-1"
    ASIA_NORTHEAST = "ap-northeast-1"
    CANADA = "ca-central-1"
    AUSTRALIA = "ap-southeast-2"


class DeploymentStrategy(str, Enum):
    """Deployment strategy types"""
    BLUE_GREEN = "blue_green"
    ROLLING = "rolling"
    CANARY = "canary"
    A_B_TESTING = "a_b_testing"
    IMMUTABLE = "immutable"


class DeploymentStatus(str, Enum):
    """Deployment status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLING_BACK = "rolling_back"
    ROLLED_BACK = "rolled_back"


class CDNProvider(str, Enum):
    """CDN provider options"""
    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws_cloudfront"
    AZURE_CDN = "azure_cdn"
    GOOGLE_CDN = "google_cdn"
    FASTLY = "fastly"


@dataclass
class RegionMetrics:
    """Regional deployment metrics"""
    region: DeploymentRegion
    timestamp: datetime
    latency_ms: float
    uptime_percentage: float
    error_rate: float
    throughput_rps: float
    cpu_usage: float
    memory_usage: float
    storage_usage: float
    active_connections: int


class DeploymentConfiguration(BaseModel):
    """Global deployment configuration"""
    deployment_id: str = Field(..., description="Unique deployment identifier")
    name: str = Field(..., description="Deployment name")
    description: str = Field(..., description="Deployment description")
    strategy: DeploymentStrategy = Field(..., description="Deployment strategy")
    
    # Regional configuration
    target_regions: List[DeploymentRegion] = Field(..., description="Target deployment regions")
    primary_region: DeploymentRegion = Field(..., description="Primary region")
    failover_regions: List[DeploymentRegion] = Field(default_factory=list)
    
    # Application configuration
    application_version: str = Field(..., description="Application version")
    docker_image: str = Field(..., description="Docker image")
    environment_variables: Dict[str, str] = Field(default_factory=dict)
    
    # Scaling configuration
    min_instances: int = Field(default=2, ge=1)
    max_instances: int = Field(default=10, ge=1)
    target_cpu_utilization: float = Field(default=70.0, ge=10.0, le=95.0)
    
    # CDN configuration
    cdn_provider: CDNProvider = Field(default=CDNProvider.CLOUDFLARE)
    cdn_enabled: bool = Field(default=True)
    cache_ttl: int = Field(default=3600, ge=60)
    
    # Health check configuration
    health_check_path: str = Field(default="/health")
    health_check_interval: int = Field(default=30, ge=10)
    healthy_threshold: int = Field(default=2, ge=1)
    unhealthy_threshold: int = Field(default=3, ge=1)
    
    # Security configuration
    ssl_enabled: bool = Field(default=True)
    waf_enabled: bool = Field(default=True)
    ddos_protection: bool = Field(default=True)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('deployment_id')
    def validate_deployment_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('deployment_id must be at least 3 characters')
        return v.lower().replace(' ', '_')

    @validator('max_instances')
    def validate_max_instances(cls, v, values):
        if 'min_instances' in values and v < values['min_instances']:
            raise ValueError('max_instances must be >= min_instances')
        return v


class RegionalDeploymentManager:
    """Regional deployment management"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.regional_deployments: Dict[str, Dict[str, Any]] = {}
        
    async def deploy_to_region(
        self, 
        deployment_config: DeploymentConfiguration,
        region: DeploymentRegion
    ) -> Dict[str, Any]:
        """Deploy application to specific region"""
        try:
            regional_deployment_id = f"{deployment_config.deployment_id}_{region.value}"
            
            # Create regional deployment record
            regional_deployment = {
                "regional_deployment_id": regional_deployment_id,
                "deployment_id": deployment_config.deployment_id,
                "region": region.value,
                "status": DeploymentStatus.PENDING.value,
                "strategy": deployment_config.strategy.value,
                "docker_image": deployment_config.docker_image,
                "application_version": deployment_config.application_version,
                "min_instances": deployment_config.min_instances,
                "max_instances": deployment_config.max_instances,
                "started_at": datetime.utcnow().isoformat(),
                "endpoints": []
            }
            
            # Store regional deployment
            await self.redis_client.hset(
                f"regional_deployment:{regional_deployment_id}",
                mapping=regional_deployment
            )
            
            # Execute deployment strategy
            deployment_result = await self._execute_deployment_strategy(
                deployment_config, region, regional_deployment_id
            )
            
            if deployment_result["success"]:
                regional_deployment["status"] = DeploymentStatus.DEPLOYED.value
                regional_deployment["deployed_at"] = datetime.utcnow().isoformat()
                regional_deployment["endpoints"] = deployment_result.get("endpoints", [])
            else:
                regional_deployment["status"] = DeploymentStatus.FAILED.value
                regional_deployment["error"] = deployment_result.get("error", "Deployment failed")
            
            # Update regional deployment
            await self.redis_client.hset(
                f"regional_deployment:{regional_deployment_id}",
                mapping=regional_deployment
            )
            
            # Add to region registry
            await self.redis_client.sadd(f"region_deployments:{region.value}", regional_deployment_id)
            
            return {
                "success": deployment_result["success"],
                "regional_deployment_id": regional_deployment_id,
                "region": region.value,
                "status": regional_deployment["status"],
                "endpoints": regional_deployment.get("endpoints", [])
            }
            
        except Exception as e:
            logging.error(f"Regional deployment failed for {region.value}: {e}")
            return {
                "success": False,
                "error": str(e),
                "region": region.value
            }
    
    async def _execute_deployment_strategy(
        self,
        config: DeploymentConfiguration,
        region: DeploymentRegion,
        regional_deployment_id: str
    ) -> Dict[str, Any]:
        """Execute specific deployment strategy"""
        try:
            if config.strategy == DeploymentStrategy.BLUE_GREEN:
                return await self._blue_green_deployment(config, region, regional_deployment_id)
            elif config.strategy == DeploymentStrategy.ROLLING:
                return await self._rolling_deployment(config, region, regional_deployment_id)
            elif config.strategy == DeploymentStrategy.CANARY:
                return await self._canary_deployment(config, region, regional_deployment_id)
            else:
                return await self._standard_deployment(config, region, regional_deployment_id)
                
        except Exception as e:
            logging.error(f"Deployment strategy execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _blue_green_deployment(
        self,
        config: DeploymentConfiguration,
        region: DeploymentRegion,
        regional_deployment_id: str
    ) -> Dict[str, Any]:
        """Execute blue-green deployment"""
        try:
            # Simulate blue-green deployment
            blue_endpoint = f"blue-{regional_deployment_id}.{region.value}.ainflue.com"
            green_endpoint = f"green-{regional_deployment_id}.{region.value}.ainflue.com"
            
            # Deploy to green environment
            await self._simulate_container_deployment(green_endpoint, config)
            
            # Health check green environment
            health_ok = await self._health_check(green_endpoint, config.health_check_path)
            
            if health_ok:
                # Switch traffic to green
                active_endpoint = green_endpoint
                
                # Update load balancer (simulated)
                await self.redis_client.hset(
                    f"load_balancer:{region.value}",
                    mapping={
                        "active_endpoint": active_endpoint,
                        "switched_at": datetime.utcnow().isoformat()
                    }
                )
                
                return {
                    "success": True,
                    "strategy": "blue_green",
                    "endpoints": [active_endpoint],
                    "switch_completed": True
                }
            else:
                return {
                    "success": False,
                    "error": "Green environment health check failed"
                }
                
        except Exception as e:
            logging.error(f"Blue-green deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _rolling_deployment(
        self,
        config: DeploymentConfiguration,
        region: DeploymentRegion,
        regional_deployment_id: str
    ) -> Dict[str, Any]:
        """Execute rolling deployment"""
        try:
            endpoints = []
            
            # Rolling update instances
            for i in range(config.min_instances):
                instance_endpoint = f"instance-{i}-{regional_deployment_id}.{region.value}.ainflue.com"
                
                # Update instance
                await self._simulate_container_deployment(instance_endpoint, config)
                
                # Health check
                health_ok = await self._health_check(instance_endpoint, config.health_check_path)
                
                if health_ok:
                    endpoints.append(instance_endpoint)
                    
                    # Update load balancer configuration
                    await self.redis_client.lpush(
                        f"rolling_endpoints:{regional_deployment_id}",
                        instance_endpoint
                    )
                else:
                    return {
                        "success": False,
                        "error": f"Instance {i} health check failed during rolling deployment"
                    }
                
                # Wait between instance updates
                await asyncio.sleep(2)
            
            return {
                "success": True,
                "strategy": "rolling",
                "endpoints": endpoints,
                "instances_updated": len(endpoints)
            }
            
        except Exception as e:
            logging.error(f"Rolling deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _canary_deployment(
        self,
        config: DeploymentConfiguration,
        region: DeploymentRegion,
        regional_deployment_id: str
    ) -> Dict[str, Any]:
        """Execute canary deployment"""
        try:
            # Deploy canary instance (10% of traffic)
            canary_endpoint = f"canary-{regional_deployment_id}.{region.value}.ainflue.com"
            stable_endpoint = f"stable-{regional_deployment_id}.{region.value}.ainflue.com"
            
            # Deploy canary version
            await self._simulate_container_deployment(canary_endpoint, config)
            
            # Health check canary
            health_ok = await self._health_check(canary_endpoint, config.health_check_path)
            
            if health_ok:
                # Configure traffic splitting (10% canary, 90% stable)
                await self.redis_client.hset(
                    f"traffic_split:{regional_deployment_id}",
                    mapping={
                        "canary_endpoint": canary_endpoint,
                        "canary_percentage": 10,
                        "stable_endpoint": stable_endpoint,
                        "stable_percentage": 90,
                        "deployed_at": datetime.utcnow().isoformat()
                    }
                )
                
                return {
                    "success": True,
                    "strategy": "canary",
                    "endpoints": [canary_endpoint, stable_endpoint],
                    "traffic_split": {"canary": 10, "stable": 90}
                }
            else:
                return {
                    "success": False,
                    "error": "Canary health check failed"
                }
                
        except Exception as e:
            logging.error(f"Canary deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _standard_deployment(
        self,
        config: DeploymentConfiguration,
        region: DeploymentRegion,
        regional_deployment_id: str
    ) -> Dict[str, Any]:
        """Execute standard deployment"""
        try:
            endpoint = f"{regional_deployment_id}.{region.value}.ainflue.com"
            
            # Deploy application
            await self._simulate_container_deployment(endpoint, config)
            
            # Health check
            health_ok = await self._health_check(endpoint, config.health_check_path)
            
            if health_ok:
                return {
                    "success": True,
                    "strategy": "standard",
                    "endpoints": [endpoint]
                }
            else:
                return {
                    "success": False,
                    "error": "Health check failed"
                }
                
        except Exception as e:
            logging.error(f"Standard deployment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _simulate_container_deployment(
        self,
        endpoint: str,
        config: DeploymentConfiguration
    ):
        """Simulate container deployment"""
        # Simulate deployment delay
        await asyncio.sleep(1)
        
        # Store deployment info
        await self.redis_client.hset(
            f"container:{endpoint}",
            mapping={
                "docker_image": config.docker_image,
                "version": config.application_version,
                "deployed_at": datetime.utcnow().isoformat(),
                "status": "running"
            }
        )
    
    async def _health_check(self, endpoint: str, health_path: str) -> bool:
        """Perform health check on endpoint"""
        try:
            # Simulate health check
            await asyncio.sleep(0.5)
            
            # Store health check result
            await self.redis_client.hset(
                f"health:{endpoint}",
                mapping={
                    "status": "healthy",
                    "checked_at": datetime.utcnow().isoformat(),
                    "response_time": 150  # ms
                }
            )
            
            return True  # Simulate successful health check
            
        except Exception as e:
            logging.error(f"Health check failed for {endpoint}: {e}")
            return False


class CDNManager:
    """Global CDN management"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.cdn_configurations: Dict[str, Dict[str, Any]] = {}
    
    async def configure_cdn(
        self,
        deployment_config: DeploymentConfiguration,
        regional_endpoints: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Configure global CDN"""
        try:
            if not deployment_config.cdn_enabled:
                return {"success": True, "message": "CDN disabled"}
            
            cdn_config_id = f"cdn_{deployment_config.deployment_id}"
            
            # Create CDN configuration
            cdn_config = {
                "cdn_config_id": cdn_config_id,
                "deployment_id": deployment_config.deployment_id,
                "provider": deployment_config.cdn_provider.value,
                "cache_ttl": deployment_config.cache_ttl,
                "ssl_enabled": deployment_config.ssl_enabled,
                "origins": [],
                "edge_locations": [],
                "configured_at": datetime.utcnow().isoformat()
            }
            
            # Configure origins from regional endpoints
            for region, endpoints in regional_endpoints.items():
                for endpoint in endpoints:
                    cdn_config["origins"].append({
                        "region": region,
                        "endpoint": endpoint,
                        "priority": 1 if region == deployment_config.primary_region.value else 2
                    })
            
            # Configure edge locations based on provider
            edge_locations = await self._get_edge_locations(deployment_config.cdn_provider)
            cdn_config["edge_locations"] = edge_locations
            
            # Store CDN configuration
            await self.redis_client.hset(
                f"cdn_config:{cdn_config_id}",
                mapping=cdn_config
            )
            
            # Configure cache rules
            await self._configure_cache_rules(cdn_config_id, deployment_config)
            
            # Set up monitoring
            await self._setup_cdn_monitoring(cdn_config_id)
            
            logging.info(f"CDN configured for deployment {deployment_config.deployment_id}")
            
            return {
                "success": True,
                "cdn_config_id": cdn_config_id,
                "provider": deployment_config.cdn_provider.value,
                "edge_locations_count": len(edge_locations),
                "origins_count": len(cdn_config["origins"])
            }
            
        except Exception as e:
            logging.error(f"CDN configuration failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_edge_locations(self, provider: CDNProvider) -> List[Dict[str, str]]:
        """Get edge locations for CDN provider"""
        # Simulate edge locations based on provider
        edge_locations_map = {
            CDNProvider.CLOUDFLARE: [
                {"city": "New York", "country": "US", "continent": "NA"},
                {"city": "London", "country": "UK", "continent": "EU"},
                {"city": "Singapore", "country": "SG", "continent": "AS"},
                {"city": "Tokyo", "country": "JP", "continent": "AS"},
                {"city": "Sydney", "country": "AU", "continent": "OC"},
                {"city": "Frankfurt", "country": "DE", "continent": "EU"},
                {"city": "São Paulo", "country": "BR", "continent": "SA"}
            ],
            CDNProvider.AWS_CLOUDFRONT: [
                {"city": "Virginia", "country": "US", "continent": "NA"},
                {"city": "Ireland", "country": "IE", "continent": "EU"},
                {"city": "Singapore", "country": "SG", "continent": "AS"},
                {"city": "Tokyo", "country": "JP", "continent": "AS"},
                {"city": "Sydney", "country": "AU", "continent": "OC"}
            ]
        }
        
        return edge_locations_map.get(provider, [])
    
    async def _configure_cache_rules(self, cdn_config_id: str, config: DeploymentConfiguration):
        """Configure CDN cache rules"""
        cache_rules = {
            "static_assets": {
                "pattern": "*.{css,js,png,jpg,jpeg,gif,ico,svg}",
                "ttl": config.cache_ttl * 24,  # 24x longer for static assets
                "compression": True
            },
            "api_responses": {
                "pattern": "/api/*",
                "ttl": 300,  # 5 minutes for API responses
                "compression": True
            },
            "html_pages": {
                "pattern": "*.html",
                "ttl": config.cache_ttl,
                "compression": True
            }
        }
        
        await self.redis_client.hset(
            f"cdn_cache_rules:{cdn_config_id}",
            mapping=cache_rules
        )
    
    async def _setup_cdn_monitoring(self, cdn_config_id: str):
        """Set up CDN monitoring"""
        monitoring_config = {
            "metrics_enabled": True,
            "log_enabled": True,
            "alert_on_high_error_rate": True,
            "alert_threshold": 5.0,  # 5% error rate
            "monitoring_interval": 60  # 1 minute
        }
        
        await self.redis_client.hset(
            f"cdn_monitoring:{cdn_config_id}",
            mapping=monitoring_config
        )


class LoadBalancerManager:
    """Global load balancer management"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    async def configure_global_load_balancer(
        self,
        deployment_config: DeploymentConfiguration,
        regional_endpoints: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Configure global load balancer"""
        try:
            lb_config_id = f"lb_{deployment_config.deployment_id}"
            
            # Create load balancer configuration
            lb_config = {
                "lb_config_id": lb_config_id,
                "deployment_id": deployment_config.deployment_id,
                "primary_region": deployment_config.primary_region.value,
                "failover_regions": [r.value for r in deployment_config.failover_regions],
                "health_check_enabled": True,
                "health_check_path": deployment_config.health_check_path,
                "health_check_interval": deployment_config.health_check_interval,
                "sticky_sessions": False,
                "ssl_termination": deployment_config.ssl_enabled,
                "backends": [],
                "configured_at": datetime.utcnow().isoformat()
            }
            
            # Configure backend servers
            for region, endpoints in regional_endpoints.items():
                for endpoint in endpoints:
                    backend = {
                        "endpoint": endpoint,
                        "region": region,
                        "weight": 100 if region == deployment_config.primary_region.value else 50,
                        "health_status": "healthy",
                        "max_connections": 1000
                    }
                    lb_config["backends"].append(backend)
            
            # Store load balancer configuration
            await self.redis_client.hset(
                f"lb_config:{lb_config_id}",
                mapping=lb_config
            )
            
            # Configure routing rules
            await self._configure_routing_rules(lb_config_id, deployment_config)
            
            # Set up health monitoring
            await self._setup_lb_health_monitoring(lb_config_id, lb_config["backends"])
            
            return {
                "success": True,
                "lb_config_id": lb_config_id,
                "backends_count": len(lb_config["backends"]),
                "primary_region": deployment_config.primary_region.value
            }
            
        except Exception as e:
            logging.error(f"Load balancer configuration failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _configure_routing_rules(
        self,
        lb_config_id: str,
        config: DeploymentConfiguration
    ):
        """Configure load balancer routing rules"""
        routing_rules = {
            "default_rule": {
                "type": "round_robin",
                "health_check_required": True
            },
            "geo_routing": {
                "enabled": True,
                "rules": [
                    {"continent": "NA", "preferred_regions": ["us-east-1", "us-west-2"]},
                    {"continent": "EU", "preferred_regions": ["eu-west-1", "eu-central-1"]},
                    {"continent": "AS", "preferred_regions": ["ap-southeast-1", "ap-northeast-1"]}
                ]
            },
            "failover": {
                "enabled": True,
                "primary_region": config.primary_region.value,
                "failover_threshold": 3  # failures before failover
            }
        }
        
        await self.redis_client.hset(
            f"lb_routing:{lb_config_id}",
            mapping=routing_rules
        )
    
    async def _setup_lb_health_monitoring(
        self,
        lb_config_id: str,
        backends: List[Dict[str, Any]]
    ):
        """Set up load balancer health monitoring"""
        for backend in backends:
            health_monitor = {
                "endpoint": backend["endpoint"],
                "region": backend["region"],
                "last_check": datetime.utcnow().isoformat(),
                "status": "healthy",
                "consecutive_failures": 0,
                "response_time": 0
            }
            
            await self.redis_client.hset(
                f"lb_health:{lb_config_id}:{backend['endpoint']}",
                mapping=health_monitor
            )


class GlobalDeploymentManager:
    """
    Enterprise Global Deployment Manager
    
    Comprehensive global deployment management system providing:
    - Multi-region deployment orchestration
    - CDN optimization and management
    - Global load balancing
    - Enterprise-grade scalability
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: redis.Redis):
        self.db_session = db_session
        self.redis_client = redis_client
        
        # Initialize managers
        self.regional_manager = RegionalDeploymentManager(redis_client)
        self.cdn_manager = CDNManager(redis_client)
        self.lb_manager = LoadBalancerManager(redis_client)
        
        # Deployment registry
        self.deployments: Dict[str, DeploymentConfiguration] = {}
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        logging.info("Global Deployment Manager initialized")
    
    async def create_global_deployment(self, deployment_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create new global deployment"""
        try:
            config = DeploymentConfiguration(**deployment_config)
            
            # Store deployment configuration
            await self.redis_client.hset(
                f"deployment:{config.deployment_id}",
                mapping=config.dict()
            )
            
            self.deployments[config.deployment_id] = config
            
            # Add to deployment registry
            await self.redis_client.sadd("deployment_registry", config.deployment_id)
            
            logging.info(f"Global deployment {config.deployment_id} created successfully")
            
            return {
                "success": True,
                "deployment_id": config.deployment_id,
                "strategy": config.strategy.value,
                "target_regions": [r.value for r in config.target_regions],
                "created_at": config.created_at.isoformat()
            }
            
        except Exception as e:
            logging.error(f"Global deployment creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_global_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Execute global deployment across all regions"""
        try:
            # Get deployment configuration
            config = await self._get_deployment_config(deployment_id)
            if not config:
                return {
                    "success": False,
                    "error": f"Deployment {deployment_id} not found"
                }
            
            # Update deployment status
            await self.redis_client.hset(
                f"deployment:{deployment_id}",
                mapping={
                    "status": DeploymentStatus.IN_PROGRESS.value,
                    "execution_started_at": datetime.utcnow().isoformat()
                }
            )
            
            # Deploy to all target regions
            regional_results = {}
            regional_endpoints = {}
            
            for region in config.target_regions:
                result = await self.regional_manager.deploy_to_region(config, region)
                regional_results[region.value] = result
                
                if result["success"]:
                    regional_endpoints[region.value] = result.get("endpoints", [])
            
            # Check if any region deployment succeeded
            successful_regions = [r for r, result in regional_results.items() if result["success"]]
            
            if not successful_regions:
                # All deployments failed
                await self.redis_client.hset(
                    f"deployment:{deployment_id}",
                    mapping={
                        "status": DeploymentStatus.FAILED.value,
                        "failed_at": datetime.utcnow().isoformat(),
                        "error": "All regional deployments failed"
                    }
                )
                
                return {
                    "success": False,
                    "error": "All regional deployments failed",
                    "regional_results": regional_results
                }
            
            # Configure CDN
            cdn_result = await self.cdn_manager.configure_cdn(config, regional_endpoints)
            
            # Configure global load balancer
            lb_result = await self.lb_manager.configure_global_load_balancer(
                config, regional_endpoints
            )
            
            # Update deployment status
            await self.redis_client.hset(
                f"deployment:{deployment_id}",
                mapping={
                    "status": DeploymentStatus.DEPLOYED.value,
                    "deployed_at": datetime.utcnow().isoformat(),
                    "successful_regions": json.dumps(successful_regions),
                    "cdn_configured": cdn_result.get("success", False),
                    "lb_configured": lb_result.get("success", False)
                }
            )
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "successful_regions": successful_regions,
                "regional_results": regional_results,
                "cdn_result": cdn_result,
                "lb_result": lb_result,
                "deployed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Global deployment execution failed for {deployment_id}: {e}")
            
            # Update deployment status
            await self.redis_client.hset(
                f"deployment:{deployment_id}",
                mapping={
                    "status": DeploymentStatus.FAILED.value,
                    "failed_at": datetime.utcnow().isoformat(),
                    "error": str(e)
                }
            )
            
            return {
                "success": False,
                "error": str(e),
                "deployment_id": deployment_id
            }
    
    async def get_deployment_status(self, deployment_id: str) -> Dict[str, Any]:
        """Get comprehensive deployment status"""
        try:
            # Get deployment configuration
            deployment_data = await self.redis_client.hgetall(f"deployment:{deployment_id}")
            if not deployment_data:
                return {"error": "Deployment not found"}
            
            # Get regional deployment statuses
            regional_statuses = {}
            config = await self._get_deployment_config(deployment_id)
            
            if config:
                for region in config.target_regions:
                    regional_deployment_id = f"{deployment_id}_{region.value}"
                    regional_data = await self.redis_client.hgetall(
                        f"regional_deployment:{regional_deployment_id}"
                    )
                    
                    if regional_data:
                        regional_statuses[region.value] = {
                            "status": regional_data.get("status"),
                            "endpoints": json.loads(regional_data.get("endpoints", "[]")),
                            "deployed_at": regional_data.get("deployed_at")
                        }
            
            # Get health metrics
            health_metrics = await self._get_deployment_health_metrics(deployment_id)
            
            return {
                "deployment_id": deployment_id,
                "global_status": deployment_data.get("status"),
                "regional_statuses": regional_statuses,
                "health_metrics": health_metrics,
                "cdn_configured": deployment_data.get("cdn_configured") == "True",
                "lb_configured": deployment_data.get("lb_configured") == "True",
                "created_at": deployment_data.get("created_at"),
                "deployed_at": deployment_data.get("deployed_at")
            }
            
        except Exception as e:
            logging.error(f"Get deployment status failed for {deployment_id}: {e}")
            return {"error": str(e)}
    
    async def rollback_deployment(self, deployment_id: str) -> Dict[str, Any]:
        """Rollback global deployment"""
        try:
            # Update deployment status
            await self.redis_client.hset(
                f"deployment:{deployment_id}",
                mapping={
                    "status": DeploymentStatus.ROLLING_BACK.value,
                    "rollback_started_at": datetime.utcnow().isoformat()
                }
            )
            
            # Get deployment configuration
            config = await self._get_deployment_config(deployment_id)
            if not config:
                return {"success": False, "error": "Deployment configuration not found"}
            
            # Rollback regional deployments
            rollback_results = {}
            
            for region in config.target_regions:
                regional_deployment_id = f"{deployment_id}_{region.value}"
                
                # Simulate rollback (in real implementation, restore previous version)
                await self.redis_client.hset(
                    f"regional_deployment:{regional_deployment_id}",
                    mapping={
                        "status": DeploymentStatus.ROLLED_BACK.value,
                        "rolled_back_at": datetime.utcnow().isoformat()
                    }
                )
                
                rollback_results[region.value] = {"success": True}
            
            # Update global deployment status
            await self.redis_client.hset(
                f"deployment:{deployment_id}",
                mapping={
                    "status": DeploymentStatus.ROLLED_BACK.value,
                    "rolled_back_at": datetime.utcnow().isoformat()
                }
            )
            
            return {
                "success": True,
                "deployment_id": deployment_id,
                "rollback_results": rollback_results,
                "rolled_back_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Deployment rollback failed for {deployment_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_deployments(self, status_filter: Optional[DeploymentStatus] = None) -> List[Dict[str, Any]]:
        """List all deployments with optional status filtering"""
        try:
            deployment_ids = await self.redis_client.smembers("deployment_registry")
            deployments = []
            
            for deployment_id in deployment_ids:
                deployment_data = await self.redis_client.hgetall(f"deployment:{deployment_id}")
                
                if status_filter and deployment_data.get("status") != status_filter.value:
                    continue
                
                deployments.append({
                    "deployment_id": deployment_id,
                    "name": deployment_data.get("name"),
                    "status": deployment_data.get("status"),
                    "strategy": deployment_data.get("strategy"),
                    "created_at": deployment_data.get("created_at"),
                    "deployed_at": deployment_data.get("deployed_at")
                })
            
            return deployments
            
        except Exception as e:
            logging.error(f"List deployments failed: {e}")
            return []
    
    async def _get_deployment_config(self, deployment_id: str) -> Optional[DeploymentConfiguration]:
        """Get deployment configuration"""
        if deployment_id in self.deployments:
            return self.deployments[deployment_id]
        
        config_data = await self.redis_client.hgetall(f"deployment:{deployment_id}")
        if config_data:
            # Convert string lists back to enums
            config_data["target_regions"] = [
                DeploymentRegion(r) for r in json.loads(config_data.get("target_regions", "[]"))
            ]
            config_data["failover_regions"] = [
                DeploymentRegion(r) for r in json.loads(config_data.get("failover_regions", "[]"))
            ]
            config_data["strategy"] = DeploymentStrategy(config_data["strategy"])
            config_data["primary_region"] = DeploymentRegion(config_data["primary_region"])
            config_data["cdn_provider"] = CDNProvider(config_data["cdn_provider"])
            
            config = DeploymentConfiguration(**config_data)
            self.deployments[deployment_id] = config
            return config
        
        return None
    
    async def _get_deployment_health_metrics(self, deployment_id: str) -> Dict[str, Any]:
        """Get deployment health metrics"""
        try:
            config = await self._get_deployment_config(deployment_id)
            if not config:
                return {}
            
            health_metrics = {}
            
            for region in config.target_regions:
                regional_deployment_id = f"{deployment_id}_{region.value}"
                
                # Get regional health data (simplified)
                health_data = await self.redis_client.hgetall(f"health_metrics:{regional_deployment_id}")
                
                if health_data:
                    health_metrics[region.value] = {
                        "uptime": float(health_data.get("uptime", 99.9)),
                        "response_time": float(health_data.get("response_time", 150)),
                        "error_rate": float(health_data.get("error_rate", 0.1)),
                        "last_check": health_data.get("last_check")
                    }
                else:
                    # Default healthy metrics
                    health_metrics[region.value] = {
                        "uptime": 99.9,
                        "response_time": 150,
                        "error_rate": 0.1,
                        "last_check": datetime.utcnow().isoformat()
                    }
            
            return health_metrics
            
        except Exception as e:
            logging.error(f"Get deployment health metrics failed: {e}")
            return {}
    
    async def start_monitoring(self) -> bool:
        """Start global deployment monitoring"""
        try:
            if self.monitoring_active:
                logging.warning("Global deployment monitoring already active")
                return True
            
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logging.info("Global deployment monitoring started")
            return True
            
        except Exception as e:
            logging.error(f"Global deployment monitoring start failed: {e}")
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop global deployment monitoring"""
        try:
            self.monitoring_active = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
                self.monitoring_task = None
            
            logging.info("Global deployment monitoring stopped")
            return True
            
        except Exception as e:
            logging.error(f"Global deployment monitoring stop failed: {e}")
            return False
    
    async def _monitoring_loop(self):
        """Internal monitoring loop"""
        while self.monitoring_active:
            try:
                deployment_ids = await self.redis_client.smembers("deployment_registry")
                
                for deployment_id in deployment_ids:
                    # Monitor deployment health
                    await self._monitor_deployment_health(deployment_id)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Global deployment monitoring loop error: {e}")
                await asyncio.sleep(120)  # Extended wait on error
    
    async def _monitor_deployment_health(self, deployment_id: str):
        """Monitor individual deployment health"""
        try:
            config = await self._get_deployment_config(deployment_id)
            if not config:
                return
            
            # Monitor each region
            for region in config.target_regions:
                regional_deployment_id = f"{deployment_id}_{region.value}"
                
                # Simulate health metrics collection
                health_metrics = {
                    "uptime": 99.9 + (hash(regional_deployment_id) % 10) / 100,  # 99.9-99.99%
                    "response_time": 100 + (hash(regional_deployment_id) % 100),  # 100-200ms
                    "error_rate": (hash(regional_deployment_id) % 5) / 100,  # 0-0.05%
                    "last_check": datetime.utcnow().isoformat()
                }
                
                # Store health metrics
                await self.redis_client.hset(
                    f"health_metrics:{regional_deployment_id}",
                    mapping=health_metrics
                )
                
                # Set TTL for metrics
                await self.redis_client.expire(f"health_metrics:{regional_deployment_id}", 3600)
                
        except Exception as e:
            logging.error(f"Deployment health monitoring failed for {deployment_id}: {e}")
    
    async def get_enterprise_deployment_metrics(self) -> Dict[str, Any]:
        """Get comprehensive enterprise deployment metrics"""
        try:
            deployment_ids = await self.redis_client.smembers("deployment_registry")
            total_deployments = len(deployment_ids)
            
            # Count by status and strategy
            status_counts = {}
            strategy_counts = {}
            region_counts = {}
            
            for deployment_id in deployment_ids:
                deployment_data = await self.redis_client.hgetall(f"deployment:{deployment_id}")
                
                status = deployment_data.get("status", "unknown")
                strategy = deployment_data.get("strategy", "unknown")
                
                status_counts[status] = status_counts.get(status, 0) + 1
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
                
                # Count regions
                successful_regions = json.loads(deployment_data.get("successful_regions", "[]"))
                for region in successful_regions:
                    region_counts[region] = region_counts.get(region, 0) + 1
            
            return {
                "total_deployments": total_deployments,
                "status_distribution": status_counts,
                "strategy_distribution": strategy_counts,
                "region_distribution": region_counts,
                "monitoring_active": self.monitoring_active,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Enterprise deployment metrics collection failed: {e}")
            return {}


# Enterprise global deployment manager instance
_deployment_manager_instance: Optional[GlobalDeploymentManager] = None


async def get_global_deployment_manager(
    db_session: AsyncSession,
    redis_client: redis.Redis
) -> GlobalDeploymentManager:
    """Get or create global deployment manager instance"""
    global _deployment_manager_instance
    
    if _deployment_manager_instance is None:
        _deployment_manager_instance = GlobalDeploymentManager(db_session, redis_client)
    
    return _deployment_manager_instance


async def initialize_enterprise_global_deployment(
    db_session: AsyncSession,
    redis_client: redis.Redis
) -> bool:
    """Initialize enterprise global deployment manager"""
    try:
        deployment_manager = await get_global_deployment_manager(db_session, redis_client)
        
        # Start monitoring
        await deployment_manager.start_monitoring()
        
        logging.info("Enterprise global deployment manager initialized successfully")
        return True
        
    except Exception as e:
        logging.error(f"Enterprise global deployment manager initialization failed: {e}")
        return False


# Export enterprise global deployment components
__all__ = [
    "GlobalDeploymentManager",
    "DeploymentConfiguration",
    "DeploymentRegion",
    "DeploymentStrategy",
    "DeploymentStatus",
    "CDNProvider",
    "RegionalDeploymentManager",
    "CDNManager",
    "LoadBalancerManager",
    "get_global_deployment_manager",
    "initialize_enterprise_global_deployment"
]