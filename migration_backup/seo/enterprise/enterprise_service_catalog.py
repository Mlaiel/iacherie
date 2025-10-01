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

Enterprise Service Catalog
==========================

Enterprise-grade service catalog and API management system for IA Chéries SEO platform.
Provides comprehensive service discovery, documentation, and lifecycle management.

Author: Fahed Mlaiel (mlaiel@live.de)
Enterprise Architecture: Advanced Service Management Systems
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import semver

from pydantic import BaseModel, Field, validator, HttpUrl
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession


class ServiceType(str, Enum):
    """Service type classification"""
    REST_API = "rest_api"
    GRAPHQL_API = "graphql_api"
    MICROSERVICE = "microservice"
    DATABASE_SERVICE = "database_service"
    MESSAGE_QUEUE = "message_queue"
    CACHE_SERVICE = "cache_service"
    AUTHENTICATION_SERVICE = "authentication_service"
    FILE_STORAGE = "file_storage"
    ANALYTICS_SERVICE = "analytics_service"
    AI_SERVICE = "ai_service"


class ServiceStatus(str, Enum):
    """Service status enumeration"""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class ServiceTier(str, Enum):
    """Service tier classification"""
    TIER_1_CRITICAL = "tier_1_critical"
    TIER_2_IMPORTANT = "tier_2_important"
    TIER_3_STANDARD = "tier_3_standard"
    TIER_4_DEVELOPMENT = "tier_4_development"


class APIMethod(str, Enum):
    """API HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


@dataclass
class ServiceMetrics:
    """Service performance metrics"""
    service_id: str
    timestamp: datetime
    uptime_percentage: float
    average_response_time: float
    request_count: int
    error_count: int
    active_connections: int
    cpu_usage: float
    memory_usage: float


class APIEndpoint(BaseModel):
    """API endpoint definition"""
    endpoint_id: str = Field(..., description="Unique endpoint identifier")
    path: str = Field(..., description="API endpoint path")
    method: APIMethod = Field(..., description="HTTP method")
    description: str = Field(..., description="Endpoint description")
    
    # Request/Response schema
    request_schema: Dict[str, Any] = Field(default_factory=dict)
    response_schema: Dict[str, Any] = Field(default_factory=dict)
    
    # Authentication
    authentication_required: bool = Field(default=True)
    authorization_scopes: List[str] = Field(default_factory=list)
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=1000)
    rate_limit_per_hour: int = Field(default=10000)
    
    # Documentation
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    # Versioning
    version: str = Field(default="1.0.0")
    deprecated: bool = Field(default=False)
    deprecation_date: Optional[datetime] = None


class ServiceConfiguration(BaseModel):
    """Service configuration model"""
    service_id: str = Field(..., description="Unique service identifier")
    name: str = Field(..., description="Service display name")
    description: str = Field(..., description="Service description")
    service_type: ServiceType = Field(..., description="Service type")
    status: ServiceStatus = Field(default=ServiceStatus.ACTIVE)
    tier: ServiceTier = Field(..., description="Service tier")
    
    # Technical details
    version: str = Field(..., description="Service version")
    base_url: HttpUrl = Field(..., description="Service base URL")
    health_check_url: Optional[HttpUrl] = None
    documentation_url: Optional[HttpUrl] = None
    
    # API endpoints
    endpoints: List[APIEndpoint] = Field(default_factory=list)
    
    # Dependencies
    dependencies: List[str] = Field(default_factory=list)
    dependents: List[str] = Field(default_factory=list)
    
    # Ownership and contacts
    owner_team: str = Field(..., description="Owning team")
    technical_contact: str = Field(..., description="Technical contact")
    business_contact: str = Field(..., description="Business contact")
    
    # SLA and requirements
    sla_uptime: float = Field(default=99.9, description="SLA uptime percentage")
    max_response_time: int = Field(default=1000, description="Max response time in ms")
    
    # Environment configuration
    environments: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Tags and metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('service_id')
    def validate_service_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('service_id must be at least 3 characters')
        return v.lower().replace(' ', '_')

    @validator('version')
    def validate_version(cls, v):
        try:
            semver.VersionInfo.parse(v)
            return v
        except ValueError:
            raise ValueError('version must be valid semantic version (e.g., 1.0.0)')


class ServiceDiscoveryEngine:
    """Service discovery and registration engine"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.service_registry: Dict[str, ServiceConfiguration] = {}
        
    async def register_service(self, service_config: ServiceConfiguration) -> bool:
        """Register service in discovery engine"""
        try:
            # Store service configuration
            await self.redis_client.hset(
                f"service_catalog:{service_config.service_id}",
                mapping=service_config.dict()
            )
            
            self.service_registry[service_config.service_id] = service_config
            
            # Add to service registry
            await self.redis_client.sadd("service_registry", service_config.service_id)
            
            # Index by type
            await self.redis_client.sadd(
                f"services_by_type:{service_config.service_type.value}",
                service_config.service_id
            )
            
            # Index by tier
            await self.redis_client.sadd(
                f"services_by_tier:{service_config.tier.value}",
                service_config.service_id
            )
            
            # Index by owner
            await self.redis_client.sadd(
                f"services_by_owner:{service_config.owner_team}",
                service_config.service_id
            )
            
            # Register endpoints
            await self._register_endpoints(service_config)
            
            logging.info(f"Service {service_config.service_id} registered successfully")
            return True
            
        except Exception as e:
            logging.error(f"Service registration failed for {service_config.service_id}: {e}")
            return False
    
    async def _register_endpoints(self, service_config: ServiceConfiguration):
        """Register service endpoints"""
        try:
            for endpoint in service_config.endpoints:
                endpoint_key = f"endpoint:{service_config.service_id}:{endpoint.endpoint_id}"
                
                endpoint_data = endpoint.dict()
                endpoint_data["service_id"] = service_config.service_id
                endpoint_data["service_name"] = service_config.name
                endpoint_data["base_url"] = str(service_config.base_url)
                
                await self.redis_client.hset(endpoint_key, mapping=endpoint_data)
                
                # Index by method
                await self.redis_client.sadd(
                    f"endpoints_by_method:{endpoint.method.value}",
                    endpoint_key
                )
                
                # Index by tags
                for tag in endpoint.tags:
                    await self.redis_client.sadd(f"endpoints_by_tag:{tag}", endpoint_key)
            
        except Exception as e:
            logging.error(f"Endpoint registration failed: {e}")
    
    async def discover_services(
        self, 
        service_type: Optional[ServiceType] = None,
        tier: Optional[ServiceTier] = None,
        owner: Optional[str] = None,
        status: Optional[ServiceStatus] = None
    ) -> List[Dict[str, Any]]:
        """Discover services based on criteria"""
        try:
            # Start with all services
            if service_type:
                service_ids = await self.redis_client.smembers(f"services_by_type:{service_type.value}")
            elif tier:
                service_ids = await self.redis_client.smembers(f"services_by_tier:{tier.value}")
            elif owner:
                service_ids = await self.redis_client.smembers(f"services_by_owner:{owner}")
            else:
                service_ids = await self.redis_client.smembers("service_registry")
            
            services = []
            
            for service_id in service_ids:
                service_data = await self.redis_client.hgetall(f"service_catalog:{service_id}")
                
                if not service_data:
                    continue
                
                # Apply status filter
                if status and service_data.get("status") != status.value:
                    continue
                
                # Get health metrics
                health_data = await self._get_service_health(service_id)
                
                services.append({
                    "service_id": service_id,
                    "name": service_data.get("name"),
                    "description": service_data.get("description"),
                    "service_type": service_data.get("service_type"),
                    "status": service_data.get("status"),
                    "tier": service_data.get("tier"),
                    "version": service_data.get("version"),
                    "base_url": service_data.get("base_url"),
                    "owner_team": service_data.get("owner_team"),
                    "health": health_data,
                    "updated_at": service_data.get("updated_at")
                })
            
            return services
            
        except Exception as e:
            logging.error(f"Service discovery failed: {e}")
            return []
    
    async def discover_endpoints(
        self, 
        method: Optional[APIMethod] = None,
        tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Discover API endpoints"""
        try:
            if method:
                endpoint_keys = await self.redis_client.smembers(f"endpoints_by_method:{method.value}")
            elif tag:
                endpoint_keys = await self.redis_client.smembers(f"endpoints_by_tag:{tag}")
            else:
                # Get all endpoints
                endpoint_keys = await self.redis_client.keys("endpoint:*")
            
            endpoints = []
            
            for endpoint_key in endpoint_keys:
                endpoint_data = await self.redis_client.hgetall(endpoint_key)
                
                if endpoint_data:
                    endpoints.append({
                        "endpoint_id": endpoint_data.get("endpoint_id"),
                        "service_id": endpoint_data.get("service_id"),
                        "service_name": endpoint_data.get("service_name"),
                        "path": endpoint_data.get("path"),
                        "method": endpoint_data.get("method"),
                        "description": endpoint_data.get("description"),
                        "full_url": f"{endpoint_data.get('base_url')}{endpoint_data.get('path')}",
                        "authentication_required": endpoint_data.get("authentication_required") == "True",
                        "version": endpoint_data.get("version"),
                        "deprecated": endpoint_data.get("deprecated") == "True"
                    })
            
            return endpoints
            
        except Exception as e:
            logging.error(f"Endpoint discovery failed: {e}")
            return []
    
    async def _get_service_health(self, service_id: str) -> Dict[str, Any]:
        """Get service health status"""
        try:
            health_data = await self.redis_client.hgetall(f"service_health:{service_id}")
            
            if health_data:
                return {
                    "status": health_data.get("status", "unknown"),
                    "uptime": float(health_data.get("uptime", 0.0)),
                    "response_time": float(health_data.get("response_time", 0.0)),
                    "last_check": health_data.get("last_check")
                }
            
            return {"status": "unknown"}
            
        except Exception as e:
            logging.error(f"Get service health failed: {e}")
            return {"status": "error"}


class APIDocumentationGenerator:
    """Automatic API documentation generation"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    async def generate_service_documentation(self, service_id: str) -> Dict[str, Any]:
        """Generate comprehensive service documentation"""
        try:
            service_data = await self.redis_client.hgetall(f"service_catalog:{service_id}")
            
            if not service_data:
                return {"error": "Service not found"}
            
            # Get endpoints
            endpoint_keys = await self.redis_client.keys(f"endpoint:{service_id}:*")
            endpoints = []
            
            for endpoint_key in endpoint_keys:
                endpoint_data = await self.redis_client.hgetall(endpoint_key)
                if endpoint_data:
                    endpoints.append(self._format_endpoint_documentation(endpoint_data))
            
            # Generate OpenAPI specification
            openapi_spec = self._generate_openapi_spec(service_data, endpoints)
            
            # Generate markdown documentation
            markdown_doc = self._generate_markdown_documentation(service_data, endpoints)
            
            return {
                "service_id": service_id,
                "openapi_specification": openapi_spec,
                "markdown_documentation": markdown_doc,
                "endpoints_count": len(endpoints),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Generate service documentation failed: {e}")
            return {"error": str(e)}
    
    def _format_endpoint_documentation(self, endpoint_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format endpoint data for documentation"""
        return {
            "endpoint_id": endpoint_data.get("endpoint_id"),
            "path": endpoint_data.get("path"),
            "method": endpoint_data.get("method"),
            "description": endpoint_data.get("description"),
            "request_schema": json.loads(endpoint_data.get("request_schema", "{}")),
            "response_schema": json.loads(endpoint_data.get("response_schema", "{}")),
            "authentication_required": endpoint_data.get("authentication_required") == "True",
            "authorization_scopes": json.loads(endpoint_data.get("authorization_scopes", "[]")),
            "rate_limit_per_minute": int(endpoint_data.get("rate_limit_per_minute", 1000)),
            "examples": json.loads(endpoint_data.get("examples", "[]")),
            "tags": json.loads(endpoint_data.get("tags", "[]")),
            "version": endpoint_data.get("version"),
            "deprecated": endpoint_data.get("deprecated") == "True"
        }
    
    def _generate_openapi_spec(self, service_data: Dict[str, Any], endpoints: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate OpenAPI 3.0 specification"""
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": service_data.get("name", "Unknown Service"),
                "description": service_data.get("description", ""),
                "version": service_data.get("version", "1.0.0"),
                "contact": {
                    "name": service_data.get("technical_contact", ""),
                    "email": f"{service_data.get('technical_contact', '')}@ainflue.com"
                }
            },
            "servers": [
                {
                    "url": service_data.get("base_url", ""),
                    "description": "Production server"
                }
            ],
            "paths": {},
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer"
                    }
                }
            }
        }
        
        # Add paths
        for endpoint in endpoints:
            path = endpoint["path"]
            method = endpoint["method"].lower()
            
            if path not in openapi_spec["paths"]:
                openapi_spec["paths"][path] = {}
            
            endpoint_spec = {
                "summary": endpoint["description"],
                "description": endpoint["description"],
                "tags": endpoint["tags"],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": endpoint.get("response_schema", {})
                            }
                        }
                    }
                }
            }
            
            # Add request body for POST/PUT/PATCH
            if method in ["post", "put", "patch"] and endpoint.get("request_schema"):
                endpoint_spec["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint["request_schema"]
                        }
                    }
                }
            
            # Add security if required
            if endpoint["authentication_required"]:
                endpoint_spec["security"] = [{"bearerAuth": endpoint["authorization_scopes"]}]
            
            openapi_spec["paths"][path][method] = endpoint_spec
        
        return openapi_spec
    
    def _generate_markdown_documentation(self, service_data: Dict[str, Any], endpoints: List[Dict[str, Any]]) -> str:
        """Generate markdown documentation"""
        markdown_lines = [
            f"# {service_data.get('name', 'Unknown Service')}",
            "",
            f"**Version:** {service_data.get('version', '1.0.0')}",
            f"**Type:** {service_data.get('service_type', 'Unknown')}",
            f"**Tier:** {service_data.get('tier', 'Unknown')}",
            f"**Owner:** {service_data.get('owner_team', 'Unknown')}",
            "",
            "## Description",
            "",
            service_data.get('description', 'No description available.'),
            "",
            "## Base URL",
            "",
            f"`{service_data.get('base_url', 'Unknown')}`",
            "",
            "## Endpoints",
            ""
        ]
        
        # Group endpoints by tag
        endpoints_by_tag = {}
        for endpoint in endpoints:
            tags = endpoint.get("tags", ["General"])
            for tag in tags:
                if tag not in endpoints_by_tag:
                    endpoints_by_tag[tag] = []
                endpoints_by_tag[tag].append(endpoint)
        
        # Generate documentation for each tag
        for tag, tag_endpoints in endpoints_by_tag.items():
            markdown_lines.extend([
                f"### {tag}",
                ""
            ])
            
            for endpoint in tag_endpoints:
                method = endpoint["method"]
                path = endpoint["path"]
                description = endpoint["description"]
                
                markdown_lines.extend([
                    f"#### `{method} {path}`",
                    "",
                    description,
                    ""
                ])
                
                # Authentication
                if endpoint["authentication_required"]:
                    scopes = ", ".join(endpoint["authorization_scopes"])
                    markdown_lines.extend([
                        "**Authentication:** Required",
                        f"**Scopes:** {scopes if scopes else 'None'}",
                        ""
                    ])
                
                # Rate limits
                markdown_lines.extend([
                    f"**Rate Limit:** {endpoint['rate_limit_per_minute']} requests/minute",
                    ""
                ])
                
                # Examples
                if endpoint.get("examples"):
                    markdown_lines.extend([
                        "**Example:**",
                        "",
                        "```json",
                        json.dumps(endpoint["examples"][0], indent=2),
                        "```",
                        ""
                    ])
                
                # Deprecation notice
                if endpoint.get("deprecated"):
                    markdown_lines.extend([
                        "⚠️ **DEPRECATED** - This endpoint is deprecated and will be removed in a future version.",
                        ""
                    ])
                
                markdown_lines.append("---")
                markdown_lines.append("")
        
        # Dependencies
        dependencies = json.loads(service_data.get("dependencies", "[]"))
        if dependencies:
            markdown_lines.extend([
                "## Dependencies",
                "",
                "This service depends on the following services:",
                ""
            ])
            
            for dep in dependencies:
                markdown_lines.append(f"- {dep}")
            
            markdown_lines.append("")
        
        # SLA
        markdown_lines.extend([
            "## Service Level Agreement",
            "",
            f"- **Uptime:** {service_data.get('sla_uptime', 99.9)}%",
            f"- **Max Response Time:** {service_data.get('max_response_time', 1000)}ms",
            ""
        ])
        
        # Contact information
        markdown_lines.extend([
            "## Contact Information",
            "",
            f"- **Technical Contact:** {service_data.get('technical_contact', 'Unknown')}",
            f"- **Business Contact:** {service_data.get('business_contact', 'Unknown')}",
            "",
            "---",
            "",
            f"*Documentation generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*"
        ])
        
        return "\n".join(markdown_lines)


class ServiceLifecycleManager:
    """Service lifecycle management"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    async def update_service_version(
        self, 
        service_id: str, 
        new_version: str, 
        changes: List[str]
    ) -> Dict[str, Any]:
        """Update service version"""
        try:
            # Get current service
            service_data = await self.redis_client.hgetall(f"service_catalog:{service_id}")
            
            if not service_data:
                return {"success": False, "error": "Service not found"}
            
            current_version = service_data.get("version", "1.0.0")
            
            # Validate version
            try:
                current_semver = semver.VersionInfo.parse(current_version)
                new_semver = semver.VersionInfo.parse(new_version)
                
                if new_semver <= current_semver:
                    return {"success": False, "error": "New version must be greater than current version"}
                    
            except ValueError as e:
                return {"success": False, "error": f"Invalid version format: {e}"}
            
            # Create version history entry
            version_history = {
                "previous_version": current_version,
                "new_version": new_version,
                "changes": changes,
                "updated_at": datetime.utcnow().isoformat(),
                "updated_by": "system"  # Should be actual user
            }
            
            # Store version history
            await self.redis_client.lpush(
                f"service_version_history:{service_id}",
                json.dumps(version_history)
            )
            
            # Update service version
            await self.redis_client.hset(
                f"service_catalog:{service_id}",
                mapping={
                    "version": new_version,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            return {
                "success": True,
                "service_id": service_id,
                "previous_version": current_version,
                "new_version": new_version,
                "changes": changes
            }
            
        except Exception as e:
            logging.error(f"Update service version failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def deprecate_service(
        self, 
        service_id: str, 
        deprecation_date: datetime,
        reason: str,
        migration_guide: str
    ) -> Dict[str, Any]:
        """Deprecate service"""
        try:
            # Update service status
            await self.redis_client.hset(
                f"service_catalog:{service_id}",
                mapping={
                    "status": ServiceStatus.DEPRECATED.value,
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            # Store deprecation information
            deprecation_info = {
                "service_id": service_id,
                "deprecation_date": deprecation_date.isoformat(),
                "reason": reason,
                "migration_guide": migration_guide,
                "deprecated_at": datetime.utcnow().isoformat()
            }
            
            await self.redis_client.hset(
                f"service_deprecation:{service_id}",
                mapping=deprecation_info
            )
            
            # Notify dependents
            await self._notify_service_dependents(service_id, "deprecated")
            
            return {
                "success": True,
                "service_id": service_id,
                "deprecation_date": deprecation_date.isoformat(),
                "reason": reason
            }
            
        except Exception as e:
            logging.error(f"Deprecate service failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _notify_service_dependents(self, service_id: str, event_type: str):
        """Notify services that depend on this service"""
        try:
            # Find dependent services
            dependent_services = await self.redis_client.smembers("service_registry")
            
            for dependent_service_id in dependent_services:
                service_data = await self.redis_client.hgetall(f"service_catalog:{dependent_service_id}")
                
                if service_data:
                    dependencies = json.loads(service_data.get("dependencies", "[]"))
                    
                    if service_id in dependencies:
                        # Create notification
                        notification = {
                            "dependent_service": dependent_service_id,
                            "affected_dependency": service_id,
                            "event_type": event_type,
                            "timestamp": datetime.utcnow().isoformat(),
                            "acknowledged": False
                        }
                        
                        await self.redis_client.lpush(
                            f"service_notifications:{dependent_service_id}",
                            json.dumps(notification)
                        )
            
        except Exception as e:
            logging.error(f"Notify service dependents failed: {e}")


class EnterpriseServiceCatalog:
    """
    Enterprise Service Catalog
    
    Comprehensive service catalog management system providing:
    - Service discovery and registration
    - API documentation generation
    - Service lifecycle management
    - Dependency tracking and management
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: redis.Redis):
        self.db_session = db_session
        self.redis_client = redis_client
        
        # Initialize components
        self.discovery_engine = ServiceDiscoveryEngine(redis_client)
        self.documentation_generator = APIDocumentationGenerator(redis_client)
        self.lifecycle_manager = ServiceLifecycleManager(redis_client)
        
        # Service registry
        self.services: Dict[str, ServiceConfiguration] = {}
        
        # Monitoring
        self.catalog_active = False
        self.catalog_task: Optional[asyncio.Task] = None
        
        logging.info("Enterprise Service Catalog initialized")
    
    async def register_service(self, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """Register new service in catalog"""
        try:
            config = ServiceConfiguration(**service_config)
            
            success = await self.discovery_engine.register_service(config)
            
            if success:
                self.services[config.service_id] = config
                
                # Generate initial documentation
                await self.documentation_generator.generate_service_documentation(config.service_id)
                
                return {
                    "success": True,
                    "service_id": config.service_id,
                    "name": config.name,
                    "version": config.version,
                    "endpoints_count": len(config.endpoints),
                    "registered_at": config.created_at.isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": "Service registration failed"
                }
                
        except Exception as e:
            logging.error(f"Register service failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def discover_services(
        self, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Discover services with optional filters"""
        try:
            # Parse filters
            service_type = None
            tier = None
            owner = None
            status = None
            
            if filters:
                if "service_type" in filters:
                    service_type = ServiceType(filters["service_type"])
                if "tier" in filters:
                    tier = ServiceTier(filters["tier"])
                if "owner" in filters:
                    owner = filters["owner"]
                if "status" in filters:
                    status = ServiceStatus(filters["status"])
            
            services = await self.discovery_engine.discover_services(
                service_type=service_type,
                tier=tier,
                owner=owner,
                status=status
            )
            
            return services
            
        except Exception as e:
            logging.error(f"Discover services failed: {e}")
            return []
    
    async def get_service_details(self, service_id: str) -> Dict[str, Any]:
        """Get comprehensive service details"""
        try:
            service_data = await self.redis_client.hgetall(f"service_catalog:{service_id}")
            
            if not service_data:
                return {"error": "Service not found"}
            
            # Get endpoints
            endpoints = await self.discovery_engine.discover_endpoints()
            service_endpoints = [ep for ep in endpoints if ep["service_id"] == service_id]
            
            # Get dependencies
            dependencies = json.loads(service_data.get("dependencies", "[]"))
            dependents = json.loads(service_data.get("dependents", "[]"))
            
            # Get health metrics
            health_data = await self.discovery_engine._get_service_health(service_id)
            
            # Get version history
            version_history = await self._get_version_history(service_id)
            
            return {
                "service_id": service_id,
                "configuration": {
                    "name": service_data.get("name"),
                    "description": service_data.get("description"),
                    "service_type": service_data.get("service_type"),
                    "status": service_data.get("status"),
                    "tier": service_data.get("tier"),
                    "version": service_data.get("version"),
                    "base_url": service_data.get("base_url"),
                    "owner_team": service_data.get("owner_team"),
                    "technical_contact": service_data.get("technical_contact"),
                    "business_contact": service_data.get("business_contact"),
                    "sla_uptime": float(service_data.get("sla_uptime", 99.9)),
                    "max_response_time": int(service_data.get("max_response_time", 1000))
                },
                "endpoints": service_endpoints,
                "dependencies": dependencies,
                "dependents": dependents,
                "health": health_data,
                "version_history": version_history,
                "created_at": service_data.get("created_at"),
                "updated_at": service_data.get("updated_at")
            }
            
        except Exception as e:
            logging.error(f"Get service details failed for {service_id}: {e}")
            return {"error": str(e)}
    
    async def generate_api_documentation(self, service_id: str) -> Dict[str, Any]:
        """Generate API documentation for service"""
        try:
            documentation = await self.documentation_generator.generate_service_documentation(service_id)
            
            return documentation
            
        except Exception as e:
            logging.error(f"Generate API documentation failed for {service_id}: {e}")
            return {"error": str(e)}
    
    async def update_service_version(
        self, 
        service_id: str, 
        new_version: str, 
        changes: List[str]
    ) -> Dict[str, Any]:
        """Update service version"""
        try:
            result = await self.lifecycle_manager.update_service_version(
                service_id, new_version, changes
            )
            
            if result.get("success"):
                # Regenerate documentation
                await self.documentation_generator.generate_service_documentation(service_id)
            
            return result
            
        except Exception as e:
            logging.error(f"Update service version failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_dependency_graph(self) -> Dict[str, Any]:
        """Get service dependency graph"""
        try:
            service_ids = await self.redis_client.smembers("service_registry")
            
            nodes = []
            edges = []
            
            for service_id in service_ids:
                service_data = await self.redis_client.hgetall(f"service_catalog:{service_id}")
                
                if service_data:
                    # Add node
                    nodes.append({
                        "id": service_id,
                        "name": service_data.get("name"),
                        "type": service_data.get("service_type"),
                        "tier": service_data.get("tier"),
                        "status": service_data.get("status")
                    })
                    
                    # Add edges for dependencies
                    dependencies = json.loads(service_data.get("dependencies", "[]"))
                    for dependency in dependencies:
                        edges.append({
                            "source": service_id,
                            "target": dependency,
                            "type": "depends_on"
                        })
            
            return {
                "nodes": nodes,
                "edges": edges,
                "total_services": len(nodes),
                "total_dependencies": len(edges),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Get dependency graph failed: {e}")
            return {"error": str(e)}
    
    async def _get_version_history(self, service_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get service version history"""
        try:
            history_data = await self.redis_client.lrange(
                f"service_version_history:{service_id}", 0, limit - 1
            )
            
            history = []
            for entry in history_data:
                history.append(json.loads(entry))
            
            return history
            
        except Exception as e:
            logging.error(f"Get version history failed: {e}")
            return []
    
    async def start_catalog_monitoring(self) -> bool:
        """Start service catalog monitoring"""
        try:
            if self.catalog_active:
                logging.warning("Service catalog monitoring already active")
                return True
            
            self.catalog_active = True
            self.catalog_task = asyncio.create_task(self._catalog_monitoring_loop())
            
            logging.info("Service catalog monitoring started")
            return True
            
        except Exception as e:
            logging.error(f"Service catalog monitoring start failed: {e}")
            return False
    
    async def stop_catalog_monitoring(self) -> bool:
        """Stop service catalog monitoring"""
        try:
            self.catalog_active = False
            
            if self.catalog_task:
                self.catalog_task.cancel()
                try:
                    await self.catalog_task
                except asyncio.CancelledError:
                    pass
                self.catalog_task = None
            
            logging.info("Service catalog monitoring stopped")
            return True
            
        except Exception as e:
            logging.error(f"Service catalog monitoring stop failed: {e}")
            return False
    
    async def _catalog_monitoring_loop(self):
        """Internal catalog monitoring loop"""
        while self.catalog_active:
            try:
                service_ids = await self.redis_client.smembers("service_registry")
                
                for service_id in service_ids:
                    # Monitor service health
                    await self._monitor_service_health(service_id)
                
                # Update catalog status
                await self.redis_client.hset(
                    "service_catalog_status",
                    mapping={
                        "last_monitoring": datetime.utcnow().isoformat(),
                        "services_monitored": len(service_ids),
                        "active": self.catalog_active
                    }
                )
                
                await asyncio.sleep(300)  # Monitor every 5 minutes
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Service catalog monitoring loop error: {e}")
                await asyncio.sleep(600)  # Extended wait on error
    
    async def _monitor_service_health(self, service_id: str):
        """Monitor individual service health"""
        try:
            service_data = await self.redis_client.hgetall(f"service_catalog:{service_id}")
            
            if not service_data:
                return
            
            # Simulate health check (in production, would make actual HTTP request)
            health_check_url = service_data.get("health_check_url")
            
            if health_check_url:
                # Simulate health check result
                health_status = "healthy"  # Would be actual check result
                uptime = 99.9 + (hash(service_id) % 10) / 100  # Simulate uptime
                response_time = 50 + (hash(service_id) % 200)  # Simulate response time
                
                # Store health data
                await self.redis_client.hset(
                    f"service_health:{service_id}",
                    mapping={
                        "status": health_status,
                        "uptime": uptime,
                        "response_time": response_time,
                        "last_check": datetime.utcnow().isoformat()
                    }
                )
                
                # Set TTL for health data
                await self.redis_client.expire(f"service_health:{service_id}", 600)
            
        except Exception as e:
            logging.error(f"Service health monitoring failed for {service_id}: {e}")
    
    async def get_enterprise_catalog_metrics(self) -> Dict[str, Any]:
        """Get comprehensive enterprise catalog metrics"""
        try:
            service_ids = await self.redis_client.smembers("service_registry")
            total_services = len(service_ids)
            
            # Count by type, tier, and status
            type_counts = {}
            tier_counts = {}
            status_counts = {}
            endpoint_count = 0
            
            for service_id in service_ids:
                service_data = await self.redis_client.hgetall(f"service_catalog:{service_id}")
                
                if service_data:
                    service_type = service_data.get("service_type", "unknown")
                    tier = service_data.get("tier", "unknown")
                    status = service_data.get("status", "unknown")
                    
                    type_counts[service_type] = type_counts.get(service_type, 0) + 1
                    tier_counts[tier] = tier_counts.get(tier, 0) + 1
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                # Count endpoints
                endpoints = await self.discovery_engine.discover_endpoints()
                service_endpoints = [ep for ep in endpoints if ep["service_id"] == service_id]
                endpoint_count += len(service_endpoints)
            
            return {
                "total_services": total_services,
                "total_endpoints": endpoint_count,
                "type_distribution": type_counts,
                "tier_distribution": tier_counts,
                "status_distribution": status_counts,
                "catalog_active": self.catalog_active,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Enterprise catalog metrics collection failed: {e}")
            return {}


# Enterprise service catalog instance
_service_catalog_instance: Optional[EnterpriseServiceCatalog] = None


async def get_service_catalog(
    db_session: AsyncSession,
    redis_client: redis.Redis
) -> EnterpriseServiceCatalog:
    """Get or create service catalog instance"""
    global _service_catalog_instance
    
    if _service_catalog_instance is None:
        _service_catalog_instance = EnterpriseServiceCatalog(db_session, redis_client)
    
    return _service_catalog_instance


async def initialize_enterprise_service_catalog(
    db_session: AsyncSession,
    redis_client: redis.Redis
) -> bool:
    """Initialize enterprise service catalog"""
    try:
        service_catalog = await get_service_catalog(db_session, redis_client)
        
        # Start monitoring
        await service_catalog.start_catalog_monitoring()
        
        logging.info("Enterprise service catalog initialized successfully")
        return True
        
    except Exception as e:
        logging.error(f"Enterprise service catalog initialization failed: {e}")
        return False


# Export enterprise service catalog components
__all__ = [
    "EnterpriseServiceCatalog",
    "ServiceConfiguration",
    "APIEndpoint",
    "ServiceType",
    "ServiceStatus",
    "ServiceTier",
    "APIMethod",
    "ServiceDiscoveryEngine",
    "APIDocumentationGenerator",
    "ServiceLifecycleManager",
    "get_service_catalog",
    "initialize_enterprise_service_catalog"
]