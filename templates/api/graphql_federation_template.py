"""GraphQL Federation Template for iacherie Platform
Enterprise-grade Apollo Federation implementation for microservices architecture

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
from typing import Dict, Any, Optional, List, Union, Type
from datetime import datetime
from dataclasses import dataclass
import json

import graphene
from graphene import ObjectType, Field, String, List as GrapheneList, Int, Boolean, Interface
from graphene_federation import build_schema, key, external, requires, provides, extend
from graphql import GraphQLSchema, GraphQLResolveInfo
from graphql.execution.executors.asyncio import AsyncioExecutor

from core.config import get_settings
from core.database import get_db_session
from core.auth import get_current_user, verify_permissions
from core.caching import cache_federated_response
from core.logging import log_federation_operation
from utils.exceptions import FederationException
from monitoring.api_metrics import FederationMetrics

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ServiceMetadata:
    """Metadata for federated service"""
    name: str
    version: str
    url: str
    health_check_url: str
    schema_url: str
    capabilities: List[str]


class FederatedEntity(Interface):
    """Base interface for federated entities"""
    
    class Meta:
        name = "FederatedEntity"
    
    id = String(required=True, description="Global entity ID")
    _service = String(description="Originating service name")
    _typename = String(description="GraphQL type name")


@key(fields="id")
class {{EntityName}}(ObjectType):
    """Federated {{entity_description}} entity"""
    
    class Meta:
        interfaces = (FederatedEntity,)
    
    # Primary fields owned by this service
    id = external(String(required=True))
    name = String(description="{{EntityName}} name")
    description = String(description="{{EntityName}} description")
    status = String(description="Current status")
    created_at = String(description="Creation timestamp")
    updated_at = String(description="Last update timestamp")
    
    # Extended fields from other services
    creator = external(Field("User"))  # From user service
    analytics = Field("{{EntityName}}Analytics")  # From analytics service
    monetization = Field("{{EntityName}}Monetization")  # From monetization service
    
    # Computed fields requiring data from multiple services
    @requires(fields="creator { id premium_status }")
    def resolve_premium_features(self, info):
        """Resolve premium features based on creator status"""
        if hasattr(self, 'creator') and self.creator:
            return self.creator.premium_status == "active"
        return False
    
    @provides(fields="analytics { view_count engagement_rate }")
    def resolve_performance_score(self, info):
        """Calculate performance score from analytics"""
        if hasattr(self, 'analytics') and self.analytics:
            return min(
                (self.analytics.view_count * 0.3) + 
                (self.analytics.engagement_rate * 0.7),
                100.0
            )
        return 0.0
    
    def __resolve_reference(self, info, **representation):
        """Resolve entity reference for federation"""
        entity_id = representation.get("id")
        if not entity_id:
            return None
        
        # Load entity from this service's database
        return {{EntityName}}Loader.load_by_id(entity_id)


@key(fields="id")
class User(ObjectType):
    """Extended user entity with {{entity_name}} relationships"""
    
    id = external(String(required=True))
    username = external(String())
    email = external(String())
    
    # Fields provided by this service
    {{entity_name}}_count = Int(description="Number of {{entity_name}}s created")
    featured_{{entity_name}} = Field({{EntityName}}, description="Featured {{entity_name}}")
    recent_{{entity_name}}s = GrapheneList({{EntityName}}, limit=Int(default_value=5))
    
    @cache_federated_response(ttl=300)
    async def resolve_{{entity_name}}_count(self, info):
        """Resolve count of user's {{entity_name}}s"""
        async with get_db_session() as session:
            count = await {{EntityName}}Service.count_by_user(session, self.id)
            return count
    
    async def resolve_featured_{{entity_name}}(self, info):
        """Resolve user's featured {{entity_name}}"""
        async with get_db_session() as session:
            featured = await {{EntityName}}Service.get_featured_by_user(session, self.id)
            return featured
    
    async def resolve_recent_{{entity_name}}s(self, info, limit=5):
        """Resolve user's recent {{entity_name}}s"""
        async with get_db_session() as session:
            recent = await {{EntityName}}Service.get_recent_by_user(session, self.id, limit)
            return recent
    
    def __resolve_reference(self, info, **representation):
        """Resolve user reference for federation"""
        user_id = representation.get("id")
        if not user_id:
            return User(id=user_id)  # Return stub for federation
        
        # This service doesn't own User data, return reference
        return User(
            id=user_id,
            username=representation.get("username"),
            email=representation.get("email")
        )


class {{EntityName}}Analytics(ObjectType):
    """Analytics data for {{entity_name}} (from analytics service)"""
    
    view_count = Int(description="Total view count")
    engagement_rate = Float(description="Engagement rate percentage")
    revenue_total = Float(description="Total revenue generated")
    collaboration_count = Int(description="Number of collaborations")
    
    # This would typically be resolved by the analytics service
    # Here we provide a stub or make a federated call


class {{EntityName}}Monetization(ObjectType):
    """Monetization data for {{entity_name}} (from monetization service)"""
    
    revenue_total = Float(description="Total revenue")
    revenue_monthly = Float(description="Monthly revenue")
    payment_methods = GrapheneList(String, description="Available payment methods")
    monetization_enabled = Boolean(description="Monetization status")


class {{EntityName}}Query(ObjectType):
    """Queries specific to {{entity_name}} service"""
    
    {{entity_name}} = Field({{EntityName}}, id=String(required=True))
    {{entity_name}}s = GrapheneList(
        {{EntityName}},
        limit=Int(default_value=20),
        offset=Int(default_value=0),
        user_id=String()
    )
    search_{{entity_name}}s = GrapheneList(
        {{EntityName}},
        query=String(required=True),
        limit=Int(default_value=10)
    )
    
    # Federated queries that combine data from multiple services
    {{entity_name}}_with_analytics = Field(
        {{EntityName}},
        id=String(required=True),
        description="Get {{entity_name}} with full analytics data"
    )
    
    top_performing_{{entity_name}}s = GrapheneList(
        {{EntityName}},
        limit=Int(default_value=10),
        time_range=String(default_value="30d"),
        description="Get top performing {{entity_name}}s across all metrics"
    )
    
    @log_federation_operation
    async def resolve_{{entity_name}}(self, info, id):
        """Resolve single {{entity_name}} with federation"""
        async with get_db_session() as session:
            entity = await {{EntityName}}Service.get_by_id(session, id)
            if not entity:
                return None
            
            # Check permissions
            user = await get_current_user(info.context["request"])
            if not await {{EntityName}}Service.can_read(entity, user):
                return None
            
            FederationMetrics.record_entity_resolution("{{entity_name}}", id)
            return entity
    
    @log_federation_operation
    async def resolve_{{entity_name}}s(self, info, limit, offset, user_id=None):
        """Resolve list of {{entity_name}}s"""
        async with get_db_session() as session:
            entities = await {{EntityName}}Service.get_paginated(
                session, 
                limit=limit, 
                offset=offset, 
                user_id=user_id
            )
            
            # Apply permission filtering
            user = await get_current_user(info.context["request"])
            filtered_entities = []
            for entity in entities:
                if await {{EntityName}}Service.can_read(entity, user):
                    filtered_entities.append(entity)
            
            FederationMetrics.record_list_resolution("{{entity_name}}", len(filtered_entities))
            return filtered_entities
    
    @log_federation_operation
    async def resolve_search_{{entity_name}}s(self, info, query, limit):
        """Search {{entity_name}}s with federation"""
        async with get_db_session() as session:
            results = await {{EntityName}}Service.search(session, query, limit)
            
            user = await get_current_user(info.context["request"])
            filtered_results = []
            for entity in results:
                if await {{EntityName}}Service.can_read(entity, user):
                    filtered_results.append(entity)
            
            FederationMetrics.record_search_resolution("{{entity_name}}", query, len(filtered_results))
            return filtered_results
    
    @log_federation_operation
    @cache_federated_response(ttl=600)
    async def resolve_{{entity_name}}_with_analytics(self, info, id):
        """Resolve {{entity_name}} with complete analytics (federated)"""
        # First get the base entity
        entity = await self.resolve_{{entity_name}}(info, id)
        if not entity:
            return None
        
        # The analytics data would be automatically resolved by federation
        # when the analytics field is requested in the query
        
        return entity
    
    @log_federation_operation
    @cache_federated_response(ttl=1800)  # 30 minutes cache
    async def resolve_top_performing_{{entity_name}}s(self, info, limit, time_range):
        """Get top performing {{entity_name}}s (requires federation with analytics service)"""
        
        # This query requires data from multiple services:
        # 1. Base {{entity_name}} data from this service
        # 2. Analytics data from analytics service
        # 3. User data from user service
        
        async with get_db_session() as session:
            # Get {{entity_name}}s with basic performance metrics
            top_entities = await {{EntityName}}Service.get_top_performing(
                session, 
                limit=limit, 
                time_range=time_range
            )
            
            user = await get_current_user(info.context["request"])
            filtered_entities = []
            for entity in top_entities:
                if await {{EntityName}}Service.can_read(entity, user):
                    filtered_entities.append(entity)
            
            FederationMetrics.record_federated_query("top_performing_{{entity_name}}s", len(filtered_entities))
            return filtered_entities


class {{EntityName}}Mutation(ObjectType):
    """Mutations for {{entity_name}} service"""
    
    create_{{entity_name}} = Field(
        {{EntityName}},
        name=String(required=True),
        description=String(),
        category=String()
    )
    
    update_{{entity_name}} = Field(
        {{EntityName}},
        id=String(required=True),
        name=String(),
        description=String(),
        category=String()
    )
    
    delete_{{entity_name}} = Boolean(
        id=String(required=True)
    )
    
    @log_federation_operation
    async def resolve_create_{{entity_name}}(self, info, name, description=None, category=None):
        """Create new {{entity_name}} with federation events"""
        user = await get_current_user(info.context["request"])
        if not user:
            raise FederationException("Authentication required")
        
        if not await verify_permissions(user, "create_{{entity_name}}"):
            raise FederationException("Insufficient permissions")
        
        async with get_db_session() as session:
            entity_data = {
                "name": name,
                "description": description,
                "category": category,
                "created_by_id": user.id,
                "created_at": datetime.utcnow()
            }
            
            entity = await {{EntityName}}Service.create(session, entity_data)
            
            # Publish federation event for other services
            await self._publish_federation_event(
                "{{entity_name}}.created",
                {
                    "entity_id": str(entity.id),
                    "user_id": user.id,
                    "entity_data": entity_data
                }
            )
            
            FederationMetrics.record_mutation("create_{{entity_name}}", user.id)
            return entity
    
    @log_federation_operation
    async def resolve_update_{{entity_name}}(self, info, id, **updates):
        """Update {{entity_name}} with federation events"""
        user = await get_current_user(info.context["request"])
        if not user:
            raise FederationException("Authentication required")
        
        async with get_db_session() as session:
            entity = await {{EntityName}}Service.get_by_id(session, id)
            if not entity:
                raise FederationException("Entity not found")
            
            if not await {{EntityName}}Service.can_update(entity, user):
                raise FederationException("Insufficient permissions")
            
            # Apply updates
            update_data = {k: v for k, v in updates.items() if v is not None}
            if update_data:
                update_data["updated_at"] = datetime.utcnow()
                entity = await {{EntityName}}Service.update(session, id, update_data)
                
                # Publish federation event
                await self._publish_federation_event(
                    "{{entity_name}}.updated",
                    {
                        "entity_id": id,
                        "user_id": user.id,
                        "changes": update_data
                    }
                )
            
            FederationMetrics.record_mutation("update_{{entity_name}}", user.id)
            return entity
    
    @log_federation_operation
    async def resolve_delete_{{entity_name}}(self, info, id):
        """Delete {{entity_name}} with federation cleanup"""
        user = await get_current_user(info.context["request"])
        if not user:
            raise FederationException("Authentication required")
        
        async with get_db_session() as session:
            entity = await {{EntityName}}Service.get_by_id(session, id)
            if not entity:
                return False
            
            if not await {{EntityName}}Service.can_delete(entity, user):
                raise FederationException("Insufficient permissions")
            
            # Delete entity
            await {{EntityName}}Service.delete(session, id)
            
            # Publish federation event for cleanup in other services
            await self._publish_federation_event(
                "{{entity_name}}.deleted",
                {
                    "entity_id": id,
                    "user_id": user.id,
                    "entity_type": "{{entity_name}}"
                }
            )
            
            FederationMetrics.record_mutation("delete_{{entity_name}}", user.id)
            return True
    
    async def _publish_federation_event(self, event_type: str, data: Dict[str, Any]):
        """Publish event to federation event bus"""
        # This would typically use a message broker like RabbitMQ or Kafka
        # For this template, we'll use Redis pub/sub
        
        import redis.asyncio as aioredis
        redis_client = aioredis.from_url(settings.REDIS_URL)
        
        try:
            event = {
                "type": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "service": "{{entity_name}}_service",
                "data": data
            }
            
            await redis_client.publish(
                f"federation:events:{event_type}",
                json.dumps(event, default=str)
            )
            
            logger.info(f"Published federation event: {event_type}")
            
        except Exception as e:
            logger.error(f"Failed to publish federation event: {e}")
        finally:
            await redis_client.close()


class FederationHealthCheck(ObjectType):
    """Health check for federation service"""
    
    service_name = String(description="Service name")
    version = String(description="Service version")
    status = String(description="Service status")
    capabilities = GrapheneList(String, description="Service capabilities")
    dependencies = GrapheneList(String, description="Service dependencies")
    last_updated = String(description="Last health check update")
    
    def resolve_service_name(self, info):
        return "{{entity_name}}_service"
    
    def resolve_version(self, info):
        return settings.SERVICE_VERSION
    
    def resolve_status(self, info):
        # Perform health checks
        return "healthy"  # or "degraded", "unhealthy"
    
    def resolve_capabilities(self, info):
        return [
            "{{entity_name}}_crud",
            "{{entity_name}}_search",
            "{{entity_name}}_analytics_integration",
            "user_relations"
        ]
    
    def resolve_dependencies(self, info):
        return [
            "user_service",
            "analytics_service", 
            "monetization_service",
            "database",
            "redis"
        ]
    
    def resolve_last_updated(self, info):
        return datetime.utcnow().isoformat()


class Query(ObjectType):
    """Root query for federated {{entity_name}} service"""
    
    # Service-specific queries
    {{entity_name}} = {{EntityName}}Query.{{entity_name}}
    {{entity_name}}s = {{EntityName}}Query.{{entity_name}}s
    search_{{entity_name}}s = {{EntityName}}Query.search_{{entity_name}}s
    {{entity_name}}_with_analytics = {{EntityName}}Query.{{entity_name}}_with_analytics
    top_performing_{{entity_name}}s = {{EntityName}}Query.top_performing_{{entity_name}}s
    
    # Federation health check
    _service_health = Field(FederationHealthCheck, description="Service health status")
    
    def resolve__service_health(self, info):
        """Resolve service health for federation monitoring"""
        return FederationHealthCheck()


class Mutation(ObjectType):
    """Root mutation for federated {{entity_name}} service"""
    
    create_{{entity_name}} = {{EntityName}}Mutation.create_{{entity_name}}
    update_{{entity_name}} = {{EntityName}}Mutation.update_{{entity_name}}
    delete_{{entity_name}} = {{EntityName}}Mutation.delete_{{entity_name}}


# Build federated schema
schema = build_schema(
    query=Query,
    mutation=Mutation,
    types=[{{EntityName}}, User, {{EntityName}}Analytics, {{EntityName}}Monetization]
)


# Federation service configuration
FEDERATION_CONFIG = {
    "service_name": "{{entity_name}}_service",
    "service_url": f"{settings.SERVICE_BASE_URL}/graphql",
    "schema_url": f"{settings.SERVICE_BASE_URL}/graphql/schema.sdl",
    "health_url": f"{settings.SERVICE_BASE_URL}/health",
    "version": settings.SERVICE_VERSION,
    "capabilities": [
        "{{entity_name}}_management",
        "user_{{entity_name}}_relations",
        "search_and_discovery",
        "real_time_subscriptions"
    ],
    "dependencies": [
        "user_service",
        "analytics_service",
        "monetization_service"
    ]
}


def get_federated_schema_sdl() -> str:
    """Get Schema Definition Language representation for federation"""
    from graphql import build_client_schema, get_introspection_query, graphql_sync
    
    # Get introspection result
    introspection_result = graphql_sync(schema, get_introspection_query())
    
    if introspection_result.errors:
        raise Exception(f"Schema introspection failed: {introspection_result.errors}")
    
    # Build client schema and print SDL
    client_schema = build_client_schema(introspection_result.data)
    from graphql import print_schema
    
    return print_schema(client_schema)


async def register_with_gateway():
    """Register this service with the federation gateway"""
    import aiohttp
    
    registration_data = {
        "name": FEDERATION_CONFIG["service_name"],
        "url": FEDERATION_CONFIG["service_url"],
        "schema": get_federated_schema_sdl(),
        "version": FEDERATION_CONFIG["version"],
        "capabilities": FEDERATION_CONFIG["capabilities"]
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.FEDERATION_GATEWAY_URL}/register",
                json=registration_data
            ) as response:
                if response.status == 200:
                    logger.info(f"Successfully registered {FEDERATION_CONFIG['service_name']} with gateway")
                else:
                    logger.error(f"Failed to register with gateway: {response.status}")
                    
    except Exception as e:
        logger.error(f"Error registering with federation gateway: {e}")


# Export for template system
__all__ = [
    "schema",
    "Query",
    "Mutation",
    "{{EntityName}}",
    "User",
    "{{EntityName}}Query",
    "{{EntityName}}Mutation",
    "FederationHealthCheck",
    "FEDERATION_CONFIG",
    "get_federated_schema_sdl",
    "register_with_gateway"
]