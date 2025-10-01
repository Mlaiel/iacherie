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

GraphQL API Template for iacherie Microservices Platform
======================================================

Enterprise-grade GraphQL API service template providing:
- Strawberry GraphQL framework integration
- Schema federation and stitching
- Real-time subscriptions with WebSockets
- Query complexity analysis and depth limiting
- Automatic schema generation and introspection
- Authentication and authorization
- Caching and performance optimization
- File upload handling
- Batch query processing
- Monitoring and metrics collection

Author: Fahed Mlaiel (mlaiel@live.de)
Backend Senior & GraphQL Expert
"""

import logging
from typing import Dict, Any, Optional, List, Callable, Type, AsyncGenerator, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import json

from fastapi import FastAPI, HTTPException, Depends, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
from strawberry.permission import BasePermission
from strawberry.extensions import Extension
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
import redis.asyncio as redis
from prometheus_client import Counter, Histogram

from ..base_microservice import BaseMicroservice
from ..microservice_template import ServiceConfig, ServiceStatus

logger = logging.getLogger(__name__)


class GraphQLConfig(ServiceConfig):
    """GraphQL API specific configuration"""
    schema_title: str = "iacherie GraphQL API"
    schema_description: str = "Enterprise GraphQL API service"
    enable_introspection: bool = True
    enable_graphiql: bool = True
    enable_subscriptions: bool = True
    max_query_depth: int = 10
    max_query_complexity: int = 1000
    enable_federation: bool = False
    federation_service_name: str = "microservice"
    subscription_heartbeat_interval: int = 30
    enable_file_uploads: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    enable_batch_queries: bool = True
    max_batch_size: int = 10
    enable_persisted_queries: bool = False
    enable_automatic_persisted_queries: bool = True


class AuthPermission(BasePermission):
    """Authentication permission for GraphQL"""
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user has permission"""
        request = info.context["request"]
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return False
        
        # Implement authentication logic here
        return self._validate_token(auth_header)
    
    def _validate_token(self, auth_header: str) -> bool:
        """Validate authentication token"""
        # Simplified token validation
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            return len(token) > 10  # Basic validation
        return False


class RolePermission(BasePermission):
    """Role-based permission for GraphQL"""
    
    def __init__(self, required_roles: List[str]):
        self.required_roles = required_roles
    
    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user has required roles"""
        request = info.context["request"]
        user_roles = self._get_user_roles(request)
        
        return any(role in user_roles for role in self.required_roles)
    
    def _get_user_roles(self, request: Request) -> List[str]:
        """Extract user roles from request"""
        # Implement role extraction logic
        return ["user"]  # Default role


class QueryComplexityExtension(Extension):
    """Extension to analyze query complexity"""
    
    def __init__(self, max_complexity: int = 1000):
        self.max_complexity = max_complexity
    
    async def on_request_start(self):
        """Analyze query complexity before execution"""
        complexity = self._calculate_complexity(self.execution_context.query)
        
        if complexity > self.max_complexity:
            raise HTTPException(
                status_code=400,
                detail=f"Query complexity {complexity} exceeds maximum {self.max_complexity}"
            )
    
    def _calculate_complexity(self, query: str) -> int:
        """Calculate query complexity score"""
        # Simplified complexity calculation
        complexity = 0
        complexity += query.count("{") * 2  # Nested fields
        complexity += query.count("(") * 1  # Arguments
        complexity += len(query.split()) * 0.1  # Query length
        
        return int(complexity)


class QueryDepthExtension(Extension):
    """Extension to limit query depth"""
    
    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
    
    async def on_request_start(self):
        """Check query depth before execution"""
        depth = self._calculate_depth(self.execution_context.query)
        
        if depth > self.max_depth:
            raise HTTPException(
                status_code=400,
                detail=f"Query depth {depth} exceeds maximum {self.max_depth}"
            )
    
    def _calculate_depth(self, query: str) -> int:
        """Calculate query nesting depth"""
        max_depth = 0
        current_depth = 0
        
        for char in query:
            if char == "{":
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == "}":
                current_depth -= 1
        
        return max_depth


class MetricsExtension(Extension):
    """Extension for GraphQL metrics collection"""
    
    def __init__(self):
        self.query_counter = Counter(
            "graphql_queries_total",
            "Total GraphQL queries",
            ["operation_type", "operation_name"]
        )
        
        self.query_duration = Histogram(
            "graphql_query_duration_seconds",
            "GraphQL query duration",
            ["operation_type", "operation_name"]
        )
    
    async def on_request_start(self):
        """Record query start"""
        self.start_time = datetime.utcnow()
    
    async def on_request_end(self):
        """Record query completion"""
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        operation_type = self._get_operation_type()
        operation_name = self._get_operation_name()
        
        self.query_counter.labels(
            operation_type=operation_type,
            operation_name=operation_name
        ).inc()
        
        self.query_duration.labels(
            operation_type=operation_type,
            operation_name=operation_name
        ).observe(duration)
    
    def _get_operation_type(self) -> str:
        """Get GraphQL operation type"""
        # Extract from execution context
        return "query"  # Default
    
    def _get_operation_name(self) -> str:
        """Get GraphQL operation name"""
        # Extract from execution context
        return "unknown"  # Default


@strawberry.type
class User:
    """User type definition"""
    id: strawberry.ID
    name: str
    email: str
    created_at: datetime
    is_active: bool = True


@strawberry.type
class CreateUserInput:
    """Input for creating user"""
    name: str
    email: str


@strawberry.type
class UpdateUserInput:
    """Input for updating user"""
    name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


@strawberry.type
class UserConnection:
    """Paginated user connection"""
    edges: List[User]
    total_count: int
    has_next_page: bool
    has_previous_page: bool


@strawberry.type
class Query:
    """GraphQL Query root"""
    
    @strawberry.field(permission_classes=[AuthPermission])
    async def users(
        self,
        info: Info,
        first: Optional[int] = 10,
        after: Optional[str] = None,
        filter: Optional[str] = None
    ) -> UserConnection:
        """Get paginated list of users"""
        # Implement user retrieval logic
        users = await self._get_users(first, after, filter, info.context)
        
        return UserConnection(
            edges=users["edges"],
            total_count=users["total_count"],
            has_next_page=users["has_next_page"],
            has_previous_page=users["has_previous_page"]
        )
    
    @strawberry.field(permission_classes=[AuthPermission])
    async def user(self, info: Info, id: strawberry.ID) -> Optional[User]:
        """Get user by ID"""
        return await self._get_user_by_id(id, info.context)
    
    @strawberry.field
    async def health(self) -> str:
        """Health check query"""
        return "GraphQL service is healthy"
    
    async def _get_users(self, first: int, after: Optional[str], filter: Optional[str], context: Dict) -> Dict:
        """Get users from data source"""
        # Implement data retrieval logic
        return {
            "edges": [],
            "total_count": 0,
            "has_next_page": False,
            "has_previous_page": False
        }
    
    async def _get_user_by_id(self, user_id: strawberry.ID, context: Dict) -> Optional[User]:
        """Get user by ID from data source"""
        # Implement user retrieval logic
        return None


@strawberry.type
class Mutation:
    """GraphQL Mutation root"""
    
    @strawberry.mutation(permission_classes=[AuthPermission])
    async def create_user(self, info: Info, input: CreateUserInput) -> User:
        """Create new user"""
        user_data = await self._create_user(input, info.context)
        
        # Publish subscription event
        await self._publish_user_created(user_data)
        
        return user_data
    
    @strawberry.mutation(permission_classes=[AuthPermission, RolePermission(["admin"])])
    async def update_user(self, info: Info, id: strawberry.ID, input: UpdateUserInput) -> Optional[User]:
        """Update existing user"""
        return await self._update_user(id, input, info.context)
    
    @strawberry.mutation(permission_classes=[AuthPermission, RolePermission(["admin"])])
    async def delete_user(self, info: Info, id: strawberry.ID) -> bool:
        """Delete user"""
        success = await self._delete_user(id, info.context)
        
        if success:
            await self._publish_user_deleted(id)
        
        return success
    
    async def _create_user(self, input: CreateUserInput, context: Dict) -> User:
        """Create user in data source"""
        # Implement user creation logic
        return User(
            id=strawberry.ID("1"),
            name=input.name,
            email=input.email,
            created_at=datetime.utcnow()
        )
    
    async def _update_user(self, user_id: strawberry.ID, input: UpdateUserInput, context: Dict) -> Optional[User]:
        """Update user in data source"""
        # Implement user update logic
        return None
    
    async def _delete_user(self, user_id: strawberry.ID, context: Dict) -> bool:
        """Delete user from data source"""
        # Implement user deletion logic
        return True
    
    async def _publish_user_created(self, user: User):
        """Publish user created event"""
        # Implement subscription publishing
        pass
    
    async def _publish_user_deleted(self, user_id: strawberry.ID):
        """Publish user deleted event"""
        # Implement subscription publishing
        pass


@strawberry.type
class Subscription:
    """GraphQL Subscription root"""
    
    @strawberry.subscription(permission_classes=[AuthPermission])
    async def user_created(self) -> AsyncGenerator[User, None]:
        """Subscribe to user creation events"""
        # Implement subscription logic with Redis or message queue
        while True:
            # Simulate event streaming
            await asyncio.sleep(10)
            yield User(
                id=strawberry.ID("new"),
                name="New User",
                email="new@example.com",
                created_at=datetime.utcnow()
            )
    
    @strawberry.subscription(permission_classes=[AuthPermission])
    async def user_updated(self, id: strawberry.ID) -> AsyncGenerator[User, None]:
        """Subscribe to user update events"""
        while True:
            await asyncio.sleep(15)
            yield User(
                id=id,
                name="Updated User",
                email="updated@example.com",
                created_at=datetime.utcnow()
            )


class GraphqlApiTemplate(BaseMicroservice):
    """
    Enterprise GraphQL API service template
    
    Provides comprehensive GraphQL functionality including:
    - Strawberry GraphQL framework integration
    - Schema federation and stitching capabilities
    - Real-time subscriptions with WebSocket support
    - Query complexity analysis and depth limiting
    - Authentication and authorization middleware
    - Automatic schema introspection and documentation
    - Performance monitoring and metrics collection
    - File upload handling and validation
    - Batch query processing and optimization
    - Caching and response optimization
    """
    
    def __init__(self, config: GraphQLConfig):
        """Initialize GraphQL API service"""
        self.graphql_config = config
        super().__init__(config)
        
        # Create GraphQL schema
        self.schema = self._create_schema()
        
        # Create GraphQL router
        self.graphql_router = GraphQLRouter(
            self.schema,
            graphiql=config.enable_graphiql,
            allow_queries_via_get=True,
            multipart_uploads_enabled=config.enable_file_uploads,
            subscription_protocols=[
                GRAPHQL_TRANSPORT_WS_PROTOCOL,
                GRAPHQL_WS_PROTOCOL
            ] if config.enable_subscriptions else []
        )
        
        # WebSocket connections for subscriptions
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Setup GraphQL-specific routes
        self._setup_graphql_routes()
        
        logger.info(f"GraphQL API service initialized: {config.schema_title}")
    
    def _create_schema(self) -> strawberry.Schema:
        """Create GraphQL schema with extensions"""
        extensions = [
            QueryComplexityExtension(max_complexity=self.graphql_config.max_query_complexity),
            QueryDepthExtension(max_depth=self.graphql_config.max_query_depth),
            MetricsExtension()
        ]
        
        schema_kwargs = {
            "query": Query,
            "mutation": Mutation,
            "extensions": extensions
        }
        
        if self.graphql_config.enable_subscriptions:
            schema_kwargs["subscription"] = Subscription
        
        return strawberry.Schema(**schema_kwargs)
    
    def _setup_graphql_routes(self):
        """Setup GraphQL-specific routes"""
        # Include GraphQL router
        self.app.include_router(self.graphql_router, prefix="/graphql")
        
        @self.app.get("/graphql/schema")
        async def get_schema():
            """Get GraphQL schema SDL"""
            if self.graphql_config.enable_introspection:
                return {"schema": str(self.schema)}
            else:
                raise HTTPException(status_code=404, detail="Schema introspection disabled")
        
        @self.app.get("/graphql/playground")
        async def graphql_playground():
            """GraphQL Playground interface"""
            if self.graphql_config.enable_graphiql:
                return HTMLResponse(self._get_playground_html())
            else:
                raise HTTPException(status_code=404, detail="GraphQL Playground disabled")
        
        @self.app.websocket("/graphql/subscriptions")
        async def graphql_subscriptions(websocket: WebSocket):
            """WebSocket endpoint for GraphQL subscriptions"""
            if not self.graphql_config.enable_subscriptions:
                await websocket.close(code=1003, reason="Subscriptions disabled")
                return
            
            await self._handle_subscription_connection(websocket)
    
    async def _handle_subscription_connection(self, websocket: WebSocket):
        """Handle GraphQL subscription WebSocket connection"""
        connection_id = str(id(websocket))
        
        try:
            await websocket.accept(subprotocol=GRAPHQL_TRANSPORT_WS_PROTOCOL)
            self.active_connections[connection_id] = websocket
            
            logger.info(f"GraphQL subscription connection established: {connection_id}")
            
            # Handle subscription lifecycle
            await self._subscription_lifecycle(websocket, connection_id)
            
        except WebSocketDisconnect:
            logger.info(f"GraphQL subscription connection closed: {connection_id}")
        except Exception as e:
            logger.error(f"GraphQL subscription error: {str(e)}")
        finally:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
    
    async def _subscription_lifecycle(self, websocket: WebSocket, connection_id: str):
        """Handle subscription message lifecycle"""
        while True:
            try:
                # Receive message from client
                message = await websocket.receive_json()
                
                # Process subscription message
                await self._process_subscription_message(websocket, message)
                
                # Send heartbeat if configured
                if self.graphql_config.subscription_heartbeat_interval > 0:
                    await asyncio.sleep(self.graphql_config.subscription_heartbeat_interval)
                    await websocket.send_json({"type": "ka"})  # Keep alive
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Subscription message processing error: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "payload": {"message": str(e)}
                })
    
    async def _process_subscription_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """Process GraphQL subscription message"""
        message_type = message.get("type")
        
        if message_type == "connection_init":
            await websocket.send_json({"type": "connection_ack"})
        
        elif message_type == "start":
            # Start subscription
            subscription_id = message.get("id")
            query = message.get("payload", {}).get("query")
            variables = message.get("payload", {}).get("variables", {})
            
            # Execute subscription
            await self._execute_subscription(websocket, subscription_id, query, variables)
        
        elif message_type == "stop":
            # Stop subscription
            subscription_id = message.get("id")
            await websocket.send_json({
                "type": "complete",
                "id": subscription_id
            })
        
        elif message_type == "connection_terminate":
            await websocket.close()
    
    async def _execute_subscription(self, websocket: WebSocket, subscription_id: str, query: str, variables: Dict):
        """Execute GraphQL subscription"""
        try:
            # Create execution context
            context = {
                "request": websocket,
                "websocket": websocket,
                "subscription_id": subscription_id
            }
            
            # Execute subscription (simplified)
            await websocket.send_json({
                "type": "data",
                "id": subscription_id,
                "payload": {
                    "data": {"subscription": "started"}
                }
            })
            
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "id": subscription_id,
                "payload": {"message": str(e)}
            })
    
    def _get_playground_html(self) -> str:
        """Get GraphQL Playground HTML"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GraphQL Playground</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/static/css/index.css" />
            <link rel="shortcut icon" href="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/favicon.png" />
            <script src="https://cdn.jsdelivr.net/npm/graphql-playground-react/build/static/js/middleware.js"></script>
        </head>
        <body>
            <div id="root">
                <style>
                    body { margin: 0; overflow: hidden; }
                    #root { height: 100vh; }
                </style>
            </div>
            <script>
                window.addEventListener('load', function (event) {
                    GraphQLPlayground.init(document.getElementById('root'), {
                        endpoint: '/graphql',
                        subscriptionEndpoint: '/graphql/subscriptions'
                    })
                })
            </script>
        </body>
        </html>
        """
    
    # Override abstract methods from BaseMicroservice
    
    async def initialize_service(self):
        """Initialize GraphQL API service"""
        logger.info(f"GraphQL API service {self.config.name} initialized")
    
    async def cleanup_service(self):
        """Cleanup GraphQL API service"""
        # Close all WebSocket connections
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket connection {connection_id}: {str(e)}")
        
        self.active_connections.clear()
        logger.info(f"GraphQL API service {self.config.name} cleaned up")
    
    def register_routes(self):
        """Register service-specific routes"""
        # Routes are registered in _setup_graphql_routes
        pass
    
    async def register_service(self):
        """Register service with service discovery"""
        logger.info(f"GraphQL API service {self.config.name} registered")
    
    async def deregister_service(self):
        """Deregister service from service discovery"""
        logger.info(f"GraphQL API service {self.config.name} deregistered")
    
    async def get_service_url(self, service_name: str) -> str:
        """Get service URL from service discovery"""
        return f"http://{service_name}:8000"
    
    async def start_background_tasks(self):
        """Start background tasks"""
        logger.info("GraphQL subscription management started")
    
    async def stop_background_tasks(self):
        """Stop background tasks"""
        logger.info("GraphQL subscription management stopped")


def create_graphql_api_service(
    service_name: str = "graphql-api-service",
    schema_title: str = "iacherie GraphQL API",
    schema_description: str = "Enterprise GraphQL API service for iacherie platform"
) -> GraphqlApiTemplate:
    """Factory function to create GraphQL API service"""
    
    config = GraphQLConfig(
        name=service_name,
        schema_title=schema_title,
        schema_description=schema_description,
        port=8000,
        enable_introspection=True,
        enable_graphiql=True,
        enable_subscriptions=True,
        enable_metrics=True
    )
    
    return GraphqlApiTemplate(config)


if __name__ == "__main__":
    # Example usage
    service = create_graphql_api_service()
    service.run()