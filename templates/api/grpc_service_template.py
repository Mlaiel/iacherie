"""gRPC Service Template for Ainflue Platform
Enterprise-grade gRPC service with comprehensive features and security

⚠️  AVERTISSEMENT LÉGAL:
==========================================
© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

Author: Fahed Mlaiel (mlaiel@live.de)
Created: 2025-01-18
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, AsyncIterator, Callable
from datetime import datetime
import json
import uuid

import grpc
from grpc import aio
from grpc_reflection.v1alpha import reflection
from grpc_health.v1 import health, health_pb2, health_pb2_grpc
from google.protobuf.json_format import MessageToDict, ParseDict
from google.protobuf.empty_pb2 import Empty

# Import generated protobuf files (would be generated from .proto files)
# import {{service_name}}_pb2
# import {{service_name}}_pb2_grpc

from core.config import get_settings
from core.database import get_db_session
from core.auth import verify_grpc_token, get_user_from_token
from core.rate_limiting import grpc_rate_limit
from core.logging import log_grpc_operation
from utils.exceptions import GRPCException, AuthenticationException
from monitoring.api_metrics import GRPCMetrics

logger = logging.getLogger(__name__)
settings = get_settings()


class {{ServiceName}}Service({{service_name}}_pb2_grpc.{{ServiceName}}ServiceServicer):
    """Enterprise gRPC service for {{service_description}}"""
    
    def __init__(self):
        self.metrics = GRPCMetrics()
        self.db_session_factory = get_db_session
        
    async def Get{{EntityName}}(
        self, 
        request: {{service_name}}_pb2.Get{{EntityName}}Request, 
        context: grpc.aio.ServicerContext
    ) -> {{service_name}}_pb2.{{EntityName}}Response:
        """Get single {{entity_description}}"""
        
        try:
            # Extract metadata
            metadata = dict(context.invocation_metadata())
            
            # Authentication
            user = await self._authenticate_request(context, metadata)
            
            # Rate limiting
            await self._check_rate_limit(context, "get_{{entity_name}}", user.id if user else None)
            
            # Validate request
            if not request.id:
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "ID is required")
            
            # Get entity from database
            async with self.db_session_factory() as session:
                entity = await {{EntityName}}Service.get_by_id(session, request.id)
                
                if not entity:
                    await context.abort(grpc.StatusCode.NOT_FOUND, "{{EntityName}} not found")
                
                # Check permissions
                if not await {{EntityName}}Service.can_read(entity, user):
                    await context.abort(grpc.StatusCode.PERMISSION_DENIED, "Access denied")
                
                # Convert to protobuf response
                response = {{service_name}}_pb2.{{EntityName}}Response()
                self._populate_entity_response(response, entity)
                
                # Log operation
                log_grpc_operation(
                    method="Get{{EntityName}}",
                    user_id=user.id if user else None,
                    entity_id=request.id,
                    success=True
                )
                
                # Record metrics
                self.metrics.record_method_call("Get{{EntityName}}", user.id if user else None)
                
                return response
                
        except Exception as e:
            logger.error(f"Error in Get{{EntityName}}: {str(e)}")
            self.metrics.record_method_error("Get{{EntityName}}", str(e))
            await self._handle_grpc_error(context, e)
    
    async def List{{EntityName}}s(
        self, 
        request: {{service_name}}_pb2.List{{EntityName}}sRequest, 
        context: grpc.aio.ServicerContext
    ) -> {{service_name}}_pb2.List{{EntityName}}sResponse:
        """List {{entity_description}}s with pagination"""
        
        try:
            metadata = dict(context.invocation_metadata())
            user = await self._authenticate_request(context, metadata)
            
            await self._check_rate_limit(context, "list_{{entity_name}}s", user.id if user else None)
            
            # Validate pagination parameters
            page_size = min(request.page_size or 50, 100)  # Max 100 items per page
            page_token = request.page_token
            
            async with self.db_session_factory() as session:
                # Build query with filters
                query_params = {
                    "page_size": page_size,
                    "page_token": page_token,
                    "user": user,
                    "filters": self._extract_filters(request)
                }
                
                result = await {{EntityName}}Service.get_paginated_for_grpc(session, **query_params)
                
                # Build response
                response = {{service_name}}_pb2.List{{EntityName}}sResponse()
                
                for entity in result["entities"]:
                    entity_pb = response.{{entity_name}}s.add()
                    self._populate_entity_response(entity_pb, entity)
                
                response.next_page_token = result.get("next_page_token", "")
                response.total_count = result.get("total_count", 0)
                
                log_grpc_operation(
                    method="List{{EntityName}}s",
                    user_id=user.id if user else None,
                    metadata={"count": len(result["entities"])}
                )
                
                self.metrics.record_method_call("List{{EntityName}}s", user.id if user else None)
                
                return response
                
        except Exception as e:
            logger.error(f"Error in List{{EntityName}}s: {str(e)}")
            self.metrics.record_method_error("List{{EntityName}}s", str(e))
            await self._handle_grpc_error(context, e)
    
    async def Create{{EntityName}}(
        self, 
        request: {{service_name}}_pb2.Create{{EntityName}}Request, 
        context: grpc.aio.ServicerContext
    ) -> {{service_name}}_pb2.{{EntityName}}Response:
        """Create new {{entity_description}}"""
        
        try:
            metadata = dict(context.invocation_metadata())
            user = await self._authenticate_request(context, metadata, required=True)
            
            await self._check_rate_limit(context, "create_{{entity_name}}", user.id)
            
            # Validate request
            if not request.{{entity_name}}.name:
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Name is required")
            
            # Check permissions
            if not await self._check_permission(user, "create_{{entity_name}}"):
                await context.abort(grpc.StatusCode.PERMISSION_DENIED, "Insufficient permissions")
            
            async with self.db_session_factory() as session:
                # Convert protobuf to entity data
                entity_data = self._extract_entity_data(request.{{entity_name}})
                entity_data["created_by_id"] = user.id
                entity_data["created_at"] = datetime.utcnow()
                
                # Business logic validation
                validation_errors = await {{EntityName}}Service.validate_create(session, entity_data)
                if validation_errors:
                    await context.abort(
                        grpc.StatusCode.INVALID_ARGUMENT, 
                        f"Validation errors: {', '.join(validation_errors)}"
                    )
                
                # Create entity
                entity = await {{EntityName}}Service.create(session, entity_data)
                
                # Build response
                response = {{service_name}}_pb2.{{EntityName}}Response()
                self._populate_entity_response(response, entity)
                
                log_grpc_operation(
                    method="Create{{EntityName}}",
                    user_id=user.id,
                    entity_id=str(entity.id),
                    success=True
                )
                
                self.metrics.record_method_call("Create{{EntityName}}", user.id)
                
                return response
                
        except Exception as e:
            logger.error(f"Error in Create{{EntityName}}: {str(e)}")
            self.metrics.record_method_error("Create{{EntityName}}", str(e))
            await self._handle_grpc_error(context, e)
    
    async def Update{{EntityName}}(
        self, 
        request: {{service_name}}_pb2.Update{{EntityName}}Request, 
        context: grpc.aio.ServicerContext
    ) -> {{service_name}}_pb2.{{EntityName}}Response:
        """Update existing {{entity_description}}"""
        
        try:
            metadata = dict(context.invocation_metadata())
            user = await self._authenticate_request(context, metadata, required=True)
            
            await self._check_rate_limit(context, "update_{{entity_name}}", user.id)
            
            if not request.{{entity_name}}.id:
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "ID is required")
            
            async with self.db_session_factory() as session:
                # Get existing entity
                entity = await {{EntityName}}Service.get_by_id(session, request.{{entity_name}}.id)
                if not entity:
                    await context.abort(grpc.StatusCode.NOT_FOUND, "{{EntityName}} not found")
                
                # Check permissions
                if not await {{EntityName}}Service.can_update(entity, user):
                    await context.abort(grpc.StatusCode.PERMISSION_DENIED, "Access denied")
                
                # Extract update data
                update_data = self._extract_entity_data(request.{{entity_name}})
                update_data["updated_at"] = datetime.utcnow()
                
                # Apply field mask if provided
                if request.update_mask and request.update_mask.paths:
                    filtered_data = {}
                    for path in request.update_mask.paths:
                        if path in update_data:
                            filtered_data[path] = update_data[path]
                    update_data = filtered_data
                
                # Update entity
                updated_entity = await {{EntityName}}Service.update(session, entity.id, update_data)
                
                # Build response
                response = {{service_name}}_pb2.{{EntityName}}Response()
                self._populate_entity_response(response, updated_entity)
                
                log_grpc_operation(
                    method="Update{{EntityName}}",
                    user_id=user.id,
                    entity_id=request.{{entity_name}}.id,
                    success=True
                )
                
                self.metrics.record_method_call("Update{{EntityName}}", user.id)
                
                return response
                
        except Exception as e:
            logger.error(f"Error in Update{{EntityName}}: {str(e)}")
            self.metrics.record_method_error("Update{{EntityName}}", str(e))
            await self._handle_grpc_error(context, e)
    
    async def Delete{{EntityName}}(
        self, 
        request: {{service_name}}_pb2.Delete{{EntityName}}Request, 
        context: grpc.aio.ServicerContext
    ) -> Empty:
        """Delete {{entity_description}}"""
        
        try:
            metadata = dict(context.invocation_metadata())
            user = await self._authenticate_request(context, metadata, required=True)
            
            await self._check_rate_limit(context, "delete_{{entity_name}}", user.id)
            
            if not request.id:
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "ID is required")
            
            async with self.db_session_factory() as session:
                entity = await {{EntityName}}Service.get_by_id(session, request.id)
                if not entity:
                    await context.abort(grpc.StatusCode.NOT_FOUND, "{{EntityName}} not found")
                
                if not await {{EntityName}}Service.can_delete(entity, user):
                    await context.abort(grpc.StatusCode.PERMISSION_DENIED, "Access denied")
                
                # Soft delete or hard delete based on configuration
                await {{EntityName}}Service.delete(session, request.id, soft_delete=True)
                
                log_grpc_operation(
                    method="Delete{{EntityName}}",
                    user_id=user.id,
                    entity_id=request.id,
                    success=True
                )
                
                self.metrics.record_method_call("Delete{{EntityName}}", user.id)
                
                return Empty()
                
        except Exception as e:
            logger.error(f"Error in Delete{{EntityName}}: {str(e)}")
            self.metrics.record_method_error("Delete{{EntityName}}", str(e))
            await self._handle_grpc_error(context, e)
    
    async def Stream{{EntityName}}Events(
        self, 
        request: {{service_name}}_pb2.Stream{{EntityName}}EventsRequest, 
        context: grpc.aio.ServicerContext
    ) -> AsyncIterator[{{service_name}}_pb2.{{EntityName}}Event]:
        """Stream real-time {{entity_description}} events"""
        
        try:
            metadata = dict(context.invocation_metadata())
            user = await self._authenticate_request(context, metadata, required=True)
            
            await self._check_rate_limit(context, "stream_{{entity_name}}_events", user.id)
            
            # Set up event stream
            event_filter = {
                "entity_types": ["{{entity_name}}"],
                "user_id": user.id if request.only_own else None,
                "event_types": list(request.event_types) if request.event_types else None
            }
            
            async for event in self._stream_events(event_filter, context):
                # Convert to protobuf event
                event_pb = {{service_name}}_pb2.{{EntityName}}Event()
                event_pb.event_type = event["event_type"]
                event_pb.entity_id = event["entity_id"]
                event_pb.timestamp.FromDatetime(event["timestamp"])
                
                if event.get("entity_data"):
                    self._populate_entity_response(event_pb.entity, event["entity_data"])
                
                yield event_pb
                
        except Exception as e:
            logger.error(f"Error in Stream{{EntityName}}Events: {str(e)}")
            self.metrics.record_method_error("Stream{{EntityName}}Events", str(e))
            await self._handle_grpc_error(context, e)
    
    async def Search{{EntityName}}s(
        self, 
        request: {{service_name}}_pb2.Search{{EntityName}}sRequest, 
        context: grpc.aio.ServicerContext
    ) -> {{service_name}}_pb2.Search{{EntityName}}sResponse:
        """Search {{entity_description}}s with full-text search"""
        
        try:
            metadata = dict(context.invocation_metadata())
            user = await self._authenticate_request(context, metadata)
            
            await self._check_rate_limit(context, "search_{{entity_name}}s", user.id if user else None)
            
            if not request.query:
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Search query is required")
            
            async with self.db_session_factory() as session:
                search_params = {
                    "query": request.query,
                    "page_size": min(request.page_size or 20, 50),
                    "page_token": request.page_token,
                    "user": user,
                    "filters": self._extract_search_filters(request)
                }
                
                results = await {{EntityName}}Service.search(session, **search_params)
                
                # Build response
                response = {{service_name}}_pb2.Search{{EntityName}}sResponse()
                
                for entity in results["entities"]:
                    result_pb = response.results.add()
                    self._populate_entity_response(result_pb.entity, entity)
                    result_pb.relevance_score = entity.get("relevance_score", 0.0)
                
                response.next_page_token = results.get("next_page_token", "")
                response.total_count = results.get("total_count", 0)
                
                log_grpc_operation(
                    method="Search{{EntityName}}s",
                    user_id=user.id if user else None,
                    metadata={"query": request.query, "count": len(results["entities"])}
                )
                
                self.metrics.record_method_call("Search{{EntityName}}s", user.id if user else None)
                
                return response
                
        except Exception as e:
            logger.error(f"Error in Search{{EntityName}}s: {str(e)}")
            self.metrics.record_method_error("Search{{EntityName}}s", str(e))
            await self._handle_grpc_error(context, e)
    
    # Helper methods
    
    async def _authenticate_request(
        self, 
        context: grpc.aio.ServicerContext, 
        metadata: Dict[str, str], 
        required: bool = False
    ) -> Optional[Any]:
        """Authenticate gRPC request"""
        
        auth_token = metadata.get("authorization", "")
        if auth_token.startswith("Bearer "):
            token = auth_token[7:]
            try:
                user = await get_user_from_token(token)
                return user
            except AuthenticationException:
                if required:
                    await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid authentication token")
                return None
        
        if required:
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Authentication required")
        
        return None
    
    async def _check_rate_limit(
        self, 
        context: grpc.aio.ServicerContext, 
        method: str, 
        user_id: Optional[str]
    ):
        """Check rate limiting for gRPC method"""
        
        # Extract client IP
        peer = context.peer()
        client_ip = peer.split(":")[-2] if ":" in peer else "unknown"
        
        # Check rate limit
        limit_key = f"grpc:{method}:{user_id or client_ip}"
        
        if not await grpc_rate_limit(limit_key, calls=100, period=60):
            await context.abort(grpc.StatusCode.RESOURCE_EXHAUSTED, "Rate limit exceeded")
    
    async def _check_permission(self, user: Any, permission: str) -> bool:
        """Check user permission"""
        # Implement permission checking logic
        return True  # Placeholder
    
    def _populate_entity_response(self, response_pb, entity):
        """Populate protobuf response from entity model"""
        response_pb.id = str(entity.id)
        response_pb.name = entity.name or ""
        response_pb.description = entity.description or ""
        response_pb.status = entity.status or ""
        
        if entity.created_at:
            response_pb.created_at.FromDatetime(entity.created_at)
        if entity.updated_at:
            response_pb.updated_at.FromDatetime(entity.updated_at)
        
        # Add custom fields based on entity type
        if hasattr(entity, "category"):
            response_pb.category = entity.category or ""
        
        if hasattr(entity, "tags") and entity.tags:
            response_pb.tags.extend(entity.tags)
        
        if hasattr(entity, "metadata") and entity.metadata:
            # Convert metadata to JSON string or structured fields
            response_pb.metadata = json.dumps(entity.metadata)
    
    def _extract_entity_data(self, entity_pb) -> Dict[str, Any]:
        """Extract entity data from protobuf message"""
        data = {}
        
        if entity_pb.name:
            data["name"] = entity_pb.name
        if entity_pb.description:
            data["description"] = entity_pb.description
        if entity_pb.status:
            data["status"] = entity_pb.status
        if entity_pb.category:
            data["category"] = entity_pb.category
        if entity_pb.tags:
            data["tags"] = list(entity_pb.tags)
        if entity_pb.metadata:
            try:
                data["metadata"] = json.loads(entity_pb.metadata)
            except json.JSONDecodeError:
                pass
        
        return data
    
    def _extract_filters(self, request) -> Dict[str, Any]:
        """Extract filters from list request"""
        filters = {}
        
        if hasattr(request, "filter"):
            if request.filter.status:
                filters["status"] = request.filter.status
            if request.filter.category:
                filters["category"] = request.filter.category
            if request.filter.user_id:
                filters["user_id"] = request.filter.user_id
        
        return filters
    
    def _extract_search_filters(self, request) -> Dict[str, Any]:
        """Extract filters from search request"""
        filters = {}
        
        if hasattr(request, "filter"):
            if request.filter.categories:
                filters["categories"] = list(request.filter.categories)
            if request.filter.date_range:
                filters["date_range"] = {
                    "start": request.filter.date_range.start.ToDatetime(),
                    "end": request.filter.date_range.end.ToDatetime()
                }
        
        return filters
    
    async def _stream_events(self, event_filter: Dict[str, Any], context: grpc.aio.ServicerContext):
        """Stream events based on filter"""
        # This would typically connect to a message broker or event stream
        # For this template, we'll simulate with a simple async generator
        
        import redis.asyncio as aioredis
        
        redis_client = aioredis.from_url(settings.REDIS_URL)
        pubsub = redis_client.pubsub()
        
        try:
            # Subscribe to relevant channels
            channels = []
            for entity_type in event_filter.get("entity_types", []):
                channels.append(f"events:{entity_type}")
            
            if channels:
                await pubsub.subscribe(*channels)
                
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        try:
                            event_data = json.loads(message["data"])
                            
                            # Apply filters
                            if self._event_matches_filter(event_data, event_filter):
                                yield event_data
                                
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            logger.error(f"Error processing event: {e}")
                            continue
                    
                    # Check if client disconnected
                    if context.cancelled():
                        break
                        
        finally:
            await pubsub.unsubscribe()
            await redis_client.close()
    
    def _event_matches_filter(self, event_data: Dict[str, Any], event_filter: Dict[str, Any]) -> bool:
        """Check if event matches filter criteria"""
        
        # Check entity types
        if event_filter.get("entity_types"):
            if event_data.get("entity_type") not in event_filter["entity_types"]:
                return False
        
        # Check user ID
        if event_filter.get("user_id"):
            if event_data.get("user_id") != event_filter["user_id"]:
                return False
        
        # Check event types
        if event_filter.get("event_types"):
            if event_data.get("event_type") not in event_filter["event_types"]:
                return False
        
        return True
    
    async def _handle_grpc_error(self, context: grpc.aio.ServicerContext, error: Exception):
        """Handle and convert exceptions to gRPC errors"""
        
        if isinstance(error, AuthenticationException):
            await context.abort(grpc.StatusCode.UNAUTHENTICATED, str(error))
        elif isinstance(error, PermissionError):
            await context.abort(grpc.StatusCode.PERMISSION_DENIED, str(error))
        elif isinstance(error, ValueError):
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(error))
        elif isinstance(error, FileNotFoundError):
            await context.abort(grpc.StatusCode.NOT_FOUND, str(error))
        else:
            # Log internal errors but don't expose details
            logger.error(f"Internal gRPC error: {str(error)}")
            await context.abort(grpc.StatusCode.INTERNAL, "Internal server error")


class {{ServiceName}}HealthService(health_pb2_grpc.HealthServicer):
    """Health check service for {{service_name}}"""
    
    def __init__(self):
        self.service_status = health_pb2.HealthCheckResponse.SERVING
    
    async def Check(
        self, 
        request: health_pb2.HealthCheckRequest, 
        context: grpc.aio.ServicerContext
    ) -> health_pb2.HealthCheckResponse:
        """Check service health"""
        
        service = request.service
        
        if service == "" or service == "{{service_name}}":
            # Perform health checks
            is_healthy = await self._check_service_health()
            status = health_pb2.HealthCheckResponse.SERVING if is_healthy else health_pb2.HealthCheckResponse.NOT_SERVING
        else:
            status = health_pb2.HealthCheckResponse.SERVICE_UNKNOWN
        
        return health_pb2.HealthCheckResponse(status=status)
    
    async def Watch(
        self, 
        request: health_pb2.HealthCheckRequest, 
        context: grpc.aio.ServicerContext
    ) -> AsyncIterator[health_pb2.HealthCheckResponse]:
        """Watch service health status"""
        
        last_status = None
        
        while not context.cancelled():
            current_status = await self.Check(request, context)
            
            if current_status.status != last_status:
                yield current_status
                last_status = current_status.status
            
            await asyncio.sleep(5)  # Check every 5 seconds
    
    async def _check_service_health(self) -> bool:
        """Perform actual health checks"""
        try:
            # Check database connectivity
            async with get_db_session() as session:
                await session.execute("SELECT 1")
            
            # Check other dependencies (Redis, external services, etc.)
            
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


async def create_grpc_server(port: int = 50051) -> aio.Server:
    """Create and configure gRPC server"""
    
    server = aio.server()
    
    # Add services
    {{service_name}}_pb2_grpc.add_{{ServiceName}}ServiceServicer_to_server({{ServiceName}}Service(), server)
    health_pb2_grpc.add_HealthServicer_to_server({{ServiceName}}HealthService(), server)
    
    # Add reflection for development
    if settings.ENVIRONMENT != "production":
        SERVICE_NAMES = (
            {{service_name}}_pb2.DESCRIPTOR.services_by_name["{{ServiceName}}Service"].full_name,
            reflection.SERVICE_NAME,
        )
        reflection.enable_server_reflection(SERVICE_NAMES, server)
    
    # Configure server
    listen_addr = f"[::]:{port}"
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting gRPC server on {listen_addr}")
    
    return server


async def serve():
    """Start the gRPC server"""
    server = await create_grpc_server()
    
    await server.start()
    logger.info("gRPC server started")
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server")
        await server.stop(grace=5)


# Export for template system
__all__ = [
    "{{ServiceName}}Service",
    "{{ServiceName}}HealthService", 
    "create_grpc_server",
    "serve"
]


# Example protobuf definitions (would be in separate .proto file)
PROTOBUF_DEFINITION = '''
syntax = "proto3";

package {{service_name}};

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";
import "google/protobuf/field_mask.proto";

// {{EntityName}} service definition
service {{ServiceName}}Service {
  rpc Get{{EntityName}}(Get{{EntityName}}Request) returns ({{EntityName}}Response);
  rpc List{{EntityName}}s(List{{EntityName}}sRequest) returns (List{{EntityName}}sResponse);
  rpc Create{{EntityName}}(Create{{EntityName}}Request) returns ({{EntityName}}Response);
  rpc Update{{EntityName}}(Update{{EntityName}}Request) returns ({{EntityName}}Response);
  rpc Delete{{EntityName}}(Delete{{EntityName}}Request) returns (google.protobuf.Empty);
  rpc Stream{{EntityName}}Events(Stream{{EntityName}}EventsRequest) returns (stream {{EntityName}}Event);
  rpc Search{{EntityName}}s(Search{{EntityName}}sRequest) returns (Search{{EntityName}}sResponse);
}

// Messages
message {{EntityName}} {
  string id = 1;
  string name = 2;
  string description = 3;
  string status = 4;
  string category = 5;
  repeated string tags = 6;
  string metadata = 7;
  google.protobuf.Timestamp created_at = 8;
  google.protobuf.Timestamp updated_at = 9;
}

message Get{{EntityName}}Request {
  string id = 1;
}

message {{EntityName}}Response {
  {{EntityName}} {{entity_name}} = 1;
}

message List{{EntityName}}sRequest {
  int32 page_size = 1;
  string page_token = 2;
  {{EntityName}}Filter filter = 3;
}

message List{{EntityName}}sResponse {
  repeated {{EntityName}} {{entity_name}}s = 1;
  string next_page_token = 2;
  int32 total_count = 3;
}

message Create{{EntityName}}Request {
  {{EntityName}} {{entity_name}} = 1;
}

message Update{{EntityName}}Request {
  {{EntityName}} {{entity_name}} = 1;
  google.protobuf.FieldMask update_mask = 2;
}

message Delete{{EntityName}}Request {
  string id = 1;
}

message {{EntityName}}Filter {
  string status = 1;
  string category = 2;
  string user_id = 3;
}

message Stream{{EntityName}}EventsRequest {
  bool only_own = 1;
  repeated string event_types = 2;
}

message {{EntityName}}Event {
  string event_type = 1;
  string entity_id = 2;
  {{EntityName}} entity = 3;
  google.protobuf.Timestamp timestamp = 4;
}

message Search{{EntityName}}sRequest {
  string query = 1;
  int32 page_size = 2;
  string page_token = 3;
  SearchFilter filter = 4;
}

message Search{{EntityName}}sResponse {
  repeated SearchResult results = 1;
  string next_page_token = 2;
  int32 total_count = 3;
}

message SearchResult {
  {{EntityName}} entity = 1;
  float relevance_score = 2;
}

message SearchFilter {
  repeated string categories = 1;
  DateRange date_range = 2;
}

message DateRange {
  google.protobuf.Timestamp start = 1;
  google.protobuf.Timestamp end = 2;
}
'''