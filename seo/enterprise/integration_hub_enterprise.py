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

Integration Hub Enterprise
==========================

Enterprise-grade integration management system for IA Chérie SEO platform.
Provides comprehensive API gateway, service orchestration, and enterprise connectivity.

Author: Fahed Mlaiel (mlaiel@live.de)
Enterprise Architecture: Advanced Integration Systems
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
import aiohttp
import jwt
from contextlib import asynccontextmanager

from pydantic import BaseModel, Field, validator, HttpUrl
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status


class IntegrationType(str, Enum):
    """Integration type classification"""
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    WEBHOOK = "webhook"
    MESSAGE_QUEUE = "message_queue"
    DATABASE = "database"
    FILE_SYSTEM = "file_system"
    MICROSERVICE = "microservice"
    LEGACY_SYSTEM = "legacy_system"


class AuthenticationType(str, Enum):
    """Authentication type enumeration"""
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    BASIC_AUTH = "basic_auth"
    MUTUAL_TLS = "mutual_tls"
    CUSTOM = "custom"


class IntegrationStatus(str, Enum):
    """Integration status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class DataFormat(str, Enum):
    """Data format enumeration"""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    AVRO = "avro"
    PROTOBUF = "protobuf"
    BINARY = "binary"


@dataclass
class IntegrationMetrics:
    """Integration performance metrics"""
    integration_id: str
    timestamp: datetime
    request_count: int
    success_count: int
    error_count: int
    avg_response_time: float
    max_response_time: float
    min_response_time: float
    throughput_per_second: float
    error_rate: float
    uptime_percentage: float


class IntegrationConfiguration(BaseModel):
    """Integration configuration model"""
    integration_id: str = Field(..., description="Unique integration identifier")
    name: str = Field(..., description="Integration display name")
    description: str = Field(..., description="Integration description")
    integration_type: IntegrationType = Field(..., description="Integration type")
    status: IntegrationStatus = Field(default=IntegrationStatus.ACTIVE)
    
    # Connection configuration
    endpoint_url: HttpUrl = Field(..., description="Integration endpoint URL")
    authentication_type: AuthenticationType = Field(..., description="Authentication method")
    authentication_config: Dict[str, Any] = Field(default_factory=dict)
    
    # Data configuration
    input_format: DataFormat = Field(default=DataFormat.JSON)
    output_format: DataFormat = Field(default=DataFormat.JSON)
    data_mapping: Dict[str, str] = Field(default_factory=dict)
    
    # Quality of Service
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    retry_attempts: int = Field(default=3, ge=0, le=10)
    rate_limit_per_minute: int = Field(default=1000, ge=1)
    
    # Monitoring
    health_check_interval: int = Field(default=60, ge=10)
    alert_on_failure: bool = Field(default=True)
    
    # Security
    encryption_enabled: bool = Field(default=True)
    allowed_ip_ranges: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('integration_id')
    def validate_integration_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('integration_id must be at least 3 characters')
        return v.lower().replace(' ', '_')


class APIGatewayManager:
    """Enterprise API Gateway management"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.route_cache: Dict[str, Dict[str, Any]] = {}
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}
        
    async def register_route(self, integration_config: IntegrationConfiguration) -> bool:
        """Register API route in gateway"""
        try:
            route_key = f"route:{integration_config.integration_id}"
            
            route_data = {
                "integration_id": integration_config.integration_id,
                "endpoint_url": str(integration_config.endpoint_url),
                "method": "POST",  # Default method
                "timeout": integration_config.timeout_seconds,
                "rate_limit": integration_config.rate_limit_per_minute,
                "auth_type": integration_config.authentication_type.value,
                "status": integration_config.status.value,
                "registered_at": datetime.utcnow().isoformat()
            }
            
            await self.redis_client.hset(route_key, mapping=route_data)
            self.route_cache[integration_config.integration_id] = route_data
            
            logging.info(f"Route registered for integration {integration_config.integration_id}")
            return True
            
        except Exception as e:
            logging.error(f"Route registration failed for {integration_config.integration_id}: {e}")
            return False
    
    async def route_request(self, integration_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route request through API gateway"""
        try:
            # Get route configuration
            route_data = await self._get_route_config(integration_id)
            if not route_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Integration {integration_id} not found"
                )
            
            # Check rate limiting
            rate_limit_ok = await self._check_rate_limit(integration_id, route_data["rate_limit"])
            if not rate_limit_ok:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            # Route request
            start_time = datetime.utcnow()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    route_data["endpoint_url"],
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=route_data["timeout"])
                ) as response:
                    response_data = await response.json()
                    
                    # Record metrics
                    end_time = datetime.utcnow()
                    response_time = (end_time - start_time).total_seconds() * 1000
                    
                    await self._record_request_metrics(
                        integration_id, response.status, response_time
                    )
                    
                    return {
                        "status": "success",
                        "status_code": response.status,
                        "data": response_data,
                        "response_time_ms": response_time
                    }
            
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Request routing failed for {integration_id}: {e}")
            
            await self._record_request_metrics(integration_id, 500, 0)
            
            return {
                "status": "error",
                "error": str(e),
                "integration_id": integration_id
            }
    
    async def _get_route_config(self, integration_id: str) -> Optional[Dict[str, Any]]:
        """Get route configuration"""
        if integration_id in self.route_cache:
            return self.route_cache[integration_id]
        
        route_data = await self.redis_client.hgetall(f"route:{integration_id}")
        if route_data:
            self.route_cache[integration_id] = route_data
            return route_data
        
        return None
    
    async def _check_rate_limit(self, integration_id: str, limit_per_minute: int) -> bool:
        """Check rate limiting"""
        try:
            current_minute = datetime.utcnow().strftime("%Y%m%d%H%M")
            rate_key = f"rate_limit:{integration_id}:{current_minute}"
            
            current_count = await self.redis_client.incr(rate_key)
            
            if current_count == 1:
                await self.redis_client.expire(rate_key, 60)  # TTL 1 minute
            
            return current_count <= limit_per_minute
            
        except Exception as e:
            logging.error(f"Rate limit check failed for {integration_id}: {e}")
            return True  # Allow on error
    
    async def _record_request_metrics(self, integration_id: str, status_code: int, response_time: float):
        """Record request metrics"""
        try:
            metrics_key = f"metrics:{integration_id}"
            timestamp = datetime.utcnow().isoformat()
            
            # Update metrics
            await self.redis_client.hincrby(metrics_key, "total_requests", 1)
            
            if 200 <= status_code < 300:
                await self.redis_client.hincrby(metrics_key, "success_count", 1)
            else:
                await self.redis_client.hincrby(metrics_key, "error_count", 1)
            
            # Store response time
            await self.redis_client.lpush(
                f"response_times:{integration_id}",
                f"{timestamp}:{response_time}"
            )
            
            # Keep only last 1000 response times
            await self.redis_client.ltrim(f"response_times:{integration_id}", 0, 999)
            
        except Exception as e:
            logging.error(f"Metrics recording failed for {integration_id}: {e}")


class ServiceOrchestrator:
    """Enterprise service orchestration management"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.service_registry: Dict[str, Dict[str, Any]] = {}
        self.workflow_engine: Dict[str, List[Dict[str, Any]]] = {}
    
    async def register_service(self, service_config: Dict[str, Any]) -> bool:
        """Register service in orchestrator"""
        try:
            service_id = service_config["service_id"]
            
            service_data = {
                "service_id": service_id,
                "name": service_config["name"],
                "version": service_config.get("version", "1.0.0"),
                "endpoint": service_config["endpoint"],
                "health_check_url": service_config.get("health_check_url"),
                "dependencies": service_config.get("dependencies", []),
                "capabilities": service_config.get("capabilities", []),
                "status": "active",
                "registered_at": datetime.utcnow().isoformat()
            }
            
            await self.redis_client.hset(f"service:{service_id}", mapping=service_data)
            self.service_registry[service_id] = service_data
            
            logging.info(f"Service {service_id} registered successfully")
            return True
            
        except Exception as e:
            logging.error(f"Service registration failed: {e}")
            return False
    
    async def orchestrate_workflow(self, workflow_id: str, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Orchestrate multi-service workflow"""
        try:
            workflow_context = {
                "workflow_id": workflow_id,
                "started_at": datetime.utcnow().isoformat(),
                "status": "running",
                "steps": workflow_steps,
                "results": {}
            }
            
            # Store workflow context
            await self.redis_client.hset(
                f"workflow:{workflow_id}",
                mapping={"context": json.dumps(workflow_context)}
            )
            
            # Execute workflow steps
            for step_index, step in enumerate(workflow_steps):
                step_result = await self._execute_workflow_step(
                    workflow_id, step_index, step, workflow_context["results"]
                )
                
                workflow_context["results"][f"step_{step_index}"] = step_result
                
                if not step_result.get("success", False):
                    workflow_context["status"] = "failed"
                    workflow_context["failed_at"] = datetime.utcnow().isoformat()
                    break
            
            if workflow_context["status"] == "running":
                workflow_context["status"] = "completed"
                workflow_context["completed_at"] = datetime.utcnow().isoformat()
            
            # Update workflow context
            await self.redis_client.hset(
                f"workflow:{workflow_id}",
                mapping={"context": json.dumps(workflow_context)}
            )
            
            return workflow_context
            
        except Exception as e:
            logging.error(f"Workflow orchestration failed for {workflow_id}: {e}")
            return {
                "workflow_id": workflow_id,
                "status": "error",
                "error": str(e)
            }
    
    async def _execute_workflow_step(
        self, 
        workflow_id: str, 
        step_index: int, 
        step: Dict[str, Any], 
        previous_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute individual workflow step"""
        try:
            service_id = step["service_id"]
            action = step["action"]
            parameters = step.get("parameters", {})
            
            # Get service configuration
            service_data = await self.redis_client.hgetall(f"service:{service_id}")
            if not service_data:
                return {
                    "success": False,
                    "error": f"Service {service_id} not found"
                }
            
            # Prepare request data
            request_data = {
                "action": action,
                "parameters": parameters,
                "workflow_id": workflow_id,
                "step_index": step_index,
                "previous_results": previous_results
            }
            
            # Execute service call
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    service_data["endpoint"],
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response_data = await response.json()
                    
                    return {
                        "success": response.status == 200,
                        "status_code": response.status,
                        "data": response_data,
                        "service_id": service_id,
                        "action": action
                    }
            
        except Exception as e:
            logging.error(f"Workflow step execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "service_id": step.get("service_id"),
                "action": step.get("action")
            }
    
    async def get_service_health(self, service_id: str) -> Dict[str, Any]:
        """Get service health status"""
        try:
            service_data = await self.redis_client.hgetall(f"service:{service_id}")
            if not service_data:
                return {"error": "Service not found"}
            
            health_check_url = service_data.get("health_check_url")
            if not health_check_url:
                return {"status": "unknown", "message": "No health check endpoint"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    health_check_url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    health_data = await response.json()
                    
                    return {
                        "service_id": service_id,
                        "status": "healthy" if response.status == 200 else "unhealthy",
                        "status_code": response.status,
                        "health_data": health_data,
                        "checked_at": datetime.utcnow().isoformat()
                    }
            
        except Exception as e:
            logging.error(f"Service health check failed for {service_id}: {e}")
            return {
                "service_id": service_id,
                "status": "error",
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat()
            }


class DataTransformationEngine:
    """Enterprise data transformation engine"""
    
    def __init__(self):
        self.transformation_rules: Dict[str, Callable] = {}
        self.format_converters: Dict[str, Callable] = {}
        
        # Register default converters
        self._register_default_converters()
    
    def _register_default_converters(self):
        """Register default data format converters"""
        self.format_converters[f"{DataFormat.JSON.value}_to_{DataFormat.XML.value}"] = self._json_to_xml
        self.format_converters[f"{DataFormat.XML.value}_to_{DataFormat.JSON.value}"] = self._xml_to_json
        self.format_converters[f"{DataFormat.JSON.value}_to_{DataFormat.CSV.value}"] = self._json_to_csv
        self.format_converters[f"{DataFormat.CSV.value}_to_{DataFormat.JSON.value}"] = self._csv_to_json
    
    async def transform_data(
        self, 
        data: Any, 
        from_format: DataFormat, 
        to_format: DataFormat,
        mapping_rules: Optional[Dict[str, str]] = None
    ) -> Any:
        """Transform data between formats"""
        try:
            # Apply field mapping if provided
            if mapping_rules and isinstance(data, dict):
                data = self._apply_field_mapping(data, mapping_rules)
            
            # Convert format if needed
            if from_format != to_format:
                converter_key = f"{from_format.value}_to_{to_format.value}"
                if converter_key in self.format_converters:
                    data = self.format_converters[converter_key](data)
                else:
                    logging.warning(f"No converter available for {from_format} to {to_format}")
            
            return data
            
        except Exception as e:
            logging.error(f"Data transformation failed: {e}")
            raise
    
    def _apply_field_mapping(self, data: Dict[str, Any], mapping_rules: Dict[str, str]) -> Dict[str, Any]:
        """Apply field mapping rules"""
        mapped_data = {}
        
        for source_field, target_field in mapping_rules.items():
            if source_field in data:
                mapped_data[target_field] = data[source_field]
        
        # Include unmapped fields
        for field, value in data.items():
            if field not in mapping_rules and field not in mapped_data:
                mapped_data[field] = value
        
        return mapped_data
    
    def _json_to_xml(self, data: Dict[str, Any]) -> str:
        """Convert JSON to XML"""
        import dicttoxml
        return dicttoxml.dicttoxml(data, custom_root='root', attr_type=False).decode('utf-8')
    
    def _xml_to_json(self, xml_data: str) -> Dict[str, Any]:
        """Convert XML to JSON"""
        import xmltodict
        return xmltodict.parse(xml_data)
    
    def _json_to_csv(self, data: List[Dict[str, Any]]) -> str:
        """Convert JSON to CSV"""
        import csv
        import io
        
        if not data:
            return ""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    def _csv_to_json(self, csv_data: str) -> List[Dict[str, Any]]:
        """Convert CSV to JSON"""
        import csv
        import io
        
        input_stream = io.StringIO(csv_data)
        reader = csv.DictReader(input_stream)
        
        return list(reader)


class IntegrationHubEnterprise:
    """
    Enterprise Integration Hub
    
    Comprehensive integration management system providing:
    - API Gateway management
    - Service orchestration
    - Data transformation
    - Enterprise connectivity
    """
    
    def __init__(self, db_session: AsyncSession, redis_client: redis.Redis):
        self.db_session = db_session
        self.redis_client = redis_client
        
        # Initialize managers
        self.api_gateway = APIGatewayManager(redis_client)
        self.service_orchestrator = ServiceOrchestrator(redis_client)
        self.data_transformer = DataTransformationEngine()
        
        # Integration registry
        self.integrations: Dict[str, IntegrationConfiguration] = {}
        
        # Monitoring
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        
        logging.info("Integration Hub Enterprise initialized")
    
    async def create_integration(self, integration_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create new enterprise integration"""
        try:
            config = IntegrationConfiguration(**integration_config)
            
            # Register in API gateway
            gateway_success = await self.api_gateway.register_route(config)
            if not gateway_success:
                return {
                    "success": False,
                    "error": "API Gateway registration failed",
                    "integration_id": config.integration_id
                }
            
            # Store configuration
            await self.redis_client.hset(
                f"integration:{config.integration_id}",
                mapping=config.dict()
            )
            
            self.integrations[config.integration_id] = config
            
            # Add to integration registry
            await self.redis_client.sadd("integration_registry", config.integration_id)
            
            logging.info(f"Integration {config.integration_id} created successfully")
            
            return {
                "success": True,
                "integration_id": config.integration_id,
                "type": config.integration_type.value,
                "status": config.status.value,
                "created_at": config.created_at.isoformat()
            }
            
        except Exception as e:
            logging.error(f"Integration creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_integration(self, integration_id: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration request"""
        try:
            # Get integration configuration
            config = await self._get_integration_config(integration_id)
            if not config:
                return {
                    "success": False,
                    "error": f"Integration {integration_id} not found"
                }
            
            # Check integration status
            if config.status != IntegrationStatus.ACTIVE:
                return {
                    "success": False,
                    "error": f"Integration {integration_id} is not active (status: {config.status})"
                }
            
            # Transform input data if needed
            if config.data_mapping:
                request_data = await self.data_transformer.transform_data(
                    request_data,
                    config.input_format,
                    DataFormat.JSON,  # Internal processing format
                    config.data_mapping
                )
            
            # Route request through API gateway
            response = await self.api_gateway.route_request(integration_id, request_data)
            
            # Transform output data if needed
            if response.get("status") == "success" and config.output_format != DataFormat.JSON:
                response["data"] = await self.data_transformer.transform_data(
                    response["data"],
                    DataFormat.JSON,
                    config.output_format
                )
            
            return response
            
        except Exception as e:
            logging.error(f"Integration execution failed for {integration_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "integration_id": integration_id
            }
    
    async def orchestrate_multi_integration_workflow(
        self, 
        workflow_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Orchestrate workflow across multiple integrations"""
        try:
            workflow_id = workflow_definition.get("workflow_id", str(uuid.uuid4()))
            integrations = workflow_definition.get("integrations", [])
            
            workflow_steps = []
            for integration_step in integrations:
                integration_id = integration_step["integration_id"]
                
                # Convert integration to service step
                workflow_steps.append({
                    "service_id": f"integration_{integration_id}",
                    "action": "execute",
                    "parameters": integration_step.get("parameters", {})
                })
            
            # Execute workflow
            result = await self.service_orchestrator.orchestrate_workflow(
                workflow_id, workflow_steps
            )
            
            return result
            
        except Exception as e:
            logging.error(f"Multi-integration workflow failed: {e}")
            return {
                "workflow_id": workflow_definition.get("workflow_id"),
                "status": "error",
                "error": str(e)
            }
    
    async def get_integration_info(self, integration_id: str) -> Dict[str, Any]:
        """Get comprehensive integration information"""
        try:
            config = await self._get_integration_config(integration_id)
            if not config:
                return {"error": "Integration not found"}
            
            # Get metrics
            metrics = await self._get_integration_metrics(integration_id)
            
            # Get health status
            health = await self._check_integration_health(integration_id)
            
            return {
                "integration_id": integration_id,
                "configuration": config.dict(),
                "metrics": metrics,
                "health": health,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Get integration info failed for {integration_id}: {e}")
            return {"error": str(e)}
    
    async def list_integrations(self, status_filter: Optional[IntegrationStatus] = None) -> List[Dict[str, Any]]:
        """List all integrations with optional status filtering"""
        try:
            integration_ids = await self.redis_client.smembers("integration_registry")
            integrations = []
            
            for integration_id in integration_ids:
                config = await self._get_integration_config(integration_id)
                if not config:
                    continue
                
                if status_filter and config.status != status_filter:
                    continue
                
                integrations.append({
                    "integration_id": integration_id,
                    "name": config.name,
                    "type": config.integration_type.value,
                    "status": config.status.value,
                    "endpoint_url": str(config.endpoint_url),
                    "created_at": config.created_at.isoformat()
                })
            
            return integrations
            
        except Exception as e:
            logging.error(f"List integrations failed: {e}")
            return []
    
    async def _get_integration_config(self, integration_id: str) -> Optional[IntegrationConfiguration]:
        """Get integration configuration"""
        if integration_id in self.integrations:
            return self.integrations[integration_id]
        
        config_data = await self.redis_client.hgetall(f"integration:{integration_id}")
        if config_data:
            config = IntegrationConfiguration(**config_data)
            self.integrations[integration_id] = config
            return config
        
        return None
    
    async def _get_integration_metrics(self, integration_id: str) -> Dict[str, Any]:
        """Get integration metrics"""
        try:
            metrics_data = await self.redis_client.hgetall(f"metrics:{integration_id}")
            
            # Get response time statistics
            response_times = await self.redis_client.lrange(
                f"response_times:{integration_id}", 0, -1
            )
            
            if response_times:
                times = [float(rt.split(':')[1]) for rt in response_times]
                avg_response_time = sum(times) / len(times)
                max_response_time = max(times)
                min_response_time = min(times)
            else:
                avg_response_time = max_response_time = min_response_time = 0.0
            
            total_requests = int(metrics_data.get("total_requests", 0))
            success_count = int(metrics_data.get("success_count", 0))
            error_count = int(metrics_data.get("error_count", 0))
            
            error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0.0
            
            return {
                "total_requests": total_requests,
                "success_count": success_count,
                "error_count": error_count,
                "error_rate": error_rate,
                "avg_response_time": avg_response_time,
                "max_response_time": max_response_time,
                "min_response_time": min_response_time
            }
            
        except Exception as e:
            logging.error(f"Get integration metrics failed for {integration_id}: {e}")
            return {}
    
    async def _check_integration_health(self, integration_id: str) -> Dict[str, Any]:
        """Check integration health"""
        try:
            config = await self._get_integration_config(integration_id)
            if not config:
                return {"status": "unknown", "error": "Configuration not found"}
            
            # Simple health check - ping endpoint
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    str(config.endpoint_url),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return {
                        "status": "healthy" if response.status < 400 else "unhealthy",
                        "status_code": response.status,
                        "response_time_ms": 0,  # Could be measured
                        "checked_at": datetime.utcnow().isoformat()
                    }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat()
            }
    
    async def start_monitoring(self) -> bool:
        """Start enterprise integration monitoring"""
        try:
            if self.monitoring_active:
                logging.warning("Integration monitoring already active")
                return True
            
            self.monitoring_active = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logging.info("Enterprise integration monitoring started")
            return True
            
        except Exception as e:
            logging.error(f"Integration monitoring start failed: {e}")
            return False
    
    async def stop_monitoring(self) -> bool:
        """Stop enterprise integration monitoring"""
        try:
            self.monitoring_active = False
            
            if self.monitoring_task:
                self.monitoring_task.cancel()
                try:
                    await self.monitoring_task
                except asyncio.CancelledError:
                    pass
                self.monitoring_task = None
            
            logging.info("Enterprise integration monitoring stopped")
            return True
            
        except Exception as e:
            logging.error(f"Integration monitoring stop failed: {e}")
            return False
    
    async def _monitoring_loop(self):
        """Internal monitoring loop"""
        while self.monitoring_active:
            try:
                integration_ids = await self.redis_client.smembers("integration_registry")
                
                for integration_id in integration_ids:
                    # Check health
                    health = await self._check_integration_health(integration_id)
                    
                    # Store health data
                    await self.redis_client.hset(
                        f"health:{integration_id}",
                        mapping={
                            "status": health.get("status", "unknown"),
                            "checked_at": health.get("checked_at", datetime.utcnow().isoformat())
                        }
                    )
                    
                    # Set TTL for health data
                    await self.redis_client.expire(f"health:{integration_id}", 300)
                
                await asyncio.sleep(60)  # Monitor every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Integration monitoring loop error: {e}")
                await asyncio.sleep(120)  # Extended wait on error
    
    async def get_enterprise_integration_metrics(self) -> Dict[str, Any]:
        """Get comprehensive enterprise integration metrics"""
        try:
            integration_ids = await self.redis_client.smembers("integration_registry")
            total_integrations = len(integration_ids)
            
            # Count by status and type
            status_counts = {}
            type_counts = {}
            total_requests = 0
            total_errors = 0
            
            for integration_id in integration_ids:
                config = await self._get_integration_config(integration_id)
                if config:
                    status_counts[config.status.value] = status_counts.get(config.status.value, 0) + 1
                    type_counts[config.integration_type.value] = type_counts.get(config.integration_type.value, 0) + 1
                
                # Get metrics
                metrics = await self._get_integration_metrics(integration_id)
                total_requests += metrics.get("total_requests", 0)
                total_errors += metrics.get("error_count", 0)
            
            overall_error_rate = (total_errors / total_requests * 100) if total_requests > 0 else 0.0
            
            return {
                "total_integrations": total_integrations,
                "status_distribution": status_counts,
                "type_distribution": type_counts,
                "total_requests": total_requests,
                "total_errors": total_errors,
                "overall_error_rate": overall_error_rate,
                "monitoring_active": self.monitoring_active,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Enterprise integration metrics collection failed: {e}")
            return {}


# Enterprise integration hub instance
_integration_hub_instance: Optional[IntegrationHubEnterprise] = None


async def get_integration_hub(
    db_session: AsyncSession,
    redis_client: redis.Redis
) -> IntegrationHubEnterprise:
    """Get or create integration hub instance"""
    global _integration_hub_instance
    
    if _integration_hub_instance is None:
        _integration_hub_instance = IntegrationHubEnterprise(db_session, redis_client)
    
    return _integration_hub_instance


async def initialize_enterprise_integration_hub(
    db_session: AsyncSession,
    redis_client: redis.Redis
) -> bool:
    """Initialize enterprise integration hub"""
    try:
        integration_hub = await get_integration_hub(db_session, redis_client)
        
        # Start monitoring
        await integration_hub.start_monitoring()
        
        logging.info("Enterprise integration hub initialized successfully")
        return True
        
    except Exception as e:
        logging.error(f"Enterprise integration hub initialization failed: {e}")
        return False


# Export enterprise integration components
__all__ = [
    "IntegrationHubEnterprise",
    "IntegrationConfiguration",
    "IntegrationType",
    "IntegrationStatus",
    "AuthenticationType",
    "DataFormat",
    "APIGatewayManager",
    "ServiceOrchestrator",
    "DataTransformationEngine",
    "get_integration_hub",
    "initialize_enterprise_integration_hub"
]