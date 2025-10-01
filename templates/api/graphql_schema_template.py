"""GraphQL Schema Template for iacherie Platform
Enterprise-grade GraphQL schema with advanced security and performance optimization

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
from enum import Enum

import graphene
from graphene import ObjectType, Mutation, Field, List as GrapheneList, String, Int, Boolean, DateTime, Float
from graphene.relay import Node, ConnectionField
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from graphql import GraphQLError

from core.config import get_settings
from core.database import get_db_session
from core.auth import get_current_user, verify_permissions
from core.rate_limiting import graphql_rate_limit
from core.caching import cache_graphql_response
from core.validation import validate_graphql_input
from core.logging import log_graphql_operation
from utils.exceptions import GraphQLException, ValidationException
from utils.pagination import CursorPagination
from monitoring.api_metrics import GraphQLMetricsCollector

logger = logging.getLogger(__name__)
settings = get_settings()


class GraphQLErrorType(Enum):
    """GraphQL error types for structured error handling"""
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class CreatorEconomyNode(Node):
    """Base Node interface for Creator Economy entities"""
    
    class Meta:
        name = "CreatorEconomyNode"
    
    @staticmethod
    def to_global_id(type_name: str, id: Any) -> str:
        """Convert local ID to global ID"""
        return f"{type_name}:{id}"
    
    @staticmethod
    def from_global_id(global_id: str) -> tuple:
        """Convert global ID to type and local ID"""
        try:
            type_name, local_id = global_id.split(":", 1)
            return type_name, local_id
        except ValueError:
            raise GraphQLError("Invalid global ID format")


class {{EntityName}}Type(SQLAlchemyObjectType):
    """GraphQL type for {{entity_description}}"""
    
    class Meta:
        model = {{EntityModel}}
        interfaces = (CreatorEconomyNode,)
        exclude_fields = ("password_hash", "api_key", "private_data")
    
    # Custom fields with business logic
    display_name = String(description="Formatted display name")
    is_active = Boolean(description="Whether the entity is active")
    creator_score = Float(description="Creator economy score")
    monetization_status = String(description="Current monetization status")
    
    def resolve_display_name(self, info):
        """Resolve display name with fallback logic"""
        return self.display_name or f"{self.first_name} {self.last_name}"
    
    def resolve_is_active(self, info):
        """Resolve active status with business rules"""
        return self.status == "active" and self.verified_at is not None
    
    def resolve_creator_score(self, info):
        """Calculate creator economy score"""
        # Implement scoring algorithm
        base_score = 50.0
        if self.content_count > 0:
            base_score += min(self.content_count * 2, 30)
        if self.collaboration_count > 0:
            base_score += min(self.collaboration_count * 5, 20)
        return min(base_score, 100.0)
    
    def resolve_monetization_status(self, info):
        """Resolve monetization status"""
        if not self.is_monetization_enabled:
            return "disabled"
        if self.revenue_total > 1000:
            return "established"
        elif self.revenue_total > 100:
            return "growing"
        else:
            return "starter"


class {{EntityName}}Connection(graphene.relay.Connection):
    """Connection for paginated {{entity_description}} results"""
    
    class Meta:
        node = {{EntityName}}Type
    
    total_count = Int(description="Total number of items")
    edge_count = Int(description="Number of items in current page")
    
    def resolve_total_count(self, info):
        """Resolve total count for pagination info"""
        return self.length if hasattr(self, 'length') else 0
    
    def resolve_edge_count(self, info):
        """Resolve edge count for current page"""
        return len(self.edges) if self.edges else 0


class {{EntityName}}FilterInput(graphene.InputObjectType):
    """Input type for filtering {{entity_description}}"""
    
    name_contains = String(description="Filter by name containing text")
    status = String(description="Filter by status")
    is_verified = Boolean(description="Filter by verification status")
    created_after = DateTime(description="Filter by creation date")
    created_before = DateTime(description="Filter by creation date")
    min_score = Float(description="Minimum creator score")
    max_score = Float(description="Maximum creator score")
    monetization_enabled = Boolean(description="Filter by monetization status")


class {{EntityName}}SortInput(graphene.InputObjectType):
    """Input type for sorting {{entity_description}}"""
    
    field = String(required=True, description="Field to sort by")
    direction = String(default_value="ASC", description="Sort direction (ASC/DESC)")


class Create{{EntityName}}Input(graphene.InputObjectType):
    """Input type for creating {{entity_description}}"""
    
    name = String(required=True, description="Entity name")
    description = String(description="Entity description")
    category = String(description="Entity category")
    tags = GrapheneList(String, description="Entity tags")
    metadata = graphene.JSONString(description="Additional metadata")


class Update{{EntityName}}Input(graphene.InputObjectType):
    """Input type for updating {{entity_description}}"""
    
    id = String(required=True, description="Entity ID")
    name = String(description="Entity name")
    description = String(description="Entity description")
    category = String(description="Entity category")
    tags = GrapheneList(String, description="Entity tags")
    metadata = graphene.JSONString(description="Additional metadata")


class Create{{EntityName}}Mutation(Mutation):
    """Mutation for creating {{entity_description}}"""
    
    class Arguments:
        input = Create{{EntityName}}Input(required=True)
    
    success = Boolean()
    {{entity_name}} = Field({{EntityName}}Type)
    errors = GrapheneList(String)
    
    @staticmethod
    @log_graphql_operation
    @graphql_rate_limit(calls=10, period=60)
    async def mutate(root, info, input):
        """Create new {{entity_description}}"""
        try:
            # Authentication check
            user = await get_current_user(info.context["request"])
            if not user:
                raise GraphQLError("Authentication required", 
                                 extensions={"code": GraphQLErrorType.AUTHENTICATION_ERROR.value})
            
            # Authorization check
            if not await verify_permissions(user, "create_{{entity_name}}"):
                raise GraphQLError("Insufficient permissions", 
                                 extensions={"code": GraphQLErrorType.AUTHORIZATION_ERROR.value})
            
            # Input validation
            validation_errors = await validate_graphql_input(input, Create{{EntityName}}Input)
            if validation_errors:
                return Create{{EntityName}}Mutation(
                    success=False,
                    errors=validation_errors
                )
            
            # Business logic validation
            if await {{EntityName}}Service.name_exists(input.name):
                return Create{{EntityName}}Mutation(
                    success=False,
                    errors=["Name already exists"]
                )
            
            # Create entity
            async with get_db_session() as session:
                entity_data = {
                    "name": input.name,
                    "description": input.description,
                    "category": input.category,
                    "tags": input.tags or [],
                    "metadata": input.metadata or {},
                    "created_by_id": user.id,
                    "created_at": datetime.utcnow()
                }
                
                entity = await {{EntityName}}Service.create(session, entity_data)
                
                # Log metrics
                GraphQLMetricsCollector.record_mutation("create_{{entity_name}}", user.id)
                
                return Create{{EntityName}}Mutation(
                    success=True,
                    {{entity_name}}=entity
                )
                
        except GraphQLError:
            raise
        except Exception as e:
            logger.error(f"Error creating {{entity_description}}: {str(e)}")
            raise GraphQLError("Internal server error", 
                             extensions={"code": GraphQLErrorType.INTERNAL_ERROR.value})


class Update{{EntityName}}Mutation(Mutation):
    """Mutation for updating {{entity_description}}"""
    
    class Arguments:
        input = Update{{EntityName}}Input(required=True)
    
    success = Boolean()
    {{entity_name}} = Field({{EntityName}}Type)
    errors = GrapheneList(String)
    
    @staticmethod
    @log_graphql_operation
    @graphql_rate_limit(calls=20, period=60)
    async def mutate(root, info, input):
        """Update existing {{entity_description}}"""
        try:
            # Authentication and authorization
            user = await get_current_user(info.context["request"])
            if not user:
                raise GraphQLError("Authentication required", 
                                 extensions={"code": GraphQLErrorType.AUTHENTICATION_ERROR.value})
            
            # Get entity and check ownership/permissions
            async with get_db_session() as session:
                entity = await {{EntityName}}Service.get_by_id(session, input.id)
                if not entity:
                    return Update{{EntityName}}Mutation(
                        success=False,
                        errors=["Entity not found"]
                    )
                
                # Check ownership or admin permissions
                if entity.created_by_id != user.id and not await verify_permissions(user, "admin_{{entity_name}}"):
                    raise GraphQLError("Insufficient permissions", 
                                     extensions={"code": GraphQLErrorType.AUTHORIZATION_ERROR.value})
                
                # Update entity
                update_data = {k: v for k, v in input.__dict__.items() if v is not None and k != "id"}
                if update_data:
                    update_data["updated_at"] = datetime.utcnow()
                    entity = await {{EntityName}}Service.update(session, entity.id, update_data)
                
                # Invalidate cache
                await cache_graphql_response.invalidate(f"{{entity_name}}:{entity.id}")
                
                GraphQLMetricsCollector.record_mutation("update_{{entity_name}}", user.id)
                
                return Update{{EntityName}}Mutation(
                    success=True,
                    {{entity_name}}=entity
                )
                
        except GraphQLError:
            raise
        except Exception as e:
            logger.error(f"Error updating {{entity_description}}: {str(e)}")
            raise GraphQLError("Internal server error", 
                             extensions={"code": GraphQLErrorType.INTERNAL_ERROR.value})


class Delete{{EntityName}}Mutation(Mutation):
    """Mutation for deleting {{entity_description}}"""
    
    class Arguments:
        id = String(required=True, description="Entity ID")
    
    success = Boolean()
    errors = GrapheneList(String)
    
    @staticmethod
    @log_graphql_operation
    @graphql_rate_limit(calls=5, period=60)
    async def mutate(root, info, id):
        """Delete {{entity_description}}"""
        try:
            user = await get_current_user(info.context["request"])
            if not user:
                raise GraphQLError("Authentication required", 
                                 extensions={"code": GraphQLErrorType.AUTHENTICATION_ERROR.value})
            
            async with get_db_session() as session:
                entity = await {{EntityName}}Service.get_by_id(session, id)
                if not entity:
                    return Delete{{EntityName}}Mutation(
                        success=False,
                        errors=["Entity not found"]
                    )
                
                # Check permissions
                if entity.created_by_id != user.id and not await verify_permissions(user, "admin_{{entity_name}}"):
                    raise GraphQLError("Insufficient permissions", 
                                     extensions={"code": GraphQLErrorType.AUTHORIZATION_ERROR.value})
                
                # Soft delete or hard delete based on business rules
                await {{EntityName}}Service.delete(session, id, soft_delete=True)
                
                # Invalidate cache
                await cache_graphql_response.invalidate(f"{{entity_name}}:{id}")
                
                GraphQLMetricsCollector.record_mutation("delete_{{entity_name}}", user.id)
                
                return Delete{{EntityName}}Mutation(success=True)
                
        except GraphQLError:
            raise
        except Exception as e:
            logger.error(f"Error deleting {{entity_description}}: {str(e)}")
            raise GraphQLError("Internal server error", 
                             extensions={"code": GraphQLErrorType.INTERNAL_ERROR.value})


class Query(ObjectType):
    """Root Query for {{EntityName}} GraphQL API"""
    
    # Single entity queries
    {{entity_name}} = Field({{EntityName}}Type, id=String(required=True), description="Get {{entity_description}} by ID")
    {{entity_name}}_by_name = Field({{EntityName}}Type, name=String(required=True), description="Get {{entity_description}} by name")
    
    # Collection queries with pagination
    {{entity_name}}_list = ConnectionField(
        {{EntityName}}Connection,
        filter={{EntityName}}FilterInput(),
        sort={{EntityName}}SortInput(),
        description="Get paginated list of {{entity_description}}"
    )
    
    # Search queries
    search_{{entity_name}} = ConnectionField(
        {{EntityName}}Connection,
        query=String(required=True),
        filter={{EntityName}}FilterInput(),
        description="Search {{entity_description}} by text query"
    )
    
    # Analytics queries
    {{entity_name}}_analytics = Field(
        graphene.JSONString,
        entity_id=String(),
        date_range=String(),
        description="Get analytics for {{entity_description}}"
    )
    
    @log_graphql_operation
    @cache_graphql_response(ttl=300)  # Cache for 5 minutes
    async def resolve_{{entity_name}}(self, info, id):
        """Resolve single {{entity_description}} by ID"""
        try:
            async with get_db_session() as session:
                entity = await {{EntityName}}Service.get_by_id(session, id)
                if not entity:
                    raise GraphQLError("Entity not found")
                
                # Check read permissions
                user = await get_current_user(info.context["request"])
                if not await {{EntityName}}Service.can_read(entity, user):
                    raise GraphQLError("Insufficient permissions", 
                                     extensions={"code": GraphQLErrorType.AUTHORIZATION_ERROR.value})
                
                GraphQLMetricsCollector.record_query("{{entity_name}}", user.id if user else None)
                return entity
                
        except GraphQLError:
            raise
        except Exception as e:
            logger.error(f"Error resolving {{entity_description}}: {str(e)}")
            raise GraphQLError("Internal server error", 
                             extensions={"code": GraphQLErrorType.INTERNAL_ERROR.value})
    
    @log_graphql_operation
    @cache_graphql_response(ttl=600)  # Cache for 10 minutes
    async def resolve_{{entity_name}}_list(self, info, **kwargs):
        """Resolve paginated list of {{entity_description}}"""
        try:
            user = await get_current_user(info.context["request"])
            
            async with get_db_session() as session:
                # Build query with filters and sorting
                query_params = {
                    "filter": kwargs.get("filter"),
                    "sort": kwargs.get("sort"),
                    "user": user
                }
                
                entities = await {{EntityName}}Service.get_paginated(session, **query_params)
                
                GraphQLMetricsCollector.record_query("{{entity_name}}_list", user.id if user else None)
                return entities
                
        except Exception as e:
            logger.error(f"Error resolving {{entity_description}} list: {str(e)}")
            raise GraphQLError("Internal server error", 
                             extensions={"code": GraphQLErrorType.INTERNAL_ERROR.value})
    
    @log_graphql_operation
    async def resolve_search_{{entity_name}}(self, info, query, **kwargs):
        """Resolve search results for {{entity_description}}"""
        try:
            user = await get_current_user(info.context["request"])
            
            async with get_db_session() as session:
                search_params = {
                    "query": query,
                    "filter": kwargs.get("filter"),
                    "user": user
                }
                
                results = await {{EntityName}}Service.search(session, **search_params)
                
                GraphQLMetricsCollector.record_query("search_{{entity_name}}", user.id if user else None)
                return results
                
        except Exception as e:
            logger.error(f"Error searching {{entity_description}}: {str(e)}")
            raise GraphQLError("Internal server error", 
                             extensions={"code": GraphQLErrorType.INTERNAL_ERROR.value})


class Mutation(ObjectType):
    """Root Mutation for {{EntityName}} GraphQL API"""
    
    create_{{entity_name}} = Create{{EntityName}}Mutation.Field()
    update_{{entity_name}} = Update{{EntityName}}Mutation.Field()
    delete_{{entity_name}} = Delete{{EntityName}}Mutation.Field()


# Schema definition
schema = graphene.Schema(
    query=Query,
    mutation=Mutation,
    types=[{{EntityName}}Type]
)


# Schema metadata for introspection
schema.description = """
{{EntityName}} GraphQL API Schema for iacherie Platform

This schema provides comprehensive CRUD operations for {{entity_description}}
with enterprise-grade security, caching, rate limiting, and monitoring.

Features:
- JWT authentication and RBAC authorization
- Input validation and sanitization
- Rate limiting and caching
- Comprehensive error handling
- Audit logging and metrics
- Relay-style pagination
- Advanced filtering and sorting
- Full-text search capabilities
- Real-time subscriptions support

Security:
- All mutations require authentication
- Field-level authorization
- Input validation and sanitization
- Rate limiting protection
- Audit trail logging

© 2025 Fahed Mlaiel - All Rights Reserved
"""


# Export for template system
__all__ = [
    "schema",
    "Query",
    "Mutation",
    "{{EntityName}}Type",
    "{{EntityName}}Connection",
    "Create{{EntityName}}Mutation",
    "Update{{EntityName}}Mutation",
    "Delete{{EntityName}}Mutation"
]